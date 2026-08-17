"""Symplectic integrators: composition orders and structure preservation."""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import ODEProblem, solve
from odesuite.problems import harmonic_oscillator_2d, kepler_second_order
from odesuite.steppers.symplectic import (
    CompositionMethod,
    StormerVerlet,
    second_order_problem,
    triple_jump_weights,
)


# ---------------------------------------------------------------------------
# Composition weights, derived rather than transcribed
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("order", [2, 4, 6, 8])
def test_triple_jump_weights_sum_to_one(order):
    """Consistency: the substeps must span exactly one step of length h."""
    weights = triple_jump_weights(order)
    assert weights.sum() == pytest.approx(1.0, abs=1e-14)
    assert weights.size == 3 ** (order // 2 - 1)


@pytest.mark.parametrize("order", [4, 6, 8])
def test_triple_jump_weights_are_palindromic(order):
    """Symmetry is what raises the order; an asymmetric composition would not."""
    weights = triple_jump_weights(order)
    assert np.allclose(weights, weights[::-1], atol=1e-14)


def test_triple_jump_has_a_negative_substep():
    """Any composition above order 2 must step backwards somewhere.

    A theorem of Suzuki: no composition with all-positive weights exceeds order
    two. The negative middle weight is therefore not a quirk of this
    construction but unavoidable, and worth asserting so nobody "fixes" it.
    """
    assert triple_jump_weights(4).min() < 0
    assert triple_jump_weights(6).min() < 0


def test_invalid_order_raises():
    for bad in (0, 3, -2):
        with pytest.raises(ValueError, match="even and at least 2"):
            triple_jump_weights(bad)


# ---------------------------------------------------------------------------
# Order verification
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method,expected", [("verlet", 2), ("yoshida4", 4), ("yoshida6", 6)]
)
def test_convergence_order(method, expected):
    """Global error against the analytic solution of ``q'' = -q``."""
    bench = harmonic_oscillator_2d(t_end=2.0)
    exact = bench.exact_at_end()

    errors, steps = [], [20, 40, 80, 160]
    for n in steps:
        sol = solve(bench.problem, method=method, n_steps=n)
        errors.append(np.linalg.norm(sol.y[:, -1] - exact))

    slope = np.log(errors[-2] / errors[-1]) / np.log(2.0)
    assert slope == pytest.approx(expected, abs=0.25), (
        f"{method}: order {slope:.2f}, expected {expected}; "
        f"errors={['%.2e' % e for e in errors]}"
    )


def test_higher_order_composition_is_more_accurate():
    bench = harmonic_oscillator_2d(t_end=2.0)
    exact = bench.exact_at_end()
    errors = [
        np.linalg.norm(solve(bench.problem, method=m, n_steps=80).y[:, -1] - exact)
        for m in ("verlet", "yoshida4", "yoshida6")
    ]
    assert errors[0] > errors[1] > errors[2]


# ---------------------------------------------------------------------------
# Structure preservation -- the reason these methods exist
# ---------------------------------------------------------------------------


def _energy_trace(sol, bench, samples=400):
    idx = np.linspace(0, sol.y.shape[1] - 1, min(samples, sol.y.shape[1])).astype(int)
    E0 = bench.invariant(bench.problem.y0)
    return np.array([abs(bench.invariant(sol.y[:, i]) - E0) / abs(E0) for i in idx])


@pytest.mark.parametrize("method,n_steps", [("verlet", 100_000), ("yoshida4", 40_000)])
def test_energy_error_is_bounded_not_growing(method, n_steps):
    """A symplectic method's energy error oscillates; it does not accumulate.

    Measured as the ratio of the worst energy error in the second half of the
    integration to the worst in the first half. For a symplectic method that
    ratio is 1: the error is a bounded oscillation, the same size at the end as
    at the beginning. For a non-symplectic method it grows with time.
    """
    bench = kepler_second_order(eccentricity=0.3, n_orbits=500.0)
    sol = solve(bench.problem, method=method, n_steps=n_steps)
    assert sol.success, sol.message

    drift = _energy_trace(sol, bench)
    half = drift.size // 2
    ratio = drift[half:].max() / max(drift[:half].max(), 1e-30)
    assert ratio < 1.5, (
        f"{method}: energy error grew by {ratio:.2f}x over the second half; "
        f"a symplectic method must stay bounded"
    )


def test_non_symplectic_method_drifts_where_verlet_does_not():
    """The comparison that makes the point.

    DOPRI5 is far more accurate per step, and over 500 orbits its energy error
    is still smaller in absolute terms -- but it *grows linearly with time*
    while Verlet's does not. Extrapolate and the orbit eventually decays.
    """
    bench = kepler_second_order(eccentricity=0.3, n_orbits=500.0)

    verlet = solve(bench.problem, method="verlet", n_steps=100_000)
    rk = solve(bench.problem, method="dopri5", rtol=3e-8, atol=3e-10)

    verlet_drift = _energy_trace(verlet, bench)
    rk_drift = _energy_trace(rk, bench)

    verlet_half = verlet_drift.size // 2
    rk_half = rk_drift.size // 2
    verlet_ratio = verlet_drift[verlet_half:].max() / max(verlet_drift[:verlet_half].max(), 1e-30)
    rk_ratio = rk_drift[rk_half:].max() / max(rk_drift[:rk_half].max(), 1e-30)

    assert verlet_ratio < 1.5, f"Verlet drifted, ratio {verlet_ratio:.2f}"
    assert rk_ratio > 1.5, (
        f"DOPRI5 energy ratio {rk_ratio:.2f}; expected visible secular growth"
    )


