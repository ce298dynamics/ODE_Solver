"""What a solve returns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np

from .dense import DenseOutput

__all__ = ["Stats", "Solution", "Diagnosis", "DiagnosisKind"]


#: Why a solve ended, as something a caller can branch on.
#:
#: Deliberately *not* finer than the loop can actually tell. There is no
#: ``"blow_up"`` and no ``"nan_right_hand_side"`` because the driver cannot
#: distinguish them -- a state that goes non-finite and never recovers looks the
#: same either way, and `underflow_message` has always said so in prose. A
#: diagnosis that claimed the difference would be a confident guess, which is
#: the failure mode this whole type exists to remove.
DiagnosisKind = Literal[
    "finished",              # reached the end of the interval
    "terminal_event",        # an event used up its allowance
    "cancelled",             # the callback asked to stop
    "max_steps",             # the safety valve tripped
    "insufficient_progress",  # could not finish within max_steps at this rate
    "min_step",              # the caller's own floor was hit
    "step_underflow",        # h fell below the local floating-point spacing
    "nonfinite",             # the state went non-finite and did not recover
    "fixed_step_nonfinite",  # ditto, for a method that cannot shrink h
    "fixed_step_failure",    # a fixed-step method's step could not be completed
]


@dataclass(frozen=True)
class Diagnosis:
    """Why a solve ended, in a form other code can act on.

    `Solution.message` says the same thing in prose, and stays the thing to show
    a person. This is for the caller that has to *decide* something -- offer a
    stiff solver, mark a trajectory as ending in a singularity, retry with a
    smaller step -- and could previously only have done it by matching on
    English.
    """

    kind: DiagnosisKind
    #: Where it happened. The end of the interval for a clean finish.
    t: float
    #: Anything specific to the kind, for a message a person will read.
    detail: str = ""

    @property
    def failed(self) -> bool:
        return self.kind not in ("finished", "terminal_event", "cancelled")

    def __str__(self) -> str:
        return f"{self.kind} at t={self.t:.6g}" + (
            f": {self.detail}" if self.detail else ""
        )


@dataclass
class Stats:
    """Work counters. The denominator of every efficiency claim in the benchmarks."""

    nfev: int = 0        # RHS evaluations
    njev: int = 0        # Jacobian evaluations
    nlu: int = 0         # LU factorisations
    nsteps: int = 0      # steps attempted
    naccepted: int = 0
    nrejected: int = 0
    runtime: float = 0.0  # wall seconds

    @property
    def reject_ratio(self) -> float:
        return self.nrejected / self.nsteps if self.nsteps else 0.0

    def __str__(self) -> str:
        parts = [
            f"nfev={self.nfev}",
            f"steps={self.naccepted}/{self.nsteps}",
            f"rejected={self.nrejected}",
        ]
        if self.njev:
            parts.append(f"njev={self.njev}")
        if self.nlu:
            parts.append(f"nlu={self.nlu}")
        parts.append(f"{self.runtime * 1e3:.1f}ms")
        return "  ".join(parts)


@dataclass
class Solution:
    """The result of `solve`.

    Attributes
    ----------
    t, y
        Output times ``(k,)`` and states ``(n, k)``. `y` is column-oriented so
        that ``y[:, j]`` is the state at ``t[j]`` and ``y[i]`` is the trajectory
        of component `i` -- the latter is what plotting wants.
    sol
        Continuous solution, or None if dense output was not requested.
    t_events, y_events
        Per-event arrays of detection times and states. Empty arrays for events
        that never fired.
    status
        ``"finished"``, ``"terminated"`` (a terminal event stopped it),
        ``"cancelled"`` (a `solve` callback returned False), or ``"failed"``.
    """

    t: np.ndarray
    y: np.ndarray
    status: str = "finished"
    message: str = ""
    #: Rejected step attempts as ``(m, 2)`` columns ``(t, h)``.
    #:
    #: The accepted steps alone say where the solver ended up but not where it
    #: struggled. A rejection is the controller discovering the step it chose
    #: was too ambitious, so these points mark exactly where the solution got
    #: hard -- the relaxation jumps of a stiff oscillator, a near-collision in
    #: an n-body problem. Rejections are rare by design, so recording them
    #: costs essentially nothing.
    rejected: np.ndarray = field(
        default_factory=lambda: np.empty((0, 2), dtype=float)
    )
    sol: DenseOutput | None = None
    t_events: list[np.ndarray] = field(default_factory=list)
    y_events: list[np.ndarray] = field(default_factory=list)
    stats: Stats = field(default_factory=Stats)
    method: str = ""
    #: Why the solve ended, in a form that can be branched on. `message` is the
    #: same thing in prose and remains what to show a person.
    diagnosis: Diagnosis | None = None
    #: Names of events for which crossings are *known* to have been missed,
    #: because a mid-step probe found `g` on the far side of zero from both
    #: endpoints. Endpoint bracketing loses any even number of crossings inside
    #: a step, silently; this is how you find out it happened. Empty does not
    #: prove completeness -- see `events_complete`.
    incomplete_events: tuple[str, ...] = ()

    @property
    def success(self) -> bool:
        """True when the solve produced the trajectory it was asked for.

        ``"cancelled"`` is deliberately *not* success. Nothing went wrong -- the
        caller asked to stop -- but the requested interval was not integrated,
        and code that checks `success` before using `y[:, -1]` as an endpoint
        would otherwise read a partial result as a complete one. Use
        `Solution.cancelled` to tell a deliberate stop from a failure.
        """
        return self.status in ("finished", "terminated")

    @property
    def cancelled(self) -> bool:
        """True when a `solve` callback stopped the integration."""
        return self.status == "cancelled"

    @property
    def events_complete(self) -> bool:
        """False when crossings are known to have been missed.

        True means "nothing was caught going missing", which is weaker than
        "nothing went missing" and deliberately so: the probe behind
        `incomplete_events` sees an even number of crossings inside one step,
        and four arranged to agree at both ends and the middle would still slip
        past. The honest reading is that False is certain and True is not.

        Set `Event.subdivisions` to close the gap where it matters.
        """
        return not self.incomplete_events

    @property
    def n(self) -> int:
        return self.y.shape[0]

    def y_at(self, t):
        """Evaluate the continuous solution. Requires ``dense_output=True``."""
        if self.sol is None:
            raise RuntimeError(
                "no continuous solution available; call solve(..., dense_output=True)"
            )
        return self.sol(t)

    def __call__(self, t):
        return self.y_at(t)

    def __repr__(self) -> str:
        return (
            f"Solution({self.method}, status={self.status!r}, "
            f"n={self.n}, points={self.t.size}, {self.stats})"
        )
