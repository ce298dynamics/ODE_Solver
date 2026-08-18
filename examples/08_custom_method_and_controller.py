"""Add a Runge-Kutta method, and a step-size controller, without touching the library.

    py -3.10 examples/08_custom_method_and_controller.py

Butcher tableaux are data here, not code: one generic explicit stepper drives
every named explicit method, so a new one is a table of coefficients. This
example registers Ralston's third-order method and then *measures* its order,
rather than trusting the label.

A controller sees only a scalar error norm, the method's error order, and the
step just taken -- never the method itself. That is what lets a user-written
controller drive a user-written method with nothing in the library changed.
"""

from __future__ import annotations

import numpy as np

from odesuite import ButcherTableau, Controller, ExplicitRungeKutta, ODEProblem, solve

_B = np.array([2 / 9, 1 / 3, 4 / 9])          # Ralston, third order
# The embedded companion is the explicit midpoint method, which is already
# sitting inside this tableau: stage 2 is evaluated at c = 1/2, so `y + h*k2` is
# a second-order estimate that costs nothing extra.
_B_HAT = np.array([0.0, 1.0, 0.0])

# Consistency is the cheapest check there is, and it catches the most common way
# of getting an embedded pair wrong -- borrowing b_hat from a *different*
# tableau. Weights that do not sum to 1 are not a method of any order, and the
# resulting error estimate is a constant offset that no step size can satisfy:
# the solver grinds to a halt rather than returning a wrong answer.
assert abs(_B.sum() - 1.0) < 1e-15, "propagated weights must sum to 1"
assert abs(_B_HAT.sum() - 1.0) < 1e-15, "embedded weights must sum to 1"

RALSTON3 = ButcherTableau(
    name="ralston3",
    A=np.array([
        [0.0, 0.0, 0.0],
        [0.5, 0.0, 0.0],
        [0.0, 0.75, 0.0],
    ]),
    b=_B,
    c=np.array([0.0, 0.5, 0.75]),
    # The tableau stores the *difference* rather than b_hat itself, because the
    # difference is what the error estimate actually is -- and storing it that
    # way makes a degenerate estimator visible as a zero vector instead of
    # hiding inside a subtraction the reader has to perform.
    e=_B - _B_HAT,
    order=3,
    error_order=2,
)


class FixedStep(Controller):
    """Never changes the step size.

    The minimal controller: the contract is one method mapping an error norm to
    a multiplicative factor, and returning 1.0 satisfies it. Paired with a loose
    tolerance so nothing is ever rejected, this turns any adaptive method into a
    fixed-step one -- which is what a convergence study needs, because
    `first_step` alone sets only the *first* step and the controller immediately
    adapts away from it.
    """

    def _factor(self, err: float) -> float:
        return 1.0


class ConservativeController(Controller):
    """An I-controller that refuses to grow the step by more than 20% at a time.

    Not better than the default -- deliberately timid -- but it shows the whole
    contract in four lines.
    """

    max_factor = 1.2

    def _factor(self, err: float) -> float:
        return self.safety * err ** (-self.exponent)


def main() -> None:
    # y' = -y, y(0) = 1, so y(t) = exp(-t): a closed form to measure against.
    problem = ODEProblem(lambda t, y: -y, t_span=(0.0, 1.0), y0=[1.0])
    exact = np.exp(-1.0)
    stepper = ExplicitRungeKutta(RALSTON3)

    print(f"registered {stepper!r}")
    print("\n  measuring the order by halving the step:")
    print(f"  {'steps':>7s} {'h':>10s} {'error':>12s} {'ratio':>8s} {'order':>8s}")

    previous, order = None, float("nan")
    for n in (20, 40, 80, 160, 320):
        sol = solve(problem, stepper, first_step=1.0 / n,
                    rtol=1e3, atol=1e3, controller=FixedStep(2))
        steps = np.diff(sol.t)
        # Every step but the last is exactly h. The final one is clamped so the
        # run lands on t_end rather than overshooting it and interpolating back,
        # so it can be a rounding error shorter.
        assert np.allclose(steps[:-1], 1.0 / n), "the step should not have moved"
        assert steps[-1] <= 1.0 / n + 1e-12

        error = abs(sol.y[0, -1] - exact)
        if previous is None:
            print(f"  {n:7d} {1 / n:10.5f} {error:12.4e} {'':>8s} {'':>8s}")
        else:
            ratio = previous / error
            order = np.log2(ratio)
            print(f"  {n:7d} {1 / n:10.5f} {error:12.4e} {ratio:8.2f} {order:8.2f}")
        previous = error

    # Halving h must divide the error by 2^3. Measured, not taken on trust:
    # a declared order is a claim like any other.
    assert 2.8 < order < 3.2, f"declared order 3, measured {order:.2f}"
    print(f"\n  declared order {RALSTON3.order}, measured {order:.2f}")

    # The same method again, under a custom adaptive controller.
    adaptive = solve(problem, stepper, rtol=1e-8, atol=1e-10,
                     controller=ConservativeController(2))
    print(f"\n  adaptive, custom controller: {adaptive.stats}")
    print(f"  endpoint error {abs(adaptive.y[0, -1] - exact):.3e}")
    assert adaptive.success
    assert abs(adaptive.y[0, -1] - exact) < 1e-7


if __name__ == "__main__":
    main()
