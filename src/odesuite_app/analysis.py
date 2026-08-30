"""Phase-plane analysis for planar autonomous systems.

Everything the Phase Portrait screen draws beyond the trajectories themselves:
the vector field, the nullclines, the equilibria and their classification, and
the separatrices emanating from saddles.

No Qt here. The screen renders what this module computes, which keeps the
mathematics testable on its own -- and the classification below *is*
mathematics, not presentation: whether a fixed point is a saddle or a spiral is
decided by the eigenvalues of the Jacobian, and getting it wrong would be a
wrong answer rather than an ugly picture.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from odesuite import ODEProblem, solve
from odesuite.linalg import forward_diff_jacobian

__all__ = [
    "FixedPoint",
    "Equilibrium",
    "PortraitData",
    "vector_field",
    "slope_field",
    "jacobian_at",
    "classify",
    "find_fixed_points",
    "phase_line",
    "nullclines",
    "separatrices",
    "trajectory_through",
    "analyse",
]


#: How a planar equilibrium is named, keyed by the eigenvalue signature.
STABLE = "stable"
UNSTABLE = "unstable"
NEUTRAL = "neutral"


@dataclass
class FixedPoint:
    """An equilibrium and its linear classification."""

    position: np.ndarray            # (2,)
    eigenvalues: np.ndarray         # (2,) complex
    eigenvectors: np.ndarray        # (2, 2) columns matching eigenvalues
    kind: str                       # "saddle", "stable spiral", ...
    stability: str                  # STABLE / UNSTABLE / NEUTRAL

    @property
    def is_saddle(self) -> bool:
        return self.kind == "saddle"

    def __repr__(self) -> str:
        x, y = self.position
        return f"FixedPoint(({x:.4g}, {y:.4g}), {self.kind})"


@dataclass
class PortraitData:
    """Everything computed for one parameter setting."""

    xlim: tuple[float, float]
    ylim: tuple[float, float]
    streamlines: list[np.ndarray] = field(default_factory=list)
    speed_grid: np.ndarray | None = None
    nullcline_x: list[np.ndarray] = field(default_factory=list)
    nullcline_y: list[np.ndarray] = field(default_factory=list)
    fixed_points: list[FixedPoint] = field(default_factory=list)
    separatrices: list[tuple[np.ndarray, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Field sampling
# ---------------------------------------------------------------------------


def vector_field(problem: ODEProblem, xlim, ylim, resolution: int = 33):
    """Sample the RHS on a grid. Returns ``(X, Y, U, V, speed)``."""
    x = np.linspace(xlim[0], xlim[1], resolution)
    y = np.linspace(ylim[0], ylim[1], resolution)
    X, Y = np.meshgrid(x, y)
    U = np.empty_like(X)
    V = np.empty_like(Y)

    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            derivative = problem.f(0.0, np.array([X[i, j], Y[i, j]]))
            U[i, j], V[i, j] = derivative[0], derivative[1]

    return X, Y, U, V, np.hypot(U, V)


def slope_field(problem: ODEProblem, tlim, ylim, resolution: int = 21,
                fill: float = 0.62):
    """Short tangent segments for a scalar equation, in the ``(t, y)`` plane.

    Not the same picture as `vector_field`, and the difference matters. A phase
    portrait plots one state against another and only makes sense for an
    autonomous system; a slope field plots the *independent* variable across and
    marks the slope ``y' = f(t, y)`` the solution must have at each point. Time
    dependence is the axis rather than a problem, so this is the right drawing
    for exactly the first-order equations the portrait cannot take -- and every
    solution curve threads it tangentially, which is the whole idea.

    Returns ``(segments, slopes)``: an ``(n, 2, 2)`` array of endpoints and the
    slope at each midpoint, for colouring.
    """
    if problem.y0.size != 1:
        raise ValueError("a slope field is only defined for a scalar equation")

    times = np.linspace(tlim[0], tlim[1], resolution)
    values = np.linspace(ylim[0], ylim[1], resolution)

    # Segments are drawn in *screen* proportion rather than data units: the two
    # axes usually differ by orders of magnitude, and a fixed data-length dash
    # would be invisible on one axis and span the plot on the other.
    dt = (tlim[1] - tlim[0]) / max(resolution - 1, 1) * fill
    dy = (ylim[1] - ylim[0]) / max(resolution - 1, 1) * fill

    segments, slopes = [], []
    for t in times:
        for y in values:
            try:
                derivative = float(np.asarray(problem.f(float(t), np.array([y])))[0])
            except Exception:
                continue
            if not np.isfinite(derivative):
                continue
            # Normalise in the plot's own aspect so every dash is the same
            # length on screen and only its angle carries information.
            scaled = derivative * (dt / dy) if dy else 0.0
            norm = np.hypot(1.0, scaled) or 1.0
            half_t = 0.5 * dt / norm
            half_y = 0.5 * dy * scaled / norm
            segments.append([[t - half_t, y - half_y], [t + half_t, y + half_y]])
            slopes.append(derivative)

    if not segments:
        return np.empty((0, 2, 2)), np.empty(0)
    return np.asarray(segments, dtype=float), np.asarray(slopes, dtype=float)


def streamlines(problem: ODEProblem, xlim, ylim, resolution: int = 33,
                density: float = 1.1) -> list[np.ndarray]:
    """Evenly spaced streamlines of the vector field, as ``(n, 2)`` polylines.

    Computed with matplotlib's streamplot placement algorithm -- which solves
    the genuinely fiddly problem of spacing lines evenly without them crowding
    or colliding -- and then extracted as raw segments for pyqtgraph to draw.
    Only the geometry is borrowed; nothing is rendered.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    X, Y, U, V, _ = vector_field(problem, xlim, ylim, resolution)
    figure = plt.figure()
    axes = figure.add_subplot()
    try:
        # Unbroken streamlines: each one is returned as a continuous run of
        # segments, which stitches into a single long path. Broken ones
        # fragment into short disconnected dashes that read as noise.
        stream = axes.streamplot(
            X[0], Y[:, 0], U, V, density=density, broken_streamlines=False
        )
        segments = stream.lines.get_segments()
    except TypeError:                   # matplotlib < 3.6
        stream = axes.streamplot(X[0], Y[:, 0], U, V, density=density)
        segments = stream.lines.get_segments()
    except Exception:
        segments = []
    finally:
        plt.close(figure)

    # Stitch consecutive segments into polylines so the renderer draws a few
    # long paths instead of thousands of two-point ones.
    # Segments come back in one of two shapes depending on the matplotlib
    # version and options: as consecutive two-point pieces of one streamline,
    # or as whole multi-point polylines. Handle both by appending every
    # interior point, not just the endpoints -- reading only the ends silently
    # discards the entire curve when the segments are already polylines.
    scale = max(xlim[1] - xlim[0], ylim[1] - ylim[0])
    tolerance = 1e-6 * scale
    paths: list[np.ndarray] = []
    current: np.ndarray | None = None

    for segment in segments:
        piece = np.asarray(segment, dtype=float)
        if piece.ndim != 2 or len(piece) < 2:
            continue
        if current is not None and np.linalg.norm(current[-1] - piece[0]) <= tolerance:
            current = np.vstack([current, piece[1:]])
        else:
            if current is not None and len(current) > 2:
                paths.append(current)
            current = piece
    if current is not None and len(current) > 2:
        paths.append(current)
    return paths


