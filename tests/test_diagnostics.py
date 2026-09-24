"""The local failed-solve log and the report built from it (REL-04)."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from odesuite_app import diagnostics


def _result(error=None, diagnosis=None, cancelled=False, trace=None):
    request = SimpleNamespace(problem_key="lorenz", method="rk23", rtol=1e-6,
                              atol=1e-9, n_steps=None, params={"rho": 28.0})
    solution = SimpleNamespace(diagnosis=diagnosis)
    result = SimpleNamespace(request=request, error=error, solution=solution,
                             cancelled=cancelled)
    if trace:
        result.traceback = trace
    return result


def _failed(kind="step_size_underflow"):
    return SimpleNamespace(failed=True, __str__=lambda self: kind)


def test_a_failure_appends_one_entry(tmp_path):
    log = tmp_path / "diagnostics.log"
    assert diagnostics.record_result(_result(error="ValueError: boom"), where=log)
    entries = diagnostics.recent(where=log)
    assert len(entries) == 1
    entry = entries[0]
    assert entry["problem"] == "lorenz" and entry["method"] == "rk23"
    assert entry["error"] == "ValueError: boom"
    assert entry["params"] == {"rho": 28.0}


def test_success_and_cancellation_are_not_failures(tmp_path):
    log = tmp_path / "diagnostics.log"
    clean = SimpleNamespace(failed=False)
    assert not diagnostics.record_result(_result(diagnosis=clean), where=log)
    assert not diagnostics.record_result(_result(error="x", cancelled=True), where=log)
    assert not log.exists()


def test_the_log_stays_bounded(tmp_path):
    log = tmp_path / "diagnostics.log"
    for index in range(2000):
        diagnostics.record({"problem": f"p{index}", "error": "x" * 100}, where=log)
    assert log.stat().st_size <= diagnostics.MAX_BYTES
    # The newest survive, and every surviving line is still whole JSON.
    lines = log.read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[-1])["problem"] == "p1999"
    assert all(json.loads(line) for line in lines)


def test_logging_never_raises(tmp_path):
    """A log that fails must not become a second failure."""
    blocked = tmp_path / "a-file"
    blocked.write_text("")
    diagnostics.record({"x": 1}, where=blocked / "diagnostics.log")
    assert diagnostics.recent(where=blocked / "diagnostics.log") == []


@pytest.mark.parametrize("raw,shown", [
    (r'File "C:\Users\someone\proj\src\odesuite_app\solver.py", line 3',
     'File "odesuite_app/solver.py", line 3'),
    ('File "/home/someone/.venv/lib/python3.12/site-packages/numpy/core/x.py"',
     'File "numpy/core/x.py"'),
    ('File "/home/someone/private/script.py", line 9',
     'File "script.py", line 9'),
])
def test_paths_are_cut_to_the_package(raw, shown):
    assert diagnostics.scrub(raw) == shown


def test_the_report_carries_versions_and_the_failure_but_no_paths(tmp_path):
    log = tmp_path / "diagnostics.log"
    trace = ('Traceback (most recent call last):\n'
             '  File "C:\\Users\\someone\\src\\odesuite\\driver.py", line 40\n'
             'ValueError: boom')
    diagnostics.record_result(_result(error="ValueError: boom", trace=trace),
                              where=log)
    text = diagnostics.report(where=log)
    assert "odesuite " in text and "Python " in text
    assert "lorenz with rk23" in text and "ValueError: boom" in text
    assert "odesuite/driver.py" in text
    assert "someone" not in text


def test_an_empty_log_says_so(tmp_path):
    assert "No failed solves" in diagnostics.report(where=tmp_path / "none.log")


# ---------------------------------------------------------------------------
# Wired into the application
# ---------------------------------------------------------------------------


def test_a_failed_solve_in_the_app_is_recorded_and_copyable():
    pytest.importorskip("PySide6")
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtWidgets import QApplication

    from odesuite_app.app import MainWindow

    app = QApplication.instance() or QApplication([])
    before = len(diagnostics.recent(count=10_000))

    window = MainWindow("dark")
    state = window.state
    # Explicit RK4 needs a step count; with none, the driver refuses -- a
    # failure raised by the solver, which is exactly what the log is for.
    state.runner.submit(state.request(method="rk4", n_steps=None))
    assert state.runner.wait(60_000)
    app.processEvents()

    entries = diagnostics.recent(count=10_000)
    assert len(entries) == before + 1
    assert entries[-1]["method"] == "rk4" and entries[-1].get("error")

    text = window.copy_diagnostics()
    assert QGuiApplication.clipboard().text() == text
    assert "with rk4" in text
    assert window.sidebar.status.text().startswith("diagnostics copied")
    window.close()
