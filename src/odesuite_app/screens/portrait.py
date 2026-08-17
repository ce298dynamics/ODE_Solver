"""Phase Portrait Studio.

A planar autonomous system laid out as a picture of its flow: streamlines,
nullclines, equilibria classified by the Jacobian's eigenvalues, and the
separatrices out of every saddle. Click anywhere to launch a trajectory through
that point -- forwards *and* backwards, which is what makes it the curve through
the point rather than merely the curve after it.

The analysis runs on a worker thread. Recomputing a portrait costs a few hundred
milliseconds, which is imperceptible when it happens off the interface thread
and intolerable when it does not: the parameter sliders are meant to be dragged,
and watching a pitchfork bifurcation happen is the point of having them.
"""

from __future__ import annotations

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
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import analysis, catalog
from ..state import SessionState
from ..theme import Palette
from ..widgets.controls import ParameterPanel

__all__ = ["PortraitScreen"]

#: Marker shape per equilibrium type. Shape carries the classification as well
#: as colour, so it survives greyscale and colour-vision deficiency.
_MARKERS = {
    "saddle": "x",
    "stable node": "o",
    "unstable node": "o",
    "stable spiral": "s",
    "unstable spiral": "s",
    "centre": "d",
    "non-hyperbolic": "t",
}


class _Signals(QObject):
    done = Signal(object, object)      # PortraitData, token


class _AnalysisJob(QRunnable):
    def __init__(self, problem, xlim, ylim, options, token, signals) -> None:
        super().__init__()
        self.problem, self.xlim, self.ylim = problem, xlim, ylim
        self.options, self.token, self.signals = options, token, signals

    def run(self) -> None:
        try:
            data = analysis.analyse(
                self.problem, self.xlim, self.ylim, **self.options
            )
        except Exception:
            data = None
        try:
            self.signals.done.emit(data, self.token)
        except RuntimeError:
            pass                        # the screen went away mid-computation


