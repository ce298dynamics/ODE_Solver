"""Step-size control, tested directly rather than through a solve.

Every other test in this suite exercises the controller *indirectly*: a solve
lands on the right answer, so the controller must have been roughly sane. That
is exactly the kind of evidence this project has already been burned by. The
recorded ROS3P bug was an error estimator that was identically zero -- every
accuracy test passed while the controller ran blind on a constant input.

So these tests check the controller's arithmetic against the formulas it claims
to implement, and its state machine against the rules it documents, with no
integration involved.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import solve
from odesuite.controllers import (
    Controller,
    IController,
    PIController,
    PredictiveController,
    error_norm,
    initial_step_size,
    make_controller,
)
from odesuite.problems import exponential_decay, lotka_volterra, sine_cosine

# ---------------------------------------------------------------------------
# error_norm
# ---------------------------------------------------------------------------


def test_error_exactly_at_tolerance_normalises_to_one():
    """1.0 is the accept/reject boundary, so it has to mean what it says."""
    y = np.array([1.0, 1.0])
    atol, rtol = 0.0, 1e-6
    err = rtol * np.abs(y)          # exactly the permitted error
    assert error_norm(err, y, y, rtol, atol) == pytest.approx(1.0)


def test_scale_uses_the_larger_of_the_two_endpoints():
    """``scale = atol + rtol*max(|y_old|, |y_new|)`` -- the max, not either one.

    Using only `y_old` would judge a step that grows the solution too harshly,
    and only `y_new` too leniently on a decaying one.
    """
    err = np.array([1.0])
    small, large = np.array([1.0]), np.array([100.0])
    assert error_norm(err, small, large, 1e-3, 0.0) == pytest.approx(
        error_norm(err, large, small, 1e-3, 0.0)
    )
    # and it is the large one that sets the scale
    assert error_norm(err, small, large, 1e-3, 0.0) == pytest.approx(1.0 / (1e-3 * 100))


def test_norm_is_rms_not_maximum():
    """The RMS choice is deliberate: one bad component must not dominate a
    large system's step size. A max norm would return 1.0 here, RMS returns
    1/sqrt(n)."""
    n = 100
    err = np.zeros(n)
    err[0] = 1.0
    y = np.ones(n)
    assert error_norm(err, y, y, 1.0, 0.0) == pytest.approx(1.0 / np.sqrt(n))


def test_atol_may_be_a_vector():
    err = np.array([1.0, 1.0])
    y = np.zeros(2)
    atol = np.array([1.0, 0.5])
    assert error_norm(err, y, y, 0.0, atol) == pytest.approx(
        np.sqrt(np.mean([1.0**2, 2.0**2]))
    )


def test_a_zero_error_estimate_normalises_to_zero():
    """The degenerate case the ROS3P bug produced. It must reach the controller
    as 0.0 so that `update` can recognise it, not as a small positive number."""
    y = np.ones(3)
    assert error_norm(np.zeros(3), y, y, 1e-6, 1e-9) == 0.0


# ---------------------------------------------------------------------------
# initial_step_size
# ---------------------------------------------------------------------------


def test_initial_step_is_scaled_to_the_problem_not_the_interval():
    """The whole point of the two-stage estimate: `h0` follows the solution's own
    timescale, and monotonically so.

    The dependence is deliberately *sub-linear* -- `h1` is an order-(p+1) root of
    the curvature estimate, so a 1000x faster problem gets a step roughly 46x
    smaller, not 1000x. That is the correct behaviour and worth pinning: the
    estimate is a starting guess for an adaptive controller, not a converged
    answer, and rooting it is what stops one stiff component from driving the
    first step to zero.
    """
    steps = [
        initial_step_size(
            lambda t, y, l=lam: -l * y, 0.0, np.array([1.0]), np.array([-lam]),
            5, 1.0, 1e-6, np.asarray(1e-9),
        )
        for lam in (1.0, 10.0, 1000.0)
    ]
    assert steps[0] > steps[1] > steps[2], f"not monotone in the timescale: {steps}"
    assert steps[2] < steps[0] / 10, (
        f"a 1000x faster problem got a step only {steps[0] / steps[2]:.3g}x smaller"
    )


def test_initial_step_respects_max_step():
    h = initial_step_size(
        lambda t, y: -y, 0.0, np.array([1.0]), np.array([-1.0]),
        5, 1.0, 1e-6, np.asarray(1e-9), max_step=1e-4,
    )
    assert h <= 1e-4


def test_initial_step_survives_a_stationary_start():
    """``y' = 0`` at t0 makes both `d0` and `d1` degenerate. The documented
    fallback must fire instead of dividing by zero."""
    h = initial_step_size(
        lambda t, y: np.zeros_like(y), 0.0, np.zeros(2), np.zeros(2),
        5, 1.0, 1e-6, np.asarray(1e-9),
    )
    assert np.isfinite(h) and h > 0


def test_initial_step_follows_the_integration_direction():
    """Backward integration probes backwards; the returned magnitude is positive
    either way because the driver applies the sign."""
    forward = initial_step_size(
        lambda t, y: -y, 0.0, np.array([1.0]), np.array([-1.0]),
        5, 1.0, 1e-6, np.asarray(1e-9),
    )
    backward = initial_step_size(
        lambda t, y: -y, 0.0, np.array([1.0]), np.array([-1.0]),
        5, -1.0, 1e-6, np.asarray(1e-9),
    )
    assert forward > 0 and backward > 0


# ---------------------------------------------------------------------------
# The controller formulas
# ---------------------------------------------------------------------------


def test_exponent_comes_from_the_embedded_order_not_the_propagated_one():
    """``k = error_order + 1``. Getting this wrong makes every step-size decision
    subtly wrong in a way no accuracy test would catch -- the solve still
    converges, just inefficiently."""
    c = IController(error_order=4)
    assert c.k == 5
    assert c.exponent == pytest.approx(1.0 / 5)


def test_i_controller_matches_its_documented_formula():
    c = IController(error_order=4)
    err = 0.5
    assert c._factor(err) == pytest.approx(c.safety * err ** (-1.0 / 5))


def test_pi_controller_matches_its_documented_formula():
    c = PIController(error_order=4)
    c.update(0.25, accepted=True)          # sets err_prev
    err = 0.5
    alpha, beta = 0.7 / 5, 0.4 / 5
    expected = c.safety * err ** (-alpha) * c.err_prev**beta
    assert c._factor(err) == pytest.approx(expected)


def test_pi_controller_ignores_history_on_its_very_first_step():
    """With no previous error there is no PI term, and the controller must
    degrade to the I formula rather than to a NaN."""
    c = PIController(error_order=4)
    assert c.err_prev is None
    assert c._factor(0.5) == pytest.approx(c.safety * 0.5 ** (-0.7 / 5))


def test_factor_is_clamped_both_ways():
    """The clamps are what stop a single freak error estimate from throwing the
    step size across many orders of magnitude."""
    c = IController(error_order=4)
    assert c.update(1e-30, accepted=True) == pytest.approx(c.max_factor)
    assert c.update(1e30, accepted=False) == pytest.approx(c.min_factor)


def test_a_zero_error_asks_for_the_largest_permitted_growth():
    c = PIController(error_order=4)
    assert c.update(0.0, accepted=True) == c.max_factor


def test_a_rejected_step_can_only_shrink():
    """A rejected step whose formula suggests growth must still shrink, or the
    controller can loop forever re-proposing a step it just refused."""
    c = PIController(error_order=4)
    factor = c.update(0.99, accepted=False)      # err < 1 but rejected
    assert factor <= 1.0


def test_a_rejection_does_not_enter_the_pi_history():
    """Documented at controllers.py: feeding a rejected step's error into the PI
    term makes the controller oscillate."""
    c = PIController(error_order=4)
    c.update(0.5, accepted=True)
    remembered = c.err_prev
    c.update(0.9, accepted=False)
    assert c.err_prev == remembered


def test_accepted_error_history_is_floored():
    """The floor damps the derivative term; without it a near-zero error makes
    the PI factor explode on the following step."""
    c = PIController(error_order=4)
    c.update(1e-20, accepted=True)
    assert c.err_prev == 1e-4


def test_unknown_controller_option_is_rejected():
    """A typo'd option must not be silently attached as a new attribute."""
    with pytest.raises(TypeError, match="unknown controller option"):
        PIController(error_order=4, saftey=0.8)


