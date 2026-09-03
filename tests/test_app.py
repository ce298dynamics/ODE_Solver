"""The desktop application: catalogue, state machine and headless rendering.

Runs entirely offscreen. The point is not to test Qt but to test the parts of
the app that carry real logic -- that every catalogued problem builds and
solves, that the state machine never offers a method a problem cannot run, and
that the generated "copy as code" snippet is genuinely executable.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

pytest.importorskip("PySide6", reason="the app extra is not installed")

from PySide6.QtWidgets import QApplication  # noqa: E402

from odesuite_app import catalog, progress  # noqa: E402
from odesuite_app.solver import SolveRequest, SolveRunner  # noqa: E402
from odesuite_app.state import METHOD_GROUPS, SessionState, methods_for  # noqa: E402
from odesuite_app.theme import PALETTES, stylesheet  # noqa: E402

ALL_KEYS = catalog.keys()


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def small_params(entry) -> dict:
    """Parameters shrunk to whatever still exercises the code path.

    Chiefly for the spectral problems: 128 Fourier modes with an implicit
    method means a 128-column finite-difference Jacobian of FFT pairs and three
    complex 128x128 factorisations per step, which turns a smoke test into a
    ten-minute one. Thirty-two modes covers exactly the same code.
    """
    params = dict(entry.defaults())
    for name, cap in (("t_end", 2.0), ("n_orbits", 2.0),
                      ("log_t_end", 2.0), ("n_modes", 32)):
        if name in params:
            params[name] = min(params[name], cap)
    return params


# ---------------------------------------------------------------------------
# Catalogue
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", ALL_KEYS)
def test_entry_builds_at_its_defaults(key):
    entry = catalog.get(key)
    bench = entry.build(entry.defaults())
    problem = bench.problem
    f0 = problem.f(problem.t0, problem.y0)
    assert f0.shape == problem.y0.shape
    assert np.all(np.isfinite(f0))


@pytest.mark.parametrize("key", ALL_KEYS)
def test_entry_builds_at_parameter_extremes(key):
    """Slider endpoints must be safe -- a user will drag to both ends."""
    entry = catalog.get(key)
    for extreme in ("low", "high"):
        params = {p.name: getattr(p, extreme) for p in entry.params}
        bench = entry.build({**entry.defaults(), **params})
        assert bench.problem.n > 0, f"{key} failed at its {extreme} extremes"


@pytest.mark.parametrize("key", ALL_KEYS)
def test_entry_metadata_is_sane(key):
    entry = catalog.get(key)
    assert entry.title and entry.blurb and entry.tags
    assert entry.plot_kind in ("time", "phase", "orbit", "nbody", "spacetime")
    assert 0 < entry.default_rtol < 1
    for spec in entry.params:
        assert spec.low < spec.high, f"{key}.{spec.name} has an empty range"
        assert spec.low <= spec.default <= spec.high, (
            f"{key}.{spec.name} default {spec.default} is outside "
            f"[{spec.low}, {spec.high}]"
        )
        if spec.log:
            assert spec.low > 0, f"{key}.{spec.name} is log-scaled but allows <= 0"


@pytest.mark.parametrize("key", ALL_KEYS)
def test_default_method_actually_runs(key):
    """The default method must work on its own problem.

    Offering a default that raises on selection is the most annoying possible
    first impression, and it is entirely preventable.
    """
    from odesuite import solve

    entry = catalog.get(key)
    bench = entry.build(small_params(entry))
    kwargs = (
        {"n_steps": 400}
        if entry.default_method in ("verlet", "yoshida4", "yoshida6", "etdrk4")
        else {"rtol": 1e-6, "atol": 1e-9, "max_steps": 200_000}
    )
    sol = solve(bench.problem, method=entry.default_method, **kwargs)
    assert sol.success, f"{key} with {entry.default_method}: {sol.message}"


def test_tags_are_discoverable():
    tags = catalog.all_tags()
    assert "stiff" in tags and "classic" in tags
    for tag in tags:
        assert catalog.filter_by(tag), f"tag {tag!r} matches nothing"
    assert len(catalog.filter_by("all")) == len(ALL_KEYS)


def test_unknown_key_raises():
    with pytest.raises(KeyError, match="unknown problem"):
        catalog.get("not_a_problem")


# ---------------------------------------------------------------------------
# Method availability
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", ALL_KEYS)
def test_offered_methods_are_all_runnable(key):
    """Every method the picker offers must actually accept the problem.

    Symplectic methods need a separable system, ETDRK4 a semilinear splitting,
    and nothing explicit can take a mass matrix. The filter exists so those
    combinations are never presented, and this checks it is complete.
    """
    from odesuite import solve

    entry = catalog.get(key)
    bench = entry.build(small_params(entry))

    for group, names in methods_for(entry).items():
        for method in names:
            kwargs = (
                {"n_steps": 200}
                if method in ("verlet", "yoshida4", "yoshida6", "etdrk4")
                else {"rtol": 1e-4, "atol": 1e-7, "max_steps": 20_000}
            )
            try:
                solve(bench.problem, method=method, **kwargs)
            except Exception as exc:
                pytest.fail(
                    f"{key} offers {method!r} in group {group!r} but it raises: "
                    f"{type(exc).__name__}: {exc}"
                )


@pytest.mark.parametrize("key", ALL_KEYS)
@pytest.mark.slow
def test_taylor_offered_exactly_where_it_works(key):
    """`supports_taylor` must be neither optimistic nor needlessly cautious.

    Jet arithmetic cannot express every right-hand side -- Pleiades' zero-valued
    non-integer power, the spectral problems' FFTs, the separable Kepler form's
    object-array division all defeat it -- and being explicit in character, the
    method also stalls on stiff problems. Both halves are checked: where the
    flag is set the method must run, and where it is not, it must be for one of
    those reasons rather than an oversight.
    """
    from odesuite import solve

    entry = catalog.get(key)
    bench = entry.build(small_params(entry))

    try:
        sol = solve(bench.problem, method="taylor8", rtol=1e-5, atol=1e-8,
                    max_steps=20_000)
        works = sol.success
    except Exception:
        works = False

    if entry.supports_taylor:
        assert works, f"{key} claims Taylor support but the solve fails"
    else:
        stiff_only = "stiff" in entry.tags and "nonstiff" not in entry.tags
        assert not works or stiff_only, (
            f"{key} runs fine under Taylor but does not offer it — "
            f"set supports_taylor=True"
        )


def test_separable_methods_only_offered_for_separable_problems():
    for key in ALL_KEYS:
        entry = catalog.get(key)
        offered = {m for names in methods_for(entry).values() for m in names}
        if "separable" not in entry.tags:
            assert not offered & {"verlet", "yoshida4", "yoshida6"}, key
        if "semilinear" not in entry.tags:
            assert "etdrk4" not in offered, key
        if "dae" in entry.tags or "mass" in entry.tags:
            assert not offered & {"dopri5", "tsit5", "rk23"}, key


def test_every_group_method_exists_in_the_library():
    from odesuite.steppers import METHODS

    for names in METHOD_GROUPS.values():
        for name in names:
            assert name in METHODS, f"{name} is offered but not registered"


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------


def test_state_defaults_are_coherent(qapp):
    state = SessionState()
    assert state.problem_key in catalog.CATALOG
    assert state.method == state.entry.default_method
    assert state.rtol > state.atol


def test_switching_problem_resets_parameters(qapp):
    state = SessionState()
    state.set_problem("lorenz", resolve=False)
    state.set_param("rho", 40.0, resolve=False)
    assert state.params["rho"] == 40.0

    state.set_problem("kepler", resolve=False)
    assert "rho" not in state.params
    assert state.params == catalog.get("kepler").defaults()


def test_switching_problem_repairs_an_incompatible_method(qapp):
    """Choosing Verlet then switching to a non-separable problem must not
    leave the session in a state that cannot be solved."""
    state = SessionState()
    state.set_problem("kepler_symplectic", resolve=False)
    state.set_method("verlet", resolve=False)
    assert state.method == "verlet"

    state.set_problem("robertson", resolve=False)
    offered = {m for names in methods_for(state.entry).values() for m in names}
    assert state.method in offered
    assert state.method != "verlet"


def test_fixed_step_detection(qapp):
    state = SessionState()
    state.set_problem("kepler_symplectic", resolve=False)
    state.set_method("verlet", resolve=False)
    assert state.uses_fixed_step
    assert state.request().n_steps is not None

    state.set_problem("lorenz", resolve=False)
    assert not state.uses_fixed_step
    assert state.request().n_steps is None


def test_signals_fire_on_change(qapp):
    state = SessionState()
    seen = []
    state.problem_changed.connect(seen.append)
    state.set_problem("brusselator", resolve=False)
    assert seen == ["brusselator"]

    # Setting the same value again must not emit -- otherwise a slider that
    # snaps back to its current position triggers a redundant solve.
    seen.clear()
    state.set_problem("brusselator", resolve=False)
    assert seen == []


# ---------------------------------------------------------------------------
# Background solving
# ---------------------------------------------------------------------------


def test_runner_returns_a_result(qapp):
    runner = SolveRunner()
    received = []
    runner.finished.connect(received.append)
    runner.submit(
        SolveRequest(problem_key="logistic", method="dopri5", rtol=1e-8, atol=1e-10)
    )
    assert runner.wait(30_000)
    qapp.processEvents()

    assert len(received) == 1
    result = received[0]
    assert result.ok, result.status_text
    assert result.solution.y.shape[0] == 1
    assert result.wall_time > 0


def test_runner_reports_failure_without_raising(qapp):
    """A bad solve must surface as an error on the result, not an exception."""
    runner = SolveRunner()
    received = []
    runner.finished.connect(received.append)
    runner.submit(
        SolveRequest(problem_key="not_a_problem", method="dopri5", rtol=1e-8, atol=1e-10)
    )
    assert runner.wait(20_000)
    qapp.processEvents()

    assert len(received) == 1
    assert not received[0].ok
    assert "KeyError" in received[0].error


def test_only_the_newest_request_reaches_latest(qapp):
    """Dragging a slider queues many solves; only the last one may be shown."""
    runner = SolveRunner()
    latest, finished = [], []
    runner.latest.connect(latest.append)
    runner.finished.connect(finished.append)

    for t_end in (4.0, 6.0, 8.0):
        runner.submit(
            SolveRequest(
                problem_key="logistic", method="dopri5", rtol=1e-8, atol=1e-10,
                params={"t_end": t_end},
            )
        )
    assert runner.wait(30_000)
    qapp.processEvents()

    assert len(finished) == 3
    assert len(latest) == 1
    assert latest[0].request.params["t_end"] == 8.0


def test_step_sizes_are_recoverable(qapp):
    runner = SolveRunner()
    received = []
    runner.finished.connect(received.append)
    runner.submit(
        SolveRequest(problem_key="van_der_pol", method="dopri5", rtol=1e-7,
                     atol=1e-10, params={"mu": 5.0, "t_end": 20.0})
    )
    assert runner.wait(30_000)
    qapp.processEvents()

    midpoints, h = received[0].step_sizes()
    assert midpoints.size == h.size == received[0].solution.t.size - 1
    assert np.all(h > 0)
    # A relaxation oscillator must show real step-size variation, or the
    # timeline view would be showing nothing worth looking at.
    assert h.max() / h.min() > 10


def test_invariant_drift_available_where_expected(qapp):
    runner = SolveRunner()
    received = []
    runner.finished.connect(received.append)
    runner.submit(
        SolveRequest(problem_key="kepler", method="dopri5", rtol=1e-9, atol=1e-12,
                     params={"n_orbits": 2.0})
    )
    assert runner.wait(30_000)
    qapp.processEvents()

    t, drift = received[0].invariant_drift()
    assert t is not None and drift is not None
    assert drift.size == t.size
    assert drift[0] == pytest.approx(0.0, abs=1e-12)


# ---------------------------------------------------------------------------
# "Copy as code"
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", ["lorenz", "robertson", "kepler_symplectic"])
def test_generated_code_runs_and_reproduces_the_solve(key):
    """The snippet the app hands the user must actually work.

    A copy-to-clipboard button that emits code which does not run would be
    worse than no button, so the generated text is executed here.
    """
    entry = catalog.get(key)
    request = SolveRequest(
        problem_key=key,
        method=entry.default_method,
        rtol=1e-6,
        atol=1e-9,
        params={**entry.defaults(), **({"log_t_end": 3.0} if "log_t_end" in
                                       entry.defaults() else {}),
                **({"n_orbits": 2.0} if "n_orbits" in entry.defaults() else {})},
        n_steps=400 if entry.default_method in ("verlet", "etdrk4") else None,
    )
    code = request.as_code()
    assert "from odesuite import solve" in code
    assert entry.default_method in code

    namespace: dict = {}
    exec(compile(code, "<generated>", "exec"), namespace)   # noqa: S102
    assert "sol" in namespace
    assert namespace["sol"].success


# ---------------------------------------------------------------------------
# Theme and rendering
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["dark", "light"])
def test_stylesheet_is_complete(name):
    sheet = stylesheet(PALETTES[name])
    assert "QPushButton" in sheet and "QLabel" in sheet
    assert "{}" not in sheet, "an unformatted placeholder is left in the stylesheet"


def test_palettes_define_every_colour():
    for palette in PALETTES.values():
        for field, value in vars(palette).items():
            if field in ("name", "series"):
                continue
            assert isinstance(value, str) and value.startswith("#"), (
                f"{palette.name}.{field} is not a hex colour"
            )
        assert len(palette.series) >= 6


def test_window_builds_and_navigates(qapp):
    """A headless smoke test: construct the window and visit every screen."""
    from odesuite_app.app import SCREENS, MainWindow

    window = MainWindow("dark")
    window.resize(1280, 800)
    for key, _label, _shortcut in SCREENS:
        window.go(key)
        qapp.processEvents()
        assert window.stack.currentWidget() is window._screens[key]
        assert window.sidebar.buttons[key].isChecked(), (
            f"the sidebar did not follow the switch to {key!r}"
        )
    # Every screen is a real screen. Through the phased build of the Learning
    # Hub this was a set of allowed placeholders, shrinking by one each phase;
    # with the last of them replaced there is a stronger thing to assert, which
    # also catches a stand-in being introduced again later.
    stubs = {
        key for key, widget in window._screens.items()
        if not type(widget).__module__.startswith("odesuite_app.screens")
    }
    assert not stubs, f"these are stand-ins rather than screens: {sorted(stubs)}"
    window.deleteLater()


def test_home_screen_lists_every_problem(qapp):
    from odesuite_app.screens.home import HomeScreen

    screen = HomeScreen(PALETTES["dark"])
    assert set(screen._cards) == set(ALL_KEYS)

    screen._apply_filter("stiff")
    visible = [k for k, c in screen._cards.items() if c.isVisibleTo(screen)]
    assert set(visible) == {k for k in ALL_KEYS if "stiff" in catalog.get(k).tags}

    screen._apply_filter("all")
    assert all(c.isVisibleTo(screen) for c in screen._cards.values())
    screen.deleteLater()


# ---------------------------------------------------------------------------
# Cancelling superseded solves
# ---------------------------------------------------------------------------
#
# Discarding a result is not the same as not computing it. Before `solve` grew a
# callback, a superseded job ran to completion anyway, holding a pool thread for
# however long the problem takes purely to have its answer thrown away.
#
# Supersession is opt-in, and that is load-bearing rather than cautious: the
# Method Race submits one solve per method through this same runner and wants
# every one of them. A runner that treated "not the newest token" as "cancel"
# would silently have raced one method.


def test_supersede_is_off_by_default_so_concurrent_solves_all_survive(qapp):
    """The Method Race's requirement, pinned directly."""
    runner = SolveRunner()
    finished = []
    runner.finished.connect(finished.append)

    for method in ("rk23", "dopri5", "tsit5"):
        runner.submit(
            SolveRequest(problem_key="logistic", method=method, rtol=1e-8,
                         atol=1e-10, dense_output=False)
        )
    assert runner.wait(30_000)
    qapp.processEvents()

    assert len(finished) == 3, "concurrent solves must not cancel one another"
    assert all(not result.cancelled for result in finished)
    assert {r.request.method for r in finished} == {"rk23", "dopri5", "tsit5"}


