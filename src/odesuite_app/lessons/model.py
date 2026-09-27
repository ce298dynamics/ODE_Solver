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

**`Numeric` questions are for when the answer is a number**, which a
substitution check cannot grade and four options misrepresent. One Euler step,
a terminal velocity, the trace of a matrix: each has a single right value, and
what a grader owes it is a tolerance rather than a comparison of strings.

**`Example`s are equations a narrator can work through**, never transcribed
working. An example that drifted out of step with the tool that explains it
would be worse than none.

**A `Template` is a factory for `Solve`s**, and that is the whole of the drill
design: a generated question *is* an ordinary practice question, so the grading,
the hint ladder, "Show me" and the recording of progress are all reused rather
than rebuilt for it.

Four later shapes answer the same complaint about all of the above: every one
of them hands the student an equation and asks what to do with it, which is
not what an examination does.

**`Model` asks for the equation itself** -- from a situation described in
words, or from the family of curves that solves it. Nothing can be substituted
into a word problem, so it is graded by `symbolic.check_model`, which asks
whether two equations are the same rather than whether two strings are.

**`Expression` asks for one move of the method** -- the integrating factor, the
characteristic polynomial, the Wronskian. Also not a solution, also graded by
equivalence, and the only question type here that asks what a student can
*produce* rather than what they can recognise or finish.

**`ClassifyTemplate` asks which method applies**, over a pool of equations, and
**`FaultTemplate` asks what is wrong with an answer somebody arrived at**. Both
produce ordinary `Choice`s, so both are graded, shuffled and recorded by
machinery that already existed.

And every slot-based template can say which of `TIERS` each of its draws
belongs to, so a drill can be made easier or harder without becoming a
different drill.

**A question can be asked about a picture.** `Choice`, `Numeric` and `Solve`
each carry an optional `figure`, a key into the same registry a lesson's own
figure comes from, and it is shown above the prompt. This is the graphical
leg of the rule of four becoming assessable rather than merely illustrative:
until a question could hold a figure, every question here was about a formula
or a number, and reading a phase portrait -- which is most of what the later
units are for -- could be demonstrated to a student and never asked of one.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

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
    "Template",
    "ChoiceTemplate",
    "NumericTemplate",
    "ModelTemplate",
    "ExpressionTemplate",
    "ClassifyTemplate",
    "FaultTemplate",
    "Lesson",
    "Unit",
    "grade_choice",
]

#: How a note is presented. `idea` is the default prose card; `formula` is a
#: result to keep; `pitfall` is the mistake this topic actually produces, boxed
#: so it reads differently from an idea; `aside` is context that can be skipped.
NOTE_KINDS = ("idea", "formula", "pitfall", "aside")

#: How hard a draw is, in order. A template says which of these each of its
#: draws belongs to by carrying a `level`; one that says nothing has every
#: draw in `typical`, which is what every drill was before tiers existed.
#:
#: Three rather than five, and named rather than numbered, because the author
#: of a template has to be able to say honestly which bucket a draw is in. The
#: distinction that survives contact with a real family of equations is
#: coarse: the ones where the method runs straight through, the ones where it
#: is the usual amount of work, and the ones with the complication the topic
#: is really about -- a repeated root, a resonant forcing term, a
#: variable coefficient.
TIERS = ("easier", "typical", "harder")


@dataclass(frozen=True)
class Passage:
    """One step of an argument: what is claimed, and the mathematics of it.

    Deliberately not called `Step`. `steps.Step` is one mechanical move in
    solving a *particular* equation -- "divide by g(y)", with that equation's
    numbers in it. A `Passage` is a move in the argument for why the method is
    legitimate *at all*, and confusing the two is the exact distinction this
    exists to draw. The narrator can already show anyone the steps; what it
    cannot do is say why they are allowed.
    """

    prose: str
    #: Display mathematics for this step, typeset beneath the prose.
    latex: str = ""


