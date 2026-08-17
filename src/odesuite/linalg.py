"""Jacobians and linear solves for the implicit steppers.

Written once and shared by every implicit method. Four ways to obtain
``J = df/dy``, in descending order of preference:

1. **Analytic** -- whatever the user supplied on the `ODEProblem`.
2. **Complex step** -- ``Im f(t, y + i*h*e_j) / h``. Exact to machine precision
   because there is no subtractive cancellation, so `h` can be taken absurdly
   small. Requires `f` to be complex-analytic, which rules out `abs`, `max`,
   comparisons and anything that inspects `.real`; it is therefore opt-in.
3. **Sparse finite differences** -- columns whose row supports do not overlap are
   structurally orthogonal and can be perturbed simultaneously. Greedy graph
   colouring turns a banded 1000x1000 Jacobian from 1000 RHS evaluations into
   about five.
4. **Dense finite differences** -- the fallback, with Shampine's perturbation
   scaling and an exactly-representable increment.
"""

from __future__ import annotations

import warnings

import numpy as np
from scipy import sparse
from scipy.linalg import LinAlgWarning, lu_factor, lu_solve
from scipy.sparse.linalg import splu

__all__ = [
    "EPS",
    "forward_diff_jacobian",
    "complex_step_jacobian",
    "column_groups",
    "sparse_diff_jacobian",
    "JacobianEvaluator",
    "lu_factorize",
    "apply_mass",
    "threshold_from_tolerances",
]

EPS = np.finfo(float).eps

#: Floor on the finite-difference perturbation scale, so that components sitting
#: at exactly zero still get a meaningful increment. Callers that know the
#: integration tolerances should pass ``threshold_from_tolerances`` instead --
#: this bare default is deliberately conservative.
DEFAULT_THRESHOLD = 1e-8


def threshold_from_tolerances(rtol: float, atol) -> float:
    """A finite-difference floor derived from the integration tolerances.

    ``atol/rtol`` is the state magnitude below which the integrator has stopped
    caring about relative accuracy, which is exactly the "typical size" a
    perturbation should be measured against (the convention in Shampine's
    NUMJAC). Using a fixed tiny floor instead makes the increment for a
    component sitting at zero absurdly small -- ``sqrt(EPS) * 1e-8`` is
    ``1.5e-16`` -- and the resulting column is noise.
    """
    scale = float(np.max(np.asarray(atol))) / max(float(rtol), EPS)
    return float(np.clip(scale, DEFAULT_THRESHOLD, 1.0))


def _increments(y: np.ndarray, threshold: float) -> np.ndarray:
    """Shampine-scaled finite-difference increments, one per component.

    Scaled by the component's own magnitude so that a state spanning many orders
    of magnitude -- which is the normal case for stiff kinetics -- is
    differentiated accurately in every component rather than only the largest.
    """
    return np.sqrt(EPS) * np.maximum(np.abs(y), threshold)


def forward_diff_jacobian(f, t, y, f0, threshold: float = DEFAULT_THRESHOLD):
    """Dense Jacobian by forward differences. Costs n RHS evaluations."""
    n = y.size
    # Dtype taken from the state, not assumed real: a complex-valued system
    # (a spectral PDE discretisation, say) would otherwise have the imaginary
    # part of every Jacobian entry silently discarded on assignment.
    J = np.empty((f0.size, n), dtype=np.result_type(y, f0))
    h = _increments(np.abs(y), threshold)
    for j in range(n):
        y1 = y.copy()
        y1[j] += h[j]
        # Recover the increment that was *actually* applied: y1[j] - y[j] differs
        # from h[j] by rounding, and dividing by the nominal value would inject
        # that rounding straight into the derivative.
        dy = y1[j] - y[j]
        J[:, j] = (f(t, y1) - f0) / dy
    return J


def complex_step_jacobian(f, t, y, step: float = 1e-30):
    """Dense Jacobian by the complex-step trick. Costs n RHS evaluations.

    ``f(y + i*h) = f(y) + i*h*f'(y) + O(h^2)``, so the derivative is the
    imaginary part over `h` with no differencing of nearby values and hence no
    cancellation. Accuracy is that of the function evaluation itself,
    independent of `h`, which is why a step of 1e-30 is not only safe but
    optimal -- the opposite of the finite-difference trade-off.
    """
    n = y.size
    yc = y.astype(np.complex128)
    J = np.empty((y.size, n))
    for j in range(n):
        y1 = yc.copy()
        y1[j] += 1j * step
        J[:, j] = np.asarray(f(t, y1)).imag / step
    return J


def column_groups(sparsity) -> np.ndarray:
    """Partition columns into structurally orthogonal groups (greedy colouring).

    Two columns may share a perturbation if no row is nonzero in both: their
    contributions to the difference vector land in disjoint entries and can be
    separated afterwards. Finding the fewest such groups is graph colouring;
    greedy sequential colouring gets within a small factor of optimal and is
    what every production sparse-Jacobian code uses.
    """
    S = sparse.csc_matrix(sparsity)
    n = S.shape[1]
    groups = np.empty(n, dtype=int)
    occupied: list[set[int]] = []

    for j in range(n):
        rows = set(S.indices[S.indptr[j] : S.indptr[j + 1]].tolist())
        for g, used in enumerate(occupied):
            if used.isdisjoint(rows):
                used |= rows
                groups[j] = g
                break
        else:
            occupied.append(rows)
            groups[j] = len(occupied) - 1
    return groups