def test_a_superseded_solve_stops_early(qapp):
    """A slider drag: several superseding submissions, only the last wanted."""
    runner = SolveRunner(max_threads=1)      # force them to queue, so the
    finished, latest = [], []                # earlier ones are stale on arrival
    runner.finished.connect(finished.append)
    runner.latest.connect(latest.append)

    for log_t_end in (9.0, 10.0, 11.0):
        runner.submit(
            SolveRequest(problem_key="robertson", method="radau", rtol=1e-8,
                         atol=1e-10, params={"log_t_end": log_t_end},
                         dense_output=False),
            supersede=True,
        )
    assert runner.wait(60_000)
    qapp.processEvents()

    assert len(latest) == 1
    assert latest[0].request.params["log_t_end"] == 11.0
    assert not latest[0].cancelled
    # The superseded ones were stopped, so they never reached a consumer.
    assert len(finished) == 1, f"{len(finished)} results emitted; expected only the newest"


def test_cancel_all_stops_everything_in_flight(qapp):
    """For screen teardown: leaving a screen mid-solve should not leave the pool
    computing an answer nobody will read."""
    runner = SolveRunner(max_threads=1)
    finished = []
    runner.finished.connect(finished.append)

    for _ in range(3):
        runner.submit(
            SolveRequest(problem_key="robertson", method="radau", rtol=1e-10,
                         atol=1e-12, params={"log_t_end": 11.0}, dense_output=False)
        )
    runner.cancel_all()
    assert runner.wait(60_000)
    qapp.processEvents()

    assert finished == [], "cancel_all should suppress every pending result"


