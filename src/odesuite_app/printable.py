"""Pages to print: a worksheet, its solution key, and the formula sheet.

Everything else in this application is answered by typing into a box, and the
examination it is preparing somebody for is written by hand on paper. That gap
is not a detail. Typing ``y = 3*exp(-2*t) + C`` and writing it out are different
motor tasks with different failure modes, and the second is the one being
graded: the arithmetic slips that cost marks are almost all slips of the pen,
and a tool that never once puts a pen in your hand cannot rehearse them. So
this module produces pages, and the questions on them come from exactly the
same draw the screen uses.

Four decisions.

**HTML, not PDF.** The pages are self-contained HTML files with a print
stylesheet: they open in any browser, print from it with the browser's own
dialog, and carry their mathematics inside them as images. A PDF writer would
mean a new dependency for a file nobody edits, and Qt's own printing support
would tie a page to a running application. An HTML file is also legible,
diffable and trivially testable, which a PDF is not.

**The mathematics goes through `mathrender`**, the same typesetter the screen
uses, baked into each page as a data URI. One typesetter means a worksheet
cannot disagree with the lesson it came from about how a formula is set -- and
because the images are embedded, the file is one thing to email, carry on a
stick or open with no network.

**The key is a separate file.** A key stapled to the worksheet is not a key; it
is the answers, three inches below the question. `worksheet` and `solution_key`
are two functions returning two documents, and the caller writes them to two
paths.

**A `Solve` keeps its source form where it cannot be typeset safely.** The
generated equations are assembled from a draw, so there is no authored LaTeX
for them; `typeset` parses the string and asks sympy to set it, and falls back
to the monospace the drill screen shows when the parse does not come out. The
string printed is in every case the string that would be graded.

Qt-free, so a page can be built on a worker thread or in a test with no
interface at all. `work_out` runs the real narrator and is therefore the slow
part -- seconds, sometimes -- which is why the screen that calls it does so off
the interface thread and shows what it is doing.
"""

from __future__ import annotations

import base64
import datetime as _datetime
import struct
from dataclasses import dataclass
from html import escape

__all__ = ["Line", "Worked", "work_out", "typeset", "math_image",
           "worksheet", "solution_key", "formula_sheet", "write"]

#: Black, because a printed page is black on white whatever the application's
#: theme happens to be. The screen's palette has no business on paper.
INK = "#000000"

#: Rendering resolution for the embedded images. Well above screen density:
#: these are printed, and a 96-dpi glyph enlarged by a printer is a smudge.
#: The image is scaled back down to its true point size in the markup, so the
#: extra pixels buy sharpness rather than size.
DPI = 220.0

#: Body size for mathematics set in a question, and in a step of working.
QUESTION_POINTS = 13.0
STEP_POINTS = 11.5

#: How much blank page each question gets to be worked in, in millimetres.
#: Measured against the questions rather than guessed: the long ones here are
#: a second-order forced equation solved by variation of parameters, which is
#: about two thirds of a side by hand.
WORKING_SPACE_MM = 46


@dataclass(frozen=True)
class Line:
    """One line of worked solution: what the move is, and the mathematics."""

    title: str
    latex: str = ""
    note: str = ""
    #: True, False, or None where the step makes no checkable claim. Carried
    #: through from `steps.Step` unchanged -- a key that quietly prints a line
    #: the narrator could not verify would be the one thing worse than no key.
    verified: bool | None = None


@dataclass(frozen=True)
class Worked:
    """The full account of one question, for the key.

    Three shapes, because the three question kinds are answered differently and
    a key that pretended otherwise would be padding. A `Solve` gets the
    narrator's derivation, line by line. A `Choice` gets the option that is
    right and the reason it is -- which is the whole of the answer, since the
    question was never about computing anything. A `Numeric` gets the value and
    the account of where it comes from.
    """

    #: The technique's textbook name, where one was found.
    technique: str = ""
    lines: tuple[Line, ...] = ()
    #: The answer, as LaTeX where there is any, for the box at the end.
    answer_latex: str = ""
    #: The answer as plain text, always present.
    answer: str = ""
    #: Why that is the answer, in prose.
    because: str = ""
    #: Why there is no working, when there is none. Printed rather than
    #: hidden: a key with a silent gap teaches the reader to distrust it.
    problem: str = ""

    @property
    def worked(self) -> bool:
        return bool(self.lines)