# ---------------------------------------------------------------------------
# Equilibria
# ---------------------------------------------------------------------------


def jacobian_at(problem: ODEProblem, point: np.ndarray) -> np.ndarray:
    """``df/dy`` at `point`, analytic where the problem supplies one."""
    point = np.asarray(point, dtype=float)
    if problem.has_jac:
        return np.asarray(problem.jac(0.0, point), dtype=float)
    return forward_diff_jacobian(
        problem.f, 0.0, point, problem.f(0.0, point), threshold=1e-6
    )


def classify(eigenvalues: np.ndarray) -> tuple[str, str]:
    """Name a planar equilibrium from its Jacobian eigenvalues.

    The standard trace-determinant taxonomy. A pair of real eigenvalues of
    opposite sign is a saddle; a complex pair spirals, in or out according to
    the sign of the real part; purely imaginary is a centre. "Non-hyperbolic"
    covers the cases where the linearisation decides nothing and the true
    behaviour depends on higher-order terms -- worth naming honestly rather
    than guessing at.
    """
    values = np.asarray(eigenvalues)
    real = values.real
    imaginary = values.imag
    scale = max(float(np.max(np.abs(values))), 1e-12)
    tolerance = 1e-8 * scale

    complex_pair = bool(np.any(np.abs(imaginary) > tolerance))

    if np.all(np.abs(real) <= tolerance):
        if complex_pair:
            return "centre", NEUTRAL
        return "non-hyperbolic", NEUTRAL

    if complex_pair:
        if np.all(real < -tolerance):
            return "stable spiral", STABLE
        if np.all(real > tolerance):
            return "unstable spiral", UNSTABLE
        return "non-hyperbolic", NEUTRAL

    if np.any(np.abs(real) <= tolerance):
        return "non-hyperbolic", NEUTRAL
    if real[0] * real[1] < 0:
        return "saddle", UNSTABLE
    if np.all(real < 0):
        return "stable node", STABLE
    return "unstable node", UNSTABLE


