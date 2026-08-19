"""Solve Step by Step: which technique solves your equation, and whether your
answer is right.

The Solver Lab can already type an equation and produce a closed form. This
screen is the same capability aimed at a different question: not *what is the
answer* but *how is this kind of equation solved*, and *is what I wrote
correct*.

At present it names the technique, shows the closed form and checks a typed
answer. The narrated derivation -- the actual steps of separation, integrating
factors, undetermined coefficients -- lands here next, which is why the layout
leaves room for it.
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
from ..widgets.controls import add_heading, control_panel
from ..widgets.equationeditor import EquationEditor
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
        frame = QFrame()
        frame.setProperty("role", "panel")
        outer = QVBoxLayout(frame)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(10)

        self.symbolic = SymbolicPanel(self.palette_obj)
        outer.addWidget(self.symbolic, 1)

        outer.addWidget(self._build_check())
        return frame

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
        self.answer.setPlaceholderText("y = C1*exp(-2*t) + C2*exp(-t)")
        self.answer.setClearButtonEnabled(True)
        row.addWidget(self.answer, 1)

        self.check_button = QPushButton("Check")
        self.check_button.setProperty("role", "primary")
        self.check_button.setCursor(Qt.PointingHandCursor)
        row.addWidget(self.check_button)
        layout.addLayout(row)

        self.verdict = QLabel("")
        self.verdict.setWordWrap(True)
        self.verdict.setTextFormat(Qt.RichText)
        layout.addWidget(self.verdict)

        self.check_button.clicked.connect(self.check)
        self.answer.returnPressed.connect(self.check)
        self._set_enabled(False)
        return box

    # -- behaviour -------------------------------------------------------

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
            self.editor.show_message(str(exc), error=True)
            return

        self.symbolic.solve_for(self._parsed)
        self._set_enabled(True)
        self.verdict.setText("")

    def _on_failed(self, message: str) -> None:
        self._parsed = None
        self._set_enabled(False)

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
