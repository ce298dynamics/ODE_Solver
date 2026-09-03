"""Linear systems, by the eigenvalue method.

Two equations that will not come apart. ``x' = x + 2y``, ``y' = 3x + 2y`` is
not two problems -- neither unknown can be solved for without the other -- and
the whole content of a first course on systems is that writing it as a matrix
makes it one problem again, whose answer is read off the eigenvalues.

The narration is the chain a course writes on the board:

    write it as x' = A x · det(A - lambda I) = 0 · the eigenvalues ·
    an eigenvector for each · the general solution · the initial conditions ·
    what the origin is

The interesting part is the fifth move, which has three cases, and they are the
three a course spends its time on. **Real distinct** eigenvalues give a plain
combination of exponentials. A **complex pair** gives complex answers that must
be turned back into real ones, and the step that does it is Euler's formula
applied to the eigenvector as well as the exponential -- which is the move
people find hardest and which is therefore shown in full. A **defective**
matrix has fewer eigenvectors than it needs, and the missing solution comes
from a generalised eigenvector solving ``(A - lambda I)w = v``; the answer
carries a ``t`` for the same reason a repeated characteristic root does.

Everything is checked rather than asserted. The matrix is reconstructed into
the original equations, the characteristic polynomial is expanded back, every
eigenvector is put through ``A v = lambda v``, every basis solution is
substituted into the system, and the constants pinned by initial conditions are
checked at the initial point.

Plain sympy in, plain data out -- no PySide6. Results are `steps.Derivation`,
which already has a renderer and a wire format, exactly as `laplace` does.
"""

from __future__ import annotations

import sympy as sp

from .steps import Derivation, Step, _is_zero

__all__ = ["derive", "matrix_of", "split_system", "classify",
           "fundamental_matrix", "TITLE"]

_T = sp.Symbol("t", real=True)
_L = sp.Symbol("lambda")

TITLE = "Eigenvalue method"

#: How a planar system's origin is named, by the eigenvalue signature. The same
#: vocabulary `analysis.classify` uses for a numerically located fixed point --
#: the two must agree, because a student can see both on one screen.
_SADDLE = "saddle"


def _latex(expr) -> str:
    return expr if isinstance(expr, str) else sp.latex(expr)


def _eq(lhs, rhs) -> str:
    return f"{_latex(lhs)} = {_latex(rhs)}"


def split_system(equations, functions):
    """``(A, f)`` for ``x' = A x + f(t)``, or None when it is not that.

    Constant coefficients and first order; the forcing may be anything in `t`.
    A `t` in a *coefficient*, a product of unknowns, or a second derivative all
    mean the eigenvalue method does not apply as stated, and saying so plainly
    beats narrating a method whose hypotheses have failed.
    """
    states = [f(_T) for f in functions]
    rows, forcing = [], []
    for equation, function in zip(equations, functions):
        derivative = function(_T).diff(_T)
        solved = sp.solve(equation, derivative, dict=True)
        if not solved:
            return None
        rhs = sp.expand(solved[0][derivative])
        row = []
        for state in states:
            coefficient = rhs.coeff(state)
            if coefficient.has(_T) or any(coefficient.has(s) for s in states):
                return None
            row.append(sp.simplify(coefficient))
        # Whatever is left once the linear part is removed is the forcing. It
        # may depend on t, and it may be zero -- which is the homogeneous case
        # and the one every other lesson in the unit is about.
        remainder = sp.simplify(rhs - sum(c * s for c, s in zip(row, states)))
        if any(remainder.has(state) for state in states):
            return None
        rows.append(row)
        forcing.append(remainder)
    return sp.Matrix(rows), sp.Matrix(forcing)


def matrix_of(equations, functions):
    """``A`` for a *homogeneous* ``x' = A x``, or None.

    Kept as the narrower question because most of this module asks it: the
    eigenvalue method proper is about the homogeneous system, and forcing is
    handled by varying the constants afterwards.
    """
    parts = split_system(equations, functions)
    if parts is None or any(entry != 0 for entry in parts[1]):
        return None
    return parts[0]