# ---------------------------------------------------------------------------
# Working the questions out
# ---------------------------------------------------------------------------


def work_out(question, narrator: str = "steps") -> Worked:
    """The full solution to one question, however that question is answered.

    `narrator` is the lesson's -- "steps", "laplace" or "series" -- because a
    question carries no narrator of its own and the lesson's first example is
    what decides which tool explains the topic.

    Never raises. The narrator reaches sympy, a subprocess and a timeout, and
    a key that failed to build because one question of sixteen could not be
    solved would be worth far less than one that says so on that question.
    """
    kind = getattr(question, "kind", "")
    if kind == "choice":
        return _worked_choice(question)
    if kind == "numeric":
        return _worked_numeric(question)
    if kind == "model":
        return Worked(answer=question.equation,
                      answer_latex=typeset(question.equation),
                      because=question.because or "")
    if kind == "expression":
        return Worked(answer=question.answer,
                      answer_latex=_expression_latex(question.answer),
                      because=question.because or "")
    return _worked_solve(question, narrator)


def _expression_latex(expression: str) -> str:
    """LaTeX for one expression, or "" if sympy will not read it.

    A separate route from `typeset`, which wants a whole equation: an
    integrating factor or a characteristic polynomial has no ``=`` in it and
    `parse_equation` would reject it for exactly that.
    """
    try:
        import sympy as sp

        from .symbolic import _parse_side

        return sp.latex(_parse_side(expression, {}))
    except Exception:
        return ""


def _worked_choice(question) -> Worked:
    """The right option, and the reason it is right.

    There is nothing to narrate: the question asks which technique applies, or
    whether a point is ordinary, and the answer is a judgement rather than a
    computation. The reason is the working.
    """
    index = question.answer
    options = question.options
    chosen = options[index] if 0 <= index < len(options) else ""
    return Worked(answer=chosen, answer_latex="",
                  because=question.because if question.becauses else "")


def _worked_numeric(question) -> Worked:
    """The value, to the precision the tolerance makes meaningful.

    Six significant figures rather than the full float: a question graded to a
    relative tolerance of 1e-6 has no business printing seventeen digits, and a
    key that did would invite somebody to chase the last eleven of them.
    """
    value = f"{question.answer:.6g}"
    if question.units:
        value = f"{value} {question.units}"
    return Worked(answer=value, because=question.because or "")


def _worked_solve(question, narrator: str) -> Worked:
    """The narrator's derivation, line by line.

    The same route the "Show me" button takes on the lesson page, and the same
    one the Solve Step by Step screen takes: parse the equation, hand it to the
    narrator for the topic, and print what comes back. Nothing here decides any
    mathematics.
    """
    try:
        derivation = _narrate(question.equation, question.conditions, narrator)
    except Exception as exc:                  # surfaced on the page, not lost
        return Worked(problem=f"could not be worked here: {exc}")

    if derivation is None:
        return Worked(problem="no technique from this course applies to it.")

    lines = tuple(
        Line(title=step.title, latex=step.latex, note=step.note,
             verified=step.verified)
        for step in derivation.steps
    )
    answer_latex = ""
    if derivation.result is not None:
        from . import mathrender

        answer_latex = mathrender.to_latex(derivation.result)
    return Worked(
        technique=derivation.title,
        lines=lines,
        answer_latex=answer_latex,
        answer=str(derivation.result) if derivation.result is not None else "",
        problem=derivation.message if derivation.result is None else "",
    )


def _narrate(equation: str, conditions: str, narrator: str):
    """The narrated solution, through the routes the Hub tools already use."""
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
        return solve_by_laplace(parsed).derivation
    if narrator == "series":
        from .series import derive as series_derive

        return series_derive(parsed.equation, parsed.function, ics=parsed.ics)
    return solve_symbolically(parsed, steps=True).derivation


