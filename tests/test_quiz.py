"""The unit check-up, and the mastery it reports.

Two claims are worth holding this screen to. The first is that it adds no
mathematics: a quiz question is a drill question, graded by the same
substitution, so anything it says about right and wrong is something the rest
of the Hub already said. The second is subtler and is the reason the screen
exists -- it must not tell you which method the question wants, because
choosing the method is what it is asking.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sympy")
pytest.importorskip("PySide6")

from odesuite_app import progress  # noqa: E402
from odesuite_app.lessons import UNITS, by_key  # noqa: E402
from odesuite_app.screens.learn_quiz import (  # noqa: E402
    DEFAULT_LENGTH,
    build,
    buildable,
)


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def store(tmp_path, monkeypatch):
    """Point the progress file somewhere disposable.

    The real one lives in the user's config directory, and a test that wrote
    there would quietly destroy someone's answers.
    """
    monkeypatch.setattr(progress, "directory", lambda: tmp_path / "odesuite")
    return progress


@pytest.fixture()
def screen(qapp, store):
    from odesuite_app.screens.learn_quiz import QuizScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    made = QuizScreen(SessionState(), PALETTES["dark"])
    made.resize(1400, 900)
    qapp.processEvents()
    yield made
    made.deleteLater()


# ---------------------------------------------------------------------------
# Which units can offer one
# ---------------------------------------------------------------------------


def test_only_units_with_drills_are_offered():
    """A unit with no templates has nothing to draw from. It is absent rather
    than present and empty, which is this project's standing rule."""
    offered = buildable()
    assert offered
    for unit in offered:
        assert unit.quizzable, unit.key
    for unit in UNITS:
        if not unit.quizzable:
            assert unit not in offered


def test_the_series_unit_can_now_be_quizzed():
    """It could not, until generated multiple choice existed. A `Solve` drill
    there would have had to draw from the few parameters where the series
    terminates; what a course actually asks is classification, which
    `ChoiceTemplate` drills and `grade_choice` decides."""
    series = next(unit for unit in UNITS if unit.key == "series")
    assert series.quizzable
    assert series in buildable()


def test_quizzable_respects_a_named_list():
    """`Unit.quiz` names the lessons a check-up may draw on; empty means every
    lesson that has drills."""
    from odesuite_app.lessons.model import Unit

    unit = next(u for u in UNITS if len(u.quizzable) > 1)
    narrowed = Unit(key=unit.key, title=unit.title, summary=unit.summary,
                    lessons=unit.lessons, quiz=(unit.quizzable[0].key,))
    assert [lesson.key for lesson in narrowed.quizzable] == [
        unit.quizzable[0].key
    ]


# ---------------------------------------------------------------------------
# Building the set
# ---------------------------------------------------------------------------


def test_a_set_is_the_length_asked_for():
    unit = buildable()[0]
    assert len(build(unit, 7, seed=0)) == 7


def test_a_short_set_still_touches_several_lessons():
    """Round-robin rather than sampled: mixing is the entire point, and random
    choice could easily hand out five questions from one lesson."""
    unit = next(u for u in buildable() if len(u.quizzable) >= 3)
    lessons = {lesson.key for lesson, _, _ in build(unit, 3, seed=0)}
    assert len(lessons) == 3


def test_every_question_is_one_the_hub_already_grades():
    """The whole design. If these were a new kind of question they would need a
    new grader, and a second grader is a second opinion about what is correct.

    All three kinds come straight from the lessons: a `Solve` graded by
    substituting it into its own equation, a `Choice` by `grade_choice`, and a
    `Numeric` by `grade_numeric` to a tolerance. Each is the type the Drill
    segment already shows, which is why the quiz has no grader of its own.
    """
    from odesuite_app.lessons.model import Choice, Numeric, Solve

    seen = set()
    for unit in buildable():
        for _lesson, _template, question in build(unit, 4, seed=3):
            assert isinstance(question, (Solve, Choice, Numeric))
            seen.add(question.kind)
            if isinstance(question, Solve):
                assert question.equation
                assert question.hints, "a Solve keeps its hint ladder"
            elif isinstance(question, Choice):
                assert question.options
                assert len(question.becauses) == len(question.options)
            else:
                assert question.tolerance > 0
                assert question.because, "a number needs a reason"
    assert seen == {"solve", "choice", "numeric"}, (
        f"the quiz never draws one of the three kinds: {sorted(seen)}"
    )


