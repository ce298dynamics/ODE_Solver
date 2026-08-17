"""Problem cards and filter chips for the gallery."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..catalog import CatalogEntry
from ..theme import Palette
from .flow import FlowWidget

__all__ = ["ProblemCard", "TagChip", "ChipBar", "ShowcaseTile"]

CARD_WIDTH = 268
THUMB_HEIGHT = 148


class _Clickable(QFrame):
    clicked = Signal()

    def mouseReleaseEvent(self, event) -> None:     # noqa: N802
        if event.button() == Qt.LeftButton and self.rect().contains(event.position().toPoint()):
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class ProblemCard(_Clickable):
    """A thumbnail, a title, a one-line blurb and the problem's tags."""

    def __init__(self, entry: CatalogEntry, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.entry = entry
        self.setProperty("role", "card")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedWidth(CARD_WIDTH)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setToolTip(entry.blurb)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.thumb = QLabel()
        self.thumb.setFixedHeight(THUMB_HEIGHT)
        self.thumb.setAlignment(Qt.AlignCenter)
        self.thumb.setStyleSheet(
            f"background: {palette.surface_alt};"
            f"border-top-left-radius: 12px; border-top-right-radius: 12px;"
        )
        self.thumb.setText("…")
        layout.addWidget(self.thumb)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(13, 11, 13, 12)
        body_layout.setSpacing(5)

        title = QLabel(entry.title)
        title.setProperty("role", "heading")
        body_layout.addWidget(title)

        blurb = QLabel(entry.blurb)
        blurb.setWordWrap(True)
        blurb.setProperty("role", "muted")
        blurb.setStyleSheet("font-size: 12px;")
        blurb.setFixedHeight(52)
        body_layout.addWidget(blurb)

        tags = QHBoxLayout()
        tags.setSpacing(5)
        tags.setContentsMargins(0, 2, 0, 0)
        for tag in entry.tags[:3]:
            chip = QLabel(tag)
            colour = (
                palette.danger if tag == "stiff"
                else palette.warning if tag == "chaotic"
                else palette.text_muted
            )
            chip.setStyleSheet(
                f"color: {colour}; font-size: 10px; font-weight: 600;"
                f"border: 1px solid {palette.border}; border-radius: 8px;"
                f"padding: 1px 7px;"
            )
            tags.addWidget(chip)
        tags.addStretch(1)
        body_layout.addLayout(tags)

        layout.addWidget(body)

    def set_thumbnail(self, path: Path) -> None:
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            self.thumb.setText("preview unavailable")
            return
        self.thumb.setPixmap(
            pixmap.scaled(
                QSize(CARD_WIDTH, THUMB_HEIGHT),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation,
            )
        )


class TagChip(QPushButton):
    def __init__(self, tag: str, parent=None) -> None:
        super().__init__(tag, parent)
        self.tag = tag
        self.setProperty("role", "chip")
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)


class ChipBar(FlowWidget):
    """Mutually exclusive tag filters, wrapping to as many rows as needed.

    Wrapping rather than a fixed row: a dozen chips in a non-wrapping layout
    give the widget a large minimum width, which inside a scroll area widens
    the entire page and stops everything else from wrapping either.
    """

    changed = Signal(str)

    def __init__(self, tags: list[str], parent=None) -> None:
        super().__init__(spacing=6, parent=parent)
        self._chips: list[TagChip] = []
        for tag in ["all", *tags]:
            chip = TagChip(tag)
            chip.clicked.connect(lambda _=False, c=chip: self._select(c))
            self.addWidget(chip)
            self._chips.append(chip)
        self._chips[0].setChecked(True)
        self.current = "all"

    def _select(self, chosen: TagChip) -> None:
        for chip in self._chips:
            chip.setChecked(chip is chosen)
        self.current = chosen.tag
        self.changed.emit(chosen.tag)


class ShowcaseTile(_Clickable):
    """A large tile linking to one of the set-piece demonstrations."""

    def __init__(self, title: str, subtitle: str, accent: str, parent=None) -> None:
        super().__init__(parent)
        self.setProperty("role", "card")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(82)
        self.setMinimumWidth(232)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(3)

        heading = QLabel(title)
        heading.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {accent};")
        layout.addWidget(heading)

        detail = QLabel(subtitle)
        detail.setWordWrap(True)
        detail.setProperty("role", "muted")
        detail.setStyleSheet("font-size: 11.5px;")
        detail.setAlignment(Qt.AlignTop)
        layout.addWidget(detail, 1)
