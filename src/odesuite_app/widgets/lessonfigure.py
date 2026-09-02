"""A lesson's own picture, with the sliders that make it a demonstration.

A note can say that raising the harvest rate eventually wipes out both
equilibria. A figure can let someone raise it and watch the two dots slide
together and vanish, which is a different kind of knowing. That is the whole
argument for this module, and it is why each figure is built around the one
parameter the lesson turns on rather than around a general plotting API.

Nothing here computes mathematics of its own. The slope field comes from
`analysis.slope_field`, the equilibria from `analysis.phase_line`, the step
tables from `byhand.walk` and `byhand.refinement`, and the solution curves from
the library's own `solve`. A figure that disagreed with the tools would be
worse than no figure, so it is not given the chance to.

A lesson names a figure by key (`Lesson.figure`), because `lessons/` holds
content and must stay free of Qt -- `tests/test_lessons.py` imports it with
PySide6 blocked and would fail if that ever stopped being true. The registry
that turns a key into a widget lives here, at the other end.
"""

from __future__ import annotations

import math

import numpy as np
import pyqtgraph as pg
import sympy as sp
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from odesuite import ODEProblem, problems, solve

from .. import analysis, byhand, systems
from ..symbolic import describe_roots
from ..theme import Palette
from .controls import ValueSlider

__all__ = ["FIGURES", "LessonFigure", "build_figure"]

#: Height of the plot itself. A lesson figure sits inside a scrolling column of
#: note cards, so it has to be tall enough to read and short enough that the
#: notes above and below it are still visibly part of the same page.
_PLOT_HEIGHT = 300


