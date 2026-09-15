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
    PROGRESS_CHECK_AFTER,
    PROGRESS_CHECK_EVERY,
    EventTracker,
    Recorder,
    StepPlanner,
    fixed_step_message,
    insufficient_progress_message,
    prepare_controller,
    prepare_t_eval,
    prepare_tolerances,
    projected_steps,
    underflow_message,
)
from .controllers import error_norm
from .dense import ConstantInterpolant, DenseOutput
from .events import prepare_events
from .problem import ODEProblem
from .solution import Diagnosis, Solution, Stats
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
    progress_check: bool = True,
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
    progress_check
        Stop early when the step size being taken cannot cover the remaining
        interval within `max_steps`. On by default, because the alternative is
        to spend the whole budget discovering the same thing: an explicit method
        on Robertson takes about 500 000 steps and 17 seconds to conclude it
        cannot finish, and this concludes it in well under one second and says
        why rather than blaming the step count.

        Pass False to let a solve run to `max_steps` regardless -- to time the
        grind, or to demonstrate it. The projection is never applied to a
        fixed-step method, whose total is known from the outset, and never
        before `_loop.PROGRESS_CHECK_AFTER` steps, which is above every adaptive
        solve in the benchmark suite that succeeds.

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
    #: Why the loop stopped, in a form a caller can branch on. Set at every exit.
    diagnosis: Diagnosis | None = None

    # -- main loop -------------------------------------------------------
    while direction * (t - tf) < 0:
        if stats.nsteps >= max_steps:
            status, message = "failed", f"exceeded max_steps={max_steps}"
            diagnosis = Diagnosis("max_steps", t, f"max_steps={max_steps}")
            break

        # Stop a solve that arithmetic says cannot finish, rather than letting
        # it grind to `max_steps` and then blame the step count. An explicit
        # method on a stiff problem takes ~500 000 steps and 17 seconds to
        # arrive at that conclusion; this reaches it in under a second, and says
        # something more useful when it does.
        #
        # Three restrictions, and the third is the one that matters.
        #
        # Not fixed-step: such a run's total is known from the outset.
        #
        # Not before `PROGRESS_CHECK_AFTER` steps: a solve deserves a chance.
        #
        # **Not implicit.** The projection assumes the step size will not
        # improve, and for a stiff solver that assumption is simply false: it
        # spends the transient taking tiny steps and then grows them by orders
        # of magnitude. Measured on Robertson at rtol=1e-12, RODAS4 has covered
        # 0.0000% of the interval after 5000 steps -- indistinguishable from
        # DOPRI5, which never finishes -- and then finishes in 10 017, its step
        # size having grown by a factor of 1.7e8. Coverage cannot separate those
        # two, and neither can step-size growth: RODAS4 on Van der Pol at the
        # same tolerance has *flat* growth and still finishes, in 203 377 steps.
        #
        # So this is not a stiffness detector, and does not pretend to be one.
        # It is a projection, applied only where a projection holds -- to a
        # method whose step size is already as large as it is going to get.
        if (
            progress_check
            and not planner.fixed
            and not stepper.implicit
            and stats.nsteps >= PROGRESS_CHECK_AFTER
            and stats.nsteps % PROGRESS_CHECK_EVERY == 0
        ):
            projected = projected_steps(t, tf, planner.h_abs, stats.nsteps)
            if projected > max_steps:
                status = "failed"
                message = insufficient_progress_message(
                    stepper.name, t, problem.t0, tf, stats.nsteps, projected,
                    max_steps, not stepper.implicit,
                )
                diagnosis = Diagnosis(
                    "insufficient_progress", t,
                    f"about {projected:.3g} steps needed, max_steps={max_steps}",
                )
                break

        h_floor = MIN_STEP_FACTOR * abs(np.nextafter(t, direction * np.inf) - t)
        if planner.h_abs < h_floor:
            status = "failed"
            message = underflow_message(t, planner.h_abs, nonfinite_at)
            # Two situations reach this floor and the loop can tell those two
            # apart -- but no further, and the diagnosis stops where the
            # knowledge does. Neither kind names a single cause because neither
            # has one:
            #
            #   nonfinite       the state went non-finite and never recovered.
            #                   A right-hand side returning NaN or inf, or an
            #                   overflow. Indistinguishable from here.
            #   step_underflow  the state is still finite and it is h that has
            #                   collapsed. A singularity on the path or a
            #                   blow-up in finite time. Also indistinguishable:
            #                   y' = y^2 and y' = 1/(t-1) both land here.
            diagnosis = (
                Diagnosis("nonfinite", nonfinite_at,
                          "a non-finite right-hand side, or an overflow")
                if nonfinite_at is not None
                else Diagnosis("step_underflow", t,
                               f"required h={planner.h_abs:.3g}; the solution may "
                               f"be singular or blowing up there")
            )
            break
        if min_step > 0 and planner.h_abs < min_step:
            status, message = (
                "failed",
                f"step size {planner.h_abs:.3g} fell below min_step={min_step:.3g} "
                f"at t={t:.6g}",
            )
            diagnosis = Diagnosis(
                "min_step", t,
                f"h={planner.h_abs:.3g} below min_step={min_step:.3g}",
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
            if planner.fixed:
                status, message = "failed", fixed_step_message(
                    stepper.name, t, "the step could not be completed"
                )
                diagnosis = Diagnosis(
                    "fixed_step_failure", t,
                    f"{stepper.name} cannot reduce a fixed step",
                )
                break
            planner.h_abs = h_abs * 0.5
            continue

        y_new = result.y_new
        if not np.all(np.isfinite(y_new)):
            stats.nrejected += 1
            recorder.reject(t, abs(h))
            nonfinite_at = t
            # Shrinking is the right answer for a method that chooses its own
            # step and no answer at all for one that cannot: `StepPlanner.plan`
            # derives a fixed step from the interval, so assigning `h_abs` here
            # is overwritten on the next pass and the identical failing step is
            # retried. That is not a slow failure but an unbounded one -- 909393
            # rejections and 13.7 seconds before `max_steps` stopped it, and
            # then blamed the step count for an overflow the loop already knew
            # about.
            if planner.fixed:
                status, message = "failed", fixed_step_message(
                    stepper.name, t, "the solution became non-finite"
                )
                diagnosis = Diagnosis(
                    "fixed_step_nonfinite", t,
                    f"{stepper.name} cannot reduce a fixed step",
                )
                break
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
            diagnosis = Diagnosis("cancelled", step_end_t, "the callback returned False")
            t, y = step_end_t, step_end_y
            break

        if terminated:
            status = "terminated"
            names = tracker.exhausted_names()
            message = f"terminal event {names} at t={step_end_t:.10g}"
            diagnosis = Diagnosis("terminal_event", step_end_t, names)
            t, y = step_end_t, step_end_y
            break

        t, y, f = t_new, y_new, f_new
        planner.h_abs = h_abs * factor

    else:
        message = f"reached the end of the integration interval at t={tf:g}"
        diagnosis = Diagnosis("finished", tf)

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
        diagnosis=diagnosis,
        incomplete_events=tuple(
            tracker.events[i].name for i in sorted(tracker.incomplete)
        ),
    )