def typeset(equation: str, conditions: str = "") -> str:
    """LaTeX for a typed equation, or "" if it cannot be had.

    A generated question has no authored LaTeX -- the equation is assembled
    from a draw, and writing a second LaTeX form of it would be authoring the
    same equation twice and waiting for the two to disagree. So the one string
    there is gets parsed and set by sympy, which derives the typesetting from
    the thing being graded rather than from a copy of it.

    Returns "" rather than raising on anything it cannot parse -- a system
    written with a semicolon, a form sympy reads differently -- and the caller
    prints the source text instead, which is what the drill screen shows.
    """
    try:
        import sympy as sp

        from .laplace import EXTRA_FUNCTIONS
        from .symbolic import parse_equation, spec_for

        parsed = parse_equation(spec_for(equation, conditions),
                                extra_functions=EXTRA_FUNCTIONS)
        pieces = [sp.latex(one) for one in parsed.equations]
    except Exception:
        return ""
    return r",\quad ".join(pieces)


# ---------------------------------------------------------------------------
# Mathematics on the page
# ---------------------------------------------------------------------------


def _png_size(data: bytes) -> tuple[int, int]:
    """The pixel dimensions of a PNG, read from its IHDR chunk.

    Needed because the images are rendered far above screen density for print
    and then scaled back to their true size in the markup: without the true
    pixel count there is no way to work out what that size is. The header is
    fixed-format -- an eight-byte signature, a four-byte length, ``IHDR``, then
    two big-endian 32-bit integers -- so this is a read rather than a parse.
    """
    if len(data) < 24 or data[12:16] != b"IHDR":
        return (0, 0)
    width, height = struct.unpack(">II", data[16:24])
    return (int(width), int(height))


def math_image(latex: str, point_size: float = QUESTION_POINTS,
               *, alt: str = "") -> str:
    """`latex` as an embedded image, or "" if it cannot be typeset.

    The image is drawn at `DPI` and given an explicit CSS width in pixels, so
    the printed glyphs carry the full resolution while occupying the size the
    point value asks for. Without the width a 220-dpi image would print three
    times too large.
    """
    if not latex or not latex.strip():
        return ""
    from . import mathrender

    data = mathrender.latex_to_png(latex, INK, point_size, DPI)
    if not data:
        return ""
    width, _height = _png_size(data)
    if not width:
        return ""
    # CSS pixels are 96 to the inch; the image is DPI to the inch.
    shown = width * 96.0 / DPI
    encoded = base64.b64encode(data).decode("ascii")
    return (f'<img class="math" style="width:{shown:.1f}px" '
            f'alt="{escape(alt or latex, quote=True)}" '
            f'src="data:image/png;base64,{encoded}">')


def _math_or_code(latex: str, source: str, point_size: float) -> str:
    """Typeset mathematics where it can be had, monospace source where not."""
    rendered = math_image(latex, point_size, alt=source or latex)
    if rendered:
        return f'<div class="display">{rendered}</div>'
    return f'<pre class="source">{escape(source or latex)}</pre>'


