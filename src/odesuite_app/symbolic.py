"""Closed-form solutions for differential equations that have them.

Given ``y'' + 3y' + 2y = sin(t)`` this returns the general solution, the
particular solution for initial conditions, the characteristic polynomial and
its roots, the fundamental solution set each root contributes -- and a
*verification* that the answer satisfies the equation, obtained by substituting
it back and simplifying to zero. It also reduces the equation to a first-order
system so every numeric method in the library applies to the same input.

Three things about `sympy.dsolve` shape this module, all of them measured rather
than assumed:

**It hangs.** Not "is slow" -- ``y' = sin(y)`` and the pendulum never return.
A thread cannot be killed, so `dsolve` runs in a **subprocess** under a hard
timeout. Everything else here is fast: every hand-solvable family probed came
back in under a second.

**It succeeds far more often than expected.** Constant-coefficient equations of
any order, resonant forcing, Cauchy-Euler, integrating factors, separable,
Bernoulli, and Airy functions all come out.

**Its answers can be checked exactly.** Substituting the solution into the
equation and simplifying yields precisely ``0``, so the module never has to
present an unverified result as though it were certain.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, replace

import numpy as np
import sympy as sp

from odesuite import ODEProblem

from .custom import ALLOWED_FUNCTIONS, ParseError, _SAFE_GLOBALS, _TRANSFORMATIONS

__all__ = [
    "EquationSpec",
    "SymbolicSolution",
    "ParsedEquation",
    "parse_equation",
    "parse_initial_conditions",
    "solve_symbolically",
    "characteristic_analysis",
    "describe_roots",
    "with_parameters",
    "to_first_order",
    "EXAMPLES",
    "DSOLVE_TIMEOUT",
]

#: Seconds before a `dsolve` subprocess is killed. Generous next to the sub-second
#: cost of everything solvable, and finite unlike `y' = sin(y)`.
DSOLVE_TIMEOUT = 12.0

_T = sp.Symbol("t", real=True)

def _token(name: str, order: int) -> str:
    """Placeholder standing in for the `order`-th derivative of `name`.

    Three properties, each of which was a bug before it was one:

    * It **names the variable**. A shared token makes ``x`` and ``y`` in a
      system rewrite to the same symbol, and the system silently collapses.
    * The **digit comes last**, so the implicit-multiplication rule -- which
      inserts ``*`` between a digit and a following letter -- cannot split the
      token in half.
    * The variable name is **surrounded by word characters**, so rewriting a
      later variable cannot match the name embedded in an earlier token.
    """
    return f"ODEDZ{name}Z{order}"


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------


@dataclass
class EquationSpec:
    """A differential equation as typed."""

    #: ``y'' + 3y' + 2y = sin(t)``, or several ``x' = ...`` lines for a system.
    equations: list[str]
    #: ``y(0)=1, y'(0)=0``; empty for the general solution.
    initial_conditions: str = ""
    #: Dependent variable names. For a scalar equation this is one name.
    variables: list[str] = field(default_factory=lambda: ["y"])
    parameters: dict[str, float] = field(default_factory=dict)
    t_span: tuple[float, float] = (0.0, 10.0)
    name: str = "equation"

    @property
    def is_system(self) -> bool:
        return len(self.equations) > 1


@dataclass
class ParsedEquation:
    """The parsed form: sympy objects plus what could be read off them."""

    spec: EquationSpec
    #: ``sp.Eq`` per equation, in terms of ``y(t)`` and its derivatives.
    equations: list[sp.Eq]
    functions: list[sp.Function]
    order: int
    is_system: bool
    ics: dict = field(default_factory=dict)

    @property
    def function(self) -> sp.Function:
        return self.functions[0]

    @property
    def equation(self) -> sp.Eq:
        return self.equations[0]


@dataclass
class SymbolicSolution:
    """Everything the symbolic route produced."""

    general: sp.Expr | list[sp.Expr] | None = None
    particular: sp.Expr | list[sp.Expr] | None = None
    classification: str = ""
    order: int = 0
    linear: bool = False
    homogeneous: bool = False
    constant_coefficients: bool = False
    #: ``(root, multiplicity)`` of the characteristic polynomial.
    roots: list[tuple[sp.Expr, int]] = field(default_factory=list)
    characteristic_poly: sp.Expr | None = None
    #: Basis functions the roots contribute, in the by-hand order.
    fundamental_set: list[sp.Expr] = field(default_factory=list)
    #: ``None`` when not attempted; ``True``/``False`` from substituting back.
    verified: bool | None = None
    residual: sp.Expr | None = None
    timed_out: bool = False
    message: str = ""

    @property
    def solved(self) -> bool:
        return self.general is not None or self.particular is not None

    @property
    def best(self):
        """The particular solution where there is one, else the general."""
        return self.particular if self.particular is not None else self.general


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _insert_multiplication(text: str) -> str:
    """Make ``3y'`` and ``2(t+1)`` explicit, which the parser needs.

    Only between a digit and an identifier or bracket, never between two
    identifiers -- ``sin t`` must stay an error rather than silently becoming
    ``sin*t``.
    """
    text = re.sub(r"(\d)\s*([A-Za-z_(])", r"\1*\2", text)
    text = re.sub(r"(\))\s*([A-Za-z_0-9(])", r"\1*\2", text)
    return text


def _rewrite_derivatives(text: str, name: str) -> tuple[str, int]:
    """Turn ``y''`` and ``y^(3)`` into placeholder symbols. Returns the order too."""
    highest = 0

    def superscript(match: re.Match) -> str:
        nonlocal highest
        order = int(match.group(1))
        highest = max(highest, order)
        return _token(name, order)

    # y^(4) before y'''' before bare y, so an earlier rewrite is never rescanned.
    text = re.sub(rf"\b{re.escape(name)}\s*\^\s*\(\s*(\d+)\s*\)", superscript, text)

    def primes(match: re.Match) -> str:
        nonlocal highest
        order = len(match.group(1))
        highest = max(highest, order)
        return _token(name, order)

    text = re.sub(rf"\b{re.escape(name)}((?:'|′)+)", primes, text)
    text = re.sub(rf"\b{re.escape(name)}\b", _token(name, 0), text)
    return text, highest


def _parse_side(text: str, scope: dict) -> sp.Expr:
    from sympy.parsing.sympy_parser import parse_expr

    try:
        expression = parse_expr(
            text,
            local_dict=scope,
            global_dict=dict(_SAFE_GLOBALS),
            transformations=_TRANSFORMATIONS,
            evaluate=True,
        )
        return sp.sympify(expression)
    except Exception as exc:
        raise ParseError(f"cannot parse {text!r}: {exc}") from exc


def parse_equation(spec: EquationSpec) -> ParsedEquation:
    """Parse `spec` into sympy equations in terms of ``y(t)``."""
    if not spec.equations or not any(e.strip() for e in spec.equations):
        raise ParseError("type an equation")
    for name in [*spec.variables, *spec.parameters]:
        if name == "t":
            raise ParseError("'t' is the independent variable")
        if name in ALLOWED_FUNCTIONS:
            raise ParseError(f"{name!r} shadows a built-in function")
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            raise ParseError(f"{name!r} is not a valid variable name")

    functions = [sp.Function(name) for name in spec.variables]
    parameters = {n: sp.Symbol(n, real=True) for n in spec.parameters}

    equations: list[sp.Eq] = []
    order = 0

    for index, raw in enumerate(spec.equations):
        text = raw.strip()
        if not text:
            continue
        text = text.replace("^", "**") if "^(" not in text else text
        if text.count("=") != 1:
            raise ParseError(
                f"{raw!r} must contain exactly one '=' (write the whole equation)"
            )
        left, right = text.split("=")

        scope: dict = {"t": _T, **parameters, **ALLOWED_FUNCTIONS}
        rewritten_sides = []
        equation_order = 0

        for side in (left, right):
            # Multiplication first, on the text the user actually wrote. Doing
            # it afterwards would run the digit-then-letter rule across the
            # placeholder tokens themselves.
            side_text = _insert_multiplication(side)
            for name in spec.variables:
                side_text, highest = _rewrite_derivatives(side_text, name)
                equation_order = max(equation_order, highest)
            rewritten_sides.append(side_text)

        # Placeholders become real derivatives after parsing, so the parser only
        # ever sees plain symbols.
        for name in spec.variables:
            for k in range(equation_order + 1):
                scope[_token(name, k)] = sp.Symbol(f"__{name}_{k}", real=True)

        parsed = [_parse_side(side, scope) for side in rewritten_sides]

        substitutions = {}
        for name, function in zip(spec.variables, functions):
            for k in range(equation_order + 1):
                placeholder = sp.Symbol(f"__{name}_{k}", real=True)
                substitutions[placeholder] = (
                    function(_T) if k == 0 else function(_T).diff(_T, k)
                )

        equation = sp.Eq(
            parsed[0].subs(substitutions), parsed[1].subs(substitutions)
        )
        _reject_leftovers(equation, spec)
        equations.append(equation)
        order = max(order, equation_order)

    if order == 0:
        raise ParseError(
            "no derivative found — write y' or y'' (or y^(3)) somewhere"
        )

    return ParsedEquation(
        spec=spec,
        equations=equations,
        functions=functions,
        order=order,
        is_system=len(equations) > 1,
        ics=parse_initial_conditions(spec, functions),
    )


def _reject_leftovers(equation: sp.Eq, spec: EquationSpec) -> None:
    """Any free symbol that is not `t` or a declared parameter is a typo."""
    allowed = {"t", *spec.parameters}
    unknown = {
        symbol.name
        for symbol in equation.free_symbols
        if symbol.name not in allowed and not symbol.name.startswith("__")
    }
    if unknown:
        raise ParseError(
            f"unknown name{'s' if len(unknown) > 1 else ''}: "
            f"{', '.join(sorted(unknown))}. Declare it as a parameter, or check "
            f"the spelling."
        )


def parse_initial_conditions(spec: EquationSpec, functions=None) -> dict:
    """Parse ``y(0)=1, y'(0)=0`` into the mapping `dsolve` expects."""
    text = (spec.initial_conditions or "").strip()
    if not text:
        return {}
    functions = functions or [sp.Function(n) for n in spec.variables]
    by_name = {str(f.__name__ if hasattr(f, "__name__") else f): f
               for f in functions}
    for name, function in zip(spec.variables, functions):
        by_name[name] = function

    parameters = {n: sp.Symbol(n, real=True) for n in spec.parameters}
    scope = {"t": _T, **parameters, **ALLOWED_FUNCTIONS}

    conditions: dict = {}
    for piece in re.split(r"[,;\n]", text):
        piece = piece.strip()
        if not piece:
            continue
        match = re.match(
            r"^([A-Za-z_][A-Za-z0-9_]*)((?:'|′)*)\s*\(\s*([^)]*)\s*\)\s*=\s*(.+)$",
            piece,
        )
        if not match:
            raise ParseError(
                f"cannot read the condition {piece!r} — write it like y(0) = 1 "
                f"or y'(0) = 0"
            )
        name, primes, at, value = match.groups()
        if name not in by_name:
            raise ParseError(f"{name!r} is not one of the variables in the equation")

        point = _parse_side(at, scope)
        amount = _parse_side(value, scope)
        function = by_name[name]
        order = len(primes)
        key = (
            function(point) if order == 0
            else function(_T).diff(_T, order).subs(_T, point)
        )
        conditions[key] = amount
    return conditions