def test_controller_options_reach_the_controller():
    c = PIController(error_order=4, safety=0.5)
    assert c.safety == 0.5


def test_reset_clears_the_error_history():
    c = PIController(error_order=4)
    c.update(0.5, accepted=True)
    assert c.err_prev is not None
    c.reset()
    assert c.err_prev is None


# ---------------------------------------------------------------------------
# make_controller
# ---------------------------------------------------------------------------


def test_make_controller_accepts_name_class_and_instance():
    assert isinstance(make_controller("pi", 4), PIController)
    assert isinstance(make_controller("i", 4), IController)
    assert isinstance(make_controller(IController, 4), IController)
    instance = PIController(4)
    assert make_controller(instance, 4) is instance


def test_make_controller_rejects_an_unknown_name():
    with pytest.raises(KeyError, match="unknown controller"):
        make_controller("pid", 4)


# ---------------------------------------------------------------------------
# State must not survive a solve
# ---------------------------------------------------------------------------


def test_a_reused_controller_gives_bit_identical_repeat_solves():
    """The same problem, solved twice with the same controller object, must give
    the same answer.

    `make_controller` returns a caller-supplied instance unchanged, so its
    `err_prev` from the end of one solve became the PI history for the *first*
    step of the next -- and the first step of a solve has no history by
    definition. Measured before the fix: 90 steps then 91, on identical input.
    """
    bench = exponential_decay()
    controller = PIController(error_order=4)

    first = solve(bench.problem, "dopri5", rtol=1e-8, atol=1e-10, controller=controller)
    second = solve(bench.problem, "dopri5", rtol=1e-8, atol=1e-10, controller=controller)

    assert second.stats.naccepted == first.stats.naccepted, (
        f"repeat solve took {second.stats.naccepted} steps against "
        f"{first.stats.naccepted}: controller state leaked across solves"
    )
    assert second.stats.nfev == first.stats.nfev
    np.testing.assert_array_equal(first.t, second.t)
    np.testing.assert_array_equal(first.y, second.y)


