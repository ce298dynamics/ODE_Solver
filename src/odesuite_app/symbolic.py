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

from .custom import (
    _SAFE_GLOBALS,
    _TRANSFORMATIONS,
    ALLOWED_FUNCTIONS,
    ParseError,
    reject_unsafe_syntax,
)

__all__ = [
    "EquationSpec",
    "SymbolicSolution",
    "ParsedEquation",
    "parse_equation",
    "read_answer",
    "spec_for",
    "parse_initial_conditions",
    "solve_symbolically",
    "solve_by_laplace",
    "characteristic_analysis",
    "analyse_linear",
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
    #: The technique named to the user. This is the *teaching* choice among
    #: `hints`, not sympy's first: `classify_ode` leads `y'' + 3y' + 2y = 0`
    #: with `factorable` and `y' + 2y = t` with `1st_exact`, neither of which
    #: is what the equation is called in a course.
    classification: str = ""
    #: Every hint `classify_ode` returned, in its order.
    hints: tuple[str, ...] = ()
    #: The narrated derivation, when a technique in `steps` applies.
    derivation: object | None = None
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
    #: The `t` the initial conditions were given at, when they agree on one.
    #: None when there are none, or they disagree, or the point is symbolic.
    #: An interval of validity is meaningless without it -- ``1/(1-t)`` is valid
    #: on ``(-oo, 1)`` from t = 0 and on ``(1, oo)`` from t = 2.
    initial_point: float | None = None

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

    # Every route by which a user's text reaches sympy from this module passes
    # through here -- both sides of an equation, an initial condition, a typed
    # answer -- so this is the one place the syntax guard has to be.
    reject_unsafe_syntax(text)

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


def spec_for(equation: str, conditions: str = "") -> EquationSpec:
    """An `EquationSpec` from one string, whether it is a system or not.

    A lesson stores its equation as text, and a system is several equations.
    Rather than give the content model a list it would need only sometimes,
    the convention is a semicolon: ``x' = x + 2*y; y' = 3*x + 2*y``. The
    unknowns are then read off the left-hand sides, because a system's
    `variables` cannot be guessed and getting them wrong renames the problem.

    A semicolon rather than a comma, deliberately: conditions are written
    ``x(0) = 1, y(0) = 0`` and reusing the separator across both would make
    one of them ambiguous the first time an equation needed a comma.
    """
    parts = [part.strip() for part in equation.split(";") if part.strip()]
    if len(parts) < 2:
        return EquationSpec(equations=parts or [equation],
                            initial_conditions=conditions)

    names = []
    for part in parts:
        left = part.split("=", 1)[0]
        name = re.sub(r"[^A-Za-z0-9_].*$", "", left.strip())
        if not name:
            raise ParseError(f"cannot tell what {part!r} solves for")
        names.append(name)
    return EquationSpec(equations=parts, initial_conditions=conditions,
                        variables=names)


def parse_equation(spec: EquationSpec, *,
                   extra_functions: dict | None = None) -> ParsedEquation:
    """Parse `spec` into sympy equations in terms of ``y(t)``.

    `extra_functions` widens the whitelist for one caller only. The Laplace
    screen is the only user: it needs `Heaviside` and `DiracDelta`, and those
    must not become typeable everywhere, because `DiracDelta` has no numerical
    value at all and a discontinuous right-hand side is exactly what an adaptive
    step can cross without noticing. See `laplace.EXTRA_FUNCTIONS`.
    """
    if not spec.equations or not any(e.strip() for e in spec.equations):
        raise ParseError("type an equation")
    allowed = {**ALLOWED_FUNCTIONS, **(extra_functions or {})}
    for name in [*spec.variables, *spec.parameters]:
        if name == "t":
            raise ParseError("'t' is the independent variable")
        if name in allowed:
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

        scope: dict = {"t": _T, **parameters, **allowed}
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
    if parsed.is_system:
        return _system_analysis(parsed)
    return analyse_linear(parsed.equation, parsed.function, parsed.order)


def _system_analysis(parsed: ParsedEquation) -> dict:
    """The same table, read off a matrix instead of a polynomial.

    A system has no characteristic *polynomial* in the scalar sense, but it
    has the same object under a different name: ``det(A - lambda I)``, whose
    roots are the eigenvalues and decide the behaviour exactly as the
    characteristic roots do. Reporting nothing here left the Studio's root
    table blank for systems, which read as "this equation has no structure"
    rather than "we did not look".

    `describe_roots` then summarises these through its general branch, because
    a parsed system has `order == 1` -- and that is the right branch. The
    damping vocabulary belongs to a second-order *equation*; a system's origin
    is named saddle or node or spiral, which `systems.classify` does inside
    the narration where the eigenvectors are also to hand.
    """
    from .systems import split_system

    result = _no_analysis()
    parts = split_system(parsed.equations, parsed.functions)
    if parts is None:
        return result
    matrix, forcing = parts

    lam = sp.Symbol("lambda")
    polynomial = sp.expand((matrix - lam * sp.eye(matrix.shape[0])).det())
    try:
        roots = sp.roots(sp.Poly(polynomial, lam))
    except Exception:
        return result
    if not roots:
        return result

    basis: list = []
    for value, multiplicity, vectors in matrix.eigenvects():
        for vector in vectors[:multiplicity]:
            basis.append(vector * sp.exp(value * _T))

    return {
        "linear": True,
        "homogeneous": all(entry == 0 for entry in forcing),
        "constant_coefficients": True,
        "poly": polynomial,
        "roots": sorted(roots.items(), key=lambda item: sp.default_sort_key(
            item[0])),
        "fundamental_set": basis,
        "forcing": forcing if any(entry != 0 for entry in forcing) else None,
    }


def _no_analysis() -> dict:
    return {
        "linear": False, "homogeneous": False, "constant_coefficients": False,
        "poly": None, "roots": [], "fundamental_set": [], "forcing": None,
    }


def analyse_linear(equation: sp.Eq, function: sp.Function, order: int) -> dict:
    """`characteristic_analysis` on plain sympy, without a `ParsedEquation`.

    Split out so `steps` can narrate the same working from inside the solver
    subprocess, which has the equation but not the app's dataclasses.
    """
    result = _no_analysis()
    expression = sp.expand(equation.lhs - equation.rhs)
    derivatives = [function(_T).diff(_T, k) for k in range(order + 1)]

    try:
        poly = sp.Poly(expression, *derivatives)
    except sp.PolynomialError:
        return result
    if poly.total_degree() > 1:
        return result                      # nonlinear in y or a derivative
    result["linear"] = True

    coefficients = []
    for k in range(order + 1):
        exponents = [0] * (order + 1)
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
        (coefficients[k] or 0) * r**k for k in range(order + 1)
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
    except subprocess.TimeoutExpired as expired:
        # The worker publishes the classification and any derivation *before*
        # attempting `dsolve`, so a killed process usually still left something
        # on stdout. ``y' = sin(y)`` is the case that matters: `dsolve` never
        # returns, while separation of variables solves it outright, and losing
        # that to the timeout would be discarding a complete answer.
        partial = _last_reply(expired.stdout)
        message = f"no closed form found within {timeout:g} s"
        if partial is not None:
            return dict(partial, ok=False, timeout=True, error=message)
        return {"ok": False, "timeout": True, "error": message}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    if completed.returncode != 0 and not completed.stdout.strip():
        return {"ok": False,
                "error": (completed.stderr or "the solver process failed").strip()[-200:]}
    reply = _last_reply(completed.stdout)
    if reply is None:
        return {"ok": False, "error": "could not read the solver's reply"}
    return reply


def _last_reply(stream) -> dict | None:
    """The last complete JSON object the worker wrote, if any.

    Scans backwards rather than taking the final line outright: a killed
    process can be cut off mid-write, leaving a truncated last line above an
    intact earlier one.
    """
    if not stream:
        return None
    text = stream if isinstance(stream, str) else stream.decode("utf-8", "replace")
    for line in reversed(text.strip().splitlines()):
        try:
            parsed = json.loads(line)
        except Exception:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def solve_by_laplace(parsed: ParsedEquation,
                     timeout: float | None = None) -> SymbolicSolution:
    """Solve by transforming, in the same killable subprocess `dsolve` uses.

    Returns a `SymbolicSolution` whose `derivation` is the narrated transform.
    `general`/`particular` stay empty: the answer is the derivation's result,
    checked by the derivation itself, and there is no second opinion to report.
    """
    timeout = DSOLVE_TIMEOUT if timeout is None else timeout
    solution = SymbolicSolution(order=parsed.order)
    if parsed.is_system:
        solution.message = "the transform method here handles one equation at a time"
        return solution

    reply = _run_dsolve({
        "equations": [sp.srepr(parsed.equation)],
        "functions": [sp.srepr(parsed.function(_T))],
        "ics": {sp.srepr(k): sp.srepr(v) for k, v in parsed.ics.items()},
        "mode": "laplace",
    }, timeout)

    solution.derivation = _restore_derivation(reply.get("derivation"))
    solution.timed_out = bool(reply.get("timeout"))
    if not reply.get("ok") and solution.derivation is None:
        # `_run_dsolve`'s timeout text is about `dsolve`, which this path never
        # runs. Saying "no closed form found" here would name the wrong cause.
        solution.message = (
            f"the transform did not finish within {timeout:g} s"
            if solution.timed_out
            else reply.get("error", "the transform could not be taken")
        )
    return solution


def _label(hints, first: str) -> str:
    """What to call the equation: the technique a course teaches, if there is one.

    `classify_ode` orders its hints by what sympy would rather solve with, and
    that order buries the teaching name -- ``y'' + 3y' + 2y = 0`` comes back
    led by `factorable`. Where one of the narrated techniques applies, it is the
    better label whether or not a derivation is asked for.
    """
    from .steps import preferred_hint

    return preferred_hint(hints) or first


def _restore_derivation(blob):
    """Rebuild a `steps.Derivation` from the worker's plain-dict form."""
    if not blob:
        return None
    from .steps import Derivation, Step

    return Derivation(
        technique=blob.get("technique", ""),
        title=blob.get("title", ""),
        steps=[
            Step(title=s.get("title", ""), latex=s.get("latex", ""),
                 note=s.get("note", ""), verified=s.get("verified"))
            for s in blob.get("steps", [])
        ],
        result=(sp.sympify(blob["result"]) if blob.get("result") else None),
        verified=blob.get("verified"),
        check=blob.get("check", ""),
        message=blob.get("message", ""),
    )


def solve_symbolically(parsed: ParsedEquation, timeout: float | None = None,
                       steps: bool = False) -> SymbolicSolution:
    """Find a closed form, verify it, and describe the equation.

    `timeout` defaults to `DSOLVE_TIMEOUT`, read at call time so the module
    attribute can be raised on a slow or heavily loaded machine.

    `steps` asks the worker to narrate the derivation as well. Off by default:
    only the Learning Hub displays it, and the Solver Studio should not pay for
    work it does not show.
    """
    timeout = DSOLVE_TIMEOUT if timeout is None else timeout
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
        "steps": bool(steps),
    }
    reply = _run_dsolve(payload, timeout)

    solution.hints = tuple(reply.get("hints") or ())
    solution.classification = _label(solution.hints,
                                     reply.get("classification", ""))
    solution.derivation = _restore_derivation(reply.get("derivation"))
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
    solution.initial_point = _initial_point(parsed)
    _verify(parsed, solution)
    return solution


