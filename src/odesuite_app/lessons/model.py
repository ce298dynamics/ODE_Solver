"""What a lesson is made of.

Content only -- no PySide6, no Qt, no sympy -- so the curriculum can be read,
counted and tested without an interface, and so a unit module is a file anyone
can edit without knowing how the screen works.

Three of these shapes carry a decision worth stating, because they are what
keep this from being a quiz with a stored answer key.

**`Solve` questions are graded by mathematics, not by comparison.** The answer
is substituted into the equation and simplified, through the same
`symbolic.check_answer` the Solve Step by Step screen uses. Any correct form
passes and nothing is marked wrong merely for being spelled differently. So a
`Solve` stores no answer at all -- only the equation, which is the question.

**`Choice` questions exist for what that cannot reach**, and each carries one
reason *per option*. A tick that does not say why teaches nothing, and a cross
that does not say why teaches less: the reason a wrong option was tempting is
usually the thing the student actually got wrong.

**`Example`s are equations a narrator can work through**, never transcribed
working. An example that drifted out of step with the tool that explains it
would be worse than none.

**A `Template` is a factory for `Solve`s**, and that is the whole of the drill
design: a generated question *is* an ordinary practice question, so the grading,
the hint ladder, "Show me" and the recording of progress are all reused rather
than rebuilt for it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

__all__ = [
    "NOTE_KINDS",
    "Note",
    "Example",
    "Choice",
    "Solve",
    "Template",
    "Lesson",
    "Unit",
    "grade_choice",
]

#: How a note is presented. `idea` is the default prose card; `formula` is a
#: result to keep; `pitfall` is the mistake this topic actually produces, boxed
#: so it reads differently from an idea; `aside` is context that can be skipped.
NOTE_KINDS = ("idea", "formula", "pitfall", "aside")


@dataclass(frozen=True)
class Note:
    """One idea, with the formula that carries it."""

    heading: str
    body: str
    #: Displayed centred beneath the prose. LaTeX, typeset like everything else.
    latex: str = ""
    #: One of `NOTE_KINDS`.
    kind: str = "idea"


@dataclass(frozen=True)
class Example:
    """An equation the narrator works through, and what it is here to show."""

    equation: str
    conditions: str = ""
    #: Which narrator explains it: "steps" or "laplace".
    narrator: str = "steps"
    #: What this example is *for*. A lesson usually wants a plain case and then
    #: one that breaks the plain rule, and the reader should be told which is
    #: which before the working appears.
    why: str = ""


@dataclass(frozen=True)
class Choice:
    """A question with one right option and a reason for every option."""

    key: str
    prompt: str
    options: tuple[str, ...]
    #: Index into `options`.
    answer: int
    #: One per option, in the same order: why this one is right, or why it is
    #: tempting and wrong. Shown for the option picked, whichever it was.
    becauses: tuple[str, ...]
    #: The equation the question is about, if it is about one.
    latex: str = ""

    kind: str = field(default="choice", init=False)

    @property
    def because(self) -> str:
        """The reason the right answer is right."""
        return self.becauses[self.answer]


@dataclass(frozen=True)
class Solve:
    """Solve it and type the answer; graded by substitution."""

    key: str
    prompt: str
    #: As it would be typed into the editor, so the grader parses it the same
    #: way the rest of the application does.
    equation: str
    conditions: str = ""
    #: The ladder, in order: a nudge, then the first move, then the next. Each
    #: is revealed only when asked for, and "Show me" -- the narrator itself --
    #: sits at the end of it.
    hints: tuple[str, ...] = ()

    kind: str = field(default="solve", init=False)

    @property
    def hint(self) -> str:
        """The first rung, for callers that want one line."""
        return self.hints[0] if self.hints else ""


@dataclass(frozen=True)
class Template:
    """A practice question with its numbers left open.

    Generated questions come out as ordinary `Solve`s, so nothing downstream
    knows the difference: the same grader, the same hint ladder, the same
    "Show me". A template only decides which numbers go in.

    `slots` is a tuple of `(names, values)` pairs rather than a mapping, so a
    template stays hashable and its draws stay in a fixed order. A name holding
    a comma binds several at once from one tuple::

        slots=(("b,c", ((3, 2), (4, 4), (2, 5))),)

    which is what the second-order templates need: drawing `b` and `c`
    independently produces discriminants whose roots are irrational, and the
    point of a drill is repetition of the method rather than of the arithmetic.
    """

    key: str
    #: What this drill is, in the header: "Integrating factor, constant p".
    title: str
    #: All four of these are format strings over the slot names.
    prompt: str
    equation: str
    conditions: str = ""
    hints: tuple[str, ...] = ()
    slots: tuple[tuple[str, tuple], ...] = ()
    #: Draws to throw away, as a predicate over the drawn values. Keeps a
    #: template from producing the degenerate case it was not written for.
    reject: Callable[[Mapping[str, object]], bool] | None = None
    #: The technique the generated question must be narrated by. Asserted in
    #: the tests, so a template that quietly starts producing something else is
    #: a failure rather than a surprise.
    technique: str = ""
    #: Which narrator works it: "steps" or "laplace".
    narrator: str = "steps"

    kind: str = field(default="template", init=False)


@dataclass(frozen=True)
class Lesson:
    key: str
    title: str
    #: One sentence: what this is for.
    summary: str
    notes: tuple[Note, ...]
    questions: tuple[Choice | Solve, ...]
    #: The Hub screen that does this technique, offered as a way on.
    tool: str
    #: What you should be able to do afterwards. Written as verbs, because a
    #: goal you cannot tell whether you have met is not a goal.
    objectives: tuple[str, ...] = ()
    #: Worked through by the narrator, in the order they should be read.
    examples: tuple[Example, ...] = ()
    #: Practice that never runs out. A lesson with none simply has no Drill —
    #: Euler and RK4 have no closed form to substitute into, and a drill whose
    #: verdict could never be "right" would be worse than no drill.
    templates: tuple[Template, ...] = ()
    #: Lesson keys worth having met first. Advisory: nothing is locked.
    prerequisites: tuple[str, ...] = ()
    #: A figure to put at the top of Learn, named by key rather than built
    #: here: this module is content and holds no Qt, which is what lets the
    #: whole course be read and tested without an interface. The keys live in
    #: `widgets.lessonfigure.FIGURES`, and the tests require every one used
    #: here to be found there.
    figure: str = ""
    #: Where this sits in Edwards, Penney and Calvis, 6e.
    reference: str = ""

    @property
    def example(self) -> str:
        """The first example's equation, for callers that want just one."""
        return self.examples[0].equation if self.examples else ""

    @property
    def example_conditions(self) -> str:
        return self.examples[0].conditions if self.examples else ""

    @property
    def narrator(self) -> str:
        return self.examples[0].narrator if self.examples else "steps"


@dataclass(frozen=True)
class Unit:
    """A run of lessons that a course meets together and examines together."""

    key: str
    title: str
    #: What the unit is about, in a sentence or two.
    summary: str
    lessons: tuple[Lesson, ...]
    #: The chapter in Edwards, Penney and Calvis, 6e.
    reference: str = ""
    #: Lesson keys the unit check-up draws from. Empty means every lesson in
    #: the unit that has drills, which is the right default: a quiz is built
    #: out of templates, so a lesson with none has nothing to contribute.
    #: Naming them is for units where some lesson should be left out of the
    #: mixed set even though it could supply questions.
    quiz: tuple[str, ...] = ()

    @property
    def questions(self) -> int:
        return sum(len(lesson.questions) for lesson in self.lessons)

    @property
    def quizzable(self) -> tuple[Lesson, ...]:
        """The lessons a check-up may draw on, in course order."""
        named = set(self.quiz)
        return tuple(lesson for lesson in self.lessons
                     if lesson.templates and (not named or lesson.key in named))


def grade_choice(question: Choice, picked: int) -> bool:
    return picked == question.answer
