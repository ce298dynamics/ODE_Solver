"""Machine-verification of every Butcher tableau against the order conditions.

This is the cheapest and sharpest correctness test in the library. A Runge-Kutta
method attains order p if and only if its coefficients satisfy one algebraic
condition per rooted tree of order <= p. Checking them directly catches a single
mistyped digit instantly and exactly, whereas a convergence test would only show
a degraded slope and a debugging session.

Conditions are taken from Hairer, Norsett & Wanner I, Theorem II.2.13 (the
elementary weights of rooted trees through order 5).
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite.tableaux import TABLEAUX, ButcherTableau

# Distinct tableaux, deduplicated because "rk45" aliases "dopri5".
UNIQUE = {tab.name: tab for tab in TABLEAUX.values()}
ALL_TABLEAUX = sorted(UNIQUE.values(), key=lambda t: t.name)
IDS = [t.name for t in ALL_TABLEAUX]

TOL = 1e-13


def order_condition_residuals(A, b, c, order: int) -> dict[str, float]:
    """Residuals of every rooted-tree order condition up to `order`.

    Notation: `Ac` is the vector ``A @ c``, and products of vectors are
    elementwise. Each entry maps a tree label to ``lhs - rhs``.
    """
    Ac = A @ c
    Ac2 = A @ (c**2)
    Ac3 = A @ (c**3)
    AAc = A @ Ac
    res: dict[str, float] = {}

    if order >= 1:
        res["1"] = b @ np.ones_like(c) - 1.0
    if order >= 2:
        res["c"] = b @ c - 1 / 2
    if order >= 3:
        res["c^2"] = b @ c**2 - 1 / 3
        res["Ac"] = b @ Ac - 1 / 6
    if order >= 4:
        res["c^3"] = b @ c**3 - 1 / 4
        res["c*Ac"] = b @ (c * Ac) - 1 / 8
        res["Ac^2"] = b @ Ac2 - 1 / 12
        res["AAc"] = b @ AAc - 1 / 24
    if order >= 5:
        res["c^4"] = b @ c**4 - 1 / 5
        res["c^2*Ac"] = b @ (c**2 * Ac) - 1 / 10
        res["(Ac)^2"] = b @ (Ac * Ac) - 1 / 20
        res["c*Ac^2"] = b @ (c * Ac2) - 1 / 15
        res["Ac^3"] = b @ Ac3 - 1 / 20
        res["c*AAc"] = b @ (c * AAc) - 1 / 30
        res["A(c*Ac)"] = b @ (A @ (c * Ac)) - 1 / 40
        res["AAc^2"] = b @ (A @ Ac2) - 1 / 60
        res["AAAc"] = b @ (A @ AAc) - 1 / 120
    if order >= 6:
        raise NotImplementedError("order conditions above 5 are not tabulated")
    return res


@pytest.mark.parametrize("tab", ALL_TABLEAUX, ids=IDS)
def test_row_sum_consistency(tab: ButcherTableau):
    """``c_i == sum_j a_ij`` -- required for consistency on non-autonomous problems.

    A method violating this integrates ``y' = g(t)`` incorrectly while still
    looking fine on autonomous test problems, so it is worth checking on its own.
    """
    assert np.allclose(tab.A.sum(axis=1), tab.c, atol=TOL), (
        f"{tab.name}: row sums {tab.A.sum(axis=1)} != c {tab.c}"
    )


@pytest.mark.parametrize("tab", ALL_TABLEAUX, ids=IDS)
def test_propagated_order_conditions(tab: ButcherTableau):
    """The b weights satisfy every order condition up to the claimed order."""
    res = order_condition_residuals(tab.A, tab.b, tab.c, tab.order)
    bad = {k: v for k, v in res.items() if abs(v) > TOL}
    assert not bad, f"{tab.name} claims order {tab.order} but violates {bad}"


@pytest.mark.parametrize("tab", ALL_TABLEAUX, ids=IDS)
def test_propagated_order_is_maximal(tab: ButcherTableau):
    """The claimed order is not an understatement.

    If the method actually satisfied the conditions one order higher, the error
    estimator would be mis-scaled and the step controller would use the wrong
    exponent, so a wrong claim in either direction matters.
    """
    if tab.order >= 5:
        pytest.skip("order-6 conditions are not tabulated")
    res = order_condition_residuals(tab.A, tab.b, tab.c, tab.order + 1)
    assert any(abs(v) > TOL for v in res.values()), (
        f"{tab.name} satisfies all order-{tab.order + 1} conditions; "
        f"its declared order {tab.order} is too low"
    )


@pytest.mark.parametrize("tab", ALL_TABLEAUX, ids=IDS)
def test_embedded_order_conditions(tab: ButcherTableau):
    """The embedded weights ``b_hat = b - e`` satisfy their own order conditions."""
    b_hat = tab.b - tab.e
    res = order_condition_residuals(tab.A, b_hat, tab.c, tab.error_order)
    bad = {k: v for k, v in res.items() if abs(v) > TOL}
    assert not bad, (
        f"{tab.name}: embedded solution claims order {tab.error_order} "
        f"but violates {bad}"
    )


@pytest.mark.parametrize("tab", ALL_TABLEAUX, ids=IDS)
def test_embedded_pair_differs(tab: ButcherTableau):
    """The two solutions must actually differ, or there is no error estimate."""
    assert np.linalg.norm(tab.e) > 1e-10, f"{tab.name}: b_hat == b, no error estimate"
    assert tab.error_order < tab.order, (
        f"{tab.name}: embedded order {tab.error_order} must be below "
        f"propagated order {tab.order}"
    )


@pytest.mark.parametrize("tab", ALL_TABLEAUX, ids=IDS)
def test_structure(tab: ButcherTableau):
    """Explicitness, and a first abscissa of zero."""
    assert np.allclose(np.triu(tab.A), 0.0), f"{tab.name}: A is not strictly lower"
    assert tab.c[0] == 0.0, f"{tab.name}: c[0] must be 0"


def test_fsal_detection():
    """FSAL is inferred from the coefficients, and the inference is right."""
    assert TABLEAUX["dopri5"].fsal
    assert TABLEAUX["rk23"].fsal
    assert TABLEAUX["tsit5"].fsal
    assert not TABLEAUX["rkf45"].fsal
    assert not TABLEAUX["cashkarp"].fsal


@pytest.mark.parametrize("tab", ALL_TABLEAUX, ids=IDS)
def test_dense_output_matrix_consistency(tab: ButcherTableau):
    """A native interpolant must reproduce both endpoints of the step.

    At theta=0 it must give y0 (so the P-weighted sum vanishes) and at theta=1
    it must give y1, which requires the interpolant's coefficient sums to equal
    the tableau's b weights.
    """
    if tab.P is None:
        pytest.skip(f"{tab.name} has no native dense output")
    assert np.allclose(tab.P.sum(axis=1), tab.b, atol=1e-12), (
        f"{tab.name}: interpolant does not land on y1 at theta=1"
    )