# ---------------------------------------------------------------------------
# Constant-coefficient analysis: the by-hand method, shown
# ---------------------------------------------------------------------------


def characteristic_analysis(parsed: ParsedEquation) -> dict:
    """Characteristic polynomial, roots and fundamental set, when they exist.

    This is what one does on paper: collect the coefficients of each derivative,
    check they are constant, form ``a_n r^n + ... + a_0``, factor it, and read
    the basis off the roots -- ``e^{rt}`` for a simple real root, an extra
    ``t^k`` for each repetition, and ``e^{at}cos(bt)``/``e^{at}sin(bt)`` for a
    complex pair.
    """
    result = {
        "linear": False, "homogeneous": False, "constant_coefficients": False,
        "poly": None, "roots": [], "fundamental_set": [], "forcing": None,
    }
    if parsed.is_system:
        return result

    equation, function = parsed.equation, parsed.function
    expression = sp.expand(equation.lhs - equation.rhs)
    derivatives = [function(_T).diff(_T, k) for k in range(parsed.order + 1)]

    try:
        poly = sp.Poly(expression, *derivatives)
    except sp.PolynomialError:
        return result
    if poly.total_degree() > 1:
        return result                      # nonlinear in y or a derivative
    result["linear"] = True

    coefficients = []
    for k in range(parsed.order + 1):
        exponents = [0] * (parsed.order + 1)
        exponents[k] = 1
        coefficients.append(poly.coeff_monomial(sp.prod(
            [d**e for d, e in zip(derivatives, exponents)]
        )))
    constant_term = poly.coeff_monomial(1)
    forcing = sp.simplify(-constant_term)
    result["forcing"] = forcing
    result["homogeneous"] = forcing == 0

    if any(c.free_symbols & {_T} for c in coefficients if c is not None):
        return result                      # variable coefficients
    result["constant_coefficients"] = True

    r = sp.Symbol("r")
    characteristic = sum(
        (coefficients[k] or 0) * r**k for k in range(parsed.order + 1)
    )
    characteristic = sp.expand(characteristic)
    if characteristic == 0:
        return result
    result["poly"] = characteristic

    try:
        roots = sp.roots(sp.Poly(characteristic, r))
    except Exception:
        return result
    # Ordering by (real, imaginary) is what puts the roots in the sequence one
    # would write them, but it only works when they are numbers. With an
    # undetermined parameter left in -- `y'' + 2*c*y' + y = 0` before a value is
    # chosen -- the comparison is a symbolic relational and sympy refuses to
    # take its truth value. Fall back to a stable textual order rather than
    # letting a legitimate general answer raise.
    try:
        ordered = sorted(
            roots.items(), key=lambda item: (sp.re(item[0]), sp.im(item[0]))
        )
    except TypeError:
        ordered = sorted(roots.items(), key=lambda item: sp.default_sort_key(item[0]))
    result["roots"] = [(root, multiplicity) for root, multiplicity in ordered]

    basis: list[sp.Expr] = []
    seen_pairs: set = set()
    for root, multiplicity in ordered:
        real, imaginary = sp.re(root), sp.im(root)
        if imaginary == 0:
            for k in range(multiplicity):
                basis.append(_T**k * sp.exp(root * _T) if k else sp.exp(root * _T))
        else:
            key = (sp.simplify(real), sp.simplify(abs(imaginary)))
            if key in seen_pairs:
                continue               # a conjugate pair contributes once
            seen_pairs.add(key)
            for k in range(multiplicity):
                prefix = _T**k if k else sp.Integer(1)
                basis.append(prefix * sp.exp(real * _T) * sp.cos(abs(imaginary) * _T))
                basis.append(prefix * sp.exp(real * _T) * sp.sin(abs(imaginary) * _T))
    result["fundamental_set"] = basis
    return result