@dataclass(frozen=True)
class Note:
    """One idea, with the formula that carries it."""

    heading: str
    #: Prose. Blank lines separate paragraphs, and the renderer honours them --
    #: a card long enough to need two paragraphs and given only one is a wall,
    #: which is the opposite of what a card is for.
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
    #: What to watch for, in prose, beside the generated working. The narrator
    #: supplies the steps and cannot supply the reading of them: which line is
    #: the one that matters, what would have gone wrong a step earlier, what
    #: the answer's shape is telling you. Blank lines separate paragraphs.
    commentary: str = ""


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
    #: The equation the question is about, as it would be *typed*, set in the
    #: monospace the editor uses.
    #:
    #: `latex` and this are not alternatives to each other. A question written
    #: by hand can be typeset, because somebody wrote the LaTeX for it. A
    #: question built out of a template cannot: the equation is assembled from
    #: the draw, and authoring a second LaTeX form of it would be authoring
    #: the same equation twice and waiting for the two to disagree. So a
    #: generated question shows the string it is actually solving.
    shown: str = ""
    #: Where each option came from in the `ChoiceTemplate` that produced this
    #: question: ``origins[position]`` is that option's index *as the template
    #: writes them*, before the per-draw shuffle. Empty for a question written
    #: out by hand, whose positions are already the canonical ones.
    #:
    #: It exists so that a *pick* can be recorded and compared across draws.
    #: The shuffle is what stops a generated question drilling position rather
    #: than content, and it is also what makes "you keep choosing the option
    #: with no arbitrary constant" unsayable from a bare index: position 2 is
    #: a different option every time. This maps the position back to the
    #: option the author wrote, which is stable, and `progress` stores that.
    origins: tuple[int, ...] = ()
    #: A figure to put *above* the prompt, named by key as `Lesson.figure` is.
    #:
    #: The difference between this and the lesson's own figure is what the
    #: picture is for. A lesson's figure illustrates; a question's figure is
    #: the question -- "read the marked point off the b-c plane" cannot be
    #: asked without one, and until a question could carry a picture the
    #: graphical leg of the rule of four was the only one this application
    #: never assessed.
    #:
    #: The same registry and the same widget, so a figure written for a lesson
    #: can be asked about without being written twice, and moving its sliders
    #: while answering is the intended way to answer.
    figure: str = ""

    kind: str = field(default="choice", init=False)

    @property
    def because(self) -> str:
        """The reason the right answer is right."""
        return self.becauses[self.answer]

    def canonical(self, position: int) -> int:
        """The author's index for the option shown at `position`."""
        if 0 <= position < len(self.origins):
            return self.origins[position]
        return position


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
    #: A figure to put *above* the prompt, named by key as `Lesson.figure` is.
    #:
    #: The difference between this and the lesson's own figure is what the
    #: picture is for. A lesson's figure illustrates; a question's figure is
    #: the question -- "read the marked point off the b-c plane" cannot be
    #: asked without one, and until a question could carry a picture the
    #: graphical leg of the rule of four was the only one this application
    #: never assessed.
    #:
    #: The same registry and the same widget, so a figure written for a lesson
    #: can be asked about without being written twice, and moving its sliders
    #: while answering is the intended way to answer.
    figure: str = ""

    kind: str = field(default="solve", init=False)

    @property
    def hint(self) -> str:
        """The first rung, for callers that want one line."""
        return self.hints[0] if self.hints else ""


