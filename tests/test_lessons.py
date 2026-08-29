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

import json

import pytest

pytest.importorskip("sympy")

import sympy as sp  # noqa: E402

from odesuite_app import lessons as content  # noqa: E402
from odesuite_app.lessons import (  # noqa: E402
    LESSONS,
    UNITS,
    Choice,
    Solve,
    by_key,
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
    from odesuite_app.symbolic import EquationSpec, parse_equation

    return parse_equation(
        EquationSpec(equations=[equation], initial_conditions=conditions),
        extra_functions=EXTRA_FUNCTIONS,
    )


def _work_out(lesson, equation: str, conditions: str):
    """The derivation the screen would show, produced the same way it does."""
    from odesuite_app import laplace, steps

    parsed = _parse(equation, conditions)
    if lesson.narrator == "laplace":
        return laplace.derive(parsed.equation, parsed.function, ics=parsed.ics)
    return steps.derive(
        parsed.equation, parsed.function,
        hints=sp.classify_ode(parsed.equation, parsed.function(T)),
        ics=parsed.ics,
    )


# ---------------------------------------------------------------------------
# The shape of the course
# ---------------------------------------------------------------------------


def test_the_lessons_cover_the_techniques_the_app_can_teach():
    """A lesson on something no tool here explains would be notes with nothing
    behind them."""
    keys = {lesson.key for lesson in LESSONS}
    assert keys == {"separable", "linear", "roots", "undetermined", "cauchy",
                    "laplace", "numerical"}


def test_every_lesson_is_complete():
    for lesson in LESSONS:
        assert lesson.title and lesson.summary
        assert len(lesson.notes) >= 3, f"{lesson.key} is thin on notes"
        assert len(lesson.questions) >= 4, f"{lesson.key} is thin on practice"
        assert lesson.tool in {"steps", "laplace", "byhand", "worked"}
        assert lesson.narrator in {"steps", "laplace"}


def test_keys_are_unique():
    assert len({lesson.key for lesson in LESSONS}) == len(LESSONS)
    for lesson in LESSONS:
        keys = [q.key for q in lesson.questions]
        assert len(set(keys)) == len(keys), f"{lesson.key} repeats a question key"


def test_by_key_finds_them_and_declines_the_rest():
    assert by_key("separable") is LESSONS[0]
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
            assert example.narrator in {"steps", "laplace"}
            assert len(example.why) > 40, (
                f"{lesson.key}/{example.equation} does not say what it shows"
            )
        assert lesson.example == lesson.examples[0].equation


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
    from odesuite_app import laplace, steps

    parsed = _parse(example.equation, example.conditions)
    if example.narrator == "laplace":
        derivation = laplace.derive(parsed.equation, parsed.function,
                                    ics=parsed.ics)
    else:
        derivation = steps.derive(
            parsed.equation, parsed.function,
            hints=sp.classify_ode(parsed.equation, parsed.function(T)),
            ics=parsed.ics,
        )

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
        "from odesuite_app.lessons import LESSONS; assert len(LESSONS) == 7\n"
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
    assert kept["q1"] == store.Answer("correct", right=1, tries=1)
    assert kept["q2"] == store.Answer("attempted", right=0, tries=1)
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
    assert store.load() == {"roots": {"q1": store.Answer("correct", 1, 1)}}


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