def with_parameters(parsed: ParsedEquation,
                    values: dict[str, float]) -> ParsedEquation:
    """The same equation with its parameters replaced by numbers.

    What makes a parameter slider worth having. `characteristic_analysis` on
    ``y'' + 2*c*y' + y = 0`` returns roots in terms of `c`, which is the honest
    general answer but not what someone dragging the slider wants to see: they
    want to watch a complex pair collide on the real axis at c = 1. Substituting
    first turns the roots into numbers that move.

    Cheap enough to run on every slider tick -- it is a substitution, not a
    re-parse.
    """
    if not values:
        return parsed
    # Exact rationals, not floats. With `Float(1.0)` the polynomial
    # ``r^2 + 2r + 1`` factors numerically into two roots that happen to be
    # equal, each carrying a whisker of imaginary part -- so the critically
    # damped case, the whole point of dragging the slider, was reported as
    # underdamped. In exact arithmetic sympy sees ``(r + 1)^2`` and returns one
    # root of multiplicity two. `str` keeps the rational as short as the value
    # the user actually chose.
    substitutions = {
        sp.Symbol(name, real=True): sp.Rational(str(float(amount)))
        for name, amount in values.items()
        if name in parsed.spec.parameters
    }
    if not substitutions:
        return parsed

    spec = replace(parsed.spec,
                   parameters={**parsed.spec.parameters, **{
                       k: v for k, v in values.items()
                       if k in parsed.spec.parameters
                   }})
    return ParsedEquation(
        spec=spec,
        equations=[equation.subs(substitutions) for equation in parsed.equations],
        functions=parsed.functions,
        order=parsed.order,
        is_system=parsed.is_system,
        ics={k.subs(substitutions): sp.sympify(v).subs(substitutions)
             for k, v in parsed.ics.items()},
    )


