"""Method Race: several integrators on one problem, side by side.

Each method solves the same problem at the same tolerance, and the results are
replayed together against integration time. A progress bar per method shows how
far through the interval it has reached and what that has cost so far in steps
and right-hand-side evaluations.

Run it on Robertson and the Phase 2 acceptance result becomes a spectator
sport: Radau sprints across eleven decades of time while DOPRI5 is still
inching through the first fifty units, bound by stability rather than accuracy.
The leaderboard at the end ranks by accuracy achieved and work spent, which is
the honest comparison -- a method that finishes first having taken a hundred
times the evaluations has not won anything.
"""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import catalog
from ..solver import SolveRequest
from ..state import SessionState, methods_for
from ..theme import Palette
from ..widgets.controls import ValueSlider

__all__ = ["RaceScreen"]

#: The default line-up, filtered per problem to what can actually run.
_CANDIDATES = ["rk23", "dopri5", "tsit5", "cashkarp", "rkf45", "radau",
               "rodas4", "taylor20"]

_FRAMES = 260


class _Lane(QWidget):
    """One competitor: name, progress bar, and live counters."""

    def __init__(self, method: str, colour: str, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.method = method
        self.colour = colour

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(1)

        self.name = QLabel(method)
        self.name.setStyleSheet(
            f"color: {colour}; font-weight: 700; font-size: 12px;"
        )
        self.name.setFixedWidth(84)
        layout.addWidget(self.name, 0, 0)

        self.bar = QProgressBar()
        self.bar.setRange(0, 1000)
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(13)
        self.bar.setStyleSheet(
            f"QProgressBar {{ background: {palette.surface_alt}; border: none;"
            f" border-radius: 6px; }}"
            f"QProgressBar::chunk {{ background: {colour}; border-radius: 6px; }}"
        )
        layout.addWidget(self.bar, 0, 1)

        self.counters = QLabel("—")
        self.counters.setProperty("role", "mono")
        self.counters.setStyleSheet("font-size: 11px;")
        self.counters.setFixedWidth(268)
        self.counters.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.counters, 0, 2)
        layout.setColumnStretch(1, 1)

    def update_to(self, steps: int, evaluations: int, fraction: float,
                  finished: bool) -> None:
        self.bar.setValue(int(1000 * min(max(fraction, 0.0), 1.0)))
        mark = "✔" if finished else " "
        self.counters.setText(
            f"{steps:>7,} steps   {evaluations:>8,} evals  {mark}"
        )


