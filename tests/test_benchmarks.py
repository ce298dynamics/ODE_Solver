"""The verification harness itself: stability classification and the problem zoo.

The benchmarks are part of the deliverable, so they get tested too -- a figure
that silently stops being generated, or a stability classification that quietly
changes, is a regression like any other.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from odesuite import solve
from odesuite.problems import BVPS, DAE, NONSTIFF, SEMILINEAR, SEPARABLE, STIFF, all_benchmarks
from odesuite.stability import (  # noqa: E402
    stability_function,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "benchmarks"))
from stability_regions import stability_summary  # noqa: E402

# ---------------------------------------------------------------------------
# Stability functions, measured by running the steppers
# ---------------------------------------------------------------------------


def test_stability_function_of_an_explicit_method_is_its_polynomial():
    """For an explicit RK method ``R(z)`` is a known polynomial.

    A fifth-order method reproduces ``sum z^k/k!`` through ``k = 5``; the sixth
    coefficient is method-specific. Checking the low-order terms confirms the
    measured `R` really is the stability function.
    """
    from math import factorial

    z = np.array([0.1, 0.2, 0.3])
    R = stability_function("dopri5", z.astype(complex)).real
    truncated = sum(z**k / factorial(k) for k in range(6))
    assert np.allclose(R, truncated, rtol=1e-6)


def test_stability_at_the_origin_is_one():
    for method in ("rk23", "dopri5", "radau", "rodas4"):
        R = stability_function(method, np.array([0.0 + 0.0j]))
        assert abs(R[0] - 1.0) < 1e-10, f"{method}: R(0) = {R[0]}"


@pytest.mark.parametrize(
    "method,expected", [("rk23", 2.51), ("dopri5", 3.31), ("rkf45", 3.67)]
)
def test_real_axis_stability_limits_match_published_values(method, expected):
    """The classical real-axis intervals, recovered by measurement."""
    report = stability_summary([method], verbose=False)
    assert report[method]["real_axis_limit"] == pytest.approx(expected, abs=0.1)


@pytest.mark.parametrize("method", ["radau", "rodas4"])
def test_implicit_methods_are_l_stable(method):
    """A-stable and ``R(z) -> 0`` at infinity: what tames Robertson."""
    report = stability_summary([method], verbose=False)
    assert report[method]["A_stable"], f"{method} is not A-stable"
    assert report[method]["L_stable"], f"{method} is not L-stable"
    assert report[method]["R_at_minus_infinity"] < 1e-6


@pytest.mark.parametrize("method", ["rk23", "dopri5", "tsit5"])
def test_explicit_methods_are_not_a_stable(method):
    """The other half of the claim -- otherwise the classification proves nothing."""
    report = stability_summary([method], verbose=False)
    assert not report[method]["A_stable"]
    assert np.isfinite(report[method]["real_axis_limit"])


# ---------------------------------------------------------------------------
# The problem zoo
# ---------------------------------------------------------------------------


def test_every_benchmark_constructs_and_is_integrable():
    """Each registered problem builds and takes at least a few steps."""
    for bench in all_benchmarks():
        problem = bench.problem
        assert problem.n > 0
        f0 = problem.f(problem.t0, problem.y0)
        assert f0.shape == problem.y0.shape, bench.name
        assert np.all(np.isfinite(f0)), bench.name


@pytest.mark.parametrize("factory", NONSTIFF, ids=lambda f: getattr(f, "__name__", "lambda"))
def test_nonstiff_benchmarks_solve(factory):
    bench = factory()
    sol = solve(bench.problem, method="dopri5", rtol=1e-8, atol=1e-10)
    assert sol.success, f"{bench.name}: {sol.message}"


@pytest.mark.parametrize("factory", STIFF, ids=lambda f: getattr(f, "__name__", "lambda"))
def test_stiff_benchmarks_solve_with_an_implicit_method(factory):
    bench = factory()
    sol = solve(bench.problem, method="radau", rtol=1e-6, atol=1e-9)
    assert sol.success, f"{bench.name}: {sol.message}"
    assert np.all(np.isfinite(sol.y[:, -1]))


@pytest.mark.parametrize("factory", DAE, ids=lambda f: getattr(f, "__name__", "lambda"))
def test_dae_benchmarks_solve(factory):
    bench = factory()
    sol = solve(bench.problem, method="radau", rtol=1e-7, atol=1e-10)
    assert sol.success, f"{bench.name}: {sol.message}"


@pytest.mark.parametrize("factory", SEPARABLE, ids=lambda f: getattr(f, "__name__", "lambda"))
def test_separable_benchmarks_solve_symplectically(factory):
    bench = factory()
    sol = solve(bench.problem, method="verlet", n_steps=5000)
    assert sol.success, f"{bench.name}: {sol.message}"


@pytest.mark.parametrize("factory", SEMILINEAR, ids=lambda f: getattr(f, "__name__", "lambda"))
def test_semilinear_benchmarks_solve_with_etdrk4(factory):
    bench = factory()
    sol = solve(bench.problem, method="etdrk4", n_steps=2000)
    assert sol.success, f"{bench.name}: {sol.message}"
    assert np.all(np.isfinite(sol.y[:, -1]))


@pytest.mark.parametrize("factory", BVPS, ids=lambda f: getattr(f, "__name__", "lambda"))
def test_bvp_benchmarks_solve(factory):
    from odesuite import solve_bvp

    bench = factory()
    sol = solve_bvp(bench.problem, bench.guess, n_nodes=10, rtol=1e-10, tol=1e-8)
    assert sol.converged, f"{bench.name}: {sol.message}"
    if bench.exact is not None:
        t = np.linspace(bench.problem.a, bench.problem.b, 101)
        assert np.abs(sol.y_at(t) - bench.exact(t)).max() < 1e-6


@pytest.mark.slow
def test_stiff_benchmarks_really_are_stiff():
    """An explicit method must struggle where an implicit one does not.

    Guards the benchmark set itself: a "stiff" problem an explicit method
    handles comfortably would make the stiff-solver comparisons meaningless.
    """
    from odesuite.problems import hires, orego, robertson

    for factory in (robertson, hires, orego):
        bench = factory()
        implicit = solve(bench.problem, method="radau", rtol=1e-6, atol=1e-9)
        explicit = solve(
            bench.problem, method="dopri5", rtol=1e-6, atol=1e-9, max_steps=30_000
        )
        assert implicit.success, bench.name
        assert explicit.stats.naccepted > 20 * implicit.stats.naccepted, (
            f"{bench.name} is not stiff enough to be a useful test: dopri5 used "
            f"{explicit.stats.naccepted} steps against radau's "
            f"{implicit.stats.naccepted}"
        )


def test_benchmark_metadata_is_consistent():
    for bench in all_benchmarks():
        assert bench.name
        assert bench.description
        if bench.has_exact:
            end = bench.exact_at_end()
            assert end.shape == bench.problem.y0.shape, bench.name
        if bench.invariant is not None:
            assert np.isfinite(bench.invariant(bench.problem.y0)), bench.name
