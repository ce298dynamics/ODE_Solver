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

pytest.importorskip("sympy")

import sympy as sp  # noqa: E402

from odesuite_app import lessons as content  # noqa: E402
from odesuite_app.lessons import LESSONS, generate  # noqa: E402

T = sp.Symbol("t", real=True)

TEMPLATES = [(lesson, template) for lesson in LESSONS
             for template in lesson.templates]
IDS = [f"{lesson.key}-{template.key}" for lesson, template in TEMPLATES]

#: How many draws of each template the default run checks. Enough that a
#: template broken for most of its range fails here rather than only in the
#: nightly sweep, few enough that the file stays runnable.
SAMPLE = 4


def _parse(question):
    from odesuite_app.laplace import EXTRA_FUNCTIONS
    from odesuite_app.symbolic import EquationSpec, parse_equation

    return parse_equation(
        EquationSpec(equations=[question.equation],
                     initial_conditions=question.conditions),
        extra_functions=EXTRA_FUNCTIONS,
    )


def _work_out(template, question):
    """The derivation the drill would show, produced the way it produces it."""
    from odesuite_app import laplace, steps

    parsed = _parse(question)
    if template.narrator == "laplace":
        return laplace.derive(parsed.equation, parsed.function, ics=parsed.ics)
    return steps.derive(
        parsed.equation, parsed.function,
        hints=sp.classify_ode(parsed.equation, parsed.function(T)),
        ics=parsed.ics,
    )


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


def test_the_numerical_lesson_deliberately_has_no_drill():
    """Euler and RK4 have no closed form for the grader to substitute into, so
    a drill there could never say "right". Offering one anyway would be the
    kind of stand-in this application has removed everywhere else."""
    assert content.by_key("numerical").templates == ()


@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
def test_every_template_is_well_formed(lesson, template):
    where = f"{lesson.key}/{template.key}"
    assert template.title and template.prompt and template.equation
    assert template.narrator in {"steps", "laplace"}
    assert template.slots, f"{where}: nothing to vary"
    for names, values in template.slots:
        assert values, f"{where}: slot {names!r} has no values"
        wanted = len([part for part in names.split(",")])
        if wanted > 1:
            for value in values:
                assert len(value) == wanted, (
                    f"{where}: slot {names!r} expects {wanted} values per draw"
                )


@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
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


@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
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
        if template.reject is None:
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


@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
def test_the_same_seed_always_gives_the_same_question(lesson, template):
    """The page is rebuilt on every check, so a draw that moved would change
    the question out from under someone mid-answer."""
    first = generate.draw(template, 3)
    again = generate.draw(template, 3)
    assert first == again
    assert first.key.startswith(template.key + "#")


@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
def test_no_two_draws_are_the_same_question(lesson, template):
    """A draw that differs only in a slot nothing renders is a wasted version,
    and would show up as the same question twice in a row."""
    asked = [(question.equation, question.conditions)
             for question in generate.every(template)]
    assert len(set(asked)) == len(asked), (
        f"{template.key} can ask the same question twice"
    )


@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
def test_the_seed_wraps_rather_than_running_out(lesson, template):
    made = generate.combinations(template)
    assert generate.draw(template, made) == generate.draw(template, 0)
    assert generate.draw(template, made * 3 + 2) == generate.draw(template, 2)


@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
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
    r"|(?<![\d.])[01](?=[a-zA-Z(])"   # 1t, 0s, 1e^, 1(
    r"|(?<![\d.])[01]·"           # 1·t
    r"|\+\s*-"                    # + -3
    r"|−\s*-"                     # − -3
)


@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
def test_no_draw_reads_as_machine_made(lesson, template):
    for question in generate.every(template):
        for text in (question.equation, question.prompt, question.conditions,
                     *question.hints):
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
    assert generate.tidy("y' = t**12") == "y' = t**12"


# ---------------------------------------------------------------------------
# The claim that matters: a generated question is one the app can answer
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
def test_a_sample_of_draws_is_solvable(lesson, template):
    """The default run's version of the exhaustive test below."""
    made = generate.combinations(template)
    # Spread across the pool rather than taking the first few, so a template
    # broken only at one end of its range still fails here.
    for step in range(SAMPLE):
        seed = (step * made) // SAMPLE
        _solvable(template, generate.draw(template, seed))


@pytest.mark.slow
@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
def test_every_draw_of_every_template_is_solvable(lesson, template):
    """The whole point of enumerating rather than sampling.

    Nobody wrote these questions, so nobody read them either. This is what
    stands in for having read them."""
    for question in generate.every(template):
        _solvable(template, question)


@pytest.mark.parametrize("lesson,template", TEMPLATES, ids=IDS)
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
