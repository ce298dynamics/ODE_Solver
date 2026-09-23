"""Figures for Linear systems."""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
import sympy as sp
from PySide6.QtCore import Qt

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


# ---------------------------------------------------------------------------
# From one equation to a system: the same motion, drawn in the plane
# ---------------------------------------------------------------------------


class StatePlaneFigure(LessonFigure):
    """``y" + b*y' + c*y = 0`` as a curve in time and as a curve in the plane.

    Rewriting a second-order equation as a pair of first-order ones is
    presented as bookkeeping, and the reader is entitled to ask what it bought.
    This is the answer: the state of the system at an instant is *two*
    numbers, and once they are treated as a point the whole solution is a
    single curve rather than two graphs that have to be read together.

    The two panes are the same solution. Drag the time slider and the marker
    moves along both at once, which is the identification being made -- the
    height of one graph and the slope of the other are the two coordinates of
    the same point.

    The claim worth watching for is that the curve in the plane never crosses
    itself, however long it runs. That is uniqueness again, and in the plane
    it is a statement about the picture rather than a theorem.
    """

    title = "The same motion, as two graphs and as one curve"
    caption = ("Left: y and y′ against time. Right: the point (y, y′) as it "
               "moves. Two numbers say everything about where the system is, "
               "which is exactly what turning one second-order equation into "
               "two first-order ones records.")
    plots = 2

    _T_END = 14.0

    def build_sliders(self) -> None:
        self.add_slider("b", "b  (coefficient of y′)", 0.0, 2.0, 0.4)
        self.add_slider("c", "c  (coefficient of y)", 0.2, 4.0, 2.0)
        self.add_slider("y0", "y(0)", -2.0, 2.0, 1.0)
        self.add_slider("v0", "y′(0)", -2.0, 2.0, 0.0)

    def _trajectory(self):
        b, c = self.value("b"), self.value("c")
        problem = ODEProblem(
            f=lambda t, y: np.array([y[1], -c * y[0] - b * y[1]]),
            t_span=(0.0, self._T_END),
            y0=np.array([self.value("y0"), self.value("v0")]),
        )
        found = solve(problem, method="dopri5", rtol=1e-9, atol=1e-11)
        return found.t, found.y

    def draw(self) -> None:
        times, state = self._trajectory()
        self._draw_time(times, state)
        self._draw_plane(state)
        self._describe(times, state)

    def _draw_time(self, times, state) -> None:
        pane = self.panes[0]
        pane.clear()
        pane.setLabel("bottom", "t")
        pane.setLabel("left", "value")
        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.plot(times, state[0], pen=pg.mkPen(self.colour(0), width=3))
        pane.plot(times, state[1], pen=pg.mkPen(self.colour(1), width=2,
                                                style=Qt.DashLine))
        pane.plot([times[0]], [state[0][0]], pen=None, symbol="o",
                  symbolSize=10, symbolBrush=self.colour(0))
        pane.setYRange(-3.0, 3.0, padding=0.02)

    def _draw_plane(self, state) -> None:
        pane = self.panes[1]
        pane.clear()
        pane.setLabel("bottom", "y")
        pane.setLabel("left", "y′")
        pane.addLine(x=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.plot(state[0], state[1], pen=pg.mkPen(self.colour(0), width=2))
        pane.plot([state[0][0]], [state[1][0]], pen=None, symbol="o",
                  symbolSize=11, symbolBrush=self.colour(0))
        pane.plot([0.0], [0.0], pen=None, symbol="x", symbolSize=12,
                  symbolPen=pg.mkPen(self.palette_obj.text_muted, width=2))
        pane.setXRange(-3.0, 3.0, padding=0.02)
        pane.setYRange(-3.0, 3.0, padding=0.02)

    def _describe(self, times, state) -> None:
        b, c = self.value("b"), self.value("c")
        radius = float(np.hypot(state[0][-1], state[1][-1]))
        started = float(np.hypot(state[0][0], state[1][0]))
        turning = b * b - 4.0 * c
        shape = ("a spiral into the origin" if turning < 0 and b > 1e-9
                 else "a closed loop, returning to where it started"
                 if turning < 0 else "a direct approach to the origin")
        self.readout.setText(
            f"as a system: y₁′ = y₂, y₂′ = −{c:.2f}·y₁ − {b:.2f}·y₂. The "
            f"point starts {started:.3f} from the origin and is "
            f"{radius:.3f} from it at t = {self._T_END:.0f} — {shape}. The "
            "right-hand curve never crosses itself, because one point of the "
            "plane fixes the whole future from it."
        )


# ---------------------------------------------------------------------------
# Eigenvalues: two modes, and which one you are left with
# ---------------------------------------------------------------------------


class EigenModesFigure(LessonFigure):
    """``x' = A x`` with both eigenvalues on sliders, drawn against time.

    `EigenlinesFigure` draws the plane, which is where the eigenvectors live.
    This draws the *modes*, which is where the eigenvalues live, and the two
    facts are genuinely different. An eigenvector says which directions are
    preserved; an eigenvalue says what happens along one, and it is the
    eigenvalue that decides which of the two solutions anybody eventually
    sees.

    The matrix is built from the numbers rather than the numbers read off a
    matrix: A = V diag(L1, L2) V^-1 with fixed eigenvectors (1,1) and (1,-1),
    so the sliders move the eigenvalues directly and the eigenvectors hold
    still. That is the one arrangement in which "the eigenvalue decides" can
    be watched in isolation.

    Set the two eigenvalues to opposite signs and the picture is a saddle
    seen in time: one mode dies, the other takes over, and the answer ends up
    along an eigendirection whatever it started as.
    """

    title = "Two modes, and the one that is left"
    caption = ("Dashed: the two straight-line solutions c₁e^(λ₁t)·v₁ and "
               "c₂e^(λ₂t)·v₂. Solid: their sum, which is the general answer. "
               "The larger eigenvalue owns the end of the story — and if one "
               "is negative and the other positive, that is a saddle, watched "
               "in time rather than in the plane.")

    _T_END = 4.0
    #: The eigenvectors, held fixed so the eigenvalues can be varied alone.
    _V1 = np.array([1.0, 1.0])
    _V2 = np.array([1.0, -1.0])

    def build_sliders(self) -> None:
        self.add_slider("L1", "λ₁  (along (1, 1))", -1.5, 1.5, 0.8)
        self.add_slider("L2", "λ₂  (along (1, −1))", -1.5, 1.5, -1.0)
        self.add_slider("c1", "c₁", -1.5, 1.5, 1.0)
        self.add_slider("c2", "c₂", -1.5, 1.5, 1.0)

    def matrix(self) -> np.ndarray:
        """``A`` itself, so the readout can quote the equation being solved."""
        vectors = np.column_stack([self._V1, self._V2])
        values = np.diag([self.value("L1"), self.value("L2")])
        return vectors @ values @ np.linalg.inv(vectors)

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "x  (first component)")

        t = np.linspace(0.0, self._T_END, 900)
        first = self.value("c1") * np.exp(self.value("L1") * t) * self._V1[0]
        second = self.value("c2") * np.exp(self.value("L2") * t) * self._V2[0]

        self.plot.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        for curve, index in ((first, 1), (second, 2)):
            self.plot.plot(t, curve, pen=pg.mkPen(self.colour(index), width=2,
                                                  style=Qt.DashLine))
        self.plot.plot(t, first + second,
                       pen=pg.mkPen(self.colour(0), width=3))
        self.plot.setYRange(-6.0, 6.0, padding=0.02)
        self._describe(t, first, second)

    def _describe(self, t, first, second) -> None:
        l1, l2 = self.value("L1"), self.value("L2")
        A = self.matrix()
        checked = np.linalg.eigvals(A)
        naming = {
            (True, True): "both eigenvalues negative: every solution goes to "
                          "the origin, a stable node",
            (False, False): "both positive: everything leaves, an unstable "
                            "node",
        }.get((l1 < 0, l2 < 0),
              "opposite signs: a saddle. One mode dies and the other takes "
              "over, so the answer lines up with an eigendirection whatever "
              "it started as")
        bigger = max(l1, l2)
        share = float(
            abs(first[-1] if l1 >= l2 else second[-1])
            / max(abs(first[-1] + second[-1]), 1e-30)
        )
        self.readout.setText(
            f"A = [[{A[0, 0]:.2f}, {A[0, 1]:.2f}], [{A[1, 0]:.2f}, "
            f"{A[1, 1]:.2f}]], whose eigenvalues come back as "
            f"{checked[0].real:+.2f} and {checked[1].real:+.2f}. {naming}. "
            f"By t = {self._T_END:.0f} the mode with λ = {bigger:+.2f} is "
            f"{100 * share:.0f}% of the answer."
        )


