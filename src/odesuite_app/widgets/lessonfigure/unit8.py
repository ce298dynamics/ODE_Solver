"""Figures for Nonlinear systems.

Every number these print is measured from the flow they draw, never taken
from the formula the lesson derives -- the angle between the nonlinear field
and its linearisation, the radius a trajectory settles at, the energy a
damped pendulum has left. The lesson states the claim; the figure checks it
where the reader can watch, which is the only reason to have both.

The equilibria, their names, the separatrices and the phase lines come from
`analysis`, the module behind the Phase Portrait screen, so a figure here and
the screen a lesson sends the reader to cannot describe the same system
differently.
"""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt

from odesuite import ODEProblem, solve

from ... import analysis
from .base import LessonFigure

__all__ = [
    "LinearisationFigure",
    "AlmostLinearFigure",
    "CompetitionFigure",
    "PendulumEnergyFigure",
    "LimitCycleFigure",
    "NormalFormsFigure",
]


def _planar(f) -> ODEProblem:
    return ODEProblem(f=f, t_span=(0.0, 1.0), y0=np.array([0.1, 0.1]))


def _dashes(plot, problem: ODEProblem, xlim, ylim, colour: str, *,
            count: int = 15, width: float = 1.0, skip=None) -> None:
    """The direction field as equal-length dashes, drawn as one item.

    One `PlotDataItem` with ``connect="pairs"`` rather than a plot call per
    dash: a 15x15 field is 225 items the other way, and these figures redraw
    on every slider tick.
    """
    xs = np.linspace(xlim[0], xlim[1], count)
    ys = np.linspace(ylim[0], ylim[1], count)
    length = 0.42 * min(xlim[1] - xlim[0], ylim[1] - ylim[0]) / count
    points = []
    for x in xs:
        for y in ys:
            if skip is not None and skip(x, y):
                continue
            vx, vy = problem.f(0.0, np.array([x, y]))
            norm = float(np.hypot(vx, vy))
            if not np.isfinite(norm) or norm < 1e-12:
                continue
            dx, dy = vx / norm * length, vy / norm * length
            points += [(x - dx / 2, y - dy / 2), (x + dx / 2, y + dy / 2)]
    if points:
        data = np.asarray(points)
        plot.plot(data[:, 0], data[:, 1], connect="pairs",
                  pen=pg.mkPen(colour, width=width))


def _trajectory(f, start, t_end: float, *, rtol: float = 1e-7,
                bound: float | None = None) -> np.ndarray:
    """``(2, m)`` points of the trajectory from `start`, cut where it leaves.

    Integrated in short pieces so a trajectory that runs away -- the
    almost-linear spiral blows up in finite time -- is stopped at `bound`
    rather than handed to the solver to fail on.
    """
    pieces, t, y = [], 0.0, np.asarray(start, dtype=float)
    piece = 1.0 if bound is not None else t_end
    while t < t_end - 1e-12:
        span = min(piece, t_end - t)
        try:
            found = solve(ODEProblem(f=f, t_span=(t, t + span), y0=y),
                          method="dopri5", rtol=rtol, atol=rtol * 1e-3,
                          dense_output=True)
        except Exception:
            break
        if not found.success or found.sol is None:
            break
        grid = np.linspace(t, t + span, max(60, int(40 * span)))
        values = found.sol(grid)
        pieces.append(values)
        y = values[:, -1]
        t += span
        if bound is not None and float(np.hypot(*y)) > bound:
            break
    if not pieces:
        return np.empty((2, 0))
    return np.concatenate(pieces, axis=1)


def _marker(plot, point, stability: str, palette) -> None:
    stable = stability == analysis.STABLE
    colour = (palette.success if stable else
              palette.danger if stability == analysis.UNSTABLE else palette.warning)
    plot.plot([float(point[0])], [float(point[1])], pen=None, symbol="o",
              symbolSize=11, symbolPen=pg.mkPen(colour, width=2),
              symbolBrush=colour if stable else None)


