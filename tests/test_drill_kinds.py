"""The four later drill kinds, and the oracle each one is held to.

Every drill in this application used to hand the student an equation and ask
what to do with it. These four ask the other questions a course asks:

* `ClassifyTemplate` -- *which method would you reach for first*, and the same
  question about a phase portrait and about a damping regime.
* `ModelTemplate` -- *write the equation*, from a situation or from the family
  of curves that solves it.
* `ExpressionTemplate` -- *write one move of the method*: the integrating
  factor, the characteristic polynomial, the Wronskian.
* `FaultTemplate` -- *what went wrong here*, over an answer with one named
  mistake in it.

All four store something, which none of the earlier kinds had to. A `Solve`
stores no answer at all because substituting *is* the grading, and that is the
property this file exists to buy back: **nothing stored here is taken on
trust.** Each kind has a routine in the application that decides its answers
independently, and every draw of every template is put through it.

    which method    -> classify_ode + steps.preferred_hint, the dispatch the
                       narrator itself uses
    which portrait  -> analysis.classify, the routine the Phase Portrait screen
                       prints from
    which regime    -> the sign of c^2 - 4mk
    write the equation -> symbolic.check_model, against a rearrangement sympy
                       produced rather than one an author typed
    one move        -> a property of the thing asked for: an integrating factor
                       differentiates back, a characteristic polynomial has the
                       roots the equation has
    what went wrong -> symbolic.check_answer, which has to return the verdict
                       the named fault claims

So a question here cannot quietly disagree with the tool that would answer it,
and cannot go on claiming an answer the application has stopped giving. The
worst question this application could ship is a *spot the mistake* whose
mistake is not one, and `test_a_generated_wrong_answer_is_really_wrong` is what
stands in front of it.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sympy")

import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

from odesuite_app import steps  # noqa: E402
from odesuite_app.lessons import LESSONS, generate  # noqa: E402
from odesuite_app.lessons.model import TIERS  # noqa: E402
from odesuite_app.lessons.vocabulary import (  # noqa: E402
    FAULTS,
    VOCABULARIES,
)
from odesuite_app.symbolic import (  # noqa: E402
    check_answer,
    check_expression,
    check_model,
    parse_equation,
    spec_for,
)

T = sp.Symbol("t", real=True)


def _expr(text: str):
    """Stored text as sympy, in the same `t` the rest of the project uses.

    `sympify` left to itself makes a fresh, assumption-free ``t``, and
    differentiating with respect to the project's real one then gives zero --
    which looks exactly like a correct answer failing its own property check.
    """
    return sp.sympify(text, locals={"t": T, "s": sp.Symbol("s")})


def _of_kind(kind):
    return [(lesson, template) for lesson in LESSONS
            for template in lesson.templates if template.kind == kind]


def _ids(pairs):
    return [f"{lesson.key}-{template.key}" for lesson, template in pairs]


CLASSIFY = _of_kind("classify-template")
MODELS = _of_kind("model-template")
EXPRESSIONS = _of_kind("expression-template")
FAULTY = _of_kind("fault-template")

CLASSIFY_IDS = _ids(CLASSIFY)
MODEL_IDS = _ids(MODELS)
EXPRESSION_IDS = _ids(EXPRESSIONS)
FAULT_IDS = _ids(FAULTY)


def _parsed(equation: str, conditions: str = ""):
    from odesuite_app.laplace import EXTRA_FUNCTIONS

    return parse_equation(spec_for(equation, conditions),
                          extra_functions=EXTRA_FUNCTIONS)


# ---------------------------------------------------------------------------
# Which method, which portrait, which regime
# ---------------------------------------------------------------------------


def _technique_of(equation: str) -> str:
    """What the application would narrate this equation as.

    The dispatch `steps.derive` performs, stopping short of the narration
    itself: `classify_ode` for the hints, `preferred_hint` to choose among
    them in teaching order, and the structural detector for the one family
    `classify_ode` is not authoritative about. Running the full narrator would
    be more faithful and would cost a second an equation; this is the same
    decision, and it is the decision the drill is claiming.
    """
    from sympy.solvers.ode import classify_ode

    parsed = _parsed(equation)
    hints = classify_ode(parsed.equation, parsed.function(T))
    return (steps.preferred_hint(hints)
            or steps.detected(steps._exact(parsed.equation), parsed.function))


def _matrix_of(equation: str) -> sp.Matrix:
    """The coefficient matrix of a linear system written as one string."""
    parsed = _parsed(equation)
    unknowns = [function(T) for function in parsed.functions]
    # By differentiation rather than by `linear_eq_to_matrix`, which refuses
    # an expression containing ``Derivative(x(t), t)`` as nonlinear. For a
    # linear system the partial derivative of the right-hand side with
    # respect to each unknown *is* the coefficient, and it needs no rewriting
    # to get at it.
    return sp.Matrix([[sp.diff(equation.rhs, unknown) for unknown in unknowns]
                      for equation in parsed.equations])


def _regime_of(equation: str) -> str:
    """Which damping regime, from the sign of the discriminant."""
    parsed = _parsed(equation)
    y = parsed.function(T)
    poly = sp.Poly(sp.expand(parsed.equation.lhs - parsed.equation.rhs),
                   [sp.Derivative(y, (T, 2)), sp.Derivative(y, T), y])
    mass = poly.coeff_monomial(sp.Derivative(y, (T, 2)))
    damping = poly.coeff_monomial(sp.Derivative(y, T))
    stiffness = poly.coeff_monomial(y)
    if damping == 0:
        return "undamped"
    discriminant = damping ** 2 - 4 * mass * stiffness
    if discriminant > 0:
        return "overdamped"
    return "critically damped" if discriminant == 0 else "underdamped"


def _equilibrium_of(case) -> str:
    """What linearising says at `case.at`, through the Phase Portrait's own
    routines: `analysis.jacobian_at` on the system, then `analysis.classify`.

    A linear centre and every other non-hyperbolic answer are "undecided" --
    for a nonlinear system the Jacobian cannot settle them. And the point has
    to *be* an equilibrium, or the question is about nothing.
    """
    from odesuite import ODEProblem
    from odesuite_app import analysis

    x, y = sp.symbols("x y")
    sides = [part.split("=", 1)[1] for part in case.equation.split(";")]
    f = sp.lambdify((x, y), [sp.sympify(side, locals={"x": x, "y": y})
                             for side in sides], "numpy")
    point = np.array([float(sp.sympify(value))
                      for value in case.at.strip("()").split(",")])
    if np.max(np.abs(f(*point))) > 1e-9:
        return f"not an equilibrium: f{case.at} = {f(*point)}"
    problem = ODEProblem(f=lambda t, z: np.array(f(z[0], z[1]), dtype=float),
                         t_span=(0.0, 1.0), y0=point)
    kind, _ = analysis.classify(
        np.linalg.eigvals(analysis.jacobian_at(problem, point)))
    return "undecided" if kind in ("centre", "non-hyperbolic") else kind


#: How each vocabulary's answers are checked. A `ClassifyTemplate` naming a
#: table with no oracle here fails `test_every_vocabulary_has_an_oracle`,
#: which is the point: the table is what makes the drill honest, and a table
#: nothing checks is a stored answer key with extra steps. Each takes the whole
#: `Case`, because an equilibrium question needs its point as well.
ORACLES = {
    "methods": lambda case: _technique_of(case.equation),
    "portraits": lambda case: __import__(
        "odesuite_app.analysis", fromlist=["classify"]
    ).classify(
        np.linalg.eigvals(np.array(_matrix_of(case.equation).tolist(),
                                   dtype=float))
    )[0],
    "damping": lambda case: _regime_of(case.equation),
    "equilibria": _equilibrium_of,
}


def test_every_vocabulary_has_an_oracle():
    assert set(ORACLES) == set(VOCABULARIES), (
        "a vocabulary with nothing to check it against is an answer key"
    )


@pytest.mark.parametrize("lesson,template", CLASSIFY, ids=CLASSIFY_IDS)
def test_a_classify_drill_is_well_formed(lesson, template):
    where = f"{lesson.key}/{template.key}"
    table = VOCABULARIES[template.table]
    assert len(template.options) >= 3, f"{where}: too few to be a choice"
    assert len(set(template.options)) == len(template.options)
    for key in template.options:
        assert key in table, f"{where}: {key!r} is not in {template.table}"
    assert template.cases, f"{where}: nothing to ask about"
    seen = set()
    for case in template.cases:
        assert case.technique in template.options, (
            f"{where}: {case.equation} claims {case.technique}, which is not "
            "on the menu"
        )
        assert len(case.why) > 40, f"{where}: {case.equation} says too little"
        assert case.tier in TIERS
        # The same system at two different points is two questions, and the
        # equilibrium drill asks exactly that on purpose.
        asked = (case.equation, case.at)
        assert asked not in seen, f"{where}: {case.equation} {case.at} twice"
        seen.add(asked)


@pytest.mark.parametrize("lesson,template", CLASSIFY, ids=CLASSIFY_IDS)
def test_every_option_on_the_menu_is_the_answer_to_something(lesson, template):
    """A distractor nobody's case uses is fine; a menu where one option is
    *never* right is a pattern to learn instead of a question."""
    used = {case.technique for case in template.cases}
    unused = [key for key in template.options if key not in used]
    assert len(unused) <= 1, (
        f"{lesson.key}/{template.key}: {unused} are never the answer"
    )


@pytest.mark.parametrize("lesson,template", CLASSIFY, ids=CLASSIFY_IDS)
def test_the_application_agrees_with_every_case(lesson, template):
    """The claim this drill rests on, checked case by case.

    Not "an author believes this is separable" but "this application, asked
    today, says separable" -- so the drill and the tool that would answer the
    question cannot come apart, and a change of mind in sympy shows up here
    rather than in front of a student.
    """
    oracle = ORACLES[template.table]
    for case in template.cases:
        assert oracle(case) == case.technique, (
            f"{lesson.key}/{template.key}: {case.equation} {case.at} is "
            f"claimed to be {case.technique}, and the application says "
            f"{oracle(case)}"
        )


@pytest.mark.parametrize("lesson,template", CLASSIFY, ids=CLASSIFY_IDS)
def test_the_shuffle_keeps_the_answer_with_its_case(lesson, template):
    table = VOCABULARIES[template.table]
    for seed, case in enumerate(generate.draws(template)):
        question = generate.draw(template, seed)
        assert question.options[question.answer] == table[case.technique].title
        assert question.becauses[question.answer] == case.why
        assert question.shown == generate.case_shown(case)
        if case.at:
            assert case.at in question.shown, "the point must be shown"


def test_the_answer_does_not_sit_still():
    """Shuffling is the whole defence of a fixed menu of options, and a drill
    whose answer stayed at one index would teach the index."""
    for _lesson, template in CLASSIFY:
        places = {generate.draw(template, seed).answer
                  for seed in range(generate.combinations(template))}
        assert len(places) > 1, f"{template.key}: the answer never moves"


# ---------------------------------------------------------------------------
# Write the equation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lesson,template", MODELS, ids=MODEL_IDS)
def test_every_model_draw_is_an_equation_the_grader_accepts(lesson, template):
    """The reference equation, rearranged three ways and handed back in.

    Checking ``check_model(reference, reference)`` would test nothing but
    string equality. What is worth checking is that the grader accepts forms
    *nobody typed*: everything moved to one side, the sides swapped, and the
    whole thing multiplied through. Those are what a student who arranged it
    differently actually produces, and all three have to pass.

    Rearranged as text rather than through sympy, deliberately. The parsed
    form prints as ``Derivative(ODEDZyZ0(t), t)`` -- the internal placeholder
    -- which is not something anybody could type, so a test built on it would
    be checking a route no student can take.
    """
    for question in generate.every(template):
        where = f"{template.key}: {question.equation}"
        left, right = question.equation.split("=")
        for rearranged in (f"({left}) - ({right}) = 0",
                           f"0 = ({right}) - ({left})",
                           f"3*({left}) = 3*({right})"):
            verdict = check_model(question.equation, rearranged)
            assert verdict.correct is True, (
                f"{where}: {rearranged!r} -- {verdict.message}"
            )


@pytest.mark.parametrize("lesson,template", MODELS, ids=MODEL_IDS)
def test_a_model_drill_refuses_a_different_equation(lesson, template):
    """The grader has to be able to say no, or the streak means nothing."""
    for seed in range(min(4, generate.combinations(template))):
        question = generate.draw(template, seed)
        verdict = check_model(question.equation, "y' = t + 7")
        assert verdict.correct is not True, question.equation


@pytest.mark.parametrize("lesson,template", MODELS, ids=MODEL_IDS)
def test_a_model_drill_says_why_and_offers_a_ladder(lesson, template):
    assert len(template.hints) >= 2, f"{template.key}: a hint is not a ladder"
    for question in generate.every(template):
        assert len(question.because) > 40, f"{template.key}: no account given"


# ---------------------------------------------------------------------------
# One move of the method
# ---------------------------------------------------------------------------


def _integrating_factor_holds(question, slots) -> None:
    """mu' = p*mu, which is the whole definition of an integrating factor."""
    mu = _expr(question.answer)
    p = _expr(slots["p"])
    assert sp.simplify(sp.diff(mu, T) - p * mu) == 0, (
        f"{question.answer} is not an integrating factor for p = {p}"
    )


