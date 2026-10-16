"""A side column that folds away to a thin strip, and comes back from it.

The Lessons screen is mostly read, and three columns beside the text -- the
navigation, the course and the answers -- left the text the narrowest of the
four. Each of them can now be put away when it is not wanted. The pattern is
the Solver Lab's `StatsPanel`, generalised: only visibility and width change, so
whatever lives inside keeps working while it is folded, and is up to date the
moment it is opened again.

Two signals rather than one. `collapsed_changed` reports every change, however
it came about; `user_toggled` only the ones somebody asked for. The screen
folds the course column by itself on a narrow window, and that must not be
remembered as the reader's preference -- the next, wider window would open
with it shut for no reason anybody chose.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from .. import theme
from ..theme import Palette

__all__ = ["CollapsibleRail"]


class CollapsibleRail(QFrame):
    """`content` with a fold control above it, or a strip that opens it.

    `side` is which edge of the window the column sits against, "left" or
    "right": the chevrons point the way the column will move.
    """

    #: The width of the strip a folded column leaves behind.
    COLLAPSED_WIDTH = 30

    #: Every change, including ones the screen made for itself.
    collapsed_changed = Signal(bool)
    #: Only the changes somebody asked for -- the ones worth remembering.
    user_toggled = Signal(bool)

    def __init__(self, content: QWidget, title: str, side: str, width: int,
                 palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.content = content
        self.title = title
        self.side = side
        self.expanded_width = width
        self._collapsed = False
        self.setFixedWidth(width)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Styled explicitly, as `StatsPanel` explains: `setFlat` does not
        # override the application-wide `QPushButton` rule.
        quiet = theme.scaled(
            f"QPushButton {{ background: transparent; border: none;"
            f" color: {palette.text_muted}; font-size: 12px;"
            f" padding: 2px 4px; }}"
            f"QPushButton:hover {{ color: {palette.accent}; }}"
        )
        away, back = ("‹", "›") if side == "left" else ("›", "‹")

        self._header = QWidget()
        self._header.setStyleSheet("background: transparent;")
        row = QHBoxLayout(self._header)
        row.setContentsMargins(4, 0, 4, 2)
        row.setSpacing(0)
        self.collapse_button = QPushButton(
            f"{away} Hide" if side == "left" else f"Hide {away}"
        )
        self.collapse_button.setAccessibleName(f"hide {title.lower()}")
        self.collapse_button.setToolTip(f"Fold the {title.lower()} away and "
                                        "give its width to the text")
        self.collapse_button.setCursor(Qt.PointingHandCursor)
        self.collapse_button.setStyleSheet(quiet)
        self.collapse_button.clicked.connect(lambda: self._ask(True))
        if side == "left":
            row.addStretch(1)
            row.addWidget(self.collapse_button)
        else:
            row.addWidget(self.collapse_button)
            row.addStretch(1)
        outer.addWidget(self._header)
        outer.addWidget(content, 1)

        # Stacked characters rather than rotated text, as in `StatsPanel`: Qt
        # has no vertical label. The whole strip is the button.
        self._strip = QPushButton(back + "\n\n" + "\n".join(title))
        self._strip.setAccessibleName(f"show {title.lower()}")
        self._strip.setToolTip(f"Show the {title.lower()}")
        self._strip.setCursor(Qt.PointingHandCursor)
        self._strip.setStyleSheet(
            theme.scaled(f"QPushButton {{ background: {palette.surface};"
                         f" border: 1px solid {palette.border};"
                         f" border-radius: 6px; padding: 10px 0;"
                         f" color: {palette.text_muted}; font-size: 11px; }}"
                         f"QPushButton:hover {{ color: {palette.accent}; }}")
        )
        self._strip.clicked.connect(lambda: self._ask(False))
        self._strip.setVisible(False)
        outer.addWidget(self._strip, 0, Qt.AlignTop)
        self._spacer = outer.addStretch(0)

    # -- state -----------------------------------------------------------

    def is_collapsed(self) -> bool:
        return self._collapsed

    def set_collapsed(self, collapsed: bool) -> None:
        """Fold or open, without saying anybody asked for it."""
        collapsed = bool(collapsed)
        if collapsed == self._collapsed:
            return
        self._collapsed = collapsed
        self._header.setVisible(not collapsed)
        self.content.setVisible(not collapsed)
        self._strip.setVisible(collapsed)
        self.setFixedWidth(self.COLLAPSED_WIDTH if collapsed
                           else self.expanded_width)
        self.collapsed_changed.emit(collapsed)

    def set_expanded_width(self, width: int) -> None:
        """Change how wide the open column is, now if it is open."""
        if width == self.expanded_width:
            return
        self.expanded_width = width
        if not self._collapsed:
            self.setFixedWidth(width)

    def toggle(self) -> None:
        """Fold or open, as somebody asking for it."""
        self._ask(not self._collapsed)

    def _ask(self, collapsed: bool) -> None:
        if collapsed == self._collapsed:
            return
        self.set_collapsed(collapsed)
        self.user_toggled.emit(collapsed)