# ---------------------------------------------------------------------------
# A repeated eigenvalue: one direction where there should be two
# ---------------------------------------------------------------------------


class DefectiveFigure(LessonFigure):
    """``x' = [[L, 1], [0, L]] x``, which has one eigendirection and needs two.

    Every other case in the unit produces two independent straight-line
    solutions and the general answer is a combination of them. This matrix
    produces one. The left pane is that fact: the field has a single line
    through the origin that trajectories stay on, and there is no second one
    anywhere, however long you look.

    What fills the gap is t*e^(L t)*v, and the right pane is why that shape
    and not another. A factor of t does not change where the solution ends up
    -- the exponential still decides that -- but it delays it, which is the
    bulge every defective solution has and no other case does. Set L negative
    and watch the curve rise before it falls: nothing in the eigenvalue
    predicts that hump, and the missing eigenvector is what puts it there.
    """

    title = "One eigendirection, and the t that makes up the difference"
    caption = ("Left: the field of x′ = [[λ, 1], [0, λ]]·x. There is exactly "
               "one line through the origin that trajectories stay on. "
               "Right: the second solution t·e^(λt), which is what being an "
               "eigenvector short of a basis costs — a hump, then the same "
               "fate the exponential always had.")
    plots = 2

    _LIM = 2.5
    _T_END = 9.0

    def build_sliders(self) -> None:
        self.add_slider("L", "λ  (the repeated eigenvalue)",
                        -1.2, 0.6, -0.5,
                        hint="Repeated, so there is one eigenvalue and one "
                             "eigendirection. Its sign still decides where "
                             "everything ends up.")
        self.add_slider("c2", "c₂  (weight on the t·e^(λt) solution)",
                        0.0, 2.0, 1.0)

    def draw(self) -> None:
        self._draw_plane()
        self._draw_solutions()
        self._describe()

    def _draw_plane(self) -> None:
        pane = self.panes[0]
        pane.clear()
        pane.setLabel("bottom", "x")
        pane.setLabel("left", "y")
        value = self.value("L")

        grid = np.linspace(-self._LIM, self._LIM, 13)
        length = 2 * self._LIM / 13 * 0.42
        for x in grid:
            for y in grid:
                vx, vy = value * x + y, value * y
                norm = float(np.hypot(vx, vy))
                if norm < 1e-9:
                    continue
                dx, dy = vx / norm * length, vy / norm * length
                pane.plot([x - dx / 2, x + dx / 2], [y - dy / 2, y + dy / 2],
                          pen=pg.mkPen(self.palette_obj.text_muted, width=1))

        # The only eigendirection: (1, 0), from (A - L I)v = 0.
        colour = (self.palette_obj.success if value < 0
                  else self.palette_obj.danger)
        pane.plot([-self._LIM * 1.5, self._LIM * 1.5], [0.0, 0.0],
                  pen=pg.mkPen(colour, width=3))
        for start in ((1.0, 1.2), (-1.0, -1.2), (1.6, -0.6), (-1.6, 0.6)):
            self._draw_curve(pane, start)
        pane.setXRange(-self._LIM, self._LIM, padding=0.02)
        pane.setYRange(-self._LIM, self._LIM, padding=0.02)

    def _draw_curve(self, pane, start) -> None:
        value = self.value("L")
        x0, y0 = start
        # The closed form of the defective system: y = y0 e^(Lt) and
        # x = (x0 + y0 t) e^(Lt). Written out, because the t is the subject.
        t = np.linspace(0.0, 6.0, 400)
        decay = np.exp(value * t)
        xs, ys = (x0 + y0 * t) * decay, y0 * decay
        inside = (np.abs(xs) <= self._LIM * 1.4) & (np.abs(ys) <= self._LIM * 1.4)
        if inside.any():
            pane.plot(xs[inside], ys[inside],
                      pen=pg.mkPen(self.colour(0), width=2))

    def _draw_solutions(self) -> None:
        pane = self.panes[1]
        pane.clear()
        pane.setLabel("bottom", "t")
        pane.setLabel("left", "first component")
        value, weight = self.value("L"), self.value("c2")
        t = np.linspace(0.0, self._T_END, 900)
        plain = np.exp(value * t)
        delayed = weight * t * np.exp(value * t)

        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.plot(t, plain, pen=pg.mkPen(self.colour(1), width=2,
                                         style=Qt.DashLine))
        pane.plot(t, delayed, pen=pg.mkPen(self.colour(2), width=2,
                                           style=Qt.DotLine))
        pane.plot(t, plain + delayed, pen=pg.mkPen(self.colour(0), width=3))
        pane.setYRange(-0.5, 3.0, padding=0.02)

    def _describe(self) -> None:
        value, weight = self.value("L"), self.value("c2")
        if weight <= 1e-9:
            hump = ("with c2 at zero there is only the one solution, which is "
                    "the whole problem: a single eigenvector cannot span a "
                    "two-dimensional space")
        elif value < -1e-9:
            # Two different peaks, and they are not the same number: the
            # t*e^(Lt) term alone turns at t = -1/lambda, while the drawn sum
            # turns wherever c2 puts it. Printing one of them as the other is
            # the sort of near-miss a reader would check and find wrong, so
            # the sum's peak is measured off the samples and the term's is
            # quoted from the formula, each labelled as what it is.
            t = np.linspace(0.0, self._T_END, 900)
            drawn = float(t[np.argmax(np.exp(value * t)
                                      + weight * t * np.exp(value * t))])
            hump = (f"the answer rises to a peak at t = {drawn:.2f} before "
                    f"it decays, which nothing in the eigenvalue predicts. "
                    f"The t·e^(λt) term on its own turns at t = −1/λ = "
                    f"{-1 / value:.2f}")
        else:
            hump = ("with λ positive nothing decays and the t merely makes "
                    "the growth faster still")
        self.readout.setText(
            f"λ = {value:.2f}, repeated. (A − λI) has rank 1, so there is one "
            f"eigenvector, (1, 0), and one straight-line solution; {hump}."
        )


