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
from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np

from odesuite import Event, ODEProblem, solve
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
    "largest_lyapunov",
    "LyapunovEstimate",
    "predictability_horizon",
    "phase_line",
    "nullclines",
    "separatrices",
    "trajectory_through",
    "Section",
    "poincare_section",
    "LimitCycle",
    "largest_closed_orbit",
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

    @property
    def hyperbolic(self) -> bool:
        """Whether the linearisation actually decides the nonlinear behaviour.

        It does when no eigenvalue sits on the imaginary axis -- that is the
        Hartman-Grobman hypothesis, and where it holds the flow near the point
        looks like the linear flow. Where it fails, `kind` is a statement about
        the *linearisation* and nothing more, because arbitrarily small
        higher-order terms decide the rest.

        The case that matters is a centre, and it is not a corner case:
        ``x' = -y + x(x^2+y^2)``, ``y' = x + y(x^2+y^2)`` has eigenvalues
        exactly ``+-i`` and a flow that spirals *outward*. Lotka-Volterra has
        the same eigenvalue signature and is a genuine centre. Nothing in the
        eigenvalues separates them, so anything that reports `kind` to a reader
        has to say which of the two situations it is in.
        """
        scale = max(float(np.max(np.abs(self.eigenvalues))), 1e-12)
        return bool(np.all(np.abs(self.eigenvalues.real) > 1e-8 * scale))

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


#: Grid density for the arrow field, and for the nullclines drawn over it.
#:
#: Two numbers rather than one, because they are read differently. The arrows
#: are counted -- 33 across is dense enough to show the flow and sparse enough
#: that individual arrows stay legible, and the cost is quadratic in this. The
#: nullclines are contours of the same sampling, where the eye follows a curve
#: rather than counting marks, so they need a much finer grid before the
#: polyline stops looking like a staircase; 140 is where that happens and the
#: extra cost is one pass of `_contour_paths`.
#:
#: Constants rather than parameters. Both were arguments with defaults that no
#: caller ever overrode, which reads as a density control the interface offers
#: and does not. `slope_field` keeps its parameter, because the lesson figures
#: genuinely do vary it (19 and 17, against the default 21, to keep a small
#: figure from crowding).
VECTOR_FIELD_RESOLUTION = 33
NULLCLINE_RESOLUTION = 140
#: Grid the streamline placement samples the field on. Not a density --
#: matplotlib's `density` is a separate argument of `streamlines`, and
#: conflating the two is exactly the defect the call site above records.
STREAMLINE_RESOLUTION = 33


def vector_field(problem: ODEProblem, xlim, ylim, resolution: int | None = None):
    """Sample the RHS on a grid. Returns ``(X, Y, U, V, speed)``.

    `resolution` exists for `nullclines`, which needs the same sampling at a
    much finer grid; it is not a knob the interface turns.
    """
    resolution = VECTOR_FIELD_RESOLUTION if resolution is None else resolution
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


