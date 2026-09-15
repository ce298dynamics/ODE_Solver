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
* **It grows with the reader's text.** An equation here is a *bitmap*, so it
  cannot inherit a font size the way the prose around it does, and the point
  size a caller asks for is a size chosen against the operating system's
  default text. Every render therefore multiplies it by `theme.text_scale`,
  and an application font change re-renders rather than leaving the maths --
  which is the content -- the only thing on the page that did not grow.

`MathBlock` stacks rows. It exists because mathtext cannot render a LaTeX
``cases`` or ``matrix`` environment at all, so anything with more than one line
-- a `Piecewise` solution, a system, a fundamental solution set -- has to be
composed by Qt rather than by LaTeX.
"""

from __future__ import annotations

import weakref

from PySide6.QtCore import QEvent, QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from .. import mathrender, theme
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


class _FontWatch(QObject):
    """One event filter for every `MathLabel` there will ever be.

    `changeEvent` below is the fast path and it is not reliable on its own.
    Measured, with the application style sheet installed -- which it always is
    in the running application, and is not in a test that builds one label:

        label state        events delivered by QApplication.setFont
        unpolished         ApplicationFontChange        -> re-renders
        polished           *none at all*                -> keeps a stale bitmap

    A widget is polished the moment it is shown, so the broken row is the only
    one the real application is ever in: raise the operating system's text
    scale with the window open and every equation keeps the bitmap it was first
    painted with, while the prose around it grows. The style sheet is what does
    it -- it gives the label a font of its own, so the application font no
    longer resolves through it and `FontChange` stops firing -- and polish is
    what removes the other notification.

    What does survive both is the event sent to the *application object*, which
    `QApplication::setFont` posts unconditionally. So one filter is installed
    there and the labels are held weakly behind it.

    One filter, not one per label: a filter on the application object sees
    every event in the application, and installing several hundred of those --
    one per equation on a lesson page -- is exactly the cost Qt's documentation
    warns about. This one compares an integer and returns.
    """

    def __init__(self) -> None:
        super().__init__()
        self._labels: weakref.WeakSet = weakref.WeakSet()

    def watch(self, label: "MathLabel") -> None:
        self._labels.add(label)

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.ApplicationFontChange:
            for label in list(self._labels):
                label.rescale_if_needed()
        return False


#: The single instance, created with the first label that needs it. Module
#: level rather than per-application because there is one `QApplication` in a
#: process and the tests reuse it.
_FONT_WATCH: _FontWatch | None = None


def _watch_font(label: "MathLabel") -> None:
    global _FONT_WATCH
    app = QApplication.instance()
    if app is None:
        return                          # headless rendering: no scale to track
    if _FONT_WATCH is None:
        _FONT_WATCH = _FontWatch()
        app.installEventFilter(_FONT_WATCH)
    _FONT_WATCH.watch(label)


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
        #: The text scale the current bitmap was rendered at. Compared against
        #: on a font change, so a re-render happens exactly when it is needed.
        self._scale = theme.text_scale()
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

        _watch_font(self)

        if expr is not None:
            self.set_expression(expr)

    #: Both of the events Qt uses to say a font changed. Measured rather than
    #: assumed: `QApplication.setFont` was expected to deliver
    #: `ApplicationFontChange` to every widget, and to a label that has never
    #: been shown it delivers only `FontChange`. Listening for one of them
    #: left the equations at whatever size they were first painted, which is
    #: the exact bug this handler exists to fix.
    _FONT_EVENTS = (QEvent.ApplicationFontChange, QEvent.FontChange)

    def changeEvent(self, event) -> None:
        """Re-typeset when the operating system's text scale changes.

        Guarded on the scale actually having moved, not merely on a font event
        having arrived: `FontChange` also fires when a style sheet touches this
        widget's own font, and re-rendering for each of those would put a job
        on the thread pool every time a theme is applied.
        """
        super().changeEvent(event)
        if event.type() not in self._FONT_EVENTS:
            return
        self.rescale_if_needed()

    def rescale_if_needed(self) -> None:
        """Re-typeset if the reader's text scale has moved since last time.

        The one guard both notifications funnel through -- `changeEvent` when
        Qt delivers a font event to this widget, and `_FontWatch` when it does
        not. Guarded on the scale actually having moved, not merely on a
        notification having arrived: `FontChange` also fires when a style sheet
        touches this widget's own font, and re-rendering for each of those
        would put a job on the thread pool every time a theme is applied.

        Every live label is re-rendered, not only the visible ones, and that is
        deliberate after measuring it. Deferring the hidden ones until they are
        shown was written and then removed: with 150 labels alive and none of
        them shown, one scale change costs 2.42s of rendering in total and
        0.15s before the call returns, against 0.12s deferred. That is a
        saving of two seconds on something a reader does roughly never, paid
        for with a second code path and a staleness flag -- and it broke two
        tests that build a label without showing it, which is a fair thing for
        a test of this to do.
        """
        if not self._latex:
            return
        if abs(theme.text_scale() - self._scale) > 0.005:
            self._refresh()

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

    def rendered_point_size(self) -> float:
        """The size this label actually typesets at.

        Distinct from `point_size`, which is what the caller asked for: the
        two differ by the reader's text scale, and the tests compare this
        against the body text's line height.
        """
        return self.point_size * theme.text_scale()

    def _refresh(self) -> None:
        self._token += 1
        self._scale = theme.text_scale()
        self._show_text()                       # stands in until the image lands

        if not mathrender.is_renderable(self._latex):
            return

        ratio = self._ratio()
        size = self.rendered_point_size()
        image = mathrender.pixmap(
            self._latex, self.colour, size, ratio, cached_only=True
        )
        if image is not None:
            self._show_pixmap(image)            # cache hit: no flicker, no job
            return

        QThreadPool.globalInstance().start(
            _RenderJob(self._token, self._latex, self.colour,
                       size, ratio, self._signals)
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
        # A typeset equation is an *image*, and an image with no alternative
        # text is invisible to a screen reader -- which in a reading
        # application is most of the content. The plain form is already
        # computed for the fallback path, so exposing it costs nothing and is
        # the single highest-value accessibility fix here.
        described = self._plain or "equation"
        self.setAccessibleName("equation")
        self.setAccessibleDescription(described)
        self._label.setAccessibleName("equation")
        self._label.setAccessibleDescription(described)
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
            theme.scaled(f"background: transparent;"
                         f' font-family: "Cascadia Mono", "Consolas", monospace;'
                         f" font-size: {self.point_size - 3:.0f}px; color: {self.colour};")
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
                    theme.scaled(f"background: transparent; font-size: 13px;"
                                 f" color: {self.palette_obj.text};")
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
                note.setStyleSheet(theme.scaled("background: transparent; font-size: 11.5px;"))
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
