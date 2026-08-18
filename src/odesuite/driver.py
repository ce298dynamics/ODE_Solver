"""The integration loop.

This is the only place that owns time. It asks the stepper to advance, asks the
controller how far to advance next, locates events, samples output, and stops.
It contains no method-specific mathematics, which is why the same loop drives
every method in the library.

The bookkeeping that surrounds the loop -- validating arguments, deciding where
each step lands, accumulating output, tracking events -- lives in `_loop`, so
that what remains here is the loop.
"""

from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any

import numpy as np

from ._loop import (
    MIN_STEP_FACTOR,
    EventTracker,
    Recorder,
    StepPlanner,
    prepare_controller,
    prepare_t_eval,
    prepare_tolerances,
    underflow_message,
)
from .controllers import error_norm
from .dense import ConstantInterpolant, DenseOutput
from .events import prepare_events
from .problem import ODEProblem
from .solution import Solution, Stats
from .steppers import make_stepper

__all__ = ["solve"]


def solve(
    problem: ODEProblem,
    method: Any = "dopri5",
    rtol: float = 1e-6,
    atol: Any = 1e-9,
    t_eval: Sequence[float] | None = None,
    dense_output: bool = False,
    events: Any = None,
    first_step: float | None = None,
    n_steps: int | None = None,
    max_step: float = np.inf,
    min_step: float = 0.0,
    max_steps: int = 1_000_000,
    controller: Any = None,
    controller_options: dict | None = None,
    callback: Any = None,
) -> Solution:
    """Integrate an `ODEProblem`.

    Parameters
    ----------
    problem
        The IVP to solve.
    method
        Method name (``"dopri5"``, ``"tsit5"``, ``"rk45"``, ``"rkf45"``,
        ``"cashkarp"``, ``"rk23"``), a `Stepper` subclass, or an instance.
    rtol, atol
        Relative tolerance (scalar) and absolute tolerance (scalar or per
        component). The local error is held to
        ``atol + rtol * max(|y_old|, |y_new|)`` in an RMS sense.
    t_eval
        Times at which to report the solution. Must lie within `t_span`. When
        given, the returned `t` is exactly these times (truncated if a terminal
        event fires first); the internal steps are unaffected.
    dense_output
        Attach a continuous solution to ``Solution.sol``.
    events
        An `Event`, a bare callable ``g(t, y, *args)``, or a sequence of either.
    first_step
        Override the automatic initial step size.
    max_step, min_step
        Bounds on ``|h|``. A step forced below `min_step` aborts the solve.
    max_steps
        Safety valve on the total number of attempted steps.
    controller
        ``"pi"``, ``"i"``, ``"predictive"``, a `Controller` subclass, or an
        instance. The default, None, lets the method choose: ``"pi"`` for the
        explicit pairs, ``"predictive"`` for the implicit ones.
    callback
        Optional ``callback(t, y, stats) -> bool | None``, called once after
        every accepted step. Returning ``False`` stops the integration and the
        solve comes back with ``status="cancelled"``; any other return value
        (including None) continues.

        One parameter, and it is what makes a long solve *observable* rather
        than a black box that returns eventually: progress reporting, live
        plotting, streaming output to disk, and -- because it can say stop --
        cancellation from another thread. Nothing else in the loop offers a way
        in.

        `y` is the solver's own state array, not a copy. Do not mutate it; copy
        first if it needs to outlive the call. Exceptions propagate rather than
        being swallowed, so a broken callback is not silently ignored.

    Returns
    -------
    Solution
    """
    t_start = time.perf_counter()

    stepper = make_stepper(method)
    stepper.validate(problem)
    rtol, atol = prepare_tolerances(rtol, atol, max_step, problem.n)
    stepper.set_tolerances(rtol, atol)
    ctrl = prepare_controller(stepper, controller, controller_options)

    tf, direction = problem.tf, problem.direction
    t = problem.t0
    y = problem.y0.copy()
    stats = Stats()

    f0 = problem.f(t, y)
    f: np.ndarray | None = f0
    stats.nfev += 1

    tracker = EventTracker(prepare_events(events), problem.args, t, y)
    t_eval_arr = prepare_t_eval(t_eval, t, tf, direction)
    recorder = Recorder(problem, t_eval_arr, direction)
    planner = StepPlanner(
        stepper, problem, first_step=first_step, n_steps=n_steps,
        max_step=max_step, rtol=rtol, atol=atol, f0=f0, stats=stats,
    )

    # An interpolant is needed for any of these three consumers; when none of
    # them is present we skip building one and save the work.
    need_interp = dense_output or t_eval_arr is not None or bool(tracker)

    status = "finished"
    message = ""
    #: Where the state last came back non-finite, cleared by any accepted step.
    #: Halving is the right response to one such attempt -- an over-ambitious
    #: step can overshoot into overflow where a shorter one is fine -- but if it
    #: never recovers, the eventual failure is a NaN, not a step-size problem.
    nonfinite_at: float | None = None

    # -- main loop -------------------------------------------------------
    while direction * (t - tf) < 0:
        if stats.nsteps >= max_steps:
            status, message = "failed", f"exceeded max_steps={max_steps}"
            break

        h_floor = MIN_STEP_FACTOR * abs(np.nextafter(t, direction * np.inf) - t)
        if planner.h_abs < h_floor:
            status = "failed"
            message = underflow_message(t, planner.h_abs, nonfinite_at)
            break
        if min_step > 0 and planner.h_abs < min_step:
            status, message = (
                "failed",
                f"step size {planner.h_abs:.3g} fell below min_step={min_step:.3g} "
                f"at t={t:.6g}",
            )
            break

        h, h_abs, t_target, last_step = planner.plan(t, stats.naccepted)
        planner.h_abs = h_abs

        result = stepper.step(problem, t, y, f, h)
        stats.nsteps += 1
        stats.nfev += result.nfev
        stats.njev += result.njev
        stats.nlu += result.nlu

        if not result.ok:
            # The stepper itself failed -- Newton divergence, or a singular
            # iteration matrix. Shrink hard and retry rather than giving up.
            stats.nrejected += 1
            recorder.reject(t, abs(h))
            planner.h_abs = h_abs * 0.5
            continue

        y_new = result.y_new
        if not np.all(np.isfinite(y_new)):
            stats.nrejected += 1
            recorder.reject(t, abs(h))
            nonfinite_at = t
            planner.h_abs = h_abs * 0.5
            continue

        if result.error is None:
            err, accepted, factor = 0.0, True, 1.0
        else:
            err = error_norm(result.error, y, y_new, rtol, atol)
            accepted = err <= 1.0
            factor = ctrl.update(err, accepted, abs(h))

        if not accepted:
            stats.nrejected += 1
            recorder.reject(t, abs(h))
            planner.h_abs = h_abs * factor
            continue

        # A step landed, so whatever went non-finite earlier was recovered from.
        nonfinite_at = None

        t_new = tf if last_step else (t_target if t_target is not None else t + h)
        f_new = result.f_new
        if f_new is None and (need_interp or stepper.uses_f):
            # Not FSAL. For a method that consumes `f` this is not wasted work:
            # it becomes the first stage of the next step, so the cost is the
            # same as computing it then, and a Hermite interpolant comes free.
            # For a method that ignores `f` it would be pure overhead, so it is
            # skipped unless an interpolant actually needs it.
            f_new = problem.f(t_new, y_new)
            stats.nfev += 1

        interp = (
            stepper.interpolant(t, y, f, t_new, y_new, f_new) if need_interp else None
        )

        step_end_t, step_end_y, terminated = t_new, y_new, False
        if tracker:
            assert interp is not None  # need_interp is true when events exist
            step_end_t, step_end_y, terminated = tracker.process(
                interp, t, t_new, y_new
            )

        recorder.accept(interp, step_end_t, step_end_y)
        stats.naccepted += 1

        if callback is not None and callback(step_end_t, step_end_y, stats) is False:
            status = "cancelled"
            message = f"cancelled by the callback at t={step_end_t:.10g}"
            t, y = step_end_t, step_end_y
            break

        if terminated:
            status = "terminated"
            message = (
                f"terminal event {tracker.exhausted_names()} at t={step_end_t:.10g}"
            )
            t, y = step_end_t, step_end_y
            break

        t, y, f = t_new, y_new, f_new
        planner.h_abs = h_abs * factor

    else:
        message = f"reached the end of the integration interval at t={tf:g}"

    # -- assemble --------------------------------------------------------
    t_out, y_out, rejected = recorder.arrays()
    t_events, y_events = tracker.arrays(problem.n)

    sol = None
    if dense_output:
        interpolants = recorder.interpolants
        if not interpolants:
            # The solve produced no accepted step (a terminal event at t0, say);
            # a degenerate single-point interpolant keeps sol callable.
            interpolants = [ConstantInterpolant(problem.t0, problem.y0)]
        sol = DenseOutput(interpolants, problem.n, t_last=t)

    stats.runtime = time.perf_counter() - t_start

    return Solution(
        t=t_out,
        y=y_out,
        status=status,
        message=message,
        rejected=rejected,
        sol=sol,
        t_events=t_events,
        y_events=y_events,
        stats=stats,
        method=stepper.name,
    )