@dataclass(frozen=True)
class Numeric:
    """Compute it and type the number; graded to a tolerance.

    The one question type in this application that stores its answer, and the
    reason is that there is nothing else to store. A `Solve` keeps only the
    equation because substituting into it *is* the grading; here the equation
    has no closed form, or the thing asked for is a step of a method rather
    than a solution at all, and a number is what there is.

    That makes the tolerance a correctness question rather than a cosmetic one.
    A drill asking for one Runge-Kutta step is asking for the *method's* value,
    which sits a few parts in ten thousand from the exact solution -- so a
    tolerance loose enough to accept the exact answer would mark a student
    right for having done the wrong thing.
    """

    key: str
    prompt: str
    #: The value expected, already evaluated.
    answer: float
    #: How close counts, relative to the size of the answer. Not a display
    #: choice: see the class docstring.
    tolerance: float = 1e-6
    #: Shown after the entry box, and never part of what is typed.
    units: str = ""
    #: Why that is the answer, shown once the attempt is marked. A number with
    #: no account of itself is the least instructive verdict there is.
    because: str = ""
    #: The equation the question is about, if it is about one.
    latex: str = ""
    hints: tuple[str, ...] = ()
    #: A figure to put *above* the prompt, named by key as `Lesson.figure` is.
    #:
    #: The difference between this and the lesson's own figure is what the
    #: picture is for. A lesson's figure illustrates; a question's figure is
    #: the question -- "read the marked point off the b-c plane" cannot be
    #: asked without one, and until a question could carry a picture the
    #: graphical leg of the rule of four was the only one this application
    #: never assessed.
    #:
    #: The same registry and the same widget, so a figure written for a lesson
    #: can be asked about without being written twice, and moving its sliders
    #: while answering is the intended way to answer.
    figure: str = ""
    #: Wrong numbers with a known cause, as ``(value, cause)``. A typed
    #: number that lands on one is told the cause instead of only "not
    #: quite" -- see `NumericTemplate.mistakes`.
    mistakes: tuple[tuple[float, str], ...] = ()

    kind: str = field(default="numeric", init=False)

    @property
    def hint(self) -> str:
        return self.hints[0] if self.hints else ""


@dataclass(frozen=True)
class Model:
    """Write the equation. Graded by equivalence, not by substitution.

    The one thing every other question type here has in common is that the
    equation is given and something else is asked for. These are the questions
    where the equation *is* the answer, and they come from both ends of the
    course:

    * *A tank holds 100 litres of brine and 5 litres a minute flow in at
      0.4 kg/l...* -- the modelling question a first course opens with, and
      the half of an applied problem a technique drill never touches.
    * *Every curve in the family ``y = C e^{3t}`` solves one first-order
      equation. Write it.* -- the same question asked backwards, which is
      how a course checks that somebody knows what a differential equation
      says rather than only how to unwind one.

    Both store the equation, because there is nothing to substitute a
    situation into. What keeps that from being an answer key is
    `symbolic.check_model`: two equations are the same when their sides agree
    up to a nonzero constant multiple, so ``y' = 2 - y/20``, ``y' + y/20 = 2``
    and ``20y' + y = 40`` are one answer and none of them is marked wrong for
    being arranged differently.
    """

    key: str
    prompt: str
    #: The equation expected, as it would be typed into the editor.
    equation: str
    #: Why that is the equation, term by term, shown once the attempt is
    #: marked. A model with no account of where each term came from is a
    #: formula to memorise.
    because: str = ""
    #: The situation's data, typeset above the box, where it is worth seeing
    #: as mathematics rather than as prose.
    latex: str = ""
    hints: tuple[str, ...] = ()

    kind: str = field(default="model", init=False)

    @property
    def hint(self) -> str:
        return self.hints[0] if self.hints else ""


@dataclass(frozen=True)
class Expression:
    """Write one move of the method: the object it produces, not the answer.

    The integrating factor, the characteristic polynomial, the Wronskian, the
    transform of the forcing term. A course asks for each of these on its own,
    and none of them is a solution -- so `check_answer` has nothing to
    substitute them into, and a drill that only ever asks for the final answer
    never finds out which move somebody cannot make.

    This is the closest thing here to *do the next step*, and what makes it
    gradeable is `symbolic.check_expression`, which compares two expressions
    rather than two strings.

    `up_to_constant` is mathematics rather than leniency. An integrating
    factor is determined only up to a constant multiple, and so is a
    characteristic equation; where that is true this says so, and where it is
    not -- a Wronskian, a transform -- it stays off and a multiple is a
    different answer.
    """

    key: str
    prompt: str
    #: The expression expected, as it would be typed. Left as text rather than
    #: evaluated, because it is symbolic: ``exp(3*t)``, ``r**2 + 3*r + 2``.
    answer: str
    #: Whether any nonzero constant multiple of it is also right.
    up_to_constant: bool = False
    #: Why that is what the step produces, shown once the attempt is marked.
    because: str = ""
    #: The equation the step is being taken on.
    latex: str = ""
    hints: tuple[str, ...] = ()

    kind: str = field(default="expression", init=False)

    @property
    def hint(self) -> str:
        return self.hints[0] if self.hints else ""


