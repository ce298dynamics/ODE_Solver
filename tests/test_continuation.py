"""Parameter continuation: the bifurcation diagram, checked against closed forms.

Every bifurcation asserted here has an exact location known on paper -- the
fold of ``x' = mu - x^2`` at zero, the Brusselator's Hopf at ``b = 1 + a^2``,
Duffing's pitchfork at ``alpha = 0``, the harvested population's fold at
``H = rK/4``. That is the point of choosing these four: a continuation routine
that is merely self-consistent can be confidently wrong, and none of these can.

The negative cases matter as much. A damped pendulum's damping slider passes
through no bifurcation at all, and a routine that finds one there is finding
noise.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import ODEProblem
from odesuite_app import catalog, continuation
from odesuite_app.analysis import STABLE, UNSTABLE

# ---------------------------------------------------------------------------
# Systems with a bifurcation at a known place
# ---------------------------------------------------------------------------


def saddle_node_problem(mu: float) -> ODEProblem:
    """``x' = mu - x^2``: no equilibria below zero, two above."""
    return ODEProblem(
        f=lambda t, y: np.array([mu - y[0] ** 2]),
        t_span=(0.0, 1.0),
        y0=[0.5],
        jac=lambda t, y: np.array([[-2.0 * y[0]]]),
    )


def transcritical_problem(mu: float) -> ODEProblem:
    """``x' = mu x - x^2``: two branches that cross and swap stability at zero."""
    return ODEProblem(
        f=lambda t, y: np.array([mu * y[0] - y[0] ** 2]),
        t_span=(0.0, 1.0),
        y0=[0.5],
        jac=lambda t, y: np.array([[mu - 2.0 * y[0]]]),
    )


def brusselator_problem(a: float, b: float) -> ODEProblem:
    """The Brusselator at an arbitrary `a`, which the catalogue slider fixes."""
    return ODEProblem(
        f=lambda t, y: np.array(
            [a + y[0] ** 2 * y[1] - (b + 1) * y[0], b * y[0] - y[0] ** 2 * y[1]]
        ),
        t_span=(0.0, 20.0),
        y0=[1.5, 3.0],
        jac=lambda t, y: np.array(
            [
                [2 * y[0] * y[1] - (b + 1), y[0] ** 2],
                [b - 2 * y[0] * y[1], -(y[0] ** 2)],
            ]
        ),
    )


# ---------------------------------------------------------------------------
# The fold
# ---------------------------------------------------------------------------


def test_saddle_node_has_two_branches_meeting_at_zero():
    diagram = continuation.continue_equilibria(
        saddle_node_problem, np.linspace(-1.0, 1.0, 81), ((-2.0, 2.0),),
        parameter="mu",
    )

    assert len(diagram.branches) == 2

    folds = diagram.of_kind(continuation.SADDLE_NODE)
    assert len(folds) == 1
    assert abs(folds[0].parameter) < 1e-4


def test_saddle_node_upper_branch_is_stable_and_lower_is_not():
    diagram = continuation.continue_equilibria(
        saddle_node_problem, np.linspace(-1.0, 1.0, 81), ((-2.0, 2.0),),
        parameter="mu",
    )

    upper = max(diagram.branches, key=lambda b: b.coordinate()[-1])
    lower = min(diagram.branches, key=lambda b: b.coordinate()[-1])

    # x = +sqrt(mu) has f'(x) = -2 sqrt(mu) < 0, and x = -sqrt(mu) the reverse.
    assert set(upper.stabilities) == {STABLE}
    assert set(lower.stabilities) == {UNSTABLE}
    assert upper.coordinate()[-1] == pytest.approx(1.0, abs=1e-6)
    assert lower.coordinate()[-1] == pytest.approx(-1.0, abs=1e-6)


def test_no_equilibria_exist_below_the_fold():
    diagram = continuation.continue_equilibria(
        saddle_node_problem, np.linspace(-1.0, 1.0, 81), ((-2.0, 2.0),),
        parameter="mu",
    )
    for branch in diagram.branches:
        assert branch.parameters.min() >= -1e-9


def test_harvested_population_folds_at_rK_over_four():
    entry = catalog.get("harvested_population")
    diagram = continuation.sweep(entry, "harvest", 0.0, 300.0, steps=81)

    folds = diagram.of_kind(continuation.SADDLE_NODE)
    assert len(folds) == 1
    # r = 0.6, K = 1000 by default, so the equilibria collide at 150.
    assert folds[0].parameter == pytest.approx(150.0, rel=1e-4)


