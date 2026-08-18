"""Accuracy Lab: work-precision, convergence order, and energy drift.

The verification harness made interactive. Three studies, each of which is the
standard way of answering a different question:

**Work-precision** — what accuracy does a method actually deliver per unit of
work? Tolerances are requests, not guarantees, so comparing methods at a fixed
tolerance says nothing; sweeping it and plotting error against evaluations does.

**Convergence order** — does the method attain its theoretical order? Fixed-step
runs, a log-log fit, and the fitted slope against the claim.

**Energy drift** — is the error bounded or growing? For a Hamiltonian problem
this separates methods that are merely accurate from methods that are faithful.
"""

from __future__ import annotations

import time

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from odesuite import make_stepper, solve

from .. import catalog
from ..state import SessionState, methods_for
from ..theme import Palette
from ..widgets.controls import add_heading, control_panel

__all__ = ["AccuracyScreen"]

_STUDIES = ["Work–precision", "Convergence order", "Energy drift"]
_CANDIDATES = ["rk23", "dopri5", "tsit5", "cashkarp", "rkf45", "radau",
               "rodas4", "taylor20", "verlet", "yoshida4"]


class _Signals(QObject):
    done = Signal(object, int)


class _StudyJob(QRunnable):
    def __init__(self, work, token, signals) -> None:
        super().__init__()
        self.work, self.token, self.signals = work, token, signals

    def run(self) -> None:
        try:
            payload = self.work()
        except Exception as exc:
            payload = {"error": f"{type(exc).__name__}: {exc}"}
        try:
            self.signals.done.emit(payload, self.token)
        except RuntimeError:
            pass


# ---------------------------------------------------------------------------
# The studies themselves (pure functions, run on a worker)
# ---------------------------------------------------------------------------


def _reference(entry, params):
    """A trustworthy endpoint for the problem, independent of the competitors."""
    bench = entry.build(params)
    if bench.has_exact:
        return bench.exact_at_end(), "analytic"
    method = "radau" if entry.is_stiff else "dopri5"
    solution = solve(
        bench.problem, method=method, rtol=1e-13, atol=1e-15, max_steps=500_000
    )
    return solution.y[:, -1], f"{method} at rtol=1e-13"


def work_precision(entry, params, methods, tolerances):
    reference, source = _reference(entry, params)
    bench = entry.build(params)
    series: dict[str, list[tuple[float, int, float]]] = {}

    for method in methods:
        points = []
        for tol in tolerances:
            start = time.perf_counter()
            try:
                solution = solve(
                    bench.problem, method=method, rtol=tol, atol=tol * 1e-3,
                    max_steps=300_000,
                )
            except Exception:
                continue
            elapsed = time.perf_counter() - start
            if not solution.success:
                continue
            error = float(
                np.linalg.norm(solution.y[:, -1] - reference)
                / max(np.linalg.norm(reference), 1e-12)
            )
            points.append((max(error, 1e-17), solution.stats.nfev, elapsed))
        if points:
            series[method] = points
    return {"series": series, "reference": source}


def convergence(entry, params, methods, counts):
    """Fixed-step global error against the step size, with a fitted slope."""
    bench = entry.build(params)
    if not bench.has_exact:
        return {"error": "this study needs a problem with a closed-form solution"}
    exact = bench.exact_at_end()
    span = abs(bench.problem.tf - bench.problem.t0)

    series = {}
    for method in methods:
        stepper = make_stepper(method)
        if not stepper.adaptive:
            continue
        errors, steps = [], []
        for n in counts:
            try:
                y = _fixed_step(stepper, bench.problem, n)
            except Exception:
                break
            error = float(np.linalg.norm(y - exact))
            if error <= 1e-13:
                break
            errors.append(error)
            steps.append(span / n)
        if len(errors) >= 2:
            slope = float(
                np.log(errors[-2] / errors[-1]) / np.log(steps[-2] / steps[-1])
            )
            series[method] = (np.array(steps), np.array(errors), slope, stepper.order)
    return {"series": series}