def _a(noun: str) -> str:
    """With its article: a saddle, an unstable spiral."""
    return ("an " if noun[:1].lower() in "aeiou" else "a ") + noun


def _eigen_words(values) -> str:
    values = np.asarray(values)
    if np.all(np.abs(values.imag) < 1e-9):
        return ", ".join(f"{v.real:+.3f}" for v in values)
    return f"{values[0].real:+.3f} ± {abs(values[0].imag):.3f}i"


# ---------------------------------------------------------------------------
# Linearisation: zoom in and the flow straightens out
# ---------------------------------------------------------------------------


class LinearisationFigure(LessonFigure):
    """The pendulum's field beside its linearisation, as the window shrinks.

    The claim of linearisation is a limit: close enough to the equilibrium,
    the nonlinear field and the Jacobian's field point the same way. So the
    readout is the *largest angle between them* over the window drawn, which
    falls towards zero as the window is shrunk -- measured on the grid, not
    asserted -- and grows as it widens until the two pictures stop agreeing.
    """

    title = "Zoom in, and the flow becomes linear"
    caption = ("The pendulum's direction field (grey) and the field of its "
               "linearisation at the chosen equilibrium (coloured), drawn at "
               "the same points. Shrink the window and they line up; widen it "
               "and the nonlinearity shows. The readout is the worst "
               "disagreement between them in degrees.")

    def build_sliders(self) -> None:
        self.add_slider("window", "window half-width", 0.05, 3.0, 1.5, log=True)
        self.add_slider("damping", "c  (damping)", 0.0, 1.0, 0.3)
        self.add_slider("which", "equilibrium  (0 hanging, 1 inverted)", 0.0, 1.0,
                        0.0, hint="The hanging rest state at x = 0 or the "
                                  "balanced one at x = π.")

    def _parts(self):
        c = self.value("damping")
        centre = np.pi if self.value("which") >= 0.5 else 0.0

        def f(t, y):
            return np.array([y[1], -np.sin(y[0]) - c * y[1]])

        problem = _planar(f)
        point = np.array([centre, 0.0])
        jacobian = analysis.jacobian_at(problem, point)
        linear = _planar(lambda t, y: jacobian @ (y - point))
        return problem, linear, point, jacobian

    def worst_angle(self) -> float:
        """Degrees: the largest angle between the two fields over the window."""
        problem, linear, point, _ = self._parts()
        half = self.value("window")
        worst = 0.0
        for dx in np.linspace(-half, half, 15):
            for dy in np.linspace(-half, half, 15):
                if abs(dx) < 1e-12 and abs(dy) < 1e-12:
                    continue
                here = point + np.array([dx, dy])
                a, b = problem.f(0.0, here), linear.f(0.0, here)
                na, nb = np.linalg.norm(a), np.linalg.norm(b)
                if na < 1e-14 or nb < 1e-14:
                    continue
                cosine = float(np.clip(a @ b / (na * nb), -1.0, 1.0))
                worst = max(worst, float(np.degrees(np.arccos(cosine))))
        return worst

    def draw(self) -> None:
        self.plot.clear()
        problem, linear, point, jacobian = self._parts()
        half = self.value("window")
        xlim = (point[0] - half, point[0] + half)
        ylim = (point[1] - half, point[1] + half)
        self.plot.setLabel("bottom", "x  (angle)")
        self.plot.setLabel("left", "y  (angular velocity)")
        self.plot.setXRange(*xlim, padding=0.02)
        self.plot.setYRange(*ylim, padding=0.02)

        _dashes(self.plot, problem, xlim, ylim, self.palette_obj.text_muted,
                width=2.4)
        _dashes(self.plot, linear, xlim, ylim, self.colour(0), width=1.3)

        values = np.linalg.eigvals(jacobian)
        kind, stability = analysis.classify(values)
        _marker(self.plot, point, stability, self.palette_obj)
        name = "inverted" if point[0] > 1.0 else "hanging"
        self.readout.setText(
            f"{name} equilibrium ({point[0]:.3f}, 0): Jacobian eigenvalues "
            f"{_eigen_words(values)} — the linearisation is {_a(kind)}. "
            f"Worst angle between the two fields in this window: "
            f"{self.worst_angle():.2f}°."
        )