class LessonFigure(QFrame):
    """A plot, a caption and a row of sliders, themed like the note cards.

    Subclasses supply `title`, `caption`, the sliders they want, and a `draw`
    that redraws from the current slider values. Everything else -- the frame,
    the plot, the palette, and the wiring that redraws on a change -- is here,
    because three figures with three copies of it would drift apart.
    """

    title = ""
    caption = ""
    #: How many plots side by side. Two where the lesson is genuinely two
    #: pictures -- the response in time *and* the response against frequency
    #: are different claims, and overlaying them would say neither clearly.
    plots = 1

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette
        self.setProperty("role", "panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 13, 16, 14)
        layout.setSpacing(8)

        heading = QLabel(self.title)
        heading.setProperty("role", "heading")
        layout.addWidget(heading)

        if self.caption:
            blurb = QLabel(self.caption)
            blurb.setProperty("role", "muted")
            blurb.setWordWrap(True)
            layout.addWidget(blurb)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        #: Every plot, in order. `self.plot` is the first, so the figures
        #: written before this existed are untouched.
        self.panes: list[pg.PlotWidget] = []
        for _ in range(max(int(self.plots), 1)):
            pane = pg.PlotWidget()
            pane.setBackground(palette.plot_background)
            pane.showGrid(x=True, y=True, alpha=0.18)
            pane.setMinimumHeight(_PLOT_HEIGHT)
            self.panes.append(pane)
            row.addWidget(pane, 1)
        self.plot = self.panes[0]
        layout.addLayout(row)

        #: What the figure currently says in words. Kept beside the picture
        #: because the number that changed is usually the point.
        self.readout = QLabel("")
        self.readout.setProperty("role", "mono")
        self.readout.setWordWrap(True)
        layout.addWidget(self.readout)

        self.sliders: dict[str, ValueSlider] = {}
        self._grid = QGridLayout()
        self._grid.setContentsMargins(0, 4, 0, 0)
        self._grid.setHorizontalSpacing(18)
        layout.addLayout(self._grid)

        self.build_sliders()
        self.draw()

    # -- scaffolding -----------------------------------------------------

    def add_slider(self, name: str, label: str, low: float, high: float,
                   value: float, *, log: bool = False, hint: str = "") -> None:
        slider = ValueSlider(label, low, high, value, log=log, hint=hint)
        # `preview` rather than `committed`: these figures redraw in a few
        # milliseconds, and a figure that lags behind the thumb stops feeling
        # like a demonstration of anything.
        slider.preview.connect(lambda _: self.draw())
        self.sliders[name] = slider
        row, column = divmod(len(self.sliders) - 1, 2)
        self._grid.addWidget(slider, row, column)

    def value(self, name: str) -> float:
        return self.sliders[name].value()

    def colour(self, index: int) -> str:
        series = self.palette_obj.series
        return series[index % len(series)]

    def build_sliders(self) -> None:
        """Subclass hook: call `add_slider` for each control."""

    def draw(self) -> None:
        """Subclass hook: redraw from the current slider values."""
        raise NotImplementedError


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
        self.draw()

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
# The phase line
# ---------------------------------------------------------------------------


class PhaseLineFigure(LessonFigure):
    """Harvested logistic growth: ``y' = r·y(1 − y/K) − h``.

    The reason this equation and not a tidier one: raising `h` slides the two
    equilibria together until they collide and vanish, and the population that
    was heading comfortably for its capacity now crashes to zero from every
    starting point. The parabola dropping below the axis is the whole story,
    and it happens at a value you can find on the slider.
    """

    title = "The phase line, and what raising the harvest does"
    caption = ("f(y) plotted against y. Where the curve is above the axis y "
               "increases, so the arrows point right; below it they point "
               "left. Equilibria are where it crosses — filled where the "
               "arrows come in, hollow where they go out. Raise h and watch "
               "the two of them meet.")

    _YLIM = (-1.0, 10.0)

    def build_sliders(self) -> None:
        self.add_slider("r", "r  (growth rate)", 0.2, 2.0, 1.0)
        self.add_slider("K", "K  (capacity)", 2.0, 9.0, 6.0)
        self.add_slider("h", "h  (harvest)", 0.0, 3.0, 0.0,
                        hint="Removed at a constant rate, regardless of how "
                             "many are left. That is what makes the collapse "
                             "abrupt.")

    def _problem(self) -> ODEProblem:
        r, k, h = self.value("r"), self.value("K"), self.value("h")
        return ODEProblem(
            f=lambda t, y: np.array([r * y[0] * (1 - y[0] / k) - h]),
            t_span=(0.0, 1.0),
            y0=np.array([1.0]),
        )

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "y")
        self.plot.setLabel("left", "f(y)")

        problem = self._problem()
        grid = np.linspace(self._YLIM[0], self._YLIM[1], 400)
        values = np.array([problem.f(0.0, np.array([y]))[0] for y in grid])

        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        self.plot.plot(grid, values, pen=pg.mkPen(self.colour(0), width=2))

        points = analysis.phase_line(problem, self._YLIM)
        for point in points:
            stable = point.stability == analysis.STABLE
            colour = (self.palette_obj.success if stable
                      else self.palette_obj.danger)
            self.plot.plot(
                [point.value], [0.0], pen=None, symbol="o", symbolSize=11,
                symbolPen=pg.mkPen(colour, width=2),
                symbolBrush=colour if stable else None,
            )

        self._draw_arrows(problem, points)
        self._describe(points)

    def _draw_arrows(self, problem: ODEProblem, points) -> None:
        """One arrow in each interval the equilibria cut the line into.

        Placed at the midpoint of the interval and pointing the way f says, so
        the arrows are read off the picture rather than asserted beside it.
        """
        edges = [self._YLIM[0]] + [p.value for p in points] + [self._YLIM[1]]
        for low, high in zip(edges, edges[1:]):
            if high - low < 1e-6:
                continue
            middle = 0.5 * (low + high)
            slope = float(problem.f(0.0, np.array([middle]))[0])
            if not np.isfinite(slope) or slope == 0.0:
                continue
            arrow = pg.ArrowItem(
                angle=180 if slope > 0 else 0, headLen=12, tipAngle=32,
                pen=None, brush=self.palette_obj.text_muted,
            )
            arrow.setPos(middle, 0.0)
            self.plot.addItem(arrow)

    def _describe(self, points) -> None:
        if not points:
            self.readout.setText(
                "No equilibria: f(y) < 0 everywhere, so every population "
                "falls to zero. The harvest is past what this K can support."
            )
            return
        named = ", ".join(f"y = {p.value:.2f} ({p.stability})" for p in points)
        # The fold is where the two roots merge, which is where the parabola's
        # maximum r·K/4 first fails to reach the harvest rate.
        fold = self.value("r") * self.value("K") / 4.0
        self.readout.setText(
            f"{named}    —    they merge and vanish at h = r·K/4 = {fold:.2f}"
        )


