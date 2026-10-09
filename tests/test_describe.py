"""`describe`: the words a plot owes a reader who cannot see it.

The risk with a generated summary is not that it crashes, it is that it is
vacuous -- "the solution varies over time" is true of everything and worth
nothing. So the assertions here are about the *content* of the sentence for
three shapes a reader would describe differently: a decay, an oscillation, and
a blow-up. If the wording ever collapses into something that fits all three,
these fail.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite import ODEProblem, solve
from odesuite_app import describe


def _run(field, y0, t_end, **kwargs):
    problem = ODEProblem(f=field, t_span=(0.0, t_end),
                         y0=np.array(y0, dtype=float))
    return solve(problem, method="dopri5", rtol=1e-9, atol=1e-11, **kwargs)


@pytest.fixture(scope="module")
def decay():
    return _run(lambda t, y: -y, [1.0], 10.0)


@pytest.fixture(scope="module")
def oscillation():
    return _run(lambda t, y: np.array([y[1], -0.3 * y[1] - y[0]]),
                [1.0, 0.0], 40.0)


@pytest.fixture(scope="module")
def blowup():
    return _run(lambda t, y: y * y, [1.0], 2.0)


# ---------------------------------------------------------------------------
# The three shapes
# ---------------------------------------------------------------------------


def test_a_decay_is_described_as_one(decay):
    words = describe.summarise(decay, ("y",))
    assert "falls without turning back" in words
    assert "settles to" in words
    assert "oscillat" not in words


def test_an_oscillation_says_so_and_counts_its_turns(oscillation):
    words = describe.summarise(oscillation, ("x", "v"))
    assert "oscillates" in words
    assert "decaying amplitude" in words, words
    # The count is the part that could be vacuous, so it is asserted to be a
    # real number of swings rather than merely present.
    turns = [int(part) for part in words.split()
             if part.isdigit() and "turning" in words]
    assert any(turn >= 4 for turn in turns), words


def test_a_blow_up_reports_that_the_solver_stopped(blowup):
    words = describe.summarise(blowup, ("y",))
    assert "did not reach the end of the interval" in words
    assert "stopped at t =" in words
    assert "settles" not in words


def test_every_summary_names_the_endpoint_and_the_range(decay):
    """The two numbers a reader always wants, whatever the shape."""
    words = describe.summarise(decay, ("y",))
    assert "starts at 1" in words
    assert "stays between" in words


# ---------------------------------------------------------------------------
# The measurements behind the wording
# ---------------------------------------------------------------------------


def test_turning_points_do_not_depend_on_how_finely_it_was_sampled():
    """The first implementation of this was wrong in exactly this way.

    Counting sign changes of `diff` with small steps discarded compares one
    step against a fraction of the whole range, so a finely sampled curve has
    every step discarded and reports no turns at all. The shape of a solution
    is not allowed to depend on the solver's step size."""
    coarse = np.linspace(0.0, 40.0, 200)
    fine = np.linspace(0.0, 40.0, 20_000)
    shape = lambda t: np.exp(-0.15 * t) * np.cos(t)  # noqa: E731

    few = describe.component_summary(coarse, shape(coarse), "y")
    many = describe.component_summary(fine, shape(fine), "y")
    assert "oscillates" in few and "oscillates" in many
    assert few.split("turning")[1] == many.split("turning")[1], (
        f"the count changed with sampling:\n  {few}\n  {many}"
    )


def test_integrator_noise_is_not_reported_as_an_oscillation():
    t = np.linspace(0.0, 10.0, 4000)
    values = np.exp(-t) + 1e-12 * np.sin(500 * t)
    assert "oscillat" not in describe.component_summary(t, values, "y")


def test_a_component_that_never_moves_says_so():
    t = np.linspace(0.0, 5.0, 200)
    assert "holds steady" in describe.component_summary(t, np.full(200, 3.0),
                                                        "y")


def test_a_non_finite_component_is_named_where_it_stops():
    t = np.linspace(0.0, 4.0, 100)
    values = np.where(t < 2.0, 1.0, np.inf)
    words = describe.component_summary(t, values, "y")
    assert "stops being a number" in words and "t = 2" in words


# ---------------------------------------------------------------------------
# The table
# ---------------------------------------------------------------------------


def test_a_short_solution_keeps_every_row(decay):
    times, values = describe.table_rows(decay)
    assert times.size == decay.t.size
    assert np.array_equal(values, decay.y)


def test_a_long_solution_is_thinned_but_keeps_its_ends():
    class Fake:
        t = np.linspace(0.0, 1.0, 50_000)
        y = np.vstack([np.linspace(0.0, 1.0, 50_000)])

    times, values = describe.table_rows(Fake(), limit=1000)
    assert times.size <= 1001
    assert times[0] == pytest.approx(0.0)
    assert times[-1] == pytest.approx(1.0)
    # Every row is one the solver produced, not an interpolation between two.
    assert np.all(np.isin(times, Fake.t))


def test_a_complex_state_is_shown_as_its_real_part():
    class Fake:
        t = np.linspace(0.0, 1.0, 5)
        y = np.vstack([np.linspace(0.0, 1.0, 5) + 2j])

    _, values = describe.table_rows(Fake())
    assert values.dtype == np.float64
    assert values[0][-1] == pytest.approx(1.0)


def test_many_components_are_summarised_rather_than_listed():
    """Pleiades has twenty-eight, and a paragraph naming each is the table
    read aloud -- which is what the table is for."""
    class Fake:
        t = np.linspace(0.0, 1.0, 50)
        y = np.vstack([np.linspace(0.0, 1.0, 50)] * 28)
        status = "finished"
        success = True

    words = describe.summarise(Fake(), limit=4)
    assert "remaining 24 components are in the data table" in words