def classify(eigenvalues) -> str:
    """What the origin is, in the words a course uses.

    Read off the eigenvalues alone, which is the point of computing them: the
    shape of every trajectory is decided before a single one is drawn.
    """
    values = list(eigenvalues)
    if len(values) != 2:
        real = [sp.re(v) for v in values]
        if all(r.is_negative for r in real):
            return "stable"
        if any(r.is_positive for r in real):
            return "unstable"
        return "neither stable nor unstable"

    first, second = values
    if any(sp.im(v) != 0 for v in values):
        real = sp.re(first)
        if real == 0:
            return "a centre — closed orbits, neither growing nor decaying"
        if real.is_negative:
            return "a stable spiral — it winds inwards"
        return "an unstable spiral — it winds outwards"

    if first * second < 0:
        return f"a {_SADDLE} — one direction in, one direction out"
    if first == second:
        inward = "stable" if first.is_negative else "unstable"
        return f"a degenerate node, {inward}"
    if first.is_negative and second.is_negative:
        return "a stable node — every trajectory runs into it"
    if first.is_positive and second.is_positive:
        return "an unstable node — every trajectory runs away from it"
    return "a line of equilibria — one eigenvalue is zero"


def derive(equations, functions, *, ics: dict | None = None) -> Derivation:
    """Solve the system by eigenvalues, and narrate every move."""
    derivation = Derivation(technique="systems", title=TITLE)
    try:
        _build(equations, functions, ics or {}, derivation)
    except Exception as exc:                     # never propagate into the app
        derivation.message = (
            derivation.message
            or f"the eigenvalue method stopped early ({type(exc).__name__})"
        )
    return derivation


def _build(equations, functions, ics: dict, derivation: Derivation) -> None:
    parts = split_system(equations, functions)
    if parts is None:
        derivation.message = (
            "the eigenvalue method needs a first-order system with constant "
            "coefficients"
        )
        return
    matrix, forcing = parts
    driven = any(entry != 0 for entry in forcing)

    states = [f(_T) for f in functions]
    vector = sp.Matrix(states)

    derivation.steps.append(Step(
        title="Write it as one matrix equation",
        latex=(rf"\frac{{d}}{{dt}}{sp.latex(vector)} = "
               rf"{sp.latex(matrix)}{sp.latex(vector)}"
               + (rf" + {sp.latex(forcing)}" if driven else "")),
        note="Neither equation can be solved without the other, so they stop "
             "being two problems and become one. Everything that follows is "
             "about the matrix, not about the equations."
             + ("  The forcing rides along on the right, and is set aside "
                "until the homogeneous part is solved." if driven else ""),
        # The matrix and the forcing have to reproduce the equations they came
        # from -- both of them, not merely the matrix.
        verified=all(
            _is_zero(sp.simplify(
                sp.solve(equation, function(_T).diff(_T), dict=True)[0][
                    function(_T).diff(_T)]
                - (matrix * vector + forcing)[index]
            ))
            for index, (equation, function) in enumerate(zip(equations,
                                                             functions))
        ),
    ))

    size = matrix.shape[0]
    characteristic = sp.expand((matrix - _L * sp.eye(size)).det())
    derivation.steps.append(Step(
        title="The characteristic equation",
        latex=_eq(rf"\det(A - \lambda I) = {sp.latex(sp.factor(characteristic))}",
                  0),
        note="A non-zero vector v with Av = λv exists exactly when A − λI is "
             "singular, and a matrix is singular exactly when its determinant "
             "is zero. That is the whole derivation of this step.",
        verified=_is_zero(sp.expand(sp.factor(characteristic)
                                    - characteristic)),
    ))

    eigen = matrix.eigenvects()
    if not eigen:
        derivation.message = "the eigenvalues could not be found"
        return
    ordered = sorted(eigen, key=lambda item: sp.default_sort_key(item[0]))
    values = [value for value, multiplicity, _ in ordered
              for _ in range(multiplicity)]

    derivation.steps.append(Step(
        title="Its roots are the eigenvalues",
        latex=r",\qquad ".join(
            _eq(r"\lambda", value)
            + (rf"\ (\times {multiplicity})" if multiplicity > 1 else "")
            for value, multiplicity, _ in ordered
        ),
        note="Each eigenvalue contributes a solution that grows or decays "
             "like e^{λt}. Their signs decide the long run before any "
             "trajectory is drawn.",
        verified=all(_is_zero(characteristic.subs(_L, value))
                     for value, _, _ in ordered),
    ))

    total = sum(len(vectors) for _, _, vectors in ordered)
    defective = total < size
    if any(sp.im(value) != 0 for value in values):
        basis = _complex_basis(matrix, ordered, derivation)
    elif defective:
        basis = _defective_basis(matrix, ordered, derivation)
    else:
        basis = _distinct_basis(matrix, ordered, derivation)

    if basis is None or len(basis) < size:
        derivation.message = (
            derivation.message
            or "a full set of independent solutions could not be built"
        )
        return

    constants = [sp.Symbol(f"C{i + 1}") for i in range(size)]
    general = sp.zeros(size, 1)
    for constant, column in zip(constants, basis):
        general += constant * column
    general = sp.simplify(general)

    derivation.steps.append(Step(
        title=("The homogeneous solution" if driven
               else "The general solution"),
        latex=_eq(sp.latex(vector), sp.latex(general)),
        note=f"One arbitrary constant per equation, as a {size}×{size} system "
             "must have."
             + ("  Now for one solution of the forced system."
                if driven else
                "  Every solution of the system is one of these."),
        verified=_solves(matrix, general),
    ))

    if not driven:
        derivation.steps.append(Step(
            title="What the origin is",
            latex=_eq(r"\text{origin}", sp.latex(sp.Matrix([0] * size).T)),
            note=f"Read off the eigenvalues alone: {classify(values)}. "
                 "The trajectories were decided the moment the roots were.",
        ))
    else:
        general = _particular(matrix, forcing, basis, general, derivation)
        if general is None:
            return

    derivation.result = general
    derivation.verified = _solves(matrix, general, forcing)
    _apply_conditions(general, constants, functions, ics, matrix, derivation,
                      forcing)


