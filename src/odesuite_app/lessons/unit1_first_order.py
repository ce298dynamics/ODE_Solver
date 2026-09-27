"""Unit 1 -- First-order equations.

Edwards, Penney and Calvis 6e, chapter 1. The two techniques a course meets
first, and the two it falls back on for the rest of the term.

Six lessons: what a differential equation is, reading one off a slope field,
and the four techniques a first course solves them with.
"""

from __future__ import annotations

from .chapters import unit1 as chapters
from .model import (
    Case,
    Choice,
    ChoiceTemplate,
    ClassifyTemplate,
    Example,
    ExpressionTemplate,
    FaultTemplate,
    Lesson,
    ModelTemplate,
    Note,
    NumericTemplate,
    Passage,
    Solve,
    Template,
)

__all__ = ["BASICS", "SLOPEFIELDS", "SEPARABLE", "LINEAR",
           "EXACT", "SUBSTITUTIONS", "LESSONS"]


SEPARABLE = Lesson(
    key="separable",
    chapter=chapters.SEPARABLE,
    title="Separable equations",
    summary="The first technique, and the one every other first-order method "
            "falls back on when it can.",
    tool="steps",
    reference="Edwards 1.4",
    figure="separable_family",
    motivation=(
        "The general first-order equation y' = F(t, y) is not solvable in any "
        "systematic way — no technique in this course touches the general "
        "case, and none exists. What a first course does instead is find the "
        "*shapes* of F for which something can be said, and this is the first "
        "and most forgiving of them.\n\n"
        "The shape is a product: everything involving t in one factor, "
        "everything involving y in the other. That is a real restriction — "
        "y' = t + y is not of this form and neither is y' = sin(t + y) — but "
        "it covers a surprising amount of what actually arises. Growth "
        "proportional to population, cooling proportional to temperature "
        "difference, a reaction rate proportional to concentration: all "
        "products, because the physical law usually multiplies a rate by an "
        "amount rather than adding them.\n\n"
        "The reason to meet it first is that the method needs nothing but "
        "integration. There is no formula to memorise and no auxiliary "
        "function to construct; the equation is rearranged until both sides "
        "are integrable, and then they are integrated. Every other "
        "first-order technique in this unit is, in the end, a way of turning "
        "some other equation into one of these."
    ),
    derivation=(
        Passage(
            prose="Suppose the right-hand side factors. Write the equation "
                  "with everything in y on the left and everything in t on "
                  "the right — which is legitimate as long as g(y) is not "
                  "zero, and that caveat will come back.",
            latex=r"\frac{dy}{dt} = f(t)\,g(y) \quad\Longrightarrow\quad "
                  r"\frac{1}{g(y)}\frac{dy}{dt} = f(t)",
        ),
        Passage(
            prose="Here is the step usually waved at, and it is worth doing "
                  "honestly. Let H be any antiderivative of 1/g. Then by the "
                  "chain rule, the left-hand side is exactly the derivative "
                  "of H(y(t)) with respect to t — no manipulation of "
                  "differentials required, and nothing informal about it.",
            latex=r"\frac{d}{dt}H(y(t)) = H'(y)\,\frac{dy}{dt} "
                  r"= \frac{1}{g(y)}\frac{dy}{dt}",
        ),
        Passage(
            prose="So the equation says two functions of t have the same "
                  "derivative. By the argument from the first lesson they "
                  "differ by a constant, and that single constant is the one "
                  "the answer carries — both integrals produce one, but their "
                  "difference is again a constant, so only one is ever "
                  "written.",
            latex=r"\frac{d}{dt}H(y(t)) = \frac{d}{dt}\int f(t)\,dt "
                  r"\;\Longrightarrow\; H(y) = \int f(t)\,dt + C",
        ),
        Passage(
            prose="That is the whole method, and it explains the "
                  "differentials notation rather than relying on it. Writing "
                  "dy/g(y) = f(t)dt and integrating each side against its own "
                  "variable gives the same equation, which is why the "
                  "shorthand is safe — it is bookkeeping for the chain-rule "
                  "argument above.",
            latex=r"\int\frac{dy}{g(y)} = \int f(t)\,dt",
        ),
        Passage(
            prose="Two things the derivation quietly assumed, and both bite "
                  "in practice. Dividing by g(y) required it to be non-zero, "
                  "so any root of g has been excluded — and each root is a "
                  "constant solution in its own right, which the family above "
                  "may not contain. And H(y) = … is an *implicit* answer; "
                  "solving it for y needs H to be invertible, which is where "
                  "the ± branches come from.",
            latex=r"g(y_0) = 0 \;\Longrightarrow\; y \equiv y_0 "
                  r"\text{ solves it too}",
        ),
    ),
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
            commentary=(
                "Watch the division, which is where this method always pays. "
                "Separating means dividing by y(1 - y), and that throws away exactly "
                "the two values at which it vanishes — so read the answer as covering "
                "everything except those two, and add them back by inspection.\n\n"
                "Then read what the family does rather than being told. Every curve "
                "starting between the two equilibria rises towards the upper one, and "
                "that is the whole content of logistic growth sitting in the algebra "
                "of the answer. Nothing had to be asserted about it: substitute a "
                "starting value near zero and the limit is visible."
            ),
        ),
        Example(
            equation="y' = y**2",
            conditions="y(0) = 1",
            why="Nothing about this equation looks dangerous, and yet the "
                "solution runs to infinity at t = 1. Separating finds that; "
                "the equation itself never says so.",
            commentary=(
                "Look for where the finite time comes from, because nothing in the "
                "equation mentions it. The antiderivative of one over y squared puts "
                "y into a denominator, and the initial condition places that "
                "denominator's zero at t = 1. Start somewhere else and the blow-up "
                "moves.\n\n"
                "So this equation satisfies the uniqueness theorem at every point of "
                "the plane and still fails to have a solution for all t. The two "
                "facts are compatible, and holding them together is the point: the "
                "theorem promises a solution near the start and promises nothing "
                "whatever about how far it extends."
            ),
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
        # PED-06: where the method itself stops, not a mistake a student makes.
        Note(
            "Where it stops: f must factor",
            "The method needs y' = g(t)·h(y) exactly. y' = t + y does not "
            "factor, however it is rearranged, and needs an integrating factor "
            "instead. And a factored equation can still defeat the second step:"
            " ∫ exp(y²) dy has no elementary form, so the answer stays an "
            "integral or an implicit relation.",
            r"y' = t + y \;\neq\; g(t)\,h(y)",
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
            # The power of t is what decides the work: k = 0 is a bare
            # exponential, k = 2 an integral somebody has to stop and do.
            level=lambda slots: ("easier", "typical", "harder")[slots["k"]],
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
        FaultTemplate(
            key="lost-the-constant",
            title="Spot the mistake: a decay with a condition",
            prompt="Somebody separated this, integrated both sides and "
                   "handed in the answer below. What went wrong?",
            equation="y' = -{a}*y",
            conditions="y(0) = {c}",
            wrong="exp(-{a}*t)",
            fault="no-constant",
            others=("sign-in-exponent", "missing-particular",
                    "undivided-factor"),
            slots=(("a", (1, 2, 3, 4)), ("c", (2, 3, 5, 7))),
        ),
    ),
)