def _question_body(question) -> str:
    """The equation or statement of one question, as it should appear.

    The prompt is deliberately absent for a `Solve`, exactly as it is in the
    Unit Quiz and for the same reason: a drill prompt names the method, and on
    a mixed paper choosing the method is the question being asked. The other
    four kinds ask for something specific -- a number, an option, the equation
    for a situation, one move of a method -- and name no technique in doing so,
    so their prompts are printed.

    A `Model`'s `equation` is never printed. It is the answer to the question
    rather than the question, which is what makes that kind different from
    every other one here.
    """
    kind = getattr(question, "kind", "")
    out = []
    if kind in ("choice", "numeric", "model", "expression"):
        out.append(f'<p class="prompt">{escape(question.prompt)}</p>')
        if question.latex:
            out.append(_math_or_code(question.latex, "", QUESTION_POINTS))
    else:
        out.append('<p class="prompt">Solve it.'
                   + (" Then satisfy the condition."
                      if question.conditions else "") + "</p>")
        out.append(_math_or_code(typeset(question.equation),
                                 question.equation, QUESTION_POINTS))
        if question.conditions:
            out.append(f'<p class="conditions">'
                       f'{escape(question.conditions)}</p>')
    if kind == "choice":
        out.append("<ol class=\"options\">")
        for option in question.options:
            out.append(f"<li>{escape(option)}</li>")
        out.append("</ol>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# The pages
# ---------------------------------------------------------------------------

_STYLE = """
@page { size: A4; margin: 16mm 15mm 14mm 15mm; }
* { box-sizing: border-box; }
body {
  margin: 0 auto; max-width: 180mm; padding: 10mm 6mm 14mm;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 11.5pt; line-height: 1.45; color: #000; background: #fff;
}
h1 { font-size: 17pt; margin: 0 0 2mm; }
h2 { font-size: 12.5pt; margin: 7mm 0 2mm; padding-bottom: 1mm;
     border-bottom: 1px solid #000; }
h3 { font-size: 11pt; margin: 4mm 0 1mm; font-weight: normal;
     font-style: italic; color: #333; }
.meta { font-size: 9.5pt; color: #333; margin: 0 0 1mm; }
.rules { font-size: 9.5pt; color: #222; border: 1px solid #999;
         padding: 3mm 4mm; margin: 4mm 0 6mm; background: #f6f6f6; }
.rules p { margin: 0 0 1.5mm; }
.rules p:last-child { margin: 0; }
.name-line { margin: 4mm 0 6mm; font-size: 10pt; }
.q { margin: 0 0 4mm; padding: 0; break-inside: avoid; page-break-inside: avoid; }
.q-head { font-weight: bold; font-size: 10.5pt; }
.q-head .from { font-weight: normal; font-style: italic; color: #444; }
.prompt { margin: 1mm 0; }
.conditions { margin: 1mm 0; font-family: "Cascadia Mono", Consolas, monospace;
              font-size: 10pt; }
.display { margin: 2mm 0; text-align: center; }
img.math { vertical-align: middle; max-width: 100%; }
pre.source { margin: 2mm 0; font-family: "Cascadia Mono", Consolas, monospace;
             font-size: 10.5pt; white-space: pre-wrap; text-align: center; }
ol.options { margin: 1mm 0 1mm 6mm; padding: 0; }
ol.options li { margin: 0.5mm 0; }
.space { border-bottom: 1px solid #ccc; }
.step { margin: 0 0 2.5mm; break-inside: avoid; page-break-inside: avoid; }
.step-title { font-size: 10pt; font-weight: bold; }
.step-title .mark { font-weight: normal; color: #444; }
.step-note { font-size: 9.5pt; color: #333; margin: 0.5mm 0 0; }
.answer { margin: 2mm 0 0; padding: 2mm 3mm; border: 1px solid #000; }
.answer .label { font-size: 9pt; text-transform: uppercase;
                 letter-spacing: 0.06em; color: #333; }
.because { font-size: 10pt; margin: 1.5mm 0 0; }
.problem { font-size: 10pt; font-style: italic; color: #444; margin: 1.5mm 0 0; }
.formula { break-inside: avoid; page-break-inside: avoid; margin: 0 0 4mm; }
.formula .heading { font-weight: bold; font-size: 10.5pt; }
.formula .where { font-size: 9pt; color: #555; }
.formula .body { font-size: 9.5pt; color: #222; margin: 1mm 0 0; }
.sheet { column-count: 2; column-gap: 8mm; }
.sheet .display { text-align: left; margin: 1mm 0; }
.foot { margin-top: 8mm; padding-top: 2mm; border-top: 1px solid #ccc;
        font-size: 9pt; color: #555; }
@media print {
  body { max-width: none; padding: 0; }
  .rules { background: none; }
  .no-print { display: none; }
}
"""


def _document(title: str, body: str) -> str:
    """One complete, self-contained page."""
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{escape(title)}</title>\n<style>{_STYLE}</style>\n"
        f"</head>\n<body>\n{body}\n</body>\n</html>\n"
    )


def _today() -> str:
    return _datetime.date.today().isoformat()


def _origin(lesson, unit=None) -> str:
    """Where a question came from, for the key. Never for the worksheet."""
    if unit is None:
        from . import lessons as content

        unit = content.unit_of(lesson)
    return f"{lesson.title}" + (f" · {unit.title}" if unit is not None else "")


