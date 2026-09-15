"""Pages to print: the worksheet, its key, and the formula sheet.

One rule runs through all of it and is the reason most of these tests exist:
**the worksheet must not say anything the sat paper would not.** Naming the
lesson a question came from would answer the hardest part of it, and the answer
to a `Model` question is stored in the field called `equation`, which is
exactly the field every other question type prints. Both are one line away from
being leaked onto the page, so both are tested for by looking at the page.

The rest is about the pages being self-contained: mathematics embedded as
images rather than fetched, UTF-8 on disk, and a key that is a separate
document from the questions it answers.
"""

from __future__ import annotations

import re

import pytest

pytest.importorskip("sympy")
pytest.importorskip("matplotlib")

from odesuite_app import exam, printable  # noqa: E402
from odesuite_app import lessons as content  # noqa: E402
from odesuite_app.lessons import generate  # noqa: E402


@pytest.fixture(scope="module")
def items():
    """A short paper, spanning two units. Small, because the key narrates."""
    return exam.build(exam.by_key("exam-1"), seed=5, length=4)


def _templates_of(kind: str) -> list:
    """Every template in the course whose draws are of one kind, with a lesson."""
    found = []
    for unit in content.UNITS:
        for lesson in unit.lessons:
            for template in lesson.templates:
                if generate.draw(template, 0).kind == kind:
                    found.append((lesson, template))
    return found


def _one(kind: str):
    """One drawn question of `kind`, with the lesson it came from."""
    found = _templates_of(kind)
    if not found:
        pytest.skip(f"the course has no {kind} template")
    lesson, template = found[0]
    return lesson, template, generate.draw(template, 0)


def _strip_images(html: str) -> str:
    """The page with its data URIs removed, so a search reads the text."""
    return re.sub(r'src="data:image/png;base64,[^"]*"', "src=IMG", html)


# ---------------------------------------------------------------------------
# What a worksheet may say
# ---------------------------------------------------------------------------


def test_a_worksheet_never_names_the_lesson_a_question_came_from(items):
    """The claim the whole screen rests on. Choosing the method is most of
    what a mixed paper asks, and the lesson title answers it."""
    page = _strip_images(printable.worksheet("Practice", items))
    for lesson, _template, _question in items:
        assert lesson.title not in page, f"the page named {lesson.title!r}"
    for unit in content.UNITS:
        assert unit.title not in page


def test_a_worksheet_never_prints_the_answer_to_a_model_question():
    """A `Model` asks you to write the equation, so its `equation` field is
    the answer -- and it is the very field every other kind prints."""
    lesson, _template, question = _one("model")
    page = _strip_images(printable.worksheet("Practice",
                                             [(lesson, _template, question)]))
    assert question.prompt in page or question.prompt[:40] in page
    assert question.equation not in page
    assert question.because not in page


def test_a_worksheet_leaves_room_to_work_each_question(items):
    page = printable.worksheet("Practice", items, space_mm=40)
    assert page.count('class="space"') == len(items)
    assert "height:40mm" in page


def test_a_worksheet_numbers_every_question(items):
    page = _strip_images(printable.worksheet("Practice", items))
    for number in range(1, len(items) + 1):
        assert f'<p class="q-head">{number}.</p>' in page


def test_a_worksheet_prints_the_seed_so_its_key_can_be_found(items):
    page = printable.worksheet("Practice", items, seed=4321)
    assert "paper 4321" in page


def test_the_options_of_a_multiple_choice_question_reach_the_page():
    lesson, template, question = _one("choice")
    page = _strip_images(
        printable.worksheet("Practice", [(lesson, template, question)])
    )
    for option in question.options:
        assert option in page or option.replace("'", "&#x27;") in page


# ---------------------------------------------------------------------------
# The key
# ---------------------------------------------------------------------------


def test_the_key_is_a_separate_document(items):
    """Stapled to the worksheet it is not a key, it is the answers three
    inches below the question."""
    workings = [printable.Worked(answer="42") for _ in items]
    sheet = printable.worksheet("Practice", items)
    key = printable.solution_key("Practice", items, workings)
    assert sheet != key
    assert sheet.count("<!doctype html>") == key.count("<!doctype html>") == 1
    assert "solution key" in key.lower()
    assert "42" in _strip_images(key)


def test_the_key_names_the_lesson_the_worksheet_would_not(items):
    """By the time the key is open the question has been attempted, and the
    lesson behind it is the most useful thing there is to say."""
    workings = [printable.Worked() for _ in items]
    key = _strip_images(printable.solution_key("Practice", items, workings))
    for lesson, _template, _question in items:
        assert lesson.title in key


def test_a_step_that_failed_its_own_check_is_shown_failing():
    """`steps` differentiates its antiderivatives back and substitutes its
    basis functions in. A key that quietly printed a line the narrator could
    not verify would be worse than no key at all."""
    worked = printable.Worked(lines=(
        printable.Line("Checked and fine", "x = 1", verified=True),
        printable.Line("Checked and not", "x = 2", verified=False),
        printable.Line("Nothing to check", "x = 3", verified=None),
    ))
    page = _strip_images(printable.solution_key(
        "Practice", [(content.LESSONS[0], None, _one("solve")[2])], [worked]
    ))
    assert "✓" in page and "✗" in page
    assert page.count('class="mark"') == 2, "the unchecked step gained a mark"


