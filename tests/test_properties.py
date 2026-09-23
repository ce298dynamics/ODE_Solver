"""Structural properties of the integrators, checked over drawn inputs (TEST-03).

Every other file here checks named problems against known answers. These check
things that must hold for *any* input -- the shape of test that finds a defect
living in one branch of the code, where an example-based test only finds it if
somebody thought to pick an example from that branch. NUM-03 was exactly that:
RODAS4 was fourth order on every autonomous problem in the suite and first
order on the non-autonomous ones nobody had written down, and property 4 below
is the direct check on it.

Derandomised, so a failure reproduces on every machine and in CI; bounded, so
nothing drawn is stiff enough, or long enough, to turn a property into a
timeout; and small in `max_examples`, because each example is a real solve.
"""

from __future__ import annotations

import numpy as np
import pytest

hypothesis = pytest.importorskip("hypothesis")

from hypothesis import given, settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

from odesuite import ODEProblem, solve  # noqa: E402
from odesuite.steppers import second_order_problem  # noqa: E402

PROPERTY = settings(max_examples=20, deadline=None, derandomize=True,
                    database=None)

coefficient = st.floats(-2.0, 2.0, allow_nan=False, allow_infinity=False)
initial = st.floats(-3.0, 3.0, allow_nan=False, allow_infinity=False)
duration = st.floats(0.5, 4.0, allow_nan=False, allow_infinity=False)

ADAPTIVE = ("dopri5", "tsit5", "rodas4", "radau")


def _end(problem, method, rtol=1e-10):
    solution = solve(problem, method=method, rtol=rtol, atol=rtol * 1e-2)
    assert solution.success, (method, solution.message)
    return solution.y[:, -1]


# ---------------------------------------------------------------------------
# (1) Time-reversibility of the symmetric methods
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", ["verlet", "yoshida4"])
@PROPERTY
@given(q0=initial, v0=initial, t_end=duration)
def test_a_symmetric_method_retraces_its_steps(method, q0, v0, t_end):
    """Forward n steps, then backward n steps, lands on the start.

    A symmetric method's map reversed in time is its exact inverse, so the
    round trip is limited by round-off and not by the method's order -- which
    is what separates it from merely being accurate. Checked on the nonlinear
    pendulum rather than the oscillator, where linearity could hide a defect.
    """
    n_steps = 400

    def acceleration(t, q):
        return -np.sin(q)

    forward = solve(second_order_problem(acceleration, (0.0, t_end), [q0], [v0]),
                    method=method, n_steps=n_steps)
    end = forward.y[:, -1]
    back = solve(second_order_problem(acceleration, (t_end, 0.0), end[:1], end[1:]),
                 method=method, n_steps=n_steps)
    assert np.allclose(back.y[:, -1], [q0, v0], atol=1e-10, rtol=0.0)


# ---------------------------------------------------------------------------
# (2) Superposition for a linear system
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", ADAPTIVE)
@PROPERTY
@given(
    entries=st.lists(coefficient, min_size=4, max_size=4),
    y0=st.lists(initial, min_size=2, max_size=2),
    z0=st.lists(initial, min_size=2, max_size=2),
    a=coefficient, b=coefficient, t_end=duration,
)
def test_a_linear_system_superposes(method, entries, y0, z0, a, b, t_end):
    """solve(a y0 + b z0) = a solve(y0) + b solve(z0), to solver tolerance.

    Exact for the flow, so any departure is solver error -- and the adaptive
    controller chooses different steps for the three solves, so this is a check
    that the error really is controlled, not just that a fixed map is linear.
    """
    A = np.asarray(entries).reshape(2, 2)

    def build(start):
        return ODEProblem(f=lambda t, y: A @ y, t_span=(0.0, t_end), y0=start,
                          jac=lambda t, y: A)

    combined = _end(build(a * np.asarray(y0) + b * np.asarray(z0)), method)
    separate = a * _end(build(y0), method) + b * _end(build(z0), method)
    scale = 1.0 + np.max(np.abs(separate))
    assert np.max(np.abs(combined - separate)) <= 1e-6 * scale


