"""Event detection: root location, direction filtering, and termination."""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import Event, ODEProblem, solve
from odesuite.problems import bouncing_ball, sine_cosine
from odesuite.tableaux import TABLEAUX

METHOD_NAMES = sorted({tab.name.lower(): key for key, tab in TABLEAUX.items()}.values())


# ---------------------------------------------------------------------------
# Accuracy of the located root
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", METHOD_NAMES)
def test_impact_time_matches_closed_form(method):
    """The ball's ground impact is known exactly: ``t = sqrt(2*h0/g)``.

    Because the root is found on the continuous extension rather than at a step
    boundary, its accuracy is set by the interpolant, not by the step size --
    which is the whole reason events and dense output were built together.
    """
    bench = bouncing_ball(h0=1.0, g=9.81)
    hit_ground = Event(lambda t, y: y[0], terminal=True, direction=-1, name="impact")

    sol = solve(
        bench.problem,
        method=method,
        rtol=1e-11,
        atol=1e-13,
        events=[hit_ground],
        dense_output=True,
    )

    assert sol.status == "terminated"
    assert sol.t_events[0].size == 1
    assert sol.t_events[0][0] == pytest.approx(bench.impact_time, abs=1e-12), (
        f"{method}: impact at {sol.t_events[0][0]!r}, expected {bench.impact_time!r}"
    )
    # The recorded state at the event must sit on the event surface.
    assert abs(sol.y_events[0][0, 0]) < 1e-11


def test_event_state_matches_dense_output():
    bench = bouncing_ball()
    ev = Event(lambda t, y: y[0], terminal=True, direction=-1)
    sol = solve(bench.problem, rtol=1e-10, events=[ev], dense_output=True)

    t_hit = sol.t_events[0][0]
    assert np.allclose(sol.y_events[0][:, 0], sol.y_at(t_hit), atol=1e-12)


def test_solution_stops_at_the_event():
    bench = bouncing_ball()
    ev = Event(lambda t, y: y[0], terminal=True, direction=-1)
    sol = solve(bench.problem, rtol=1e-10, events=[ev])

    assert sol.t[-1] == pytest.approx(sol.t_events[0][0])
    assert sol.t[-1] < bench.problem.tf
    assert "terminal event" in sol.message


# ---------------------------------------------------------------------------
# Direction filtering
# ---------------------------------------------------------------------------


def test_direction_filters_crossings():
    """sin(t) over [0, 10] crosses zero at 0, pi, 2*pi, 3*pi.

    Upward crossings are at 0 and 2*pi; the downward one is at pi. Direction
    filtering must separate them.
    """
    prob = ODEProblem(
        f=lambda t, y: np.array([y[1], -y[0]]), t_span=(0.0, 10.0), y0=[0.0, 1.0]
    )
    up = Event(lambda t, y: y[0], direction=+1)
    down = Event(lambda t, y: y[0], direction=-1)
    both = Event(lambda t, y: y[0], direction=0)

    sol = solve(prob, rtol=1e-11, atol=1e-13, events=[up, down, both])

    assert np.allclose(sol.t_events[0], [2 * np.pi], atol=1e-8)
    assert np.allclose(sol.t_events[1], [np.pi, 3 * np.pi], atol=1e-8)
    assert np.allclose(sol.t_events[2], [np.pi, 2 * np.pi, 3 * np.pi], atol=1e-8)


def test_bare_callable_is_accepted():
    """A plain function works as an event, defaulting to non-terminal, both ways."""
    prob = ODEProblem(
        f=lambda t, y: np.array([y[1], -y[0]]), t_span=(0.0, 4.0), y0=[0.0, 1.0]
    )
    sol = solve(prob, rtol=1e-10, events=lambda t, y: y[0])
    assert np.allclose(sol.t_events[0], [np.pi], atol=1e-8)
    assert sol.status == "finished"


# ---------------------------------------------------------------------------
# Termination policy
# ---------------------------------------------------------------------------


def test_non_terminal_event_records_all_crossings():
    prob = ODEProblem(
        f=lambda t, y: np.array([y[1], -y[0]]), t_span=(0.0, 20.0), y0=[0.0, 1.0]
    )
    sol = solve(prob, rtol=1e-11, atol=1e-13, events=Event(lambda t, y: y[0]))

    expected = [np.pi * k for k in range(1, 7)]
    assert sol.status == "finished"
    assert np.allclose(sol.t_events[0], expected, atol=1e-7)


def test_terminal_count_stops_at_kth_crossing():
    """``terminal=3`` runs until the third crossing, not the first."""
    prob = ODEProblem(
        f=lambda t, y: np.array([y[1], -y[0]]), t_span=(0.0, 20.0), y0=[0.0, 1.0]
    )
    ev = Event(lambda t, y: y[0], terminal=3)
    sol = solve(prob, rtol=1e-11, atol=1e-13, events=[ev])

    assert sol.status == "terminated"
    assert sol.t_events[0].size == 3
    assert sol.t_events[0][-1] == pytest.approx(3 * np.pi, abs=1e-7)
    assert sol.t[-1] == pytest.approx(3 * np.pi, abs=1e-7)