def _characteristic_polynomial_holds(question, slots) -> None:
    """Its roots are the exponents the equation's own analysis finds."""
    from odesuite_app.symbolic import characteristic_analysis

    r = sp.Symbol("r")
    written = sp.Poly(_expr(question.answer), r)
    poly = characteristic_analysis(_parsed(slots["equation"]))["poly"]
    # The analysis names the variable itself; whatever it calls it, it is the
    # same polynomial, so it is renamed rather than assumed.
    named = poly.subs({symbol: r for symbol in poly.free_symbols})
    wanted = sp.Poly(named, r)
    assert sp.simplify(written.as_expr() * wanted.LC()
                       - wanted.as_expr() * written.LC()) == 0, (
        f"{question.answer} is not the characteristic polynomial of "
        f"{slots['equation']}: that is {wanted.as_expr()}"
    )


def _wronskian_holds(question, slots) -> None:
    first, second = _expr(slots["y1"]), _expr(slots["y2"])
    wanted = sp.simplify(first * sp.diff(second, T) - second * sp.diff(first, T))
    assert sp.simplify(_expr(question.answer) - wanted) == 0, (
        f"{question.answer} is not the Wronskian of {first} and {second}: "
        f"that is {wanted}"
    )


def _transform_holds(question, slots) -> None:
    s = sp.Symbol("s", positive=True)
    wanted = sp.laplace_transform(_expr(slots["f"]), T, s, noconds=True)
    assert sp.simplify(_expr(question.answer).subs(sp.Symbol("s"), s)
                       - wanted) == 0, (
        f"{question.answer} is not the transform of {slots['f']}: that is "
        f"{wanted}"
    )


