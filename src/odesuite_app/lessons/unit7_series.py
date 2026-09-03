"""Unit 7 -- Series solutions.

Edwards, Penney and Calvis 6e, chapter 8. What to do when there is no closed
form at all, which is the ordinary case rather than the exceptional one: build
the answer coefficient by coefficient and stop when you have enough.

**Every Solve question here has an answer that terminates**, and the reason is
measured rather than stylistic. `check_answer` grades by substituting and
simplifying to zero, and a truncated series leaves the truncation error behind
-- ``C1(1 - t^2/2 + t^4/24) + C2(t - t^3/6)`` into ``y'' + y`` leaves
``t^3(C1 t - 4 C2)/24``, which is the correct residual and not a mistake. A
question whose model answer the grader marks wrong would be worse than no
question, so the practice uses Legendre's and Hermite's equations at the
parameters where the series stops, with conditions that kill the branch that
does not. Those answers are exact polynomials and the grader accepts them.

That is not a workaround. Terminating series *are* the classical polynomials,
and they are what a course does with this chapter anyway. What the substitution
check cannot reach -- is this point ordinary, how far does the series converge,
what are the indicial roots -- is asked as multiple choice, which is also how a
course asks it.

The drills are **generated multiple choice** rather than generated `Solve`s,
for the same reason. A `Solve` drill would have to draw from the terminating
parameters only, and there are few enough of those that the practice already
covers them. What a course actually asks here is classification -- is this
point ordinary, how far does the series reach, what are the indicial roots --
and `ChoiceTemplate` drills exactly that, graded by `grade_choice` rather than
by substitution.

The Frobenius lesson is worked by the Cauchy-Euler narrator rather than the
series one, and that is not a compromise. At a regular singular point
`series.derive` classifies the point, forms the indicial equation and stops --
the Frobenius series themselves are past what this application narrates -- so
it has no answer to show, and a worked example with no answer is one the reader
is invited to fail at. The equation the lesson is really about is a
Cauchy-Euler equation, whose indicial equation is the object Frobenius
generalises, and that one can be worked end to end.
"""

from __future__ import annotations

from .model import (
    Choice,
    ChoiceTemplate,
    Example,
    Lesson,
    Note,
    Solve,
)

__all__ = ["POWERSERIES", "RECURRENCE", "FROBENIUS", "LESSONS"]


