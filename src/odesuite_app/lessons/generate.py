"""Turning a `Template` into a practice question.

The whole design fits in one sentence: **a template is a factory for the `Solve`
type that already exists.** A generated question carries no marker of being
generated, so it is graded by substituting it into its own equation, hinted by
the same ladder, and worked by the same narrator — the drill adds no mathematics
of its own, and cannot disagree with the rest of the Hub about what is correct.

Draws are **enumerated, not sampled**, which buys three things worth having:

- `draw` is a pure function of the seed, so rebuilding the page cannot change
  the question out from under someone mid-answer;
- the test that every generated question is solvable can be *exhaustive* rather
  than a sample, which is the only version of that test worth trusting;
- the drill can honestly say "one of 18 versions", because it knows.

The order is shuffled — deterministically, from the template's own key — so that
consecutive questions do not march through the coefficients in numerical order,
which reads as a pattern to learn rather than a method to practise.
"""

from __future__ import annotations

import functools
import itertools
import math
import random
import re
from collections.abc import Iterator

from .model import (
    TIERS,
    Case,
    Choice,
    ChoiceTemplate,
    ClassifyTemplate,
    Expression,
    ExpressionTemplate,
    FaultTemplate,
    Model,
    ModelTemplate,
    Numeric,
    NumericTemplate,
    Solve,
    Template,
)

__all__ = ["draws", "draw", "draw_choice", "draw_numeric", "draw_model",
           "draw_expression", "draw_classify", "draw_fault", "case_shown",
           "combinations", "every", "every_at", "tidy", "tier_of",
           "tiers", "option_written"]


#: Cosmetic repairs to a formatted equation, in order. Substituting numbers
#: into a template leaves `1*y`, `t**1`, `+ -3*t` and `0*y'`, which is how you
#: can tell a question was generated -- and a drill whose questions look
#: generated reads as busywork rather than as practice. None of these changes
#: what is parsed: the tidied string is the one both shown *and* solved, and
#: the whole draw set is checked through the real narrator either way.
_TIDY = (
    (re.compile(r"\*t\*\*0(?![\d.])"), ""),       # 2*t**0*y -> 2*y
    (re.compile(r"t\*\*0\*"), ""),                # t**0*y   -> y
    (re.compile(r"\*\*1(?![\d.])"), ""),          # t**1  -> t
    # The lookbehind refuses a *word* character, not merely a digit: the
    # constants of integration are called C1 and C2, and a rule that only
    # checked for digits turned "C1*cos(3t)" into "Ccos(3t)" -- an answer
    # nothing could parse, inside a drill whose whole job was to show one.
    (re.compile(r"(?<![\w.])1\*"), ""),           # 1*y   -> y,  -1*(…) -> -(…)
    (re.compile(r"\+\s*-\s*"), "- "),             # + -3*t -> - 3*t
    # A zero coefficient has to take its whole term with it. The rules above
    # only rewrite what is in front of a term; this one deletes it, which is a
    # different claim about the equation and so is kept visibly separate.
    # Undamped and missing-root draws are the interesting ones, so the fix
    # cannot be to keep zero out of the slots.
    (re.compile(r"[+\-]\s*0\*[A-Za-z][\w']*"), ""),   # y'' + 0*y' -> y''
    (re.compile(r"(^|=)\s*0\*[A-Za-z][\w']*\s*\+\s*"), r"\1 "),  # = 0*x + y
    (re.compile(r"  +"), " "),                    # the gaps those leave
)


def tidy(equation: str) -> str:
    """Drop the arithmetic scaffolding a substitution leaves behind."""
    for pattern, replacement in _TIDY:
        equation = pattern.sub(replacement, equation)
    return equation.strip()


def _spread(template) -> Iterator:
    """Every draw a template can make, before `reject` has its say.

    A slot-based template spreads its slots; a `ClassifyTemplate` has no slots
    to spread, because what varies in it is the equation itself. Both come
    back through here so that shuffling, seeding, counting and the tiers below
    are written once rather than twice.
    """
    if isinstance(template, ClassifyTemplate):
        yield from template.cases
        return
    names = [name for name, _ in template.slots]
    pools = [values for _, values in template.slots]
    for combination in itertools.product(*pools):
        slots: dict[str, object] = {}
        for name, value in zip(names, combination):
            parts = [part.strip() for part in name.split(",")]
            if len(parts) == 1:
                slots[parts[0]] = value
            else:
                # A comma-named slot binds several at once from one tuple.
                slots.update(zip(parts, value))
        yield slots


