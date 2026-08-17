"""Mass matrices and index-1 differential-algebraic systems.

Supporting ``M y' = f(t, y)`` throughout, rather than only ``y' = f``, is what
makes DAEs nearly free: a singular `M` turns the same code path into an index-1
DAE solver with no special-casing beyond requiring stiff accuracy.
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from odesuite import ODEProblem, solve
from odesuite.problems import linear_dae, mass_matrix_oscillator, robertson, robertson_dae
from odesuite.steppers.rosenbrock import RODAS4, Rosenbrock

DAE_METHODS = ["radau", "rodas4"]


# ---------------------------------------------------------------------------
# Problem-level classification
# ---------------------------------------------------------------------------


def test_singular_mass_matrix_is_detected():
    assert robertson_dae().problem.is_dae
    assert linear_dae().problem.is_dae
    assert not mass_matrix_oscillator().problem.is_dae
    assert not robertson().problem.is_dae


def test_mass_matrix_shape_is_validated():
    with pytest.raises(ValueError, match="mass must have shape"):
        ODEProblem(
            f=lambda t, y: -y, t_span=(0, 1), y0=[1.0, 2.0], mass=np.eye(3)
        )


def test_explicit_methods_refuse_a_mass_matrix():
    bench = mass_matrix_oscillator()
    for method in ("dopri5", "tsit5", "rk23"):
        with pytest.raises(ValueError, match="mass matrix"):
            solve(bench.problem, method=method)


def test_non_stiffly_accurate_rosenbrock_refuses_a_dae():
    """Stiff accuracy is a hard requirement for a DAE, not a preference.

    Without it the algebraic constraint is only approximated at the end of the
    step and the solution drifts off the manifold.
    """
    not_stiffly_accurate = dataclasses.replace(
        RODAS4, name="Perturbed", b=RODAS4.b * 1.01
    )
    assert not not_stiffly_accurate.stiffly_accurate

    with pytest.raises(ValueError, match="stiffly accurate"):
        solve(linear_dae().problem, method=Rosenbrock(not_stiffly_accurate))

    # ...and the same method is fine on a plain ODE.
    from odesuite.problems import logistic

    solve(logistic().problem, method=Rosenbrock(not_stiffly_accurate), rtol=1e-6)


# ---------------------------------------------------------------------------
# Non-singular mass matrix
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", DAE_METHODS)
def test_non_singular_mass_matrix(method):
    """``M y' = A y`` must match ``expm(M^-1 A t) y0``."""
    bench = mass_matrix_oscillator()
    sol = solve(bench.problem, method=method, rtol=1e-10, atol=1e-12)

    assert sol.success, sol.message
    err = np.linalg.norm(sol.y[:, -1] - bench.exact_at_end())
    assert err < 1e-8, f"{method}: endpoint error {err:.3e}"


@pytest.mark.parametrize("method", DAE_METHODS)
def test_mass_matrix_dense_output(method):
    """Continuous output under a mass matrix needs M^-1 f as the slope, not f."""
    bench = mass_matrix_oscillator()
    sol = solve(
        bench.problem, method=method, rtol=1e-10, atol=1e-12, dense_output=True
    )
    t = np.linspace(0.0, bench.problem.tf, 301)
    err = np.abs(sol.y_at(t) - bench.exact(t)).max()
    assert err < 1e-6, f"{method}: dense output error {err:.3e}"


def test_mass_matrix_equals_transformed_problem():
    """``M y' = A y`` and ``y' = M^-1 A y`` must give the same trajectory."""
    bench = mass_matrix_oscillator()
    M = bench.problem.mass
    A = np.array([[-1.0, 2.0], [-3.0, -1.0]])
    transformed = ODEProblem(
        f=lambda t, y: np.linalg.solve(M, A @ y),
        t_span=(0.0, bench.problem.tf),
        y0=bench.problem.y0,
    )

    with_mass = solve(bench.problem, method="radau", rtol=1e-11, atol=1e-13)
    without = solve(transformed, method="dopri5", rtol=1e-11, atol=1e-13)
    assert np.allclose(with_mass.y[:, -1], without.y[:, -1], atol=1e-8)


# ---------------------------------------------------------------------------
# Index-1 DAE with a known solution
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", DAE_METHODS)
def test_linear_dae_matches_analytic_solution(method):
    bench = linear_dae()
    sol = solve(bench.problem, method=method, rtol=1e-10, atol=1e-12)

    assert sol.success, sol.message
    err = np.linalg.norm(sol.y[:, -1] - bench.exact_at_end())
    assert err < 1e-8, f"{method}: endpoint error {err:.3e}"


