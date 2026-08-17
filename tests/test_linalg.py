"""Jacobian strategies, graph colouring, and the linear-solve wrappers."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from odesuite import ODEProblem
from odesuite.linalg import (
    JacobianEvaluator,
    apply_mass,
    column_groups,
    complex_step_jacobian,
    forward_diff_jacobian,
    lu_factorize,
    mass_minus_jacobian,
    sparse_diff_jacobian,
)
from odesuite.problems import brusselator, robertson


def _nonlinear_problem():
    """A problem with a strongly state-dependent Jacobian and mixed magnitudes."""

    def f(t, y):
        return np.array(
            [
                -0.04 * y[0] + 1e4 * y[1] * y[2],
                np.sin(y[0]) * y[2] - 3.0 * y[1] ** 2,
                y[0] * y[1] - np.exp(-y[2]),
            ]
        )

    def jac(t, y):
        return np.array(
            [
                [-0.04, 1e4 * y[2], 1e4 * y[1]],
                [np.cos(y[0]) * y[2], -6.0 * y[1], np.sin(y[0])],
                [y[1], y[0], np.exp(-y[2])],
            ]
        )

    return ODEProblem(f=f, t_span=(0.0, 1.0), y0=[0.7, 0.02, 0.3], jac=jac)


# ---------------------------------------------------------------------------
# Agreement between strategies
# ---------------------------------------------------------------------------


def test_finite_difference_matches_analytic():
    prob = _nonlinear_problem()
    y = np.array([0.7, 0.02, 0.3])
    f0 = prob.f(0.0, y)

    exact = prob.jac(0.0, y)
    approx = forward_diff_jacobian(prob.f, 0.0, y, f0)
    assert np.allclose(approx, exact, rtol=1e-6, atol=1e-6)


def test_complex_step_is_exact():
    """Complex-step differentiation has no truncation error at all.

    Unlike a finite difference it never subtracts nearby values, so the result
    is as accurate as the function evaluation itself. On an analytic RHS it
    reproduces the hand-derived Jacobian to the last bit -- which is the point
    of implementing it.
    """
    prob = _nonlinear_problem()
    y = np.array([0.7, 0.02, 0.3])
    f0 = prob.f(0.0, y)

    exact = prob.jac(0.0, y)
    approx = complex_step_jacobian(prob.f, 0.0, y)

    assert np.allclose(approx, exact, rtol=1e-14, atol=1e-15)
    # Strictly better than the finite difference on the same problem.
    fd = forward_diff_jacobian(prob.f, 0.0, y, f0)
    assert np.abs(approx - exact).max() < np.abs(fd - exact).max()


def test_complex_step_beats_finite_difference_on_tiny_values():
    """The regime where finite differences fall apart and complex step does not."""

    def f(t, y):
        return np.array([y[0] ** 3 * 1e-12])

    y = np.array([1e-4])
    exact = 3e-12 * y[0] ** 2

    cs = complex_step_jacobian(f, 0.0, y)[0, 0]
    fd = forward_diff_jacobian(f, 0.0, y, f(0.0, y))[0, 0]
    assert abs(cs - exact) <= abs(fd - exact)


@pytest.mark.parametrize("method", ["analytic", "fd", "complex_step"])
def test_evaluator_strategies_agree(method):
    prob = _nonlinear_problem()
    y = np.array([0.7, 0.02, 0.3])
    f0 = prob.f(0.0, y)

    J = JacobianEvaluator(prob, method)(0.0, y, f0)
    assert np.allclose(J, prob.jac(0.0, y), rtol=1e-5, atol=1e-6)


def test_evaluator_counts_its_own_work():
    """`nfev` must include the cost of numerical differentiation."""
    prob = brusselator().problem
    y = prob.y0
    f0 = prob.f(0.0, y)

    fd = JacobianEvaluator(prob, "fd")
    fd(0.0, y, f0)
    assert fd.nfev == prob.n
    assert fd.njev == 1

    analytic = JacobianEvaluator(prob, "analytic")
    analytic(0.0, y, f0)
    assert analytic.nfev == 0


def test_auto_prefers_analytic():
    assert JacobianEvaluator(robertson().problem, "auto").method == "analytic"

    plain = ODEProblem(f=lambda t, y: -y, t_span=(0, 1), y0=[1.0])
    assert JacobianEvaluator(plain, "auto").method == "fd"


def test_constant_jacobian_is_evaluated_once():
    A = np.array([[-1.0, 2.0], [0.5, -3.0]])
    prob = ODEProblem(f=lambda t, y: A @ y, t_span=(0, 1), y0=[1.0, 1.0], jac=A)
    ev = JacobianEvaluator(prob, "auto")
    first = ev(0.0, prob.y0, prob.f(0.0, prob.y0))
    second = ev(0.5, prob.y0 * 2, prob.f(0.0, prob.y0))
    assert first is second


# ---------------------------------------------------------------------------
# Sparsity and colouring
# ---------------------------------------------------------------------------


def test_colouring_of_a_tridiagonal_matrix():
    """A tridiagonal Jacobian needs exactly three colours, at any size."""
    n = 200
    S = sparse.diags([np.ones(n - 1), np.ones(n), np.ones(n - 1)], [-1, 0, 1])
    groups = column_groups(S)
    assert groups.max() + 1 == 3


def test_colouring_of_a_diagonal_matrix():
    """A diagonal Jacobian is one colour: every column is independent."""
    groups = column_groups(sparse.eye(50))
    assert groups.max() + 1 == 1


def test_colouring_of_a_dense_matrix():
    """A dense Jacobian admits no savings: one colour per column."""
    groups = column_groups(np.ones((12, 12)))
    assert groups.max() + 1 == 12


def test_colour_groups_are_structurally_orthogonal():
    """The colouring must be valid, not merely small.

    Two columns sharing a colour may not share a nonzero row, or their
    contributions to the difference vector would be inseparable.
    """
    rng = np.random.default_rng(0)
    S = sparse.csc_matrix(rng.random((30, 30)) < 0.12)
    groups = column_groups(S)
    for g in range(groups.max() + 1):
        members = np.nonzero(groups == g)[0]
        rows = [set(S.indices[S.indptr[j] : S.indptr[j + 1]]) for j in members]
        for a in range(len(rows)):
            for b in range(a + 1, len(rows)):
                assert rows[a].isdisjoint(rows[b]), (
                    f"columns {members[a]} and {members[b]} share colour {g} "
                    f"but overlap in rows"
                )


def test_sparse_jacobian_matches_dense():
    n = 60
    A = sparse.diags(
        [np.ones(n - 1), -2 * np.ones(n), np.ones(n - 1)], [-1, 0, 1], format="csc"
    )
    prob = ODEProblem(
        f=lambda t, y: A @ y, t_span=(0, 1), y0=np.ones(n), jac_sparsity=A
    )
    y = np.linspace(0.5, 2.0, n)
    f0 = prob.f(0.0, y)

    groups = column_groups(A)
    J = sparse_diff_jacobian(prob.f, 0.0, y, f0, A, groups)
    # Forward differences carry O(sqrt(eps)) error, about 1.5e-8 for an O(1)
    # state, so the tolerance is set by the method rather than by the colouring.
    assert np.abs(J.toarray() - A.toarray()).max() < 1e-6


def test_sparse_evaluator_costs_one_eval_per_colour():
    n = 100
    A = sparse.diags(
        [np.ones(n - 1), -2 * np.ones(n), np.ones(n - 1)], [-1, 0, 1], format="csc"
    )
    prob = ODEProblem(
        f=lambda t, y: A @ y, t_span=(0, 1), y0=np.ones(n), jac_sparsity=A
    )
    ev = JacobianEvaluator(prob, "sparse")
    ev(0.0, prob.y0, prob.f(0.0, prob.y0))

    assert ev.n_groups == 3
    assert ev.nfev == 3, "a tridiagonal Jacobian must not cost n evaluations"


def test_sparse_jacobian_on_a_nonlinear_problem():
    """Colouring must work when the Jacobian entries actually vary."""
    n = 40

    def f(t, y):
        out = np.empty(n)
        out[0] = -2 * y[0] ** 2 + y[1]
        out[-1] = y[-2] - 2 * y[-1] ** 2
        out[1:-1] = y[:-2] - 2 * y[1:-1] ** 2 + y[2:]
        return out

    S = sparse.diags(
        [np.ones(n - 1), np.ones(n), np.ones(n - 1)], [-1, 0, 1], format="csc"
    )
    prob = ODEProblem(f=f, t_span=(0, 1), y0=np.ones(n), jac_sparsity=S)
    y = np.linspace(0.3, 1.7, n)
    f0 = prob.f(0.0, y)

    approx = JacobianEvaluator(prob, "sparse")(0.0, y, f0).toarray()
    exact = forward_diff_jacobian(prob.f, 0.0, y, f0)
    assert np.abs(approx - exact).max() < 1e-6


# ---------------------------------------------------------------------------
# Linear solves and the mass matrix
# ---------------------------------------------------------------------------


def test_dense_lu_round_trip():
    rng = np.random.default_rng(1)
    A = rng.random((25, 25)) + 25 * np.eye(25)
    b = rng.random(25)
    assert np.allclose(lu_factorize(A.copy()).solve(b), np.linalg.solve(A, b))


def test_complex_lu_round_trip():
    """Radau's split solve factorises a complex matrix; it must round-trip."""
    rng = np.random.default_rng(2)
    A = rng.random((10, 10)) + 1j * rng.random((10, 10)) + 10 * np.eye(10)
    b = rng.random(10) + 1j * rng.random(10)
    assert np.allclose(lu_factorize(A.copy()).solve(b), np.linalg.solve(A, b))