# ---------------------------------------------------------------------------
# The three cases
# ---------------------------------------------------------------------------


def _eigenvector_step(matrix, value, vectors, derivation: Derivation) -> None:
    """Show an eigenvector, and check that it is one."""
    column = vectors[0]
    derivation.steps.append(Step(
        title=f"An eigenvector for λ = {sp.sstr(value)}",
        latex=(rf"(A - ({sp.latex(value)})I)\,v = 0 \quad\Longrightarrow\quad "
               rf"v = {sp.latex(column)}"),
        note="Any non-zero multiple will do — the arbitrary constant in front "
             "absorbs the scaling, which is why a course never worries about "
             "normalising these.",
        verified=_is_zero(sp.simplify(matrix * column - value * column).norm()),
    ))


def _distinct_basis(matrix, ordered, derivation: Derivation):
    """Real distinct eigenvalues: one exponential each."""
    basis = []
    for value, _, vectors in ordered:
        _eigenvector_step(matrix, value, vectors, derivation)
        basis.append(sp.simplify(vectors[0] * sp.exp(value * _T)))
    derivation.steps.append(Step(
        title="Each pair gives a solution",
        latex=r",\qquad ".join(sp.latex(column) for column in basis),
        note="A solution that keeps a fixed direction and only changes length "
             "— the straight-line solutions, and the skeleton every other "
             "trajectory bends around.",
        verified=all(_solves(matrix, column) for column in basis),
    ))
    return basis


def _complex_basis(matrix, ordered, derivation: Derivation):
    """A complex pair, turned back into two real solutions.

    The step everybody finds hardest, so it is shown in full rather than
    quoted. Euler's formula is applied to the eigenvector as well as to the
    exponential, and the real and imaginary parts of the *whole product* are
    the two real solutions.
    """
    value, _, vectors = next(
        (item for item in ordered if sp.im(item[0]) > 0), ordered[0]
    )
    column = vectors[0]
    _eigenvector_step(matrix, value, vectors, derivation)

    alpha, beta = sp.re(value), sp.im(value)
    product = sp.simplify(sp.expand(column * sp.exp(value * _T)))
    real_part = sp.simplify(sp.Matrix(
        [sp.re(sp.expand_complex(entry)) for entry in product]
    ))
    imaginary_part = sp.simplify(sp.Matrix(
        [sp.im(sp.expand_complex(entry)) for entry in product]
    ))

    derivation.steps.append(Step(
        title="One complex solution carries both real ones",
        latex=(rf"v e^{{\lambda t}} = {sp.latex(column)}"
               rf"e^{{({sp.latex(alpha)} + {sp.latex(beta)}i)t}}"),
        note="The conjugate eigenvalue gives the conjugate solution, which is "
             "no new information. Instead of using both, take this one apart.",
    ))
    derivation.steps.append(Step(
        title="Euler's formula, on the vector as well",
        latex=(rf"e^{{{sp.latex(beta)}it}} = \cos {sp.latex(beta)}t "
               rf"+ i\sin {sp.latex(beta)}t"),
        note="Multiply it out — the eigenvector has complex entries too, so "
             "they mix into both parts. This is the step to take slowly.",
    ))
    derivation.steps.append(Step(
        title="Its real and imaginary parts are the two solutions",
        latex=(rf"{sp.latex(real_part)}, \qquad {sp.latex(imaginary_part)}"),
        note="Both solve the system, because the system has real coefficients: "
             "if a complex function solves it, its real and imaginary parts "
             "each do separately.",
        verified=(_solves(matrix, real_part)
                  and _solves(matrix, imaginary_part)),
    ))
    return [real_part, imaginary_part]