LINEAR = Lesson(
    key="linear",
    chapter=chapters.LINEAR,
    title="First-order linear, and the integrating factor",
    summary="What to do when the equation is linear in y but refuses to "
            "separate.",
    tool="steps",
    reference="Edwards 1.5",
    figure="integrating_factor",
    motivation=(
        "Separation asked the right-hand side to factor, and an enormous class "
        "of equations refuses. y' = -2y + t is the plainest example: the two "
        "influences on the rate are *added*, not multiplied, and no "
        "rearrangement turns a sum into a product. Yet this is the shape "
        "physical modelling produces most often of all, because it is what "
        "happens whenever something decays on its own and is driven from "
        "outside at the same time.\n\n"
        "A cooling cup of coffee in a room whose own temperature is changing; "
        "a balance losing value to inflation while deposits arrive; a drug "
        "clearing from the bloodstream against a steady infusion. Each is a "
        "decay term proportional to the amount present, plus a forcing term "
        "that does not care what the amount is. Separation cannot touch any of "
        "them.\n\n"
        "What can is a manoeuvre with an unusual character: rather than "
        "rearranging the equation, multiply it by something. The right "
        "multiplier collapses the entire left-hand side into a single "
        "derivative, at which point the equation is the y' = f(t) of the first "
        "lesson and one integration finishes it. The multiplier is not "
        "guessed — it can be derived, and the derivation is four lines."
    ),
    derivation=(
        Passage(
            prose="Put the equation in standard form, with the coefficient of "
                  "y' equal to one. This matters more than it looks: p and q "
                  "are read off *after* dividing, and reading them off before "
                  "is the most common route to the wrong integrating factor.",
            latex=r"y' + p(t)\,y = q(t)",
        ),
        Passage(
            prose="The obstruction is that the left-hand side is not the "
                  "derivative of anything obvious. But look at what the "
                  "product rule does to a product of y with some as-yet-"
                  "unknown factor: it produces that factor times y' plus its "
                  "own derivative times y. Compare with what multiplying the "
                  "equation by the same factor gives.",
            latex=r"(\mu y)' = \mu y' + \mu' y \qquad\text{versus}\qquad "
                  r"\mu(y' + py) = \mu y' + \mu p\,y",
        ),
        Passage(
            prose="The two agree exactly when the factor satisfies one "
                  "condition — and that condition has no y in it, so it is an "
                  "equation for the factor alone. Better still it is "
                  "separable, so the previous lesson already solves it. That "
                  "is the step worth noticing: this method is not a new idea "
                  "but a trade of one hard equation for an easy one.",
            latex=r"\mu' = p(t)\,\mu \;\Longrightarrow\; "
                  r"\frac{d\mu}{\mu} = p\,dt \;\Longrightarrow\; "
                  r"\mu = e^{\int p\,dt}",
        ),
        Passage(
            prose="Any one antiderivative of p will do, and the constant of "
                  "integration can be dropped. A different constant multiplies "
                  "the factor by a non-zero number, which scales both sides of "
                  "the equation equally — the same equation. That is why no "
                  "second constant appears in the integrating factor even "
                  "though it came out of an integration.",
            latex=r"\mu \to C\mu \;\Longrightarrow\; C(\mu y)' = C\mu q "
                  r"\;\text{(unchanged)}",
        ),
        Passage(
            prose="With that factor the left-hand side genuinely is a "
                  "derivative, and the equation has been reduced to the "
                  "y' = f(t) case. Integrate once, then divide back.",
            latex=r"(\mu y)' = \mu q \;\Longrightarrow\; "
                  r"y = \frac{1}{\mu}\left(\int \mu(t)q(t)\,dt + C\right)",
        ),
        Passage(
            prose="Two things this buys beyond an answer. Because the factor "
                  "is an exponential it is never zero, so dividing back is "
                  "always legal and no solutions are lost — unlike separation, "
                  "this method has no missing constant solution to hunt for. "
                  "And the answer's shape is legible: the term carrying C is "
                  "whatever the initial condition contributed, and the integral "
                  "term is the response to the forcing. That split is the "
                  "transient and the steady state, and it returns in every "
                  "later unit.",
            latex=r"y = \frac{1}{\mu}\int \mu q\,dt \;+\; \frac{C}{\mu}"
                  r"\qquad \text{forcing} \;+\; \text{initial condition}",
        ),
    ),
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
            commentary=(
                "The line to watch is the one where the left-hand side becomes a "
                "single derivative. Everything before it exists to set that collapse "
                "up; everything after it is one integration and a division. If the "
                "collapse does not happen, the integrating factor is wrong — and that "
                "is the only symptom you get, because nothing raises an error.\n\n"
                "Then read the answer's two terms separately. The polynomial part is "
                "the response to the forcing and stays; the exponential part carries "
                "the constant and dies. That is the steady state and the transient in "
                "the simplest place they ever appear, and recognising the split here "
                "makes the vibrations unit much shorter."
            ),
        ),
        Example(
            equation="t*y' + y = t",
            conditions="y(1) = 1",
            why="p(t) = 1/t is not constant, which is what the method is "
                "actually for — and the left side was already a product-rule "
                "derivative before anything was multiplied by anything.",
            commentary=(
                "The first step is the one most easily skipped: divide through so the "
                "coefficient of y' is one. Reading p off before dividing gives the "
                "wrong factor, and a wrong factor fails silently — the left-hand side "
                "simply does not become a derivative, with nothing to tell you why.\n\n"
                "There is a bonus hiding in this particular equation. The "
                "construction returns a factor of t, which is precisely the "
                "factor the left-hand side was carrying all along, so it could "
                "have been finished by inspection — and the method arrived "
                "at the same place without needing to spot that. And watch the "
                "interval: the coefficient is undefined at zero, so a "
                "condition given at t = 1 "
                "selects the solution on the positive axis and says nothing at all "
                "about the other side."
            ),
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
            r"t y' + y = t \;\Longrightarrow\; y' + \frac{1}{t}\,y = 1",
            "pitfall",
        ),
        # PED-06: where the method itself stops, not a mistake a student makes.
        Note(
            "Where it stops: y must appear linearly",
            "An integrating factor exists because y and y' appear only to the "
            "first power. y' = y² + t is not linear, and no μ(t) straightens "
            "it. Even when the equation is linear, ∫ μq dt may have no "
            "elementary antiderivative; the method still works, and the answer "
            "keeps that integral in it.",
            r"y' = y^{2} + t \quad\text{is not linear in } y",
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
        ModelTemplate(
            key="mixing-tank",
            title="Set up the equation: a stirred tank",
            prompt="A tank holds {V} litres of water and is kept stirred. "
                   "Dye solution carrying {c} grams a litre runs in at {r} "
                   "litres a minute, and the mixture runs out at the same "
                   "rate. Write the equation for y, the grams of dye in the "
                   "tank after t minutes.",
            equation="y' = {c}*{r} - {r}*y/{V}",
            because="Rate in minus rate out, in grams a minute. In: {r} "
                    "litres a minute at {c} grams a litre — a constant, and "
                    "nothing to do with y. Out: the volume stays at {V} "
                    "litres because the two rates are equal, so the mixture "
                    "leaving is at y/{V} grams a litre and carries away {r} "
                    "times that.",
            hints=(
                "Write it as rate in − rate out, in grams per minute. "
                "Nothing else changes the amount of dye.",
                "The inflow is a concentration times a flow rate, and "
                "neither depends on how much dye is already in the tank.",
                "For the outflow, the concentration is the amount divided by "
                "the volume — and the volume never changes, because as much "
                "runs out as runs in.",
            ),
            slots=(("V", (100, 200, 500)), ("r", (4, 5, 10)),
                   ("c", (2, 3, 5))),
        ),
        ExpressionTemplate(
            key="the-integrating-factor",
            title="One step only: the integrating factor",
            prompt="Write the integrating factor μ(t) for   {shown} = {q}.   "
                   "Do not solve the equation.",
            answer="{mu}",
            up_to_constant=True,
            because="μ = e^(∫p dt) with p = {p}. The constant of integration "
                    "in that exponent only multiplies μ by a constant, and a "
                    "constant multiple of an integrating factor is another "
                    "one — so it is left out.",
            hints=(
                "μ is e to the integral of the coefficient of y. The forcing "
                "term on the right plays no part in choosing it.",
                "Integrate p with respect to t and put the result in the "
                "exponent. Nothing else goes in there.",
                "Write it as exp(...). If the integral came out as a "
                "logarithm, remember that e^(k·ln t) is t^k — the "
                "exponential and the logarithm undo each other and leave a "
                "power.",
            ),
            slots=(("p,shown,mu,tier", (
                ("3", "y' + 3y", "exp(3*t)", "easier"),
                ("-2", "y' − 2y", "exp(-2*t)", "easier"),
                ("5", "y' + 5y", "exp(5*t)", "easier"),
                ("t", "y' + t·y", "exp(t**2/2)", "typical"),
                ("2*t", "y' + 2t·y", "exp(t**2)", "typical"),
                ("-t", "y' − t·y", "exp(-t**2/2)", "typical"),
                ("2/t", "y' + 2y/t", "t**2", "harder"),
                ("-3/t", "y' − 3y/t", "t**(-3)", "harder"),
                ("cos(t)", "y' + y·cos(t)", "exp(sin(t))", "harder"),
            )), ("q", ("t", "1", "e^t"))),
            level=lambda slots: slots["tier"],
        ),
        FaultTemplate(
            key="never-divided-back",
            title="Spot the mistake: an integrating factor left in",
            prompt="Somebody multiplied through by μ, integrated, and "
                   "handed this in. What went wrong?",
            equation="y' + {a}*y = {b}",
            wrong="{ratio}*exp({a}*t) + C1",
            fault="undivided-factor",
            others=("sign-in-exponent", "no-constant", "missing-particular"),
            slots=(("a,b,ratio", (
                (2, 10, 5), (2, 12, 6), (3, 12, 4), (3, 30, 10),
                (4, 20, 5), (4, 12, 3), (5, 30, 6), (5, 20, 4),
                (2, 30, 15), (3, 60, 20),
            )),),
        ),
    ),
)