@functools.cache
def draws(template: Template) -> tuple[dict[str, object], ...]:
    """Every accepted draw, in a fixed but unobvious order.

    Cached: the enumeration is the same every time by construction, and the
    drill asks for it on every keystroke-free redraw.
    """
    reject = getattr(template, "reject", None)
    kept = [slots for slots in _spread(template)
            if not (reject and reject(slots))]
    # Seeded from the key, so the order is stable across runs and machines but
    # is not the order the coefficients were written in.
    random.Random(template.key).shuffle(kept)
    return tuple(kept)


def combinations(template: Template, tier: str = "") -> int:
    """How many distinct questions this template can produce.

    Within one tier when asked for one, because that is the number the drill
    card prints: "one of 27 versions" beside a control set to *harder* would
    be counting questions it is not going to ask.
    """
    if not tier:
        return len(draws(template))
    within = sum(1 for item in draws(template)
                 if tier_of(template, item) == tier)
    return within or len(draws(template))


def tier_of(template, item) -> str:
    """Which of `TIERS` one draw belongs to.

    A template that says nothing has every draw in `typical`, which is what
    every drill in this application was before tiers existed -- so adding the
    idea changed no existing question.
    """
    if isinstance(item, Case):
        return item.tier
    level = getattr(template, "level", None)
    return level(item) if level is not None else "typical"


def tiers(template) -> tuple[str, ...]:
    """The tiers this template actually offers, in order.

    One tier means the drill has no spread worth offering a choice about, and
    the card shows no control. That is the common case and it should be: a
    tier that exists because the author felt they ought to provide three is
    worse than none, since a student who picks *harder* and gets the same
    question learns to distrust the label.
    """
    present = {tier_of(template, item) for item in draws(template)}
    return tuple(tier for tier in TIERS if tier in present)


def _pick(template, seed: int, tier: str = ""):
    """``(index, draw)`` for this seed, within `tier` when one is asked for.

    The index is the draw's place in the *whole* pool, not in the filtered
    one, so a question keeps the same key however it was reached -- the
    seventh draw is `#7` whether it arrived as the seventh question, as the
    second harder one, or from a quiz.
    """
    pool = draws(template)
    if not pool:
        raise ValueError(f"template {template.key!r} has no accepted draws")
    if tier:
        within = [(index, item) for index, item in enumerate(pool)
                  if tier_of(template, item) == tier]
        if within:
            return within[seed % len(within)]
    index = seed % len(pool)
    return index, pool[index]


def draw(template, seed: int, tier: str = ""):
    """One question, as the ordinary type the template produces.

    A `Template` gives a `Solve`, a `ChoiceTemplate` a `Choice` and a
    `NumericTemplate` a `Numeric`, and the dispatch lives here so that every
    caller -- the drill card, the quiz, `every()` -- can ask for a question
    without knowing which kind it will get. The four later template types
    dispatch here too, and two of them also produce a `Choice`: a *which
    method* question and a *what went wrong* question are multiple choice by
    the time they reach a screen, whatever they were built from.

    The same seed always gives the same question, and the key names the draw
    rather than the seed, so the twentieth and the second version of an
    eighteen-draw template are recognisably the same question.

    `tier` narrows the pool to draws of one difficulty. It is a request rather
    than a demand: a template with nothing at that tier draws from the whole
    pool instead, because a drill that refuses to ask anything is worse than
    one that asks a typical question.
    """
    if isinstance(template, ChoiceTemplate):
        return draw_choice(template, seed, tier)
    if isinstance(template, NumericTemplate):
        return draw_numeric(template, seed, tier)
    if isinstance(template, ModelTemplate):
        return draw_model(template, seed, tier)
    if isinstance(template, ExpressionTemplate):
        return draw_expression(template, seed, tier)
    if isinstance(template, ClassifyTemplate):
        return draw_classify(template, seed, tier)
    if isinstance(template, FaultTemplate):
        return draw_fault(template, seed, tier)
    index, slots = _pick(template, seed, tier)
    return Solve(
        key=f"{template.key}#{index}",
        prompt=template.prompt.format(**slots),
        equation=tidy(template.equation.format(**slots)),
        conditions=template.conditions.format(**slots),
        hints=tuple(hint.format(**slots) for hint in template.hints),
    )


