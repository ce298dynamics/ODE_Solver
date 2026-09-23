"""The eigenvalue method: whether the working is right, not merely present.

A system's answer is a pair of functions, and the ways it can be quietly wrong
are the ways a course warns about: an eigenvector that is not one, a complex
pair turned into real solutions by taking the real part of the exponential and
forgetting the vector, a defective matrix answered with one solution where two
were needed. Each of those is a test here, and each is checked by substituting
back into the system rather than by comparing with a stored answer.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sympy")

import sympy as sp  # noqa: E402

from odesuite_app.systems import (  # noqa: E402
    TITLE,
    classify,
    derive,
    fundamental_matrix,
    matrix_exponential,
    matrix_of,
    split_system,
)

T = sp.Symbol("t", real=True)
X, Y = sp.Function("x"), sp.Function("y")


def _system(a, b, c, d):
    return [sp.Eq(X(T).diff(T), a * X(T) + b * Y(T)),
            sp.Eq(Y(T).diff(T), c * X(T) + d * Y(T))]


def _derive(a, b, c, d, ics=None):
    return derive(_system(a, b, c, d), [X, Y], ics=ics or {})


#: One system per case, and the case is the point of each.
CASES = {
    "distinct": (1, 2, 3, 2),          # eigenvalues -1 and 4: a saddle
    "complex": (0, -1, 1, 0),          # eigenvalues +-i: a centre
    "defective": (3, 1, 0, 3),         # 3 twice, one eigenvector
    "stable": (-2, 1, 1, -2),          # -1 and -3: a stable node
}


# ---------------------------------------------------------------------------
# Reading the system
# ---------------------------------------------------------------------------


def test_the_matrix_is_read_off_the_equations():
    assert matrix_of(_system(1, 2, 3, 2), [X, Y]) == sp.Matrix([[1, 2], [3, 2]])


@pytest.mark.parametrize("equations", [
    # A coefficient that depends on t.
    [sp.Eq(X(T).diff(T), T * X(T)), sp.Eq(Y(T).diff(T), Y(T))],
    # Nonlinear: a product of two unknowns.
    [sp.Eq(X(T).diff(T), X(T) * Y(T)), sp.Eq(Y(T).diff(T), Y(T))],
])
def test_a_system_the_method_does_not_fit_is_declined(equations):
    """Declined rather than narrated badly. A method whose hypotheses have
    failed should say so, not produce steps that look like working."""
    assert split_system(equations, [X, Y]) is None
    assert matrix_of(equations, [X, Y]) is None

    derivation = derive(equations, [X, Y])
    assert derivation.result is None
    assert "constant coefficients" in derivation.message
    assert not derivation.steps


def test_forcing_is_split_off_rather_than_refused():
    """`matrix_of` asks the narrower question -- is this homogeneous -- and a
    forced system is correctly not that. But it is still solvable, and
    `split_system` is what says so."""
    forced = [sp.Eq(X(T).diff(T), X(T) + 2 * Y(T) + sp.exp(T)),
              sp.Eq(Y(T).diff(T), 3 * X(T) + 2 * Y(T))]

    assert matrix_of(forced, [X, Y]) is None
    matrix, forcing = split_system(forced, [X, Y])
    assert matrix == sp.Matrix([[1, 2], [3, 2]])
    assert forcing == sp.Matrix([sp.exp(T), 0])


# ---------------------------------------------------------------------------
# The three cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", list(CASES))
def test_every_case_is_solved_and_verified(case):
    derivation = _derive(*CASES[case])

    assert derivation.title == TITLE
    assert derivation.result is not None, derivation.message
    assert derivation.verified is True
    assert derivation.complete


@pytest.mark.parametrize("case", list(CASES))
def test_no_step_fails_its_own_check(case):
    failed = [s.title for s in _derive(*CASES[case]).steps
              if s.verified is False]
    assert not failed, f"these steps did not verify: {failed}"


def test_the_distinct_case_shows_an_eigenvector_for_each_eigenvalue():
    titles = [s.title for s in _derive(*CASES["distinct"]).steps]
    assert sum(1 for t in titles if t.startswith("An eigenvector")) == 2
    assert "Each pair gives a solution" in titles


def test_the_complex_case_takes_the_vector_apart_too():
    """The step people get wrong: the eigenvector has complex entries, so
    Euler's formula mixes them into both real solutions. Taking the real part
    of the exponential and leaving the vector alone is the classic error, and
    it produces something that does not solve the system."""
    derivation = _derive(*CASES["complex"])
    titles = [s.title for s in derivation.steps]

    assert "Euler's formula, on the vector as well" in titles
    assert "Its real and imaginary parts are the two solutions" in titles
    # Only one of the conjugate pair is worked through.
    assert sum(1 for t in titles if t.startswith("An eigenvector")) == 1

    step = next(s for s in derivation.steps
                if s.title == "Its real and imaginary parts are the two "
                              "solutions")
    assert step.verified is True


def test_the_complex_answer_is_real():
    """A real system deserves a real answer. Leaving an i in it would be
    correct and useless."""
    result = _derive(*CASES["complex"]).result
    assert not result.has(sp.I)


def test_the_defective_case_builds_a_generalised_eigenvector():
    derivation = _derive(*CASES["defective"])
    titles = [s.title for s in derivation.steps]

    assert "There is only one eigenvector" in titles
    assert "A generalised eigenvector supplies the second" in titles
    assert "The second solution carries a t" in titles

    step = next(s for s in derivation.steps
                if s.title == "A generalised eigenvector supplies the second")
    assert step.verified is True


def test_the_defective_second_solution_really_has_a_t():
    """(vt + w)e^{λt}, not w·e^{λt}. Without the t it does not solve the
    system at all, which is what the step's own check would catch."""
    result = _derive(*CASES["defective"]).result
    assert result.has(T)
    # The t survives simplification rather than cancelling away.
    assert any(entry.has(T) and entry.has(sp.exp) for entry in result)