@pytest.mark.parametrize("kind", ["choice", "numeric", "model", "expression"])
def test_work_out_answers_the_kinds_that_are_not_narrated(kind):
    """Four of the five question types have no derivation to print -- the
    answer is a judgement, a number, an equation or one expression -- and what
    the key owes each of them is the answer and the reason for it."""
    _lesson, _template, question = _one(kind)
    worked = printable.work_out(question)
    assert worked.answer, f"{kind} produced no answer"
    assert worked.because, f"{kind} produced no reason"
    assert not worked.lines, "there is nothing to narrate here"
    assert not worked.problem


def test_work_out_narrates_a_solve():
    """The slow one, and the reason the screen does this on a worker."""
    from odesuite_app.lessons.model import Solve

    question = Solve(key="t", prompt="", equation="y' = 2*y",
                     conditions="y(0) = 3")
    worked = printable.work_out(question, "steps")
    assert worked.technique
    assert worked.lines, "no working was produced"
    assert any(line.verified is not None for line in worked.lines), (
        "not one line of the derivation was checked"
    )
    assert worked.answer_latex
    assert not worked.problem


def test_work_out_reports_a_question_it_cannot_do_rather_than_raising():
    """A key that failed to build because one question of sixteen could not be
    solved would be worth far less than one that says so on that question."""
    from odesuite_app.lessons.model import Solve

    broken = Solve(key="t", prompt="", equation="this is not an equation")
    worked = printable.work_out(broken, "steps")
    assert worked.problem
    assert not worked.lines


# ---------------------------------------------------------------------------
# The formula sheet
# ---------------------------------------------------------------------------


def test_every_formula_note_in_the_course_reaches_the_sheet():
    """Found in the course rather than authored beside it, so it cannot drift
    from what the lessons teach."""
    found = content.formulas()
    assert len(found) >= 60, f"only {len(found)} formula notes were collected"
    page = _strip_images(printable.formula_sheet())
    for _unit, _lesson, note in found:
        assert note.heading in page or note.heading.replace("'", "&#x27;") in page
    assert f"{len(found)} formulas" in page


def test_the_sheet_can_be_narrowed_to_one_unit():
    unit = content.UNITS[0]
    page = _strip_images(printable.formula_sheet((unit,)))
    assert unit.title in page
    for other in content.UNITS[1:]:
        assert other.title not in page


def test_a_crib_sheet_leaves_the_prose_out_unless_asked():
    """A crib sheet you have to read is not a crib sheet — but a first pass
    through one is much easier with the sentences, so it is one switch."""
    _unit, _lesson, note = content.formulas()[0]
    assert note.body
    without = _strip_images(printable.formula_sheet((content.UNITS[0],)))
    with_it = _strip_images(
        printable.formula_sheet((content.UNITS[0],), include_body=True)
    )
    assert note.body[:40] not in without
    assert note.body[:40] in with_it


def test_the_sheet_groups_by_unit_and_by_lesson():
    page = printable.formula_sheet((content.UNITS[0],))
    assert page.count("<h2>") == 1
    assert page.count("<h3>") >= 2


# ---------------------------------------------------------------------------
# The pages as files
# ---------------------------------------------------------------------------


def test_a_page_carries_its_mathematics_inside_it(items):
    """Self-contained: no network, no LaTeX installation, one file to email."""
    page = printable.worksheet("Practice", items)
    assert 'src="data:image/png;base64,' in page
    stripped = _strip_images(page)
    assert "http://" not in stripped and "https://" not in stripped
    assert "<script" not in stripped


def test_an_untypesettable_formula_falls_back_to_its_source():
    """Mathtext has no environments, and a silent blank where a formula should
    be is the failure this application has been bitten by before."""
    assert printable.math_image(r"\begin{matrix} 1 \end{matrix}") == ""
    assert printable.math_image("") == ""
    assert printable.math_image("x^2").startswith("<img")


def test_an_image_is_scaled_back_to_the_size_its_points_ask_for():
    """Rendered far above screen density for print, then given an explicit CSS
    width. Without the width a 220-dpi image prints three times too large."""
    tag = printable.math_image("x^2 + y^2", point_size=13)
    width = float(re.search(r"width:([\d.]+)px", tag).group(1))
    assert 10 < width < 200, f"a two-term expression came out {width}px wide"


def test_png_dimensions_are_read_from_the_header():
    data = __import__("odesuite_app.mathrender", fromlist=["x"]).latex_to_png(
        "x", "#000000", 13.0, printable.DPI
    )
    width, height = printable._png_size(data)
    assert width > 0 and height > 0
    assert printable._png_size(b"") == (0, 0)
    assert printable._png_size(b"not a png at all, but long enough") == (0, 0)


def test_writing_a_page_uses_utf8_whatever_the_platform_prefers(tmp_path):
    """The pages carry ✓, ✗ and the en dashes the course's prose is full of,
    and this machine's default codepage is not UTF-8. Mojibake in print is the
    one place it cannot be fixed afterwards."""
    page = printable.solution_key(
        "Practice", [], [], subtitle="checked — ✓ and ✗"
    )
    where = printable.write(page, tmp_path / "deeper" / "key.html")
    assert where.exists()
    assert "✓" in where.read_text(encoding="utf-8")


def test_typeset_falls_back_rather_than_raising():
    assert printable.typeset("y' + 2*y = 0").strip()
    assert printable.typeset("not an equation at all") == ""
