"""Unit Quiz: a mixed set, drawn from a unit's drills.

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

Both question types appear, and the mix is the point. A `Solve` asks you to
work the method out; a generated `Choice` asks the thing a substitution check
can never grade -- which technique this is, whether a point is ordinary, what
the indicial roots are.

**There is no countdown.** The clock runs and the report says how long it took,
which is enough to learn your pace by; a timer counting down turns practice
into an examination, and this is not one. It also means an interruption costs
nothing, which matters for a tool someone opens between other things.

A unit appears in the picker only if its lessons have drills to draw on. Every
unit does now: the series unit had none until generated multiple choice existed,
because a `Solve` drill there would have had to draw from the handful of
parameters where the series terminates.
"""

from __future__ import annotations

import time

from PySide6.QtCore import Qt, Signal
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

from .. import lessons as content
from .. import progress
from ..lessons import generate
from ..theme import Palette
from ..widgets.controls import add_heading, control_panel
from ..widgets.mathlabel import MathLabel

__all__ = ["QuizScreen"]

#: How many questions a check-up offers by default. Ten is long enough that the
#: mix is genuinely mixed and short enough to finish in a sitting.
DEFAULT_LENGTH = 10


def buildable() -> tuple:
    """The units a quiz can actually be drawn from."""
    return tuple(unit for unit in content.UNITS if unit.quizzable)


def build(unit, length: int, seed: int) -> list:
    """`length` questions from `unit`, as ``(lesson, template, question)``.

    Round-robin across the unit's **lessons**, not across its templates. That
    distinction matters: a lesson with two drills would otherwise take two of
    the first few slots and crowd another lesson out of a short set, which is
    the opposite of what a mixed set is for. Within a lesson the templates
    take turns as the rounds come round.
    """
    lessons = [lesson for lesson in unit.quizzable if lesson.templates]
    if not lessons:
        return []
    out = []
    for index in range(length):
        lesson = lessons[index % len(lessons)]
        round_number = index // len(lessons)
        template = lesson.templates[round_number % len(lesson.templates)]
        out.append((lesson, template, generate.draw(template, seed + index)))
    return out


