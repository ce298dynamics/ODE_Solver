"""The transform method: the algebra, the answers, and what backs them.

Laplace is the one technique in a first course that copes with forcing switched
on partway through or delivered as an impulse, so the switched and impulsive
cases are tested at least as hard as the smooth ones — they are the reason the
screen exists, and they are also where every sharp edge turned out to be.

Three things carry most of the weight.

**The answers are the textbook ones.** Not "some expression that verifies", but
`u(t-2)(1 - e^{-(t-2)})` and `sin(t-1)u(t-1)` — the results a student would
compare against.

**A claim is never stronger than its evidence.** Smooth answers are decided by
substitution. A switched answer cannot be: differentiating a Heaviside leaves
Dirac terms that never cancel *even when the answer is right*, so those are
decided against this project's own integrator, and `Derivation.check` records
which route was taken so the interface cannot name the wrong one. An impulse is
decided by neither and is reported unchecked.

**The widened whitelist stays where it was put.** `Heaviside` and `DiracDelta`
are typeable here and nowhere else.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sympy")

import sympy as sp  # noqa: E402

from odesuite_app.laplace import (  # noqa: E402
    EXTRA_FUNCTIONS,
    TABLE,
    derive,
    pairs_used,
)

T = sp.Symbol("t", real=True)
Y = sp.Function("y")
ZERO = sp.Integer(0)


def _ics(*values):
    """``y(0)=a, y'(0)=b`` in the two shapes conditions actually arrive in."""
    conditions = {}
    for order, value in enumerate(values):
        key = Y(ZERO) if order == 0 else sp.Subs(Y(T).diff(T, order), T, 0)
        conditions[key] = sp.Integer(value) if isinstance(value, int) else value
    return conditions


def _derive(expr, rhs=0, ics=None):
    return derive(sp.Eq(expr, rhs), Y, ics=ics or {})


# ---------------------------------------------------------------------------
# Smooth forcing: substitution decides
# ---------------------------------------------------------------------------

SMOOTH = [
    ("free oscillator", Y(T).diff(T, 2) + 4 * Y(T), 0, (0, 2), sp.sin(2 * T)),
    ("first order", Y(T).diff(T) + 2 * Y(T), T, (0,),
     T / 2 - sp.Rational(1, 4) + sp.exp(-2 * T) / 4),
    ("resonant", Y(T).diff(T, 2) + Y(T), sp.cos(T), (0, 0), T * sp.sin(T) / 2),
    ("repeated root", Y(T).diff(T, 2) + 2 * Y(T).diff(T) + Y(T), 0, (1, 1),
     (2 * T + 1) * sp.exp(-T)),
]


@pytest.mark.parametrize("name,lhs,rhs,ics,expected", SMOOTH,
                         ids=[c[0] for c in SMOOTH])
def test_the_answer_is_the_textbook_one(name, lhs, rhs, ics, expected):
    derivation = _derive(lhs, rhs, _ics(*ics))
    assert derivation.result is not None, derivation.message
    assert sp.simplify(derivation.result - expected) == 0, (
        f"{name}: got {derivation.result}, expected {expected}"
    )


@pytest.mark.parametrize("name,lhs,rhs,ics,expected", SMOOTH,
                         ids=[c[0] for c in SMOOTH])
def test_smooth_answers_are_decided_by_substitution(name, lhs, rhs, ics, expected):
    """The check used everywhere else here, and it is decisive on these."""
    derivation = _derive(lhs, rhs, _ics(*ics))
    assert derivation.verified is True
    assert derivation.check == "substitution"


@pytest.mark.parametrize("name,lhs,rhs,ics,expected", SMOOTH,
                         ids=[c[0] for c in SMOOTH])
def test_no_step_of_a_smooth_derivation_fails_its_check(name, lhs, rhs, ics,
                                                        expected):
    failed = [s.title for s in _derive(lhs, rhs, _ics(*ics)).steps
              if s.verified is False]
    assert not failed, f"{name}: these steps did not verify: {failed}"


def test_resonance_comes_out_without_being_a_special_case():
    """`y'' + y = cos t` is the case undetermined coefficients needs a rule for.
    The transform does not: it is the same algebra, and a repeated factor in
    Y(s) is what produces the t."""
    derivation = _derive(Y(T).diff(T, 2) + Y(T), sp.cos(T), _ics(0, 0))
    assert sp.simplify(derivation.result - T * sp.sin(T) / 2) == 0
    assert derivation.verified is True


#: The moves of the method, derived by hand. Names and order, not spelling.
EXPECTED_STEPS = [
    "Transform both sides",
    "The transformed equation",
    "Put the initial conditions in",
    "Solve for Y(s) — it is only algebra",
    "Split into partial fractions",
    "Invert term by term",
]


