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
