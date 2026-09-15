"""The expression parser must not execute anything.

`sympy.parsing.parse_expr` compiles its input and evaluates it. `custom.py`
already empties ``__builtins__`` so that no *name* resolves to anything
dangerous -- but a name whitelist cannot stop an expression walking out through
an *attribute*. ``sin`` is on the whitelist, and

    sin.__class__.__init__.__globals__["__builtins__"]

is the real builtins, ``__import__`` included. That is arbitrary code execution
from an equation someone typed, and it reached both places a user can type one:
the "build your own system" editor (`custom.build`) and the equation editor
(`symbolic.parse_equation`).

These tests are the record of that. Each payload is fed through the same call
the interface makes, and a canary file proves the difference between "returned
something odd" and "ran".

The second half matters as much as the first: a guard that rejects
``sec(t)`` or ``atan2(y, x)`` would be a worse bug than the one it fixes, so
every shape the application itself parses is asserted to still work.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sympy")

from odesuite_app import custom, symbolic  # noqa: E402
from odesuite_app.custom import CustomSpec, ParseError  # noqa: E402

#: Escapes. Every one of these either reached the real builtins or walked the
#: type hierarchy towards them; the first is the one that was demonstrated to
#: execute.
ESCAPES = [
    'sin.__class__.__init__.__globals__["__builtins__"]',
    'sin.__class__.__init__.__globals__["__builtins__"]["__import__"]("os")',
    "().__class__.__base__.__subclasses__()",
    "(1).__class__.__mro__[1].__subclasses__()",
    "sin(t).__reduce__()",
    "Symbol.__subclasshook__",
    "sin.__globals__",
    '__import__("os").system("echo pwned")',
    'eval("1+1")',
    'exec("import os")',
    "[x for x in ().__class__.__mro__]",
    "(lambda: 1)()",
    "globals()",
    "t.__class__",
]


def _canary_payload(path) -> str:
    """An expression that writes `path` if -- and only if -- it is executed."""
    return (
        'sin.__class__.__init__.__globals__["__builtins__"]["open"]'
        f"({str(path)!r}, 'w').write('pwned')"
    )


# ---------------------------------------------------------------------------
# The escapes must be refused
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("payload", ESCAPES)
def test_custom_build_refuses_an_escape(payload):
    spec = CustomSpec(variables=["x"], expressions=[payload], initial=[1.0])
    with pytest.raises(ParseError):
        custom.build(spec)


@pytest.mark.parametrize("payload", ESCAPES)
def test_the_equation_editor_refuses_an_escape(payload):
    with pytest.raises(ParseError):
        symbolic.parse_equation(symbolic.spec_for(f"y' = {payload}"))


def test_custom_build_does_not_execute_the_payload(tmp_path):
    canary = tmp_path / "canary.txt"
    spec = CustomSpec(
        variables=["x"], expressions=[_canary_payload(canary)], initial=[1.0]
    )
    with pytest.raises(ParseError):
        custom.build(spec)
    assert not canary.exists(), "the expression was executed"


def test_the_equation_editor_does_not_execute_the_payload(tmp_path):
    canary = tmp_path / "canary.txt"
    with pytest.raises(ParseError):
        symbolic.parse_equation(
            symbolic.spec_for(f"y' = {_canary_payload(canary)}")
        )
    assert not canary.exists(), "the expression was executed"


def test_initial_conditions_are_checked_too(tmp_path):
    """`parse_initial_conditions` is a second door into the same parser."""
    canary = tmp_path / "canary.txt"
    spec = symbolic.spec_for("y' = y", f"y(0) = {_canary_payload(canary)}")
    with pytest.raises(ParseError):
        parsed = symbolic.parse_equation(spec)
        symbolic.parse_initial_conditions(parsed.spec, parsed.functions)
    assert not canary.exists(), "the expression was executed"


def test_a_typed_answer_is_checked_too(tmp_path):
    """`check_answer` parses whatever the learner typed into the answer box.

    It reports rather than raises, so the assertion is that nothing ran.
    """
    canary = tmp_path / "canary.txt"
    parsed = symbolic.parse_equation(symbolic.spec_for("y' = -2*y"))
    symbolic.check_answer(parsed, _canary_payload(canary))
    assert not canary.exists(), "the expression was executed"


# ---------------------------------------------------------------------------
# ...without refusing mathematics
# ---------------------------------------------------------------------------

#: Right-hand sides in the shape `custom.build` takes them. `sec` is here on
#: purpose: it is whitelisted precisely because variation of parameters is
#: taught on `y'' + y = sec(t)`.
LEGITIMATE_RHS = [
    "-2*x",
    "x*cos(t)",
    "mu*(1 - x**2)*v - x",
    "r*x*(1 - x/K)",
    "sec(t)",
    "exp(-t)*sin(3*t)",
    "sqrt(Abs(x))",
    "-(g/L)*sin(x) - c*v",
    "a*x - b*x*v",
    "3*t^2 + 1",
    "Max(0, x)",
    "atan2(x, v)",
    "1/(1 + t**2)",
    "tanh(x) + sinh(v) - cosh(t)",
    "pi*x + E",
]


@pytest.mark.parametrize("rhs", LEGITIMATE_RHS)
def test_legitimate_right_hand_sides_still_parse(rhs):
    spec = CustomSpec(
        variables=["x", "v"],
        expressions=[rhs, "-x"],
        initial=[1.0, 0.0],
        parameters={"mu": 1.0, "r": 1.0, "K": 1.0, "g": 9.8,
                    "L": 1.0, "c": 0.1, "a": 1.0, "b": 1.0},
    )
    custom.build(spec)


def test_every_shipped_custom_example_still_builds():
    for name, spec in custom.EXAMPLES.items():
        custom.build(spec), f"{name} stopped building"


def test_every_shipped_equation_example_still_parses():
    for name, spec in symbolic.EXAMPLES.items():
        parsed = symbolic.parse_equation(spec)
        symbolic.parse_initial_conditions(parsed.spec, parsed.functions)
        assert parsed.equations, f"{name} parsed to nothing"


def test_every_lesson_equation_still_parses():
    """The corpus that matters: everything the course itself asks the parser
    to read. A guard that broke one of these would break a lesson.

    `EXTRA_FUNCTIONS` is passed because that is what the lesson screens do
    (`screens/learn_lessons.py:105`) -- the Laplace unit's equations use
    `Heaviside` and `DiracDelta`, which are deliberately not typeable
    everywhere.
    """
    from odesuite_app import lessons as L
    from odesuite_app.laplace import EXTRA_FUNCTIONS

    checked = 0
    for lesson in L.LESSONS:
        for item in (*lesson.examples, *lesson.questions):
            equation = getattr(item, "equation", None)
            if not equation:
                continue
            spec = symbolic.spec_for(
                equation, getattr(item, "conditions", "") or ""
            )
            symbolic.parse_equation(spec, extra_functions=EXTRA_FUNCTIONS)
            checked += 1
    assert checked > 100, f"only {checked} lesson equations were checked"


def test_every_drill_template_draw_still_parses():
    """Generated questions are a different shape from hand-written ones -- a
    format string with numbers substituted in and then tidied -- so they get
    their own pass.

    `tests/test_templates.py` checks these far more thoroughly (it asserts
    every draw is *solvable*, not merely parseable). This is the cheap version,
    here so the guard's compatibility can be read in one file.
    """
    from odesuite_app.laplace import EXTRA_FUNCTIONS
    from odesuite_app.lessons import LESSONS, generate

    checked = 0
    for lesson in LESSONS:
        for template in (lesson.templates or ()):
            if template.kind != "template":
                continue        # choice/numeric drills carry no equation
            for seed in range(4):
                question = generate.draw(template, seed)
                symbolic.parse_equation(
                    symbolic.spec_for(question.equation, question.conditions),
                    extra_functions=EXTRA_FUNCTIONS,
                )
                checked += 1
    assert checked > 40, f"only {checked} generated questions were checked"


# ---------------------------------------------------------------------------
# The guard itself
# ---------------------------------------------------------------------------


def test_the_guard_names_what_it_refused():
    """The message reaches a text box, so it has to say something useful."""
    with pytest.raises(ParseError) as caught:
        custom.build(
            CustomSpec(variables=["x"], expressions=["sin.__class__"],
                       initial=[1.0])
        )
    assert "attribute" in str(caught.value).lower()


def test_a_plain_decimal_is_not_mistaken_for_attribute_access():
    """`2.5` contains a dot and must survive."""
    custom.build(
        CustomSpec(variables=["x"], expressions=["2.5*x - 0.5"], initial=[1.0])
    )
