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
from .soon import run_soon

__all__ = ["MathLabel", "MathBlock"]


class _RenderSignals(QObject):
    ready = Signal(int, object)          # token, QPixmap


class _Wanted:
    """The one render a label still wants, readable from the worker.

    A plain object rather than an attribute of the label, because a job can
    outlive its label: the page it sat on is gone, and the job is still in
    the queue. `token` is None once the label has been destroyed.
    """

    __slots__ = ("token",)

    def __init__(self) -> None:
        self.token: int | None = 0


_RENDER_POOL: QThreadPool | None = None


def render_pool() -> QThreadPool:
    """The one thread every equation is typeset on.

    mathtext is not safe to run twice at once: a Linux CI worker segfaulted
    with three renders inside it together. A lock around the render was the
    first fix, and it made Linux legs hang until their timeout. A pool of one
    thread serialises the renders without a lock, and keeps them off the
    shared pool, so a queue of equations never holds up a solve or an analysis.
    """
    global _RENDER_POOL
    if _RENDER_POOL is None:
        _RENDER_POOL = QThreadPool()
        _RENDER_POOL.setMaxThreadCount(1)
    return _RENDER_POOL


class _RenderJob(QRunnable):
    """Typesets one expression off the GUI thread."""

    def __init__(self, token: int, latex: str, colour: str, point_size: float,
                 ratio: float, signals: _RenderSignals,
                 wanted: _Wanted | None = None) -> None:
        super().__init__()
        self.token = token
        self.latex = latex
        self.colour = colour
        self.point_size = point_size
        self.ratio = ratio
        self.signals = signals
        self.wanted = wanted
        self.setAutoDelete(True)

    def run(self) -> None:
        # Skip a render nobody will see. Every page typesets its equations on
        # the shared pool, and leaving a page or re-typing a label left those
        # jobs queued: thousands over a long visit, each ~15 ms, all ahead of
        # whatever the reader asked for next -- a worked example once waited
        # over a minute behind them. Checked here, when the job is reached,
        # because that is when it is known whether anyone still wants it.
        if self.wanted is not None and self.wanted.token != self.token:
            return
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

    def watch(self, label: MathLabel) -> None:
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


def _watch_font(label: MathLabel) -> None:
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
        self._pending = False
        #: The text scale the current bitmap was rendered at. Compared against
        #: on a font change, so a re-render happens exactly when it is needed.
        self._scale = theme.text_scale()
        self._signals = _RenderSignals()
        self._signals.ready.connect(self._on_rendered)
        # What a queued job checks before it renders. Cleared when the label
        # goes, through a closure over the object alone: nothing that refers
        # to the label itself may run once it is being destroyed.
        self._wanted = _Wanted()
        wanted = self._wanted
        self.destroyed.connect(lambda *_: setattr(wanted, "token", None))

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
        self._wanted.token = self._token
        self._scale = theme.text_scale()
        self._pending = False

        if not mathrender.is_renderable(self._latex):
            self._show_text()
            return

        ratio = self._ratio()
        size = self.rendered_point_size()
        image = mathrender.pixmap(
            self._latex, self.colour, size, ratio, cached_only=True
        )
        if image is not None:
            self._show_pixmap(image)            # cache hit: no flicker, no job
            return

        self._show_waiting()
        # Decided on the next pass of the event loop, not here: a label is
        # usually given its expression in its constructor, before anything has
        # put it on a page, and only once it is placed can it tell whether
        # that page is hidden.
        self._pending = True
        run_soon(self, self._start_if_wanted)

    def _start_if_wanted(self) -> None:
        if not self._pending:
            return
        if self._offstage():
            # On a screen or tab that is not in front. Typesetting it now is
            # work for an equation nobody can see, and it is not free: the app
            # builds every screen at launch, and those renders shared the pool
            # with the open lesson's -- 51 jobs at once, each 8 ms alone and
            # over a second in that crowd, so the lesson in front showed raw
            # LaTeX for five to fifteen seconds. `showEvent` catches up.
            return
        self._pending = False
        render_pool().start(
            _RenderJob(self._token, self._latex, self.colour,
                       self.rendered_point_size(), self._ratio(),
                       self._signals, self._wanted)
        )

    def _offstage(self) -> bool:
        """Whether this label sits on a hidden page of its window.

        Not merely "not shown": a label nobody has put in a window, or one on
        the front page of a window not shown yet, typesets as it always did.
        Only a label its own window is hiding waits.
        """
        window = self.window()
        return window is not self and not self.isVisibleTo(window)

    def showEvent(self, event) -> None:         # noqa: N802
        super().showEvent(event)
        if self._pending:
            self._refresh()

    def _show_waiting(self) -> None:
        """What stands in while the image is typeset.

        The plain form where it reads as mathematics -- ``exp(-t)`` from a sympy
        expression -- and nothing where it would not. An equation given as
        LaTeX has only its source for a plain form, and showing the source of a
        fraction, backslashes and braces, for the moment before the image lands
        looked like a broken page, which is what a first-time reader took it
        for.
        """
        if self._plain == self._latex:
            self._label.setPixmap(_null_pixmap())
            self._label.setText("")
            # Blank is not unnamed: a screen reader reaching it before the
            # image lands gets what it will get afterwards.
            described = self._plain or "equation"
            for widget in (self, self._label):
                widget.setAccessibleName("equation")
                widget.setAccessibleDescription(described)
            return
        self._show_text()

    def _on_rendered(self, token: int, data: bytes) -> None:
        if token != self._token:
            return                              # superseded
        if not data:
            self._show_text()                   # could not be typeset after all
            return
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


def equation_label(palette: Palette, equation: str, conditions: str = "", *,
                   point_size: float = mathrender.DEFAULT_POINT_SIZE) -> QWidget:
    """A question's equation, typeset in the notation a course writes.

    The stored text -- ``y' = 2*t*y`` -- stays the label's plain form, so a
    screen reader and "Copy" still get something typeable. Where the text
    cannot be read as mathematics, the code itself is shown, as before.

    A generated question's `shown` text may run to several lines, each an
    equation with its conditions after three spaces and a comma, and may
    open with words: ``the answer handed in:   y = 5*exp(2*t) + C1``. Each
    line is typeset on its own and the words stay words.
    """
    if "\n" in equation and not conditions:
        box = QWidget()
        lines = QVBoxLayout(box)
        lines.setContentsMargins(0, 0, 0, 0)
        lines.setSpacing(4)
        for line in equation.splitlines():
            if line.strip():
                lines.addWidget(equation_label(palette, line,
                                               point_size=point_size))
        return box

    prefix = ""
    if ":" in equation and not conditions:
        prefix, equation = (part.strip() for part in equation.split(":", 1))
    if ",   " in equation and not conditions:
        equation, conditions = (part.strip() for part in equation.split(",   ", 1))

    shown = equation + (f",   {conditions}" if conditions else "")
    latex = mathrender.equation_latex(equation, conditions)
    if latex is not None:
        label = MathLabel(palette, point_size=point_size)
        label.set_row(Row(latex=latex, plain=shown))
        widget: QWidget = label
    else:
        fallback = QLabel(shown)
        fallback.setStyleSheet(
            theme.scaled("font-family: Cascadia Mono, Consolas, monospace; "
                         f"font-size: {point_size:.0f}px;")
        )
        fallback.setWordWrap(True)
        widget = fallback
    if not prefix:
        return widget
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    words = QLabel(prefix[0].upper() + prefix[1:] + ":")
    words.setProperty("role", "muted")
    layout.addWidget(words)
    layout.addWidget(widget)
    layout.addStretch(1)
    return row
