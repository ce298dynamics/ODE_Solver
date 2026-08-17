"""Steppers: one-step integrators, each advancing the solution by a given h."""

from __future__ import annotations

from collections.abc import Callable
from functools import partial

from ..tableaux import TABLEAUX
from .base import Stepper, StepResult
from .erk import ExplicitRungeKutta
from .exponential import ETDRK4, phi_coefficients_contour, semilinear_problem
from .irk import RADAU_IIA_5, RadauIIA
from .rosenbrock import ROSENBROCK_TABLEAUX, Rosenbrock
from .symplectic import (
    SYMPLECTIC_METHODS,
    CompositionMethod,
    StormerVerlet,
    second_order_problem,
)
from .taylor import Jet, TaylorMethod

__all__ = [
    "Stepper",
    "StepResult",
    "ExplicitRungeKutta",
    "Rosenbrock",
    "RadauIIA",
    "RADAU_IIA_5",
    "StormerVerlet",
    "CompositionMethod",
    "second_order_problem",
    "TaylorMethod",
    "Jet",
    "ETDRK4",
    "semilinear_problem",
    "phi_coefficients_contour",
    "make_stepper",
    "METHODS",
    "EXPLICIT_METHODS",
    "IMPLICIT_METHODS",
    "SPECIAL_METHODS",
]

EXPLICIT_METHODS: dict[str, Callable[[], Stepper]] = {
    name: partial(ExplicitRungeKutta, tab) for name, tab in TABLEAUX.items()
}

IMPLICIT_METHODS: dict[str, Callable[[], Stepper]] = {
    name: partial(Rosenbrock, tab) for name, tab in ROSENBROCK_TABLEAUX.items()
}
IMPLICIT_METHODS.update(
    {
        "radau": RadauIIA,
        "radau5": RadauIIA,
        # The unsplit 3n x 3n solve, kept as the oracle the fast path is
        # validated against rather than as a method anyone should choose.
        "radaudense": partial(RadauIIA, linear_solve="dense"),
    }
)

#: Methods that need a problem with extra structure -- a separable second-order
#: system for the symplectic family, a semilinear splitting for ETDRK4 -- or, in
#: the Taylor method's case, a right-hand side expressible in jet arithmetic.
SPECIAL_METHODS: dict[str, Callable[[], Stepper]] = {
    **SYMPLECTIC_METHODS,
    "etdrk4": ETDRK4,
    "taylor": TaylorMethod,
    "taylor8": partial(TaylorMethod, 8),
    "taylor20": partial(TaylorMethod, 20),
    "taylor30": partial(TaylorMethod, 30),
}

#: Names accepted by `solve(..., method=...)`.
METHODS: dict[str, Callable[[], Stepper]] = {
    **EXPLICIT_METHODS,
    **IMPLICIT_METHODS,
    **SPECIAL_METHODS,
}


def make_stepper(method) -> Stepper:
    """Resolve a method name, class, or instance into a `Stepper`."""
    if isinstance(method, Stepper):
        return method
    if isinstance(method, type) and issubclass(method, Stepper):
        return method()
    key = str(method).lower().replace("-", "").replace("_", "")
    if key not in METHODS:
        raise KeyError(
            f"unknown method {method!r}; available: {', '.join(sorted(METHODS))}"
        )
    return METHODS[key]()
