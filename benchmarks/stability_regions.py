"""Stability-region atlas: contours of |R(z)| = 1 for every method.

The stability function ``R(z)`` is what a method returns after one step of the
Dahlquist test problem ``y' = lambda y`` from ``y = 1`` with ``h = 1``, so that
``z = h*lambda``. The region where ``|R(z)| <= 1`` is where errors decay rather
than grow, and its shape is the whole story of which problems a method can
handle:

* An **explicit** method has a polynomial `R`, so ``|R|`` blows up far from the
  origin and the region is bounded. That bound is the stability restriction: on
  a stiff problem `h` is capped by ``|h*lambda_max|`` no matter how loose the
  tolerance.
* An **A-stable** method covers the entire left half-plane -- no restriction at
  all for a decaying mode.
* An **L-stable** method is A-stable *and* has ``R(z) -> 0`` as
  ``z -> -infinity``, so the stiffest modes are annihilated in a single step
  rather than merely not amplified. That is what makes Radau and RODAS4 behave
  well on Robertson.

`R` is measured rather than derived. Writing out the stability function of a
Rosenbrock method by hand is error-prone and would have to be redone for every
family; running the actual stepper on the test equation works for all of them,
exercises the shipping code path, and cannot disagree with the implementation.
"""

from __future__ import annotations

import numpy as np

from odesuite import make_stepper
from odesuite.stability import classify_stability, stability_function, stability_grid

__all__ = ["stability_function", "stability_summary", "plot_atlas"]


def stability_summary(methods, verbose: bool = True) -> dict[str, dict]:
    """Classify each method: real-axis interval, A-stability, L-stability."""
    return {
        str(method): classify_stability(method, verbose=verbose)
        for method in methods
    }


def plot_atlas(explicit=None, implicit=None, path: str = "stability_regions.png"):
    """Draw |R(z)| = 1 for the explicit and implicit families side by side."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    explicit = explicit or ["rk23", "rkf45", "cashkarp", "dopri5", "tsit5"]
    implicit = implicit or ["rodas4", "radau"]

    figure, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    # Explicit: bounded regions, so a modest window suffices.
    re = np.linspace(-5.0, 2.0, 320)
    im = np.linspace(-4.5, 4.5, 320)
    for method in explicit:
        R = stability_grid(method, re, im)
        axes[0].contour(re, im, R, levels=[1.0], linewidths=1.8)
        axes[0].plot([], [], label=make_stepper(method).name)
    axes[0].set_title("Explicit methods: |R(z)| = 1\n(bounded region = stability limits h)")

    # Implicit: the interesting behaviour is the whole left half-plane.
    re = np.linspace(-30.0, 12.0, 320)
    im = np.linspace(-20.0, 20.0, 320)
    for method in implicit:
        R = stability_grid(method, re, im)
        axes[1].contourf(re, im, R, levels=[0.0, 1.0], alpha=0.25)
        axes[1].contour(re, im, R, levels=[1.0], linewidths=1.8)
        axes[1].plot([], [], label=make_stepper(method).name)
    axes[1].set_title("Implicit methods: stable region shaded\n(A-stable: covers the left half-plane)")

    for ax in axes:
        ax.axhline(0.0, lw=0.6, color="0.6")
        ax.axvline(0.0, lw=0.6, color="0.6")
        ax.set_xlabel(r"Re$(h\lambda)$")
        ax.set_ylabel(r"Im$(h\lambda)$")
        ax.legend(loc="upper left", fontsize=9)
        ax.set_aspect("equal")

    figure.tight_layout()
    figure.savefig(path, dpi=140)
    print(f"  wrote {path}")
    return path


if __name__ == "__main__":
    print("Stability classification (measured, not derived):")
    stability_summary(["rk23", "rkf45", "cashkarp", "dopri5", "tsit5", "rodas4", "radau"])
    print()
    plot_atlas()
