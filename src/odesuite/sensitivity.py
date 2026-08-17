"""Forward parameter sensitivities.

Answers "how does the solution move when a parameter moves" -- the derivative
``S = dy/dp`` -- which is what parameter fitting, optimal control and
uncertainty propagation all need.

Differentiating ``y' = f(t, y, p)`` with respect to `p` gives the *variational
equations*

    S' = J S + df/dp,      S(t0) = dy0/dp

with ``J = df/dy``. These are linear in `S` and share the Jacobian the stiff
solvers already compute, so they are appended to the state and integrated by the
same driver: an ``n(1+q)`` system solved once. This is *internal
differentiation* -- the sensitivities follow the same step sequence as the
state, so the derivative that comes out is the derivative of the computed
solution rather than of an unrelated nearby one.

Finite-differencing the whole solve instead would cost `q` extra integrations,
each with independently chosen steps, and would inherit the usual
cancellation problem: the difference of two `1e-10`-accurate trajectories
divided by a small perturbation.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.linalg import block_diag

from .driver import solve
from .linalg import EPS
from .problem import ODEProblem
from .solution import Stats

__all__ = ["SensitivitySolution", "forward_sensitivities"]


@dataclass
class SensitivitySolution:
    """Solution of the state together with its parameter sensitivities."""

    t: np.ndarray
    #: State, shape ``(n, k)``.
    y: np.ndarray
    #: Sensitivities, shape ``(n, q, k)``: ``S[i, j, m] = dy_i/dp_j`` at ``t[m]``.
    S: np.ndarray
    status: str = "finished"
    message: str = ""
    stats: Stats = field(default_factory=Stats)
    method: str = ""

    @property
    def success(self) -> bool:
        return self.status in ("finished", "terminated")

    def S_at_end(self) -> np.ndarray:
        """Sensitivity matrix at the final time, shape ``(n, q)``."""
        return self.S[:, :, -1]

    def __repr__(self) -> str:
        n, q, k = self.S.shape
        return (
            f"SensitivitySolution(n={n}, q={q}, points={k}, "
            f"status={self.status!r}, {self.stats})"
        )


def _finite_difference_dfdp(f, t, y, p, f0):
    """``df/dp`` by forward differences. Costs q RHS evaluations."""
    q = p.size
    out = np.empty((y.size, q))
    steps = np.sqrt(EPS) * np.maximum(np.abs(p), 1e-8)
    for j in range(q):
        p1 = p.copy()
        p1[j] += steps[j]
        dp = p1[j] - p[j]
        out[:, j] = (np.asarray(f(t, y, p1)).reshape(-1) - f0) / dp
    return out


def _finite_difference_jac(f, t, y, p, f0):
    """``df/dy`` by forward differences. Costs n RHS evaluations."""
    n = y.size
    out = np.empty((n, n))
    steps = np.sqrt(EPS) * np.maximum(np.abs(y), 1e-8)
    for j in range(n):
        y1 = y.copy()
        y1[j] += steps[j]
        dy = y1[j] - y[j]
        out[:, j] = (np.asarray(f(t, y1, p)).reshape(-1) - f0) / dy
    return out


def forward_sensitivities(
    f,
    t_span,
    y0,
    p,
    *,
    jac=None,
    dfdp=None,
    dy0dp=None,
    method: str = "radau",
    rtol: float = 1e-8,
    atol=1e-10,
    t_eval=None,
    **solve_kwargs,
) -> SensitivitySolution:
    """Integrate ``y' = f(t, y, p)`` together with ``S = dy/dp``.

    Parameters
    ----------
    f
        Right-hand side, called as ``f(t, y, p)`` with `p` an array.
    t_span, y0
        As for `ODEProblem`.
    p
        Parameter vector, length `q`.
    jac
        Optional ``df/dy`` as ``jac(t, y, p)``. Finite-differenced if omitted.
    dfdp
        Optional ``df/dp`` as ``dfdp(t, y, p)``, shape ``(n, q)``. Finite-
        differenced if omitted.
    dy0dp
        Optional ``dy0/dp``, shape ``(n, q)``. Defaults to zero, which is right
        whenever the initial condition does not itself depend on `p`. Passing
        the identity here (with ``dfdp`` zero) yields ``dy/dy0`` instead, the
        propagation matrix multiple shooting needs.
    method
        Any method name the driver accepts. Defaults to ``"radau"``: the
        augmented system inherits the stiffness of the original, and often
        sharpens it, since the variational equations are driven by `J`.

    Returns
    -------
    SensitivitySolution

    Notes
    -----
    The Jacobian handed to an implicit method is ``blkdiag(J, I_q (x) J)``. That
    is the exact derivative of the augmented right-hand side except for the
    block coupling `S` back into `y`, which involves second derivatives of `f`.
    Dropping it makes the iteration quasi-Newton rather than Newton -- it may
    cost an occasional extra iteration but cannot affect the converged answer,
    since the *residual* is always evaluated exactly.

    **Match `rtol` to the derivatives you supply.** When `jac` or `dfdp` is
    omitted it is finite-differenced *inside* the augmented right-hand side, so
    the sensitivity equations are driven by a term carrying ``O(sqrt(eps))``
    error -- roughly ``1e-8``. Asking for ``rtol=1e-12`` in that case is
    self-defeating: the controller keeps cutting the step chasing an accuracy
    the right-hand side cannot deliver, and the solve becomes orders of
    magnitude slower without becoming more accurate. Use ``rtol`` around
    ``1e-9`` with differenced derivatives, and save the tight tolerances for
    when both `jac` and `dfdp` are supplied analytically.
    """
    y0 = np.atleast_1d(np.asarray(y0, dtype=float))
    p = np.atleast_1d(np.asarray(p, dtype=float))
    n, q = y0.size, p.size

    S0 = np.zeros((n, q)) if dy0dp is None else np.asarray(dy0dp, dtype=float)
    if S0.shape != (n, q):
        raise ValueError(f"dy0dp must have shape {(n, q)}, got {S0.shape}")

    def f_augmented(t, Y):
        y = Y[:n]
        S = Y[n:].reshape(n, q)
        f0 = np.asarray(f(t, y, p)).reshape(-1)
        J = np.asarray(jac(t, y, p)) if jac is not None else _finite_difference_jac(
            f, t, y, p, f0
        )
        Fp = (
            np.asarray(dfdp(t, y, p))
            if dfdp is not None
            else _finite_difference_dfdp(f, t, y, p, f0)
        )
        return np.concatenate([f0, (J @ S + Fp).ravel()])

    def jac_augmented(t, Y):
        y = Y[:n]
        f0 = np.asarray(f(t, y, p)).reshape(-1)
        J = np.asarray(jac(t, y, p)) if jac is not None else _finite_difference_jac(
            f, t, y, p, f0
        )
        return block_diag(J, *([J] * q))

    augmented = ODEProblem(
        f=f_augmented,
        t_span=t_span,
        y0=np.concatenate([y0, S0.ravel()]),
        jac=jac_augmented,
    )

    sol = solve(
        augmented, method=method, rtol=rtol, atol=atol, t_eval=t_eval, **solve_kwargs
    )

    k = sol.t.size
    # The augmented state is laid out row-major per time point, so the
    # sensitivity block reshapes directly into (n, q, k) once the time axis is
    # moved to the end.
    S = sol.y[n:].reshape(n, q, k)

    return SensitivitySolution(
        t=sol.t,
        y=sol.y[:n],
        S=S,
        status=sol.status,
        message=sol.message,
        stats=sol.stats,
        method=sol.method,
    )
