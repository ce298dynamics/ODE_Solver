"""The bookkeeping `solve` delegates to.

`driver.solve` owns time -- when to step, how far, and when to stop. It kept
four other jobs as well: validating arguments, deciding each step's endpoint,
accumulating output, and tracking events. Each is cohesive on its own and none
needs to be interleaved with the loop, so they live here and `solve` reads as
the loop it is meant to be.

Nothing here contains method-specific mathematics either. That constraint is
what the whole design rests on, and moving code out of one file is not a licence
to relax it.
"""

from __future__ import annotations

import numpy as np

from .controllers import initial_step_size, make_controller
from .events import find_active_events, locate_events, scan_step

__all__ = [
    "prepare_tolerances",
    "prepare_controller",
    "prepare_t_eval",
    "StepPlanner",
    "Recorder",
    "EventTracker",
    "underflow_message",
    "fixed_step_message",
    "insufficient_progress_message",
    "projected_steps",
    "PROGRESS_CHECK_AFTER",
    "PROGRESS_CHECK_EVERY",
]

#: Below this multiple of the local floating-point spacing, advancing t is a no-op.
MIN_STEP_FACTOR = 10.0


# ---------------------------------------------------------------------------
# Argument validation
# ---------------------------------------------------------------------------


def prepare_tolerances(rtol, atol, max_step: float, n: int):
    """Validate and normalise the tolerances. Returns ``(rtol, atol)``."""
    if rtol <= 0:
        raise ValueError("rtol must be positive")
    # Asking for a relative accuracy near machine epsilon cannot be met by any
    # finite-precision method; nudging it up is friendlier than silently
    # thrashing on rejected steps.
    rtol = max(float(rtol), 10 * np.finfo(float).eps)

    atol = np.asarray(atol, dtype=float)
    if np.any(atol < 0):
        raise ValueError("atol must be non-negative")
    if atol.ndim == 1 and atol.size != n:
        raise ValueError(f"atol vector has length {atol.size}, expected {n}")

    if max_step <= 0:
        raise ValueError("max_step must be positive")
    return rtol, atol


def prepare_controller(stepper, controller, options):
    """Resolve the controller and clear any history it arrives with.

    A controller passed in as an instance is returned unchanged by
    `make_controller`, so it carries the error history of whatever it was used
    for last. The first step of a solve has no history by definition, and
    inheriting one makes the same solve run twice give different answers.
    Resetting here covers every route in, including a caller who reuses one
    deliberately.
    """
    ctrl = make_controller(
        stepper.default_controller if controller is None else controller,
        stepper.error_order,
        **(options or {}),
    )
    ctrl.reset()
    return ctrl


def prepare_t_eval(t_eval, t0: float, tf: float, direction: float):
    """Validate and orient the requested output times."""
    if t_eval is None:
        return None
    arr: np.ndarray = np.asarray(t_eval, dtype=float).ravel()
    if arr.size == 0:
        return arr
    lo, hi = (t0, tf) if direction > 0 else (tf, t0)
    if np.any(arr < lo) or np.any(arr > hi):
        raise ValueError(f"t_eval values must lie within t_span [{lo:g}, {hi:g}]")
    arr = np.sort(arr)
    if direction < 0:
        arr = np.ascontiguousarray(arr[::-1])
    if np.any(np.diff(direction * arr) < 0):
        raise ValueError("t_eval must be sortable in the integration direction")
    return np.ascontiguousarray(arr)


# ---------------------------------------------------------------------------
# Where each step lands
# ---------------------------------------------------------------------------