def test_a_reused_controller_is_reset_even_after_a_failed_solve():
    """A solve that aborts leaves the controller mid-recovery, with a history
    reflecting a step that was going badly. The next solve must not inherit it."""
    controller = PIController(error_order=4)
    bench = sine_cosine()

    failed = solve(bench.problem, rtol=1e-13, atol=1e-16, min_step=0.5,
                   controller=controller)
    assert failed.status == "failed"

    clean = solve(bench.problem, "dopri5", rtol=1e-8, atol=1e-10, controller=controller)
    reference = solve(bench.problem, "dopri5", rtol=1e-8, atol=1e-10,
                      controller=PIController(error_order=4))
    assert clean.stats.naccepted == reference.stats.naccepted
    np.testing.assert_array_equal(clean.y, reference.y)


def test_a_fresh_controller_instance_matches_the_string_spelling():
    """`controller="pi"` and `controller=PIController(...)` must be the same
    thing; if they are not, one of the two paths is mis-wired."""
    bench = lotka_volterra()
    by_name = solve(bench.problem, rtol=1e-8, atol=1e-10, controller="pi")
    by_instance = solve(bench.problem, rtol=1e-8, atol=1e-10,
                        controller=PIController(error_order=4))
    np.testing.assert_array_equal(by_name.y, by_instance.y)


def test_a_custom_controller_subclass_drives_a_real_solve():
    """The Controller ABC is public API; a user-written controller must work
    without touching the library."""

    class Fixed(Controller):
        """Never changes the step size; accepts whatever the error says."""

        def _factor(self, err: float) -> float:
            return 1.0

    bench = exponential_decay()
    sol = solve(bench.problem, "dopri5", rtol=1e-6, atol=1e-9,
                controller=Fixed(error_order=4))
    assert sol.success
    steps = np.diff(sol.t)
    assert np.allclose(steps[:-1], steps[0], rtol=1e-9), "step size should be constant"