def _defective_basis(matrix, ordered, derivation: Derivation):
    """Fewer eigenvectors than the size: a generalised one supplies the rest.

    The systems counterpart of the repeated characteristic root, and it brings
    the same factor of `t` for the same reason -- one direction cannot carry
    two independent solutions.
    """
    value, multiplicity, vectors = ordered[0]
    if len(ordered) != 1 or multiplicity != matrix.shape[0]:
        derivation.message = (
            "this defective case is beyond the two-by-two one narrated here"
        )
        return None

    column = vectors[0]
    _eigenvector_step(matrix, value, vectors, derivation)
    derivation.steps.append(Step(
        title="There is only one eigenvector",
        latex=(rf"\lambda = {sp.latex(value)} \ (\times {multiplicity}), "
               rf"\qquad \dim\ker(A - \lambda I) = {len(vectors)}"),
        note="A repeated eigenvalue does not have to be short of "
             "eigenvectors, but this one is — and a single direction cannot "
             "carry two independent solutions. The matrix is called "
             "defective.",
        verified=len(vectors) < multiplicity,
    ))

    shifted = matrix - value * sp.eye(matrix.shape[0])
    generalised = sp.Matrix(sp.linsolve((shifted, column)).args[0])
    # linsolve leaves the free parameter in; any choice works, and zero is the
    # choice a course makes because it is the one that writes down shortest.
    generalised = generalised.subs(
        {symbol: 0 for symbol in generalised.free_symbols}
    )
    derivation.steps.append(Step(
        title="A generalised eigenvector supplies the second",
        latex=(rf"(A - \lambda I)\,w = v \quad\Longrightarrow\quad "
               rf"w = {sp.latex(generalised)}"),
        note="Not an eigenvector — it is one step away from being one. Any "
             "solution of this will do; the free part of it is a multiple of "
             "v, which the first constant already covers.",
        verified=_is_zero(sp.simplify((shifted * generalised - column).norm())),
    ))

    first = sp.simplify(column * sp.exp(value * _T))
    second = sp.simplify((column * _T + generalised) * sp.exp(value * _T))
    derivation.steps.append(Step(
        title="The second solution carries a t",
        latex=_eq(r"x_2(t)", sp.latex(second)),
        note="(vt + w)e^{λt}, not simply w·e^{λt}. Differentiating it "
             "produces the extra v·e^{λt} that the equation needs, which is "
             "exactly why w had to solve (A − λI)w = v.",
        verified=_solves(matrix, second),
    ))
    return [first, second]


# ---------------------------------------------------------------------------
# Checks and conditions
# ---------------------------------------------------------------------------


def _solves(matrix, column, forcing=None) -> bool:
    """Whether a vector function satisfies ``x' = A x + f`` identically.

    `forcing` defaults to zero, which is what every basis solution has to
    satisfy: the basis solves the *homogeneous* system, and checking it
    against a forced one would report a correct fundamental set as wrong --
    the same trap the second-order narrator documents.
    """
    try:
        right = matrix * column
        if forcing is not None:
            right = right + forcing
        residual = sp.simplify(sp.expand(column.diff(_T) - right))
        return all(_is_zero(entry) for entry in residual)
    except Exception:
        return False


def fundamental_matrix(basis):
    """``Phi(t)``: the basis solutions as columns.

    Everything about a forced system is expressed through this. It is
    invertible for every t precisely because the columns are independent,
    which is what the eigenvector work established.
    """
    return sp.Matrix.hstack(*basis)