# ---------------------------------------------------------------------------
# Almost linear: the centre the linearisation cannot decide
# ---------------------------------------------------------------------------


class AlmostLinearFigure(LessonFigure):
    """``x' = -y + a·x·r²,  y' = x + a·y·r²`` -- a centre, linearly, for every a.

    The Jacobian at the origin is the same rotation whatever `a` is, so the
    linearisation calls it a centre every time. The trajectory disagrees:
    outward for a > 0, inward for a < 0, closed only at a = 0 exactly. The
    readout measures the radius after a fixed time from a fixed start, and
    names what the linearisation says beside it, so the disagreement is two
    numbers on the same line.
    """

    title = "A centre the linearisation cannot vouch for"
    caption = ("Every value of a gives the same linearisation at the origin — "
               "a pure rotation, a centre. Slide a away from zero and the real "
               "trajectory spirals out or in, which the linear part cannot "
               "see: the cubic terms decide.")

    _LIM = 1.5
    _START = (0.5, 0.0)
    _TIME = 18.0

    def build_sliders(self) -> None:
        self.add_slider("a", "a  (strength of the cubic term)", -0.3, 0.3, 0.1)

    def a(self) -> float:
        # Snapped, because the subject is a boundary: a slider quantised to a
        # thousand steps never lands on 0.000 exactly, and a = 0 is the one
        # value where the centre is real.
        value = self.value("a")
        return 0.0 if abs(value) < 0.006 else value

    def _f(self):
        a = self.a()

        def f(t, y):
            r2 = y[0] ** 2 + y[1] ** 2
            return np.array([-y[1] + a * y[0] * r2, y[0] + a * y[1] * r2])

        return f

    def final_radius(self) -> float:
        path = _trajectory(self._f(), self._START, self._TIME, bound=3.0)
        return float(np.hypot(*path[:, -1])) if path.size else float("nan")

    def draw(self) -> None:
        self.plot.clear()
        lim = self._LIM
        self.plot.setLabel("bottom", "x")
        self.plot.setLabel("left", "y")
        self.plot.setXRange(-lim, lim, padding=0.02)
        self.plot.setYRange(-lim, lim, padding=0.02)
        # A circle has to look like one: the claim is a radius.
        self.plot.setAspectLocked(True)
        f = self._f()
        problem = _planar(f)
        _dashes(self.plot, problem, (-lim, lim), (-lim, lim),
                self.palette_obj.text_muted)

        path = _trajectory(f, self._START, self._TIME, bound=3.0)
        inside = np.all(np.abs(path) <= lim * 1.2, axis=0)
        if inside.any():
            self.plot.plot(path[0, inside], path[1, inside],
                           pen=pg.mkPen(self.colour(0), width=2.2))
        values = np.linalg.eigvals(analysis.jacobian_at(problem, np.zeros(2)))
        kind, stability = analysis.classify(values)
        _marker(self.plot, (0.0, 0.0), stability, self.palette_obj)

        start = float(np.hypot(*self._START))
        end = float(np.hypot(*path[:, -1])) if path.size else float("nan")
        if not np.isfinite(end) or end > 1.02 * start:
            real = "spirals outwards"
        elif end < 0.98 * start:
            real = "spirals inwards"
        else:
            real = "closes up — a genuine centre"
        self.readout.setText(
            f"a = {self.a():+.3f}.  Linearisation: eigenvalues "
            f"{_eigen_words(values)}, {_a(kind)}.  The trajectory from r = "
            f"{start:.2f}: r = {end:.3f} after t = {self._TIME:g} — it {real}."
        )


# ---------------------------------------------------------------------------
# Competition: nullclines decide who survives
# ---------------------------------------------------------------------------


