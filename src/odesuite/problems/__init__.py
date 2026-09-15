"""The benchmark problem zoo.

Standard test problems from the ODE literature, wrapped so that tests and
benchmarks can iterate over them uniformly. Using the recognised benchmarks --
rather than ad-hoc examples -- is what makes accuracy and efficiency claims
comparable to published results.

Each factory returns a `Benchmark`. Those with a closed-form solution expose
`exact(t)`, which is what the order-of-convergence suite measures against;
those with a conserved quantity expose `invariant(y)`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.linalg import expm

from ..problem import ODEProblem

__all__ = [
    "Benchmark",
    "exponential_decay",
    "linear_system",
    "sine_cosine",
    "logistic",
    "lotka_volterra",
    "van_der_pol",
    "brusselator",
    "fitzhugh_nagumo",
    "hopf_window",
    "sir",
    "pendulum",
    "duffing",
    "lorenz",
    "kepler",
    "pleiades",
    "robertson",
    "hires",
    "orego",
    "bouncing_ball",
    "mass_matrix_oscillator",
    "linear_dae",
    "robertson_dae",
    "kepler_second_order",
    "harmonic_oscillator_2d",
    "kuramoto_sivashinsky",
    "allen_cahn",
    "SEPARABLE",
    "SEMILINEAR",
    "BVPBenchmark",
    "bvp_linear",
    "bvp_trig",
    "bratu",
    "NONSTIFF",
    "STIFF",
    "ANALYTIC",
    "DAE",
    "BVPS",
    "all_benchmarks",
]


@dataclass
class Benchmark:
    """A named test problem, optionally with a reference solution."""

    name: str
    problem: ODEProblem
    exact: Callable[[Any], np.ndarray] | None = None
    invariant: Callable[[np.ndarray], float] | None = None
    stiff: bool = False
    description: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def has_exact(self) -> bool:
        return self.exact is not None

    def exact_at_end(self) -> np.ndarray:
        if self.exact is None:
            raise RuntimeError(f"{self.name} has no closed-form solution")
        return np.asarray(self.exact(self.problem.tf)).reshape(-1)

    def __repr__(self) -> str:
        return f"Benchmark({self.name}, n={self.problem.n})"


# ---------------------------------------------------------------------------
# Problems with closed-form solutions -- the basis of order verification
# ---------------------------------------------------------------------------


def exponential_decay(k: float = 1.5, y0: float = 2.0, t_end: float = 4.0) -> Benchmark:
    """``y' = -k y``. The simplest possible order check."""
    prob = ODEProblem(
        f=lambda t, y: -k * y,
        t_span=(0.0, t_end),
        y0=[y0],
        jac=lambda t, y: np.array([[-k]]),
    )
    return Benchmark(
        name="exponential_decay",
        problem=prob,
        exact=lambda t: y0 * np.exp(-k * np.asarray(t)),
        description="y' = -k y, scalar linear decay.",
        tags=("analytic", "linear", "nonstiff"),
    )


def linear_system(t_end: float = 2.0) -> Benchmark:
    """``y' = A y`` with a non-normal, non-diagonalisable-looking A.

    The reference solution is ``expm(A t) y0``. A genuine coupled system, so it
    exercises the vector paths that a scalar problem leaves untested.
    """
    A = np.array([[-2.0, 1.0, 0.5], [0.3, -1.0, -2.0], [0.0, 1.5, -3.0]])
    y0 = np.array([1.0, -0.5, 2.0])

    def exact(t):
        t = np.asarray(t, dtype=float)
        if t.ndim == 0:
            return expm(A * float(t)) @ y0
        return np.stack([expm(A * float(ti)) @ y0 for ti in t], axis=-1)

    prob = ODEProblem(
        f=lambda t, y: A @ y,
        t_span=(0.0, t_end),
        y0=y0,
        jac=lambda t, y: A,
    )
    return Benchmark(
        name="linear_system",
        problem=prob,
        exact=exact,
        description="3x3 constant-coefficient linear system, reference via expm.",
        tags=("analytic", "linear", "nonstiff"),
    )


def sine_cosine(t_end: float = 6.0) -> Benchmark:
    """The harmonic oscillator ``y'' = -y`` as a first-order pair.

    Non-autonomous behaviour in disguise and a nonzero invariant, so it catches
    sign errors that a monotone decay problem hides.
    """
    prob = ODEProblem(
        f=lambda t, y: np.array([y[1], -y[0]]),
        t_span=(0.0, t_end),
        y0=[0.0, 1.0],
        jac=lambda t, y: np.array([[0.0, 1.0], [-1.0, 0.0]]),
    )

    def exact(t):
        t = np.asarray(t, dtype=float)
        return np.stack([np.sin(t), np.cos(t)], axis=0)

    return Benchmark(
        name="sine_cosine",
        problem=prob,
        exact=exact,
        invariant=lambda y: float(0.5 * (y[0] ** 2 + y[1] ** 2)),
        description="Harmonic oscillator; exact solution (sin t, cos t).",
        tags=("analytic", "oscillatory", "nonstiff"),
    )


def logistic(r: float = 1.2, y0: float = 0.1, t_end: float = 8.0) -> Benchmark:
    """``y' = r y (1 - y)``. Nonlinear, with a closed-form sigmoid solution."""
    prob = ODEProblem(
        f=lambda t, y: r * y * (1.0 - y),
        t_span=(0.0, t_end),
        y0=[y0],
        jac=lambda t, y: np.array([[r * (1.0 - 2.0 * y[0])]]),
    )

    def exact(t):
        t = np.asarray(t, dtype=float)
        return np.atleast_1d(y0 / (y0 + (1.0 - y0) * np.exp(-r * t)))

    return Benchmark(
        name="logistic",
        problem=prob,
        exact=exact,
        description="Logistic growth, nonlinear with an analytic solution.",
        tags=("analytic", "nonlinear", "nonstiff"),
    )


# ---------------------------------------------------------------------------
# Classic non-stiff benchmarks
# ---------------------------------------------------------------------------


def lotka_volterra(a=1.5, b=1.0, c=3.0, d=1.0, t_end: float = 15.0) -> Benchmark:
    """Predator-prey. Periodic, mildly nonlinear, with a conserved quantity."""

    def f(t, y):
        return np.array([a * y[0] - b * y[0] * y[1], -c * y[1] + d * y[0] * y[1]])

    def jac(t, y):
        return np.array(
            [[a - b * y[1], -b * y[0]], [d * y[1], -c + d * y[0]]]
        )

    prob = ODEProblem(f=f, t_span=(0.0, t_end), y0=[10.0, 5.0], jac=jac)
    return Benchmark(
        name="lotka_volterra",
        problem=prob,
        invariant=lambda y: float(
            d * y[0] - c * np.log(y[0]) + b * y[1] - a * np.log(y[1])
        ),
        description="Predator-prey system with a first integral.",
        tags=("nonlinear", "periodic", "nonstiff"),
    )


def van_der_pol(mu: float = 1.0, t_end: float | None = None) -> Benchmark:
    """Van der Pol oscillator. Non-stiff at mu=1, brutally stiff at mu=1000."""
    if t_end is None:
        t_end = 3.0 * mu if mu > 10 else 20.0

    def f(t, y):
        return np.array([y[1], mu * (1.0 - y[0] ** 2) * y[1] - y[0]])

    def jac(t, y):
        return np.array(
            [[0.0, 1.0], [-2.0 * mu * y[0] * y[1] - 1.0, mu * (1.0 - y[0] ** 2)]]
        )

    prob = ODEProblem(f=f, t_span=(0.0, t_end), y0=[2.0, 0.0], jac=jac)
    return Benchmark(
        name=f"van_der_pol(mu={mu:g})",
        problem=prob,
        stiff=mu >= 10,
        description="Relaxation oscillator; stiffness scales with mu.",
        tags=("nonlinear", "stiff" if mu >= 10 else "nonstiff"),
    )