def test_a_choice_question_reaches_the_quiz_and_is_graded_there(screen, qapp):
    """The series unit is now all generated multiple choice, so this is also
    the test that its questions are answerable at all."""
    from odesuite_app.lessons.model import Choice

    index = next(i for i, unit in enumerate(buildable())
                 if unit.key == "series")
    screen.unit_picker.setCurrentIndex(index)
    screen.length.setValue(4)
    screen._start()
    qapp.processEvents()

    lesson, _template, question = screen._questions[0]
    assert isinstance(question, Choice)
    assert screen.group is not None, "no radio buttons were built"
    assert screen.answer is None, "a Choice must not offer an answer box"

    screen.group.button(question.answer).setChecked(True)
    screen._check(lesson, question)
    qapp.processEvents()
    assert screen._verdicts[0] is True


def test_a_choice_question_with_nothing_picked_says_so(screen, qapp):
    index = next(i for i, unit in enumerate(buildable())
                 if unit.key == "series")
    screen.unit_picker.setCurrentIndex(index)
    screen.length.setValue(4)
    screen._start()
    qapp.processEvents()

    lesson, _template, question = screen._questions[0]
    screen._check(lesson, question)
    assert "pick an option" in screen.verdict.text()
    assert 0 not in screen._verdicts, "nothing was answered, so nothing counts"


def test_the_same_seed_gives_the_same_set():
    # By key rather than by equation: only a `Solve` has one, and the key
    # names the draw, which is what has to be reproducible.
    unit = buildable()[0]
    first = [q.key for _, _, q in build(unit, 6, seed=11)]
    again = [q.key for _, _, q in build(unit, 6, seed=11)]
    assert first == again
    assert len(set(first)) > 1, "a set of six identical questions is not a set"


# ---------------------------------------------------------------------------
# The screen
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("palette", ["dark", "light"])
def test_the_screen_renders_in_both_palettes(qapp, store, palette):
    from odesuite_app.screens.learn_quiz import QuizScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    made = QuizScreen(SessionState(), PALETTES[palette])
    made.resize(1400, 900)
    qapp.processEvents()
    assert not made.grab().isNull()
    made.deleteLater()


def test_a_question_never_names_its_method(screen, qapp):
    """The claim the screen exists for. A drill prompt says "Separate it,
    integrate both sides" -- right in the Drill segment, and fatal here, since
    choosing the method is the question being asked.
    """
    from PySide6.QtWidgets import QLabel

    screen.length.setValue(6)
    screen._start()
    qapp.processEvents()

    shown = " ".join(label.text() for label in screen._page.findChildren(QLabel))
    for lesson_key in ("separable", "linear", "exact", "substitutions"):
        lesson = by_key(lesson_key)
        if lesson is not None:
            assert lesson.title not in shown, "the lesson was named"
    for giveaway in ("Separate it", "integrating factor", "Bernoulli form",
                     "characteristic"):
        assert giveaway not in shown, f"the prompt gave away {giveaway!r}"


def test_working_through_reaches_a_report(screen, qapp):
    screen.length.setValue(4)
    screen._start()
    qapp.processEvents()
    for _ in range(4):
        screen._advance()
        qapp.processEvents()

    assert screen.progress_label.text() == "0 of 4"
    from PySide6.QtWidgets import QLabel

    shown = " ".join(label.text() for label in screen._page.findChildren(QLabel))
    assert "Worth going back to" in shown
    assert "Finished in" in shown


def test_the_report_lists_the_lessons_behind_the_misses(screen, qapp):
    """A missed question is most useful as a pointer to its lesson, so the
    report offers the lesson rather than the question."""
    from PySide6.QtWidgets import QPushButton

    screen.length.setValue(4)
    screen._start()
    qapp.processEvents()
    expected = {lesson.key for lesson, _, _ in screen._questions}
    for _ in range(4):
        screen._advance()
        qapp.processEvents()

    opens = [b for b in screen._page.findChildren(QPushButton)
             if b.text().startswith("Open")]
    assert opens
    seen = []
    screen.open_lesson.connect(seen.append)
    for button in opens:
        button.click()
    assert set(seen) <= expected
    assert seen


def _typed(screen, qapp):
    """Advance to the first question with a box to type into.

    Two of the three question kinds have one; a multiple-choice question does
    not, and which kind arrives first depends on the unit and the seed. So the
    test looks for one rather than assuming the set opens with it.
    """
    for _ in range(len(screen._questions)):
        if screen.answer is not None:
            return screen._questions[screen._index]
        screen._advance()
        qapp.processEvents()
    raise AssertionError("no question in this set can be typed into")


def test_a_second_press_of_check_cannot_turn_a_miss_into_a_hit(screen, qapp):
    """Otherwise the report records persistence rather than what was known."""
    screen.length.setValue(6)
    screen._start()
    qapp.processEvents()

    lesson, _template, question = _typed(screen, qapp)
    index = screen._index
    screen.answer.setText("0")                  # almost certainly wrong
    screen._check(lesson, question)
    qapp.processEvents()
    assert screen._verdicts.get(index) is False

    # The screen has not advanced, so the same question can be answered again.
    if screen._index == index:
        screen._check(lesson, question)
        assert screen._verdicts[index] is False


