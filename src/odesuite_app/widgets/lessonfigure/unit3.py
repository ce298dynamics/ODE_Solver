"""Figures for Second-order linear equations."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt

from .base import LessonFigure

# ---------------------------------------------------------------------------
# Undetermined coefficients: which half of the answer the constants own
# ---------------------------------------------------------------------------


class ForcedStructureFigure(LessonFigure):
    """``y″ + 2c·y′ + y = cos(Ω t)``, drawn as its two structural halves.

    The derivation's first two passages say the general answer is one
    particular solution plus the homogeneous family, and that the constants
    live in the *homogeneous* part. Both are sliders here. Moving them moves
    the dashed curve and leaves the dotted one exactly where it was, which is
    that claim made visible -- and after a while only the dotted one is left,
    whatever the constants were.
    """

    title = "One particular solution, plus the family"
    caption = ("Dotted: a particular solution, the response to the forcing. "
               "Dashed: the homogeneous part, which is where the two "
               "constants live. Solid: their sum, the answer. Move c₁ or c₂ "
               "and only the dashed curve responds — and with any damping at "
               "all it dies, leaving the dotted one.")

    _TLIM = (0.0, 24.0)

    def build_sliders(self) -> None:
        self.add_slider("c", "damping", 0.0, 0.6, 0.12,
                        hint="Zero leaves the homogeneous part ringing "
                             "forever, so both halves survive. Anything "
                             "positive and only the response to the forcing "
                             "is left.")
        self.add_slider("W", "Ω  (driving frequency)", 0.2, 2.2, 0.7)
        self.add_slider("c1", "c₁", -2.0, 2.0, 1.0)
        self.add_slider("c2", "c₂", -2.0, 2.0, 0.5)

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        damping, omega = self.value("c"), self.value("W")
        c1, c2 = self.value("c1"), self.value("c2")
        t = np.linspace(*self._TLIM, 1200)

        # The particular solution of y" + 2c y' + y = cos(W t), by undetermined
        # coefficients: the trial form is a cosine and a sine, and matching
        # coefficients gives these two.
        gap = 1.0 - omega * omega
        drag = 2.0 * damping * omega
        size = gap * gap + drag * drag
        particular = (gap * np.cos(omega * t) + drag * np.sin(omega * t)) / size

        # The homogeneous part, from the characteristic roots.
        if damping < 1.0:
            rung = np.sqrt(1.0 - damping * damping)
            homogeneous = np.exp(-damping * t) * (
                c1 * np.cos(rung * t) + c2 * np.sin(rung * t)
            )
        else:                                     # not reachable from the
            root = np.sqrt(damping * damping - 1.0)   # slider, but harmless
            homogeneous = (c1 * np.exp((-damping + root) * t)
                           + c2 * np.exp((-damping - root) * t))

        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        self.plot.plot(t, particular,
                       pen=pg.mkPen(self.colour(2), width=2, style=Qt.DotLine))
        self.plot.plot(t, homogeneous,
                       pen=pg.mkPen(self.colour(1), width=2,
                                    style=Qt.DashLine))
        self.plot.plot(t, particular + homogeneous,
                       pen=pg.mkPen(self.colour(0), width=3))
        self._describe(damping, omega, size)

    def _describe(self, damping: float, omega: float, size: float) -> None:
        amplitude = 1.0 / np.sqrt(size)
        if damping <= 1e-9:
            note = ("nothing removes energy, so the homogeneous part never "
                    "decays and both halves are here forever")
        else:
            note = (f"the homogeneous part is under 5% of itself by "
                    f"t ≈ {3 / damping:.0f}, after which the answer *is* the "
                    "dotted curve")
        self.readout.setText(
            f"driving at Ω = {omega:.2f} against a natural frequency of 1: "
            f"steady amplitude {amplitude:.3f}. {note}."
        )


# ---------------------------------------------------------------------------
# Cauchy-Euler: powers, and what happens at the origin
# ---------------------------------------------------------------------------


class PowersFigure(LessonFigure):
    """``t^r`` and ``t^r·ln t``, and why the origin is excluded.

    Two things the lesson asserts are visible here at once. A power is the
    shape a scale-invariant equation admits, and its exponent decides
    everything about the origin -- negative and it runs away, positive and it
    arrives flat. And the second solution at a repeated root carries a
    logarithm rather than a factor of t, which is what the substitution
    t = e^s turns the constant-coefficient answer into.
    """

    title = "t to a power, and the logarithm that joins it"
    caption = ("Solid: t^r. Dashed: t^r·ln t, the second solution when the "
               "indicial root repeats. Slide r through zero and watch the "
               "behaviour at the origin change completely — which is why the "
               "answer is only claimed on one side of it.")

    _TLIM = (0.02, 4.0)

    def build_sliders(self) -> None:
        self.add_slider("r", "r  (indicial root)", -2.0, 2.5, 0.5,
                        hint="The root of a·r(r−1) + b·r + c. Negative and "
                             "the solution is unbounded at the origin; "
                             "positive and it reaches it.")

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        r = self.value("r")
        t = np.linspace(*self._TLIM, 900)
        power = t ** r
        logged = power * np.log(t)

        self.plot.addLine(x=0, pen=pg.mkPen(self.palette_obj.warning, width=2,
                                            style=Qt.DashLine))
        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        self.plot.plot(t, power, pen=pg.mkPen(self.colour(0), width=3))
        self.plot.plot(t, logged,
                       pen=pg.mkPen(self.colour(1), width=2,
                                    style=Qt.DashLine))
        self.plot.setXRange(-0.35, self._TLIM[1], padding=0.02)
        # From the curves rather than fixed: a small r leaves most of a fixed
        # window empty, and a negative one runs off the top of it.
        seen = np.concatenate([power, logged])
        seen = seen[np.isfinite(seen)]
        high = float(np.clip(np.max(seen), 2.0, 9.0))
        low = float(np.clip(np.min(seen), -9.0, -0.5))
        self.plot.setYRange(low - 0.4, high + 0.4, padding=0.02)
        self._describe(r)

    def _describe(self, r: float) -> None:
        if r < -1e-9:
            near = "runs off to infinity at the origin"
        elif r < 1e-9:
            near = "is the constant 1, and its partner is ln t, which does not"
        elif r < 1:
            near = "reaches zero at the origin, but with an infinite slope"
        else:
            near = "reaches zero at the origin, flat"
        self.readout.setText(
            f"r = {r:.2f}: t^r {near}. Neither solution is defined at t = 0 "
            "in any case — that is where the equation loses its leading "
            "coefficient, so the answer is claimed on one side only."
        )
