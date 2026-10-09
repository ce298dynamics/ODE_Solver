"""Grading an equation, and grading one move of a method.

`check_answer` grades a solution by substituting it into the equation, which
needs nothing stored and cannot be fooled by a different spelling. Two kinds of
question cannot be reached that way, because in both the thing asked for is not
a solution: *write the equation for this situation*, and *write the integrating
factor*. `check_model` and `check_expression` grade those, and this file is
about the two properties that make them safe to use.

**Rearranging is not a mistake.** ``y' = 2 - y/20``, ``y' + y/20 = 2`` and
``20y' + y = 40`` are one equation, and a grader that accepted only the first
would be teaching a spelling rather than a model. The same goes for an
integrating factor, which is determined only up to a constant: ``e^{3t}`` and
``5e^{3t}`` both work.

**Both verdicts are proofs.** Right is proved by simplifying a difference to
zero; wrong is proved by evaluating at a point where the two disagree -- and
where a constant multiple is allowed, at two points whose ratios disagree,
since a constant is the same constant everywhere. Anything else is *cannot
tell*, exactly as in `check_answer`, and the tests at the bottom hold that
line: a verdict of wrong is a claim about the mathematics, and this must never
make it about the typing.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sympy")

from odesuite_app.symbolic import check_expression, check_model  # noqa: E402

# ---------------------------------------------------------------------------
# An equation, however it is arranged
# ---------------------------------------------------------------------------

#: The mixing tank of the `linear` lesson, written six ways somebody might.
TANK = "y' = 2 - y/20"


@pytest.mark.parametrize(
    "written",
    [
        "y' = 2 - y/20",
        "y' + y/20 = 2",
        "y' + 0.05*y = 2",
        "20*y' + y = 40",
        "-y' - y/20 = -2",
        "y' = (40 - y)/20",
    ],
)
def test_an_equation_is_accepted_however_it_is_arranged(written):
    result = check_model(TANK, written)
    assert result.correct is True, f"{written}: {result.message}"
    assert result.ok


@pytest.mark.parametrize(
    "written,leftover",
    [
        # The sign of the outflow, which is the mistake this question exists
        # to catch -- and the difference names the term it happened to.
        ("y' = 2 + y/20", "y/10"),
        # The inflow left out altogether.
        ("y' = -y/20", "-2"),
        # The volume and the flow rate the wrong way round.
        ("y' = 2 - y/5", None),
    ],
)
def test_a_different_equation_is_refused_and_says_what_differs(written,
                                                              leftover):
    result = check_model(TANK, written)
    assert result.correct is False, result.message
    assert result.difference is not None
    if leftover is not None:
        import sympy as sp

        assert sp.simplify(abs(result.difference) - abs(sp.sympify(leftover))) == 0


def test_a_higher_order_equation_is_graded_the_same_way():
    assert check_model("y'' + 3*y' + 2*y = 0",
                       "y'' = -3*y' - 2*y").correct is True
    assert check_model("y'' + 3*y' + 2*y = 0",
                       "y'' + 3*y' - 2*y = 0").correct is False


def test_a_constant_multiple_is_the_same_equation_and_says_so():
    result = check_model(TANK, "20*y' + y = 40")
    assert result.correct is True
    assert result.factor == 20
    assert "20" in result.message


def test_a_multiple_by_something_that_is_not_constant_is_not_the_same():
    """Dividing ``y' = 3y`` by `y` loses the solution ``y = 0``.

    It is the one wrong answer here that comes from doing the algebra
    correctly and going one step too far, so the verdict names the factor
    rather than saying only that the equation is different.
    """
    result = check_model("y' = 3*y", "y'/y = 3")
    assert result.correct is False
    assert "1/y" in result.message

    through_t = check_model("y' = 3*y", "t*y' = 3*t*y")
    assert through_t.correct is False
    assert "by t" in through_t.message


def test_the_leftover_is_written_in_the_names_somebody_used():
    """The difference is shown, so it has to be readable.

    It is in terms of `y` and `y'`, not the internal symbols the comparison
    runs on: a verdict that prints ``-__y_0/10`` says only that something
    leaked out of the machinery.
    """
    result = check_model(TANK, "y' = 2 + y/20")
    assert "__" not in str(result.difference)
    assert "y" in str(result.difference)


def test_an_equation_in_the_wrong_unknown_is_asked_for_again():
    result = check_model("y' = 3*y", "x' = 3*x")
    assert result.correct is None
    assert "y" in result.message


def test_something_that_is_not_an_equation_asks_rather_than_marks():
    for text in ("", "   ", "2 - y/20"):
        result = check_model(TANK, text)
        assert result.correct is None
        assert result.message


def test_a_broken_question_says_so_rather_than_marking_the_answer():
    result = check_model("this is not an equation", "y' = 2")
    assert result.correct is None
    assert "could not be set up" in result.message


# ---------------------------------------------------------------------------
# One move of a method
# ---------------------------------------------------------------------------


def test_an_expression_is_graded_exactly_when_it_should_be():
    assert check_expression("t*exp(2*t)", "t*exp(2*t)").correct is True
    assert check_expression("t*exp(2*t)", "exp(2*t)*t").correct is True
    assert check_expression("t*exp(2*t)", "t*exp(-2*t)").correct is False
    # Exactly: without `up_to_constant` a multiple is a different answer.
    assert check_expression("exp(3*t)", "5*exp(3*t)").correct is False


def test_an_integrating_factor_is_right_up_to_its_constant():
    """It is not a leniency: any nonzero multiple of an integrating factor is
    an integrating factor, and marking ``2e^{3t}`` wrong would teach something
    false about the method."""
    for written in ("exp(3*t)", "2*exp(3*t)", "-exp(3*t)", "exp(3*t)/7"):
        result = check_expression("exp(3*t)", written, up_to_constant=True)
        assert result.correct is True, f"{written}: {result.message}"
    wrong = check_expression("exp(3*t)", "exp(-3*t)", up_to_constant=True)
    assert wrong.correct is False


def test_a_characteristic_equation_may_be_written_as_an_equation():
    """``r^2 + 3r + 2`` and ``r^2 + 3r + 2 = 0`` are the same answer, and so is
    ``r^2 + 3r = -2``."""
    for written in ("r**2 + 3*r + 2", "r^2+3r+2 = 0", "r^2 + 3r = -2",
                    "2*r**2 + 6*r + 4", "(r+1)*(r+2)"):
        result = check_expression("r**2 + 3*r + 2", written,
                                  up_to_constant=True)
        assert result.correct is True, f"{written}: {result.message}"
    assert check_expression("r**2 + 3*r + 2", "r**2 + 3*r - 2",
                            up_to_constant=True).correct is False


def test_a_label_in_front_of_the_answer_is_not_part_of_it():
    """Somebody writing an integrating factor writes ``mu = ...``; somebody
    writing a characteristic equation writes ``r^2 + ... = 0``. Both have an
    equals sign and they mean opposite things by it."""
    labelled = check_expression("exp(3*t)", "mu = exp(3*t)", up_to_constant=True)
    assert labelled.correct is True
    assert check_expression("r**2 + 3*r + 2", "r = -1", up_to_constant=True
                            ).correct is not True


def test_an_answer_written_in_the_transform_variable_uses_the_same_symbol():
    assert check_expression("1/(s - 2)**2", "1/(s-2)^2").correct is True
    assert check_expression("1/(s - 2)**2", "1/(s+2)^2").correct is False


def test_implicit_multiplication_is_read_as_a_student_writes_it():
    assert check_expression("3*t**2", "3t^2").correct is True
    assert check_expression("2*(t + 1)", "2(t+1)").correct is True


def test_a_wrong_expression_shows_what_is_left_over():
    result = check_expression("t**2 + 3*t", "t**2 + 5*t")
    assert result.correct is False
    assert str(result.difference) == "2*t"


def test_typing_nothing_asks_rather_than_marks():
    result = check_expression("exp(3*t)", "  ")
    assert result.correct is None
    assert result.message


def test_nonsense_is_a_reading_failure_not_a_wrong_answer():
    """The discipline `check_answer` keeps: *wrong* is a claim about the
    mathematics, and *I could not read that* is a claim about the typing."""
    result = check_expression("exp(3*t)", "exp(3*t")
    assert result.correct is None
    assert "cannot parse" in result.message


def test_the_hardened_parser_is_still_in_front_of_this_one():
    """A new route from a typed string into sympy is a new place for the
    syntax guard to be missing from. It is not missing from this one."""
    from odesuite_app.custom import ParseError

    for attack in ("sin.__class__", "(1).__class__.__bases__",
                   "[x for x in (1, 2)]"):
        result = check_expression("exp(3*t)", attack)
        assert result.correct is None, attack
        model = check_model("y' = 3*y", f"y' = {attack}")
        assert model.correct is None, attack
    # And the guard is the thing refusing them, not a parse accident.
    with pytest.raises(ParseError):
        from odesuite_app.symbolic import _parse_side

        _parse_side("sin.__class__", {})


# ---------------------------------------------------------------------------
# What a verdict says to the reader -- one rule, shared by lesson and quiz
# ---------------------------------------------------------------------------


def _question(kind: str, **fields):
    from types import SimpleNamespace

    base = dict(kind=kind, because="because the rule says so, at length",
                up_to_constant=False, equation="", answer="")
    base.update(fields)
    return SimpleNamespace(**base)


def test_a_right_answer_is_told_why():
    from odesuite_app.symbolic import mark_equivalent

    _, marking = mark_equivalent(_question("model", equation=TANK), TANK)
    assert marking.tone == "right" and marking.counts
    assert marking.headline.startswith("✓")
    assert marking.detail == "because the rule says so, at length"


def test_a_wrong_answer_is_shown_what_differs_and_not_the_reason():
    """The `because` states the rule and very nearly the answer. A lesson
    drill once showed it on a wrong expression, while the model card beside
    it and the quiz did not; a retry after reading it is not a question."""
    from odesuite_app.symbolic import mark_equivalent

    for question, typed in (
        (_question("model", equation=TANK), "y' = 2 + y/20"),
        (_question("expression", answer="exp(2*t)"), "exp(3*t)"),
    ):
        _, marking = mark_equivalent(question, typed)
        assert marking.tone == "wrong" and marking.counts
        assert "because" not in marking.detail


def test_an_unreadable_answer_is_not_a_mark():
    from odesuite_app.symbolic import mark_equivalent

    _, marking = mark_equivalent(_question("expression", answer="exp(2*t)"), "")
    assert marking.tone == "undecided"
    assert not marking.counts
    assert marking.detail == ""


def test_the_screens_no_longer_grade_equivalence_themselves():
    """Three copies became one. A fourth would start the drift again."""
    from pathlib import Path

    screens = Path(__file__).parents[1] / "src" / "odesuite_app" / "screens"
    for path in screens.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for name in ("check_model(", "check_expression("):
            assert name not in text.replace("symbolic." + name, ""), (
                f"{path.name} calls {name} directly; use mark_equivalent")