def _eigen_polynomial_holds(question, slots) -> None:
    r = sp.Symbol("r")
    matrix = sp.Matrix([[_expr(slots["a"]), _expr(slots["b"])],
                        [_expr(slots["c"]), _expr(slots["d"])]])
    wanted = matrix.charpoly(r).as_expr()
    written = _expr(question.answer)
    assert sp.simplify(written - wanted) == 0, (
        f"{question.answer} is not det(A - rI) for {matrix.tolist()}: that is "
        f"{wanted}"
    )


#: One property per expression drill, checked on every draw.
#:
#: The list gates, the way `FULL_DEPTH` does in `test_lessons.py`: an
#: expression template cannot be added without something here that knows how to
#: check what it asks for. A stored answer nothing verifies is exactly the
#: thing this application does not ship.
PROPERTIES = {
    "the-integrating-factor": _integrating_factor_holds,
    "the-characteristic-equation": _characteristic_polynomial_holds,
    "the-wronskian": _wronskian_holds,
    "the-transform": _transform_holds,
    "det-a-minus-lambda": _eigen_polynomial_holds,
}


def test_every_expression_drill_has_a_property_that_checks_it():
    keys = {template.key for _lesson, template in EXPRESSIONS}
    assert keys <= set(PROPERTIES), (
        f"no property checks {sorted(keys - set(PROPERTIES))}"
    )


