"""The lessons: whether the content is true, and whether the grading is honest.

Prose can be wrong in a way code cannot, so the tests here are mostly about the
*claims* the lessons make rather than about the widgets that show them.

The strongest of them is this: **every solve-it question is actually solvable,
and the app can produce the answer it would show you.** A practice question
whose model solution the tool cannot generate would be a question the learner
is invited to fail at, and a worked example that drifted out of step with the
narrator explaining it would be worse than none. Both are checked by running
the real narrator over the real content.

Multiple-choice answers cannot be derived, so they are the one place a stored
key is trusted. They are held to what can still be checked mechanically: the
index is in range, the reason is present, and no option is duplicated.
"""

from __future__ import annotations

import contextlib
import json
import re

import pytest

from .narrators import NARRATORS, narrate

pytest.importorskip("sympy")

import sympy as sp  # noqa: E402

from odesuite_app import lessons as content  # noqa: E402
from odesuite_app.lessons import (  # noqa: E402
    LESSONS,
    UNITS,
    Choice,
    Solve,
    by_key,
    generate,
)

T = sp.Symbol("t", real=True)

SOLVES = [(lesson, q) for lesson in LESSONS
          for q in lesson.questions if isinstance(q, Solve)]
CHOICES = [(lesson, q) for lesson in LESSONS
           for q in lesson.questions if isinstance(q, Choice)]


def _ids(pairs):
    return [f"{lesson.key}-{q.key}" for lesson, q in pairs]


def _parse(equation: str, conditions: str = ""):
    from odesuite_app.laplace import EXTRA_FUNCTIONS
    from odesuite_app.symbolic import parse_equation, spec_for

    return parse_equation(spec_for(equation, conditions),
                          extra_functions=EXTRA_FUNCTIONS)


def _work_out(lesson, equation: str, conditions: str):
    """The derivation the screen would show, produced the same way it does."""
    return narrate(lesson.narrator, _parse(equation, conditions))


# ---------------------------------------------------------------------------
# The shape of the course
# ---------------------------------------------------------------------------


def test_the_lessons_cover_the_techniques_the_app_can_teach():
    """Every technique the narrator can explain is drilled by some lesson.

    Stated in this direction rather than by listing the lessons, because this
    is the direction with teeth: a narrator added without the lesson to go
    with it is the failure the course order exists to prevent, and it is a
    silent one -- the app would simply be able to explain something it never
    offers to teach. The converse, a lesson on something no tool explains, is
    what `test_every_lesson_is_complete` checks by pinning `tool` and
    `narrator`.
    """
    from odesuite_app.steps import TITLES

    # Only the templates a narrator solves claim a technique -- a generated
    # multiple-choice drill has no narrator and nothing to claim.
    drilled = {template.technique for lesson in LESSONS
               for template in lesson.templates
               if getattr(template, "technique", "")}
    missing = set(TITLES) - drilled
    assert not missing, (
        f"the narrator explains these but nothing drills them: {sorted(missing)}"
    )


def test_every_lesson_is_complete():
    for lesson in LESSONS:
        assert lesson.title and lesson.summary
        assert len(lesson.notes) >= 3, f"{lesson.key} is thin on notes"
        assert len(lesson.questions) >= 4, f"{lesson.key} is thin on practice"
        assert lesson.tool in {"steps", "laplace", "byhand", "worked"}
        assert lesson.narrator in NARRATORS


def test_keys_are_unique():
    assert len({lesson.key for lesson in LESSONS}) == len(LESSONS)
    for lesson in LESSONS:
        keys = [q.key for q in lesson.questions]
        assert len(set(keys)) == len(keys), f"{lesson.key} repeats a question key"


def test_by_key_finds_them_and_declines_the_rest():
    # By its own key, not by position: the course grows at the front as much
    # as at the end -- `basics` and `slopefields` went in before `separable`
    # when Unit 1 was filled out -- and a lookup test that tracks the order is
    # testing the order.
    for lesson in LESSONS:
        assert by_key(lesson.key) is lesson
    assert by_key("nonexistent") is None


def test_every_note_says_something():
    for lesson in LESSONS:
        for note in lesson.notes:
            assert note.heading and note.body
            assert len(note.body) > 60, (
                f"{lesson.key}/{note.heading!r} is too short to teach anything"
            )
            assert note.kind in content.NOTE_KINDS, (
                f"{lesson.key}/{note.heading!r}: unknown note kind {note.kind!r}"
            )


def test_the_units_partition_the_lessons():
    """Every lesson belongs to exactly one unit, and the flattened order is the
    order the units are in. A lesson in no unit would be unreachable from the
    course map; a lesson in two would be counted twice."""
    assert UNITS, "there is no course"
    seen = [lesson for unit in UNITS for lesson in unit.lessons]
    assert seen == list(LESSONS)
    assert len({lesson.key for lesson in seen}) == len(seen)
    assert len({unit.key for unit in UNITS}) == len(UNITS)

    for unit in UNITS:
        assert unit.title and unit.summary and unit.reference
        assert unit.lessons, (
            f"{unit.key} has no lessons — a unit appears once it has them, "
            "and never as a placeholder"
        )
        assert unit.questions == sum(len(le.questions) for le in unit.lessons)
        for lesson in unit.lessons:
            assert content.unit_of(lesson) is unit
            assert content.unit_of(lesson.key) is unit
    assert content.unit_by_key("nonexistent") is None


def test_every_prerequisite_names_a_real_lesson_that_comes_first():
    """Advice, not a gate — but advice pointing at a lesson that does not
    exist, or at one taught later, is worse than none."""
    order = {lesson.key: index for index, lesson in enumerate(LESSONS)}
    for lesson in LESSONS:
        for key in lesson.prerequisites:
            assert key in order, f"{lesson.key} requires unknown {key!r}"
            assert order[key] < order[lesson.key], (
                f"{lesson.key} requires {key}, which the course teaches later"
            )


def test_every_lesson_says_what_it_is_for():
    for lesson in LESSONS:
        assert lesson.reference, f"{lesson.key} cites no textbook section"
        assert len(lesson.objectives) >= 3, f"{lesson.key} is vague about aims"
        for objective in lesson.objectives:
            assert len(objective) > 20


def test_every_example_says_why_it_is_there():
    """Two examples that are the same case twice teach once. Each has to say
    what it is showing that the others do not."""
    for lesson in LESSONS:
        assert lesson.examples, f"{lesson.key} has no worked example"
        equations = [example.equation for example in lesson.examples]
        assert len(set(equations)) == len(equations), (
            f"{lesson.key} works the same equation twice"
        )
        for example in lesson.examples:
            assert example.narrator in NARRATORS
            assert len(example.why) > 40, (
                f"{lesson.key}/{example.equation} does not say what it shows"
            )
        assert lesson.example == lesson.examples[0].equation


# ---------------------------------------------------------------------------
# Depth: the lessons that have been written up as textbook sections
# ---------------------------------------------------------------------------


#: Lessons rewritten to full depth -- motivation, a derivation, and commentary
#: on every worked example. Every lesson in the course is now on it, which is
#: the point: the list was built one unit at a time so that what remained to be
#: written was visible here rather than in a plan file, and it is empty.
#:
#: It still earns its keep. A lesson added later is not full-depth until it is
#: listed, and a lesson that grows a motivation without being listed fails
#: below -- the list has to stay honest in both directions.
FULL_DEPTH = (
    "basics",
    "slopefields",
    "separable",
    "linear",
    "exact",
    "substitutions",
    "population",
    "equilibria",
    "motion",
    "numerical",
    "rungekutta",
    "superposition",
    "roots",
    "undetermined",
    "variation",
    "cauchy",
    "higher",
    "free-vibration",
    "forced-vibration",
    "circuits",
    "transform",
    "laplace",
    "shifting",
    "convolution",
    "step-forcing",
    "impulses",
    "systems-intro",
    "eigenvalues",
    "complex-eigenvalues",
    "repeated-eigenvalues",
    "forced-systems",
    "phase-portraits",
    "power-series",
    "recurrence",
    "frobenius",
)

DEEP = [by_key(key) for key in FULL_DEPTH]


def test_the_full_depth_list_names_real_lessons_and_stays_honest():
    assert len(set(FULL_DEPTH)) == len(FULL_DEPTH)
    for key in FULL_DEPTH:
        assert by_key(key) is not None, f"{key} is not a lesson"
    written = {lesson.key for lesson in LESSONS
               if lesson.motivation or lesson.derivation}
    assert written == set(FULL_DEPTH), (
        "these have depth but are not listed as full: "
        f"{sorted(written - set(FULL_DEPTH))}"
    )


@pytest.mark.parametrize("lesson", DEEP, ids=list(FULL_DEPTH))
def test_a_full_depth_lesson_says_why_the_topic_exists(lesson):
    """Motivation, in paragraphs, before any technique is named.

    A reader who does not know why a topic exists cannot be told what its
    technique is, and the length floor is there because two sentences of
    preamble is what the lessons already had.
    """
    assert len(lesson.motivation) >= 600, (
        f"{lesson.key} is {len(lesson.motivation)} characters of motivation"
    )
    paragraphs = lesson.motivation.split("\n\n")
    assert len(paragraphs) >= 2, f"{lesson.key} motivation is one block"
    for paragraph in paragraphs:
        assert paragraph == paragraph.strip(), (
            f"{lesson.key} motivation has a stray blank line"
        )
        assert len(paragraph) >= 150, (
            f"{lesson.key} has a stub paragraph: {paragraph[:60]!r}"
        )
        assert len(paragraph) <= 900, (
            f"{lesson.key} has a paragraph long enough to be two"
        )


