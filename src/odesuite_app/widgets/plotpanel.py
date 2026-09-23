"""The main trajectory plot.

Draws the solution from the **dense output**, not from the accepted step points.
That distinction is the whole reason the library's continuous extension exists
and it shows here directly: a Taylor-20 solve of Kepler takes about sixty steps,
and joining sixty points with straight lines would look like a polygon. Sampling
the interpolant instead gives a smooth curve at any zoom level, and the step
points can then be drawn *on top* — so the picture shows both the true
trajectory and how sparsely the solver needed to sample it.

Beside the picture, in words and in numbers. A plot is the one representation
of a solution this application cannot hand to somebody who is not looking at
it, and until now that is exactly what it did: no alternative text, no table,
nothing. So the panel carries three views of the same solve -- the curve, a
paragraph describing what the curve does (`describe.summarise`, which measures
rather than asserts), and the output points as a table that can be arrowed
through and copied. The paragraph is also the plot's accessible description,
which is what a screen reader reads in place of the image.
"""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QGuiApplication, QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableView,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import analysis, describe, theme
from ..theme import Palette
from .flow import FlowWidget

__all__ = ["PlotPanel"]

#: Samples used to render a dense curve. Far more than any solver takes, which
#: is the point.
_DENSE_SAMPLES = 2400


