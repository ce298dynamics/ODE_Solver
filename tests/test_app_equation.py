"""Typed equations as catalogue entries.

The design under test: an equation the user types becomes an ordinary
`CatalogEntry`, so the rest of the application solves and draws it without
knowing where it came from. Two consequences need pinning.

**It must reach everything.** The entry has to build, solve, and carry the
labels, plot kind and sliders that the screens read.

**It must not leak.** The home gallery, the tag filter and the thumbnail cache
enumerate the *fixed* problem set. A transient entry appearing there would put a
user's equation in the gallery and write a thumbnail to disk under a key that
means something different next session.
"""

from __future__ import annotations

import numpy as np
import pytest

sp = pytest.importorskip("sympy", reason="the app extra is not installed")

from odesuite import solve  # noqa: E402
from odesuite_app import catalog  # noqa: E402
from odesuite_app.custom import ParseError  # noqa: E402
from odesuite_app.equationmodel import (  # noqa: E402
    build_entry,
    default_range,
    entry_from_text,
    parameter_specs,
)
from odesuite_app.symbolic import (  # noqa: E402
    EXAMPLES,
    EquationSpec,
    parse_equation,
    solve_symbolically,
    to_first_order,
)

T = sp.Symbol("t", real=True)


@pytest.fixture(autouse=True)
def _no_leftover_entry():
    """The registry is module state; never let one test's equation reach another."""
    catalog.clear_user_equation()
    yield
    catalog.clear_user_equation()


def _register(spec: EquationSpec):
    entry, parsed = entry_from_text(spec)
    catalog.register_user_equation(entry)
    return entry, parsed


# -- the round trip ------------------------------------------------------

@pytest.mark.parametrize("name", sorted(EXAMPLES))
def test_every_example_becomes_a_solvable_entry(name):
    entry, _ = _register(EXAMPLES[name])
    fetched = catalog.get(catalog.USER_KEY)
    assert fetched is entry

    bench = fetched.build(fetched.defaults())
    solution = solve(bench.problem, method="dopri5", rtol=1e-9, atol=1e-12,
                     dense_output=True, max_steps=200_000)
    assert solution.success, solution.message
    assert np.all(np.isfinite(solution.y[:, -1]))


@pytest.mark.parametrize("name", sorted(EXAMPLES))
def test_entry_labels_every_state(name):
    entry, _ = _register(EXAMPLES[name])
    bench = entry.build(entry.defaults())
    assert len(entry.labels) == bench.problem.y0.size


@pytest.mark.slow
def test_closed_form_agrees_with_the_numeric_solve_through_the_entry():
    """The S3 gate: two independent routes to the same answer.

    sympy and this library share no code, so agreement is evidence about both.
    """
    checked = 0
    for name, spec in EXAMPLES.items():
        entry, parsed = _register(spec)
        symbolic = solve_symbolically(parsed)
        if symbolic.particular is None or parsed.is_system:
            continue
        bench = entry.build(entry.defaults())
        numeric = solve(bench.problem, method="radau", rtol=1e-11, atol=1e-13,
                        dense_output=True, max_steps=300_000)
        assert numeric.success, name

        exact = sp.lambdify(T, symbolic.particular, "numpy")
        grid = np.linspace(bench.problem.t0, bench.problem.tf, 300)
        error = np.abs(np.asarray(exact(grid), float) - numeric.sol(grid)[0]).max()
        assert error < 1e-8, f"{name}: symbolic and numeric differ by {error:.2e}"
        checked += 1
    assert checked >= 8, "expected most examples to have a closed form"


# -- the trap: a forced equation has no static vector field --------------

#: ``(equation, span, autonomous)``. The last column is the whole point: a
#: static phase portrait is only meaningful when it is ``True``. The span is
#: carried because Cauchy-Euler is singular at the origin and cannot be started
#: there at all.
AUTONOMY = [
    ("y'' + 2*y' + 5*y = 0", (0.0, 10.0), True),      # constant coefficients
    ("y'' + y = cos(t)", (0.0, 10.0), False),         # forced
    ("t**2*y'' + t*y' - y = 0", (1.0, 6.0), False),   # variable coefficients
    ("y' = y*(1 - y)", (0.0, 10.0), True),            # autonomous, first order
    ("y' + 2*y = exp(-t)", (0.0, 10.0), False),       # forced, first order
]


@pytest.mark.parametrize("text,span,expected", AUTONOMY)
def test_time_dependence_is_detected(text, span, expected):
    parsed = parse_equation(EquationSpec(equations=[text], t_span=span))
    assert to_first_order(parsed).autonomous is expected


