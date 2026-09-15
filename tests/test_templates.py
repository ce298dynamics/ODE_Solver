"""Drills: whether a generated question is a question worth being asked.

A template produces questions nobody wrote, so the usual defence -- an author
read it -- is gone. What replaces it is this file, and the strongest claim in
it is the same one `test_lessons.py` makes about the hand-written practice:
**every generated question can be solved by the app, and the app's own answer
is accepted by its own grader.** A drill that produced a question with no
answer, or one the grader rejected, would be a machine for telling someone
their correct work is wrong.

Because draws are enumerated rather than sampled, that claim can be checked
*exhaustively*. It is: `test_every_draw_of_every_template_is_solvable` runs the
real narrator over all of them. At roughly a fifth of a second each that is
most of a minute, so it carries the `slow` marker and a fixed representative
sample runs by default.

The other tests are about the two ways a generated question can be bad without
being wrong: it can read as generated (`1t`, `t**0`, `+ -3`), or it can be the
degenerate member of its family that the template was not written for.
"""

from __future__ import annotations

import re

import pytest

from .narrators import NARRATORS, narrate

pytest.importorskip("sympy")

import sympy as sp  # noqa: E402

from odesuite_app import lessons as content  # noqa: E402
from odesuite_app.lessons import LESSONS, generate  # noqa: E402

T = sp.Symbol("t", real=True)

TEMPLATES = [(lesson, template) for lesson in LESSONS
             for template in lesson.templates]
IDS = [f"{lesson.key}-{template.key}" for lesson, template in TEMPLATES]

#: Split by kind, because the two are checked by different means. A `Template`
#: produces a `Solve` and is held to being *solvable* -- narrated by the
#: technique it claims, every step verifying, its own answer accepted by the
#: grader. A `ChoiceTemplate` produces a `Choice`, which has a stored answer
#: and no narrator at all, so what there is to check is that the question is
#: well formed and that the shuffle has not misplaced anything.
SOLVE_TEMPLATES = [(lesson, template) for lesson, template in TEMPLATES
                   if template.kind == "template"]
SOLVE_IDS = [f"{lesson.key}-{template.key}"
             for lesson, template in SOLVE_TEMPLATES]
CHOICE_TEMPLATES = [(lesson, template) for lesson, template in TEMPLATES
                    if template.kind == "choice-template"]
CHOICE_IDS = [f"{lesson.key}-{template.key}"
              for lesson, template in CHOICE_TEMPLATES]
NUMERIC_TEMPLATES = [(lesson, template) for lesson, template in TEMPLATES
                     if template.kind == "numeric-template"]
NUMERIC_IDS = [f"{lesson.key}-{template.key}"
               for lesson, template in NUMERIC_TEMPLATES]

#: How many draws of each template the default run checks. Enough that a
#: template broken for most of its range fails here rather than only in the
#: nightly sweep, few enough that the file stays runnable.
SAMPLE = 4


def _parse(question):
    from odesuite_app.laplace import EXTRA_FUNCTIONS
    from odesuite_app.symbolic import parse_equation, spec_for

    # Through `spec_for`, like the screen and the lesson sweep: a drill on a
    # system is one string holding two equations, and only that helper knows
    # how to read it.
    return parse_equation(spec_for(question.equation, question.conditions),
                          extra_functions=EXTRA_FUNCTIONS)


def _work_out(template, question):
    """The derivation the drill would show, produced the way it produces it."""
    return narrate(template.narrator, _parse(question))


def _solvable(template, question):
    """Assert one generated question is one the app can actually answer."""
    from odesuite_app.symbolic import check_answer

    where = f"{template.key}: {question.equation}"
    derivation = _work_out(template, question)
    assert derivation is not None, f"{where}: no technique applies"
    assert derivation.result is not None, f"{where}: {derivation.message}"
    assert derivation.verified is not False, f"{where}: does not check out"

    unverified = [s.title for s in derivation.steps if s.verified is False]
    assert not unverified, f"{where}: these steps failed: {unverified}"

    if template.technique:
        assert derivation.technique == template.technique, (
            f"{where}: narrated as {derivation.technique}, and the drill "
            f"claims to be practice at {template.technique}"
        )

    verdict = check_answer(_parse(question), sp.sstr(derivation.result))
    assert verdict.correct is not False, (
        f"{where}: the grader rejects the app's own answer: {verdict.message}"
    )
    assert verdict.matches_conditions is not False, (
        f"{where}: the app's own answer is said to miss the conditions"
    )


