"""Forward parameter sensitivities, and the parameter fit they enable."""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import ODEProblem, forward_sensitivities, solve


# ---------------------------------------------------------------------------
# Test systems
# ---------------------------------------------------------------------------


def lotka_volterra_parts():
    """Predator-prey with all four rate constants exposed as parameters."""

    def f(t, y, p):
        return np.array(
            [p[0] * y[0] - p[1] * y[0] * y[1], -p[2] * y[1] + p[3] * y[0] * y[1]]
        )

    def jac(t, y, p):
        return np.array(
            [[p[0] - p[1] * y[1], -p[1] * y[0]], [p[3] * y[1], -p[2] + p[3] * y[0]]]
        )

    def dfdp(t, y, p):
        return np.array(
            [
                [y[0], -y[0] * y[1], 0.0, 0.0],
                [0.0, 0.0, -y[1], y[0] * y[1]],
            ]
        )

    return f, jac, dfdp


def central_difference_sensitivity(f, t_span, y0, p, index, h=None):
    """``dy(T)/dp_index`` by central differences on the whole solve."""
    h = h if h is not None else 1e-6 * max(abs(p[index]), 1.0)

    def endpoint(pv):
        prob = ODEProblem(f=lambda t, y: f(t, y, pv), t_span=t_span, y0=y0)
        return solve(prob, method="dopri5", rtol=1e-13, atol=1e-15).y[:, -1]

    plus, minus = p.copy(), p.copy()
    plus[index] += h
    minus[index] -= h
    return (endpoint(plus) - endpoint(minus)) / (2 * h)


# ---------------------------------------------------------------------------
# Correctness against finite differences
# ---------------------------------------------------------------------------


def test_sensitivities_match_central_differences():
    """The gate: ``dy/dp`` agrees with differencing the whole solve.

    Central differences are the independent oracle here, and they are the *less*
    accurate of the two -- limited to about ``h^2 + eps/h`` -- so agreement at
    this level is really a statement about the variational equations being
    right.
    """
    f, jac, dfdp = lotka_volterra_parts()
    p = np.array([1.5, 1.0, 3.0, 1.0])
    y0 = np.array([10.0, 5.0])
    t_span = (0.0, 4.0)

    result = forward_sensitivities(
        f, t_span, y0, p, jac=jac, dfdp=dfdp, method="radau", rtol=1e-12, atol=1e-14
    )
    assert result.success, result.message
    S = result.S_at_end()
    assert S.shape == (2, 4)

    for j in range(4):
        reference = central_difference_sensitivity(f, t_span, y0, p, j)
        assert np.allclose(S[:, j], reference, rtol=1e-5, atol=1e-6), (
            f"parameter {j}: sensitivities {S[:, j]} vs central diff {reference}"
        )


def test_finite_difference_fallbacks_agree_with_analytic_derivatives():
    """Omitting `jac` and `dfdp` gives the same answer, at a matched tolerance.

    The tolerance here is 1e-9, not 1e-12, and that is the point rather than a
    concession. With the derivatives differenced inside the augmented
    right-hand side, that side carries ``O(sqrt(eps)) ~ 1e-8`` error; asking for
    1e-12 makes the controller chase an accuracy the equations cannot deliver.
    Measured on this problem it turned a 1-second solve into a 130-second one
    and produced no extra accuracy at all.
    """
    f, jac, dfdp = lotka_volterra_parts()
    p = np.array([1.5, 1.0, 3.0, 1.0])
    y0 = np.array([10.0, 5.0])

    supplied = forward_sensitivities(
        f, (0.0, 4.0), y0, p, jac=jac, dfdp=dfdp, rtol=1e-9, atol=1e-11
    )
    differenced = forward_sensitivities(f, (0.0, 4.0), y0, p, rtol=1e-9, atol=1e-11)

    assert np.allclose(
        supplied.S_at_end(), differenced.S_at_end(), rtol=1e-4, atol=1e-5
    )
    assert differenced.stats.nfev > supplied.stats.nfev


def test_state_matches_a_plain_solve():
    """Augmenting the system must not perturb the state trajectory."""
    f, jac, dfdp = lotka_volterra_parts()
    p = np.array([1.5, 1.0, 3.0, 1.0])
    y0 = np.array([10.0, 5.0])

    augmented = forward_sensitivities(
        f, (0.0, 4.0), y0, p, jac=jac, dfdp=dfdp, rtol=1e-11, atol=1e-13
    )
    plain = solve(
        ODEProblem(f=lambda t, y: f(t, y, p), t_span=(0.0, 4.0), y0=y0),
        method="radau",
        rtol=1e-11,
        atol=1e-13,
    )
    assert np.allclose(augmented.y[:, -1], plain.y[:, -1], rtol=1e-7, atol=1e-9)


