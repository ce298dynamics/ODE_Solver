"""The textbook models, and the screen that presents them.

Every other problem in the catalogue is there because it is hard on an
integrator. These are there because they are what a first course is about, and
they are held to the same standard as the rest: each constructs, solves, and
where it has a closed form agrees with the numeric solution.

The closed forms are the part worth checking hardest. A wrong one would not
crash -- it would quietly make the Methods-by-Hand error column, which exists to
teach, report a number that means nothing. `spring_mass_damper` gets the most
attention because it branches on the damping ratio, and the critically damped
branch is exactly where this project has a recorded bug (#9).
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import solve
from odesuite.problems import TEXTBOOK, all_benchmarks, spring_mass_damper

FACTORIES = [(f.__name__, f) for f in TEXTBOOK]
IDS = [name for name, _ in FACTORIES]


# ---------------------------------------------------------------------------
# The models
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name,factory", FACTORIES, ids=IDS)
def test_every_model_solves(name, factory):
    bench = factory()
    sol = solve(bench.problem, "dopri5", rtol=1e-10, atol=1e-12)
    assert sol.success, f"{name}: {sol.message}"
    assert np.all(np.isfinite(sol.y))


@pytest.mark.parametrize("name,factory", FACTORIES, ids=IDS)
def test_every_model_says_where_it_comes_from(name, factory):
    """These exist to be read, so an empty description is a real defect."""
    bench = factory()
    assert len(bench.description) > 40, f"{name} has no description worth reading"
    assert "textbook" in bench.tags


@pytest.mark.parametrize("name,factory", FACTORIES, ids=IDS)
def test_the_closed_form_agrees_with_the_numeric_solution(name, factory):
    """Two independent routes to the same trajectory, checked across the whole
    interval rather than only at the endpoint."""
    bench = factory()
    if bench.exact is None:
        pytest.skip(f"{name} has no elementary closed form")

    sol = solve(bench.problem, "dopri5", rtol=1e-11, atol=1e-13, dense_output=True)
    times = np.linspace(bench.problem.t0, bench.problem.tf, 60)
    truth = np.asarray([bench.exact(t) for t in times]).T
    error = float(np.max(np.abs(sol.y_at(times) - truth)))
    assert error < 1e-8, f"{name}: closed form and numeric solution differ by {error:.2e}"


@pytest.mark.parametrize("name,factory", FACTORIES, ids=IDS)
def test_the_analytic_jacobian_matches_a_differenced_one(name, factory):
    """Each of these supplies `jac`; a wrong one is invisible on an explicit
    method and costs Newton iterations on an implicit one."""
    bench = factory()
    problem = bench.problem
    y = problem.y0.astype(float) + 0.1
    t = problem.t0 + 0.1

    analytic = np.atleast_2d(problem.jac(t, y))
    step = 1e-6
    differenced = np.empty_like(analytic)
    base = problem.f(t, y)
    for j in range(problem.n):
        perturbed = y.copy()
        perturbed[j] += step
        differenced[:, j] = (problem.f(t, perturbed) - base) / step

    assert np.allclose(analytic, differenced, rtol=1e-4, atol=1e-6), (
        f"{name}: supplied Jacobian\n{analytic}\ndiffers from\n{differenced}"
    )


def test_the_models_join_the_shared_benchmark_sweep():
    """They are ordinary benchmarks, so the existing suite covers them too."""
    names = {bench.name for bench in all_benchmarks()}
    for factory in TEXTBOOK:
        assert factory().name in names


# ---------------------------------------------------------------------------
# The one with three regimes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "damping,regime",
    [(0.5, "under"), (4.0, "critical"), (10.0, "over")],
)
def test_spring_closed_form_holds_in_every_damping_regime(damping, regime):
    """m=1, k=4 puts critical damping at c = 2*sqrt(mk) = 4, so these three
    values land in the three branches of the closed form."""
    bench = spring_mass_damper(mass=1.0, damping=damping, stiffness=4.0)
    sol = solve(bench.problem, "dopri5", rtol=1e-12, atol=1e-14, dense_output=True)

    times = np.linspace(0.0, bench.problem.tf, 80)
    truth = np.asarray([bench.exact(t) for t in times]).T
    error = float(np.max(np.abs(sol.y_at(times) - truth)))
    assert error < 1e-8, f"{regime}-damped: error {error:.2e}"


@pytest.mark.parametrize("damping", [3.999, 4.0, 4.001])
def test_the_spring_is_continuous_across_the_critical_boundary(damping):
    """The closed form switches branch at zeta = 1. A branch that is subtly
    wrong shows up as a discontinuity here and nowhere else -- and the
    critically damped case is the one interesting point on the slider."""
    bench = spring_mass_damper(mass=1.0, damping=damping, stiffness=4.0)
    sol = solve(bench.problem, "dopri5", rtol=1e-12, atol=1e-14)
    endpoint = np.atleast_1d(bench.exact(bench.problem.tf)).reshape(-1)
    assert np.allclose(sol.y[:, -1], endpoint, atol=1e-9)


def test_the_three_regimes_actually_look_different():
    """Otherwise the parameter that selects them is not doing anything, and the
    problem teaches nothing."""

    def sign_changes(damping: float) -> int:
        bench = spring_mass_damper(mass=1.0, damping=damping, stiffness=4.0)
        sol = solve(bench.problem, "dopri5", rtol=1e-10, atol=1e-12,
                    dense_output=True)
        x = sol.y_at(np.linspace(0.0, bench.problem.tf, 400))[0]
        return int(np.sum(np.diff(np.sign(x)) != 0))

    assert sign_changes(0.5) >= 4, "under-damped should oscillate"
    assert sign_changes(4.0) <= 1, "critically damped should not oscillate"
    assert sign_changes(10.0) <= 1, "over-damped should not oscillate"


# ---------------------------------------------------------------------------
# The screen
# ---------------------------------------------------------------------------

pytest.importorskip("PySide6", reason="the app extra is not installed")


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


def test_every_model_reaches_the_worked_problems_screen(qapp):
    from odesuite_app.screens.learn_problems import WorkedProblemsScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    screen = WorkedProblemsScreen(SessionState(), PALETTES["dark"])
    assert screen.listing.count() == len(TEXTBOOK)

    for row in range(screen.listing.count()):
        screen.listing.setCurrentRow(row)
        qapp.processEvents()
        assert screen.title.text()
        assert screen.setup.text(), "a problem with no setup teaches nothing"
        assert screen.status.text()
    screen.deleteLater()


def test_the_screen_does_not_disturb_the_session(qapp):
    """It solves its own problem rather than through `SessionState`, so browsing
    the Learning Hub must not change what the Solver Studio is showing."""
    from odesuite_app.screens.learn_problems import WorkedProblemsScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    state = SessionState()
    state.set_problem("brusselator")

    screen = WorkedProblemsScreen(state, PALETTES["dark"])
    screen.listing.setCurrentRow(1)
    qapp.processEvents()

    assert state.problem_key == "brusselator"
    screen.deleteLater()


def test_the_models_are_ordinary_catalogue_entries(qapp):
    """Which is why they also appear in the Solver Studio's pickers: the content
    is shared even though this presentation of it is not."""
    from odesuite_app import catalog

    tagged = [k for k in catalog.keys() if "textbook" in catalog.get(k).tags]
    assert len(tagged) == len(TEXTBOOK)
    for key in tagged:
        entry = catalog.get(key)
        bench = entry.build(entry.defaults())
        assert bench.problem.n >= 1
        # The "copy as code" snippet must name a real factory.
        assert entry.code({}).startswith("problems.")