def _particular(matrix, forcing, basis, homogeneous, derivation: Derivation):
    """Vary the constants: ``x_p = Phi * integral of Phi^-1 f``.

    The systems counterpart of variation of parameters, and the same idea
    exactly -- let the constants become functions of t. It is written with the
    fundamental matrix because that is what makes it one formula instead of a
    system of them: `Phi^-1 f` is the vector of `u_i'`, and integrating it is
    the whole of the method.

    Undetermined coefficients would also work for the forcing terms a course
    sets, and is not narrated here: it needs a resonance correction whenever
    the forcing matches an eigenvalue, and that correction is fiddlier for
    systems than for one equation. This route never needs one.
    """
    phi = fundamental_matrix(basis)
    determinant = sp.simplify(phi.det())
    derivation.steps.append(Step(
        title="Build the fundamental matrix",
        latex=_eq(r"\Phi(t)", phi),
        note="The basis solutions as columns. Its determinant is non-zero for "
             "every t — which is what independence bought — so it can be "
             "inverted, and everything below divides by it.",
        verified=bool(determinant != 0),
    ))
    if determinant == 0:
        derivation.message = "the fundamental matrix is singular"
        return None

    try:
        integrand = sp.simplify(phi.inv() * forcing)
    except Exception:
        derivation.message = "the fundamental matrix could not be inverted"
        return None

    derivation.steps.append(Step(
        title="Vary the constants",
        latex=(r"\mathbf{x}_p = \Phi(t)\int \Phi^{-1}(t)\,"
               rf"\mathbf{{f}}(t)\,dt, \qquad \Phi^{{-1}}\mathbf{{f}} = "
               rf"{sp.latex(integrand)}"),
        note="Replace the constant vector by a function of t. Requiring "
             "Φ·c′ = f is what makes the derivative work out, and it leaves "
             "c′ = Φ⁻¹f — one integral per constant.",
        verified=_is_zero(sp.simplify((phi * integrand - forcing).norm())),
    ))

    integrated = integrand.applyfunc(lambda entry: sp.integrate(entry, _T))
    if integrated.has(sp.Integral):
        derivation.message = (
            "the formula is right but the integrals have no closed form"
        )
        return None
    derivation.steps.append(Step(
        title="Integrate",
        latex=_eq(r"\int \Phi^{-1}\mathbf{f}\,dt", integrated),
        note="No constants of integration: they would only add multiples of "
             "the basis solutions back in, and the homogeneous part already "
             "carries those with arbitrary coefficients.",
        verified=all(_is_zero(sp.simplify(item.diff(_T) - prime))
                     for item, prime in zip(integrated, integrand)),
    ))

    particular = sp.simplify(phi * integrated)
    derivation.steps.append(Step(
        title="A particular solution",
        latex=_eq(r"\mathbf{x}_p(t)", particular),
        note="One solution of the forced system — no constants in it at all, "
             "which is what makes it particular.",
        verified=_solves(matrix, particular, forcing),
    ))

    general = sp.simplify(homogeneous + particular)
    derivation.steps.append(Step(
        title="The general solution",
        latex=_eq(r"\mathbf{x}(t)", sp.latex(general)),
        note="Homogeneous plus particular, as for any linear equation. The "
             "constants are still arbitrary; the forcing has not touched them.",
        verified=_solves(matrix, general, forcing),
    ))
    return general


def matrix_exponential(matrix):
    """``e^{At}``, the fundamental matrix that is the identity at t = 0.

    Not needed to solve anything -- Phi built from the basis does that -- but
    it is the object the theory is stated in, and it is worth being able to
    show: any two fundamental matrices differ by a constant matrix on the
    right, and this is the one normalised so that x(t) = e^{At} x(0).
    """
    return sp.simplify(sp.exp(matrix * _T))


def _apply_conditions(general, constants, functions, ics: dict, matrix,
                      derivation: Derivation, forcing=None) -> None:
    """Pin the constants from ``x(0) = ...`` values, if there are any."""
    if not ics:
        return

    wanted = {}
    for key, value in ics.items():
        for index, function in enumerate(functions):
            if getattr(key, "func", None) is function:
                point = key.args[0]
                if not point.free_symbols:
                    wanted[index] = (point, sp.sympify(value))
    if len(wanted) < len(functions):
        derivation.message = (
            "one condition per unknown is needed to pin the constants"
        )
        return

    system = [sp.Eq(general[index].subs(_T, point), value)
              for index, (point, value) in sorted(wanted.items())]
    solved = sp.solve(system, constants, dict=True)
    if not solved:
        derivation.message = "the initial conditions could not be applied"
        return

    particular = sp.simplify(general.subs(solved[0]))
    derivation.steps.append(Step(
        title="Apply the initial conditions",
        latex=", ".join(
            _eq(symbol, value)
            for symbol, value in sorted(solved[0].items(), key=lambda i: str(i[0]))
        ),
        note="One linear equation per component, at the starting time. Two "
             "unknowns, two equations — the same shape as pinning C₁ and C₂ "
             "for a second-order equation.",
        verified=all(
            _is_zero(sp.simplify(particular[index].subs(_T, point) - value))
            for index, (point, value) in sorted(wanted.items())
        ),
    ))
    derivation.steps.append(Step(
        title="The particular solution",
        latex=_eq(sp.latex(sp.Matrix([f(_T) for f in functions])),
                  sp.latex(particular)),
        note="One trajectory now, rather than a family of them.",
        verified=_solves(matrix, particular, forcing),
    ))
    derivation.result = particular
    derivation.verified = _solves(matrix, particular, forcing)
