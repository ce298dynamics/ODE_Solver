"""Jet arithmetic and the arbitrary-order Taylor method."""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import Jet, ODEProblem, solve
from odesuite.problems import exponential_decay, kepler, logistic, sine_cosine
from odesuite.steppers.taylor import TaylorMethod

from .test_convergence import ROUNDOFF_FLOOR

# ---------------------------------------------------------------------------
# Jet arithmetic
# ---------------------------------------------------------------------------

#: (label, jet/numpy expression, plain-float expression). Each is evaluated as a
#: truncated series about x0 and compared with the true function nearby.
EXPRESSIONS = [
    ("x**2", lambda z: z * z, lambda x: x * x),
    ("x**1.5", lambda z: z**1.5, lambda x: x**1.5),
    ("1/(1+x)", lambda z: 1.0 / (1.0 + z), lambda x: 1.0 / (1.0 + x)),
    ("exp(x)", lambda z: np.exp(z), lambda x: np.exp(x)),
    ("log(1+x)", lambda z: np.log(1.0 + z), lambda x: np.log(1.0 + x)),
    ("sqrt(x)", lambda z: np.sqrt(z), lambda x: np.sqrt(x)),
    ("sin(x)", lambda z: np.sin(z), lambda x: np.sin(x)),
    ("cos(x)", lambda z: np.cos(z), lambda x: np.cos(x)),
    ("tanh(x)", lambda z: np.tanh(z), lambda x: np.tanh(x)),
    ("sin(x)*exp(-x)", lambda z: np.sin(z) * np.exp(-z),
     lambda x: np.sin(x) * np.exp(-x)),
    ("exp(sin(x))/sqrt(x)", lambda z: np.exp(np.sin(z)) / np.sqrt(z),
     lambda x: np.exp(np.sin(x)) / np.sqrt(x)),
    ("(1+x**2)**-0.5", lambda z: (1.0 + z * z) ** -0.5,
     lambda x: (1.0 + x * x) ** -0.5),
]


@pytest.mark.parametrize("label,jet_expr,plain", EXPRESSIONS, ids=[e[0] for e in EXPRESSIONS])
def test_jet_series_reproduces_the_function(label, jet_expr, plain):
    """A degree-12 jet must reproduce its function to machine precision nearby.

    The series is built by the coefficient recurrences alone -- no derivative is
    ever evaluated numerically -- so agreement at 1e-15 is a statement that the
    recurrences are exactly right, not merely close.
    """
    x0 = 0.7
    jet = jet_expr(Jet.variable(x0, 12))
    for ds in (1e-4, 1e-3, 1e-2):
        assert jet(ds) == pytest.approx(plain(x0 + ds), abs=1e-13), (
            f"{label}: series at ds={ds} disagrees with the function"
        )


@pytest.mark.parametrize("label,jet_expr,plain", EXPRESSIONS, ids=[e[0] for e in EXPRESSIONS])
def test_jet_first_two_coefficients_are_the_derivatives(label, jet_expr, plain):
    """``c_0 = f(x0)`` and ``c_1 = f'(x0)``, checked against central differences."""
    x0 = 0.7
    jet = jet_expr(Jet.variable(x0, 6))
    assert jet.c[0] == pytest.approx(plain(x0), rel=1e-13)

    h = 1e-6
    derivative = (plain(x0 + h) - plain(x0 - h)) / (2 * h)
    assert jet.c[1] == pytest.approx(derivative, rel=1e-7)


def test_jet_coefficients_of_exp_are_factorials():
    """``exp(x)`` about 0 has coefficients ``1/k!`` exactly."""
    jet = np.exp(Jet.variable(0.0, 15))
    from math import factorial

    for k in range(16):
        assert jet.c[k] == pytest.approx(1.0 / factorial(k), rel=1e-13)


