"""Radau IIA specifics: spectral data, the split solve, and collocation output."""

from __future__ import annotations

import time

import numpy as np
import pytest

from odesuite import solve
from odesuite.linalg import lu_factorize, mass_minus_jacobian
from odesuite.problems import (
    linear_dae,
    linear_system,
    logistic,
    lotka_volterra,
    robertson,
    sine_cosine,
    van_der_pol,
)
from odesuite.steppers.irk import RADAU_IIA_5, RadauIIA, _lagrange_basis, _spectral_data

# ---------------------------------------------------------------------------
# The tableau
# ---------------------------------------------------------------------------


def test_collocation_coefficients():
    """Row sums, abscissae and stiff accuracy of three-stage Radau IIA."""
    tab = RADAU_IIA_5
    s6 = np.sqrt(6.0)

    assert np.allclose(tab.c, [(4 - s6) / 10, (4 + s6) / 10, 1.0])
    assert tab.c[-1] == 1.0, "Radau IIA must include the right endpoint"
    # Collocation consistency: row sums of A are the abscissae.
    assert np.allclose(tab.A.sum(axis=1), tab.c)
    # Stiffly accurate: the weights are the last row of A.
    assert np.allclose(tab.b, tab.A[-1])
    assert tab.b.sum() == pytest.approx(1.0)


def test_quadrature_order():
    """The Radau IIA quadrature integrates polynomials up to degree 2s-2 exactly.

    For three stages that is degree 4, which is what underwrites the order-5
    claim. Checking it here means the order claim rests on the coefficients, not
    only on an observed convergence slope.
    """
    tab = RADAU_IIA_5
    for degree in range(2 * tab.n_stages - 1):
        quadrature = tab.b @ tab.c**degree
        assert quadrature == pytest.approx(1.0 / (degree + 1), abs=1e-13), (
            f"quadrature fails at degree {degree}"
        )


def test_spectral_data_matches_published_values():
    """`T` and its inverse are computed, not transcribed -- but must still be right.

    The eigenvalues of ``A^-1`` have closed forms in Hairer & Wanner; agreeing
    with them to machine precision confirms the eigendecomposition ordering and
    removes the transcription risk that hardcoding `T` and `TI` would carry.
    """
    values, T, TI = _spectral_data(RADAU_IIA_5.A)

    mu_real = 3 + 3 ** (2 / 3) - 3 ** (1 / 3)
    mu_complex = (
        3 + 0.5 * (3 ** (1 / 3) - 3 ** (2 / 3)) - 0.5j * (3 ** (5 / 6) + 3 ** (7 / 6))
    )

    assert values[0].imag == pytest.approx(0.0, abs=1e-14)
    assert values[0].real == pytest.approx(mu_real, abs=1e-12)

    # `_spectral_data` orders the conjugate pair with positive imaginary part
    # first; the published constant is quoted with the negative one. Either
    # member may be used for the complex block -- the other is its conjugate and
    # is never solved for -- so the pair is compared without regard to sign.
    assert values[1] == pytest.approx(np.conj(mu_complex), abs=1e-12)
    assert values[2] == pytest.approx(mu_complex, abs=1e-12)
    assert values[1].imag > 0 > values[2].imag

    assert np.allclose(TI @ T, np.eye(3), atol=1e-12)
    assert np.allclose(T @ np.diag(values) @ TI, np.linalg.inv(RADAU_IIA_5.A), atol=1e-12)


def test_lagrange_basis_partition_of_unity():
    nodes = np.array([0.0, 0.3, 0.7, 1.0])
    x = np.linspace(-0.5, 1.8, 17)
    basis = _lagrange_basis(nodes, x)
    assert np.allclose(basis.sum(axis=0), 1.0)
    # Cardinality: L_j(x_k) == delta_jk
    assert np.allclose(_lagrange_basis(nodes, nodes), np.eye(4), atol=1e-13)


