"""A flow layout: items wrap to the next row when they run out of width.

Qt ships no such layout. A fixed grid would either waste space on a wide window
or clip on a narrow one, and the problem gallery needs to reflow as the window
resizes.
"""

from __future__ import annotations

from PySide6.QtCore import QMargins, QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QSizePolicy, QWidget

__all__ = ["FlowLayout", "FlowWidget"]


class FlowLayout(QLayout):
    def __init__(self, parent=None, margin: int = 0, spacing: int = 14) -> None:
        super().__init__(parent)
        self._items: list = []
        self._spacing = spacing
        self.setContentsMargins(QMargins(margin, margin, margin, margin))

    # -- QLayout plumbing ------------------------------------------------

    def addItem(self, item) -> None:            # noqa: N802 (Qt naming)
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index):                    # noqa: N802
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):                    # noqa: N802
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def expandingDirections(self):              # noqa: N802
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self) -> bool:        # noqa: N802
        return True

    def heightForWidth(self, width: int) -> int:    # noqa: N802
        return self._layout(QRect(0, 0, width, 0), apply=False)

    def setGeometry(self, rect) -> None:        # noqa: N802
        super().setGeometry(rect)
        self._layout(rect, apply=True)

    def sizeHint(self) -> QSize:                # noqa: N802
        return self.minimumSize()

    def minimumSize(self) -> QSize:             # noqa: N802
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        return size + QSize(
            margins.left() + margins.right(), margins.top() + margins.bottom()
        )

    # -- the actual placement --------------------------------------------

    def widthForContent(self) -> int:           # noqa: N802
        """Width of the widest single item -- the true minimum before clipping."""
        return max((item.sizeHint().width() for item in self._items), default=0)

    def _layout(self, rect: QRect, apply: bool) -> int:
        margins = self.contentsMargins()
        effective = rect.adjusted(
            margins.left(), margins.top(), -margins.right(), -margins.bottom()
        )
        x, y = effective.x(), effective.y()
        row_height = 0

        for item in self._items:
            hint = item.sizeHint()
            next_x = x + hint.width() + self._spacing
            if next_x - self._spacing > effective.right() and row_height > 0:
                x = effective.x()
                y = y + row_height + self._spacing
                next_x = x + hint.width() + self._spacing
                row_height = 0
            if apply:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x = next_x
            row_height = max(row_height, hint.height())

        return y + row_height - rect.y() + margins.bottom()


class FlowWidget(QWidget):
    """Host widget for a `FlowLayout`.

    Two things a bare `QWidget` gets wrong. It does not advertise
    height-for-width, so a vertical layout above it reserves the height of a
    single row and the rest is clipped. And its size hint inherits the layout's
    preferred width, which for a wrapping layout is meaningless -- inside a
    scroll area that widens the whole page and defeats the wrapping. Reporting
    the widest single item as the minimum fixes both.
    """

    def __init__(self, spacing: int = 14, parent=None) -> None:
        super().__init__(parent)
        self.flow = FlowLayout(self, margin=0, spacing=spacing)
        policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)

    def addWidget(self, widget) -> None:        # noqa: N802
        self.flow.addWidget(widget)

    def hasHeightForWidth(self) -> bool:        # noqa: N802
        return True

    def heightForWidth(self, width: int) -> int:    # noqa: N802
        return self.flow.heightForWidth(width)

    def minimumSizeHint(self) -> QSize:         # noqa: N802
        return QSize(self.flow.widthForContent(), 0)

    def sizeHint(self) -> QSize:                # noqa: N802
        width = self.width() or self.flow.widthForContent()
        return QSize(width, self.flow.heightForWidth(width))

    def resizeEvent(self, event) -> None:       # noqa: N802
        super().resizeEvent(event)
        # Height depends on width, so a resize changes the geometry the parent
        # layout must reserve.
        self.updateGeometry()
