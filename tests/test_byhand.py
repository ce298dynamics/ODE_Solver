"""Euler and RK4 as fixed-step methods, and the walkthrough that displays them.

Two claims are being made and both are checkable.

The **methods** claim their orders. `tests/test_tableaux.py` already checks the
rooted-tree conditions algebraically and asserts they fail one order higher, so
what is left here is the numerical counterpart: measured slopes of 1 and 4.

The **walkthrough** claims to show what the method does. That is only worth
anything if the table cannot drift from the library, so
`test_the_walkthrough_matches_a_real_solve` compares its endpoint with `solve`
at the same step size, bit-for-bit. A teaching aid that quietly computed
something else would be worse than none.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import ODEProblem, get_tableau, make_stepper, solve
from odesuite.problems import exponential_decay, linear_system, sine_cosine

pytest.importorskip("PySide6", reason="the app extra is not installed")

from odesuite_app.byhand import SUPPORTED, refinement, walk  # noqa: E402

# ---------------------------------------------------------------------------
# The methods themselves
# ---------------------------------------------------------------------------


def test_the_two_methods_a_course_teaches_by_hand_exist():
    """Before this, the method list started at Bogacki-Shampine: a learner
    could not select either of the methods they had just been taught."""
    assert get_tableau("euler").order == 1
    assert get_tableau("rk4").order == 4


@pytest.mark.parametrize("name", ["euler", "rk4"])
def test_they_carry_no_embedded_estimate_and_say_so(name):
    """Inventing an error estimate for them would let the controller adapt on a
    number that means nothing -- the exact failure mode this project has a
    recorded bug for. They are fixed-step, and the driver enforces it."""
    tab = get_tableau(name)
    assert tab.e is None
    assert not tab.embedded
    assert not make_stepper(name).adaptive

    problem = ODEProblem(lambda t, y: -y, (0.0, 1.0), [1.0])
    with pytest.raises(ValueError, match="fixed step size"):
        solve(problem, name, rtol=1e-6)


@pytest.mark.parametrize("name", ["euler", "rk4"])
def test_a_step_produces_no_error_estimate(name):
    problem = ODEProblem(lambda t, y: -y, (0.0, 1.0), [1.0])
    stepper = make_stepper(name)
    result = stepper.step(problem, 0.0, problem.y0, problem.f(0.0, problem.y0), 0.1)
    assert result.ok
    assert result.error is None


@pytest.mark.parametrize(
    "name,expected,steps",
    [("euler", 1.0, [200, 400, 800, 1600]), ("rk4", 4.0, [20, 40, 80, 160])],
)
def test_measured_convergence_order(name, expected, steps):
    bench = sine_cosine()
    stepper = make_stepper(name)
    exact = bench.exact_at_end()

    errors, sizes = [], []
    for n in steps:
        h = (bench.problem.tf - bench.problem.t0) / n
        t, y = bench.problem.t0, bench.problem.y0.copy()
        f = bench.problem.f(t, y)
        for _ in range(n):
            result = stepper.step(bench.problem, t, y, f, h)
            t, y = t + h, result.y_new
            f = result.f_new if result.f_new is not None else bench.problem.f(t, y)
        errors.append(float(np.linalg.norm(y - exact)))
        sizes.append(h)

    slope = float(np.polyfit(np.log(sizes), np.log(errors), 1)[0])
    assert abs(slope - expected) < 0.15, f"{name}: measured order {slope:.2f}"


def test_rk4_is_the_classical_tableau():
    """The coefficients everyone recognises, checked as themselves rather than
    only through their order."""
    tab = get_tableau("rk4")
    assert np.allclose(tab.b, [1 / 6, 1 / 3, 1 / 3, 1 / 6])
    assert np.allclose(tab.c, [0, 1 / 2, 1 / 2, 1])
    assert np.allclose(tab.A[1], [1 / 2, 0, 0, 0])
    assert np.allclose(tab.A[2], [0, 1 / 2, 0, 0])
    assert np.allclose(tab.A[3], [0, 0, 1, 0])


# ---------------------------------------------------------------------------
# The walkthrough
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method", SUPPORTED)
def test_the_walkthrough_matches_a_real_solve(method):
    """The load-bearing test. The table has to be what the method does, not a
    second implementation that happens to look similar."""
    bench = exponential_decay()
    h = 0.05
    n_steps = 12

    run = walk(bench.problem, method, h=h, n_steps=n_steps, exact=bench.exact)
    assert len(run.rows) == n_steps

    reference = solve(bench.problem, method, first_step=h, max_step=h)
    # Same method, same step size: the walkthrough's n-th row must be the
    # solver's n-th state, exactly.
    for row in run.rows:
        np.testing.assert_array_equal(row.y_next, reference.y[:, row.n + 1])


@pytest.mark.parametrize("method", SUPPORTED)
def test_each_row_is_internally_consistent(method):
    """`y_{n+1} = y_n + increment`, and the increment is what the step added."""
    bench = sine_cosine()
    run = walk(bench.problem, method, h=0.05, n_steps=6, exact=bench.exact)
    for row in run.rows:
        np.testing.assert_allclose(row.y + row.increment, row.y_next, rtol=0, atol=0)


def test_euler_is_exactly_y_plus_h_times_the_slope():
    """The whole method, in one identity, asserted bit-for-bit.

    Note the direction: `y_next == y + h*f` is exact, while
    `increment == h*f` is not -- the increment is recovered by subtracting, and
    ``(y + h*f) - y`` is not ``h*f`` in floating point. The identity worth
    checking is the one the method actually computes.
    """
    bench = sine_cosine()
    run = walk(bench.problem, "euler", h=0.05, n_steps=5, exact=bench.exact)
    for row in run.rows:
        # `row.h`, not the nominal step: the endpoint is `t0 + (n+1)*h` and the
        # step is the difference, which can differ by an ulp. Using the nominal
        # value here would be asserting against a number the method never saw.
        np.testing.assert_array_equal(row.y_next, row.y + row.h * row.f)
        assert row.h == pytest.approx(0.05, rel=1e-12)


def test_rk4_reports_its_intermediate_stages():
    """The four slopes are the thing a student is asked to compute; Euler has
    only the one and should not pretend otherwise."""
    bench = sine_cosine()
    rk4 = walk(bench.problem, "rk4", h=0.05, n_steps=3, exact=bench.exact)
    assert all(len(row.stages) == 3 for row in rk4.rows), (
        "k1 is reported as `f`; k2, k3 and k4 are the extra stages"
    )

    euler = walk(bench.problem, "euler", h=0.05, n_steps=3, exact=bench.exact)
    assert all(row.stages == [] for row in euler.rows)


def test_the_error_column_measures_against_the_closed_form():
    bench = exponential_decay()
    run = walk(bench.problem, "euler", h=0.1, n_steps=5, exact=bench.exact)

    assert run.has_exact
    for row in run.rows:
        expected = float(np.linalg.norm(row.y_next - bench.exact(row.t + run.h)))
        assert row.error == pytest.approx(expected)
    # Euler's error accumulates; that is the lesson the column exists to teach.
    errors = [row.error for row in run.rows]
    assert errors == sorted(errors)


def test_without_a_closed_form_there_is_simply_no_error_column():
    bench = sine_cosine()
    run = walk(bench.problem, "rk4", h=0.05, n_steps=3)
    assert not run.has_exact
    assert all(row.error is None for row in run.rows)


@pytest.mark.parametrize(
    "kwargs,message",
    [
        (dict(method="dopri5"), "by-hand methods"),
        (dict(h=0.0), "h must be positive"),
        (dict(h=-0.1), "h must be positive"),
        (dict(n_steps=0), "n_steps must be at least 1"),
    ],
)
def test_bad_arguments_are_refused(kwargs, message):
    bench = sine_cosine()
    call = dict(method="euler", h=0.1, n_steps=5)
    call.update(kwargs)
    with pytest.raises(ValueError, match=message):
        walk(bench.problem, **call)


# ---------------------------------------------------------------------------
# Halving the step
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("method,factor", [("euler", 2.0), ("rk4", 16.0)])
def test_halving_the_step_divides_the_error_by_two_to_the_order(method, factor):
    """The beginner's convergence study: not a fitted slope, four numbers whose
    ratios are the order."""
    bench = linear_system()
    levels = refinement(bench.problem, method, h=0.05, exact=bench.exact, levels=4)

    assert levels[0][3] is None, "the first row has nothing to compare against"
    ratios = [ratio for *_, ratio in levels[1:]]
    for ratio in ratios:
        assert factor / 1.6 < ratio < factor * 1.6, (
            f"{method}: halving h changed the error by {ratio:.2f}x, "
            f"expected about {factor:g}x"
        )


def test_refinement_halves_the_step_each_level():
    bench = sine_cosine()
    levels = refinement(bench.problem, "euler", h=0.1, exact=bench.exact, levels=4)
    sizes = [h for h, *_ in levels]
    assert sizes == pytest.approx([0.1, 0.05, 0.025, 0.0125])
    # And the error falls monotonically, which is what makes the table readable.
    errors = [error for _, _, error, _ in levels]
    assert errors == sorted(errors, reverse=True)