def test_a_forced_equation_is_refused_a_vector_field():
    """Regression: the field is sampled at t=0 and would silently mislead.

    `analysis.vector_field` evaluates the right-hand side at a single instant.
    For a forced equation the field genuinely moves, so a drawn trajectory
    would cross its own streamlines -- a picture that looks right and is not.
    `autonomous_2d` is the flag the portrait screen filters on.
    """
    forced, _ = _register(EXAMPLES["Forced, resonant"])
    assert forced.plot_kind == "phase", "still worth plotting y against y'"
    assert not forced.autonomous_2d, "but not against a static field"

    free, _ = _register(EXAMPLES["Damped oscillator"])
    assert free.autonomous_2d, "an autonomous planar system should get one"


def test_a_third_order_equation_is_not_offered_a_phase_plane():
    entry, _ = _register(EXAMPLES["Third order"])
    assert entry.plot_kind == "time"
    assert not entry.autonomous_2d


# -- registry hygiene ----------------------------------------------------

def test_the_user_entry_is_reachable_but_not_enumerated():
    _register(EXAMPLES["Damped oscillator"])
    assert catalog.get(catalog.USER_KEY) is not None
    assert catalog.USER_KEY not in catalog.keys()
    assert catalog.USER_KEY in catalog.keys(include_user=True)


def test_the_user_entry_stays_out_of_the_gallery():
    """Home builds its grid from `filter_by`, and thumbnails from `CATALOG`."""
    before = len(catalog.CATALOG)
    _register(EXAMPLES["Van der Pol (no closed form)"])

    assert len(catalog.CATALOG) == before
    assert all(e.key != catalog.USER_KEY for e in catalog.filter_by("all"))
    assert all(e.key != catalog.USER_KEY for e in catalog.filter_by("user"))
    assert "user" not in catalog.all_tags()


def test_keys_include_user_is_harmless_with_nothing_registered():
    assert catalog.keys(include_user=True) == catalog.keys()


def test_registering_replaces_rather_than_accumulates():
    _register(EXAMPLES["Overdamped"])
    entry, _ = _register(EXAMPLES["Repeated root"])
    assert catalog.get(catalog.USER_KEY) is entry
    assert catalog.keys(include_user=True).count(catalog.USER_KEY) == 1


def test_a_user_entry_must_use_the_reserved_key():
    _, parsed = entry_from_text(EXAMPLES["Overdamped"])
    wrong = build_entry(parsed)
    wrong = type(wrong)(**{**wrong.__dict__, "key": "van_der_pol"})
    with pytest.raises(ValueError, match="reserved|__user__"):
        catalog.register_user_equation(wrong)


def test_an_unknown_key_still_raises_with_nothing_registered():
    with pytest.raises(KeyError):
        catalog.get("no_such_problem")


# -- parameters and sliders ----------------------------------------------

def test_symbolic_parameters_become_sliders():
    entry, _ = _register(EXAMPLES["Van der Pol (no closed form)"])
    names = [p.name for p in entry.params]
    assert "mu" in names
    assert "t_end" in names, "a duration slider is always offered"


def test_a_slider_changes_the_equation_it_solves():
    """The parameter has to reach the compiled right-hand side, not just the UI."""
    entry, _ = _register(EXAMPLES["Van der Pol (no closed form)"])
    state = np.array([0.5, 1.0])            # y' != 0, so mu contributes

    gentle = entry.build({**entry.defaults(), "mu": 0.5})
    violent = entry.build({**entry.defaults(), "mu": 20.0})
    assert not np.allclose(
        gentle.problem.f(0.0, state), violent.problem.f(0.0, state)
    )
    # The exact Jacobian must track it too, or the implicit methods get a
    # derivative for a different problem than the one being solved.
    assert not np.allclose(
        gentle.problem.jac(0.0, state), violent.problem.jac(0.0, state)
    )


def test_the_duration_slider_changes_the_span():
    entry, _ = _register(EXAMPLES["Damped oscillator"])
    bench = entry.build({**entry.defaults(), "t_end": 3.0})
    assert bench.problem.tf == pytest.approx(3.0)


def test_a_default_outside_its_range_is_widened_not_clipped():
    """A pinned slider would report a value the equation was not built at."""
    spec = EquationSpec(equations=["y' = -k*y"], parameters={"k": 5.0})
    specs = parameter_specs(spec, ranges={"k": (0.0, 1.0)})
    assert specs[0].low <= specs[0].default <= specs[0].high


