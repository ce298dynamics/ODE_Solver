"""The arithmetic of a Runge-Kutta step, laid out the way a course teaches it.

A textbook introduces Euler and RK4 as a table you fill in by hand: at each row,
evaluate the right-hand side, multiply by `h`, add. The rest of this application
shows what a *solver* does -- adaptive steps, error estimates, stability -- which
is a different subject and, for someone meeting the methods for the first time,
the wrong one.

Nothing here reimplements a method. The rows are produced by the library's own
stepper, so what the table shows is what the method does; `tests/test_byhand.py`
asserts the endpoint agrees with `solve` bit-for-bit. A teaching aid that quietly
computed something else would be worse than none.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from odesuite import ODEProblem, make_stepper

__all__ = ["Row", "Walkthrough", "walk", "refinement", "SUPPORTED"]

#: The two methods a first course does by hand. Both are fixed-step here, which
#: is the point: the student chooses `h`, and sees what that choice costs.
SUPPORTED = ("euler", "rk4")


@dataclass
class Row:
    """One step of the method, as it would be written out."""

    n: int
    t: float
    #: The step actually taken. Equal to the nominal `h` to within an ulp: the
    #: endpoint is computed as ``t0 + (n+1)*h`` and the step is the difference,
    #: so it is the exact distance travelled rather than a repeated addition.
    h: float
    y: np.ndarray
    #: ``f(t_n, y_n)`` -- the slope the method starts from.
    f: np.ndarray
    #: The intermediate slopes, for a multi-stage method. Empty for Euler.
    stages: list[np.ndarray] = field(default_factory=list)
    #: ``y_{n+1} - y_n``: the increment the step contributes.
    increment: np.ndarray = field(default_factory=lambda: np.empty(0))
    y_next: np.ndarray = field(default_factory=lambda: np.empty(0))
    #: The true solution at ``t_{n+1}``, where the problem has one.
    exact_next: np.ndarray | None = None

    @property
    def error(self) -> float | None:
        if self.exact_next is None:
            return None
        return float(np.linalg.norm(self.y_next - self.exact_next))


@dataclass
class Walkthrough:
    """A method applied to a problem at a fixed step size."""

    method: str
    h: float
    rows: list[Row]
    labels: list[str]
    #: True when an exact solution was available to compare against.
    has_exact: bool

    @property
    def final_error(self) -> float | None:
        return self.rows[-1].error if self.rows else None


def walk(problem: ODEProblem, method: str, h: float, n_steps: int = 10,
         exact=None) -> Walkthrough:
    """Take `n_steps` steps of `method` at step size `h`, recording each.

    Uses the library's stepper directly rather than `solve`: there is no
    controller, no rejection and no interpolation to explain away, which is
    exactly the setting a textbook presents.
    """
    if method not in SUPPORTED:
        raise ValueError(
            f"{method!r} is not one of the by-hand methods: {', '.join(SUPPORTED)}"
        )
    if h <= 0:
        raise ValueError("h must be positive")
    if n_steps < 1:
        raise ValueError("n_steps must be at least 1")

    stepper = make_stepper(method)
    t = problem.t0
    y = problem.y0.copy()
    f = problem.f(t, y)

    rows: list[Row] = []
    for n in range(n_steps):
        # Land on `t0 + (n+1)*h` computed afresh, and take the step that reaches
        # it -- which is what the driver does, and why. Accumulating `t` by
        # repeated addition drifts by O(n*eps), so the table would slowly stop
        # being the arithmetic the solver performs. That is recorded bug #4 in
        # the README, and it is just as wrong here as it was there.
        t_next = problem.t0 + (n + 1) * h
        step = t_next - t

        result = stepper.step(problem, t, y, f, step)
        if not result.ok or not np.all(np.isfinite(result.y_new)):
            break

        # The stage derivatives the stepper just used. `_K` is its own record of
        # them, so the table reports the method's arithmetic rather than a
        # second, possibly different, computation of it.
        stages = [np.array(k, copy=True) for k in getattr(stepper, "_K", [])]
        rows.append(
            Row(
                n=n,
                t=t,
                h=step,
                y=y.copy(),
                f=np.array(f, copy=True),
                stages=stages[1:] if len(stages) > 1 else [],
                increment=result.y_new - y,
                y_next=result.y_new.copy(),
                exact_next=(
                    np.atleast_1d(np.asarray(exact(t_next), dtype=float)).reshape(-1)
                    if exact is not None
                    else None
                ),
            )
        )

        t, y = t_next, result.y_new
        f = result.f_new if result.f_new is not None else problem.f(t, y)

    labels = getattr(problem, "state_labels", None) or [
        f"y{i}" for i in range(problem.n)
    ]
    return Walkthrough(
        method=method, h=h, rows=rows, labels=list(labels),
        has_exact=exact is not None,
    )


def refinement(problem: ODEProblem, method: str, h: float, exact,
               levels: int = 4, span: float | None = None):
    """Halve `h` repeatedly and report the endpoint error each time.

    The beginner's version of a convergence study: not a fitted log-log slope
    but four numbers whose ratios are the order. Halving `h` should quarter
    Euler's error and divide RK4's by sixteen, and seeing that happen is the
    point of the exercise.

    Returns a list of ``(h, n_steps, error, ratio)``; `ratio` is None on the
    first row, which has nothing to compare against.
    """
    stepper = make_stepper(method)
    total = span if span is not None else abs(problem.tf - problem.t0)

    out = []
    previous: float | None = None
    for level in range(levels):
        step = h / 2**level
        n_steps = max(1, int(round(total / step)))

        t = problem.t0
        y = problem.y0.copy()
        f = problem.f(t, y)
        for n in range(n_steps):
            t_next = problem.t0 + (n + 1) * step
            result = stepper.step(problem, t, y, f, t_next - t)
            if not result.ok:
                break
            t, y = t_next, result.y_new
            f = result.f_new if result.f_new is not None else problem.f(t, y)

        truth = np.atleast_1d(np.asarray(exact(t), dtype=float)).reshape(-1)
        error = float(np.linalg.norm(y - truth))
        out.append((step, n_steps, error, None if previous is None else previous / error))
        previous = error
    return out
