"""Figures for Second-order linear equations."""

from __future__ import annotations

import math

import numpy as np
import pyqtgraph as pg
import sympy as sp
from PySide6.QtCore import Qt

from ...symbolic import describe_roots
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


# ---------------------------------------------------------------------------
# Superposition: why two solutions are worth more than two solutions
# ---------------------------------------------------------------------------


class SuperpositionFigure(LessonFigure):
    """``y" - y = 0``, its two basic solutions, and every combination of them.

    Superposition is the property the rest of the unit is built on, and it is
    easy to nod at and hard to feel. Here the two dashed curves never move --
    they are e^t and e^(-t), and they are all the equation ever supplies.
    Everything else on the screen is arithmetic done to them.

    The cases worth reaching for are the ones a reader would not guess. At
    c1 = 0 the answer decays although one of its ingredients explodes; at
    c1 = c2 it is a cosh, symmetric about the axis, and nothing in the
    ingredients looks symmetric at all. Neither is a new solution: both are
    the same two curves, weighted.
    """

    title = "Two solutions, and everything you can make from them"
    caption = ("Dashed: eᵗ and e⁻ᵗ, the two solutions of y″ − y = 0. Solid: "
               "c₁eᵗ + c₂e⁻ᵗ, which solves it for every pair of constants. "
               "The two conditions at t = 0 are read straight off them: "
               "y(0) = c₁ + c₂ and y′(0) = c₁ − c₂.")

    _TLIM = (-2.0, 2.0)

    def build_sliders(self) -> None:
        self.add_slider("c1", "c₁  (weight on eᵗ)", -2.0, 2.0, 1.0)
        self.add_slider("c2", "c₂  (weight on e⁻ᵗ)", -2.0, 2.0, 1.0,
                        hint="Equal weights give a cosh, symmetric about the "
                             "axis; opposite ones give a sinh. Neither is a "
                             "new solution.")

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        c1, c2 = self.value("c1"), self.value("c2")
        t = np.linspace(*self._TLIM, 900)
        rising, falling = np.exp(t), np.exp(-t)

        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        for curve, index in ((rising, 1), (falling, 2)):
            self.plot.plot(t, curve,
                           pen=pg.mkPen(self.colour(index), width=2,
                                        style=Qt.DashLine))
        total = c1 * rising + c2 * falling
        self.plot.plot(t, total, pen=pg.mkPen(self.colour(0), width=3))
        self.plot.plot([0.0], [c1 + c2], pen=None, symbol="o", symbolSize=10,
                       symbolBrush=self.colour(0))
        self.plot.setYRange(-6.0, 9.0, padding=0.02)
        self._describe(c1, c2, t, total)

    def _describe(self, c1, c2, t, total) -> None:
        # The residual of the combination, measured off the drawn samples
        # rather than asserted: what is being checked is the curve on screen.
        step = float(t[1] - t[0])
        second = np.gradient(np.gradient(total, step), step)
        residual = float(np.max(np.abs(second - total)[4:-4]))
        if abs(c1) < 1e-6 and abs(c2) < 1e-6:
            shape = "the zero solution, which is a member of the family too"
        elif abs(c1 - c2) < 1e-6:
            shape = f"{2 * c1:.2f}·cosh t — symmetric, though neither part is"
        elif abs(c1 + c2) < 1e-6:
            shape = f"{2 * c1:.2f}·sinh t — odd, though neither part is"
        elif abs(c1) < 1e-6:
            shape = "pure decay, although eᵗ is still one of the ingredients"
        else:
            shape = "a combination that grows like eᵗ in the end, since c₁ ≠ 0"
        self.readout.setText(
            f"y(0) = {c1 + c2:.2f}, y′(0) = {c1 - c2:.2f}: {shape}. "
            f"Substituting the drawn curve back leaves at most {residual:.1e} "
            "— it solves the equation for every pair."
        )


# ---------------------------------------------------------------------------
# Characteristic roots: one discriminant, three answers
# ---------------------------------------------------------------------------