# ---------------------------------------------------------------------------
# Euler's error
# ---------------------------------------------------------------------------


class EulerErrorFigure(LessonFigure):
    """``y' = y``, ``y(0) = 1`` — the one problem whose answer everyone knows.

    Chosen precisely because ``e^t`` needs no defending: every gap between the
    polygon and the curve is the method's, not the problem's. The slider is `h`
    and the thing to watch is the pair of ratios, which is the difference
    between first order and fourth.

    Those ratios are asymptotic, and the figure is honest about it rather than
    printing the theory: measured on this problem they run 1.46 and 10.6 at
    h = 1, 1.81 and 14.7 at h = 0.2, and 1.94 and 15.7 at h = 0.05. Watching
    them climb towards 2 and 16 as `h` shrinks is a better demonstration of
    what an order statement claims than seeing either number arrive exactly.
    """

    title = "Euler's method, and the price of h"
    caption = ("Both methods on y′ = y, y(0) = 1, whose exact solution is eᵗ. "
               "Drag h and watch the two ratios: halving h roughly halves "
               "Euler's error and cuts RK4's by about sixteen. Neither is "
               "exact at a usable h — they climb towards 2 and 16 as h "
               "shrinks, and that limit is what “order” claims.")

    _SPAN = 2.0

    def build_sliders(self) -> None:
        self.add_slider("h", "h  (step size)", 0.02, 1.0, 0.2, log=True,
                        hint="Logarithmic, because the interesting range "
                             "spans a factor of fifty.")

    @staticmethod
    def _problem() -> ODEProblem:
        return ODEProblem(f=lambda t, y: y.copy(), t_span=(0.0, 2.0),
                          y0=np.array([1.0]), jac=lambda t, y: np.eye(1))

    @staticmethod
    def _exact(t):
        return np.array([np.exp(t)])

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        problem = self._problem()
        h = self.value("h")
        steps = max(int(round(self._SPAN / h)), 1)

        errors = {}
        for index, method in enumerate(byhand.SUPPORTED):
            walked = byhand.walk(problem, method, h, n_steps=steps,
                                 exact=self._exact)
            if not walked.rows:
                continue
            times = [row.t for row in walked.rows] + [walked.rows[-1].t
                                                      + walked.rows[-1].h]
            values = ([float(row.y[0]) for row in walked.rows]
                      + [float(walked.rows[-1].y_next[0])])
            colour = self.colour(index)
            self.plot.plot(times, values, pen=pg.mkPen(colour, width=2),
                           symbol="o", symbolSize=6, symbolBrush=colour,
                           symbolPen=colour)
            errors[method] = walked.final_error

        # eᵗ last, so its dashes fall *on top of* RK4 rather than under it.
        # At a usable h the two are indistinguishable, and a truth curve
        # hidden beneath the approximation would look like it was missing
        # rather than like it had been matched.
        fine = np.linspace(0.0, self._SPAN, 400)
        self.plot.plot(fine, np.exp(fine),
                       pen=pg.mkPen(self.palette_obj.text_muted, width=2,
                                    style=Qt.DashLine))

        self._describe(problem, h, errors)

    def _describe(self, problem: ODEProblem, h: float, errors: dict) -> None:
        parts = [f"h = {h:.3g}"]
        for method in byhand.SUPPORTED:
            error = errors.get(method)
            if error is None:
                continue
            # The ratio the next halving would give, from the same routine the
            # by-hand screen uses -- two levels is all that is needed to state
            # it, and it keeps the figure honest about where the number comes
            # from.
            rows = byhand.refinement(problem, method, h, self._exact, levels=2)
            ratio = rows[-1][3] if len(rows) > 1 and rows[-1][3] else None
            name = "Euler" if method == "euler" else "RK4"
            parts.append(f"{name} error {error:.3g}"
                         + (f" (÷{ratio:.1f} when h halves)" if ratio else ""))
        self.readout.setText("    —    ".join(parts))


# ---------------------------------------------------------------------------
# Damping: one coefficient, three behaviours
# ---------------------------------------------------------------------------


