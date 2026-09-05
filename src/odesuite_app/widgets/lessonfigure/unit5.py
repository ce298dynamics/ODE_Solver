"""Figures for Laplace transforms."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt

from odesuite import ODEProblem, solve

from .base import LessonFigure

# ---------------------------------------------------------------------------
# Shifting: a translation in s is a decay in t
# ---------------------------------------------------------------------------


class PolesFigure(LessonFigure):
    """The poles in the s-plane beside the response they produce.

    The first shifting theorem says multiplying by an exponential in t moves
    the transform along the s axis. Two panes make that one statement: drag
    the shift and the pair of poles slides left while the response acquires an
    envelope, at exactly the rate the poles moved. The imaginary part is the
    frequency and the real part is the decay -- which is the second-order
    unit's characteristic root, seen from the other side.
    """

    title = "Poles on the left, response on the right"
    caption = ("1/((s + a)² + b²) and the function it inverts to. The crosses "
               "are the poles at −a ± b·i. Slide a and both move: the poles "
               "travel left, and the response gains an envelope decaying at "
               "that same rate. Slide b and only the oscillation changes.")

    plots = 2
    _TLIM = (0.0, 12.0)

    def build_sliders(self) -> None:
        self.add_slider("a", "a  (the shift in s)", 0.0, 1.5, 0.4,
                        hint="How far the transform is translated along the "
                             "s axis — which is the decay rate in t. At zero "
                             "the poles sit on the imaginary axis and nothing "
                             "decays.")
        self.add_slider("b", "b  (the frequency)", 0.4, 4.0, 2.0)

    def draw(self) -> None:
        a, b = self.value("a"), self.value("b")

        poles, response = self.panes
        poles.clear()
        poles.setLabel("bottom", "Re s")
        poles.setLabel("left", "Im s")
        poles.addLine(x=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        poles.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        poles.plot(
            [-a, -a], [b, -b], pen=None, symbol="x", symbolSize=14,
            symbolPen=pg.mkPen(self.colour(0), width=3),
        )
        poles.setXRange(-1.8, 0.6, padding=0.02)
        poles.setYRange(-4.4, 4.4, padding=0.02)

        response.clear()
        response.setLabel("bottom", "t")
        response.setLabel("left", "y")
        t = np.linspace(*self._TLIM, 1100)
        envelope = np.exp(-a * t)
        response.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        for sign in (1, -1):
            response.plot(t, sign * envelope / b,
                          pen=pg.mkPen(self.palette_obj.text_muted, width=1,
                                       style=Qt.DashLine))
        response.plot(t, envelope * np.sin(b * t) / b,
                      pen=pg.mkPen(self.colour(0), width=3))
        response.setYRange(-1.35 / b, 1.35 / b, padding=0.02)

        settled = ("nothing decays: the poles are on the axis and this rings "
                   "forever" if a <= 1e-9 else
                   f"under 5% of its envelope by t ≈ {3 / a:.1f}")
        self.readout.setText(
            f"poles at −{a:.2f} ± {b:.2f}i  ·  e^(−{a:.2f}t)·sin({b:.2f}t)"
            f"/{b:.2f}  —  {settled}"
        )


# ---------------------------------------------------------------------------
# Convolution: the sliding flip, with t on a slider
# ---------------------------------------------------------------------------


class ConvolutionFigure(LessonFigure):
    """One function held still, the other reversed and slid across it.

    The derivation ends with an integral in which one function runs forwards
    while the other runs backwards, their arguments always summing to the
    current time. That sentence is what this draws. The left pane holds f
    fixed and slides the reversed g across it, shading where they overlap; the
    right pane plots the area of that shading against t, which *is* the
    convolution. Dragging t is the animation.
    """

    title = "The sliding flip, and the area it sweeps"
    caption = ("Left: f(τ) — a pulse — held still, with g(t − τ) reversed and "
               "slid across it. The shading is where they overlap, and its "
               "area is the convolution at that t. Right: that area, plotted "
               "against t. Drag t and watch the point trace the curve.")

    plots = 2
    _TAU = (-1.0, 8.0)

    def build_sliders(self) -> None:
        self.add_slider("t", "t  (where the answer is wanted)", 0.0, 7.0, 2.0,
                        hint="The one variable the convolution integral is a "
                             "function of. Everything in the left pane moves "
                             "with it.")
        self.add_slider("a", "a  in  g(τ) = e^(−aτ)", 0.2, 2.0, 0.8)
        self.add_slider("w", "width of the pulse f", 0.5, 3.0, 1.5)

    def _f(self, tau):
        """A pulse on [0, w]: one inside, zero outside."""
        width = self.value("w")
        return np.where((tau >= 0.0) & (tau <= width), 1.0, 0.0)

    def _g(self, tau):
        a = self.value("a")
        return np.where(tau >= 0.0, np.exp(-a * tau), 0.0)

    def _convolution(self, t: float) -> float:
        """The overlap integral, by quadrature on a fine grid."""
        tau = np.linspace(0.0, max(t, 1e-9), 2001)
        return float(np.trapezoid(self._f(tau) * self._g(t - tau), tau))

    def draw(self) -> None:
        now = self.value("t")
        sliding, built = self.panes

        sliding.clear()
        sliding.setLabel("bottom", "τ")
        sliding.setLabel("left", "")
        tau = np.linspace(*self._TAU, 1400)
        held, reversed_ = self._f(tau), self._g(now - tau)

        sliding.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        sliding.plot(tau, held, pen=pg.mkPen(self.colour(0), width=2))
        sliding.plot(tau, reversed_, pen=pg.mkPen(self.colour(1), width=2))
        # `fillLevel` rather than a `FillBetweenItem`: one call instead of
        # three, and it fills against the axis rather than against a second
        # curve that has to be kept in step with the first.
        overlap = np.minimum(held, reversed_)
        sliding.plot(
            tau, overlap, fillLevel=0.0,
            pen=pg.mkPen(self.palette_obj.accent, width=1),
            brush=pg.mkBrush(self.palette_obj.accent + "99"),
        )
        sliding.addLine(x=now, pen=pg.mkPen(self.palette_obj.warning, width=1,
                                            style=Qt.DashLine))
        sliding.setYRange(-0.1, 1.3, padding=0.02)

        built.clear()
        built.setLabel("bottom", "t")
        built.setLabel("left", "(f * g)(t)")
        grid = np.linspace(0.0, 7.0, 160)
        values = np.array([self._convolution(point) for point in grid])
        built.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        built.plot(grid, values, pen=pg.mkPen(self.colour(2), width=3))
        here = self._convolution(now)
        built.plot([now], [here], pen=None, symbol="o", symbolSize=11,
                   symbolBrush=self.palette_obj.warning)

        self.readout.setText(
            f"(f * g)({now:.2f}) = {here:.4f} — the shaded area on the left. "
            "The two arguments always sum to t, which is why one runs "
            "backwards."
        )


# ---------------------------------------------------------------------------
# Step forcing: nothing happens until it does
# ---------------------------------------------------------------------------


class PulseResponseFigure(LessonFigure):
    """A pulse switched on and off, and what the system does about it.

    Two claims of the lesson are drawn at once. The answer is *identically*
    zero before the first switch, which is what the step factor in the
    inverted transform enforces -- and after the second switch, with nothing
    driving it, the system keeps whatever the pulse gave it. Take the damping
    to zero and it keeps it forever.
    """

    title = "A pulse, and the ringing it leaves behind"
    caption = ("Dashed: the forcing, one step minus a later one. Solid: the "
               "response of y″ + 2c·y′ + 4y. Before the first switch the "
               "answer is exactly zero — not small, zero. After the second "
               "the forcing is gone and whatever is left keeps going.")

    _TLIM = (0.0, 20.0)

    def build_sliders(self) -> None:
        self.add_slider("on", "on at", 0.5, 6.0, 2.0)
        self.add_slider("off", "off at", 1.0, 12.0, 5.0,
                        hint="Set this below the switch-on time and the "
                             "forcing is never applied, which the response "
                             "reports by staying flat.")
        self.add_slider("c", "damping", 0.0, 0.8, 0.1)

    def _problem(self) -> ODEProblem:
        on, off, damping = self.value("on"), self.value("off"), self.value("c")

        def field(t, y):
            drive = 1.0 if on <= t < off else 0.0
            return np.array([y[1], drive - 4.0 * y[0] - 2.0 * damping * y[1]])

        return ODEProblem(f=field, t_span=self._TLIM, y0=np.array([0.0, 0.0]))

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        on, off = self.value("on"), self.value("off")
        try:
            found = solve(self._problem(), method="dopri5",
                          rtol=1e-8, atol=1e-10, max_step=0.02)
        except Exception:
            self.readout.setText("that pulse could not be integrated")
            return

        t = np.linspace(*self._TLIM, 1200)
        forcing = np.where((t >= on) & (t < off), 1.0, 0.0)
        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        self.plot.plot(t, 0.25 * forcing,
                       pen=pg.mkPen(self.palette_obj.text_muted, width=2,
                                    style=Qt.DashLine))
        self.plot.plot(found.t, found.y[0],
                       pen=pg.mkPen(self.colour(0), width=3))
        for switch in (on, off):
            self.plot.addLine(x=switch,
                              pen=pg.mkPen(self.palette_obj.warning, width=1,
                                           style=Qt.DotLine))
        self._describe(found, on, off)

    def _describe(self, found, on: float, off: float) -> None:
        if off <= on:
            self.readout.setText(
                "the pulse is switched off before it is switched on, so "
                "nothing ever drives the system and the answer stays zero"
            )
            return
        before = float(np.max(np.abs(found.y[0][found.t < on])))
        after = float(np.max(np.abs(found.y[0][found.t > off])))
        damping = self.value("c")
        keeps = ("rings on forever — nothing removes the energy the pulse put "
                 "in" if damping <= 1e-9 else
                 f"rings and dies, at a rate {damping:.2f}")
        self.readout.setText(
            f"largest value before t = {on:.1f}: {before:.2e} — zero to the "
            f"solver's precision.  After t = {off:.1f} it reaches {after:.3f} "
            f"and {keeps}."
        )
