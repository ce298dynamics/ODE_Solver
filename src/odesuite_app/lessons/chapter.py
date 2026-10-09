"""A lesson written as a textbook section.

The first form of the Learn page was a column of cards -- objectives, a few
paragraphs of motivation, a derivation cut into numbered one-paragraph steps,
and three to five short notes. About a thousand words a lesson, with nothing
connecting one card to the next. The complaint that replaced it was fair:
too short, and badly formatted, and not what a textbook reads like.

A chapter is a sequence of `Section`s, each a sequence of blocks read top to
bottom as one document:

* `Para`     -- prose, with ``*emphasis*`` as everywhere else in the course;
* `Display`  -- a displayed equation, optionally numbered;
* `Box`      -- a definition, theorem, proof, remark or warning, set apart;
* `Worked`   -- a worked example: the problem, the solution in steps, and an
  answer that the tests substitute back into the equation;
* `Plot`     -- a static graph, drawn from expressions rather than pictures,
  so the curves are computed and cannot be wrong in a way nobody checks;
* `Figure`   -- one of the interactive lesson figures, placed in the text.

**What is checked** (`tests/test_chapters.py`): length, so a chapter is five
pages unless it says why it is shorter; that every displayed equation really
typesets; that every worked example's answer satisfies its equation and its
conditions; that every plotted expression evaluates over its range; and that
every figure named exists. A textbook's worked examples are the part most
likely to carry a slip, and here each one is a claim a test can falsify.

Content only -- no Qt, no sympy at import -- like the rest of this package.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

__all__ = ["Para", "Display", "Box", "Worked", "Plot", "Curve", "Figure",
           "Section", "BOX_KINDS", "words", "blocks_of"]

#: What a `Box` can be, in the order a reader meets them.
BOX_KINDS = ("definition", "theorem", "proof", "remark", "warning")


@dataclass(frozen=True)
class Para:
    text: str
    kind: str = field(default="para", init=False)


@dataclass(frozen=True)
class Display:
    latex: str
    #: Shown at the right margin, as (1.3) is in a textbook. Empty for none.
    number: str = ""
    kind: str = field(default="display", init=False)


@dataclass(frozen=True)
class Box:
    #: One of `BOX_KINDS`.
    box: str
    title: str
    body: str
    latex: str = ""
    kind: str = field(default="box", init=False)


@dataclass(frozen=True)
class Step:
    """One move in a worked example: what is done, and the result of doing it."""

    prose: str
    latex: str = ""


@dataclass(frozen=True)
class Worked:
    """A worked example, with its answer checked by substitution.

    `equation` and `conditions` are the machine form the rest of the course
    uses (``"y' = t*y"``, ``"y(0) = 2"``); `answer` is the solution as it would
    be typed. The tests put the answer through `symbolic.check_answer`, so a
    worked example with a slip in it fails rather than teaches the slip.

    An example that is not an equation to solve -- computing a transform, say
    -- leaves `equation` empty and has nothing to substitute into.
    """

    title: str
    problem: str
    steps: tuple[Step, ...]
    equation: str = ""
    conditions: str = ""
    answer: str = ""
    #: The answer as it should be shown, when that differs from `answer`.
    answer_latex: str = ""
    kind: str = field(default="worked", init=False)


@dataclass(frozen=True)
class Curve:
    """One curve on a `Plot`: y = expr(t), or the parametric (x(t), y(t))."""

    expr: str
    label: str = ""
    #: For a parametric curve, the second coordinate; `expr` is then x(t).
    y: str = ""


@dataclass(frozen=True)
class Plot:
    title: str
    caption: str
    curves: tuple[Curve, ...]
    #: The range of the parameter t.
    t: tuple[float, float] = (0.0, 5.0)
    xlabel: str = "t"
    ylabel: str = "y"
    #: Fixed vertical range, or None to fit the curves.
    ylim: tuple[float, float] | None = None
    kind: str = field(default="plot", init=False)


@dataclass(frozen=True)
class Figure:
    #: A key into `widgets.lessonfigure.FIGURES`.
    key: str
    #: What to do with it, here. The figure's own caption says what it is.
    caption: str = ""
    kind: str = field(default="figure", init=False)


@dataclass(frozen=True)
class Section:
    title: str
    blocks: tuple


_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")


def blocks_of(sections) -> list:
    return [block for section in sections for block in section.blocks]


def words(sections) -> int:
    """Words of prose a reader reads, the measure of "five pages".

    Prose only: equations are not words, and counting their symbols would let
    a chapter reach its length on notation.
    """
    count = 0
    for section in sections:
        count += len(_WORD.findall(section.title))
        for block in section.blocks:
            if block.kind == "para":
                texts = [block.text]
            elif block.kind == "box":
                texts = [block.title, block.body]
            elif block.kind == "worked":
                texts = [block.title, block.problem] + [s.prose for s in block.steps]
            elif block.kind in ("plot", "figure"):
                texts = [getattr(block, "caption", "")]
            else:
                texts = []
            count += sum(len(_WORD.findall(text)) for text in texts)
    return count