def _initial_point(parsed: ParsedEquation) -> float | None:
    """The `t` the initial conditions were given at, when they agree on one.

    Needed because an interval of validity is a statement about the solution
    through a *point*: the same expression ``1/(1-t)`` is valid on ``(-oo, 1)``
    from ``t = 0`` and on ``(1, oo)`` from ``t = 2``. Assuming zero would be
    right almost always and confidently wrong the rest of the time, which is
    the trade this module keeps declining to make.
    """
    points = set()
    for condition in parsed.ics:
        _order, point = _condition_at(condition)
        if point is None:
            return None
        try:
            value = float(point)
        except (TypeError, ValueError):
            return None
        points.add(round(value, 12))
    if len(points) != 1:
        return None
    return points.pop()


#: Functions with no singularity anywhere on the real line. An expression built
#: only from these, rational operations and integer powers has poles exactly
#: where its denominator vanishes -- which is a question about a polynomial, and
#: therefore quick and certain. Anything else declines.
_ENTIRE_FUNCTIONS = (sp.exp, sp.sin, sp.cos, sp.sinh, sp.cosh)


def _time_symbol(expression: sp.Expr):
    """The symbol standing for time in `expression`, or None if unclear.

    `_T` carries ``real=True`` and a symbol's assumptions are part of its
    identity, so the ``t`` in an expression built elsewhere -- by `sympify` on
    plain text, say -- is a *different* symbol. Treating them as one made
    `sp.Poly` read `1/(1-t)` as a constant and report no poles at all, which is
    the wrong answer in the dangerous direction.
    """
    free = expression.free_symbols
    if _T in free:
        return _T
    named = [s for s in free if s.name == "t"]
    if len(named) == 1:
        return named[0]
    if len(free) == 1:
        return next(iter(free))
    return None


def _real_poles(expression: sp.Expr) -> list[float] | None:
    """Real poles of `expression`, or None when they cannot be settled cheaply.

    Declining is a real answer here, and the reason to prefer it is that the
    alternative is worse than useless. `tan(t)` has poles at every odd multiple
    of pi/2 and no denominator to show for it; a routine that looked only at the
    denominator would report "no poles" and the interface would tell a student
    the solution is valid on the whole line. A missing interval is a gap. A
    wrong one is a lie, and this module exists partly to stop telling those.

    `sympy.singularities` is the general answer and is not usable here: it did
    not return within ten minutes on ``1/(1-t)``, against a twelve-second budget
    for the whole symbolic route.
    """
    expression = sp.together(expression)
    if not expression.free_symbols:
        return []                       # a constant has no poles
    variable = _time_symbol(expression)
    if variable is None:
        return None

    for function in expression.atoms(sp.Function):
        if not isinstance(function, _ENTIRE_FUNCTIONS):
            return None                 # tan, log, sqrt, Bessel, ...
    for power in expression.atoms(sp.Pow):
        if not power.exp.is_Integer:
            return None                 # a branch point, not a pole

    denominator = sp.denom(expression)
    # exp never vanishes on the reals, so an exp factor contributes no pole.
    denominator = denominator.replace(
        lambda e: isinstance(e, sp.exp), lambda e: sp.Integer(1)
    )
    if denominator.has(sp.sin) or denominator.has(sp.cos):
        return None                     # these do vanish; where is another question
    if denominator.is_number:
        return []
    try:
        polynomial = sp.Poly(denominator, variable)
    except sp.PolynomialError:
        return None
    if polynomial.degree() < 1:
        return []
    try:
        return sorted(float(r) for r in sp.real_roots(polynomial) if r.is_real)
    except (TypeError, ValueError):
        return None