POWERSERIES = Lesson(
    key="power-series",
    title="Power series and ordinary points",
    summary="What to do when there is no closed form — which is most of the "
            "time.",
    tool="steps",
    reference="Edwards 8.1",
    prerequisites=("roots",),
    objectives=(
        "Say what an ordinary point is, and test whether one is.",
        "Assume a power series and substitute it into the equation.",
        "Explain why a0 and a1 are the two arbitrary constants.",
        "Say what it means for an answer to be correct through a given power.",
    ),
    examples=(
        Example(
            equation="(1-t**2)*y'' - 2*t*y' + 6*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            narrator="series",
            why="Legendre's equation at n = 2. The even branch stops at t², so "
                "the conditions given pick out the exact polynomial 1 − 3t² — "
                "a series solution that happens to be finite.",
        ),
        Example(
            equation="y'' - 2*t*y' + 4*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            narrator="series",
            why="Hermite's equation at n = 2, giving 1 − 2t². The same "
                "phenomenon from a different family, and worth comparing: the "
                "recurrences differ but both terminate.",
        ),
    ),
    notes=(
        Note(
            "Most equations have no closed form",
            "y'' = t·y is the standard example. It is linear, it has constant "
            "nothing, and no combination of exponentials, sines or "
            "logarithms solves it. This is not an unlucky equation — it is "
            "Airy's, it describes light near a caustic, and closed forms are "
            "the exception rather than the rule.",
            r"y'' = t\,y",
        ),
        Note(
            "So build the answer instead",
            "Assume the solution is a power series and find its coefficients "
            "one at a time. The method does not need to know what function it "
            "is producing, which is exactly why it works where naming the "
            "answer fails.",
            r"y = \sum_{n=0}^{\infty} a_n t^{n}",
            "formula",
        ),
        Note(
            "Ordinary points are where this is guaranteed",
            "Write the equation as P y'' + Q y' + R y = 0. If P(t₀) ≠ 0 the "
            "point is ordinary, and the theorem promises two independent "
            "solutions analytic there. Where P vanishes, all bets are off "
            "until you check further.",
            r"P(t_0) \neq 0",
            "formula",
        ),
        Note(
            "a₀ and a₁ are the initial conditions",
            "They are never determined by the recurrence — they are the two "
            "arbitrary constants, and they are exactly y(0) and y′(0). No "
            "system to solve at the end, which is a genuine convenience this "
            "method has and the others do not.",
            r"a_0 = y(0), \qquad a_1 = y'(0)",
            "idea",
        ),
        Note(
            "A truncation is not a wrong answer",
            "Substituting a truncated series back does not give zero — it "
            "gives the terms that were never written down. That residual is "
            "the truncation error, and expecting it to vanish is expecting "
            "the series to be finite. What is claimed is correctness up to a "
            "given power, and that is what can be checked.",
            r"y'' + y \;\longrightarrow\; O(t^{N})",
            "pitfall",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="For (1 − t²)y'' − 2ty' + 6y = 0, is t = 0 an ordinary "
                   "point?",
            options=(
                "Yes: P(0) = 1 ≠ 0",
                "No: the equation is not constant-coefficient",
                "No: there is a t² in it",
                "Only if y(0) is given",
            ),
            answer=0,
            becauses=(
                "The leading coefficient is 1 − t², which is 1 at the origin. "
                "That is the whole test, and it is why a series about 0 is "
                "guaranteed to exist here.",
                "Constant coefficients are not required — if they held there "
                "would be a closed form and no need for a series at all.",
                "Where the t² appears matters, not whether it appears. It is "
                "in the leading coefficient, and it makes t = ±1 singular "
                "while leaving 0 ordinary.",
                "Whether a point is ordinary is a property of the equation. "
                "Conditions pick a solution; they do not change where one "
                "exists.",
            ),
        ),
        Choice(
            key="q2",
            prompt="In y = Σ aₙtⁿ, which coefficients stay arbitrary?",
            options=("None", "a₀ only", "a₀ and a₁", "All of them"),
            answer=2,
            becauses=(
                "Two must stay free — a second-order equation has a "
                "two-parameter family of solutions, and the series has to be "
                "able to express all of them.",
                "One would give a one-parameter family, which is not enough "
                "to meet an arbitrary pair of initial conditions.",
                "The recurrence determines a₂ onwards from these two, and "
                "they are y(0) and y′(0). Exactly two, matching the order of "
                "the equation.",
                "Then the equation would say nothing at all. The recurrence "
                "pins every coefficient from a₂ on.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Why does substituting a truncated series not give zero?",
            options=(
                "The series is wrong",
                "The terms beyond the truncation are missing",
                "Power series never solve equations exactly",
                "The recurrence was misapplied",
            ),
            answer=1,
            becauses=(
                "It is right as far as it goes. Every coefficient written "
                "down satisfies the recurrence.",
                "The residual is exactly the contribution of the terms that "
                "were dropped. It is the truncation error, and it is what a "
                "correct partial answer must leave.",
                "They can solve them exactly — when the series terminates, or "
                "when it sums to a familiar function, as the series for "
                "y'' + y = 0 sums to sine and cosine.",
                "Misapplying it would leave a residual at a *low* power. The "
                "truncation error only appears at high ones, which is how the "
                "two are told apart.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Legendre at n = 2. The series terminates.",
            equation="(1-t**2)*y'' - 2*t*y' + 6*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            hints=(
                "P(0) = 1, so t = 0 is ordinary and a power series is "
                "guaranteed to work.",
                "Substitute y = Σ aₙtⁿ and match the coefficient of each "
                "power; the recurrence relates aₙ₊₂ to aₙ.",
                "With y′(0) = 0 the odd coefficients all vanish, and the even "
                "ones stop after a₂ — leaving the polynomial 1 − 3t².",
            ),
        ),
        Solve(
            key="q5",
            prompt="Hermite at n = 2, from the same starting values.",
            equation="y'' - 2*t*y' + 4*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            hints=(
                "The leading coefficient is 1, so every point is ordinary and "
                "the series converges everywhere.",
                "Matching coefficients gives aₙ₊₂ in terms of aₙ, with a "
                "factor that hits zero when n reaches 2.",
                "That zero is what makes it stop: the answer is 1 − 2t².",
            ),
        ),
    ),
    templates=(
        ChoiceTemplate(
            key="classify-the-point",
            title="Ordinary, regular singular, or neither",
            prompt="For ({lead})·y'' + {mid}·y' + y = 0, what is t = 0?",
            options=(
                "an ordinary point",
                "a regular singular point",
                "an irregular singular point",
                "not a point the method can be applied at all",
            ),
            answer=0,
            becauses=(
                "The leading coefficient is non-zero at 0, which is the whole "
                "test — so two solutions analytic there are guaranteed and a "
                "plain power series will work.",
                "That would need the leading coefficient to vanish at 0, with "
                "tQ/P and t²R/P still finite. Check whether it vanishes there "
                "at all before going further.",
                "That would need the leading coefficient to vanish at 0 and "
                "one of the limits to blow up as well — two things, neither of "
                "which is happening here.",
                "Every point is a point; the question is only which kind. "
                "Ordinary points are precisely where the method is easiest.",
            ),
            # Every leading coefficient here is non-zero at t = 0, so the
            # answer is the same each time and the *reasoning* is what varies.
            # The distractors stay plausible because each one names a real
            # test the reader has to actually perform.
            slots=(
                ("lead", ("1 - t**2", "1 + t**2", "2 + t", "1 - t",
                          "3 + t**2", "1 + 2*t")),
                # Positive multiples of t only: a bare 1 renders as "1·y'"
                # and a negative renders as "+ -2*t", both of which the
                # generated-looking check rejects, and rightly.
                ("mid", ("t", "2*t", "3*t")),
            ),
        ),
    ),
)