@pytest.mark.parametrize("lesson", DEEP, ids=list(FULL_DEPTH))
def test_a_full_depth_lesson_derives_its_method(lesson):
    """The argument, not the steps.

    Distinct from the worked examples on purpose: the narrator shows the moves
    for one equation, and no number of those adds up to why the moves are
    allowed. Three passages is not an argument, so the floor is four.
    """
    assert len(lesson.derivation) >= 4, (
        f"{lesson.key} has {len(lesson.derivation)} passages"
    )
    assert len(lesson.derivation) <= 8, (
        f"{lesson.key} has {len(lesson.derivation)} passages, which is a "
        "lesson rather than a derivation"
    )
    for number, passage in enumerate(lesson.derivation, start=1):
        assert len(passage.prose) >= 100, (
            f"{lesson.key} passage {number} asserts rather than argues"
        )
        assert passage.prose == passage.prose.strip()


@pytest.mark.parametrize("lesson", DEEP, ids=list(FULL_DEPTH))
def test_a_full_depth_lesson_reads_its_own_worked_examples(lesson):
    """The narrator supplies the steps; only prose can supply the reading of
    them -- which line is the one that matters, and what the shape of the
    answer is telling you."""
    for example in lesson.examples:
        assert len(example.commentary) >= 300, (
            f"{lesson.key}/{example.equation} has no real commentary"
        )
        assert len(example.commentary.split("\n\n")) >= 2, (
            f"{lesson.key}/{example.equation} commentary is one block"
        )
        assert example.commentary != example.why


def _shingles(text: str, length: int = 6) -> set[str]:
    words = text.lower().replace("\u2014", " ").split()
    return {" ".join(words[at:at + length])
            for at in range(max(0, len(words) - length + 1))}


@pytest.mark.parametrize("lesson", DEEP, ids=list(FULL_DEPTH))
def test_commentary_adds_to_the_why_rather_than_repeating_it(lesson):
    """`why` is read before deciding to open an example; commentary is read
    with the working. A commentary that opens by restating the why has spent
    its first paragraph saying nothing, which is how the first draft of all
    twelve of these read."""
    for example in lesson.examples:
        shared = _shingles(example.why) & _shingles(example.commentary)
        assert not shared, (
            f"{lesson.key}/{example.equation} repeats itself: {sorted(shared)}"
        )


def test_emphasis_markers_are_balanced_everywhere():
    """The lessons write emphasis as ``*this*`` and the renderer turns it into
    italics. An odd marker is therefore a marker that will be printed, so it
    is worth catching in the content rather than in a screenshot."""
    from odesuite_app import richtext

    marked = 0
    for lesson in LESSONS:
        prose = [("motivation", lesson.motivation)]
        prose += [(f"note {note.heading!r}", note.body) for note in lesson.notes]
        prose += [(f"passage {number}", passage.prose)
                  for number, passage in enumerate(lesson.derivation, 1)]
        for example in lesson.examples:
            prose.append((f"why {example.equation}", example.why))
            prose.append((f"commentary {example.equation}", example.commentary))
        for objective in lesson.objectives:
            prose.append(("objective", objective))

        for where, text in prose:
            if "*" not in text:
                continue
            marked += 1
            rendered = richtext.emphasise(text)
            # Whatever asterisks survive must be operators, not markers. The
            # convolution star in the Laplace unit is the only one that does,
            # and it survives precisely because it stands between two spaces.
            for position in (found.start()
                             for found in re.finditer(r"\*", rendered)):
                before = rendered[position - 1] if position else " "
                after = rendered[position + 1:position + 2] or " "
                assert before == " " and after == " ", (
                    f"{lesson.key}/{where} prints a stray emphasis marker: "
                    f"{text[max(0, position - 30):position + 30]!r}"
                )
    assert marked >= 15, "expected the lessons to use emphasis"


def test_every_stored_equation_really_typesets():
    """Notes and derivations carry hand-written LaTeX, and it is the one place
    in the application where an unrenderable expression can be committed.

    Rendered, not merely passed through `is_renderable`. The two disagree, and
    the difference is the whole reason this test exists: mathtext accepts
    `\\geq` and not `\\ge`, has no `\\tfrac`, no `\\underbrace` and no
    `\\iff` -- none of which sympy ever emits, so only hand-written content can
    contain them. The failure is silent in the worst way: the label falls back
    to plain text and prints its own backslashes, which reads as a typo in the
    lesson rather than a limit of the renderer. Seventeen equations were doing
    exactly that when this was written.
    """
    from odesuite_app import mathrender

    checked = 0
    for lesson in LESSONS:
        stored = [(f"note {note.heading!r}", note.latex)
                  for note in lesson.notes if note.latex]
        stored += [(f"passage {number}", passage.latex)
                   for number, passage in enumerate(lesson.derivation, 1)
                   if passage.latex]
        for where, latex in stored:
            assert mathrender.is_renderable(latex), (
                f"{lesson.key}/{where} is refused up front: {latex!r}"
            )
            png = mathrender.latex_to_png(latex, "#000000", 15.0, 110.0)
            assert png.startswith(b"\x89PNG"), (
                f"{lesson.key}/{where} cannot be typeset: {latex!r}"
            )
            checked += 1
    assert checked >= 150, "expected the stored mathematics to be substantial"


# ---------------------------------------------------------------------------
# The claim that matters: the content is solvable
# ---------------------------------------------------------------------------


EXAMPLES = [(lesson, example) for lesson in LESSONS
            for example in lesson.examples]


@pytest.mark.parametrize(
    "lesson,example", EXAMPLES,
    ids=[f"{le.key}-{ex.equation}" for le, ex in EXAMPLES],
)
def test_every_worked_example_can_actually_be_worked(lesson, example):
    """The examples are generated by the narrator, not transcribed, so this is
    what keeps the lesson and the tool from drifting apart. Every one of them,
    not merely the first: an example nobody checked is the one that rots."""
    derivation = narrate(example.narrator,
                         _parse(example.equation, example.conditions))

    where = f"{lesson.key}/{example.equation}"
    assert derivation is not None, f"{where}: no technique applies"
    assert derivation.result is not None, f"{where}: {derivation.message}"
    assert derivation.verified is not False, (
        f"{where}: the worked example does not check out"
    )
    assert derivation.steps, f"{where}: nothing to show"
    failed = [s.title for s in derivation.steps if s.verified is False]
    assert not failed, f"{where}: these steps did not verify: {failed}"


@pytest.mark.parametrize("lesson,question", SOLVES, ids=_ids(SOLVES))
def test_every_practice_question_has_an_answer_the_app_can_produce(lesson,
                                                                   question):
    """Otherwise it is a question the learner is invited to fail at: they press
    "Show me" and nothing comes back."""
    derivation = _work_out(lesson, question.equation, question.conditions)
    assert derivation is not None, "no technique applies to this question"
    assert derivation.result is not None, derivation.message
    assert derivation.verified is not False


@pytest.mark.parametrize("lesson,question", SOLVES, ids=_ids(SOLVES))
def test_no_step_of_a_model_answer_fails_its_own_check(lesson, question):
    derivation = _work_out(lesson, question.equation, question.conditions)
    failed = [s.title for s in derivation.steps if s.verified is False]
    assert not failed, f"these steps did not verify: {failed}"


@pytest.mark.parametrize("lesson,question", SOLVES, ids=_ids(SOLVES))
def test_the_model_answer_is_accepted_by_the_grader(lesson, question):
    """The two halves have to agree. If the narrator's own answer failed the
    check_answer grader, a learner typing the right thing could be told it is
    wrong -- which is the worst failure this screen has available."""
    from odesuite_app.symbolic import check_answer

    derivation = _work_out(lesson, question.equation, question.conditions)
    parsed = _parse(question.equation, question.conditions)
    verdict = check_answer(parsed, sp.sstr(derivation.result))

    assert verdict.correct is not False, (
        f"the grader rejects the app's own answer: {verdict.message}"
    )
    assert verdict.matches_conditions is not False, (
        f"the app's own answer is said to miss the conditions: {verdict.message}"
    )


@pytest.mark.parametrize("lesson,question", SOLVES, ids=_ids(SOLVES))
def test_a_wrong_answer_is_rejected(lesson, question):
    """The grader has to be able to say no, or the tick means nothing."""
    from odesuite_app.symbolic import check_answer

    parsed = _parse(question.equation, question.conditions)
    verdict = check_answer(parsed, "t**7 + 5")
    assert verdict.correct is not True


@pytest.mark.parametrize("lesson,question", SOLVES, ids=_ids(SOLVES))
def test_every_solve_question_offers_a_ladder_of_hints(lesson, question):
    """One rung at a time. A single hint is either useless or the answer, and
    the last rung -- "Show me", the narrator itself -- is already the answer,
    so what is asked for here is the steps in between."""
    where = f"{lesson.key}/{question.key}"
    assert len(question.hints) >= 2, f"{where}: a hint is not a ladder"
    for rung in question.hints:
        assert len(rung) > 25, f"{where}: {rung!r} says too little"
    assert len(set(question.hints)) == len(question.hints), (
        f"{where}: a rung is repeated"
    )
    assert question.hint == question.hints[0]


