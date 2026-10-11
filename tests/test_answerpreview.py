"""The live preview under a typed-answer box.

What matters is that it reads the text exactly as the grader does: a preview
with its own idea of what was typed would show the student one function and
mark them on another. So these tests compare it with `read_answer` and
`check_answer` rather than with LaTeX written out by hand.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6", reason="the app extra is not installed")

from PySide6.QtWidgets import QApplication, QLineEdit  # noqa: E402

from odesuite_app.symbolic import (  # noqa: E402
    EquationSpec,
    check_answer,
    parse_equation,
    spec_for,
)
from odesuite_app.theme import PALETTES  # noqa: E402
from odesuite_app.widgets.answerpreview import AnswerPreview  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _preview(qapp, equation: str, text: str, conditions: str = ""):
    parsed = parse_equation(spec_for(equation, conditions))
    box = QLineEdit()
    preview = AnswerPreview(PALETTES["dark"], box, lambda: parsed)
    box.setText(text)
    preview.refresh()
    return preview, parsed


def test_an_empty_box_shows_nothing(qapp):
    preview, _ = _preview(qapp, "y' = 2*t*y", "")
    assert preview.isHidden()


def test_a_readable_answer_is_typeset_as_the_grader_reads_it(qapp):
    preview, parsed = _preview(qapp, "y' = 2*t*y", "y = exp(t**2)", "y(0) = 1")
    assert not preview.isHidden()
    [row] = preview.rows
    assert "e^{t^{2}}" in row.latex
    assert check_answer(parsed, "y = exp(t**2)").correct is True


def test_the_y_equals_is_optional_here_as_in_the_grader(qapp):
    with_it, _ = _preview(qapp, "y' = y", "y = C1*exp(t)")
    without, _ = _preview(qapp, "y' = y", "C1*exp(t)")
    assert with_it.rows[0].latex == without.rows[0].latex


def test_a_misplaced_bracket_reads_as_a_different_function(qapp):
    """The case the preview exists for: two strings one bracket apart, both
    valid, meaning different things. As code they look alike; typeset they
    do not."""
    meant, _ = _preview(qapp, "y'' + 2*y' + 5*y = 0",
                        "y = exp(-t)*(C1*cos(2*t) + C2*sin(2*t))")
    typo, _ = _preview(qapp, "y'' + 2*y' + 5*y = 0",
                       "y = exp(-t)*C1*cos(2*t) + C2*sin(2*t)")
    assert meant.rows[0].latex != typo.rows[0].latex


def test_half_typed_text_gets_a_quiet_note_not_an_error(qapp):
    preview, _ = _preview(qapp, "y' = y", "y = exp(")
    assert not preview.isHidden()
    assert preview.rows == []
    assert preview.note.text().startswith("Not readable yet")
    assert preview.note.property("role") == "muted"


def test_a_system_answer_gets_one_line_per_unknown(qapp):
    preview, _ = _preview(qapp, "x' = y; y' = -x",
                          "x = C1*cos(t) + C2*sin(t); y = -C1*sin(t) + C2*cos(t)")
    assert len(preview.rows) == 2
    assert preview.rows[0].latex.startswith("x{\\left(t \\right)}")


def test_a_system_line_that_does_not_name_its_unknown_is_explained(qapp):
    preview, _ = _preview(qapp, "x' = y; y' = -x", "C1*cos(t)")
    assert "naming each" in preview.note.text()


def test_attribute_access_is_refused_not_evaluated(qapp):
    """The preview is a new place typed text reaches sympy, so it must go
    through the hardened parser and not around it."""
    preview, _ = _preview(qapp, "y' = y", "sin.__class__")
    assert preview.rows == []
    assert preview.note.text().startswith("Not readable yet")


def test_a_question_that_cannot_be_parsed_hides_the_preview(qapp):
    box = QLineEdit()
    preview = AnswerPreview(PALETTES["dark"], box, lambda: None)
    box.setText("y = t")
    preview.refresh()
    assert preview.isHidden()


def test_typing_refreshes_after_a_pause(qapp):
    parsed = parse_equation(EquationSpec(equations=["y' = y"]))
    box = QLineEdit()
    preview = AnswerPreview(PALETTES["dark"], box, lambda: parsed)
    box.setText("y = exp(t)")
    assert preview.isHidden()               # nothing yet: the timer is running
    assert preview._timer.isActive()


def test_every_typed_solution_box_in_the_app_has_a_preview(qapp):
    """Practice, Drill and Solve Step by Step: wherever a typed solution is
    graded by substitution, the reader can see what was read. The quiz builds
    its box only once a paper is under way, so it is not reached from here."""
    from odesuite_app.app import build_application

    _, window = build_application("dark")
    try:
        lessons = window._screens["lessons"]
        lessons.select("separable")
        lessons.segment_buttons["Practice"].click()
        qapp.processEvents()
        assert lessons.findChildren(AnswerPreview)

        lessons.segment_buttons["Drill"].click()
        qapp.processEvents()
        assert lessons.findChildren(AnswerPreview)

        assert window._screens["steps"].findChildren(AnswerPreview)
    finally:
        window.deleteLater()
        qapp.processEvents()
