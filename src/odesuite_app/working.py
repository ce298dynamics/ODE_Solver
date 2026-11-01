"""Checking a student's working line by line, not just the answer at the end.

A wrong final answer says that something went wrong. Which line it went wrong
on is the thing worth knowing, and the thing a marker writes in the margin.

**The approach.** Each line is checked against the *verified solution
family* rather than against the line before it. Line-to-line equivalence breaks
the moment a constant of integration appears -- ``e^(2t) y = 2e^(2t) + C`` is
not equivalent to anything before it, it is a new statement with a new
unknown in it -- and matching the narrator's own LaTeX would mark every
student who took a different, equally good route. Instead a line is a claim
about the solution, and the claim is tested:

* A **relation** in y -- ``y' + 2y = 4``, ``(e^(2t) y)' = 4e^(2t)``,
  ``ln|y| = 2t + C`` -- is substituted with the general solution
  ``y(t; K)``. If, for every member of the family, the student's own
  constants can be chosen to make it hold, it is ✓. Their constants must enter
  linearly, which is how they enter in a first course; otherwise the line is
  "unchecked", never ✗.
* If it holds only for one member, and the question had no conditions to
  pick that member out, a constant was lost on the way.
* A **definition** of the integrating factor is compared with ``exp(∫p)`` up
  to a constant factor; a **characteristic polynomial** with the equation's
  own, up to a factor; **roots** by substituting them in.
* The **final** ``y = ...`` goes through `symbolic.check_answer`, so the
  verdict at the bottom of the working is the verdict the answer box gives.

Everything is decided numerically at probe points, without `simplify`: a
probe that disproves a line is a proof it is wrong, and nothing is marked ✗
without one. A line that cannot be read, or cannot be decided, says so and
the rest are still checked.

No Qt here: the screen runs this on a worker thread and the tests call it
directly.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass

import numpy as np
import sympy as sp

from .custom import ParseError
from .symbolic import (
    _T,
    ParsedEquation,
    _answer_scope,
    _answer_text,
    _friendly_parse_error,
    _parse_side,
    _rewrite_derivatives,
    _token,
    analyse_linear,
    check_answer,
)

__all__ = ["LineVerdict", "available", "check_working", "OK", "WRONG",
           "UNCHECKED", "UNREADABLE"]

OK, WRONG, UNCHECKED, UNREADABLE = "ok", "wrong", "unchecked", "unreadable"

#: The names a student calls the integrating factor by.
_FACTOR_NAMES = {"mu", "μ", "u", "I", "IF", "rho", "ρ"}

#: Leading words that join one line to the last and say nothing themselves.
_LEADERS = re.compile(
    r"^\s*(?:=>|⇒|->|→|∴|so\b|hence\b|then\b|therefore\b|thus\b)\s*",
    re.IGNORECASE,
)

#: Times at which a line is tested, kept away from t = 0 where 1/t and ln t
#: live, and spread so that two of them agreeing is not a coincidence.
_TIMES = (0.31, 0.74, 1.13, 1.58, 2.27, 0.46, 0.93, 1.36, 1.87, 0.62)

#: Values for the family's constants: positive, so ln|...| of a member and
#: ln of it agree, and irregular, so that no member is special.
_MEMBERS = ((0.73, 1.41), (1.9, 0.57), (2.6, 1.17))

#: Stands in for d/dt( until after parsing. Lower case and z-heavy, so it can
#: never be split into a product of names a line may use.
_MARK = "zzddtzz"


@dataclass(frozen=True)
class LineVerdict:
    """One line of working and what was found about it."""

    number: int
    text: str
    status: str
    message: str = ""


def available(parsed: ParsedEquation, narrator: str) -> tuple[bool, str]:
    """Whether working can be checked for this equation, and if not, why."""
    reason = ("Checking working is not available for this kind of equation "
              "yet -- first-order linear, separable, constant-coefficient "
              "second-order, Laplace-transform and 2×2 linear-system "
              "questions only.")
    if parsed.is_system:
        from .systems import split_system

        if narrator != "systems" or len(parsed.functions) != 2 \
                or split_system(parsed.equations, parsed.functions) is None:
            return False, reason
        return True, ""
    if narrator == "laplace":
        # The method needs the conditions, and its working is in s.
        if not parsed.ics:
            return False, reason
        return True, ""
    if narrator != "steps" or parsed.order > 2:
        return False, reason
    if parsed.order == 2:
        analysis = analyse_linear(parsed.equation, parsed.function, 2)
        if not analysis.get("constant_coefficients"):
            return False, reason
    return True, ""


# ---------------------------------------------------------------------------
# Reading a line
# ---------------------------------------------------------------------------


def _strip(text: str) -> str:
    text = text.split("#", 1)[0]
    while True:
        shorter = _LEADERS.sub("", text, count=1)
        if shorter == text:
            break
        text = shorter
    return (text.replace("−", "-").replace("·", "*").replace("×", "*")
            .replace("′", "'").strip())


def _wrap_primes(text: str) -> str:
    """``(e^(2t) y)'`` -> ``zzddtzz(e^(2t) y)``, innermost first."""
    while True:
        at = re.search(r"\)\s*'", text)
        if at is None:
            return text
        close = at.start()
        depth = 0
        for open_ in range(close, -1, -1):
            depth += {")": 1, "(": -1}.get(text[open_], 0)
            if depth == 0:
                break
        else:
            return text                       # unbalanced: let parsing fail
        text = (text[:open_] + _MARK + text[open_:close + 1]
                + text[at.end():])


