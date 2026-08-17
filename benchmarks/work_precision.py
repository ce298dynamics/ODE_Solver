"""Work-precision diagrams: achieved accuracy against the work it cost.

The canonical way to compare integrators, and the only fair one. Comparing
methods at a fixed tolerance says nothing -- tolerances are requests, not
guarantees, and different methods honour them differently. What matters is the
accuracy actually delivered per unit of work, traced out by sweeping the
tolerance over several decades.

Two work measures are plotted because they answer different questions.
Right-hand-side evaluations are implementation-independent and are the right
metric when `f` is expensive (the usual case in practice). Wall time captures
everything else -- linear algebra, Python overhead, memory traffic -- and is
what a user actually waits for.

`scipy.integrate.solve_ivp` is included as a reference implementation. Note the
asymmetry: scipy is used only as a *comparison target* here and as a
cross-validation oracle in the tests. Correctness is established independently
by the convergence suite, so none of the accuracy claims in this project rest on
scipy being right.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp as scipy_solve_ivp

from odesuite import solve
from odesuite.problems import (
    brusselator,
    hires,
    kepler,
    lotka_volterra,
    orego,
    robertson,
    van_der_pol,
)

__all__ = ["Point", "sweep", "scipy_sweep", "run", "plot", "save", "load"]

#: Timing repeats. Every wall-clock number published from this module is the
#: best of this many runs -- the minimum rather than the mean, because the
#: noise here is one-sided: a run can be slowed by the machine but never
#: sped up below the work it actually has to do.
#:
#: This is enough to stabilise the numbers *within* a run and not enough to
#: compare *across* runs. Two sweeps taken minutes apart on the same machine
#: were seen to differ by 30-60% in the same direction, which was very nearly
#: read as a regression in a change that had in fact reduced the work by a
#: fifth. Comparing two versions means interleaving them in one process,
#: alternating A and B so machine drift lands on both equally -- not running
#: one, editing, and running the other.
REPEATS = 3


@dataclass
class Point:
    tol: float
    error: float
    nfev: int
    runtime: float
    steps: int


def _reference(bench):
    """A trustworthy reference endpoint.

    For non-stiff problems the Taylor method at order 30 is the natural choice:
    it is far more accurate than any fifth-order pair can be, and it is
    algorithmically independent of everything being measured against it.
    """
    problem = bench.problem
    if bench.stiff:
        return solve(problem, method="radau", rtol=1e-13, atol=1e-15).y[:, -1]
    sol = solve(problem, method="taylor30", rtol=1e-14, atol=1e-16)
    if not sol.success:
        sol = solve(problem, method="dopri5", rtol=1e-13, atol=1e-15)
    return sol.y[:, -1]


def _relative_error(y, reference) -> float:
    """Norm-based relative error.

    Deliberately not componentwise: on a periodic problem an individual
    component routinely passes through zero at the endpoint, and dividing by it
    reports a huge "relative error" for a solution that is in fact excellent.
    Measuring the error vector against the norm of the state avoids that.
    """
    return float(
        np.linalg.norm(y - reference) / max(float(np.linalg.norm(reference)), 1e-10)
    )


def sweep(bench, method, tolerances, reference, repeats: int = 1) -> list[Point]:
    """Solve `bench` at each tolerance and record accuracy against work."""
    points = []
    for tol in tolerances:
        best = None
        for _ in range(repeats):
            start = time.perf_counter()
            sol = solve(bench.problem, method=method, rtol=tol, atol=tol * 1e-3,
                        max_steps=2_000_000)
            elapsed = time.perf_counter() - start
            if best is None or elapsed < best[0]:
                best = (elapsed, sol)
        elapsed, sol = best
        if not sol.success:
            continue
        points.append(
            Point(tol, _relative_error(sol.y[:, -1], reference), sol.stats.nfev,
                  elapsed, sol.stats.naccepted)
        )
    return points


def scipy_sweep(bench, method, tolerances, reference, repeats: int = 1) -> list[Point]:
    """The same sweep through `scipy.integrate.solve_ivp`."""
    problem = bench.problem
    jac = (lambda t, y: problem.jac(t, y)) if problem.has_jac else None
    points = []
    for tol in tolerances:
        best = None
        for _ in range(repeats):
            start = time.perf_counter()
            try:
                sol = scipy_solve_ivp(
                    lambda t, y: problem.f(t, y),
                    (problem.t0, problem.tf),
                    problem.y0,
                    method=method,
                    rtol=tol,
                    atol=tol * 1e-3,
                    **({"jac": jac} if method in ("Radau", "BDF", "LSODA") and jac else {}),
                )
            except Exception:
                sol = None
            elapsed = time.perf_counter() - start
            if best is None or elapsed < best[0]:
                best = (elapsed, sol)
        elapsed, sol = best
        if sol is None or not sol.success:
            continue
        points.append(
            Point(tol, _relative_error(sol.y[:, -1], reference), sol.nfev,
                  elapsed, len(sol.t) - 1)
        )
    return points


#: (benchmark factory, our methods, scipy methods, tolerance range)
SUITES = [
    ("lotka_volterra", lotka_volterra,
     ["rk23", "rkf45", "cashkarp", "dopri5", "tsit5", "taylor20"],
     ["RK23", "RK45", "DOP853"], np.logspace(-4, -12, 9)),
    ("brusselator", brusselator,
     ["dopri5", "tsit5", "radau", "taylor20"],
     ["RK45", "DOP853", "Radau"], np.logspace(-4, -12, 9)),
    ("kepler", lambda: kepler(0.5, 2.0),
     ["dopri5", "tsit5", "taylor20"],
     ["RK45", "DOP853"], np.logspace(-4, -13, 10)),
    ("robertson", robertson,
     ["radau", "rodas4"], ["Radau", "BDF", "LSODA"], np.logspace(-4, -11, 8)),
    ("hires", hires,
     ["radau", "rodas4"], ["Radau", "BDF", "LSODA"], np.logspace(-4, -11, 8)),
    # OREGO and Van der Pol are cut off two decades earlier: RODAS4 recomputes
    # its Jacobian every step, so at 1e-11 it takes minutes without changing the
    # shape of the curve.
    ("orego", orego,
     ["radau", "rodas4"], ["Radau", "BDF", "LSODA"], np.logspace(-4, -9, 6)),
    ("van_der_pol_1000", lambda: van_der_pol(mu=1000.0),
     ["radau", "rodas4"], ["Radau", "BDF", "LSODA"], np.logspace(-5, -9, 5)),
]


def run(names=None, verbose: bool = True):
    """Run every suite and return ``{suite: {label: [Point, ...]}}``."""
    results = {}
    for name, factory, ours, theirs, tolerances in SUITES:
        if names and name not in names:
            continue
        bench = factory()
        reference = _reference(bench)
        if verbose:
            print(f"\n{name}  (n={bench.problem.n}, {'stiff' if bench.stiff else 'non-stiff'})")
        table = {}
        for method in ours:
            table[method] = sweep(bench, method, tolerances, reference, REPEATS)
        for method in theirs:
            table[f"scipy:{method}"] = scipy_sweep(
                bench, method, tolerances, reference, REPEATS
            )

        if verbose:
            for label, points in table.items():
                if not points:
                    continue
                tightest = points[-1]
                print(
                    f"    {label:16s} best err={tightest.error:.2e} "
                    f"nfev={tightest.nfev:8d} steps={tightest.steps:7d} "
                    f"{tightest.runtime * 1e3:8.1f}ms"
                )
        results[name] = table
    return results


def save(results, path: str = "work_precision.json") -> str:
    """Write the sweep to JSON.

    Two reasons. The figure can be redrawn without re-running a suite that
    takes minutes; and a committed result file turns a performance change
    into a reviewable diff instead of something noticed by eye months later.
    """
    import json

    payload = {
        suite: {
            label: [
                {"tol": p.tol, "error": p.error, "nfev": p.nfev,
                 "runtime": p.runtime, "steps": p.steps}
                for p in points
            ]
            for label, points in table.items()
        }
        for suite, table in results.items()
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=1, sort_keys=True)
    print(f"  wrote {path}")
    return path


def load(path: str = "work_precision.json"):
    """Read back what `save` wrote."""
    import json

    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    return {
        suite: {label: [Point(**row) for row in rows] for label, rows in table.items()}
        for suite, table in payload.items()
    }


def plot(results, path: str = "work_precision.png", max_cols: int = 4):
    """Render the sweep.

    Each suite occupies a column of two panels: accuracy against evaluations,
    and accuracy against wall time. Columns wrap after `max_cols`, because the
    alternative -- one row of every suite side by side -- produced a figure
    nearly 4 000 px wide in which no legend was legible at any sane display
    size. A grid that wraps stays readable as the suite list grows.
    """
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    names = list(results)
    cols = min(max_cols, len(names)) or 1
    blocks = -(-len(names) // cols)          # ceil
    rows = 2 * blocks

    figure = Figure(figsize=(4.6 * cols, 4.3 * rows))
    FigureCanvasAgg(figure)
    axes = figure.subplots(rows, cols, squeeze=False)

    for index, name in enumerate(names):
        block, column = divmod(index, cols)
        top, bottom = axes[2 * block][column], axes[2 * block + 1][column]

        for label, points in results[name].items():
            if len(points) < 2:
                continue
            errors = [max(p.error, 1e-16) for p in points]
            style = (
                dict(marker="s", ls="--", alpha=0.6, lw=1.3, ms=4)
                if label.startswith("scipy:")
                else dict(marker="o", ls="-", lw=1.9, ms=4.5)
            )
            top.loglog([p.nfev for p in points], errors, label=label, **style)
            bottom.loglog([p.runtime for p in points], errors, label=label, **style)

        top.set_title(name, fontsize=11, pad=6)
        top.set_xlabel("RHS evaluations", fontsize=9)
        bottom.set_xlabel("wall time (s)", fontsize=9)
        for ax in (top, bottom):
            ax.set_ylabel("relative error at $t_{end}$", fontsize=9)
            ax.grid(True, which="major", alpha=0.28, lw=0.6)
            ax.grid(True, which="minor", alpha=0.12, lw=0.4)
            ax.tick_params(labelsize=8)
            ax.legend(fontsize=7.5, framealpha=0.85)

    # Hide the leftover panels of a partly-filled final block.
    for index in range(len(names), blocks * cols):
        block, column = divmod(index, cols)
        axes[2 * block][column].set_visible(False)
        axes[2 * block + 1][column].set_visible(False)

    figure.suptitle(
        "Work-precision: down and to the left is better  "
        "(solid = odesuite, dashed = scipy)",
        fontsize=13,
    )
    figure.tight_layout(rect=(0, 0, 1, 0.985))
    figure.savefig(path, dpi=120)
    print(f"  wrote {path}")
    return path


if __name__ == "__main__":
    plot(run())