# ---------------------------------------------------------------------------
# The shape of a template
# ---------------------------------------------------------------------------


def test_there_are_templates_and_they_belong_to_lessons():
    assert TEMPLATES, "no lesson offers a drill"
    keys = [template.key for _, template in TEMPLATES]
    assert len(set(keys)) == len(keys), "two templates share a key"


def test_every_lesson_has_a_drill():
    """This was once the opposite claim, and the change is worth recording.

    Euler and RK4 have no closed form to substitute into, so a `Solve` drill
    there could never say "right", and ten lessons went without one rather
    than be given a verdict that meant nothing. The substitution grader did
    not get better. What changed is that a question whose answer is a *number*
    never needed it: `NumericTemplate` is graded to a tolerance, and the seven
    lessons it reaches are exactly the ones asking for a number.

    Two of the ten needed nothing new at all -- they have closed forms, and an
    ordinary template with the systems narrator solves them -- and one takes a
    `ChoiceTemplate`, because "which of these is a solution" has four honest
    options and no natural number.
    """
    without = [lesson.key for lesson in LESSONS if not lesson.templates]
    assert without == [], f"no drill for {without}"


@pytest.mark.parametrize("lesson,template", SOLVE_TEMPLATES,
                         ids=SOLVE_IDS)
def test_every_template_is_well_formed(lesson, template):
    where = f"{lesson.key}/{template.key}"
    assert template.title and template.prompt and template.equation
    assert template.narrator in NARRATORS
    assert template.slots, f"{where}: nothing to vary"
    for names, values in template.slots:
        assert values, f"{where}: slot {names!r} has no values"
        wanted = len([part for part in names.split(",")])
        if wanted > 1:
            for value in values:
                assert len(value) == wanted, (
                    f"{where}: slot {names!r} expects {wanted} values per draw"
                )


@pytest.mark.parametrize("lesson,template", SOLVE_TEMPLATES,
                         ids=SOLVE_IDS)
def test_every_template_names_the_technique_it_drills(lesson, template):
    """A template with no technique would pass its solvability test whatever it
    happened to produce, which is a test that cannot fail."""
    if template.narrator == "laplace":
        return                       # the Laplace narrator has one technique
    assert template.technique, f"{lesson.key}/{template.key} claims nothing"


@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
def test_every_template_has_enough_draws_to_be_worth_repeating(lesson,
                                                               template):
    made = generate.combinations(template)
    assert made >= 6, (
        f"{lesson.key}/{template.key} has only {made} versions, which is not "
        "practice, it is memorisation"
    )


@pytest.mark.parametrize("lesson,template", SOLVE_TEMPLATES,
                         ids=SOLVE_IDS)
def test_every_template_offers_a_ladder_of_hints(lesson, template):
    assert len(template.hints) >= 2, (
        f"{lesson.key}/{template.key}: a hint is not a ladder"
    )
    for rung in template.hints:
        assert len(rung) > 25


def test_a_reject_predicate_actually_rejects_something():
    """A `reject` that never fires is either wrong or unnecessary, and both are
    worth knowing about."""
    for _, template in TEMPLATES:
        # `getattr`, because a `ClassifyTemplate` has no `reject` at all and is
        # right not to. Every other kind fills its question in from slots, so
        # a predicate over the drawn values is the way to keep a degenerate
        # combination out; a classify drill has no slots -- its pool is a
        # tuple of real equations somebody chose one at a time, and a draw it
        # did not want is simply a `Case` nobody wrote. `generate.draws` has
        # always read the attribute this way for the same reason.
        if getattr(template, "reject", None) is None:
            continue
        everything = list(generate._spread(template))
        kept = generate.combinations(template)
        assert kept < len(everything), (
            f"{template.key}: its reject never rejects anything"
        )
        assert kept > 0, f"{template.key}: its reject rejects everything"


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lesson,template", SOLVE_TEMPLATES,
                         ids=SOLVE_IDS)
def test_the_same_seed_always_gives_the_same_question(lesson, template):
    """The page is rebuilt on every check, so a draw that moved would change
    the question out from under someone mid-answer."""
    first = generate.draw(template, 3)
    again = generate.draw(template, 3)
    assert first == again
    assert first.key.startswith(template.key + "#")


