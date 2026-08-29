"""Home: the gallery of problems and the showcase entry points."""

from __future__ import annotations

from threading import Event

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import catalog, thumbnails
from ..theme import Palette
from ..widgets.cards import ChipBar, ProblemCard, ShowcaseTile
from ..widgets.controls import add_heading
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
            "A from-scratch ODE solver, and two ways in. The <b>Learning Hub</b> "
            "is about solving equations — techniques, worked step by step, and "
            "the methods done by hand. <b>Solver Studio</b> is about the solvers "
            "themselves — adaptivity, stiffness and accuracy."
        )
        subtitle.setTextFormat(Qt.RichText)
        subtitle.setProperty("role", "subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # -- showcase tiles, one group per section -----------------------
        groups = [
            ("Learning Hub", [
                ("Course Map", "Every unit and lesson, and how far through "
                 "you are. Start here.", palette.accent, "course"),
                ("Lessons", "One technique at a time: what it is, examples "
                 "worked through, and practice that grades your own answer.",
                 palette.success, "lessons"),
                ("Solve Step by Step", "See which technique solves your "
                 "equation, worked a line at a time — and check your own answer.",
                 palette.warning, "steps"),
                ("Laplace Transforms", "Transform the equation, solve for "
                 "Y(s), and invert it back.", palette.danger, "laplace"),
                ("Methods by Hand", "Euler and RK4 as they are taught: the "
                 "arithmetic, beside the exact answer.", palette.accent, "byhand"),
                ("Worked Problems", "Mixing tanks, circuits and cooling — "
                 "where the equation comes from.", palette.success, "worked"),
            ]),
            ("Solver Studio", [
                ("Solver Lab", "Solve anything, and watch the step size adapt "
                 "underneath the trajectory.", palette.accent, "lab"),
                ("Phase Portrait", "Vector fields, nullclines and fixed points. "
                 "Click anywhere to launch a trajectory.", palette.success,
                 "portrait"),
                ("Stiffness Explorer", "See why stiff problems break explicit "
                 "methods — eigenvalues crossing the stability boundary.",
                 palette.danger, "stiffness"),
                ("Method Race", "Four integrators, one problem, live evaluation "
                 "counters and a finish line.", palette.warning, "race"),
            ]),
        ]
        for group_index, (title, specs) in enumerate(groups):
            add_heading(layout, title, space_above=6 if group_index == 0 else 12)
            tiles = QGridLayout()
            tiles.setSpacing(12)
            for index, (name, blurb, colour, screen) in enumerate(specs):
                tile = ShowcaseTile(name, blurb, colour)
                tile.clicked.connect(lambda s=screen: self.showcase_chosen.emit(s))
                tiles.addWidget(tile, index // 2, index % 2)
            layout.addLayout(tiles)

        # -- gallery -----------------------------------------------------
        add_heading(layout, "Problem gallery", space_above=10)

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
