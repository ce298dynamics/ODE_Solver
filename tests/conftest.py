"""Shared pytest configuration.

Qt is forced into its offscreen platform before PySide6 is imported anywhere, so
the interface tests run headlessly -- in CI, over SSH, and without stealing
focus by flashing windows onto the developer's screen.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# Qt no longer bundles fonts; under the offscreen platform it needs pointing at
# the system directory or every text metric collapses to zero.
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _generous_dsolve_timeout():
    """Give `dsolve` a longer budget for the duration of the test session.

    The product's 12 s is a UI-responsiveness figure -- how long the Symbolic
    tab may sit on "solving…" before giving up. It is not a claim about how long
    a closed form takes to find, and the tests that wait for one are asserting
    that it *lands*, not that it lands within the interface's patience.

    On an unloaded machine the two never differ. Under `pytest -n auto` the
    machine is oversubscribed, the subprocess misses a wall-clock deadline it
    would otherwise beat, and two equation-editor tests fail intermittently --
    which is why CI could not run in parallel.

    `test_unsolvable_equations_time_out_rather_than_hang` passes its own
    explicit timeout and so is unaffected: it must still prove the deadline
    bites.
    """
    try:
        from odesuite_app import symbolic
    except ImportError:                      # the app extra is not installed
        yield
        return

    original = symbolic.DSOLVE_TIMEOUT
    symbolic.DSOLVE_TIMEOUT = 90.0
    try:
        yield
    finally:
        symbolic.DSOLVE_TIMEOUT = original