class CompetitionFigure(LessonFigure):
    """Two competing species, ``x' = x(1 - x - a y),  y' = y(1 - y - b x)``.

    Scaled so each species alone settles at 1, which leaves the two
    competition coefficients as the only thing that matters. The nullclines
    are drawn from `analysis.nullclines`, the equilibria found and named by
    `analysis.find_fixed_points`, and the verdict in the readout is read off
    the named interior equilibrium rather than off the textbook condition
    a < 1, b < 1 -- which it then agrees with.
    """

    title = "Competition, and where the nullclines cross"
    caption = ("Dashed lines are the nullclines: on one x stops changing, on "
               "the other y does. Equilibria sit where an x-nullcline meets a "
               "y-nullcline. When each species holds the other back less than "
               "it holds itself back the lines cross inside the quadrant and "
               "both survive; otherwise one is driven out.")

    _XLIM = (-0.05, 1.3)
    _YLIM = (-0.05, 1.3)

    def build_sliders(self) -> None:
        self.add_slider("a", "a  (y's effect on x)", 0.2, 2.0, 0.5)
        self.add_slider("b", "b  (x's effect on y)", 0.2, 2.0, 0.5)

    def _problem(self) -> ODEProblem:
        a, b = self.value("a"), self.value("b")
        return _planar(lambda t, y: np.array([y[0] * (1 - y[0] - a * y[1]),
                                              y[1] * (1 - y[1] - b * y[0])]))

    def equilibria(self):
        return analysis.find_fixed_points(self._problem(), self._XLIM, self._YLIM,
                                          seeds=9)

    def verdict(self, found=None) -> str:
        found = self.equilibria() if found is None else found
        interior = [p for p in found
                    if p.position[0] > 1e-6 and p.position[1] > 1e-6]
        if not interior:
            wins = [p for p in found if p.stability == analysis.STABLE]
            if len(wins) == 1:
                who = "x" if wins[0].position[0] > 0.5 else "y"
                return f"no coexistence equilibrium: {who} drives the other out"
            return "no coexistence equilibrium"
        point = interior[0]
        where = f"({point.position[0]:.3f}, {point.position[1]:.3f})"
        if point.stability == analysis.STABLE:
            return f"coexistence at {where}, {_a(point.kind)}: both survive"
        return (f"coexistence point {where} is {_a(point.kind)}: which species "
                "survives depends on where you start")

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "x  (species 1)")
        self.plot.setLabel("left", "y  (species 2)")
        self.plot.setXRange(*self._XLIM, padding=0.02)
        self.plot.setYRange(*self._YLIM, padding=0.02)
        problem = self._problem()
        _dashes(self.plot, problem, self._XLIM, self._YLIM,
                self.palette_obj.text_muted, count=13)

        for index, paths in enumerate(analysis.nullclines(problem, self._XLIM,
                                                          self._YLIM)):
            for path in paths:
                self.plot.plot(path[:, 0], path[:, 1],
                               pen=pg.mkPen(self.colour(index), width=1.8,
                                            style=Qt.DashLine))

        f = problem.f_user
        for index, start in enumerate(((0.1, 0.9), (0.9, 0.1), (0.05, 0.05),
                                       (1.2, 1.2))):
            path = _trajectory(f, start, 25.0, rtol=1e-5)
            if path.size:
                self.plot.plot(path[0], path[1],
                               pen=pg.mkPen(self.colour(index + 3), width=1.8))

        found = self.equilibria()
        for point in found:
            _marker(self.plot, point.position, point.stability, self.palette_obj)
        self.readout.setText(
            f"a = {self.value('a'):.2f}, b = {self.value('b'):.2f}: "
            f"{self.verdict(found)}."
        )


# ---------------------------------------------------------------------------
# The pendulum: energy, the separatrix, and what damping takes away
# ---------------------------------------------------------------------------


