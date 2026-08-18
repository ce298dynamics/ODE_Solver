"""Stiffness Explorer: why stiff problems break explicit methods.

Two panels side by side. On the left, the method's stability region -- the set
where ``|R(z)| <= 1``. On the right, the trajectory. As the solve plays back,
the Jacobian's eigenvalues scaled by the current step, ``h*lambda``, are drawn
as dots moving across the complex plane.

That is the whole argument of stiffness in one picture. An explicit method has a
*bounded* region, so as the solve proceeds the dots press against its boundary
and the step size is forced down to keep them inside -- not for accuracy, but
purely to stay stable. Switch to Radau and the boundary disappears: the entire
left half-plane is stable, the dots go wherever they like, and `h` grows by
orders of magnitude.

The eigenvalues are computed after the fact from the accepted steps, so nothing
in the solver has to be instrumented to produce them.
"""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from odesuite.stability import stability_grid

from .. import catalog
from ..analysis import jacobian_at
from ..state import SessionState, methods_for
from ..theme import Palette
from ..widgets.controls import ParameterPanel, ValueSlider, add_heading, control_panel

__all__ = ["StiffnessScreen"]

#: Methods worth comparing here: the two families whose regions differ most.
_METHODS = ["dopri5", "tsit5", "rk23", "rkf45", "radau", "rodas4"]

#: Grid resolution for the stability image.
_GRID = 190


class _Signals(QObject):
    grid_ready = Signal(object, object, object, str, object)  # |R|, re, im, method, report
    track_ready = Signal(object, int)                         # eigen track, token


class _GridJob(QRunnable):
    """Stability region plus classification, computed off the interface thread.

    Both are cached. The tableau methods take milliseconds, but RODAS4 has no
    Butcher tableau and falls back to running a step per sample -- several
    seconds for a full grid, which must not happen on the UI thread and must
    not happen twice.
    """

    _grids: dict[tuple, tuple] = {}
    _reports: dict[str, dict] = {}

    def __init__(self, method, window, signals) -> None:
        super().__init__()
        self.method, self.window, self.signals = method, window, signals

    def run(self) -> None:
        from odesuite.stability import classify_stability

        key = (self.method, self.window, _GRID)
        if key not in self._grids:
            re = np.linspace(self.window[0], self.window[1], _GRID)
            im = np.linspace(self.window[2], self.window[3], _GRID)
            try:
                self._grids[key] = (stability_grid(self.method, re, im), re, im)
            except Exception:
                return
        if self.method not in self._reports:
            try:
                self._reports[self.method] = classify_stability(self.method)
            except Exception:
                self._reports[self.method] = {
                    "A_stable": False, "real_axis_limit": float("nan"),
                    "L_stable": False, "R_at_minus_infinity": float("nan"),
                }

        magnitude, re, im = self._grids[key]
        try:
            self.signals.grid_ready.emit(
                magnitude, re, im, self.method, self._reports[self.method]
            )
        except RuntimeError:
            pass


class _TrackJob(QRunnable):
    """Compute ``h*lambda`` at every accepted step of a finished solve."""

    def __init__(self, problem, solution, token, signals) -> None:
        super().__init__()
        self.problem, self.solution = problem, solution
        self.token, self.signals = token, signals

    def run(self) -> None:
        try:
            track = eigenvalue_track(self.problem, self.solution)
        except Exception:
            track = None
        try:
            self.signals.track_ready.emit(track, self.token)
        except RuntimeError:
            pass


def eigenvalue_track(problem, solution, max_points: int = 900):
    """``(t, h, eigenvalues)`` at each accepted step.

    The quantity that decides stability is ``h * lambda``, with `lambda` the
    Jacobian's eigenvalues at the current state -- so both factors change as the
    solve proceeds, and the product is what has to stay inside the region.
    Sampled down for long solves, since the display cannot show more anyway.
    """
    times, states = solution.t, solution.y
    if times.size < 2:
        return None

    steps = np.diff(times)
    midpoints = times[:-1]
    indices = np.arange(midpoints.size)
    if indices.size > max_points:
        indices = np.unique(
            np.linspace(0, midpoints.size - 1, max_points).astype(int)
        )

    collected = []
    for index in indices:
        state = states[:, index]
        try:
            J = jacobian_at(problem, state) if state.size <= 64 else None
        except Exception:
            J = None
        if J is None:
            continue
        try:
            values = np.linalg.eigvals(np.asarray(J, dtype=complex))
        except np.linalg.LinAlgError:
            continue
        collected.append((midpoints[index], abs(steps[index]), values))

    if not collected:
        return None
    return collected