class QuizScreen(QWidget):
    """Pick a unit, answer a mixed set, and see what to go back to."""

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
        self._started = 0.0
        #: Fixed seed for the next paper, or None to draw from the clock.
        #: Exists so a test can ask for a particular paper; unused in the app.
        self.seed_override: int | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_body(), 1)
        self._show_start()

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(268)

        add_heading(layout, "Unit check-up")
        blurb = QLabel(
            "A mixed set from one unit, in no particular order. Working out "
            "*which* method a question wants is most of what an exam asks, "
            "and it is the one thing lesson-by-lesson practice cannot "
            "rehearse."
        )
        blurb.setProperty("role", "muted")
        blurb.setWordWrap(True)
        layout.addWidget(blurb)

        self.unit_picker = QComboBox()
        for unit in buildable():
            self.unit_picker.addItem(unit.title, unit.key)
        layout.addWidget(self.unit_picker)

        add_heading(layout, "Questions", space_above=8)
        self.length = QSpinBox()
        self.length.setRange(4, 20)
        self.length.setValue(DEFAULT_LENGTH)
        layout.addWidget(self.length)

        self.start_button = QPushButton("Start")
        self.start_button.setToolTip(
            "Begin the set. Nothing is timed, and you can stop at any point."
        )
        self.start_button.setProperty("role", "primary")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.clicked.connect(self._start)
        layout.addWidget(self.start_button)

        self.progress_label = QLabel("")
        self.progress_label.setProperty("role", "muted")
        self.progress_label.setWordWrap(True)
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)

        layout.addStretch(1)

        note = QLabel(
            "No countdown — the clock only reports how long you took."
        )
        note.setProperty("role", "muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        return panel

    def _build_body(self) -> QWidget:
        self._scroll = QScrollArea()
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

    def current_unit(self):
        key = self.unit_picker.currentData()
        return content.unit_by_key(key) if key else None

    def _show_start(self) -> None:
        self._clear()
        frame, inner = self._panel(self.palette_obj.accent)
        heading = QLabel("Ready when you are")
        heading.setProperty("role", "heading")
        inner.addWidget(heading)
        units = buildable()
        body = QLabel(
            f"{len(units)} of the {len(content.UNITS)} units have drills to "
            "draw a check-up from. Pick one on the left and press Start. "
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

    def _start(self) -> None:
        unit = self.current_unit()
        if unit is None:
            return
        # The clock is the right seed for a quiz -- sitting it twice should not
        # give the same paper -- and the wrong one for a test, which then
        # depends on when it runs. `seed_override` is the seam: nothing in the
        # application sets it, and a test that needs a particular paper can.
        #
        # This is not hypothetical. `test_a_second_press_of_check_cannot_turn_a
        # _miss_into_a_hit` typed "0" and assumed it wrong; once numeric drills
        # existed, some questions have 0 as their answer, and the test began
        # failing on the runs that happened to draw one.
        seed = (
            self.seed_override
            if self.seed_override is not None
            else int(time.time()) % 100_000
        )
        self._questions = build(unit, self.length.value(), seed=seed)
        self._verdicts = {}
        self._index = 0
        self._started = time.perf_counter()
        self._show_question()

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
        # A numeric question's own prompt is shown for the same reason a
        # choice's is: it asks for a specific number rather than naming a
        # method, so it gives nothing away about which technique to reach for.
        prompt = QLabel(
            question.prompt if choosing or counting
            else "Solve it." if not question.conditions
            else "Solve it, and satisfy the condition."
        )
        prompt.setWordWrap(True)
        inner.addWidget(prompt)

        # A Choice carries real LaTeX and is typeset; a Solve carries source
        # text, which is shown monospaced. Running generated source through the
        # renderer produces a mangled image or a silent fallback, and typesetting
        # a `\,` as literal characters is just as wrong the other way.
        if choosing or counting:
            if question.latex:
                inner.addWidget(MathLabel(self.palette_obj, question.latex,
                                          point_size=15))
        else:
            shown = question.equation + (
                f",   {question.conditions}" if question.conditions else ""
            )
            equation = QLabel(shown)
            equation.setStyleSheet(
                "font-family: Cascadia Mono, Consolas, monospace; "
                "font-size: 15px;"
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
            self.answer.setPlaceholderText(
                "a number" if counting else "y = …"
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
        self._settle(lesson, question, right)

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
        self._settle(lesson, question, right)

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
        self.verdict.setStyleSheet("")
        self.verdict.setText(
            f'<span style="color:{colour};">{mark}{result.message}</span>'
        )
        self._settle(lesson, question, right)

    def _settle(self, lesson, question, right: bool) -> None:
        """Record the verdict and move on if it was right.

        Only the first verdict on a question counts, so pressing Check twice
        cannot turn a miss into a hit -- which would make the report a record
        of persistence rather than of what was known.
        """
        self._verdicts.setdefault(self._index, right)
        progress.record(
            lesson.key, f"quiz-{question.key}",
            progress.State.CORRECT if right else progress.State.ATTEMPTED,
        )
        if right:
            self._advance()

    def _advance(self) -> None:
        self._verdicts.setdefault(self._index, False)
        self._index += 1
        self._show_question()

    # -- the report ------------------------------------------------------

    def _show_report(self) -> None:
        self._clear()
        total = len(self._questions)
        right = sum(1 for value in self._verdicts.values() if value)
        elapsed = max(time.perf_counter() - self._started, 0.0)
        self.progress_bar.setValue(total)
        self.progress_label.setText(f"{right} of {total}")

        frame, inner = self._panel(self.palette_obj.accent)
        heading = QLabel(f"{right} of {total}")
        heading.setProperty("role", "title")
        inner.addWidget(heading)

        minutes, seconds = divmod(int(elapsed), 60)
        pace = QLabel(
            f"Finished in {minutes} min {seconds:02d} s"
            + (f" — about {elapsed / total:.0f} s a question."
               if total else ".")
        )
        pace.setProperty("role", "muted")
        pace.setWordWrap(True)
        inner.addWidget(pace)
        self._layout.addWidget(frame)

        missed = [self._questions[index][0]
                  for index, value in sorted(self._verdicts.items())
                  if not value]
        if not missed:
            done, inner2 = self._panel(self.palette_obj.success)
            label = QLabel("Nothing missed. This unit is worth an exam.")
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
                "behind it, which is why they are listed by lesson rather "
                "than by question."
            )
            note.setProperty("role", "muted")
            note.setWordWrap(True)
            inner2.addWidget(note)
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

        again = QPushButton("Another set")
        again.setToolTip("Draw a fresh set of questions from this unit")
        again.setProperty("role", "primary")
        again.setCursor(Qt.PointingHandCursor)
        again.clicked.connect(self._start)
        self._layout.addWidget(again)
        self._layout.addStretch(1)

    def refresh(self) -> None:
        """Nothing to reload: a quiz in progress should survive a visit
        elsewhere, and one not started has nothing to show."""