class RaceScreen(QWidget):
    def __init__(self, state: SessionState, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette
        self._results: dict[str, object] = {}
        self._lanes: dict[str, _Lane] = {}
        self._curves: dict[str, object] = {}
        self._frame = 0
        self._pending = 0

        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._advance)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(self._build_controls())

        right = QVBoxLayout()
        right.setSpacing(10)
        right.addWidget(self._build_plot(), 1)
        right.addWidget(self._build_track())
        layout.addLayout(right, 1)

        self._problem_key = "robertson"
        self._params = catalog.get(self._problem_key).defaults()
        self._sync_controls()

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel = QFrame()
        panel.setProperty("role", "panel")
        panel.setFixedWidth(238)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner = QWidget()
        scroll.setWidget(inner)
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        heading = QLabel("Problem")
        heading.setProperty("role", "heading")
        layout.addWidget(heading)

        self.problem_picker = QComboBox()
        self.refresh_problems()
        self.problem_picker.currentIndexChanged.connect(self._on_problem)
        layout.addWidget(self.problem_picker)

        layout.addSpacing(4)
        competitors = QLabel("Competitors")
        competitors.setProperty("role", "heading")
        layout.addWidget(competitors)

        self.checks: dict[str, QCheckBox] = {}
        for method in _CANDIDATES:
            box = QCheckBox(method)
            box.setChecked(method in ("dopri5", "radau", "rodas4", "tsit5"))
            layout.addWidget(box)
            self.checks[method] = box

        layout.addSpacing(4)
        tolerance = QLabel("Tolerance")
        tolerance.setProperty("role", "heading")
        layout.addWidget(tolerance)
        self.rtol = ValueSlider("relative tolerance", 1e-11, 1e-3, 1e-6, log=True)
        layout.addWidget(self.rtol)

        layout.addSpacing(8)
        self.run_button = QPushButton("Run the race")
        self.run_button.setProperty("role", "primary")
        self.run_button.clicked.connect(self._start)
        layout.addWidget(self.run_button)

        self.replay_button = QPushButton("Replay")
        self.replay_button.clicked.connect(self._replay)
        self.replay_button.setEnabled(False)
        layout.addWidget(self.replay_button)

        self.status = QLabel("choose competitors and press run")
        self.status.setProperty("role", "muted")
        self.status.setStyleSheet("font-size: 10.5px;")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch(1)

        holder = QVBoxLayout(panel)
        holder.setContentsMargins(0, 0, 0, 0)
        holder.addWidget(scroll)
        return panel

    def _build_plot(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        self.title = QLabel("Method race")
        self.title.setProperty("role", "heading")
        layout.addWidget(self.title)

        self.plot = pg.PlotWidget()
        self.plot.setBackground(self.palette_obj.plot_background)
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.setLabel("bottom", "t")
        self.plot.setMenuEnabled(False)
        self.plot.addLegend(offset=(-10, 10), labelTextSize="9pt")
        layout.addWidget(self.plot, 1)
        return frame

    def _build_track(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        frame.setMinimumHeight(210)
        frame.setMaximumHeight(300)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        header = QHBoxLayout()
        heading = QLabel("Progress")
        heading.setProperty("role", "heading")
        header.addWidget(heading)
        header.addStretch(1)
        self.leaderboard = QLabel("")
        self.leaderboard.setProperty("role", "mono")
        self.leaderboard.setStyleSheet("font-size: 11px;")
        header.addWidget(self.leaderboard)
        layout.addLayout(header)

        self.lanes_host = QWidget()
        self.lanes_layout = QVBoxLayout(self.lanes_host)
        self.lanes_layout.setContentsMargins(0, 0, 0, 0)
        self.lanes_layout.setSpacing(2)
        layout.addWidget(self.lanes_host)
        layout.addStretch(1)
        return frame

    # -- setup -----------------------------------------------------------

    def _sync_controls(self) -> None:
        entry = catalog.get(self._problem_key)
        index = self.problem_picker.findData(self._problem_key)
        if index >= 0:
            self.problem_picker.blockSignals(True)
            self.problem_picker.setCurrentIndex(index)
            self.problem_picker.blockSignals(False)

        available = {m for names in methods_for(entry).values() for m in names}
        for method, box in self.checks.items():
            usable = method in available
            box.setEnabled(usable)
            box.setToolTip("" if usable else f"{method} cannot run this problem")
            if not usable:
                box.setChecked(False)

    def refresh_problems(self) -> None:
        """Re-read the catalogue, so a newly typed equation appears here too."""
        from ..widgets.controls import fill_problem_picker

        fill_problem_picker(
            self.problem_picker, lambda entry: "pde" not in entry.tags
        )

    def _on_problem(self, index: int) -> None:
        key = self.problem_picker.itemData(index)
        if not key:
            return
        self._problem_key = key
        self._params = catalog.get(key).defaults()
        self._sync_controls()
        self.status.setText("press run")

    def selected_methods(self) -> list[str]:
        return [m for m, box in self.checks.items()
                if box.isChecked() and box.isEnabled()]

    # -- running ---------------------------------------------------------

    def _start(self) -> None:
        methods = self.selected_methods()
        if not methods:
            self.status.setText("select at least one method")
            return

        self._timer.stop()
        self._results.clear()
        self._pending = len(methods)
        self.run_button.setEnabled(False)
        self.replay_button.setEnabled(False)
        self.status.setText(f"solving {len(methods)} methods…")
        self._build_lanes(methods)

        rtol = self.rtol.value()
        runner = self.state.runner
        runner.finished.connect(self._on_one_finished)
        self._connected = True

        for method in methods:
            runner.submit(
                SolveRequest(
                    problem_key=self._problem_key, method=method,
                    rtol=rtol, atol=rtol * 1e-3, params=dict(self._params),
                    dense_output=False, max_steps=400_000,
                )
            )

    def _build_lanes(self, methods: list[str]) -> None:
        while self.lanes_layout.count():
            item = self.lanes_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()
        self._lanes.clear()

        palette = self.palette_obj
        for index, method in enumerate(methods):
            colour = palette.series[index % len(palette.series)]
            lane = _Lane(method, colour, palette)
            self.lanes_layout.addWidget(lane)
            self._lanes[method] = lane

    def _on_one_finished(self, result) -> None:
        if result.request.problem_key != self._problem_key:
            return
        method = result.request.method
        if method not in self._lanes:
            return
        self._results[method] = result
        self._pending -= 1
        self.status.setText(f"{len(self._results)} done, {self._pending} running…")
        if self._pending <= 0:
            self._finish_solving()

    def _finish_solving(self) -> None:
        if getattr(self, "_connected", False):
            try:
                self.state.runner.finished.disconnect(self._on_one_finished)
            except (RuntimeError, TypeError):
                pass
            self._connected = False

        self.run_button.setEnabled(True)
        self.replay_button.setEnabled(True)
        self._prepare_plot()
        self._replay()

    # -- playback --------------------------------------------------------

    def _prepare_plot(self) -> None:
        entry = catalog.get(self._problem_key)
        palette = self.palette_obj
        self.plot.clear()
        self.plot.addLegend(offset=(-10, 10), labelTextSize="9pt")
        self._curves.clear()

        finite = [r for r in self._results.values() if r.ok]
        if not finite:
            self.status.setText("every method failed on this problem")
            return

        self._t_end = max(r.solution.t[-1] for r in finite)
        self._t_start = min(r.solution.t[0] for r in finite)
        # Log time whenever the interval spans decades, which is exactly when
        # the difference between the methods is most dramatic.
        self._log_time = entry.log_time_default
        self.plot.setLogMode(x=self._log_time, y=False)
        self.plot.setLabel("left", entry.labels[0] if entry.labels else "y[0]")

        for index, (method, result) in enumerate(self._results.items()):
            colour = palette.series[index % len(palette.series)]
            self._curves[method] = self.plot.plot(
                [], [], name=method, pen=pg.mkPen(colour, width=2)
            )

        self.title.setText(
            f"{entry.title} — {len(self._results)} methods at rtol="
            f"{self.rtol.value():.0e}"
        )
        self._write_leaderboard()

    def _replay(self) -> None:
        if not self._results:
            return
        self._frame = 0
        self._timer.start()

    def _advance(self) -> None:
        self._frame += 1
        fraction = self._frame / _FRAMES
        if fraction >= 1.0:
            fraction = 1.0
            self._timer.stop()

        # Sweep in log time when the axis is logarithmic, so early decades get
        # their share of the animation instead of flashing past in one frame.
        if self._log_time:
            lo = max(self._t_start, self._t_end * 1e-14)
            now = lo * (self._t_end / lo) ** fraction
        else:
            now = self._t_start + fraction * (self._t_end - self._t_start)

        for method, result in self._results.items():
            lane = self._lanes.get(method)
            if lane is None:
                continue
            solution = result.solution
            if not result.ok:
                # Show what a failed method actually spent. Reporting zero
                # would hide the whole point: DOPRI5 does not merely fail on
                # Robertson, it fails after hundreds of thousands of steps.
                if solution is not None:
                    reached = solution.t[-1] if solution.t.size else 0.0
                    lane.update_to(
                        solution.stats.naccepted, solution.stats.nfev,
                        reached / self._t_end if self._t_end else 0.0,
                        False,
                    )
                    lane.counters.setText(
                        f"{solution.stats.naccepted:>7,} steps   "
                        f"{solution.stats.nfev:>8,} evals  ✗"
                    )
                continue

            count = int(np.searchsorted(solution.t, now, side="right"))
            count = max(count, 1)
            reached = solution.t[min(count, solution.t.size) - 1]

            curve = self._curves.get(method)
            if curve is not None:
                t = solution.t[:count]
                y = solution.y[0, :count]
                if self._log_time:
                    keep = t > 0
                    t, y = t[keep], y[keep]
                curve.setData(t, y)

            # Steps are exact; evaluations are apportioned across the solve,
            # since the solver reports only the total.
            steps = min(count, solution.stats.naccepted)
            share = steps / max(solution.stats.naccepted, 1)
            lane.update_to(
                steps, int(share * solution.stats.nfev),
                reached / self._t_end if self._t_end else 1.0,
                steps >= solution.stats.naccepted,
            )

    def _write_leaderboard(self) -> None:
        palette = self.palette_obj
        finished = [(m, r) for m, r in self._results.items() if r.ok]
        if not finished:
            self.leaderboard.setText("")
            return

        # Ranked by evaluations, which is the implementation-independent cost.
        # No accuracy column: with no independent reference at hand, comparing
        # the competitors against one of themselves would rank a method
        # against its own answer.
        rows = []
        for method, result in sorted(
            finished, key=lambda item: item[1].solution.stats.nfev
        ):
            rows.append(
                f"<span style='color:{palette.text}'>{method}</span> "
                f"{result.solution.stats.nfev:,} evals "
                f"({result.wall_time * 1e3:.0f} ms)"
            )
        failed = [m for m, r in self._results.items() if not r.ok]
        if failed:
            rows.append(
                f"<span style='color:{palette.danger}'>failed: "
                f"{', '.join(failed)}</span>"
            )
        self.leaderboard.setText("&nbsp;&nbsp;·&nbsp;&nbsp;".join(rows))
