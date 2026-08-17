"""The stiff solvers: order, error estimates, and the Phase 2 acceptance problems.

The order machinery is shared with `test_convergence.py`; the implicit methods
hit exactly the same pre-asymptotic behaviour the explicit ones do, so the same
self-terminating sweep is reused rather than reinvented.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.integrate import solve_ivp as scipy_solve_ivp

from odesuite import ODEProblem, make_stepper, solve
from odesuite.problems import (
    exponential_decay,
    linear_system,
    logistic,
    lotka_volterra,
    robertson,
    sine_cosine,
    van_der_pol,
)
from odesuite.steppers.rosenbrock import RODAS4

from .test_convergence import ROUNDOFF_FLOOR, asymptotic_order

STIFF_METHODS = ["rodas4", "radau"]
ANALYTIC_FACTORIES = (exponential_decay, linear_system, sine_cosine, logistic)


def implicit_local_error_sweep(stepper, bench, h0: float = 0.5):
    """As `local_error_sweep`, but resetting the stepper's cached Jacobian.

    An implicit stepper carries state between calls -- Jacobian, factorisation,
    the extrapolation history. Measuring a *local* error requires each step to
    start clean, or the previous h leaks into the next measurement.
    """
    problem = bench.problem
    t0 = problem.t0
    y0 = problem.y0.copy()
    f0 = problem.f(t0, y0)

    pairs = []
    for k in range(20):
        h = h0 * 0.5**k
        if hasattr(stepper, "_reset_cache"):
            stepper._reset_cache()
        result = stepper.step(problem, t0, y0, f0, h)
        if not result.ok:
            break
        exact = np.asarray(bench.exact(t0 + h)).reshape(-1)
        err = float(np.linalg.norm(result.y_new - exact))
        if err <= ROUNDOFF_FLOOR:
            break
        pairs.append((h, err))
    return pairs


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", STIFF_METHODS)
@pytest.mark.parametrize("factory", ANALYTIC_FACTORIES, ids=lambda f: f.__name__)
def test_local_error_order(method, factory):
    """Local truncation error scales as ``h^(p+1)``.

    The tolerance is looser than the explicit methods' because a higher-order
    method has a narrower usable window in double precision, and on some
    problems a sign cancellation between consecutive terms of the error
    expansion eats most of it. RODAS4 on `logistic` is the clear case: the
    measured slope runs 7.3, 8.3, 2.7, 4.6, 4.8 as h halves -- the h^5 and h^6
    terms cancel near h = 0.09 -- and the round-off floor arrives before the
    slope has finished climbing back to 5. The method is fine; the measurement
    is what is limited. It reads 4.99, 4.99 and 5.00 on the other three
    problems, and `test_rodas4_consistency_condition` pins the coefficients
    algebraically.
    """
    bench = factory()
    stepper = make_stepper(method)
    stepper.set_tolerances(1e-13, 1e-15)
    expected = stepper.order + 1

    pairs = implicit_local_error_sweep(stepper, bench)
    slope = asymptotic_order(pairs)

    assert slope == pytest.approx(expected, abs=0.5), (
        f"{stepper.name} on {bench.name}: local error order {slope:.3f}, "
        f"expected {expected}. sweep="
        f"{[('%.4g' % h, '%.3e' % e) for h, e in pairs]}"
    )


@pytest.mark.parametrize("method", STIFF_METHODS)
def test_adaptive_accuracy_tracks_tolerance(method):
    bench = sine_cosine()
    exact = bench.exact_at_end()

    errors = []
    for rtol in (1e-4, 1e-6, 1e-8, 1e-10):
        sol = solve(bench.problem, method=method, rtol=rtol, atol=rtol * 1e-3)
        assert sol.success, sol.message
        errors.append(np.linalg.norm(sol.y[:, -1] - exact))

    assert errors[-1] < errors[0] * 1e-3, (
        f"{method}: accuracy did not follow tolerance: "
        f"{['%.2e' % e for e in errors]}"
    )


@pytest.mark.parametrize("method", STIFF_METHODS)
def test_agrees_with_scipy_on_a_nonstiff_problem(method):
    bench = lotka_volterra()
    ours = solve(bench.problem, method=method, rtol=1e-9, atol=1e-11)
    theirs = scipy_solve_ivp(
        lambda t, y: bench.problem.f(t, y),
        (bench.problem.t0, bench.problem.tf),
        bench.problem.y0,
        method="DOP853",
        rtol=1e-12,
        atol=1e-14,
    )
    assert np.allclose(ours.y[:, -1], theirs.y[:, -1], rtol=1e-5, atol=1e-7)


# ---------------------------------------------------------------------------
# The error estimate itself
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", STIFF_METHODS)
def test_error_estimate_is_nondegenerate(method):
    """The error estimate must be non-zero and scale like the true error.

    This test exists because a Rosenbrock pair transcribed into this library had
    an embedded weight vector that annihilated the stage vector exactly,
    producing an estimate of ~1e-17 on every problem. Every accuracy test still
    passed -- the *solution* was fine -- while the adaptive controller was
    accepting every step it was offered. Only a direct check of the estimator
    catches that.
    """
    bench = linear_system()
    stepper = make_stepper(method)
    stepper.set_tolerances(1e-13, 1e-15)
    problem = bench.problem
    t0, y0 = problem.t0, problem.y0.copy()
    f0 = problem.f(t0, y0)

    ratios = []
    for h in (0.2, 0.1, 0.05, 0.025):
        if hasattr(stepper, "_reset_cache"):
            stepper._reset_cache()
        result = stepper.step(problem, t0, y0, f0, h)
        exact = np.asarray(bench.exact(t0 + h)).reshape(-1)
        true_err = np.linalg.norm(result.y_new - exact)

        assert result.error is not None, f"{method} produced no error estimate"
        estimate = np.linalg.norm(result.error)
        assert estimate > 1e-14, (
            f"{method}: error estimate {estimate:.3e} at h={h} is numerically "
            f"zero while the true error is {true_err:.3e} -- the estimator is "
            f"degenerate and the step controller would be blind"
        )
        ratios.append(estimate / true_err)

    # The estimate need not equal the true error, but it must stay within a
    # couple of orders of magnitude of it across the range, or step-size
    # selection is systematically mis-scaled.
    assert max(ratios) / min(ratios) < 1e3, (
        f"{method}: estimate/true ratio wanders over {ratios}"
    )


@pytest.mark.parametrize("method", STIFF_METHODS)
def test_rejections_are_rare_on_a_smooth_problem(method):
    """A working error estimate plus a working controller means few rejections."""
    bench = lotka_volterra()
    sol = solve(bench.problem, method=method, rtol=1e-8, atol=1e-10)
    assert sol.stats.reject_ratio < 0.2, (
        f"{method}: {sol.stats.nrejected}/{sol.stats.nsteps} steps rejected"
    )


# ---------------------------------------------------------------------------
# Phase 2 acceptance problems
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", STIFF_METHODS)
def test_robertson_reaches_1e11(method):
    """The canonical stiff problem, over eleven decades of time."""
    bench = robertson()
    sol = solve(bench.problem, method=method, rtol=1e-6, atol=1e-10)

    assert sol.success, sol.message
    assert sol.t[-1] == pytest.approx(1e11)
    # Mass is conserved by the chemistry: the three species always sum to one.
    assert abs(sol.y[:, -1].sum() - 1.0) < 1e-8
    # Essentially all of species 1 has become species 3 by t = 1e11.
    assert sol.y[2, -1] == pytest.approx(1.0, abs=1e-6)
    assert sol.stats.naccepted < 2000, f"{sol.stats.naccepted} steps is too many"


@pytest.mark.parametrize("method", STIFF_METHODS)
def test_robertson_step_count_is_competitive_with_scipy(method):
    bench = robertson()
    ours = solve(bench.problem, method=method, rtol=1e-6, atol=1e-10)
    theirs = scipy_solve_ivp(
        lambda t, y: bench.problem.f(t, y),
        (0, 1e11),
        bench.problem.y0,
        method="Radau",
        rtol=1e-6,
        atol=1e-10,
        jac=lambda t, y: bench.problem.jac(t, y),
    )
    assert ours.stats.naccepted < 4 * (len(theirs.t) - 1), (
        f"{method}: {ours.stats.naccepted} steps vs scipy's {len(theirs.t) - 1}"
    )
    assert np.allclose(ours.y[:, -1], theirs.y[:, -1], atol=1e-7)


@pytest.mark.parametrize("method", STIFF_METHODS)
def test_van_der_pol_mu_1000(method):
    """Relaxation oscillator, stiff enough to stop any explicit method dead."""
    bench = van_der_pol(mu=1000.0)
    ours = solve(bench.problem, method=method, rtol=1e-7, atol=1e-9)
    assert ours.success, ours.message

    theirs = scipy_solve_ivp(
        lambda t, y: bench.problem.f(t, y),
        (0, bench.problem.tf),
        bench.problem.y0,
        method="Radau",
        rtol=1e-7,
        atol=1e-9,
        jac=lambda t, y: bench.problem.jac(t, y),
    )
    assert np.allclose(ours.y[:, -1], theirs.y[:, -1], rtol=1e-4, atol=1e-6), (
        f"{method}: {ours.y[:, -1]} vs scipy {theirs.y[:, -1]}"
    )
    assert ours.stats.naccepted < 3 * (len(theirs.t) - 1), (
        f"{method}: {ours.stats.naccepted} steps vs scipy's {len(theirs.t) - 1}"
    )


@pytest.mark.parametrize("method", ["dopri5", "tsit5", "rk23"])
def test_explicit_methods_fail_on_robertson(method):
    """The other half of the claim: these problems really are stiff.

    An explicit method is not merely slower here -- it is bounded by absolute
    stability rather than accuracy, so its step size cannot exceed roughly
    1/|lambda_max| no matter how loose the tolerance. Over eleven decades of
    time that is an impossible number of steps.
    """
    bench = robertson()
    sol = solve(bench.problem, method=method, rtol=1e-6, atol=1e-10, max_steps=20000)
    assert not sol.success
    assert "max_steps" in sol.message


def test_stiff_methods_still_work_on_nonstiff_problems():
    """Using an implicit method where it is not needed must not break anything."""
    bench = sine_cosine()
    for method in STIFF_METHODS:
        sol = solve(bench.problem, method=method, rtol=1e-9, atol=1e-12)
        assert sol.success
        assert np.allclose(sol.y[:, -1], bench.exact_at_end(), atol=1e-7)


# ---------------------------------------------------------------------------
# Jacobian handling inside the steppers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", STIFF_METHODS)
def test_works_without_an_analytic_jacobian(method):
    """Falling back to finite differences must not change the answer."""
    bench = robertson()
    with_jac = solve(bench.problem, method=method, rtol=1e-7, atol=1e-11)

    no_jac = ODEProblem(
        f=bench.problem.f_user, t_span=(0.0, 1e11), y0=bench.problem.y0
    )
    without = solve(no_jac, method=method, rtol=1e-7, atol=1e-11)

    assert without.success, without.message
    assert np.allclose(without.y[:, -1], with_jac.y[:, -1], atol=1e-7)
    assert without.stats.nfev > with_jac.stats.nfev, (
        "finite-difference Jacobians must be counted in nfev"
    )


@pytest.mark.parametrize("method", STIFF_METHODS)
def test_stats_record_implicit_work(method):
    bench = van_der_pol(mu=100.0)
    sol = solve(bench.problem, method=method, rtol=1e-6, atol=1e-8)
    assert sol.stats.njev > 0, "no Jacobian evaluations recorded"
    assert sol.stats.nlu > 0, "no LU factorisations recorded"
    assert sol.stats.nfev > sol.stats.nsteps


def test_radau_reuses_jacobians_across_steps():
    """Simplified Newton's whole point: far fewer Jacobians than steps.

    Rosenbrock cannot do this -- its coefficients assume an exact Jacobian -- so
    the comparison also documents the real trade-off between the two families.
    """
    bench = van_der_pol(mu=1000.0)
    radau = solve(bench.problem, method="radau", rtol=1e-7, atol=1e-9)
    rodas = solve(bench.problem, method="rodas4", rtol=1e-7, atol=1e-9)

    assert radau.stats.njev < 0.1 * radau.stats.naccepted, (
        f"radau evaluated {radau.stats.njev} Jacobians for "
        f"{radau.stats.naccepted} steps"
    )
    assert rodas.stats.njev >= rodas.stats.naccepted
    assert radau.stats.njev < rodas.stats.njev


def test_rodas4_is_stiffly_accurate():
    assert RODAS4.stiffly_accurate
    assert np.isclose(RODAS4.alpha[-1], 1.0)


def test_rodas4_consistency_condition():
    """``sum(b_i d_i) == 1``, the ``f == 1`` collapse described in the module.

    The Rosenbrock analogue of the Butcher row-sum condition, and the cheapest
    check that the coefficient block was transcribed correctly.
    """
    assert RODAS4.b @ RODAS4.d == pytest.approx(1.0, abs=1e-12)
    assert RODAS4.b_hat @ RODAS4.d == pytest.approx(1.0, abs=1e-12)


def test_rodas4_gamma_is_the_repeated_diagonal():
    assert RODAS4.gamma == 0.25
    assert np.allclose(np.triu(RODAS4.A), 0.0)
    assert np.allclose(np.triu(RODAS4.C), 0.0)
