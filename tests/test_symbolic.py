"""Closed-form solutions: parsing, dsolve, verification, and the numeric bridge.

The strongest checks here are the two independent ones. A closed form is
substituted back into its own equation and must simplify to *exactly* zero; and
it is evaluated against the numeric solution of the same equation, which shares
no code with sympy. Either alone could be fooled; together they are hard to
argue with.
"""

from __future__ import annotations

import time

import numpy as np
import pytest

pytest.importorskip("sympy")

import sympy as sp  # noqa: E402

from odesuite import solve  # noqa: E402
from odesuite_app.custom import ParseError  # noqa: E402
from odesuite_app.symbolic import (  # noqa: E402
    EXAMPLES,
    EquationSpec,
    characteristic_analysis,
    parse_equation,
    solve_symbolically,
    to_first_order,
)

T = sp.Symbol("t", real=True)


def _spec(equation: str, ics: str = "", **kwargs) -> EquationSpec:
    return EquationSpec(equations=[equation], initial_conditions=ics, **kwargs)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,order",
    [
        ("y' = -y", 1),
        ("y'' + 3y' + 2y = sin(t)", 2),
        ("y^(3) - y = 0", 3),
        ("y^(4) = y", 4),
        ("2y'' = -8y", 2),
        ("t**2*y'' + t*y' - y = 0", 2),
        ("y'' - y = 0", 2),
    ],
)
def test_parses_prime_notation(text, order):
    parsed = parse_equation(_spec(text))
    assert parsed.order == order
    assert parsed.equation.free_symbols <= {T}


def test_implicit_multiplication_is_understood():
    """``3y'`` means ``3*y'`` -- students write it that way."""
    explicit = parse_equation(_spec("3*y' + 2*y = 0")).equation
    implicit = parse_equation(_spec("3y' + 2y = 0")).equation
    assert sp.simplify(explicit.lhs - implicit.lhs) == 0


@pytest.mark.parametrize(
    "text,message",
    [
        ("y = 5", "no derivative"),
        ("y'' + z = 0", "unknown name"),
        ("y'' + 3y'", "exactly one"),
        ("y'' = = 0", "exactly one"),
        ("", "type an equation"),
        ("y'' + = 0", "cannot parse"),
    ],
)
def test_bad_input_is_rejected_with_a_readable_message(text, message):
    with pytest.raises(ParseError, match=message):
        parse_equation(_spec(text))


def test_parser_cannot_execute_code():
    """The same hardening as the numeric editor, on the new entry point."""
    for payload in (
        "y' = __import__('os').system('echo pwned')",
        "y' = open('x','w')",
        "y' = eval('1+1')",
    ):
        with pytest.raises(ParseError):
            parse_equation(_spec(payload))


def test_variables_in_a_system_do_not_collide():
    """Each variable needs its own placeholder during parsing.

    A shared one makes ``x`` and ``y`` rewrite to the same symbol, and the
    system silently collapses into a single equation in one unknown.
    """
    parsed = parse_equation(
        EquationSpec(
            equations=["x' = x + 2*y", "y' = 3*x + 2*y"], variables=["x", "y"]
        )
    )
    assert parsed.is_system and len(parsed.equations) == 2
    x, y = (f(T) for f in parsed.functions)
    assert sp.simplify(parsed.equations[0].rhs - (x + 2 * y)) == 0
    assert sp.simplify(parsed.equations[1].rhs - (3 * x + 2 * y)) == 0


# ---------------------------------------------------------------------------
# Initial conditions
# ---------------------------------------------------------------------------


def test_initial_conditions_of_every_order():
    parsed = parse_equation(
        _spec("y^(3) - y = 0", "y(0) = 1, y'(0) = 2, y''(0) = 3")
    )
    problem = to_first_order(parsed)
    assert np.allclose(problem.y0, [1.0, 2.0, 3.0])
    assert problem.state_labels[0] == "y"


def test_initial_conditions_at_a_nonzero_point():
    parsed = parse_equation(_spec("t**2*y'' + t*y' - y = 0", "y(1) = 1, y'(1) = 0"))
    assert len(parsed.ics) == 2


@pytest.mark.parametrize("text", ["y(0) 1", "y[0] = 1", "z(0) = 1"])
def test_malformed_conditions_are_rejected(text):
    with pytest.raises(ParseError):
        parse_equation(_spec("y' = -y", text))


