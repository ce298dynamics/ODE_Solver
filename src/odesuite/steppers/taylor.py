"""Arbitrary-order Taylor series method, powered by jet arithmetic.

Most integrators are stuck at a fixed order chosen when the coefficients were
derived. The Taylor method has no such ceiling: it computes the Taylor
coefficients of the solution directly, to whatever order is asked for. Order 20
is routine and costs no derivation at all.

**Jet arithmetic.** A `Jet` is a truncated power series
``a_0 + a_1 s + ... + a_N s^N`` carrying its coefficient array, with every
arithmetic operation and elementary function overloaded to propagate
coefficients by the classical recurrences -- ``exp``, ``log``, ``sin``, ``cos``,
``**`` and the rest each satisfy a convolution identity that gives coefficient
`k` from coefficients below it. This is forward-mode automatic differentiation
carried to all orders simultaneously, not a finite difference: the coefficients
are exact to machine precision.

**The recurrence that makes it an ODE solver.** Write the solution as
``y(t0 + s) = sum_k y_k s^k``. Then ``y'`` has coefficients ``(k+1) y_{k+1}``,
while evaluating ``f(t, y)`` in jet arithmetic gives the coefficients ``F_k`` of
the right-hand side. Matching them,

    y_{k+1} = F_k / (k + 1)

and -- this is the crucial part -- ``F_k`` depends only on ``y_0 ... y_k``. So
the coefficients can be generated one at a time, each from those already known,
with a single sweep of jet evaluations. No derivatives are ever taken by hand.

**Cost of admission.** The right-hand side must be written in operations `Jet`
understands. Most numerical code already is; anything with `abs`, comparisons or
branching on the state is not.
"""

from __future__ import annotations

import numpy as np

from ..dense import Interpolant
from .base import StepResult, Stepper

__all__ = ["Jet", "TaylorMethod"]