def describe_roots(roots: list[tuple[sp.Expr, int]], order: int = 0) -> str:
    """The behaviour the characteristic roots imply, in words.

    The vocabulary a course uses -- underdamped, critically damped, overdamped
    -- is read directly off the roots, and naming it is most of what makes the
    root table worth showing. Dragging a parameter until a complex pair collides
    on the real axis *is* the discriminant crossing, and it should say so.
    """
    if not roots:
        return ""

    complex_pair = any(sp.im(root) != 0 for root, _ in roots)
    repeated = any(multiplicity > 1 for _, multiplicity in roots)
    try:
        real_parts = [float(sp.re(root)) for root, _ in roots]
    except TypeError:
        return ""                      # symbolic parameters still present

    if all(part < 0 for part in real_parts):
        stability = "decays to zero"
    elif any(part > 0 for part in real_parts):
        stability = "grows without bound"
    else:
        stability = "neither grows nor decays"

    if order == 2 and len(real_parts) <= 2:
        if complex_pair:
            shape = "underdamped — oscillates inside a decaying envelope"
        elif repeated:
            shape = "critically damped — the fastest return without overshoot"
        else:
            shape = "overdamped — two decaying exponentials, no oscillation"
        return f"{shape}; {stability}"

    shape = "oscillatory" if complex_pair else "non-oscillatory"
    return f"{shape}; {stability}"


