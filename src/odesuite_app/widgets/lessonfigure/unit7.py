"""Figures for Series solutions."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt

from .base import LessonFigure

# ---------------------------------------------------------------------------
# Power series: how many terms, and how far they are good for
# ---------------------------------------------------------------------------


class PartialSumsFigure(LessonFigure):
    """Partial sums of a series solution, against the answer and the radius.

    Two of the lesson's claims are hard to believe from prose and obvious
    here. Truncating is a *choice* -- add terms and the partial sum hugs the
    true curve further out, with the series itself never in error. And the
    radius of convergence is real: past the marked line no number of terms
    helps at all, because the coefficient of y′ vanishes there and the
    equation has nothing to say.

    The equation is (1 − t)·y′ = y with y(0) = 1, whose recurrence gives
    a_{n+1} = a_n and so the series 1 + t + t² + …, and whose closed form is
    1/(1 − t). Everything on the screen can therefore be checked by hand.
    """

    title = "Partial sums, and where they stop being any use"
    caption = ("(1 − t)·y′ = y with y(0) = 1. Every coefficient equals the "
               "one before it, so the series is 1 + t + t² + … and the answer "
               "is 1/(1 − t). Add terms and the partial sum follows the curve "
               "further — but never past the dashed line, which is where the "
               "leading coefficient vanishes.")

    _TLIM = (-1.25, 1.25)
    _RADIUS = 1.0

    def build_sliders(self) -> None:
        self.add_slider("n", "terms kept", 1, 24, 5,
                        hint="How far the sum is truncated. The series is "
                             "not an approximation; a truncation of it is.")

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        terms = int(round(self.value("n")))
        t = np.linspace(*self._TLIM, 1400)

        # The exact solution, drawn either side of its own singularity so the
        # two branches are not joined by a spurious vertical line.
        for piece in (t[t < self._RADIUS - 0.02], t[t > self._RADIUS + 0.02]):
            if piece.size:
                self.plot.plot(piece, 1.0 / (1.0 - piece),
                               pen=pg.mkPen(self.palette_obj.text_muted,
                                            width=2, style=Qt.DotLine))

        # Every coefficient is 1, which is the recurrence this equation gives.
        partial = np.zeros_like(t)
        for power in range(terms):
            partial = partial + t ** power
        self.plot.plot(t, partial, pen=pg.mkPen(self.colour(0), width=3))

        for edge in (-self._RADIUS, self._RADIUS):
            self.plot.addLine(x=edge,
                              pen=pg.mkPen(self.palette_obj.warning, width=2,
                                           style=Qt.DashLine))
        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        # Tall enough that the agreement near the origin is as visible as the
        # departure past the radius, which is the comparison being made.
        self.plot.setYRange(-2.0, 14.0, padding=0.02)
        self._describe(terms)

    def _describe(self, terms: int) -> None:
        # Where the truncation is still within a percent of the truth, found
        # by walking out from the origin rather than asserted.
        grid = np.linspace(0.0, 0.995, 800)
        partial = np.zeros_like(grid)
        for power in range(terms):
            partial = partial + grid ** power
        exact = 1.0 / (1.0 - grid)
        close = np.abs(partial - exact) <= 0.01 * np.abs(exact)
        reach = float(grid[close][-1]) if close.any() else 0.0
        self.readout.setText(
            f"{terms} term{'' if terms == 1 else 's'}: within 1% of the "
            f"answer out to t = {reach:.3f}. The radius is 1 whatever the "
            "number of terms — past it the series diverges and the equation "
            "loses its leading coefficient."
        )
