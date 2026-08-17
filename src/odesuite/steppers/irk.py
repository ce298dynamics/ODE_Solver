"""Implicit Runge-Kutta: Radau IIA.

Radau IIA with three stages is fifth order, L-stable and stiffly accurate --
the reference method for stiff systems and index-1 DAEs. Unlike a Rosenbrock
method it solves genuinely nonlinear stage equations, so a stale Jacobian costs
Newton iterations but not accuracy, which lets it reuse one factorisation across
many steps.

The stage equations are ``M Z = h (A (x) I) F(y + Z)``. Applying Newton and
multiplying through by ``A^-1 / h`` gives

    [ (A^-1 (x) M)/h - I (x) J ] dZ = G(Z)

a ``3n x 3n`` system. Two ways to solve it are implemented:

``linear_solve="split"`` (default)
    Diagonalise ``A^-1 = T L T^-1``. Its spectrum is one real eigenvalue and one
    complex-conjugate pair, so the system decouples into one real ``n x n``
    solve and one complex ``n x n`` solve -- the second conjugate block is the
    conjugate of the first and is free. Cost drops from ``O(27 n^3)`` to about
    ``O(5 n^3)``.

``linear_solve="dense"``
    Assemble and factor the full ``3n x 3n`` matrix. Obviously correct, and
    retained as the oracle: `tests/test_radau.py` asserts the two paths agree to
    round-off on every test problem, which is what makes the fast path
    trustworthy.

`T` and its inverse are obtained from `numpy.linalg.eig` at import time rather
than transcribed from published tables, removing a whole class of
transcription error.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from ..dense import CollocationInterpolant, Interpolant
from ..linalg import (
    JacobianEvaluator,
    apply_mass,
    lu_factorize,
    mass_minus_jacobian,
    threshold_from_tolerances,
)
from ..newton import JacobianPolicy, NewtonSettings, simplified_newton
from .base import Stepper, StepResult

__all__ = ["RadauTableau", "RADAU_IIA_5", "RadauIIA"]


@dataclass(frozen=True)
class RadauTableau:
    """Collocation coefficients plus the spectral data the split solve needs."""

    name: str
    A: np.ndarray        # (s, s) collocation matrix
    c: np.ndarray        # (s,)   abscissae, with c[-1] == 1
    E: np.ndarray        # (s,)   error-estimate weights
    order: int
    error_order: int

    @property
    def n_stages(self) -> int:
        return self.c.size

    @property
    def b(self) -> np.ndarray:
        """Radau IIA is stiffly accurate: the weights are the last row of A."""
        return self.A[-1]


def _radau_iia_5() -> RadauTableau:
    """Three-stage Radau IIA, order 5. Coefficients in closed form."""
    s6 = np.sqrt(6.0)
    A = np.array(
        [
            [(88 - 7 * s6) / 360, (296 - 169 * s6) / 1800, (-2 + 3 * s6) / 225],
            [(296 + 169 * s6) / 1800, (88 + 7 * s6) / 360, (-2 - 3 * s6) / 225],
            [(16 - s6) / 36, (16 + s6) / 36, 1 / 9],
        ]
    )
    c = np.array([(4 - s6) / 10, (4 + s6) / 10, 1.0])
    # Hairer & Wanner II, IV.8: weights of the embedded order-3 estimate.
    E = np.array([-13 - 7 * s6, -13 + 7 * s6, -1.0]) / 3.0
    return RadauTableau("Radau5", A, c, E, order=5, error_order=3)


RADAU_IIA_5 = _radau_iia_5()


def _lagrange_basis(nodes: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Lagrange basis polynomials of `nodes`, evaluated at `x`. Shape (len(nodes), len(x))."""
    diffs = nodes[:, None] - nodes[None, :]
    np.fill_diagonal(diffs, 1.0)
    denominators = np.prod(diffs, axis=1)
    delta = x[None, :] - nodes[:, None]
    basis = np.empty((nodes.size, x.size))
    for j in range(nodes.size):
        basis[j] = np.prod(np.delete(delta, j, axis=0), axis=0) / denominators[j]
    return basis


def _spectral_data(A: np.ndarray):
    """Eigen-decompose ``A^-1``, ordering the real eigenvalue first.

    Returns ``(eigenvalues, T, TI)`` with the complex-conjugate pair in
    positions 1 and 2, positive imaginary part first.
    """
    values, vectors = np.linalg.eig(np.linalg.inv(A))
    real_index = int(np.argmin(np.abs(values.imag)))
    rest = [i for i in range(values.size) if i != real_index]
    rest.sort(key=lambda i: -values[i].imag)
    order = [real_index, *rest]
    T = vectors[:, order]
    return values[order], T, np.linalg.inv(T)


