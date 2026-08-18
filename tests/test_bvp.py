"""Two-point boundary value problems by multiple shooting."""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import BVProblem, solve_bvp
from odesuite.problems import bratu, bvp_linear, bvp_trig

# ---------------------------------------------------------------------------
# Linear problems: Newton must converge immediately
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("n_nodes", [1, 2, 5, 10, 20])
def test_linear_bvp_matches_analytic_solution(n_nodes):
    """``y'' = y``, ``y(0)=0``, ``y(1)=1``; solution ``sinh(x)/sinh(1)``."""
    bench = bvp_linear()
    sol = solve_bvp(
        bench.problem, bench.guess, n_nodes=n_nodes, rtol=1e-11, atol=1e-13, tol=1e-10
    )

    assert sol.converged, sol.message
    t = np.linspace(0.0, 1.0, 201)
    err = np.abs(sol.y_at(t) - bench.exact(t)).max()
    assert err < 1e-9, f"n_nodes={n_nodes}: max error {err:.3e}"


def test_linear_problem_converges_in_one_newton_step():
    """Newton is exact on a linear problem, so the first step must land on it.

    A sharp check on the shooting Jacobian: if any propagation block or boundary
    block were wrong, the first correction would not solve the system and
    convergence would take several iterations instead of one.
    """
    bench = bvp_linear()
    sol = solve_bvp(
        bench.problem, bench.guess, n_nodes=5, rtol=1e-12, atol=1e-14, tol=1e-9
    )
    assert sol.converged
    # history[0] is the initial residual, history[1] the one after a single
    # Newton step. It should already be at the integrator's noise floor.
    assert sol.history[1] < 1e-8 * sol.history[0], (
        f"one Newton step reduced the residual only from {sol.history[0]:.2e} "
        f"to {sol.history[1]:.2e}; the Jacobian is inexact"
    )


def test_boundary_conditions_are_satisfied():
    bench = bvp_linear()
    sol = solve_bvp(bench.problem, bench.guess, n_nodes=8, rtol=1e-11, tol=1e-10)
    ya, yb = sol.y_at(0.0), sol.y_at(1.0)
    assert abs(ya[0]) < 1e-9
    assert abs(yb[0] - 1.0) < 1e-9


def test_continuity_across_nodes():
    """The converged node states must lie on one continuous trajectory."""
    bench = bvp_trig(6.0)
    sol = solve_bvp(bench.problem, bench.guess, n_nodes=12, rtol=1e-11, tol=1e-10)
    assert sol.converged
    at_nodes = sol.y_at(sol.nodes)
    assert np.allclose(at_nodes, sol.y_nodes, atol=1e-8), (
        "the continuous solution disagrees with the node states"
    )


@pytest.mark.parametrize("k", [6.0, 20.0, 50.0])
def test_oscillatory_bvp(k):
    """``y'' = -k^2 y``: increasingly ill-conditioned as k grows."""
    bench = bvp_trig(k)
    sol = solve_bvp(bench.problem, bench.guess, n_nodes=20, rtol=1e-11, atol=1e-13, tol=1e-9)

    assert sol.converged, sol.message
    t = np.linspace(0.0, 1.0, 401)
    err = np.abs(sol.y_at(t) - bench.exact(t)).max()
    assert err < 1e-6, f"k={k}: max error {err:.3e}"


# ---------------------------------------------------------------------------
# Bratu: the nonlinear test, and the one with two answers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("branch", ["lower", "upper"])
def test_bratu_both_branches(branch):
    """``y'' + exp(y) = 0`` has two solutions; the guess selects which.

    The real test of a BVP solver: converging to the branch it was aimed at
    rather than always sliding to the easy one. The upper branch is the unstable
    solution and is the harder of the two.
    """
    bench = bratu(1.0, branch)
    sol = solve_bvp(
        bench.problem, bench.guess, n_nodes=10, rtol=1e-11, atol=1e-13, tol=1e-9
    )

    assert sol.converged, f"{branch} branch: {sol.message}"
    t = np.linspace(0.0, 1.0, 201)
    err = np.abs(sol.y_at(t) - bench.exact(t)).max()
    assert err < 1e-7, f"{branch} branch: max error {err:.3e}"
    assert sol.y_at(0.5)[0] == pytest.approx(bench.peak, abs=1e-7)


