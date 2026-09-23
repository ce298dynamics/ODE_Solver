"""Figures for First-order equations."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt

from odesuite import ODEProblem, solve

from ... import analysis
from ...theme import Palette
from .base import LessonFigure

# ---------------------------------------------------------------------------
# Slope fields: the picture the equation draws before it is solved
# ---------------------------------------------------------------------------


class SlopeFieldFigure(LessonFigure):
    """``y' = a·y + b·t``, its slope field, and solutions threading it.

    Two things are on show, and the clicking is what carries the second. The
    dashes are the equation itself -- no solving involved, just the slope it
    demands at each point. Clicking drops an initial condition and integrates
    through it, and the curve comes out tangent to every dash it passes, which
    is the claim a slope field makes. Click again and the second curve never
    crosses the first: exactly one solution threads each point, which is what
    the uniqueness theorem says and is far easier to see than to state.
    """

    title = "The slope field, and solutions through it"
    caption = ("Each dash is the slope y′ = a·y + b·t demands at that point — "
               "no solving involved. Click anywhere to drop an initial "
               "condition and watch the solution thread the dashes. Two curves "
               "never cross: that is uniqueness.")

    _TLIM = (0.0, 4.0)
    _YLIM = (-3.0, 3.0)

    def __init__(self, palette: Palette, parent=None) -> None:
        #: Conditions dropped by clicking, oldest first.
        self._points: list[tuple[float, float]] = []
        super().__init__(palette, parent)
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")
        self.plot.setXRange(*self._TLIM, padding=0.02)
        self.plot.setYRange(*self._YLIM, padding=0.02)
        self.plot.scene().sigMouseClicked.connect(self._clicked)

    def build_sliders(self) -> None:
        self.add_slider("a", "a", -2.0, 2.0, -1.0,
                        hint="The coefficient of y. Negative pulls solutions "
                             "together, positive drives them apart.")
        self.add_slider("b", "b", -2.0, 2.0, 1.0,
                        hint="The coefficient of t, which tilts the field.")

    def _problem(self, y0: float = 0.0, t_span=None) -> ODEProblem:
        a, b = self.value("a"), self.value("b")
        return ODEProblem(
            f=lambda t, y: np.array([a * y[0] + b * t]),
            t_span=t_span or self._TLIM,
            y0=np.array([float(y0)]),
        )

    def _clicked(self, event) -> None:
        point = self.plot.plotItem.vb.mapSceneToView(event.scenePos())
        t, y = float(point.x()), float(point.y())
        if not (self._TLIM[0] <= t <= self._TLIM[1]
                and self._YLIM[0] <= y <= self._YLIM[1]):
            return
        # Six is enough to make the point and few enough that the field is
        # still visible underneath; past that the oldest goes.
        self._points.append((t, y))
        del self._points[:-6]
        self.redraw()

    def _curve_through(self, t0: float, y0: float):
        """The solution through ``(t0, y0)``, integrated both ways.

        Backwards as well as forwards, because half a curve through a dropped
        point looks like the point caused the solution rather than merely
        naming it.
        """
        pieces = []
        for horizon in (self._TLIM[1], self._TLIM[0]):
            if abs(horizon - t0) < 1e-9:
                continue
            problem = ODEProblem(
                f=self._problem().f_user,
                t_span=(t0, horizon),
                y0=np.array([y0]),
            )
            try:
                found = solve(problem, method="dopri5", rtol=1e-7, atol=1e-9)
            except Exception:
                continue
            if found.t.size:
                pieces.append((found.t, found.y[0]))
        if not pieces:
            return None
        # The backward leg comes out in descending time; flip it so the two
        # legs join into one left-to-right curve.
        parts = [(t[::-1], y[::-1]) if t[0] > t[-1] else (t, y)
                 for t, y in pieces]
        parts.sort(key=lambda piece: piece[0][0])
        return (np.concatenate([t for t, _ in parts]),
                np.concatenate([y for _, y in parts]))

    def draw(self) -> None:
        self.plot.clear()
        segments, _ = analysis.slope_field(
            self._problem(), self._TLIM, self._YLIM, resolution=19,
        )
        for segment in segments:
            self.plot.plot(segment[:, 0], segment[:, 1],
                           pen=pg.mkPen(self.palette_obj.text_muted, width=1))

        for index, (t0, y0) in enumerate(self._points):
            curve = self._curve_through(t0, y0)
            colour = self.colour(index)
            if curve is not None:
                self.plot.plot(curve[0], curve[1],
                               pen=pg.mkPen(colour, width=2))
            self.plot.plot([t0], [y0], pen=None, symbol="o", symbolSize=8,
                           symbolBrush=colour, symbolPen=colour)

        a, b = self.value("a"), self.value("b")
        self.readout.setText(
            f"y′ = {a:.2f}·y + {b:.2f}·t"
            + ("    —    click the plot to drop a condition"
               if not self._points else
               f"    —    {len(self._points)} condition"
               f"{'s' if len(self._points) > 1 else ''}, "
               f"{len(self._points)} solution"
               f"{'s' if len(self._points) > 1 else ''}, no crossings")
        )


# ---------------------------------------------------------------------------
# Separable: the family, and the two solutions the method divides away
# ---------------------------------------------------------------------------


class SeparableFigure(LessonFigure):
    """The logistic family, and the constant solutions separating discards.

    The lesson's sharpest point is that dividing by g(y) throws away every root
    of g, and that those roots are solutions in their own right. Said in a
    note it is a caveat; drawn, it is the two horizontal lines every other
    curve crowds up against and never touches.
    """

    title = "The whole family, and the two curves separating loses"
    caption = ("Solutions of y′ = r·y(1 − y) from a fan of starting values. "
               "The two dashed lines are the constant solutions y = 0 and "
               "y = 1 — the roots of g, which the separation divides by and "
               "so cannot produce. Nothing crosses them, which is why they "
               "have to be added back by hand.")

    _TLIM = (0.0, 8.0)
    _STARTS = (0.02, 0.08, 0.2, 0.4, 0.6, 0.8, 0.95, 1.15, 1.5, 2.0)

    def build_sliders(self) -> None:
        self.add_slider("r", "r  (growth rate)", 0.3, 3.0, 1.0,
                        hint="How fast the approach is. It changes the "
                             "steepness and nothing else: the two constant "
                             "solutions do not move.")
        self.add_slider("y0", "y(0)  (the highlighted curve)", 0.02, 2.0, 0.1)

    def _curve(self, y0: float):
        r = self.value("r")
        problem = ODEProblem(
            f=lambda t, y: np.array([r * y[0] * (1 - y[0])]),
            t_span=self._TLIM,
            y0=np.array([float(y0)]),
        )
        try:
            found = solve(problem, method="dopri5", rtol=1e-7, atol=1e-9)
        except Exception:
            return None
        return (found.t, found.y[0]) if found.t.size else None

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")
        self.plot.setYRange(-0.15, 2.1, padding=0.02)

        faint = pg.mkPen(self.palette_obj.text_muted, width=1)
        for start in self._STARTS:
            curve = self._curve(start)
            if curve is not None:
                self.plot.plot(curve[0], curve[1], pen=faint)

        for level in (0.0, 1.0):
            self.plot.addLine(
                y=level,
                pen=pg.mkPen(self.palette_obj.warning, width=2,
                             style=Qt.DashLine),
            )

        chosen = self._curve(self.value("y0"))
        if chosen is not None:
            self.plot.plot(chosen[0], chosen[1],
                           pen=pg.mkPen(self.colour(0), width=3))
        self._describe(chosen)

    def _describe(self, chosen) -> None:
        if chosen is None:
            self.readout.setText("that start runs away too fast to draw")
            return
        y0 = self.value("y0")
        ends = float(chosen[1][-1])
        where = ("rises towards" if y0 < 1 else
                 "falls towards" if y0 > 1 else "sits at")
        self.readout.setText(
            f"y(0) = {y0:.2f} {where} 1, reaching {ends:.4f} — and it never "
            "arrives. Reaching a constant solution would put two solutions "
            "through one point."
        )


# ---------------------------------------------------------------------------
# The integrating factor: what decays, and what is left
# ---------------------------------------------------------------------------


class LinearFigure(LessonFigure):
    """``y′ + p·y = A·cos(ω t)``, split into the two terms of its answer.

    The derivation ends by reading the answer as a response to the forcing
    plus a term carrying the initial condition. Both are drawn here, so that
    the second visibly dies and the first visibly does not -- which is the
    transient and the steady state, met for the first time.
    """

    title = "The transient and the steady state, drawn apart"
    caption = ("The answer to y′ + p·y = A·cos(ω t) has two terms. The one "
               "carrying y(0) decays at a rate p and forgets where it "
               "started; the one responding to the forcing does not. Raise p "
               "and watch the first vanish sooner, leaving the second alone.")

    _TLIM = (0.0, 14.0)

    def build_sliders(self) -> None:
        self.add_slider("p", "p  (decay rate)", 0.1, 2.0, 0.5,
                        hint="How fast the system forgets its starting "
                             "value. Nothing about the forcing changes.")
        self.add_slider("w", "ω  (driving frequency)", 0.2, 3.0, 1.0)
        self.add_slider("y0", "y(0)", -3.0, 3.0, 2.0)

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        p, w, y0 = self.value("p"), self.value("w"), self.value("y0")
        t = np.linspace(*self._TLIM, 900)

        # The closed form the derivation produces, term by term.
        denominator = p * p + w * w
        steady = (p * np.cos(w * t) + w * np.sin(w * t)) / denominator
        transient = (y0 - p / denominator) * np.exp(-p * t)

        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        self.plot.plot(t, transient, pen=pg.mkPen(self.colour(1), width=2,
                                                  style=Qt.DashLine))
        self.plot.plot(t, steady, pen=pg.mkPen(self.colour(2), width=2,
                                               style=Qt.DotLine))
        self.plot.plot(t, steady + transient,
                       pen=pg.mkPen(self.colour(0), width=3))

        amplitude = 1.0 / np.sqrt(denominator)
        # Three time constants is the usual "as good as gone".
        self.readout.setText(
            f"solid: the answer.  dashed: the transient, gone by t ≈ "
            f"{3 / p:.1f}.  dotted: the steady state, amplitude "
            f"{amplitude:.3f} — set by p and ω, and not by where it started."
        )


# ---------------------------------------------------------------------------
# Exact equations: the answer is a curve, not a formula
# ---------------------------------------------------------------------------


class ExactFigure(LessonFigure):
    """Level curves of the potential, with the field they solve laid over.

    The lesson's claim is that an exact equation's answer is a relation rather
    than a formula for y, and that this is a feature. One level curve of
    F(t, y) = sin t + t·y + y² is drawn bright among its neighbours, with the
    slope field over the top: the curve is tangent to the field everywhere,
    and for most values of C no rearrangement gives y as a function of t.
    """

    title = "The level curves of the potential"
    caption = ("F(t, y) = sin t + t·y + y² held at a constant. Every level "
               "curve solves cos t + y + (t + 2y)·y′ = 0, and the dashes are "
               "that equation's own slope field — the curve runs along them. "
               "Slide C and watch the curve you are on change shape entirely.")

    _TLIM = (-4.0, 4.0)
    _YLIM = (-3.0, 3.0)

    def build_sliders(self) -> None:
        self.add_slider("C", "C  (which level curve)", -6.0, 6.0, 1.0,
                        hint="The constant of integration. One value of C is "
                             "one solution — and an initial condition is how "
                             "you choose it.")

    @staticmethod
    def _potential(T, Y):
        return np.sin(T) + T * Y + Y * Y

    def _problem(self) -> ODEProblem:
        # y' = -(cos t + y) / (t + 2y), the equation the potential solves.
        def field(t, y):
            bottom = t + 2 * y[0]
            if abs(bottom) < 1e-9:
                return np.array([np.nan])
            return np.array([-(np.cos(t) + y[0]) / bottom])

        return ODEProblem(f=field, t_span=self._TLIM,
                          y0=np.array([1.0]))

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")
        self.plot.setXRange(*self._TLIM, padding=0.02)
        self.plot.setYRange(*self._YLIM, padding=0.02)

        segments, _ = analysis.slope_field(
            self._problem(), self._TLIM, self._YLIM, resolution=17,
        )
        pen = pg.mkPen(self.palette_obj.text_muted, width=1)
        for segment in segments:
            self.plot.plot(segment[:, 0], segment[:, 1], pen=pen)

        grid_t = np.linspace(self._TLIM[0], self._TLIM[1], 260)
        grid_y = np.linspace(self._YLIM[0], self._YLIM[1], 260)
        T, Y = np.meshgrid(grid_t, grid_y)
        potential = self._potential(T, Y)

        neighbours = pg.mkPen(self.palette_obj.border, width=1)
        chosen = self.value("C")
        for level in np.arange(-6.0, 6.5, 1.5):
            bright = abs(level - chosen) < 0.75
            for path in analysis._contour_paths(T, Y, potential - level):
                self.plot.plot(
                    path[:, 0], path[:, 1],
                    pen=(pg.mkPen(self.colour(0), width=3) if bright
                         else neighbours),
                )
        self._describe(chosen, T, Y, potential)

    def _describe(self, level, T, Y, potential) -> None:
        paths = analysis._contour_paths(T, Y, potential - level)
        pieces = len(paths)
        if not pieces:
            self.readout.setText(
                f"F = {level:.1f} is not attained in this window — the "
                "potential never reaches it here."
            )
            return
        self.readout.setText(
            f"F(t, y) = {level:.1f}, in {pieces} "
            f"{'piece' if pieces == 1 else 'separate pieces'}. That is the "
            "answer, and there is no rearrangement of it into y = something."
        )


# ---------------------------------------------------------------------------
# What a solution is: a family, and the condition that picks one of it
# ---------------------------------------------------------------------------


class FamilyFigure(LessonFigure):
    """``y' = a·t^n``, integrated, with the constant of integration on a slider.

    The first lesson's hardest sentence is that an equation of order one has a
    *family* of solutions and that one initial condition picks a member of it.
    Stated, it sounds like bookkeeping. Here the family is on the screen at
    once, every member the same shape lifted by a different amount, and moving
    the condition slides the marked curve through them without ever changing
    its shape -- which is the whole content of "+ C".

    Order is a slider too, and it is the same claim again: raising `n` by one
    adds nothing to the picture, but the *number of conditions* the answer
    needs is the order of the equation, not the power on the right.
    """

    title = "One equation, a family of answers"
    caption = ("y′ = a·tⁿ integrates to a family of curves, one per constant "
               "of integration — all the same shape, stacked. An initial "
               "condition does not solve anything; it picks a member. Move "
               "y(0) and watch the marked curve step through the family.")

    _TLIM = (0.0, 2.2)

    def build_sliders(self) -> None:
        self.add_slider("a", "a", 0.5, 4.0, 3.0)
        self.add_slider("n", "n  (power of t)", 0.0, 3.0, 2.0,
                        hint="The power on the right-hand side. It changes "
                             "the shape of every member and not the number "
                             "of them.")
        self.add_slider("y0", "y(0)  (the condition)", -4.0, 6.0, 5.0,
                        hint="One condition, one member of the family. There "
                             "is nothing else for it to decide.")

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        a, n, y0 = self.value("a"), self.value("n"), self.value("y0")
        t = np.linspace(*self._TLIM, 700)
        # The antiderivative of a·t^n. Written out rather than integrated
        # numerically: the point of the lesson is that this one can be done by
        # inspection, and a figure that reached for a solver to draw it would
        # be saying the opposite.
        shape = a * t ** (n + 1) / (n + 1)

        for level in np.arange(-4.0, 6.5, 1.0):
            self.plot.plot(t, shape + level,
                           pen=pg.mkPen(self.palette_obj.border, width=1))
        self.plot.plot(t, shape + y0,
                       pen=pg.mkPen(self.colour(0), width=3))
        self.plot.plot([0.0], [y0], pen=None, symbol="o", symbolSize=11,
                       symbolBrush=self.colour(0))
        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        self.plot.setYRange(-5.0, 12.0, padding=0.02)
        self._describe(a, n, y0, float(shape[-1] + y0))

    def _describe(self, a, n, y0, ending) -> None:
        power = n + 1
        self.readout.setText(
            f"y′ = {a:.2f}·t^({n:.2f})  →  y = {a / power:.3f}·t^({power:.2f})"
            " + C, "
            f"and y(0) = {y0:.2f} makes C = {y0:.2f}. Every curve here solves "
            f"the equation; only this one meets the condition, and it reaches "
            f"{ending:.2f} at t = {self._TLIM[1]:.1f}."
        )


# ---------------------------------------------------------------------------
# Substitution: the change of variable that straightens the family out
# ---------------------------------------------------------------------------


class SubstitutionFigure(LessonFigure):
    """``y' = (t² + y²)/(t·y)`` before and after ``v = y/t``.

    A substitution is asked to be believed twice: that it is legitimate, and
    that it helps. The derivation argues the first. This is the second, and it
    is the pane on the right that makes it -- in the original variables the
    solutions are a family of curves with no obvious rule; in v² against ln t
    they are *parallel straight lines*, every one of slope 2, which is what
    "the substituted equation is separable" looks like when it is drawn.

    The equation is the standard homogeneous one. With v = y/t it becomes
    t·v′ = 1/v, so v² = 2·ln t + K and y = t·√(2·ln t + K): the same family,
    read twice.
    """

    title = "The same family, before and after the substitution"
    caption = ("Left: solutions of y′ = (t² + y²)/(t·y) in the variables it "
               "was written in. Right: the same solutions as v² = (y/t)² "
               "against ln t, where every one of them is a straight line of "
               "slope 2. That is the substituted equation being separable, "
               "drawn.")
    plots = 2

    _TLIM = (0.2, 5.0)

    def build_sliders(self) -> None:
        self.add_slider("K", "K  (the constant)", 0.5, 12.0, 4.0,
                        hint="v² = 2·ln t + K. One constant, one member of "
                             "the family, in either pane.")

    def _members(self):
        """``(t, y, v²)`` for a spread of constants, the chosen one first."""
        t = np.linspace(*self._TLIM, 900)
        chosen = self.value("K")
        for level in [chosen] + [k for k in np.arange(1.0, 12.1, 1.5)]:
            inside = 2.0 * np.log(t) + level
            keep = inside > 0
            yield level, t[keep], t[keep] * np.sqrt(inside[keep]), inside[keep]

    def draw(self) -> None:
        left, right = self.panes[0], self.panes[1]
        for pane in (left, right):
            pane.clear()
        left.setLabel("bottom", "t")
        left.setLabel("left", "y")
        right.setLabel("bottom", "ln t")
        right.setLabel("left", "v²  where  v = y/t")

        faint = pg.mkPen(self.palette_obj.border, width=1)
        for index, (_, t, y, square) in enumerate(self._members()):
            pen = pg.mkPen(self.colour(0), width=3) if index == 0 else faint
            left.plot(t, y, pen=pen)
            right.plot(np.log(t), square, pen=pen)
        left.setYRange(0.0, 12.0, padding=0.02)
        right.setYRange(0.0, 14.0, padding=0.02)
        self._describe()

    def _describe(self) -> None:
        # The slope is measured off the drawn line rather than asserted to be
        # 2, because the claim being made is about the picture.
        t = np.linspace(*self._TLIM, 900)
        square = 2.0 * np.log(t) + self.value("K")
        keep = square > 0
        logs, square = np.log(t[keep]), square[keep]
        slope = float(np.polyfit(logs, square, 1)[0]) if logs.size > 2 else 0.0
        self.readout.setText(
            f"K = {self.value('K'):.2f}: y = t·√(2·ln t + K), which is "
            f"v² = 2·ln t + K. The line on the right has slope {slope:.3f} — "
            "the 2 in the separated equation, and the same 2 for every member "
            "of the family."
        )