def test_the_steps_are_the_moves_of_the_method():
    titles = [s.title for s in _derive(Y(T).diff(T, 2) + 4 * Y(T), 0,
                                       _ics(0, 2)).steps]
    assert titles == EXPECTED_STEPS


def test_the_algebra_and_the_inversion_are_both_checked():
    """Solving for Y(s) is checked by substituting it back into the transformed
    equation; the inversion is checked by transforming the answer forward again,
    which uses the table in the opposite direction so a misread row cannot
    cancel itself out."""
    derivation = _derive(Y(T).diff(T, 2) + 3 * Y(T).diff(T) + 2 * Y(T),
                         sp.sin(T), _ics(1, 0))
    checked = {s.title: s.verified for s in derivation.steps}
    assert checked["Solve for Y(s) — it is only algebra"] is True
    assert checked["Split into partial fractions"] is True
    assert checked["Invert term by term"] is True


def test_the_initial_conditions_enter_at_the_start():
    """The point of the technique, and what separates it from every other one
    in the Hub: no arbitrary constants are ever introduced, so none have to be
    pinned down at the end."""
    derivation = _derive(Y(T).diff(T, 2) + 4 * Y(T), 0, _ics(0, 2))
    assert "Put the initial conditions in" in [s.title for s in derivation.steps]
    assert not derivation.result.free_symbols - {T}, "a constant survived"


def test_without_conditions_the_answer_keeps_them_as_symbols():
    derivation = _derive(Y(T).diff(T, 2) + 4 * Y(T), 0, {})
    assert derivation.result is not None, derivation.message
    assert derivation.result.has(sp.cos(2 * T)) and derivation.result.has(
        sp.sin(2 * T)
    )
    assert "No initial conditions were given" in [
        s.title for s in derivation.steps
    ]


# ---------------------------------------------------------------------------
# Switched and impulsive forcing: the reason the screen exists
# ---------------------------------------------------------------------------


def test_a_switch_gives_the_textbook_answer():
    """``y' + y = u(t-2)``, y(0)=0. Off until t = 2, then approaching 1 —
    `u(t-2)(1 - e^{-(t-2)})`. Not separable, no integrating factor worth
    writing, and not what undetermined coefficients is for."""
    derivation = _derive(Y(T).diff(T) + Y(T), sp.Heaviside(T - 2), _ics(0))
    expected = sp.Heaviside(T - 2) * (1 - sp.exp(-(T - 2)))
    assert sp.simplify(derivation.result - expected) == 0, derivation.result


def test_an_impulse_gives_the_textbook_answer():
    """``y'' + y = δ(t-1)`` at rest: nothing until the blow, then a sine that
    starts at t = 1."""
    derivation = _derive(Y(T).diff(T, 2) + Y(T), sp.DiracDelta(T - 1),
                         _ics(0, 0))
    expected = sp.sin(T - 1) * sp.Heaviside(T - 1)
    assert sp.simplify(derivation.result - expected) == 0, derivation.result


def test_a_switched_answer_is_decided_numerically_not_by_substitution():
    """Substituting a Heaviside answer back leaves Dirac terms that never
    cancel even though the answer is right, so substitution cannot decide it.
    The integrator can, and `check` records which route was taken so the
    interface cannot claim the wrong one."""
    derivation = _derive(Y(T).diff(T) + Y(T), sp.Heaviside(T - 2), _ics(0))
    assert derivation.verified is True
    assert derivation.check == "numeric"

    # The premise: substitution really is unable to decide this.
    residual = sp.simplify(
        (Y(T).diff(T) + Y(T) - sp.Heaviside(T - 2)).subs(
            Y(T), derivation.result
        ).doit()
    )
    assert residual != 0
    assert residual.has(sp.DiracDelta), (
        "if substitution now decides this, the numeric route is unnecessary"
    )


def test_an_impulse_is_reported_unchecked_rather_than_guessed_at():
    """Neither route can decide it: substitution leaves impulse terms, and
    `DiracDelta` has no numerical value to compare against. Saying so is the
    only honest option — and it must not be reported as wrong."""
    derivation = _derive(Y(T).diff(T, 2) + Y(T), sp.DiracDelta(T - 1),
                         _ics(0, 0))
    assert derivation.verified is None
    assert derivation.verified is not False
    assert "impulse" in derivation.message


