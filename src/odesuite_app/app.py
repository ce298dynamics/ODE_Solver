"""The main window: sidebar navigation over a stack of screens."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QSettings, Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from . import theme
from .state import SessionState
from .theme import PALETTES, Palette

__all__ = ["MainWindow", "build_application"]

#: (section id, sidebar label, [(screen id, label, shortcut), ...])
#:
#: Two audiences, one app. The Learning Hub is about *solving ODEs* -- the
#: techniques a first course teaches, and the arithmetic behind the methods.
#: Solver Studio is about *the solvers themselves* -- adaptivity, stiffness,
#: accuracy, the comparisons between methods.
#:
#: The split is presentation only. Both sections drive the same `SessionState`
#: and select from the same catalogue by key, which is what lets a problem --
#: including one the user typed -- appear on either side without either knowing
#: about the other.
SECTIONS = [
    (
        "learn",
        "Learning Hub",
        [
            ("course", "Course Map", "Ctrl+1"),
            ("lessons", "Lessons", "Ctrl+2"),
            ("quiz", "Quiz & Exams", "Ctrl+3"),
            ("glossary", "Glossary", "Ctrl+4"),
            ("steps", "Solve Step by Step", "Ctrl+5"),
            ("laplace", "Laplace Transforms", "Ctrl+6"),
            ("byhand", "Methods by Hand", "Ctrl+7"),
            ("worked", "Worked Problems", "Ctrl+8"),
            ("print", "Print & Revise", "Ctrl+9"),
        ],
    ),
    (
        "studio",
        "Solver Studio",
        [
            ("lab", "Solver Lab", "Ctrl+Shift+1"),
            ("portrait", "Phase Portrait", "Ctrl+Shift+2"),
            ("stiffness", "Stiffness Explorer", "Ctrl+Shift+3"),
            ("race", "Method Race", "Ctrl+Shift+4"),
            ("accuracy", "Accuracy Lab", "Ctrl+Shift+5"),
        ],
    ),
]

#: Headings the sidebar draws above a screen, splitting a section into parts.
#:
#: The Learning Hub has nine screens, and listed as equals they were nine
#: competing ways in. Four of them are the course: the map, the lessons, the
#: check-ups and the glossary they lean on. The other five are tools a lesson
#: opens when it needs one. Saying so is what makes the course the obvious
#: path through the app rather than one option among nine.
SUBHEADINGS = {"course": "Study", "steps": "Tools"}

#: Shortcuts number each section from 1 and the modifier picks the section:
#: `Ctrl+N` for the Learning Hub, `Ctrl+Shift+N` for Solver Studio. Ten screens
#: plus Home no longer fit a single run of digits, and a flat run had the odd
#: effect that `Ctrl+5` jumped out of the section you were in. Every binding is
#: still globally unique, which is the property that matters: a shortcut never
#: means two different screens.
#:
#: Home sits above the split and belongs to neither section.
HOME = ("home", "Home", "Ctrl+0")

#: Flattened, in nav order, for the places that just want every screen.
SCREENS = [HOME] + [entry for _, _, group in SECTIONS for entry in group]

#: screen id -> section id, for `MainWindow.go`.
SECTION_OF = {
    key: section for section, _, group in SECTIONS for key, _, _ in group
}


class Sidebar(QFrame):
    """Fixed-width navigation rail: Home, a section switch, then that section.

    It folds to a thin strip (Ctrl+B) for reading: a lesson wants the width
    more than the menu does, and the shortcuts still reach every screen.
    """

    #: Emitted when the user picks a section from the switch.
    section_changed = Signal(str)
    #: Emitted when the fold button or the strip is pressed: the reader asking.
    fold_requested = Signal(bool)

    WIDTH = 196
    COLLAPSED_WIDTH = 30

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.setFixedWidth(self.WIDTH)
        # The border on the rail alone: a bare declaration reaches every child,
        # and drew a short rule beside each button and label.
        self.setObjectName("sidebar")
        self.setStyleSheet(
            f"* {{ background: {palette.surface}; }}"
            f"QFrame#sidebar {{ border-right: 1px solid {palette.border}; }}"
        )
        self._collapsed = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        self._body = QWidget()
        outer.addWidget(self._body, 1)

        quiet = theme.scaled(
            f"QPushButton {{ background: transparent; border: none;"
            f" color: {palette.text_muted}; font-size: 12px; padding: 2px 4px; }}"
            f"QPushButton:hover {{ color: {palette.accent}; }}"
        )
        # The whole strip is the button, as in `CollapsibleRail`.
        self._strip = QPushButton("›\n\n" + "\n".join("Menu"))
        self._strip.setAccessibleName("show menu")
        self._strip.setToolTip("Show the menu (Ctrl+B)")
        self._strip.setCursor(Qt.PointingHandCursor)
        self._strip.setStyleSheet(quiet)
        self._strip.clicked.connect(lambda: self.fold_requested.emit(False))
        self._strip.setVisible(False)
        outer.addWidget(self._strip, 0, Qt.AlignTop)
        outer.addStretch(0)

        layout = QVBoxLayout(self._body)
        layout.setContentsMargins(12, 18, 12, 14)
        layout.setSpacing(3)

        top = QHBoxLayout()
        top.setSpacing(0)
        brand = QLabel("odesuite")
        brand.setStyleSheet(
            theme.scaled(f"font-size: 17px; font-weight: 700; color: {palette.accent};"
                         f"padding: 0 8px 2px 8px;")
        )
        top.addWidget(brand, 1)
        self.fold_button = QPushButton("‹")
        self.fold_button.setAccessibleName("hide menu")
        self.fold_button.setToolTip("Fold the menu away (Ctrl+B)")
        self.fold_button.setCursor(Qt.PointingHandCursor)
        self.fold_button.setStyleSheet(quiet)
        self.fold_button.clicked.connect(lambda: self.fold_requested.emit(True))
        top.addWidget(self.fold_button)
        layout.addLayout(top)

        tagline = QLabel("ODE solver studio")
        tagline.setProperty("role", "muted")
        tagline.setStyleSheet(theme.scaled("font-size: 11px; padding: 0 8px 14px 8px;"))
        layout.addWidget(tagline)

        self.buttons: dict[str, QPushButton] = {}

        # Home is above the split: it belongs to neither section and is how you
        # get back to choosing one.
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        home_button = QPushButton(HOME[1])
        home_button.setProperty("role", "nav")
        home_button.setCheckable(True)
        home_button.setCursor(Qt.PointingHandCursor)
        home_button.setToolTip(HOME[2])
        self.group.addButton(home_button)
        layout.addWidget(home_button)
        self.buttons[HOME[0]] = home_button

        layout.addSpacing(10)

        # The section switch. Segmented rather than a combo box: there are two
        # of them and both should be visible without a click.
        self.section_group = QButtonGroup(self)
        self.section_group.setExclusive(True)
        self.section_buttons: dict[str, QPushButton] = {}
        for section, label, _ in SECTIONS:
            button = QPushButton(label)
            button.setProperty("role", "section")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            self.section_group.addButton(button)
            layout.addWidget(button)
            self.section_buttons[section] = button
            button.clicked.connect(
                lambda _=False, s=section: self.section_changed.emit(s)
            )

        layout.addSpacing(6)

        # One page of screen buttons per section, only one of which is visible.
        self.section_pages: dict[str, QWidget] = {}
        self.subheadings: dict[str, QLabel] = {}
        for section, _, group in SECTIONS:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(0, 0, 0, 0)
            page_layout.setSpacing(3)
            for key, label, shortcut in group:
                if key in SUBHEADINGS:
                    heading = QLabel(SUBHEADINGS[key].upper())
                    heading.setProperty("role", "muted")
                    heading.setStyleSheet(theme.scaled(
                        "font-size: 10.5px; font-weight: 600; letter-spacing: 1px;"
                        f"padding: {'8' if page_layout.count() else '2'}px 8px 2px 8px;"
                    ))
                    page_layout.addWidget(heading)
                    self.subheadings[key] = heading
                button = QPushButton(label.replace("&", "&&"))
                button.setProperty("role", "nav")
                button.setCheckable(True)
                button.setCursor(Qt.PointingHandCursor)
                button.setToolTip(shortcut)
                self.group.addButton(button)
                page_layout.addWidget(button)
                self.buttons[key] = button
            layout.addWidget(page)
            self.section_pages[section] = page

        layout.addStretch(1)

        self.theme_button = QPushButton("Light theme")
        self.theme_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.theme_button)

        # REL-04: the one way a failure here can reach the author, and only
        # when the user chooses to paste it somewhere.
        self.diagnostics_button = QPushButton("Copy diagnostics")
        self.diagnostics_button.setCursor(Qt.PointingHandCursor)
        self.diagnostics_button.setToolTip(
            "Copy versions, platform and the last few failed solves to the "
            "clipboard, for a bug report. Nothing is sent anywhere."
        )
        layout.addWidget(self.diagnostics_button)

        self.status = QLabel("ready")
        self.status.setProperty("role", "muted")
        self.status.setStyleSheet(theme.scaled("font-size: 10.5px; padding: 8px 8px 0 8px;"))
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.show_section(SECTIONS[0][0])

    def is_collapsed(self) -> bool:
        return self._collapsed

    def set_collapsed(self, collapsed: bool) -> None:
        """Fold to the strip or open again. Only width and visibility change,
        so the buttons inside keep their checked state while hidden."""
        self._collapsed = bool(collapsed)
        self._body.setVisible(not self._collapsed)
        self._strip.setVisible(self._collapsed)
        self.setFixedWidth(self.COLLAPSED_WIDTH if self._collapsed else self.WIDTH)

    def show_section(self, section: str) -> None:
        """Reveal one section's screen buttons and check its switch button."""
        for name, page in self.section_pages.items():
            page.setVisible(name == section)
        button = self.section_buttons.get(section)
        if button is not None:
            button.setChecked(True)