def test_angular_momentum_is_conserved():
    """Verlet preserves angular momentum to round-off on a central-force problem."""
    bench = kepler_second_order(eccentricity=0.5, n_orbits=50.0)
    sol = solve(bench.problem, method="verlet", n_steps=50_000)

    L0 = bench.angular_momentum(bench.problem.y0)
    L = np.array([bench.angular_momentum(sol.y[:, i]) for i in range(0, sol.y.shape[1], 97)])
    assert np.abs(L - L0).max() / abs(L0) < 1e-12


def test_time_reversibility():
    """Integrating forward then backward returns to the start.

    Verlet is symmetric, so reversing time reverses the map exactly -- the
    round trip is limited only by round-off, not by the method's order.
    """
    bench = harmonic_oscillator_2d(t_end=10.0)
    forward = solve(bench.problem, method="verlet", n_steps=2000)

    d = bench.problem.n_coordinates
    end = forward.y[:, -1]
    back = second_order_problem(
        lambda t, q: -q, (10.0, 0.0), end[:d], end[d:]
    )
    reverse = solve(back, method="verlet", n_steps=2000)
    assert np.allclose(reverse.y[:, -1], bench.problem.y0, atol=1e-11)


# ---------------------------------------------------------------------------
# Problem construction and validation
# ---------------------------------------------------------------------------


def test_second_order_problem_builds_a_normal_ivp():
    """The wrapped problem is an ordinary IVP any method can integrate."""
    bench = harmonic_oscillator_2d(t_end=3.0)
    exact = bench.exact_at_end()
    for method in ("dopri5", "radau", "verlet"):
        kwargs = {"n_steps": 3000} if method == "verlet" else {"rtol": 1e-11, "atol": 1e-13}
        sol = solve(bench.problem, method=method, **kwargs)
        assert np.allclose(sol.y[:, -1], exact, atol=1e-6), f"{method} disagrees"


def test_symplectic_method_rejects_a_non_separable_problem():
    """Without the separable structure the flow cannot be split."""
    problem = ODEProblem(f=lambda t, y: -y, t_span=(0.0, 1.0), y0=[1.0])
    with pytest.raises(ValueError, match="separable second-order system"):
        solve(problem, method="verlet", n_steps=10)


def test_fixed_step_methods_require_a_step_specification():
    """A non-adaptive method must not be allowed to pick its own step."""
    bench = harmonic_oscillator_2d()
    with pytest.raises(ValueError, match="fixed step size"):
        solve(bench.problem, method="verlet")


@pytest.mark.parametrize("n_steps", [64, 97, 1000, 2003])
def test_fixed_step_solve_is_exactly_uniform(n_steps):
    """Every step identical, and the last one landing exactly on tf.

    Time is advanced as ``t0 + k*h`` rather than by accumulation. Accumulating
    drifts by O(n*eps) -- material over a 200 000-step symplectic run -- and
    leaves the final step a rounding error short of tf, producing a crumb step
    orders of magnitude smaller than the rest. Harmless numerically, but it
    destroys the constant-step property these methods are chosen for.
    """
    bench = harmonic_oscillator_2d(t_end=10.0)
    sol = solve(bench.problem, method="verlet", n_steps=n_steps)

    assert sol.stats.naccepted == n_steps
    assert sol.stats.nrejected == 0
    assert sol.t[-1] == 10.0, "the final step must land exactly on t_end"

    h = np.diff(sol.t)
    assert h.max() / h.min() == pytest.approx(1.0, abs=1e-12), (
        f"steps are not uniform: {h.min():.6e} to {h.max():.6e}"
    )


def test_first_step_also_specifies_a_fixed_step():
    """A step that does not divide the interval shortens only the last one."""
    bench = harmonic_oscillator_2d(t_end=10.0)
    sol = solve(bench.problem, method="verlet", first_step=0.3)
    assert sol.success
    assert sol.t[-1] == pytest.approx(10.0, abs=1e-12)

    h = np.diff(sol.t)
    assert np.allclose(h[:-1], 0.3, atol=1e-12)
    assert 0 < h[-1] <= 0.3 + 1e-12


def test_mismatched_initial_conditions_raise():
    with pytest.raises(ValueError, match="q0 and v0 must match"):
        second_order_problem(lambda t, q: -q, (0.0, 1.0), [1.0, 2.0], [0.0])


def test_verlet_costs_two_accelerations_per_step():
    bench = harmonic_oscillator_2d(t_end=1.0)
    sol = solve(bench.problem, method="verlet", n_steps=50)
    assert sol.stats.nfev / sol.stats.nsteps == pytest.approx(2.0, abs=0.1)


def test_composition_repr_and_names():
    assert StormerVerlet().name == "Verlet"
    assert CompositionMethod(6).name == "Yoshida6"
    assert not StormerVerlet().adaptive
    assert not CompositionMethod(4).adaptive
