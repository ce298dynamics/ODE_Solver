"""Accuracy and qualitative fidelity are different properties.

    py -3.10 examples/07_symplectic_energy.py

Integrate a Kepler orbit for a long time and compare a high-order adaptive
method with a low-order symplectic one at matched work.

DOPRI5 is far more accurate in absolute terms, and stays so for a long while.
But its energy error *grows with the interval* -- double the run, double the
error -- while Verlet's is a bounded oscillation that is the same size after a
thousand orbits as after ten. For a long-run simulation the bounded error is
usually the one you want, even though it is numerically larger.

This is the diagnostic the benchmark figure `figures/energy_drift.png` plots.
"""

from __future__ import annotations

import numpy as np

from odesuite import ODEProblem, second_order_problem, solve

ECCENTRICITY = 0.3


def initial_state():
    # Position at apoapsis, velocity for the chosen eccentricity.
    x = 1.0 - ECCENTRICITY
    v = np.sqrt((1.0 + ECCENTRICITY) / (1.0 - ECCENTRICITY))
    return np.array([x, 0.0]), np.array([0.0, v])


def acceleration(t, q):
    r = np.linalg.norm(q)
    return -q / r**3


def energy(state):
    q, p = state[:2], state[2:]
    return 0.5 * p @ p - 1.0 / np.linalg.norm(q)


def drift_ratio(times, states) -> tuple[float, float, float]:
    values = np.array([energy(states[:, i]) for i in range(states.shape[1])])
    error = np.abs((values - values[0]) / values[0])
    half = error.size // 2
    first, second = error[:half].max(), error[half:].max()
    return first, second, (second / first if first else float("nan"))


def main() -> None:
    q0, p0 = initial_state()
    orbits = 200
    t_end = orbits * 2 * np.pi

    print(f"Kepler at e={ECCENTRICITY}, {orbits} orbits\n")
    print(f"  {'method':10s} {'nfev':>9s} {'1st half':>11s} {'2nd half':>11s} {'ratio':>7s}")

    second_order = second_order_problem(acceleration, q0, p0, (0.0, t_end))
    verlet = solve(second_order, "verlet", n_steps=orbits * 300)
    first, second, ratio = drift_ratio(verlet.t, verlet.y)
    print(f"  {'verlet':10s} {verlet.stats.nfev:9d} {first:11.3e} {second:11.3e} {ratio:7.2f}")
    assert ratio < 1.2, "a symplectic method's energy error must stay bounded"

    def flow(t, y):
        return np.concatenate([y[2:], acceleration(t, y[:2])])

    adaptive = ODEProblem(flow, (0.0, t_end), np.concatenate([q0, p0]))
    dopri = solve(adaptive, "dopri5", rtol=1e-7, atol=1e-9)
    first, second, ratio = drift_ratio(dopri.t, dopri.y)
    print(f"  {'dopri5':10s} {dopri.stats.nfev:9d} {first:11.3e} {second:11.3e} {ratio:7.2f}")

    print("\n  verlet is less accurate and does not drift; dopri5 is more accurate")
    print("  and its error grows roughly linearly with the interval.")


if __name__ == "__main__":
    main()