class PendulumEnergyFigure(LessonFigure):
    """``x'' + c x' + sin x = 0`` in the phase plane, with its energy measured.

    Undamped, every orbit is a level curve of E = y²/2 − cos x, and the
    separatrices -- computed by `analysis.separatrices` from the saddles at
    ±π -- divide swinging from going over the top. The launched trajectory's
    energy is measured at its start and end, so the readout shows it
    conserved at c = 0 (to the integrator's tolerance) and draining away
    otherwise.
    """

    title = "The pendulum: energy and the separatrix"
    caption = ("Grey curves are orbits of the undamped pendulum — curves of "
               "constant energy — and the heavy ones are the separatrices "
               "through the inverted positions. The coloured trajectory starts "
               "at the bottom with the speed you choose. Add damping and it "
               "crosses the energy curves inwards.")

    _XLIM = (-2 * np.pi - 0.4, 2 * np.pi + 0.4)
    _YLIM = (-3.2, 3.2)
    _TIME = 30.0

    def __init__(self, palette, parent=None) -> None:
        self._background = None
        super().__init__(palette, parent)

    def build_sliders(self) -> None:
        self.add_slider("speed", "starting speed at the bottom", 0.4, 2.8, 1.5)
        self.add_slider("damping", "c  (damping)", 0.0, 0.6, 0.0)

    def damping(self) -> float:
        value = self.value("damping")
        return 0.0 if value < 0.004 else value

    @staticmethod
    def energy(x, y):
        return 0.5 * np.asarray(y) ** 2 - np.cos(x)

    def _undamped(self):
        """The background: orbits, separatrices and equilibria at c = 0.

        None of it depends on a slider, and it is most of the cost of a
        redraw, so it is computed once.
        """
        if self._background is None:
            undamped = _planar(lambda t, y: np.array([y[1], -np.sin(y[0])]))
            orbits = []
            for speed in (0.6, 1.2, 1.7, 2.3, 2.7):
                for sign in (1.0, -1.0):
                    # An orbit that goes over the top starts a full turn back,
                    # where cos x -- and so the energy -- is the same, so it
                    # crosses the whole window rather than half of it.
                    x0 = -sign * 2 * np.pi if speed > 2.0 else 0.0
                    path = _trajectory(undamped.f_user, (x0, sign * speed), 9.0,
                                       rtol=1e-8)
                    if path.size:
                        orbits.append(path)
            points = analysis.find_fixed_points(undamped, self._XLIM, self._YLIM,
                                                seeds=9)
            manifolds = []
            for point in points:
                if point.kind != "saddle":
                    continue
                # Leaving a saddle from 1e-4 away takes about ln(1e4) = 9.2
                # time units, so a shorter span draws a stub -- which the
                # first version of this figure did, at 8.
                for curve, _ in analysis.separatrices(undamped, point, span=16.0):
                    manifolds += analysis.clip_to_window(curve, self._XLIM,
                                                         self._YLIM)
            self._background = (orbits, manifolds, points)
        return self._background

    def launched(self) -> np.ndarray:
        c = self.damping()
        return _trajectory(lambda t, y: np.array([y[1], -np.sin(y[0]) - c * y[1]]),
                           (0.0, self.value("speed")), self._TIME, rtol=1e-9)

    def draw(self) -> None:
        self.plot.clear()
        self.plot.setLabel("bottom", "x  (angle)")
        self.plot.setLabel("left", "y  (angular velocity)")
        self.plot.setXRange(*self._XLIM, padding=0.02)
        self.plot.setYRange(*self._YLIM, padding=0.02)

        orbits, manifolds, points = self._undamped()
        for path in orbits:
            self.plot.plot(path[0], path[1],
                           pen=pg.mkPen(self.palette_obj.text_muted, width=1))
        for piece in manifolds:
            self.plot.plot(piece[:, 0], piece[:, 1],
                           pen=pg.mkPen(self.palette_obj.warning, width=2.2))
        for point in points:
            _marker(self.plot, point.position, point.stability, self.palette_obj)

        path = self.launched()
        if path.size:
            self.plot.plot(path[0], path[1], pen=pg.mkPen(self.colour(0), width=2.4))
        start = float(self.energy(0.0, self.value("speed")))
        end = float(self.energy(path[0, -1], path[1, -1])) if path.size else start
        over = bool(path.size and np.max(np.abs(path[0])) > np.pi)
        self.readout.setText(
            f"c = {self.damping():.3f}.  Energy at the start {start:+.4f}, "
            f"after t = {self._TIME:g} {end:+.4f}.  "
            + ("It goes over the top." if over else "It swings without going over.")
            + ("  (Over the top needs E > 1: a starting speed above 2.)"
               if self.damping() == 0.0 else "")
        )