def worksheet(title: str, items, *, subtitle: str = "", seed: int | None = None,
              minutes: int = 0, space_mm: int = WORKING_SPACE_MM) -> str:
    """A printable page of questions, with room to work each one.

    `items` is the ``(lesson, template, question)`` triples the quiz and the
    exam both build, so a worksheet is the same paper as a sitting -- printed
    instead of typed.

    The lesson each question came from is **not** printed. That is the same
    rule the Unit Quiz screen keeps: naming the lesson answers the hardest part
    of the question before it is asked. The key names it, because by then the
    question has been attempted.

    `seed` is printed when given, and it is the thing that makes the key
    findable again: a worksheet and its key are the same draw, and the number
    on the foot of the page says which.
    """
    parts = [f"<h1>{escape(title)}</h1>"]
    if subtitle:
        parts.append(f'<p class="meta">{escape(subtitle)}</p>')
    parts.append(
        f'<p class="meta">{len(items)} questions'
        + (f" · {minutes} minutes" if minutes else "")
        + f" · {escape(_today())}</p>"
    )
    parts.append(
        '<div class="rules">'
        "<p><b>Work every question on this page.</b> The answers are on the "
        "separate key; do not open it until you have finished, and mark "
        "against it rather than while you go.</p>"
        "<p>A typed answer is graded in the application by substituting it "
        "into its own equation, so any correct form passes. The same is true "
        "of what you write here: check yours by differentiating it back.</p>"
        "</div>"
    )
    parts.append('<p class="name-line">Name ' + "&nbsp;" * 40
                 + " Date " + "&nbsp;" * 16 + "</p>")

    for number, (_lesson, _template, question) in enumerate(items, start=1):
        parts.append('<div class="q">')
        parts.append(f'<p class="q-head">{number}.</p>')
        parts.append(_question_body(question))
        parts.append(f'<div class="space" style="height:{space_mm}mm"></div>')
        parts.append("</div>")

    parts.append(
        '<p class="foot">Drawn from the odesuite Learning Hub'
        + (f" · paper {seed}" if seed is not None else "")
        + " · the solution key is the companion file.</p>"
    )
    return _document(title, "\n".join(parts))


def solution_key(title: str, items, workings, *, subtitle: str = "",
                 seed: int | None = None) -> str:
    """The narrated working for each question of a worksheet.

    `workings` is one `Worked` per item, in the same order -- produced by
    `work_out`, which is slow enough that the caller runs it off the interface
    thread and may want to show progress while it does.

    Every line of every derivation comes from the narrator, including the ticks
    and crosses beside them: `steps` does not merely print a derivation, it
    differentiates the antiderivatives back and substitutes the basis functions
    into the equation. A line that failed its own check is printed failing,
    because a key that quietly prints a wrong line is worse than no key.
    """
    parts = [f"<h1>{escape(title)}</h1>"]
    if subtitle:
        parts.append(f'<p class="meta">{escape(subtitle)}</p>')
    parts.append(
        f'<p class="meta">Solution key · {len(items)} questions · '
        f"{escape(_today())}"
        + (f" · paper {seed}" if seed is not None else "") + "</p>"
    )
    parts.append(
        '<div class="rules">'
        "<p><b>The working below is generated, not transcribed.</b> Each "
        "derivation is produced by the same narrator that powers the tool for "
        "its topic, and each line that makes a checkable claim has been "
        "checked — the antiderivatives differentiated back, the basis "
        "functions substituted in. A line marked ✗ failed that check and is "
        "shown failing rather than hidden.</p>"
        "<p>Where your answer differs from the one here, that is not by "
        "itself a mistake: a general solution has many correct forms. "
        "Substitute yours into the equation.</p>"
        "</div>"
    )

    for number, ((lesson, _template, question), worked) in enumerate(
            zip(items, workings), start=1):
        parts.append('<div class="q">')
        parts.append(
            f'<p class="q-head">{number}. '
            f'<span class="from">{escape(_origin(lesson))}'
            + (f" · {escape(worked.technique)}" if worked.technique else "")
            + "</span></p>"
        )
        parts.append(_question_body(question))
        parts.extend(_key_body(worked))
        parts.append("</div>")

    parts.append('<p class="foot">odesuite Learning Hub'
                 + (f" · paper {seed}" if seed is not None else "") + "</p>")
    return _document(f"{title} — solution key", "\n".join(parts))