def interval_of_validity(expression, t0: float):
    """The largest interval around `t0` on which `expression` is defined.

    Returned as ``(low, high)`` with None for an unbounded end, or None when it
    could not be decided.

    Worth having because the application currently disagrees with itself about
    it. Solving ``y' = y^2, y(0) = 1`` shows ``y = 1/(1 - t)`` with nothing to
    say it means anything only for ``t < 1``; the *numerical* side of the same
    application stops at ``t = 1`` and reports that the solution may be blowing
    up there; and the `slopefields` lesson teaches that the existence theorem is
    local. Three parts of one product, one of them silent.
    """
    if expression is None:
        return None
    try:
        poles = _real_poles(sp.sympify(expression))
    except Exception:
        return None
    if poles is None:
        return None
    if any(abs(p - t0) <= 1e-12 for p in poles):
        return None                     # t0 is itself a pole; say nothing
    below = [p for p in poles if p < t0]
    above = [p for p in poles if p > t0]
    return (max(below) if below else None, min(above) if above else None)


def format_interval(bounds) -> str:
    """``(low, high)`` as a reader would write it. Empty for the whole line."""
    if bounds is None:
        return ""
    low, high = bounds
    if low is None and high is None:
        return ""                       # valid everywhere: saying so adds noise
    left = "-∞" if low is None else f"{low:g}"
    right = "∞" if high is None else f"{high:g}"
    return f"({left}, {right})"


def _verify(parsed: ParsedEquation, solution: SymbolicSolution) -> None:
    """Substitute the solution back into the equation and simplify.

    A closed form is either right or it is not, and that is decidable here --
    so the interface never has to present an unchecked answer as though it were
    certain.
    """
    candidate = solution.best
    if candidate is None:
        return
    if parsed.is_system:
        _verify_system(parsed, solution, candidate)
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


def _verify_system(parsed: ParsedEquation, solution: SymbolicSolution,
                   candidate) -> None:
    """The same substitution, all components into all equations at once.

    A system's answer is one function per unknown, so every component has to
    go into every equation together -- substituting them one equation at a
    time would call a pair correct that satisfies the first and fails the
    second. This used to be skipped entirely, which left the Studio showing a
    system's answer unchecked even though checking it is no harder than
    checking a scalar one.
    """
    parts = candidate if isinstance(candidate, (list, tuple)) else [candidate]
    if len(parts) != len(parsed.functions):
        solution.verified = None
        return
    try:
        substitutions = {function(_T): part
                         for function, part in zip(parsed.functions, parts)}
        residuals = [
            sp.simplify((equation.lhs - equation.rhs)
                        .subs(substitutions).doit())
            for equation in parsed.equations
        ]
        solution.residual = sp.Matrix(residuals)
        solution.verified = all(sp.simplify(residual) == 0
                                for residual in residuals)
    except Exception:
        solution.verified = None


# ---------------------------------------------------------------------------
# Checking the student's own answer
# ---------------------------------------------------------------------------


@dataclass
class AnswerCheck:
    """The verdict on a solution somebody typed in."""

    #: What was parsed, or None if it could not be.
    expression: sp.Expr | None = None
    #: The residual after substituting it into the equation, simplified.
    residual: sp.Expr | None = None
    #: True when the residual simplifies to exactly zero. None when sympy could
    #: not decide, which is not the same as "wrong" and must not be shown as it.
    correct: bool | None = None
    #: True when it also satisfies the initial conditions, where any were given.
    matches_conditions: bool | None = None
    message: str = ""
    #: What the residual says went wrong, in a sentence, or "" when the ladder
    #: in `diagnose` recognised nothing. Never a substitute for `message`:
    #: this says *how far the answer got*, which is a different claim from
    #: whether it is right.
    diagnosis: str = ""

    @property
    def ok(self) -> bool:
        return bool(self.correct) and self.matches_conditions is not False


def read_answer(parsed: ParsedEquation, text: str) -> list[tuple[str, sp.Expr]]:
    """Read a typed solution into ``(unknown, expression)`` pairs, or raise.

    The parsing half of `check_answer`, on its own so that the answer box's
    live preview reads the text exactly as the grader will. A preview with its
    own parser would be a second opinion, and the student would be shown one
    reading and marked on another.

    One pair for a single equation, written with or without its ``y =``; one
    per unknown, in the system's order, for a system, where every line must
    name its unknown. `ParseError` carries a message meant for the student.
    """
    if not text or not text.strip():
        raise ParseError("type a solution to check")
    if parsed.is_system:
        return _read_system_answer(parsed, text)

    scope = {"t": _T, "C1": sp.Symbol("C1"), "C2": sp.Symbol("C2"),
             "C3": sp.Symbol("C3"), "C": sp.Symbol("C1")}
    # Any free symbol already in the equation -- a parameter the user gave a
    # slider -- must resolve to the *same* symbol here, or the residual will
    # never simplify away.
    for symbol in parsed.equation.free_symbols:
        if symbol.is_Symbol and symbol is not _T:
            scope.setdefault(symbol.name, symbol)
    # Likewise a function the equation was allowed to use: a caller that widened
    # the whitelist for ``Heaviside(t - 2)`` in the forcing gets an answer
    # written with it too, which is the only way a switched answer can be
    # written at all. Only named sympy functions -- never the unknown itself.
    for applied in parsed.equation.atoms(sp.Function):
        if not isinstance(applied, sp.core.function.AppliedUndef):
            scope.setdefault(type(applied).__name__, type(applied))
    # The two are one family: the response to a blow δ(t - a) is switched on
    # by u(t - a), so an impulsive equation needs the step in its answer.
    if "DiracDelta" in scope or "Heaviside" in scope:
        scope.setdefault("Heaviside", sp.Heaviside)
        scope.setdefault("DiracDelta", sp.DiracDelta)

    # A student writes the answer the way it is written on paper: "y = ...".
    # Accept that, with or without spaces and with or without the "(t)".
    text = re.sub(
        r"^\s*y\s*(\(\s*t\s*\))?\s*=\s*", "", text.strip(), count=1,
        flags=re.IGNORECASE,
    )
    if not text:
        raise ParseError("type a solution to check")
    return [(parsed.function.__name__, _parse_side(text, scope))]


def _read_system_answer(parsed: ParsedEquation,
                        text: str) -> list[tuple[str, sp.Expr]]:
    names = {function.__name__: function for function in parsed.functions}
    scope = {"t": _T}
    for index in range(1, 5):
        scope[f"C{index}"] = sp.Symbol(f"C{index}")
    for equation in parsed.equations:
        for symbol in equation.free_symbols:
            if symbol.is_Symbol and symbol is not _T:
                scope.setdefault(symbol.name, symbol)

    candidates: dict[str, sp.Expr] = {}
    for line in re.split(r"[\n;]+", text.strip()):
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^\s*([A-Za-z]\w*)\s*(\(\s*t\s*\))?\s*=\s*(.+)$",
                         line, flags=re.DOTALL)
        if not match or match.group(1) not in names:
            raise ParseError(
                "write one line per unknown, naming each: "
                + ", ".join(f"{name} = ..." for name in names)
            )
        candidates[match.group(1)] = _parse_side(match.group(3), scope)

    missing = set(names) - set(candidates)
    if missing:
        raise ParseError(f"no line for {', '.join(sorted(missing))}")
    return [(function.__name__, candidates[function.__name__])
            for function in parsed.functions]


