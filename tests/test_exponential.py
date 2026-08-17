"""ETDRK4 and the phi functions it depends on."""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import ODEProblem, solve
from odesuite.problems import allen_cahn, kuramoto_sivashinsky
from odesuite.steppers.exponential import (
    ETDRK4,
    phi1_naive,
    phi_coefficients_contour,
    semilinear_problem,
)


def phi1_reference(z: float) -> float:
    """``(e^z - 1)/z`` computed stably: series for small z, direct otherwise."""
    if abs(z) > 1e-3:
        return float((np.exp(z) - 1.0) / z)
    # Taylor series, which is exactly what the direct formula fails to resolve.
    total, term = 1.0, 1.0
    for k in range(1, 20):
        term *= z / (k + 1)
        total += term
    return total


# ---------------------------------------------------------------------------
# The phi functions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("z", [-1e-12, -1e-10, -1e-8, -1e-6, -1e-4, -1e-2, -1.0, -100.0])
def test_contour_phi_is_accurate_everywhere(z):
    """Contour evaluation must be exact across twelve orders of magnitude in z.

    A spectral discretisation produces modes spanning exactly this range in one
    array, so accuracy at both extremes simultaneously is the requirement --
    not accuracy somewhere.
    """
    # With h = 2 and hL = 2z, the routine's Q is (h/2) phi1(hL/2) = phi1(z).
    Q, _, _, _ = phi_coefficients_contour(np.array([2.0 * z]), 2.0)
    reference = phi1_reference(z)
    assert Q[0] == pytest.approx(reference, rel=1e-12), (
        f"contour phi1({z}) = {Q[0]!r} vs reference {reference!r}"
    )


def test_naive_phi_loses_precision_where_contour_does_not():
    """The reason the contour trick is in the library at all.

    ``(e^z - 1)/z`` at small ``|z|`` subtracts two numbers that agree to
    fifteen digits and divides by a small one. At ``z = 1e-12`` it retains
    roughly four correct digits; the contour form retains all of them.
    """
    z = -1e-12
    reference = phi1_reference(z)

    naive_error = abs(phi1_naive(z).real - reference) / abs(reference)
    Q, _, _, _ = phi_coefficients_contour(np.array([2.0 * z]), 2.0)
    contour_error = abs(Q[0] - reference) / abs(reference)

    assert naive_error > 1e-6, (
        "the naive formula was expected to lose precision here; if it no "
        "longer does, this test is no longer demonstrating anything"
    )
    assert contour_error < 1e-14
    assert naive_error / max(contour_error, 1e-18) > 1e6


def test_phi_coefficients_have_the_right_limits():
    """As ``z -> 0`` the ETDRK4 coefficients approach the classical RK4 weights.

    In that limit the exponential integrator must degenerate to an ordinary
    fourth-order Runge-Kutta method, which fixes the normalisation of all four
    coefficient vectors at once.
    """
    h = 0.1
    Q, f1, f2, f3 = phi_coefficients_contour(np.array([-1e-13]), h)
    assert Q[0] == pytest.approx(h / 2, rel=1e-9)
    assert f1[0] == pytest.approx(h / 6, rel=1e-6)
    assert f2[0] == pytest.approx(h / 6, rel=1e-6)
    assert f3[0] == pytest.approx(h / 6, rel=1e-6)


def test_more_contour_points_do_not_change_the_answer():
    """32 points already saturate; the integral is not being under-resolved."""
    z = np.array([-1e-10, -1.0, -50.0])
    a = phi_coefficients_contour(z, 1.0, 32)
    b = phi_coefficients_contour(z, 1.0, 128)
    for x, y in zip(a, b):
        assert np.allclose(x, y, rtol=1e-12, atol=1e-15)


# ---------------------------------------------------------------------------
# ETDRK4
# ---------------------------------------------------------------------------


