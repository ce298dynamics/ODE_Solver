"""Unit 8, held to the tools it teaches.

Every drill in the nonlinear unit stores its answer as an expression over the
slots, and every one of those expressions is checked here, draw by draw,
against the routine in the application that would decide the same question:
`analysis.jacobian_at`, `find_fixed_points`, `largest_closed_orbit`, an
integration. The figures make measured claims in their readouts, and those
are checked here too, by moving the sliders and reading what comes back.
"""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("sympy", reason="the app extra is not installed")

from odesuite import ODEProblem, solve
from odesuite_app import analysis
from odesuite_app.lessons import by_key, generate, unit_by_key


def _template(lesson: str, key: str):
    for template in by_key(lesson).templates:
        if template.key == key:
            return template
    raise KeyError(key)


def _planar(f) -> ODEProblem:
    return ODEProblem(f=f, t_span=(0.0, 1.0), y0=np.array([0.1, 0.1]))


def test_the_unit_is_in_the_course_between_systems_and_series():
    from odesuite_app.lessons import UNITS

    keys = [unit.key for unit in UNITS]
    assert keys.index("systems") < keys.index("nonlinear") < keys.index("series")
    unit = unit_by_key("nonlinear")
    assert len(unit.lessons) == 6
    assert all(lesson.tool == "portrait" for lesson in unit.lessons)


# ---------------------------------------------------------------------------
# The drills, against their oracles
# ---------------------------------------------------------------------------


def test_the_coexistence_determinant_is_the_jacobians():
    template = _template("nonlinear-equilibria", "coexistence-determinant")
    for index, slots in enumerate(generate.draws(template)):
        question = generate.draw(template, index)
        a, c = float(slots["a"]), float(slots["c"])
        problem = _planar(lambda t, y: np.array([a * y[0] - y[0] * y[1],
                                                 y[0] * y[1] - c * y[1]]))
        point = np.array([c, a])
        assert np.allclose(problem.f(0.0, point), 0.0), "not an equilibrium"
        jacobian = analysis.jacobian_at(problem, point)
        assert question.answer == pytest.approx(np.linalg.det(jacobian), rel=1e-6)
        assert np.trace(jacobian) == pytest.approx(0.0, abs=1e-6), (
            "the because says the trace is zero")


def test_imaginary_eigenvalues_are_non_hyperbolic_and_really_undecided():
    """The drill's answer is "nothing definite". The oracle for that is two
    systems with the same imaginary pair at the origin that do opposite
    things -- which is the figure's system at a = +0.1 and a = -0.1."""
    template = _template("almost-linear", "centre-undecided")
    for slots in generate.draws(template):
        w = float(slots["w"])
        kind, stability = analysis.classify(np.array([1j * w, -1j * w]))
        assert (kind, stability) == ("centre", analysis.NEUTRAL)

    radii = []
    for a in (0.1, -0.1):
        def f(t, y, a=a):
            r2 = y[0] ** 2 + y[1] ** 2
            return np.array([-y[1] + a * y[0] * r2, y[0] + a * y[1] * r2])

        problem = _planar(f)
        values = np.linalg.eigvals(analysis.jacobian_at(problem, np.zeros(2)))
        assert analysis.classify(values)[0] == "centre"
        end = solve(ODEProblem(f=f, t_span=(0.0, 12.0), y0=np.array([0.5, 0.0])),
                    "dopri5", rtol=1e-9, atol=1e-12).y[:, -1]
        radii.append(float(np.hypot(*end)))
    assert radii[0] > 0.6 > 0.5 > 0.45 > radii[1], radii


def test_the_nullcline_crossing_is_an_equilibrium_the_portrait_finds():
    template = _template("ecological-models", "nullcline-crossing")
    for index, slots in enumerate(generate.draws(template)):
        question = generate.draw(template, index)
        p, r = float(slots["p"]), float(slots["r"])
        problem = _planar(lambda t, y: np.array([y[0] * (p - y[0] - y[1]),
                                                 y[1] * (r - y[0] - 2 * y[1])]))
        found = analysis.find_fixed_points(problem, (-0.5, 10.0), (-0.5, 10.0))
        interior = [point.position for point in found
                    if point.position[0] > 1e-6 and point.position[1] > 1e-6]
        assert len(interior) == 1, (question.prompt, interior)
        assert question.answer == pytest.approx(interior[0][0], abs=1e-8)


def test_the_peak_speed_is_what_an_integration_reaches():
    template = _template("nonlinear-mechanics", "peak-speed")
    for index, slots in enumerate(generate.draws(template)):
        question = generate.draw(template, index)
        k, amplitude = float(slots["k"]), float(slots["A"])
        found = solve(
            ODEProblem(f=lambda t, y: np.array([y[1], -k * y[0] ** 3]),
                       t_span=(0.0, 20.0), y0=np.array([amplitude, 0.0])),
            "dopri5", rtol=1e-10, atol=1e-12, dense_output=True,
        )
        speeds = np.abs(found.sol(np.linspace(0.0, 20.0, 20001))[1])
        assert question.answer == pytest.approx(float(speeds.max()), rel=1e-4)


@pytest.mark.slow
def test_the_cycle_radius_is_what_the_limit_cycle_finder_measures():
    template = _template("limit-cycles", "cycle-radius")
    for index, slots in enumerate(generate.draws(template)):
        question = generate.draw(template, index)
        mu = float(slots["mu"])

        def f(t, y, mu=mu):
            r2 = y[0] ** 2 + y[1] ** 2
            return np.array([mu * y[0] - y[1] - y[0] * r2,
                             y[0] + mu * y[1] - y[1] * r2])

        cycle = analysis.largest_closed_orbit(
            ODEProblem(f=f, t_span=(0.0, 1.0), y0=np.array([0.3, 0.0])))
        assert cycle.isolated, cycle.verdict
        assert question.answer == pytest.approx(cycle.diameter / 2.0, rel=1e-3)
        assert cycle.period == pytest.approx(2 * np.pi, rel=1e-4)


