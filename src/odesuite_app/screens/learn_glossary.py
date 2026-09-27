"""Glossary: every term the course uses, and the way back to where it is taught.

The content and its two honesty rules live in `lessons.glossary`; this is the
screen. A search box, the terms, and for the chosen term its definition, the
lesson that teaches it and every lesson that uses it -- each a button that
opens the lesson.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..lessons import LESSONS, by_key
from ..lessons.glossary import TERMS, search, uses
from ..theme import Palette
from ..widgets.controls import add_heading, control_panel

__all__ = ["GlossaryScreen"]


class GlossaryScreen(QWidget):
    #: Asks the window to open `Lessons` at a particular lesson.
    open_lesson = Signal(str)

    def __init__(self, state, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        panel, controls = control_panel(300)
        add_heading(controls, "Glossary")
        blurb = QLabel(f"{len(TERMS)} terms, each linked to the lesson that "
                       "teaches it and every lesson that uses it.")
        blurb.setProperty("role", "muted")
        blurb.setWordWrap(True)
        controls.addWidget(blurb)

        self.query = QLineEdit()
        self.query.setAccessibleName("search the glossary")
        self.query.setPlaceholderText("Search terms and definitions")
        self.query.setClearButtonEnabled(True)
        self.query.textChanged.connect(self._filter)
        controls.addWidget(self.query)

        self.listing = QListWidget()
        self.listing.setAccessibleName("glossary terms")
        self.listing.currentItemChanged.connect(lambda *_: self._show())
        controls.addWidget(self.listing, 1)
        layout.addWidget(panel)

        scroll = QScrollArea()
        scroll.setAccessibleName("glossary entry")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        page = QWidget()
        self._page = QVBoxLayout(page)
        self._page.setContentsMargins(18, 16, 18, 18)
        self._page.setSpacing(10)
        scroll.setWidget(page)
        layout.addWidget(scroll, 1)

        self._filter("")

    # -- the list --------------------------------------------------------

    def _filter(self, text: str) -> None:
        found = search(text)
        self.listing.blockSignals(True)
        self.listing.clear()
        for term in found:
            item = QListWidgetItem(term.name)
            item.setData(Qt.UserRole, term)
            self.listing.addItem(item)
        self.listing.blockSignals(False)
        if found:
            self.listing.setCurrentRow(0)
        self._show()

    def current_term(self):
        item = self.listing.currentItem()
        return item.data(Qt.UserRole) if item is not None else None

    # -- the entry -------------------------------------------------------

    def _clear(self) -> None:
        while self._page.count():
            item = self._page.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()

    def _show(self) -> None:
        self._clear()
        term = self.current_term()
        if term is None:
            empty = QLabel("No term matches that search.")
            empty.setProperty("role", "muted")
            self._page.addWidget(empty)
            self._page.addStretch(1)
            return

        name = QLabel(term.name)
        name.setProperty("role", "heading")
        self._page.addWidget(name)
        definition = QLabel(term.definition)
        definition.setWordWrap(True)
        self._page.addWidget(definition)

        home = by_key(term.lesson)
        add_heading(self._page, "Taught in", space_above=6)
        self._page.addWidget(self._link(home))

        others = [lesson for lesson in uses(term, LESSONS) if lesson is not home]
        add_heading(self._page, "Also used in", space_above=6)
        if not others:
            none = QLabel("No other lesson uses it by name.")
            none.setProperty("role", "muted")
            self._page.addWidget(none)
        for lesson in others:
            self._page.addWidget(self._link(lesson))
        self._page.addStretch(1)

    def _link(self, lesson) -> QPushButton:
        button = QPushButton(lesson.title)
        button.setToolTip(f"Open the lesson: {lesson.title}")
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("text-align: left; padding: 4px 10px;")
        button.clicked.connect(lambda: self.open_lesson.emit(lesson.key))
        return button