# ---------------------------------------------------------------------------
# dsolve, in a subprocess it can be killed in
# ---------------------------------------------------------------------------


def _worker_command() -> list[str]:
    """How to invoke this package as a solver subprocess.

    A frozen build has no interpreter to run ``-m`` with -- `sys.executable` is
    the application itself -- so the flag is routed through the normal CLI and
    works either way.
    """
    if getattr(sys, "frozen", False):
        return [sys.executable, "--dsolve-worker"]
    return [sys.executable, "-m", "odesuite_app", "--dsolve-worker"]


def _run_dsolve(payload: dict, timeout: float) -> dict:
    try:
        completed = subprocess.run(
            _worker_command(),
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "timeout": True,
                "error": f"no closed form found within {timeout:g} s"}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    if completed.returncode != 0 and not completed.stdout.strip():
        return {"ok": False,
                "error": (completed.stderr or "the solver process failed").strip()[-200:]}
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])
    except Exception:
        return {"ok": False, "error": "could not read the solver's reply"}


def solve_symbolically(parsed: ParsedEquation,
                       timeout: float = DSOLVE_TIMEOUT) -> SymbolicSolution:
    """Find a closed form, verify it, and describe the equation."""
    analysis = characteristic_analysis(parsed)
    solution = SymbolicSolution(
        order=parsed.order,
        linear=analysis["linear"],
        homogeneous=analysis["homogeneous"],
        constant_coefficients=analysis["constant_coefficients"],
        roots=analysis["roots"],
        characteristic_poly=analysis["poly"],
        fundamental_set=analysis["fundamental_set"],
    )

    payload = {
        "equations": [sp.srepr(equation) for equation in parsed.equations],
        "functions": [sp.srepr(f(_T)) for f in parsed.functions],
        "ics": {sp.srepr(k): sp.srepr(v) for k, v in parsed.ics.items()},
    }
    reply = _run_dsolve(payload, timeout)

    solution.classification = reply.get("classification", "")
    if not reply.get("ok"):
        solution.timed_out = bool(reply.get("timeout"))
        solution.message = reply.get("error", "no closed form found")
        return solution

    def restore(blob):
        """Rebuild sympy objects from the `srepr` strings the worker sent back."""
        if blob is None:
            return None
        if isinstance(blob, list):
            return [sp.sympify(item) for item in blob]
        return sp.sympify(blob)

    try:
        solution.general = restore(reply.get("general"))
        solution.particular = restore(reply.get("particular"))
    except Exception as exc:
        solution.message = f"could not read the solution back: {exc}"
        return solution

    solution.message = reply.get("message", "")
    _verify(parsed, solution)
    return solution


