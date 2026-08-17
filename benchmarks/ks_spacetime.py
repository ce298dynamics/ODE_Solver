"""Kuramoto-Sivashinsky: the exponential integrator's showcase.

``u_t = -u_xx - u_xxxx - u u_x`` on a periodic domain. Spectrally discretised the
linear part is diagonal, ``L = k^2 - k^4``, and brutally stiff -- the spectral
radius grows like the fourth power of the mode number, reaching ~4000 at 256
modes and ~65 000 at 512. An explicit method is stability-bound at
``h < 2/|L|max`` regardless of the accuracy it needs.

ETDRK4 handles that linear part exactly through ``exp(hL)`` and so is not bound
at all. The measured consequence at 256 modes is roughly a 24x reduction in
steps and a 45x reduction in wall time against DOPRI5, for comparable accuracy.

The spacetime plot is the familiar KS "flame front": cells that form, drift,
merge and split, never settling -- the canonical low-dimensional route to
spatiotemporal chaos.
"""

from __future__ import annotations

import time

import numpy as np

from odesuite import solve
from odesuite.problems import kuramoto_sivashinsky

__all__ = ["compare_cost", "run", "plot"]


def compare_cost(n_modes: int = 256, t_end: float = 20.0, verbose: bool = True):
    """ETDRK4 against explicit methods on the same stiff problem."""
    bench = kuramoto_sivashinsky(n_modes=n_modes, t_end=t_end)
    L = bench.problem.linear_operator
    spectral_radius = float(np.abs(L).max())

    reference = solve(bench.problem, method="etdrk4", n_steps=40_000)
    u_reference = bench.to_real(reference.y[:, -1])

    if verbose:
        print(f"KS, {n_modes} modes, t in [0, {t_end:g}]")
        print(f"  |L|max = {spectral_radius:.0f}  =>  explicit stability needs "
              f"h < {2 / spectral_radius:.2e}\n")
        print(f"  {'method':18s} {'steps':>8s} {'nfev':>9s} {'error':>11s} {'time':>10s}")

    rows = {}
    configurations = [
        ("etdrk4", dict(n_steps=1000)),
        ("etdrk4", dict(n_steps=2000)),
        ("dopri5", dict(rtol=1e-6, atol=1e-8, max_steps=500_000)),
        ("tsit5", dict(rtol=1e-6, atol=1e-8, max_steps=500_000)),
    ]
    for method, kwargs in configurations:
        start = time.perf_counter()
        sol = solve(bench.problem, method=method, **kwargs)
        elapsed = time.perf_counter() - start
        error = (
            float(np.abs(bench.to_real(sol.y[:, -1]) - u_reference).max())
            if sol.success
            else float("nan")
        )
        label = f"{method}({list(kwargs.values())[0]:g})"
        rows[label] = (sol.stats.naccepted, sol.stats.nfev, error, elapsed)
        if verbose:
            print(
                f"  {label:18s} {sol.stats.naccepted:8d} {sol.stats.nfev:9d} "
                f"{error:11.2e} {elapsed * 1e3:9.0f}ms"
            )
    return rows


def run(n_modes: int = 128, t_end: float = 150.0, n_steps: int = 15_000):
    """Integrate KS far enough onto the attractor for the spacetime plot."""
    bench = kuramoto_sivashinsky(n_modes=n_modes, length=32.0 * np.pi, t_end=t_end)
    start = time.perf_counter()
    sol = solve(bench.problem, method="etdrk4", n_steps=n_steps)
    elapsed = time.perf_counter() - start

    u = bench.to_real(sol.y)
    print(f"\nKS attractor: {n_modes} modes, t to {t_end:g}, {n_steps} ETDRK4 steps, "
          f"{elapsed:.1f}s")
    print(f"  u in [{u.min():.3f}, {u.max():.3f}], "
          f"spatial mean drift {np.abs(u.mean(axis=0)).max():.2e} (conserved at 0)")
    return bench, sol, u


def plot(bench, sol, u, path: str = "ks_spacetime.png"):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(1, 2, figsize=(13, 5.2),
                                gridspec_kw={"width_ratios": [2.2, 1]})

    mesh = axes[0].pcolormesh(
        sol.t, bench.x, u, shading="auto", cmap="RdBu_r",
        vmin=-np.abs(u).max(), vmax=np.abs(u).max(),
    )
    figure.colorbar(mesh, ax=axes[0], label="u(x, t)")
    axes[0].set_xlabel("t")
    axes[0].set_ylabel("x")
    axes[0].set_title("Kuramoto-Sivashinsky, integrated by ETDRK4")

    for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
        index = int(fraction * (sol.t.size - 1))
        axes[1].plot(bench.x, u[:, index], lw=1.2, label=f"t = {sol.t[index]:.0f}")
    axes[1].set_xlabel("x")
    axes[1].set_ylabel("u")
    axes[1].set_title("Snapshots")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.25)

    figure.tight_layout()
    figure.savefig(path, dpi=140)
    print(f"  wrote {path}")
    return path


if __name__ == "__main__":
    compare_cost()
    plot(*run())