@pytest.mark.parametrize("lesson,template", EXPRESSIONS, ids=EXPRESSION_IDS)
def test_every_expression_answer_is_what_it_claims_to_be(lesson, template):
    check = PROPERTIES[template.key]
    for seed, slots in enumerate(generate.draws(template)):
        check(generate.draw(template, seed), slots)


@pytest.mark.parametrize("lesson,template", EXPRESSIONS, ids=EXPRESSION_IDS)
def test_the_grader_accepts_the_answer_the_drill_expects(lesson, template):
    for question in generate.every(template):
        verdict = check_expression(question.answer, question.answer,
                                   up_to_constant=question.up_to_constant)
        assert verdict.correct is True, f"{question.answer}: {verdict.message}"


@pytest.mark.parametrize("lesson,template", EXPRESSIONS, ids=EXPRESSION_IDS)
def test_an_expression_drill_refuses_something_else(lesson, template):
    for seed in range(min(4, generate.combinations(template))):
        question = generate.draw(template, seed)
        verdict = check_expression(question.answer, "t + 11",
                                   up_to_constant=question.up_to_constant)
        assert verdict.correct is not True, question.answer


@pytest.mark.parametrize("lesson,template", EXPRESSIONS, ids=EXPRESSION_IDS)
def test_an_expression_drill_says_why_and_offers_a_ladder(lesson, template):
    assert len(template.hints) >= 2
    for question in generate.every(template):
        assert len(question.because) > 40