def _normalise(text: str, name: str) -> str:
    """The notations of a page of working, turned into the parser's."""
    # y(t) and y'(t) are y and y'.
    text = re.sub(rf"\b({re.escape(name)}(?:')*)\s*\(\s*t\s*\)", r"\1", text)
    # Leibniz: d²y/dt², d^2y/dt^2, dy/dt, d/dt(...).
    text = re.sub(rf"d\s*\^?\s*2\s*{re.escape(name)}\s*/\s*d\s*t\s*\^?\s*2",
                  f"{name}''", text)
    text = re.sub(rf"d\s*{re.escape(name)}\s*/\s*d\s*t\b", f"{name}'", text)
    text = re.sub(r"d\s*/\s*d\s*t\s*\(", f"{_MARK}(", text)
    # |x| is Abs(x), bracketed so that ln|y| is ln(Abs(y)), not a name lnAbs.
    while True:
        replaced = re.sub(r"\|([^|]*)\|", r"(Abs(\1))", text)
        if replaced == text:
            break
        text = replaced
    text = _wrap_primes(text)
    # y' y is a product: a prime ends an operand.
    return re.sub(r"'(?=\s*[A-Za-z0-9_(])", "'*", text)


class _Reader:
    """Parses lines in the setting of one equation."""

    def __init__(self, parsed: ParsedEquation) -> None:
        self.parsed = parsed
        self.name = parsed.function.__name__
        self.parameters = {s for s in parsed.equation.free_symbols
                           if s.is_Symbol and s != _T}
        self.scope = _answer_scope(self.parameters)
        self.scope[self.name] = sp.Symbol("__plain_y")    # replaced below
        self.marker = sp.Function("__ddt")
        self.scope[_MARK] = self.marker
        for order in range(parsed.order + 3):
            self.scope[_token(self.name, order)] = sp.Symbol(
                f"__{self.name}_{order}")
        # Single capital letters are constants a student may name: A, B, K.
        self.constants = {letter for letter in "ABCDFGHJKLMNPQRSUVW"}
        for letter in self.constants:
            self.scope.setdefault(letter, sp.Symbol(letter))

    def expression(self, text: str, extra: dict | None = None) -> sp.Expr:
        original = text
        scope = {**self.scope, **(extra or {})}
        known = (set(scope) - {_MARK}) | {"pi", "E"}
        text = _answer_text(_normalise(text, self.name), known)
        text, _ = _rewrite_derivatives(text, self.name)
        try:
            parsed = _parse_side(text, scope)
        except ParseError as exc:
            # The parser's own message quotes the rewritten text, placeholder
            # tokens and all, which would mean nothing to the reader.
            raise ParseError(_friendly_parse_error(original).replace(
                "cannot parse that: ", "") or "check the brackets and the "
                "operators") from exc
        function = self.parsed.function(_T)
        substitutions = {sp.Symbol(f"__{self.name}_{k}"): function.diff(_T, k)
                         if k else function for k in range(self.parsed.order + 3)}
        substitutions[sp.Symbol("__plain_y")] = function
        expression = parsed.subs(substitutions)
        return expression.replace(
            lambda e: isinstance(e, sp.core.function.AppliedUndef)
            and e.func.__name__ == "__ddt",
            lambda e: sp.diff(e.args[0], _T),
        )


# ---------------------------------------------------------------------------
# Numbers
# ---------------------------------------------------------------------------


def _numeric(expression, symbols):
    """A numpy function of `symbols`, evaluated in complex arithmetic."""
    function = sp.lambdify(symbols, expression, "numpy")

    def call(*values):
        with np.errstate(all="ignore"):
            try:
                return complex(function(*[complex(v) for v in values]))
            except (ZeroDivisionError, OverflowError, TypeError, ValueError):
                return complex("nan")
    return call


def _close(left: complex, right: complex) -> bool:
    return abs(left - right) <= 1e-7 * max(1.0, abs(left), abs(right))


def _finite(*values: complex) -> bool:
    return all(np.isfinite(v.real) and np.isfinite(v.imag) for v in values)


