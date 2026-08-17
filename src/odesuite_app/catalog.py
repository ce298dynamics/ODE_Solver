"""The problem catalogue: what the app can solve, and how to present it.

Wraps the library's benchmark factories with the metadata a user interface
needs -- a title, a one-line explanation, which parameters are worth a slider
and over what range, which components to plot against which, and a sensible
default method.

Keeping this here rather than in `odesuite.problems` is deliberate: slider
ranges and blurbs are presentation concerns, and the library must stay usable
with no interface attached.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from odesuite import problems

__all__ = [
    "ParamSpec", "CatalogEntry", "CATALOG", "get", "keys", "all_tags", "filter_by",
    "USER_KEY", "register_user_equation", "user_entry", "clear_user_equation",
]


@dataclass(frozen=True)
class ParamSpec:
    """A parameter the user can sweep from the interface."""

    name: str
    label: str
    low: float
    high: float
    default: float
    #: Sweep on a logarithmic scale. Right for anything spanning decades --
    #: a linear slider for Van der Pol's mu would spend 99% of its travel in
    #: the non-stiff regime.
    log: bool = False
    #: Short note shown as a tooltip.
    hint: str = ""

    def clamp(self, value: float) -> float:
        return float(min(max(value, self.low), self.high))


@dataclass(frozen=True)
class CatalogEntry:
    """One problem, as the interface sees it."""

    key: str
    title: str
    blurb: str
    tags: tuple[str, ...]
    #: The `odesuite.problems` factory this entry wraps.
    factory: Callable[..., object]
    #: Maps the interface's parameters onto the factory's keyword arguments.
    #: They are not always the same: a slider reading "log₁₀ duration" has to
    #: become ``t_end=10**value``, and "eccentricity" becomes ``eccentricity``
    #: only by luck. Holding the mapping in one place means `build` and the
    #: generated code snippet can never disagree -- a divergence that would
    #: otherwise show up as a copy-paste button emitting code that does not run.
    arg_map: Callable[[dict], dict] = lambda p: dict(p)
    params: tuple[ParamSpec, ...] = ()
    default_method: str = "dopri5"
    #: "time" | "phase" | "orbit" | "nbody" | "spacetime"
    plot_kind: str = "time"
    #: Component indices for the phase plot.
    phase_axes: tuple[int, int] = (0, 1)
    #: Component names, for legends and axis labels.
    labels: tuple[str, ...] = ()
    #: Suggested tolerance, overriding the global default.
    default_rtol: float = 1e-8
    #: Show the time axis logarithmically by default.
    #:
    #: Declared rather than inferred. The tempting heuristic -- compare t_end
    #: to the smallest positive output time -- flags almost every problem,
    #: because the first accepted step is always tiny. Whether a solution is
    #: *interesting* across decades is a property of the problem, so it is
    #: recorded here alongside the other presentation choices.
    log_time_default: bool = False
    #: Whether the problem supports a live phase-portrait vector field
    #: (needs a 2-component autonomous system).
    autonomous_2d: bool = False
    #: Overrides `code` for entries whose `factory` is not a named function in
    #: `odesuite.problems` -- currently the user's typed equation, whose factory
    #: is a closure. Without this, `code` would emit a call to a function that
    #: does not exist, and "copy as code" would hand back a snippet that cannot
    #: run. That exact failure has happened here once already.
    code_text: Callable[[dict], str] | None = None
    #: Whether the Taylor method may be offered. Two independent requirements,
    #: both verified rather than assumed:
    #:
    #: * The right-hand side must be expressible in jet arithmetic. Pleiades
    #:   fails (its ``(dx²+dy²)^1.5`` has zero entries, and a non-integer jet
    #:   power needs a positive constant term); the spectral problems fail
    #:   (FFTs); the separable Kepler form fails (object-array division).
    #: * The problem must not be stiff. Taylor is explicit in character, so on
    #:   Robertson, HIRES or OREGO it is stability-bound and simply stalls.
    supports_taylor: bool = False

    def defaults(self) -> dict:
        return {p.name: p.default for p in self.params}

    def build(self, params: dict):
        """Instantiate the benchmark for these interface parameters."""
        return self.factory(**self.arg_map({**self.defaults(), **params}))

    def code(self, params: dict) -> str:
        """The call that reproduces `build(params)`."""
        merged = {**self.defaults(), **params}
        if self.code_text is not None:
            return self.code_text(merged)
        arguments = self.arg_map(merged)
        rendered = ", ".join(f"{k}={v!r}" for k, v in arguments.items())
        return f"problems.{self.factory.__name__}({rendered})"

    @property
    def is_stiff(self) -> bool:
        return "stiff" in self.tags


def _entry(**kwargs) -> CatalogEntry:
    return CatalogEntry(**kwargs)


# ---------------------------------------------------------------------------
# Non-stiff classics
# ---------------------------------------------------------------------------

_ENTRIES: list[CatalogEntry] = [
    _entry(
        key="lotka_volterra",
        title="Lotka–Volterra",
        blurb="Predator and prey chasing each other around a closed orbit. "
              "Periodic, nonlinear, and it conserves a first integral.",
        tags=("nonstiff", "periodic", "2d", "classic"),
        factory=problems.lotka_volterra,
        params=(
            ParamSpec("a", "prey growth a", 0.2, 4.0, 1.5),
            ParamSpec("b", "predation b", 0.2, 3.0, 1.0),
            ParamSpec("c", "predator death c", 0.5, 6.0, 3.0),
            ParamSpec("d", "conversion d", 0.2, 3.0, 1.0),
            ParamSpec("t_end", "duration", 5.0, 60.0, 15.0),
        ),
        plot_kind="phase",
        labels=("prey", "predator"),
        autonomous_2d=True,
        supports_taylor=True,
    ),
    _entry(
        key="van_der_pol",
        title="Van der Pol",
        blurb="A relaxation oscillator whose stiffness you control directly. "
              "At μ=1 it is gentle; at μ=1000 no explicit method survives.",
        tags=("nonstiff", "stiff", "oscillator", "2d", "classic"),
        factory=problems.van_der_pol,
        params=(
            ParamSpec("mu", "stiffness μ", 0.1, 1000.0, 1.0, log=True,
                      hint="Above ~10 the problem becomes stiff"),
            ParamSpec("t_end", "duration", 5.0, 200.0, 20.0),
        ),
        plot_kind="phase",
        labels=("y", "y'"),
        autonomous_2d=True,
        supports_taylor=True,
    ),
    _entry(
        key="brusselator",
        title="Brusselator",
        blurb="An autocatalytic reaction that settles onto a limit cycle. "
              "Crossing b = 1 + a² triggers a Hopf bifurcation.",
        tags=("nonstiff", "oscillator", "2d", "chemistry"),
        factory=problems.brusselator,
        params=(
            ParamSpec("a", "a", 0.3, 3.0, 1.0),
            ParamSpec("b", "b", 0.5, 6.0, 3.0,
                      hint="Limit cycle appears once b > 1 + a²"),
            ParamSpec("t_end", "duration", 5.0, 80.0, 20.0),
        ),
        plot_kind="phase",
        labels=("x", "y"),
        autonomous_2d=True,
        supports_taylor=True,
    ),
    _entry(
        key="pendulum",
        title="Pendulum",
        blurb="The textbook phase portrait: centres, saddles, and the "
              "separatrices dividing swinging from rotating.",
        tags=("nonstiff", "oscillator", "2d", "classic"),
        factory=problems.pendulum,
        params=(
            ParamSpec("damping", "damping b", 0.0, 2.0, 0.0,
                      hint="Zero is Hamiltonian; damping turns centres into spirals"),
            ParamSpec("t_end", "duration", 5.0, 80.0, 20.0),
        ),
        plot_kind="phase",
        labels=("θ", "ω"),
        autonomous_2d=True,
        supports_taylor=True,
    ),
    _entry(
        key="duffing",
        title="Duffing oscillator",
        blurb="A double-well potential with a saddle between the wells. "
              "Raising α through zero collapses all three into one.",
        tags=("nonstiff", "oscillator", "2d", "classic"),
        factory=problems.duffing,
        params=(
            ParamSpec("alpha", "stiffness α", -2.0, 2.0, -1.0,
                      hint="Pitchfork bifurcation as α crosses zero"),
            ParamSpec("beta", "nonlinearity β", 0.1, 3.0, 1.0),
            ParamSpec("delta", "damping δ", 0.0, 1.0, 0.2),
            ParamSpec("t_end", "duration", 5.0, 80.0, 30.0),
        ),
        plot_kind="phase",
        labels=("x", "v"),
        autonomous_2d=True,
        supports_taylor=True,
    ),
    _entry(
        key="lorenz",
        title="Lorenz attractor",
        blurb="The butterfly. Deterministic but chaotic — two trajectories a "
              "hair apart diverge exponentially.",
        tags=("nonstiff", "chaotic", "3d", "classic"),
        factory=problems.lorenz,
        params=(
            ParamSpec("sigma", "σ", 1.0, 20.0, 10.0),
            ParamSpec("rho", "ρ", 0.5, 60.0, 28.0,
                      hint="Chaos sets in around ρ ≈ 24.7"),
            ParamSpec("beta", "β", 0.5, 5.0, 8.0 / 3.0),
            ParamSpec("t_end", "duration", 5.0, 120.0, 40.0),
        ),
        plot_kind="orbit",
        phase_axes=(0, 2),
        labels=("x", "y", "z"),
        supports_taylor=True,
    ),
    _entry(
        key="kepler",
        title="Kepler orbit",
        blurb="Two-body motion in a plane. Energy and angular momentum are "
              "conserved exactly — so any drift is the integrator's fault.",
        tags=("nonstiff", "hamiltonian", "2d", "classic"),
        factory=problems.kepler,
        arg_map=lambda p: {"eccentricity": p["e"], "n_orbits": p["n_orbits"]},
        params=(
            ParamSpec("e", "eccentricity", 0.0, 0.9, 0.6,
                      hint="Higher eccentricity means a sharper perihelion pass"),
            ParamSpec("n_orbits", "orbits", 0.5, 60.0, 3.0),
        ),
        plot_kind="orbit",
        labels=("x", "y", "vx", "vy"),
        default_rtol=1e-9,
        supports_taylor=True,
    ),
    _entry(
        key="pleiades",
        title="Pleiades (7-body)",
        blurb="Seven gravitating bodies, 28 equations, several near-collisions "
              "that force the step size down hard.",
        tags=("nonstiff", "nbody", "classic"),
        factory=problems.pleiades,
        params=(ParamSpec("t_end", "duration", 0.5, 5.0, 3.0),),
        plot_kind="nbody",
        default_rtol=1e-9,
    ),
    _entry(
        key="logistic",
        title="Logistic growth",
        blurb="The simplest interesting nonlinear ODE, and one of the few with "
              "a closed-form solution to check against.",
        tags=("nonstiff", "analytic", "1d"),
        factory=problems.logistic,
        params=(
            ParamSpec("r", "growth rate r", 0.1, 5.0, 1.2),
            ParamSpec("y0", "initial y", 0.01, 0.9, 0.1),
            ParamSpec("t_end", "duration", 2.0, 30.0, 8.0),
        ),
        labels=("y",),
        supports_taylor=True,
    ),
    _entry(
        key="sine_cosine",
        title="Harmonic oscillator",
        blurb="y'' = −y, whose exact solution is (sin t, cos t). The reference "
              "problem for order verification.",
        tags=("nonstiff", "analytic", "2d", "hamiltonian"),
        factory=problems.sine_cosine,
        params=(ParamSpec("t_end", "duration", 2.0, 60.0, 6.0),),
        plot_kind="phase",
        labels=("sin", "cos"),
        autonomous_2d=True,
        supports_taylor=True,
    ),
]

# ---------------------------------------------------------------------------
# Stiff problems
# ---------------------------------------------------------------------------

_ENTRIES += [
    _entry(
        key="robertson",
        title="Robertson kinetics",
        blurb="The canonical stiff problem. Rate constants spanning seven "
              "decades, integrated over eleven decades of time.",
        tags=("stiff", "chemistry", "classic"),
        factory=problems.robertson,
        arg_map=lambda p: {"t_end": 10.0 ** p["log_t_end"]},
        params=(
            ParamSpec("log_t_end", "log₁₀ duration", 1.0, 11.0, 11.0,
                      hint="Explicit methods stall around t = 50"),
        ),
        default_method="radau",
        default_rtol=1e-6,
        labels=("A", "B", "C"),
        log_time_default=True,
    ),
    _entry(
        key="hires",
        title="HIRES",
        blurb="Eight-equation plant-physiology model from the Bari stiff test "
              "set. A full Jacobian, so it exercises the linear algebra.",
        tags=("stiff", "biology"),
        factory=problems.hires,
        params=(ParamSpec("t_end", "duration", 10.0, 400.0, 321.8122),),
        default_method="radau",
        default_rtol=1e-7,
    ),
    _entry(
        key="orego",
        title="Oregonator",
        blurb="The Belousov–Zhabotinsky reaction: stiff and violently "
              "oscillatory, with concentrations swinging over many decades.",
        tags=("stiff", "oscillator", "chemistry"),
        factory=problems.orego,
        params=(ParamSpec("t_end", "duration", 30.0, 500.0, 360.0),),
        default_method="radau",
        default_rtol=1e-6,
        labels=("x", "y", "z"),
    ),
]

# ---------------------------------------------------------------------------
# Mass matrices and DAEs
# ---------------------------------------------------------------------------

_ENTRIES += [
    _entry(
        key="robertson_dae",
        title="Robertson (DAE form)",
        blurb="Robertson with the conservation law substituted for the third "
              "rate equation. Mass is then conserved structurally, to round-off.",
        tags=("stiff", "dae", "chemistry"),
        factory=problems.robertson_dae,
        arg_map=lambda p: {"t_end": 10.0 ** p["log_t_end"]},
        params=(ParamSpec("log_t_end", "log₁₀ duration", 1.0, 11.0, 11.0),),
        default_method="radau",
        default_rtol=1e-6,
        labels=("A", "B", "C"),
        log_time_default=True,
    ),
    _entry(
        key="linear_dae",
        title="Index-1 DAE",
        blurb="A semi-explicit DAE with a closed-form solution: one "
              "differential equation, one algebraic constraint.",
        tags=("dae", "analytic"),
        factory=problems.linear_dae,
        params=(ParamSpec("t_end", "duration", 1.0, 12.0, 3.0),),
        default_method="radau",
        labels=("y₁ (differential)", "y₂ (algebraic)"),
    ),
    _entry(
        key="mass_matrix_oscillator",
        title="Mass-matrix system",
        blurb="M y' = A y with a non-diagonal, non-singular mass matrix — an "
              "ODE in disguise, and a check on the mass-matrix path.",
        tags=("mass", "analytic", "2d"),
        factory=problems.mass_matrix_oscillator,
        params=(ParamSpec("t_end", "duration", 1.0, 20.0, 3.0),),
        default_method="radau",
        plot_kind="phase",
    ),
]

# ---------------------------------------------------------------------------
# Separable Hamiltonian systems, for the symplectic methods
# ---------------------------------------------------------------------------

_ENTRIES += [
    _entry(
        key="kepler_symplectic",
        title="Kepler (separable)",
        blurb="The same orbit written as q'' = a(q), so symplectic integrators "
              "can split the flow. Watch energy stay bounded forever.",
        tags=("hamiltonian", "separable", "2d", "classic"),
        factory=problems.kepler_second_order,
        arg_map=lambda p: {"eccentricity": p["e"], "n_orbits": p["n_orbits"]},
        params=(
            ParamSpec("e", "eccentricity", 0.0, 0.9, 0.3),
            ParamSpec("n_orbits", "orbits", 1.0, 2000.0, 50.0, log=True),
        ),
        default_method="verlet",
        plot_kind="orbit",
        labels=("x", "y", "vx", "vy"),
    ),
    _entry(
        key="harmonic_2d",
        title="2-D oscillator (separable)",
        blurb="q'' = −q in the plane. Separable, analytic, and the reference "
              "problem for symplectic order checks.",
        tags=("hamiltonian", "separable", "analytic", "2d"),
        factory=problems.harmonic_oscillator_2d,
        params=(ParamSpec("t_end", "duration", 4.0, 200.0, 20.0),),
        default_method="verlet",
        plot_kind="orbit",
        labels=("x", "y", "vx", "vy"),
        supports_taylor=True,
    ),
]

# ---------------------------------------------------------------------------
# Semilinear PDE discretisations, for the exponential integrator
# ---------------------------------------------------------------------------

_ENTRIES += [
    _entry(
        key="kuramoto_sivashinsky",
        title="Kuramoto–Sivashinsky",
        blurb="A chaotic flame front, spectrally discretised. Enormously stiff "
              "in its linear part — ETDRK4's home ground.",
        tags=("pde", "semilinear", "stiff", "chaotic"),
        factory=problems.kuramoto_sivashinsky,
        arg_map=lambda p: {"n_modes": int(p["n_modes"]), "t_end": p["t_end"]},
        params=(
            ParamSpec("n_modes", "Fourier modes", 64, 256, 128,
                      hint="Stiffness grows like the fourth power of this"),
            ParamSpec("t_end", "duration", 20.0, 200.0, 100.0),
        ),
        default_method="etdrk4",
        plot_kind="spacetime",
    ),
    _entry(
        key="allen_cahn",
        title="Allen–Cahn",
        blurb="Reaction-diffusion phase separation. Semilinear and real-valued, "
              "so it can be checked against an explicit reference.",
        tags=("pde", "semilinear", "stiff"),
        factory=problems.allen_cahn,
        arg_map=lambda p: {
            "n_modes": int(p["n_modes"]), "epsilon": p["epsilon"],
            "t_end": p["t_end"],
        },
        params=(
            ParamSpec("n_modes", "Fourier modes", 32, 256, 128),
            ParamSpec("epsilon", "diffusion ε", 0.001, 0.2, 0.01, log=True),
            ParamSpec("t_end", "duration", 5.0, 80.0, 30.0),
        ),
        default_method="etdrk4",
        plot_kind="spacetime",
    ),
]

# ---------------------------------------------------------------------------
# Event-driven
# ---------------------------------------------------------------------------

_ENTRIES += [
    _entry(
        key="bouncing_ball",
        title="Bouncing ball",
        blurb="Free fall with a terminal event at the ground. The impact time "
              "is known exactly, so event location can be graded.",
        tags=("events", "analytic", "2d"),
        factory=problems.bouncing_ball,
        arg_map=lambda p: {"h0": p["h0"], "g": p["g"], "t_end": 10.0},
        params=(
            ParamSpec("h0", "drop height", 0.2, 20.0, 1.0),
            ParamSpec("g", "gravity", 1.0, 25.0, 9.81),
        ),
        plot_kind="phase",
        labels=("height", "velocity"),
        supports_taylor=True,
    ),
]


CATALOG: dict[str, CatalogEntry] = {e.key: e for e in _ENTRIES}


# ---------------------------------------------------------------------------
# The user's own equation, as a catalogue entry
# ---------------------------------------------------------------------------
#
# An equation typed in the Solver Lab is registered here as an ordinary
# `CatalogEntry`, which is what lets it reach the rest of the application: every
# screen selects a problem by key and everything downstream -- `SessionState`,
# `SolveRunner`, the plot, the stats -- speaks `CatalogEntry`. Registering one
# is therefore cheaper and far less error-prone than a parallel pipeline for
# user input, and the phase portrait, the method race and the stiffness sweep
# all start working on a typed equation without knowing it exists.
#
# It is held apart from `CATALOG` rather than inserted into it, because the two
# are not interchangeable in every context: the home gallery, the thumbnail
# cache and `--list-problems` enumerate the *fixed* problem set, and a transient
# entry appearing there would be wrong (and, for thumbnails, would be written to
# disk under a key that means something different next session).

#: Reserved key for the user's equation. Not a valid Python identifier prefix
#: anywhere else in the catalogue, so it cannot collide with a real problem.
USER_KEY = "__user__"

_USER: CatalogEntry | None = None


def register_user_equation(entry: CatalogEntry) -> CatalogEntry:
    """Install `entry` as the current user equation, replacing any previous one."""
    global _USER
    if entry.key != USER_KEY:
        raise ValueError(f"a user entry must use the key {USER_KEY!r}")
    _USER = entry
    return entry


def user_entry() -> CatalogEntry | None:
    """The registered user equation, or ``None`` if nothing has been typed."""
    return _USER


def clear_user_equation() -> None:
    global _USER
    _USER = None


def keys(include_user: bool = False) -> list[str]:
    """The catalogue's problem keys.

    The user equation is excluded unless asked for, so callers that mean "the
    problems this application ships with" -- the home gallery, the thumbnail
    renderer, `--list-problems` -- get exactly that by default.
    """
    names = list(CATALOG)
    if include_user and _USER is not None:
        names.append(USER_KEY)
    return names


def get(key: str) -> CatalogEntry:
    if key == USER_KEY and _USER is not None:
        return _USER
    if key not in CATALOG:
        raise KeyError(f"unknown problem {key!r}; have {', '.join(CATALOG)}")
    return CATALOG[key]


def all_tags() -> list[str]:
    """Tags in a stable, roughly most-useful-first order."""
    preferred = [
        "classic", "nonstiff", "stiff", "chaotic", "hamiltonian",
        "dae", "pde", "events", "analytic", "oscillator",
    ]
    present = {tag for entry in CATALOG.values() for tag in entry.tags}
    ordered = [t for t in preferred if t in present]
    return ordered + sorted(present - set(ordered))


def filter_by(tag: str | None) -> list[CatalogEntry]:
    entries = list(CATALOG.values())
    if not tag or tag == "all":
        return entries
    return [e for e in entries if tag in e.tags]


def preview_curves(entry: CatalogEntry, solution) -> list[tuple[np.ndarray, np.ndarray]]:
    """The (x, y) curves that represent this problem visually.

    Used by both the home-screen thumbnails and the main plot, so a problem
    looks the same everywhere it appears.
    """
    t, y = solution.t, solution.y
    kind = entry.plot_kind

    if kind in ("phase", "orbit") and y.shape[0] > max(entry.phase_axes):
        i, j = entry.phase_axes
        return [(y[i], y[j])]
    if kind == "nbody":
        # Pleiades: seven bodies, positions stacked as x[0:7], y[7:14].
        return [(y[k], y[k + 7]) for k in range(7)]
    if kind == "spacetime":
        return []
    return [(t, y[i]) for i in range(min(y.shape[0], 6))]
