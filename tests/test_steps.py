"""Narrated derivations: the working, and whether it is honest.

A derivation that prints a wrong intermediate line is worse than no derivation,
so these tests are weighted towards the claims rather than the prose. Three
things are checked hardest.

**Dispatch.** `classify_ode` orders its hints by what sympy would rather solve
with, and four of the five techniques narrated here are *not* its first hint --
`y'' + 3y' + 2y = 0` leads with `factorable`. Picking the first hint would have
left this feature silently inert on most of a first course, so every technique
has a canonical equation pinned to it.

**Every step's own check.** `Step.verified` is not decoration: the
antiderivatives are differentiated back, each basis function is substituted into
the equation, the particular solution has to reproduce the forcing term. A step
that reports False is a failure here, not a warning.

**Spelling is not pinned.** Titles and counts are asserted; the exact LaTeX is
not, because sympy is free to factor an answer differently between releases and
that is not a regression.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sympy")

import sympy as sp  # noqa: E402

from odesuite_app.steps import (  # noqa: E402
    TECHNIQUES,
    TITLES,
    Derivation,
    derive,
    preferred_hint,
)

T = sp.Symbol("t", real=True)
Y = sp.Function("y")


def _eq(expr, rhs=0):
    return sp.Eq(expr, rhs)


def _derive(equation, ics=None):
    return derive(equation, Y, hints=sp.classify_ode(equation, Y(T)),
                  ics=ics or {})


#: One canonical equation per technique, and the answer a course would give.
CANONICAL = {
    "separable": _eq(Y(T).diff(T), Y(T) * (1 - Y(T))),
    "1st_linear": _eq(Y(T).diff(T) + 2 * Y(T), T),
    "nth_linear_constant_coeff_homogeneous":
        _eq(Y(T).diff(T, 2) + 3 * Y(T).diff(T) + 2 * Y(T)),
    "nth_linear_constant_coeff_undetermined_coefficients":
        _eq(Y(T).diff(T, 2) + 4 * Y(T), sp.sin(T)),
    "1st_homogeneous_coeff_best":
        _eq(Y(T).diff(T), (T**2 + Y(T) ** 2) / (T * Y(T))),
    "Bernoulli": _eq(Y(T).diff(T) + Y(T), T * Y(T) ** 3),
    "nth_linear_euler_eq_homogeneous":
        _eq(T**2 * Y(T).diff(T, 2) + T * Y(T).diff(T) - Y(T)),
}

#: Exact equations are deliberately absent from `CANONICAL`: they are not
#: dispatched from a hint at all. See the exactness tests below.
EXACT = _eq(Y(T).diff(T), -(sp.cos(T) + Y(T)) / (T + 2 * Y(T)))


# ---------------------------------------------------------------------------
# Dispatch -- the half that decides whether any of this runs at all
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("technique", TECHNIQUES)
def test_every_technique_is_selected_for_its_own_equation(technique):
    derivation = _derive(CANONICAL[technique])
    assert derivation is not None, f"{technique} did not dispatch"
    assert derivation.technique == technique
    assert derivation.title == TITLES[technique]


@pytest.mark.parametrize("technique", TECHNIQUES)
def test_the_teaching_hint_is_usually_not_sympys_first(technique):
    """The finding this phase turns on, pinned so a sympy change surfaces it.

    Only `undetermined_coefficients` happens to lead sympy's list. If this test
    ever reports that *every* technique is first, the preference order has
    stopped doing anything and can be reconsidered -- but it must be measured,
    not assumed.
    """
    hints = sp.classify_ode(CANONICAL[technique], Y(T))
    assert technique in hints, "sympy no longer offers this hint at all"
    assert preferred_hint(hints) == technique


def test_sympys_first_hint_really_is_the_wrong_one_to_teach():
    """Concretely, so the reason for the preference order is not forgotten."""
    firsts = {
        name: sp.classify_ode(equation, Y(T))[0]
        for name, equation in CANONICAL.items()
    }
    assert firsts["nth_linear_constant_coeff_homogeneous"] == "factorable"
    assert firsts["1st_linear"] == "1st_exact"
    assert firsts["nth_linear_euler_eq_homogeneous"] == "factorable"
    wrong = sum(1 for name, first in firsts.items() if first != name)
    assert wrong >= 3, f"only {wrong} disagree now; revisit the ordering"


def test_where_two_techniques_apply_the_one_taught_first_wins():
    """Newton's cooling is both separable and linear. A first course separates."""
    cooling = _eq(Y(T).diff(T), -sp.Rational(1, 5) * (Y(T) - 20))
    hints = sp.classify_ode(cooling, Y(T))
    assert {"separable", "1st_linear"} <= set(hints)
    assert preferred_hint(hints) == "separable"


def test_the_preference_order_is_the_teaching_order():
    assert TECHNIQUES.index("separable") < TECHNIQUES.index("1st_linear")
    assert (TECHNIQUES.index("nth_linear_constant_coeff_homogeneous")
            < TECHNIQUES.index(
                "nth_linear_constant_coeff_undetermined_coefficients"))


