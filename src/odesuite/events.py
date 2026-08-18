"""Event detection: locating the roots of ``g(t, y) = 0`` during integration.

The mechanism is method-agnostic. After each accepted step the driver hands the
event machinery the step's interpolant; a sign change in `g` across the step
brackets a root, which Brent's method then locates on the continuous extension.
Accuracy is therefore limited by the interpolant, not the step size -- which is
why dense output is built in Phase 1 alongside events rather than bolted on.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from scipy.optimize import brentq

__all__ = ["Event", "prepare_events", "find_active_events", "locate_events",
           "scan_step"]


class Event:
    """A scalar function whose zeros are to be detected.

    Parameters
    ----------
    g
        Called as ``g(t, y, *args)``, returning a scalar.
    terminal
        ``False`` to record and continue. ``True`` to stop at the first
        occurrence. An integer ``k`` stops at the k-th occurrence, which is what
        makes something like "simulate exactly 5 bounces" a one-liner.
    direction
        ``+1`` to detect only upward crossings, ``-1`` only downward, ``0`` both.
    name
        Optional label, used in reporting.
    subdivisions
        Sample `g` at this many interior points of each step before looking for
        a sign change. Zero, the default, compares only the two step endpoints.

        Endpoint comparison misses any *even* number of crossings inside a
        single step, silently: `g` has the same sign at both ends, so nothing
        looks wrong. It is not a rare corner either -- an event that oscillates
        faster than the solution does is entirely ordinary, because the step
        size is chosen to resolve `y`, not `g`. Measured on a smooth decay with
        ``g = sin(20t)``: 63 roots exist in the interval and endpoint comparison
        finds 5 of them, with no indication that 58 are missing.

        The cost is `subdivisions` extra evaluations of `g` and of the step
        interpolant per step, which is why this is off unless asked for: for the
        common case of an event that changes sign once, it buys nothing. Set it
        when `g` can wiggle within a step. `scipy.integrate.solve_ivp` has no
        equivalent.
    """

    def __init__(
        self,
        g: Callable[..., float],
        terminal: bool | int = False,
        direction: float = 0.0,
        name: str | None = None,
        subdivisions: int = 0,
    ) -> None:
        if not callable(g):
            raise TypeError("event g must be callable")
        self.g = g
        self.direction = float(direction)
        if int(subdivisions) < 0:
            raise ValueError("subdivisions must be >= 0")
        self.subdivisions = int(subdivisions)
        self.name: str = str(name or getattr(g, "__name__", "event"))

        if terminal is False or terminal is None:
            self.max_count = None
        elif terminal is True:
            self.max_count = 1
        else:
            count = int(terminal)
            if count < 1:
                raise ValueError("terminal count must be >= 1 when given as an int")
            self.max_count = count
        self.count = 0

    @property
    def terminal(self) -> bool:
        return self.max_count is not None

    def __call__(self, t: float, y: np.ndarray, args: tuple = ()) -> float:
        return float(self.g(t, y, *args))

    def is_exhausted(self) -> bool:
        """True once this event has fired its full allowance and should stop the solve."""
        return self.max_count is not None and self.count >= self.max_count

    def __repr__(self) -> str:
        term = "False" if self.max_count is None else str(self.max_count)
        return f"Event({self.name}, terminal={term}, direction={self.direction:g})"


def prepare_events(events) -> list[Event]:
    """Normalise the user's `events` argument into a list of `Event`."""
    if events is None:
        return []
    if isinstance(events, Event) or callable(events):
        events = [events]
    out = []
    for ev in events:
        out.append(ev if isinstance(ev, Event) else Event(ev))
    for ev in out:
        ev.count = 0
    return out


def find_active_events(g_old, g_new, events: list[Event]) -> np.ndarray:
    """Indices of events whose sign change across the step matches their direction.

    The test is *strict* at the start of the step and *inclusive* at the end:
    ``g_old < 0 <= g_new`` is an upward crossing, and the mirror image is a
    downward one. That asymmetry is deliberate and handles the two awkward cases
    correctly at once:

    * A root landing exactly on a step boundary is caught once, at that
      boundary. On the following step ``g_old`` is zero, which no longer
      qualifies, so it is not reported a second time.
    * An event function that is already zero at ``t0`` does not fire there.
      There is no prior history to cross from, and reporting the initial point
      as a detection is spurious -- callers asking "when does the ball hit the
      ground" do not mean "at the moment it was released from ground level".
    """
    g_old = np.asarray(g_old, dtype=float)
    g_new = np.asarray(g_new, dtype=float)

    up = (g_old < 0) & (g_new >= 0)
    down = (g_old > 0) & (g_new <= 0)
    either = up | down

    directions = np.array([ev.direction for ev in events])
    return np.nonzero(
        (up & (directions > 0))
        | (down & (directions < 0))
        | (either & (directions == 0))
    )[0]