def test_sensitivity_of_an_analytically_known_problem():
    """``y' = -p y`` has ``y = y0 e^(-pt)``, so ``dy/dp = -t y0 e^(-pt)`` exactly."""
    y0 = np.array([2.0])
    p = np.array([1.3])
    T = 3.0

    result = forward_sensitivities(
        lambda t, y, p: -p[0] * y,
        (0.0, T),
        y0,
        p,
        jac=lambda t, y, p: np.array([[-p[0]]]),
        dfdp=lambda t, y, p: np.array([[-y[0]]]),
        rtol=1e-12,
        atol=1e-14,
    )
    expected = -T * y0[0] * np.exp(-p[0] * T)
    assert result.S_at_end()[0, 0] == pytest.approx(expected, rel=1e-9)


def test_multiple_parameters_are_independent():
    """Two decoupled parameters must produce a diagonal sensitivity matrix."""

    def f(t, y, p):
        return np.array([-p[0] * y[0], -p[1] * y[1]])

    result = forward_sensitivities(
        f,
        (0.0, 2.0),
        np.array([1.0, 1.0]),
        np.array([0.5, 2.0]),
        jac=lambda t, y, p: np.diag(-p),
        dfdp=lambda t, y, p: np.diag(-y),
        rtol=1e-12,
        atol=1e-14,
    )
    S = result.S_at_end()
    assert abs(S[0, 1]) < 1e-10
    assert abs(S[1, 0]) < 1e-10
    assert S[0, 0] == pytest.approx(-2.0 * np.exp(-1.0), rel=1e-8)
    assert S[1, 1] == pytest.approx(-2.0 * np.exp(-4.0), rel=1e-8)


# ---------------------------------------------------------------------------
# Sensitivity with respect to the initial condition
# ---------------------------------------------------------------------------


def test_initial_condition_sensitivity_is_the_propagation_matrix():
    """Setting ``dy0dp = I`` with ``dfdp = 0`` yields ``dy(T)/dy0``.

    That matrix is exactly what multiple shooting differences numerically, so
    this is also a cross-check between the two Phase 3 components.
    """
    f, jac, _ = lotka_volterra_parts()
    p = np.array([1.5, 1.0, 3.0, 1.0])
    y0 = np.array([10.0, 5.0])
    T = 4.0

    result = forward_sensitivities(
        lambda t, y, _q: f(t, y, p),
        (0.0, T),
        y0,
        np.zeros(2),
        jac=lambda t, y, _q: jac(t, y, p),
        dfdp=lambda t, y, _q: np.zeros((2, 2)),
        dy0dp=np.eye(2),
        rtol=1e-12,
        atol=1e-14,
    )
    G = result.S_at_end()

    reference = np.empty((2, 2))
    for j in range(2):
        h = 1e-6
        plus, minus = y0.copy(), y0.copy()
        plus[j] += h
        minus[j] -= h
        a = solve(
            ODEProblem(f=lambda t, y: f(t, y, p), t_span=(0.0, T), y0=plus),
            method="dopri5", rtol=1e-13, atol=1e-15,
        ).y[:, -1]
        b = solve(
            ODEProblem(f=lambda t, y: f(t, y, p), t_span=(0.0, T), y0=minus),
            method="dopri5", rtol=1e-13, atol=1e-15,
        ).y[:, -1]
        reference[:, j] = (a - b) / (2 * h)

    assert np.allclose(G, reference, rtol=1e-5, atol=1e-6)


def test_identity_propagation_at_zero_time_offset():
    """Over a vanishing interval ``dy/dy0`` is the identity."""
    result = forward_sensitivities(
        lambda t, y, p: -y,
        (0.0, 1e-10),
        np.array([1.0, 2.0]),
        np.zeros(2),
        dfdp=lambda t, y, p: np.zeros((2, 2)),
        dy0dp=np.eye(2),
        rtol=1e-12,
        atol=1e-14,
    )
    assert np.allclose(result.S_at_end(), np.eye(2), atol=1e-8)


# ---------------------------------------------------------------------------
# The application: parameter fitting
# ---------------------------------------------------------------------------