# ---------------------------------------------------------------------------
# The derivations themselves
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("technique", TECHNIQUES)
def test_every_step_passes_its_own_check(technique):
    derivation = _derive(CANONICAL[technique])
    failed = [s.title for s in derivation.steps if s.verified is False]
    assert not failed, f"{technique}: these steps did not verify: {failed}"


@pytest.mark.parametrize("technique", TECHNIQUES)
def test_the_derivation_reaches_a_verified_answer(technique):
    derivation = _derive(CANONICAL[technique])
    assert derivation.result is not None, derivation.message
    assert derivation.verified is True
    assert derivation.complete


@pytest.mark.parametrize("technique", TECHNIQUES)
def test_something_is_actually_checked_rather_than_only_printed(technique):
    """At least one step must make a claim that was verified, or the ticks are
    decoration and the panel is lying about what it did."""
    derivation = _derive(CANONICAL[technique])
    assert sum(1 for s in derivation.steps if s.verified is True) >= 2


@pytest.mark.parametrize("technique", TECHNIQUES)
def test_every_step_is_readable(technique):
    for step in _derive(CANONICAL[technique]).steps:
        assert step.title and step.latex
        # Two internal placeholders have leaked to the reader before: the
        # parser's derivative token, and the plain symbol `separatevars` needs
        # in place of `y(t)`. Both are capitals, and neither belongs on screen.
        assert "ODEDZ" not in step.latex, "a parser placeholder reached the user"
        assert "Y" not in step.latex, "the separatevars placeholder reached the user"


#: Title sequences, derived by hand. Counts and names, not spelling.
EXPECTED = {
    "separable": ["Write it as a product", "Separate the variables",
                  "Integrate both sides", "Solve for y"],
    "1st_linear": ["Put it in standard form", "Form the integrating factor",
                   "Multiply through by it", "The left side is a product rule",
                   "Integrate both sides", "Divide by the integrating factor"],
    "nth_linear_constant_coeff_homogeneous":
        ["Try an exponential", "The characteristic equation", "Its roots",
         "The fundamental set", "The general solution"],
    "nth_linear_constant_coeff_undetermined_coefficients":
        ["Try an exponential", "The characteristic equation", "Its roots",
         "The fundamental set", "That is the homogeneous solution",
         "Guess a form from the forcing term", "Substitute the guess",
         "Solve for the coefficients", "The general solution"],
    "1st_homogeneous_coeff_best":
        ["Everything depends on y/t", "Substitute y = v·t",
         "Now it separates", "Write it as a product",
         "Separate the variables", "Integrate both sides", "Solve for v",
         "Undo the substitution"],
    "Bernoulli":
        ["Put it in Bernoulli form", "Substitute v = y^{-2}",
         "It is linear in v", "Put it in standard form",
         "Form the integrating factor", "Multiply through by it",
         "The left side is a product rule", "Integrate both sides",
         "Divide by the integrating factor", "Undo the substitution"],
    "nth_linear_euler_eq_homogeneous":
        ["Try a power of t", "The indicial equation", "Its roots",
         "The fundamental set", "The general solution"],
}


@pytest.mark.parametrize("technique", TECHNIQUES)
def test_the_steps_are_the_ones_a_course_writes(technique):
    titles = [step.title for step in _derive(CANONICAL[technique]).steps]
    assert titles == EXPECTED[technique]


# ---------------------------------------------------------------------------
# The cases each technique exists to handle
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("equation,expected", [
    (_eq(Y(T).diff(T, 2) + 2 * Y(T).diff(T) + Y(T)), "repeated"),
    (_eq(Y(T).diff(T, 2) + 4 * Y(T)), "complex"),
    (_eq(Y(T).diff(T, 2) + 3 * Y(T).diff(T) + 2 * Y(T)), "distinct"),
])
def test_all_three_root_cases_are_narrated(equation, expected):
    """The three branches every course spends a lecture on. Each basis function
    is substituted into the equation, so a wrong multiplicity fails here."""
    derivation = _derive(equation)
    assert derivation.verified is True
    basis_step = next(s for s in derivation.steps if s.title == "The fundamental set")
    assert basis_step.verified is True


def test_a_repeated_root_says_where_the_extra_t_comes_from():
    derivation = _derive(_eq(Y(T).diff(T, 2) + 2 * Y(T).diff(T) + Y(T)))
    note = next(s for s in derivation.steps if s.title == "Its roots").note
    assert "repeated" in note
    assert "critically damped" in note, "describe_roots should still contribute"


def test_a_complex_pair_is_described_once_not_twice():
    """It contributes one cosine and one sine, and the note counts it once --
    saying it twice made a second-order equation read as having four solutions."""
    note = next(s for s in _derive(_eq(Y(T).diff(T, 2) + 4 * Y(T))).steps
                if s.title == "Its roots").note
    assert note.count("a complex pair") == 1