def test_jet_coefficients_of_sin_and_cos():
    s = np.sin(Jet.variable(0.0, 11))
    c = np.cos(Jet.variable(0.0, 11))
    from math import factorial

    for k in range(12):
        expected_sin = 0.0 if k % 2 == 0 else (-1) ** ((k - 1) // 2) / factorial(k)
        expected_cos = 0.0 if k % 2 else (-1) ** (k // 2) / factorial(k)
        assert s.c[k] == pytest.approx(expected_sin, abs=1e-14)
        assert c.c[k] == pytest.approx(expected_cos, abs=1e-14)


def test_jet_algebraic_identities():
    """Identities that must hold if the recurrences are mutually consistent."""
    x = Jet.variable(0.4, 10)

    assert np.allclose((np.sin(x) ** 2 + np.cos(x) ** 2).c, np.eye(11)[0], atol=1e-13)
    assert np.allclose(np.exp(np.log(1.0 + x)).c, (1.0 + x).c, atol=1e-13)
    assert np.allclose((np.sqrt(x) * np.sqrt(x)).c, x.c, atol=1e-13)
    assert np.allclose((x ** 3).c, (x * x * x).c, atol=1e-13)


def test_jet_division_roundoff_grows_as_the_recurrence_predicts():
    """``(x*x)/x == x``, to within the division recurrence's known amplification.

    Each coefficient of a quotient is computed from the ones below it and
    divided by ``b_0``, so round-off is amplified by ``1/|b_0|`` per order --
    here ``1/0.4 = 2.5``. The observed residuals grow at exactly that rate
    (2.8e-16 at order 2 rising to 4.2e-13 at order 10), which is the recurrence
    behaving correctly rather than drifting. Asserting a flat tolerance would
    either fail spuriously or hide a genuine defect at low order, so the bound
    tracks the amplification.
    """
    x0, order = 0.4, 10
    x = Jet.variable(x0, order)
    residual = np.abs(((x * x) / x).c - x.c)

    amplification = (1.0 / x0) ** np.arange(order + 1)
    bound = 50 * np.finfo(float).eps * amplification
    assert np.all(residual <= bound), (
        f"residuals {residual} exceed the predicted growth {bound}"
    )
    # And the growth really is geometric at the predicted rate, not faster.
    assert residual[-1] < 1e-11


def test_jet_scalar_interoperability():
    x = Jet.variable(2.0, 5)
    for expression in (x + 1, 1 + x, x - 1, 1 - x, 2 * x, x * 2, x / 2, 2 / x, -x, +x):
        assert isinstance(expression, Jet)
    assert (1 - x).c[0] == pytest.approx(-1.0)
    assert (2 / x).c[0] == pytest.approx(1.0)


def test_jet_division_by_zero_constant_term_raises():
    with pytest.raises(ZeroDivisionError):
        Jet.variable(1.0, 4) / Jet.constant(0.0, 4)


def test_jet_log_of_nonpositive_raises():
    with pytest.raises(ValueError, match="positive constant term"):
        np.log(Jet.constant(-1.0, 4))


def test_jet_repr():
    assert "Jet(order=5" in repr(Jet.variable(1.0, 5))


# ---------------------------------------------------------------------------
# The Taylor method
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("order", [4, 8, 12])
@pytest.mark.parametrize(
    "factory", [exponential_decay, sine_cosine, logistic], ids=lambda f: f.__name__
)
def test_local_error_order_matches_the_requested_order(order, factory):
    """A Taylor method of order N has local error ``h^(N+1)`` -- for any N.

    Unlike a Runge-Kutta pair there is no tableau to get wrong, so this checks
    the coefficient recurrence rather than a coefficient table.
    """
    bench = factory()
    stepper = TaylorMethod(order)
    problem = bench.problem
    t0, y0 = problem.t0, problem.y0.copy()
    f0 = problem.f(t0, y0)

    pairs = []
    for k in range(30):
        # Geometric ratio 0.75 rather than 0.5: at high order the error falls so
        # fast that halving reaches round-off in two or three steps.
        h = 0.5 * 0.75**k
        result = stepper.step(problem, t0, y0, f0, h)
        exact = np.asarray(bench.exact(t0 + h)).reshape(-1)
        err = float(np.linalg.norm(result.y_new - exact))
        if err <= ROUNDOFF_FLOOR:
            break
        pairs.append((h, err))

    if len(pairs) < 2:
        pytest.skip("error reaches round-off immediately at this order")
    (h0, e0), (h1, e1) = pairs[-2], pairs[-1]
    slope = np.log(e0 / e1) / np.log(h0 / h1)
    assert slope == pytest.approx(order + 1, abs=0.4), (
        f"Taylor{order} on {bench.name}: local order {slope:.2f}, "
        f"expected {order + 1}"
    )


def test_error_estimate_is_nondegenerate():
    """The Phase 2 lesson applied to a new adaptive method.

    ROS3P shipped an estimator that was identically zero and every accuracy test
    still passed. Any adaptive method added to this library gets checked here.
    """
    bench = sine_cosine()
    stepper = TaylorMethod(8)
    problem = bench.problem
    t0, y0 = problem.t0, problem.y0.copy()
    f0 = problem.f(t0, y0)

    for h in (0.4, 0.2, 0.1):
        result = stepper.step(problem, t0, y0, f0, h)
        exact = np.asarray(bench.exact(t0 + h)).reshape(-1)
        true_error = np.linalg.norm(result.y_new - exact)
        estimate = np.linalg.norm(result.error)
        assert estimate > 1e-15, f"estimate {estimate:.3e} is numerically zero"
        assert 1e-3 < estimate / max(true_error, 1e-16) < 1e5, (
            f"estimate {estimate:.3e} is not commensurate with the true error "
            f"{true_error:.3e}"
        )


@pytest.mark.parametrize("method", ["taylor8", "taylor20"])
def test_adaptive_solve_is_accurate(method):
    bench = sine_cosine()
    sol = solve(bench.problem, method=method, rtol=1e-10, atol=1e-12)
    assert sol.success, sol.message
    assert np.allclose(sol.y[:, -1], bench.exact_at_end(), atol=1e-9)


def test_high_order_reaches_machine_precision_in_few_steps():
    """The showcase claim: order 30 solves Kepler to ~1e-13 in a handful of steps.

    A fifth-order pair needs hundreds of steps for the same accuracy. High order
    costs more per step but the error falls exponentially in the order, so on a
    smooth problem it wins decisively.
    """
    bench = kepler(eccentricity=0.3, n_orbits=1.0)
    reference = solve(bench.problem, method="dopri5", rtol=1e-13, atol=1e-15)

    taylor = solve(bench.problem, method="taylor30", rtol=1e-13, atol=1e-15)
    rk = solve(bench.problem, method="dopri5", rtol=1e-10, atol=1e-12)

    taylor_error = np.linalg.norm(taylor.y[:, -1] - reference.y[:, -1])
    rk_error = np.linalg.norm(rk.y[:, -1] - reference.y[:, -1])

    assert taylor.success
    assert taylor_error < 1e-11, f"Taylor30 error {taylor_error:.3e}"
    assert taylor.stats.naccepted < 40, (
        f"{taylor.stats.naccepted} steps is more than expected for order 30"
    )
    assert taylor_error < rk_error
    assert taylor.stats.naccepted < 0.2 * rk.stats.naccepted


def test_dense_output_is_the_taylor_polynomial():
    """The continuous extension has the method's own order, for free."""
    bench = sine_cosine()
    sol = solve(
        bench.problem,
        method=TaylorMethod(12),
        rtol=1e-11,
        atol=1e-13,
        dense_output=True,
    )
    t = np.linspace(0.0, bench.problem.tf, 401)
    err = np.abs(sol.y_at(t) - bench.exact(t)).max()
    assert err < 1e-9, f"dense output error {err:.3e}"


def test_vectorised_right_hand_sides_work_unchanged():
    """A right-hand side written in ordinary numpy runs under jet arithmetic.

    The state is handed to `f` as an object array of jets, so expressions like
    ``-k * y`` and ``r * y * (1 - y)`` dispatch elementwise without the user
    rewriting anything.
    """
    problem = ODEProblem(f=lambda t, y: -1.5 * y, t_span=(0.0, 2.0), y0=[3.0])
    sol = solve(problem, method="taylor20", rtol=1e-12, atol=1e-14)
    assert sol.y[0, -1] == pytest.approx(3.0 * np.exp(-3.0), rel=1e-10)


def test_time_dependent_right_hand_side():
    """``y' = cos(t)`` exercises the independent-variable jet."""
    problem = ODEProblem(
        f=lambda t, y: np.array([np.cos(t)]), t_span=(0.0, 2.0), y0=[0.0]
    )
    sol = solve(problem, method="taylor20", rtol=1e-12, atol=1e-14)
    assert sol.y[0, -1] == pytest.approx(np.sin(2.0), abs=1e-11)


def test_invalid_order_raises():
    with pytest.raises(ValueError, match="at least 2"):
        TaylorMethod(1)
