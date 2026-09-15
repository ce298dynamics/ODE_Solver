"""A lesson's own picture, with the sliders that make it a demonstration.

A note can say that raising the harvest rate eventually wipes out both
equilibria. A figure can let someone raise it and watch the two dots slide
together and vanish, which is a different kind of knowing. That is the whole
argument for this module, and it is why each figure is built around the one
parameter the lesson turns on rather than around a general plotting API.

Nothing here computes mathematics of its own. The slope field comes from
`analysis.slope_field`, the equilibria from `analysis.phase_line`, the step
tables from `byhand.walk` and `byhand.refinement`, the transforms from
`laplace`, and the solution curves from the library's own `solve`. A figure
that disagreed with the tools would be worse than no figure, so it is not
given the chance to.

A lesson names a figure by key (`Lesson.figure`), because `lessons/` holds
content and must stay free of Qt -- `tests/test_lessons.py` imports it with
PySide6 blocked and would fail if that ever stopped being true. The registry
that turns a key into a widget lives here, at the other end.

**One module per unit.** Six figures fitted in one file; eighteen do not, and
`lessons.py` was made a package at very nearly this size for the same reason.
The base class and the registry stay here; the figures themselves sit beside
the unit whose lessons show them.
"""

from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

from ...theme import Palette
from ..controls import ValueSlider

__all__ = ["LessonFigure"]

#: Height of the plot itself. A lesson figure sits inside a scrolling column of
#: note cards, so it has to be tall enough to read and short enough that the
#: notes above and below it are still visibly part of the same page.
_PLOT_HEIGHT = 300


class LessonFigure(QFrame):
    """A plot, a caption and a row of sliders, themed like the note cards.

    Subclasses supply `title`, `caption`, the sliders they want, and a `draw`
    that redraws from the current slider values. Everything else -- the frame,
    the plot, the palette, and the wiring that redraws on a change -- is here,
    because three figures with three copies of it would drift apart.
    """

    title = ""
    caption = ""
    #: How many plots side by side. Two where the lesson is genuinely two
    #: pictures -- the response in time *and* the response against frequency
    #: are different claims, and overlaying them would say neither clearly.
    plots = 1

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.palette_obj = palette
        self.setProperty("role", "panel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 13, 16, 14)
        layout.setSpacing(8)

        heading = QLabel(self.title)
        heading.setProperty("role", "heading")
        layout.addWidget(heading)

        if self.caption:
            blurb = QLabel(self.caption)
            blurb.setProperty("role", "muted")
            blurb.setWordWrap(True)
            layout.addWidget(blurb)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        #: Every plot, in order. `self.plot` is the first, so the figures
        #: written before this existed are untouched.
        self.panes: list[pg.PlotWidget] = []
        for _ in range(max(int(self.plots), 1)):
            pane = pg.PlotWidget()
            pane.setBackground(palette.plot_background)
            pane.showGrid(x=True, y=True, alpha=0.18)
            pane.setMinimumHeight(_PLOT_HEIGHT)
            self.panes.append(pane)
            row.addWidget(pane, 1)
        self.plot = self.panes[0]
        layout.addLayout(row)

        #: What the figure currently says in words. Kept beside the picture
        #: because the number that changed is usually the point.
        self.readout = QLabel("")
        self.readout.setProperty("role", "mono")
        self.readout.setWordWrap(True)
        layout.addWidget(self.readout)

        self.sliders: dict[str, ValueSlider] = {}
        self._grid = QGridLayout()
        self._grid.setContentsMargins(0, 4, 0, 0)
        self._grid.setHorizontalSpacing(18)
        layout.addLayout(self._grid)

        self.build_sliders()
        self.redraw()

    # -- scaffolding -----------------------------------------------------

    def add_slider(self, name: str, label: str, low: float, high: float,
                   value: float, *, log: bool = False, hint: str = "") -> None:
        slider = ValueSlider(label, low, high, value, log=log, hint=hint)
        # `preview` rather than `committed`: these figures redraw in a few
        # milliseconds, and a figure that lags behind the thumb stops feeling
        # like a demonstration of anything.
        slider.preview.connect(lambda _: self.redraw())
        self.sliders[name] = slider
        row, column = divmod(len(self.sliders) - 1, 2)
        self._grid.addWidget(slider, row, column)

    def value(self, name: str) -> float:
        return self.sliders[name].value()

    def colour(self, index: int) -> str:
        series = self.palette_obj.series
        return series[index % len(series)]

    def build_sliders(self) -> None:
        """Subclass hook: call `add_slider` for each control."""

    def draw(self) -> None:
        """Subclass hook: redraw from the current slider values."""
        raise NotImplementedError

    def redraw(self) -> None:
        """`draw`, and then say in words what it drew.

        Every figure here already writes its own readout -- the number that
        changed is usually the point -- so the text alternative a plot owes a
        reader who is not looking at it has been sitting beside the picture
        all along, unattached to it. This is the attachment, done once for
        every figure rather than asked of each of them, because an accessible
        description that each subclass has to remember is one that the next
        subclass forgets.
        """
        self.draw()
        self.publish_text()

    def publish_text(self) -> None:
        """Hang the caption and the readout on the plots as alt text."""
        words = " ".join(part for part in (self.caption, self.readout.text())
                         if part)
        for index, pane in enumerate(self.panes):
            pane.setAccessibleName(
                self.title if len(self.panes) == 1
                else f"{self.title}, plot {index + 1} of {len(self.panes)}"
            )
            pane.setAccessibleDescription(words)
        self.setAccessibleName(self.title)
        self.setAccessibleDescription(words)