def test_resonance_is_caught_and_corrected():
    """y'' + y = sin(t): the obvious guess is already a homogeneous solution, so
    it can never produce the forcing term. Getting this wrong is the classic
    error the technique exists to warn about."""
    derivation = _derive(_eq(Y(T).diff(T, 2) + Y(T), sp.sin(T)))
    titles = [s.title for s in derivation.steps]
    assert "Correct for resonance" in titles
    assert derivation.verified is True
    assert derivation.result.has(T * sp.cos(T)) or derivation.result.has(T * sp.sin(T))


def test_without_resonance_no_correction_is_claimed():
    derivation = _derive(_eq(Y(T).diff(T, 2) + 4 * Y(T), sp.sin(T)))
    assert "Correct for resonance" not in [s.title for s in derivation.steps]


def test_an_integrating_factor_handles_variable_coefficients():
    """The whole reason the technique exists: p(t) need not be constant."""
    derivation = _derive(_eq(T * Y(T).diff(T) + Y(T), sp.sin(T)))
    assert derivation.technique == "1st_linear"
    assert derivation.verified is True


@pytest.mark.parametrize("equation", [
    _eq(T**2 * Y(T).diff(T, 2) + T * Y(T).diff(T) - Y(T)),        # distinct
    _eq(T**2 * Y(T).diff(T, 2) - 3 * T * Y(T).diff(T) + 4 * Y(T)),  # repeated
    _eq(T**2 * Y(T).diff(T, 2) + T * Y(T).diff(T) + Y(T)),        # complex
])
def test_cauchy_euler_covers_its_three_root_cases(equation):
    derivation = _derive(equation)
    assert derivation.verified is True, derivation.message


def test_a_repeated_cauchy_euler_root_brings_in_a_logarithm():
    derivation = _derive(_eq(T**2 * Y(T).diff(T, 2) - 3 * T * Y(T).diff(T)
                             + 4 * Y(T)))
    assert derivation.result.has(sp.log(T))


# ---------------------------------------------------------------------------
# Initial conditions
# ---------------------------------------------------------------------------


def test_an_initial_condition_pins_the_constant():
    cooling = _eq(Y(T).diff(T), -sp.Rational(1, 5) * (Y(T) - 20))
    derivation = _derive(cooling, ics={Y(sp.Integer(0)): 95})
    assert "Apply the initial conditions" in [s.title for s in derivation.steps]
    assert sp.simplify(derivation.result.subs(T, 0) - 95) == 0
    assert not derivation.result.free_symbols - {T}, "a constant survived"


def test_a_derivative_condition_is_evaluated_at_the_right_point():
    """Conditions arrive as `y(0)` and as `Subs(Derivative(y(t), t), t, 0)`.
    Handling only the first evaluates every derivative condition at the wrong
    place -- a bug that shipped once in `symbolic._satisfies_conditions`, where
    it reported a correct answer as wrong."""
    ics = {Y(sp.Integer(0)): 0, sp.Subs(Y(T).diff(T), T, 0): 2}
    derivation = _derive(_eq(Y(T).diff(T, 2) + 4 * Y(T)), ics=ics)
    assert derivation.verified is True
    answer = derivation.result
    assert sp.simplify(answer.subs(T, 0)) == 0
    assert sp.simplify(answer.diff(T).subs(T, 0)) == 2


def test_without_conditions_the_constants_stay():
    derivation = _derive(_eq(Y(T).diff(T, 2) + 4 * Y(T)))
    assert {s.name for s in derivation.result.free_symbols} >= {"C1", "C2"}
    assert "Apply the initial conditions" not in [
        s.title for s in derivation.steps
    ]


# ---------------------------------------------------------------------------
# Degrading rather than guessing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("equation", [
    _eq(Y(T).diff(T, 2) - T * Y(T)),                    # Airy
    _eq(Y(T).diff(T), Y(T) ** 2 + T**2),                # Riccati
    _eq(Y(T).diff(T, 2) + sp.sin(Y(T))),                # the pendulum
])
def test_an_equation_outside_the_techniques_gets_no_derivation(equation):
    """None, not a vague derivation. The interface then shows exactly what it
    showed before this feature existed."""
    assert _derive(equation) is None


def test_no_hints_at_all_is_not_an_error():
    assert derive(_eq(Y(T).diff(T), Y(T)), Y, hints=()) is None
    assert preferred_hint(()) == ""
    assert preferred_hint(None) == ""


@pytest.mark.parametrize("equation,hint", [
    # Each pairs a technique with an equation it cannot possibly handle, which
    # is what a mis-classification would look like from inside a builder.
    (_eq(Y(T).diff(T, 2) + Y(T)), "separable"),
    (_eq(Y(T) ** 2, T), "separable"),
    (_eq(Y(T).diff(T), Y(T) ** 2), "1st_linear"),
    (_eq(Y(T).diff(T), sp.sin(Y(T))), "nth_linear_constant_coeff_homogeneous"),
    (_eq(Y(T).diff(T, 2) + sp.sin(T) * Y(T)), "nth_linear_euler_eq_homogeneous"),
])
def test_a_builder_pointed_at_the_wrong_equation_gives_up_cleanly(equation, hint):
    """`derive` runs on whatever a user typed, inside a worker whose only other
    option is to die. It may give up; it may not raise, and it may not claim a
    result it does not have."""
    derivation = derive(equation, Y, hints=(hint,))
    assert isinstance(derivation, Derivation)
    assert derivation.result is None
    assert derivation.message, "a derivation that stopped must say why"
    assert not derivation.complete
    assert derivation.verified is not True