# ---------------------------------------------------------------------------
# What went wrong
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("lesson,template", FAULTY, ids=FAULT_IDS)
def test_a_fault_drill_is_well_formed(lesson, template):
    where = f"{lesson.key}/{template.key}"
    assert template.fault in FAULTS, f"{where}: {template.fault!r} is not one"
    assert template.fault not in template.others, f"{where}: answer repeated"
    for key in template.others:
        assert key in FAULTS, f"{where}: {key!r} is not one"
    assert len(template.others) >= 2, f"{where}: too few to be a choice"


@pytest.mark.parametrize("lesson,template", FAULTY, ids=FAULT_IDS)
def test_a_generated_wrong_answer_is_really_wrong(lesson, template):
    """The worst question this application could ask is a *spot the mistake*
    whose mistake is not one. Every draw goes through the grader.

    Two verdicts count as wrong and the fault says which to expect. A sign
    error does not satisfy the equation at all. A dropped constant does --
    what it fails is the initial condition, and a drill that asked about it
    without giving one would be asking about nothing.
    """
    fault = FAULTS[template.fault]
    for seed, slots in enumerate(generate.draws(template)):
        equation = generate.tidy(template.equation.format(**slots))
        conditions = template.conditions.format(**slots)
        wrong = generate.tidy(template.wrong.format(**slots))
        where = f"{template.key}#{seed}: {equation} -> {wrong}"

        if fault.solves_equation:
            assert conditions, (
                f"{where}: this fault only shows against a condition, and "
                "the drill gives none"
            )
        verdict = check_answer(_parsed(equation, conditions), wrong)
        if fault.solves_equation:
            assert verdict.correct is True, f"{where}: {verdict.message}"
            assert verdict.matches_conditions is False, (
                f"{where}: it meets the conditions too, so it is not wrong"
            )
        else:
            assert verdict.correct is False, f"{where}: {verdict.message}"


@pytest.mark.parametrize("lesson,template", FAULTY, ids=FAULT_IDS)
def test_the_shuffle_keeps_the_fault_with_its_description(lesson, template):
    for seed in range(generate.combinations(template)):
        question = generate.draw(template, seed)
        assert question.options[question.answer] == FAULTS[template.fault].label
        assert question.becauses[question.answer] == FAULTS[template.fault].tell
        assert question.shown, "the question never shows what it is about"


# ---------------------------------------------------------------------------
# Tiers
# ---------------------------------------------------------------------------


ALL_TEMPLATES = [(lesson, template) for lesson in LESSONS
                 for template in lesson.templates]
ALL_IDS = _ids(ALL_TEMPLATES)


