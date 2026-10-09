"""Figures for Laplace transforms."""

from __future__ import annotations

import math

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


# ---------------------------------------------------------------------------
# The transform itself: an integral, and where it stops converging
# ---------------------------------------------------------------------------


class TransformFigure(LessonFigure):
    """``F(s) = integral of e^(-s t) f(t)``, drawn as the area it actually is.

    The transform is introduced as a formula and then used as a lookup table,
    and the step between those two is where it stops being understood. This
    figure keeps the integral in view: the shaded region *is* F(s), the slider
    is s, and pushing s up visibly flattens the integrand and shrinks the area
    -- which is the whole of why F(s) decays.

    The condition for existence falls out of the same picture rather than
    being announced. With f(t) = e^(a t), the integrand is e^((a - s) t); at
    s = a it is the constant 1 and the area under it is infinite. The right
    pane draws F(s) = 1/(s - a) with its asymptote at exactly that s, so the
    "region of convergence" is a place on the axis, not a proviso in small
    print.
    """

    title = "The transform is an area, and it can be infinite"
    caption = ("Left: f(t) = e^(at), the decaying weight e^(−st), and their "
               "product — whose area is F(s). Right: F(s) = 1/(s − a). Slide "
               "s down towards a and watch the shaded area stop being finite "
               "at the moment the curve on the right runs off.")
    plots = 2

    _TLIM = (0.0, 6.0)
    _SLIM = (-1.0, 4.0)

    def build_sliders(self) -> None:
        self.add_slider("a", "a  in  f(t) = e^(at)", -1.0, 1.5, 0.5)
        self.add_slider("s", "s", -0.5, 3.5, 2.0,
                        hint="The transform variable. Everything the "
                             "transform can say about f needs s > a; at or "
                             "below it the integral does not converge.")

    def draw(self) -> None:
        a, s = self.value("a"), self.value("s")
        self._draw_integrand(a, s)
        self._draw_transform(a, s)
        self._describe(a, s)

    def _draw_integrand(self, a: float, s: float) -> None:
        pane = self.panes[0]
        pane.clear()
        pane.setLabel("bottom", "t")
        pane.setLabel("left", "value")
        t = np.linspace(*self._TLIM, 900)

        pane.plot(t, np.exp(a * t), pen=pg.mkPen(self.colour(1), width=2,
                                                 style=Qt.DashLine))
        pane.plot(t, np.exp(-s * t), pen=pg.mkPen(self.colour(2), width=2,
                                                  style=Qt.DotLine))
        # The product, shaded down to the axis: the area under it is F(s), so
        # the area is what the eye should be given.
        product = np.exp((a - s) * t)
        pane.plot(t, product, pen=pg.mkPen(self.colour(0), width=3),
                  fillLevel=0.0,
                  brush=pg.mkBrush(self.palette_obj.accent_soft))
        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.setYRange(0.0, 4.0, padding=0.02)

    def _draw_transform(self, a: float, s: float) -> None:
        pane = self.panes[1]
        pane.clear()
        pane.setLabel("bottom", "s")
        pane.setLabel("left", "F(s)")
        grid = np.linspace(*self._SLIM, 1200)
        # Either side of the pole, never through it: joining the two branches
        # would draw a vertical line that is not part of the function.
        for piece in (grid[grid < a - 0.02], grid[grid > a + 0.02]):
            if piece.size:
                pane.plot(piece, 1.0 / (piece - a),
                          pen=pg.mkPen(self.colour(0), width=3))
        pane.addLine(x=a, pen=pg.mkPen(self.palette_obj.warning, width=2,
                                       style=Qt.DashLine))
        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        if s > a:
            pane.plot([s], [1.0 / (s - a)], pen=None, symbol="o",
                      symbolSize=11, symbolBrush=self.colour(0))
        pane.setYRange(-8.0, 8.0, padding=0.02)

    def _describe(self, a: float, s: float) -> None:
        if s <= a + 1e-9:
            self.readout.setText(
                f"s = {s:.2f} is not above a = {a:.2f}, so e^((a − s)t) does "
                "not decay and the area is infinite. F(s) does not exist "
                "here, which is what the dashed line marks."
            )
            return
        # The area measured off the drawn samples, against the closed form.
        # The window is finite, so the two differ by the tail -- which is
        # itself worth printing, because it is the part the picture cannot
        # show and the formula quietly includes.
        t = np.linspace(*self._TLIM, 4000)
        # The trapezium rule written out: `np.trapz` is deprecated in numpy 2
        # and `np.trapezoid` does not exist in numpy 1, and this figure is not
        # worth a version check.
        heights = np.exp((a - s) * t)
        drawn = float(np.sum((heights[:-1] + heights[1:]) / 2.0 * np.diff(t)))
        exact = 1.0 / (s - a)
        self.readout.setText(
            f"a = {a:.2f}, s = {s:.2f}: the shaded area out to "
            f"t = {self._TLIM[1]:.0f} is {drawn:.4f}, and the whole integral "
            f"is 1/(s − a) = {exact:.4f}. The missing {exact - drawn:.4f} is "
            "the tail off the right of the pane, which is why the transform "
            "needs the integral to converge."
        )


