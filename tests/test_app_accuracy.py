"""The Accuracy Lab and Build Your Own screens, plus the packaged entry point."""

from __future__ import annotations

import numpy as np
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


def _settle(qapp, timeout: int = 300_000) -> None:
    for _ in range(4):
        QThreadPool.globalInstance().waitForDone(timeout)
        for _ in range(25):
            qapp.processEvents()


# ---------------------------------------------------------------------------
# The studies, as functions
# ---------------------------------------------------------------------------


def test_convergence_study_recovers_the_theoretical_orders():
    """The library's central claim, computed the way the screen computes it."""
    from odesuite_app.screens.accuracy import convergence

    entry = catalog.get("sine_cosine")
    payload = convergence(
        entry, entry.defaults(), ["rk23", "dopri5", "tsit5", "rodas4"],
        [10, 20, 40, 80, 160, 320],
    )
    assert "error" not in payload

    for method, (_steps, _errors, slope, order) in payload["series"].items():
        assert slope == pytest.approx(order, abs=0.4), (
            f"{method}: fitted {slope:.2f} against a claimed order of {order}"
        )


def test_convergence_study_refuses_problems_without_an_exact_solution():
    from odesuite_app.screens.accuracy import convergence

    entry = catalog.get("lotka_volterra")
    payload = convergence(entry, entry.defaults(), ["dopri5"], [10, 20, 40])
    assert "closed-form" in payload["error"]


def test_work_precision_error_falls_as_work_rises():
    from odesuite_app.screens.accuracy import work_precision

    entry = catalog.get("lotka_volterra")
    payload = work_precision(
        entry, entry.defaults(), ["dopri5", "tsit5"], np.logspace(-4, -10, 7)
    )
    assert "error" not in payload

    for method, points in payload["series"].items():
        errors = [p[0] for p in points]
        evaluations = [p[1] for p in points]
        assert len(points) >= 4, f"{method} produced too few points"
        assert evaluations == sorted(evaluations), "work should rise with tolerance"
        assert errors[-1] < errors[0] * 1e-3, f"{method}: accuracy did not improve"


def test_energy_drift_separates_symplectic_from_conventional():
    """The Phase 4 library result, reproduced through the screen's own code."""
    from odesuite_app.screens.accuracy import energy_drift

    entry = catalog.get("kepler_symplectic")
    params = {**entry.defaults(), "n_orbits": 300.0}
    payload = energy_drift(entry, params, ["verlet", "dopri5"], 300 * 200)
    assert "error" not in payload

    def growth(method):
        _t, drift, _n = payload["series"][method]
        half = drift.size // 2
        return drift[half:].max() / max(drift[:half].max(), 1e-30)

    assert growth("verlet") < 1.5, "a symplectic method must stay bounded"
    assert growth("dopri5") > 1.5, "DOPRI5 should show secular growth"


def test_energy_drift_refuses_problems_without_an_invariant():
    from odesuite_app.screens.accuracy import energy_drift

    entry = catalog.get("robertson_dae")
    payload = energy_drift(entry, entry.defaults(), ["radau"], 1000)
    assert "error" in payload or payload["series"]


# ---------------------------------------------------------------------------
# The screens
# ---------------------------------------------------------------------------


def test_accuracy_screen_filters_problems_per_study(qapp):
    from odesuite_app.screens.accuracy import AccuracyScreen

    screen = AccuracyScreen(SessionState(), PALETTE)

    screen.study.setCurrentText("Convergence order")
    offered = {
        screen.problem_picker.itemData(i)
        for i in range(screen.problem_picker.count())
    }
    assert offered, "no problems offered for the convergence study"
    for key in offered:
        assert "analytic" in catalog.get(key).tags

    screen.study.setCurrentText("Energy drift")
    offered = {
        screen.problem_picker.itemData(i)
        for i in range(screen.problem_picker.count())
    }
    for key in offered:
        tags = catalog.get(key).tags
        assert "hamiltonian" in tags or "periodic" in tags
    screen.deleteLater()


def test_accuracy_screen_runs_a_study(qapp):
    from odesuite_app.screens.accuracy import AccuracyScreen

    screen = AccuracyScreen(SessionState(), PALETTE)
    screen.study.setCurrentText("Convergence order")
    index = screen.problem_picker.findData("sine_cosine")
    assert index >= 0
    screen.problem_picker.setCurrentIndex(index)
    screen._on_problem(index)
    for method, box in screen.checks.items():
        box.setChecked(method in ("dopri5", "rk23") and box.isEnabled())

    screen._run()
    _settle(qapp)
    assert "fitted" in screen.summary.text()
    assert "vs claimed" in screen.summary.text()
    screen.deleteLater()