def test_bratu_branches_are_distinct():
    """Confirms the two solutions really are different, not the same one twice."""
    lower = bratu(1.0, "lower")
    upper = bratu(1.0, "upper")
    assert upper.peak > 20 * lower.peak

    sl = solve_bvp(lower.problem, lower.guess, n_nodes=10, rtol=1e-11, tol=1e-9)
    su = solve_bvp(upper.problem, upper.guess, n_nodes=10, rtol=1e-11, tol=1e-9)
    assert sl.converged and su.converged
    assert su.y_at(0.5)[0] > 20 * sl.y_at(0.5)[0]


def test_bratu_newton_converges_quadratically():
    """Residuals should roughly square each iteration once close.

    Quadratic convergence is the signature of a correct Jacobian; a
    finite-difference Jacobian that is merely approximate degrades it to linear.
    """
    bench = bratu(1.0, "upper")
    sol = solve_bvp(
        bench.problem, bench.guess, n_nodes=10, rtol=1e-12, atol=1e-14, tol=1e-11
    )
    assert sol.converged, sol.message

    history = [h for h in sol.history if h > 1e-11]
    # Over the last two usable iterations the exponent should improve sharply.
    assert len(history) >= 3
    ratio = history[-1] / history[-2] ** 1.5
    assert ratio < 1.0, f"convergence looks linear, not quadratic: {history}"


def test_bratu_above_critical_lambda_is_rejected():
    """No solution exists above lam_c = 3.5138; the benchmark must say so."""
    with pytest.raises(ValueError, match="no solution"):
        bratu(4.0, "lower")


# ---------------------------------------------------------------------------
# Robustness and failure reporting
# ---------------------------------------------------------------------------


def test_multiple_shooting_beats_single_on_an_unstable_problem():
    """``y'' = 400 y`` grows like ``e^(20x)``: single shooting cannot see the solution.

    Over a unit interval a perturbation at the left end is amplified by
    ``e^20 ~ 5e8``, which swamps the boundary residual. Splitting the interval
    caps the amplification per shot and restores conditioning -- the entire
    reason multiple shooting exists.
    """
    k = 20.0
    problem = BVProblem(
        f=lambda t, y: np.array([y[1], k**2 * y[0]]),
        t_span=(0.0, 1.0),
        bc=lambda ya, yb: np.array([ya[0] - 1.0, yb[0] - 1.0]),
        n=2,
    )
    guess = lambda t: np.array([1.0, 0.0])

    single = solve_bvp(problem, guess, n_nodes=1, rtol=1e-10, atol=1e-12, tol=1e-8)
    multi = solve_bvp(problem, guess, n_nodes=20, rtol=1e-10, atol=1e-12, tol=1e-8)

    assert multi.converged, multi.message
    # The exact solution is cosh-like; check the boundary conditions hold.
    assert abs(multi.y_at(0.0)[0] - 1.0) < 1e-7
    assert abs(multi.y_at(1.0)[0] - 1.0) < 1e-7
    if single.converged:
        assert multi.residual_norm <= single.residual_norm * 1e3


def test_failure_is_reported_not_silently_returned():
    """A guess that cannot converge must set converged=False with a reason."""
    bench = bratu(3.5, "upper")
    sol = solve_bvp(
        bench.problem,
        np.array([-50.0, 0.0]),   # nowhere near either branch
        n_nodes=3,
        rtol=1e-8,
        tol=1e-10,
        max_iter=4,
    )
    assert not sol.converged
    assert sol.message
    with pytest.raises(RuntimeError, match="no continuous solution"):
        sol.y_at(0.5)


def test_unintegrable_guess_is_reported():
    """A guess that makes the very first shot blow up fails cleanly."""
    problem = BVProblem(
        f=lambda t, y: np.array([y[0] ** 2]),
        t_span=(0.0, 10.0),
        bc=lambda ya, yb: np.array([ya[0] - 1.0]),
        n=1,
    )
    sol = solve_bvp(problem, np.array([1e3]), n_nodes=1, rtol=1e-8, max_iter=3)
    assert not sol.converged
    assert sol.message