class StiffnessScreen(QWidget):
    def __init__(self, state: SessionState, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette
        self._track = None
        self._token = 0
        self._frame = 0
        self._grid_items: list = []
        self._signals = _Signals()
        self._signals.grid_ready.connect(self._on_grid)
        self._signals.track_ready.connect(self._on_track)

        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._advance)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(self._build_controls())

        plots = QHBoxLayout()
        plots.setSpacing(10)
        plots.addWidget(self._build_region(), 1)
        plots.addWidget(self._build_trajectory(), 1)
        layout.addLayout(plots, 1)

        self._method = "dopri5"
        self._problem_key = "van_der_pol"
        self._params = catalog.get(self._problem_key).defaults()
        self._params["mu"] = 30.0
        self._sync_controls()
        self._recompute()

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(252)

        explanation = QLabel(
            "Each dot is <b>h·λ</b> — a Jacobian eigenvalue times the current "
            "step. It must stay inside the shaded region or the step is "
            "unstable. Explicit methods have a small region, so a stiff "
            "problem forces <i>h</i> down for stability, not accuracy."
        )
        explanation.setWordWrap(True)
        explanation.setProperty("role", "muted")
        explanation.setStyleSheet("font-size: 11px;")
        layout.addWidget(explanation)

        add_heading(layout, "Problem", space_above=4)

        self.problem_picker = QComboBox()
        self.refresh_problems()
        self.problem_picker.currentIndexChanged.connect(self._on_problem)
        layout.addWidget(self.problem_picker)

        add_heading(layout, "Method")

        self.method_picker = QComboBox()
        self.method_picker.currentTextChanged.connect(self._on_method)
        layout.addWidget(self.method_picker)

        self.verdict = QLabel("")
        self.verdict.setWordWrap(True)
        self.verdict.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.verdict)

        add_heading(layout, "Tolerance", space_above=4)
        self.rtol = ValueSlider("relative tolerance", 1e-11, 1e-3, 1e-6, log=True)
        self.rtol.committed.connect(lambda _: self._recompute())
        layout.addWidget(self.rtol)

        add_heading(layout, "Parameters", space_above=4)
        self.parameters = ParameterPanel()
        self.parameters.changed.connect(self._on_param)
        layout.addWidget(self.parameters)

        layout.addSpacing(8)
        self.play_button = QPushButton("▶  Play")
        self.play_button.clicked.connect(self._toggle_play)
        layout.addWidget(self.play_button)

        self.scrub = QSlider(Qt.Horizontal)
        self.scrub.setRange(0, 0)
        self.scrub.valueChanged.connect(self._on_scrub)
        layout.addWidget(self.scrub)

        self.readout = QLabel("")
        self.readout.setProperty("role", "mono")
        self.readout.setStyleSheet("font-size: 11px;")
        self.readout.setWordWrap(True)
        layout.addWidget(self.readout)

        self.status = QLabel("")
        self.status.setProperty("role", "muted")
        self.status.setStyleSheet("font-size: 10.5px;")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch(1)
        return panel

    def _build_region(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        self.region_title = QLabel("Stability region")
        self.region_title.setProperty("role", "heading")
        layout.addWidget(self.region_title)

        self.region_plot = pg.PlotWidget()
        self.region_plot.setBackground(self.palette_obj.plot_background)
        self.region_plot.showGrid(x=True, y=True, alpha=0.15)
        self.region_plot.setLabel("bottom", "Re(hλ)")
        self.region_plot.setLabel("left", "Im(hλ)")
        self.region_plot.setMenuEnabled(False)
        layout.addWidget(self.region_plot, 1)
        return frame

    def _build_trajectory(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        self.trajectory_title = QLabel("Solution")
        self.trajectory_title.setProperty("role", "heading")
        layout.addWidget(self.trajectory_title)

        self.trajectory_plot = pg.PlotWidget()
        self.trajectory_plot.setBackground(self.palette_obj.plot_background)
        self.trajectory_plot.showGrid(x=True, y=True, alpha=0.15)
        self.trajectory_plot.setLabel("bottom", "t")
        self.trajectory_plot.setMenuEnabled(False)
        layout.addWidget(self.trajectory_plot, 1)

        self.step_plot = pg.PlotWidget()
        self.step_plot.setBackground(self.palette_obj.plot_background)
        self.step_plot.showGrid(x=True, y=True, alpha=0.15)
        self.step_plot.setLabel("left", "h")
        self.step_plot.setLabel("bottom", "t")
        self.step_plot.setLogMode(x=False, y=True)
        self.step_plot.setMaximumHeight(150)
        self.step_plot.setMenuEnabled(False)
        layout.addWidget(self.step_plot)
        return frame

    # -- control wiring --------------------------------------------------

    def _sync_controls(self) -> None:
        entry = catalog.get(self._problem_key)
        index = self.problem_picker.findData(self._problem_key)
        if index >= 0:
            self.problem_picker.blockSignals(True)
            self.problem_picker.setCurrentIndex(index)
            self.problem_picker.blockSignals(False)

        available = {m for names in methods_for(entry).values() for m in names}
        usable = [m for m in _METHODS if m in available]
        self.method_picker.blockSignals(True)
        self.method_picker.clear()
        self.method_picker.addItems(usable)
        if self._method in usable:
            self.method_picker.setCurrentText(self._method)
        elif usable:
            self._method = usable[0]
            self.method_picker.setCurrentText(self._method)
        self.method_picker.blockSignals(False)

        self.parameters.rebuild(entry, self._params)

    def refresh_problems(self) -> None:
        """Re-read the catalogue, so a newly typed equation appears here too."""
        from ..widgets.controls import fill_problem_picker

        # Needs a Jacobian small enough to diagonalise per step.
        fill_problem_picker(
            self.problem_picker,
            lambda entry: entry.plot_kind != "spacetime" and "pde" not in entry.tags,
        )

    def _on_problem(self, index: int) -> None:
        key = self.problem_picker.itemData(index)
        if not key:
            return
        self._problem_key = key
        self._params = catalog.get(key).defaults()
        self._sync_controls()
        self._recompute()

    def _on_method(self, method: str) -> None:
        if not method or method == self._method:
            return
        self._method = method
        self._recompute()

    def _on_param(self, name: str, value: float) -> None:
        self._params[name] = value
        self._recompute()

    # -- computation -----------------------------------------------------

    def _recompute(self) -> None:
        from odesuite import solve

        self._timer.stop()
        self.play_button.setText("▶  Play")
        entry = catalog.get(self._problem_key)
        bench = entry.build(self._params)
        rtol = self.rtol.value()

        self.status.setText("solving…")
        try:
            solution = solve(
                bench.problem, method=self._method, rtol=rtol, atol=rtol * 1e-3,
                max_steps=60_000,
            )
        except Exception as exc:
            self.status.setText(f"{type(exc).__name__}: {exc}")
            return

        self._solution = solution
        self._bench = bench
        self._draw_solution(solution, entry)

        # The eigenvalue extent sets a window that actually contains the
        # action; a fixed one would either clip the dots or hide the region.
        self._token += 1
        QThreadPool.globalInstance().start(
            _TrackJob(bench.problem, solution, self._token, self._signals)
        )
        self.status.setText(
            f"{solution.stats.naccepted} steps, {solution.stats.nrejected} rejected"
            + ("" if solution.success else f" — {solution.message}")
        )

    def _draw_solution(self, solution, entry) -> None:
        palette = self.palette_obj
        self.trajectory_plot.clear()
        for index in range(min(solution.y.shape[0], 4)):
            label = (
                entry.labels[index] if index < len(entry.labels) else f"y[{index}]"
            )
            self.trajectory_plot.plot(
                solution.t, solution.y[index], name=label,
                pen=pg.mkPen(palette.series[index % len(palette.series)], width=1.6),
            )
        self._playhead = pg.InfiniteLine(
            angle=90, pen=pg.mkPen(palette.warning, width=1.6)
        )
        self.trajectory_plot.addItem(self._playhead)
        self.trajectory_title.setText(f"{entry.title} — {self._method}")

        self.step_plot.clear()
        if solution.t.size > 1:
            midpoints = 0.5 * (solution.t[:-1] + solution.t[1:])
            self.step_plot.plot(
                midpoints, np.abs(np.diff(solution.t)),
                pen=pg.mkPen(palette.accent, width=1.4),
            )
        if solution.rejected.size:
            self.step_plot.plot(
                solution.rejected[:, 0], solution.rejected[:, 1],
                pen=None, symbol="x", symbolSize=7,
                symbolPen=pg.mkPen(palette.danger, width=1.4), symbolBrush=None,
            )
        self._step_playhead = pg.InfiniteLine(
            angle=90, pen=pg.mkPen(palette.warning, width=1.6)
        )
        self.step_plot.addItem(self._step_playhead)

    def _on_track(self, track, token: int) -> None:
        if token != self._token:
            return
        self._track = track
        if not track:
            self.scrub.setRange(0, 0)
            self.status.setText("could not compute eigenvalues for this problem")
            return

        products = np.concatenate([h * values for _t, h, values in track])
        span_re = float(np.max(np.abs(products.real))) or 1.0
        span_im = float(np.max(np.abs(products.imag))) or 1.0
        # Always show enough of the plane to include the region boundary, even
        # when every eigenvalue sits near the origin.
        window = (
            -max(1.4 * span_re, 6.0), max(0.4 * span_re, 2.0),
            -max(1.4 * span_im, 4.0), max(1.4 * span_im, 4.0),
        )
        self._window = window
        QThreadPool.globalInstance().start(
            _GridJob(self._method, window, self._signals)
        )

        self.scrub.blockSignals(True)
        self.scrub.setRange(0, len(track) - 1)
        self.scrub.setValue(0)
        self.scrub.blockSignals(False)
        self._frame = 0

    def _on_grid(self, magnitude, re, im, method: str, report: dict) -> None:
        if method != self._method:
            return
        palette = self.palette_obj
        self.region_plot.clear()
        self._grid_items.clear()

        stable = (magnitude <= 1.0).astype(float)
        image = pg.ImageItem(stable.T)
        image.setLookupTable(
            np.array(
                [[0, 0, 0, 0], [*pg.colorTuple(pg.mkColor(palette.accent))[:3], 55]],
                dtype=np.ubyte,
            )
        )
        image.setLevels([0.0, 1.0])
        image.setRect(re[0], im[0], re[-1] - re[0], im[-1] - im[0])
        self.region_plot.addItem(image)

        self.region_plot.addItem(
            pg.InfiniteLine(angle=90, pos=0, pen=pg.mkPen(palette.border, width=1))
        )
        self.region_plot.addItem(
            pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen(palette.border, width=1))
        )

        self._eigen_marks = self.region_plot.plot(
            [], [], pen=None, symbol="o", symbolSize=11,
            symbolPen=pg.mkPen(palette.text, width=1.4),
            symbolBrush=pg.mkBrush(palette.warning),
        )
        self._eigen_trail = self.region_plot.plot(
            [], [], pen=None, symbol="o", symbolSize=4,
            symbolPen=None, symbolBrush=pg.mkBrush(palette.text_muted),
        )
        self._eigen_trail.setOpacity(0.4)

        self.region_plot.setXRange(re[0], re[-1], padding=0.0)
        self.region_plot.setYRange(im[0], im[-1], padding=0.0)

        if report["A_stable"]:
            self.region_title.setText(f"Stability region — {self._method} (A-stable)")
            self.verdict.setText(
                f"<span style='color:{palette.success}'><b>{self._method}</b> is "
                f"A-stable</span>: the whole left half-plane is stable, so "
                f"stiffness places no limit on the step."
            )
        else:
            limit = report["real_axis_limit"]
            self.region_title.setText(
                f"Stability region — {self._method} (bounded, |hλ| < {limit:.2f})"
            )
            self.verdict.setText(
                f"<span style='color:{palette.danger}'><b>{self._method}</b> is not "
                f"A-stable</span>: stable only for |hλ| ≲ {limit:.2f} on the real "
                f"axis, so a stiff eigenvalue caps the step size."
            )
        self._render_frame()

    # -- playback --------------------------------------------------------

    def _toggle_play(self) -> None:
        if self._timer.isActive():
            self._timer.stop()
            self.play_button.setText("▶  Play")
        elif self._track:
            if self._frame >= len(self._track) - 1:
                self._frame = 0
            self._timer.start()
            self.play_button.setText("❚❚  Pause")

    def _advance(self) -> None:
        if not self._track:
            self._timer.stop()
            return
        self._frame += 1
        if self._frame >= len(self._track):
            self._frame = len(self._track) - 1
            self._timer.stop()
            self.play_button.setText("▶  Play")
        self.scrub.blockSignals(True)
        self.scrub.setValue(self._frame)
        self.scrub.blockSignals(False)
        self._render_frame()

    def _on_scrub(self, value: int) -> None:
        self._frame = value
        self._render_frame()

    def _render_frame(self) -> None:
        if not self._track or not hasattr(self, "_eigen_marks"):
            return
        frame = min(self._frame, len(self._track) - 1)
        t, h, values = self._track[frame]
        products = h * values

        self._eigen_marks.setData(products.real, products.imag)
        trail = np.concatenate(
            [hh * vv for _tt, hh, vv in self._track[max(0, frame - 60):frame]]
        ) if frame else np.empty(0, dtype=complex)
        self._eigen_trail.setData(trail.real, trail.imag)

        if hasattr(self, "_playhead"):
            self._playhead.setPos(t)
            self._step_playhead.setPos(t)

        self.readout.setText(
            f"t = {t:.6g}\nh = {h:.3e}\n"
            + "\n".join(
                f"hλ = {p.real:+.3f}{p.imag:+.3f}i" for p in products[:4]
            )
        )
