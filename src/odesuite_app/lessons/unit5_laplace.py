"""Unit 5 -- Laplace transforms.

Edwards, Penney and Calvis 6e, chapter 7. The one technique in a first course
that turns the equation into algebra, and the only one that copes with forcing
switched on partway through or delivered as an impulse.

Six lessons, in the order Edwards presents them: what the transform is and how
to read the table, solving an initial value problem with it, the two shifting
theorems and the partial fractions that feed them, convolution, forcing that
switches on partway through, and impulses.

Where a typed answer cannot be graded, the drill is **multiple choice** instead.
`check_answer` grades by substituting an answer back and simplifying, and a
switched or impulsive answer differentiated twice leaves Heaviside and delta
terms that never cancel -- so the verdict is "cannot tell", which is correct
and which can never advance a mastery streak. That is a reason to change the
question type rather than to omit the drill, and `ChoiceTemplate` is what
`step-forcing` and `impulses` use.

`convolution` still has none: its integrals cost seconds apiece, and the
exhaustive sweep runs every draw of every template.
"""

from __future__ import annotations

from .model import (
    Choice,
    ChoiceTemplate,
    Example,
    ExpressionTemplate,
    Lesson,
    Note,
    NumericTemplate,
    Passage,
    Solve,
    Template,
)

__all__ = ["TRANSFORM", "LAPLACE", "SHIFTING", "CONVOLUTION",
           "STEPFORCING", "IMPULSES", "LESSONS"]


