"""The adaptive integration loop: accuracy, output control, and bookkeeping."""

from __future__ import annotations

import numpy as np
import pytest
from scipy.integrate import solve_ivp as scipy_solve_ivp

from odesuite import ODEProblem, solve
from odesuite.problems import (
    exponential_decay,
    linear_system,
    logistic,
    lotka_volterra,
    sine_cosine,
    van_der_pol,
)
from odesuite.tableaux import TABLEAUX

METHOD_NAMES = sorted({tab.name.lower(): key for key, tab in TABLEAUX.items()}.values())
ANALYTIC_FACTORIES = (exponential_decay, linear_system, sine_cosine, logistic)


# ---------------------------------------------------------------------------
# Accuracy
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", METHOD_NAMES)
@pytest.mark.parametrize("factory", ANALYTIC_FACTORIES, ids=lambda f: f.__name__)
def test_adaptive_solve_matches_exact(method, factory):
    """The adaptive solve lands on the analytic answer at the requested tolerance."""
    bench = factory()
    sol = solve(bench.problem, method=method, rtol=1e-9, atol=1e-12)

    assert sol.success, sol.message
    assert sol.t[-1] == pytest.approx(bench.problem.tf, abs=1e-13)

    err = np.linalg.norm(sol.y[:, -1] - bench.exact_at_end())
    assert err < 1e-7, f"{method} on {bench.name}: endpoint error {err:.3e}"


@pytest.mark.parametrize("method", METHOD_NAMES)
def test_accuracy_tracks_tolerance(method):
    """Tightening rtol by 100x must actually improve the answer.

    This is the adaptive counterpart to the fixed-step order tests: it verifies
    the controller and error norm are wired together correctly, which the
    fixed-step tests deliberately bypass.
    """
    bench = sine_cosine()
    exact = bench.exact_at_end()

    errors = []
    for rtol in (1e-4, 1e-6, 1e-8, 1e-10):
        sol = solve(bench.problem, method=method, rtol=rtol, atol=rtol * 1e-3)
        errors.append(np.linalg.norm(sol.y[:, -1] - exact))

    for coarse, fine in zip(errors, errors[1:]):
        assert fine < coarse * 1.5, f"{method}: error did not improve: {errors}"
    assert errors[-1] < errors[0] * 1e-3, (
        f"{method}: six decades of tolerance bought less than three of accuracy: "
        f"{['%.2e' % e for e in errors]}"
    )


@pytest.mark.parametrize("method", METHOD_NAMES)
def test_agrees_with_scipy(method):
    """Cross-validation against an independent implementation.

    Used as an oracle only; the order tests are what establish correctness
    independently, so that the suite is not merely reproducing scipy.
    """
    bench = lotka_volterra()
    ours = solve(bench.problem, method=method, rtol=1e-10, atol=1e-12)
    theirs = scipy_solve_ivp(
        lambda t, y: bench.problem.f(t, y),
        (bench.problem.t0, bench.problem.tf),
        bench.problem.y0,
        method="DOP853",
        rtol=1e-12,
        atol=1e-14,
    )
    assert np.allclose(ours.y[:, -1], theirs.y[:, -1], rtol=1e-6, atol=1e-8), (
        f"{method}: {ours.y[:, -1]} vs scipy {theirs.y[:, -1]}"
    )


# ---------------------------------------------------------------------------
# Output control
# ---------------------------------------------------------------------------


def test_t_eval_returns_exactly_requested_times():
    bench = sine_cosine()
    t_eval = np.linspace(0.0, bench.problem.tf, 37)
    sol = solve(bench.problem, t_eval=t_eval, rtol=1e-10, atol=1e-12)

    assert np.array_equal(sol.t, t_eval)
    assert sol.y.shape == (2, 37)
    assert np.allclose(sol.y, bench.exact(t_eval), atol=1e-8)


def test_t_eval_subset_of_interval():
    """`t_eval` need not span the whole interval."""
    bench = sine_cosine()
    t_eval = np.array([1.0, 2.5, 4.0])
    sol = solve(bench.problem, t_eval=t_eval, rtol=1e-10, atol=1e-12)
    assert np.array_equal(sol.t, t_eval)
    assert np.allclose(sol.y, bench.exact(t_eval), atol=1e-8)