def test_default_range_brackets_the_value_and_keeps_its_sign():
    low, high = default_range(3.0)
    assert low <= 3.0 <= high and low >= 0.0
    low, high = default_range(-2.0)
    assert low <= -2.0 <= high and high <= 0.0
    low, high = default_range(0.0)
    assert low < 0.0 < high, "a zero value still needs a usable range"


# -- copy as code --------------------------------------------------------

def test_copy_as_code_emits_a_runnable_snippet(tmp_path):
    """Regression: the built-in `code` renders `problems.{factory.__name__}`.

    A user entry's factory is a closure, so the default would emit a call to a
    function that does not exist. This has to be executed, not pattern-matched:
    inspecting the string is exactly how the original version of this bug
    survived review.
    """
    import subprocess
    import sys

    entry, _ = _register(EXAMPLES["Van der Pol (no closed form)"])
    code = entry.code({**entry.defaults(), "mu": 7.5, "t_end": 4.0})
    assert "<lambda>" not in code and "factory" not in code

    script = tmp_path / "snippet.py"
    script.write_text(code, encoding="utf-8")
    finished = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, timeout=300,
    )
    assert finished.returncode == 0, finished.stderr[-800:]


def test_the_snippet_carries_the_slider_values():
    entry, _ = _register(EXAMPLES["Van der Pol (no closed form)"])
    code = entry.code({**entry.defaults(), "mu": 7.5, "t_end": 4.0})
    assert "7.5" in code and "4.0" in code


# -- failure ------------------------------------------------------------

def test_starting_at_a_singularity_says_so():
    """Regression: this surfaced as a bare ZeroDivisionError.

    `t^2 y'' + t y' - y = 0` is singular at the origin. Starting there made
    ``f(t0, y0)`` infinite, which drove the automatic starting step to zero and
    then divided by it -- inside a step-size heuristic, naming nothing the user
    had typed. Letting people type their own equations makes that reachable.
    """
    spec = EquationSpec(
        equations=["t**2*y'' + t*y' - y = 0"],
        initial_conditions="y(0) = 1, y'(0) = 0", t_span=(0.0, 5.0),
    )
    with pytest.raises(ValueError, match="not finite|singular"):
        to_first_order(parse_equation(spec))


def test_the_same_equation_away_from_the_singularity_is_fine():
    entry, _ = _register(EXAMPLES["Cauchy–Euler"])       # starts at t = 1
    bench = entry.build(entry.defaults())
    solution = solve(bench.problem, method="dopri5", rtol=1e-10, atol=1e-13,
                     dense_output=True)
    assert solution.success
    # Closed form is t/2 + 1/(2t).
    end = bench.problem.tf
    assert solution.y[0, -1] == pytest.approx(end / 2 + 1 / (2 * end), rel=1e-6)


def test_a_bad_equation_raises_before_anything_is_registered():
    with pytest.raises(ParseError):
        entry_from_text(EquationSpec(equations=["y = 5"]))     # no derivative
    assert catalog.user_entry() is None


# -- the slope field -----------------------------------------------------

def test_slope_field_reports_the_true_slope():
    from odesuite_app import analysis

    parsed = parse_equation(
        EquationSpec(equations=["y' = y*(1 - y)"], t_span=(0.0, 8.0))
    )
    problem = to_first_order(parsed)
    segments, slopes = analysis.slope_field(problem, (0.0, 8.0), (-0.3, 1.4),
                                            resolution=15)
    assert segments.shape[0] == 15 * 15

    midpoints = segments.mean(axis=1)
    expected = midpoints[:, 1] * (1.0 - midpoints[:, 1])
    assert np.abs(slopes - expected).max() < 1e-9

    # The angle has to carry the slope, or the picture is decorative.
    delta = segments[:, 1, :] - segments[:, 0, :]
    assert np.abs(delta[:, 1] / delta[:, 0] - slopes).max() < 1e-9


def test_slope_field_dashes_are_the_same_length_on_screen():
    """Only the angle should carry information.

    The axes differ by orders of magnitude, so a fixed length in data units
    would be a full-width streak on one axis and invisible on the other.
    """
    from odesuite_app import analysis

    parsed = parse_equation(
        EquationSpec(equations=["y' = 100*y*(1 - y)"], t_span=(0.0, 0.2))
    )
    tlim, ylim = (0.0, 0.2), (-0.3, 1.4)
    segments, _ = analysis.slope_field(to_first_order(parsed), tlim, ylim)

    delta = segments[:, 1, :] - segments[:, 0, :]
    on_screen = np.hypot(
        delta[:, 0] / (tlim[1] - tlim[0]), delta[:, 1] / (ylim[1] - ylim[0])
    )
    assert on_screen.max() / on_screen.min() == pytest.approx(1.0, abs=1e-9)


