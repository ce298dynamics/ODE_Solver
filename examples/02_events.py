"""Stop, or record, when something happens -- located to machine precision.

    py -3.10 examples/02_events.py

An event is a scalar function g(t, y) whose zeros are interesting. The solver
brackets a sign change across a step and then finds the root *on the step's
interpolant*, so the accuracy of an event time is set by the continuous
extension rather than by how big the steps happened to be.

`terminal` takes an integer, which is what makes "simulate exactly five
bounces" a one-liner rather than a loop with restarts.
"""

from __future__ import annotations

import numpy as np

from odesuite import Event, ODEProblem, solve

GRAVITY = 9.81


def falling(t, y):
    return np.array([y[1], -GRAVITY])


def main() -> None:
    # Dropped from 10 m. Analytically it lands at sqrt(2h/g).
    problem = ODEProblem(falling, t_span=(0.0, 10.0), y0=[10.0, 0.0])

    hit_ground = Event(lambda t, y: y[0], terminal=True, direction=-1, name="impact")
    apex = Event(lambda t, y: y[1], direction=-1, name="apex")

    sol = solve(problem, "dopri5", rtol=1e-10, atol=1e-12,
                events=[hit_ground, apex], dense_output=True)

    exact = np.sqrt(2 * 10.0 / GRAVITY)
    found = sol.t_events[0][0]
    print(f"status        {sol.status}")
    print(f"message       {sol.message}")
    print(f"impact at     t = {found:.12f}")
    print(f"exact         t = {exact:.12f}")
    print(f"error             {abs(found - exact):.2e}  ({sol.stats.naccepted} steps)")
    assert abs(found - exact) < 1e-10, "event location should be near machine precision"

    # The integration stopped *at* the event, not at the end of the step that
    # contained it, so the final state is the state at impact.
    print(f"height at impact  {sol.y[0, -1]:.2e} (should be 0)")
    assert abs(sol.y[0, -1]) < 1e-9

    # The apex event never fires: the ball starts at rest and only falls.
    print(f"apex crossings    {sol.t_events[1].size}")


if __name__ == "__main__":
    main()