def draw_choice(template: ChoiceTemplate, seed: int,
                tier: str = "") -> Choice:
    """One multiple-choice question, as an ordinary `Choice`.

    **The options are shuffled, and that is the point.** Formatting them and
    leaving the answer where the author wrote it would put the right option at
    the same index in every version, so the drill would teach the position
    rather than the mathematics -- the exact failure a generated question
    exists to avoid. The shuffle is seeded from the template's key and the
    draw index, so it is stable across runs and machines while differing from
    one version to the next.

    Each *becaus* moves with its own option. A reason attached to the wrong
    option would be worse than no reason at all, since it is shown for
    whichever option was picked.
    """
    index, slots = _pick(template, seed, tier)
    filled = [option.format(**slots) for option in template.options]
    reasons = [because.format(**slots) for because in template.becauses]

    order = list(range(len(filled)))
    random.Random(f"{template.key}#{index}").shuffle(order)
    return Choice(
        key=f"{template.key}#{index}",
        prompt=template.prompt.format(**slots),
        options=tuple(filled[position] for position in order),
        answer=order.index(template.answer),
        becauses=tuple(reasons[position] for position in order),
        latex=template.latex.format(**slots) if template.latex else "",
        # The shuffle, kept rather than thrown away. It is what lets a pick be
        # recorded as "the option the author wrote third" instead of "the
        # third radio button", and only the first of those means anything from
        # one draw to the next. See `Choice.origins`.
        origins=tuple(order),
    )


def draw_numeric(template: NumericTemplate, seed: int,
                 tier: str = "") -> Numeric:
    """One question whose answer is a number, with the number worked out.

    The template's `answer` is an expression over the slots, so filling the
    slots and evaluating it is the whole of the work. It goes through sympy
    rather than `eval`, for the reason everything in this application does --
    and `float` at the end rather than leaving it symbolic, because the grader
    compares magnitudes and a comparison is not the place to discover that an
    answer never simplified.

    A draw whose answer will not evaluate to a real number is a broken
    template, and it raises here rather than reaching a card that would have to
    apologise for it. `tests/test_templates.py` walks every draw of every
    template, so that cannot reach anyone.
    """
    import sympy as sp

    index, slots = _pick(template, seed, tier)
    value = sp.sympify(template.answer.format(**slots))
    number = complex(value.evalf())
    if abs(number.imag) > 1e-12:
        raise ValueError(
            f"template {template.key!r} draw {index} has a complex answer: "
            f"{value}"
        )
    def apart(first: float, second: float) -> bool:
        return abs(first - second) > 10 * template.tolerance * max(
            1.0, abs(first), abs(second))

    mistakes = []
    for expression, cause in template.mistakes:
        try:
            wrong = complex(sp.sympify(expression.format(**slots)).evalf())
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        if abs(wrong.imag) > 1e-12 or not math.isfinite(wrong.real):
            continue                      # a backward step with h·a = 1
        # Dropped where it coincides with the answer: with mu = 1, "gave r²
        # for r" is the right number, and saying so would mark it a mistake.
        if not apart(wrong.real, number.real):
            continue
        mistakes.append((wrong.real, cause.format(**slots)))
    # And where two causes give the same number, naming either would be a
    # guess: a d + b c and a + d are both -1 for (1, -2; 1, -2).
    mistakes = [(value, cause) for value, cause in mistakes
                if all(apart(value, other) for other, _ in mistakes
                       if other is not value)]
    return Numeric(
        key=f"{template.key}#{index}",
        # Tidied, because a numeric prompt states its equation inline and a
        # substituted coefficient leaves "+ -1*t" behind. `tidy` is written
        # for exactly that and touches nothing else in a sentence -- its
        # patterns all need an adjacent `*` or `**`.
        prompt=tidy(template.prompt.format(**slots)),
        answer=number.real,
        tolerance=template.tolerance,
        units=template.units,
        because=template.because.format(**slots),
        latex=template.latex.format(**slots) if template.latex else "",
        hints=tuple(hint.format(**slots) for hint in template.hints),
        mistakes=tuple(mistakes),
    )


def draw_model(template: ModelTemplate, seed: int, tier: str = "") -> Model:
    """One question whose answer is an equation, as an ordinary `Model`."""
    index, slots = _pick(template, seed, tier)
    return Model(
        key=f"{template.key}#{index}",
        # Tidied, because a modelling prompt states its quantities inline and
        # a substituted coefficient leaves "+ -1*t" behind.
        prompt=tidy(template.prompt.format(**slots)),
        equation=tidy(template.equation.format(**slots)),
        because=template.because.format(**slots),
        latex=template.latex.format(**slots) if template.latex else "",
        hints=tuple(hint.format(**slots) for hint in template.hints),
    )