class DampingFigure(LessonFigure):
    """``m x'' + c x' + k x = 0``, with the roots drawn beside the motion.

    The two panes are the same fact told twice, which is the point. On the left
    a complex pair sits off the real axis and the motion oscillates; drag `c`
    up and the pair slides together, collides at ``c = 2*sqrt(mk)``, and splits
    along the real axis -- and the curve on the right stops crossing zero at
    the same moment. Seeing the discriminant change sign is usually a sentence
    in a textbook; here it is a thing that happens.

    The name under the picture comes from `symbolic.describe_roots`, which the
    Solver Studio's root table already uses, so the figure cannot disagree with
    the screen that names the same roots.
    """

    title = "Damping: where the roots go, and what the mass does"
    caption = ("Left: the characteristic roots in the complex plane. Right: "
               "the motion they produce. Drag c and watch the pair slide "
               "together, meet on the real axis at c = 2√(mk), and separate — "
               "the moment the oscillation stops.")
    plots = 2

    _T_END = 12.0

    #: Half a step of the damping slider. Critical damping is a single point
    #: on a continuum, so a slider can essentially never land on it -- at
    #: m = 1, k = 4 the nearest reachable value was 3.996, which is genuinely
    #: underdamped and reported as such. The middle of the three regimes then
    #: never appeared at all, in a figure whose whole subject is the moment
    #: the roots collide. So the damping snaps to the critical value when it
    #: comes within half a step of it: the number shown *is* the number used,
    #: and the regime named is the regime drawn.
    _SNAP = 12.0 / 1000 / 2

    def build_sliders(self) -> None:
        self.add_slider("m", "m  (mass)", 0.5, 4.0, 1.0)
        self.add_slider("c", "c  (damping)", 0.0, 12.0, 1.0,
                        hint="The one coefficient that decides the regime. "
                             "Critical damping is at 2√(mk), and the slider "
                             "snaps to it as it passes.")
        self.add_slider("k", "k  (stiffness)", 1.0, 16.0, 4.0)

    def damping(self) -> tuple[float, float]:
        """``(c, c_critical)``, with `c` snapped to critical when it is near."""
        m, k = self.value("m"), self.value("k")
        critical = 2.0 * math.sqrt(m * k)
        c = self.value("c")
        return (critical if abs(c - critical) <= self._SNAP else c), critical

    def _roots(self, m: float, c: float, k: float):
        """The characteristic roots, as sympy expects to be handed them.

        `describe_roots` wants ``[(root, multiplicity)]`` -- the same shape the
        Studio's root table passes it -- so a repeated root is one entry with
        multiplicity two rather than the same number twice, and the words
        "critically damped" depend on getting that right.
        """
        discriminant = c * c - 4.0 * m * k
        if abs(discriminant) < 1e-9 * max(c * c, 1.0):
            return [(sp.Float(-c / (2 * m)), 2)]
        if discriminant > 0:
            root = math.sqrt(discriminant)
            return [(sp.Float((-c + root) / (2 * m)), 1),
                    (sp.Float((-c - root) / (2 * m)), 1)]
        imaginary = math.sqrt(-discriminant) / (2 * m)
        real = -c / (2 * m)
        return [(sp.Float(real) + sp.I * sp.Float(imaginary), 1),
                (sp.Float(real) - sp.I * sp.Float(imaginary), 1)]

    def draw(self) -> None:
        m, k = self.value("m"), self.value("k")
        c, critical = self.damping()
        roots = self._roots(m, c, k)

        plane, motion = self.panes
        plane.clear()
        plane.setLabel("bottom", "Re r")
        plane.setLabel("left", "Im r")
        plane.addLine(x=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        plane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))

        oscillates = any(sp.im(root) != 0 for root, _ in roots)
        colour = self.palette_obj.accent if oscillates else self.colour(1)
        for root, multiplicity in roots:
            plane.plot(
                [float(sp.re(root))], [float(sp.im(root))], pen=None,
                symbol="o", symbolSize=13 if multiplicity > 1 else 10,
                symbolBrush=colour, symbolPen=pg.mkPen(colour, width=2),
            )
        # Fix the window so the roots *move* rather than the axes moving under
        # them: a pair colliding is only visible if the frame holds still.
        # The natural frequency is the scale to use, because every underdamped
        # root lies inside a circle of that radius -- so the frame does not
        # budge anywhere in the range where the collision happens. It widens
        # only once a root runs off to the left, which is well past it.
        natural = math.sqrt(k / m)
        furthest = max(abs(float(sp.re(root))) for root, _ in roots)
        reach = 1.4 * max(natural, furthest)
        plane.setXRange(-reach, 0.35 * natural, padding=0.02)
        plane.setYRange(-1.4 * natural, 1.4 * natural, padding=0.02)

        motion.clear()
        motion.setLabel("bottom", "t")
        motion.setLabel("left", "x")
        motion.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        bench = problems.spring_mass_damper(
            mass=m, damping=c, stiffness=k,
            initial_position=1.0, initial_velocity=0.0, t_end=self._T_END,
        )
        times = np.linspace(0.0, self._T_END, 600)
        values = np.atleast_2d(bench.exact(times))[0]
        motion.plot(times, values, pen=pg.mkPen(colour, width=2))

        self.readout.setText(
            f"{describe_roots(roots, order=2)}    —    "
            f"c = {c:.2f} against a critical {critical:.2f}"
        )