# ---------------------------------------------------------------------------
# Every equation the app itself offers
# ---------------------------------------------------------------------------


def _examples():
    from odesuite_app.symbolic import EXAMPLES

    return [(name, spec) for name, spec in EXAMPLES.items() if not spec.is_system]


@pytest.mark.parametrize("name,spec", _examples(),
                         ids=[n for n, _ in _examples()])
def test_every_built_in_example_derives_or_declines(name, spec):
    """The examples are one click away in the editor, so they are the
    derivations a user is most likely to see. Each must either narrate cleanly
    or decline -- never narrate badly."""
    from odesuite_app.symbolic import parse_equation

    parsed = parse_equation(spec)
    derivation = derive(
        parsed.equation, parsed.function,
        hints=sp.classify_ode(parsed.equation, parsed.function(T)),
        ics=parsed.ics,
    )
    if derivation is None:
        return                      # no elementary technique; the honest answer

    failed = [s.title for s in derivation.steps if s.verified is False]
    assert not failed, f"{name}: these steps did not verify: {failed}"
    assert derivation.verified is True, f"{name}: {derivation.message}"


def test_a_decimal_initial_condition_does_not_poison_the_answer():
    """``y(0) = 0.1`` parses to a Float, which propagates through `solve` into a
    constant whose imaginary part is the *number* 3.14159… rather than `pi`.
    sympy cannot cancel that, so the answer came out carrying a complex
    exponential and the conditions step was marked failed -- a red cross on a
    correct step. The conditions are rationalised before solving instead."""
    from odesuite_app.symbolic import EXAMPLES, parse_equation

    parsed = parse_equation(EXAMPLES["Logistic (separable)"])
    derivation = derive(
        parsed.equation, parsed.function,
        hints=sp.classify_ode(parsed.equation, parsed.function(T)),
        ics=parsed.ics,
    )
    assert derivation.verified is True
    assert not derivation.result.atoms(sp.I), "a complex exponential survived"
    assert derivation.result == sp.exp(T) / (sp.exp(T) + 9)

    conditions = next(s for s in derivation.steps
                      if s.title == "Apply the initial conditions")
    assert conditions.verified is True


def test_conditions_that_cannot_be_decided_are_not_called_wrong():
    """False must mean demonstrably wrong. `check_answer` holds to the same
    rule, and for the same reason: the alternative tells someone their correct
    work is incorrect."""
    from odesuite_app.steps import _conditions_hold

    k = sp.Symbol("k")
    assert _conditions_hold(sp.exp(-T), {Y(sp.Integer(0)): 1}) is True
    assert _conditions_hold(sp.exp(-T), {Y(sp.Integer(0)): 2}) is False
    # A parameter left in makes the residual undecidable, not false.
    assert _conditions_hold(k * sp.exp(-T), {Y(sp.Integer(0)): 1}) is None


# ---------------------------------------------------------------------------
# The private sympy dependency
# ---------------------------------------------------------------------------


def test_the_private_ansatz_helper_is_still_where_it_was():
    """`_undetermined_coefficients_match` is private. Reusing it is worth it --
    choosing the trial set *is* the technique -- but a sympy release that moves
    it should fail here, loudly, rather than silently dropping the technique."""
    from sympy.solvers.ode.nonhomogeneous import (
        _undetermined_coefficients_match as match,
    )

    plain = match(sp.sin(T), T, func=Y(T))
    assert plain["test"] is True
    assert plain["trialset"] == {sp.sin(T), sp.cos(T)}

    resonant = match(sp.sin(T), T, func=Y(T),
                     eq_homogeneous=Y(T).diff(T, 2) + Y(T))
    assert resonant["trialset"] == {T * sp.sin(T), T * sp.cos(T)}, (
        "sympy no longer applies the resonance correction here"
    )


def test_the_public_coefficient_solver_is_still_public():
    """`solve_undetermined_coeffs` does the "match like terms" step. Unlike the
    ansatz helper it is public API, which is why it is used in preference."""
    a1, a2 = sp.symbols("A1 A2")
    residual = 3 * a1 * sp.cos(T) + 3 * a2 * sp.sin(T) - sp.sin(T)
    assert sp.solve_undetermined_coeffs(sp.Eq(residual, 0), [a1, a2], T) == {
        a1: 0, a2: sp.Rational(1, 3)
    }


