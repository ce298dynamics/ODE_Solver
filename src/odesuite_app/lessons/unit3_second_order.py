"""Unit 3 -- Second-order linear equations.

Edwards, Penney and Calvis 6e, chapter 3. The three techniques a first course
spends most of its second half on: reading a solution off the characteristic
roots, guessing a particular solution when something is driving the system, and
the one variable-coefficient family that still comes out in closed form.

Superposition and the Wronskian, variation of parameters, and the higher-order
case belong here too, and arrive with the narrator each needs.
"""

from __future__ import annotations

from .model import Choice, Example, Lesson, Note, Solve

__all__ = ["ROOTS", "UNDETERMINED", "CAUCHY", "LESSONS"]


ROOTS = Lesson(
    key="roots",
    title="Second order: characteristic roots",
    summary="Constant coefficients, no forcing — where a differential equation "
            "becomes a quadratic.",
    tool="steps",
    reference="Edwards 3.1–3.3",
    objectives=(
        "Turn a constant-coefficient equation into its characteristic "
        "polynomial, and say why that is allowed.",
        "Write the general solution in each of the three root cases.",
        "Recognise the repeated root, and supply the missing factor of t.",
        "Read damping behaviour off the roots without solving anything.",
    ),
    examples=(
        Example(
            equation="y'' + 3*y' + 2*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            why="Two distinct real roots — the case where the machinery is "
                "plainest, and the two conditions pin the two constants.",
        ),
        Example(
            equation="y'' + 2*y' + 5*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            why="A complex pair, −1 ± 2i. Watch the exponentials become a "
                "cosine and a sine, with the real part left outside as the "
                "decaying envelope.",
        ),
    ),
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
            "formula",
        ),
        Note(
            "A repeated root",
            "One root cannot supply two independent solutions, so the second is "
            "the first multiplied by t. This is the case people forget, and it "
            "is the critically damped one — the fastest return to rest without "
            "overshooting.",
            r"y = (C_1 + C_2 t)\,e^{rt}",
            "pitfall",
        ),
        Note(
            "A complex pair",
            "Complex roots a ± bi give real solutions. Euler's formula turns "
            "the exponentials into a cosine and a sine, with the real part "
            "setting the envelope and the imaginary part the oscillation. This "
            "is the underdamped case.",
            r"y = e^{at}\left(C_1 \cos bt + C_2 \sin bt\right)",
            "formula",
        ),
        Note(
            "The roots are the behaviour",
            "You can answer most questions about a system without solving it. "
            "Negative real parts mean it settles; a nonzero imaginary part "
            "means it oscillates on the way; a positive real part means it runs "
            "away. The sign of the discriminant decides which case you are in.",
            r"b^{2} - 4ac > 0 \ \mid\ = 0 \ \mid\ < 0",
            "aside",
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
            becauses=(
                "Two different exponentials need two *different* roots. The "
                "discriminant here is 16 − 16 = 0, so there is only one.",
                "Oscillation needs a complex pair, which needs a negative "
                "discriminant. Here it is exactly zero — the boundary case.",
                "r² + 4r + 4 = (r + 2)², a repeated root at −2. A repeated "
                "root brings in the extra factor of t: y = (C₁ + C₂t)e^{−2t}. "
                "Critically damped.",
                "The root is −2, which decays. Growth would need a root with a "
                "positive real part, and the factor of t is not enough to "
                "produce it.",
            ),
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
            becauses=(
                "r² + 5r + 6 = (r+2)(r+3): two real roots, so two decaying "
                "exponentials and no oscillation at all.",
                "Its discriminant is 4 − 20 = −16, so the roots are "
                "−1 ± 2i — a complex pair, which is what oscillation means. "
                "The others have real roots and never cross zero more than "
                "once.",
                "(r+2)² — a repeated real root. The extra factor of t can make "
                "it rise before it falls, but it crosses zero at most once.",
                "Roots ±1: one growing exponential and one decaying one. No "
                "oscillation, and unstable besides.",
            ),
        ),
        Solve(
            key="q3",
            prompt="Distinct real roots.",
            equation="y'' + 3*y' + 2*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            hints=(
                "Substitute y = e^{rt} to get r² + 3r + 2 = 0.",
                "It factors: (r+1)(r+2), so the roots are −1 and −2.",
                "y = C₁e^{−t} + C₂e^{−2t}. Two conditions pin two constants: "
                "C₁ = 2 and C₂ = −1.",
            ),
        ),
        Solve(
            key="q4",
            prompt="The repeated-root case.",
            equation="y'' + 2*y' + y = 0",
            conditions="y(0) = 1, y'(0) = 1",
            hints=(
                "r² + 2r + 1 = (r+1)², a repeated root at −1.",
                "A repeated root needs t on the second solution: "
                "y = (C₁ + C₂t)e^{−t}. Without it you cannot satisfy both "
                "conditions.",
                "y(0) = 1 gives C₁ = 1; differentiating and setting t = 0 "
                "gives C₂ − C₁ = 1, so C₂ = 2.",
            ),
        ),
        Solve(
            key="q5",
            prompt="Simple harmonic motion.",
            equation="y'' + 9*y = 0",
            conditions="y(0) = 0, y'(0) = 3",
            hints=(
                "r² + 9 = 0, so the roots are ±3i — purely imaginary.",
                "A zero real part means no envelope at all: "
                "y = C₁cos 3t + C₂sin 3t.",
                "y(0) = 0 kills the cosine; y′(0) = 3 gives 3C₂ = 3, so "
                "y = sin 3t.",
            ),
        ),
    ),
)