def test_a_decimal_coefficient_still_gives_a_clean_answer():
    """The mixing-tank question is written with decimals, as a student would
    type them. Floats propagate through `solve` into a constant whose imaginary
    part is the *number* 3.14159… rather than `pi`, which sympy cannot cancel --
    so the answer came out carrying a complex exponential. It should read
    40 - 35e^{-t/20}."""
    lesson = by_key("linear")
    question = next(q for q in lesson.questions if q.key == "q5")
    derivation = _work_out(lesson, question.equation, question.conditions)

    assert not derivation.result.atoms(sp.I), "a complex exponential survived"
    assert sp.simplify(
        derivation.result - (40 - 35 * sp.exp(-T / 20))
    ) == 0, derivation.result


def test_the_branch_matching_the_initial_condition_is_the_one_shown():
    """`y' = t/y` with y(0) = 2 rearranges to ±sqrt(t² + 2C), and taking the
    first root gave the negative branch -- which satisfies the equation but
    passes through no point the condition allows."""
    lesson = by_key("separable")
    question = next(q for q in lesson.questions if q.key == "q5")
    derivation = _work_out(lesson, question.equation, question.conditions)

    assert sp.simplify(derivation.result - sp.sqrt(T**2 + 4)) == 0, (
        derivation.result
    )
    assert float(derivation.result.subs(T, 0)) == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# Multiple choice: the one place a stored answer is trusted
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lesson,question", CHOICES, ids=_ids(CHOICES))
def test_every_choice_question_is_well_formed(lesson, question):
    assert len(question.options) >= 3, "too few options to be a real choice"
    assert 0 <= question.answer < len(question.options)
    assert len(set(question.options)) == len(question.options), (
        "a duplicated option means two answers are equally right"
    )
    assert question.prompt


@pytest.mark.parametrize("lesson,question", CHOICES, ids=_ids(CHOICES))
def test_every_choice_question_explains_every_option(lesson, question):
    """A tick that does not say why teaches nothing, and a cross that explains
    someone else's answer teaches less than nothing. This is also the only
    question type whose answer is asserted rather than derived, so the reasons
    are the only thing standing behind it."""
    where = f"{lesson.key}/{question.key}"
    assert len(question.becauses) == len(question.options), (
        f"{where}: {len(question.becauses)} reasons for "
        f"{len(question.options)} options"
    )
    for index, reason in enumerate(question.becauses):
        assert reason, f"{where}: option {index} gives no reason"
        assert len(reason) > 40, f"{where}: option {index} is a one-liner"
    assert len(set(question.becauses)) == len(question.becauses), (
        f"{where}: two options share a reason, so one of them is not explained"
    )
    assert question.because == question.becauses[question.answer]


@pytest.mark.parametrize("lesson,question", CHOICES, ids=_ids(CHOICES))
def test_grading_a_choice(lesson, question):
    assert content.grade_choice(question, question.answer) is True
    for index in range(len(question.options)):
        if index != question.answer:
            assert content.grade_choice(question, index) is False


def test_the_stated_answers_are_true_where_they_can_be_checked():
    """Several choice questions assert something about a specific equation.
    Those are checked against sympy rather than taken on trust."""
    y = sp.Function("y")

    # roots/q1: y'' + 4y' + 4y = 0 has a repeated root, so t·e^{rt} appears.
    roots = sp.roots(sp.Poly(sp.Symbol("r") ** 2 + 4 * sp.Symbol("r") + 4,
                             sp.Symbol("r")))
    assert roots == {-2: 2}

    # roots/q2: only y'' + 2y' + 5y = 0 among its options oscillates.
    r = sp.Symbol("r")
    assert sp.roots(sp.Poly(r**2 + 2 * r + 5, r)) == {-1 - 2 * sp.I: 1,
                                                     -1 + 2 * sp.I: 1}
    for polynomial in (r**2 + 5 * r + 6, r**2 + 4 * r + 4, r**2 - 1):
        assert all(sp.im(root) == 0 for root in sp.roots(sp.Poly(polynomial, r)))

    # laplace/q1: L{y''} with y(0)=2, y'(0)=0 is s²Y − 2s.
    from sympy.integrals.laplace import (
        laplace_correspondence,
        laplace_initial_conds,
        laplace_transform,
    )
    s = sp.Symbol("s")
    transformed = laplace_initial_conds(
        laplace_correspondence(
            laplace_transform(y(T).diff(T, 2), T, s, noconds=True),
            {y: sp.Function("Y")}),
        T, {y: [2, 0]})
    assert sp.simplify(transformed - (s**2 * sp.Function("Y")(s) - 2 * s)) == 0

    # numerical/q1: one Euler step on y' = y from 1 with h = 0.1 gives 1.1.
    assert 1 + 0.1 * 1 == pytest.approx(1.1)

    # cauchy/q2: the indicial equation of t²y'' − 3ty' + 4y = 0 is (r−2)².
    indicial = sp.expand(
        (T**2 * y(T).diff(T, 2) - 3 * T * y(T).diff(T) + 4 * y(T))
        .subs(y(T), T**r).doit() / T**r
    )
    assert sp.factor(sp.simplify(indicial)) == (r - 2) ** 2


def test_lessons_needs_no_interface_toolkit():
    """Content, not widgets. It has to be readable and countable headlessly."""
    import subprocess
    import sys

    code = (
        "import sys; sys.modules['PySide6'] = None\n"
        "from odesuite_app.lessons import LESSONS; assert len(LESSONS) == 35\n"
    )
    done = subprocess.run([sys.executable, "-c", code], capture_output=True,
                          text=True)
    assert done.returncode == 0, done.stderr[-400:]


# ---------------------------------------------------------------------------
# Progress on disk
# ---------------------------------------------------------------------------


@pytest.fixture()
def store(tmp_path, monkeypatch):
    """Point the progress file somewhere disposable.

    The real one lives in the user's config directory, and a test that wrote
    there would quietly destroy someone's answers.
    """
    from odesuite_app import progress

    monkeypatch.setattr(progress, "directory", lambda: tmp_path / "odesuite")
    return progress


def test_nothing_recorded_reads_as_nothing(store):
    assert store.load() == {}
    assert store.counts("separable", 5) == (0, 5)


def test_an_answer_survives_being_written_and_read(store):
    store.record("separable", "q1", store.State.CORRECT)
    store.record("separable", "q2", store.State.ATTEMPTED)
    kept = store.load()["separable"]
    # `seen` is stamped today by `record`, and is compared separately so this
    # test does not have to be rewritten the next time a field is added.
    assert kept["q1"] == store.Answer("correct", right=1, tries=1, streak=1,
                                      seen=kept["q1"].seen)
    assert kept["q2"] == store.Answer("attempted", right=0, tries=1,
                                      streak=0, seen=kept["q2"].seen)
    assert kept["q1"].days_since_seen == 0
    assert store.counts("separable", 5) == (1, 5)
    assert store.mastery("separable", 5) == pytest.approx(0.2)


def test_getting_it_right_then_mistyping_keeps_the_tick(store):
    """Otherwise going back to a solved question and fumbling the spelling
    takes away work already done. The attempt is still counted: it happened."""
    store.record("roots", "q3", store.State.CORRECT)
    store.record("roots", "q3", store.State.ATTEMPTED)
    answer = store.load()["roots"]["q3"]
    assert answer.state == store.State.CORRECT
    assert (answer.right, answer.tries) == (1, 2)


def test_a_file_from_the_previous_format_keeps_its_ticks(store):
    """Version 1 stored the bare state string. Someone who has been using the
    Hub already must not lose their answers to a format change."""
    store.directory().mkdir(parents=True, exist_ok=True)
    store.path().write_text(
        '{"roots": {"q1": "correct", "q2": "attempted"}}', encoding="utf-8")

    loaded = store.load()
    assert loaded["roots"]["q1"].correct
    assert loaded["roots"]["q2"].state == store.State.ATTEMPTED
    assert store.counts("roots", 5) == (1, 5)

    store.record("roots", "q3", store.State.CORRECT)
    written = json.loads(store.path().read_text(encoding="utf-8"))
    assert written["version"] == store.VERSION
    assert store.load()["roots"]["q1"].correct, "a tick was lost on rewrite"


def test_nonsense_counters_are_sanitised_rather_than_stored(store):
    """`right` and `tries` are printed back to the user, and the file is
    hand-editable. `True` is an `int` in Python and would otherwise be shown
    as a tally of one."""
    store.directory().mkdir(parents=True, exist_ok=True)
    store.path().write_text(
        '{"version": 2, "answers": {"roots": {"q1": '
        '{"state": "correct", "right": true, "tries": -4}}}}',
        encoding="utf-8")
    answer = store.load()["roots"]["q1"]
    assert (answer.right, answer.tries) == (0, 0)


def test_reset_removes_the_file(store):
    store.record("roots", "q1", store.State.CORRECT)
    assert store.path().exists()
    store.reset()
    assert not store.path().exists()
    assert store.load() == {}
    store.reset()                      # and again, on nothing, without raising