# ---------------------------------------------------------------------------
# split vs dense: the fast path validated against the obvious one
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "factory", [linear_system, logistic, sine_cosine, lotka_volterra, linear_dae],
    ids=lambda f: f.__name__,
)
def test_split_and_dense_solves_agree(factory):
    """The eigendecomposition split must reproduce the full 3n x 3n solve.

    This is what makes the fast path trustworthy. The dense path assembles
    ``(A^-1 (x) M)/h - I (x) J`` literally and factors it, so it is correct by
    construction but nine times the work; the split path exploits the spectrum
    of ``A^-1`` and is what actually ships.
    """
    bench = factory()
    split = solve(bench.problem, method="radau", rtol=1e-10, atol=1e-12)
    # Constructed directly rather than by name: the unsplit solve is this
    # test's oracle, not a method anyone should pick, so it is no longer in
    # the registry. This is the interface it was always a wrapper around.
    dense = solve(bench.problem, method=RadauIIA(linear_solve="dense"),
                  rtol=1e-10, atol=1e-12)

    assert split.success and dense.success
    assert np.allclose(split.y[:, -1], dense.y[:, -1], rtol=1e-6, atol=1e-8), (
        f"{bench.name}: split {split.y[:, -1]} vs dense {dense.y[:, -1]}"
    )


def test_split_and_dense_agree_step_for_step():
    """Tighter than the end-to-end check: identical output from a single step."""
    bench = linear_system()
    problem = bench.problem
    y0 = problem.y0.copy()
    f0 = problem.f(0.0, y0)

    split = RadauIIA(linear_solve="split")
    dense = RadauIIA(linear_solve="dense")
    for stepper in (split, dense):
        stepper.set_tolerances(1e-12, 1e-14)

    for h in (0.4, 0.1, 0.025):
        split._reset_cache()
        dense._reset_cache()
        a = split.step(problem, 0.0, y0, f0, h)
        b = dense.step(problem, 0.0, y0, f0, h)
        assert np.allclose(a.y_new, b.y_new, rtol=1e-11, atol=1e-13), (
            f"h={h}: split and dense diverge by {np.abs(a.y_new - b.y_new).max():.3e}"
        )


def _heat_equation(n: int = 60):
    """Method-of-lines heat equation: a stiff linear system of adjustable size."""
    dx = 1.0 / (n + 1)
    A = (
        np.diag(-2.0 * np.ones(n))
        + np.diag(np.ones(n - 1), 1)
        + np.diag(np.ones(n - 1), -1)
    ) / dx**2
    x = np.linspace(dx, 1 - dx, n)
    from odesuite import ODEProblem

    return ODEProblem(
        f=lambda t, y: A @ y, t_span=(0.0, 0.05), y0=np.sin(np.pi * x), jac=A
    )


def test_split_and_dense_solves_agree_on_a_large_system():
    """The two linear-solve paths are two ways to solve the same system.

    This is the assertion that makes the fast path trustworthy, and it is
    deterministic -- no timing involved.
    """
    problem = _heat_equation(60)
    split = solve(problem, method="radau", rtol=1e-8, atol=1e-10)
    dense = solve(problem, method=RadauIIA(linear_solve="dense"),
                  rtol=1e-8, atol=1e-10)

    assert split.success and dense.success
    assert np.allclose(split.y[:, -1], dense.y[:, -1], rtol=1e-6, atol=1e-9)
    assert split.stats.naccepted == dense.stats.naccepted


def _best_of(work, repeats: int = 9) -> float:
    """Minimum wall time over `repeats` calls.

    The minimum rather than the mean because the noise is one-sided: a run can
    be slowed by the machine but never sped up below the work it has to do.
    """
    best = float("inf")
    for _ in range(repeats):
        started = time.perf_counter()
        work()
        best = min(best, time.perf_counter() - started)
    return best


def _complex_lu_is_pathological(n: int = 80) -> bool:
    """True when this machine's BLAS has a badly slow complex `getrf`.

    Not hypothetical: the OpenBLAS shipped with numpy 2.2.6 on this Windows
    machine factors a complex 120x120 matrix in ~230 ms against ~0.17 ms for the
    real one of the same size -- a factor of 1300, reproducible with
    `numpy.linalg.inv` and unrelated to this library. Where that is true the
    split path is *slower* than the dense one, and the test below is measuring
    the BLAS rather than the algorithm, so it skips instead of failing.
    """
    rng = np.random.default_rng(0)
    real = rng.normal(size=(n, n))
    complex_ = real + 1j * rng.normal(size=(n, n))
    return _best_of(lambda: lu_factorize(complex_), 3) > 20 * _best_of(
        lambda: lu_factorize(real), 3
    )


