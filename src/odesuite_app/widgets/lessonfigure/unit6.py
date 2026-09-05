"""Figures for Linear systems."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
import sympy as sp

from odesuite import ODEProblem, solve

from ... import systems
from .base import LessonFigure

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


# ---------------------------------------------------------------------------
# Complex eigenvalues: the two parts of the root, drawn as one picture
# ---------------------------------------------------------------------------


class SpiralFigure(LessonFigure):
    """Trajectories of a rotation-and-scaling matrix, with both parts on
    sliders.

    The derivation's last two passages say the imaginary part of the
    eigenvalue turns the solution round the origin and the real part scales
    it, so the sign of the real part alone decides inward, closed or outward.
    Both are sliders. Cross zero with the first and every trajectory changes
    character at once; change the second and only the rate of turning does.
    """

    title = "In, round, or out — decided by the real part"
    caption = ("Trajectories of x′ = αx − βy, y′ = βx + αy, whose eigenvalues "
               "are α ± βi. The real part scales and the imaginary part "
               "turns, so α < 0 spirals in, α = 0 closes into circles, and "
               "α > 0 spirals out. β changes how fast it goes round and "
               "nothing else.")

    _SPAN = 3.0
    _STARTS = ((1.0, 0.0), (0.0, 1.4), (-1.9, 0.0), (0.0, -2.4), (1.9, 1.9))

    def build_sliders(self) -> None:
        self.add_slider("alpha", "α  (real part)", -0.6, 0.6, -0.25,
                        hint="The envelope. Negative pulls every trajectory "
                             "into the origin; zero leaves closed loops; "
                             "positive drives them out.")
        self.add_slider("beta", "β  (imaginary part)", 0.3, 3.0, 1.5,
                        hint="How fast the rotation goes round. It never "
                             "decides whether the spiral comes in or goes "
                             "out.")

    def _trajectory(self, start):
        alpha, beta = self.value("alpha"), self.value("beta")
        problem = ODEProblem(
            f=lambda t, v: np.array([alpha * v[0] - beta * v[1],
                                     beta * v[0] + alpha * v[1]]),
            t_span=(0.0, 14.0),
            y0=np.array([float(start[0]), float(start[1])]),
        )
        try:
            found = solve(problem, method="dopri5", rtol=1e-8, atol=1e-10)
        except Exception:
            return None
        return (found.y[0], found.y[1]) if found.t.size else None

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "x")
        self.plot.setLabel("left", "y")
        self.plot.setXRange(-self._SPAN, self._SPAN, padding=0.02)
        self.plot.setYRange(-self._SPAN, self._SPAN, padding=0.02)
        self.plot.addLine(x=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))

        for index, start in enumerate(self._STARTS):
            curve = self._trajectory(start)
            if curve is None:
                continue
            self.plot.plot(curve[0], curve[1],
                           pen=pg.mkPen(self.colour(index), width=2))
            self.plot.plot([start[0]], [start[1]], pen=None, symbol="o",
                           symbolSize=8, symbolBrush=self.colour(index))

        # The origin is the only place nothing moves, unless the matrix is
        # singular -- and this one never is while beta is non-zero.
        self.plot.plot([0.0], [0.0], pen=None, symbol="o", symbolSize=10,
                       symbolPen=pg.mkPen(self.palette_obj.text_muted,
                                          width=2),
                       symbolBrush=None)
        self._describe()

    def _describe(self) -> None:
        alpha, beta = self.value("alpha"), self.value("beta")
        if abs(alpha) < 1e-3:
            what = "closed loops: nothing grows or decays"
        elif alpha < 0:
            what = f"a stable spiral, its radius decaying at {abs(alpha):.2f}"
        else:
            what = f"an unstable spiral, its radius growing at {alpha:.2f}"
        period = 2 * np.pi / beta
        self.readout.setText(
            f"eigenvalues {alpha:.2f} ± {beta:.2f}i — {what}, going round "
            f"once every {period:.1f} time units. Same numbers as the "
            "underdamped spring, drawn in the plane rather than against time."
        )
