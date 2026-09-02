"""Unit Quiz: a mixed set, drawn from a unit's drills.

The Lessons screen asks about one topic at a time, which is how you learn a
technique and not how you are examined on one. An exam mixes the unit up and
does not tell you which method each question wants -- and choosing the method
is most of the difficulty, as anyone who has done well on every section and
badly on the paper can attest. That gap is what this screen is for.

**A quiz question is an ordinary drill question.** `generate.draw` returns the
same `Solve` the Practice and Drill segments use, so it is graded by the same
substitution, hinted by the same ladder, worked by the same narrator, and
recorded through the same `progress`. The quiz contributes no mathematics of
its own and therefore cannot disagree with the rest of the Hub about what is
correct -- the same argument that made the Drill cheap to add.

**There is no countdown.** The clock runs and the report says how long it took,
which is enough to learn your pace by; a timer counting down turns practice
into an examination, and this is not one. It also means an interruption costs
nothing, which matters for a tool someone opens between other things.

A unit appears in the picker only if its lessons have drills to draw on. Unit 7
has none -- a series drill would have to draw from the handful of parameters
where the series terminates -- so it is absent rather than present and empty,
which is this application's standing rule about placeholders.
"""

from __future__ import annotations

import time

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
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

__all__ = ["QuizScreen"]

#: How many questions a check-up offers by default. Ten is long enough that the
#: mix is genuinely mixed and short enough to finish in a sitting.
DEFAULT_LENGTH = 10


def buildable() -> tuple:
    """The units a quiz can actually be drawn from."""
    return tuple(unit for unit in content.UNITS if unit.quizzable)


def build(unit, length: int, seed: int) -> list:
    """`length` questions from `unit`, as ``(lesson, template, Solve)``.

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
            frame.setStyleSheet(f"QFrame {{ border-left: 3px solid {accent}; }}")
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
            "draw a check-up from. Pick one on the left and press Start — "
            "every question is graded the same way the practice is, by "
            "substituting what you type into the equation."
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
        self._questions = build(unit, self.length.value(),
                                seed=int(time.time()) % 100_000)
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
        prompt = QLabel("Solve it." if not question.conditions
                        else "Solve it, and satisfy the condition.")
        prompt.setWordWrap(True)
        inner.addWidget(prompt)

        # Monospace rather than typeset, as the Drill card does it: a generated
        # equation is source text, and running it through the LaTeX renderer
        # produces either a mangled image or a silent fallback to this anyway.
        shown = question.equation + (
            f",   {question.conditions}" if question.conditions else ""
        )
        equation = QLabel(shown)
        equation.setStyleSheet(
            "font-family: Cascadia Mono, Consolas, monospace; font-size: 15px;"
        )
        equation.setWordWrap(True)
        inner.addWidget(equation)

        self.answer = QLineEdit()
        self.answer.setPlaceholderText("y = …")
        inner.addWidget(self.answer)

        self.verdict = QLabel("")
        self.verdict.setWordWrap(True)
        inner.addWidget(self.verdict)

        row = QHBoxLayout()
        check = QPushButton("Check")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        check.clicked.connect(lambda: self._check(lesson, question))
        row.addWidget(check)

        skip = QPushButton("Skip")
        skip.setCursor(Qt.PointingHandCursor)
        skip.clicked.connect(self._advance)
        row.addWidget(skip)
        row.addStretch(1)
        inner.addLayout(row)

        self.answer.returnPressed.connect(lambda: self._check(lesson, question))
        self._layout.addWidget(frame)
        self._layout.addStretch(1)
        self._scroll.verticalScrollBar().setValue(0)

    def _check(self, lesson, question) -> None:
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
        # Only the first verdict on a question counts, so pressing Check twice
        # cannot turn a miss into a hit -- which would make the report a
        # record of persistence rather than of what was known.
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
                button.setCursor(Qt.PointingHandCursor)
                button.clicked.connect(
                    lambda _=False, key=lesson.key: self.open_lesson.emit(key)
                )
                inner2.addWidget(button)
            self._layout.addWidget(card)

        again = QPushButton("Another set")
        again.setProperty("role", "primary")
        again.setCursor(Qt.PointingHandCursor)
        again.clicked.connect(self._start)
        self._layout.addWidget(again)
        self._layout.addStretch(1)

    def refresh(self) -> None:
        """Nothing to reload: a quiz in progress should survive a visit
        elsewhere, and one not started has nothing to show."""