# ---------------------------------------------------------------------------
# API surface
# ---------------------------------------------------------------------------


def test_guess_forms_are_equivalent():
    """Constant, callable and array guesses must all be accepted."""
    bench = bvp_linear()
    nodes = np.linspace(0.0, 1.0, 6)

    from_constant = solve_bvp(bench.problem, np.array([0.5, 1.0]), n_nodes=5, tol=1e-10)
    from_callable = solve_bvp(bench.problem, lambda t: np.array([t, 1.0]), n_nodes=5, tol=1e-10)
    from_array = solve_bvp(
        bench.problem, np.stack([nodes, np.ones_like(nodes)]), n_nodes=5, tol=1e-10
    )

    for sol in (from_constant, from_callable, from_array):
        assert sol.converged, sol.message
    assert np.allclose(from_constant.y_nodes, from_callable.y_nodes, atol=1e-7)
    assert np.allclose(from_constant.y_nodes, from_array.y_nodes, atol=1e-7)


def test_bad_guess_shape_raises():
    bench = bvp_linear()
    with pytest.raises(ValueError, match="constant guess must have length"):
        solve_bvp(bench.problem, np.array([1.0, 2.0, 3.0]), n_nodes=4)
    with pytest.raises(ValueError, match="guess array must have shape"):
        solve_bvp(bench.problem, np.zeros((2, 3)), n_nodes=4)


def test_wrong_number_of_boundary_conditions_raises():
    problem = BVProblem(
        f=lambda t, y: np.array([y[1], -y[0]]),
        t_span=(0.0, 1.0),
        bc=lambda ya, yb: np.array([ya[0]]),   # only one condition for n=2
        n=2,
    )
    with pytest.raises(ValueError, match="bc returned 1 residuals"):
        solve_bvp(problem, np.array([0.0, 1.0]), n_nodes=2)


def test_reversed_t_span_raises():
    with pytest.raises(ValueError, match="a < b"):
        BVProblem(
            f=lambda t, y: y, t_span=(1.0, 0.0), bc=lambda ya, yb: ya, n=1
        )


def test_invalid_n_nodes_raises():
    bench = bvp_linear()
    with pytest.raises(ValueError, match="n_nodes must be at least 1"):
        solve_bvp(bench.problem, bench.guess, n_nodes=0)


def test_stiff_method_can_be_used_for_the_shots():
    """The shots are ordinary `solve` calls, so any method is available."""
    bench = bvp_linear()
    sol = solve_bvp(
        bench.problem, bench.guess, n_nodes=5, method="radau", rtol=1e-11, tol=1e-9
    )
    assert sol.converged, sol.message
    t = np.linspace(0.0, 1.0, 101)
    assert np.abs(sol.y_at(t) - bench.exact(t)).max() < 1e-8


def test_stats_and_repr():
    bench = bvp_linear()
    sol = solve_bvp(bench.problem, bench.guess, n_nodes=5, tol=1e-10)
    assert sol.stats.nfev > 0
    assert sol.stats.naccepted > 0
    assert "BVPSolution" in repr(sol)
    assert "converged" in repr(sol)


# ---------------------------------------------------------------------------
# The shooting system, tested without running Newton
# ---------------------------------------------------------------------------
#
# `solve_bvp` had reached 262 lines by holding the shooting machinery and the
# Newton iteration in one function, as five closures over its own arguments.
# The machinery is now `_ShootingSystem`, which is the point: the residual
# layout, the block-bidiagonal Jacobian and the Armijo line search could
# previously only be checked by inference from a converged answer.
#
# The load-bearing test here is `test_the_assembled_jacobian_matches_a_dense_one`.
# The `-I` coupling blocks are written in analytically rather than differenced,
# and an error there is exactly the kind that still converges on easy problems
# and fails mysteriously on hard ones.

from odesuite.bvp.shooting import (  # noqa: E402
    _initial_guess,
    _line_search,
    _ShootingSystem,
)


def _linear_system(n_nodes=3, rtol=1e-11, atol=1e-13, fd_floor=1.0):
    """``y'' = y`` on [0, 1] with y(0)=0, y(1)=1, split into `n_nodes` shots."""
    bvp = bvp_linear().problem
    nodes = np.linspace(bvp.a, bvp.b, n_nodes + 1)
    system = _ShootingSystem(
        bvp, nodes, method="dopri5", rtol=rtol, atol=atol, fd_floor=fd_floor
    )
    return system, nodes


