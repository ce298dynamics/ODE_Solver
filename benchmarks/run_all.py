"""Run every benchmark and regenerate the figures in `figures/`.

    py -3.10 benchmarks/run_all.py

Takes a few minutes, most of it in the work-precision sweeps at tight
tolerances on the stiff problems.
"""

from __future__ import annotations

import pathlib
import sys

FIGURES = pathlib.Path(__file__).resolve().parent.parent / "figures"


def main() -> int:
    FIGURES.mkdir(exist_ok=True)

    import energy_drift
    import ks_spacetime
    import stability_regions
    import work_precision

    print("=" * 72)
    print("1/4  Stability regions")
    print("=" * 72)
    stability_regions.stability_summary(
        ["rk23", "rkf45", "cashkarp", "dopri5", "tsit5", "rodas4", "radau"]
    )
    stability_regions.plot_atlas(path=str(FIGURES / "stability_regions.png"))

    print("\n" + "=" * 72)
    print("2/4  Work-precision diagrams")
    print("=" * 72)
    wp_results = work_precision.run()
    work_precision.plot(wp_results, path=str(FIGURES / "work_precision.png"))
    # Committed alongside the figure, so a performance change is a reviewable
    # diff rather than something spotted by eye in a picture months later.
    work_precision.save(wp_results, path=str(FIGURES / "work_precision.json"))

    print("\n" + "=" * 72)
    print("3/4  Energy drift")
    print("=" * 72)
    _, drift = energy_drift.run()
    energy_drift.plot(drift, path=str(FIGURES / "energy_drift.png"))

    print("\n" + "=" * 72)
    print("4/4  Kuramoto-Sivashinsky")
    print("=" * 72)
    ks_spacetime.compare_cost()
    ks_spacetime.plot(*ks_spacetime.run(), path=str(FIGURES / "ks_spacetime.png"))

    print(f"\nAll figures written to {FIGURES}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    raise SystemExit(main())
