"""A lesson's chapter, drawn as one continuous document.

The blocks are defined in `lessons.chapter`; this turns them into a page. The
design choices are the ones a printed textbook makes, because the complaint
this answers was that the lessons did not read like one:

* prose in paragraphs with room between the lines, not cards;
* sections numbered, so "see 3" means something;
* equations displayed on their own line, centred, with their number at the
  margin;
* definitions, theorems and proofs set apart in a tinted box and numbered in
  one sequence, warnings in the warning colour;
* worked examples in their own panel -- problem, solution, answer -- and
  numbered;
* graphs drawn from the expressions the chapter states, not from pictures.
"""

from __future__ import annotations

import re
from html import escape

import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from .. import richtext, theme
from ..lessons import glossary
from ..theme import Palette
from .mathlabel import MathLabel

__all__ = ["ChapterView", "evaluate_curve"]

_BOX_TITLES = {
    "definition": "Definition",
    "theorem": "Theorem",
    "proof": "Proof",
    "remark": "Remark",
    "warning": "Watch out",
}

#: Samples per plotted curve. Enough that a decaying oscillation over a few
#: periods is smooth; the plots are static, so the cost is paid once.
_SAMPLES = 600


#: ``e^(t + y)`` and ``e^t`` in prose, as superscripts. Prose is written in
#: plain text so it reads in the source and in a screen reader; on the page an
#: exponent should look like one.
_GROUPED_POWER = re.compile(r"\^\(([^()]*)\)")
_BARE_POWER = re.compile(r"\^([A-Za-z0-9.−-]+)")


def superscripts(html: str) -> str:
    html = _GROUPED_POWER.sub(r"<sup>\1</sup>", html)
    return _BARE_POWER.sub(r"<sup>\1</sup>", html)


_INTEGRAL = re.compile(r"\\int(?![a-z])\s*")


def _spaced(latex: str) -> str:
    """Mathtext sets the integral sign on top of whatever follows it -- "∫y dy"
    printed with the y inside the sign. A thin space after it is enough."""
    return _INTEGRAL.sub(lambda _: "\\int\\;\\;", latex)


def evaluate_curve(curve, t_range) -> tuple[np.ndarray, np.ndarray]:
    """``(xs, ys)`` for one `Curve`, over `t_range`. Non-finite points are NaN.

    Shared with the tests, so what they check is what the page draws.
    """
    import sympy as sp

    t = sp.Symbol("t", real=True)
    grid = np.linspace(float(t_range[0]), float(t_range[1]), _SAMPLES)

    def values(text: str) -> np.ndarray:
        expr = sp.sympify(text, locals={"t": t})
        function = sp.lambdify(t, expr, "numpy")
        with np.errstate(all="ignore"):
            out = np.asarray(function(grid), dtype=complex) * np.ones_like(grid)
        real = np.where(np.abs(out.imag) < 1e-9, out.real, np.nan)
        return np.where(np.isfinite(real), real, np.nan)

    if curve.y:
        return values(curve.expr), values(curve.y)
    return grid, values(curve.expr)


