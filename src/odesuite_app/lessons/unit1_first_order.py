"""Unit 1 -- First-order equations.

Edwards, Penney and Calvis 6e, chapter 1. The two techniques a course meets
first, and the two it falls back on for the rest of the term.

Four further lessons belong here -- what a differential equation is, slope
fields and uniqueness, exact equations, and the substitutions -- and arrive
with the narrators that can work them.
"""

from __future__ import annotations

from .model import Choice, Example, Lesson, Note, Solve

__all__ = ["SEPARABLE", "LINEAR", "LESSONS"]


SEPARABLE = Lesson(
    key="separable",
    title="Separable equations",
    summary="The first technique, and the one every other first-order method "
            "falls back on when it can.",
    tool="steps",
    reference="Edwards 1.4",
    objectives=(
        "Decide whether an equation separates, by looking for a product.",
        "Carry out the separation and integrate both sides.",
        "Apply an initial condition, and pick the right branch when "
        "rearranging gives two.",
        "Name the constant solutions the method loses, and say why it loses "
        "them.",
    ),
    examples=(
        Example(
            equation="y' = y*(1 - y)",
            conditions="y(0) = 0.1",
            why="The logistic equation — the standard case, and one whose two "
                "equilibria are exactly what separating divides away.",
        ),
        Example(
            equation="y' = y**2",
            conditions="y(0) = 1",
            why="Nothing about this equation looks dangerous, and yet the "
                "solution runs to infinity at t = 1. Separating finds that; "
                "the equation itself never says so.",
        ),
    ),
    notes=(
        Note(
            "What makes an equation separable",
            "An equation is separable when the right-hand side factors into "
            "something in t times something in y. Nothing mixed: no t + y, no "
            "sin(t + y). If you can pull the two variables apart into separate "
            "factors, you can pull them apart into separate integrals.",
            r"\frac{dy}{dt} = f(t)\,g(y)",
        ),
        Note(
            "The move",
            "Divide by g(y), multiply by dt, and integrate both sides. The dy "
            "and dt are being handled loosely here, and that is fine — it is "
            "shorthand for the chain rule, and it gives the right answer for "
            "the right reason.",
            r"\int \frac{dy}{g(y)} = \int f(t)\,dt",
        ),
        Note(
            "One constant, not two",
            "Both integrals produce a constant, but their difference is just "
            "another constant, so only one is written. Add it on the t side by "
            "convention and solve for y afterwards.",
            r"G(y) = F(t) + C",
            "formula",
        ),
        Note(
            "The step that can lose a solution",
            "Dividing by g(y) assumes g(y) is not zero. Wherever g(y₀) = 0, the "
            "constant function y = y₀ solves the equation on its own — an "
            "equilibrium. The logistic equation has two, y = 0 and y = 1, and "
            "neither comes out of the general formula.",
            r"g(y_0) = 0 \;\Longrightarrow\; y \equiv y_0 \text{ is a solution}",
            "pitfall",
        ),
        Note(
            "Rearranging can give two branches",
            "Solving y²/2 = t²/2 + C for y gives ±√(t² + 2C), and only one of "
            "those passes through the point you were given. Both satisfy the "
            "equation, so substituting will not tell you which — the initial "
            "condition is the only thing that does.",
            r"y^{2} = t^{2} + C \;\Longrightarrow\; y = \pm\sqrt{t^{2} + C}",
            "pitfall",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="Which of these is separable?",
            options=(
                "y' = t + y",
                "y' = t·y²",
                "y' = sin(t + y)",
                "y' = (t + y)/(t − y)",
            ),
            answer=1,
            becauses=(
                "A sum is not a product. There is no f and g with "
                "f(t)·g(y) = t + y — set t = 0, then y = 0, and the two factors "
                "are forced into a contradiction.",
                "t·y² is a function of t times a function of y, which is "
                "exactly the test. Divide by y², multiply by dt, and the "
                "variables are apart.",
                "Both variables are locked inside one function. sin(t)·sin(y) "
                "would separate; sin(t + y) does not, and no identity turns one "
                "into the other.",
                "A quotient can separate — y' = t/y does — but only when the "
                "numerator and denominator each involve one variable. Here both "
                "mix t and y, and dividing does not undo that.",
            ),
        ),
        Solve(
            key="q2",
            prompt="Solve it, and apply the condition.",
            equation="y' = 2*t*y",
            conditions="y(0) = 1",
            hints=(
                "The right-hand side is already a product: 2t times y.",
                "Separate to dy/y = 2t dt. The left integrates to ln|y|, the "
                "right to t².",
                "ln|y| = t² + C, so y = Ae^{t²}, and y(0) = 1 makes A = 1.",
            ),
        ),
        Solve(
            key="q3",
            prompt="Newton's cooling: coffee at 95 °C in a 20 °C room.",
            equation="y' = -0.2*(y - 20)",
            conditions="y(0) = 95",
            hints=(
                "The right-hand side involves y alone, so it separates with "
                "f(t) = 1.",
                "Separate to dy/(y − 20) = −0.2 dt. The 20 does not go away; "
                "it is what the answer decays towards.",
                "ln|y − 20| = −0.2t + C, so y = 20 + Ae^{−0.2t}, and A = 75.",
            ),
        ),
        Choice(
            key="q4",
            prompt="For y' = y(1 − y), which constant functions are solutions?",
            latex=r"y' = y(1-y)",
            options=(
                "Only y = 0",
                "Only y = 1",
                "Both y = 0 and y = 1",
                "None — every solution changes with t",
            ),
            answer=2,
            becauses=(
                "y = 0 does give y' = 0, but it is not the only one: "
                "y(1 − y) = 0 has a second root.",
                "y = 1 does give y' = 0, but so does y = 0. This equation has "
                "two equilibria, not one.",
                "Setting y' = 0 needs y(1 − y) = 0, so y = 0 or y = 1. These "
                "are exactly the values you divided by when separating, which "
                "is why they are not in the general answer.",
                "Constant solutions are exactly where the right-hand side "
                "vanishes, and y(1 − y) = 0 has two roots. They are easy to "
                "miss precisely because separating throws them away.",
            ),
        ),
        Solve(
            key="q5",
            prompt="A harder separation — the answer is not an exponential.",
            equation="y' = t/y",
            conditions="y(0) = 2",
            hints=(
                "t/y is t times 1/y — a product, so it separates.",
                "Separating gives y dy = t dt. Both sides integrate to squares.",
                "y²/2 = t²/2 + C gives y² = t² + 4. Take the positive root: "
                "y(0) = 2 sits on that branch, and the negative one passes "
                "through no point the condition allows.",
            ),
        ),
    ),
)


