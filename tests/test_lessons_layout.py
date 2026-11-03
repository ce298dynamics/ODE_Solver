"""The Lessons screen's columns: the course, the text, and the answers.

The text used to be the narrowest of the four columns on its own page. These
hold the arrangement that fixed it: both sides fold away, the answer apparatus
lives beside the question rather than inside it, reading mode gives the whole
window to the text, and the window remembers what the reader chose.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def store(tmp_path, monkeypatch):
    from odesuite_app import progress

    monkeypatch.setattr(progress, "directory", lambda: tmp_path / "odesuite")
    return progress


@pytest.fixture()
def screen(qapp, store):
    from PySide6.QtCore import QThreadPool

    from odesuite_app.screens.learn_lessons import LessonsScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    made = LessonsScreen(SessionState(), PALETTES["dark"])
    made.resize(1500, 950)
    qapp.processEvents()
    yield made
    made.deleteLater()
    QThreadPool.globalInstance().clear()


@pytest.fixture()
def scratch_settings(tmp_path, monkeypatch):
    """QSettings in a scratch file, never the developer's own registry."""
    from PySide6.QtCore import QSettings

    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, str(tmp_path))
    monkeypatch.setattr(
        "odesuite_app.app.QSettings",
        lambda *a, **k: QSettings(QSettings.IniFormat, QSettings.UserScope,
                                  "odesuite-test", "odesuite-test"),
    )
    yield tmp_path


def _open(screen, qapp, key: str, segment: str = "Practice"):
    screen.select(key)
    screen._choose_segment(segment)
    qapp.processEvents()
    return screen.current_lesson()


# ---------------------------------------------------------------------------
# The rail itself
# ---------------------------------------------------------------------------


def test_a_rail_folds_to_a_strip_and_says_so(qapp):
    from PySide6.QtWidgets import QLabel

    from odesuite_app.theme import PALETTES
    from odesuite_app.widgets.collapsible import CollapsibleRail

    rail = CollapsibleRail(QLabel("inside"), "Course", "left", 250,
                           PALETTES["dark"])
    every, asked = [], []
    rail.collapsed_changed.connect(every.append)
    rail.user_toggled.connect(asked.append)

    assert rail.width() == 250 and not rail.is_collapsed()
    rail.toggle()
    assert rail.is_collapsed()
    assert rail.maximumWidth() == CollapsibleRail.COLLAPSED_WIDTH
    rail.set_collapsed(False)
    assert rail.maximumWidth() == 250

    assert every == [True, False]
    assert asked == [True], "only the toggle was somebody asking"
    rail.deleteLater()


def test_every_fold_control_has_a_name(qapp):
    from PySide6.QtWidgets import QLabel

    from odesuite_app.theme import PALETTES
    from odesuite_app.widgets.collapsible import CollapsibleRail

    rail = CollapsibleRail(QLabel("inside"), "Answers", "right", 300,
                           PALETTES["dark"])
    assert rail.collapse_button.accessibleName() == "hide answers"
    assert rail._strip.accessibleName() == "show answers"
    rail.deleteLater()


# ---------------------------------------------------------------------------
# The screen's columns
# ---------------------------------------------------------------------------


def test_the_answer_column_folds_where_there_is_nothing_to_answer(screen, qapp):
    _open(screen, qapp, "separable", "Learn")
    assert screen.workspace_rail.is_collapsed()

    _open(screen, qapp, "separable", "Practice")
    assert not screen.workspace_rail.is_collapsed()


def test_folding_by_hand_is_reported_and_kept(screen, qapp):
    said = []
    screen.rails_changed.connect(lambda name, folded: said.append((name, folded)))
    _open(screen, qapp, "separable")

    screen.toggle_workspace()
    assert screen.workspace_rail.is_collapsed()
    _open(screen, qapp, "separable", "Drill")
    assert screen.workspace_rail.is_collapsed(), (
        "a folded answer column stays folded on the next page"
    )
    screen.toggle_course()
    assert said == [("workspace", True), ("course", True)]


def test_reading_mode_folds_both_and_gives_them_back(screen, qapp):
    _open(screen, qapp, "separable")
    screen.toggle_course()                    # the reader's own choice
    assert screen.course_rail.is_collapsed()
    assert not screen.workspace_rail.is_collapsed()

    screen.reading_mode()
    assert screen.is_reading()
    assert screen.course_rail.is_collapsed()
    assert screen.workspace_rail.is_collapsed()
    assert screen.reading_button.isChecked()

    screen.reading_mode()
    assert not screen.is_reading()
    assert screen.course_rail.is_collapsed(), "it was folded before; still is"
    assert not screen.workspace_rail.is_collapsed()


def test_opening_a_column_leaves_reading_mode(screen, qapp):
    _open(screen, qapp, "separable")
    screen.reading_mode(True)
    screen.toggle_workspace()
    assert not screen.is_reading()
    assert not screen.workspace_rail.is_collapsed()
    assert screen.course_rail.is_collapsed(), "only the one asked for opens"


def test_a_narrow_screen_folds_the_course_without_remembering(screen, qapp):
    said = []
    screen.rails_changed.connect(lambda *a: said.append(a))
    _open(screen, qapp, "separable")
    screen.resize(1000, 700)
    screen._apply_rails()
    assert screen.course_rail.is_collapsed()
    screen.resize(1700, 950)
    screen._apply_rails()
    assert not screen.course_rail.is_collapsed()
    assert said == [], "the screen's own folding is not the reader's choice"


# ---------------------------------------------------------------------------
# One question's answer, beside it
# ---------------------------------------------------------------------------