@pytest.mark.parametrize("lesson,template", SOLVE_TEMPLATES,
                         ids=SOLVE_IDS)
def test_no_two_draws_are_the_same_question(lesson, template):
    """A draw that differs only in a slot nothing renders is a wasted version,
    and would show up as the same question twice in a row."""
    asked = [(question.equation, question.conditions)
             for question in generate.every(template)]
    assert len(set(asked)) == len(asked), (
        f"{template.key} can ask the same question twice"
    )


@pytest.mark.parametrize("lesson,template", SOLVE_TEMPLATES,
                         ids=SOLVE_IDS)
def test_the_seed_wraps_rather_than_running_out(lesson, template):
    made = generate.combinations(template)
    assert generate.draw(template, made) == generate.draw(template, 0)
    assert generate.draw(template, made * 3 + 2) == generate.draw(template, 2)


@pytest.mark.parametrize("lesson,template", SOLVE_TEMPLATES,
                         ids=SOLVE_IDS)
def test_every_slot_is_filled_in(lesson, template):
    names = set()
    for group, _ in template.slots:
        names.update(part.strip() for part in group.split(","))
    for question in generate.every(template):
        texts = (question.equation, question.prompt, question.conditions,
                 *question.hints)
        for text in texts:
            for name in names:
                assert "{" + name + "}" not in text, (
                    f"{template.key}: {name!r} was never substituted in {text!r}"
                )


#: What a question looks like when nobody tidied up after the substitution:
#: `1*y`, `t**0`, `1t`, `+ -3`. Cosmetic, and worth a test anyway -- a drill
#: whose questions look generated reads as busywork rather than as practice.
GENERATED_LOOKING = re.compile(
    r"\*\*[01](?![\d.])"          # t**0, t**1
    r"|(?<![\d.])[01](?=[^\W\d_]|\()"  # 1t, 0s, 1e^, 1(, and 1\u03c4
    r"|(?<![\d.])[01]·"           # 1·t
    r"|\+\s*-"                    # + -3
    r"|−\s*-"                     # − -3
    r"|(?<![\d.])0\*"             # 0*y\', a term that should not be there
)


def _shown(question) -> list[str]:
    """Every string a draw puts in front of somebody.

    All three question kinds pass through here, and they carry different
    fields -- a `Solve` has an equation, a `Choice` has options and a reason
    per option, a `Numeric` has a single reason and its units. Anything
    displayed is checked; nothing else is.
    """
    fields = ["prompt", "equation", "conditions", "latex", "because", "units",
              "answer", "shown"]
    out = [getattr(question, name, "") for name in fields]
    out += list(getattr(question, "hints", ()))
    out += list(getattr(question, "options", ()))
    out += list(getattr(question, "becauses", ()))
    # Strings only. `Expression.answer` is one -- it stays symbolic, so it is
    # shown and has to read properly -- while `Numeric.answer` is a float that
    # nobody ever sees, and handing that to a regular expression would fail as
    # a type error rather than as a verdict about the question.
    return [text for text in out if isinstance(text, str) and text]


@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
def test_no_draw_reads_as_machine_made(lesson, template):
    """Over every template kind, not only the ones graded by substitution.

    A generated prompt, hint or reason gives itself away exactly as an
    equation does -- "into -1y + -1t", "it is 2 ± 1i", "y(6 - 1y)" -- and
    those are not tidied, because `tidy` is for equations and these are
    sentences. The wording has to state the rule rather than interpolate a
    signed value, and this is what enforces that.
    """
    for question in generate.every(template):
        for text in _shown(question):
            found = GENERATED_LOOKING.search(text)
            assert not found, (
                f"{template.key}: {text[max(0, found.start() - 20):]!r} "
                "reads as generated"
            )


