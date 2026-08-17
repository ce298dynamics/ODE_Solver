"""Thumbnail rendering, and the thread-safety it advertises.

`ensure_all` is documented as safe to call on a worker thread, and the home
screen does exactly that from a `QRunnable`. It was not safe: `render_thumbnail`
drove pyplot, whose figure registry is global, and called `matplotlib.use`,
which swaps the global backend. `mathrender._render` had already been moved off
pyplot for this reason; this module had not.

The concurrency test below is the honest kind -- it cannot *prove* the absence
of a race, but it does exercise the path that was unsafe, and it fails loudly
if the rendering ever goes back to shared global state that breaks under it.
"""

from __future__ import annotations

import concurrent.futures

import pytest

pytest.importorskip("matplotlib")

from odesuite_app import thumbnails  # noqa: E402
from odesuite_app.catalog import CATALOG  # noqa: E402
from odesuite_app.theme import PALETTES  # noqa: E402

PALETTE = PALETTES["dark"]


def _png_header_ok(data: bytes) -> bool:
    return data[:8] == b"\x89PNG\r\n\x1a\n"


def test_a_thumbnail_is_a_real_png():
    data = thumbnails.render_thumbnail(CATALOG["lotka_volterra"], PALETTE)
    assert _png_header_ok(data)
    assert len(data) > 1000, "suspiciously small for a rendered plot"


def test_rendering_does_not_import_pyplot():
    """The specific regression. pyplot's global figure registry is what made
    this unsafe off-thread, so its absence is the property worth pinning --
    checking for thread-safety directly is not something a test can do."""
    import sys

    sys.modules.pop("matplotlib.pyplot", None)
    thumbnails.render_thumbnail(CATALOG["van_der_pol"], PALETTE)
    assert "matplotlib.pyplot" not in sys.modules, (
        "render_thumbnail pulled in pyplot; its figure registry is global and "
        "this function runs on a worker thread"
    )


def test_concurrent_renders_all_succeed():
    """Four threads rendering at once, which is what the home screen's job pool
    can produce on a cold cache."""
    keys = ["lotka_volterra", "van_der_pol", "brusselator", "lorenz"]
    keys = [k for k in keys if k in CATALOG]

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(
            pool.map(lambda k: thumbnails.render_thumbnail(CATALOG[k], PALETTE), keys)
        )

    assert len(results) == len(keys)
    for key, data in zip(keys, results):
        assert _png_header_ok(data), f"{key} did not render to a PNG"


def test_both_palettes_render_and_differ():
    """The palette reaches the drawing, so the two themes must not produce the
    same bytes -- otherwise the cache key is doing nothing."""
    entry = CATALOG["lotka_volterra"]
    dark = thumbnails.render_thumbnail(entry, PALETTES["dark"])
    light = thumbnails.render_thumbnail(entry, PALETTES["light"])
    assert _png_header_ok(dark) and _png_header_ok(light)
    assert dark != light


def test_a_failing_problem_still_produces_a_card():
    """Documented behaviour: never break the grid. A problem that cannot be
    solved must come back as a picture saying so, not as an exception."""

    class Broken:
        key = "broken"
        plot_kind = "time"
        default_method = "dopri5"

        def defaults(self):
            return {}

        def build(self, params):
            raise RuntimeError("no such problem")

    data = thumbnails.render_thumbnail(Broken(), PALETTE)
    assert _png_header_ok(data)


def test_cache_paths_are_distinct_per_palette():
    entry = CATALOG["lotka_volterra"]
    assert thumbnails.thumbnail_path(entry, PALETTES["dark"]) != thumbnails.thumbnail_path(
        entry, PALETTES["light"]
    )