class ChapterView(QWidget):
    """A whole chapter. Built once per lesson; the page scrolls around it.

    Given `lesson_key`, the first use of each glossary term in the chapter's
    prose is a link: hovering shows its definition, and activating it emits
    `term_chosen` with the term's name, for the window to open the glossary
    there. Terms the lesson itself teaches are not linked (see
    `glossary.link_terms`).
    """

    #: The name of a glossary term the reader followed.
    term_chosen = Signal(str)

    def __init__(self, sections, palette: Palette, parent=None, *,
                 lesson_key: str = "") -> None:
        super().__init__(parent)
        self.palette_obj = palette
        self._counts = {"box": 0, "example": 0}
        self._lesson_key = lesson_key
        #: Terms already linked on this page: one link per term, at its first
        #: use, not one per paragraph.
        self._linked: set[int] = set()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        self._layout = layout

        for number, section in enumerate(sections, start=1):
            self._section(number, section)

    # -- pieces ----------------------------------------------------------

    def _paragraph(self, layout, text: str, *, muted: bool = False) -> None:
        for part in (piece.strip() for piece in text.split("\n\n")):
            if not part:
                continue
            body = superscripts(richtext.emphasise(part))
            if self._lesson_key:
                body = glossary.link_terms(body, self._lesson_key, self._linked,
                                           self.palette_obj.accent)
            label = QLabel(f'<p style="line-height: 145%;">{body}</p>')
            label.setTextFormat(Qt.RichText)
            label.setWordWrap(True)
            if "<a " in body:
                # Keyboard-reachable as well as clickable: a link only a mouse
                # can follow is not there for a keyboard reader.
                label.setTextInteractionFlags(
                    Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse
                    | Qt.LinksAccessibleByKeyboard)
                label.setOpenExternalLinks(False)
                label.linkActivated.connect(self._follow)
                label.linkHovered.connect(self._define)
            else:
                label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            label.setAccessibleName("paragraph")
            label.setAccessibleDescription(richtext.plain(part))
            label.setStyleSheet(theme.scaled("font-size: 14px;"))
            if muted:
                label.setProperty("role", "muted")
            layout.addWidget(label)

    def _follow(self, href: str) -> None:
        term = glossary.term_of(href)
        if term is not None:
            self.term_chosen.emit(term.name)

    def _define(self, href: str) -> None:
        """The definition beside the cursor while it rests on a term."""
        term = glossary.term_of(href)
        if term is None:
            QToolTip.hideText()
            return
        QToolTip.showText(QCursor.pos(),
                              f"<b>{escape(term.name)}</b><br>"
                              f"{escape(term.definition)}"
                              "<br><i>Click for the glossary entry.</i>",
                              self)

    def _display(self, layout, latex: str, number: str = "") -> None:
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(MathLabel(self.palette_obj, _spaced(latex), point_size=16))
        row.addStretch(1)
        if number:
            tag = QLabel(f"({number})")
            tag.setProperty("role", "muted")
            row.addWidget(tag, 0, Qt.AlignVCenter)
        layout.addLayout(row)

    def _section(self, number: int, section) -> None:
        heading = QLabel(f"{number}   {section.title}")
        heading.setProperty("role", "heading")
        heading.setWordWrap(True)
        heading.setStyleSheet(theme.scaled("font-size: 19px; font-weight: 600;"))
        heading.setAccessibleName(f"Section {number}: {section.title}")
        self._layout.addSpacing(10)
        self._layout.addWidget(heading)

        for block in section.blocks:
            builder = getattr(self, f"_block_{block.kind}")
            builder(block)

    def _framed(self, accent: str, tint: bool = True) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("chapterBox")
        background = self.palette_obj.surface_alt if tint else "transparent"
        frame.setStyleSheet(
            f"QFrame#chapterBox {{ border-left: 4px solid {accent}; "
            f"background: {background}; border-radius: 6px; }}")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 12, 18, 14)
        layout.setSpacing(8)
        return frame, layout

    # -- blocks ----------------------------------------------------------

    def _block_para(self, block) -> None:
        self._paragraph(self._layout, block.text)

    def _block_display(self, block) -> None:
        self._display(self._layout, block.latex, block.number)

    def _block_box(self, block) -> None:
        palette = self.palette_obj
        accent = {"warning": palette.warning, "proof": palette.text_muted,
                  "remark": palette.text_muted}.get(block.box, palette.accent)
        frame, layout = self._framed(accent, tint=block.box != "proof")
        name = _BOX_TITLES.get(block.box, block.box.title())
        if block.box in ("definition", "theorem"):
            self._counts["box"] += 1
            name = f"{name} {self._counts['box']}"
        heading = QLabel(f"<b>{name}</b>" + (f" — {block.title}" if block.title else ""))
        heading.setTextFormat(Qt.RichText)
        heading.setWordWrap(True)
        heading.setStyleSheet(theme.scaled(f"color: {accent}; font-size: 14px;"))
        layout.addWidget(heading)
        self._paragraph(layout, block.body)
        if block.latex:
            self._display(layout, block.latex)
        frame.setAccessibleName(f"{name}: {block.title}")
        self._layout.addWidget(frame)

    def _block_worked(self, block) -> None:
        palette = self.palette_obj
        self._counts["example"] += 1
        frame, layout = self._framed(palette.success)
        heading = QLabel(f"<b>Example {self._counts['example']}</b> — {block.title}")
        heading.setTextFormat(Qt.RichText)
        heading.setWordWrap(True)
        heading.setStyleSheet(theme.scaled(f"color: {palette.success}; font-size: 14px;"))
        layout.addWidget(heading)
        self._paragraph(layout, block.problem)

        solution = QLabel("<i>Solution.</i>")
        solution.setTextFormat(Qt.RichText)
        layout.addWidget(solution)
        for step in block.steps:
            self._paragraph(layout, step.prose)
            if step.latex:
                self._display(layout, step.latex)

        if block.answer_latex or block.answer:
            answer = QLabel("<b>Answer.</b>")
            answer.setTextFormat(Qt.RichText)
            layout.addWidget(answer)
            if block.answer_latex:
                self._display(layout, block.answer_latex)
            else:
                plain = QLabel(block.answer)
                plain.setStyleSheet("font-family: Cascadia Mono, Consolas, monospace;")
                layout.addWidget(plain, 0, Qt.AlignHCenter)
        frame.setAccessibleName(f"Example {self._counts['example']}: {block.title}")
        self._layout.addWidget(frame)

    def _block_plot(self, block) -> None:
        palette = self.palette_obj
        title = QLabel(f"<b>{block.title}</b>")
        title.setTextFormat(Qt.RichText)
        self._layout.addWidget(title)

        plot = pg.PlotWidget()
        plot.setBackground(palette.plot_background)
        plot.showGrid(x=True, y=True, alpha=0.18)
        plot.setMinimumHeight(280)
        plot.setMenuEnabled(False)
        plot.setMouseEnabled(x=False, y=False)
        plot.setLabel("bottom", block.xlabel)
        plot.setLabel("left", block.ylabel)
        if any(curve.label for curve in block.curves):
            plot.addLegend(offset=(-10, 10))
        for index, curve in enumerate(block.curves):
            xs, ys = evaluate_curve(curve, block.t)
            colour = palette.series[index % len(palette.series)]
            plot.plot(xs, ys, pen=pg.mkPen(colour, width=2.2),
                      name=curve.label or None, connect="finite")
        if block.ylim is not None:
            plot.setYRange(*block.ylim, padding=0.02)
        plot.setAccessibleName(f"graph: {block.title}")
        plot.setAccessibleDescription(block.caption)
        self._layout.addWidget(plot)
        self._paragraph(self._layout, block.caption, muted=True)

    def _block_figure(self, block) -> None:
        from .lessonfigure import build_figure

        if block.caption:
            self._paragraph(self._layout, block.caption, muted=True)
        figure = build_figure(block.key, self.palette_obj)
        if figure is not None:
            self._layout.addWidget(figure)
