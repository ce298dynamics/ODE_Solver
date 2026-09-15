"""The live statistics panel.

Deliberately prominent rather than tucked into a status bar. The whole argument
of this project is that *how* a solver reaches an answer matters -- how many
Jacobians it needed, how many steps it threw away -- and those numbers are the
evidence. Watching `njev` stay at 16 while `steps` climbs past 400 is the
clearest possible demonstration of why simplified Newton reuses factorisations.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import theme
from ..theme import Palette

__all__ = ["StatsPanel"]


def _thousands(value: int) -> str:
    return f"{value:,}"


class _Row(QWidget):
    """One label/value pair, with an optional highlight colour."""

    def __init__(self, label: str, tooltip: str, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 1, 0, 1)
        layout.setSpacing(0)

        self.name = QLabel(label)
        self.name.setProperty("role", "muted")
        self.name.setStyleSheet(theme.scaled("font-size: 11.5px;"))
        self.name.setToolTip(tooltip)
        layout.addWidget(self.name, 0, 0, Qt.AlignLeft)

        self.value = QLabel("—")
        self.value.setProperty("role", "mono")
        self.value.setStyleSheet(theme.scaled("font-size: 13px; font-weight: 600;"))
        self.value.setToolTip(tooltip)
        layout.addWidget(self.value, 0, 1, Qt.AlignRight)
        layout.setColumnStretch(0, 1)

    def set(self, text: str, colour: str | None = None) -> None:
        self.value.setText(text)
        self.value.setStyleSheet(
            theme.scaled("font-size: 13px; font-weight: 600;"
                         + (f" color: {colour};" if colour else ""))
        )


class StatsPanel(QFrame):
    """Work counters and diagnostics for the most recent solve."""

    #: Width expanded, and as a collapsed strip.
    WIDTH = 196
    COLLAPSED_WIDTH = 30

    collapsed_changed = Signal(bool)

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette
        self.setProperty("role", "panel")
        self.setFixedWidth(self.WIDTH)
        self._collapsed = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # -- header, with the control that collapses the panel -------------
        self._header = QWidget()
        self._header.setStyleSheet("background: transparent;")
        header_row = QHBoxLayout(self._header)
        header_row.setContentsMargins(14, 12, 10, 2)
        header_row.setSpacing(4)

        heading = QLabel("Work")
        heading.setProperty("role", "heading")
        header_row.addWidget(heading)
        header_row.addStretch(1)

        self.collapse_button = QPushButton("‹")
        self.collapse_button.setFixedSize(20, 20)
        self.collapse_button.setToolTip("Hide the work counters and widen the plot")
        self.collapse_button.setCursor(Qt.PointingHandCursor)
        # Styled explicitly rather than with `setFlat`, which does not override
        # the application-wide `QPushButton` rule -- left to it, the control
        # paints as an empty raised box with the chevron lost inside it.
        self.collapse_button.setStyleSheet(
            theme.scaled(f"QPushButton {{ background: transparent; border: none;"
                         f" color: {palette.text_muted}; font-size: 17px;"
                         f" padding: 0; margin: 0; }}"
                         f"QPushButton:hover {{ color: {palette.accent}; }}")
        )
        self.collapse_button.clicked.connect(lambda: self.set_collapsed(True))
        header_row.addWidget(self.collapse_button)
        outer.addWidget(self._header)

        # -- the collapsed strip -------------------------------------------
        # Set as stacked characters rather than rotated text: Qt has no
        # vertical label, and a rotated one needs a custom `paintEvent` for no
        # benefit at four letters. The whole strip is the button, so there is
        # no small target to hunt for.
        self._strip = QPushButton("›\n\n" + "\n".join("Work"))
        self._strip.setFlat(True)
        self._strip.setCursor(Qt.PointingHandCursor)
        self._strip.setToolTip("Show the work counters")
        self._strip.setStyleSheet(
            theme.scaled(f"background: transparent; border: none; padding: 10px 0;"
                         f" color: {palette.text_muted}; font-size: 11px;")
        )
        self._strip.clicked.connect(lambda: self.set_collapsed(False))
        self._strip.setVisible(False)
        outer.addWidget(self._strip)
        outer.addStretch(0)

        # -- everything else, hidden wholesale when collapsed ---------------
        self._body = QWidget()
        self._body.setStyleSheet("background: transparent;")
        outer.addWidget(self._body, 1)

        layout = QVBoxLayout(self._body)
        layout.setContentsMargins(14, 2, 14, 12)
        layout.setSpacing(1)

        self.rows: dict[str, _Row] = {}
        specification = [
            ("nfev", "RHS evaluations",
             "Calls to f(t, y). The implementation-independent cost measure, "
             "and what dominates when f is expensive."),
            ("njev", "Jacobians",
             "Jacobian evaluations. Simplified Newton reuses one across many "
             "steps, so this stays far below the step count for Radau."),
            ("nlu", "LU factorisations",
             "Refactorisations of the iteration matrix. Redone when the step "
             "size drifts or the Jacobian goes stale."),
            ("steps", "accepted steps", "Steps the controller kept."),
            ("rejected", "rejected steps",
             "Attempts the error estimate refused. A few are healthy; many "
             "means the controller is fighting the problem."),
            ("runtime", "wall time", "Time spent inside solve()."),
        ]
        for key, label, tip in specification:
            row = _Row(label, tip, palette)
            layout.addWidget(row)
            self.rows[key] = row

        layout.addSpacing(10)
        self.quality_heading = QLabel("Solution")
        self.quality_heading.setProperty("role", "heading")
        layout.addWidget(self.quality_heading)
        layout.addSpacing(4)

        for key, label, tip in [
            ("points", "output points", "Points in the returned solution."),
            ("hmin", "smallest step",
             "The tightest the controller had to squeeze. On a stiff problem "
             "this is orders of magnitude below the largest."),
            ("hmax", "largest step", "The most it could stretch."),
            ("hratio", "step ratio",
             "Largest over smallest. A big ratio is the signature of a "
             "problem with widely separated timescales."),
            ("invariant", "invariant drift",
             "Relative drift of the problem's conserved quantity, where it "
             "has one. Bounded for a symplectic method; growing otherwise."),
        ]:
            row = _Row(label, tip, palette)
            layout.addWidget(row)
            self.rows[key] = row

        layout.addSpacing(10)
        self.status = QLabel("no solve yet")
        self.status.setProperty("role", "muted")
        self.status.setStyleSheet(theme.scaled("font-size: 10.5px;"))
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        layout.addStretch(1)

    # -- collapsing ------------------------------------------------------

    @property
    def collapsed(self) -> bool:
        return self._collapsed

    def set_collapsed(self, collapsed: bool) -> None:
        """Shrink to a strip, giving the width back to the plot.

        Only visibility and width change. The rows themselves stay alive and
        `update_from` keeps writing to them, so a solve that finishes while the
        panel is shut is already shown the moment it is opened -- rather than
        the panel reappearing with whatever was there when it closed.
        """
        collapsed = bool(collapsed)
        if collapsed == self._collapsed:
            return
        self._collapsed = collapsed

        self._header.setVisible(not collapsed)
        self._body.setVisible(not collapsed)
        self._strip.setVisible(collapsed)
        self.setFixedWidth(self.COLLAPSED_WIDTH if collapsed else self.WIDTH)
        self.collapsed_changed.emit(collapsed)

    def toggle(self) -> None:
        self.set_collapsed(not self._collapsed)

    # -- updates ---------------------------------------------------------

    def clear(self, message: str = "solving…") -> None:
        for row in self.rows.values():
            row.set("—")
        self.status.setText(message)

    def update_from(self, result) -> None:
        palette = self.palette_obj
        if result.error:
            self.clear("")
            self.status.setText(result.error)
            self.status.setStyleSheet(theme.scaled(f"font-size: 10.5px; color: {palette.danger};"))
            return

        self.status.setStyleSheet(theme.scaled(f"font-size: 10.5px; color: {palette.text_muted};"))
        solution, stats = result.solution, result.solution.stats

        self.rows["nfev"].set(_thousands(stats.nfev))
        self.rows["njev"].set(_thousands(stats.njev) if stats.njev else "—")
        self.rows["nlu"].set(_thousands(stats.nlu) if stats.nlu else "—")
        self.rows["steps"].set(_thousands(stats.naccepted))

        # A high rejection ratio is worth flagging: it usually means the
        # tolerance and the method are mismatched to the problem.
        ratio = stats.reject_ratio
        self.rows["rejected"].set(
            _thousands(stats.nrejected),
            palette.warning if ratio > 0.15 else (
                palette.danger if ratio > 0.35 else None
            ),
        )
        self.rows["runtime"].set(f"{result.wall_time * 1e3:,.0f} ms")
        self.rows["points"].set(_thousands(solution.t.size))

        _, h = result.step_sizes()
        if h.size:
            self.rows["hmin"].set(f"{h.min():.2e}")
            self.rows["hmax"].set(f"{h.max():.2e}")
            spread = h.max() / h.min()
            self.rows["hratio"].set(
                f"{spread:,.0f}×" if spread < 1e5 else f"{spread:.1e}×",
                palette.accent if spread > 1e3 else None,
            )
        else:
            for key in ("hmin", "hmax", "hratio"):
                self.rows[key].set("—")

        _, drift = result.invariant_drift()
        if drift is not None and drift.size:
            final = float(drift[-1])
            self.rows["invariant"].set(
                f"{final:.2e}",
                palette.success if final < 1e-8 else (
                    palette.warning if final > 1e-3 else None
                ),
            )
        else:
            self.rows["invariant"].set("—")

        self.status.setText(result.status_text)