def test_tidy_leaves_the_mathematics_alone():
    assert generate.tidy("y' = 1*t**1*y") == "y' = t*y"
    assert generate.tidy("y' = 2*t**0*y") == "y' = 2*y"
    assert generate.tidy("t**2*y'' + -1*t*y' + 5*y = 0") == (
        "t**2*y'' - t*y' + 5*y = 0"
    )
    # A two-digit coefficient is not a one followed by something.
    assert generate.tidy("y' + 12*y = 10*t") == "y' + 12*y = 10*t"
    # Neither is a constant of integration. This one reached a drill: the
    # rule above used to strip the "1*" out of "C1*cos(3*t)" and leave
    # "Ccos(3*t)", which is not an expression at all.
    assert generate.tidy("C1*cos(3*t) + C2*sin(3*t)") == (
        "C1*cos(3*t) + C2*sin(3*t)"
    )
    # A zero coefficient takes its whole term with it, wherever it sits.
    assert generate.tidy("y'' + 0*y' + 9*y = 0") == "y'' + 9*y = 0"
    assert generate.tidy("y''' - 0*y'' - y' - 0*y = 0") == "y''' - y' = 0"
    assert generate.tidy("x' = 0*x + y") == "x' = y"
    # But a right-hand side of zero is the equation, not a stray term.
    assert generate.tidy("y'' + 4*y = 0") == "y'' + 4*y = 0"
    assert generate.tidy("y(0) = 5") == "y(0) = 5"
    assert generate.tidy("y' = t**12") == "y' = t**12"


# ---------------------------------------------------------------------------
# The claim that matters: a generated question is one the app can answer
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lesson,template", SOLVE_TEMPLATES,
                         ids=SOLVE_IDS)
def test_a_sample_of_draws_is_solvable(lesson, template):
    """The default run's version of the exhaustive test below."""
    made = generate.combinations(template)
    # Spread across the pool rather than taking the first few, so a template
    # broken only at one end of its range still fails here.
    for step in range(SAMPLE):
        seed = (step * made) // SAMPLE
        _solvable(template, generate.draw(template, seed))


@pytest.mark.slow
@pytest.mark.parametrize("lesson,template", SOLVE_TEMPLATES,
                         ids=SOLVE_IDS)
def test_every_draw_of_every_template_is_solvable(lesson, template):
    """The whole point of enumerating rather than sampling.

    Nobody wrote these questions, so nobody read them either. This is what
    stands in for having read them."""
    for question in generate.every(template):
        _solvable(template, question)


@pytest.mark.parametrize("lesson,template", SOLVE_TEMPLATES,
                         ids=SOLVE_IDS)
def test_a_wrong_answer_to_a_generated_question_is_rejected(lesson, template):
    """The grader has to be able to say no, or the streak means nothing."""
    from odesuite_app.symbolic import check_answer

    question = generate.draw(template, 0)
    verdict = check_answer(_parse(question), "t**7 + 5")
    assert verdict.correct is not True


# ---------------------------------------------------------------------------
# Streaks, and where they are recorded
# ---------------------------------------------------------------------------


@pytest.fixture()
def store(tmp_path, monkeypatch):
    from odesuite_app import progress

    monkeypatch.setattr(progress, "directory", lambda: tmp_path / "odesuite")
    return progress


def test_a_streak_builds_and_a_miss_resets_it(store):
    bucket = store.drill_key("separable")
    for expected in range(1, store.MASTERED_STREAK + 1):
        store.record(bucket, "growth", store.State.CORRECT)
        answer = store.load()[bucket]["growth"]
        assert answer.streak == expected
        assert answer.mastered is (expected >= store.MASTERED_STREAK)

    store.record(bucket, "growth", store.State.ATTEMPTED)
    answer = store.load()[bucket]["growth"]
    assert answer.streak == 0
    assert not answer.mastered
    assert answer.correct, "the tick itself is not taken away, only the streak"
    assert answer.right == store.MASTERED_STREAK


def test_drills_are_counted_in_their_own_bucket(store):
    """An unbounded number of generated answers must not disturb the count of
    the practice questions, whose denominator is fixed."""
    lesson = content.by_key("separable")
    for _ in range(store.MASTERED_STREAK):
        store.record(store.drill_key(lesson.key), "growth",
                     store.State.CORRECT)
    everything = store.load()

    assert store.counts(lesson.key, len(lesson.questions), everything) == (
        0, len(lesson.questions)
    )
    assert store.drills(lesson.key, lesson.templates, everything) == (
        1, len(lesson.templates)
    )


def test_a_lesson_with_no_drills_reports_none(store):
    assert store.drills("numerical", (), store.load()) == (0, 0)