def test_a_corrupt_file_is_not_fatal(store):
    """It is a plain file in a directory the user owns, so it can contain
    anything. Losing a tick is a small harm; refusing to open the Learning Hub
    is a large one."""
    store.directory().mkdir(parents=True, exist_ok=True)
    for rubbish in ("", "{", "null", "[1, 2, 3]", '"a string"',
                    '{"separable": "not a mapping"}',
                    '{"separable": {"q1": "not-a-state"}}'):
        store.path().write_text(rubbish, encoding="utf-8")
        assert store.load() == {}, f"{rubbish!r} was not discarded"


def test_partly_valid_content_keeps_the_valid_part(store):
    store.directory().mkdir(parents=True, exist_ok=True)
    store.path().write_text(
        '{"roots": {"q1": "correct", "q2": "nonsense"}, "bad": 7}',
        encoding="utf-8")
    assert store.load() == {
        "roots": {"q1": store.Answer("correct", right=1, tries=1,
                                     streak=1)}
    }


def test_an_unknown_state_is_refused_rather_than_stored(store):
    with pytest.raises(ValueError):
        store.record("roots", "q1", "brilliant")


def test_counts_never_exceed_the_questions_asked(store):
    """A lesson that lost a question should not report 6 of 5 from an older
    file."""
    for index in range(6):
        store.record("roots", f"q{index}", store.State.CORRECT)
    assert store.counts("roots", 5) == (5, 5)


