"""User-defined systems: parsing, symbolic differentiation, and safety."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("sympy")

from odesuite import solve  # noqa: E402
from odesuite.linalg import forward_diff_jacobian  # noqa: E402
from odesuite_app.custom import (  # noqa: E402
    EXAMPLES,
    CustomSpec,
    ParseError,
    build,
)


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------


def test_expressions_cannot_execute_code(tmp_path):
    """The central safety property, and it is not the obvious one.

    `sympy.sympify` *evaluates* its input with the ordinary builtins available:
    its ``locals`` argument adds names but removes none, so it will happily run
    ``__import__('os').system(...)``. Parsing here goes through `parse_expr`
    with ``__builtins__`` explicitly emptied -- explicitly, because an absent
    key makes Python reinstate the real builtins.
    """
    marker = tmp_path / "executed.txt"
    payloads = [
        f"__import__('pathlib').Path({str(marker)!r}).write_text('x')",
        f"open({str(marker)!r}, 'w')",
        "__import__('os').system('echo pwned')",
        "().__class__.__bases__[0].__subclasses__()",
        "eval('1+1')",
    ]
    for payload in payloads:
        with pytest.raises(ParseError):
            build(CustomSpec(variables=["x"], expressions=[payload], initial=[1.0]))

    assert not marker.exists(), "an expression managed to touch the file system"


def test_unknown_names_are_rejected():
    with pytest.raises(ParseError, match="unknown name"):
        build(CustomSpec(variables=["x"], expressions=["x + wobble"], initial=[1.0]))


@pytest.mark.parametrize(
    "spec,message",
    [
        (CustomSpec(["t"], ["1"], [0.0]), "reserved"),
        (CustomSpec(["sin"], ["1"], [0.0]), "shadows"),
        (CustomSpec(["x", "x"], ["1", "1"], [0.0, 0.0]), "twice"),
        (CustomSpec(["x"], ["1", "2"], [0.0]), "equations"),
        (CustomSpec(["x"], ["1"], [0.0, 1.0]), "initial values"),
        (CustomSpec([], [], []), "at least one variable"),
        (CustomSpec(["2bad"], ["1"], [0.0]), "not a valid name"),
        (CustomSpec(["x"], ["1"], [0.0], t_span=(1.0, 1.0)), "non-empty"),
    ],
)
def test_validation_messages(spec, message):
    with pytest.raises(ParseError, match=message):
        build(spec)


def test_syntax_errors_are_reported_not_raised():
    for bad in ("x +", "((x)", "x ** ** 2"):
        with pytest.raises(ParseError, match="cannot parse"):
            build(CustomSpec(variables=["x"], expressions=[bad], initial=[1.0]))


def test_every_failure_is_a_parse_error():
    """The caller is a text box; nothing may escape as a raw exception."""
    awkward = ["sign(x)", "floor(x)", "log(x)", "1/0", "sqrt(x)"]
    for expression in awkward:
        try:
            build(CustomSpec(variables=["x"], expressions=[expression], initial=[1.0]))
        except ParseError:
            pass
        except Exception as exc:                        # pragma: no cover
            pytest.fail(f"{expression!r} raised {type(exc).__name__}: {exc}")


# ---------------------------------------------------------------------------
# Symbolic differentiation
# ---------------------------------------------------------------------------


def test_jacobian_is_exact_not_differenced():
    """The point of the feature: an exact derivative for the implicit methods."""
    system = build(
        CustomSpec(
            variables=["x", "y"],
            expressions=["y", "mu*(1 - x**2)*y - x"],
            initial=[2.0, 0.0],
            parameters={"mu": 3.0},
        )
    )
    state = np.array([0.7, -1.3])
    exact = system.problem.jac(0.0, state)

    # Hand-derived: [[0, 1], [-2*mu*x*y - 1, mu*(1 - x^2)]]
    mu = 3.0
    expected = np.array(
        [[0.0, 1.0], [-2 * mu * state[0] * state[1] - 1.0, mu * (1 - state[0] ** 2)]]
    )
    assert np.allclose(exact, expected, atol=1e-12)

    # And it beats a finite difference, which is the whole reason to have it.
    differenced = forward_diff_jacobian(
        system.problem.f, 0.0, state, system.problem.f(0.0, state)
    )
    assert np.abs(exact - expected).max() < np.abs(differenced - expected).max()


def test_jacobian_source_is_reported():
    system = build(EXAMPLES["Damped pendulum"])
    text = system.jacobian_text
    assert "cos(theta)" in text
    assert len(text.splitlines()) == 2


def test_absolute_value_works_because_symbols_are_real():
    """Sympy symbols default to complex, which breaks ``d|x|/dx``.

    With a complex symbol the derivative comes back in terms of ``re`` and
    ``im`` and then fails to lambdify, so `abs()` in a right-hand side would
    die with an obscure printer error instead of simply working.
    """
    system = build(
        CustomSpec(variables=["v"], expressions=["-v*abs(v)"], initial=[2.0])
    )
    assert system.problem.f(0.0, np.array([2.0]))[0] == pytest.approx(-4.0)
    assert system.problem.f(0.0, np.array([-2.0]))[0] == pytest.approx(4.0)
    assert system.problem.jac(0.0, np.array([2.0]))[0, 0] == pytest.approx(-4.0)


def test_time_dependent_right_hand_side():
    system = build(
        CustomSpec(variables=["y"], expressions=["cos(t)"], initial=[0.0],
                   t_span=(0.0, 2.0))
    )
    solution = solve(system.problem, method="dopri5", rtol=1e-11, atol=1e-13)
    assert solution.y[0, -1] == pytest.approx(np.sin(2.0), abs=1e-9)


def test_parameters_are_substituted_by_value():
    spec = CustomSpec(
        variables=["y"], expressions=["-k*y"], initial=[1.0],
        parameters={"k": 2.5}, t_span=(0.0, 1.0),
    )
    system = build(spec)
    assert system.problem.f(0.0, np.array([1.0]))[0] == pytest.approx(-2.5)

    spec.parameters["k"] = 4.0
    rebuilt = build(spec)
    assert rebuilt.problem.f(0.0, np.array([1.0]))[0] == pytest.approx(-4.0)


# ---------------------------------------------------------------------------
# The examples, end to end
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", list(EXAMPLES))
def test_examples_build_and_solve(name):
    system = build(EXAMPLES[name])
    solution = solve(
        system.problem, method="radau", rtol=1e-8, atol=1e-11, max_steps=300_000
    )
    assert solution.success, f"{name}: {solution.message}"
    assert np.all(np.isfinite(solution.y[:, -1]))


def test_custom_van_der_pol_matches_the_library_version():
    """A typed system must give the same answer as the built-in one."""
    from odesuite.problems import van_der_pol

    mu, t_end = 3.0, 30.0
    typed = build(
        CustomSpec(
            variables=["x", "v"],
            expressions=["v", "mu*(1 - x**2)*v - x"],
            initial=[2.0, 0.0],
            parameters={"mu": mu},
            t_span=(0.0, t_end),
        )
    )
    library = van_der_pol(mu=mu, t_end=t_end)

    a = solve(typed.problem, method="radau", rtol=1e-10, atol=1e-13)
    b = solve(library.problem, method="radau", rtol=1e-10, atol=1e-13)
    assert np.allclose(a.y[:, -1], b.y[:, -1], rtol=1e-6, atol=1e-8)


def test_stiff_custom_system_favours_an_implicit_method():
    """The exact Jacobian is what lets Radau handle a user's stiff system.

    Measured at a loose tolerance on purpose. Stiffness caps an explicit
    method's step for *stability*; accuracy caps it too, and at a tight
    tolerance the accuracy limit is the binding one, so the two methods
    converge in cost and the comparison stops measuring stiffness at all.
    """
    system = build(EXAMPLES["Stiff decay"])

    implicit = solve(system.problem, method="radau", rtol=1e-5, atol=1e-8)
    explicit = solve(
        system.problem, method="dopri5", rtol=1e-5, atol=1e-8, max_steps=200_000
    )
    assert implicit.success and explicit.success
    assert implicit.stats.naccepted < 0.25 * explicit.stats.naccepted, (
        f"radau {implicit.stats.naccepted} vs dopri5 "
        f"{explicit.stats.naccepted} steps"
    )


def test_the_stiffness_advantage_narrows_at_tight_tolerance():
    """The other side of the same coin, stated rather than left implicit."""
    system = build(EXAMPLES["Stiff decay"])
    ratios = {}
    for rtol in (1e-5, 1e-9):
        implicit = solve(system.problem, method="radau", rtol=rtol, atol=rtol * 1e-3)
        explicit = solve(
            system.problem, method="dopri5", rtol=rtol, atol=rtol * 1e-3,
            max_steps=200_000,
        )
        ratios[rtol] = explicit.stats.naccepted / implicit.stats.naccepted

    assert ratios[1e-5] > ratios[1e-9], (
        f"the advantage should shrink as accuracy starts to bind: {ratios}"
    )


def test_all_methods_accept_a_custom_system():
    system = build(EXAMPLES["Damped pendulum"])
    for method in ("dopri5", "tsit5", "rk23", "radau", "rodas4", "taylor20"):
        solution = solve(
            system.problem, method=method, rtol=1e-7, atol=1e-10, max_steps=200_000
        )
        assert solution.success, f"{method}: {solution.message}"