class _ComponentChip(QPushButton):
    """A toggle for one component, carrying that component's colour.

    Doubles as the legend, which is why it is coloured and why the plot's own
    legend is suppressed while these are showing -- two lists of the same names
    beside each other would be clutter, and only one of them can be clicked.
    """

    def __init__(self, label: str, colour: str, muted: str, parent=None) -> None:
        super().__init__(parent)
        self.label = label
        self.colour = colour
        self.muted = muted
        self.setCheckable(True)
        self.setChecked(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(f"Show or hide {label}")
        self.toggled.connect(lambda _: self._restyle())
        self._restyle()

    def _restyle(self) -> None:
        on = self.isChecked()
        self.setText(f"{'●' if on else '○'}  {self.label}")
        colour = self.colour if on else self.muted
        self.setStyleSheet(
            theme.scaled(f"QPushButton {{"
                         f" background: transparent; border: 1px solid"
                         f" {'transparent' if not on else colour + '55'};"
                         f" border-radius: 10px; padding: 2px 9px;"
                         f" font-size: 11.5px; color: {colour}; }}"
                         f"QPushButton:hover {{ border-color: {colour}; }}")
        )


class _SolutionModel(QAbstractTableModel):
    """``(t, y₁ … yₙ)`` at the output times, as a table.

    A model rather than a filled `QTableWidget`: Robertson to t = 1e11 has
    tens of thousands of output points, and building a widget item for each of
    them costs more than the solve did. A model is asked only for the rows
    that are on screen.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._t = np.empty(0)
        self._y = np.empty((0, 0))
        self._labels: tuple[str, ...] = ()

    def set_solution(self, t, y, labels=()) -> None:
        self.beginResetModel()
        self._t = np.asarray(t, dtype=float)
        self._y = np.atleast_2d(np.asarray(y, dtype=float))
        self._labels = tuple(labels)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else int(self._t.size)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else int(self._y.shape[0]) + 1

    def column_name(self, column: int) -> str:
        if column == 0:
            return "t"
        index = column - 1
        return (self._labels[index] if index < len(self._labels)
                else f"y[{index}]")

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role not in (Qt.DisplayRole, Qt.AccessibleTextRole):
            return None
        row, column = index.row(), index.column()
        value = (self._t[row] if column == 0 else self._y[column - 1, row])
        text = f"{float(value):.6g}"
        if role == Qt.AccessibleTextRole:
            return f"{self.column_name(column)} {text}"
        return text

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.column_name(section)
        return str(section + 1)

class _SolutionTable(QTableView):
    """The table view, with the one thing a table owes its reader: copying.

    Qt gives a view selection and navigation for free and copying not at all,
    so `Ctrl+C` is wired here. Tab-separated, which is what a spreadsheet
    expects when text is pasted into it.
    """

    def keyPressEvent(self, event) -> None:
        if event.matches(QKeySequence.Copy):
            self.copy_selection()
            event.accept()
            return
        super().keyPressEvent(event)

    def copy_selection(self) -> str:
        """Put the selected cells on the clipboard, and return what was put."""
        chosen = self.selectedIndexes()
        if not chosen:
            return ""
        rows = sorted({index.row() for index in chosen})
        columns = sorted({index.column() for index in chosen})
        table = {(index.row(), index.column()): index.data() for index in chosen}
        text = "\n".join(
            "\t".join(str(table.get((row, column), "")) for column in columns)
            for row in rows
        )
        QGuiApplication.clipboard().setText(text)
        return text


class PlotPanel(QFrame):
    """Trajectory display, switching form to suit the problem."""

    view_changed = Signal(str)

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette
        self.setProperty("role", "panel")
        self._image = None
        self._colourbar = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        header = QHBoxLayout()
        self.title = QLabel("—")
        self.title.setProperty("role", "heading")
        header.addWidget(self.title)
        header.addStretch(1)

        self.view = QComboBox()
        self.view.addItems(["Auto", "Time series", "Phase", "Components"])
        self.view.setFixedWidth(118)
        self.view.currentTextChanged.connect(
            lambda text: self.view_changed.emit(text)
        )
        header.addWidget(self.view)

        self.show_steps = QCheckBox("step points")
        self.show_steps.setChecked(True)
        self.show_steps.setToolTip(
            "Mark where the solver actually stopped. The curve itself comes "
            "from the dense output, so it stays smooth however few steps "
            "were taken."
        )
        header.addWidget(self.show_steps)

        self.log_time = QCheckBox("log t")
        self.log_time.setToolTip(
            "Essential for problems spanning many decades of time, such as "
            "Robertson to t = 1e11."
        )
        header.addWidget(self.log_time)

        # Only meaningful for a scalar equation, so it appears only then --
        # see `_redraw`.
        self.show_slope_field = QCheckBox("slope field")
        self.show_slope_field.setToolTip(
            "The slope y′ = f(t, y) at each point. Every solution of the "
            "equation runs tangent to it, whatever its initial value."
        )
        self.show_slope_field.setVisible(False)
        header.addWidget(self.show_slope_field)

        header.addSpacing(4)
        layout.addLayout(header)

        # One chip per component, wrapping. Wrapping is not cosmetic: Pleiades
        # has more components than fit a single row, and a non-wrapping layout
        # would give this widget a minimum width wider than the window.
        self.components = FlowWidget(spacing=6)
        self.components.setVisible(False)
        layout.addWidget(self.components)
        self._chips: list[_ComponentChip] = []
        #: Component indices the user has switched off.
        self._hidden: set[int] = set()
        #: What `_hidden` refers to. Component 2 of Lorenz and component 2 of
        #: Van der Pol are unrelated, so the set is dropped when this changes.
        self._hidden_for: tuple | None = None
        #: Plot items belonging to each component: the curve and its markers.
        self._series: dict[int, list] = {}

        self.plot = pg.PlotWidget()
        self.plot.setBackground(palette.plot_background)
        self.plot.showGrid(x=True, y=True, alpha=0.18)

        # Tabs rather than a second panel: the three are the same solution
        # said three ways, only one is wanted at a time, and a tab bar is the
        # one arrangement of them that a keyboard already knows how to move
        # between.
        self.views = QTabWidget()
        self.views.addTab(self.plot, "Plot")
        self.views.addTab(self._build_description(), "In words")
        self.views.addTab(self._build_table(), "Data")
        self.views.setTabToolTip(
            1, "What the curve does, in a sentence per component"
        )
        self.views.setTabToolTip(
            2, "Every output point. Arrow through it; Ctrl+C copies."
        )
        layout.addWidget(self.views, 1)

        self.legend = self.plot.addLegend(offset=(-10, 10), labelTextSize="9pt")
        self._curves: list = []
        self._markers: list = []

        self.show_steps.toggled.connect(lambda _: self._redraw())
        self.log_time.toggled.connect(lambda _: self._redraw())
        self.show_slope_field.toggled.connect(lambda _: self._redraw())
        self._last = None
        #: Where the solver kept refusing steps onto one instant -- see
        #: `analysis.rough_spots`. Read by the Solver Lab for its caution line,
        #: so the words and the marks on the plot come from one computation.
        self.rough_spots: list[float] = []
        #: Where a single trajectory stops being a prediction (UX-04), or
        #: None. Set by the Solver Lab, which owns the Lyapunov estimate it
        #: comes from; the panel only draws it.
        self.horizon: float | None = None
        self._auto_log_for: str | None = None
        # An empty panel is still a panel somebody may land on, and "" is not
        # a description of anything.
        self._say("Nothing has been solved yet.")

    # -- helpers ---------------------------------------------------------

    def _colour(self, index: int) -> str:
        series = self.palette_obj.series
        return series[index % len(series)]

    def _reset(self) -> None:
        self.plot.clear()
        self.legend = self.plot.addLegend(offset=(-10, 10), labelTextSize="9pt")
        self._curves.clear()
        self._markers.clear()
        self._series.clear()
        self._image = None

    def _dense(self, solution, samples: int = _DENSE_SAMPLES):
        """``(t, y)`` sampled from the continuous solution where available.

        The grid is the union of a uniform sweep and the solver's *own* step
        points. Uniform sampling alone is not enough: on a relaxation
        oscillator the fast jumps occupy a tiny slice of the time axis, get a
        handful of uniform samples, and the phase portrait shows straight
        chords cutting across the limit cycle. The accepted step points cluster
        precisely where the solution moves fastest -- that is what adaptivity
        means -- so including them guarantees at least the solver's own
        resolution everywhere, while the uniform part keeps slow stretches
        smooth.
        """
        if solution.sol is None:
            return solution.t, solution.y
        lo, hi = solution.sol.t_min, solution.sol.t_max
        if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
            return solution.t, solution.y

        uniform = np.linspace(lo, hi, samples)
        steps = solution.t[(solution.t >= lo) & (solution.t <= hi)]
        if steps.size > 6 * samples:
            # Already far finer than the display needs.
            return solution.t, solution.y
        grid = np.union1d(uniform, steps)
        try:
            return grid, solution.sol(grid)
        except Exception:
            return solution.t, solution.y

    def _wants_log_time(self, result) -> bool:
        """Whether this problem should default to a logarithmic time axis.

        Read from the catalogue rather than inferred from the solution: the
        obvious heuristic -- comparing t_end to the smallest positive output
        time -- fires for nearly every problem, since the first accepted step
        is always minuscule.
        """
        entry = result.entry
        return bool(entry is not None and entry.log_time_default)

    # -- entry point -----------------------------------------------------

    def clear(self, message: str = "") -> None:
        self._reset()
        self.rough_spots = []
        self.title.setText(message or "—")
        self._say(message or "Nothing has been solved yet.")
        self.table_model.set_solution(np.empty(0), np.empty((0, 0)))
        self.table_note.setText("")

    def _say(self, words: str, title: str = "") -> None:
        """Put one paragraph on the words tab and on the plot's alt text.

        One function for both, so the two can never say different things --
        which is the failure mode of every hand-maintained alternative text
        there has ever been.
        """
        self.summary_label.setText(words)
        self.plot.setAccessibleName(f"plot of {title}" if title else "plot")
        self.plot.setAccessibleDescription(words)

    def update_from(self, result, view: str = "Auto") -> None:
        # Apply the catalogue's log-time preference once per problem, then
        # leave the control alone. Re-deriving it on every redraw would make
        # the checkbox impossible to switch off.
        key = result.entry.key if result.entry is not None else None
        if key is not None and key != self._auto_log_for:
            self._auto_log_for = key
            self.log_time.blockSignals(True)
            self.log_time.setChecked(self._wants_log_time(result))
            self.log_time.blockSignals(False)

        self._last = (result, view)
        self._redraw()

    def _redraw(self) -> None:
        if self._last is None:
            return
        result, view = self._last
        if not result.ok:
            self.clear(result.error or "solve failed")
            return

        entry, solution = result.entry, result.solution
        self._reset()
        self.rough_spots = analysis.rough_spots(solution)

        kind = entry.plot_kind if view == "Auto" else {
            "Time series": "time", "Phase": "phase", "Components": "time",
        }.get(view, entry.plot_kind)
        if view == "Phase" and solution.y.shape[0] < 2:
            kind = "time"

        # A slope field is a picture of a scalar equation and nothing else.
        scalar = solution.y.shape[0] == 1
        self.show_slope_field.setVisible(scalar and kind == "time")

        if kind == "spacetime":
            self._draw_spacetime(result)
        elif kind in ("phase", "orbit", "nbody"):
            self._draw_phase(result, kind)
        else:
            self._draw_time(result)
            if scalar and self.show_slope_field.isChecked():
                self._draw_slope_field(result)

        # Chips belong to the time view, where a component is a meaningful unit
        # to switch off. In the phase plane the curve *is* the pair of them.
        components = solution.y.shape[0] if kind not in (
            "spacetime", "phase", "orbit", "nbody"
        ) else 0
        self._sync_components(result, components)
        self._describe(result, kind)

    # -- the other two views ---------------------------------------------

    def _build_description(self) -> QWidget:
        """The paragraph, on its own tab and selectable.

        Selectable because it is text somebody may want to quote into their
        own notes, and scrolling because a twenty-eight-component problem
        produces a paragraph longer than the panel.
        """
        holder = QWidget()
        inner = QVBoxLayout(holder)
        inner.setContentsMargins(10, 10, 10, 10)

        self.summary_label = QLabel("Nothing has been solved yet.")
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.summary_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.summary_label.setAccessibleName("what the plot shows")
        inner.addWidget(self.summary_label, 1)
        return holder

    def _build_table(self) -> QWidget:
        holder = QWidget()
        inner = QVBoxLayout(holder)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(4)

        self.table_model = _SolutionModel(self)
        self.table = _SolutionTable()
        self.table.setModel(self.table_model)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setAccessibleName("solution values")
        self.table.setAccessibleDescription(
            "The output times and the state at each of them."
        )
        self.table.verticalHeader().setDefaultSectionSize(20)
        inner.addWidget(self.table, 1)

        self.table_note = QLabel("")
        self.table_note.setProperty("role", "muted")
        self.table_note.setWordWrap(True)
        self.table_note.setStyleSheet(theme.scaled("font-size: 10.5px;"))
        inner.addWidget(self.table_note)
        return holder

    def summary(self) -> str:
        """The paragraph currently describing the plot. For tests, and alt text."""
        return self.summary_label.text()

    def _describe(self, result, kind: str) -> None:
        """Say what was just drawn, in words and in a table.

        Called from `_redraw` rather than from each of the three drawing
        methods, so a form added later cannot forget to do it -- which is the
        way an accessible description rots.
        """
        entry, solution = result.entry, result.solution
        labels = tuple(entry.labels) if entry is not None else ()
        title = entry.title if entry is not None else ""

        if kind == "spacetime":
            # The rows of `y` are points in space, not components of a state,
            # so describing them one by one would be describing the grid.
            field = np.real(solution.y)
            words = (
                f"{title}: a spacetime plot of {field.shape[0]} points in "
                f"space against {solution.t.size} in time, u between "
                f"{float(np.min(field)):.3g} and {float(np.max(field)):.3g}."
            )
        else:
            words = describe.summarise(solution, labels, title=title)

        # The plot is an image, and an image with no alternative text is
        # nothing at all to a screen reader.
        self._say(words, title)

        times, values = describe.table_rows(solution)
        self.table_model.set_solution(times, values, labels)
        self.table.resizeColumnsToContents()
        shown, total = times.size, solution.t.size
        self.table_note.setText(
            f"{total} output points." if shown == total else
            f"{shown} of {total} output points, evenly spaced through them."
        )

    # -- component visibility ---------------------------------------------

    def _sync_components(self, result, count: int) -> None:
        """Rebuild the chip row if the problem changed, then apply the hiding."""
        entry = result.entry
        shown = min(count, 8)
        key = (entry.key, shown)

        if key != self._hidden_for:
            # A different problem, or a different number of components. The
            # previous selection cannot be carried over meaningfully, but a
            # re-solve of the *same* problem must keep it -- otherwise nudging
            # a slider quietly switches hidden components back on.
            self._hidden_for = key
            self._hidden.clear()
            self._rebuild_chips(entry, shown)

        self.components.setVisible(shown >= 2)
        self._apply_component_visibility()

    def _rebuild_chips(self, entry, count: int) -> None:
        for chip in self._chips:
            chip.setParent(None)
            chip.deleteLater()
        self._chips.clear()
        if count < 2:
            return

        for index in range(count):
            label = (
                entry.labels[index] if index < len(entry.labels) else f"y[{index}]"
            )
            chip = _ComponentChip(
                label, self._colour(index), self.palette_obj.text_muted
            )
            chip.toggled.connect(
                lambda on, i=index: self._set_component_visible(i, on)
            )
            self.components.addWidget(chip)
            self._chips.append(chip)

    def _set_component_visible(self, index: int, visible: bool) -> None:
        if visible:
            self._hidden.discard(index)
        else:
            self._hidden.add(index)
        self._apply_component_visibility()

    def _apply_component_visibility(self) -> None:
        """Hide items rather than redraw. No solving, no resampling."""
        for index, items in self._series.items():
            visible = index not in self._hidden
            for item in items:
                item.setVisible(visible)

    def hidden_components(self) -> set[int]:
        """Which components are switched off. For tests and for the Lab."""
        return set(self._hidden)

    def _draw_slope_field(self, result) -> None:
        """Tangent dashes under a scalar solution curve.

        Drawn after the curve is in place so the window is already framed on
        it, and as a single item with NaN breaks rather than several hundred
        separate ones -- pyqtgraph slows to a crawl otherwise.
        """
        from .. import analysis

        solution = result.solution
        if result.benchmark is None or self.log_time.isChecked():
            return
        problem = getattr(result.benchmark, "problem", None)
        if problem is None or problem.y0.size != 1:
            return

        values = solution.y[0]
        low, high = float(np.min(values)), float(np.max(values))
        pad = 0.25 * (high - low) or 1.0
        try:
            segments, _ = analysis.slope_field(
                problem,
                (float(solution.t[0]), float(solution.t[-1])),
                (low - pad, high + pad),
            )
        except Exception:
            return
        if segments.size == 0:
            return

        # One polyline, with a NaN between each pair of endpoints to lift the pen.
        count = segments.shape[0]
        xs = np.full(count * 3, np.nan)
        ys = np.full(count * 3, np.nan)
        xs[0::3], xs[1::3] = segments[:, 0, 0], segments[:, 1, 0]
        ys[0::3], ys[1::3] = segments[:, 0, 1], segments[:, 1, 1]

        item = pg.PlotDataItem(
            xs, ys, connect="finite",
            pen=pg.mkPen(self.palette_obj.text_muted, width=1.0),
        )
        item.setOpacity(0.55)
        item.setZValue(-10)                 # beneath the solution curve
        self.plot.addItem(item)

    # -- the three forms -------------------------------------------------

    def _draw_time(self, result) -> None:
        entry, solution = result.entry, result.solution

        use_log = self.log_time.isChecked()
        self.plot.setLogMode(x=use_log, y=False)
        self.plot.setAspectLocked(False)
        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "y")

        t, y = self._dense(solution)
        if use_log:
            keep = t > 0
            t, y = t[keep], y[:, keep]

        count = min(y.shape[0], 8)
        # With chips on show they *are* the legend, so the plot's own is left
        # empty rather than repeating the same names inside the axes.
        chipped = count >= 2
        for index in range(count):
            label = (
                entry.labels[index] if index < len(entry.labels) else f"y[{index}]"
            )
            curve = self.plot.plot(
                t, y[index], name=None if chipped else label,
                pen=pg.mkPen(self._colour(index), width=2),
            )
            self._curves.append(curve)
            self._series.setdefault(index, []).append(curve)

        if self.show_steps.isChecked() and solution.t.size < 4000:
            st, sy = solution.t, solution.y
            if use_log:
                keep = st > 0
                st, sy = st[keep], sy[:, keep]
            for index in range(count):
                # Plotted via `plot` rather than a bare ScatterPlotItem so the
                # markers follow the log-time transform along with the curve.
                marker = self.plot.plot(
                    st, sy[index], pen=None, symbol="o", symbolSize=4,
                    symbolPen=None, symbolBrush=pg.mkBrush(self._colour(index)),
                )
                marker.setOpacity(0.55)
                self._markers.append(marker)
                # Recorded against the component so hiding a curve takes its
                # step points with it -- otherwise a "hidden" component leaves
                # a trail of dots exactly where its curve used to be.
                self._series.setdefault(index, []).append(marker)

        # A dashed rule at each rough spot, beneath the curves. The tooltip
        # repeats the caution rather than inventing a second wording.
        tip = analysis.rough_spot_note(self.rough_spots) or ""
        for spot in self.rough_spots:
            if use_log and spot <= 0:
                continue
            rule = pg.InfiniteLine(
                pos=np.log10(spot) if use_log else spot, angle=90,
                pen=pg.mkPen(self.palette_obj.warning, width=1,
                             style=Qt.DashLine),
            )
            rule.setZValue(-5)
            rule.setToolTip(tip)
            self.plot.addItem(rule)

        # The horizon: a rule, and everything after it shaded, so the part of
        # the curve that is a prediction and the part that is a sample of the
        # attractor are told apart without reading the caption.
        if self.horizon is not None and self.horizon < t[-1]:
            start = np.log10(self.horizon) if use_log else self.horizon
            finish = np.log10(t[-1]) if use_log else t[-1]
            shade = pg.LinearRegionItem(
                values=(start, finish), movable=False,
                brush=pg.mkBrush(self.palette_obj.text_muted + "22"),
                pen=pg.mkPen(self.palette_obj.text_muted, width=1,
                             style=Qt.DashLine),
            )
            shade.setZValue(-20)
            shade.setToolTip(
                "Beyond here a single trajectory is not a prediction: the "
                "attractor is, the path is not."
            )
            self.plot.addItem(shade)

        self.title.setText(
            f"{entry.title} — {solution.stats.naccepted} steps, "
            f"{solution.y.shape[0]} component"
            f"{'s' if solution.y.shape[0] != 1 else ''}"
        )

    def _draw_phase(self, result, kind: str) -> None:
        entry, solution = result.entry, result.solution
        self.plot.setLogMode(x=False, y=False)
        self.plot.setAspectLocked(kind in ("orbit", "nbody"))

        _, y = self._dense(solution)

        if kind == "nbody":
            self.plot.setLabel("bottom", "x")
            self.plot.setLabel("left", "y")
            bodies = y.shape[0] // 4
            for body in range(bodies):
                self._curves.append(
                    self.plot.plot(
                        y[body], y[body + bodies], name=f"body {body + 1}",
                        pen=pg.mkPen(self._colour(body), width=1.6),
                    )
                )
            self.title.setText(f"{entry.title} — {bodies} bodies")
            return

        i, j = entry.phase_axes
        if max(i, j) >= y.shape[0]:
            i, j = 0, 1
        x_label = entry.labels[i] if i < len(entry.labels) else f"y[{i}]"
        y_label = entry.labels[j] if j < len(entry.labels) else f"y[{j}]"
        self.plot.setLabel("bottom", x_label)
        self.plot.setLabel("left", y_label)

        # Past the predictability horizon the path is drawn faint: the shape
        # it traces is still the attractor, but *where on it* the system is
        # has stopped being information. Faded rather than cut, because the
        # attractor is the part that remains true.
        times, _ = self._dense(solution)
        cut = (int(np.searchsorted(times, self.horizon))
               if self.horizon is not None else times.size)
        self._curves.append(
            self.plot.plot(
                y[i, :cut + 1], y[j, :cut + 1],
                pen=pg.mkPen(self._colour(0), width=2), name="trajectory",
            )
        )
        if cut < times.size - 1:
            beyond = self.plot.plot(
                y[i, cut:], y[j, cut:], pen=pg.mkPen(self._colour(0), width=1),
                name="past the horizon",
            )
            beyond.setOpacity(0.3)
            self._curves.append(beyond)
        if self.show_steps.isChecked() and solution.t.size < 4000:
            marker = self.plot.plot(
                solution.y[i], solution.y[j], pen=None, symbol="o", symbolSize=4,
                symbolPen=None, symbolBrush=pg.mkBrush(self._colour(0)),
            )
            marker.setOpacity(0.55)
            self._markers.append(marker)

        # Start and end, so the direction of travel is unambiguous.
        start = self.plot.plot(
            [solution.y[i, 0]], [solution.y[j, 0]], pen=None, symbol="o",
            symbolSize=11, symbolBrush=None,
            symbolPen=pg.mkPen(self.palette_obj.success, width=2), name="start",
        )
        finish = self.plot.plot(
            [solution.y[i, -1]], [solution.y[j, -1]], pen=None, symbol="s",
            symbolSize=11, symbolBrush=None,
            symbolPen=pg.mkPen(self.palette_obj.danger, width=2), name="end",
        )
        self._markers += [start, finish]

        self.title.setText(
            f"{entry.title} — phase portrait ({solution.stats.naccepted} steps)"
        )

    def _draw_spacetime(self, result) -> None:
        entry, solution = result.entry, result.solution
        benchmark = result.benchmark
        self.plot.setLogMode(x=False, y=False)
        self.plot.setAspectLocked(False)

        to_real = getattr(benchmark, "to_real", None)
        field = to_real(solution.y) if to_real else np.real(solution.y)
        limit = float(np.abs(field).max()) or 1.0

        image = pg.ImageItem(field.T)
        colours = pg.colormap.get("CET-D1A") or pg.colormap.get("viridis")
        image.setLookupTable(colours.getLookupTable(nPts=256))
        image.setLevels([-limit, limit])

        x = getattr(benchmark, "x", np.arange(field.shape[0]))
        image.setRect(
            solution.t[0], float(x[0]),
            solution.t[-1] - solution.t[0], float(x[-1] - x[0]),
        )
        self.plot.addItem(image)
        self._image = image

        self.plot.setLabel("bottom", "t")
        self.plot.setLabel("left", "x")
        self.title.setText(
            f"{entry.title} — spacetime, u ∈ [{field.min():.2f}, {field.max():.2f}]"
        )