def test_exact_on_a_purely_linear_problem():
    """With ``N = 0`` the method reduces to ``exp(hL)``, which is exact.

    A strong check on the ``E`` coefficient and the overall structure: any error
    in the linear part shows up immediately because the true answer is known in
    closed form.
    """
    L = np.array([-1000.0, -10.0, -0.1, 0.5])
    u0 = np.array([1.0, 2.0, -1.0, 0.5])
    problem = semilinear_problem(L, lambda t, u: np.zeros_like(u), (0.0, 2.0), u0)

    sol = solve(problem, method="etdrk4", n_steps=8)
    assert np.allclose(sol.y[:, -1], u0 * np.exp(2.0 * L), rtol=1e-12, atol=1e-14)


def test_stiffness_does_not_restrict_the_step():
    """The defining property: ``h`` is limited by accuracy, never by stability.

    The linear part here has a spectral radius of 1e6, so an explicit method
    would need ``h < 2e-6`` -- a million steps. ETDRK4 takes ten.
    """
    L = np.array([-1e6, -1e3, -1.0])
    u0 = np.array([1.0, 1.0, 1.0])
    problem = semilinear_problem(L, lambda t, u: np.zeros_like(u), (0.0, 1.0), u0)

    sol = solve(problem, method="etdrk4", n_steps=10)
    assert sol.success
    assert np.all(np.isfinite(sol.y[:, -1]))
    assert np.allclose(sol.y[:, -1], u0 * np.exp(L), rtol=1e-10, atol=1e-14)


def test_fourth_order_convergence_on_allen_cahn():
    bench = allen_cahn(n_modes=64, epsilon=0.01, t_end=2.0)
    reference = solve(bench.problem, method="dopri5", rtol=1e-13, atol=1e-15)
    u_ref = bench.to_real(reference.y[:, -1])

    errors = []
    for n in (100, 200, 400):
        sol = solve(bench.problem, method="etdrk4", n_steps=n)
        errors.append(np.abs(bench.to_real(sol.y[:, -1]) - u_ref).max())

    slope = np.log(errors[-2] / errors[-1]) / np.log(2.0)
    assert slope == pytest.approx(4.0, abs=0.5), (
        f"ETDRK4 order {slope:.2f}; errors={['%.2e' % e for e in errors]}"
    )


def test_agrees_with_an_explicit_method_on_a_mild_problem():
    """Cross-validation: where an explicit method is affordable, they must agree."""
    bench = allen_cahn(n_modes=64, epsilon=0.01, t_end=2.0)
    etd = solve(bench.problem, method="etdrk4", n_steps=2000)
    rk = solve(bench.problem, method="dopri5", rtol=1e-12, atol=1e-14)
    assert np.allclose(
        bench.to_real(etd.y[:, -1]), bench.to_real(rk.y[:, -1]), atol=1e-9
    )


def test_beats_explicit_methods_on_a_stiff_spectral_problem():
    """The showcase claim, measured.

    Kuramoto-Sivashinsky at 256 modes has ``|L|max ~ 4000``, so an explicit
    method is stability-bound at ``h ~ 5e-4``. ETDRK4 is not, and needs an order
    of magnitude fewer steps for comparable accuracy.
    """
    bench = kuramoto_sivashinsky(n_modes=256, t_end=10.0)
    reference = solve(bench.problem, method="etdrk4", n_steps=20_000)
    u_ref = bench.to_real(reference.y[:, -1])

    etd = solve(bench.problem, method="etdrk4", n_steps=1000)
    rk = solve(bench.problem, method="dopri5", rtol=1e-6, atol=1e-8, max_steps=200_000)

    assert etd.success and rk.success
    etd_error = np.abs(bench.to_real(etd.y[:, -1]) - u_ref).max()
    assert etd_error < 1e-6, f"ETDRK4 error {etd_error:.3e}"
    assert etd.stats.naccepted < 0.2 * rk.stats.naccepted, (
        f"ETDRK4 used {etd.stats.naccepted} steps against DOPRI5's "
        f"{rk.stats.naccepted}; expected a large advantage"
    )