# ---------------------------------------------------------------------------
# Beats, and resonance
# ---------------------------------------------------------------------------


class ResonanceFigure(LessonFigure):
    """``x'' + w0^2 x = cos(w t)`` from rest, and the amplitude it settles to.

    Two panes because these are two different claims. On the left, an *undamped*
    system driven near its natural frequency: the response is a difference of
    cosines, which reads as a fast oscillation inside a slow envelope, and the
    envelope grows longer the closer the frequencies get. On the right, what
    damping does to the same story -- the blow-up becomes a peak, finite and
    lower and further left the more damping there is.

    Measured, and it shapes the code: the beats amplitude ``1/(w0^2 - w^2)`` is
    0.69 at w = 1.6, 2.56 at 1.9 and **25.1 at 1.99**, so the pane is left to
    autorange rather than pinned, and at w = w0 the closed form is the secular
    ``t*sin(w0 t)/(2 w0)`` rather than a division by zero.
    """

    title = "Beats, and what happens when the frequencies match"
    caption = ("Left: an undamped system driven at ω, from rest. As ω "
               "approaches ω₀ = 2 the beats stretch out and grow, and at ω = "
               "ω₀ exactly the envelope becomes a straight line — resonance. "
               "Right: with damping the blow-up is only a peak.")
    plots = 2

    _W0 = 2.0
    _T_END = 60.0

    def build_sliders(self) -> None:
        self.add_slider("w", "ω  (driving frequency)", 0.5, 3.5, 1.6,
                        hint="The natural frequency is 2. Bring ω up to it "
                             "and watch the envelope stretch.")
        self.add_slider("c", "c  (damping, right-hand plot)", 0.05, 3.0, 0.4)

    def _response(self, times, omega: float):
        """``x(t)`` from rest, and whether this is the resonant case.

        The two formulas are one limit apart, and the limit is the lesson: as
        w -> w0 the bounded solution's amplitude runs away, and exactly at w0
        the t out front is what is left of it.
        """
        w0 = self._W0
        if abs(omega - w0) < 1e-3:
            return times * np.sin(w0 * times) / (2 * w0), True
        amplitude = 1.0 / (w0 * w0 - omega * omega)
        return amplitude * (np.cos(omega * times) - np.cos(w0 * times)), False

    def draw(self) -> None:
        omega, c = self.value("w"), self.value("c")
        beats, resonant = self.panes

        times = np.linspace(0.0, self._T_END, 3000)
        values, at_resonance = self._response(times, omega)

        beats.clear()
        beats.setLabel("bottom", "t")
        beats.setLabel("left", "x")
        beats.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        beats.plot(times, values, pen=pg.mkPen(self.colour(0), width=1))

        # The envelope, drawn because it is the thing being described. Off
        # resonance it is the slow half of the product formula; at resonance
        # it is the straight line the amplitude follows.
        w0 = self._W0
        if at_resonance:
            envelope = times / (2 * w0)
        else:
            envelope = np.abs(
                2.0 / (w0 * w0 - omega * omega)
                * np.sin((w0 - omega) * times / 2)
            )
        for sign in (1, -1):
            beats.plot(times, sign * envelope,
                       pen=pg.mkPen(self.palette_obj.text_muted, width=2,
                                    style=Qt.DashLine))
        beats.enableAutoRange(axis="y")

        resonant.clear()
        resonant.setLabel("bottom", "ω")
        resonant.setLabel("left", "steady amplitude")
        frequencies = np.linspace(0.05, 4.0, 500)
        # The standard response of m x'' + c x' + k x = cos(wt), with m = 1 and
        # k = w0^2 so the two panes describe the same oscillator.
        stiffness = w0 * w0
        amplitudes = 1.0 / np.sqrt(
            (stiffness - frequencies**2) ** 2 + (c * frequencies) ** 2
        )
        resonant.plot(frequencies, amplitudes,
                      pen=pg.mkPen(self.colour(1), width=2))
        peak = int(np.argmax(amplitudes))
        resonant.plot([frequencies[peak]], [amplitudes[peak]], pen=None,
                      symbol="o", symbolSize=9,
                      symbolBrush=self.colour(1), symbolPen=self.colour(1))
        resonant.addLine(x=omega,
                         pen=pg.mkPen(self.palette_obj.text_muted, width=1,
                                      style=Qt.DashLine))

        if at_resonance:
            words = ("ω = ω₀: resonance. The particular solution carries a "
                     "factor of t, so the amplitude grows without bound")
        else:
            period = 4 * math.pi / abs(w0 - omega)
            words = (f"beats: amplitude {abs(1 / (w0 * w0 - omega * omega)):.2f}"
                     f", one swell every {period:.0f} time units")
        self.readout.setText(
            f"{words}    —    damped peak {amplitudes[peak]:.2f} at "
            f"ω = {frequencies[peak]:.2f}"
        )


