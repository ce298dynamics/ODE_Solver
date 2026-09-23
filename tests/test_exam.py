"""Cumulative papers: Exam 1, Exam 2 and the final.

A unit check-up rehearses choosing the method within a chapter. A paper asks
the same question across a term, and the difference is the whole point of this
module -- so the tests here are almost all about what a paper must *not* let
you infer. If the units march in a cycle, or the same eight lessons appear
every time, or the position of a question tells you its chapter, then the paper
has answered the hardest part of itself before it is sat.

The other claim worth holding it to is that it adds no mathematics: an exam
question is a drill question, drawn by `generate.draw` and graded by whatever
already grades that kind.
"""

from __future__ import annotations

from collections import Counter

import pytest

pytest.importorskip("sympy")

from odesuite_app import exam  # noqa: E402
from odesuite_app import lessons as content  # noqa: E402

# ---------------------------------------------------------------------------
# The papers themselves
# ---------------------------------------------------------------------------


def test_there_are_three_papers_and_they_are_a_term():
    assert [paper.key for paper in exam.PAPERS] == ["exam-1", "exam-2", "final"]


@pytest.mark.parametrize("paper", exam.PAPERS, ids=lambda p: p.key)
def test_a_paper_is_well_formed(paper):
    assert paper.title and paper.summary and paper.reference
    assert paper.questions > 0
    assert paper.minutes > 0
    assert 3 <= paper.pace <= 12, (
        f"{paper.key} allows {paper.pace:.1f} minutes a question, which is not "
        "a pace anybody sits an exam at"
    )


@pytest.mark.parametrize("paper", exam.PAPERS, ids=lambda p: p.key)
def test_every_unit_a_paper_names_exists_and_can_be_drawn_from(paper):
    """A named unit with no drills would silently shorten the paper."""
    assert paper.units
    for key in paper.units:
        unit = content.unit_by_key(key)
        assert unit is not None, f"{paper.key} names an absent unit {key!r}"
        assert unit.quizzable, f"{key} has nothing to draw from"
    assert len(exam.units_of(paper)) == len(paper.units)


def test_the_final_covers_the_whole_course():
    final = exam.by_key("final")
    assert set(final.units) == {unit.key for unit in content.UNITS}


def test_the_midterms_between_them_cover_everything_up_to_the_transform():
    """Not an arbitrary check: a unit on no paper at all can only be examined
    on the final, which is how a syllabus quietly loses a chapter."""
    covered = set(exam.by_key("exam-1").units) | set(exam.by_key("exam-2").units)
    assert covered, "the midterms cover nothing"
    for key in covered:
        assert content.unit_by_key(key) is not None


def test_by_key_finds_each_and_refuses_the_rest():
    for paper in exam.PAPERS:
        assert exam.by_key(paper.key) is paper
    assert exam.by_key("exam-9") is None
    assert exam.by_key("") is None


# ---------------------------------------------------------------------------
# Building one
# ---------------------------------------------------------------------------


def _units_of(items) -> list[str]:
    return [content.unit_of(lesson).key for lesson, _, _ in items]


@pytest.mark.parametrize("paper", exam.PAPERS, ids=lambda p: p.key)
def test_a_paper_is_the_length_it_says(paper):
    assert len(exam.build(paper, seed=1)) == paper.questions


@pytest.mark.parametrize("paper", exam.PAPERS, ids=lambda p: p.key)
def test_a_paper_spans_its_units(paper):
    """The property a per-unit check-up cannot have."""
    seen = set(_units_of(exam.build(paper, seed=1)))
    assert seen == set(paper.units), (
        f"{paper.key} drew from {sorted(seen)} of {sorted(paper.units)}"
    )


@pytest.mark.parametrize("paper", exam.PAPERS, ids=lambda p: p.key)
def test_no_question_repeats_a_lesson_before_every_other_has_had_one(paper):
    """Round-robin across lessons rather than sampled. Random choice would
    happily hand out three questions from one lesson and none from four."""
    lessons = [lesson.key for lesson, _, _ in exam.build(paper, seed=1)]
    available = len(exam.lessons_for(paper, 1))
    most = Counter(lessons).most_common(1)[0][1]
    assert most <= -(-paper.questions // available) , (
        f"{paper.key} leans on one lesson: {Counter(lessons).most_common(3)}"
    )