def _solve_event(
    event: Event, interpolant, t_old: float, t_new: float, args: tuple
) -> float | None:
    """Locate a single root inside ``[t_old, t_new]`` using the step interpolant."""
    lo, hi = (t_old, t_new) if t_old < t_new else (t_new, t_old)

    def h(t: float) -> float:
        return event(t, interpolant(t), args)

    f_lo, f_hi = h(lo), h(hi)
    # brentq requires a strict sign change; endpoints that are already zero are
    # the answer.
    if f_lo == 0.0:
        return lo
    if f_hi == 0.0:
        return hi
    if np.sign(f_lo) == np.sign(f_hi):
        # The step endpoints bracketed a crossing but the interpolant does not.
        # There is no root to report here, and reporting the step end as one
        # would be a fabricated detection -- a plausible wrong answer of exactly
        # the kind this library's tests exist to catch. Say so instead.
        return None
    return float(brentq(h, lo, hi, xtol=1e-14, rtol=1e-14, maxiter=100))


def scan_step(events, active_mask, interpolant, t_old, t_new, args, g_old, g_new):
    """Find every crossing inside one step, not just one per event.

    Returns ``(indices, roots)`` covering both the endpoint-bracketed crossings
    and any additional ones found by sub-sampling, sorted in integration order
    and with each event's own `direction` respected.

    The sub-interval walk is the whole point: an event with `subdivisions` set
    is examined on `subdivisions + 1` consecutive brackets across the step, so
    two crossings that cancel out at the endpoints are each found on their own
    sub-interval. Events with ``subdivisions == 0`` cost nothing extra -- they
    take the endpoint bracket exactly as before.
    """
    found: list[tuple[float, int]] = []

    for index, event in enumerate(events):
        if event.subdivisions <= 0:
            if active_mask[index]:
                root = _solve_event(event, interpolant, t_old, t_new, args)
                if root is not None:
                    found.append((root, index))
            continue

        # Sample the interpolant across the step and bracket each sub-interval
        # separately. The endpoint values are reused rather than recomputed, so
        # the extra cost is exactly `subdivisions` evaluations of g.
        taus = np.linspace(t_old, t_new, event.subdivisions + 2)
        values = [float(g_old[index])]
        values.extend(
            event(t, interpolant(t), args) for t in taus[1:-1]
        )
        values.append(float(g_new[index]))

        for left in range(len(taus) - 1):
            lo, hi = float(taus[left]), float(taus[left + 1])
            if not _crosses(values[left], values[left + 1], event.direction):
                continue
            root = _solve_event(event, interpolant, lo, hi, args)
            if root is not None:
                found.append((root, index))

    if not found:
        return np.empty(0, dtype=int), np.empty(0, dtype=float)

    found.sort(key=lambda pair: pair[0] if t_new > t_old else -pair[0])
    return (
        np.array([index for _, index in found], dtype=int),
        np.array([root for root, _ in found], dtype=float),
    )


def _crosses(g_lo: float, g_hi: float, direction: float) -> bool:
    """The same sign-change rule as `find_active_events`, for one pair.

    Strict at the left end and inclusive at the right, so a root landing exactly
    on a sub-interval boundary is counted once rather than twice.
    """
    up = g_lo < 0 <= g_hi
    down = g_lo > 0 >= g_hi
    if direction > 0:
        return up
    if direction < 0:
        return down
    return up or down


def locate_events(
    events: list[Event],
    active: np.ndarray,
    interpolant,
    t_old: float,
    t_new: float,
    args: tuple,
    roots: np.ndarray | None = None,
):
    """Refine all active events on a step and decide whether to terminate.

    Returns ``(indices, roots, terminate_at)`` sorted in integration order.
    `terminate_at` is the time of the earliest terminal event that has used up
    its allowance, or None to continue. Simultaneous events are all reported;
    only the trailing ones beyond a terminal root are discarded.
    """
    if roots is not None:
        # Already located, by `scan_step`, which may have found several
        # crossings for a single event within this step.
        located = list(zip(active.tolist(), roots.tolist()))
    else:
        located = [
            (i, _solve_event(events[i], interpolant, t_old, t_new, args))
            for i in active
        ]
    # Drop the events whose bracket did not survive interpolation; they are not
    # detections and must not be counted towards a terminal event's allowance.
    located = [(i, root) for i, root in located if root is not None]
    if not located:
        return np.empty(0, dtype=int), np.empty(0, dtype=float), None

    active = np.array([i for i, _ in located], dtype=int)
    roots = np.array([root for _, root in located], dtype=float)

    order = np.argsort(roots if t_new > t_old else -roots)
    active = active[order]
    roots = roots[order]

    terminate_at = None
    for k, i in enumerate(active):
        events[i].count += 1
        if events[i].is_exhausted():
            terminate_at = float(roots[k])
            active = active[: k + 1]
            roots = roots[: k + 1]
            break

    return active, roots, terminate_at
