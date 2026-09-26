"""Check-ups and exams: a mixed set, drawn from a unit or from a whole term.

The Lessons screen asks about one topic at a time, which is how you learn a
technique and not how you are examined on one. An exam mixes the unit up and
does not tell you which method each question wants -- and choosing the method
is most of the difficulty, as anyone who has done well on every section and
badly on the paper can attest. That gap is what this screen is for.

**A quiz question is an ordinary drill question.** `generate.draw` returns the
very same `Solve` or `Choice` the Practice and Drill segments use, so it is
graded the same way -- by substitution or by `grade_choice` -- and recorded
through the same `progress`. The quiz contributes no mathematics of its own and
therefore cannot disagree with the rest of the Hub about what is correct, which
is the same argument that made the Drill cheap to add.

Every question type appears, and the mix is the point. A `Solve` asks you to
work the method out; a generated `Choice` asks the thing a substitution check
can never grade -- which technique this is, whether a point is ordinary, what
the indicial roots are; a `Numeric` asks for a value and is graded to a
tolerance; and a `Model` or an `Expression` asks for the equation itself or for
one move of a method, graded by equivalence rather than by substitution. Five
kinds, five graders, and not one of them written here.

**A check-up has no countdown; an exam paper does.** The distinction is the
whole reason both are here. For a unit check-up the clock runs and the report
says how long it took, which is enough to learn your pace by; a timer counting
down would turn practice into an examination, and an interruption would cost
something, which matters for a tool someone opens between other things. An
`exam.Paper` is an examination -- it spans a term's units, it is sized like the
real paper and it is given the real paper's time -- and running one without the
clock would rehearse everything about it except the part people actually lose
marks to. When the time goes, the paper ends and the report opens; nothing is
thrown away, and every unanswered question counts as missed, which is what
would have happened.

**A paper spans units; a check-up spans one.** Told a set is about Chapter 3
you have been handed half the answer to every question in it. `exam.build`
interleaves the units of a whole term so that the only thing a question tells
you is that it is on the syllabus, which is the condition the real paper sets.

**What you got wrong is a queue, not a list.** Retrieval practice is worth most
in the minutes after the miss, and the report used to end at a list of lessons
to go back to -- true, useful, and something almost nobody does at eleven at
night. So the report offers the missed questions again, the same draws, one
button away. A second pass is untimed whatever the first was: it is practice.

A unit appears in the picker only if its lessons have drills to draw on. Every
unit does now: the series unit had none until generated multiple choice existed,
because a `Solve` drill there would have had to draw from the handful of
parameters where the series terminates.
"""

from __future__ import annotations

import time
from html import escape

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .. import exam, progress, theme
from .. import lessons as content
from ..theme import Palette
from ..widgets.controls import add_heading, control_panel
from ..widgets.lessonfigure import build_figure
from ..widgets.mathlabel import MathLabel

__all__ = ["QuizScreen"]

#: How many questions a check-up offers by default. Ten is long enough that the
#: mix is genuinely mixed and short enough to finish in a sitting.
DEFAULT_LENGTH = 10

#: How long before the end a countdown starts warning, in seconds. Five minutes
#: is the invigilator's announcement, and it is announced because it changes
#: what a candidate should do next.
WARN_SECONDS = 5 * 60


def buildable() -> tuple:
    """The units a quiz can actually be drawn from."""
    return tuple(unit for unit in content.UNITS if unit.quizzable)


def build(unit, length: int, seed: int) -> list:
    """`length` questions from `unit`, as ``(lesson, template, question)``.

    Round-robin across the unit's lessons, through `exam.draw_from` -- which is
    the same routine that builds a whole paper, so a check-up and an exam
    cannot drift apart about what a mixed set means. See its docstring for why
    the round-robin is across lessons rather than templates.
    """
    return exam.draw_from(unit.quizzable, length, seed)