def test_the_single_solve_path_supersedes(qapp):
    """`SessionState.resolve` is what every slider drives, so it must opt in --
    otherwise the hook exists and nothing uses it."""
    import inspect

    from odesuite_app.state import SessionState

    source = inspect.getsource(SessionState.resolve)
    assert "supersede=True" in source


# ---------------------------------------------------------------------------
# The shared control-panel scaffolding
# ---------------------------------------------------------------------------
#
# All five screens opened `_build_controls` with the same seventeen lines of Qt
# scaffolding and closed it with the same five, and repeated a three-line
# heading idiom twenty-one times between them. Both are now helpers in
# `widgets/controls.py`.
#
# The refactor was gated on 42 offscreen renders -- every screen, both palettes,
# whole and per-panel -- hashing pixel-identically. These tests keep the helpers
# honest afterwards.


def test_control_panel_builds_a_themed_scrolling_column(qapp):
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout

    from odesuite_app.widgets.controls import control_panel

    panel, layout = control_panel(250)

    assert isinstance(panel, QFrame)
    assert panel.property("role") == "panel", "the theme styles on this property"
    assert panel.width() == 250
    assert isinstance(layout, QVBoxLayout)

    scrolls = panel.findChildren(QScrollArea)
    assert len(scrolls) == 1
    scroll = scrolls[0]
    assert scroll.widgetResizable()
    # A control column scrolls vertically only; a horizontal bar here would mean
    # a control is too wide, which is a thing to fix rather than to scroll to.
    assert scroll.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff


def test_control_panel_width_is_the_callers_choice(qapp):
    """The five screens use 238 to 258 px. That looks like drift rather than
    design, but unifying it would change the layout, which is not what
    extracting boilerplate is for."""
    from odesuite_app.widgets.controls import control_panel

    assert control_panel(238)[0].width() == 238
    assert control_panel(258)[0].width() == 258


def test_widgets_added_to_the_returned_layout_land_inside_the_panel(qapp):
    from PySide6.QtWidgets import QLabel

    from odesuite_app.widgets.controls import control_panel

    panel, layout = control_panel(250)
    label = QLabel("inside")
    layout.addWidget(label)

    assert label in panel.findChildren(QLabel)


def test_add_heading_marks_the_label_for_the_theme(qapp):
    from PySide6.QtWidgets import QLabel

    from odesuite_app.widgets.controls import add_heading, control_panel

    panel, layout = control_panel(250)
    heading = add_heading(layout, "Problem")

    assert isinstance(heading, QLabel)
    assert heading.text() == "Problem"
    assert heading.property("role") == "heading"
    assert heading in panel.findChildren(QLabel)


def test_add_heading_can_leave_room_above_itself(qapp):
    from odesuite_app.widgets.controls import add_heading, control_panel

    _, plain = control_panel(250)
    add_heading(plain, "First")
    assert plain.count() == 1

    _, spaced = control_panel(250)
    add_heading(spaced, "First", space_above=6)
    assert spaced.count() == 2, "the spacer is an item in its own right"


