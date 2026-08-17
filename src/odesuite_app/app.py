"""The main window: sidebar navigation over a stack of screens."""

from __future__ import annotations

from PySide6.QtCore import Qt
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

#: (screen id, sidebar label, keyboard shortcut)
SCREENS = [
    ("home", "Home", "Ctrl+1"),
    ("lab", "Solver Lab", "Ctrl+2"),
    ("portrait", "Phase Portrait", "Ctrl+3"),
    ("stiffness", "Stiffness Explorer", "Ctrl+4"),
    ("race", "Method Race", "Ctrl+5"),
    ("accuracy", "Accuracy Lab", "Ctrl+6"),
]


class _Placeholder(QWidget):
    """Stands in for a screen that has not been built yet.

    Explicit rather than an empty widget: during a phased build it should be
    obvious what is missing and what is merely broken.
    """

    def __init__(self, title: str, note: str, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.addStretch(1)

        heading = QLabel(title)
        heading.setProperty("role", "title")
        heading.setAlignment(Qt.AlignCenter)
        layout.addWidget(heading)

        detail = QLabel(note)
        detail.setProperty("role", "subtitle")
        detail.setAlignment(Qt.AlignCenter)
        detail.setWordWrap(True)
        layout.addWidget(detail)
        layout.addStretch(1)


class Sidebar(QFrame):
    """Fixed-width navigation rail."""

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

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.buttons: dict[str, QPushButton] = {}
        for index, (key, label, shortcut) in enumerate(SCREENS):
            button = QPushButton(label)
            button.setProperty("role", "nav")
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setToolTip(shortcut)
            self.group.addButton(button, index)
            layout.addWidget(button)
            self.buttons[key] = button

        layout.addStretch(1)

        self.theme_button = QPushButton("Light theme")
        self.theme_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.theme_button)

        self.status = QLabel("ready")
        self.status.setProperty("role", "muted")
        self.status.setStyleSheet("font-size: 10.5px; padding: 8px 8px 0 8px;")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)


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

        for index, (key, _, shortcut) in enumerate(SCREENS):
            self.sidebar.buttons[key].clicked.connect(
                lambda _=False, k=key: self.go(k)
            )
            QShortcut(QKeySequence(shortcut), self,
                      activated=lambda k=key: self.go(k))

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
        self._add("lab", LabScreen(self.state, self.palette_obj))
        self._add("portrait", PortraitScreen(self.state, self.palette_obj))
        self._add("stiffness", StiffnessScreen(self.state, self.palette_obj))
        self._add("race", RaceScreen(self.state, self.palette_obj))

        from .screens.accuracy import AccuracyScreen

        self._add("accuracy", AccuracyScreen(self.state, self.palette_obj))

    def _add(self, key: str, widget: QWidget) -> None:
        self._screens[key] = widget
        self.stack.addWidget(widget)

    def go(self, key: str) -> None:
        if key not in self._screens:
            return
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