class StepPlanner:
    """Turns "a step of about this size" into "a step ending exactly here".

    Adaptive and fixed-step methods differ only here, and the difference is not
    cosmetic. A fixed-step method must land on ``t0 + k*h`` computed afresh each
    time rather than on an accumulated sum: repeated addition drifts by
    ``O(n*eps)``, which over a 200 000-step symplectic run is not negligible,
    and it leaves the final step a rounding error short of `tf` -- a crumb many
    orders of magnitude smaller than every other step, harmless numerically but
    enough to make a constant-step method report a huge step-size spread.

    `_reference` is therefore never mutated; deriving the target from a running
    `h_abs` would compound the very drift this exists to remove.
    """

    def __init__(self, stepper, problem, *, first_step, n_steps, max_step,
                 rtol, atol, f0, stats):
        self.t0, self.tf = problem.t0, problem.tf
        self.direction = problem.direction
        self.max_step = max_step
        self.fixed = not stepper.adaptive
        self.total_fixed_steps = 0
        self._reference = 0.0

        span = abs(self.tf - self.t0)
        if self.fixed:
            # A non-adaptive method cannot choose its own step, and must not be
            # allowed to drift into one: the whole point of a symplectic
            # integrator is the constant-step structure preservation.
            if n_steps is not None:
                self.total_fixed_steps = int(n_steps)
                h_abs = span / self.total_fixed_steps
            elif first_step is not None:
                # A step that does not divide the interval exactly leaves a
                # shortened final step, which is correct: overshooting tf would
                # be worse than one uneven step at the end.
                h_abs = abs(float(first_step))
                self.total_fixed_steps = max(1, int(np.ceil(span / h_abs)))
            else:
                raise ValueError(
                    f"{stepper.name} runs at a fixed step size; pass n_steps or "
                    f"first_step"
                )
            self._reference = h_abs
        elif first_step is not None:
            h_abs = abs(float(first_step))
            if h_abs <= 0:
                raise ValueError("first_step must be positive")
            h_abs = min(h_abs, max_step, span)
        else:
            h_abs = initial_step_size(
                problem.f, self.t0, problem.y0, f0, stepper.order,
                self.direction, rtol, atol, max_step,
            )
            stats.nfev += 1
            h_abs = min(h_abs, span)

        self.h_abs = h_abs

    def plan(self, t: float, naccepted: int):
        """Return ``(h, h_abs, t_target, last_step)`` for the next attempt.

        `t_target` is the exact endpoint for a fixed-step run, and None when the
        endpoint is simply ``t + h``.
        """
        h_abs = min(self.h_abs, self.max_step)
        h = self.direction * h_abs

        if self.fixed:
            last_step = naccepted + 1 >= self.total_fixed_steps
            t_target = (
                self.tf if last_step
                else self.t0 + (naccepted + 1) * self.direction * self._reference
            )
            h = t_target - t
            return h, abs(h), t_target, last_step

        # Clamp the final step so the integration lands exactly on tf rather
        # than overshooting and being interpolated back.
        last_step = self.direction * (t + h - self.tf) >= 0
        if last_step:
            h = self.tf - t
            h_abs = abs(h)
        return h, h_abs, None, last_step


#: Steps before the progress projection is trusted at all, and how often it is
#: re-checked after that.
#:
#: 5000 is not a round number chosen for comfort -- it is above every adaptive
#: solve in the benchmark suite that *succeeds*. Radau finishes Robertson over
#: eleven decades of time in 239 steps, Van der Pol at mu=1000 in 1142, OREGO in
#: 947. A stiff solver's step size grows enormously once the transient is past
#: (3.8e6 over that Robertson run), so a projection made early would be wildly
#: pessimistic about exactly the solves that work. Waiting until 5000 steps
#: means the projection is only ever consulted for solves that are not
#: progressing at all.
PROGRESS_CHECK_AFTER = 5000
PROGRESS_CHECK_EVERY = 1000


def projected_steps(t: float, tf: float, h_abs: float, taken: int) -> float:
    """Steps needed to finish, at the step size currently being taken.

    `h_abs` is the controller's latest choice, which is the most *optimistic*
    honest estimate: it is the largest step the solver has managed to justify so
    far, so a projection built on it cannot be accused of assuming the worst.
    """
    remaining = abs(tf - t)
    if h_abs <= 0:
        return float("inf")
    return taken + remaining / h_abs


def insufficient_progress_message(
    name: str, t: float, t0: float, tf: float, taken: int, projected: float,
    max_steps: int, explicit: bool,
) -> str:
    """Why a solve was stopped for making no headway.

    This says only what was counted. It reports the fraction of the interval
    covered and what finishing would cost at the current rate -- both
    arithmetic -- and stops short of asserting that the problem *is* stiff,
    which is a property of the equation and not something a step counter can
    establish. For an explicit method it names the usual cause, hedged, because
    that is the actionable part.
    """
    covered = abs(t - t0) / abs(tf - t0) if tf != t0 else 1.0
    advice = (
        " An explicit method's step size is limited by stability rather than "
        "accuracy on a stiff problem, which is the usual reason for this; an "
        "implicit method (radau, rodas4) has no such limit."
        if explicit
        else ""
    )
    return (
        f"{name} covered {covered:.3%} of the interval in {taken} steps and, at "
        f"the step size it is now taking, would need about {projected:.3g} to "
        f"finish — past the max_steps={max_steps} limit. Stopped early rather "
        f"than grinding to that limit and then reporting the step count.{advice}"
    )