# ---------------------------------------------------------------------------
# PredictiveController
# ---------------------------------------------------------------------------
#
# The controller for methods where changing h costs a factorisation. Two
# behaviours to pin: Gustafsson's predictive term, and the refusal to make small
# increases at all.


def _predictive(**kwargs):
    # error_order 3 -> k = 4, exponent = 1/4, matching Radau and RODAS4.
    return PredictiveController(error_order=3, **kwargs)


def test_a_small_proposed_increase_is_declined_outright():
    """The economic rule. ``0.9 * 0.448^-0.25`` is 1.1, a 10% increase -- worth
    less than the O(n^3) refactorisation that changing h would force."""
    c = _predictive()
    assert c._factor(0.448) == pytest.approx(1.1, abs=1e-3)
    assert c.update(0.448, accepted=True, h=0.1) == 1.0


def test_the_frozen_step_is_bit_for_bit_the_same():
    """Not merely close: the stepper reuses its factorisation only if `h` is
    unchanged, so the factor has to be exactly 1.0."""
    c = _predictive()
    factor = c.update(0.448, accepted=True, h=0.1)
    assert factor == 1.0
    assert 0.1 * factor == 0.1


def test_a_large_proposed_increase_is_allowed_through():
    """The freeze is a threshold, not a ceiling: when the step really can grow,
    it must."""
    c = _predictive()
    factor = c.update(0.1, accepted=True, h=0.1)
    assert factor > c.freeze_below
    assert factor == pytest.approx(0.9 * 0.1 ** -0.25)


def test_a_shrink_is_never_frozen():
    """Only *increases* are declined. Freezing a shrink would keep a step the
    controller has just judged too large."""
    c = _predictive()
    factor = c.update(2.0, accepted=True, h=0.1)
    assert factor < 1.0


def test_a_rejected_step_does_not_become_the_reference():
    """`h_acc` and `err_acc` are the last *accepted* step; a rejection must not
    poison the prediction."""
    c = _predictive()
    c.update(0.5, accepted=True, h=0.1)
    h_acc, err_acc = c.h_acc, c.err_acc
    c.update(4.0, accepted=False, h=0.1)
    assert (c.h_acc, c.err_acc) == (h_acc, err_acc)


def test_the_predictive_term_can_only_make_the_controller_more_cautious():
    """The smaller of the classical and predicted factors is taken, so the
    prediction can restrain an increase but never inflate one."""
    c = _predictive()
    c.update(0.5, accepted=True, h=0.1)          # establishes the reference
    classical = c._factor(0.05)
    # A step that grew a lot while the error barely improved: the trend says be
    # careful even though the current error alone says accelerate.
    factor = c.update(0.05, accepted=True, h=1.0)
    assert factor <= classical + 1e-12


def test_the_error_reference_is_floored():
    """An essentially-zero error would otherwise make the next predicted factor
    enormous on the strength of one lucky step. radau5.f floors it at 1e-2."""
    c = _predictive()
    c.update(1e-12, accepted=True, h=0.1)
    assert c.err_acc == 1e-2


def test_growth_and_shrink_are_bounded():
    c = _predictive()
    assert c.update(1e-30, accepted=True, h=0.1) == pytest.approx(c.max_factor)
    assert c.update(1e30, accepted=False, h=0.1) == pytest.approx(c.min_factor)


def test_reset_clears_the_prediction_reference():
    c = _predictive()
    c.update(0.5, accepted=True, h=0.1)
    assert c.h_acc is not None
    c.reset()
    assert c.h_acc is None and c.err_acc is None


def test_without_a_step_size_it_degrades_to_the_classical_factor():
    """`h` is optional on the base signature, so a caller that does not supply
    one must still get sensible control rather than an exception."""
    c = _predictive()
    factor = c.update(0.1, accepted=True)
    assert factor == pytest.approx(0.9 * 0.1 ** -0.25)
    assert c.h_acc is None


# ---------------------------------------------------------------------------
# The method picks its own controller
# ---------------------------------------------------------------------------


def test_implicit_methods_default_to_the_predictive_controller():
    from odesuite.steppers import make_stepper

    assert make_stepper("radau").default_controller == "predictive"
    assert make_stepper("rodas4").default_controller == "predictive"
    assert make_stepper("dopri5").default_controller == "pi"


