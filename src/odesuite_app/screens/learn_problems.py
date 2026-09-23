"""Worked Problems: where the equation comes from, before it is solved.

The problem gallery on Home is a grid of pictures, which is the right shape for
choosing something to explore and the wrong shape for learning. A textbook
problem arrives as a situation -- a tank, a circuit, a falling body -- and the
equation is something you derive from it. That derivation is the part a solver
never shows.

So this screen leads with the setup and the equation, in units, and offers the
solve second. The problems themselves are ordinary catalogue entries, which is
why they also appear in every Solver Studio picker: the content is shared even
though this presentation of it is not.
"""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import catalog
from ..theme import Palette
from ..widgets.controls import add_heading, control_panel
from ..widgets.plotpanel import PlotPanel

__all__ = ["WorkedProblemsScreen"]

#: The tag that marks a catalogue entry as a modelling problem rather than an
#: integrator benchmark.
TAG = "textbook"


class WorkedProblemsScreen(QWidget):
    """Modelling problems, with the setup first and the solve second."""

    #: Asks the window to open this problem in the Solver Lab.
    open_in_lab = Signal(str)

    def __init__(self, state, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_body(), 1)

        if self.listing.count():
            self.listing.setCurrentRow(0)

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(252)

        add_heading(layout, "Problems")
        note = QLabel(
            "Situations first. Each one says where its equation comes from and "
            "what the letters mean."
        )
        note.setProperty("role", "muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        self.listing = QListWidget()
        self.listing.setAccessibleName("worked problems")
        self.listing.setMinimumHeight(220)
        for key in catalog.keys(include_user=False):
            entry = catalog.get(key)
            if TAG not in entry.tags:
                continue
            item = QListWidgetItem(entry.title)
            item.setData(Qt.UserRole, key)
            self.listing.addItem(item)
        layout.addWidget(self.listing)

        self.open_button = QPushButton("Open in the Solver Lab")
        self.open_button.setProperty("role", "primary")
        self.open_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.open_button)

        self.status = QLabel("")
        self.status.setProperty("role", "muted")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch(1)

        self.listing.currentRowChanged.connect(lambda _: self._show())
        self.open_button.clicked.connect(self._open_in_lab)
        return panel

    def _build_body(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        outer = QVBoxLayout(frame)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(8)

        self.title = QLabel("Worked Problems")
        self.title.setProperty("role", "heading")
        outer.addWidget(self.title)

        scroll = QScrollArea()
        scroll.setAccessibleName("worked problem")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner = QWidget()
        scroll.setWidget(inner)
        body = QVBoxLayout(inner)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(10)

        self.setup = QLabel()
        self.setup.setWordWrap(True)
        self.setup.setTextFormat(Qt.RichText)
        body.addWidget(self.setup)

        self.quantities = QLabel()
        self.quantities.setWordWrap(True)
        self.quantities.setTextFormat(Qt.RichText)
        body.addWidget(self.quantities)

        self.plot = PlotPanel(self.palette_obj)
        self.plot.setMinimumHeight(320)
        body.addWidget(self.plot, 1)

        outer.addWidget(scroll, 1)
        return frame

    # -- behaviour -------------------------------------------------------

    def current_key(self) -> str | None:
        item = self.listing.currentItem()
        return None if item is None else item.data(Qt.UserRole)

    def _show(self) -> None:
        key = self.current_key()
        if key is None:
            return
        entry = catalog.get(key)
        palette = self.palette_obj

        self.title.setText(entry.title)
        self.setup.setText(
            f'<div style="color:{palette.text};font-size:13px;line-height:150%;">'
            f"{entry.blurb}</div>"
        )

        rows = "".join(
            f'<tr><td style="padding:2px 14px 2px 0;color:{palette.text_muted};">'
            f"{spec.label}</td>"
            f'<td style="padding:2px 0;font-family:Cascadia Mono,Consolas,monospace;">'
            f"{spec.default:g}</td></tr>"
            for spec in entry.params
        )
        self.quantities.setText(
            f'<div style="color:{palette.text_muted};font-size:12px;">'
            f"<b>Quantities</b></div>"
            f'<table style="font-size:12px;color:{palette.text};">{rows}</table>'
        )

        self._solve(entry)

    def _solve(self, entry: catalog.CatalogEntry) -> None:
        """Solve at the default parameters and draw it.

        Solved here rather than through `SessionState` on purpose: this screen
        shows a problem in its own right, and should not move the session's
        current problem out from under the Solver Studio.
        """
        from odesuite import solve

        from ..solver import SolveRequest, SolveResult

        bench = entry.build(entry.defaults())
        solution = solve(
            bench.problem, method=entry.default_method,
            rtol=entry.default_rtol, atol=entry.default_rtol * 1e-3,
            dense_output=True, max_steps=200_000,
        )
        request = SolveRequest(
            problem_key=entry.key, method=entry.default_method,
            rtol=entry.default_rtol, atol=entry.default_rtol * 1e-3,
            params=entry.defaults(),
        )
        result = SolveResult(
            request=request, solution=solution, benchmark=bench, entry=entry
        )
        self.plot.update_from(result)

        if solution.success and bench.exact is not None:
            times = np.linspace(bench.problem.t0, bench.problem.tf, 60)
            truth = np.asarray([bench.exact(t) for t in times]).T
            error = float(np.max(np.abs(solution.y_at(times) - truth)))
            self.status.setText(
                f"{solution.stats.naccepted} steps · agrees with the closed form "
                f"to {error:.1e}"
            )
        else:
            self.status.setText(f"{solution.stats.naccepted} steps")

    def _open_in_lab(self) -> None:
        key = self.current_key()
        if key is not None:
            self.open_in_lab.emit(key)
