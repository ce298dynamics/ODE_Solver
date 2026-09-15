"""Rendered mathematics follows the operating system's text scale.

The bug this guards is easy to reintroduce and invisible in a screenshot taken
at 100%: every font size in this application is written in *pixels*, so raising
the OS text scale -- which Qt reports as a larger default font point size and
nothing else -- left the entire interface exactly where it was. Equations were
the worst case, because they are matplotlib bitmaps and cannot inherit a font
size at all, so the maths would have stayed smallest on a page whose prose had
grown around it.

The tests drive it the way a reader would: by changing the application font and
looking at what comes out.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6", reason="the app extra is not installed")

from PySide6.QtGui import QFont  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from odesuite_app import mathrender, theme  # noqa: E402
from odesuite_app.theme import PALETTES  # noqa: E402
from odesuite_app.widgets.mathlabel import MathLabel  # noqa: E402

PALETTE = PALETTES["dark"]


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def at_scale(qapp):
    """Set the application font to a chosen multiple of the baseline."""
    original = qapp.font()

    def set_scale(factor: float):
        font = QFont(original)
        font.setPointSizeF(theme.BASELINE_POINT_SIZE * factor)
        qapp.setFont(font)
        qapp.processEvents()
        return theme.text_scale(qapp)

    yield set_scale
    qapp.setFont(original)
    qapp.processEvents()


# ---------------------------------------------------------------------------
# The factor itself
# ---------------------------------------------------------------------------


def test_the_baseline_font_is_no_scale_at_all(at_scale):
    assert at_scale(1.0) == pytest.approx(1.0)


def test_two_hundred_percent_is_read_as_two(at_scale):
    assert at_scale(2.0) == pytest.approx(2.0)


def test_the_scale_is_clamped_at_both_ends(at_scale):
    """A machine reporting a tiny default font must not shrink the whole
    application into illegibility, and nothing sane asks for 10x."""
    assert at_scale(0.1) >= 0.8
    assert at_scale(12.0) <= 3.0


def test_no_application_means_no_scaling():
    """The thumbnail generator and the headless tests get the sizes the code
    was written against."""
    assert theme.text_scale(app=None) == 1.0 or theme.text_scale() > 0


# ---------------------------------------------------------------------------
# The style sheet
# ---------------------------------------------------------------------------


def test_the_style_sheet_grows_every_font_size():
    plain = theme.stylesheet(PALETTE, 1.0)
    doubled = theme.stylesheet(PALETTE, 2.0)
    assert "font-size: 13px" in plain
    assert "font-size: 26.0px" in doubled
    assert "font-size: 52.0px" in doubled, "the title should double too"


def test_scaling_touches_font_size_and_nothing_else():
    """Padding and borders are device pixels and Qt already scales those;
    multiplying them here as well would double-count the high-DPI factor."""
    css = "font-size: 12px; padding: 4px 8px; border-radius: 10px;"
    scaled = theme.scaled(css, 2.0)
    assert "font-size: 24.0px" in scaled
    assert "padding: 4px 8px" in scaled
    assert "border-radius: 10px" in scaled


def test_an_inline_html_size_is_scaled_too():
    """Several verdicts are rich text with a style attribute rather than a
    style sheet, and a reader does not care which a caption happened to use."""
    assert "font-size:24.0px" in theme.scaled(
        '<span style="color:#fff;font-size:12px;">x</span>', 2.0
    )


def test_the_unscaled_sheet_is_returned_unchanged():
    assert theme.stylesheet(PALETTE, 1.0) == theme.stylesheet(PALETTE)


# ---------------------------------------------------------------------------
# The equations
# ---------------------------------------------------------------------------


def test_an_equation_is_rendered_at_the_readers_scale(qapp, at_scale):
    label = MathLabel(PALETTE, "y = e^{-t}", point_size=15.0)
    at_scale(1.0)
    assert label.rendered_point_size() == pytest.approx(15.0)
    at_scale(2.0)
    assert label.rendered_point_size() == pytest.approx(30.0)
    label.deleteLater()


def test_raising_the_scale_re_renders_rather_than_keeping_a_stale_bitmap(
    qapp, at_scale
):
    """The half of A11Y-04 that a size calculation alone does not give.

    Qt delivers an OS text-scale change as an application font change, and
    without handling it the prose grows while the equation keeps whatever
    bitmap it was first painted with."""
    at_scale(1.0)
    label = MathLabel(PALETTE, "y = e^{-t}", point_size=15.0)
    _settle(qapp, label)
    before = _height(label)

    at_scale(2.0)
    _settle(qapp, label, until=lambda: _height(label) != before)
    after = _height(label)

    assert after > before * 1.5, (
        f"the equation stayed {before}px tall at twice the text scale "
        f"({after}px)"
    )
    label.deleteLater()


def test_the_maths_tracks_the_body_text(qapp, at_scale):
    """A11Y-04's acceptance criterion: at 200% the equation is still about the
    same size relative to the prose around it as it was at 100%."""
    label = MathLabel(PALETTE, "y = e^{-t}", point_size=15.0)
    ratios = []
    seen = 0
    for factor in (1.0, 2.0):
        at_scale(factor)
        _settle(qapp, label, until=lambda: _height(label) not in (0, seen))
        seen = _height(label)
        ratios.append(seen / _body_pixels(factor))
    assert ratios[1] == pytest.approx(ratios[0], rel=0.1), ratios
    label.deleteLater()


def _height(label: MathLabel) -> int:
    """The height of the bitmap currently painted, in device pixels."""
    pixmap = label._label.pixmap()
    return 0 if pixmap is None or pixmap.isNull() else pixmap.height()


def _body_pixels(factor: float) -> float:
    """The body font size the style sheet asks for at this scale."""
    import re

    sheet = theme.stylesheet(PALETTE, theme.text_scale())
    first = re.search(r"font-size:\s*([0-9.]+)px", sheet)
    assert first is not None
    return float(first.group(1))


def _settle(qapp, label: MathLabel, until=None, timeout: float = 20.0) -> None:
    """Wait for a render to land, the way `test_mathrender` does.

    Waiting on the thread pool rather than spinning `processEvents`: a bare
    spin completes hundreds of iterations in under a millisecond and concludes
    that matplotlib, which needs about a hundred, never rendered anything.

    `until` exists because a re-render is not always a render. The image cache
    is keyed on point size, so a size seen before is painted *synchronously*
    inside the font change and there is no job to wait for; the condition the
    caller actually cares about is that the bitmap changed, not that a worker
    ran.
    """
    import time

    from PySide6.QtCore import QThreadPool

    done = until or (lambda: label.is_typeset)
    started = time.perf_counter()
    deadline = started + timeout
    while time.perf_counter() < deadline:
        qapp.processEvents()
        if done():
            return
        QThreadPool.globalInstance().waitForDone(50)

    # Pump once more and then *check*. The previous version pumped and threw
    # the result away, so a render landing on that last pass -- or a budget
    # that had already expired before the first one -- failed a condition that
    # was true. That is not hypothetical: with the condition hard-coded to
    # True and the timeout to zero, the old helper still raised.
    #
    # It is also the shape of the only failure this file has ever had. Both
    # tests that failed under `-n 4` were the two passing `until=`, which are
    # the re-render cases and the slowest here; neither reproduces alone, with
    # its real predecessors, or under deliberate parallel load.
    qapp.processEvents()
    if done():
        return

    waited = time.perf_counter() - started
    pending = not QThreadPool.globalInstance().waitForDone(0)
    # The state that decides which of the two it is. An idle pool with an
    # unchanged bitmap means the font change never reached the label, so the
    # application font is the thing to look at -- and this failure has only
    # ever been seen in a whole-suite run, where that state is whatever three
    # thousand earlier tests left behind.
    point = qapp.font().pointSizeF() if qapp is not None else float("nan")
    raise AssertionError(
        f"the equation never settled: waited {waited:.1f}s of a {timeout:g}s "
        f"budget, with a render job still {'pending' if pending else 'finished'}; "
        f"bitmap {_height(label)}px, typeset={getattr(label, 'is_typeset', '?')}, "
        f"application font {point:g}pt against a {theme.BASELINE_POINT_SIZE:g}pt "
        f"baseline. A finished job with an unchanged bitmap means the condition "
        f"is wrong, not the budget."
    )


def test_the_render_cache_distinguishes_the_two_sizes(qapp, at_scale):
    """The cache is keyed on point size, so the two scales cannot collide --
    which is what would produce a correctly-sized layout around a bitmap of
    the wrong size."""
    mathrender.clear_cache()
    for factor in (1.0, 2.0):
        at_scale(factor)
        label = MathLabel(PALETTE, "y = t^{2}", point_size=15.0)
        _settle(qapp, label)
        label.deleteLater()
    assert mathrender.cache_size() >= 2