class Jet:
    """A truncated Taylor series with `order + 1` coefficients.

    Supports ``+ - * / **`` against jets and scalars, and the numpy ufuncs
    ``exp``, ``log``, ``sqrt``, ``sin``, ``cos``, ``tanh`` and ``negative``, so
    a right-hand side written in ordinary numpy style usually needs no changes.
    """

    __slots__ = ("c",)
    # Take precedence over ndarray.__mul__ etc., so `array * jet` dispatches here.
    __array_priority__ = 1000.0

    def __init__(self, coefficients) -> None:
        self.c = np.asarray(coefficients, dtype=float)

    # -- construction ----------------------------------------------------

    @classmethod
    def constant(cls, value: float, order: int) -> "Jet":
        c = np.zeros(order + 1)
        c[0] = value
        return cls(c)

    @classmethod
    def variable(cls, value: float, order: int) -> "Jet":
        """The independent variable: ``value + s``, i.e. derivative one."""
        c = np.zeros(order + 1)
        c[0] = value
        if order >= 1:
            c[1] = 1.0
        return cls(c)

    @property
    def order(self) -> int:
        return self.c.size - 1

    def _lift(self, other) -> "Jet":
        return other if isinstance(other, Jet) else Jet.constant(float(other), self.order)

    def __call__(self, s: float) -> float:
        """Evaluate the series at offset `s` by Horner's rule."""
        result = 0.0
        for coefficient in self.c[::-1]:
            result = result * s + coefficient
        return result

    # -- arithmetic ------------------------------------------------------

    def __add__(self, other):
        return Jet(self.c + self._lift(other).c)

    __radd__ = __add__

    def __sub__(self, other):
        return Jet(self.c - self._lift(other).c)

    def __rsub__(self, other):
        return Jet(self._lift(other).c - self.c)

    def __neg__(self):
        return Jet(-self.c)

    def __pos__(self):
        return Jet(self.c.copy())

    def __mul__(self, other):
        if not isinstance(other, Jet):
            return Jet(self.c * float(other))
        # Cauchy product, truncated: c_k = sum_j a_j b_{k-j}
        a, b = self.c, other.c
        out = np.zeros_like(a)
        for k in range(a.size):
            out[k] = a[: k + 1] @ b[k::-1][: k + 1]
        return Jet(out)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if not isinstance(other, Jet):
            return Jet(self.c / float(other))
        a, b = self.c, other.c
        if b[0] == 0.0:
            raise ZeroDivisionError("jet division by a series with zero constant term")
        out = np.zeros_like(a)
        for k in range(a.size):
            # c_k = (a_k - sum_{j<k} c_j b_{k-j}) / b_0
            acc = out[:k] @ b[k:0:-1][:k] if k else 0.0
            out[k] = (a[k] - acc) / b[0]
        return Jet(out)

    def __rtruediv__(self, other):
        return self._lift(other) / self

    def __pow__(self, exponent):
        if isinstance(exponent, Jet):
            return (exponent * self.log()).exp()
        exponent = float(exponent)
        if exponent == 0.0:
            return Jet.constant(1.0, self.order)
        if exponent == int(exponent) and 0 < exponent < 8:
            result = self
            for _ in range(int(exponent) - 1):
                result = result * self
            return result
        a = self.c
        if a[0] <= 0.0:
            raise ValueError(
                "jet power with a non-integer exponent needs a positive constant term"
            )
        out = np.zeros_like(a)
        out[0] = a[0] ** exponent
        for k in range(1, a.size):
            # k a_0 c_k = sum_{j=0}^{k-1} (exponent (k-j) - j) a_{k-j} c_j
            j = np.arange(k)
            out[k] = ((exponent * (k - j) - j) * a[k - j] * out[j]).sum() / (k * a[0])
        return Jet(out)

    # -- elementary functions --------------------------------------------

    def exp(self) -> "Jet":
        a = self.c
        out = np.zeros_like(a)
        out[0] = np.exp(a[0])
        for k in range(1, a.size):
            j = np.arange(1, k + 1)
            out[k] = (j * a[j] * out[k - j]).sum() / k
        return Jet(out)

    def log(self) -> "Jet":
        a = self.c
        if a[0] <= 0.0:
            raise ValueError("jet log needs a positive constant term")
        out = np.zeros_like(a)
        out[0] = np.log(a[0])
        for k in range(1, a.size):
            j = np.arange(1, k)
            acc = (j * out[j] * a[k - j]).sum() / k if k > 1 else 0.0
            out[k] = (a[k] - acc) / a[0]
        return Jet(out)

    def sqrt(self) -> "Jet":
        return self ** 0.5

    def _sin_cos(self):
        a = self.c
        s = np.zeros_like(a)
        c = np.zeros_like(a)
        s[0], c[0] = np.sin(a[0]), np.cos(a[0])
        for k in range(1, a.size):
            j = np.arange(1, k + 1)
            weighted = j * a[j]
            s[k] = (weighted * c[k - j]).sum() / k
            c[k] = -(weighted * s[k - j]).sum() / k
        return Jet(s), Jet(c)

    def sin(self) -> "Jet":
        return self._sin_cos()[0]

    def cos(self) -> "Jet":
        return self._sin_cos()[1]

    def tanh(self) -> "Jet":
        e = (2.0 * self).exp()
        return (e - 1.0) / (e + 1.0)

    # -- numpy interoperability ------------------------------------------

    _UFUNCS = {
        "add": lambda a, b: a + b,
        "subtract": lambda a, b: a - b,
        "multiply": lambda a, b: a * b,
        "true_divide": lambda a, b: a / b,
        "power": lambda a, b: a ** b,
        "negative": lambda a: -a,
        "positive": lambda a: +a,
        "exp": lambda a: a.exp(),
        "log": lambda a: a.log(),
        "sqrt": lambda a: a.sqrt(),
        "sin": lambda a: a.sin(),
        "cos": lambda a: a.cos(),
        "tanh": lambda a: a.tanh(),
    }

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        """Let `np.exp(jet)`, `np.sin(jet)` and friends work unchanged.

        Without this a right-hand side written with numpy calls would have to be
        rewritten to use jet-specific functions; with it, most existing code
        runs under jet arithmetic as-is.
        """
        if method != "__call__" or kwargs:
            return NotImplemented
        handler = self._UFUNCS.get(ufunc.__name__)
        if handler is None:
            return NotImplemented
        try:
            return handler(*inputs)
        except (TypeError, AttributeError):
            return NotImplemented

    def __repr__(self) -> str:
        head = ", ".join(f"{v:.4g}" for v in self.c[: min(4, self.c.size)])
        tail = ", ..." if self.c.size > 4 else ""
        return f"Jet(order={self.order}, [{head}{tail}])"


