"""The Phase Portrait screen."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6", reason="the app extra is not installed")

from PySide6.QtCore import QThreadPool  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from odesuite_app import catalog  # noqa: E402
from odesuite_app.state import SessionState  # noqa: E402
from odesuite_app.theme import PALETTES  # noqa: E402

PALETTE = PALETTES["dark"]


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def screen(qapp):
    from odesuite_app.screens.portrait import PortraitScreen

    state = SessionState()
    view = PortraitScreen(state, PALETTE)
    _settle(qapp)
    yield view
    view.deleteLater()


def _settle(qapp, timeout: int = 120_000) -> None:
    """Let the background analysis land."""
    QThreadPool.globalInstance().waitForDone(timeout)
    for _ in range(20):
        qapp.processEvents()


def _select(screen, key: str, qapp, **params) -> None:
    index = screen.picker.findData(key)
    assert index >= 0, f"{key} is not offered on the portrait screen"
    screen.picker.setCurrentIndex(index)
    screen._on_problem_picked(index)
    for name, value in params.items():
        screen._params[name] = value
    if params:
        screen._recompute(reset_window=True)
    _settle(qapp)


# ---------------------------------------------------------------------------
# Which systems are offered
# ---------------------------------------------------------------------------


def test_only_planar_autonomous_systems_are_offered(screen):
    offered = {screen.picker.itemData(i) for i in range(screen.picker.count())}
    assert offered, "no systems offered"
    for key in offered:
        entry = catalog.get(key)
        assert entry.autonomous_2d, f"{key} has no planar phase portrait"
    # Anything higher-dimensional must be absent.
    for key in ("lorenz", "robertson", "pleiades", "kuramoto_sivashinsky"):
        assert key not in offered


def test_falls_back_when_the_session_problem_has_no_portrait(qapp):
    """Opening the screen from a 3-D problem must not leave it blank."""
    from odesuite_app.screens.portrait import PortraitScreen

    state = SessionState()
    state.set_problem("lorenz", resolve=False)
    view = PortraitScreen(state, PALETTE)
    _settle(qapp)

    assert view.picker.currentData() is not None
    assert catalog.get(view.picker.currentData()).autonomous_2d
    view.deleteLater()


# ---------------------------------------------------------------------------
# The analysis reaching the screen
# ---------------------------------------------------------------------------


def test_pendulum_portrait_reports_its_equilibria(screen, qapp):
    _select(screen, "pendulum", qapp)

    assert screen._data is not None
    kinds = sorted(p.kind for p in screen._data.fixed_points)
    assert "saddle" in kinds
    assert "centre" in kinds
    assert screen._data.separatrices, "the saddles should have manifolds"

    report = screen.report.text()
    assert "saddle" in report and "λ" in report


@pytest.mark.slow
def test_damped_pendulum_turns_centres_into_spirals(screen, qapp):
    _select(screen, "pendulum", qapp, damping=0.4)
    kinds = {p.kind for p in screen._data.fixed_points}
    assert "stable spiral" in kinds
    assert "centre" not in kinds


@pytest.mark.slow
def test_duffing_bifurcation_is_visible_through_the_parameter(screen, qapp):
    """Sliding alpha through zero must actually change the portrait.

    Three equilibria below, one above. This is the payoff of recomputing the
    whole analysis on a parameter change rather than only the trajectories.
    """
    _select(screen, "duffing", qapp, alpha=-1.0)
    assert len(screen._data.fixed_points) == 3

    screen._on_param("alpha", 1.0)
    _settle(qapp)
    assert len(screen._data.fixed_points) == 1
    assert screen._data.fixed_points[0].kind == "stable spiral"


def test_window_frames_all_the_equilibria(screen, qapp):
    _select(screen, "duffing", qapp, alpha=-1.0, delta=0.25)
    xlim, ylim = screen._data.xlim, screen._data.ylim
    for point in screen._data.fixed_points:
        assert xlim[0] <= point.position[0] <= xlim[1]
        assert ylim[0] <= point.position[1] <= ylim[1]


# ---------------------------------------------------------------------------
# Layers
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_layer_toggles_change_what_is_computed(screen, qapp):
    _select(screen, "pendulum", qapp)
    assert screen._data.streamlines

    screen.toggles["field"].setChecked(False)
    screen._recompute(reset_window=False)
    _settle(qapp)
    assert screen._data.streamlines == []

    screen.toggles["field"].setChecked(True)
    screen._recompute(reset_window=False)
    _settle(qapp)
    assert screen._data.streamlines


def test_streamlines_are_real_polylines(screen, qapp):
    """Guards a silent extraction failure.

    The streamline geometry comes out of matplotlib in one of two shapes, and
    an earlier version read only segment endpoints -- which produced an empty
    list whenever they arrived as whole polylines, leaving the field invisible
    with no error anywhere.
    """
    _select(screen, "pendulum", qapp)
    paths = screen._data.streamlines
    assert len(paths) > 10, f"only {len(paths)} streamlines extracted"
    assert all(path.ndim == 2 and path.shape[1] == 2 for path in paths)
    assert all(len(path) > 2 for path in paths)
    assert max(len(path) for path in paths) > 20, "all streamlines are stubs"


# ---------------------------------------------------------------------------
# Interaction
# ---------------------------------------------------------------------------


def test_clicking_launches_a_trajectory(screen, qapp):
    _select(screen, "pendulum", qapp)
    before = len(screen._trajectories)

    screen._launch(0.0, 1.0)
    assert len(screen._trajectories) > before
    assert screen._launched == 1
    assert "trajectory through" in screen.status.text()

    screen._clear_trajectories()
    assert screen._trajectories == []
    assert screen._launched == 0


def test_launched_trajectories_stay_inside_the_window(screen, qapp):
    """Otherwise a divergent orbit rescales the plot and hides everything."""
    _select(screen, "duffing", qapp, alpha=-1.0)
    xlim, ylim = screen._data.xlim, screen._data.ylim

    screen._launch(1.8, 0.9)
    for item in screen._trajectories:
        x, y = item.getData()
        if x is None or len(x) == 0:
            continue
        # Boundary crossings are interpolated, so nothing should escape at all
        # beyond floating-point slack.
        tol = 1e-9 * max(xlim[1] - xlim[0], ylim[1] - ylim[0])
        assert x.min() >= xlim[0] - tol and x.max() <= xlim[1] + tol
        assert y.min() >= ylim[0] - tol and y.max() <= ylim[1] + tol


def test_launched_trajectories_avoid_the_manifold_colours(screen, qapp):
    """A user's trajectory must not read as part of the computed skeleton."""
    _select(screen, "pendulum", qapp)
    for _ in range(5):
        screen._launch(0.0, 0.5)

    reserved = {PALETTE.success.lower(), PALETTE.danger.lower()}
    for item in screen._trajectories:
        pen = item.opts.get("pen")
        if pen is None or not hasattr(pen, "color"):
            continue
        assert pen.color().name().lower() not in reserved


