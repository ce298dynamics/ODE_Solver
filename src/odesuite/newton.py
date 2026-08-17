"""Simplified Newton iteration and the Jacobian-freshness policy.

Two ideas do most of the work in any stiff solver, and both live here rather
than inside a particular method:

**Simplified Newton.** The iteration matrix is held fixed across iterations (and
usually across steps), so each iteration costs one triangular solve instead of a
Jacobian evaluation plus a factorisation. Convergence degrades from quadratic to
linear, but a factorisation costs O(n^3) against O(n^2) for the solve, so on
anything but a tiny system this is a large net win.

**Convergence-rate monitoring.** Successive corrections shrink by roughly a
constant factor ``theta``. Tracking it gives three things for free: a
termination test that predicts the remaining error rather than guessing from the
last correction, early detection of divergence, and the signal that tells the
step controller when the Jacobian has gone stale.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

__all__ = ["NewtonResult", "NewtonSettings", "simplified_newton", "JacobianPolicy"]


@dataclass
class NewtonResult:
    """Outcome of a Newton solve."""

    converged: bool
    x: np.ndarray
    n_iter: int
    #: Estimated linear convergence rate; None when too few iterations to infer.
    rate: float | None = None
    #: Norm of the final correction, scaled by the tolerance weights.
    correction: float = np.inf


@dataclass
class NewtonSettings:
    max_iter: int = 10
    #: Iteration stops when the *predicted remaining* error falls below this
    #: fraction of the integration tolerance. Solving the nonlinear system much
    #: tighter than the local truncation error is wasted work.
    tol_factor: float = 0.03
    #: Above this rate, convergence is too slow to be worth continuing.
    max_rate: float = 0.95


def simplified_newton(
    residual,
    solve_linear,
    x0: np.ndarray,
    scale: np.ndarray,
    settings: NewtonSettings | None = None,
) -> NewtonResult:
    """Solve ``residual(x) = 0`` with a frozen iteration matrix.

    Parameters
    ----------
    residual
        Callable returning the residual vector at `x`.
    solve_linear
        Applies the (already factorised) inverse iteration matrix to a vector.
    x0
        Starting guess.
    scale
        Per-component weights, normally ``atol + rtol*|y|``. All norms below are
        taken with respect to these, so the test means the same thing for every
        component regardless of magnitude.

    Notes
    -----
    The termination test uses ``theta/(1-theta) * |dx|``, the sum of the
    remaining geometric series, rather than ``|dx|`` itself. With a slowly
    converging iteration those differ by orders of magnitude, and stopping on
    the raw correction would accept a badly-solved stage.
    """
    settings = settings or NewtonSettings()
    x = x0.copy()
    dx_norm_old: float | None = None
    rate: float | None = None
    dx_norm = np.inf

    for k in range(settings.max_iter):
        dx = solve_linear(residual(x))
        dx_norm = float(np.linalg.norm(dx / scale) / np.sqrt(dx.size))

        if dx_norm_old is not None and dx_norm_old > 0:
            rate = dx_norm / dx_norm_old
            if rate >= settings.max_rate:
                # Diverging, or converging so slowly that refactorising and
                # restarting will be cheaper than grinding on.
                return NewtonResult(False, x, k + 1, rate, dx_norm)

        x = x + dx

        if dx_norm == 0.0:
            return NewtonResult(True, x, k + 1, rate, 0.0)

        if rate is not None:
            remaining = rate / (1.0 - rate) * dx_norm
            if remaining < settings.tol_factor:
                return NewtonResult(True, x, k + 1, rate, dx_norm)
        elif dx_norm < settings.tol_factor:
            # First iteration already tiny: the initial guess was good enough.
            return NewtonResult(True, x, k + 1, rate, dx_norm)

        dx_norm_old = dx_norm

    return NewtonResult(False, x, settings.max_iter, rate, dx_norm)


class JacobianPolicy:
    """Decides when to recompute the Jacobian and when to refactorise.

    Both are expensive and neither is needed every step. A Jacobian stays usable
    while Newton keeps converging briskly; the factorisation additionally
    depends on the step size, so it must be redone whenever `h` moves
    appreciably even if `J` itself is still good.
    """

    #: Recompute J when the observed Newton rate exceeds this.
    stale_rate = 0.3
    #: Refactorise when h has drifted by more than this fraction.
    step_change = 0.2

    def __init__(self) -> None:
        # `Any` rather than a concrete type: `J` may be dense or sparse, and the
        # factorisation is whatever the chosen linear-solve path produced -- a
        # single object for the dense route, a tuple of them for the split one.
        self.J: Any = None
        self.factorization: Any = None
        self.h_factored: float | None = None
        self.jacobian_current = False

    def needs_jacobian(self, last_rate: float | None, after_failure: bool) -> bool:
        if self.J is None or after_failure:
            return True
        if self.jacobian_current:
            return False
        return last_rate is None or last_rate > self.stale_rate

    def needs_factorization(self, h: float) -> bool:
        if self.factorization is None or self.h_factored is None:
            return True
        return abs(h - self.h_factored) > self.step_change * abs(self.h_factored)

    def store_jacobian(self, J) -> None:
        self.J = J
        self.jacobian_current = True
        # A new Jacobian invalidates any factorisation built from the old one.
        self.factorization = None
        self.h_factored = None

    def store_factorization(self, factorization, h: float) -> None:
        self.factorization = factorization
        self.h_factored = h

    def invalidate_factorization(self) -> None:
        """Drop the factorisation but keep the Jacobian.

        For the case where `J` is still a faithful derivative but the matrix
        built from it is no longer usable -- a state that has just become
        complex, say, where the entries are right but the dtype is not.
        """
        self.factorization = None
        self.h_factored = None

    def invalidate(self) -> None:
        """Discard the Jacobian and everything derived from it.

        Used after a nonlinear solve fails on an already-stale `J`: grinding on
        with the Jacobian that just failed to converge is the one thing known
        not to work, so the next attempt starts from a fresh evaluation.
        """
        self.J = None
        self.jacobian_current = False
        self.invalidate_factorization()

    def mark_step_done(self) -> None:
        """After a completed step the Jacobian is one step out of date."""
        self.jacobian_current = False