def test_slope_field_is_refused_for_a_system():
    """It is a picture of a scalar equation; a system needs the phase plane."""
    from odesuite_app import analysis

    parsed = parse_equation(EquationSpec(equations=["y'' + y = 0"]))
    with pytest.raises(ValueError, match="scalar"):
        analysis.slope_field(to_first_order(parsed), (0.0, 1.0), (0.0, 1.0))


# ---------------------------------------------------------------------------
# The screens
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


def _settle(qapp, state=None, rounds: int = 60) -> None:
    """Pump the event loop, elapsing real time as well as iterations.

    The sleep is not padding. Asking for a closed form is deliberately delayed
    behind a 450 ms timer so that dragging a slider does not spawn a subprocess
    per pixel, and a Qt timer fires on wall-clock time. A loop of
    `processEvents` plus `waitForDone` returns instantly once the pool is idle,
    so a round-counting wait can burn through sixty iterations in a few
    milliseconds and never let the timer fire at all -- which is how this
    helper produced a test that passed alone and failed in the suite.
    """
    import time

    from PySide6.QtCore import QThreadPool

    deadline = time.monotonic() + rounds * 0.02
    while time.monotonic() < deadline:
        qapp.processEvents()
        if state is not None:
            state.runner.wait(200)
        QThreadPool.globalInstance().waitForDone(20)
        time.sleep(0.01)
    qapp.processEvents()


def _wait_until(qapp, predicate, timeout: float = 40.0) -> bool:
    """Pump until `predicate` holds, or the deadline passes.

    Preferred over a fixed wait wherever there is something to test for: it
    finishes as soon as the work lands and still fails loudly if it never does.
    """
    import time

    from PySide6.QtCore import QThreadPool

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        qapp.processEvents()
        if predicate():
            return True
        QThreadPool.globalInstance().waitForDone(20)
        time.sleep(0.02)
    qapp.processEvents()
    return bool(predicate())


def _wait_for_closed_form(qapp, screen, timeout: float = 60.0):
    """Wait for the debounced `dsolve` result, not merely the fast preview."""
    _wait_until(
        qapp,
        lambda: screen.symbolic.solution is not None
        and screen.symbolic.solution.solved,
        timeout,
    )
    return screen.symbolic.solution


def _lab(qapp):
    from odesuite_app.screens.lab import LabScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import DARK

    state = SessionState()
    screen = LabScreen(state, DARK)
    _settle(qapp, state, 10)
    return screen, state


def test_the_lab_starts_on_the_catalogue(qapp):
    screen, state = _lab(qapp)
    assert not screen.showing_equation
    assert state.problem_key != catalog.USER_KEY
    assert not screen.tabs.isTabEnabled(1), "no equation, nothing symbolic to show"
    screen.deleteLater()


def test_switching_to_your_equation_solves_one(qapp):
    screen, state = _lab(qapp)
    screen.source_buttons.button(1).click()
    _settle(qapp, state, 40)

    assert screen.showing_equation
    assert state.problem_key == catalog.USER_KEY
    assert screen.tabs.isTabEnabled(1)
    assert state.result is not None and state.result.ok

    # The roots arrive immediately; the closed form is debounced behind them.
    assert screen.symbolic.solution is not None
    assert screen.symbolic.solution.roots, "the characteristic roots are local"

    solution = _wait_for_closed_form(qapp, screen)
    assert solution.solved, "the debounced dsolve never landed"
    assert solution.verified is True
    screen.deleteLater()


def test_switching_back_restores_the_catalogue_problem(qapp):
    screen, state = _lab(qapp)
    original = state.problem_key
    screen.source_buttons.button(1).click()
    _settle(qapp, state, 30)
    screen.source_buttons.button(0).click()
    _settle(qapp, state, 20)

    assert state.problem_key == original
    assert not screen.tabs.isTabEnabled(1)
    screen.deleteLater()


