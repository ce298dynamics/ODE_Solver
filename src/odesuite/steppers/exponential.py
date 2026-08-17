"""Exponential time differencing: ETDRK4.

For a *semilinear* problem ``u' = L u + N(u)`` -- a stiff linear operator plus a
mild nonlinearity, which is what a spatial discretisation of a PDE almost always
produces -- the stiffness lives entirely in `L`. An exponential integrator
handles `L` **exactly**, via ``exp(hL)``, and applies a Runge-Kutta treatment
only to `N`. The stability restriction from `L` disappears completely: no
Jacobian, no Newton iteration, no linear solves, and step sizes set by accuracy
rather than by stability.

The coefficients are the *phi functions*

    phi_1(z) = (e^z - 1)/z,   phi_2(z) = (e^z - 1 - z)/z^2,   ...

and evaluating them is where naive implementations fail. For small ``|z|`` the
numerator of ``phi_1`` is the difference of two nearly equal numbers divided by
a small number: at ``z ~ 1e-8`` catastrophic cancellation leaves no correct
digits at all. Since a spectral discretisation always contains modes with
``z`` near zero *and* modes with ``z`` hugely negative, this is not an edge
case -- it is every run.

**Kassam & Trefethen's fix** (SIAM J. Sci. Comput. 26 (2005) 1214) is Cauchy's
integral formula: a function analytic near `z` equals its mean over a circle
around `z`. Averaging the same expression over a contour of radius 1 evaluates
it where the arithmetic is well conditioned, and the cancellation never happens.
It costs a few dozen extra evaluations per distinct `h` and is exact to machine
precision. `tests/test_exponential.py` measures the naive formula losing eight
digits where the contour version loses none.
"""

from __future__ import annotations

import numpy as np

from ..dense import HermiteInterpolant, Interpolant
from ..problem import ODEProblem
from .base import Stepper, StepResult

__all__ = [
    "semilinear_problem",
    "phi_coefficients_contour",
    "phi1_naive",
    "ETDRK4",
]


def semilinear_problem(linear, nonlinear, t_span, u0, args: tuple = ()):
    """Build an `ODEProblem` for ``u' = L u + N(t, u)``.

    Parameters
    ----------
    linear
        The diagonal of `L`, as a 1-D array. Diagonal because the intended use
        is a spectral discretisation, where the linear operator is diagonal in
        Fourier space -- which is exactly what makes exponential integrators
        cheap.
    nonlinear
        ``N(t, u, *args)``, returning an array shaped like `u`.

    The resulting problem is a perfectly ordinary IVP with ``f = L u + N``, so
    any method can integrate it; `ETDRK4` additionally reads the split off the
    attached attributes.
    """
    linear = np.asarray(linear)
    u0 = np.atleast_1d(np.asarray(u0))
    if linear.shape != u0.shape:
        raise ValueError(
            f"linear operator diagonal has shape {linear.shape}, expected {u0.shape}"
        )

    def f(t, u, *extra):
        return linear * u + np.asarray(nonlinear(t, u, *extra)).reshape(-1)

    problem = ODEProblem(f=f, t_span=t_span, y0=u0, args=args)
    problem.linear_operator = linear      # type: ignore[attr-defined]
    problem.nonlinear_part = nonlinear    # type: ignore[attr-defined]
    return problem


def phi1_naive(z):
    """``(e^z - 1)/z`` evaluated directly. Present only to be compared against.

    Used by `tests/test_exponential.py` to demonstrate the cancellation the
    contour method avoids; never used to integrate anything.
    """
    z = np.asarray(z, dtype=complex)
    return (np.exp(z) - 1.0) / z


def phi_coefficients_contour(hL: np.ndarray, h: float, n_points: int = 32):
    """The four ETDRK4 coefficient vectors, by contour integration.

    Each is a combination of phi functions of ``hL``. Rather than evaluating
    those formulas at ``hL`` -- where the small-modulus entries lose all
    precision -- each is averaged over a circle of radius 1 centred on the
    entry, which is exact by Cauchy's integral formula and numerically benign
    everywhere on the contour.

    Returns ``(Q, f1, f2, f3)``, each shaped like `hL`.
    """
    hL = np.asarray(hL)
    # Roots of unity offset by half a step, so no sample lands on the real axis
    # where a pole of the integrand could sit.
    roots = np.exp(1j * np.pi * (np.arange(1, n_points + 1) - 0.5) / n_points)
    z = hL[:, None] + roots[None, :]

    Q = h * np.real(np.mean((np.exp(z / 2) - 1.0) / z, axis=1))
    f1 = h * np.real(
        np.mean((-4.0 - z + np.exp(z) * (4.0 - 3.0 * z + z**2)) / z**3, axis=1)
    )
    f2 = h * np.real(np.mean((2.0 + z + np.exp(z) * (z - 2.0)) / z**3, axis=1))
    f3 = h * np.real(
        np.mean((-4.0 - 3.0 * z - z**2 + np.exp(z) * (4.0 - z)) / z**3, axis=1)
    )
    return Q, f1, f2, f3


class ETDRK4(Stepper):
    """Fourth-order exponential time differencing Runge-Kutta (Cox & Matthews).

    Fixed step by construction: every coefficient depends on `h`, so varying it
    would mean rebuilding them each step and discarding the contour work. The
    coefficients are cached and rebuilt only when `h` actually changes.

    Costs four nonlinear evaluations per step and no linear algebra whatsoever.
    """

    order = 4
    error_order = 3
    interpolant_order = 3
    adaptive = False
    supports_mass = False
    # The step is driven by exp(hL) and four evaluations of N alone; the full
    # right-hand side is never needed.
    uses_f = False
    name = "ETDRK4"

    def __init__(self, contour_points: int = 32):
        self.contour_points = contour_points
        self._cached_h: float | None = None
        self._coefficients: tuple | None = None

    def validate(self, problem) -> None:
        super().validate(problem)
        if not hasattr(problem, "linear_operator"):
            raise ValueError(
                "ETDRK4 needs a semilinear splitting u' = L u + N(u); build the "
                "problem with odesuite.semilinear_problem(...)"
            )

    def _prepare(self, problem, h: float):
        if self._cached_h is not None and h == self._cached_h:
            return self._coefficients
        L = problem.linear_operator
        hL = h * L
        E = np.exp(hL)
        E2 = np.exp(hL / 2.0)
        Q, f1, f2, f3 = phi_coefficients_contour(hL, h, self.contour_points)
        self._coefficients = (E, E2, Q, f1, f2, f3)
        self._cached_h = h
        return self._coefficients

    def step(self, problem, t, y, f, h) -> StepResult:
        E, E2, Q, f1, f2, f3 = self._prepare(problem, h)
        N = problem.nonlinear_part
        args = problem.args

        Nu = np.asarray(N(t, y, *args)).reshape(-1)
        a = E2 * y + Q * Nu
        Na = np.asarray(N(t + h / 2, a, *args)).reshape(-1)
        b = E2 * y + Q * Na
        Nb = np.asarray(N(t + h / 2, b, *args)).reshape(-1)
        c = E2 * a + Q * (2.0 * Nb - Nu)
        Nc = np.asarray(N(t + h, c, *args)).reshape(-1)

        y_new = E * y + Nu * f1 + 2.0 * (Na + Nb) * f2 + Nc * f3

        return StepResult(y_new=y_new, f_new=None, error=None, nfev=4)

    def interpolant(self, t, y, f, t_new, y_new, f_new) -> Interpolant:
        return HermiteInterpolant(t, y, f, t_new, y_new, f_new)