def test_steps_needs_no_interface_toolkit():
    """It runs inside the solver subprocess, which has no Qt. `byhand` holds to
    the same rule for the same reason."""
    import subprocess
    import sys

    code = (
        "import sys; sys.modules['PySide6'] = None\n"
        "import odesuite_app.steps as s; assert s.TECHNIQUES\n"
        "print('ok')\n"
    )
    done = subprocess.run([sys.executable, "-c", code], capture_output=True,
                          text=True)
    assert done.returncode == 0, done.stderr[-400:]


# ---------------------------------------------------------------------------
# Through the subprocess, which is where it actually runs
# ---------------------------------------------------------------------------


def _solve(equation: str, ics: str = "", **kwargs):
    from odesuite_app.symbolic import EquationSpec, parse_equation, solve_symbolically

    parsed = parse_equation(
        EquationSpec(equations=[equation], initial_conditions=ics)
    )
    return solve_symbolically(parsed, steps=True, **kwargs)


@pytest.mark.parametrize("equation,technique", [
    ("y' = y*(1 - y)", "separable"),
    ("y' + 2*y = t", "1st_linear"),
    ("y'' + 3*y' + 2*y = 0", "nth_linear_constant_coeff_homogeneous"),
    ("y'' + 4*y = sin(t)",
     "nth_linear_constant_coeff_undetermined_coefficients"),
])
def test_the_derivation_survives_the_round_trip(equation, technique):
    """It is built in the worker and rebuilt from `srepr` in the parent, so the
    interface sees something quite different from what `derive` returned."""
    solution = _solve(equation)
    assert solution.derivation is not None, solution.message
    assert solution.derivation.technique == technique
    assert solution.derivation.verified is True
    assert all(step.title and step.latex for step in solution.derivation.steps)


def test_the_label_is_the_teaching_name_not_sympys_first():
    """This is what the Solver Studio's Symbolic tab shows too: it used to read
    "factorable", which is true and useless."""
    assert _solve("y'' + 3*y' + 2*y = 0").classification == (
        "nth_linear_constant_coeff_homogeneous"
    )
    assert _solve("y' + 2*y = t").classification == "1st_linear"


def test_the_whole_hint_list_comes_back():
    """The preference order cannot be applied to a single string, which is why
    `hints` exists alongside `classification`."""
    solution = _solve("y'' + 3*y' + 2*y = 0")
    assert "factorable" in solution.hints
    assert "nth_linear_constant_coeff_homogeneous" in solution.hints
    assert not any(h.endswith("_Integral") for h in solution.hints)


def test_narration_is_off_unless_asked_for():
    """The Studio does not display a derivation and should not pay for one."""
    from odesuite_app.symbolic import EquationSpec, parse_equation, solve_symbolically

    parsed = parse_equation(EquationSpec(equations=["y'' + 4*y = sin(t)"]))
    assert solve_symbolically(parsed).derivation is None
    assert solve_symbolically(parsed, steps=True).derivation is not None


def test_the_derivation_is_published_before_dsolve_is_attempted():
    """The mechanism behind surviving a hang, tested without racing a clock.

    The worker writes what it knows to stdout and flushes, so a process killed
    later still left it behind. Calling `solve_payload` directly with a
    capturing `emit` shows the ordering: the classification goes out first
    because it costs milliseconds, the derivation second, and `dsolve` -- the
    part that hangs -- is attempted only after both are safely out.
    """
    from odesuite_app.dsolve_worker import solve_payload

    equation = _eq(Y(T).diff(T) + 2 * Y(T), T)
    payload = {
        "equations": [sp.srepr(equation)],
        "functions": [sp.srepr(Y(T))],
        "ics": {},
        "steps": True,
    }
    published = []
    reply = solve_payload(payload, emit=published.append)

    assert len(published) == 2, "classification and derivation publish separately"
    # Publishing once, after narration, was a regression: a slow derivation
    # took the classification down with it when the timeout fired, so asking
    # for steps made the reply *worse* than not asking.
    assert published[0]["classification"], "the cheap half goes out first"
    assert published[0].get("derivation") is None
    assert published[1]["derivation"]["technique"] == "1st_linear"
    assert all(p["partial"] for p in published)
    # And none of them waited for the answer.
    assert "general" not in published[1]
    assert reply["ok"] and reply["general"]


@pytest.mark.slow
def test_a_derivation_outlives_a_dsolve_that_hangs():
    """``y' = sin(y)`` is the equation the README records `dsolve` hanging on --
    not slow, hanging. Separation of variables solves it in a few seconds, so
    the worker publishes the derivation *before* attempting `dsolve`, and the
    parent reads it back out of the killed process's captured output.

    Without this the Learning Hub would show nothing for an equation it can
    solve completely.

    What is asserted unconditionally is the *recovery*: the classification is
    milliseconds of work, so it is always published in time and must come back
    out of the killed process. The derivation is asserted only when narration
    finished inside the budget -- narrating this equation takes about four
    seconds idle but can exceed thirty under a fully parallel test run, and one
    hard limit covers narration and `dsolve` together. Racing that clock would
    make the test flaky rather than make the feature better; the ordering it
    depends on is pinned deterministically by
    `test_the_derivation_is_published_before_dsolve_is_attempted`.
    """
    solution = _solve("y' = sin(y)", timeout=30.0)

    assert solution.timed_out is True
    assert not solution.solved, "dsolve started returning; re-pick the example"

    # Recovered from what the killed process had already written.
    assert solution.classification == "separable"
    assert "separable" in solution.hints

    if solution.derivation is not None:
        assert solution.derivation.technique == "separable"
        assert solution.derivation.verified is True, (
            "a derivation that survived the kill must still be a correct one"
        )