def test_t_eval_unsorted_is_sorted():
    bench = sine_cosine()
    sol = solve(bench.problem, t_eval=[3.0, 1.0, 2.0], rtol=1e-10)
    assert np.array_equal(sol.t, [1.0, 2.0, 3.0])


def test_t_eval_outside_span_raises():
    bench = sine_cosine()
    with pytest.raises(ValueError, match="within t_span"):
        solve(bench.problem, t_eval=[0.0, 99.0])


def test_step_output_without_t_eval():
    """Without `t_eval` the output is the accepted step points, starting at t0."""
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-6)
    assert sol.t[0] == bench.problem.t0
    assert sol.t[-1] == pytest.approx(bench.problem.tf)
    assert sol.t.size == sol.stats.naccepted + 1
    assert np.all(np.diff(sol.t) > 0)


# ---------------------------------------------------------------------------
# Direction
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", METHOD_NAMES)
def test_backward_integration(method):
    """Integrating from tf back to t0 recovers the initial condition.

    Required in its own right and a prerequisite for adjoint sensitivities, and
    an easy place to leave a sign error that forward-only tests never catch.
    """
    bench = sine_cosine()
    forward = solve(bench.problem, method=method, rtol=1e-11, atol=1e-13)

    back = ODEProblem(
        f=bench.problem.f_user,
        t_span=(bench.problem.tf, bench.problem.t0),
        y0=forward.y[:, -1],
    )
    reverse = solve(back, method=method, rtol=1e-11, atol=1e-13)

    assert reverse.t[-1] == pytest.approx(bench.problem.t0, abs=1e-12)
    assert np.allclose(reverse.y[:, -1], bench.problem.y0, atol=1e-7), (
        f"{method}: round trip gave {reverse.y[:, -1]}, expected {bench.problem.y0}"
    )


def test_backward_integration_with_t_eval():
    bench = sine_cosine()
    back = ODEProblem(f=bench.problem.f_user, t_span=(6.0, 0.0), y0=bench.exact(6.0))
    t_eval = [5.0, 3.0, 1.0]
    sol = solve(back, t_eval=t_eval, rtol=1e-10, atol=1e-13)

    # Output follows the integration direction.
    assert np.array_equal(sol.t, [5.0, 3.0, 1.0])
    assert np.allclose(sol.y, bench.exact(np.array(t_eval)), atol=1e-7)


# ---------------------------------------------------------------------------
# Step-size machinery
# ---------------------------------------------------------------------------


def test_max_step_is_respected():
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-3, max_step=0.1)
    assert np.all(np.diff(sol.t) <= 0.1 + 1e-12)


def test_first_step_is_respected():
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-6, first_step=0.01)
    assert sol.t[1] - sol.t[0] == pytest.approx(0.01)


def test_automatic_first_step_is_sane():
    """The Hairer heuristic must not propose something absurd.

    A first step that is orders of magnitude too large wastes rejections; one
    that is too small wastes hundreds of steps ramping up.
    """
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-6)
    first = sol.t[1] - sol.t[0]
    assert 1e-4 < first < 1.0, f"implausible automatic first step {first:g}"
    assert sol.stats.nrejected <= 2, (
        f"{sol.stats.nrejected} rejections suggests a poor starting step"
    )


def test_loose_tolerance_uses_fewer_steps():
    bench = lotka_volterra()
    loose = solve(bench.problem, rtol=1e-3, atol=1e-6)
    tight = solve(bench.problem, rtol=1e-10, atol=1e-12)
    assert loose.stats.naccepted < tight.stats.naccepted


def test_pi_controller_rejects_less_than_i_controller():
    """The PI controller's damping is the reason it is the default."""
    bench = lotka_volterra()
    pi = solve(bench.problem, rtol=1e-8, atol=1e-10, controller="pi")
    i = solve(bench.problem, rtol=1e-8, atol=1e-10, controller="i")
    assert pi.stats.nrejected <= i.stats.nrejected


def test_max_steps_guard():
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-12, atol=1e-14, max_steps=5)
    assert sol.status == "failed"
    assert "max_steps" in sol.message
    assert not sol.success


def test_min_step_guard():
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-13, atol=1e-16, min_step=0.5)
    assert sol.status == "failed"
    assert "min_step" in sol.message


# ---------------------------------------------------------------------------
# Bookkeeping
# ---------------------------------------------------------------------------


