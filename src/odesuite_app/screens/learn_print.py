"""Print: a worksheet with its solution key, and the formula sheet.

Every other screen in this application is answered by typing into a box, and
the examination all of it is preparing for is written by hand on paper. The gap
is not a detail: writing ``y = 3e^{-2t}`` out and typing it are different motor
tasks, the slips that cost marks are almost all slips of the pen, and a tool
that never puts a pen in your hand cannot rehearse them. This screen closes it.

Three things it produces, and one rule they share.

**A worksheet**, drawn from a unit, a paper or the whole course, with room
under each question to work it. The questions are the same draws the Unit Quiz
builds -- `exam.draw_from` and `exam.build`, unchanged -- so a printed paper is
a sat paper that happens to be on paper.

**Its key**, as a second file. Separate because a key stapled to the worksheet
is not a key, it is the answers three inches below the question. The working in
it is produced by the same narrator the "Show me" button runs, which is why it
is the slow part and why it happens on a worker thread with something to watch.

**The formula sheet**, collected from the sixty-five notes the lessons already
mark as formulas. Nothing is authored for it, so it cannot drift from what the
course teaches.

The rule: **the preview shows exactly what the worksheet will show, and no
more.** It would be easy, and would feel helpful, to label each question with
the lesson it came from. It is the one thing that must not happen -- choosing
the method is most of what a mixed paper asks, and a preview that named the
lesson would answer it before the page was printed. The key names them, because
by then the question has been attempted.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .. import exam
from .. import lessons as content
from .. import printable, theme
from ..theme import Palette
from ..widgets.controls import add_heading, control_panel
from ..widgets.mathlabel import MathLabel

__all__ = ["PrintScreen", "SOURCES", "sources"]

#: How many questions a worksheet offers by default. Longer than a check-up:
#: the cost of a printed page is in the printing, and a sheet you work over two
#: sittings is a perfectly ordinary thing, which a screen you sit at is not.
DEFAULT_LENGTH = 10

#: The key for "every unit", which is a choice neither a unit nor a paper
#: offers: a worksheet spanning the course but not sized like the final.
WHOLE_COURSE = "whole-course"

#: What a worksheet may be drawn from, as ``(kind, key, label)``. Built at call
#: time rather than at import, so it follows the curriculum rather than a copy.
SOURCES = "unit", "paper", "course"


def sources() -> list[tuple[str, str, str]]:
    """Everything a worksheet can be drawn from, in the order it is offered."""
    out: list[tuple[str, str, str]] = [
        ("unit", unit.key, f"Unit — {unit.title}")
        for unit in content.UNITS if unit.quizzable
    ]
    out += [("paper", paper.key, f"{paper.title} — {paper.reference}")
            for paper in exam.PAPERS]
    out.append(("course", WHOLE_COURSE, "Whole course — every unit"))
    return out


def draw(kind: str, key: str, length: int, seed: int) -> list:
    """`length` questions from whichever source was chosen.

    Each of the three routes already exists. A unit is `exam.draw_from` over
    its quizzable lessons, which is what the check-up does; a paper is
    `exam.build`, which is what the exam does; the whole course is a paper
    whose units are all of them -- assembled here rather than added to
    `exam.PAPERS`, because it is not an examination anybody sits and putting it
    in that tuple would advertise a fourth paper that does not exist.
    """
    if kind == "unit":
        unit = content.unit_by_key(key)
        return exam.draw_from(unit.quizzable, length, seed) if unit else []
    if kind == "paper":
        paper = exam.by_key(key)
        return exam.build(paper, seed, length=length) if paper else []
    every = exam.Paper(
        key=WHOLE_COURSE, title="Whole course",
        units=tuple(unit.key for unit in content.UNITS),
        questions=length, minutes=0, summary="", reference="Edwards ch. 1–8",
    )
    return exam.build(every, seed, length=length)


def title_for(kind: str, key: str) -> str:
    """What the printed page calls itself."""
    if kind == "unit":
        unit = content.unit_by_key(key)
        return f"{unit.title} — worksheet" if unit else "Worksheet"
    if kind == "paper":
        paper = exam.by_key(key)
        return f"{paper.title} — practice paper" if paper else "Worksheet"
    return "Ordinary differential equations — worksheet"


# ---------------------------------------------------------------------------
# The slow half, off the interface thread
# ---------------------------------------------------------------------------


class _Signals(QObject):
    #: token, and either the finished HTML pair or the exception that stopped it
    done = Signal(int, object)
    #: token, questions worked so far, questions in all
    progress = Signal(int, int, int)


class _KeyJob(QRunnable):
    """Narrates every question of a worksheet and builds both documents.

    On a worker because the narrator reaches sympy and a subprocess: a single
    second-order forced equation can take a few seconds, and sixteen of them
    would freeze the window for the better part of a minute. Progress is
    reported per question rather than at the end, so the wait is legible.
    """

    def __init__(self, token: int, title: str, subtitle: str, items,
                 seed: int, minutes: int, signals: _Signals) -> None:
        super().__init__()
        self.token = token
        self.title = title
        self.subtitle = subtitle
        self.items = items
        self.seed = seed
        self.minutes = minutes
        self.signals = signals
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            workings = []
            for done, (lesson, _template, question) in enumerate(self.items):
                workings.append(printable.work_out(question, lesson.narrator))
                self._say(done + 1, len(self.items))
            result = (
                printable.worksheet(self.title, self.items,
                                    subtitle=self.subtitle, seed=self.seed,
                                    minutes=self.minutes),
                printable.solution_key(self.title, self.items, workings,
                                       subtitle=self.subtitle, seed=self.seed),
            )
        except Exception as exc:                  # surfaced, never swallowed
            result = exc
        self._emit(result)

    def _say(self, done: int, total: int) -> None:
        try:
            self.signals.progress.emit(self.token, done, total)
        except RuntimeError:
            pass                                  # the screen went away

    def _emit(self, result) -> None:
        try:
            self.signals.done.emit(self.token, result)
        except RuntimeError:
            pass


class _SheetJob(QRunnable):
    """Builds the formula sheet. Sixty-five typeset formulas is a few seconds."""

    def __init__(self, token: int, units, include_body: bool, title: str,
                 subtitle: str, signals: _Signals) -> None:
        super().__init__()
        self.token = token
        self.units = units
        self.include_body = include_body
        self.title = title
        self.subtitle = subtitle
        self.signals = signals
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            result = printable.formula_sheet(
                self.units, title=self.title, subtitle=self.subtitle,
                include_body=self.include_body,
            )
        except Exception as exc:
            result = exc
        try:
            self.signals.done.emit(self.token, result)
        except RuntimeError:
            pass


# ---------------------------------------------------------------------------
# The screen
# ---------------------------------------------------------------------------


class PrintScreen(QWidget):
    """Draw a worksheet, look at it, and save it with its key."""

    def __init__(self, state, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette

        #: The draw being previewed.
        self._items: list = []
        #: Rising token: a reply carrying an old one is a job whose answer is
        #: no longer wanted, which is how a second press while the first is
        #: still working cannot write the first one's file.
        self._token = 0
        self._pool = QThreadPool.globalInstance()
        self._signals = _Signals()
        self._signals.done.connect(self._finished)
        self._signals.progress.connect(self._worked)
        #: Where the two documents are going, decided before the job starts.
        self._destination = None
        #: What was saved last, so it can be opened.
        self._saved: list = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_body(), 1)
        self._redraw()

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(280)

        add_heading(layout, "Worksheet")
        blurb = QLabel(
            "Questions to work *on paper*, with the solutions in a separate "
            "file. Everything else here is typed into a box; the exam is not."
        )
        blurb.setProperty("role", "muted")
        blurb.setWordWrap(True)
        layout.addWidget(blurb)

        self.source_picker = QComboBox()
        for kind, key, label in sources():
            self.source_picker.addItem(label, (kind, key))
        self.source_picker.currentIndexChanged.connect(self._redraw)
        layout.addWidget(self.source_picker)

        row = QHBoxLayout()
        row.setSpacing(8)
        count = QLabel("Questions")
        count.setProperty("role", "muted")
        row.addWidget(count, 1)
        self.length = QSpinBox()
        self.length.setRange(2, 30)
        self.length.setValue(DEFAULT_LENGTH)
        self.length.valueChanged.connect(self._redraw)
        row.addWidget(self.length)
        layout.addLayout(row)

        # The seed is shown rather than hidden, and it is the only thing that
        # makes a printed sheet findable again: the worksheet and its key are
        # the same draw, and the number in the footer says which.
        seeds = QHBoxLayout()
        seeds.setSpacing(8)
        label = QLabel("Paper")
        label.setProperty("role", "muted")
        seeds.addWidget(label, 1)
        self.seed = QSpinBox()
        self.seed.setRange(1, 99_999)
        self.seed.setValue(1)
        self.seed.setToolTip(
            "Which draw this is. The same number gives the same questions, "
            "and it is printed on both pages."
        )
        self.seed.valueChanged.connect(self._redraw)
        seeds.addWidget(self.seed)
        layout.addLayout(seeds)

        another = QPushButton("Different questions")
        another.setToolTip("Move on to the next paper")
        another.setCursor(Qt.PointingHandCursor)
        another.clicked.connect(
            lambda: self.seed.setValue(self.seed.value() % 99_999 + 1)
        )
        layout.addWidget(another)

        self.save_button = QPushButton("Save worksheet and key…")
        self.save_button.setToolTip(
            "Write two files: the questions, and the narrated solutions"
        )
        self.save_button.setProperty("role", "primary")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.clicked.connect(self._save_worksheet)
        layout.addWidget(self.save_button)

        add_heading(layout, "Formula sheet", space_above=12)
        crib = QLabel(
            "Every formula box in the lessons, on one page — collected from "
            "the course rather than written beside it."
        )
        crib.setProperty("role", "muted")
        crib.setWordWrap(True)
        layout.addWidget(crib)

        self.sheet_picker = QComboBox()
        self.sheet_picker.addItem("Whole course", "")
        for unit in content.UNITS:
            self.sheet_picker.addItem(unit.title, unit.key)
        layout.addWidget(self.sheet_picker)

        self.with_prose = QCheckBox("Include the sentence with each formula")
        self.with_prose.setToolTip(
            "Helpful the first time through, and the opposite of what a crib "
            "sheet is for"
        )
        layout.addWidget(self.with_prose)

        self.sheet_button = QPushButton("Save formula sheet…")
        self.sheet_button.setCursor(Qt.PointingHandCursor)
        self.sheet_button.clicked.connect(self._save_sheet)
        layout.addWidget(self.sheet_button)

        self.status = QLabel("")
        self.status.setProperty("role", "muted")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setFixedHeight(8)
        self.bar.setVisible(False)
        layout.addWidget(self.bar)

        self.open_button = QPushButton("Open what was saved")
        self.open_button.setToolTip(
            "Open the pages in your browser, which is what prints them"
        )
        self.open_button.setCursor(Qt.PointingHandCursor)
        self.open_button.setVisible(False)
        self.open_button.clicked.connect(self._open_saved)
        layout.addWidget(self.open_button)

        layout.addStretch(1)

        note = QLabel(
            "The pages are self-contained HTML with the mathematics typeset "
            "inside them. Open one and print it from the browser."
        )
        note.setProperty("role", "muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        return panel

    def _build_body(self) -> QWidget:
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._page = QWidget()
        self._layout = QVBoxLayout(self._page)
        self._layout.setContentsMargins(4, 0, 12, 12)
        self._layout.setSpacing(10)
        self._scroll.setWidget(self._page)
        return self._scroll

    # -- the preview -----------------------------------------------------

    def chosen(self) -> tuple[str, str]:
        data = self.source_picker.currentData()
        return data if isinstance(data, tuple) else ("unit", "")

    def _redraw(self) -> None:
        """Draw the questions again and show them. No mathematics happens here
        -- `generate.draw` is a lookup into an enumerated set."""
        kind, key = self.chosen()
        self._items = draw(kind, key, self.length.value(), self.seed.value())
        self._show_preview()

    def _show_preview(self) -> None:
        self._clear()
        frame, inner = self._panel(self.palette_obj.accent)
        heading = QLabel(title_for(*self.chosen()))
        heading.setProperty("role", "title")
        inner.addWidget(heading)
        blurb = QLabel(
            f"{len(self._items)} questions · paper {self.seed.value()}. This "
            "is what the printed page will say, and deliberately no more: the "
            "lesson each question came from is on the key, not on the sheet, "
            "because working out which method it wants is the question."
        )
        blurb.setProperty("role", "muted")
        blurb.setWordWrap(True)
        inner.addWidget(blurb)
        self._layout.addWidget(frame)

        for number, (_lesson, _template, question) in enumerate(self._items,
                                                                start=1):
            self._layout.addWidget(self._question_card(number, question))
        self._layout.addStretch(1)
        self._scroll.verticalScrollBar().setValue(0)

    def _question_card(self, number: int, question) -> QWidget:
        frame, inner = self._panel()
        head = QLabel(f"Question {number}")
        head.setProperty("role", "heading")
        inner.addWidget(head)

        # The same five-way split `printable._question_body` makes, and it has
        # to stay the same one: this is a preview, and a preview that showed
        # something the page will not is worse than no preview. Only a `Solve`
        # has its prompt replaced, because only a `Solve` prompt names the
        # method; and a `Model`'s equation is the answer, so it is never shown.
        choosing = question.kind == "choice"
        asking = question.kind in ("choice", "numeric", "model", "expression")
        prompt = QLabel(
            question.prompt if asking
            else "Solve it." if not question.conditions
            else "Solve it, and satisfy the condition."
        )
        prompt.setWordWrap(True)
        inner.addWidget(prompt)

        # A generated question carries source text and a hand-written one
        # carries LaTeX, exactly as on the quiz screen: typesetting a `\,` as
        # literal characters is as wrong as printing a mangled image.
        if asking:
            if question.latex:
                inner.addWidget(MathLabel(self.palette_obj, question.latex,
                                          point_size=15))
        else:
            shown = question.equation + (
                f",   {question.conditions}" if question.conditions else ""
            )
            equation = QLabel(shown)
            equation.setStyleSheet(theme.scaled(
                "font-family: Cascadia Mono, Consolas, monospace; "
                "font-size: 15px;"
            ))
            equation.setWordWrap(True)
            inner.addWidget(equation)

        if choosing:
            options = QLabel("\n".join(
                f"  {letter}.  {text}" for letter, text
                in zip("ABCDEFGH", question.options)
            ))
            options.setProperty("role", "muted")
            options.setWordWrap(True)
            inner.addWidget(options)
        return frame

    def _panel(self, accent: str = "") -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setProperty("role", "panel")
        if accent:
            # Object name, not a bare `QFrame`: QLabel is a QFrame, so an
            # unscoped rule borders every label inside the card as well.
            frame.setObjectName("accentPanel")
            frame.setStyleSheet(
                f"QFrame#accentPanel {{ border-left: 3px solid {accent}; }}"
            )
        inner = QVBoxLayout(frame)
        inner.setContentsMargins(16, 13, 16, 14)
        inner.setSpacing(8)
        return frame, inner

    def _clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    # -- saving ----------------------------------------------------------

    def key_path(self, worksheet):
        """Where the key goes, given where the worksheet went.

        Beside it and named after it, rather than asked for separately. Two
        save dialogs for one action would be two chances to put the key
        somewhere the worksheet is not, and the pair is only useful together.
        """
        from pathlib import Path

        worksheet = Path(worksheet)
        return worksheet.with_name(f"{worksheet.stem}-key{worksheet.suffix}")

    def _save_worksheet(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        if not self._items:
            self._say("there is nothing drawn to save", bad=True)
            return
        kind, key = self.chosen()
        suggested = f"odesuite-{key}-{self.seed.value()}.html"
        chosen, _ = QFileDialog.getSaveFileName(
            self, "Save worksheet", suggested, "Web pages (*.html)"
        )
        if not chosen:
            return

        paper = exam.by_key(key) if kind == "paper" else None
        self._destination = chosen
        self._token += 1
        self._busy(f"working out {len(self._items)} solutions for the key…",
                   len(self._items))
        self._pool.start(_KeyJob(
            self._token, title_for(kind, key), self._subtitle(kind, key),
            list(self._items), self.seed.value(),
            paper.minutes if paper is not None else 0, self._signals,
        ))

    def _subtitle(self, kind: str, key: str) -> str:
        if kind == "unit":
            unit = content.unit_by_key(key)
            return unit.reference if unit else ""
        if kind == "paper":
            paper = exam.by_key(key)
            return f"{paper.summary}" if paper else ""
        return "Drawn from every unit, in the proportions the course teaches."

    def _save_sheet(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        key = self.sheet_picker.currentData() or ""
        unit = content.unit_by_key(key) if key else None
        units = (unit,) if unit is not None else None
        suggested = f"odesuite-formulas-{key or 'course'}.html"
        chosen, _ = QFileDialog.getSaveFileName(
            self, "Save formula sheet", suggested, "Web pages (*.html)"
        )
        if not chosen:
            return
        self._destination = chosen
        self._token += 1
        self._busy("typesetting the formulas…", 0)
        self._pool.start(_SheetJob(
            self._token, units, self.with_prose.isChecked(),
            f"{unit.title} — formula sheet" if unit is not None
            else "Formula sheet",
            unit.reference if unit is not None
            else "Every formula in the course, in the order it is taught.",
            self._signals,
        ))

    def _busy(self, message: str, total: int) -> None:
        self.save_button.setEnabled(False)
        self.sheet_button.setEnabled(False)
        self.open_button.setVisible(False)
        self.bar.setVisible(True)
        self.bar.setRange(0, total)          # 0, 0 is Qt's indeterminate bar
        self.bar.setValue(0)
        self._say(message)

    def _worked(self, token: int, done: int, total: int) -> None:
        if token != self._token:
            return
        self.bar.setRange(0, total)
        self.bar.setValue(done)
        self._say(f"working out the key — {done} of {total}")

    def _finished(self, token: int, result) -> None:
        """Write whatever the job produced, or say why there is nothing.

        A stale token is a job whose answer is no longer wanted: the user has
        pressed again, or chosen something else, and the destination now
        belongs to the later job. Writing it would put one job's pages at
        another's path.
        """
        if token != self._token:
            return
        self.bar.setVisible(False)
        self.save_button.setEnabled(True)
        self.sheet_button.setEnabled(True)
        if isinstance(result, Exception):
            self._say(f"could not build it: {result}", bad=True)
            return
        try:
            if isinstance(result, tuple):
                sheet, key = result
                first = printable.write(sheet, self._destination)
                second = printable.write(key, self.key_path(self._destination))
                self._saved = [first, second]
                self._say(f"saved {first.name} and {second.name} — "
                          f"open the first to print it, and keep the second "
                          f"shut until you have finished.")
            else:
                first = printable.write(result, self._destination)
                self._saved = [first]
                self._say(f"saved {first.name}")
        except OSError as exc:
            self._say(f"could not write it: {exc}", bad=True)
            return
        self.open_button.setVisible(True)

    def _open_saved(self) -> None:
        """Hand the pages to the browser, which is what prints them.

        Only the worksheet, never the key. They are saved together and the key
        is the half that has to stay shut; opening both would undo the reason
        they are two files at all.
        """
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        if not self._saved:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self._saved[0])))

    def _say(self, message: str, *, bad: bool = False) -> None:
        colour = (self.palette_obj.danger if bad
                  else self.palette_obj.text_muted)
        self.status.setStyleSheet(f"color: {colour};")
        self.status.setText(message)

    # -- the window's hooks ----------------------------------------------

    def refresh(self) -> None:
        """Nothing to reload: a drawn worksheet should survive a visit
        elsewhere, and redrawing it would change the paper under someone who
        had already started writing on it."""

    def refresh_problems(self) -> None:
        self.refresh()

    def set_palette_colours(self, palette: Palette) -> None:
        self.palette_obj = palette