# ---------------------------------------------------------------------------
# (3) Time-translation invariance of an autonomous problem
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", ADAPTIVE)
@PROPERTY
@given(mu=st.floats(0.1, 2.0), x0=initial, v0=initial, t_end=duration,
       shift=st.floats(-50.0, 50.0))
def test_an_autonomous_problem_does_not_care_when_it_starts(
        method, mu, x0, v0, t_end, shift):
    """Van der Pol on [0, T] and on [s, s + T] from the same state agree."""

    def f(t, y):
        return np.array([y[1], mu * (1.0 - y[0] ** 2) * y[1] - y[0]])

    here = _end(ODEProblem(f=f, t_span=(0.0, t_end), y0=[x0, v0]), method)
    there = _end(ODEProblem(f=f, t_span=(shift, shift + t_end), y0=[x0, v0]), method)
    scale = 1.0 + np.max(np.abs(here))
    assert np.max(np.abs(here - there)) <= 1e-6 * scale


# ---------------------------------------------------------------------------
# (4) A non-autonomous problem agrees with its autonomised form
# ---------------------------------------------------------------------------


def _fixed_steps(method, problem, n_steps):
    """March a stepper at constant h, bypassing the controller.

    Through `solve` an adaptive method ignores `n_steps`, and error control
    then hides exactly the defect this property is for: the controller simply
    takes smaller steps. Measured on the pre-NUM-03 code, the adaptive
    endpoints agreed with the autonomised form to 5e-14 at rtol = 1e-10.
    """
    from odesuite import make_stepper

    stepper = make_stepper(method)
    t, y = problem.t0, problem.y0.copy()
    h = (problem.tf - problem.t0) / n_steps
    f = problem.f(t, y)
    for step in range(n_steps):
        result = stepper.step(problem, t, y, f, h)
        assert result.ok
        y = result.y_new
        t = problem.t0 + (step + 1) * h
        f = result.f_new if result.f_new is not None else problem.f(t, y)
    return y


@pytest.mark.parametrize("method,exact_dfdt,bound", [
    ("rk4", False, 1e-14),
    ("dopri5", False, 1e-14),
    ("radau", False, 1e-14),
    ("rodas4", False, 1e-11),
    ("rodas4", True, 1e-14),
])
@PROPERTY
@given(k=st.floats(0.2, 3.0), omega=st.floats(0.5, 5.0), y0=initial,
       t_end=duration)
def test_time_as_an_argument_and_time_as_a_state_agree(
        method, exact_dfdt, bound, k, omega, y0, t_end):
    """y' = -k y + sin(omega t), against the same with t carried as a state.

    Every Runge-Kutta method, and a correctly implemented Rosenbrock method,
    takes *identical* steps on the two forms, so the property is equality to
    round-off at a fixed h -- not agreement to some tolerance. Both sides get
    exact Jacobians, so a difference cannot come from differencing df/dy.

    The direct check on NUM-03. Rosenbrock needs df/dt as well, and where it
    is not supplied it is differenced. Measured at h = T/20 (three problems):

    ==========================  ===================
    RODAS4                      largest difference
    ==========================  ===================
    before NUM-03 (forward)     2.6e-10
    central difference          4.9e-13
    exact ``dfdt`` supplied     6.7e-16
    ==========================  ===================

    so the 1e-11 bound fails the old code by more than an order of magnitude
    and passes the current one by the same margin.
    """
    def f(t, y):
        return np.array([-k * y[0] + np.sin(omega * t)])

    extras = {"dfdt": lambda t, y: np.array([omega * np.cos(omega * t)])}         if exact_dfdt else {}
    direct = ODEProblem(f=f, t_span=(0.0, t_end), y0=[y0],
                        jac=lambda t, y: np.array([[-k]]), **extras)
    extended = ODEProblem(
        f=lambda t, z: np.array([-k * z[0] + np.sin(omega * z[1]), 1.0]),
        t_span=(0.0, t_end), y0=[y0, 0.0],
        jac=lambda t, z: np.array([[-k, omega * np.cos(omega * z[1])],
                                   [0.0, 0.0]]),
    )
    one = _fixed_steps(method, direct, 20)[0]
    other = _fixed_steps(method, extended, 20)[0]
    assert abs(one - other) <= bound * (1.0 + abs(one))