@pytest.mark.parametrize("lesson,template", ALL_TEMPLATES, ids=ALL_IDS)
def test_every_tier_a_template_names_is_a_real_one_with_draws_in_it(lesson,
                                                                    template):
    offered = generate.tiers(template)
    assert offered, f"{template.key}: no draws at all"
    for tier in offered:
        assert tier in TIERS, f"{template.key}: {tier!r} is not a tier"
        assert list(generate.every_at(template, tier)), (
            f"{template.key}: {tier} is offered and empty"
        )


@pytest.mark.parametrize("lesson,template", ALL_TEMPLATES, ids=ALL_IDS)
def test_asking_for_a_tier_stays_inside_it(lesson, template):
    for tier in generate.tiers(template):
        keys = {question.key for question in generate.every_at(template, tier)}
        wanted = {f"{template.key}#{index}"
                  for index, item in enumerate(generate.draws(template))
                  if generate.tier_of(template, item) == tier}
        assert keys == wanted, f"{template.key}: {tier} drew outside itself"


def test_a_tier_nothing_has_falls_back_rather_than_refusing():
    """A drill that answered "no question at that difficulty" would be worse
    than one that asks a typical question, so the request is advisory."""
    _lesson, template = ALL_TEMPLATES[0]
    asked = generate.draw(template, 0, "nonexistent-tier")
    assert asked == generate.draw(template, 0)


def test_a_template_that_says_nothing_has_one_tier():
    plain = [template for _lesson, template in ALL_TEMPLATES
             if getattr(template, "level", None) is None
             and template.kind != "classify-template"]
    assert plain, "every template now has tiers, so this test means nothing"
    for template in plain:
        assert generate.tiers(template) == ("typical",)


# ---------------------------------------------------------------------------
# The screen
# ---------------------------------------------------------------------------

pytest.importorskip("PySide6", reason="the app extra is not installed")


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture()
def store(tmp_path, monkeypatch):
    """Point the progress file somewhere disposable."""
    from odesuite_app import progress

    monkeypatch.setattr(progress, "directory", lambda: tmp_path / "odesuite")
    return progress


@pytest.fixture()
def screen(qapp, store):
    from odesuite_app.screens.learn_lessons import LessonsScreen
    from odesuite_app.state import SessionState
    from odesuite_app.theme import PALETTES

    made = LessonsScreen(SessionState(), PALETTES["dark"])
    made.resize(1500, 950)
    qapp.processEvents()
    yield made
    made.deleteLater()


def _drill(screen, qapp, key: str):
    screen.select(key)
    screen._choose_segment("Drill")
    qapp.processEvents()
    return screen.current_lesson()


def _boxes(screen):
    from PySide6.QtWidgets import QLineEdit

    return screen._page.findChildren(QLineEdit)


def _page_text(screen) -> str:
    from PySide6.QtWidgets import QLabel

    return "\n".join(label.text() for label in screen._page.findChildren(QLabel)
                      if label.isVisibleTo(screen))


def _lessons_with(kind):
    return [lesson for lesson in LESSONS
            if any(template.kind == kind for template in lesson.templates)]


@pytest.mark.parametrize("kind", ["model-template", "expression-template",
                                  "classify-template", "fault-template"])
def test_every_new_kind_of_drill_opens(screen, qapp, kind):
    """Rendered, not merely constructed: a card that raised on the way to the
    screen would fail here rather than in front of somebody."""
    for lesson in _lessons_with(kind):
        _drill(screen, qapp, lesson.key)
        assert screen._segment == "Drill", lesson.key
        text = _page_text(screen)
        title = next(template.title for template in lesson.templates
                     if template.kind == kind)
        assert title in text, f"{lesson.key}: {title} did not render"


def test_a_model_drill_accepts_the_equation_rearranged(screen, qapp, store):
    """The property the whole question type rests on, through the screen."""
    lesson = _drill(screen, qapp, "linear")
    template = next(item for item in lesson.templates
                    if item.key == "mixing-tank")
    question = generate.draw(template, screen._drill_seed[template.key])

    left, right = question.equation.split("=")
    box = _boxes(screen)[0]
    for written in (question.equation, f"({left}) - ({right}) = 0"):
        box.setText(written)
        marked = screen._check_equivalent(
            lesson, question, box, screen._verdicts[template.key],
            bucket=store.drill_key(lesson.key), key=template.key,
        )
        assert marked, written
        assert "\u2713" in screen._verdicts[template.key].text(), written
    assert store.load()[store.drill_key(lesson.key)][template.key].correct