def check_answer(parsed: ParsedEquation, text: str) -> AnswerCheck:
    """Substitute a proposed solution into the equation and report what is left.

    The same test the library already applies to sympy's own answer, pointed at
    the user's instead. That is the whole implementation: `_verify` decides
    whether a closed form is right by substituting and simplifying, and there is
    no reason a hand-written candidate deserves a weaker check.

    Two things it deliberately does not do. It does not compare against sympy's
    answer -- an equation has many equivalent forms and a student who wrote
    ``C*exp(-t)`` where sympy wrote ``C1*exp(-t)`` is not wrong. And it does not
    report "wrong" when simplification merely fails; `correct` is None there,
    because the residual not visibly vanishing is not proof that it does not.

    The text goes through the same hardened parser as everything else --
    `parse_expr` with an emptied ``__builtins__`` and a whitelist -- because
    this is a new place a user's string reaches sympy, and `sympify` executes
    what it is given.
    """
    if not text or not text.strip():
        return AnswerCheck(message="type a solution to check")
    if parsed.is_system:
        return _check_system(parsed, text)

    try:
        [(_, candidate)] = read_answer(parsed, text)
    except ParseError as exc:
        return AnswerCheck(message=str(exc))

    from .steps import vanishes

    check = AnswerCheck(expression=candidate)
    jumps: list = []
    try:
        equation = parsed.equation
        raw = (equation.lhs - equation.rhs).subs(parsed.function(_T), candidate).doit()
        if raw.has(sp.DiracDelta):
            raw, jumps = _sift_impulses(raw)
        residual = sp.simplify(raw)
        check.residual = residual
        # `vanishes`, not `simplify(...) == 0`. The docstring above always
        # promised that a residual sympy merely failed to simplify is "cannot
        # tell", not "wrong", and the code said wrong: a correct answer to the
        # course's own non-uniqueness example was marked as a mistake.
        check.correct, domain = vanishes(residual)
    except Exception as exc:
        check.message = f"could not decide: {exc}"
        return check

    if jumps:
        where = ", ".join(sp.sstr(point) for point in sorted(jumps, key=float))
        check.correct = False
        check.message = (
            f"substituting it leaves an impulse at t = {where}: the answer or "
            f"one of its derivatives jumps there by the wrong amount. Check "
            f"that each switched-on term has its argument shifted too -- "
            f"u(t - a)g(t - a), not u(t - a)g(t)"
        )
        return check

    if check.correct and parsed.ics:
        check.matches_conditions = _satisfies_conditions(parsed, candidate)

    if check.correct is False:
        check.message = "substituting it does not give zero"
    elif check.correct is None:
        check.message = ("sympy could not simplify what is left, though it "
                         "vanishes at every point tried -- probably right, "
                         "not proven")
    elif check.matches_conditions is False:
        check.message = "it solves the equation, but not with these conditions"
    elif domain:
        check.message = (f"verified for {domain}: substituting it gives "
                         f"exactly zero there")
    else:
        check.message = "verified: substituting it gives exactly zero"
    check.diagnosis = diagnose(parsed, check)
    return check


def _sift_impulses(expression) -> tuple[sp.Expr, list]:
    """Separate the impulses from a residual: ``(smooth part, [where one is left])``.

    Differentiating ``Heaviside(t - a)`` leaves ``DiracDelta(t - a)`` terms in a
    residual, and those are exactly where a switched answer is right or wrong --
    ``u(t - 2)(1 - e^(-t))`` solves ``y' + y = u(t - 2)`` on both sides of the
    switch and fails only by jumping at it. Sampling cannot see that, because a
    delta is zero at every point tried. So sift: ``c(t)δ⁽ᵏ⁾(t - a)`` is a
    combination of ``δ⁽ʲ⁾(t - a)`` with the constant coefficients
    ``(-1)^(k-j) C(k, j) c^(k-j)(a)``, and the answer is right only if every one of
    those collects to zero. Returns the smooth part with the zero impulses
    removed, and the points where an impulse survives. An impulse sympy cannot
    decide about is left in the smooth part, where the usual check sees it.
    """
    smooth = sp.Integer(0)
    impulses: dict = {}
    for term in sp.Add.make_args(sp.expand(expression)):
        deltas = [f for f in term.atoms(sp.DiracDelta) if f.args[0].has(_T)]
        if len(deltas) != 1:
            smooth += term
            continue
        delta = deltas[0]
        coefficient = term / delta
        argument = delta.args[0]
        order = int(delta.args[1]) if len(delta.args) > 1 else 0
        slope = sp.diff(argument, _T)
        if (coefficient.has(delta)
                or not sp.Poly(argument, _T).degree() == 1
                or slope not in (1, -1)):
            smooth += term
            continue
        # sympy writes δ(t - 1 - π) as δ(-t + 1 + π); δ⁽ᵏ⁾ is even or odd as k is.
        if slope == -1:
            coefficient *= (-1) ** order
        point = sp.solve(argument, _T)[0]
        for j in range(order + 1):
            key = (point, order - j)
            weight = (-1) ** j * sp.binomial(order, j)
            value = weight * sp.diff(coefficient, _T, j).subs(_T, point)
            impulses[key] = impulses.get(key, 0) + value

    jumps = []
    for (point, order), total in impulses.items():
        total = sp.simplify(total)
        if total == 0:
            continue
        if total.is_zero is False and point not in jumps:
            jumps.append(point)
        else:
            smooth += total * sp.DiracDelta(_T - point, order)
    return smooth, jumps


# ---------------------------------------------------------------------------
# Reading the residual
# ---------------------------------------------------------------------------
#
# A residual is not a verdict, it is evidence, and printing it raw asks the
# person who has just got the question wrong to do the one piece of analysis
# they have just shown they cannot do. Almost always it names the mistake:
#
# * left with exactly what substituting nothing leaves -> the left-hand side
#   vanished, so this is the complementary function and no particular solution;
# * a scalar multiple away from vanishing -> the shape is right and a
#   coefficient was dropped, or at k = -1 a sign;
# * a constant away -> a constant of integration went missing;
# * zero residual but the conditions fail -> the method was right and the
#   constants were not.
#
# Every rung is a *test that either fires or does not*, never a guess: each one
# ends in ``simplify(...) == 0`` or in a root sympy actually found. A rung that
# recognises nothing returns "", and the caller falls back to showing the
# residual -- worth less than a sentence and a great deal more than silence.


def diagnose(parsed: ParsedEquation, check: AnswerCheck) -> str:
    """What the residual says went wrong, in a sentence, or "".

    Never raises, and never contradicts `check`: it is asked only once the
    verdict is settled, and it explains that verdict rather than revising it.
    """
    try:
        if check.correct is True and check.matches_conditions is False:
            return _diagnose_constants(parsed, check)
        if check.correct is not False or check.residual is None:
            return ""
        if parsed.is_system:
            return _diagnose_system(parsed, check)
        return _diagnose_one(parsed, check)
    except Exception:
        return ""