@dataclass(frozen=True)
class Case:
    """One equation in a *which method* drill, and what gives it away."""

    #: As it would be typed.
    equation: str
    #: What it is: a key into the vocabulary its template names. For methods
    #: that is the sympy spelling `steps.TECHNIQUES` uses, for portraits the
    #: string `analysis.classify` returns.
    #:
    #: The tests put every case through the routine that owns its vocabulary
    #: and require it to agree, so a case cannot quietly claim the wrong
    #: answer -- and cannot keep claiming the right one after the application
    #: changes its mind.
    technique: str
    #: What in the equation decides it. This is the whole content of the
    #: question: "the y-terms come apart from the t-terms" is the reading that
    #: has to become automatic, and naming the method without it is a label.
    why: str
    #: Typeset above the options, where the equation is worth seeing set.
    latex: str = ""
    #: One of `TIERS`.
    tier: str = "typical"


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
    #: Which tier a draw belongs to, as a predicate over the drawn values, or
    #: None where the family has no honest spread. One of `TIERS`.
    level: Callable[[Mapping[str, object]], str] | None = None
    #: The technique the generated question must be narrated by. Asserted in
    #: the tests, so a template that quietly starts producing something else is
    #: a failure rather than a surprise.
    technique: str = ""
    #: Which narrator works it: "steps" or "laplace".
    narrator: str = "steps"

    kind: str = field(default="template", init=False)


@dataclass(frozen=True)
class ChoiceTemplate:
    """A multiple-choice question with its numbers left open.

    What `Template` is to `Solve`, this is to `Choice` -- and it exists for the
    lessons a substitution check cannot reach. `check_answer` grades by putting
    an answer into its equation and simplifying, which cannot decide a switched
    or impulsive answer, has nothing to substitute for Euler's method, and
    marks a truncated series wrong. Those lessons were left without a drill
    entirely; what they needed was a question type graded some other way, and
    `grade_choice` is that way.

    The options are format strings like everything else, and they are
    **shuffled per draw** -- see `generate.draw_choice`. A generated
    multiple-choice question whose answer sat at a fixed index would drill
    position rather than content, which is the one thing it must not do.
    """

    key: str
    #: What this drill is, in the header.
    title: str
    #: A format string over the slot names, as for `Template`.
    prompt: str
    options: tuple[str, ...]
    #: Index into `options` **as written here**, before the per-draw shuffle.
    answer: int
    #: One per option, in the same order, and shuffled along with them.
    becauses: tuple[str, ...]
    #: The equation the question is about, if it is about one.
    latex: str = ""
    slots: tuple[tuple[str, tuple], ...] = ()
    reject: Callable[[Mapping[str, object]], bool] | None = None

    #: Which tier a draw belongs to, as a predicate over the drawn
    #: values, or None where the family has no honest spread.
    level: Callable[[Mapping[str, object]], str] | None = None

    kind: str = field(default="choice-template", init=False)