def _holds(lhs, rhs, unknowns: list) -> bool | None:
    """Whether some values of `unknowns` make ``lhs = rhs`` for every t.

    The unknowns must enter linearly; if they visibly do not, None. The fit
    is made at a few times and verified at the rest. None, too, when too few
    times give finite values to decide anything.
    """
    symbols = [_T, *unknowns]
    left, right = _numeric(lhs, symbols), _numeric(rhs, symbols)

    def gap(t, values):
        return left(t, *values) - right(t, *values)

    count = len(unknowns)
    zero = [0.0] * count
    if count:
        # Linearity: the gap at 2e_j is twice its change at e_j, and the
        # changes for two unknowns add.
        probe = _TIMES[0]
        base = gap(probe, zero)
        units = []
        for j in range(count):
            unit = [0.0] * count
            unit[j] = 1.0
            units.append(gap(probe, unit) - base)
            twice = [0.0] * count
            twice[j] = 2.0
            if not _finite(base, units[-1]) or not _close(
                    gap(probe, twice) - base, 2 * units[-1]):
                return None
        if count > 1 and not _close(gap(probe, [1.0] * count) - base,
                                    sum(units)):
            return None

    fit_times = _TIMES[: count + 2]
    if count:
        rows, targets = [], []
        for t in fit_times:
            base = gap(t, zero)
            row = []
            for j in range(count):
                unit = [0.0] * count
                unit[j] = 1.0
                row.append(gap(t, unit) - base)
            if not _finite(base, *row):
                continue
            rows.append(row)
            targets.append(-base)
        if len(rows) < count:
            return None
        values = np.linalg.lstsq(np.array(rows), np.array(targets),
                                 rcond=None)[0]
    else:
        values = np.array([])

    checked = 0
    trivial = True
    for t in _TIMES:
        args = [*values]
        lv, rv = left(t, *args), right(t, *args)
        if not _finite(lv, rv):
            continue
        checked += 1
        if not _close(lv, rv):
            return False
        trivial = trivial and max(abs(lv), abs(rv)) < 1e-9
    if trivial and count:
        # Made true only by choosing a constant that zeroes both sides --
        # `d y = d t` with d = 0 -- which says nothing about the solution.
        return None
    return True if checked >= 4 else None


def _some_member(lhs, rhs, unknowns: list) -> bool:
    """Whether *some* choice of `unknowns` makes ``lhs = rhs`` for every t.

    Solved numerically at as many times as there are unknowns, from a few
    starting points, then verified at the rest. The family's constants enter
    however the narrator wrote them -- ``exp(-2C)`` as often as ``C`` -- so
    this cannot be a linear fit. False when nothing is found, which here
    only means "no member was found", never a verdict on its own.
    """
    if not unknowns:
        return False
    gap = lhs - rhs
    times = _TIMES[: len(unknowns)]
    system = [gap.subs(_T, t) for t in times]
    left, right = _numeric(lhs, [_T, *unknowns]), _numeric(rhs, [_T, *unknowns])
    for start in (0.5, 1.2, -0.7, 2.5):
        try:
            found = sp.nsolve(system, unknowns, [start] * len(unknowns))
        except Exception:
            continue
        values = [complex(v) for v in found]
        checked = 0
        for t in _TIMES:
            lv, rv = left(t, *values), right(t, *values)
            if not _finite(lv, rv):
                continue
            checked += 1
            if not _close(lv, rv):
                break
        else:
            if checked >= 4:
                return True
    return False


def _substitute(relation, function, solution):
    """`relation` with ``y(t)`` and its derivatives replaced by `solution`."""
    unknown = function(_T)
    highest = max([d.derivative_count for d in relation.atoms(sp.Derivative)
                   if d.expr == unknown] + [0])
    substitutions = {unknown.diff(_T, k): sp.diff(solution, _T, k)
                     for k in range(highest, 0, -1)}
    return relation.subs(substitutions).subs(unknown, solution).doit()


# ---------------------------------------------------------------------------
# The check
# ---------------------------------------------------------------------------


