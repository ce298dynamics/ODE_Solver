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
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import analysis, catalog, continuation, theme
from ..state import SessionState
from ..theme import Palette
from ..widgets.controls import ParameterPanel, add_heading, control_panel

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
    done = Signal(object, object)          # PortraitData, token
    diagram = Signal(object, object)       # continuation.Diagram, token


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


class _ContinuationJob(QRunnable):
    """A parameter sweep, off the interface thread.

    A sweep is a Newton solve at each of 161 parameter values plus a bisection
    at every crossing -- a few hundred milliseconds for a planar system, which
    is the same order as the portrait itself and belongs in the same pool for
    the same reason.

    Unlike the portrait, this one is not recomputed as a slider moves: the
    diagram *is* the slider's whole range, so moving the slider does not change
    it. It is drawn on request, and the request is a button.
    """

    def __init__(self, entry, parameter, token, signals) -> None:
        super().__init__()
        self.entry, self.parameter = entry, parameter
        self.token, self.signals = token, signals

    def run(self) -> None:
        try:
            diagram = continuation.sweep(self.entry, self.parameter)
        except Exception as exc:                # noqa: BLE001 - reported, not raised
            diagram = exc
        try:
            self.signals.diagram.emit(diagram, self.token)
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
        self._diagram: continuation.Diagram | None = None
        self._diagram_token = 0
        self._signals = _Signals()
        self._signals.done.connect(self._on_analysis)
        self._signals.diagram.connect(self._on_diagram)
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
        panel, layout = control_panel(250)

        add_heading(layout, "System")

        self.picker = QComboBox()
        self.picker.setAccessibleName("system")
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
        self.blurb.setStyleSheet(theme.scaled("font-size: 11px;"))
        layout.addWidget(self.blurb)

        add_heading(layout, "Parameters", space_above=6)

        self.parameters = ParameterPanel()
        self.parameters.changed.connect(self._on_param)
        layout.addWidget(self.parameters)

        add_heading(layout, "Layers", space_above=6)

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
        hint.setStyleSheet(theme.scaled("font-size: 11px;"))
        layout.addWidget(hint)

        clear = QPushButton("Clear trajectories")
        clear.clicked.connect(self._clear_trajectories)
        layout.addWidget(clear)

        rescale = QPushButton("Reset view")
        rescale.clicked.connect(lambda: self._recompute(reset_window=True))
        layout.addWidget(rescale)

        self.status = QLabel("")
        self.status.setProperty("role", "muted")
        self.status.setStyleSheet(theme.scaled("font-size: 10.5px;"))
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch(1)
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
        self.legend_label.setStyleSheet(theme.scaled("font-size: 10.5px;"))
        header.addWidget(self.legend_label)
        layout.addLayout(header)

        self.plot = pg.PlotWidget()
        self.plot.setAccessibleName("phase portrait")
        self.plot.setBackground(self.palette_obj.plot_background)
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.setMenuEnabled(False)
        self.plot.scene().sigMouseClicked.connect(self._on_click)

        # Two tabs rather than two screens. The portrait and the diagram are
        # the same system asked two questions -- "what does it do here" and
        # "what does it do as I turn this" -- and the second is only ever asked
        # by someone already looking at the first. Splitting them across the
        # navigation would put the parameter sliders on one screen and the
        # picture of what they do on another.
        self.views = QTabWidget()
        self.views.setAccessibleName("portrait or bifurcation diagram")
        self.views.addTab(self.plot, "Portrait")
        self.views.addTab(self._build_bifurcation(), "Bifurcation")
        layout.addWidget(self.views, 1)
        return frame

    def _build_bifurcation(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(6)

        row = QHBoxLayout()
        row.addWidget(QLabel("Sweep"))
        self.sweep_param = QComboBox()
        self.sweep_param.setAccessibleName("parameter to sweep")
        self.sweep_param.setMinimumWidth(130)
        row.addWidget(self.sweep_param)
        self.sweep_button = QPushButton("Draw diagram")
        self.sweep_button.clicked.connect(self._draw_diagram)
        row.addWidget(self.sweep_button)
        row.addStretch(1)
        self.sweep_legend = QLabel("solid = stable · dashed = unstable")
        self.sweep_legend.setProperty("role", "muted")
        self.sweep_legend.setStyleSheet(theme.scaled("font-size: 10.5px;"))
        row.addWidget(self.sweep_legend)
        layout.addLayout(row)

        self.sweep_plot = pg.PlotWidget()
        self.sweep_plot.setAccessibleName("bifurcation diagram")
        self.sweep_plot.setBackground(self.palette_obj.plot_background)
        self.sweep_plot.showGrid(x=True, y=True, alpha=0.15)
        self.sweep_plot.setMenuEnabled(False)
        layout.addWidget(self.sweep_plot, 1)

        self.sweep_note = QLabel("")
        self.sweep_note.setProperty("role", "muted")
        self.sweep_note.setStyleSheet(theme.scaled("font-size: 10.5px;"))
        self.sweep_note.setWordWrap(True)
        layout.addWidget(self.sweep_note)
        return page

    def _build_report(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        frame.setMaximumHeight(132)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(3)

        add_heading(layout, "Equilibria")

        self.report = QLabel("—")
        self.report.setProperty("role", "mono")
        self.report.setStyleSheet(theme.scaled("font-size: 11px;"))
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
        self._refresh_sweep_parameters(entry)
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

    # -- the bifurcation diagram -----------------------------------------

    #: Sliders that are not worth a diagram.
    #:
    #: Duration and the initial condition move the *trajectory*, and the
    #: equilibria do not depend on either -- a diagram over `t_end` is a set of
    #: flat lines, which is a true picture of nothing. Excluded by name rather
    #: than by asking whether the answer comes out flat, because a flat diagram
    #: over a parameter that *could* have moved the equilibria is a real result
    #: worth seeing.
    _NOT_WORTH_SWEEPING = frozenset({"t_end", "initial", "duration"})

    def _refresh_sweep_parameters(self, entry) -> None:
        self.sweep_param.blockSignals(True)
        self.sweep_param.clear()
        for spec in entry.params:
            if spec.name in self._NOT_WORTH_SWEEPING:
                continue
            self.sweep_param.addItem(spec.label, spec.name)
        self.sweep_param.blockSignals(False)

        usable = self.sweep_param.count() > 0
        self.sweep_button.setEnabled(usable)
        self._diagram = None
        self.sweep_plot.clear()
        self.sweep_note.setText(
            "" if usable else
            f"{entry.title} has no parameter whose value moves the equilibria."
        )

    def _draw_diagram(self) -> None:
        name = self.sweep_param.currentData()
        if not name:
            return
        self._diagram_token += 1
        self.sweep_button.setEnabled(False)
        self.sweep_note.setText("sweeping…")
        QThreadPool.globalInstance().start(
            _ContinuationJob(self.entry, name, self._diagram_token, self._signals)
        )

    def _on_diagram(self, diagram, token: int) -> None:
        if token != self._diagram_token:
            return                      # a newer sweep has been asked for
        self.sweep_button.setEnabled(True)
        if isinstance(diagram, Exception):
            self._diagram = None
            self.sweep_plot.clear()
            self.sweep_note.setText(f"the sweep failed: {diagram}")
            return
        self._diagram = diagram
        self._render_diagram()

    def _render_diagram(self) -> None:
        diagram, palette = self._diagram, self.palette_obj
        if diagram is None:
            return

        self.sweep_plot.clear()
        entry = self.entry
        axis = entry.phase_axes[0] if entry.phase_axes else 0
        label = entry.labels[axis] if axis < len(entry.labels) else "state"
        self.sweep_plot.setLabel("bottom", diagram.parameter)
        self.sweep_plot.setLabel("left", label)

        solid = pg.mkPen(palette.accent, width=2)
        dashed = pg.mkPen(palette.text_muted, width=2, style=Qt.DashLine)

        for branch in diagram.branches:
            parameters, coordinate = branch.parameters, branch.coordinate(axis)
            for stability, low, high in branch.segments():
                pen = solid if stability == analysis.STABLE else dashed
                self.sweep_plot.plot(parameters[low:high], coordinate[low:high],
                                     pen=pen)

        for found in diagram.bifurcations:
            value = float(found.position[axis]) if axis < len(found.position) else 0.0
            self.sweep_plot.plot(
                [found.parameter], [value], pen=None, symbol="o", symbolSize=9,
                symbolBrush=palette.warning, symbolPen=palette.warning,
            )
            text = pg.TextItem(found.kind, color=palette.warning, anchor=(0.5, 1.4))
            text.setPos(found.parameter, value)
            self.sweep_plot.addItem(text)

        self.sweep_note.setText(self._diagram_note(diagram))

    def _diagram_note(self, diagram) -> str:
        parts = []
        if diagram.bifurcations:
            for found in diagram.bifurcations:
                parts.append(
                    f"<b>{found.kind}</b> at {diagram.parameter} = "
                    f"{found.parameter:.4g} — {found.detail}"
                )
        else:
            parts.append(
                f"No bifurcation over this range of {diagram.parameter}: the "
                "equilibria move, but none appears, vanishes or changes "
                "stability."
            )
        if diagram.clipped:
            parts.append(
                "A branch left the search window rather than ceasing to "
                "exist — where it stops is a fact about the box, not the "
                "system."
            )
        parts.append(diagram.method_note)
        return "<br>".join(parts)

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
            # A11Y-03. Colour alone was red against green -- the pairing
            # red-green colour blindness collapses -- although this file already
            # encodes equilibria by marker shape for exactly that reason. The
            # unstable manifold is dash-dot rather than dashed because the
            # nullclines already have dashes, and a third line that matched
            # them in pattern would only move the ambiguity.
            for path, label in data.separatrices:
                unstable = label == "unstable"
                self.plot.plot(
                    path[:, 0], path[:, 1],
                    pen=pg.mkPen(palette.danger if unstable else palette.success,
                                 width=2.2,
                                 style=Qt.DashDotLine if unstable else Qt.SolidLine),
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
            f"<span style='color:{palette.danger}'>-·-</span> unstable manifold "
            f"&nbsp;<span style='color:{palette.success}'>——</span> stable manifold"
        )
        self._write_report()
        self._describe_plot()

    def _describe_plot(self) -> None:
        """The portrait in words, as the plot's alternative text.

        Everything in it is already computed -- `analysis` names each
        equilibrium and classifies it -- so this is a rewriting of the report
        beside the picture into a sentence, not a second analysis that could
        disagree with the first.
        """
        data, entry = self._data, self.entry
        if data is None or entry is None:
            self.plot.setAccessibleName("phase portrait")
            self.plot.setAccessibleDescription("Nothing has been analysed yet.")
            return

        names = entry.labels if entry.labels else ("x", "y")
        where = (f"{names[0]} from {data.xlim[0]:.3g} to {data.xlim[1]:.3g} and "
                 f"{names[1] if len(names) > 1 else 'y'} from "
                 f"{data.ylim[0]:.3g} to {data.ylim[1]:.3g}")
        if not data.fixed_points:
            found = "No equilibria lie in this window."
        else:
            found = " ".join(
                f"A {point.kind} at ({point.position[0]:+.4f}, "
                f"{point.position[1]:+.4f}), "
                + ("classified from the linearisation only, since an "
                   "eigenvalue lies on the imaginary axis."
                   if not point.hyperbolic else f"{point.stability}.")
                for point in data.fixed_points
            )
            found = (f"{len(data.fixed_points)} equilibri"
                     f"{'um' if len(data.fixed_points) == 1 else 'a'}. {found}")
        self.plot.setAccessibleName(f"phase portrait of {entry.title}")
        self.plot.setAccessibleDescription(
            f"{entry.title}: the vector field over {where}, with nullclines "
            f"and the trajectories through any points clicked. {found}"
        )

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
            # A name for a non-hyperbolic point is a claim about the
            # linearisation, not about the flow: with an eigenvalue on the
            # imaginary axis, Hartman-Grobman does not apply and the
            # higher-order terms decide. "centre" is the case that bites --
            # Lotka-Volterra really is one, and x' = -y + x(x²+y²) has the same
            # eigenvalues and spirals outward. Printing the word alone, in
            # bold, tells the reader the wrong thing half the time.
            caveat = (
                ""
                if point.hyperbolic
                else "&nbsp;&nbsp;<i>(from the linearisation only — an "
                     "eigenvalue lies on the imaginary axis, so the "
                     "higher-order terms decide)</i>"
            )
            rows.append(
                f"({point.position[0]:+.4f},&nbsp;{point.position[1]:+.4f})&nbsp;&nbsp;"
                f"<span style='color:{colour}'><b>{point.kind}</b></span>"
                f"&nbsp;&nbsp;λ&nbsp;=&nbsp;{values}{caveat}"
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
