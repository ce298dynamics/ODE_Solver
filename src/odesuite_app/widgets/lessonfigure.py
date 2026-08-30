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

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from odesuite import ODEProblem, solve

from .. import analysis, byhand
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

        self.plot = pg.PlotWidget()
        self.plot.setBackground(palette.plot_background)
        self.plot.showGrid(x=True, y=True, alpha=0.18)
        self.plot.setMinimumHeight(_PLOT_HEIGHT)
        layout.addWidget(self.plot)

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


#: Figure key -> the widget class that draws it. `Lesson.figure` names one of
#: these, and `tests/test_lessons.py` requires that every name it uses is here
#: -- a typo would otherwise be a lesson that silently lost its picture.
FIGURES: dict[str, type[LessonFigure]] = {
    "slope_field": SlopeFieldFigure,
    "phase_line": PhaseLineFigure,
    "euler_error": EulerErrorFigure,
}


def build_figure(key: str, palette: Palette, parent=None) -> QWidget | None:
    """The figure named by `key`, or None where there is no such figure.

    None rather than an exception: a lesson naming a figure that does not exist
    is a content bug, caught by the tests, and it should not take the whole
    lesson page down with it in the meantime.
    """
    figure = FIGURES.get(key)
    return None if figure is None else figure(palette, parent)