def _exact_nodes(nodes):
    s = np.sinh(1.0)
    return np.stack([np.sinh(nodes) / s, np.cosh(nodes) / s], axis=0)


def test_a_shot_integrates_one_interval_and_counts_its_work():
    system, nodes = _linear_system(n_nodes=4)
    exact = _exact_nodes(nodes)

    end, dense = system.shoot(0, exact[:, 0])
    assert dense is None, "dense output is opt-in"
    assert np.allclose(end, exact[:, 1], atol=1e-9)
    assert system.stats.nfev > 0 and system.stats.naccepted > 0


def test_a_shot_can_return_its_continuous_solution():
    system, nodes = _linear_system(n_nodes=2)
    _, dense = system.shoot(0, _exact_nodes(nodes)[:, 0], want_dense=True)
    assert dense is not None
    midpoint = dense(0.5 * (nodes[0] + nodes[1]))
    assert midpoint.shape == (2,)


def test_a_shot_that_cannot_be_integrated_raises():
    """It must raise rather than return a large residual, because the line
    search treats the exception as "step too long" and backs off."""
    bvp = BVProblem(
        f=lambda t, y: np.array([y[0] ** 2 * 1e8, 0.0]),
        t_span=(0.0, 1.0),
        bc=lambda ya, yb: np.array([ya[0], yb[1]]),
        n=2,
    )
    system = _ShootingSystem(
        bvp, np.array([0.0, 1.0]), method="dopri5", rtol=1e-8, atol=1e-10,
        fd_floor=1.0,
    )
    with pytest.raises(FloatingPointError, match="shot 0 failed"):
        system.shoot(0, np.array([1e8, 1.0]))


def test_the_residual_vanishes_at_the_true_solution():
    system, nodes = _linear_system(n_nodes=5)
    r = system.residual(_exact_nodes(nodes))
    assert system.norm(r) < 1e-9


def test_the_residual_is_continuity_blocks_then_the_boundary_block():
    """Layout matters: the Jacobian is assembled against these row indices."""
    system, nodes = _linear_system(n_nodes=3)
    n, m = system.n, system.n_nodes

    S = _exact_nodes(nodes)
    S[:, 2] += 0.5                       # break continuity at node 2 only
    r = system.residual(S)

    assert r.size == (m + 1) * n
    # The boundary block is untouched: node 0 and node m still satisfy the bc.
    assert np.allclose(r[m * n :], 0.0, atol=1e-9)
    # Continuity is broken across the two intervals that touch node 2.
    assert abs(r[1 * n : 2 * n]).max() > 0.1
    assert abs(r[2 * n : 3 * n]).max() > 0.1
    assert abs(r[0 * n : 1 * n]).max() < 1e-8