def test_gauss_newton_parameter_fit_recovers_true_parameters():
    """Fit Lotka-Volterra rate constants to noisy data using the sensitivities.

    The point of computing ``dy/dp`` at all. The Gauss-Newton step needs exactly
    the sensitivity matrix as its Jacobian, so a successful recovery of the true
    parameters from a perturbed start is an end-to-end check that they are both
    correct and correctly assembled.
    """
    f, jac, dfdp = lotka_volterra_parts()
    p_true = np.array([1.5, 1.0, 3.0, 1.0])
    y0 = np.array([10.0, 5.0])
    t_obs = np.linspace(0.5, 6.0, 25)

    truth = solve(
        ODEProblem(f=lambda t, y: f(t, y, p_true), t_span=(0.0, 6.0), y0=y0),
        method="radau", rtol=1e-12, atol=1e-14, t_eval=t_obs,
    ).y
    rng = np.random.default_rng(20260815)
    data = truth + rng.normal(0.0, 0.02, truth.shape)

    def residual_and_jacobian(p):
        result = forward_sensitivities(
            f, (0.0, 6.0), y0, p, jac=jac, dfdp=dfdp,
            method="radau", rtol=1e-9, atol=1e-11, t_eval=t_obs,
        )
        r = (result.y - data).ravel()
        # d(residual)/dp: stack the sensitivity blocks in the same order.
        J = result.S.transpose(0, 2, 1).reshape(-1, p.size)
        return r, J

    p = np.array([1.2, 0.8, 3.4, 1.2])   # perturbed by ~20%
    for _ in range(12):
        r, J = residual_and_jacobian(p)
        step, *_ = np.linalg.lstsq(J, -r, rcond=None)
        # Damped, because Gauss-Newton on a periodic system overshoots easily.
        p = p + 0.7 * step
        if np.linalg.norm(step) < 1e-10:
            break

    assert np.allclose(p, p_true, rtol=0.02), (
        f"recovered {np.round(p, 4)}, expected {p_true}"
    )


# ---------------------------------------------------------------------------
# API surface
# ---------------------------------------------------------------------------


def test_shapes_and_t_eval():
    f, jac, dfdp = lotka_volterra_parts()
    t_eval = np.linspace(0.0, 3.0, 17)
    result = forward_sensitivities(
        f, (0.0, 3.0), np.array([10.0, 5.0]), np.array([1.5, 1.0, 3.0, 1.0]),
        jac=jac, dfdp=dfdp, t_eval=t_eval, rtol=1e-10,
    )
    assert np.array_equal(result.t, t_eval)
    assert result.y.shape == (2, 17)
    assert result.S.shape == (2, 4, 17)
    assert "SensitivitySolution" in repr(result)


def test_initial_sensitivity_is_respected():
    """``S(t0)`` must equal `dy0dp`, not silently be zeroed."""
    S0 = np.array([[1.0, 0.0], [0.0, 3.0]])
    result = forward_sensitivities(
        lambda t, y, p: -y, (0.0, 1.0), np.array([1.0, 1.0]), np.zeros(2),
        dfdp=lambda t, y, p: np.zeros((2, 2)), dy0dp=S0,
        t_eval=[0.0, 1.0], rtol=1e-12, atol=1e-14,
    )
    assert np.allclose(result.S[:, :, 0], S0)
    # y' = -y decays every component by e^-1, and so must their sensitivities.
    assert np.allclose(result.S[:, :, -1], S0 * np.exp(-1.0), rtol=1e-8)


def test_bad_dy0dp_shape_raises():
    with pytest.raises(ValueError, match="dy0dp must have shape"):
        forward_sensitivities(
            lambda t, y, p: -y, (0.0, 1.0), np.array([1.0, 2.0]),
            np.zeros(3), dy0dp=np.eye(2),
        )


def test_explicit_method_also_works():
    """Nothing about the augmented system requires an implicit method."""
    f, jac, dfdp = lotka_volterra_parts()
    p = np.array([1.5, 1.0, 3.0, 1.0])
    stiff = forward_sensitivities(
        f, (0.0, 4.0), np.array([10.0, 5.0]), p, jac=jac, dfdp=dfdp,
        method="radau", rtol=1e-11, atol=1e-13,
    )
    explicit = forward_sensitivities(
        f, (0.0, 4.0), np.array([10.0, 5.0]), p, jac=jac, dfdp=dfdp,
        method="dopri5", rtol=1e-11, atol=1e-13,
    )
    assert np.allclose(stiff.S_at_end(), explicit.S_at_end(), rtol=1e-6, atol=1e-8)