class PortraitScreen(QWidget):
    def __init__(self, state: SessionState, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette
        self._token = 0
        self._data: analysis.PortraitData | None = None
        self._trajectories: list = []
        self._launched = 0
        self._signals = _Signals()
        self._signals.done.connect(self._on_analysis)
        self.destroyed.connect(lambda *_: setattr(self, "_token", -1))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        layout.addWidget(self._build_controls())

        right = QVBoxLayout()
        right.setSpacing(10)
        right.addWidget(self._build_plot(), 1)
        right.addWidget(self._build_report())
        layout.addLayout(right, 1)

        self._pick_initial_problem()

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel = QFrame()
        panel.setProperty("role", "panel")
        panel.setFixedWidth(250)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner = QWidget()
        scroll.setWidget(inner)
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        heading = QLabel("System")
        heading.setProperty("role", "heading")
        layout.addWidget(heading)

        self.picker = QComboBox()
        # Only planar autonomous systems have a phase portrait in this sense.
        # `autonomous_2d` is the honest gate: a static vector field only means
        # anything when the right-hand side does not depend on t. A typed
        # equation answers it like any other entry, so a forced one is kept out
        # of this screen rather than drawn against a field it does not obey.
        self.refresh_problems()
        self.picker.currentIndexChanged.connect(self._on_problem_picked)
        layout.addWidget(self.picker)

        self.blurb = QLabel("")
        self.blurb.setWordWrap(True)
        self.blurb.setProperty("role", "muted")
        self.blurb.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.blurb)

        layout.addSpacing(6)
        parameters = QLabel("Parameters")
        parameters.setProperty("role", "heading")
        layout.addWidget(parameters)

        self.parameters = ParameterPanel()
        self.parameters.changed.connect(self._on_param)
        layout.addWidget(self.parameters)

        layout.addSpacing(6)
        layers = QLabel("Layers")
        layers.setProperty("role", "heading")
        layout.addWidget(layers)

        self.toggles: dict[str, QCheckBox] = {}
        for key, label, tip, default in [
            ("field", "vector field",
             "Evenly spaced streamlines of the flow", True),
            ("nullclines", "nullclines",
             "Curves where each derivative vanishes; they cross at the "
             "equilibria", True),
            ("fixed", "fixed points",
             "Equilibria, classified by the Jacobian's eigenvalues", True),
            ("separatrices", "separatrices",
             "Stable and unstable manifolds of each saddle — the boundaries "
             "between qualitatively different behaviour", True),
        ]:
            box = QCheckBox(label)
            box.setChecked(default)
            box.setToolTip(tip)
            box.toggled.connect(self._on_layer_toggled)
            layout.addWidget(box)
            self.toggles[key] = box

        layout.addSpacing(10)
        hint = QLabel("Click the plot to launch a trajectory through that point.")
        hint.setWordWrap(True)
        hint.setProperty("role", "muted")
        hint.setStyleSheet("font-size: 11px;")
        layout.addWidget(hint)

        clear = QPushButton("Clear trajectories")
        clear.clicked.connect(self._clear_trajectories)
        layout.addWidget(clear)

        rescale = QPushButton("Reset view")
        rescale.clicked.connect(lambda: self._recompute(reset_window=True))
        layout.addWidget(rescale)

        self.status = QLabel("")
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

        header = QHBoxLayout()
        self.title = QLabel("Phase portrait")
        self.title.setProperty("role", "heading")
        header.addWidget(self.title)
        header.addStretch(1)
        self.legend_label = QLabel("")
        self.legend_label.setStyleSheet("font-size: 10.5px;")
        header.addWidget(self.legend_label)
        layout.addLayout(header)

        self.plot = pg.PlotWidget()
        self.plot.setBackground(self.palette_obj.plot_background)
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.setMenuEnabled(False)
        self.plot.scene().sigMouseClicked.connect(self._on_click)
        layout.addWidget(self.plot, 1)
        return frame

    def _build_report(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        frame.setMaximumHeight(132)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(3)

        heading = QLabel("Equilibria")
        heading.setProperty("role", "heading")
        layout.addWidget(heading)

        self.report = QLabel("—")
        self.report.setProperty("role", "mono")
        self.report.setStyleSheet("font-size: 11px;")
        self.report.setTextFormat(Qt.RichText)
        self.report.setWordWrap(True)
        self.report.setAlignment(Qt.AlignTop)
        layout.addWidget(self.report, 1)
        return frame

    # -- problem selection -----------------------------------------------

    def _pick_initial_problem(self) -> None:
        key = self.state.problem_key
        index = self.picker.findData(key)
        if index < 0:
            # The session is on a problem with no planar portrait; fall back
            # to the pendulum rather than showing an empty screen.
            index = max(self.picker.findData("pendulum"), 0)
        self.picker.setCurrentIndex(index)
        self._on_problem_picked(index)

    def refresh_problems(self) -> None:
        """Re-read the catalogue, so a newly typed equation appears here too."""
        from ..widgets.controls import fill_problem_picker

        fill_problem_picker(self.picker, lambda entry: entry.autonomous_2d)

    def _on_problem_picked(self, index: int) -> None:
        key = self.picker.itemData(index)
        if not key:
            return
        entry = catalog.get(key)
        self.blurb.setText(entry.blurb)
        self._params = entry.defaults()
        self.parameters.rebuild(entry, self._params)
        self._clear_trajectories()
        self._recompute(reset_window=True)

    def _on_param(self, name: str, value: float) -> None:
        self._params[name] = value
        self._recompute(reset_window=False)

    def _on_layer_toggled(self, _checked: bool) -> None:
        if self._data is not None:
            self._render()

    @property
    def entry(self):
        return catalog.get(self.picker.currentData())

    # -- analysis --------------------------------------------------------

    def _window(self, reset: bool):
        if not reset and self._data is not None:
            return self._data.xlim, self._data.ylim

        entry = self.entry
        problem = entry.build(self._params)
        # Frame the window on a representative trajectory rather than guessing
        # at bounds: it puts the interesting structure on screen for a limit
        # cycle and an orbit alike.
        from odesuite import solve

        try:
            solution = solve(
                problem.problem, method="dopri5", rtol=1e-6, atol=1e-9,
                max_steps=50_000,
            )
        except Exception:
            solution = None
        return analysis.default_window(problem.problem, solution)

    def _recompute(self, reset_window: bool = False) -> None:
        entry = self.entry
        bench = entry.build(self._params)
        xlim, ylim = self._window(reset_window)

        self._token += 1
        self.status.setText("analysing…")
        options = dict(
            with_streamlines=self.toggles["field"].isChecked(),
            with_nullclines=self.toggles["nullclines"].isChecked(),
            with_separatrices=self.toggles["separatrices"].isChecked(),
        )
        QThreadPool.globalInstance().start(
            _AnalysisJob(
                bench.problem, xlim, ylim, options, self._token, self._signals
            )
        )

    def _on_analysis(self, data, token: int) -> None:
        if token != self._token:
            return                      # a newer parameter value has arrived
        if data is None:
            self.status.setText("analysis failed")
            return
        self._data = data
        self.status.setText("")
        self._render()

    # -- rendering -------------------------------------------------------

    def _render(self) -> None:
        data, palette = self._data, self.palette_obj
        if data is None:
            return

        self.plot.clear()
        self._trajectories.clear()
        self._launched = 0

        if self.toggles["field"].isChecked():
            for index, path in enumerate(data.streamlines):
                self.plot.plot(
                    path[:, 0], path[:, 1],
                    pen=pg.mkPen(palette.text_muted, width=1.1),
                ).setOpacity(0.75)
                # A streamline is a curve, not a direction. Arrowheads on a
                # subset restore the sense of the flow without the clutter of
                # arming every line.
                if index % 2 or len(path) < 8:
                    continue
                middle = len(path) // 2
                tail, head = path[middle - 1], path[middle + 1]
                delta = head - tail
                if not np.any(delta):
                    continue
                self.plot.addItem(
                    pg.ArrowItem(
                        pos=(float(path[middle][0]), float(path[middle][1])),
                        # pyqtgraph measures the angle to the arrow's tail, so
                        # it runs opposite to the direction of travel.
                        angle=float(
                            180.0 - np.degrees(np.arctan2(delta[1], delta[0]))
                        ),
                        headLen=9, tipAngle=32, pxMode=True,
                        brush=pg.mkBrush(palette.text_muted),
                        pen=None,
                    )
                )

        if self.toggles["nullclines"].isChecked():
            for path in data.nullcline_x:
                self.plot.plot(
                    path[:, 0], path[:, 1],
                    pen=pg.mkPen(palette.series[0], width=1.6, style=Qt.DashLine),
                )
            for path in data.nullcline_y:
                self.plot.plot(
                    path[:, 0], path[:, 1],
                    pen=pg.mkPen(palette.series[1], width=1.6, style=Qt.DashLine),
                )

        if self.toggles["separatrices"].isChecked():
            for path, label in data.separatrices:
                colour = palette.danger if label == "unstable" else palette.success
                self.plot.plot(
                    path[:, 0], path[:, 1], pen=pg.mkPen(colour, width=2.2)
                )

        if self.toggles["fixed"].isChecked():
            for point in data.fixed_points:
                colour = {
                    "stable": palette.success,
                    "unstable": palette.danger,
                }.get(point.stability, palette.warning)
                self.plot.plot(
                    [point.position[0]], [point.position[1]],
                    pen=None, symbol=_MARKERS.get(point.kind, "o"), symbolSize=13,
                    symbolPen=pg.mkPen(colour, width=2.2),
                    symbolBrush=pg.mkBrush(colour) if point.stability == "stable"
                    else None,
                )

        self.plot.setXRange(*data.xlim, padding=0.02)
        self.plot.setYRange(*data.ylim, padding=0.02)
        entry = self.entry
        self.plot.setLabel("bottom", entry.labels[0] if entry.labels else "x")
        self.plot.setLabel("left", entry.labels[1] if len(entry.labels) > 1 else "y")
        self.title.setText(f"{entry.title} — phase portrait")

        self.legend_label.setText(
            f"<span style='color:{palette.series[0]}'>--</span> nullcline "
            f"{entry.labels[0] if entry.labels else 'x'}′=0 &nbsp; "
            f"<span style='color:{palette.series[1]}'>--</span> "
            f"{entry.labels[1] if len(entry.labels) > 1 else 'y'}′=0 &nbsp; "
            f"<span style='color:{palette.danger}'>—</span> unstable manifold "
            f"&nbsp;<span style='color:{palette.success}'>—</span> stable manifold"
        )
        self._write_report()

    def _write_report(self) -> None:
        data, palette = self._data, self.palette_obj
        if data is None or not data.fixed_points:
            self.report.setText(
                "<i>no equilibria in this window</i>"
                if data is not None else "—"
            )
            return

        rows = []
        for point in data.fixed_points:
            colour = {
                "stable": palette.success, "unstable": palette.danger,
            }.get(point.stability, palette.warning)
            values = ",&nbsp;".join(
                f"{v.real:+.3f}{v.imag:+.3f}i" if abs(v.imag) > 1e-9
                else f"{v.real:+.3f}"
                for v in point.eigenvalues
            )
            rows.append(
                f"({point.position[0]:+.4f},&nbsp;{point.position[1]:+.4f})&nbsp;&nbsp;"
                f"<span style='color:{colour}'><b>{point.kind}</b></span>"
                f"&nbsp;&nbsp;λ&nbsp;=&nbsp;{values}"
            )
        self.report.setText("<br>".join(rows))

    # -- interaction -----------------------------------------------------

    def _on_click(self, event) -> None:
        if event.button() != Qt.LeftButton or self._data is None:
            return
        view = self.plot.plotItem.vb
        point = view.mapSceneToView(event.scenePos())
        self._launch(float(point.x()), float(point.y()))

    def _launch(self, x: float, y: float) -> None:
        entry = self.entry
        bench = entry.build(self._params)
        data = self._data
        span = 4.0 * max(
            data.xlim[1] - data.xlim[0], data.ylim[1] - data.ylim[0]
        ) if data else 40.0

        curve = analysis.trajectory_through(
            bench.problem, (x, y), span=min(span, 200.0), backward=True
        )
        if curve.size == 0:
            return

        # Deliberately not the green or red used for the stable and unstable
        # manifolds: a launched trajectory drawn in manifold colours reads as
        # part of the skeleton rather than as something the user added.
        palette = self.palette_obj
        trajectory_colours = [
            palette.series[i] for i in (3, 5, 4, 6, 1)
            if i < len(palette.series)
        ]
        colour = trajectory_colours[self._launched % len(trajectory_colours)]
        pieces = analysis.clip_to_window(curve, data.xlim, data.ylim) if data else [curve]
        if not pieces:
            return
        for piece in pieces:
            self._trajectories.append(
                self.plot.plot(
                    piece[:, 0], piece[:, 1], pen=pg.mkPen(colour, width=2.0)
                )
            )
        self._trajectories.append(
            self.plot.plot(
                [x], [y], pen=None, symbol="o", symbolSize=7,
                symbolPen=None, symbolBrush=pg.mkBrush(colour),
            )
        )
        self._launched += 1
        self.status.setText(
            f"trajectory through ({x:.3f}, {y:.3f}) — {self._launched} drawn"
        )

    def _clear_trajectories(self) -> None:
        for item in self._trajectories:
            try:
                self.plot.removeItem(item)
            except Exception:
                pass
        self._trajectories.clear()
        self._launched = 0
        self.status.setText("")