def check_working(parsed: ParsedEquation, text: str, general, particular=None,
                  *, budget: float = 6.0,
                  narrator: str = "steps") -> list[LineVerdict]:
    """A verdict per non-empty line of `text`.

    `general` is the verified general solution, with sympy's ``C1``, ``C2``;
    `particular` the solution meeting the question's conditions, when it has
    any. Lines after `budget` seconds are left "unchecked" rather than
    holding the screen up.

    A system's general solution is a column, one entry per unknown, and its
    working is checked by `_check_system`. Under the Laplace `narrator` lines
    in s are checked against the transform of `particular`; a Laplace
    solution has no free constants, so `general` may be `particular` itself.
    """
    if parsed.is_system:
        return _check_system(parsed, text, general, particular, budget)
    transform = (_Transform(parsed, particular)
                 if narrator == "laplace" and particular is not None else None)
    reader = _Reader(parsed)
    parameters = sorted(reader.parameters, key=str)
    # Every free symbol of the family that is not t or a parameter is one of
    # its constants -- the narrator writes `C` as often as `C1`, and inside
    # an exponential as often as in front of one. Renamed, so the student's
    # own `C` is never mistaken for it.
    family_constants = sorted(general.free_symbols - {_T} - set(parameters),
                              key=lambda s: s.name)
    members = [sp.Dummy(f"K{i}") for i in range(len(family_constants))]
    family = general.subs(dict(zip(family_constants, members)),
                          simultaneous=True)
    linear = _is_linear(parsed)
    if linear and members:
        # A linear equation's solutions are an affine space, however the
        # narrator wrote them: one member plus any combination of the
        # differences. Rewritten that way the constants enter linearly and
        # every member is reachable -- `exp(-2C - 2t)/2 + 2` never reaches
        # y = 2, and `2 + A e^(-2t)` does at A = 0.
        anchor = {member: sp.Rational(1, 3) for member in members}
        base = family.subs(anchor)
        basis = [family.subs({**anchor, member: sp.Rational(4, 3)}) - base
                 for member in members]
        family = base + sum(member * vector
                            for member, vector in zip(members, basis))
    # A parameter left in -- a slider's value -- is fixed for the check.
    fixed = {symbol: 1.3 + 0.2 * index for index, symbol in enumerate(parameters)}

    lines = [(number, raw) for number, raw in enumerate(text.splitlines(), 1)
             if _strip(raw)]
    final = lines[-1][0] if lines else 0
    started = time.monotonic()
    verdicts: list[LineVerdict] = []
    last_good = 0
    for number, raw in lines:
        if time.monotonic() - started > budget:
            verdicts.append(LineVerdict(number, raw, UNCHECKED,
                                        "ran out of time before this line"))
            continue
        try:
            if transform is not None and transform.claims(_strip(raw)):
                verdict = transform.check(_strip(raw), last_good)
            else:
                verdict = _check_line(reader, parsed, _strip(raw), family,
                                      members, particular, fixed, last_good,
                                      number == final, linear)
        except ParseError as exc:
            verdict = (UNREADABLE, f"could not read this line: {exc}")
        except Exception:                        # never the thing that breaks
            verdict = (UNCHECKED, "could not decide about this line")
        status, message = verdict
        verdicts.append(LineVerdict(number, raw, status, message))
        if status == OK:
            last_good = number
    return verdicts


def _is_linear(parsed: ParsedEquation) -> bool:
    if parsed.order == 1:
        from .steps import _first_order_coefficients

        try:
            _first_order_coefficients(parsed.equation, parsed.function)
        except (ValueError, sp.PolynomialError):
            return False
        return True
    return bool(analyse_linear(parsed.equation, parsed.function,
                               parsed.order).get("linear"))


def _check_line(reader, parsed, text, family, members, particular, fixed,
                last_good, is_final, linear):
    if text.count("=") != 1:
        return UNREADABLE, ("write one equation per line, with one =")
    left_text, right_text = (side.strip() for side in text.split("="))
    if not left_text or not right_text:
        return UNREADABLE, "one side of the = is empty"

    function = parsed.function
    # dy/y = 2 dt: a line in differentials is a step on the way to the
    # integral, not a statement about y(t), and the next line is checked.
    differential = rf"(?<![A-Za-z_/])d\s*(?:{re.escape(reader.name)}|t)(?![A-Za-z_'/])"
    if re.search(differential, text) and not re.search(r"d\s*\w+\s*/\s*d", text):
        return UNCHECKED, ("a line in differentials is not checked -- the "
                           "line that integrates it is")
    if left_text in _FACTOR_NAMES and reader.name not in right_text:
        return _check_factor(reader, parsed, right_text, fixed)
    if reader.name not in text:
        char = _characteristic_line(left_text, right_text)
        if char:
            return _check_characteristic(reader, parsed, char, left_text,
                                         right_text)

    raw_lhs = reader.expression(left_text)
    raw_rhs = reader.expression(right_text)
    if not (raw_lhs.has(function) or raw_rhs.has(function)):
        return UNCHECKED, ("nothing in this line can be checked against the "
                           "solution -- it is checked where it is used")
    if is_final and raw_lhs == function(_T) and not raw_rhs.has(function):
        return _check_final(reader, parsed, raw_rhs)
    lhs, rhs = raw_lhs.subs(fixed), raw_rhs.subs(fixed)

    student = sorted((lhs - rhs).free_symbols - {_T} - set(fixed), key=str)
    relation_left, relation_right = lhs, rhs

    def holds_for(solution, unknowns):
        return _holds(_substitute(relation_left, function, solution),
                      _substitute(relation_right, function, solution),
                      unknowns)

    family_fixed = family.subs(fixed)
    results = []
    for values in _MEMBERS:
        member = family_fixed.subs(dict(zip(members, values)))
        results.append(holds_for(member, student))
    if all(result is True for result in results):
        return OK, ""
    if any(result is None for result in results):
        return UNCHECKED, ("this line could not be decided -- its constants "
                           "do not enter in a way that can be tested")

    if particular is not None:
        if holds_for(particular.subs(fixed), student) is True:
            return OK, "true of the solution that meets the conditions"
    else:
        if linear:
            lost = holds_for(family_fixed, [*student, *members]) is True
        else:
            lost = _some_member(
                _substitute(relation_left, function, family_fixed),
                _substitute(relation_right, function, family_fixed),
                [*student, *members])
        if lost:
            return WRONG, ("this holds for one solution only, not the whole "
                           "family: a constant was lost -- usually the + C "
                           "when integrating")
    if last_good:
        return WRONG, f"this does not follow: the slip is between line " \
                      f"{last_good} and this one"
    return WRONG, "this is not true of the solution -- check it against the " \
                  "equation"


