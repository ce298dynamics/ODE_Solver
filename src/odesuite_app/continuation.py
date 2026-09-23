"""Parameter continuation: where the equilibria go, and where they stop existing.

The phase portrait answers "what does this system do" for one setting of the
parameters. This module answers the question a slider makes people ask without
having a way to see: *what happens as I turn it*. Drag the Brusselator's `b`
upwards and the spiral it settles into stops being stable somewhere; the
portrait shows the before and the after, and nothing shows the crossing itself
or names it.

A bifurcation diagram is the picture that does. Equilibrium coordinate up the
side, parameter along the bottom, solid where the branch is stable and dashed
where it is not -- so a branch that fades from solid to dashed *is* the loss of
stability, drawn, and two branches that run into each other and stop *is* the
pair annihilating.

No Qt here, for the same reason as `analysis.py`: whether the Brusselator's
equilibrium loses stability at ``b = 1 + a^2`` is mathematics, and a wrong
answer would be a wrong answer rather than an ugly picture.

Three things about the method, stated up front because each is a real limit:

**Natural parameter continuation, not pseudo-arclength.** At each parameter
value the equilibria are found by Newton, seeded from the previous value's
solutions and from a coarse grid. That is enough for every bifurcation this
application ships a problem for, and it has one honest failure: a branch that
*turns back* in the parameter -- a fold traversed rather than approached -- is
seen as one branch ending and, possibly, another beginning. The fold is still
detected and reported, because a branch terminating in the interior of the
window is exactly what a fold looks like from here; what cannot be done is
following the curve around it. `Diagram.method_note` says so, and it is shown
in the interface rather than buried here.

**Stability from the eigenvalues, not from the sign of `f`.** For a scalar
equation `analysis.phase_line` deliberately classifies by the sign of `f` on
either side, because that stays right where the derivative vanishes (``y' =
y^2`` is semi-stable and the derivative says "neutral"). Here the opposite
choice is correct: the eigenvalue reaching zero is the *subject* of the
diagram, not an inconvenience, and the crossing is what has to be located.

**Crossings are refined, not read off the grid.** A grid fine enough to place
``b = 1 + a^2`` to within a percent on every parameter range would be
wastefully fine on all of them. The sweep is coarse and each sign change is
then bisected, which costs a handful of extra Newton solves per bifurcation
instead of multiplying the whole sweep.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

import numpy as np

from odesuite import ODEProblem

from .analysis import classify, jacobian_at

__all__ = [
    "BranchPoint",
    "Branch",
    "Bifurcation",
    "Diagram",
    "continue_equilibria",
    "sweep",
    "SADDLE_NODE",
    "HOPF",
    "PITCHFORK",
    "TRANSCRITICAL",
    "STABILITY_CHANGE",
]

#: Parameter samples across the requested range.
#:
#: 161 rather than a round number: an odd count puts a sample exactly on the
#: midpoint of the range, which is where a symmetric problem's bifurcation
#: tends to sit, and 160 intervals divide evenly by 2, 4, 5, 8 and 10 so a
#: slider that stops on a tenth of its travel lands on a sample. The cost is
#: one equilibrium solve per sample, which for a planar system is microseconds.
CONTINUATION_STEPS = 161

#: Grid seeds per axis for the fresh search run alongside the continued one.
#:
#: Deliberately coarser than `find_fixed_points`' default of 11. Its job here
#: is only to *notice* a branch that has just appeared -- once noticed, the
#: previous-point seeding carries it -- and every sample pays for it.
GRID_SEEDS = 7

#: Newton stops when the residual falls below this, and a converged point is
#: rejected if it is above `_ACCEPT_RESIDUAL`.
_NEWTON_TOL = 1e-11
_ACCEPT_RESIDUAL = 1e-7
_NEWTON_STEPS = 40

#: Two equilibria closer than this fraction of the window are the same one.
_MERGE_FRACTION = 1e-4

#: A point at parameter p and a point at the next parameter belong to the same
#: branch if they are no further apart than this fraction of the window.
#:
#: Generous, because equilibria move fastest exactly where the diagram is most
#: interesting: near a fold the position goes as the square root of the
#: distance to it, so consecutive samples separate far more than the parameter
#: step would suggest. Too small and every fold frays into a scatter of
#: one-sample branches. The pairing is greedy over sorted distances rather than
#: nearest-neighbour per point, so a generous cap does not mis-link two
#: branches that pass close: the genuinely closest pair is taken first and both
#: of its endpoints are then spent.
_LINK_FRACTION = 0.2

SADDLE_NODE = "saddle-node"
HOPF = "Hopf"
PITCHFORK = "pitchfork"
TRANSCRITICAL = "transcritical"
STABILITY_CHANGE = "stability change"


@dataclass(frozen=True)
class BranchPoint:
    """One equilibrium, at one value of the parameter."""

    parameter: float
    position: np.ndarray            # (n,)
    eigenvalues: np.ndarray         # (n,) complex
    kind: str                       # "saddle", "stable spiral", "stable", ...
    stability: str                  # STABLE / UNSTABLE / NEUTRAL

    @property
    def growth(self) -> float:
        """The largest real part -- negative when the equilibrium attracts."""
        return float(np.max(self.eigenvalues.real))

    @property
    def oscillatory(self) -> bool:
        """Whether the eigenvalue deciding stability comes as a complex pair.

        Read at the crossing, this is what separates a Hopf bifurcation from a
        steady-state one: the same eigenvalue reaching zero means a pair of
        conjugates leaving the left half-plane together, and an oscillation
        being born, rather than a branch of equilibria appearing or vanishing.
        """
        scale = max(float(np.max(np.abs(self.eigenvalues))), 1e-12)
        leading = np.argmax(self.eigenvalues.real)
        return bool(abs(self.eigenvalues[leading].imag) > 1e-8 * scale)


@dataclass
class Branch:
    """A connected family of equilibria, followed across the parameter."""

    points: list[BranchPoint] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.points)

    @property
    def parameters(self) -> np.ndarray:
        return np.array([p.parameter for p in self.points], dtype=float)

    def coordinate(self, index: int = 0) -> np.ndarray:
        """One component of the equilibrium position, along the branch."""
        return np.array([p.position[index] for p in self.points], dtype=float)

    @property
    def stabilities(self) -> list[str]:
        return [p.stability for p in self.points]

    def segments(self) -> list[tuple[str, int, int]]:
        """Runs of constant stability, as ``(stability, start, stop)`` slices.

        What a renderer wants: one polyline per run, solid or dashed by the
        first element. Adjacent runs share an endpoint so the drawn curve has
        no gap at the crossing -- the line changes style mid-branch, which is
        the whole visual point, and a gap there would read as the branch
        ending.
        """
        if not self.points:
            return []
        runs: list[tuple[str, int, int]] = []
        start = 0
        for i in range(1, len(self.points)):
            if self.points[i].stability != self.points[i - 1].stability:
                runs.append((self.points[start].stability, start, i))
                start = i
        runs.append((self.points[start].stability, start, len(self.points)))
        # Every run after the first starts one sample early, so consecutive
        # polylines share a point and the drawn curve has no gap at the change
        # of style.
        return [(kind, lo - 1 if n else lo, hi)
                for n, (kind, lo, hi) in enumerate(runs)]


@dataclass(frozen=True)
class Bifurcation:
    """A parameter value at which the equilibrium structure changes."""

    parameter: float
    position: np.ndarray
    kind: str
    detail: str

    def __repr__(self) -> str:
        return f"Bifurcation({self.kind} at {self.parameter:.6g})"


@dataclass
class Diagram:
    """The result of one sweep: the branches, and what happens along them."""

    parameter: str
    lo: float
    hi: float
    branches: list[Branch] = field(default_factory=list)
    bifurcations: list[Bifurcation] = field(default_factory=list)
    window: tuple[tuple[float, float], ...] = ()
    #: Set when a branch left the search window rather than ceasing to exist.
    #: The difference matters: one is a fact about the system and the other is
    #: a fact about the box it was looked for in, and a diagram that cannot
    #: tell them apart would report the second as the first.
    clipped: bool = False

    method_note: str = (
        "Natural parameter continuation: equilibria are re-solved at each "
        "parameter value, seeded from the previous one. Branches that turn "
        "back in the parameter are reported where they end but cannot be "
        "followed around the turn."
    )

    def of_kind(self, kind: str) -> list[Bifurcation]:
        return [b for b in self.bifurcations if b.kind == kind]


# ---------------------------------------------------------------------------
# Finding the equilibria at one parameter value
# ---------------------------------------------------------------------------


def _newton(problem: ODEProblem, start: np.ndarray, span: float) -> np.ndarray | None:
    """Newton on ``f(y) = 0`` from `start`, or None if it does not settle.

    The same damped iteration `analysis.find_fixed_points` uses, lifted out
    because it is needed here for an arbitrary number of components and for
    seeds that come from the previous parameter value rather than a grid.
    """
    point = np.asarray(start, dtype=float).copy()
    for _ in range(_NEWTON_STEPS):
        residual = np.asarray(problem.f(0.0, point), dtype=float)
        if np.linalg.norm(residual) < _NEWTON_TOL:
            break
        try:
            step = np.linalg.solve(jacobian_at(problem, point), residual)
        except np.linalg.LinAlgError:
            return None
        if not np.all(np.isfinite(step)):
            return None
        # An almost-singular Jacobian throws the iterate arbitrarily far, which
        # near a fold -- where the Jacobian *is* singular -- is exactly where
        # this runs. Damping keeps it in the neighbourhood it started in.
        length = float(np.linalg.norm(step))
        if length > 0.5 * span:
            step = step * (0.5 * span / length)
        point = point - step
    else:
        return None

    if not np.all(np.isfinite(point)):
        return None
    if np.linalg.norm(np.asarray(problem.f(0.0, point), dtype=float)) > _ACCEPT_RESIDUAL:
        return None
    return point


def _grid(window: Sequence[tuple[float, float]], seeds: int) -> list[np.ndarray]:
    """A Cartesian grid of starting guesses over the window."""
    axes = [np.linspace(lo, hi, seeds) for lo, hi in window]
    mesh = np.meshgrid(*axes, indexing="ij")
    return [np.array(coords, dtype=float) for coords in zip(*(m.ravel() for m in mesh))]


def _inside(point: np.ndarray, window: Sequence[tuple[float, float]]) -> bool:
    return all(lo <= value <= hi for value, (lo, hi) in zip(point, window))


def equilibria_at(problem: ODEProblem,
                  window: Sequence[tuple[float, float]],
                  *,
                  seeds: Sequence[np.ndarray] = (),
                  grid_seeds: int = GRID_SEEDS) -> list[BranchPoint]:
    """Every equilibrium of `problem` inside `window`, classified.

    `seeds` are extra starting guesses -- in a sweep, the previous parameter
    value's answers. They are tried first and they are what makes the sweep
    continuous: a grid alone re-finds the same points independently at each
    step and its answers wander by the grid spacing, which a diagram renders
    as a branch that jitters.
    """
    span = max(hi - lo for lo, hi in window)
    found: list[np.ndarray] = []
    merge = _MERGE_FRACTION * span

    for start in list(seeds) + _grid(window, grid_seeds):
        point = _newton(problem, start, span)
        if point is None or not _inside(point, window):
            continue
        if any(np.linalg.norm(point - other) < merge for other in found):
            continue
        found.append(point)

    results = []
    for point in sorted(found, key=lambda p: tuple(p)):
        values = np.linalg.eigvals(jacobian_at(problem, point))
        kind, stability = _name(values)
        results.append(BranchPoint(0.0, point, values, kind, stability))
    return results


def _name(eigenvalues: np.ndarray) -> tuple[str, str]:
    """Classify an equilibrium from its eigenvalues, in any dimension.

    Two components are the planar taxonomy `analysis.classify` already owns,
    and this defers to it so the two screens can never disagree about what a
    saddle is. One component has no such taxonomy -- a scalar equation has no
    spirals and no saddles -- and anything larger has one too big to be useful
    on a diagram, so both are reduced to the only question the diagram asks:
    does the largest real part sit left of the imaginary axis.
    """
    values = np.asarray(eigenvalues)
    if values.size == 2:
        return classify(values)

    from .analysis import NEUTRAL, STABLE, UNSTABLE

    scale = max(float(np.max(np.abs(values))), 1e-12)
    tolerance = 1e-8 * scale
    growth = float(np.max(values.real))
    if abs(growth) <= tolerance:
        return "non-hyperbolic", NEUTRAL
    if growth < 0.0:
        return "stable", STABLE
    return "unstable", UNSTABLE


# ---------------------------------------------------------------------------
# Following them across the parameter
# ---------------------------------------------------------------------------


def _link(previous: list[BranchPoint], current: list[BranchPoint],
          span: float) -> dict[int, int]:
    """Match each current equilibrium to the previous one it continues.

    Greedy over all pairs in increasing distance rather than nearest-neighbour
    per point, because nearest-neighbour is not symmetric: where two branches
    pass close, both new points can name the same old one as nearest and one
    of them then has to be re-assigned. Taking the globally closest pair first
    and spending both its endpoints gets the crossing right.
    """
    cap = _LINK_FRACTION * span
    pairs = []
    for i, before in enumerate(previous):
        for j, after in enumerate(current):
            distance = float(np.linalg.norm(after.position - before.position))
            if distance <= cap:
                pairs.append((distance, i, j))
    pairs.sort()

    used_before: set[int] = set()
    used_after: set[int] = set()
    matched: dict[int, int] = {}
    for _, i, j in pairs:
        if i in used_before or j in used_after:
            continue
        used_before.add(i)
        used_after.add(j)
        matched[j] = i
    return matched


def continue_equilibria(make_problem: Callable[[float], ODEProblem],
                        values: Sequence[float],
                        window: Sequence[tuple[float, float]],
                        *,
                        parameter: str = "parameter",
                        grid_seeds: int = GRID_SEEDS,
                        should_stop: Callable[[], bool] | None = None) -> Diagram:
    """Follow the equilibria of ``make_problem(value)`` across `values`.

    `make_problem` takes one parameter value and returns the system at it;
    `window` bounds the search, one ``(lo, hi)`` per component.
    """
    values = [float(v) for v in values]
    window = tuple((float(lo), float(hi)) for lo, hi in window)
    span = max(hi - lo for lo, hi in window)

    diagram = Diagram(parameter=parameter, lo=min(values), hi=max(values),
                      window=window)

    branches: list[Branch] = []
    live: dict[int, int] = {}       # index into `previous` -> branch index
    previous: list[BranchPoint] = []

    for value in values:
        if should_stop is not None and should_stop():
            break
        problem = make_problem(value)
        seeds = [p.position for p in previous]
        found = equilibria_at(problem, window, seeds=seeds, grid_seeds=grid_seeds)
        found = [BranchPoint(value, p.position, p.eigenvalues, p.kind, p.stability)
                 for p in found]

        matched = _link(previous, found, span)
        next_live: dict[int, int] = {}
        for j, point in enumerate(found):
            i = matched.get(j)
            if i is not None and i in live:
                index = live[i]
            else:
                branches.append(Branch())
                index = len(branches) - 1
            branches[index].points.append(point)
            next_live[j] = index

        live = next_live
        previous = found

    diagram.branches = [b for b in branches if b.points]
    diagram.clipped = _left_the_window(make_problem, diagram, values, span)
    diagram.bifurcations = _find_bifurcations(make_problem, diagram, span, values)
    return diagram


def _left_the_window(make_problem, diagram: Diagram, values: Sequence[float],
                     span: float) -> bool:
    """Whether any branch stopped because it went outside the search box.

    A branch that leaves the box has not been shown to stop existing; it has
    been shown to leave. Reporting the first as the second is the easiest wrong
    answer this module could give -- and the tempting test, "is the last point
    near the edge", gets it wrong in both directions: an equilibrium moving
    fast can be a visible distance inside the boundary at its last sample and
    well outside at the next, and one that genuinely annihilates on the
    boundary is not clipped at all.

    So the question is asked directly. Continue the branch one more parameter
    step with no window filter at all: if Newton still finds an equilibrium,
    the branch is alive and the box is what ended it.
    """
    if not values:
        return False
    ordered = list(values)
    index_of = {v: i for i, v in enumerate(ordered)}

    for branch in diagram.branches:
        for point, direction in ((branch.points[0], -1), (branch.points[-1], +1)):
            index = index_of.get(point.parameter)
            if index is None:
                continue
            following = index + direction
            if not 0 <= following < len(ordered):
                continue
            beyond = _newton(make_problem(ordered[following]), point.position, span)
            if beyond is not None and not _inside(beyond, diagram.window):
                return True
    return False


# ---------------------------------------------------------------------------
# Naming what happens
# ---------------------------------------------------------------------------


#: Bisection steps used to place a bifurcation between two parameter samples.
#: Twenty halvings take a sample spacing down by a factor of a million, which
#: is far below any accuracy a diagram can show and costs twenty Newton solves.
_REFINE_STEPS = 20


def _solve_near(make_problem: Callable[[float], ODEProblem], value: float,
                guess: np.ndarray, window, span: float) -> BranchPoint | None:
    """The equilibrium near `guess` at parameter `value`, if there is one."""
    problem = make_problem(value)
    point = _newton(problem, guess, span)
    if point is None or not _inside(point, window):
        return None
    values = np.linalg.eigvals(jacobian_at(problem, point))
    kind, stability = _name(values)
    return BranchPoint(value, point, values, kind, stability)


def _refine_stability_crossing(make_problem, branch: Branch, index: int,
                               window, span: float) -> BranchPoint:
    """Bisect the parameter for the zero of the leading real part.

    Between `index` and ``index + 1`` the largest real part changes sign. The
    equilibrium is re-solved at each trial value, seeded from the bracket, so
    the branch is followed rather than re-found -- which matters when several
    equilibria coexist and only one of them is crossing.
    """
    low, high = branch.points[index], branch.points[index + 1]
    p_low, p_high = low.parameter, high.parameter
    guess_low, guess_high = low.position, high.position
    sign_low = np.sign(low.growth)
    best = None

    for _ in range(_REFINE_STEPS):
        middle = 0.5 * (p_low + p_high)
        guess = 0.5 * (guess_low + guess_high)
        found = _solve_near(make_problem, middle, guess, window, span)
        if found is None:
            break
        best = found
        if np.sign(found.growth) == sign_low:
            p_low, guess_low = middle, found.position
        else:
            p_high, guess_high = middle, found.position

    if best is None:
        # Nothing converged in between. The bracket midpoint is still right to
        # the sample spacing, which is the accuracy the sweep was asked for.
        return BranchPoint(0.5 * (low.parameter + high.parameter),
                           0.5 * (low.position + high.position),
                           high.eigenvalues, high.kind, high.stability)
    return best


def _refine_fold(make_problem, absent: float, present: float,
                 guess: np.ndarray, window, span: float) -> float:
    """Bisect the parameter for the value at which the pair appears."""
    for _ in range(_REFINE_STEPS):
        middle = 0.5 * (absent + present)
        if _solve_near(make_problem, middle, guess, window, span) is None:
            absent = middle
        else:
            present = middle
    return 0.5 * (absent + present)


def _count_at(diagram: Diagram, value: float) -> int:
    """How many branches carry a sample at this parameter value."""
    return sum(1 for b in diagram.branches
               if any(p.parameter == value for p in b.points))


#: How far in from a branch end to read its stability.
#:
#: The end itself can be the bifurcation point, where the eigenvalue is zero
#: and its computed sign is noise. Three samples in is past that and still
#: firmly on the same side of it.
_SETTLE_IN = 3


def _settled(branch: Branch, side: str) -> str:
    """The stability of a branch a few samples in from one of its ends."""
    if side == "start":
        return branch.points[min(_SETTLE_IN, len(branch.points) - 1)].stability
    return branch.points[max(-_SETTLE_IN - 1, -len(branch.points))].stability


def _find_bifurcations(make_problem, diagram: Diagram, span: float,
                       values: Sequence[float]) -> list[Bifurcation]:
    found: list[Bifurcation] = []
    window = diagram.window
    ends = (min(values), max(values)) if values else (0.0, 0.0)
    step = (diagram.hi - diagram.lo) / max(len(values) - 1, 1)

    # Folds first, because a pitchfork is recognised partly by a stability
    # crossing that coincides with one, so the folds have to be known already.
    endpoints: list[tuple[BranchPoint, str, str]] = []
    for branch in diagram.branches:
        faces = ((branch.points[0], "start", _settled(branch, "start")),
                 (branch.points[-1], "end", _settled(branch, "end")))
        for point, side, settled in faces:
            if point.parameter in ends:
                continue
            interior = all(lo + 1e-3 * (hi - lo) < v < hi - 1e-3 * (hi - lo)
                           for v, (lo, hi) in zip(point.position, window))
            if interior:
                endpoints.append((point, side, settled))

    fold_parameters: list[float] = []
    used: set[int] = set()
    for i, (a, side_a, settled_a) in enumerate(endpoints):
        if i in used:
            continue
        for j in range(i + 1, len(endpoints)):
            if j in used:
                continue
            b, side_b, settled_b = endpoints[j]
            if side_a != side_b:
                continue
            # Within a sample of each other, not identical. At the fold itself
            # the two roots coincide, so whichever branch happens to catch the
            # double root starts one sample before the other -- requiring the
            # same parameter would miss every fold that lands near a sample.
            if abs(a.parameter - b.parameter) > 1.5 * abs(step):
                continue
            if settled_a == settled_b:
                # Two branches born together with the same stability are a
                # pitchfork's outer pair, not a fold: a saddle-node annihilates
                # an attractor against a repeller, and two attractors cannot
                # annihilate each other. Read a few samples in rather than at
                # the endpoint, because the endpoint may be the degenerate
                # point itself, where the eigenvalue is zero and its sign is
                # whatever the rounding made it.
                continue
            if np.linalg.norm(a.position - b.position) > _LINK_FRACTION * span:
                continue

            # The two names are doing different things -- one is a parameter
            # value the branch reaches and the other is a step past where it
            # stops -- so they are assigned separately rather than as a pair.
            if side_a == "start":
                present = max(a.parameter, b.parameter)
                absent = min(a.parameter, b.parameter) - step
            else:
                present = min(a.parameter, b.parameter)
                absent = max(a.parameter, b.parameter) + step
            midpoint = 0.5 * (a.position + b.position)
            location = _refine_fold(make_problem, absent, present, midpoint,
                                    window, span)
            found.append(Bifurcation(
                location, midpoint, SADDLE_NODE,
                "a stable and an unstable equilibrium meet and annihilate",
            ))
            fold_parameters.append(location)
            used.update((i, j))
            break

    # Then the stability crossings along each branch.
    for branch in diagram.branches:
        for index in range(len(branch.points) - 1):
            before, after = branch.points[index], branch.points[index + 1]
            if before.growth == 0.0:
                continue
            if np.sign(before.growth) == np.sign(after.growth):
                continue
            crossing = _refine_stability_crossing(make_problem, branch, index,
                                                  window, span)
            if before.oscillatory and after.oscillatory:
                found.append(Bifurcation(
                    crossing.parameter, crossing.position, HOPF,
                    "a conjugate pair crosses the imaginary axis, so a "
                    "periodic orbit is born or dies here",
                ))
                continue
            kind, detail = _name_steady_crossing(diagram, crossing, before, after,
                                                 fold_parameters, span)
            found.append(Bifurcation(crossing.parameter, crossing.position,
                                     kind, detail))

    found.sort(key=lambda b: b.parameter)
    return found


def _name_steady_crossing(diagram: Diagram, crossing: BranchPoint,
                          before: BranchPoint, after: BranchPoint,
                          fold_parameters: Sequence[float],
                          span: float) -> tuple[str, str]:
    """Distinguish a pitchfork from a transcritical from an unnamed crossing.

    All three have a real eigenvalue passing through zero, so the eigenvalues
    alone cannot separate them. What separates them is what the *other*
    branches do at the same parameter: a pitchfork changes the number of
    equilibria by two, a transcritical keeps the count and exchanges stability
    between two branches that meet, and anything else is reported as a
    stability change rather than given a name it has not earned.
    """
    count_before = _count_at(diagram, before.parameter)
    count_after = _count_at(diagram, after.parameter)

    if abs(count_before - count_after) == 2:
        verb = "appear alongside it" if count_after > count_before else "merge into it"
        return PITCHFORK, (
            f"the equilibrium changes stability and two more {verb}: the "
            "symmetric case of a steady-state bifurcation"
        )

    tolerance = 1e-6 * max(1.0, abs(crossing.parameter))
    if any(abs(f - crossing.parameter) < tolerance for f in fold_parameters):
        return SADDLE_NODE, "the branch turns and changes stability at the fold"

    if count_before == count_after:
        gap = abs(after.parameter - before.parameter)
        meeting = any(
            abs(p.parameter - crossing.parameter) <= gap
            and 0.0 < float(np.linalg.norm(p.position - crossing.position)) < 0.02 * span
            for b in diagram.branches for p in b.points
        )
        if meeting:
            return TRANSCRITICAL, (
                "two branches meet and exchange stability without either "
                "ceasing to exist"
            )

    return STABILITY_CHANGE, "a real eigenvalue passes through zero"


# ---------------------------------------------------------------------------
# Sweeping a catalogue entry's slider
# ---------------------------------------------------------------------------


#: Parameter values the automatic window is measured at.
#:
#: Three, not one: the equilibria move as the parameter does, and a window
#: framed at the middle of the range can leave the ends of the sweep looking
#: outside it. Taking the union of the three keeps every branch in view without
#: the cost of framing at all 161.
_WINDOW_PROBES = (0.0, 0.5, 1.0)


def _frame_on_equilibria(problem: ODEProblem) -> tuple[tuple[float, float], ...]:
    """A box around the system's own equilibria, not around its trajectory.

    `analysis.default_window` frames the *phase portrait*, and frames it on a
    representative orbit with the equilibria pulled in afterwards, clamped so
    one distant equilibrium cannot zoom the picture out to nothing. Both of
    those are right for a picture and wrong for a search box: the Brusselator's
    equilibrium sits at ``(a, b/a)``, which for ``b = 6`` is outside anything
    framed on an orbit at ``b = 3``, and a branch that leaves the box looks
    like a branch that ends.

    So this frames on the equilibria alone, found over a deliberately wide
    net -- five times the initial condition's own reach in each component.
    """
    y0 = np.asarray(problem.y0, dtype=float).reshape(-1)
    reach = np.maximum(np.abs(y0), 1.0)
    search = tuple((float(a - 5.0 * r), float(a + 5.0 * r)) for a, r in zip(y0, reach))

    positions = [p.position for p in
                 equilibria_at(problem, search, grid_seeds=9)]
    positions.append(y0)
    stacked = np.vstack(positions)

    low, high = stacked.min(axis=0), stacked.max(axis=0)
    extents = high - low
    # A floor on each axis, because an axis on which every equilibrium has the
    # same value -- the velocity of every rest state of an oscillator is zero --
    # would otherwise get a window of zero width and reject its own answers to
    # rounding.
    floor = max(float(extents.max()), 1.0) * 0.1
    pad = np.maximum(0.35 * extents, 0.5 * floor)
    return tuple((float(lo - d), float(hi + d))
                 for lo, hi, d in zip(low, high, pad))


def _automatic_window(make_problem: Callable[[float], ODEProblem],
                      lo: float, hi: float) -> tuple[tuple[float, float], ...]:
    """A search box wide enough for the whole sweep."""
    boxes = [_frame_on_equilibria(make_problem(lo + f * (hi - lo)))
             for f in _WINDOW_PROBES]
    return tuple(
        (min(box[i][0] for box in boxes), max(box[i][1] for box in boxes))
        for i in range(len(boxes[0]))
    )


def sweep(entry, parameter: str, lo: float | None = None, hi: float | None = None,
          *, steps: int = CONTINUATION_STEPS, window=None,
          grid_seeds: int = GRID_SEEDS,
          should_stop: Callable[[], bool] | None = None) -> Diagram:
    """Follow a catalogue entry's equilibria across one of its sliders.

    `lo` and `hi` default to the slider's own range, so the diagram covers
    exactly what the interface lets the user reach -- which is the point of
    drawing it next to the slider.
    """
    specs = {spec.name: spec for spec in entry.params}
    if parameter not in specs:
        available = ", ".join(sorted(specs)) or "none"
        raise KeyError(f"{entry.key!r} has no parameter {parameter!r} (has: {available})")
    spec = specs[parameter]

    lo = spec.low if lo is None else float(lo)
    hi = spec.high if hi is None else float(hi)
    if not hi > lo:
        raise ValueError(f"empty parameter range for {parameter!r}: [{lo}, {hi}]")

    def make_problem(value: float) -> ODEProblem:
        return entry.build({parameter: value}).problem

    # A log slider is swept in log space, for the same reason it is a log
    # slider: sweeping Van der Pol's mu linearly would spend the whole diagram
    # in one regime.
    if spec.log and lo > 0.0:
        values = np.logspace(np.log10(lo), np.log10(hi), steps)
    else:
        values = np.linspace(lo, hi, steps)

    if window is None:
        window = _automatic_window(make_problem, lo, hi)

    diagram = continue_equilibria(make_problem, values, window,
                                  parameter=spec.label or parameter,
                                  grid_seeds=grid_seeds, should_stop=should_stop)
    return diagram
