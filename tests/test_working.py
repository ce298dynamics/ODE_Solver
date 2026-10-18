"""Checking working line by line.

Each line is a claim about the solution, tested against the verified family:
these are the worked examples a marker would write in a margin about.
"""

from __future__ import annotations

import pytest

sp = pytest.importorskip("sympy")

from odesuite_app.symbolic import parse_equation, spec_for  # noqa: E402
from odesuite_app.working import (  # noqa: E402
    OK,
    UNCHECKED,
    UNREADABLE,
    WRONG,
    available,
    check_working,
)

from .narrators import narrate  # noqa: E402


def _solutions(equation: str, conditions: str = ""):
    general = narrate("steps", parse_equation(spec_for(equation, "")))
    parsed = parse_equation(spec_for(equation, conditions))
    particular = None
    if conditions:
        particular = narrate("steps", parsed).result
        particular = getattr(particular, "rhs", particular)
    result = getattr(general.result, "rhs", general.result)
    return parsed, result, particular


def _check(equation: str, working: str, conditions: str = ""):
    parsed, general, particular = _solutions(equation, conditions)
    return check_working(parsed, working, general, particular)


def _statuses(verdicts):
    return [v.status for v in verdicts]


# ---------------------------------------------------------------------------
# Right working is right
# ---------------------------------------------------------------------------


def test_an_integrating_factor_chain_checks_out():
    verdicts = _check("y' + 2*y = 4", """
        y' + 2y = 4
        mu = e^(2t)
        (e^(2t) y)' = 4e^(2t)
        e^(2t) y = 2e^(2t) + C
        y = 2 + Ce^(-2t)
    """)
    assert _statuses(verdicts) == [OK] * 5, verdicts


def test_leibniz_notation_and_joining_words_are_read():
    verdicts = _check("y' + 2*y = 4", """
        dy/dt + 2y = 4
        so d/dt(e^(2t) y) = 4 e^(2t)    # multiply through by mu
        => y(t) = 2 + C e^(-2t)
    """)
    assert _statuses(verdicts) == [OK] * 3, verdicts


def test_separable_with_a_logarithm():
    verdicts = _check("y' = 2*t*y", """
        dy/dt = 2ty
        ln|y| = t^2 + C
        y = A e^(t^2)
    """)
    assert _statuses(verdicts) == [OK] * 3, verdicts


def test_conditions_applied_on_the_way_are_right():
    verdicts = _check("y' + 2*y = 4", """
        e^(2t) y = 2e^(2t) + C
        y = 2 + Ce^(-2t)
        y = 2 - e^(-2t)
    """, "y(0) = 1")
    assert _statuses(verdicts) == [OK] * 3, verdicts


def test_a_repeated_root_worked_through():
    verdicts = _check("y'' + 2*y' + y = 0", """
        r^2 + 2r + 1 = 0
        r = -1, -1
        y = (C1 + C2 t) e^(-t)
    """)
    assert _statuses(verdicts) == [OK] * 3, verdicts


def test_complex_roots_with_plus_or_minus():
    verdicts = _check("y'' + 2*y' + 5*y = 0", """
        r^2 + 2r + 5 = 0
        r = -1 ± 2i
        y = e^(-t)(C1 cos(2t) + C2 sin(2t))
    """)
    assert _statuses(verdicts) == [OK] * 3, verdicts


# ---------------------------------------------------------------------------
# The first slip is found where it is
# ---------------------------------------------------------------------------


def test_a_sign_slip_is_placed_on_its_line():
    verdicts = _check("y' + 2*y = 4", """
        y' + 2y = 4
        mu = e^(2t)
        (e^(2t) y)' = -4e^(2t)
        e^(2t) y = -2e^(2t) + C
        y = -2 + Ce^(-2t)
    """)
    statuses = _statuses(verdicts)
    assert statuses[:2] == [OK, OK]
    assert statuses[2] == WRONG, verdicts
    # Numbered as the editor numbers them: the text opens with a blank line.
    assert "between line 3" in verdicts[2].message
    assert statuses[-1] == WRONG


def test_a_dropped_constant_is_named():
    verdicts = _check("y' + 2*y = 4", """
        (e^(2t) y)' = 4e^(2t)
        e^(2t) y = 2e^(2t)
        y = 2
    """)
    assert verdicts[0].status == OK
    assert verdicts[1].status == WRONG
    assert "constant was lost" in verdicts[1].message


def test_a_wrong_integrating_factor():
    verdicts = _check("y' + 2*y = 4", "mu = e^(-2t)")
    assert verdicts[0].status == WRONG
    assert "e^(∫p dt)" in verdicts[0].message


def test_a_factor_up_to_a_constant_is_fine():
    assert _check("y' + 2*y = 4", "mu = 3e^(2t)")[0].status == OK


def test_a_wrong_characteristic_polynomial():
    verdicts = _check("y'' + 2*y' + y = 0", """
        r^2 + r + 1 = 0
        r = -1
    """)
    assert verdicts[0].status == WRONG
    assert verdicts[1].status == OK, "-1 is still a root of the real one"