def _verify(parsed: ParsedEquation, solution: SymbolicSolution) -> None:
    """Substitute the solution back into the equation and simplify.

    A closed form is either right or it is not, and that is decidable here --
    so the interface never has to present an unchecked answer as though it were
    certain.
    """
    candidate = solution.best
    if candidate is None or parsed.is_system:
        return
    try:
        equation = parsed.equation
        residual = sp.simplify(
            (equation.lhs - equation.rhs)
            .subs(parsed.function(_T), candidate)
            .doit()
        )
        solution.residual = residual
        solution.verified = bool(sp.simplify(residual) == 0)
    except Exception:
        solution.verified = None


# ---------------------------------------------------------------------------
# Reduction to a first-order system, for the numeric side
# ---------------------------------------------------------------------------


def to_first_order(parsed: ParsedEquation, initial: list[float] | None = None,
                   params: dict[str, float] | None = None,
                   t_span: tuple[float, float] | None = None):
    """Build an `ODEProblem` equivalent to the parsed equation.

    A scalar equation of order *n* becomes the usual companion system with state
    ``[y, y', ..., y^(n-1)]``, so the whole numeric library -- every method,
    events, dense output, and the phase-plane analysis -- applies to an equation
    the user typed.

    `params` and `t_span` override what the spec carries, so a slider can rebuild
    the problem at a new parameter value without re-parsing the text.
    """
    spec = parsed.spec
    values = {**spec.parameters, **(params or {})}
    parameters = {sp.Symbol(n, real=True): v for n, v in values.items()}

    if parsed.is_system:
        states = [f(_T) for f in parsed.functions]
        derivatives = []
        for equation, function in zip(parsed.equations, parsed.functions):
            highest = function(_T).diff(_T)
            solved = sp.solve(equation, highest, dict=True)
            if not solved:
                raise ParseError(
                    f"cannot solve the equation for {function.__name__}'"
                )
            derivatives.append(solved[0][highest].subs(parameters))
        symbols = [sp.Symbol(f"__s{i}", real=True) for i in range(len(states))]
        replace = dict(zip(states, symbols))
        expressions = [d.subs(replace) for d in derivatives]
    else:
        function = parsed.function
        order = parsed.order
        highest = function(_T).diff(_T, order)
        solved = sp.solve(parsed.equation, highest, dict=True)
        if not solved:
            raise ParseError(
                "cannot rearrange the equation for its highest derivative"
            )
        top = solved[0][highest].subs(parameters)

        symbols = [sp.Symbol(f"__s{i}", real=True) for i in range(order)]
        replace = {function(_T).diff(_T, k): symbols[k] for k in range(order)}
        replace[function(_T)] = symbols[0]
        expressions = [*symbols[1:], top.subs(replace)]

    n = len(symbols)
    arguments = [_T, *symbols]
    try:
        f_compiled = sp.lambdify(arguments, expressions, "numpy")
        jacobian = sp.Matrix(expressions).jacobian(symbols)
        jac_compiled = sp.lambdify(arguments, jacobian, "numpy")
    except Exception as exc:
        raise ParseError(f"could not compile the system: {exc}") from exc

    def f(time, state):
        result = f_compiled(time, *state)
        try:
            return np.asarray(result, dtype=float).reshape(n)
        except (TypeError, ValueError):
            out = np.empty(n, dtype=object)
            for index in range(n):
                out[index] = result[index]
            return out

    def jac(time, state):
        return np.asarray(jac_compiled(time, *state), dtype=float).reshape(n, n)

    if initial is None:
        initial = _initial_from_ics(parsed, n)
    y0 = np.asarray(initial, dtype=float)
    if y0.size != n:
        raise ParseError(f"expected {n} initial values, got {y0.size}")

    problem = ODEProblem(f=f, t_span=t_span or spec.t_span, y0=y0, jac=jac)
    problem.state_labels = _state_labels(parsed, n)     # type: ignore[attr-defined]

    # Whether the right-hand side depends on `t` explicitly. Decided here
    # because this is the only place the reduced expressions exist: by now
    # ``y(t)`` has become a plain state symbol, so a surviving `t` is genuine
    # time dependence rather than the argument of the unknown function.
    #
    # It matters because a static vector field is only meaningful for an
    # autonomous system. Forcing (``y'' + y = cos t``) or variable coefficients
    # (Cauchy-Euler) make the field move, and drawing one snapshot of it would
    # show trajectories crossing their own streamlines -- a picture that looks
    # right and is not.
    problem.autonomous = not any(          # type: ignore[attr-defined]
        _T in expression.free_symbols for expression in expressions
    )
    return problem