def test_a_model_drill_shows_what_differs(screen, qapp, store):
    lesson = _drill(screen, qapp, "linear")
    template = next(item for item in lesson.templates
                    if item.key == "mixing-tank")
    question = generate.draw(template, screen._drill_seed[template.key])

    box = _boxes(screen)[0]
    box.setText("y' = t + 1")
    screen._check_equivalent(lesson, question, box,
                        screen._verdicts[template.key],
                        bucket=store.drill_key(lesson.key), key=template.key)
    verdict = screen._verdicts[template.key].text()
    assert "\u2717" in verdict
    assert "what differs" in verdict


def test_an_expression_drill_takes_any_constant_multiple(screen, qapp, store):
    """Where the mathematics allows one. An integrating factor is determined
    only up to a constant, and the drill says so rather than being generous."""
    lesson = _drill(screen, qapp, "linear")
    template = next(item for item in lesson.templates
                    if item.key == "the-integrating-factor")
    tier = screen._tier_of(template, generate.tiers(template))
    question = generate.draw(template, screen._drill_seed[template.key], tier)

    box = _boxes(screen)[-1]
    for written in (question.answer, f"7*({question.answer})"):
        box.setText(written)
        screen._check_equivalent(
            lesson, question, box, screen._verdicts[template.key],
            bucket=store.drill_key(lesson.key), key=template.key,
        )
        assert "\u2713" in screen._verdicts[template.key].text(), written


def test_a_classify_drill_shows_the_equation_it_is_asking_about(screen, qapp):
    """It carries no LaTeX -- the equation comes out of the draw -- so if the
    monospace line were missing the question would be unanswerable."""
    lesson = _drill(screen, qapp, "substitutions")
    template = next(item for item in lesson.templates
                    if item.kind == "classify-template")
    tier = screen._tier_of(template, generate.tiers(template))
    question = generate.draw(template, screen._drill_seed[template.key], tier)
    assert question.shown in _page_text(screen)


def test_a_fault_drill_shows_both_the_equation_and_the_answer(screen, qapp):
    lesson = _drill(screen, qapp, "separable")
    template = next(item for item in lesson.templates
                    if item.kind == "fault-template")
    question = generate.draw(template, screen._drill_seed[template.key])
    for line in question.shown.splitlines():
        assert line in _page_text(screen)


def test_the_difficulty_control_appears_only_where_there_is_a_spread(screen,
                                                                     qapp):
    from PySide6.QtWidgets import QPushButton

    def offered():
        return {button.text() for button in screen._page.findChildren(QPushButton)
                if button.isCheckable() and button.isVisibleTo(screen)}

    _drill(screen, qapp, "substitutions")      # has tiers
    assert {"Easier", "Typical", "Harder"} <= offered()

    _drill(screen, qapp, "exact")              # one template, one tier
    assert not offered()


def test_choosing_a_tier_draws_from_that_tier(screen, qapp):
    lesson = _drill(screen, qapp, "substitutions")
    template = next(item for item in lesson.templates
                    if item.kind == "classify-template")

    for tier in generate.tiers(template):
        screen._choose_tier(template.key, tier)
        qapp.processEvents()
        seed = screen._drill_seed[template.key]
        asked = generate.draw(template, seed, tier)
        assert asked.shown in _page_text(screen)
        index = int(asked.key.split("#")[1])
        assert generate.tier_of(template, generate.draws(template)[index]) == tier


def test_the_version_count_follows_the_tier(screen, qapp):
    """"One of 14 versions" beside a control set to *harder* would be counting
    questions the drill is not going to ask."""
    lesson = _drill(screen, qapp, "substitutions")
    template = next(item for item in lesson.templates
                    if item.kind == "classify-template")
    screen._choose_tier(template.key, "harder")
    qapp.processEvents()
    within = generate.combinations(template, "harder")
    assert within < generate.combinations(template)
    assert f"one of {within} versions" in _page_text(screen)
