"""Shared pytest configuration.

Qt is forced into its offscreen platform before PySide6 is imported anywhere, so
the interface tests run headlessly -- in CI, over SSH, and without stealing
focus by flashing windows onto the developer's screen.
"""

from __future__ import annotations

import os
import sys

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

    Raised again under coverage. `dsolve` runs in a subprocess, and measuring it
    makes that subprocess several times slower; combined with `-n auto` it
    misses even the 90 s budget, and a test that had nothing to do with
    coverage fails on the coverage leg only. That was reproduced deliberately --
    `-n auto` with `--cov` fails
    `test_a_technique_sympy_never_named_is_not_handed_back_to_dsolve`, which
    passes three times out of three in isolation under the same coverage. The
    deadline is a property of the interface, not of the mathematics, so
    stretching it for a slower harness costs nothing real.
    """
    try:
        from odesuite_app import symbolic
    except ImportError:                      # the app extra is not installed
        yield
        return

    measuring = "coverage" in sys.modules or "COV_CORE_SOURCE" in os.environ
    original = symbolic.DSOLVE_TIMEOUT
    symbolic.DSOLVE_TIMEOUT = 300.0 if measuring else 90.0
    try:
        yield
    finally:
        symbolic.DSOLVE_TIMEOUT = original


@pytest.fixture(scope="session", autouse=True)
def _private_diagnostics_log(tmp_path_factory):
    """Keep the failed-solve log (REL-04) out of the real per-user directory.

    Many tests fail a solve on purpose -- that is what they test -- and
    `SolveRunner` records every failure. Without this they would write into the
    developer's own per-user `diagnostics.log`, and a bug
    report pasted from it would be full of the suite's deliberate failures.
    """
    try:
        from odesuite_app import diagnostics
    except ImportError:
        yield
        return
    original = diagnostics.path
    log = tmp_path_factory.mktemp("diagnostics") / "diagnostics.log"
    diagnostics.path = lambda: log
    try:
        yield
    finally:
        diagnostics.path = original


@pytest.fixture(scope="session", autouse=True)
def _collect_garbage_on_the_main_thread():
    """Never let Python's collector run on a worker thread.

    Automatic collection runs on whichever thread allocates past a threshold.
    The screens under test start workers (the portrait's analysis, the
    typesetter, the solver), and a cycle holding a Qt object collected on one
    of them destroys it off the GUI thread. On the Linux runners, the runs
    without this hung near the end of the suite with renders left pending,
    which fits a render thread stuck in a collection; the runs with it did
    not hang.
    The application does the same through pyqtgraph's `GarbageCollector`
    (see `build_application`); most tests build screens directly, so the
    suite does it here, collecting between tests where the main thread is the
    only one doing anything.
    """
    import gc

    was_enabled = gc.isenabled()
    gc.disable()
    try:
        yield
    finally:
        if was_enabled:
            gc.enable()


@pytest.fixture(autouse=True)
def _collect_between_tests():
    """The collection automatic GC would have done, done here instead.

    Generation by generation against the usual thresholds, as pyqtgraph's
    collector does, so a test that made no garbage costs nothing extra.
    """
    yield
    import gc

    counts = gc.get_count()
    thresholds = gc.get_threshold()
    for generation in (2, 1, 0):
        if counts[generation] > thresholds[generation]:
            gc.collect(generation)
            break
