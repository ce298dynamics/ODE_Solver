"""Home: the gallery of problems and the showcase entry points."""

from __future__ import annotations

from threading import Event

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import catalog, thumbnails
from ..theme import Palette
from ..widgets.cards import ProblemCard, ChipBar, ShowcaseTile
from ..widgets.flow import FlowWidget

__all__ = ["HomeScreen"]


class _ThumbSignals(QObject):
    ready = Signal(str, str)     # key, path
    done = Signal()


class _ThumbJob(QRunnable):
    """Renders thumbnails off the GUI thread so the window appears immediately.

    Rendering nineteen previews takes a few seconds on a cold cache, which is
    far longer than the screen may live for -- switching theme rebuilds every
    screen, and tests construct and destroy them freely. The job therefore
    watches a cancellation flag and treats a destroyed receiver as a normal
    stop rather than an error.
    """

    def __init__(self, palette: Palette, signals: _ThumbSignals,
                 cancelled: Event) -> None:
        super().__init__()
        self.palette = palette
        self.signals = signals
        self.cancelled = cancelled

    def run(self) -> None:
        for key in catalog.keys():
            if self.cancelled.is_set():
                return
            entry = catalog.get(key)
            path = thumbnails.thumbnail_path(entry, self.palette)
            if not path.exists():
                try:
                    path.write_bytes(thumbnails.render_thumbnail(entry, self.palette))
                except Exception:
                    continue
            try:
                self.signals.ready.emit(key, str(path))
            except RuntimeError:
                # The receiving screen was destroyed mid-render.
                return
        try:
            self.signals.done.emit()
        except RuntimeError:
            pass


class HomeScreen(QWidget):
    """Problem gallery with tag filtering, plus links to the showcase screens."""

    problem_chosen = Signal(str)     # key
    showcase_chosen = Signal(str)    # screen name

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.palette = palette
        self._cards: dict[str, ProblemCard] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        page = QWidget()
        scroll.setWidget(page)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(18)

        # -- masthead ----------------------------------------------------
        title = QLabel("odesuite")
        title.setProperty("role", "title")
        layout.addWidget(title)

        subtitle = QLabel(
            "A from-scratch ODE solver — 13 methods, adaptive stepping, stiff "
            "systems, DAEs, events and dense output.  Pick a problem to begin."
        )
        subtitle.setProperty("role", "subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # -- showcase tiles ----------------------------------------------
        layout.addSpacing(6)
        showcase_heading = QLabel("Start here")
        showcase_heading.setProperty("role", "heading")
        layout.addWidget(showcase_heading)

        tiles = QGridLayout()
        tiles.setSpacing(12)
        specs = [
            ("Solver Lab", "Solve anything, and watch the step size adapt "
             "underneath the trajectory.", palette.accent, "lab"),
            ("Phase Portrait", "Vector fields, nullclines and fixed points. "
             "Click anywhere to launch a trajectory.", palette.success, "portrait"),
            ("Stiffness Explorer", "See why stiff problems break explicit "
             "methods — eigenvalues crossing the stability boundary.",
             palette.danger, "stiffness"),
            ("Method Race", "Four integrators, one problem, live evaluation "
             "counters and a finish line.", palette.warning, "race"),
        ]
        for index, (name, blurb, colour, screen) in enumerate(specs):
            tile = ShowcaseTile(name, blurb, colour)
            tile.clicked.connect(lambda s=screen: self.showcase_chosen.emit(s))
            tiles.addWidget(tile, index // 2, index % 2)
        layout.addLayout(tiles)

        # -- gallery -----------------------------------------------------
        layout.addSpacing(10)
        gallery_heading = QLabel("Problem gallery")
        gallery_heading.setProperty("role", "heading")
        layout.addWidget(gallery_heading)

        self.chips = ChipBar(catalog.all_tags())
        self.chips.changed.connect(self._apply_filter)
        layout.addWidget(self.chips)

        self.status = QLabel("rendering previews…")
        self.status.setProperty("role", "muted")
        self.status.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.status)

        self.grid_host = FlowWidget(spacing=14)
        for key in catalog.keys():
            entry = catalog.get(key)
            card = ProblemCard(entry, palette)
            card.clicked.connect(lambda k=key: self.problem_chosen.emit(k))
            self.grid_host.addWidget(card)
            self._cards[key] = card
        layout.addWidget(self.grid_host)
        layout.addStretch(1)

        self._start_thumbnails()

    # -- thumbnails ------------------------------------------------------

    def _start_thumbnails(self) -> None:
        self._cancelled = Event()
        self._signals = _ThumbSignals()
        self._signals.ready.connect(self._on_thumb)
        self._signals.done.connect(
            lambda: self.status.setText(f"{len(self._cards)} problems")
        )
        # Cancel on destruction so a rebuild (theme switch) does not leave an
        # orphaned job emitting into a dead object.
        self.destroyed.connect(lambda *_: self._cancelled.set())
        QThreadPool.globalInstance().start(
            _ThumbJob(self.palette, self._signals, self._cancelled)
        )

    def closeEvent(self, event) -> None:            # noqa: N802
        self._cancelled.set()
        super().closeEvent(event)

    def _on_thumb(self, key: str, path: str) -> None:
        card = self._cards.get(key)
        if card is not None:
            from pathlib import Path

            card.set_thumbnail(Path(path))

    # -- filtering -------------------------------------------------------

    def _apply_filter(self, tag: str) -> None:
        visible = 0
        for key, card in self._cards.items():
            keep = tag == "all" or tag in catalog.get(key).tags
            card.setVisible(keep)
            visible += int(keep)
        self.status.setText(
            f"{visible} problems" + ("" if tag == "all" else f" tagged “{tag}”")
        )
        self.grid_host.flow.invalidate()
        self.grid_host.updateGeometry()