BASICS = Lesson(
    key="basics",
    chapter=chapters.BASICS,
    title="What a differential equation is",
    summary="An equation whose unknown is a function, and what it means to "
            "have solved one.",
    tool="steps",
    reference="Edwards 1.1–1.2",
    figure="solution_family",
    motivation=(
        "Algebra asks which *number* satisfies a condition. A differential "
        "equation asks which *function* does — and the condition is about the "
        "function's rate of change rather than its value. That is the whole "
        "shift, and nearly everything unfamiliar about the subject follows "
        "from it.\n\n"
        "It is worth making because rates of change are what the world "
        "actually reports. Nobody measures a bacterial colony as a formula "
        "in t; what is observable is that it grows in proportion to how many "
        "are already there. Nobody knows a falling object's height in "
        "advance; what is known is that gravity pulls down and the air pushes "
        "back in proportion to speed. In each case the law is a statement "
        "about the derivative, and the function wanted is whatever satisfies "
        "it.\n\n"
        "So the equation is the easy half to write and the hard half to "
        "solve. This lesson is about what solving even means here, because "
        "the answer is not a number, and usually not one function either — "
        "it is a whole family of them, and it takes extra information to "
        "single one out."
    ),
    derivation=(
        Passage(
            prose="Start with the simplest possible case, where the "
                  "right-hand side never mentions y. Then the equation says "
                  "only that y is an antiderivative of f, and the "
                  "fundamental theorem of calculus answers it outright.",
            latex=r"y' = f(t) \quad\Longrightarrow\quad y(t) = \int f(t)\,dt",
        ),
        Passage(
            prose="Now notice what that integral leaves behind. Any two "
                  "antiderivatives of the same f differ by a constant, "
                  "because a function whose derivative vanishes everywhere is "
                  "constant. So the equation does not have *a* solution — it "
                  "has a one-parameter family of them, and the parameter is "
                  "real rather than an artefact of how we happened to solve "
                  "it.",
            latex=r"\frac{d}{dt}(y_1 - y_2) = f - f = 0 "
                  r"\;\Longrightarrow\; y_1 - y_2 = C",
        ),
        Passage(
            prose="That is why an initial condition is not an optional extra. "
                  "Giving y at one instant picks one curve out of the family, "
                  "and it is the least information that can. Physically it is "
                  "the statement that the law alone does not determine the "
                  "motion: you must also say where it started.",
            latex=r"y(t_0) = y_0 \;\Longrightarrow\; C \text{ is pinned}",
        ),
        Passage(
            prose="Each further derivative costs another constant, for the "
                  "same reason — integrating twice leaves two. An nth-order "
                  "equation therefore has an n-parameter family and needs n "
                  "conditions, which is why a second-order equation always "
                  "arrives with a position *and* a velocity.",
            latex=r"y'' = f(t) \;\Longrightarrow\; "
                  r"y = \iint f\,dt\,dt + C_1 t + C_2",
        ),
        Passage(
            prose="One asymmetry makes the whole subject workable: checking "
                  "is differentiation, and solving is integration. "
                  "Differentiating is mechanical — every elementary function "
                  "has an elementary derivative — while integration has no "
                  "such guarantee. So a candidate can always be verified even "
                  "when it could never have been produced, which is why every "
                  "answer in this application is substituted back.",
            latex=r"\text{substitute } y,\ \text{simplify } y' - f(t) "
                  r"\text{ to } 0",
        ),
    ),
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
            commentary=(
                "Read the working as three moves: integrate, name the constant, use "
                "the condition. The order is not a preference. Substituting the "
                "condition before integrating has nothing to substitute into, and "
                "reaching for it too early is the most common way a problem this "
                "simple goes wrong.\n\n"
                "Watch where the constant enters and where it leaves. It appears at "
                "the integration, carrying the fact that infinitely many functions "
                "have this derivative, and the condition then discards all but one of "
                "them. The general family comes first and the particular curve "
                "second, always."
            ),
        ),
        Example(
            equation="y'' + y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            why="Second order, so two constants and two conditions. Count them "
                "as they appear: it is the clearest illustration of why the "
                "order decides how much information you have to supply.",
            commentary=(
                "This one is not solved by integrating twice. The right-hand side is "
                "not a function of t, so the first lesson's method does not reach it "
                "and the answer arrives from a technique three units away. Read it "
                "for its shape rather than its derivation.\n\n"
                "And the shape is the point. A starting position alone would leave a "
                "whole one-parameter family still satisfying it, so the second "
                "condition is not redundant bookkeeping — it is the other half of the "
                "information. That is the concrete content of one condition per "
                "order, and physically the statement that where a spring starts does "
                "not determine what it does unless you also say how fast it is "
                "moving."
            ),
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
    templates=(
        ChoiceTemplate(
            key="which-solves-it",
            title="Check it by substituting",
            prompt="Which of these is a solution of y' = {a}*y?",
            options=(
                "y = e^({a}t)",
                "y = e^(-{a}t)",
                "y = {a}·e^t",
                "y = t^{a}",
            ),
            answer=0,
            becauses=(
                "Differentiating gives {a}e^({a}t), which is {a} times the "
                "function itself — exactly what the equation asks for. Any "
                "constant multiple works too, which is the one arbitrary "
                "constant a first-order equation is entitled to.",
                "Differentiating gives −{a}e^(−{a}t), so this satisfies "
                "y' = −{a}y instead. The sign of the exponent is the sign of "
                "the growth rate, and it is the commonest slip there is.",
                "Differentiating gives {a}e^t, but {a} times the function is "
                "{a}·{a}e^t. The constant out front cannot fix a rate that is "
                "wrong: it cancels from both sides.",
                "Differentiating gives {a}t^({a}−1), and {a} times the "
                "function is {a}t^{a}. Those agree only where t = 1, and a "
                "solution has to satisfy the equation everywhere.",
            ),
            latex=r"y' = {a}\,y",
            slots=(("a", (2, 3, 4, 5, 6, 7, 8)),),
        ),
        ModelTemplate(
            key="family-to-equation",
            title="Read the equation off the family",
            prompt="Every curve in the family   y = {family}   solves one "
                   "first-order equation, and the equation has no C in it. "
                   "Write it.",
            equation="{answer}",
            because="{why}",
            hints=(
                "Differentiate the family once. That gives y' in terms of t "
                "and the constant C.",
                "Now get rid of C. The family itself tells you what C is in "
                "terms of t and y — rearrange it and substitute.",
                "What is left relates y', y and t, with no C anywhere. That "
                "is the equation the family came from.",
            ),
            slots=(("family,answer,why,tier", (
                ("C·e^(2t)", "y' = 2*y",
                 "Differentiating gives y' = 2·C·e^(2t). But C·e^(2t) is y "
                 "itself, so y' = 2y — and the constant has gone.",
                 "easier"),
                ("C·e^(-3t)", "y' = -3*y",
                 "y' = −3·C·e^(-3t), and C·e^(-3t) is y, so y' = −3y. The "
                 "rate is negative, which is what decay means.",
                 "easier"),
                ("t² + C", "y' = 2*t",
                 "Here C comes off on its own: y' = 2t, with no y in it at "
                 "all. Not every family leads to an equation that mentions "
                 "y.",
                 "easier"),
                ("C·t²", "t*y' = 2*y",
                 "y' = 2·C·t, and C is y/t², so y' = 2y/t. Multiply up by t "
                 "and nothing is left in the denominator.",
                 "typical"),
                ("C·t³", "t*y' = 3*y",
                 "y' = 3·C·t², and C is y/t³, so y' = 3y/t. The power of t "
                 "in the family becomes the coefficient.",
                 "typical"),
                ("C/t", "t*y' = -y",
                 "y' = −C/t², and C is t·y, so y' = −y/t. The same shape as "
                 "the powers above, with the exponent negative.",
                 "typical"),
                ("C·e^(t²)", "y' = 2*t*y",
                 "The chain rule gives y' = 2t·C·e^(t²), and the exponential "
                 "with its constant is y — so the coefficient of y is what "
                 "the exponent differentiated to.",
                 "harder"),
                ("4 + C·e^(-t)", "y' = 4 - y",
                 "y' = −C·e^(-t). The family says C·e^(-t) is y − 4, so "
                 "y' = −(y − 4) = 4 − y. The constant 4 is where the "
                 "solutions settle, and it survives into the equation.",
                 "harder"),
                ("C·e^t - t - 1", "y' = y + t",
                 "y' = C·e^t − 1, and the family says C·e^t is y + t + 1. "
                 "Substituting gives y' = y + t: the polynomial part is what "
                 "the forcing term left behind.",
                 "harder"),
            )),),
            level=lambda slots: slots["tier"],
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
    motivation=(
        "Every technique in this unit hands back a formula, which invites a "
        "false impression: that solving an equation means finding one. It does "
        "not, and the equations for which a formula exists are a thin and "
        "unrepresentative slice of them. The equation y' = y² − t has no "
        "elementary solution, and nothing is wrong with it — it is a perfectly "
        "ordinary equation with perfectly ordinary solutions that simply "
        "cannot be written in closed form.\n\n"
        "So a first course needs a way of seeing solutions that does not go "
        "through solving, and the equation itself supplies one. Written as "
        "y' = f(t, y), it assigns a slope to every point of the plane. It says "
        "nothing about which curve you are on — only which direction you must "
        "travel if you are at that point. Drawing those directions turns an "
        "equation into a picture of every solution at once.\n\n"
        "The other question this lesson settles comes before all of it. Ahead "
        "of spending an hour on a technique it is worth knowing whether there "
        "is anything to find: whether a solution through a given point exists, "
        "and whether it is the only one. Both can fail, and the conditions "
        "under which they do not fail are checkable without solving anything."
    ),
    derivation=(
        Passage(
            prose="Read the equation as an instruction rather than a problem. "
                  "At each point of the plane it names a number, and that "
                  "number is the slope any solution through that point must "
                  "have. Draw a short segment of that slope at each point and "
                  "the result is a field of directions.",
            latex=r"\text{at } (t_0, y_0): \quad "
                  r"\text{slope} = f(t_0, y_0)",
        ),
        Passage(
            prose="A solution is then exactly a curve that is everywhere "
                  "tangent to the field. This is a restatement, not an "
                  "approximation: the graph of any solution can be traced by "
                  "following the segments, and any curve that follows them "
                  "solves the equation. What the picture gives up is "
                  "precision; what it gains is every solution rather than one.",
            latex=r"y'(t) = f(t, y(t)) \;\Longleftrightarrow\; "
                  r"\text{the graph is tangent to the field}",
        ),
        Passage(
            prose="Two features of the field can be read off directly. Where f "
                  "vanishes the segments are horizontal, and that curve — the "
                  "nullcline — separates the region where solutions rise from "
                  "the region where they fall. And if f never mentions t, "
                  "every vertical slice of the field is identical, which is "
                  "why the solutions of an autonomous equation are horizontal "
                  "shifts of one another.",
            latex=r"f(t, y) = f(y) \;\Longrightarrow\; y(t) "
                  r"\text{ solves it} \Rightarrow y(t - c) \text{ does too}",
        ),
        Passage(
            prose="Now the prior question. Continuity of f near a point is "
                  "enough to guarantee that *some* solution passes through it: "
                  "the field is defined there and does not jump, so there is a "
                  "direction to follow and following it gets somewhere. That "
                  "is existence, and it is the cheaper half.",
            latex=r"f \text{ continuous near } (t_0, y_0) "
                  r"\;\Longrightarrow\; \text{at least one solution}",
        ),
        Passage(
            prose="Uniqueness costs more, and why is visible in the field. If "
                  "the slope can change arbitrarily fast as y changes, two "
                  "curves can leave the same point and separate. Requiring the "
                  "y-derivative of f to be continuous as well bounds how "
                  "quickly the field can turn as you move vertically, and that "
                  "bound is what forces the curve to be the only one.",
            latex=r"f,\ \partial f/\partial y \text{ continuous near } "
                  r"(t_0, y_0) \;\Longrightarrow\; \text{exactly one}",
        ),
        Passage(
            prose="Read the theorem for what it does not claim. It is local — "
                  "it promises a solution on some interval around the starting "
                  "time and says nothing about how wide, which is how a "
                  "well-behaved equation can have a solution that escapes to "
                  "infinity in finite time. And its hypotheses are sufficient, "
                  "not necessary: failing them means the theorem is silent, "
                  "not that uniqueness fails.",
            latex=r"y' = y^2,\ y(0) = 1 \;\Longrightarrow\; "
                  r"y = \frac{1}{1 - t}, \text{ only for } t < 1",
        ),
    ),
    prerequisites=("basics",),
    figure="slope_field",
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
            commentary=(
                "Take up the comparison this example exists for. Solve it, then look "
                "back at the field: the line along which the slope is zero is the "
                "nullcline, and the exponential term in the answer is what carries "
                "solutions away from it on both sides. The picture said that before "
                "any integration did.\n\n"
                "Then watch one solution behave differently from the rest. A single "
                "member of the family has no exponential term at all and runs "
                "straight along the field, and every other solution is that one plus "
                "a growing multiple of an exponential. Reading a field for the curve "
                "everything else peels away from is a habit worth forming here, "
                "because it is how the phase-plane lessons in the next unit are read."
            ),
        ),
        Example(
            equation="y' = t/y",
            conditions="y(0) = 2",
            why="f = t/y is undefined on the whole line y = 0, and the answer "
                "shows what that costs: the solution exists only while it "
                "stays away from it, and the ± branches never meet.",
            commentary=(
                "Watch the algebra force a choice the equation never made. What comes "
                "out is a relation in y squared, so extracting y needs a sign, and "
                "the initial condition supplies it — a curve starting above the bad "
                "line stays above it, because crossing would require the two branches "
                "to meet.\n\n"
                "Then read the interval, not just the formula. The solution is "
                "defined only while the expression under the root stays positive, so "
                "the answer comes with a domain attached and the domain depends on "
                "where it started. This is the local half of the existence theorem "
                "made concrete, and it is why the theorem promises an interval rather "
                "than a solution."
            ),
        ),
        # PED-05. The lesson says this equation has two solutions through the
        # origin, and the Solver Lab answers y = 0 and nothing else. Made into
        # an example so the contradiction is the lesson rather than a surprise.
        Example(
            equation="y' = y**(1/3)",
            conditions="y(0) = 0",
            why="∂f/∂y = 1/(3y^(2/3)) is infinite on y = 0, so the uniqueness "
                "half of the theorem has nothing to say at the origin, and "
                "separation finds a solution that is not the obvious one.",
            commentary=(
                "Notice first what separation did not find. Dividing by y^(1/3) "
                "assumed it was not zero, and y ≡ 0 is exactly the solution that "
                "division threw away: it passes through the origin, its slope is "
                "zero, and y^(1/3) is zero there too. So this condition is met by "
                "two different curves, (2t/3)^(3/2) and the constant zero, and in "
                "fact by infinitely many — stay at zero until any t = a, then leave "
                "along (2(t − a)/3)^(3/2).\n\n"
                "Then put it into the Solver Lab and watch a numerical method "
                "choose. Started exactly at y = 0, every step sees a slope of zero "
                "and the answer is y ≡ 0, reported as a success, while the Lab "
                "warns that the uniqueness hypothesis fails at the start. Neither "
                "answer is wrong. A method returns one solution, and only the "
                "theorem can tell you whether there was only one to return."
            ),
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
        # PED-07. The content above is the ∂f/∂y form deliberately -- it is the
        # one a student can check -- and this note does not change that. It
        # exists so that someone who wants to read further can search for what
        # they were taught: without the names, nothing here is findable.
        Note(
            "Its name, for reading further",
            "Books call the uniqueness half the Picard–Lindelöf theorem, and "
            "usually state it with a weaker-looking hypothesis: that f is "
            "Lipschitz in y, meaning |f(t, y₁) − f(t, y₂)| ≤ L·|y₁ − y₂| for "
            "some constant L near the point. A continuous ∂f/∂y implies that "
            "— take L to be the largest |∂f/∂y| nearby — so the test taught "
            "here is a special case of the textbook one, and y^{1/3} fails "
            "both for the same reason.",
            r"|f(t, y_1) - f(t, y_2)| \leq L\,|y_1 - y_2|",
            kind="aside",
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
        Choice(
            key="q-figure",
            prompt="In the figure, drag a down to −1 and b to 0, so the "
                   "equation is y′ = −y. Now read the dashes rather than any "
                   "curve: what do they say about every solution?",
            figure="slope_field",
            options=(
                "Every solution approaches y = 0, from whichever side it "
                "started on",
                "Solutions above the axis rise and those below it fall, so "
                "they separate",
                "Solutions cross the axis and oscillate about it",
                "It depends on the initial condition, and the field cannot "
                "say",
            ),
            answer=0,
            becauses=(
                "The slope is −y, so it is negative wherever y is positive "
                "and positive wherever y is negative. Every dash leans "
                "towards the axis, and a solution curve has no choice but to "
                "follow them there.",
                "That is what a = +1 would give. Read the sign: with a = −1 a "
                "positive y has a negative slope, so the curve comes back "
                "down rather than running away.",
                "Nothing crosses the axis. y = 0 is itself a solution, and "
                "uniqueness says no other curve may touch it — so no curve "
                "can get to the other side of it.",
                "Answering exactly this, without solving anything, is what a "
                "slope field is for. Drop conditions anywhere you like and "
                "every curve does the same thing.",
            ),
        ),
    ),
    templates=(
        NumericTemplate(
            key="slope-at-a-point",
            title="Read the slope straight off the equation",
            mistakes=(
                ("{a}*{t0} + {b}*{y0}",
                 "t and y are swapped when substituting — the point is (t, "
                 "y), time first"),
            ),
            prompt="For y' = {a}*y + {b}*t, what slope does the field have "
                   "at the point (t, y) = ({t0}, {y0})?",
            answer="{a}*{y0} + {b}*{t0}",
            because="No solving is involved: the equation gives the slope at "
                    "every point, and the point is substituted into the "
                    "right-hand side. That is the whole of what a slope field "
                    "draws.",
            # No `latex`: it would have to be built from the source slots and
            # would read "y' = -1\,y + -2\,t", which nothing tidies -- and
            # the prompt states the equation already.
            hints=(
                "The equation already is the answer, once the point is put "
                "into it.",
                "Substitute y = {y0} and t = {t0} into the right-hand "
                "side, and evaluate.",
            ),
            slots=(("a", (-2, -1, 1, 2)), ("b", (-2, -1, 2, 3)),
                   ("t0", (0, 1, 2)), ("y0", (-2, -1, 2, 3))),
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
    figure="level_curves",
    motivation=(
        "Separation needs a product; the integrating factor needs linearity in "
        "y. An equation like 2ty + (t² + 3y²)y' = 0 offers neither — y "
        "appears in both coefficients and nothing separates. It looks like a "
        "dead end, and then it comes out in three lines. That is the "
        "interesting part, because the reason has nothing to do with either "
        "earlier method.\n\n"
        "The idea is to stop looking for y as a function of t and look for a "
        "*surface* instead. Many first-order equations are secretly the "
        "statement that some quantity built from t and y does not change along "
        "a solution. Conservation of energy has exactly this form, and so does "
        "every level curve of every function: if a function of two variables "
        "is held constant, differentiating along the curve produces a "
        "first-order equation — and running that backwards is the whole "
        "method.\n\n"
        "This also changes what counts as an answer. What comes out here is a "
        "relation between t and y, not a formula for y, and often it cannot be "
        "untangled into one. That is a feature rather than a shortfall: the "
        "level curve is the honest description of the solution, and insisting "
        "on y = something would either fail outright or force a choice of "
        "branch the equation never made."
    ),
    derivation=(
        Passage(
            prose="Start from the answer and work backwards. Suppose some "
                  "function of t and y stays constant along a solution curve. "
                  "Differentiate that statement with respect to t, using the "
                  "chain rule for a function of two variables, and a "
                  "first-order equation falls out.",
            latex=r"F(t, y(t)) = C \;\Longrightarrow\; "
                  r"F_t + F_y\,\frac{dy}{dt} = 0",
        ),
        Passage(
            prose="Compare that with an equation presented as one coefficient "
                  "plus another times y'. It is solved by setting F equal to a "
                  "constant the moment those two coefficients are the two "
                  "partial derivatives of a single F. So the entire method "
                  "reduces to one question: given the coefficients, does such "
                  "an F exist? If it does, the work is already over.",
            latex=r"M(t, y) + N(t, y)\,y' = 0 \quad\text{with}\quad "
                  r"M = F_t,\; N = F_y",
        ),
        Passage(
            prose="That question has a cheap test, and it comes from a fact "
                  "about second derivatives: for a function whose second "
                  "partials are continuous, differentiating in either order "
                  "gives the same result. Apply it to the F we are hoping for.",
            latex=r"F_{ty} = F_{yt} \;\Longrightarrow\; "
                  r"\frac{\partial M}{\partial y} = "
                  r"\frac{\partial N}{\partial t}",
        ),
        Passage(
            prose="This is why exactness is a test rather than a formula: two "
                  "derivatives and a comparison decide, before any integration, "
                  "whether the method applies. And the condition is not a "
                  "technicality invented for the occasion — it is the symmetry "
                  "of second derivatives. On a rectangle where the "
                  "coefficients behave, the converse holds too, so the test is "
                  "exactly right and not merely necessary.",
            latex=r"M_y = N_t \;\Longleftrightarrow\; "
                  r"F \text{ exists (on a rectangle)}",
        ),
        Passage(
            prose="Constructing F is then bookkeeping. Integrate the first "
                  "coefficient in t: that recovers F up to anything a "
                  "t-derivative would have destroyed — so the leftover is a "
                  "function of y alone, not a constant. Differentiating the "
                  "result in y and matching against the second coefficient "
                  "pins it down.",
            latex=r"F = \int M\,dt + g(y), \qquad F_y = "
                  r"\frac{\partial}{\partial y}\int M\,dt + g'(y) = N",
        ),
        Passage(
            prose="One built-in consistency check. When the equation really is "
                  "exact, that last matching leaves an expression in y alone, "
                  "with every t cancelling. If a t survives, either the test "
                  "was misapplied or the algebra slipped — the cancellation is "
                  "not luck, it is the exactness condition showing up again "
                  "one step later.",
            latex=r"g'(y) = N - \frac{\partial}{\partial y}\int M\,dt"
                  r"\quad\text{must be free of } t",
        ),
    ),
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
            commentary=(
                "Watch the two partial derivatives agree before anything else "
                "happens. That agreement is not a formality — it is the entire "
                "licence for the rest of the working, and had it failed the remaining "
                "lines would be meaningless rather than merely wrong.\n\n"
                "Then watch the potential get built. Integrating in t leaves an "
                "unknown *function of y*, not an unknown constant, because anything "
                "in y alone has no t-derivative to have been recovered. Matching "
                "against the other coefficient pins it down — and notice that every t "
                "cancels when it does. That cancellation is the exactness condition "
                "turning up again one step later, and it is the check that the "
                "working held."
            ),
        ),
        Example(
            equation="y' = -(2*t + 3*y)/(3*t + 4*y)",
            conditions="",
            why="Exact and homogeneous at once. This application narrates it "
                "as a substitution, because that is the technique a course "
                "meets first — a reminder that a method applying does not make "
                "it the method to use.",
            commentary=(
                "Run the exactness test by hand alongside the narrated working. The "
                "two partials agree, so the potential could have been constructed "
                "instead, and the relation it produces is the same family of curves "
                "in different clothing.\n\n"
                "Which route is shorter depends on the equation and not on a rule, "
                "and that is worth sitting with: an equation can have two honest "
                "solutions that look nothing alike, and neither is the right one. "
                "Recognising several applicable methods and picking among them is a "
                "different skill from carrying any of them out, and it is the one an "
                "exam actually tests."
            ),
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
        # PED-06: where the method itself stops, not a mistake a student makes.
        Note(
            "Where it stops: most equations are not exact",
            "Exactness is a coincidence of partial derivatives, and most "
            "equations lack it. The rescue is an integrating factor, and the "
            "usual ones exist only in special cases: a factor depending on t "
            "alone exists exactly when (M_y − N_t)/N depends on t alone. When "
            "neither that nor its y-counterpart does, the textbook routes have "
            "nothing to offer.",
            r"\mu(t) \text{ exists} \Leftrightarrow \frac{M_y - N_t}{N} \text{ "
            r"depends on } t \text{ only}",
            "pitfall",
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
    figure="substitution",
    motivation=(
        "Four techniques in, the pattern is that each one recognises a shape. "
        "That raises an obvious question about everything else: is an equation "
        "matching none of the four simply out of reach? Usually not — because "
        "an equation can be the wrong shape in the variables it is written in "
        "and the right shape in different ones.\n\n"
        "The move is familiar from integration. A substitution does not make "
        "an integral easier in any absolute sense; it rewrites it as one "
        "already known. The same works here, and with more leverage, because "
        "the target is not a table of integrals but a technique — turning an "
        "equation into a separable or a linear one is enough, since those are "
        "solved.\n\n"
        "Two substitutions cover most of what a first course meets, and "
        "neither is arbitrary. Each is the substitution suggested by a "
        "*symmetry* of the equation, which is why it works rather than being a "
        "lucky guess. When the right-hand side can only see the ratio of y to "
        "t, the ratio is the natural unknown; when the nonlinearity in y is a "
        "single power, a power of y is."
    ),
    derivation=(
        Passage(
            prose="Take the first case: the right-hand side depends on y and t "
                  "only through their ratio. There is a test for it that does "
                  "not require spotting the ratio by eye — scale both "
                  "variables by the same factor, and if the right-hand side is "
                  "unchanged then it cannot be measuring anything but the "
                  "ratio.",
            latex=r"f(\lambda t, \lambda y) = f(t, y) \;\Longrightarrow\; "
                  r"f(t, y) = F(y/t)",
        ),
        Passage(
            prose="So make the ratio the unknown, which means y is t times the "
                  "new variable. Differentiate that as a product — this is the "
                  "step to get right, and dropping the product rule here is "
                  "the single most common error in the method.",
            latex=r"v = y/t \;\Longrightarrow\; y = t\,v "
                  r"\;\Longrightarrow\; y' = v + t\,v'",
        ),
        Passage(
            prose="Substitute and watch what happens. The lone v cancels "
                  "against the right-hand side, leaving t times v' equal to a "
                  "function of v with no t anywhere in it — a function of t "
                  "times a function of v. It is separable, by construction "
                  "rather than by luck.",
            latex=r"v + t v' = F(v) \;\Longrightarrow\; "
                  r"v' = \frac{F(v) - v}{t}",
        ),
        Passage(
            prose="The second case is an equation that would be linear except "
                  "for a single power of y on the right. Since exactly one "
                  "power is in the way, look for a power of y that flattens "
                  "it — and rather than remembering which, leave the exponent "
                  "unnamed and let the algebra choose it.",
            latex=r"y' + p(t)\,y = q(t)\,y^{n}, \qquad v = y^{k} "
                  r"\text{ for some } k",
        ),
        Passage(
            prose="Differentiate the new variable, divide the equation through "
                  "by that power of y to isolate the pieces, and compare the "
                  "two. They match for one value of k, and that is where the "
                  "substitution comes from — it is forced, not memorised. It "
                  "needs the exponent to be neither zero nor one, which costs "
                  "nothing: both of those cases are already linear.",
            latex=r"v' = k\,y^{k-1}y' \;\text{ matches }\; "
                  r"y^{-n}y' + p\,y^{1-n} = q \;\Longrightarrow\; k = 1 - n",
        ),
        Passage(
            prose="With that exponent the equation in the new variable is "
                  "linear, so the integrating factor finishes it, and y comes "
                  "back by undoing the power. Both substitutions carry the "
                  "same moral: the work is in recognising which change of "
                  "variable the equation is asking for, and after that there "
                  "is nothing new to learn.",
            latex=r"v' + (1-n)p\,v = (1-n)q \;\Longrightarrow\; "
                  r"y = v^{1/(1-n)}",
        ),
    ),
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
            commentary=(
                "Confirm the shape before substituting. Scale both variables by the "
                "same factor and the right-hand side is unchanged, which is the test "
                "— dividing numerator and denominator by t squared then leaves the "
                "ratio alone, and that is why the ratio is the variable to use.\n\n"
                "Two lines then carry the method. First the differentiation of y as a "
                "product of t and the new variable: the extra term is where "
                "everything happens, and dropping it is the commonest way to lose "
                "this problem. Then the substituted equation separating, with the "
                "lone copy of the new variable cancelling against the right-hand side "
                "exactly as promised. The condition is applied last, after the "
                "substitution is undone, and it is what chooses the sign."
            ),
        ),
        Example(
            equation="y' + y = t*y**3",
            conditions="y(0) = 1",
            why="Bernoulli with n = 3. The derivation visibly turns into the "
                "integrating-factor derivation you already know, which is the "
                "whole point of the substitution.",
            commentary=(
                "Rather than taking the exponent on trust, watch it fall out. "
                "Dividing through by y cubed produces exactly the combination that "
                "the derivative of y to the minus two supplies, and no other power of "
                "y would have matched. The substitution is forced by the algebra, not "
                "remembered from a table.\n\n"
                "After it, the working visibly becomes the integrating-factor working "
                "from two lessons ago. That is the whole economy of the method: it "
                "buys no new machinery, it only reaches machinery already built. Note "
                "the last step is a fractional power, so a branch has to be chosen, "
                "and the initial condition chooses it."
            ),
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
        # PED-06: where the method itself stops, not a mistake a student makes.
        Note(
            "Where it stops: the form has to match exactly",
            "Each substitution is built for one shape. Homogeneous needs f(λt, "
            "λy) = f(t, y); Bernoulli needs y' + p y = q yⁿ and nothing else. "
            "y' = y² + t is neither — it is a Riccati equation, which has no "
            "general elementary method at all. A substitution that does not fit"
            " the equation does not fail loudly; it just produces something no "
            "easier.",
            r"y' = y^{2} + t: \ \text{neither homogeneous nor Bernoulli}",
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
        ClassifyTemplate(
            key="which-first-order-method",
            title="Which method would you reach for first?",
            prompt="Read it, decide, and say what decided it. Do not solve "
                   "it.",
            options=("separable", "1st_linear", "1st_exact",
                     "1st_homogeneous_coeff_best", "Bernoulli"),
            cases=(
                Case(
                    equation="y' = y**2*cos(t)",
                    technique="separable",
                    why="A function of t times a function of y, which is the "
                        "whole test. It is not linear — y appears squared — "
                        "so no integrating factor will touch it.",
                    tier="easier",
                ),
                Case(
                    equation="y' = t*(1 + y**2)",
                    technique="separable",
                    why="Already factored for you: t in one bracket, "
                        "everything in y in the other. Divide by 1 + y² and "
                        "both sides integrate.",
                    tier="easier",
                ),
                Case(
                    equation="y' = cos(t)/y",
                    technique="separable",
                    why="A quotient, but the numerator is all t and the "
                        "denominator all y. Multiply up by y·dt and it is "
                        "separated.",
                    tier="typical",
                ),
                Case(
                    equation="y' + 2*y = t",
                    technique="1st_linear",
                    why="Linear in y and already in standard form, with "
                        "p = 2. The t on the right is what stops it "
                        "separating: there is no way to factor it into a "
                        "t-part times a y-part.",
                    tier="easier",
                ),
                Case(
                    equation="t*y' + y = t**3",
                    technique="1st_linear",
                    why="Divide by t: y' + y/t = t², linear with p = 1/t. "
                        "The left side was already (t·y)' — the integrating "
                        "factor arriving before it was asked for.",
                    tier="typical",
                ),
                Case(
                    equation="y' + y/t = exp(t)",
                    technique="1st_linear",
                    why="Linear with p = 1/t, so μ = t. The forcing term e^t "
                        "never enters the choice of μ, however awkward it "
                        "looks.",
                    tier="typical",
                ),
                Case(
                    equation="y' = (t + y)/t",
                    technique="1st_linear",
                    why="It looks homogeneous, and it is — but expand it "
                        "first: y' = 1 + y/t is linear, with p = −1/t. The "
                        "integrating factor is the shorter route, and it is "
                        "the one to reach for.",
                    tier="harder",
                ),
                Case(
                    equation="y' = (t**2 + y**2)/(t*y)",
                    technique="1st_homogeneous_coeff_best",
                    why="Divide top and bottom by t²: the right-hand side "
                        "becomes (1 + (y/t)²)/(y/t), which depends on "
                        "nothing but the ratio. So v = y/t.",
                    tier="typical",
                ),
                Case(
                    equation="y' = (2*t*y + y**2)/(2*t**2)",
                    technique="1st_homogeneous_coeff_best",
                    why="Every term is degree two over degree two, so "
                        "dividing through by t² leaves a function of y/t "
                        "alone — which is what homogeneous means.",
                    tier="typical",
                ),
                Case(
                    equation="y' = (y - t)/(y + t)",
                    technique="1st_homogeneous_coeff_best",
                    why="Divide top and bottom by t and the right-hand side "
                        "is (y/t − 1)/(y/t + 1). Nothing separates, and y "
                        "appears in a denominator so it is not linear "
                        "either.",
                    tier="harder",
                ),
                Case(
                    equation="y' + y = t*y**2",
                    technique="Bernoulli",
                    why="Linear apart from the y² on the right. That is the "
                        "Bernoulli shape with n = 2, and v = 1/y turns it "
                        "into a linear equation.",
                    tier="typical",
                ),
                Case(
                    equation="y' + 3*y/t = y**2",
                    technique="Bernoulli",
                    why="p is 3/t rather than a constant, which changes "
                        "nothing: the shape is still linear except for one "
                        "power of y on the right.",
                    tier="harder",
                ),
                Case(
                    equation="y' = -(2*t + y)/(t + 3*y**2)",
                    technique="1st_exact",
                    why="Write it as (2t + y) + (t + 3y²)·y' = 0. Then "
                        "∂M/∂y = 1 and ∂N/∂t = 1, so the left-hand side is "
                        "already the derivative of some F(t, y).",
                    tier="typical",
                ),
                Case(
                    equation="(2*t + y**2)*y' = -(2*y + 1)",
                    technique="1st_exact",
                    why="M = 2y + 1 and N = 2t + y², and both cross "
                        "derivatives are 2. Nothing separates, and the y² "
                        "stops it being linear.",
                    tier="harder",
                ),
            ),
        ),
    ),
)


LESSONS = (BASICS, SLOPEFIELDS, SEPARABLE, LINEAR, EXACT,
           SUBSTITUTIONS)