def test_switching_system_clears_the_previous_trajectories(screen, qapp):
    _select(screen, "pendulum", qapp)
    screen._launch(0.0, 1.0)
    assert screen._launched == 1

    _select(screen, "duffing", qapp)
    assert screen._launched == 0
    assert screen._trajectories == []


def test_render_is_safe_before_any_analysis(qapp):
    from odesuite_app.screens.portrait import PortraitScreen

    state = SessionState()
    view = PortraitScreen(state, PALETTE)
    view._data = None
    view._render()          # must not raise
    view._write_report()
    assert view.report.text() in ("—", "<i>no equilibria in this window</i>")
    view.deleteLater()


def test_stale_analysis_results_are_discarded(screen, qapp):
    """Dragging a slider queues several analyses; only the newest may land."""
    _select(screen, "duffing", qapp, alpha=-1.0)

    screen._token = 99
    stale = object()
    screen._on_analysis(stale, 98)
    assert screen._data is not stale


# ---------------------------------------------------------------------------
# The bifurcation tab
# ---------------------------------------------------------------------------


def _draw_diagram(screen, qapp, parameter: str) -> None:
    index = screen.sweep_param.findData(parameter)
    assert index >= 0, f"{parameter} is not offered as a sweep"
    screen.sweep_param.setCurrentIndex(index)
    screen._draw_diagram()
    _settle(qapp)


def test_the_bifurcation_tab_exists_beside_the_portrait(screen):
    assert [screen.views.tabText(i) for i in range(screen.views.count())] == [
        "Portrait", "Bifurcation",
    ]


def test_duration_is_not_offered_as_a_sweep(screen, qapp):
    """A diagram over `t_end` is a set of flat lines: a true picture of nothing."""
    _select(screen, "brusselator", qapp)
    offered = {screen.sweep_param.itemData(i) for i in range(screen.sweep_param.count())}
    assert "a" in offered and "b" in offered
    assert "t_end" not in offered


def test_the_brusselator_sweep_finds_its_hopf(screen, qapp):
    _select(screen, "brusselator", qapp)
    _draw_diagram(screen, qapp, "b")

    diagram = screen._diagram
    assert diagram is not None
    hopfs = [f for f in diagram.bifurcations if f.kind == "Hopf"]
    assert len(hopfs) == 1
    assert hopfs[0].parameter == pytest.approx(2.0, rel=0.01)


def test_the_diagram_note_names_the_bifurcation_it_found(screen, qapp):
    _select(screen, "brusselator", qapp)
    _draw_diagram(screen, qapp, "b")

    note = screen.sweep_note.text()
    assert "Hopf" in note
    assert "turn back" in note, "the method's limitation is stated on screen"


def test_stable_and_unstable_stretches_are_drawn_differently(screen, qapp):
    """Dash pattern, not only colour -- the same rule the separatrices follow."""
    from PySide6.QtCore import Qt

    _select(screen, "brusselator", qapp)
    _draw_diagram(screen, qapp, "b")

    styles = {
        item.opts["pen"].style()
        for item in screen.sweep_plot.listDataItems()
        if item.opts.get("pen") is not None
    }
    assert Qt.DashLine in styles
    assert Qt.SolidLine in styles