def _check_final(reader, parsed, rhs):
    """``y = ...`` at the bottom: the answer box's own verdict."""
    student = sorted((s for s in rhs.free_symbols
                      if s != _T and s not in reader.parameters),
                     key=str)
    renamed = rhs.subs({symbol: sp.Symbol(f"C{index}")
                        for index, symbol in enumerate(student, 1)},
                       simultaneous=True)
    result = check_answer(parsed, sp.sstr(renamed),
                          general=not parsed.ics)
    if result.ok:
        return OK, "the answer checks out"
    if result.correct is None and result.general is not False:
        return UNCHECKED, result.message
    return WRONG, result.diagnosis or result.message


def _check_factor(reader, parsed, right_text, fixed):
    from .steps import _first_order_coefficients

    if parsed.order != 1:
        return UNCHECKED, "an integrating factor is for a first-order equation"
    try:
        p, _, _ = _first_order_coefficients(parsed.equation, parsed.function)
    except ValueError:
        return UNCHECKED, "this equation is not linear, so has no such factor"
    wanted = sp.exp(sp.integrate(p, _T)).subs(fixed)
    student = reader.expression(right_text).subs(fixed)
    if student.free_symbols - {_T}:
        return UNCHECKED, "a constant in the factor is not needed -- any one " \
                          "factor will do"
    ratio_of = _numeric(student / wanted, [_T])
    ratios = [ratio_of(t) for t in _TIMES]
    ratios = [r for r in ratios if _finite(r) and abs(r) > 1e-12]
    if len(ratios) < 4:
        return UNCHECKED, "could not evaluate this factor"
    if all(_close(r, ratios[0]) for r in ratios):
        return OK, ""
    return WRONG, (f"the integrating factor is e^(∫p dt) with p = "
                   f"{sp.sstr(p)}, which is {sp.sstr(sp.simplify(wanted))} "
                   f"(any constant multiple will do)")


def _characteristic_line(left: str, right: str) -> str:
    """"poly", "roots" or "" for a line written in r (or λ, m)."""
    joined = left + "=" + right
    if not re.search(r"(?<![A-Za-z_])(r|λ|lambda|m)(?![A-Za-z_])", joined) \
            and not re.match(r"^r\d$", left):
        return ""
    if re.fullmatch(r"(r|λ|lambda|m)\s*_?\d?", left.strip()):
        return "roots"
    return "poly"


def _check_characteristic(reader, parsed, kind, left, right, reference=None):
    """A characteristic polynomial, or its roots, against `reference` in r:
    the equation's own unless given -- a system gives det(A - rI)."""
    if reference is None:
        analysis = analyse_linear(parsed.equation, parsed.function,
                                  parsed.order)
        reference = analysis.get("poly")
    if reference is None:
        return UNCHECKED, "this equation has no characteristic polynomial"
    r = sp.Symbol("r")
    extra = {"r": r, "i": sp.I, "j": sp.I}

    def to_r(text):
        text = re.sub(r"(?<![A-Za-z_])(λ|lambda)(?![A-Za-z_])", "r", text)
        if "m" not in {s.name for s in reader.parameters}:
            text = re.sub(r"(?<![A-Za-z_])m(?![A-Za-z_])", "r", text)
        return text

    if kind == "poly":
        student = sp.expand(reader.expression(to_r(left), extra)
                            - reader.expression(to_r(right), extra))
        try:
            mine, theirs = sp.Poly(student, r), sp.Poly(reference, r)
        except sp.PolynomialError:
            return UNREADABLE, "that is not a polynomial in r"
        if mine.degree() == theirs.degree() and sp.simplify(
                mine.LC() * theirs.as_expr() - theirs.LC() * mine.as_expr()) == 0:
            return OK, ""
        how = ("it is det(A - rI) for the system's matrix A"
               if parsed.is_system else "each y^(k) becomes r^k")
        return WRONG, (f"the characteristic equation is "
                       f"{sp.sstr(reference)} = 0: {how}")

    values = []
    for piece in re.split(r",|\band\b", right):
        piece = piece.strip()
        if not piece:
            continue
        if "±" in piece or "+-" in piece:
            head, tail = re.split(r"±|\+-", piece, maxsplit=1)
            head = head.strip() or "0"
            values += [f"({head}) + ({tail})", f"({head}) - ({tail})"]
        else:
            values.append(piece)
    if not values:
        return UNREADABLE, "no root on the right of the ="
    for value in values:
        root = reader.expression(to_r(value), extra)
        if root.free_symbols - {r}:
            return UNCHECKED, "a root with letters in it cannot be checked"
        at = complex(sp.N(reference.subs(r, root)))
        scale = max(1.0, abs(complex(sp.N(root))) ** sp.degree(reference, r))
        if abs(at) > 1e-8 * scale:
            return WRONG, (f"{sp.sstr(root)} is not a root of "
                           f"{sp.sstr(reference)} = 0")
    return OK, ""