def brusselator(a: float = 1.0, b: float = 3.0, t_end: float = 20.0) -> Benchmark:
    """Autocatalytic reaction, settling onto a limit cycle."""

    def f(t, y):
        return np.array(
            [a + y[0] ** 2 * y[1] - (b + 1) * y[0], b * y[0] - y[0] ** 2 * y[1]]
        )

    def jac(t, y):
        return np.array(
            [
                [2 * y[0] * y[1] - (b + 1), y[0] ** 2],
                [b - 2 * y[0] * y[1], -(y[0] ** 2)],
            ]
        )

    prob = ODEProblem(f=f, t_span=(0.0, t_end), y0=[1.5, 3.0], jac=jac)
    return Benchmark(
        name="brusselator",
        problem=prob,
        description="Two-species autocatalytic reaction with a limit cycle.",
        tags=("nonlinear", "nonstiff"),
    )


def fitzhugh_nagumo(a: float = 0.7, b: float = 0.8, tau: float = 12.5,
                    I_ext: float = 0.5, t_end: float = 200.0) -> Benchmark:
    """Excitable membrane: the two-variable reduction of Hodgkin-Huxley.

    ``v`` is the fast voltage-like variable and ``w`` the slow recovery one, and
    the timescale separation ``tau = 12.5`` between them is the whole character
    of the model -- it is the cleanest small example of a slow-fast system, and
    of *excitability*: below threshold a perturbation decays, above it the state
    takes a long excursion before returning.

    The oscillating window is derived rather than looked up. The fixed point
    loses stability where the trace of the Jacobian vanishes, and the trace is
    ``(1 - v^2) - b/tau``, so the Hopf points sit at ``v^2 = 1 - b/tau`` and the
    corresponding currents follow from the fixed-point equation
    ``I = -v + v^3/3 + (v + a)/b``. For the defaults that gives
    ``I in (0.331281, 1.418719)``, which is where the measured amplitude of `v`
    actually turns on and off: 1.5e-2 at I = 0.30 against 3.75 at I = 0.33, and
    3.75 at I = 1.42 against 3.4e-5 at I = 1.50.
    """

    def f(t, y):
        v, w = y[0], y[1]
        return np.array([v - v ** 3 / 3.0 - w + I_ext, (v + a - b * w) / tau])

    def jac(t, y):
        v = y[0]
        return np.array([[1.0 - v * v, -1.0], [1.0 / tau, -b / tau]])

    prob = ODEProblem(f=f, t_span=(0.0, t_end), y0=[-1.0, -0.5], jac=jac)
    return Benchmark(
        name=f"fitzhugh_nagumo(I={I_ext:g})",
        problem=prob,
        description="Excitable membrane; a slow-fast system with a Hopf window.",
        tags=("nonlinear", "nonstiff", "oscillator"),
    )


def hopf_window(a: float = 0.7, b: float = 0.8, tau: float = 12.5):
    """The interval of `I_ext` on which `fitzhugh_nagumo` oscillates.

    Derived from ``trace J = 0``, not measured and not transcribed -- see the
    reasoning in `fitzhugh_nagumo`. Returned so the interface can mark the
    window on the slider and a test can check the model against its own theory.
    """
    v_squared = 1.0 - b / tau
    if v_squared <= 0.0:
        # No real v satisfies trace J = 0: the fixed point never loses
        # stability and there is no oscillating window to mark.
        return None
    currents = [
        -v + v ** 3 / 3.0 + (v + a) / b
        for v in (-np.sqrt(v_squared), np.sqrt(v_squared))
    ]
    return (min(currents), max(currents))


def sir(beta: float = 0.9, gamma: float = 0.2, N: float = 1000.0,
        initial_infected: float = 1.0, t_end: float = 80.0) -> Benchmark:
    """The compartment model everyone met in 2020: susceptible, infected, recovered.

    Worth having as more than a topical example. ``S + I + R`` is conserved
    exactly, which makes it one of the few nonlinear models here with an
    invariant a reader can check by inspection -- and the basic reproduction
    number ``R0 = beta/gamma`` decides the whole qualitative outcome, so it is a
    two-slider demonstration that a threshold in a parameter is a different kind
    of thing from a change of degree.
    """

    def f(t, y):
        S, I = y[0], y[1]
        infection = beta * S * I / N
        recovery = gamma * I
        return np.array([-infection, infection - recovery, recovery])

    def jac(t, y):
        S, I = y[0], y[1]
        return np.array([
            [-beta * I / N, -beta * S / N, 0.0],
            [beta * I / N, beta * S / N - gamma, 0.0],
            [0.0, gamma, 0.0],
        ])

    prob = ODEProblem(
        f=f, t_span=(0.0, t_end),
        y0=[N - initial_infected, initial_infected, 0.0], jac=jac,
    )
    return Benchmark(
        name="sir",
        problem=prob,
        invariant=lambda y: float(np.sum(np.asarray(y)[:3])),
        description="Epidemic compartments; S+I+R is conserved and R0 = beta/gamma.",
        tags=("nonlinear", "nonstiff", "biology"),
    )


def pendulum(damping: float = 0.0, t_end: float = 20.0) -> Benchmark:
    """Damped pendulum ``theta'' = -sin(theta) - b theta'``.

    The canonical phase portrait. Centres (or stable spirals when damped) at
    ``theta = 2k*pi`` and saddles at ``theta = (2k+1)*pi``, joined by
    separatrices that divide swinging from rotating motion. Undamped it is
    Hamiltonian and conserves energy exactly.
    """

    def f(t, y):
        return np.array([y[1], -np.sin(y[0]) - damping * y[1]])

    def jac(t, y):
        return np.array([[0.0, 1.0], [-np.cos(y[0]), -damping]])

    prob = ODEProblem(f=f, t_span=(0.0, t_end), y0=[2.0, 0.0], jac=jac)
    return Benchmark(
        name=f"pendulum(b={damping:g})",
        problem=prob,
        invariant=(
            (lambda y: float(0.5 * y[1] ** 2 - np.cos(y[0])))
            if damping == 0.0 else None
        ),
        description="Damped pendulum; saddles, centres and separatrices.",
        tags=("nonlinear", "oscillator", "nonstiff")
        + (("hamiltonian",) if damping == 0.0 else ()),
    )


def duffing(alpha: float = -1.0, beta: float = 1.0, delta: float = 0.2,
            t_end: float = 30.0) -> Benchmark:
    """Duffing oscillator ``x'' = -delta x' - alpha x - beta x^3``.

    With ``alpha < 0 < beta`` the potential has two wells: a saddle at the
    origin and a fixed point in each well, spirals when damped and centres
    when not. Raising `alpha` through zero merges the three into one -- a
    pitchfork bifurcation that is easy to watch on a slider.
    """

    def f(t, y):
        return np.array([y[1], -delta * y[1] - alpha * y[0] - beta * y[0] ** 3])

    def jac(t, y):
        return np.array([[0.0, 1.0], [-alpha - 3 * beta * y[0] ** 2, -delta]])

    prob = ODEProblem(f=f, t_span=(0.0, t_end), y0=[1.5, 0.0], jac=jac)
    return Benchmark(
        name=f"duffing(a={alpha:g}, b={beta:g}, d={delta:g})",
        problem=prob,
        invariant=(
            (lambda y: float(
                0.5 * y[1] ** 2 + 0.5 * alpha * y[0] ** 2 + 0.25 * beta * y[0] ** 4
            ))
            if delta == 0.0 else None
        ),
        description="Double-well Duffing oscillator; pitchfork bifurcation in alpha.",
        tags=("nonlinear", "oscillator", "nonstiff"),
    )