class RootCasesFigure(LessonFigure):
    """``y" + b*y' + c*y = 0``, with the parameter plane beside the solution.

    The three cases are usually met as three formulas to remember. They are
    one picture: the parabola c = b^2/4 in the left pane *is* the case
    distinction, and the marker is the equation currently being drawn. Cross
    the parabola and the right pane changes character -- two exponentials, one
    exponential with a t in front of it, or an oscillation -- at precisely the
    moment the marker crosses.

    Deliberately not the same picture as `DampingFigure`, which draws the
    *roots* moving in the complex plane. This draws the *coefficients*, which
    is what a reader actually has in front of them when they have to choose
    which of the three formulas to write down.

    The naming comes from `symbolic.describe_roots`, the same function the
    Solver Studio's root table uses, so the figure and that screen cannot
    disagree about an equation they both name.
    """

    title = "The discriminant, drawn: which case an equation is in"
    caption = ("Left: the b–c plane. The parabola is b² = 4c and it is the "
               "whole case distinction — below it two real roots, on it a "
               "repeated one, above it a complex pair. Right: the solution "
               "for the marked point, from y(0) = 1 and y′(0) = 0, with its "
               "two basic solutions dashed.")
    plots = 2

    _TLIM = (0.0, 12.0)
    #: Half a slider step. A repeated root is a single curve through a plane,
    #: so a quantised slider can essentially never land on it -- the problem
    #: `DampingFigure` found, and the same answer: snap when within half a
    #: step, so the case named is the case drawn.
    _SNAP = 4.0 / 1000 / 2

    def build_sliders(self) -> None:
        self.add_slider("b", "b  (coefficient of y′)", -1.0, 4.0, 3.0)
        self.add_slider("c", "c  (coefficient of y)", 0.0, 4.0, 2.0,
                        hint="With b this is the whole equation. b² − 4c "
                             "decides everything, and c snaps onto b²/4 "
                             "when it comes within half a step of it.")

    def coefficients(self) -> tuple[float, float]:
        b, c = self.value("b"), self.value("c")
        critical = b * b / 4.0
        return b, (critical if abs(c - critical) < self._SNAP else c)

    def _basis(self, b: float, c: float, t: np.ndarray):
        """The two solutions the case supplies, and the one meeting y(0)=1."""
        discriminant = b * b - 4.0 * c
        if abs(discriminant) < 1e-12:
            root = -b / 2.0
            decay = np.exp(root * t)
            return decay, t * decay, (1.0 - root * t) * decay
        if discriminant > 0:
            gap = np.sqrt(discriminant)
            r1, r2 = (-b + gap) / 2.0, (-b - gap) / 2.0
            first, second = np.exp(r1 * t), np.exp(r2 * t)
            return first, second, (r2 * first - r1 * second) / (r2 - r1)
        alpha, beta = -b / 2.0, np.sqrt(-discriminant) / 2.0
        envelope = np.exp(alpha * t)
        first, second = envelope * np.cos(beta * t), envelope * np.sin(beta * t)
        return first, second, first - (alpha / beta) * second

    def draw(self) -> None:
        b, c = self.coefficients()
        self._draw_plane(b, c)
        self._draw_solution(b, c)
        self._describe(b, c)

    def _draw_plane(self, b: float, c: float) -> None:
        pane = self.panes[0]
        pane.clear()
        pane.setLabel("bottom", "b")
        pane.setLabel("left", "c")
        grid = np.linspace(-1.0, 4.0, 400)
        pane.plot(grid, grid * grid / 4.0,
                  pen=pg.mkPen(self.palette_obj.warning, width=3))
        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.addLine(x=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.plot([b], [c], pen=None, symbol="o", symbolSize=13,
                  symbolBrush=self.colour(0))
        pane.setXRange(-1.0, 4.0, padding=0.02)
        pane.setYRange(0.0, 4.0, padding=0.02)

    def _draw_solution(self, b: float, c: float) -> None:
        pane = self.panes[1]
        pane.clear()
        pane.setLabel("bottom", "t")
        pane.setLabel("left", "y")
        t = np.linspace(*self._TLIM, 1200)
        first, second, chosen = self._basis(b, c, t)

        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        for curve, index in ((first, 1), (second, 2)):
            pane.plot(t, np.clip(curve, -40.0, 40.0),
                      pen=pg.mkPen(self.colour(index), width=2,
                                   style=Qt.DashLine))
        pane.plot(t, np.clip(chosen, -40.0, 40.0),
                  pen=pg.mkPen(self.colour(0), width=3))
        pane.setYRange(-2.5, 2.5, padding=0.02)

    def _roots(self, b: float, c: float):
        """The characteristic roots as ``[(root, multiplicity)]``.

        The shape `describe_roots` takes, which is also the shape the Studio's
        root table hands it -- a repeated root is one entry with multiplicity
        two rather than the same number twice, and the words "critically
        damped" depend on getting that right.
        """
        discriminant = b * b - 4.0 * c
        if abs(discriminant) < 1e-12:
            return [(sp.Float(-b / 2.0), 2)]
        if discriminant > 0:
            gap = math.sqrt(discriminant)
            return [(sp.Float((-b + gap) / 2.0), 1),
                    (sp.Float((-b - gap) / 2.0), 1)]
        imaginary = math.sqrt(-discriminant) / 2.0
        return [(sp.Float(-b / 2.0) + sp.I * sp.Float(imaginary), 1),
                (sp.Float(-b / 2.0) - sp.I * sp.Float(imaginary), 1)]

    def _describe(self, b: float, c: float) -> None:
        discriminant = b * b - 4.0 * c
        words = describe_roots(self._roots(b, c), order=2)
        where = ("on the parabola" if abs(discriminant) < 1e-12
                 else "below it" if discriminant > 0 else "above it")
        self.readout.setText(
            f"b² − 4c = {discriminant:+.3f}, so the marker sits {where}: "
            f"{words}."
        )


# ---------------------------------------------------------------------------
# Variation of parameters: the forcing no guess can cover
# ---------------------------------------------------------------------------


class VariationFigure(LessonFigure):
    """``y" + y = sec t``, whose particular solution cannot be guessed.

    The lesson's whole justification is negative: undetermined coefficients
    needs a forcing term whose derivatives close into a finite family, and
    sec t does not have one. That is an assertion about an infinite list, so
    the left pane shows the next best thing -- sec t against the shapes a
    guess would have to be built from, running away from all of them towards
    the singularity.

    The right pane is the answer variation of parameters produces, with the
    homogeneous part on sliders as usual. The two vertical lines are where
    the forcing is undefined, and they are the reason the solution is only
    claimed on the interval between them -- an existence statement the figure
    makes visible rather than asserting.

    Everything drawn is closed form: the particular solution of this equation
    is cos t * ln|cos t| + t * sin t, which is what the narrator derives.
    """

    title = "A forcing term no guess covers, and the answer anyway"
    caption = ("Left: sec t, against the cosine and the line a guess would "
               "be assembled from. It leaves both, and it does so by going "
               "to infinity at ±π/2. Right: the answer there — a particular "
               "solution (dotted) plus the usual family (dashed).")
    plots = 2

    #: Just inside the singularities of sec at +-pi/2. The interval is the
    #: content, so it is drawn right up to its ends rather than trimmed to a
    #: round number that would hide where it stops.
    _EDGE = math.pi / 2
    _TLIM = (-1.52, 1.52)

    def build_sliders(self) -> None:
        self.add_slider("c1", "c₁  (weight on cos t)", -2.0, 2.0, 0.0)
        self.add_slider("c2", "c₂  (weight on sin t)", -2.0, 2.0, 0.0,
                        hint="The homogeneous part. It moves the answer "
                             "about inside the interval and does nothing "
                             "whatever about the singularities at its ends.")

    def _parts(self):
        t = np.linspace(*self._TLIM, 1400)
        cosine = np.cos(t)
        # cos t * ln|cos t| + t * sin t. Both integrals come from the
        # Wronskian formula: -sin t * sec t integrates to ln|cos t|, and
        # cos t * sec t to t.
        particular = cosine * np.log(np.abs(cosine)) + t * np.sin(t)
        homogeneous = self.value("c1") * cosine + self.value("c2") * np.sin(t)
        return t, particular, homogeneous

    def draw(self) -> None:
        self._draw_forcing()
        self._draw_answer()
        self._describe()

    def _draw_forcing(self) -> None:
        pane = self.panes[0]
        pane.clear()
        pane.setLabel("bottom", "t")
        pane.setLabel("left", "forcing")
        t = np.linspace(*self._TLIM, 1400)
        pane.plot(t, 1.0 / np.cos(t), pen=pg.mkPen(self.colour(0), width=3))
        for curve, index in ((np.cos(t), 1), (t, 2)):
            pane.plot(t, curve, pen=pg.mkPen(self.colour(index), width=2,
                                             style=Qt.DashLine))
        self._mark_edges(pane)
        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.setYRange(-3.0, 12.0, padding=0.02)

    def _draw_answer(self) -> None:
        pane = self.panes[1]
        pane.clear()
        pane.setLabel("bottom", "t")
        pane.setLabel("left", "y")
        t, particular, homogeneous = self._parts()
        pane.plot(t, particular, pen=pg.mkPen(self.colour(2), width=2,
                                              style=Qt.DotLine))
        pane.plot(t, homogeneous, pen=pg.mkPen(self.colour(1), width=2,
                                               style=Qt.DashLine))
        pane.plot(t, particular + homogeneous,
                  pen=pg.mkPen(self.colour(0), width=3))
        self._mark_edges(pane)
        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.setYRange(-4.0, 4.0, padding=0.02)

    def _mark_edges(self, pane) -> None:
        for edge in (-self._EDGE, self._EDGE):
            pane.addLine(x=edge, pen=pg.mkPen(self.palette_obj.warning,
                                              width=2, style=Qt.DashLine))

    def _describe(self) -> None:
        t, particular, homogeneous = self._parts()
        total = particular + homogeneous
        step = float(t[1] - t[0])
        second = np.gradient(np.gradient(total, step), step)
        middle = slice(t.size // 4, 3 * t.size // 4)
        residual = float(np.max(
            np.abs(second[middle] + total[middle] - 1.0 / np.cos(t[middle]))
        ))
        self.readout.setText(
            "the Wronskian of cos t and sin t is 1, so the two integrals are "
            "just −sin t · sec t and cos t · sec t, giving ln|cos t| and t. "
            f"Substituting the drawn answer back over the middle half leaves "
            f"{residual:.1e}, and it says nothing at all outside "
            "(−π/2, π/2), where sec t does not exist."
        )


# ---------------------------------------------------------------------------
# Higher order: n roots, n solutions, and which one wins
# ---------------------------------------------------------------------------


class HigherOrderFigure(LessonFigure):
    """``y^(3) - 6y" + 11y' - 6y = 0``, whose roots are 1, 2 and 3.

    Order three changes nothing about the method and two things about the
    experience of using it. There are now three constants, so three conditions
    are needed rather than two -- and the picture makes the count concrete,
    because switching any one weight to zero visibly leaves a curve that still
    solves the equation and no longer meets the conditions.

    The second is dominance. The three ingredients differ only in how fast
    they grow, and past a certain t the largest root owns the answer entirely;
    the figure measures where that happens rather than saying "eventually".
    Set c3 to zero and the same sentence is true of the next root down, which
    is the part worth noticing.
    """

    title = "Three roots, three solutions, and the one that takes over"
    caption = ("Dashed: eᵗ, e²ᵗ and e³ᵗ, the three solutions the roots 1, 2 "
               "and 3 supply. Solid: their weighted sum, which is the general "
               "answer. Three constants means three conditions — and past a "
               "certain t the largest root with a non-zero weight owns the "
               "curve.")

    _TLIM = (0.0, 2.4)
    _ROOTS = (1.0, 2.0, 3.0)

    def build_sliders(self) -> None:
        for index, root in enumerate(self._ROOTS, start=1):
            self.add_slider(
                f"c{index}", f"c{index}  (weight on e^({root:.0f}t))",
                -1.5, 1.5, 1.0 if index == 1 else 0.5,
            )

    def weights(self) -> tuple[float, float, float]:
        return (self.value("c1"), self.value("c2"), self.value("c3"))

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        t = np.linspace(*self._TLIM, 900)
        weights = self.weights()
        total = np.zeros_like(t)
        for index, (root, weight) in enumerate(zip(self._ROOTS, weights)):
            piece = np.exp(root * t)
            self.plot.plot(t, piece, pen=pg.mkPen(self.colour(index + 1),
                                                  width=2, style=Qt.DashLine))
            total = total + weight * piece
        self.plot.plot(t, total, pen=pg.mkPen(self.colour(0), width=3))
        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        self.plot.setYRange(-30.0, 60.0, padding=0.02)
        self._describe(t, total, weights)

    def _describe(self, t, total, weights) -> None:
        live = [(root, weight) for root, weight in zip(self._ROOTS, weights)
                if abs(weight) > 1e-6]
        if not live:
            self.readout.setText(
                "every weight is zero, which is the zero solution — a member "
                "of the family, and the only one meeting "
                "y(0) = y′(0) = y″(0) = 0."
            )
            return
        biggest, weight = max(live, key=lambda pair: pair[0])
        leading = weight * np.exp(biggest * t)
        # The leading term's share of the answer, walked off the drawn samples
        # rather than argued asymptotically -- and reported at the end of the
        # window whether or not it has crossed, because "not yet" with no
        # number attached is the least useful thing this could say.
        share = float(np.abs(leading[-1]) / max(np.abs(total[-1]), 1e-30))
        close = np.abs(total - leading) <= 0.1 * np.abs(total)
        when = float(t[close][0]) if close.any() else float("inf")
        reached = (
            f"e^({biggest:.0f}t) is within 10% of the whole answer from "
            f"t = {when:.2f} onwards, and is {100 * share:.0f}% of it by "
            f"t = {self._TLIM[1]:.1f}"
            if np.isfinite(when) else
            f"e^({biggest:.0f}t) is only {100 * share:.0f}% of the answer by "
            f"t = {self._TLIM[1]:.1f}, so the smaller roots still matter here"
        )
        self.readout.setText(
            f"y(0) = {sum(weights):.2f}, y′(0) = "
            f"{sum(r * w for r, w in zip(self._ROOTS, weights)):.2f}, "
            f"y″(0) = "
            f"{sum(r * r * w for r, w in zip(self._ROOTS, weights)):.2f} — "
            f"three numbers, which is what three constants cost. {reached}."
        )