def test_the_duffing_sweep_draws_three_branches(screen, qapp):
    _select(screen, "duffing", qapp)
    _draw_diagram(screen, qapp, "alpha")

    assert len(screen._diagram.branches) == 3
    assert [f.kind for f in screen._diagram.bifurcations] == ["pitchfork"]


def test_switching_system_drops_the_previous_diagram(screen, qapp):
    _select(screen, "brusselator", qapp)
    _draw_diagram(screen, qapp, "b")
    assert screen._diagram is not None

    _select(screen, "duffing", qapp)
    assert screen._diagram is None
    assert not screen.sweep_plot.listDataItems()


def test_a_stale_sweep_result_is_discarded(screen, qapp):
    _select(screen, "brusselator", qapp)
    screen._diagram_token = 7
    screen._on_diagram(object(), 3)
    assert screen._diagram is None


def test_a_failed_sweep_is_reported_rather_than_raised(screen, qapp):
    _select(screen, "brusselator", qapp)
    screen._on_diagram(ValueError("no"), screen._diagram_token)

    assert screen._diagram is None
    assert "sweep failed" in screen.sweep_note.text()
    assert screen.sweep_button.isEnabled()


def test_a_system_with_nothing_to_sweep_says_so(screen, qapp):
    """Not a silent empty tab: the reason is on screen."""
    entry = next(
        (catalog.get(key) for key in catalog.keys()
         if catalog.get(key).autonomous_2d
         and not [s for s in catalog.get(key).params
                  if s.name not in screen._NOT_WORTH_SWEEPING]),
        None,
    )
    if entry is None:
        pytest.skip("every planar system here has a parameter worth sweeping")

    _select(screen, entry.key, qapp)
    assert not screen.sweep_button.isEnabled()
    assert "no parameter" in screen.sweep_note.text()


def test_the_two_manifolds_differ_in_pattern_not_only_colour(screen, qapp):
    """A11Y-03: stable solid, unstable dash-dot, and neither the nullclines' dash."""
    from PySide6.QtCore import Qt

    _select(screen, "pendulum", qapp)
    assert screen._data.separatrices
    manifold_colours = {PALETTE.danger.lower(), PALETTE.success.lower()}
    styles = {
        item.opts["pen"].style()
        for item in screen.plot.listDataItems()
        if item.opts.get("pen") is not None
        and item.opts["pen"].color().name().lower() in manifold_colours
    }
    assert styles == {Qt.SolidLine, Qt.DashDotLine}
    legend = screen.legend_label.text()
    assert "-·-" in legend and "unstable manifold" in legend


# ---------------------------------------------------------------------------
# The limit cycle, drawn
# ---------------------------------------------------------------------------


def test_van_der_pol_shows_its_limit_cycle_and_period(screen, qapp):
    """DYN-02 found the cycle and nothing drew it. The orbit is on the plot
    and the period is in the report."""
    _select(screen, "van_der_pol", qapp)

    assert screen._cycle is not None and screen._cycle.isolated
    assert len(screen._cycle_items) == 1
    text = screen.report.text()
    assert "period 6.66" in text and "attracting limit cycle" in text
    assert "limit cycle" in screen.plot.accessibleDescription()


def test_a_centre_orbit_is_drawn_dotted_and_not_called_a_limit_cycle(screen, qapp):
    from PySide6.QtCore import Qt

    _select(screen, "lotka_volterra", qapp)

    assert screen._cycle is not None and not screen._cycle.isolated
    pen = screen._cycle_items[0].opts["pen"]
    assert pen.style() == Qt.DotLine
    assert "not an isolated one" in screen.report.text()


def test_no_cycle_is_reported_with_its_reason(screen, qapp):
    _select(screen, "duffing", qapp)

    assert screen._cycle_items == []
    assert "No limit cycle" in screen.report.text()
    assert "equilibrium" in screen.report.text()


def test_the_cycle_layer_can_be_switched_off(screen, qapp):
    _select(screen, "van_der_pol", qapp)
    screen.toggles["cycle"].setChecked(False)
    _settle(qapp)

    assert screen._cycle_items == []
    assert "period" not in screen.report.text()

    screen.toggles["cycle"].setChecked(True)
    _settle(qapp)
    assert len(screen._cycle_items) == 1


def test_a_late_cycle_does_not_wipe_clicked_trajectories(screen, qapp):
    """The cycle arrives after the portrait. Drawing it must not re-render,
    which clears the trajectories the user launched in the meantime."""
    _select(screen, "van_der_pol", qapp)
    screen._launch(0.5, 0.5)
    drawn = len(screen._trajectories)
    assert drawn > 0

    screen._on_cycle(screen._cycle, screen._token)
    assert len(screen._trajectories) == drawn
