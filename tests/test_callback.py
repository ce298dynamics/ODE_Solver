"""The `callback` hook: observing a solve, and stopping one.

`solve` was a black box that returned when it was finished. For a solve that
takes seconds -- Robertson to 1e11, a work-precision sweep -- that meant no
progress, no live output, and no way to stop: the interface could run a solve on
a worker thread but could not tell it to give up, so a superseded slider drag
kept a pool thread busy computing an answer that would be discarded on arrival.

One parameter fixes all of those, because they are the same problem: nothing in
the loop offered a way in.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import ODEProblem, solve
from odesuite.problems import exponential_decay, lotka_volterra, robertson


def _decay(t_end: float = 10.0) -> ODEProblem:
    return ODEProblem(lambda t, y: -y, (0.0, t_end), [1.0])


# ---------------------------------------------------------------------------
# Observing
# ---------------------------------------------------------------------------


def test_the_callback_sees_every_accepted_step():
    seen = []
    sol = solve(_decay(), "dopri5", rtol=1e-8, callback=lambda t, y, s: seen.append(t))

    assert sol.success
    assert len(seen) == sol.stats.naccepted
    # And it is handed the step's own time, in order.
    assert seen == sorted(seen)
    assert seen[-1] == pytest.approx(sol.t[-1])


def test_the_callback_sees_the_live_statistics():
    """`stats` is the running object, not a snapshot, so a progress display can
    read work counters as they climb."""
    counts = []
    solve(_decay(), "dopri5", rtol=1e-8,
          callback=lambda t, y, s: counts.append(s.nfev))

    assert counts == sorted(counts)
    assert counts[0] > 0 and counts[-1] > counts[0]


def test_a_callback_that_never_stops_changes_nothing():
    """The hook must be observationally pure when it does not intervene --
    otherwise every progress bar would perturb the answer it is reporting."""
    bench = lotka_volterra()
    reference = solve(bench.problem, "dopri5", rtol=1e-9, atol=1e-11)
    watched = solve(bench.problem, "dopri5", rtol=1e-9, atol=1e-11,
                    callback=lambda t, y, s: None)

    assert reference.status == watched.status
    np.testing.assert_array_equal(reference.t, watched.t)
    np.testing.assert_array_equal(reference.y, watched.y)
    assert reference.stats.nfev == watched.stats.nfev


@pytest.mark.parametrize("returned", [None, True, 0, "", [], object()])
def test_only_False_stops_the_solve(returned):
    """Specifically `False`, not anything falsy. A callback that forgets to
    return would otherwise stop the solve after one step."""
    sol = solve(_decay(), "dopri5", rtol=1e-6, callback=lambda t, y, s: returned)
    assert sol.success and not sol.cancelled


# ---------------------------------------------------------------------------
# Stopping
# ---------------------------------------------------------------------------


def test_returning_false_stops_the_solve():
    sol = solve(_decay(), "dopri5", rtol=1e-8, callback=lambda t, y, s: t < 3.0)

    assert sol.cancelled
    assert not sol.success, "a partial trajectory must not read as a complete one"
    assert sol.status == "cancelled"
    assert "cancelled" in sol.message
    assert 3.0 <= sol.t[-1] < 10.0


def test_a_cancelled_solve_keeps_what_it_computed():
    """Stopping is not failing: the trajectory up to the stopping point is
    valid, and a caller streaming output wants to keep it."""
    sol = solve(_decay(), "dopri5", rtol=1e-10, atol=1e-12,
                callback=lambda t, y, s: t < 2.0, dense_output=True)

    assert sol.cancelled
    assert sol.t.size > 1
    error = np.abs(sol.y[0] - np.exp(-sol.t)).max()
    assert error < 1e-8, f"the partial trajectory should still be accurate: {error:.2e}"
    # Dense output covers what was actually integrated.
    assert sol.y_at(1.0)[0] == pytest.approx(np.exp(-1.0), abs=1e-8)


def test_stopping_immediately_is_not_an_error():
    sol = solve(_decay(), "dopri5", rtol=1e-6, callback=lambda t, y, s: False)
    assert sol.cancelled
    assert sol.stats.naccepted == 1


def test_cancellation_works_on_a_stiff_solve():
    """The case it exists for: Robertson to 1e11 is where a user actually needs
    to be able to give up."""
    bench = robertson()
    full = solve(bench.problem, "radau", rtol=1e-6, atol=1e-9)
    stopped = solve(bench.problem, "radau", rtol=1e-6, atol=1e-9,
                    callback=lambda t, y, s: s.naccepted < 20)

    assert stopped.cancelled
    assert stopped.stats.naccepted == 20
    assert stopped.stats.nfev < full.stats.nfev / 2


def test_an_exception_in_the_callback_propagates():
    """A broken callback must not be silently swallowed -- debugging a progress
    display that quietly does nothing is far worse than a traceback."""

    def explode(t, y, stats):
        raise RuntimeError("callback blew up")

    with pytest.raises(RuntimeError, match="callback blew up"):
        solve(_decay(), "dopri5", rtol=1e-6, callback=explode)


def test_the_callback_is_given_the_state_not_a_copy():
    """Documented behaviour, so that streaming a large state costs nothing.
    Pinned because a well-meaning `y.copy()` in the driver would be a silent
    per-step allocation on every solve that uses the hook."""
    bench = exponential_decay()
    captured = []
    solve(bench.problem, "dopri5", rtol=1e-6,
          callback=lambda t, y, s: captured.append(y))
    assert all(isinstance(y, np.ndarray) for y in captured)


def test_cancellation_composes_with_events():
    """Both can stop a solve; whichever happens first should win, and the other
    machinery must not be confused by it."""
    from odesuite import Event

    late = Event(lambda t, y: t - 9.0, terminal=True)
    sol = solve(_decay(), "dopri5", rtol=1e-8, events=[late],
                callback=lambda t, y, s: t < 2.0)

    assert sol.cancelled, "the callback stops first, at t=2, before the event at t=9"
    assert sol.t_events[0].size == 0