def test_drills_accepts_keys_as_well_as_templates(store):
    bucket = store.drill_key("linear")
    for _ in range(store.MASTERED_STREAK):
        store.record(bucket, "constant-p", store.State.CORRECT)
    everything = store.load()
    assert store.drills("linear", ["constant-p", "variable-p"],
                        everything) == (1, 2)


# ---------------------------------------------------------------------------
# Generated multiple choice
#
# A `ChoiceTemplate` has a stored answer and no narrator, so "is it solvable"
# is the wrong question. What can go wrong instead is that the question is
# malformed, or that the per-draw shuffle has moved an option away from its own
# reason -- which would show a tick or a cross explaining somebody else's
# answer.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lesson,template", CHOICE_TEMPLATES, ids=CHOICE_IDS)
def test_every_choice_template_is_well_formed(lesson, template):
    where = f"{lesson.key}/{template.key}"
    assert template.title and template.prompt
    assert len(template.options) >= 3, f"{where}: too few options to choose"
    assert len(template.becauses) == len(template.options), (
        f"{where}: {len(template.becauses)} reasons for "
        f"{len(template.options)} options"
    )
    assert 0 <= template.answer < len(template.options), f"{where}: bad answer"
    assert template.slots, f"{where}: nothing to vary"


@pytest.mark.parametrize("lesson,template", CHOICE_TEMPLATES, ids=CHOICE_IDS)
def test_every_choice_draw_is_a_well_formed_question(lesson, template):
    for question in generate.every(template):
        where = f"{lesson.key}/{template.key}#{question.key}"
        assert question.kind == "choice", where
        assert len(question.options) == len(template.options), where
        assert len(question.becauses) == len(question.options), where
        assert 0 <= question.answer < len(question.options), where
        for option in question.options:
            assert option.strip(), f"{where}: an option came out empty"
        for reason in question.becauses:
            assert len(reason) > 20, f"{where}: {reason!r} explains nothing"


@pytest.mark.parametrize("lesson,template", CHOICE_TEMPLATES, ids=CHOICE_IDS)
def test_the_right_answer_moves_between_draws(lesson, template):
    """The whole reason the options are shuffled. Leaving the answer where the
    author wrote it would put it at the same index in every version, so the
    drill would teach the position rather than the mathematics."""
    if generate.combinations(template) < 4:
        pytest.skip("too few draws to expect movement")
    seen = {question.answer for question in generate.every(template)}
    assert len(seen) > 1, (
        f"{lesson.key}/{template.key}: the answer sits at index "
        f"{seen.pop()} in every version"
    )


@pytest.mark.parametrize("lesson,template", CHOICE_TEMPLATES, ids=CHOICE_IDS)
def test_each_reason_stays_with_its_own_option(lesson, template):
    """The reason is shown for whichever option was *picked*, so a reason that
    drifted onto a neighbouring option would explain somebody else's answer --
    worse than offering no reason at all."""
    written = dict(zip(template.options, template.becauses))
    for question in generate.every(template):
        for option, reason in zip(question.options, question.becauses):
            # The pairing survives formatting, so compare on the unformatted
            # text where a template has no slots in its options.
            if option in written:
                assert reason == written[option], (
                    f"{lesson.key}/{template.key}: {option!r} was explained "
                    f"by another option's reason"
                )


@pytest.mark.parametrize("lesson,template", CHOICE_TEMPLATES, ids=CHOICE_IDS)
def test_the_grader_accepts_the_drawn_answer_and_nothing_else(lesson,
                                                              template):
    for question in generate.every(template):
        assert content.grade_choice(question, question.answer) is True
        for index in range(len(question.options)):
            if index != question.answer:
                assert content.grade_choice(question, index) is False


@pytest.mark.parametrize("lesson,template", CHOICE_TEMPLATES, ids=CHOICE_IDS)
def test_no_choice_draw_reads_as_machine_made(lesson, template):
    for question in generate.every(template):
        texts = [question.prompt, question.latex,
                 *question.options, *question.becauses]
        for text in texts:
            found = GENERATED_LOOKING.search(text)
            assert not found, (
                f"{template.key}: {text[max(0, found.start() - 20):]!r} "
                "reads as generated"
            )


@pytest.mark.parametrize("lesson,template", CHOICE_TEMPLATES, ids=CHOICE_IDS)
def test_the_same_seed_always_gives_the_same_choice(lesson, template):
    for seed in (0, 1, 7, 30):
        first = generate.draw(template, seed)
        again = generate.draw(template, seed)
        assert first.options == again.options
        assert first.answer == again.answer