def _fixed_step(stepper, problem, n_steps: int):
    """Integrate with `n_steps` equal steps, bypassing the controller."""
    t, tf = problem.t0, problem.tf
    h = (tf - t) / n_steps
    y = problem.y0.copy()
    f = problem.f(t, y)
    for index in range(n_steps):
        result = stepper.step(problem, t, y, f, h)
        if not result.ok:
            raise RuntimeError("step failed")
        y = result.y_new
        t = tf if index == n_steps - 1 else t + h
        f = result.f_new if result.f_new is not None else problem.f(t, y)
    return y


def energy_drift(entry, params, methods, n_steps: int):
    bench = entry.build(params)
    if bench.invariant is None:
        return {"error": "this problem has no conserved quantity to track"}
    reference = bench.invariant(bench.problem.y0)
    if abs(reference) < 1e-30:
        return {"error": "the conserved quantity is zero at the initial state"}

    series = {}
    for method in methods:
        stepper = make_stepper(method)
        try:
            kwargs = (
                {"n_steps": n_steps} if not stepper.adaptive
                else {"rtol": 1e-8, "atol": 1e-11}
            )
            solution = solve(bench.problem, method=method, max_steps=500_000, **kwargs)
        except Exception:
            continue
        if not solution.success:
            continue
        indices = np.unique(
            np.linspace(0, solution.y.shape[1] - 1, 900).astype(int)
        )
        drift = np.array([
            abs(bench.invariant(solution.y[:, i]) - reference) / abs(reference)
            for i in indices
        ])
        series[method] = (solution.t[indices], drift, solution.stats.nfev)
    return {"series": series}


# ---------------------------------------------------------------------------
# The screen
# ---------------------------------------------------------------------------


