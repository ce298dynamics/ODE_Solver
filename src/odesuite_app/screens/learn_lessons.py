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
from .. import progress
from ..lessons import generate
from ..theme import Palette
from ..widgets.controls import add_heading, control_panel
from ..widgets.lessonfigure import build_figure
from ..widgets.mathlabel import MathLabel
from ..widgets.stepspanel import StepsPanel

__all__ = ["LessonsScreen", "SEGMENTS"]

#: The parts of a lesson, in the order they are meant to be met. `Drill` is
#: offered only where the lesson has templates -- see `_build_drill`.
SEGMENTS = ("Learn", "Examples", "Practice", "Drill")


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


class LessonsScreen(QWidget):
    """One lesson at a time: what it is, worked examples, and practice."""

    #: Asks the window to open the tool a lesson belongs to.
    open_tool = Signal(str)

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
        #: Question key -> the label that shows its verdict.
        self._verdicts: dict[str, QLabel] = {}
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

        self.reset_button = QPushButton("Reset progress")
        self.reset_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.reset_button)

        where = QLabel(f"Answers are remembered in\n{progress.path()}")
        where.setProperty("role", "muted")
        where.setWordWrap(True)
        where.setStyleSheet("font-size: 10px;")
        layout.addWidget(where)

        self.listing.currentItemChanged.connect(lambda *_: self._show())
        self.tool_button.clicked.connect(self._open_tool)
        self.reset_button.clicked.connect(self._reset)
        return panel

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
        self._abandon()

        if lesson is None:
            # A unit heading is selected rather than a lesson. Say so instead
            # of leaving the reading column blank.
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
            # rather than opening an empty page. Euler and RK4 have no closed
            # form for the grader to substitute into, so a drill there could
            # never say "right" — which is worse than not offering one.
            button.setVisible(name != "Drill" or bool(lesson.templates))
        if self._segment == "Drill" and not lesson.templates:
            self._segment = "Practice"
            self.segment_buttons["Practice"].setChecked(True)

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

    def _build_learn(self, lesson) -> None:
        if lesson.objectives:
            self._layout.addWidget(self._objectives_card(lesson))
        # After the objectives and before the notes: a figure is a thing to
        # play with while reading, not a summary of what was read.
        if lesson.figure:
            figure = build_figure(lesson.figure, self.palette_obj)
            if figure is not None:
                self._layout.addWidget(figure)
        for note in lesson.notes:
            self._layout.addWidget(self._note_card(note))

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
        substituting = any(item.kind == "template" for item in lesson.templates)
        choosing = any(item.kind == "choice-template"
                       for item in lesson.templates)
        how = (
            "your answer is substituted into its own equation, so any correct "
            "form passes" if substituting and not choosing else
            "pick the right option" if choosing and not substituting else
            "typed answers are substituted into their own equation; the "
            "multiple-choice ones are marked against their answer"
        )
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

    def _panel(self, accent: str = "") -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setProperty("role", "panel")
        if accent:
            frame.setStyleSheet(f"QFrame {{ border-left: 3px solid {accent}; }}")
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
            row = QLabel(f"·  {objective}")
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
            tag.setStyleSheet(
                f"color: {palette.warning if note.kind == 'pitfall' else palette.text_muted};"
                "font-size: 10px; letter-spacing: 1px;"
            )
            layout.addWidget(tag)

        heading = QLabel(note.heading)
        heading.setProperty("role", "heading")
        heading.setWordWrap(True)
        layout.addWidget(heading)

        body = QLabel(note.body)
        body.setWordWrap(True)
        layout.addWidget(body)

        if note.latex:
            layout.addWidget(MathLabel(palette, note.latex, point_size=15))
        return frame

    def _example_card(self, number: int, example) -> QWidget:
        frame, layout = self._panel()

        heading = QLabel(f"Example {number}")
        heading.setProperty("role", "heading")
        layout.addWidget(heading)

        if example.why:
            why = QLabel(example.why)
            why.setProperty("role", "muted")
            why.setWordWrap(True)
            layout.addWidget(why)

        shown = example.equation + (
            f",   {example.conditions}" if example.conditions else ""
        )
        equation = QLabel(shown)
        equation.setStyleSheet("font-family: Cascadia Mono, Consolas, monospace;")
        equation.setWordWrap(True)
        layout.addWidget(equation)

        row = QHBoxLayout()
        button = QPushButton("Work it through")
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

    def _drill_card(self, lesson, template) -> QWidget:
        palette = self.palette_obj
        seed = self._drill_seed.setdefault(template.key, 0)
        question = generate.draw(template, seed)
        streak, mastered = self._streak_of(lesson, template)

        frame, layout = self._panel(palette.success if mastered else "")

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
            f"{generate.combinations(template)} versions"
        )
        prompt.setProperty("role", "muted")
        prompt.setWordWrap(True)
        layout.addWidget(prompt)

        # A generated multiple-choice drill takes the other path. It has no
        # hint ladder and no narrator -- a `Choice` carries neither -- so the
        # Hint and "Show me" buttons are absent rather than present and inert.
        if question.kind == "choice":
            self._build_choice_drill(lesson, template, question, run, layout)
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
        answer.setPlaceholderText("y = ...")
        answer.setClearButtonEnabled(True)
        row.addWidget(answer, 1)

        check = QPushButton("Check")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)

        hint_button = QPushButton("Hint")
        hint_button.setCursor(Qt.PointingHandCursor)
        hint_button.setEnabled(bool(question.hints))
        row.addWidget(hint_button)

        show = QPushButton("Show me")
        show.setCursor(Qt.PointingHandCursor)
        row.addWidget(show)

        again = QPushButton("New question")
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

        def graded() -> None:
            self._check_solve(lesson, question, answer, verdict,
                              bucket=progress.drill_key(lesson.key),
                              key=template.key)
            now, done = self._streak_of(lesson, template)
            run.setText(self._streak_text(now, done))
            run.setStyleSheet(
                f"color: {palette.success if done else palette.text_muted};"
            )

        def next_question() -> None:
            self._drill_seed[template.key] = seed + 1
            self._show()

        check.clicked.connect(graded)
        answer.returnPressed.connect(graded)
        show.clicked.connect(
            lambda: self._work(question.equation, question.conditions,
                               template.narrator, working, show)
        )
        again.clicked.connect(next_question)
        return frame

    def _build_choice_drill(self, lesson, template, question, run: QLabel,
                            layout) -> None:
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
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)

        again = QPushButton("New question")
        again.setCursor(Qt.PointingHandCursor)
        row.addWidget(again)
        row.addStretch(1)
        layout.addLayout(row)

        def graded() -> None:
            self._check_choice(lesson, question, group, verdict,
                               bucket=progress.drill_key(lesson.key),
                               key=template.key)
            now, done = self._streak_of(lesson, template)
            run.setText(self._streak_text(now, done))
            run.setStyleSheet(
                f"color: {palette.success if done else palette.text_muted};"
            )

        def next_question() -> None:
            self._drill_seed[template.key] = (
                self._drill_seed.get(template.key, 0) + 1
            )
            self._show()

        check.clicked.connect(graded)
        again.clicked.connect(next_question)

    def _question_card(self, lesson, number: int, question) -> QWidget:
        frame, layout = self._panel()

        prompt = QLabel(f"{number}.  {question.prompt}")
        prompt.setProperty("role", "heading")
        prompt.setWordWrap(True)
        layout.addWidget(prompt)

        if question.kind == "choice":
            self._build_choice(lesson, question, layout)
        else:
            self._build_solve(lesson, question, layout)
        return frame

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
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)
        row.addStretch(1)
        layout.addLayout(row)

        check.clicked.connect(
            lambda: self._check_choice(lesson, question, group, verdict)
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
        answer.setPlaceholderText("y = ...")
        answer.setClearButtonEnabled(True)
        row.addWidget(answer, 1)

        check = QPushButton("Check")
        check.setProperty("role", "primary")
        check.setCursor(Qt.PointingHandCursor)
        row.addWidget(check)

        hint_button = QPushButton("Hint")
        hint_button.setCursor(Qt.PointingHandCursor)
        hint_button.setEnabled(bool(question.hints))
        row.addWidget(hint_button)

        show = QPushButton("Show me")
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

    def _record(self, bucket: str, key: str, state: str) -> None:
        """Note one answer.

        `bucket` is the lesson's own key for its practice questions, and
        `progress.drill_key(lesson)` for its drills -- a separate bucket, so
        that an unbounded number of generated answers cannot disturb the
        "3 of 5" the practice questions mean.
        """
        self._answered = progress.record(bucket, key, state)
        self._refresh_labels()

    def _check_choice(self, lesson, question, group, verdict: QLabel, *,
                      bucket: str = "", key: str = "") -> None:
        picked = group.checkedId()
        palette = self.palette_obj
        if picked < 0:
            verdict.setStyleSheet(f"color: {palette.text_muted};")
            verdict.setText("pick an option first")
            return

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
        self._record(bucket or lesson.key, key or question.key,
                     progress.State.CORRECT if right else progress.State.ATTEMPTED)

    def _check_solve(self, lesson, question, answer: QLineEdit,
                     verdict: QLabel, *, bucket: str = "",
                     key: str = "") -> None:
        from ..laplace import EXTRA_FUNCTIONS
        from ..symbolic import EquationSpec, check_answer, parse_equation

        palette = self.palette_obj
        try:
            parsed = parse_equation(
                EquationSpec(equations=[question.equation],
                             initial_conditions=question.conditions),
                extra_functions=EXTRA_FUNCTIONS,
            )
        except Exception as exc:                  # a broken question, not a
            verdict.setStyleSheet(f"color: {palette.danger};")   # broken answer
            verdict.setText(f"this question could not be set up: {exc}")
            return

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

        detail = ""
        if result.correct is False and result.residual is not None:
            detail = (f'<br><span style="color:{palette.text_muted};'
                      f'font-size:12px;">what is left over: '
                      f"{result.residual}</span>")
        verdict.setStyleSheet("")
        verdict.setText(f'<span style="color:{colour};">{text}</span>{detail}')
        self._record(bucket or lesson.key, key or question.key, state)

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
        if lesson is not None:
            self.open_tool.emit(lesson.tool)

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