# ---------------------------------------------------------------------------
# Eigendirections: the skeleton a phase portrait bends around
# ---------------------------------------------------------------------------


class EigenlinesFigure(LessonFigure):
    """``x' = A x`` for a 2x2 matrix you can change entry by entry.

    The claim this makes visible is the one a formula states and a picture
    proves: the eigenvectors are the *only* straight-line trajectories, and
    every other curve bends between them. Drag an entry and watch the two
    lines swing; drag it further and watch them collide and vanish, at which
    point the field starts to rotate and the origin becomes a spiral.

    The classification underneath is `systems.classify`, the same function the
    narrator uses to name the origin at the end of its derivation -- so the
    picture and the working cannot disagree about what they are looking at.
    """

    title = "Eigendirections, and the flow around them"
    caption = ("The vector field of x′ = Ax, with the eigendirections drawn "
               "on. Trajectories that start on one stay on it forever; every "
               "other one bends between them. Change an entry until the two "
               "lines collide — past that the eigenvalues are complex and "
               "there are no straight-line solutions at all.")

    _LIM = 3.0

    def build_sliders(self) -> None:
        self.add_slider("a", "a  (row 1, col 1)", -4.0, 4.0, 1.0)
        self.add_slider("b", "b  (row 1, col 2)", -4.0, 4.0, 2.0)
        self.add_slider("c", "c  (row 2, col 1)", -4.0, 4.0, 3.0)
        self.add_slider("d", "d  (row 2, col 2)", -4.0, 4.0, 2.0)

    def entries(self) -> tuple[float, float, float, float]:
        return (self.value("a"), self.value("b"),
                self.value("c"), self.value("d"))

    def _problem(self) -> ODEProblem:
        a, b, c, d = self.entries()
        return ODEProblem(
            f=lambda t, y: np.array([a * y[0] + b * y[1],
                                     c * y[0] + d * y[1]]),
            t_span=(0.0, 6.0),
            y0=np.array([1.0, 1.0]),
        )

    def eigen(self):
        """``(eigenvalues, eigenvectors)`` as plain numpy, or complex ones.

        numpy rather than sympy: this runs on every slider tick, and the
        narrator's exact arithmetic is not what a picture needs. The two agree
        on the classification, which is the part that is claimed in words.
        """
        a, b, c, d = self.entries()
        return np.linalg.eig(np.array([[a, b], [c, d]], dtype=float))

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "x")
        self.plot.setLabel("left", "y")
        self.plot.setXRange(-self._LIM, self._LIM, padding=0.02)
        self.plot.setYRange(-self._LIM, self._LIM, padding=0.02)

        problem = self._problem()
        self._draw_field(problem)

        values, vectors = self.eigen()
        real = np.all(np.abs(values.imag) < 1e-9)
        if real:
            for index in range(2):
                direction = vectors[:, index].real
                if np.linalg.norm(direction) < 1e-12:
                    continue
                direction = direction / np.linalg.norm(direction)
                span = direction * self._LIM * 1.5
                growing = values[index].real > 0
                colour = (self.palette_obj.danger if growing
                          else self.palette_obj.success)
                self.plot.plot([-span[0], span[0]], [-span[1], span[1]],
                               pen=pg.mkPen(colour, width=3))
                # An arrowhead a little way out, pointing the way the flow
                # goes: outwards for a positive eigenvalue, inwards for a
                # negative one. Which way the line points is the whole
                # information a line by itself cannot carry.
                at = direction * self._LIM * 0.62
                angle = np.degrees(np.arctan2(direction[1], direction[0]))
                arrow = pg.ArrowItem(
                    angle=180 - angle if growing else -angle,
                    headLen=13, tipAngle=32, pen=None, brush=colour,
                )
                arrow.setPos(float(at[0]), float(at[1]))
                self.plot.addItem(arrow)

        self._draw_trajectories(problem)
        self._describe(values, real)

    def _draw_field(self, problem: ODEProblem) -> None:
        """The direction field, as short dashes of equal length on screen."""
        grid = np.linspace(-self._LIM, self._LIM, 13)
        length = 2 * self._LIM / 13 * 0.42
        for x in grid:
            for y in grid:
                vx, vy = problem.f(0.0, np.array([x, y]))
                norm = float(np.hypot(vx, vy))
                if norm < 1e-9:
                    continue
                dx, dy = vx / norm * length, vy / norm * length
                self.plot.plot([x - dx / 2, x + dx / 2],
                               [y - dy / 2, y + dy / 2],
                               pen=pg.mkPen(self.palette_obj.text_muted,
                                            width=1))

    def _draw_trajectories(self, problem: ODEProblem) -> None:
        """A few curves that are *not* on an eigendirection, to bend."""
        for index, start in enumerate(((1.0, 0.2), (-0.6, 1.0), (0.3, -1.0))):
            pieces = []
            for horizon in (2.5, -2.5):
                candidate = ODEProblem(f=problem.f_user, t_span=(0.0, horizon),
                                       y0=np.array(start, dtype=float))
                try:
                    found = solve(candidate, method="dopri5", rtol=1e-7,
                                  atol=1e-9)
                except Exception:
                    continue
                if found.t.size:
                    pieces.append((found.y[0], found.y[1]))
            colour = self.colour(index)
            for xs, ys in pieces:
                inside = (np.abs(xs) <= self._LIM * 1.4) & (
                    np.abs(ys) <= self._LIM * 1.4)
                if inside.any():
                    self.plot.plot(xs[inside], ys[inside],
                                   pen=pg.mkPen(colour, width=2))

    def _describe(self, values, real: bool) -> None:
        if real:
            names = ", ".join(f"λ = {value.real:.2f}" for value in values)
        else:
            first = values[0]
            names = f"λ = {first.real:.2f} ± {abs(first.imag):.2f}i"
        # The words come from the narrator, so the picture and the working
        # cannot disagree about what the origin is.
        words = systems.classify(
            [sp.Float(value.real) + sp.I * sp.Float(value.imag)
             for value in values]
        )
        self.readout.setText(f"{names}    —    {words}")


#: Figure key -> the widget class that draws it. `Lesson.figure` names one of
#: these, and `tests/test_lessons.py` requires that every name it uses is here
#: -- a typo would otherwise be a lesson that silently lost its picture.
FIGURES: dict[str, type[LessonFigure]] = {
    "slope_field": SlopeFieldFigure,
    "phase_line": PhaseLineFigure,
    "euler_error": EulerErrorFigure,
    "damping": DampingFigure,
    "resonance": ResonanceFigure,
    "eigenlines": EigenlinesFigure,
}


def build_figure(key: str, palette: Palette, parent=None) -> QWidget | None:
    """The figure named by `key`, or None where there is no such figure.

    None rather than an exception: a lesson naming a figure that does not exist
    is a content bug, caught by the tests, and it should not take the whole
    lesson page down with it in the meantime.
    """
    figure = FIGURES.get(key)
    return None if figure is None else figure(palette, parent)
