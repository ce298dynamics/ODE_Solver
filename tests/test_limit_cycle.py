"""The limit-cycle finder, checked against known periods and known non-cycles.

Written after the fact: DYN-02 landed checked "by direct measurement on five
systems" with this file promised and never written. The measurements are
repeated here as assertions, plus the slow orbits the finder used to give up on.

Every positive case has a period known independently of this code -- Van der
Pol's from the literature and from the relaxation asymptotics -- and every
negative case is a system where a cycle provably is not: a centre's continuum,
a damped spiral, a trajectory that never returns.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite_app import catalog
from odesuite_app.analysis import largest_closed_orbit


def _problem(key, **params):
    entry = catalog.get(key)
    return entry.build({**entry.defaults(), **params}).problem


def test_van_der_pol_has_its_literature_period():
    cycle = largest_closed_orbit(_problem("van_der_pol"))
    assert cycle.isolated, cycle.verdict
    assert cycle.period == pytest.approx(6.6633, abs=2e-4)
    assert "attracting limit cycle" in cycle.verdict
    assert cycle.orbit.shape[1] == 2 and cycle.orbit.shape[0] > 10


def test_the_brusselator_cycle_is_found_and_attracts():
    cycle = largest_closed_orbit(_problem("brusselator"))
    assert cycle.isolated
    assert cycle.period == pytest.approx(7.1569, abs=1e-3)
    assert cycle.contraction < 1.0


def test_a_slow_relaxation_oscillation_is_followed_long_enough_to_close():
    """FitzHugh-Nagumo goes round once in about 40 time units; the finder's
    first run is 120, which holds three crossings. It used to stop there with
    "too few to judge" -- on the textbook relaxation oscillator."""
    cycle = largest_closed_orbit(_problem("fitzhugh_nagumo"))
    assert cycle.isolated, cycle.verdict
    assert 35.0 < cycle.period < 45.0


@pytest.mark.slow
def test_van_der_pol_at_large_mu_matches_the_relaxation_asymptotics():
    """T ~ (3 - 2 ln 2) mu + 7.014 mu^(-1/3) for large mu: 34.86 at mu = 20."""
    mu = 20.0
    asymptotic = (3.0 - 2.0 * np.log(2.0)) * mu + 7.014 * mu ** (-1.0 / 3.0)
    cycle = largest_closed_orbit(_problem("van_der_pol", mu=mu))
    assert cycle.isolated
    assert cycle.period == pytest.approx(asymptotic, rel=0.02)


@pytest.mark.parametrize("key", ["lotka_volterra", "pendulum"])
def test_a_closed_orbit_of_a_centre_is_not_a_limit_cycle(key):
    """Every orbit near a centre is closed and none is isolated. Pushed off, the
    orbit settles onto a neighbour instead of coming back."""
    cycle = largest_closed_orbit(_problem(key))
    assert np.isfinite(cycle.period)
    assert not cycle.isolated
    assert "not an isolated one" in cycle.verdict


@pytest.mark.parametrize("key, params", [
    ("duffing", {}),
    ("pendulum", {"damping": 0.3}),
    ("fitzhugh_nagumo", {"I_ext": 0.2}),     # below the Hopf at 0.3313
])
def test_a_trajectory_spiralling_in_is_not_called_an_orbit(key, params):
    cycle = largest_closed_orbit(_problem(key, **params))
    assert not cycle.isolated
    assert np.isnan(cycle.period)
    assert "equilibrium" in cycle.verdict


def test_a_trajectory_that_never_returns_is_given_up_on_promptly():
    """No crossings means no period to size a longer run from: one blind
    extension and stop, rather than following a falling ball for 1920 units."""
    import time

    start = time.process_time()
    cycle = largest_closed_orbit(_problem("bouncing_ball"))
    assert np.isnan(cycle.period)
    assert "too few to judge" in cycle.verdict
    assert time.process_time() - start < 5.0


def test_only_planar_systems_are_attempted():
    cycle = largest_closed_orbit(_problem("lorenz"))
    assert "only planar" in cycle.verdict


def test_the_search_can_be_abandoned():
    cycle = largest_closed_orbit(_problem("fitzhugh_nagumo"), should_stop=lambda: True)
    assert cycle.verdict == "cancelled"