def test_editing_the_equation_is_not_swallowed(qapp):
    """Regression: the key never changes, so `set_problem` returned early.

    Every typed equation is registered under the same reserved key. Without
    forcing, the second one is silently ignored and the screen goes on showing
    the first one's answer -- which looks like the solver being wrong.
    """
    screen, state = _lab(qapp)
    screen.source_buttons.button(1).click()
    _settle(qapp, state, 30)
    first = state.entry.labels

    screen.editor.equation_fields[0].setText("y^(3) - y = 0")
    screen.editor.ics.setText("y(0) = 1, y'(0) = 0, y''(0) = 0")
    screen.editor.submit()
    _settle(qapp, state, 30)

    assert len(first) == 2 and len(state.entry.labels) == 3
    assert state.result.solution.y.shape[0] == 3
    screen.deleteLater()


def test_a_parameter_slider_moves_the_characteristic_roots(qapp):
    """The showcase: dragging c crosses the discriminant."""
    import sympy as sp

    from odesuite_app.symbolic import describe_roots

    screen, state = _lab(qapp)
    screen.source_buttons.button(1).click()
    _settle(qapp, state, 20)

    screen.editor.equation_fields[0].setText("y'' + 2*c*y' + y = 0")
    screen.editor.ics.setText("y(0) = 1, y'(0) = 0")
    for label, value, low, high in screen.editor.parameter_rows:
        if label.text() == "c":
            value.setText("0.3")
            low.setText("0")
            high.setText("3")
    screen.editor.submit()
    _settle(qapp, state, 30)
    assert "c" in [p.name for p in state.entry.params]

    seen = {}
    for amount in (0.3, 1.0, 2.0):
        state.set_param("c", amount)
        qapp.processEvents()
        solution = screen.symbolic.solution
        seen[amount] = (solution.roots, describe_roots(solution.roots, 2))

    under, critical, over = seen[0.3], seen[1.0], seen[2.0]
    assert any(sp.im(r) != 0 for r, _ in under[0]), "c=0.3 should be underdamped"
    assert critical[0] == [(sp.Integer(-1), 2)], "c=1 is the repeated root"
    assert "critically damped" in critical[1]
    assert all(sp.im(r) == 0 for r, _ in over[0]), "c=2 should be overdamped"
    assert "overdamped" in over[1]
    screen.deleteLater()


@pytest.mark.slow
def test_a_typed_equation_reaches_the_other_screens(qapp):
    """The point of registering it as a catalogue entry."""
    from odesuite_app.screens.portrait import PortraitScreen
    from odesuite_app.screens.race import RaceScreen
    from odesuite_app.screens.stiffness import StiffnessScreen
    from odesuite_app.theme import DARK

    screen, state = _lab(qapp)
    screen.source_buttons.button(1).click()
    _settle(qapp, state, 30)
    screen.editor.select_example("Van der Pol")     # autonomous and planar
    _settle(qapp, state, 40)
    assert state.problem_key == catalog.USER_KEY

    for factory in (PortraitScreen, StiffnessScreen, RaceScreen):
        other = factory(state, DARK)
        other.refresh_problems()
        picker = getattr(other, "picker", None) or other.problem_picker
        keys = [picker.itemData(i) for i in range(picker.count())]
        assert catalog.USER_KEY in keys, f"{factory.__name__} did not offer it"
        other.deleteLater()
    screen.deleteLater()


def test_a_forced_equation_is_kept_out_of_the_phase_portrait(qapp):
    """The other half of the trap: the screen must actually apply the flag."""
    from odesuite_app.screens.portrait import PortraitScreen
    from odesuite_app.theme import DARK

    screen, state = _lab(qapp)
    screen.source_buttons.button(1).click()
    _settle(qapp, state, 20)
    screen.editor.select_example("Forced, resonant")
    _settle(qapp, state, 40)

    portrait = PortraitScreen(state, DARK)
    portrait.refresh_problems()
    keys = [portrait.picker.itemData(i) for i in range(portrait.picker.count())]
    assert catalog.USER_KEY not in keys, "a forced equation has no static field"
    portrait.deleteLater()
    screen.deleteLater()


def test_a_bad_equation_shows_a_message_rather_than_crashing(qapp):
    screen, state = _lab(qapp)
    screen.source_buttons.button(1).click()
    _settle(qapp, state, 20)

    screen.editor.equation_fields[0].setText("y'' + wobble = 0")
    for label, value, low, high in screen.editor.parameter_rows:
        if label.text() == "wobble":
            label.setText("")               # leave it genuinely undeclared
    screen.editor.submit()
    _settle(qapp, state, 10)

    assert screen.editor.message.text(), "the user must be told something"
    screen.deleteLater()
