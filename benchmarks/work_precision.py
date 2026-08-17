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

from odesuite import ODEProblem, solve
from odesuite.problems import (
    brusselator,
    hires,
    kepler,
    lotka_volterra,
    orego,
    robertson,
    van_der_pol,
)

__all__ = ["Point", "sweep", "scipy_sweep", "run", "plot"]


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
            table[method] = sweep(bench, method, tolerances, reference)
        for method in theirs:
            table[f"scipy:{method}"] = scipy_sweep(bench, method, tolerances, reference)

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


def plot(results, path: str = "work_precision.png"):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = list(results)
    figure, axes = plt.subplots(2, len(names), figsize=(4.2 * len(names), 8.4), squeeze=False)

    for column, name in enumerate(names):
        for label, points in results[name].items():
            if len(points) < 2:
                continue
            errors = [max(p.error, 1e-16) for p in points]
            style = dict(marker="s", ls="--", alpha=0.65) if label.startswith("scipy:") \
                else dict(marker="o", ls="-", lw=1.8)
            axes[0][column].loglog([p.nfev for p in points], errors, label=label, **style)
            axes[1][column].loglog([p.runtime for p in points], errors, label=label, **style)

        axes[0][column].set_title(name)
        axes[0][column].set_xlabel("RHS evaluations")
        axes[1][column].set_xlabel("wall time (s)")
        for row in (0, 1):
            axes[row][column].set_ylabel("relative error at $t_{end}$")
            axes[row][column].grid(True, which="both", alpha=0.25)
            axes[row][column].legend(fontsize=6.5)

    figure.suptitle(
        "Work-precision: down and to the left is better  "
        "(solid = odesuite, dashed = scipy)",
        y=1.0,
    )
    figure.tight_layout()
    figure.savefig(path, dpi=130, bbox_inches="tight")
    print(f"\n  wrote {path}")
    return path


if __name__ == "__main__":
    plot(run())
