"""The derivation, numbered and typeset.

One card per move: what it is, the mathematics, and why it is allowed. The
mathematics is `MathLabel` like everywhere else in the application, so it is set
in Computer Modern and falls back to monospace rather than to a blank rectangle.

The marks in the corner of each card are the point. `steps` does not merely
print a derivation -- it differentiates the antiderivatives back, substitutes
each basis function into the equation, and checks the particular solution
reproduces the forcing term. A card that carries a tick has had its claim
checked; a card with nothing is a rewriting with nothing to check. A card that
*fails* its check is shown failing rather than hidden, because a derivation that
quietly prints a wrong line is the one thing worse than no derivation at all.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..theme import Palette
from .mathlabel import MathLabel

__all__ = ["StepsPanel"]


class StepsPanel(QWidget):
    """Renders a `steps.Derivation`, or says plainly why there is not one."""

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        outer.addWidget(scroll)

        page = QWidget()
        scroll.setWidget(page)
        self._layout = QVBoxLayout(page)
        self._layout.setContentsMargins(18, 16, 18, 18)
        self._layout.setSpacing(12)

        self._heading = QLabel("")
        self._heading.setProperty("role", "heading")
        self._heading.setWordWrap(True)
        self._layout.addWidget(self._heading)

        self._status = QLabel("Type an equation to see how it is solved.")
        self._status.setProperty("role", "muted")
        self._status.setWordWrap(True)
        self._layout.addWidget(self._status)

        self._body = QVBoxLayout()
        self._body.setSpacing(12)
        self._layout.addLayout(self._body)
        self._layout.addStretch(1)

    # -- rendering -------------------------------------------------------

    def clear(self, message: str = "") -> None:
        self._clear_body()
        self._heading.setText("")
        self._heading.setVisible(False)
        self._status.setVisible(True)
        self._status.setText(message or "Type an equation to see how it is solved.")

    def show_derivation(self, derivation) -> None:
        """Render `derivation`, or explain its absence if it is None."""
        self._clear_body()
        if derivation is None:
            self.clear(
                "This equation is not solved by one of the techniques a first "
                "course covers — separation of variables, integrating factors, "
                "characteristic roots, undetermined coefficients or "
                "Cauchy–Euler. The closed form beside this is still checked by "
                "substitution."
            )
            return

        self._heading.setVisible(True)
        self._heading.setText(derivation.title)
        self._status.setVisible(bool(derivation.message))
        self._status.setText(derivation.message)

        for number, step in enumerate(derivation.steps, start=1):
            self._body.addWidget(self._card(number, step))
        if derivation.verified is not None:
            self._body.addWidget(self._verdict(derivation))

    def _card(self, number: int, step) -> QWidget:
        palette = self.palette_obj
        frame = QFrame()
        frame.setProperty("role", "panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(14, 11, 14, 12)
        layout.setSpacing(7)

        header = QHBoxLayout()
        header.setSpacing(8)
        title = QLabel(f"{number}.  {step.title}")
        title.setProperty("role", "heading")
        title.setWordWrap(True)
        header.addWidget(title, 1)
        header.addWidget(self._mark(step.verified))
        layout.addLayout(header)

        layout.addWidget(MathLabel(palette, step.latex, point_size=15))

        if step.note:
            note = QLabel(step.note)
            note.setProperty("role", "muted")
            note.setWordWrap(True)
            layout.addWidget(note)
        return frame

    def _mark(self, verified) -> QLabel:
        """The tick, cross or blank, with what it means on hover."""
        palette = self.palette_obj
        if verified is True:
            text, colour, tip = "✓", palette.success, (
                "checked: this step was verified symbolically"
            )
        elif verified is False:
            text, colour, tip = "✗", palette.danger, (
                "this step did not verify — treat it with suspicion"
            )
        else:
            text, colour, tip = "", palette.text_muted, (
                "a rewriting: there is nothing here to check"
            )
        label = QLabel(text)
        label.setStyleSheet(f"color: {colour}; font-size: 15px;")
        label.setToolTip(tip)
        return label

    def _verdict(self, derivation) -> QWidget:
        """Whether the derivation's own answer satisfies the equation.

        The wording must not name a check that was not the one performed. Most
        answers here are decided by substituting them back; a switched answer
        cannot be — differentiating a Heaviside leaves impulse terms that never
        cancel — and is decided against the numeric solver instead.
        `Derivation.check` records which route ran, because claiming
        "simplified to zero" for the other one would be the panel asserting
        something it did not do.
        """
        palette = self.palette_obj
        substituted = getattr(derivation, "check", "") != "numeric"
        if derivation.verified:
            colour = palette.success
            text = ("✓ The answer above satisfies the equation exactly — "
                    "substituted back and simplified to zero."
                    if substituted else
                    "✓ The answer above agrees with this project's own solver, "
                    "which is what decides it here.")
        else:
            colour = palette.danger
            text = ("✗ The answer above does not satisfy the equation. "
                    "Treat it with suspicion.")
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {colour};")
        return label

    def _clear_body(self) -> None:
        while self._body.count():
            item = self._body.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def set_palette_colours(self, palette: Palette) -> None:
        self.palette_obj = palette