# ---------------------------------------------------------------------------
# A limit cycle is born
# ---------------------------------------------------------------------------


class LimitCycleFigure(LessonFigure):
    """The Hopf normal form, ``r' = r(μ − r²)``, drawn in the plane.

    One trajectory starts near the origin and one far outside. For μ > 0
    both end on the same circle, from opposite sides -- that is what makes it
    a *limit* cycle -- and the readout prints both measured radii beside
    √μ. For μ ≤ 0 both fall into the origin and there is no cycle at all.
    """

    title = "A limit cycle, approached from both sides"
    caption = ("A trajectory from just outside the origin and one from far "
               "out. When μ is positive they wind onto the same closed orbit, "
               "one growing and one shrinking — nearby orbits converge to it, "
               "which is what a limit cycle is. Take μ below zero and the "
               "cycle is gone.")

    _LIM = 1.7
    _TIME = 40.0

    def build_sliders(self) -> None:
        self.add_slider("mu", "μ", -0.5, 1.2, 0.5)

    def _f(self):
        mu = self.value("mu")

        def f(t, y):
            r2 = y[0] ** 2 + y[1] ** 2
            return np.array([mu * y[0] - y[1] - y[0] * r2,
                             y[0] + mu * y[1] - y[1] * r2])

        return f

    def final_radii(self) -> tuple[float, float]:
        f = self._f()
        radii = []
        for start in ((0.05, 0.0), (1.6, 0.0)):
            path = _trajectory(f, start, self._TIME, rtol=1e-8)
            radii.append(float(np.hypot(*path[:, -1])) if path.size else float("nan"))
        return radii[0], radii[1]

    def draw(self) -> None:
        self.plot.clear()
        lim = self._LIM
        self.plot.setLabel("bottom", "x")
        self.plot.setLabel("left", "y")
        self.plot.setXRange(-lim, lim, padding=0.02)
        self.plot.setYRange(-lim, lim, padding=0.02)
        # A circle has to look like one: the claim is a radius.
        self.plot.setAspectLocked(True)
        f = self._f()
        problem = _planar(f)
        _dashes(self.plot, problem, (-lim, lim), (-lim, lim),
                self.palette_obj.text_muted)
        radii = []
        for index, start in enumerate(((0.05, 0.0), (1.6, 0.0))):
            path = _trajectory(f, start, self._TIME, rtol=1e-7)
            if path.size:
                self.plot.plot(path[0], path[1],
                               pen=pg.mkPen(self.colour(index), width=2))
            radii.append(float(np.hypot(*path[:, -1])) if path.size
                         else float("nan"))
        values = np.linalg.eigvals(analysis.jacobian_at(problem, np.zeros(2)))
        kind, stability = analysis.classify(values)
        _marker(self.plot, (0.0, 0.0), stability, self.palette_obj)

        inner, outer = radii
        mu = self.value("mu")
        if mu > 0:
            words = (f"both end at r ≈ {inner:.3f} and {outer:.3f}, "
                     f"against √μ = {np.sqrt(mu):.3f}")
        else:
            words = f"both fall inwards (r = {inner:.3f}, {outer:.3f}): no cycle"
        self.readout.setText(
            f"μ = {mu:+.3f}.  Origin: eigenvalues {_eigen_words(values)}, "
            f"{_a(kind)}.  Trajectories: {words}."
        )


# ---------------------------------------------------------------------------
# The three one-dimensional bifurcations
# ---------------------------------------------------------------------------


