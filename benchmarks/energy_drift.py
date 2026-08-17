"""Energy drift: what a symplectic integrator buys, and what it costs.

The most direct demonstration that accuracy and *fidelity* are different things.
Integrating a Kepler orbit for thousands of periods:

* DOPRI5 is far more accurate per step, and its energy error stays smaller in
  absolute terms for a long time -- but that error **grows linearly with time**.
  Run it long enough and the orbit decays; the qualitative behaviour is wrong.
* Stormer-Verlet is only second order and its energy error is larger, but the
  error is a **bounded oscillation**. It is the same size after a million orbits
  as after ten. The orbit stays an orbit.

The comparison is made at matched work, since a symplectic method's cheapness
per step is part of its case. The diagnostic is the ratio of the worst energy
error in the second half of the run to the worst in the first half: 1.0 means
bounded, 2.0 means it doubled.
"""

from __future__ import annotations

import numpy as np

from odesuite import solve
from odesuite.problems import kepler_second_order

__all__ = ["energy_trace", "run", "plot"]


def energy_trace(sol, bench, samples: int = 1500):
    """Sampled ``|dE/E|`` along a solution, with the matching times."""
    idx = np.unique(
        np.linspace(0, sol.y.shape[1] - 1, min(samples, sol.y.shape[1])).astype(int)
    )
    E0 = bench.invariant(bench.problem.y0)
    drift = np.array([abs(bench.invariant(sol.y[:, i]) - E0) / abs(E0) for i in idx])
    return sol.t[idx], drift


def run(n_orbits: float = 3000.0, force_evaluations_per_orbit: int = 120,
        verbose: bool = True):
    """Integrate Kepler with several methods at roughly matched cost."""
    bench = kepler_second_order(eccentricity=0.3, n_orbits=n_orbits)
    budget = int(n_orbits * force_evaluations_per_orbit)

    configurations = [
        # Verlet costs 2 accelerations per step, Yoshida4 costs 6 (3 substeps).
        ("verlet", dict(n_steps=budget // 2)),
        ("yoshida4", dict(n_steps=budget // 6)),
        ("dopri5", dict(rtol=3e-8, atol=3e-10)),
    ]

    results = {}
    if verbose:
        print(f"Kepler e=0.3, {n_orbits:g} orbits, ~{budget} force evaluations budgeted\n")
        print(f"  {'method':10s} {'nfev':>9s} {'1st-half max':>14s} {'2nd-half max':>14s} "
              f"{'ratio':>7s}  verdict")
    for method, kwargs in configurations:
        sol = solve(bench.problem, method=method, **kwargs)
        t, drift = energy_trace(sol, bench)
        results[method] = (t, drift, sol.stats)

        half = drift.size // 2
        first, second = drift[:half].max(), drift[half:].max()
        ratio = second / max(first, 1e-30)
        if verbose:
            verdict = "bounded" if ratio < 1.5 else f"growing (~{ratio:.1f}x)"
            print(
                f"  {method:10s} {sol.stats.nfev:9d} {first:14.3e} {second:14.3e} "
                f"{ratio:7.2f}  {verdict}"
            )
    return bench, results


def plot(results, path: str = "energy_drift.png"):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(1, 2, figsize=(12.5, 5.0))

    for method, (t, drift, stats) in results.items():
        periods = t / (2 * np.pi)
        label = f"{method}  ({stats.nfev:,} evals)"
        axes[0].plot(periods, drift, lw=0.9, label=label)
        axes[1].loglog(np.maximum(periods, 1e-3), np.maximum(drift, 1e-18), lw=0.9,
                       label=label)

    axes[0].set_yscale("log")
    axes[0].set_xlabel("orbits")
    axes[0].set_ylabel(r"$|\Delta E / E|$")
    axes[0].set_title("Energy error over time (matched work)")

    axes[1].set_xlabel("orbits")
    axes[1].set_ylabel(r"$|\Delta E / E|$")
    axes[1].set_title("Same, log-log: a slope of 1 is linear secular growth")
    # Reference slope for the eye.
    x = np.array([10.0, 3000.0])
    axes[1].plot(x, 1e-9 * x, "k:", lw=1.0, label="slope 1 (linear drift)")

    for ax in axes:
        ax.grid(True, which="both", alpha=0.25)
        ax.legend(fontsize=8, loc="best")

    figure.suptitle(
        "Symplectic integrators: bounded energy error forever; "
        "DOPRI5: more accurate, but drifting"
    )
    figure.tight_layout()
    figure.savefig(path, dpi=140)
    print(f"\n  wrote {path}")
    return path


if __name__ == "__main__":
    _, results = run()
    plot(results)