# ---------------------------------------------------------------------------
# Laplace transforms: lines in s
# ---------------------------------------------------------------------------

#: A line in s: ``Y``, ``Y(s)``, ``L{...}``, ``ℒ{...}``, or a bare ``s``.
_S_LINE = re.compile(
    r"(?<![A-Za-z_])(?:s?Y|s)(?![A-Za-z_])|ℒ|(?<![A-Za-z_])L\s*\{")
#: ``L^-1{...}``, ``L^{-1}{...}``: the inverse, judged by the line it gives.
_INVERSE = re.compile(r"(?:L|ℒ)\s*\^\s*\{?\s*-\s*1")


class _Transform:
    """Checks the lines of Laplace working written in s.

    Every such line is a claim about Y(s), the transform of the solution, and
    is tested by substituting the transform of the verified particular
    solution: ``sY - 1 + 2Y = 4/s``, ``Y = 2/s - 1/(s + 2)``. ``L{y'}`` and
    ``y(0)`` are read too. The probes are at real s to the right of every
    pole, where the transform is defined. A partial-fraction line with its
    own unknowns -- ``Y = A/s + B/(s+2)`` -- holds if some A and B make it.
    """

    def __init__(self, parsed: ParsedEquation, particular) -> None:
        self.parsed = parsed
        self.name = parsed.function.__name__
        self.particular = particular
        self.s = sp.Symbol("s")
        self.Y = sp.Symbol("Yofs")
        self._expected = None
        self._shift = 1.0
        self.reader = _Reader(parsed)
        #: Order of derivative -> its value at 0, from the conditions.
        self.at_zero: dict[int, sp.Expr] = {}
        function = parsed.function(_T)
        for key, value in parsed.ics.items():
            if key == parsed.function(0):
                self.at_zero[0] = value
            elif (isinstance(key, sp.Subs) and tuple(key.point) == (0,)
                  and isinstance(key.expr, sp.Derivative)
                  and key.expr.expr == function):
                self.at_zero[key.expr.derivative_count] = value

    def claims(self, text: str) -> bool:
        return bool(_S_LINE.search(text) or _INVERSE.search(text))

    def expected(self):
        """Y(s), and how far right the probes start. Worked out once."""
        if self._expected is None:
            transform = sp.laplace_transform(self.particular, _T, self.s,
                                             noconds=True)
            if transform.has(sp.LaplaceTransform):
                raise ValueError("the solution's transform was not found")
            _, denominator = sp.fraction(sp.together(transform))
            try:
                poles = sp.Poly(denominator, self.s).nroots()
                rightmost = max([0.0] + [float(sp.re(p)) for p in poles])
            except (sp.PolynomialError, ValueError, TypeError):
                rightmost = 0.0
            self._shift = rightmost + 1.0
            self._expected = transform
        return self._expected

    def _derivative(self, order: int) -> str:
        """``L{y^(k)}`` in Y and the conditions."""
        if any(k not in self.at_zero for k in range(order)):
            raise ParseError("the conditions do not give every value at 0 "
                             "this needs")
        terms = [f"s**{order}*Yofs"] + [
            f"s**{order - 1 - k}*({sp.sstr(self.at_zero[k])})"
            for k in range(order)]
        return "(" + " - ".join(terms) + ")"

    def _transform_of(self, inner: str) -> str:
        inner = re.sub(rf"^{re.escape(self.name)}\s*\(\s*t\s*\)", self.name,
                       inner.strip())
        match = re.fullmatch(rf"{re.escape(self.name)}('*)", inner)
        if match:
            return self._derivative(len(match.group(1)))
        expression = self.reader.expression(inner)
        if expression.has(self.parsed.function):
            raise ParseError("transform y and its derivatives one at a time")
        return "(" + sp.sstr(sp.laplace_transform(expression, _T, self.s,
                                                  noconds=True)) + ")"

    def _read(self, text: str) -> sp.Expr:
        # L{...} first, its braces matched by hand.
        while True:
            at = re.search(r"(?:ℒ|(?<![A-Za-z_])L)\s*\{", text)
            if at is None:
                break
            depth, close = 0, None
            for index in range(at.end() - 1, len(text)):
                depth += {"{": 1, "}": -1}.get(text[index], 0)
                if depth == 0:
                    close = index
                    break
            if close is None:
                raise ParseError("a { is never closed")
            text = (text[:at.start()]
                    + self._transform_of(text[at.end():close])
                    + text[close + 1:])
        # Y alone, or after an s: sY and s^2Y are how the working is written.
        lone_y = r"(?:(?<=s)|(?<![A-Za-z_]))Y"
        text = re.sub(lone_y + r"\s*\(\s*s\s*\)", "Y", text)
        # y(0), y'(0): the values the conditions give.
        for order, value in self.at_zero.items():
            primes = "'" * order
            text = re.sub(
                rf"(?<![A-Za-z_]){re.escape(self.name)}{primes}\s*\(\s*0\s*\)",
                f"({sp.sstr(value)})", text)
        text = text.replace("{", "(").replace("}", ")")
        text = re.sub(lone_y + r"(?![A-Za-z_])", "Yofs", text)
        scope = _answer_scope(set())
        scope.update({"s": self.s, "Yofs": self.Y})
        for letter in self.reader.constants:
            scope.setdefault(letter, sp.Symbol(letter))
        known = set(scope) | {"pi", "E"}
        return _parse_side(_answer_text(text, known), scope)

    def check(self, text: str, last_good: int):
        if _INVERSE.search(text):
            return UNCHECKED, ("an inverse transform is checked by the "
                               "y = ... line it gives")
        if text.count("=") != 1:
            return UNREADABLE, "write one equation per line, with one ="
        left_text, right_text = (side.strip() for side in text.split("="))
        if not left_text or not right_text:
            return UNREADABLE, "one side of the = is empty"
        try:
            expected = self.expected()
        except Exception:
            return UNCHECKED, ("the transform of this solution could not be "
                               "worked out, so lines in s are not checked")
        lhs, rhs = self._read(left_text), self._read(right_text)
        if not any(side.has(self.s) or side.has(self.Y)
                   for side in (lhs, rhs)):
            return UNCHECKED, "nothing in this line can be checked"
        probe = self._shift + 3 * _T
        lhs = lhs.subs(self.Y, expected).subs(self.s, probe)
        rhs = rhs.subs(self.Y, expected).subs(self.s, probe)
        unknowns = sorted((lhs - rhs).free_symbols - {_T}, key=str)
        result = _holds(lhs, rhs, unknowns)
        if result is True:
            return OK, ""
        if result is None:
            return UNCHECKED, "this line could not be decided"
        if last_good:
            return WRONG, (f"this is not true of Y(s), the transform of the "
                           f"solution: the slip is between line {last_good} "
                           f"and this one")
        return WRONG, ("this is not true of Y(s), the transform of the "
                       "solution -- check the transform of each term")