# ---------------------------------------------------------------------------
# Solving with it: one pole, one term of the answer
# ---------------------------------------------------------------------------


class PartialFractionFigure(LessonFigure):
    """``y" + 3y' + 2y = sin t``, rebuilt one partial fraction at a time.

    The middle of the Laplace method is the step people find least motivated:
    Y(s) is split into partial fractions, and each piece is looked up
    separately. Why that is the natural thing to do is a fact about the
    answer, not about the algebra -- each pole of Y(s) contributes exactly one
    term of y(t), and the terms are the behaviours a reader already knows how
    to name.

    So the slider adds the terms back one at a time, in order of the poles
    they come from, against the true solution. Two exponentials arrive first
    and fix the start; the sinusoid arrives last and fixes everything after
    the transient. Nothing here is a truncation -- with all four terms the
    curves coincide exactly, which the readout measures.

    Worked out by hand and written in, because it is a lesson about a
    particular equation: Y(s) has poles at -1, -2 and +-i, and
    y = 2.5e^(-t) - 1.2e^(-2t) - 0.3cos t + 0.1 sin t.
    """

    title = "One pole, one term: the answer assembled"
    caption = ("y″ + 3y′ + 2y = sin t with y(0) = 1, y′(0) = 0. Y(s) has "
               "four poles and the answer has four terms, one from each. Add "
               "them back in and watch the curve arrive — the exponentials "
               "fix the transient, the sinusoid fixes the rest.")

    _TLIM = (0.0, 12.0)
    #: ``(pole, coefficient, kind)`` in the order the terms are added. The
    #: order is the poles' own -- the two real ones, then the imaginary pair,
    #: which is also the order a partial-fraction decomposition produces them.
    _TERMS = (
        ("s = −1", 2.5, "exp-1"),
        ("s = −2", -1.2, "exp-2"),
        ("s = ±i (cos)", -0.3, "cos"),
        ("s = ±i (sin)", 0.1, "sin"),
    )

    def build_sliders(self) -> None:
        self.add_slider("n", "terms put back", 0, len(self._TERMS),
                        len(self._TERMS),
                        hint="Each step adds the contribution of one pole. "
                             "At the last one the two curves are the same "
                             "curve, not an approximation of it.")

    def _pieces(self, t: np.ndarray):
        return {
            "exp-1": np.exp(-t),
            "exp-2": np.exp(-2.0 * t),
            "cos": np.cos(t),
            "sin": np.sin(t),
        }

    def _partial(self, t: np.ndarray, count: int) -> np.ndarray:
        pieces = self._pieces(t)
        total = np.zeros_like(t)
        for _, weight, kind in self._TERMS[:count]:
            total = total + weight * pieces[kind]
        return total

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        t = np.linspace(*self._TLIM, 1400)
        count = int(round(self.value("n")))
        exact = self._partial(t, len(self._TERMS))

        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        self.plot.plot(t, exact, pen=pg.mkPen(self.palette_obj.text_muted,
                                              width=2, style=Qt.DotLine))
        for index in range(count):
            _, weight, kind = self._TERMS[index]
            self.plot.plot(t, weight * self._pieces(t)[kind],
                           pen=pg.mkPen(self.colour(index + 1), width=1,
                                        style=Qt.DashLine))
        self.plot.plot(t, self._partial(t, count),
                       pen=pg.mkPen(self.colour(0), width=3))
        self.plot.setYRange(-1.6, 1.6, padding=0.02)
        self._describe(t, count, exact)

    def _describe(self, t: np.ndarray, count: int, exact: np.ndarray) -> None:
        gap = float(np.max(np.abs(self._partial(t, count) - exact)))
        if count == 0:
            self.readout.setText(
                "no terms yet. Y(s) has been written down and nothing has "
                "been inverted, which is the state the method is in halfway "
                "through."
            )
            return
        named = ", ".join(name for name, _, _ in self._TERMS[:count])
        if count == len(self._TERMS):
            self.readout.setText(
                f"all four poles ({named}): the two curves differ by "
                f"{gap:.1e}, which is nothing. The answer is finished, not "
                "approximated — a transform has no truncation error."
            )
            return
        self.readout.setText(
            f"poles {named}: still {gap:.3f} away from the answer at worst. "
            "The terms not yet added are the behaviours their poles name, "
            "and nothing else is missing."
        )


# ---------------------------------------------------------------------------
# Impulses: what a delta is the limit of
# ---------------------------------------------------------------------------