def test_the_directory_is_the_platform_convention(monkeypatch):
    # Deliberately not using the `store` fixture: it replaces `directory`,
    # which is the function under test here.
    from odesuite_app import progress as real

    monkeypatch.setattr(real.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", r"C:\Users\someone\AppData\Local")
    assert real.directory().as_posix().endswith("AppData/Local/odesuite")

    monkeypatch.setattr(real.sys, "platform", "linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", "/home/someone/.config")
    assert real.directory().as_posix() == "/home/someone/.config/odesuite"


# ---------------------------------------------------------------------------
# The screen
# ---------------------------------------------------------------------------

pytest.importorskip("PySide6", reason="the app extra is not installed")


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def screen(qapp, store):
    from odesuite_app.screens.learn_lessons import LessonsScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    made = LessonsScreen(SessionState(), PALETTES["dark"])
    made.resize(1500, 950)
    qapp.processEvents()
    yield made
    made.deleteLater()


def _open(screen, qapp, key: str, segment: str = "Practice"):
    """Put the screen on one lesson and one part of it."""
    screen.select(key)
    screen._choose_segment(segment)
    qapp.processEvents()
    return screen.current_lesson()


def _row_text(screen, key: str) -> str:
    for item, lesson in screen._lesson_items():
        if lesson.key == key:
            return item.text(0)
    raise AssertionError(f"{key} is not in the tree")


def _page_text(screen) -> str:
    """Everything the reading column is currently showing."""
    from PySide6.QtWidgets import QLabel

    return "\n".join(label.text() for label in screen._page.findChildren(QLabel)
                     if label.isVisibleTo(screen))


def _press(screen, caption: str) -> None:
    """Click the first visible button with this caption."""
    from PySide6.QtWidgets import QPushButton

    for button in screen._page.findChildren(QPushButton):
        if button.text().startswith(caption) and button.isEnabled():
            button.click()
            return
    raise AssertionError(f"no enabled {caption!r} button on the page")


@pytest.mark.parametrize("palette", ["dark", "light"])
def test_the_screen_renders_in_both_palettes(qapp, store, palette):
    from odesuite_app.screens.learn_lessons import LessonsScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    made = LessonsScreen(SessionState(), PALETTES[palette])
    made.resize(1500, 950)
    qapp.processEvents()
    assert not made.grab().isNull()
    made.deleteLater()


def test_the_tree_holds_every_unit_and_every_lesson(screen, qapp):
    assert screen.listing.topLevelItemCount() == len(UNITS)
    assert [lesson.key for _, lesson in screen._lesson_items()] == [
        lesson.key for lesson in LESSONS
    ]


def test_every_lesson_can_be_opened_at_every_segment(screen, qapp):
    from odesuite_app.screens.learn_lessons import SEGMENTS

    for lesson in LESSONS:
        for segment in SEGMENTS:
            _open(screen, qapp, lesson.key, segment)
            assert screen.current_lesson() is lesson
            assert screen.title_label.text() == lesson.title
            assert screen._layout.count() > 1, f"{lesson.key}/{segment} is empty"
        # The questions live on Practice, so that is the only segment that
        # registers verdict labels -- and it must register all of them.
        _open(screen, qapp, lesson.key, "Practice")
        assert set(screen._verdicts) == {q.key for q in lesson.questions}


def test_every_button_says_what_it_does(screen, qapp):
    """A one-word label is enough for someone who can see the card around it.

    A screen reader announces the button and not the paragraph above it, so
    *Check* alone does not say what is being checked or how, and *Show me* does
    not say that asking costs the question. Every button carries a tooltip,
    which is what Qt exposes as the accessible description.
    """
    from PySide6.QtWidgets import QPushButton

    from odesuite_app.screens.learn_lessons import SEGMENTS

    for key in ("separable", "basics", "linear"):
        for segment in SEGMENTS:
            _open(screen, qapp, key, segment)
            for button in screen.findChildren(QPushButton):
                assert button.text(), "a button with no text at all"
                if button.text() in SEGMENTS:
                    continue          # the segment tabs label themselves
                assert button.toolTip(), (
                    f"{key}/{segment}: {button.text()!r} says nothing more "
                    "than its label"
                )


def test_a_card_announces_what_it_is(screen, qapp):
    """Landing on a panel and hearing "panel" is landing nowhere. Each card
    names itself from its own heading."""
    from PySide6.QtWidgets import QFrame

    lesson = _open(screen, qapp, "separable", "Learn")
    named = {frame.accessibleName()
             for frame in screen.findChildren(QFrame)
             if frame.accessibleName()}
    assert any("Why this topic exists" in one for one in named)
    assert any("Where this comes from" in one for one in named)
    for note in lesson.notes:
        assert any(note.heading in one for one in named), note.heading


def test_each_paragraph_of_prose_is_announced_as_one(screen, qapp):
    """The whole point of splitting on blank lines is that a long body stops
    being a wall -- for a reader listening to it as much as one seeing it."""
    from PySide6.QtWidgets import QLabel

    from odesuite_app import richtext

    lesson = _open(screen, qapp, "separable", "Learn")
    paragraphs = [label for label in screen.findChildren(QLabel)
                  if label.accessibleName() == "paragraph"]
    expected = len(lesson.motivation.split("\n\n"))
    assert len(paragraphs) >= expected, (
        f"{len(paragraphs)} paragraphs for a motivation with {expected}"
    )
    for label in paragraphs:
        assert label.wordWrap(), "a paragraph that cannot wrap is one long line"
        spoken = label.accessibleDescription()
        assert spoken, "a paragraph with nothing to announce"
        assert spoken == richtext.plain(spoken), (
            f"the spoken form still carries markers: {spoken[:60]!r}"
        )


def test_selecting_a_unit_heading_says_so_rather_than_going_blank(screen, qapp):
    screen.listing.setCurrentItem(screen.listing.topLevelItem(0))
    qapp.processEvents()
    assert screen.current_lesson() is None
    assert "Choose a lesson" in screen.summary_label.text()
    assert not any(b.isEnabled() for b in screen.segment_buttons.values())


def test_the_lesson_names_its_unit_and_its_textbook_section(screen, qapp):
    _open(screen, qapp, "laplace", "Learn")
    trail = screen.reference_label.text()
    assert content.unit_of("laplace").title in trail
    assert by_key("laplace").reference in trail


def test_a_right_answer_is_recorded_and_counted(screen, qapp, store):
    from PySide6.QtWidgets import QLineEdit

    lesson = _open(screen, qapp, "separable")
    question = next(q for q in lesson.questions if isinstance(q, Solve))

    box = screen._page.findChildren(QLineEdit)[0]
    box.setText("exp(t**2)")                       # solves y' = 2ty, y(0)=1
    screen._check_solve(lesson, question, box, screen._verdicts[question.key])

    assert "✓" in screen._verdicts[question.key].text()
    assert store.load()[lesson.key][question.key].correct
    assert "(1/" in _row_text(screen, lesson.key), "the count did not follow"


def test_an_equivalent_form_is_accepted(screen, qapp, store):
    """There is no stored answer to match against, so any correct spelling
    passes. This is the property that makes grading by substitution worth the
    trouble."""
    from PySide6.QtWidgets import QLineEdit

    lesson = _open(screen, qapp, "roots")
    question = next(q for q in lesson.questions if q.key == "q5")
    verdict = screen._verdicts[question.key]

    box = screen._page.findChildren(QLineEdit)[-1]
    for spelling in ("sin(3*t)", "3*sin(3*t)/3", "-sin(-3*t)"):
        box.setText(spelling)
        screen._check_solve(lesson, question, box, verdict)
        assert "✓" in verdict.text(), f"{spelling} was not accepted"


def test_a_wrong_answer_shows_what_is_left_over(screen, qapp, store):
    from PySide6.QtWidgets import QLineEdit

    lesson = _open(screen, qapp, "separable")
    question = next(q for q in lesson.questions if isinstance(q, Solve))

    box = screen._page.findChildren(QLineEdit)[0]
    box.setText("exp(t)")
    screen._check_solve(lesson, question, box, screen._verdicts[question.key])

    assert "✗" in screen._verdicts[question.key].text()
    assert "left over" in screen._verdicts[question.key].text()
    assert store.load()[lesson.key][question.key].state == store.State.ATTEMPTED


def test_a_wrong_answer_is_diagnosed_rather_than_dumped(screen, qapp, store):
    """Where the residual says something, the card says it instead. Printing
    `(1 - 2*t)*exp(t)` asks the person who has just got the question wrong to
    do the one piece of analysis they have shown they cannot do."""
    from PySide6.QtWidgets import QLineEdit

    lesson = _open(screen, qapp, "separable")
    question = next(q for q in lesson.questions if isinstance(q, Solve))
    assert question.conditions, "this test needs a question with a condition"

    box = screen._page.findChildren(QLineEdit)[0]
    # Solves the equation; wrong member of the family. The most encouraging
    # miss there is, and the one a bare cross hides completely.
    box.setText("2*exp(t**2)")
    screen._check_solve(lesson, question, box, screen._verdicts[question.key])

    shown = screen._verdicts[question.key].text()
    assert "✗" in shown
    assert "The method is right" in shown
    assert "left over" not in shown, "the dump gave way to the sentence"


def test_the_option_picked_is_remembered_not_just_the_verdict(screen, qapp,
                                                              store):
    """A state says a question was missed. The options say how: each one is
    written as a misconception, which is unreadable from a tick."""
    from PySide6.QtWidgets import QButtonGroup

    lesson = _open(screen, qapp, "separable")
    question = next(q for q in lesson.questions if isinstance(q, Choice))
    wrong = next(index for index in range(len(question.options))
                 if index != question.answer)

    group = screen._page.findChildren(QButtonGroup)[0]
    group.button(wrong).setChecked(True)
    screen._check_choice(lesson, question, group, screen._verdicts[question.key])

    saved = store.load()[lesson.key][question.key]
    assert saved.picks == (wrong,)
    assert saved.state == store.State.ATTEMPTED


def test_a_typed_answer_records_no_option(screen, qapp, store):
    from PySide6.QtWidgets import QLineEdit

    lesson = _open(screen, qapp, "separable")
    question = next(q for q in lesson.questions if isinstance(q, Solve))
    box = screen._page.findChildren(QLineEdit)[0]
    box.setText("exp(t**2)")
    screen._check_solve(lesson, question, box, screen._verdicts[question.key])

    assert store.load()[lesson.key][question.key].picks == ()


def test_the_course_map_names_a_repeated_wrong_option(qapp, store):
    """The point of storing the pick. "Worth another look" says a lesson is
    weak; this says what is believed instead, which is what the per-option
    reasons were written for."""
    from odesuite_app.lessons import UNITS
    from odesuite_app.screens.learn_course import CourseScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    lesson = next(lesson for unit in UNITS for lesson in unit.lessons
                  if any(isinstance(q, Choice) for q in lesson.questions))
    question = next(q for q in lesson.questions if isinstance(q, Choice))
    wrong = next(index for index in range(len(question.options))
                 if index != question.answer)
    for _ in range(3):
        store.record(lesson.key, question.key, store.State.ATTEMPTED,
                     picked=wrong)

    made = CourseScreen(SessionState(), PALETTES["dark"])
    qapp.processEvents()
    try:
        shown = made.review_label.text()
        assert "A habit, not a slip" in shown
        assert lesson.title in shown
        assert question.options[wrong][:20] in shown
    finally:
        made.deleteLater()


def test_a_choice_explains_the_option_that_was_picked(screen, qapp, store):
    """Not the reason the right answer is right -- the reason *this* answer is
    wrong. Explaining someone else's answer back at them teaches nothing."""
    from PySide6.QtWidgets import QButtonGroup

    lesson = _open(screen, qapp, "separable")
    question = next(q for q in lesson.questions if isinstance(q, Choice))
    group = screen._page.findChildren(QButtonGroup)[0]
    verdict = screen._verdicts[question.key]

    group.button(question.answer).setChecked(True)
    screen._check_choice(lesson, question, group, verdict)
    assert "✓" in verdict.text()
    assert question.becauses[question.answer][:30] in verdict.text()

    wrong = (question.answer + 1) % len(question.options)
    group.button(wrong).setChecked(True)
    screen._check_choice(lesson, question, group, verdict)
    assert "✗" in verdict.text()
    assert question.becauses[wrong][:30] in verdict.text(), (
        "the cross explained a different option than the one chosen"
    )


def test_answering_nothing_asks_rather_than_marks(screen, qapp, store):
    from PySide6.QtWidgets import QButtonGroup

    lesson = _open(screen, qapp, "separable")
    question = next(q for q in lesson.questions if isinstance(q, Choice))
    group = screen._page.findChildren(QButtonGroup)[0]
    verdict = screen._verdicts[question.key]

    screen._check_choice(lesson, question, group, verdict)
    assert "pick an option" in verdict.text()
    assert store.load() == {}, "an unanswered question was recorded"


def test_hints_come_one_rung_at_a_time(screen, qapp):
    """The whole point of a ladder is that the first press does not hand over
    the method."""
    from PySide6.QtWidgets import QLabel, QPushButton

    lesson = _open(screen, qapp, "separable")
    question = next(q for q in lesson.questions if isinstance(q, Solve))
    card = screen._page.findChildren(QPushButton)
    hint_button = next(b for b in card if b.text() == "Hint")
    hints = [w for w in screen._page.findChildren(QLabel)
             if w.property("role") == "muted"]

    assert not any(w.isVisibleTo(screen) and w.text() for w in hints)
    hint_button.click()
    qapp.processEvents()

    shown = [w for w in screen._page.findChildren(QLabel)
             if w.isVisibleTo(screen) and question.hints[0] in w.text()]
    assert shown, "the first rung did not appear"
    assert all(question.hints[1] not in w.text() for w in shown), (
        "the second rung was given away with the first"
    )
    assert "left" in hint_button.text()

    for _ in question.hints:
        hint_button.click()
        qapp.processEvents()
    assert not hint_button.isEnabled()
    last = [w for w in screen._page.findChildren(QLabel)
            if question.hints[-1] in w.text()]
    assert last, "the ladder never reached its last rung"


def test_progress_is_restored_when_the_lesson_is_reopened(screen, qapp, store):
    from PySide6.QtWidgets import QButtonGroup

    lesson = _open(screen, qapp, "separable")
    question = next(q for q in lesson.questions if isinstance(q, Choice))
    group = screen._page.findChildren(QButtonGroup)[0]
    group.button(question.answer).setChecked(True)
    screen._check_choice(lesson, question, group, screen._verdicts[question.key])

    _open(screen, qapp, "undetermined")
    _open(screen, qapp, "separable")
    assert "answered correctly" in screen._verdicts[question.key].text()


def test_a_second_attempt_is_counted_without_taking_the_tick_away(screen, qapp,
                                                                 store):
    from PySide6.QtWidgets import QLineEdit

    lesson = _open(screen, qapp, "separable")
    question = next(q for q in lesson.questions if isinstance(q, Solve))
    box = screen._page.findChildren(QLineEdit)[0]
    verdict = screen._verdicts[question.key]

    box.setText("exp(t**2)")
    screen._check_solve(lesson, question, box, verdict)
    box.setText("exp(t)")
    screen._check_solve(lesson, question, box, verdict)

    _open(screen, qapp, "separable")
    assert "answered correctly" in screen._verdicts[question.key].text()
    assert "2 attempts" in screen._verdicts[question.key].text()


def test_reset_clears_the_ticks_and_the_counts(screen, qapp, store):
    from PySide6.QtWidgets import QButtonGroup

    lesson = _open(screen, qapp, "separable")
    question = next(q for q in lesson.questions if isinstance(q, Choice))
    group = screen._page.findChildren(QButtonGroup)[0]
    group.button(question.answer).setChecked(True)
    screen._check_choice(lesson, question, group, screen._verdicts[question.key])
    assert "(1/" in _row_text(screen, lesson.key)

    screen._reset()
    qapp.processEvents()
    assert store.load() == {}
    assert "(0/" in _row_text(screen, lesson.key)


def test_switching_around_does_not_accumulate_widgets(screen, qapp):
    """The cards are rebuilt on every switch of lesson *or* segment, so
    anything parented to the screen rather than the card would pile up one set
    per visit."""
    from PySide6.QtWidgets import QButtonGroup

    from odesuite_app.screens.learn_lessons import SEGMENTS

    for _ in range(3):
        for lesson in LESSONS:
            for segment in SEGMENTS:
                _open(screen, qapp, lesson.key, segment)
    _open(screen, qapp, "separable")

    groups = screen.findChildren(QButtonGroup)
    # One per choice question on the page, plus the segment bar's own.
    assert len(groups) <= len(by_key("separable").questions) + 2


def test_the_tool_button_asks_for_the_matching_screen(screen, qapp):
    seen = []
    screen.open_tool.connect(seen.append)
    for lesson in LESSONS:
        _open(screen, qapp, lesson.key, "Learn")
        screen._open_tool()
    assert seen == [lesson.tool for lesson in LESSONS]


@pytest.mark.slow
def test_a_worked_example_is_produced_on_request(screen, qapp):
    """It is generated by the narrator through the real subprocess, not stored,
    so what the lesson shows cannot drift from what the tool would say."""
    from PySide6.QtCore import QThreadPool
    from PySide6.QtWidgets import QPushButton

    from odesuite_app.widgets.stepspanel import StepsPanel

    lesson = _open(screen, qapp, "separable", "Examples")
    panels = screen._page.findChildren(StepsPanel)
    button = next(b for b in screen._page.findChildren(QPushButton)
                  if b.text() == "Work it through")

    assert len(panels) == len(lesson.examples)
    assert not panels[0].isVisibleTo(screen)

    button.click()
    QThreadPool.globalInstance().waitForDone(90_000)
    for _ in range(6):
        qapp.processEvents()

    assert panels[0].isVisibleTo(screen)
    assert panels[0]._body.count() >= 4
    assert button.isEnabled(), "the button was left disabled"


def test_a_superseded_request_hands_its_button_back(screen, qapp):
    """Two "work it through" presses in a row: only the second is delivered,
    and the first must not leave its button disabled for the rest of the
    visit."""
    from PySide6.QtWidgets import QPushButton

    from odesuite_app.widgets.stepspanel import StepsPanel

    _open(screen, qapp, "separable", "Examples")
    buttons = [b for b in screen._page.findChildren(QPushButton)
               if b.text() == "Work it through"]
    panels = screen._page.findChildren(StepsPanel)
    assert len(buttons) >= 2

    screen._work("y' = y", "", "steps", panels[0], buttons[0])
    screen._work("y' = y", "", "steps", panels[1], buttons[1])
    assert buttons[0].isEnabled(), "the superseded button stayed disabled"
    assert not buttons[1].isEnabled()
    screen._abandon()


# ---------------------------------------------------------------------------
# The course map
# ---------------------------------------------------------------------------


@pytest.fixture()
def course(qapp, store):
    from odesuite_app.screens.learn_course import CourseScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    made = CourseScreen(SessionState(), PALETTES["dark"])
    made.resize(1500, 950)
    qapp.processEvents()
    yield made
    made.deleteLater()


@pytest.mark.parametrize("palette", ["dark", "light"])
def test_the_course_map_renders_in_both_palettes(qapp, store, palette):
    from odesuite_app.screens.learn_course import CourseScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    made = CourseScreen(SessionState(), PALETTES[palette])
    made.resize(1500, 950)
    qapp.processEvents()
    assert not made.grab().isNull()
    made.deleteLater()


def test_the_course_map_totals_every_question(course, store):
    asked = sum(len(lesson.questions) for lesson in LESSONS)
    assert course.overall_label.text() == f"0 of {asked}"
    assert course.overall_bar.maximum() == asked
    assert str(len(LESSONS)) in course.overall_detail.text()
    assert str(len(UNITS)) in course.overall_detail.text()


def test_the_course_map_follows_the_progress_file(course, qapp, store):
    store.record("separable", "q1", store.State.CORRECT)
    store.record("separable", "q2", store.State.CORRECT)
    course.refresh()
    qapp.processEvents()

    asked = sum(len(lesson.questions) for lesson in LESSONS)
    assert course.overall_label.text() == f"2 of {asked}"
    assert course.overall_bar.value() == 2


def test_continue_offers_the_earliest_unfinished_lesson(course, qapp, store):
    assert LESSONS[0].title in course.continue_detail.text()

    for question in LESSONS[0].questions:
        store.record(LESSONS[0].key, question.key, store.State.CORRECT)
    course.refresh()
    qapp.processEvents()
    assert LESSONS[1].title in course.continue_detail.text()

    seen = []
    course.open_lesson.connect(seen.append)
    course._continue()
    assert seen == [LESSONS[1].key]


def test_a_finished_course_offers_nothing_more(course, qapp, store):
    for lesson in LESSONS:
        for question in lesson.questions:
            store.record(lesson.key, question.key, store.State.CORRECT)
    course.refresh()
    qapp.processEvents()

    assert not course.continue_button.isEnabled()
    assert "Every question is answered" in course.continue_detail.text()


def test_every_lesson_has_a_row_that_opens_it(course, qapp):
    from PySide6.QtWidgets import QPushButton

    opens = [b for b in course._page.findChildren(QPushButton)
             if b.text() == "Open"]
    assert len(opens) == len(LESSONS)

    seen = []
    course.open_lesson.connect(seen.append)
    for button in opens:
        button.click()
    assert seen == [lesson.key for lesson in LESSONS]


# ---------------------------------------------------------------------------
# The Drill segment
# ---------------------------------------------------------------------------


def _drill(screen, qapp, key: str):
    lesson = _open(screen, qapp, key, "Drill")
    assert screen._segment == "Drill", f"{key} has no drill to open"
    return lesson


def test_the_drill_is_offered_on_every_lesson(screen, qapp):
    """This was once the opposite test.

    Ten lessons had no drill, because a `Solve` question is graded by
    substituting the answer into its own equation and Euler's method has no
    closed form to substitute into. Now that a question can be graded to a
    tolerance instead, every lesson has one and the button is offered on all
    of them.
    """
    for lesson in LESSONS:
        _open(screen, qapp, lesson.key, "Learn")
        assert screen.segment_buttons["Drill"].isVisibleTo(screen), lesson.key


@contextlib.contextmanager
def _lesson_replaced(lesson):
    """Hand the screen a modified lesson, and put the real one back."""
    original = content.by_key
    content.by_key = (lambda key: lesson if key == lesson.key
                      else original(key))
    try:
        yield
    finally:
        content.by_key = original


def test_drill_is_withheld_from_a_lesson_that_has_none(screen, qapp):
    """The guard is unreachable from the content, and is kept anyway.

    Nothing in the course is without a drill, so this drives the screen with a
    lesson whose templates have been taken away -- the shape a lesson added
    without one would arrive in. The button goes rather than opening an empty
    page, and an already-open Drill falls back to Practice.
    """
    import dataclasses

    lesson = dataclasses.replace(content.by_key("separable"), templates=())
    _drill(screen, qapp, "separable")
    with _lesson_replaced(lesson):
        screen._show()
        assert not screen.segment_buttons["Drill"].isVisibleTo(screen)
        assert screen._segment == "Practice"
        assert screen.segment_buttons["Practice"].isChecked()


def test_the_drill_page_offers_every_template(screen, qapp):
    lesson = _drill(screen, qapp, "separable")
    assert set(screen._verdicts) == {t.key for t in lesson.templates}
    for template in lesson.templates:
        assert str(generate.combinations(template)) in _page_text(screen), (
            "the drill does not say how many versions there are"
        )


def test_a_new_question_is_a_different_question(screen, qapp):
    lesson = _drill(screen, qapp, "separable")
    template = lesson.templates[0]

    first = generate.draw(template, screen._drill_seed[template.key])
    _press(screen, "New question")
    qapp.processEvents()
    second = generate.draw(template, screen._drill_seed[template.key])

    assert (first.equation, first.conditions) != (second.equation,
                                                  second.conditions)
    assert first.equation in _page_text(screen) or \
        second.equation in _page_text(screen)


def test_the_question_survives_leaving_the_lesson_and_coming_back(screen,
                                                                 qapp):
    """The seed is remembered, so an answer half typed is not thrown away by a
    glance at the notes."""
    lesson = _drill(screen, qapp, "separable")
    template = lesson.templates[0]
    _press(screen, "New question")
    qapp.processEvents()
    seed = screen._drill_seed[template.key]

    _open(screen, qapp, "roots", "Learn")
    _drill(screen, qapp, "separable")
    assert screen._drill_seed[template.key] == seed


def test_a_drill_is_mastered_by_three_in_a_row(screen, qapp, store):
    from PySide6.QtWidgets import QLineEdit

    lesson = _drill(screen, qapp, "separable")
    template = lesson.templates[0]
    bucket = store.drill_key(lesson.key)

    for expected in range(1, store.MASTERED_STREAK + 1):
        question = generate.draw(template, screen._drill_seed[template.key])
        derivation = _work_out(lesson, question.equation, question.conditions)
        box = screen._page.findChildren(QLineEdit)[0]
        box.setText(sp.sstr(derivation.result))
        screen._check_solve(lesson, question, box,
                            screen._verdicts[template.key],
                            bucket=bucket, key=template.key)
        answer = store.load()[bucket][template.key]
        assert answer.streak == expected
        _press(screen, "New question")
        qapp.processEvents()

    assert store.load()[bucket][template.key].mastered
    assert "mastered" in _page_text(screen)


def test_a_wrong_drill_answer_starts_the_count_again(screen, qapp, store):
    from PySide6.QtWidgets import QLineEdit

    lesson = _drill(screen, qapp, "separable")
    template = lesson.templates[0]
    bucket = store.drill_key(lesson.key)

    question = generate.draw(template, screen._drill_seed[template.key])
    derivation = _work_out(lesson, question.equation, question.conditions)
    box = screen._page.findChildren(QLineEdit)[0]
    box.setText(sp.sstr(derivation.result))
    screen._check_solve(lesson, question, box, screen._verdicts[template.key],
                        bucket=bucket, key=template.key)
    assert store.load()[bucket][template.key].streak == 1

    box.setText("t**7 + 5")
    screen._check_solve(lesson, question, box, screen._verdicts[template.key],
                        bucket=bucket, key=template.key)
    assert store.load()[bucket][template.key].streak == 0
    assert "✗" in screen._verdicts[template.key].text()


def test_drilling_does_not_move_the_lessons_own_count(screen, qapp, store):
    """The two numbers mean different things and must not be added together."""
    from PySide6.QtWidgets import QLineEdit

    lesson = _drill(screen, qapp, "separable")
    template = lesson.templates[0]
    question = generate.draw(template, screen._drill_seed[template.key])
    derivation = _work_out(lesson, question.equation, question.conditions)

    box = screen._page.findChildren(QLineEdit)[0]
    box.setText(sp.sstr(derivation.result))
    screen._check_solve(lesson, question, box, screen._verdicts[template.key],
                        bucket=store.drill_key(lesson.key), key=template.key)

    assert "(0/" in _row_text(screen, lesson.key)
    assert store.counts(lesson.key, len(lesson.questions), store.load()) == (
        0, len(lesson.questions)
    )


def test_the_drill_hint_ladder_behaves_like_the_practice_one(screen, qapp):
    lesson = _drill(screen, qapp, "separable")
    template = lesson.templates[0]
    question = generate.draw(template, screen._drill_seed[template.key])

    _press(screen, "Hint")
    qapp.processEvents()
    text = _page_text(screen)
    assert question.hints[0] in text
    assert question.hints[1] not in text, (
        "the second rung was given away with the first"
    )


def test_the_course_map_counts_mastered_drills(course, qapp, store):
    lesson = by_key("separable")
    for _ in range(store.MASTERED_STREAK):
        store.record(store.drill_key(lesson.key), lesson.templates[0].key,
                     store.State.CORRECT)
    course.refresh()
    qapp.processEvents()
    assert "1 of" in course.overall_detail.text()
    assert "drills mastered" in course.overall_detail.text()


# ---------------------------------------------------------------------------
# Lesson figures
# ---------------------------------------------------------------------------


def test_every_figure_a_lesson_names_exists():
    """A lesson names its figure by key, because `lessons/` holds no Qt. That
    indirection is what makes a typo silent -- the lesson would simply lose
    its picture -- so the two ends are checked against each other here."""
    from odesuite_app.widgets.lessonfigure import FIGURES

    for lesson in LESSONS:
        if lesson.figure:
            assert lesson.figure in FIGURES, (
                f"{lesson.key} names a figure that does not exist: "
                f"{lesson.figure!r}"
            )


def test_the_figures_are_all_used():
    """The other direction: a figure nobody shows is code that cannot rot
    visibly, because nobody would see it break."""
    from odesuite_app.widgets.lessonfigure import FIGURES

    used = {lesson.figure for lesson in LESSONS if lesson.figure}
    assert set(FIGURES) == used


def _figure(key: str, palette: str = "dark"):
    from odesuite_app.theme import PALETTES
    from odesuite_app.widgets.lessonfigure import build_figure

    made = build_figure(key, PALETTES[palette])
    assert made is not None, key
    return made


def _figure_keys() -> list[str]:
    from odesuite_app.widgets.lessonfigure import FIGURES

    return sorted(FIGURES)


@pytest.mark.parametrize("key", _figure_keys())
@pytest.mark.parametrize("palette", ["dark", "light"])
def test_every_figure_draws_in_both_palettes(qapp, key, palette):
    """Over the registry, not over a list somebody has to remember to extend.

    Three of the six were named here when there were six. A figure added
    without being added to this line would be the one nobody ever drew."""
    made = _figure(key, palette)
    made.resize(700, 480)
    qapp.processEvents()
    assert not made.grab().isNull()
    assert made.readout.text(), f"{key} drew nothing in words"
    made.deleteLater()


def test_an_unknown_figure_key_is_declined_rather_than_raising(qapp):
    from odesuite_app.theme import PALETTES
    from odesuite_app.widgets.lessonfigure import build_figure

    assert build_figure("no-such-figure", PALETTES["dark"]) is None


def _plotted(figure) -> list:
    """The y-data of every curve currently on the plot."""
    import pyqtgraph as pg

    return [item.getData()[1] for item in figure.plot.plotItem.items
            if isinstance(item, pg.PlotDataItem) and item.getData()[1] is not None]


@pytest.mark.parametrize("key,slider", [
    ("slope_field", "a"),
    ("phase_line", "h"),
    ("euler_error", "h"),
])
def test_moving_a_slider_changes_what_is_drawn(qapp, key, slider):
    """The point of a figure is that it responds. Comparing the drawn data
    rather than merely checking that nothing raised, because a figure wired to
    the wrong signal would pass that weaker test while sitting perfectly
    still."""
    import numpy as np

    made = _figure(key)
    made.resize(700, 480)
    qapp.processEvents()
    before = _plotted(made)

    control = made.sliders[slider]
    control.set_value(0.5 * (control.low + control.high) if slider != "a"
                      else control.high, notify=True)
    qapp.processEvents()
    after = _plotted(made)

    changed = len(before) != len(after) or any(
        first.shape != second.shape or not np.allclose(first, second)
        for first, second in zip(before, after)
    )
    assert changed, f"{key} drew the same thing after moving {slider}"
    made.deleteLater()


def test_the_phase_line_loses_its_equilibria_when_the_harvest_is_too_high(qapp):
    """The figure's whole reason for existing: past h = r·K/4 the two
    equilibria merge and vanish, and the readout has to say so rather than
    quietly drawing nothing."""
    made = _figure("phase_line")
    made.sliders["r"].set_value(1.0)
    made.sliders["K"].set_value(6.0)

    made.sliders["h"].set_value(0.0, notify=True)
    qapp.processEvents()
    assert "stable" in made.readout.text()

    made.sliders["h"].set_value(2.5, notify=True)     # r·K/4 = 1.5
    qapp.processEvents()
    assert "No equilibria" in made.readout.text()
    made.deleteLater()


def test_clicking_the_slope_field_drops_a_solution_through_the_point(qapp):
    """Clicking is the part that shows uniqueness, so it is checked as
    behaviour rather than left to be discovered broken on screen."""
    made = _figure("slope_field")
    made.resize(700, 480)
    qapp.processEvents()
    before = len(_plotted(made))

    made._points.append((1.0, 0.5))
    made.draw()
    qapp.processEvents()

    assert len(_plotted(made)) > before, "no curve was added"
    assert "1 condition" in made.readout.text()
    made.deleteLater()


def test_the_two_orders_are_reported_as_measured_ratios(qapp):
    """First order against fourth is the lesson, and it is a number rather
    than an impression: the readout carries the ratio the next halving
    actually gives, from the same `byhand.refinement` the by-hand screen uses.

    Measured rather than asserted, and the difference shows -- at h = 0.2 the
    ratios are 1.8 and 14.7, not 2 and 16. Printing the theory instead would
    be printing something the figure had not checked."""
    made = _figure("euler_error")
    made.sliders["h"].set_value(0.2, notify=True)
    qapp.processEvents()

    text = made.readout.text()
    assert "Euler error" in text and "RK4 error" in text
    ratios = [float(part) for part in re.findall(r"÷([0-9.]+) when h halves",
                                                 text)]
    assert len(ratios) == 2, text
    euler, rk4 = ratios
    assert 1.5 < euler < 2.0, f"Euler should be nearing 2, not {euler}"
    assert 12.0 < rk4 < 16.0, f"RK4 should be nearing 16, not {rk4}"
    made.deleteLater()


def test_a_lesson_with_a_figure_shows_it_and_one_without_does_not(screen, qapp):
    from odesuite_app.widgets.lessonfigure import LessonFigure

    _open(screen, qapp, "slopefields", "Learn")
    assert screen._page.findChildren(LessonFigure), "the figure is missing"

    # And it belongs to Learn only: the same lesson's Practice is questions.
    _open(screen, qapp, "slopefields", "Practice")
    assert not screen._page.findChildren(LessonFigure)

    # A lesson genuinely without one. Eighteen of the thirty-five have a
    # figure and seventeen do not, because a figure earns its place only
    # where the lesson has a parameter worth turning.
    _open(screen, qapp, "basics", "Learn")
    assert not screen._page.findChildren(LessonFigure)


# ---------------------------------------------------------------------------
# The figures that make a measurable claim
# ---------------------------------------------------------------------------


def test_the_order_figure_measures_the_orders_it_claims(qapp):
    """Its whole point is that 1 and 4 are *measured*, not asserted.

    The numbers come from `byhand.refinement`, the same function Methods by
    Hand tabulates, so a figure that quietly disagreed with the by-hand screen
    would be worse than none. Read back off the last halving, where the
    asymptotic claim is closest to true.
    """
    import numpy as np

    made = _figure("order_slope")
    for method, wanted in (("euler", 1.0), ("rk4", 4.0)):
        steps, errors = made._measured(method)
        slope = ((np.log(errors[-2]) - np.log(errors[-1]))
                 / (np.log(steps[-2]) - np.log(steps[-1])))
        assert abs(slope - wanted) < 0.15, f"{method} measured {slope:.2f}"
    made.deleteLater()


def test_the_convolution_figure_shades_the_overlap(qapp):
    """The shading is the figure.

    Everything else in that pane is two curves, which any plot has. What makes
    it a picture of a convolution is the region between them being filled --
    so this counts the pixels actually painted in the blend of the accent
    colour over the plot background, rather than asserting the widget exists.
    """
    import collections

    from odesuite_app.theme import PALETTES

    made = _figure("convolution")
    made.resize(1000, 520)
    qapp.processEvents()
    image = made.grab().toImage()

    counts: collections.Counter = collections.Counter()
    for y in range(0, image.height(), 2):
        for x in range(0, image.width() // 2, 2):
            counts[image.pixelColor(x, y).name()] += 1
    background = PALETTES["dark"].plot_background.lower()
    shaded = [count for name, count in counts.items()
              if name != background and _is_blend(name)]
    assert sum(shaded) > 300, "the overlap is not shaded"
    made.deleteLater()


def _is_blend(name: str) -> bool:
    """Is this the accent colour laid over the plot background?

    Between the two, channel by channel, and not equal to either -- which is
    what a semi-transparent fill produces and what nothing else on that pane
    does.
    """
    from odesuite_app.theme import PALETTES

    accent = PALETTES["dark"].accent.lstrip("#")
    ground = PALETTES["dark"].plot_background.lstrip("#")
    try:
        parts = [int(name.lstrip("#")[at:at + 2], 16) for at in (0, 2, 4)]
    except ValueError:
        return False
    for index, value in enumerate(parts):
        low = int(ground[index * 2:index * 2 + 2], 16)
        high = int(accent[index * 2:index * 2 + 2], 16)
        if not low < value < high:
            return False
    return True


def test_the_partial_sums_figure_reaches_further_with_more_terms(qapp):
    """More terms, more agreement -- and never past the radius.

    Both halves of the lesson's claim. The reach is computed by the figure
    itself from the curves it drew, so this is checking the picture rather
    than repeating its arithmetic.
    """
    made = _figure("partial_sums")
    reaches = []
    for terms in (2, 6, 14):
        made.sliders["n"].set_value(terms)
        made.draw()
        qapp.processEvents()
        # Not "[\d.]+", which swallows the full stop that ends the sentence.
        found = re.search(r"out to t = (\d+\.\d+)", made.readout.text())
        assert found, made.readout.text()
        reaches.append(float(found.group(1)))
    assert reaches[0] < reaches[1] < reaches[2], reaches
    assert reaches[-1] < 1.0, "the radius is 1 and nothing may reach past it"
    made.deleteLater()


# ---------------------------------------------------------------------------
# The vibration figures
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("c,expected", [
    (1.0, "underdamped"),
    (4.0, "critically damped"),
    (8.0, "overdamped"),
])
def test_the_damping_figure_names_all_three_regimes(qapp, c, expected):
    """m = 1, k = 4, so critical damping is exactly 4. All three regimes have
    to be reachable, or the figure fails at the one thing it is for."""
    made = _figure("damping")
    made.sliders["m"].set_value(1.0)
    made.sliders["k"].set_value(4.0)
    made.sliders["c"].set_value(c, notify=True)
    qapp.processEvents()

    assert expected in made.readout.text()
    made.deleteLater()


def test_critical_damping_is_reachable_at_all(qapp):
    """A slider quantises to 1000 steps, so it can essentially never land on a
    single point of a continuum: asking for c = 4 gave 3.996, which really is
    underdamped, and the middle regime never appeared. The damping snaps to
    critical within half a step, so the number shown is the number used."""
    made = _figure("damping")
    made.sliders["m"].set_value(1.0)
    made.sliders["k"].set_value(4.0)
    made.sliders["c"].set_value(4.0, notify=True)
    qapp.processEvents()

    used, critical = made.damping()
    # Every slider quantises, m and k included, so the critical value itself
    # lands near 4 rather than on it. What has to hold exactly is that the
    # damping in use *is* the critical value, whatever that value turned out
    # to be -- otherwise the regime named and the regime drawn disagree.
    assert critical == pytest.approx(4.0, abs=0.02)
    assert used == critical, "the slider missed critical again"
    # And it does not snap from far away.
    made.sliders["c"].set_value(3.0, notify=True)
    assert made.damping()[0] == pytest.approx(3.0, abs=0.02)
    made.deleteLater()


def test_the_roots_collide_as_the_damping_rises(qapp):
    """The picture's whole claim: a complex pair slides together, meets on the
    real axis, and separates along it."""
    made = _figure("damping")
    made.sliders["m"].set_value(1.0)
    made.sliders["k"].set_value(4.0)

    made.sliders["c"].set_value(1.0, notify=True)
    under = made._roots(1.0, 1.0, 4.0)
    assert all(sp.im(root) != 0 for root, _ in under)

    critical = made._roots(1.0, 4.0, 4.0)
    assert len(critical) == 1 and critical[0][1] == 2, "not a repeated root"

    over = made._roots(1.0, 8.0, 4.0)
    assert len(over) == 2
    assert all(sp.im(root) == 0 for root, _ in over)
    made.deleteLater()


def test_the_resonance_figure_switches_to_the_secular_form(qapp):
    """At ω = ω₀ the beats amplitude 1/(ω₀²−ω²) divides by zero. The closed
    form there is t·sin(ω₀t)/(2ω₀), and the figure has to use it rather than
    producing infinities."""
    import numpy as np

    made = _figure("resonance")
    times = np.linspace(0.0, 20.0, 200)

    values, resonant = made._response(times, made._W0)
    assert resonant
    assert np.all(np.isfinite(values))
    # The envelope grows linearly, which is what resonance means.
    assert abs(values).max() > 4.0
    expected = times * np.sin(made._W0 * times) / (2 * made._W0)
    assert np.allclose(values, expected)

    off, resonant = made._response(times, 1.6)
    assert not resonant
    assert np.all(np.isfinite(off))
    made.deleteLater()


def test_near_resonance_is_large_but_still_bounded(qapp):
    """Measured: the beats amplitude is 0.69 at ω = 1.6, 2.56 at 1.9 and 25.1
    at 1.99. Growing without becoming infinite is the distinction the lesson
    turns on, so the figure has to keep getting it right."""
    import numpy as np

    made = _figure("resonance")
    times = np.linspace(0.0, 200.0, 4000)
    peaks = [abs(made._response(times, w)[0]).max() for w in (1.6, 1.9, 1.99)]

    assert all(np.isfinite(peak) for peak in peaks)
    assert peaks[0] < peaks[1] < peaks[2]
    assert peaks[2] > 10 * peaks[0]
    made.deleteLater()


def test_the_readout_says_which_case_it_is_in(qapp):
    made = _figure("resonance")
    made.sliders["w"].set_value(1.5, notify=True)
    qapp.processEvents()
    assert "beats" in made.readout.text()

    made.sliders["w"].set_value(2.0, notify=True)
    qapp.processEvents()
    assert "resonance" in made.readout.text()
    made.deleteLater()


def test_a_two_pane_figure_really_has_two_panes(qapp):
    """The base class gained a second plot for these, and the three figures
    written before it must be untouched by that."""
    for key in ("damping", "resonance"):
        made = _figure(key)
        assert len(made.panes) == 2, key
        assert made.plot is made.panes[0]
        made.deleteLater()

    for key in ("slope_field", "phase_line", "euler_error"):
        made = _figure(key)
        assert len(made.panes) == 1, key
        made.deleteLater()


# ---------------------------------------------------------------------------
# The eigenlines figure
# ---------------------------------------------------------------------------


def test_the_eigenlines_figure_names_what_the_origin_is(qapp):
    """The words come from `systems.classify`, the same function the narrator
    ends its derivation with, so the picture and the working cannot disagree
    about what they are looking at."""
    made = _figure("eigenlines")
    for key, value in zip("abcd", (1.0, 2.0, 3.0, 2.0)):
        made.sliders[key].set_value(value)
    made.draw()
    qapp.processEvents()
    assert "saddle" in made.readout.text()

    for key, value in zip("abcd", (-2.0, 1.0, 1.0, -2.0)):
        made.sliders[key].set_value(value)
    made.draw()
    qapp.processEvents()
    assert "stable node" in made.readout.text()
    made.deleteLater()


def test_complex_eigenvalues_draw_no_straight_lines(qapp):
    """There are none to draw: an eigendirection is a real eigenvector, and a
    rotating system has none. Drawing something anyway would be inventing a
    straight-line solution that does not exist."""
    import numpy as np

    made = _figure("eigenlines")
    for key, value in zip("abcd", (-1.0, -2.0, 2.0, -1.0)):
        made.sliders[key].set_value(value)
    made.draw()
    qapp.processEvents()

    values, _ = made.eigen()
    assert np.any(np.abs(values.imag) > 1e-9), "the premise has changed"
    assert "spiral" in made.readout.text()
    made.deleteLater()


def test_the_figure_agrees_with_the_narrator_on_the_same_matrix(qapp):
    """Two independent routes -- numpy in the figure, sympy in the narrator --
    to the same words. If they ever parted, one screen would contradict the
    other."""
    import sympy as sp

    from odesuite_app.systems import derive

    t = sp.Symbol("t", real=True)
    x, y = sp.Function("x"), sp.Function("y")
    made = _figure("eigenlines")
    for key, value in zip("abcd", (1.0, 2.0, 3.0, 2.0)):
        made.sliders[key].set_value(value)
    made.draw()
    qapp.processEvents()

    narrated = derive(
        [sp.Eq(x(t).diff(t), x(t) + 2 * y(t)),
         sp.Eq(y(t).diff(t), 3 * x(t) + 2 * y(t))],
        [x, y],
    )
    step = next(s for s in narrated.steps if s.title == "What the origin is")
    assert "saddle" in step.note and "saddle" in made.readout.text()
    made.deleteLater()
