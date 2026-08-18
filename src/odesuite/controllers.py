"""Error measurement and step-size selection.

Deliberately separated from the steppers: a controller sees only a scalar error
norm and the method's error order, never the method itself. That is what lets
the same PI controller drive an explicit RK pair in Phase 1 and a Radau solve in
Phase 2 without modification.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

__all__ = [
    "error_norm",
    "initial_step_size",
    "Controller",
    "IController",
    "PIController",
    "PredictiveController",
    "make_controller",
]


def error_norm(err, y_old, y_new, rtol: float, atol) -> float:
    """RMS norm of the local error, weighted by the mixed tolerance.

    ``scale_i = atol_i + rtol * max(|y_old_i|, |y_new_i|)``

    The root-mean-square (rather than max) norm is the standard choice: it stops
    a single stiff component from dominating the step-size decision for a large
    system, and it is what the classical order/efficiency results assume. A
    return value of 1.0 means "exactly at tolerance".
    """
    scale = atol + rtol * np.maximum(np.abs(y_old), np.abs(y_new))
    ratio = np.abs(err) / scale
    return float(np.sqrt(np.mean(np.real(ratio * np.conj(ratio)))))


def initial_step_size(
    f,
    t0: float,
    y0: np.ndarray,
    f0: np.ndarray,
    order: int,
    direction: float,
    rtol: float,
    atol,
    max_step: float = np.inf,
) -> float:
    """Automatic starting step, after Hairer, Norsett & Wanner I, section II.4.

    Two stages: a crude guess from the ratio ``|y0| / |f0|``, then one explicit
    Euler probe to estimate the second derivative and refine. Costs one extra
    RHS evaluation and is dramatically better than any fixed guess -- getting
    this wrong is one of the most common flaws in homemade solvers, which
    typically waste dozens of rejected steps recovering from ``h = (b-a)/100``.
    """
    scale = atol + np.abs(y0) * rtol
    d0 = float(np.sqrt(np.mean(np.abs(y0 / scale) ** 2)))
    d1 = float(np.sqrt(np.mean(np.abs(f0 / scale) ** 2)))

    h0 = 1e-6 if (d0 < 1e-5 or d1 < 1e-5) else 0.01 * d0 / d1

    y1 = y0 + h0 * direction * f0
    f1 = f(t0 + h0 * direction, y1)
    d2 = float(np.sqrt(np.mean(np.abs((f1 - f0) / scale) ** 2))) / h0

    if max(d1, d2) <= 1e-15:
        h1 = max(1e-6, h0 * 1e-3)
    else:
        h1 = (0.01 / max(d1, d2)) ** (1.0 / (order + 1))

    return float(min(100 * h0, h1, max_step))


class Controller(ABC):
    """Maps an error norm to a step-size factor."""

    #: Never grow or shrink by more than these factors in one step.
    min_factor = 0.2
    max_factor = 10.0
    safety = 0.9

    def __init__(self, error_order: int, **kwargs) -> None:
        # The local error of an embedded pair behaves like h^(q+1) where q is
        # the lower of the two orders, so the exponent is 1/(q+1).
        self.k = error_order + 1
        self.exponent = 1.0 / self.k
        for key, value in kwargs.items():
            if not hasattr(type(self), key):
                raise TypeError(f"unknown controller option {key!r}")
            setattr(self, key, value)
        self.reset()

    def reset(self) -> None:
        self.err_prev: float | None = None

    @abstractmethod
    def _factor(self, err: float) -> float: ...

    def update(self, err: float, accepted: bool, h: float | None = None) -> float:
        """Return the multiplicative step-size change for an error norm `err`.

        On rejection the factor is capped at 1 so the step can only shrink, and
        the error history is *not* advanced: feeding a rejected step's error into
        the PI term makes the controller oscillate.

        `h` is the magnitude of the step just attempted. Controllers that read
        only the error ignore it; a predictive controller needs the ratio
        between this step and the last accepted one.
        """
        if err == 0.0:
            factor = self.max_factor
        else:
            factor = self._factor(err)
            factor = float(np.clip(factor, self.min_factor, self.max_factor))

        if accepted:
            self.err_prev = max(err, 1e-4)  # floor damps the derivative term
        else:
            factor = min(factor, 1.0)
        return factor


class IController(Controller):
    """Classical integral controller, ``h_new = h * (1/err)^(1/k)``.

    Simple and robust, but tends to oscillate between accepted and rejected
    steps on problems where the error estimate is noisy. Kept for comparison in
    the benchmarks.
    """

    def _factor(self, err: float) -> float:
        return self.safety * err ** (-self.exponent)


class PIController(Controller):
    """Proportional-integral controller (Gustafsson).

    ``h_new = h * safety * err_n^(-alpha) * err_{n-1}^(beta)``

    with ``alpha = 0.7/k`` and ``beta = 0.4/k``. The derivative-like second term
    damps the accept/reject oscillation that the pure I-controller shows, which
    in practice means noticeably fewer rejected steps on stiff and
    sharply-varying problems. This is the default.
    """

    alpha_coef = 0.7
    beta_coef = 0.4

    def _factor(self, err: float) -> float:
        alpha = self.alpha_coef / self.k
        beta = self.beta_coef / self.k
        factor = self.safety * err ** (-alpha)
        if self.err_prev is not None:
            factor *= self.err_prev ** beta
        return factor


class PredictiveController(Controller):
    """Gustafsson's predictive controller — Hairer & Wanner II, IV.8.

    The default for the implicit methods, and the reason is economic rather than
    numerical. For an explicit method a step-size change is free. For an implicit
    one `h` is baked into the iteration matrix ``M/(gamma h) - J``, so changing it
    throws away an ``O(n^3)`` factorisation. A controller that is right about the
    step size but changes it constantly can easily lose to one that is
    approximately right and leaves it alone.

    Two things follow, and this class is both of them.

    **Predict, don't just react.** The classical factor reads the current error.
    Gustafsson's additional term reads how the error *responded to the last
    change*: with `h_acc` and `err_acc` from the previously accepted step,

        ``h/h_acc * (err_acc / err^2)^(1/k)``

    which is an estimate built from the observed trend rather than from one
    sample. The smaller of the two factors is taken, so the controller is
    ambitious only when both agree. On a problem whose stiffness varies this
    converts rejected steps — each of which costs a full refactorisation — into
    slightly smaller accepted ones.

    **Decline small increases outright.** If the proposed growth is under
    `freeze_below`, the step is kept exactly as it is. `h` then equals the `h`
    the current factorisation was built for, so the stepper reuses it instead of
    rebuilding. Nudging `h` up by 15% buys a few percent fewer steps and costs a
    cubic-time factorisation; it is not a good trade, and `radau5.f` declines it
    for the same reason.

    The bounds follow ``radau5.f``'s ``FACL``/``FACR``: the step may grow by at
    most 8x and shrink by at most 5x in one go.

    **Where it loses.** The base factor here is the I-controller's, without the
    PI term's damping, which makes it responsive -- and that responsiveness
    depends on the error estimate being trustworthy. It is, when the Jacobian is
    analytic. With a finite-difference Jacobian on a badly-scaled problem the
    estimate is noisy and the nonlinear solve is fragile, and this controller
    will push the step into Newton failures that the PI controller's damping
    would have avoided.

    Measured at rtol=1e-8, RHS evaluations against `PIController`, with the
    Jacobian differenced rather than supplied:

    ==============  ==========
    HIRES           0.83x
    Van der Pol     0.84x
    OREGO           0.87x
    **Robertson**   **2.10x**
    ==============  ==========

    Robertson is the outlier because its own finite-difference Jacobian is
    notoriously poor -- one component sits near 1e-8 while entries of `J` reach
    3e7. Supply `jac` there, which its catalogue entry does and which drops the
    figure back to 0.92x. Everything else measured improves under both routes,
    which is why this is still the default; `controller="pi"` is one argument
    away if a problem disagrees.
    """

    min_factor = 0.2
    max_factor = 8.0
    safety = 0.9
    #: Proposed growth at or below this is declined, keeping `h` bit-for-bit
    #: identical so the iteration matrix stays valid. ``radau5.f``'s ``QUOT2``.
    freeze_below = 1.2

    def reset(self) -> None:
        super().reset()
        #: Step size and error norm of the last *accepted* step.
        self.h_acc: float | None = None
        self.err_acc: float | None = None

    def _factor(self, err: float) -> float:
        return self.safety * err ** (-self.exponent)

    def update(self, err: float, accepted: bool, h: float | None = None) -> float:
        if err == 0.0:
            factor = self.max_factor
        else:
            factor = self._factor(err)
            if self.h_acc is not None and self.err_acc is not None and h:
                predicted = (
                    self.safety
                    * (h / self.h_acc)
                    * (self.err_acc / (err * err)) ** self.exponent
                )
                factor = min(factor, predicted)
            factor = float(np.clip(factor, self.min_factor, self.max_factor))

        if accepted:
            if h:
                self.h_acc = h
            # Floored as in radau5.f: an error of essentially zero would make the
            # next predicted factor enormous on the strength of one lucky step.
            self.err_acc = max(err, 1e-2)
            self.err_prev = max(err, 1e-4)
            if 1.0 <= factor <= self.freeze_below:
                factor = 1.0
        else:
            factor = min(factor, 1.0)
        return factor


#: Every entry is concrete; the annotation says `type[Controller]` because that
#: is the contract callers rely on, and `Controller` itself is abstract.
_CONTROLLERS: dict[str, type[Controller]] = {
    "pi": PIController,
    "i": IController,
    "predictive": PredictiveController,
    "gustafsson": PredictiveController,
}


def make_controller(spec, error_order: int, **kwargs) -> Controller:
    """Build a controller from a name, a class, or an existing instance."""
    if isinstance(spec, Controller):
        return spec
    if isinstance(spec, type) and issubclass(spec, Controller):
        return spec(error_order, **kwargs)
    key = str(spec).lower()
    if key not in _CONTROLLERS:
        raise KeyError(
            f"unknown controller {spec!r}; available: {', '.join(_CONTROLLERS)}"
        )
    return _CONTROLLERS[key](error_order, **kwargs)
