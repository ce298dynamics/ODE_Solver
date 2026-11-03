"""Fresh drill questions, each one solved before it is asked.

A template's enumerated draws are checked exhaustively by the test suite,
which is what lets a drill say "one of 18 versions" and mean it. Past the
eighteenth there is nothing left to check in advance, so a sampled draw is
checked here, at the moment it is made, by the same means the tests use: the
narrator must work it by the technique the drill claims, every step must
verify, and the grader must accept the narrator's own answer. A draw that
fails any of it is thrown away and the next one tried; one that cannot be
found inside the budget is None, and the drill goes back to its pool.

No Qt: the drill runs `fresh_draw` on a worker thread.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from .lessons import generate
from .lessons.model import Solve, Template

__all__ = ["ENABLED", "work_out", "answer_text", "verify_solve", "fresh_draw",
           "readable"]

#: Whether the drills draw fresh numbers at all. Off for the test suite,
#: whose screen tests walk round a pool many times over and compare what is
#: shown against `generate.draw`; the tests of fresh draws turn it back on.
ENABLED = True


def work_out(equation: str, conditions: str, narrator: str,
             timeout: float | None = None):
    """The worked solution, through the same timed subprocess as the Hub."""
    from .laplace import EXTRA_FUNCTIONS
    from .symbolic import (
        parse_equation,
        solve_by_laplace,
        solve_symbolically,
        spec_for,
    )

    parsed = parse_equation(spec_for(equation, conditions),
                            extra_functions=EXTRA_FUNCTIONS)
    if narrator == "laplace":
        return solve_by_laplace(parsed, timeout=timeout).derivation
    if narrator == "series":
        from .series import derive as series_derive

        return series_derive(parsed.equation, parsed.function, ics=parsed.ics)
    return solve_symbolically(parsed, timeout=timeout, steps=True).derivation


def readable(derivation) -> bool:
    """Whether the answer is one a student could be asked to write.

    The pool is curated for this by hand; sampled numbers are not. A right
    answer three lines long is still a bad drill question.
    """
    import sympy as sp

    result = derivation.result
    # A system's column is several answers, each typed on its own line.
    parts = list(result) if isinstance(result, sp.MatrixBase) else [result]
    return all(len(sp.sstr(part)) <= 120 for part in parts)


def answer_text(parsed, result) -> str:
    """The narrator's result as a student would type it into the answer box.

    A system's result is a column, one entry per unknown, and the box wants
    one ``x = ...`` line for each: the whole column on one line is refused.
    """
    import sympy as sp

    if getattr(parsed, "is_system", False):
        return "\n".join(f"{function.__name__} = {sp.sstr(component)}"
                         for function, component in zip(parsed.functions,
                                                        result))
    return sp.sstr(result)


def verify_solve(template: Template, question: Solve,
                 timeout: float | None = None,
                 nice: Callable | None = readable):
    """``(derivation, "")`` when `question` is one the app can answer,
    else ``(None, why)``.

    The same conditions `tests/test_templates.py` holds every enumerated draw
    to, so a fresh question is no less checked than a built-in one.
    """
    from .laplace import EXTRA_FUNCTIONS
    from .symbolic import check_answer, parse_equation, spec_for

    try:
        derivation = work_out(question.equation, question.conditions,
                              template.narrator, timeout)
    except Exception as exc:                      # a draw, not a crash
        return None, f"could not be worked: {exc}"
    if derivation is None or not derivation.complete:
        return None, "no complete derivation"
    if derivation.result is None or derivation.verified is False:
        return None, "the derivation does not check out"
    if any(step.verified is False for step in derivation.steps):
        return None, "a step does not verify"
    if template.technique and derivation.technique != template.technique:
        return None, (f"worked as {derivation.technique}, not "
                      f"{template.technique}")
    parsed = parse_equation(spec_for(question.equation, question.conditions),
                            extra_functions=EXTRA_FUNCTIONS)
    verdict = check_answer(parsed, answer_text(parsed, derivation.result),
                           general=not question.conditions)
    if verdict.correct is not True or not verdict.ok:
        return None, f"the grader does not accept it: {verdict.message}"
    if nice is not None and not nice(derivation):
        return None, "the answer is not one to ask a student for"
    return derivation, ""


def fresh_draw(template: Template, seed: int, tier: str = "",
               budget: float = 8.0, timeout: float | None = None,
               attempts: int = 40):
    """``(Solve, Derivation)`` with new numbers that the solver has checked,
    or None when the template has no sampler or nothing passed in `budget`
    seconds.

    Deterministic: a seed tries the same attempts in the same order, so the
    question it settles on is the same wherever it is drawn, unless the
    clock ran out first.
    """
    if template.sampler is None:
        return None
    deadline = time.monotonic() + budget
    for attempt in range(attempts):
        if time.monotonic() >= deadline:
            return None
        question = generate.sample(template, seed, tier, attempt)
        if question is None:
            continue
        left = max(deadline - time.monotonic(), 0.5)
        derivation, _ = verify_solve(
            template, question,
            timeout=left if timeout is None else min(timeout, left))
        if derivation is not None:
            return question, derivation
    return None
