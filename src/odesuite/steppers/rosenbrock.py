"""Rosenbrock (linearly implicit Runge-Kutta) methods.

The cheapest correct way to solve a stiff system. A Rosenbrock method replaces
the nonlinear stage equations of an implicit Runge-Kutta method with *linear*
ones by folding the Jacobian directly into the formula, so there is no Newton
iteration at all: one Jacobian, one factorisation and one triangular solve per
stage. Nothing can fail to converge, which makes the step controller the only
thing deciding step size.

The price is that the coefficients are only valid for the exact Jacobian, so
accuracy degrades if `J` is stale -- unlike a Newton-based method, where a stale
Jacobian costs iterations but not accuracy. This implementation therefore
recomputes `J` every step.

Each stage solves

    (M/(gamma*h) - J) k_i = f(t + alpha_i*h, y + sum_j a_ij k_j)
                            + M * (sum_j c_ij k_j) / h
                            + h * d_i * df/dt

and the step is ``y_new = y + sum_i b_i k_i``.

Both tableaux below satisfy ``sum_i b_i d_i == 1``, which is the consistency
condition this formulation imposes: on ``f == 1`` the stages collapse to
``k_i = d_i h``, so that sum *is* the method applied to ``y' = 1``. It is checked
in `tests/test_rosenbrock.py` and is the analogue of the Butcher row-sum test.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..dense import HermiteInterpolant, Interpolant, LinearInterpolant
from ..linalg import EPS, apply_mass, lu_factorize, mass_minus_jacobian
from .base import StepResult, Stepper

__all__ = ["RosenbrockTableau", "Rosenbrock", "RODAS4", "ROSENBROCK_TABLEAUX"]


@dataclass(frozen=True)
class RosenbrockTableau:
    """Coefficients of a Rosenbrock method in the ``(A, C, gamma, d)`` form."""

    name: str
    A: np.ndarray       # (s, s) strictly lower: stage state combinations
    C: np.ndarray       # (s, s) strictly lower: stage derivative combinations
    b: np.ndarray       # (s,)   propagated weights
    b_hat: np.ndarray   # (s,)   embedded weights
    gamma: float        # the repeated diagonal coefficient
    d: np.ndarray       # (s,)   weights on h * df/dt
    alpha: np.ndarray   # (s,)   stage times, supplied explicitly
    order: int
    error_order: int
    description: str = ""

    @property
    def n_stages(self) -> int:
        return self.b.size

    @property
    def e(self) -> np.ndarray:
        return self.b - self.b_hat

    @property
    def stiffly_accurate(self) -> bool:
        """True when the propagated solution *is* the last stage.

        Requires ``b_j == a_sj`` for ``j < s`` together with ``b_s == 1``, not
        merely ``alpha_s == 1``. The weaker test is tempting and wrong: ROS3P
        evaluates its final stage at ``t + h`` yet weights the stages
        differently from the last row of A, so it is not stiffly accurate and
        cannot be trusted on a DAE.

        Stiff accuracy is what makes an index-1 DAE solvable: the algebraic
        constraint is imposed exactly at the end of the step, so the solution
        stays on the constraint manifold instead of drifting off it.
        """
        return bool(
            np.allclose(self.b[:-1], self.A[-1, :-1]) and np.isclose(self.b[-1], 1.0)
        )


def _build(name, gamma, a_rows, c_rows, b, b_hat, d, alpha, order, error_order, description=""):
    s = len(b)
    A = np.zeros((s, s))
    C = np.zeros((s, s))
    for i, row in enumerate(a_rows):
        A[i, : len(row)] = row
    for i, row in enumerate(c_rows):
        C[i, : len(row)] = row
    return RosenbrockTableau(
        name=name,
        A=A,
        C=C,
        b=np.asarray(b, dtype=float),
        b_hat=np.asarray(b_hat, dtype=float),
        gamma=float(gamma),
        d=np.asarray(d, dtype=float),
        alpha=np.asarray(alpha, dtype=float),
        order=order,
        error_order=error_order,
        description=description,
    )


# ---------------------------------------------------------------------------
# A note on ROS3P
#
# Lang & Verwer's ROS3P was intended for this slot and was implemented, but its
# embedded pair as transcribed produced an error estimate that vanished
# identically -- b - b_hat annihilated the stage vector to machine precision on
# every test problem, not just degenerate ones. An adaptive solver with an
# always-zero error estimate accepts every step it is offered, which is far
# worse than having one fewer method: it is silently wrong rather than slow.
#
# Rather than ship an unverifiable estimator, ROS3P was removed. RODAS4 below is
# higher order, L-stable, stiffly accurate and DAE-capable, and its estimator is
# verified by `tests/test_rosenbrock.py::test_error_estimate_is_nondegenerate`,
# which exists precisely because of this.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# RODAS4 -- Hairer & Wanner II, IV.7 (the coefficients of rodas.f)
#
# Fourth order, six stages, L-stable and stiffly accurate. The stiff accuracy is
# what makes it the DAE workhorse here. Because the last two d coefficients
# vanish and b differs from b_hat only in the final component, the embedded
# error estimate is exactly the last stage, k6 -- so the estimate is free.
# ---------------------------------------------------------------------------

_RODAS4_A6 = [
    1.221224509226641e00,
    6.019134481288629e00,
    1.253708332932087e01,
    -6.878860361058950e-01,
    1.0,
]

RODAS4 = _build(
    "RODAS4",
    gamma=0.25,
    a_rows=[
        [],
        [1.544000000000000e00],
        [9.466785280815826e-01, 2.557011698983284e-01],
        [3.314825187068521e00, 2.896124015972201e00, 9.986419139977817e-01],
        [
            1.221224509226641e00,
            6.019134481288629e00,
            1.253708332932087e01,
            -6.878860361058950e-01,
        ],
        _RODAS4_A6,
    ],
    c_rows=[
        [],
        [-5.668800000000000e00],
        [-2.430093356833875e00, -2.063599157091915e-01],
        [-1.073529058151375e-01, -9.594562251023355e00, -2.047028614809616e01],
        [
            7.496443313967647e00,
            -1.024680431464352e01,
            -3.399990352819905e01,
            1.170890893206160e01,
        ],
        [
            8.083246795921522e00,
            -7.981132988064893e00,
            -3.152159432874371e01,
            1.631930543123136e01,
            -6.058818238834054e00,
        ],
    ],
    b=[*_RODAS4_A6, 1.0],
    b_hat=[*_RODAS4_A6, 0.0],
    d=[
        2.500000000000000e-01,
        -1.043000000000000e-01,
        1.035000000000000e-01,
        -3.620000000000023e-02,
        0.0,
        0.0,
    ],
    alpha=[0.0, 0.386, 0.21, 0.63, 1.0, 1.0],
    order=4,
    error_order=3,
    description="Hairer & Wanner RODAS4, 6 stages, L-stable, stiffly accurate, "
    "order 4(3); handles index-1 DAEs.",
)


ROSENBROCK_TABLEAUX = {"rodas4": RODAS4}


# ---------------------------------------------------------------------------


class Rosenbrock(Stepper):
    """Generic Rosenbrock stepper, driven by a `RosenbrockTableau`."""

    implicit = True
    supports_mass = True

    def __init__(self, tableau: RosenbrockTableau | str = RODAS4, jac_method: str = "auto"):
        if isinstance(tableau, str):
            tableau = ROSENBROCK_TABLEAUX[tableau.lower()]
        self.tab = tableau
        self.name = tableau.name
        self.order = tableau.order
        self.error_order = tableau.error_order
        self.interpolant_order = 3
        self.jac_method = jac_method
        self._jac = None
        self._mass = None
        self._mass_lu = None
        self.rtol = 1e-6
        self.atol = np.asarray(1e-9)

    def validate(self, problem) -> None:
        super().validate(problem)
        if problem.is_dae and not self.tab.stiffly_accurate:
            raise ValueError(
                f"{self.name} is not stiffly accurate and cannot solve a DAE; "
                f"use rodas4 or radau"
            )
        self._mass = problem.mass
        self._mass_lu = None
        if problem.mass is not None and not problem.is_dae:
            # Non-singular mass matrix: keep a factorisation so the interpolant
            # can recover the true derivative M^-1 f at the step endpoints.
            self._mass_lu = lu_factorize(
                problem.mass.toarray()
                if hasattr(problem.mass, "toarray")
                else np.array(problem.mass, dtype=float)
            )

    def set_tolerances(self, rtol, atol) -> None:
        self.rtol = rtol
        self.atol = np.asarray(atol)
        self._jac = None  # rebuild with a perturbation floor matched to these

    def _jacobian_evaluator(self, problem):
        # Built lazily so the stepper can be constructed before it sees a problem.
        if self._jac is None or self._jac.problem is not problem:
            from ..linalg import JacobianEvaluator, threshold_from_tolerances

            self._jac = JacobianEvaluator(
                problem,
                self.jac_method,
                threshold=threshold_from_tolerances(self.rtol, self.atol),
            )
        return self._jac

    def _time_derivative(self, problem, t, y, f0, h):
        """Finite-difference ``df/dt`` at fixed y. One extra RHS evaluation.

        Only Rosenbrock methods need this term; it is what keeps them full order
        on non-autonomous problems instead of dropping to order two.
        """
        dt = np.sqrt(EPS) * max(abs(t), 1.0) * np.sign(h)
        return (problem.f(t + dt, y) - f0) / dt

    def step(self, problem, t, y, f, h) -> StepResult:
        tab = self.tab
        s = tab.n_stages
        jac_eval = self._jacobian_evaluator(problem)

        nfev_before = jac_eval.nfev
        J = jac_eval(t, y, f)
        nfev = jac_eval.nfev - nfev_before

        f_t = self._time_derivative(problem, t, y, f, h)
        nfev += 1

        try:
            lu = lu_factorize(
                mass_minus_jacobian(problem.mass, J, 1.0 / (tab.gamma * h))
            )
        except (np.linalg.LinAlgError, RuntimeError):
            # Singular iteration matrix: the step is too large for this
            # Jacobian. Report failure and let the driver shrink h.
            return StepResult(y, None, None, nfev=nfev, njev=1, nlu=1, ok=False)

        k = np.zeros((s, y.size), dtype=y.dtype)
        for i in range(s):
            if i == 0:
                stage_f = f
            else:
                stage_f = problem.f(t + tab.alpha[i] * h, y + tab.A[i, :i] @ k[:i])
                nfev += 1

            rhs = stage_f + h * tab.d[i] * f_t
            if i > 0:
                rhs = rhs + apply_mass(problem.mass, (tab.C[i, :i] @ k[:i]) / h)
            k[i] = lu.solve(rhs)

        y_new = y + tab.b @ k
        self._last = (t, y, h, y_new)

        return StepResult(
            y_new=y_new,
            f_new=None,
            error=tab.e @ k,
            nfev=nfev,
            njev=1,
            nlu=1,
        )

    def interpolant(self, t, y, f, t_new, y_new, f_new) -> Interpolant:
        """Continuous extension, chosen according to the mass matrix.

        A cubic Hermite needs the state *derivative* at both ends. For a plain
        ODE that is `f`; under a mass matrix it is ``M^-1 f``; and for the
        algebraic components of a DAE it does not exist at all -- there `f` is a
        constraint residual sitting near zero, and feeding it to Hermite as a
        slope produces an interpolant that is confidently wrong between nodes
        even though both endpoints are exact.
        """
        if self._mass is None:
            return HermiteInterpolant(t, y, f, t_new, y_new, f_new)
        if self._mass_lu is not None:
            return HermiteInterpolant(
                t, y, self._mass_lu.solve(f), t_new, y_new, self._mass_lu.solve(f_new)
            )
        return LinearInterpolant(t, y, t_new, y_new)
