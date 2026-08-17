"""Continuous extensions (dense output).

An `Interpolant` represents the solution on a single accepted step. It owns
copies of everything it needs, so the driver is free to overwrite its work
arrays afterwards. `DenseOutput` glues the per-step interpolants into one
callable covering the whole integration interval.

Two flavours exist in Phase 1:

* `RKPolynomialInterpolant` -- a method's native continuous extension, built
  from the stage values via the tableau's `P` matrix. Currently only DOPRI5
  publishes one (order 4, free).
* `HermiteInterpolant` -- cubic Hermite through the endpoint states and
  derivatives. Order 3, available for every method at no extra cost because the
  driver already carries `f` at both ends of each step.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np

__all__ = [
    "Interpolant",
    "HermiteInterpolant",
    "RKPolynomialInterpolant",
    "ConstantInterpolant",
    "DenseOutput",
]


class Interpolant(ABC):
    """Solution on one step, evaluable anywhere in ``[min(t0,t1), max(t0,t1)]``."""

    __slots__ = ("t0", "t1", "h")

    def __init__(self, t0: float, t1: float) -> None:
        self.t0 = float(t0)
        self.t1 = float(t1)
        self.h = self.t1 - self.t0

    @abstractmethod
    def _eval(self, theta: np.ndarray) -> np.ndarray:
        """Evaluate at normalised positions ``theta = (t - t0) / h``.

        Returns shape ``(n, k)`` for ``k`` query points.
        """

    def __call__(self, t):
        """Evaluate at scalar or array `t`; returns ``(n,)`` or ``(n, k)``."""
        t = np.asarray(t, dtype=float)
        scalar = t.ndim == 0
        theta = (np.atleast_1d(t) - self.t0) / self.h
        y = self._eval(theta)
        return y[:, 0] if scalar else y

    def __repr__(self) -> str:
        return f"{type(self).__name__}([{self.t0:g}, {self.t1:g}])"


class ConstantInterpolant(Interpolant):
    """Degenerate interpolant for a zero-length interval."""

    __slots__ = ("y",)

    def __init__(self, t0: float, y: np.ndarray) -> None:
        super().__init__(t0, t0)
        self.h = 1.0  # avoid a divide-by-zero in __call__
        self.y = np.array(y, copy=True)

    def _eval(self, theta: np.ndarray) -> np.ndarray:
        return np.repeat(self.y[:, None], theta.size, axis=1)


class HermiteInterpolant(Interpolant):
    """Cubic Hermite through ``(t0, y0, f0)`` and ``(t1, y1, f1)``.

    Third-order accurate, which is enough for event location and for `t_eval`
    sampling at the tolerances these methods run at, but below the order of the
    5th-order pairs. Methods that publish a native interpolant use that instead.
    """

    __slots__ = ("y0", "y1", "f0", "f1")

    def __init__(self, t0, y0, f0, t1, y1, f1) -> None:
        super().__init__(t0, t1)
        self.y0 = np.array(y0, copy=True)
        self.y1 = np.array(y1, copy=True)
        self.f0 = np.array(f0, copy=True)
        self.f1 = np.array(f1, copy=True)

    def _eval(self, theta: np.ndarray) -> np.ndarray:
        t = theta[None, :]
        t2 = t * t
        t3 = t2 * t
        h00 = 2 * t3 - 3 * t2 + 1
        h10 = t3 - 2 * t2 + t
        h01 = -2 * t3 + 3 * t2
        h11 = t3 - t2
        return (
            h00 * self.y0[:, None]
            + h10 * (self.h * self.f0[:, None])
            + h01 * self.y1[:, None]
            + h11 * (self.h * self.f1[:, None])
        )


class RKPolynomialInterpolant(Interpolant):
    """A Runge-Kutta method's native continuous extension.

    Evaluates ``y(t0 + theta*h) = y0 + h * Q @ [theta, theta^2, ..., theta^k]``
    where ``Q = K^T P`` combines the stage derivatives `K` with the tableau's
    dense-output matrix `P`.
    """

    __slots__ = ("y0", "Q", "order")

    def __init__(self, t0, t1, y0, K, P, order: int) -> None:
        super().__init__(t0, t1)
        self.y0 = np.array(y0, copy=True)
        self.Q = K.T @ P
        self.order = order

    def _eval(self, theta: np.ndarray) -> np.ndarray:
        k = self.Q.shape[1]
        # Vandermonde in theta: rows are theta^1 .. theta^k
        powers = np.cumprod(np.broadcast_to(theta, (k, theta.size)), axis=0)
        return self.y0[:, None] + self.h * (self.Q @ powers)


class LinearInterpolant(Interpolant):
    """Straight line between the step endpoints.

    The fallback for a differential-algebraic system whose stepper has no
    continuous extension of its own. Only first order, but unlike a Hermite
    interpolant it needs no derivative -- and for the algebraic components of a
    DAE no derivative exists, so a cubic Hermite built from ``f`` there is not
    merely less accurate but wrong.
    """

    __slots__ = ("y0", "y1")

    def __init__(self, t0, y0, t1, y1) -> None:
        super().__init__(t0, t1)
        self.y0 = np.array(y0, copy=True)
        self.y1 = np.array(y1, copy=True)

    def _eval(self, theta: np.ndarray) -> np.ndarray:
        t = theta[None, :]
        return self.y0[:, None] * (1.0 - t) + self.y1[:, None] * t


class CollocationInterpolant(Interpolant):
    """Lagrange polynomial through the collocation nodes of an implicit RK step.

    An implicit Runge-Kutta method has already computed the solution at its
    stage abscissae, so the polynomial through ``(0, y0)`` and ``(c_i, Y_i)`` is
    available for nothing. For Radau IIA with three stages that is a cubic, and
    it is the method's natural continuous extension -- the same polynomial the
    collocation conditions were imposed on, rather than an interpolant bolted on
    afterwards.
    """

    __slots__ = ("nodes", "values", "_denominators")

    def __init__(self, t0: float, t1: float, nodes: np.ndarray, values: np.ndarray) -> None:
        super().__init__(t0, t1)
        self.nodes = np.asarray(nodes, dtype=float)
        self.values = np.array(values, copy=True)  # (k, n)
        diffs = self.nodes[:, None] - self.nodes[None, :]
        np.fill_diagonal(diffs, 1.0)
        self._denominators = np.prod(diffs, axis=1)

    def _eval(self, theta: np.ndarray) -> np.ndarray:
        # Lagrange basis: L_j(theta) = prod_{m != j} (theta - x_m) / (x_j - x_m)
        diff = theta[None, :] - self.nodes[:, None]          # (k, npts)
        basis = np.empty_like(diff)
        for j in range(self.nodes.size):
            others = np.delete(diff, j, axis=0)
            basis[j] = np.prod(others, axis=0) / self._denominators[j]
        return self.values.T @ basis


class DenseOutput:
    """The full continuous solution, assembled from consecutive step interpolants.

    Segments must be contiguous and monotone in `t`; the driver guarantees this.
    Lookup is a binary search, so evaluation cost is logarithmic in the number of
    steps and the whole thing is vectorised over query points.
    """

    __slots__ = ("interpolants", "ts", "t_min", "t_max", "direction", "n")

    def __init__(
        self,
        interpolants: list[Interpolant],
        n: int,
        t_last: float | None = None,
    ) -> None:
        if not interpolants:
            raise ValueError("DenseOutput needs at least one interpolant")
        self.interpolants = interpolants
        self.n = int(n)
        self.direction = 1.0 if interpolants[-1].t1 >= interpolants[0].t0 else -1.0
        # Breakpoints, always stored increasing so searchsorted works directly.
        edges = [ip.t0 for ip in interpolants] + [interpolants[-1].t1]
        self.ts = np.asarray(edges if self.direction > 0 else edges[::-1])
        self.t_min = float(self.ts[0])
        self.t_max = float(self.ts[-1])
        # A terminal event can stop the solve partway through the final step.
        # The interpolant still spans the whole step, but querying past the
        # event would return the continuation of a trajectory that was cut
        # short, so the valid range is clipped to where the solve actually ended.
        if t_last is not None:
            if self.direction > 0:
                self.t_max = min(self.t_max, float(t_last))
            else:
                self.t_min = max(self.t_min, float(t_last))

    def __call__(self, t):
        """Evaluate the solution at scalar or array `t`."""
        t = np.asarray(t, dtype=float)
        scalar = t.ndim == 0
        tq = np.atleast_1d(t)

        tol = 1e-10 * max(1.0, abs(self.t_max - self.t_min))
        if np.any(tq < self.t_min - tol) or np.any(tq > self.t_max + tol):
            raise ValueError(
                f"requested t outside the solved interval "
                f"[{self.t_min:g}, {self.t_max:g}]"
            )

        n_seg = len(self.interpolants)
        idx = np.searchsorted(self.ts, tq, side="right") - 1
        np.clip(idx, 0, n_seg - 1, out=idx)
        if self.direction < 0:
            # `ts` was reversed relative to integration order.
            idx = n_seg - 1 - idx

        out = None
        for seg in np.unique(idx):
            mask = idx == seg
            ip = self.interpolants[seg]
            values = ip._eval((tq[mask] - ip.t0) / ip.h)
            if out is None:
                # Allocated from the first segment's dtype so complex-valued
                # states survive the round trip.
                out = np.empty((self.n, tq.size), dtype=values.dtype)
            out[:, mask] = values
        return out[:, 0] if scalar else out

    def __len__(self) -> int:
        return len(self.interpolants)

    def __repr__(self) -> str:
        return f"DenseOutput({len(self)} segments, [{self.t_min:g}, {self.t_max:g}])"
