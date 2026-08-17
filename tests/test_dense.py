"""Continuous extensions: accuracy, endpoint consistency, and vectorisation."""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import ODEProblem, solve
from odesuite.dense import HermiteInterpolant
from odesuite.problems import lotka_volterra, sine_cosine
from odesuite.tableaux import TABLEAUX

METHOD_NAMES = sorted({tab.name.lower(): key for key, tab in TABLEAUX.items()}.values())


@pytest.mark.parametrize("method", METHOD_NAMES)
def test_dense_output_matches_step_points(method):
    """Evaluated at the accepted step times, the interpolant must return the
    step values themselves -- otherwise the segments do not join up."""
    bench = sine_cosine()
    sol = solve(bench.problem, method=method, rtol=1e-8, atol=1e-10, dense_output=True)

    values = sol.y_at(sol.t)
    assert np.allclose(values, sol.y, atol=1e-11), (
        f"{method}: interpolant disagrees with the step values by "
        f"{np.abs(values - sol.y).max():.3e}"
    )


@pytest.mark.parametrize("method", METHOD_NAMES)
def test_dense_output_accuracy(method):
    """Between step points the interpolant must still track the true solution.

    Sampled off the step grid on purpose: an interpolant that is exact at the
    nodes but poor in between would pass the previous test and still be useless
    for event location.
    """
    bench = sine_cosine()
    sol = solve(bench.problem, method=method, rtol=1e-9, atol=1e-12, dense_output=True)

    t = np.linspace(sol.sol.t_min, sol.sol.t_max, 977)
    err = np.abs(sol.y_at(t) - bench.exact(t)).max()
    assert err < 1e-6, f"{method}: dense output error {err:.3e}"


def test_native_interpolant_beats_hermite():
    """DOPRI5's published interpolant is 4th order; the Hermite fallback is 3rd.

    Confirms the tableau's P matrix is actually being used, rather than the code
    quietly falling back for every method.
    """
    bench = sine_cosine()
    t = np.linspace(0.0, 6.0, 501)
    exact = bench.exact(t)

    native = solve(bench.problem, method="dopri5", rtol=1e-6, dense_output=True)
    fallback = solve(bench.problem, method="cashkarp", rtol=1e-6, dense_output=True)

    err_native = np.abs(native.y_at(t) - exact).max()
    err_hermite = np.abs(fallback.y_at(t) - exact).max()
    assert err_native < err_hermite, (
        f"native interpolant ({err_native:.2e}) should beat Hermite "
        f"({err_hermite:.2e})"
    )


def test_scalar_and_array_evaluation_agree():
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-8, dense_output=True)

    times = [0.5, 1.7, 3.3, 5.9]
    stacked = sol.y_at(np.array(times))
    for j, t in enumerate(times):
        single = sol.y_at(t)
        assert single.shape == (2,)
        assert np.array_equal(single, stacked[:, j])


def test_evaluation_order_does_not_matter():
    """Query points are matched to segments individually, not assumed sorted."""
    bench = lotka_volterra()
    sol = solve(bench.problem, rtol=1e-8, dense_output=True)

    t = np.array([9.1, 0.4, 14.0, 3.3, 7.7])
    shuffled = sol.y_at(t)
    one_by_one = np.stack([sol.y_at(ti) for ti in t], axis=-1)
    assert np.array_equal(shuffled, one_by_one)


def test_out_of_range_raises():
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-6, dense_output=True)
    with pytest.raises(ValueError, match="outside the solved interval"):
        sol.y_at(100.0)
    with pytest.raises(ValueError, match="outside the solved interval"):
        sol.y_at(-5.0)


def test_endpoints_are_evaluable():
    """Both ends of the interval must be in range despite floating-point edges."""
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-8, dense_output=True)
    assert np.allclose(sol.y_at(sol.sol.t_min), bench.problem.y0, atol=1e-12)
    assert np.allclose(sol.y_at(sol.sol.t_max), sol.y[:, -1], atol=1e-10)


def test_dense_output_backward():
    """Segments are stored in integration order; backward solves must still index."""
    bench = sine_cosine()
    back = ODEProblem(f=bench.problem.f_user, t_span=(6.0, 0.0), y0=bench.exact(6.0))
    sol = solve(back, rtol=1e-10, atol=1e-13, dense_output=True)

    t = np.linspace(0.5, 5.5, 211)
    err = np.abs(sol.y_at(t) - bench.exact(t)).max()
    assert err < 1e-7, f"backward dense output error {err:.3e}"


def test_no_dense_output_raises():
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-6)
    assert sol.sol is None
    with pytest.raises(RuntimeError, match="dense_output=True"):
        sol.y_at(1.0)


def test_dense_output_segment_count():
    bench = sine_cosine()
    sol = solve(bench.problem, rtol=1e-8, dense_output=True)
    assert len(sol.sol) == sol.stats.naccepted
    assert "DenseOutput" in repr(sol.sol)


# ---------------------------------------------------------------------------
# The Hermite interpolant in isolation
# ---------------------------------------------------------------------------


def test_hermite_reproduces_endpoints_and_slopes():
    """Cubic Hermite must match value *and* derivative at both ends."""
    y0, f0 = np.array([1.0, -2.0]), np.array([0.5, 3.0])
    y1, f1 = np.array([2.0, 1.0]), np.array([-1.0, 0.25])
    ip = HermiteInterpolant(1.0, y0, f0, 3.0, y1, f1)

    assert np.allclose(ip(1.0), y0)
    assert np.allclose(ip(3.0), y1)

    eps = 1e-6
    slope0 = (ip(1.0 + eps) - ip(1.0)) / eps
    slope1 = (ip(3.0) - ip(3.0 - eps)) / eps
    assert np.allclose(slope0, f0, atol=1e-4)
    assert np.allclose(slope1, f1, atol=1e-4)


def test_hermite_is_exact_on_cubics():
    """A cubic Hermite interpolant reproduces any cubic exactly."""

    def poly(t):
        return np.array([2 * t**3 - t**2 + 4 * t - 1])

    def dpoly(t):
        return np.array([6 * t**2 - 2 * t + 4])

    ip = HermiteInterpolant(0.0, poly(0.0), dpoly(0.0), 2.0, poly(2.0), dpoly(2.0))
    for t in np.linspace(0.0, 2.0, 25):
        assert ip(t)[0] == pytest.approx(poly(t)[0], abs=1e-12)
