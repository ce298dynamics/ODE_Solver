"""The glossary: every link goes somewhere real, and "used in" is found."""

from __future__ import annotations

import pytest

from odesuite_app.lessons import LESSONS, by_key
from odesuite_app.lessons.glossary import TERMS, search, text_of, uses


def test_names_are_unique():
    names = [term.name.lower() for term in TERMS]
    assert len(set(names)) == len(names)


@pytest.mark.parametrize("term", TERMS, ids=[t.name for t in TERMS])
def test_the_defining_lesson_exists_and_uses_the_term(term):
    """A link to a lesson where the word never appears is a link to nowhere."""
    lesson = by_key(term.lesson)
    assert lesson is not None, f"{term.name}: no lesson {term.lesson!r}"
    assert lesson in uses(term, LESSONS), (
        f"{term.name} does not appear in {term.lesson}")
    assert len(term.definition) > 40


def test_used_in_is_found_rather_than_written():
    """The Wronskian is defined once and used across the second-order unit.
    Nothing lists those lessons: they are found in the text."""
    wronskian = next(t for t in TERMS if t.name == "Wronskian")
    found = {lesson.key for lesson in uses(wronskian, LESSONS)}
    assert {"superposition", "variation", "reduction-of-order"} <= found


def test_a_term_is_matched_as_a_word_not_inside_one():
    order = next(t for t in TERMS if t.name == "order")
    assert all("order" in text_of(lesson).lower()
               for lesson in uses(order, LESSONS))
    spiral = next(t for t in TERMS if t.name == "spiral")
    assert all(lesson in LESSONS for lesson in uses(spiral, LESSONS))


def test_search_ranks_names_before_definitions():
    found = search("eigen")
    assert found[0].name == "eigenvalue"
    assert search("") == TERMS
    assert search("no such thing anywhere") == ()


def test_the_glossary_covers_every_unit():
    from odesuite_app.lessons import unit_of

    units = {unit_of(term.lesson).key for term in TERMS}
    assert len(units) == 8, sorted(units)


# ---------------------------------------------------------------------------
# The screen
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def qapp():
    pytest.importorskip("PySide6", reason="the app extra is not installed")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def screen(qapp):
    from odesuite_app.screens.learn_glossary import GlossaryScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    made = GlossaryScreen(SessionState(), PALETTES["dark"])
    yield made
    made.deleteLater()


def test_the_screen_lists_every_term_and_filters(screen, qapp):
    assert screen.listing.count() == len(TERMS)
    screen.query.setText("separatri")
    qapp.processEvents()
    assert screen.listing.count() == 1
    assert screen.current_term().name == "separatrix"


def test_a_link_opens_the_lesson(screen, qapp):
    from PySide6.QtWidgets import QPushButton

    screen.query.setText("Jacobian")
    qapp.processEvents()
    opened = []
    screen.open_lesson.connect(opened.append)
    first = next(b for b in screen.findChildren(QPushButton)
                 if b.text() == by_key("nonlinear-equilibria").title)
    first.click()
    assert opened == ["nonlinear-equilibria"]


def test_the_window_opens_the_lesson_a_glossary_link_names(qapp):
    from odesuite_app.app import MainWindow

    window = MainWindow("dark")
    glossary = window._screens["glossary"]
    glossary.open_lesson.emit("limit-cycles")
    qapp.processEvents()
    assert window.stack.currentWidget() is window._screens["lessons"]
    assert window._screens["lessons"].current_lesson().key == "limit-cycles"
    window.deleteLater()
