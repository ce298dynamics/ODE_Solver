"""The course itself: what each technique is, and questions to try.

The rest of the Learning Hub is *tools* -- bring an equation and they work on
it. This is the part that assumes you do not yet know which equation to bring.
Seven lessons, each with notes, a worked example, and practice.

Two decisions about the practice questions are worth stating, because they are
what keep this from being a quiz with a stored answer key.

**Solve-it questions are graded by mathematics, not by comparison.** The answer
is substituted into the equation and simplified, through the same
`symbolic.check_answer` the Solve Step by Step screen uses. Any correct form
passes -- ``3e^{-2t}``, ``3/e^{2t}``, ``3*exp(-t)*exp(-t)`` are one answer -- and
nothing is marked wrong merely for being spelled differently from what the
author had in mind. Where simplification cannot decide, the verdict is "cannot
tell", never "wrong".

**Multiple-choice questions exist for what that cannot reach.** *Which technique
solves this* is the question a course actually tests and a substitution check
can say nothing about, so those have a stored answer -- and every one of them
carries the reason, because a tick that does not say why teaches nothing.

The worked example of each lesson is an equation the narrator can already
handle, so the working shown is generated and checked rather than transcribed.
An example that drifted out of step with the tool that explains it would be
worse than none.

Content only -- no PySide6, no Qt -- so the lessons can be read, counted and
tested without an interface.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "Note",
    "Choice",
    "Solve",
    "Lesson",
    "LESSONS",
    "by_key",
    "questions_of",
    "grade_choice",
]


@dataclass(frozen=True)
class Note:
    """One idea, with the formula that carries it."""

    heading: str
    body: str
    #: Displayed centred beneath the prose. LaTeX, typeset like everything else.
    latex: str = ""


@dataclass(frozen=True)
class Choice:
    """A question with one right option and a reason for it."""

    key: str
    prompt: str
    options: tuple[str, ...]
    #: Index into `options`.
    answer: int
    #: Why -- shown once answered, right or wrong. A tick that does not explain
    #: itself teaches nothing.
    because: str
    #: The equation the question is about, if it is about one.
    latex: str = ""

    kind: str = field(default="choice", init=False)


@dataclass(frozen=True)
class Solve:
    """Solve it and type the answer; graded by substitution."""

    key: str
    prompt: str
    #: As it would be typed into the editor, so the grader parses it the same
    #: way the rest of the application does.
    equation: str
    conditions: str = ""
    hint: str = ""

    kind: str = field(default="solve", init=False)


@dataclass(frozen=True)
class Lesson:
    key: str
    title: str
    #: One sentence: what this is for.
    summary: str
    notes: tuple[Note, ...]
    #: An equation the narrator can work through, shown on request.
    example: str
    example_conditions: str
    questions: tuple[Choice | Solve, ...]
    #: The Hub screen that does this technique, offered as a way on.
    tool: str
    #: Which narrator explains the example: "steps" or "laplace".
    narrator: str = "steps"


# ---------------------------------------------------------------------------
# 1. Separable equations
# ---------------------------------------------------------------------------

_SEPARABLE = Lesson(
    key="separable",
    title="Separable equations",
    summary="The first technique, and the one every other first-order method "
            "falls back on when it can.",
    tool="steps",
    example="y' = y*(1 - y)",
    example_conditions="y(0) = 0.1",
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
        ),
        Note(
            "The step that can lose a solution",
            "Dividing by g(y) assumes g(y) is not zero. Wherever g(y₀) = 0, the "
            "constant function y = y₀ solves the equation on its own — an "
            "equilibrium. The logistic equation has two, y = 0 and y = 1, and "
            "neither comes out of the general formula.",
            r"g(y_0) = 0 \;\Longrightarrow\; y \equiv y_0 \text{ is a solution}",
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
            because="t·y² is a function of t times a function of y. The others "
                    "mix the variables in a way no factoring undoes — a sum is "
                    "not a product.",
        ),
        Solve(
            key="q2",
            prompt="Solve it, and apply the condition.",
            equation="y' = 2*t*y",
            conditions="y(0) = 1",
            hint="Separate to dy/y = 2t dt. The left integrates to ln|y|.",
        ),
        Solve(
            key="q3",
            prompt="Newton's cooling: coffee at 95 °C in a 20 °C room.",
            equation="y' = -0.2*(y - 20)",
            conditions="y(0) = 95",
            hint="Separate to dy/(y − 20) = −0.2 dt. The 20 does not go away; "
                 "it is what the answer decays towards.",
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
            because="Setting y' = 0 needs y(1 − y) = 0, so y = 0 or y = 1. "
                    "These are exactly the values you divided by when "
                    "separating, which is why they are not in the general "
                    "answer.",
        ),
        Solve(
            key="q5",
            prompt="A harder separation — the answer is not an exponential.",
            equation="y' = t/y",
            conditions="y(0) = 2",
            hint="Separating gives y dy = t dt. Both sides integrate to "
                 "squares.",
        ),
    ),
)


# ---------------------------------------------------------------------------
# 2. First-order linear
# ---------------------------------------------------------------------------

_LINEAR = Lesson(
    key="linear",
    title="First-order linear, and the integrating factor",
    summary="What to do when the equation is linear in y but refuses to "
            "separate.",
    tool="steps",
    example="y' + 2*y = t",
    example_conditions="",
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
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="What is the integrating factor for y' + 3y = e^t ?",
            latex=r"y' + 3y = e^{t}",
            options=(r"e^{3t}", r"e^{-3t}", r"3e^{t}", r"e^{t^{2}/2}"),
            answer=0,
            because="p(t) = 3, so μ = e^{∫3 dt} = e^{3t}. The sign trips people "
                    "up: μ uses +∫p, and the decay appears later when you "
                    "divide by μ.",
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
            because="Linear means linear in y and y′ — each appearing to the "
                    "first power and not multiplied together. y² breaks that. "
                    "Coefficients may depend on t however they like.",
        ),
        Solve(
            key="q3",
            prompt="Standard form, integrating factor, integrate.",
            equation="y' + y = t",
            conditions="y(0) = 0",
            hint="μ = e^t. The right side becomes ∫t·e^t dt, which needs "
                 "integration by parts.",
        ),
        Solve(
            key="q4",
            prompt="Here p(t) is not constant, which is what the method is for.",
            equation="t*y' + y = t",
            conditions="y(1) = 1",
            hint="Divide by t first. Notice the left side was already (t·y)′ "
                 "before you did anything — sometimes μ is staring at you.",
        ),
        Solve(
            key="q5",
            prompt="A mixing tank: 100 litres, 5 l/min in at 0.4 kg/l, "
                   "well stirred, same rate out.",
            equation="y' = 2 - 0.05*y",
            conditions="y(0) = 5",
            hint="Rearrange to y′ + 0.05y = 2. It settles at 40 kg — check "
                 "your answer does.",
        ),
    ),
)


# ---------------------------------------------------------------------------
# 3. Characteristic roots
# ---------------------------------------------------------------------------

_ROOTS = Lesson(
    key="roots",
    title="Second order: characteristic roots",
    summary="Constant coefficients, no forcing — where a differential equation "
            "becomes a quadratic.",
    tool="steps",
    example="y'' + 3*y' + 2*y = 0",
    example_conditions="y(0) = 1, y'(0) = 0",
    notes=(
        Note(
            "Guess an exponential",
            "Try y = e^{rt}. Every derivative brings down a factor of r and "
            "leaves the exponential alone, so the whole equation collapses to a "
            "polynomial in r. Divide by e^{rt}, which is never zero, and the "
            "calculus is gone.",
            r"y = e^{rt} \;\Longrightarrow\; ar^{2} + br + c = 0",
        ),
        Note(
            "Two distinct real roots",
            "Each root contributes its own exponential, and the general "
            "solution is any combination of them. Two constants, matching the "
            "order of the equation.",
            r"y = C_1 e^{r_1 t} + C_2 e^{r_2 t}",
        ),
        Note(
            "A repeated root",
            "One root cannot supply two independent solutions, so the second is "
            "the first multiplied by t. This is the case people forget, and it "
            "is the critically damped one — the fastest return to rest without "
            "overshooting.",
            r"y = (C_1 + C_2 t)\,e^{rt}",
        ),
        Note(
            "A complex pair",
            "Complex roots a ± bi give real solutions. Euler's formula turns "
            "the exponentials into a cosine and a sine, with the real part "
            "setting the envelope and the imaginary part the oscillation. This "
            "is the underdamped case.",
            r"y = e^{at}\left(C_1 \cos bt + C_2 \sin bt\right)",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="y'' + 4y' + 4y = 0. What does the solution look like?",
            latex=r"y'' + 4y' + 4y = 0",
            options=(
                "Two different decaying exponentials",
                "An oscillation inside a decaying envelope",
                "A decaying exponential and t times the same one",
                "Growth without bound",
            ),
            answer=2,
            because="r² + 4r + 4 = (r + 2)², a repeated root at −2. A repeated "
                    "root brings in the extra factor of t: y = (C₁ + C₂t)e^{−2t}. "
                    "Critically damped.",
        ),
        Choice(
            key="q2",
            prompt="Which equation oscillates?",
            options=(
                "y'' + 5y' + 6y = 0",
                "y'' + 2y' + 5y = 0",
                "y'' + 4y' + 4y = 0",
                "y'' − y = 0",
            ),
            answer=1,
            because="Its discriminant is 4 − 20 = −16, so the roots are "
                    "−1 ± 2i — a complex pair, which is what oscillation means. "
                    "The others have real roots and never cross zero more than "
                    "once.",
        ),
        Solve(
            key="q3",
            prompt="Distinct real roots.",
            equation="y'' + 3*y' + 2*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            hint="r² + 3r + 2 = (r+1)(r+2). Two conditions pin two constants.",
        ),
        Solve(
            key="q4",
            prompt="The repeated-root case.",
            equation="y'' + 2*y' + y = 0",
            conditions="y(0) = 1, y'(0) = 1",
            hint="(r+1)² = 0. Do not forget the t on the second solution — "
                 "without it you cannot satisfy both conditions.",
        ),
        Solve(
            key="q5",
            prompt="Simple harmonic motion.",
            equation="y'' + 9*y = 0",
            conditions="y(0) = 0, y'(0) = 3",
            hint="Roots ±3i, so no decaying envelope at all — pure oscillation.",
        ),
    ),
)


# ---------------------------------------------------------------------------
# 4. Undetermined coefficients
# ---------------------------------------------------------------------------

_UNDETERMINED = Lesson(
    key="undetermined",
    title="Forced equations: undetermined coefficients",
    summary="When something is driving the system, and you can guess the shape "
            "of its response.",
    tool="steps",
    example="y'' + 4*y = sin(t)",
    example_conditions="y(0) = 0, y'(0) = 1",
    notes=(
        Note(
            "The structure of the answer",
            "Solve the homogeneous equation first, then find any one solution "
            "of the forced equation. Every solution is the sum. This is worth "
            "understanding rather than memorising: the difference of two "
            "solutions of the forced equation solves the homogeneous one.",
            r"y = y_h + y_p",
        ),
        Note(
            "Guessing the particular solution",
            "For forcing that reproduces its own shape under differentiation — "
            "exponentials, polynomials, sines and cosines — guess that shape "
            "with unknown coefficients, substitute, and match terms. A sine "
            "brings in a cosine when differentiated, so guess both.",
            r"g(t) = \sin bt \;\Longrightarrow\; y_p = A\cos bt + B\sin bt",
        ),
        Note(
            "Resonance: the case that catches people",
            "If the guess already solves the homogeneous equation, substituting "
            "it gives zero and it can never produce the forcing term. Multiply "
            "by t and try again. Physically this is driving a system at its own "
            "natural frequency, and the t is the amplitude growing without "
            "bound.",
            r"y'' + y = \cos t \;\Longrightarrow\; y_p = \tfrac{1}{2}\,t\sin t",
        ),
        Note(
            "What it cannot do",
            "The guess has to be a finite set of shapes closed under "
            "differentiation. tan t and 1/t are not, and neither is anything "
            "with a corner or a jump in it. Those need variation of parameters "
            "or the Laplace transform.",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="What should you guess for y'' + y' + y = t² ?",
            latex=r"y'' + y' + y = t^{2}",
            options=(
                "y_p = At²",
                "y_p = At² + Bt + C",
                "y_p = At³",
                "y_p = Ae^{t}",
            ),
            answer=1,
            because="Differentiating t² produces t and then a constant, so all "
                    "three powers must be in the guess. Guessing At² alone "
                    "leaves terms nothing can cancel.",
        ),
        Choice(
            key="q2",
            prompt="For y'' + 4y = cos 2t, why is y_p = A cos 2t + B sin 2t "
                   "wrong?",
            latex=r"y'' + 4y = \cos 2t",
            options=(
                "The forcing is a cosine, so no sine is needed",
                "Both terms already solve the homogeneous equation, so "
                "substituting gives zero",
                "The coefficients cannot be found",
                "It is not wrong",
            ),
            answer=1,
            because="The homogeneous solutions are exactly cos 2t and sin 2t. "
                    "Anything built from them substitutes to zero and can never "
                    "equal cos 2t. Multiply by t: y_p = t(A cos 2t + B sin 2t). "
                    "This is resonance.",
        ),
        Solve(
            key="q3",
            prompt="Off resonance — the straightforward case.",
            equation="y'' + 4*y = sin(t)",
            conditions="y(0) = 0, y'(0) = 1",
            hint="Homogeneous roots are ±2i, and the forcing is at frequency 1. "
                 "No clash, so guess A cos t + B sin t.",
        ),
        Solve(
            key="q4",
            prompt="Resonant. Expect a t in the answer.",
            equation="y'' + y = cos(t)",
            conditions="y(0) = 0, y'(0) = 0",
            hint="The natural frequency is 1 and you are driving at 1. Multiply "
                 "the guess by t.",
        ),
        Solve(
            key="q5",
            prompt="Polynomial forcing.",
            equation="y'' + 3*y' + 2*y = t",
            conditions="y(0) = 0, y'(0) = 0",
            hint="Guess At + B, not just At — the derivative of the guess has "
                 "to be able to contribute too.",
        ),
    ),
)


# ---------------------------------------------------------------------------
# 5. Cauchy-Euler
# ---------------------------------------------------------------------------

_CAUCHY = Lesson(
    key="cauchy",
    title="Cauchy–Euler equations",
    summary="Variable coefficients that still come out in closed form, because "
            "the powers of t line up.",
    tool="steps",
    example="t**2*y'' + t*y' - y = 0",
    example_conditions="",
    notes=(
        Note(
            "How to recognise one",
            "Each derivative is multiplied by the matching power of t: t² with "
            "y'', t with y', and t⁰ with y. That balance is the whole point — "
            "it is what makes the substitution below cancel cleanly.",
            r"a t^{2} y'' + b t y' + c y = 0",
        ),
        Note(
            "Try a power instead of an exponential",
            "Exponentials do not help here. Try y = t^r: differentiating drops "
            "the power by one and the t^k in front puts it back, so every term "
            "becomes a multiple of t^r. Divide through and an equation in r is "
            "left — the indicial equation.",
            r"y = t^{r} \;\Longrightarrow\; a r(r-1) + b r + c = 0",
        ),
        Note(
            "The three cases again, with logs",
            "Same three cases as constant coefficients, with ln t where t used "
            "to be. That is not a coincidence: substituting t = e^s turns a "
            "Cauchy–Euler equation into a constant-coefficient one, and s = ln t.",
            r"t^{r_1},\ t^{r_2} \quad\mid\quad t^{r},\ t^{r}\ln t "
            r"\quad\mid\quad t^{a}\cos(b\ln t),\ t^{a}\sin(b\ln t)",
        ),
        Note(
            "Where it is valid",
            "The solutions involve t^r and ln t, so they are stated for t > 0. "
            "At t = 0 the leading coefficient vanishes and the equation stops "
            "being second order at all — a singular point, and conditions "
            "cannot be given there.",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="Which of these is a Cauchy–Euler equation?",
            options=(
                "t²y'' + 3ty' + y = 0",
                "t²y'' + 3y' + y = 0",
                "y'' + 3ty' + y = 0",
                "t y'' + 3t²y' + y = 0",
            ),
            answer=0,
            because="Only the first has t^k matching the k-th derivative: t² "
                    "with y'', t with y'. In the others the powers do not line "
                    "up and the substitution y = t^r leaves t behind.",
        ),
        Choice(
            key="q2",
            prompt="For t²y'' − 3ty' + 4y = 0 the indicial equation is "
                   "(r − 2)². What is the solution?",
            latex=r"t^{2}y'' - 3ty' + 4y = 0",
            options=(
                "y = C₁t² + C₂t^{−2}",
                "y = (C₁ + C₂t)t²",
                "y = t²(C₁ + C₂ ln t)",
                "y = C₁t² + C₂",
            ),
            answer=2,
            because="A repeated indicial root brings in ln t, not t — the "
                    "Cauchy–Euler counterpart of the extra factor of t in the "
                    "constant-coefficient case. The substitution t = e^s is why.",
        ),
        Solve(
            key="q3",
            prompt="Distinct indicial roots.",
            equation="t**2*y'' + t*y' - y = 0",
            hint="Substituting y = t^r gives r(r−1) + r − 1 = r² − 1.",
        ),
        Solve(
            key="q4",
            prompt="A repeated root — expect a logarithm.",
            equation="t**2*y'' - 3*t*y' + 4*y = 0",
            hint="r(r−1) − 3r + 4 = r² − 4r + 4 = (r−2)².",
        ),
    ),
)


# ---------------------------------------------------------------------------
# 6. Laplace transforms
# ---------------------------------------------------------------------------

_LAPLACE = Lesson(
    key="laplace",
    title="Laplace transforms",
    summary="Turn the differential equation into algebra — and handle forcing "
            "that switches on partway through.",
    tool="laplace",
    narrator="laplace",
    example="y'' + 3*y' + 2*y = sin(t)",
    example_conditions="y(0) = 1, y'(0) = 0",
    notes=(
        Note(
            "What it does",
            "The transform turns a function of t into a function of s, and — "
            "this is the point — it turns differentiation into multiplication. "
            "A differential equation becomes an algebraic one, which you solve "
            "with ordinary algebra and then transform back.",
            r"\mathcal{L}\{y'\} = sY(s) - y(0)",
        ),
        Note(
            "The initial conditions come in at the start",
            "Look at where y(0) appears: in the transform of the derivative "
            "itself. No arbitrary constants are ever introduced, so there is "
            "nothing to pin down at the end. This is the real difference from "
            "every other method here.",
            r"\mathcal{L}\{y''\} = s^{2}Y(s) - s\,y(0) - y'(0)",
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
            because="s²Y − s·y(0) − y'(0) = s²Y − 2s − 0. The y(0) term carries "
                    "the factor of s; it is y'(0) that does not. Swapping them "
                    "is the usual slip.",
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
            because="A forcing term switched on at t = 2 has no shape to guess "
                    "and does not separate, so undetermined coefficients and "
                    "separation both fail. The transform takes it as one extra "
                    "factor e^{−2s}. The others all have simpler routes.",
        ),
        Solve(
            key="q3",
            prompt="Transform, solve for Y(s), invert.",
            equation="y'' + 4*y = 0",
            conditions="y(0) = 0, y'(0) = 2",
            hint="Y(s) = 2/(s² + 4), which is a row of the table on sight.",
        ),
        Solve(
            key="q4",
            prompt="Needs partial fractions on the way back.",
            equation="y' + 2*y = t",
            conditions="y(0) = 0",
            hint="Y(s) = 1/(s²(s+2)). Split it into pieces in 1/s, 1/s² and "
                 "1/(s+2).",
        ),
        Solve(
            key="q5",
            prompt="A switch thrown at t = 2. Type Heaviside(t-2) for the step.",
            equation="y' + y = Heaviside(t - 2)",
            conditions="y(0) = 0",
            hint="Y(s) = e^{−2s}/(s(s+1)). The e^{−2s} is a delay, not "
                 "something to expand: invert the rest and shift it.",
        ),
    ),
)


# ---------------------------------------------------------------------------
# 7. Numerical methods
# ---------------------------------------------------------------------------

_NUMERICAL = Lesson(
    key="numerical",
    title="Euler and Runge–Kutta",
    summary="What to do when there is no closed form — which is almost always.",
    tool="byhand",
    example="y' = y",
    example_conditions="y(0) = 1",
    notes=(
        Note(
            "Euler's method",
            "The equation tells you the slope at any point. So take the slope "
            "where you are, follow it for a short step h, and repeat. That is "
            "the whole idea, and every other method here is a refinement of it.",
            r"y_{n+1} = y_n + h\,f(t_n, y_n)",
        ),
        Note(
            "Order: what halving h buys you",
            "Euler is first order — halve the step and the error roughly halves. "
            "That is a poor return: ten times the work for ten times the "
            "accuracy. The order is the exponent in the error, and it is what "
            "separates a usable method from a toy.",
            r"\text{error} \approx C h^{p}, \qquad p = 1 \text{ for Euler}",
        ),
        Note(
            "Runge–Kutta 4",
            "Instead of one slope, sample four across the step and take a "
            "weighted average — the midpoint slopes counting double. Four times "
            "the work per step, but fourth order: halve h and the error drops "
            "by sixteen.",
            r"y_{n+1} = y_n + \tfrac{h}{6}\left(k_1 + 2k_2 + 2k_3 + k_4\right)",
        ),
        Note(
            "Why anyone bothers with adaptive steps",
            "A fixed h is either too small where the solution is calm or too "
            "large where it turns sharply. Real solvers estimate the error each "
            "step and change h to match — which is what the Solver Studio "
            "shows you happening.",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="One Euler step on y' = y from y(0) = 1 with h = 0.1. "
                   "What is y₁?",
            latex=r"y' = y,\quad y(0) = 1,\quad h = 0.1",
            options=("1.0", "1.1", "1.105", "1.21"),
            answer=1,
            because="y₁ = y₀ + h·f(t₀,y₀) = 1 + 0.1·1 = 1.1. The true value is "
                    "e^{0.1} ≈ 1.10517, so this one step is already short by "
                    "about 0.005.",
        ),
        Choice(
            key="q2",
            prompt="You halve h and the error drops to a sixteenth. What order "
                   "is the method?",
            options=("First", "Second", "Fourth", "Sixteenth"),
            answer=2,
            because="Error ≈ Ch^p, so halving h scales it by 2^{−p}. A "
                    "sixteenth means 2^p = 16, so p = 4 — the behaviour of RK4.",
        ),
        Choice(
            key="q3",
            prompt="Why does RK4 usually beat Euler even at equal *cost*?",
            options=(
                "It takes larger steps, so it needs fewer of them",
                "Four evaluations per step, but the error falls so much faster "
                "with h that far fewer steps are needed for a given accuracy",
                "It does not — Euler is cheaper per unit accuracy",
                "It avoids rounding error",
            ),
            answer=1,
            because="Cost is evaluations, not steps. RK4 costs four times as "
                    "much per step, but to get error ε it needs about ε^{−1/4} "
                    "steps against Euler's ε^{−1}. At any accuracy worth having, "
                    "RK4 wins by orders of magnitude.",
        ),
        Choice(
            key="q4",
            prompt="Which is true of a fixed-step method on a stiff problem?",
            options=(
                "It is more accurate than an adaptive one",
                "h must stay small enough for stability even where the solution "
                "is barely changing",
                "Stiffness only affects implicit methods",
                "It cannot be used at all",
            ),
            answer=1,
            because="Stiffness is a stability constraint, not an accuracy one. "
                    "An explicit method has to keep h inside its stability "
                    "region no matter how flat the solution has become — which "
                    "is exactly what makes stiff problems expensive.",
        ),
    ),
)


#: Every lesson, in the order a course meets them.
LESSONS: tuple[Lesson, ...] = (
    _SEPARABLE,
    _LINEAR,
    _ROOTS,
    _UNDETERMINED,
    _CAUCHY,
    _LAPLACE,
    _NUMERICAL,
)


def by_key(key: str) -> Lesson | None:
    for lesson in LESSONS:
        if lesson.key == key:
            return lesson
    return None


def questions_of(lesson: Lesson) -> tuple[Choice | Solve, ...]:
    return lesson.questions


def grade_choice(question: Choice, picked: int) -> bool:
    return picked == question.answer