# ---------------------------------------------------------------------------
# Forcing a system: the part that is forgotten, and the part that is not
# ---------------------------------------------------------------------------


class ForcedSystemFigure(LessonFigure):
    """``x' = A x + f(t)`` for a stable A and a periodic f.

    The structure theorem for systems is the same one as for a single
    equation -- a particular solution plus the homogeneous family -- and it
    has the same consequence, which is easier to see in the plane than
    anywhere else. Whatever the system starts at, it ends on one closed loop,
    and that loop is the particular solution. The homogeneous part is the
    distance from it, and it is gone.

    Three starting points are drawn at once, because one would leave open
    whether the loop was a property of the start. They spiral in from
    different places onto the same curve, which is the claim: the initial
    conditions are forgotten, and the forcing is not.
    """

    title = "Three starts, one steady loop"
    caption = ("x′ = Ax + (cos ωt, 0), with A stable. Three different "
               "initial conditions, all spiralling onto the same closed "
               "curve. That curve is the particular solution; everything "
               "that distinguished the three starts was homogeneous, and it "
               "decayed.")
    plots = 2

    _T_END = 60.0
    _STARTS = ((2.2, 0.0), (-1.8, 1.4), (0.3, -2.2))

    def build_sliders(self) -> None:
        self.add_slider("d", "damping in A", 0.05, 0.8, 0.25,
                        hint="How fast the homogeneous part is forgotten. "
                             "Small and the transient is still visible at "
                             "the end of the window.")
        self.add_slider("w", "ω  (forcing frequency)", 0.3, 2.5, 0.8)
        self.add_slider("F", "forcing amplitude", 0.0, 2.0, 1.0)

    def _run(self, start):
        damping, omega, amplitude = (self.value("d"), self.value("w"),
                                     self.value("F"))

        def field(t, y):
            return np.array([
                y[1],
                -y[0] - 2.0 * damping * y[1] + amplitude * np.cos(omega * t),
            ])

        problem = ODEProblem(f=field, t_span=(0.0, self._T_END),
                             y0=np.array(start, dtype=float))
        found = solve(problem, method="dopri5", rtol=1e-9, atol=1e-11)
        return found.t, found.y

    def draw(self) -> None:
        runs = [self._run(start) for start in self._STARTS]
        self._draw_time(runs[0])
        self._draw_plane(runs)
        self._describe(runs)

    def _draw_time(self, run) -> None:
        pane = self.panes[0]
        pane.clear()
        pane.setLabel("bottom", "t")
        pane.setLabel("left", "x")
        times, state = run
        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.plot(times, state[0], pen=pg.mkPen(self.colour(0), width=2))
        pane.setYRange(-3.0, 3.0, padding=0.02)

    def _draw_plane(self, runs) -> None:
        pane = self.panes[1]
        pane.clear()
        pane.setLabel("bottom", "x")
        pane.setLabel("left", "x′")
        pane.addLine(x=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        for index, (times, state) in enumerate(runs):
            pane.plot(state[0], state[1],
                      pen=pg.mkPen(self.colour(index + 1), width=1))
            pane.plot([state[0][0]], [state[1][0]], pen=None, symbol="o",
                      symbolSize=9, symbolBrush=self.colour(index + 1))
            # The last fifth, drawn heavily: that is the steady loop, and it
            # is the same curve for all three however different the starts.
            late = times > self._T_END * 0.8
            pane.plot(state[0][late], state[1][late],
                      pen=pg.mkPen(self.colour(0), width=3))
        pane.setXRange(-3.0, 3.0, padding=0.02)
        pane.setYRange(-3.0, 3.0, padding=0.02)

    def _describe(self, runs) -> None:
        # How far apart the three trajectories still are at the end. The
        # claim is that they converge, so the number that matters is this
        # one, not the shape of any of them.
        endings = np.array([state[:, -1] for _, state in runs])
        spread = float(np.max(np.linalg.norm(
            endings[:, None, :] - endings[None, :, :], axis=-1
        )))
        started = np.array(self._STARTS, dtype=float)
        apart = float(np.max(np.linalg.norm(
            started[:, None, :] - started[None, :, :], axis=-1
        )))
        self.readout.setText(
            f"the three starts are up to {apart:.2f} apart; at "
            f"t = {self._T_END:.0f} the three states are {spread:.2e} apart. "
            "Everything that told them apart was homogeneous. What is left "
            "is the particular solution, and it belongs to the forcing."
        )