def _diagnose_constants(parsed: ParsedEquation, check: AnswerCheck) -> str:
    """Right equation, wrong member of its family.

    The most encouraging verdict in the ladder and the one most worth spelling
    out: the method is entirely right and what is left is arithmetic. It names
    the condition that fails and what the answer gives there instead, because
    "solve for C1" is advice and "it gives 3 where the condition asks for 5" is
    a place to start.
    """
    tail = ""
    if not parsed.is_system and check.expression is not None:
        name = parsed.function.__name__
        for condition, value in parsed.ics.items():
            order, point = _condition_at(condition)
            if point is None:
                continue
            expression = check.expression
            if order:
                expression = sp.diff(expression, _T, order)
            got = sp.simplify(expression.subs(_T, point))
            if sp.simplify(got - value) == 0:
                continue
            marks = "'" * order
            tail = (f" At t = {point} yours gives {name}{marks} = {got}, "
                    f"where the condition asks for {value}.")
            break
    return ("The method is right and the constants are not: this solves the "
            "equation, but it is the wrong member of the family." + tail
            + " Put the condition into your general solution and solve for "
              "the constant -- the hard part is already done.")


def _diagnose_one(parsed: ParsedEquation, check: AnswerCheck) -> str:
    """The ladder for a single equation. The rungs are listed above."""
    candidate, residual = check.expression, check.residual
    if candidate is None or residual is None:
        return ""
    name = parsed.function.__name__
    unknown = parsed.function(_T)
    operator = parsed.equation.lhs - parsed.equation.rhs

    def leftover(expression) -> sp.Expr:
        return sp.simplify(operator.subs(unknown, expression).doit())

    if not candidate.has(_T):
        return ("Your answer does not contain t at all, so every derivative "
                "of it is zero and the equation collapses to whatever is left "
                "when the derivatives go. A solution of this one has to "
                "change with t.")

    # Substituting nothing at all: for a linear L[y] = f this is exactly -f,
    # so an answer that leaves the same thing has killed L and ignored f.
    nothing = leftover(sp.Integer(0))
    if nothing != 0 and sp.simplify(residual - nothing) == 0:
        return ("You have the complementary function and no particular "
                "solution. Substituting your answer leaves exactly what "
                f"substituting {name} = 0 leaves, so it makes the homogeneous "
                "equation vanish and does nothing whatever about the forcing "
                "term. Find any one solution of the full equation and add it "
                "on.")

    # The additive rung is asked *before* the multiplicative one, and the order
    # is not arbitrary. An answer carrying an arbitrary constant absorbs a
    # scaling -- 5*(C1*exp(-t) + 1) solves y' + y = 5 as surely as C1*exp(-t)
    # + 5 does -- so the coefficient rung fires on answers whose real mistake
    # is a dropped constant, and says the less useful of two true things.
    shift = sp.Symbol("_c")
    for root in _roots(leftover(candidate + shift), shift):
        if root == 0:
            continue
        # "adding -3" is how a program writes it and not how anybody says it.
        move = (f"adding {root}" if root.is_positive
                else f"subtracting {-root}")
        return (f"You are one constant away: {move} makes your answer exact. "
                f"A constant of integration, or the constant term of a "
                f"particular solution, is what went missing.")

    scale = sp.Symbol("_k")
    for root in _roots(leftover(scale * candidate), scale):
        if root in (0, 1):
            continue
        if root == -1:
            return ("A sign, and nothing else: minus your answer satisfies "
                    "the equation exactly. The shape and every coefficient "
                    "inside it are right.")
        return (f"The shape is right and a coefficient is not: {root} times "
                f"your answer satisfies the equation exactly, so the "
                f"functions are the ones the method gives and the constant in "
                f"front of them was lost.")

    return ""


def _diagnose_system(parsed: ParsedEquation, check: AnswerCheck) -> str:
    """The ladder for a system, where "half right" is a literal statement."""
    if check.expression is None or check.residual is None:
        return ""
    components = list(check.expression)
    residuals = list(check.residual)
    names = [function.__name__ for function in parsed.functions]

    def leftovers(assignment) -> list:
        return [sp.simplify((equation.lhs - equation.rhs)
                            .subs(assignment).doit())
                for equation in parsed.equations]

    if len(names) == 2 and len(components) == 2:
        swapped = {parsed.functions[0](_T): components[1],
                   parsed.functions[1](_T): components[0]}
        if all(value == 0 for value in leftovers(swapped)):
            return (f"The two components are the wrong way round: what you "
                    f"wrote for {names[0]} is the answer for {names[1]}, and "
                    f"the other way about. The mathematics is right.")

    solved = [index for index, value in enumerate(residuals)
              if sp.simplify(value) == 0]
    if solved and len(solved) < len(residuals):
        missed = [index for index in range(len(residuals))
                  if index not in solved]
        return ("Half-way: " + _equations(solved) + " comes out exactly zero "
                "and " + _equations(missed) + " does not. A pair has to "
                "satisfy both at once, which is the whole difficulty of a "
                "system -- fixing one component on its own is what breaks the "
                "other.")
    return ""


def _equations(indices: list) -> str:
    """``equation 1``, or ``equations 1 and 3``, for a sentence."""
    numbers = [str(index + 1) for index in indices]
    if len(numbers) == 1:
        return f"equation {numbers[0]}"
    return "equations " + " and ".join([", ".join(numbers[:-1]), numbers[-1]])


def _roots(expression: sp.Expr, symbol: sp.Symbol) -> list:
    """Real numeric roots of `expression` in `symbol`, or none at all.

    Numeric ones only: a root in terms of t would mean "your answer works at
    one instant", which is nobody's mistake and not a sentence worth showing.
    Anything sympy cannot solve reads as no roots, because this is a hint, and
    a hint that raises is worse than no hint.
    """
    try:
        if not expression.has(symbol):
            return []
        found = sp.solve(sp.Eq(expression, 0), symbol, dict=False)
    except Exception:
        return []
    if not isinstance(found, (list, tuple)):
        found = [found]
    kept = []
    for root in found:
        root = sp.simplify(root)
        if root.is_number and root.is_real:
            kept.append(root)
    return kept


def grade_numeric(question, text: str) -> tuple[bool | None, str]:
    """Mark a typed number against the one a `Numeric` question expects.

    Here rather than beside `model.grade_choice` because it needs the parser,
    and `lessons/` is content that holds no sympy -- the same layering that
    makes `Lesson.figure` a string rather than a widget. `grade_choice` needs
    nothing and can therefore live with the model; this cannot.

    The text goes through `_parse_side`, the same hardened parser the rest of
    the application uses, so ``11/10``, ``sqrt(2)`` and ``-4.9e1`` all work and
    nothing with a name in it does. Somebody who worked the arithmetic out as a
    fraction should not have to convert it first.

    Returns `None` -- *cannot decide* -- for anything that will not parse or
    does not come out as a real number, never `False`. That is the discipline
    `check_answer` already keeps: a verdict of wrong is a claim about the
    mathematics, and "I could not read that" is a claim about the typing.

    The comparison is relative to the size of the answer, with an absolute
    floor, so one tolerance means the same thing for a terminal velocity of
    -49 and for a step of 0.0039.
    """
    if not text or not text.strip():
        return None, "type a number to check"

    try:
        value = _parse_side(text.strip(), {})
    except ParseError as exc:
        return None, str(exc)

    if value.free_symbols:
        names = ", ".join(sorted(map(str, value.free_symbols)))
        if value.is_Symbol:
            return None, f"{names!r} is not a number"
        return None, f"that still has {names} in it"

    try:
        got = complex(value.evalf())
    except (TypeError, ValueError) as exc:
        return None, f"that is not a number: {exc}"
    if abs(got.imag) > 1e-12:
        return None, "that is a complex number; this question wants a real one"

    wanted = float(question.answer)
    allowed = question.tolerance * max(1.0, abs(wanted))
    if abs(got.real - wanted) <= allowed:
        return True, f"correct: {_tidy_number(wanted)}"
    for value, cause in getattr(question, "mistakes", ()):
        if abs(got.real - value) <= question.tolerance * max(1.0, abs(value)):
            return False, (f"not quite -- {_tidy_number(value)} is what you "
                           f"get if {cause}. The answer is "
                           f"{_tidy_number(wanted)}")
    return False, f"not quite -- the answer is {_tidy_number(wanted)}"


