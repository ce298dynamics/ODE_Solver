"""Running solves off the UI thread.

Robertson to t=1e11 takes the better part of a second, Van der Pol at mu=1000
several seconds, and a work-precision sweep far longer. Doing any of that on the
GUI thread freezes the window, so every solve goes through a worker here and the
result arrives back as a signal.

Requests carry a monotonically increasing token. When the user drags a slider,
a dozen solves may be in flight at once; the screen keeps only the newest token
and discards the rest as they land, so a slow early solve can never overwrite a
fast later one.

Discarding a result is not the same as not computing it. Until `solve` grew a
`callback`, a superseded job ran to completion anyway -- holding one of four
pool threads for however long Robertson-at-1e11 takes, purely to have its answer
thrown away. Each job now passes a callback that returns False as soon as its
token is stale, so a superseded solve stops at its next step boundary instead of
at the end of the interval.
"""

from __future__ import annotations

import time
import traceback
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from odesuite import Event, solve

from . import diagnostics
from .catalog import CatalogEntry, get

__all__ = ["SolveRequest", "SolveResult", "SolveRunner"]


@dataclass
class SolveRequest:
    """Everything needed to reproduce one solve."""

    problem_key: str
    method: str
    rtol: float
    atol: float
    params: dict[str, float] = field(default_factory=dict)
    dense_output: bool = True
    n_steps: int | None = None
    events: list[Event] = field(default_factory=list)
    max_steps: int = 500_000
    #: Set by the runner; screens use it to ignore stale results.
    token: int = 0

    def build(self):
        """Instantiate the benchmark for these parameters."""
        entry: CatalogEntry = get(self.problem_key)
        return entry, entry.build(self.params)

    def as_code(self) -> str:
        """The `odesuite` snippet that reproduces this solve.

        Powers the "copy as code" action: whatever the user has arrived at by
        dragging sliders, they can paste into a script and get the same result.
        """
        entry = get(self.problem_key)
        lines = [
            "import numpy as np",
            "from odesuite import solve",
            "from odesuite import problems",
            "",
            # `entry.code` shares the argument mapping with `entry.build`, so
            # the snippet cannot drift from what the app actually ran.
            f"bench = {entry.code(self.params)}",
        ]
        if self.n_steps is not None:
            lines.append(
                f"sol = solve(bench.problem, method={self.method!r}, "
                f"n_steps={self.n_steps})"
            )
        else:
            lines.append(
                f"sol = solve(bench.problem, method={self.method!r}, "
                f"rtol={self.rtol:g}, atol={self.atol:g}, dense_output=True)"
            )
        lines += ["", "print(sol.stats)", "print(sol.y[:, -1])"]
        return "\n".join(lines)


@dataclass
class SolveResult:
    """Outcome of a solve, plus everything the screens want to display."""

    request: SolveRequest
    solution: Any = None
    benchmark: Any = None
    entry: CatalogEntry | None = None
    error: str | None = None
    wall_time: float = 0.0

    @property
    def ok(self) -> bool:
        return self.error is None and self.solution is not None and self.solution.success

    @property
    def cancelled(self) -> bool:
        """True when this solve was abandoned because a newer one superseded it.

        Distinct from `ok` being False: nothing went wrong, the answer simply
        stopped being wanted. Screens should ignore these rather than reporting
        them.
        """
        return self.solution is not None and self.solution.status == "cancelled"

    @property
    def status_text(self) -> str:
        if self.error:
            return f"failed — {self.error}"
        if self.solution is None:
            return "no result"
        return self.solution.message or self.solution.status

    def step_sizes(self):
        """``(midpoints, h)`` for the step-size timeline.

        The accepted step points are the only record of how the controller
        behaved, and plotting the gaps between them is what makes adaptivity
        visible.
        """
        t = self.solution.t
        if t.size < 2:
            return np.empty(0), np.empty(0)
        h = np.diff(t)
        midpoints = 0.5 * (t[:-1] + t[1:])
        return midpoints, np.abs(h)

    def invariant_drift(self):
        """Relative drift of the problem's conserved quantity, if it has one."""
        if self.benchmark is None or getattr(self.benchmark, "invariant", None) is None:
            return None, None
        y = self.solution.y
        reference = self.benchmark.invariant(y[:, 0])
        if abs(reference) < 1e-30:
            return None, None
        values = np.array(
            [self.benchmark.invariant(y[:, i]) for i in range(y.shape[1])]
        )
        return self.solution.t, np.abs(values - reference) / abs(reference)


class _Signals(QObject):
    finished = Signal(object)   # SolveResult


