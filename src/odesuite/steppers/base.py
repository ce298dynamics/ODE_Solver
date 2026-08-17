"""The stepper contract.

A stepper advances the solution by exactly one step of a *given* size and
reports what happened. It does not choose the step size, does not decide whether
to accept, does not loop, and does not know about events or output. Those belong
to the controller and the driver.

Keeping that boundary sharp is the reason events, dense output, DAE support and
sensitivities are each written once in this library rather than once per method.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from ..dense import Interpolant

__all__ = ["StepResult", "Stepper"]


@dataclass
class StepResult:
    """Outcome of a single attempted step."""

    y_new: np.ndarray
    #: ``f(t + h, y_new)`` when the method produces it for free (FSAL), else None.
    f_new: np.ndarray | None
    #: Local error estimate as a vector, or None for methods without an estimate.
    error: np.ndarray | None
    #: RHS evaluations consumed.
    nfev: int = 0
    #: Jacobian evaluations consumed (implicit methods, Phase 2).
    njev: int = 0
    #: LU factorisations consumed (implicit methods, Phase 2).
    nlu: int = 0
    #: False when the step could not be completed at all, e.g. Newton diverged.
    ok: bool = True


class Stepper(ABC):
    """Base class for one-step integrators."""

    #: Order of the propagated solution.
    order: int = 1
    #: Order of the embedded estimate; the controller uses this, not `order`.
    error_order: int = 1
    #: Order of the continuous extension this stepper can build.
    interpolant_order: int = 1
    #: Whether the method needs a Jacobian / linear solves.
    implicit: bool = False
    #: False for methods that must run at a constant step size. Symplectic
    #: integrators lose the structure preservation that is their entire purpose
    #: if the step varies, and exponential integrators bake `h` into their
    #: coefficients. Such steppers return no error estimate, and the driver
    #: requires `n_steps` or `first_step` instead of choosing h itself.
    adaptive: bool = True
    #: Whether `step` actually reads the incoming `f`. Exponential and Taylor
    #: methods do not -- one rebuilds the state from its own coefficients, the
    #: other splits the operator itself -- so when no interpolant is needed the
    #: driver can skip evaluating the right-hand side at the step endpoint
    #: entirely, saving one evaluation per step.
    uses_f: bool = True
    #: Whether a non-identity mass matrix is supported.
    supports_mass: bool = False
    #: Controller used when the caller does not name one. Implicit methods
    #: override this: for them a step-size change invalidates the iteration
    #: matrix, so the controller has to weigh a better `h` against an
    #: O(n^3) refactorisation.
    default_controller: str = "pi"
    name: str = "stepper"

    @abstractmethod
    def step(
        self, problem, t: float, y: np.ndarray, f: np.ndarray | None, h: float
    ) -> StepResult:
        """Advance from ``(t, y)`` by `h`. `f` is ``f(t, y)``, already evaluated.

        `f` is None only for steppers that declare ``uses_f = False``: the driver
        skips the endpoint evaluation for them when no interpolant needs it, so
        such a stepper must not read this argument.
        """

    @abstractmethod
    def interpolant(
        self,
        t: float,
        y: np.ndarray,
        f: np.ndarray | None,
        t_new: float,
        y_new: np.ndarray,
        f_new: np.ndarray | None,
    ) -> Interpolant:
        """Build the continuous extension for the step just accepted.

        Called only when dense output, `t_eval` sampling or event location needs
        it, and always immediately after the corresponding `step`, so a stepper
        may rely on internal state cached during that call.
        """

    def set_tolerances(self, rtol: float, atol) -> None:
        """Tell the stepper the integration tolerances. Called once by the driver.

        Only implicit methods need this: their nonlinear solve must be
        terminated relative to the accuracy actually being asked for, since
        solving the stage equations far tighter than the local truncation error
        is pure waste. Explicit methods ignore it.
        """

    def validate(self, problem) -> None:
        """Reject problems this method cannot handle. Called once by the driver."""
        if problem.has_mass and not self.supports_mass:
            raise ValueError(
                f"{self.name} cannot integrate a problem with a mass matrix; "
                f"use an implicit method (radau, rodas4)"
            )

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name}, order={self.order})"
