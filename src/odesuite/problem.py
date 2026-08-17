"""Problem definition: the data an integrator needs, and nothing about how to integrate.

The mass matrix is accepted here in Phase 1 even though only the explicit solvers
exist so far. Explicit steppers reject a non-identity mass matrix outright; the
implicit ones (Phase 2) consume it, including the singular case that turns the
system into an index-1 DAE. Accepting it from the start keeps the retrofit out of
`ODEProblem`'s callers.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import cached_property
from typing import Any

import numpy as np
from scipy import sparse

__all__ = ["ODEProblem"]


class ODEProblem:
    """An initial value problem ``M y'(t) = f(t, y, *args)``, ``y(t0) = y0``.

    Parameters
    ----------
    f
        Right-hand side, called as ``f(t, y, *args)`` and returning an array
        shaped like ``y``.
    t_span
        ``(t0, tf)``. ``tf < t0`` integrates backwards, which is supported
        everywhere in the library.
    y0
        Initial state. Cast to float64 (or complex128 if complex).
    jac
        Optional analytic Jacobian ``df/dy``, either a callable
        ``jac(t, y, *args)`` or a constant matrix. Dense or sparse.
    jac_sparsity
        Optional sparsity pattern of the Jacobian. Enables coloured
        finite-difference approximation (Phase 2) when `jac` is not given.
    mass
        Optional mass matrix ``M``. May be singular, which makes the problem a
        DAE. ``None`` means the identity.
    args
        Extra positional arguments threaded through to `f`, `jac` and events.
    """

    def __init__(
        self,
        f: Callable[..., Any],
        t_span: Sequence[float],
        y0: Any,
        jac: Any = None,
        jac_sparsity: Any = None,
        mass: Any = None,
        args: tuple = (),
    ) -> None:
        if not callable(f):
            raise TypeError("f must be callable")
        if not isinstance(args, tuple):
            args = (args,)

        t0, tf = (float(v) for v in t_span)
        if not np.isfinite(t0) or not np.isfinite(tf):
            raise ValueError(f"t_span must be finite, got ({t0}, {tf})")
        if t0 == tf:
            raise ValueError("t_span endpoints must differ")

        y0 = np.atleast_1d(np.asarray(y0))
        if y0.ndim != 1:
            raise ValueError(f"y0 must be 1-D, got shape {y0.shape}")
        y0 = y0.astype(np.complex128 if np.iscomplexobj(y0) else np.float64)
        if not np.all(np.isfinite(y0)):
            raise ValueError("y0 contains non-finite values")

        self.f_user = f
        self.t0 = t0
        self.tf = tf
        self.y0 = y0
        self.args = args
        self.n = y0.size
        self.direction = 1.0 if tf > t0 else -1.0

        self.mass = self._validate_mass(mass)
        self.jac_sparsity = jac_sparsity
        self._jac_user = jac

        # Validate f once, up front: a shape mismatch here is far cheaper to
        # diagnose than the same mismatch surfacing 400 steps into a solve.
        f0 = np.asarray(self.f(t0, y0), dtype=y0.dtype)
        if f0.shape != y0.shape:
            raise ValueError(
                f"f returned shape {f0.shape}, expected {y0.shape} to match y0"
            )

        # The same argument applies to a non-finite derivative, and the failure
        # it prevents is much worse than a bad message. The automatic starting
        # step divides by the norm of f0; an infinite norm makes that step zero,
        # and the next line divides by it -- so an equation started at its own
        # singularity (``t^2 y'' + t y' - y = 0`` at t = 0, say) came out as a
        # bare ZeroDivisionError from inside a step-size heuristic, naming
        # nothing the caller had written.
        if f0.dtype.kind in "fc" and not np.all(np.isfinite(f0)):
            bad = np.flatnonzero(~np.isfinite(np.asarray(f0).ravel()))
            raise ValueError(
                f"f(t0, y0) is not finite at t0={t0:g} "
                f"(component{'s' if bad.size > 1 else ''} "
                f"{', '.join(str(int(i)) for i in bad[:6])}"
                f"{'…' if bad.size > 6 else ''}). The problem may be singular "
                f"there — try starting from a different t0."
            )

    # -- right-hand side -------------------------------------------------

    def f(self, t: float, y: np.ndarray) -> np.ndarray:
        """Evaluate the RHS. Always returns a 1-D array of the state dtype.

        This is the hottest function in the library -- a stiff solve calls it
        tens of thousands of times -- so the common case, a user function that
        already returns a 1-D array, skips the normalising round trip.
        `np.asarray(...).reshape(-1)` costs about 0.5 us against a 1.2 us
        right-hand side, i.e. 40% overhead on a cheap problem, and all of it
        is spent confirming that nothing needs doing.
        """
        out = self.f_user(t, y, *self.args)
        if type(out) is np.ndarray and out.ndim == 1:
            return out
        return np.asarray(out).reshape(-1)

    @property
    def has_jac(self) -> bool:
        return self._jac_user is not None

    def jac(self, t: float, y: np.ndarray):
        """Evaluate the analytic Jacobian. Raises if none was supplied."""
        if self._jac_user is None:
            raise RuntimeError("no analytic Jacobian was supplied")
        if callable(self._jac_user):
            J = self._jac_user(t, y, *self.args)
        else:
            J = self._jac_user
        if sparse.issparse(J):
            return J
        J = np.asarray(J)
        if J.shape != (self.n, self.n):
            raise ValueError(
                f"jac returned shape {J.shape}, expected {(self.n, self.n)}"
            )
        return J

    # -- mass matrix -----------------------------------------------------

    def _validate_mass(self, mass):
        if mass is None:
            return None
        if sparse.issparse(mass):
            M = mass.tocsc()
        else:
            M = np.asarray(mass, dtype=float)
        if M.shape != (self.n, self.n):
            raise ValueError(
                f"mass must have shape {(self.n, self.n)}, got {M.shape}"
            )
        return M

    @property
    def has_mass(self) -> bool:
        return self.mass is not None

    @cached_property
    def is_dae(self) -> bool:
        """True when the mass matrix is singular, i.e. the system is a DAE."""
        if self.mass is None:
            return False
        M = self.mass.toarray() if sparse.issparse(self.mass) else self.mass
        return bool(np.linalg.matrix_rank(M) < self.n)

    def __repr__(self) -> str:
        bits = [f"n={self.n}", f"t_span=({self.t0:g}, {self.tf:g})"]
        if self.has_jac:
            bits.append("jac=analytic")
        if self.has_mass:
            bits.append("DAE" if self.is_dae else "mass")
        return f"ODEProblem({', '.join(bits)})"
