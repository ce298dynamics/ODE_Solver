"""Solve Step by Step: which technique solves your equation, and whether your
answer is right.

The Solver Lab can already type an equation and produce a closed form. This
screen is the same capability aimed at a different question: not *what is the
answer* but *how is this kind of equation solved*, and *is what I wrote
correct*.

The derivation leads, because it is the point: separation of variables,
integrating factors, characteristic roots, undetermined coefficients and
Cauchy-Euler, written out a step at a time with each step checked. The closed
form and the answer box sit beside it -- useful, but they are the answer, and
this screen is about the method.

Note which panel is which when they disagree. `steps` derives the answer itself
and verifies it independently, so on an equation `dsolve` cannot finish -- it
hangs outright on ``y' = sin(y)`` -- the derivation can still arrive at a
checked solution while the closed form beside it reports a timeout.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..symbolic import ParsedEquation, check_answer
from ..theme import Palette
from ..widgets.answerpreview import AnswerPreview
from ..widgets.controls import add_heading, control_panel
from ..widgets.equationeditor import EquationEditor
from ..widgets.stepspanel import StepsPanel
from ..widgets.symbolicpanel import SymbolicPanel

__all__ = ["StepsScreen"]


class StepsScreen(QWidget):
    """Type an equation; see how it is solved, and check your own answer."""

    def __init__(self, state, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette
        self._parsed: ParsedEquation | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_body(), 1)

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(300)

        add_heading(layout, "Your equation")
        self.editor = EquationEditor(self.palette_obj)
        layout.addWidget(self.editor)
        layout.addStretch(1)

        self.editor.submitted.connect(self._on_submitted)
        self.editor.failed.connect(self._on_failed)
        return panel

    def _build_body(self) -> QWidget:
        """The derivation beside the answer, rather than above or below it.

        Two scrolling regions stacked would put the answer below the fold on a
        long derivation, and the answer box is what a student reaches for after
        reading the steps.
        """
        body = QWidget()
        layout = QHBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        derivation = QFrame()
        derivation.setProperty("role", "panel")
        left = QVBoxLayout(derivation)
        left.setContentsMargins(2, 2, 2, 2)
        self.steps = StepsPanel(self.palette_obj)
        left.addWidget(self.steps)
        layout.addWidget(derivation, 3)

        answer = QFrame()
        answer.setProperty("role", "panel")
        right = QVBoxLayout(answer)
        right.setContentsMargins(12, 10, 12, 10)
        right.setSpacing(10)
        self.symbolic = SymbolicPanel(self.palette_obj)
        self.symbolic.narrate = True          # this screen displays the steps
        self.symbolic.solved.connect(self._on_solved)
        right.addWidget(self.symbolic, 1)
        right.addWidget(self._build_check())
        layout.addWidget(answer, 2)
        return body

    def _build_check(self) -> QWidget:
        box = QFrame()
        box.setProperty("role", "panel")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        heading = QLabel("Check your answer")
        heading.setProperty("role", "heading")
        layout.addWidget(heading)

        note = QLabel(
            "Type what you got. It is substituted back into your equation and "
            "simplified — the same check the closed form above has to pass. "
            "Many forms are equivalent, so this asks whether yours solves the "
            "equation, not whether it looks like the one shown."
        )
        note.setProperty("role", "muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.answer = QLineEdit()
        self.answer.setAccessibleName("your answer")
        self.answer.setPlaceholderText("y = C1*exp(-2*t) + C2*exp(-t)")
        self.answer.setClearButtonEnabled(True)
        row.addWidget(self.answer, 1)

        self.check_button = QPushButton("Check")
        self.check_button.setProperty("role", "primary")
        self.check_button.setCursor(Qt.PointingHandCursor)
        row.addWidget(self.check_button)
        layout.addLayout(row)
        layout.addWidget(AnswerPreview(self.palette_obj, self.answer,
                                       lambda: self._parsed))

        self.verdict = QLabel("")
        self.verdict.setWordWrap(True)
        self.verdict.setTextFormat(Qt.RichText)
        layout.addWidget(self.verdict)

        self.check_button.clicked.connect(self.check)
        self.answer.returnPressed.connect(self.check)
        self._set_enabled(False)
        return box

    # -- behaviour -------------------------------------------------------

    def load_equation(self, equation: str, conditions: str = "") -> None:
        """Type an equation in from elsewhere and work it out.

        The lesson that sends one here has just shown it being solved, so the
        screen it opens should be looking at that equation rather than at
        whatever was last in the box. Nothing is bypassed on the way: the text
        goes into the same fields somebody would type it into, and the same
        submit path reads them.
        """
        self.editor.set_equation(equation, conditions)

    def _set_enabled(self, enabled: bool) -> None:
        self.answer.setEnabled(enabled)
        self.check_button.setEnabled(enabled)
        if not enabled:
            self.verdict.setText(
                f'<span style="color:{self.palette_obj.text_muted};">'
                f"enter an equation first</span>"
            )

    def _on_submitted(self, spec) -> None:
        from ..symbolic import parse_equation

        try:
            self._parsed = parse_equation(spec)
        except Exception as exc:
            self._parsed = None
            self._set_enabled(False)
            self.editor.show_message(str(exc), kind="error")
            return

        self.steps.clear("working out how this one is solved…")
        self.symbolic.solve_for(self._parsed)
        self._set_enabled(True)
        self.verdict.setText("")

    def _on_solved(self, solution) -> None:
        """The worker is done; show whatever derivation came back with it."""
        self.steps.show_derivation(getattr(solution, "derivation", None))

    def _on_failed(self, message: str) -> None:
        self._parsed = None
        self._set_enabled(False)
        self.steps.clear()

    def check(self) -> None:
        """Substitute the typed answer and report the residual."""
        if self._parsed is None:
            return
        result = check_answer(self._parsed, self.answer.text())
        palette = self.palette_obj

        if result.correct is True and result.matches_conditions is not False:
            colour, prefix = palette.success, "✓ "
        elif result.correct is False or result.matches_conditions is False:
            colour, prefix = palette.danger, "✗ "
        else:
            colour, prefix = palette.text_muted, ""

        detail = ""
        if result.correct is False and result.residual is not None:
            detail = (
                f'<br><span style="color:{palette.text_muted};font-size:12px;">'
                f"what is left over: {result.residual}</span>"
            )
        self.verdict.setText(
            f'<span style="color:{colour};">{prefix}{result.message}</span>{detail}'
        )