def find_fixed_points(problem: ODEProblem, xlim, ylim, seeds: int = 11,
                      tolerance: float = 1e-10) -> list[FixedPoint]:
    """Locate equilibria by Newton from a grid of starting guesses.

    A grid rather than anything cleverer: the basins of attraction of Newton's
    method on a planar system are fractal, so no single start finds everything,
    but a modest sweep reliably does. Duplicates are then merged, since many
    seeds converge to the same root.
    """
    xs = np.linspace(xlim[0], xlim[1], seeds)
    ys = np.linspace(ylim[0], ylim[1], seeds)
    span = max(xlim[1] - xlim[0], ylim[1] - ylim[0])
    found: list[np.ndarray] = []

    for x0 in xs:
        for y0 in ys:
            point = np.array([x0, y0], dtype=float)
            for _ in range(40):
                residual = problem.f(0.0, point)
                if np.linalg.norm(residual) < tolerance:
                    break
                J = jacobian_at(problem, point)
                try:
                    step = np.linalg.solve(J, residual)
                except np.linalg.LinAlgError:
                    break
                # Damp long steps: an almost-singular Jacobian otherwise throws
                # the iterate far outside the window, where it either diverges
                # or converges to an irrelevant root.
                length = np.linalg.norm(step)
                if length > 0.5 * span:
                    step *= 0.5 * span / length
                point = point - step
            else:
                continue

            if np.linalg.norm(problem.f(0.0, point)) > 1e-7:
                continue
            if not (xlim[0] <= point[0] <= xlim[1] and ylim[0] <= point[1] <= ylim[1]):
                continue
            if any(np.linalg.norm(point - other) < 1e-4 * span for other in found):
                continue
            found.append(point)

    results = []
    for point in sorted(found, key=lambda p: (p[0], p[1])):
        values, vectors = np.linalg.eig(jacobian_at(problem, point))
        kind, stability = classify(values)
        results.append(FixedPoint(point, values, vectors, kind, stability))
    return results


# ---------------------------------------------------------------------------
# The phase line
#
# One dimension, not two, and deliberately not `find_fixed_points` with a
# degenerate second axis. That routine is a planar Newton sweep classified by
# the eigenvalues of a 2x2 Jacobian; a scalar autonomous equation has no such
# thing. It also has something better available: on a line, "which way does a
# solution move from here" is settled by the *sign* of f on either side, which
# is what a course draws and what stays right where the linearisation says
# nothing at all.
#
# That last case is not a curiosity. `y' = y**2` has one equilibrium, at 0,
# with f'(0) = 0, and it is semi-stable -- attracting from below, repelling
# from above. Classifying it by the derivative would call it neutral and lose
# both arrows; classifying it by the signs gets it right, and gets an ordinary
# crossing right too.
# ---------------------------------------------------------------------------