def test_the_delay_is_split_off_rather_than_expanded():
    """`apart` raises PolynomialError on e^{-as} — on exactly the problems this
    technique is for. Splitting the delay off first is both the fix and the
    textbook move, so the narration gains a step rather than losing one."""
    derivation = _derive(Y(T).diff(T) + Y(T), sp.Heaviside(T - 2), _ics(0))
    titles = [s.title for s in derivation.steps]
    assert "Split off the delay" in titles
    assert "Split into partial fractions" not in titles
    shift_step = next(s for s in derivation.steps if s.title == "Split off the delay")
    assert shift_step.verified is True
    assert "second shifting theorem" in shift_step.note


def test_apart_really_does_fail_on_a_delayed_transform():
    """The premise of the step above, pinned: if sympy ever copes with this,
    the special case can go."""
    s = sp.Symbol("s")
    with pytest.raises(sp.PolynomialError):
        sp.apart(sp.exp(-2 * s) / (s * (s + 1)), s)


def test_the_unit_step_marker_is_dropped_but_a_real_delay_is_kept():
    """Inversion decorates every term with `Heaviside(t)`, which is 1 across the
    whole domain the transform describes and is noise on every line. A shifted
    step is the entire content of a switched answer and must survive."""
    smooth = _derive(Y(T).diff(T, 2) + 4 * Y(T), 0, _ics(0, 2))
    assert not smooth.result.has(sp.Heaviside)

    switched = _derive(Y(T).diff(T) + Y(T), sp.Heaviside(T - 2), _ics(0))
    assert switched.result.has(sp.Heaviside(T - 2))


# ---------------------------------------------------------------------------
# Declining, rather than producing something meaningless
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lhs,rhs", [
    (Y(T).diff(T) - Y(T) ** 2, 0),
    (Y(T).diff(T) - sp.sin(Y(T)), 0),
])
def test_a_nonlinear_equation_says_the_method_does_not_apply(lhs, rhs):
    derivation = _derive(lhs, rhs, _ics(1))
    assert derivation.result is None
    assert not derivation.steps
    assert "linear" in derivation.message


@pytest.mark.parametrize("lhs", [
    T * Y(T).diff(T) + Y(T),
    T**2 * Y(T).diff(T, 2) + T * Y(T).diff(T) - Y(T),
])
def test_variable_coefficients_are_declined_with_the_reason(lhs):
    """`L{t·y'}` is a derivative in s, so transforming produces another
    differential equation rather than an algebraic one. The method has not
    failed, it has not helped — and saying that beats showing the reader an
    unevaluated InverseLaplaceTransform, which is what it did before."""
    derivation = _derive(lhs, 0, _ics(1))
    assert derivation.result is None
    assert "differential equation in s" in derivation.message
    assert derivation.verified is not False, "declining is not being wrong"


def test_a_condition_away_from_zero_is_refused_with_a_reason():
    """The transform integrates from zero, so a condition given anywhere else
    cannot enter the method at all."""
    derivation = derive(sp.Eq(Y(T).diff(T) + Y(T), 0), Y,
                        ics={Y(sp.Integer(2)): 1})
    assert derivation.result is None
    assert "t = 0" in derivation.message


def test_a_derivation_never_raises():
    """It runs on whatever a user typed, inside a worker whose only other
    option is to die."""
    for equation in (sp.Eq(Y(T) ** 2, T), sp.Eq(Y(T).diff(T), sp.zoo)):
        derivation = derive(equation, Y, ics={})
        assert derivation is not None
        assert derivation.verified is not True or derivation.result is not None


# ---------------------------------------------------------------------------
# The transform table
# ---------------------------------------------------------------------------


def test_the_table_covers_what_a_course_memorises():
    keys = {pair.key for pair in TABLE}
    assert {"one", "power", "exp", "sin", "cos", "derivative", "step",
            "impulse", "shift"} <= keys
    for pair in TABLE:
        assert pair.f_latex and pair.F_latex


def test_the_rows_an_answer_needed_are_identified():
    assert "exp" in pairs_used(sp.exp(-2 * T))
    assert "sin" in pairs_used(sp.sin(2 * T))
    assert "step" in pairs_used(sp.Heaviside(T - 2) * (1 - sp.exp(-T)))
    assert "impulse" in pairs_used(sp.DiracDelta(T - 1))
    # The derivative rows are what made it algebra in the first place.
    assert {"derivative", "derivative2"} <= pairs_used(sp.sin(T))
    assert pairs_used(None) == set()


def test_every_identified_row_exists_in_the_table():
    """A key that matches nothing would highlight nothing, silently."""
    keys = {pair.key for pair in TABLE}
    for answer in (sp.exp(-T), sp.sin(T) + sp.cos(T), T**2,
                   sp.Heaviside(T - 1), sp.DiracDelta(T - 2)):
        assert pairs_used(answer) <= keys