def test_missing_conditions_give_the_general_solution():
    """Under-determined is a legitimate request, not an error."""
    result = solve_symbolically(parse_equation(_spec("y'' + y = 0")))
    assert result.general is not None
    assert result.particular is None
    assert result.general.free_symbols - {T}, "expected arbitrary constants"


# ---------------------------------------------------------------------------
# Characteristic analysis -- the by-hand method
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,poly,roots",
    [
        ("y'' + 3y' + 2y = 0", "r**2 + 3*r + 2", {-2: 1, -1: 1}),
        ("y'' + 2y' + y = 0", "r**2 + 2*r + 1", {-1: 2}),
        ("y'' + 4y = 0", "r**2 + 4", {-2j: 1, 2j: 1}),
        ("y' + 2y = 0", "r + 2", {-2: 1}),
    ],
)
def test_characteristic_polynomial_and_roots(text, poly, roots):
    analysis = characteristic_analysis(parse_equation(_spec(text)))
    assert sp.simplify(analysis["poly"] - sp.sympify(poly)) == 0
    assert analysis["constant_coefficients"] and analysis["linear"]

    found = {complex(root): multiplicity for root, multiplicity in analysis["roots"]}
    expected = {complex(k): v for k, v in roots.items()}
    assert found == expected


def test_repeated_root_contributes_a_factor_of_t():
    """The rule everyone learns: a double root gives ``e^{rt}`` and ``t e^{rt}``."""
    analysis = characteristic_analysis(parse_equation(_spec("y'' + 2y' + y = 0")))
    basis = [sp.simplify(b) for b in analysis["fundamental_set"]]
    assert len(basis) == 2
    assert any(sp.simplify(b - sp.exp(-T)) == 0 for b in basis)
    assert any(sp.simplify(b - T * sp.exp(-T)) == 0 for b in basis)


def test_complex_pair_contributes_sine_and_cosine():
    analysis = characteristic_analysis(parse_equation(_spec("y'' + 2y' + 5y = 0")))
    basis = [sp.simplify(b) for b in analysis["fundamental_set"]]
    assert len(basis) == 2, "a conjugate pair contributes one pair of real solutions"
    assert any(sp.simplify(b - sp.exp(-T) * sp.cos(2 * T)) == 0 for b in basis)
    assert any(sp.simplify(b - sp.exp(-T) * sp.sin(2 * T)) == 0 for b in basis)


def test_fundamental_set_solves_the_homogeneous_equation():
    """Every basis function must actually satisfy the equation."""
    for text in ("y'' + 3y' + 2y = 0", "y'' + 2y' + y = 0", "y^(3) + y'' - y' - y = 0"):
        parsed = parse_equation(_spec(text))
        analysis = characteristic_analysis(parsed)
        assert analysis["fundamental_set"]
        for basis in analysis["fundamental_set"]:
            residual = sp.simplify(
                (parsed.equation.lhs - parsed.equation.rhs)
                .subs(parsed.function(T), basis)
                .doit()
            )
            assert residual == 0, f"{basis} does not solve {text}"


def test_variable_coefficients_are_detected_not_faked():
    analysis = characteristic_analysis(parse_equation(_spec("t*y' + y = t**2")))
    assert analysis["linear"]
    assert not analysis["constant_coefficients"]
    assert analysis["poly"] is None


def test_nonlinear_equations_are_detected():
    analysis = characteristic_analysis(parse_equation(_spec("y' = y*(1 - y)")))
    assert not analysis["linear"]


def test_forcing_term_and_homogeneity():
    homogeneous = characteristic_analysis(parse_equation(_spec("y'' + 4y = 0")))
    forced = characteristic_analysis(parse_equation(_spec("y'' + 4y = sin(t)")))
    assert homogeneous["homogeneous"]
    assert not forced["homogeneous"]
    assert sp.simplify(forced["forcing"] - sp.sin(T)) == 0