@dataclass
class Equilibrium:
    """A constant solution of a scalar autonomous equation, and its arrows."""

    value: float
    #: f'(y*), the linearisation a course teaches beside the picture. Zero at
    #: a touch -- which is exactly when `stability` is the thing to trust.
    slope: float
    #: The sign of f immediately below and above the equilibrium: -1, 0 or +1.
    below: int
    above: int
    stability: str                  # STABLE / UNSTABLE / NEUTRAL

    @property
    def is_semistable(self) -> bool:
        """Attracting from one side and repelling from the other."""
        return self.stability == NEUTRAL and self.below * self.above > 0

    def __repr__(self) -> str:
        return f"Equilibrium({self.value:.4g}, {self.stability})"


def _scalar_f(problem: ODEProblem):
    """``f(y)`` as a plain float function, for an autonomous scalar problem."""
    if problem.y0.size != 1:
        raise ValueError("a phase line is only defined for a scalar equation")

    def f(y: float) -> float:
        return float(np.asarray(problem.f(0.0, np.array([float(y)])))[0])

    return f


def phase_line(problem: ODEProblem, ylim, samples: int = 801,
               tolerance: float = 1e-9) -> list[Equilibrium]:
    """The equilibria of a scalar autonomous ``y' = f(y)``, in increasing order.

    Found by scanning `f` across `ylim` and refining every local minimum of
    ``|f|``, not only the sign changes. Sign changes alone would miss a root
    the curve touches without crossing, and those are the ones a lesson on
    stability is most interested in.

    `f` is evaluated at ``t = 0`` throughout: the equation is assumed
    autonomous, which is what makes a phase line meaningful in the first place.
    """
    f = _scalar_f(problem)
    low, high = float(ylim[0]), float(ylim[1])
    if not high > low:
        raise ValueError("ylim must be increasing")

    grid = np.linspace(low, high, max(int(samples), 3))
    values = np.array([f(y) for y in grid], dtype=float)
    finite = np.isfinite(values)
    span = high - low
    scale = float(np.max(np.abs(values[finite]))) if finite.any() else 1.0
    near_zero = max(tolerance, tolerance * scale)

    roots: list[float] = []
    for i in range(len(grid) - 1):
        if not (finite[i] and finite[i + 1]):
            continue
        if values[i] == 0.0:
            roots.append(float(grid[i]))
        elif values[i] * values[i + 1] < 0:
            roots.append(_bisect(f, float(grid[i]), float(grid[i + 1]), span))

    # Touches. Bisection cannot reach these: there is no sign change to
    # bracket, so what is refined is the nearest local minimum of |f| instead.
    magnitude = np.where(finite, np.abs(values), np.inf)
    for i in range(1, len(grid) - 1):
        if not (magnitude[i] <= magnitude[i - 1]
                and magnitude[i] <= magnitude[i + 1]):
            continue
        candidate = _minimise(f, float(grid[i - 1]), float(grid[i + 1]))
        if abs(f(candidate)) <= near_zero:
            roots.append(candidate)

    merged: list[float] = []
    for root in sorted(roots):
        if not merged or abs(root - merged[-1]) > 1e-6 * span:
            merged.append(root)

    out = []
    for index, root in enumerate(merged):
        # Far enough out to be clear of the root itself, never so far as to
        # reach the next equilibrium -- where the sign would be about that one.
        reach = span / 200.0
        if index:
            reach = min(reach, 0.4 * (root - merged[index - 1]))
        if index + 1 < len(merged):
            reach = min(reach, 0.4 * (merged[index + 1] - root))
        below, above = _sign(f, root - reach), _sign(f, root + reach)
        out.append(Equilibrium(
            value=root,
            slope=(f(root + reach) - f(root - reach)) / (2 * reach),
            below=below,
            above=above,
            stability=_stability_on_a_line(below, above),
        ))
    return out


def _stability_on_a_line(below: int, above: int) -> str:
    """Arrows in from both sides is stable, out on both is unstable.

    Anything else -- a touch, or a flat stretch -- is neither, and saying so is
    more useful than picking one of the two.
    """
    if below > 0 and above < 0:
        return STABLE
    if below < 0 and above > 0:
        return UNSTABLE
    return NEUTRAL