def test_a_wrong_root():
    verdicts = _check("y'' - 3*y' + 2*y = 0", "r = 1, 3")
    assert verdicts[0].status == WRONG
    assert "3 is not a root" in verdicts[0].message


def test_the_final_answer_is_judged_as_the_answer_box_would():
    verdicts = _check("y'' + 2*y' + y = 0", "y = C1 e^(-t) + C2 e^(-t)")
    assert verdicts[0].status == WRONG
    assert "one constant" in verdicts[0].message


# ---------------------------------------------------------------------------
# What cannot be read does not stop the rest
# ---------------------------------------------------------------------------


def test_an_unreadable_line_does_not_stop_the_check():
    verdicts = _check("y' + 2*y = 4", """
        y' + 2y = 4
        (e^(2t) y' = 4e^(2t)
        y = 2 + Ce^(-2t)
    """)
    assert _statuses(verdicts) == [OK, UNREADABLE, OK], verdicts
    assert "bracket" in verdicts[1].message


def test_a_line_in_differentials_is_left_to_the_next():
    """`dy/y^2 = dt` once passed, by reading d as a constant and setting it
    to zero. The integrated line after it is what gets checked."""
    verdicts = _check("y' = y^2", """
        dy/y^2 = dt
        -1/y = t + C
    """)
    assert _statuses(verdicts) == [UNCHECKED, OK], verdicts


def test_a_line_with_nothing_to_check_says_so():
    verdicts = _check("y' + 2*y = 4", "C = 3")
    assert verdicts[0].status == UNCHECKED


def test_blank_lines_and_comments_are_skipped():
    verdicts = _check("y' + 2*y = 4", "\n\n   # my working\ny = 2 + Ce^(-2t)\n")
    assert len(verdicts) == 1 and verdicts[0].number == 4


@pytest.mark.parametrize(
    "payload",
    [
        "y = __import__('os').system('echo pwned')",
        "y = ().__class__.__bases__",
        "y = open('x', 'w')",
        "mu = eval('1+1')",
    ],
)
def test_working_cannot_execute_code(payload):
    verdicts = _check("y' + 2*y = 4", payload)
    assert verdicts[0].status in (UNREADABLE, UNCHECKED, WRONG)
    assert verdicts[0].status != OK


def test_systems_and_laplace_are_not_offered_yet():
    parsed = parse_equation(spec_for("y' + 2*y = 4"))
    assert available(parsed, "steps")[0]
    assert not available(parsed, "laplace")[0]
    system = parse_equation(spec_for("x' = y; y' = -x"))
    assert not available(system, "systems")[0]


# ---------------------------------------------------------------------------
# On the page
# ---------------------------------------------------------------------------


@pytest.mark.slow
def test_working_is_checked_on_the_lesson_page(tmp_path, monkeypatch):
    """Typed into a practice question's answer page, checked off the thread,
    and the first slip is the line the report names."""
    import time

    from PySide6.QtCore import QThreadPool
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QPlainTextEdit,
        QPushButton,
    )

    from odesuite_app import progress
    from odesuite_app.lessons import Solve
    from odesuite_app.screens.learn_lessons import LessonsScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(progress, "directory", lambda: tmp_path / "odesuite")
    screen = LessonsScreen(SessionState(), PALETTES["dark"])
    try:
        screen.select("separable")
        screen._choose_segment("Practice")
        app.processEvents()
        lesson = screen.current_lesson()
        question = next(q for q in lesson.questions if isinstance(q, Solve))
        assert question.equation.replace(" ", "") == "y'=2*t*y"
        page = screen._workspace.page(question.key)
        toggle = next(b for b in page.findChildren(QPushButton)
                      if b.text().startswith("Show your working"))
        toggle.click()
        box = page.findChildren(QPlainTextEdit)[0]
        box.setPlainText("dy/dt = 2ty\nln|y| = t^2 + C\ny = A e^(2t^2)")
        next(b for b in page.findChildren(QPushButton)
             if b.text() == "Check working").click()
        report = next(label for label in page.findChildren(QLabel)
                      if label.accessibleName() == "working checked")
        deadline = time.monotonic() + 120
        while "checking" in report.text() and time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.05)
        assert "first slip is on line 3" in report.text(), report.text()
        assert progress.load() == {}, "checking working is not recorded"
    finally:
        screen.deleteLater()
        QThreadPool.globalInstance().clear()


def test_a_fresh_t_after_sympys_cache_is_evicted_is_still_t():
    """SymPy's symbol cache is an LRU: after enough expressions, a newly
    parsed t is equal to the module's t without being the same object. An
    identity test then read t as a student's constant and every final line
    "did not contain t at all" -- seen only late in a long test run."""
    from sympy.core.cache import clear_cache

    parsed, general, particular = _solutions("y' + 2*y = 4")
    clear_cache()
    verdicts = check_working(parsed, "y = 2 + Ce^(-2t)", general, particular)
    assert verdicts[0].status == OK, verdicts