def lorenz(sigma=10.0, rho=28.0, beta=8.0 / 3.0, t_end: float = 20.0) -> Benchmark:
    """The Lorenz attractor. Chaotic, so it is an integration-robustness test
    rather than an accuracy test -- trajectories separate exponentially."""

    def f(t, y):
        return np.array(
            [
                sigma * (y[1] - y[0]),
                y[0] * (rho - y[2]) - y[1],
                y[0] * y[1] - beta * y[2],
            ]
        )

    def jac(t, y):
        return np.array(
            [
                [-sigma, sigma, 0.0],
                [rho - y[2], -1.0, -y[0]],
                [y[1], y[0], -beta],
            ]
        )

    prob = ODEProblem(f=f, t_span=(0.0, t_end), y0=[1.0, 1.0, 1.0], jac=jac)
    return Benchmark(
        name="lorenz",
        problem=prob,
        description="Chaotic convection model.",
        tags=("nonlinear", "chaotic", "nonstiff"),
    )


def kepler(eccentricity: float = 0.6, n_orbits: float = 3.0) -> Benchmark:
    """Two-body problem in the plane, state ``[x, y, vx, vy]``.

    Total energy is conserved exactly by the true flow, so the drift in
    `invariant` measures a method's qualitative fidelity -- the basis of the
    symplectic comparison in Phase 4. The period is 2*pi for these units.
    """
    e = eccentricity
    y0 = np.array([1.0 - e, 0.0, 0.0, np.sqrt((1.0 + e) / (1.0 - e))])

    def f(t, y):
        x1, x2, v1, v2 = y
        r3 = (x1 * x1 + x2 * x2) ** 1.5
        return np.array([v1, v2, -x1 / r3, -x2 / r3])

    def jac(t, y):
        x1, x2 = y[0], y[1]
        r2 = x1 * x1 + x2 * x2
        r3, r5 = r2 ** 1.5, r2 ** 2.5
        J = np.zeros((4, 4))
        J[0, 2] = J[1, 3] = 1.0
        J[2, 0] = -1.0 / r3 + 3.0 * x1 * x1 / r5
        J[2, 1] = 3.0 * x1 * x2 / r5
        J[3, 0] = 3.0 * x1 * x2 / r5
        J[3, 1] = -1.0 / r3 + 3.0 * x2 * x2 / r5
        return J

    def energy(y):
        y = np.asarray(y)
        r = np.hypot(y[0], y[1])
        return float(0.5 * (y[2] ** 2 + y[3] ** 2) - 1.0 / r)

    prob = ODEProblem(
        f=f, t_span=(0.0, 2.0 * np.pi * n_orbits), y0=y0, jac=jac
    )
    return Benchmark(
        name=f"kepler(e={e:g})",
        problem=prob,
        invariant=energy,
        description="Planar two-body problem; energy is conserved.",
        tags=("nonlinear", "hamiltonian", "nonstiff"),
    )


def pleiades(t_end: float = 3.0) -> Benchmark:
    """The Pleiades problem: seven gravitating bodies in the plane, 28 equations.

    A standard non-stiff benchmark (Hairer & Wanner I, II.10) featuring several
    near-collisions that force sharp step-size reductions.
    """
    m = np.arange(1.0, 8.0)
    x0 = np.array([3.0, 3.0, -1.0, -3.0, 2.0, -2.0, 2.0])
    y0_ = np.array([3.0, -3.0, 2.0, 0.0, 0.0, -4.0, 4.0])
    vx0 = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.75, -1.5])
    vy0 = np.array([0.0, 0.0, 0.0, -1.25, 1.0, 0.0, 0.0])
    y0 = np.concatenate([x0, y0_, vx0, vy0])

    def f(t, y):
        x, yy = y[:7], y[7:14]
        dx = x[:, None] - x[None, :]
        dy = yy[:, None] - yy[None, :]
        r = (dx * dx + dy * dy) ** 1.5
        np.fill_diagonal(r, 1.0)  # self-terms are zeroed by dx/dy anyway
        w = m[None, :] / r
        ax = -np.sum(dx * w, axis=1)
        ay = -np.sum(dy * w, axis=1)
        return np.concatenate([y[14:21], y[21:28], ax, ay])

    prob = ODEProblem(f=f, t_span=(0.0, t_end), y0=y0)
    return Benchmark(
        name="pleiades",
        problem=prob,
        description="Seven-body gravitational problem, 28 equations.",
        tags=("nonlinear", "nbody", "nonstiff"),
    )


# ---------------------------------------------------------------------------
# Stiff benchmarks (exercised properly in Phase 2)
# ---------------------------------------------------------------------------


def robertson(t_end: float = 1e11) -> Benchmark:
    """Robertson's autocatalytic kinetics. The canonical stiff test problem.

    Rate constants spanning seven orders of magnitude, integrated over eleven
    decades of time. Explicit methods are hopeless here; this is the Phase 2
    acceptance test.
    """

    def f(t, y):
        return np.array(
            [
                -0.04 * y[0] + 1e4 * y[1] * y[2],
                0.04 * y[0] - 1e4 * y[1] * y[2] - 3e7 * y[1] ** 2,
                3e7 * y[1] ** 2,
            ]
        )

    def jac(t, y):
        return np.array(
            [
                [-0.04, 1e4 * y[2], 1e4 * y[1]],
                [0.04, -1e4 * y[2] - 6e7 * y[1], -1e4 * y[1]],
                [0.0, 6e7 * y[1], 0.0],
            ]
        )

    prob = ODEProblem(f=f, t_span=(0.0, t_end), y0=[1.0, 0.0, 0.0], jac=jac)
    return Benchmark(
        name="robertson",
        problem=prob,
        stiff=True,
        invariant=lambda y: float(np.sum(y[:3])),  # mass conservation: sum = 1
        description="Robertson chemical kinetics; the canonical stiff problem.",
        tags=("nonlinear", "stiff", "kinetics"),
    )


# ---------------------------------------------------------------------------
# Mass matrices and differential-algebraic systems
# ---------------------------------------------------------------------------


def mass_matrix_oscillator(t_end: float = 3.0) -> Benchmark:
    """``M y' = A y`` with a non-singular, non-diagonal mass matrix.

    Still an ODE -- equivalent to ``y' = M^-1 A y`` -- but it exercises the
    mass-matrix paths without the extra difficulty of a singular `M`. The
    reference is ``expm(M^-1 A t) y0``.
    """
    M = np.array([[2.0, 1.0], [1.0, 3.0]])
    A = np.array([[-1.0, 2.0], [-3.0, -1.0]])
    y0 = np.array([1.0, 0.5])
    Minv_A = np.linalg.solve(M, A)

    def exact(t):
        t = np.asarray(t, dtype=float)
        if t.ndim == 0:
            return expm(Minv_A * float(t)) @ y0
        return np.stack([expm(Minv_A * float(ti)) @ y0 for ti in t], axis=-1)

    prob = ODEProblem(
        f=lambda t, y: A @ y,
        t_span=(0.0, t_end),
        y0=y0,
        jac=lambda t, y: A,
        mass=M,
    )
    return Benchmark(
        name="mass_matrix_oscillator",
        problem=prob,
        exact=exact,
        description="Non-singular mass matrix, M y' = A y.",
        tags=("analytic", "linear", "mass"),
    )


