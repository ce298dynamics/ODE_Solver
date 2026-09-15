"""Phase-plane analysis: equilibria, classification, manifolds.

This is mathematics rather than presentation, and it is checked against closed
forms wherever one exists. Whether a fixed point is a saddle or a spiral is
decided by the Jacobian's eigenvalues, so getting it wrong would be a wrong
answer, not an ugly picture.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite.problems import (
    brusselator,
    duffing,
    lotka_volterra,
    pendulum,
    van_der_pol,
)
from odesuite_app import analysis

# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "eigenvalues,kind,stability",
    [
        ([-1.0, -2.0], "stable node", analysis.STABLE),
        ([1.0, 2.0], "unstable node", analysis.UNSTABLE),
        ([-1.0, 2.0], "saddle", analysis.UNSTABLE),
        ([3.0, -0.5], "saddle", analysis.UNSTABLE),
        ([-1 + 2j, -1 - 2j], "stable spiral", analysis.STABLE),
        ([1 + 2j, 1 - 2j], "unstable spiral", analysis.UNSTABLE),
        ([2j, -2j], "centre", analysis.NEUTRAL),
        ([0.0, -1.0], "non-hyperbolic", analysis.NEUTRAL),
        ([0.0, 0.0], "non-hyperbolic", analysis.NEUTRAL),
    ],
)
def test_classification(eigenvalues, kind, stability):
    got_kind, got_stability = analysis.classify(np.array(eigenvalues))
    assert got_kind == kind
    assert got_stability == stability


def test_classification_is_scale_invariant():
    """A system scaled by 1e6 has the same qualitative structure."""
    for factor in (1e-6, 1.0, 1e6):
        kind, _ = analysis.classify(np.array([-1.0, 2.0]) * factor)
        assert kind == "saddle"


# ---------------------------------------------------------------------------
# Equilibria, against closed forms
# ---------------------------------------------------------------------------


def test_pendulum_equilibria_are_exact():
    """Centres at multiples of 2*pi, saddles at odd multiples of pi."""
    bench = pendulum(0.0)
    points = analysis.find_fixed_points(bench.problem, (-7.0, 7.0), (-3.0, 3.0))

    positions = sorted(p.position[0] for p in points)
    assert np.allclose(positions, [-2 * np.pi, -np.pi, 0.0, np.pi, 2 * np.pi], atol=1e-8)
    assert all(abs(p.position[1]) < 1e-9 for p in points)

    by_x = {round(p.position[0], 6): p for p in points}
    assert by_x[0.0].kind == "centre"
    assert by_x[round(np.pi, 6)].kind == "saddle"
    assert by_x[round(-np.pi, 6)].kind == "saddle"

    # The undamped saddle has eigenvalues exactly +-1.
    saddle = by_x[round(np.pi, 6)]
    assert np.allclose(sorted(saddle.eigenvalues.real), [-1.0, 1.0], atol=1e-9)


def test_damped_pendulum_eigenvalues_match_the_closed_form():
    """Spiral: -b/2 +- i*sqrt(1 - b^2/4). Saddle: (-b +- sqrt(b^2+4))/2."""
    b = 0.35
    bench = pendulum(b)
    points = analysis.find_fixed_points(bench.problem, (-4.0, 4.0), (-3.0, 3.0))
    by_x = {round(p.position[0], 6): p for p in points}

    spiral = by_x[0.0]
    assert spiral.kind == "stable spiral"
    assert np.allclose(spiral.eigenvalues.real, -b / 2, atol=1e-9)
    assert np.allclose(
        sorted(np.abs(spiral.eigenvalues.imag)),
        [np.sqrt(1 - b**2 / 4)] * 2, atol=1e-9,
    )

    saddle = by_x[round(np.pi, 6)]
    expected = sorted([(-b + np.sqrt(b**2 + 4)) / 2, (-b - np.sqrt(b**2 + 4)) / 2])
    assert np.allclose(sorted(saddle.eigenvalues.real), expected, atol=1e-9)


def test_lotka_volterra_centre_is_at_the_predicted_point():
    """Equilibria at the origin (saddle) and at (c/d, a/b) (a centre)."""
    a, b, c, d = 1.5, 1.0, 3.0, 1.0
    bench = lotka_volterra(a=a, b=b, c=c, d=d)
    points = analysis.find_fixed_points(bench.problem, (-1.0, 8.0), (-1.0, 5.0))
    by_position = {(round(p.position[0], 6), round(p.position[1], 6)): p for p in points}

    assert (0.0, 0.0) in by_position
    assert by_position[(0.0, 0.0)].kind == "saddle"

    interior = by_position[(round(c / d, 6), round(a / b, 6))]
    assert interior.kind == "centre"
    # Purely imaginary, with modulus sqrt(a*c).
    assert np.allclose(interior.eigenvalues.real, 0.0, atol=1e-9)
    assert np.allclose(
        sorted(np.abs(interior.eigenvalues.imag)), [np.sqrt(a * c)] * 2, atol=1e-9
    )


def test_duffing_pitchfork_bifurcation():
    """Three equilibria for alpha < 0, collapsing to one for alpha > 0."""
    before = analysis.find_fixed_points(
        duffing(-1.0, 1.0, 0.2).problem, (-2.0, 2.0), (-2.0, 2.0)
    )
    assert len(before) == 3
    assert sorted(p.kind for p in before) == [
        "saddle", "stable spiral", "stable spiral",
    ]
    assert np.allclose(sorted(p.position[0] for p in before), [-1, 0, 1], atol=1e-9)

    after = analysis.find_fixed_points(
        duffing(1.0, 1.0, 0.2).problem, (-2.0, 2.0), (-2.0, 2.0)
    )
    assert len(after) == 1
    assert after[0].kind == "stable spiral"


def test_van_der_pol_origin_is_an_unstable_spiral():
    """Eigenvalues mu/2 +- i*sqrt(1 - mu^2/4) for mu < 2."""
    mu = 1.0
    points = analysis.find_fixed_points(
        van_der_pol(mu).problem, (-3.0, 3.0), (-3.0, 3.0)
    )
    assert len(points) == 1
    assert points[0].kind == "unstable spiral"
    assert np.allclose(points[0].eigenvalues.real, mu / 2, atol=1e-9)


def test_brusselator_is_neutral_exactly_at_the_hopf_point():
    """At ``b = 1 + a^2`` the eigenvalues are purely imaginary.

    The linearisation decides nothing there, and reporting a definite
    stability would be a claim the mathematics does not support.
    """
    points = analysis.find_fixed_points(
        brusselator(1.0, 2.0).problem, (0.01, 4.0), (0.01, 5.0)
    )
    assert len(points) == 1
    assert points[0].stability == analysis.NEUTRAL
    assert np.allclose(points[0].eigenvalues.real, 0.0, atol=1e-9)


def test_brusselator_equilibrium_and_hopf_threshold():
    """The fixed point sits at (a, b/a) and destabilises once b > 1 + a^2.

    Tested either side of the threshold, not on it: at exactly ``b = 1 + a^2``
    the eigenvalues are purely imaginary and "neutral" is the right answer, so
    that value tests the Hopf point rather than the stability rule.
    """
    a = 1.0
    for b, expected_stability in [(1.5, analysis.STABLE), (3.0, analysis.UNSTABLE)]:
        points = analysis.find_fixed_points(
            brusselator(a, b).problem, (0.01, 4.0), (0.01, 5.0)
        )
        assert len(points) == 1
        assert np.allclose(points[0].position, [a, b / a], atol=1e-8)
        assert points[0].stability == expected_stability


def test_fixed_points_are_deduplicated():
    """Many Newton seeds converge to the same root; only one may be reported."""
    points = analysis.find_fixed_points(
        pendulum(0.0).problem, (-1.0, 1.0), (-1.0, 1.0), seeds=15
    )
    assert len(points) == 1


def test_no_equilibria_outside_the_window():
    points = analysis.find_fixed_points(
        pendulum(0.0).problem, (1.0, 2.5), (-1.0, 1.0)
    )
    assert points == []


def test_finite_difference_jacobian_matches_analytic():
    """The analysis must work on problems that supply no Jacobian."""
    from odesuite import ODEProblem

    bench = pendulum(0.3)
    without = ODEProblem(
        f=bench.problem.f_user,
        t_span=(0.0, 1.0),
        y0=bench.problem.y0,
    )
    point = np.array([0.7, -0.4])
    assert np.allclose(
        analysis.jacobian_at(without, point),
        analysis.jacobian_at(bench.problem, point),
        atol=1e-6,
    )


# ---------------------------------------------------------------------------
# Manifolds and trajectories
# ---------------------------------------------------------------------------


def test_pendulum_separatrix_lies_on_the_exact_energy_level():
    """The undamped separatrix is exactly the level set ``E = 1``.

    ``E = v^2/2 - cos(theta)`` equals 1 at the saddle ``(pi, 0)``, and the
    manifolds are invariant, so every point on them has that energy. It is a
    closed-form check on both the eigenvector directions and the integration.
    """
    bench = pendulum(0.0)
    points = analysis.find_fixed_points(bench.problem, (-4.0, 4.0), (-3.0, 3.0))
    saddle = next(p for p in points if p.is_saddle)

    curves = analysis.separatrices(bench.problem, saddle)
    assert len(curves) == 4, "a saddle has two branches of each manifold"

    for curve, _label in curves:
        energy = 0.5 * curve[:, 1] ** 2 - np.cos(curve[:, 0])
        assert np.allclose(energy, 1.0, atol=1e-6), (
            f"separatrix left its energy level: {energy.min()} to {energy.max()}"
        )


def test_separatrices_are_labelled_by_stability():
    bench = pendulum(0.0)
    saddle = next(
        p for p in analysis.find_fixed_points(bench.problem, (-4.0, 4.0), (-3.0, 3.0))
        if p.is_saddle
    )
    labels = sorted(label for _curve, label in analysis.separatrices(bench.problem, saddle))
    assert labels == ["stable", "stable", "unstable", "unstable"]


def test_non_saddles_have_no_separatrices():
    bench = pendulum(0.0)
    centre = next(
        p for p in analysis.find_fixed_points(bench.problem, (-1.0, 1.0), (-1.0, 1.0))
        if not p.is_saddle
    )
    assert analysis.separatrices(bench.problem, centre) == []


def test_trajectory_runs_both_ways_through_the_point():
    """Backward integration is what makes it the curve *through* the point."""
    bench = pendulum(0.0)
    seed = (0.6, 0.0)
    both = analysis.trajectory_through(bench.problem, seed, span=6.0, backward=True)
    forward = analysis.trajectory_through(bench.problem, seed, span=6.0, backward=False)

    assert both.shape[0] > forward.shape[0]
    # The seed must lie on the curve, not at one end of it.
    distances = np.linalg.norm(both - np.asarray(seed), axis=1)
    index = int(np.argmin(distances))
    assert distances[index] < 1e-6
    assert 0.2 * len(both) < index < 0.8 * len(both)


def test_trajectory_conserves_pendulum_energy():
    bench = pendulum(0.0)
    curve = analysis.trajectory_through(bench.problem, (0.9, 0.0), span=12.0)
    energy = 0.5 * curve[:, 1] ** 2 - np.cos(curve[:, 0])
    assert np.ptp(energy) < 1e-7


# ---------------------------------------------------------------------------
# Clipping and windows
# ---------------------------------------------------------------------------


def test_clipping_keeps_only_the_inside_runs():
    curve = np.array([[0.0, 0.0], [0.5, 0.5], [5.0, 5.0], [6.0, 6.0],
                      [0.6, 0.6], [0.7, 0.7]])
    pieces = analysis.clip_to_window(curve, (0.0, 1.0), (0.0, 1.0))
    assert len(pieces) == 2
    assert pieces[0][0].tolist() == [0.0, 0.0]

    # Every retained point lies inside the window, because the boundary
    # crossing is interpolated rather than approximated by a nearby sample.
    for piece in pieces:
        assert np.all(piece[:, 0] >= -1e-12) and np.all(piece[:, 0] <= 1 + 1e-12)
        assert np.all(piece[:, 1] >= -1e-12) and np.all(piece[:, 1] <= 1 + 1e-12)

    # The first run ends exactly on the edge of the box.
    assert max(pieces[0][-1]) == pytest.approx(1.0, abs=1e-12)


def test_clipping_handles_a_fully_outside_curve():
    curve = np.array([[5.0, 5.0], [6.0, 6.0]])
    assert analysis.clip_to_window(curve, (0.0, 1.0), (0.0, 1.0)) == []


def test_default_window_includes_nearby_equilibria():
    """Framing on one orbit alone hides the rest of the structure.

    A damped Duffing trajectory spirals into a single well and never visits the
    saddle or the other well, so the window has to be widened to the system's
    structure rather than to the orbit.
    """
    from odesuite import solve

    bench = duffing(-1.0, 1.0, 0.25)
    solution = solve(bench.problem, method="dopri5", rtol=1e-6, atol=1e-9)
    xlim, ylim = analysis.default_window(bench.problem, solution)

    for x in (-1.0, 0.0, 1.0):
        assert xlim[0] <= x <= xlim[1], f"equilibrium at x={x} is outside the window"
    assert ylim[0] < 0 < ylim[1]


# ---------------------------------------------------------------------------
# The whole picture
# ---------------------------------------------------------------------------


def test_analyse_produces_every_layer():
    bench = pendulum(0.0)
    data = analysis.analyse(bench.problem, (-4.0, 4.0), (-3.0, 3.0))

    assert data.streamlines, "no streamlines were extracted"
    assert all(len(path) > 2 for path in data.streamlines)
    assert data.nullcline_x and data.nullcline_y
    assert data.fixed_points
    assert data.separatrices
    assert data.speed_grid is not None and np.all(np.isfinite(data.speed_grid))


def test_analyse_asks_for_the_streamline_density_it_means():
    """PORT-01 -- `analyse` was passing its `resolution` into `density`.

    The two are different quantities that sat in adjacent parameter slots:
    `streamlines` samples the field on `STREAMLINE_RESOLUTION` and takes
    matplotlib's line-spacing `density` next, and `analyse` handed 33 to it
    positionally. Measured on the pendulum over the window the screen opens on,
    that cost 372.045 s and produced 4609 overlapping paths where the intended
    density takes 0.781 s and produces 90 -- a 476x slowdown, an unreadable
    picture, and the reason `tests/test_app_portrait.py` never finished.

    Asserted as a *count*, because a count is what separates the two settings
    and a wall-clock budget on a shared machine is not a fact about this code.
    Ninety-odd paths over this window; thirty times the density is thousands,
    so the threshold does not need to be delicate to catch the mistake coming
    back.
    """
    bench = pendulum(0.0)
    window = ((-10.8, 10.8), (-2.9, 2.9))
    data = analysis.analyse(bench.problem, *window)

    assert data.streamlines, "no streamlines were extracted"
    assert len(data.streamlines) < 500, (
        f"{len(data.streamlines)} streamline paths over this window: "
        "`analyse` is asking matplotlib for far more line density than "
        "`streamlines` defaults to, which is PORT-01 returning"
    )
    # The default really is the cheap one, and the expensive setting really is
    # the expensive one -- so the assertion above is discriminating rather than
    # merely true.
    assert len(analysis.streamlines(bench.problem, *window)) == \
        len(data.streamlines)


def test_the_streamline_density_cannot_be_passed_positionally():
    """What stops PORT-01 coming back: the two numbers can no longer be
    confused by position, only by name."""
    bench = pendulum(0.0)
    with pytest.raises(TypeError):
        analysis.streamlines(bench.problem, (-4.0, 4.0), (-3.0, 3.0), 33)


def test_analyse_respects_the_layer_switches():
    bench = pendulum(0.0)
    data = analysis.analyse(
        bench.problem, (-4.0, 4.0), (-3.0, 3.0),
        with_streamlines=False, with_nullclines=False, with_separatrices=False,
    )
    assert data.streamlines == []
    assert data.nullcline_x == [] and data.nullcline_y == []
    assert data.separatrices == []
    assert data.fixed_points, "equilibria are always computed"


def test_nullclines_pass_through_the_equilibria():
    """Every fixed point must sit on a crossing of the two nullclines."""
    bench = duffing(-1.0, 1.0, 0.2)
    xlim, ylim = (-2.0, 2.0), (-1.5, 1.5)
    x_curves, y_curves = analysis.nullclines(bench.problem, xlim, ylim)
    points = analysis.find_fixed_points(bench.problem, xlim, ylim)

    for point in points:
        for curves in (x_curves, y_curves):
            closest = min(
                np.min(np.linalg.norm(curve - point.position, axis=1))
                for curve in curves
            )
            assert closest < 0.06, (
                f"{point} is {closest:.3f} from the nearest nullcline"
            )


# ---------------------------------------------------------------------------
# The phase line
# ---------------------------------------------------------------------------


def _scalar(f, y0: float = 1.0):
    from odesuite import ODEProblem

    return ODEProblem(f=lambda t, y: np.array([f(y[0])]), t_span=(0.0, 1.0),
                      y0=np.array([float(y0)]))


def test_the_logistic_equilibria_are_the_two_it_should_have():
    """y' = r·y(1 - y/K): zero is unstable, the capacity is stable. Both are
    known exactly, so this is a closed form rather than a self-comparison."""
    found = analysis.phase_line(_scalar(lambda y: 0.8 * y * (1 - y / 5.0)),
                                (-3.0, 9.0))

    assert [point.value for point in found] == pytest.approx([0.0, 5.0],
                                                             abs=1e-8)
    assert [point.stability for point in found] == [analysis.UNSTABLE,
                                                    analysis.STABLE]
    # f'(0) = r and f'(K) = -r, which is the linearisation a course computes
    # beside the picture.
    assert [point.slope for point in found] == pytest.approx([0.8, -0.8],
                                                             abs=1e-6)


def test_a_cubic_alternates_stable_and_unstable():
    """y' = -(y+2)(y-1)(y-3). Three simple roots, and on a line the arrows
    have no choice but to alternate."""
    found = analysis.phase_line(
        _scalar(lambda y: -(y + 2) * (y - 1) * (y - 3)), (-5.0, 6.0),
    )

    assert [point.value for point in found] == pytest.approx([-2.0, 1.0, 3.0],
                                                             abs=1e-8)
    assert [point.stability for point in found] == [
        analysis.STABLE, analysis.UNSTABLE, analysis.STABLE,
    ]


def test_a_root_the_curve_only_touches_is_found_and_called_semi_stable():
    """y' = y² is the case that decides the method.

    There is no sign change to bracket, so scanning for one finds nothing, and
    f'(0) = 0 so the linearisation says nothing either. The equilibrium is
    real and it is semi-stable: solutions below it rise towards zero, and
    solutions above it run away.
    """
    found = analysis.phase_line(_scalar(lambda y: y**2), (-2.0, 2.0))

    assert len(found) == 1
    assert found[0].value == pytest.approx(0.0, abs=1e-6)
    assert found[0].slope == pytest.approx(0.0, abs=1e-6)
    assert found[0].stability == analysis.NEUTRAL
    assert found[0].is_semistable
    assert (found[0].below, found[0].above) == (1, 1)


def test_harvesting_past_the_fold_leaves_no_equilibrium_at_all():
    """y' = r·y(1 - y/K) - h. The parabola's maximum is r·K/4, so above that
    harvest rate f is negative everywhere and every population collapses.
    Checked either side of the fold, since the interesting claim is that the
    equilibria genuinely disappear rather than drift off the window."""
    r, k = 1.0, 6.0
    fold = r * k / 4.0

    below = analysis.phase_line(
        _scalar(lambda y: r * y * (1 - y / k) - (fold - 0.2)), (-2.0, 10.0))
    above = analysis.phase_line(
        _scalar(lambda y: r * y * (1 - y / k) - (fold + 0.2)), (-2.0, 10.0))

    assert len(below) == 2
    assert [point.stability for point in below] == [analysis.UNSTABLE,
                                                    analysis.STABLE]
    assert above == []


def test_equilibria_outside_the_window_are_not_reported():
    found = analysis.phase_line(_scalar(lambda y: y * (1 - y / 5.0)),
                                (1.0, 3.0))
    assert found == []


def test_a_phase_line_needs_a_scalar_equation():
    with pytest.raises(ValueError, match="scalar"):
        analysis.phase_line(lotka_volterra().problem, (0.0, 3.0))