def test_every_typed_question_has_an_answer_page(screen, qapp):
    from odesuite_app.lessons import Solve

    lesson = _open(screen, qapp, "separable")
    typed = [q.key for q in lesson.questions if isinstance(q, Solve)]
    assert typed
    assert set(typed) <= set(screen._workspace.keys())
    assert screen._workspace.current_key() == screen._workspace.keys()[0]


def test_clicking_a_card_brings_its_answer_up(screen, qapp):
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtTest import QTest

    _open(screen, qapp, "separable")
    keys = screen._workspace.keys()
    assert len(keys) >= 2, "this test needs two answerable questions"
    card = screen._cards[keys[1]]
    QTest.mouseClick(card, Qt.LeftButton, Qt.NoModifier, QPoint(4, 4))
    assert screen._workspace.current_key() == keys[1]
    assert card.property("active")
    assert not screen._cards[keys[0]].property("active")


def test_focus_inside_a_page_follows_to_its_question(screen, qapp):
    _open(screen, qapp, "separable")
    keys = screen._workspace.keys()
    other = keys[1]
    # Called directly: focus is only given in an active window, and the
    # tests have none.
    page = screen._workspace.page(other)
    from PySide6.QtWidgets import QPushButton

    button = page.findChildren(QPushButton)[0]
    screen._on_focus(None, button)
    assert screen._workspace.current_key() == other


def test_the_answer_button_opens_a_folded_column(screen, qapp):
    _open(screen, qapp, "separable")
    keys = screen._workspace.keys()
    screen.toggle_workspace()
    assert screen.workspace_rail.is_collapsed()
    screen.answer(keys[-1])
    assert not screen.workspace_rail.is_collapsed()
    assert screen._workspace.current_key() == keys[-1]


def test_the_cards_chip_mirrors_the_verdict(screen, qapp, store):
    from PySide6.QtWidgets import QLineEdit

    from odesuite_app.lessons import Solve

    lesson = _open(screen, qapp, "separable")
    question = next(q for q in lesson.questions if isinstance(q, Solve))
    chip = screen._chips[question.key]
    assert chip.text() == "not answered yet"

    box = screen._workspace.page(question.key).findChildren(QLineEdit)[0]
    box.setText("exp(t**2)")
    screen._check_solve(lesson, question, box, screen._verdicts[question.key])
    assert chip.text().startswith("✓")

    box.setText("exp(t)")
    screen._check_solve(lesson, question, box, screen._verdicts[question.key])
    assert chip.text().startswith("✗")
    assert "\n" not in chip.text() and len(chip.text()) <= 90


def test_a_new_page_drops_the_old_answers(screen, qapp):
    _open(screen, qapp, "separable")
    before = set(screen._workspace.keys())
    _open(screen, qapp, "separable", "Learn")
    assert screen._workspace.keys() == []
    assert screen._workspace.current_key() == ""
    _open(screen, qapp, "separable", "Drill")
    assert set(screen._workspace.keys()).isdisjoint(before)


# ---------------------------------------------------------------------------
# The window remembers
# ---------------------------------------------------------------------------


def test_the_window_remembers_the_columns_across_a_theme_change(
        qapp, store, scratch_settings):
    from odesuite_app.app import MainWindow

    window = MainWindow()
    window.go("lessons")
    lessons = window._screens["lessons"]
    lessons.toggle_course()
    window.toggle_sidebar(False)
    assert window._settings.value("lessons/course_collapsed") in (True, "true")

    window.toggle_theme()
    qapp.processEvents()
    rebuilt = window._screens["lessons"]
    assert rebuilt is not lessons
    assert rebuilt.course_rail.is_collapsed()
    assert window.sidebar.is_collapsed()

    second = MainWindow()
    assert second.sidebar.is_collapsed()
    assert second._screens["lessons"].course_rail.is_collapsed()
    window.deleteLater()
    second.deleteLater()


def test_reading_mode_folds_the_menu_and_gives_it_back(qapp, store,
                                                       scratch_settings):
    from odesuite_app.app import MainWindow

    window = MainWindow()
    window.go("lessons")
    lessons = window._screens["lessons"]
    assert not window.sidebar.is_collapsed()

    lessons.reading_mode(True)
    assert window.sidebar.is_collapsed()
    assert window._flag("layout/sidebar_collapsed") is False, (
        "reading mode is not the reader's choice of menu"
    )
    lessons.reading_mode(False)
    assert not window.sidebar.is_collapsed()
    window.deleteLater()


def test_the_smallest_window_still_has_a_readable_column(qapp, store,
                                                         scratch_settings):
    from PySide6.QtCore import Qt

    from odesuite_app.app import MainWindow
    from odesuite_app.screens.learn_lessons import WORKSPACE_NARROW

    window = MainWindow()
    window.setAttribute(Qt.WA_DontShowOnScreen)
    window.resize(1080, 680)
    window.show()
    window.go("lessons")
    lessons = window._screens["lessons"]
    lessons.select("separable")
    lessons._choose_segment("Practice")
    for _ in range(5):
        qapp.processEvents()
    lessons._apply_rails()
    qapp.processEvents()

    # With the menu open there is no room for 600 px of text beside a full
    # answer column; the course folds and the answer column narrows instead.
    assert lessons.course_rail.is_collapsed()
    assert lessons.workspace_rail.width() == WORKSPACE_NARROW
    assert lessons._scroll.viewport().width() >= 440
    assert lessons.width() <= window.width() - window.sidebar.width()
    assert window._flag("lessons/course_collapsed") is False
    window.close()
    window.deleteLater()