@pytest.mark.slow
def test_the_split_factorisation_is_cheaper_than_the_dense_one():
    """One real plus one complex n x n factorisation beats one 3n x 3n.

    Timed at the factorisation rather than through a whole solve. Through a
    solve the advantage is diluted to about 1.5x by the triangular solves and
    the T/TI transforms, which is small enough that eight parallel pytest
    workers can invert it; measured directly it is ~9x, and a ratio is robust to
    load in a way an absolute comparison is not, because contention slows both
    arms together.

    The advantage is asymptotic in `n` and genuinely does not exist for small
    systems -- at n=40 the two are level, because a 120x120 dense factorisation
    is cheaper than the overhead of complex arithmetic.
    """
    if _complex_lu_is_pathological():
        pytest.skip("this machine's BLAS has a pathologically slow complex getrf")

    n = 80
    h = 1e-4
    stepper = RadauIIA()
    A = _heat_equation(n).jac(0.0, np.zeros(n))

    def split():
        lu_factorize(mass_minus_jacobian(None, A, stepper.eigenvalues[0].real / h))
        lu_factorize(mass_minus_jacobian(None, A, stepper.eigenvalues[1] / h))

    big = np.kron(stepper.A_inv / h, np.eye(n)) - np.kron(np.eye(3), A)

    split_time = _best_of(split)
    dense_time = _best_of(lambda: lu_factorize(big))

    assert dense_time > 2.0 * split_time, (
        f"split {split_time * 1e3:.3f}ms vs dense(3n={3 * n}) "
        f"{dense_time * 1e3:.3f}ms -- expected the split path to win clearly"
    )


def test_invalid_linear_solve_rejected():
    with pytest.raises(ValueError, match="split.*dense"):
        RadauIIA(linear_solve="banana")


# ---------------------------------------------------------------------------
# Newton machinery
# ---------------------------------------------------------------------------


def test_newton_failure_is_reported_not_hidden():
    """A step the Newton iteration cannot solve must return ok=False.

    The driver responds by halving h. Silently returning an unconverged answer
    would corrupt the solution with no diagnostic at all.
    """
    bench = van_der_pol(mu=1000.0)
    stepper = RadauIIA()
    stepper.set_tolerances(1e-10, 1e-12)
    problem = bench.problem
    y0 = problem.y0.copy()

    # A single step spanning the entire interval: Newton cannot possibly solve
    # the stage equations for a relaxation oscillator over 3000 time units.
    result = stepper.step(problem, 0.0, y0, problem.f(0.0, y0), 3000.0)
    assert not result.ok


def test_extrapolation_predictor_beats_a_cold_start():
    """The collocation-polynomial predictor is why Robertson is affordable.

    Disabling it (forcing every step to start from Z = 0) measurably increases
    the work, which is the evidence that the predictor is doing its job.
    """
    bench = robertson()

    warm = solve(bench.problem, method="radau", rtol=1e-6, atol=1e-10)

    class ColdStart(RadauIIA):
        def _predict(self, h, n):
            return np.zeros((self.tab.n_stages, n))

    cold = solve(bench.problem, method=ColdStart(), rtol=1e-6, atol=1e-10)

    assert warm.success and cold.success
    assert warm.stats.nfev < cold.stats.nfev, (
        f"predictor saved nothing: warm {warm.stats.nfev} vs cold {cold.stats.nfev}"
    )


# ---------------------------------------------------------------------------
# Collocation dense output
# ---------------------------------------------------------------------------


def test_collocation_dense_output_accuracy():
    """Radau's continuous extension is the collocation polynomial itself."""
    bench = sine_cosine()
    sol = solve(
        bench.problem, method="radau", rtol=1e-10, atol=1e-12, dense_output=True
    )
    t = np.linspace(0.0, bench.problem.tf, 501)
    err = np.abs(sol.y_at(t) - bench.exact(t)).max()
    assert err < 1e-7, f"dense output error {err:.3e}"


def test_dense_output_matches_step_values():
    bench = logistic()
    sol = solve(
        bench.problem, method="radau", rtol=1e-9, atol=1e-11, dense_output=True
    )
    assert np.allclose(sol.y_at(sol.t), sol.y, atol=1e-10)


def test_collocation_output_is_exact_at_stage_points():
    """By construction the polynomial passes through y0 and every stage value."""
    bench = logistic()
    problem = bench.problem
    stepper = RadauIIA()
    stepper.set_tolerances(1e-12, 1e-14)

    y0 = problem.y0.copy()
    f0 = problem.f(0.0, y0)
    h = 0.25
    result = stepper.step(problem, 0.0, y0, f0, h)
    interp = stepper.interpolant(0.0, y0, f0, h, result.y_new, None)

    assert np.allclose(interp(0.0), y0, atol=1e-14)
    for i, c in enumerate(RADAU_IIA_5.c):
        assert np.allclose(interp(c * h), y0 + stepper._Z[i], atol=1e-12)