class QuizScreen(QWidget):
    """Pick a unit or a paper, sit it, and requeue whatever was missed."""

    #: Asks the window to open the Lessons screen at a particular lesson.
    open_lesson = Signal(str)

    def __init__(self, state, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette

        #: The questions in flight, and what has been answered.
        self._questions: list = []
        self._index = 0
        self._verdicts: dict[int, bool] = {}
        #: How far each answer got, by question index -- the sentence the
        #: report shows beside a miss. Separate from `_verdicts` because it is
        #: a different kind of fact: the verdict decides the score and this
        #: decides what to say about it, and a report that could only say
        #: "wrong" four times is the thing this exists to stop.
        self._notes: dict[int, str] = {}
        self._started = 0.0
        #: Fixed seed for the next paper, or None to draw from the clock.
        #: Exists so a test can ask for a particular paper; unused in the app.
        self.seed_override: int | None = None

        #: The paper being sat, or None for a unit check-up. Only a paper is
        #: timed, so this is also what says whether the countdown runs.
        self._paper = None
        #: Seconds left, and the timer that spends them. The timer is a child
        #: of the screen, so it dies with it rather than firing into a deleted
        #: widget.
        self._left = 0
        self._clock = QTimer(self)
        self._clock.setInterval(1000)
        self._clock.timeout.connect(self._tick)
        #: True while re-running the questions missed in the set just finished.
        #: A retry is practice rather than an examination, so it is never
        #: timed. It can itself be retried: a second miss is a third chance.
        self._retrying = False
        #: The report's queue button, or None when there is nothing to requeue.
        self.retry_button = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_body(), 1)
        self._show_start()

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(268)

        add_heading(layout, "Check-up or exam")
        blurb = QLabel(
            "A mixed set, in no particular order. Working out *which* method a "
            "question wants is most of what an exam asks, and it is the one "
            "thing lesson-by-lesson practice cannot rehearse."
        )
        blurb.setProperty("role", "muted")
        blurb.setWordWrap(True)
        layout.addWidget(blurb)

        # One picker for both, units first. They are two lengths of the same
        # exercise rather than two exercises, and a second control to choose
        # between two modes -- each of which then needs its own list -- would
        # be three clicks where one does.
        self.unit_picker = QComboBox()
        self.unit_picker.setAccessibleName("quiz or exam")
        for unit in buildable():
            self.unit_picker.addItem(f"Unit — {unit.title}",
                                     ("unit", unit.key))
        for paper in exam.PAPERS:
            self.unit_picker.addItem(
                f"{paper.title} — {paper.reference}", ("paper", paper.key)
            )
        self.unit_picker.currentIndexChanged.connect(self._source_changed)
        layout.addWidget(self.unit_picker)

        self.source_note = QLabel("")
        self.source_note.setProperty("role", "muted")
        self.source_note.setWordWrap(True)
        layout.addWidget(self.source_note)

        add_heading(layout, "Questions", space_above=8)
        self.length = QSpinBox()
        self.length.setAccessibleName("number of questions")
        self.length.setRange(4, 20)
        self.length.setValue(DEFAULT_LENGTH)
        self.length.setToolTip(
            "How many questions a check-up asks. A paper is the length of the "
            "paper it stands in for, so this is fixed while one is chosen."
        )
        layout.addWidget(self.length)

        self.start_button = QPushButton("Start")
        self.start_button.setProperty("role", "primary")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.clicked.connect(self._start)
        layout.addWidget(self.start_button)

        # The countdown, present only while a paper is in flight. Hidden rather
        # than blank: a clock reading nothing is a clock somebody has to look
        # at twice to find out it means nothing.
        self.clock_label = QLabel("")
        self.clock_label.setProperty("role", "title")
        self.clock_label.setVisible(False)
        layout.addWidget(self.clock_label)

        self.progress_label = QLabel("")
        self.progress_label.setProperty("role", "muted")
        self.progress_label.setWordWrap(True)
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)

        layout.addStretch(1)

        self.mode_note = QLabel("")
        self.mode_note.setProperty("role", "muted")
        self.mode_note.setWordWrap(True)
        layout.addWidget(self.mode_note)

        self._source_changed()
        return panel

    def _build_body(self) -> QWidget:
        self._scroll = QScrollArea()
        self._scroll.setAccessibleName("quiz questions")
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._page = QWidget()
        self._layout = QVBoxLayout(self._page)
        self._layout.setContentsMargins(4, 0, 12, 12)
        self._layout.setSpacing(12)
        self._scroll.setWidget(self._page)
        return self._scroll

    # -- state -----------------------------------------------------------

    def _clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _panel(self, accent: str = "") -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setProperty("role", "panel")
        if accent:
            # Object name, not a bare `QFrame`: QLabel is a QFrame, so an
            # unscoped rule borders every label inside the card as well.
            frame.setObjectName("accentPanel")
            frame.setStyleSheet(
                f"QFrame#accentPanel {{ border-left: 3px solid {accent}; }}"
            )
        inner = QVBoxLayout(frame)
        inner.setContentsMargins(16, 13, 16, 14)
        inner.setSpacing(8)
        return frame, inner

    def chosen(self) -> tuple[str, str]:
        """``(kind, key)`` for the picker: ``("unit", …)`` or ``("paper", …)``."""
        data = self.unit_picker.currentData()
        if isinstance(data, tuple) and len(data) == 2:
            return data
        # A combo entry written before the pairs existed, or a bare key from a
        # test. Read as a unit, which is what it was.
        return ("unit", data) if data else ("", "")

    def current_unit(self):
        """The unit chosen, or None -- including when a paper is chosen.

        A paper is not a unit and must not be made to look like one: reporting
        its first unit here would have `_start` quietly build a check-up.
        """
        kind, key = self.chosen()
        return content.unit_by_key(key) if kind == "unit" and key else None

    def current_paper(self):
        kind, key = self.chosen()
        return exam.by_key(key) if kind == "paper" and key else None

    def _source_changed(self) -> None:
        """Re-word the panel for whichever of the two is chosen.

        The length spin is disabled rather than hidden while a paper is
        chosen. A paper's size is part of what makes it that paper, and a
        control that silently stopped mattering would be worse than one that
        visibly does not apply.
        """
        paper = self.current_paper()
        if paper is None:
            unit = self.current_unit()
            self.source_note.setText(unit.summary if unit is not None else "")
            self.length.setEnabled(True)
            self.start_button.setToolTip(
                "Begin the set. Nothing is timed, and you can stop at any "
                "point."
            )
            self.mode_note.setText(
                "No countdown — the clock only reports how long you took."
            )
            return
        self.source_note.setText(paper.summary)
        self.length.setEnabled(False)
        self.length.setValue(min(max(paper.questions, self.length.minimum()),
                                 self.length.maximum()))
        self.start_button.setToolTip(
            f"Sit {paper.title}: {paper.questions} questions in "
            f"{paper.minutes} minutes"
        )
        self.mode_note.setText(
            f"{paper.questions} questions in {paper.minutes} minutes — about "
            f"{paper.pace:.1f} a question. The clock counts down, and when it "
            "reaches zero the paper ends and the report opens. Nothing is "
            "lost; whatever is unanswered counts as missed, which is what "
            "would have happened."
        )

    def _show_start(self) -> None:
        self._clear()
        frame, inner = self._panel(self.palette_obj.accent)
        heading = QLabel("Ready when you are")
        heading.setProperty("role", "heading")
        inner.addWidget(heading)
        units = buildable()
        body = QLabel(
            f"{len(units)} of the {len(content.UNITS)} units have drills to "
            f"draw a check-up from, and {len(exam.PAPERS)} papers span them "
            "the way a term does. Pick one on the left and press Start. "
            "Every question is graded exactly as the practice is: a typed "
            "answer by substituting it into its own equation, so any correct "
            "form passes, and a multiple-choice one against its answer."
        )
        body.setWordWrap(True)
        inner.addWidget(body)
        self._layout.addWidget(frame)
        self._layout.addStretch(1)
        self.progress_label.setText("")
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(0)

    def _seed(self) -> int:
        """The seed for the next paper.

        The clock is the right seed for a quiz -- sitting it twice should not
        give the same paper -- and the wrong one for a test, which then depends
        on when it runs. `seed_override` is the seam: nothing in the
        application sets it, and a test that needs a particular paper can.

        This is not hypothetical. `test_a_second_press_of_check_cannot_turn_a
        _miss_into_a_hit` typed "0" and assumed it wrong; once numeric drills
        existed, some questions have 0 as their answer, and the test began
        failing on the runs that happened to draw one.
        """
        if self.seed_override is not None:
            return self.seed_override
        return int(time.time()) % 100_000

    def _start(self) -> None:
        paper = self.current_paper()
        if paper is not None:
            self._run(exam.build(paper, self._seed()), paper=paper)
            return
        unit = self.current_unit()
        if unit is None:
            return
        self._run(build(unit, self.length.value(), seed=self._seed()))

    def _run(self, questions: list, *, paper=None, retrying: bool = False
             ) -> None:
        """Begin a set. The one path in, so nothing can start half-reset.

        Every field that describes a sitting is cleared here, including the
        two that decide whether the clock runs. A retry reaching this with
        `paper` left over from the sitting it came out of would put an
        untimed second pass under a countdown.
        """
        self._questions = questions
        self._verdicts = {}
        self._notes = {}
        self._index = 0
        self._retrying = retrying
        self._paper = paper
        self._started = time.perf_counter()
        self._start_clock(paper)
        self._show_question()

    # -- the clock -------------------------------------------------------

    def _start_clock(self, paper) -> None:
        """Run a countdown for a paper, and none for anything else."""
        self._clock.stop()
        if paper is None:
            self._left = 0
            self.clock_label.setVisible(False)
            return
        self._left = paper.seconds
        self.clock_label.setVisible(True)
        self._show_clock()
        self._clock.start()

    def _tick(self) -> None:
        self._left = max(self._left - 1, 0)
        self._show_clock()
        if self._left <= 0:
            self._time_up()

    def _show_clock(self) -> None:
        minutes, seconds = divmod(max(self._left, 0), 60)
        colour = (self.palette_obj.danger if self._left <= WARN_SECONDS
                  else self.palette_obj.text)
        self.clock_label.setStyleSheet(f"color: {colour};")
        self.clock_label.setText(f"{minutes}:{seconds:02d} left")

    def _time_up(self) -> None:
        """End the paper and open the report.

        Everything unanswered is settled as missed rather than dropped. That is
        what happens to an unanswered question on the real paper, and a report
        that quietly shortened itself to the questions reached would flatter
        the score by exactly the amount that ran out of time.
        """
        self._clock.stop()
        self.clock_label.setVisible(False)
        for index in range(len(self._questions)):
            self._verdicts.setdefault(index, False)
            self._notes.setdefault(index, "Time ran out before this one.")
        self._index = len(self._questions)
        self._show_question()

    def _retry_missed(self) -> None:
        """Run the questions just missed again, as the same draws.

        The same `(lesson, template, question)` triples rather than a fresh
        draw from the same templates. A fresh draw would be a different
        question about the same technique, which is a fine thing to do next and
        is what "Another set" is for; the thing worth doing in the minute after
        a miss is the question that was missed.
        """
        wrong = [index for index, value in sorted(self._verdicts.items())
                 if not value and index < len(self._questions)]
        if not wrong:
            return
        self._run([self._questions[index] for index in wrong], retrying=True)

    def _question_figure(self, question, layout) -> None:
        """Put a question's own figure above its prompt, where it has one.

        The same helper the Lessons screen has, because a quiz question *is*
        an ordinary question: one that asks what a phase portrait shows has to
        show one here too, or the quiz would silently drop the only leg of the
        rule of four this application has just learned to assess.
        """
        key = getattr(question, "figure", "")
        if not key:
            return
        figure = build_figure(key, self.palette_obj)
        if figure is not None:
            layout.addWidget(figure)

    def _show_question(self) -> None:
        self._clear()
        if self._index >= len(self._questions):
            self._show_report()
            return

        lesson, _template, question = self._questions[self._index]
        total = len(self._questions)
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(self._index)
        self.progress_label.setText(f"Question {self._index + 1} of {total}")

        frame, inner = self._panel()
        heading = QLabel(f"Question {self._index + 1}")
        heading.setProperty("role", "heading")
        inner.addWidget(heading)

        # Neither the template's prompt nor the lesson's name is shown, and
        # that is the whole design. A drill prompt says "Separate it, integrate
        # both sides" -- perfectly right in the Drill segment, where you have
        # just read the lesson, and fatal here: choosing the method *is* the
        # question a check-up asks, so anything that answers it has to go.
        choosing = question.kind == "choice"
        counting = question.kind == "numeric"
        # Four of the five kinds ask for something specific -- a number, an
        # option, the equation for a situation, one move of a method -- and
        # their own prompts name none of the techniques, so those are shown.
        # Only a `Solve` prompt gives the method away, and only it is replaced.
        asking = question.kind in ("choice", "numeric", "model", "expression")
        prompt = QLabel(
            question.prompt if asking
            else "Solve it." if not question.conditions
            else "Solve it, and satisfy the condition."
        )
        prompt.setWordWrap(True)
        inner.addWidget(prompt)
        self._question_figure(question, inner)

        # A Choice carries real LaTeX and is typeset; a Solve carries source
        # text, which is shown monospaced. Running generated source through the
        # renderer produces a mangled image or a silent fallback, and typesetting
        # a `\,` as literal characters is just as wrong the other way.
        #
        # A `Model` is the one question here whose `equation` field is the
        # *answer* rather than the question -- it asks you to write the
        # equation for a situation -- so it must never be printed. Its `latex`
        # carries the situation's data, and its prompt carries the rest.
        if asking:
            if question.latex:
                inner.addWidget(MathLabel(self.palette_obj, question.latex,
                                          point_size=15))
            if getattr(question, "shown", ""):
                # A generated `Choice` -- which method, which portrait, what
                # went wrong -- carries its equation as text rather than as
                # LaTeX, because the equation came out of the draw and could
                # not be authored twice. Without this the question asks about
                # an equation it never shows.
                written = QLabel(question.shown)
                written.setStyleSheet(
                    theme.scaled("font-family: Cascadia Mono, Consolas, "
                                 "monospace; font-size: 15px;")
                )
                written.setWordWrap(True)
                inner.addWidget(written)
        else:
            shown = question.equation + (
                f",   {question.conditions}" if question.conditions else ""
            )
            equation = QLabel(shown)
            equation.setStyleSheet(
                theme.scaled("font-family: Cascadia Mono, Consolas, monospace; "
                             "font-size: 15px;")
            )
            equation.setWordWrap(True)
            inner.addWidget(equation)

        self.answer = None
        self.group = None
        if choosing:
            # A generated multiple-choice question. Its own prompt *is* shown,
            # unlike a Solve's: a Choice prompt asks the question rather than
            # naming the method, so it gives nothing away.
            self.group = QButtonGroup(self._page)
            self.group.setExclusive(True)
            for index, option in enumerate(question.options):
                button = QRadioButton(option)
                button.setCursor(Qt.PointingHandCursor)
                self.group.addButton(button, index)
                inner.addWidget(button)
        else:
            self.answer = QLineEdit()
            self.answer.setAccessibleName("your answer")
            self.answer.setPlaceholderText(
                "a number" if counting
                else "an equation, with an = in it" if question.kind == "model"
                else "an expression" if question.kind == "expression"
                else "y = …"
            )
            if counting and question.units:
                row = QHBoxLayout()
                row.addWidget(self.answer, 1)
                units = QLabel(question.units)
                units.setProperty("role", "muted")
                row.addWidget(units)
                inner.addLayout(row)
            else:
                inner.addWidget(self.answer)

        self.verdict = QLabel("")
        self.verdict.setWordWrap(True)
        inner.addWidget(self.verdict)

        row = QHBoxLayout()
        check = QPushButton("Check")
        check.setToolTip("Mark this answer and move on")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        check.clicked.connect(lambda: self._check(lesson, question))
        row.addWidget(check)

        skip = QPushButton("Skip")
        skip.setToolTip("Leave this one unanswered and go to the next")
        skip.setCursor(Qt.PointingHandCursor)
        skip.clicked.connect(self._advance)
        row.addWidget(skip)
        row.addStretch(1)
        inner.addLayout(row)

        if self.answer is not None:
            self.answer.returnPressed.connect(
                lambda: self._check(lesson, question)
            )
        self._layout.addWidget(frame)
        self._layout.addStretch(1)
        self._scroll.verticalScrollBar().setValue(0)

    def _check(self, lesson, question) -> None:
        if question.kind in ("model", "expression"):
            self._check_equivalent(lesson, question)
            return
        if question.kind == "choice":
            self._check_choice(lesson, question)
            return
        if question.kind == "numeric":
            self._check_numeric(lesson, question)
            return
        self._check_solve(lesson, question)

    def _check_numeric(self, lesson, question) -> None:
        """Graded to a tolerance, which is what a number deserves.

        The lessons whose answer is a number rather than a function -- one
        Euler step, a terminal velocity, a trace -- reach the quiz through
        here. As in the Drill segment there are three verdicts: a number that
        could not be read is an attempt, not a mistake.
        """
        from ..symbolic import grade_numeric

        palette = self.palette_obj
        right, message = grade_numeric(question, self.answer.text())
        if right is None:
            self.verdict.setStyleSheet(f"color: {palette.text_muted};")
            self.verdict.setText(message)
            return
        colour = palette.success if right else palette.danger
        self.verdict.setStyleSheet(f"color: {colour};")
        mark = "✓ " if right else "✗ "
        because = f"  —  {question.because}" if question.because else ""
        self.verdict.setText(mark + message + because)
        # A number is either near enough or it is not, so "how far it got" can
        # only be the value it missed and the reason that value is the answer.
        self._settle(lesson, question, right,
                     message + (f" {question.because}" if question.because
                                else ""))

    def _check_equivalent(self, lesson, question) -> None:
        """Graded by equivalence, for the two kinds that are not solutions.

        A `Model` asks for the equation a situation satisfies and an
        `Expression` for one move of a method -- the integrating factor, the
        characteristic polynomial. Neither is a solution, so there is nothing
        to substitute either into, and `check_answer` has no purchase on them.
        `symbolic.check_model` and `check_expression` compare two pieces of
        mathematics instead, which is why ``y' = 2 - y/20`` and
        ``20y' + y = 40`` are one answer.

        These reached the quiz as soon as a set was long enough to cycle round
        to the three templates that produce them, and until this existed they
        fell through to the `Solve` path -- where a `Model` was reported as a
        question that could not be set up and an `Expression`, having no
        equation at all, was worse. Both are now graded as the lessons intend.
        """
        from ..symbolic import mark_equivalent

        palette = self.palette_obj
        result, marking = mark_equivalent(question, self.answer.text())
        right = marking.tone == "right"
        colour = {"right": palette.success,
                  "wrong": palette.danger}.get(marking.tone, palette.text_muted)
        self.verdict.setStyleSheet(f"color: {colour};")
        self.verdict.setText(marking.headline
                             + (f"  —  {marking.detail}" if marking.detail else ""))
        # The difference is the useful half of a wrong verdict here: a
        # forgotten inflow term or a sign that went the other way appears in
        # it by itself, which no restatement of the right answer would show.
        note = result.message
        if result.difference is not None:
            note = f"{note} (out by {result.difference})"
        self._settle(lesson, question, right, note)

    def _check_choice(self, lesson, question) -> None:
        """Graded by `grade_choice`, which is what this question type is for.

        The lessons a substitution check cannot decide -- switched forcing,
        impulses, series classification -- reach the quiz through here.
        """
        palette = self.palette_obj
        picked = self.group.checkedId() if self.group else -1
        if picked < 0:
            self.verdict.setStyleSheet(f"color: {palette.text_muted};")
            self.verdict.setText("pick an option first")
            return

        right = content.grade_choice(question, picked)
        # The reason for the option *picked*, as everywhere else in the Hub: a
        # cross that explains somebody else's answer teaches less than nothing.
        reason = (question.becauses[picked]
                  if picked < len(question.becauses) else "")
        self.verdict.setStyleSheet("")
        colour = palette.success if right else palette.danger
        self.verdict.setText(
            f'<span style="color:{colour};">'
            f'{"✓ Right. " if right else "✗ Not quite. "}{reason}</span>'
        )
        # The reason for the option picked is exactly "how far this got": the
        # distractors are written as misconceptions, one apiece.
        self._settle(lesson, question, right,
                     f"You chose “{question.options[picked]}”. {reason}"
                     if picked < len(question.options) else reason)

    def _check_solve(self, lesson, question) -> None:
        from ..laplace import EXTRA_FUNCTIONS
        from ..symbolic import check_answer, parse_equation, spec_for

        palette = self.palette_obj
        try:
            parsed = parse_equation(
                spec_for(question.equation, question.conditions),
                extra_functions=EXTRA_FUNCTIONS,
            )
        except Exception as exc:
            self.verdict.setStyleSheet(f"color: {palette.danger};")
            self.verdict.setText(f"this question could not be set up: {exc}")
            return

        result = check_answer(parsed, self.answer.text())
        right = (result.correct is True
                 and result.matches_conditions is not False)
        colour = (palette.success if right
                  else palette.danger if result.correct is False
                  else palette.text_muted)
        mark = "✓ " if right else "✗ " if result.correct is False else ""
        # `symbolic.diagnose` reads the residual for what it usually says --
        # the complementary function without a particular solution, a lost
        # coefficient, the right family and the wrong member of it. Shown here
        # as it is on the lesson card, and kept for the report, which is the
        # difference between a set of crosses and a list of what to fix.
        detail = ""
        if result.diagnosis:
            detail = (f'<br><span style="color:{palette.text_muted};'
                      f'font-size:12px;">{result.diagnosis}</span>')
        self.verdict.setStyleSheet("")
        self.verdict.setText(
            f'<span style="color:{colour};">{mark}{result.message}</span>'
            + detail
        )
        self._settle(lesson, question, right,
                     result.diagnosis or result.message)

    def _settle(self, lesson, question, right: bool, note: str = "") -> None:
        """Record the verdict and move on if it was right.

        Only the first verdict on a question counts, so pressing Check twice
        cannot turn a miss into a hit -- which would make the report a record
        of persistence rather than of what was known. `note` is pinned by the
        same first answer and for the same reason: it has to describe the
        attempt that was scored, not a later one.
        """
        self._verdicts.setdefault(self._index, right)
        if note:
            self._notes.setdefault(self._index, note)
        progress.record(
            lesson.key, f"quiz-{question.key}",
            progress.State.CORRECT if right else progress.State.ATTEMPTED,
        )
        if right:
            self._advance()

    def _advance(self) -> None:
        self._verdicts.setdefault(self._index, False)
        self._notes.setdefault(self._index, "Skipped — nothing was typed.")
        self._index += 1
        self._show_question()

    # -- the report ------------------------------------------------------

    def _show_report(self) -> None:
        self._clear()
        # A paper that was worked to the end rather than timed out still has a
        # clock running. Stopping it here rather than only in `_time_up` is
        # what keeps a finished paper from counting down behind its own report.
        self._clock.stop()
        self.clock_label.setVisible(False)

        total = len(self._questions)
        right = sum(1 for value in self._verdicts.values() if value)
        elapsed = max(time.perf_counter() - self._started, 0.0)
        self.progress_bar.setValue(total)
        self.progress_label.setText(f"{right} of {total}")

        frame, inner = self._panel(self.palette_obj.accent)
        heading = QLabel(f"{right} of {total}")
        heading.setProperty("role", "title")
        inner.addWidget(heading)

        paper = self._paper
        if paper is not None:
            sat = QLabel(
                f"{paper.title} · {paper.reference} · "
                f"{100 * right / total:.0f}%" if total else paper.title
            )
            sat.setProperty("role", "muted")
            sat.setWordWrap(True)
            inner.addWidget(sat)

        minutes, seconds = divmod(int(elapsed), 60)
        pace = QLabel(
            f"Finished in {minutes} min {seconds:02d} s"
            + (f" — about {elapsed / total:.0f} s a question."
               if total else ".")
            + (f"  The paper allows {paper.minutes} minutes."
               if paper is not None else "")
            + ("  Time ran out." if paper is not None and self._left <= 0
               else "")
        )
        pace.setProperty("role", "muted")
        pace.setWordWrap(True)
        inner.addWidget(pace)
        self._layout.addWidget(frame)

        wrong = [index for index, value in sorted(self._verdicts.items())
                 if not value and index < len(self._questions)]
        missed = [self._questions[index][0] for index in wrong]
        if not missed:
            done, inner2 = self._panel(self.palette_obj.success)
            label = QLabel(
                "Nothing missed on the retry. That is the pass that counts — "
                "the one taken straight after the miss."
                if self._retrying else
                "Nothing missed. This unit is worth an exam."
            )
            label.setWordWrap(True)
            inner2.addWidget(label)
            self._layout.addWidget(done)
        else:
            seen = []
            for lesson in missed:
                if lesson.key not in [item.key for item in seen]:
                    seen.append(lesson)
            card, inner2 = self._panel(self.palette_obj.warning)
            label = QLabel("Worth going back to")
            label.setProperty("role", "heading")
            inner2.addWidget(label)
            note = QLabel(
                "A missed question is most useful as a pointer to the lesson "
                "behind it, which is why the ways back in are listed by "
                "lesson rather than by question."
            )
            note.setProperty("role", "muted")
            note.setWordWrap(True)
            inner2.addWidget(note)

            # How far each one got, before the lessons to go back to. Most
            # wrong answers are not wrong in the same way -- the method right
            # and the constants not, the complementary function without a
            # particular solution, the option that always forgets the constant
            # -- and a report that says only "✗ four times" throws away
            # every one of those distinctions at the moment they are most
            # useful.
            for index in wrong:
                inner2.addWidget(self._miss(index))
            for lesson in seen:
                button = QPushButton(f"Open  {lesson.title}")
                button.setToolTip(
                    f"Go to {lesson.title}, where this question came from"
                )
                button.setCursor(Qt.PointingHandCursor)
                button.clicked.connect(
                    lambda _=False, key=lesson.key: self.open_lesson.emit(key)
                )
                inner2.addWidget(button)
            self._layout.addWidget(card)

        # The queue, above the ways back into the lessons and above another
        # set, because it is the thing worth doing first and by some distance:
        # retrieval practice is worth most in the minutes after the miss, and
        # a list of lessons to revisit is something almost nobody does at
        # eleven at night.
        if wrong:
            self.retry_button = QPushButton(
                f"Try those {len(wrong)} again" if len(wrong) > 1
                else "Try that one again"
            )
            self.retry_button.setToolTip(
                "The same questions, straight away and untimed — not fresh "
                "ones on the same techniques"
            )
            self.retry_button.setProperty("role", "primary")
            self.retry_button.setCursor(Qt.PointingHandCursor)
            self.retry_button.clicked.connect(self._retry_missed)
            self._layout.addWidget(self.retry_button)
        else:
            self.retry_button = None

        again = QPushButton("Another set")
        again.setToolTip(
            "Draw a fresh set of questions from whatever is chosen on the left"
        )
        if not wrong:
            again.setProperty("role", "primary")
        again.setCursor(Qt.PointingHandCursor)
        again.clicked.connect(self._start)
        self._layout.addWidget(again)
        self._layout.addStretch(1)

    def _miss(self, index: int) -> QLabel:
        """One line of the report: which question, and how far it got.

        Escaped, because the sentence is built from a question's own options
        and from a residual read back through `symbolic.diagnose`, and a "<"
        in either would swallow the rest of the line as a tag.
        """
        lesson, _template, question = self._questions[index]
        note = self._notes.get(index, "")
        label = QLabel(
            f'<b>Question {index + 1}</b> · {escape(lesson.title)}'
            + (f'<br><span style="color:{self.palette_obj.text_muted};">'
               f'{escape(note)}</span>' if note else "")
        )
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)
        return label

    def refresh(self) -> None:
        """Nothing to reload: a quiz in progress should survive a visit
        elsewhere, and one not started has nothing to show."""
