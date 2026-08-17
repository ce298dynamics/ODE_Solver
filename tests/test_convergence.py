"""Order-of-convergence verification.

The strongest correctness signal in the library. For a method of order p the
global error at a fixed endpoint scales as ``C h^p``, so a least-squares fit of
``log(error)`` against ``log(h)`` must recover a slope of p. A mistyped
coefficient, a misapplied stage weight or an off-by-one in the stage loop all
show up here as a wrong slope.

Steppers are driven directly in a fixed-step loop rather than through `solve`,
which isolates the method's own order from the step-size controller. The
adaptive path is verified separately in `test_driver.py` by checking that the
achieved accuracy tracks the requested tolerance.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import ExplicitRungeKutta, ODEProblem, make_stepper
from odesuite.problems import ANALYTIC, kepler, linear_system, sine_cosine
from odesuite.tableaux import TABLEAUX, ButcherTableau

METHOD_NAMES = sorted({tab.name.lower(): key for key, tab in TABLEAUX.items()}.values())

#: Errors at or below this are dominated by floating-point round-off rather than
#: truncation, and including them flattens the measured slope. Set at roughly
#: 450 * eps for an O(1) state: low enough to leave a usable dynamic range for
#: the 5th-order methods, high enough to stay clear of the accumulated rounding
#: of a seven-stage evaluation.
ROUNDOFF_FLOOR = 1e-13

#: Problems whose solution stays O(1) over the interval, so that a 5th-order
#: method still has a usable window between "asymptotic regime reached" and
#: "round-off floor hit". On problems that decay to ~1e-3 that window can close
#: entirely for a method with a large error constant, which is a property of
#: double precision rather than of the method -- see test_local_error_order,
#: which has no such limitation and carries the tight tolerance.
GLOBAL_ORDER_PROBLEMS = (sine_cosine, linear_system)


def fixed_step_integrate(stepper, problem: ODEProblem, n_steps: int) -> np.ndarray:
    """Integrate with `n_steps` equal steps and return the final state.

    Deliberately bypasses `solve`: no controller, no rejection, no interpolation.
    """
    t, tf = problem.t0, problem.tf
    h = (tf - t) / n_steps
    y = problem.y0.copy()
    f = problem.f(t, y)

    for i in range(n_steps):
        result = stepper.step(problem, t, y, f, h)
        assert result.ok, f"stepper failed at step {i}"
        y = result.y_new
        t = tf if i == n_steps - 1 else t + h
        f = result.f_new if result.f_new is not None else problem.f(t, y)
    return y


def fit_order(n_steps_list, errors, h_list) -> float:
    """Least-squares slope of log(error) vs log(h)."""
    mask = np.asarray(errors) > ROUNDOFF_FLOOR
    if mask.sum() < 3:
        pytest.skip("too few points above the round-off floor to fit a slope")
    logh = np.log(np.asarray(h_list)[mask])
    loge = np.log(np.asarray(errors)[mask])
    slope, _ = np.polyfit(logh, loge, 1)
    return float(slope)


def finest_pair_order(errors, h_list) -> float:
    """Slope from the two finest usable refinements.

    Preferred over a least-squares fit across the whole sweep for *global*
    error: the coarse end of a sweep is typically still pre-asymptotic, and
    averaging it in biases the estimate upward.
    """
    usable = [(h, e) for h, e in zip(h_list, errors) if e > ROUNDOFF_FLOOR]
    if len(usable) < 2:
        pytest.skip("fewer than two points above the round-off floor")
    (h0, e0), (h1, e1) = usable[-2], usable[-1]
    return float(np.log(e0 / e1) / np.log(h0 / h1))


def local_error_sweep(stepper, bench, h0: float = 0.5, max_halvings: int = 20):
    """Single-step error from exact initial data, halving h until round-off.

    The local truncation error of an order-p method is ``C h^(p+1)`` with no
    accumulated history, which makes it the sharpest available order check. The
    sweep is geometric and self-terminating rather than a fixed list, because
    the usable window differs by orders of magnitude between methods: a 3rd
    order method needs coarse steps to stay above round-off, while a 5th order
    one reaches the floor within a handful of halvings.

    Returns the ``(h, error)`` pairs that are above `ROUNDOFF_FLOOR`.
    """
    problem = bench.problem
    t0 = problem.t0
    y0 = problem.y0.copy()
    f0 = problem.f(t0, y0)

    pairs = []
    for k in range(max_halvings):
        h = h0 * 0.5**k
        result = stepper.step(problem, t0, y0, f0, h)
        exact = np.asarray(bench.exact(t0 + h)).reshape(-1)
        err = float(np.linalg.norm(result.y_new - exact))
        if err <= ROUNDOFF_FLOOR:
            break
        pairs.append((h, err))
    return pairs


def asymptotic_order(pairs) -> float:
    """Order estimated from the two finest steps that clear the round-off floor.

    Preferred to a fit over the whole sweep. The coarse end is pre-asymptotic
    and biases the estimate -- upward for a method whose leading error
    coefficient is small (Tsit5, DOPRI5), downward for one where the next term
    partly cancels it (Cash-Karp). Both settle onto the true order at the fine
    end, so that is where the measurement is taken.
    """
    if len(pairs) < 2:
        pytest.skip("fewer than two step sizes clear the round-off floor")
    (h0, e0), (h1, e1) = pairs[-2], pairs[-1]
    return float(np.log(e0 / e1) / np.log(h0 / h1))


def measure_convergence(method: str, bench, n_steps_list):
    """Return (fitted slope, errors, step sizes) for a method on a benchmark."""
    stepper = make_stepper(method)
    problem = bench.problem
    exact = bench.exact_at_end()

    errors, h_list = [], []
    for n in n_steps_list:
        y_end = fixed_step_integrate(stepper, problem, n)
        err = float(np.linalg.norm(y_end - exact) / max(np.linalg.norm(exact), 1.0))
        errors.append(max(err, 1e-18))
        h_list.append(abs(problem.tf - problem.t0) / n)
    return fit_order(n_steps_list, errors, h_list), errors, h_list


# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", METHOD_NAMES)
@pytest.mark.parametrize("factory", ANALYTIC, ids=lambda f: f.__name__)
def test_local_error_order(method, factory):
    """The local truncation error scales as ``h^(p+1)``. The primary order check.

    Together with `tests/test_tableaux.py` this pins the order from both sides:
    that file proves the *coefficients* satisfy the order conditions through p
    and fail at p+1, algebraically and exactly; this one proves the
    *implementation* realises them. Any assembly bug -- a misplaced stage, a
    dropped weight, a wrong abscissa -- breaks order conditions and shows up
    here as a wrong slope.
    """
    bench = factory()
    stepper = make_stepper(method)
    expected = stepper.order + 1

    pairs = local_error_sweep(stepper, bench)
    slope = asymptotic_order(pairs)

    assert slope == pytest.approx(expected, abs=0.3), (
        f"{stepper.name} on {bench.name}: local error order {slope:.3f}, "
        f"expected {expected}. sweep="
        f"{[('%.3g' % h, '%.3e' % e) for h, e in pairs]}"
    )


@pytest.mark.parametrize("method", METHOD_NAMES)
@pytest.mark.parametrize("factory", GLOBAL_ORDER_PROBLEMS, ids=lambda f: f.__name__)
def test_global_convergence_order(method, factory):
    """Global error at a fixed endpoint scales as ``h^p``.

    Uses the two finest refinements rather than a fit over the whole sweep, and
    a looser tolerance than the local test, because the coarse end of any
    feasible sweep is still pre-asymptotic for a 5th-order method in double
    precision. The tight guarantee comes from `test_local_error_order`.
    """
    bench = factory()
    stepper = make_stepper(method)
    p = stepper.order
    n_steps_list = [10, 20, 40, 80] if p >= 5 else [20, 40, 80, 160]

    _, errors, h_list = measure_convergence(method, bench, n_steps_list)
    slope = finest_pair_order(errors, h_list)

    assert slope == pytest.approx(p, abs=0.5), (
        f"{stepper.name} on {bench.name}: global order {slope:.3f}, "
        f"expected {p}. errors={['%.3e' % e for e in errors]}"
    )


@pytest.mark.parametrize("method", METHOD_NAMES)
def test_embedded_estimator_order(method):
    """The embedded solution attains its own, lower, declared order.

    Guards the error *estimate*: the tableau test checks its order conditions
    algebraically, this checks the resulting method numerically. If the embedded
    order were wrong the controller would use the wrong exponent and mis-size
    every step.

    The embedded weights are propagated as a method in their own right, by
    rebuilding the tableau with ``b := b - e``. Applying a single embedded step
    on top of the higher-order trajectory would instead measure that method's
    *local* error, which is one order higher and would pass for the wrong reason.
    """
    stepper = make_stepper(method)
    tab = stepper.tab

    embedded = ExplicitRungeKutta(
        ButcherTableau(
            name=f"{tab.name}-embedded",
            A=tab.A,
            b=tab.b - tab.e,
            c=tab.c,
            e=tab.e,
            order=tab.error_order,
            error_order=max(tab.error_order - 1, 1),
        )
    )

    bench = sine_cosine()
    pairs = local_error_sweep(embedded, bench)
    slope = asymptotic_order(pairs)

    assert slope == pytest.approx(tab.error_order + 1, abs=0.3), (
        f"{tab.name}: embedded local error order {slope:.3f}, "
        f"expected {tab.error_order + 1}"
    )


@pytest.mark.parametrize("method", METHOD_NAMES)
def test_convergence_on_nonlinear_problem(method):
    """Order also holds on a genuinely nonlinear problem with a strong gradient.

    Linear test problems can mask errors in how stage *states* (rather than
    stage derivatives) are formed, because the RHS is insensitive to them.
    Kepler at moderate eccentricity does not let that slide.
    """
    stepper = make_stepper(method)
    p = stepper.order
    bench = kepler(eccentricity=0.3, n_orbits=0.5)
    problem = bench.problem

    # No closed form; use a very fine run with the same method as reference.
    reference = fixed_step_integrate(stepper, problem, 4000)

    n_list = [25, 50, 100, 200]
    errors, h_list = [], []
    for n in n_list:
        y_end = fixed_step_integrate(stepper, problem, n)
        errors.append(max(float(np.linalg.norm(y_end - reference)), 1e-18))
        h_list.append(abs(problem.tf - problem.t0) / n)

    slope = fit_order(n_list, errors, h_list)
    assert slope == pytest.approx(p, abs=0.35), (
        f"{stepper.name} on Kepler: fitted order {slope:.3f}, expected {p}"
    )


@pytest.mark.parametrize("method", METHOD_NAMES)
def test_error_decreases_monotonically(method):
    """Halving the step must reduce the error at every refinement level."""
    bench = sine_cosine()
    _, errors, _ = measure_convergence(method, bench, [20, 40, 80, 160])
    for a, b in zip(errors, errors[1:]):
        assert b < a, f"error grew on refinement: {errors}"


def test_non_autonomous_problem():
    """``y' = g(t)`` integrates correctly, which requires ``c_i == sum_j a_ij``.

    An autonomous test problem cannot detect a wrong abscissa, since `c` never
    enters the RHS. This one can.
    """
    prob = ODEProblem(f=lambda t, y: np.array([np.cos(t)]), t_span=(0.0, 2.0), y0=[0.0])
    for method in METHOD_NAMES:
        stepper = make_stepper(method)
        y_end = fixed_step_integrate(stepper, prob, 40)
        assert y_end[0] == pytest.approx(np.sin(2.0), abs=1e-6), (
            f"{stepper.name} mishandles a time-dependent RHS"
        )