# ---------------------------------------------------------------------------
# Hopf
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("a", [0.8, 1.0, 1.5])
def test_brusselator_loses_stability_at_one_plus_a_squared(a):
    expected = 1.0 + a * a
    diagram = continuation.continue_equilibria(
        lambda b: brusselator_problem(a, b),
        np.linspace(0.5, expected + 2.0, 81),
        ((a - 1.0, a + 1.0), (-1.0, expected + 3.0)),
        parameter="b",
    )

    hopfs = diagram.of_kind(continuation.HOPF)
    assert len(hopfs) == 1
    assert hopfs[0].parameter == pytest.approx(expected, rel=0.01)


def test_brusselator_equilibrium_sits_at_a_and_b_over_a():
    diagram = continuation.sweep(catalog.get("brusselator"), "b", 0.5, 6.0, steps=41)

    assert len(diagram.branches) == 1
    branch = diagram.branches[0]
    # a = 1 by default, so the equilibrium is (1, b) throughout.
    assert branch.coordinate(0) == pytest.approx(np.ones(len(branch)), abs=1e-8)
    assert branch.coordinate(1) == pytest.approx(branch.parameters, abs=1e-8)


def test_the_brusselator_crossing_is_oscillatory_and_named_hopf():
    diagram = continuation.sweep(catalog.get("brusselator"), "b", 0.5, 6.0, steps=41)

    assert [b.kind for b in diagram.bifurcations] == [continuation.HOPF]
    assert "periodic orbit" in diagram.bifurcations[0].detail


# ---------------------------------------------------------------------------
# Pitchfork and transcritical
# ---------------------------------------------------------------------------


def test_duffing_pitchforks_at_alpha_zero():
    diagram = continuation.sweep(catalog.get("duffing"), "alpha", -2.0, 1.0, steps=81)

    pitchforks = diagram.of_kind(continuation.PITCHFORK)
    assert len(pitchforks) == 1
    assert abs(pitchforks[0].parameter) < 1e-4


def test_duffing_has_three_branches_below_and_one_above():
    diagram = continuation.sweep(catalog.get("duffing"), "alpha", -2.0, 1.0, steps=81)

    assert len(diagram.branches) == 3
    at_bottom = [b for b in diagram.branches if b.parameters.min() == pytest.approx(-2.0)]
    reaching_top = [b for b in diagram.branches if b.parameters.max() == pytest.approx(1.0)]
    assert len(at_bottom) == 3
    assert len(reaching_top) == 1

    # The outer pair sits at x = +-sqrt(-alpha/beta), which is +-sqrt(2) here.
    outer = sorted(b.coordinate()[0] for b in diagram.branches)
    assert outer == pytest.approx([-np.sqrt(2.0), 0.0, np.sqrt(2.0)], abs=1e-6)


def test_the_duffing_outer_pair_is_not_reported_as_a_fold():
    """Both outer branches are stable, and two attractors cannot annihilate."""
    diagram = continuation.sweep(catalog.get("duffing"), "alpha", -2.0, 1.0, steps=81)
    assert diagram.of_kind(continuation.SADDLE_NODE) == []


def test_transcritical_branches_cross_without_either_ending():
    diagram = continuation.continue_equilibria(
        transcritical_problem, np.linspace(-1.0, 1.0, 81), ((-2.0, 2.0),),
        parameter="mu",
    )

    named = {b.kind for b in diagram.bifurcations}
    assert continuation.SADDLE_NODE not in named
    assert diagram.bifurcations, "the crossing at mu = 0 should be reported"
    for found in diagram.bifurcations:
        assert abs(found.parameter) < 1e-3


# ---------------------------------------------------------------------------
# Not finding what is not there
# ---------------------------------------------------------------------------


def test_the_damped_pendulum_has_no_bifurcation_in_its_damping():
    """Damping moves the eigenvalues but never across the imaginary axis.

    The origin is a stable spiral for every positive damping and the saddle
    stays a saddle, so a routine reporting a bifurcation here is reporting
    noise. Started just above zero because the undamped case is a centre --
    genuinely non-hyperbolic, and a boundary rather than a crossing.
    """
    diagram = continuation.sweep(catalog.get("pendulum"), "damping", 0.05, 2.0,
                                 steps=41)
    assert diagram.bifurcations == []


