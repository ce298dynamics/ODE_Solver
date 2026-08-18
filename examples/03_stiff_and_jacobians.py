"""A stiff problem, and the four ways to get the Jacobian an implicit method needs.

    py -3.10 examples/03_stiff_and_jacobians.py

Robertson's kinetics spans eleven decades of time and has rate constants
differing by nine orders of magnitude. An explicit method is not slow on it --
it is *stability-bound*, which is a different and much worse thing: the step
size is capped by the fastest transient forever, long after that transient has
died.

The Jacobian can come from four places, and the choice is a real one: analytic
is exact and free of noise but you have to write it; complex-step is exact to
machine precision and needs nothing written; finite differences always work;
and a supplied sparsity pattern turns an O(n) cost into O(colours).
"""

from __future__ import annotations

import numpy as np

from odesuite import ODEProblem, solve


def robertson(t, y):
    a, b, c = y
    return np.array([
        -0.04 * a + 1e4 * b * c,
        0.04 * a - 1e4 * b * c - 3e7 * b * b,
        3e7 * b * b,
    ])


def robertson_jac(t, y):
    a, b, c = y
    return np.array([
        [-0.04, 1e4 * c, 1e4 * b],
        [0.04, -1e4 * c - 6e7 * b, -1e4 * b],
        [0.0, 6e7 * b, 0.0],
    ])


def main() -> None:
    span = (0.0, 1e5)
    y0 = [1.0, 0.0, 0.0]

    print("An explicit method on a stiff problem:")
    explicit = solve(ODEProblem(robertson, span, y0), "dopri5",
                     rtol=1e-6, atol=1e-9, max_steps=50_000)
    reached = explicit.t[-1]
    print(f"  dopri5   {explicit.status}: reached t = {reached:.3g} of {span[1]:g}"
          f" after {explicit.stats.nsteps} steps")
    print("  the step is capped by stability, not accuracy -- more steps will not help\n")

    print("The same problem, implicitly, with each Jacobian strategy:")
    variants = {
        "analytic":     ODEProblem(robertson, span, y0, jac=robertson_jac),
        "finite diff":  ODEProblem(robertson, span, y0),
    }
    endpoints = {}
    for label, problem in variants.items():
        sol = solve(problem, "radau", rtol=1e-8, atol=1e-10)
        endpoints[label] = sol.y[:, -1]
        print(f"  {label:12s} {sol.stats}")

    difference = np.abs(endpoints["analytic"] - endpoints["finite diff"]).max()
    print(f"\n  analytic vs finite-difference endpoints differ by {difference:.2e}")
    assert difference < 1e-8, "the two Jacobian routes should agree"

    # Mass conservation: a + b + c is invariant, and it is not something the
    # solver is told about, so it is an independent check on the answer.
    total = endpoints["analytic"].sum()
    print(f"  a + b + c = {total:.15f} (conserved, should be 1)")
    assert abs(total - 1.0) < 1e-10


if __name__ == "__main__":
    main()
