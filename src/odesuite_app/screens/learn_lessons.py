"""Lessons: read the technique, then try it.

The other four Hub screens are tools — you bring an equation and they work on
it. This one assumes you do not yet know which equation to bring. A topic list,
then notes, a worked example, and practice.

The practice is the part worth being careful about, and it works the way the
rest of this application works: a typed solution is **substituted into the
equation and simplified**, through the same `symbolic.check_answer` the Solve
Step by Step screen uses. There is no stored answer to compare against, so any
correct form passes and nothing is marked wrong for being spelled differently.
Where sympy cannot decide, the verdict says so rather than guessing.

Multiple-choice questions do have a stored answer, because *which technique
solves this* is not something a substitution check can grade — and each one
carries its reason, shown whether you got it right or wrong.

Progress is recorded on disk (see `progress`), so the ticks survive closing the
application. Everything expensive — the worked example, and the model solution
for a practice question — happens on the thread pool and only when asked for,
so switching topics stays instant.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import lessons as content
from .. import progress
from ..theme import Palette
from ..widgets.controls import add_heading, control_panel
from ..widgets.mathlabel import MathLabel
from ..widgets.stepspanel import StepsPanel

__all__ = ["LessonsScreen"]


class _Signals(QObject):
    done = Signal(int, object)          # token, Derivation | Exception


class _WorkingJob(QRunnable):
    """Produces the narrated solution for an equation, off the interface thread."""

    def __init__(self, token: int, equation: str, conditions: str,
                 narrator: str, signals: _Signals) -> None:
        super().__init__()
        self.token = token
        self.equation = equation
        self.conditions = conditions
        self.narrator = narrator
        self.signals = signals
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            result = _work_out(self.equation, self.conditions, self.narrator)
        except Exception as exc:                  # surfaced, never swallowed
            result = exc
        try:
            self.signals.done.emit(self.token, result)
        except RuntimeError:
            pass                                  # the screen went away


def _work_out(equation: str, conditions: str, narrator: str):
    """The worked solution, through the same subprocess the Hub tools use."""
    from ..laplace import EXTRA_FUNCTIONS
    from ..symbolic import (
        EquationSpec,
        parse_equation,
        solve_by_laplace,
        solve_symbolically,
    )

    parsed = parse_equation(
        EquationSpec(equations=[equation], initial_conditions=conditions),
        extra_functions=EXTRA_FUNCTIONS,
    )
    if narrator == "laplace":
        return solve_by_laplace(parsed).derivation
    return solve_symbolically(parsed, steps=True).derivation


class LessonsScreen(QWidget):
    """Notes, a worked example, and practice, for each technique in turn."""

    #: Asks the window to open the tool a lesson belongs to.
    open_tool = Signal(str)

    def __init__(self, state, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette
        self._token = 0
        self._answered = progress.load()
        #: Question key -> the widgets that show its verdict.
        self._verdicts: dict[str, QLabel] = {}

        self._signals = _Signals()
        self._signals.done.connect(self._on_worked)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_body(), 1)

        if self.listing.count():
            self.listing.setCurrentRow(0)

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(276)

        add_heading(layout, "Topics")
        note = QLabel(
            "Each one has notes, a worked example, and questions. The count is "
            "how many you have answered correctly."
        )
        note.setProperty("role", "muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        self.listing = QListWidget()
        self.listing.setMinimumHeight(180)
        for lesson in content.LESSONS:
            item = QListWidgetItem(self._label_for(lesson))
            item.setData(Qt.UserRole, lesson.key)
            self.listing.addItem(item)
        layout.addWidget(self.listing)

        self.tool_button = QPushButton("Open the tool for this topic")
        self.tool_button.setProperty("role", "primary")
        self.tool_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.tool_button)

        layout.addStretch(1)

        self.reset_button = QPushButton("Reset progress")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.reset_button)

        where = QLabel(f"Answers are remembered in\n{progress.path()}")
        where.setProperty("role", "muted")
        where.setWordWrap(True)
        where.setStyleSheet("font-size: 10px;")
        layout.addWidget(where)

        self.listing.currentRowChanged.connect(lambda _: self._show())
        self.tool_button.clicked.connect(self._open_tool)
        self.reset_button.clicked.connect(self._reset)
        return panel

    def _build_body(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        outer = QVBoxLayout(frame)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        outer.addWidget(scroll)

        # A reading column, not the full width of the window. Notes set across
        # 1400 pixels are genuinely hard to read -- the eye loses the line on
        # the way back -- and this is the one screen here whose main job is
        # being read rather than being operated.
        holder = QWidget()
        scroll.setWidget(holder)
        across = QHBoxLayout(holder)
        across.setContentsMargins(0, 0, 0, 0)

        self._page = QWidget()
        self._page.setMaximumWidth(900)
        # Stretch as well as a cap: without it the column takes its size hint
        # and the answer boxes collapse to nothing.
        across.addWidget(self._page, 1)
        across.addStretch(0)

        self._layout = QVBoxLayout(self._page)
        self._layout.setContentsMargins(24, 20, 24, 24)
        self._layout.setSpacing(14)
        return frame

    # -- behaviour -------------------------------------------------------

    def _label_for(self, lesson) -> str:
        done, total = progress.counts(lesson.key, len(lesson.questions),
                                      self._answered)
        return f"{lesson.title}   ({done}/{total})"

    def _refresh_labels(self) -> None:
        for row, lesson in enumerate(content.LESSONS):
            item = self.listing.item(row)
            if item is not None:
                item.setText(self._label_for(lesson))

    def current_lesson(self):
        item = self.listing.currentItem()
        return None if item is None else content.by_key(item.data(Qt.UserRole))

    def _show(self) -> None:
        lesson = self.current_lesson()
        if lesson is None:
            return
        self._token += 1                          # abandon anything in flight
        self._clear()
        self._verdicts = {}
        palette = self.palette_obj

        title = QLabel(lesson.title)
        title.setProperty("role", "title")
        title.setWordWrap(True)
        self._layout.addWidget(title)

        summary = QLabel(lesson.summary)
        summary.setProperty("role", "subtitle")
        summary.setWordWrap(True)
        self._layout.addWidget(summary)

        for note in lesson.notes:
            self._layout.addWidget(self._note_card(note))

        self._layout.addWidget(self._example_card(lesson))

        heading = QLabel("Practice")
        heading.setProperty("role", "heading")
        heading.setStyleSheet(f"color: {palette.text}; padding-top: 8px;")
        self._layout.addWidget(heading)

        for number, question in enumerate(lesson.questions, start=1):
            self._layout.addWidget(self._question_card(lesson, number, question))
        self._layout.addStretch(1)

    def _note_card(self, note) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 13, 16, 14)
        layout.setSpacing(8)

        heading = QLabel(note.heading)
        heading.setProperty("role", "heading")
        heading.setWordWrap(True)
        layout.addWidget(heading)

        body = QLabel(note.body)
        body.setWordWrap(True)
        layout.addWidget(body)

        if note.latex:
            maths = MathLabel(self.palette_obj, note.latex, point_size=15)
            layout.addWidget(maths)
        return frame

    def _example_card(self, lesson) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 13, 16, 14)
        layout.setSpacing(8)

        heading = QLabel("Worked example")
        heading.setProperty("role", "heading")
        layout.addWidget(heading)

        shown = lesson.example + (
            f",   {lesson.example_conditions}" if lesson.example_conditions else ""
        )
        equation = QLabel(shown)
        equation.setStyleSheet("font-family: Cascadia Mono, Consolas, monospace;")
        equation.setWordWrap(True)
        layout.addWidget(equation)

        row = QHBoxLayout()
        self.example_button = QPushButton("Work it through")
        self.example_button.setProperty("role", "primary")
        self.example_button.setCursor(Qt.PointingHandCursor)
        row.addWidget(self.example_button)
        row.addStretch(1)
        layout.addLayout(row)

        self.example_steps = StepsPanel(self.palette_obj)
        self.example_steps.setMinimumHeight(260)
        self.example_steps.setVisible(False)
        layout.addWidget(self.example_steps)

        self.example_button.clicked.connect(
            lambda: self._work(lesson.example, lesson.example_conditions,
                               lesson.narrator, self.example_steps,
                               self.example_button)
        )
        return frame

    def _question_card(self, lesson, number: int, question) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 13, 16, 14)
        layout.setSpacing(8)

        prompt = QLabel(f"{number}.  {question.prompt}")
        prompt.setProperty("role", "heading")
        prompt.setWordWrap(True)
        layout.addWidget(prompt)

        if question.kind == "choice":
            self._build_choice(lesson, question, layout)
        else:
            self._build_solve(lesson, question, layout)
        return frame

    def _build_choice(self, lesson, question, layout) -> None:
        if question.latex:
            layout.addWidget(MathLabel(self.palette_obj, question.latex,
                                       point_size=15))

        # Parented to the card, not to the screen: switching topics deletes the
        # cards, and a group owned by the screen would outlive its own radio
        # buttons and accumulate one dead set per topic visited.
        group = QButtonGroup(layout.parentWidget())
        group.setExclusive(True)
        for index, option in enumerate(question.options):
            button = QRadioButton(option)
            button.setCursor(Qt.PointingHandCursor)
            group.addButton(button, index)
            layout.addWidget(button)

        verdict = QLabel("")
        verdict.setWordWrap(True)
        layout.addWidget(verdict)
        self._verdicts[question.key] = verdict

        row = QHBoxLayout()
        check = QPushButton("Check")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)
        row.addStretch(1)
        layout.addLayout(row)

        check.clicked.connect(
            lambda: self._check_choice(lesson, question, group, verdict)
        )
        self._restore(lesson, question, verdict)

    def _build_solve(self, lesson, question, layout) -> None:
        shown = question.equation + (
            f",   {question.conditions}" if question.conditions else ""
        )
        equation = QLabel(shown)
        equation.setStyleSheet("font-family: Cascadia Mono, Consolas, monospace;")
        equation.setWordWrap(True)
        layout.addWidget(equation)

        row = QHBoxLayout()
        row.setSpacing(8)
        answer = QLineEdit()
        answer.setPlaceholderText("y = ...")
        answer.setClearButtonEnabled(True)
        row.addWidget(answer, 1)

        check = QPushButton("Check")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)

        hint_button = QPushButton("Hint")
        hint_button.setCursor(Qt.PointingHandCursor)
        row.addWidget(hint_button)

        show = QPushButton("Show me")
        show.setCursor(Qt.PointingHandCursor)
        row.addWidget(show)
        layout.addLayout(row)

        verdict = QLabel("")
        verdict.setWordWrap(True)
        verdict.setTextFormat(Qt.RichText)
        layout.addWidget(verdict)
        self._verdicts[question.key] = verdict

        hint = QLabel(question.hint)
        hint.setProperty("role", "muted")
        hint.setWordWrap(True)
        hint.setVisible(False)
        layout.addWidget(hint)

        working = StepsPanel(self.palette_obj)
        working.setMinimumHeight(240)
        working.setVisible(False)
        layout.addWidget(working)

        check.clicked.connect(
            lambda: self._check_solve(lesson, question, answer, verdict)
        )
        answer.returnPressed.connect(
            lambda: self._check_solve(lesson, question, answer, verdict)
        )
        hint_button.clicked.connect(lambda: hint.setVisible(True))
        show.clicked.connect(
            lambda: self._work(question.equation, question.conditions,
                               lesson.narrator, working, show)
        )
        self._restore(lesson, question, verdict)

    # -- grading ---------------------------------------------------------

    def _restore(self, lesson, question, verdict: QLabel) -> None:
        """Show what was recorded last time, so a tick survives a restart."""
        state = self._answered.get(lesson.key, {}).get(question.key)
        if state == progress.State.CORRECT:
            verdict.setStyleSheet(f"color: {self.palette_obj.success};")
            verdict.setText("✓ answered correctly")
        elif state == progress.State.ATTEMPTED:
            verdict.setStyleSheet(f"color: {self.palette_obj.text_muted};")
            verdict.setText("attempted")

    def _record(self, lesson, question, state: str) -> None:
        self._answered = progress.record(lesson.key, question.key, state)
        self._refresh_labels()

    def _check_choice(self, lesson, question, group, verdict: QLabel) -> None:
        picked = group.checkedId()
        palette = self.palette_obj
        if picked < 0:
            verdict.setStyleSheet(f"color: {palette.text_muted};")
            verdict.setText("pick an option first")
            return

        right = content.grade_choice(question, picked)
        verdict.setStyleSheet(
            f"color: {palette.success if right else palette.danger};"
        )
        # The reason is shown either way: a tick that does not say why teaches
        # nothing, and a cross without one teaches less.
        verdict.setText(("✓ Right. " if right else "✗ Not quite. ")
                        + question.because)
        self._record(lesson, question,
                     progress.State.CORRECT if right else progress.State.ATTEMPTED)

    def _check_solve(self, lesson, question, answer: QLineEdit,
                     verdict: QLabel) -> None:
        from ..laplace import EXTRA_FUNCTIONS
        from ..symbolic import EquationSpec, check_answer, parse_equation

        palette = self.palette_obj
        try:
            parsed = parse_equation(
                EquationSpec(equations=[question.equation],
                             initial_conditions=question.conditions),
                extra_functions=EXTRA_FUNCTIONS,
            )
        except Exception as exc:                  # a broken question, not a
            verdict.setStyleSheet(f"color: {palette.danger};")   # broken answer
            verdict.setText(f"this question could not be set up: {exc}")
            return

        result = check_answer(parsed, answer.text())
        if result.correct is True and result.matches_conditions is not False:
            colour, text = palette.success, "✓ " + result.message
            state = progress.State.CORRECT
        elif result.correct is False or result.matches_conditions is False:
            colour, text = palette.danger, "✗ " + result.message
            state = progress.State.ATTEMPTED
        else:
            colour, text = palette.text_muted, result.message
            state = progress.State.ATTEMPTED

        detail = ""
        if result.correct is False and result.residual is not None:
            detail = (f'<br><span style="color:{palette.text_muted};'
                      f'font-size:12px;">what is left over: '
                      f"{result.residual}</span>")
        verdict.setStyleSheet("")
        verdict.setText(f'<span style="color:{colour};">{text}</span>{detail}')
        self._record(lesson, question, state)

    # -- the worked solution ---------------------------------------------

    def _work(self, equation: str, conditions: str, narrator: str,
              panel: StepsPanel, button: QPushButton) -> None:
        self._token += 1
        panel.setVisible(True)
        panel.clear("working it through…")
        button.setEnabled(False)
        self._pending = (panel, button)
        QThreadPool.globalInstance().start(
            _WorkingJob(self._token, equation, conditions, narrator,
                        self._signals)
        )

    def _on_worked(self, token: int, result) -> None:
        if token != self._token:
            return                                # superseded
        panel, button = getattr(self, "_pending", (None, None))
        if panel is None:
            return
        button.setEnabled(True)
        if isinstance(result, Exception):
            panel.clear(f"{type(result).__name__}: {result}")
            return
        if result is None:
            panel.clear("no working could be produced for this one")
            return
        panel.show_derivation(result)

    # -- the rest --------------------------------------------------------

    def _open_tool(self) -> None:
        lesson = self.current_lesson()
        if lesson is not None:
            self.open_tool.emit(lesson.tool)

    def _reset(self) -> None:
        progress.reset()
        self._answered = {}
        self._refresh_labels()
        self._show()

    def _clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def set_palette_colours(self, palette: Palette) -> None:
        self.palette_obj = palette