# ---------------------------------------------------------------------------
# Linear systems
# ---------------------------------------------------------------------------

#: An eigenvector's name: v, v1, v_2, u, w, ξ, K.
_VECTOR_NAME = re.compile(r"(?:v|u|w|ξ|xi|K)\s*_?\s*\d*")


def _check_system(parsed, text, general, particular, budget):
    """A 2×2 system's working: the characteristic polynomial and its roots
    against det(A - rI), each eigenvector by A v = λ v, and each ``x = ...``
    against that component of the solution family. A final pair of
    component lines goes through the answer checker as one answer."""
    from types import SimpleNamespace

    from .systems import split_system

    names = [function.__name__ for function in parsed.functions]
    matrix = split_system(parsed.equations, parsed.functions)[0]
    r = sp.Symbol("r")
    reference = sp.expand((matrix - r * sp.eye(matrix.rows)).det())
    reader = _Reader(SimpleNamespace(function=parsed.functions[0],
                                     equation=parsed.equations[0], order=1))
    family = sp.Matrix(general)
    constants = sorted(family.free_symbols - {_T} - reader.parameters,
                       key=lambda s: s.name)
    members = [sp.Dummy(f"K{i}") for i in range(len(constants))]
    family = family.subs(dict(zip(constants, members)), simultaneous=True)
    target = sp.Matrix(particular) if particular is not None else None

    lines = [(number, raw) for number, raw in enumerate(text.splitlines(), 1)
             if _strip(raw)]
    started = time.monotonic()
    verdicts: list[LineVerdict] = []
    components: dict[str, tuple[int, str]] = {}
    last_good = 0
    for number, raw in lines:
        if time.monotonic() - started > budget:
            verdicts.append(LineVerdict(number, raw, UNCHECKED,
                                        "ran out of time before this line"))
            continue
        try:
            status, message = _system_line(
                reader, parsed, _strip(raw), names, matrix, reference, family,
                members, target, last_good, components, number)
        except ParseError as exc:
            status, message = UNREADABLE, f"could not read this line: {exc}"
        except Exception:
            status, message = UNCHECKED, "could not decide about this line"
        verdicts.append(LineVerdict(number, raw, status, message))
        if status == OK:
            last_good = number

    # The working ends on a pair x = ..., y = ...: the answer box's own
    # verdict on the two together, which a line at a time cannot give.
    closing = {verdict.number for verdict in verdicts[-2:]}
    if set(components) == set(names) and all(
            components[name][0] in closing for name in names):
        try:
            pieces = {name: reader.expression(right)
                      for name, (_, right) in components.items()}
        except ParseError:
            return verdicts
        own = sorted(set().union(*(p.free_symbols for p in pieces.values()))
                     - {_T} - reader.parameters, key=str)
        renamed = {symbol: sp.Symbol(f"C{index}")
                   for index, symbol in enumerate(own, 1)}
        answer = "\n".join(
            f"{name} = {sp.sstr(pieces[name].subs(renamed, simultaneous=True))}"
            for name in names)
        result = check_answer(parsed, answer, general=not parsed.ics)
        last = verdicts[-1]
        if result.ok:
            verdicts[-1] = LineVerdict(last.number, last.text, OK,
                                       "the answer checks out")
        elif result.correct is False:
            verdicts[-1] = LineVerdict(last.number, last.text, WRONG,
                                       result.diagnosis or result.message)
    return verdicts