class ImpulseLimitFigure(LessonFigure):
    """A narrowing pulse of unit area, and the response converging on it.

    A delta is usually introduced by saying what it does rather than what it
    is, because what it is cannot be drawn. What *can* be drawn is the
    sequence it is the limit of -- a rectangle of width w and height 1/w,
    whose area is 1 however narrow it gets -- and the response to it, which
    converges on the delta response long before the pulse looks like anything
    in particular.

    That convergence is the content, and it is fast: measured here, a pulse
    of width 0.5 already matches the impulse response to 1.05% of its peak,
    and one of width 0.2 to 0.17% -- second order in w, which is what
    centring the pulse buys. That is the honest reason an impulse model is used for a hammer
    blow -- not that the blow is instantaneous, but that the response cannot
    tell.

    The pulse response is integrated by the library's own solver; the delta
    response is the closed form the lesson derives, so the two come from
    genuinely different routes and agreeing means something.
    """

    title = "The delta is a limit, and the response gets there first"
    caption = ("Left: a rectangle of width w and height 1/w — area 1 "
               "whatever w is. Right: the response of y″ + 2c·y′ + y to it, "
               "against the response to a true impulse at the same instant. "
               "Narrow the pulse and the two curves merge.")
    plots = 2

    _T_END = 22.0
    _AT = 3.0

    def build_sliders(self) -> None:
        self.add_slider("w", "w  (pulse width)", 0.05, 3.0, 1.0, log=True,
                        hint="Height is 1/w, so the area is always 1. "
                             "Logarithmic, because the interesting part is "
                             "the last factor of ten.")
        self.add_slider("c", "c  (damping)", 0.0, 0.4, 0.08)

    def _delta_response(self, t: np.ndarray, damping: float) -> np.ndarray:
        """``sin(beta (t - a)) e^(-c(t - a))/beta`` after the impulse, 0 before.

        The closed form the lesson derives from the transform: an impulse at
        t = a leaves the solution at rest until a and moving with unit
        velocity after it.
        """
        beta = math.sqrt(max(1.0 - damping * damping, 1e-12))
        shifted = t - self._AT
        after = np.where(shifted > 0.0, shifted, 0.0)
        response = np.exp(-damping * after) * np.sin(beta * after) / beta
        return np.where(shifted > 0.0, response, 0.0)

    def _pulse_response(self, width: float, damping: float):
        """The same equation forced by the rectangle, integrated numerically.

        The rectangle is *centred* on the instant of the impulse rather than
        starting at it. Both sequences converge on the delta, but a pulse that
        starts there also arrives half a width late, and that offset is first
        order in w -- it dominates the difference and makes the convergence
        look far slower than it is. Centred, what is left is the second-order
        part, which is what the limit is really about.
        """
        height = 1.0 / width
        start, stop = self._AT - width / 2.0, self._AT + width / 2.0

        def field(t, y):
            force = height if start <= t <= stop else 0.0
            return np.array([y[1], force - 2.0 * damping * y[1] - y[0]])

        problem = ODEProblem(f=field, t_span=(0.0, self._T_END),
                             y0=np.zeros(2))
        # Small steps through the corners of the rectangle: an adaptive solver
        # can step clean over a narrow pulse and never see it, which would
        # make this figure claim the response to an impulse is nothing.
        found = solve(problem, method="dopri5", rtol=1e-9, atol=1e-11,
                      max_step=width / 8.0)
        return found.t, found.y[0]

    def draw(self) -> None:
        width, damping = self.value("w"), self.value("c")
        self._draw_pulse(width)
        self._draw_responses(width, damping)

    def _draw_pulse(self, width: float) -> None:
        pane = self.panes[0]
        pane.clear()
        pane.setLabel("bottom", "t")
        pane.setLabel("left", "forcing")
        height = 1.0 / width
        start, stop = self._AT - width / 2.0, self._AT + width / 2.0
        edges = np.array([0.0, start, start, stop, stop, self._T_END])
        values = np.array([0.0, 0.0, height, height, 0.0, 0.0])
        pane.plot(edges, values, pen=pg.mkPen(self.colour(0), width=3),
                  fillLevel=0.0,
                  brush=pg.mkBrush(self.palette_obj.accent_soft))
        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.setXRange(0.0, 10.0, padding=0.02)
        pane.setYRange(0.0, max(2.5, min(height * 1.2, 22.0)), padding=0.02)

    def _draw_responses(self, width: float, damping: float) -> None:
        pane = self.panes[1]
        pane.clear()
        pane.setLabel("bottom", "t")
        pane.setLabel("left", "y")
        times, values = self._pulse_response(width, damping)
        ideal = self._delta_response(times, damping)

        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.plot(times, ideal, pen=pg.mkPen(self.palette_obj.text_muted,
                                             width=2, style=Qt.DotLine))
        pane.plot(times, values, pen=pg.mkPen(self.colour(0), width=3))
        pane.setYRange(-1.2, 1.2, padding=0.02)
        self._describe(width, times, values, ideal)

    def _describe(self, width, times, values, ideal) -> None:
        after = times > self._AT + width / 2.0
        gap = float(np.max(np.abs(values[after] - ideal[after]))) if after.any() \
            else 0.0
        peak = float(np.max(np.abs(ideal))) or 1.0
        self.readout.setText(
            f"pulse of width {width:.3f} and height {1 / width:.2f}, so its "
            f"area is 1. After it has passed, the two responses differ by at "
            f"most {gap:.4f} — {100 * gap / peak:.2f}% of the peak. The delta "
            "is not a function; the response to it is the limit of responses "
            "to these."
        )