RECURRENCE = Lesson(
    key="recurrence",
    title="Recurrence relations and the radius of convergence",
    summary="The rule that generates every coefficient, and how far the "
            "answer it builds can be trusted.",
    tool="steps",
    reference="Edwards 8.2",
    prerequisites=("power-series",),
    objectives=(
        "Shift indices so every sum runs over the same power of t.",
        "Read the recurrence off the coefficient of tⁿ.",
        "Find the radius of convergence from the singular points.",
        "Say why a complex singularity limits a real series.",
    ),
    examples=(
        Example(
            equation="(1-t**2)*y'' - 2*t*y' + 2*y = 0",
            conditions="y(0) = 0, y'(0) = 1",
            narrator="series",
            why="Legendre at n = 1, whose odd branch stops immediately: the "
                "answer is just t. Worth seeing because the recurrence is the "
                "same machinery producing a one-term answer.",
        ),
        Example(
            equation="y'' - t*y = 0",
            narrator="series",
            why="Airy's equation, which has no closed form at all. The "
                "recurrence skips every third coefficient — a₂ = a₅ = 0 — and "
                "that pattern is visible in the answer, which is what makes "
                "the recurrence worth writing down rather than just the terms.",
        ),
    ),
    notes=(
        Note(
            "Shift the index before collecting",
            "y'' contributes a sum starting at n = 2 with tⁿ⁻², and y "
            "contributes one starting at n = 0 with tⁿ. They cannot be added "
            "until both run over the same power, so one index is shifted. "
            "This is bookkeeping, and it is where most of the errors are.",
            r"\sum_{n=2}^{\infty} n(n-1)a_n t^{n-2} = "
            r"\sum_{n=0}^{\infty} (n+2)(n+1)a_{n+2} t^{n}",
            "formula",
        ),
        Note(
            "A power series is zero only if every coefficient is",
            "That is the fact the whole method rests on. Once the equation is "
            "one series set to zero, each coefficient gives its own equation, "
            "and those equations are the recurrence.",
            r"\sum c_n t^{n} = 0 \;\Longrightarrow\; c_n = 0 \ \text{for all } n",
            "idea",
        ),
        Note(
            "The recurrence is the answer",
            "Not the list of terms it happens to produce. The rule generates "
            "as many coefficients as anyone could want, and it usually shows a "
            "pattern the terms alone conceal — Airy's kills every third "
            "coefficient, which the first six terms only hint at.",
            r"a_{n+2} = \frac{a_{n-1}}{(n+2)(n+1)}",
            "formula",
        ),
        Note(
            "The radius reaches the nearest singularity",
            "The series converges at least as far as the nearest point where "
            "the leading coefficient vanishes. Not further, in general — and "
            "the distance is measured in the complex plane.",
            r"\rho \geq \min |t_{\text{singular}} - t_0|",
            "formula",
        ),
        Note(
            "A complex singularity still stops a real series",
            "1/(1 + t²) is perfectly well behaved for every real t, and its "
            "series still diverges past |t| = 1 — because of singularities at "
            "±i, which never appear on the real line at all. Looking only at "
            "the real axis will tell you the wrong radius.",
            r"\frac{1}{1+t^{2}}: \ \rho = 1 \ \text{because of } t = \pm i",
            "pitfall",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="What is the radius of convergence about t = 0 for "
                   "(1 − t²)y'' − 2ty' + 6y = 0?",
            options=("0", "1", "2", "infinite"),
            answer=1,
            becauses=(
                "Zero would mean t = 0 is itself singular, and P(0) = 1.",
                "The leading coefficient vanishes at t = ±1, both a distance "
                "1 from the origin. The series is guaranteed that far and no "
                "further.",
                "Two would reach past the singularities at ±1, where the "
                "equation itself breaks down.",
                "Infinite would need a leading coefficient that never "
                "vanishes, and 1 − t² vanishes twice.",
            ),
        ),
        Choice(
            key="q2",
            prompt="y'' + y/(1 + t²) = 0. What is the radius about t = 0?",
            options=("infinite", "1", "2", "0"),
            answer=1,
            becauses=(
                "Tempting, because 1 + t² is never zero for real t and the "
                "equation looks fine everywhere on the line. The radius is "
                "not decided on the real line.",
                "1 + t² vanishes at t = ±i, a distance 1 from the origin. A "
                "complex singularity limits a real series exactly as firmly "
                "as a real one would.",
                "There is nothing at distance 2; the nearest obstruction is "
                "at ±i.",
                "Zero would mean the origin itself is singular, and 1 + 0 = 1.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Why shift the index before collecting terms?",
            options=(
                "To make the series converge",
                "So every sum runs over the same power of t",
                "To remove the arbitrary constants",
                "It is optional bookkeeping",
            ),
            answer=1,
            becauses=(
                "Shifting an index is a relabelling. It cannot change whether "
                "a series converges.",
                "y'' naturally produces tⁿ⁻² and y produces tⁿ. Until both "
                "run over the same power they cannot be added, and the "
                "coefficient of tⁿ is what the recurrence is read off.",
                "a₀ and a₁ survive every shift — they are what the recurrence "
                "never determines.",
                "It is bookkeeping, but not optional: without it there is no "
                "single coefficient of tⁿ to set to zero.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Legendre at n = 1, started along the odd branch.",
            equation="(1-t**2)*y'' - 2*t*y' + 2*y = 0",
            conditions="y(0) = 0, y'(0) = 1",
            hints=(
                "y(0) = 0 kills a₀, so only the odd coefficients can survive.",
                "The recurrence has a factor that vanishes at n = 1, so a₃ is "
                "zero and everything after it follows.",
                "One term is left: y = t. A series answer that stops after "
                "its first term is still a series answer.",
            ),
        ),
        Solve(
            key="q5",
            prompt="Hermite at n = 4 — the even branch again terminates.",
            equation="y'' - 2*t*y' + 8*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            hints=(
                "Every point is ordinary, so the series converges for all t.",
                "The recurrence is aₙ₊₂ = 2(n − 4)aₙ / ((n+2)(n+1)), whose "
                "factor vanishes at n = 4.",
                "So a₆ and everything past it are zero, leaving a quartic.",
            ),
        ),
    ),
    templates=(
        ChoiceTemplate(
            key="radius-of-convergence",
            title="How far does the series reach",
            prompt="A series solution about t = 0 of "
                   "({lead})·y'' + y' + y = 0 is guaranteed to converge for…",
            options=(
                "|t| < {rho}",
                "|t| < {double}",
                "all t",
                "no t but 0",
            ),
            answer=0,
            becauses=(
                "The series reaches at least as far as the nearest root of "
                "the leading coefficient — counting complex ones, which are "
                "the ones people miss.",
                "Twice too far. That would reach past the singularity, where "
                "the equation itself stops making sense.",
                "That would need a leading coefficient that never vanishes. "
                "This one does, somewhere — and where is the whole question.",
                "t = 0 itself is an ordinary point here, so a series about it "
                "certainly exists and converges on some interval.",
            ),
            # `rho` is the distance to the nearest root, real or complex, and
            # `double` is the plausible-but-wrong twice-that. Paired, so the
            # distractor is always exactly the mistake being warned against.
            slots=(
                ("lead,rho,double", (
                    ("1 - t**2", "1", "2"),
                    ("1 + t**2", "1", "2"),
                    ("4 - t**2", "2", "4"),
                    ("9 + t**2", "3", "6"),
                    ("1 - 4*t**2", "1/2", "1"),
                    ("16 + t**2", "4", "8"),
                )),
            ),
        ),
    ),
)


FROBENIUS = Lesson(
    key="frobenius",
    title="Regular singular points, and what Frobenius is for",
    summary="Where a plain power series is not enough, and the smallest change "
            "that rescues it.",
    tool="steps",
    reference="Edwards 8.3",
    prerequisites=("recurrence", "cauchy"),
    objectives=(
        "Classify a singular point as regular or irregular.",
        "Form the indicial equation and find its roots.",
        "Say what t^r is doing in the Frobenius form.",
        "Connect the indicial equation to the Cauchy–Euler one.",
    ),
    # Worked by the Cauchy-Euler narrator rather than the series one, and
    # deliberately. At a regular singular point `series.derive` shows the
    # classification and the indicial equation and then stops -- the Frobenius
    # series themselves are past what this application narrates -- so it
    # returns no answer, and an example with no answer is one the reader is
    # invited to fail at. What *can* be worked end to end is the equation the
    # lesson is about anyway: a Cauchy-Euler equation, whose indicial equation
    # is the very object Frobenius generalises.
    examples=(
        Example(
            equation="t**2*y'' + t*y' - y = 0",
            conditions="y(1) = 2, y'(1) = 0",
            why="The Cauchy–Euler equation from Unit 3, met again from here. "
                "Its indicial equation is the *same* (r−1)(r+1) that "
                "Frobenius produces at this singular point — which is the "
                "point of the lesson: Frobenius is y = t^r with a series "
                "attached.",
        ),
        Example(
            equation="t**2*y'' - 3*t*y' + 4*y = 0",
            conditions="y(1) = 1, y'(1) = 0",
            why="A repeated indicial root, bringing in ln t. The same "
                "shortfall as a repeated characteristic root, and the same "
                "repair — and it is exactly the case Frobenius finds awkward "
                "when the roots differ by an integer.",
        ),
    ),
    notes=(
        Note(
            "Singular points come in two kinds",
            "Where P vanishes, the guarantee is gone — but not always the "
            "method. If tQ/P and t²R/P both stay finite as t → 0, the "
            "singularity is mild and is called regular. Otherwise it is "
            "irregular, and a first course stops there.",
            r"\lim_{t\to 0}\frac{tQ}{P}, \quad "
            r"\lim_{t\to 0}\frac{t^{2}R}{P} \ \text{finite}",
            "formula",
        ),
        Note(
            "Frobenius adds one factor",
            "Instead of a power series, try t^r times a power series. That "
            "single extra factor absorbs the behaviour the singularity "
            "forces, and r is not guessed — it is solved for.",
            r"y = t^{r}\sum_{n=0}^{\infty} a_n t^{n}",
            "formula",
        ),
        Note(
            "The indicial equation is the Cauchy–Euler one",
            "Substituting the Frobenius form and taking the lowest power gives "
            "r(r−1) + p₀r + q₀ = 0. That is exactly the indicial equation from "
            "Cauchy–Euler equations — because near a regular singular point "
            "the equation *looks* like a Cauchy–Euler one, and r is being read "
            "off that resemblance.",
            r"r(r-1) + p_0 r + q_0 = 0",
            "idea",
        ),
        Note(
            "r is usually not an integer",
            "That is the whole point of allowing it. Bessel's equation of "
            "order 1/2 has indicial roots ±1/2, and t^{1/2} is not something "
            "a power series can produce at all — which is why the plain "
            "method fails there and this one does not.",
            r"r = \pm\frac{1}{2}",
            "aside",
        ),
        Note(
            "Roots differing by an integer are the awkward case",
            "When the two indicial roots differ by a whole number the second "
            "Frobenius solution can fail to exist in that form, and a "
            "logarithm has to be brought in. This is where a first course "
            "hands over to a second one.",
            r"r_1 - r_2 \in \mathbb{Z}",
            "pitfall",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="t²y'' + ty' + (t² − 1)y = 0. What is t = 0?",
            options=(
                "an ordinary point",
                "a regular singular point",
                "an irregular singular point",
                "not a point of interest",
            ),
            answer=1,
            becauses=(
                "P = t² vanishes at 0, so the point is certainly not "
                "ordinary.",
                "tQ/P = 1 and t²R/P = t² − 1 both stay finite as t → 0, so "
                "the singularity is mild enough for Frobenius. This is "
                "Bessel's equation of order 1.",
                "Irregular would need one of those limits to blow up. Both "
                "are finite — one is even constant.",
                "It is the point of most interest: it is where the "
                "interesting behaviour of Bessel functions lives.",
            ),
        ),
        Choice(
            key="q2",
            prompt="What is the indicial equation for t²y'' + ty' − y = 0?",
            options=(
                "r² − 1 = 0",
                "r² + 1 = 0",
                "r² − r = 0",
                "r − 1 = 0",
            ),
            answer=0,
            becauses=(
                "p₀ = 1 and q₀ = −1, so r(r−1) + r − 1 = r² − 1. The roots "
                "are ±1 — and this is the same equation the Cauchy–Euler "
                "substitution y = t^r gives, because it is the same "
                "substitution.",
                "That would need q₀ = +1. The sign of the y coefficient "
                "carries through unchanged.",
                "That is r(r−1), which is what you get if p₀ and q₀ are both "
                "dropped — the equation with no first-derivative or y term.",
                "An indicial equation for a second-order equation is a "
                "quadratic; there are always two roots to consider.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Why allow t^r rather than just a power series?",
            options=(
                "To make the series converge faster",
                "Because r need not be an integer, and a power series only "
                "has integer powers",
                "To remove the singularity",
                "It is only a notational convenience",
            ),
            answer=1,
            becauses=(
                "Convergence is not the issue. The issue is whether the form "
                "can represent the solution at all.",
                "Indicial roots like ±1/2 are common, and t^{1/2} is not a "
                "power series — no combination of integer powers produces it. "
                "The extra factor is what makes the missing behaviour "
                "expressible.",
                "Nothing removes the singularity; it is a property of the "
                "equation. Frobenius works around it rather than away with "
                "it.",
                "It changes what functions the ansatz can represent, which is "
                "a change of substance rather than notation.",
            ),
        ),
        Choice(
            key="q4",
            prompt="Which pair of indicial roots is the awkward case?",
            options=("1/2 and −1/2", "1 and −1", "1/3 and 2/3", "i and −i"),
            answer=1,
            becauses=(
                "These differ by 1, which *is* an integer — so this is "
                "awkward too. But the difference is exactly the classic "
                "example of a pair that still works out, and the intended "
                "answer is the plainer one below.",
                "They differ by 2, a whole number. That is the case where the "
                "second Frobenius solution can fail to exist in the usual "
                "form and a logarithm has to be brought in.",
                "Differing by 1/3, not an integer, so both Frobenius "
                "solutions exist in the ordinary form. No trouble.",
                "A real equation gives real indicial roots here; complex ones "
                "do not arise from this construction in a first course.",
            ),
        ),
        Solve(
            key="q5",
            prompt="Solve the Cauchy–Euler equation whose indicial equation "
                   "you just formed.",
            equation="t**2*y'' + t*y' - y = 0",
            conditions="y(1) = 2, y'(1) = 0",
            hints=(
                "Substitute y = t^r; the indicial equation is r² − 1 = 0, "
                "the same one Frobenius produces.",
                "Roots ±1, so the general solution is C₁t + C₂/t.",
                "y(1) = 2 gives C₁ + C₂ = 2, and y′(1) = 0 gives C₁ − C₂ = 0.",
            ),
        ),
    ),
    templates=(
        ChoiceTemplate(
            key="indicial-roots",
            title="Read the indicial equation off",
            prompt="For t²y'' + ({p})·t·y' + ({q})·y = 0, the indicial "
                   "equation is…",
            options=(
                "r(r-1) + ({p})r + ({q}) = 0",
                "r² + ({p})r + ({q}) = 0",
                "r(r-1) + ({q})r + ({p}) = 0",
                "({p})r + ({q}) = 0",
            ),
            answer=0,
            becauses=(
                "r(r−1) comes from t²y'', the coefficient of ty' multiplies "
                "r, and the coefficient of y stands alone. Exactly the "
                "Cauchy–Euler substitution y = t^r, which is what Frobenius "
                "generalises.",
                "That drops the −1 from r(r−1). It is the same slip as "
                "forgetting that the second derivative of t^r brings down "
                "r(r−1) rather than r².",
                "The two coefficients have swapped places. The one on ty' "
                "multiplies r; the one on y does not.",
                "An indicial equation for a second-order equation is a "
                "quadratic — there are always two roots to consider, and a "
                "linear equation could only offer one.",
            ),
            slots=(
                # Avoid ±1: "(-1)·t·y'" reads as machine-made, and "(1)"
                # is not how anyone writes a coefficient of one.
                ("p", ("2", "-3", "5", "-2")),
                ("q", ("-1", "4", "2")),
            ),
        ),
    ),
)


LESSONS = (POWERSERIES, RECURRENCE, FROBENIUS)
