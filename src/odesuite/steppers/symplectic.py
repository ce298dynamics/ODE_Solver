"""Symplectic integrators for separable Hamiltonian systems.

For a Hamiltonian ``H(q, p) = T(p) + V(q)`` the exact flow preserves the
symplectic two-form, and with it the phase-space volume and -- to within a
bounded oscillation -- the energy. A symplectic integrator preserves that
structure *exactly*, at every step, rather than approximately.

The practical consequence is qualitative rather than quantitative. A
conventional high-order method like DOPRI5 is far more accurate over one orbit,
but its energy error accumulates monotonically: integrate a planet for a hundred
thousand orbits and it spirals. Stormer-Verlet is only second order and its
per-orbit error is much larger, yet its energy error stays *bounded* forever, so
the orbit remains an orbit. `benchmarks/energy_drift.py` shows the two curves.

Two structural requirements follow, and both are enforced here:

* The system must be **separable** -- ``q' = v``, ``v' = a(t, q)`` -- so the two
  halves of the flow can be integrated exactly in turn.
* The step size must be **constant**. Adaptive stepping destroys symplecticity;
  a variable-step "symplectic" method is neither. These steppers therefore set
  ``adaptive = False`` and the driver requires `n_steps` or `first_step`.

Higher orders are built by *composition*: a symmetric method of order ``2k``
composed as ``S(z h) S(z0 h) S(z h)`` with the triple-jump weights below is
symmetric of order ``2k + 2``. Applying that recursively generates orders 4, 6,
8, ... from Verlet with no coefficient tables to mistype -- the same
"derive, don't transcribe" tactic used for Radau's eigendecomposition.
"""

from __future__ import annotations

import numpy as np

from ..dense import HermiteInterpolant, Interpolant
from ..problem import ODEProblem
from .base import StepResult, Stepper

__all__ = [
    "second_order_problem",
    "StormerVerlet",
    "CompositionMethod",
    "triple_jump_weights",
    "SYMPLECTIC_METHODS",
]


def second_order_problem(acceleration, t_span, q0, v0, args: tuple = (), jac=None):
    """Build an `ODEProblem` for ``q'' = a(t, q)`` in the form the symplectic
    steppers require.

    The state is the concatenation ``[q, v]`` and the right-hand side is
    ``[v, a(t, q)]``, so the problem is an ordinary IVP that *any* method can
    integrate. The acceleration is additionally attached to the problem, which
    is what lets a symplectic stepper split the flow.
    """
    q0 = np.atleast_1d(np.asarray(q0, dtype=float))
    v0 = np.atleast_1d(np.asarray(v0, dtype=float))
    if q0.shape != v0.shape:
        raise ValueError(f"q0 and v0 must match, got {q0.shape} and {v0.shape}")
    d = q0.size

    def f(t, y, *extra):
        return np.concatenate([y[d:], np.asarray(acceleration(t, y[:d], *extra)).reshape(-1)])

    problem = ODEProblem(
        f=f, t_span=t_span, y0=np.concatenate([q0, v0]), jac=jac, args=args
    )
    problem.acceleration = acceleration     # type: ignore[attr-defined]
    problem.n_coordinates = d               # type: ignore[attr-defined]
    return problem


def triple_jump_weights(order: int) -> np.ndarray:
    """Composition weights giving a method of `order` from a symmetric order-2 base.

    Yoshida's triple jump: if ``S`` is symmetric of order ``2k``, then

        S(z h) . S(z0 h) . S(z h),    z = 1/(2 - 2^(1/(2k+1))),
                                      z0 = -2^(1/(2k+1)) / (2 - 2^(1/(2k+1)))

    is symmetric of order ``2k + 2``. The construction is applied recursively,
    so the returned weights are computed from that closed form rather than
    copied from a table. Order 6 costs 9 base steps this way against Yoshida's
    optimised 7 -- a modest efficiency loss bought in exchange for coefficients
    that cannot be mistyped and that generalise to any even order.
    """
    if order < 2 or order % 2:
        raise ValueError(f"order must be even and at least 2, got {order}")
    weights = np.array([1.0])
    for k in range(1, order // 2):
        gamma = 2.0 ** (1.0 / (2 * k + 1))
        z = 1.0 / (2.0 - gamma)
        z0 = -gamma / (2.0 - gamma)
        weights = np.concatenate([z * weights, z0 * weights, z * weights])
    return weights


class StormerVerlet(Stepper):
    """Stormer-Verlet (velocity Verlet). Second order, symmetric, symplectic.

    One acceleration evaluation per step: the end-of-step acceleration is
    carried into the next step's opening half-kick, which is the leapfrog
    structure rather than an optimisation.
    """

    order = 2
    error_order = 1
    interpolant_order = 3
    adaptive = False
    name = "Verlet"

    def validate(self, problem) -> None:
        super().validate(problem)
        if not hasattr(problem, "acceleration"):
            raise ValueError(
                "symplectic methods need a separable second-order system; "
                "build the problem with odesuite.second_order_problem(...)"
            )

    def step(self, problem, t, y, f, h) -> StepResult:
        d = problem.n_coordinates
        q, v = y[:d], y[d:]
        args = problem.args

        a0 = np.asarray(problem.acceleration(t, q, *args)).reshape(-1)
        v_half = v + 0.5 * h * a0
        q_new = q + h * v_half
        a1 = np.asarray(problem.acceleration(t + h, q_new, *args)).reshape(-1)
        v_new = v_half + 0.5 * h * a1

        return StepResult(
            y_new=np.concatenate([q_new, v_new]),
            f_new=np.concatenate([v_new, a1]),
            error=None,          # no embedded estimate: this is a fixed-step method
            nfev=2,
        )

    def interpolant(self, t, y, f, t_new, y_new, f_new) -> Interpolant:
        return HermiteInterpolant(t, y, f, t_new, y_new, f_new)


class CompositionMethod(Stepper):
    """Higher-order symplectic method by composing Stormer-Verlet substeps.

    Symmetric composition preserves symplecticity and time-reversibility, so the
    composed method keeps every structural property of the base method while
    raising the order.
    """

    adaptive = False
    interpolant_order = 3

    def __init__(self, order: int = 4):
        self.weights = triple_jump_weights(order)
        self.base = StormerVerlet()
        self.order = order
        self.error_order = order - 1
        self.name = f"Yoshida{order}"

    def validate(self, problem) -> None:
        self.base.validate(problem)

    def step(self, problem, t, y, f, h) -> StepResult:
        state = y
        time = t
        nfev = 0
        f_new = f
        for w in self.weights:
            result = self.base.step(problem, time, state, f_new, w * h)
            state = result.y_new
            f_new = result.f_new
            time += w * h
            nfev += result.nfev
        return StepResult(y_new=state, f_new=f_new, error=None, nfev=nfev)

    def interpolant(self, t, y, f, t_new, y_new, f_new) -> Interpolant:
        return HermiteInterpolant(t, y, f, t_new, y_new, f_new)


SYMPLECTIC_METHODS = {
    "verlet": StormerVerlet,
    "yoshida4": (lambda: CompositionMethod(4)),
    "yoshida6": (lambda: CompositionMethod(6)),
    "yoshida8": (lambda: CompositionMethod(8)),
}