def streamlines(problem: ODEProblem, xlim, ylim, *,
                density: float = 1.1) -> list[np.ndarray]:
    """Evenly spaced streamlines of the vector field, as ``(n, 2)`` polylines.

    Computed with matplotlib's streamplot placement algorithm -- which solves
    the genuinely fiddly problem of spacing lines evenly without them crowding
    or colliding -- and then extracted as raw segments for pyqtgraph to draw.
    Only the geometry is borrowed; nothing is rendered.

    **`density` is keyword-only, and that is a fix rather than a style.** The
    grid this samples on is `STREAMLINE_RESOLUTION`, decided here and not by
    the caller; `density` is matplotlib's line-spacing knob, which is a
    different quantity that happens to sit in the next parameter slot. `analyse`
    passed its own `resolution` -- 33 -- positionally into it, so every portrait
    this application has drawn asked matplotlib for thirty times the intended
    line spacing. Measured on the pendulum over its default window:

        density=1.1      0.781 s     90 paths
        density=33     372.045 s   4609 paths

    A 476x slowdown, and 4609 overlapping curves is a scribble rather than a
    picture. It is why `tests/test_app_portrait.py` did not finish -- the
    fixture builds a screen per test and each one waited out an analysis -- and
    why the module docstring's "a few hundred milliseconds" had quietly stopped
    being true. Keyword-only is what stops the two being confused again.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    X, Y, U, V, _ = vector_field(problem, xlim, ylim, STREAMLINE_RESOLUTION)
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


#: Offsets the uniqueness probe differences over, coarsest first.
_UNIQUENESS_OFFSETS = (1e-2, 1e-4, 1e-6, 1e-8)


def uniqueness_warning(problem: ODEProblem) -> str | None:
    """Whether the existence-and-uniqueness hypothesis fails at the start.

    The theorem the course teaches (lesson `slopefields`) is that a continuous
    `f` gets you a solution and a continuous ``df/dy`` gets you *one*. Where the
    second condition fails, several solutions can pass through the same point --
    and a numerical method will return one of them, with nothing to say the
    others exist.

    That is not a hypothetical shortcoming. This application teaches
    ``y' = y^(1/3), y(0) = 0`` as the standard case where uniqueness fails, and
    its own solver answers ``y = 0`` with `success` set and no remark, while
    ``y = (2t/3)^(3/2)`` solves it just as well. The lesson and the tool
    disagreed, and the tool was the one keeping quiet.

    **How it decides.** ``df/dy`` is differenced at the initial point over
    offsets four decades apart. A derivative that exists is roughly the same at
    all of them; one that does not grows without bound as the offset shrinks.
    Measured:

    ==========================  ========  ========  =======
    problem                     h = 1e-2  h = 1e-8  ratio
    ==========================  ========  ========  =======
    ``y' = y^(1/3), y(0)=0``        21.5   2.15e+05    1e+04
    ``y' = sqrt|y|, y(0)=0``          10      1e+04    1e+03
    ``y' = -2y``                       2          2        1
    ``y' = -1000y``                1e+03      1e+03        1
    Robertson                      3e+05        0.3    1e-06
    Van der Pol, mu = 1000         3e+03      3e+03        1
    ==========================  ========  ========  =======

    The margin is four orders of magnitude, and the two stiff problems are the
    reason the test is growth rather than size: their derivatives are enormous
    and perfectly well defined. Robertson's quotient *falls*, because its second
    derivative is large -- which is also why the test asks for monotone growth
    rather than a single ratio.

    Returns a sentence to show the user, or None. It says the hypothesis is not
    satisfied, never that there are two solutions: the first is what was
    measured, the second would be a claim about the equation.
    """
    y0 = np.asarray(problem.y0, dtype=float)
    t0 = float(problem.t0)
    try:
        f0 = np.asarray(problem.f(t0, y0), dtype=float)
    except Exception:
        return None

    quotients = []
    for offset in _UNIQUENESS_OFFSETS:
        worst = 0.0
        for j in range(y0.size):
            step = offset * max(abs(float(y0[j])), 1.0)
            probe = y0.copy()
            probe[j] += step
            try:
                nearby = np.asarray(problem.f(t0, probe), dtype=float)
            except Exception:
                return None
            if not np.all(np.isfinite(nearby)):
                return None
            worst = max(worst, float(np.max(np.abs(nearby - f0)) / step))
        if not np.isfinite(worst):
            return None
        quotients.append(worst)

    # Growth, not size. A doubling across each hundredfold refinement, and a
    # hundredfold overall, separates an unbounded derivative from a merely
    # large one by four orders of magnitude on everything measured above.
    growing = all(
        later >= 2.0 * earlier
        for earlier, later in zip(quotients, quotients[1:])
    )
    if not (growing and quotients[-1] >= 100.0 * quotients[0] and quotients[-1] > 1.0):
        return None

    return (
        "∂f/∂y appears to be unbounded at the initial condition, so the "
        "uniqueness half of the existence-and-uniqueness theorem does not "
        "apply here. More than one solution may pass through this point, and a "
        "numerical method will return only one of them."
    )


#: Renormalisation interval for the Benettin walk, and the size of the
#: perturbation it keeps the two trajectories apart by.
#:
#: `tau` has to be short enough that the separation stays in the linear regime
#: -- on Lorenz the states are O(10) apart and 0.5 keeps the perturbation around
#: 1e-8, six orders below that -- and long enough that the renormalisations do
#: not dominate the cost. `d0` is well above round-off on an O(10) state and far
#: below any curvature of the flow.
LYAPUNOV_TAU = 0.5
LYAPUNOV_D0 = 1e-8
#: Time discarded before measuring, so the walk starts on the attractor rather
#: than on the way to it.
LYAPUNOV_TRANSIENT = 20.0
#: Independent runs whose scatter becomes the error bar. Five is the smallest
#: number that gives a usable standard error; the cost is linear in it.
LYAPUNOV_REPLICATES = 5


@dataclass
class LyapunovEstimate:
    """The largest Lyapunov exponent, with an error bar that means something."""

    value: float
    #: Standard error of the mean over `replicates` independent runs.
    error: float
    replicates: int
    #: "chaotic", "attracting", or "indistinguishable from zero".
    verdict: str

    @property
    def significant(self) -> bool:
        """Whether the sign of the exponent is resolved at all."""
        return abs(self.value) > 2.0 * self.error

    def __str__(self) -> str:
        return f"{self.value:+.4f} ± {self.error:.4f}  ({self.verdict})"


def largest_lyapunov(
    problem: ODEProblem,
    *,
    t_end: float = 300.0,
    replicates: int = LYAPUNOV_REPLICATES,
    spread: float = 0.5,
    rtol: float = 1e-8,
    atol: float = 1e-11,
    should_stop=None,
) -> LyapunovEstimate:
    """Estimate the largest Lyapunov exponent by Benettin renormalisation.

    Two trajectories a hair apart are integrated together; every `LYAPUNOV_TAU`
    the separation is measured, its log accumulated, and the perturbed state
    pulled back to `LYAPUNOV_D0` along the same direction. The mean log growth
    rate over the second half of the run is the exponent.

    **The error bar is the whole difficulty, and the obvious one is wrong.**
    Treating the per-interval log growths as independent samples gives a
    standard error 8.5 times too large -- measured, over 12 replicates on
    Lorenz: the estimates scatter with a standard deviation of 0.0281 while the
    naive iid formula reports 0.2404. Batch means over ten blocks is better and
    still 3.4 times too large, at 0.0960. The growths are strongly
    anti-correlated, so treating them as independent overstates the spread, and
    a 26% "relative standard error" would have made the routine refuse to report
    a perfectly good answer.

    So the error bar is the scatter across `replicates` **independent** runs,
    which measures the thing being reported rather than modelling it. Each
    replicate starts from a different point on the attractor *and* a different
    perturbation direction. Both matter: replicates that share a start point and
    differ only in direction agree with each other while being wrong together,
    and on a 15-time-unit Lorenz run that produced an error bar of exactly
    0.0000 -- the precise false negative an error bar exists to prevent.

    Measured with this design (five replicates):

    ==============================  ==========  ========  ==========================
    system                          estimate    error     verdict
    ==============================  ==========  ========  ==========================
    Lorenz, T = 300                   +0.8936    0.0078   chaotic  (lit. 0.9056)
    damped pendulum, T = 300          -0.1501    0.0002   attracting
    Lotka-Volterra, T = 400           +0.0035    0.0064   indistinguishable from zero
    harmonic oscillator, T = 400      -0.0000    0.0000   indistinguishable from zero
    ==============================  ==========  ========  ==========================

    The last two are why the verdict exists. A conservative system's largest
    exponent *is* zero, and a routine that reports "+0.0035, chaotic" of
    Lotka-Volterra would be confidently wrong about the most famous
    non-chaotic system in the catalogue.

    `should_stop` is polled once per interval and abandons the estimate when it
    returns True, because a 300-time-unit Lorenz run takes about 26 seconds and
    must not pin a thread the user has moved on from.
    """
    base = np.asarray(problem.y0, dtype=float)
    n = base.size
    rng = np.random.default_rng(0)
    f_user, args = problem.f_user, problem.args

    def pair(t, z):
        first = np.asarray(f_user(t, z[:n], *args), dtype=float).reshape(-1)
        second = np.asarray(f_user(t, z[n:], *args), dtype=float).reshape(-1)
        return np.concatenate([first, second])

    estimates = []
    for _ in range(max(2, replicates)):
        start = base + rng.normal(scale=spread, size=n)
        direction = rng.normal(size=n)
        direction /= np.linalg.norm(direction)

        settled = solve(
            ODEProblem(f=f_user, t_span=(problem.t0, problem.t0 + LYAPUNOV_TRANSIENT),
                       y0=start, args=args),
            "dopri5", rtol=rtol, atol=atol,
        )
        y = settled.y[:, -1].copy()
        t = float(settled.t[-1])
        perturbed = y + LYAPUNOV_D0 * direction

        growths = []
        for _ in range(max(4, int(round(t_end / LYAPUNOV_TAU)))):
            if should_stop is not None and should_stop():
                return LyapunovEstimate(float("nan"), float("nan"), 0, "cancelled")
            step = solve(
                ODEProblem(f=pair, t_span=(t, t + LYAPUNOV_TAU),
                           y0=np.concatenate([y, perturbed])),
                "dopri5", rtol=rtol, atol=atol,
            )
            both = step.y[:, -1]
            y, perturbed = both[:n].copy(), both[n:].copy()
            t = float(step.t[-1])
            separation = perturbed - y
            distance = float(np.linalg.norm(separation))
            if distance <= 0.0:
                break
            growths.append(np.log(distance / LYAPUNOV_D0))
            perturbed = y + (LYAPUNOV_D0 / distance) * separation

        if len(growths) < 4:
            return LyapunovEstimate(float("nan"), float("nan"), 0, "not converged")
        second_half = np.asarray(growths[len(growths) // 2:]) / LYAPUNOV_TAU
        estimates.append(float(second_half.mean()))

    values = np.asarray(estimates)
    value = float(values.mean())
    error = float(values.std(ddof=1) / np.sqrt(values.size))
    if abs(value) <= 2.0 * error:
        verdict = "indistinguishable from zero"
    else:
        verdict = "chaotic" if value > 0 else "attracting"
    return LyapunovEstimate(value, error, values.size, verdict)


def predictability_horizon(exponent: LyapunovEstimate, rtol: float) -> float | None:
    """How long a single trajectory carries information, at this tolerance.

    An error of size `rtol` grows like ``exp(lambda t)``, so it reaches O(1) at
    ``t = ln(1/rtol) / lambda``. Past that the trajectory is a sample from the
    attractor rather than a prediction of where the system is.

    None unless the exponent is resolved and positive: a horizon computed from
    an exponent indistinguishable from zero would be an enormous number
    presented as a fact, and for an attracting system there is no horizon at all.
    """
    if not exponent.significant or exponent.value <= 0 or not np.isfinite(exponent.value):
        return None
    return float(np.log(1.0 / max(rtol, 1e-16)) / exponent.value)


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


def nullclines(problem: ODEProblem, xlim, ylim):
    """Curves where each component of the derivative vanishes.

    Their intersections are exactly the equilibria, which makes them a useful
    visual cross-check on `find_fixed_points`: every marker should sit on a
    crossing.
    """
    X, Y, U, V, _ = vector_field(problem, xlim, ylim, NULLCLINE_RESOLUTION)
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
        # No resolution argument. `streamlines` takes matplotlib's line
        # *density* rather than a grid, and passing the grid resolution into it
        # asked for a seeding thirty times denser than intended. Measured on
        # the pendulum, two sessions arriving at this independently:
        #
        #     density   1.1     0.76 s     105 segments  /  90 stitched paths
        #     density   4.0     7.87 s     503 segments
        #     density  10.0    45.15 s    1384 segments
        #     density  33.0   372.05 s    4609 stitched paths
        #
        # The grid it samples is `STREAMLINE_RESOLUTION`, which the function
        # reads for itself. `density` is keyword-only now, so this call site
        # can no longer make the mistake by position -- but the numbers stay
        # here, because the next person to reach for a fourth argument should
        # see what one cost.
        data.streamlines = streamlines(problem, xlim, ylim)
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


# ---------------------------------------------------------------------------
# Closed orbits: the Poincare section and the return map
#
# Poincare-Bendixson is the central theorem of planar nonlinear dynamics, and
# the catalogue ships three systems whose whole character is a limit cycle --
# Van der Pol, the Brusselator, Duffing when it is driven -- described in prose
# with no way to find one, measure its period, or take a section. This is that
# way.
#
# The construction is the textbook one. Put a line across the flow, integrate,
# and record where the trajectory crosses it going the same way each time. A
# closed orbit crosses at the same point forever; anything else moves along the
# line, and how it moves is the return map.
#
# Two things here are more careful than the textbook picture, and both are
# about not claiming more than was measured.
#
# **A closed orbit is not the same thing as a limit cycle.** Lotka-Volterra's
# orbits are closed -- every one of them -- and not one is a limit cycle,
# because a limit cycle is *isolated*: nearby orbits have to converge to it.
# A routine that integrates, sees the trajectory return to its start and
# announces a limit cycle would announce one for every initial condition of
# every conservative system in the catalogue. So the orbit is pushed off by a
# sixth of its own diameter and asked whether it comes back. Van der Pol's
# does, to one part in ten thousand. Lotka-Volterra's does not: it settles onto
# a *different* closed orbit and stays there, and the return map's coordinate
# is unchanged to all the digits there are.
#
# **A decaying spiral crosses a section repeatedly too.** A damped pendulum's
# crossings march steadily inwards and its successive loops shrink by a factor
# of 0.385 each time, so the test is not "does it keep crossing" but "does the
# loop stop shrinking". Measured over five successive returns, as the audit
# asked, which is what rules out a spiral converging slowly enough to look
# closed over two.
#
# One correction to the plan this was written from, which asked that the return
# map be shown to contract over at least five crossings. It cannot be, and the
# reason is that the contraction is too strong rather than too weak: Van der
# Pol's return map contracts by a factor of about a thousand per circuit, so
# from a displacement of 0.85 it reaches the integrator's own noise floor --
# around 2e-13 -- on the fourth return, and every ratio after that is the
# floor dividing by itself. The five-crossing requirement is enforced where it
# is meaningful, on the closure test above, and the contraction is reported
# over however many returns stay above the noise.
# ---------------------------------------------------------------------------


#: How long to integrate before a section is placed, and for how long after.
#:
#: The transient exists to get off whatever the initial condition was and onto
#: whatever the system does; the run after it has to be long enough for the
#: five returns the closure test needs. Van der Pol's period is 6.66 and the
#: Brusselator's 7.16, so 120 time units is fifteen-odd circuits of the slowest
#: thing here -- ample, and cheap at these tolerances.
CYCLE_TRANSIENT = 60.0
CYCLE_SPAN = 120.0

#: Returns the closure test is measured over. The audit asked for five.
CYCLE_MIN_RETURNS = 5

#: Tolerances used to decide the two questions.
#:
#: `CYCLE_DIAMETER_TOL` is how much the loop may change size between successive
#: returns and still count as closed -- a tenth of a percent, against the
#: damped pendulum's 61% per loop, so the margin is three orders of magnitude.
#: `CYCLE_ISOLATION_TOL` is how closely a pushed-off orbit must come back:
#: 1%, against a measured 0.011% for Van der Pol and 79% for Lotka-Volterra.
CYCLE_DIAMETER_TOL = 1e-3
CYCLE_ISOLATION_TOL = 1e-2

#: How far off the orbit to push, as a fraction of its diameter. Large enough
#: that returning is evidence rather than rounding, small enough to stay in the
#: cycle's basin.
CYCLE_PUSH = 0.15

#: Tolerances for the integrations underneath all of this. Tight, because the
#: period is quoted to six figures and the return map is read down to 1e-13.
CYCLE_RTOL = 1e-10
CYCLE_ATOL = 1e-12

#: Samples per loop when measuring a diameter or returning the orbit.
CYCLE_SAMPLES = 200

#: A trajectory this much slower than it was half a transient ago is on
#: its way into an equilibrium rather than round an orbit. A tenth is far
#: below anything a genuine orbit does -- on a closed orbit the two speeds
#: are the same number -- and far above the pendulum's measured ratio.
_DECAY_FRACTION = 0.1


def _repose(problem: ODEProblem, y0, t_end: float) -> ODEProblem:
    """The same system, started somewhere else and run for a different time."""
    return ODEProblem(
        f=problem.f_user, t_span=(0.0, float(t_end)),
        y0=np.asarray(y0, dtype=float), jac=problem._jac_user, args=problem.args,
    )


@dataclass(frozen=True)
class Section:
    """A line across the flow, and where a trajectory crosses it."""

    base: np.ndarray            # (2,) a point on the line
    normal: np.ndarray          # (2,) unit normal; the line is perpendicular
    times: np.ndarray           # (k,) crossing times
    points: np.ndarray          # (k, 2) crossing states
    direction: int

    @property
    def tangent(self) -> np.ndarray:
        """The unit vector along the section line."""
        return np.array([-self.normal[1], self.normal[0]])

    @property
    def coordinates(self) -> np.ndarray:
        """Signed distance of each crossing from `base`, along the line.

        This is the return map's variable: a closed orbit through `base` sits
        at zero forever, and everything else is measured by how far from it
        the trajectory comes back.
        """
        if self.points.size == 0:
            return np.empty(0)
        return (self.points - self.base) @ self.tangent

    @property
    def intervals(self) -> np.ndarray:
        """Time between successive crossings -- the period, once settled."""
        return np.diff(self.times)

    def __len__(self) -> int:
        return int(self.times.size)


def poincare_section(problem: ODEProblem, base=None, normal=None, *,
                     start=None, span: float = CYCLE_SPAN, direction: int = 1,
                     rtol: float = CYCLE_RTOL, atol: float = CYCLE_ATOL) -> Section:
    """Cross-sect the flow and record the crossings, one direction only.

    `base` defaults to the starting point and `normal` to the flow direction
    there, which makes the section perpendicular to the trajectory -- the
    transversality the construction requires, obtained rather than assumed.

    One direction only, because both directions would pair each outward
    crossing with the inward one half a loop later and halve the apparent
    period. `direction` says which.
    """
    start = np.asarray(problem.y0 if start is None else start, dtype=float)
    base = start.copy() if base is None else np.asarray(base, dtype=float)
    if normal is None:
        velocity = np.asarray(problem.f(0.0, base), dtype=float)
        length = float(np.linalg.norm(velocity))
        if length < 1e-14:
            raise ValueError("cannot place a section at an equilibrium: the "
                             "flow there has no direction")
        normal = velocity / length
    else:
        normal = np.asarray(normal, dtype=float)
        normal = normal / float(np.linalg.norm(normal))

    offset = base.copy()
    crossed = Event(lambda t, y: float(np.dot(np.asarray(y) - offset, normal)),
                    direction=float(direction), name="section")
    solution = solve(_repose(problem, start, span), method="dopri5",
                     rtol=rtol, atol=atol, events=crossed, dense_output=True)

    times = np.asarray(solution.t_events[0], dtype=float) if solution.t_events else np.empty(0)
    points = (np.asarray(solution.y_events[0], dtype=float)
              if solution.y_events else np.empty((0, 2)))
    # The library reports event states column-wise for some shapes and
    # row-wise for others; settle it against the time count rather than
    # trusting either.
    if points.ndim == 2 and points.shape[0] != times.size and points.shape[1] == times.size:
        points = points.T
    if points.size == 0:
        points = np.empty((0, base.size))

    section = Section(base, normal, times, points, int(direction))
    object.__setattr__(section, "_solution", solution)
    return section


@dataclass(frozen=True)
class LimitCycle:
    """What was found when a system was asked whether it has a closed orbit."""

    #: Time to go round once. NaN when no closed orbit was found.
    period: float
    #: The loop itself, as ``(m, 2)`` -- empty when there is none.
    orbit: np.ndarray
    #: Widest separation of two points on the loop.
    diameter: float
    #: Factor the return map shrinks a displacement by, per circuit. Below one
    #: for an attracting cycle; NaN when it could not be measured.
    contraction: float
    #: Whether a pushed-off orbit came back -- what makes a closed orbit a
    #: *limit* cycle rather than one of a continuum.
    isolated: bool
    #: How far off the pushed orbit settled, relative to the diameter.
    return_error: float
    #: How many returns the closure test saw.
    returns: int
    verdict: str

    @property
    def found(self) -> bool:
        """Whether there is an isolated attracting closed orbit here."""
        return bool(self.isolated and np.isfinite(self.period))

    @property
    def closed(self) -> bool:
        """Whether the orbit closes, isolated or not."""
        return bool(np.isfinite(self.period))

    def __repr__(self) -> str:
        if not self.closed:
            return f"LimitCycle(none: {self.verdict})"
        return (f"LimitCycle(period={self.period:.6g}, "
                f"diameter={self.diameter:.4g}, {self.verdict})")


def _loop_diameter(solution, t0: float, t1: float) -> float:
    """Widest separation between two points of one circuit."""
    samples = solution.sol(np.linspace(t0, t1, CYCLE_SAMPLES))
    return float(np.max(np.linalg.norm(samples[:, :, None] - samples[:, None, :], axis=0)))


def _no_cycle(reason: str) -> LimitCycle:
    return LimitCycle(float("nan"), np.empty((0, 2)), float("nan"), float("nan"),
                      False, float("nan"), 0, reason)


def largest_closed_orbit(problem: ODEProblem, seed=None, *,
                         transient: float = CYCLE_TRANSIENT,
                         span: float = CYCLE_SPAN,
                         should_stop: Callable[[], bool] | None = None) -> LimitCycle:
    """Find the closed orbit a trajectory settles onto, and say what kind it is.

    Returns a `LimitCycle` in every case, including the cases where there is
    none: the verdict is the answer, and "no closed orbit" is as much of an
    answer as a period is.
    """
    seed = np.asarray(problem.y0 if seed is None else seed, dtype=float)
    if seed.size != 2:
        return _no_cycle("only planar systems are handled here")

    settled = solve(_repose(problem, seed, transient), method="dopri5",
                    rtol=CYCLE_RTOL, atol=CYCLE_ATOL)
    base = settled.y[:, -1]
    if should_stop is not None and should_stop():
        return _no_cycle("cancelled")

    velocity = np.asarray(problem.f(0.0, base), dtype=float)
    speed = float(np.linalg.norm(velocity))
    if speed < 1e-12:
        return _no_cycle("the trajectory settles to an equilibrium, not an orbit")

    # A trajectory spiralling into a fixed point also crosses a section over
    # and over, and rejecting it for crossing too few times would be the right
    # answer for the wrong reason -- and would read, to anyone shown it, as
    # "integrate for longer". Compare the speed now with the speed half a
    # transient ago: on an orbit those are the same, and on the way into an
    # equilibrium the first is a fraction of the second.
    half = int(settled.t.size // 2)
    earlier = float(np.linalg.norm(np.asarray(problem.f(0.0, settled.y[:, half]),
                                              dtype=float)))
    if earlier > 0.0 and speed < _DECAY_FRACTION * earlier:
        return _no_cycle(
            "the trajectory is decaying towards an equilibrium -- it is "
            f"moving {earlier / max(speed, 1e-300):.3g} times slower than it "
            "was half a transient ago -- so there is no orbit to close"
        )

    section = poincare_section(problem, base=base, start=base, span=span)
    if len(section) < CYCLE_MIN_RETURNS + 1:
        return _no_cycle(
            f"the trajectory crossed the section {len(section)} times in "
            f"{span:g} time units, too few to judge"
        )

    # Does the loop stop shrinking? Five successive circuits, as required.
    solution = getattr(section, "_solution")
    times = section.times[-(CYCLE_MIN_RETURNS + 1):]
    diameters = np.array([_loop_diameter(solution, times[i], times[i + 1])
                          for i in range(len(times) - 1)])
    if np.any(diameters <= 0.0):
        return _no_cycle("the loop has no extent")
    ratios = diameters[1:] / diameters[:-1]
    if np.any(np.abs(ratios - 1.0) > CYCLE_DIAMETER_TOL):
        worst = float(np.min(ratios))
        return _no_cycle(
            f"the loop is still changing size -- by a factor of {worst:.3g} "
            "per circuit -- so this is a spiral, not a closed orbit"
        )

    period = float(np.mean(np.diff(times)))
    diameter = float(diameters[-1])
    orbit = solution.sol(np.linspace(times[-2], times[-1], CYCLE_SAMPLES))[:2].T

    if should_stop is not None and should_stop():
        return _no_cycle("cancelled")

    isolated, contraction, error = _test_isolation(problem, section, diameter, span)
    if isolated:
        verdict = "an attracting limit cycle: nearby orbits converge to it"
    else:
        verdict = ("a closed orbit, but not an isolated one -- nearby orbits "
                   "stay on closed orbits of their own, as they do around a "
                   "centre, so this is one of a continuum rather than a limit "
                   "cycle")

    return LimitCycle(period, orbit, diameter, contraction, isolated, error,
                      len(diameters), verdict)


def _test_isolation(problem: ODEProblem, section: Section, diameter: float,
                    span: float) -> tuple[bool, float, float]:
    """Push off the orbit and see whether the return map brings it back.

    Returns ``(isolated, contraction, return_error)``. The contraction is the
    geometric mean of successive return distances, measured only over the
    returns that stay above the integrator's noise -- below that the ratio is
    the noise floor dividing by itself, which for a strongly attracting cycle
    is most of the sequence.
    """
    tangent = section.tangent
    pushed = section.base + CYCLE_PUSH * diameter * tangent

    probe = poincare_section(problem, base=section.base, normal=section.normal,
                             start=pushed, span=span)
    coordinates = np.abs(probe.coordinates)
    if coordinates.size < 3:
        return False, float("nan"), float("nan")

    noise = max(1e-9 * diameter, 1e-12)
    usable = coordinates[coordinates > noise]
    if usable.size < 2:
        # It was back inside the noise on the first return: as isolated as the
        # arithmetic can show.
        return True, 0.0, float(coordinates[-1] / diameter)

    steps = usable[1:] / usable[:-1]
    contraction = float(np.exp(np.mean(np.log(steps)))) if steps.size else float("nan")
    error = float(coordinates[-1] / diameter)
    isolated = bool(error < CYCLE_ISOLATION_TOL and contraction < 1.0)
    return isolated, contraction, error
