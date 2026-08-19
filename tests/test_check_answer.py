"""Checking a solution somebody typed in.

The library already decides whether a closed form is right by substituting it
back and simplifying -- that is how `SymbolicSolution.verified` is set. This
points the same check at the user's expression instead, which is the thing a
student actually wants at eleven at night.

Two properties matter more than the happy path.

**Equivalent forms must pass.** An equation has many correct spellings, and a
student who wrote `3*sin(2t)` where sympy wrote something else has not made a
mistake. The check substitutes; it never compares against sympy's answer.

**"Cannot decide" is not "wrong."** If simplification fails, `correct` is None.
Reporting that as incorrect would tell a student their right answer is wrong,
which is far worse than saying nothing.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sympy")

from odesuite_app.symbolic import (  # noqa: E402
    EquationSpec,
    check_answer,
    parse_equation,
)


def _parsed(equation: str, ics: str = ""):
    return parse_equation(EquationSpec(equations=[equation], initial_conditions=ics))


# ---------------------------------------------------------------------------
# Correct answers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "equation,answer",
    [
        ("y' + 2*y = 0", "C1*exp(-2*t)"),
        ("y'' + 4*y = 0", "C1*cos(2*t) + C2*sin(2*t)"),
        ("y'' + 3*y' + 2*y = 0", "C1*exp(-t) + C2*exp(-2*t)"),
        ("y'' + 2*y' + y = 0", "(C1 + C2*t)*exp(-t)"),
        ("y' = y*(1 - y)", "1/(1 + C1*exp(-t))"),
    ],
)
def test_a_correct_answer_verifies(equation, answer):
    result = check_answer(_parsed(equation), answer)
    assert result.correct is True, f"{answer}: {result.message}"
    assert result.ok


@pytest.mark.parametrize(
    "answer",
    [
        "C1*cos(2*t) + C2*sin(2*t)",
        "3*sin(2*t)",
        "cos(2*t)",
        "5*cos(2*t) - 2*sin(2*t)",
        "sin(2*t + 1)",
    ],
)
def test_any_equivalent_form_passes(answer):
    """The check substitutes; it does not compare against sympy's spelling.
    Every one of these solves ``y'' + 4y = 0`` and none looks like the others."""
    assert check_answer(_parsed("y'' + 4*y = 0"), answer).correct is True


@pytest.mark.parametrize(
    "written",
    ["y = 3*sin(2*t)", "y(t) = 3*sin(2*t)", "Y = 3*sin(2*t)", "  y   =  3*sin(2*t) ",
     "3*sin(2*t)"],
)
def test_the_answer_may_be_written_the_way_it_is_written_on_paper(written):
    """A student writes "y = ...". Refusing that would be a puzzle, not a check."""
    assert check_answer(_parsed("y'' + 4*y = 0"), written).correct is True


# ---------------------------------------------------------------------------
# Wrong answers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "answer", ["exp(-t)", "C1*cos(3*t)", "t**2", "0*t + 1"]
)
def test_a_wrong_answer_is_reported_as_wrong(answer):
    result = check_answer(_parsed("y'' + 4*y = 0"), answer)
    assert result.correct is False
    assert not result.ok
    assert result.residual is not None, "the leftover is what makes it a lesson"


def test_the_residual_shows_what_is_left_over():
    """Not just a verdict: the point is to see how far off it is."""
    result = check_answer(_parsed("y'' + 3*y' + 2*y = 0"), "exp(-3*t)")
    assert result.correct is False
    assert result.residual != 0


def test_the_trivial_solution_is_accepted_where_it_is_one():
    """y = 0 really does solve a homogeneous equation. Rejecting it would be
    the check being opinionated rather than correct."""
    assert check_answer(_parsed("y'' + 4*y = 0"), "0").correct is True


# ---------------------------------------------------------------------------
# Initial conditions
# ---------------------------------------------------------------------------


def test_an_answer_may_solve_the_equation_but_miss_the_conditions():
    """The distinction a student most needs drawn, and the one a bare
    substitution check would miss."""
    parsed = _parsed("y' + 2*y = 0", "y(0) = 3")

    right = check_answer(parsed, "3*exp(-2*t)")
    assert right.correct is True and right.matches_conditions is True
    assert right.ok

    general = check_answer(parsed, "5*exp(-2*t)")
    assert general.correct is True, "it does solve the equation"
    assert general.matches_conditions is False
    assert not general.ok
    assert "conditions" in general.message


def test_conditions_on_a_derivative_are_checked_too():
    parsed = _parsed("y'' + 4*y = 0", "y(0) = 0, y'(0) = 2")
    assert check_answer(parsed, "sin(2*t)").ok
    assert check_answer(parsed, "cos(2*t)").matches_conditions is False


def test_without_conditions_none_are_claimed():
    result = check_answer(_parsed("y'' + 4*y = 0"), "cos(2*t)")
    assert result.correct is True
    assert result.matches_conditions is None


# ---------------------------------------------------------------------------
# Nothing typed, nothing parseable, nothing dangerous
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text", ["", "   ", "y =", "y(t) ="])
def test_an_empty_answer_asks_rather_than_judges(text):
    result = check_answer(_parsed("y'' + 4*y = 0"), text)
    assert result.correct is None
    assert "type a solution" in result.message


def test_unparseable_input_is_reported_not_called_wrong():
    result = check_answer(_parsed("y'' + 4*y = 0"), "cos(2*t")
    assert result.correct is None, "a typo is not a wrong answer"
    assert "cannot parse" in result.message


@pytest.mark.parametrize(
    "payload",
    [
        "__import__('os').system('echo pwned')",
        "open('x','w')",
        "eval('1+1')",
        "().__class__.__bases__",
    ],
)
def test_the_answer_box_cannot_execute_code(payload):
    """A new place a user's string reaches sympy, and `sympify` executes what it
    is given. The README records this project already having that hole once, so
    every new entry point is checked for it."""
    result = check_answer(_parsed("y'' + 4*y = 0"), payload)
    assert result.correct is not True
    assert result.expression is None or result.correct is False


def test_a_system_says_it_is_not_supported_rather_than_guessing():
    parsed = parse_equation(
        EquationSpec(equations=["x' = x + 2*y", "y' = 3*x + 2*y"],
                     variables=["x", "y"])
    )
    result = check_answer(parsed, "exp(t)")
    assert result.correct is None
    assert "single equation" in result.message


def test_a_parameter_in_the_equation_is_shared_with_the_answer():
    """`y'' + c*y = 0` and an answer mentioning `c` must resolve to the *same*
    symbol, or the residual can never simplify away."""
    parsed = parse_equation(
        EquationSpec(equations=["y'' + c*y = 0"], parameters={"c": 4.0})
    )
    result = check_answer(parsed, "C1*cos(sqrt(c)*t)")
    assert result.correct is True, result.message