def test_the_hopf_value_is_where_the_trace_changes_sign():
    template = _template("bifurcations-chaos", "hopf-value")
    for index, slots in enumerate(generate.draws(template)):
        question = generate.draw(template, index)
        a = float(slots["a"])
        growth = []
        for b in (question.answer - 0.01, question.answer + 0.01):
            problem = _planar(lambda t, y, b=b: np.array([
                a - (b + 1) * y[0] + y[0] ** 2 * y[1],
                b * y[0] - y[0] ** 2 * y[1]]))
            point = np.array([a, b / a])
            assert np.allclose(problem.f(0.0, point), 0.0, atol=1e-12)
            values = np.linalg.eigvals(analysis.jacobian_at(problem, point))
            assert np.all(np.abs(values.imag) > 0.1), "not a complex pair"
            growth.append(float(np.max(values.real)))
        assert growth[0] < 0 < growth[1], (question.prompt, growth)


# ---------------------------------------------------------------------------
# The figures' measured claims
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def qapp():
    pytest.importorskip("PySide6", reason="the app extra is not installed")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def _figure(qapp, key: str):
    from odesuite_app.theme import PALETTES
    from odesuite_app.widgets.lessonfigure import build_figure

    made = build_figure(key, PALETTES["dark"])
    made.resize(700, 480)
    qapp.processEvents()
    return made


def test_zooming_in_makes_the_linearisation_agree(qapp):
    """The figure's whole claim is a limit, so it is measured at three sizes."""
    figure = _figure(qapp, "linearise")
    angles = []
    for half in (2.0, 0.5, 0.1):
        figure.sliders["window"].set_value(half, notify=True)
        angles.append(figure.worst_angle())
    assert angles[0] > angles[1] > angles[2]
    assert angles[2] < 1.0, angles
    figure.deleteLater()


def test_the_inverted_pendulum_linearises_to_a_saddle(qapp):
    figure = _figure(qapp, "linearise")
    figure.sliders["which"].set_value(1.0, notify=True)
    assert "saddle" in figure.readout.text()
    figure.deleteLater()


def test_the_almost_linear_figure_disagrees_with_its_linearisation(qapp):
    figure = _figure(qapp, "almost_linear")
    for value, word in ((0.1, "outwards"), (-0.1, "inwards"), (0.0, "closes")):
        figure.sliders["a"].set_value(value, notify=True)
        text = figure.readout.text()
        assert "a centre" in text, text
        assert word in text, text
    figure.deleteLater()


@pytest.mark.parametrize("a,b,word", [
    (0.5, 0.5, "both survive"),
    (1.5, 1.5, "depends on where you start"),
    (0.5, 1.5, "drives the other out"),
])
def test_the_competition_verdict_follows_the_coefficients(qapp, a, b, word):
    figure = _figure(qapp, "competition")
    figure.sliders["a"].set_value(a, notify=True)
    figure.sliders["b"].set_value(b, notify=True)
    assert word in figure.readout.text(), figure.readout.text()
    figure.deleteLater()


def test_the_pendulum_keeps_its_energy_until_damped(qapp):
    figure = _figure(qapp, "pendulum_energy")
    path = figure.launched()
    start = figure.energy(0.0, figure.value("speed"))
    assert figure.energy(path[0, -1], path[1, -1]) == pytest.approx(start, abs=1e-6)

    figure.sliders["damping"].set_value(0.3, notify=True)
    path = figure.launched()
    assert figure.energy(path[0, -1], path[1, -1]) < start - 0.5
    figure.deleteLater()


def test_the_pendulum_goes_over_the_top_only_above_speed_two(qapp):
    figure = _figure(qapp, "pendulum_energy")
    figure.sliders["speed"].set_value(1.9, notify=True)
    assert "without going over" in figure.readout.text()
    figure.sliders["speed"].set_value(2.1, notify=True)
    assert "goes over the top" in figure.readout.text()
    figure.deleteLater()


def test_both_trajectories_end_on_the_cycle_of_radius_root_mu(qapp):
    figure = _figure(qapp, "limit_cycle")
    for mu in (0.25, 0.81):
        figure.sliders["mu"].set_value(mu, notify=True)
        inner, outer = figure.final_radii()
        mu = figure.value("mu")
        assert inner == pytest.approx(np.sqrt(mu), rel=1e-3)
        assert outer == pytest.approx(np.sqrt(mu), rel=1e-3)
    figure.sliders["mu"].set_value(-0.3, notify=True)
    assert max(figure.final_radii()) < 0.01
    figure.deleteLater()


def test_the_pitchfork_branches_sit_at_root_r(qapp):
    figure = _figure(qapp, "normal_forms")
    figure.sliders["form"].set_value(2.0, notify=True)
    figure.sliders["r"].set_value(0.64, notify=True)
    r = figure.value("r")
    stable = sorted(value for rr, value, s in figure.diagram()
                    if s == analysis.STABLE and abs(rr - 1.0) < 1e-9)
    assert stable == pytest.approx([-1.0, 1.0], abs=1e-6)
    assert f"{np.sqrt(r):.3f}" in figure.readout.text()
    figure.deleteLater()
