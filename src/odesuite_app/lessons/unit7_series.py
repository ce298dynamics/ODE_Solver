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
    Passage,
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
    figure="partial_sums",
    motivation=(
        "The whole course so far has been a search for equations that can be "
        "solved in closed form, and the honest summary is that they are a "
        "thin and unrepresentative slice. Change one coefficient of a "
        "solvable equation from a constant to t and every technique in the "
        "course stops applying, while the equation itself remains perfectly "
        "ordinary and its solutions perfectly well behaved.\n\n"
        "That is not a rare misfortune. Bessel's equation, Legendre's, "
        "Airy's, Hermite's — the equations that describe a vibrating drum, a "
        "potential on a sphere, light near a caustic, a quantum oscillator — "
        "none of them has an elementary solution, and all of them are "
        "ordinary second-order linear equations with polynomial coefficients.\n\n"
        "So the last technique of the course changes what an answer is "
        "allowed to look like. Rather than searching for a formula in terms "
        "of functions that already have names, build the solution coefficient "
        "by coefficient as a power series. The equation itself supplies the "
        "rule for the coefficients, and that rule *is* the answer — a "
        "complete description, even when no elementary function matches it."
    ),
    derivation=(
        Passage(
            prose="Assume the answer is a power series about the point of interest, "
                  "with the coefficients unknown. This is a genuine assumption and the "
                  "next two passages are about when it is safe — but grant it for a "
                  "moment and see what the equation does with it.",
            latex=r"y(t) = \sum_{n=0}^{\infty} a_n t^{n}",
        ),
        Passage(
            prose="Inside its interval of convergence such a series can be "
                  "differentiated term by term, so the derivatives are series of the "
                  "same kind. That is the property being relied on, and it is what "
                  "makes the whole method work rather than merely look plausible.",
            latex=r"y'(t) = \sum_{n=1}^{\infty} n\,a_n t^{n-1}, \qquad y''(t) "
                  r"= \sum_{n=2}^{\infty} n(n-1)\,a_n t^{n-2}",
        ),
        Passage(
            prose="Now the condition. Write the equation with the second derivative's "
                  "coefficient equal to one — the same first move as the integrating "
                  "factor lesson — and ask whether the two remaining coefficients are "
                  "analytic at the point, meaning each has a power series of its own "
                  "there. A point where they are is called ordinary.",
            latex=r"y'' + p(t)y' + q(t)y = 0, \qquad p,\ q \text{ analytic at } t_0",
        ),
        Passage(
            prose="At such a point the assumption is guaranteed, not hoped for: there "
                  "are two independent solutions, each a power series, each converging "
                  "at least as far as the nearest point where p or q fails. The theorem "
                  "is what turns the method from a gamble into a procedure.",
            latex=r"t_0 \text{ ordinary} \;\Longrightarrow\; \text{two series solutions exist}",
        ),
        Passage(
            prose="Substituting the series into the equation gives a series equal to "
                  "zero, and one fact makes that usable: a power series vanishing on an "
                  "interval must have every coefficient zero. So the single equation "
                  "splits into infinitely many, one for each power, each relating a few "
                  "coefficients — and solving them is arithmetic, not calculus.",
            latex=r"\sum_n c_n t^{n} = 0 \text{ on an interval} "
                  r"\;\Longrightarrow\; c_n = 0 \text{ for every } n",
        ),
        Passage(
            prose="The first two coefficients are never determined by any of those "
                  "equations, and that is exactly right. Evaluating the series and its "
                  "derivative at the point shows why: they *are* the two initial "
                  "conditions, so the freedom the equation leaves is precisely the "
                  "freedom a second-order equation is supposed to have.",
            latex=r"y(t_0) = a_0, \qquad y'(t_0) = a_1",
        ),
        Passage(
            prose="One caution about what has been produced. Any finite number of terms "
                  "is an approximation and is wrong away from the point — but the "
                  "series itself is not an approximation, and neither is the rule that "
                  "generates it. Truncating is a choice made when a number is wanted, "
                  "and it should not be confused with the answer.",
            latex=r"y \approx a_0 + a_1 t + a_2 t^{2} + \cdots \text{ "
                  r"(truncated, not incomplete)}",
        ),
    ),
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
            commentary=(
                "Check the point before assuming anything, since that is the step the "
                "derivation insists on. Divide through so the second derivative "
                "stands alone: the coefficients acquire a denominator that vanishes "
                "at plus and minus one, and nowhere else. The origin is comfortably "
                "clear of both, so the theorem applies and two series solutions are "
                "guaranteed.\n\n"
                "Then watch the recurrence terminate. The numerator of the ratio hits "
                "zero at one particular index, so every coefficient past it is zero "
                "and the infinite series collapses to a polynomial. That is not the "
                "method failing to produce a series — it is producing one whose tail "
                "is entirely zeros, and it is why this family of equations turns up "
                "wherever a physical problem needs an answer that stays finite."
            ),
        ),
        Example(
            equation="y'' - 2*t*y' + 4*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            narrator="series",
            why="Hermite's equation at n = 2, giving 1 − 2t². The same "
                "phenomenon from a different family, and worth comparing: the "
                "recurrences differ but both terminate.",
            commentary=(
                "The coefficients here are polynomials with no denominator at all, so "
                "every point of the line is ordinary and the guaranteed radius is "
                "infinite. Compare that with the previous example, where the "
                "guarantee stopped at one — the difference is visible in the equation "
                "before any coefficient is computed.\n\n"
                "Then set the two recurrences side by side. They are not the same "
                "rule, and the coefficients they generate differ — yet both "
                "terminate, and for the same structural reason: a numerator that "
                "vanishes at one index and therefore zeros everything after it. Two "
                "different families, one mechanism, and it is the mechanism rather "
                "than either answer that is worth carrying away."
            ),
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
        # PED-06: where the method itself stops, not a mistake a student makes.
        Note(
            "Where it stops: at a singular point",
            "A power series about t₀ is guaranteed only when p and q are "
            "analytic there, and then it converges at least out to the nearest "
            "singularity — complex ones included. At a singular point itself "
            "there may be no power series solution at all: t²y'' + t y' + (t² −"
            " ν²)y = 0 at t = 0 needs the Frobenius form t^r·Σ aₙtⁿ.",
            r"y = t^{r}\sum_{n \geq 0} a_n t^{n}",
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
    figure="recurrence",
    motivation=(
        "Assuming a series and substituting it is the easy half. What comes "
        "back is an equation between three or four infinite sums whose powers "
        "do not line up, and turning that into something usable is where the "
        "actual work of this unit lives.\n\n"
        "The obstacle is bookkeeping rather than mathematics, and it has a "
        "standard remedy. Differentiating shifts the exponent down, "
        "multiplying by t shifts it up, so the sums arrive misaligned — and "
        "before any coefficient can be compared with any other, they have to "
        "be re-indexed onto a common power. Almost every error in this topic "
        "happens in that step.\n\n"
        "Once aligned, one fact does everything: a power series that vanishes "
        "on an interval has every coefficient zero. That converts a single "
        "equation into an infinite family of ordinary ones, each linking a "
        "coefficient to earlier ones — and that rule, not any list of "
        "numbers, is the answer. There is also a second dividend, since the "
        "equation announces in advance how far the series will be good for."
    ),
    derivation=(
        Passage(
            prose="Substitute the series and its derivatives. Each term arrives with "
                  "its own starting index and its own exponent, and no two of the sums "
                  "are expressed in the same power of t — which is why nothing can yet "
                  "be compared.",
            latex=r"\sum_{n\geq 2} n(n-1)a_n t^{n-2} + \cdots + \sum_{n\geq 0} a_n t^{n} = 0",
        ),
        Passage(
            prose="So shift the index before collecting anything. Replacing the "
                  "summation variable moves the exponent without changing the sum — "
                  "this is renaming, not manipulation — and the starting index moves by "
                  "the same amount, which is the half that gets forgotten.",
            latex=r"\sum_{n\geq 2} n(n-1)a_n t^{n-2} = \sum_{k\geq 0}(k+2)(k+1)a_{k+2}t^{k}",
        ),
        Passage(
            prose="With every sum on the same power, collect the coefficient of each. "
                  "The equation is now a single series set equal to zero, and "
                  "everything depends on what that permits.",
            latex=r"\sum_{k\geq 0}\left[(k+2)(k+1)a_{k+2} + \cdots\right]t^{k} = 0",
        ),
        Passage(
            prose="What it permits is nothing. A power series that vanishes throughout "
                  "an interval must have every coefficient zero — evaluate at the "
                  "centre to kill the first, differentiate and evaluate again for the "
                  "second, and so on indefinitely. That is the identity theorem, and it "
                  "is the licence for everything that follows.",
            latex=r"c_k = 0 \quad \text{for every } k",
        ),
        Passage(
            prose="Each of those equations expresses a later coefficient in terms of "
                  "earlier ones, so the whole infinite family collapses into a single "
                  "rule. Two coefficients stay free, they are the initial conditions, "
                  "and the rule generates every other coefficient from them.",
            latex=r"a_{k+2} = -\frac{\left(\text{terms in } a_k,\ a_{k+1}\right)}{(k+2)(k+1)}",
        ),
        Passage(
            prose="The rule is the answer, and it is worth being firm about that. A "
                  "list of the first six coefficients is a truncation; the recurrence "
                  "is complete, generates as many terms as anyone asks for, and shows "
                  "structure a list conceals — such as every third coefficient "
                  "vanishing, which is invisible in the numbers and obvious in the "
                  "rule.",
            latex=r"a_{k+3} = \frac{a_k}{(k+2)(k+3)} \;\Longrightarrow\; a_2 = a_5 = a_8 = 0",
        ),
        Passage(
            prose="Finally, how far the series is good for, which the equation answers "
                  "before any coefficient is computed. Put the equation in standard "
                  "form and find where its coefficients fail; the radius of convergence "
                  "reaches at least to the nearest such point. Nothing has to be tested "
                  "for convergence by hand.",
            latex=r"\rho \geq \min\left|t_{\text{singular}} - t_0\right|",
        ),
        Passage(
            prose="And that nearest point may be complex, which is the surprise. A real "
                  "equation with no real trouble anywhere can still have its series "
                  "stop, because a root of the leading coefficient off the real axis is "
                  "just as close and just as fatal — a fact about the real line that "
                  "only the complex plane explains.",
            latex=r"1 + t^{2} = 0 \;\Longrightarrow\; t = \pm i \;\Longrightarrow\; \rho = 1",
        ),
    ),
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
            commentary=(
                "Find the singular points first: the leading coefficient factors, so "
                "the two of them are immediate and the guaranteed radius is the "
                "distance from the origin to the nearer one. That number is available "
                "before a single coefficient is computed, and having it first is the "
                "habit this lesson is for.\n\n"
                "Then watch a recurrence do something surprising. The numerator "
                "vanishes at the very first step of the odd branch, so every odd "
                "coefficient after the first is zero and the whole branch is a single "
                "term. The machinery did not fail and no shortcut was taken — the "
                "rule simply generated zeros, which is what a rule is entitled to do."
            ),
        ),
        Example(
            equation="y'' - t*y = 0",
            narrator="series",
            why="Airy's equation, which has no closed form at all. The "
                "recurrence skips every third coefficient — a₂ = a₅ = 0 — and "
                "that pattern is visible in the answer, which is what makes "
                "the recurrence worth writing down rather than just the terms.",
            commentary=(
                "The leading coefficient is one and never vanishes, so the guaranteed "
                "radius is infinite and the series converges everywhere. That is "
                "worth noting precisely because the answer is not elementary: "
                "convergence for all t and expressibility in closed form are "
                "different questions, and this equation settles them opposite ways.\n\n"
                "Then read the pattern rather than the numbers. The rule connects "
                "each coefficient to the one three places back, so the sequence "
                "splits into three independent chains — two started by the free "
                "constants and one started by a zero, which therefore stays zero "
                "forever. A printed list of terms shows a scattering of zeros with no "
                "evident cause; the recurrence shows why they are there and which "
                "ones come next."
            ),
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
        Choice(
            key="q-figure",
            prompt="Slide l in the figure onto 4. Reading the stems in the "
                   "left pane, which of the drawn coefficients are zero?",
            figure="recurrence",
            options=(
                "a₆ and every even coefficient after it",
                "a₄ and every even coefficient after it",
                "Every odd coefficient, because l is even",
                "None of them — a recurrence never produces an exact zero",
            ),
            answer=0,
            becauses=(
                "The numerator n(n+1) − l(l+1) is zero at n = 4, and the "
                "recurrence takes a₄ to a₆, so a₆ is zero and every later "
                "even coefficient inherits it. What is left is a polynomial "
                "of degree 4, which is why Legendre polynomials exist.",
                "a₄ is the last coefficient that survives, not the first that "
                "dies. The recurrence multiplies a₄ by the vanishing factor "
                "to get a₆, so the zero lands one step further on.",
                "The odd coefficients descend from a₁ and their numerators "
                "are n(n+1) − 20 at odd n, which is never zero. Read the "
                "stems: they are still there at a₁₅.",
                "It produces one exactly when l is a whole number, and that "
                "is the whole reason whole numbers are the interesting case. "
                "The slider snaps onto them so that it can be seen happening.",
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
    figure="indicial",
    motivation=(
        "The series method came with a condition: the point must be ordinary. "
        "The points that are not ordinary are exactly the interesting ones. A "
        "singular point is usually where the geometry does something — the "
        "centre of a disc, the axis of a cylinder, the pole of a sphere — and "
        "the boundary condition that matters is usually stated there.\n\n"
        "Assuming a plain power series at such a point simply fails, and it "
        "fails informatively. Substituting one into a Cauchy–Euler equation "
        "forces every coefficient to zero, so the method reports that the "
        "only solution of its assumed shape is the zero function. The "
        "assumption was wrong, not the equation.\n\n"
        "What is wrong with it is visible in Unit 3. The solutions of a "
        "Cauchy–Euler equation are powers with exponents that are usually "
        "neither whole numbers nor positive, and no power series contains "
        "such a thing. So allow one factor of an arbitrary power in front of "
        "an ordinary series — and that single change is the whole of "
        "Frobenius."
    ),
    derivation=(
        Passage(
            prose="First distinguish the singular points that can be handled from those "
                  "that cannot. Write the equation in standard form; if the "
                  "coefficients blow up no faster than a fixed rate — one factor for "
                  "the first derivative's coefficient, two for the other's — the point "
                  "is called regular, and the method applies.",
            latex=r"(t - t_0)\,p(t) \text{ and } (t - t_0)^{2}q(t) \text{ analytic at } t_0",
        ),
        Passage(
            prose="The reason that is the right condition is worth seeing rather than "
                  "accepting. Multiply through by the square of the distance from the "
                  "point and the leading behaviour of every coefficient is a constant — "
                  "which is to say the equation looks, near that point, exactly like a "
                  "Cauchy–Euler equation.",
            latex=r"(t-t_0)^{2}y'' + (t-t_0)\,\left[(t-t_0)p\right]y' + "
                  r"\left[(t-t_0)^{2}q\right]y = 0",
        ),
        Passage(
            prose="And that lesson already says what such an equation does: its "
                  "solutions are powers, with the exponent given by a quadratic. So "
                  "near a regular singular point the solution must behave like some "
                  "power — and there is no reason at all for the exponent to be a whole "
                  "number.",
            latex=r"y \sim (t - t_0)^{r} \text{ near } t_0",
        ),
        Passage(
            prose="So assume that behaviour and correct it with an ordinary series. The "
                  "leading coefficient is taken non-zero, which is what makes the "
                  "exponent mean what it should — otherwise it could be raised at will "
                  "and would say nothing.",
            latex=r"y = (t - t_0)^{r}\sum_{n=0}^{\infty}a_n (t-t_0)^{n}, \qquad a_0 \neq 0",
        ),
        Passage(
            prose="Substitute and collect the lowest power. Its coefficient involves "
                  "only the leading term, and setting it to zero gives a quadratic in "
                  "the exponent — which is precisely the indicial equation of the "
                  "Cauchy–Euler equation from the second passage. The two lessons share "
                  "it because they are looking at the same leading behaviour.",
            latex=r"r(r-1) + p_0\,r + q_0 = 0",
        ),
        Passage(
            prose="The larger root always works and always produces a solution. The "
                  "smaller one usually does too, and the exception is worth knowing: "
                  "when the two roots differ by a whole number, the smaller root's "
                  "series can collide with the larger one's and break down partway "
                  "through.",
            latex=r"r_1 - r_2 \notin \mathbb{Z} \;\Longrightarrow\; \text{two "
                  r"Frobenius series}",
        ),
        Passage(
            prose="When it does break down the repair is the one this course has used "
                  "twice already — for a repeated characteristic root and for a "
                  "repeated indicial root. Something is missing, and what supplies it "
                  "carries a logarithm, which is what the substitution in the "
                  "Cauchy–Euler lesson showed a repeated exponent must produce.",
            latex=r"y_2 = C\,y_1\ln(t-t_0) + (t-t_0)^{r_2}\sum_n b_n (t-t_0)^{n}",
        ),
    ),
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
            commentary=(
                "Confirm the point is regular before anything else: in standard form "
                "the coefficients have one and two factors of t underneath them "
                "respectively, which is exactly the rate the first passage permits. "
                "Had either been worse, no method in this course would apply at that "
                "point.\n\n"
                "Then do the comparison this example exists for. Form the indicial "
                "equation here and set it beside the one Unit 3 produced for the same "
                "equation: they are identical, because this equation *is* its own "
                "leading behaviour — there is nothing for the series to correct, so "
                "every coefficient after the first comes out zero and Frobenius "
                "returns the Cauchy–Euler answer exactly."
            ),
        ),
        Example(
            equation="t**2*y'' - 3*t*y' + 4*y = 0",
            conditions="y(1) = 1, y'(1) = 0",
            why="A repeated indicial root, bringing in ln t. The same "
                "shortfall as a repeated characteristic root, and the same "
                "repair — and it is exactly the case Frobenius finds awkward "
                "when the roots differ by an integer.",
            commentary=(
                "The indicial equation is a perfect square, so the two exponents "
                "coincide — which is the extreme case of roots differing by a whole "
                "number, since they differ by zero. One Frobenius series is all that "
                "this exponent can produce, and a second solution has to come from "
                "somewhere else.\n\n"
                "It comes with a logarithm, and the shortfall is the same one this "
                "course has met twice before: a repeated characteristic root gave one "
                "exponential where two solutions were needed, and a repeated indicial "
                "root gives one power. Three different settings, one pattern — "
                "something is missing, and what fills the gap carries an extra factor "
                "that the first solution does not have."
            ),
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
