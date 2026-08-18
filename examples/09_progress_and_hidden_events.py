"""Watching a solve as it runs, stopping it early, and finding events it would miss.

    py -3.10 examples/09_progress_and_hidden_events.py

Two capabilities that are really the same observation: a solver's step size is
chosen for the solution's convenience, and everything else has to be told about
it explicitly.

`callback(t, y, stats)` is called after every accepted step, and returning False
stops the integration. That one parameter is progress reporting, live plotting,
streaming to disk, and cancellation from another thread -- because without it
nothing in the loop offers a way in.

`Event(..., subdivisions=k)` samples the event function inside each step instead
of only at its ends. Endpoint comparison misses any *even* number of crossings
within a step, silently, and the step size is chosen to resolve `y`, not `g`.
"""

from __future__ import annotations

import numpy as np

from odesuite import Event, ODEProblem, solve


def robertson(t, y):
    a, b, c = y
    return np.array([
        -0.04 * a + 1e4 * b * c,
        0.04 * a - 1e4 * b * c - 3e7 * b * b,
        3e7 * b * b,
    ])


def progress() -> None:
    """A long stiff solve, reporting as it goes instead of returning eventually."""
    print("watching Robertson to t = 1e11:")
    print(f"  {'t':>12s} {'steps':>7s} {'nfev':>8s} {'LU':>5s}")

    marks = iter([1e-2, 1e2, 1e6, 1e10])
    next_mark = next(marks)

    def report(t, y, stats):
        nonlocal next_mark
        if next_mark is not None and t >= next_mark:
            print(f"  {t:12.2e} {stats.naccepted:7d} {stats.nfev:8d} {stats.nlu:5d}")
            next_mark = next(marks, None)

    problem = ODEProblem(robertson, (0.0, 1e11), [1.0, 0.0, 0.0])
    sol = solve(problem, "radau", rtol=1e-8, atol=1e-10, callback=report)
    print(f"  finished: {sol.stats}")
    assert sol.success


def cancellation() -> None:
    """Stopping a solve that is taking too long, and keeping what it produced."""
    problem = ODEProblem(robertson, (0.0, 1e11), [1.0, 0.0, 0.0])

    budget = 200
    sol = solve(problem, "radau", rtol=1e-8, atol=1e-10,
                callback=lambda t, y, stats: stats.naccepted < budget)

    print(f"\nstopped after a {budget}-step budget:")
    print(f"  status    {sol.status}   cancelled={sol.cancelled}  success={sol.success}")
    print(f"  reached   t = {sol.t[-1]:.3e} of 1e+11")
    print(f"  mass      a + b + c = {sol.y[:, -1].sum():.12f}")

    # `success` is False -- the requested interval was not integrated -- but the
    # trajectory computed so far is perfectly good, which is what a caller
    # streaming output or driving a progress bar needs.
    assert sol.cancelled and not sol.success
    assert abs(sol.y[:, -1].sum() - 1.0) < 1e-10
    assert sol.stats.naccepted == budget


def hidden_events() -> None:
    """An event that oscillates faster than the solution it rides on."""
    problem = ODEProblem(lambda t, y: -0.1 * y, (0.0, 10.0), [1.0])
    exact = np.array([k * np.pi / 20 for k in range(1, 200) if 0 < k * np.pi / 20 < 10])

    print(f"\ng(t) = sin(20 t) on [0, 10]: {exact.size} roots exist")
    print(f"  {'subdivisions':>13s} {'found':>7s} {'max error':>12s}")

    for k in (0, 4, 8, 16):
        event = Event(lambda t, y: np.sin(20 * t), subdivisions=k)
        sol = solve(problem, "dopri5", rtol=1e-6, atol=1e-9, events=[event])
        found = sol.t_events[0]
        error = max(np.abs(exact - t).min() for t in found) if found.size else np.nan
        print(f"  {k:13d} {found.size:7d} {error:12.2e}")

        if k == 0:
            missed = exact.size - found.size
            assert missed > 50
        if k == 16:
            assert found.size == exact.size
            assert error < 1e-10

    print(f"  the solve took {sol.stats.naccepted} steps -- the step size resolves y,")
    print("  not g, so the endpoints of a step say nothing about what happens inside.")


def main() -> None:
    progress()
    cancellation()
    hidden_events()


if __name__ == "__main__":
    main()
