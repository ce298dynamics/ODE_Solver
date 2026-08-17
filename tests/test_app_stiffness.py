"""The Stiffness Explorer and Method Race screens."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("PySide6", reason="the app extra is not installed")

from PySide6.QtCore import QThreadPool  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from odesuite_app.state import SessionState  # noqa: E402
from odesuite_app.theme import PALETTES  # noqa: E402

PALETTE = PALETTES["dark"]


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def _settle(qapp, timeout: int = 240_000) -> None:
    """Drain the thread pool, including jobs queued by earlier jobs' signals.

    The stiffness screen chains work: the eigenvalue track finishes, its
    signal is delivered on the main thread, and *that* starts the stability
    grid job -- which a single `waitForDone` would already have missed.
    """
    for _ in range(4):
        QThreadPool.globalInstance().waitForDone(timeout)
        for _ in range(25):
            qapp.processEvents()


# ---------------------------------------------------------------------------
# Eigenvalue track
# ---------------------------------------------------------------------------


def test_eigenvalue_track_follows_the_solve():
    """``h*lambda`` at each accepted step, from a finished solution.

    Computed after the fact rather than instrumented into the solver, so the
    library needs no hooks for the interface to visualise it.
    """
    from odesuite import solve
    from odesuite.problems import van_der_pol
    from odesuite_app.screens.stiffness import eigenvalue_track

    bench = van_der_pol(mu=30.0, t_end=40.0)
    solution = solve(bench.problem, method="dopri5", rtol=1e-6, atol=1e-9)
    track = eigenvalue_track(bench.problem, solution)

    assert track, "no eigenvalues recovered"
    for t, h, values in track[:20]:
        assert np.isfinite(t) and h > 0
        assert values.shape == (2,), "two eigenvalues for a 2-component system"

    times = [t for t, _h, _v in track]
    assert times == sorted(times), "the track must follow the solve in order"


def test_stiff_eigenvalue_presses_against_the_explicit_boundary():
    """The core claim of the screen, checked numerically.

    On a stiff problem an explicit method is stability-limited, so the product
    ``h*lambda`` should sit close to the edge of the stability region rather
    than comfortably inside it. DOPRI5's real-axis limit is about 3.3.
    """
    from odesuite import solve
    from odesuite.problems import van_der_pol
    from odesuite_app.screens.stiffness import eigenvalue_track

    bench = van_der_pol(mu=60.0, t_end=60.0)
    solution = solve(bench.problem, method="dopri5", rtol=1e-6, atol=1e-9,
                     max_steps=200_000)
    track = eigenvalue_track(bench.problem, solution)

    worst = max(
        float(np.max(np.abs(h * values))) for _t, h, values in track
    )
    assert 1.5 < worst < 4.5, (
        f"largest |h*lambda| was {worst:.2f}; an explicit method on a stiff "
        f"problem should be pinned near its stability boundary (~3.3)"
    )


def test_implicit_method_is_not_stability_limited():
    """Radau should push ``h*lambda`` far beyond anything explicit could take."""
    from odesuite import solve
    from odesuite.problems import van_der_pol
    from odesuite_app.screens.stiffness import eigenvalue_track

    bench = van_der_pol(mu=60.0, t_end=60.0)
    solution = solve(bench.problem, method="radau", rtol=1e-6, atol=1e-9)
    track = eigenvalue_track(bench.problem, solution)

    worst = max(float(np.max(np.abs(h * values))) for _t, h, values in track)
    assert worst > 20.0, (
        f"largest |h*lambda| was only {worst:.2f}; an A-stable method should "
        f"go far outside any explicit region"
    )


# ---------------------------------------------------------------------------
# The screen
# ---------------------------------------------------------------------------


@pytest.fixture
def stiffness(qapp):
    from odesuite_app.screens.stiffness import StiffnessScreen

    screen = StiffnessScreen(SessionState(), PALETTE)
    _settle(qapp)
    yield screen
    screen.deleteLater()


def test_screen_builds_a_track_and_a_region(stiffness, qapp):
    assert stiffness._track, "no eigenvalue track computed"
    assert stiffness.scrub.maximum() == len(stiffness._track) - 1
    assert hasattr(stiffness, "_eigen_marks"), "no stability region rendered"


def test_verdict_distinguishes_a_stable_from_bounded(stiffness, qapp):
    stiffness._method = "dopri5"
    stiffness.method_picker.setCurrentText("dopri5")
    stiffness._recompute()
    _settle(qapp)
    assert "not A-stable" in stiffness.verdict.text()
    assert "bounded" in stiffness.region_title.text()

    stiffness._method = "radau"
    stiffness.method_picker.setCurrentText("radau")
    stiffness._recompute()
    _settle(qapp)
    assert "is A-stable" in stiffness.verdict.text()
    assert "A-stable" in stiffness.region_title.text()


def test_scrubbing_moves_through_the_track(stiffness, qapp):
    assert stiffness._track
    stiffness._on_scrub(0)
    first = stiffness.readout.text()
    stiffness._on_scrub(len(stiffness._track) - 1)
    last = stiffness.readout.text()
    assert first != last
    assert "hλ" in last and "t =" in last


def test_playback_advances_and_stops_at_the_end(stiffness, qapp):
    assert stiffness._track
    stiffness._frame = len(stiffness._track) - 2
    stiffness._toggle_play()
    assert stiffness._timer.isActive()
    stiffness._advance()
    stiffness._advance()
    assert not stiffness._timer.isActive(), "playback should stop at the end"
    assert stiffness._frame == len(stiffness._track) - 1


def test_pde_problems_are_excluded(stiffness):
    """Their Jacobians are too large to diagonalise per step."""
    offered = {
        stiffness.problem_picker.itemData(i)
        for i in range(stiffness.problem_picker.count())
    }
    for key in ("kuramoto_sivashinsky", "allen_cahn"):
        assert key not in offered


@pytest.mark.slow
def test_method_list_is_filtered_to_what_can_run(stiffness, qapp):
    index = stiffness.problem_picker.findData("robertson")
    stiffness.problem_picker.setCurrentIndex(index)
    stiffness._on_problem(index)
    _settle(qapp)

    offered = {
        stiffness.method_picker.itemText(i)
        for i in range(stiffness.method_picker.count())
    }
    assert "radau" in offered
    assert offered, "no methods offered"


# ---------------------------------------------------------------------------
# Method Race
# ---------------------------------------------------------------------------


@pytest.fixture
def race(qapp):
    from odesuite_app.screens.race import RaceScreen

    screen = RaceScreen(SessionState(), PALETTE)
    yield screen
    screen.deleteLater()


def _run_race(race, qapp, key: str, methods: list[str], timeout: float = 240.0):
    import time

    index = race.problem_picker.findData(key)
    race.problem_picker.setCurrentIndex(index)
    race._on_problem(index)
    for method, box in race.checks.items():
        box.setChecked(method in methods and box.isEnabled())
    race._start()

    deadline = time.time() + timeout
    while race._pending > 0 and time.time() < deadline:
        qapp.processEvents()
        time.sleep(0.02)
    _settle(qapp)
    return race._results


def test_race_runs_every_selected_method(race, qapp):
    results = _run_race(race, qapp, "lotka_volterra", ["dopri5", "tsit5", "rk23"])
    assert set(results) == {"dopri5", "tsit5", "rk23"}
    assert all(r.ok for r in results.values())
    assert set(race._lanes) == set(results)


@pytest.mark.slow
def test_race_shows_an_explicit_method_failing_on_robertson(race, qapp):
    """The Phase 2 acceptance result, as a race.

    DOPRI5 must not merely lose -- it must run out of steps entirely, while the
    implicit methods finish.
    """
    results = _run_race(race, qapp, "robertson", ["dopri5", "radau", "rodas4"])

    assert results["radau"].ok and results["rodas4"].ok
    assert not results["dopri5"].ok
    assert "max_steps" in results["dopri5"].solution.message

    # And the implicit methods do it in a tiny fraction of the work.
    assert results["radau"].solution.stats.naccepted < 2000
    assert (
        results["dopri5"].solution.stats.naccepted
        > 50 * results["radau"].solution.stats.naccepted
    )


@pytest.mark.slow
def test_failed_competitor_still_reports_what_it_spent(race, qapp):
    """Reporting zero work for a failure would hide the whole point."""
    _run_race(race, qapp, "robertson", ["dopri5", "radau"])
    race._prepare_plot()
    for _ in range(30):
        race._advance()

    lane = race._lanes["dopri5"]
    text = lane.counters.text()
    assert "✗" in text
    assert "0 steps" not in text
    assert "0 evals" not in text


def test_playback_fills_the_bars_of_finishers(race, qapp):
    _run_race(race, qapp, "lotka_volterra", ["dopri5", "tsit5"])
    race._prepare_plot()
    for _ in range(300):
        race._advance()

    for method in ("dopri5", "tsit5"):
        assert race._lanes[method].bar.value() == 1000, f"{method} did not finish"
        assert "✔" in race._lanes[method].counters.text()


def test_leaderboard_ranks_by_evaluations(race, qapp):
    results = _run_race(race, qapp, "lotka_volterra", ["rk23", "dopri5", "tsit5"])
    race._prepare_plot()
    text = race.leaderboard.text()

    order = [
        m for m, _ in sorted(
            results.items(), key=lambda kv: kv[1].solution.stats.nfev
        )
    ]
    positions = [text.index(method) for method in order]
    assert positions == sorted(positions), f"leaderboard is out of order: {text}"


def test_incompatible_methods_are_disabled(race, qapp):
    index = race.problem_picker.findData("linear_dae")
    race.problem_picker.setCurrentIndex(index)
    race._on_problem(index)

    # A DAE rules out every explicit method.
    for method in ("dopri5", "tsit5", "rk23", "taylor20"):
        assert not race.checks[method].isEnabled()
        assert not race.checks[method].isChecked()
    assert race.checks["radau"].isEnabled()


def test_race_with_nothing_selected_is_reported(race, qapp):
    for box in race.checks.values():
        box.setChecked(False)
    race._start()
    assert "select at least one" in race.status.text()