def _sign(f, y: float, tolerance: float = 1e-12) -> int:
    value = f(y)
    if not np.isfinite(value) or abs(value) <= tolerance:
        return 0
    return 1 if value > 0 else -1


def _bisect(f, low: float, high: float, span: float, steps: int = 80) -> float:
    """A root bracketed by a sign change.

    Plain bisection: the bracket is one grid cell wide to begin with, so this
    is a handful of halvings, and it cannot wander out of the bracket the way
    a secant step can.
    """
    f_low = f(low)
    for _ in range(steps):
        if high - low < 1e-15 * max(span, 1.0):
            break
        middle = 0.5 * (low + high)
        f_mid = f(middle)
        if f_mid == 0.0:
            return middle
        if (f_low > 0) != (f_mid > 0):
            high = middle
        else:
            low, f_low = middle, f_mid
    return 0.5 * (low + high)


def _minimise(f, low: float, high: float, steps: int = 60) -> float:
    """Golden-section minimum of ``|f|`` on ``[low, high]``.

    Bracketed and derivative-free, because the case this exists for is exactly
    the one where the derivative vanishes.
    """
    ratio = 0.5 * (math.sqrt(5.0) - 1.0)
    left = high - ratio * (high - low)
    right = low + ratio * (high - low)
    f_left, f_right = abs(f(left)), abs(f(right))
    for _ in range(steps):
        if f_left <= f_right:
            high, right, f_right = right, left, f_left
            left = high - ratio * (high - low)
            f_left = abs(f(left))
        else:
            low, left, f_left = left, right, f_right
            right = low + ratio * (high - low)
            f_right = abs(f(right))
    return 0.5 * (low + high)


# ---------------------------------------------------------------------------
# Nullclines
# ---------------------------------------------------------------------------


