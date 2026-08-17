"""Two-point boundary value problems by multiple shooting.

Shooting turns a BVP into a root-finding problem over initial conditions: guess
the unknown part of ``y(a)``, integrate to `b`, and drive the boundary residual
to zero with Newton.

*Single* shooting does that with one long integration and is fragile for exactly
the reason it is simple -- the map from initial state to final state inherits
the full sensitivity of the problem, so on anything mildly unstable a
perturbation of ``1e-8`` at `a` becomes enormous at `b` and Newton has no usable
Jacobian.

*Multiple* shooting cuts ``[a, b]`` into `m` short intervals and treats the state
at every node as an unknown, adding continuity conditions to close the system:

    unknowns   S_0 ... S_m                      (m+1) n
    residuals  y(t_{k+1}; t_k, S_k) - S_{k+1}     m n     continuity
               bc(S_0, S_m)                        n      boundary

No single integration is long enough for the sensitivity to blow up, and the
Jacobian gains a block-bidiagonal structure that a sparse factorisation
exploits. The cost is a larger system, which the structure pays back.

Everything here is built on the IVP solver: each shot is an ordinary `solve`
call, so multiple shooting inherits adaptivity, dense output, stiff methods and
DAE support without knowing anything about them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from scipy import sparse

from ..dense import DenseOutput
from ..driver import solve
from ..linalg import EPS, lu_factorize
from ..problem import ODEProblem
from ..solution import Stats

__all__ = ["BVProblem", "BVPSolution", "solve_bvp"]


class BVProblem:
    """A two-point boundary value problem ``y' = f(t, y)`` on ``[a, b]``.

    Parameters
    ----------
    f
        Right-hand side ``f(t, y, *args)``.
    t_span
        ``(a, b)`` with ``a < b``.
    bc
        Boundary conditions ``bc(ya, yb, *args)`` returning `n` residuals, where
        `ya` and `yb` are the states at `a` and `b`. A well-posed problem needs
        exactly as many conditions as components.
    n
        Number of state components.
    jac
        Optional ``df/dy``, passed through to the inner IVP solves. Used by the
        stiff methods; it does not affect the shooting Jacobian, which is
        differenced.
    args
        Extra arguments threaded to `f` and `bc`.
    """

    def __init__(
        self,
        f: Callable,
        t_span,
        bc: Callable,
        n: int,
        jac=None,
        args: tuple = (),
    ) -> None:
        a, b = (float(v) for v in t_span)
        if a >= b:
            raise ValueError(f"t_span must satisfy a < b, got ({a}, {b})")
        if not callable(f) or not callable(bc):
            raise TypeError("f and bc must be callable")
        self.f = f
        self.bc = bc
        self.a = a
        self.b = b
        self.n = int(n)
        self.jac = jac
        self.args = args if isinstance(args, tuple) else (args,)

    def residual(self, ya: np.ndarray, yb: np.ndarray) -> np.ndarray:
        r = np.asarray(self.bc(ya, yb, *self.args), dtype=float).reshape(-1)
        if r.size != self.n:
            raise ValueError(
                f"bc returned {r.size} residuals, expected {self.n} for an "
                f"{self.n}-component system"
            )
        return r

    def __repr__(self) -> str:
        return f"BVProblem(n={self.n}, [{self.a:g}, {self.b:g}])"


@dataclass
class BVPSolution:
    """Result of `solve_bvp`."""

    nodes: np.ndarray          # (m+1,) shooting node times
    y_nodes: np.ndarray        # (n, m+1) converged states at the nodes
    converged: bool
    n_iter: int
    residual_norm: float
    message: str = ""
    sol: DenseOutput | None = None
    stats: Stats = field(default_factory=Stats)
    #: Residual norm at each Newton iteration, for diagnosing convergence.
    history: list[float] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.converged

    def y_at(self, t):
        """Evaluate the continuous solution on ``[a, b]``."""
        if self.sol is None:
            raise RuntimeError("no continuous solution was assembled")
        return self.sol(t)

    def __call__(self, t):
        return self.y_at(t)

    def __repr__(self) -> str:
        return (
            f"BVPSolution(converged={self.converged}, iterations={self.n_iter}, "
            f"residual={self.residual_norm:.3e}, nodes={self.nodes.size})"
        )


def _initial_guess(guess, nodes: np.ndarray, n: int) -> np.ndarray:
    """Normalise the user's guess into an ``(n, m+1)`` array of node states."""
    m1 = nodes.size
    if callable(guess):
        return np.stack([np.asarray(guess(t), dtype=float).reshape(-1) for t in nodes], axis=-1)
    arr = np.asarray(guess, dtype=float)
    if arr.ndim == 1:
        if arr.size != n:
            raise ValueError(f"constant guess must have length {n}, got {arr.size}")
        return np.repeat(arr[:, None], m1, axis=1)
    if arr.shape != (n, m1):
        raise ValueError(f"guess array must have shape {(n, m1)}, got {arr.shape}")
    return arr.copy()