def test_a_repeated_eigenvalue_that_is_not_defective_takes_the_plain_route():
    """3I has a double eigenvalue and two eigenvectors, so nothing generalised
    is needed. Assuming repetition means defective is the mistake here."""
    titles = [s.title for s in _derive(3, 0, 0, 3).steps]
    assert "A generalised eigenvector supplies the second" not in titles


# ---------------------------------------------------------------------------
# Conditions, and what the origin is
# ---------------------------------------------------------------------------


def test_initial_conditions_pin_the_constants():
    derivation = _derive(*CASES["distinct"], ics={X(0): 1, Y(0): 0})

    assert derivation.complete
    assert not derivation.result.free_symbols - {T}
    assert float(derivation.result[0].subs(T, 0)) == pytest.approx(1.0)
    assert float(derivation.result[1].subs(T, 0)) == pytest.approx(0.0)


def test_one_condition_short_is_reported_rather_than_guessed():
    derivation = _derive(*CASES["distinct"], ics={X(0): 1})
    assert "one condition per unknown" in derivation.message


def test_conditions_survive_sympys_cache_being_full():
    """The bug this is here for is invisible until a session gets long.

    `sp.Function("x")` is memoised, so two calls normally hand back one object
    and matching a condition to its unknown by identity looks safe. But sympy's
    cache is an `lru_cache` bounded at `SYMPY_CACHE_SIZE`, which defaults to a
    thousand entries: once that many other functions and symbols have been
    built, the entry for "x" is evicted and the next `Function("x")` is a
    *different* class, still equal to the first. Under identity the conditions
    then matched nothing, and `derive` reported "one condition per unknown is
    needed" about a pair that had been supplied -- handing back the general
    solution where a particular one was asked for, silently.

    It surfaced as a full-suite failure that passed on its own, which is the
    signature of exactly this: nothing to do with the test before it, only with
    how much sympy had been made to build first. Filling the cache here makes
    it deterministic and costs about a tenth of a second.
    """
    evicted = sp.Function("x")
    for index in range(3000):
        sp.Function(f"cachefiller{index}")
    assert sp.Function("x") is not evicted, (
        "sympy no longer evicts, and this test is no longer testing anything"
    )

    fresh_x, fresh_y = sp.Function("x"), sp.Function("y")
    system = [sp.Eq(fresh_x(T).diff(T), CASES["distinct"][0] * fresh_x(T)
                    + CASES["distinct"][1] * fresh_y(T)),
              sp.Eq(fresh_y(T).diff(T), CASES["distinct"][2] * fresh_x(T)
                    + CASES["distinct"][3] * fresh_y(T))]
    # The conditions are keyed by the *stale* classes, which is the situation
    # the application is in: the parse that made them happened earlier.
    derivation = derive(system, [fresh_x, fresh_y],
                        ics={evicted(0): 1, sp.Function("y")(0): 0})

    assert derivation.complete
    assert not derivation.result.free_symbols - {T}
    assert float(derivation.result[0].subs(T, 0)) == pytest.approx(1.0)


@pytest.mark.parametrize("entries,expected", [
    ((1, 2, 3, 2), "saddle"),
    ((-2, 1, 1, -2), "stable node"),
    ((2, 1, 1, 2), "unstable node"),
    ((0, -1, 1, 0), "centre"),
    ((-1, -2, 2, -1), "stable spiral"),
    ((1, -2, 2, 1), "unstable spiral"),
])
def test_the_origin_is_named_from_the_eigenvalues_alone(entries, expected):
    values = sp.Matrix([[entries[0], entries[1]],
                        [entries[2], entries[3]]]).eigenvals()
    spread = [value for value, count in values.items() for _ in range(count)]
    assert expected in classify(spread)


