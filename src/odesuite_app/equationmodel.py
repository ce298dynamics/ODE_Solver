"""Turning a typed equation into an ordinary catalogue entry.

The application is built around `CatalogEntry`: screens choose a problem by key,
`SessionState` holds the key, `SolveRunner` builds and solves it, and the plot,
the statistics panel and the step timeline all read the result. None of that
knows or cares where an entry came from.

So an equation the user types does not need a pipeline of its own -- it needs to
*become* a catalogue entry. That is what this module does, and the consequence is
disproportionate: the phase portrait, the stiffness sweep, the method race and
the accuracy study all start working on a hand-typed equation without a line of
change, because to them it is just another problem.

The pieces all exist already. `symbolic.to_first_order` reduces the equation to
an `ODEProblem` with an exact Jacobian; it labels the states and records whether
the right-hand side depends on time; and a symbolic parameter maps onto the same
`ParamSpec` the built-in problems use for their sliders.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .catalog import USER_KEY, CatalogEntry, ParamSpec
from .symbolic import EquationSpec, ParsedEquation, parse_equation, to_first_order

__all__ = [
    "UserBenchmark",
    "parameter_specs",
    "default_range",
    "build_entry",
    "entry_from_text",
]


@dataclass
class UserBenchmark:
    """What the entry's factory returns: a problem, plus its provenance.

    Shaped like the library's benchmark objects -- `SolveResult` only ever asks
    for `.problem`, and optionally `.invariant`, which a typed equation has no
    general way to supply.
    """

    problem: object
    spec: EquationSpec
    parsed: ParsedEquation
    #: The parameter values this instance was built at.
    values: dict[str, float] = field(default_factory=dict)

    # The library's benchmarks advertise what extras they carry, and the screens
    # ask before using them. A typed equation has none of them, but it has to
    # *say* so rather than simply lack the attribute: the accuracy study reads
    # `has_exact` unguarded to decide whether it needs a reference solve, and an
    # AttributeError there would look like a bug in the study rather than a
    # missing declaration here.
    #
    # `has_exact` is False even when the equation does have a closed form. The
    # attribute means "this benchmark can hand back an exact endpoint", and the
    # symbolic route deliberately does not feed the numeric one -- keeping them
    # independent is what makes their agreement worth anything.
    invariant = None
    has_exact = False

    def exact_at_end(self):
        raise NotImplementedError("a typed equation carries no reference solution")


def default_range(value: float) -> tuple[float, float]:
    """A slider range around a typed parameter value.

    Only a starting point -- the editor shows the bounds and lets them be
    changed, because a range guessed from one number is wrong about as often as
    it is right. The guess is deliberately plain: span zero to twice the value,
    keeping the sign, and fall back to a unit range when the value is zero.
    """
    if value == 0.0:
        return (-1.0, 1.0)
    low, high = sorted((0.0, 2.0 * float(value)))
    return (low, high)


def parameter_specs(spec: EquationSpec,
                    ranges: dict[str, tuple[float, float]] | None = None,
                    ) -> tuple[ParamSpec, ...]:
    """One `ParamSpec` per symbolic parameter, so the sliders come for free."""
    ranges = ranges or {}
    out = []
    for name, value in spec.parameters.items():
        low, high = ranges.get(name) or default_range(value)
        # A default outside its own range would leave the slider pinned to an
        # end stop and silently reporting a value the equation was not built at.
        low, high = min(low, value), max(high, value)
        if low == high:
            low, high = low - 1.0, high + 1.0
        out.append(
            ParamSpec(name=name, label=name, low=float(low), high=float(high),
                      default=float(value), hint=f"parameter {name}")
        )
    return tuple(out)


def _code_text(spec: EquationSpec) -> str:
    """A runnable snippet reproducing this equation.

    The built-in entries render a call into `odesuite.problems`; a typed
    equation has no such function, so it reproduces itself through the parser
    instead. Getting this wrong is not cosmetic -- "copy as code" is supposed to
    hand back something that runs.
    """
    def render(values: dict) -> str:
        parameters = {**spec.parameters, **{
            k: v for k, v in values.items() if k in spec.parameters
        }}
        span = spec.t_span
        if "t_end" in values:
            span = (span[0], float(values["t_end"]))
        lines = [
            "from odesuite import solve",
            "from odesuite_app.symbolic import (EquationSpec, parse_equation,",
            "                                   solve_symbolically, to_first_order)",
            "",
            "spec = EquationSpec(",
            f"    equations={spec.equations!r},",
            f"    initial_conditions={spec.initial_conditions!r},",
            f"    variables={spec.variables!r},",
        ]
        if parameters:
            lines.append(f"    parameters={parameters!r},")
        lines += [
            f"    t_span=({span[0]!r}, {span[1]!r}),",
            ")",
            "parsed = parse_equation(spec)",
            "",
            "# the closed form, if the equation has one",
            "print(solve_symbolically(parsed).best)",
            "",
            "# and the numeric solution",
            "problem = to_first_order(parsed)",
            "sol = solve(problem, method='dopri5', rtol=1e-8, atol=1e-11,",
            "            dense_output=True)",
            "print(sol.stats)",
        ]
        return "\n".join(lines)

    return render


def build_entry(parsed: ParsedEquation,
                ranges: dict[str, tuple[float, float]] | None = None,
                *, title: str | None = None,
                method: str | None = None) -> CatalogEntry:
    """A `CatalogEntry` for an already-parsed equation."""
    spec = parsed.spec
    problem = to_first_order(parsed)          # once, to read its shape
    n = int(problem.y0.size)
    labels = tuple(getattr(problem, "state_labels", ()) or ())
    autonomous = bool(getattr(problem, "autonomous", False))

    def factory(**kwargs) -> UserBenchmark:
        values = {k: float(v) for k, v in kwargs.items()}
        span = spec.t_span
        if "t_end" in values:
            span = (span[0], values.pop("t_end"))
        built = to_first_order(parsed, params=values, t_span=span)
        return UserBenchmark(problem=built, spec=spec, parsed=parsed, values=values)

    params = parameter_specs(spec, ranges)
    # A duration slider is worth having whatever the equation is; the built-in
    # entries carry one too.
    start, end = spec.t_span
    reach = abs(end - start) or 1.0
    params = params + (
        ParamSpec("t_end", "duration", float(start + 0.05 * reach),
                  float(start + 5.0 * reach), float(end),
                  hint="how far to integrate"),
    )

    return CatalogEntry(
        key=USER_KEY,
        title=title or spec.name or "your equation",
        blurb=" ; ".join(spec.equations),
        tags=("user",),
        factory=factory,
        params=params,
        default_method=method or "dopri5",
        # Second order or a two-variable system reads naturally in the phase
        # plane; anything else is a time series.
        plot_kind="phase" if n == 2 else "time",
        labels=labels,
        # Only an autonomous planar system has a static vector field. This is
        # the gate the phase-portrait screen already filters on, so answering it
        # honestly is what stops a forced equation being drawn against a field
        # that does not apply to it.
        autonomous_2d=(n == 2 and autonomous),
        code_text=_code_text(spec),
        supports_taylor=False,
    )


def entry_from_text(spec: EquationSpec,
                    ranges: dict[str, tuple[float, float]] | None = None,
                    **kwargs) -> tuple[CatalogEntry, ParsedEquation]:
    """Parse `spec` and build its entry. Raises `ParseError` on bad input."""
    parsed = parse_equation(spec)
    return build_entry(parsed, ranges, **kwargs), parsed
