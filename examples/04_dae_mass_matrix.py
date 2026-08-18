"""A differential-algebraic system, written as a singular mass matrix.

    py -3.10 examples/04_dae_mass_matrix.py

`ODEProblem` solves `M y' = f(t, y)`. Nothing requires M to be invertible, and
when it is singular the rows with a zero diagonal stop being differential
equations and become *constraints* -- the same code path is now an index-1 DAE
solver.

Two things are needed to make that work, and both are properties of the method
rather than of the problem: the method must be stiffly accurate (the solution at
the end of the step must be the last stage, so the constraint is imposed exactly
where the answer is taken) and it must be L-stable. `radau` and `rodas4` are;
the explicit methods refuse the problem rather than silently drifting off the
constraint manifold.
"""

from __future__ import annotations

import numpy as np

from odesuite import ODEProblem, solve

# Robertson again, but with the third equation replaced by the conservation law
# it implies. The system is now two ODEs and one algebraic constraint.
MASS = np.diag([1.0, 1.0, 0.0])


def robertson_dae(t, y):
    a, b, c = y
    return np.array([
        -0.04 * a + 1e4 * b * c,
        0.04 * a - 1e4 * b * c - 3e7 * b * b,
        a + b + c - 1.0,          # 0 = a + b + c - 1
    ])


def main() -> None:
    problem = ODEProblem(robertson_dae, t_span=(0.0, 1e5), y0=[1.0, 0.0, 0.0], mass=MASS)
    print(f"problem     {problem!r}")
    print(f"is_dae      {problem.is_dae}  (the mass matrix is singular)")

    for method in ("radau", "rodas4"):
        sol = solve(problem, method, rtol=1e-8, atol=1e-10)
        residual = abs(sol.y[:, -1].sum() - 1.0)
        print(f"  {method:8s} {sol.status:9s} {sol.stats}")
        print(f"           constraint residual at the end: {residual:.2e}")
        assert sol.success
        # The constraint is imposed exactly, not merely integrated accurately --
        # this is what stiff accuracy buys.
        assert residual < 1e-12, f"{method} drifted off the constraint"

    # An explicit method cannot do this, and says so rather than trying.
    try:
        solve(problem, "dopri5", rtol=1e-6)
    except ValueError as exc:
        print(f"\n  dopri5 refuses, correctly: {exc}")
    else:
        raise AssertionError("an explicit method should not accept a mass matrix")


if __name__ == "__main__":
    main()
