"""Simplified Newton and the Jacobian-freshness policy, tested in isolation.

`newton.py` is the module the design table names as the single home for
theta-monitoring and LU reuse. Both behaviours are subtle, both are invisible in
an accuracy test -- a stiff solve that iterates twice as long still lands on the
right answer -- and until now neither had a test of its own.

The load-bearing one is `test_slow_convergence_is_not_mistaken_for_convergence`:
it pins the documented reason the termination test uses the remaining geometric
series rather than the last correction.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite.newton import (
    JacobianPolicy,
    NewtonSettings,
    simplified_newton,
)

UNIT = np.array([1.0])


def _geometric(start: float, ratio: float):
    """A `solve_linear` whose correction norms decay by exactly `ratio`.

    Lets the convergence logic be tested against arithmetic that is known in
    closed form, rather than against whatever a real problem happens to do.
    """
    state = {"k": 0}

    def solve_linear(residual_value):
        k = state["k"]
        state["k"] += 1
        return np.array([start * ratio**k])

    return solve_linear


# ---------------------------------------------------------------------------
# Convergence
# ---------------------------------------------------------------------------


def test_newton_finds_a_root_with_a_frozen_jacobian():
    """The defining property: the iteration matrix is held fixed and it still
    converges, just linearly instead of quadratically."""
    # x^2 - 2 = 0, Newton correction -F/J with J frozen at 2*1.5 = 3.
    result = simplified_newton(
        residual=lambda x: -(x**2 - 2.0),
        solve_linear=lambda r: r / 3.0,
        x0=np.array([1.5]),
        scale=np.array([1e-8]),
    )
    assert result.converged
    assert result.x[0] == pytest.approx(np.sqrt(2.0), abs=1e-9)


def test_an_exact_first_solve_lands_then_confirms():
    """A linear residual with the true Jacobian is solved by the *first*
    correction -- but convergence still costs a second iteration, because the
    only way to learn the residual is now zero is to evaluate it. Two is the
    floor for an exact solve, not a sign of inefficiency."""
    result = simplified_newton(
        residual=lambda x: -(2.0 * x - 4.0),
        solve_linear=lambda r: r / 2.0,
        x0=np.array([0.0]),
        scale=UNIT,
    )
    assert result.converged
    assert result.n_iter == 2
    assert result.correction == 0.0
    assert result.x[0] == pytest.approx(2.0)


def test_a_good_starting_guess_stops_on_the_first_iteration():
    """With no rate yet inferable, the fallback test is the raw correction."""
    result = simplified_newton(
        residual=lambda x: -(x - 1.0) * 1e-9,
        solve_linear=lambda r: r,
        x0=np.array([1.0 + 1e-9]),
        scale=UNIT,
        settings=NewtonSettings(tol_factor=0.03),
    )
    assert result.converged
    assert result.n_iter == 1
    assert result.rate is None


def test_slow_convergence_is_not_mistaken_for_convergence():
    """The reason the termination test is ``theta/(1-theta)*|dx|``.

    With a rate of 0.8 the remaining error is *four times* the last correction.
    A naive ``|dx| < tol`` test would stop at iteration 7, where the correction
    first dips under the tolerance but 4x that is still six times too large.
    The real iteration must run on to 13.
    """
    settings = NewtonSettings(max_iter=50, tol_factor=0.03, max_rate=0.95)
    result = simplified_newton(
        residual=lambda x: x,
        solve_linear=_geometric(start=0.1, ratio=0.8),
        x0=np.array([0.0]),
        scale=UNIT,
        settings=settings,
    )
    assert result.converged
    assert result.rate == pytest.approx(0.8)
    # The correction alone first falls below tol_factor at iteration 7.
    assert result.n_iter > 7, (
        f"stopped after {result.n_iter} iterations: the termination test is "
        f"reading the last correction, not the remaining series"
    )
    assert result.n_iter == 13
    # And the estimate it stopped on really is below tolerance.
    assert result.rate / (1 - result.rate) * result.correction < settings.tol_factor


# ---------------------------------------------------------------------------
# Failure detection
# ---------------------------------------------------------------------------


def test_divergence_is_detected_and_reported():
    """A growing correction must be caught, not iterated to max_iter."""
    result = simplified_newton(
        residual=lambda x: x,
        solve_linear=_geometric(start=0.1, ratio=1.5),
        x0=np.array([0.0]),
        scale=UNIT,
        settings=NewtonSettings(max_iter=20),
    )
    assert not result.converged
    assert result.rate is not None and result.rate >= 0.95
    assert result.n_iter == 2, "divergence should be caught on the second iteration"


def test_convergence_too_slow_to_be_worth_continuing_is_rejected():
    """Just under 1.0 is still a failure: refactorising beats grinding on."""
    result = simplified_newton(
        residual=lambda x: x,
        solve_linear=_geometric(start=0.1, ratio=0.97),
        x0=np.array([0.0]),
        scale=UNIT,
        settings=NewtonSettings(max_iter=50, max_rate=0.95),
    )
    assert not result.converged
    assert result.rate == pytest.approx(0.97)


def test_a_diverging_step_is_not_applied():
    """When the rate test fires, the iteration returns *before* adding the bad
    correction -- returning a state polluted by the step that proved divergence
    would hand the caller a worse guess than it started with."""
    result = simplified_newton(
        residual=lambda x: x,
        solve_linear=_geometric(start=1.0, ratio=10.0),
        x0=np.array([0.0]),
        scale=UNIT,
    )
    assert not result.converged
    # Only the first correction (1.0) was applied; the second (10.0) was not.
    assert result.x[0] == pytest.approx(1.0)


def test_running_out_of_iterations_reports_failure():
    result = simplified_newton(
        residual=lambda x: x,
        solve_linear=_geometric(start=0.1, ratio=0.9),
        x0=np.array([0.0]),
        scale=UNIT,
        settings=NewtonSettings(max_iter=4, tol_factor=1e-12),
    )
    assert not result.converged
    assert result.n_iter == 4


def test_the_starting_guess_is_not_mutated():
    """The caller's array is reused across step attempts; overwriting it in
    place would corrupt a retry."""
    x0 = np.array([1.5])
    simplified_newton(
        residual=lambda x: -(x**2 - 2.0),
        solve_linear=lambda r: r / 3.0,
        x0=x0,
        scale=UNIT,
    )
    assert x0[0] == 1.5


def test_the_scale_weights_the_convergence_test():
    """All norms are taken relative to `scale`, so the test means the same thing
    for a component of size 1e6 as for one of size 1e-6."""
    loose = simplified_newton(
        residual=lambda x: x, solve_linear=_geometric(0.1, 0.5),
        x0=np.array([0.0]), scale=np.array([1.0]),
    )
    tight = simplified_newton(
        residual=lambda x: x, solve_linear=_geometric(0.1, 0.5),
        x0=np.array([0.0]), scale=np.array([1e-6]),
    )
    assert loose.n_iter < tight.n_iter


def test_a_multi_component_norm_is_rms():
    """Matches `error_norm`'s convention, so a large system is not judged by its
    worst component alone."""
    result = simplified_newton(
        residual=lambda x: x,
        solve_linear=lambda r: np.array([1.0, 0.0, 0.0, 0.0]),
        x0=np.zeros(4),
        scale=np.ones(4),
        settings=NewtonSettings(max_iter=1),
    )
    assert result.correction == pytest.approx(0.5)  # norm([1,0,0,0])/sqrt(4)


# ---------------------------------------------------------------------------
# JacobianPolicy
# ---------------------------------------------------------------------------


def test_a_fresh_policy_wants_a_jacobian():
    policy = JacobianPolicy()
    assert policy.needs_jacobian(last_rate=None, after_failure=False)
    assert policy.needs_factorization(h=0.1)


def test_a_current_jacobian_is_not_recomputed():
    policy = JacobianPolicy()
    policy.store_jacobian(np.eye(2))
    assert not policy.needs_jacobian(last_rate=0.9, after_failure=False)


def test_a_step_old_jacobian_survives_brisk_convergence():
    """The whole economy of simplified Newton: reuse J while Newton is happy."""
    policy = JacobianPolicy()
    policy.store_jacobian(np.eye(2))
    policy.mark_step_done()
    assert not policy.needs_jacobian(last_rate=0.1, after_failure=False)


def test_a_stale_rate_forces_a_new_jacobian():
    policy = JacobianPolicy()
    policy.store_jacobian(np.eye(2))
    policy.mark_step_done()
    assert policy.needs_jacobian(last_rate=0.5, after_failure=False)


def test_an_unknown_rate_forces_a_new_jacobian():
    """No rate means Newton converged too fast to infer one, or not at all.
    Recomputing is the safe reading."""
    policy = JacobianPolicy()
    policy.store_jacobian(np.eye(2))
    policy.mark_step_done()
    assert policy.needs_jacobian(last_rate=None, after_failure=False)


def test_a_failure_forces_a_new_jacobian_even_when_current():
    policy = JacobianPolicy()
    policy.store_jacobian(np.eye(2))
    assert policy.needs_jacobian(last_rate=0.01, after_failure=True)


def test_factorisation_is_reused_across_a_small_step_change():
    """An O(n^3) refactorisation must not be triggered by every nudge of h."""
    policy = JacobianPolicy()
    policy.store_jacobian(np.eye(2))
    policy.store_factorization(object(), h=0.1)
    assert not policy.needs_factorization(0.105)
    assert not policy.needs_factorization(0.119)


def test_factorisation_is_redone_after_a_large_step_change():
    policy = JacobianPolicy()
    policy.store_jacobian(np.eye(2))
    policy.store_factorization(object(), h=0.1)
    assert policy.needs_factorization(0.5)
    assert policy.needs_factorization(0.01)


def test_a_new_jacobian_invalidates_the_old_factorisation():
    """The factorisation is built *from* J; keeping it after J changes would
    apply the inverse of a matrix that no longer exists."""
    policy = JacobianPolicy()
    policy.store_jacobian(np.eye(2))
    policy.store_factorization(object(), h=0.1)
    assert not policy.needs_factorization(0.1)

    policy.store_jacobian(2 * np.eye(2))
    assert policy.factorization is None
    assert policy.needs_factorization(0.1)


def test_the_sign_of_h_is_respected_when_comparing_steps():
    """Backward integration carries a negative h; the freshness test compares
    magnitudes, so a sign flip of the same size is still a large change."""
    policy = JacobianPolicy()
    policy.store_jacobian(np.eye(2))
    policy.store_factorization(object(), h=0.1)
    assert policy.needs_factorization(-0.1)
