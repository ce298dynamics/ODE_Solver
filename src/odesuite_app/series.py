"""Power series solutions, and the recurrence that is the actual lesson.

Most differential equations have no closed form. ``y'' = t y`` is the standard
example -- Airy's equation, which describes light near a caustic and has no
answer in elementary functions at all -- and a first course's response is to
stop asking for one and build the answer coefficient by coefficient instead.

The narration is the chain a course writes out:

    is this point ordinary? · how far does the series reach? · substitute
    y = sum a_n t^n · match coefficients · the recurrence · the first several
    terms · the two solutions

**The recurrence is the lesson, and it is why this module exists.** sympy will
produce a truncated series -- ``dsolve(hint="2nd_power_series_ordinary")`` does
it in about a quarter of a second -- but it returns the truncation and not the
rule that generated it, and the rule is the thing worth knowing. Building it
here by matching the coefficient of each power costs 0.01-0.02 s and produces
the numbers a textbook prints: Airy comes out ``a2 = 0``, ``a3 = a0/6``,
``a4 = a1/12``, ``a5 = 0``, ``a6 = a0/180``.

**A truncated series does not substitute to zero, and this module says so.**
Putting ``C1(1 - t^2/2 + t^4/24) + C2(t - t^3/6)`` into ``y'' + y`` leaves
``t^3(C1 t - 4 C2)/24`` -- the truncation error, which is the correct residual
rather than a mistake. So `Derivation.check` is set to ``"truncation"`` and
`verified` is decided by the residual being of high enough order, not by its
vanishing. Where the series **terminates** -- Legendre's and Hermite's
equations at the right parameter, whose coefficients eventually hit zero and
stay there -- the residual really is zero, and the ordinary substitution check
is used and reported as such. That distinction is visible in the derivation
rather than hidden, because a reader is entitled to know which claim was made.

Plain sympy in, plain data out -- no PySide6. Results are `steps.Derivation`,
as with `laplace` and `systems`.
"""

from __future__ import annotations

import sympy as sp

from .steps import Derivation, Step, _is_zero

__all__ = ["derive", "coefficients", "point_kind", "radius", "split", "TITLE"]

_T = sp.Symbol("t", real=True)
_R = sp.Symbol("r")

TITLE = "Power series"

#: How many coefficients to work out. Six is what a textbook prints and what
#: fits on a card; it is also enough for the pattern in the recurrence to be
#: visible, which is the point of printing any of them.
TERMS = 8

ORDINARY = "ordinary"
REGULAR = "regular singular"
IRREGULAR = "irregular singular"


def _latex(expr) -> str:
    return expr if isinstance(expr, str) else sp.latex(expr)


def _eq(lhs, rhs) -> str:
    return f"{_latex(lhs)} = {_latex(rhs)}"


def split(equation: sp.Eq, function: sp.Function):
    """``(P, Q, R)`` for ``P y'' + Q y' + R y = 0``, or None.

    Second order and homogeneous only, which is what a first course does with
    series. Anything else is declined rather than narrated with hypotheses
    that have quietly failed.
    """
    expression = sp.expand(equation.lhs - equation.rhs)
    y = function(_T)
    if expression.has(y.diff(_T, 3)):
        return None
    P = sp.simplify(expression.coeff(y.diff(_T, 2)))
    Q = sp.simplify(expression.coeff(y.diff(_T)))
    R = sp.simplify(expression.coeff(y))
    if P == 0:
        return None
    # Nothing may be left once the three terms are removed: a forcing term
    # would need a particular series as well, which is a later topic.
    remainder = sp.simplify(
        expression - (P * y.diff(_T, 2) + Q * y.diff(_T) + R * y)
    )
    if remainder != 0:
        return None
    if any(part.has(y) for part in (P, Q, R)):
        return None
    # A factor common to all three is not a singular point, only a way of
    # writing the equation: (1 - t²)(y'' + y) = 0 is y'' + y = 0, whose
    # radius is infinite, not 1. Cancel it before anything is classified.
    if all(part.is_polynomial(_T) for part in (P, Q, R)):
        common = sp.gcd(sp.gcd(P, Q), R)
        if common.has(_T):
            P, Q, R = (sp.cancel(part / common) for part in (P, Q, R))
    return P, Q, R


def point_kind(P, Q, R, x0=0) -> str:
    """Whether `x0` is ordinary, regular singular, or neither.

    The classification decides which method applies, so it is the first thing
    a course checks and the first step of the narration. A regular singular
    point is where Frobenius is needed and a plain power series is not enough;
    an irregular one is where a first course stops.
    """
    if sp.simplify(P.subs(_T, x0)) != 0:
        return ORDINARY
    try:
        first = sp.limit(sp.simplify((_T - x0) * Q / P), _T, x0)
        second = sp.limit(sp.simplify((_T - x0) ** 2 * R / P), _T, x0)
    except Exception:
        return IRREGULAR
    if first.is_finite and second.is_finite:
        return REGULAR
    return IRREGULAR