def test_kuramoto_sivashinsky_stays_on_its_attractor():
    """Long-run qualitative check on the chaotic showcase problem.

    KS is chaotic, so pointwise accuracy is meaningless past a short horizon.
    What must hold is that the solution stays bounded on the attractor and
    conserves the spatial mean, which the equation implies exactly.
    """
    bench = kuramoto_sivashinsky(n_modes=128, t_end=60.0)
    sol = solve(bench.problem, method="etdrk4", n_steps=6000)
    u = bench.to_real(sol.y)

    assert sol.success
    assert np.all(np.isfinite(u))
    assert np.abs(u).max() < 10.0, "solution left the attractor"
    assert np.abs(u).max() > 1.0, "solution collapsed to the trivial state"
    # u_t is a total derivative, so the spatial mean is conserved at zero.
    assert np.abs(u.mean(axis=0)).max() < 1e-10


def test_complex_state_is_not_silently_truncated():
    """Spectral states are complex; nothing may quietly discard the imaginary part.

    A regression guard: the finite-difference Jacobian and Radau's stage arrays
    were both allocated as real and were truncating complex states on
    assignment, which produced plausible-looking but wrong answers.
    """
    bench = allen_cahn(n_modes=32, epsilon=0.01, t_end=0.5)
    assert np.iscomplexobj(bench.problem.y0)

    etd = solve(bench.problem, method="etdrk4", n_steps=500)
    rk = solve(bench.problem, method="dopri5", rtol=1e-11, atol=1e-13)
    radau = solve(bench.problem, method="radau", rtol=1e-9, atol=1e-11)

    for name, sol in (("etdrk4", etd), ("dopri5", rk), ("radau", radau)):
        assert np.iscomplexobj(sol.y), f"{name} lost the complex dtype"
        assert np.allclose(
            bench.to_real(sol.y[:, -1]), bench.to_real(rk.y[:, -1]), atol=1e-6
        ), f"{name} disagrees with the explicit reference"


# ---------------------------------------------------------------------------
# Problem construction and validation
# ---------------------------------------------------------------------------


def test_semilinear_problem_is_a_normal_ivp():
    bench = allen_cahn(n_modes=32, t_end=1.0)
    for method in ("dopri5", "tsit5"):
        sol = solve(bench.problem, method=method, rtol=1e-10, atol=1e-12)
        assert sol.success


def test_etdrk4_rejects_a_problem_without_a_splitting():
    problem = ODEProblem(f=lambda t, y: -y, t_span=(0.0, 1.0), y0=[1.0])
    with pytest.raises(ValueError, match="semilinear splitting"):
        solve(problem, method="etdrk4", n_steps=10)


def test_mismatched_operator_shape_raises():
    with pytest.raises(ValueError, match="linear operator diagonal has shape"):
        semilinear_problem(
            np.zeros(3), lambda t, u: u, (0.0, 1.0), np.zeros(4)
        )


def test_etdrk4_requires_a_fixed_step():
    bench = allen_cahn(n_modes=32, t_end=1.0)
    with pytest.raises(ValueError, match="fixed step size"):
        solve(bench.problem, method="etdrk4")


def test_coefficients_are_cached_across_steps():
    """Coefficients depend only on h, so they must be built once per solve."""
    bench = allen_cahn(n_modes=32, t_end=1.0)
    stepper = ETDRK4()
    stepper.validate(bench.problem)
    y = bench.problem.y0

    stepper.step(bench.problem, 0.0, y, None, 0.01)
    first = stepper._coefficients
    stepper.step(bench.problem, 0.01, y, None, 0.01)
    assert stepper._coefficients is first, "coefficients were rebuilt needlessly"

    stepper.step(bench.problem, 0.02, y, None, 0.02)
    assert stepper._coefficients is not first, "a changed h must rebuild them"


def test_costs_four_nonlinear_evaluations_per_step():
    bench = allen_cahn(n_modes=32, t_end=1.0)
    sol = solve(bench.problem, method="etdrk4", n_steps=100)
    assert sol.stats.nfev / sol.stats.nsteps == pytest.approx(4.0, abs=0.2)
