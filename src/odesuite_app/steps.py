"""The working, not just the answer.

`dsolve` returns a closed form and nothing else -- it does not expose the moves
it made, and a first ODE course is almost entirely about those moves. This
module narrates them: given an equation and the techniques that apply to it, it
writes out the derivation a student would produce on paper.

Nine techniques, which is what a first course uses:

    separable · integrating factor · exact · homogeneous substitution ·
    Bernoulli · characteristic roots · undetermined coefficients ·
    variation of parameters · Cauchy-Euler

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
#: The two substitutions come *after* the two plain first-order techniques
#: deliberately. Measured: ``y' + 2y = t``, ``y' = (t+y)/t`` and
#: ``y' = -(3t²+2y)/(2t+1)`` all carry `Bernoulli` in their hint tuples, and
#: the second carries `1st_homogeneous_coeff_best` too. Listing either earlier
#: would start narrating equations a course solves by integrating factor as
#: substitutions instead.
#:
#: Homogeneous comes before Bernoulli because a textbook meets it first, and
#: because equations that are both -- ``y' = (t² + y²)/(t y)`` is the standard
#: example of one -- are taught as homogeneous.
#:
#: Variation of parameters comes after undetermined coefficients for the same
#: reason, and the measurement is even more one-sided: sympy names *both* on
#: every constant-coefficient forced equation tried -- ``y'' + 4y = sin t`` and
#: ``y'' + 3y' + 2y = e^t`` among them. Listing variation earlier would narrate
#: Wronskians for every equation a first course solves by guessing a form.
#: Variation is reached only where guessing has nothing to offer, which is
#: exactly when sympy names it alone: ``y'' + y = sec t`` carries no
#: undetermined-coefficients hint at all.
TECHNIQUES = (
    "separable",
    "1st_linear",
    "1st_homogeneous_coeff_best",
    "Bernoulli",
    "nth_linear_constant_coeff_homogeneous",
    "nth_linear_constant_coeff_undetermined_coefficients",
    "nth_linear_constant_coeff_variation_of_parameters",
    "nth_linear_euler_eq_homogeneous",
)

#: What each technique is called in a textbook, rather than in sympy.
TITLES = {
    "separable": "Separation of variables",
    "1st_linear": "Integrating factor",
    "Bernoulli": "Bernoulli substitution",
    "1st_homogeneous_coeff_best": "Homogeneous substitution",
    "1st_exact": "Exact equation",
    "nth_linear_constant_coeff_homogeneous": "Characteristic roots",
    "nth_linear_constant_coeff_undetermined_coefficients":
        "Undetermined coefficients",
    "nth_linear_constant_coeff_variation_of_parameters":
        "Variation of parameters",
    "nth_linear_euler_eq_homogeneous": "Cauchy-Euler equation",
    "reduction_of_order": "Reduction of order",
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


#: Where sympy spells one technique several ways, and every spelling narrates
#: identically. Prefix -> the technique to use. Scanned in order, after the
#: exact names in `TECHNIQUES`, so a hint tuple naming both still gets the
#: earlier technique.
_ALIASES = (
    # Nonhomogeneous Cauchy-Euler is spelled differently, and both start from
    # the same substitution.
    ("nth_linear_euler_eq", "nth_linear_euler_eq_homogeneous"),
    # `..._subs_dep_div_indep` and `..._subs_indep_div_dep` are the same
    # substitution written the two ways round.
    ("1st_homogeneous_coeff", "1st_homogeneous_coeff_best"),
    # `Bernoulli_Integral` is the same technique with the integral left
    # unevaluated.
    ("Bernoulli", "Bernoulli"),
    # `..._variation_of_parameters_Integral`, likewise. Our own narration
    # evaluates the integrals where sympy can, and says so where it cannot,
    # so the two spellings are one technique here.
    ("nth_linear_constant_coeff_variation_of_parameters",
     "nth_linear_constant_coeff_variation_of_parameters"),
)


def preferred_hint(hints) -> str:
    """The technique to narrate, or "" if none of them applies."""
    available = set(hints or ())
    for technique in TECHNIQUES:
        if technique in available:
            return technique
    for hint in hints or ():
        for prefix, technique in _ALIASES:
            if hint.startswith(prefix):
                return technique
    return ""


def detected(equation: sp.Eq, function: sp.Function) -> str:
    """A technique recognised structurally, or "".

    `classify_ode` is authoritative about the techniques it names well, and it
    is not authoritative about exactness -- see `_DETECTORS`. This is only ever
    consulted once the hints have been exhausted.
    """
    for technique, detector in _DETECTORS:
        try:
            if detector(equation, function):
                return technique
        except Exception:
            continue
    return ""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def derive(equation: sp.Eq, function: sp.Function, *,
           hints=(), ics: dict | None = None) -> Derivation | None:
    """Narrate how `equation` is solved, or None if no technique here applies.

    `hints` is the whole tuple from `classify_ode`, not its first element --
    see `TECHNIQUES` for why that distinction decides whether this works at all.
    Where the hints name nothing, the equation is examined directly; today that
    finds exact equations, which `classify_ode` cannot be trusted about.
    """
    equation = _exact(equation)
    technique = preferred_hint(hints) or detected(equation, function)
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


#: A stand-in for t with the assumption the real `_T` lacks. `t` is declared
#: real project-wide, which is right for plotting and wrong for simplifying:
#: sympy will not reduce ((2t/3)^(3/2))^(1/3) to (2t/3)^(1/2) without knowing
#: t is positive, because for negative t it is not true.
_T_POSITIVE = sp.Symbol("t", positive=True)

#: Where `vanishes` evaluates a residual that would not simplify, and the value
#: every other free symbol -- a constant C1, a parameter -- is given there.
#: Positive times, because the positive-t retry is the one that just failed and
#: a solution valid only for t > 0 must not be condemned at t < 0; irregular
#: values, so that no sample lands on a special point by accident.
_PROBE_TIMES = (0.37, 0.81, 1.29, 2.03)
_PROBE_VALUE = 0.731


def vanishes(residual) -> tuple[bool | None, str]:
    """Whether a substituted residual is zero, and on what domain.

    Three answers, not two, and "not simplified" is never "wrong":

    1. It simplifies to zero: ``(True, "")``.
    2. It simplifies to zero once t is known positive: ``(True, "t > 0")``.
       ``y = (2t/3)^(3/2)`` solves ``y' = y^(1/3)`` -- the slope-fields
       lesson's own example of non-uniqueness -- and was graded *wrong*,
       because with t merely real the cube root of its cube will not cancel.
    3. Otherwise it is evaluated at a few positive times. Measurably nonzero
       anywhere it is finite: ``(False, "")``, because that is a proof. Zero
       at every sample: ``(None, "")`` -- strong evidence, not a proof, and
       this function never claims more than it has.
    """
    try:
        if sp.simplify(residual) == 0:
            return True, ""
        if sp.simplify(residual.subs(_T, _T_POSITIVE)) == 0:
            return True, "t > 0"
    except Exception:
        pass
    others = {symbol: _PROBE_VALUE for symbol in residual.free_symbols
              if symbol is not _T}
    for time in _PROBE_TIMES:
        try:
            value = complex(residual.subs(others).subs(_T, time).evalf())
        except Exception:
            continue
        if not (abs(value) < float("inf")):
            continue
        if abs(value) > 1e-9:
            return False, ""
    return None, ""


def _satisfies(equation: sp.Eq, function: sp.Function, candidate) -> bool | None:
    """Substitute `candidate` into `equation`; the check `_verify` already uses.

    True where the residual vanishes, including only for t > 0 -- a
    narrator's answer involving t^(3/2) or ln t is a solution there and
    nowhere else, which is how every textbook states it.
    """
    try:
        residual = (equation.lhs - equation.rhs).subs(
            function(_T), candidate
        ).doit()
        return vanishes(residual)[0]
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

    Floats reach here from two places -- a condition typed as ``y(0) = 0.1``,
    and a coefficient typed as ``y' = 2 - 0.05*y`` -- and both cause the same
    damage. They propagate through `solve` into constants like ``log(-7/4)``
    whose imaginary part is the *number* 3.14159… rather than `pi`. sympy
    cannot recognise that as pi, so ``e^{-t/20 + i·3.14159…}`` never collapses
    to ``-e^{-t/20}`` and a mixing-tank answer that should read
    ``40 - 35e^{-t/20}`` is shown carrying a complex exponential instead.

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
               derivation: Derivation, *, variable: str = "y") -> None:
    """Separate, integrate, rearrange.

    `variable` names the unknown in the *displayed* mathematics. It is "y" for
    an equation somebody typed, and "v" when a substitution builder hands its
    own equation here: the moves are identical and the letters are not, and a
    derivation that called v "y" would misreport what it had just done.
    """
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

    # `Y` is scaffolding for `separatevars` and must never reach the reader --
    # and what replaces it is the variable actually being solved for, which is
    # `v` when a substitution builder handed this equation over.
    plain = sp.Symbol(variable)
    g_shown = g_y.subs(Y, plain)
    product = (sp.Mul(f_t, g_shown, evaluate=False) if f_t != 1 else g_shown)

    derivation.steps.append(Step(
        title="Write it as a product",
        latex=_eq(rf"\frac{{d{variable}}}{{dt}}", product),
        note="Everything in t in one factor, everything in y in the other. "
             "This is what makes the equation separable.",
        verified=_is_zero(sp.expand(f_t * g_y.subs(Y, function(_T)) - rhs)),
    ))
    derivation.steps.append(Step(
        title="Separate the variables",
        latex=(rf"\frac{{d{variable}}}{{{sp.latex(g_shown)}}} = "
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

    # `solve` raises rather than returning nothing on a transcendental
    # rearrangement -- ``atan(v) + ln(v²+1)/2 = -ln t + C`` is a real one,
    # reached by the homogeneous substitution. The integrated form above is
    # still correct and still worth showing, so this degrades to the message
    # below rather than losing the whole derivation to an exception.
    try:
        solutions = sp.solve(sp.Eq(left.subs(Y, function(_T)), right + _C),
                             function(_T))
    except (NotImplementedError, sp.PolynomialError):
        solutions = []
    if not solutions:
        derivation.message = (
            "the integrated form is correct but cannot be rearranged for y"
        )
        return
    general = sp.simplify(_pick_branch(solutions, ics, equation, function))
    derivation.steps.append(Step(
        title=f"Solve for {variable}",
        latex=_eq(f"{variable}(t)", _branches_latex(solutions, ics, general)),
        note="The general solution: one arbitrary constant, as a first-order "
             "equation must have."
             + ("" if len(solutions) < 2 else
                "  Rearranging gave two branches; this is the one the initial "
                "condition sits on." if ics else
                "  Rearranging gave two branches — which one applies depends on "
                "the initial condition."),
        verified=_satisfies(equation, function, general),
    ))
    _apply_conditions(general, ics, derivation, _constants_in(general))


def _branches_latex(solutions, ics: dict, chosen):
    r"""The right-hand side a "Solve for y" step shows (SYM-03).

    With a condition, the branch it sits on -- `_pick_branch` has chosen it.
    Without one, *every* branch: showing one of two as "the general solution"
    silently discards half the family, and ``y' = -t/y`` came out as
    ``y = -sqrt(2C - t^2)`` with nothing on the page to say the upper half of
    every circle existed. Two branches are written the way a textbook writes
    them, as a centre plus or minus a half-difference, which gives both
    ``\pm\sqrt{2C - t^2}`` and the exact equation's
    ``-t^2/2 \pm \sqrt{4C + t^4}/2``; anything else is listed.
    """
    if ics or len(solutions) < 2:
        return sp.latex(chosen)
    if len(solutions) == 2:
        first, second = solutions
        centre = sp.simplify((first + second) / 2)
        half = sp.simplify((first - second) / 2)
        if half.could_extract_minus_sign():
            half = -half
        if centre == 0:
            return rf"\pm {sp.latex(half)}"
        return rf"{sp.latex(centre)} \pm {sp.latex(half)}"
    return r"\quad\text{or}\quad ".join(sp.latex(sp.simplify(branch))
                                         for branch in solutions)


def _pick_branch(solutions, ics: dict, equation=None, function=None):
    """The branch the initial condition actually sits on.

    Solving ``y²/2 = t²/2 + C`` for y gives a positive and a negative root, and
    taking the first was picking the negative one regardless. With ``y(0) = 2``
    that is the wrong half of the curve: the answer still satisfies the
    equation, so nothing complained, but no choice of C makes it pass through
    the given point.
    """
    if len(solutions) < 2 or not ics:
        return solutions[0]
    on_the_point = [candidate for candidate in solutions
                    if _passes_through(candidate, ics)]
    # Several branches can pass through the point -- for y' = y^(1/3) and
    # y(0) = 0 both roots do, with C = 0 -- and only one of them may solve the
    # equation: under sympy's principal cube root, -(2t/3)^(3/2) does not. The
    # first was being taken, so the lesson on non-uniqueness narrated an
    # answer its own check then marked unverified.
    #
    # Ranked rather than filtered: a proven solution first, then one the
    # numeric probe could not fault, and a proven non-solution only if nothing
    # else passes through the point. With C still free the right branch here
    # is usually only "not faulted" -- (C + t)^(3/2) will not simplify.
    if equation is not None and len(on_the_point) > 1:
        rank = {True: 0, None: 1, False: 2}
        return min(on_the_point,
                   key=lambda candidate: rank[_satisfies(equation, function,
                                                         candidate)])
    return on_the_point[0] if on_the_point else solutions[0]


def _passes_through(candidate, ics: dict) -> bool:
    """Whether some choice of the constants puts `candidate` on the condition."""
    constants = _constants_in(candidate)
    if not constants:
        return bool(_conditions_hold(candidate, ics))
    try:
        equations = []
        for key, value in ics.items():
            point, order = _condition_point(key)
            if point is None:
                continue
            expression = (candidate.diff(_T, order) if order else candidate)
            equations.append(
                sp.Eq(expression.subs(_T, _exact(point)), _exact(value))
            )
        found = sp.solve(equations, list(constants), dict=True)
    except Exception:
        return False
    return bool(found) and bool(_conditions_hold(candidate.subs(found[0]), ics))


# ---------------------------------------------------------------------------
# Integrating factor
# ---------------------------------------------------------------------------


def _integrating_factor(equation: sp.Eq, function: sp.Function, ics: dict,
                        derivation: Derivation, *,
                        variable: str = "y") -> None:
    """Standard form, integrating factor, integrate, divide.

    `variable` names the unknown in the displayed mathematics; see
    `_separable`, which takes it for the same reason.
    """
    p, q, lead = _first_order_coefficients(equation, function)
    y = function(_T)

    derivation.steps.append(Step(
        title="Put it in standard form",
        latex=rf"{variable}' + \left({sp.latex(p)}\right) {variable}"
              rf" = {sp.latex(q)}",
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
        latex=rf"{sp.latex(mu)}\, {variable}' + "
              rf"{sp.latex(sp.simplify(p * mu))}\, {variable}"
              rf" = {sp.latex(sp.simplify(q * mu))}",
    ))
    derivation.steps.append(Step(
        title="The left side is a product rule",
        latex=_eq(rf"\frac{{d}}{{dt}}\left[{sp.latex(mu)}\, {variable}"
                  rf"\right]", sp.simplify(q * mu)),
        note=f"Because mu' = p·mu, the two terms on the left are exactly "
             f"the expansion of (mu·{variable})'.",
        verified=_is_zero(sp.expand(
            sp.diff(mu * y, _T) - (mu * y.diff(_T) + p * mu * y)
        )),
    ))

    integral = sp.integrate(sp.simplify(mu * q), _T)
    derivation.steps.append(Step(
        title="Integrate both sides",
        latex=_eq(rf"{sp.latex(mu)}\, {variable}",
                  sp.Add(integral, _C, evaluate=False)),
        note="The left side integrates by inspection — it was arranged to.",
        verified=_is_zero(sp.diff(integral, _T) - sp.simplify(mu * q)),
    ))

    general = sp.simplify((integral + _C) / mu)
    derivation.steps.append(Step(
        title="Divide by the integrating factor",
        latex=_eq(f"{variable}(t)", general),
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
# Variation of parameters
#
# The technique that finishes the job undetermined coefficients starts. Guessing
# a form needs the forcing term to be closed under differentiation, and `sec t`,
# `tan t` and `e^t/t` are not -- there is no finite trial set to guess, so the
# other technique has nothing to say about them. Measured: sympy names
# `..._variation_of_parameters` alone on all three, and names it *alongside*
# undetermined coefficients on every forced equation that does have a trial set.
# See `TECHNIQUES` for why that decides the ordering.
#
# Written for order n rather than the usual two. The 2x2 formulas
# ``u1' = -y2 g / W``, ``u2' = y1 g / W`` are Cramer's rule on the n x n system
# below, and the system costs no more to write: measured on the third-order
# ``y''' + y' = tan t``, solving it took 0.05 s and integrating 0.04 s. Hard-
# coding the pair would have meant a second implementation for the higher-order
# lesson, saying the same thing less generally.
# ---------------------------------------------------------------------------


def _wronskian(basis: list):
    """``W(y1..yn)``, simplified.

    The simplify is load-bearing rather than cosmetic: on ``cos t, sin t`` the
    determinant comes back as ``sin²t + cos²t``, and a step showing that as the
    Wronskian would be showing its arithmetic instead of its answer.
    """
    rows = [[b.diff(_T, k) for b in basis] for k in range(len(basis))]
    return sp.simplify(sp.Matrix(rows).det())


def _standard_form(equation: sp.Eq, function: sp.Function, order: int):
    """``(g, lead)``: the forcing once the leading coefficient is divided out.

    The step everybody skips and then gets wrong. ``t²y'' + ty' - y = t³`` has
    forcing ``t`` in the formula, not ``t³``, and every u' after it inherits
    the error.
    """
    expression = sp.expand(equation.lhs - equation.rhs)
    lead = sp.simplify(expression.coeff(function(_T).diff(_T, order)))
    if lead == 0:
        return None, None
    forcing = sp.simplify(
        -sum(term for term in sp.Add.make_args(expression)
             if not term.has(function(_T)))
    )
    return sp.simplify(forcing / lead), lead


def _variation_particular(equation: sp.Eq, function: sp.Function,
                          basis: list, derivation: Derivation):
    """``y_p`` by varying the constants of `basis`, or None having said why.

    `basis` solves the homogeneous equation; this finds the one solution of the
    forced one that the general solution is missing. Shared by the
    constant-coefficient builder and by `_cauchy_euler`, which reaches the same
    point by a different route and then needs exactly this.
    """
    order = len(basis)
    g, lead = _standard_form(equation, function, order)
    if g is None:
        derivation.message = "the leading coefficient could not be read off"
        return None

    if lead != 1:
        derivation.steps.append(Step(
            title="Divide by the leading coefficient",
            latex=_eq("g(t)", g),
            note="The formula below is stated for y⁽ⁿ⁾ + … = g(t). Using the "
                 "forcing term before dividing is the most common way to get "
                 "this technique wrong.",
        ))

    wronskian = _wronskian(basis)
    derivation.steps.append(Step(
        title="The Wronskian",
        latex=_eq("W", wronskian),
        note="The determinant of the basis and its derivatives. That it is "
             "non-zero is what says these solutions are independent — and it "
             "is what the system below is divided by, so it has to be.",
        verified=bool(wronskian != 0),
    ))
    if wronskian == 0:
        derivation.message = "the Wronskian is zero, so the basis is dependent"
        return None

    # Sum(u_i' y_i^(k)) = 0 for every derivative but the last, and = g for it.
    # Those n-1 zeros are a choice, not a consequence: they are what keeps the
    # derivatives of y_p from growing new u'' terms, and they are why the
    # technique is only n equations rather than a mess.
    matrix = sp.Matrix([[b.diff(_T, k) for b in basis] for k in range(order)])
    target = sp.Matrix([0] * (order - 1) + [g])
    try:
        primes = [sp.simplify(value) for value in matrix.solve(target)]
    except Exception:
        derivation.message = "the system for the u' could not be solved"
        return None

    derivation.steps.append(Step(
        title="Solve for the derivatives of the coefficients",
        latex=r",\qquad ".join(
            _eq(f"u_{{{i + 1}}}'", value) for i, value in enumerate(primes)
        ),
        note="Let the constants vary, and impose that their derivatives "
             "contribute nothing to the first n−1 derivatives of y_p. That "
             "leaves one equation per unknown.",
        verified=_is_zero(sp.simplify(
            sum(u * b.diff(_T, order - 1) for u, b in zip(primes, basis)) - g
        )),
    ))

    integrals = [sp.integrate(value, _T) for value in primes]
    if any(item.has(sp.Integral) for item in integrals):
        derivation.message = (
            "the formula is right but the integrals for u have no closed form"
        )
        return None

    derivation.steps.append(Step(
        title="Integrate",
        latex=r",\qquad ".join(
            _eq(f"u_{{{i + 1}}}", value) for i, value in enumerate(integrals)
        ),
        note="No constants of integration here — they would only rebuild the "
             "homogeneous solution, which is already accounted for.",
        verified=all(_is_zero(sp.simplify(item.diff(_T) - prime))
                     for item, prime in zip(integrals, primes)),
    ))

    y_p = sp.simplify(sum(u * b for u, b in zip(integrals, basis)))
    derivation.steps.append(Step(
        title="Assemble the particular solution",
        latex=_eq("y_p(t)", y_p),
        note="Each basis function carried by its own coefficient rather than "
             "a constant. That is the whole idea, and it is where the name "
             "comes from.",
        verified=_is_zero(sp.simplify(
            (equation.lhs - equation.rhs).subs(function(_T), y_p).doit()
        )),
    ))
    return y_p


def _variation(equation: sp.Eq, function: sp.Function, ics: dict,
               derivation: Derivation) -> None:
    from .symbolic import analyse_linear

    order = _order_of(equation, function)
    analysis = analyse_linear(equation, function, order)
    forcing = analysis["forcing"]
    if not analysis["poly"] or forcing in (None, 0):
        derivation.message = "no characteristic polynomial could be formed"
        return

    homogeneous_expr = sp.expand(equation.lhs - equation.rhs + forcing)
    basis = _characteristic_steps(
        sp.Eq(homogeneous_expr, 0), function, derivation, analysis
    )
    if not basis:
        derivation.message = "no fundamental set could be read off the roots"
        return

    constants = [sp.Symbol(f"C{i + 1}") for i in range(len(basis))]
    y_h = sum(c * b for c, b in zip(constants, basis))
    derivation.steps.append(Step(
        title="That is the homogeneous solution",
        latex=_eq("y_h(t)", y_h),
        note="As with undetermined coefficients, the forced equation is "
             "solved by this plus any one solution of the full equation.",
        verified=_satisfies(sp.Eq(homogeneous_expr, 0), function, y_h),
    ))
    derivation.steps.append(Step(
        title="Guessing a form will not work here",
        latex=_eq("g(t)", forcing),
        note="Undetermined coefficients needs a forcing term whose derivatives "
             "close up into a finite list. This one's do not, so there is "
             "nothing to guess — and that is exactly when this technique is "
             "reached for.",
    ))

    y_p = _variation_particular(equation, function, basis, derivation)
    if y_p is None:
        return

    general = sp.simplify(y_h + y_p)
    derivation.steps.append(Step(
        title="The general solution",
        latex=_eq("y(t)", general),
        note="Homogeneous plus particular, as before. The constants stay "
             "arbitrary until initial conditions are applied.",
        verified=_satisfies(equation, function, general),
    ))
    _apply_conditions(general, ics, derivation, constants)


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

    # The forcing term has to come off before the substitution, not after.
    # Leaving it in put a bare `t³` alongside the `t^r` terms, so `indicial`
    # still contained t and the builder gave up having appended *no steps at
    # all* -- a forced Cauchy-Euler used to produce an empty derivation.
    # Splitting on `has(y(t))` is exact here because the equation is linear in
    # y and its derivatives; measured, `t³` and `log t` both come off cleanly.
    homogeneous_expr = sp.expand(
        sum(term for term in sp.Add.make_args(expression)
            if term.has(function(_T)))
    )
    forcing = sp.simplify(homogeneous_expr - expression)

    substituted = sp.expand(
        homogeneous_expr.subs(function(_T), _T**_R).doit()
    )
    indicial = sp.simplify(sp.expand(substituted / _T**_R))
    if indicial.has(_T):
        derivation.message = "the substitution y = t^r did not clear t"
        return

    homogeneous_eq = sp.Eq(homogeneous_expr, 0)
    if forcing != 0:
        derivation.steps.append(Step(
            title="Set the forcing aside first",
            latex=_eq("g(t)", forcing),
            note="A power of t only balances the left side when the right is "
                 "zero, so solve the homogeneous equation first and come back "
                 "for one solution of the forced one.",
            verified=_is_zero(sp.expand(homogeneous_expr - forcing
                                        - expression)),
        ))

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
        # Against the homogeneous equation, which is what the basis solves.
        # Checking it against a forced equation would report a correct
        # fundamental set as wrong.
        verified=all(_satisfies(homogeneous_eq, function, b) is True
                     for b in basis),
    ))

    constants = [sp.Symbol(f"C{i + 1}") for i in range(len(basis))]
    general = sum(c * b for c, b in zip(constants, basis))

    if forcing != 0:
        derivation.steps.append(Step(
            title="That is the homogeneous solution",
            latex=_eq("y_h(t)", general),
            note="Now for one solution of the forced equation. Guessing a "
                 "form has no theory behind it here — the coefficients are "
                 "not constant — so the constants are varied instead.",
            verified=_satisfies(homogeneous_eq, function, general),
        ))
        y_p = _variation_particular(equation, function, basis, derivation)
        if y_p is None:
            return
        general = sp.simplify(general + y_p)
        derivation.steps.append(Step(
            title="The general solution",
            latex=_eq("y(t)", general),
            note="Homogeneous plus particular, as for any linear equation.",
            verified=_satisfies(equation, function, general),
        ))
    else:
        derivation.steps.append(Step(
            title="The general solution",
            latex=_eq("y(t)", general),
            verified=_satisfies(equation, function, general),
        ))
    _apply_conditions(general, ics, derivation, constants)


# ---------------------------------------------------------------------------
# Exact equations
#
# The one technique here that `classify_ode` cannot be asked for. Measured on
# this sympy: of six exact equations, it named `1st_exact` for three, missed it
# entirely on the three the lesson exists for -- `y' = -(2t+y)/(t+3y^2)` comes
# back as `1st_power_series, lie_group` -- and *offered* it on `y' = -y/t^2`,
# which is not exact under this splitting. So exactness is decided here, by the
# test a course teaches, and never taken from a hint.
# ---------------------------------------------------------------------------


def _split_exact(equation: sp.Eq, function: sp.Function):
    """``y' = -M/N`` as ``(M, N, Y)``, with `Y` standing in for y.

    The plain symbol is needed because the exactness test differentiates with
    respect to y as a *variable*, which `y(t)` is not.
    """
    Y = sp.Symbol("Y")
    rhs = _rhs_of(equation, function).subs(function(_T), Y)
    numerator, denominator = sp.fraction(sp.together(-rhs))
    return sp.expand(numerator), sp.expand(denominator), Y


def _degree_in(expression, symbol) -> int:
    """The polynomial degree in `symbol`, or -1 if it is not polynomial."""
    try:
        return int(sp.Poly(expression, symbol).degree())
    except (sp.PolynomialError, sp.GeneratorsNeeded, TypeError, ValueError):
        return -1


def _is_exact(equation: sp.Eq, function: sp.Function) -> bool:
    """Whether ``M dt + N dy = 0`` has ∂M/∂y = ∂N/∂t.

    Never raises: it is asked about every equation no named technique fits.

    First order only. It used to be asked about second-order equations too,
    and ``y'' + t y' + y = 0`` passed: the split treated y' as the unknown's
    rate and found an "exact" first-order equation that is not this one, so
    the narrator printed a solution, C/t, that fails its own check.
    """
    if _order_of(equation, function) != 1:
        return False
    try:
        M, N, Y = _split_exact(equation, function)
    except Exception:
        return False
    if N == 0 or not (M.has(Y) or N.has(Y)):
        return False              # nothing to be exact about
    return _is_zero(sp.diff(M, Y) - sp.diff(N, _T))


def _exact_equation(equation: sp.Eq, function: sp.Function, ics: dict,
                    derivation: Derivation) -> None:
    M, N, Y = _split_exact(equation, function)
    plain = sp.Symbol("y")

    derivation.steps.append(Step(
        title="Write it as M dt + N dy = 0",
        latex=(rf"\left({sp.latex(M.subs(Y, plain))}\right) dt + "
               rf"\left({sp.latex(N.subs(Y, plain))}\right) dy = 0"),
        note="Clear the fraction and put everything on one side. M is what "
             "multiplies dt, N what multiplies dy.",
        verified=_is_zero(sp.simplify(
            _rhs_of(equation, function) + (M / N).subs(Y, function(_T))
        )),
    ))

    dM, dN = sp.simplify(sp.diff(M, Y)), sp.simplify(sp.diff(N, _T))
    derivation.steps.append(Step(
        title="Test for exactness",
        latex=(rf"\frac{{\partial M}}{{\partial y}} = "
               rf"{sp.latex(dM.subs(Y, plain))} = "
               rf"{sp.latex(dN.subs(Y, plain))} = "
               rf"\frac{{\partial N}}{{\partial t}}"),
        note="These agreeing is what says the left side is already the "
             "derivative of something. If they differed, no ψ would exist and "
             "the method would not apply.",
        verified=_is_zero(dM - dN),
    ))

    partial = sp.integrate(M, _T)
    derivation.steps.append(Step(
        title="Integrate M with respect to t",
        latex=(rf"\psi(t, y) = {sp.latex(partial.subs(Y, plain))} + h(y)"),
        note="Holding y fixed. The constant of integration may depend on y, "
             "which is what h(y) is for.",
        verified=_is_zero(sp.diff(partial, _T) - M),
    ))

    remainder = sp.simplify(N - sp.diff(partial, Y))
    h = sp.integrate(remainder, Y)
    derivation.steps.append(Step(
        title="Pin h(y) by matching N",
        latex=(rf"h'(y) = {sp.latex(remainder.subs(Y, plain))}"
               rf"\quad\Longrightarrow\quad h(y) = {sp.latex(h.subs(Y, plain))}"),
        note="∂ψ/∂y has to equal N. What is left over involves y alone — and "
             "that it does is exactly what the exactness test bought.",
        # Two claims: the leftover really is free of t, and h integrates back.
        verified=(not remainder.has(_T)
                  and _is_zero(sp.diff(h, Y) - remainder)),
    ))

    psi = sp.simplify(partial + h)
    derivation.steps.append(Step(
        title="The solution is ψ = C",
        latex=_eq(sp.latex(psi.subs(Y, plain)), _C),
        note="Along a solution curve ψ does not change, because dψ = M dt + "
             "N dy is zero. That is the whole method.",
        verified=(_is_zero(sp.diff(psi, _T) - M)
                  and _is_zero(sp.diff(psi, Y) - N)),
    ))

    # Only rearrange where rearranging helps. Measured: a ψ quartic in y sends
    # `solve` past sixty seconds, and a cubic one returns in under a second but
    # as three lines of nested radicals nobody would write down. A textbook
    # leaves those implicit, and so does this.
    if _degree_in(psi, Y) > 2:
        derivation.message = (
            "ψ(t, y) = C is the answer, and is left in that form: solving it "
            "for y would give radicals rather than anything worth reading"
        )
        return

    solutions = sp.solve(sp.Eq(psi, _C), Y)
    if not solutions:
        derivation.message = (
            "the answer is correct but implicit: ψ(t, y) = C cannot be "
            "rearranged for y"
        )
        return
    general = sp.simplify(_pick_branch(solutions, ics, equation, function))
    derivation.steps.append(Step(
        title="Solve for y",
        latex=_eq("y(t)", _branches_latex(solutions, ics, general)),
        note="The general solution."
             + ("" if len(solutions) < 2 else
                "  Rearranging gave several branches; this is the one the "
                "initial condition sits on." if ics else
                "  Rearranging gave several branches — which one applies "
                "depends on the initial condition."),
        verified=_satisfies(equation, function, general),
    ))
    _apply_conditions(general, ics, derivation, _constants_in(general))


# ---------------------------------------------------------------------------
# Bernoulli
# ---------------------------------------------------------------------------


def _signed_branch(candidate, equation: sp.Eq, function: sp.Function,
                   ics: dict):
    """The sign of `candidate` the initial condition sits on.

    Both substitution builders end by undoing a root -- ``y = v^{1/(1-n)}``,
    or ``y = t·v`` where v came out of a square -- and an even root leaves a
    sign that nothing before the condition can settle. The inner builder never
    saw the condition (it was solving in v), so this is the first point at
    which the question can be asked.

    The negated branch is offered only once it has been checked to solve the
    equation too, so an odd root -- where there is no second branch -- cannot
    be handed a wrong answer that merely happens to pass through the point.
    """
    if not ics:
        return candidate
    candidates = [candidate]
    if _satisfies(equation, function, -candidate) is True:
        candidates.append(-candidate)
    return _pick_branch(candidates, ics)


def _bernoulli_parts(equation: sp.Eq, function: sp.Function):
    """``(p, q, n)`` for ``y' + p y = q y^n``, or None if it is not that.

    `n` may be negative -- ``y' = (t² + y²)/(t y)`` is ``y' - y/t = t·y^{-1}``
    -- so the powers are read off term by term rather than through `Poly`,
    which refuses a negative exponent.
    """
    Y = sp.Symbol("Y")
    rhs = sp.expand(_rhs_of(equation, function).subs(function(_T), Y))
    powers: dict[int, sp.Expr] = {}
    for term in sp.Add.make_args(rhs):
        coefficient, exponent = term.as_coeff_exponent(Y)
        if coefficient.has(Y) or not exponent.is_Integer:
            return None
        index = int(exponent)
        powers[index] = powers.get(index, sp.Integer(0)) + coefficient

    powers = {index: value for index, value in powers.items() if value != 0}
    if len(powers) != 2 or 1 not in powers:
        return None
    n = next(index for index in powers if index != 1)
    if n in (0, 1):
        return None
    return -powers[1], powers[n], sp.Integer(n)


def _bernoulli(equation: sp.Eq, function: sp.Function, ics: dict,
               derivation: Derivation) -> None:
    parts = _bernoulli_parts(equation, function)
    if parts is None:
        derivation.message = "this is not y' + p(t)y = q(t)y^n"
        return
    p, q, n = parts
    power = sp.Integer(1) - n

    derivation.steps.append(Step(
        title="Put it in Bernoulli form",
        latex=(rf"y' + \left({sp.latex(p)}\right) y = "
               rf"\left({sp.latex(q)}\right) y^{{{sp.latex(n)}}}"),
        note="Linear except for the power on the right. That single term is "
             "the whole difficulty, and the substitution below removes it.",
        verified=_is_zero(sp.simplify(
            _rhs_of(equation, function)
            - (-p * function(_T) + q * function(_T) ** n)
        )),
    ))
    derivation.steps.append(Step(
        title=f"Substitute v = y^{{{sp.latex(power)}}}",
        latex=(rf"v = y^{{{sp.latex(power)}}}, \qquad "
               rf"v' = {sp.latex(power)}\, y^{{{sp.latex(-n)}}}\, y'"),
        note="Chosen so that dividing the equation by y^n turns every term "
             "into one in v. The exponent is 1 − n, and nothing else works.",
    ))

    v = sp.Function("v")
    v_equation = sp.Eq(v(_T).diff(_T) + power * p * v(_T), power * q)
    derivation.steps.append(Step(
        title="It is linear in v",
        latex=(rf"v' + \left({sp.latex(sp.simplify(power * p))}\right) v = "
               rf"{sp.latex(sp.simplify(power * q))}"),
        note="The same equation, in a variable that makes it linear. From "
             "here it is the integrating factor, exactly as usual.",
        # Substituting v = y^{1-n} back has to reproduce the original equation
        # divided by y^n -- the division that motivated the substitution.
        verified=_is_zero(sp.simplify(
            ((v_equation.lhs - v_equation.rhs)
             .subs(v(_T), function(_T) ** power).doit())
            - power * function(_T) ** (-n)
            * (function(_T).diff(_T) + p * function(_T)
               - q * function(_T) ** n)
        )),
    ))

    # `ics` are conditions on y, not on v, so the hand-off gets none of them:
    # they are applied once, at the end, to the answer in y.
    _integrating_factor(v_equation, v, {}, derivation, variable="v")
    v_general = derivation.result
    if v_general is None:
        derivation.message = derivation.message or "the linear step failed"
        return

    general = _signed_branch(
        sp.simplify(sp.Pow(v_general, sp.Rational(1, int(power)))),
        equation, function, ics,
    )
    derivation.steps.append(Step(
        title="Undo the substitution",
        latex=_eq("y(t)", general),
        note=f"y = v^(1/({sp.sstr(power)})), which is where the root in the "
             "answer comes from."
             + ("  An even root leaves a sign to choose, and the initial "
                "condition is what chooses it." if ics else ""),
        verified=_satisfies(equation, function, general),
    ))
    derivation.result = None            # `_apply_conditions` sets it properly
    _apply_conditions(general, ics, derivation, _constants_in(general))


# ---------------------------------------------------------------------------
# Homogeneous substitution
# ---------------------------------------------------------------------------


def _homogeneous_substitution(equation: sp.Eq, function: sp.Function,
                              ics: dict, derivation: Derivation) -> None:
    V = sp.Symbol("V")
    rhs = _rhs_of(equation, function)
    in_v = sp.simplify(rhs.subs(function(_T), V * _T))
    if in_v.has(_T):
        derivation.message = "the right-hand side does not depend on y/t alone"
        return

    derivation.steps.append(Step(
        title="Everything depends on y/t",
        latex=_eq("y'", in_v.subs(V, sp.Symbol("y/t"))),
        note="t and y appear only in that ratio. An equation of this shape is "
             "called homogeneous, and the ratio is what to substitute for.",
        verified=not in_v.has(_T),
    ))
    derivation.steps.append(Step(
        title="Substitute y = v·t",
        latex=r"y = v\,t, \qquad y' = v + t\,v'",
        note="Differentiate the substitution by the product rule. The v on "
             "the right is what will cancel against the equation.",
    ))

    v = sp.Function("v")
    v_rhs = sp.simplify((in_v - V) / _T).subs(V, v(_T))
    v_equation = sp.Eq(v(_T).diff(_T), v_rhs)
    derivation.steps.append(Step(
        title="Now it separates",
        latex=_eq("v'", sp.simplify((in_v - V) / _T).subs(V, sp.Symbol("v"))),
        note="v + t·v' = F(v), so t·v' = F(v) − v. The variables come apart, "
             "which they did not before.",
        verified=_is_zero(sp.simplify(
            v_rhs.subs(v(_T), function(_T) / _T)
            - (rhs - function(_T) / _T) / _T
        )),
    ))

    # As in `_bernoulli`: the conditions are on y, so they are applied once, at
    # the end, and never to the answer in v.
    _separable(v_equation, v, {}, derivation, variable="v")
    v_general = derivation.result
    if v_general is None:
        derivation.message = derivation.message or "the separable step failed"
        return

    general = _signed_branch(sp.simplify(_T * v_general),
                             equation, function, ics)
    derivation.steps.append(Step(
        title="Undo the substitution",
        latex=_eq("y(t)", general),
        note="y = v·t, so multiply the answer in v by t."
             + ("  Separating left a square root, and the initial condition "
                "is what decides its sign." if ics else ""),
        verified=_satisfies(equation, function, general),
    ))
    derivation.result = None            # `_apply_conditions` sets it properly
    _apply_conditions(general, ics, derivation, _constants_in(general))


# ---------------------------------------------------------------------------
# Reduction of order
# ---------------------------------------------------------------------------


def _standard_second_order(equation: sp.Eq, function: sp.Function):
    """``(P, Q)`` for ``y'' + P y' + Q y = 0``, or None.

    None unless the equation is second order, linear, homogeneous, and has a
    coefficient that is not constant -- the constant case has characteristic
    roots and a technique of its own, which a course meets first.
    """
    if _order_of(equation, function) != 2:
        return None
    y = function(_T)
    second, first, zeroth = sp.symbols("_Y2 _Y1 _Y0")
    expr = sp.expand((equation.lhs - equation.rhs)
                     .subs(y.diff(_T, 2), second)
                     .subs(y.diff(_T), first)
                     .subs(y, zeroth))
    if expr.has(function):
        return None
    try:
        poly = sp.Poly(expr, second, first, zeroth)
    except sp.PolynomialError:
        return None
    if poly.total_degree() != 1 or poly.coeff_monomial(1) != 0:
        return None
    a = poly.coeff_monomial(second)
    b = poly.coeff_monomial(first)
    c = poly.coeff_monomial(zeroth)
    if a == 0:
        return None
    p, q = sp.simplify(b / a), sp.simplify(c / a)
    if not (p.has(_T) or q.has(_T)):
        return None
    return p, q


#: What a first solution is looked for among, in the order a course would try
#: them. A textbook *gives* y1 for this technique; the narrator has no box to
#: be given it in, so it does what a student does on seeing none -- try the
#: obvious forms and keep the first that substitutes to zero. Each candidate
#: is checked, never assumed, so a lucky guess cannot produce a wrong answer.
_TRIAL_SOLUTIONS = (
    _T, _T**2, sp.exp(_T), sp.exp(-_T), 1 / _T, _T**3, sp.exp(2 * _T),
    sp.exp(-2 * _T), 1 + _T, _T**-2, sp.exp(3 * _T), sp.Integer(1),
)


def _first_solution(p, q):
    for candidate in _TRIAL_SOLUTIONS:
        residual = (candidate.diff(_T, 2) + p * candidate.diff(_T)
                    + q * candidate)
        if _is_zero(residual) or _is_zero(residual.subs(_T, _T_POSITIVE)):
            return candidate
    return None


def _reducible(equation: sp.Eq, function: sp.Function) -> bool:
    coefficients = _standard_second_order(equation, function)
    return coefficients is not None and _first_solution(*coefficients) is not None


def _reduction_of_order(equation: sp.Eq, function: sp.Function, ics: dict,
                        derivation: Derivation) -> None:
    coefficients = _standard_second_order(equation, function)
    if coefficients is None:
        derivation.message = "this is not a second-order linear homogeneous equation"
        return
    p, q = coefficients
    derivation.steps.append(Step(
        title="Divide through by the leading coefficient",
        latex=_eq(sp.Symbol("y''") + p * sp.Symbol("y'") + q * sp.Symbol("y"), 0),
        note="The method is stated for y'' + P(t)y' + Q(t)y = 0, and P is "
             "read off this form. Reading it off the equation as written, with "
             "a coefficient still in front of y'', gives the wrong P.",
    ))

    y1 = _first_solution(p, q)
    if y1 is None:
        derivation.message = ("no first solution could be found by trying "
                              "powers and exponentials")
        return
    derivation.steps.append(Step(
        title="Find one solution",
        latex=_eq("y_1(t)", y1),
        note="Reduction of order needs one solution to start from. A textbook "
             "usually supplies it; here it was found by trying powers of t and "
             "exponentials, and substituting this one gives zero.",
        verified=_satisfies(equation, function, y1),
    ))

    w_symbol = sp.Symbol("w")
    reduced = sp.simplify(2 * y1.diff(_T) / y1 + p)
    derivation.steps.append(Step(
        title="Look for the second as y = v·y₁",
        latex=(r"y_1 v'' + \left(2y_1' + P y_1\right) v' = 0"
               r"\quad\Longrightarrow\quad " + _eq(sp.Symbol("w'"),
                                                   -reduced * w_symbol)),
        note="Substituting y = v·y₁ gives three groups of terms, and the one "
             "multiplying v is y₁'' + P y₁' + Q y₁, which is zero because y₁ is "
             "a solution. What is left has no v in it, only v' and v'' — so "
             "w = v' satisfies a first-order equation. That is the reduction.",
    ))

    exponent = sp.integrate(p, _T)
    w = sp.simplify(sp.exp(-exponent) / y1**2)
    derivation.steps.append(Step(
        title="Solve for w = v'",
        latex=_eq("w(t)", w),
        note="The equation for w is separable: w = e^(−∫P dt) / y₁². The "
             "constant of integration is dropped here — any nonzero multiple "
             "of w gives a second solution just as good.",
        verified=_is_zero(w.diff(_T) + reduced * w)
        or _is_zero((w.diff(_T) + reduced * w).subs(_T, _T_POSITIVE)),
    ))

    v_of_t = sp.integrate(w, _T)
    if v_of_t.has(sp.Integral):
        derivation.message = ("the integral for v has no elementary form, so "
                              "the second solution stays an integral")
        return
    y2 = sp.simplify(v_of_t * y1)
    derivation.steps.append(Step(
        title="Integrate for v, and multiply by y₁",
        latex=_eq("v(t)", v_of_t) + r",\qquad " + _eq("y_2(t)", y2),
        note="Again the constant of integration is left out: it would only add "
             "a multiple of y₁ to y₂, which the general solution already has.",
        verified=_satisfies(equation, function, y2),
    ))

    wronskian = sp.simplify(y1 * y2.diff(_T) - y1.diff(_T) * y2)
    derivation.steps.append(Step(
        title="The two are independent",
        latex=_eq("W(y_1, y_2)", wronskian),
        note="The Wronskian is y₁² v' = y₁² w, which is never zero where y₁ is "
             "not — so y₂ is not a multiple of y₁, and the pair is a "
             "fundamental set.",
        verified=None if wronskian == 0 else True,
    ))

    constants = [sp.Symbol("C1"), sp.Symbol("C2")]
    general = constants[0] * y1 + constants[1] * y2
    derivation.steps.append(Step(
        title="The general solution",
        latex=_eq("y(t)", general),
        verified=_satisfies(equation, function, general),
    ))
    _apply_conditions(general, ics, derivation, constants)


_BUILDERS = {
    "separable": _separable,
    "1st_linear": _integrating_factor,
    "Bernoulli": _bernoulli,
    "1st_homogeneous_coeff_best": _homogeneous_substitution,
    "1st_exact": _exact_equation,
    "nth_linear_constant_coeff_homogeneous": _homogeneous,
    "nth_linear_constant_coeff_undetermined_coefficients": _undetermined,
    "nth_linear_constant_coeff_variation_of_parameters": _variation,
    "nth_linear_euler_eq_homogeneous": _cauchy_euler,
    "reduction_of_order": _reduction_of_order,
}

#: Techniques `classify_ode` cannot be relied on to name, and how to recognise
#: them ourselves. Consulted by `derive` only when no named technique applies,
#: so an equation a course would solve by separation or an integrating factor
#: still gets the method it is met by first.
_DETECTORS = (
    ("1st_exact", _is_exact),
    ("reduction_of_order", _reducible),
)