def test_sparse_lu_round_trip():
    n = 40
    A = sparse.diags(
        [np.ones(n - 1), -4 * np.ones(n), np.ones(n - 1)], [-1, 0, 1], format="csc"
    )
    b = np.arange(n, dtype=float)
    assert np.allclose(lu_factorize(A).solve(b), np.linalg.solve(A.toarray(), b))


def test_singular_matrix_raises():
    A = np.array([[1.0, 2.0], [2.0, 4.0]])
    with pytest.raises((np.linalg.LinAlgError, RuntimeError, ValueError)):
        lu_factorize(A).solve(np.array([1.0, 1.0]))


def test_apply_mass_treats_none_as_identity():
    v = np.array([1.0, 2.0, 3.0])
    assert np.array_equal(apply_mass(None, v), v)
    M = np.diag([2.0, 3.0, 4.0])
    assert np.array_equal(apply_mass(M, v), np.array([2.0, 6.0, 12.0]))


def test_mass_minus_jacobian_combinations():
    J = np.array([[1.0, 2.0], [3.0, 4.0]])
    assert np.allclose(mass_minus_jacobian(None, J, 2.0), 2 * np.eye(2) - J)

    M = np.array([[2.0, 0.0], [0.0, 5.0]])
    assert np.allclose(mass_minus_jacobian(M, J, 3.0), 3 * M - J)

    Js = sparse.csc_matrix(J)
    assert np.allclose(mass_minus_jacobian(None, Js, 2.0).toarray(), 2 * np.eye(2) - J)
    assert sparse.issparse(mass_minus_jacobian(sparse.csc_matrix(M), Js, 3.0))


def test_mass_minus_jacobian_accepts_complex_coefficient():
    """Required by Radau's complex block; the dtype must be promoted."""
    J = np.array([[1.0, 2.0], [3.0, 4.0]])
    W = mass_minus_jacobian(None, J, 1.0 + 2.0j)
    assert np.iscomplexobj(W)
    assert np.allclose(W, (1 + 2j) * np.eye(2) - J)
