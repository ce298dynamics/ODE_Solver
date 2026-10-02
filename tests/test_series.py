"""Power series: whether the recurrence is right, and what "checked" means here.

This module's answers are usually *truncations*, and that makes the honesty
question sharper than anywhere else in the project. Substituting a truncated
series back does not give zero, so the usual check would reject every correct
answer; accepting anything would reject none. What is actually claimed is
correctness through a given power, and these tests hold the module to that
claim -- including the case where a wrong series is correctly rejected.

The recurrences themselves are checked against the numbers a textbook prints,
and cross-checked against sympy's own truncation, which is a second opinion and
never the source.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sympy")

import sympy as sp  # noqa: E402

from odesuite_app.series import (  # noqa: E402
    IRREGULAR,
    ORDINARY,
    REGULAR,
    TITLE,
    coefficients,
    derive,
    indicial,
    point_kind,
    radius,
    split,
)

T = sp.Symbol("t", real=True)
R = sp.Symbol("r")
Y = sp.Function("y")


def _eq(lhs, rhs=0):
    return sp.Eq(lhs, rhs)


AIRY = _eq(Y(T).diff(T, 2) - T * Y(T))
LEGENDRE2 = _eq((1 - T**2) * Y(T).diff(T, 2) - 2 * T * Y(T).diff(T)
                + 6 * Y(T))
HERMITE2 = _eq(Y(T).diff(T, 2) - 2 * T * Y(T).diff(T) + 4 * Y(T))
BESSEL1 = _eq(T**2 * Y(T).diff(T, 2) + T * Y(T).diff(T) + (T**2 - 1) * Y(T))
EULER = _eq(T**2 * Y(T).diff(T, 2) + T * Y(T).diff(T) - Y(T))


# ---------------------------------------------------------------------------
# Reading the equation
# ---------------------------------------------------------------------------


def test_the_three_coefficients_are_read_off():
    assert split(LEGENDRE2, Y) == (1 - T**2, -2 * T, sp.Integer(6))


@pytest.mark.parametrize("equation", [
    # Forced: a particular series as well, which is a later topic.
    _eq(Y(T).diff(T, 2) + Y(T), T),
    # Third order.
    _eq(Y(T).diff(T, 3) + Y(T)),
    # Nonlinear.
    _eq(Y(T).diff(T, 2) + Y(T) ** 2),
])
def test_an_equation_the_method_does_not_fit_is_declined(equation):
    derivation = derive(equation, Y)
    assert derivation.result is None
    assert "homogeneous second-order linear" in derivation.message
    assert not derivation.steps


# ---------------------------------------------------------------------------
# Where the series may be built, and how far it reaches
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("equation,expected", [
    (AIRY, ORDINARY),
    (LEGENDRE2, ORDINARY),
    (BESSEL1, REGULAR),
    (EULER, REGULAR),
    # t^3 y'' + y: t*Q/P and t^2*R/P both blow up.
    (_eq(T**3 * Y(T).diff(T, 2) + Y(T)), IRREGULAR),
])
def test_the_point_is_classified(equation, expected):
    assert point_kind(*split(equation, Y)) == expected


def test_the_radius_reaches_the_nearest_singularity():
    assert radius(1 - T**2) == 1
    assert radius(sp.Integer(1)) is sp.oo


def test_a_factor_common_to_every_term_is_not_a_singularity():
    """(1 - t²)(y'' + y) = 0 is y'' + y = 0 written badly. Kept as typed, the
    factor looked like a leading coefficient vanishing at ±1, and the radius
    came out as 1 instead of infinite."""
    equation = sp.Eq((1 - T**2) * Y(T).diff(T, 2) + (1 - T**2) * Y(T), 0)
    P, Q, R_ = split(equation, Y)
    assert radius(P) is sp.oo
    assert point_kind(P, Q, R_, 1) == ORDINARY
    # A factor that is not common stays: Legendre's (1 - t²) is real.
    legendre = sp.Eq((1 - T**2) * Y(T).diff(T, 2) - 2 * T * Y(T).diff(T)
                     + 6 * Y(T), 0)
    assert radius(split(legendre, Y)[0]) == 1


def test_a_complex_singularity_limits_a_real_series():
    """1 + t² never vanishes for real t, and the series still stops at 1.
    Looking only at the real axis gives the wrong radius, which is the mistake
    the lesson warns about."""
    assert radius(1 + T**2) == 1


# ---------------------------------------------------------------------------
# The recurrence, which is the point of the module
# ---------------------------------------------------------------------------


def test_airys_coefficients_are_the_ones_a_textbook_prints():
    values, symbols = coefficients(*split(AIRY, Y), terms=8)
    a0, a1 = symbols[0], symbols[1]

    assert values[symbols[2]] == 0
    assert sp.simplify(values[symbols[3]] - a0 / 6) == 0
    assert sp.simplify(values[symbols[4]] - a1 / 12) == 0
    assert values[symbols[5]] == 0
    assert sp.simplify(values[symbols[6]] - a0 / 180) == 0


def test_every_third_airy_coefficient_vanishes():
    """The pattern the recurrence shows and a list of terms conceals -- which
    is the argument for narrating the rule rather than the numbers."""
    values, symbols = coefficients(*split(AIRY, Y), terms=8)
    assert values[symbols[2]] == 0
    assert values[symbols[5]] == 0


def test_the_recurrence_agrees_with_sympys_own_truncation():
    """A second opinion, not the source. sympy returns the truncation without
    the rule that generated it, which is why this module exists -- but the
    truncations must still match."""
    theirs = sp.dsolve(AIRY, Y(T), hint="2nd_power_series_ordinary").rhs
    ours = derive(AIRY, Y, terms=6).result
    c1, c2 = sp.Symbol("C1"), sp.Symbol("C2")

    def branches(expression):
        """The even and odd solutions, told apart by their own shape rather
        than by which constant sympy happened to attach to each -- the naming
        is sympy's business and is not the thing being checked."""
        expression = sp.expand(sp.expand(expression).removeO()
                               if expression.has(sp.Order) else expression)
        pair = [sp.expand(expression.subs({c1: a, c2: b}))
                for a, b in ((1, 0), (0, 1))]
        # The even branch is the one with a constant term.
        return sorted(pair, key=lambda item: item.coeff(T, 0) == 0)

    for mine, sympys in zip(branches(ours), branches(theirs)):
        # Only the powers both actually claim: sympy stops at O(t^6).
        for power in range(5):
            assert sp.simplify(mine.coeff(T, power)
                               - sympys.coeff(T, power)) == 0, power


