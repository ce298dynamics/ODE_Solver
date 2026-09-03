"""The course map: every unit, every lesson, and how far through you are.

`Lessons` shows one lesson at a time and is where the work happens. This is the
view from above — what the course contains, what you have done, and what to do
next. With thirty-odd lessons a single scrolling list stops being navigable, and
the shape of the subject is itself worth seeing: first-order techniques, then
models and numerics, then second-order, then the transform.

Nothing here is computed that is not shown. A bar means *questions answered
correctly out of questions asked*, and that number comes from the same
`progress` file the Lessons screen writes, read once and passed down rather than
re-read per row.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import lessons as content
from .. import progress
from ..theme import Palette
from ..widgets.controls import add_heading, control_panel

__all__ = ["CourseScreen"]


class CourseScreen(QWidget):
    """Units, lessons and progress, with a way into each."""

    #: Asks the window to open `Lessons` at a particular lesson.
    open_lesson = Signal(str)

    def __init__(self, state, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.state = state
        self.palette_obj = palette
        self._answered = progress.load()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)
        layout.addWidget(self._build_controls())
        layout.addWidget(self._build_body(), 1)
        self.refresh()

    # -- construction ----------------------------------------------------

    def _build_controls(self) -> QWidget:
        panel, layout = control_panel(258)

        add_heading(layout, "Where you are")

        self.overall_label = QLabel("")
        self.overall_label.setProperty("role", "title")
        layout.addWidget(self.overall_label)

        self.overall_bar = QProgressBar()
        self.overall_bar.setTextVisible(False)
        self.overall_bar.setFixedHeight(8)
        layout.addWidget(self.overall_bar)

        self.overall_detail = QLabel("")
        self.overall_detail.setProperty("role", "muted")
        self.overall_detail.setWordWrap(True)
        layout.addWidget(self.overall_detail)

        self.continue_button = QPushButton("Continue")
        self.continue_button.setProperty("role", "primary")
        self.continue_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.continue_button)

        self.continue_detail = QLabel("")
        self.continue_detail.setProperty("role", "muted")
        self.continue_detail.setWordWrap(True)
        layout.addWidget(self.continue_detail)

        add_heading(layout, "Review", space_above=10)
        self.review_label = QLabel("")
        self.review_label.setProperty("role", "muted")
        self.review_label.setWordWrap(True)
        layout.addWidget(self.review_label)

        layout.addStretch(1)

        note = QLabel(
            "A unit appears here once it has lessons. Nothing is locked — the "
            "prerequisites are advice about what makes a topic easier, not a "
            "gate."
        )
        note.setProperty("role", "muted")
        note.setWordWrap(True)
        layout.addWidget(note)

        self.continue_button.clicked.connect(self._continue)
        return panel

    def _build_body(self) -> QWidget:
        frame = QFrame()
        frame.setProperty("role", "panel")
        outer = QVBoxLayout(frame)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll)

        holder = QWidget()
        scroll.setWidget(holder)
        across = QHBoxLayout(holder)
        across.setContentsMargins(0, 0, 0, 0)

        self._page = QWidget()
        self._page.setMaximumWidth(940)
        across.addWidget(self._page, 1)
        across.addStretch(0)

        self._layout = QVBoxLayout(self._page)
        self._layout.setContentsMargins(24, 20, 24, 24)
        self._layout.setSpacing(14)
        return frame

    # -- content ---------------------------------------------------------

    def refresh(self) -> None:
        """Rebuild from the progress file. Cheap — no mathematics happens here."""
        self._answered = progress.load()
        self._clear()

        title = QLabel("Ordinary differential equations")
        title.setProperty("role", "title")
        self._layout.addWidget(title)

        blurb = QLabel(
            "The techniques a first course teaches, in the order it teaches "
            "them. Each lesson explains the method, works examples through the "
            "narrator that powers its tool, and asks you to do it."
        )
        blurb.setProperty("role", "subtitle")
        blurb.setWordWrap(True)
        self._layout.addWidget(blurb)

        for unit in content.UNITS:
            self._layout.addWidget(self._unit_card(unit))
        self._layout.addStretch(1)
        self._refresh_summary()

    def _unit_card(self, unit) -> QWidget:
        palette = self.palette_obj
        frame = QFrame()
        frame.setProperty("role", "panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 15, 18, 16)
        layout.setSpacing(10)

        head = QHBoxLayout()
        heading = QLabel(unit.title)
        heading.setProperty("role", "heading")
        heading.setWordWrap(True)
        head.addWidget(heading, 1)
        reference = QLabel(unit.reference)
        reference.setProperty("role", "muted")
        head.addWidget(reference, 0, Qt.AlignRight | Qt.AlignTop)
        layout.addLayout(head)

        summary = QLabel(unit.summary)
        summary.setProperty("role", "muted")
        summary.setWordWrap(True)
        layout.addWidget(summary)

        # The unit's own standing, above its lessons. Questions and drills
        # together: a unit whose questions are all ticked and whose drills are
        # untouched is not finished in any sense the word is usually meant,
        # and a bar that said it was would be lying by omission.
        standing = progress.unit_progress(unit, self._answered)
        ring = QProgressBar()
        ring.setTextVisible(False)
        ring.setFixedHeight(6)
        ring.setRange(0, 1000)
        ring.setValue(int(standing.fraction * 1000))
        layout.addWidget(ring)

        tally = QLabel(
            f"{standing.answered} of {standing.questions} questions"
            + (f" · {standing.mastered} of {standing.drills} drills mastered"
               if standing.drills else "")
            + (f" · {standing.finished} of {standing.lessons} lessons finished"
               if standing.finished else "")
        )
        tally.setProperty("role", "muted")
        tally.setWordWrap(True)
        layout.addWidget(tally)

        for lesson in unit.lessons:
            layout.addWidget(self._lesson_row(lesson, palette))
        return frame

    def _lesson_row(self, lesson, palette: Palette) -> QWidget:
        done, total = progress.counts(lesson.key, len(lesson.questions),
                                      self._answered)

        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(10)

        name = QLabel(lesson.title)
        name.setWordWrap(True)
        layout.addWidget(name, 1)

        bar = QProgressBar()
        bar.setTextVisible(False)
        bar.setFixedSize(110, 8)
        bar.setRange(0, max(total, 1))
        bar.setValue(done)
        layout.addWidget(bar, 0)

        tally = QLabel(f"{done}/{total}")
        tally.setProperty("role", "muted")
        tally.setFixedWidth(38)
        tally.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if done and done == total:
            tally.setStyleSheet(f"color: {palette.success};")
        layout.addWidget(tally, 0)

        # Drills are counted separately from the practice questions, and shown
        # separately: one number is out of a fixed denominator and the other is
        # a streak that can go back down.
        drilled, drillable = progress.drills(lesson.key, lesson.templates,
                                             self._answered)
        drill = QLabel(f"{drilled}/{drillable} drills" if drillable else "")
        drill.setProperty("role", "muted")
        drill.setFixedWidth(72)
        drill.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        if drillable and drilled == drillable:
            drill.setStyleSheet(f"color: {palette.success};")
        layout.addWidget(drill, 0)

        button = QPushButton("Open")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(lambda _=False, k=lesson.key:
                               self.open_lesson.emit(k))
        layout.addWidget(button, 0)
        return row

    def _refresh_summary(self) -> None:
        done = total = 0
        for lesson in content.LESSONS:
            right, asked = progress.counts(lesson.key, len(lesson.questions),
                                           self._answered)
            done += right
            total += asked

        self.overall_label.setText(f"{done} of {total}")
        self.overall_bar.setRange(0, max(total, 1))
        self.overall_bar.setValue(done)
        mastered = drillable = 0
        for lesson in content.LESSONS:
            one, many = progress.drills(lesson.key, lesson.templates,
                                        self._answered)
            mastered += one
            drillable += many
        self.overall_detail.setText(
            f"questions answered correctly, across "
            f"{len(content.LESSONS)} lessons in {len(content.UNITS)} units."
            + (f"  {mastered} of {drillable} drills mastered."
               if drillable else "")
        )
        nxt = self._next_lesson()
        if nxt is None:
            self.continue_button.setEnabled(False)
            self.continue_detail.setText("Every question is answered.")
        else:
            self.continue_button.setEnabled(True)
            self.continue_detail.setText(f"Next: {nxt.title}")

        self._refresh_review()

    def _refresh_review(self) -> None:
        """What is worth going back to, weakest first.

        Only lessons already started. One never opened is not weak, it is
        simply next -- listing it here would turn "what to review" into a
        second table of contents, which the unit cards below already are.
        """
        lines = []
        weak = progress.weakest(content.UNITS, self._answered)
        if weak:
            names = ", ".join(lesson.title for lesson, _ in weak)
            lines.append(f"Worth another look: {names}")

        # Ranked by score, `weakest` can never surface a lesson finished in
        # July and untouched since -- it scores perfectly. That is exactly what
        # a course wants brought back, so it is asked for separately.
        old_now = progress.stale(content.UNITS, self._answered)
        if old_now:
            names = ", ".join(
                f"{lesson.title} ({days} days ago)"
                for lesson, _unit, days in old_now
            )
            lines.append(f"Not seen in a while: {names}")

        self.review_label.setText(
            "\n".join(lines) if lines else
            "Nothing to review yet — answer a few questions and the weakest "
            "lessons will appear here."
        )

    def _next_lesson(self):
        """The first lesson with a question left, in course order.

        Deliberately the *first* rather than the least complete: this course
        has an order, and the honest answer to "what next" is the earliest
        thing not yet finished.
        """
        for lesson in content.LESSONS:
            done, total = progress.counts(lesson.key, len(lesson.questions),
                                          self._answered)
            if done < total:
                return lesson
        return None

    def _continue(self) -> None:
        lesson = self._next_lesson()
        if lesson is not None:
            self.open_lesson.emit(lesson.key)

    def _clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    # -- the window's hooks ----------------------------------------------

    def refresh_problems(self) -> None:
        """`MainWindow.go` calls this on every screen it shows.

        There are no problem pickers here, but progress may have changed on the
        Lessons screen since this one was last visible, and this is the one
        place it becomes visible again.
        """
        self.refresh()

    def set_palette_colours(self, palette: Palette) -> None:
        self.palette_obj = palette
