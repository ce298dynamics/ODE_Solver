"""Lessons: read the technique, watch it worked, then try it.

The other Hub screens are tools — you bring an equation and they work on it.
This one assumes you do not yet know which equation to bring. A course on the
left, and on the right one lesson at a time in four parts: **Learn** (what the
technique is, with a figure to move where the topic has one), **Examples** (it
worked through, by the narrator), **Practice** (your turn), and **Drill**
(more of it, with fresh numbers).

The practice is the part worth being careful about, and it works the way the
rest of this application works: a typed solution is **substituted into the
equation and simplified**, through the same `symbolic.check_answer` the Solve
Step by Step screen uses. There is no stored answer to compare against, so any
correct form passes and nothing is marked wrong for being spelled differently.
Where sympy cannot decide, the verdict says so rather than guessing.

Multiple-choice questions do have a stored answer, because *which technique
solves this* is not something a substitution check can grade — and each one
carries a reason for every option, shown for whichever was picked. The reason a
wrong option was tempting is usually the thing that was actually misunderstood.

Hints come one rung at a time rather than all at once: a nudge, then the first
move, then the next, and "Show me" — the real narrator — at the end of the
ladder. A hint that gives the answer away on the first press is not a hint.

**A drill is driven from the keyboard alone.** Enter marks what is in the box;
Enter again draws the next question and leaves the caret where the answer goes.
Nothing else here is done forty times in a row, and nothing else here needs it.

Progress is recorded on disk (see `progress`), so the ticks survive closing the
application. Everything expensive — a worked example, a model answer — happens
on the thread pool and only when asked for, so switching lesson or segment
stays instant.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import lessons as content
from .. import progress, richtext, theme
from ..lessons import generate
from ..theme import Palette
from ..widgets.controls import add_heading, control_panel
from ..widgets.lessonfigure import build_figure
from ..widgets.mathlabel import MathLabel
from ..widgets.stepspanel import StepsPanel

__all__ = ["CARRIES_EQUATION", "TOOL_NAMES", "LessonsScreen", "SEGMENTS"]

#: The parts of a lesson, in the order they are meant to be met. `Drill` is
#: offered only where the lesson has templates -- see `_build_drill`.
SEGMENTS = ("Learn", "Examples", "Practice", "Drill")

#: What a `Lesson.tool` is called on screen. A copy of four of the labels in
#: `app.SECTIONS` rather than an import of them: this screen is constructed by
#: that module, and reaching back into it for four strings would make the two
#: mutually dependent for no gain. `tests/test_lessons.py` checks the copies
#: against the originals, which is the part that actually matters.
TOOL_NAMES = {
    "steps": "Solve Step by Step",
    "laplace": "Laplace Transforms",
    "byhand": "Methods by Hand",
    "worked": "Worked Problems",
    "portrait": "Phase Portrait",
}

#: Which of those can be opened *on* an equation. The other two are driven by
#: the catalogue -- they offer a list of problems rather than a box to type in
#: -- so there is nothing for a lesson's example to be loaded into, and
#: promising otherwise is the bug this set exists to avoid repeating.
CARRIES_EQUATION = frozenset({"steps", "laplace"})


class _Signals(QObject):
    done = Signal(int, object)          # token, Derivation | Exception


class _WorkingJob(QRunnable):
    """Produces the narrated solution for an equation, off the interface thread."""

    def __init__(self, token: int, equation: str, conditions: str,
                 narrator: str, signals: _Signals) -> None:
        super().__init__()
        self.token = token
        self.equation = equation
        self.conditions = conditions
        self.narrator = narrator
        self.signals = signals
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            result = _work_out(self.equation, self.conditions, self.narrator)
        except Exception as exc:                  # surfaced, never swallowed
            result = exc
        try:
            self.signals.done.emit(self.token, result)
        except RuntimeError:
            pass                                  # the screen went away


def _work_out(equation: str, conditions: str, narrator: str):
    """The worked solution, through the same subprocess the Hub tools use."""
    from ..laplace import EXTRA_FUNCTIONS
    from ..symbolic import (
        parse_equation,
        solve_by_laplace,
        solve_symbolically,
        spec_for,
    )

    parsed = parse_equation(spec_for(equation, conditions),
                            extra_functions=EXTRA_FUNCTIONS)
    if narrator == "laplace":
        return solve_by_laplace(parsed).derivation
    if narrator == "series":
        from ..series import derive as series_derive

        return series_derive(parsed.equation, parsed.function, ics=parsed.ics)
    return solve_symbolically(parsed, steps=True).derivation


class _DrillCard(QFrame):
    """A drill's card, which answers to Enter however it is focused.

    A `QLineEdit` consumes Return and reports it as `returnPressed`, so a
    drill with a box to type in needs nothing from here. A multiple-choice
    drill has no box: the focus is on a radio button, which ignores Return and
    lets it travel up to this frame.

    A `QShortcut` scoped to the card was the first attempt and is the wrong
    tool. Shortcuts are matched against the *window*, so they do nothing until
    the window is active -- which makes the behaviour untestable and, worse,
    makes it depend on something the reader cannot see.
    """

    #: Enter was pressed somewhere in this card and nothing else wanted it.
    returned = Signal()

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.returned.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class LessonsScreen(QWidget):
    """One lesson at a time: what it is, worked examples, and practice."""

    #: Asks the window to open the tool a lesson belongs to, carrying the
    #: lesson's own example: ``(screen key, equation, conditions)``. The
    #: equation travels with the request rather than being fetched at the
    #: other end, because the window knows which screen to show and only this
    #: screen knows which lesson is open.
    open_tool = Signal(str, str, str)

    def __init__(self, state, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette
        self._token = 0
        self._answered = progress.load()
        self._segment = SEGMENTS[0]
        #: Template key -> which draw is on screen. In memory rather than on
        #: disk: the streak is the thing worth keeping, not the question.
        self._drill_seed: dict[str, int] = {}
        #: Which difficulty each drill is drawing from, where it
        #: offers a choice. Kept for the session rather than stored:
        #: it is a way of working through one sitting, not a record
        #: of what somebody can do.
        self._drill_tier: dict[str, str] = {}
        #: Question key -> the label that shows its verdict.
        self._verdicts: dict[str, QLabel] = {}
        #: Template key -> the box its answer is typed into, for the drill's
        #: keyboard loop. Rebuilt with the page, because the widgets are.
        self._drill_inputs: dict[str, QLineEdit] = {}
        #: Which drill asked for the next draw, so the caret can go back to it
        #: once the page has been rebuilt. Cleared as soon as it is honoured:
        #: it describes one rebuild, not a preference.
        self._focus_drill: str = ""
        #: Token -> the panel and button waiting on it. Keyed rather than held
        #: singly, so a superseded request can still re-enable its own button
        #: instead of leaving it disabled for good.
        self._pending: dict[int, tuple[StepsPanel, QPushButton]] = {}

        self._signals = _Signals()
        self._signals.done.connect(self._on_worked)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_body(), 1)

        self.select(content.LESSONS[0].key if content.LESSONS else "")

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(276)

        add_heading(layout, "Course")
        note = QLabel(
            "Each lesson has notes, worked examples and questions. The count "
            "is how many you have answered correctly."
        )
        note.setProperty("role", "muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        # A tree rather than a list: the units are what make thirty-odd
        # lessons navigable, and a flat list of them is a wall.
        self.listing = QTreeWidget()
        self.listing.setAccessibleName("lessons")
        self.listing.setHeaderHidden(True)
        self.listing.setIndentation(12)
        self.listing.setMinimumHeight(260)
        self.listing.setRootIsDecorated(True)
        for unit in content.UNITS:
            parent = QTreeWidgetItem([unit.title])
            parent.setData(0, Qt.UserRole, "")     # a unit is not a lesson
            font = parent.font(0)
            font.setBold(True)
            parent.setFont(0, font)
            for lesson in unit.lessons:
                child = QTreeWidgetItem([self._label_for(lesson)])
                child.setData(0, Qt.UserRole, lesson.key)
                parent.addChild(child)
            self.listing.addTopLevelItem(parent)
            parent.setExpanded(True)
        layout.addWidget(self.listing)

        self.tool_button = QPushButton("Open the tool for this topic")
        self.tool_button.setProperty("role", "primary")
        self.tool_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.tool_button)

        layout.addStretch(1)

        # Export and import sit beside Reset because they are the same
        # subject: what happens to what you have done. A reinstall, a new
        # machine or a wiped profile used to lose all of it, and the file was
        # already the right shape to hand over -- there was simply no way to
        # ask for a copy.
        moving = QHBoxLayout()
        moving.setSpacing(8)
        self.export_button = QPushButton("Export…")
        self.export_button.setCursor(Qt.PointingHandCursor)
        self.export_button.setToolTip(
            "Save everything you have answered to a file you can keep"
        )
        moving.addWidget(self.export_button)

        self.import_button = QPushButton("Import…")
        self.import_button.setCursor(Qt.PointingHandCursor)
        self.import_button.setToolTip(
            "Merge a saved file back in. Nothing already recorded is lost."
        )
        moving.addWidget(self.import_button)
        layout.addLayout(moving)

        self.transfer_note = QLabel("")
        self.transfer_note.setProperty("role", "muted")
        self.transfer_note.setWordWrap(True)
        self.transfer_note.setStyleSheet(theme.scaled("font-size: 11px;"))
        layout.addWidget(self.transfer_note)

        self.reset_button = QPushButton("Reset progress")
        self.reset_button.setToolTip(
            "Forget every answer recorded, for every lesson. Asks first."
        )
        self.reset_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.reset_button)

        where = QLabel(f"Answers are remembered in\n{progress.path()}")
        where.setProperty("role", "muted")
        where.setWordWrap(True)
        where.setStyleSheet(theme.scaled("font-size: 10px;"))
        layout.addWidget(where)

        self.listing.currentItemChanged.connect(lambda *_: self._show())
        self.tool_button.clicked.connect(self._open_tool)
        self.reset_button.clicked.connect(self._reset)
        self.export_button.clicked.connect(self._export)
        self.import_button.clicked.connect(self._import)
        return panel

    def _export(self) -> None:
        """Write everything recorded to a file the user chooses."""
        from PySide6.QtWidgets import QFileDialog

        chosen, _ = QFileDialog.getSaveFileName(
            self, "Export progress", "odesuite-progress.json",
            "JSON files (*.json)",
        )
        if not chosen:
            return
        try:
            written = progress.export_to(chosen)
        except OSError as exc:
            self._say_transfer(f"could not write it: {exc}", bad=True)
            return
        answered = sum(len(answers) for answers in progress.load().values())
        self._say_transfer(f"exported {answered} answers to {written.name}")

    def _import(self) -> None:
        """Merge a saved file back in, keeping whichever record is better.

        Merged rather than replacing, and the distinction matters: importing a
        file from a machine where less had been done would otherwise delete
        work, which is the exact failure this feature exists to prevent.
        """
        from PySide6.QtWidgets import QFileDialog

        chosen, _ = QFileDialog.getOpenFileName(
            self, "Import progress", "", "JSON files (*.json)",
        )
        if not chosen:
            return
        before = sum(len(answers) for answers in progress.load().values())
        everything = progress.import_from(chosen)
        after = sum(len(answers) for answers in everything.values())
        if after == before == 0:
            self._say_transfer("nothing usable in that file", bad=True)
        else:
            self._say_transfer(
                f"merged — {after} answers now recorded"
                + (f", {after - before} new" if after > before else
                   ", none of yours replaced")
            )
        self._answered = everything
        self._show()

    def _say_transfer(self, message: str, *, bad: bool = False) -> None:
        colour = (self.palette_obj.danger if bad
                  else self.palette_obj.text_muted)
        self.transfer_note.setStyleSheet(theme.scaled(f"font-size: 11px; color: {colour};"))
        self.transfer_note.setText(message)

    def _build_body(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        outer = QVBoxLayout(frame)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # The heading and the segment bar stay put while the part below them
        # scrolls: which lesson you are in, and which part of it, should not be
        # something you have to scroll back up to find out.
        head = QWidget()
        head_layout = QVBoxLayout(head)
        head_layout.setContentsMargins(24, 18, 24, 10)
        head_layout.setSpacing(6)

        self.title_label = QLabel("")
        self.title_label.setProperty("role", "title")
        self.title_label.setWordWrap(True)
        head_layout.addWidget(self.title_label)

        self.summary_label = QLabel("")
        self.summary_label.setProperty("role", "subtitle")
        self.summary_label.setWordWrap(True)
        head_layout.addWidget(self.summary_label)

        self.reference_label = QLabel("")
        self.reference_label.setProperty("role", "muted")
        self.reference_label.setWordWrap(True)
        head_layout.addWidget(self.reference_label)

        bar = QHBoxLayout()
        bar.setSpacing(6)
        bar.setContentsMargins(0, 8, 0, 0)
        self.segment_buttons: dict[str, QPushButton] = {}
        self._segment_group = QButtonGroup(head)
        self._segment_group.setExclusive(True)
        for index, name in enumerate(SEGMENTS):
            button = QPushButton(name)
            button.setProperty("role", "section")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setChecked(index == 0)
            self._segment_group.addButton(button, index)
            self.segment_buttons[name] = button
            bar.addWidget(button)
            button.clicked.connect(
                lambda _=False, n=name: self._choose_segment(n)
            )
        bar.addStretch(1)
        head_layout.addLayout(bar)
        outer.addWidget(head)

        scroll = QScrollArea()
        scroll.setAccessibleName("lesson")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll, 1)
        self._scroll = scroll

        # A reading column, not the full width of the window. Notes set across
        # 1400 pixels are genuinely hard to read -- the eye loses the line on
        # the way back -- and this is the one screen here whose main job is
        # being read rather than being operated.
        holder = QWidget()
        scroll.setWidget(holder)
        across = QHBoxLayout(holder)
        across.setContentsMargins(0, 0, 0, 0)

        self._page = QWidget()
        self._page.setMaximumWidth(900)
        # Stretch as well as a cap: without it the column takes its size hint
        # and the answer boxes collapse to nothing.
        across.addWidget(self._page, 1)
        across.addStretch(0)

        self._layout = QVBoxLayout(self._page)
        self._layout.setContentsMargins(24, 14, 24, 24)
        self._layout.setSpacing(14)
        return frame

    # -- navigation ------------------------------------------------------

    def _label_for(self, lesson) -> str:
        done, total = progress.counts(lesson.key, len(lesson.questions),
                                      self._answered)
        return f"{lesson.title}   ({done}/{total})"

    def _lesson_items(self):
        """Every tree item that stands for a lesson, with its lesson."""
        for index in range(self.listing.topLevelItemCount()):
            unit_item = self.listing.topLevelItem(index)
            for child in range(unit_item.childCount()):
                item = unit_item.child(child)
                lesson = content.by_key(item.data(0, Qt.UserRole))
                if lesson is not None:
                    yield item, lesson

    def _refresh_labels(self) -> None:
        for item, lesson in self._lesson_items():
            item.setText(0, self._label_for(lesson))

    def current_lesson(self):
        item = self.listing.currentItem()
        if item is None:
            return None
        return content.by_key(item.data(0, Qt.UserRole) or "")

    def select(self, key: str) -> None:
        """Open a lesson by key. Used by the Course Map to jump straight in."""
        for item, lesson in self._lesson_items():
            if lesson.key == key:
                self.listing.setCurrentItem(item)
                return

    def _choose_segment(self, name: str) -> None:
        self._segment = name
        button = self.segment_buttons.get(name)
        if button is not None:
            button.setChecked(True)
        self._show()

    # -- the page --------------------------------------------------------

    def _show(self) -> None:
        lesson = self.current_lesson()
        self._clear()
        self._verdicts = {}
        self._drill_inputs = {}
        self._abandon()

        if lesson is None:
            # A unit heading is selected rather than a lesson. Say so instead
            # of leaving the reading column blank.
            self._describe_tool(None)
            self.title_label.setText("")
            self.summary_label.setText("Choose a lesson from the unit on the "
                                       "left.")
            self.reference_label.setText("")
            for button in self.segment_buttons.values():
                button.setEnabled(False)
            return

        for name, button in self.segment_buttons.items():
            button.setEnabled(True)
            # A lesson with no templates has no Drill, and the button goes
            # rather than opening an empty page. No lesson is in that position
            # any more -- `tests/test_templates.py` asserts every one has a
            # drill -- but the guard stays, because it is what keeps a lesson
            # added without one from opening a blank page.
            button.setVisible(name != "Drill" or bool(lesson.templates))
        if self._segment == "Drill" and not lesson.templates:
            self._segment = "Practice"
            self.segment_buttons["Practice"].setChecked(True)

        self._describe_tool(lesson)
        self.title_label.setText(lesson.title)
        self.summary_label.setText(lesson.summary)
        unit = content.unit_of(lesson)
        trail = " · ".join(
            part for part in (unit.title if unit else "", lesson.reference)
            if part
        )
        self.reference_label.setText(trail)

        if self._segment == "Learn":
            self._build_learn(lesson)
        elif self._segment == "Examples":
            self._build_examples(lesson)
        elif self._segment == "Drill":
            self._build_drill(lesson)
        else:
            self._build_practice(lesson)
        self._layout.addStretch(1)
        self._scroll.verticalScrollBar().setValue(0)
        self._restore_drill_focus()

    def _restore_drill_focus(self) -> None:
        """Put the caret back in the drill that asked for a new question.

        Advancing rebuilds the whole segment, which destroys the box that was
        being typed in. Without this the keyboard loop would run exactly one
        question before handing the mouse back, which is the thing it exists
        to stop.
        """
        wanted, self._focus_drill = self._focus_drill, ""
        box = self._drill_inputs.get(wanted)
        if box is not None:
            box.setFocus(Qt.OtherFocusReason)
            # The card is somewhere down a scrolling column, and a caret
            # nobody can see is not where the caret should be.
            self._scroll.ensureWidgetVisible(box, 0, 60)

    def _build_learn(self, lesson) -> None:
        if lesson.objectives:
            self._layout.addWidget(self._objectives_card(lesson))
        # Motivation before anything else that is not a promise about the
        # lesson: a reader who does not yet know why the topic exists cannot
        # be told what the technique is. Then the figure, to play with while
        # reading, then the argument, then the facts.
        if lesson.motivation:
            self._layout.addWidget(self._motivation_card(lesson))
        if lesson.figure:
            figure = build_figure(lesson.figure, self.palette_obj)
            if figure is not None:
                self._layout.addWidget(figure)
        if lesson.derivation:
            self._layout.addWidget(self._derivation_card(lesson))
        for note in lesson.notes:
            self._layout.addWidget(self._note_card(note))

    def _prose(self, layout, text: str) -> None:
        """Add `text` as one wrapped label per paragraph.

        Blank lines separate paragraphs and are honoured, because the whole
        point of writing more is that it stops being a wall. One label each
        rather than one with newlines in it: the layout's spacing then does the
        work, and each paragraph can carry its own accessible name.
        """
        for paragraph in (part.strip() for part in text.split("\n\n")):
            if not paragraph:
                continue
            label = QLabel(richtext.emphasise(paragraph))
            label.setTextFormat(Qt.RichText)
            label.setWordWrap(True)
            label.setAccessibleName("paragraph")
            # The markers are ours, not the reader's: the description a screen
            # reader speaks gets the words without them.
            label.setAccessibleDescription(richtext.plain(paragraph))
            layout.addWidget(label)

    def _motivation_card(self, lesson) -> QWidget:
        frame, layout = self._panel()
        frame.setAccessibleName(f"Why this topic exists: {lesson.title}")

        heading = QLabel("Why this comes up")
        heading.setProperty("role", "heading")
        layout.addWidget(heading)
        self._prose(layout, lesson.motivation)
        return frame

    def _derivation_card(self, lesson) -> QWidget:
        """The argument for why the method works.

        Its own card, and numbered, because it is a chain rather than a set of
        facts -- and separate from the Examples segment on purpose. The
        narrator there shows the steps for one equation; this is the general
        case, which no amount of worked examples supplies.
        """
        frame, layout = self._panel(self.palette_obj.accent)
        frame.setAccessibleName(f"Where this comes from: {lesson.title}")

        heading = QLabel("Where this comes from")
        heading.setProperty("role", "heading")
        layout.addWidget(heading)

        for number, passage in enumerate(lesson.derivation, start=1):
            row = QLabel(f"Step {number}")
            row.setProperty("role", "muted")
            row.setStyleSheet("font-weight: 600; letter-spacing: 1px;")
            if number > 1:
                layout.addSpacing(6)
            layout.addWidget(row)
            self._prose(layout, passage.prose)
            if passage.latex:
                layout.addWidget(MathLabel(self.palette_obj, passage.latex,
                                           point_size=15))
        return frame

    def _build_examples(self, lesson) -> None:
        heading = QLabel(
            "Worked by the same narrator that powers the tool for this topic, "
            "so what you see here is what that screen would show — generated "
            "and checked, not transcribed."
        )
        heading.setProperty("role", "muted")
        heading.setWordWrap(True)
        self._layout.addWidget(heading)
        for number, example in enumerate(lesson.examples, start=1):
            self._layout.addWidget(self._example_card(number, example))

    def _build_practice(self, lesson) -> None:
        for number, question in enumerate(lesson.questions, start=1):
            self._layout.addWidget(self._question_card(lesson, number, question))

    def _build_drill(self, lesson) -> None:
        # Which grading is described depends on what this lesson drills. A
        # multiple-choice drill is not graded by substitution, and saying it is
        # would tell the reader something false about the tick they get.
        kinds = {item.kind for item in lesson.templates}
        described = {
            "template": "an answer you type is substituted into its own "
                        "equation, so any correct form passes",
            "choice-template": "pick the right option",
            "numeric-template": "a number you type is marked to a tolerance",
            "model-template": "an equation you write is compared with the "
                              "one the situation gives, however you arrange "
                              "it",
            "expression-template": "one step of the method, marked by what "
                                   "it is rather than how it is spelled",
            "classify-template": "name the method, and say what decided it",
            "fault-template": "find what is wrong with an answer somebody "
                              "else arrived at",
        }
        parts = [described[kind] for kind in
                 ("template", "choice-template", "numeric-template",
                  "model-template", "expression-template",
                  "classify-template", "fault-template")
                 if kind in kinds]
        how = "; ".join(parts) if parts else "answers are marked"
        blurb = QLabel(
            f"Fresh numbers every time — {how}. "
            f"{progress.MASTERED_STREAK} right in a row and the drill is "
            "mastered; one wrong answer starts the count again."
        )
        blurb.setProperty("role", "muted")
        blurb.setWordWrap(True)
        self._layout.addWidget(blurb)
        for template in lesson.templates:
            self._layout.addWidget(self._drill_card(lesson, template))

    # -- cards -----------------------------------------------------------

    def _panel(self, accent: str = "",
               card: type[QFrame] = QFrame) -> tuple[QFrame, QVBoxLayout]:
        """A themed card and its layout. `card` picks the class it is built as.

        Only the drill cards want anything but a plain `QFrame` -- they take
        `_DrillCard`, which answers to Enter -- and they want everything else
        about a card unchanged, which is why this is a parameter rather than a
        second copy of the function.
        """
        frame = card()
        frame.setProperty("role", "panel")
        if accent:
            # Scoped by object name, and it has to be. A stylesheet set on a
            # widget applies to its descendants, and QLabel *is* a QFrame --
            # so a bare `QFrame` selector gave every label in the card its own
            # left border, drawn over the first character of the text and
            # standing beside every equation like a stray bracket.
            frame.setObjectName("accentPanel")
            frame.setStyleSheet(
                f"QFrame#accentPanel {{ border-left: 3px solid {accent}; }}"
            )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 13, 16, 14)
        layout.setSpacing(8)
        return frame, layout

    def _objectives_card(self, lesson) -> QWidget:
        frame, layout = self._panel(self.palette_obj.accent)

        heading = QLabel("What you should be able to do")
        heading.setProperty("role", "heading")
        layout.addWidget(heading)

        for objective in lesson.objectives:
            row = QLabel("·  " + richtext.emphasise(objective))
            row.setTextFormat(Qt.RichText)
            row.setWordWrap(True)
            layout.addWidget(row)

        if lesson.prerequisites:
            names = [
                found.title for found in
                (content.by_key(key) for key in lesson.prerequisites)
                if found is not None
            ]
            if names:
                before = QLabel("Worth having met first: " + ", ".join(names))
                before.setProperty("role", "muted")
                before.setWordWrap(True)
                layout.addWidget(before)
        return frame

    def _note_card(self, note) -> QWidget:
        palette = self.palette_obj
        # A pitfall should not read like an idea. The colour is the whole
        # difference: same card, same typography, a warning stripe down it.
        accent = {"pitfall": palette.warning, "formula": palette.accent_soft}
        frame, layout = self._panel(accent.get(note.kind, ""))

        label = {"pitfall": "Common mistake", "aside": "Aside"}.get(note.kind)
        if label:
            tag = QLabel(label.upper())
            tag.setProperty("role", "muted")
            accent = (palette.warning if note.kind == "pitfall"
                      else palette.text_muted)
            tag.setStyleSheet(theme.scaled(
                f"color: {accent}; font-size: 10px; letter-spacing: 1px;"
            ))
            layout.addWidget(tag)

        heading = QLabel(note.heading)
        heading.setProperty("role", "heading")
        heading.setWordWrap(True)
        layout.addWidget(heading)
        frame.setAccessibleName(f"{label or 'Note'}: {note.heading}")

        self._prose(layout, note.body)

        if note.latex:
            layout.addWidget(MathLabel(palette, note.latex, point_size=15))
        return frame

    def _example_card(self, number: int, example) -> QWidget:
        frame, layout = self._panel()

        heading = QLabel(f"Example {number}")
        heading.setProperty("role", "heading")
        layout.addWidget(heading)

        frame.setAccessibleName(f"Example {number}: {example.equation}")

        if example.why:
            why = QLabel(richtext.emphasise(example.why))
            why.setTextFormat(Qt.RichText)
            why.setProperty("role", "muted")
            why.setWordWrap(True)
            layout.addWidget(why)

        # What to watch for, before the working appears. The narrator supplies
        # the steps and cannot supply the reading of them -- which line is the
        # one that matters, and what the answer's shape is telling you.
        if example.commentary:
            self._prose(layout, example.commentary)

        shown = example.equation + (
            f",   {example.conditions}" if example.conditions else ""
        )
        equation = QLabel(shown)
        equation.setStyleSheet("font-family: Cascadia Mono, Consolas, monospace;")
        equation.setWordWrap(True)
        layout.addWidget(equation)

        row = QHBoxLayout()
        button = QPushButton("Work it through")
        button.setToolTip(
            "Run the narrator over this equation and show every step"
        )
        button.setProperty("role", "primary")
        button.setCursor(Qt.PointingHandCursor)
        row.addWidget(button)
        row.addStretch(1)
        layout.addLayout(row)

        steps = StepsPanel(self.palette_obj)
        steps.setMinimumHeight(260)
        steps.setVisible(False)
        layout.addWidget(steps)

        button.clicked.connect(
            lambda: self._work(example.equation, example.conditions,
                               example.narrator, steps, button)
        )
        return frame

    def _streak_of(self, lesson, template):
        """The recorded streak for one drill, and whether it is mastered."""
        answers = self._answered.get(progress.drill_key(lesson.key), {})
        answer = answers.get(template.key)
        return (answer.streak if answer else 0), bool(answer and answer.mastered)

    def _streak_text(self, streak: int, mastered: bool) -> str:
        run = min(streak, progress.MASTERED_STREAK)
        dots = "●" * run + "○" * (progress.MASTERED_STREAK - run)
        if mastered:
            return f"{dots}   mastered"
        if streak == 0:
            return f"{dots}   {progress.MASTERED_STREAK} in a row to master"
        left = progress.MASTERED_STREAK - streak
        return (f"{dots}   {streak} in a row, {left} more"
                if left > 0 else f"{dots}   mastered")

    def _keyboard_loop(self, frame, template, answer, graded, advance):
        """Enter checks; Enter again draws the next one.

        A drill is the one part of this screen somebody does forty times in a
        row, and it was the one part that still needed the mouse:
        `returnPressed` marked an answer, and *New question* was a button. So
        the same key does both, in the order they are wanted -- there is no
        point advancing before the verdict has been read, and no point
        re-marking an answer that has already been marked.

        `graded` says whether it actually marked anything, which is what keeps
        an empty box or an unpicked option from being spent as a turn: the key
        stays on this question until there is a verdict to move past.

        The key is taken once, by the card. A `QLineEdit` emits
        `returnPressed` *and* lets the event travel on, so wiring both would
        check and advance on a single press -- which is exactly what the first
        version of this did. Listening at the card also means Enter works
        wherever the focus happens to be inside it: the answer box, a radio
        button, or the Hint button beside them.
        """
        marked = {"done": False}

        def step() -> None:
            if marked["done"]:
                advance()
            else:
                marked["done"] = bool(graded())

        if answer is not None:
            # Where the caret goes when the next draw is built. Recorded per
            # template rather than globally: a Drill segment shows every
            # template the lesson has, and the one that advanced is the one
            # that should still have the focus afterwards.
            self._drill_inputs[template.key] = answer
        frame.returned.connect(step)
        return step

    def _tier_row(self, template, offered: tuple[str, ...]) -> QHBoxLayout:
        """The easier/typical/harder control, for a drill that has a spread.

        Shown only where the template really has one. A control offering
        three difficulties over a family that has one would teach a student to
        distrust the label, which is worse than not offering the choice.

        Switching keeps the seed rather than resetting it, so coming back to a
        tier does not re-ask the question it opened with.
        """
        row = QHBoxLayout()
        row.setSpacing(6)
        label = QLabel("Difficulty")
        label.setProperty("role", "muted")
        row.addWidget(label)

        current = self._tier_of(template, offered)
        for tier in offered:
            button = QPushButton(tier.capitalize())
            button.setCheckable(True)
            button.setChecked(tier == current)
            button.setCursor(Qt.PointingHandCursor)
            button.setToolTip(
                f"Draw only the {tier} questions of this drill"
            )
            button.clicked.connect(
                lambda _checked=False, key=template.key, choice=tier:
                self._choose_tier(key, choice)
            )
            row.addWidget(button)
        row.addStretch(1)
        return row

    def _tier_of(self, template, offered: tuple[str, ...]) -> str:
        """Which tier this drill is currently drawing from."""
        chosen = self._drill_tier.get(template.key)
        if chosen in offered:
            return chosen
        return "typical" if "typical" in offered else offered[0]

    def _choose_tier(self, key: str, tier: str) -> None:
        self._drill_tier[key] = tier
        self._focus_drill = key
        self._show()

    def _drill_card(self, lesson, template) -> QWidget:
        palette = self.palette_obj
        seed = self._drill_seed.setdefault(template.key, 0)
        offered = generate.tiers(template)
        tier = self._tier_of(template, offered) if len(offered) > 1 else ""
        question = generate.draw(template, seed, tier)
        streak, mastered = self._streak_of(lesson, template)

        frame, layout = self._panel(palette.success if mastered else "",
                                    card=_DrillCard)

        head = QHBoxLayout()
        heading = QLabel(template.title)
        heading.setProperty("role", "heading")
        heading.setWordWrap(True)
        head.addWidget(heading, 1)

        run = QLabel(self._streak_text(streak, mastered))
        run.setProperty("role", "muted")
        run.setStyleSheet(
            f"color: {palette.success if mastered else palette.text_muted};"
        )
        head.addWidget(run, 0, Qt.AlignRight | Qt.AlignTop)
        layout.addLayout(head)

        prompt = QLabel(
            f"{question.prompt}   ·   one of "
            f"{generate.combinations(template, tier)} versions"
        )
        prompt.setProperty("role", "muted")
        prompt.setWordWrap(True)
        layout.addWidget(prompt)
        self._question_figure(question, layout)

        if len(offered) > 1:
            layout.addLayout(self._tier_row(template, offered))

        # The other two kinds take their own paths. Neither has a narrator, so
        # neither offers "Show me": a button that cannot do anything is worse
        # than an absent one. A `Choice` has no hints either; a `Numeric` may.
        if question.kind == "choice":
            self._build_choice_drill(lesson, template, question, run, layout,
                                     frame)
            return frame
        if question.kind == "numeric":
            self._build_numeric_drill(lesson, template, question, run, layout,
                                      frame)
            return frame
        if question.kind == "model":
            self._build_model_drill(lesson, template, question, run, layout,
                                    frame)
            return frame
        if question.kind == "expression":
            self._build_expression_drill(lesson, template, question, run,
                                         layout, frame)
            return frame

        shown = question.equation + (
            f",   {question.conditions}" if question.conditions else ""
        )
        equation = QLabel(shown)
        equation.setStyleSheet("font-family: Cascadia Mono, Consolas, monospace;")
        equation.setWordWrap(True)
        layout.addWidget(equation)

        row = QHBoxLayout()
        row.setSpacing(8)
        answer = QLineEdit()
        answer.setAccessibleName("your answer")
        answer.setPlaceholderText("y = ...")
        answer.setClearButtonEnabled(True)
        row.addWidget(answer, 1)

        check = QPushButton("Check")
        check.setToolTip("Mark what you have entered")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)

        hint_button = QPushButton("Hint")
        hint_button.setToolTip(
            "Reveal the next hint. They come one at a time, and never "
            "the answer."
        )
        hint_button.setCursor(Qt.PointingHandCursor)
        hint_button.setEnabled(bool(question.hints))
        row.addWidget(hint_button)

        show = QPushButton("Show me")
        show.setToolTip("Work it through in full, and stop counting this one")
        show.setCursor(Qt.PointingHandCursor)
        row.addWidget(show)

        again = QPushButton("New question")
        again.setToolTip(
            "Draw another of the same kind, with new numbers. Enter does "
            "this too, once the answer has been marked."
        )
        again.setCursor(Qt.PointingHandCursor)
        row.addWidget(again)
        layout.addLayout(row)

        verdict = QLabel("")
        verdict.setWordWrap(True)
        verdict.setTextFormat(Qt.RichText)
        layout.addWidget(verdict)
        self._verdicts[template.key] = verdict

        hints = QLabel("")
        hints.setProperty("role", "muted")
        hints.setWordWrap(True)
        hints.setVisible(False)
        layout.addWidget(hints)

        working = StepsPanel(palette)
        working.setMinimumHeight(240)
        working.setVisible(False)
        layout.addWidget(working)

        self._wire_hints(question, hints, hint_button)

        def graded() -> bool:
            marked = self._check_solve(lesson, question, answer, verdict,
                                       bucket=progress.drill_key(lesson.key),
                                       key=template.key)
            now, done = self._streak_of(lesson, template)
            run.setText(self._streak_text(now, done))
            run.setStyleSheet(
                f"color: {palette.success if done else palette.text_muted};"
            )
            return marked

        def next_question() -> None:
            self._drill_seed[template.key] = seed + 1
            self._focus_drill = template.key
            self._show()

        check.clicked.connect(graded)
        self._keyboard_loop(frame, template, answer, graded, next_question)
        show.clicked.connect(
            lambda: self._work(question.equation, question.conditions,
                               template.narrator, working, show)
        )
        again.clicked.connect(next_question)
        return frame

    def _build_choice_drill(self, lesson, template, question, run: QLabel,
                            layout, frame) -> None:
        """The radio-button half of a drill, for a generated `Choice`.

        Everything a `Solve` drill offers that a `Choice` cannot honour is left
        out: no hint ladder, because a `Choice` has no hints, and no "Show me",
        because there is no narrator to show. Offering a button that cannot do
        anything is worse than not offering it.
        """
        palette = self.palette_obj
        if question.latex:
            layout.addWidget(MathLabel(self.palette_obj, question.latex,
                                       point_size=15))
        if question.shown:
            # A generated question cannot be typeset: the equation comes out
            # of the draw, and authoring a LaTeX form of it as well would be
            # writing the same equation twice and waiting for the two to
            # disagree. So it is shown in the font the editor uses, which is
            # also the form it would be typed in.
            written = QLabel(question.shown)
            written.setStyleSheet(
                "font-family: Cascadia Mono, Consolas, monospace;"
            )
            written.setWordWrap(True)
            layout.addWidget(written)

        # Parented to the card, as `_build_choice` explains: a group owned by
        # the screen would outlive its own buttons and accumulate a dead set
        # per visit.
        group = QButtonGroup(layout.parentWidget())
        group.setExclusive(True)
        for index, option in enumerate(question.options):
            button = QRadioButton(option)
            button.setCursor(Qt.PointingHandCursor)
            group.addButton(button, index)
            layout.addWidget(button)

        verdict = QLabel("")
        verdict.setWordWrap(True)
        layout.addWidget(verdict)
        self._verdicts[template.key] = verdict

        row = QHBoxLayout()
        row.setSpacing(8)
        check = QPushButton("Check")
        check.setToolTip("Mark what you have entered")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)

        again = QPushButton("New question")
        again.setToolTip(
            "Draw another of the same kind, with new numbers. Enter does "
            "this too, once the answer has been marked."
        )
        again.setCursor(Qt.PointingHandCursor)
        row.addWidget(again)
        row.addStretch(1)
        layout.addLayout(row)

        def graded() -> bool:
            marked = self._check_choice(lesson, question, group, verdict,
                                        bucket=progress.drill_key(lesson.key),
                                        key=template.key)
            now, done = self._streak_of(lesson, template)
            run.setText(self._streak_text(now, done))
            run.setStyleSheet(
                f"color: {palette.success if done else palette.text_muted};"
            )
            return marked

        def next_question() -> None:
            self._drill_seed[template.key] = (
                self._drill_seed.get(template.key, 0) + 1
            )
            self._focus_drill = template.key
            self._show()

        check.clicked.connect(graded)
        self._keyboard_loop(frame, template, None, graded, next_question)
        again.clicked.connect(next_question)

    def _build_numeric_drill(self, lesson, template, question, run: QLabel,
                             layout, frame) -> None:
        """The typed-number half of a drill, for a generated `Numeric`.

        Closer to the `Solve` drill than to the `Choice` one -- there is a box
        to type in and a ladder of hints behind it -- but there is no narrator,
        because what is being asked for is a step of a method rather than a
        solution to be worked through. So no "Show me"; the reason the answer
        is what it is arrives with the verdict instead.
        """
        palette = self.palette_obj
        if question.latex:
            layout.addWidget(MathLabel(self.palette_obj, question.latex,
                                       point_size=15))

        row = QHBoxLayout()
        row.setSpacing(8)
        answer = QLineEdit()
        answer.setAccessibleName("your answer")
        answer.setPlaceholderText("a number")
        answer.setClearButtonEnabled(True)
        row.addWidget(answer, 1)

        if question.units:
            # Beside the box rather than inside it: the units are never part of
            # what is typed, and a placeholder that showed them would invite
            # somebody to type them.
            units = QLabel(question.units)
            units.setProperty("role", "muted")
            row.addWidget(units)

        check = QPushButton("Check")
        check.setToolTip("Mark the number you have entered")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)

        hint_button = QPushButton("Hint")
        hint_button.setToolTip(
            "Reveal the next hint. They come one at a time, and never the "
            "answer."
        )
        hint_button.setCursor(Qt.PointingHandCursor)
        hint_button.setEnabled(bool(question.hints))
        row.addWidget(hint_button)

        again = QPushButton("New question")
        again.setToolTip(
            "Draw another of the same kind, with new numbers. Enter does "
            "this too, once the answer has been marked."
        )
        again.setCursor(Qt.PointingHandCursor)
        row.addWidget(again)
        layout.addLayout(row)

        verdict = QLabel("")
        verdict.setWordWrap(True)
        verdict.setTextFormat(Qt.RichText)
        layout.addWidget(verdict)
        self._verdicts[template.key] = verdict

        hints = QLabel("")
        hints.setProperty("role", "muted")
        hints.setWordWrap(True)
        hints.setVisible(False)
        layout.addWidget(hints)

        self._wire_hints(question, hints, hint_button)

        def graded() -> bool:
            marked = self._check_numeric(lesson, question, answer, verdict,
                                         bucket=progress.drill_key(lesson.key),
                                         key=template.key)
            now, done = self._streak_of(lesson, template)
            run.setText(self._streak_text(now, done))
            run.setStyleSheet(
                f"color: {palette.success if done else palette.text_muted};"
            )
            return marked

        def next_question() -> None:
            self._drill_seed[template.key] = (
                self._drill_seed.get(template.key, 0) + 1
            )
            self._focus_drill = template.key
            self._show()

        check.clicked.connect(graded)
        self._keyboard_loop(frame, template, answer, graded, next_question)
        again.clicked.connect(next_question)

    def _build_model_drill(self, lesson, template, question, run: QLabel,
                           layout, frame) -> None:
        """The half of a drill that asks for an equation rather than a number.

        A `Model` question gives a situation, or a family of curves, and asks
        what equation it is. So the box wants an equation in it, and the
        placeholder says so -- somebody who types only a right-hand side is
        told to write the whole thing rather than marked wrong for it.

        No "Show me", for the same reason the numeric drill has none: the
        narrator works equations, and this question has not got to one yet.
        The account of where each term comes from arrives with the verdict
        instead.
        """
        palette = self.palette_obj
        if question.latex:
            layout.addWidget(MathLabel(self.palette_obj, question.latex,
                                       point_size=15))

        row = QHBoxLayout()
        row.setSpacing(8)
        answer = QLineEdit()
        answer.setAccessibleName("your answer")
        answer.setPlaceholderText("y' = ...")
        answer.setClearButtonEnabled(True)
        row.addWidget(answer, 1)

        check = QPushButton("Check")
        check.setToolTip("Mark the equation you have written")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)

        hint_button = QPushButton("Hint")
        hint_button.setToolTip(
            "Reveal the next hint. They come one at a time, and never the "
            "equation."
        )
        hint_button.setCursor(Qt.PointingHandCursor)
        hint_button.setEnabled(bool(question.hints))
        row.addWidget(hint_button)

        again = QPushButton("New question")
        again.setToolTip(
            "Draw another of the same kind, with new numbers. Enter does "
            "this too, once the answer has been marked."
        )
        again.setCursor(Qt.PointingHandCursor)
        row.addWidget(again)
        layout.addLayout(row)

        verdict = QLabel("")
        verdict.setWordWrap(True)
        verdict.setTextFormat(Qt.RichText)
        layout.addWidget(verdict)
        self._verdicts[template.key] = verdict

        hints = QLabel("")
        hints.setProperty("role", "muted")
        hints.setWordWrap(True)
        hints.setVisible(False)
        layout.addWidget(hints)

        self._wire_hints(question, hints, hint_button)

        def graded() -> bool:
            marked = self._check_model(lesson, question, answer, verdict,
                                       bucket=progress.drill_key(lesson.key),
                                       key=template.key)
            now, done = self._streak_of(lesson, template)
            run.setText(self._streak_text(now, done))
            run.setStyleSheet(
                f"color: {palette.success if done else palette.text_muted};"
            )
            return marked

        def next_question() -> None:
            self._drill_seed[template.key] = (
                self._drill_seed.get(template.key, 0) + 1
            )
            self._focus_drill = template.key
            self._show()

        check.clicked.connect(graded)
        self._keyboard_loop(frame, template, answer, graded, next_question)
        again.clicked.connect(next_question)

    def _build_expression_drill(self, lesson, template, question, run: QLabel,
                                layout, frame) -> None:
        """The half of a drill that asks for one move of a method.

        The integrating factor, the characteristic polynomial, the Wronskian.
        The box wants an expression, so the placeholder shows the notation the
        rest of the application reads -- ``exp`` rather than a written-out e,
        because that is what the editor accepts everywhere else and a drill is
        a bad place to teach a second dialect.
        """
        palette = self.palette_obj
        if question.latex:
            layout.addWidget(MathLabel(self.palette_obj, question.latex,
                                       point_size=15))

        row = QHBoxLayout()
        row.setSpacing(8)
        answer = QLineEdit()
        answer.setAccessibleName("your answer")
        answer.setPlaceholderText("an expression, like exp(3*t)")
        answer.setClearButtonEnabled(True)
        row.addWidget(answer, 1)

        check = QPushButton("Check")
        check.setToolTip("Mark the expression you have written")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)

        hint_button = QPushButton("Hint")
        hint_button.setToolTip(
            "Reveal the next hint. They come one at a time, and never the "
            "answer."
        )
        hint_button.setCursor(Qt.PointingHandCursor)
        hint_button.setEnabled(bool(question.hints))
        row.addWidget(hint_button)

        again = QPushButton("New question")
        again.setToolTip(
            "Draw another of the same kind, with new numbers. Enter does "
            "this too, once the answer has been marked."
        )
        again.setCursor(Qt.PointingHandCursor)
        row.addWidget(again)
        layout.addLayout(row)

        verdict = QLabel("")
        verdict.setWordWrap(True)
        verdict.setTextFormat(Qt.RichText)
        layout.addWidget(verdict)
        self._verdicts[template.key] = verdict

        hints = QLabel("")
        hints.setProperty("role", "muted")
        hints.setWordWrap(True)
        hints.setVisible(False)
        layout.addWidget(hints)

        self._wire_hints(question, hints, hint_button)

        def graded() -> bool:
            marked = self._check_expression(
                lesson, question, answer, verdict,
                bucket=progress.drill_key(lesson.key), key=template.key,
            )
            now, done = self._streak_of(lesson, template)
            run.setText(self._streak_text(now, done))
            run.setStyleSheet(
                f"color: {palette.success if done else palette.text_muted};"
            )
            return marked

        def next_question() -> None:
            self._drill_seed[template.key] = (
                self._drill_seed.get(template.key, 0) + 1
            )
            self._focus_drill = template.key
            self._show()

        check.clicked.connect(graded)
        self._keyboard_loop(frame, template, answer, graded, next_question)
        again.clicked.connect(next_question)

    def _question_card(self, lesson, number: int, question) -> QWidget:
        frame, layout = self._panel()

        prompt = QLabel(f"{number}.  {question.prompt}")
        prompt.setProperty("role", "heading")
        prompt.setWordWrap(True)
        layout.addWidget(prompt)
        # After the prompt and before the options: the prompt says what to
        # read off the picture, so it has to have been read first.
        self._question_figure(question, layout)

        # Dispatched by kind rather than by "choice or everything else",
        # which is what it was. A practice question could only ever be a
        # `Choice` or a `Solve`, so the fall-through was safe; the first
        # `Numeric` written into a lesson's `questions` landed in
        # `_build_solve` and raised on `question.equation`, which a `Numeric`
        # does not have. An unknown kind now says so on the card instead of
        # taking the page down.
        builder = {
            "choice": self._build_choice,
            "numeric": self._build_numeric,
            "solve": self._build_solve,
        }.get(question.kind)
        if builder is None:
            unknown = QLabel(
                f"this question is a {question.kind!r}, which this screen "
                "does not know how to ask"
            )
            unknown.setWordWrap(True)
            unknown.setStyleSheet(
                theme.scaled(f"color: {self.palette_obj.danger};")
            )
            layout.addWidget(unknown)
        else:
            builder(lesson, question, layout)
        return frame

    def _question_figure(self, question, layout) -> None:
        """Put a question's own figure above its prompt, where it has one.

        The same widget the Learn segment shows, deliberately: a question
        about a phase portrait should be answered by moving the sliders on
        the phase portrait, not by remembering one. The figure is live here
        for the same reason it is live there.

        Silent where the key is unknown, as `build_figure` is: a question that
        lost its picture is still a question, and the tests catch the typo.
        """
        key = getattr(question, "figure", "")
        if not key:
            return
        figure = build_figure(key, self.palette_obj)
        if figure is not None:
            layout.addWidget(figure)

    def _build_choice(self, lesson, question, layout) -> None:
        if question.latex:
            layout.addWidget(MathLabel(self.palette_obj, question.latex,
                                       point_size=15))

        # Parented to the card, not to the screen: switching lesson or segment
        # deletes the cards, and a group owned by the screen would outlive its
        # own radio buttons and accumulate one dead set per visit.
        group = QButtonGroup(layout.parentWidget())
        group.setExclusive(True)
        for index, option in enumerate(question.options):
            button = QRadioButton(option)
            button.setCursor(Qt.PointingHandCursor)
            group.addButton(button, index)
            layout.addWidget(button)

        verdict = QLabel("")
        verdict.setWordWrap(True)
        layout.addWidget(verdict)
        self._verdicts[question.key] = verdict

        row = QHBoxLayout()
        check = QPushButton("Check")
        check.setToolTip("Mark what you have entered")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)
        row.addStretch(1)
        layout.addLayout(row)

        check.clicked.connect(
            lambda: self._check_choice(lesson, question, group, verdict)
        )
        self._restore(lesson, question, verdict)

    def _build_numeric(self, lesson, question, layout) -> None:
        """A practice question whose answer is a number.

        The same shape as the drill's numeric card and for the same reasons:
        a box, a tolerance-graded check through `symbolic.grade_numeric`, and
        the hint ladder behind it. No "Show me" — what is being asked for is a
        value read off a figure or off one step of a method, and there is no
        narrator that works through *that*; the reason the answer is the
        answer arrives with the verdict instead.
        """
        row = QHBoxLayout()
        row.setSpacing(8)
        answer = QLineEdit()
        answer.setAccessibleName("your answer")
        answer.setPlaceholderText("a number")
        answer.setClearButtonEnabled(True)
        row.addWidget(answer, 1)

        if question.units:
            # Beside the box rather than inside it: the units are never part
            # of what is typed, and a placeholder showing them would invite
            # somebody to type them.
            units = QLabel(question.units)
            units.setProperty("role", "muted")
            row.addWidget(units)

        check = QPushButton("Check")
        check.setToolTip("Mark the number you have entered")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)

        hint_button = QPushButton("Hint")
        hint_button.setToolTip(
            "Reveal the next hint. They come one at a time, and never the "
            "answer."
        )
        hint_button.setCursor(Qt.PointingHandCursor)
        hint_button.setEnabled(bool(question.hints))
        row.addWidget(hint_button)
        layout.addLayout(row)

        verdict = QLabel("")
        verdict.setWordWrap(True)
        verdict.setTextFormat(Qt.RichText)
        layout.addWidget(verdict)
        self._verdicts[question.key] = verdict

        hints = QLabel("")
        hints.setProperty("role", "muted")
        hints.setWordWrap(True)
        hints.setVisible(False)
        layout.addWidget(hints)

        self._wire_hints(question, hints, hint_button)
        check.clicked.connect(
            lambda: self._check_numeric(lesson, question, answer, verdict)
        )
        answer.returnPressed.connect(
            lambda: self._check_numeric(lesson, question, answer, verdict)
        )
        self._restore(lesson, question, verdict)

    def _build_solve(self, lesson, question, layout) -> None:
        shown = question.equation + (
            f",   {question.conditions}" if question.conditions else ""
        )
        equation = QLabel(shown)
        equation.setStyleSheet("font-family: Cascadia Mono, Consolas, monospace;")
        equation.setWordWrap(True)
        layout.addWidget(equation)

        row = QHBoxLayout()
        row.setSpacing(8)
        answer = QLineEdit()
        answer.setAccessibleName("your answer")
        answer.setPlaceholderText("y = ...")
        answer.setClearButtonEnabled(True)
        row.addWidget(answer, 1)

        check = QPushButton("Check")
        check.setToolTip("Mark what you have entered")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)

        hint_button = QPushButton("Hint")
        hint_button.setToolTip(
            "Reveal the next hint. They come one at a time, and never "
            "the answer."
        )
        hint_button.setCursor(Qt.PointingHandCursor)
        hint_button.setEnabled(bool(question.hints))
        row.addWidget(hint_button)

        show = QPushButton("Show me")
        show.setToolTip("Work it through in full, and stop counting this one")
        show.setCursor(Qt.PointingHandCursor)
        row.addWidget(show)
        layout.addLayout(row)

        verdict = QLabel("")
        verdict.setWordWrap(True)
        verdict.setTextFormat(Qt.RichText)
        layout.addWidget(verdict)
        self._verdicts[question.key] = verdict

        # One rung at a time. A hint that hands over the whole method on the
        # first press is not a hint, and the last rung is the narrator itself.
        hints = QLabel("")
        hints.setProperty("role", "muted")
        hints.setWordWrap(True)
        hints.setVisible(False)
        layout.addWidget(hints)

        working = StepsPanel(self.palette_obj)
        working.setMinimumHeight(240)
        working.setVisible(False)
        layout.addWidget(working)

        self._wire_hints(question, hints, hint_button)

        check.clicked.connect(
            lambda: self._check_solve(lesson, question, answer, verdict)
        )
        answer.returnPressed.connect(
            lambda: self._check_solve(lesson, question, answer, verdict)
        )
        show.clicked.connect(
            lambda: self._work(question.equation, question.conditions,
                               lesson.narrator, working, show)
        )
        self._restore(lesson, question, verdict)

    def _wire_hints(self, question, hints: QLabel,
                    hint_button: QPushButton) -> None:
        """One rung per press, and the button says how many are left.

        Shared by Practice and Drill, because a generated question *is* an
        ordinary question and its ladder had better behave identically.
        """
        shown: list[str] = []

        def next_hint() -> None:
            ladder = question.hints
            if len(shown) >= len(ladder):
                hint_button.setEnabled(False)
                return
            shown.append(ladder[len(shown)])
            hints.setText("\n\n".join(
                f"{number}.  {text}"
                for number, text in enumerate(shown, start=1)
            ))
            hints.setVisible(True)
            remaining = len(ladder) - len(shown)
            hint_button.setText(f"Next hint ({remaining} left)" if remaining
                                else "That is every hint")
            hint_button.setEnabled(bool(remaining))

        hint_button.clicked.connect(next_hint)

    # -- grading ---------------------------------------------------------

    def _restore(self, lesson, question, verdict: QLabel) -> None:
        """Show what was recorded last time, so a tick survives a restart."""
        answer = self._answered.get(lesson.key, {}).get(question.key)
        if answer is None:
            return
        tally = "" if answer.tries < 2 else f"  ({answer.tries} attempts)"
        if answer.correct:
            verdict.setStyleSheet(f"color: {self.palette_obj.success};")
            verdict.setText("✓ answered correctly" + tally)
        else:
            verdict.setStyleSheet(f"color: {self.palette_obj.text_muted};")
            verdict.setText("attempted" + tally)

    def _record(self, bucket: str, key: str, state: str,
                picked: int | None = None) -> None:
        """Note one answer.

        `bucket` is the lesson's own key for its practice questions, and
        `progress.drill_key(lesson)` for its drills -- a separate bucket, so
        that an unbounded number of generated answers cannot disturb the
        "3 of 5" the practice questions mean.

        `picked` is the *author's* index for the option chosen, where one was.
        Kept because a state cannot say which wrong answer somebody gave, and
        the wrong answer is the interesting half: the options are written as
        one misconception apiece, and the same one chosen four times is a
        different fact from four questions missed.
        """
        self._answered = progress.record(bucket, key, state, picked=picked)
        self._refresh_labels()

    def _check_choice(self, lesson, question, group, verdict: QLabel, *,
                      bucket: str = "", key: str = "") -> bool:
        """Mark one multiple-choice answer. True if there was one to mark.

        The verdict is the point; the return value exists for the keyboard
        loop, which has to know whether this press was the check or whether
        the check never happened -- see `_keyboard_loop`.
        """
        picked = group.checkedId()
        palette = self.palette_obj
        if picked < 0:
            verdict.setStyleSheet(f"color: {palette.text_muted};")
            verdict.setText("pick an option first")
            return False

        right = content.grade_choice(question, picked)
        verdict.setStyleSheet(
            f"color: {palette.success if right else palette.danger};"
        )
        # The reason for the option *picked*, not for the right one. A tick
        # that does not say why teaches nothing, and a cross that explains
        # someone else's answer teaches less than nothing.
        reason = (question.becauses[picked]
                  if picked < len(question.becauses) else question.because)
        verdict.setText(("✓ Right. " if right else "✗ Not quite. ") + reason)
        # A drill records into its own bucket under the *template's* key, not
        # the lesson's question bucket. The two numbers mean different things
        # and the Course Map shows both: questions are out of a fixed
        # denominator, drills are a streak that can go back down.
        #
        # The pick is recorded through `Choice.canonical`, which undoes the
        # per-draw shuffle. A drill records under the template's key, so its
        # picks accumulate across draws -- and a bare position would be a
        # different option in each of them, which is precisely the tally the
        # shuffle exists to prevent anyone drilling.
        self._record(bucket or lesson.key, key or question.key,
                     progress.State.CORRECT if right else progress.State.ATTEMPTED,
                     picked=question.canonical(picked))
        return True

    def _check_solve(self, lesson, question, answer: QLineEdit,
                     verdict: QLabel, *, bucket: str = "",
                     key: str = "") -> bool:
        from ..laplace import EXTRA_FUNCTIONS
        from ..symbolic import check_answer, parse_equation, spec_for

        palette = self.palette_obj
        try:
            # `spec_for` rather than a one-equation spec: a systems drill
            # writes its question as "x' = ...; y' = ...", and splitting on
            # that semicolon is what turns it into a system rather than one
            # unparseable line.
            parsed = parse_equation(
                spec_for(question.equation, question.conditions),
                extra_functions=EXTRA_FUNCTIONS,
            )
        except Exception as exc:                  # a broken question, not a
            verdict.setStyleSheet(f"color: {palette.danger};")   # broken answer
            verdict.setText(f"this question could not be set up: {exc}")
            return False

        result = check_answer(parsed, answer.text())
        if result.correct is True and result.matches_conditions is not False:
            colour, text = palette.success, "✓ " + result.message
            state = progress.State.CORRECT
        elif result.correct is False or result.matches_conditions is False:
            colour, text = palette.danger, "✗ " + result.message
            state = progress.State.ATTEMPTED
        else:
            colour, text = palette.text_muted, result.message
            state = progress.State.ATTEMPTED

        # The residual is evidence, not a verdict, and `symbolic.diagnose`
        # turns it into a sentence wherever it recognises one -- "you have the
        # complementary function and no particular solution" rather than
        # "-6*t". Where it recognises nothing the expression is still shown:
        # it is worth less than the sentence and a great deal more than
        # silence, and the person who can read it should not lose it.
        detail = ""
        if result.diagnosis:
            detail = (f'<br><span style="color:{palette.text_muted};'
                      f'font-size:12px;">{result.diagnosis}</span>')
        elif result.correct is False and result.residual is not None:
            detail = (f'<br><span style="color:{palette.text_muted};'
                      f'font-size:12px;">what is left over: '
                      f"{result.residual}</span>")
        verdict.setStyleSheet("")
        verdict.setText(f'<span style="color:{colour};">{text}</span>{detail}')
        self._record(bucket or lesson.key, key or question.key, state)
        return True

    def _check_numeric(self, lesson, question, answer: QLineEdit,
                       verdict: QLabel, *, bucket: str = "",
                       key: str = "") -> bool:
        """Mark a typed number, and say why the answer is the answer.

        Three verdicts rather than two, as everywhere else here: right, wrong,
        and *could not read that*. The third records an attempt but says
        nothing about the mathematics, because a typo is not a mistake about
        Euler's method.
        """
        from ..symbolic import grade_numeric

        palette = self.palette_obj
        right, message = grade_numeric(question, answer.text())
        if right is True:
            colour, text = palette.success, "✓ " + message
            state = progress.State.CORRECT
        elif right is False:
            colour, text = palette.danger, "✗ " + message
            state = progress.State.ATTEMPTED
        else:
            colour, text = palette.text_muted, message
            state = progress.State.ATTEMPTED

        detail = ""
        if right is not None and question.because:
            detail = (f'<br><span style="color:{palette.text_muted};'
                      f'font-size:12px;">{question.because}</span>')
        verdict.setStyleSheet("")
        verdict.setText(f'<span style="color:{colour};">{text}</span>{detail}')
        self._record(bucket or lesson.key, key or question.key, state)
        # "could not read that" is not a mark. The keyboard loop stays on this
        # question rather than counting a typo as a turn taken.
        return right is not None

    def _check_model(self, lesson, question, answer: QLineEdit,
                     verdict: QLabel, *, bucket: str = "",
                     key: str = "") -> bool:
        """Mark an equation somebody wrote, and say where a wrong one differs.

        The three verdicts again, and the third does more work here than
        anywhere else: "write the whole equation, with an = in it" and "write
        it in terms of y" are both things to fix rather than things to be
        marked wrong for, and neither says anything about whether the model
        was understood.

        A wrong answer shows what is left over when the two equations are
        subtracted, which is usually the whole diagnosis -- a forgotten
        inflow term appears by itself, and a sign that went the wrong way
        appears as twice the term it belongs to.
        """
        from ..symbolic import check_model

        palette = self.palette_obj
        result = check_model(question.equation, answer.text())
        if result.correct is True:
            colour, text = palette.success, "✓ " + result.message
            state = progress.State.CORRECT
        elif result.correct is False:
            colour, text = palette.danger, "✗ " + result.message
            state = progress.State.ATTEMPTED
        else:
            colour, text = palette.text_muted, result.message
            state = progress.State.ATTEMPTED

        detail = ""
        if result.correct is False and result.difference is not None:
            detail = self._aside(f"what differs: {result.difference}")
        elif result.correct is True and question.because:
            detail = self._aside(question.because)
        verdict.setStyleSheet("")
        verdict.setText(f'<span style="color:{colour};">{text}</span>{detail}')
        self._record(bucket or lesson.key, key or question.key, state)
        return result.correct is not None

    def _check_expression(self, lesson, question, answer: QLineEdit,
                          verdict: QLabel, *, bucket: str = "",
                          key: str = "") -> bool:
        """Mark one move of a method."""
        from ..symbolic import check_expression

        palette = self.palette_obj
        result = check_expression(question.answer, answer.text(),
                                  up_to_constant=question.up_to_constant)
        if result.correct is True:
            colour, text = palette.success, "✓ " + result.message
            state = progress.State.CORRECT
        elif result.correct is False:
            colour, text = palette.danger, "✗ " + result.message
            state = progress.State.ATTEMPTED
        else:
            colour, text = palette.text_muted, result.message
            state = progress.State.ATTEMPTED

        detail = ""
        if result.correct is not None and question.because:
            detail = self._aside(question.because)
        verdict.setStyleSheet("")
        verdict.setText(f'<span style="color:{colour};">{text}</span>{detail}')
        self._record(bucket or lesson.key, key or question.key, state)
        return result.correct is not None

    def _aside(self, text: str) -> str:
        """A second line under a verdict, in the muted colour."""
        return (f'<br><span style="color:{self.palette_obj.text_muted};'
                f'font-size:12px;">{text}</span>')

    # -- the worked solution ---------------------------------------------

    def _abandon(self) -> None:
        """Give up on anything in flight, and free the buttons waiting on it."""
        self._token += 1
        self._pending.clear()

    def _work(self, equation: str, conditions: str, narrator: str,
              panel: StepsPanel, button: QPushButton) -> None:
        self._token += 1
        # Whatever else was waiting will never be delivered now, so hand its
        # button back rather than leaving it disabled for the rest of the visit.
        for stale_panel, stale_button in self._pending.values():
            stale_button.setEnabled(True)
            stale_panel.clear("superseded")
        self._pending.clear()

        panel.setVisible(True)
        panel.clear("working it through…")
        button.setEnabled(False)
        self._pending[self._token] = (panel, button)
        QThreadPool.globalInstance().start(
            _WorkingJob(self._token, equation, conditions, narrator,
                        self._signals)
        )

    def _on_worked(self, token: int, result) -> None:
        waiting = self._pending.pop(token, None)
        if waiting is None:
            return                                # superseded, or not ours
        panel, button = waiting
        button.setEnabled(True)
        if isinstance(result, Exception):
            panel.clear(f"{type(result).__name__}: {result}")
            return
        if result is None:
            panel.clear("no working could be produced for this one")
            return
        panel.show_derivation(result)

    # -- the rest --------------------------------------------------------

    def _open_tool(self) -> None:
        lesson = self.current_lesson()
        if lesson is None:
            return
        if lesson.tool == "portrait":
            # The portrait takes a catalogue key, not an equation: what a
            # nonlinear lesson is about is a system no narrator can solve, and
            # its worked examples are the pieces of it that can be.
            self.open_tool.emit("portrait", lesson.portrait, "")
            return
        self.open_tool.emit(lesson.tool, lesson.example,
                            lesson.example_conditions)

    def _describe_tool(self, lesson) -> None:
        """Say which screen the button opens, and on what.

        The button used to promise "with an example loaded" and deliver an
        empty one. Now that it delivers, it can say which equation it is
        taking -- and where the tool cannot accept a typed equation, it says
        the plainer thing instead of the old claim.
        """
        if lesson is None:
            self.tool_button.setText("Open the tool for this topic")
            self.tool_button.setToolTip("")
            self.tool_button.setEnabled(False)
            return
        self.tool_button.setEnabled(True)
        name = TOOL_NAMES.get(lesson.tool, "the tool for this topic")
        self.tool_button.setText(f"Open in {name}")
        equation = lesson.example
        if lesson.tool == "portrait" and lesson.portrait:
            from .. import catalog

            try:
                title = catalog.get(lesson.portrait).title
            except KeyError:
                title = lesson.portrait
            self.tool_button.setToolTip(f"Opens {name} on  {title}")
        elif equation and lesson.tool in CARRIES_EQUATION:
            shown = equation + (f",  {lesson.example_conditions}"
                                if lesson.example_conditions else "")
            self.tool_button.setToolTip(f"Opens {name} on  {shown}")
        else:
            self.tool_button.setToolTip(f"Opens {name}")

    def _reset(self) -> None:
        progress.reset()
        self._answered = {}
        self._refresh_labels()
        self._show()

    def _clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def set_palette_colours(self, palette: Palette) -> None:
        self.palette_obj = palette