def test_answering_records_progress(screen, qapp, store):
    screen.length.setValue(6)
    screen._start()
    qapp.processEvents()

    lesson, _template, question = _typed(screen, qapp)
    screen.answer.setText("0")
    screen._check(lesson, question)

    saved = progress.load()
    assert lesson.key in saved
    assert any(key.startswith("quiz-") for key in saved[lesson.key])


def test_starting_a_second_set_resets_the_score(screen, qapp):
    screen.length.setValue(4)
    screen._start()
    qapp.processEvents()
    for _ in range(4):
        screen._advance()
    screen._start()
    qapp.processEvents()

    assert screen._index == 0
    assert screen._verdicts == {}


# ---------------------------------------------------------------------------
# Mastery, aggregated
# ---------------------------------------------------------------------------


def test_unit_progress_counts_questions_and_drills(store):
    unit = buildable()[0]
    lesson = unit.lessons[0]
    for question in lesson.questions[:2]:
        store.record(lesson.key, question.key, store.State.CORRECT)

    standing = progress.unit_progress(unit)
    assert standing.answered == 2
    assert standing.questions == unit.questions
    assert standing.lessons == len(unit.lessons)
    assert 0.0 < standing.fraction < 1.0


def test_an_untouched_unit_reads_as_zero(store):
    standing = progress.unit_progress(buildable()[0], {})
    assert standing.answered == 0
    assert standing.mastered == 0
    assert standing.fraction == 0.0


def test_a_finished_unit_reads_as_one(store):
    unit = buildable()[0]
    everything: dict = {}
    for lesson in unit.lessons:
        everything[lesson.key] = {
            q.key: progress.Answer(state=progress.State.CORRECT, right=1,
                                   tries=1, streak=1)
            for q in lesson.questions
        }
        everything[progress.drill_key(lesson.key)] = {
            t.key: progress.Answer(state=progress.State.CORRECT, right=3,
                                   tries=3, streak=progress.MASTERED_STREAK)
            for t in lesson.templates
        }
    standing = progress.unit_progress(unit, everything)
    assert standing.answered == standing.questions
    assert standing.mastered == standing.drills
    assert standing.fraction == pytest.approx(1.0)
    assert standing.finished == standing.lessons


def test_weakest_names_only_lessons_already_started(store):
    """A lesson never opened is not weak, it is simply next. Listing it would
    make "what to review" a second table of contents."""
    lesson = UNITS[0].lessons[0]
    everything = {
        lesson.key: {
            lesson.questions[0].key: progress.Answer(
                state=progress.State.ATTEMPTED, right=0, tries=1, streak=0,
            )
        }
    }
    weak = progress.weakest(UNITS, everything)

    assert [item[0].key for item in weak] == [lesson.key]
    assert weak[0][1] is UNITS[0]


def test_weakest_leaves_out_finished_lessons(store):
    lesson = UNITS[0].lessons[0]
    everything = {
        lesson.key: {
            q.key: progress.Answer(state=progress.State.CORRECT, right=1,
                                   tries=1, streak=1)
            for q in lesson.questions
        }
    }
    assert progress.weakest(UNITS, everything) == []


def test_weakest_puts_the_worst_first(store):
    first, second = UNITS[0].lessons[0], UNITS[0].lessons[1]
    everything = {
        # `second` is half done; `first` has been attempted and got nothing.
        first.key: {
            first.questions[0].key: progress.Answer(
                state=progress.State.ATTEMPTED, right=0, tries=2, streak=0)
        },
        second.key: {
            q.key: progress.Answer(state=progress.State.CORRECT, right=1,
                                   tries=1, streak=1)
            for q in second.questions[:len(second.questions) // 2]
        },
    }
    weak = progress.weakest(UNITS, everything)
    assert [item[0].key for item in weak][0] == first.key


def test_the_course_map_says_what_to_review(qapp, store):
    from odesuite_app.screens.learn_course import CourseScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    made = CourseScreen(SessionState(), PALETTES["dark"])
    qapp.processEvents()
    assert "Nothing to review yet" in made.review_label.text()

    lesson = UNITS[0].lessons[0]
    store.record(lesson.key, lesson.questions[0].key, store.State.ATTEMPTED)
    made.refresh()
    qapp.processEvents()
    assert lesson.title in made.review_label.text()
    made.deleteLater()


def test_the_default_length_is_a_sitting():
    assert 4 <= DEFAULT_LENGTH <= 20