def _system_line(reader, parsed, text, names, matrix, reference, family,
                 members, target, last_good, components, number):
    if text.count("=") != 1:
        return UNREADABLE, "write one equation per line, with one ="
    left, right = (side.strip() for side in text.split("="))
    if not left or not right:
        return UNREADABLE, "one side of the = is empty"

    # det(A - λI) = λ² + ... : the right-hand side is the polynomial.
    if re.match(r"det\b", left):
        left = "0"
    name = re.sub(r"\s*\(\s*t\s*\)$", "", left)
    if name in names:
        components[name] = (number, right)
        return _component(reader, names.index(name), name, right, family,
                          members, target, last_good)
    if _VECTOR_NAME.fullmatch(left) and re.match(r"^[\[(<]", right):
        return _eigenvector(reader, matrix, right)
    kind = _characteristic_line(left, right)
    if kind:
        return _check_characteristic(reader, parsed, kind, left, right,
                                     reference)
    return UNCHECKED, ("nothing in this line can be checked -- write the "
                       "characteristic equation, the eigenvalues, each "
                       "eigenvector as v = (a, b), or x = ... and y = ...")


def _eigenvector(reader, matrix, right):
    right = right.strip()
    if right[-1:] not in ")]>":
        return UNREADABLE, "write an eigenvector as (a, b)"
    entries = [part for part in re.split(r"[,;]", right[1:-1]) if part.strip()]
    if len(entries) != matrix.rows:
        return UNREADABLE, f"an eigenvector here has {matrix.rows} entries"
    extra = {"i": sp.I, "j": sp.I}
    vector = sp.Matrix([reader.expression(entry, extra) for entry in entries])
    if vector.free_symbols:
        return UNCHECKED, "an eigenvector with letters in it is not checked"
    if all(entry == 0 for entry in vector):
        return WRONG, "an eigenvector is never zero"
    image = matrix * vector
    for value in matrix.eigenvals():
        if all(sp.simplify(entry) == 0 for entry in image - value * vector):
            return OK, f"for λ = {sp.sstr(value)}"
    return WRONG, (f"A v = {sp.sstr(list(image))}, which is not a multiple "
                   f"of v, so v is not an eigenvector of A")


def _component(reader, index, name, right, family, members, target,
               last_good):
    expression = reader.expression(right)
    student = sorted(expression.free_symbols - {_T} - reader.parameters,
                     key=str)
    if target is not None:
        if _holds(expression, target[index], student) is True:
            return OK, ""
    else:
        results = [_holds(expression,
                          family[index].subs(dict(zip(members, values))),
                          student)
                   for values in _MEMBERS]
        if all(result is True for result in results):
            return OK, ""
        if any(result is None for result in results):
            return UNCHECKED, ("this line could not be decided -- its "
                               "constants do not enter in a way that can be "
                               "tested")
    if last_good:
        return WRONG, (f"this is not the {name}-part of a solution: the slip "
                       f"is between line {last_good} and this one")
    return WRONG, (f"this is not the {name}-part of a solution -- check the "
                   f"eigenvalues and eigenvectors it is built from")
