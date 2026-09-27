"""Unit 3 -- Second-order linear equations.

Edwards, Penney and Calvis 6e, chapter 3. The three techniques a first course
spends most of its second half on: reading a solution off the characteristic
roots, guessing a particular solution when something is driving the system, and
the one variable-coefficient family that still comes out in closed form.

Superposition and the Wronskian, variation of parameters, and the higher-order
case belong here too, and arrive with the narrator each needs.
"""

from __future__ import annotations

from .model import (
    Case,
    Choice,
    ClassifyTemplate,
    Example,
    ExpressionTemplate,
    FaultTemplate,
    Lesson,
    ModelTemplate,
    Note,
    Passage,
    Solve,
    Template,
)

__all__ = ["SUPERPOSITION", "ROOTS", "UNDETERMINED", "VARIATION",
           "REDUCTION", "CAUCHY", "HIGHER", "LESSONS"]


ROOTS = Lesson(
    key="roots",
    title="Second order: characteristic roots",
    summary="Constant coefficients, no forcing — where a differential equation "
            "becomes a quadratic.",
    tool="steps",
    reference="Edwards 3.1–3.3",
    figure="root_cases",
    motivation=(
        "Superposition says that two independent solutions are the whole "
        "answer. It does not say how to find even one of them, and for a "
        "general second-order equation with varying coefficients nobody can. "
        "The case that goes through completely is the one where the "
        "coefficients are constants — which is also, by a wide margin, the "
        "case that arises.\n\n"
        "The reason constants are tractable is worth stating plainly. With "
        "constant coefficients the equation does not care where the origin of "
        "time is, so its solutions must be functions whose *shape* is "
        "unchanged by a shift in time. There is essentially one such "
        "function, and that is the whole of why the exponential is the right "
        "thing to try.\n\n"
        "What follows is the most mechanical procedure in the course: write a "
        "polynomial, find its roots, read off the answer. It repays being "
        "understood rather than memorised, because the two awkward cases — a "
        "repeated root and a complex pair — both look arbitrary if the reason "
        "for the exponential is not clear."
    ),
    derivation=(
        Passage(
            prose="Try an exponential and watch what the operator does to it. Every "
                  "derivative multiplies by the same constant, so the exponential comes "
                  "straight back out and what is left in front of it is a polynomial.",
            latex=r"L\left[e^{rt}\right] = \left(a r^{2} + b r + c\right)e^{rt}",
        ),
        Passage(
            prose="An exponential is never zero, so the whole equation collapses to "
                  "that polynomial being zero. Solving a differential equation has been "
                  "traded for solving a quadratic, and the trade *is* the method.",
            latex=r"a r^{2} + b r + c = 0",
        ),
        Passage(
            prose="Two distinct real roots give two exponentials, and their determinant "
                  "is a non-zero multiple of an exponential — so the previous lesson "
                  "certifies them as a basis and there is nothing left to do.",
            latex=r"W\left(e^{r_1 t}, e^{r_2 t}\right) = (r_2 - r_1)e^{(r_1 + r_2)t} \neq 0",
        ),
        Passage(
            prose="A complex pair still gives two solutions, but they are complex, and "
                  "the equation had real coefficients — so real answers must be "
                  "available. Superposition supplies them: half the sum of the two, and "
                  "the difference divided by twice the imaginary unit, are both "
                  "combinations and both real. Euler's formula names them.",
            latex=r"\frac{e^{(\alpha + i\beta)t} + e^{(\alpha - i\beta)t}}{2} "
                  r"= e^{\alpha t}\cos\beta t",
        ),
        Passage(
            prose="So the real part of the root becomes the envelope and the imaginary "
                  "part the frequency. Nothing was approximated on the way: the complex "
                  "exponentials were a route, and the answer they lead to is exactly "
                  "real.",
            latex=r"y = e^{\alpha t}\left(c_1\cos\beta t + c_2\sin\beta t\right)",
        ),
        Passage(
            prose="A repeated root is the genuinely awkward case, because the method "
                  "has produced one solution where two are needed. Watch what happens "
                  "as two distinct roots collide. The difference of their exponentials, "
                  "divided by the gap between the roots, is a solution by superposition "
                  "for every gap — and it has a limit.",
            latex=r"\lim_{r_2 \to r_1}\frac{e^{r_2 t} - e^{r_1 t}}{r_2 - r_1} = t\,e^{r_1 t}",
        ),
        Passage(
            prose="That is where the factor of t comes from. It is not a rule bolted on "
                  "for an awkward case; it is what the second solution was already "
                  "turning into as the roots approached each other. Substituting "
                  "confirms it solves the equation, and the determinant confirms the "
                  "pair is independent.",
            latex=r"y = \left(c_1 + c_2 t\right)e^{r_1 t}",
        ),
    ),
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
            commentary=(
                "The polynomial factors, so take the two roots off it before looking "
                "at the working — and notice that both are negative. Without solving "
                "anything, every solution of this equation decays. The signs of the "
                "roots are the qualitative answer; the constants only settle the "
                "details.\n\n"
                "Then watch the conditions produce a system rather than two separate "
                "statements. What comes out is a difference of two decaying "
                "exponentials with the faster one subtracted, and that is what makes "
                "the curve leave the axis flat: at the start the two decay rates "
                "cancel exactly, which is what a zero initial slope means. After that "
                "the fast term dies and the slow one governs, so the long run belongs "
                "to the root nearer zero."
            ),
        ),
        Example(
            equation="y'' + 2*y' + 5*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            why="A complex pair, −1 ± 2i. Watch the exponentials become a "
                "cosine and a sine, with the real part left outside as the "
                "decaying envelope.",
            commentary=(
                "Read the two halves of the root separately and predict the picture "
                "before any algebra. The real part is negative, so whatever "
                "oscillation there is must die away; the imaginary part is two, so it "
                "oscillates at that rate. Neither statement needed the closed form.\n\n"
                "Then satisfy yourself that the answer is genuinely real. The route "
                "ran through complex exponentials, which can feel like a sleight of "
                "hand, so substitute the finished expression back — this application "
                "does — and note that no imaginary part survives anywhere in it. The "
                "complex numbers were scaffolding, and the derivation says why: the "
                "two combinations that were taken are exactly the ones whose "
                "imaginary halves cancel."
            ),
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
        # PED-06: where the method itself stops, not a mistake a student makes.
        Note(
            "Where it stops: constant coefficients only",
            "Guessing eʳᵗ works because differentiating it only rescales it, "
            "and that survives multiplication by a constant but not by a "
            "function of t. For y'' + t·y = 0 the guess leaves t·eʳᵗ terms that"
            " no choice of r cancels, and a different method — a series, here —"
            " is needed.",
            r"y'' + t\,y = 0: \ e^{rt} \text{ leaves } t\,e^{rt}",
            "pitfall",
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
        Choice(
            key="q-figure",
            prompt="In the left pane of the figure, hold b fixed and drag c "
                   "upwards until the marker crosses the parabola. What "
                   "happens to the solution in the right pane as it does?",
            figure="root_cases",
            options=(
                "The two real roots collide into one, and past the parabola "
                "the solution starts to oscillate",
                "The solution changes from decaying to growing, because "
                "crossing the parabola changes the sign of the roots",
                "Nothing visible happens: the parabola marks a change in the "
                "formula used, not in the behaviour",
                "The solution stops existing, because above the parabola the "
                "characteristic equation has no roots",
            ),
            answer=0,
            becauses=(
                "b² − 4c changes sign exactly at the parabola. Below it the "
                "roots are two real numbers, on it they are one repeated "
                "root, and above it they are a complex pair — which is the "
                "first moment the curve crosses the axis rather than "
                "approaching it.",
                "Growth or decay is decided by the real part, which is −b/2 "
                "and has nothing to do with c. Hold b positive and everything "
                "decays on both sides of the parabola.",
                "The formula changes because the behaviour does. Watch the "
                "right pane while you cross: the curve goes from never "
                "crossing zero to crossing it repeatedly.",
                "It always has roots — a quadratic always does. What changes "
                "is whether they are real, and complex roots are roots.",
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
            # By the discriminant, which is the only thing that changes what
            # has to be done. Distinct real roots are the case the method is
            # introduced on; a repeated root is the one that needs the extra
            # factor of t, and it is where this goes wrong.
            level=lambda slots: (
                "easier" if slots["b"] ** 2 - 4 * slots["c"] > 0
                else "harder" if slots["b"] ** 2 == 4 * slots["c"]
                else "typical"
            ),
        ),
        ExpressionTemplate(
            key="the-characteristic-equation",
            title="One step only: the characteristic equation",
            prompt="Write the characteristic equation for   {equation}.   Do "
                   "not solve it.",
            answer="{answer}",
            up_to_constant=True,
            because="Substituting y = e^(rt) turns every derivative into a "
                    "power of r: y'' becomes r², y' becomes r, and y itself "
                    "contributes nothing but its coefficient. Dividing "
                    "through by e^(rt), which is never zero, leaves the "
                    "polynomial — and any nonzero multiple of it has the "
                    "same roots, so any multiple is accepted.",
            hints=(
                "Try y = e^(rt) and see what each term becomes. Every "
                "derivative brings down another factor of r.",
                "Every term now has e^(rt) in it, and e^(rt) is never zero, "
                "so it can be divided out.",
                "What is left is a polynomial in r with the same "
                "coefficients the equation has.",
            ),
            slots=(("equation,answer,tier", (
                ("y'' + 5*y' + 6*y = 0", "r**2 + 5*r + 6", "easier"),
                ("y'' - 3*y' + 2*y = 0", "r**2 - 3*r + 2", "easier"),
                ("y'' + 4*y' + 4*y = 0", "r**2 + 4*r + 4", "easier"),
                ("y'' + 2*y' + 5*y = 0", "r**2 + 2*r + 5", "typical"),
                ("y'' - 6*y' + 13*y = 0", "r**2 - 6*r + 13", "typical"),
                ("y'' + 9*y = 0", "r**2 + 9", "typical"),
                ("2*y'' + 5*y' + 3*y = 0", "2*r**2 + 5*r + 3", "harder"),
                ("3*y'' - y' - 2*y = 0", "3*r**2 - r - 2", "harder"),
                ("y''' - y' = 0", "r**3 - r", "harder"),
            )),),
            level=lambda slots: slots["tier"],
        ),
        FaultTemplate(
            key="a-root-used-twice",
            title="Spot the mistake: a repeated root",
            prompt="Somebody solved the characteristic equation, found one "
                   "root, and wrote the general solution like this. What "
                   "went wrong?",
            equation="y'' - {two_r}*y' + {r_squared}*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            wrong="C1*exp({r}*t) + C2*exp({r}*t)",
            fault="repeated-root",
            others=("real-roots-for-complex", "sign-in-exponent",
                    "forcing-not-reduced"),
            slots=(("r,two_r,r_squared", (
                (2, 4, 4), (3, 6, 9), (4, 8, 16),
                (5, 10, 25), (6, 12, 36), (7, 14, 49),
            )),),
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
    figure="forced_structure",
    motivation=(
        "Every second-order equation so far has had nothing on the right, and "
        "nothing on the right means nothing driving the system. An undriven "
        "spring is not much of a model. A radio has a signal in it, a "
        "building has an earthquake under it, a circuit has a source — the "
        "forced equation is the one that actually gets used.\n\n"
        "The shape of the answer is settled by linearity before any technique "
        "appears. If two functions produce the same forcing then their "
        "difference produces nothing, so it is a homogeneous solution. Every "
        "solution is therefore one particular solution plus the homogeneous "
        "family, and the only new work is finding a single particular "
        "solution.\n\n"
        "For that there is a method which looks too good to be true: guess "
        "the shape of the answer, leave its coefficients unknown, and let the "
        "equation determine them. It works — but only for certain forcings, "
        "and both why it works and why it sometimes collapses are worth "
        "having rather than remembering."
    ),
    derivation=(
        Passage(
            prose="First the structure, which needs no guessing at all. Take any single "
                  "solution of the forced equation and any other one, and apply the "
                  "operator to their difference: the forcing appears twice and cancels.",
            latex=r"L\left[y - y_p\right] = f - f = 0",
        ),
        Passage(
            prose="So the general solution is one particular solution plus the general "
                  "homogeneous solution, and the homogeneous half is already known from "
                  "the previous lesson. Note where the constants live — in the "
                  "homogeneous part. A particular solution needs none of its own.",
            latex=r"y = y_p + c_1 y_1 + c_2 y_2",
        ),
        Passage(
            prose="Now the guessing, and here is why a finite guess can work at all. "
                  "Look at what differentiation does to a polynomial times an "
                  "exponential times a sinusoid: it gives back another function of "
                  "exactly that shape. The family is closed under differentiation, so "
                  "the operator maps it into itself.",
            latex=r"\frac{d}{dt}\left(t^{n}e^{at}\cos bt\right) \text{ stays "
                  r"in the same family}",
        ),
        Passage(
            prose="Which turns the problem into algebra. Write the trial function with "
                  "unknown coefficients and apply the operator; both sides now lie in "
                  "the same finite family, so matching coefficients is a finite linear "
                  "system and solving it is the whole method. Nothing is guessed except "
                  "the family, and the forcing chooses the family.",
            latex=r"L\left[A\cos bt + B\sin bt\right] = f \;\Longrightarrow\; "
                  r"\text{solve for } A,\ B",
        ),
        Passage(
            prose="It also explains why the trial form must carry terms the forcing "
                  "does not have. Differentiating a cosine produces a sine, so the "
                  "operator returns a combination of both; offering only a cosine "
                  "leaves the equation no way to cancel the sine that appears. The "
                  "family has to be complete, not minimal.",
            latex=r"L\left[A\cos bt\right] \text{ contains } \sin bt",
        ),
        Passage(
            prose="And it explains the failure. If the trial function is itself a "
                  "homogeneous solution then the operator sends it to zero, so no "
                  "choice of coefficients can produce a non-zero forcing — the system "
                  "is unsolvable rather than merely awkward. That is resonance, and it "
                  "is the forcing lying inside what the operator kills.",
            latex=r"L\left[y_{\text{trial}}\right] = 0 \;\Longrightarrow\; "
                  r"\text{no coefficient works}",
        ),
        Passage(
            prose="The repair is the same idea as the repeated root: multiply by t "
                  "until the trial function is no longer a homogeneous solution. So the "
                  "growing amplitude of a resonant response is not a fudge — the factor "
                  "of t is the only thing left in the family that the operator does not "
                  "annihilate.",
            latex=r"y_p = t\left(A\cos bt + B\sin bt\right)",
        ),
    ),
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
            commentary=(
                "Check for a clash first, because that check is what decides whether "
                "this method applies at all. The homogeneous solutions here oscillate "
                "at one rate and the forcing at another, so nothing in the trial form "
                "is annihilated by the operator and the plain guess is admissible. "
                "Two seconds of arithmetic saves the whole problem.\n\n"
                "Then read the finished answer as two superimposed oscillations at "
                "different rates rather than as one formula. One of them is the "
                "response to the forcing and lasts exactly as long as the forcing "
                "does; the other carries the constants and is there only because of "
                "how the motion started. Both persist here, because nothing in this "
                "equation removes energy — which is precisely what the vibrations "
                "unit changes."
            ),
        ),
        Example(
            equation="y'' + y = cos(t)",
            conditions="y(0) = 0, y'(0) = 0",
            why="Driven at exactly its own natural frequency. The obvious "
                "guess substitutes to zero, and correcting it produces the t "
                "that makes the amplitude grow without bound.",
            commentary=(
                "Try the plain trial form yourself before reading on. It takes a "
                "single substitution and it collapses to zero, which is the failure "
                "the sixth passage predicts rather than an algebra slip. Watching it "
                "fail once is worth more than remembering a rule about when to bring "
                "in a factor of t.\n\n"
                "Then look at what the corrected answer claims physically. The "
                "amplitude grows steadily and without limit, which no real spring "
                "does — so the model is reporting that something it left out must "
                "eventually intervene: friction, or the spring ceasing to be linear. "
                "An unbounded answer is not automatically a wrong answer. Here it is "
                "an honest statement of what the assumptions imply."
            ),
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
            r"y'' + y = \cos t \;\Longrightarrow\; y_p = \frac{1}{2}\,t\sin t",
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
        # PED-06: where the method itself stops, not a mistake a student makes.
        Note(
            "Where it stops: the forcing must have finitely many derivatives",
            "A guess works when the forcing and all its derivatives lie in a "
            "finite family: polynomials, exponentials, sines and cosines, and "
            "their products. sec t does not — its derivatives keep producing "
            "new functions — so no finite guess can contain the answer, and "
            "variation of parameters is the method that still works. The "
            "equation must also have constant coefficients.",
            r"\frac{d}{dt}\sec t = \sec t\tan t,\quad \frac{d^{2}}{dt^{2}}\sec t = "
            r"\sec t\tan^{2} t + \sec^{3} t,\ \dots",
            "pitfall",
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
        FaultTemplate(
            key="stopped-at-the-complementary",
            title="Spot the mistake: a forced equation",
            prompt="Somebody solved the characteristic equation, wrote down "
                   "the two solutions it gives, and handed that in. What "
                   "went wrong?",
            equation="y'' + {w2}*y = {d}",
            wrong="C1*cos({w}*t) + C2*sin({w}*t)",
            fault="missing-particular",
            others=("missing-complementary", "no-constant",
                    "sign-in-exponent"),
            slots=(("w,w2", ((2, 4), (3, 9), (4, 16), (5, 25))),
                   ("d", (6, 8, 12))),
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
    figure="powers",
    motivation=(
        "Constant coefficients were tractable because the equation does not "
        "care where the origin of time sits. There is a second kind of "
        "equation that is tractable for a closely related reason, and it "
        "turns up wherever a problem has no natural length scale — steady "
        "heat flow in a disc, a potential written in polar coordinates, the "
        "stress in a thick pipe.\n\n"
        "In those problems the coefficients are not constant, but they are "
        "arranged so that each derivative arrives with the matching power of "
        "t in front of it. The effect is that the equation is unchanged by "
        "*rescaling* t rather than by shifting it, and that symmetry is every "
        "bit as strong. It says what kind of function to try, and the answer "
        "is not an exponential.\n\n"
        "Powers of t are the functions whose shape survives a rescaling, so a "
        "power is the thing to try — and after that every step follows the "
        "constant-coefficient pattern exactly, including a repeated root and "
        "a complex pair. The one visible difference is that logarithms appear "
        "where factors of t used to, and the substitution at the end of the "
        "derivation is what explains them."
    ),
    derivation=(
        Passage(
            prose="Recognise the shape first: each term pairs the kth derivative with t "
                  "raised to the kth power. That pairing is the entire point, because "
                  "it is what makes the operator blind to the scale of t.",
            latex=r"a\,t^{2}y'' + b\,t\,y' + c\,y = 0",
        ),
        Passage(
            prose="Check the symmetry rather than taking it on trust. Differentiating k "
                  "times introduces k factors of one over the scale, and the t to the "
                  "kth in front cancels every one of them — so replacing t by any "
                  "multiple of itself leaves the equation exactly as it was.",
            latex=r"t \to \lambda t \;\Longrightarrow\; "
                  r"t^{k}\frac{d^{k}}{dt^{k}} \text{ unchanged}",
        ),
        Passage(
            prose="So try a function whose shape survives rescaling, which is a power. "
                  "Applying the operator gives the same power back, multiplied by a "
                  "number — exactly what an exponential does for constant coefficients.",
            latex=r"t^{k}\frac{d^{k}}{dt^{k}}t^{r} = r(r-1)\cdots(r-k+1)\,t^{r}",
        ),
        Passage(
            prose="Which turns the equation into a polynomial again: the indicial "
                  "equation. Look closely at its coefficients — the second-derivative "
                  "term contributes r(r−1) and not r², because differentiating a power "
                  "twice gives exactly that. It is the single most common error in this "
                  "topic.",
            latex=r"a\,r(r-1) + b\,r + c = 0",
        ),
        Passage(
            prose="Distinct real roots give two powers, and they are independent. But "
                  "something was assumed quietly: a power is only defined and only "
                  "continuous away from the origin, and the origin is exactly where the "
                  "equation's leading coefficient vanishes. So the answer holds on one "
                  "side of zero and makes no claim at zero itself.",
            latex=r"y = c_1 t^{r_1} + c_2 t^{r_2}, \qquad t > 0",
        ),
        Passage(
            prose="Now explain the logarithms instead of asserting them. Substitute t "
                  "for an exponential of a new variable. Each pairing of a power with a "
                  "derivative becomes a plain derivative in that variable, so the "
                  "equation *is* a constant-coefficient equation wearing a disguise, "
                  "and a power of t is an exponential in the new variable.",
            latex=r"t = e^{s} \;\Longrightarrow\; t\frac{d}{dt} = \frac{d}{ds}",
        ),
        Passage(
            prose="Everything then follows from the previous lesson with no new work at "
                  "all. A repeated root there brings a factor of the new variable, and "
                  "that variable is the logarithm of t; a complex pair brings a cosine "
                  "and a sine of it. The three cases here are not three rules — they "
                  "are one rule seen through a substitution.",
            latex=r"\left(c_1 + c_2 s\right)e^{rs} \;\Longrightarrow\; "
                  r"\left(c_1 + c_2\ln t\right)t^{r}",
        ),
    ),
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
            commentary=(
                "Form the indicial equation by hand before reading the working, and "
                "take care over the first term: it contributes r(r−1), not r². Get "
                "that wrong and the polynomial becomes r² + r − 1, whose roots are "
                "irrational and nothing like the answer shown — which is exactly the "
                "pitfall this lesson names, seen from the inside.\n\n"
                "Then look at what the two solutions do near the origin, since that "
                "is the point of this example. One of them is unbounded there and the "
                "other is not, so no combination behaves well at zero except the one "
                "that discards the first — and even that is not a solution *at* zero, "
                "because the equation loses its leading coefficient there. The "
                "interval has to be stated along with the answer."
            ),
        ),
        Example(
            equation="t**2*y'' - 3*t*y' + 4*y = 0",
            why="A repeated indicial root at 2. The second solution picks up "
                "ln t rather than t, which is the substitution t = e^s showing "
                "through.",
            commentary=(
                "Check the discriminant first: the indicial polynomial is a perfect "
                "square here, and its vanishing discriminant is the only thing that "
                "has to be noticed. Everything after that is the repeated-root case "
                "of the previous lesson, transported.\n\n"
                "Then confirm where the logarithm comes from rather than accepting "
                "it. In the substituted variable the answer would read as a constant "
                "plus that variable, multiplying an exponential — precisely the "
                "repeated-root form — and the variable is the logarithm of t. "
                "Substituting the second solution back into the original equation is "
                "the other confirmation, and this application performs it: the "
                "logarithm survives both differentiations and cancels exactly."
            ),
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
            r"t^{2}\,\frac{d^{2}}{dt^{2}}t^{r} = r(r-1)\,t^{r}",
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
        # PED-06: where the method itself stops, not a mistake a student makes.
        Note(
            "Where it stops: t = 0, and the wrong pattern",
            "The guess y = tʳ works only when the k-th derivative is multiplied"
            " by exactly tᵏ. And t = 0 is a singular point: the solutions are "
            "found on t > 0 (or on t < 0 with |t|), and generally do not "
            "continue through zero — tʳ with r negative or fractional is not "
            "defined there.",
            r"t^{2}y'' + a\,t\,y' + b\,y = 0 \quad (t > 0)",
            "pitfall",
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
    figure="superposition",
    motivation=(
        "Everything so far has been first order, and first order means one "
        "constant and one condition. The physical world is mostly second "
        "order, because Newton's law is: a mass on a spring, a pendulum, a "
        "beam, a circuit. So the subject has to move up an order, and the "
        "useful question is what actually changes.\n\n"
        "What changes is that there are now two constants to find, and that "
        "raises something the first-order case never had to face. Where do "
        "two independent solutions come from, and how would you know when you "
        "had *enough* of them? Two solutions that are secretly multiples of "
        "one another look like two and behave like one, and no pair of "
        "conditions can then be met.\n\n"
        "Almost everything in this unit rests on a single structural fact: "
        "these equations are linear, so solutions can be added. That one "
        "property is what makes a two-parameter family the whole answer "
        "rather than merely part of it. It is worth establishing before any "
        "technique appears, because every technique in the unit assumes it."
    ),
    derivation=(
        Passage(
            prose="Collect the derivatives on the left and give that side a name. What "
                  "sits there is a *machine*: hand it a function and it returns another "
                  "one. Naming it makes the structure visible and every argument below "
                  "shorter.",
            latex=r"L[y] = a(t)\,y'' + b(t)\,y' + c(t)\,y",
        ),
        Passage(
            prose="The machine is linear — it distributes over sums and lets constants "
                  "through — because differentiation does. That is one line to check, "
                  "and it is the source of everything else in this unit.",
            latex=r"L[c_1 y_1 + c_2 y_2] = c_1 L[y_1] + c_2 L[y_2]",
        ),
        Passage(
            prose="So if two functions are each sent to zero, every combination of them "
                  "is too. Superposition is not a trick peculiar to this equation; it "
                  "is linearity, and it fails the instant the equation is not linear. "
                  "Two solutions of y'' = y² have a sum that solves nothing.",
            latex=r"L[y_1] = L[y_2] = 0 \;\Longrightarrow\; L[c_1 y_1 + c_2 y_2] = 0",
        ),
        Passage(
            prose="That produces a two-parameter family. Whether it is *all* of the "
                  "solutions turns on the two being genuinely different: if one is a "
                  "multiple of the other the family quietly collapses to a one-"
                  "parameter one, and two conditions can no longer be satisfied.",
            latex=r"y_2 = k\,y_1 \;\Longrightarrow\; c_1 y_1 + c_2 y_2 = (c_1 + k c_2)\,y_1",
        ),
        Passage(
            prose="So test it by asking whether the conditions can be met at all. "
                  "Fitting a value and a slope at one instant is a pair of linear "
                  "equations in the two constants — an ordinary 2×2 system, and nothing "
                  "about differential equations is left in it.",
            latex=r"c_1 y_1(t_0) + c_2 y_2(t_0) = y_0, \quad c_1 y_1'(t_0) + "
                  r"c_2 y_2'(t_0) = v_0",
        ),
        Passage(
            prose="Such a system is solvable for every pair of conditions exactly when "
                  "its determinant is non-zero, and that determinant is the Wronskian. "
                  "It is not a definition handed down to be remembered: it is the "
                  "condition for the two constants to exist, written out.",
            latex=r"W(y_1, y_2) = y_1 y_2' - y_2 y_1' \neq 0",
        ),
        Passage(
            prose="And here is the step usually waved at — why testing one instant "
                  "settles every instant. Differentiate the Wronskian and use the "
                  "equation to replace both second derivatives. Almost everything "
                  "cancels, and what is left is a first-order linear equation for the "
                  "Wronskian itself. Its solution is a constant times an exponential, "
                  "and an exponential is never zero, so the Wronskian vanishes "
                  "everywhere or nowhere at all.",
            latex=r"W' = -\frac{b(t)}{a(t)}W \;\Longrightarrow\; W(t) = "
                  r"W(t_0)\exp\left(-\int \frac{b}{a}\,dt\right)",
        ),
    ),
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
            commentary=(
                "Substitute both functions before reading anything else. Each check "
                "takes one line and it is the only part of this lesson that needs no "
                "theory at all. Then form the determinant of the pair by hand and "
                "notice that it comes out the same at every instant.\n\n"
                "That constancy is not a coincidence, and it is the fastest possible "
                "confirmation of the last passage of the derivation. This equation "
                "has no first-derivative term, so the coefficient in the equation "
                "governing the determinant is zero and its derivative vanishes. Any "
                "equation missing its y' term has this property, which is a small "
                "thing to notice and a useful one."
            ),
        ),
        Example(
            equation="y'' + 4*y = 0",
            conditions="y(0) = 1, y'(0) = 2",
            why="cos 2t and sin 2t, Wronskian 2. The two conditions pick one "
                "member of the family, which is what two constants are for.",
            commentary=(
                "Watch the two conditions being applied and notice they are applied "
                "to different things — one to the function, one to its derivative. "
                "That is what makes them a solvable pair rather than the same "
                "statement twice, and it is the 2×2 system from the derivation with "
                "numbers in it.\n\n"
                "Then compare the determinant of that system against the pair's "
                "determinant at the same instant. They are the same number, because "
                "they are the same determinant — it was never a separate quantity "
                "computed for its own sake. And note that the amplitude of the "
                "finished answer is not one, even though the starting value is: the "
                "condition on the slope contributes to it as well."
            ),
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
            r"W(y_1, y_2) = y_1 y_2' - y_2 y_1' \neq 0",
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
        ModelTemplate(
            key="family-to-second-order",
            title="Read the equation off the general solution",
            prompt="This is the general solution of one second-order "
                   "equation with constant coefficients:   y = {family}.   "
                   "Write the equation.",
            equation="{answer}",
            because="{why}",
            hints=(
                "The exponents in the solution are the roots of the "
                "characteristic equation. Read them off first.",
                "With roots r₁ and r₂ the characteristic equation is "
                "(r − r₁)(r − r₂) = 0. Multiply that out.",
                "Then read the equation back off the polynomial: r² is y'', "
                "r is y', and the constant term multiplies y.",
            ),
            slots=(("family,answer,why,tier", (
                ("C₁e^(2t) + C₂e^(-5t)", "y'' + 3*y' - 10*y = 0",
                 "The roots are 2 and −5, so the characteristic equation is "
                 "(r − 2)(r + 5) = r² + 3r − 10 — and the coefficients of "
                 "that polynomial are the coefficients of the equation.",
                 "easier"),
                ("C₁e^t + C₂e^(4t)", "y'' - 5*y' + 4*y = 0",
                 "Roots 1 and 4: (r − 1)(r − 4) = r² − 5r + 4. The sum of "
                 "the roots comes back with its sign reversed, which is "
                 "worth remembering as a check.",
                 "easier"),
                ("C₁e^(-t) + C₂e^(-3t)", "y'' + 4*y' + 3*y = 0",
                 "Roots −1 and −3: (r + 1)(r + 3) = r² + 4r + 3. Both roots "
                 "negative makes every coefficient positive, which is what "
                 "damping looks like in the equation.",
                 "easier"),
                ("(C₁ + C₂t)e^(3t)", "y'' - 6*y' + 9*y = 0",
                 "The factor of t is the sign of a repeated root: r = 3 "
                 "twice, so the polynomial is (r − 3)² = r² − 6r + 9.",
                 "typical"),
                ("(C₁ + C₂t)e^(-2t)", "y'' + 4*y' + 4*y = 0",
                 "A repeated root at −2, so (r + 2)² = r² + 4r + 4. The "
                 "discriminant of that polynomial is exactly zero, which is "
                 "what put the t there.",
                 "typical"),
                ("C₁cos(2t) + C₂sin(2t)", "y'' + 4*y = 0",
                 "A sine and cosine of the same frequency and no exponential "
                 "means roots ±2i: (r − 2i)(r + 2i) = r² + 4. No y' term, "
                 "because the roots have no real part to contribute one.",
                 "typical"),
                ("e^(-t)(C₁cos(2t) + C₂sin(2t))", "y'' + 2*y' + 5*y = 0",
                 "The exponential gives the real part and the frequency the "
                 "imaginary part: roots −1 ± 2i. Then r² + 2r + 5, since the "
                 "constant term is the modulus squared.",
                 "harder"),
                ("e^(2t)(C₁cos(t) + C₂sin(t))", "y'' - 4*y' + 5*y = 0",
                 "Roots 2 ± i. The growing exponential shows up as a "
                 "negative coefficient of y', which is an equation with "
                 "negative damping — energy being put in rather than taken "
                 "out.",
                 "harder"),
                ("C₁ + C₂e^(-4t)", "y'' + 4*y' = 0",
                 "A bare constant is an exponential too, with rate zero. So "
                 "the roots are 0 and −4, and the polynomial is "
                 "r(r + 4) = r² + 4r — the missing constant term is the zero "
                 "root.",
                 "harder"),
            )),),
            level=lambda slots: slots["tier"],
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
    figure="variation",
    motivation=(
        "Undetermined coefficients works because one particular family of "
        "functions is closed under differentiation. Step outside that family "
        "and the method offers nothing at all — not a harder calculation, but "
        "no calculation. Differentiate sec t, or ln t, or an exponential over "
        "t, repeatedly: the list of new functions never closes, so there is "
        "no finite trial form to write down.\n\n"
        "These are not exotic forcings. A resistance that varies with time, a "
        "source that fades as one over t, a driving term that is itself the "
        "answer to something else — each leaves the trial-set method behind "
        "while remaining a perfectly ordinary equation with a perfectly "
        "ordinary answer.\n\n"
        "What is wanted is a method that builds a particular solution out of "
        "the *homogeneous* solutions rather than out of a guess about the "
        "forcing. Remarkably, one exists, and it never fails to describe the "
        "answer. It costs two integrals, which may not be elementary — and "
        "that is the price of generality, since an integral left unevaluated "
        "is still a finished answer."
    ),
    derivation=(
        Passage(
            prose="Start from the homogeneous solutions, which are taken as known. The "
                  "homogeneous family is those two with *constant* coefficients in "
                  "front of them, so keep the shape and let the coefficients vary with "
                  "t instead. That is where the method's name comes from, and it is the "
                  "whole of the idea.",
            latex=r"y_p = u_1(t)\,y_1 + u_2(t)\,y_2",
        ),
        Passage(
            prose="Differentiate it. Two terms appear that would not be there if the "
                  "coefficients were constant, and they are the entire difficulty of "
                  "the method.",
            latex=r"y_p' = u_1 y_1' + u_2 y_2' + \left(u_1' y_1 + u_2' y_2\right)",
        ),
        Passage(
            prose="Here is the step that looks like cheating and is not. There are two "
                  "unknown functions and only one equation for them to satisfy, so the "
                  "problem is underdetermined and one further condition may simply be "
                  "*chosen*. Any choice that makes the algebra close is legitimate, so "
                  "choose the one that deletes the awkward bracket.",
            latex=r"u_1' y_1 + u_2' y_2 = 0 \qquad \text{(chosen, not derived)}",
        ),
        Passage(
            prose="With that choice the first derivative reads exactly as it would for "
                  "constants, so differentiating again brings only one extra bracket. "
                  "Substitute into the equation and almost everything cancels — because "
                  "the two solutions already satisfy the homogeneous equation, which is "
                  "the only property of them being used.",
            latex=r"a\left(u_1' y_1' + u_2' y_2'\right) = f(t)",
        ),
        Passage(
            prose="So two conditions on the two derivatives are left, and they are a "
                  "2×2 linear system whose determinant is the Wronskian. It is non-zero "
                  "precisely because the two solutions are independent, which is what "
                  "that lesson was for.",
            latex=r"u_1' y_1 + u_2' y_2 = 0, \qquad u_1' y_1' + u_2' y_2' = \frac{f}{a}",
        ),
        Passage(
            prose="Solve the system and integrate. The resulting formula is not worth "
                  "memorising — the derivation above is three lines and reconstructs it "
                  "on demand — but the two signs in it are exactly where errors happen, "
                  "so it is worth writing out once.",
            latex=r"u_1 = -\int\frac{y_2 f}{a\,W}\,dt, \qquad u_2 = \int\frac{y_1 f}{a\,W}\,dt",
        ),
        Passage(
            prose="Two cautions the derivation makes obvious. The forcing inside those "
                  "integrals is the one that appears *after* dividing by the leading "
                  "coefficient, because that is where it entered. And no constants are "
                  "added at the integration: a constant there merely adds a homogeneous "
                  "solution, which the general answer already carries.",
            latex=r"u_1 + C \;\Longrightarrow\; y_p + C\,y_1 \text{, already in the family}",
        ),
    ),
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
            commentary=(
                "The homogeneous half is the easy half, so write it down first: a "
                "cosine and a sine, whose determinant comes out as one. A determinant "
                "of one is a small mercy that makes the two integrals as clean as "
                "this method ever gets, and it is why this is the example every book "
                "uses.\n\n"
                "Then watch which of the two integrals does the work. One of them "
                "integrates to something elementary and dull; the other produces a "
                "logarithm, and no amount of differentiating a trial family will ever "
                "produce a logarithm — which is the concrete form of the claim that "
                "the previous method could not have begun. Note too that the answer "
                "is valid only where the forcing is defined, so the interval stops at "
                "the first place the cosine vanishes."
            ),
        ),
        Example(
            equation="y'' - 2*y' + y = exp(t)/t",
            why="A repeated root, so the basis is e^t and t·e^t, and the "
                "forcing is an exponential divided by t. Dividing is what "
                "puts it out of reach of a trial set.",
            commentary=(
                "Compute the determinant of the two homogeneous solutions before "
                "starting anything else: it is a single exponential, and it cancels "
                "against the exponential in the forcing. That cancellation is the "
                "only reason this problem is workable by hand, and spotting it in "
                "advance turns two intimidating integrals into two easy ones.\n\n"
                "Then look at the integrands that remain after it. One is a constant "
                "and the other is one over t — and the second is where the logarithm "
                "comes from, which is the whole reason a trial set was hopeless here. "
                "Notice also that the particular solution comes out carrying a term "
                "that is already a homogeneous solution; dropping it changes nothing, "
                "because the general answer absorbs it into a constant."
            ),
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
        # PED-06: where the method itself stops, not a mistake a student makes.
        Note(
            "Where it stops: you need the homogeneous solutions first",
            "Variation of parameters never guesses, but it assumes y₁ and y₂ "
            "are already known. For constant coefficients they are; for most "
            "variable-coefficient equations they are not, and the method has "
            "nothing to start from. And the integrals it produces need not be "
            "elementary — the answer is then correct but written with integrals"
            " in it.",
            r"u_1' = -\frac{y_2\,g}{W},\qquad u_2' = \frac{y_1\,g}{W}",
            "pitfall",
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
        ExpressionTemplate(
            key="the-wronskian",
            title="One step only: the Wronskian",
            prompt="Write the Wronskian W of   y₁ = {y1}   and   y₂ = {y2}.",
            answer="{answer}",
            because="W = y₁·y₂′ − y₂·y₁′, the determinant of the two "
                    "solutions written above their derivatives. Variation of "
                    "parameters divides by it, which is why it matters that "
                    "it is never zero where the solutions are independent.",
            hints=(
                "W is a 2×2 determinant: the solutions on the top row, their "
                "derivatives on the bottom.",
                "So it is y₁ times the derivative of y₂, minus y₂ times the "
                "derivative of y₁. Differentiate each one first.",
                "Expect the two terms to collapse into something simpler "
                "than either of them — for a constant-coefficient pair it "
                "usually comes out as a single exponential or a constant.",
            ),
            slots=(("y1,y2,answer,tier", (
                ("exp(2*t)", "exp(5*t)", "3*exp(7*t)", "easier"),
                ("exp(-t)", "exp(3*t)", "4*exp(2*t)", "easier"),
                ("cos(2*t)", "sin(2*t)", "2", "typical"),
                ("cos(3*t)", "sin(3*t)", "3", "typical"),
                ("exp(3*t)", "t*exp(3*t)", "exp(6*t)", "typical"),
                ("t", "t**2", "t**2", "typical"),
                ("exp(-t)*cos(t)", "exp(-t)*sin(t)", "exp(-2*t)", "harder"),
                ("t", "t*log(t)", "t", "harder"),
                ("exp(-2*t)", "1", "2*exp(-2*t)", "harder"),
            )),),
            level=lambda slots: slots["tier"],
        ),
        ClassifyTemplate(
            key="which-second-order-method",
            title="Which method would you reach for first?",
            prompt="Read it, decide, and say what decided it. Do not solve "
                   "it.",
            options=("nth_linear_constant_coeff_homogeneous",
                     "nth_linear_constant_coeff_undetermined_coefficients",
                     "nth_linear_constant_coeff_variation_of_parameters",
                     "nth_linear_euler_eq_homogeneous"),
            cases=(
                Case(
                    equation="y'' + 3*y' + 2*y = 0",
                    technique="nth_linear_constant_coeff_homogeneous",
                    why="Constant coefficients and nothing on the right, so "
                        "there is nothing to find a particular solution for. "
                        "The characteristic roots are the whole answer.",
                    tier="easier",
                ),
                Case(
                    equation="y'' + 2*y' + 5*y = 0",
                    technique="nth_linear_constant_coeff_homogeneous",
                    why="Still homogeneous. The discriminant is negative, so "
                        "the roots are complex — which changes the form of "
                        "the answer but not the method that finds it.",
                    tier="typical",
                ),
                Case(
                    equation="y''' - y' = 0",
                    technique="nth_linear_constant_coeff_homogeneous",
                    why="Third order changes nothing: constant coefficients, "
                        "no forcing, so try e^(rt) and solve the cubic. Here "
                        "it factors as r(r − 1)(r + 1).",
                    tier="harder",
                ),
                Case(
                    equation="y'' + 4*y = sin(3*t)",
                    technique=(
                        "nth_linear_constant_coeff_undetermined_coefficients"
                    ),
                    why="The forcing is a sine, whose derivatives stay "
                        "inside {sin, cos}, so a trial A·cos(3t) + B·sin(3t) "
                        "closes. Variation of parameters would also work and "
                        "costs two integrals for nothing.",
                    tier="easier",
                ),
                Case(
                    equation="y'' - 5*y' + 6*y = t**2",
                    technique=(
                        "nth_linear_constant_coeff_undetermined_coefficients"
                    ),
                    why="A polynomial forcing term: differentiate it and you "
                        "stay inside polynomials of the same degree or "
                        "lower, so a quadratic trial has enough room.",
                    tier="typical",
                ),
                Case(
                    equation="y'' - y = exp(t)",
                    technique=(
                        "nth_linear_constant_coeff_undetermined_coefficients"
                    ),
                    why="Still undetermined coefficients, but the trial "
                        "needs care: e^t already solves the homogeneous "
                        "equation, so the guess has to be multiplied by t "
                        "before it can work.",
                    tier="harder",
                ),
                Case(
                    equation="y'' + y = sec(t)",
                    technique=(
                        "nth_linear_constant_coeff_variation_of_parameters"
                    ),
                    why="Differentiating sec t gives sec t·tan t, then more "
                        "of the same and worse: the family never closes, so "
                        "there is no finite trial form to undetermine the "
                        "coefficients of.",
                    tier="typical",
                ),
                Case(
                    equation="y'' + y = tan(t)",
                    technique=(
                        "nth_linear_constant_coeff_variation_of_parameters"
                    ),
                    why="Same reason as sec t: the derivatives of tan t "
                        "generate an unbounded family. The equation is "
                        "otherwise ordinary, which is what makes the forcing "
                        "term the deciding thing.",
                    tier="typical",
                ),
                Case(
                    equation="y'' + y = 1/(1 + exp(t))",
                    technique=(
                        "nth_linear_constant_coeff_variation_of_parameters"
                    ),
                    why="A quotient. Nothing about it repeats under "
                        "differentiation, so the only route is to build the "
                        "particular solution out of the homogeneous pair.",
                    tier="harder",
                ),
                Case(
                    equation="t**2*y'' + 3*t*y' + y = 0",
                    technique="nth_linear_euler_eq_homogeneous",
                    why="The coefficients are not constant, but each "
                        "derivative carries exactly the power of t that "
                        "matches its order — t² with y'', t with y'. That is "
                        "the Cauchy-Euler pattern, and y = t^r turns it into "
                        "a polynomial.",
                    tier="easier",
                ),
                Case(
                    equation="t**2*y'' - 2*y = 0",
                    technique="nth_linear_euler_eq_homogeneous",
                    why="The missing y' term makes no difference: what "
                        "matters is that the term that *is* there carries t² "
                        "against y''. Still t^r.",
                    tier="typical",
                ),
                Case(
                    equation="t**2*y'' - 3*t*y' + 4*y = 0",
                    technique="nth_linear_euler_eq_homogeneous",
                    why="Cauchy-Euler again, and this one has a repeated "
                        "index — the polynomial in r comes out as (r − 2)², "
                        "so the second solution carries a logarithm rather "
                        "than another power.",
                    tier="harder",
                ),
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
    figure="higher_order",
    motivation=(
        "Second order covers a mass on a spring. Higher orders appear as soon "
        "as more than one thing is storing energy: a beam's deflection is "
        "fourth order, a circuit with two loops is fourth order, and a "
        "control system with a lag in it can be of any order at all.\n\n"
        "Nothing about the method changes, and that is worth saying out loud, "
        "because the notation grows alarmingly and suggests otherwise. The "
        "operator is still linear, so superposition still holds. An "
        "exponential still comes back multiplied by a polynomial, so the "
        "characteristic equation is still the whole story. What grows is the "
        "bookkeeping.\n\n"
        "The one genuinely new thing is multiplicity beyond two. A root "
        "repeated three or four times has to supply three or four independent "
        "solutions, so the pattern that produced a single factor of t for a "
        "double root needs extending — which it does, and for exactly the "
        "same reason."
    ),
    derivation=(
        Passage(
            prose="The operator at order n is still linear, and it still returns an "
                  "exponential multiplied by a polynomial — now of degree n. Nothing in "
                  "that argument ever used the fact that the order was two.",
            latex=r"L\left[e^{rt}\right] = \left(a_n r^{n} + \cdots + a_1 r + a_0\right)e^{rt}",
        ),
        Passage(
            prose="So the characteristic equation is a polynomial of degree n, and it "
                  "has n roots once multiplicity is counted. The count is what matters "
                  "here: n roots, n solutions, n constants, n conditions — the "
                  "accounting from the very first lesson of the course, unchanged.",
            latex=r"a_n r^{n} + \cdots + a_1 r + a_0 = 0",
        ),
        Passage(
            prose="Distinct roots need no new argument at all. A root repeated m times "
                  "supplies only one exponential, so m − 1 further solutions must come "
                  "from somewhere — and the colliding-roots argument extends: each "
                  "further collision contributes one more power of t.",
            latex=r"r \text{ with multiplicity } m \;\Longrightarrow\; "
                  r"e^{rt},\ t e^{rt},\ \ldots,\ t^{m-1}e^{rt}",
        ),
        Passage(
            prose="A complex root of a real polynomial always arrives with its "
                  "conjugate, so a repeated complex pair repeats *both* halves and the "
                  "powers of t multiply the cosine and the sine alike. Forgetting the "
                  "second half is the commonest way to finish short of solutions.",
            latex=r"\alpha \pm i\beta \text{ twice} \;\Longrightarrow\; "
                  r"e^{\alpha t}\cos\beta t,\ t e^{\alpha t}\cos\beta t,\ "
                  r"e^{\alpha t}\sin\beta t,\ t e^{\alpha t}\sin\beta t",
        ),
        Passage(
            prose="The count is the check, and it is worth doing before any condition "
                  "is applied. The multiplicities must add up to the order; if the "
                  "collected solutions number fewer than that, a repetition was missed, "
                  "and the conditions will turn out unsatisfiable rather than merely "
                  "give a wrong answer.",
            latex=r"\sum_j m_j = n",
        ),
        Passage(
            prose="Forcing behaves exactly as it did at second order, because the "
                  "structure argument used only linearity. One particular solution plus "
                  "the homogeneous family is still the general answer, and the "
                  "resonance repair is still to multiply by t until the trial function "
                  "is no longer homogeneous — with the multiplicity deciding how many "
                  "times.",
            latex=r"y = y_p + \sum_j \left(\text{terms from the root } r_j\right)",
        ),
    ),
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
            commentary=(
                "Factor the cubic before reading the working, and do it with the "
                "rational root test rather than a formula: the constant term is six, "
                "so the candidates are its divisors and the first one tried succeeds. "
                "Higher-order exercises are set with factorable characteristic "
                "polynomials for precisely this reason, and reaching for a cubic "
                "formula is a sign of having missed that.\n\n"
                "Then check the count and read the behaviour off the roots. Three "
                "roots, three constants — and all three positive, so every solution "
                "grows and the largest root eventually dominates whatever the "
                "starting values were. Three conditions would be needed to single one "
                "out, and none are given here, so what is shown is the whole family "
                "rather than one member of it."
            ),
        ),
        Example(
            equation="y''' + y'' = t",
            why="A root at zero with multiplicity two, so the homogeneous "
                "part carries a constant and a t. The forcing is a "
                "polynomial that resonates with both, which is where the "
                "correction matters most.",
            commentary=(
                "Factor the characteristic polynomial and look hard at what a "
                "repeated zero root means. Its exponential is the constant function, "
                "and the extra power of t makes the second solution t itself. A zero "
                "root is easy to overlook precisely because neither of the solutions "
                "it contributes looks like an exponential.\n\n"
                "Then watch the correction to the trial polynomial. A polynomial "
                "forcing would ordinarily be met with a polynomial of the same "
                "degree, but a constant and a t are both already homogeneous here — "
                "so the trial form has to be multiplied by t twice before the "
                "operator stops annihilating it. That is the multiplicity deciding "
                "how many factors are needed, and it is why the particular solution "
                "ends up two degrees higher than the forcing."
            ),
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


REDUCTION = Lesson(
    key="reduction-of-order",
    title="Reduction of order: a second solution from the first",
    summary="When one solution is known, the second is a first-order problem "
            "— for any linear second-order equation, constant coefficients "
            "or not.",
    tool="steps",
    reference="Edwards 3.2 (problems)",
    figure="reduction",
    prerequisites=("superposition",),
    motivation=(
        "Everything the course can do with a second-order equation so far "
        "depends on constant coefficients, or on the one variable-coefficient "
        "family, Cauchy–Euler, that turns into constant coefficients under a "
        "change of variable. Most equations with coefficients that change "
        "with t are neither, and for them there is no characteristic "
        "polynomial to write down and no trial form to guess.\n\n"
        "Often, though, one solution is visible. It may be given, it may be "
        "a power or an exponential that happens to fit, or it may come from "
        "the physics. And superposition says a second-order equation needs "
        "exactly two independent solutions — so having one is half the "
        "answer, and the question becomes how to turn one into two.\n\n"
        "The idea is to look for the second solution as a multiple of the "
        "first by a function, y₂ = v(t)·y₁. Substituting that in, the known "
        "solution cancels every term containing v itself, and what remains is "
        "a first-order equation for v′. First-order equations are what Unit 1 "
        "solves. The order has been reduced by one, which is where the name "
        "comes from — and the same substitution, run on a forced equation, is "
        "where variation of parameters comes from too."
    ),
    derivation=(
        Passage(
            prose="Put the equation in standard form, with nothing in front of y''. "
                  "Everything the method needs is read off P, so this step is not "
                  "cosmetic.",
            latex=r"y'' + P(t)\, y' + Q(t)\, y = 0",
        ),
        Passage(
            prose="Try y = v y₁ and differentiate twice. The product rule makes "
                  "three groups of terms, and grouping them by v, v' and v'' shows "
                  "what happens.",
            latex=r"v\left(y_1'' + P y_1' + Q y_1\right) + v'\left(2y_1' + "
                  r"P y_1\right) + v'' y_1 = 0",
        ),
        Passage(
            prose="The bracket multiplying v is the equation applied to y₁, and y₁ "
                  "is a solution, so the bracket is zero. The v term vanishes "
                  "entirely — that single cancellation is the whole method.",
            latex=r"y_1 v'' + \left(2y_1' + P y_1\right) v' = 0",
        ),
        Passage(
            prose="Call w = v'. The equation is first order in w, and separable: "
                  "divide by y₁ w and integrate. The two logarithms combine into "
                  "a formula that needs no further thought.",
            latex=r"w = v' = \frac{e^{-\int P\, dt}}{y_1^{2}}",
        ),
        Passage(
            prose="Integrate once more to get v, and multiply by y₁. The constants "
                  "of integration can be dropped at both stages: one would scale "
                  "y₂ and the other would add a multiple of y₁, and the general "
                  "solution has room for both already.",
            latex=r"y_2 = y_1 \int \frac{e^{-\int P\, dt}}{y_1^{2}}\, dt",
        ),
        Passage(
            prose="Independence is automatic. The Wronskian of y₁ and v y₁ is "
                  "y₁² v', which is y₁² w, and that is an exponential — never "
                  "zero. So y₁ and y₂ are a fundamental set wherever y₁ is not "
                  "zero, and the general solution follows.",
            latex=r"W(y_1, y_2) = y_1^{2} v' = e^{-\int P\, dt} \neq 0",
        ),
    ),
    objectives=(
        "Put a second-order linear equation in standard form and read off P.",
        "Check that a proposed first solution really is one, by substituting.",
        "Derive the first-order equation for v′ and solve it.",
        "Build the second solution and confirm the pair is independent.",
    ),
    examples=(
        Example(
            equation="t*y'' - (t + 1)*y' + y = 0",
            why="A variable-coefficient equation with no characteristic "
                "polynomial, where e^t can be spotted as a solution. The "
                "second solution comes out a polynomial.",
            commentary=(
                "Divide by t first: P = −(t + 1)/t = −1 − 1/t. Getting P wrong "
                "is the usual way this goes astray, and it goes astray "
                "quietly, because every later step still produces something "
                "that looks like an answer.\n\n"
                "Then e^(−∫P) = e^(t + ln t) = t e^t, and dividing by "
                "y₁² = e^(2t) leaves t e^(−t) to integrate. By parts that is "
                "−(t + 1)e^(−t), and multiplying by e^t gives y₂ = −(t + 1): a "
                "second solution with no exponential in it at all, which is "
                "easy to check by substituting."
            ),
        ),
        Example(
            equation="t**2*y'' - t*(t + 2)*y' + (t + 2)*y = 0",
            why="Here y₁ = t, and the method produces y₂ = t e^t — the "
                "exponential appears from the reduction, not from any guess "
                "about the equation.",
            commentary=(
                "In standard form P = −(t + 2)/t = −1 − 2/t, so e^(−∫P) = "
                "t² e^t. Divided by y₁² = t² that leaves simply e^t — the "
                "powers of t cancel exactly, which is the sign the "
                "arithmetic has gone right.\n\n"
                "Integrating gives v = e^t and y₂ = t e^t. Nothing about the "
                "original equation suggested an exponential solution; it "
                "came out of the integral. That is the practical value of "
                "the method: it finds solutions nobody would have thought to "
                "try."
            ),
        ),
    ),
    notes=(
        Note(
            "The formula",
            "With y₁ known, a second solution of y'' + Py' + Qy = 0 is y₁ "
            "times the integral of e^(−∫P) / y₁². Both constants of "
            "integration may be dropped.",
            r"y_2 = y_1 \int \frac{e^{-\int P\, dt}}{y_1^{2}}\, dt",
            "formula",
        ),
        Note(
            "Why the v term disappears",
            "Substituting y = v y₁ collects y₁'' + P y₁' + Q y₁ as the "
            "coefficient of v, and that is zero because y₁ is a solution. "
            "Only v' and v'' survive, so the equation is first order in v'.",
            r"v\,(y_1'' + P y_1' + Q y_1) = 0",
            "idea",
        ),
        Note(
            "Standard form first",
            "P is the coefficient of y' after dividing by the coefficient of "
            "y''. Reading it straight off t y'' − (t + 1)y' + y = 0 as "
            "−(t + 1) instead of −(t + 1)/t gives a wrong v and a y₂ that "
            "fails when substituted.",
            r"P = \frac{b(t)}{a(t)}",
            "pitfall",
        ),
        Note(
            "It is where variation of parameters comes from",
            "Run the same substitution on a forced equation, allowing both "
            "solutions' coefficients to vary, and the result is variation of "
            "parameters. Reduction of order is the one-solution version of "
            "the same idea.",
            r"y = u_1 y_1 + u_2 y_2",
            "aside",
        ),
        Note(
            "Constant coefficients, seen again",
            "Applied to y'' − 2y' + y = 0 with y₁ = e^t, the method gives "
            "y₂ = t e^t — which is where the factor of t for a repeated "
            "characteristic root really comes from.",
            r"r = 1 \text{ twice} \;\Longrightarrow\; y_2 = t e^{t}",
            "idea",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="In reduction of order, why does the substitution y = v y₁ "
                   "lead to a first-order equation?",
            options=(
                "The coefficient of v is the equation applied to y₁, which is "
                "zero",
                "v is assumed to be a constant",
                "The v'' term cancels against the v' term",
                "y₁ is assumed to be an exponential",
            ),
            answer=0,
            becauses=(
                "Grouping by v, v' and v'' puts y₁'' + P y₁' + Q y₁ in front "
                "of v, and y₁ solves the equation — so only v' and v'' remain, "
                "and w = v' satisfies a first-order equation.",
                "If v were constant, y₂ would be a multiple of y₁ and not a "
                "new solution. The whole point is that v varies.",
                "v'' survives; it is v itself that disappears. The equation "
                "left is first order in v', not in v.",
                "y₁ can be any solution — a power of t, a polynomial, "
                "anything. The cancellation needs only that it solves the "
                "equation.",
            ),
        ),
        Choice(
            key="q2",
            prompt="For t² y'' + t y' − y = 0 with y₁ = t, what is P in the "
                   "formula?",
            options=("1/t", "t", "−1/t²", "1"),
            answer=0,
            becauses=(
                "Divide by t²: y'' + (1/t) y' − (1/t²) y = 0, so P = 1/t.",
                "That is the coefficient of y' before dividing by t². The "
                "formula needs the standard form.",
                "That is Q, the coefficient of y in standard form, not P.",
                "P is a function of t here; only after dividing does the "
                "coefficient of y' become clear, and it is 1/t.",
            ),
        ),
        Solve(
            key="q3",
            prompt="One solution is y₁ = t. Find the general solution.",
            equation="t**2*y'' - t*(t + 3)*y' + (t + 3)*y = 0",
            hints=(
                "Standard form: P = −(t + 3)/t = −1 − 3/t, so e^(−∫P) = "
                "t³ e^t.",
                "Divide by y₁² = t²: v' = t e^t. Integrate by parts.",
                "v = (t − 1)e^t, so y₂ = t(t − 1)e^t, and the general "
                "solution is C₁ t + C₂ t(t − 1)e^t.",
            ),
        ),
        Solve(
            key="q4",
            prompt="The first worked example with conditions: e^t is one "
                   "solution. Find the solution through y(1) = 0, y'(1) = 1.",
            equation="t*y'' - (t + 1)*y' + y = 0",
            conditions="y(1) = 0, y'(1) = 1",
            hints=(
                "The general solution is C₁ e^t + C₂(t + 1), from the worked "
                "example.",
                "At t = 1: C₁ e + 2C₂ = 0 and C₁ e + C₂ = 1.",
                "Subtracting gives C₂ = −1, then C₁ = 2/e.",
            ),
        ),
    ),
    templates=(
        Template(
            key="second-from-first",
            title="A second solution from y₁ = t",
            prompt="y₁ = t is one solution. Reduce the order and give the "
                   "general solution.",
            equation="t**2*y'' - t*({b}*t + {a})*y' + ({b}*t + {a})*y = 0",
            technique="reduction_of_order",
            hints=(
                "Divide by t² to get the standard form, and read off P as "
                "the coefficient of y'.",
                "Work out e^(−∫P) and divide by y₁² = t² — what is left is "
                "v', a power of t times an exponential.",
                "Integrate v' (by parts if a power of t is left), multiply "
                "by t for y₂, and combine C₁ y₁ + C₂ y₂.",
            ),
            slots=(("a", (2, 3)), ("b", (1, 2, 3))),
        ),
    ),
)


LESSONS = (SUPERPOSITION, ROOTS, UNDETERMINED, VARIATION, REDUCTION, CAUCHY,
           HIGHER)
