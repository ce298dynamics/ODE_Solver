"""The main window: sidebar navigation over a stack of screens."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
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
            ("lessons", "Lessons", "Ctrl+1"),
            ("steps", "Solve Step by Step", "Ctrl+2"),
            ("laplace", "Laplace Transforms", "Ctrl+3"),
            ("byhand", "Methods by Hand", "Ctrl+4"),
            ("worked", "Worked Problems", "Ctrl+5"),
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
    """Fixed-width navigation rail: Home, a section switch, then that section."""

    #: Emitted when the user picks a section from the switch.
    section_changed = Signal(str)

    def __init__(self, palette: Palette, parent=None) -> None:
        super().__init__(parent)
        self.setFixedWidth(196)
        self.setStyleSheet(
            f"background: {palette.surface}; border-right: 1px solid {palette.border};"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 18, 12, 14)
        layout.setSpacing(3)

        brand = QLabel("odesuite")
        brand.setStyleSheet(
            f"font-size: 17px; font-weight: 700; color: {palette.accent};"
            f"padding: 0 8px 2px 8px;"
        )
        layout.addWidget(brand)

        tagline = QLabel("ODE solver studio")
        tagline.setProperty("role", "muted")
        tagline.setStyleSheet("font-size: 11px; padding: 0 8px 14px 8px;")
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
        for section, _, group in SECTIONS:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(0, 0, 0, 0)
            page_layout.setSpacing(3)
            for key, label, shortcut in group:
                button = QPushButton(label)
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

        self.status = QLabel("ready")
        self.status.setProperty("role", "muted")
        self.status.setStyleSheet("font-size: 10.5px; padding: 8px 8px 0 8px;")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.show_section(SECTIONS[0][0])

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

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.sidebar = Sidebar(self.palette_obj)
        layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        self._screens: dict[str, QWidget] = {}
        self._build_screens()

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
        self.state.busy_changed.connect(
            lambda busy: self.sidebar.status.setText("solving…" if busy else "ready")
        )
        self.state.result_changed.connect(self._on_result)

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
        from .screens.learn_lessons import LessonsScreen

        lessons = LessonsScreen(self.state, self.palette_obj)
        lessons.open_tool.connect(self.go)
        self._add("lessons", lessons)
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

    def _add(self, key: str, widget: QWidget) -> None:
        self._screens[key] = widget
        self.stack.addWidget(widget)

    def show_section(self, section: str) -> None:
        """Switch the sidebar to a section, opening its first screen."""
        self.sidebar.show_section(section)
        group = next((g for s, _, g in SECTIONS if s == section), None)
        if group:
            self.go(group[0][0])

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
        button = self.sidebar.buttons.get(key)
        if button is not None:
            button.setChecked(True)

    def _open_problem(self, key: str) -> None:
        self.state.set_problem(key)
        lab = self._screens.get("lab")
        if lab is not None and hasattr(lab, "sync"):
            lab.sync()
        self.go("lab")

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
        # Screens hold palette-derived colours, so they are rebuilt wholesale
        # rather than patched piecemeal.
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


def build_application(palette_name: str = "dark"):
    """Create the QApplication and the main window, without showing it."""
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("odesuite")
    app.setOrganizationName("odesuite")
    theme.apply_theme(app, PALETTES[palette_name])
    window = MainWindow(palette_name)
    return app, window