class AccuracyScreen(QWidget):
    def __init__(self, state: SessionState, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette
        self._token = 0
        self._signals = _Signals()
        self._signals.done.connect(self._on_done)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(self._build_controls())

        right = QVBoxLayout()
        right.setSpacing(10)
        right.addWidget(self._build_plot(), 1)
        right.addWidget(self._build_summary())
        layout.addLayout(right, 1)

        self._problem_key = "lotka_volterra"
        self._sync_controls()

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(244)

        add_heading(layout, "Study")

        self.study = QComboBox()
        self.study.addItems(_STUDIES)
        self.study.currentTextChanged.connect(self._on_study)
        layout.addWidget(self.study)

        self.explanation = QLabel("")
        self.explanation.setWordWrap(True)
        self.explanation.setProperty("role", "muted")
        self.explanation.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.explanation)

        add_heading(layout, "Problem", space_above=4)

        self.problem_picker = QComboBox()
        self.problem_picker.currentIndexChanged.connect(self._on_problem)
        layout.addWidget(self.problem_picker)

        add_heading(layout, "Methods", space_above=4)

        self.checks: dict[str, QCheckBox] = {}
        for method in _CANDIDATES:
            box = QCheckBox(method)
            box.setChecked(method in ("dopri5", "tsit5", "radau"))
            layout.addWidget(box)
            self.checks[method] = box

        layout.addSpacing(8)
        self.run_button = QPushButton("Run study")
        self.run_button.setProperty("role", "primary")
        self.run_button.clicked.connect(self._run)
        layout.addWidget(self.run_button)

        self.status = QLabel("")
        self.status.setProperty("role", "muted")
        self.status.setStyleSheet("font-size: 10.5px;")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch(1)
        self._on_study(_STUDIES[0])
        return panel

    def _build_plot(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        self.title = QLabel("Accuracy Lab")
        self.title.setProperty("role", "heading")
        layout.addWidget(self.title)

        self.plot = pg.PlotWidget()
        self.plot.setBackground(self.palette_obj.plot_background)
        self.plot.showGrid(x=True, y=True, alpha=0.18)
        self.plot.setMenuEnabled(False)
        self.plot.addLegend(offset=(-10, 10), labelTextSize="9pt")
        layout.addWidget(self.plot, 1)
        return frame

    def _build_summary(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        frame.setMinimumHeight(120)
        frame.setMaximumHeight(190)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(3)

        add_heading(layout, "Results")

        self.summary = QLabel("—")
        self.summary.setProperty("role", "mono")
        self.summary.setStyleSheet("font-size: 11px;")
        self.summary.setTextFormat(Qt.RichText)
        self.summary.setWordWrap(True)
        self.summary.setAlignment(Qt.AlignTop)
        layout.addWidget(self.summary, 1)
        return frame

    # -- control wiring --------------------------------------------------

    def _on_study(self, study: str) -> None:
        self.explanation.setText({
            "Work–precision": "Sweeps the tolerance and plots the accuracy "
                              "actually achieved against the work it cost. "
                              "Down and to the left is better.",
            "Convergence order": "Fixed-step runs at decreasing h, with the "
                                 "log-log slope fitted and compared against "
                                 "the method's theoretical order. Needs a "
                                 "problem with a closed-form solution.",
            "Energy drift": "Tracks the conserved quantity over time. A "
                            "symplectic method's error oscillates; a "
                            "conventional one's grows.",
        }.get(study, ""))
        self._sync_controls()

    def refresh_problems(self) -> None:
        """Re-read the catalogue, so a newly typed equation appears here too."""
        self._sync_controls()

    def _sync_controls(self) -> None:
        study = self.study.currentText()
        current = self.problem_picker.currentData()

        self.problem_picker.blockSignals(True)
        self.problem_picker.clear()
        # Rebuilt on every study change, which is also how a typed equation
        # finds its way in. The per-study filters below keep it out of the two
        # studies it cannot support: convergence order needs a closed-form
        # reference and energy drift a conserved quantity, and a hand-typed
        # equation is not declared to have either.
        for key in catalog.keys(include_user=True):
            entry = catalog.get(key)
            if "pde" in entry.tags:
                continue
            bench_ok = True
            if study == "Convergence order":
                bench_ok = "analytic" in entry.tags
            elif study == "Energy drift":
                bench_ok = "hamiltonian" in entry.tags or "periodic" in entry.tags
            if bench_ok:
                self.problem_picker.addItem(entry.title, key)
        index = self.problem_picker.findData(current)
        self.problem_picker.setCurrentIndex(max(index, 0))
        self.problem_picker.blockSignals(False)

        key = self.problem_picker.currentData()
        if key:
            self._problem_key = key
            self._filter_methods()

    def _filter_methods(self) -> None:
        entry = catalog.get(self._problem_key)
        available = {m for names in methods_for(entry).values() for m in names}
        study = self.study.currentText()
        for method, box in self.checks.items():
            usable = method in available
            if study == "Convergence order" and usable:
                usable = make_stepper(method).adaptive
            box.setEnabled(usable)
            if not usable:
                box.setChecked(False)

    def _on_problem(self, index: int) -> None:
        key = self.problem_picker.itemData(index)
        if key:
            self._problem_key = key
            self._filter_methods()

    def selected_methods(self) -> list[str]:
        return [m for m, b in self.checks.items() if b.isChecked() and b.isEnabled()]

    # -- running ---------------------------------------------------------

    def _run(self) -> None:
        methods = self.selected_methods()
        if not methods:
            self.status.setText("select at least one method")
            return

        entry = catalog.get(self._problem_key)
        params = entry.defaults()
        study = self.study.currentText()
        self._token += 1
        self._study_running = study
        self.status.setText("running…")
        self.run_button.setEnabled(False)

        if study == "Work–precision":
            tolerances = np.logspace(-4, -11, 8)
            work = lambda: work_precision(entry, params, methods, tolerances)
        elif study == "Convergence order":
            work = lambda: convergence(
                entry, params, methods, [10, 20, 40, 80, 160, 320]
            )
        else:
            work = lambda: energy_drift(entry, params, methods, 20_000)

        QThreadPool.globalInstance().start(
            _StudyJob(work, self._token, self._signals)
        )

    def _on_done(self, payload, token: int) -> None:
        if token != self._token:
            return
        self.run_button.setEnabled(True)
        if "error" in payload:
            self.status.setText(payload["error"])
            self.summary.setText(f"<i>{payload['error']}</i>")
            return
        self.status.setText("")

        study = getattr(self, "_study_running", _STUDIES[0])
        if study == "Work–precision":
            self._draw_work_precision(payload)
        elif study == "Convergence order":
            self._draw_convergence(payload)
        else:
            self._draw_energy(payload)

    # -- drawing ---------------------------------------------------------

    def _fresh_plot(self):
        self.plot.clear()
        self.plot.addLegend(offset=(-10, 10), labelTextSize="9pt")
        return self.palette_obj

    def _draw_work_precision(self, payload) -> None:
        palette = self._fresh_plot()
        self.plot.setLogMode(x=True, y=True)
        self.plot.setLabel("bottom", "RHS evaluations")
        self.plot.setLabel("left", "relative error at t_end")

        rows = []
        for index, (method, points) in enumerate(payload["series"].items()):
            colour = palette.series[index % len(palette.series)]
            errors = [p[0] for p in points]
            evaluations = [p[1] for p in points]
            self.plot.plot(
                evaluations, errors, name=method,
                pen=pg.mkPen(colour, width=2), symbol="o", symbolSize=6,
                symbolBrush=pg.mkBrush(colour), symbolPen=None,
            )
            best = min(points, key=lambda p: p[0])
            rows.append(
                f"<span style='color:{colour}'>{method}</span> best "
                f"{best[0]:.2e} at {best[1]:,} evals ({best[2] * 1e3:.0f} ms)"
            )
        self.title.setText(
            f"{catalog.get(self._problem_key).title} — work-precision "
            f"(reference: {payload['reference']})"
        )
        self.summary.setText("<br>".join(rows) or "<i>no results</i>")

    def _draw_convergence(self, payload) -> None:
        palette = self._fresh_plot()
        self.plot.setLogMode(x=True, y=True)
        self.plot.setLabel("bottom", "step size h")
        self.plot.setLabel("left", "error at t_end")

        rows = []
        for index, (method, (steps, errors, slope, order)) in enumerate(
            payload["series"].items()
        ):
            colour = palette.series[index % len(palette.series)]
            self.plot.plot(
                steps, errors, name=f"{method} (slope {slope:.2f})",
                pen=pg.mkPen(colour, width=2), symbol="o", symbolSize=6,
                symbolBrush=pg.mkBrush(colour), symbolPen=None,
            )
            agrees = abs(slope - order) < 0.5
            mark = palette.success if agrees else palette.warning
            rows.append(
                f"<span style='color:{colour}'>{method}</span> fitted "
                f"<b>{slope:.2f}</b> vs claimed {order} "
                f"<span style='color:{mark}'>{'✔' if agrees else '≈'}</span>"
            )
        self.title.setText(
            f"{catalog.get(self._problem_key).title} — convergence order"
        )
        self.summary.setText("<br>".join(rows) or "<i>no results</i>")

    def _draw_energy(self, payload) -> None:
        palette = self._fresh_plot()
        self.plot.setLogMode(x=False, y=True)
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "|ΔE / E|")

        rows = []
        for index, (method, (t, drift, evaluations)) in enumerate(
            payload["series"].items()
        ):
            colour = palette.series[index % len(palette.series)]
            self.plot.plot(
                t, np.maximum(drift, 1e-18), name=method,
                pen=pg.mkPen(colour, width=1.6),
            )
            half = drift.size // 2
            first = float(drift[:half].max()) if half else 0.0
            second = float(drift[half:].max()) if half else 0.0
            ratio = second / max(first, 1e-30)
            bounded = ratio < 1.5
            rows.append(
                f"<span style='color:{colour}'>{method}</span> "
                f"{evaluations:,} evals · halves {first:.2e} → {second:.2e} · "
                f"<span style='color:"
                f"{palette.success if bounded else palette.danger}'>"
                f"{'bounded' if bounded else f'growing {ratio:.1f}×'}</span>"
            )
        self.title.setText(
            f"{catalog.get(self._problem_key).title} — energy drift"
        )
        self.summary.setText("<br>".join(rows) or "<i>no results</i>")