# ---------------------------------------------------------------------------
# Checking an equation, and checking one move of a method
# ---------------------------------------------------------------------------


@dataclass
class EquivalenceCheck:
    """The verdict on an equation, or on one intermediate expression.

    `check_answer` grades a *solution* by substituting it into the equation,
    which is the strongest check there is and needs nothing stored. Two kinds
    of question cannot be graded that way, because what they ask for is not a
    solution:

    * **write the equation** -- for a situation described in words, or for a
      family of curves. There is nothing to substitute it into; the equation
      *is* the answer.
    * **write one move of the method** -- the integrating factor, the
      characteristic polynomial, the Wronskian, the transform of the forcing
      term. Again not a solution, and again nothing to substitute into.

    Both come down to the same question -- are these two pieces of mathematics
    the same? -- so both use the same verdict, and it keeps the same three
    values `AnswerCheck` does. `None` is *cannot tell*, never *wrong*.
    """

    #: What was parsed, or None if it could not be.
    expression: sp.Expr | None = None
    #: True when the two were proved the same, False when they were proved
    #: different, None when neither could be shown. See `_same_expression`.
    correct: bool | None = None
    #: The constant multiple relating what was typed to what was wanted, where
    #: the question allows one and one was found. ``1`` when they are equal
    #: outright.
    factor: sp.Expr | None = None
    #: What is left when the answer is subtracted from the expected one, for a
    #: wrong answer that could be lined up with it. This is the useful half of
    #: a wrong verdict: a forgotten inflow term or a sign that went the other
    #: way appears here by itself.
    difference: sp.Expr | None = None
    message: str = ""

    @property
    def ok(self) -> bool:
        return bool(self.correct)


#: Values substituted when simplification will not decide. Rationals rather
#: than floats, so the arithmetic stays exact, and none of them 0, 1 or -1:
#: those are the points at which a wrong answer is most likely to agree with a
#: right one by accident.
_PROBE_VALUES = (
    sp.Rational(2, 3), sp.Rational(7, 5), sp.Rational(-3, 4),
    sp.Rational(5, 2), sp.Rational(-11, 7), sp.Rational(9, 4),
    sp.Rational(3, 8), sp.Rational(-6, 5),
)

#: How many points to try. Two are enough to refute a constant multiple; the
#: rest are there because a point can be unusable -- the expected expression
#: can vanish at it, or fail to evaluate.
_PROBE_ROUNDS = 5


def _probe_at(symbols: list, round_index: int) -> dict:
    """One point: a rational for every symbol, chosen without a pattern."""
    return {
        symbol: _PROBE_VALUES[(3 * round_index + 5 * position)
                              % len(_PROBE_VALUES)]
        for position, symbol in enumerate(symbols)
    }


def _exactly(expression):
    """The same expression with its decimals read as exact rationals."""
    try:
        return sp.nsimplify(expression, rational=True)
    except Exception:
        return expression


def _vanishes(expression) -> bool:
    """Whether `expression` simplifies to exactly zero. Never raises."""
    try:
        return bool(sp.simplify(expression) == 0)
    except Exception:
        return False


def _apart(left, right) -> bool:
    """Whether two numbers are *definitely* different.

    Numeric, and deliberately so: this is the refuting half of the check, and
    what it needs is to be sure rather than to be exact. The threshold is
    relative, and four orders of magnitude looser than the error either side
    can carry, so it separates a wrong answer from a right one without ever
    separating a right one from itself.
    """
    try:
        gap = complex(sp.N(left - right))
        scale = max(1.0, abs(complex(sp.N(left))), abs(complex(sp.N(right))))
    except (TypeError, ValueError):
        return False
    return abs(gap) > 1e-9 * scale


def _same_expression(student, reference, *, up_to_factor: bool):
    """Whether two expressions are the same, up to a constant if allowed.

    Both verdicts are proofs, and that is the design. **Right** is proved
    symbolically: the difference simplifies to exactly zero. **Wrong** is
    proved by evaluation: two expressions that agree everywhere agree at every
    point, so one point where they differ settles it -- and where a constant
    multiple is allowed, two points whose ratios differ settle it just as
    firmly, because a constant is the same constant everywhere. Anything else
    is *cannot tell*, which is the verdict `check_answer` already gives when
    simplification will not decide, and for the same reason: failing to
    simplify is not evidence of anything.

    The constant multiple matters for both kinds of question this serves. An
    equation multiplied through by 20 is the same equation, and an integrating
    factor is only ever determined up to a constant -- ``e^{3t}`` and
    ``5e^{3t}`` both work, and marking the second wrong would be teaching
    something false.

    Returns ``(verdict, factor)``.
    """
    # Decimals first, and this is not cosmetic. A reference equation written
    # with 9.8 in it and an answer written with 9.8 in it are two different
    # binary approximations the moment either is scaled, so the difference
    # comes out as 7e-15 rather than as zero and a correct answer is reported
    # as "cannot tell". `nsimplify` reads a decimal as the exact rational it
    # was written as -- 9.8 is 49/5 -- and the arithmetic is exact again.
    student, reference = _exactly(student), _exactly(reference)
    symbols = sorted(student.free_symbols | reference.free_symbols, key=str)

    if _vanishes(student - reference):
        return True, sp.Integer(1)

    ratios = []
    for round_index in range(_PROBE_ROUNDS):
        point = _probe_at(symbols, round_index)
        try:
            here = sp.simplify(student.subs(point))
            there = sp.simplify(reference.subs(point))
        except Exception:
            continue
        if here.free_symbols or there.free_symbols:
            continue                       # a symbol nothing substituted for
        if not up_to_factor:
            if _apart(here, there):
                return False, None
            continue
        if there == 0:
            continue                       # nothing to take a ratio against
        try:
            ratios.append(sp.simplify(here / there))
        except Exception:
            continue

    if not up_to_factor:
        return None, None

    if not ratios:
        return None, None
    factor = ratios[0]
    if any(_apart(other, factor) for other in ratios[1:]):
        return False, None                 # not one constant, so not a multiple
    if factor == 0:
        return False, None                 # vanishes where the answer does not
    if _vanishes(student - factor * reference):
        return True, factor
    return None, None


def _strip_label(text: str, wanted) -> str:
    """Drop a leading ``mu =`` from an answer that is an expression.

    Somebody writing down an integrating factor writes ``mu = e^{3t}``, and
    somebody writing down a characteristic equation writes ``r^2 + 3r + 2 =
    0``. Both have an equals sign in them and they mean opposite things by it:
    the first is a label on an expression, the second is half of what was
    asked for.

    The rule that separates them: a left-hand side that is a bare name the
    expected answer never mentions is a label, and anything else is
    mathematics. So ``mu`` goes (the answer is in `t`), ``r^2 + 3r + 2`` stays,
    and ``r`` would stay too, because an answer written in `r` uses it.
    """
    text = text.strip()
    if text.count("=") != 1:
        return text
    left, right = (part.strip() for part in text.split("="))
    named = {str(symbol) for symbol in wanted.free_symbols}
    if re.fullmatch(r"[A-Za-z]\w*(\s*\(\s*\w+\s*\))?", left) and left not in named:
        return right
    return f"({left}) - ({right})"


