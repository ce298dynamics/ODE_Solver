"""The driver's bookkeeping, tested without running a solve.

`solve` had grown to 408 lines by absorbing four jobs that are not the loop:
validating arguments, deciding where each step lands, accumulating output, and
tracking events. They are now in `odesuite._loop`, which is the point of this
file -- extracting them was only worth doing if it made them checkable, and
until now every one of these rules could be verified only by inference from a
finished trajectory.

The load-bearing one is `StepPlanner`. It owns the exact-landing arithmetic
behind the README's recorded bug #4, where a fixed-step method accumulated `t`
by repeated addition and reported a 1.4e+10x step-size spread.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import ODEProblem, solve
from odesuite._loop import (
    EventTracker,
    Recorder,
    StepPlanner,
    prepare_t_eval,
    prepare_tolerances,
    underflow_message,
)
from odesuite.solution import Stats
from odesuite.steppers import make_stepper


def _problem(t_span=(0.0, 1.0), n=1):
    return ODEProblem(lambda t, y: -y, t_span, np.ones(n))


# ---------------------------------------------------------------------------
# prepare_tolerances
# ---------------------------------------------------------------------------


def test_an_impossible_rtol_is_raised_to_what_is_achievable():
    """Below ~10 eps no finite-precision method can deliver, and thrashing on
    rejected steps is a worse answer than quietly asking for the possible."""
    rtol, _ = prepare_tolerances(1e-20, 1e-12, np.inf, 1)
    assert rtol == pytest.approx(10 * np.finfo(float).eps)


def test_a_workable_rtol_is_left_alone():
    rtol, _ = prepare_tolerances(1e-8, 1e-10, np.inf, 1)
    assert rtol == 1e-8


def test_atol_may_be_scalar_or_per_component():
    _, scalar = prepare_tolerances(1e-6, 1e-9, np.inf, 3)
    assert scalar.ndim == 0
    _, vector = prepare_tolerances(1e-6, [1e-9, 1e-8, 1e-7], np.inf, 3)
    assert vector.shape == (3,)


@pytest.mark.parametrize(
    "kwargs,message",
    [
        (dict(rtol=0.0), "rtol must be positive"),
        (dict(rtol=-1e-6), "rtol must be positive"),
        (dict(atol=-1e-9), "atol must be non-negative"),
        (dict(atol=[1e-9, 1e-9]), "expected 3"),
        (dict(max_step=0.0), "max_step must be positive"),
        (dict(max_step=-1.0), "max_step must be positive"),
    ],
)
def test_bad_tolerances_are_rejected(kwargs, message):
    call = dict(rtol=1e-6, atol=1e-9, max_step=np.inf, n=3)
    call.update(kwargs)
    with pytest.raises(ValueError, match=message):
        prepare_tolerances(**call)


# ---------------------------------------------------------------------------
# prepare_t_eval
# ---------------------------------------------------------------------------


def test_t_eval_is_sorted_into_the_integration_direction():
    forward = prepare_t_eval([0.9, 0.1, 0.5], 0.0, 1.0, 1.0)
    assert list(forward) == [0.1, 0.5, 0.9]

    backward = prepare_t_eval([0.1, 0.9, 0.5], 1.0, 0.0, -1.0)
    assert list(backward) == [0.9, 0.5, 0.1]


def test_t_eval_outside_the_span_is_rejected():
    with pytest.raises(ValueError, match="within t_span"):
        prepare_t_eval([0.5, 1.5], 0.0, 1.0, 1.0)
    with pytest.raises(ValueError, match="within t_span"):
        prepare_t_eval([-0.5], 0.0, 1.0, 1.0)


def test_t_eval_edge_cases():
    assert prepare_t_eval(None, 0.0, 1.0, 1.0) is None
    assert prepare_t_eval([], 0.0, 1.0, 1.0).size == 0


# ---------------------------------------------------------------------------
# StepPlanner -- exact landings
# ---------------------------------------------------------------------------


def _planner(method, **kwargs):
    problem = kwargs.pop("problem", _problem())
    stepper = make_stepper(method)
    defaults = dict(
        first_step=None, n_steps=None, max_step=np.inf,
        rtol=1e-6, atol=np.asarray(1e-9), f0=-problem.y0, stats=Stats(),
    )
    defaults.update(kwargs)
    return StepPlanner(stepper, problem, **defaults)


def test_a_fixed_step_run_lands_on_exact_multiples():
    """Recorded bug #4: accumulating `t` by repeated addition drifts by
    O(n*eps) and leaves the final step a rounding error short of `tf`, which
    made a constant-step method report a huge step-size spread. Every target
    here is computed from `t0` afresh.
    """
    planner = _planner("verlet", problem=_problem((0.0, 1.0), n=2), n_steps=7)

    targets = []
    t = 0.0
    for accepted in range(7):
        h, h_abs, t_target, last = planner.plan(t, accepted)
        targets.append(t_target)
        t = t_target

    # Exact, not merely close: bit-for-bit equal to t0 + k*h.
    for k, target in enumerate(targets[:-1], start=1):
        assert target == 0.0 + k * (1.0 / 7)
    assert targets[-1] == 1.0, "the last step must land exactly on tf"


def test_a_fixed_step_run_reports_its_last_step():
    planner = _planner("verlet", problem=_problem((0.0, 1.0), n=2), n_steps=4)
    flags = [planner.plan(i * 0.25, i)[3] for i in range(4)]
    assert flags == [False, False, False, True]


def test_a_fixed_step_size_that_does_not_divide_the_span_shortens_the_last_step():
    """Documented behaviour: overshooting tf would be worse than one uneven
    step at the end."""
    planner = _planner("verlet", problem=_problem((0.0, 1.0), n=2), first_step=0.3)
    assert planner.total_fixed_steps == 4          # ceil(1.0 / 0.3)

    t, sizes = 0.0, []
    for accepted in range(4):
        h, _, t_target, _ = planner.plan(t, accepted)
        sizes.append(h)
        t = t_target
    assert t == 1.0
    assert sizes[:-1] == pytest.approx([0.3, 0.3, 0.3])
    assert sizes[-1] == pytest.approx(0.1)


def test_a_fixed_step_method_demands_a_step_size():
    with pytest.raises(ValueError, match="fixed step size"):
        _planner("verlet", problem=_problem((0.0, 1.0), n=2))


def test_an_adaptive_run_clamps_the_final_step_onto_tf():
    planner = _planner("dopri5")
    planner.h_abs = 0.4
    h, h_abs, t_target, last = planner.plan(0.8, 5)

    assert last is True
    assert t_target is None, "an adaptive run has no precomputed target"
    assert 0.8 + h == 1.0, "the step must land exactly on tf, not past it"
    assert h_abs == pytest.approx(0.2)


def test_an_adaptive_run_does_not_clamp_an_interior_step():
    planner = _planner("dopri5")
    planner.h_abs = 0.1
    h, h_abs, t_target, last = planner.plan(0.2, 3)
    assert last is False and h == pytest.approx(0.1)


def test_max_step_caps_every_step():
    planner = _planner("dopri5", max_step=0.05)
    planner.h_abs = 10.0
    h, h_abs, _, _ = planner.plan(0.0, 0)
    assert h_abs <= 0.05


def test_the_automatic_first_step_costs_one_evaluation():
    stats = Stats()
    planner = _planner("dopri5", stats=stats)
    assert stats.nfev == 1, "the two-stage estimate uses one Euler probe"
    assert 0 < planner.h_abs <= 1.0


def test_a_supplied_first_step_is_used_and_bounded():
    assert _planner("dopri5", first_step=0.01).h_abs == pytest.approx(0.01)
    # Never longer than the interval itself.
    assert _planner("dopri5", first_step=10.0).h_abs == pytest.approx(1.0)


def test_first_step_is_a_magnitude_not_a_signed_step():
    """`first_step` is read as a size; the integration direction supplies the
    sign. So a negative value is its magnitude, and only zero is rejected --
    there is no step size a solve could start from."""
    assert _planner("dopri5", first_step=-0.1).h_abs == pytest.approx(0.1)
    with pytest.raises(ValueError, match="first_step must be positive"):
        _planner("dopri5", first_step=0.0)


def test_backward_integration_plans_negative_steps():
    planner = _planner("dopri5", problem=_problem((1.0, 0.0)))
    planner.h_abs = 0.1
    h, h_abs, _, _ = planner.plan(1.0, 0)
    assert h < 0 and h_abs > 0


# ---------------------------------------------------------------------------
# Recorder
# ---------------------------------------------------------------------------


class _Constant:
    """An interpolant returning a fixed column, whatever it is asked for."""

    def __init__(self, value):
        self.value = np.asarray(value, dtype=float)

    def __call__(self, t):
        t = np.asarray(t, dtype=float)
        if t.ndim == 0:
            return self.value
        return np.tile(self.value[:, None], (1, t.size))


def test_without_t_eval_every_accepted_step_is_reported():
    recorder = Recorder(_problem(), None, 1.0)
    assert recorder.ts == [0.0], "the initial state is recorded up front"

    recorder.accept(None, 0.5, np.array([0.5]))
    recorder.accept(None, 1.0, np.array([0.25]))
    t, y, _ = recorder.arrays()
    assert list(t) == [0.0, 0.5, 1.0]
    assert y.shape == (1, 3)


def test_with_t_eval_only_the_requested_times_are_reported():
    grid = prepare_t_eval([0.25, 0.75], 0.0, 1.0, 1.0)
    recorder = Recorder(_problem(), grid, 1.0)
    assert recorder.ts == [], "0.0 was not requested, so it is not recorded"

    recorder.accept(_Constant([9.0]), 0.5, np.array([0.5]))
    recorder.accept(_Constant([8.0]), 1.0, np.array([0.25]))
    t, y, _ = recorder.arrays()
    assert list(t) == [0.25, 0.75]
    # Sampled off each step's interpolant, not from the step endpoints.
    assert list(y[0]) == [9.0, 8.0]


def test_a_requested_sample_exactly_on_t0_needs_no_interpolation():
    grid = prepare_t_eval([0.0, 0.5], 0.0, 1.0, 1.0)
    recorder = Recorder(_problem(), grid, 1.0)
    assert recorder.ts == [0.0]


def test_rejections_are_recorded_as_time_and_step_size():
    recorder = Recorder(_problem(), None, 1.0)
    recorder.reject(0.3, 0.01)
    recorder.reject(0.4, 0.005)
    _, _, rejected = recorder.arrays()
    assert rejected.shape == (2, 2)
    assert list(rejected[:, 0]) == [0.3, 0.4]


def test_no_rejections_gives_an_empty_two_column_array():
    _, _, rejected = Recorder(_problem(), None, 1.0).arrays()
    assert rejected.shape == (0, 2)


def test_interpolants_are_kept_only_when_supplied():
    recorder = Recorder(_problem(), None, 1.0)
    recorder.accept(None, 0.5, np.array([0.5]))
    assert recorder.interpolants == []
    recorder.accept(_Constant([1.0]), 1.0, np.array([0.25]))
    assert len(recorder.interpolants) == 1


# ---------------------------------------------------------------------------
# EventTracker
# ---------------------------------------------------------------------------


def test_a_tracker_with_no_events_is_falsey():
    tracker = EventTracker([], (), 0.0, np.array([1.0]))
    assert not tracker
    t_events, y_events = tracker.arrays(1)
    assert t_events == [] and y_events == []


def test_the_tracker_locates_a_crossing_and_reports_termination():
    from odesuite import Event

    event = Event(lambda t, y: y[0], terminal=True, direction=-1)
    tracker = EventTracker([event], (), 0.0, np.array([1.0]))
    assert tracker

    # A straight line from +1 to -1 across the step crosses zero at the middle.
    class Line:
        def __call__(self, t):
            return np.asarray([1.0 - 2.0 * float(t)])

    end_t, end_y, terminated = tracker.process(Line(), 0.0, 1.0, np.array([-1.0]))
    assert terminated
    assert end_t == pytest.approx(0.5)
    assert tracker.exhausted_names() == event.name


def test_the_tracker_carries_g_across_steps():
    """The only state event detection needs, and getting it wrong would either
    miss every crossing or report each one twice."""
    from odesuite import Event

    tracker = EventTracker([Event(lambda t, y: y[0])], (), 0.0, np.array([1.0]))

    class Line:
        def __call__(self, t):
            return np.asarray([1.0 - float(t)])

    # First step stays positive: no crossing.
    _, _, terminated = tracker.process(Line(), 0.0, 0.5, np.array([0.5]))
    assert not terminated
    assert tracker.t_events[0] == []

    # Second step crosses.
    tracker.process(Line(), 0.5, 1.5, np.array([-0.5]))
    assert len(tracker.t_events[0]) == 1
    assert tracker.t_events[0][0] == pytest.approx(1.0)


def test_scanning_is_decided_once_from_the_events():
    from odesuite import Event

    plain = EventTracker([Event(lambda t, y: y[0])], (), 0.0, np.array([1.0]))
    assert plain.scanning is False

    scanned = EventTracker(
        [Event(lambda t, y: y[0]), Event(lambda t, y: y[0], subdivisions=4)],
        (), 0.0, np.array([1.0]),
    )
    assert scanned.scanning is True, "one event asking is enough"


# ---------------------------------------------------------------------------
# Failure messages
# ---------------------------------------------------------------------------


def test_underflow_names_the_cause_it_can_identify():
    plain = underflow_message(1.5, 1e-16, None)
    assert "underflow" in plain and "singular or blowing up" in plain

    nonfinite = underflow_message(1.5, 1e-16, 0.5)
    assert "non-finite" in nonfinite and "0.5" in nonfinite
    assert "underflow" not in nonfinite


# ---------------------------------------------------------------------------
# The extraction changed nothing
# ---------------------------------------------------------------------------


def test_the_driver_still_owns_the_loop():
    """`_loop` is bookkeeping, not integration. If a stepper or a tableau ever
    appears in it, the separation the whole design rests on has gone."""
    import odesuite._loop as loop

    source = open(loop.__file__, encoding="utf-8").read()
    for forbidden in ("make_stepper", "ButcherTableau", "stepper.step("):
        assert forbidden not in source, f"{forbidden} does not belong in _loop"


def test_a_representative_solve_is_unchanged_by_the_extraction():
    """A coarse end-to-end anchor. The refactor was gated on 78 solves hashing
    bit-identically; this keeps one of them in the suite."""
    from odesuite.problems import lotka_volterra

    bench = lotka_volterra()
    sol = solve(bench.problem, "dopri5", rtol=1e-10, atol=1e-12, dense_output=True)
    assert sol.success
    assert sol.stats.naccepted == 1579
    assert sol.y_at(5.0)[0] == pytest.approx(0.2641867721, abs=1e-8)