def test_every_unit_can_now_be_quizzed():
    """The number this work exists to change. Before generated multiple choice
    the series unit had no templates at all, so it offered no check-up -- and a
    unit you cannot examine is a unit you cannot tell you have finished."""
    from odesuite_app.lessons import UNITS

    without = [unit.key for unit in UNITS if not unit.quizzable]
    assert not without, f"these units still offer no quiz: {without}"


# ---------------------------------------------------------------------------
# Numeric drills: graded to a tolerance, and checked against the real tools
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lesson,template", NUMERIC_TEMPLATES,
                         ids=NUMERIC_IDS)
def test_every_numeric_template_is_well_formed(lesson, template):
    where = f"{lesson.key}/{template.key}"
    assert template.title and template.prompt and template.answer
    assert template.slots, f"{where}: nothing to vary"
    assert template.because, f"{where}: a number with no account of itself"
    assert 0 < template.tolerance < 1, f"{where}: {template.tolerance}"


@pytest.mark.parametrize("lesson,template", NUMERIC_TEMPLATES,
                         ids=NUMERIC_IDS)
def test_every_numeric_draw_has_a_real_finite_answer(lesson, template):
    import math

    for question in generate.every(template):
        assert math.isfinite(question.answer), (
            f"{template.key}: {question.prompt} has no usable answer"
        )
        assert question.because, f"{template.key}: no reason given"


@pytest.mark.parametrize("lesson,template", NUMERIC_TEMPLATES,
                         ids=NUMERIC_IDS)
def test_the_grader_accepts_the_answer_and_rejects_a_near_miss(lesson,
                                                               template):
    """The tolerance has to admit an honest rounding and refuse a wrong step.

    Both halves matter. Too tight and somebody who worked to the number of
    decimal places the prompt asked for is marked wrong; too loose and, for
    the Runge-Kutta drill, the *exact* solution slips through -- which would
    mark somebody right for having solved the equation rather than taken the
    step.
    """
    from odesuite_app.symbolic import grade_numeric

    for question in generate.every(template):
        right, _ = grade_numeric(question, repr(question.answer))
        assert right is True, f"{template.key}: rejects its own answer"

        # A rounding at the precision the prompt asks for must pass.
        places = 4 if "four decimal places" in question.prompt else 6
        rounded = round(question.answer, places)
        right, _ = grade_numeric(question, repr(rounded))
        assert right is True, (
            f"{template.key}: {question.answer} rounded to {places} places "
            "is rejected"
        )

        # A wrong answer of the size these questions produce must fail.
        off = question.answer + 10 * template.tolerance * max(
            1.0, abs(question.answer)
        )
        right, _ = grade_numeric(question, repr(off))
        assert right is False, f"{template.key}: accepts {off}"


@pytest.mark.parametrize("text", ["", "   ", "banana", "y + 1", "sqrt(-1)"])
def test_the_grader_declines_rather_than_marking_it_wrong(text):
    """Three verdicts, not two. "I could not read that" is a claim about the
    typing and must never be reported as a claim about the mathematics."""
    from odesuite_app.lessons import Numeric
    from odesuite_app.symbolic import grade_numeric

    right, message = grade_numeric(Numeric("k", "p", 1.0), text)
    assert right is None, text
    assert message


def _stepped(a: float, y0: float, h: float, method: str) -> float:
    """One step of `method` on ``y' = a*y``, through the app's own walker."""
    import numpy as np

    from odesuite import ODEProblem
    from odesuite_app import byhand

    problem = ODEProblem(f=lambda t, y: np.array([a * y[0]]),
                         t_span=(0.0, 10 * h), y0=np.array([float(y0)]))
    return float(byhand.walk(problem, method, h, 1).rows[0].y_next[0])


def test_the_euler_drill_agrees_with_the_by_hand_walker():
    """The declarative answer against the machinery the lesson teaches.

    A `Solve` drill cannot disagree with the rest of the application, because
    substitution is the grading. A stored number can, so it is checked here
    against `byhand.walk` -- the same function the Methods by Hand screen
    steps with.
    """
    template = content.by_key("numerical").templates[0]
    checked = 0
    for index, slots in enumerate(generate.draws(template)):
        question = generate.draw(template, index)
        walked = _stepped(slots["a"], slots["y0"], slots["h"], "euler")
        assert question.answer == pytest.approx(walked, abs=1e-12), (
            f"{question.prompt}: drill says {question.answer}, "
            f"byhand.walk says {walked}"
        )
        checked += 1
    assert checked >= 20