# ---------------------------------------------------------------------------
# What "checked" means for a truncation
# ---------------------------------------------------------------------------


def test_a_truncation_says_it_is_one():
    derivation = derive(AIRY, Y)

    assert derivation.result is not None
    assert derivation.verified is True
    assert derivation.check == "truncation"
    assert "residual is of order" in derivation.message


def test_a_terminating_series_is_checked_by_substitution_instead():
    """Legendre at n = 2 with y′(0) = 0 kills the branch that never stops, and
    what is left is an exact polynomial. That deserves the stronger claim, and
    gets it."""
    derivation = derive(LEGENDRE2, Y,
                        ics={Y(0): 1, sp.Subs(Y(T).diff(T), T, 0): 0})

    assert derivation.check == "substitution"
    assert derivation.verified is True
    assert sp.simplify(derivation.result - (1 - 3 * T**2)) == 0
    assert not derivation.message


def test_a_terminating_answer_is_accepted_by_the_grader():
    """The constraint the whole unit is built around: a truncation is graded
    wrong, so every practice question must terminate."""
    from odesuite_app.symbolic import EquationSpec, check_answer, parse_equation

    parsed = parse_equation(EquationSpec(
        equations=["(1-t**2)*y'' - 2*t*y' + 6*y = 0"],
        initial_conditions="y(0) = 1, y'(0) = 0",
    ))
    derivation = derive(parsed.equation, parsed.function, ics=parsed.ics)
    assert check_answer(parsed, sp.sstr(derivation.result)).correct is True


def test_a_truncation_is_not_accepted_by_the_grader():
    """Stated as a test because it is the reason the unit is shaped as it is.
    The grader is right to say no -- the residual really is non-zero."""
    from odesuite_app.symbolic import EquationSpec, check_answer, parse_equation

    parsed = parse_equation(EquationSpec(equations=["y'' + y = 0"]))
    derivation = derive(parsed.equation, parsed.function)
    assert derivation.check == "truncation"
    assert check_answer(parsed, sp.sstr(derivation.result)).correct is False


