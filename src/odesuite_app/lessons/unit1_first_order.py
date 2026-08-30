"""Unit 1 -- First-order equations.

Edwards, Penney and Calvis 6e, chapter 1. The two techniques a course meets
first, and the two it falls back on for the rest of the term.

Six lessons: what a differential equation is, reading one off a slope field,
and the four techniques a first course solves them with.
"""

from __future__ import annotations

from .model import Choice, Example, Lesson, Note, Solve, Template

__all__ = ["BASICS", "SLOPEFIELDS", "SEPARABLE", "LINEAR",
           "EXACT", "SUBSTITUTIONS", "LESSONS"]


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
    templates=(
        Template(
            key="growth",
            title="Separate, integrate, apply the condition",
            prompt="Separate it, integrate both sides, and use the condition.",
            equation="y' = {a}*t**{k}*y",
            conditions="y(0) = {c}",
            technique="separable",
            hints=(
                "Everything in t sits in one factor and everything in y "
                "in the other, so it separates.",
                "Divide by y and multiply by dt. The left side integrates to "
                "ln|y|; integrate the t side as a power.",
                "Exponentiate both sides, then y(0) = {c} fixes the constant "
                "multiplying the exponential.",
            ),
            slots=(("a", (1, 2, 3)), ("k", (0, 1, 2)), ("c", (1, 2))),
        ),
        Template(
            key="cooling",
            title="A decay towards an equilibrium",
            prompt="Solve it, and check the answer settles where it should.",
            equation="y' = -{a}*(y - {b})",
            conditions="y(0) = {c}",
            technique="separable",
            hints=(
                "Setting y' = 0 gives y = {b}. That is where the answer must "
                "end up, whatever else happens.",
                "Separate to dy/(y − {b}) = −{a} dt; the left integrates to "
                "ln|y − {b}|.",
                "The answer is {b} plus a decaying exponential, and "
                "y(0) = {c} fixes the coefficient in front of it.",
            ),
            slots=(("a", (1, 2, 3)), ("b", (5, 10, 20)), ("c", (0, 30, 50))),
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
    templates=(
        Template(
            key="constant-p",
            title="Constant p, polynomial forcing",
            prompt="Standard form, integrating factor, integrate, divide.",
            equation="y' + {a}*y = {b}*t",
            conditions="y(0) = {c}",
            technique="1st_linear",
            hints=(
                "It is already in standard form, with p = {a} and a "
                "forcing term that is a multiple of t.",
                "μ = e^(pt) with p = {a}, which turns the left side into "
                "the derivative of a single product.",
                "The integral on the right needs integration by parts. Divide "
                "by μ at the end, and the constant comes with it.",
            ),
            slots=(("a", (1, 2, 3)), ("b", (1, 2, 3)), ("c", (0, 1))),
        ),
        Template(
            key="variable-p",
            title="p is not constant — divide first",
            prompt="Careful: y′ has a coefficient. Standard form comes first.",
            equation="t*y' + {a}*y = {b}*t**{k}",
            conditions="y(1) = {c}",
            technique="1st_linear",
            hints=(
                "Divide by t before reading anything off. That gives "
                "p = {a}/t.",
                "∫p dt is a multiple of ln t, so μ is a power of t — and the "
                "left side becomes the derivative of that power times y.",
                "Integrate the right, divide μ back out, then y(1) = {c} "
                "fixes the constant.",
            ),
            slots=(("a", (1, 2)), ("b", (1, 2)), ("k", (1, 2)), ("c", (0, 1))),
        ),
        Template(
            key="exponential-forcing",
            title="Exponential forcing, off resonance",
            prompt="The forcing decays too. Watch what the integral becomes.",
            equation="y' + {a}*y = {b}*exp(-{c}*t)",
            conditions="y(0) = 0",
            technique="1st_linear",
            hints=(
                "p is the constant {a}, so μ is e^(pt); the forcing decays "
                "at the different rate {c}.",
                "Multiplying gives a single exponential to integrate, because "
                "the two rates differ — had they matched, the integral would "
                "have been t instead.",
                "Divide by μ: the answer is a difference of two exponentials, "
                "and y(0) = 0 makes them cancel at t = 0.",
            ),
            slots=(("a", (1, 2, 3)), ("b", (1, 2)), ("c", (1, 2, 3))),
            # a == c is resonance for a first-order equation: mu*q becomes a
            # constant and the integral is t, not an exponential. A different
            # answer shape, and not what this drill is practising.
            reject=lambda s: s["a"] == s["c"],
        ),
    ),
)


BASICS = Lesson(
    key="basics",
    title="What a differential equation is",
    summary="An equation whose unknown is a function, and what it means to "
            "have solved one.",
    tool="steps",
    reference="Edwards 1.1–1.2",
    objectives=(
        "Say what the order of an equation is, and read it off.",
        "Check whether a given function is a solution, by substituting it.",
        "Tell a general solution from a particular one, and count the "
        "constants you should expect.",
        "Recognise when an equation can be solved by integrating alone.",
    ),
    examples=(
        Example(
            equation="y' = 3*t**2",
            conditions="y(0) = 5",
            why="The whole of the method is one integration — no technique is "
                "needed, because y does not appear on the right at all. Worth "
                "seeing first, so that later equations are recognisably harder "
                "than this one rather than differently mysterious.",
        ),
        Example(
            equation="y'' + y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            why="Second order, so two constants and two conditions. Count them "
                "as they appear: it is the clearest illustration of why the "
                "order decides how much information you have to supply.",
        ),
    ),
    notes=(
        Note(
            "The unknown is a function",
            "In an algebraic equation you are looking for a number. Here you "
            "are looking for a function, and the equation is a statement about "
            "how that function and its rate of change are related. A solution "
            "is a function that makes the statement true for every t.",
            r"y' = f(t, y)",
        ),
        Note(
            "Order is the highest derivative",
            "First order if only y' appears, second if y'' does, and so on. "
            "The order is the single most useful thing to notice about an "
            "equation: it decides which techniques can apply and how many "
            "arbitrary constants the answer will carry.",
            r"y'' + 3y' + 2y = 0 \quad\text{is second order}",
        ),
        Note(
            "One constant per order",
            "Integrating once introduces one constant, so an equation of order "
            "n has a general solution with n of them, and needs n conditions "
            "to pin down a particular one. If your answer has the wrong "
            "number, something has gone wrong before the arithmetic.",
            r"y'' = 0 \;\Longrightarrow\; y = C_1 + C_2 t",
            "formula",
        ),
        Note(
            "Checking is easier than solving",
            "You never have to take a solution on trust. Substitute it back "
            "and see whether both sides agree — which is exactly what this "
            "application does to every answer it shows you, and what the "
            "practice below does to yours.",
            r"y = e^{-2t} \;\Longrightarrow\; y' + 2y = -2e^{-2t} + 2e^{-2t} = 0",
        ),
        Note(
            "Not every equation has a formula",
            "y' = e^{−t²} has a perfectly good solution and no elementary "
            "expression for it, and most equations that come out of a real "
            "model are worse than that. That is not a failure of the subject; "
            "it is why numerical methods exist.",
            kind="aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="What is the order of t²y'' + y' − y = sin t ?",
            latex=r"t^{2}y'' + y' - y = \sin t",
            options=("First", "Second", "Third", "It depends on t"),
            answer=1,
            becauses=(
                "y' is there, but so is y''. The order is the *highest* "
                "derivative that appears, not the lowest.",
                "y'' is the highest derivative present, so the equation is "
                "second order — and its general solution will carry two "
                "arbitrary constants.",
                "Nothing here is differentiated three times. The t² is a "
                "coefficient, not a derivative.",
                "The coefficients may depend on t as much as they like; the "
                "order counts derivatives, and is the same for every t.",
            ),
        ),
        Choice(
            key="q2",
            prompt="Which of these is a solution of y' + 2y = 0 ?",
            latex=r"y' + 2y = 0",
            options=(
                "y = e^{2t}",
                "y = e^{-2t}",
                "y = 2e^{t}",
                "y = -2t",
            ),
            answer=1,
            becauses=(
                "y' = 2e^{2t}, so y' + 2y = 4e^{2t}, which is zero only if the "
                "exponential is — and it never is. The sign of the exponent is "
                "the thing to get right.",
                "y' = −2e^{−2t}, so y' + 2y = −2e^{−2t} + 2e^{−2t} = 0 for "
                "every t. Substituting is the whole check.",
                "y' = 2e^t, so y' + 2y = 6e^t, not zero. The coefficient in "
                "front does not help: the equation constrains the exponent.",
                "y' = −2 and 2y = −4t, so the sum is −2 − 4t, which is zero at "
                "one instant rather than for all t. A solution has to hold "
                "everywhere.",
            ),
        ),
        Solve(
            key="q3",
            prompt="No technique needed — y does not appear on the right.",
            equation="y' = 4*t + 1",
            conditions="y(0) = 3",
            hints=(
                "The right-hand side involves t alone, so this is an "
                "integration rather than a differential equation to solve.",
                "Integrate both sides with respect to t. Remember the "
                "constant.",
                "y = 2t² + t + C, and y(0) = 3 makes C = 3.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Second order, so expect two constants — and two conditions "
                   "to pin them.",
            equation="y'' = 6*t",
            conditions="y(0) = 1, y'(0) = 2",
            hints=(
                "Integrate once to get y', constant and all, then again.",
                "y' = 3t² + C₁, so y = t³ + C₁t + C₂.",
                "y'(0) = 2 gives C₁ = 2, and y(0) = 1 gives C₂ = 1.",
            ),
        ),
        Choice(
            key="q5",
            prompt="How many arbitrary constants should the general solution "
                   "of a third-order equation have?",
            options=("One", "Two", "Three", "It cannot be said in advance"),
            answer=2,
            becauses=(
                "One constant is what a first-order equation carries. Each "
                "integration adds another.",
                "Two is the second-order case. A third-order equation needs "
                "one more.",
                "One per order: integrating three times introduces three "
                "constants, and three conditions are needed to pin them down.",
                "It can, and that is what makes the count useful as a check: "
                "an answer with the wrong number of constants is wrong before "
                "you look at anything else.",
            ),
        ),
    ),
)


SLOPEFIELDS = Lesson(
    key="slopefields",
    title="Slope fields, existence and uniqueness",
    summary="What the equation tells you about its solutions before you solve "
            "anything at all.",
    tool="steps",
    reference="Edwards 1.3",
    prerequisites=("basics",),
    objectives=(
        "Read the shape of a solution off a slope field without solving.",
        "State what existence and uniqueness require, and check it.",
        "Recognise where uniqueness fails, and what goes wrong there.",
        "Say why two solution curves of a well-behaved equation cannot cross.",
    ),
    examples=(
        Example(
            equation="y' = y - t",
            conditions="y(0) = 1",
            why="The right-hand side and its y-derivative are continuous "
                "everywhere, so exactly one curve passes through each point. "
                "Solvable too, which lets the picture and the formula be "
                "compared.",
        ),
        Example(
            equation="y' = t/y",
            conditions="y(0) = 2",
            why="f = t/y is undefined on the whole line y = 0, and the answer "
                "shows what that costs: the solution exists only while it "
                "stays away from it, and the ± branches never meet.",
        ),
    ),
    notes=(
        Note(
            "The equation is a field of slopes",
            "y' = f(t, y) says: at the point (t, y), a solution through it has "
            "slope f(t, y). Draw a short segment of that slope at each point "
            "and the solutions are the curves that follow them. No solving "
            "involved — this is just the equation, read out loud.",
            r"\text{at } (t, y): \quad \text{slope} = f(t, y)",
        ),
        Note(
            "Existence and uniqueness",
            "If f is continuous near a point, some solution passes through it. "
            "If ∂f/∂y is continuous there too, exactly one does. Both halves "
            "matter: continuity gets you a curve, and the derivative condition "
            "is what stops there being several.",
            r"f,\ \frac{\partial f}{\partial y}\ \text{continuous near } "
            r"(t_0, y_0) \;\Longrightarrow\; \text{exactly one solution}",
            "formula",
        ),
        Note(
            "Solutions cannot cross",
            "Where the theorem applies, two different solution curves through "
            "the same point would contradict uniqueness. That is a strong "
            "constraint on a picture: it means the curves stack up without "
            "ever meeting, and a sketch showing them cross is wrong.",
        ),
        Note(
            "The theorem is local, and only sufficient",
            "It promises a solution near the starting point, not forever — "
            "y' = y² with y(0) = 1 runs to infinity at t = 1 while satisfying "
            "every hypothesis. And failing the test does not prove there is no "
            "solution, only that this theorem has nothing to say.",
            r"y' = y^{2},\ y(0) = 1 \;\Longrightarrow\; y = \frac{1}{1-t}",
            "pitfall",
        ),
        Note(
            "Where uniqueness really fails",
            "y' = y^{1/3} with y(0) = 0 has both y ≡ 0 and y = (2t/3)^{3/2} "
            "through the origin. ∂f/∂y blows up there, which is exactly the "
            "hypothesis that fails — the theorem is not being coy, it is "
            "pointing at the problem.",
            r"\frac{\partial}{\partial y} y^{1/3} = \frac{1}{3y^{2/3}}",
            "pitfall",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="For y' = y − t, what is the slope at the point (1, 1)?",
            latex=r"y' = y - t",
            options=("0", "1", "2", "−1"),
            answer=0,
            becauses=(
                "f(1, 1) = 1 − 1 = 0, so a solution through that point is "
                "momentarily flat. Reading a slope off the equation is a "
                "substitution, nothing more.",
                "1 is the value of y there, not the slope. The slope is what "
                "the right-hand side evaluates to.",
                "2 would be y + t. The equation has a minus sign.",
                "−1 is what you get evaluating t − y. The order of the "
                "subtraction matters.",
            ),
        ),
        Choice(
            key="q2",
            prompt="Where does the uniqueness theorem fail to apply to "
                   "y' = t/y ?",
            latex=r"y' = \frac{t}{y}",
            options=(
                "Nowhere — it applies everywhere",
                "On the line y = 0",
                "On the line t = 0",
                "Only where t and y are both negative",
            ),
            answer=1,
            becauses=(
                "It fails somewhere: f = t/y is a quotient, and a quotient has "
                "a denominator that can vanish.",
                "f = t/y is not even defined when y = 0, let alone continuous, "
                "so neither hypothesis holds there. Away from that line both "
                "do, and solutions are unique.",
                "t = 0 is harmless — f(0, y) = 0 is perfectly continuous, and "
                "∂f/∂y = −t/y² is too as long as y is not zero.",
                "Sign has nothing to do with it. What matters is whether the "
                "denominator vanishes.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Two solution curves of y' = y − t appear to cross. What "
                   "does that tell you?",
            options=(
                "The equation has more than one solution there",
                "The drawing is wrong — f and ∂f/∂y are continuous, so "
                "solutions through a point are unique",
                "The crossing point is an equilibrium",
                "Nothing; curves may cross",
            ),
            answer=1,
            becauses=(
                "That is what a crossing would mean, which is precisely why it "
                "cannot happen here: uniqueness rules it out.",
                "f = y − t and ∂f/∂y = 1 are continuous everywhere, so exactly "
                "one solution passes through each point. Two curves meeting "
                "would be two solutions through it.",
                "An equilibrium is a constant solution, and it would not "
                "involve two curves meeting. y = t + 1 is the straight-line "
                "solution here, and nothing crosses it.",
                "They may where the hypotheses fail, and this is not such an "
                "equation. Uniqueness is exactly the statement that they do "
                "not.",
            ),
        ),
        Solve(
            key="q4",
            prompt="The equation whose slope field the notes describe.",
            equation="y' = y - t",
            conditions="y(0) = 2",
            hints=(
                "Rearrange to y' − y = −t, which is linear with p = −1.",
                "μ = e^{−t}, so the left side becomes (e^{−t}·y)′.",
                "Integrating gives y = t + 1 + Ae^{t}, and y(0) = 2 makes "
                "A = 1.",
            ),
        ),
        Solve(
            key="q5",
            prompt="Existence is local: this one stops existing at t = 1.",
            equation="y' = y**2",
            conditions="y(0) = 1",
            hints=(
                "Separable: everything on the right is a function of y alone.",
                "dy/y² = dt integrates to −1/y = t + C.",
                "y = 1/(1 − t), which runs to infinity as t approaches 1 — "
                "even though the equation itself looks harmless there.",
            ),
        ),
    ),
)


EXACT = Lesson(
    key="exact",
    title="Exact equations",
    summary="When the left side is already the derivative of something, and "
            "the only work is finding what.",
    tool="steps",
    reference="Edwards 1.6",
    prerequisites=("separable", "linear"),
    objectives=(
        "Write a first-order equation as M dt + N dy = 0.",
        "Apply the exactness test, and say what it is testing.",
        "Recover ψ by integrating M and matching against N.",
        "State the solution as ψ(t, y) = C, and say why that is a solution.",
    ),
    examples=(
        Example(
            equation="y' = -(cos(t) + y)/(t + 2*y)",
            conditions="y(0) = 1",
            why="Neither separable nor linear, and yet it comes out in three "
                "lines. Watch ∂M/∂y and ∂N/∂t agree first — that agreement is "
                "what licenses everything after it.",
        ),
        Example(
            equation="y' = -(2*t + 3*y)/(3*t + 4*y)",
            conditions="",
            why="Exact and homogeneous at once. This application narrates it "
                "as a substitution, because that is the technique a course "
                "meets first — a reminder that a method applying does not make "
                "it the method to use.",
        ),
    ),
    notes=(
        Note(
            "Rewrite it without the fraction",
            "Put the equation in the form M dt + N dy = 0. Every first-order "
            "equation can be written that way, and in this form the question "
            "becomes: is the left side the differential of some function "
            "ψ(t, y)?",
            r"M(t, y)\,dt + N(t, y)\,dy = 0",
        ),
        Note(
            "The test",
            "If the left side is dψ, then M = ∂ψ/∂t and N = ∂ψ/∂y, and mixed "
            "partial derivatives agree. So ∂M/∂y must equal ∂N/∂t. That is the "
            "whole test, and it is the reason it works rather than a rule to "
            "memorise.",
            r"\frac{\partial M}{\partial y} = \frac{\partial N}{\partial t}",
            "formula",
        ),
        Note(
            "Building ψ",
            "Integrate M with respect to t, holding y fixed. The constant of "
            "that integration may depend on y, so call it h(y). Then "
            "differentiate what you have with respect to y, set it equal to N, "
            "and what is left determines h.",
            r"\psi = \int M\,dt + h(y), \qquad "
            r"h'(y) = N - \frac{\partial}{\partial y}\int M\,dt",
            "formula",
        ),
        Note(
            "Why ψ = C is the answer",
            "Along a solution curve, dψ = M dt + N dy = 0, so ψ does not "
            "change. The solution is the level curve of ψ through your initial "
            "point — which is why the answer often comes out implicit, and why "
            "that is a real answer rather than a failure.",
            r"\frac{d}{dt}\psi(t, y(t)) = M + N y' = 0",
        ),
        Note(
            "What is left over must not contain t",
            "After differentiating ∫M dt with respect to y and subtracting it "
            "from N, the remainder has to be a function of y alone — h cannot "
            "depend on t. If a t survives, the equation was not exact, and the "
            "test would have said so.",
            "pitfall",
        ),
        Note(
            "sympy is no help here",
            "Measured on this machine: of six exact equations, `classify_ode` "
            "named this technique for three, missed it on the three a lesson "
            "is actually about, and offered it on one that is not exact. So "
            "this application applies the test itself — the same test as "
            "above, run on your equation.",
            kind="aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="Which of these is exact?",
            options=(
                "(2t + y) dt + (t + 3y²) dy = 0",
                "(y) dt + (t²) dy = 0",
                "(t + y²) dt + (2t) dy = 0",
                "(y²) dt + (t) dy = 0",
            ),
            answer=0,
            becauses=(
                "∂M/∂y = 1 and ∂N/∂t = 1. They agree, so ψ exists — and it is "
                "t² + ty + y³.",
                "∂M/∂y = 1 but ∂N/∂t = 2t. They agree only at t = 1/2, and "
                "exactness has to hold on a region, not at a point.",
                "∂M/∂y = 2y and ∂N/∂t = 2. Those match only where y = 1, which "
                "is not enough.",
                "∂M/∂y = 2y and ∂N/∂t = 1. This one is separable, though, "
                "which is a better reason to be unbothered by it.",
            ),
        ),
        Choice(
            key="q2",
            prompt="You have ψ = t²y + h(y) and N = t² + 4y³. What is h(y)?",
            latex=r"\psi = t^{2}y + h(y), \qquad N = t^{2} + 4y^{3}",
            options=("h = 4y³", "h = y⁴", "h = t² + y⁴", "h = 0"),
            answer=1,
            becauses=(
                "4y³ is h′(y), not h. One more integration is needed.",
                "∂ψ/∂y = t² + h′(y), and that has to equal t² + 4y³, so "
                "h′ = 4y³ and h = y⁴.",
                "h is a function of y alone by construction — it was the "
                "constant of an integration in t. A t in it would mean the "
                "equation was not exact.",
                "h = 0 would need N to be exactly t², and it is not. The 4y³ "
                "has to come from somewhere, and h is the only thing left.",
            ),
        ),
        Solve(
            key="q3",
            prompt="Test it, build ψ, then solve for y.",
            equation="y' = -(3*t**2 + y)/(t + 2*y)",
            conditions="y(0) = 1",
            hints=(
                "M = 3t² + y and N = t + 2y. Check ∂M/∂y against ∂N/∂t before "
                "anything else.",
                "∫M dt = t³ + ty, so ψ = t³ + ty + h(y), and matching ∂ψ/∂y "
                "against N leaves h′ = 2y.",
                "ψ = t³ + ty + y² = C. It is a quadratic in y, so the "
                "condition picks which root.",
            ),
        ),
        Solve(
            key="q4",
            prompt="A trigonometric one — the method does not care.",
            equation="y' = -(cos(t) + y)/(t + 2*y)",
            conditions="y(0) = 2",
            hints=(
                "M = cos t + y and N = t + 2y, and both partials come out 1.",
                "∫M dt = sin t + ty, so ψ = sin t + ty + h(y) with h′ = 2y.",
                "ψ = sin t + ty + y² = C, and y(0) = 2 gives C = 4.",
            ),
        ),
        Choice(
            key="q5",
            prompt="An exact equation gives ψ(t, y) = C and you cannot solve "
                   "it for y. What have you got?",
            options=(
                "Nothing usable — the method has failed",
                "A solution, in implicit form: the solution curves are the "
                "level curves of ψ",
                "Only an approximation",
                "A solution that is valid only near t = 0",
            ),
            answer=1,
            becauses=(
                "The method has done exactly what it promised. Being unable to "
                "rearrange a correct relation is a limitation of algebra, not "
                "of the technique.",
                "ψ = C *is* the solution. Every solution curve is a level "
                "curve of ψ, and a textbook leaves the answer in that form as "
                "often as not — it can still be differentiated, plotted and "
                "checked.",
                "There is no approximation anywhere in this method. Everything "
                "in it is exact, which is where the name comes from.",
                "Nothing about ψ = C is local. The initial condition picks "
                "which level curve, and that curve is a solution for as long "
                "as it is defined.",
            ),
        ),
    ),
    templates=(
        Template(
            key="linear-exact",
            title="Test it, build ψ, solve for y",
            prompt="Check exactness first, then integrate M and match N.",
            equation="y' = -({a}*t**2 + y)/(t + {b}*y)",
            conditions="y(0) = {c}",
            technique="1st_exact",
            hints=(
                "Read off M and N, then compare ∂M/∂y with ∂N/∂t. Both are 1 "
                "here, which is what lets the rest happen.",
                "Integrate M with respect to t. What is left after matching "
                "∂ψ/∂y against N is a function of y alone.",
                "ψ comes out quadratic in y, so ψ = C is a quadratic to solve "
                "— and the initial condition picks which root.",
            ),
            slots=(("a", (3, 6, 9)), ("b", (2, 3, 4)), ("c", (1, 2))),
        ),
    ),
)


SUBSTITUTIONS = Lesson(
    key="substitutions",
    title="Substitutions: homogeneous and Bernoulli",
    summary="Two equations that are not separable or linear, and two changes "
            "of variable that make them so.",
    tool="steps",
    reference="Edwards 1.6",
    prerequisites=("separable", "linear"),
    objectives=(
        "Recognise a homogeneous equation from the ratio y/t.",
        "Carry out y = v·t, and say why it produces a separable equation.",
        "Recognise the Bernoulli form, and pick the exponent for v.",
        "Undo a substitution, including choosing the sign an even root leaves.",
    ),
    examples=(
        Example(
            equation="y' = (t**2 + y**2)/(t*y)",
            conditions="y(1) = 2",
            why="Homogeneous: divide top and bottom by t² and only y/t "
                "survives. Watch the substituted equation separate, and watch "
                "the initial condition choose the sign at the very end.",
        ),
        Example(
            equation="y' + y = t*y**3",
            conditions="y(0) = 1",
            why="Bernoulli with n = 3. The derivation visibly turns into the "
                "integrating-factor derivation you already know, which is the "
                "whole point of the substitution.",
        ),
    ),
    notes=(
        Note(
            "Homogeneous: everything is y/t",
            "If the right-hand side can be written using only the ratio y/t, "
            "the equation is homogeneous. Test it by replacing y with v·t: if "
            "every t cancels, it was. Nothing to do with the *other* meaning "
            "of homogeneous, which is about a zero right-hand side.",
            r"y' = F\!\left(\frac{y}{t}\right)",
            "pitfall",
        ),
        Note(
            "y = v·t makes it separable",
            "Substitute y = v·t, so y' = v + t·v' by the product rule. The "
            "equation becomes v + t v' = F(v), which rearranges to "
            "t v' = F(v) − v — and that always separates, whatever F is.",
            r"t\,v' = F(v) - v \;\Longrightarrow\; "
            r"\frac{dv}{F(v) - v} = \frac{dt}{t}",
            "formula",
        ),
        Note(
            "Bernoulli: linear except for one power",
            "y' + p y = q yⁿ is linear apart from that exponent. For n = 0 or "
            "n = 1 it already is linear and needs nothing. For anything else, "
            "dividing by yⁿ and substituting v = y^{1−n} turns it into an "
            "equation that is linear in v.",
            r"y' + p(t)y = q(t)y^{n} \;\Longrightarrow\; "
            r"v' + (1-n)p\,v = (1-n)q, \quad v = y^{1-n}",
            "formula",
        ),
        Note(
            "The exponent is forced, not chosen",
            "1 − n is the only exponent that works: it is what makes v' "
            "produce the y^{−n} that dividing by yⁿ left behind. Guessing v = "
            "y² or v = 1/y and hoping is the usual way to lose ten minutes.",
            r"v = y^{1-n} \;\Longrightarrow\; v' = (1-n)y^{-n}y'",
            "pitfall",
        ),
        Note(
            "Undoing the substitution can leave a sign",
            "y = v^{1/(1−n)} is an even root whenever 1 − n is even, and both "
            "signs solve the equation. Only one passes through your initial "
            "point. Substituting will not tell you which — the condition is "
            "the only thing that does.",
            "pitfall",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="Which equation is homogeneous?",
            options=(
                "y' = (t + y)/(t − y)",
                "y' = t + y",
                "y' = t·y²",
                "y' = y + t²",
            ),
            answer=0,
            becauses=(
                "Divide top and bottom by t and it is (1 + y/t)/(1 − y/t) — "
                "the ratio and nothing else. Substituting y = v·t clears every "
                "t.",
                "Substituting y = v·t gives t + v·t = t(1 + v), and the t does "
                "not cancel against the v' side. A sum of unlike degrees is "
                "not homogeneous.",
                "t·y² becomes t·v²t² = v²t³, which keeps a t. This one is "
                "separable, so it needs no substitution anyway.",
                "y + t² is degree 1 plus degree 2, so the t survives the "
                "substitution. Homogeneity needs every term at the same "
                "degree.",
            ),
        ),
        Choice(
            key="q2",
            prompt="For y' + y/t = y³, what substitution linearises it?",
            latex=r"y' + \frac{y}{t} = y^{3}",
            options=("v = y³", "v = y^{-2}", "v = y²", "v = 1/y"),
            answer=1,
            becauses=(
                "v = yⁿ is the exponent already in the equation, not the one "
                "that removes it. The substitution has to undo the power, not "
                "repeat it.",
                "n = 3, so v = y^{1−n} = y^{−2}. Dividing by y³ leaves y^{−3}y' "
                ", and that is exactly what v' produces up to a constant.",
                "y² is y^{1−n} for n = −1, which is a different equation. Here "
                "n is 3.",
                "1/y is y^{−1}, which is y^{1−n} for n = 2. Close, but the "
                "exponent here is 3.",
            ),
        ),
        Solve(
            key="q3",
            prompt="Homogeneous. Substitute y = v·t.",
            equation="y' = (t**2 + y**2)/(t*y)",
            conditions="y(1) = 2",
            hints=(
                "Divide top and bottom by t²: the right-hand side is "
                "(1 + (y/t)²)/(y/t), which is the ratio alone.",
                "With y = v·t it becomes v + t v' = (1 + v²)/v, so "
                "t v' = 1/v — which separates.",
                "v dv = dt/t gives v² = 2 ln t + C, so y = t·√(2 ln t + C), "
                "and y(1) = 2 makes C = 4. Take the positive root.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Bernoulli with n = 3.",
            equation="y' + y = t*y**3",
            conditions="y(0) = 1",
            hints=(
                "It is linear apart from the y³, so the substitution is "
                "v = y^{1−3} = y^{−2}.",
                "Dividing by y³ and substituting gives v' − 2v = −2t, which is "
                "linear with p = −2.",
                "Solve that with the integrating factor e^{−2t}, then undo the "
                "substitution: y = v^{−1/2}, and the condition picks the "
                "positive root.",
            ),
        ),
        Choice(
            key="q5",
            prompt="Why is y' + p y = q y¹ not a Bernoulli problem?",
            options=(
                "Because n must be at least 2",
                "Because with n = 1 the y term can be moved to the left and "
                "the equation is already linear",
                "Because the substitution would be v = y⁰ = 1",
                "It is a Bernoulli problem",
            ),
            answer=1,
            becauses=(
                "Negative n is fine — y' − y/t = t·y^{−1} is a perfectly good "
                "Bernoulli equation. It is n = 0 and n = 1 that are excluded, "
                "and for a different reason.",
                "y' + py = qy is y' + (p − q)y = 0, which is linear and "
                "separable. There is nothing for a substitution to fix.",
                "That is true and is a symptom rather than the reason: v = 1 "
                "is useless precisely because the equation was already linear.",
                "It is not, and the substitution would tell you so by "
                "collapsing to nothing. The technique is for the exponents "
                "that make the equation nonlinear.",
            ),
        ),
    ),
    templates=(
        Template(
            key="homogeneous",
            title="Homogeneous: substitute y = v·t",
            prompt="Check it depends on y/t alone, then substitute.",
            equation="y' = ({a}*t**2 + y**2)/(t*y)",
            conditions="y(1) = {c}",
            technique="1st_homogeneous_coeff_best",
            hints=(
                "Divide top and bottom by t². If only y/t survives, the "
                "substitution will clear every t.",
                "y = v·t gives y' = v + t·v', and the equation becomes "
                "t·v' = F(v) − v, which separates.",
                "Separate, integrate, then multiply back by t — and let the "
                "condition choose the sign of the square root.",
            ),
            slots=(("a", (1, 2, 3)), ("c", (1, 2, 3))),
        ),
        Template(
            key="bernoulli",
            title="Bernoulli: substitute v = y^(1-n)",
            prompt="Read off n, substitute, and finish with an integrating "
                   "factor.",
            equation="y' + {a}*y = {b}*t*y**3",
            conditions="y(0) = 1",
            technique="Bernoulli",
            # Braces are doubled because these are format strings: `y^{{-2}}`
            # renders as y^{-2}, while `y^{-2}` would be read as a slot name.
            hints=(
                "The exponent on the right is 3, so n = 3 and the "
                "substitution is v = y^{{-2}}.",
                "Dividing by y³ and substituting turns it into a linear "
                "equation in v. Find its integrating factor.",
                "Solve for v, then undo the substitution with y = v^{{-1/2}}, "
                "taking the branch the condition sits on.",
            ),
            slots=(("a", (1, 2, 3)), ("b", (1, 2))),
        ),
    ),
)


LESSONS = (BASICS, SLOPEFIELDS, SEPARABLE, LINEAR, EXACT,
           SUBSTITUTIONS)