LAPLACE = Lesson(
    key="laplace",
    title="Laplace transforms",
    summary="Turn the differential equation into algebra — and handle forcing "
            "that switches on partway through.",
    tool="laplace",
    reference="Edwards 7.1–7.6",
    figure="partial_fractions",
    motivation=(
        "With the transform of a derivative in hand, the method can be run "
        "end to end. What makes it worth learning is not that it solves "
        "equations the earlier methods could not reach in principle — for "
        "smooth forcing it produces exactly the same answer that undetermined "
        "coefficients would. It is what it does with the *shape* of the "
        "problem.\n\n"
        "Two features stand out. The initial conditions enter at the "
        "beginning rather than at the end: there is no general solution with "
        "constants in it waiting to be pinned down, because the conditions "
        "were absorbed the moment the derivatives were transformed. That "
        "removes an entire stage of the work and with it an entire class of "
        "mistakes.\n\n"
        "And the forcing can be discontinuous. A switch thrown at two "
        "seconds, or a hammer blow at one, is hopeless for a trial-set method "
        "— there is no single formula on both sides of the switch — but under "
        "the transform it is one more row of the table. That is what the "
        "transform is really for, and it is why this unit sits where it does "
        "in the course."
    ),
    derivation=(
        Passage(
            prose="Transform every term of the equation. The derivatives become powers "
                  "of s times the transform of the answer, each dragging its own piece "
                  "of initial data with it, and the forcing becomes whatever its "
                  "transform is.",
            latex=r"\mathcal{L}\{y''\} + a\,\mathcal{L}\{y'\} + "
                  r"b\,\mathcal{L}\{y\} = \mathcal{L}\{f\}",
        ),
        Passage(
            prose="Collect the terms. Everything multiplying the transform of the "
                  "answer is a polynomial in s — and it is the characteristic "
                  "polynomial of the equation, unchanged, which is the first sign that "
                  "this method is not unrelated to the previous unit.",
            latex=r"\left(s^{2} + a s + b\right)Y(s) = F(s) + \left(s + a\right)y(0) + y'(0)",
        ),
        Passage(
            prose="Divide. The answer's transform is now written down completely, with "
                  "no constants left undetermined anywhere — which is the structural "
                  "difference from every earlier method. The conditions are not fitted "
                  "afterwards because they were never left out.",
            latex=r"Y(s) = \frac{F(s) + (s + a)y(0) + y'(0)}{s^{2} + a s + b}",
        ),
        Passage(
            prose="Notice the two halves of that numerator, because they are the split "
                  "the vibrations unit spent a lesson on. One piece comes from the "
                  "forcing and one from the initial data, and since the whole thing is "
                  "divided by the same polynomial, the transform is already the steady "
                  "state plus the transient — separated before anything is inverted.",
            latex=r"Y(s) = \frac{F(s)}{P(s)} + \frac{(s+a)y(0) + y'(0)}{P(s)}",
        ),
        Passage(
            prose="Then invert, and this is where the work is. The expression almost "
                  "never matches a table row as it stands, so it has to be taken apart "
                  "into pieces that do — partial fractions when the denominator "
                  "factors, completing the square when it does not, and the shifting "
                  "theorems for everything that has been displaced.",
            latex=r"Y(s) = \sum_j \frac{A_j}{s - r_j} \;\Longrightarrow\; y(t) "
                  r"= \sum_j A_j e^{r_j t}",
        ),
        Passage(
            prose="The roots of that denominator are the roots of the characteristic "
                  "polynomial, so the exponentials that come back are the ones the "
                  "previous unit would have produced. For smooth forcing this method is "
                  "a different route to the same answer, and knowing that is what makes "
                  "it possible to check one against the other.",
            latex=r"P(r) = 0 \;\Longleftrightarrow\; e^{rt} \text{ appears in } y",
        ),
        Passage(
            prose="What is genuinely new is that the forcing need not be smooth. A "
                  "step, a pulse, an impulse — each has a perfectly ordinary transform, "
                  "so each passes through the division untroubled. No earlier method "
                  "can even state such a problem in one piece, and that is the reason "
                  "this unit exists.",
            latex=r"\mathcal{L}\{u(t-a)\} = \frac{e^{-as}}{s}",
        ),
    ),
    prerequisites=("roots", "undetermined", "transform"),
    objectives=(
        "Transform a derivative, and place the initial conditions where they "
        "actually enter.",
        "Solve the transformed equation for Y(s) — it is only algebra.",
        "Split Y(s) into pieces that match rows of the table, and invert them.",
        "Handle a forcing term that switches on at t = a, using the second "
        "shifting theorem.",
    ),
    examples=(
        Example(
            equation="y'' + 3*y' + 2*y = sin(t)",
            conditions="y(0) = 1, y'(0) = 0",
            narrator="laplace",
            why="Smooth forcing and nonzero conditions — the case that shows "
                "the conditions entering at the *start*, through the transform "
                "of y'', rather than arriving at the end as constants to pin.",
            commentary=(
                "Smooth forcing and non-zero conditions, so this is the case where "
                "the two methods can be compared directly. Factor the denominator and "
                "look at its roots: they are the characteristic roots of the "
                "equation, so the exponentials that come back are exactly the ones "
                "the previous unit would have produced.\n\n"
                "Then count where the work went. There is no stage at which a general "
                "solution is written down and constants are fitted, because the "
                "conditions were absorbed at the transform. What replaced that stage "
                "is the partial fraction split — which is more algebra, not less, and "
                "that is the honest trade. The method wins on problems where the old "
                "stage was impossible, not on problems where it was merely tedious."
            ),
        ),
        Example(
            equation="y' + y = Heaviside(t - 2)",
            conditions="y(0) = 0",
            narrator="laplace",
            why="A switch thrown at two seconds. Not separable, no integrating "
                "factor worth writing, and not what undetermined coefficients "
                "is for — this is the problem the transform exists for.",
            commentary=(
                "Try, briefly, to solve this any other way. Separation gives two "
                "problems and no way to join them; an integrating factor works on "
                "each side of the switch and then needs the two answers matched by "
                "hand at the join. The transform never notices that anything "
                "discontinuous happened.\n\n"
                "Then look at what the exponential factor in the transform does on "
                "the way back. It does not scale the answer — it *delays* it, and the "
                "Heaviside factor that appears alongside is what makes the answer "
                "identically zero beforehand. Check that by substituting a time "
                "before the switch: every term vanishes, which is the correct "
                "physical claim rather than an artefact of the notation."
            ),
        ),
    ),
    notes=(
        Note(
            "What it does",
            "The transform turns a function of t into a function of s, and — "
            "this is the point — it turns differentiation into multiplication. "
            "A differential equation becomes an algebraic one, which you solve "
            "with ordinary algebra and then transform back.",
            r"\mathcal{L}\{y'\} = sY(s) - y(0)",
            "formula",
        ),
        Note(
            "The initial conditions come in at the start",
            "Look at where y(0) appears: in the transform of the derivative "
            "itself. No arbitrary constants are ever introduced, so there is "
            "nothing to pin down at the end. This is the real difference from "
            "every other method here.",
            r"\mathcal{L}\{y''\} = s^{2}Y(s) - s\,y(0) - y'(0)",
            "formula",
        ),
        Note(
            "y(0) carries the s, y'(0) does not",
            "In s²Y − s·y(0) − y'(0) the two conditions enter differently, and "
            "swapping them is the mistake this topic produces. Count powers: "
            "the term that came from differentiating twice keeps one factor of "
            "s for the condition it consumed first.",
            r"\mathcal{L}\{y''\} = s^{2}Y - s\,y(0) - y'(0)",
            "pitfall",
        ),
        Note(
            "Getting back",
            "Solve for Y(s), split it into partial fractions until every piece "
            "matches a row of the table, and read each one backwards. Partial "
            "fractions exist in this subject for exactly this purpose.",
            r"Y(s) = \frac{1}{(s+1)(s+2)} = \frac{1}{s+1} - \frac{1}{s+2}",
        ),
        Note(
            "Why it is worth the trouble: switches and impulses",
            "A step u(t−a) transforms to e^{−as}/s and an impulse δ(t−a) to "
            "e^{−as}. Neither is something separation, integrating factors or "
            "undetermined coefficients can handle at all — a switch thrown at "
            "t = 2 has no shape to guess. Here it is one more factor.",
            r"\mathcal{L}\{u(t-a)g(t-a)\} = e^{-as}G(s)",
            "formula",
        ),
        Note(
            "The transform integrates from zero",
            "Every condition has to be given at t = 0. A condition at t = 1 "
            "cannot be used at all — not because the algebra is harder, but "
            "because the transform never sees the interval it applies to. "
            "Restate the problem before transforming.",
            r"\mathcal{L}\{f\}(s) = \int_{0}^{\infty} e^{-st} f(t)\,dt",
            "aside",
        ),
        # PED-06: where the method itself stops, not a mistake a student makes.
        Note(
            "Where it stops: exponential order and constant coefficients",
            "The transform exists only for functions that grow no faster than "
            "some exp(at): exp(t²) has none. And the method turns derivatives "
            "into algebra only for constant coefficients; a coefficient of t "
            "turns multiplication into differentiation in s, so t·y'' gives a "
            "new differential equation rather than an equation to rearrange.",
            r"\mathcal{L}\{t\,f(t)\} = -F'(s)",
            "pitfall",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="What is L{y''} for an equation with y(0) = 2, y'(0) = 0 ?",
            options=(
                r"s^{2}Y(s)",
                r"s^{2}Y(s) - 2s",
                r"s^{2}Y(s) - 2",
                r"s^{2}Y(s) - 2s - 2",
            ),
            answer=1,
            becauses=(
                "s²Y alone is the transform of y'' only when both initial "
                "values are zero. Here y(0) = 2.",
                "s²Y − s·y(0) − y'(0) = s²Y − 2s − 0. The y(0) term carries "
                "the factor of s; it is y'(0) that does not. Swapping them "
                "is the usual slip.",
                "This attaches y(0) to the term with no s, which is where "
                "y'(0) goes. That is exactly the swap the rule is written to "
                "prevent.",
                "This subtracts something for y'(0) as well, but y'(0) = 0 "
                "here, so there is nothing to subtract for it.",
            ),
        ),
        Choice(
            key="q2",
            prompt="Which problem is the transform the *only* practical method "
                   "here for?",
            options=(
                "y' + 2y = 0, y(0) = 1",
                "y'' + y = cos t, at rest",
                "y' + y = u(t − 2), y(0) = 0",
                "t²y'' + ty' − y = 0",
            ),
            answer=2,
            becauses=(
                "This separates in one line. The transform works too, but it "
                "is not the only route, nor the shortest.",
                "This is exactly what undetermined coefficients is for — and "
                "it is the resonant case, which that method handles by "
                "multiplying the guess by t.",
                "A forcing term switched on at t = 2 has no shape to guess "
                "and does not separate, so undetermined coefficients and "
                "separation both fail. The transform takes it as one extra "
                "factor e^{−2s}. The others all have simpler routes.",
                "Variable coefficients turn the transform into a *differential* "
                "equation in s rather than an algebraic one. The transform is "
                "the wrong tool here, not the only one — this is Cauchy–Euler.",
            ),
        ),
        Solve(
            key="q3",
            prompt="Transform, solve for Y(s), invert.",
            equation="y'' + 4*y = 0",
            conditions="y(0) = 0, y'(0) = 2",
            hints=(
                "L{y''} = s²Y − s·y(0) − y'(0), and here that is s²Y − 2.",
                "So (s² + 4)Y = 2, giving Y = 2/(s² + 4).",
                "That is the row for sin bt with b = 2, on sight: y = sin 2t.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Needs partial fractions on the way back.",
            equation="y' + 2*y = t",
            conditions="y(0) = 0",
            hints=(
                "L{y'} = sY − y(0) = sY, and L{t} = 1/s².",
                "So (s + 2)Y = 1/s², giving Y = 1/(s²(s+2)).",
                "Split it into A/s + B/s² + C/(s+2) and read each row "
                "backwards.",
            ),
        ),
        Solve(
            key="q5",
            prompt="A switch thrown at t = 2. Type Heaviside(t-2) for the step.",
            equation="y' + y = Heaviside(t - 2)",
            conditions="y(0) = 0",
            hints=(
                "L{u(t−2)} = e^{−2s}/s. The delay is a factor, not something "
                "to expand.",
                "Y = e^{−2s}/(s(s+1)). Invert 1/(s(s+1)) first — it is "
                "1 − e^{−t}.",
                "Then shift it: multiply by u(t−2) and replace t by t−2, "
                "giving u(t−2)(1 − e^{−(t−2)}).",
            ),
        ),
    ),
    templates=(
        Template(
            key="first-order",
            title="Transform, solve for Y(s), split, invert",
            prompt="The routine case: it needs partial fractions coming back.",
            equation="y' + {a}*y = {b}*t",
            conditions="y(0) = {c}",
            narrator="laplace",
            hints=(
                "L{{y'}} = sY − y(0), and the forcing is a multiple of t, "
                "whose transform is that multiple over s².",
                "Collect the Y terms and solve for Y(s) — it is only algebra "
                "from here.",
                "Split Y into pieces in 1/s, 1/s² and 1/(s + {a}), then read "
                "each one backwards off the table.",
            ),
            slots=(("a", (1, 2, 3)), ("b", (1, 2, 3)), ("c", (0, 1))),
        ),
        Template(
            key="second-order",
            title="A second-order transform, conditions at the start",
            prompt="Both conditions enter through the transform of y''.",
            equation="y'' + {w2}*y = 0",
            conditions="y(0) = {p}, y'(0) = {v}",
            narrator="laplace",
            hints=(
                "L{{y''}} = s²Y − s·y(0) − y'(0). Put both conditions in, "
                "remembering that it is y(0) that carries the factor of s.",
                "Collect and solve for Y(s). It comes out as a sum of two "
                "rows of the table.",
                "s/(s² + w²) inverts to cos(wt) and w/(s² + w²) to sin(wt); "
                "here w² is the coefficient of y.",
            ),
            slots=(("w2", (1, 4, 9)), ("p", (0, 1)), ("v", (1, 2))),
        ),
    ),
)


TRANSFORM = Lesson(
    key="transform",
    title="The transform, and reading the table",
    summary="What the transform does to a function, and why the table is the "
            "only part you need to memorise.",
    tool="laplace",
    reference="Edwards 7.1",
    figure="transform_area",
    motivation=(
        "Every method so far has attacked the differential equation directly. "
        "There is a completely different strategy, and it is one used all "
        "over mathematics: if a problem is hard in the form it arrives in, "
        "move it somewhere it is easy, solve it there, and come back. "
        "Logarithms do this for multiplication — they turn products into "
        "sums, which are easier, and the exponential brings you home.\n\n"
        "The Laplace transform does it for differentiation. It converts a "
        "function of t into a function of a new variable, and under that "
        "conversion differentiating becomes *multiplying*. So a differential "
        "equation becomes an algebraic one, and algebra is something anyone "
        "can do. That is the entire proposition, and it rests on a single "
        "integration by parts carried out once and reused forever.\n\n"
        "The price is that you must be able to get back, and there is no "
        "formula for the return trip that is usable by hand. What is used "
        "instead is a table read in reverse — which is why this lesson spends "
        "as long on recognising a transform as on computing one, and why "
        "partial fractions matter so much later."
    ),
    derivation=(
        Passage(
            prose="The definition is an integral against a decaying exponential, over "
                  "all positive time. Nothing about it is obvious in advance; what "
                  "justifies it is what happens two passages from here.",
            latex=r"\mathcal{L}\{f\}(s) = F(s) = \int_0^{\infty} e^{-st}f(t)\,dt",
        ),
        Passage(
            prose="It is linear, because integration is. That is worth stating early "
                  "because it is doing most of the work in every problem: a transform "
                  "of a sum is a sum of transforms, and constants come straight out.",
            latex=r"\mathcal{L}\{af + bg\} = a\,\mathcal{L}\{f\} + b\,\mathcal{L}\{g\}",
        ),
        Passage(
            prose="Now the computation the whole method rests on. Transform a "
                  "*derivative* and integrate by parts: the derivative moves off f and "
                  "onto the exponential, which simply brings down a factor of s.",
            latex=r"\int_0^{\infty}e^{-st}f'(t)\,dt = "
                  r"\left[e^{-st}f(t)\right]_0^{\infty} + "
                  r"s\int_0^{\infty}e^{-st}f(t)\,dt",
        ),
        Passage(
            prose="Evaluate the boundary term. At infinity the exponential wins "
                  "provided f does not grow too fast, so that end contributes nothing; "
                  "at zero the exponential is one and what is left is the starting "
                  "value. Two things have happened at once — differentiation became "
                  "multiplication, and the initial condition arrived uninvited.",
            latex=r"\mathcal{L}\{f'\} = s\,F(s) - f(0)",
        ),
        Passage(
            prose="Apply the same result twice for a second derivative. The pattern is "
                  "the point: each derivative costs one factor of s and drags in one "
                  "more piece of initial data, which is exactly as much data as an "
                  "equation of that order needs.",
            latex=r"\mathcal{L}\{f''\} = s^{2}F(s) - s\,f(0) - f'(0)",
        ),
        Passage(
            prose="So a linear equation with constant coefficients transforms into an "
                  "algebraic equation for the transform of the answer, with the initial "
                  "conditions already inside it. Solving it is division. That is the "
                  "whole method, and everything after this is about getting back.",
            latex=r"P(s)\,Y(s) = F(s) + \left(\text{terms in } y(0),\, y'(0)\right)",
        ),
        Passage(
            prose="Getting back is the asymmetry. The inverse transform is a contour "
                  "integral in the complex plane and no help by hand, so in practice "
                  "the table is read from right to left: manipulate the answer until "
                  "each piece matches a row you recognise. That is why the table has to "
                  "be learned in *both* directions, and why a partial-fraction "
                  "decomposition is not algebra for its own sake — it is the act of "
                  "turning one unrecognisable expression into a sum of recognisable "
                  "ones.",
            latex=r"Y(s) = \frac{1}{s+2} - \frac{1}{s+3} \;\Longrightarrow\; y "
                  r"= e^{-2t} - e^{-3t}",
        ),
        Passage(
            prose="One limitation is built into the definition and is easy to overlook. "
                  "The integral runs from zero, so nothing before t = 0 is ever seen "
                  "and no answer produced this way makes any claim about negative time. "
                  "That is a genuine restriction, and it is also exactly right for the "
                  "problems the method is used on, which start when something is "
                  "switched on.",
            latex=r"t < 0 \text{ contributes nothing to } F(s)",
        ),
    ),
    prerequisites=("roots",),
    objectives=(
        "State the definition, and say what the integral converges for.",
        "Transform a constant, a power, an exponential and a sine from the "
        "definition or the table.",
        "Use linearity to transform a sum without integrating anything.",
        "Say what L{y'} is, and where the initial condition comes from.",
    ),
    examples=(
        Example(
            equation="y' + 2*y = 1",
            conditions="y(0) = 0",
            narrator="laplace",
            why="The smallest complete example: one derivative, a constant "
                "forcing term, and a single row of the table each way. Watch "
                "the initial condition enter at the transform rather than at "
                "the end.",
            commentary=(
                "Transform each of the three terms separately and notice that only "
                "one of them needs the result from the fourth passage. The rest is "
                "linearity moving constants around, which is why this problem is the "
                "right first one — the machinery is visible because there is so "
                "little of it.\n\n"
                "Then look at where the answer's two pieces come from. A constant "
                "forcing contributes a pole at zero, which inverts to a constant; the "
                "equation contributes a pole at minus two, which inverts to a "
                "decaying exponential. The first is the level the system settles at "
                "and the second is how it gets there — the steady state and the "
                "transient, arriving here as two rows of a table rather than as two "
                "integrals."
            ),
        ),
        Example(
            equation="y' + 3*y = exp(-t)",
            conditions="y(0) = 1",
            narrator="laplace",
            why="Two rows of the table and a non-zero starting value, so the "
                "y(0) term is actually carrying something. The answer needs "
                "partial fractions on the way back.",
            commentary=(
                "Here the starting value is not zero, so the term the integration by "
                "parts produced is actually carrying something. Watch it travel: it "
                "enters as a constant on the algebraic side, gets divided along with "
                "everything else, and lands in the answer as a contribution to one of "
                "the coefficients. Nothing was fitted at the end.\n\n"
                "Then watch the return trip need real work for the first time. What "
                "comes out of the division matches no row of the table, and splitting "
                "it into two pieces that do is the whole difficulty of the method in "
                "miniature. Notice that the two poles are at different places, so the "
                "split is the easy kind — a repeated pole would need a second term "
                "for the same factor, which is the case the shifting lesson deals "
                "with."
            ),
        ),
    ),
    notes=(
        Note(
            "The definition",
            "The transform multiplies a function by a decaying exponential "
            "and integrates it away to infinity, turning a function of t into "
            "a function of s. The integral converges once s is large enough, "
            "which is why every table row comes with a condition on s that "
            "nobody ever writes down after the first week.",
            r"\mathcal{L}\{f\}(s) = \int_0^{\infty} e^{-st} f(t)\,dt",
        ),
        Note(
            "Why it is worth doing",
            "Differentiating in t becomes multiplying by s. That single fact "
            "is the entire method: a differential equation in t becomes an "
            "algebraic equation in s, and the initial conditions arrive with "
            "it rather than waiting to be applied at the end.",
            r"\mathcal{L}\{y'\} = sY(s) - y(0), \qquad "
            r"\mathcal{L}\{y''\} = s^{2}Y(s) - s\,y(0) - y'(0)",
            "formula",
        ),
        Note(
            "It is linear, and that is most of the work",
            "The transform of a sum is the sum of the transforms, and "
            "constants come straight out. Almost every transform you will "
            "ever need is a table row or a linear combination of them — the "
            "definition is something you use to build the table, not to solve "
            "problems with.",
            r"\mathcal{L}\{af + bg\} = a\mathcal{L}\{f\} + b\mathcal{L}\{g\}",
            "formula",
        ),
        Note(
            "Only t ≥ 0 exists here",
            "The integral starts at zero, so the transform knows nothing "
            "about negative t and the answers it returns are only claims "
            "about t ≥ 0. This is why initial conditions must be given at "
            "t = 0 and nowhere else, and why the method suits problems that "
            "start when something is switched on.",
            r"t < 0 \ \text{is not described}",
            "pitfall",
        ),
        Note(
            "Read the table both ways",
            "Going forwards you look up f and write down F. Coming back you "
            "look up F and write down f, which is the harder direction and "
            "the one the algebra is arranged to make possible: every piece of "
            "Y(s) has to be manoeuvred into something that appears on the "
            "right-hand side of some row.",
            r"F(s) = \frac{b}{s^{2}+b^{2}} \;\Longrightarrow\; f(t) = \sin bt",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="What is L{e^{5t}}?",
            options=(
                r"1/(s+5)",
                r"1/(s-5)",
                r"5/(s^2+25)",
                r"s/(s^2-25)",
            ),
            answer=1,
            becauses=(
                "That is the transform of e^{−5t}. The sign flips: the pole "
                "sits at the exponential's own rate, so a growing exponential "
                "gives a pole on the positive side.",
                "L{e^{at}} = 1/(s − a) with a = 5. The integral converges only "
                "for s > 5, which is exactly where the pole is.",
                "That is the transform of sin 5t. An exponential gives a "
                "single pole, not a quadratic denominator.",
                "That is the transform of cosh 5t, which is the average of "
                "e^{5t} and e^{−5t} — related, but twice as much as asked "
                "for.",
            ),
        ),
        Choice(
            key="q2",
            prompt="Which fact makes the method worth using at all?",
            options=(
                "The transform of a product is the product of the transforms",
                "Differentiating in t becomes multiplying by s",
                "Every function has a transform",
                "The transform is its own inverse",
            ),
            answer=1,
            becauses=(
                "It is not — a product of transforms is a *convolution*, not "
                "a product, which is a later lesson and a much subtler fact.",
                "This is the whole idea. Derivatives become multiplication, so "
                "the differential equation collapses into algebra, and the "
                "initial conditions ride in on the derivative rule.",
                "Not every function does: it has to grow slower than some "
                "exponential for the integral to converge. e^{t²} has no "
                "transform.",
                "It is not. Going back requires the table read in reverse, and "
                "getting Y(s) into a form the table recognises is most of the "
                "work in every problem.",
            ),
        ),
        Choice(
            key="q3",
            prompt="L{y''} for a function with y(0) = 2 and y'(0) = −1 is…",
            options=(
                r"s^2 Y(s)",
                r"s^2 Y(s) - 2s + 1",
                r"s^2 Y(s) - 2s - 1",
                r"s^2 Y(s) - s + 2",
            ),
            answer=1,
            becauses=(
                "That is what you would get from rest. The initial values do "
                "not disappear — carrying them is the point of the rule.",
                "s²Y − s·y(0) − y'(0) = s²Y − 2s − (−1) = s²Y − 2s + 1. The "
                "y(0) term is the one that carries the factor of s.",
                "Close, but y'(0) = −1 and it enters with a minus sign, so "
                "the two negatives make a plus.",
                "The values have been swapped: it is y(0) that multiplies s, "
                "not y'(0).",
            ),
        ),
        Solve(
            key="q4",
            prompt="One derivative, constant forcing.",
            equation="y' + 2*y = 1",
            conditions="y(0) = 0",
            hints=(
                "Transform both sides: sY − y(0) + 2Y = 1/s, and y(0) = 0.",
                "Collect: (s + 2)Y = 1/s, so Y = 1/(s(s+2)).",
                "Split into A/s + B/(s+2) with A = 1/2 and B = −1/2, then "
                "invert each row.",
            ),
        ),
        Solve(
            key="q5",
            prompt="A non-zero starting value.",
            equation="y' + 3*y = exp(-t)",
            conditions="y(0) = 1",
            hints=(
                "L{e^{−t}} = 1/(s+1), and the y(0) = 1 rides in through "
                "L{y'} = sY − 1.",
                "Collect: (s + 3)Y = 1/(s+1) + 1, so Y = "
                "(s + 2)/((s+1)(s+3)).",
                "Partial fractions give 1/2 over each factor; both are "
                "exponential rows.",
            ),
        ),
        Choice(
            key="q-figure",
            prompt="In the figure, drag s downwards until it passes a. What "
                   "happens to the shaded area on the left, and to the curve "
                   "on the right?",
            figure="transform_area",
            options=(
                "The area stops being finite, and F(s) runs off to infinity "
                "at s = a and does not exist below it",
                "The area becomes negative, and F(s) is the negative value "
                "the right pane marks",
                "The area is unchanged; only the shape of the integrand moves",
                "The area goes to zero, because the two dashed curves cancel "
                "each other",
            ),
            answer=0,
            becauses=(
                "The integrand is e^{(a−s)t}. Above s = a the exponent is "
                "negative and the tail decays fast enough to have a finite "
                "area; at s = a it is the constant 1, whose area over an "
                "infinite interval is infinite. That is the region of "
                "convergence, and it is a place on the axis rather than a "
                "proviso in small print.",
                "The integrand is an exponential, which is positive "
                "everywhere, so the area under it can never be negative. The "
                "right pane is negative below the pole, but the transform is "
                "not defined there to be read.",
                "Changing s changes the weight e^{−st} that multiplies f, so "
                "it changes the integrand and therefore the area. That is "
                "precisely how F depends on s.",
                "They are two separate curves drawn for reference, not "
                "something being added. The shaded region is under their "
                "product, which is positive throughout.",
            ),
        ),
    ),
    templates=(
        Template(
            key="first-order-constant",
            title="Transform, solve, invert",
            prompt="One derivative and a constant. Every step is a table row.",
            equation="y' + {a}*y = {b}",
            conditions="y(0) = {c}",
            narrator="laplace",
            hints=(
                "Transform both sides. A constant b has transform b/s, and "
                "L{{y'}} = sY − y(0).",
                "Collect the Y terms and divide — this is the algebra the "
                "method exists to produce.",
                "Split into partial fractions over s and s + {a}, then read "
                "each piece backwards off the table.",
            ),
            slots=(("a", (1, 2, 3, 4)), ("b", (1, 2, 5)), ("c", (0, 1, 2))),
        ),
        ExpressionTemplate(
            key="the-transform",
            title="One step only: the transform of a forcing term",
            prompt="Write F(s) = ℒ{{f}} for   f(t) = {f}.   Give it in terms "
                   "of s.",
            answer="{answer}",
            because="Straight from the table, which is how this step is "
                    "meant to be done: the definition is an integral, and "
                    "the point of the table is never to compute it twice. "
                    "Each entry is worth recognising in both directions, "
                    "because the inverse transform at the end of the method "
                    "reads the same table backwards.",
            hints=(
                "This is a table lookup rather than an integral. Find the "
                "shape of f in the table first.",
                "An exponential shifts s; a power of t raises the power of s "
                "in the denominator; a sine or cosine puts a sum of squares "
                "there.",
                "If f is an exponential times something, transform the "
                "something and then replace s by s minus the rate in the "
                "exponential — that is the shifting rule.",
            ),
            slots=(("f,answer,tier", (
                ("exp(3*t)", "1/(s - 3)", "easier"),
                ("exp(-2*t)", "1/(s + 2)", "easier"),
                ("t", "1/s**2", "easier"),
                ("t**2", "2/s**3", "typical"),
                ("sin(2*t)", "2/(s**2 + 4)", "typical"),
                ("cos(3*t)", "s/(s**2 + 9)", "typical"),
                ("t*exp(2*t)", "1/(s - 2)**2", "harder"),
                ("exp(-t)*sin(3*t)", "3/((s + 1)**2 + 9)", "harder"),
                ("t**3", "6/s**4", "harder"),
            )),),
            level=lambda slots: slots["tier"],
        ),
    ),
)


SHIFTING = Lesson(
    key="shifting",
    title="Shifting theorems and partial fractions",
    summary="The two theorems that let the table cover far more than it "
            "lists, and the algebra that gets Y(s) into their shape.",
    tool="laplace",
    reference="Edwards 7.2–7.3",
    figure="poles",
    motivation=(
        "The method reduces every problem to the same final difficulty: an "
        "expression in s that has to be recognised as something on the table. "
        "The table is short, so almost nothing matches it directly, and the "
        "entire practical skill of this unit is turning what you have into "
        "what the table has.\n\n"
        "Two moves do nearly all of it. The first is a theorem that says "
        "multiplying by an exponential in t is the same as *sliding* along "
        "the s axis — so a table with four entries covers sixteen cases, "
        "since every entry can be shifted. The second is partial fractions, "
        "which is not really algebra practice at all but the act of breaking "
        "one unrecognisable expression into a sum of recognisable ones.\n\n"
        "There is also a trap worth naming in advance. There are two shifting "
        "theorems, they look alike written down, and they do opposite things: "
        "one shifts in s and one shifts in t. Confusing them is the single "
        "most common error in this unit, and the way to keep them apart is to "
        "remember which variable each one moves."
    ),
    derivation=(
        Passage(
            prose="Take the definition and multiply the function by an exponential "
                  "before transforming it. The two exponentials in the integral "
                  "combine, and what is left is the original integral with a different "
                  "value of s.",
            latex=r"\int_0^{\infty}e^{-st}e^{at}f(t)\,dt = \int_0^{\infty}e^{-(s-a)t}f(t)\,dt",
        ),
        Passage(
            prose="So multiplying by an exponential in t translates the transform along "
                  "the s axis. That is the first shifting theorem, it costs one line, "
                  "and it multiplies the reach of a short table enormously.",
            latex=r"\mathcal{L}\left\{e^{at}f(t)\right\} = F(s - a)",
        ),
        Passage(
            prose="Read it backwards and it becomes a recipe. Any transform in which s "
                  "appears only as a shifted combination is an exponential times "
                  "something simpler — so the task is to make the shift visible, and "
                  "for a quadratic denominator that means completing the square.",
            latex=r"\frac{1}{s^{2} + 2s + 5} = \frac{1}{(s+1)^{2} + 4}",
        ),
        Passage(
            prose="Which is exactly the damped oscillation of the vibrations unit, seen "
                  "from the other side. The amount of the shift is the decay rate and "
                  "what remains is the frequency — the real and imaginary parts of the "
                  "characteristic root, arriving as a translation rather than as a "
                  "root.",
            latex=r"\frac{2}{(s+1)^{2} + 4} \;\Longrightarrow\; e^{-t}\sin 2t",
        ),
        Passage(
            prose="When the denominator does factor, the job is different: split the "
                  "fraction into pieces the table knows. Each distinct linear factor "
                  "contributes one term, and matching numerators determines the "
                  "coefficients — a finite linear system, exactly as undetermined "
                  "coefficients was.",
            latex=r"\frac{1}{(s+1)(s+2)} = \frac{1}{s+1} - \frac{1}{s+2}",
        ),
        Passage(
            prose="A repeated factor needs a term for *each* power of it, and the "
                  "reason is a counting argument rather than a convention: a "
                  "denominator of degree n needs n coefficients to match against, and "
                  "one term per distinct factor would supply too few. The extra terms "
                  "invert to powers of t, which is the same factor of t that a repeated "
                  "characteristic root produced.",
            latex=r"\frac{1}{(s+1)^{2}} \;\Longrightarrow\; t\,e^{-t}",
        ),
        Passage(
            prose="Finally, the trap. The *second* shifting theorem concerns a delay in "
                  "t rather than a shift in s, and it produces an exponential factor in "
                  "front of the transform instead of a translation inside it. The two "
                  "are not variants of each other; they move different variables, and "
                  "the step-forcing lesson is about the other one.",
            latex=r"\mathcal{L}\left\{e^{at}f(t)\right\} = F(s-a) "
                  r"\quad\text{versus}\quad "
                  r"\mathcal{L}\left\{u(t-a)f(t-a)\right\} = e^{-as}F(s)",
        ),
    ),
    prerequisites=("laplace",),
    objectives=(
        "Apply the first shifting theorem: multiplying by e^{at} in t is "
        "replacing s by s − a.",
        "Complete the square to reach a shifted sine or cosine row.",
        "Split a rational Y(s) into partial fractions, including a repeated "
        "factor.",
        "Say what the second shifting theorem does, and when it applies.",
    ),
    examples=(
        Example(
            equation="y'' + 2*y' + 5*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            narrator="laplace",
            why="Completing the square turns s² + 2s + 5 into (s+1)² + 4, "
                "which is a shifted sine and cosine — the first shifting "
                "theorem doing exactly what it is for.",
            commentary=(
                "Complete the square on the denominator before doing anything else, "
                "and read the two numbers off: the amount of the shift and what is "
                "left underneath. Those are the real and imaginary parts of the "
                "characteristic root, so the answer's decay rate and frequency are "
                "available from the transform without inverting anything.\n\n"
                "Then watch the numerator have to be adjusted to match the table. It "
                "is rarely in the right form on its own, and forcing it there — "
                "adding and subtracting a multiple of the shift — is the fiddly part "
                "of this method. Compare the finished answer against what the "
                "characteristic roots would have given in the second-order unit: "
                "identical, which is the check worth doing at least once."
            ),
        ),
        Example(
            equation="y'' + 3*y' + 2*y = exp(-t)",
            conditions="y(0) = 0, y'(0) = 0",
            narrator="laplace",
            why="The forcing shares a root with the equation, so Y(s) has a "
                "repeated factor and the partial fractions bring in a term "
                "with t in front — resonance seen from the s side.",
            commentary=(
                "Factor the denominator and count the factors carefully, because one "
                "of them appears twice: the forcing contributes a pole that the "
                "equation already had. That coincidence is the whole content of this "
                "example, and it is visible in the transform long before any "
                "inversion.\n\n"
                "So the split needs two terms for that one factor, not one — and the "
                "second of them inverts to something with a t in front. That t is the "
                "resonance of the second-order unit seen from the s side: the same "
                "phenomenon, the same factor, arriving here as a counting fact about "
                "partial fractions rather than as a rule about trial forms."
            ),
        ),
    ),
    notes=(
        Note(
            "The first shifting theorem",
            "Multiplying a function by e^{at} shifts its transform sideways "
            "in s. Every row of the table therefore covers a whole family: "
            "you never need a row for e^{at}sin bt, because it is the sin row "
            "with s replaced by s − a.",
            r"\mathcal{L}\{e^{at}f(t)\} = F(s-a)",
            "formula",
        ),
        Note(
            "Complete the square to use it",
            "A quadratic denominator that does not factor is a shifted sine "
            "or cosine in disguise. Completing the square is how you find the "
            "shift: s² + 2s + 5 becomes (s+1)² + 4, so a = −1 and b = 2, and "
            "the answer is e^{−t} times an oscillation at frequency 2.",
            r"s^{2}+2s+5 = (s+1)^{2} + 2^{2}",
            "formula",
        ),
        Note(
            "Repeated factors need a term each",
            "A factor (s − a)² contributes both A/(s − a) and B/(s − a)², not "
            "just one of them. The second inverts to t·e^{at}, which is where "
            "the factor of t in a resonant answer comes from — the same t "
            "that the repeated characteristic root produced.",
            r"\frac{1}{(s-a)^{2}} \;\longrightarrow\; t\,e^{at}",
            "pitfall",
        ),
        Note(
            "The second shifting theorem is a different thing",
            "The first shifts in s and multiplies by an exponential in t; the "
            "second shifts in t and multiplies by an exponential in s. They "
            "are easy to confuse and do opposite jobs: the second is for "
            "forcing that switches on late, and it always brings a unit step "
            "with it.",
            r"\mathcal{L}\{u(t-a)g(t-a)\} = e^{-as}G(s)",
            "pitfall",
        ),
        Note(
            "Partial fractions exist only for this",
            "There is no other reason to break a rational function apart. "
            "Each piece has to match a row of the table, so the target shape "
            "is decided by what the table contains — which is why you aim for "
            "linear factors, repeated linear factors, and irreducible "
            "quadratics, and nothing else.",
            r"\frac{P(s)}{Q(s)} = \sum \frac{A_i}{(s-r_i)^{k}}",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="L{e^{-t} cos 3t} is…",
            options=(
                r"s/((s+1)^2+9)",
                r"(s+1)/((s+1)^2+9)",
                r"(s-1)/((s-1)^2+9)",
                r"3/((s+1)^2+9)",
            ),
            answer=1,
            becauses=(
                "The numerator has to shift too. The rule replaces *every* s "
                "in F(s) by s − a, not only the ones in the denominator.",
                "The cosine row is s/(s²+9); the first shifting theorem with "
                "a = −1 replaces s by s + 1 throughout, numerator included.",
                "The sign is wrong. e^{−t} means a = −1, so s becomes s + 1.",
                "That numerator belongs to the sine row. A cosine keeps the "
                "shifted s on top.",
            ),
        ),
        Choice(
            key="q2",
            prompt="Y(s) = 1/((s+2)^2). What is y(t)?",
            options=(
                r"e^{-2t}",
                r"t e^{-2t}",
                r"t^2 e^{-2t}",
                r"e^{-2t}/2",
            ),
            answer=1,
            becauses=(
                "That is 1/(s+2), the unsquared row. Squaring the denominator "
                "has to change the answer.",
                "1/s² inverts to t, and the shift by −2 multiplies by e^{−2t}. "
                "This is exactly the repeated-root case seen from the s side.",
                "t² would need 1/(s+2)³ — the power of t is one less than the "
                "power in the denominator.",
                "The factor of a half would come from 2/(s+2)² or similar; "
                "there is nothing here to produce it.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Why complete the square in s² + 4s + 13?",
            options=(
                "To factor it into linear pieces",
                "To reach a shifted sine or cosine row",
                "To make the numerator simpler",
                "To find the initial conditions",
            ),
            answer=1,
            becauses=(
                "It does not factor over the reals — its discriminant is "
                "16 − 52 < 0. That is precisely why completing the square is "
                "the move instead.",
                "(s+2)² + 9 matches the shifted sine and cosine rows with "
                "a = −2 and b = 3, giving e^{−2t}(C₁cos 3t + C₂sin 3t). The "
                "table has no row for an un-shifted irreducible quadratic.",
                "It usually makes the numerator more awkward, not less — you "
                "often have to add and subtract a constant to match the "
                "shifted numerator.",
                "The initial conditions went in long before this, at the "
                "transform step.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Completing the square.",
            equation="y'' + 2*y' + 5*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            hints=(
                "Transform: (s² + 2s + 5)Y = s·y(0) + y'(0) + 2y(0) = s + 2.",
                "s² + 2s + 5 = (s+1)² + 4, so Y = (s+2)/((s+1)²+4).",
                "Write the numerator as (s+1) + 1 to split it into a shifted "
                "cosine plus half a shifted sine.",
            ),
        ),
        Solve(
            key="q5",
            prompt="A repeated factor.",
            equation="y'' + 3*y' + 2*y = exp(-t)",
            conditions="y(0) = 0, y'(0) = 0",
            hints=(
                "(s² + 3s + 2)Y = 1/(s+1), and s² + 3s + 2 = (s+1)(s+2).",
                "So Y = 1/((s+1)²(s+2)) — the forcing shares the root at −1, "
                "which is what makes the factor repeat.",
                "Three terms: A/(s+1), B/(s+1)² and C/(s+2). The middle one is "
                "where the t·e^{−t} comes from.",
            ),
        ),
    ),
    templates=(
        Template(
            key="complete-the-square",
            title="An irreducible quadratic, from rest displaced",
            prompt="Transform, complete the square, split the numerator.",
            equation="y'' + {b}*y' + {c}*y = 0",
            conditions="y(0) = {p}, y'(0) = 0",
            narrator="laplace",
            hints=(
                "Transform both derivatives. With y'(0) = 0 the right-hand "
                "side is y(0)(s + {b}).",
                "The quadratic does not factor, so complete the square: it "
                "becomes (s + {b}/2)² plus a positive constant.",
                "Split the numerator so one piece matches the shifted cosine "
                "row and the rest is a multiple of the shifted sine row.",
            ),
            # Every pair has a negative discriminant, so completing the square
            # is always the move -- a draw that happened to factor would be
            # practising a different technique.
            slots=(
                ("b,c", ((2, 5), (2, 10), (4, 13), (2, 2), (6, 13), (4, 5))),
                ("p", (1, 2)),
            ),
        ),
    ),
)


CONVOLUTION = Lesson(
    key="convolution",
    title="Convolution",
    summary="What to do when Y(s) is a product that refuses to split.",
    tool="laplace",
    reference="Edwards 7.4",
    figure="convolution",
    motivation=(
        "Everything so far has relied on the transform of the answer being "
        "recognisable once it is split apart. That assumes the forcing has a "
        "transform on the table in the first place, and plenty of perfectly "
        "ordinary forcings do not: one over one plus t, or a measured signal "
        "with no formula at all.\n\n"
        "There is also a structural question that the partial-fraction "
        "machinery keeps hiding. The transform of the answer is a *product* — "
        "the forcing's transform times one over the characteristic polynomial "
        "— and the second factor has nothing to do with the forcing at all. "
        "It belongs to the system. It would be useful to know what that "
        "product means back in t, independently of what the forcing happens "
        "to be.\n\n"
        "It does not mean the product of the two functions, which is the "
        "first guess and is wrong. It means a particular integral of one "
        "against a reversed copy of the other, and that integral has a "
        "physical reading: the system's response now is everything the "
        "forcing did earlier, each part weighted by how long ago it happened."
    ),
    derivation=(
        Passage(
            prose="Start with the wrong guess, because it is worth killing explicitly. "
                  "The transform of a product is not the product of the transforms — "
                  "check it on any two table rows and the two sides disagree.",
            latex=r"\mathcal{L}\{fg\} \neq F(s)\,G(s)",
        ),
        Passage(
            prose="So ask the opposite question: given the product of two transforms, "
                  "what function of t is it the transform of? Write each factor as its "
                  "own integral and multiply. What appears is a double integral over "
                  "the whole positive quadrant, with the two exponentials combining "
                  "into one.",
            latex=r"F(s)G(s) = \int_0^{\infty}\!\!\int_0^{\infty} e^{-s(\tau + "
                  r"\sigma)}f(\tau)g(\sigma)\,d\tau\,d\sigma",
        ),
        Passage(
            prose="The exponent depends on the two variables only through their sum, so "
                  "change variables to that sum and one of the originals. The region "
                  "becomes a wedge — for each total time, the first variable runs from "
                  "zero up to it — and the integral over the wedge can be taken in the "
                  "other order.",
            latex=r"t = \tau + \sigma \;\Longrightarrow\; 0 \leq \tau \leq t",
        ),
        Passage(
            prose="Doing so puts the whole thing back in the shape of a transform: an "
                  "integral against a decaying exponential, of some inner integral in "
                  "t. That inner integral is the function whose transform is the "
                  "product — and it has a name.",
            latex=r"F(s)G(s) = \int_0^{\infty}e^{-st}\,h(t)\,dt, \qquad "
                  r"h(t) = \int_0^{t}f(\tau)\,g(t - \tau)\,d\tau",
        ),
        Passage(
            prose="That inner integral is the convolution. Note its shape: one function "
                  "runs forwards while the other runs backwards, and the two arguments "
                  "always sum to the current time.",
            latex=r"(f * g)(t) = \int_0^{t} f(\tau)\,g(t - \tau)\,d\tau",
        ),
        Passage(
            prose="Now use it on the transform of an answer. With zero initial "
                  "conditions, that transform is the forcing's transform divided by the "
                  "characteristic polynomial — a product of two things, one belonging "
                  "to the forcing and one to the system alone.",
            latex=r"Y(s) = \frac{1}{P(s)}F(s) = G(s)F(s)",
        ),
        Passage(
            prose="So the answer is the convolution of the forcing with one fixed "
                  "function of the system, and that function is what the system does "
                  "when struck once. Every response to every forcing is that single "
                  "response, smeared over the history of the input — which is why an "
                  "unevaluated convolution integral is a finished answer and not a "
                  "failure to finish.",
            latex=r"y = g * f, \qquad g = \mathcal{L}^{-1}\left\{\frac{1}{P(s)}\right\}",
        ),
    ),
    prerequisites=("shifting",),
    objectives=(
        "State the convolution theorem, and get the order of the arguments "
        "right.",
        "Recognise when partial fractions cannot help.",
        "Write the convolution integral for a forced system at rest.",
        "Identify the impulse response, and say what it means.",
    ),
    examples=(
        Example(
            equation="y'' + y = 1/(1+t)",
            conditions="y(0) = 0, y'(0) = 0",
            narrator="laplace",
            why="1/(1+t) has no tabulated transform, so there is nothing to "
                "split. The convolution integral is the answer — and this one "
                "happens to evaluate, into the sine and cosine integrals.",
            commentary=(
                "Find the system's own response first, before the forcing is "
                "considered at all. Invert one over the characteristic polynomial and "
                "what comes back is a sine — that is what this oscillator does when "
                "struck once, and it does not depend on what is driving it.\n\n"
                "Then check why nothing else in this unit could have started. The "
                "forcing has no transform on any table, so there is no expression in "
                "s to split and no rows to match; the convolution needs none of that, "
                "because it never transforms the forcing at all. The integral it "
                "produces happens to evaluate here, into functions with names of "
                "their own — but it would have been just as complete left as it "
                "stood."
            ),
        ),
        Example(
            equation="y'' + y = 1/(2+t)",
            conditions="y(0) = 0, y'(0) = 0",
            narrator="laplace",
            why="The same shape with the pole moved. Watch the impulse "
                "response sin t come out of the transfer function alone, "
                "before the forcing is involved at all.",
            commentary=(
                "Compare this with the previous example before working it, since only "
                "one thing differs. The equation is identical, so the function that "
                "comes out of the transfer function is identical too — the same sine, "
                "obtained the same way, and it would be the same for any forcing "
                "whatever.\n\n"
                "That is the observation the lesson is built on. Moving the pole "
                "changes the forcing and therefore the convolution integral, but not "
                "the thing it is convolved against. A system is characterised once, "
                "by what it does when struck, and after that every input is handled "
                "by the same integral with a different second factor."
            ),
        ),
    ),
    notes=(
        Note(
            "A product of transforms is not a product",
            "This is the fact the whole lesson exists to correct. The "
            "transform of a product of two functions is *not* the product of "
            "their transforms — but a product of transforms is the transform "
            "of something, and that something is the convolution.",
            r"\mathcal{L}\{f\}\mathcal{L}\{g\} = \mathcal{L}\{f * g\}",
            "formula",
        ),
        Note(
            "The convolution integral",
            "One function is reversed and slid across the other, and the "
            "overlap is integrated. The limits are 0 and t rather than the "
            "whole line, because both functions are zero before t = 0 — the "
            "transform only ever describes t ≥ 0.",
            r"(f * g)(t) = \int_0^{t} f(t-\tau)\,g(\tau)\,d\tau",
            "formula",
        ),
        Note(
            "The transfer function and the impulse response",
            "For a system at rest, Y(s) = G(s)F(s), where G is one over the "
            "characteristic polynomial. Its inverse g is the impulse "
            "response: what the system does when struck once. The convolution "
            "then says the output is that response smeared over the whole "
            "history of the input.",
            r"Y(s) = G(s)F(s), \quad G(s) = \frac{1}{P(s)} \;\Longrightarrow"
            r"\; y = g * f",
            "idea",
        ),
        Note(
            "An unevaluated integral is a finished answer",
            "Plenty of convolution integrals have no elementary closed form — "
            "e^{-t²} forcing is the standard example. Writing the integral "
            "down *is* the answer, and it can be differentiated, bounded and "
            "computed numerically. Waiting for it to simplify is waiting for "
            "something that is not going to happen.",
            r"y(t) = \int_0^{t} \sin(t-\tau)\,e^{-\tau^{2}}\,d\tau",
            "aside",
        ),
        Note(
            "Order matters less than it looks",
            "Convolution is commutative, so f * g and g * f are the same "
            "function — but only if you move the shift with the function. "
            "Writing f(t−τ)g(τ) and then integrating g(t−τ)f(τ) by mistake is "
            "the usual slip, and it gives a different integral.",
            r"f * g = g * f",
            "pitfall",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="L^{-1}{F(s)G(s)} is…",
            options=(
                r"f(t)g(t)",
                r"\int_0^t f(t-\tau)g(\tau)\,d\tau",
                r"\int_0^\infty f(\tau)g(\tau)\,d\tau",
                r"f(t) + g(t)",
            ),
            answer=1,
            becauses=(
                "This is the tempting answer and it is wrong. The transform "
                "is linear, not multiplicative — L{fg} has no simple form at "
                "all.",
                "The convolution: one function reversed and shifted, the other "
                "left alone, integrated over 0 to t. The limits come from both "
                "functions vanishing before t = 0.",
                "That is a number, not a function of t, so it cannot be the "
                "inverse transform of anything but a constant.",
                "A sum of transforms inverts to a sum of functions — that is "
                "linearity, and it is a different rule.",
            ),
        ),
        Choice(
            key="q2",
            prompt="For y'' + y = f(t) at rest, what is the impulse response?",
            options=(r"\cos t", r"\sin t", r"e^{-t}", r"t"),
            answer=1,
            becauses=(
                "cos t is the response to an initial displacement, not to an "
                "impulse. It has cos(0) = 1, whereas a system at rest struck "
                "at t = 0 must start from zero.",
                "G(s) = 1/(s²+1), whose inverse is sin t. It starts at zero "
                "and has slope 1 — precisely what a unit impulse delivers to a "
                "system at rest.",
                "That is the impulse response of y' + y, a first-order system. "
                "This one oscillates rather than decaying.",
                "t is the impulse response of y'' alone, with no restoring "
                "term to bring it back.",
            ),
        ),
        Choice(
            key="q3",
            prompt="When is convolution the right move rather than partial "
                   "fractions?",
            options=(
                "When Y(s) is a ratio of polynomials",
                "When the forcing has no tabulated transform to split",
                "Whenever there is a product anywhere",
                "When the initial conditions are non-zero",
            ),
            answer=1,
            becauses=(
                "A rational Y(s) always splits, and partial fractions is the "
                "faster and tidier route. Reach for convolution only when that "
                "one fails.",
                "e^{-t²}, 1/(1+t) and ln t have no rational transform, so "
                "there is nothing for partial fractions to break apart. The "
                "product structure is all you have left, and convolution is "
                "what reads it.",
                "Products of rational pieces are exactly what partial "
                "fractions handles. The presence of a product is not the "
                "signal — the absence of a split is.",
                "Non-zero conditions add polynomial terms and make Y(s) a sum "
                "rather than a single product, which is when convolution is "
                "*less* applicable, not more.",
            ),
        ),
        Solve(
            key="q4",
            prompt="No transform to look up.",
            equation="y'' + y = 1/(1+t)",
            conditions="y(0) = 0, y'(0) = 0",
            hints=(
                "Transform and solve: Y(s) = F(s)/(s²+1), where F is whatever "
                "the transform of 1/(1+t) happens to be. You will not need it.",
                "The first factor is the transfer function; its inverse is "
                "sin t, the impulse response.",
                "So y = ∫₀ᵗ sin(t−τ)/(1+τ) dτ. That integral does evaluate, "
                "into the sine and cosine integral functions.",
            ),
        ),
        Solve(
            key="q5",
            prompt="The same system, a different input.",
            equation="y'' + y = 1/(2+t)",
            conditions="y(0) = 0, y'(0) = 0",
            hints=(
                "The system has not changed, so neither has the impulse "
                "response: it is still sin t.",
                "Only the second factor of the convolution changes.",
                "y = ∫₀ᵗ sin(t−τ)/(2+τ) dτ.",
            ),
        ),
    ),
    templates=(
        NumericTemplate(
            key="step-response",
            title="A convolution evaluated",
            mistakes=(
                ("exp(-{a}*{t0})",
                 "the impulse response g({t0}) is given instead of its "
                 "running integral"),
                ("1 - exp(-{a}*{t0})",
                 "the integral of e^(−{a}t) loses its factor 1/{a}"),
            ),
            prompt="A system at rest has impulse response g(t) = e^(-{a}t). "
                   "Driven by a constant 1, its response is (1 * g)(t). What "
                   "is that at t = {t0}? Give four decimal places.",
            answer="(1 - exp(-{a}*{t0}))/{a}",
            tolerance=1e-4,
            because="Convolving with the constant 1 integrates g from 0 to t, "
                    "so the step response is the running total of the impulse "
                    "response — and it climbs towards the reciprocal of the "
                    "decay rate, which is where the system settles.",
            latex=r"(1 * g)(t) = \int_0^{{t}} g(\tau)\,d\tau",
            hints=(
                "One of the two factors is the constant 1, so the convolution "
                "integral loses that factor entirely.",
                "What is left is the integral of e^(-{a}τ) from 0 to {t0}.",
            ),
            slots=(("a", (0.5, 2, 3, 4)), ("t0", (0.5, 1, 2, 3))),
        ),
    ),
)


STEPFORCING = Lesson(
    key="step-forcing",
    title="Step functions and piecewise forcing",
    summary="Forcing that switches on partway through — the case no other "
            "technique in this course handles.",
    tool="laplace",
    reference="Edwards 7.5",
    figure="pulse_response",
    motivation=(
        "The transform's real advantage is forcing that no formula covers in "
        "one piece. A voltage switched on at two seconds, a load applied and "
        "removed, a valve opened: each is described by different expressions "
        "on different intervals, and every earlier method needs the problem "
        "cut into pieces and the pieces matched at the joins by hand.\n\n"
        "That matching is not a formality. Position and velocity have to "
        "agree across each join, which means solving one problem, evaluating "
        "it, using the values as initial conditions for the next, and "
        "repeating. With three switches there are four problems and three "
        "matchings, and every one is an opportunity to lose a sign.\n\n"
        "The transform does all of it at once, and the reason is that a "
        "switch has a perfectly ordinary transform. Once the unit step is "
        "available as a function rather than as a case distinction, a "
        "piecewise forcing is a single expression — and a single expression "
        "passes through the method without anything special happening to it."
    ),
    derivation=(
        Passage(
            prose="Define the switch as a function rather than as a case distinction: "
                  "zero before a given instant and one after it. Multiplying by it "
                  "turns anything on at that instant, and subtracting a later copy "
                  "turns it off again — so any piecewise-constant forcing is a "
                  "combination of these.",
            latex=r"u(t-a) = 0 \;\; (t < a), \qquad u(t-a) = 1 \;\; (t \geq a)",
        ),
        Passage(
            prose="Transform it straight from the definition. The step is zero over the "
                  "first part of the range, so the integral simply starts later, and "
                  "what comes out is the transform of the constant one with an "
                  "exponential in front.",
            latex=r"\mathcal{L}\{u(t-a)\} = \int_a^{\infty}e^{-st}\,dt = \frac{e^{-as}}{s}",
        ),
        Passage(
            prose="Now do the same for a whole function switched on and delayed. "
                  "Substituting for the shifted time turns the integral back into an "
                  "ordinary transform, and the shift comes out as a factor that does "
                  "not depend on the function at all.",
            latex=r"\int_a^{\infty}e^{-st}f(t-a)\,dt \;\;\left(\tau = t - "
                  r"a\right)\;\; = "
                  r"e^{-as}\int_0^{\infty}e^{-s\tau}f(\tau)\,d\tau",
        ),
        Passage(
            prose="That is the second shifting theorem: a delay in t becomes a factor "
                  "in s. Compare it with the first, which was a shift *inside* the "
                  "transform — these are different statements about different "
                  "variables, and this is the one that handles switches.",
            latex=r"\mathcal{L}\left\{u(t-a)f(t-a)\right\} = e^{-as}F(s)",
        ),
        Passage(
            prose="Using it in reverse is where care is needed, because the theorem is "
                  "about f(t − a) and not about f(t). Peel the exponential off, invert "
                  "what remains, and only then replace t by t − a *everywhere* in the "
                  "result — and attach the step, which is what makes the answer zero "
                  "beforehand.",
            latex=r"e^{-as}F(s) \;\Longrightarrow\; u(t-a)\,f(t-a)",
        ),
        Passage(
            prose="The step is not decoration. Without it the inverted expression would "
                  "claim a non-zero value before the switch was thrown, which is not "
                  "what the equation says: nothing has driven the system yet, so an "
                  "answer starting from rest must be identically zero there.",
            latex=r"t < a \;\Longrightarrow\; y(t) = 0",
        ),
        Passage(
            prose="And a pulse needs no new theory at all. On at one instant, off at "
                  "another, is one step minus another, and linearity carries both "
                  "through the method separately — so the answer is a difference of two "
                  "delayed responses, each switched on at its own time.",
            latex=r"u(t-1) - u(t-2) \;\Longrightarrow\; y_1(t)u(t-1) - y_1(t-1)u(t-2)",
        ),
    ),
    prerequisites=("shifting",),
    objectives=(
        "Write a piecewise forcing term as a combination of unit steps.",
        "Transform a delayed function using the second shifting theorem.",
        "Invert an e^{-as}G(s) term back into a switched-on response.",
        "Say why the answer is identically zero before the switch.",
    ),
    examples=(
        Example(
            equation="y' + y = Heaviside(t - 2)",
            conditions="y(0) = 0",
            narrator="laplace",
            why="The simplest switched problem: nothing happens until t = 2, "
                "and then the system starts climbing towards its new "
                "equilibrium. The Heaviside factor in the answer is what "
                "enforces the 'nothing happens' part.",
            commentary=(
                "Work out what the system settles at before solving. After the switch "
                "the equation is driven by a constant, so it climbs towards the value "
                "where the right-hand side balances — and that number can be read "
                "straight off the equation. The transform's job is only to say how it "
                "gets there and when it starts.\n\n"
                "Then check the answer at a time before the switch by substituting "
                "it. Every term carries the step factor, so the whole expression is "
                "zero, and that is a claim about physics rather than about notation: "
                "the system has not been touched yet. An answer that gave a non-zero "
                "value there would be wrong, and it is the commonest way this method "
                "is misapplied."
            ),
        ),
        Example(
            equation="y'' + 4*y = Heaviside(t - 1) - Heaviside(t - 2)",
            conditions="y(0) = 0, y'(0) = 0",
            narrator="laplace",
            why="A single pulse, on at t = 1 and off at t = 2, written as a "
                "difference of two steps. The system rings afterwards, "
                "because nothing removes the energy the pulse put in.",
            commentary=(
                "Read the forcing as two switches rather than as a pulse, because "
                "that is how the method sees it. Linearity then carries each through "
                "separately, so there are two delayed copies of the same response and "
                "the second is subtracted — which is what makes the driving stop.\n\n"
                "Then look at what happens after the second switch, where the forcing "
                "is back to nothing. The system does not return to rest: it keeps "
                "oscillating, because this equation has no damping term and nothing "
                "removes what the pulse deposited. Compare that with the first "
                "example, which settles — the difference is one term in the equation, "
                "and it is visible in the answer as the absence of any decaying "
                "factor."
            ),
        ),
    ),
    notes=(
        Note(
            "The unit step is a switch",
            "u(t − a) is zero before t = a and one after it. Multiplying by it "
            "turns anything on at t = a; subtracting a later step turns it off "
            "again. Any piecewise-constant forcing term can be built this way, "
            "and that is how it gets into the transform.",
            r"u(t-a) = 0 \;\; (t < a), \qquad "
            r"u(t-a) = 1 \;\; (t \geq a)",
        ),
        Note(
            "The second shifting theorem",
            "A delay in t becomes a factor of e^{-as} in s. That factor is "
            "never expanded and never split — it is peeled off, the rest is "
            "inverted, and the result is then shifted and switched on at "
            "t = a.",
            r"\mathcal{L}\{u(t-a)g(t-a)\} = e^{-as}G(s)",
            "formula",
        ),
        Note(
            "Shift the argument, not just the answer",
            "The theorem is about g(t − a), not g(t). Inverting e^{-as}G(s) "
            "to u(t − a)g(t) instead of u(t − a)g(t − a) is the standard "
            "mistake: it switches on at the right moment but starts from the "
            "wrong place, as though the system had been running all along.",
            r"e^{-as}G(s) \;\longrightarrow\; u(t-a)\,g(t-a)",
            "pitfall",
        ),
        Note(
            "Why no other technique here copes",
            "Undetermined coefficients needs a forcing term with a finite "
            "trial set, and a step has none. Variation of parameters would "
            "need the integral of a discontinuous function handled by cases. "
            "The transform absorbs the discontinuity into a single algebraic "
            "factor, which is the strongest argument for the method.",
            r"e^{-as}",
            "idea",
        ),
        Note(
            "The answer really is zero before the switch",
            "Every term in the solution carries its own u(t − a). Before the "
            "earliest switch, the whole expression is zero — not small, "
            "exactly zero — which is the correct answer for a system at rest "
            "that has not yet been disturbed.",
            r"y(t) = 0 \quad \text{for } t < a",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="How do you write 'zero until t = 3, then 5' with steps?",
            options=(
                r"5\,u(t-3)",
                r"u(5t-3)",
                r"5 - u(t-3)",
                r"5\,u(3-t)",
            ),
            answer=0,
            becauses=(
                "The step switches on at t = 3 and the 5 scales it. This is "
                "the whole idiom, and every piecewise forcing term is built "
                "from pieces of exactly this shape.",
                "Scaling inside the argument changes *when* it switches, not "
                "what it switches to — this one turns on at t = 3/5.",
                "That is 5 until t = 3 and 4 after it: a step down from a "
                "non-zero level, not a switch on from nothing.",
                "u(3 − t) is on *before* t = 3 and off after, which is the "
                "reverse of what was asked for.",
            ),
        ),
        Choice(
            key="q2",
            prompt="L^{-1}{e^{-3s}/(s+1)} is…",
            options=(
                r"u(t-3)e^{-t}",
                r"u(t-3)e^{-(t-3)}",
                r"e^{-3t}/(t+1)",
                r"e^{-(t+3)}",
            ),
            answer=1,
            becauses=(
                "The switch is in the right place but the function is not "
                "shifted with it, so it starts at e^{−3} instead of at 1. "
                "This is the standard slip.",
                "Peel off e^{−3s}, invert 1/(s+1) to e^{−t}, then shift the "
                "argument and switch it on: u(t−3)e^{−(t−3)}. It starts from "
                "1 at the moment it switches on.",
                "The delay factor has been treated as though it multiplied "
                "the answer rather than shifting it.",
                "There is no switch at all here, so the expression is non-zero "
                "before t = 3, where the answer must be zero.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Why can undetermined coefficients not handle u(t − 2)?",
            options=(
                "It is not differentiable at t = 2",
                "There is no finite family of functions to guess from",
                "It is not defined at t = 2",
                "Its transform does not exist",
            ),
            answer=1,
            becauses=(
                "True, but not the obstacle. Plenty of forcing terms that "
                "method does handle are perfectly smooth and still need a "
                "trial set; the issue is what the trial set would be.",
                "The technique guesses a combination of a finite list of "
                "functions closed under differentiation. A step has no such "
                "list — there is literally nothing to write down as a guess.",
                "It is defined everywhere; the convention at the jump makes no "
                "difference to the solution, because a single point cannot "
                "change an integral.",
                "It does exist — e^{-2s}/s — and that is precisely why this "
                "method works where the other does not.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Switched on at t = 2.",
            equation="y' + y = Heaviside(t - 2)",
            conditions="y(0) = 0",
            hints=(
                "L{u(t−2)} = e^{−2s}/s, so (s+1)Y = e^{−2s}/s.",
                "Y = e^{−2s}·1/(s(s+1)). Peel the exponential off and split "
                "the rest: 1/s − 1/(s+1).",
                "Invert to 1 − e^{−t}, then shift and switch on: "
                "y = u(t−2)(1 − e^{−(t−2)}).",
            ),
        ),
        Solve(
            key="q5",
            prompt="A pulse: on at 1, off at 2.",
            equation="y'' + 4*y = Heaviside(t - 1) - Heaviside(t - 2)",
            conditions="y(0) = 0, y'(0) = 0",
            hints=(
                "Two steps means two delay factors, and the equation is "
                "linear — handle each separately and subtract.",
                "For each, (s²+4)Y = e^{−as}/s, so peel off the exponential "
                "and split 1/(s(s²+4)).",
                "1/(s(s²+4)) inverts to (1 − cos 2t)/4; shift each copy to "
                "its own switch-on time.",
            ),
        ),
    ),
    # Multiple choice rather than a typed answer, and for the reason this
    # lesson is about: a switched answer substituted back leaves Heaviside and
    # delta terms that never cancel, so `check_answer` returns "cannot tell".
    # A verdict that can never be "right" cannot advance a streak.
    templates=(
        ChoiceTemplate(
            key="invert-a-delay",
            title="Peel off the delay, then shift",
            prompt="What is the inverse transform of "
                   "e^(-{a}s)/(s + {b})?",
            options=(
                "u(t-{a})·e^(-{b}(t-{a}))",
                "u(t-{a})·e^(-{b}t)",
                "e^(-{b}(t-{a}))",
                "u(t-{a})·e^(-{b}(t+{a}))",
            ),
            answer=0,
            becauses=(
                "Peel off the delay, invert what is left, then shift its "
                "argument and switch it on. It starts from 1 at t = {a}, "
                "which is what the second shifting theorem promises.",
                "The switch is in the right place but the function was not "
                "shifted with it, so it starts partway down its own decay "
                "instead of at 1. This is the standard slip.",
                "No switch at all, so this is non-zero before t = {a} — where "
                "a system at rest that has not yet been disturbed must be "
                "exactly zero.",
                "Shifted the wrong way. A delay moves the graph to the "
                "right, so the argument gains a minus, not a plus.",
            ),
            # Neither may be 1: `b` would render as "e^(-1(t-2))" and `a`
            # as "e^(-1s)", and both read as generated rather than written.
            slots=(("a", (2, 3, 4, 5)), ("b", (2, 3, 5))),
        ),
    ),
)


IMPULSES = Lesson(
    key="impulses",
    title="Impulses and the delta function",
    summary="A hammer blow: all the forcing delivered at a single instant, "
            "and what that does to a system.",
    tool="laplace",
    reference="Edwards 7.6",
    figure="impulse_limit",
    motivation=(
        "A pulse can be made shorter and taller at the same time. A hammer "
        "blow, a spark, a collision: each delivers its effect over an "
        "interval so brief that the interval itself is of no interest, and "
        "only the total effect matters. The natural thing to do is take the "
        "limit.\n\n"
        "The limit does not exist as a function, and that is not a "
        "technicality to be waved through. There is no function that is zero "
        "everywhere except one point and still has area one — the value at a "
        "single point cannot contribute anything to an integral. So whatever "
        "the delta is, it is not a function, and every manipulation of it "
        "needs a justification that is not the usual one.\n\n"
        "What makes it usable anyway is that it is only ever met *inside an "
        "integral*, and there its behaviour is perfectly definite: it picks "
        "out the value of whatever it is multiplied by at one instant. Treat "
        "that picking-out as the definition, forget the picture of an "
        "infinite spike, and the transform method absorbs it without "
        "difficulty."
    ),
    derivation=(
        Passage(
            prose="Start with an honest pulse: a rectangle of some short duration, "
                  "whose height is chosen so that the area is one. Whatever the "
                  "duration, the total impulse delivered is the same, and only the "
                  "duration is being sent to zero.",
            latex=r"p_\varepsilon(t) = \frac{1}{\varepsilon} \;\; (0 \leq t < "
                  r"\varepsilon), \qquad \int\, p_\varepsilon = 1",
        ),
        Passage(
            prose="Integrate it against a continuous function and let the duration "
                  "shrink. Over a shorter and shorter interval that function is more "
                  "and more nearly constant, so the integral tends to the function's "
                  "value at the instant — and it is this limit, not the pulse itself, "
                  "that survives.",
            latex=r"\int\, p_\varepsilon(t - a)\,f(t)\,dt \;\longrightarrow\; f(a)",
        ),
        Passage(
            prose="So *define* the delta by that behaviour rather than by a picture. It "
                  "is not a function that happens to be infinite somewhere; it is a "
                  "rule that assigns to each function its value at one point, and "
                  "everything below follows from this line alone.",
            latex=r"\int_{-\infty}^{\infty}\delta(t - a)\,f(t)\,dt = f(a)",
        ),
        Passage(
            prose="Its transform is then immediate, since transforming *is* integrating "
                  "against a function. No table row is needed and no limit has to be "
                  "taken a second time.",
            latex=r"\mathcal{L}\{\delta(t-a)\} = e^{-as}",
        ),
        Passage(
            prose="Which is as simple as a transform gets — for an impulse at time "
                  "zero, just one. An impulse is therefore the easiest forcing this "
                  "method handles, despite being the one that cannot be written as a "
                  "function at all.",
            latex=r"\mathcal{L}\{\delta(t)\} = 1",
        ),
        Passage(
            prose="Now what it does to a mechanical system. Integrate the equation "
                  "across the instant of the blow. The delta term contributes one; the "
                  "term in y contributes nothing, because y is bounded and the interval "
                  "is vanishing. What is left says the *velocity* jumps and the "
                  "position does not.",
            latex=r"\int_{a^-}^{a^+}\left(m y'' + k y\right)dt = 1 "
                  r"\;\Longrightarrow\; m\left[y'\right]_{a^-}^{a^+} = 1",
        ),
        Passage(
            prose="Which is exactly what a blow does physically — a struck object "
                  "leaves instantly with a velocity, from where it was standing. The "
                  "delta was an awkward object, and it has produced a completely "
                  "unsurprising answer, which is the best evidence that the definition "
                  "was the right one.",
            latex=r"y(a^+) = y(a^-), \qquad y'(a^+) = y'(a^-) + \frac{1}{m}",
        ),
        Passage(
            prose="One more consequence, and it is the reason impulses matter beyond "
                  "the exam. With zero conditions the transform of the answer is the "
                  "transfer function times one — so the response to an impulse *is* the "
                  "function the convolution lesson convolved everything against. Strike "
                  "a system once and you have characterised it for every input it will "
                  "ever see.",
            latex=r"\mathcal{L}\{\delta\} = 1 \;\Longrightarrow\; Y(s) = \frac{1}{P(s)} = G(s)",
        ),
    ),
    prerequisites=("step-forcing",),
    objectives=(
        "Say what δ(t − a) is, and what it is not.",
        "Transform an impulse, and explain why the answer is so simple.",
        "Solve an impulsively forced system at rest.",
        "Describe the jump an impulse produces in y'.",
    ),
    examples=(
        Example(
            equation="y'' + y = DiracDelta(t - 3)",
            conditions="y(0) = 0, y'(0) = 0",
            narrator="laplace",
            why="Nothing at all until t = 3, then a struck oscillator ringing "
                "forever at unit amplitude. The impulse response, delayed — "
                "which is what an impulse at t = 3 must produce.",
            commentary=(
                "Predict the answer from the sixth passage before reading the "
                "working. The system is at rest, the blow gives it a velocity and "
                "leaves its position alone, and after that nothing drives it — so "
                "what follows must be free oscillation started from zero displacement "
                "with a velocity, at the system's own frequency.\n\n"
                "Then notice what makes this the *impulse response*: the amplitude "
                "comes out at exactly the value the transfer function alone predicts, "
                "because the transform of the forcing was one. This answer is the "
                "function the convolution lesson used as its second factor, computed "
                "directly rather than inferred, and the delay is the exponential "
                "factor and nothing more."
            ),
        ),
        Example(
            equation="y'' + 2*y' + 2*y = DiracDelta(t - 1)",
            conditions="y(0) = 0, y'(0) = 0",
            narrator="laplace",
            why="The same blow to a damped system: it rings and dies away "
                "rather than ringing forever. Compare the two answers to see "
                "what the damping term is doing.",
            commentary=(
                "The blow is the same, so the difference between this answer and the "
                "previous one is entirely the system's doing. Look at the "
                "characteristic roots first: they are a complex pair with a negative "
                "real part, so whatever starts must decay, and the envelope's rate is "
                "fixed before the forcing is considered at all.\n\n"
                "Then compare the two answers as a pair, which is what this example "
                "is for. One rings forever and one dies away, and the term "
                "responsible is present in one equation and absent from the other. "
                "Both are the impulse response of their own system, so a single "
                "strike has characterised each of them — and the contrast shows what "
                "characterisation actually captures."
            ),
        ),
    ),
    notes=(
        Note(
            "It is not a function",
            "δ(t − a) is zero everywhere except one point, where it is not "
            "any number at all, and yet it integrates to one. No function "
            "does that. It is shorthand for a limit of taller and narrower "
            "pulses, and every statement about it is really a statement about "
            "that limit.",
            r"\int_{-\infty}^{\infty} \delta(t-a)\,dt = 1",
            "pitfall",
        ),
        Note(
            "The sifting property is the definition worth remembering",
            "Integrating anything against δ(t − a) picks out its value at a. "
            "Every fact about impulses follows from this, including the "
            "transform: put e^{-st} in as the anything.",
            r"\int_0^{\infty} f(t)\,\delta(t-a)\,dt = f(a)",
            "formula",
        ),
        Note(
            "Its transform is as simple as it gets",
            "By the sifting property the transform of δ(t − a) is just "
            "e^{-as}, with no 1/s. Compare the step, which has one: "
            "differentiating a step gives an impulse, and multiplying by s is "
            "what differentiating does in the s domain.",
            r"\mathcal{L}\{\delta(t-a)\} = e^{-as}",
            "formula",
        ),
        Note(
            "An impulse jumps the velocity, not the position",
            "For a second-order system, a unit impulse leaves y continuous "
            "and makes y' jump by 1/m instantly. That is what being struck "
            "means: the position cannot change in zero time, but the momentum "
            "can, and does.",
            r"y'(a^{+}) - y'(a^{-}) = \frac{1}{m}",
            "idea",
        ),
        Note(
            "The impulse response is the whole system",
            "The answer to an impulse at t = a is the impulse response, "
            "delayed to a. Since convolution builds every other response out "
            "of that same function, knowing how a system reacts to one blow "
            "tells you how it reacts to anything.",
            r"y = u(t-a)\,g(t-a)",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="What is L{δ(t − 4)}?",
            options=(r"e^{-4s}/s", r"e^{-4s}", r"4e^{-s}", r"1/s"),
            answer=1,
            becauses=(
                "That is the transform of the *step* u(t − 4). The extra 1/s "
                "is exactly the difference between a switch and a blow.",
                "By the sifting property, integrating e^{−st} against "
                "δ(t − 4) picks out e^{−4s}. No 1/s, which is why impulsive "
                "problems are algebraically the easiest of all.",
                "The delay belongs in the exponent, not as a factor in front. "
                "A unit impulse carries unit strength wherever it lands.",
                "That is the transform of the constant 1. An impulse is "
                "concentrated at one instant, not spread over all time.",
            ),
        ),
        Choice(
            key="q2",
            prompt="An oscillator at rest is struck at t = 5. Just after, …",
            options=(
                "y jumps and y' is unchanged",
                "y' jumps and y is unchanged",
                "both jump",
                "neither jumps; both ramp up smoothly",
            ),
            answer=1,
            becauses=(
                "Position cannot change in zero time — that would need "
                "infinite velocity, and the impulse only supplies finite "
                "momentum.",
                "A blow delivers momentum instantly, so the velocity jumps "
                "while the position is still where it was. This is why the "
                "answer starts from zero at t = 5 and rises with slope 1.",
                "If y jumped too, y' would contain an impulse of its own and "
                "y'' a derivative of one — the equation would not balance.",
                "Something does jump: an impulse is precisely a discontinuous "
                "change in the state, which is what distinguishes it from a "
                "step in the forcing.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Why does the app show an impulsive answer unchecked?",
            options=(
                "The answer is a guess",
                "Substituting it back leaves impulse terms that never cancel",
                "Impulses have no transform",
                "The answer has no closed form",
            ),
            answer=1,
            becauses=(
                "It is not a guess — it comes out of the same transform "
                "machinery as every other answer on this screen.",
                "Checking works by substituting and simplifying to zero, and a "
                "switched answer differentiated twice produces δ terms sympy "
                "will not cancel. δ also has no numerical value to compare "
                "against, so the app says so rather than claiming either way.",
                "It has the simplest transform in the table, e^{-as}, which "
                "is what makes these problems easy in the first place.",
                "It has a perfectly good closed form — the impulse response, "
                "delayed and switched on.",
            ),
        ),
        Solve(
            key="q4",
            prompt="An undamped oscillator, struck once.",
            equation="y'' + y = DiracDelta(t - 3)",
            conditions="y(0) = 0, y'(0) = 0",
            hints=(
                "L{δ(t−3)} = e^{−3s}, so (s²+1)Y = e^{−3s} with no 1/s.",
                "Y = e^{−3s}/(s²+1). Peel off the delay; 1/(s²+1) inverts to "
                "sin t.",
                "Shift and switch on: y = u(t−3)sin(t−3). It rings forever, "
                "because nothing is removing the energy.",
            ),
        ),
        Solve(
            key="q5",
            prompt="The same blow, this time damped.",
            equation="y'' + 2*y' + 2*y = DiracDelta(t - 1)",
            conditions="y(0) = 0, y'(0) = 0",
            hints=(
                "(s² + 2s + 2)Y = e^{−s}, with no 1/s — an impulse never "
                "brings one.",
                "Complete the square: s² + 2s + 2 = (s+1)² + 1, so the "
                "impulse response is e^{−t}sin t.",
                "Shift it to t = 1: y = u(t−1)e^{−(t−1)}sin(t−1). Compare with "
                "the undamped case — the ringing now dies away.",
            ),
        ),
    ),
    # Multiple choice for the same reason as `step-forcing`, and one more: an
    # impulsive answer cannot be checked numerically either, since DiracDelta
    # does not lambdify. The narrator shows those unchecked, which is honest
    # and is not something a drill can grade.
    templates=(
        ChoiceTemplate(
            key="impulse-transform",
            title="The impulse against the step",
            prompt="What is the Laplace transform of delta(t - {a})?",
            options=(
                "e^(-{a}s)",
                "e^(-{a}s)/s",
                "{a}·e^(-s)",
                "1/s",
            ),
            answer=0,
            becauses=(
                "By the sifting property, integrating e^(-st) against the "
                "impulse picks out its value at t = {a}. No 1/s, which is "
                "what makes impulsive problems the algebraically easiest of "
                "all.",
                "That is the transform of the *step* u(t - {a}). The extra "
                "1/s is exactly the difference between a switch and a blow — "
                "differentiating a step gives an impulse, and multiplying by "
                "s is what differentiating does here.",
                "The delay belongs in the exponent, not as a factor in front. "
                "A unit impulse carries unit strength wherever it lands.",
                "That is the transform of the constant 1, which is spread "
                "over all time. An impulse is concentrated at one instant.",
            ),
            # `a` avoids 1, which would render as "1·e^(-s)" in the third
            # option and read as generated.
            slots=(("a", (2, 3, 4, 5, 6, 7)),),
        ),
    ),
)


LESSONS = (TRANSFORM, LAPLACE, SHIFTING, CONVOLUTION, STEPFORCING,
           IMPULSES)