@pytest.mark.parametrize("method", DAE_METHODS)
def test_algebraic_constraint_holds_exactly(method):
    """The constraint ``y1 + y2 - t == 0`` is imposed, not approximated.

    A stiffly accurate method enforces it at every accepted step, so the
    residual sits at round-off rather than at the integration tolerance.
    """
    bench = linear_dae()
    sol = solve(bench.problem, method=method, rtol=1e-8, atol=1e-10)
    residual = np.abs(sol.y[0] + sol.y[1] - sol.t).max()
    assert residual < 1e-12, f"{method}: constraint violated by {residual:.3e}"


@pytest.mark.parametrize("method", DAE_METHODS)
def test_dae_dense_output_is_not_silently_wrong(method):
    """Between steps as well as at them.

    A cubic Hermite built from `f` looks fine at the nodes and is badly wrong in
    between, because for the algebraic components `f` is a constraint residual
    near zero rather than a derivative. This test is what catches that.
    """
    bench = linear_dae()
    sol = solve(
        bench.problem, method=method, rtol=1e-10, atol=1e-12, dense_output=True
    )
    t = np.linspace(0.05, bench.problem.tf - 0.05, 401)
    err = np.abs(sol.y_at(t) - bench.exact(t)).max()
    endpoint = np.linalg.norm(sol.y[:, -1] - bench.exact_at_end())

    assert err < 1e-4, f"{method}: dense output error {err:.3e}"
    assert err < 1e6 * max(endpoint, 1e-14), (
        f"{method}: dense error {err:.3e} is wildly worse than the endpoint "
        f"error {endpoint:.3e}, which means the interpolant is wrong rather "
        f"than merely low order"
    )


# ---------------------------------------------------------------------------
# Robertson in DAE form
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", DAE_METHODS)
def test_robertson_dae_conserves_mass_exactly(method):
    """In DAE form conservation is structural, not a numerical accident.

    The ODE form conserves mass to within the integration tolerance; here the
    conservation law *is* one of the equations, so it holds to round-off.
    """
    bench = robertson_dae()
    sol = solve(bench.problem, method=method, rtol=1e-6, atol=1e-10)

    assert sol.success, sol.message
    assert sol.t[-1] == pytest.approx(1e11)
    drift = np.abs(sol.y.sum(axis=0) - 1.0).max()
    assert drift < 1e-12, f"{method}: mass drifted by {drift:.3e}"


@pytest.mark.parametrize("method", DAE_METHODS)
def test_robertson_dae_matches_ode_form(method):
    """The two formulations describe the same chemistry and must agree."""
    dae = solve(robertson_dae().problem, method=method, rtol=1e-7, atol=1e-11)
    ode = solve(robertson().problem, method=method, rtol=1e-7, atol=1e-11)

    assert dae.success and ode.success
    assert np.allclose(dae.y[:, -1], ode.y[:, -1], atol=1e-9), (
        f"{method}: DAE {dae.y[:, -1]} vs ODE {ode.y[:, -1]}"
    )


@pytest.mark.parametrize("method", DAE_METHODS)
def test_dae_with_finite_difference_jacobian(method):
    """DAEs must also work without an analytic Jacobian."""
    bench = linear_dae()
    prob = ODEProblem(
        f=bench.problem.f_user,
        t_span=(bench.problem.t0, bench.problem.tf),
        y0=bench.problem.y0,
        mass=bench.problem.mass,
    )
    sol = solve(prob, method=method, rtol=1e-9, atol=1e-11)
    assert sol.success, sol.message
    assert np.allclose(sol.y[:, -1], bench.exact_at_end(), atol=1e-7)


def test_dae_backward_integration():
    """Time reversal must work for DAEs too."""
    bench = linear_dae()
    forward = solve(bench.problem, method="radau", rtol=1e-11, atol=1e-13)

    back = ODEProblem(
        f=bench.problem.f_user,
        t_span=(bench.problem.tf, bench.problem.t0),
        y0=forward.y[:, -1],
        mass=bench.problem.mass,
        jac=bench.problem._jac_user,
    )
    reverse = solve(back, method="radau", rtol=1e-11, atol=1e-13)
    assert np.allclose(reverse.y[:, -1], bench.problem.y0, atol=1e-7)