def solve_bvp(
    bvp: BVProblem,
    guess,
    n_nodes: int = 10,
    *,
    method: str = "dopri5",
    rtol: float = 1e-8,
    atol=1e-10,
    tol: float = 1e-8,
    max_iter: int = 40,
    fd_floor: float = 1.0,
    dense_output: bool = True,
    verbose: bool = False,
) -> BVPSolution:
    """Solve a two-point BVP by multiple shooting with damped Newton.

    Parameters
    ----------
    bvp
        The problem.
    guess
        Initial guess: a constant state ``(n,)``, a callable ``t -> y``, or an
        array ``(n, n_nodes+1)`` giving a state at every node. A callable is
        usually best -- shooting converges from a rough shape far more reliably
        than from a constant.
    n_nodes
        Number of shooting intervals. More nodes shorten each shot and widen
        the basin of convergence at the cost of a larger linear system; the
        default suits mildly nonlinear problems. ``n_nodes=1`` is single
        shooting.
    rtol, atol
        Tolerances for the inner IVP solves. These must be tighter than `tol`,
        or Newton will stall on integration noise rather than converge.
    tol
        Convergence threshold on the RMS residual norm.
    fd_floor
        Typical magnitude of a state component, used to size the
        finite-difference perturbations when a component is near zero. Raise it
        for problems whose states are large, lower it for very small ones.

    Returns
    -------
    BVPSolution
    """
    if n_nodes < 1:
        raise ValueError("n_nodes must be at least 1")

    n = bvp.n
    nodes = np.linspace(bvp.a, bvp.b, n_nodes + 1)
    S = _initial_guess(guess, nodes, n)
    stats = Stats()

    def shoot(k: int, state: np.ndarray, want_dense: bool = False):
        """Integrate interval `k` from `state`. Returns (endpoint, interpolants)."""
        problem = ODEProblem(
            f=bvp.f,
            t_span=(nodes[k], nodes[k + 1]),
            y0=state,
            jac=bvp.jac,
            args=bvp.args,
        )
        sol = solve(
            problem,
            method=method,
            rtol=rtol,
            atol=atol,
            dense_output=want_dense,
        )
        stats.nfev += sol.stats.nfev
        stats.njev += sol.stats.njev
        stats.nlu += sol.stats.nlu
        stats.nsteps += sol.stats.nsteps
        stats.naccepted += sol.stats.naccepted
        stats.nrejected += sol.stats.nrejected
        if not sol.success:
            raise FloatingPointError(f"shot {k} failed: {sol.message}")
        return sol.y[:, -1], (sol.sol if want_dense else None)

    def residual(S: np.ndarray) -> np.ndarray:
        """Continuity residuals for every interval, then the boundary residual."""
        r = np.empty((n_nodes + 1) * n)
        for k in range(n_nodes):
            end, _ = shoot(k, S[:, k])
            r[k * n : (k + 1) * n] = end - S[:, k + 1]
        r[n_nodes * n :] = bvp.residual(S[:, 0], S[:, n_nodes])
        return r

    # Differentiating a *numerically integrated* map: the effective machine
    # epsilon is the integration tolerance, not np.finfo(float).eps. A shot is
    # only accurate to ~rtol, so the optimal forward-difference step is
    # sqrt(rtol) rather than sqrt(EPS) -- about 3e-6 at rtol=1e-11 instead of
    # 1.5e-8. Getting this wrong is silent: the Jacobian fills with noise, the
    # Newton direction is meaningless, and the line search rejects every step
    # while reporting only "line search failed".
    fd_eps = np.sqrt(max(float(rtol), EPS))

    def fd_steps(values: np.ndarray) -> np.ndarray:
        # The floor must be a *typical size* of the state, not a tiny number:
        # a component sitting at zero still needs a perturbation big enough to
        # register above the integrator's noise.
        return fd_eps * np.maximum(np.abs(values), fd_floor)

    def jacobian(S: np.ndarray):
        """Block-bidiagonal Jacobian of the residual, assembled sparsely.

        Only the propagation blocks ``G_k = dy(t_{k+1})/dS_k`` and the two
        boundary blocks need differencing; the ``-I`` coupling each continuity
        residual has to the *next* node is exact and is written in directly.
        That is what keeps the cost at ``m*n`` short shots rather than
        ``(m+1)*n`` full ones.
        """
        rows, cols, vals = [], [], []

        def add_block(block, row0, col0):
            block = np.asarray(block)
            r_idx, c_idx = np.nonzero(np.ones_like(block))
            rows.append(r_idx + row0)
            cols.append(c_idx + col0)
            vals.append(block.ravel())

        for k in range(n_nodes):
            base, _ = shoot(k, S[:, k])
            G = np.empty((n, n))
            steps = fd_steps(S[:, k])
            for j in range(n):
                perturbed = S[:, k].copy()
                perturbed[j] += steps[j]
                delta = perturbed[j] - S[j, k]
                end, _ = shoot(k, perturbed)
                G[:, j] = (end - base) / delta
            add_block(G, k * n, k * n)
            add_block(-np.eye(n), k * n, (k + 1) * n)

        ya, yb = S[:, 0].copy(), S[:, n_nodes].copy()
        base_bc = bvp.residual(ya, yb)
        Ba = np.empty((n, n))
        Bb = np.empty((n, n))
        # `bc` is evaluated exactly rather than integrated, so here the ordinary
        # sqrt(EPS) step is the right one.
        a_steps = np.sqrt(EPS) * np.maximum(np.abs(ya), fd_floor)
        b_steps = np.sqrt(EPS) * np.maximum(np.abs(yb), fd_floor)
        for j in range(n):
            ya_p = ya.copy()
            ya_p[j] += a_steps[j]
            Ba[:, j] = (bvp.residual(ya_p, yb) - base_bc) / (ya_p[j] - ya[j])

            yb_p = yb.copy()
            yb_p[j] += b_steps[j]
            Bb[:, j] = (bvp.residual(ya, yb_p) - base_bc) / (yb_p[j] - yb[j])

        add_block(Ba, n_nodes * n, 0)
        add_block(Bb, n_nodes * n, n_nodes * n)

        size = (n_nodes + 1) * n
        return sparse.csc_matrix(
            (np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
            shape=(size, size),
        )

    def norm(r: np.ndarray) -> float:
        return float(np.linalg.norm(r) / np.sqrt(r.size))

    # -- damped Newton ---------------------------------------------------
    history: list[float] = []
    converged = False
    message = ""
    n_iter = 0

    try:
        r = residual(S)
    except FloatingPointError as exc:
        return BVPSolution(
            nodes, S, False, 0, np.inf, f"initial guess is not integrable: {exc}"
        )
    r_norm = norm(r)
    history.append(r_norm)

    for n_iter in range(1, max_iter + 1):
        if r_norm < tol:
            converged = True
            n_iter -= 1
            break

        try:
            factorization = lu_factorize(jacobian(S))
        except (np.linalg.LinAlgError, RuntimeError) as exc:
            message = f"shooting Jacobian is singular at iteration {n_iter}: {exc}"
            break
        except FloatingPointError as exc:
            message = f"a shot diverged while building the Jacobian: {exc}"
            break

        step = -factorization.solve(r).reshape(n_nodes + 1, n).T

        # Armijo backtracking. Undamped Newton overshoots readily on a
        # nonlinear BVP -- Bratu's upper branch is the standard example -- and
        # a diverged shot raises rather than returning a large residual, so the
        # failure has to be caught and treated as "step too long".
        lam = 1.0
        accepted = False
        while lam >= 1.0 / 64:
            trial = S + lam * step
            try:
                r_trial = residual(trial)
                trial_norm = norm(r_trial)
            except FloatingPointError:
                lam /= 2
                continue
            if trial_norm < (1.0 - 0.25 * lam) * r_norm:
                S, r, r_norm = trial, r_trial, trial_norm
                accepted = True
                break
            lam /= 2

        if not accepted:
            # No damping improved the residual. If it is already below
            # tolerance that is convergence, not failure: near the solution the
            # residual sits on the integrator's noise floor and no step can
            # reduce it further.
            if r_norm < tol:
                converged = True
            else:
                message = (
                    f"line search failed at iteration {n_iter} with residual "
                    f"{r_norm:.3e}; try more nodes, a better guess, or tighter "
                    f"rtol (the shooting Jacobian is only accurate to ~sqrt(rtol))"
                )
            break

        history.append(r_norm)
        if verbose:
            print(f"  iter {n_iter:2d}  |r| = {r_norm:.3e}  damping = {lam:g}")

        if r_norm < tol:
            converged = True
            break
    else:
        message = f"did not converge in {max_iter} iterations"

    if converged:
        message = f"converged in {n_iter} iterations, residual {r_norm:.3e}"

    # -- assemble the continuous solution --------------------------------
    dense = None
    if dense_output and converged:
        interpolants = []
        for k in range(n_nodes):
            _, piece = shoot(k, S[:, k], want_dense=True)
            interpolants.extend(piece.interpolants)
        dense = DenseOutput(interpolants, n)

    return BVPSolution(
        nodes=nodes,
        y_nodes=S,
        converged=converged,
        n_iter=n_iter,
        residual_norm=r_norm,
        message=message,
        sol=dense,
        stats=stats,
        history=history,
    )