def linear_dae(t_end: float = 3.0) -> Benchmark:
    """A semi-explicit index-1 DAE with a closed-form solution.

    ::

        y1' = y2
        0   = y1 + y2 - t

    so ``M = diag(1, 0)``. Eliminating the constraint gives ``y1' = t - y1``,
    whose solution from ``y1(0) = 0`` is ``y1 = e^-t + t - 1``, ``y2 = t - y1``.
    Index 1 because the algebraic equation can be solved for `y2` directly --
    its partial derivative with respect to `y2` is 1, never singular.

    Having an exact answer makes this the DAE the order and accuracy tests use;
    Robertson in DAE form covers the nonlinear stiff case.
    """
    prob = ODEProblem(
        f=lambda t, y: np.array([y[1], y[0] + y[1] - t]),
        t_span=(0.0, t_end),
        y0=[0.0, 0.0],
        jac=lambda t, y: np.array([[0.0, 1.0], [1.0, 1.0]]),
        mass=np.array([[1.0, 0.0], [0.0, 0.0]]),
    )

    def exact(t):
        t = np.asarray(t, dtype=float)
        y1 = np.exp(-t) + t - 1.0
        return np.stack([y1, t - y1], axis=0)

    return Benchmark(
        name="linear_dae",
        problem=prob,
        exact=exact,
        description="Semi-explicit index-1 DAE with an analytic solution.",
        tags=("analytic", "dae", "index1"),
    )


def robertson_dae(t_end: float = 1e11) -> Benchmark:
    """Robertson's kinetics as an index-1 DAE.

    The third rate equation is replaced by the conservation law
    ``y1 + y2 + y3 = 1`` that it implies, giving ``M = diag(1, 1, 0)``. The
    solution is identical to `robertson`, so the two can be cross-checked --
    but here mass is conserved *exactly*, by construction, rather than to within
    the integration tolerance.
    """

    def f(t, y):
        return np.array(
            [
                -0.04 * y[0] + 1e4 * y[1] * y[2],
                0.04 * y[0] - 1e4 * y[1] * y[2] - 3e7 * y[1] ** 2,
                y[0] + y[1] + y[2] - 1.0,
            ]
        )

    def jac(t, y):
        return np.array(
            [
                [-0.04, 1e4 * y[2], 1e4 * y[1]],
                [0.04, -1e4 * y[2] - 6e7 * y[1], -1e4 * y[1]],
                [1.0, 1.0, 1.0],
            ]
        )

    prob = ODEProblem(
        f=f,
        t_span=(0.0, t_end),
        y0=[1.0, 0.0, 0.0],
        jac=jac,
        mass=np.diag([1.0, 1.0, 0.0]),
    )
    return Benchmark(
        name="robertson_dae",
        problem=prob,
        stiff=True,
        invariant=lambda y: float(np.sum(y[:3])),
        description="Robertson kinetics in index-1 DAE form.",
        tags=("nonlinear", "stiff", "dae", "index1"),
    )


# ---------------------------------------------------------------------------
# Event-driven
# ---------------------------------------------------------------------------


def bouncing_ball(h0: float = 1.0, g: float = 9.81, t_end: float = 10.0) -> Benchmark:
    """Free fall under gravity, state ``[height, velocity]``.

    Used for event verification: with ``h(0) = h0`` and zero initial velocity the
    ground impact happens at exactly ``sqrt(2 h0 / g)``, so the detected root can
    be checked against a closed-form answer.
    """
    prob = ODEProblem(
        f=lambda t, y: np.array([y[1], -g]),
        t_span=(0.0, t_end),
        y0=[h0, 0.0],
        jac=lambda t, y: np.array([[0.0, 1.0], [0.0, 0.0]]),
    )

    def exact(t):
        t = np.asarray(t, dtype=float)
        return np.stack([h0 - 0.5 * g * t**2, -g * t], axis=0)

    bench = Benchmark(
        name="bouncing_ball",
        problem=prob,
        exact=exact,
        description="Ballistic fall; first impact at sqrt(2*h0/g).",
        tags=("analytic", "events"),
    )
    bench.impact_time = float(np.sqrt(2.0 * h0 / g))  # type: ignore[attr-defined]
    return bench


def hires(t_end: float = 321.8122) -> Benchmark:
    """HIRES: eight-equation plant-physiology model of high irradiance response.

    A standard stiff benchmark from the Bari test set. Harder than Robertson in
    one respect -- it is genuinely eight-dimensional with a full Jacobian, so it
    exercises the linear algebra rather than just the step control.
    """

    def f(t, y):
        return np.array(
            [
                -1.71 * y[0] + 0.43 * y[1] + 8.32 * y[2] + 0.0007,
                1.71 * y[0] - 8.75 * y[1],
                -10.03 * y[2] + 0.43 * y[3] + 0.035 * y[4],
                8.32 * y[1] + 1.71 * y[2] - 1.12 * y[3],
                -1.745 * y[4] + 0.43 * y[5] + 0.43 * y[6],
                -280.0 * y[5] * y[7] + 0.69 * y[3] + 1.71 * y[4]
                - 0.43 * y[5] + 0.69 * y[6],
                280.0 * y[5] * y[7] - 1.81 * y[6],
                -280.0 * y[5] * y[7] + 1.81 * y[6],
            ]
        )

    def jac(t, y):
        J = np.zeros((8, 8))
        J[0, 0], J[0, 1], J[0, 2] = -1.71, 0.43, 8.32
        J[1, 0], J[1, 1] = 1.71, -8.75
        J[2, 2], J[2, 3], J[2, 4] = -10.03, 0.43, 0.035
        J[3, 1], J[3, 2], J[3, 3] = 8.32, 1.71, -1.12
        J[4, 4], J[4, 5], J[4, 6] = -1.745, 0.43, 0.43
        J[5, 3], J[5, 4] = 0.69, 1.71
        J[5, 5], J[5, 6], J[5, 7] = -280.0 * y[7] - 0.43, 0.69, -280.0 * y[5]
        J[6, 5], J[6, 6], J[6, 7] = 280.0 * y[7], -1.81, 280.0 * y[5]
        J[7, 5], J[7, 6], J[7, 7] = -280.0 * y[7], 1.81, -280.0 * y[5]
        return J

    y0 = np.array([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0057])
    prob = ODEProblem(f=f, t_span=(0.0, t_end), y0=y0, jac=jac)
    return Benchmark(
        name="hires",
        problem=prob,
        stiff=True,
        description="HIRES, 8 stiff equations from the Bari test set.",
        tags=("nonlinear", "stiff", "kinetics"),
    )