def test_accuracy_screen_reports_no_selection(qapp):
    from odesuite_app.screens.accuracy import AccuracyScreen

    screen = AccuracyScreen(SessionState(), PALETTE)
    for box in screen.checks.values():
        box.setChecked(False)
    screen._run()
    assert "at least one" in screen.status.text()
    screen.deleteLater()


# The three tests below covered the old "Build Your Own" screen, which the
# Solver Lab's equation editor replaced. They are kept, pointed at the editor,
# because what they check did not change: every worked example must load and
# solve, and bad input must produce a message rather than a traceback.

def test_the_editor_loads_and_solves_every_example(qapp):
    from odesuite_app.equationmodel import entry_from_text
    from odesuite_app.widgets.equationeditor import EquationEditor

    editor = EquationEditor(PALETTE)
    received: list = []
    editor.submitted.connect(lambda spec, ranges: received.append((spec, ranges)))

    for index in range(editor.example_picker.count()):
        name = editor.example_picker.itemText(index)
        received.clear()
        editor.select_example(name)
        qapp.processEvents()
        assert received, f"{name} did not submit: {editor.message.text()}"

        spec, ranges = received[-1]
        entry, _ = entry_from_text(spec, ranges)
        bench = entry.build(entry.defaults())
        assert bench.problem.y0.size >= 1, name
    editor.deleteLater()


def test_the_editor_reports_an_unknown_name_without_crashing(qapp):
    from odesuite_app.custom import ParseError
    from odesuite_app.equationmodel import entry_from_text
    from odesuite_app.widgets.equationeditor import EquationEditor

    editor = EquationEditor(PALETTE)
    editor.equation_fields[0].setText("y' = y + nonsense")
    for field in editor.equation_fields[1:]:
        field.clear()
    # `nonsense` is inferred as a parameter, so blank its value to make it
    # genuinely undeclared rather than silently defaulted.
    for label, value, low, high in editor.parameter_rows:
        if label.text() == "nonsense":
            label.setText("")

    spec, ranges = editor.read()
    with pytest.raises(ParseError, match="unknown name"):
        entry_from_text(spec, ranges)
    editor.deleteLater()


def test_the_editor_rejects_a_non_numeric_parameter(qapp):
    from odesuite_app.custom import ParseError
    from odesuite_app.widgets.equationeditor import EquationEditor

    editor = EquationEditor(PALETTE)
    editor.equation_fields[0].setText("y' = -k*y")
    for field in editor.equation_fields[1:]:
        field.clear()
    qapp.processEvents()
    for label, value, low, high in editor.parameter_rows:
        if label.text() == "k":
            value.setText("abc")

    with pytest.raises(ParseError, match="not a number"):
        editor.read()

    editor.submit()                       # the screen path must not raise
    assert "not a number" in editor.message.text()
    editor.deleteLater()


# ---------------------------------------------------------------------------
# Packaging entry point
# ---------------------------------------------------------------------------


def test_selftest_passes_from_source():
    """The same check the packaged executable runs.

    A frozen GUI application on Windows has no stdout, so the exit code is the
    only signal a build script can act on -- which makes this worth having as
    a library-level test too.
    """
    from odesuite_app.cli import selftest

    assert selftest("-") == 0


def test_selftest_writes_a_report(tmp_path):
    from odesuite_app.cli import selftest

    report = tmp_path / "report.txt"
    assert selftest(str(report)) == 0
    text = report.read_text(encoding="utf-8")
    assert "passed" in text
    assert "FAIL" not in text


def test_cli_parser_accepts_the_documented_flags():
    from odesuite_app.cli import build_parser

    parser = build_parser()
    args = parser.parse_args(["--theme", "light", "--problem", "lorenz",
                              "--screen", "lab"])
    assert args.theme == "light" and args.problem == "lorenz"
    assert parser.parse_args(["--selftest"]).selftest == "-"
    assert parser.parse_args(["--selftest", "out.txt"]).selftest == "out.txt"


def test_packaging_spec_exists_and_names_the_launcher():
    """The spec must point at the absolute-import launcher.

    Aiming PyInstaller at `odesuite_app/__main__.py` builds successfully and
    then fails at runtime with "attempted relative import with no known parent
    package", because the bundle runs the entry script as a top-level module.
    """
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    spec = root / "packaging" / "odesuite.spec"
    launcher = root / "packaging" / "launch.py"

    assert spec.exists() and launcher.exists()
    text = spec.read_text(encoding="utf-8")
    assert "launch.py" in text
    assert "__main__.py" not in text.split("analysis = Analysis")[1][:400]
    assert "torch" in text, "the torch exclusion saves 263 MB and must stay"
    assert "from odesuite_app.cli import main" in launcher.read_text(encoding="utf-8")
