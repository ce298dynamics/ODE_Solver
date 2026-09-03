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
    Lesson,
    Note,
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
        ),
        Example(
            equation="y' + y = Heaviside(t - 2)",
            conditions="y(0) = 0",
            narrator="laplace",
            why="A switch thrown at two seconds. Not separable, no integrating "
                "factor worth writing, and not what undetermined coefficients "
                "is for — this is the problem the transform exists for.",
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
        ),
        Example(
            equation="y' + 3*y = exp(-t)",
            conditions="y(0) = 1",
            narrator="laplace",
            why="Two rows of the table and a non-zero starting value, so the "
                "y(0) term is actually carrying something. The answer needs "
                "partial fractions on the way back.",
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
    ),
)


SHIFTING = Lesson(
    key="shifting",
    title="Shifting theorems and partial fractions",
    summary="The two theorems that let the table cover far more than it "
            "lists, and the algebra that gets Y(s) into their shape.",
    tool="laplace",
    reference="Edwards 7.2–7.3",
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
        ),
        Example(
            equation="y'' + 3*y' + 2*y = exp(-t)",
            conditions="y(0) = 0, y'(0) = 0",
            narrator="laplace",
            why="The forcing shares a root with the equation, so Y(s) has a "
                "repeated factor and the partial fractions bring in a term "
                "with t in front — resonance seen from the s side.",
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
        ),
        Example(
            equation="y'' + y = 1/(2+t)",
            conditions="y(0) = 0, y'(0) = 0",
            narrator="laplace",
            why="The same shape with the pole moved. Watch the impulse "
                "response sin t come out of the transfer function alone, "
                "before the forcing is involved at all.",
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
            r"Y(s) = \underbrace{\frac{1}{P(s)}}_{G(s)}F(s) \;\Longrightarrow"
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
)


STEPFORCING = Lesson(
    key="step-forcing",
    title="Step functions and piecewise forcing",
    summary="Forcing that switches on partway through — the case no other "
            "technique in this course handles.",
    tool="laplace",
    reference="Edwards 7.5",
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
        ),
        Example(
            equation="y'' + 4*y = Heaviside(t - 1) - Heaviside(t - 2)",
            conditions="y(0) = 0, y'(0) = 0",
            narrator="laplace",
            why="A single pulse, on at t = 1 and off at t = 2, written as a "
                "difference of two steps. The system rings afterwards, "
                "because nothing removes the energy the pulse put in.",
        ),
    ),
    notes=(
        Note(
            "The unit step is a switch",
            "u(t − a) is zero before t = a and one after it. Multiplying by it "
            "turns anything on at t = a; subtracting a later step turns it off "
            "again. Any piecewise-constant forcing term can be built this way, "
            "and that is how it gets into the transform.",
            r"u(t-a) = \begin{cases} 0 & t < a \\ 1 & t \ge a \end{cases}",
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
        ),
        Example(
            equation="y'' + 2*y' + 2*y = DiracDelta(t - 1)",
            conditions="y(0) = 0, y'(0) = 0",
            narrator="laplace",
            why="The same blow to a damped system: it rings and dies away "
                "rather than ringing forever. Compare the two answers to see "
                "what the damping term is doing.",
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
