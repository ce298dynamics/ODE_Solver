"""One generic explicit Runge-Kutta stepper, driven entirely by a Butcher tableau.

Every explicit method in the library -- RK23, RKF45, Cash-Karp, DOPRI5, Tsit5 --
is this class holding different coefficients. Adding a sixth costs a few lines of
data in `tableaux.py` and no code at all.
"""

from __future__ import annotations

import numpy as np

from ..dense import HermiteInterpolant, Interpolant, RKPolynomialInterpolant
from ..tableaux import ButcherTableau, get_tableau
from .base import Stepper, StepResult

__all__ = ["ExplicitRungeKutta"]


class ExplicitRungeKutta(Stepper):
    """Embedded explicit Runge-Kutta pair.

    The stage derivatives from the most recent `step` are retained so that
    `interpolant` can build a native continuous extension without recomputing
    anything.
    """

    implicit = False
    supports_mass = False

    def __init__(self, tableau: ButcherTableau | str):
        if isinstance(tableau, str):
            tableau = get_tableau(tableau)
        self.tab = tableau
        self.name = tableau.name
        self.order = tableau.order
        self.error_order = tableau.error_order
        self.interpolant_order = (
            tableau.interpolant_order if tableau.P is not None else 3
        )
        self.n_stages = tableau.n_stages
        # A pair without embedded weights has no error estimate, so it cannot
        # choose its own step: the driver will require `n_steps` or
        # `first_step`, as it does for the symplectic methods.
        self.adaptive = tableau.embedded
        self._K: np.ndarray | None = None
        self._h: float = 0.0

    def step(self, problem, t, y, f, h) -> StepResult:
        tab = self.tab
        A, b, c, e = tab.A, tab.b, tab.c, tab.e
        s = self.n_stages

        K = np.empty((s, y.size), dtype=y.dtype)
        K[0] = f
        for i in range(1, s):
            dy = h * (A[i, :i] @ K[:i])
            K[i] = problem.f(t + c[i] * h, y + dy)

        y_new = y + h * (b @ K)

        # For an FSAL tableau the final stage is exactly f(t+h, y_new), because
        # the last row of A equals b and c[-1] == 1. The driver carries it into
        # the next step, so such methods cost s-1 evaluations per step.
        f_new = K[-1] if tab.fsal else None

        self._K = K
        self._h = h

        return StepResult(
            y_new=y_new,
            f_new=f_new,
            error=None if e is None else h * (e @ K),
            nfev=s - 1,
        )

    def interpolant(self, t, y, f, t_new, y_new, f_new) -> Interpolant:
        tab = self.tab
        if tab.P is not None and self._K is not None:
            return RKPolynomialInterpolant(
                t, t_new, y, self._K, tab.P, tab.interpolant_order
            )
        # No published continuous extension: cubic Hermite through both
        # endpoints. Costs nothing, since the driver holds f at both ends.
        return HermiteInterpolant(t, y, f, t_new, y_new, f_new)
