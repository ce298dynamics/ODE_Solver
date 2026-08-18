"""A two-point boundary value problem, by multiple shooting.

    py -3.10 examples/05_boundary_value_problem.py

An IVP knows where it starts. A BVP is told something at each end and has to
find the trajectory joining them, which is a root-finding problem wrapped
around an integrator.

Multiple shooting splits the interval into segments, integrates each
independently, and asks Newton to make the segments meet *and* satisfy the
boundary conditions. Splitting is what makes it usable: single shooting on a
sensitive problem amplifies the initial guess exponentially across the whole
interval, whereas each segment here only has to survive its own short span.

`y'' = -k^2 y` with `y(0) = 0`, `y(1) = 1` shows exactly that. At `k = 6` the
solution oscillates several times across the interval and single shooting is
already badly conditioned.
"""

from __future__ import annotations

import numpy as np

from odesuite import BVProblem, solve_bvp

K = 6.0


def main() -> None:
    problem = BVProblem(
        f=lambda t, y: np.array([y[1], -(K**2) * y[0]]),
        t_span=(0.0, 1.0),
        bc=lambda ya, yb: np.array([ya[0], yb[0] - 1.0]),
        n=2,
    )

    def exact(t):
        return np.sin(K * t) / np.sin(K)

    print(f"y'' = -{K:g}^2 y,  y(0) = 0,  y(1) = 1\n")
    print(f"  {'segments':>9s} {'converged':>10s} {'Newton its':>11s} {'max error':>12s}")

    sample = np.linspace(0.0, 1.0, 201)
    for n_nodes in (1, 2, 5, 10):
        sol = solve_bvp(problem, guess=np.array([0.5, 1.0]), n_nodes=n_nodes,
                        rtol=1e-11, atol=1e-13, tol=1e-10)
        error = np.abs(sol.y_at(sample)[0] - exact(sample)).max()
        print(f"  {n_nodes:9d} {str(sol.converged):>10s} {sol.n_iter:11d} {error:12.3e}")
        assert sol.converged, sol.message
        assert error < 1e-8, f"n_nodes={n_nodes} converged to the wrong curve"

    print("\n  Every segmentation finds the same curve -- which is the point:")
    print("  more segments is a conditioning choice, not a different answer.")

    # The residual history shows Newton at work. A linear problem like this one
    # is solved exactly by the first correction.
    sol = solve_bvp(problem, guess=np.array([0.5, 1.0]), n_nodes=5,
                    rtol=1e-12, atol=1e-14, tol=1e-9)
    print(f"\n  residuals: {' -> '.join(f'{r:.1e}' for r in sol.history)}")
    print("  the equation is linear, so one Newton step lands on the answer.")


if __name__ == "__main__":
    main()