# ---------------------------------------------------------------------------
# Closed forms, against hand-derived answers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text,ics,expected",
    [
        # y'' + 3y' + 2y = 0, y(0)=1, y'(0)=0  ->  2e^-t - e^-2t
        ("y'' + 3y' + 2y = 0", "y(0)=1, y'(0)=0", "2*exp(-t) - exp(-2*t)"),
        # y'' + 2y' + 5y = 0, y(0)=1, y'(0)=0  ->  e^-t (cos2t + sin(2t)/2)
        ("y'' + 2y' + 5y = 0", "y(0)=1, y'(0)=0",
         "exp(-t)*(cos(2*t) + sin(2*t)/2)"),
        # repeated root
        ("y'' + 2y' + y = 0", "y(0)=1, y'(0)=1", "(1 + 2*t)*exp(-t)"),
        # resonance: forcing at the natural frequency gives a t multiplier
        ("y'' + y = cos(t)", "y(0)=0, y'(0)=0", "t*sin(t)/2"),
        # first order, integrating factor
        ("y' + 2y = exp(-t)", "y(0)=0", "exp(-t) - exp(-2*t)"),
        # separable logistic
        ("y' = y*(1 - y)", "y(0)=0.5", "1/(1 + exp(-t))"),
    ],
)
def test_closed_form_matches_the_hand_derived_answer(text, ics, expected):
    result = solve_symbolically(parse_equation(_spec(text, ics)))
    assert result.particular is not None, result.message

    # `locals` matters: a bare sympify makes Symbol('t') with no assumptions,
    # which sympy treats as a *different* symbol from the parser's
    # Symbol('t', real=True) -- so even identical expressions refuse to cancel.
    reference = sp.sympify(expected, locals={"t": T})

    # nsimplify first, because an initial condition written as 0.5 puts a Float
    # into the answer and exact cancellation then fails on the float alone.
    difference = sp.simplify(sp.nsimplify(result.particular - reference))
    if difference != 0:
        # Symbolic simplification is not complete; agreement to machine
        # precision across the interval settles it either way.
        grid = np.linspace(0.13, 3.7, 60)
        got = np.asarray(sp.lambdify(T, result.particular, "numpy")(grid), dtype=float)
        want = np.asarray(sp.lambdify(T, reference, "numpy")(grid), dtype=float)
        assert np.abs(got - want).max() < 1e-12, (
            f"got {result.particular}, expected {expected}"
        )


def test_solutions_are_verified_by_substitution():
    """Substituting back must give exactly zero, and the flag must say so."""
    for text, ics in [
        ("y'' + 2y' + 5y = 0", "y(0)=1, y'(0)=0"),
        ("y'' + 4y = sin(t)", "y(0)=0, y'(0)=1"),
        ("y^(3) + y'' - y' - y = 0", "y(0)=1, y'(0)=0, y''(0)=0"),
        ("t**2*y'' + t*y' - y = 0", "y(1)=1, y'(1)=0"),
    ]:
        result = solve_symbolically(parse_equation(_spec(text, ics)))
        assert result.solved, f"{text}: {result.message}"
        assert result.verified is True, f"{text}: residual {result.residual}"
        assert result.residual == 0


def test_linear_system_gets_a_closed_form():
    parsed = parse_equation(
        EquationSpec(
            equations=["x' = x + 2*y", "y' = 3*x + 2*y"],
            initial_conditions="x(0) = 1, y(0) = 0",
            variables=["x", "y"], t_span=(0.0, 1.0),
        )
    )
    result = solve_symbolically(parsed)
    assert result.particular is not None, result.message
    assert len(result.particular) == 2


# ---------------------------------------------------------------------------
# The two solvers against each other
# ---------------------------------------------------------------------------


SOLVABLE = [name for name in EXAMPLES if "no closed form" not in name]


@pytest.mark.parametrize("name", SOLVABLE)
def test_symbolic_and_numeric_agree(name):
    """The strongest check available: two unrelated methods, one answer.

    sympy derives a formula; the library integrates the same equation with
    Radau. They share no code, so agreement to ten digits is meaningful in a
    way that either result alone is not.
    """
    spec = EXAMPLES[name]
    parsed = parse_equation(spec)
    result = solve_symbolically(parsed)
    if result.particular is None or parsed.is_system:
        pytest.skip(f"{name}: no scalar particular solution to compare")

    problem = to_first_order(parsed)
    numeric = solve(
        problem, method="radau", rtol=1e-11, atol=1e-13, dense_output=True,
        max_steps=300_000,
    )
    assert numeric.success, numeric.message

    exact = sp.lambdify(T, result.particular, "numpy")
    grid = np.linspace(problem.t0, problem.tf, 300)
    deviation = np.abs(np.asarray(exact(grid), dtype=float) - numeric.sol(grid)[0]).max()
    assert deviation < 1e-6, f"{name}: symbolic and numeric differ by {deviation:.2e}"


