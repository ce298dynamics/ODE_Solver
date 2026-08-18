"""Solve an initial value problem, then evaluate the answer between the steps.

    py -3.10 examples/01_getting_started.py

The point of `dense_output=True` is that a solver's output times are chosen for
the solver's convenience, not yours. With it, the solution becomes a continuous
function you can evaluate anywhere -- and for a good method the interpolant is
almost as accurate as the steps themselves, so this is not resampling, it is
the answer the method already computed.
"""

from __future__ import annotations

import numpy as np

from odesuite import ODEProblem, solve


def lotka_volterra(t, y, alpha=1.5, beta=1.0, delta=1.0, gamma=3.0):
    prey, predator = y
    return np.array([
        alpha * prey - beta * prey * predator,
        delta * prey * predator - gamma * predator,
    ])


def main() -> None:
    problem = ODEProblem(lotka_volterra, t_span=(0.0, 15.0), y0=[1.0, 1.0])
    sol = solve(problem, method="dopri5", rtol=1e-10, atol=1e-12, dense_output=True)

    print(f"status   {sol.status}")
    print(f"stats    {sol.stats}")
    print(f"steps    {sol.t.size} output points over [{sol.t[0]:g}, {sol.t[-1]:g}]")

    # The continuous solution is vectorised over t.
    times = np.linspace(0.0, 15.0, 7)
    values = sol.y_at(times)
    print("\n     t      prey   predator")
    for t, (prey, predator) in zip(times, values.T):
        print(f"  {t:5.2f}  {prey:8.4f}  {predator:8.4f}")

    # Lotka-Volterra conserves V = delta*x - gamma*ln(x) + beta*y - alpha*ln(y).
    # A first integral is the cheapest honest accuracy check available: no
    # reference solution required.
    x, y = sol.y
    invariant = 1.0 * x - 3.0 * np.log(x) + 1.0 * y - 1.5 * np.log(y)
    drift = np.abs(invariant - invariant[0]).max() / abs(invariant[0])
    print(f"\nconserved quantity drifts by {drift:.2e} (relative) over the run")
    assert drift < 1e-8, "the invariant should be conserved at this tolerance"


if __name__ == "__main__":
    main()
