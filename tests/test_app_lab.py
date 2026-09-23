"""The Solver Lab screen and the widgets it is built from."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("PySide6", reason="the app extra is not installed")

from PySide6.QtWidgets import QApplication  # noqa: E402

from odesuite_app import catalog  # noqa: E402
from odesuite_app.state import SessionState  # noqa: E402
from odesuite_app.theme import PALETTES  # noqa: E402
from odesuite_app.widgets.controls import ValueSlider, format_value  # noqa: E402

PALETTE = PALETTES["dark"]


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture
def solved(qapp):
    """A completed solve for a problem with interesting step-size structure."""
    state = SessionState()
    state.set_problem("van_der_pol", resolve=False)
    state.set_method("dopri5", resolve=False)
    state.set_param("mu", 20.0, resolve=False)
    state.set_param("t_end", 60.0, resolve=False)
    state.resolve()
    assert state.runner.wait(60_000)
    qapp.processEvents()
    assert state.result is not None and state.result.ok, "fixture solve failed"
    return state


# ---------------------------------------------------------------------------
# Sliders
# ---------------------------------------------------------------------------


def test_linear_slider_round_trips(qapp):
    slider = ValueSlider("x", 0.0, 10.0, 5.0)
    for value in (0.0, 2.5, 5.0, 9.99, 10.0):
        slider.set_value(value)
        assert slider.value() == pytest.approx(value, abs=0.02)


def test_log_slider_round_trips_across_decades(qapp):
    """A logarithmic slider must be as precise at 1e-13 as at 1e-2."""
    slider = ValueSlider("tol", 1e-13, 1e-2, 1e-8, log=True)
    for value in (1e-13, 1e-10, 1e-8, 1e-5, 1e-2):
        slider.set_value(value)
        assert slider.value() == pytest.approx(value, rel=0.05)


def test_log_slider_spends_travel_evenly_across_decades(qapp):
    """The reason for log scaling: each decade gets equal slider travel.

    On a linear slider over [0.1, 1000], everything below mu = 10 -- the entire
    non-stiff regime of Van der Pol -- would occupy under 1% of the range.
    """
    slider = ValueSlider("mu", 0.1, 1000.0, 1.0, log=True)
    slider.set_value(1.0)
    quarter = slider.slider.value()
    slider.set_value(10.0)
    half = slider.slider.value()
    slider.set_value(100.0)
    three_quarters = slider.slider.value()

    assert (half - quarter) == pytest.approx(three_quarters - half, rel=0.02)


def test_log_slider_rejects_a_nonpositive_lower_bound(qapp):
    with pytest.raises(ValueError, match="positive lower bound"):
        ValueSlider("bad", 0.0, 10.0, 1.0, log=True)


def test_slider_debounces_a_drag(qapp):
    """Dragging must produce many previews but only one committed value.

    Otherwise a single drag queues a solve per pixel to display the last one.
    """
    slider = ValueSlider("x", 0.0, 100.0, 50.0)
    previews, commits = [], []
    slider.preview.connect(previews.append)
    slider.committed.connect(commits.append)

    start = slider.slider.value()
    for tick in range(start + 1, start + 61):
        slider.slider.setValue(tick)
    qapp.processEvents()

    assert len(previews) == 60, "the readout should track every movement"
    assert commits == [], "no solve should be triggered mid-drag"


@pytest.mark.parametrize(
    "value,expected",
    [(0, "0"), (1234.5, "1234.5"), (0.5, "0.5"), (1e-9, "1e-09"), (2.5e6, "2.5e+06")],
)
def test_value_formatting(value, expected):
    assert format_value(value) == expected


# ---------------------------------------------------------------------------
# The screen
# ---------------------------------------------------------------------------


def test_lab_builds_and_shows_a_solution(solved):
    from odesuite_app.screens.lab import LabScreen

    lab = LabScreen(solved, PALETTE)
    lab._on_result(solved.result)

    assert lab.stats.rows["nfev"].value.text() != "—"
    assert lab.plot._curves, "no curve was drawn"
    assert lab.timeline.caption.text()
    lab.deleteLater()


def test_controls_follow_a_problem_change(solved):
    from odesuite_app.screens.lab import LabScreen

    lab = LabScreen(solved, PALETTE)
    assert set(lab.parameters._sliders) == {"mu", "t_end"}

    solved.set_problem("lorenz", resolve=False)
    lab.sync()
    assert set(lab.parameters._sliders) == {"sigma", "rho", "beta", "t_end"}
    assert lab.blurb.text() == catalog.get("lorenz").blurb
    lab.deleteLater()


def test_tolerance_controls_swap_for_fixed_step_methods(solved):
    """A constant-step method must not be shown a tolerance slider."""
    from odesuite_app.screens.lab import LabScreen

    solved.set_problem("kepler_symplectic", resolve=False)
    lab = LabScreen(solved, PALETTE)
    solved.set_method("verlet", resolve=False)
    lab._sync_method_dependent()

    assert lab.tolerances.steps.isVisibleTo(lab.tolerances)
    assert not lab.tolerances.rtol.isVisibleTo(lab.tolerances)
    assert "constant step size" in lab.method_note.text()

    solved.set_method("dopri5", resolve=False)
    lab._sync_method_dependent()
    assert lab.tolerances.rtol.isVisibleTo(lab.tolerances)
    assert not lab.tolerances.steps.isVisibleTo(lab.tolerances)
    lab.deleteLater()


def test_method_picker_headings_are_not_selectable(solved):
    """Group labels are structure, not choices."""
    from odesuite_app.screens.lab import LabScreen

    lab = LabScreen(solved, PALETTE)
    model = lab.method_picker._model
    headings = [
        model.item(row) for row in range(model.rowCount())
        if not model.item(row).data(0x0100)     # Qt.UserRole
    ]
    assert headings, "expected at least one group heading"
    for item in headings:
        assert not item.isEnabled()
    lab.deleteLater()


def test_copy_as_code_puts_runnable_code_on_the_clipboard(solved, qapp):
    from odesuite_app.screens.lab import LabScreen

    lab = LabScreen(solved, PALETTE)
    lab._copy_code()
    code = qapp.clipboard().text()

    assert "from odesuite import solve" in code
    namespace: dict = {}
    exec(compile(code, "<clipboard>", "exec"), namespace)   # noqa: S102
    assert namespace["sol"].success
    lab.deleteLater()


def test_csv_export_writes_every_component(solved, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QFileDialog

    from odesuite_app.screens.lab import LabScreen

    target = tmp_path / "solution.csv"
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName", staticmethod(lambda *a, **k: (str(target), ""))
    )
    lab = LabScreen(solved, PALETTE)
    lab._export_csv()

    assert target.exists()
    rows = target.read_text().strip().splitlines()
    assert rows[0].startswith("t,")
    solution = solved.result.solution
    assert len(rows) == solution.t.size + 1
    assert len(rows[0].split(",")) == solution.y.shape[0] + 1
    lab.deleteLater()


# ---------------------------------------------------------------------------
# Plot and timeline
# ---------------------------------------------------------------------------


def test_dense_sampling_includes_the_solver_step_points(solved):
    """The plotting grid must be at least as fine as the solver's own.

    Uniform sampling alone cuts chords across the fast jumps of a relaxation
    oscillator, because those jumps occupy a tiny slice of the time axis.
    """
    from odesuite_app.widgets.plotpanel import PlotPanel

    panel = PlotPanel(PALETTE)
    solution = solved.result.solution
    grid, values = panel._dense(solution)

    assert grid.size >= solution.t.size
    assert values.shape[1] == grid.size
    interior = solution.t[1:-1]
    assert np.all(np.isin(interior, grid)), "step points are missing from the grid"
    panel.deleteLater()


def test_log_time_defaults_per_problem_but_stays_overridable(solved, qapp):
    """Robertson spans eleven decades and defaults to log; Van der Pol does not.

    And the default must be applied once per problem, not re-derived on every
    redraw -- otherwise the checkbox cannot be switched off.
    """
    from odesuite_app.widgets.plotpanel import PlotPanel

    panel = PlotPanel(PALETTE)
    panel.update_from(solved.result, "Auto")
    assert not panel.log_time.isChecked(), "Van der Pol should use a linear axis"

    solved.set_problem("robertson", resolve=False)
    solved.set_method("radau", resolve=False)
    solved.resolve()
    assert solved.runner.wait(120_000)
    qapp.processEvents()

    panel.update_from(solved.result, "Auto")
    assert panel.log_time.isChecked(), "Robertson should default to a log axis"

    # The user overrides it; a redraw of the same problem must respect that.
    panel.log_time.setChecked(False)
    panel.update_from(solved.result, "Auto")
    assert not panel.log_time.isChecked(), "the override was discarded"
    panel.deleteLater()


def test_timeline_reports_the_step_spread(solved):
    from odesuite_app.widgets.steptimeline import StepTimeline

    timeline = StepTimeline(PALETTE)
    timeline.update_from(solved.result)

    caption = timeline.caption.text()
    assert "spread" in caption
    _, h = solved.result.step_sizes()
    assert h.max() / h.min() > 5, "this problem should show real step variation"
    timeline.deleteLater()


def test_timeline_labels_a_fixed_step_method_as_constant(qapp):
    """A flat line must be explained, not left looking like a measurement."""
    from odesuite_app.widgets.steptimeline import StepTimeline

    state = SessionState()
    state.set_problem("harmonic_2d", resolve=False)
    state.set_method("verlet", resolve=False)
    state.set_n_steps(500, resolve=False)
    state.resolve()
    assert state.runner.wait(60_000)
    qapp.processEvents()

    timeline = StepTimeline(PALETTE)
    timeline.update_from(state.result)
    assert "constant h" in timeline.caption.text()
    timeline.deleteLater()


def test_stats_panel_flags_a_high_rejection_rate(solved):
    from odesuite_app.widgets.stats import StatsPanel

    panel = StatsPanel(PALETTE)
    panel.update_from(solved.result)
    assert panel.rows["steps"].value.text() != "—"
    assert panel.rows["nfev"].value.text() != "—"

    panel.clear("solving…")
    assert panel.rows["nfev"].value.text() == "—"
    panel.deleteLater()


def test_spacetime_problems_render_as_an_image(qapp):
    from odesuite_app.widgets.plotpanel import PlotPanel

    state = SessionState()
    state.set_problem("allen_cahn", resolve=False)
    state.set_method("etdrk4", resolve=False)
    state.set_param("n_modes", 32, resolve=False)
    state.set_param("t_end", 5.0, resolve=False)
    state.set_n_steps(400, resolve=False)
    state.resolve()
    assert state.runner.wait(120_000)
    qapp.processEvents()
    assert state.result.ok, state.result.status_text

    panel = PlotPanel(PALETTE)
    panel.update_from(state.result, "Auto")
    assert panel._image is not None, "spacetime problems should draw an image"
    panel.deleteLater()


# ---------------------------------------------------------------------------
# Display toggles: per-component chips, and collapsing the work panel
# ---------------------------------------------------------------------------


def _lab(qapp, state):
    from odesuite_app.screens.lab import LabScreen

    screen = LabScreen(state, PALETTE)
    screen.resize(1400, 860)
    screen.show()
    qapp.processEvents()
    return screen


def _resolve(qapp, state):
    state.resolve()
    assert state.runner.wait(120_000)
    qapp.processEvents()


def _items(panel, index):
    return panel._series.get(index, [])


def _shown(panel, index):
    items = _items(panel, index)
    return bool(items) and all(item.isVisible() for item in items)


def test_a_chip_appears_for_every_component(solved, qapp):
    lab = _lab(qapp, solved)
    lab.plot.view.setCurrentText("Components")
    qapp.processEvents()

    labels = [chip.label for chip in lab.plot._chips]
    assert labels == list(solved.entry.labels)
    assert lab.plot.components.isVisible()
    lab.deleteLater()


def test_hiding_a_component_takes_its_step_points_with_it(solved, qapp):
    """A curve hidden while its markers stay would leave a trail of dots."""
    lab = _lab(qapp, solved)
    lab.plot.view.setCurrentText("Components")
    qapp.processEvents()
    panel = lab.plot

    assert panel.show_steps.isChecked()
    assert len(_items(panel, 0)) >= 2, "expected a curve and its markers"
    assert all(_shown(panel, i) for i in panel._series)

    panel._chips[0].setChecked(False)
    qapp.processEvents()

    assert not any(item.isVisible() for item in _items(panel, 0))
    assert _shown(panel, 1), "the other component must be untouched"
    assert panel.hidden_components() == {0}
    lab.deleteLater()


def test_hiding_a_component_does_not_resolve(solved, qapp):
    """It is a visibility change; recomputing would be wasteful and visible."""
    lab = _lab(qapp, solved)
    lab.plot.view.setCurrentText("Components")
    qapp.processEvents()

    before = solved.result
    lab.plot._chips[0].setChecked(False)
    qapp.processEvents()
    assert solved.result is before
    lab.deleteLater()


def test_hidden_components_survive_a_re_solve(solved, qapp):
    """Nudging a slider must not quietly switch a hidden component back on."""
    lab = _lab(qapp, solved)
    lab.plot.view.setCurrentText("Components")
    qapp.processEvents()
    lab.plot._chips[0].setChecked(False)
    qapp.processEvents()

    solved.set_param("mu", 12.0, resolve=False)
    _resolve(qapp, solved)

    assert lab.plot.hidden_components() == {0}
    assert not _shown(lab.plot, 0)
    assert _shown(lab.plot, 1)
    lab.deleteLater()


def test_switching_problem_clears_the_hidden_set(solved, qapp):
    """Component 2 of one problem has nothing to do with component 2 of another."""
    lab = _lab(qapp, solved)
    lab.plot.view.setCurrentText("Components")
    qapp.processEvents()
    lab.plot._chips[0].setChecked(False)
    qapp.processEvents()
    assert lab.plot.hidden_components() == {0}

    solved.set_problem("lorenz", resolve=False)
    _resolve(qapp, solved)

    assert lab.plot.hidden_components() == set()
    assert [c.label for c in lab.plot._chips] == list(catalog.get("lorenz").labels)
    assert all(chip.isChecked() for chip in lab.plot._chips)
    lab.deleteLater()


def test_no_chip_row_for_a_single_component_problem(qapp):
    """One curve needs no legend and nothing to switch between."""
    state = SessionState()
    state.set_problem("logistic", resolve=False)
    _resolve(qapp, state)
    assert state.result.solution.y.shape[0] == 1, "logistic must stay scalar"

    lab = _lab(qapp, state)
    lab.plot.view.setCurrentText("Components")
    qapp.processEvents()

    assert not lab.plot.components.isVisible()
    assert lab.plot._chips == []
    # With no chips the plot's own legend is the only one, so it stays.
    assert lab.plot.legend.items
    lab.deleteLater()


def test_no_chip_row_in_the_phase_view(solved, qapp):
    """In the phase plane the curve *is* the pair of components."""
    lab = _lab(qapp, solved)
    lab.plot.view.setCurrentText("Phase")
    qapp.processEvents()
    assert not lab.plot.components.isVisible()
    lab.deleteLater()


def test_the_chips_replace_the_in_plot_legend(solved, qapp):
    """Two lists of the same names would be clutter, and only one is clickable.

    pyqtgraph keeps a legend row when its item is hidden, so leaving both would
    also let the legend contradict the chips.
    """
    lab = _lab(qapp, solved)
    lab.plot.view.setCurrentText("Components")
    qapp.processEvents()

    assert lab.plot._chips, "chips are showing"
    assert not lab.plot.legend.items, "so the plot's own legend should be empty"
    lab.deleteLater()


@pytest.mark.parametrize("name", ["dark", "light"])
def test_chips_render_under_both_themes(solved, qapp, name):
    from odesuite_app.screens.lab import LabScreen

    lab = LabScreen(solved, PALETTES[name])
    lab.resize(1400, 860)
    lab.show()
    lab.plot.view.setCurrentText("Components")
    qapp.processEvents()
    assert lab.grab().width() > 0
    for chip in lab.plot._chips:
        assert chip.styleSheet(), "a chip must carry its series colour"
    lab.deleteLater()


# -- the work panel ------------------------------------------------------

def test_the_work_panel_collapses_to_a_strip(solved, qapp):
    lab = _lab(qapp, solved)
    stats = lab.stats
    full = stats.width()

    stats.set_collapsed(True)
    qapp.processEvents()
    assert stats.collapsed
    assert stats.width() < full // 3
    assert not stats._body.isVisible()

    stats.set_collapsed(False)
    qapp.processEvents()
    assert not stats.collapsed
    assert stats.width() == full
    lab.deleteLater()


def test_a_solve_finishing_while_collapsed_is_shown_on_reopening(solved, qapp):
    """Otherwise reopening shows whatever was there when it was shut."""
    lab = _lab(qapp, solved)
    lab.stats.set_collapsed(True)
    qapp.processEvents()

    solved.set_param("mu", 5.0, resolve=False)
    solved.set_param("t_end", 25.0, resolve=False)
    _resolve(qapp, solved)

    lab.stats.set_collapsed(False)
    qapp.processEvents()
    steps = lab.stats.rows["steps"].value.text()
    assert steps not in ("", "—")
    assert int(steps.replace(",", "")) == solved.result.solution.stats.naccepted
    lab.deleteLater()


def test_collapsing_gives_the_width_to_the_plot(solved, qapp):
    lab = _lab(qapp, solved)
    qapp.processEvents()
    before = lab.plot.width()

    lab.stats.set_collapsed(True)
    qapp.processEvents()
    lab.resize(lab.width(), lab.height())      # force a re-layout
    qapp.processEvents()
    assert lab.plot.width() > before
    lab.deleteLater()


def test_the_collapse_control_round_trips(solved, qapp):
    lab = _lab(qapp, solved)
    seen: list = []
    lab.stats.collapsed_changed.connect(seen.append)

    lab.stats.collapse_button.click()
    qapp.processEvents()
    assert lab.stats.collapsed

    lab.stats._strip.click()                   # the whole strip reopens it
    qapp.processEvents()
    assert not lab.stats.collapsed
    assert seen == [True, False]
    lab.deleteLater()


# ---------------------------------------------------------------------------
# The two views that are not the picture
# ---------------------------------------------------------------------------
#
# A plot is the one representation of a solution this application could not
# hand to somebody who is not looking at it. These are the other two: the
# paragraph a screen reader announces in its place, and the numbers behind it.


def test_the_panel_offers_the_plot_the_words_and_the_data(solved, qapp):
    from odesuite_app.widgets.plotpanel import PlotPanel

    panel = PlotPanel(PALETTE)
    tabs = [panel.views.tabText(i) for i in range(panel.views.count())]
    assert tabs == ["Plot", "In words", "Data"]
    panel.deleteLater()


def test_a_plot_describes_itself_for_a_reader_who_cannot_see_it(solved, qapp):
    """The alternative text is the accessible description of the plot widget,
    which is what a screen reader reads in place of the image."""
    from odesuite_app.widgets.plotpanel import PlotPanel

    panel = PlotPanel(PALETTE)
    panel.update_from(solved.result, "Auto")
    qapp.processEvents()

    words = panel.plot.accessibleDescription()
    assert words == panel.summary()
    assert "Van der Pol" in words
    # Not vacuous: it names the shape and the interval it was found over.
    assert "oscillates" in words, words
    assert "t from 0 to 60" in words, words
    panel.deleteLater()


def test_an_empty_panel_says_so_rather_than_describing_nothing(qapp):
    from odesuite_app.widgets.plotpanel import PlotPanel

    panel = PlotPanel(PALETTE)
    assert "Nothing has been solved" in panel.plot.accessibleDescription()
    panel.clear("solve failed")
    assert panel.plot.accessibleDescription() == "solve failed"
    panel.deleteLater()


def test_the_data_table_matches_the_solution(solved, qapp):
    from odesuite_app.widgets.plotpanel import PlotPanel

    panel = PlotPanel(PALETTE)
    panel.update_from(solved.result, "Auto")
    qapp.processEvents()

    model = panel.table_model
    solution = solved.result.solution
    assert model.columnCount() == solution.y.shape[0] + 1
    assert model.column_name(0) == "t"
    assert model.column_name(1) == catalog.get("van_der_pol").labels[0]

    index = model.index(0, 0)
    assert float(model.data(index)) == pytest.approx(float(solution.t[0]),
                                                     rel=1e-5)
    last = model.index(model.rowCount() - 1, 1)
    assert float(model.data(last)) == pytest.approx(float(solution.y[0, -1]),
                                                    rel=1e-5)
    panel.deleteLater()


def test_the_data_table_is_reachable_and_copyable_from_the_keyboard(solved,
                                                                    qapp):
    """Qt gives a table view selection and navigation and no copying at all,
    so `Ctrl+C` is the part that had to be written and is the part worth
    testing."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QGuiApplication

    from odesuite_app.widgets.plotpanel import PlotPanel

    panel = PlotPanel(PALETTE)
    panel.update_from(solved.result, "Auto")
    qapp.processEvents()

    assert panel.table.focusPolicy() != Qt.NoFocus, "not reachable by tab"
    panel.table.selectRow(0)
    copied = panel.table.copy_selection()
    assert copied, "nothing was copied"
    assert "\t" in copied, "a row should be tab separated for a spreadsheet"
    assert QGuiApplication.clipboard().text() == copied
    panel.deleteLater()


def test_a_huge_solution_is_thinned_for_the_table_and_says_so(solved, qapp):
    """Robertson has tens of thousands of output points, and a table row per
    point costs more to build than the solve did."""
    from odesuite_app.widgets.plotpanel import PlotPanel

    panel = PlotPanel(PALETTE)
    panel.update_from(solved.result, "Auto")
    qapp.processEvents()

    total = solved.result.solution.t.size
    assert panel.table_model.rowCount() <= 2001
    if total > 2000:
        assert "of" in panel.table_note.text()
    else:
        assert str(total) in panel.table_note.text()
    panel.deleteLater()