def sparse_diff_jacobian(
    f, t, y, f0, sparsity, groups, threshold: float = DEFAULT_THRESHOLD
):
    """Sparse Jacobian by grouped finite differences.

    Costs one RHS evaluation per colour group rather than per column.
    """
    S = sparse.csc_matrix(sparsity)
    n = y.size
    h = _increments(np.abs(y), threshold)
    rows_out, cols_out, vals_out = [], [], []

    for g in range(groups.max() + 1):
        members = np.nonzero(groups == g)[0]
        y1 = y.copy()
        y1[members] += h[members]
        dy = y1[members] - y[members]
        df = f(t, y1) - f0
        for j, step in zip(members, dy):
            rows = S.indices[S.indptr[j] : S.indptr[j + 1]]
            if rows.size == 0:
                continue
            rows_out.append(rows)
            cols_out.append(np.full(rows.size, j))
            vals_out.append(df[rows] / step)

    if not rows_out:
        return sparse.csc_matrix((n, n))
    return sparse.csc_matrix(
        (
            np.concatenate(vals_out),
            (np.concatenate(rows_out), np.concatenate(cols_out)),
        ),
        shape=(n, n),
    )


class JacobianEvaluator:
    """Produces ``df/dy`` by whichever strategy suits the problem.

    Also counts its own RHS evaluations, so the driver's `nfev` stays honest
    about the cost of numerical differentiation -- which on a large problem is
    most of the work.
    """

    def __init__(self, problem, method: str = "auto", threshold: float = DEFAULT_THRESHOLD):
        self.problem = problem
        self.threshold = threshold
        self.njev = 0
        self.nfev = 0

        if method == "auto":
            if problem.has_jac:
                method = "analytic"
            elif problem.jac_sparsity is not None:
                method = "sparse"
            else:
                method = "fd"
        self.method = method

        self.groups = None
        self.sparsity = None
        if method == "sparse":
            if problem.jac_sparsity is None:
                raise ValueError("jac_sparsity is required for method='sparse'")
            self.sparsity = sparse.csc_matrix(problem.jac_sparsity)
            self.groups = column_groups(self.sparsity)

        self.constant_jac = problem.has_jac and not callable(problem._jac_user)
        self._cached = None

    @property
    def n_groups(self) -> int | None:
        """Number of colour groups, i.e. RHS evaluations per sparse Jacobian."""
        return None if self.groups is None else int(self.groups.max() + 1)

    def __call__(self, t: float, y: np.ndarray, f0: np.ndarray):
        """Evaluate the Jacobian at ``(t, y)``."""
        self.njev += 1

        if self.method == "analytic":
            # A constant Jacobian supplied as a matrix is evaluated once, ever.
            if self.constant_jac:
                if self._cached is None:
                    self._cached = self.problem.jac(t, y)
                return self._cached
            return self.problem.jac(t, y)

        f = self.problem.f
        if self.method == "complex_step":
            self.nfev += y.size
            return complex_step_jacobian(f, t, y)
        if self.method == "sparse":
            assert self.n_groups is not None  # the sparse path requires a pattern
            self.nfev += self.n_groups
            return sparse_diff_jacobian(
                f, t, y, f0, self.sparsity, self.groups, self.threshold
            )
        self.nfev += y.size
        return forward_diff_jacobian(f, t, y, f0, self.threshold)


# ---------------------------------------------------------------------------
# Linear solves
# ---------------------------------------------------------------------------


class _DenseLU:
    __slots__ = ("lu", "piv")

    def __init__(self, A):
        with warnings.catch_warnings():
            # scipy only warns on an exactly singular factorisation and then
            # returns silently poisoned factors; we want a hard failure instead.
            warnings.simplefilter("ignore", LinAlgWarning)
            self.lu, self.piv = lu_factor(A, overwrite_a=True)
        if not np.all(np.diagonal(self.lu)):
            raise np.linalg.LinAlgError(
                "singular iteration matrix: zero pivot in the LU factorisation"
            )

    def solve(self, b):
        return lu_solve((self.lu, self.piv), b, overwrite_b=False)


class _SparseLU:
    __slots__ = ("factorization",)

    def __init__(self, A):
        self.factorization = splu(A)

    def solve(self, b):
        return self.factorization.solve(b)


def lu_factorize(A):
    """Factorise `A`, dispatching on sparseness. Returns an object with ``.solve``.

    Raises `np.linalg.LinAlgError` on a singular matrix so callers can react by
    shrinking the step rather than propagating NaNs.
    """
    if sparse.issparse(A):
        return _SparseLU(sparse.csc_matrix(A))
    return _DenseLU(np.asarray(A, dtype=A.dtype if hasattr(A, "dtype") else float))


def apply_mass(mass, v):
    """Compute ``M @ v``, treating ``mass is None`` as the identity."""
    if mass is None:
        return v
    return mass @ v


def mass_minus_jacobian(mass, J, coefficient):
    """Build ``coefficient * M - J``, the matrix every implicit method factorises.

    Handles the four dense/sparse combinations and preserves sparsity whenever
    both operands are sparse, which is the case that makes large problems
    tractable at all.
    """
    if sparse.issparse(J):
        M = sparse.eye(J.shape[0], format="csc") if mass is None else sparse.csc_matrix(mass)
        return (coefficient * M - J).tocsc()
    J = np.asarray(J)
    if mass is None:
        return coefficient * np.eye(J.shape[0], dtype=np.result_type(J, coefficient)) - J
    M = mass.toarray() if sparse.issparse(mass) else np.asarray(mass)
    return coefficient * M - J