_FORMS = (
    ("saddle-node", "x' = r + x²", lambda r, x: r + x * x),
    ("transcritical", "x' = r·x − x²", lambda r, x: r * x - x * x),
    ("pitchfork", "x' = r·x − x³", lambda r, x: r * x - x ** 3),
)


class NormalFormsFigure(LessonFigure):
    """Saddle-node, transcritical and pitchfork: the phase line and the diagram.

    Left, f(x) at the current r with its equilibria, from
    `analysis.phase_line`. Right, the equilibria against r over the whole
    range -- the bifurcation diagram -- built by running the same routine at
    each r, with the current value marked. The two panes are one computation
    read two ways, which is the relationship the lesson is about.
    """

    title = "Three ways an equilibrium can change"
    caption = ("Left: the phase line at the current r. Right: every "
               "equilibrium against r, solid where stable and hollow where "
               "not, with the current r marked. Move r through zero and watch "
               "equilibria appear, exchange stability or split.")
    plots = 2

    _XLIM = (-1.6, 1.6)
    _R = np.linspace(-1.0, 1.0, 61)

    def __init__(self, palette, parent=None) -> None:
        self._diagrams: dict[int, list] = {}
        super().__init__(palette, parent)

    def build_sliders(self) -> None:
        self.add_slider("r", "r", -1.0, 1.0, 0.4)
        self.add_slider("form", "form  (0 saddle-node, 1 transcritical, "
                        "2 pitchfork)", 0.0, 2.0, 2.0)

    def form(self) -> int:
        return int(round(self.value("form")))

    @staticmethod
    def _line(f, r):
        problem = ODEProblem(f=lambda t, y: np.array([f(r, y[0])]),
                             t_span=(0.0, 1.0), y0=np.array([0.1]))
        return problem, analysis.phase_line(problem, NormalFormsFigure._XLIM)

    def diagram(self) -> list:
        """``[(r, value, stability), ...]`` over the range, cached per form."""
        index = self.form()
        if index not in self._diagrams:
            f = _FORMS[index][2]
            rows = []
            for r in self._R:
                for point in self._line(f, float(r))[1]:
                    rows.append((float(r), point.value, point.stability))
            self._diagrams[index] = rows
        return self._diagrams[index]

    def draw(self) -> None:
        name, formula, f = _FORMS[self.form()]
        r = self.value("r")
        left, right = self.panes
        left.clear()
        right.clear()

        grid = np.linspace(*self._XLIM, 300)
        left.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        left.plot(grid, [f(r, x) for x in grid], pen=pg.mkPen(self.colour(0), width=2))
        left.setLabel("bottom", "x")
        left.setLabel("left", "f(x)")
        left.setXRange(*self._XLIM, padding=0.02)
        left.setYRange(-1.5, 1.5, padding=0.02)
        _, points = self._line(f, r)
        for point in points:
            _marker(left, (point.value, 0.0), point.stability, self.palette_obj)

        rows = self.diagram()
        for stability, filled in ((analysis.STABLE, True), (analysis.UNSTABLE, False),
                                  (analysis.NEUTRAL, False)):
            chosen = [(rr, v) for rr, v, s in rows if s == stability]
            if not chosen:
                continue
            data = np.asarray(chosen)
            colour = (self.palette_obj.success if stability == analysis.STABLE
                      else self.palette_obj.danger if stability == analysis.UNSTABLE
                      else self.palette_obj.warning)
            right.plot(data[:, 0], data[:, 1], pen=None, symbol="o", symbolSize=5,
                       symbolPen=pg.mkPen(colour), symbolBrush=colour if filled else None)
        right.addLine(x=r, pen=pg.mkPen(self.palette_obj.accent, width=1.5,
                                        style=Qt.DashLine))
        right.setLabel("bottom", "r")
        right.setLabel("left", "equilibria")
        right.setXRange(-1.0, 1.0, padding=0.02)
        right.setYRange(*self._XLIM, padding=0.02)

        where = ", ".join(f"{p.value:+.3f} ({p.stability})" for p in points) or "none"
        self.readout.setText(f"{name}, {formula}, at r = {r:+.3f}: equilibria {where}.")