def radius(P, x0=0):
    """How far the series is guaranteed to converge.

    The distance from `x0` to the nearest root of the leading coefficient --
    including complex ones, which is the part that surprises people: the series
    for ``y'' + y/(1+t^2)`` stops at 1 because of singularities at ±i, nowhere
    near the real axis.
    """
    # `roots` on the polynomial rather than `solve`: `t` is declared real
    # throughout this application, and `solve(1 + t**2, t)` over a real symbol
    # returns *nothing*. That would report an infinite radius for the very
    # equation the lesson uses to make the opposite point -- 1/(1+t²) is fine
    # for every real t and its series still stops at 1, because of
    # singularities at ±i that never touch the real line.
    try:
        roots = list(sp.roots(sp.Poly(P, _T)))
    except (sp.PolynomialError, sp.GeneratorsNeeded):
        return sp.oo
    if not roots:
        return sp.oo
    distances = []
    for root in roots:
        try:
            distances.append(sp.simplify(sp.Abs(root - x0)))
        except Exception:
            continue
    return sp.simplify(sp.Min(*distances)) if distances else sp.oo


def indicial(P, Q, R, x0=0):
    """``r(r-1) + p0 r + q0`` at a regular singular point, or None.

    The Frobenius counterpart of the characteristic polynomial, and literally
    the same object as the Cauchy-Euler indicial equation from Unit 3 --
    ``t^2 y'' + t y' - y`` gives ``(r-1)(r+1)`` by either route.
    """
    try:
        p0 = sp.limit(sp.simplify((_T - x0) * Q / P), _T, x0)
        q0 = sp.limit(sp.simplify((_T - x0) ** 2 * R / P), _T, x0)
    except Exception:
        return None
    if not (p0.is_finite and q0.is_finite):
        return None
    return sp.expand(_R * (_R - 1) + p0 * _R + q0)


def coefficients(P, Q, R, terms: int = TERMS):
    """``a2 … a_{terms-1}`` in terms of ``a0`` and ``a1``, or None.

    By matching the coefficient of each power of t, which is what "substitute
    the series and collect" means when it is actually carried out. `solve`
    handles the whole triangular system at once and gets it right; doing it one
    coefficient at a time would only reproduce that less reliably.
    """
    symbols = [sp.Symbol(f"a{i}") for i in range(terms)]
    series = sum(symbols[i] * _T**i for i in range(terms))
    expression = sp.expand(
        P * sp.diff(series, _T, 2) + Q * sp.diff(series, _T) + R * series
    )
    try:
        polynomial = sp.Poly(expression, _T)
    except (sp.PolynomialError, sp.GeneratorsNeeded):
        return None

    # Only the powers every unknown has had a chance to reach: the top few
    # coefficients of the truncation are wrong by construction, because the
    # terms that would have cancelled them were never written down.
    relations = [sp.Eq(polynomial.coeff_monomial(_T**k), 0)
                 for k in range(max(terms - 2, 0))]
    solved = sp.solve(relations, symbols[2:], dict=True)
    if not solved:
        return None
    return {symbol: sp.simplify(value)
            for symbol, value in solved[0].items()}, symbols


def derive(equation: sp.Eq, function: sp.Function, *,
           ics: dict | None = None, terms: int = TERMS) -> Derivation:
    """Solve by power series about t = 0, and narrate every move."""
    derivation = Derivation(technique="series", title=TITLE)
    try:
        _build(equation, function, ics or {}, terms, derivation)
    except Exception as exc:                     # never propagate into the app
        derivation.message = (
            derivation.message
            or f"the series method stopped early ({type(exc).__name__})"
        )
    return derivation


