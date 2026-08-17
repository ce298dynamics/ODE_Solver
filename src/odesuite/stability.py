"""Linear stability: the function ``R(z)`` and the region where ``|R| <= 1``.

Applying a one-step method to Dahlquist's test problem ``y' = lambda y`` gives
``y_1 = R(h*lambda) y_0``. The set where ``|R(z)| <= 1`` is where errors decay
rather than grow, and its shape decides which problems a method can handle at
all: an explicit method has a *bounded* region, which is exactly the stiffness
restriction, while an A-stable method covers the whole left half-plane.

Two ways to evaluate it, and the library uses whichever applies:

`stability_function`
    Runs the actual stepper for one step with ``h = 1``. Works for every
    method, exercises the shipping code path, and therefore cannot disagree
    with the implementation. Costs one step per sample point.

`tableau_stability_function`
    For a Butcher tableau, ``R(z) = det(I - zA + z e b^T) / det(I - zA)`` by the
    matrix determinant lemma. Exact, and batched over the whole grid at once --
    a few milliseconds where stepping point by point takes seconds. Used for
    the grids an interactive display needs, and checked against the stepper in
    `tests/test_stability.py`.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "stability_function",
    "tableau_stability_function",
    "stability_grid",
    "classify_stability",
    "REAL_AXIS_LIMITS",
]

#: Published real-axis stability intervals, for cross-checking. The largest
#: ``|h*lambda|`` on the negative real axis with ``|R| <= 1``.
REAL_AXIS_LIMITS = {
    "RK23": 2.51,
    "DOPRI5": 3.31,
    "RKF45": 3.67,
}


def tableau_stability_function(tableau, z) -> np.ndarray:
    """``R(z)`` for a Butcher tableau, evaluated over an array of `z`.

    Uses ``det(I - zA + z e b^T) / det(I - zA)``, which follows from the matrix
    determinant lemma applied to ``R(z) = 1 + z b^T (I - zA)^-1 e``. Batched
    over every sample at once.
    """
    z = np.asarray(z, dtype=complex)
    shape = z.shape
    flat = z.ravel()

    A = np.asarray(tableau.A, dtype=complex)
    b = np.asarray(tableau.b, dtype=complex)
    s = b.size
    identity = np.eye(s, dtype=complex)
    outer = np.outer(np.ones(s, dtype=complex), b)

    # (N, s, s) stacks, one matrix per sample.
    scaled = flat[:, None, None] * A[None, :, :]
    denominator = np.linalg.det(identity[None, :, :] - scaled)
    numerator = np.linalg.det(
        identity[None, :, :] - scaled + flat[:, None, None] * outer[None, :, :]
    )

    with np.errstate(divide="ignore", invalid="ignore"):
        values = numerator / denominator
    # A zero denominator is a pole of R: unbounded, hence unstable.
    values[denominator == 0] = np.inf
    return values.reshape(shape)


def stability_function(method, z) -> np.ndarray:
    """``R(z)`` by running `method` for one step of ``y' = z y`` with ``h = 1``.

    General but slow: one full step per sample. Entries where the step fails --
    a singular iteration matrix, Newton divergence -- come back as NaN.
    """
    from .problem import ODEProblem
    from .steppers import make_stepper

    z = np.asarray(z, dtype=complex)
    flat = z.ravel()
    out = np.empty(flat.size, dtype=complex)

    for index, value in enumerate(flat):
        stepper = make_stepper(method)
        stepper.set_tolerances(1e-12, 1e-14)
        problem = ODEProblem(
            f=lambda t, y, v=value: v * y,
            t_span=(0.0, 1.0),
            y0=np.array([1.0 + 0.0j]),
            jac=lambda t, y, v=value: np.array([[v]]),
        )
        try:
            result = stepper.step(
                problem, 0.0, problem.y0.copy(), problem.f(0.0, problem.y0), 1.0
            )
            out[index] = result.y_new[0] if result.ok else np.nan
        except Exception:
            out[index] = np.nan
    return out.reshape(z.shape)


def stability_grid(method, real, imaginary, prefer_fast: bool = True):
    """``|R(z)|`` on the grid ``real x imaginary``. Returns shape ``(len(imaginary), len(real))``.

    Takes the batched tableau route where the method has a Butcher tableau, and
    falls back to stepping otherwise (Rosenbrock, exponential, symplectic).
    """
    real = np.asarray(real, dtype=float)
    imaginary = np.asarray(imaginary, dtype=float)
    Z = real[None, :] + 1j * imaginary[:, None]

    tableau = _tableau_for(method) if prefer_fast else None
    if tableau is not None:
        return np.abs(tableau_stability_function(tableau, Z))
    return np.abs(stability_function(method, Z))


def _tableau_for(method):
    """The Butcher tableau behind `method`, if it has one."""
    from .steppers import make_stepper
    from .steppers.erk import ExplicitRungeKutta
    from .steppers.irk import RadauIIA

    try:
        stepper = make_stepper(method) if isinstance(method, str) else method
    except Exception:
        return None

    if isinstance(stepper, ExplicitRungeKutta):
        return stepper.tab
    if isinstance(stepper, RadauIIA):
        # Radau IIA is a collocation method, so its tableau slots into the same
        # formula; it just has a full A rather than a strictly lower one, which
        # is precisely why R is rational instead of polynomial.
        class _Adapter:
            A = stepper.tab.A
            b = stepper.tab.b

        return _Adapter
    return None


def classify_stability(method, verbose: bool = False) -> dict:
    """Real-axis limit, A-stability and L-stability for one method."""
    x = -np.logspace(-3, 3, 1500)
    magnitude = stability_grid(method, x, np.array([0.0]))[0]
    unstable = np.nonzero(magnitude > 1.0 + 1e-12)[0]
    real_limit = float(abs(x[unstable[0]])) if unstable.size else np.inf

    real = -np.logspace(-2, 3, 60)
    imaginary = np.concatenate(
        [-np.logspace(-2, 3, 30)[::-1], [0.0], np.logspace(-2, 3, 30)]
    )
    half_plane = stability_grid(method, real, imaginary)
    a_stable = bool(np.nanmax(half_plane) <= 1.0 + 1e-8)

    at_infinity = float(stability_grid(method, np.array([-1e10]), np.array([0.0]))[0, 0])
    l_stable = a_stable and at_infinity < 1e-6

    report = {
        "real_axis_limit": real_limit,
        "A_stable": a_stable,
        "L_stable": l_stable,
        "R_at_minus_infinity": at_infinity,
    }
    if verbose:
        limit = "inf" if np.isinf(real_limit) else f"{real_limit:.2f}"
        print(
            f"  {str(method):10s} |h*lam| < {limit:>6s}   A={str(a_stable):5s}  "
            f"L={str(l_stable):5s}  |R(-inf)|={at_infinity:.3e}"
        )
    return report