def check_expression(reference: str, text: str, *,
                     up_to_constant: bool = False) -> EquivalenceCheck:
    """Mark an expression written for one move of a method.

    The integrating factor, the characteristic polynomial, the Wronskian, the
    transform of a forcing term: each is a step a course asks for by itself,
    and none of them is a solution, so `check_answer` has nothing to substitute
    it into. What there is instead is the expression the step should produce,
    and this compares the two.

    `up_to_constant` is not a leniency. An integrating factor is determined
    only up to a constant multiple and a characteristic equation only up to a
    scaling, so where it is set, accepting ``2e^{3t}`` is the mathematics
    rather than a kindness -- and where it is not set, a constant multiple is a
    different answer and is marked as one.

    The text goes through `_parse_side`, the same hardened parser as every
    other route from a typed string into sympy, and every symbol the expected
    answer uses is bound to the same object, so an answer written in `r` or `s`
    is compared against the same `r` or `s` rather than a fresh one.
    """
    if not text or not text.strip():
        return EquivalenceCheck(message="type an expression to check")

    scope: dict = {"t": _T}
    try:
        wanted = _parse_side(reference, scope)
    except ParseError as exc:               # a broken question, not an answer
        return EquivalenceCheck(message=f"this question could not be set up: {exc}")
    for symbol in wanted.free_symbols:
        if symbol.is_Symbol:
            scope.setdefault(symbol.name, symbol)

    try:
        # Through `_insert_multiplication` for the same reason `parse_equation`
        # uses it: a student writes ``3r`` and ``2(t+1)``, and a grader that
        # refused those would be marking the typing rather than the
        # mathematics. `^` needs no help -- `convert_xor` is already one of the
        # parser's transformations.
        candidate = _parse_side(
            _insert_multiplication(_strip_label(text, wanted)), scope
        )
    except ParseError as exc:
        return EquivalenceCheck(message=str(exc))

    check = EquivalenceCheck(expression=candidate)
    verdict, factor = _same_expression(candidate, wanted,
                                       up_to_factor=up_to_constant)
    check.correct, check.factor = verdict, factor
    if verdict is True and factor is not None and factor != 1:
        check.message = f"correct -- {factor} times the usual form, which works"
    elif verdict is True:
        check.message = "correct"
    elif verdict is False:
        check.difference = _difference(candidate, wanted, factor)
        check.message = "not the expression this step produces"
    else:
        check.message = "could not tell whether that is the same expression"
    return check


def _difference(candidate, wanted, factor):
    """What is left when the answer is taken from the expected one.

    Shown with a wrong verdict, and it is the half of that verdict worth
    reading: a forgotten term appears here by itself, and a sign that went the
    wrong way appears as twice the term it belongs to.
    """
    try:
        # `expand` rather than `simplify`: this is read, and simplify likes to
        # be clever -- it returns the difference of two exponentials as a
        # hyperbolic sine, which is true and tells nobody which term went
        # astray.
        return sp.expand(candidate - (factor or 1) * wanted)
    except Exception:
        return None


def check_model(reference: str, text: str) -> EquivalenceCheck:
    """Mark an equation somebody wrote for a situation, or for a family.

    Two question types land here and they are the same question asked from
    either end. *A tank holds 100 litres of brine...* asks the student to
    turn a situation into an equation; *every curve in the family
    ``y = C e^{3t}`` solves one first-order equation* asks them to turn
    solutions back into the equation they came from. Neither can be graded by
    substitution, because in both the equation is the answer rather than the
    question.

    What makes it gradeable anyway is that an equation has a canonical thing to
    compare: move everything to one side and two equations are the same exactly
    when the two sides agree up to a nonzero constant multiple. ``y' = 2 -
    y/20``, ``y' + y/20 = 2`` and ``20y' + y = 40`` are one equation and all
    three are accepted; nothing is marked wrong for being arranged differently.

    A constant multiple only. Multiplying through by `t` also leaves an
    equation with the same solutions where `t` is not zero, and a different one
    where it is -- so that is not accepted, and the difference is shown instead
    of a bare refusal.
    """
    if not text or not text.strip():
        return EquivalenceCheck(message="type an equation to check")
    if "=" not in text:
        return EquivalenceCheck(
            message="write the whole equation, with an = in it"
        )

    try:
        wanted = parse_equation(spec_for(reference))
    except Exception as exc:                # a broken question, not an answer
        return EquivalenceCheck(
            message=f"this question could not be set up: {exc}"
        )

    expected = {function.__name__ for function in wanted.functions}
    unknowns = ", ".join(sorted(expected))
    # Checked before parsing, because an unexpected prime does not survive it:
    # `spec_for` reads a scalar equation as one in `y`, so ``x' = 3x`` reaches
    # the parser with the prime still attached and comes back as a quotation
    # mark somebody forgot to close, which is a true statement about Python
    # and no help at all.
    primed = set(re.findall(r"([A-Za-z]\w*)\s*(?:'+|\^\s*\(\s*\d+\s*\))",
                            text))
    if primed and not primed <= expected:
        return EquivalenceCheck(
            message=f"write it in terms of {unknowns}, as the question does"
        )

    try:
        written = parse_equation(spec_for(text.strip()))
    except ParseError as exc:
        return EquivalenceCheck(message=str(exc))
    except Exception as exc:
        return EquivalenceCheck(message=f"cannot read that: {exc}")

    order = max(written.order, wanted.order)
    left = _flatten(written.equation, written.functions, order)
    right = _flatten(wanted.equation, wanted.functions, order)
    if right.free_symbols and not (left.free_symbols & right.free_symbols):
        return EquivalenceCheck(
            message=f"write it in terms of {unknowns}, as the question does"
        )

    check = EquivalenceCheck(expression=left)
    verdict, factor = _same_expression(left, right, up_to_factor=True)
    check.correct, check.factor = verdict, factor
    if verdict is True and factor is not None and factor != 1:
        check.message = (
            f"correct -- {factor} times the equation as usually written, "
            "which is the same equation"
        )
    elif verdict is True:
        check.message = "correct: that is the equation"
    elif verdict is False:
        multiple = _multiple_of(left, right)
        if multiple is not None:
            check.message = (
                f"that is the right equation multiplied through by {multiple}, "
                "which is not the same equation -- it says nothing where that "
                "is zero"
            )
        else:
            check.difference = _difference(left, right, factor)
            check.message = "that is not the same equation"
    else:
        check.message = "could not tell whether that is the same equation"
    return check


@dataclass(frozen=True)
class Marking:
    """What an `EquivalenceCheck` says to the person who typed the answer.

    Decided here, once, rather than on each screen. It was written out three
    times -- the lesson drill's model and expression cards and the quiz -- and
    by the time the third copy existed the three disagreed: a wrong
    *expression* in a lesson showed the question's `because`, which states the
    rule and very nearly the answer, while a wrong *model* in the same lesson
    and anything wrong in the quiz did not. The rule is now the model card's,
    because it is the one that keeps a retry a question:

    * right -- the `because`, which is the reason it is right;
    * wrong -- what differs, when the two could be lined up, and nothing else;
    * cannot tell -- the message only, and it is not a mark.
    """

    #: "right", "wrong" or "undecided". A screen maps these to its colours.
    tone: str
    #: The verdict line, with its tick or cross.
    headline: str
    #: A second line under it, or "".
    detail: str = ""

    @property
    def counts(self) -> bool:
        """Whether this was a mark at all. "Could not read that" is not."""
        return self.tone != "undecided"