UNDETERMINED = Lesson(
    key="undetermined",
    title="Forced equations: undetermined coefficients",
    summary="When something is driving the system, and you can guess the shape "
            "of its response.",
    tool="steps",
    reference="Edwards 3.5",
    prerequisites=("roots",),
    objectives=(
        "Split a forced equation into homogeneous and particular parts, and "
        "say why every solution is that sum.",
        "Choose a trial form from the shape of the forcing.",
        "Detect resonance, and correct the guess by multiplying by t.",
        "Recognise forcing the method cannot handle at all.",
    ),
    examples=(
        Example(
            equation="y'' + 4*y = sin(t)",
            conditions="y(0) = 0, y'(0) = 1",
            why="Natural frequency 2, driven at 1 — no clash, so the guess "
                "goes straight through. Watch both a sine and a cosine enter "
                "the trial form even though the forcing has only one of them.",
        ),
        Example(
            equation="y'' + y = cos(t)",
            conditions="y(0) = 0, y'(0) = 0",
            why="Driven at exactly its own natural frequency. The obvious "
                "guess substitutes to zero, and correcting it produces the t "
                "that makes the amplitude grow without bound.",
        ),
    ),
    notes=(
        Note(
            "The structure of the answer",
            "Solve the homogeneous equation first, then find any one solution "
            "of the forced equation. Every solution is the sum. This is worth "
            "understanding rather than memorising: the difference of two "
            "solutions of the forced equation solves the homogeneous one.",
            r"y = y_h + y_p",
            "formula",
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
            "pitfall",
        ),
        Note(
            "Guess the whole family, not just the top term",
            "Polynomial forcing needs every power below it as well: for t² "
            "guess At² + Bt + C. Differentiating the guess produces the lower "
            "powers, and if they are not in the trial form there is nothing to "
            "cancel them against.",
            r"g(t) = t^{2} \;\Longrightarrow\; y_p = At^{2} + Bt + C",
            "pitfall",
        ),
        Note(
            "What it cannot do",
            "The guess has to be a finite set of shapes closed under "
            "differentiation. tan t and 1/t are not, and neither is anything "
            "with a corner or a jump in it. Those need variation of parameters "
            "or the Laplace transform.",
            kind="aside",
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
            becauses=(
                "At² alone cannot work: y′ brings in a t and y″ a constant, and "
                "there is nothing in the trial form to cancel them against.",
                "Differentiating t² produces t and then a constant, so all "
                "three powers must be in the guess. Guessing At² alone "
                "leaves terms nothing can cancel.",
                "Raising the degree is the resonance correction, and there is "
                "no resonance here — the roots are complex, so no polynomial "
                "solves the homogeneous equation.",
                "An exponential guess matches exponential forcing. The forcing "
                "here is a polynomial, and no combination of e^t produces t².",
            ),
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
            becauses=(
                "The opposite: differentiating a cosine gives a sine, so a "
                "sine is always needed. That is not what is wrong here.",
                "The homogeneous solutions are exactly cos 2t and sin 2t. "
                "Anything built from them substitutes to zero and can never "
                "equal cos 2t. Multiply by t: y_p = t(A cos 2t + B sin 2t). "
                "This is resonance.",
                "The algebra is not the obstacle — the guess is. Substituting "
                "gives 0 = cos 2t, which no choice of A and B repairs.",
                "It is wrong. Substituting it gives zero, never cos 2t, "
                "whatever A and B are.",
            ),
        ),
        Solve(
            key="q3",
            prompt="Off resonance — the straightforward case.",
            equation="y'' + 4*y = sin(t)",
            conditions="y(0) = 0, y'(0) = 1",
            hints=(
                "Homogeneous roots are ±2i, and the forcing is at frequency 1. "
                "No clash, so no factor of t.",
                "Guess y_p = A cos t + B sin t and substitute.",
                "y_p = sin(t)/3. Add y_h = C₁cos 2t + C₂sin 2t and use the two "
                "conditions.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Resonant. Expect a t in the answer.",
            equation="y'' + y = cos(t)",
            conditions="y(0) = 0, y'(0) = 0",
            hints=(
                "The natural frequency is 1 and you are driving at 1. That is "
                "resonance.",
                "cos t already solves the homogeneous equation, so multiply "
                "the guess by t: y_p = t(A cos t + B sin t).",
                "y_p = t·sin(t)/2, and with both conditions zero that is the "
                "whole answer.",
            ),
        ),
        Solve(
            key="q5",
            prompt="Polynomial forcing.",
            equation="y'' + 3*y' + 2*y = t",
            conditions="y(0) = 0, y'(0) = 0",
            hints=(
                "Roots −1 and −2, so a polynomial guess cannot clash with the "
                "homogeneous solutions.",
                "Guess At + B, not just At — the derivative of the guess "
                "contributes a constant that has to be cancelled.",
                "y_p = t/2 − 3/4. Then fit C₁ and C₂ to the two conditions.",
            ),
        ),
    ),
)


CAUCHY = Lesson(
    key="cauchy",
    title="Cauchy–Euler equations",
    summary="Variable coefficients that still come out in closed form, because "
            "the powers of t line up.",
    tool="steps",
    reference="Edwards 3.3",
    prerequisites=("roots",),
    objectives=(
        "Recognise a Cauchy–Euler equation by matching powers to derivatives.",
        "Derive the indicial equation from the substitution y = t^r.",
        "Write the solution in each of the three indicial cases, with ln t "
        "where the constant-coefficient case has t.",
        "Say why the solutions are stated only for t > 0.",
    ),
    examples=(
        Example(
            equation="t**2*y'' + t*y' - y = 0",
            why="Distinct indicial roots ±1, so the answer is a power and its "
                "reciprocal — the plainest case, and the one that shows why "
                "t = 0 has to be excluded.",
        ),
        Example(
            equation="t**2*y'' - 3*t*y' + 4*y = 0",
            why="A repeated indicial root at 2. The second solution picks up "
                "ln t rather than t, which is the substitution t = e^s showing "
                "through.",
        ),
    ),
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
            "formula",
        ),
        Note(
            "The three cases again, with logs",
            "Same three cases as constant coefficients, with ln t where t used "
            "to be. That is not a coincidence: substituting t = e^s turns a "
            "Cauchy–Euler equation into a constant-coefficient one, and s = ln t.",
            r"t^{r_1},\ t^{r_2} \quad\mid\quad t^{r},\ t^{r}\ln t "
            r"\quad\mid\quad t^{a}\cos(b\ln t),\ t^{a}\sin(b\ln t)",
            "formula",
        ),
        Note(
            "r(r−1), not r²",
            "The indicial equation is not the characteristic polynomial with t "
            "swapped for e. Differentiating t^r twice gives r(r−1)t^{r−2}, so "
            "the quadratic starts from ar(r−1) + br + c — writing ar² + br + c "
            "loses a term and gives the wrong roots.",
            r"t^{2}\,\tfrac{d^{2}}{dt^{2}}t^{r} = r(r-1)\,t^{r}",
            "pitfall",
        ),
        Note(
            "Where it is valid",
            "The solutions involve t^r and ln t, so they are stated for t > 0. "
            "At t = 0 the leading coefficient vanishes and the equation stops "
            "being second order at all — a singular point, and conditions "
            "cannot be given there.",
            kind="aside",
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
            becauses=(
                "Only this one has t^k matching the k-th derivative: t² "
                "with y'', t with y'. Substituting y = t^r leaves every term a "
                "multiple of t^r.",
                "y' carries 3 rather than 3t, so after y = t^r that term is "
                "t^{r−1} while the others are t^r. Nothing cancels.",
                "y'' has no t² in front. The powers are off by two there, and "
                "the t on y' does not repair it.",
                "t with y'' and 3t² with y' — both off by one, in the same "
                "direction, which does not save it.",
            ),
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
            becauses=(
                "That is the distinct-root pattern, r = 2 and r = −2. Here the "
                "indicial equation is a perfect square, so there is only one "
                "root.",
                "This is the constant-coefficient repeated-root pattern with t "
                "in the wrong place. Under t = e^s the extra factor is s, and "
                "s = ln t.",
                "A repeated indicial root brings in ln t, not t — the "
                "Cauchy–Euler counterpart of the extra factor of t in the "
                "constant-coefficient case. The substitution t = e^s is why.",
                "A constant is t⁰, which is not a solution here: substituting "
                "y = C₂ leaves 4C₂, which is zero only if C₂ is.",
            ),
        ),
        Solve(
            key="q3",
            prompt="Distinct indicial roots.",
            equation="t**2*y'' + t*y' - y = 0",
            hints=(
                "Try y = t^r. Every term becomes a multiple of t^r.",
                "r(r−1) + r − 1 = r² − 1, so the roots are ±1.",
                "Distinct roots, so one power each: y = C₁t + C₂/t. Notice "
                "the second blows up at t = 0, which is the singular point.",
            ),
        ),
        Solve(
            key="q4",
            prompt="A repeated root — expect a logarithm.",
            equation="t**2*y'' - 3*t*y' + 4*y = 0",
            hints=(
                "Try y = t^r: the indicial equation is r(r−1) − 3r + 4.",
                "That is r² − 4r + 4 = (r−2)², a repeated root at 2.",
                "A repeated indicial root brings in ln t: "
                "y = t²(C₁ + C₂ ln t).",
            ),
        ),
    ),
)


LESSONS = (ROOTS, UNDETERMINED, CAUCHY)
