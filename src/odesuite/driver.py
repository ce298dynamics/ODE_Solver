"""The integration loop.

This is the only place that owns time. It asks the stepper to advance, asks the
controller how far to advance next, locates events, samples output, and stops.
It contains no method-specific mathematics, which is why it will drive the
implicit steppers in Phase 2 unchanged.
"""

from __future__ import annotations

import time
from typing import Any, Sequence

import numpy as np

from .controllers import error_norm, initial_step_size, make_controller
from .dense import ConstantInterpolant, DenseOutput
from .events import find_active_events, locate_events, prepare_events
from .problem import ODEProblem
from .solution import Solution, Stats
from .steppers import make_stepper

__all__ = ["solve"]

#: Below this multiple of the local floating-point spacing, advancing t is a no-op.
_MIN_STEP_FACTOR = 10.0


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
    controller: Any = "pi",
    controller_options: dict | None = None,
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
        ``"pi"`` (default) or ``"i"``, a `Controller` subclass, or an instance.

    Returns
    -------
    Solution
    """
    t_start = time.perf_counter()

    stepper = make_stepper(method)
    stepper.validate(problem)

    if rtol <= 0:
        raise ValueError("rtol must be positive")
    # Asking for a relative accuracy near machine epsilon cannot be met by any
    # finite-precision method; nudging it up is friendlier than silently
    # thrashing on rejected steps.
    rtol = max(float(rtol), 10 * np.finfo(float).eps)
    atol = np.asarray(atol, dtype=float)
    if np.any(atol < 0):
        raise ValueError("atol must be non-negative")
    if atol.ndim == 1 and atol.size != problem.n:
        raise ValueError(f"atol vector has length {atol.size}, expected {problem.n}")
    if max_step <= 0:
        raise ValueError("max_step must be positive")

    stepper.set_tolerances(rtol, atol)
    ctrl = make_controller(controller, stepper.error_order, **(controller_options or {}))

    t0, tf, direction = problem.t0, problem.tf, problem.direction
    t = t0
    y = problem.y0.copy()
    stats = Stats()

    f = problem.f(t, y)
    stats.nfev += 1

    event_list = prepare_events(events)
    t_eval_arr = _prepare_t_eval(t_eval, t0, tf, direction)

    # An interpolant is needed for any of these three consumers; when none of
    # them is present we skip building one and save the work.
    need_interp = dense_output or t_eval_arr is not None or bool(event_list)

    # -- output buffers --------------------------------------------------
    ts: list[float] = []
    ys: list[np.ndarray] = []
    rejections: list[tuple[float, float]] = []
    interpolants = []
    t_events: list[list[float]] = [[] for _ in event_list]
    y_events: list[list[np.ndarray]] = [[] for _ in event_list]
    eval_idx = 0

    if t_eval_arr is None:
        ts.append(t)
        ys.append(y.copy())
    elif t_eval_arr.size and t_eval_arr[0] == t0:
        # A requested sample sitting exactly on t0 is known without interpolation.
        ts.append(t0)
        ys.append(y.copy())
        eval_idx = 1

    g_old = (
        np.array([ev(t, y, problem.args) for ev in event_list])
        if event_list
        else None
    )

    # -- initial step size -----------------------------------------------
    fixed_step = not stepper.adaptive
    total_fixed_steps = 0
    if fixed_step:
        # A non-adaptive method cannot choose its own step, and must not be
        # allowed to drift into one: the whole point of a symplectic integrator
        # is the constant-step structure preservation.
        if n_steps is not None:
            total_fixed_steps = int(n_steps)
            h_abs = abs(tf - t0) / total_fixed_steps
        elif first_step is not None:
            # A step that does not divide the interval exactly leaves a
            # shortened final step, which is correct: overshooting tf would be
            # worse than one uneven step at the end.
            h_abs = abs(float(first_step))
            total_fixed_steps = max(1, int(np.ceil(abs(tf - t0) / h_abs)))
        else:
            raise ValueError(
                f"{stepper.name} runs at a fixed step size; pass n_steps or "
                f"first_step"
            )
        fixed_h = h_abs
    elif first_step is not None:
        h_abs = abs(float(first_step))
        if h_abs <= 0:
            raise ValueError("first_step must be positive")
        h_abs = min(h_abs, max_step, abs(tf - t0))
    else:
        h_abs = initial_step_size(
            problem.f, t, y, f, stepper.order, direction, rtol, atol, max_step
        )
        stats.nfev += 1
        h_abs = min(h_abs, abs(tf - t0))

    status = "finished"
    message = ""
    terminated = False

    # -- main loop -------------------------------------------------------
    while direction * (t - tf) < 0:
        if stats.nsteps >= max_steps:
            status, message = "failed", f"exceeded max_steps={max_steps}"
            break

        h_floor = _MIN_STEP_FACTOR * abs(np.nextafter(t, direction * np.inf) - t)
        if h_abs < h_floor:
            status, message = (
                "failed",
                f"step size underflow at t={t:.6g}: required h={h_abs:.3g} is below "
                f"the local floating-point resolution",
            )
            break
        if min_step > 0 and h_abs < min_step:
            status, message = (
                "failed",
                f"step size {h_abs:.3g} fell below min_step={min_step:.3g} at t={t:.6g}",
            )
            break

        h_abs = min(h_abs, max_step)
        h = direction * h_abs

        if fixed_step:
            # Land on t0 + k*h rather than accumulating t. Repeated addition
            # drifts by O(n*eps), which over a 200 000-step symplectic run is
            # not negligible, and it leaves the final step a rounding error
            # short of tf -- a crumb many orders of magnitude smaller than
            # every other step, harmless numerically but enough to make a
            # constant-step method report a huge step-size spread.
            #
            # `fixed_h` is the reference and is never mutated; deriving the
            # target from a running h_abs would compound the very drift this
            # is meant to remove.
            index = stats.naccepted
            last_step = index + 1 >= total_fixed_steps
            t_target = tf if last_step else t0 + (index + 1) * direction * fixed_h
            h = t_target - t
            h_abs = abs(h)
        else:
            t_target = None
            # Clamp the final step so the integration lands exactly on tf
            # rather than overshooting and being interpolated back.
            last_step = direction * (t + h - tf) >= 0
            if last_step:
                h = tf - t
                h_abs = abs(h)

        result = stepper.step(problem, t, y, f, h)
        stats.nsteps += 1
        stats.nfev += result.nfev
        stats.njev += result.njev
        stats.nlu += result.nlu

        if not result.ok:
            # The stepper itself failed (Newton divergence in Phase 2). Shrink
            # hard and retry rather than giving up.
            stats.nrejected += 1
            rejections.append((t, abs(h)))
            h_abs *= 0.5
            continue

        y_new = result.y_new
        if not np.all(np.isfinite(y_new)):
            stats.nrejected += 1
            rejections.append((t, abs(h)))
            h_abs *= 0.5
            continue

        if result.error is None:
            err = 0.0
            accepted = True
            factor = 1.0
        else:
            err = error_norm(result.error, y, y_new, rtol, atol)
            accepted = err <= 1.0
            factor = ctrl.update(err, accepted)

        if not accepted:
            stats.nrejected += 1
            rejections.append((t, abs(h)))
            h_abs *= factor
            continue

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

        # -- events ------------------------------------------------------
        step_end_t, step_end_y = t_new, y_new
        if event_list:
            g_new = np.array([ev(t_new, y_new, problem.args) for ev in event_list])
            active = find_active_events(g_old, g_new, event_list)
            if active.size:
                active, roots, terminate_at = locate_events(
                    event_list, active, interp, t, t_new, problem.args
                )
                for i, root in zip(active, roots):
                    t_events[i].append(float(root))
                    y_events[i].append(interp(root))
                if terminate_at is not None:
                    step_end_t = float(terminate_at)
                    step_end_y = interp(step_end_t)
                    terminated = True
            g_old = g_new

        # -- output ------------------------------------------------------
        if interp is not None:
            interpolants.append(interp)

        if t_eval_arr is not None:
            stop = np.searchsorted(
                direction * t_eval_arr, direction * step_end_t, side="right"
            )
            if stop > eval_idx:
                chunk = t_eval_arr[eval_idx:stop]
                values = interp(chunk)
                ts.extend(chunk.tolist())
                ys.extend(values.T)
                eval_idx = stop
        else:
            ts.append(step_end_t)
            ys.append(step_end_y.copy())

        stats.naccepted += 1

        if terminated:
            status = "terminated"
            fired = [ev.name for ev in event_list if ev.is_exhausted()]
            message = f"terminal event {', '.join(fired)} at t={step_end_t:.10g}"
            t, y = step_end_t, step_end_y
            break

        t, y, f = t_new, y_new, f_new
        h_abs *= factor

    else:
        message = f"reached the end of the integration interval at t={tf:g}"

    # -- assemble --------------------------------------------------------
    t_out = np.asarray(ts, dtype=float)
    if ys:
        y_out = np.stack(ys, axis=-1)
    else:
        y_out = np.empty((problem.n, 0))

    sol = None
    if dense_output:
        if not interpolants:
            # The solve produced no accepted step (a terminal event at t0, say);
            # a degenerate single-point interpolant keeps sol callable.
            interpolants = [ConstantInterpolant(t0, problem.y0)]
        sol = DenseOutput(interpolants, problem.n, t_last=t)

    stats.runtime = time.perf_counter() - t_start

    return Solution(
        t=t_out,
        y=y_out,
        status=status,
        message=message,
        rejected=(
            np.asarray(rejections, dtype=float)
            if rejections
            else np.empty((0, 2), dtype=float)
        ),
        sol=sol,
        t_events=[np.asarray(v, dtype=float) for v in t_events],
        y_events=[
            np.stack(v, axis=-1) if v else np.empty((problem.n, 0)) for v in y_events
        ],
        stats=stats,
        method=stepper.name,
    )


def _prepare_t_eval(t_eval, t0: float, tf: float, direction: float):
    """Validate and orient the requested output times."""
    if t_eval is None:
        return None
    arr = np.asarray(t_eval, dtype=float).ravel()
    if arr.size == 0:
        return arr
    lo, hi = (t0, tf) if direction > 0 else (tf, t0)
    if np.any(arr < lo) or np.any(arr > hi):
        raise ValueError(
            f"t_eval values must lie within t_span [{lo:g}, {hi:g}]"
        )
    arr = np.sort(arr)
    if direction < 0:
        arr = arr[::-1]
    if np.any(np.diff(direction * arr) < 0):
        raise ValueError("t_eval must be sortable in the integration direction")
    return np.ascontiguousarray(arr)
