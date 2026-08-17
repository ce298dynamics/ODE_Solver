"""Build an `ODEProblem` from equations typed as text.

Turns the application from a demonstration into a tool. The user writes a
right-hand side; sympy parses it, **differentiates it symbolically** to get an
exact Jacobian, and lambdifies both. Every method in the library then works on
it -- including the implicit ones, which without a Jacobian would be reduced to
finite differences.

Parsing is deliberately restricted, and the restriction is not the obvious one.
`sympy.sympify` **evaluates** its input with the ordinary Python builtins in
scope: its ``locals`` argument adds names, it does not remove any, so
``sympify('__import__("os").system(...)')` runs the command. Expressions here
go through `parse_expr` with an explicit ``global_dict`` whose ``__builtins__``
is emptied -- and emptied deliberately, because an absent ``__builtins__`` key
makes Python reinstate the real one. Only the declared variables, the declared
parameters and a whitelist of elementary functions remain reachable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    parse_expr,
    standard_transformations,
)

from odesuite import ODEProblem

__all__ = ["CustomSpec", "ParseError", "ALLOWED_FUNCTIONS", "build", "EXAMPLES"]


class ParseError(ValueError):
    """Raised with a message meant to be shown to the user."""


#: The only names an expression may use, beyond the declared variables,
#: parameters and `t`.
ALLOWED_FUNCTIONS: dict[str, object] = {
    name: getattr(sp, name)
    for name in (
        "sin", "cos", "tan", "asin", "acos", "atan", "atan2",
        "sinh", "cosh", "tanh", "exp", "log", "sqrt", "Abs",
        "sign", "Min", "Max", "erf", "floor", "ceiling",
    )
}
ALLOWED_FUNCTIONS.update({"pi": sp.pi, "E": sp.E, "abs": sp.Abs})

_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

_TRANSFORMATIONS = standard_transformations + (convert_xor,)

#: The globals `parse_expr` compiles against. ``__builtins__`` is set to an
#: empty mapping rather than omitted: leaving it out causes Python to insert
#: the real builtins, which is exactly the hole this is meant to close. The
#: numeric constructors are required by the standard transformations.
_SAFE_GLOBALS: dict[str, object] = {
    "__builtins__": {},
    "Symbol": sp.Symbol,
    "Integer": sp.Integer,
    "Float": sp.Float,
    "Rational": sp.Rational,
    **ALLOWED_FUNCTIONS,
}


@dataclass
class CustomSpec:
    """A user-defined system, as typed."""

    variables: list[str]
    expressions: list[str]
    initial: list[float]
    parameters: dict[str, float] = field(default_factory=dict)
    t_span: tuple[float, float] = (0.0, 20.0)
    name: str = "custom system"

    def validate(self) -> None:
        if not self.variables:
            raise ParseError("declare at least one variable")
        if len(self.variables) != len(self.expressions):
            raise ParseError(
                f"{len(self.variables)} variables but "
                f"{len(self.expressions)} equations"
            )
        if len(self.initial) != len(self.variables):
            raise ParseError(
                f"{len(self.variables)} variables but "
                f"{len(self.initial)} initial values"
            )
        seen = set()
        for name in [*self.variables, *self.parameters]:
            if not _IDENTIFIER.match(name):
                raise ParseError(f"{name!r} is not a valid name")
            if name == "t":
                raise ParseError("'t' is reserved for the independent variable")
            if name in ALLOWED_FUNCTIONS:
                raise ParseError(f"{name!r} shadows a built-in function")
            if name in seen:
                raise ParseError(f"{name!r} is declared twice")
            seen.add(name)
        if self.t_span[0] == self.t_span[1]:
            raise ParseError("the time span must be non-empty")


@dataclass
class CustomSystem:
    """A parsed system: callables, the symbolic Jacobian, and its source text."""

    spec: CustomSpec
    problem: ODEProblem
    jacobian_source: list[list[str]]
    expressions: list[sp.Expr]

    @property
    def jacobian_text(self) -> str:
        """The symbolic Jacobian, formatted for display.

        Worth surfacing: it is the part the user did not have to write, and
        seeing it derived is the clearest evidence that the implicit methods
        are getting an exact derivative rather than a difference quotient.
        """
        width = max(
            (len(entry) for row in self.jacobian_source for entry in row),
            default=1,
        )
        return "\n".join(
            "  ".join(entry.rjust(width) for entry in row)
            for row in self.jacobian_source
        )


def _parse(text: str, symbols: dict[str, sp.Symbol]) -> sp.Expr:
    """Parse one expression against the whitelist."""
    if not text or not text.strip():
        raise ParseError("empty expression")
    local = {**symbols, **ALLOWED_FUNCTIONS}
    try:
        expression = parse_expr(
            text,
            local_dict=local,
            global_dict=dict(_SAFE_GLOBALS),
            transformations=_TRANSFORMATIONS,
            evaluate=True,
        )
        # A bare constant parses to a plain number on some paths; sympify it so
        # the free-symbol check below always has a sympy object to work with.
        # Inside the try, because a rejected expression can leave something
        # here that sympify itself refuses.
        expression = sp.sympify(expression)
    except Exception as exc:
        raise ParseError(f"cannot parse {text!r}: {exc}") from exc

    if not isinstance(expression, sp.Basic):
        raise ParseError(f"{text!r} is not a mathematical expression")

    unknown = {
        symbol.name for symbol in expression.free_symbols
        if symbol.name not in local
    }
    if unknown:
        raise ParseError(
            f"unknown name{'s' if len(unknown) > 1 else ''} in {text!r}: "
            f"{', '.join(sorted(unknown))}"
        )
    return expression


def build(spec: CustomSpec) -> CustomSystem:
    """Parse `spec` into an `ODEProblem` with an exact symbolic Jacobian."""
    spec.validate()

    # Real symbols, not the sympy default of complex. It matters for
    # differentiation: with a complex symbol, d|x|/dx comes back in terms of
    # re(x) and im(x), which then fails to lambdify -- so `abs()` in a
    # right-hand side would break with an obscure printer error rather than
    # simply working.
    t = sp.Symbol("t", real=True)
    variables = [sp.Symbol(name, real=True) for name in spec.variables]
    parameters = {name: sp.Symbol(name, real=True) for name in spec.parameters}
    scope = {"t": t, **dict(zip(spec.variables, variables)), **parameters}

    expressions = [_parse(text, scope) for text in spec.expressions]
    try:
        jacobian = sp.Matrix(expressions).jacobian(variables)
    except Exception as exc:
        # Every failure in this function must surface as a ParseError with a
        # readable message; the caller is a text box, not a stack trace.
        raise ParseError(f"could not differentiate the system: {exc}") from exc

    arguments = [t, *variables, *parameters.values()]
    values = [float(spec.parameters[name]) for name in parameters]

    try:
        f_compiled = sp.lambdify(arguments, expressions, "numpy")
        jac_compiled = sp.lambdify(arguments, jacobian, "numpy")
    except Exception as exc:
        raise ParseError(
            f"could not compile the system: {exc}. Functions without a "
            f"continuous derivative (floor, ceiling) cannot be used in a "
            f"right-hand side."
        ) from exc

    n = len(variables)

    def f(time, state):
        result = f_compiled(time, *state, *values)
        try:
            return np.asarray(result, dtype=float).reshape(n)
        except (TypeError, ValueError):
            # The Taylor method evaluates the right-hand side on `Jet` objects
            # rather than numbers. The lambdified code copes -- Jet overloads
            # the arithmetic and the numpy ufuncs -- but forcing a float dtype
            # afterwards would throw the result away.
            out = np.empty(n, dtype=object)
            for index in range(n):
                out[index] = result[index]
            return out

    def jac(time, state):
        return np.asarray(
            jac_compiled(time, *state, *values), dtype=float
        ).reshape(n, n)

    initial = np.asarray(spec.initial, dtype=float)
    try:
        problem = ODEProblem(f=f, t_span=spec.t_span, y0=initial, jac=jac)
    except Exception as exc:
        raise ParseError(f"the system does not evaluate: {exc}") from exc

    # A Jacobian that disagrees with the right-hand side is worse than none,
    # so it is checked against a difference quotient once at build time.
    try:
        _verify_jacobian(problem, initial)
    except ParseError:
        raise
    except Exception as exc:
        raise ParseError(f"the Jacobian does not evaluate: {exc}") from exc

    return CustomSystem(
        spec=spec,
        problem=problem,
        jacobian_source=[[sp.sstr(entry) for entry in row] for row in jacobian.tolist()],
        expressions=expressions,
    )


def _verify_jacobian(problem: ODEProblem, state: np.ndarray) -> None:
    """Check the symbolic Jacobian against central differences at one point."""
    from odesuite.linalg import EPS

    exact = problem.jac(problem.t0, state)
    step = np.cbrt(EPS) * np.maximum(np.abs(state), 1.0)
    approx = np.empty_like(exact)
    for index in range(state.size):
        plus, minus = state.copy(), state.copy()
        plus[index] += step[index]
        minus[index] -= step[index]
        approx[:, index] = (
            problem.f(problem.t0, plus) - problem.f(problem.t0, minus)
        ) / (2 * step[index])

    scale = np.maximum(np.abs(exact), 1.0)
    if not np.all(np.abs(exact - approx) / scale < 1e-4):
        raise ParseError(
            "the symbolic Jacobian disagrees with the right-hand side; this "
            "usually means the expression uses a non-differentiable function "
            "such as abs() or sign()"
        )


#: Ready-made systems for the editor, chosen to show different features.
EXAMPLES: dict[str, CustomSpec] = {
    "Van der Pol": CustomSpec(
        variables=["x", "v"],
        expressions=["v", "mu*(1 - x**2)*v - x"],
        initial=[2.0, 0.0],
        parameters={"mu": 3.0},
        t_span=(0.0, 30.0),
        name="Van der Pol",
    ),
    "Damped pendulum": CustomSpec(
        variables=["theta", "omega"],
        expressions=["omega", "-sin(theta) - b*omega"],
        initial=[2.5, 0.0],
        parameters={"b": 0.2},
        t_span=(0.0, 40.0),
        name="Damped pendulum",
    ),
    "Rössler attractor": CustomSpec(
        variables=["x", "y", "z"],
        expressions=["-y - z", "x + a*y", "b + z*(x - c)"],
        initial=[1.0, 1.0, 1.0],
        parameters={"a": 0.2, "b": 0.2, "c": 5.7},
        t_span=(0.0, 200.0),
        name="Rössler attractor",
    ),
    "SIR epidemic": CustomSpec(
        variables=["S", "I", "R"],
        expressions=["-beta*S*I", "beta*S*I - gamma*I", "gamma*I"],
        initial=[0.99, 0.01, 0.0],
        parameters={"beta": 0.9, "gamma": 0.2},
        t_span=(0.0, 80.0),
        name="SIR epidemic",
    ),
    "Stiff decay": CustomSpec(
        variables=["u", "w"],
        expressions=["-k*u + w", "-w"],
        initial=[1.0, 1.0],
        parameters={"k": 1000.0},
        t_span=(0.0, 5.0),
        name="Stiff decay",
    ),
}