class MainWindow(QWidget):
    def __init__(self, palette_name: str = "dark") -> None:
        super().__init__()
        self.palette_name = palette_name
        self.palette_obj = PALETTES[palette_name]
        self.state = SessionState(self)

        self.setWindowTitle("odesuite — ODE solver studio")
        self.resize(1440, 900)
        self.setMinimumSize(1080, 680)
        self._settings = QSettings("odesuite", "odesuite")
        self._restore_geometry()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar(self.palette_obj)
        layout.addWidget(self.sidebar)
        #: The reader's choice for the menu; reading mode folds it without
        #: changing this, so leaving reading mode puts back what was chosen.
        self._sidebar_wanted = not self._flag("layout/sidebar_collapsed")
        self._reading = False
        self.sidebar.set_collapsed(not self._sidebar_wanted)
        self.sidebar.fold_requested.connect(
            lambda folded: self.toggle_sidebar(not folded))
        QShortcut(QKeySequence("Ctrl+B"), self,
                  activated=lambda: self.toggle_sidebar())

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self._screens: dict[str, QWidget] = {}
        self._build_screens()
        from . import mathrender
        from .widgets.mathlabel import render_pool

        render_pool().start(mathrender.warm_up)

        for key, _, shortcut in SCREENS:
            self.sidebar.buttons[key].clicked.connect(
                lambda _=False, k=key: self.go(k)
            )
            # Shortcuts are unique across the whole app rather than restarting
            # per section, so one never means two different screens.
            QShortcut(QKeySequence(shortcut), self,
                      activated=lambda k=key: self.go(k))

        self.sidebar.section_changed.connect(self.show_section)

        self.sidebar.theme_button.clicked.connect(self.toggle_theme)
        self.sidebar.diagnostics_button.clicked.connect(self.copy_diagnostics)
        self.state.busy_changed.connect(
            lambda busy: self.sidebar.status.setText("solving…" if busy else "ready")
        )
        self.state.result_changed.connect(self._on_result)

        #: What `changeEvent` compares against. Qt sends an application font
        #: change for reasons other than the text scale -- a palette swap is
        #: one -- and rebuilding every screen for each of them would be a
        #: visible stutter for no change on screen.
        self._text_scale = theme.text_scale()

        self.go("home")

    # -- screens ---------------------------------------------------------

    def _build_screens(self) -> None:
        from .screens.home import HomeScreen
        from .screens.lab import LabScreen
        from .screens.portrait import PortraitScreen
        from .screens.race import RaceScreen
        from .screens.stiffness import StiffnessScreen

        home = HomeScreen(self.palette_obj)
        home.problem_chosen.connect(self._open_problem)
        home.showcase_chosen.connect(self.go)
        self._add("home", home)

        # The Learning Hub.
        from .screens.learn_course import CourseScreen
        from .screens.learn_lessons import LessonsScreen

        lessons = LessonsScreen(self.state, self.palette_obj)
        lessons.open_tool.connect(self._open_tool)
        lessons.open_term.connect(self._open_term)
        # Held here, not by the screen: a theme or text-scale change rebuilds
        # every screen, and the columns must come back the way they were.
        lessons.set_rails(course=not self._flag("lessons/course_collapsed"),
                          workspace=not self._flag("lessons/workspace_collapsed"))
        if self._reading:
            lessons.reading_mode(True)
        lessons.rails_changed.connect(
            lambda name, folded: self._settings.setValue(
                f"lessons/{name}_collapsed", bool(folded)))
        lessons.reading_changed.connect(self._on_reading)
        self._add("lessons", lessons)

        course = CourseScreen(self.state, self.palette_obj)
        course.open_lesson.connect(self._open_lesson)
        self._add("course", course)

        from .screens.learn_quiz import QuizScreen

        quiz = QuizScreen(self.state, self.palette_obj)
        quiz.open_lesson.connect(self._open_lesson)
        self._add("quiz", quiz)

        from .screens.learn_print import PrintScreen

        self._add("print", PrintScreen(self.state, self.palette_obj))
        from .screens.learn_glossary import GlossaryScreen

        glossary = GlossaryScreen(self.state, self.palette_obj)
        glossary.open_lesson.connect(self._open_lesson)
        self._add("glossary", glossary)
        from .screens.learn_steps import StepsScreen

        self._add("steps", StepsScreen(self.state, self.palette_obj))
        from .screens.learn_laplace import LaplaceScreen

        self._add("laplace", LaplaceScreen(self.state, self.palette_obj))
        from .screens.learn_byhand import ByHandScreen

        self._add("byhand", ByHandScreen(self.state, self.palette_obj))
        from .screens.learn_problems import WorkedProblemsScreen

        worked = WorkedProblemsScreen(self.state, self.palette_obj)
        worked.open_in_lab.connect(self._open_problem)
        self._add("worked", worked)
        self._add("lab", LabScreen(self.state, self.palette_obj))
        self._add("portrait", PortraitScreen(self.state, self.palette_obj))
        self._add("stiffness", StiffnessScreen(self.state, self.palette_obj))
        self._add("race", RaceScreen(self.state, self.palette_obj))

        from .screens.accuracy import AccuracyScreen

        self._add("accuracy", AccuracyScreen(self.state, self.palette_obj))

    # -- remembering where you were --------------------------------------
    #
    # Small, and paid back every single time the application opens. Reopening
    # on Home at a default size is a tax collected constantly, and the state
    # worth keeping is two values.
    #
    # `QSettings` rather than the progress file: this is preference, not
    # achievement. A geometry has no business in a file the user may export to
    # another machine with a different screen, and the progress file is
    # deliberately legible and hand-editable, which window pixels are not.

    def _restore_geometry(self) -> None:
        saved = self._settings.value("window/geometry")
        if saved is not None:
            self.restoreGeometry(saved)

    def _flag(self, key: str) -> bool:
        """A saved yes/no. The INI and registry backends hand a bool back as
        the string "true" or "false", and `bool("false")` is True."""
        value = self._settings.value(key, False)
        if isinstance(value, str):
            return value.lower() == "true"
        return bool(value)

    def toggle_sidebar(self, show: bool | None = None) -> None:
        """Fold or open the menu, as the reader asking for it (Ctrl+B)."""
        show = self.sidebar.is_collapsed() if show is None else bool(show)
        self._sidebar_wanted = show
        self._settings.setValue("layout/sidebar_collapsed", not show)
        self.sidebar.set_collapsed(not show)
        if show and self._reading:
            # Opening the menu is leaving reading mode.
            lessons = self._screens.get("lessons")
            if lessons is not None and hasattr(lessons, "reading_mode"):
                lessons.reading_mode(False)

    def _on_reading(self, on: bool) -> None:
        """Reading mode folds the menu too, without it being remembered."""
        self._reading = bool(on)
        self.sidebar.set_collapsed(on or not self._sidebar_wanted)

    def current_screen(self) -> str:
        """The key of the screen on show, or "" if it cannot be told."""
        showing = self.stack.currentWidget()
        return next((key for key, widget in self._screens.items()
                     if widget is showing), "")

    def _remember(self) -> None:
        self._settings.setValue("window/geometry", self.saveGeometry())
        key = self.current_screen()
        if key:
            self._settings.setValue("window/screen", key)

        # And the rest of what was on screen: problem, method, tolerances,
        # parameter values. `QSettings` holds the window; this holds the work.
        # Never allowed to fail -- `session.save` returns None rather than
        # raising, for the same reason `progress.py` does: losing a session is
        # a small harm and refusing to close is a large one.
        from . import session

        session.save(self.state, key, equation=self.typed_equation())

    def typed_equation(self):
        """The `EquationSpec` the Solver Lab last parsed, or None.

        Asked of the Lab rather than of `catalog`, which keeps only the built
        entry -- and the text the user wrote cannot be recovered from that.
        """
        lab = self._screens.get("lab")
        return getattr(getattr(lab, "_parsed", None), "spec", None)

    def restore_session(self) -> str:
        """Reopen the problem, method and tolerances last used.

        Returns the screen the session names, or "". Separate from
        `remembered_screen` and returned rather than applied for the same
        reason: `cli.py` owns the precedence, because only it knows whether an
        explicit `--problem` or `--screen` was given.
        """
        from . import session

        stored = session.load()
        return session.apply(self.state, stored) if stored else ""

    def remembered_screen(self) -> str:
        """The screen this window was last closed on, or "" if unknown.

        Returned rather than applied, because `cli.py` owns the decision: an
        explicit `--screen` or `--problem` must win over what was remembered,
        and only the caller knows whether one was given.
        """
        key = self._settings.value("window/screen", "")
        return key if isinstance(key, str) and key in self._screens else ""

    def closeEvent(self, event) -> None:               # noqa: N802
        self._remember()
        super().closeEvent(event)

    def _add(self, key: str, widget: QWidget) -> None:
        self._screens[key] = widget
        self.stack.addWidget(widget)

    def show_section(self, section: str) -> None:
        """Switch the sidebar to a section, opening its first screen."""
        self.sidebar.show_section(section)
        group = next((g for s, _, g in SECTIONS if s == section), None)
        if group:
            self.go(group[0][0])

    def copy_diagnostics(self) -> str:
        """Put the diagnostics report on the clipboard, and return it."""
        from PySide6.QtGui import QGuiApplication

        from . import diagnostics

        text = diagnostics.report()
        QGuiApplication.clipboard().setText(text)
        self.sidebar.status.setText("diagnostics copied to the clipboard")
        return text

    def go(self, key: str) -> None:
        """Open a screen by key, switching section if it lives in the other one.

        Callers pass a bare screen key and always have -- `cli.py --screen`,
        the Home screen's showcase tiles, and the tests. Resolving the section
        here rather than at every call site is what keeps that true.
        """
        if key not in self._screens:
            return
        section = SECTION_OF.get(key)
        if section is not None:
            self.sidebar.show_section(section)
        screen = self._screens[key]
        # An equation typed in the Solver Lab is registered long after the other
        # screens were built, so their problem lists are stale until asked. This
        # is the one place every screen becomes visible, which makes it the one
        # place worth refreshing them.
        if hasattr(screen, "refresh_problems"):
            screen.refresh_problems()
        self.stack.setCurrentWidget(screen)
        # A screen that holds its work while hidden starts it here as well as
        # in its `showEvent`: a window that is never shown -- the tests, the
        # screenshot scripts -- never sends one.
        if hasattr(screen, "catch_up"):
            screen.catch_up()
        button = self.sidebar.buttons.get(key)
        if button is not None:
            button.setChecked(True)

    def _open_problem(self, key: str) -> None:
        self.state.set_problem(key)
        lab = self._screens.get("lab")
        if lab is not None and hasattr(lab, "sync"):
            lab.sync()
        self.go("lab")

    def _open_tool(self, key: str, equation: str = "",
                   conditions: str = "") -> None:
        """Open the screen a lesson teaches, on that lesson's own example.

        The screen is asked whether it can take an equation rather than
        checked against a list of the ones that can. Two of the four tools a
        lesson links to are driven by the catalogue and have no box to type
        into; they simply open, as they always did.
        """
        screen = self._screens.get(key)
        if screen is not None and equation and hasattr(screen, "load_equation"):
            # Before `go`, so the screen is already working on the right
            # equation by the time it becomes visible.
            screen.load_equation(equation, conditions)
        self.go(key)

    def _open_term(self, name: str) -> None:
        """Open the glossary at one term, for a link in a lesson's chapter."""
        glossary = self._screens.get("glossary")
        if glossary is not None and hasattr(glossary, "select_term"):
            glossary.select_term(name)
        self.go("glossary")

    def _open_lesson(self, key: str) -> None:
        """Open `Lessons` at one lesson, for the Course Map's rows."""
        lessons = self._screens.get("lessons")
        if lessons is not None and hasattr(lessons, "select"):
            lessons.select(key)
        self.go("lessons")

    def _on_result(self, result) -> None:
        if result.error:
            self.sidebar.status.setText(result.error[:70])
        elif result.solution is not None:
            self.sidebar.status.setText(
                f"{result.solution.stats.naccepted} steps · "
                f"{result.wall_time * 1e3:.0f} ms"
            )

    # -- theming ---------------------------------------------------------

    def toggle_theme(self) -> None:
        self.palette_name = "light" if self.palette_name == "dark" else "dark"
        self.palette_obj = PALETTES[self.palette_name]
        theme.apply_theme(QApplication.instance(), self.palette_obj)
        self.sidebar.theme_button.setText(
            "Dark theme" if self.palette_name == "light" else "Light theme"
        )
        self.rebuild_screens()

    def rebuild_screens(self) -> None:
        """Throw every screen away and build it again, staying where we are.

        Screens bake palette-derived colours and scaled font sizes into their
        widgets at construction, so the two things that invalidate all of them
        -- a theme switch and a change in the reader's text scale -- are both
        served by rebuilding wholesale rather than by patching piecemeal.
        """
        current = self.stack.currentWidget()
        current_key = next(
            (k for k, w in self._screens.items() if w is current), "home"
        )
        while self.stack.count():
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()
        self._screens.clear()
        self._build_screens()
        self.go(current_key)

    def changeEvent(self, event) -> None:
        """Follow the operating system's text scale while running.

        Raising it mid-session reaches Qt as an application font change. The
        style sheet is written in pixels against the default font, so it has
        to be re-generated at the new scale and the screens rebuilt to pick up
        the inline sizes -- otherwise the reader gets a window that grew its
        chrome and kept its content the size it was.
        """
        super().changeEvent(event)
        # Both events, for the reason `MathLabel._FONT_EVENTS` records: which
        # of the two Qt delivers depends on the widget, and the scale
        # comparison below is what makes listening for both harmless.
        if event.type() not in (QEvent.ApplicationFontChange,
                                QEvent.FontChange):
            return
        scale = theme.text_scale()
        if abs(scale - self._text_scale) < 0.005:
            return
        self._text_scale = scale
        theme.apply_theme(QApplication.instance(), self.palette_obj)
        self.rebuild_screens()


def build_application(palette_name: str = "dark"):
    """Create the QApplication and the main window, without showing it."""
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("odesuite")
    app.setOrganizationName("odesuite")
    theme.apply_theme(app, PALETTES[palette_name])
    # Python's collector runs on whichever thread happens to allocate when a
    # threshold is crossed, and the portrait, the solvers and the typesetter
    # all allocate on worker threads. A cycle holding a Qt object collected
    # there destroys that object off the GUI thread, which Qt does not
    # support. pyqtgraph documents the hazard and ships this remedy: automatic
    # collection off, and a collection on a timer here, on the GUI thread.
    # Kept on the app so it lives as long. On the Linux CI runners every run
    # without this (and the suite's equivalent in conftest) hung or aborted;
    # every run with it under PySide6 6.11 did neither.
    from pyqtgraph.util.garbage_collector import GarbageCollector

    if not hasattr(app, "_odesuite_gc"):
        app._odesuite_gc = GarbageCollector(interval=1.0)
    window = MainWindow(palette_name)
    return app, window