def _build_controls_bodies():
    """Source of every screen's `_build_controls`, keyed by file."""
    import ast
    import glob

    newline = chr(10)
    bodies = {}
    for path in sorted(glob.glob("src/odesuite_app/screens/*.py")):
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        for node in ast.walk(ast.parse(newline.join(lines))):
            if isinstance(node, ast.FunctionDef) and node.name == "_build_controls":
                bodies[path] = newline.join(lines[node.lineno - 1: node.end_lineno])
    return bodies


def test_no_screen_rebuilds_the_scrolling_column_by_hand():
    """Finding #27, pinned.

    Scoped to `_build_controls` rather than to whole files, and checked on
    `QScrollArea` rather than on the panel role, because both broader versions
    are wrong: screens legitimately build other `role="panel"` frames for the
    plot area and the results summary, and the home screen legitimately scrolls
    its whole gallery. The duplicated thing was specifically the scrolling
    control column, and `control_panel` is now the only place one is built.
    """
    offenders = [
        path for path, body in _build_controls_bodies().items()
        if "QScrollArea(" in body
    ]
    assert not offenders, (
        "these screens build a scrolling control column by hand instead of "
        f"using control_panel(): {offenders}"
    )


def test_every_screen_with_a_control_column_uses_the_shared_one():
    """The other half: the helper is adopted, not merely available."""
    bodies = _build_controls_bodies()
    # A floor rather than an exact count: screens are still being added, and the
    # invariant is that each one uses the shared helper, not how many there are.
    # The floor is only here so a glob that silently matches nothing cannot make
    # this pass vacuously.
    assert len(bodies) >= 5, f"only found {len(bodies)} control columns"
    for path, body in bodies.items():
        assert "control_panel(" in body, f"{path} builds its control column by hand"


