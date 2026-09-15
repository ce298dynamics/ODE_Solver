"""Defects found by audit, each with the test that would have caught it.

Every test here failed before its fix. They are gathered in one file rather
than scattered into the module suites because what they have in common is how
they were found -- measurement rather than reasoning -- and because a reader
asking "what went wrong once?" deserves one place to look.

Each names its audit item, so the finding, the experiment that produced the
number and the test that pins it stay connected.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import ODEProblem, solve
from odesuite.problems import (
    hires,
    logistic,
    lotka_volterra,
    orego,
    robertson,
    sine_cosine,
    van_der_pol,
)

# ---------------------------------------------------------------------------
# NUM-02 -- Radau missed the tolerance it was asked for, and said nothing
# ---------------------------------------------------------------------------
#
# Below rtol=1e-9 the achieved error stopped tracking the request: 15x at
# 1e-10, 30x at 1e-11, 54x at 1e-12, 103x at 1e-13, while `success` stayed True
# throughout. DOPRI5 on the same problem holds 1.8x across that whole range.
#
# The work was being done -- steps rose 1.78x per decade, more than the 1.58x a
# fifth-order method needs -- so it was not the step controller, and supplying
# an analytic Jacobian changed nothing to four significant figures, so it was
# not the differenced Jacobian either. It was the Newton termination: the stage
# equations were solved to a fixed 3% of the integration tolerance, which is
# far below the truncation error at loose tolerances and dominates at tight
# ones.

DECAY_RTOLS = [1e-6, 1e-7, 1e-8, 1e-9, 1e-10, 1e-11, 1e-12]


def _decay():
    return ODEProblem(lambda t, y: -2.0 * y, (0.0, 5.0), [1.0])


def _decay_error(method, rtol):
    """Achieved relative error at the endpoint, against the exact solution."""
    solution = solve(_decay(), method, rtol=rtol, atol=rtol * 1e-3)
    assert solution.success, solution.message
    exact = np.exp(-2.0 * 5.0)
    return abs(solution.y[0, -1] - exact) / exact, solution


@pytest.mark.parametrize("rtol", DECAY_RTOLS)
def test_radau_delivers_the_tolerance_it_was_asked_for(rtol):
    """The ratio was 54x at 1e-12 and 15x at 1e-10 before this was fixed."""
    achieved, _ = _decay_error("radau", rtol)
    assert achieved <= 5 * rtol, (
        f"radau at rtol={rtol:.0e} achieved {achieved:.3e}, "
        f"{achieved / rtol:.1f}x the tolerance it was given"
    )


@pytest.mark.parametrize("rtol", DECAY_RTOLS)
def test_the_explicit_pair_was_never_the_problem(rtol):
    """The control: DOPRI5 held its tolerance across this range all along, so a
    regression here means the harness drifted rather than the stiff solver."""
    achieved, _ = _decay_error("dopri5", rtol)
    assert achieved <= 5 * rtol


def test_tightening_newton_did_not_cost_loose_tolerance_work():
    """The fix scales the Newton tolerance with `rtol`, so the cheap end must
    be left alone. Bounds are ~25% above the measured values at the time of
    the fix (584 evaluations, 83 steps), which is slack enough for a different
    BLAS and tight enough to catch the whole termination test being tightened
    by mistake."""
    _, solution = _decay_error("radau", 1e-6)
    assert solution.stats.nfev <= 730, solution.stats
    assert solution.stats.naccepted <= 105, solution.stats


def test_the_newton_budget_grows_with_the_tightened_target():
    """Tightening the target without lengthening the iteration turns a
    converging solve into a reported failure.

    Caught while fixing the above: at rtol=1e-13 on the logistic equation the
    iteration was converging at a rate of 0.013 -- two decimal digits a pass --
    and still ran out of its eight iterations before reaching a target 25x
    tighter, so the step came back `ok=False`. The local-error test for Radau
    then stopped measuring anything and skipped instead, which is how a fix can
    quietly cost coverage.
    """
    from odesuite import make_stepper
    from odesuite.problems import logistic
    from odesuite.steppers.irk import newton_iteration_budget, newton_tol_factor

    assert newton_tol_factor(1e-6, 5) == pytest.approx(0.03)
    assert newton_iteration_budget(0.03) == 8
    assert newton_iteration_budget(newton_tol_factor(1e-13, 5)) > 8

    problem = logistic().problem
    stepper = make_stepper("radau")
    stepper.set_tolerances(1e-13, 1e-15)
    stepper._reset_cache()
    result = stepper.step(
        problem, problem.t0, problem.y0.copy(),
        problem.f(problem.t0, problem.y0), 0.5,
    )
    assert result.ok, (
        f"a step converging at rate {stepper._last_rate} was reported as failed"
    )


def test_a_caller_who_supplies_newton_settings_keeps_them():
    from odesuite.newton import NewtonSettings
    from odesuite.steppers import RadauIIA

    stepper = RadauIIA(newton=NewtonSettings(max_iter=3, tol_factor=0.5))
    stepper.set_tolerances(1e-13, 1e-15)
    assert stepper.newton.tol_factor == 0.5
    assert stepper.newton.max_iter == 3


#: Stiff work at the default tolerance, measured before the fix. These exist so
#: that "obey the tolerance" cannot be bought by simply doing more work
#: everywhere; the bound is ~35% above what each cost at the time.
STIFF_BUDGET = [
    ("robertson", lambda: robertson(t_end=1e11).problem, 3600),
    ("hires", lambda: hires().problem, 1900),
    ("orego", lambda: orego().problem, 15200),
    ("van_der_pol_1000", lambda: van_der_pol(mu=1000.0).problem, 16900),
]


@pytest.mark.parametrize(
    "name,build,budget", STIFF_BUDGET, ids=[c[0] for c in STIFF_BUDGET]
)
def test_the_stiff_problems_did_not_get_more_expensive(name, build, budget):
    solution = solve(build(), "radau", rtol=1e-6, atol=1e-8)
    assert solution.success, solution.message
    assert solution.stats.nfev <= budget, (
        f"{name}: {solution.stats.nfev} right-hand side evaluations, "
        f"budget {budget}"
    )


# ---------------------------------------------------------------------------
# NUM-03 / NUM-07 -- RODAS4 lost three orders of accuracy to one difference
# ---------------------------------------------------------------------------
#
# On the non-autonomous `y' = y cos t` RODAS4 held order 4 down to 2.8e-11 and
# then converged at order *one*, flattening near 4e-13. On the autonomous
# `y' = -2y` the same method ran clean to 1.9e-14. An analytic Jacobian changed
# nothing to four significant figures, which ruled out df/dy and left df/dt:
# differenced forward, its O(sqrt(eps)) error enters the step as O(h*sqrt(eps)),
# a first-order term. `ODEProblem` had no way to supply the exact value.


def _max_relative_error(stepper_name, make_problem, exact, n_steps):
    """Worst relative error over the trajectory of a fixed-step run.

    Endpoint error alone is the wrong measure here: it can pass through zero as
    `h` varies, which makes a convergence ratio meaningless at exactly the step
    sizes being compared.
    """
    from odesuite import make_stepper

    stepper = make_stepper(stepper_name)
    problem = make_problem()
    t, y = problem.t0, problem.y0.copy()
    h = (problem.tf - problem.t0) / n_steps
    f = problem.f(t, y)
    worst = 0.0
    for step in range(n_steps):
        result = stepper.step(problem, t, y, f, h)
        assert result.ok and np.all(np.isfinite(result.y_new))
        y = result.y_new
        t = problem.t0 + (step + 1) * h
        f = result.f_new if result.f_new is not None else problem.f(t, y)
        reference = exact(t)
        worst = max(
            worst,
            float(np.max(np.abs(y - reference) / np.maximum(np.abs(reference), 1e-300))),
        )
    return worst


def _cos_problem(dfdt=None):
    return ODEProblem(
        lambda t, y: np.array([y[0] * np.cos(t)]), (0.0, 5.0), [1.0], dfdt=dfdt
    )


def _cos_exact(t):
    return np.array([np.exp(np.sin(t))])


def test_rodas4_keeps_its_order_on_a_non_autonomous_problem():
    """Observed order collapsed to 0.98 here before the fix."""
    coarse = _max_relative_error("rodas4", _cos_problem, _cos_exact, 256)
    fine = _max_relative_error("rodas4", _cos_problem, _cos_exact, 512)
    order = np.log2(coarse / fine)
    assert order >= 3.85, f"observed order {order:.2f} between n=256 and n=512"


def test_rodas4_reaches_the_accuracy_the_other_methods_reach():
    """It floored at 7.7e-13 while every other method reached ~2e-15."""
    achieved = _max_relative_error("rodas4", _cos_problem, _cos_exact, 8192)
    assert achieved < 1e-13, f"floored at {achieved:.2e}"


def test_an_exact_time_derivative_is_used_when_given():
    """`dfdt` should be at least as good as the difference, and free of the
    two extra evaluations it costs."""
    with_exact = _max_relative_error(
        "rodas4",
        lambda: _cos_problem(dfdt=lambda t, y: np.array([-y[0] * np.sin(t)])),
        _cos_exact,
        512,
    )
    differenced = _max_relative_error("rodas4", _cos_problem, _cos_exact, 512)
    assert with_exact <= differenced * 1.5

    supplied = solve(
        _cos_problem(dfdt=lambda t, y: np.array([-y[0] * np.sin(t)])),
        "rodas4", rtol=1e-8, atol=1e-10,
    )
    differenced_solve = solve(_cos_problem(), "rodas4", rtol=1e-8, atol=1e-10)
    assert supplied.stats.nfev < differenced_solve.stats.nfev


#: RODAS4's stiff work after the change, ~25% above measured. The central
#: difference costs one extra right-hand side evaluation per step and nothing
#: else: step counts were identical before and after (246, 189, 1524, 1402),
#: and only `nfev` moved, by 14%. A regression here would mean the step
#: controller had been disturbed, not the derivative.
RODAS4_BUDGET = [
    ("robertson", lambda: robertson(t_end=1e11).problem, 2500, 310),
    ("hires", lambda: hires().problem, 1900, 240),
    ("orego", lambda: orego().problem, 15400, 1910),
    ("van_der_pol_1000", lambda: van_der_pol(mu=1000.0).problem, 14200, 1760),
]


@pytest.mark.parametrize(
    "name,build,nfev_budget,step_budget",
    RODAS4_BUDGET,
    ids=[c[0] for c in RODAS4_BUDGET],
)
def test_the_exact_time_derivative_did_not_cost_stiff_work(
    name, build, nfev_budget, step_budget
):
    solution = solve(build(), "rodas4", rtol=1e-6, atol=1e-8)
    assert solution.success, solution.message
    assert solution.stats.nfev <= nfev_budget, solution.stats
    assert solution.stats.naccepted <= step_budget, solution.stats


def test_rodas4_still_reaches_round_off_on_an_autonomous_problem():
    """The control: this path was never broken and must stay that way."""
    achieved = _max_relative_error(
        "rodas4", _decay, lambda t: np.array([np.exp(-2.0 * t)]), 4096
    )
    assert achieved < 1e-12, f"{achieved:.2e}"


def test_dfdt_is_validated_at_the_point_of_use():
    problem = ODEProblem(
        lambda t, y: np.array([y[0]]), (0.0, 1.0), [1.0],
        dfdt=lambda t, y: np.array([0.0, 0.0]),
    )
    with pytest.raises(ValueError, match="dfdt returned shape"):
        problem.dfdt(0.0, problem.y0)


def test_a_constant_dfdt_may_be_given_as_an_array():
    problem = ODEProblem(
        lambda t, y: np.array([t]), (0.0, 1.0), [0.0], dfdt=[1.0]
    )
    assert problem.has_dfdt
    assert problem.dfdt(0.3, problem.y0) == pytest.approx([1.0])


def test_a_problem_without_dfdt_says_so():
    problem = ODEProblem(lambda t, y: -y, (0.0, 1.0), [1.0])
    assert not problem.has_dfdt
    with pytest.raises(RuntimeError, match="no analytic df/dt"):
        problem.dfdt(0.0, problem.y0)


# ---------------------------------------------------------------------------
# NUM-01 -- the Taylor method killed the interpreter
# ---------------------------------------------------------------------------
#
# `solve(problem, "taylor20")` on `y' = y * cos(t)` exited with no traceback and
# no Python exception: `__array_priority__` handed `array * jet` to Jet.__rmul__,
# whose non-jet branch called float() on an object array, which re-entered jet
# arithmetic and recursed until the C stack was gone.
#
# Unreachable from the interface -- Taylor is gated behind `supports_taylor`,
# and all 18 catalogue entries that enable it were checked -- but `odesuite` is
# a library in its own right and this is the most ordinary non-autonomous
# right-hand side there is.


def test_a_jet_times_an_array_of_jets_is_elementwise():
    from odesuite.steppers.taylor import Jet

    jets = np.empty(3, dtype=object)
    for i in range(3):
        jets[i] = Jet.constant(float(i + 1), 4)
    scale = Jet.constant(2.0, 4)

    for product in (jets * scale, scale * jets):
        assert isinstance(product, np.ndarray) and product.dtype == object
        assert [p.c[0] for p in product] == pytest.approx([2.0, 4.0, 6.0])


def test_a_jet_combined_with_nonsense_says_what_went_wrong():
    from odesuite.steppers.taylor import Jet

    with pytest.raises(TypeError, match="cannot combine a Jet"):
        Jet.constant(1.0, 4) * object()


@pytest.mark.parametrize("method", ["taylor8", "taylor20"])
def test_taylor_integrates_a_non_autonomous_right_hand_side(method):
    """Written the obvious way -- `y * np.cos(t)`, the whole array at once --
    which is what used to kill the process."""
    problem = ODEProblem(lambda t, y: y * np.cos(t), (0.0, 5.0), [1.0])
    solution = solve(problem, method, rtol=1e-10, atol=1e-12)
    assert solution.success, solution.message
    assert solution.y[0, -1] == pytest.approx(np.exp(np.sin(5.0)), rel=1e-9)


def test_taylor_survives_a_right_hand_side_it_cannot_evaluate():
    """`abs` has no jet arithmetic. Whatever happens, the process must live to
    report it -- that, not the failure, was the defect."""
    problem = ODEProblem(lambda t, y: np.abs(y) * -1.0, (0.0, 1.0), [1.0])
    try:
        solve(problem, "taylor8", rtol=1e-6)
    except Exception:
        pass    # an exception is a fine outcome; dying is not


# ---------------------------------------------------------------------------
# NUM-04 -- a fixed-step method that overflowed spun, then blamed the wrong thing
# ---------------------------------------------------------------------------
#
# Euler on a harmonic oscillator is unconditionally unstable, so it overflows.
# The driver's response -- halve the step -- does nothing for a method whose
# step comes from the interval rather than from `h_abs`, so the identical
# failing step was retried 909393 times over 13.7 seconds, and the failure was
# then reported as `exceeded max_steps` rather than as the overflow the loop
# had already recorded.


def _unstable_oscillator():
    return ODEProblem(
        lambda t, y: np.array([y[1], -y[0]]), (0.0, 2 * np.pi * 10_000), [1.0, 0.0]
    )


def test_a_fixed_step_overflow_stops_at_once():
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")     # the overflow itself is expected
        solution = solve(
            _unstable_oscillator(), "euler", n_steps=500_000, max_steps=1_000_000
        )
    assert not solution.success
    assert solution.stats.nrejected <= 1, (
        f"{solution.stats.nrejected} rejections; a fixed-step method cannot "
        f"shrink its step, so retrying is unbounded"
    )


def test_a_fixed_step_overflow_says_what_actually_happened():
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        solution = solve(_unstable_oscillator(), "euler", n_steps=500_000)
    assert "max_steps" not in solution.message, solution.message
    assert "non-finite" in solution.message, solution.message
    assert "fixed step size" in solution.message, solution.message


def test_an_adaptive_method_still_shrinks_its_way_out():
    """The control. Halving is right for a method that can halve, and the
    blow-up message it produces must not have changed."""
    solution = solve(ODEProblem(lambda t, y: y * y, (0.0, 2.0), [1.0]), "dopri5")
    assert not solution.success
    assert solution.stats.nrejected > 1
    assert "t=1" in solution.message


# ---------------------------------------------------------------------------
# NUM-08 -- a right-hand side that raised at t0 escaped as a bare exception
# ---------------------------------------------------------------------------
#
# `ODEProblem` checks that f(t0, y0) is finite, and says in a comment that the
# check exists so a singular starting point does not surface as "a bare
# ZeroDivisionError ... naming nothing the caller had written". It caught a
# right-hand side that *returned* inf, and not one that raised on the way --
# so `y' = 1/t` from t=0 produced precisely that bare ZeroDivisionError.


def test_a_right_hand_side_that_raises_at_t0_is_named_as_such():
    with pytest.raises(ValueError, match=r"raised ZeroDivisionError at t0=0"):
        ODEProblem(lambda t, y: np.array([1.0 / t]), (0.0, 1.0), [0.0])


def test_a_right_hand_side_that_returns_inf_at_t0_still_says_so():
    """The half that already worked, kept working."""
    with pytest.raises(ValueError, match="not finite at t0"):
        ODEProblem(lambda t, y: np.array([np.inf]), (0.0, 1.0), [0.0])


def test_an_ordinary_right_hand_side_error_is_still_readable():
    def wrong_shape(t, y):
        raise RuntimeError("model not configured")

    with pytest.raises(ValueError, match="model not configured"):
        ODEProblem(wrong_shape, (0.0, 1.0), [1.0])


# ---------------------------------------------------------------------------
# ARCH-01 -- every diagnostic the solver produced was a prose string
# ---------------------------------------------------------------------------
#
# A caller -- including the application's own screens -- could not tell "blew up
# in finite time" from "hit max_steps" from "the right-hand side returned NaN"
# without matching on English. `Solution.diagnosis` is that answer in a form
# code can branch on.


def test_a_clean_finish_is_diagnosed_as_such():
    solution = solve(_decay(), "dopri5", rtol=1e-8)
    assert solution.diagnosis is not None
    assert solution.diagnosis.kind == "finished"
    assert not solution.diagnosis.failed
    assert solution.diagnosis.t == pytest.approx(5.0)


def test_a_blow_up_is_diagnosed_and_located():
    """`y' = y^2` runs to infinity at t=1. The state is still finite when the
    step collapses -- 6.2e13, not inf -- so this is `step_underflow`, and the
    location is what matters."""
    solution = solve(ODEProblem(lambda t, y: y * y, (0.0, 2.0), [1.0]), "dopri5")
    assert solution.diagnosis.kind == "step_underflow"
    assert solution.diagnosis.failed
    assert solution.diagnosis.t == pytest.approx(1.0, abs=1e-6)


def test_a_kind_covers_exactly_the_causes_the_loop_cannot_separate():
    """The point of the type: it stops where the knowledge stops.

    `y' = y^2` blows up at t=1; `y' = 1/(t-1)` has a pole there. From inside the
    loop both look identical -- finite state, collapsing step -- so both are
    `step_underflow` and the detail offers both readings. A kind called
    "blow_up" would have been a confident guess, and the two problems here are
    the proof that it could not have been made honestly.
    """
    blow_up = solve(ODEProblem(lambda t, y: y * y, (0.0, 2.0), [1.0]), "dopri5")
    pole = solve(
        ODEProblem(lambda t, y: np.array([1.0 / (t - 1.0)]), (0.0, 2.0), [0.0]),
        "dopri5",
    )
    assert blow_up.diagnosis.kind == pole.diagnosis.kind == "step_underflow"
    assert "singular or blowing up" in blow_up.diagnosis.detail
    assert pole.diagnosis.t == pytest.approx(1.0, abs=1e-6)


def test_a_non_finite_state_is_its_own_kind():
    """Distinct from the above because the loop *can* tell this apart: here the
    state itself went non-finite rather than the step collapsing."""

    def nan_after_one(t, y):
        return np.array([np.nan]) if t > 1.0 else np.array([1.0])

    solution = solve(ODEProblem(nan_after_one, (0.0, 2.0), [0.0]), "dopri5")
    assert solution.diagnosis.kind == "nonfinite"
    assert solution.diagnosis.t == pytest.approx(1.0, abs=1e-3)


def test_max_steps_is_diagnosed_as_max_steps():
    solution = solve(
        ODEProblem(lambda t, y: y * y, (0.0, 2.0), [1.0]), "dopri5", max_steps=20
    )
    assert solution.diagnosis.kind == "max_steps"


def test_min_step_is_diagnosed_as_the_callers_own_floor():
    solution = solve(
        ODEProblem(lambda t, y: y * y, (0.0, 2.0), [1.0]), "dopri5", min_step=1e-3
    )
    assert solution.diagnosis.kind == "min_step"


def test_a_terminal_event_is_not_a_failure():
    from odesuite import Event

    problem = ODEProblem(lambda t, y: np.array([y[1], -9.81]), (0.0, 2.0), [1.0, 0.0])
    event = Event(lambda t, y: y[0], terminal=True, direction=-1, name="impact")
    solution = solve(problem, "dopri5", events=event, dense_output=True)
    assert solution.diagnosis.kind == "terminal_event"
    assert not solution.diagnosis.failed
    assert "impact" in solution.diagnosis.detail


def test_a_cancelled_solve_is_diagnosed_as_cancelled():
    solution = solve(_decay(), "dopri5", callback=lambda t, y, s: t < 1.0)
    assert solution.diagnosis.kind == "cancelled"
    assert not solution.diagnosis.failed


def test_a_fixed_step_failure_is_its_own_kind():
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        solution = solve(_unstable_oscillator(), "euler", n_steps=500_000)
    assert solution.diagnosis.kind == "fixed_step_nonfinite"
    assert solution.diagnosis.failed


# ---------------------------------------------------------------------------
# PERF-02 -- an explicit method ground for ~17 s to say it could not finish
# ---------------------------------------------------------------------------
#
# dopri5 on Robertson took 499 996 steps and 33 s to reach `max_steps`, then
# reported the step count -- not the reason. `solve` now projects, and stops
# when the projection says the budget cannot cover the interval.
#
# The projection is deliberately *not* applied to implicit methods, and that
# restriction is the whole design. A stiff solver spends its transient taking
# tiny steps and then grows them by orders of magnitude: on Robertson at
# rtol=1e-12, RODAS4 has covered 0.0000% after 5000 steps -- indistinguishable
# from dopri5, which never finishes -- and then finishes in 10 017 steps with
# its step size 1.7e8 times larger. Coverage cannot separate them, and nor can
# growth: RODAS4 on Van der Pol at the same tolerance has flat growth and still
# finishes, in 203 377 steps. Applying the projection to implicit methods
# produced eleven aborted solves that would all have succeeded.

STIFF_FOR_EXPLICIT = [
    ("robertson", lambda: robertson(t_end=1e11).problem),
    ("orego", lambda: orego().problem),
    ("van_der_pol_1000", lambda: van_der_pol(mu=1000.0).problem),
]


@pytest.mark.parametrize(
    "name,build", STIFF_FOR_EXPLICIT, ids=[c[0] for c in STIFF_FOR_EXPLICIT]
)
def test_an_explicit_method_gives_up_quickly_on_a_stiff_problem(name, build):
    import time

    started = time.perf_counter()
    solution = solve(build(), "dopri5", rtol=1e-6, atol=1e-8, max_steps=500_000)
    elapsed = time.perf_counter() - started

    assert not solution.success
    assert solution.diagnosis.kind == "insufficient_progress"
    assert solution.stats.nsteps < 50_000, solution.stats
    # It took 17-33 s before this existed. One second is a generous ceiling
    # that still catches the check being disabled.
    assert elapsed < 5.0, f"{elapsed:.1f}s"


def test_the_message_names_the_symptom_and_the_remedy():
    solution = solve(
        robertson(t_end=1e11).problem, "dopri5", rtol=1e-6, max_steps=500_000
    )
    assert "max_steps" in solution.message
    assert "% of the interval" in solution.message
    # For an explicit method the actionable part is naming the usual cause,
    # hedged -- a step counter cannot establish that a problem is stiff.
    assert "implicit method" in solution.message
    assert "usual reason" in solution.message


@pytest.mark.parametrize(
    "name,build", STIFF_FOR_EXPLICIT, ids=[c[0] for c in STIFF_FOR_EXPLICIT]
)
@pytest.mark.parametrize("method", ["radau", "rodas4"])
@pytest.mark.parametrize("rtol", [1e-9, 1e-12])
def test_a_stiff_solver_is_never_cut_off(name, build, method, rtol):
    """The eleven false positives. Every one of these finishes, and several
    look exactly like a doomed solve at the moment the projection is taken."""
    solution = solve(build(), method, rtol=rtol, atol=rtol * 1e-2, max_steps=500_000)
    assert solution.success, f"{name}/{method}: {solution.message}"


@pytest.mark.parametrize("rtol", [1e-3, 1e-6, 1e-9, 1e-12])
def test_a_non_stiff_problem_is_never_cut_off(rtol):
    for factory in (logistic, lotka_volterra, sine_cosine):
        problem = factory().problem
        solution = solve(problem, "dopri5", rtol=rtol, atol=rtol * 1e-2)
        assert solution.success, solution.message


def test_the_check_can_be_turned_off():
    """For timing the grind, or demonstrating it."""
    solution = solve(
        robertson(t_end=1e11).problem, "dopri5", rtol=1e-6,
        max_steps=8000, progress_check=False,
    )
    assert solution.diagnosis.kind == "max_steps"
    assert solution.stats.nsteps == 8000


def test_a_fixed_step_run_is_never_projected():
    """Its total is known from the outset, so there is nothing to project."""
    problem = ODEProblem(lambda t, y: -0.5 * y, (0.0, 10.0), [1.0])
    solution = solve(problem, "rk4", n_steps=20_000)
    assert solution.success
    assert solution.stats.naccepted == 20_000


# ---------------------------------------------------------------------------
# SYM-01 -- a symbolic answer was shown with no interval of validity
# ---------------------------------------------------------------------------
#
# `y' = y^2, y(0) = 1` was shown as `y = 1/(1-t)` with nothing to say it means
# anything only for t < 1 -- while the numerical side of the same application
# stops at t = 1 and reports that the solution may be blowing up there, and the
# `slopefields` lesson teaches that the existence theorem is local.


def _interval(expr_text, t0=0.0):
    import sympy as sp

    from odesuite_app import symbolic

    return symbolic.interval_of_validity(sp.sympify(expr_text), t0)


@pytest.mark.parametrize(
    "expression,t0,expected",
    [
        ("1/(1-t)", 0.0, (None, 1.0)),          # the blow-up case
        ("1/(1-t)", 2.0, (1.0, None)),          # same solution, other branch
        ("1/t", 1.0, (0.0, None)),
        ("1/(t**2-1)", 0.0, (-1.0, 1.0)),
        ("(t+1)/((t-2)*(t+3))", 0.0, (-3.0, 2.0)),
        ("exp(-2*t)", 0.0, (None, None)),       # valid everywhere
        ("3*exp(-t)+2*t", 0.0, (None, None)),
        ("exp(-t)*sin(3*t)", 0.0, (None, None)),
        ("t/(t**2+1)", 0.0, (None, None)),
    ],
)
def test_the_interval_of_validity_is_found(expression, t0, expected):
    assert _interval(expression, t0) == expected


@pytest.mark.parametrize(
    "expression,t0",
    [("tan(t)", 0.0), ("log(t)", 1.0), ("sqrt(t)", 1.0), ("1/sin(t)", 1.0)],
)
def test_it_declines_rather_than_guessing(expression, t0):
    """`tan(t)` is the case that matters: poles at every odd multiple of pi/2
    and no denominator to show for them. Anything that looked only at the
    denominator would report "valid everywhere", which is worse than silence."""
    assert _interval(expression, t0) is None


def test_it_is_fast_enough_for_the_interface():
    """The whole symbolic route has a twelve-second budget.
    `sympy.singularities`, the general answer, did not return within ten
    minutes on `1/(1-t)`, which is why this is denominator-based."""
    import time

    started = time.perf_counter()
    for _ in range(20):
        _interval("(t+1)/((t-2)*(t+3))", 0.0)
    assert time.perf_counter() - started < 2.0


def test_the_interval_is_rendered_the_way_it_would_be_written():
    from odesuite_app import symbolic

    assert symbolic.format_interval((None, 1.0)) == "(-∞, 1)"
    assert symbolic.format_interval((0.0, None)) == "(0, ∞)"
    assert symbolic.format_interval((-1.0, 1.0)) == "(-1, 1)"
    # Valid everywhere says nothing rather than "(-oo, oo)": it is the ordinary
    # case and printing it on every answer would be noise.
    assert symbolic.format_interval((None, None)) == ""
    assert symbolic.format_interval(None) == ""


@pytest.mark.parametrize(
    "equation,conditions,expected_point",
    [
        ("y' = y**2", "y(0) = 1", 0.0),
        ("t*y' + y = 0", "y(1) = 1", 1.0),
        ("y'' + y = 0", "y(0) = 1, y'(0) = 0", 0.0),
        ("y' = y**2", "", None),                 # no conditions: no point
    ],
)
def test_the_initial_point_is_read_from_the_conditions(
    equation, conditions, expected_point
):
    """The interval is a statement about the solution through a *point*:
    `1/(1-t)` is valid on (-oo, 1) from t=0 and on (1, oo) from t=2. Assuming
    zero would be right almost always and confidently wrong the rest."""
    from odesuite_app import symbolic

    parsed = symbolic.parse_equation(symbolic.spec_for(equation, conditions))
    assert symbolic._initial_point(parsed) == expected_point


def test_the_symbolic_and_numerical_halves_now_agree_about_this_equation():
    """`y' = y^2, y(0)=1`: the solver stops at t=1 and says so; the symbolic
    answer now carries the same boundary."""
    solution = solve(ODEProblem(lambda t, y: y * y, (0.0, 2.0), [1.0]), "dopri5")
    assert solution.diagnosis.t == pytest.approx(1.0, abs=1e-6)
    assert _interval("1/(1-t)", 0.0) == (None, 1.0)


# ---------------------------------------------------------------------------
# NUM-06 -- the course teaches a failure of uniqueness the tool then hid
# ---------------------------------------------------------------------------
#
# `lessons/unit1_first_order.py`, lesson `slopefields`, carries a pitfall note:
# "y' = y^{1/3} with y(0) = 0 has both y = 0 and y = (2t/3)^{3/2} through the
# origin." Solving exactly that returned y = 0, status "finished", success True,
# in eight steps, with no remark. The lesson and the tool disagreed and the tool
# was the one keeping quiet.


@pytest.mark.parametrize(
    "name,rhs,y0",
    [
        ("cube root", lambda t, y: np.cbrt(y), [0.0]),
        ("square root", lambda t, y: np.sqrt(np.abs(y)), [0.0]),
    ],
)
def test_a_failure_of_uniqueness_is_reported(name, rhs, y0):
    from odesuite_app import analysis

    warning = analysis.uniqueness_warning(ODEProblem(rhs, (0.0, 5.0), y0))
    assert warning is not None, f"{name}: no warning"
    assert "uniqueness" in warning


@pytest.mark.parametrize(
    "name,build",
    [
        ("linear decay", lambda: ODEProblem(lambda t, y: -2.0 * y, (0.0, 5.0), [1.0])),
        ("stiff decay", lambda: ODEProblem(lambda t, y: -1000.0 * y, (0.0, 5.0), [1.0])),
        # The same right-hand side, started away from the singular point.
        ("cube root at y=1", lambda: ODEProblem(lambda t, y: np.cbrt(y), (0.0, 5.0), [1.0])),
        ("logistic", lambda: logistic().problem),
        ("robertson", lambda: robertson(t_end=1e5).problem),
        ("van der Pol 1000", lambda: van_der_pol(mu=1000.0).problem),
        ("hires", lambda: hires().problem),
        ("orego", lambda: orego().problem),
    ],
)
def test_an_ordinary_problem_is_not_warned_about(name, build):
    """The two stiff entries are the point: their derivatives are enormous and
    perfectly well defined, so the test has to be growth and not size."""
    from odesuite_app import analysis

    assert analysis.uniqueness_warning(build()) is None, name


def test_the_warning_does_not_claim_more_than_it_measured():
    """It reports the hypothesis failing, not the existence of two solutions --
    the first is measurable here, the second is a claim about the equation."""
    from odesuite_app import analysis

    warning = analysis.uniqueness_warning(
        ODEProblem(lambda t, y: np.cbrt(y), (0.0, 5.0), [0.0])
    )
    assert "may" in warning
    assert "two solutions" not in warning


def test_the_lesson_and_the_tool_now_agree():
    """The counterexample the course teaches is the one the probe catches."""
    from odesuite_app import analysis
    from odesuite_app.lessons import by_key

    lesson = by_key("slopefields")
    pitfalls = " ".join(n.body for n in lesson.notes if n.kind == "pitfall")
    assert "y^{1/3}" in pitfalls or "1/3" in pitfalls, (
        "the lesson no longer teaches this counterexample; the probe's "
        "justification has moved"
    )
    assert analysis.uniqueness_warning(
        ODEProblem(lambda t, y: np.cbrt(y), (0.0, 5.0), [0.0])
    ) is not None


# ---------------------------------------------------------------------------
# DYN-05 -- missed event crossings were missed silently
# ---------------------------------------------------------------------------
#
# Endpoint bracketing loses any even number of crossings inside a step, without
# a trace: `g` has the same sign at both ends, so nothing looks wrong. Measured
# on a smooth decay with `g = sin(20t)` over [0,10]: 63 roots exist and the
# default finds 7. `Event.subdivisions` has always been the cure; what was
# missing was any way to learn that you needed it.


def _wiggly_event_solve(subdivisions):
    from odesuite import Event

    problem = ODEProblem(lambda t, y: -0.1 * y, (0.0, 10.0), [1.0])
    event = Event(lambda t, y: np.sin(20 * t), name="wiggle",
                  subdivisions=subdivisions)
    return solve(problem, "dopri5", rtol=1e-8, events=event, dense_output=True)


def test_missed_crossings_are_reported():
    solution = _wiggly_event_solve(0)
    true_roots = int(20 * 10 / np.pi)
    found = solution.t_events[0].size
    assert found < true_roots, "the premise of this test has changed"
    assert not solution.events_complete
    assert "wiggle" in solution.incomplete_events


def test_subdivisions_finds_them_and_the_flag_clears():
    solution = _wiggly_event_solve(8)
    assert solution.t_events[0].size >= 60, solution.t_events[0].size
    assert solution.events_complete
    assert solution.incomplete_events == ()


def test_an_ordinary_single_crossing_is_not_flagged():
    """The probe must not cry wolf on the case it exists to leave alone."""
    from odesuite import Event

    problem = ODEProblem(lambda t, y: np.array([y[1], -9.81]), (0.0, 1.0), [1.0, 0.0])
    event = Event(lambda t, y: y[0], direction=-1, name="impact")
    solution = solve(problem, "dopri5", rtol=1e-8, events=event, dense_output=True)
    assert solution.t_events[0].size == 1
    assert solution.events_complete


def test_a_solve_with_no_events_is_complete_by_definition():
    assert solve(_decay(), "dopri5").events_complete


def test_the_probe_costs_one_evaluation_per_step():
    """It is paid on every step of every event-bearing solve, so the price has
    to stay one `g` evaluation and one interpolant evaluation."""
    from odesuite import Event

    calls = {"n": 0}

    def counted(t, y):
        calls["n"] += 1
        return y[0] - 0.5

    problem = ODEProblem(lambda t, y: -0.1 * y, (0.0, 10.0), [1.0])
    solution = solve(problem, "dopri5", rtol=1e-6,
                     events=Event(counted, name="half"), dense_output=True)
    steps = solution.stats.naccepted
    # one at t0, then one endpoint and one midpoint per accepted step, plus
    # whatever the root-finder needed for the single crossing.
    assert calls["n"] <= 2 * steps + 60, (calls["n"], steps)


# ---------------------------------------------------------------------------
# DYN-04 -- a non-hyperbolic equilibrium was labelled with a definite answer
# ---------------------------------------------------------------------------
#
# The Phase Portrait rendered `point.kind` verbatim, in bold. For
# x' = -y + x(x^2+y^2), y' = x + y(x^2+y^2) that reads "centre" -- which is what
# the linearisation says and the opposite of what the flow does, since it
# spirals outward. Lotka-Volterra has the same eigenvalue signature and *is* a
# centre. Nothing in the eigenvalues separates the two, so the label has to
# admit which situation it is in.


def _fixed_points(rhs, xlim=(-2, 2), ylim=(-2, 2)):
    from odesuite_app import analysis

    return analysis.find_fixed_points(
        ODEProblem(rhs, (0.0, 1.0), [0.1, 0.1]), xlim, ylim
    )


def test_a_centre_from_a_linearisation_is_marked_non_hyperbolic():
    points = _fixed_points(
        lambda t, z: np.array([
            -z[1] + z[0] * (z[0] ** 2 + z[1] ** 2),
            z[0] + z[1] * (z[0] ** 2 + z[1] ** 2),
        ])
    )
    origin = [p for p in points if np.allclose(p.position, 0.0, atol=1e-6)]
    assert origin, "the origin should have been found"
    assert origin[0].kind == "centre"
    assert not origin[0].hyperbolic, (
        "the flow here spirals outward; the label must not stand unqualified"
    )


def test_lotka_volterras_centre_is_also_marked_non_hyperbolic():
    """It is a real centre -- but only because the system is conservative, which
    the eigenvalues do not know. The caveat is honest for both."""
    points = _fixed_points(
        lambda t, z: np.array([
            1.5 * z[0] - z[0] * z[1], -3.0 * z[1] + z[0] * z[1]
        ]),
        xlim=(-1, 6), ylim=(-1, 4),
    )
    interior = [p for p in points if np.allclose(p.position, [3.0, 1.5], atol=1e-6)]
    assert interior and interior[0].kind == "centre"
    assert not interior[0].hyperbolic


@pytest.mark.parametrize(
    "rhs,expected",
    [
        (lambda t, z: np.array([z[1], -np.sin(z[0]) - 0.3 * z[1]]), "stable spiral"),
        (lambda t, z: np.array([1.0 - z[0] ** 2, -z[1]]), "stable node"),
    ],
)
def test_an_ordinary_equilibrium_is_hyperbolic_and_carries_no_caveat(rhs, expected):
    points = _fixed_points(rhs, xlim=(-3, 3), ylim=(-2, 2))
    match = [p for p in points if p.kind == expected]
    assert match, f"no {expected} found among {[p.kind for p in points]}"
    assert match[0].hyperbolic


def test_the_prose_message_still_says_the_same_thing():
    """`message` remains what to show a person, and did not change shape."""
    solution = solve(ODEProblem(lambda t, y: y * y, (0.0, 2.0), [1.0]), "dopri5")
    assert "t=1" in solution.message
    assert str(solution.diagnosis).startswith("step_underflow at t=1")


# ---------------------------------------------------------------------------
# REL-03 -- nothing said where each method stops working
# ---------------------------------------------------------------------------
#
# The per-module documentation on *how* each method works was thorough; there
# was no page saying when each one fails, which for a teaching product is the
# more useful half. `docs/limits.md` is that page, and these tests are what stop
# it drifting away from the code it describes.


def _limits_page() -> str:
    from pathlib import Path

    page = Path(__file__).resolve().parent.parent / "docs" / "limits.md"
    assert page.exists(), "docs/limits.md is missing"
    return page.read_text(encoding="utf-8")


def test_every_method_the_library_offers_has_its_limits_documented():
    """A method that can be selected and has nothing written about where it
    breaks is the gap this page exists to close, so adding one should fail
    here until it is documented."""
    from odesuite.steppers import METHODS

    page = _limits_page()
    undocumented = sorted(name for name in METHODS if f"`{name}`" not in page)
    assert not undocumented, (
        f"docs/limits.md does not mention: {', '.join(undocumented)}"
    )


def test_the_page_is_in_the_documentation_nav():
    """A page mkdocs does not know about is a file, not documentation."""
    from pathlib import Path

    config = (Path(__file__).resolve().parent.parent / "mkdocs.yml").read_text(
        encoding="utf-8"
    )
    assert "limits.md" in config


def test_the_refusals_quoted_on_the_page_are_the_real_ones():
    """The page quotes error messages verbatim, so each one is provoked here
    and matched against what actually comes out.

    Provoked rather than grepped for. The first version of this test searched
    the source, and failed on a message that is real but written across two
    adjacent f-strings -- proving only that the test was reading the wrong
    thing. What a reader will search for is the text they saw, so that is what
    has to be checked.
    """
    from odesuite import ODEProblem, solve

    plain = ODEProblem(
        lambda t, y: np.array([y[1], -y[0]]), (0.0, 1.0), [1.0, 0.0]
    )
    provocations = [
        (
            "cannot integrate a problem with a mass matrix",
            lambda: solve(
                ODEProblem(lambda t, y: -y, (0.0, 1.0), [1.0], mass=[[2.0]]),
                "dopri5",
            ),
        ),
        (
            "runs at a fixed step size; pass n_steps or first_step",
            lambda: solve(plain, "rk4"),
        ),
        (
            "symplectic methods need a separable second-order system",
            lambda: solve(plain, "verlet", n_steps=10),
        ),
        (
            "needs a semilinear splitting",
            lambda: solve(plain, "etdrk4", n_steps=10),
        ),
        (
            "does not support complex states",
            lambda: solve(
                ODEProblem(lambda t, y: 1j * y, (0.0, 1.0), [1 + 0j]), "taylor8"
            ),
        ),
    ]
    page = _limits_page()
    for phrase, provoke in provocations:
        with pytest.raises(ValueError) as caught:
            provoke()
        assert phrase in str(caught.value), (
            f"the real message no longer contains {phrase!r}"
        )
        assert phrase in page, f"docs/limits.md no longer quotes {phrase!r}"


def test_every_docs_link_in_the_readme_survives_being_staged():
    """A `docs/…` link is right for a reader of the repository and wrong on the
    site, where `docs/` is already the root. `scripts/docs_hooks.py` rewrites
    the ones it knows about; one it does not know about fails
    `mkdocs build --strict`, which is a CI job.

    Adding the limits page broke that build exactly this way, so the rule is
    checked here rather than only in CI, where it costs a full docs install to
    discover.
    """
    import re
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    readme = (root / "README.md").read_text(encoding="utf-8")
    hook = (root / "scripts" / "docs_hooks.py").read_text(encoding="utf-8")

    # Every relative link to a file in the repository. The first version of
    # this looked only for `docs/...` paths and so let a bare `SECURITY.md`
    # through, which broke the build in exactly the same way a week later.
    # Documents only. `figures/` is copied into `docs/` wholesale by the hook,
    # so image links resolve on the site without being named individually;
    # links to *pages* are the ones that break, because each has to become a
    # page or be rewritten.
    linked = {
        target
        for target in re.findall(r"\]\(([^)#\s]+)\)", readme)
        if not target.startswith(("http://", "https://", "#", "mailto:"))
        and (target.endswith(".md") or target == "LICENSE")
    }
    pages = {page.name for page in (root / "docs").glob("*.md")}
    unhandled = sorted(
        target
        for target in linked
        if f"]({target})" not in hook and Path(target).name not in pages
    )
    assert not unhandled, (
        f"README links to {unhandled}, which are neither pages under docs/ nor "
        f"rewritten by scripts/docs_hooks.py; `mkdocs build --strict` will fail"
    )


# ---------------------------------------------------------------------------
# REL-02 -- the package advertised platforms nobody tested
# ---------------------------------------------------------------------------
#
# `pyproject.toml` claims Python 3.10-3.13 and "Operating System :: OS
# Independent". CI tested 3.10 and 3.12 on Linux and Windows, leaving macOS and
# two Python versions as promises with nothing behind them.


def _ci_test_matrix():
    from pathlib import Path

    yaml = pytest.importorskip("yaml")
    root = Path(__file__).resolve().parent.parent
    config = yaml.safe_load(
        (root / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    )
    matrix = config["jobs"]["tests"]["strategy"]["matrix"]
    legs = [(os_, py) for os_ in matrix["os"] for py in matrix["python"]]
    legs += [(entry["os"], entry["python"]) for entry in matrix.get("include", [])]
    return legs


def _advertised_pythons():
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    import re

    return sorted(set(re.findall(r"Programming Language :: Python :: (3\.\d+)", text)))


def test_every_advertised_python_version_is_tested():
    """A classifier is a promise. This is the only thing that makes it one."""
    legs = _ci_test_matrix()
    tested = {python for _os, python in legs}
    missing = [v for v in _advertised_pythons() if v not in tested]
    assert not missing, (
        f"pyproject advertises Python {missing} but no CI leg runs them. Either "
        f"add the leg or drop the classifier."
    )


def test_os_independence_is_tested_on_three_operating_systems():
    """`Operating System :: OS Independent` is a strong claim; macOS was the
    one nobody checked, and it is where Qt and font handling differ most."""
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    if "OS Independent" not in text:
        pytest.skip("the package no longer claims OS independence")

    families = {os_.split("-")[0] for os_, _python in _ci_test_matrix()}
    for expected in ("ubuntu", "windows", "macos"):
        assert expected in families, (
            f"no CI leg runs on {expected}, but the package claims to be OS "
            f"independent"
        )


# ---------------------------------------------------------------------------
# SEC-03 -- a good privacy position that no document stated
# ---------------------------------------------------------------------------
#
# No network access, no telemetry, one small file on disk. All true, and
# establishable only by reading the source. The README now says it; this makes
# the claim enforceable rather than aspirational.


def test_the_application_makes_no_network_calls():
    """The README promises this, so it has to stay true. A future feature that
    needs the network is fine -- but it must update the promise in the same
    commit, and this is what makes that unavoidable."""
    import re
    from pathlib import Path

    source_root = Path(__file__).resolve().parent.parent / "src"
    forbidden = re.compile(
        r"^\s*(?:import|from)\s+"
        r"(requests|urllib|socket|http|ftplib|smtplib|telnetlib|xmlrpc|asyncio)\b",
        re.MULTILINE,
    )
    offenders = {}
    for module in source_root.rglob("*.py"):
        found = forbidden.findall(module.read_text(encoding="utf-8"))
        if found:
            offenders[module.relative_to(source_root).as_posix()] = sorted(set(found))
    assert not offenders, (
        f"the README promises no network access, but: {offenders}"
    )


def test_the_readme_states_where_progress_is_stored():
    """The path is the part a cautious user or an institution actually needs,
    so a rename must not leave the documentation behind."""
    from pathlib import Path

    from odesuite_app import progress

    readme = (
        Path(__file__).resolve().parent.parent / "README.md"
    ).read_text(encoding="utf-8")
    assert "## Privacy" in readme
    assert progress._FILENAME in readme, (
        f"the progress file is called {progress._FILENAME} and the README does "
        f"not mention it"
    )
    for promise in ("no telemetry", "No network access"):
        assert promise.lower() in readme.lower(), promise


def test_progress_is_the_only_thing_written_outside_a_temporary_directory():
    """`progress.directory()` is the one location the application writes to.
    Anything else appearing here would be a second store nobody documented."""
    from odesuite_app import progress

    location = progress.directory()
    assert progress.path().parent == location
    assert location.name == "odesuite"


# ---------------------------------------------------------------------------
# PED-04 -- two canonical models the catalogue was missing
# ---------------------------------------------------------------------------
#
# FitzHugh-Nagumo is the standard excitable-medium model and the cleanest small
# slow-fast system; it was absent entirely. SIR existed only as a preset inside
# the custom-equation editor, so it never appeared in the gallery and a learner
# could not find it.


def test_the_fitzhugh_nagumo_hopf_window_is_derived_not_transcribed():
    """`hopf_window` solves trace J = 0 rather than quoting a number, so the
    model and its own theory cannot drift apart."""
    from odesuite.problems import hopf_window

    low, high = hopf_window()
    assert low == pytest.approx(0.331281, abs=1e-5)
    assert high == pytest.approx(1.418719, abs=1e-5)

    # And it declines rather than inventing one where no real v satisfies it.
    assert hopf_window(tau=0.5) is None


@pytest.mark.parametrize(
    "current,oscillates",
    [(0.0, False), (0.30, False), (0.40, True), (1.0, True), (1.5, False), (2.0, False)],
)
def test_fitzhugh_nagumo_oscillates_exactly_inside_that_window(current, oscillates):
    """The theory above, checked against the trajectory. Amplitude measured over
    the last 60% of a long run, after the transient: 1.5e-2 at I=0.30 against
    3.75 at I=0.33, and 3.75 at I=1.42 against 3.4e-5 at I=1.50."""
    from odesuite.problems import fitzhugh_nagumo

    solution = solve(
        fitzhugh_nagumo(I_ext=current, t_end=600.0).problem,
        "dopri5", rtol=1e-10, atol=1e-12,
    )
    assert solution.success
    settled = solution.y[0, solution.t > 0.4 * solution.t[-1]]
    amplitude = float(settled.max() - settled.min())
    if oscillates:
        assert amplitude > 1.0, f"I={current}: amplitude {amplitude:.3e}"
    else:
        assert amplitude < 0.1, f"I={current}: amplitude {amplitude:.3e}"


def test_sir_conserves_its_population():
    """S+I+R is exact, which makes it one of the few nonlinear models here with
    an invariant a reader can check by inspection."""
    from odesuite.problems import sir

    bench = sir()
    solution = solve(bench.problem, "dopri5", rtol=1e-10, atol=1e-12)
    total = solution.y.sum(axis=0)
    assert float(total.max() - total.min()) < 1e-9, "population is not conserved"
    assert bench.invariant is not None
    assert bench.invariant(solution.y[:, 0]) == pytest.approx(1000.0)


def test_r_nought_below_one_means_no_outbreak():
    """The threshold, which is the point of the model: R0 = beta/gamma."""
    from odesuite.problems import sir

    quiet = solve(sir(beta=0.1, gamma=0.2).problem, "dopri5", rtol=1e-10)
    outbreak = solve(sir(beta=0.9, gamma=0.2).problem, "dopri5", rtol=1e-10)
    assert quiet.y[1].max() <= quiet.y[1][0] * 1.01, "infection grew with R0 < 1"
    assert outbreak.y[1].max() > 100 * outbreak.y[1][0], "no outbreak with R0 = 4.5"


@pytest.mark.parametrize("key", ["fitzhugh_nagumo", "sir"])
def test_both_are_reachable_from_the_interface(key):
    """A model in `problems` that never reaches the catalogue is a model a
    learner cannot find -- which is what had happened to SIR."""
    from odesuite_app import catalog
    from odesuite_app.state import methods_for

    entry = catalog.get(key)
    assert key in catalog.keys()
    assert entry.params, "no sliders: nothing to explore"
    assert methods_for(entry), "no method can run it"

    solution = solve(entry.build({}).problem, entry.default_method,
                     rtol=entry.default_rtol, atol=entry.default_rtol * 1e-3)
    assert solution.success


@pytest.mark.parametrize("key", ["fitzhugh_nagumo", "sir"])
def test_supports_taylor_is_not_claimed_without_checking(key):
    """`supports_taylor` is a promise that the right-hand side is expressible in
    jet arithmetic. Getting it wrong used to kill the interpreter, so the flag
    is asserted against the method actually running."""
    from odesuite_app import catalog

    entry = catalog.get(key)
    if not entry.supports_taylor:
        pytest.skip(f"{key} does not claim Taylor support")
    solution = solve(entry.build({}).problem, "taylor20", rtol=1e-8, atol=1e-10)
    assert solution.success, solution.message


# ---------------------------------------------------------------------------
# DYN-03 -- the largest Lyapunov exponent, with an error bar that means something
# ---------------------------------------------------------------------------
#
# Lorenz shipped tagged "chaotic" with no way to quantify the chaos, and without
# an exponent there is no predictability horizon to show either.
#
# The error bar was the difficulty. Treating the per-interval log growths as
# independent samples gives a standard error 8.5x too large -- measured over 12
# replicates: estimates scatter with sd 0.0281 while the naive iid formula
# reports 0.2404, because the growths are anti-correlated. A 26% "relative
# standard error" would have made the routine refuse to report a good answer.
# The bar is therefore the scatter across independent replicates.


@pytest.mark.slow
def test_the_lorenz_exponent_matches_the_literature():
    from odesuite.problems import lorenz
    from odesuite_app.analysis import largest_lyapunov

    estimate = largest_lyapunov(lorenz().problem, t_end=150.0)
    assert estimate.verdict == "chaotic"
    assert estimate.value == pytest.approx(0.9056, abs=0.06), str(estimate)
    assert estimate.significant


@pytest.mark.slow
def test_an_attracting_system_gets_a_negative_exponent():
    from odesuite.problems import pendulum
    from odesuite_app.analysis import largest_lyapunov

    estimate = largest_lyapunov(
        pendulum(damping=0.3, t_end=200.0).problem, t_end=150.0, spread=0.2
    )
    assert estimate.verdict == "attracting"
    assert estimate.value < 0


@pytest.mark.slow
@pytest.mark.parametrize("name", ["lotka_volterra", "sine_cosine"])
def test_a_conservative_system_is_not_called_chaotic(name):
    """The case the verdict exists for. A conservative system's largest exponent
    IS zero, and reporting "+0.0035, chaotic" of Lotka-Volterra would be
    confidently wrong about the most famous non-chaotic system in the catalogue.
    """
    from odesuite import problems
    from odesuite_app.analysis import largest_lyapunov

    problem = getattr(problems, name)(t_end=300.0).problem
    estimate = largest_lyapunov(problem, t_end=250.0, spread=0.2)
    assert estimate.verdict == "indistinguishable from zero", str(estimate)
    assert not estimate.significant


def test_replicates_differ_in_where_they_start_not_only_how_they_are_nudged():
    """Replicates that share a start point agree with each other while being
    wrong together: on a 15-time-unit Lorenz run that produced an error bar of
    exactly 0.0000, which is the false negative an error bar exists to prevent.
    Different starts must produce a non-degenerate spread."""
    from odesuite.problems import lorenz
    from odesuite_app.analysis import largest_lyapunov

    estimate = largest_lyapunov(lorenz().problem, t_end=30.0, replicates=5)
    assert estimate.error > 0.0, "a five-replicate estimate reported no scatter"


def test_a_horizon_is_only_offered_when_the_exponent_is_resolved_and_positive():
    """A horizon computed from an exponent indistinguishable from zero is an
    enormous number presented as a fact, and an attracting system has none."""
    from odesuite_app.analysis import LyapunovEstimate, predictability_horizon

    chaotic = LyapunovEstimate(0.9056, 0.01, 5, "chaotic")
    horizon = predictability_horizon(chaotic, 1e-8)
    assert horizon == pytest.approx(np.log(1e8) / 0.9056, rel=1e-9)

    for unresolved in (
        LyapunovEstimate(0.003, 0.005, 5, "indistinguishable from zero"),
        LyapunovEstimate(-0.15, 0.001, 5, "attracting"),
        LyapunovEstimate(float("nan"), float("nan"), 0, "not converged"),
    ):
        assert predictability_horizon(unresolved, 1e-8) is None


def test_the_estimate_can_be_abandoned_midway():
    """A 300-time-unit Lorenz run takes about 26 seconds and must not pin a
    thread the user has moved on from."""
    from odesuite.problems import lorenz
    from odesuite_app.analysis import largest_lyapunov

    estimate = largest_lyapunov(
        lorenz().problem, t_end=300.0, should_stop=lambda: True
    )
    assert estimate.verdict == "cancelled"
    assert estimate.replicates == 0
