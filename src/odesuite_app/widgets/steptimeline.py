"""The step-size timeline: h(t) beneath the trajectory.

The application's signature view, and the reason it is more than a plotting
front end. Every adaptive solver spends its effort unevenly, but that effort is
invisible in the solution curve -- a trajectory through a relaxation jump looks
much like a trajectory anywhere else. Plotting the gaps between accepted steps
makes it visible: on Van der Pol at mu=1000 the step size collapses by four
orders of magnitude at each jump and recovers in between, and the shape of that
collapse *is* the definition of stiffness.

Rejected attempts are drawn as separate marks. They cluster exactly where the
controller misjudged the problem, which is usually the moment before a sharp
feature.
"""

from __future__ import annotations

import numpy as np
import pyqtgraph as pg
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from .. import theme
from ..theme import Palette

__all__ = ["StepTimeline"]


class StepTimeline(QFrame):
    """Log-scaled step size against time, with rejections marked."""

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette
        self.setProperty("role", "panel")
        self.setMinimumHeight(150)
        self.setMaximumHeight(210)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        header = QHBoxLayout()
        title = QLabel("Step size")
        title.setProperty("role", "heading")
        header.addWidget(title)

        self.caption = QLabel("")
        self.caption.setProperty("role", "muted")
        self.caption.setStyleSheet(theme.scaled("font-size: 11px;"))
        header.addSpacing(10)
        header.addWidget(self.caption)
        header.addStretch(1)

        self.legend = QLabel("")
        self.legend.setStyleSheet(theme.scaled("font-size: 10.5px;"))
        header.addWidget(self.legend)
        layout.addLayout(header)

        self.plot = pg.PlotWidget()
        self.plot.setBackground(palette.plot_background)
        self.plot.showGrid(x=True, y=True, alpha=0.18)
        self.plot.setLabel("left", "h")
        self.plot.setLabel("bottom", "t")
        self.plot.setLogMode(x=False, y=True)
        self.plot.setMouseEnabled(x=True, y=False)
        layout.addWidget(self.plot)

        self._curve = self.plot.plot(
            [], [], pen=pg.mkPen(palette.accent, width=1.6)
        )
        # Markers are PlotDataItems, not ScatterPlotItems. `setLogMode` only
        # transforms PlotDataItems; a ScatterPlotItem added straight to the plot
        # has its coordinates taken as already-logged, which silently puts a
        # step of 1.3e-4 at y = 1.
        self._rejects = self.plot.plot(
            [], [], pen=None, symbol="x", symbolSize=8,
            symbolPen=pg.mkPen(palette.danger, width=1.6), symbolBrush=None,
        )
        self._minimum = self.plot.plot(
            [], [], pen=None, symbol="o", symbolSize=9,
            symbolPen=pg.mkPen(palette.warning, width=1.5),
            symbolBrush=pg.mkBrush(palette.warning),
        )

    # -- updates ---------------------------------------------------------

    def clear(self) -> None:
        self._curve.setData([], [])
        self._rejects.setData([], [])
        self._minimum.setData([], [])
        self.caption.setText("")
        self.legend.setText("")

    def update_from(self, result, log_time: bool = False) -> None:
        palette = self.palette_obj
        if not result.ok:
            self.clear()
            return

        midpoints, h = result.step_sizes()
        if h.size == 0:
            self.clear()
            return

        # A fixed-step method draws a flat line; say so rather than presenting
        # a featureless plot as though it were a measurement.
        constant = float(h.max() / h.min()) < 1.0 + 1e-9

        self.plot.setLogMode(x=log_time, y=True)
        positive = midpoints > 0
        x = midpoints[positive] if log_time else midpoints
        y = h[positive] if log_time else h
        self._curve.setData(x, y)

        rejected = result.solution.rejected
        if rejected.size and not constant:
            rx, ry = rejected[:, 0], rejected[:, 1]
            keep = (rx > 0) if log_time else np.ones(rx.shape, dtype=bool)
            self._rejects.setData(rx[keep], ry[keep])
        else:
            self._rejects.setData([], [])

        index = int(np.argmin(h))
        if not constant and (midpoints[index] > 0 or not log_time):
            self._minimum.setData([midpoints[index]], [h[index]])
        else:
            self._minimum.setData([], [])

        if constant:
            self.caption.setText(f"constant h = {h[0]:.3g} (fixed-step method)")
            self.legend.setText("")
        else:
            spread = h.max() / h.min()
            self.caption.setText(
                f"{h.min():.2e} … {h.max():.2e}   ({spread:,.0f}× spread)"
                if spread < 1e6
                else f"{h.min():.2e} … {h.max():.2e}   ({spread:.1e}× spread)"
            )
            parts = [f"<span style='color:{palette.warning}'>●</span> smallest step"]
            if rejected.size:
                parts.append(
                    f"<span style='color:{palette.danger}'>✕</span> "
                    f"{len(rejected)} rejected"
                )
            self.legend.setText("&nbsp;&nbsp;".join(parts))