class TaylorMethod(Stepper):
    """Taylor series method of arbitrary order, by jet arithmetic.

    At high order the local error falls off so steeply that the method reaches
    machine precision in a handful of steps on a smooth problem -- on Kepler it
    holds ~1e-14 where a fifth-order Runge-Kutta pair needs thousands of steps.

    Parameters
    ----------
    order
        Number of Taylor terms used to propagate. Twenty is a good default; the
        cost per step grows roughly quadratically while the accuracy gain is
        exponential, so high orders pay for themselves on smooth problems.
    """

    implicit = False
    supports_mass = False
    # The coefficient recurrence starts from the state alone, and the continuous
    # extension is the Taylor polynomial itself, so `f` is never consulted.
    uses_f = False

    def __init__(self, order: int = 20):
        if order < 2:
            raise ValueError("Taylor order must be at least 2")
        self.order = order
        # The last retained term estimates the truncated tail, so the estimate
        # behaves like h^order and the controller's exponent is 1/order.
        self.error_order = order - 1
        self.interpolant_order = order
        self.name = f"Taylor{order}"
        self._coefficients: np.ndarray | None = None
        self._t0 = 0.0

    def validate(self, problem) -> None:
        super().validate(problem)
        if np.iscomplexobj(problem.y0):
            # `Jet` carries real coefficients, so a complex state would be
            # silently truncated on assignment. Refuse rather than return a
            # confident wrong answer.
            raise ValueError(
                f"{self.name} does not support complex states; jet arithmetic "
                f"is real-valued. Use an explicit method or ETDRK4."
            )

    def coefficients(self, problem, t: float, y: np.ndarray) -> np.ndarray:
        """Taylor coefficients of the solution at `t`, shape ``(n, order+1)``.

        Built one order at a time: coefficient ``k+1`` follows from the right-
        hand side's coefficient `k`, which depends only on solution
        coefficients up to `k`.
        """
        n = y.size
        N = self.order
        coefficients = np.zeros((n, N + 1))
        coefficients[:, 0] = y

        for k in range(N):
            t_jet = Jet.variable(t, N)
            # An *object* array rather than a list, so that vectorised
            # right-hand sides -- `-k * y`, `r * y * (1 - y)` -- work unchanged
            # by dispatching elementwise onto Jet's operators.
            y_jets = np.empty(n, dtype=object)
            for i in range(n):
                y_jets[i] = Jet(coefficients[i])

            derivative = problem.f_user(t_jet, y_jets, *problem.args)
            for i in range(n):
                term = derivative[i]
                fk = term.c[k] if isinstance(term, Jet) else (float(term) if k == 0 else 0.0)
                coefficients[i, k + 1] = fk / (k + 1)
        return coefficients

    def step(self, problem, t, y, f, h) -> StepResult:
        coefficients = self.coefficients(problem, t, y)
        self._coefficients = coefficients
        self._t0 = t

        powers = h ** np.arange(self.order + 1)
        y_new = coefficients @ powers
        # The last retained term is the standard proxy for the truncated tail.
        error = coefficients[:, -1] * powers[-1]

        return StepResult(
            y_new=y_new,
            f_new=None,
            error=error,
            # Each of the `order` sweeps evaluates the right-hand side once.
            nfev=self.order,
        )

    def interpolant(self, t, y, f, t_new, y_new, f_new) -> Interpolant:
        """The Taylor polynomial itself -- dense output of the method's own order.

        Unusually for a continuous extension this costs nothing and matches the
        order of the step, because the polynomial *is* what was integrated.
        """
        return _TaylorInterpolant(t, t_new, self._coefficients)


class _TaylorInterpolant(Interpolant):
    """Evaluates the step's Taylor polynomial at any point inside it."""

    __slots__ = ("coefficients",)

    def __init__(self, t0: float, t1: float, coefficients: np.ndarray) -> None:
        super().__init__(t0, t1)
        self.coefficients = np.array(coefficients, copy=True)

    def _eval(self, theta: np.ndarray) -> np.ndarray:
        s = theta * self.h                      # offset from t0 in real time
        order = self.coefficients.shape[1] - 1
        powers = s[None, :] ** np.arange(order + 1)[:, None]
        return self.coefficients @ powers
