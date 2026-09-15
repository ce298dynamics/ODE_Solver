"""Papers that span units, sized and timed like the real thing.

The Unit Quiz mixes one unit up, which rehearses the hardest thing a section
of practice cannot: choosing the method. An examination asks that question
across a *term*, and the difference is not cosmetic. Told a paper is about
Chapter 3 you have already been handed half the answer to every question on
it; told only that it is Exam 2 you have not. This module is the second case.

Three decisions are worth stating.

**A paper is a selection, not a new kind of question.** `build` returns the
very same ``(lesson, template, question)`` triples the Unit Quiz builds, drawn
by the same `lessons.generate.draw`, so an exam question is a drill question
and is graded by the same substitution, the same `grade_choice` and the same
tolerance. The exam contributes no mathematics and therefore cannot disagree
with the rest of the Hub about what is correct — which is the argument that
made the quiz cheap to add, used a second time.

**The units are interleaved, not concatenated.** A paper built by taking six
questions from Chapter 1 and then six from Chapter 3 would still tell you
which chapter each question came from, just more slowly. `lessons_for` takes
one lesson from each unit in turn, so consecutive questions are from different
units by construction.

**Which lessons appear depends on the seed.** A paper is shorter than the run
of lessons it draws from — eight questions against twenty-odd lessons — so a
fixed order would examine the same eight every time and leave the rest
unexaminable. The per-unit order is shuffled from the seed before the
interleave, so the unit balance is fixed and the choice within it is not.

The boundaries below are the ones this course keeps, and they are one tuple to
edit for a section that splits the term differently. They follow Edwards,
Penney and Calvis in order: the first paper is the first-order material and
the models built on it, the second is everything about higher-order linear
equations up to and including systems, and the final is the whole course —
which is where the transform and the series methods land, being the last
things taught.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from . import lessons as content
from .lessons import generate

__all__ = ["Paper", "PAPERS", "by_key", "units_of", "lessons_for", "build",
           "draw_from"]


@dataclass(frozen=True)
class Paper:
    """One examination: what it covers, how long it is, and how long you get."""

    key: str
    title: str
    #: The unit keys it examines, in course order.
    units: tuple[str, ...]
    #: How many questions. Sized like the paper it stands in for rather than
    #: like a practice set: a check-up you can stop at any point is a different
    #: exercise from one you have to pace.
    questions: int
    #: The time allowed, in minutes.
    minutes: int
    #: What it covers, in a sentence.
    summary: str
    #: The chapters, as the textbook numbers them.
    reference: str = ""

    @property
    def seconds(self) -> int:
        return self.minutes * 60

    @property
    def pace(self) -> float:
        """Minutes a question, which is the number worth knowing beforehand."""
        return self.minutes / self.questions if self.questions else 0.0


#: The three papers a term contains. Fifty minutes is the ordinary length of a
#: midterm and two hours of a final; the question counts are what fits at a
#: pace of roughly six minutes a question, which is what these questions take
#: by hand.
PAPERS: tuple[Paper, ...] = (
    Paper(
        key="exam-1",
        title="Exam 1",
        units=("first-order", "models"),
        questions=8,
        minutes=50,
        summary="First-order equations and the models built out of them — "
                "separation, integrating factors, exact equations and "
                "substitutions, then the applications and the numerical "
                "methods for when none of them applies.",
        reference="Edwards ch. 1–2",
    ),
    Paper(
        key="exam-2",
        title="Exam 2",
        units=("second-order", "vibrations", "systems"),
        questions=8,
        minutes=50,
        summary="Higher-order linear equations: characteristic roots, "
                "undetermined coefficients and variation of parameters, the "
                "vibrating systems they describe, and the same machinery "
                "written as a matrix.",
        reference="Edwards ch. 3–5",
    ),
    Paper(
        key="final",
        title="Final exam",
        units=tuple(unit.key for unit in content.UNITS),
        questions=16,
        minutes=120,
        summary="The whole course, in the proportions it was taught — which "
                "is the only paper on which the Laplace transform and the "
                "series methods have to compete with everything before them.",
        reference="Edwards ch. 1–8",
    ),
)


def by_key(key: str) -> Paper | None:
    for paper in PAPERS:
        if paper.key == key:
            return paper
    return None


def units_of(paper: Paper) -> tuple:
    """The `Unit` objects a paper examines, in course order.

    A unit named here but carrying no drills is dropped rather than left in as
    an empty heading. Every unit has drills now, so this is a guard against a
    future edit rather than a live case — but a paper that silently produced
    fewer questions than it promised would be a bad way to find that out.
    """
    found = []
    for key in paper.units:
        unit = content.unit_by_key(key)
        if unit is not None and unit.quizzable:
            found.append(unit)
    return tuple(found)


def lessons_for(paper: Paper, seed: int = 0) -> tuple:
    """The lessons a paper may draw on, ordered so any prefix is in proportion.

    A paper is far shorter than the material it examines -- sixteen questions
    against thirty-odd lessons -- so what matters is not the whole order but
    the *first N* of it, and two properties of that prefix:

    **Every unit is represented in proportion to its size.** Each lesson is
    given a position ``(index + ½) / lessons in its unit`` and the whole list
    is sorted by it, which is the interleave a progress bar uses to space
    ticks: a unit of six lessons recurs twice as often as one of three, so the
    first sixteen entries carry both in the ratio they were taught. A plain
    round-robin would instead give a six-lesson unit and a three-lesson one the
    same weight, which is not what a cumulative paper is.

    **Which lessons those are depends on the seed.** Within a unit the order is
    shuffled first, so a fixed prefix does not examine the same handful every
    time and leave the rest of the course unexaminable.
    """
    placed = []
    for unit in units_of(paper):
        lessons = [lesson for lesson in unit.quizzable if lesson.templates]
        if not lessons:
            continue
        # Seeded from the unit key as well as the paper's seed, so two units
        # do not shuffle in lockstep and the same seed is reproducible.
        random.Random(f"{paper.key}:{unit.key}:{seed}").shuffle(lessons)
        for index, lesson in enumerate(lessons):
            placed.append(((index + 0.5) / len(lessons), unit.key, lesson))
    placed.sort(key=lambda item: (item[0], item[1]))
    return tuple(lesson for _, _, lesson in placed)


def draw_from(lessons, length: int, seed: int) -> list:
    """`length` questions round-robin across `lessons`.

    Round-robin across the **lessons**, not across their templates. That
    distinction is what a mixed set is for: a lesson with two drills would
    otherwise take two of the first few slots and crowd another lesson out of
    a short paper. Within a lesson the templates take turns as the rounds come
    round.

    Shared by the Unit Quiz and by `build`, so the two cannot drift apart
    about what a mixed set means.
    """
    lessons = [lesson for lesson in lessons if lesson.templates]
    if not lessons:
        return []
    out = []
    for index in range(length):
        lesson = lessons[index % len(lessons)]
        round_number = index // len(lessons)
        template = lesson.templates[round_number % len(lesson.templates)]
        out.append((lesson, template, generate.draw(template, seed + index)))
    return out


def build(paper: Paper, seed: int, length: int = 0) -> list:
    """A whole paper, as ``(lesson, template, question)`` triples.

    The order is shuffled after the draw, and that is the last thing standing
    between this and a set of questions you can read the syllabus off. Selected
    in proportion and left in that order, the units would march -- first-order,
    models, first-order, models -- and by question three the position would be
    telling you the chapter, which is most of what the question was asking.

    `length` overrides the paper's own size, for the one caller that wants a
    shorter version of the same spread -- a printable worksheet, where the
    point is the mix rather than the sitting.
    """
    drawn = draw_from(lessons_for(paper, seed), length or paper.questions, seed)
    random.Random(f"{paper.key}:order:{seed}").shuffle(drawn)
    return drawn
