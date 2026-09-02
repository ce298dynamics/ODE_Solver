"""Solving an equation by transforming it out of the time domain and back.

The Laplace transform is the one technique in a first course that turns a
differential equation into an *algebraic* one -- and the only one that copes
with forcing that is switched on partway through or delivered as an impulse.
``y' + y = u(t-2)``, a switch thrown at two seconds, is not separable, has no
integrating factor worth writing, and is not what undetermined coefficients is
for. It is three lines of algebra here.

The method, and the narration, are the same six moves:

    transform both sides · name the unknown Y(s) · put the initial conditions
    in · solve for Y(s) · split into partial fractions · invert term by term

The initial conditions are the point of the third move and the reason the
technique exists. They do not arrive at the end as constants to be pinned down;
they enter at the beginning, through ``L{y''} = s^2 Y - s y(0) - y'(0)``, and
the narration shows them appearing there.

Two things are worth knowing about what this can and cannot promise.

**The answer is checked, by whichever route can decide it.** With smooth forcing
it is substituted into the equation and must simplify to exactly zero, as
everywhere else in this project. That check cannot decide a step-forced answer:
differentiating a Heaviside leaves Dirac terms that never cancel *even when the
answer is right*. Those are checked against this project's own integrator
instead. An impulse can be checked by neither -- `DiracDelta` does not lambdify
-- and is reported as unchecked rather than as either right or wrong.

**Its input is parsed more permissively than the rest of the application**, by
exactly two names: `Heaviside` and `DiracDelta`. Those belong here and nowhere
else. `DiracDelta` cannot be evaluated numerically at all, and a discontinuous
right-hand side is precisely what an adaptive step can step over without
noticing -- so the Solver Lab keeps the narrower list, and the widening lives on
the symbolic path that never reaches an integrator.

Plain sympy in, plain data out -- no PySide6. Results are `steps.Derivation`,
which is already the right shape and already has a renderer and a wire format.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from .steps import Derivation, Step, _condition_point, _exact, _is_zero

__all__ = [
    "derive",
    "EXTRA_FUNCTIONS",
    "TABLE",
    "Pair",
    "pairs_used",
    "TITLE",
]

_T = sp.Symbol("t", real=True)
_S = sp.Symbol("s")
_Y = sp.Function("Y")

TITLE = "Laplace transform"

#: The two names this screen accepts that the rest of the application does not.
#:
#: A unit switched on at ``t = 2`` is ``Heaviside(t - 2)``; a hammer blow at
#: ``t = 1`` is ``DiracDelta(t - 1)``. They are ordinary sympy functions, no
#: different in kind from the `sign` and `floor` already allowed -- but they are
#: added *here* rather than to `custom.ALLOWED_FUNCTIONS`, because neither
#: belongs anywhere near the numeric solver. See the module docstring.
EXTRA_FUNCTIONS: dict[str, object] = {
    "Heaviside": sp.Heaviside,
    "DiracDelta": sp.DiracDelta,
}


# ---------------------------------------------------------------------------
# The table
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Pair:
    """One row of the transform table."""

    key: str
    #: The time-domain function, as LaTeX.
    f_latex: str
    #: Its transform, as LaTeX.
    F_latex: str
    note: str = ""


#: The pairs a first course memorises, in the order they are usually met.
TABLE: tuple[Pair, ...] = (
    Pair("one", r"1", r"\frac{1}{s}"),
    Pair("power", r"t^{n}", r"\frac{n!}{s^{n+1}}"),
    Pair("exp", r"e^{at}", r"\frac{1}{s-a}",
         "Shifting in s is multiplying by an exponential in t."),
    Pair("sin", r"\sin(bt)", r"\frac{b}{s^{2}+b^{2}}"),
    Pair("cos", r"\cos(bt)", r"\frac{s}{s^{2}+b^{2}}"),
    Pair("expsin", r"e^{at}\sin(bt)", r"\frac{b}{(s-a)^{2}+b^{2}}",
         "The first shifting theorem: replace s by s − a."),
    Pair("expcos", r"e^{at}\cos(bt)", r"\frac{s-a}{(s-a)^{2}+b^{2}}"),
    Pair("derivative", r"y'(t)", r"sY(s) - y(0)",
         "Why the method exists: differentiating becomes multiplying by s, "
         "and the initial condition comes along with it."),
    Pair("derivative2", r"y''(t)", r"s^{2}Y(s) - s\,y(0) - y'(0)"),
    Pair("step", r"u(t-a)", r"\frac{e^{-as}}{s}",
         "The unit step: switched off until t = a, then on."),
    Pair("shift", r"u(t-a)\,g(t-a)", r"e^{-as}G(s)",
         "The second shifting theorem: a delay in t is a factor e^{-as}."),
    Pair("impulse", r"\delta(t-a)", r"e^{-as}",
         "A unit impulse at t = a. Not a function at all, which is part of "
         "why the transform is the natural way to handle one."),
    Pair("tf", r"t\,f(t)", r"-F'(s)"),
    Pair("convolution", r"\int_0^{t} f(t-\tau)\,g(\tau)\,d\tau", r"F(s)G(s)",
         "A product of transforms is never the transform of a product — it "
         "is the transform of a convolution. The row to reach for when Y(s) "
         "will not split."),
    Pair("periodic", r"f(t+T) = f(t)",
         r"\frac{1}{1-e^{-Ts}}\int_0^{T}\! f(t)e^{-st}\,dt",
         "A periodic forcing term only has to be integrated over one period; "
         "the factor in front sums the rest of them."),
)

#: How to recognise, in a time-domain answer, that a row was needed.
#:
#: The last two table rows are deliberately absent. `convolution` and
#: `periodic` describe a *route* rather than a shape -- an answer reached by
#: convolution looks like any other answer, and one left as an integral has no
#: `result` to inspect at all -- so there is nothing in the time domain to
#: recognise them by. A detector that guessed would highlight the wrong row,
#: which is worse than highlighting none: the table is meant to read as a
#: reference being consulted.
_DETECT = {
    "one": lambda e: e.is_number and e != 0,
    "power": lambda e: e.has(_T) and _is_polynomial_in_t(e),
    "exp": lambda e: e.has(sp.exp),
    "sin": lambda e: e.has(sp.sin),
    "cos": lambda e: e.has(sp.cos),
    "expsin": lambda e: e.has(sp.exp) and e.has(sp.sin),
    "expcos": lambda e: e.has(sp.exp) and e.has(sp.cos),
    "step": lambda e: e.has(sp.Heaviside),
    "shift": lambda e: e.has(sp.Heaviside),
    "impulse": lambda e: e.has(sp.DiracDelta),
}


def _is_polynomial_in_t(expr) -> bool:
    try:
        return bool(sp.Poly(expr, _T).degree() >= 1)
    except (sp.PolynomialError, sp.GeneratorsNeeded):
        return False


def pairs_used(answer) -> set[str]:
    """Which table rows the answer actually needed.

    Used to highlight them beside the derivation, so the table reads as a
    reference being consulted rather than as decoration. Recognition is by
    form -- an exponential in the answer came from the ``e^{at}`` row -- which
    is how a student uses the table in the other direction.
    """
    if answer is None:
        return set()
    found = {key for key, test in _DETECT.items() if _safe(test, answer)}
    # The derivative rows are what made it an algebraic equation in the first
    # place, so they are always in play.
    return found | {"derivative", "derivative2"}


def _safe(test, expr) -> bool:
    try:
        return bool(test(expr))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# The derivation
# ---------------------------------------------------------------------------


def _latex(expr) -> str:
    return expr if isinstance(expr, str) else sp.latex(expr)


def _eq(lhs, rhs) -> str:
    return f"{_latex(lhs)} = {_latex(rhs)}"


def _strip_unit_step(expr):
    """Drop the ``Heaviside(t)`` the inverse transform decorates everything with.

    It carries no information -- the transform only ever describes t >= 0, so a
    factor that is 1 throughout that range is noise on every line of the answer.
    A *shifted* step is the opposite: ``Heaviside(t - 2)`` is the whole content
    of a switched input, and is kept.
    """
    try:
        return expr.replace(
            sp.Heaviside,
            lambda arg, *rest: (sp.Integer(1) if sp.simplify(arg - _T) == 0
                                else sp.Heaviside(arg, *rest)),
        )
    except Exception:
        return expr


def _initial_values(function, ics: dict, order: int):
    """``[y(0), y'(0), …]`` for `laplace_initial_conds`, or a reason it cannot be.

    The transform integrates from zero, so a condition given anywhere else
    cannot enter the method at all. Saying that is more use than silently
    solving a different problem.
    """
    values: dict[int, object] = {}
    for key, value in ics.items():
        point, derivative_order = _condition_point(key)
        if point is None:
            continue
        if sp.simplify(point) != 0:
            return None, (
                f"the Laplace transform integrates from t = 0, so a condition "
                f"given at t = {point} cannot be used — restate it at t = 0"
            )
        values[derivative_order] = _exact(value)

    if not values:
        return [], ""
    highest = max(values)
    if highest >= order:
        return None, (
            f"a condition on y{'′' * highest} is one the equation does not need"
        )
    # A gap is left as the symbol it stands for -- ``x(0)`` when only ``x'(0)``
    # was given -- and it must be *this* equation's function. Hardcoding `y`
    # here put a `y(0)` into the answer for an equation written in `x`, which
    # is a symbol from no equation the reader ever wrote.
    return [values.get(k, _unknown(function, k)) for k in range(highest + 1)], ""


def _unknown(function, order: int):
    """The still-unknown initial value of order `order`, as it should be shown."""
    if order == 0:
        return function(0)
    return sp.Subs(function(_T).diff(_T, order), _T, 0)


def derive(equation: sp.Eq, function: sp.Function, *,
           ics: dict | None = None) -> Derivation:
    """Solve `equation` by transforming it, and narrate every move."""
    derivation = Derivation(technique="laplace", title=TITLE)
    try:
        _build(equation, function, ics or {}, derivation)
    except Exception as exc:                      # never propagate into the app
        derivation.message = (
            derivation.message
            or f"the transform stopped early ({type(exc).__name__})"
        )
    return derivation


def _build(equation: sp.Eq, function: sp.Function, ics: dict,
           derivation: Derivation) -> None:
    from sympy.integrals.laplace import (
        laplace_correspondence,
        laplace_initial_conds,
        laplace_transform,
    )

    order = _order_of(equation, function)
    expression = equation.lhs - equation.rhs

    # -- transform ------------------------------------------------------
    raw = laplace_transform(expression, _T, _S, noconds=True)
    named = laplace_correspondence(raw, {function: _Y})
    if _unresolved(named, function):
        derivation.message = (
            "this equation has no Laplace transform in closed form — the "
            "method needs it to be linear in y with constant coefficients"
        )
        return
    if _differentiates_in_s(named):
        # A coefficient of t transforms to a derivative in s, so the result is
        # another differential equation rather than an algebraic one. The
        # method has not failed; it has simply not helped, and saying so beats
        # showing the reader an unevaluated InverseLaplaceTransform.
        derivation.message = (
            "the coefficients depend on t, so transforming turns this into a "
            "differential equation in s rather than an algebraic one — the "
            "transform does not simplify this equation"
        )
        return

    derivation.steps.append(Step(
        title="Transform both sides",
        latex=r"\mathcal{L}\{y'\} = sY(s) - y(0), \qquad "
              r"\mathcal{L}\{y''\} = s^{2}Y(s) - s\,y(0) - y'(0)",
        note="Differentiating in t becomes multiplying by s. That is the whole "
             "idea: the differential equation turns into an algebraic one — "
             "and the initial conditions come in with it, rather than waiting "
             "until the end.",
    ))
    derivation.steps.append(Step(
        title="The transformed equation",
        latex=_eq(named, 0),
        note="Every derivative is gone. What is left involves only s, Y(s), "
             "and the values of y and its derivatives at zero.",
    ))

    # -- initial conditions ---------------------------------------------
    values, complaint = _initial_values(function, ics, order)
    if values is None:
        derivation.message = complaint
        return
    with_conditions = (
        laplace_initial_conds(named, _T, {function: values}) if values else named
    )
    if values:
        derivation.steps.append(Step(
            title="Put the initial conditions in",
            latex=_eq(with_conditions, 0),
            note="They were already in the equation, waiting — substituting "
                 "them is all that is needed. No constants have to be pinned "
                 "down afterwards.",
        ))
    else:
        derivation.steps.append(Step(
            title="No initial conditions were given",
            latex=_eq(with_conditions, 0),
            note="y(0) and its derivatives stay as symbols, and the answer "
                 "below is the general solution written in terms of them.",
        ))

    _solve_and_invert(equation, function, ics, with_conditions, derivation,
                      order)


def _solve_and_invert(equation: sp.Eq, function: sp.Function, ics: dict,
                      with_conditions, derivation: Derivation,
                      order: int) -> None:
    """The second half: algebra in s, then the journey back to t.

    Split from `_build` along the seam the method itself has -- everything up to
    here was turning the equation into algebra, and everything from here is
    solving that algebra and inverting the result.
    """
    from sympy.integrals.laplace import inverse_laplace_transform

    solutions = sp.solve(sp.Eq(with_conditions, 0), _Y(_S))
    if not solutions:
        derivation.message = "the transformed equation could not be solved for Y(s)"
        return
    transform = sp.simplify(solutions[0])
    derivation.steps.append(Step(
        title="Solve for Y(s) — it is only algebra",
        latex=_eq("Y(s)", transform),
        note="No calculus here at all. This is what the transform bought.",
        verified=_is_zero(with_conditions.subs(_Y(_S), transform)),
    ))

    # -- partial fractions ----------------------------------------------
    # Where the split ends, so the convolution branch below can take back any
    # step it is about to contradict.
    before_split = len(derivation.steps)
    pieces, delay = _split(transform, derivation)

    # -- invert ---------------------------------------------------------
    #
    # Two ways this fails, and both mean the same thing. sympy either returns
    # an unevaluated `InverseLaplaceTransform` or raises `NotImplementedError`,
    # depending on the forcing term: `e^{-t^2}` gives the object, `1/(1+t)`
    # raises. The object used to reach the screen *as the answer*, marked
    # unverified -- a student was shown sympy giving up, dressed as
    # mathematics.
    #
    # Both cases have the same shape: Y(s) is a product whose second factor has
    # no tabulated inverse. That is precisely when a course reaches for the
    # convolution theorem, so it is tried before the derivation is allowed to
    # fail -- and the integral it writes down is a complete answer whether or
    # not it evaluates.
    try:
        inverse = inverse_laplace_transform(pieces, _S, _T, noconds=True)
        answer = sp.simplify(_strip_unit_step(inverse))
        stuck = answer.has(sp.InverseLaplaceTransform)
    except (NotImplementedError, ValueError):
        answer, stuck = None, True

    if stuck:
        # Anything the split appended is about to be contradicted by "nothing
        # here splits into partial fractions", so it comes back off.
        del derivation.steps[before_split:]
        if _convolution(equation, function, ics, order, derivation):
            return
        derivation.message = (
            derivation.message
            or "the inverse transform has no elementary form"
        )
        return
    if delay is not None:
        answer = sp.simplify(_strip_unit_step(answer))
    derivation.steps.append(Step(
        title="Invert term by term",
        latex=_eq("y(t)", answer),
        note="Each piece is read backwards out of the table. The Heaviside "
             "factor the inversion attaches to every term is dropped: the "
             "transform only ever describes t ≥ 0, where it is 1.",
        verified=_round_trip(answer, transform),
    ))

    derivation.result = answer
    (derivation.verified, derivation.check,
     derivation.message) = _check(equation, function, answer, ics,
                                  derivation.message)


def _transfer_and_forcing(equation: sp.Eq, function: sp.Function, ics: dict,
                          order: int):
    """``(P(s), f(t))`` for ``P(s)Y(s) = F(s)``, or None if it is not that.

    The convolution route needs the equation split the way the theorem is
    stated: a transfer function on one side and a forcing term on the other.
    It only applies from rest -- with non-zero initial conditions the
    transformed equation carries extra polynomial terms, the answer is not a
    single product, and the theorem is not what a course would reach for.
    """
    if any(value != 0 for value in ics.values()):
        return None
    y = function(_T)
    expression = sp.expand(equation.lhs - equation.rhs)
    forcing = sp.simplify(-sum(term for term in sp.Add.make_args(expression)
                               if not term.has(y)))
    if forcing == 0 or not forcing.has(_T):
        return None

    # P(s) is read off the homogeneous side: each y^{(k)} becomes s^k, which
    # is exactly the derivative rule at rest.
    polynomial = sp.Integer(0)
    for term in sp.Add.make_args(sp.expand(expression + forcing)):
        for k in range(order, -1, -1):
            derivative = y.diff(_T, k) if k else y
            coefficient = term.coeff(derivative)
            if coefficient != 0 and not coefficient.has(y):
                if coefficient.has(_T):
                    return None          # not constant-coefficient
                polynomial += coefficient * _S**k
                break
        else:
            return None
    return sp.simplify(polynomial), forcing


def _convolution(equation: sp.Eq, function: sp.Function, ics: dict,
                 order: int, derivation: Derivation) -> bool:
    """Narrate ``y = g * f`` where inverting term by term will not work.

    Reached only once the ordinary route has failed, because partial fractions
    are what a course tries first and what it should be shown doing. When the
    forcing has no rational transform -- ``1/(1+t)``, ``e^{-t^2}``, ``ln t`` --
    there is nothing to split, and sympy's `inverse_laplace_transform` returns
    an unevaluated `InverseLaplaceTransform` object. That object used to reach
    the screen as the answer, marked unverified: a student was shown sympy
    giving up, dressed as mathematics.

    The convolution theorem is the textbook response, and it is a better answer
    than the one it replaces even when the integral does not evaluate, because
    the integral *is* what a textbook writes down.

    Returns whether it managed to say anything.
    """
    from sympy.integrals.laplace import inverse_laplace_transform

    parts = _transfer_and_forcing(equation, function, ics, order)
    if parts is None:
        return False
    polynomial, forcing = parts

    derivation.steps.append(Step(
        title="Y(s) is a product, not a sum",
        latex=(rf"Y(s) = \underbrace{{\frac{{1}}{{{sp.latex(polynomial)}}}}}"
               rf"_{{G(s)}}\; \underbrace{{F(s)}}_{{\mathcal{{L}}\{{"
               rf"{sp.latex(forcing)}\}}}}"),
        note="Nothing here splits into partial fractions — the forcing term "
             "has no rational transform to split. A product of two transforms "
             "is a convolution, which is what the theorem is for.",
        verified=bool(polynomial != 0),
    ))

    impulse = sp.simplify(_strip_unit_step(
        inverse_laplace_transform(1 / polynomial, _S, _T, noconds=True)
    ))
    if impulse.has(sp.InverseLaplaceTransform):
        derivation.message = (
            "the transfer function itself could not be inverted"
        )
        return False
    derivation.steps.append(Step(
        title="Invert the transfer function alone",
        latex=_eq("g(t)", impulse),
        note="G(s) is rational, so this half comes straight off the table. "
             "g is the impulse response — what the system does when struck "
             "once — and the convolution below is that response smeared over "
             "the whole history of the forcing.",
        # g solves the homogeneous equation, which is the claim being made.
        verified=_is_zero(sp.simplify(
            (equation.lhs - equation.rhs + forcing)
            .subs(function(_T), impulse).doit()
        )),
    ))

    tau = sp.Symbol("tau", positive=True)
    integrand = sp.simplify(impulse.subs(_T, _T - tau) * forcing.subs(_T, tau))
    derivation.steps.append(Step(
        title="The convolution theorem",
        latex=(rf"y(t) = (g * f)(t) = \int_0^{{t}} "
               rf"{sp.latex(integrand)}\, d\tau"),
        note="A product of transforms is the transform of a convolution. Note "
             "the order: g is shifted and reversed, f is not, and the "
             "integral runs over the interval from 0 to t.",
    ))

    evaluated = sp.integrate(integrand, (tau, 0, _T))
    if evaluated.has(sp.Integral):
        derivation.result = None
        derivation.message = (
            "the convolution integral is the answer, and is left in that "
            "form: it has no elementary closed form"
        )
        return True

    answer = sp.simplify(evaluated)
    derivation.steps.append(Step(
        title="Evaluate the integral",
        latex=_eq("y(t)", answer),
        note="This one comes out in closed form. Many do not, and a "
             "convolution integral left unevaluated is still a complete "
             "answer.",
        verified=_round_trip(answer, sp.simplify(1 / polynomial
                                                 * sp.laplace_transform(
                                                     forcing, _T, _S,
                                                     noconds=True))),
    ))
    derivation.result = answer
    (derivation.verified, derivation.check,
     derivation.message) = _check(equation, function, answer, ics,
                                  derivation.message)
    return True


def _split(transform, derivation: Derivation):
    """Partial fractions, and the second shifting theorem when there is a delay.

    `apart` cannot cope with an ``e^{-as}`` factor -- it raises
    `PolynomialError`, and that factor is present on exactly the switched and
    impulsive problems this technique is for. Splitting it off first is also
    the textbook move, so the obstacle and the teaching agree.
    """
    delay = _delay_of(transform)
    if delay is not None:
        shift, rest = delay
        try:
            parted = sp.apart(rest, _S)
        except sp.PolynomialError:
            parted = rest
        derivation.steps.append(Step(
            title="Split off the delay",
            latex=rf"Y(s) = e^{{-{sp.latex(shift)}s}}\,G(s), \qquad "
                  rf"G(s) = {sp.latex(parted)}",
            note=f"The factor e^(-{shift}s) is a delay, not something to expand. "
                 f"By the second shifting theorem it becomes u(t-{shift}) "
                 f"multiplying the inverse of G, shifted by {shift}: the answer "
                 f"is switched on at t = {shift} and is zero before it.",
            verified=_is_zero(sp.together(parted * sp.exp(-shift * _S)
                                          - transform)),
        ))
        return sp.exp(-shift * _S) * parted, shift

    try:
        parted = sp.apart(transform, _S)
    except sp.PolynomialError:
        return transform, None
    derivation.steps.append(Step(
        title="Split into partial fractions",
        latex=_eq("Y(s)", parted),
        note="Each piece is now something the table can invert on sight, which "
             "is the only reason partial fractions appear in this subject.",
        verified=_is_zero(sp.together(parted - transform)),
    ))
    return parted, None


def _delay_of(transform):
    """``(a, G(s))`` when the transform is a single ``e^{-as}G(s)``, else None.

    Only the single-delay case is split out. Several different delays added
    together would each need their own shift, and inverting the sum directly
    handles that correctly without claiming a step that was not taken.
    """
    factors = [f for f in sp.Mul.make_args(transform) if f.has(sp.exp)]
    if len(factors) != 1 or transform.is_Add:
        return None
    factor = factors[0]
    if not isinstance(factor, sp.exp):
        return None
    shift = sp.simplify(-factor.args[0] / _S)
    if shift.has(_S) or not shift.is_number or shift <= 0:
        return None
    return shift, sp.simplify(transform / factor)


def _round_trip(answer, transform) -> bool | None:
    """Transform the answer forward again and compare with `Y(s)`.

    An independent check on the inversion: it uses the table in the opposite
    direction, so a misread row does not cancel out.
    """
    from sympy.integrals.laplace import laplace_transform

    try:
        again = laplace_transform(answer, _T, _S, noconds=True)
        if again.has(sp.LaplaceTransform):
            return None
        return bool(sp.simplify(sp.together(again - transform)) == 0)
    except Exception:
        return None


def _check(equation, function, answer, ics, message):
    """Is the answer right? Symbolically if that can decide, numerically if not.

    Returns ``(verified, check, message)``, where `check` names the route that
    decided it so the interface never claims one that was not taken. False
    means demonstrably wrong; None means undecided, which is never presented
    as wrong.
    """
    impulsive = answer.has(sp.DiracDelta) or (equation.lhs - equation.rhs).has(
        sp.DiracDelta
    )
    if impulsive:
        return None, "", (
            message
            or "an impulse cannot be checked either way: substituting a "
               "switched answer back leaves impulse terms that never cancel, "
               "and DiracDelta has no numerical value to compare against. The "
               "answer is shown unchecked rather than claimed either right or "
               "wrong"
        )

    residual = None
    try:
        residual = sp.simplify(
            (equation.lhs - equation.rhs).subs(function(_T), answer).doit()
        )
    except Exception:
        residual = None

    if residual is not None and residual == 0:
        return True, "substitution", message
    if residual is not None and not residual.has(sp.DiracDelta):
        return False, "substitution", message

    # Substitution left distributional terms: differentiating a step produces
    # an impulse, and that never cancels even when the answer is right. Ask the
    # integrator instead.
    agrees = _agrees_numerically(equation, function, answer, ics)
    if agrees is True:
        return True, "numeric", (message or
                      "checked against this project's own solver: substituting "
                      "a switched answer back leaves impulse terms that cannot "
                      "be simplified away, so the two are compared numerically")
    if agrees is False:
        return False, "numeric", message
    return None, "", (message or "this answer could not be checked either way")


def _agrees_numerically(equation, function, answer, ics) -> bool | None:
    """Solve the same problem numerically and compare on a grid."""
    try:
        import numpy as np

        from odesuite import solve

        from .symbolic import EquationSpec, ParsedEquation, to_first_order
    except Exception:
        return None

    try:
        order = _order_of(equation, function)
        spec = EquationSpec(equations=["<laplace>"], t_span=(0.0, 6.0))
        parsed = ParsedEquation(spec=spec, equations=[equation],
                                functions=[function], order=order,
                                is_system=False, ics=ics)
        problem = to_first_order(parsed)
        solution = solve(problem, "dopri5", rtol=1e-10, atol=1e-12,
                         dense_output=True, max_steps=200_000)
        if not solution.success:
            return None

        exact = sp.lambdify(_T, answer, "numpy")
        times = np.linspace(problem.t0 + 1e-9, problem.tf, 40)
        predicted = np.asarray([float(exact(time)) for time in times])
        actual = solution.y_at(times)[0]
        scale = max(1.0, float(np.max(np.abs(actual))))
        return bool(np.max(np.abs(predicted - actual)) < 1e-5 * scale)
    except Exception:
        return None


def _unresolved(expression, function) -> bool:
    """Whether a transform other than ``Y(s)`` itself was left unevaluated."""
    return any(
        term.args[0] != function(_T)
        for term in expression.atoms(sp.LaplaceTransform)
    ) or expression.has(sp.LaplaceTransform)


def _differentiates_in_s(expression) -> bool:
    """Whether the transformed equation still contains d/ds.

    ``L{t·f(t)} = -F'(s)``, so a coefficient of t turns the equation into a
    differential one in s. The transform of a well-behaved constant-coefficient
    equation contains derivatives only inside the `Subs` that carries an
    initial condition, and those are with respect to t.
    """
    return any(
        any(variable == _S for variable, _ in derivative.variable_count)
        for derivative in expression.atoms(sp.Derivative)
    )


def _order_of(equation: sp.Eq, function: sp.Function) -> int:
    orders = [
        sum(count for _, count in derivative.variable_count)
        for derivative in (equation.lhs - equation.rhs).atoms(sp.Derivative)
        if derivative.expr == function(_T)
    ]
    return max(orders) if orders else 0