# ---------------------------------------------------------------------------
# Failure must not mean hanging
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("text", ["y' = sin(y)", "y'' + sin(y) = 0"])
@pytest.mark.slow
def test_unsolvable_equations_time_out_rather_than_hang(text):
    """`dsolve` does not merely take a long time on these -- it never returns.

    A thread cannot be killed, which is why the solver runs in a subprocess.
    This test would hang forever if that changed, so the timeout is the
    assertion.
    """
    started = time.perf_counter()
    result = solve_symbolically(parse_equation(_spec(text)), timeout=8.0)
    elapsed = time.perf_counter() - started

    assert result.timed_out
    assert not result.solved
    assert elapsed < 25.0, f"took {elapsed:.1f}s; the timeout did not bite"
    assert "closed form" in result.message


def test_equations_with_no_closed_form_fail_cleanly():
    result = solve_symbolically(parse_equation(_spec("y'' - 3*(1 - y**2)*y' + y = 0")))
    assert not result.solved
    assert result.message
    assert not result.timed_out


def test_no_closed_form_still_allows_the_numeric_route():
    """The point of reducing to a first-order system regardless."""
    spec = EXAMPLES["Van der Pol (no closed form)"]
    parsed = parse_equation(spec)
    assert not solve_symbolically(parsed).solved

    problem = to_first_order(parsed)
    numeric = solve(problem, method="radau", rtol=1e-8, atol=1e-10, max_steps=300_000)
    assert numeric.success
    assert np.all(np.isfinite(numeric.y[:, -1]))


# ---------------------------------------------------------------------------
# Reduction to a first-order system
# ---------------------------------------------------------------------------


def test_reduction_produces_the_companion_system():
    """``y'' = -y`` becomes ``[y', -y]`` with state ``[y, y']``."""
    parsed = parse_equation(_spec("y'' + y = 0", "y(0)=1, y'(0)=0"))
    problem = to_first_order(parsed)
    assert problem.n == 2
    assert np.allclose(problem.f(0.0, np.array([1.0, 0.0])), [0.0, -1.0])
    assert np.allclose(problem.f(0.0, np.array([0.0, 1.0])), [1.0, 0.0])


def test_reduction_supplies_an_exact_jacobian():
    parsed = parse_equation(_spec("y'' + 3y' + 2y = 0", "y(0)=1, y'(0)=0"))
    problem = to_first_order(parsed)
    assert problem.has_jac
    assert np.allclose(problem.jac(0.0, np.array([1.0, 1.0])), [[0, 1], [-2, -3]])


def test_reduction_handles_parameters():
    spec = _spec("y'' - mu*(1 - y**2)*y' + y = 0", "y(0)=2, y'(0)=0",
                 parameters={"mu": 4.0})
    problem = to_first_order(parse_equation(spec))
    # y'' = mu (1-y^2) y' - y, at y=0, y'=1  ->  4
    assert problem.f(0.0, np.array([0.0, 1.0]))[1] == pytest.approx(4.0)


def test_every_method_can_integrate_a_reduced_equation():
    parsed = parse_equation(_spec("y'' + 0.3*y' + y = 0", "y(0)=1, y'(0)=0",
                                  t_span=(0.0, 10.0)))
    problem = to_first_order(parsed)
    for method in ("dopri5", "tsit5", "radau", "rodas4", "taylor20"):
        numeric = solve(problem, method=method, rtol=1e-9, atol=1e-12)
        assert numeric.success, f"{method}: {numeric.message}"


@pytest.mark.parametrize("name", list(EXAMPLES))
def test_every_example_parses_and_integrates(name):
    parsed = parse_equation(EXAMPLES[name])
    problem = to_first_order(parsed)
    numeric = solve(problem, method="radau", rtol=1e-8, atol=1e-11, max_steps=300_000)
    assert numeric.success, f"{name}: {numeric.message}"