def _initial_from_ics(parsed: ParsedEquation, n: int) -> list[float]:
    """Read ``y(0)=..., y'(0)=...`` into a state vector, defaulting to zero."""
    values = [0.0] * n
    if parsed.is_system:
        for index, function in enumerate(parsed.functions):
            for key, amount in parsed.ics.items():
                if key.func == function and not key.args[0].free_symbols:
                    values[index] = float(amount)
        return values

    function = parsed.function
    for key, amount in parsed.ics.items():
        order = 0
        target = key
        while isinstance(target, sp.Subs):
            target = target.expr
        if isinstance(target, sp.Derivative):
            order = int(target.derivative_count)
        if order < n:
            try:
                values[order] = float(amount)
            except TypeError:
                pass
    return values


def _state_labels(parsed: ParsedEquation, n: int) -> list[str]:
    if parsed.is_system:
        return list(parsed.spec.variables)
    name = parsed.spec.variables[0]
    return [name] + [f"{name}{chr(0x2032) * k}" for k in range(1, n)]


# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------

EXAMPLES: dict[str, EquationSpec] = {
    "Damped oscillator": EquationSpec(
        equations=["y'' + 2*y' + 5*y = 0"],
        initial_conditions="y(0) = 1, y'(0) = 0",
        t_span=(0.0, 8.0), name="Damped oscillator",
    ),
    "Overdamped": EquationSpec(
        equations=["y'' + 3*y' + 2*y = 0"],
        initial_conditions="y(0) = 1, y'(0) = 0",
        t_span=(0.0, 6.0), name="Overdamped",
    ),
    "Repeated root": EquationSpec(
        equations=["y'' + 2*y' + y = 0"],
        initial_conditions="y(0) = 1, y'(0) = 1",
        t_span=(0.0, 10.0), name="Repeated root",
    ),
    "Forced, resonant": EquationSpec(
        equations=["y'' + y = cos(t)"],
        initial_conditions="y(0) = 0, y'(0) = 0",
        t_span=(0.0, 30.0), name="Forced, resonant",
    ),
    "Forced, off-resonance": EquationSpec(
        equations=["y'' + 4*y = sin(t)"],
        initial_conditions="y(0) = 0, y'(0) = 1",
        t_span=(0.0, 20.0), name="Forced, off-resonance",
    ),
    "Third order": EquationSpec(
        equations=["y^(3) + y'' - y' - y = 0"],
        initial_conditions="y(0) = 1, y'(0) = 0, y''(0) = 0",
        t_span=(0.0, 5.0), name="Third order",
    ),
    "First order linear": EquationSpec(
        equations=["y' + 2*y = exp(-t)"],
        initial_conditions="y(0) = 0",
        t_span=(0.0, 6.0), name="First order linear",
    ),
    "Cauchy–Euler": EquationSpec(
        equations=["t**2*y'' + t*y' - y = 0"],
        initial_conditions="y(1) = 1, y'(1) = 0",
        t_span=(1.0, 6.0), name="Cauchy–Euler",
    ),
    "Logistic (separable)": EquationSpec(
        equations=["y' = y*(1 - y)"],
        initial_conditions="y(0) = 0.1",
        t_span=(0.0, 12.0), name="Logistic (separable)",
    ),
    "Linear system": EquationSpec(
        equations=["x' = x + 2*y", "y' = 3*x + 2*y"],
        initial_conditions="x(0) = 1, y(0) = 0",
        variables=["x", "y"], t_span=(0.0, 1.5), name="Linear system",
    ),
    "Van der Pol (no closed form)": EquationSpec(
        equations=["y'' - mu*(1 - y**2)*y' + y = 0"],
        initial_conditions="y(0) = 2, y'(0) = 0",
        parameters={"mu": 3.0}, t_span=(0.0, 30.0),
        name="Van der Pol (no closed form)",
    ),
}