def fixed_step_message(name: str, t: float, what: str) -> str:
    """Why a constant-step method stopped, and what the caller can do about it.

    A method that chooses its own step responds to trouble by taking a smaller
    one. A fixed-step method has no such move -- the step is the caller's
    choice, not the solver's -- so the first failure is the last one, and the
    only useful message is the one that says so and hands the decision back.
    """
    return (
        f"{what} at t={t:.6g}. {name} runs at a fixed step size and cannot "
        f"reduce it: pass a smaller first_step or a larger n_steps, or use an "
        f"adaptive method (dopri5, tsit5) or an A-stable one (radau, rodas4) "
        f"if the problem is stiff"
    )


def underflow_message(t: float, h_abs: float, nonfinite_at: float | None) -> str:
    """Why the step size could not be cut any further.

    Two very different causes reach the same floor, and reporting the symptom
    for both names nothing the caller wrote.
    """
    if nonfinite_at is not None:
        return (
            f"the solution became non-finite at t={nonfinite_at:.6g} and did not "
            f"recover as the step was cut to h={h_abs:.3g}. Either the right-hand "
            f"side returns NaN or inf there, or the solution blows up in finite time"
        )
    return (
        f"step size underflow at t={t:.6g}: required h={h_abs:.3g} is below the "
        f"local floating-point resolution. The solution may be singular or blowing "
        f"up there"
    )


# ---------------------------------------------------------------------------
# Accumulating output
# ---------------------------------------------------------------------------


class Recorder:
    """Collects what the solve produces: samples, interpolants, rejections.

    There are two output modes and the difference is confined here: with
    `t_eval` the reported times are exactly the requested ones, sampled off each
    step's interpolant; without it, every accepted step contributes its
    endpoint.
    """

    def __init__(self, problem, t_eval_arr, direction: float):
        self.n = problem.n
        self.direction = direction
        self._t_eval = t_eval_arr
        self._eval_idx = 0

        self.ts: list[float] = []
        self.ys: list[np.ndarray] = []
        self.interpolants: list = []
        self.rejections: list[tuple[float, float]] = []

        t0 = problem.t0
        if t_eval_arr is None:
            self.ts.append(t0)
            self.ys.append(problem.y0.copy())
        elif t_eval_arr.size and t_eval_arr[0] == t0:
            # A requested sample sitting exactly on t0 is known without
            # interpolation.
            self.ts.append(t0)
            self.ys.append(problem.y0.copy())
            self._eval_idx = 1

    def reject(self, t: float, h_abs: float) -> None:
        self.rejections.append((t, h_abs))

    def accept(self, interp, step_end_t: float, step_end_y: np.ndarray) -> None:
        if interp is not None:
            self.interpolants.append(interp)

        if self._t_eval is None:
            self.ts.append(step_end_t)
            self.ys.append(step_end_y.copy())
            return

        stop = int(
            np.searchsorted(
                self.direction * self._t_eval,
                self.direction * step_end_t,
                side="right",
            )
        )
        if stop > self._eval_idx:
            chunk = self._t_eval[self._eval_idx:stop]
            values = interp(chunk)
            self.ts.extend(chunk.tolist())
            self.ys.extend(values.T)
            self._eval_idx = stop

    def arrays(self):
        t_out = np.asarray(self.ts, dtype=float)
        y_out = np.stack(self.ys, axis=-1) if self.ys else np.empty((self.n, 0))
        rejected = (
            np.asarray(self.rejections, dtype=float)
            if self.rejections
            else np.empty((0, 2), dtype=float)
        )
        return t_out, y_out, rejected


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