def test_rejected_steps_are_recorded():
    """Where the controller misjudged, not just how often.

    The accepted step points say where the solver ended up; the rejections say
    where it struggled. They are what the interface marks on the step-size
    timeline, so they have to carry a time and a step size, not just a count.
    """
    bench = van_der_pol(mu=200.0)
    sol = solve(bench.problem, method="radau", rtol=1e-9, atol=1e-11)

    assert sol.rejected.ndim == 2 and sol.rejected.shape[1] == 2
    assert sol.rejected.shape[0] == sol.stats.nrejected
    if sol.rejected.size:
        times, steps = sol.rejected[:, 0], sol.rejected[:, 1]
        assert np.all(steps > 0)
        lo, hi = sorted((bench.problem.t0, bench.problem.tf))
        assert np.all((times >= lo) & (times <= hi))


def test_no_rejections_gives_an_empty_array():
    """The attribute is always an array, never None -- callers need not guard."""
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-4, atol=1e-6)
    assert isinstance(sol.rejected, np.ndarray)
    assert sol.rejected.shape == (sol.stats.nrejected, 2)


def test_stats_are_consistent():
    bench = lotka_volterra()
    sol = solve(bench.problem, rtol=1e-8, atol=1e-10)
    s = sol.stats
    assert s.nsteps == s.naccepted + s.nrejected
    assert s.nfev > s.nsteps
    assert s.runtime > 0
    assert 0.0 <= s.reject_ratio < 1.0


@pytest.mark.parametrize("method", METHOD_NAMES)
def test_fsal_saves_an_evaluation(method):
    """An FSAL method must cost one fewer RHS evaluation per step than its stages.

    Verifies the driver actually reuses the final stage rather than silently
    recomputing it, which would be invisible in any accuracy test.
    """
    bench = sine_cosine()
    sol = solve(bench.problem, method=method, rtol=1e-8, atol=1e-10)
    tab = TABLEAUX[method]
    s = tab.n_stages

    # 2 evaluations of startup overhead (initial f, first-step probe).
    per_step = (sol.stats.nfev - 2) / sol.stats.nsteps
    expected = (s - 1) if tab.fsal else s
    assert per_step == pytest.approx(expected, abs=0.35), (
        f"{tab.name}: {per_step:.2f} evaluations per step, expected ~{expected} "
        f"({'FSAL' if tab.fsal else 'non-FSAL'})"
    )


def test_solution_repr_and_properties():
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-6, dense_output=True)
    assert sol.n == 2
    assert sol.success
    assert "Solution" in repr(sol)
    assert "nfev" in str(sol.stats)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


def test_unknown_method_raises():
    with pytest.raises(KeyError, match="unknown method"):
        solve(sine_cosine().problem, method="not_a_method")


def test_bad_atol_length_raises():
    with pytest.raises(ValueError, match="atol vector"):
        solve(sine_cosine().problem, atol=[1e-6, 1e-6, 1e-6])


def test_vector_atol_is_accepted():
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-8, atol=np.array([1e-10, 1e-12]))
    assert sol.success


def test_negative_rtol_raises():
    with pytest.raises(ValueError, match="rtol must be positive"):
        solve(sine_cosine().problem, rtol=-1.0)


def test_mass_matrix_rejected_by_explicit_methods():
    """Explicit methods must refuse a mass matrix rather than silently ignore it."""
    prob = ODEProblem(
        f=lambda t, y: -y, t_span=(0, 1), y0=[1.0], mass=np.array([[2.0]])
    )
    with pytest.raises(ValueError, match="mass matrix"):
        solve(prob, method="dopri5")


def test_bad_rhs_shape_raises():
    with pytest.raises(ValueError, match="f returned shape"):
        ODEProblem(f=lambda t, y: np.array([1.0, 2.0]), t_span=(0, 1), y0=[1.0])


def test_degenerate_t_span_raises():
    with pytest.raises(ValueError, match="endpoints must differ"):
        ODEProblem(f=lambda t, y: -y, t_span=(1.0, 1.0), y0=[1.0])


def test_args_are_threaded_through():
    prob = ODEProblem(
        f=lambda t, y, k: -k * y, t_span=(0.0, 2.0), y0=[1.0], args=(3.0,)
    )
    sol = solve(prob, rtol=1e-10, atol=1e-12)
    assert sol.y[0, -1] == pytest.approx(np.exp(-6.0), rel=1e-7)
