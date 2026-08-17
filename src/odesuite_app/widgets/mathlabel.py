"""Widgets that display typeset mathematics.

`MathLabel` is the workhorse: hand it a sympy expression and a palette and it
shows the equation set in Computer Modern. Two behaviours matter more than they
might appear to:

* **It never fails visibly.** If the expression cannot be typeset -- a
  construct mathtext lacks, an expression too wide to read -- the label shows
  the monospace form instead. There is no error state and no blank rectangle,
  because a slightly ugly answer beats a missing one.
* **It never blocks.** A cached image is painted immediately; anything else is
  rendered on the thread pool while the text form stands in. The swap follows
  the token idiom used everywhere else in this application (`solver.py`,
  `screens/home.py`), so a label that is retyped or destroyed mid-render
  discards the stale result rather than painting it.

`MathBlock` stacks rows. It exists because mathtext cannot render a LaTeX
``cases`` or ``matrix`` environment at all, so anything with more than one line
-- a `Piecewise` solution, a system, a fundamental solution set -- has to be
composed by Qt rather than by LaTeX.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMenu, QVBoxLayout, QWidget

from .. import mathrender
from ..mathrender import Row
from ..theme import Palette

__all__ = ["MathLabel", "MathBlock"]


class _RenderSignals(QObject):
    ready = Signal(int, object)          # token, QPixmap


class _RenderJob(QRunnable):
    """Typesets one expression off the GUI thread."""

    def __init__(self, token: int, latex: str, colour: str, point_size: float,
                 ratio: float, signals: _RenderSignals) -> None:
        super().__init__()
        self.token = token
        self.latex = latex
        self.colour = colour
        self.point_size = point_size
        self.ratio = ratio
        self.signals = signals
        self.setAutoDelete(True)

    def run(self) -> None:
        # Produce the PNG here, on the worker; building the QPixmap itself is
        # left to the main thread, since QPixmap may not be touched off it.
        data = mathrender.render_bytes(
            self.latex, self.colour, self.point_size, self.ratio
        )
        try:
            self.signals.ready.emit(self.token, data)
        except RuntimeError:
            pass                       # the label went away mid-render


class MathLabel(QWidget):
    """A single typeset expression, with a monospace fallback."""

    def __init__(self, palette: Palette, expr=None, *,
                 point_size: float = mathrender.DEFAULT_POINT_SIZE,
                 colour: str | None = None, parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette
        self.point_size = float(point_size)
        self.colour = colour or palette.text

        self._latex = ""
        self._plain = ""
        self._token = 0
        self._signals = _RenderSignals()
        self._signals.ready.connect(self._on_rendered)

        # Without this the generic ``QWidget`` rule in the style sheet paints
        # the window background, punching a rectangle of backdrop through
        # whatever card the equation sits on.
        self.setStyleSheet("background: transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._label = QLabel()
        self._label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self._label)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        if expr is not None:
            self.set_expression(expr)

    # -- content ---------------------------------------------------------

    def set_expression(self, expr) -> None:
        """Show `expr`, which may be a sympy object or a LaTeX string."""
        self._latex = mathrender.to_latex(expr)
        self._plain = mathrender.to_plain(expr)
        self._refresh()

    def set_row(self, row: Row) -> None:
        """Show a pre-decomposed `Row` from `mathrender.rows`."""
        self._latex, self._plain = row.latex, row.plain
        self._refresh()

    def set_palette_colours(self, palette: Palette,
                            colour: str | None = None) -> None:
        """Re-typeset for a new theme. The colour is baked into the image."""
        self.palette_obj = palette
        self.colour = colour or palette.text
        self._refresh()

    @property
    def latex(self) -> str:
        return self._latex

    @property
    def is_typeset(self) -> bool:
        """Whether mathematics is currently shown rather than the fallback."""
        return self._label.pixmap() is not None and not self._label.pixmap().isNull()

    # -- rendering -------------------------------------------------------

    def _ratio(self) -> float:
        handle = self.window().windowHandle() if self.window() else None
        if handle is not None:
            return float(handle.devicePixelRatio())
        return float(QGuiApplication.primaryScreen().devicePixelRatio())

    def _refresh(self) -> None:
        self._token += 1
        self._show_text()                       # stands in until the image lands

        if not mathrender.is_renderable(self._latex):
            return

        ratio = self._ratio()
        image = mathrender.pixmap(
            self._latex, self.colour, self.point_size, ratio, cached_only=True
        )
        if image is not None:
            self._show_pixmap(image)            # cache hit: no flicker, no job
            return

        QThreadPool.globalInstance().start(
            _RenderJob(self._token, self._latex, self.colour,
                       self.point_size, ratio, self._signals)
        )

    def _on_rendered(self, token: int, data: bytes) -> None:
        if token != self._token or not data:
            return                              # superseded, or unrenderable
        image = mathrender.to_pixmap(data, self._ratio())
        if image is not None:
            self._show_pixmap(image)

    def _show_pixmap(self, image) -> None:
        # Word wrap applies to text only, and left on it makes the label ask
        # for a height-for-width it cannot satisfy with a pixmap -- which shows
        # up as equations clipped top and bottom.
        self._label.setWordWrap(False)
        self._label.setPixmap(image)
        self._label.setToolTip(self._plain)
        self._label.setMinimumHeight(
            int(image.height() / image.devicePixelRatio())
        )

    def _show_text(self) -> None:
        self._label.setPixmap(_null_pixmap())
        self._label.setWordWrap(True)
        self._label.setMinimumHeight(0)
        self._label.setText(self._plain)
        self._label.setToolTip("")
        self._label.setStyleSheet(
            f"background: transparent;"
            f' font-family: "Cascadia Mono", "Consolas", monospace;'
            f" font-size: {self.point_size - 3:.0f}px; color: {self.colour};"
        )

    # -- context menu ----------------------------------------------------

    def _show_menu(self, position) -> None:
        if not self._plain:
            return
        menu = QMenu(self)
        menu.addAction("Copy LaTeX", lambda: _copy(self._latex))
        menu.addAction("Copy Python", lambda: _copy(self._plain))
        menu.exec(self.mapToGlobal(position))


class MathBlock(QWidget):
    """A stack of typeset rows, optionally introduced by a lead-in label.

    Used wherever the answer is not a single expression: a `Piecewise`, the two
    components of a system, or the fundamental solution set. The lead-in
    (``y(t) =``) is set once against the first row rather than repeated.
    """

    def __init__(self, palette: Palette, expr=None, *, lead: str = "",
                 point_size: float = mathrender.DEFAULT_POINT_SIZE,
                 colour: str | None = None, parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette
        self.point_size = float(point_size)
        self.colour = colour or palette.text
        self.lead = lead
        self._rows: list[MathLabel] = []

        self.setStyleSheet("background: transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(10)

        if expr is not None:
            self.set_expression(expr)

    def set_expression(self, expr) -> None:
        self.set_rows(mathrender.rows(expr))

    def set_rows(self, rows: list[Row]) -> None:
        self._clear()
        for index, row in enumerate(rows):
            line = QWidget()
            line.setStyleSheet("background: transparent;")
            layout = QHBoxLayout(line)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(8)

            if self.lead:
                # Only the first row is introduced; the rest are indented to
                # the same column so the equals signs line up. The width comes
                # from a label that actually holds the text and has already
                # been styled -- measuring the raw font metrics instead gives a
                # value too small for the style sheet's font, and the lead-in
                # arrives clipped to its last few characters.
                lead = QLabel(self.lead)
                lead.setProperty("role", "mono")
                lead.setStyleSheet(
                    f"background: transparent; font-size: 13px;"
                    f" color: {self.palette_obj.text};"
                )
                lead.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                lead.setFixedWidth(lead.sizeHint().width() + 6)
                if index:
                    lead.setText("")
                layout.addWidget(lead)

            label = MathLabel(
                self.palette_obj, point_size=self.point_size, colour=self.colour
            )
            label.set_row(row)
            layout.addWidget(label)
            self._rows.append(label)

            if row.condition:
                note = QLabel(row.condition)
                note.setProperty("role", "muted")
                note.setStyleSheet("background: transparent; font-size: 11.5px;")
                note.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                layout.addWidget(note)

            layout.addStretch(1)
            self._layout.addWidget(line)

    def set_palette_colours(self, palette: Palette,
                            colour: str | None = None) -> None:
        self.palette_obj = palette
        self.colour = colour or palette.text
        for label in self._rows:
            label.set_palette_colours(palette, colour)

    def _clear(self) -> None:
        self._rows.clear()
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                # Reparenting is what actually removes it from the display;
                # dropping the layout item alone leaves the old rows painted
                # on top of the new ones.
                widget.setParent(None)
                widget.deleteLater()


def _copy(text: str) -> None:
    QGuiApplication.clipboard().setText(text)


def _null_pixmap():
    from PySide6.QtGui import QPixmap

    return QPixmap()