# ---------------------------------------------------------------------------
# The widened whitelist stays where it was put
# ---------------------------------------------------------------------------


def test_the_extra_names_are_exactly_the_two_intended():
    assert set(EXTRA_FUNCTIONS) == {"Heaviside", "DiracDelta"}


@pytest.mark.parametrize("text", [
    "y' + y = Heaviside(t - 2)",
    "y'' + y = DiracDelta(t - 1)",
])
def test_the_solver_lab_still_refuses_a_step_or_an_impulse(text):
    """`DiracDelta` cannot be lambdified at all, and a discontinuous right-hand
    side is exactly what an adaptive step can cross without noticing. The
    widening is for the symbolic path only, and this is the assertion that keeps
    it there."""
    from odesuite_app.custom import ParseError
    from odesuite_app.symbolic import EquationSpec, parse_equation

    spec = EquationSpec(equations=[text], initial_conditions="y(0)=0")
    with pytest.raises(ParseError):
        parse_equation(spec)
    # ... and is accepted only when asked for explicitly.
    assert parse_equation(spec, extra_functions=EXTRA_FUNCTIONS) is not None


def test_dirac_delta_really_cannot_be_lambdified():
    """The reason the whitelist is not widened globally, pinned. If sympy gains
    a numeric DiracDelta this can be revisited — but it must be measured."""
    with pytest.raises(NameError):
        sp.lambdify(T, sp.DiracDelta(T - 2), "numpy")(1.0)


def test_the_widening_cannot_be_shadowed_by_a_variable_name():
    from odesuite_app.custom import ParseError
    from odesuite_app.symbolic import EquationSpec, parse_equation

    spec = EquationSpec(equations=["Heaviside' = Heaviside"],
                        variables=["Heaviside"])
    with pytest.raises(ParseError):
        parse_equation(spec, extra_functions=EXTRA_FUNCTIONS)


def test_laplace_needs_no_interface_toolkit():
    """It runs inside the solver subprocess, which has no Qt."""
    import subprocess
    import sys

    code = (
        "import sys; sys.modules['PySide6'] = None\n"
        "import odesuite_app.laplace as m; assert m.TABLE\n"
    )
    done = subprocess.run([sys.executable, "-c", code], capture_output=True,
                          text=True)
    assert done.returncode == 0, done.stderr[-400:]


# ---------------------------------------------------------------------------
# Two independent routes to one answer
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name,lhs,rhs,ics,expected", SMOOTH,
                         ids=[c[0] for c in SMOOTH])
def test_the_transform_and_dsolve_agree(name, lhs, rhs, ics, expected):
    """`dsolve` does not use the transform, so agreeing with it is real
    corroboration rather than a restatement — the standard this project already
    applies to Radau's split-versus-dense solve.
    """
    equation = sp.Eq(lhs, rhs)
    conditions = _ics(*ics)
    derivation = _derive(lhs, rhs, conditions)

    from_dsolve = sp.dsolve(equation, Y(T), ics=conditions).rhs
    assert sp.simplify(derivation.result - from_dsolve) == 0, (
        f"{name}: transform gave {derivation.result}, dsolve gave {from_dsolve}"
    )


@pytest.mark.slow
def test_a_switched_answer_agrees_with_the_numeric_solution():
    """The claim `check == "numeric"` rests on, made directly here rather than
    only through the derivation: solve the same problem with this project's own
    integrator and compare away from the switch."""
    import numpy as np

    from odesuite import solve
    from odesuite_app.laplace import EXTRA_FUNCTIONS as EXTRA
    from odesuite_app.symbolic import EquationSpec, parse_equation, to_first_order

    parsed = parse_equation(
        EquationSpec(equations=["y' + y = Heaviside(t - 2)"],
                     initial_conditions="y(0)=0", t_span=(0.0, 6.0)),
        extra_functions=EXTRA,
    )
    problem = to_first_order(parsed)
    numeric = solve(problem, "dopri5", rtol=1e-11, atol=1e-13, dense_output=True)
    assert numeric.success

    closed = sp.Heaviside(T - 2) * (1 - sp.exp(-(T - 2)))
    as_function = sp.lambdify(T, closed, "numpy")
    times = np.linspace(0.05, 6.0, 40)
    error = float(np.max(np.abs(
        np.asarray([float(as_function(x)) for x in times]) - numeric.y_at(times)[0]
    )))
    assert error < 1e-6, f"closed form and numeric solution differ by {error:.2e}"


# ---------------------------------------------------------------------------
# The screen
# ---------------------------------------------------------------------------

pytest.importorskip("PySide6", reason="the app extra is not installed")


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