def test_a_wrong_series_is_still_rejected():
    """The truncation check must not accept anything at all. A coefficient
    changed at a *low* power leaves a residual there, which is how a mistake
    is told from a truncation."""
    from odesuite_app.series import _reaches

    P, Q, R_ = split(AIRY, Y)
    right = derive(AIRY, Y, terms=8).result
    wrong = right + T**2          # a2 should be zero for Airy

    assert _reaches(P, Q, R_, right, 8)
    assert not _reaches(P, Q, R_, wrong, 8)


# ---------------------------------------------------------------------------
# Conditions, and singular points
# ---------------------------------------------------------------------------


def test_the_conditions_are_the_first_two_coefficients():
    """No system to solve -- a0 and a1 *are* y(0) and y'(0), which is a real
    convenience this method has and the others do not."""
    derivation = derive(AIRY, Y,
                        ics={Y(0): 2, sp.Subs(Y(T).diff(T), T, 0): 3})
    answer = derivation.result

    assert sp.simplify(answer.subs(T, 0) - 2) == 0
    assert sp.simplify(sp.diff(answer, T).subs(T, 0) - 3) == 0


def test_conditions_away_from_the_origin_are_declined():
    derivation = derive(AIRY, Y, ics={Y(1): 2})
    assert "given there" in derivation.message


def test_a_regular_singular_point_gets_the_indicial_equation():
    derivation = derive(BESSEL1, Y)
    titles = [step.title for step in derivation.steps]

    assert "t = 0 is not an ordinary point" in titles
    assert "But it is a regular singular point" in titles
    assert "The indicial equation fixes r" in titles
    assert derivation.result is None
    assert "regular singular point" in derivation.message
    assert not [s for s in derivation.steps if s.verified is False]


def test_the_indicial_equation_is_the_cauchy_euler_one():
    """The connection lesson 35 is built on: `t²y'' + ty' − y` gives (r−1)(r+1)
    by Frobenius, and the very same polynomial by the Cauchy–Euler
    substitution y = t^r. Frobenius is that substitution with a series
    attached."""
    theirs = sp.factor(indicial(*split(EULER, Y)))
    assert sp.simplify(theirs - (R - 1) * (R + 1)) == 0

    # And the Cauchy-Euler narrator reaches the same roots.
    from odesuite_app import steps

    derivation = steps.derive(EULER, Y,
                              hints=sp.classify_ode(EULER, Y(T)))
    assert derivation.technique == "nth_linear_euler_eq_homogeneous"
    roots = next(s for s in derivation.steps if s.title == "Its roots")
    assert "-1" in roots.latex and "1" in roots.latex


def test_an_irregular_point_says_so_rather_than_pretending():
    derivation = derive(_eq(T**3 * Y(T).diff(T, 2) + Y(T)), Y)
    assert derivation.result is None
    assert "irregular" in derivation.message


# ---------------------------------------------------------------------------
# The shape everything else depends on
# ---------------------------------------------------------------------------


def test_no_step_of_any_narration_fails_its_own_check():
    for equation in (AIRY, LEGENDRE2, HERMITE2, BESSEL1, EULER):
        failed = [s.title for s in derive(equation, Y).steps
                  if s.verified is False]
        assert not failed, f"{equation}: {failed}"


def test_it_never_raises_on_something_it_cannot_do():
    derivation = derive(_eq(sp.exp(Y(T)).diff(T, 2) + Y(T)), Y)
    assert derivation.result is None
    assert derivation.message


def test_series_needs_no_interface_toolkit():
    import subprocess
    import sys

    code = (
        "import sys; sys.modules['PySide6'] = None\n"
        "import odesuite_app.series as m; assert m.TITLE\n"
    )
    done = subprocess.run([sys.executable, "-c", code], capture_output=True,
                          text=True)
    assert done.returncode == 0, done.stderr[-400:]


def test_the_title_is_the_one_the_screen_shows():
    assert TITLE == "Power series"
    assert derive(AIRY, Y).title == TITLE
