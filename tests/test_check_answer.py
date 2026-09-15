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


def _system(conditions: str = ""):
    return parse_equation(
        EquationSpec(equations=["x' = x + 2*y", "y' = 3*x + 2*y"],
                     variables=["x", "y"], initial_conditions=conditions)
    )


#: The general solution of that system, as a learner would type it.
_SYSTEM_ANSWER = ("x = -C1*exp(-t) + 2*C2*exp(4*t)/3\n"
                  "y = C1*exp(-t) + C2*exp(4*t)")


def test_a_system_answer_is_checked_component_by_component():
    """It used to be refused outright. A system's answer is several functions,
    so it is typed as several lines and each is substituted into *every*
    equation."""
    result = check_answer(_system(), _SYSTEM_ANSWER)
    assert result.correct is True
    assert "every equation" in result.message


def test_the_order_the_components_are_typed_in_does_not_matter():
    """Each line names its unknown, so it cannot be read in the wrong order.
    Guessing from position would mark a correct answer wrong for anyone who
    wrote them the other way round."""
    swapped = "\n".join(reversed(_SYSTEM_ANSWER.split("\n")))
    assert check_answer(_system(), swapped).correct is True


def test_a_pair_that_solves_only_one_equation_is_rejected():
    """The near-miss worth catching: checking one equation at a time would
    call this correct."""
    result = check_answer(_system(), "x = exp(t)\ny = exp(t)")
    assert result.correct is False
    assert "every equation" in result.message


def test_a_missing_component_is_named_rather_than_guessed_at():
    result = check_answer(_system(), "x = exp(-t)")
    assert result.correct is None
    assert "y" in result.message


def test_an_unnamed_answer_asks_for_names():
    result = check_answer(_system(), "exp(-t)")
    assert result.correct is None
    assert "one line per unknown" in result.message


def test_system_conditions_are_judged_separately_from_the_equations():
    """A general solution solves the system but does not meet the conditions,
    and the two verdicts have to stay apart -- exactly as for one equation."""
    parsed = _system("x(0) = 1, y(0) = 0")

    general = check_answer(parsed, _SYSTEM_ANSWER)
    assert general.correct is True
    assert general.matches_conditions is False

    particular = check_answer(
        parsed,
        "x = (2*exp(5*t)+3)*exp(-t)/5\ny = (3*exp(5*t)-3)*exp(-t)/5",
    )
    assert particular.correct is True
    assert particular.matches_conditions is True


def test_a_parameter_in_the_equation_is_shared_with_the_answer():
    """`y'' + c*y = 0` and an answer mentioning `c` must resolve to the *same*
    symbol, or the residual can never simplify away."""
    parsed = parse_equation(
        EquationSpec(equations=["y'' + c*y = 0"], parameters={"c": 4.0})
    )
    result = check_answer(parsed, "C1*cos(sqrt(c)*t)")
    assert result.correct is True, result.message


# ---------------------------------------------------------------------------
# Reading the residual
# ---------------------------------------------------------------------------
#
# The verdict says whether an answer is right. These say how far it got, and
# every one of them is a claim the ladder has to *prove* by substituting
# something -- never a guess at what a wrong answer probably means.


def test_the_complementary_function_is_named_as_one():
    """The commonest miss in the whole course: the homogeneous equation solved
    and the forcing term never touched. Substituting it leaves precisely what
    substituting nothing leaves, which is what the ladder tests for."""
    result = check_answer(_parsed("y'' - y = 6*t"),
                          "C1*exp(t) + C2*exp(-t)")

    assert result.correct is False
    assert "complementary function" in result.diagnosis
    assert "particular solution" in result.diagnosis


def test_a_lost_coefficient_is_named_as_one():
    """`cos(2t)` has the shape of the particular solution and not its
    coefficient, and -4/3 of it is exact."""
    result = check_answer(_parsed("y'' + y = 4*cos(2*t)"), "cos(2*t)")

    assert result.correct is False
    assert "coefficient" in result.diagnosis
    assert "-4/3" in result.diagnosis


def test_a_sign_is_named_as_a_sign():
    result = check_answer(_parsed("y' - y = exp(2*t)"), "-exp(2*t)")

    assert result.correct is False
    assert result.diagnosis.startswith("A sign")


def test_a_missing_constant_is_named_as_one():
    """And in preference to the coefficient rung, which is also true here and
    less useful: an answer carrying an arbitrary constant absorbs a scaling."""
    result = check_answer(_parsed("y' + y = 5"), "C1*exp(-t) + 1")

    assert result.correct is False
    assert "one constant away" in result.diagnosis
    assert "adding 4" in result.diagnosis


def test_an_answer_with_no_t_in_it_is_told_so():
    result = check_answer(_parsed("y' = y"), "5")

    assert result.correct is False
    assert "does not contain t" in result.diagnosis


def test_the_right_family_and_the_wrong_member_of_it():
    """The most encouraging verdict there is, and the one most worth spelling
    out: the method is right and what is left is arithmetic."""
    result = check_answer(_parsed("y' = 2*t", "y(0) = 3"), "t**2")

    assert result.correct is True
    assert result.matches_conditions is False
    assert "The method is right" in result.diagnosis
    assert "y = 0" in result.diagnosis, "it says what the answer gives there"
    assert "3" in result.diagnosis, "and what was asked for"


def test_a_correct_answer_is_not_diagnosed():
    """There is nothing to diagnose, and a sentence under a tick would read as
    a complaint about an answer that was right."""
    result = check_answer(_parsed("y' = 2*y"), "C1*exp(2*t)")

    assert result.correct is True
    assert result.diagnosis == ""


def test_an_unrecognised_miss_says_nothing_rather_than_guessing():
    """Every rung is a test that fires or does not. `exp(t)` for `y' = 2y` is
    simply wrong, in no way the ladder can name, and inventing a sentence for
    it would be worse than the residual it falls back to."""
    result = check_answer(_parsed("y' = 2*y"), "exp(t)")

    assert result.correct is False
    assert result.diagnosis == ""


def test_a_system_says_which_equation_it_got():
    """"Half right" is a literal statement about a system, and the near-miss
    worth catching: fixing one component in isolation breaks the other."""
    parsed = parse_equation(
        EquationSpec(equations=["x' = x", "y' = x + y"], variables=["x", "y"])
    )
    result = check_answer(parsed, "x = exp(t)\ny = exp(t)")

    assert result.correct is False
    assert "equation 1" in result.diagnosis
    assert "equation 2" in result.diagnosis


def test_a_system_written_the_wrong_way_round_is_told_so():
    parsed = parse_equation(
        EquationSpec(equations=["x' = 2*x", "y' = 3*y"], variables=["x", "y"])
    )
    result = check_answer(parsed, "x = exp(3*t)\ny = exp(2*t)")

    assert result.correct is False
    assert "wrong way round" in result.diagnosis


def test_nothing_the_ladder_does_can_raise():
    """It is asked on every wrong answer, so a rung that threw would turn a
    cross into a traceback. `diagnose` swallows, and this is the promise."""
    from odesuite_app.symbolic import AnswerCheck, diagnose

    broken = AnswerCheck(expression=None, residual=None, correct=False)
    assert diagnose(_parsed("y' = y"), broken) == ""
