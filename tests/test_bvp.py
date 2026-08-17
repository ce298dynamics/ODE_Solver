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
