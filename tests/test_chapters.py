"""The textbook chapters: long enough, and right where they can be checked.

A chapter's worked examples are hand-written mathematics, which is exactly
where a slip survives longest -- a reader copies it, and the next reader too.
So every answer a worked example states is substituted back into its equation
and its conditions, every displayed equation is rendered, and every plotted
curve is evaluated. A chapter is also held to its length: five pages, about
2,400 words of prose, unless it says here why it is shorter.
"""

from __future__ import annotations

import numpy as np
import pytest

from odesuite_app.lessons import LESSONS
from odesuite_app.lessons.chapter import BOX_KINDS, blocks_of, words

#: Lessons written up as chapters, in the order they were written. Like
#: `FULL_DEPTH` in test_lessons: a chapter is not finished until it is listed,
#: and a lesson that grows a chapter without being listed fails below.
CHAPTERED = (
    "basics",
    "slopefields",
    "separable",
    "linear",
    "exact",
    "substitutions",
    "population",
    "equilibria",
    "motion",
    "numerical",
    "rungekutta",
    "superposition",
)

#: About five pages of prose.
MIN_WORDS = 2400

#: Lessons allowed to be shorter, and why. Empty until one earns it.
SHORTER: dict[str, str] = {}

CHAPTERS = [lesson for lesson in LESSONS if lesson.chapter]
IDS = [lesson.key for lesson in CHAPTERS]


def test_the_chaptered_list_is_honest():
    assert [lesson.key for lesson in CHAPTERS] == [
        lesson.key for lesson in LESSONS if lesson.key in CHAPTERED]
    assert set(CHAPTERED) == {lesson.key for lesson in CHAPTERS}


@pytest.mark.parametrize("lesson", CHAPTERS, ids=IDS)
def test_a_chapter_is_five_pages(lesson):
    count = words(lesson.chapter)
    floor = MIN_WORDS if lesson.key not in SHORTER else 1200
    assert count >= floor, f"{lesson.key}: {count} words"


@pytest.mark.parametrize("lesson", CHAPTERS, ids=IDS)
def test_a_chapter_has_the_parts_a_textbook_section_has(lesson):
    blocks = blocks_of(lesson.chapter)
    kinds = [block.kind for block in blocks]
    assert len(lesson.chapter) >= 4, "too few sections"
    assert kinds.count("worked") >= 3, "a chapter works several examples"
    assert any(block.kind == "box" and block.box in ("definition", "theorem")
               for block in blocks), "no definition or theorem stated"
    assert kinds.count("plot") + kinds.count("figure") >= 2, "too few graphs"
    for block in blocks:
        if block.kind == "box":
            assert block.box in BOX_KINDS, block.box


def _latex_of(lesson):
    for block in blocks_of(lesson.chapter):
        if block.kind == "display":
            yield block.latex
        elif block.kind == "box" and block.latex:
            yield block.latex
        elif block.kind == "worked":
            for step in block.steps:
                if step.latex:
                    yield step.latex
            if block.answer_latex:
                yield block.answer_latex


@pytest.mark.parametrize("lesson", CHAPTERS, ids=IDS)
def test_every_equation_in_a_chapter_typesets(lesson):
    """Rendered, not merely passed by `is_renderable` -- see the matching test
    in test_lessons for the silent failure this catches."""
    from odesuite_app import mathrender

    for latex in _latex_of(lesson):
        assert mathrender.is_renderable(latex), f"refused: {latex!r}"
        png = mathrender.latex_to_png(latex, "#000000", 15.0, 110.0)
        assert png.startswith(b"\x89PNG"), f"cannot typeset: {latex!r}"


def _worked(lesson):
    return [block for block in blocks_of(lesson.chapter)
            if block.kind == "worked"]


WORKED = [(lesson, block) for lesson in CHAPTERS for block in _worked(lesson)
          if block.equation]


@pytest.mark.parametrize("lesson,example", WORKED,
                         ids=[f"{le.key}-{ex.title[:30]}" for le, ex in WORKED])
def test_every_worked_answer_satisfies_its_equation(lesson, example):
    from odesuite_app.laplace import EXTRA_FUNCTIONS
    from odesuite_app.symbolic import check_answer, parse_equation, spec_for

    assert example.answer, "an equation with no answer to check"
    parsed = parse_equation(spec_for(example.equation, example.conditions),
                            extra_functions=EXTRA_FUNCTIONS)
    verdict = check_answer(parsed, example.answer)
    assert verdict.correct is True, (
        f"{example.title}: {example.answer} -- {verdict.message}")
    assert verdict.matches_conditions is not False, (
        f"{example.title}: misses {example.conditions}")


@pytest.mark.parametrize("lesson", CHAPTERS, ids=IDS)
def test_every_plotted_curve_evaluates(lesson):
    from odesuite_app.widgets.chapterview import evaluate_curve

    for block in blocks_of(lesson.chapter):
        if block.kind != "plot":
            continue
        assert block.caption, f"{block.title}: a graph with no caption"
        for curve in block.curves:
            xs, ys = evaluate_curve(curve, block.t)
            finite = np.isfinite(xs) & np.isfinite(ys)
            assert finite.mean() > 0.25, f"{block.title}: {curve.expr}"


@pytest.mark.parametrize("lesson", CHAPTERS, ids=IDS)
def test_every_figure_in_a_chapter_exists(lesson):
    pytest.importorskip("PySide6")
    from odesuite_app.widgets.lessonfigure import FIGURES

    for block in blocks_of(lesson.chapter):
        if block.kind == "figure":
            assert block.key in FIGURES, block.key


@pytest.mark.parametrize("lesson", CHAPTERS, ids=IDS)
def test_a_chapter_renders_on_the_learn_page(lesson, qapp):
    from odesuite_app.theme import PALETTES
    from odesuite_app.widgets.chapterview import ChapterView

    view = ChapterView(lesson.chapter, PALETTES["dark"])
    view.resize(900, 600)
    qapp.processEvents()
    assert not view.grab().isNull()
    view.deleteLater()


@pytest.fixture(scope="module")
def qapp():
    pytest.importorskip("PySide6", reason="the app extra is not installed")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])