def test_the_assembled_jacobian_matches_a_dense_one():
    """The whole assembly checked against brute force.

    The propagation blocks are differenced but the ``-I`` couplings are written
    in analytically, and the whole thing is placed into a sparse matrix by index
    arithmetic. Differencing the *entire* residual gives an independent answer
    that exercises none of that.
    """
    system, nodes = _linear_system(n_nodes=3, rtol=1e-12, atol=1e-14)
    S = _exact_nodes(nodes) + 0.05

    assembled = system.jacobian(S).toarray()

    size = (system.n_nodes + 1) * system.n
    dense = np.empty((size, size))
    base = system.residual(S)
    eps = 1e-6
    for col in range(size):
        perturbed = S.copy()
        perturbed[col % system.n, col // system.n] += eps
        dense[:, col] = (system.residual(perturbed) - base) / eps

    assert assembled.shape == (size, size)
    assert np.allclose(assembled, dense, rtol=2e-4, atol=2e-5), (
        f"largest discrepancy {np.abs(assembled - dense).max():.3e}"
    )


def test_the_jacobian_has_the_block_bidiagonal_sparsity():
    """The structure is the reason multiple shooting is affordable."""
    system, nodes = _linear_system(n_nodes=4)
    J = system.jacobian(_exact_nodes(nodes))
    n, m = system.n, system.n_nodes

    dense = J.toarray()
    # Every continuity row couples only to its own node and the next one.
    for k in range(m):
        rows = slice(k * n, (k + 1) * n)
        for other in range(m + 1):
            block = dense[rows, other * n : (other + 1) * n]
            if other in (k, k + 1):
                continue
            assert np.allclose(block, 0.0), f"row block {k} touches node {other}"
    # And the coupling to the next node is exactly -I, not a differenced copy.
    for k in range(m):
        block = dense[k * n : (k + 1) * n, (k + 1) * n : (k + 2) * n]
        assert np.array_equal(block, -np.eye(n))


def test_the_finite_difference_step_is_sized_by_the_integration_tolerance():
    """Recorded bug #2: a shot is only accurate to ~rtol, so the right step is
    sqrt(rtol), not sqrt(EPS). With a node component at zero the sqrt(EPS)
    perturbation was 1.5e-16 -- pure noise -- and every Bratu solve failed
    reporting only "line search failed"."""
    loose, _ = _linear_system(rtol=1e-8)
    tight, _ = _linear_system(rtol=1e-13)
    assert loose.fd_eps == pytest.approx(1e-4)
    assert tight.fd_eps > np.sqrt(np.finfo(float).eps) / 2

    # And the floor keeps a component sitting at zero from getting a useless
    # perturbation.
    steps = loose._fd_steps(np.array([0.0, 100.0]))
    assert steps[0] == pytest.approx(loose.fd_eps * 1.0)
    assert steps[1] == pytest.approx(loose.fd_eps * 100.0)


def test_the_norm_is_rms():
    system, _ = _linear_system()
    assert system.norm(np.array([3.0, 4.0])) == pytest.approx(5.0 / np.sqrt(2))


def test_dense_output_splices_every_interval():
    system, nodes = _linear_system(n_nodes=4)
    dense = system.dense_output(_exact_nodes(nodes))

    t = np.linspace(0.0, 1.0, 101)
    exact = np.sinh(t) / np.sinh(1.0)
    assert np.abs(dense(t)[0] - exact).max() < 1e-8


# ---------------------------------------------------------------------------
# The line search
# ---------------------------------------------------------------------------


def test_a_good_full_step_is_taken_undamped():
    system, nodes = _linear_system(n_nodes=3)
    exact = _exact_nodes(nodes)
    S = exact + 0.05
    r = system.residual(S)

    step = exact - S                       # exactly the correction needed
    outcome = _line_search(system, S, step, system.norm(r))

    assert outcome is not None
    _, _, new_norm, lam = outcome
    assert lam == 1.0, "no damping should be needed"
    assert new_norm < system.norm(r)


def test_a_step_that_does_not_help_is_reported_as_failure():
    """Returning None is what lets `solve_bvp` distinguish "converged onto the
    noise floor" from "genuinely stuck"."""
    system, nodes = _linear_system(n_nodes=2)
    S = _exact_nodes(nodes)
    r_norm = system.norm(system.residual(S))

    # Already at the solution: no direction can reduce the residual further.
    outcome = _line_search(system, S, np.ones_like(S) * 1e3, r_norm)
    assert outcome is None


def test_an_unintegrable_trial_step_is_backed_off_rather_than_raised():
    """A diverged shot raises; the search must treat that as "too long" and try
    a shorter step instead of letting the exception escape."""
    bvp = BVProblem(
        f=lambda t, y: np.array([y[1], np.exp(np.clip(y[0], -50, 50))]),
        t_span=(0.0, 1.0),
        bc=lambda ya, yb: np.array([ya[0], yb[0]]),
        n=2,
    )
    nodes = np.linspace(0.0, 1.0, 3)
    system = _ShootingSystem(
        bvp, nodes, method="dopri5", rtol=1e-9, atol=1e-11, fd_floor=1.0
    )
    S = _initial_guess(np.array([0.0, 0.0]), nodes, 2)
    r_norm = system.norm(system.residual(S))

    # A wildly long step: the first trials cannot be integrated at all.
    huge = np.full_like(S, 1e3)
    outcome = _line_search(system, S, huge, r_norm)
    assert outcome is None or outcome[3] <= 1.0
