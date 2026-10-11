"""The two-section shell: Learning Hub and Solver Studio.

The app grew from a flat list of six screens to two sections over a shared
Home. Navigation is the kind of thing that looks obviously correct and quietly
is not -- a screen reachable from its button but not its shortcut, a shortcut
bound twice, a section that does not follow when you jump into it from
somewhere else.

The split is presentation only: both sections drive the same `SessionState` and
select from the same catalogue. Nothing here should suggest otherwise, and
`test_the_sections_share_one_model` says so directly.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6", reason="the app extra is not installed")

from PySide6.QtWidgets import QApplication  # noqa: E402

from odesuite_app.app import (  # noqa: E402
    HOME,
    SCREENS,
    SECTION_OF,
    SECTIONS,
    build_application,
)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(scope="module")
def window(qapp):
    """One window for the module.

    Building it constructs all nine screens, which takes seconds; doing that
    per test made this file slower than the entire rest of the suite. Navigation
    state is cheap to reset instead -- see `_back_to_home` below.
    """
    _, win = build_application("dark")
    yield win
    win.deleteLater()
    qapp.processEvents()


@pytest.fixture(autouse=True)
def _back_to_home(request, qapp):
    """Leave every test on Home in the dark theme, so the shared window cannot
    carry navigation state from one test into the next."""
    yield
    win = request.node.funcargs.get("window")
    if win is not None:
        if win.palette_name != "dark":
            win.toggle_theme()
        win.go("home")
        qapp.processEvents()


# ---------------------------------------------------------------------------
# The structure
# ---------------------------------------------------------------------------


def test_there_are_two_sections_over_a_shared_home():
    assert [section for section, _, _ in SECTIONS] == ["learn", "studio"]
    assert HOME[0] == "home"
    assert HOME[0] not in SECTION_OF, "home belongs to neither section"


def test_every_screen_belongs_somewhere():
    keys = {key for key, _, _ in SCREENS}
    assert keys == set(SECTION_OF) | {"home"}
    assert len(keys) == len(SCREENS), "a screen key is duplicated"


def test_the_studio_keeps_the_screens_that_already_existed():
    """The split moved the existing screens wholesale; none was dropped."""
    studio = {key for key, section in SECTION_OF.items() if section == "studio"}
    assert studio == {"lab", "portrait", "stiffness", "race", "accuracy"}


def test_shortcuts_are_unique_across_the_whole_app():
    """Deliberately not restarting per section: a shortcut that means two
    different screens depending on an invisible mode is worse than no
    shortcut."""
    shortcuts = [shortcut for _, _, shortcut in SCREENS]
    assert len(set(shortcuts)) == len(shortcuts), f"duplicated: {shortcuts}"


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", [key for key, _, _ in SCREENS])
def test_every_screen_is_reachable_by_key(window, key):
    window.go(key)
    assert window.stack.currentWidget() is window._screens[key]


@pytest.mark.parametrize("key", [key for key, _, _ in SCREENS])
def test_every_screen_is_reachable_from_its_sidebar_button(window, qapp, key):
    window.sidebar.buttons[key].click()
    qapp.processEvents()
    assert window.stack.currentWidget() is window._screens[key]


def test_going_to_a_screen_switches_to_its_section(window):
    """Callers pass a bare screen key and always have -- `cli.py --screen`, the
    Home tiles, the tests. Resolving the section here is what keeps that true.
    """
    window.go("steps")
    assert window.sidebar.section_buttons["learn"].isChecked()

    window.go("stiffness")
    assert window.sidebar.section_buttons["studio"].isChecked(), (
        "jumping into the other section should bring the sidebar with it"
    )
    assert window.stack.currentWidget() is window._screens["stiffness"]


def test_only_the_current_sections_buttons_are_shown(window, qapp):
    window.go("lab")
    qapp.processEvents()
    assert window.sidebar.section_pages["studio"].isVisibleTo(window.sidebar)
    assert not window.sidebar.section_pages["learn"].isVisibleTo(window.sidebar)

    window.go("steps")
    qapp.processEvents()
    assert window.sidebar.section_pages["learn"].isVisibleTo(window.sidebar)
    assert not window.sidebar.section_pages["studio"].isVisibleTo(window.sidebar)


def test_the_section_switch_opens_that_sections_first_screen(window, qapp):
    window.show_section("studio")
    qapp.processEvents()
    first = SECTIONS[1][2][0][0]
    assert window.stack.currentWidget() is window._screens[first]


def test_an_unknown_key_is_ignored_rather_than_crashing(window):
    window.go("lab")
    window.go("no_such_screen")
    assert window.stack.currentWidget() is window._screens["lab"]


def test_home_belongs_to_neither_section(window, qapp):
    """It sits above the split, so reaching it should not silently retarget the
    section switch."""
    window.go("stiffness")
    qapp.processEvents()
    window.go("home")
    qapp.processEvents()
    assert window.stack.currentWidget() is window._screens["home"]
    assert window.sidebar.section_buttons["studio"].isChecked()


# ---------------------------------------------------------------------------
# The landing page
# ---------------------------------------------------------------------------


def test_home_offers_a_way_into_both_sections(window):
    from odesuite_app.widgets.cards import ShowcaseTile

    home = window._screens["home"]
    routes = []
    home.showcase_chosen.connect(routes.append)
    for tile in home.findChildren(ShowcaseTile):
        tile.clicked.emit()

    assert routes, "the landing page should offer entry points"
    sections = {SECTION_OF.get(key) for key in routes}
    assert sections == {"learn", "studio"}, (
        f"the tiles only reach {sections}; both sections should be discoverable"
    )
    for key in routes:
        assert key in window._screens, f"a tile points at a screen that is missing: {key}"


# ---------------------------------------------------------------------------
# What the split must not change
# ---------------------------------------------------------------------------


def test_the_sections_share_one_model(window):
    """The split is presentation. A problem chosen anywhere is the same problem
    everywhere, which is what lets a typed equation reach every screen."""
    from odesuite_app import catalog

    window.state.set_problem("brusselator")
    assert window.state.problem_key == "brusselator"

    window.go("steps")
    window.go("lab")
    assert window.state.problem_key == "brusselator", (
        "moving between sections must not reset the session"
    )
    assert catalog.get("brusselator") is not None


def test_toggling_the_theme_keeps_both_the_screen_and_the_section(window, qapp):
    """`toggle_theme` rebuilds every screen wholesale, so it has to put the user
    back where they were -- now in two dimensions rather than one."""
    window.go("race")
    qapp.processEvents()

    window.toggle_theme()
    qapp.processEvents()

    assert window.palette_name == "light"
    assert window.stack.currentWidget() is window._screens["race"]
    assert window.sidebar.section_buttons["studio"].isChecked()


def test_the_cli_advertises_every_screen_it_accepts():
    """`--screen` help is the only place the screen names are documented; a name
    missing from it is a feature nobody can find."""
    from odesuite_app.cli import build_parser

    help_text = build_parser().format_help()
    for key, _, _ in SCREENS:
        assert key in help_text, f"--screen help does not mention {key!r}"


def test_the_learning_hub_puts_the_course_before_the_tools(window):
    """Four screens are the course and five are tools a lesson opens; the
    sidebar says which is which, with the course first."""
    from odesuite_app.app import SUBHEADINGS

    learn = [key for key, _, _ in SECTIONS[0][2]]
    assert learn[:4] == ["course", "lessons", "quiz", "glossary"]
    assert SUBHEADINGS == {"course": "Study", "steps": "Tools"}
    assert window.sidebar.subheadings["course"].text() == "STUDY"
    assert window.sidebar.subheadings["steps"].text() == "TOOLS"


def test_an_ampersand_in_a_screen_name_is_shown_not_eaten(window):
    """Qt reads a lone `&` in a button as a mnemonic marker and hides it, so
    "Quiz & Exams" rendered as "Quiz  Exams"."""
    assert window.sidebar.buttons["quiz"].text() == "Quiz && Exams"
    assert window.sidebar.buttons["print"].text() == "Print && Revise"


@pytest.mark.parametrize("restored, remembered, expected", [
    ("", "", "course"),          # a first launch opens on the course
    ("", "portrait", "portrait"),
    ("lab", "portrait", "lab"),  # a saved session is the more specific memory
])
def test_a_launch_opens_where_it_should(restored, remembered, expected):
    from types import SimpleNamespace

    from odesuite_app.cli import opening_screen

    window = SimpleNamespace(restore_session=lambda: restored,
                             remembered_screen=lambda: remembered)
    assert opening_screen(window) == expected


def test_a_lesson_leads_on_to_the_next_one(window, qapp):
    from odesuite_app import lessons as content

    screen = window._screens["lessons"]
    first, second = content.LESSONS[0], content.LESSONS[1]
    screen.select(first.key)
    screen.segment_buttons["Drill"].click()
    qapp.processEvents()

    assert screen.next_button.isVisibleTo(screen)
    assert screen.next_button.toolTip() == f"Next: {second.title}"
    screen.next_button.click()
    qapp.processEvents()

    assert screen.current_lesson().key == second.key
    assert screen.segment_buttons["Learn"].isChecked()   # a new lesson starts at its notes


def test_the_last_lesson_has_nowhere_to_lead(window, qapp):
    from odesuite_app import lessons as content

    screen = window._screens["lessons"]
    screen.select(content.LESSONS[-1].key)
    qapp.processEvents()
    assert screen.next_lesson() is None
    assert not screen.next_button.isVisibleTo(screen)
