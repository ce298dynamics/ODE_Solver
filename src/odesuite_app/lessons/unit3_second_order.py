"""Unit 3 -- Second-order linear equations.

Edwards, Penney and Calvis 6e, chapter 3. The three techniques a first course
spends most of its second half on: reading a solution off the characteristic
roots, guessing a particular solution when something is driving the system, and
the one variable-coefficient family that still comes out in closed form.

Superposition and the Wronskian, variation of parameters, and the higher-order
case belong here too, and arrive with the narrator each needs.
"""

from __future__ import annotations

from .model import Choice, Example, Lesson, Note, Solve, Template

__all__ = ["SUPERPOSITION", "ROOTS", "UNDETERMINED", "VARIATION",
           "CAUCHY", "HIGHER", "LESSONS"]


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
    templates=(
        Template(
            key="three-cases",
            title="All three root cases, mixed",
            prompt="Characteristic polynomial, roots, then the two conditions.",
            equation="y'' + {b}*y' + {c}*y = 0",
            conditions="y(0) = {p}, y'(0) = {v}",
            technique="nth_linear_constant_coeff_homogeneous",
            hints=(
                "Substitute y = e^(rt) and read the characteristic "
                "polynomial straight off the coefficients.",
                "Work out the discriminant. Its sign is what decides which of "
                "the three shapes you are about to write down.",
                "Write the general solution for that case, then use the two "
                "conditions to pin both constants — differentiate before "
                "putting the second one in.",
            ),
            # Paired, so the discriminant always lands on a case a course
            # would set: rational roots, a perfect square, or a clean pair.
            slots=(
                ("b,c", ((3, 2), (4, 4), (2, 5), (5, 6), (2, 1), (0, 9),
                         (6, 9), (4, 13), (0, 4), (7, 12), (2, 10), (8, 16))),
                ("p,v", ((1, 0), (0, 1), (1, 1), (2, 0))),
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
    templates=(
        Template(
            key="cosine-forcing",
            title="Cosine forcing — sometimes resonant",
            prompt="Check the driving frequency against the natural one first.",
            equation="y'' + {w2}*y = {b}*cos({w}*t)",
            conditions="y(0) = 0, y'(0) = 0",
            technique="nth_linear_constant_coeff_undetermined_coefficients",
            hints=(
                "The homogeneous roots are purely imaginary, so the natural "
                "frequency is the square root of the coefficient of y. "
                "Compare it with the frequency you are driving at.",
                "If those agree, the obvious guess solves the homogeneous "
                "equation and substitutes to zero — multiply it by t.",
                "Guess the corrected form, substitute, match the coefficients, "
                "then add y_h and use the two conditions.",
            ),
            # Paired so that resonance is drawn as often as not: (4,2), (1,1)
            # and (9,3) are the cases where the guess has to be corrected.
            slots=(
                ("w2,w", ((4, 1), (4, 2), (1, 1), (1, 2), (9, 1), (9, 3),
                          (16, 2))),
                ("b", (1, 2, 3)),
            ),
        ),
        Template(
            key="polynomial-forcing",
            title="Polynomial forcing on a damped system",
            prompt="Guess the whole family, not just the top power.",
            equation="y'' + {b}*y' + {c}*y = {d}*t",
            conditions="y(0) = 0, y'(0) = 0",
            technique="nth_linear_constant_coeff_undetermined_coefficients",
            hints=(
                "Do the homogeneous part first: characteristic polynomial, "
                "roots, general solution.",
                "The forcing is a multiple of t, so guess At + B — the "
                "derivative of the guess produces a constant that needs "
                "somewhere to go.",
                "Substitute, match the t terms and the constant terms "
                "separately, then fit C₁ and C₂ to the conditions.",
            ),
            slots=(
                ("b,c", ((3, 2), (4, 4), (2, 5), (5, 6), (2, 1))),
                ("d", (1, 2, 3)),
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
    templates=(
        Template(
            key="indicial",
            title="Substitute a power, read the indicial roots",
            prompt="y = t^r, then whichever of the three cases you land in.",
            equation="t**2*y'' + {b}*t*y' + {c}*y = 0",
            conditions="",
            technique="nth_linear_euler_eq_homogeneous",
            hints=(
                "Substituting y = t^r turns every term into a multiple of "
                "t^r. Watch the second derivative: it gives r(r−1), not r².",
                "Collect what is left into a quadratic in r — the indicial "
                "equation — and solve it.",
                "Distinct roots give two powers; a repeated root brings in "
                "ln t; a complex pair gives cos and sin of ln t.",
            ),
            slots=(
                ("b,c", ((1, -1), (-3, 4), (2, -2), (-1, 1), (3, 1), (5, 4),
                         (1, -4), (-5, 9), (1, 1), (-1, 5))),
            ),
        ),
    ),
)


SUPERPOSITION = Lesson(
    key="superposition",
    title="Superposition, the Wronskian, and the general solution",
    summary="Why two solutions are enough for a second-order equation, and how "
            "to tell whether the two you have will do.",
    tool="steps",
    reference="Edwards 3.1",
    prerequisites=("basics",),
    objectives=(
        "State what makes an equation linear, and check whether one is.",
        "Add two solutions of a homogeneous linear equation and explain why "
        "the sum is one too.",
        "Compute a Wronskian and say what its being non-zero buys you.",
        "Say why a second-order equation needs exactly two arbitrary "
        "constants, and no more.",
    ),
    examples=(
        Example(
            equation="y'' - y = 0",
            why="The plainest case. e^t and e^{-t} both solve it, their "
                "Wronskian is −2, and every solution is a combination of "
                "them — there is nothing else out there.",
        ),
        Example(
            equation="y'' + 4*y = 0",
            conditions="y(0) = 1, y'(0) = 2",
            why="cos 2t and sin 2t, Wronskian 2. The two conditions pick one "
                "member of the family, which is what two constants are for.",
        ),
    ),
    notes=(
        Note(
            "Linear means the unknown appears plainly",
            "Every term is a coefficient times y or one of its derivatives, "
            "and nothing else. y'' + p(t)y' + q(t)y = g(t) is the whole shape. "
            "No y², no sin y, no y·y'. The coefficients may be as messy as "
            "they like — it is what happens to y that decides linearity.",
            r"y'' + p(t)\,y' + q(t)\,y = g(t)",
        ),
        Note(
            "Superposition",
            "If y₁ and y₂ both solve the homogeneous equation, so does any "
            "combination of them. This is the whole reason the answer to a "
            "second-order equation is a two-parameter family rather than a "
            "list of solutions found one at a time.",
            r"L[c_1 y_1 + c_2 y_2] = c_1 L[y_1] + c_2 L[y_2] = 0",
            "formula",
        ),
        Note(
            "It fails the moment the equation is nonlinear",
            "Superposition is a property of linear equations and nothing else. "
            "y = 1/(1−t) solves y' = y², but 2y does not. Adding two solutions "
            "of a nonlinear equation and expecting a solution is the most "
            "expensive habit to carry out of this chapter.",
            r"y' = y^{2}:\quad y_1 + y_2 \ \text{is not a solution}",
            "pitfall",
        ),
        Note(
            "The Wronskian tests independence",
            "Two solutions are only worth two constants if neither is a "
            "multiple of the other. The Wronskian is the determinant that "
            "checks it: non-zero at a single point is enough, because for "
            "solutions of the same linear equation it is either always zero "
            "or never zero.",
            r"W(y_1,y_2) = \begin{vmatrix} y_1 & y_2 \\ y_1' & y_2' "
            r"\end{vmatrix} = y_1 y_2' - y_2 y_1'",
            "formula",
        ),
        Note(
            "What “general solution” actually claims",
            "Not \"a solution with constants in it\" — it claims that every "
            "solution of the equation is in the family, with no exceptions "
            "waiting to be discovered. Existence and uniqueness is what makes "
            "that claim safe: two initial conditions determine one solution, "
            "and two independent solutions can meet any pair of conditions.",
            r"y = C_1 y_1 + C_2 y_2",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="Which of these is a linear equation?",
            options=(
                "y'' + t²y' − y = cos t",
                "y'' + y·y' = 0",
                "y'' + sin(y) = 0",
                "(y')² + y = t",
            ),
            answer=0,
            becauses=(
                "Every term is a coefficient times y or a derivative of it. "
                "t² is a messy coefficient, and cos t a messy forcing term, "
                "but neither touches how y itself appears — which is what "
                "linearity is about.",
                "y·y' is the unknown multiplied by its own derivative. That is "
                "a product of unknowns, so the equation is nonlinear.",
                "sin(y) puts the unknown inside a function. This is the "
                "pendulum, and it is the standard example of a nonlinear "
                "equation.",
                "Squaring y' makes the equation nonlinear in the derivative. "
                "Linear means degree one in y and every derivative.",
            ),
        ),
        Choice(
            key="q2",
            prompt="y₁ and y₂ both solve y'' + 3y' + 2y = 0. Which is also a "
                   "solution?",
            options=(
                "y₁·y₂",
                "5y₁ − 2y₂",
                "y₁/y₂",
                "y₁ + 1",
            ),
            answer=1,
            becauses=(
                "A product of two solutions is not generally a solution. "
                "Superposition covers sums and scalar multiples, not products "
                "— those would need the operator to be multiplicative, which "
                "it is not.",
                "Any linear combination of solutions of a homogeneous linear "
                "equation is a solution. That is superposition, and it is why "
                "the general solution is C₁y₁ + C₂y₂.",
                "A quotient is no better than a product. Neither is a linear "
                "combination.",
                "Adding a constant would only work if the constant itself "
                "solved the equation, and 2·1 = 2 ≠ 0 here. The equation has "
                "no constant solution but zero.",
            ),
        ),
        Choice(
            key="q3",
            prompt="W(y₁, y₂) = 0 for every t, and both solve the same "
                   "second-order linear homogeneous equation. What follows?",
            options=(
                "They are dependent, so they cannot give the general solution",
                "The equation has no solutions",
                "They are independent",
                "Nothing follows without more information",
            ),
            answer=0,
            becauses=(
                "A vanishing Wronskian means one is a constant multiple of the "
                "other. They span a one-parameter family, not a two-parameter "
                "one, so they cannot meet an arbitrary pair of initial "
                "conditions.",
                "The equation is fine. It is the *pair* that is inadequate — a "
                "linear homogeneous equation always has two independent "
                "solutions somewhere.",
                "That is backwards: a non-zero Wronskian shows independence. "
                "Zero shows the opposite here.",
                "For two solutions of the *same* linear equation it does "
                "follow, by Abel's theorem: the Wronskian is either "
                "identically zero or never zero.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Check the pair, then write the general solution.",
            equation="y'' - y = 0",
            conditions="y(0) = 2, y'(0) = 0",
            hints=(
                "The roots are ±1, so e^t and e^{−t} are the candidates.",
                "W = e^t·(−e^{−t}) − e^{−t}·e^t = −2, which is never zero — so "
                "the pair is independent and the general solution is all of "
                "them.",
                "y = C₁e^t + C₂e^{−t}. Both conditions give C₁ = C₂ = 1, so "
                "y = 2cosh t.",
            ),
        ),
        Solve(
            key="q5",
            prompt="Two constants, two conditions.",
            equation="y'' + 4*y = 0",
            conditions="y(0) = 1, y'(0) = 2",
            hints=(
                "Roots ±2i, so the fundamental set is cos 2t and sin 2t.",
                "Their Wronskian is 2cos²2t + 2sin²2t = 2 — independent "
                "everywhere, so two constants really are enough.",
                "y(0) = 1 gives C₁ = 1, and y′(0) = 2 gives 2C₂ = 2.",
            ),
        ),
    ),
    templates=(
        Template(
            key="independent-pair",
            title="Two conditions on a two-parameter family",
            prompt="Write the general solution, then pin both constants.",
            equation="y'' - {c}*y = 0",
            conditions="y(0) = {p}, y'(0) = {v}",
            technique="nth_linear_constant_coeff_homogeneous",
            hints=(
                "Substitute y = e^(rt). With a bare y'' and y the "
                "characteristic polynomial is r² − c.",
                "Two real roots ±√c, so the fundamental set is a growing and "
                "a decaying exponential. Their Wronskian is a non-zero "
                "constant, which is what says two constants suffice.",
                "Write y = C₁e^(rt) + C₂e^(−rt), differentiate, and solve the "
                "two-by-two system the conditions give.",
            ),
            slots=(
                ("c", (1, 4, 9, 16, 25)),
                ("p,v", ((2, 0), (0, 1), (1, 1), (1, 0))),
            ),
        ),
    ),
)


VARIATION = Lesson(
    key="variation",
    title="Variation of parameters",
    summary="What to do when the forcing term is not something you could ever "
            "guess.",
    tool="steps",
    reference="Edwards 3.5",
    prerequisites=("roots", "undetermined"),
    objectives=(
        "Say why undetermined coefficients cannot touch sec t or ln t.",
        "Put an equation in standard form before quoting the formula.",
        "Compute the Wronskian of a fundamental set and use it.",
        "Assemble a particular solution by integrating u₁' and u₂'.",
    ),
    examples=(
        Example(
            equation="y'' + y = sec(t)",
            why="The standard example, and the one undetermined coefficients "
                "cannot begin: differentiating sec t produces sec t·tan t, "
                "then more, and the list never closes. Watch log(cos t) "
                "appear — nothing you would have guessed.",
        ),
        Example(
            equation="y'' - 2*y' + y = exp(t)/t",
            why="A repeated root, so the basis is e^t and t·e^t, and the "
                "forcing is an exponential divided by t. Dividing is what "
                "puts it out of reach of a trial set.",
        ),
    ),
    notes=(
        Note(
            "When guessing runs out",
            "Undetermined coefficients needs the forcing term's derivatives to "
            "close into a finite list — polynomials, exponentials, sines and "
            "cosines do. sec t, tan t, ln t and e^t/t do not: differentiate "
            "them and the list grows forever, so there is no finite form to "
            "guess. This technique needs no guess at all.",
            r"g(t) = \sec t,\ \tan t,\ \ln t,\ e^{t}/t",
        ),
        Note(
            "Let the constants vary",
            "Take the homogeneous solution C₁y₁ + C₂y₂ and let the constants "
            "become functions. Requiring u₁'y₁ + u₂'y₂ = 0 keeps the second "
            "derivative from growing u'' terms, and what is left is a "
            "two-by-two system for u₁' and u₂'.",
            r"y_p = u_1(t)\,y_1 + u_2(t)\,y_2",
            "formula",
        ),
        Note(
            "The formula",
            "Solving that system by Cramer's rule gives the pair everyone "
            "memorises. The Wronskian in the denominator is exactly why the "
            "fundamental set has to be independent — a dependent pair would "
            "divide by zero.",
            r"u_1' = -\frac{y_2\,g}{W},\qquad u_2' = \frac{y_1\,g}{W}",
            "formula",
        ),
        Note(
            "Divide by the leading coefficient first",
            "The formula is stated for y'' + p y' + q y = g. If the equation "
            "starts 3y'' or t²y'', then g is *not* the right-hand side you "
            "were given — it is that divided by the leading coefficient. "
            "Skipping this is the most common way to get the technique wrong, "
            "and everything after it inherits the error.",
            r"t^{2}y'' + ty' - y = t^{3} \;\Longrightarrow\; g = t",
            "pitfall",
        ),
        Note(
            "No constants when you integrate",
            "Integrating u₁' and u₂' needs no +C. Those constants would only "
            "add multiples of y₁ and y₂ back in, and the homogeneous solution "
            "already carries both with arbitrary coefficients.",
            r"y = C_1 y_1 + C_2 y_2 + u_1 y_1 + u_2 y_2",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="Which forcing term rules out undetermined coefficients?",
            options=(
                "t²e^{3t}",
                "tan t",
                "sin 2t − 4cos 2t",
                "5t³ + 1",
            ),
            answer=1,
            becauses=(
                "Polynomial times exponential: differentiating stays inside "
                "the same finite family, so there is a trial set to guess.",
                "Differentiating tan t gives sec²t, then 2sec²t·tan t, and the "
                "list never closes. There is no finite form to guess, which is "
                "exactly when variation of parameters is the technique.",
                "Sines and cosines cycle between each other. Two terms in the "
                "trial set, and guessing works.",
                "A polynomial's derivatives terminate at zero. The trial set "
                "is finite and short.",
            ),
        ),
        Choice(
            key="q2",
            prompt="For 2y'' + 8y = tan t, what is g in the formula?",
            latex=r"2y'' + 8y = \tan t",
            options=(
                "tan t",
                "(tan t)/2",
                "2tan t",
                "tan t − 8y",
            ),
            answer=1,
            becauses=(
                "That is the right-hand side as given, before the equation is "
                "in standard form. Using it here is the classic error.",
                "The formula assumes y'' + py' + qy = g, so divide everything "
                "by the leading 2 first: y'' + 4y = (tan t)/2.",
                "Multiplying goes the wrong way. You divide by the leading "
                "coefficient, not by its reciprocal.",
                "g is what is left on the right after the y terms are on the "
                "left. It never contains y.",
            ),
        ),
        Choice(
            key="q3",
            prompt="The fundamental set of y'' + y = 0 is cos t, sin t. What "
                   "is its Wronskian?",
            options=("0", "1", "cos 2t", "sin t · cos t"),
            answer=1,
            becauses=(
                "Zero would mean the pair is dependent, and cos t is plainly "
                "not a multiple of sin t. It would also make the formula "
                "divide by zero.",
                "W = cos t·cos t − sin t·(−sin t) = cos²t + sin²t = 1. Being "
                "constant and non-zero is what makes this the tidiest example "
                "in the chapter.",
                "That is cos²t − sin²t, which is what you get from a sign slip "
                "in the determinant.",
                "That is the product of the two functions, not the "
                "determinant of the matrix with their derivatives.",
            ),
        ),
        Solve(
            key="q4",
            prompt="The standard example.",
            equation="y'' + y = sec(t)",
            hints=(
                "The homogeneous solution is C₁cos t + C₂sin t, and W = 1.",
                "u₁' = −sin t·sec t/1 = −tan t and u₂' = cos t·sec t/1 = 1.",
                "Integrate: u₁ = ln|cos t| and u₂ = t. So "
                "y_p = cos t·ln|cos t| + t·sin t.",
            ),
        ),
        Solve(
            key="q5",
            prompt="A repeated root, and forcing you cannot guess.",
            equation="y'' - 2*y' + y = exp(t)/t",
            hints=(
                "(r − 1)² = 0, so the basis is e^t and t·e^t.",
                "W = e^t·(e^t + te^t) − te^t·e^t = e^{2t}.",
                "u₁' = −t e^t·(e^t/t)/e^{2t} = −1 and u₂' = 1/t, so "
                "y_p = te^t(ln t − 1).",
            ),
        ),
    ),
    templates=(
        Template(
            key="secant-family",
            title="Forcing with no trial set",
            prompt="Homogeneous solution, Wronskian, then integrate.",
            equation="y'' + y = {g}",
            technique="nth_linear_constant_coeff_variation_of_parameters",
            hints=(
                "The homogeneous part is the same every time: r² + 1 = 0 "
                "gives cos t and sin t.",
                "Their Wronskian is 1, which makes u₁' = −y₂g and "
                "u₂' = y₁g with nothing to divide by.",
                "Integrate both, assemble u₁y₁ + u₂y₂, and add it to the "
                "homogeneous solution.",
            ),
            slots=(
                ("g", ("sec(t)", "tan(t)", "csc(t)", "cot(t)",
                       "sec(t)*tan(t)", "1/cos(t)**2")),
            ),
        ),
    ),
)


HIGHER = Lesson(
    key="higher",
    title="Higher-order linear equations",
    summary="Everything from second order, with more roots to keep track of "
            "and multiplicity to respect.",
    tool="steps",
    reference="Edwards 3.2–3.3",
    prerequisites=("roots", "undetermined"),
    objectives=(
        "Factor a cubic or quartic characteristic polynomial.",
        "Write the basis a root of multiplicity k contributes.",
        "Handle a repeated complex pair without losing terms.",
        "Say how many arbitrary constants an nth-order equation has, and why.",
    ),
    examples=(
        Example(
            equation="y''' - 6*y'' + 11*y' - 6*y = 0",
            why="Three distinct real roots, 1, 2 and 3 — the plainest "
                "higher-order case, and a reminder that the machinery does "
                "not change, only the bookkeeping.",
        ),
        Example(
            equation="y''' + y'' = t",
            why="A root at zero with multiplicity two, so the homogeneous "
                "part carries a constant and a t. The forcing is a "
                "polynomial that resonates with both, which is where the "
                "correction matters most.",
        ),
    ),
    notes=(
        Note(
            "Nothing new, only more of it",
            "The exponential substitution works at any order: y = e^{rt} "
            "turns an nth-order constant-coefficient equation into an "
            "nth-degree polynomial. The work moves from calculus to "
            "factoring, which is the only genuinely harder part.",
            r"a_n y^{(n)} + \cdots + a_0 y = 0 \;\Longrightarrow\; "
            r"a_n r^{n} + \cdots + a_0 = 0",
        ),
        Note(
            "Multiplicity brings powers of t",
            "A root repeated k times contributes k solutions, each the "
            "previous one multiplied by t. This is the repeated-root rule "
            "from second order, continued as far as the multiplicity goes.",
            r"e^{rt},\ t e^{rt},\ t^{2} e^{rt},\ \ldots,\ t^{k-1} e^{rt}",
            "formula",
        ),
        Note(
            "A repeated complex pair repeats both halves",
            "a ± bi with multiplicity two contributes four solutions, not "
            "two: the cosine and the sine, and then t times each of them. "
            "Dropping the second pair is the easiest way to end up one "
            "constant short of the order.",
            r"e^{at}\cos bt,\ e^{at}\sin bt,\ te^{at}\cos bt,\ te^{at}\sin bt",
            "pitfall",
        ),
        Note(
            "Count the constants",
            "An nth-order equation has exactly n arbitrary constants, and "
            "multiplicities have to sum to n. If your fundamental set is "
            "shorter than the order, a repeated root lost a power of t "
            "somewhere — counting is the quickest check there is.",
            r"\sum_i m_i = n",
            "aside",
        ),
        Note(
            "Forcing works exactly as before",
            "Undetermined coefficients and variation of parameters both apply "
            "unchanged. The resonance correction multiplies by t as many "
            "times as the multiplicity requires, and the Wronskian is simply "
            "an n×n determinant.",
            r"y = y_h + y_p",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="r = −2 has multiplicity 3. What does it contribute?",
            options=(
                "e^{−2t} only",
                "e^{−2t}, te^{−2t}, t²e^{−2t}",
                "e^{−2t}, e^{−4t}, e^{−6t}",
                "e^{−2t}, te^{−2t}",
            ),
            answer=1,
            becauses=(
                "One solution per root would leave the fundamental set short "
                "of the order, and the remaining conditions could not be met.",
                "Multiplicity k gives k solutions: the exponential and then "
                "successive powers of t times it, up to t^{k−1}.",
                "Multiplicity does not multiply the root. There is one root "
                "here, at −2, occurring three times.",
                "That is multiplicity two. A triple root needs the t² term as "
                "well.",
            ),
        ),
        Choice(
            key="q2",
            prompt="How many arbitrary constants does a fourth-order linear "
                   "homogeneous equation have?",
            options=("2", "4", "It depends on the roots", "1 per distinct root"),
            answer=1,
            becauses=(
                "Two is the second-order answer. The number of constants "
                "follows the order, not the chapter it was met in.",
                "Exactly n for an nth-order equation, because n initial "
                "conditions are needed to pick a single solution. "
                "Multiplicities always sum to the order.",
                "The roots decide what the solutions look like, not how many "
                "there are. Repeated roots supply their extra solutions with "
                "powers of t.",
                "That would be too few whenever a root repeats — which is "
                "precisely what the powers of t exist to fix.",
            ),
        ),
        Solve(
            key="q3",
            prompt="Three distinct real roots.",
            equation="y''' - 6*y'' + 11*y' - 6*y = 0",
            conditions="y(0) = 0, y'(0) = 1, y''(0) = 3",
            hints=(
                "r³ − 6r² + 11r − 6 factors with r = 1 as an obvious root.",
                "Dividing out gives (r − 1)(r − 2)(r − 3).",
                "y = C₁e^t + C₂e^{2t} + C₃e^{3t}, and three conditions give a "
                "three-by-three system for the constants.",
            ),
        ),
        Solve(
            key="q4",
            prompt="A repeated root at higher order.",
            equation="y''' + 3*y'' + 3*y' + y = 0",
            conditions="y(0) = 1, y'(0) = 0, y''(0) = 0",
            hints=(
                "The coefficients 1, 3, 3, 1 should look familiar: the "
                "polynomial is (r + 1)³.",
                "A triple root at −1 contributes e^{−t}, te^{−t} and t²e^{−t}.",
                "y = (C₁ + C₂t + C₃t²)e^{−t}; differentiate twice and apply "
                "all three conditions.",
            ),
        ),
        Solve(
            key="q5",
            prompt="Fourth order, two pairs.",
            equation="y'''' - y = 0",
            conditions="y(0) = 1, y'(0) = 0, y''(0) = 1, y'''(0) = 0",
            hints=(
                "r⁴ − 1 = (r² − 1)(r² + 1).",
                "Roots ±1 and ±i, so the basis is e^t, e^{−t}, cos t, sin t "
                "— four solutions for a fourth-order equation.",
                "The conditions are symmetric enough that the oscillating part "
                "drops out entirely.",
            ),
        ),
    ),
    templates=(
        Template(
            key="third-order",
            title="Third order, three conditions",
            prompt="Factor the cubic, write the basis, pin three constants.",
            equation="y''' - {a}*y'' + {b}*y' - {c}*y = 0",
            conditions="y(0) = {p}, y'(0) = {v}, y''(0) = {w}",
            technique="nth_linear_constant_coeff_homogeneous",
            hints=(
                "Substitute y = e^(rt) to get a cubic in r.",
                "Try small integers first — these are built to factor over "
                "the integers, so one of ±1, ±2, ±3 is a root.",
                "Divide it out, factor the remaining quadratic, and write one "
                "exponential per root before applying the conditions.",
            ),
            # (a, b, c) are the elementary symmetric functions of the roots,
            # so every draw factors over the integers -- which is what a
            # course would set, and what keeps the answer readable.
            slots=(
                ("a,b,c", ((6, 11, 6), (4, 5, 2), (3, 2, 0), (2, -1, -2),
                           (0, -1, 0), (5, 8, 4), (1, -4, -4), (7, 14, 8))),
                ("p,v,w", ((0, 1, 3), (1, 0, 0), (1, 1, 1))),
            ),
        ),
    ),
)


LESSONS = (SUPERPOSITION, ROOTS, UNDETERMINED, VARIATION, CAUCHY,
           HIGHER)