def orego(t_end: float = 360.0) -> Benchmark:
    """OREGO: the Oregonator model of the Belousov-Zhabotinsky reaction.

    Stiff and strongly oscillatory -- the concentrations swing over several
    orders of magnitude each cycle, so the step size must change by comparable
    factors. A good stress test of the step controller rather than just of
    stability.
    """

    def f(t, y):
        return np.array(
            [
                77.27 * (y[1] + y[0] * (1.0 - 8.375e-6 * y[0] - y[1])),
                (y[2] - (1.0 + y[0]) * y[1]) / 77.27,
                0.161 * (y[0] - y[2]),
            ]
        )

    def jac(t, y):
        return np.array(
            [
                [
                    77.27 * (1.0 - 2 * 8.375e-6 * y[0] - y[1]),
                    77.27 * (1.0 - y[0]),
                    0.0,
                ],
                [-y[1] / 77.27, -(1.0 + y[0]) / 77.27, 1.0 / 77.27],
                [0.161, 0.0, -0.161],
            ]
        )

    prob = ODEProblem(f=f, t_span=(0.0, t_end), y0=[1.0, 2.0, 3.0], jac=jac)
    return Benchmark(
        name="orego",
        problem=prob,
        stiff=True,
        description="Oregonator (Belousov-Zhabotinsky), stiff and oscillatory.",
        tags=("nonlinear", "stiff", "oscillatory", "kinetics"),
    )


# ---------------------------------------------------------------------------
# Structured problems for the specialised methods
# ---------------------------------------------------------------------------


def kepler_second_order(eccentricity: float = 0.6, n_orbits: float = 3.0) -> Benchmark:
    """Kepler as ``q'' = -q/|q|^3``, the separable form symplectic methods need.

    Identical dynamics to `kepler`, but presented as an acceleration so the
    flow can be split into kinetic and potential halves.
    """
    from ..steppers import second_order_problem

    e = eccentricity
    q0 = np.array([1.0 - e, 0.0])
    v0 = np.array([0.0, np.sqrt((1.0 + e) / (1.0 - e))])

    def acceleration(t, q):
        return -q / (q[0] * q[0] + q[1] * q[1]) ** 1.5

    def energy(y):
        y = np.asarray(y)
        return float(0.5 * (y[2] ** 2 + y[3] ** 2) - 1.0 / np.hypot(y[0], y[1]))

    def angular_momentum(y):
        y = np.asarray(y)
        return float(y[0] * y[3] - y[1] * y[2])

    prob = second_order_problem(
        acceleration, (0.0, 2.0 * np.pi * n_orbits), q0, v0
    )
    bench = Benchmark(
        name=f"kepler_second_order(e={e:g})",
        problem=prob,
        invariant=energy,
        description="Planar two-body problem as q'' = a(q); energy is conserved.",
        tags=("nonlinear", "hamiltonian", "separable"),
    )
    bench.angular_momentum = angular_momentum   # type: ignore[attr-defined]
    bench.period = 2.0 * np.pi                  # type: ignore[attr-defined]
    return bench


def harmonic_oscillator_2d(t_end: float = 20.0) -> Benchmark:
    """``q'' = -q`` in two dimensions: a separable system with an exact solution."""
    from ..steppers import second_order_problem

    q0 = np.array([1.0, 0.0])
    v0 = np.array([0.0, 2.0])
    prob = second_order_problem(lambda t, q: -q, (0.0, t_end), q0, v0)

    def exact(t):
        t = np.asarray(t, dtype=float)
        return np.stack(
            [
                q0[0] * np.cos(t) + v0[0] * np.sin(t),
                q0[1] * np.cos(t) + v0[1] * np.sin(t),
                -q0[0] * np.sin(t) + v0[0] * np.cos(t),
                -q0[1] * np.sin(t) + v0[1] * np.cos(t),
            ],
            axis=0,
        )

    return Benchmark(
        name="harmonic_oscillator_2d",
        problem=prob,
        exact=exact,
        invariant=lambda y: float(0.5 * (np.asarray(y) ** 2).sum()),
        description="Separable q'' = -q with an analytic solution.",
        tags=("analytic", "hamiltonian", "separable"),
    )


def kuramoto_sivashinsky(n_modes: int = 128, length: float = 32.0 * np.pi,
                         t_end: float = 60.0) -> Benchmark:
    """Kuramoto-Sivashinsky, ``u_t = -u_xx - u_xxxx - u u_x``, spectrally discretised.

    The showcase problem for exponential integrators. In Fourier space the
    linear part is diagonal, ``L = k^2 - k^4``, and enormously stiff: the
    highest modes decay like ``k^4``, giving a spectral radius in the millions
    for 128 modes. Any explicit method is bound by that; ETDRK4 is not bound by
    it at all, because ``exp(hL)`` is exact.

    The nonlinearity is evaluated pseudo-spectrally -- transform to real space,
    square, transform back -- which is the standard treatment and why `N` is
    written as a transform sandwich rather than a convolution.

    The state is the complex Fourier coefficient vector. Solutions settle onto a
    chaotic attractor whose spacetime plot is the familiar KS "flame front".
    """
    from ..steppers import semilinear_problem

    x = length * np.arange(1, n_modes + 1) / n_modes
    u0 = np.cos(x / 16.0) * (1.0 + np.sin(x / 16.0))

    k = 2.0 * np.pi * np.fft.fftfreq(n_modes, d=length / n_modes)
    L = k**2 - k**4
    u0_hat = np.fft.fft(u0)

    # Dealiasing: zero the top third of the spectrum so the quadratic
    # nonlinearity cannot fold energy back down as spurious low-mode content.
    mask = np.abs(k) < (2.0 / 3.0) * np.abs(k).max()

    def nonlinear(t, u_hat):
        u = np.real(np.fft.ifft(u_hat))
        return -0.5j * k * np.fft.fft(u * u) * mask

    prob = semilinear_problem(L, nonlinear, (0.0, t_end), u0_hat)

    bench = Benchmark(
        name="kuramoto_sivashinsky",
        problem=prob,
        description="KS equation, 128 Fourier modes; semilinear and very stiff.",
        tags=("pde", "semilinear", "stiff", "chaotic"),
    )
    bench.x = x                                        # type: ignore[attr-defined]
    bench.k = k                                        # type: ignore[attr-defined]
    bench.to_real = lambda uh: np.real(np.fft.ifft(uh, axis=0))  # type: ignore[attr-defined]
    return bench


def allen_cahn(n_modes: int = 128, epsilon: float = 0.01,
               t_end: float = 30.0) -> Benchmark:
    """Allen-Cahn ``u_t = eps u_xx + u - u^3``: a gentler semilinear test.

    Real-valued and non-chaotic, so unlike KS it can be checked against a
    reference solution rather than only for qualitative behaviour.
    """
    from ..steppers import semilinear_problem

    x = 2.0 * np.pi * np.arange(n_modes) / n_modes
    u0 = 0.5 * np.sin(x) + 0.1 * np.cos(3 * x)
    k = np.fft.fftfreq(n_modes, d=1.0 / n_modes)
    L = -epsilon * k**2 + 1.0

    def nonlinear(t, u_hat):
        u = np.real(np.fft.ifft(u_hat))
        return -np.fft.fft(u**3)

    prob = semilinear_problem(L, nonlinear, (0.0, t_end), np.fft.fft(u0))
    bench = Benchmark(
        name="allen_cahn",
        problem=prob,
        description="Allen-Cahn reaction-diffusion, spectrally discretised.",
        tags=("pde", "semilinear", "stiff"),
    )
    bench.x = x                                        # type: ignore[attr-defined]
    bench.to_real = lambda uh: np.real(np.fft.ifft(uh, axis=0))  # type: ignore[attr-defined]
    return bench


