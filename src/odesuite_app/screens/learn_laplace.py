"""Laplace Transforms: turn the equation into algebra, solve it, turn it back.

The screen a first course needs for the one technique that handles a switch
thrown partway through. ``y' + y = u(t-2)`` is not separable, has no integrating
factor worth writing, and is not what undetermined coefficients is for — and it
is three lines of algebra here.

Laid out like `Solve Step by Step`, because they are the same kind of screen and
the section should feel like one place: the equation on the left, the derivation
taking the larger half, and the reference beside it. The reference here is the
**transform table**, with the rows this particular answer needed marked — so it
reads as a table being consulted rather than as decoration.

Two things are different from the other Hub screens, both deliberate.

It accepts `Heaviside` and `DiracDelta`, which the rest of the application does
not. That widening lives here because this is the only path that never reaches
an integrator; see `laplace.EXTRA_FUNCTIONS`.

It runs its own solve rather than borrowing `SymbolicPanel`'s. `dsolve` is not
wanted here — the derivation carries the answer and checks it — and skipping the
one call that can hang makes the screen answer in about a second.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import laplace
from ..theme import Palette
from ..widgets.controls import add_heading, control_panel
from ..widgets.equationeditor import EquationEditor
from ..widgets.mathlabel import MathLabel
from ..widgets.stepspanel import StepsPanel

__all__ = ["LaplaceScreen"]


class _Signals(QObject):
    done = Signal(int, object)          # token, SymbolicSolution | Exception


class _LaplaceJob(QRunnable):
    """Runs the transform off the interface thread."""

    def __init__(self, token: int, parsed, signals: _Signals) -> None:
        super().__init__()
        self.token = token
        self.parsed = parsed
        self.signals = signals
        self.setAutoDelete(True)

    def run(self) -> None:
        from ..symbolic import solve_by_laplace

        try:
            result = solve_by_laplace(self.parsed)
        except Exception as exc:                  # surfaced, never swallowed
            result = exc
        try:
            self.signals.done.emit(self.token, result)
        except RuntimeError:
            pass                                  # the screen went away


class LaplaceScreen(QWidget):
    """Type an equation; watch it become algebra and come back."""

    def __init__(self, state, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette
        self._token = 0

        self._signals = _Signals()
        self._signals.done.connect(self._on_done)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_derivation(), 3)
        layout.addWidget(self._build_table(), 2)

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(300)

        add_heading(layout, "Your equation")
        note = QLabel(
            "Give initial conditions at t = 0 — the transform integrates from "
            "there, and they enter the method at the start rather than at the "
            "end.\n\nThis screen also accepts a switch, Heaviside(t-2), and an "
            "impulse, DiracDelta(t-1), which is what the transform is for."
        )
        note.setProperty("role", "muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        self.editor = EquationEditor(self.palette_obj)
        layout.addWidget(self.editor)
        layout.addStretch(1)

        self.editor.submitted.connect(self._on_submitted)
        self.editor.failed.connect(self._on_failed)
        return panel

    def _build_derivation(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(2, 2, 2, 2)
        self.steps = StepsPanel(self.palette_obj)
        self.steps.clear("Type an equation to see it transformed.")
        layout.addWidget(self.steps)
        return frame

    def _build_table(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        outer = QVBoxLayout(frame)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(8)

        heading = QLabel("Transform table")
        heading.setProperty("role", "heading")
        outer.addWidget(heading)

        self.table_note = QLabel(
            "The pairs a course memorises. Once an equation is solved, the "
            "rows it needed are highlighted."
        )
        self.table_note.setProperty("role", "muted")
        self.table_note.setWordWrap(True)
        outer.addWidget(self.table_note)

        scroll = QScrollArea()
        scroll.setAccessibleName("transform derivation")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        page = QWidget()
        scroll.setWidget(page)
        grid = QGridLayout(page)
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(12)

        for column, title in enumerate(("f(t)", "F(s)")):
            label = QLabel(title)
            label.setProperty("role", "muted")
            grid.addWidget(label, 0, column)

        #: Row widgets by pair key, so a solve can highlight the ones it used.
        self._rows: dict[str, list[QWidget]] = {}
        for index, pair in enumerate(laplace.TABLE, start=1):
            left = MathLabel(self.palette_obj, pair.f_latex, point_size=13)
            right = MathLabel(self.palette_obj, pair.F_latex, point_size=13)
            grid.addWidget(left, index, 0)
            grid.addWidget(right, index, 1)
            widgets = [left, right]
            if pair.note:
                note = QLabel(pair.note)
                note.setProperty("role", "muted")
                note.setWordWrap(True)
                grid.addWidget(note, index, 2)
                widgets.append(note)
            self._rows[pair.key] = widgets
        grid.setRowStretch(len(laplace.TABLE) + 1, 1)

        outer.addWidget(scroll, 1)
        return frame

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

    def _on_submitted(self, spec) -> None:
        from ..symbolic import parse_equation

        try:
            parsed = parse_equation(spec, extra_functions=laplace.EXTRA_FUNCTIONS)
        except Exception as exc:
            self.editor.show_message(str(exc), kind="error")
            self.steps.clear(str(exc))
            return

        self._highlight(set())
        self.steps.clear("transforming…")
        self._token += 1
        QThreadPool.globalInstance().start(
            _LaplaceJob(self._token, parsed, self._signals)
        )

    def _on_failed(self, message: str) -> None:
        self.steps.clear(message or "Type an equation to see it transformed.")
        self._highlight(set())

    def _on_done(self, token: int, result) -> None:
        if token != self._token:
            return                                # superseded
        if isinstance(result, Exception):
            self.steps.clear(f"{type(result).__name__}: {result}")
            return

        derivation = getattr(result, "derivation", None)
        if derivation is None or not derivation.steps:
            message = getattr(result, "message", "") or (
                derivation.message if derivation else ""
            )
            self.steps.clear(message or "the transform could not be taken")
            self._highlight(set())
            return

        self.steps.show_derivation(derivation)
        self._highlight(laplace.pairs_used(derivation.result))

    def _highlight(self, keys: set[str]) -> None:
        """Mark the rows this answer needed, and dim the rest."""
        palette = self.palette_obj
        for key, widgets in self._rows.items():
            used = key in keys
            for widget in widgets:
                if isinstance(widget, MathLabel):
                    widget.set_palette_colours(
                        palette, colour=palette.text if used else palette.text_muted
                    )
                else:
                    widget.setStyleSheet(
                        f"color: {palette.text if used else palette.text_muted};"
                    )

    def set_palette_colours(self, palette: Palette) -> None:
        self.palette_obj = palette
        self.steps.set_palette_colours(palette)