# ---------------------------------------------------------------------------
# Remembering where you were
# ---------------------------------------------------------------------------


@pytest.fixture()
def scratch_settings(tmp_path, monkeypatch):
    """Point QSettings at a scratch file rather than the real registry.

    A test that wrote the developer's own window position would be a test with
    a side effect on the machine it ran on.
    """
    from PySide6.QtCore import QSettings

    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))
    monkeypatch.setattr(
        "odesuite_app.app.QSettings",
        lambda *a, **k: QSettings(QSettings.IniFormat, QSettings.UserScope,
                                  "odesuite-test", "odesuite-test"),
    )
    yield tmp_path


def test_the_screen_you_were_on_is_remembered(qapp, scratch_settings):
    """Reopening on Home every time is a small tax paid constantly."""
    from odesuite_app.app import MainWindow

    first = MainWindow()
    first.go("quiz")
    assert first.current_screen() == "quiz"
    first.close()

    second = MainWindow()
    assert second.remembered_screen() == "quiz"
    first.deleteLater()
    second.deleteLater()


def test_an_unknown_remembered_screen_is_ignored(qapp, scratch_settings):
    """A screen key can disappear between versions, and a saved name that no
    longer exists must not open nothing."""
    from odesuite_app.app import MainWindow

    window = MainWindow()
    window._settings.setValue("window/screen", "a-screen-that-went-away")
    assert window.remembered_screen() == ""
    window.deleteLater()


def test_the_window_geometry_is_saved_and_restored(qapp, scratch_settings):
    """Asserted at the settings level rather than by comparing sizes.

    Under the offscreen platform `restoreGeometry` clamps to the minimum size
    for a window that was never really shown, so comparing widths would be a
    test of Qt on this platform rather than of anything here. What this code
    is responsible for is storing the geometry on close and handing it back to
    `restoreGeometry` on open, and that is what is checked.
    """
    from odesuite_app.app import MainWindow

    first = MainWindow()
    first.resize(1200, 780)
    first.close()
    saved = first._settings.value("window/geometry")
    assert saved, "nothing was stored on close"

    second = MainWindow()
    assert second._settings.value("window/geometry") == saved
    first.deleteLater()
    second.deleteLater()


def test_geometry_is_not_kept_in_the_progress_file(qapp, scratch_settings):
    """Preference, not achievement. A geometry has no business in a file the
    user may export to a machine with a different screen."""
    from odesuite_app.app import MainWindow

    window = MainWindow()
    window.resize(1100, 700)
    window.close()

    text = json.dumps(progress.load(), default=str)
    assert "geometry" not in text
    assert "1100" not in text
    window.deleteLater()
