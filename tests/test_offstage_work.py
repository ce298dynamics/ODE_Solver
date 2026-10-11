"""Work for screens nobody is looking at waits until they are looked at.

The application builds every screen at launch. Before this, their equations
and the phase portrait's analysis all started at once, on the pool the open
lesson typesets on: 51 renders and about fifteen seconds of Python, so the
lesson in front showed raw LaTeX for five to fifteen seconds on a cold start.
"""

from __future__ import annotations

import time

import pytest

pytest.importorskip("PySide6", reason="the app extra is not installed")

from PySide6.QtCore import QThreadPool  # noqa: E402
from PySide6.QtWidgets import QApplication, QStackedWidget, QWidget  # noqa: E402

from odesuite_app.theme import PALETTES  # noqa: E402
from odesuite_app.widgets.mathlabel import MathLabel  # noqa: E402

PALETTE = PALETTES["dark"]


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _spin(qapp, seconds: float, until=lambda: False) -> None:
    end = time.monotonic() + seconds
    while time.monotonic() < end and not until():
        qapp.processEvents()
        QThreadPool.globalInstance().waitForDone(20)
    qapp.processEvents()


def _stack_with_two_pages(label: MathLabel) -> tuple[QStackedWidget, QWidget]:
    stack = QStackedWidget()
    front = QWidget()
    back = QWidget()
    label.setParent(back)
    stack.addWidget(front)
    stack.addWidget(back)
    stack.setCurrentWidget(front)
    return stack, back


def test_an_equation_on_a_hidden_page_waits_to_be_shown(qapp):
    label = MathLabel(PALETTE, r"\int_0^1 t\,dt = \frac{1}{2}")
    stack, back = _stack_with_two_pages(label)
    stack.show()
    _spin(qapp, 1.0)
    assert not label.is_typeset, "typeset for a page nobody can see"

    stack.setCurrentWidget(back)
    _spin(qapp, 30.0, until=lambda: label.is_typeset)
    assert label.is_typeset, "never typeset once its page was shown"
    stack.deleteLater()


def test_a_label_in_no_window_typesets_as_it_always_did(qapp):
    label = MathLabel(PALETTE, r"e^{-t}\cos 2t")
    _spin(qapp, 30.0, until=lambda: label.is_typeset)
    assert label.is_typeset


def test_latex_source_is_never_shown_while_waiting(qapp):
    """An equation given as LaTeX has only its source for a plain form, and
    the source on screen looked like a broken page."""
    label = MathLabel(PALETTE, r"\frac{dy}{dt} = f(t)\, g(y)")
    stack, _ = _stack_with_two_pages(label)
    stack.show()
    qapp.processEvents()
    assert label._label.text() == ""
    stack.deleteLater()


def test_a_sympy_expression_still_shows_its_plain_form_while_waiting(qapp):
    import sympy as sp

    t = sp.Symbol("t")
    label = MathLabel(PALETTE, sp.exp(-t))
    stack, _ = _stack_with_two_pages(label)
    stack.show()
    qapp.processEvents()
    assert label._label.text() == "exp(-t)"
    stack.deleteLater()


def test_the_phase_portrait_does_not_analyse_until_it_is_opened(qapp):
    from odesuite_app.app import MainWindow

    window = MainWindow("dark")
    try:
        portrait = window._screens["portrait"]
        _spin(qapp, 1.0)
        assert portrait._data is None
        assert portrait._queued_reset is not None, "nothing was queued"

        window.go("portrait")
        _spin(qapp, 120.0, until=lambda: portrait._data is not None)
        assert portrait._data is not None
    finally:
        window.deleteLater()
        qapp.processEvents()