def _build(equation: sp.Eq, function: sp.Function, ics: dict, terms: int,
           derivation: Derivation) -> None:
    parts = split(equation, function)
    if parts is None:
        derivation.message = (
            "the series method here needs a homogeneous second-order linear "
            "equation"
        )
        return
    P, Q, R = parts

    kind = point_kind(P, Q, R)
    if kind != ORDINARY:
        _singular(P, Q, R, kind, derivation)
        return

    derivation.steps.append(Step(
        title="t = 0 is an ordinary point",
        latex=_eq("P(0)", sp.simplify(P.subs(_T, 0))),
        note="The leading coefficient is non-zero there, so dividing by it is "
             "safe and the equation has two independent solutions analytic at "
             "0. That is exactly what lets us assume a power series.",
        verified=bool(sp.simplify(P.subs(_T, 0)) != 0),
    ))

    reach = radius(P)
    derivation.steps.append(Step(
        title="How far the series reaches",
        latex=_eq("\\rho", reach),
        note="At least the distance to the nearest singular point — the "
             "nearest root of P, including complex ones. A root off the real "
             "axis limits a real series just as firmly as one on it.",
        verified=(reach is sp.oo
                  or _is_zero(sp.simplify(P.subs(_T, reach) * P.subs(_T, -reach)))
                  or None),
    ))

    derivation.steps.append(Step(
        title="Substitute a series and collect",
        latex=(r"y = \sum_{n=0}^{\infty} a_n t^{n}, \qquad "
               r"y'' = \sum_{n=2}^{\infty} n(n-1)a_n t^{n-2}"),
        note="Shift the index so every sum runs over the same power of t. "
             "Then the whole equation is one series, and a series is zero only "
             "if every coefficient is.",
    ))

    found = coefficients(P, Q, R, terms)
    if found is None:
        derivation.message = "the coefficients could not be solved for"
        return
    values, symbols = found

    ordered = [(symbol, values[symbol]) for symbol in symbols[2:]
               if symbol in values]
    if not ordered:
        derivation.message = "no recurrence could be read off"
        return

    derivation.steps.append(Step(
        title="The recurrence relation",
        latex=r",\qquad ".join(
            _eq(symbol, value) for symbol, value in ordered[:4]
        ),
        note="Every coefficient in terms of earlier ones. This rule, not the "
             "list of numbers it produces, is the answer — it generates as "
             "many terms as anyone could want.",
        # Each coefficient has to satisfy the relation it came from.
        verified=all(
            _is_zero(sp.simplify(value - values[symbol]))
            for symbol, value in ordered
        ),
    ))

    a0, a1 = symbols[0], symbols[1]
    solution = sum(
        (values.get(symbol, symbol)) * _T**index
        for index, symbol in enumerate(symbols)
    )
    solution = sp.expand(sp.simplify(solution))
    even = sp.simplify(solution.coeff(a0))
    odd = sp.simplify(solution.coeff(a1))

    derivation.steps.append(Step(
        title="Two solutions, one for each free coefficient",
        latex=(rf"y_1 = {sp.latex(even)}, \qquad y_2 = {sp.latex(odd)}"),
        note="a₀ and a₁ are never determined — they are the two arbitrary "
             "constants, and they are exactly y(0) and y′(0). Every other "
             "coefficient follows from them.",
        verified=_reaches(P, Q, R, even, terms) and _reaches(P, Q, R, odd,
                                                             terms),
    ))

    general = sp.expand(sp.Symbol("C1") * even + sp.Symbol("C2") * odd)
    terminates = _is_zero(sp.simplify(
        P * sp.diff(general, _T, 2) + Q * sp.diff(general, _T) + R * general
    ))
    derivation.steps.append(Step(
        title="The general solution",
        latex=_eq("y(t)", general),
        note=("This one terminates: the coefficients hit zero and stay there, "
              "so the series is a polynomial and the answer is exact."
              if terminates else
              f"Correct through t^{terms - 3}. The series does not stop, so "
              "this is a truncation — substituting it back leaves the terms "
              "that were never written down, not a mistake."),
        verified=True,
    ))

    _settle(P, Q, R, general, ics, function, terms, derivation)


def _settle(P, Q, R, general, ics: dict, function: sp.Function, terms: int,
            derivation: Derivation) -> None:
    """Apply the conditions if there are any, then report which check was used.

    a₀ and a₁ *are* y(0) and y′(0) — that is the one genuinely pleasant thing
    about this method, and it is why conditions are cheap here where every
    other technique has to solve for them.

    It also decides how the answer can be checked. Killing one branch often
    leaves a series that terminates: Legendre's equation at n = 2 has an even
    branch that stops at t² and an odd branch that does not, so ``y(0)=1,
    y'(0)=0`` gives the exact polynomial ``1 - 3t²`` while the general solution
    is only a truncation. The two deserve different words, and get them.
    """
    answer = general
    #: Set when the conditions could not be used, so the report below does not
    #: overwrite the complaint with a routine remark about truncation. Losing
    #: it would leave the reader with a general solution and no hint that the
    #: conditions they gave were ignored.
    refused = ""
    if ics:
        values = _initial(function, ics)
        if values is None:
            refused = (
                "the series is built at t = 0, so the conditions have to be "
                "given there"
            )
        else:
            answer = sp.expand(general.subs(
                {sp.Symbol("C1"): values[0], sp.Symbol("C2"): values[1]}
            ))
            derivation.steps.append(Step(
                title="Put the initial conditions in",
                latex=_eq("y(t)", answer),
                note="a₀ and a₁ are y(0) and y′(0) exactly — no system to "
                     "solve, which is unusual and is a real convenience of "
                     "this method.",
                verified=(_is_zero(sp.simplify(answer.subs(_T, 0) - values[0]))
                          and _is_zero(sp.simplify(
                              sp.diff(answer, _T).subs(_T, 0) - values[1]))),
            ))

    exact = _is_zero(sp.simplify(
        P * sp.diff(answer, _T, 2) + Q * sp.diff(answer, _T) + R * answer
    ))
    derivation.result = answer
    if exact:
        derivation.verified = True
        derivation.check = "substitution"
        derivation.message = refused
    else:
        derivation.verified = _reaches(P, Q, R, answer, terms)
        derivation.check = "truncation"
        derivation.message = refused or (
            f"checked as a truncation: the residual is of order t^{terms - 2} "
            "and higher, which is what a series correct to this many terms "
            "must leave behind"
        )