def test_the_same_seed_gives_the_same_paper():
    paper = exam.by_key("final")
    first = [question.key for _, _, question in exam.build(paper, seed=11)]
    again = [question.key for _, _, question in exam.build(paper, seed=11)]
    assert first == again


def test_a_different_seed_gives_a_different_paper():
    """Otherwise a sixteen-question final examines the same sixteen lessons of
    thirty-five for ever, and the rest of the course is unexaminable."""
    paper = exam.by_key("final")
    seeds = [
        tuple(lesson.key for lesson, _, _ in exam.build(paper, seed=seed))
        for seed in range(6)
    ]
    assert len(set(seeds)) > 1


def test_the_units_do_not_march_in_a_cycle():
    """Selected in proportion and left in that order, the units would come
    round in rotation -- and by question three the *position* would be telling
    you the chapter, which is most of what the question was asking."""
    paper = exam.by_key("final")
    unshuffled = exam.draw_from(exam.lessons_for(paper, 3), 14, 3)
    assert len(set(_units_of(unshuffled)[:7])) == 7, (
        "the selection itself should still be one per unit"
    )
    cyclic = 0
    for seed in range(8):
        order = _units_of(exam.build(paper, seed=seed))
        first_round = order[:len(paper.units)]
        if len(set(first_round)) == len(paper.units):
            cyclic += 1
    assert cyclic < 6, "the shuffle is not shuffling"


def test_the_final_is_drawn_in_the_proportions_the_course_teaches():
    """A unit of six lessons should carry about twice the weight of one of
    three. A plain round-robin across units would give them the same."""
    paper = exam.by_key("final")
    sizes = {unit.key: len(unit.quizzable) for unit in exam.units_of(paper)}
    total = sum(sizes.values())
    drawn = Counter(_units_of(exam.build(paper, seed=2)))

    biggest = max(sizes, key=lambda key: sizes[key])
    smallest = min(sizes, key=lambda key: sizes[key])
    assert sizes[biggest] > sizes[smallest]
    assert drawn[biggest] >= drawn[smallest]
    for key, count in drawn.items():
        expected = paper.questions * sizes[key] / total
        assert abs(count - expected) <= 1.5, (
            f"{key} got {count} questions where its share is {expected:.1f}"
        )


def test_a_short_paper_still_touches_every_unit():
    """`length` shortens a paper for a worksheet, and the spread is the reason
    somebody chose a paper rather than a unit."""
    paper = exam.by_key("exam-2")
    items = exam.build(paper, seed=4, length=len(paper.units))
    assert set(_units_of(items)) == set(paper.units)


# ---------------------------------------------------------------------------
# What is in one
# ---------------------------------------------------------------------------


def test_every_question_is_one_the_hub_already_grades():
    """The design, as it is for the check-up: if these were a new kind of
    question they would need a new grader, and a second grader is a second
    opinion about what is correct."""
    from odesuite_app.lessons.model import (
        Choice,
        Expression,
        Model,
        Numeric,
        Solve,
    )

    for paper in exam.PAPERS:
        for lesson, template, question in exam.build(paper, seed=5):
            assert isinstance(question,
                              (Solve, Choice, Numeric, Model, Expression))
            assert template in lesson.templates
            assert content.unit_of(lesson).key in paper.units


def test_draw_from_is_what_the_check_up_uses_too():
    """One routine, so a check-up and a paper cannot drift apart about what a
    mixed set means."""
    from odesuite_app.screens import learn_quiz

    unit = next(unit for unit in content.UNITS if unit.quizzable)
    through_quiz = [q.key for _, _, q in learn_quiz.build(unit, 6, seed=9)]
    direct = [q.key for _, _, q in exam.draw_from(unit.quizzable, 6, 9)]
    assert through_quiz == direct


def test_draw_from_copes_with_lessons_that_have_no_drills():
    """Filtered rather than crashed on, so a half-written lesson cannot take
    the whole paper down with it."""
    empty = [lesson for unit in content.UNITS for lesson in unit.lessons
             if not lesson.templates]
    assert exam.draw_from(empty, 5, 0) == []
    assert exam.draw_from([], 5, 0) == []