LINEAR = Lesson(
    key="linear",
    title="First-order linear, and the integrating factor",
    summary="What to do when the equation is linear in y but refuses to "
            "separate.",
    tool="steps",
    reference="Edwards 1.5",
    prerequisites=("separable",),
    objectives=(
        "Put a first-order equation in standard form and read off p and q.",
        "Build the integrating factor, and say what property makes it work.",
        "Recognise the left side as a product-rule derivative and integrate it.",
        "Tell linear from nonlinear when the coefficients depend on t.",
    ),
    examples=(
        Example(
            equation="y' + 2*y = t",
            why="Constant p, polynomial forcing — the case to watch the "
                "machinery on before the coefficients start moving.",
        ),
        Example(
            equation="t*y' + y = t",
            conditions="y(1) = 1",
            why="p(t) = 1/t is not constant, which is what the method is "
                "actually for — and the left side was already a product-rule "
                "derivative before anything was multiplied by anything.",
        ),
    ),
    notes=(
        Note(
            "Standard form first",
            "The technique needs the equation in exactly this shape: y' alone, "
            "coefficient 1, everything else arranged around it. If y' has a "
            "coefficient, divide the whole equation by it before doing anything "
            "else.",
            r"y' + p(t)\,y = q(t)",
        ),
        Note(
            "The trick",
            "Multiply through by μ = e^{∫p dt}. This is chosen so that μ′ = pμ, "
            "and that single property is the entire method — it makes the left "
            "side an exact derivative.",
            r"\mu(t) = e^{\int p(t)\,dt}, \qquad \mu' = p\,\mu",
            "formula",
        ),
        Note(
            "Why it works",
            "After multiplying, the left side is μy′ + pμy, which by the "
            "product rule is exactly (μy)′. An expression you could not "
            "integrate has become one you can integrate by inspection.",
            r"\mu y' + p\mu y = (\mu y)' = \mu q",
        ),
        Note(
            "Then it is just integration",
            "Integrate both sides and divide by μ. The constant of integration "
            "enters before the division, so it gets divided by μ too — which is "
            "why the answer usually has a decaying factor multiplying C.",
            r"y = \frac{1}{\mu}\left(\int \mu q\,dt + C\right)",
            "formula",
        ),
        Note(
            "Divide first, or p is wrong",
            "Reading p straight off an equation whose y′ still carries a "
            "coefficient is the mistake this topic produces. In t·y′ + y = t, "
            "p is 1/t and not 1 — and a wrong p gives a wrong μ, which leaves "
            "the left side not the derivative of anything.",
            r"t y' + y = t \;\Longrightarrow\; y' + \tfrac{1}{t}\,y = 1",
            "pitfall",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="What is the integrating factor for y' + 3y = e^t ?",
            latex=r"y' + 3y = e^{t}",
            options=(r"e^{3t}", r"e^{-3t}", r"3e^{t}", r"e^{t^{2}/2}"),
            answer=0,
            becauses=(
                "p(t) = 3, so μ = e^{∫3 dt} = e^{3t}. It is the coefficient of "
                "y that decides μ, and nothing else in the equation does.",
                "That is 1/μ. The sign trips people up: μ uses +∫p, and the "
                "decay appears later, when you divide by μ.",
                "This is built from the forcing term. The forcing plays no part "
                "in choosing μ — only p does.",
                "e^{t²/2} would be right if p(t) were t. Here p is the constant "
                "3, so ∫p dt is 3t.",
            ),
        ),
        Choice(
            key="q2",
            prompt="Which equation is NOT first-order linear?",
            options=(
                "y' + t·y = t",
                "t·y' + y = sin t",
                "y' + y² = t",
                "y' − y/t = t²",
            ),
            answer=2,
            becauses=(
                "This is linear. y and y′ each appear to the first power; the "
                "coefficient t multiplies y, which is allowed.",
                "This is linear too — divide by t and it is in standard form "
                "with p = 1/t. A coefficient on y′ does not break linearity.",
                "Linear means linear in y and y′ — each appearing to the first "
                "power and not multiplied together. y² breaks that. "
                "Coefficients may depend on t however they like.",
                "This is linear, with p(t) = −1/t. Dividing y by t is still "
                "linear in y; it is y itself that must stay to the first power.",
            ),
        ),
        Solve(
            key="q3",
            prompt="Standard form, integrating factor, integrate.",
            equation="y' + y = t",
            conditions="y(0) = 0",
            hints=(
                "It is already in standard form, with p = 1 and q = t.",
                "μ = e^{∫1 dt} = e^t, so the left side becomes (e^t·y)′.",
                "∫t·e^t dt needs integration by parts: it is (t − 1)e^t. "
                "Divide by e^t and apply y(0) = 0.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Here p(t) is not constant, which is what the method is for.",
            equation="t*y' + y = t",
            conditions="y(1) = 1",
            hints=(
                "Divide by t first — otherwise p is read wrong. That gives "
                "p = 1/t.",
                "μ = e^{∫dt/t} = t, which is what was already multiplying y′. "
                "Sometimes μ is staring at you.",
                "(t·y)′ = t, so t·y = t²/2 + C, and y(1) = 1 gives C = 1/2.",
            ),
        ),
        Solve(
            key="q5",
            prompt="A mixing tank: 100 litres, 5 l/min in at 0.4 kg/l, "
                   "well stirred, same rate out.",
            equation="y' = 2 - 0.05*y",
            conditions="y(0) = 5",
            hints=(
                "Rearrange to y′ + 0.05y = 2, so that p and q are visible.",
                "μ = e^{0.05t}. Before solving, note where it must end up: "
                "y′ = 0 gives y = 40.",
                "y = 40 + Ae^{−0.05t}, and y(0) = 5 gives A = −35.",
            ),
        ),
    ),
)


LESSONS = (SEPARABLE, LINEAR)