@dataclass(frozen=True)
class NumericTemplate:
    """A `Numeric` question with its numbers left open.

    The third of the template types, and the one that reaches the lessons the
    other two could not. `Template` needs a closed form to substitute into, and
    Euler's method has none. `ChoiceTemplate` needs a handful of plausible
    options, and "what is y after one step" has no natural four -- offering
    them would either give the answer away or invent distractors nobody would
    have written down.

    `answer` is a **format string that is an expression**, not a callable, so a
    lesson module stays data that can be read: ``"{y0} + {h}*({a}*{y0})"`` is
    an Euler step written out. `generate.draw_numeric` formats and evaluates
    it.

    That declarative form is what makes the drill checkable against the rest of
    the application. A stored number could quietly disagree with the tool the
    lesson teaches; an expression can be evaluated in a test beside
    `byhand.walk`, `analysis.phase_line` or the library's own solver, and
    `tests/test_templates.py` does exactly that for every draw. It is the
    property `Template` gets for free from substitution, bought back.
    """

    key: str
    title: str
    #: A format string over the slot names, as for `Template`.
    prompt: str
    #: An expression over the slot names, evaluated once the slots are filled.
    answer: str
    tolerance: float = 1e-6
    units: str = ""
    because: str = ""
    latex: str = ""
    hints: tuple[str, ...] = ()
    slots: tuple[tuple[str, tuple], ...] = ()
    reject: Callable[[Mapping[str, object]], bool] | None = None

    #: Which tier a draw belongs to, as a predicate over the drawn
    #: values, or None where the family has no honest spread.
    level: Callable[[Mapping[str, object]], str] | None = None
    #: The wrong answers worth recognising, as ``(expression, cause)``, the
    #: expression over the slots like `answer`.
    #:
    #: A wrong formula already gets a diagnosis -- `Fault` names it, and the
    #: residual shows it. A wrong *number* got "not quite", which is the least
    #: a verdict can say. But the usual wrong numbers are computable: an Euler
    #: step answered with a backward-Euler step, the Jacobian taken at the
    #: origin instead of the equilibrium, r² given for r. Each is an
    #: expression here, evaluated per draw, so the diagnosis is exact rather
    #: than guessed -- and a draw where a mistake happens to coincide with the
    #: right answer drops that mistake, so a right answer is never "diagnosed".
    mistakes: tuple[tuple[str, str], ...] = ()

    kind: str = field(default="numeric-template", init=False)


@dataclass(frozen=True)
class ModelTemplate:
    """A `Model` question with its numbers left open.

    What `Template` is to `Solve`. The situation keeps its shape and its
    quantities change, which is the right thing to vary here: a modelling
    question is hard because of the translation, and the translation is the
    same whether the tank holds 100 litres or 250.
    """

    key: str
    title: str
    #: All four are format strings over the slot names.
    prompt: str
    equation: str
    because: str = ""
    latex: str = ""
    hints: tuple[str, ...] = ()
    slots: tuple[tuple[str, tuple], ...] = ()
    reject: Callable[[Mapping[str, object]], bool] | None = None
    level: Callable[[Mapping[str, object]], str] | None = None

    kind: str = field(default="model-template", init=False)


@dataclass(frozen=True)
class ExpressionTemplate:
    """An `Expression` question with its numbers left open."""

    key: str
    title: str
    #: A format string over the slot names.
    prompt: str
    #: The expected expression, as a format string over the slots. An
    #: expression rather than a stored value, for the reason
    #: `NumericTemplate.answer` is one: it can be checked against the rest of
    #: the application draw by draw, and `tests/test_templates.py` does --
    #: every integrating factor is differentiated back, every characteristic
    #: polynomial is compared with the roots the narrator finds.
    answer: str
    up_to_constant: bool = False
    because: str = ""
    latex: str = ""
    hints: tuple[str, ...] = ()
    slots: tuple[tuple[str, tuple], ...] = ()
    reject: Callable[[Mapping[str, object]], bool] | None = None
    level: Callable[[Mapping[str, object]], str] | None = None

    kind: str = field(default="expression-template", init=False)


@dataclass(frozen=True)
class ClassifyTemplate:
    """*Which method would you use?* -- over a pool of equations.

    The question a course examines and a lesson cannot ask. Every drill in
    this application until now sat inside a lesson that had just named its
    technique, so the answer to "which method" was always "the one on this
    page". Choosing between them is a separate skill, it is most of what an
    exam actually tests, and nothing here practised it.

    A pool of `Case`s rather than slots to substitute: what varies is the
    equation, and the equations have to be real ones. The options are the
    method names and they are shuffled per draw, so the drill cannot be
    answered by position.

    The key is not stored twice. Each case names its technique, and the tests
    put the equation through `classify_ode` and `steps.preferred_hint` -- the
    same route the narrator takes -- and require the answer to be what the
    application would actually do with it. A case whose method changed under a
    sympy upgrade becomes a failing test rather than a question that marks the
    right answer wrong.
    """

    key: str
    title: str
    prompt: str
    cases: tuple[Case, ...]
    #: The menu offered, as keys into the table below, in teaching order.
    #: Every case's label must be in it; the labels nobody's case uses are the
    #: distractors.
    options: tuple[str, ...]
    #: Which vocabulary the labels come from: a key of
    #: `vocabulary.VOCABULARIES`.
    #:
    #: Three of them, because *which method solves this* is one instance of a
    #: question the course asks in several places, and all of them share the
    #: shape: here is an object, name what it is, and be able to say why it is
    #: not the other three. The portrait of a linear system and the damping
    #: regime of a spring are the same question about different nouns — and
    #: each vocabulary has a routine in this application that decides the
    #: answer, which is what keeps the drill honest.
    table: str = "methods"

    kind: str = field(default="classify-template", init=False)