def test_the_runge_kutta_drill_agrees_with_the_walker_and_not_with_euler():
    """Against the walker, and against the wrong answer that matters.

    Not against the exact solution, which was the first thing tried and was
    wrong: across these step sizes the method agrees with it to between seven
    and four decimal places, so no tolerance that accepts an honest rounding
    could separate them. That is fourth-order accuracy working, not a drill
    that cannot tell. The answer this question really produces by mistake is
    an *Euler* step, and that is a hundred times further away.
    """
    from odesuite_app.symbolic import grade_numeric

    template = content.by_key("rungekutta").templates[0]
    for index, slots in enumerate(generate.draws(template)):
        question = generate.draw(template, index)
        walked = _stepped(slots["a"], 1.0, slots["h"], "rk4")
        assert question.answer == pytest.approx(walked, abs=1e-12), (
            f"{question.prompt}: drill says {question.answer}, "
            f"byhand.walk says {walked}"
        )
        euler = _stepped(slots["a"], 1.0, slots["h"], "euler")
        right, _ = grade_numeric(question, repr(euler))
        assert right is False, (
            f"{question.prompt}: an Euler step of {euler} is accepted, so the "
            "drill does not distinguish the two methods"
        )


def test_the_equilibrium_drill_agrees_with_the_phase_line():
    import numpy as np

    from odesuite import ODEProblem
    from odesuite_app import analysis

    template = content.by_key("equilibria").templates[0]
    for index, slots in enumerate(generate.draws(template)):
        question = generate.draw(template, index)
        a, b = float(slots["a"]), float(slots["b"])
        problem = ODEProblem(f=lambda t, y: np.array([a * y[0] - b * y[0] ** 2]),
                             t_span=(0.0, 1.0), y0=np.array([0.5]))
        found = [point.value
                 for point in analysis.phase_line(problem, (-1.0, 12.0))]
        assert any(abs(value - question.answer) < 1e-6 for value in found), (
            f"{question.prompt}: {question.answer} is not among the equilibria "
            f"the phase line finds, {found}"
        )


def test_the_determinant_drill_agrees_with_numpy():
    import numpy as np

    template = content.by_key("phase-portraits").templates[0]
    for index, slots in enumerate(generate.draws(template)):
        question = generate.draw(template, index)
        matrix = np.array([[slots["a"], slots["b"]],
                           [slots["c"], slots["d"]]], dtype=float)
        assert question.answer == pytest.approx(float(np.linalg.det(matrix)))


def test_the_convolution_drill_agrees_with_the_integral():
    """The step response is the convolution with the constant one, which is
    the integral of the impulse response -- so sympy can be asked directly."""
    import sympy as sp

    template = content.by_key("convolution").templates[0]
    tau = sp.Symbol("tau", positive=True)
    for index, slots in enumerate(generate.draws(template)):
        question = generate.draw(template, index)
        integral = sp.integrate(sp.exp(-sp.Rational(str(slots["a"])) * tau),
                                (tau, 0, sp.Rational(str(slots["t0"]))))
        assert question.answer == pytest.approx(float(integral))


def test_the_terminal_velocity_drill_is_where_the_forces_balance():
    template = content.by_key("motion").templates[0]
    for index, slots in enumerate(generate.draws(template)):
        question = generate.draw(template, index)
        # The equation carries the mass now: m·v' = -m·9.8 - k·v, so the
        # balance is between the weight and the drag, not between g and it.
        residual = (-float(slots["m"]) * 9.8
                    - float(slots["k"]) * question.answer)
        assert abs(residual) < 1e-9, (
            f"{question.prompt}: the acceleration at {question.answer} is "
            f"{residual}, not zero"
        )


def test_the_slope_drill_is_the_right_hand_side_at_the_point():
    template = content.by_key("slopefields").templates[0]
    for index, slots in enumerate(generate.draws(template)):
        question = generate.draw(template, index)
        wanted = slots["a"] * slots["y0"] + slots["b"] * slots["t0"]
        assert question.answer == pytest.approx(float(wanted))