class EventTracker:
    """Watches `g` across each step and records where it crosses zero.

    Holds the previous step's `g` values, which is the only state event
    detection needs, and decides between endpoint bracketing and a full sub-step
    scan. The scan is off unless some event asks for it, checked once here
    rather than on every step of every solve.
    """

    def __init__(self, events, args: tuple, t0: float, y0: np.ndarray):
        self.events = events
        self.args = args
        self.scanning = any(ev.subdivisions > 0 for ev in events)
        self.t_events: list[list[float]] = [[] for _ in events]
        self.y_events: list[list[np.ndarray]] = [[] for _ in events]
        self._g = np.array([ev(t0, y0, args) for ev in events]) if events else None
        #: Indices of events known to have had crossings missed. See
        #: `_probe_for_missed_crossings`.
        self.incomplete: set[int] = set()

    def __bool__(self) -> bool:
        return bool(self.events)

    def _probe_for_missed_crossings(self, interp, t, t_new, g_new) -> None:
        """Notice when endpoint bracketing has silently lost crossings.

        Comparing only the two ends of a step misses any *even* number of
        crossings inside it, and misses them without a trace: `g` has the same
        sign at both ends, so nothing looks wrong. It is not an exotic case
        either, because the step size is chosen to resolve `y` and not `g` --
        an event that oscillates faster than the solution is entirely ordinary.
        Measured on a smooth decay with ``g = sin(20t)``: 63 roots exist and
        endpoint comparison finds 7, with nothing to say the other 56 are gone.

        `Event.subdivisions` is the cure and has always been available. What was
        missing is any way to find out that you needed it. One evaluation of `g`
        at the middle of the step is enough to *know*: if the midpoint sign
        opposes both endpoints, at least two crossings happened and at most one
        was reported.

        This detects rather than estimates -- a flag raised here is certain, not
        suspected. It is also not exhaustive: four crossings arranged to agree
        at both ends and the middle would still slip through. It answers "were
        any missed", never "were none missed", and `Solution` says so.
        """
        if self._g is None:
            return              # no events; nothing to probe
        candidates = [
            index
            for index, event in enumerate(self.events)
            # Already scanning, or already known incomplete: either way the
            # answer will not change, so do not pay for the probe.
            if event.subdivisions == 0 and index not in self.incomplete
        ]
        if not candidates:
            return

        midpoint = t + 0.5 * (t_new - t)
        y_mid = interp(midpoint)
        for index in candidates:
            event = self.events[index]
            before, after = float(self._g[index]), float(g_new[index])
            middle = event(midpoint, y_mid, self.args)
            if (before > 0 and after > 0 and middle < 0) or (
                before < 0 and after < 0 and middle > 0
            ):
                self.incomplete.add(index)

    def incomplete_names(self) -> str:
        return ", ".join(self.events[i].name for i in sorted(self.incomplete))

    def process(self, interp, t: float, t_new: float, y_new: np.ndarray):
        """Record any crossings in ``[t, t_new]``.

        Returns ``(step_end_t, step_end_y, terminated)`` -- the step's endpoint,
        truncated to a terminal event if one fired.
        """
        g_new = np.array([ev(t_new, y_new, self.args) for ev in self.events])
        self._probe_for_missed_crossings(interp, t, t_new, g_new)
        bracketed = find_active_events(self._g, g_new, self.events)

        if self.scanning:
            # At least one event wants the step examined from the inside, so the
            # endpoint bracket is not the whole story.
            mask = np.zeros(len(self.events), dtype=bool)
            mask[bracketed] = True
            active, roots = scan_step(
                self.events, mask, interp, t, t_new, self.args, self._g, g_new
            )
        else:
            active, roots = bracketed, None

        step_end_t, step_end_y, terminated = t_new, y_new, False
        if active.size:
            active, roots, terminate_at = locate_events(
                self.events, active, interp, t, t_new, self.args, roots
            )
            for index, root in zip(active, roots):
                self.t_events[index].append(float(root))
                self.y_events[index].append(interp(root))
            if terminate_at is not None:
                step_end_t = float(terminate_at)
                step_end_y = interp(step_end_t)
                terminated = True

        self._g = g_new
        return step_end_t, step_end_y, terminated

    def exhausted_names(self) -> str:
        return ", ".join(ev.name for ev in self.events if ev.is_exhausted())

    def arrays(self, n: int):
        return (
            [np.asarray(v, dtype=float) for v in self.t_events],
            [np.stack(v, axis=-1) if v else np.empty((n, 0)) for v in self.y_events],
        )