def test_a_constant_system_yields_one_flat_branch():
    def linear(mu):
        return ODEProblem(
            f=lambda t, y: np.array([-y[0]]),
            t_span=(0.0, 1.0), y0=[1.0],
            jac=lambda t, y: np.array([[-1.0]]),
        )

    diagram = continuation.continue_equilibria(
        linear, np.linspace(0.0, 1.0, 21), ((-2.0, 2.0),), parameter="mu")

    assert len(diagram.branches) == 1
    assert diagram.branches[0].coordinate() == pytest.approx(np.zeros(21), abs=1e-9)
    assert diagram.bifurcations == []


# ---------------------------------------------------------------------------
# Saying when the answer is about the box rather than the system
# ---------------------------------------------------------------------------


def test_a_branch_leaving_the_window_is_reported_as_clipped():
    diagram = continuation.sweep(catalog.get("brusselator"), "b", 0.5, 6.0, steps=41,
                                 window=((0.8, 1.7), (-0.4, 4.0)))

    # The equilibrium is at (1, b), so it leaves a box that stops at y = 4.
    assert diagram.clipped is True
    assert diagram.branches[0].parameters.max() < 6.0


def test_the_automatic_window_is_wide_enough_not_to_clip():
    diagram = continuation.sweep(catalog.get("brusselator"), "b", 0.5, 6.0, steps=41)

    assert diagram.clipped is False
    assert diagram.branches[0].parameters.max() == pytest.approx(6.0)


def test_the_method_note_admits_what_continuation_cannot_do():
    diagram = continuation.sweep(catalog.get("duffing"), "alpha", -2.0, 1.0, steps=21)
    assert "turn back" in diagram.method_note


# ---------------------------------------------------------------------------
# The interface around it
# ---------------------------------------------------------------------------


def test_sweep_defaults_to_the_sliders_own_range():
    entry = catalog.get("brusselator")
    spec = next(s for s in entry.params if s.name == "b")

    diagram = continuation.sweep(entry, "b", steps=21)

    assert diagram.lo == pytest.approx(spec.low)
    assert diagram.hi == pytest.approx(spec.high)
    assert diagram.parameter == spec.label


def test_sweep_rejects_a_parameter_the_entry_does_not_have():
    with pytest.raises(KeyError, match="no parameter"):
        continuation.sweep(catalog.get("brusselator"), "nonesuch", steps=5)


def test_sweep_rejects_an_empty_range():
    with pytest.raises(ValueError, match="empty parameter range"):
        continuation.sweep(catalog.get("brusselator"), "b", 3.0, 3.0, steps=5)


def test_should_stop_cuts_the_sweep_short():
    calls = {"n": 0}

    def stop():
        calls["n"] += 1
        return calls["n"] > 5

    diagram = continuation.continue_equilibria(
        saddle_node_problem, np.linspace(-1.0, 1.0, 81), ((-2.0, 2.0),),
        parameter="mu", should_stop=stop,
    )
    total = sum(len(b) for b in diagram.branches)
    assert total < 81


def test_segments_tile_the_branch_without_a_gap():
    diagram = continuation.sweep(catalog.get("brusselator"), "b", 0.5, 6.0, steps=41)
    branch = diagram.branches[0]

    segments = branch.segments()
    assert len(segments) == 2, "stable then unstable"
    assert segments[0][1] == 0
    assert segments[-1][2] == len(branch)
    # Consecutive runs share a sample, so the drawn curve has no break at the
    # change of style.
    assert segments[1][1] == segments[0][2] - 1


def test_branch_point_growth_and_oscillation_agree_with_the_eigenvalues():
    diagram = continuation.sweep(catalog.get("brusselator"), "b", 0.5, 6.0, steps=21)
    for point in diagram.branches[0].points:
        assert point.growth == pytest.approx(float(np.max(point.eigenvalues.real)))
        assert point.oscillatory == bool(
            abs(point.eigenvalues[np.argmax(point.eigenvalues.real)].imag) > 1e-8
        )


def test_equilibria_at_finds_all_three_duffing_rest_states():
    problem = catalog.get("duffing").build({"alpha": -1.0}).problem
    found = continuation.equilibria_at(problem, ((-2.0, 2.0), (-1.0, 1.0)))

    assert [round(p.position[0], 6) for p in found] == [-1.0, 0.0, 1.0]
    assert [p.kind for p in found] == ["stable spiral", "saddle", "stable spiral"]
