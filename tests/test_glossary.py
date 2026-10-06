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


def test_a_chapter_counts_as_a_use():
    """The chapters are most of the Learn page. "Used in" searched only the
    summary cards, and missed 200 term-lesson pairs -- the Laplace chapter
    solves initial value problems on every page and was not listed."""
    ivp = next(t for t in TERMS if t.name == "initial value problem")
    assert by_key("laplace") in uses(ivp, LESSONS)


def test_the_word_in_its_everyday_sense_is_not_a_use():
    """The centre of a disc, and a power series' centre, are not equilibria;
    hyperbolic functions are not hyperbolic equilibria."""
    centre = next(t for t in TERMS if t.name == "centre")
    found = {lesson.key for lesson in uses(centre, LESSONS)}
    assert not found & {"power-series", "recurrence", "frobenius", "motion",
                        "cauchy", "reduction-of-order"}, found
    assert {"phase-portraits", "almost-linear"} <= found
    hyperbolic = next(t for t in TERMS if t.name == "hyperbolic")
    found = {lesson.key for lesson in uses(hyperbolic, LESSONS)}
    assert not found & {"motion", "transform", "superposition"}, found


# ---------------------------------------------------------------------------
# Terms as links in a lesson's prose
# ---------------------------------------------------------------------------


def _links(html: str) -> list[tuple[str, str]]:
    import re

    from odesuite_app.lessons.glossary import term_of

    return [(term_of(href).name, text) for href, text in
            re.findall(r'<a href="(term:\d+)"[^>]*>([^<]*)</a>', html)]


def test_only_the_first_use_on_a_page_is_a_link():
    from odesuite_app.lessons.glossary import link_terms

    linked: set[int] = set()
    first = link_terms("The Wronskian decides it.", "laplace", linked)
    second = link_terms("Again the Wronskian, and a Wronskian.", "laplace", linked)
    assert _links(first) == [("Wronskian", "Wronskian")]
    assert _links(second) == []


def test_the_longest_name_wins_and_the_writing_is_kept():
    from odesuite_app.lessons.glossary import link_terms

    html = link_terms("An Initial Value Problem, then an exact equation.",
                      "laplace", set())
    assert _links(html) == [("initial value problem", "Initial Value Problem"),
                            ("exact equation", "exact equation")]


def test_a_term_is_not_linked_in_the_lesson_that_teaches_it():
    from odesuite_app.lessons.glossary import link_terms

    assert _links(link_terms("The Wronskian.", "superposition", set())) == []


def test_markup_is_stepped_over_and_never_linked_inside():
    """The input is rich text already: an entity, a tag's attributes and an
    existing link must come out exactly as they went in."""
    from odesuite_app.lessons.glossary import link_terms

    html = ('<i title="Wronskian">x</i> &amp; <a href="#">Wronskian</a> '
            "and a Jacobian")
    out = link_terms(html, "laplace", set())
    assert out.startswith('<i title="Wronskian">x</i> &amp; <a href="#">'
                          "Wronskian</a> and a ")
    assert _links(out)[-1] == ("Jacobian", "Jacobian")


def test_everyday_senses_and_unlinkable_terms_stay_plain():
    from odesuite_app.lessons.glossary import link_terms

    assert _links(link_terms("Distance from the centre of the Earth.",
                             "motion", set())) == []
    assert _links(link_terms("A centre, and its centre.", "recurrence",
                             set())) == []
    assert _links(link_terms("hyperbolic functions", "motion", set())) == []
    # "order" is in the glossary, and never a link: see Term.linkable.
    assert _links(link_terms("a second order equation", "laplace", set())) == []
    assert _links(link_terms("A linear centre.", "limit-cycles",
                             set())) == [("centre", "centre")]


def test_every_chapter_link_points_at_a_real_linkable_term():
    """Across the whole course: every link resolves, no term is linked twice
    in a lesson, and none is linked in the lesson that teaches it."""
    from odesuite_app.lessons.chapter import blocks_of
    from odesuite_app.lessons.glossary import link_terms

    total = 0
    for lesson in LESSONS:
        linked: set[int] = set()
        names = []
        for block in blocks_of(lesson.chapter):
            if block.kind == "para":
                names += [name for name, _ in
                          _links(link_terms(block.text, lesson.key, linked))]
        assert len(names) == len(set(names)), lesson.key
        for name in names:
            term = next(t for t in TERMS if t.name == name)
            assert term.linkable and term.lesson != lesson.key
            assert lesson.key not in term.not_lessons
        total += len(names)
    assert total > 200, total


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


def test_a_term_in_a_chapter_is_a_link_with_its_definition(qapp):
    from PySide6.QtWidgets import QLabel

    from odesuite_app.theme import PALETTES
    from odesuite_app.widgets.chapterview import ChapterView

    lesson = by_key("almost-linear")
    view = ChapterView(lesson.chapter, PALETTES["dark"], lesson_key=lesson.key)
    linked = [label for label in view.findChildren(QLabel)
              if "term:" in label.text()]
    assert linked, "no term was linked"
    label = linked[0]
    from PySide6.QtCore import Qt

    assert label.textInteractionFlags() & Qt.LinksAccessibleByKeyboard
    chosen = []
    view.term_chosen.connect(chosen.append)
    import re
    href = re.search(r'href="(term:\d+)"', label.text()).group(1)
    label.linkActivated.emit(href)
    assert len(chosen) == 1 and chosen[0] in {t.name for t in TERMS}
    view.deleteLater()


def test_without_a_lesson_nothing_is_linked(qapp):
    from PySide6.QtWidgets import QLabel

    from odesuite_app.theme import PALETTES
    from odesuite_app.widgets.chapterview import ChapterView

    view = ChapterView(by_key("almost-linear").chapter, PALETTES["dark"])
    assert not [label for label in view.findChildren(QLabel)
                if "term:" in label.text()]
    view.deleteLater()


def test_a_term_link_opens_the_glossary_at_it(qapp):
    """Even with a search typed that would hide it."""
    from odesuite_app.app import MainWindow

    window = MainWindow("dark")
    glossary = window._screens["glossary"]
    glossary.query.setText("separatri")
    qapp.processEvents()
    window._screens["lessons"].open_term.emit("Jacobian")
    qapp.processEvents()
    assert window.stack.currentWidget() is glossary
    assert glossary.current_term().name == "Jacobian"
    window.deleteLater()


def test_the_window_opens_the_lesson_a_glossary_link_names(qapp):
    from odesuite_app.app import MainWindow

    window = MainWindow("dark")
    glossary = window._screens["glossary"]
    glossary.open_lesson.emit("limit-cycles")
    qapp.processEvents()
    assert window.stack.currentWidget() is window._screens["lessons"]
    assert window._screens["lessons"].current_lesson().key == "limit-cycles"
    window.deleteLater()