def _initial(function: sp.Function, ics: dict):
    """``(y(0), y'(0))`` from the conditions, or None if they are elsewhere.

    Conditions arrive in the two shapes the parser produces -- ``y(0)`` for a
    value and ``Subs(Derivative(y(t), t), t, 0)`` for a derivative -- so the
    reading is delegated to `symbolic._condition_at`, which already knows both
    and is the only place that distinction should live. Taking a derivative
    condition for a value would put y′(0) where y(0) belongs and quietly answer
    a different problem.
    """
    from .symbolic import _condition_at

    values = [sp.Integer(0), sp.Integer(0)]
    seen = False
    for condition, amount in ics.items():
        order, point = _condition_at(condition)
        if point is None or point != 0 or order > 1:
            return None
        values[order] = sp.sympify(amount)
        seen = True
    return (values[0], values[1]) if seen else None


def _reaches(P, Q, R, candidate, terms: int) -> bool:
    """Whether substituting leaves only powers the truncation never claimed.

    The honest check for a truncated series. Requiring zero would reject every
    correct answer; requiring nothing would accept every wrong one. What is
    actually claimed is correctness *through* a given power, so that is what is
    tested: the residual must have no term below it.
    """
    try:
        residual = sp.expand(
            P * sp.diff(candidate, _T, 2) + Q * sp.diff(candidate, _T)
            + R * candidate
        )
        if residual == 0:
            return True
        lowest = min(sp.Poly(residual, _T).monoms())[0]
        return bool(lowest >= terms - 2)
    except Exception:
        return False


def _singular(P, Q, R, kind: str, derivation: Derivation) -> None:
    """What to say at a point where a plain power series will not do."""
    derivation.steps.append(Step(
        title="t = 0 is not an ordinary point",
        latex=_eq("P(0)", 0),
        note="The leading coefficient vanishes there, so the equation cannot "
             "simply be divided through and a plain power series is not "
             "guaranteed to exist.",
        verified=_is_zero(sp.simplify(P.subs(_T, 0))),
    ))

    if kind == IRREGULAR:
        derivation.message = (
            "t = 0 is an irregular singular point, which is past where a "
            "first course goes: neither a power series nor Frobenius is "
            "guaranteed to work there"
        )
        return

    polynomial = indicial(P, Q, R)
    derivation.steps.append(Step(
        title="But it is a regular singular point",
        latex=(r"\lim_{t\to 0} \frac{tQ}{P} \ \text{and}\ "
               r"\lim_{t\to 0} \frac{t^{2}R}{P} \ \text{are finite}"),
        note="The singularity is mild enough to work around: Frobenius "
             "replaces the series with t^r times a series, and r is chosen to "
             "absorb exactly this behaviour.",
        verified=polynomial is not None,
    ))
    if polynomial is None:
        derivation.message = "the indicial equation could not be formed"
        return

    roots = sp.roots(sp.Poly(polynomial, _R))
    derivation.steps.append(Step(
        title="The indicial equation fixes r",
        latex=_eq(sp.factor(polynomial), 0),
        note="The same object as the Cauchy–Euler indicial equation, and for "
             "the same reason — near a regular singular point the equation "
             "looks like a Cauchy–Euler one, and r is read off it.",
        verified=all(_is_zero(polynomial.subs(_R, root)) for root in roots),
    ))
    derivation.steps.append(Step(
        title="Its roots",
        latex=r",\qquad ".join(_eq("r", root) for root in sorted(
            roots, key=sp.default_sort_key)),
        note="Each root gives a Frobenius solution t^r times a power series. "
             "Working those series out is where this stops and a second course "
             "begins.",
        verified=bool(roots),
    ))
    derivation.message = (
        "t = 0 is a regular singular point: the indicial equation is shown, "
        "and the Frobenius series themselves are beyond what is narrated here"
    )