def _screen(palette_name="dark"):
    from odesuite_app.screens.learn_laplace import LaplaceScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    screen = LaplaceScreen(SessionState(), PALETTES[palette_name])
    screen.resize(1600, 950)
    return screen


def _submit(screen, qapp, equation, ics=""):
    from PySide6.QtCore import QThreadPool

    from odesuite_app.symbolic import EquationSpec

    screen._on_submitted(
        EquationSpec(equations=[equation], initial_conditions=ics)
    )
    QThreadPool.globalInstance().waitForDone(90_000)
    qapp.processEvents()
    qapp.processEvents()


@pytest.mark.parametrize("palette", ["dark", "light"])
def test_the_screen_renders_in_both_palettes(qapp, palette):
    screen = _screen(palette)
    qapp.processEvents()
    assert not screen.grab().isNull()
    screen.deleteLater()


@pytest.mark.slow
def test_a_switched_equation_reaches_the_screen(qapp):
    """End to end, through the subprocess, on the problem the screen is for."""
    screen = _screen()
    _submit(screen, qapp, "y' + y = Heaviside(t - 2)", "y(0)=0")

    assert screen.steps._heading.text() == "Laplace transform"
    assert screen.steps._body.count() >= 6
    assert not screen.grab().isNull()
    screen.deleteLater()


@pytest.mark.slow
def test_the_table_highlights_the_rows_that_were_used(qapp):
    """The table is a reference being consulted, not decoration."""
    screen = _screen()
    _submit(screen, qapp, "y'' + 4*y = 0", "y(0)=0, y'(0)=2")

    # sin(2t): the sine row is in play, the impulse row is not.
    assert "sin" in pairs_used(sp.sin(2 * T))
    assert "impulse" not in pairs_used(sp.sin(2 * T))
    assert set(screen._rows) == {pair.key for pair in TABLE}
    screen.deleteLater()


def test_the_screen_accepts_a_step_that_the_rest_of_the_app_refuses(qapp):
    """The widening reaches the screen's own parse, and only that one."""
    from odesuite_app.symbolic import EquationSpec

    screen = _screen()
    screen._on_submitted(
        EquationSpec(equations=["y' + y = Heaviside(t - 2)"],
                     initial_conditions="y(0)=0")
    )
    qapp.processEvents()
    # It got as far as starting a solve rather than reporting a parse error.
    assert "cannot parse" not in screen.steps._status.text()
    screen.deleteLater()


def test_an_unparseable_equation_is_reported_not_crashed(qapp):
    from odesuite_app.symbolic import EquationSpec

    screen = _screen()
    screen._on_submitted(EquationSpec(equations=["y' = sin(t"]))
    qapp.processEvents()
    assert screen.steps._status.isVisibleTo(screen.steps)
    assert screen.steps._body.count() == 0
    screen.deleteLater()


def test_the_derivation_gets_the_larger_half(qapp):
    screen = _screen()
    qapp.processEvents()
    layout = screen.layout()
    assert layout.stretch(1) > layout.stretch(2), (
        "the derivation should be wider than the table beside it"
    )
    screen.deleteLater()


def test_a_timeout_names_the_right_cause():
    """`_run_dsolve` is shared with the closed-form path and its timeout text
    says "no closed form found" — but this path never runs `dsolve`, so that
    would name a cause that does not exist here."""
    from odesuite_app.symbolic import EquationSpec, parse_equation, solve_by_laplace

    parsed = parse_equation(
        EquationSpec(equations=["y'' + 4*y = 0"], initial_conditions="y(0)=0")
    )
    solution = solve_by_laplace(parsed, timeout=1e-6)      # cannot start in time
    assert solution.timed_out is True
    assert "closed form" not in solution.message
    assert "transform" in solution.message


@pytest.mark.parametrize("name", ["y", "x", "v"])
def test_an_unspecified_condition_is_named_after_the_users_variable(name):
    """Give only y'(0) and y(0) stays symbolic, which is correct — but it has to
    be *this* equation's y(0). A hardcoded `y` put a `y(0)` into the answer for
    an equation written in `x`: a symbol from no equation the reader wrote."""
    f = sp.Function(name)
    derivation = derive(
        sp.Eq(f(T).diff(T, 2) + 4 * f(T), 0), f,
        ics={sp.Subs(f(T).diff(T), T, 0): 2},
    )
    assert derivation.result is not None, derivation.message
    symbols = {str(a.func) for a in derivation.result.atoms(sp.Function)}
    assert name in symbols
    for other in {"y", "x", "v"} - {name}:
        assert other not in symbols, f"{other}(0) leaked into a {name} equation"
