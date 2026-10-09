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

    Every kind comes straight from the lessons: a `Solve` graded by
    substituting it into its own equation, a `Choice` by `grade_choice`, a
    `Numeric` by `grade_numeric` to a tolerance, and a `Model` or an
    `Expression` by the equivalence graders the Drill segment uses. Each is a
    type the Drill segment already shows, which is why the quiz still has no
    grader of its own.

    It was three kinds and is now five. The two later ones arrived with the
    drills that ask for an equation rather than a solution -- *write the
    equation for this tank*, *write the integrating factor* -- and they reach
    the quiz the moment a set is long enough to come round to the lesson that
    holds them, which is what this test is really for: a question type can be
    added to a lesson without anybody remembering that the quiz draws from the
    same templates.
    """
    from odesuite_app.lessons.model import (
        Choice,
        Expression,
        Model,
        Numeric,
        Solve,
    )

    seen = set()
    for unit in buildable():
        for _lesson, _template, question in build(unit, 4, seed=3):
            assert isinstance(question,
                              (Solve, Choice, Numeric, Model, Expression))
            seen.add(question.kind)
            if isinstance(question, Solve):
                assert question.equation
                assert question.hints, "a Solve keeps its hint ladder"
            elif isinstance(question, Choice):
                assert question.options
                assert len(question.becauses) == len(question.options)
            elif isinstance(question, Model):
                assert question.equation, "a model keeps the equation it wants"
                assert question.because, "a model needs an account of itself"
            elif isinstance(question, Expression):
                assert question.answer
                assert question.because, "a step needs a reason"
            else:
                assert question.tolerance > 0
                assert question.because, "a number needs a reason"
    assert {"solve", "choice", "numeric"} <= seen, (
        f"the quiz never draws one of the three original kinds: {sorted(seen)}"
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


def test_the_report_says_how_far_each_miss_got(screen, qapp):
    """A cross says a question was missed. It cannot say how, and how is what
    somebody would go back for -- so the report carries the same sentence the
    verdict gave at the time, which for a typed answer is the residual read
    back through `symbolic.diagnose`."""
    from PySide6.QtWidgets import QLabel

    from odesuite_app.lessons.model import Solve

    lesson, template, _drawn = build(buildable()[0], 1, seed=7)[0]
    # A question with a known miss, so the sentence under it is known too.
    # Everything else about the screen is the ordinary path.
    screen._questions = [(lesson, template, Solve(
        key="made-up", prompt="Solve it.", equation="y'' - y = 6*t",
    ))]
    screen._verdicts = {}
    screen._notes = {}
    screen._index = 0
    screen._show_question()
    qapp.processEvents()

    screen.answer.setText("C1*exp(t) + C2*exp(-t)")
    screen._check(screen._questions[0][0], screen._questions[0][2])
    qapp.processEvents()
    assert "complementary function" in screen.verdict.text(), (
        "the verdict itself should say what the residual says"
    )

    screen._advance()
    qapp.processEvents()
    shown = " ".join(label.text() for label in screen._page.findChildren(QLabel))
    assert "Question 1" in shown
    assert "complementary function" in shown, (
        "the report kept how far the answer got"
    )


def test_a_skipped_question_says_it_was_skipped(screen, qapp):
    """Distinguished from a wrong answer, because they are different things
    and only one of them is evidence about the mathematics."""
    from PySide6.QtWidgets import QLabel

    screen.length.setValue(4)
    screen._start()
    qapp.processEvents()
    for _ in range(4):
        screen._advance()
        qapp.processEvents()

    shown = " ".join(label.text() for label in screen._page.findChildren(QLabel))
    assert "Skipped" in shown


def _started(screen, qapp):
    screen.length.setValue(6)
    screen._start()
    qapp.processEvents()
    return screen


def test_the_note_is_pinned_by_the_first_answer(screen, qapp):
    """As the verdict is. A second attempt that got further would otherwise
    have the report describe an answer that was never scored."""
    lesson, _template, question = _typed(_started(screen, qapp), qapp)
    screen.answer.setText("0")
    screen._check(lesson, question)
    qapp.processEvents()
    if screen._verdicts.get(screen._index) is not False:
        pytest.skip("this draw accepts 0, so there is no miss to pin")

    first = screen._notes[screen._index]
    screen.answer.setText("1")
    screen._check(lesson, question)
    assert screen._notes[screen._index] == first


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
    """Otherwise the report records persistence rather than what was known.

    Two things this test used to get wrong, both of which made it fail on the
    runs where the quiz happened to draw the wrong question:

    * the paper was seeded from the wall clock, so which questions appeared
      depended on *when* the test ran -- `seed_override` pins it;
    * it typed "0" and asserted the answer was marked wrong, on the strength of
      a comment reading "almost certainly wrong". Since numeric drills arrived,
      some questions have 0 as their answer. The miss is now found rather than
      assumed.
    """
    screen.seed_override = 20_260_907
    screen.length.setValue(6)
    screen._start()
    qapp.processEvents()

    # Walk the paper until "0" actually misses. Which question that is depends
    # on the unit, and the invariant under test does not care which.
    for _ in range(6):
        lesson, _template, question = _typed(screen, qapp)
        index = screen._index
        screen.answer.setText("0")
        screen._check(lesson, question)
        qapp.processEvents()
        if screen._verdicts.get(index) is False:
            break
        if screen._index == index:      # graded but did not advance
            screen._advance()
            qapp.processEvents()
    else:
        pytest.skip("this paper has no question that '0' gets wrong")

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


# ---------------------------------------------------------------------------
# Papers: the same machinery, spanning a term and against a clock
# ---------------------------------------------------------------------------


def _pick_paper(screen, key: str) -> None:
    """Select a paper in the picker, which holds units and papers together."""
    index = next(
        i for i in range(screen.unit_picker.count())
        if screen.unit_picker.itemData(i) == ("paper", key)
    )
    screen.unit_picker.setCurrentIndex(index)


def test_the_picker_offers_the_units_first_and_then_the_papers(screen):
    """One control for both. They are two lengths of the same exercise rather
    than two exercises, and a mode switch would be three clicks where one does.
    """
    from odesuite_app import exam

    data = [screen.unit_picker.itemData(i)
            for i in range(screen.unit_picker.count())]
    assert data[:len(buildable())] == [("unit", unit.key)
                                       for unit in buildable()]
    assert data[len(buildable()):] == [("paper", paper.key)
                                       for paper in exam.PAPERS]


def test_choosing_a_unit_reports_no_paper(screen):
    """A paper is not a unit and must not be made to look like one: reporting
    its first unit from `current_unit` would have Start build a check-up."""
    screen.unit_picker.setCurrentIndex(0)
    assert screen.current_unit() is buildable()[0]
    assert screen.current_paper() is None


def test_choosing_a_paper_fixes_the_length_and_promises_the_time(screen, qapp):
    from odesuite_app import exam

    _pick_paper(screen, "exam-1")
    qapp.processEvents()
    paper = exam.by_key("exam-1")

    assert screen.current_unit() is None
    assert screen.current_paper() is paper
    assert not screen.length.isEnabled(), (
        "a paper's size is part of what makes it that paper"
    )
    assert screen.length.value() == paper.questions
    assert str(paper.minutes) in screen.mode_note.text()


def test_a_check_up_runs_no_countdown(screen, qapp):
    """The distinction the screen exists to draw. A timer counting down turns
    practice into an examination, and this is not one."""
    screen.unit_picker.setCurrentIndex(0)
    screen.length.setValue(4)
    screen._start()
    qapp.processEvents()

    assert screen._paper is None
    assert not screen._clock.isActive()
    assert not screen.clock_label.isVisible()
    assert "No countdown" in screen.mode_note.text()


def test_a_paper_is_the_papers_length_and_runs_the_clock(screen, qapp):
    from odesuite_app import exam
    from odesuite_app.lessons import unit_of

    _pick_paper(screen, "exam-1")
    screen.seed_override = 7
    screen._start()
    qapp.processEvents()

    paper = exam.by_key("exam-1")
    assert len(screen._questions) == paper.questions
    assert screen._paper is paper
    assert screen._clock.isActive()
    assert screen._left == paper.seconds
    assert "0 left" in screen.clock_label.text()

    spread = {unit_of(lesson).key for lesson, _, _ in screen._questions}
    assert spread == set(paper.units), (
        "a cumulative paper that stays in one unit is a check-up"
    )


def test_running_out_of_time_ends_the_paper_and_keeps_the_score(screen, qapp):
    """Every unanswered question counts as missed, which is what would have
    happened. A report that quietly shortened itself to the questions reached
    would flatter the score by exactly the amount that ran out of time."""
    from PySide6.QtWidgets import QLabel

    _pick_paper(screen, "exam-1")
    screen.seed_override = 7
    screen._start()
    qapp.processEvents()
    total = len(screen._questions)

    screen._left = 1
    screen._tick()
    qapp.processEvents()

    assert not screen._clock.isActive()
    assert not screen.clock_label.isVisible()
    assert len(screen._verdicts) == total
    assert not any(screen._verdicts.values())
    shown = " ".join(label.text() for label in screen._page.findChildren(QLabel))
    assert "Time ran out" in shown
    assert f"0 of {total}" in screen.progress_label.text()


def test_finishing_a_paper_stops_its_clock(screen, qapp):
    """A finished paper counting down behind its own report would be the kind
    of loose end nobody notices until it fires into a deleted widget."""
    _pick_paper(screen, "exam-1")
    screen.seed_override = 7
    screen._start()
    qapp.processEvents()
    for _ in range(len(screen._questions)):
        screen._advance()
        qapp.processEvents()

    assert not screen._clock.isActive()
    assert not screen.clock_label.isVisible()


def test_a_paper_reports_itself_by_name(screen, qapp):
    from PySide6.QtWidgets import QLabel

    _pick_paper(screen, "exam-2")
    screen.seed_override = 3
    screen._start()
    qapp.processEvents()
    for _ in range(len(screen._questions)):
        screen._advance()
    qapp.processEvents()

    shown = " ".join(label.text() for label in screen._page.findChildren(QLabel))
    assert "Exam 2" in shown


# ---------------------------------------------------------------------------
# The queue of what was missed
# ---------------------------------------------------------------------------


def test_the_report_offers_the_missed_questions_again(screen, qapp):
    """Retrieval practice is worth most in the minutes after the miss. A list
    of lessons to go back to is true, useful, and something almost nobody does
    at eleven at night."""
    screen.length.setValue(4)
    screen.seed_override = 21
    screen._start()
    qapp.processEvents()
    missed = list(screen._questions)
    for _ in range(4):
        screen._advance()
    qapp.processEvents()

    assert screen.retry_button is not None
    assert "4 again" in screen.retry_button.text()

    screen.retry_button.click()
    qapp.processEvents()
    assert screen._retrying
    assert screen._index == 0
    assert screen._verdicts == {}
    assert screen._questions == missed, (
        "a retry is the same draws, not fresh ones on the same techniques"
    )


def test_only_the_missed_questions_are_requeued(screen, qapp):
    screen.length.setValue(6)
    screen.seed_override = 21
    screen._start()
    qapp.processEvents()
    drawn = list(screen._questions)

    # Two right, the rest missed.
    screen._verdicts = {0: True, 1: False, 2: True, 3: False, 4: False,
                        5: False}
    screen._index = 6
    screen._show_question()
    qapp.processEvents()

    screen.retry_button.click()
    qapp.processEvents()
    assert screen._questions == [drawn[1], drawn[3], drawn[4], drawn[5]]


def test_a_retry_is_never_timed_even_after_a_paper(screen, qapp):
    """A second pass is practice whatever the first was -- and a retry that
    inherited the paper's clock would put a four-question queue under a
    fifty-minute countdown that had already run down."""
    _pick_paper(screen, "exam-1")
    screen.seed_override = 7
    screen._start()
    qapp.processEvents()
    for _ in range(len(screen._questions)):
        screen._advance()
    qapp.processEvents()

    screen.retry_button.click()
    qapp.processEvents()
    assert screen._paper is None
    assert not screen._clock.isActive()
    assert not screen.clock_label.isVisible()


def test_nothing_missed_offers_no_queue(screen, qapp):
    """A button that cannot do anything is worse than an absent one."""
    from PySide6.QtWidgets import QLabel

    screen.length.setValue(4)
    screen._start()
    qapp.processEvents()
    screen._verdicts = {index: True for index in range(4)}
    screen._index = 4
    screen._show_question()
    qapp.processEvents()

    assert screen.retry_button is None
    shown = " ".join(label.text() for label in screen._page.findChildren(QLabel))
    assert "Nothing missed" in shown


def test_a_retry_can_itself_be_retried(screen, qapp):
    """A second miss is a third chance."""
    screen.length.setValue(4)
    screen.seed_override = 21
    screen._start()
    qapp.processEvents()
    for _ in range(4):
        screen._advance()
    qapp.processEvents()
    screen.retry_button.click()
    qapp.processEvents()
    for _ in range(len(screen._questions)):
        screen._advance()
    qapp.processEvents()

    assert screen.retry_button is not None


# ---------------------------------------------------------------------------
# The two kinds a long set reaches that a short one never did
# ---------------------------------------------------------------------------


def _drawn(kind: str):
    """One drawn question of `kind`, with the lesson behind it."""
    from odesuite_app.lessons import generate

    for unit in UNITS:
        for lesson in unit.lessons:
            for template in lesson.templates:
                question = generate.draw(template, 0)
                if question.kind == kind:
                    return lesson, template, question
    pytest.skip(f"the course has no {kind} drill")


@pytest.mark.parametrize("kind", ["model", "expression"])
def test_a_question_graded_by_equivalence_is_graded_at_all(screen, qapp, kind):
    """Both reached the quiz as soon as a set was long enough to cycle round to
    them, and until `_check_equivalent` existed a `Model` was reported as a
    question that could not be set up and an `Expression`, having no equation
    at all, took the screen down."""
    lesson, template, question = _drawn(kind)
    screen._run([(lesson, template, question)])
    qapp.processEvents()

    assert screen.answer is not None, "there must be something to type into"
    right = question.equation if kind == "model" else question.answer
    screen.answer.setText(right)
    screen._check(lesson, question)
    qapp.processEvents()
    assert screen._verdicts[0] is True
    assert "✓" in screen.verdict.text()


@pytest.mark.parametrize("kind", ["model", "expression"])
def test_a_wrong_answer_to_one_is_marked_wrong(screen, qapp, kind):
    lesson, template, question = _drawn(kind)
    screen._run([(lesson, template, question)])
    qapp.processEvents()

    screen.answer.setText("y' = 1 + t + t**2 + t**3" if kind == "model"
                          else "t**3 + 7")
    screen._check(lesson, question)
    qapp.processEvents()
    assert screen._verdicts[0] is False
    assert screen._notes[0], "a miss with nothing said about it is a bare cross"


def test_a_model_question_never_shows_its_own_answer(screen, qapp):
    """`Model.equation` is the answer rather than the question -- and it is the
    very field every other kind prints."""
    from PySide6.QtWidgets import QLabel

    lesson, template, question = _drawn("model")
    screen._run([(lesson, template, question)])
    qapp.processEvents()

    shown = " ".join(label.text() for label in screen._page.findChildren(QLabel))
    assert question.prompt in shown
    assert question.equation not in shown