def _contour_paths(X, Y, Z) -> list[np.ndarray]:
    """Zero-level contours of `Z`, as polylines. Nothing is rendered."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure = plt.figure()
    axes = figure.add_subplot()
    paths: list[np.ndarray] = []
    try:
        contours = axes.contour(X, Y, Z, levels=[0.0])
        for path in contours.get_paths():
            vertices, codes = path.vertices, path.codes
            if codes is None:
                if len(vertices) > 1:
                    paths.append(np.asarray(vertices))
                continue
            # A single Path may hold several disconnected curves, each opened
            # by a MOVETO; splitting on those keeps them from being joined by
            # a spurious straight line.
            starts = list(np.nonzero(codes == 1)[0]) + [len(codes)]
            for begin, end in zip(starts, starts[1:]):
                piece = vertices[begin:end]
                if len(piece) > 1:
                    paths.append(np.asarray(piece))
    except Exception:
        pass
    finally:
        plt.close(figure)
    return paths


def nullclines(problem: ODEProblem, xlim, ylim, resolution: int = 140):
    """Curves where each component of the derivative vanishes.

    Their intersections are exactly the equilibria, which makes them a useful
    visual cross-check on `find_fixed_points`: every marker should sit on a
    crossing.
    """
    X, Y, U, V, _ = vector_field(problem, xlim, ylim, resolution)
    return _contour_paths(X, Y, U), _contour_paths(X, Y, V)


# ---------------------------------------------------------------------------
# Trajectories and invariant manifolds
# ---------------------------------------------------------------------------


def trajectory_through(problem: ODEProblem, point, span: float = 40.0,
                       backward: bool = True, rtol: float = 1e-8):
    """Integrate through `point`, forwards and (by default) backwards.

    Backward integration is what turns a set of trajectories into a portrait:
    forwards alone shows where a state ends up, but the curve *through* a point
    needs its past as well. The library supports ``t_end < t0`` throughout, so
    this is one extra call rather than a special case.
    """
    point = np.asarray(point, dtype=float)
    pieces = []
    directions = [span, -span] if backward else [span]

    for horizon in directions:
        candidate = ODEProblem(
            f=problem.f_user, t_span=(0.0, horizon), y0=point,
            jac=problem._jac_user, args=problem.args,
        )
        try:
            solution = solve(
                candidate, method="dopri5", rtol=rtol, atol=rtol * 1e-3,
                dense_output=True, max_steps=20_000,
            )
        except Exception:
            continue
        if solution.t.size < 2:
            continue
        grid = np.linspace(solution.t[0], solution.t[-1], 900)
        values = solution.sol(grid) if solution.sol is not None else solution.y
        pieces.append(values[:2].T)

    if not pieces:
        return np.empty((0, 2))
    if len(pieces) == 1:
        return pieces[0]
    # Backward piece reversed, then the forward piece, so the polyline runs
    # continuously from the distant past to the distant future.
    return np.vstack([pieces[1][::-1], pieces[0]])


def clip_to_window(curve: np.ndarray, xlim, ylim) -> list[np.ndarray]:
    """Split a polyline into the runs that lie inside the window.

    Essential rather than cosmetic. Integrating a saddle's *stable* manifold
    backwards through a damped system amplifies exactly the mode that decays
    forwards, so the curve leaves the region of interest and then wanders
    across it, drawing a tangle that hides the structure it was meant to
    reveal. Only the part inside the window means anything.
    """
    if curve.size == 0:
        return []
    inside = (
        (curve[:, 0] >= xlim[0]) & (curve[:, 0] <= xlim[1])
        & (curve[:, 1] >= ylim[0]) & (curve[:, 1] <= ylim[1])
    )
    if not inside.any():
        return []

    def crossing(here: np.ndarray, there: np.ndarray) -> np.ndarray:
        """Where the segment ``here -> there`` first meets the boundary.

        Interpolated rather than approximated by the last point inside or the
        first outside: how far past the edge that point falls depends on the
        sampling density, so a fast-moving trajectory would stick out of the
        plot by an arbitrary amount.
        """
        delta = there - here
        times = []
        for axis, bounds in enumerate((xlim, ylim)):
            if delta[axis] == 0:
                continue
            for bound in bounds:
                t = (bound - here[axis]) / delta[axis]
                if 0.0 < t <= 1.0:
                    times.append(t)
        return here + min(times) * delta if times else here

    pieces: list[np.ndarray] = []
    run: list[np.ndarray] = []
    for index, flag in enumerate(inside):
        if flag:
            if not run and index > 0:
                run.append(crossing(curve[index], curve[index - 1]))
            run.append(curve[index])
        elif run:
            run.append(crossing(curve[index - 1], curve[index]))
            pieces.append(np.asarray(run))
            run = []
    if run:
        pieces.append(np.asarray(run))
    return [piece for piece in pieces if len(piece) > 1]


def separatrices(problem: ODEProblem, point: FixedPoint, span: float = 30.0,
                 offset: float = 1e-4) -> list[tuple[np.ndarray, str]]:
    """The stable and unstable manifolds of a saddle.

    Near a saddle the flow follows the Jacobian's eigendirections, so nudging
    off the equilibrium along an eigenvector and integrating traces the
    corresponding manifold: forwards for the unstable direction, backwards for
    the stable one. These curves are the skeleton of the portrait -- they
    separate qualitatively different behaviours, which on a pendulum is
    literally the boundary between swinging and rotating.
    """
    if not point.is_saddle:
        return []

    curves: list[tuple[np.ndarray, str]] = []
    for index in range(2):
        eigenvalue = point.eigenvalues[index].real
        direction = np.real(point.eigenvectors[:, index])
        norm = np.linalg.norm(direction)
        if norm == 0:
            continue
        direction = direction / norm
        horizon = span if eigenvalue > 0 else -span
        label = "unstable" if eigenvalue > 0 else "stable"

        for sign in (+1.0, -1.0):
            start = point.position + sign * offset * direction
            candidate = ODEProblem(
                f=problem.f_user, t_span=(0.0, horizon), y0=start,
                jac=problem._jac_user, args=problem.args,
            )
            try:
                solution = solve(
                    candidate, method="dopri5", rtol=1e-9, atol=1e-12,
                    dense_output=True, max_steps=20_000,
                )
            except Exception:
                continue
            if solution.t.size < 2:
                continue
            grid = np.linspace(solution.t[0], solution.t[-1], 700)
            values = solution.sol(grid) if solution.sol is not None else solution.y
            curves.append((values[:2].T, label))
    return curves


# ---------------------------------------------------------------------------
# One call for the whole picture
# ---------------------------------------------------------------------------


def analyse(problem: ODEProblem, xlim, ylim, *, with_streamlines: bool = True,
            with_nullclines: bool = True, with_separatrices: bool = True,
            resolution: int = 33) -> PortraitData:
    """Compute every layer of the portrait for one parameter setting."""
    data = PortraitData(xlim=tuple(xlim), ylim=tuple(ylim))

    _, _, _, _, speed = vector_field(problem, xlim, ylim, resolution)
    data.speed_grid = speed

    if with_streamlines:
        data.streamlines = streamlines(problem, xlim, ylim, resolution)
    if with_nullclines:
        data.nullcline_x, data.nullcline_y = nullclines(problem, xlim, ylim)

    data.fixed_points = find_fixed_points(problem, xlim, ylim)
    if with_separatrices:
        for point in data.fixed_points:
            for curve, label in separatrices(problem, point):
                pieces = clip_to_window(curve, xlim, ylim)
                # Only the *first* run counts. The curve starts at the saddle,
                # so that run is the manifold branch leaving it; anything after
                # the curve has left the window is a later, unrelated excursion
                # of the same trajectory, and drawing those turns a clean
                # skeleton into a scribble.
                if pieces:
                    data.separatrices.append((pieces[0], label))
    return data


def default_window(problem: ODEProblem, solution=None, pad: float = 0.35):
    """A viewing window framed on the system's *structure*, not one orbit.

    Starts from the extent of a representative trajectory, then searches a
    wider region for equilibria and expands to include any it finds. Framing on
    a single trajectory alone is not enough: a damped oscillator spirals into
    one well and its orbit never reveals the saddle or the second well, so the
    portrait would open on the least interesting part of the picture.
    """
    if solution is not None and solution.y.shape[0] >= 2 and solution.y.shape[1]:
        x, y = solution.y[0], solution.y[1]
        xlo, xhi = float(np.min(x)), float(np.max(x))
        ylo, yhi = float(np.min(y)), float(np.max(y))
    else:
        xlo = xhi = ylo = yhi = 0.0

    width = max(xhi - xlo, 1e-3)
    height = max(yhi - ylo, 1e-3)
    if width < 1e-2 and height < 1e-2:
        width = height = 2.0
        xlo, xhi, ylo, yhi = -1.0, 1.0, -1.0, 1.0

    # Search a box five times the size and pull in whatever is found. The
    # margin has to be generous: a damped Duffing orbit settles into one well
    # and spans barely more than that well, so the saddle and the opposite
    # well sit well outside anything close to the trajectory's own extent.
    centre_x, centre_y = 0.5 * (xlo + xhi), 0.5 * (ylo + yhi)
    base_width, base_height = width, height
    search = (
        (centre_x - 2.5 * width, centre_x + 2.5 * width),
        (centre_y - 2.5 * height, centre_y + 2.5 * height),
    )
    try:
        for point in find_fixed_points(problem, *search, seeds=9):
            xlo, xhi = min(xlo, point.position[0]), max(xhi, point.position[0])
            ylo, yhi = min(ylo, point.position[1]), max(yhi, point.position[1])
    except Exception:
        pass

    # ...but do not let a distant equilibrium zoom the picture out to nothing.
    # A periodic system such as the pendulum has equilibria every pi forever;
    # showing a few is structure, showing twenty is clutter.
    limit_x, limit_y = 2.5 * width, 2.5 * height
    xlo = max(xlo, centre_x - limit_x)
    xhi = min(xhi, centre_x + limit_x)
    ylo = max(ylo, centre_y - limit_y)
    yhi = min(yhi, centre_y + limit_y)

    # Pad by a fraction of the *original* extent, not the expanded one --
    # otherwise the margin grows with the box and re-widens it past the clamp.
    return (
        (xlo - pad * base_width, xhi + pad * base_width),
        (ylo - pad * base_height, yhi + pad * base_height),
    )