# ---------------------------------------------------------------------------
# Boundary value problems
# ---------------------------------------------------------------------------


@dataclass
class BVPBenchmark:
    """A two-point BVP, with a reference solution where one exists."""

    name: str
    problem: object                      # BVProblem; imported lazily
    exact: Callable | None = None
    guess: Callable | np.ndarray | None = None
    description: str = ""

    def __repr__(self) -> str:
        return f"BVPBenchmark({self.name})"


def bvp_linear(t_end: float = 1.0) -> BVPBenchmark:
    """``y'' = y`` with ``y(0) = 0``, ``y(1) = 1``.

    Solution ``sinh(x)/sinh(1)``. Linear, so Newton must converge in a single
    step from any guess -- which makes it a sharp test of the shooting Jacobian:
    if any block is wrong, one iteration will not suffice.
    """
    from ..bvp import BVProblem

    prob = BVProblem(
        f=lambda t, y: np.array([y[1], y[0]]),
        t_span=(0.0, t_end),
        bc=lambda ya, yb: np.array([ya[0], yb[0] - 1.0]),
        n=2,
        jac=lambda t, y: np.array([[0.0, 1.0], [1.0, 0.0]]),
    )

    def exact(t):
        t = np.asarray(t, dtype=float)
        s = np.sinh(1.0)
        return np.stack([np.sinh(t) / s, np.cosh(t) / s], axis=0)

    return BVPBenchmark(
        name="bvp_linear",
        problem=prob,
        exact=exact,
        guess=np.array([0.5, 1.0]),
        description="y'' = y, y(0)=0, y(1)=1; solution sinh(x)/sinh(1).",
    )


def bvp_trig(k: float = 6.0) -> BVPBenchmark:
    """``y'' = -k^2 y`` with ``y(0) = 0``, ``y(1) = 1``: an oscillatory BVP.

    Solution ``sin(kx)/sin(k)``. With `k` large the single-shooting map becomes
    badly conditioned, so this is where multiple shooting earns its keep.
    """
    from ..bvp import BVProblem

    prob = BVProblem(
        f=lambda t, y: np.array([y[1], -(k**2) * y[0]]),
        t_span=(0.0, 1.0),
        bc=lambda ya, yb: np.array([ya[0], yb[0] - 1.0]),
        n=2,
        jac=lambda t, y: np.array([[0.0, 1.0], [-(k**2), 0.0]]),
    )

    def exact(t):
        t = np.asarray(t, dtype=float)
        s = np.sin(k)
        return np.stack([np.sin(k * t) / s, k * np.cos(k * t) / s], axis=0)

    return BVPBenchmark(
        name=f"bvp_trig(k={k:g})",
        problem=prob,
        exact=exact,
        guess=lambda t: np.array([t, 1.0]),
        description="y'' = -k^2 y, oscillatory two-point BVP.",
    )


def bratu(lam: float = 1.0, branch: str = "lower") -> BVPBenchmark:
    """Bratu's problem ``y'' + lam*exp(y) = 0``, ``y(0) = y(1) = 0``.

    The classic nonlinear BVP. For ``0 < lam < lam_c = 3.513830719...`` it has
    *two* solutions; at `lam_c` they merge and above it none exists. Which one
    Newton finds is decided entirely by the initial guess, which makes this the
    test that the solver follows the guess rather than always sliding to the
    easy answer.

    The exact solution is ``y(x) = -2 ln( cosh((x - 1/2) theta / 2) / cosh(theta/4) )``
    where `theta` solves ``theta = sqrt(2 lam) cosh(theta/4)``. That equation has
    the two roots corresponding to the two branches.
    """
    from scipy.optimize import brentq

    from ..bvp import BVProblem

    prob = BVProblem(
        f=lambda t, y: np.array([y[1], -lam * np.exp(y[0])]),
        t_span=(0.0, 1.0),
        bc=lambda ya, yb: np.array([ya[0], yb[0]]),
        n=2,
        jac=lambda t, y: np.array([[0.0, 1.0], [-lam * np.exp(y[0]), 0.0]]),
    )

    def theta_equation(theta):
        return theta - np.sqrt(2 * lam) * np.cosh(theta / 4)

    # The two roots straddle the maximum of g(theta) = theta - sqrt(2 lam)
    # cosh(theta/4). Setting g'(theta) = 1 - sqrt(2 lam) sinh(theta/4)/4 = 0
    # gives sinh(theta/4) = 4/sqrt(2 lam), so theta* = 4 arcsinh(sqrt(8/lam)).
    # The two branches merge exactly when g(theta*) = 0, which is lam_c.
    theta_star = 4 * np.arcsinh(np.sqrt(8.0 / lam))
    if theta_equation(theta_star) < 0:
        raise ValueError(f"Bratu has no solution for lam={lam} (lam_c ~ 3.5138)")
    theta = (
        brentq(theta_equation, 1e-12, theta_star)
        if branch == "lower"
        else brentq(theta_equation, theta_star, 100.0)
    )

    def exact(t):
        t = np.asarray(t, dtype=float)
        y = -2.0 * np.log(np.cosh((t - 0.5) * theta / 2) / np.cosh(theta / 4))
        dy = -theta * np.tanh((t - 0.5) * theta / 2)
        return np.stack([y, dy], axis=0)

    peak = float(exact(0.5)[0])
    guess = (
        (lambda t: np.array([peak * 4 * t * (1 - t), 0.0]))
        if branch == "lower"
        else (lambda t: np.array([peak * 4 * t * (1 - t), 0.0]))
    )

    bench = BVPBenchmark(
        name=f"bratu(lam={lam:g}, {branch})",
        problem=prob,
        exact=exact,
        guess=guess,
        description=f"y'' + {lam:g} exp(y) = 0, {branch} branch.",
    )
    bench.theta = theta       # type: ignore[attr-defined]
    bench.peak = peak         # type: ignore[attr-defined]
    return bench


# ---------------------------------------------------------------------------
# Textbook models
#
# Every other problem in this module is here because it is hard: stiff, chaotic,
# a known integrator torture test. These are here because they are the ones a
# first course is actually about -- a tank, a circuit, a cooling cup -- and
# because a learner meets an ODE as something derived from a situation rather
# than handed over ready-made.
#
# Each has a closed form, so the convergence suite can use it and the
# Methods-by-Hand table has something to measure error against.
# ---------------------------------------------------------------------------


def mixing_tank(volume: float = 100.0, flow: float = 5.0,
                inflow_concentration: float = 0.4, initial_mass: float = 5.0,
                t_end: float = 60.0) -> Benchmark:
    """Brine entering and leaving a well-stirred tank at the same rate.

    ``Q' = flow * c_in - (flow / V) * Q``, with `Q` the dissolved mass in kg,
    `V` the volume in litres and `flow` in litres per minute. The classic
    first-order linear equation: the outflow concentration is ``Q / V`` because
    the tank is well stirred, which is the modelling assumption that makes it
    linear.

    Reaches the steady state ``V * c_in`` on a timescale ``V / flow``.
    """
    rate = flow / volume
    steady = volume * inflow_concentration

    prob = ODEProblem(
        f=lambda t, y: np.array([flow * inflow_concentration - rate * y[0]]),
        t_span=(0.0, t_end),
        y0=[initial_mass],
        jac=lambda t, y: np.array([[-rate]]),
    )

    def exact(t):
        t = np.asarray(t, dtype=float)
        return np.atleast_1d(steady + (initial_mass - steady) * np.exp(-rate * t))

    return Benchmark(
        name="mixing_tank",
        problem=prob,
        exact=exact,
        description=(
            "Brine in a well-stirred tank: Q' = flow*c_in - (flow/V)*Q. "
            "First-order linear; solved by an integrating factor."
        ),
        tags=("analytic", "linear", "first-order", "textbook", "1d"),
    )