class RadauIIA(Stepper):
    """Radau IIA collocation, solved by simplified Newton."""

    implicit = True
    supports_mass = True
    default_controller = "predictive"

    def __init__(
        self,
        tableau: RadauTableau = RADAU_IIA_5,
        linear_solve: str = "split",
        jac_method: str = "auto",
        newton: NewtonSettings | None = None,
    ):
        if linear_solve not in ("split", "dense"):
            raise ValueError("linear_solve must be 'split' or 'dense'")
        self.tab = tableau
        self.name = tableau.name
        self.order = tableau.order
        self.error_order = tableau.error_order
        self.interpolant_order = tableau.n_stages
        self.linear_solve = linear_solve
        self.jac_method = jac_method
        # `max_rate=1.0`: for a collocation solve, "slow" is not the same as
        # "failing". The stage equations are solved to a fraction of the local
        # error, so an iteration creeping along at theta = 0.97 still gets there
        # in the eight iterations allowed, and abandoning it would force a step
        # rejection and a refactorisation that cost far more than the extra
        # iteration. Only genuine divergence, theta >= 1, is worth quitting on.
        self.newton = newton or NewtonSettings(
            max_iter=8, tol_factor=0.03, max_rate=1.0
        )

        self.A_inv = np.linalg.inv(tableau.A)
        self.eigenvalues, self.T, self.TI = _spectral_data(tableau.A)

        self._jac_eval: JacobianEvaluator | None = None
        self._reset_cache()
        self.rtol = 1e-6
        self.atol = np.asarray(1e-9)

    def _reset_cache(self) -> None:
        # Jacobian freshness and LU reuse are `JacobianPolicy`'s job, not this
        # stepper's; everything below it is Radau-specific state.
        self._policy = JacobianPolicy()
        self._lu_real: Any = None
        self._last_rate: float | None = None
        self._Z: np.ndarray | None = None
        self._prev: tuple[float, np.ndarray] | None = None
        self._complex_state = False

    def set_tolerances(self, rtol, atol) -> None:
        self.rtol = rtol
        self.atol = np.asarray(atol)

    def _evaluator(self, problem) -> JacobianEvaluator:
        if self._jac_eval is None or self._jac_eval.problem is not problem:
            self._jac_eval = JacobianEvaluator(
                problem,
                self.jac_method,
                threshold=threshold_from_tolerances(self.rtol, self.atol),
            )
            self._reset_cache()
        return self._jac_eval

    # -- linear algebra --------------------------------------------------

    def _factorize(self, problem, h: float):
        """Build the factorisations the chosen solve path needs.

        Both paths produce the real-eigenvalue factorisation, because the error
        estimator needs it regardless of how the stage system was solved.
        """
        M, J = problem.mass, self._policy.J
        lu_real = lu_factorize(
            mass_minus_jacobian(M, J, self.eigenvalues[0].real / h)
        )
        self._lu_real = lu_real

        if self.linear_solve == "split":
            if self._complex_state:
                # With a complex state the conjugate shortcut below is invalid,
                # so the third block gets its own factorisation. Costs one extra
                # LU; the alternative -- assuming conjugate symmetry that is not
                # there -- is silently wrong.
                return (
                    lu_real,
                    lu_factorize(mass_minus_jacobian(M, J, self.eigenvalues[1] / h)),
                    lu_factorize(mass_minus_jacobian(M, J, self.eigenvalues[2] / h)),
                ), 3
            return (lu_real, lu_factorize(
                mass_minus_jacobian(M, J, self.eigenvalues[1] / h)
            )), 2

        n = problem.n
        s = self.tab.n_stages
        Mm = np.eye(n) if M is None else (M.toarray() if hasattr(M, "toarray") else np.asarray(M))
        Jd = J.toarray() if hasattr(J, "toarray") else np.asarray(J)
        # (A^-1 (x) M)/h - I (x) J, assembled explicitly.
        big = np.kron(self.A_inv / h, Mm) - np.kron(np.eye(s), Jd)
        return lu_factorize(big), 2

    def _solve_increment(self, problem, G: np.ndarray) -> np.ndarray:
        """Apply the inverse iteration matrix to the stacked residual `G`."""
        s, n = G.shape
        lu = self._policy.factorization
        if self.linear_solve == "dense":
            return lu.solve(G.reshape(s * n)).reshape(s, n)

        rhs = self.TI @ G                      # (s, n), complex
        dW = np.empty((s, n), dtype=complex)

        if self._complex_state:
            for block in range(s):
                dW[block] = lu[block].solve(rhs[block])
            return self.T @ dW

        lu_real, lu_complex = lu
        dW[0] = lu_real.solve(rhs[0].real)
        dW[1] = lu_complex.solve(rhs[1])
        # For a real state the third block is the conjugate of the second, so
        # solving it would duplicate work and return the conjugate anyway.
        dW[2] = np.conj(dW[1])
        return (self.T @ dW).real

    # -- Newton starting guess -------------------------------------------

    def _predict(self, h: float, n: int) -> np.ndarray:
        """Starting guess for the stage increments Z.

        Extrapolates the previous step's collocation polynomial past its own
        endpoint onto the new stage times. The obvious alternative -- a
        first-order guess ``Z_i = c_i h f`` -- is actively harmful on a stiff
        problem: once `h` grows past the fast timescale, ``h f`` is enormous
        while the true increment is tiny, so Newton starts far outside its
        convergence basin and the step is rejected. Measured on Robertson, that
        difference is a 30% rejection rate versus under 3%.

        Falls back to zero on the first step and whenever no usable history
        exists, which is always safe if unambitious.
        """
        if self._prev is None:
            return np.zeros((self.tab.n_stages, n))

        h_old, Z_old = self._prev
        ratio = h / h_old
        nodes = np.concatenate([[0.0], self.tab.c])
        values = np.vstack([np.zeros(n), Z_old])
        # Q(1) is exactly Z_old[-1] because c[-1] == 1 is itself a node.
        query = 1.0 + self.tab.c * ratio
        return _lagrange_basis(nodes, query).T @ values - Z_old[-1]

    # -- the step --------------------------------------------------------

    def step(self, problem, t, y, f, h) -> StepResult:
        tab = self.tab
        s, n = tab.n_stages, y.size
        jac_eval = self._evaluator(problem)
        njev = nlu = 0
        nfev = 0

        policy = self._policy

        complex_state = np.iscomplexobj(y)
        if complex_state != self._complex_state:
            # The Jacobian's entries are still right; only the matrix built from
            # them has the wrong dtype.
            self._complex_state = complex_state
            policy.invalidate_factorization()

        needs_jac = policy.needs_jacobian(self._last_rate, after_failure=False)
        if needs_jac:
            before = jac_eval.nfev
            policy.store_jacobian(jac_eval(t, y, f))
            nfev += jac_eval.nfev - before
            njev += 1

        if policy.needs_factorization(h):
            try:
                factorization, count = self._factorize(problem, h)
            except (np.linalg.LinAlgError, RuntimeError):
                policy.invalidate_factorization()
                return StepResult(y, None, None, nfev=nfev, njev=njev, nlu=1, ok=False)
            policy.store_factorization(factorization, h)
            nlu += count

        scale = self.atol + self.rtol * np.abs(y)

        # The stage system, expressed as a residual and a linear solve so that
        # the convergence-rate monitoring in `newton.py` drives it. What is
        # Radau-specific is only the two closures: the shape of the unknown
        # (an (s, n) stack of stage increments) and the Kronecker-structured
        # solve that the eigendecomposition above makes cheap.
        stage_nfev = 0
        # One buffer for the whole step rather than one per Newton iteration.
        # It is fully overwritten on every call and never escapes -- `residual`
        # returns a fresh array from the arithmetic below.
        F = np.empty((s, n), dtype=y.dtype)

        def residual(Z: np.ndarray) -> np.ndarray:
            nonlocal stage_nfev
            for i in range(s):
                F[i] = problem.f(t + tab.c[i] * h, y + Z[i])
            stage_nfev += s
            MZ = Z if problem.mass is None else (problem.mass @ Z.T).T
            return F - (self.A_inv @ MZ) / h

        def solve_linear(G: np.ndarray) -> np.ndarray:
            return self._solve_increment(problem, G).astype(y.dtype, copy=False)

        outcome = simplified_newton(
            residual,
            solve_linear,
            self._predict(h, n).astype(y.dtype, copy=False),
            scale,
            self.newton,
        )
        nfev += stage_nfev
        self._last_rate = outcome.rate

        if not outcome.converged:
            # Retry with a fresh Jacobian before giving up; a stale J is the
            # usual reason simplified Newton stalls, and refactorising is far
            # cheaper than the step-size cut the driver would otherwise make.
            if not needs_jac:
                policy.invalidate()
            # History from a step that failed to converge is not a safe basis
            # for extrapolation; the next attempt restarts from zero.
            self._prev = None
            return StepResult(y, None, None, nfev=nfev, njev=njev, nlu=nlu, ok=False)

        Z = outcome.x

        # Stiff accuracy: the last stage *is* the step endpoint.
        y_new = y + Z[-1]

        # Error estimate (Hairer & Wanner II, IV.8.19): filtering the embedded
        # difference through (mu_real/h M - J)^-1 is what keeps the estimate
        # bounded as the stiffness grows, instead of blowing up with |h*lambda|.
        ZE = (Z.T @ tab.E) / h
        error = self._lu_real.solve(f + apply_mass(problem.mass, ZE))

        err_norm = float(np.linalg.norm(error / scale) / np.sqrt(n))
        if err_norm > 1.0:
            # One refinement pass, evaluated at the perturbed state. Recovers a
            # usable estimate on the very stiff steps where the linear filter
            # alone is pessimistic, at the cost of a single RHS evaluation.
            error = self._lu_real.solve(
                problem.f(t, y + error) + apply_mass(problem.mass, ZE)
            )
            nfev += 1

        self._Z = Z
        self._prev = (h, Z)
        policy.mark_step_done()

        return StepResult(
            y_new=y_new,
            f_new=None,
            error=error,
            nfev=nfev,
            njev=njev,
            nlu=nlu,
        )

    def interpolant(self, t, y, f, t_new, y_new, f_new) -> Interpolant:
        """The collocation polynomial through y0 and the stage values."""
        nodes = np.concatenate([[0.0], self.tab.c])
        values = np.vstack([y, y + self._Z])
        return CollocationInterpolant(t, t_new, nodes, values)
