"""Linear stability functions and regions.

The fast batched route and the run-the-stepper route must agree: one is a
closed-form determinant, the other actually integrates the Dahlquist problem,
and they share no code. Agreement is therefore strong evidence for both.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite.stability import (
    REAL_AXIS_LIMITS,
    _tableau_for,
    classify_stability,
    stability_function,
    stability_grid,
    tableau_stability_function,
)
from odesuite.tableaux import TABLEAUX

TABLEAU_METHODS = ["rk23", "rkf45", "cashkarp", "dopri5", "tsit5", "radau"]

SAMPLES = np.array(
    [0.0, -0.5, -2.5 + 0.7j, -0.3 - 1.2j, 0.4, -8.0 + 3.0j, -1e-3, -40.0 + 12.0j]
)


@pytest.mark.parametrize("method", TABLEAU_METHODS)
def test_fast_path_matches_running_the_stepper(method):
    """Closed form against the real integrator, on the same points."""
    fast = tableau_stability_function(_tableau_for(method), SAMPLES)
    stepped = stability_function(method, SAMPLES)
    assert np.allclose(fast, stepped, rtol=1e-8, atol=1e-9), (
        f"{method}: {np.abs(fast - stepped).max():.3e} apart"
    )


def test_r_at_zero_is_one():
    """``R(0) = 1``: a zero step changes nothing."""
    for method in TABLEAU_METHODS + ["rodas4"]:
        value = stability_function(method, np.array([0.0 + 0.0j]))[0]
        assert abs(value - 1.0) < 1e-10, f"{method}: R(0) = {value}"


@pytest.mark.parametrize("method", ["rk23", "rkf45", "cashkarp", "dopri5", "tsit5"])
def test_explicit_stability_function_is_the_exponential_series(method):
    """An explicit method of order p matches ``exp(z)`` through ``z^p``.

    That is the order condition restated on the Dahlquist problem, so it is an
    independent check on the tableau: a coefficient error would break the
    agreement at the order it corrupts.
    """
    from math import factorial

    order = TABLEAUX[method].order
    z = np.array([0.02, 0.05, 0.1])
    values = tableau_stability_function(_tableau_for(method), z)
    truncated = sum(z**k / factorial(k) for k in range(order + 1))

    # Difference must be the next term, not something larger.
    residual = np.abs(values - truncated)
    assert np.all(residual < 5 * np.abs(z) ** (order + 1)), (
        f"{method}: R(z) departs from exp(z) before order {order}"
    )


@pytest.mark.parametrize(
    "method,expected", [(k.lower(), v) for k, v in REAL_AXIS_LIMITS.items()]
)
def test_real_axis_limits_match_published_values(method, expected):
    report = classify_stability(method)
    assert report["real_axis_limit"] == pytest.approx(expected, abs=0.05)


@pytest.mark.parametrize("method", ["radau", "rodas4"])
def test_implicit_methods_are_l_stable(method):
    report = classify_stability(method)
    assert report["A_stable"]
    assert report["L_stable"]
    assert report["R_at_minus_infinity"] < 1e-6


@pytest.mark.parametrize("method", ["rk23", "dopri5", "tsit5", "rkf45", "cashkarp"])
def test_explicit_methods_are_not_a_stable(method):
    """The other half of the claim; without it the classification proves nothing."""
    report = classify_stability(method)
    assert not report["A_stable"]
    assert np.isfinite(report["real_axis_limit"])
    assert report["R_at_minus_infinity"] > 1.0


def test_grid_shape_and_orientation():
    """``stability_grid`` returns ``(len(imaginary), len(real))``.

    Getting this transposed would silently produce a mirrored region, which is
    exactly the kind of error a picture does not reveal.
    """
    real = np.linspace(-4.0, 1.0, 23)
    imaginary = np.linspace(-3.0, 3.0, 17)
    grid = stability_grid("dopri5", real, imaginary)

    assert grid.shape == (17, 23)
    # Row j, column i must correspond to real[i] + 1j*imaginary[j].
    for j in (0, 8, 16):
        for i in (0, 11, 22):
            direct = abs(
                stability_function("dopri5", np.array([real[i] + 1j * imaginary[j]]))[0]
            )
            assert grid[j, i] == pytest.approx(direct, rel=1e-6)


def test_grid_is_symmetric_about_the_real_axis():
    """Real coefficients imply ``R(conj z) = conj R(z)``, so ``|R|`` is symmetric."""
    real = np.linspace(-4.0, 1.0, 31)
    imaginary = np.linspace(-3.0, 3.0, 31)
    grid = stability_grid("dopri5", real, imaginary)
    assert np.allclose(grid, grid[::-1, :], rtol=1e-10)


def test_stability_region_contains_the_origin_neighbourhood():
    """Every consistent method is stable for a small enough step."""
    for method in TABLEAU_METHODS:
        grid = stability_grid(
            method, np.linspace(-0.1, -0.01, 5), np.linspace(-0.05, 0.05, 5)
        )
        assert np.all(grid <= 1.0), f"{method} is unstable near the origin"


def test_rosenbrock_falls_back_to_stepping():
    """RODAS4 has no Butcher tableau, so the general path must handle it."""
    assert _tableau_for("rodas4") is None
    grid = stability_grid("rodas4", np.linspace(-30.0, 2.0, 9), np.linspace(-8.0, 8.0, 9))
    assert grid.shape == (9, 9)
    assert np.all(np.isfinite(grid))
    # Far into the left half-plane it is strongly damping.
    assert grid[4, 0] < 0.5