def _key_body(worked: Worked) -> list[str]:
    """The working, the answer, and the reason — whichever of them exist."""
    parts = []
    for index, line in enumerate(worked.lines, start=1):
        mark = ("✓" if line.verified is True
                else "✗" if line.verified is False else "")
        parts.append('<div class="step">')
        parts.append(
            f'<p class="step-title">{index}. {escape(line.title)}'
            + (f' <span class="mark">{mark}</span>' if mark else "")
            + "</p>"
        )
        if line.latex:
            image = math_image(line.latex, STEP_POINTS)
            parts.append(f'<div class="display">{image}</div>' if image
                         else f'<pre class="source">{escape(line.latex)}</pre>')
        if line.note:
            parts.append(f'<p class="step-note">{escape(line.note)}</p>')
        parts.append("</div>")

    if worked.answer_latex or worked.answer:
        image = math_image(worked.answer_latex, QUESTION_POINTS)
        parts.append('<div class="answer">')
        parts.append('<p class="label">Answer</p>')
        parts.append(f'<div class="display">{image}</div>' if image
                     else f'<pre class="source">{escape(worked.answer)}</pre>')
        parts.append("</div>")
    if worked.because:
        parts.append(f'<p class="because">{escape(worked.because)}</p>')
    if worked.problem:
        parts.append(f'<p class="problem">{escape(worked.problem)}</p>')
    return parts


def formula_sheet(units=None, *, title: str = "Formula sheet",
                  subtitle: str = "", include_body: bool = False) -> str:
    """Every formula in the course, or in the units given, on one sheet.

    The examination allows a crib sheet, and this course already contains one.
    Sixty-five notes were written as ``kind="formula"`` because a formula is a
    different sort of thing from an idea or a pitfall and is boxed differently
    on the lesson page; that classification was made a card at a time, for the
    reader's sake, and this collects on it. The sheet is therefore *found* in
    the course rather than authored beside it, and cannot drift from what the
    lessons teach.

    `include_body` prints the sentence that came with each formula. Off by
    default, because a crib sheet you have to read is not a crib sheet -- but
    a first pass through one is much easier with the sentences, so it is one
    switch rather than a second document.
    """
    from . import lessons as content

    found = content.formulas(units)
    parts = [f"<h1>{escape(title)}</h1>"]
    if subtitle:
        parts.append(f'<p class="meta">{escape(subtitle)}</p>')
    parts.append(
        f'<p class="meta">{len(found)} formulas · {escape(_today())}</p>'
    )

    current_unit = None
    current_lesson = None
    open_sheet = False
    for unit, lesson, note in found:
        if unit is not current_unit:
            if open_sheet:
                parts.append("</div>")
                open_sheet = False
            parts.append(f"<h2>{escape(unit.title)}"
                         + (f' <span class="where">{escape(unit.reference)}'
                            "</span>" if unit.reference else "")
                         + "</h2>")
            parts.append('<div class="sheet">')
            open_sheet = True
            current_unit = unit
            current_lesson = None
        if lesson is not current_lesson:
            parts.append(f"<h3>{escape(lesson.title)}</h3>")
            current_lesson = lesson
        parts.append('<div class="formula">')
        parts.append(f'<p class="heading">{escape(note.heading)}</p>')
        if note.latex:
            image = math_image(note.latex, QUESTION_POINTS)
            parts.append(f'<div class="display">{image}</div>' if image
                         else f'<pre class="source">{escape(note.latex)}</pre>')
        if include_body:
            parts.append(f'<p class="body">{escape(note.body)}</p>')
        parts.append("</div>")
    if open_sheet:
        parts.append("</div>")

    parts.append(
        '<p class="foot">Collected from the odesuite Learning Hub — every '
        "formula box in the lessons it covers, in course order.</p>"
    )
    return _document(title, "\n".join(parts))


def write(html: str, destination) -> object:
    """Write a page to `destination`, creating its folder, and return the path.

    UTF-8 explicitly: the pages carry ✓, ✗ and the en dashes the course's prose
    is full of, and a page written in the platform's ANSI codepage would show
    mojibake in the one place -- print -- where it cannot be fixed afterwards.
    """
    from pathlib import Path

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")
    return destination