def draw_expression(template: ExpressionTemplate, seed: int,
                    tier: str = "") -> Expression:
    """One question asking for a single move of a method.

    The answer stays a string. `draw_numeric` evaluates its expression because
    what it produces is a number; here the expression *is* the answer, and
    `symbolic.check_expression` compares it with what was typed.
    """
    index, slots = _pick(template, seed, tier)
    return Expression(
        key=f"{template.key}#{index}",
        prompt=tidy(template.prompt.format(**slots)),
        answer=tidy(template.answer.format(**slots)),
        up_to_constant=template.up_to_constant,
        because=template.because.format(**slots),
        latex=template.latex.format(**slots) if template.latex else "",
        hints=tuple(hint.format(**slots) for hint in template.hints),
    )


def draw_classify(template: ClassifyTemplate, seed: int,
                  tier: str = "") -> Choice:
    """One *which method* question, as an ordinary `Choice`.

    The options are the method names, in the order the template lists them,
    and then shuffled per draw exactly as `draw_choice` shuffles its own --
    for the same reason, and it matters more here: a menu of methods that
    never moved would be answered by position within a dozen draws.

    Each option carries a reason, and the two kinds of reason are different on
    purpose. The right one gets the case's own `why` -- what in *this*
    equation decides it. The others get the label's standing criterion from
    the vocabulary, which is what somebody who picked it needs to hold the
    equation up against.
    """
    from .vocabulary import VOCABULARIES

    table = VOCABULARIES[template.table]
    index, case = _pick(template, seed, tier)
    labels = [table[key].title for key in template.options]
    reasons = [case.why if key == case.technique else table[key].requires
               for key in template.options]
    answer = template.options.index(case.technique)

    order = list(range(len(labels)))
    random.Random(f"{template.key}#{index}").shuffle(order)
    return Choice(
        key=f"{template.key}#{index}",
        prompt=template.prompt.format(equation=case.equation, at=case.at),
        options=tuple(labels[position] for position in order),
        answer=order.index(answer),
        becauses=tuple(reasons[position] for position in order),
        latex=case.latex,
        shown=case_shown(case),
        origins=tuple(order),
    )


def case_shown(case) -> str:
    """The equation as a classify drill shows it, with its point if it has one."""
    return f"{case.equation}     at (x, y) = {case.at}" if case.at else case.equation


def draw_fault(template: FaultTemplate, seed: int, tier: str = "") -> Choice:
    """One *what went wrong* question, as an ordinary `Choice`.

    The equation and the answer somebody arrived at go into `shown` rather
    than into the prompt: they are mathematics, and the card sets them in the
    monospace the editor uses instead of burying them in a sentence.
    """
    from .vocabulary import FAULTS

    index, slots = _pick(template, seed, tier)
    keys = (template.fault, *template.others)
    labels = [FAULTS[key].label for key in keys]
    reasons = [FAULTS[key].tell for key in keys]

    order = list(range(len(labels)))
    random.Random(f"{template.key}#{index}").shuffle(order)

    equation = tidy(template.equation.format(**slots))
    conditions = template.conditions.format(**slots)
    wrong = tidy(template.wrong.format(**slots))
    return Choice(
        key=f"{template.key}#{index}",
        prompt=template.prompt.format(**slots),
        options=tuple(labels[position] for position in order),
        answer=order.index(0),
        becauses=tuple(reasons[position] for position in order),
        shown=(f"{equation}" + (f",   {conditions}" if conditions else "")
               + f"\nthe answer handed in:   y = {wrong}"),
        origins=tuple(order),
    )


def every(template) -> Iterator:
    """Every question this template can produce. For the exhaustive test."""
    for index in range(combinations(template)):
        yield draw(template, index)


def every_at(template, tier: str) -> Iterator:
    """Every question this template can produce at one tier."""
    wanted = [index for index, item in enumerate(draws(template))
              if tier_of(template, item) == tier]
    for position in range(len(wanted)):
        yield draw(template, position, tier)


def option_written(question, index: int) -> tuple[str, str]:
    """``(option, reason)`` for the author's option `index`, as it is shown.

    The inverse of the shuffle, and the piece `progress.misconceptions` cannot
    supply for itself: it counts stable option indices, because an index is all
    a progress file can honestly hold, and this turns one back into the words
    somebody actually clicked on.

    A template is drawn once, at its first draw, purely for its formatting.
    The slots differ from version to version and the sentence does not, which
    is the whole reason a repeated pick is worth naming.
    """
    if getattr(question, "kind", "") != "choice":
        try:
            question = draw(question, 0)
        except Exception:
            return "", ""
        if getattr(question, "kind", "") != "choice":
            return "", ""
    position = question.origins.index(index) if index in question.origins \
        else index
    if not 0 <= position < len(question.options):
        return "", ""
    reason = (question.becauses[position]
              if position < len(question.becauses) else "")
    return question.options[position], reason