def test_earliest_terminal_event_wins():
    """With two terminal events the solve stops at whichever comes first."""
    prob = ODEProblem(
        f=lambda t, y: np.array([y[1], -y[0]]), t_span=(0.0, 20.0), y0=[0.0, 1.0]
    )
    late = Event(lambda t, y: y[0], terminal=True, name="zero_crossing")   # t = pi
    early = Event(lambda t, y: y[1], terminal=True, name="velocity_zero")  # t = pi/2

    sol = solve(prob, rtol=1e-11, atol=1e-13, events=[late, early])

    assert sol.status == "terminated"
    assert sol.t[-1] == pytest.approx(np.pi / 2, abs=1e-8)
    assert sol.t_events[0].size == 0     # the later event never fired
    assert sol.t_events[1].size == 1
    assert "velocity_zero" in sol.message


def test_event_that_never_fires():
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-8, events=Event(lambda t, y: y[0] ** 2 + 10.0))
    assert sol.status == "finished"
    assert sol.t_events[0].size == 0
    assert sol.y_events[0].shape == (2, 0)


def test_events_do_not_change_the_trajectory():
    """Adding a non-terminal event must not perturb the solution or the steps."""
    bench = sine_cosine()
    plain = solve(bench.problem, rtol=1e-8, atol=1e-10)
    watched = solve(
        bench.problem, rtol=1e-8, atol=1e-10, events=Event(lambda t, y: y[0])
    )
    assert np.allclose(plain.t, watched.t)
    assert np.allclose(plain.y, watched.y)
    assert plain.stats.nsteps == watched.stats.nsteps


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_event_zero_at_initial_time():
    """g(t0) == 0 must not immediately trigger a spurious detection.

    Here y[0] starts at exactly 0 and moves upward. The first genuine downward
    crossing is at t = pi, and that is what should be reported.
    """
    prob = ODEProblem(
        f=lambda t, y: np.array([y[1], -y[0]]), t_span=(0.0, 4.0), y0=[0.0, 1.0]
    )
    ev = Event(lambda t, y: y[0], direction=-1, terminal=True)
    sol = solve(prob, rtol=1e-11, atol=1e-13, events=[ev])

    assert sol.t_events[0].size == 1
    assert sol.t_events[0][0] == pytest.approx(np.pi, abs=1e-8)


def test_event_during_backward_integration():
    """Roots must be located correctly when time runs backwards."""
    prob = ODEProblem(
        f=lambda t, y: np.array([y[1], -y[0]]),
        t_span=(10.0, 0.0),
        y0=[np.sin(10.0), np.cos(10.0)],
    )
    ev = Event(lambda t, y: y[0], terminal=True)
    sol = solve(prob, rtol=1e-11, atol=1e-13, events=[ev])

    assert sol.status == "terminated"
    # Coming back from t=10, the first zero of sin encountered is 3*pi.
    assert sol.t_events[0][0] == pytest.approx(3 * np.pi, abs=1e-7)
    assert sol.t[-1] < 10.0


def test_events_with_args():
    """Event functions receive the problem's extra arguments."""
    prob = ODEProblem(
        f=lambda t, y, k: -k * y, t_span=(0.0, 5.0), y0=[1.0], args=(1.0,)
    )
    ev = Event(lambda t, y, k: y[0] - 0.5, terminal=True)
    sol = solve(prob, rtol=1e-11, atol=1e-13, events=[ev])
    assert sol.t_events[0][0] == pytest.approx(np.log(2.0), abs=1e-9)


def test_event_repr_and_validation():
    ev = Event(lambda t, y: y[0], terminal=2, direction=-1, name="g")
    assert "terminal=2" in repr(ev)
    assert ev.terminal

    with pytest.raises(ValueError, match="terminal count"):
        Event(lambda t, y: y[0], terminal=0)
    with pytest.raises(TypeError, match="callable"):
        Event("not a function")


def test_terminal_event_truncates_t_eval():
    """Requested output times past a terminal event are dropped."""
    bench = bouncing_ball(h0=1.0, g=9.81)
    ev = Event(lambda t, y: y[0], terminal=True, direction=-1)
    sol = solve(
        bench.problem,
        rtol=1e-10,
        t_eval=np.linspace(0.0, 1.0, 21),
        events=[ev],
    )
    assert np.all(sol.t <= bench.impact_time + 1e-12)
    assert sol.t.size < 21


def test_dense_output_is_clipped_at_terminal_event():
    """Querying past the event is out of range, not a silent continuation."""
    bench = bouncing_ball()
    ev = Event(lambda t, y: y[0], terminal=True, direction=-1)
    sol = solve(bench.problem, rtol=1e-10, events=[ev], dense_output=True)

    assert sol.sol.t_max == pytest.approx(sol.t_events[0][0])
    with pytest.raises(ValueError, match="outside the solved interval"):
        sol.y_at(bench.impact_time + 0.5)