def test_a_truncated_final_line_falls_back_to_the_last_whole_one():
    """A killed process can be cut off mid-write, so the reply is found by
    scanning backwards rather than by taking the last line outright."""
    from odesuite_app.symbolic import _last_reply

    assert _last_reply('{"ok": true, "a": 1}\n{"ok": fal') == {"ok": True, "a": 1}
    assert _last_reply(b'{"ok": true}\n') == {"ok": True}
    assert _last_reply("") is None
    assert _last_reply(None) is None
    assert _last_reply("not json at all") is None


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
    from odesuite_app.screens.learn_steps import StepsScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    screen = StepsScreen(SessionState(), PALETTES[palette_name])
    screen.resize(1500, 950)
    return screen


def _submit(screen, qapp, equation, ics=""):
    from PySide6.QtCore import QThreadPool

    from odesuite_app.symbolic import EquationSpec

    screen._on_submitted(
        EquationSpec(equations=[equation], initial_conditions=ics)
    )
    QThreadPool.globalInstance().waitForDone(60_000)
    qapp.processEvents()
    qapp.processEvents()


@pytest.mark.parametrize("palette", ["dark", "light"])
def test_the_screen_renders_in_both_palettes(qapp, palette):
    screen = _screen(palette)
    qapp.processEvents()
    assert not screen.grab().isNull()
    screen.deleteLater()


def test_the_derivation_reaches_the_screen(qapp):
    screen = _screen()
    _submit(screen, qapp, "y'' + 4*y = sin(t)")

    assert screen.steps._heading.text() == "Undetermined coefficients"
    # One card per step, plus the closing verdict.
    assert screen.steps._body.count() == 10
    assert not screen.grab().isNull()
    screen.deleteLater()


def test_an_unsupported_equation_says_so_instead_of_going_blank(qapp):
    """Airy has no elementary technique. The panel has to explain that rather
    than leave an empty column that reads as a bug."""
    screen = _screen()
    _submit(screen, qapp, "y'' - t*y = 0")

    assert screen.steps._body.count() == 0
    assert screen.steps._status.isVisibleTo(screen.steps)
    assert "first course" in screen.steps._status.text()
    screen.deleteLater()


def test_the_answer_box_still_works_beside_the_derivation(qapp):
    """L1c's check must survive the layout change."""
    screen = _screen()
    _submit(screen, qapp, "y'' + 4*y = 0")

    screen.answer.setText("3*sin(2*t)")
    screen.check()
    assert "✓" in screen.verdict.text()

    screen.answer.setText("exp(-t)")
    screen.check()
    assert "✗" in screen.verdict.text()
    screen.deleteLater()


def test_the_derivation_gets_the_larger_half(qapp):
    """It is the point of the screen; the closed form is the supporting act."""
    screen = _screen()
    qapp.processEvents()
    layout = screen.layout().itemAt(1).widget().layout()
    assert layout.stretch(0) > layout.stretch(1)
    screen.deleteLater()


def test_only_this_screen_asks_for_narration(qapp):
    """The Studio's Symbolic tab shows no derivation, so it must not pay the
    cost of building one."""
    from odesuite_app.screens.lab import LabScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES
    from odesuite_app.widgets.symbolicpanel import SymbolicPanel

    assert _screen().symbolic.narrate is True
    assert SymbolicPanel(PALETTES["dark"]).narrate is False

    lab = LabScreen(SessionState(), PALETTES["dark"])
    for panel in lab.findChildren(SymbolicPanel):
        assert panel.narrate is False
    lab.deleteLater()


def test_an_equation_the_editor_accepts_but_the_parser_rejects_is_reported(qapp):
    """The editor only checks that a derivative is present, so an unknown
    function reaches `parse_equation` and fails there. That path called
    `show_message(..., error=True)` where the argument is `kind`, so instead of
    an error message the user got a TypeError on stderr and a silent screen.
    Found by the equivalent test on the Laplace screen; both are fixed.
    """
    from PySide6.QtWidgets import QLineEdit

    screen = _screen()
    screen.editor.findChildren(QLineEdit)[0].setText("y' = foo(t)")
    screen.editor.submit()                        # the real path, not _on_submitted
    qapp.processEvents()

    assert "cannot parse" in screen.editor.message.text()
    screen.deleteLater()


# ---------------------------------------------------------------------------
# Exact equations: the one technique not taken from a hint
# ---------------------------------------------------------------------------


