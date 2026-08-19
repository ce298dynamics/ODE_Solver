"""Event detection: root location, direction filtering, and termination."""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import Event, ODEProblem, solve
from odesuite.problems import bouncing_ball, sine_cosine
from odesuite.tableaux import TABLEAUX

#: Methods that can choose their own step. Euler and RK4 carry no embedded
#: estimate and run fixed-step, so an adaptive-solve test cannot include them.
METHOD_NAMES = sorted(
    {tab.name.lower(): key for key, tab in TABLEAUX.items() if tab.embedded}.values()
)


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


# ---------------------------------------------------------------------------
# A bracket that does not survive interpolation
# ---------------------------------------------------------------------------
#
# `find_active_events` brackets a root from `g` at the two step *endpoints*,
# but the root is then located on the *interpolant*. Those are different
# functions, and on rare occasions they disagree. The old behaviour was to
# return the end of the step as the root, which invents a detection that never
# happened -- the same shape as the recorded bugs in the README, where a
# plausible answer is worse than an error.


def test_a_bracket_that_does_not_survive_interpolation_reports_no_root():
    from odesuite.events import _solve_event

    ev = Event(lambda t, y: y[0])
    never_zero = lambda t: np.array([1.0])  # noqa: E731
    assert _solve_event(ev, never_zero, 0.0, 1.0, ()) is None


def test_a_phantom_crossing_is_dropped_rather_than_reported():
    from odesuite.events import locate_events

    ev = Event(lambda t, y: y[0])
    never_zero = lambda t: np.array([1.0])  # noqa: E731
    active, roots, terminate_at = locate_events(
        [ev], np.array([0]), never_zero, 0.0, 1.0, ()
    )
    assert active.size == 0
    assert roots.size == 0
    assert terminate_at is None


def test_a_phantom_crossing_does_not_consume_a_terminal_allowance():
    """The expensive version of the bug: a fabricated root would have ended the
    integration early, and the caller would have had no way to tell."""
    from odesuite.events import locate_events

    ev = Event(lambda t, y: y[0], terminal=True)
    never_zero = lambda t: np.array([1.0])  # noqa: E731
    _, _, terminate_at = locate_events([ev], np.array([0]), never_zero, 0.0, 1.0, ())
    assert terminate_at is None
    assert ev.count == 0, "a phantom detection used up the terminal allowance"
    assert not ev.is_exhausted()


def test_a_genuine_root_is_still_found_alongside_a_phantom_one():
    """The filter must drop only the phantom, not the whole step's detections."""
    from odesuite.events import locate_events

    real = Event(lambda t, y: y[0])        # crosses zero at t = 0.5
    phantom = Event(lambda t, y: y[0] + 5.0)
    line = lambda t: np.array([t - 0.5])   # noqa: E731

    active, roots, _ = locate_events(
        [real, phantom], np.array([0, 1]), line, 0.0, 1.0, ()
    )
    assert list(active) == [0]
    assert roots[0] == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Sub-step scanning
# ---------------------------------------------------------------------------
#
# Comparing only the two step endpoints misses any *even* number of crossings
# inside a step, and misses them silently: g has the same sign at both ends, so
# nothing looks wrong. The step size is chosen to resolve `y`, not `g`, so an
# event that oscillates faster than the solution is entirely ordinary.
#
# `scipy.integrate.solve_ivp` has the same limitation and no way around it.


def _fast_oscillation(subdivisions: int):
    """Smooth, slowly-decaying state; an event that wiggles 20x faster."""
    problem = ODEProblem(lambda t, y: -0.1 * y, (0.0, 10.0), [1.0])
    event = Event(lambda t, y: np.sin(20 * t), subdivisions=subdivisions)
    return solve(problem, "dopri5", rtol=1e-6, atol=1e-9, events=[event])


def _exact_roots() -> np.ndarray:
    return np.array([k * np.pi / 20 for k in range(1, 200) if 0 < k * np.pi / 20 < 10])


def test_endpoint_bracketing_alone_misses_most_of_the_roots():
    """The behaviour being fixed, pinned so the improvement below is measured
    against something rather than asserted."""
    sol = _fast_oscillation(subdivisions=0)
    assert sol.stats.naccepted < 20, "the state is smooth; steps should be large"
    assert sol.t_events[0].size < 10
    assert _exact_roots().size == 63


def test_subdivision_finds_every_crossing():
    sol = _fast_oscillation(subdivisions=16)
    found, exact = sol.t_events[0], _exact_roots()

    assert found.size == exact.size, f"found {found.size} of {exact.size}"
    assert np.abs(found - exact).max() < 1e-10, "and located to the usual precision"


def test_more_subdivisions_never_finds_fewer():
    counts = [_fast_oscillation(k).t_events[0].size for k in (0, 2, 4, 8, 16)]
    assert counts == sorted(counts), counts
    assert counts[-1] > 5 * counts[0]


def test_subdivision_reports_no_spurious_roots():
    """Every root it reports must be a real one -- inventing crossings would be
    a worse failure than missing them."""
    sol = _fast_oscillation(subdivisions=16)
    exact = _exact_roots()
    for t in sol.t_events[0]:
        assert np.abs(exact - t).min() < 1e-9, f"{t} is not a root of sin(20t)"


def test_subdivision_respects_direction():
    """Only upward crossings, so exactly half the roots of a sine."""
    problem = ODEProblem(lambda t, y: -0.1 * y, (0.0, 10.0), [1.0])
    up = Event(lambda t, y: np.sin(20 * t), direction=1, subdivisions=16)
    sol = solve(problem, "dopri5", rtol=1e-6, atol=1e-9, events=[up])

    found = sol.t_events[0]
    assert 30 <= found.size <= 32, found.size
    for t in found:
        assert np.cos(20 * t) > 0, f"{t} is a downward crossing"


def test_subdivision_drives_a_terminal_event_to_the_first_root():
    """A terminal event must stop at the *earliest* crossing in the step, not
    at whichever one the scan happened to evaluate first."""
    problem = ODEProblem(lambda t, y: -0.1 * y, (0.0, 10.0), [1.0])
    event = Event(lambda t, y: np.sin(20 * t), terminal=True, subdivisions=16)
    sol = solve(problem, "dopri5", rtol=1e-6, atol=1e-9, events=[event])

    assert sol.status == "terminated"
    assert sol.t_events[0][0] == pytest.approx(np.pi / 20, abs=1e-10)
    assert sol.t[-1] == pytest.approx(np.pi / 20, abs=1e-10)


def test_subdivision_is_off_by_default_and_costs_nothing():
    assert Event(lambda t, y: y[0]).subdivisions == 0

    bench = sine_cosine()
    plain = solve(bench.problem, "dopri5", rtol=1e-8,
                  events=[Event(lambda t, y: y[0])])
    assert plain.success


def test_a_negative_subdivision_count_is_rejected():
    with pytest.raises(ValueError, match="subdivisions"):
        Event(lambda t, y: y[0], subdivisions=-1)


def test_subdivision_still_finds_a_single_ordinary_crossing():
    """The common case must not regress: one crossing, found once, not twice."""
    bench = bouncing_ball()
    event = Event(lambda t, y: y[0], terminal=True, direction=-1, subdivisions=8)
    sol = solve(bench.problem, rtol=1e-10, events=[event])

    assert sol.t_events[0].size == 1
    assert sol.t_events[0][0] == pytest.approx(bench.impact_time, abs=1e-9)
