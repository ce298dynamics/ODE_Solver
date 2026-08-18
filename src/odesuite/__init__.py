"""odesuite -- a from-scratch ODE solver library.

Quick start
-----------
    from odesuite import ODEProblem, solve

    prob = ODEProblem(lambda t, y: -0.5 * y, t_span=(0, 10), y0=[1.0])
    sol = solve(prob, method="dopri5", rtol=1e-8, dense_output=True)
    sol.y_at(3.7)

Everything is built on four separated concerns -- `ODEProblem` (what to solve),
`Stepper` (advance one step), `Controller` (choose the next step size) and
`solve` (the loop) -- so that events, dense output and, from Phase 2, mass
matrices and Jacobian handling are implemented once and work with every method.
"""

from __future__ import annotations

from .bvp import BVProblem, BVPSolution, solve_bvp
from .controllers import (
    Controller,
    IController,
    PIController,
    PredictiveController,
    error_norm,
    initial_step_size,
)
from .dense import DenseOutput, HermiteInterpolant, Interpolant, RKPolynomialInterpolant
from .driver import solve
from .events import Event
from .problem import ODEProblem
from .sensitivity import SensitivitySolution, forward_sensitivities
from .solution import Solution, Stats
from .steppers import (
    ETDRK4,
    METHODS,
    CompositionMethod,
    ExplicitRungeKutta,
    Jet,
    RadauIIA,
    Rosenbrock,
    Stepper,
    StepResult,
    StormerVerlet,
    TaylorMethod,
    make_stepper,
    second_order_problem,
    semilinear_problem,
)
from .tableaux import TABLEAUX, ButcherTableau, get_tableau

__version__ = "0.2.0"

__all__ = [
    "ODEProblem",
    "solve",
    "Event",
    "Solution",
    "Stats",
    "BVProblem",
    "BVPSolution",
    "solve_bvp",
    "forward_sensitivities",
    "SensitivitySolution",
    "Stepper",
    "StepResult",
    "ExplicitRungeKutta",
    "Rosenbrock",
    "RadauIIA",
    "StormerVerlet",
    "CompositionMethod",
    "TaylorMethod",
    "Jet",
    "ETDRK4",
    "second_order_problem",
    "semilinear_problem",
    "make_stepper",
    "METHODS",
    "ButcherTableau",
    "TABLEAUX",
    "get_tableau",
    "Controller",
    "IController",
    "PIController",
    "PredictiveController",
    "error_norm",
    "initial_step_size",
    "Interpolant",
    "HermiteInterpolant",
    "RKPolynomialInterpolant",
    "DenseOutput",
    "__version__",
]
