"""The course's vocabulary, each term tied to where it is taught.

A term used in six lessons is defined in one, and a reader who meets it in
the fifth has no way back to the first. This is that way back: a short
definition, the lesson that defines it, and -- **computed, never written
down** -- every other lesson that uses it.

Two rules keep it honest, and `tests/test_glossary.py` holds both:

* The lesson named as defining a term must actually contain the term. A
  glossary that pointed to a lesson where the word never appears would be a
  link to nowhere.
* "Used in" is found by searching the lessons' own text. A hand-kept list
  would be out of date the first time a lesson was edited; a search cannot
  be.

Content only, like the rest of this package.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = ["Term", "TERMS", "text_of", "uses", "search", "chapter_prose",
           "link_terms", "term_of", "SCHEME"]


@dataclass(frozen=True)
class Term:
    name: str
    #: One or two sentences. The lesson says the rest.
    definition: str
    #: The lesson key where it is taught.
    lesson: str
    #: Other spellings found in the lessons -- "equilibria" for "equilibrium".
    also: tuple[str, ...] = ()
    #: Phrases in which the word is ordinary English rather than the term:
    #: "in a different order" is not the order of an equation, and the centre
    #: of a disc is not an equilibrium. A use inside one of these is neither
    #: linked nor counted as "used in". Found by reading every first use in
    #: the chapters, which is how `tests/test_glossary.py` keeps it honest.
    not_in: tuple[str, ...] = ()
    #: Lessons where the word always means something else, so that no phrase
    #: list could be complete: in the series unit "centre" is the point a
    #: power series is expanded about, on every page.
    not_lessons: tuple[str, ...] = ()
    #: Whether a lesson's prose may link the word here. "order" may not: the
    #: numerical-methods unit uses it as the order of *accuracy* ("Euler's
    #: method is first order"), written exactly as the order of an equation
    #: is, and no list of phrases separates the two. A link that is wrong
    #: half the time is worse than none.
    linkable: bool = True

    @property
    def spellings(self) -> tuple[str, ...]:
        return (self.name,) + self.also


TERMS: tuple[Term, ...] = (
    Term("order", "The highest derivative that appears. An equation of order "
         "n needs n conditions to pick out one solution.", "basics",
         not_in=("in order", "different order", "either order", "same order",
                 "order matters", "order of events", "windows of order",
                 "exponential order"),
         linkable=False),
    Term("initial value problem", "An equation together with the value of "
         "the solution (and of enough derivatives) at one instant.",
         "basics", ("initial condition",)),
    Term("slope field", "Short segments drawn at a grid of points with the "
         "slope the equation assigns there. Solutions run tangent to them.",
         "slopefields", ("slope fields", "direction field")),
    Term("separable", "An equation y' = f(t)g(y), whose variables can be "
         "moved to opposite sides and integrated separately.", "separable"),
    Term("integrating factor", "The multiplier μ(t) = e^(∫p dt) that turns "
         "y' + p y into the derivative of μy.", "linear"),
    Term("exact equation", "M + N y' = 0 with ∂M/∂y = ∂N/∂t: the left side "
         "is already the derivative of some F(t, y).", "exact",
         ("exact",)),
    Term("Bernoulli equation", "y' + p y = q yⁿ, made linear by the "
         "substitution v = y^(1−n).", "substitutions", ("Bernoulli",)),
    Term("equilibrium", "A constant solution: a value, or point, where every "
         "rate is zero.", "equilibria", ("equilibria",)),
    Term("phase line", "The y-axis marked with the equilibria of y' = f(y) and "
         "arrows showing which way y moves between them.", "equilibria"),
    Term("Euler's method", "Follow the slope at the current point for one "
         "step h: y_(n+1) = y_n + h f(t_n, y_n).", "numerical"),
    Term("Runge–Kutta", "A step built from several slope samples inside the "
         "step, weighted so errors cancel. RK4 is fourth order.",
         "rungekutta", ("RK4", "Runge-Kutta")),
    Term("superposition", "For a linear homogeneous equation, any combination "
         "of solutions is a solution.", "superposition"),
    Term("Wronskian", "The determinant y₁y₂' − y₁'y₂. Nonzero means the two "
         "solutions are independent.", "superposition"),
    Term("characteristic equation", "The polynomial in r found by trying "
         "y = e^(rt) in a constant-coefficient equation.", "roots",
         ("characteristic polynomial", "characteristic roots")),
    Term("undetermined coefficients", "Guessing the form of a particular "
         "solution from the forcing term and solving for its constants.",
         "undetermined"),
    Term("variation of parameters", "A particular solution built by letting "
         "the constants of the homogeneous solution vary with t.",
         "variation"),
    Term("reduction of order", "From one known solution y₁, a second one "
         "y₂ = v·y₁ found by solving a first-order equation for v'.",
         "reduction-of-order"),
    Term("Cauchy–Euler equation", "t²y'' + a t y' + b y = 0, solved by "
         "trying y = t^r.", "cauchy", ("Cauchy-Euler",)),
    Term("damping", "A force opposing velocity. Its size against 2√(mk) "
         "decides whether a vibration oscillates.", "free-vibration",
         ("damped", "underdamped", "overdamped", "critically damped")),
    Term("resonance", "Forcing at the natural frequency of an undamped "
         "system, which makes the amplitude grow without bound.",
         "forced-vibration"),
    Term("Laplace transform", "F(s) = ∫₀^∞ e^(−st) f(t) dt, which turns "
         "differentiation into multiplication by s.", "transform"),
    Term("unit step", "u(t − a): zero before a and one after. Forcing "
         "switched on partway through.", "step-forcing",
         ("Heaviside", "step function")),
    Term("convolution", "(f * g)(t) = ∫₀^t f(τ)g(t − τ) dτ, whose transform "
         "is the product of the transforms.", "convolution"),
    Term("delta function", "An impulse of unit total size delivered at one "
         "instant; its transform is e^(−as).", "impulses",
         ("impulse", "Dirac")),
    Term("eigenvalue", "A number λ with A v = λ v for some nonzero v. The "
         "eigenvalues of A decide how x' = Ax behaves.", "eigenvalues",
         ("eigenvalues", "eigenvector", "eigenvectors")),
    Term("phase portrait", "Trajectories of a two-dimensional system drawn "
         "in the plane of its two unknowns.", "phase-portraits",
         ("phase plane",)),
    Term("saddle", "An equilibrium with one direction in and one out: real "
         "eigenvalues of opposite sign.", "phase-portraits"),
    Term("spiral", "An equilibrium trajectories wind round, in or out: "
         "complex eigenvalues.", "phase-portraits"),
    Term("centre", "An equilibrium surrounded by closed orbits. Linearly, a "
         "purely imaginary pair of eigenvalues.", "phase-portraits",
         ("center",),
         # A disc's centre and the Earth's; a power series' centre is the
         # series unit's own meaning of the word.
         not_in=("from the centre", "at the centre", "centre of the disc"),
         not_lessons=("power-series", "recurrence", "frobenius")),
    Term("Jacobian", "The matrix of first partial derivatives of the "
         "right-hand sides, evaluated at an equilibrium.",
         "nonlinear-equilibria"),
    Term("linearisation", "The linear system u' = J u that approximates a "
         "nonlinear one near an equilibrium.", "nonlinear-equilibria",
         ("linearise", "linearising", "linearization")),
    Term("hyperbolic", "An equilibrium whose Jacobian has no eigenvalue with "
         "zero real part; there the linearisation tells the truth.",
         "almost-linear",
         not_in=("hyperbolic function", "hyperbolic tangent",
                 "hyperbolic versions", "hyperbolic cosine",
                 "hyperbolic sine")),
    Term("Hartman–Grobman", "Near a hyperbolic equilibrium the nonlinear flow "
         "has the type and stability of its linearisation.",
         "almost-linear", ("Hartman-Grobman",)),
    Term("nullcline", "A curve on which one of the rates is zero. Equilibria "
         "are where nullclines of different variables cross.",
         "ecological-models", ("nullclines",)),
    Term("separatrix", "The orbit through a saddle that divides regions of "
         "different behaviour, such as swinging from rotating.",
         "nonlinear-mechanics", ("separatrices",)),
    Term("conserved quantity", "A function of the state that stays constant "
         "along every solution, such as the energy of a frictionless "
         "system.", "nonlinear-mechanics", ("conserved",)),
    Term("limit cycle", "An isolated closed orbit, approached (or left) by "
         "the trajectories near it.", "limit-cycles", ("limit cycles",)),
    Term("Poincaré–Bendixson", "A bounded planar trajectory approaches an "
         "equilibrium, a closed orbit or a cycle of equilibria — so the "
         "plane has no chaos.", "limit-cycles", ("Poincare-Bendixson",)),
    Term("bifurcation", "A parameter value where the qualitative picture "
         "changes: equilibria appear, vanish or change stability.",
         "bifurcations-chaos", ("bifurcations",)),
    Term("Hopf bifurcation", "A complex pair of eigenvalues crossing the "
         "imaginary axis, where a limit cycle is born.",
         "bifurcations-chaos", ("Hopf",)),
    Term("Lyapunov exponent", "The rate at which neighbouring trajectories "
         "separate. Positive means chaos.", "bifurcations-chaos",
         ("Lyapunov",)),
    Term("power series solution", "A solution written as Σ cₙ tⁿ, with the "
         "coefficients found from a recurrence.", "power-series",
         ("power series",)),
    Term("recurrence relation", "The rule giving each series coefficient "
         "from earlier ones.", "recurrence", ("recurrence",)),
    Term("regular singular point", "A point where the equation's "
         "coefficients blow up mildly enough for a Frobenius series.",
         "frobenius", ("regular singular",)),
    Term("indicial equation", "The equation for the leading power r of a "
         "Frobenius series.", "frobenius", ("indicial",)),
)


def text_of(lesson) -> str:
    """Everything a reader sees on a lesson's Learn and Examples pages.

    The chapter included. It is most of the Learn page now, and leaving it
    out made "used in" a search of the summary cards: a term a chapter used
    on every page was reported as used nowhere.
    """
    parts = [lesson.title, lesson.summary, lesson.motivation]
    parts += [passage.prose for passage in lesson.derivation]
    parts += [f"{note.heading} {note.body}" for note in lesson.notes]
    parts += [f"{example.why} {example.commentary}" for example in lesson.examples]
    parts += list(chapter_prose(getattr(lesson, "chapter", ())))
    return "\n".join(parts)


def chapter_prose(sections):
    """The words of a chapter, block by block, as `chapter.words` counts them."""
    from .chapter import blocks_of

    for section in sections:
        yield section.title
    for block in blocks_of(sections):
        if block.kind == "para":
            yield block.text
        elif block.kind == "box":
            yield f"{block.title} {block.body}"
        elif block.kind == "worked":
            yield " ".join([block.title, block.problem]
                           + [step.prose for step in block.steps])
        elif block.kind in ("plot", "figure"):
            yield block.caption


def _pattern(term: Term) -> re.Pattern:
    words = "|".join(re.escape(spelling) for spelling in term.spellings)
    return re.compile(rf"(?<![\w-])(?:{words})(?![\w])", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Terms as links, where a lesson uses them
# ---------------------------------------------------------------------------

#: Every spelling of every term, longest first, so that at any position the
#: longest name wins: "initial value problem" rather than a shorter term
#: inside it, "exact equation" rather than "exact".
_SPELLINGS = sorted(
    ((spelling, index) for index, term in enumerate(TERMS)
     for spelling in term.spellings),
    key=lambda pair: -len(pair[0]),
)
_ANY_TERM = re.compile(
    r"(?<![\w-])(" + "|".join(re.escape(s) for s, _ in _SPELLINGS) + r")(?![\w])",
    re.IGNORECASE,
)
_BY_SPELLING = {spelling.lower(): index for spelling, index in _SPELLINGS}

#: Markup and character entities: never linked inside, never split.
_MARKUP = re.compile(r"(<[^>]*>|&[#\w]+;)")

#: The prefix a term link's href carries, followed by the term's index.
SCHEME = "term:"


def term_of(href: str) -> Term | None:
    """The term a link made by `link_terms` points to, or None."""
    if not href.startswith(SCHEME):
        return None
    try:
        return TERMS[int(href[len(SCHEME):])]
    except (ValueError, IndexError):
        return None


def link_terms(html: str, lesson_key: str, linked: set[int],
               colour: str = "") -> str:
    """`html` with the first use of each glossary term made a link.

    *First* per lesson, not per paragraph: `linked` is shared across a whole
    page and grows as terms are linked, so a word used forty times is one
    link, where the reader first meets it. A term this very lesson teaches is
    never linked -- the reader is in the middle of its definition.

    Only text is touched. The input is already rich text (escaped, with
    emphasis and superscripts), so tags and entities are stepped over whole,
    and a term inside a link is left alone. The link keeps its underline, so
    it is not marked by colour alone.
    """
    pieces = _MARKUP.split(html)
    inside_link = False
    for position, piece in enumerate(pieces):
        if position % 2:                                   # markup
            lowered = piece.lower()
            if lowered.startswith("<a ") or lowered == "<a>":
                inside_link = True
            elif lowered == "</a>":
                inside_link = False
            continue
        if inside_link or not piece:
            continue

        def replace(match: re.Match, piece=piece) -> str:
            index = _BY_SPELLING[match.group(1).lower()]
            term = TERMS[index]
            if (index in linked or term.lesson == lesson_key
                    or not term.linkable or lesson_key in term.not_lessons
                    or _ordinary(term, piece, match.start(), match.end())):
                return match.group(0)
            linked.add(index)
            style = f' style="color:{colour};"' if colour else ""
            return f'<a href="{SCHEME}{index}"{style}>{match.group(0)}</a>'

        pieces[position] = _ANY_TERM.sub(replace, piece)
    return "".join(pieces)


def _ordinary(term: Term, text: str, start: int, end: int) -> bool:
    """Whether the word at `text[start:end]` sits inside one of `term.not_in`
    -- ordinary English, not the term."""
    lowered = text.lower()
    for phrase in term.not_in:
        phrase = phrase.lower()
        at = lowered.find(phrase, max(0, start - len(phrase)))
        while at != -1 and at <= start:
            if at + len(phrase) >= end:
                return True
            at = lowered.find(phrase, at + 1)
    return False


def uses(term: Term, lessons) -> tuple:
    """The lessons whose text mentions `term`, in course order."""
    pattern = _pattern(term)

    def mentions(text: str) -> bool:
        return any(not _ordinary(term, text, m.start(), m.end())
                   for m in pattern.finditer(text))

    return tuple(lesson for lesson in lessons
                 if lesson.key not in term.not_lessons
                 and mentions(text_of(lesson)))


def search(query: str, terms: tuple[Term, ...] = TERMS) -> tuple[Term, ...]:
    """Terms whose name, spellings or definition contain `query`."""
    wanted = query.strip().lower()
    if not wanted:
        return terms
    by_name = [t for t in terms
               if any(wanted in spelling.lower() for spelling in t.spellings)]
    by_meaning = [t for t in terms if t not in by_name
                  and wanted in t.definition.lower()]
    return tuple(by_name + by_meaning)