def newton_cooling(ambient: float = 20.0, rate: float = 0.18,
                   initial: float = 95.0, t_end: float = 30.0) -> Benchmark:
    """A cup of coffee cooling towards room temperature.

    ``T' = -k (T - T_ambient)``, temperatures in degrees Celsius and `t` in
    minutes. Separable *and* first-order linear, which makes it the standard
    example for both techniques -- and the one where the two routes visibly give
    the same answer.
    """
    prob = ODEProblem(
        f=lambda t, y: np.array([-rate * (y[0] - ambient)]),
        t_span=(0.0, t_end),
        y0=[initial],
        jac=lambda t, y: np.array([[-rate]]),
    )

    def exact(t):
        t = np.asarray(t, dtype=float)
        return np.atleast_1d(ambient + (initial - ambient) * np.exp(-rate * t))

    return Benchmark(
        name="newton_cooling",
        problem=prob,
        exact=exact,
        description=(
            "Newton's law of cooling, T' = -k(T - T_ambient). Separable and "
            "linear at once, in degrees Celsius over minutes."
        ),
        tags=("analytic", "linear", "separation", "first-order", "textbook", "1d"),
    )


def rc_circuit(resistance: float = 1000.0, capacitance: float = 1e-3,
               supply: float = 5.0, initial_charge: float = 0.0,
               t_end: float = 6.0) -> Benchmark:
    """A resistor and capacitor in series with a constant supply.

    ``R Q' + Q/C = V``, i.e. ``Q' = (V - Q/C) / R``, with `Q` in coulombs, `R`
    in ohms and `C` in farads. The time constant ``RC`` is the whole content of
    the problem: after one it has covered 63% of the way to ``CV``.
    """
    tau = resistance * capacitance
    steady = capacitance * supply

    prob = ODEProblem(
        f=lambda t, y: np.array([(supply - y[0] / capacitance) / resistance]),
        t_span=(0.0, t_end),
        y0=[initial_charge],
        jac=lambda t, y: np.array([[-1.0 / tau]]),
    )

    def exact(t):
        t = np.asarray(t, dtype=float)
        return np.atleast_1d(steady + (initial_charge - steady) * np.exp(-t / tau))

    return Benchmark(
        name="rc_circuit",
        problem=prob,
        exact=exact,
        description=(
            "Charging an RC circuit: R Q' + Q/C = V, with a time constant of "
            "RC seconds."
        ),
        tags=("analytic", "linear", "first-order", "textbook", "circuit", "1d"),
    )


def falling_with_drag(mass: float = 80.0, drag: float = 12.0,
                      gravity: float = 9.81, t_end: float = 25.0) -> Benchmark:
    """A skydiver with drag proportional to speed.

    ``m v' = m g - b v``, in metres per second. Linear because the drag is taken
    proportional to `v` rather than to `v^2`, which is the simplification that
    makes it a first-course problem; the terminal velocity ``m g / b`` falls
    straight out of setting ``v' = 0``.
    """
    terminal = mass * gravity / drag
    rate = drag / mass

    prob = ODEProblem(
        f=lambda t, y: np.array([gravity - rate * y[0]]),
        t_span=(0.0, t_end),
        y0=[0.0],
        jac=lambda t, y: np.array([[-rate]]),
    )

    def exact(t):
        t = np.asarray(t, dtype=float)
        return np.atleast_1d(terminal * (1.0 - np.exp(-rate * t)))

    return Benchmark(
        name="falling_with_drag",
        problem=prob,
        exact=exact,
        description=(
            "Falling under gravity with linear drag: m v' = m g - b v. "
            "Terminal velocity m g / b, in m/s."
        ),
        tags=("analytic", "linear", "first-order", "textbook", "1d"),
    )


def harvested_population(rate: float = 0.6, capacity: float = 1000.0,
                         harvest: float = 60.0, initial: float = 200.0,
                         t_end: float = 20.0) -> Benchmark:
    """Logistic growth with a constant harvest taken off the top.

    ``P' = r P (1 - P/K) - H``. Still separable, and the interesting question is
    not the formula but the equilibria: harvesting shifts them together, and past
    ``H = rK/4`` they collide and vanish, which is a saddle-node bifurcation met
    long before anyone uses that name.

    No elementary closed form is offered here -- the partial-fraction solution
    exists but is unpleasant, and the point of the problem is the phase line.
    """
    prob = ODEProblem(
        f=lambda t, y: np.array([rate * y[0] * (1.0 - y[0] / capacity) - harvest]),
        t_span=(0.0, t_end),
        y0=[initial],
        jac=lambda t, y: np.array([[rate * (1.0 - 2.0 * y[0] / capacity)]]),
    )

    return Benchmark(
        name="harvested_population",
        problem=prob,
        description=(
            "Logistic growth with constant harvesting, P' = rP(1 - P/K) - H. "
            "The equilibria collide and vanish at H = rK/4."
        ),
        tags=("nonlinear", "separation", "first-order", "textbook", "biology", "1d"),
    )


def spring_mass_damper(mass: float = 1.0, damping: float = 0.5,
                       stiffness: float = 4.0, initial_position: float = 1.0,
                       initial_velocity: float = 0.0,
                       t_end: float = 20.0) -> Benchmark:
    """``m x'' + c x' + k x = 0``: the second-order equation of a first course.

    Written as a first-order system in ``(x, v)``. The three regimes are the
    whole lesson and are reached by moving `c` alone: under-damped below
    ``2*sqrt(mk)``, critically damped at it, over-damped above. The closed form
    below covers all three, including the repeated root.
    """
    omega0 = np.sqrt(stiffness / mass)
    zeta = damping / (2.0 * np.sqrt(mass * stiffness))

    prob = ODEProblem(
        f=lambda t, y: np.array([
            y[1],
            -(damping * y[1] + stiffness * y[0]) / mass,
        ]),
        t_span=(0.0, t_end),
        y0=[initial_position, initial_velocity],
        jac=lambda t, y: np.array([
            [0.0, 1.0],
            [-stiffness / mass, -damping / mass],
        ]),
    )

    def exact(t):
        t = np.asarray(t, dtype=float)
        x0, v0 = initial_position, initial_velocity
        decay = np.exp(-zeta * omega0 * t)
        if zeta < 1.0:                                   # under-damped
            wd = omega0 * np.sqrt(1.0 - zeta**2)
            a = x0
            b = (v0 + zeta * omega0 * x0) / wd
            x = decay * (a * np.cos(wd * t) + b * np.sin(wd * t))
            v = decay * (
                (-zeta * omega0) * (a * np.cos(wd * t) + b * np.sin(wd * t))
                + wd * (-a * np.sin(wd * t) + b * np.cos(wd * t))
            )
        elif np.isclose(zeta, 1.0):                      # critically damped
            a, b = x0, v0 + omega0 * x0
            x = decay * (a + b * t)
            v = decay * (b - omega0 * (a + b * t))
        else:                                            # over-damped
            root = omega0 * np.sqrt(zeta**2 - 1.0)
            r1, r2 = -zeta * omega0 + root, -zeta * omega0 - root
            b = (v0 - r1 * x0) / (r2 - r1)
            a = x0 - b
            x = a * np.exp(r1 * t) + b * np.exp(r2 * t)
            v = a * r1 * np.exp(r1 * t) + b * r2 * np.exp(r2 * t)
        return np.stack([np.atleast_1d(x), np.atleast_1d(v)], axis=0).reshape(2, -1).squeeze()

    return Benchmark(
        name="spring_mass_damper",
        problem=prob,
        exact=exact,
        description=(
            "m x'' + c x' + k x = 0, as a first-order system. Under-, "
            "critically and over-damped, selected by c alone."
        ),
        tags=("analytic", "linear", "second-order", "oscillator", "textbook", "2d"),
    )


