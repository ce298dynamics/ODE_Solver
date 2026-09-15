"""The course itself: what each technique is, and questions to try.

The rest of the Learning Hub is *tools* -- bring an equation and they work on
it. This is the part that assumes you do not yet know which equation to bring.
Units, lessons within them, and for each lesson notes, worked examples and
practice.

Two decisions about the practice questions are worth stating, because they are
what keep this from being a quiz with a stored answer key.

**Solve-it questions are graded by mathematics, not by comparison.** The answer
is substituted into the equation and simplified, through the same
`symbolic.check_answer` the Solve Step by Step screen uses. Any correct form
passes -- ``3e^{-2t}``, ``3/e^{2t}``, ``3*exp(-t)*exp(-t)`` are one answer -- and
nothing is marked wrong merely for being spelled differently from what the
author had in mind. Where simplification cannot decide, the verdict is "cannot
tell", never "wrong".

**Multiple-choice questions exist for what that cannot reach.** *Which technique
solves this* is the question a course actually tests and a substitution check
can say nothing about, so those have a stored answer -- and each carries a
reason for *every* option, because the reason a wrong option was tempting is
usually the thing that was actually misunderstood.

**Four later kinds ask the questions those two cannot.** Everything above hands
the student an equation and asks what to do with it, which is not what an
examination does. So a lesson may also drill *which method would you reach for
first* over a pool of equations, *write the equation* for a situation or for a
family of curves, *write one move of the method* -- the integrating factor, the
characteristic polynomial, the Wronskian -- and *what went wrong* with an
answer somebody else arrived at. The first and last produce ordinary `Choice`
questions; the middle two are graded by `symbolic.check_model` and
`check_expression`, which ask whether two pieces of mathematics are the same
rather than whether two strings are.

None of them is trusted. Each has a routine in the application that decides its
answers -- `classify_ode` for a method, `analysis.classify` for a phase
portrait, `check_answer` for whether a wrong answer is really wrong -- and
`tests/test_drill_kinds.py` puts every draw of every one of them through it.

The worked examples of each lesson are equations the narrator can already
handle, so the working shown is generated and checked rather than transcribed.
An example that drifted out of step with the tool that explains it would be
worse than none.

Content only -- no PySide6, no Qt -- so the curriculum can be read, counted and
tested without an interface. One module per unit, because thirty-five lessons
is not something one file should carry.
"""

from __future__ import annotations

from . import (
    unit1_first_order,
    unit2_models_numerics,
    unit3_second_order,
    unit4_vibrations,
    unit5_laplace,
    unit6_systems,
    unit7_series,
)
from .model import (
    NOTE_KINDS,
    TIERS,
    Case,
    Choice,
    ClassifyTemplate,
    Example,
    Expression,
    ExpressionTemplate,
    FaultTemplate,
    Lesson,
    Model,
    ModelTemplate,
    Note,
    Numeric,
    Passage,
    Solve,
    Unit,
    grade_choice,
)

__all__ = [
    "NOTE_KINDS",
    "TIERS",
    "Passage",
    "Note",
    "Example",
    "Choice",
    "Solve",
    "Numeric",
    "Model",
    "Expression",
    "Case",
    "ModelTemplate",
    "ExpressionTemplate",
    "ClassifyTemplate",
    "FaultTemplate",
    "Lesson",
    "Unit",
    "UNITS",
    "LESSONS",
    "by_key",
    "unit_by_key",
    "unit_of",
    "questions_of",
    "formulas",
    "grade_choice",
]


#: The course, in the order Edwards, Penney and Calvis present it.
#:
#: A unit appears here only once it has lessons. There is no placeholder for a
#: unit still to be written: this application removed its last stand-in
#: deliberately, and a course map advertising empty units would put them back.
UNITS: tuple[Unit, ...] = (
    Unit(
        key="first-order",
        title="First-order equations",
        summary="The two techniques a course meets first, and the two it falls "
                "back on for the rest of the term.",
        reference="Edwards ch. 1",
        lessons=unit1_first_order.LESSONS,
    ),
    Unit(
        key="models",
        title="Models and numerical methods",
        summary="Where the equations come from, and what to do when none of "
                "the closed-form techniques applies.",
        reference="Edwards ch. 2",
        lessons=unit2_models_numerics.LESSONS,
    ),
    Unit(
        key="second-order",
        title="Second-order linear equations",
        summary="Reading a solution off the characteristic roots, guessing the "
                "response to forcing, and the one variable-coefficient family "
                "that still comes out in closed form.",
        reference="Edwards ch. 3",
        lessons=unit3_second_order.LESSONS,
    ),
    Unit(
        key="vibrations",
        title="Vibrations and forcing",
        summary="Where the second-order machinery stops being an exercise and "
                "becomes a mass on a spring, a shock absorber and a tuning "
                "circuit.",
        reference="Edwards 3.4, 3.6–3.7",
        lessons=unit4_vibrations.LESSONS,
    ),
    Unit(
        key="laplace",
        title="Laplace transforms",
        summary="The one technique that turns the equation into algebra — and "
                "the only one that copes with forcing switched on partway "
                "through.",
        reference="Edwards ch. 7",
        lessons=unit5_laplace.LESSONS,
    ),
    Unit(
        key="systems",
        title="Linear systems",
        summary="Two equations that will not come apart, and the matrix that "
                "makes them one problem again.",
        reference="Edwards ch. 4-5",
        lessons=unit6_systems.LESSONS,
    ),
    Unit(
        key="series",
        title="Series solutions",
        summary="What to do when there is no closed form at all — which is\n"
                "the ordinary case rather than the exceptional one.",
        reference="Edwards ch. 8",
        lessons=unit7_series.LESSONS,
    ),
)

#: Every lesson, flattened, in course order.
LESSONS: tuple[Lesson, ...] = tuple(
    lesson for unit in UNITS for lesson in unit.lessons
)


def by_key(key: str) -> Lesson | None:
    for lesson in LESSONS:
        if lesson.key == key:
            return lesson
    return None


def unit_by_key(key: str) -> Unit | None:
    for unit in UNITS:
        if unit.key == key:
            return unit
    return None


def unit_of(lesson: Lesson | str) -> Unit | None:
    """The unit a lesson belongs to, by object or by key."""
    key = lesson if isinstance(lesson, str) else lesson.key
    for unit in UNITS:
        if any(item.key == key for item in unit.lessons):
            return unit
    return None


def questions_of(lesson: Lesson) -> tuple[Choice | Solve, ...]:
    return lesson.questions


def formulas(units: tuple[Unit, ...] | None = None
             ) -> tuple[tuple[Unit, Lesson, Note], ...]:
    """Every `Note` of kind "formula", in course order, with its provenance.

    The crib sheet a first course allows into the examination is a page of
    formulas, and this course already contains one: sixty-five notes were
    written as `kind="formula"` because a formula is a different kind of thing
    from an idea or a pitfall and is boxed differently on the lesson page. That
    classification was made for the reader's sake one card at a time, and this
    collects on it -- the sheet is *found* in the course rather than authored
    beside it, so it cannot fall out of step with what the lessons teach.

    A note is returned with its lesson and unit rather than alone, because a
    formula with no indication of what it belongs to is exactly the sheet
    nobody can use under time.
    """
    found = []
    for unit in (UNITS if units is None else units):
        for lesson in unit.lessons:
            for note in lesson.notes:
                if note.kind == "formula":
                    found.append((unit, lesson, note))
    return tuple(found)
