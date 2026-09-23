"""Methods by Hand: Euler and RK4 written out the way a course teaches them.

The rest of the application shows what a *solver* does. This shows what a
*method* does -- one row per step, the slope, the increment, the new value, and
how far that has drifted from the truth.

Every number comes from the library's own stepper (see `byhand.walk`), so the
table cannot disagree with what the method actually computes. That is checked:
`tests/test_byhand.py` asserts the walkthrough's endpoint matches `solve` at the
same step size bit-for-bit.
"""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import catalog
from ..byhand import SUPPORTED, refinement, walk
from ..theme import Palette
from ..widgets.controls import (
    ValueSlider,
    add_heading,
    control_panel,
    fill_problem_picker,
)

__all__ = ["ByHandScreen"]

#: Step sizes are chosen, not adapted -- that is the lesson. A slider over a
#: decade is more useful here than a free text box.
_H_MIN, _H_MAX, _H_DEFAULT = 0.005, 0.5, 0.1


def _has_exact(entry: catalog.CatalogEntry) -> bool:
    """Only problems with a closed form: the error column is the whole point."""
    try:
        bench = entry.build(entry.defaults())
    except Exception:
        return False
    return getattr(bench, "exact", None) is not None


class ByHandScreen(QWidget):
    """Euler and RK4, step by step, against the exact answer."""

    def __init__(self, state, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_body(), 1)

        self.refresh_problems()
        self._recompute()

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(252)

        add_heading(layout, "Problem")
        self.problem = QComboBox()
        self.problem.setAccessibleName("problem")
        self.problem.setToolTip(
            "Only problems with a closed-form solution, so every row can be "
            "compared with the truth."
        )
        layout.addWidget(self.problem)

        add_heading(layout, "Method", space_above=6)
        self.method = QComboBox()
        self.method.setAccessibleName("method")
        for key in SUPPORTED:
            self.method.addItem(
                {"euler": "Euler (order 1)", "rk4": "RK4 (order 4)"}[key], key
            )
        layout.addWidget(self.method)

        note = QLabel(
            "Neither method adapts. You choose the step size, and the table "
            "shows what that choice costs."
        )
        note.setProperty("role", "muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        add_heading(layout, "Step size", space_above=6)
        self.h_slider = ValueSlider(
            "h", _H_MIN, _H_MAX, _H_DEFAULT, log=True,
            hint="Logarithmic: the interesting range spans two decades",
        )
        layout.addWidget(self.h_slider)

        self.steps_slider = ValueSlider("rows shown", 3, 20, 8)
        layout.addWidget(self.steps_slider)

        self.status = QLabel("")
        self.status.setProperty("role", "muted")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch(1)

        self.problem.currentIndexChanged.connect(lambda _: self._recompute())
        self.method.currentIndexChanged.connect(lambda _: self._recompute())
        # `committed` rather than `preview`: rebuilding the table is cheap but
        # not free, and a drag should not recompute it on every pixel.
        self.h_slider.committed.connect(lambda _: self._recompute())
        self.steps_slider.committed.connect(lambda _: self._recompute())
        return panel

    def _build_body(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        outer = QVBoxLayout(frame)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(8)

        self.title = QLabel("Methods by Hand")
        self.title.setProperty("role", "heading")
        outer.addWidget(self.title)

        scroll = QScrollArea()
        scroll.setAccessibleName("worked table")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner = QWidget()
        scroll.setWidget(inner)
        body = QVBoxLayout(inner)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(12)

        self.table = QLabel()
        self.table.setTextFormat(Qt.RichText)
        self.table.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.table.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        body.addWidget(self.table)

        self.refine_heading = QLabel("Halve the step")
        self.refine_heading.setProperty("role", "heading")
        body.addWidget(self.refine_heading)

        self.refine_note = QLabel()
        self.refine_note.setProperty("role", "muted")
        self.refine_note.setWordWrap(True)
        body.addWidget(self.refine_note)

        self.refine_table = QLabel()
        self.refine_table.setTextFormat(Qt.RichText)
        self.refine_table.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        body.addWidget(self.refine_table)

        body.addStretch(1)
        outer.addWidget(scroll, 1)
        return frame

    # -- data ------------------------------------------------------------

    def refresh_problems(self) -> None:
        fill_problem_picker(self.problem, _has_exact, include_user=False)

    def _recompute(self) -> None:
        key = self.problem.currentData()
        if key is None:
            return
        entry = catalog.get(key)
        bench = entry.build(entry.defaults())
        method = self.method.currentData()
        h = float(self.h_slider.value())
        rows = max(1, int(round(self.steps_slider.value())))

        run = walk(bench.problem, method, h=h, n_steps=rows, exact=bench.exact)
        self.title.setText(f"{entry.title} — {method} at h = {h:g}")
        self.table.setText(self._render_steps(run))

        levels = refinement(bench.problem, method, h, bench.exact, levels=4)
        expected = 2 ** (1 if method == "euler" else 4)
        self.refine_note.setText(
            f"Halving h should divide the error by about {expected} for a "
            f"{'first' if method == 'euler' else 'fourth'}-order method. "
            f"The ratio column is that claim, measured."
        )
        self.refine_table.setText(self._render_refinement(levels))
        self.status.setText(
            f"{len(run.rows)} steps shown · endpoint error "
            f"{run.final_error:.3e}" if run.final_error is not None else ""
        )

    # -- rendering -------------------------------------------------------

    def _table(self, headers, rows) -> str:
        p = self.palette_obj
        head = "".join(
            f'<th style="padding:3px 10px;text-align:right;color:{p.text_muted};'
            f'border-bottom:1px solid {p.border};">{h}</th>'
            for h in headers
        )
        body = ""
        for row in rows:
            cells = "".join(
                f'<td style="padding:3px 10px;text-align:right;">{c}</td>' for c in row
            )
            body += f"<tr>{cells}</tr>"
        return (
            f'<table style="font-family:Cascadia Mono,Consolas,monospace;'
            f'font-size:12px;color:{p.text};border-collapse:collapse;">'
            f"<tr>{head}</tr>{body}</table>"
        )

    def _render_steps(self, run) -> str:
        if not run.rows:
            return "<i>the method could not take a step here</i>"

        multi = bool(run.rows[0].stages)
        headers = ["n", "t<sub>n</sub>", "y<sub>n</sub>", "f(t<sub>n</sub>,y<sub>n</sub>)"]
        if multi:
            headers += [f"k<sub>{i + 2}</sub>" for i in range(len(run.rows[0].stages))]
        headers += ["y<sub>n+1</sub>"]
        if run.has_exact:
            headers += ["exact", "|error|"]

        def num(value) -> str:
            return f"{float(np.atleast_1d(value)[0]):.6f}"

        rows = []
        for r in run.rows:
            cells = [str(r.n), f"{r.t:.4f}", num(r.y), num(r.f)]
            cells += [num(k) for k in r.stages]
            cells += [num(r.y_next)]
            if run.has_exact and r.exact_next is not None:
                cells += [num(r.exact_next), f"{r.error:.2e}"]
            rows.append(cells)
        return self._table(headers, rows)

    def _render_refinement(self, levels) -> str:
        rows = []
        for h, n_steps, error, ratio in levels:
            rows.append([
                f"{h:.5f}", str(n_steps), f"{error:.3e}",
                "—" if ratio is None else f"{ratio:.2f}",
            ])
        return self._table(["h", "steps", "|error|", "ratio"], rows)
