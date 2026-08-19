"""The working, not just the answer.

`dsolve` returns a closed form and nothing else -- it does not expose the moves
it made, and a first ODE course is almost entirely about those moves. This
module narrates them: given an equation and the techniques that apply to it, it
writes out the derivation a student would produce on paper.

Five techniques, which is what a first course uses:

    separable · integrating factor · characteristic roots ·
    undetermined coefficients · Cauchy-Euler

Two things about the design matter more than the narration itself.

**Every step is checked, not merely printed.** After "integrate both sides" the
antiderivative is differentiated and compared with its integrand; after "read
the basis off the roots" each basis function is substituted into the equation
and required to give exactly zero; after "solve for the coefficients" the
particular solution is required to reproduce the forcing term exactly. A
derivation that prints a wrong intermediate line is worse than no derivation,
and this project's whole argument is that a claim gets checked.

**Anything else gets no derivation at all**, rather than a vague one. `derive`
returns None and the interface shows what it already showed: the closed form and
the classification. That degradation follows `SymbolicSolution`, which likewise
distinguishes *timed out* from *no method* from *found but unverified*.

Plain sympy in, plain data out -- no PySide6, and no dependency on the app's
dataclasses, because this runs inside the `dsolve` subprocess where neither is
available. `sp.integrate` and `sp.solve` can hang on user input just as `dsolve`
can, and that subprocess is the only thing in this application that can impose a
hard time limit on them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import sympy as sp

__all__ = [
    "Step",
    "Derivation",
    "derive",
    "preferred_hint",
    "TECHNIQUES",
    "TITLES",
]

_T = sp.Symbol("t", real=True)
_R = sp.Symbol("r")
_C = sp.Symbol("C")

#: The techniques this module narrates, **in teaching order**.
#:
#: This ordering is the point. `classify_ode` returns its hints ordered by what
#: sympy would rather solve with, which is not the order a course teaches them:
#: ``y'' + 3y' + 2y = 0`` leads with `factorable` and ``y' + 2y = t`` with
#: `1st_exact`. Picking the first hint would leave four of these five never
#: dispatched. Where several apply -- Newton's cooling is both separable and
#: linear -- the earlier one wins, which is the one met first on paper.
TECHNIQUES = (
    "separable",
    "1st_linear",
    "nth_linear_constant_coeff_homogeneous",
    "nth_linear_constant_coeff_undetermined_coefficients",
    "nth_linear_euler_eq_homogeneous",
)

#: What each technique is called in a textbook, rather than in sympy.
TITLES = {
    "separable": "Separation of variables",
    "1st_linear": "Integrating factor",
    "nth_linear_constant_coeff_homogeneous": "Characteristic roots",
    "nth_linear_constant_coeff_undetermined_coefficients":
        "Undetermined coefficients",
    "nth_linear_euler_eq_homogeneous": "Cauchy-Euler equation",
}


@dataclass
class Step:
    """One line of the derivation."""

    #: What the move is: "Integrate both sides".
    title: str
    #: The mathematics, as LaTeX. Rendered by `MathLabel` like any other.
    latex: str
    #: Why the move is legal, or what to notice about it.
    note: str = ""
    #: True/False where the step makes a checkable claim, None where it does
    #: not. "Separate the variables" is a rewriting; "integrate both sides"
    #: produces something that can be differentiated back.
    verified: bool | None = None


@dataclass
class Derivation:
    """A technique applied to an equation, start to finish."""

    #: The sympy hint that was narrated.
    technique: str
    #: Its textbook name.
    title: str
    steps: list[Step] = field(default_factory=list)
    #: The solution the derivation arrives at, or None if it could not finish.
    result: sp.Expr | None = None
    #: The result substituted back into the equation: the same check
    #: `symbolic._verify` applies to sympy's own answer.
    verified: bool | None = None
    #: How `verified` was decided, so the interface never names a check that
    #: was not the one performed. Empty means substitution, which is the usual
    #: route; `laplace` sets "numeric" where substituting a switched answer
    #: leaves impulse terms that cannot be simplified away.
    check: str = ""
    #: Why it stopped early, when it did.
    message: str = ""

    @property
    def complete(self) -> bool:
        return self.result is not None and self.verified is True


def preferred_hint(hints) -> str:
    """The technique to narrate, or "" if none of the five applies."""
    available = set(hints or ())
    for technique in TECHNIQUES:
        if technique in available:
            return technique
    # sympy spells the nonhomogeneous Cauchy-Euler hints differently, and both
    # of them start from the same substitution, so they narrate the homogeneous
    # part identically.
    for hint in hints or ():
        if hint.startswith("nth_linear_euler_eq"):
            return "nth_linear_euler_eq_homogeneous"
    return ""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def derive(equation: sp.Eq, function: sp.Function, *,
           hints=(), ics: dict | None = None) -> Derivation | None:
    """Narrate how `equation` is solved, or None if no technique here applies.

    `hints` is the whole tuple from `classify_ode`, not its first element --
    see `TECHNIQUES` for why that distinction decides whether this works at all.
    """
    technique = preferred_hint(hints)
    if not technique:
        return None

    builder = _BUILDERS[technique]
    derivation = Derivation(technique=technique, title=TITLES[technique])
    try:
        builder(equation, function, ics or {}, derivation)
    except Exception as exc:                       # a derivation must never crash
        derivation.message = (
            derivation.message
            or f"the derivation stopped early ({type(exc).__name__})"
        )
        return derivation

    if derivation.result is not None:
        derivation.verified = _satisfies(equation, function, derivation.result)
    return derivation


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _latex(expr) -> str:
    return expr if isinstance(expr, str) else sp.latex(expr)


def _eq(lhs, rhs) -> str:
    return f"{_latex(lhs)} = {_latex(rhs)}"


def _is_zero(expr) -> bool:
    """Whether `expr` simplifies to exactly zero.

    `simplify` returning something non-zero is not proof of anything, so this
    is used only to *confirm* a step, never to reject the derivation.
    """
    try:
        return bool(sp.simplify(expr) == 0)
    except Exception:
        return False


def _satisfies(equation: sp.Eq, function: sp.Function, candidate) -> bool | None:
    """Substitute `candidate` into `equation`; the check `_verify` already uses."""
    try:
        residual = (equation.lhs - equation.rhs).subs(
            function(_T), candidate
        ).doit()
        return bool(sp.simplify(residual) == 0)
    except Exception:
        return None


def _rhs_of(equation: sp.Eq, function: sp.Function):
    """``y'`` isolated: the right-hand side of ``y' = F(t, y)``."""
    derivative = function(_T).diff(_T)
    solutions = sp.solve(sp.Eq(equation.lhs, equation.rhs), derivative)
    if not solutions:
        raise ValueError("could not isolate y'")
    return sp.simplify(solutions[0])


def _first_order_coefficients(equation: sp.Eq, function: sp.Function):
    """``p`` and ``q`` from ``y' + p(t)y = q(t)``.

    The same `sp.Poly` idiom `symbolic.analyse_linear` uses, but without its
    constant-coefficient requirement -- an integrating factor is exactly the
    technique for when ``p`` depends on ``t``.
    """
    y, dy = function(_T), function(_T).diff(_T)
    expression = sp.expand(equation.lhs - equation.rhs)
    poly = sp.Poly(expression, y, dy)
    if poly.total_degree() > 1:
        raise ValueError("not linear in y")
    lead = poly.coeff_monomial(dy)
    if lead is None or lead == 0:
        raise ValueError("no y' term")
    p = sp.simplify((poly.coeff_monomial(y) or 0) / lead)
    q = sp.simplify(-(poly.coeff_monomial(1) or 0) / lead)
    return p, q, lead


def _apply_conditions(candidate, ics: dict, derivation: Derivation,
                      constants) -> None:
    """Solve for the arbitrary constants and add the closing step."""
    if not ics or not constants:
        derivation.result = candidate
        return

    equations = []
    for key, value in ics.items():
        point, order = _condition_point(key)
        if point is None:
            continue
        expression = candidate.diff(_T, order) if order else candidate
        equations.append(
            sp.Eq(expression.subs(_T, _exact(point)), _exact(value))
        )
    if not equations:
        derivation.result = candidate
        return

    found = sp.solve(equations, list(constants), dict=True)
    if not found:
        derivation.result = candidate
        derivation.message = "the initial conditions could not be applied"
        return

    particular = sp.simplify(candidate.subs(found[0]))
    assignments = ", ".join(
        _eq(symbol, value) for symbol, value in sorted(
            found[0].items(), key=lambda item: str(item[0])
        )
    )
    derivation.steps.append(Step(
        title="Apply the initial conditions",
        latex=assignments,
        note="The conditions pin the constants down; the answer below is the "
             "one curve through them.",
        verified=_conditions_hold(particular, ics),
    ))
    derivation.steps.append(Step(
        title="The particular solution",
        latex=_eq("y(t)", particular),
        verified=None,
    ))
    derivation.result = particular


def _exact(value):
    """``0.1`` as one tenth rather than as a float.

    A condition is typed as ``y(0) = 0.1`` and parses to a `Float`, which then
    propagates through `solve` into constants like ``log(-1/9)`` whose imaginary
    part is the *number* 3.14159… rather than `pi`. sympy cannot recognise that
    as pi, so ``e^{t + i·3.14159…}`` never collapses to ``-e^t`` and the answer
    is shown carrying a complex exponential it does not need.

    `rational=True` rationalises and nothing more -- it will not decide that a
    float was secretly pi, which would be inventing precision the user did not
    type.
    """
    try:
        if getattr(value, "atoms", None) and value.atoms(sp.Float):
            return sp.nsimplify(value, rational=True)
    except Exception:
        pass
    return value


def _condition_point(key):
    """``(point, derivative order)`` for an initial-condition key.

    Conditions arrive in two shapes -- ``y(0)`` and
    ``Subs(Derivative(y(t), t), t, 0)`` -- and handling only the first
    evaluates every derivative condition at the wrong place. That bug shipped
    once in `symbolic._satisfies_conditions`; `_condition_at` there is the same
    reading, kept separate because this module cannot import it.
    """
    if isinstance(key, sp.Subs):
        expression = key.expr
        point = key.point[0]
        order = (
            sum(count for _, count in expression.variable_count)
            if isinstance(expression, sp.Derivative) else 0
        )
        return point, order
    if isinstance(key, sp.Derivative):
        return None, 0
    if getattr(key, "args", None):
        return key.args[0], 0
    return None, 0


def _conditions_hold(candidate, ics: dict) -> bool | None:
    """Whether `candidate` meets the conditions: True, False, or *cannot tell*.

    False has to mean demonstrably wrong. Where the conditions were typed as
    decimals the residual is a floating-point crumb rather than exact zero, and
    calling that a failure would put a red cross on a correct step -- the same
    mistake `check_answer` is careful not to make with a student's answer.
    """
    try:
        for key, value in ics.items():
            point, order = _condition_point(key)
            if point is None:
                return None
            expression = candidate.diff(_T, order) if order else candidate
            residual = sp.simplify(
                expression.subs(_T, _exact(point)) - _exact(value)
            )
            if residual == 0:
                continue
            evaluated = sp.N(residual, 20)
            if not evaluated.is_number:
                return None                    # a parameter is still in there
            size = abs(complex(evaluated))
            scale = max(1.0, abs(complex(sp.N(_exact(value)))))
            if size > 1e-9 * scale:
                return False
        return True
    except Exception:
        return None


def _constants_in(expr) -> list[sp.Symbol]:
    """The ``C1``, ``C2``, ``C`` an expression still carries."""
    return sorted(
        (s for s in expr.free_symbols
         if s.name == "C" or (s.name.startswith("C") and s.name[1:].isdigit())),
        key=lambda s: s.name,
    )


# ---------------------------------------------------------------------------
# Separation of variables
# ---------------------------------------------------------------------------


def _separable(equation: sp.Eq, function: sp.Function, ics: dict,
               derivation: Derivation) -> None:
    rhs = _rhs_of(equation, function)

    # `separatevars` needs atoms, so `y(t)` stands in as a plain symbol for the
    # split and is put back afterwards.
    Y = sp.Symbol("Y")
    parts = sp.separatevars(rhs.subs(function(_T), Y), dict=True, symbols=[_T, Y])
    if not parts:
        derivation.message = "the right-hand side does not separate"
        return
    f_t = sp.simplify(parts["coeff"] * parts[_T])
    g_y = sp.simplify(parts[Y])

    # `Y` is scaffolding for `separatevars` and must never reach the reader.
    plain = sp.Symbol("y")
    g_shown = g_y.subs(Y, plain)
    product = (sp.Mul(f_t, g_shown, evaluate=False) if f_t != 1 else g_shown)

    derivation.steps.append(Step(
        title="Write it as a product",
        latex=_eq(r"\frac{dy}{dt}", product),
        note="Everything in t in one factor, everything in y in the other. "
             "This is what makes the equation separable.",
        verified=_is_zero(sp.expand(f_t * g_y.subs(Y, function(_T)) - rhs)),
    ))
    derivation.steps.append(Step(
        title="Separate the variables",
        latex=(rf"\frac{{dy}}{{{sp.latex(g_shown)}}} = "
               + ("dt" if f_t == 1 else rf"{sp.latex(f_t)}\, dt")),
        note="Divide by g(y) and multiply by dt. Dividing assumes g(y) is not "
             "zero — where it is, y is a constant solution in its own right.",
    ))

    left = sp.integrate(1 / g_y, Y)
    right = sp.integrate(f_t, _T)
    derivation.steps.append(Step(
        title="Integrate both sides",
        latex=_eq(left.subs(Y, plain), sp.Add(right, _C, evaluate=False)),
        note="One constant of integration suffices: the two would only differ "
             "by a constant anyway.",
        verified=(_is_zero(sp.diff(left, Y) - 1 / g_y)
                  and _is_zero(sp.diff(right, _T) - f_t)),
    ))

    solutions = sp.solve(sp.Eq(left.subs(Y, function(_T)), right + _C),
                         function(_T))
    if not solutions:
        derivation.message = (
            "the integrated form is correct but cannot be rearranged for y"
        )
        return
    general = sp.simplify(solutions[0])
    derivation.steps.append(Step(
        title="Solve for y",
        latex=_eq("y(t)", general),
        note="The general solution: one arbitrary constant, as a first-order "
             "equation must have.",
        verified=_satisfies(equation, function, general),
    ))
    _apply_conditions(general, ics, derivation, _constants_in(general))


# ---------------------------------------------------------------------------
# Integrating factor
# ---------------------------------------------------------------------------


def _integrating_factor(equation: sp.Eq, function: sp.Function, ics: dict,
                        derivation: Derivation) -> None:
    p, q, lead = _first_order_coefficients(equation, function)
    y = function(_T)

    derivation.steps.append(Step(
        title="Put it in standard form",
        latex=rf"y' + \left({sp.latex(p)}\right) y = {sp.latex(q)}",
        note="Divide through by the coefficient of y'. The technique needs the "
             "equation in exactly this shape.",
        # Dividing the original by that same coefficient has to give back
        # exactly this, or p and q have been misread.
        verified=_is_zero(sp.expand(
            (equation.lhs - equation.rhs) / lead - (y.diff(_T) + p * y - q)
        )),
    ))

    exponent = sp.integrate(p, _T)
    mu = sp.simplify(sp.exp(exponent))
    derivation.steps.append(Step(
        title="Form the integrating factor",
        latex=rf"\mu(t) = e^{{\int {sp.latex(p)}\, dt}} = {sp.latex(mu)}",
        note="Chosen so that mu' = p·mu, which is the whole trick.",
        verified=_is_zero(sp.diff(mu, _T) - p * mu),
    ))
    derivation.steps.append(Step(
        title="Multiply through by it",
        latex=rf"{sp.latex(mu)}\, y' + {sp.latex(sp.simplify(p * mu))}\, y"
              rf" = {sp.latex(sp.simplify(q * mu))}",
    ))
    derivation.steps.append(Step(
        title="The left side is a product rule",
        latex=_eq(rf"\frac{{d}}{{dt}}\left[{sp.latex(mu)}\, y\right]",
                  sp.simplify(q * mu)),
        note="Because mu' = p·mu, the two terms on the left are exactly the "
             "expansion of (mu·y)'.",
        verified=_is_zero(sp.expand(
            sp.diff(mu * y, _T) - (mu * y.diff(_T) + p * mu * y)
        )),
    ))

    integral = sp.integrate(sp.simplify(mu * q), _T)
    derivation.steps.append(Step(
        title="Integrate both sides",
        latex=_eq(rf"{sp.latex(mu)}\, y",
                  sp.Add(integral, _C, evaluate=False)),
        note="The left side integrates by inspection — it was arranged to.",
        verified=_is_zero(sp.diff(integral, _T) - sp.simplify(mu * q)),
    ))

    general = sp.simplify((integral + _C) / mu)
    derivation.steps.append(Step(
        title="Divide by the integrating factor",
        latex=_eq("y(t)", general),
        note="The general solution.",
        verified=_satisfies(equation, function, general),
    ))
    _apply_conditions(general, ics, derivation, _constants_in(general))


# ---------------------------------------------------------------------------
# Characteristic roots
# ---------------------------------------------------------------------------


def _order_of(equation: sp.Eq, function: sp.Function) -> int:
    orders = [
        sum(count for _, count in d.variable_count)
        for d in (equation.lhs - equation.rhs).atoms(sp.Derivative)
        if d.expr == function(_T)
    ]
    return max(orders) if orders else 0


def _coefficient(value) -> str:
    """``2t`` rather than ``2*t``, and plain ``t`` rather than ``1t``."""
    if value == 1:
        return "t"
    if value == -1:
        return "-t"
    return f"{sp.sstr(value)}t"


def _root_note(root, multiplicity: int) -> str:
    """What a root contributes, said the way a lecture says it."""
    real, imaginary = sp.re(root), sp.im(root)
    if imaginary == 0:
        if multiplicity == 1:
            return f"a simple real root, contributing e^({_coefficient(root)})"
        powers = ["1", "t"] + [f"t^{k}" for k in range(2, multiplicity)]
        return (f"a real root repeated {multiplicity} times, so it contributes "
                f"e^({_coefficient(root)}) multiplied by {', '.join(powers)}")
    part = "" if real == 0 else f"e^({_coefficient(real)}) times "
    angle = _coefficient(abs(imaginary))
    return (f"a complex pair, contributing {part}cos({angle}) and sin({angle}) "
            f"— real solutions, from complex roots, by Euler's formula")


def _roots_note(roots, order: int) -> str:
    """What the roots contribute, then what that makes the solution do.

    A conjugate pair is described once, matching the fundamental set, which
    counts it once too. Saying it twice made a second-order equation read as
    though it had four basis functions.
    """
    from .symbolic import describe_roots

    parts, seen = [], set()
    for root, multiplicity in roots:
        imaginary = sp.im(root)
        if imaginary != 0:
            key = (sp.simplify(sp.re(root)), sp.simplify(abs(imaginary)))
            if key in seen:
                continue
            seen.add(key)
        parts.append(_root_note(root, multiplicity))

    behaviour = describe_roots(roots, order)
    if behaviour:
        parts.append(behaviour)
    return "; ".join(parts)


def _characteristic_steps(equation: sp.Eq, function: sp.Function,
                          derivation: Derivation, analysis: dict) -> list:
    """The shared chain: trial exponential, polynomial, roots, basis.

    Used both on its own and as the first half of undetermined coefficients,
    which is exactly how a course uses it.

    `equation` must be the **homogeneous** equation. The basis solves that one,
    not the forced one -- checking against the forced equation reported the
    fundamental set as wrong, which it is not.
    """
    poly, roots = analysis["poly"], analysis["roots"]
    basis = analysis["fundamental_set"]

    derivation.steps.append(Step(
        title="Try an exponential",
        latex=r"y = e^{rt} \quad\Rightarrow\quad y^{(k)} = r^{k} e^{rt}",
        note="Every derivative of e^(rt) is a multiple of it, so the whole "
             "equation collapses to a polynomial in r.",
    ))
    derivation.steps.append(Step(
        title="The characteristic equation",
        latex=_eq(sp.factor(poly), 0),
        note="Divide through by e^(rt), which is never zero.",
        verified=_is_zero(sp.expand(sp.factor(poly) - poly)),
    ))

    listing = r" \qquad ".join(
        _eq("r", root) + (rf"\ (\times {mult})" if mult > 1 else "")
        for root, mult in roots
    )
    derivation.steps.append(Step(
        title="Its roots",
        latex=listing or r"\text{no roots}",
        note=_roots_note(roots, len(basis)),
        verified=all(_is_zero(poly.subs(_R, root)) for root, _ in roots),
    ))

    each_verified = [_satisfies(equation, function, b) for b in basis]
    derivation.steps.append(Step(
        title="The fundamental set",
        latex=r",\quad ".join(sp.latex(b) for b in basis),
        note="Each of these solves the equation on its own, and together they "
             "are independent — so every solution is a combination of them.",
        verified=all(v is True for v in each_verified) if basis else None,
    ))
    return basis


def _homogeneous(equation: sp.Eq, function: sp.Function, ics: dict,
                 derivation: Derivation) -> None:
    from .symbolic import analyse_linear

    analysis = analyse_linear(equation, function, _order_of(equation, function))
    if not analysis["poly"] or not analysis["fundamental_set"]:
        derivation.message = "no characteristic polynomial could be formed"
        return

    basis = _characteristic_steps(equation, function, derivation, analysis)
    constants = [sp.Symbol(f"C{i + 1}") for i in range(len(basis))]
    general = sum(c * b for c, b in zip(constants, basis))
    derivation.steps.append(Step(
        title="The general solution",
        latex=_eq("y(t)", general),
        note="An arbitrary constant for each member of the fundamental set — "
             f"{len(basis)} of them, matching the order of the equation.",
        verified=_satisfies(equation, function, general),
    ))
    _apply_conditions(general, ics, derivation, constants)


# ---------------------------------------------------------------------------
# Undetermined coefficients
# ---------------------------------------------------------------------------


def _trial_set(forcing, function: sp.Function, homogeneous_expr):
    """The terms to guess, with and without the resonance correction.

    `_undetermined_coefficients_match` is sympy's own ansatz chooser and is
    private. Reusing it is worth the risk -- choosing the trial set *is* this
    technique -- but the import is guarded, and `tests/test_steps.py` pins it so
    a sympy release that moves it fails loudly rather than silently dropping the
    technique.
    """
    try:
        from sympy.solvers.ode.nonhomogeneous import (
            _undetermined_coefficients_match as match,
        )
    except ImportError:                     # pragma: no cover - sympy moved it
        return None, None

    naive = match(forcing, _T, func=function(_T))
    corrected = match(forcing, _T, func=function(_T),
                      eq_homogeneous=homogeneous_expr)
    if not naive or not naive.get("test") or not corrected.get("test"):
        return None, None
    order = sp.default_sort_key
    return sorted(naive["trialset"], key=order), sorted(
        corrected["trialset"], key=order
    )


def _undetermined(equation: sp.Eq, function: sp.Function, ics: dict,
                  derivation: Derivation) -> None:
    from .symbolic import analyse_linear

    order = _order_of(equation, function)
    analysis = analyse_linear(equation, function, order)
    forcing = analysis["forcing"]
    if not analysis["poly"] or forcing in (None, 0):
        derivation.message = "no characteristic polynomial could be formed"
        return

    # The forcing term moved to the right: what "solve the homogeneous equation
    # first" actually means, and the equation the fundamental set solves.
    homogeneous_expr = sp.expand(equation.lhs - equation.rhs + forcing)
    homogeneous_eq = sp.Eq(homogeneous_expr, 0)

    basis = _characteristic_steps(homogeneous_eq, function, derivation, analysis)
    homogeneous_constants = [sp.Symbol(f"C{i + 1}") for i in range(len(basis))]
    y_h = sum(c * b for c, b in zip(homogeneous_constants, basis))
    derivation.steps.append(Step(
        title="That is the homogeneous solution",
        latex=_eq("y_h(t)", y_h),
        note="Solve the equation with the forcing term removed first; the "
             "answer is this plus any one solution of the full equation.",
        verified=_satisfies(homogeneous_eq, function, y_h),
    ))

    naive, corrected = _trial_set(forcing, function, homogeneous_expr)
    if not corrected:
        derivation.message = (
            "the forcing term is not one undetermined coefficients handles"
        )
        return

    y_p = _particular_by_guessing(
        equation, function, derivation, forcing, basis, naive, corrected
    )
    if y_p is None:
        return

    general = sp.simplify(y_h + y_p)
    derivation.steps.append(Step(
        title="The general solution",
        latex=_eq("y(t)", general),
        note="Homogeneous plus particular. The constants stay arbitrary until "
             "initial conditions are applied.",
        verified=_satisfies(equation, function, general),
    ))
    _apply_conditions(general, ics, derivation, homogeneous_constants)


def _particular_by_guessing(equation, function, derivation, forcing, basis,
                            naive, corrected):
    """The second half: guess a form, fix resonance, match coefficients.

    Split from `_undetermined` along the seam the technique itself has -- solve
    the homogeneous equation, then find one solution of the forced one.
    Returns ``y_p``, or None having recorded why it stopped.
    """
    derivation.steps.append(Step(
        title="Guess a form from the forcing term",
        latex=_eq("g(t)", forcing) + r",\quad \text{try } "
              + r" ,\ ".join(sp.latex(term) for term in naive),
        note="The guess has to be closed under differentiation — a sine brings "
             "in a cosine, so both appear.",
    ))
    if list(naive) != list(corrected):
        derivation.steps.append(Step(
            title="Correct for resonance",
            latex=r" ,\ ".join(sp.latex(term) for term in corrected),
            note="The first guess is already a solution of the homogeneous "
                 "equation, so it can never produce the forcing term. Multiply "
                 "by t until it is no longer in the fundamental set.",
            verified=any(
                any(_is_zero(term - b) for b in basis) for term in naive
            ),
        ))

    coefficients = [sp.Symbol(f"A{i + 1}") for i in range(len(corrected))]
    trial = sum(a * term for a, term in zip(coefficients, corrected))
    derivation.steps.append(Step(
        title="Substitute the guess",
        latex=_eq("y_p(t)", trial),
        note="Put this into the equation and collect like terms; the unknowns "
             "are the coefficients, and the equation must hold for every t.",
    ))

    residual = sp.expand(
        (equation.lhs - equation.rhs).subs(function(_T), trial).doit()
    )
    # `solve_undetermined_coeffs` is the public routine for exactly this: it
    # gathers the coefficient of each independent function of t and solves the
    # resulting linear system, which is the "match like terms" step done by
    # hand. Rolling it here would only reproduce it less well.
    found = sp.solve_undetermined_coeffs(sp.Eq(residual, 0), coefficients, _T)
    if not found:
        derivation.message = "the coefficients could not be solved for"
        return None

    y_p = sp.simplify(trial.subs(found))
    derivation.steps.append(Step(
        title="Solve for the coefficients",
        latex=", ".join(
            _eq(symbol, value)
            for symbol, value in sorted(found.items(), key=lambda i: str(i[0]))
        ) + r"\quad\Rightarrow\quad " + _eq("y_p(t)", y_p),
        note="Matching the coefficient of each independent function of t gives "
             "one linear equation per unknown.",
        verified=_is_zero(
            (equation.lhs - equation.rhs).subs(function(_T), y_p).doit()
        ),
    ))
    return y_p


# ---------------------------------------------------------------------------
# Cauchy-Euler
# ---------------------------------------------------------------------------


def _euler_basis(roots) -> list:
    """The basis a Cauchy-Euler indicial root contributes.

    The same shape as the constant-coefficient case with ``ln t`` in place of
    ``t``, which is the substitution ``t = e^s`` seen from the other side.
    """
    basis: list = []
    seen: set = set()
    for root, multiplicity in roots:
        real, imaginary = sp.re(root), sp.im(root)
        if imaginary == 0:
            for k in range(multiplicity):
                basis.append(_T**root * sp.log(_T)**k if k else _T**root)
        else:
            key = (sp.simplify(real), sp.simplify(abs(imaginary)))
            if key in seen:
                continue                       # a conjugate pair counts once
            seen.add(key)
            for k in range(multiplicity):
                prefix = sp.log(_T)**k if k else sp.Integer(1)
                basis.append(prefix * _T**real * sp.cos(abs(imaginary)
                                                        * sp.log(_T)))
                basis.append(prefix * _T**real * sp.sin(abs(imaginary)
                                                        * sp.log(_T)))
    return basis


def _cauchy_euler(equation: sp.Eq, function: sp.Function, ics: dict,
                  derivation: Derivation) -> None:
    expression = sp.expand(equation.lhs - equation.rhs)
    substituted = sp.expand(expression.subs(function(_T), _T**_R).doit())
    indicial = sp.simplify(sp.expand(substituted / _T**_R))
    if indicial.has(_T):
        derivation.message = "the substitution y = t^r did not clear t"
        return

    derivation.steps.append(Step(
        title="Try a power of t",
        latex=r"y = t^{r} \quad\Rightarrow\quad "
              r"t^{k} y^{(k)} = r(r-1)\cdots(r-k+1)\, t^{r}",
        note="Each t^k multiplying the k-th derivative cancels the t's it "
             "produces, so every term becomes a multiple of t^r.",
    ))
    derivation.steps.append(Step(
        title="The indicial equation",
        latex=_eq(sp.factor(indicial), 0),
        note="Divide through by t^r, which is non-zero for t > 0.",
        verified=_is_zero(sp.expand(sp.factor(indicial) - indicial)),
    ))

    try:
        roots = sp.roots(sp.Poly(indicial, _R))
    except Exception:
        derivation.message = "the indicial equation could not be solved"
        return
    try:
        ordered = sorted(roots.items(), key=lambda i: (sp.re(i[0]), sp.im(i[0])))
    except TypeError:
        ordered = sorted(roots.items(), key=lambda i: sp.default_sort_key(i[0]))

    derivation.steps.append(Step(
        title="Its roots",
        latex=r" \qquad ".join(
            _eq("r", root) + (rf"\ (\times {mult})" if mult > 1 else "")
            for root, mult in ordered
        ),
        verified=all(_is_zero(indicial.subs(_R, root)) for root, _ in ordered),
    ))

    basis = _euler_basis(ordered)
    if not basis:
        derivation.message = "no basis could be read off the indicial roots"
        return
    derivation.steps.append(Step(
        title="The fundamental set",
        latex=r",\quad ".join(sp.latex(b) for b in basis),
        note="A repeated root brings in ln t rather than t, and a complex pair "
             "gives cos(b ln t) and sin(b ln t) — the substitution t = e^s "
             "turns this into the constant-coefficient case.",
        verified=all(_satisfies(equation, function, b) is True for b in basis),
    ))

    constants = [sp.Symbol(f"C{i + 1}") for i in range(len(basis))]
    general = sum(c * b for c, b in zip(constants, basis))
    derivation.steps.append(Step(
        title="The general solution",
        latex=_eq("y(t)", general),
        verified=_satisfies(equation, function, general),
    ))
    _apply_conditions(general, ics, derivation, constants)


_BUILDERS = {
    "separable": _separable,
    "1st_linear": _integrating_factor,
    "nth_linear_constant_coeff_homogeneous": _homogeneous,
    "nth_linear_constant_coeff_undetermined_coefficients": _undetermined,
    "nth_linear_euler_eq_homogeneous": _cauchy_euler,
}