#: Boundary value problems.
BVPS = (bvp_linear, bvp_trig, lambda: bratu(1.0, "lower"), lambda: bratu(1.0, "upper"))


# ---------------------------------------------------------------------------
# Collections
# ---------------------------------------------------------------------------

#: Problems with a closed-form solution *and* an O(1) state: the
#: order-of-convergence suite.
#:
#: Deliberately not "everything with a closed form". Measuring an order needs a
#: usable window between the asymptotic regime and the round-off floor, and the
#: floor is absolute. A problem whose state is small in its own natural units --
#: `rc_circuit` carries a charge of about 5e-3 coulombs -- has proportionally
#: smaller local errors and reaches that floor several halvings early, which
#: reads as a slope of 5.7 where 6 was expected. That is a property of the units,
#: not of the method, and it does not belong in a test about methods. The
#: textbook models are checked against their closed forms in
#: `tests/test_textbook.py` instead, over the whole interval.
ANALYTIC = (exponential_decay, linear_system, sine_cosine, logistic)

#: Models a first course is actually about, as opposed to the integrator
#: torture tests that make up the rest of this module.
def forced_spring(mass: float = 1.0, damping: float = 0.4,
                  stiffness: float = 4.0, amplitude: float = 1.0,
                  frequency: float = 1.8, initial_position: float = 0.0,
                  initial_velocity: float = 0.0,
                  t_end: float = 40.0) -> Benchmark:
    """``m x'' + c x' + k x = F cos(wt)``: the spring with something driving it.

    The forced counterpart of `spring_mass_damper`, and the model Unit 4 of the
    course is about. Two things are visible here that the unforced problem
    cannot show. The **transient** dies away and the **steady state** does not,
    so the long-run motion is set by the forcing rather than by how the system
    started; and sweeping `frequency` past ``sqrt(k/m)`` walks through
    resonance, where the steady amplitude peaks.

    The closed form is the steady state plus a transient matched to the initial
    conditions, which is the same three-regime formula as the unforced case
    with different starting values -- the amplitude and phase below simply move
    where the transient has to begin. Damping is kept positive by the parameter
    range: at ``c = 0`` and ``w = sqrt(k/m)`` the steady amplitude is not
    finite, and that case belongs in the lesson rather than in a benchmark.
    """
    omega = float(frequency)
    # Steady-state amplitude and phase lag: the standard response of a driven
    # linear oscillator, and the two numbers a vibration table is designed for.
    reactance = stiffness - mass * omega**2
    steady = amplitude / np.hypot(reactance, damping * omega)
    phase = np.arctan2(damping * omega, reactance)

    prob = ODEProblem(
        f=lambda t, y: np.array([
            y[1],
            (amplitude * np.cos(omega * t)
             - damping * y[1] - stiffness * y[0]) / mass,
        ]),
        t_span=(0.0, t_end),
        y0=[initial_position, initial_velocity],
        jac=lambda t, y: np.array([
            [0.0, 1.0],
            [-stiffness / mass, -damping / mass],
        ]),
    )

    omega0 = np.sqrt(stiffness / mass)
    zeta = damping / (2.0 * np.sqrt(mass * stiffness))
    # Where the transient has to start, once the steady state has claimed its
    # share of the initial position and velocity.
    x0 = initial_position - steady * np.cos(phase)
    v0 = initial_velocity - steady * omega * np.sin(phase)

    def exact(t):
        t = np.asarray(t, dtype=float)
        decay = np.exp(-zeta * omega0 * t)
        if zeta < 1.0:                                   # under-damped
            wd = omega0 * np.sqrt(1.0 - zeta**2)
            a = x0
            b = (v0 + zeta * omega0 * x0) / wd
            shape = a * np.cos(wd * t) + b * np.sin(wd * t)
            x = decay * shape
            v = decay * (
                (-zeta * omega0) * shape
                + wd * (-a * np.sin(wd * t) + b * np.cos(wd * t))
            )
        elif np.isclose(zeta, 1.0):                      # critically damped
            a, b = x0, v0 + omega0 * x0
            x = decay * (a + b * t)
            v = decay * (b - omega0 * (a + b * t))
        else:                                            # over-damped
            root = omega0 * np.sqrt(zeta**2 - 1.0)
            r1, r2 = -zeta * omega0 + root, -zeta * omega0 - root
            b = (v0 - r1 * x0) / (r2 - r1)
            a = x0 - b
            x = a * np.exp(r1 * t) + b * np.exp(r2 * t)
            v = a * r1 * np.exp(r1 * t) + b * r2 * np.exp(r2 * t)

        x = x + steady * np.cos(omega * t - phase)
        v = v - steady * omega * np.sin(omega * t - phase)
        return np.stack([np.atleast_1d(x), np.atleast_1d(v)],
                        axis=0).reshape(2, -1).squeeze()

    return Benchmark(
        name="forced_spring",
        problem=prob,
        exact=exact,
        description=(
            "m x'' + c x' + k x = F cos(wt): a driven mass on a spring. The "
            "transient dies away and the steady state does not, so the long "
            "run depends on the forcing rather than on how it started. "
            "Sweeping the driving frequency past sqrt(k/m) passes through "
            "resonance."
        ),
        tags=("analytic", "linear", "second-order", "oscillator", "forced",
              "textbook", "2d"),
    )


TEXTBOOK = (
    mixing_tank,
    newton_cooling,
    rc_circuit,
    falling_with_drag,
    harvested_population,
    spring_mass_damper,
    forced_spring,
)

#: Non-stiff benchmarks for the work-precision diagrams.
NONSTIFF = (
    fitzhugh_nagumo,
    sir,
    exponential_decay,
    linear_system,
    sine_cosine,
    logistic,
    lotka_volterra,
    brusselator,
    lorenz,
    kepler,
    pleiades,
)

#: Stiff benchmarks, for the implicit methods.
STIFF = (robertson, hires, orego, lambda: van_der_pol(mu=1000.0))

#: Mass-matrix and differential-algebraic problems.
DAE = (mass_matrix_oscillator, linear_dae, robertson_dae)

#: Separable second-order systems, for the symplectic methods.
SEPARABLE = (harmonic_oscillator_2d, kepler_second_order)

#: Semilinear PDE discretisations, for the exponential integrators.
SEMILINEAR = (allen_cahn, kuramoto_sivashinsky)


def all_benchmarks() -> list[Benchmark]:
    """Instantiate every registered benchmark."""
    seen, out = set(), []
    for factory in (*NONSTIFF, *STIFF, *DAE, *TEXTBOOK, bouncing_ball):
        bench = factory()
        if bench.name not in seen:
            seen.add(bench.name)
            out.append(bench)
    return out
