"""The answer column: where the typing happens, beside the text rather than in it.

A lesson's Practice and Drill used to stack each question's whole apparatus --
the box, five buttons, the typeset preview, the hints and a worked solution
two hundred pixels tall -- into the reading column, between one question and
the next. The text became the thin part of its own page. Now the column keeps
what is *read* (the prompt, the equation, the figure) and this keeps what is
*operated*, one question at a time: whichever one was last clicked, or had a
key pressed in it.

One page per question, built up front and kept. Switching between them is a
`QStackedWidget` flip, so what was typed, the hints shown and any working
fetched are all still there on the way back.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..theme import Palette

__all__ = ["AnswerWorkspace"]


class AnswerWorkspace(QFrame):
    """A stack of answer pages, one per question, and which one is up."""

    #: The key of the page now showing, or "" for the empty page.
    activated = Signal(str)

    EMPTY = "Nothing to answer on this page. Practice and Drill put their " \
            "answer boxes here, beside the question you are working on."

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette
        self.setProperty("role", "panel")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.heading = QLabel("Your answer")
        self.heading.setProperty("role", "heading")
        self.heading.setWordWrap(True)
        self.heading.setContentsMargins(16, 12, 16, 4)
        outer.addWidget(self.heading)

        # Not named "controls": the panels test holds those to never scrolling
        # sideways, and this one must -- a typeset equation does not reflow.
        self.scroll = QScrollArea()
        self.scroll.setAccessibleName("answer workspace")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(self.scroll, 1)

        self.stack = QStackedWidget()
        self.scroll.setWidget(self.stack)

        self._empty = QLabel(self.EMPTY)
        self._empty.setProperty("role", "muted")
        self._empty.setWordWrap(True)
        self._empty.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._empty.setContentsMargins(16, 8, 16, 8)
        self.stack.addWidget(self._empty)

        #: Key -> the holder in the stack, and the page the caller gave.
        self._pages: dict[str, QWidget] = {}
        self._content: dict[str, QWidget] = {}
        self._titles: dict[str, str] = {}
        self._current = ""

    # -- pages -----------------------------------------------------------

    def add_page(self, key: str, title: str, page: QWidget) -> None:
        """Hold `page` as the answer for `key`. It is shown by `activate`."""
        # In a holder with a stretch beneath it. The stack is as tall as the
        # column, and a page given that height spread its rows down it -- the
        # verdict ended up seven hundred pixels below the box it is about.
        holder = QWidget()
        column = QVBoxLayout(holder)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(0)
        column.addWidget(page)
        column.addStretch(1)
        self._pages[key] = holder
        self._content[key] = page
        self._titles[key] = title
        holder.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.stack.addWidget(holder)

    def page(self, key: str) -> QWidget | None:
        return self._content.get(key)

    def keys(self) -> list[str]:
        return list(self._pages)

    def current_key(self) -> str:
        return self._current

    def activate(self, key: str) -> bool:
        """Show the page for `key`. False, and nothing changes, if there is none."""
        page = self._pages.get(key)
        if page is None:
            return False
        self._size_to(page)
        self.stack.setCurrentWidget(page)
        self.heading.setText(self._titles.get(key, "Your answer"))
        changed = key != self._current
        self._current = key
        if changed:
            self.activated.emit(key)
        return True

    def _size_to(self, shown: QWidget) -> None:
        """Let only the page on show decide how tall the stack is.

        A `QStackedWidget` is as tall as its tallest page, so one question
        with its working open would leave every other page scrolling through
        a long blank. Hidden pages are told to ignore their size instead.
        """
        for page in (*self._pages.values(), self._empty):
            policy = (QSizePolicy.Preferred if page is shown
                      else QSizePolicy.Ignored)
            page.setSizePolicy(policy, policy)
        self.stack.updateGeometry()

    def clear(self) -> None:
        """Drop every page, back to the empty one."""
        for page in self._pages.values():
            self.stack.removeWidget(page)
            page.setParent(None)
            page.deleteLater()
        self._pages.clear()
        self._content.clear()
        self._titles.clear()
        self._current = ""
        self._size_to(self._empty)
        self.stack.setCurrentWidget(self._empty)
        self.heading.setText("Your answer")
