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
import random
import re
from collections.abc import Iterator

from .model import Choice, ChoiceTemplate, Solve, Template

__all__ = ["draws", "draw", "draw_choice", "combinations",
           "every", "tidy"]


#: Cosmetic repairs to a formatted equation, in order. Substituting numbers
#: into a template leaves `1*y`, `t**1` and `+ -3*t`, which is how you can tell
#: a question was generated -- and a drill whose questions look generated reads
#: as busywork rather than as practice. None of these changes what is parsed:
#: the tidied string is the one both shown *and* solved, and the whole draw set
#: is checked through the real narrator either way.
_TIDY = (
    (re.compile(r"\*t\*\*0(?![\d.])"), ""),       # 2*t**0*y -> 2*y
    (re.compile(r"t\*\*0\*"), ""),                # t**0*y   -> y
    (re.compile(r"\*\*1(?![\d.])"), ""),          # t**1  -> t
    (re.compile(r"(?<![\d.])1\*"), ""),           # 1*y   -> y,  -1*(…) -> -(…)
    (re.compile(r"\+\s*-\s*"), "- "),             # + -3*t -> - 3*t
)


def tidy(equation: str) -> str:
    """Drop the arithmetic scaffolding a substitution leaves behind."""
    for pattern, replacement in _TIDY:
        equation = pattern.sub(replacement, equation)
    return equation.strip()


def _spread(template: Template) -> Iterator[dict[str, object]]:
    """Every combination of the slots, before `reject` has its say."""
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
    kept = [slots for slots in _spread(template)
            if not (template.reject and template.reject(slots))]
    # Seeded from the key, so the order is stable across runs and machines but
    # is not the order the coefficients were written in.
    random.Random(template.key).shuffle(kept)
    return tuple(kept)


def combinations(template: Template) -> int:
    """How many distinct questions this template can produce."""
    return len(draws(template))


def _slots_for(template, seed: int) -> tuple[int, dict[str, object]]:
    """``(index, slots)`` for this seed. Shared by both draw functions."""
    pool = draws(template)
    if not pool:
        raise ValueError(f"template {template.key!r} has no accepted draws")
    index = seed % len(pool)
    return index, pool[index]


def draw(template, seed: int):
    """One question, as the ordinary type the template produces.

    A `Template` gives a `Solve` and a `ChoiceTemplate` gives a `Choice`, and
    the dispatch lives here so that every caller -- the drill card, the quiz,
    `every()` -- can ask for a question without knowing which kind it will get.

    The same seed always gives the same question, and the key names the draw
    rather than the seed, so the twentieth and the second version of an
    eighteen-draw template are recognisably the same question.
    """
    if isinstance(template, ChoiceTemplate):
        return draw_choice(template, seed)
    index, slots = _slots_for(template, seed)
    return Solve(
        key=f"{template.key}#{index}",
        prompt=template.prompt.format(**slots),
        equation=tidy(template.equation.format(**slots)),
        conditions=template.conditions.format(**slots),
        hints=tuple(hint.format(**slots) for hint in template.hints),
    )


def draw_choice(template: ChoiceTemplate, seed: int) -> Choice:
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
    index, slots = _slots_for(template, seed)
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
    )


def every(template) -> Iterator:
    """Every question this template can produce. For the exhaustive test."""
    for index in range(combinations(template)):
        yield draw(template, index)