def test_exactness_is_decided_here_and_not_by_classify_ode():
    """The measurement this builder exists because of.

    On the equations an exact-equations lesson is actually about, sympy does
    not offer `1st_exact` at all -- and it *does* offer it on an equation that
    is not exact under this splitting. Neither half of that is a sympy bug; it
    normalises M and N differently. It does mean the hint cannot be trusted,
    which is why `derive` tests for exactness itself.
    """
    from odesuite_app.steps import _is_exact

    missed = _eq(Y(T).diff(T), -(2 * T + Y(T)) / (T + 3 * Y(T) ** 2))
    assert "1st_exact" not in sp.classify_ode(missed, Y(T))
    assert _is_exact(missed, Y)

    offered = _eq(Y(T).diff(T), -Y(T) / T**2)
    assert "1st_exact" in sp.classify_ode(offered, Y(T))
    assert not _is_exact(offered, Y)

    # And `1st_exact` is never in the hint-driven table, so it cannot be
    # dispatched from a hint even when sympy offers one.
    assert "1st_exact" not in TECHNIQUES


def test_an_exact_equation_is_narrated():
    derivation = _derive(EXACT)
    assert derivation is not None
    assert derivation.technique == "1st_exact"
    assert derivation.title == "Exact equation"
    assert derivation.verified is True
    assert derivation.complete


def test_the_exact_steps_are_the_ones_a_course_writes():
    assert [step.title for step in _derive(EXACT).steps] == [
        "Write it as M dt + N dy = 0",
        "Test for exactness",
        "Integrate M with respect to t",
        "Pin h(y) by matching N",
        "The solution is ψ = C",
        "Solve for y",
    ]


def test_every_exact_step_passes_its_own_check():
    failed = [s.title for s in _derive(EXACT).steps if s.verified is False]
    assert not failed, f"these steps did not verify: {failed}"


def test_the_exactness_test_is_shown_as_the_test():
    """∂M/∂y = ∂N/∂t is not scaffolding, it is the step that decides whether
    the method applies at all, so it has to be on screen and checked."""
    step = next(s for s in _derive(EXACT).steps
                if s.title == "Test for exactness")
    assert step.verified is True
    assert "partial" in step.latex


def test_an_equation_that_is_not_exact_is_not_claimed_to_be():
    from odesuite_app.steps import _is_exact

    assert not _is_exact(_eq(Y(T).diff(T), -(T + Y(T) ** 2) / (2 * T)), Y)
    assert _derive(_eq(Y(T).diff(T), -(T + Y(T) ** 2) / (2 * T))) is None


@pytest.mark.parametrize("equation,expected", [
    # Exact *and* linear: a course reaches for the integrating factor.
    (_eq(Y(T).diff(T), -(3 * T**2 + 2 * Y(T)) / (2 * T + 1)), "1st_linear"),
    # Exact *and* homogeneous: a course substitutes.
    (_eq(Y(T).diff(T), -(2 * T + 3 * Y(T)) / (3 * T + 4 * Y(T))),
     "1st_homogeneous_coeff_best"),
])
def test_exactness_never_displaces_a_technique_met_earlier(equation, expected):
    """The detector runs only where the hints named nothing, so an equation
    with an earlier method keeps it."""
    from odesuite_app.steps import _is_exact

    assert _is_exact(equation, Y), "the premise of this test has changed"
    assert _derive(equation).technique == expected


def test_a_high_degree_psi_is_left_implicit_rather_than_solved():
    """Measured: a ψ quartic in y sends `solve` past sixty seconds, and a cubic
    one returns nested radicals nobody would write down. A textbook leaves
    those as ψ = C, and so does this."""
    import time

    quartic = _eq(Y(T).diff(T), -(2 * T * Y(T) + 1) / (T**2 + 4 * Y(T) ** 3))
    start = time.perf_counter()
    derivation = _derive(quartic)
    took = time.perf_counter() - start

    assert took < 15, f"solving was attempted anyway ({took:.0f}s)"
    assert derivation.technique == "1st_exact"
    assert derivation.result is None
    assert "implicit" in derivation.message or "left in that form" in \
        derivation.message
    # The working is still shown, and every step of it still checks out.
    assert [s.title for s in derivation.steps][-1] == "The solution is ψ = C"
    assert not [s for s in derivation.steps if s.verified is False]


# ---------------------------------------------------------------------------
# The substitutions
# ---------------------------------------------------------------------------


def test_a_substitution_says_v_where_it_means_v():
    """The hand-off shares the two first-order builders rather than copying
    them, so the letters have to follow the substitution or the derivation
    would claim to be solving for y while solving for v."""
    steps = _derive(CANONICAL["Bernoulli"]).steps
    standard = next(s for s in steps if s.title == "Put it in standard form")
    assert standard.latex.startswith("v'")
    assert "y" not in standard.latex

    divided = next(s for s in steps
                   if s.title == "Divide by the integrating factor")
    assert divided.latex.startswith("v(t)")