@dataclass(frozen=True)
class FaultTemplate:
    """*What went wrong here?* -- an answer with one named mistake in it.

    Spotting a fault is a different skill from not making one, and it is the
    one that transfers to checking your own work. The question shows an
    equation and an answer somebody arrived at, and asks what is wrong with
    it.

    **The wrong answer is generated, and it is really wrong.** `wrong` is an
    expression over the slots, like `NumericTemplate.answer`, so
    `tests/test_templates.py` can put every draw through `check_answer` and
    require the verdict the fault claims: an answer with a sign error does not
    satisfy the equation, and an answer that dropped the constant of
    integration satisfies the equation but not the initial condition. A
    "wrong" answer that turned out to be right would be the worst question in
    the application, and it cannot get here.

    Corrupting the *narrator's working* was the other way to build this, and
    it is not what happens: a derivation's steps are LaTeX, and editing that
    text can neither be verified nor be trusted to leave the mathematics wrong
    rather than merely ugly. What is checkable is the answer, so that is what
    carries the fault.
    """

    key: str
    title: str
    #: Format strings over the slots.
    prompt: str
    equation: str
    #: The answer somebody arrived at, as a format string over the slots, in
    #: the form it would be typed.
    wrong: str
    #: The fault in it: a key into `methods.FAULTS`.
    fault: str
    #: The other diagnoses offered, same keys. Shuffled in with the true one.
    others: tuple[str, ...]
    conditions: str = ""
    slots: tuple[tuple[str, tuple], ...] = ()
    reject: Callable[[Mapping[str, object]], bool] | None = None
    level: Callable[[Mapping[str, object]], str] | None = None

    kind: str = field(default="fault-template", init=False)


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
    #: Why this topic exists, before any technique is named. Where the equation
    #: arises, what goes wrong with the tools already in hand, and why this
    #: method is the natural response to that. Blank lines separate paragraphs.
    #:
    #: A lesson that opens with "here is a technique" has skipped the only part
    #: a reader cannot reconstruct for themselves.
    motivation: str = ""
    #: The argument for why the method works, as an ordered sequence. Distinct
    #: from `examples`, which show the narrator doing it to one equation: this
    #: is the general case, and it is where the step everybody waves at gets
    #: made explicit.
    derivation: tuple[Passage, ...] = ()
    #: Worked through by the narrator, in the order they should be read.
    examples: tuple[Example, ...] = ()
    #: Practice that never runs out, and every lesson has some. It did not
    #: always: Euler and RK4 have no closed form to substitute into, so a
    #: `Solve` drill there could never say "right", and those lessons went
    #: without rather than be given a verdict that meant nothing. What was
    #: missing was a question graded another way, which is what
    #: `ChoiceTemplate` and `NumericTemplate` are.
    templates: tuple[
        Template | ChoiceTemplate | NumericTemplate | ModelTemplate
        | ExpressionTemplate | ClassifyTemplate | FaultTemplate, ...
    ] = ()
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
    #: The catalogue system the Phase Portrait opens on, for a lesson whose
    #: `tool` is "portrait". A key rather than an equation: the portrait is
    #: driven by the catalogue, and a nonlinear system is the one thing a
    #: lesson's worked examples cannot carry, since no narrator solves one.
    portrait: str = ""
    #: The lesson written as a textbook section -- see `lessons.chapter`.
    #: When present it *is* the Learn page, and `motivation`, `derivation`
    #: and the notes are what it was written from; the formula notes still
    #: close the page as a summary, and still make the formula sheet.
    chapter: tuple = ()

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