def mark_equivalent(question, typed: str) -> tuple[EquivalenceCheck, Marking]:
    """Grade a `Model` or an `Expression` question and say what it means."""
    if question.kind == "model":
        result = check_model(question.equation, typed)
    else:
        result = check_expression(question.answer, typed,
                                  up_to_constant=question.up_to_constant)
    because = getattr(question, "because", "")
    if result.correct is True:
        marking = Marking("right", "✓ " + result.message, because)
    elif result.correct is False:
        detail = (f"what differs: {result.difference}"
                  if result.difference is not None else "")
        marking = Marking("wrong", "✗ " + result.message, detail)
    else:
        marking = Marking("undecided", result.message)
    return result, marking


def _multiple_of(written, wanted):
    """The non-constant factor relating two equations, when there is one.

    Dividing ``y' = 3y`` through by `y` gives ``y'/y = 3``, which has the same
    solutions everywhere except where `y` vanishes -- and ``y = 0`` *is* a
    member of the family the first equation describes. So it is not the same
    equation, and saying only "not the same equation" would leave somebody who
    did the algebra correctly with nothing to go on. Naming the factor says
    exactly which step went one step too far.
    """
    try:
        ratio = sp.cancel(sp.simplify(written / wanted))
    except Exception:
        return None
    if not ratio.free_symbols:
        return None
    # Any two expressions are multiples of each other by their own ratio, so
    # the factor is only worth naming when it is something somebody could have
    # multiplied by: a symbol, a power, a product of those. A ratio with a sum
    # anywhere inside it is the arithmetic of two unrelated equations, and
    # printing it would dress a plain wrong answer up as a near miss.
    if ratio.atoms(sp.Add):
        return None
    return ratio if _vanishes(written - ratio * wanted) else None


def _flatten(equation: sp.Eq, functions: list, order: int):
    """One side of an equation, with the unknowns turned into plain symbols.

    ``y'' + 3y' + 2y - t`` as a polynomial in three ordinary symbols, so it can
    be substituted into and compared like any other expression. Highest
    derivative first, because replacing ``y(t)`` before ``y''(t)`` would leave
    a derivative of a symbol behind.
    """
    flat = equation.lhs - equation.rhs
    for function in functions:
        name = function.__name__
        for degree in range(order, 0, -1):
            flat = flat.subs(sp.Derivative(function(_T), (_T, degree)),
                             sp.Symbol(_written(name, degree)))
        flat = flat.subs(function(_T), sp.Symbol(name))
    return sp.expand(flat)


def _written(name: str, degree: int) -> str:
    """``y''`` for the second derivative: what the symbol is called on paper.

    The names matter because these symbols are shown. A wrong answer's verdict
    prints what is left over, and ``-y/10`` says which term went astray while
    ``-__y_0/10`` says only that something internal leaked out.
    """
    if degree <= 3:
        return name + "'" * degree
    return f"{name}^({degree})"


def _tidy_number(value: float) -> str:
    """A number as it would be written, not as a float repr.

    ``0.5`` rather than ``0.5000000000000001``, and ``-49`` rather than
    ``-49.0``: the verdict is read, and a tail of noise in it reads as though
    the application is unsure of its own answer.
    """
    rounded = round(value, 6)
    if abs(rounded - round(rounded)) < 1e-9:
        return str(int(round(rounded)))
    return f"{rounded:g}"


def _check_system(parsed: ParsedEquation, text: str) -> AnswerCheck:
    """The same substitution check, component by component.

    A system's answer is several functions rather than one, so it is typed as
    several lines -- ``x = ...`` on one and ``y = ...`` on the next -- and each
    is substituted into *every* equation at once. That last part is the whole
    difficulty: a pair can satisfy the first equation and fail the second, and
    checking them one at a time would miss it.

    Every line has to name its unknown. Guessing the order from the order they
    were typed would silently mark a correct answer wrong for someone who
    wrote them the other way round, which is the failure this check exists to
    avoid making.
    """
    try:
        candidates = dict(read_answer(parsed, text))
    except ParseError as exc:
        return AnswerCheck(message=str(exc))
    names = {function.__name__: function for function in parsed.functions}

    substitutions = {names[name](_T): expression
                     for name, expression in candidates.items()}
    check = AnswerCheck(expression=sp.Matrix(
        [candidates[function.__name__] for function in parsed.functions]
    ))
    try:
        residuals = [
            sp.simplify((equation.lhs - equation.rhs).subs(substitutions).doit())
            for equation in parsed.equations
        ]
        check.residual = sp.Matrix(residuals)
        # Every equation, not merely the first: a pair that solves one and not
        # the other is exactly the near-miss worth catching.
        check.correct = all(sp.simplify(residual) == 0 for residual in residuals)
    except Exception as exc:
        check.message = f"could not decide: {exc}"
        return check

    if check.correct and parsed.ics:
        check.matches_conditions = _system_matches_conditions(parsed, candidates)

    if check.correct is False:
        check.message = "substituting it does not give zero in every equation"
    elif check.matches_conditions is False:
        check.message = "it solves the system, but not with these conditions"
    else:
        check.message = "verified: every equation gives exactly zero"
    check.diagnosis = diagnose(parsed, check)
    return check


def _system_matches_conditions(parsed: ParsedEquation,
                               candidates: dict) -> bool | None:
    """Whether the typed components also meet ``x(0) = ...``."""
    try:
        for condition, value in parsed.ics.items():
            function = getattr(condition, "func", None)
            name = getattr(function, "__name__", None)
            if name not in candidates:
                return None
            point = condition.args[0]
            if point.free_symbols:
                return None
            left = sp.simplify(candidates[name].subs(_T, point) - sp.sympify(value))
            if sp.simplify(left) != 0:
                return False
        return True
    except Exception:
        return None


def _satisfies_conditions(parsed: ParsedEquation, candidate: sp.Expr) -> bool | None:
    """Whether `candidate` also meets the initial conditions, if it can be told.

    The conditions come back from parsing in two shapes and both have to be
    handled: a value condition is the applied function ``y(0)``, while a
    derivative condition is ``Subs(Derivative(y(t), t), t, 0)``. Reading only
    the first would silently evaluate every derivative condition at the wrong
    point and at order zero -- which reports a *correct* answer as wrong, the
    worst thing this check could do.
    """
    try:
        for condition, value in parsed.ics.items():
            order, point = _condition_at(condition)
            if point is None:
                return None
            expression = candidate
            if order:
                expression = sp.diff(candidate, _T, order)
            if sp.simplify(expression.subs(_T, point) - value) != 0:
                return False
        return True
    except Exception:
        return None


def _condition_at(condition) -> tuple[int, object | None]:
    """``(derivative order, point)`` for an initial-condition key."""
    if isinstance(condition, sp.Subs):
        inner = condition.expr
        order = 0
        if isinstance(inner, sp.Derivative):
            order = sum(int(count) for _, count in inner.variable_count)
        point = condition.point[0] if condition.point else None
        return order, point
    if isinstance(condition, sp.Derivative):
        order = sum(int(count) for _, count in condition.variable_count)
        args = condition.expr.args if hasattr(condition, "expr") else ()
        return order, (args[0] if args else None)
    # An applied function: `y(0)`.
    args = getattr(condition, "args", ())
    return 0, (args[0] if args else None)


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