def test_the_predictive_default_costs_radau_less_work_than_pi():
    """The claim the change was made for, on the problem it was made for."""
    from odesuite.problems import robertson

    default = solve(robertson().problem, "radau", rtol=1e-8, atol=1e-10)
    with_pi = solve(robertson().problem, "radau", rtol=1e-8, atol=1e-10,
                    controller="pi")

    assert default.success and with_pi.success
    assert default.stats.nfev < with_pi.stats.nfev, (
        f"predictive {default.stats.nfev} nfev vs pi {with_pi.stats.nfev}"
    )
    assert default.stats.naccepted < with_pi.stats.naccepted


def test_naming_a_controller_still_overrides_the_method_default():
    from odesuite.problems import robertson

    forced = solve(robertson().problem, "radau", rtol=1e-6, atol=1e-9,
                   controller="i")
    assert forced.success


def test_explicit_methods_are_unaffected_by_the_new_default():
    """dopri5 must still be driven by the PI controller, bit for bit."""
    bench = lotka_volterra()
    default = solve(bench.problem, "dopri5", rtol=1e-8, atol=1e-10)
    forced = solve(bench.problem, "dopri5", rtol=1e-8, atol=1e-10, controller="pi")
    np.testing.assert_array_equal(default.y, forced.y)


# ---------------------------------------------------------------------------
# The predictive default with a differenced Jacobian
# ---------------------------------------------------------------------------
#
# The Tier 2 measurements that made this the default all used problems that
# supply an analytic Jacobian, which is not how most people call a stiff solver.
# Differenced, the error estimate is noisier and the nonlinear solve more
# fragile, and an undamped controller can push the step into Newton failures.
# These tests exist because that gap was found by accident rather than by
# measurement, and should not be able to reopen unnoticed.


def _without_jacobian(bench):
    from odesuite import ODEProblem

    p = bench.problem
    return ODEProblem(f=p.f_user, t_span=(p.t0, p.tf), y0=p.y0)


@pytest.mark.slow
@pytest.mark.parametrize("factory_name", ["hires", "van_der_pol"])
def test_the_predictive_default_also_wins_with_a_differenced_jacobian(factory_name):
    from odesuite import problems

    problem = _without_jacobian(getattr(problems, factory_name)())
    predictive = solve(problem, "radau", rtol=1e-8, atol=1e-10)
    with_pi = solve(problem, "radau", rtol=1e-8, atol=1e-10, controller="pi")

    assert predictive.success and with_pi.success
    assert predictive.stats.nfev <= with_pi.stats.nfev * 1.05, (
        f"{factory_name} without an analytic Jacobian: predictive "
        f"{predictive.stats.nfev} nfev vs pi {with_pi.stats.nfev}"
    )


@pytest.mark.slow
def test_robertson_without_a_jacobian_is_the_documented_exception():
    """The one measured case where the predictive default loses, pinned so the
    docstring's claim stays true and an improvement would be noticed.

    The asymmetry is the point: differenced, predictive costs about twice PI;
    supplied, it beats PI. Robertson's finite-difference Jacobian is poor -- one
    component sits near 1e-8 while entries of J reach 3e7 -- so this is a
    statement about the Jacobian, not about the controller.
    """
    from odesuite.problems import robertson

    bench = robertson()

    differenced = _without_jacobian(bench)
    fd_pred = solve(differenced, "radau", rtol=1e-8, atol=1e-10)
    fd_pi = solve(differenced, "radau", rtol=1e-8, atol=1e-10, controller="pi")
    assert fd_pred.stats.nfev > fd_pi.stats.nfev, (
        "Robertson without a Jacobian used to be the predictive controller's "
        "weak case; if this now passes, update the docstring table"
    )

    # Supplying the Jacobian -- what the catalogue entry does -- reverses it.
    supplied_pred = solve(bench.problem, "radau", rtol=1e-8, atol=1e-10)
    supplied_pi = solve(bench.problem, "radau", rtol=1e-8, atol=1e-10, controller="pi")
    assert supplied_pred.stats.nfev < supplied_pi.stats.nfev