class _Job(QRunnable):
    def __init__(self, request: SolveRequest, signals: _Signals, is_stale=None) -> None:
        super().__init__()
        self.request = request
        self.signals = signals
        self.is_stale = is_stale
        self.setAutoDelete(True)

    def run(self) -> None:  # executed on a pool thread
        started = time.perf_counter()
        try:
            entry, bench = self.request.build()
            kwargs: dict[str, Any] = dict(
                method=self.request.method,
                dense_output=self.request.dense_output,
                max_steps=self.request.max_steps,
            )
            if self.request.n_steps is not None:
                kwargs["n_steps"] = self.request.n_steps
            else:
                kwargs["rtol"] = self.request.rtol
                kwargs["atol"] = self.request.atol
            if self.request.events:
                kwargs["events"] = self.request.events

            # Returning False stops the solve. Checked once per accepted step,
            # which is a token comparison against an int -- far cheaper than the
            # step it follows.
            if self.is_stale is not None:
                kwargs["callback"] = lambda t, y, stats: not self.is_stale()

            solution = solve(bench.problem, **kwargs)
            result = SolveResult(
                request=self.request,
                solution=solution,
                benchmark=bench,
                entry=entry,
                wall_time=time.perf_counter() - started,
            )
        except Exception as exc:                      # surfaced in the UI, not swallowed
            result = SolveResult(
                request=self.request,
                error=f"{type(exc).__name__}: {exc}",
                wall_time=time.perf_counter() - started,
            )
            result.traceback = traceback.format_exc()  # type: ignore[attr-defined]
        self.signals.finished.emit(result)


class SolveRunner(QObject):
    """Submits solves to a thread pool and reports the results.

    Emits `finished` for every completed job, and `latest` only for the job
    that is still the newest at the moment it lands. Screens that just want
    "the current answer" connect to `latest` and need no staleness logic of
    their own.
    """

    finished = Signal(object)   # SolveResult (any job that ran to completion)
    latest = Signal(object)     # SolveResult (newest job only)
    started = Signal(object)    # SolveRequest

    def __init__(self, parent: QObject | None = None, max_threads: int = 4) -> None:
        super().__init__(parent)
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(max_threads)
        self._signals = _Signals()
        self._signals.finished.connect(self._on_finished)
        self._token = 0
        self._newest = 0
        self._supersede_newest = 0
        self._cancelled_before = 0

    def submit(self, request: SolveRequest, supersede: bool = False) -> int:
        """Queue a solve. Returns its token.

        `supersede` marks the request as one of a "only the newest matters"
        series -- a slider being dragged, say. Submitting another superseding
        request then *stops* the earlier ones at their next step boundary rather
        than letting them run to completion for an answer nobody will read.
        Cancelled jobs emit neither `finished` nor `latest`.

        It is opt-in because concurrency is not always supersession: the Method
        Race submits one solve per method through this same runner and wants
        every one of them. Defaulting to supersede would have silently cancelled
        all but the last.
        """
        self._token += 1
        request.token = self._token
        self._newest = self._token
        if supersede:
            self._supersede_newest = self._token
        self.started.emit(request)
        self._pool.start(
            _Job(request, self._signals, self._stale_check(request.token, supersede))
        )
        return request.token

    def _stale_check(self, token: int, supersede: bool):
        """A zero-argument predicate the worker thread polls once per step.

        Reads ints written by the GUI thread. Safe without a lock under CPython,
        and the cost of a stale read is one extra step of a solve that was about
        to stop anyway.
        """

        def is_stale() -> bool:
            if token <= self._cancelled_before:
                return True
            return supersede and token != self._supersede_newest

        return is_stale

    def cancel_all(self) -> None:
        """Stop every solve currently in flight, superseding or not.

        For screen teardown and for an explicit Cancel: without it, leaving a
        screen mid-solve keeps the pool working on an answer nobody will read.
        """
        self._cancelled_before = self._token

    def _on_finished(self, result: SolveResult) -> None:
        if result.cancelled:
            # Superseded before it finished. Nobody wants it, and emitting it
            # would let a screen render a partial trajectory as if it were the
            # answer.
            return
        # REL-04. Every failure that reaches a screen also goes to the local
        # log, so there is something to paste when reporting it. Here rather
        # than in the job, because this runs on the interface thread: two pool
        # threads appending to one file at once is a race the log need not have.
        diagnostics.record_result(result)
        self.finished.emit(result)
        if result.request.token == self._newest:
            self.latest.emit(result)

    def wait(self, milliseconds: int = 30_000) -> bool:
        """Block until the queue drains. For tests and headless rendering."""
        return self._pool.waitForDone(milliseconds)
