"""No side panel is wider than the space it is given.

Every screen's controls sit in a fixed-width column that never scrolls
sideways, so anything inside that asks to be wider than the column cuts every
line of it off at the right edge. The quiz's did, by over 100 px, and nothing
caught it, because no test looked at a laid-out screen. This one does, for
every screen: it lays the window out and compares what each panel needs with
what it has.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6", reason="the app extra is not installed")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication, QScrollArea  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(scope="module")
def window(qapp):
    from odesuite_app.app import MainWindow

    win = MainWindow("light")
    win.resize(1440, 900)
    win.show()                  # offscreen under the tests: nothing appears
    yield win
    win.close()
    win.deleteLater()
    qapp.processEvents()


def _screen_keys():
    from odesuite_app.app import SCREENS

    return [key for key, _, _ in SCREENS]


def _is_side_panel(area: QScrollArea) -> bool:
    """A fixed-width control column, as `control_panel` builds them."""
    return (area.accessibleName() == "controls"
            and area.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOff)


@pytest.mark.parametrize("key", _screen_keys())
def test_no_side_panel_is_cut_off(window, qapp, key):
    window.go(key)
    for _ in range(30):
        qapp.processEvents()

    for area in window._screens[key].findChildren(QScrollArea):
        if not _is_side_panel(area) or not area.isVisibleTo(window):
            continue
        need = area.widget().minimumSizeHint().width()
        have = area.viewport().width()
        if need > have:
            # Name the culprit: this fails on runners whose fonts and user
            # names differ from any machine the panel was looked at on.
            from PySide6.QtWidgets import QWidget

            widest = sorted(
                ((child.minimumSizeHint().width(), type(child).__name__,
                  (getattr(child, "text", lambda: "")() or "")[:40])
                 for child in area.widget().findChildren(QWidget)
                 if child.isVisibleTo(window)),
                reverse=True,
            )[:3]
            pytest.fail(f"{key}: a panel needs {need}px and has {have}px, so "
                        f"its right edge is cut off; widest: {widest}")


@pytest.mark.parametrize("key", _screen_keys())
def test_every_picker_in_a_side_panel_can_shrink_to_it(window, qapp, key):
    """The measurement above depends on the fonts: under the tests' offscreen
    platform text measures narrower than on a real Windows desktop at 150%,
    where the quiz, Print & Revise, Solver Lab, Method Race and Accuracy Lab
    panels were all cut off by their drop-downs. This holds on any platform:
    a drop-down in a panel takes the width it is given rather than the width
    of its longest entry."""
    from PySide6.QtWidgets import QComboBox

    window.go(key)
    for _ in range(5):
        qapp.processEvents()
    for area in window._screens[key].findChildren(QScrollArea):
        if not _is_side_panel(area):
            continue
        for combo in area.widget().findChildren(QComboBox):
            assert (combo.sizeAdjustPolicy()
                    == QComboBox.AdjustToMinimumContentsLengthWithIcon), (
                f"{key}: a picker sizes itself to its longest entry"
            )
