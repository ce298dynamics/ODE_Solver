"""What the grader will read, typeset under the box the student is typing in.

An answer is typed as code -- ``exp(-t)*(C1*cos(2*t) + C2*sin(2*t))`` -- and a
single misplaced bracket turns a right answer into a different function, which
the grader then marks wrong as mathematics when it was a typo. Showing the
typed text back as mathematics, while it is being typed, makes the two
distinguishable before Check is pressed: ``exp(-t)*C1*cos(2*t) + C2*sin(2*t)``
looks wrong on sight once it is typeset, and nothing about it looks wrong as
code.

The text is read by `symbolic.read_answer`, the grader's own parser, so the
preview cannot disagree with the mark. Text it cannot read yet gets a quiet
line saying why, never a red one: half-typed is the normal state of a box being
typed in, not a mistake.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget

from ..theme import Palette
from .mathlabel import MathLabel

__all__ = ["AnswerPreview", "DELAY_MS", "question_parser"]

#: How long typing has to pause before the preview is refreshed. Long enough
#: not to parse on every keystroke, short enough to feel live.
DELAY_MS = 250


class AnswerPreview(QWidget):
    """A typeset reading of `answer`, for the equation `parsed()` returns.

    `parsed` is a callable rather than a value because the screens build the
    parsed equation lazily, when Check is first pressed, and some never manage
    to (a broken question). It may return None, and the preview then stays
    hidden.
    """

    def __init__(self, palette: Palette, answer: QLineEdit,
                 parsed: Callable[[], object], parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette
        self._answer = answer
        self._parsed = parsed
        self._rows: list[MathLabel] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 0, 2)
        layout.setSpacing(2)
        self._layout = layout

        self.note = QLabel()
        self.note.setProperty("role", "muted")
        self.note.setWordWrap(True)
        layout.addWidget(self.note)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(DELAY_MS)
        self._timer.timeout.connect(self.refresh)
        answer.textChanged.connect(lambda _: self._timer.start())

        self.setVisible(False)

    @property
    def rows(self) -> list[MathLabel]:
        """The typeset lines currently shown, one per unknown."""
        return [row for row in self._rows if not row.isHidden()]

    def refresh(self) -> None:
        """Re-read the box now. Called by the timer; tests call it directly."""
        from sympy import Eq, Function, Symbol

        from ..custom import ParseError
        from ..symbolic import read_answer

        self._timer.stop()
        text = self._answer.text()
        try:
            parsed = self._parsed()
        except Exception:
            parsed = None
        if parsed is None or not text.strip():
            self.setVisible(False)
            return

        try:
            pairs = read_answer(parsed, text)
        except ParseError as exc:
            self._show_rows([])
            self.note.setText(f"Not readable yet: {exc}")
            self.note.setVisible(True)
            self.setVisible(True)
            return
        except Exception:                       # sympy can raise anything;
            self.setVisible(False)              # a preview must never be the
            return                              # thing that breaks the page

        t = Symbol("t", real=True)
        self._show_rows([Eq(Function(name)(t), expression, evaluate=False)
                         for name, expression in pairs])
        self.note.setText("Read as:")
        self.note.setVisible(True)
        self.setVisible(True)

    def _show_rows(self, equations: list) -> None:
        while len(self._rows) < len(equations):
            row = MathLabel(self.palette_obj)
            self._rows.append(row)
            self._layout.addWidget(row)
        for row, equation in zip(self._rows, equations):
            row.set_expression(equation)
            row.setVisible(True)
        for row in self._rows[len(equations):]:
            row.setVisible(False)

    def set_palette_colours(self, palette: Palette) -> None:
        self.palette_obj = palette
        for row in self._rows:
            row.set_palette_colours(palette)


def question_parser(question):
    """A callable that parses `question` as the grader does, once.

    For the answer preview, which re-reads the box on every pause in typing and
    should not re-parse the question each time. None for a question that
    cannot be parsed: the grader reports that one when Check is pressed, and a
    preview has nothing to add.
    """
    cache: list = []

    def parsed():
        if not cache:
            from ..laplace import EXTRA_FUNCTIONS
            from ..symbolic import parse_equation, spec_for

            try:
                cache.append(parse_equation(
                    spec_for(question.equation, question.conditions),
                    extra_functions=EXTRA_FUNCTIONS,
                ))
            except Exception:
                cache.append(None)
        return cache[0]

    return parsed