def test_the_classification_reaches_the_derivation():
    step = next(s for s in _derive(*CASES["distinct"]).steps
                if s.title == "What the origin is")
    assert "saddle" in step.note


# ---------------------------------------------------------------------------
# The shape everything else depends on
# ---------------------------------------------------------------------------


def test_the_answer_is_a_column_not_a_scalar():
    """The whole point of a system: the answer is one function per unknown,
    and the renderer, the wire format and `check_answer` all expect that."""
    result = _derive(*CASES["distinct"]).result
    assert isinstance(result, sp.MatrixBase)
    assert result.shape == (2, 1)


def test_it_never_raises_on_a_system_it_cannot_do():
    """`derive` is called on whatever a user typed, so failing has to be a
    message rather than an exception."""
    nonsense = [sp.Eq(X(T).diff(T, 2), X(T)), sp.Eq(Y(T).diff(T), Y(T))]
    derivation = derive(nonsense, [X, Y])
    assert derivation.result is None
    assert derivation.message


def test_systems_needs_no_interface_toolkit():
    """It runs inside the solver subprocess, where PySide6 is not imported."""
    import subprocess
    import sys

    code = (
        "import sys; sys.modules['PySide6'] = None\n"
        "import odesuite_app.systems as m; assert m.TITLE\n"
    )
    done = subprocess.run([sys.executable, "-c", code], capture_output=True,
                          text=True)
    assert done.returncode == 0, done.stderr[-400:]


# ---------------------------------------------------------------------------
# Forcing: varying the constants
# ---------------------------------------------------------------------------


FORCED = [sp.Eq(X(T).diff(T), X(T) + 2 * Y(T) + sp.exp(T)),
          sp.Eq(Y(T).diff(T), 3 * X(T) + 2 * Y(T))]


def test_a_forced_system_is_solved_and_verified():
    derivation = derive(FORCED, [X, Y])

    assert derivation.result is not None, derivation.message
    assert derivation.verified is True
    assert derivation.complete
    assert not [s for s in derivation.steps if s.verified is False]


def test_the_forced_narration_solves_the_homogeneous_part_first():
    titles = [s.title for s in derive(FORCED, [X, Y]).steps]

    assert "The homogeneous solution" in titles
    assert "Build the fundamental matrix" in titles
    assert "Vary the constants" in titles
    assert "A particular solution" in titles
    assert titles[-1] == "The general solution"
    # The origin is not classified for a forced system: with forcing there is
    # generally no equilibrium at the origin to classify.
    assert "What the origin is" not in titles


def test_the_basis_is_judged_against_the_homogeneous_system():
    """The fundamental set solves x' = Ax, not the forced system. Checking it
    against the forced one would report a correct basis as wrong -- the trap
    the second-order narrator documents and this one has to avoid too."""
    step = next(s for s in derive(FORCED, [X, Y]).steps
                if s.title == "Each pair gives a solution")
    assert step.verified is True


def test_the_particular_solution_carries_no_constants():
    derivation = derive(FORCED, [X, Y])
    step = next(s for s in derivation.steps
                if s.title == "A particular solution")
    assert "C_{1}" not in step.latex and "C_{2}" not in step.latex


def test_conditions_apply_to_a_forced_system():
    derivation = derive(FORCED, [X, Y], ics={X(0): 1, Y(0): 0})

    assert derivation.complete
    assert not derivation.result.free_symbols - {T}
    assert sp.simplify(derivation.result[0].subs(T, 0) - 1) == 0
    assert sp.simplify(derivation.result[1].subs(T, 0)) == 0


def test_a_homogeneous_system_is_untouched_by_the_forcing_branch():
    """The path every other lesson in the unit uses must not change."""
    titles = [s.title for s in _derive(*CASES["distinct"]).steps]
    assert "Build the fundamental matrix" not in titles
    assert titles[-1] == "What the origin is"


def test_the_fundamental_matrix_is_the_basis_as_columns():
    basis = [sp.Matrix([1, 1]) * sp.exp(-T), sp.Matrix([2, 3]) * sp.exp(4 * T)]
    phi = fundamental_matrix(basis)

    assert phi.shape == (2, 2)
    assert phi[:, 0] == basis[0]
    assert sp.simplify(phi.det()) != 0


def test_the_matrix_exponential_is_the_identity_at_zero():
    """Any two fundamental matrices differ by a constant matrix on the right;
    e^{At} is the one normalised so that x(t) = e^{At}x(0)."""
    exponential = matrix_exponential(sp.Matrix([[1, 2], [3, 2]]))

    assert sp.simplify(exponential.subs(T, 0) - sp.eye(2)) == sp.zeros(2, 2)
    # And it solves the system, column by column.
    assert sp.simplify(exponential.diff(T)
                       - sp.Matrix([[1, 2], [3, 2]]) * exponential) == \
        sp.zeros(2, 2)
