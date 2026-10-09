"""Figures for Models and numerical methods."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt

from odesuite import ODEProblem

from ... import analysis, byhand
from .base import LessonFigure

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
# Falling with drag: terminal velocity, and what happens without it
# ---------------------------------------------------------------------------


class MotionFigure(LessonFigure):
    """``m·v′ = −m·g − k·v``, against the terminal velocity it approaches.

    The derivation finds terminal velocity by setting the right-hand side to
    zero, before solving anything. Here that value is a line, and the solution
    is a curve bending towards it -- so the equilibrium is visibly the answer
    to a question about the equation rather than a feature of the formula.
    Take the drag to nothing and the curve straightens into free fall, which
    has no terminal velocity at all.
    """

    title = "Falling with drag, and the speed it settles at"
    caption = ("Velocity against time, with up positive. The dashed line is "
               "−m·g/k, where the two forces balance — found by setting the "
               "right-hand side to zero, with no solving. Slide k towards "
               "zero and the line runs off the bottom: free fall never "
               "settles.")

    _TLIM = (0.0, 30.0)
    _G = 9.8

    def build_sliders(self) -> None:
        self.add_slider("k", "k  (drag coefficient)", 0.02, 1.5, 0.2,
                        hint="How hard the air pushes back per unit of "
                             "speed. It sets both the terminal velocity and "
                             "how quickly the fall reaches it.")
        self.add_slider("m", "m  (mass)", 0.5, 5.0, 1.0,
                        hint="Heavier falls faster *and* forgets its "
                             "starting speed more slowly: the rate is k/m.")
        self.add_slider("v0", "v(0)", -60.0, 20.0, 0.0)

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "v")

        k, m, v0 = self.value("k"), self.value("m"), self.value("v0")
        terminal = -m * self._G / k
        t = np.linspace(*self._TLIM, 700)
        # The closed form from the derivation: terminal velocity plus a
        # decaying exponential carrying the starting speed.
        velocity = terminal + (v0 - terminal) * np.exp(-k * t / m)

        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        self.plot.addLine(
            y=terminal,
            pen=pg.mkPen(self.palette_obj.warning, width=2, style=Qt.DashLine),
        )
        self.plot.plot(t, velocity, pen=pg.mkPen(self.colour(0), width=3))
        # Free fall, for comparison: the same problem with the drag removed.
        self.plot.plot(t, v0 - self._G * t,
                       pen=pg.mkPen(self.palette_obj.text_muted, width=1,
                                    style=Qt.DotLine))

        self.plot.setYRange(min(terminal * 1.25, -20.0), max(v0 + 5, 5.0),
                            padding=0.02)
        settle = 3 * m / k
        self.readout.setText(
            f"terminal velocity {terminal:.1f} m/s, reached to within 5% by "
            f"t ≈ {settle:.1f}. The dotted line is the same fall with no "
            "drag at all, which is the previous example and never settles."
        )


# ---------------------------------------------------------------------------
# What order buys: the error against the step, on log axes
# ---------------------------------------------------------------------------


class OrderFigure(LessonFigure):
    """Endpoint error against step size for Euler and RK4, log against log.

    The claim "fourth order" is a statement about a slope, and this is that
    slope. Both methods are run through `byhand.refinement` -- the same
    function Methods by Hand tabulates -- and drawn against reference lines of
    gradient 1 and 4. The measured points lie along them, which is the whole
    of what an order means and is far more convincing than a column of
    ratios.
    """

    title = "Order, as a slope"
    caption = ("Error at t = 1 against step size, both axes logarithmic. The "
               "faint lines have gradients 1 and 4. Euler's points lie along "
               "the first and RK4's along the second — halve the step and one "
               "error halves while the other falls by sixteen.")

    _LEVELS = 7

    def build_sliders(self) -> None:
        self.add_slider("a", "a  in  y′ = a·y", -4.0, -0.5, -2.0,
                        hint="The order is a property of the method, not of "
                             "the equation. Change this and the points move "
                             "up or down; the slopes do not change.")

    def _measured(self, method: str):
        a = self.value("a")
        problem = ODEProblem(f=lambda t, y: np.array([a * y[0]]),
                             t_span=(0.0, 1.0), y0=np.array([1.0]))
        rows = byhand.refinement(problem, method, 0.2,
                                 exact=lambda t: np.array([np.exp(a * t)]),
                                 levels=self._LEVELS)
        steps = np.array([row[0] for row in rows])
        errors = np.array([max(row[2], 1e-18) for row in rows])
        return steps, errors

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLogMode(x=True, y=True)
        self.plot.setLabel("bottom", "h")
        self.plot.setLabel("left", "error at t = 1")

        reference = np.array([0.2, 0.2 / 2 ** (self._LEVELS - 1)])
        for order, colour in ((1, 1), (4, 2)):
            steps, errors = self._measured("euler" if order == 1 else "rk4")
            # A reference line of the right gradient, pinned to the first
            # measured point so the comparison is of slope and not of size.
            guide = errors[0] * (reference / steps[0]) ** order
            # Raw values, not logged ones: `setLogMode` takes the logarithm
            # itself, and handing it data already in logs logs it twice --
            # which turns every negative exponent into a NaN.
            self.plot.plot(reference, guide,
                           pen=pg.mkPen(self.palette_obj.text_muted, width=1,
                                        style=Qt.DashLine))
            self.plot.plot(
                steps, errors,
                pen=pg.mkPen(self.colour(colour), width=2),
                symbol="o", symbolSize=8, symbolBrush=self.colour(colour),
            )
        self._describe()

    def _describe(self) -> None:
        words = []
        for name, method in (("Euler", "euler"), ("RK4", "rk4")):
            steps, errors = self._measured(method)
            # The measured order between the last two points, which is where
            # the asymptotic claim is closest to being true.
            slope = (np.log(errors[-2]) - np.log(errors[-1])) / (
                np.log(steps[-2]) - np.log(steps[-1])
            )
            words.append(f"{name}: measured order {slope:.2f}")
        self.readout.setText(
            "  ·  ".join(words) + "  —  read off the last halving, and "
            "approaching 1 and 4 from below as h shrinks."
        )


# ---------------------------------------------------------------------------
# Population: the model that is right for a while, and the one that stays right
# ---------------------------------------------------------------------------


class PopulationFigure(LessonFigure):
    """Exponential against logistic growth, from the same rate and start.

    The lesson's argument is that ``P' = rP`` is not wrong so much as
    *unconditional*: it is the right model while nothing is scarce, and it
    keeps making the same prediction long after that stops being true. Drawn
    from identical r and P(0), the two curves are indistinguishable for a
    while and then are not, and the figure measures where -- the moment the
    two disagree by 10% is a number, and it moves when the carrying capacity
    does.

    The dashed line is K. It is the only thing in the picture the exponential
    model has no opinion about, and it is what decides everything.
    """

    title = "Unbounded growth, and growth with a ceiling"
    caption = ("Both curves start from the same P(0) and grow at the same "
               "rate r. One has nowhere to stop. Watch where they part "
               "company — and note that the logistic curve is steepest at "
               "K/2, not at the beginning.")

    _TLIM = (0.0, 24.0)

    def build_sliders(self) -> None:
        self.add_slider("r", "r  (growth rate)", 0.05, 0.8, 0.3)
        self.add_slider("K", "K  (carrying capacity)", 2.0, 40.0, 20.0,
                        hint="The population the environment supports. The "
                             "exponential model has no such number, which is "
                             "exactly its problem.")
        self.add_slider("P0", "P(0)", 0.2, 10.0, 1.0)

    def _curves(self):
        r, K, start = self.value("r"), self.value("K"), self.value("P0")
        t = np.linspace(*self._TLIM, 1200)
        unbounded = start * np.exp(r * t)
        # The closed form of the logistic equation, which the lesson derives
        # by partial fractions -- not a numerical solve, for the same reason
        # the first-order figures draw their antiderivatives directly.
        logistic = K / (1.0 + (K / start - 1.0) * np.exp(-r * t))
        return t, unbounded, logistic, r, K, start

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "P")

        t, unbounded, logistic, r, K, start = self._curves()
        self.plot.addLine(y=K, pen=pg.mkPen(self.palette_obj.warning, width=2,
                                            style=Qt.DashLine))
        self.plot.plot(t, unbounded,
                       pen=pg.mkPen(self.colour(1), width=2,
                                    style=Qt.DotLine))
        self.plot.plot(t, logistic, pen=pg.mkPen(self.colour(0), width=3))

        # The inflection, where the logistic curve is growing fastest. It is
        # at P = K/2 whatever r and P(0) are, which is the claim.
        half = K / 2.0
        if start < half:
            when = np.log(K / start - 1.0) / r
            if self._TLIM[0] <= when <= self._TLIM[1]:
                self.plot.plot([when], [half], pen=None, symbol="d",
                               symbolSize=12, symbolBrush=None,
                               symbolPen=pg.mkPen(self.palette_obj.accent,
                                                  width=2))
        self.plot.setYRange(0.0, min(3.0 * K, 90.0), padding=0.02)
        self._describe(t, unbounded, logistic, r, K)

    def _describe(self, t, unbounded, logistic, r, K) -> None:
        apart = np.abs(unbounded - logistic) > 0.1 * logistic
        where = float(t[apart][0]) if apart.any() else float("inf")
        parted = (f"they differ by 10% at t = {where:.2f}"
                  if np.isfinite(where) else
                  "they never differ by 10% inside this window")
        self.readout.setText(
            f"doubling time ln2/r = {np.log(2) / r:.2f}; {parted}. The "
            f"logistic curve is steepest at P = K/2 = {K / 2:.1f} and flattens "
            f"onto K = {K:.1f}; the exponential one reaches "
            f"{float(unbounded[-1]):.0f} by t = {self._TLIM[1]:.0f} and is "
            "still accelerating."
        )