def test_a_substitution_ends_in_y_and_is_checked_against_the_original():
    for technique in ("Bernoulli", "1st_homogeneous_coeff_best"):
        derivation = _derive(CANONICAL[technique])
        last = derivation.steps[-1]
        assert last.title == "Undo the substitution"
        assert last.latex.startswith("y(t)")
        assert last.verified is True, technique
        assert derivation.verified is True, technique


def test_bernoulli_handles_a_negative_power():
    """`y' = (t² + y²)/(ty)` is Bernoulli with n = −1, which `Poly` refuses to
    read. It is also homogeneous, and that is the technique a course teaches
    it by -- so the negative power is checked directly."""
    from odesuite_app.steps import _bernoulli_parts

    parts = _bernoulli_parts(_eq(Y(T).diff(T), (T**2 + Y(T) ** 2) / (T * Y(T))),
                             Y)
    assert parts is not None
    p, q, n = parts
    assert n == -1
    assert sp.simplify(p + 1 / T) == 0
    assert sp.simplify(q - T) == 0


def test_the_initial_condition_chooses_the_sign_after_a_root():
    """Undoing an even root leaves ±, and the inner builder never saw the
    condition because it was solving in v. Taking the first branch regardless
    gave `y = -t·sqrt(...)`, which cannot pass through y(1) = 2 at all."""
    derivation = _derive(
        _eq(Y(T).diff(T), (T**2 + Y(T) ** 2) / (T * Y(T))),
        ics={Y(1): 2},
    )
    assert derivation.verified is True
    assert derivation.result is not None
    assert float(derivation.result.subs(T, 1)) == pytest.approx(2.0)


def test_a_transcendental_rearrangement_degrades_rather_than_raising():
    """`atan(v) + ln(v²+1)/2 = -ln t + C` is where the homogeneous substitution
    lands on `y' = (y-t)/(y+t)`, and `solve` raises NotImplementedError there
    rather than returning nothing. The integrated form is still correct and
    still worth showing."""
    derivation = _derive(_eq(Y(T).diff(T), (Y(T) - T) / (Y(T) + T)))
    assert derivation is not None
    assert derivation.technique == "1st_homogeneous_coeff_best"
    assert derivation.result is None
    assert "cannot be rearranged" in derivation.message
    assert "stopped early" not in derivation.message
    assert len(derivation.steps) >= 5
    assert not [s for s in derivation.steps if s.verified is False]


# ---------------------------------------------------------------------------
# The worker: not asking `dsolve` what has already been answered
# ---------------------------------------------------------------------------


def _payload(equation, ics=None):
    return {
        "equations": [sp.srepr(equation)],
        "functions": [sp.srepr(Y(T))],
        "ics": {sp.srepr(k): sp.srepr(v) for k, v in (ics or {}).items()},
        "steps": True,
    }


def test_a_technique_sympy_never_named_is_not_handed_back_to_dsolve():
    """Measured: `dsolve` on `y' = -(2t+y)/(t+3y²)` runs past forty seconds
    trying `lie_group`, so the whole twelve-second budget buys a timeout. The
    derivation has already substituted its answer back and simplified it to
    zero, which is a stronger warrant than `dsolve` returning would have
    been."""
    import time

    from odesuite_app.dsolve_worker import solve_payload

    start = time.perf_counter()
    reply = solve_payload(_payload(EXACT))
    took = time.perf_counter() - start

    assert took < 10, f"dsolve was asked anyway ({took:.0f}s)"
    assert reply["ok"]
    assert reply["derivation"]["technique"] == "1st_exact"
    assert "1st_exact" not in reply["hints"], "the premise has changed"
    assert reply["general"], "the verified answer was not handed over"


def test_the_handover_uses_particular_when_there_are_conditions():
    from odesuite_app.dsolve_worker import solve_payload

    reply = solve_payload(_payload(EXACT, {Y(0): 1}))
    assert reply["ok"]
    assert reply.get("particular")
    assert "general" not in reply


def test_a_technique_sympy_does_name_is_still_asked_of_dsolve():
    """The guard is deliberately narrow. Where the hint list names the
    technique, sympy knows it too and nothing changes."""
    from odesuite_app.dsolve_worker import solve_payload

    reply = solve_payload(_payload(_eq(Y(T).diff(T) + 2 * Y(T), T)))
    assert reply["ok"]
    assert "1st_linear" in reply["hints"]
    assert reply["general"]


def test_a_dsolve_answer_with_several_branches_is_not_thrown_away():
    """`dsolve` returns a *list* where solving for y leaves branches, and
    reading `.rhs` off the list raised AttributeError -- which the caller then
    reported as "no method", discarding an answer sympy had found."""
    from odesuite_app.dsolve_worker import _right_hand_side

    equation = _eq(Y(T).diff(T) + Y(T), T * Y(T) ** 3)
    solved = sp.dsolve(equation, Y(T))
    assert isinstance(solved, list), "the premise of this test has changed"
    restored = sp.sympify(_right_hand_side(solved))
    assert restored == solved[0].rhs
