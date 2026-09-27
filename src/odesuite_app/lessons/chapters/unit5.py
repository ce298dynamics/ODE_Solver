"""Unit 5 chapters -- the Laplace transform (Edwards ch. 7)."""

from __future__ import annotations

from ..chapter import Box, Curve, Display, Figure, Para, Plot, Section, Step, Worked

__all__ = ["TRANSFORM", "LAPLACE", "SHIFTING", "CONVOLUTION", "STEPFORCING"]


LAPLACE = (
    Section("Solving an equation in three moves", (
        Para(
            "The last lesson built the tools: a table of transforms, "
            "linearity, and the rule that turns a derivative into "
            "multiplication by s. This lesson uses them on initial value "
            "problems, and the method never changes. Transform the equation, "
            "so that it becomes an algebraic equation for Y(s) with the "
            "initial values already inside it. Solve that equation for Y. "
            "Then invert: rearrange Y into pieces the table recognises, and "
            "read the solution off piece by piece."
        ),
        Para(
            "Almost all the effort is in the third move, and almost all of "
            "that is partial fractions. Y(s) is typically a ratio of "
            "polynomials in s, and the table recognises only a few simple "
            "shapes — 1/(s − a), s/(s² + k²), k/(s² + k²) and their shifted "
            "cousins. Partial fractions is the algebra that breaks a "
            "complicated ratio into a sum of those shapes. So this lesson is "
            "as much about partial fractions as about differential equations, "
            "and it is worth getting fluent in them."
        ),
        Box(
            "definition", "The transform method",
            "To solve a linear initial value problem with constant "
            "coefficients: (1) transform both sides, using the derivative "
            "rule with the initial values; (2) solve for Y(s); (3) decompose "
            "Y(s) by partial fractions; (4) invert each term using the table.",
            r"y \;\to\; Y(s) \;\to\; \text{algebra} \;\to\; y(t)",
        ),
        Para(
            "The Laplace Transforms screen of this application carries out "
            "exactly these four steps on any equation you type, showing the "
            "transformed equation, the solved Y(s), its partial fractions and "
            "the inversion as separate stages, and checking the final answer "
            "by substitution. It is worth working each example below by hand "
            "first and then comparing, stage by stage, with what the screen "
            "produces: a discrepancy points to the exact step where the hand "
            "calculation went astray. Most of the time it will be the partial "
            "fractions."
        ),
    )),
    Section("A first example, every step shown", (
        Worked(
            "Distinct real roots",
            "Solve y'' − y' − 2y = 0 with y(0) = 1, y'(0) = 0.",
            (
                Step("Transform, using L{y''} = s²Y − sy(0) − y'(0) and "
                     "L{y'} = sY − y(0):",
                     r"(s^{2}Y - s) - (sY - 1) - 2Y = 0"),
                Step("Collect the Y terms and solve. The quadratic multiplying "
                     "Y is the characteristic polynomial, which is no "
                     "coincidence.",
                     r"Y = \frac{s - 1}{s^{2} - s - 2} = \frac{s - 1}{(s - 2)(s + 1)}"),
                Step("Partial fractions: (s − 1)/((s − 2)(s + 1)) = A/(s − 2) + "
                     "B/(s + 1). Multiply through and set s = 2: 1 = 3A, so "
                     "A = 1/3. Set s = −1: −2 = −3B, so B = 2/3.",
                     r"Y = \frac{1/3}{s - 2} + \frac{2/3}{s + 1}"),
                Step("Invert each term from the table: 1/(s − a) comes from "
                     "e^(at)."),
            ),
            equation="y'' - y' - 2*y = 0", conditions="y(0) = 1, y'(0) = 0",
            answer="exp(2*t)/3 + 2*exp(-t)/3",
            answer_latex=r"y(t) = \frac{1}{3}e^{2t} + \frac{2}{3}e^{-t}",
        ),
        Para(
            "Two things in that example are worth underlining. The "
            "polynomial multiplying Y was s² − s − 2 — the characteristic "
            "polynomial of Unit 3 — so the transform method is secretly "
            "finding the characteristic roots too; they appear as the "
            "denominators of the partial fractions. And no constants had to "
            "be fitted: the initial values entered at the first step, and the "
            "answer came out already satisfying them."
        ),
    )),
    Section("Partial fractions, systematically", (
        Para(
            "A proper rational function P(s)/Q(s) — the degree of P below that "
            "of Q — can be written as a sum of simple fractions, one group for "
            "each factor of Q. The rules are the same as in the integration "
            "techniques of a calculus course, and they are summarised below."
        ),
        Box(
            "theorem", "Partial-fraction forms",
            "Each factor of the denominator contributes terms of a fixed "
            "shape: a simple linear factor s − a gives A/(s − a); a repeated "
            "factor (s − a)ⁿ gives A₁/(s − a) + … + Aₙ/(s − a)ⁿ; an irreducible "
            "quadratic s² + bs + c gives (Bs + C)/(s² + bs + c), and a repeated "
            "one a term for each power.",
            r"\frac{P(s)}{(s - a)(s - b)} = \frac{A}{s - a} + \frac{B}{s - b}",
        ),
        Para(
            "For distinct linear factors the *cover-up* method is quickest: to "
            "find the coefficient of 1/(s − a), cover up the factor s − a in "
            "the original fraction and evaluate what is left at s = a. That is "
            "exactly what setting s = 2 and s = −1 did in the example. For "
            "repeated and quadratic factors, multiply through by the "
            "denominator and either substitute convenient values of s or "
            "compare coefficients of like powers."
        ),
        Worked(
            "Three linear factors",
            "Solve y'' − 3y' + 2y = 4 with y(0) = 0, y'(0) = 0.",
            (
                Step("With zero initial values the transform is simply "
                     "(s² − 3s + 2)Y = 4/s, so Y = 4/(s(s − 1)(s − 2)).",
                     r"Y = \frac{4}{s(s - 1)(s - 2)}"),
                Step("Cover-up: at s = 0 the rest is 4/((−1)(−2)) = 2; at s = 1, "
                     "4/(1·(−1)) = −4; at s = 2, 4/(2·1) = 2.",
                     r"Y = \frac{2}{s} - \frac{4}{s - 1} + \frac{2}{s - 2}"),
                Step("Invert: 2 − 4e^t + 2e^(2t). The constant 2 is the steady "
                     "state 4/2 that the forcing alone would produce; the "
                     "exponentials make up the start from rest."),
            ),
            equation="y'' - 3*y' + 2*y = 4", conditions="y(0) = 0, y'(0) = 0",
            answer="2 - 4*exp(t) + 2*exp(2*t)",
            answer_latex=r"y(t) = 2 - 4e^{t} + 2e^{2t}",
        ),
        Figure("partial_fractions",
               "A rational function of s and its partial fractions side by "
               "side: each pole of the denominator becomes one simple term, "
               "and each term one exponential or sinusoid in the solution."),
    )),
    Section("Quadratic factors: forcing by a sinusoid", (
        Para(
            "Sinusoidal forcing and oscillatory solutions bring irreducible "
            "quadratics like s² + k² into the denominator. The partial "
            "fraction for such a factor has a linear numerator, (Bs + C)/(s² + "
            "k²), and it inverts to B cos kt + (C/k) sin kt. When all the "
            "quadratic factors are of the form s² + k², a useful shortcut is to "
            "treat s² as a single variable."
        ),
        Worked(
            "Two frequencies",
            "Solve y'' + 4y = sin t with y(0) = 0, y'(0) = 0.",
            (
                Step("(s² + 4)Y = 1/(s² + 1), so Y = 1/((s² + 1)(s² + 4)).",
                     r"Y = \frac{1}{(s^{2} + 1)(s^{2} + 4)}"),
                Step("Treat s² as u: 1/((u + 1)(u + 4)) = (1/3)(1/(u + 1) − "
                     "1/(u + 4)) by cover-up.",
                     r"Y = \frac{1}{3}\left(\frac{1}{s^{2} + 1} - "
                     r"\frac{1}{s^{2} + 4}\right)"),
                Step("1/(s² + 1) inverts to sin t and 1/(s² + 4) to (1/2)sin 2t."),
            ),
            equation="y'' + 4*y = sin(t)", conditions="y(0) = 0, y'(0) = 0",
            answer="sin(t)/3 - sin(2*t)/6",
            answer_latex=r"y(t) = \frac{1}{3}\sin t - \frac{1}{6}\sin 2t",
        ),
        Plot(
            "The response to sin t of a system tuned to 2",
            "y = sin t/3 − sin 2t/6: the forcing frequency 1 and the natural "
            "frequency 2 both appear, each coming from one quadratic factor "
            "in the denominator of Y. The transform found both without a "
            "separate complementary function.",
            (Curve("sin(t)/3 - sin(2*t)/6", "y(t)"),
             Curve("sin(t)/3", "forced part")),
            t=(0.0, 13.0),
        ),
    )),
    Section("Repeated factors and resonance", (
        Worked(
            "A repeated quadratic",
            "Solve y'' + y = 2 cos t with y(0) = 0, y'(0) = 0.",
            (
                Step("(s² + 1)Y = 2s/(s² + 1), so Y = 2s/(s² + 1)². The repeated "
                     "factor signals resonance: the forcing is at the natural "
                     "frequency.",
                     r"Y = \frac{2s}{(s^{2} + 1)^{2}}"),
                Step("The last lesson found L{t sin t} = 2s/(s² + 1)² by "
                     "differentiating in s, so the solution is t sin t — the "
                     "linearly growing response of Unit 4."),
            ),
            equation="y'' + y = 2*cos(t)", conditions="y(0) = 0, y'(0) = 0",
            answer="t*sin(t)", answer_latex=r"y(t) = t\sin t",
        ),
        Para(
            "In Unit 3 resonance required the modification rule, a special "
            "case to remember. Here it required nothing special at all: the "
            "algebra produced a squared factor and the table entry for "
            "t sin t read it off. That is typical of the transform method — "
            "the exceptional cases of the classical method become ordinary "
            "entries in a table, and the method does not need to know in "
            "advance which case it is in."
        ),
    )),
    Section("First-order equations", (
        Para(
            "The method works just as well at first order, where it is an "
            "alternative to the integrating factor. The derivative rule "
            "needs only y(0), and the algebra is a single division."
        ),
        Worked(
            "A cancellation",
            "Solve y' + 2y = e^(−t) with y(0) = 1.",
            (
                Step("sY − 1 + 2Y = 1/(s + 1), so "
                     "Y = 1/((s + 1)(s + 2)) + 1/(s + 2).",
                     r"Y = \frac{1}{(s + 1)(s + 2)} + \frac{1}{s + 2}"),
                Step("The first fraction is 1/(s + 1) − 1/(s + 2), and its second "
                     "term cancels the 1/(s + 2) outside. So Y = 1/(s + 1), and "
                     "y = e^(−t).",
                     r"Y = \frac{1}{s + 1}"),
                Step("Check: y' + 2y = −e^(−t) + 2e^(−t) = e^(−t), and y(0) = 1. "
                     "The initial value happened to be exactly the one for "
                     "which the natural mode e^(−2t) is absent."),
            ),
            equation="y' + 2*y = exp(-t)", conditions="y(0) = 1",
            answer="exp(-t)", answer_latex=r"y(t) = e^{-t}",
        ),
    )),
    Section("Why it always works: the transformed equation in general", (
        Para(
            "It is worth doing the first move once in general, because the "
            "result explains the whole method. Transform ay'' + by' + cy = f(t) "
            "with initial values y(0) = y₀ and y'(0) = y₁. The derivative rules "
            "give a(s²Y − sy₀ − y₁) + b(sY − y₀) + cY = F(s), and collecting the "
            "terms in Y leaves a single linear equation."
        ),
        Display(r"(a s^{2} + b s + c)\, Y = F(s) + (a s + b)\, y_0 + a\, y_1", "1"),
        Para(
            "So Y is always the right-hand side divided by the characteristic "
            "polynomial p(s) = as² + bs + c. The right-hand side has two "
            "parts: the transform of the forcing, and a polynomial built from "
            "the initial values. Dividing splits the solution accordingly "
            "into the response to the forcing with zero initial values, "
            "F(s)/p(s), and the response to the initial values with no "
            "forcing. The classical method called these the particular "
            "solution and the complementary function; the transform method "
            "produces both from one division."
        ),
        Display(r"Y = \frac{F(s)}{p(s)} + \frac{(a s + b)\, y_0 + a\, y_1}{p(s)}",
                "2"),
    )),
    Section("The transfer function", (
        Para(
            "The factor 1/p(s) in (2) depends only on the system, not on the "
            "forcing or the initial values, and it has a name: the *transfer "
            "function*, G(s) = 1/p(s). With zero initial values, the "
            "transform of the output is simply G(s) times the transform of "
            "the input, Y = G·F. A system is described completely by its "
            "transfer function, and the response to any input is found by one "
            "multiplication in the s-domain."
        ),
        Para(
            "This is how control engineers think. A motor, an amplifier and a "
            "sensor each have a transfer function, and when they are "
            "connected in a chain the transfer function of the whole is the "
            "product of the parts. Feedback — feeding the output back to the "
            "input — produces a new transfer function whose poles can be "
            "moved by the design, which is the whole art of making systems "
            "stable and responsive. The convolution lesson later in this unit "
            "shows what multiplying by G(s) means back in the time domain."
        ),
        Box(
            "remark", "Reading the transfer function",
            "For the spring my'' + cy' + ky = f, G(s) = 1/(ms² + cs + k). Its "
            "poles are the characteristic roots, the natural modes; its value "
            "at s = iω, in size, is the amplitude response C(ω)/F₀ of the "
            "forced-vibration lesson. The frequency response is the transfer "
            "function evaluated on the imaginary axis.",
        ),
    )),
    Section("Higher order, no harder", (
        Para(
            "The method does not change with the order of the equation. A "
            "third-order equation needs three initial values and the rule "
            "L{y'''} = s³Y − s²y(0) − sy'(0) − y''(0); after that it is the "
            "same algebra. The characteristic polynomial is now cubic, and the "
            "partial fractions have one more term, but nothing new has to be "
            "understood."
        ),
        Worked(
            "A third-order problem",
            "Solve y''' − y' = 0 with y(0) = 1, y'(0) = 0, y''(0) = 1.",
            (
                Step("Transform: (s³Y − s² − 0 − 1) − (sY − 1) = 0, and the "
                     "constants cancel to leave (s³ − s)Y = s².",
                     r"Y = \frac{s^{2}}{s(s^{2} - 1)} = \frac{s}{s^{2} - 1}"),
                Step("The factor s cancels, and s/(s² − 1) is the transform of "
                     "cosh t. (Partial fractions give the same thing: "
                     "(1/2)/(s − 1) + (1/2)/(s + 1), which is (e^t + e^(−t))/2.)"),
            ),
            equation="y''' - y' = 0", conditions="y(0) = 1, y'(0) = 0, y''(0) = 1",
            answer="cosh(t)", answer_latex=r"y(t) = \cosh t",
        ),
        Para(
            "Notice the cancellation of s. The characteristic polynomial has "
            "the root 0, so the general solution contains a constant term; "
            "these particular initial values happen to make that term zero, "
            "and the transform shows it by cancelling the pole at s = 0 before "
            "any partial fractions are needed. Cancellations like this are "
            "not accidents to be surprised by; they are the transform's way "
            "of reporting that a mode is absent."
        ),
    )),
    Section("Comparing the two methods", (
        Para(
            "For equations that Unit 3 can already solve, which method is "
            "better? For homogeneous equations and simple forcing, the "
            "classical method is often quicker: write down the characteristic "
            "roots, guess the particular solution, fit two constants. The "
            "transform method does the same work in a different order and "
            "costs a partial-fraction decomposition that can be longer than "
            "the classical algebra."
        ),
        Para(
            "The transform method wins in three situations. When the initial "
            "values are the point — in engineering, most problems start from "
            "rest, and zero initial values make the transform especially "
            "clean. When the forcing is discontinuous or impulsive, where the "
            "classical method has to solve piece by piece and match at every "
            "switch, and the transform handles the whole thing at once, as "
            "the step-forcing and impulse lessons show. And when the same "
            "system is driven by many different inputs, where the transfer "
            "function is computed once and reused."
        ),
    )),
    Section("Poles and behaviour", (
        Para(
            "The denominators of Y(s) carry the qualitative behaviour of the "
            "solution, and with practice it can be read off before any "
            "partial fractions are done. The values of s where the denominator "
            "vanishes are called the *poles* of Y. A pole at a real number a "
            "produces e^(at): decaying if a < 0, growing if a > 0. A pair of "
            "complex poles α ± iβ produces e^(αt) times a sinusoid of frequency "
            "β. A repeated pole multiplies by powers of t."
        ),
        Para(
            "So the location of the poles in the complex plane is a picture "
            "of the solution's character. Poles in the left half-plane mean "
            "decay; poles on the imaginary axis mean sustained oscillation; "
            "poles in the right half-plane mean growth. Engineers designing "
            "feedback systems reason almost entirely in terms of pole "
            "positions, moving them leftwards to make a system more stable "
            "and further from the axis to make it ring less. The next lesson "
            "shows how a pole off the real axis is handled with the shifting "
            "theorem."
        ),
        Box(
            "remark", "Poles come from two places",
            "Some poles of Y come from the characteristic polynomial — the "
            "system's own modes — and some from the transform of the forcing. "
            "The first kind produce the transient, the second the forced "
            "response. When a forcing pole coincides with a system pole, the "
            "pole is repeated, and that is resonance.",
        ),
    )),
    Section("Quick checks: the initial- and final-value theorems", (
        Para(
            "Two theorems let an answer be checked without inverting. The "
            "*initial-value theorem* says that sY(s) tends to y(0) as s → ∞, "
            "and the *final-value theorem* that sY(s) tends to the limit of "
            "y(t) as t → ∞ when s → 0 — provided that limit exists, which "
            "requires every pole of sY(s) to lie in the left half-plane."
        ),
        Display(r"\lim_{s\to\infty} sY(s) = y(0), \qquad "
                r"\lim_{s\to 0} sY(s) = \lim_{t\to\infty} y(t)"),
        Para(
            "For the charging capacitor of the circuits lesson, "
            "Q(s) = 1.2/(s(s + 10)), so sQ(s) = 1.2/(s + 10), which tends to 0 as "
            "s → ∞ — the capacitor starts uncharged — and to 0.12 as s → 0 — its "
            "final charge. Both facts are confirmed without any partial "
            "fractions. But for Y = 4/(s(s − 1)(s − 2)) in this lesson, sY has "
            "poles at 1 and 2, in the right half-plane, and the final-value "
            "theorem does not apply: blindly it would give 4/((−1)(−2)) = 2, "
            "while the true solution 2 − 4e^t + 2e^(2t) grows without bound. "
            "The condition on the poles is not a technicality."
        ),
    )),
    Section("Common errors", (
        Para(
            "Most errors come in the partial fractions. Using a constant "
            "numerator over a quadratic factor, A/(s² + 1) instead of "
            "(Bs + C)/(s² + 1), loses the cosine part. Using only the highest "
            "power for a repeated factor, A/(s − 2)² without B/(s − 2), makes the "
            "equations for the coefficients inconsistent. And applying "
            "cover-up to a repeated or quadratic factor, where it does not "
            "work directly, gives wrong numbers silently."
        ),
        Para(
            "In the inversion, the frequency must be matched: 1/(s² + 4) is "
            "(1/2) sin 2t, not sin 2t, because the table entry is k/(s² + k²) "
            "with k in the numerator. And an improper fraction — numerator of "
            "degree at least that of the denominator — signals an algebra "
            "error earlier, since the transform of a solution of an ordinary "
            "initial value problem is always proper. Checking the final "
            "answer against the equation and both initial values catches all "
            "of these."
        ),
    )),
    Section("Summary", (
        Para(
            "To solve a linear initial value problem with constant "
            "coefficients by transform: transform both sides, putting in the "
            "initial values through L{y'} = sY − y(0) and "
            "L{y''} = s²Y − sy(0) − y'(0); solve the resulting algebraic "
            "equation for Y; split Y into partial fractions, one group per "
            "factor of the denominator; and invert each term from the table. "
            "The characteristic polynomial appears as the coefficient of Y, "
            "the constants never need fitting, and resonance is simply a "
            "repeated factor. The poles of Y — real, complex or repeated — tell "
            "the character of the solution at a glance."
        ),
    )),
)


TRANSFORM = (
    Section("Turning calculus into algebra", (
        Para(
            "Every method so far has attacked a differential equation "
            "directly: guessing a form, separating, integrating. The Laplace "
            "transform takes a different road. It converts a function of time "
            "into a function of a new variable s in such a way that "
            "*differentiation becomes multiplication by s*. A linear "
            "differential equation with constant coefficients then becomes an "
            "algebraic equation, which is solved by algebra, and the answer is "
            "converted back. Three steps — transform, solve, invert — replace "
            "all the case-by-case reasoning of Unit 3."
        ),
        Para(
            "The payoff is largest exactly where the earlier methods "
            "struggle: forcing that switches on and off, impulses that act in "
            "an instant, and initial conditions that must be fitted "
            "separately at the end. The transform builds the initial "
            "conditions in from the start and handles discontinuous forcing "
            "as easily as smooth. It is the standard tool of control and "
            "electrical engineering for exactly those reasons, and this "
            "lesson sets up the machinery: the definition, the basic "
            "transforms, and the one rule that makes it all work."
        ),
        Para(
            "The idea is older than it looks. Logarithms work the same way: "
            "they turn multiplication into addition, so a hard multiplication "
            "is done by transforming the numbers, adding, and transforming "
            "back. The Laplace transform does for differential equations what "
            "logarithms did for arithmetic, and like a table of logarithms, "
            "much of its practical use comes from a table of transforms."
        ),
    )),
    Section("The definition", (
        Box(
            "definition", "Laplace transform",
            "The Laplace transform of a function f(t) defined for t ≥ 0 is the "
            "function F(s) given by the improper integral below, for all s at "
            "which the integral converges.",
            r"F(s) = \mathcal{L}\{f\}(s) = \int_{0}^{\infty} e^{-st} f(t)\, dt",
        ),
        Para(
            "The factor e^(−st) is a weight that discounts later times: for "
            "large s it decays quickly and the integral mostly sees f near "
            "t = 0, while for small s it decays slowly and the integral "
            "averages f over a long stretch. Each value of s asks the "
            "function a different question, and the whole function F answers "
            "all of them at once. The integral is improper, so it is defined "
            "as a limit, and it converges only for s large enough that the "
            "weight beats the growth of f."
        ),
        Figure("transform_area",
               "The transform as an area: the integrand e^(−st)f(t) for a "
               "chosen s, shaded. Increase s and watch the weight crush the "
               "later part of f and the area shrink."),
    )),
    Section("The first transforms", (
        Worked(
            "The constant function",
            "Find the transform of f(t) = 1.",
            (
                Step("Integrate e^(−st) from 0 to a limit b, and let b → ∞:",
                     r"\int_{0}^{b} e^{-st}\, dt = \frac{1 - e^{-sb}}{s}"),
                Step("For s > 0, e^(−sb) → 0, so the limit is 1/s. For s ≤ 0 "
                     "the integral diverges, so the transform exists only "
                     "for s > 0.",
                     r"\mathcal{L}\{1\} = \frac{1}{s}, \quad s > 0"),
            ),
            answer_latex=r"\mathcal{L}\{1\} = \frac{1}{s}",
        ),
        Worked(
            "An exponential",
            "Find the transform of f(t) = e^(at).",
            (
                Step("Combine the exponentials: e^(−st)e^(at) = e^(−(s − a)t), "
                     "which is the previous integral with s − a in place of s.",
                     r"\int_{0}^{\infty} e^{-(s-a)t}\, dt = \frac{1}{s - a}"),
                Step("It converges when s − a > 0, that is s > a. So the larger "
                     "a, the larger s must be — the weight must decay faster "
                     "than f grows."),
            ),
            answer_latex=r"\mathcal{L}\{e^{at}\} = \frac{1}{s - a}, \quad s > a",
        ),
        Para(
            "That one result generates most of the table. With a = 0 it is the "
            "constant function again. With a = ik, and Euler's formula, it "
            "gives the transforms of cos kt and sin kt at once, as Section 5 "
            "shows. And differentiating it with respect to a gives the "
            "transform of te^(at), which is 1/(s − a)² — a trick worth "
            "remembering."
        ),
    )),
    Section("Powers of t", (
        Para(
            "For f(t) = tⁿ, integration by parts reduces the power by one each "
            "time. Taking u = tⁿ and dv = e^(−st)dt, the boundary term vanishes "
            "for s > 0 and what remains is n/s times the transform of tⁿ⁻¹. "
            "Repeating n times reaches the transform of 1, which is 1/s."
        ),
        Display(r"\mathcal{L}\{t^{n}\} = \frac{n}{s}\,\mathcal{L}\{t^{n-1}\} = "
                r"\cdots = \frac{n!}{s^{n+1}}", "1"),
        Worked(
            "A cube",
            "Find the transform of t³.",
            (
                Step("By (1), L{t³} = 3!/s⁴ = 6/s⁴, valid for s > 0.",
                     r"\mathcal{L}\{t^{3}\} = \frac{6}{s^{4}}"),
            ),
            answer_latex=r"\mathcal{L}\{t^{3}\} = \frac{6}{s^{4}}",
        ),
        Para(
            "Formula (1) extends to non-integer powers with the gamma "
            "function, Γ(n + 1) in place of n!: for instance "
            "L{t^(−1/2)} = √(π/s). The transform does not require f to be "
            "bounded near t = 0 — t^(−1/2) is infinite there — only that its "
            "integral against the weight converges."
        ),
    )),
    Section("Linearity, and the trigonometric transforms", (
        Box(
            "theorem", "Linearity",
            "If the transforms of f and g exist for s > c, then for any "
            "constants a and b the transform of af + bg exists there and "
            "equals aF + bG.",
            r"\mathcal{L}\{a f + b g\} = a F(s) + b G(s)",
        ),
        Para(
            "Linearity is inherited from the integral, and it is what makes "
            "a table useful: a combination is transformed term by term. It "
            "also produces the trigonometric transforms without any "
            "integration by parts. Write cos kt = (e^(ikt) + e^(−ikt))/2 and use "
            "the exponential result with a = ±ik; the two fractions combine "
            "over a common denominator into a real expression."
        ),
        Display(r"\mathcal{L}\{\cos kt\} = \frac{s}{s^{2} + k^{2}}, \qquad "
                r"\mathcal{L}\{\sin kt\} = \frac{k}{s^{2} + k^{2}}", "2"),
        Para(
            "The same method with real exponentials gives the hyperbolic "
            "versions, L{cosh kt} = s/(s² − k²) and L{sinh kt} = k/(s² − k²), "
            "for s > |k|. The resemblance of the two pairs is no accident: "
            "cosh and cos differ only by whether the exponentials are real or "
            "imaginary, and the transform reflects that by a sign in the "
            "denominator."
        ),
        Worked(
            "A combination",
            "Find the transform of 3e^(2t) − 5 sin 3t.",
            (
                Step("By linearity and the table, 3/(s − 2) − 5·3/(s² + 9), "
                     "valid for s > 2.",
                     r"\frac{3}{s - 2} - \frac{15}{s^{2} + 9}"),
                Step("Over a common denominator this is "
                     "3(s² − 5s + 19)/((s − 2)(s² + 9)), which is how a "
                     "transform often appears in practice — and why partial "
                     "fractions will be needed to invert it."),
            ),
            answer_latex=r"\frac{3(s^{2} - 5s + 19)}{(s - 2)(s^{2} + 9)}",
        ),
        Worked(
            "Using an identity first",
            "Find the transform of sin²t.",
            (
                Step("sin²t is not in the table, but the double-angle identity "
                     "makes it a combination of things that are: "
                     "sin²t = (1 − cos 2t)/2.",
                     r"\sin^{2} t = \frac{1}{2} - \frac{1}{2}\cos 2t"),
                Step("By linearity, (1/2)(1/s) − (1/2)s/(s² + 4), which "
                     "simplifies to 2/(s(s² + 4)).",
                     r"\mathcal{L}\{\sin^{2}t\} = \frac{2}{s(s^{2} + 4)}"),
            ),
            answer_latex=r"\mathcal{L}\{\sin^{2}t\} = \frac{2}{s(s^{2} + 4)}",
        ),
        Plot(
            "Three transforms as functions of s",
            "F(s) = 1/s for f = 1, 1/(s − 1) for f = e^t and 1/(s² + 1) for "
            "f = sin t, on s > 1. Every transform tends to zero as s grows: "
            "the weight e^(−st) eventually crushes any function of "
            "exponential order.",
            (Curve("1/t", "f = 1"), Curve("1/(t - 1)", "f = e^t"),
             Curve("1/(t**2 + 1)", "f = sin t")),
            t=(1.2, 6.0), xlabel="s", ylabel="F(s)", ylim=(0.0, 5.0),
        ),
    )),
    Section("When does the transform exist?", (
        Para(
            "Two things can prevent the integral converging: the function can "
            "grow too fast for any weight to tame, or it can be too wild to "
            "integrate at all. Both are ruled out by a pair of conditions "
            "that cover every function a course meets."
        ),
        Box(
            "definition", "Exponential order",
            "f is of *exponential order* c if there are constants M and T with "
            "|f(t)| ≤ Me^(ct) for all t ≥ T. It is *piecewise continuous* if on "
            "every finite interval it has at most finitely many jumps and is "
            "continuous between them.",
            r"|f(t)| \leq M e^{ct}, \quad t \geq T",
        ),
        Box(
            "theorem", "Existence",
            "If f is piecewise continuous on [0, ∞) and of exponential order "
            "c, its Laplace transform exists for every s > c, and F(s) → 0 as "
            "s → ∞.",
        ),
        Para(
            "Polynomials, exponentials, sines, cosines and their products and "
            "sums are all of exponential order, and so are the switched and "
            "piecewise functions later in the unit. The function e^(t²) is "
            "not: it outgrows every exponential, and its transform does not "
            "exist for any s. Neither does 1/t, whose integral diverges at 0. "
            "The last clause of the theorem is a useful check — a proposed "
            "transform that does not tend to zero, such as s/(s + 1), cannot "
            "be the transform of any such function."
        ),
    )),
    Section("Piecewise functions", (
        Para(
            "The transform integrates over all t ≥ 0, and it does not care "
            "whether f is given by one formula or several. A function that is "
            "defined in pieces is transformed by splitting the integral at "
            "the joins, and this is the first sign of the transform's "
            "strength with switched forcing."
        ),
        Worked(
            "A window",
            "Find the transform of f(t) = 1 for 0 ≤ t < 2 and 0 for t ≥ 2.",
            (
                Step("Only the interval [0, 2) contributes:",
                     r"\int_{0}^{2} e^{-st}\, dt = \frac{1 - e^{-2s}}{s}"),
                Step("The factor e^(−2s) records where the function switched "
                     "off. Later in the unit such factors will be read as "
                     "delays, and inverted directly."),
            ),
            answer_latex=r"\mathcal{L}\{f\} = \frac{1 - e^{-2s}}{s}",
        ),
        Para(
            "In the language of the step-forcing lesson, that function is "
            "1 − u(t − 2), where the unit step u(t − 2) switches on at t = 2 "
            "and has transform e^(−2s)/s. A switch in time becomes an "
            "exponential factor in s, and that correspondence will make "
            "equations with discontinuous forcing no harder than any others."
        ),
    )),
    Section("What it is for: transforming a derivative", (
        Para(
            "The single property that makes the transform useful for "
            "differential equations is what it does to a derivative. "
            "Integrate L{f'} by parts: the boundary term at infinity vanishes "
            "for f of exponential order, and the boundary term at 0 leaves "
            "−f(0). What remains is s times the transform of f."
        ),
        Box(
            "theorem", "Transform of a derivative",
            "If f is continuous and of exponential order and f' is piecewise "
            "continuous, then the transform of f' is sF(s) − f(0). Applying "
            "it twice gives the second derivative.",
            r"\mathcal{L}\{f'\} = sF(s) - f(0), \qquad \mathcal{L}\{f''\} = "
            r"s^{2}F(s) - s f(0) - f'(0)",
        ),
        Para(
            "Notice what has happened to the initial values: they appear in "
            "the transformed equation as ordinary numbers. That is why the "
            "transform method never needs a separate step to fit constants — "
            "the initial conditions are part of the algebra from the start."
        ),
        Worked(
            "A first equation, by transform",
            "Solve y' + y = 1 with y(0) = 0.",
            (
                Step("Transform both sides, with Y = L{y}: sY − 0 + Y = 1/s.",
                     r"(s + 1)\, Y = \frac{1}{s}"),
                Step("Solve the algebra: Y = 1/(s(s + 1)) = 1/s − 1/(s + 1) by "
                     "partial fractions.",
                     r"Y = \frac{1}{s} - \frac{1}{s + 1}"),
                Step("Read each term backwards from the table: 1/s comes from 1 "
                     "and 1/(s + 1) from e^(−t)."),
            ),
            equation="y' + y = 1", conditions="y(0) = 0",
            answer="1 - exp(-t)", answer_latex=r"y(t) = 1 - e^{-t}",
        ),
        Worked(
            "A second-order equation",
            "Solve y'' + 9y = 0 with y(0) = 2, y'(0) = 3.",
            (
                Step("Transform: s²Y − 2s − 3 + 9Y = 0, so (s² + 9)Y = 2s + 3.",
                     r"Y = \frac{2s}{s^{2} + 9} + \frac{3}{s^{2} + 9}"),
                Step("By (2), 2s/(s² + 9) is the transform of 2 cos 3t and "
                     "3/(s² + 9) that of sin 3t."),
            ),
            equation="y'' + 9*y = 0", conditions="y(0) = 2, y'(0) = 3",
            answer="2*cos(3*t) + sin(3*t)", answer_latex=r"y(t) = 2\cos 3t + \sin 3t",
        ),
    )),
    Section("Going back: uniqueness and the inverse", (
        Para(
            "Reading a transform backwards — from F(s) to f(t) — relies on a "
            "theorem that is easy to take for granted: that different "
            "functions have different transforms. Without it, recognising "
            "1/(s + 1) in a table as the transform of e^(−t) would prove "
            "nothing, since some other function might have the same "
            "transform."
        ),
        Box(
            "theorem", "Uniqueness (Lerch)",
            "If two continuous functions of exponential order have the same "
            "Laplace transform, they are equal for all t ≥ 0. (Piecewise "
            "continuous functions with the same transform can differ only at "
            "their jump points.)",
        ),
        Para(
            "So the *inverse transform* L⁻¹ is well defined, and in practice "
            "it is computed not by an integral formula — one exists, but it "
            "needs complex analysis — but by rearranging F(s) into pieces that "
            "appear in a table. The main tool for that rearrangement is "
            "partial fractions, and the next lesson is about doing it "
            "systematically."
        ),
    )),
    Section("One more trick: differentiating in s", (
        Para(
            "Differentiating the definition F(s) = ∫e^(−st)f(t) dt with respect "
            "to s brings down a factor −t inside the integral. So multiplying "
            "a function by t corresponds to differentiating its transform and "
            "changing the sign. This extends the table cheaply: every entry "
            "yields another by one differentiation."
        ),
        Display(r"\mathcal{L}\{t\, f(t)\} = -F'(s)"),
        Worked(
            "t times an exponential, and t times a sine",
            "Find the transforms of te^(3t) and t sin t.",
            (
                Step("L{e^(3t)} = 1/(s − 3), whose derivative is −1/(s − 3)². "
                     "Changing the sign: L{te^(3t)} = 1/(s − 3)².",
                     r"\mathcal{L}\{t e^{3t}\} = \frac{1}{(s - 3)^{2}}"),
                Step("L{sin t} = 1/(s² + 1), whose derivative is −2s/(s² + 1)². "
                     "So L{t sin t} = 2s/(s² + 1)² — the transform of the "
                     "resonant response met in the vibrations unit.",
                     r"\mathcal{L}\{t\sin t\} = \frac{2s}{(s^{2} + 1)^{2}}"),
            ),
            answer_latex=r"\frac{1}{(s-3)^{2}}, \qquad \frac{2s}{(s^{2}+1)^{2}}",
        ),
        Para(
            "The repeated factor (s² + 1)² in that last transform is worth "
            "noticing. Resonance — forcing at a natural frequency — shows up in "
            "the s-domain as a repeated factor in the denominator, just as it "
            "showed up in Unit 3 as a repeated characteristic root. The two "
            "descriptions are the same fact in two languages, and learning to "
            "read the s-language is most of what this unit teaches."
        ),
    )),
    Section("The method in outline", (
        Para(
            "Every application of the transform to an initial value problem "
            "follows the same four steps, and it helps to see them together "
            "before the details of the next lessons fill them in. First, "
            "transform both sides of the equation, using linearity and the "
            "derivative rule, so that each derivative becomes a power of s "
            "times Y plus terms containing the initial values. Second, solve "
            "the resulting algebraic equation for Y(s). Third, rearrange "
            "Y(s) — usually by partial fractions — into pieces that appear "
            "in the table. Fourth, read off y(t) piece by piece."
        ),
        Para(
            "What makes this efficient is that the difficult parts of the "
            "classical method disappear. There is no separate complementary "
            "function and particular solution; the forcing term's transform "
            "simply appears on the right, and the algebra combines everything "
            "at once. There is no fitting of constants at the end; the "
            "initial values entered at the first step. And a forcing that "
            "switches on and off is no harder than a smooth one, because its "
            "transform is just another function of s. The price is the table "
            "and the partial fractions, and the next lessons make both "
            "routine."
        ),
    )),
    Section("A little history", (
        Para(
            "Pierre-Simon Laplace used integrals of this kind in the late "
            "eighteenth century in his work on probability, but the transform "
            "became a practical "
            "tool for differential equations only a century later, through the "
            "*operational calculus* of the electrical engineer Oliver "
            "Heaviside. Heaviside treated the derivative d/dt as an algebraic "
            "symbol p, solved circuit equations by manipulating p as if it "
            "were a number, and got correct answers by methods mathematicians "
            "of the time regarded as unjustified. The Laplace transform is "
            "what later made his methods rigorous: his p is the s of this "
            "lesson, and his unit step is the u(t − a) of the step-forcing "
            "lesson, which still carries his name as the Heaviside function."
        ),
    )),
    Section("Common errors", (
        Para(
            "Forgetting the initial values in the derivative rule is the most "
            "frequent mistake: L{y'} is sY − y(0), not sY, and L{y''} is "
            "s²Y − sy(0) − y'(0), with the s multiplying y(0) and not y'(0). "
            "Mixing up the cosine and sine transforms is next — the cosine has "
            "s on top, the sine has k. And the transform of a product is *not* "
            "the product of the transforms: L{t sin t} is not "
            "(1/s²)·(1/(s² + 1)). Products need the differentiation rule above, "
            "or the shifting and convolution rules of later lessons."
        ),
        Para(
            "Finally, keep track of where each transform is valid. L{e^(at)} "
            "needs s > a, and a combination is valid only where every term "
            "is. For solving differential equations the region of validity "
            "rarely matters in the arithmetic, since s is only a symbol that "
            "is eliminated at the end, but it matters for the theory, and a "
            "transform that exists for no s at all — as for e^(t²) — means the "
            "method cannot be used for that function."
        ),
    )),
    Section("Summary", (
        Para(
            "The Laplace transform F(s) = ∫₀^∞ e^(−st)f(t) dt turns a function of "
            "time into a function of s. It exists for piecewise continuous "
            "functions of exponential order, for s large enough, and tends to "
            "zero as s grows. The basic table — 1/s, 1/(s − a), n!/s^(n+1), "
            "s/(s² + k²), k/(s² + k²) — follows from the exponential and "
            "linearity. A switch in time becomes a factor e^(−as). Most "
            "importantly, differentiation becomes multiplication by s, with the "
            "initial values appearing as numbers, so a linear equation with "
            "constant coefficients becomes algebra. Transforms are unique, so "
            "the answer can be read back from the table."
        ),
    )),
)


SHIFTING = (
    Section("A short table, stretched", (
        Para(
            "The table of transforms built two lessons ago is short: constants, "
            "powers of t, exponentials, sines and cosines. Yet the solutions of "
            "constant-coefficient equations are full of products — e^(−t) cos 2t "
            "for a damped spring, t·e^(2t) for a repeated root, t²e^(−t) for a "
            "forced response at resonance with a damped system. None of these is "
            "on the table, and working out each transform from the definition "
            "would mean an integration by parts every time."
        ),
        Para(
            "This lesson removes nearly all of that work with two tools. The "
            "first shifting theorem says that multiplying a function by an "
            "exponential in t slides its transform along the s axis, so every "
            "entry of the table becomes a whole family of entries. Partial "
            "fractions, extended here to repeated factors and irreducible "
            "quadratics, is the algebra that breaks any rational Y(s) into "
            "pieces that belong to one of those families. Between them they "
            "invert every transform that a linear equation with constant "
            "coefficients and exponential, polynomial or sinusoidal forcing can "
            "produce."
        ),
        Para(
            "There is a second shifting theorem too, and it is the subject of "
            "the step-forcing lesson. It is mentioned at the end of this chapter "
            "only to separate it clearly from the first, because confusing the "
            "two is the most common single error in the whole unit."
        ),
    )),
    Section("The first shifting theorem", (
        Box(
            "theorem", "First shifting theorem",
            "If F(s) = L{f(t)} exists for s > c, then for any real number a the "
            "transform of e^(at)f(t) exists for s > a + c, and it is F with s "
            "replaced by s − a.",
            r"\mathcal{L}\left\{e^{at}f(t)\right\} = F(s - a)",
        ),
        Box(
            "proof", "Proof",
            "Write out the definition. The two exponentials inside the integral "
            "combine into one, and the result is the defining integral of F "
            "evaluated at the point s − a instead of s. It converges whenever "
            "s − a > c, which is the stated condition.",
            r"\int_{0}^{\infty} e^{-st}e^{at}f(t)\,dt = "
            r"\int_{0}^{\infty} e^{-(s-a)t}f(t)\,dt = F(s-a)",
        ),
        Para(
            "Everything about the theorem is in that one line, and the idea is "
            "worth saying in words. The transform weights f by e^(−st). An extra "
            "factor e^(at) in the function is indistinguishable from a weaker "
            "weight e^(−(s − a)t), so the transform sees f through a weight that "
            "is a units of s less severe. The graph of F(s − a) is the graph of "
            "F(s) moved a units to the right: every feature of F, including the "
            "poles, moves with it."
        ),
        Para(
            "Read in the other direction, the theorem is an inversion rule. "
            "Whenever a transform is a known F evaluated at s − a — whenever s "
            "appears only in the combination s − a — the inverse is e^(at) times "
            "the inverse of F. The practical work is to make that combination "
            "visible, which usually means completing a square."
        ),
    )),
    Section("The shifted table", (
        Para(
            "Applying the theorem to each basic entry doubles the table at no "
            "cost. The three shifted rows below cover every term that appears "
            "in the solution of a constant-coefficient equation, because every "
            "such solution is built from t^n e^(at), e^(at) cos bt and "
            "e^(at) sin bt."
        ),
        Display(r"\mathcal{L}\left\{t^{n}e^{at}\right\} = \frac{n!}{(s-a)^{n+1}}",
                "5.1"),
        Display(r"\mathcal{L}\left\{e^{at}\cos bt\right\} = \frac{s-a}{(s-a)^{2}+b^{2}}"
                r"\qquad \mathcal{L}\left\{e^{at}\sin bt\right\} = "
                r"\frac{b}{(s-a)^{2}+b^{2}}", "5.2"),
        Para(
            "Notice in 5.2 that the numerator of the cosine row shifts too. The "
            "rule replaces every s in F(s) = s/(s² + b²), not only the ones in "
            "the denominator, so the numerator becomes s − a. Forgetting this is "
            "an easy slip, and it matters when inverting: a numerator has to be "
            "rewritten in terms of s − a before the cosine row can be used."
        ),
        Worked(
            "A forward transform",
            "Find the transforms of t³e^(2t) and e^(−3t)(2 cos 4t − sin 4t).",
            (
                Step("For the first, L{t³} = 3!/s⁴ = 6/s⁴; replace s by s − 2.",
                     r"\mathcal{L}\left\{t^{3}e^{2t}\right\} = \frac{6}{(s-2)^{4}}"),
                Step("For the second, a = −3, so s − a = s + 3. The cosine "
                     "contributes 2(s + 3) and the sine 4 over the same "
                     "denominator.",
                     r"\mathcal{L}\left\{e^{-3t}(2\cos 4t - \sin 4t)\right\} = "
                     r"\frac{2(s+3) - 4}{(s+3)^{2}+16} = \frac{2s+2}{s^{2}+6s+25}"),
            ),
            answer="6/(s-2)^4 and (2s+2)/(s²+6s+25)",
            answer_latex=r"\frac{6}{(s-2)^{4}},\qquad \frac{2s+2}{s^{2}+6s+25}",
        ),
        Para(
            "The last form, with the denominator multiplied out, is what an "
            "inversion problem will usually present. Recognising it means "
            "running the calculation backwards: complete the square to recover "
            "(s + 3)² + 16, then split the numerator into a multiple of s + 3 and "
            "a constant."
        ),
    )),
    Section("Inverting by completing the square", (
        Para(
            "When the denominator of a term is an irreducible quadratic "
            "s² + ps + q, with p² < 4q, complete the square: "
            "s² + ps + q = (s + p/2)² + (q − p²/4). The shift is a = −p/2 and the "
            "frequency is b = √(q − p²/4). Then rewrite the numerator as "
            "A(s − a) + Bb, and the term inverts to e^(at)(A cos bt + B sin bt)."
        ),
        Worked(
            "An inverse transform",
            "Find the inverse transform of (s + 3)/(s² + 2s + 5).",
            (
                Step("Complete the square: s² + 2s + 5 = (s + 1)² + 4, so "
                     "a = −1 and b = 2.",
                     r"\frac{s+3}{s^{2}+2s+5} = \frac{s+3}{(s+1)^{2}+4}"),
                Step("Write the numerator in terms of s + 1: s + 3 = (s + 1) + 2, "
                     "and the 2 is exactly b.",
                     r"= \frac{s+1}{(s+1)^{2}+4} + \frac{2}{(s+1)^{2}+4}"),
                Step("The first term is the shifted cosine row, the second the "
                     "shifted sine row."),
            ),
            answer="e^(−t)(cos 2t + sin 2t)",
            answer_latex=r"f(t) = e^{-t}\left(\cos 2t + \sin 2t\right)",
        ),
        Para(
            "The two numbers read off the completed square are the real and "
            "imaginary parts of the roots of s² + 2s + 5 = 0, namely −1 ± 2i. So "
            "the decay rate and the frequency of the answer are visible in the "
            "transform before any inversion has been done — a fact that the "
            "section on poles below makes systematic."
        ),
    )),
    Section("A damped oscillator by transform", (
        Worked(
            "Free damped motion",
            "Solve y'' + 2y' + 5y = 0 with y(0) = 1, y'(0) = 0.",
            (
                Step("Transform: (s²Y − s) + 2(sY − 1) + 5Y = 0, so "
                     "(s² + 2s + 5)Y = s + 2.",
                     r"Y = \frac{s+2}{s^{2}+2s+5} = \frac{s+2}{(s+1)^{2}+4}"),
                Step("Split the numerator: s + 2 = (s + 1) + 1 = (s + 1) + "
                     "(1/2)·2.",
                     r"Y = \frac{s+1}{(s+1)^{2}+4} + \frac{1}{2}\cdot"
                     r"\frac{2}{(s+1)^{2}+4}"),
                Step("Invert both shifted rows."),
            ),
            equation="y'' + 2*y' + 5*y = 0", conditions="y(0) = 1, y'(0) = 0",
            answer="exp(-t)*(cos(2*t) + sin(2*t)/2)",
            answer_latex=r"y(t) = e^{-t}\left(\cos 2t + \frac{1}{2}\sin 2t\right)",
        ),
        Para(
            "This is the underdamped spring of the vibrations unit, and the "
            "answer agrees with what the characteristic roots −1 ± 2i give "
            "directly. Written in amplitude–phase form it is "
            "(√5/2)e^(−t)cos(2t − δ), with amplitude √5/2 ≈ 1.118, so the "
            "solution stays between the two envelope curves ±(√5/2)e^(−t) and "
            "touches them once in each half period."
        ),
        Plot(
            "A damped oscillation and its envelope",
            "y = e^(−t)(cos 2t + ½ sin 2t), with the envelope ±(√5/2)e^(−t). "
            "The shift a = −1 in the transform is the decay rate of the "
            "envelope; the 2 left under the square is the frequency of the "
            "oscillation inside it.",
            (Curve("exp(-t)*(cos(2*t) + sin(2*t)/2)", "y(t)"),
             Curve("sqrt(5)/2*exp(-t)", "envelope"),
             Curve("-sqrt(5)/2*exp(-t)", "")),
            t=(0.0, 5.0), ylim=(-1.2, 1.2),
        ),
        Worked(
            "A second damped oscillator",
            "Solve y'' + 4y' + 13y = 0 with y(0) = 0, y'(0) = 6.",
            (
                Step("Transform: (s²Y − 6) + 4sY + 13Y = 0, since y(0) = 0 "
                     "removes the s term.",
                     r"Y = \frac{6}{s^{2}+4s+13} = \frac{6}{(s+2)^{2}+9}"),
                Step("The frequency is b = 3, so write 6 = 2·3 and use the "
                     "shifted sine row.",
                     r"Y = 2\cdot\frac{3}{(s+2)^{2}+9}"),
            ),
            equation="y'' + 4*y' + 13*y = 0", conditions="y(0) = 0, y'(0) = 6",
            answer="2*exp(-2*t)*sin(3*t)",
            answer_latex=r"y(t) = 2e^{-2t}\sin 3t",
        ),
    )),
    Section("Where the poles are", (
        Para(
            "The values of s where a transform becomes infinite are its poles. "
            "For a rational Y(s) they are the roots of the denominator, and the "
            "shifted table says exactly how each pole shows up in y(t). A real "
            "pole at s = a gives e^(at). A pair of complex poles a ± bi gives "
            "e^(at) times an oscillation of frequency b. A pole of multiplicity "
            "m brings the powers t, t², …, t^(m−1) with it."
        ),
        Box(
            "theorem", "Poles and behaviour",
            "Each pole of Y(s) contributes a term to y(t) whose growth or decay "
            "is set by the real part of the pole and whose frequency is set by "
            "its imaginary part. The solution decays to zero exactly when every "
            "pole lies in the left half-plane Re s < 0.",
            r"s = a \pm bi \;\Longrightarrow\; e^{at}\cos bt,\; e^{at}\sin bt",
        ),
        Figure("poles",
               "Pole positions in the s-plane and the time functions they "
               "produce: moving a pole left speeds up the decay, moving it away "
               "from the real axis raises the frequency, and a pole in the "
               "right half-plane means growth."),
        Para(
            "The first shifting theorem is precisely the statement that moving "
            "every pole a units to the right multiplies the time function by "
            "e^(at). The picture explains why damping appears in a transform as "
            "a shift: damping moves the poles of an undamped oscillator, which "
            "sit on the imaginary axis at ±bi, into the left half-plane."
        ),
    )),
    Section("Repeated linear factors", (
        Para(
            "When a factor s − a appears in the denominator k times, the "
            "partial-fraction expansion needs a term for every power up to k. "
            "The reason is counting, not convention: a denominator of degree n "
            "leaves n coefficients to determine, and with only one term per "
            "distinct factor there would be too few unknowns to match an "
            "arbitrary numerator."
        ),
        Box(
            "theorem", "Repeated linear factors",
            "If (s − a)^k divides Q(s) exactly, the expansion of P(s)/Q(s) "
            "contains the k terms below, and by 5.1 they invert to "
            "e^(at) times a polynomial of degree k − 1.",
            r"\frac{A_{1}}{s-a} + \frac{A_{2}}{(s-a)^{2}} + \cdots + "
            r"\frac{A_{k}}{(s-a)^{k}} \;\to\; e^{at}\left(A_{1} + A_{2}t + "
            r"\cdots + \frac{A_{k}t^{k-1}}{(k-1)!}\right)",
        ),
        Worked(
            "A repeated root, from initial values",
            "Solve y'' − 4y' + 4y = 0 with y(0) = 1, y'(0) = 3.",
            (
                Step("Transform: (s²Y − s − 3) − 4(sY − 1) + 4Y = 0, so "
                     "(s − 2)²Y = s − 1.",
                     r"Y = \frac{s-1}{(s-2)^{2}}"),
                Step("Write the numerator in powers of s − 2: s − 1 = (s − 2) + 1.",
                     r"Y = \frac{1}{s-2} + \frac{1}{(s-2)^{2}}"),
                Step("Invert with 5.1: 1/(s − 2)² is the n = 1 row shifted by 2."),
            ),
            equation="y'' - 4*y' + 4*y = 0", conditions="y(0) = 1, y'(0) = 3",
            answer="exp(2*t)*(1 + t)",
            answer_latex=r"y(t) = (1 + t)e^{2t}",
        ),
        Para(
            "Rewriting the numerator in powers of s − a, as in the second step, "
            "is the quickest route whenever the denominator is a single "
            "repeated factor. It is the same move as completing the square, one "
            "degree lower, and the factor of t in the answer is the familiar "
            "t·e^(rt) of a repeated characteristic root, here produced "
            "automatically by the table rather than by a rule to remember."
        ),
    )),
    Section("Resonance with an exponential", (
        Para(
            "A repeated factor also appears when the forcing shares an "
            "exponent with the equation. The forcing then contributes a pole "
            "that the equation's own denominator already has, and the two "
            "combine into a double pole. This is resonance seen from the s "
            "side, and the partial fractions deal with it without any "
            "modification rule."
        ),
        Worked(
            "A forcing term with a shared pole",
            "Solve y'' + 3y' + 2y = e^(−t) with y(0) = 0, y'(0) = 0.",
            (
                Step("The equation's denominator is s² + 3s + 2 = (s + 1)(s + 2), "
                     "and the forcing transforms to 1/(s + 1).",
                     r"Y = \frac{1}{(s+1)^{2}(s+2)}"),
                Step("Set up three terms, two for the double factor.",
                     r"\frac{1}{(s+1)^{2}(s+2)} = \frac{A}{s+1} + \frac{B}{(s+1)^{2}} "
                     r"+ \frac{C}{s+2}"),
                Step("Cover-up works for the highest power and the simple "
                     "factor: B = 1/(−1 + 2) = 1 and C = 1/(−2 + 1)² = 1. For A, "
                     "compare s² coefficients after clearing denominators: "
                     "A + C = 0, so A = −1.",
                     r"Y = -\frac{1}{s+1} + \frac{1}{(s+1)^{2}} + \frac{1}{s+2}"),
            ),
            equation="y'' + 3*y' + 2*y = exp(-t)", conditions="y(0) = 0, y'(0) = 0",
            answer="-exp(-t) + t*exp(-t) + exp(-2*t)",
            answer_latex=r"y(t) = (t - 1)e^{-t} + e^{-2t}",
        ),
        Plot(
            "The response and its three pieces",
            "y = (t − 1)e^(−t) + e^(−2t) starts from rest. The term t·e^(−t), "
            "from the double pole at −1, dominates for large t: it is what "
            "resonance looks like in a system that also decays.",
            (Curve("-exp(-t) + t*exp(-t) + exp(-2*t)", "y(t)"),
             Curve("t*exp(-t)", "t e^(-t)"),
             Curve("exp(-2*t) - exp(-t)", "the other two")),
            t=(0.0, 8.0),
        ),
        Para(
            "The coefficient A of a repeated factor is the one that cover-up "
            "cannot give directly. Besides comparing coefficients, it can be "
            "found by differentiation: multiply Y by (s + 1)², differentiate "
            "once, and evaluate at s = −1. Here (s + 1)²Y = 1/(s + 2), whose "
            "derivative −1/(s + 2)² equals −1 at s = −1, agreeing with the "
            "value found above. In general the coefficient of 1/(s − a)^(k−j) "
            "is the j-th derivative of (s − a)^k Y at s = a, divided by j!."
        ),
    )),
    Section("Linear and quadratic factors together", (
        Para(
            "A constant forcing term puts a factor s in the denominator, and if "
            "the equation is underdamped the rest is an irreducible quadratic. "
            "The expansion then needs one constant over s and one linear "
            "numerator over the quadratic. Cover-up gives the first coefficient; "
            "the other two follow by comparing coefficients."
        ),
        Worked(
            "A step response",
            "Solve y'' + 2y' + 2y = 2 with y(0) = 0, y'(0) = 0.",
            (
                Step("From rest, (s² + 2s + 2)Y = 2/s.",
                     r"Y = \frac{2}{s\left(s^{2}+2s+2\right)}"),
                Step("Cover up s: A = 2/2 = 1. Then 2 = (s² + 2s + 2) + s(Bs + C) "
                     "forces B = −1 and C = −2.",
                     r"Y = \frac{1}{s} - \frac{s+2}{s^{2}+2s+2}"),
                Step("Complete the square, (s + 1)² + 1, and split s + 2 = "
                     "(s + 1) + 1.",
                     r"Y = \frac{1}{s} - \frac{s+1}{(s+1)^{2}+1} - "
                     r"\frac{1}{(s+1)^{2}+1}"),
            ),
            equation="y'' + 2*y' + 2*y = 2", conditions="y(0) = 0, y'(0) = 0",
            answer="1 - exp(-t)*(cos(t) + sin(t))",
            answer_latex=r"y(t) = 1 - e^{-t}\left(\cos t + \sin t\right)",
        ),
        Para(
            "The pole at s = 0 gives the steady value 1 that the constant force "
            "settles the system to; the complex pair −1 ± i gives the decaying "
            "oscillation about it. Differentiating shows y' = 2e^(−t) sin t, "
            "which first vanishes again at t = π, where the response reaches "
            "its peak 1 + e^(−π) ≈ 1.043 — an overshoot of about 4.3 percent "
            "before it settles."
        ),
        Plot(
            "Step response of an underdamped system",
            "y = 1 − e^(−t)(cos t + sin t) rises from rest, overshoots the "
            "steady value 1 by about 4.3 percent at t = π, and settles. The "
            "steady value comes from the pole at 0, the overshoot from the "
            "complex pair.",
            (Curve("1 - exp(-t)*(cos(t) + sin(t))", "y(t)"),
             Curve("1 + 0*t", "steady value")),
            t=(0.0, 8.0), ylim=(0.0, 1.2),
        ),
    )),
    Section("Shifted forcing at first order", (
        Para(
            "The shifting theorem is just as useful on the forcing side. A "
            "forcing term like e^(−t) cos t transforms by the shifted cosine "
            "row, and if the equation happens to share the shift the algebra "
            "can collapse dramatically."
        ),
        Worked(
            "A cancellation",
            "Solve y' + y = e^(−t) cos t with y(0) = 0.",
            (
                Step("Transform: (s + 1)Y = (s + 1)/((s + 1)² + 1).",
                     r"(s+1)Y = \frac{s+1}{(s+1)^{2}+1}"),
                Step("The factor s + 1 cancels, leaving the shifted sine row "
                     "with b = 1.",
                     r"Y = \frac{1}{(s+1)^{2}+1}"),
            ),
            equation="y' + y = exp(-t)*cos(t)", conditions="y(0) = 0",
            answer="exp(-t)*sin(t)",
            answer_latex=r"y(t) = e^{-t}\sin t",
        ),
        Para(
            "The integrating factor gives the same answer, since multiplying by "
            "e^t leaves (e^t y)' = cos t. The two calculations are closely "
            "related: the integrating factor e^t in time and the shift by one "
            "unit in s are the same operation seen in the two domains."
        ),
    )),
    Section("Complex roots, and why the shift appears", (
        Para(
            "There is another way to see where the shifted sine and cosine "
            "come from. Over the complex numbers every quadratic factors, and "
            "the partial fractions of a quadratic term are a conjugate pair of "
            "simple complex fractions. Each inverts to a complex exponential, "
            "and adding a conjugate pair gives a real function."
        ),
        Display(r"\frac{1}{s-(a+bi)} + \frac{1}{s-(a-bi)} = \frac{2(s-a)}{(s-a)^{2}+b^{2}}"
                r"\;\to\; e^{(a+bi)t} + e^{(a-bi)t} = 2e^{at}\cos bt", "5.3"),
        Para(
            "The factor e^(at) in the answer comes from the real part of the "
            "roots, and in the transform that real part is the shift. So the "
            "first shifting theorem and Euler's formula say the same thing: "
            "completing the square is a real-arithmetic way of locating the "
            "complex roots, and it avoids complex numbers altogether. Some "
            "texts prefer the complex route because every factor is then "
            "linear and cover-up always applies; for hand work with a single "
            "quadratic, completing the square is usually shorter."
        ),
    )),
    Section("Heaviside's formula for distinct roots", (
        Para(
            "When the denominator Q(s) has only simple roots r₁, …, rₙ, the "
            "cover-up coefficients have a compact closed form. Covering up the "
            "factor s − rᵢ and evaluating at rᵢ is the same as dividing P(rᵢ) "
            "by the derivative Q'(rᵢ), because Q'(rᵢ) is the product of the "
            "other factors at that point."
        ),
        Box(
            "theorem", "Heaviside expansion formula",
            "If P and Q are polynomials, the degree of P is less than that of "
            "Q, and Q has distinct roots r₁, …, rₙ, then the inverse transform "
            "of P/Q is a sum of exponentials with coefficients P(rᵢ)/Q'(rᵢ).",
            r"\mathcal{L}^{-1}\left\{\frac{P(s)}{Q(s)}\right\} = "
            r"\sum_{i=1}^{n}\frac{P(r_{i})}{Q'(r_{i})}e^{r_{i}t}",
        ),
        Para(
            "For Y = 4/(s(s − 1)(s − 2)) from the last lesson, Q(s) = s³ − 3s² + "
            "2s and Q'(s) = 3s² − 6s + 2. At the roots 0, 1 and 2, Q' takes the "
            "values 2, −1 and 2, so the coefficients are 2, −4 and 2 — the same "
            "numbers cover-up gave. The formula is most useful when Q is given "
            "multiplied out and factoring it is inconvenient, and it works for "
            "complex roots too, where it produces the conjugate pairs of 5.3."
        ),
    )),
    Section("Not to be confused: the second shifting theorem", (
        Box(
            "warning", "Two theorems that look alike",
            "The first theorem shifts in s and multiplies by an exponential in "
            "t. The second shifts in t — delays a function by a — and multiplies "
            "the transform by an exponential in s. It needs the unit step u, "
            "and it belongs to the step-forcing lesson.",
            r"\mathcal{L}\left\{e^{at}f(t)\right\} = F(s-a) \quad\text{versus}\quad "
            r"\mathcal{L}\left\{u(t-a)f(t-a)\right\} = e^{-as}F(s)",
        ),
        Para(
            "One way to keep them apart is to remember which variable is "
            "shifted and ask where the exponential goes: a shift in one domain "
            "always produces an exponential factor in the other. An e^(−as) in "
            "a transform therefore means a delay, and must never be treated as "
            "part of a partial-fraction expansion; a shifted s inside a "
            "denominator means an exponential factor in time."
        ),
    )),
    Section("Common errors", (
        Para(
            "Shifting only the denominator is the classic slip: L{e^(at) cos bt} "
            "has s − a on top, not s. The sign of the shift is next: e^(−2t) "
            "replaces s by s + 2, not s − 2 — the rule is F(s − a) with a = −2. "
            "When inverting, a numerator must be rewritten in terms of the "
            "shifted variable before the table is used; (s + 3)/((s + 1)² + 4) "
            "is not a shifted cosine until the 3 has been split into 1 + 2."
        ),
        Para(
            "In partial fractions, the usual error is to give a repeated factor "
            "only its highest power, which leaves too few unknowns and an "
            "inconsistent system. For an irreducible quadratic the numerator "
            "must be linear, Bs + C, not a constant. And before expanding at all, "
            "check that the fraction is proper; if the numerator's degree is "
            "not lower, something has gone wrong earlier, since the transform "
            "of a solution always tends to zero as s grows."
        ),
    )),
    Section("Summary", (
        Para(
            "Multiplying by e^(at) in time replaces s by s − a in the transform. "
            "That single rule turns the basic table into the shifted rows 5.1 "
            "and 5.2, which cover every term of a constant-coefficient "
            "solution. To invert, factor the denominator; split into partial "
            "fractions with one term per power of each repeated factor and a "
            "linear numerator over each irreducible quadratic; complete the "
            "square on the quadratics and rewrite their numerators in the "
            "shifted variable. The poles of Y(s) predict the behaviour: real "
            "part for growth or decay, imaginary part for frequency, "
            "multiplicity for powers of t."
        ),
    )),
)


CONVOLUTION = (
    Section("When Y(s) is a product", (
        Para(
            "Every example so far ended with a Y(s) that partial fractions could "
            "split into rows of the table. That relied on two things: the "
            "forcing had a transform on the table, and the product of that "
            "transform with 1/P(s), where P is the characteristic polynomial, "
            "was a rational function. Neither is guaranteed. A forcing such as "
            "1/(1 + t) has no elementary transform at all, and a forcing given "
            "as measured data has no formula to transform."
        ),
        Para(
            "There is also a structural point that the partial-fraction "
            "calculations hide. For a system starting at rest, the transform of "
            "the answer is always a product, Y(s) = F(s)/P(s): one factor belongs "
            "to the forcing and the other to the system alone. It would be "
            "useful to know what a product of transforms means back in time, "
            "because then the system's contribution could be worked out once "
            "and reused for every forcing."
        ),
        Para(
            "The obvious guess is that a product of transforms is the transform "
            "of the product of the functions. It is wrong, and it is worth "
            "seeing how badly. With f = g = t, the product fg = t² has transform "
            "2/s³, while F(s)G(s) = (1/s²)(1/s²) = 1/s⁴. The correct answer is a "
            "new operation on functions, the convolution, and it is the subject "
            "of this chapter."
        ),
        Display(r"\mathcal{L}\{f g\} \neq F(s)\,G(s)", "5.4"),
    )),
    Section("The convolution of two functions", (
        Box(
            "definition", "Convolution",
            "For functions f and g that are piecewise continuous on t ≥ 0, the "
            "convolution f * g is the function of t defined by the integral "
            "below. One function is evaluated at the earlier time τ and the "
            "other at the remaining time t − τ, and the two arguments always add "
            "up to the current time t.",
            r"(f * g)(t) = \int_{0}^{t} f(\tau)\,g(t - \tau)\,d\tau",
        ),
        Para(
            "The simplest examples show that convolution is a genuinely "
            "different operation from multiplication. Convolving with the "
            "constant 1 integrates: (1 * g)(t) = ∫₀ᵗ g(t − τ) dτ = ∫₀ᵗ g(u) du. So "
            "1 * 1 = t, 1 * t = t²/2, and 1 * cos t = sin t. In particular 1 is "
            "not an identity for convolution — convolving with 1 changes a "
            "function into its running integral."
        ),
        Worked(
            "Convolving two exponentials",
            "Compute e^t * e^(2t).",
            (
                Step("Put f(τ) = e^τ and g(t − τ) = e^(2(t − τ)), and take the "
                     "factor e^(2t), which does not depend on τ, outside.",
                     r"e^{t} * e^{2t} = \int_{0}^{t} e^{\tau}e^{2(t-\tau)}\,d\tau = "
                     r"e^{2t}\int_{0}^{t} e^{-\tau}\,d\tau"),
                Step("Integrate: the inner integral is 1 − e^(−t).",
                     r"= e^{2t}\left(1 - e^{-t}\right) = e^{2t} - e^{t}"),
                Step("Check against partial fractions: 1/((s − 1)(s − 2)) = "
                     "1/(s − 2) − 1/(s − 1), which inverts to the same function.",
                     r"\frac{1}{s-1}\cdot\frac{1}{s-2} = \frac{1}{s-2} - \frac{1}{s-1}"),
            ),
            answer="e^(2t) − e^t",
            answer_latex=r"e^{t} * e^{2t} = e^{2t} - e^{t}",
        ),
        Para(
            "The check in the last step is not a coincidence: it is the "
            "convolution theorem, which is stated and proved next."
        ),
    )),
    Section("The convolution theorem", (
        Box(
            "theorem", "Convolution theorem",
            "If f and g are piecewise continuous and of exponential order, then "
            "the transform of their convolution is the product of their "
            "transforms, for all s large enough that both transforms exist.",
            r"\mathcal{L}\{f * g\} = F(s)\,G(s)",
        ),
        Box(
            "proof", "Proof",
            "Write each transform as its own integral, using different "
            "variables of integration, and multiply. The product is a double "
            "integral over the quarter-plane τ ≥ 0, σ ≥ 0, and the exponent "
            "depends only on τ + σ. Substitute t = τ + σ for σ: for fixed τ, t "
            "runs from τ to ∞. The region τ ≥ 0, t ≥ τ is the wedge "
            "0 ≤ τ ≤ t, and reversing the order of integration over it gives "
            "an outer integral in t whose inner integral is exactly (f * g)(t). "
            "Exponential order justifies the reversal.",
            r"F(s)G(s) = \int_{0}^{\infty}\!\!\int_{0}^{\infty}e^{-s(\tau+\sigma)}"
            r"f(\tau)g(\sigma)\,d\sigma\,d\tau = \int_{0}^{\infty}e^{-st}"
            r"\left(\int_{0}^{t}f(\tau)g(t-\tau)\,d\tau\right)dt",
        ),
        Para(
            "Read the theorem in both directions. Forwards, it transforms a "
            "convolution without evaluating it. Backwards — the direction that "
            "matters for differential equations — it inverts a product of two "
            "recognisable transforms without partial fractions: the inverse of "
            "F(s)G(s) is f * g, whatever F and G are."
        ),
        Figure("convolution",
               "The convolution integral pictured: a pulse f is held still "
               "while a decaying exponential g is reversed and slid across it. "
               "The area of their overlap at each moment is the value of f * g "
               "there, and the right pane plots that area against t."),
    )),
    Section("Properties", (
        Para(
            "Because transforms are unique, every algebraic property of the "
            "product F(s)G(s) is inherited by the convolution. Products commute, "
            "associate and distribute over sums, so convolution does too. The "
            "commutative law can also be seen directly from the integral by "
            "substituting u = t − τ."
        ),
        Display(r"f * g = g * f, \qquad f * (g * h) = (f * g) * h, \qquad "
                r"f * (g + h) = f * g + f * h", "5.5"),
        Para(
            "Commutativity is useful in practice because it lets you choose "
            "which function to shift. Putting t − τ into the simpler function "
            "usually makes the integral easier. But the choice must be made "
            "consistently: f(τ)g(t − τ) and g(τ)f(t − τ) are both correct, "
            "while f(t − τ)g(t − τ) or f(τ)g(τ) are not convolutions at all."
        ),
        Para(
            "Convolving with 1 is integration, so the theorem gives at once the "
            "transform of a running integral. Dividing a transform by s "
            "integrates the function from 0 to t — the counterpart of the rule "
            "that multiplying by s differentiates it."
        ),
        Display(r"\mathcal{L}\left\{\int_{0}^{t} f(u)\,du\right\} = \frac{F(s)}{s}",
                "5.6"),
        Worked(
            "Dividing by s",
            "Find the inverse transform of 1/(s(s² + 4)).",
            (
                Step("1/(s² + 4) is the transform of (1/2) sin 2t, and the extra "
                     "factor 1/s integrates it from 0 to t, by 5.6.",
                     r"\mathcal{L}^{-1}\left\{\frac{1}{s(s^{2}+4)}\right\} = "
                     r"\int_{0}^{t}\frac{1}{2}\sin 2u\,du"),
                Step("Integrate.",
                     r"= \frac{1}{4}\left(1 - \cos 2t\right)"),
            ),
            answer="(1 − cos 2t)/4",
            answer_latex=r"\frac{1}{4}\left(1 - \cos 2t\right)",
        ),
    )),
    Section("Inverting products", (
        Para(
            "The theorem gives an alternative to partial fractions whenever "
            "Y(s) is a product of two table entries. Sometimes it is quicker, "
            "and sometimes it is the only practical route — a repeated "
            "quadratic factor such as 1/(s² + 1)² is tedious by partial "
            "fractions but straightforward by convolution."
        ),
        Worked(
            "A product of two table entries",
            "Find the inverse transform of 1/(s²(s² + 1)).",
            (
                Step("Write the transform as (1/s²)·(1/(s² + 1)), the transforms "
                     "of t and sin t. Put the shift into t, the simpler function.",
                     r"\mathcal{L}^{-1} = \int_{0}^{t} (t - \tau)\sin\tau\,d\tau"),
                Step("Integrate by parts, or split the integrand: "
                     "t∫sin τ dτ − ∫τ sin τ dτ = t(1 − cos t) − (sin t − t cos t).",
                     r"= t - \sin t"),
                Step("Check by partial fractions in s²: 1/(s²(s² + 1)) = "
                     "1/s² − 1/(s² + 1), which inverts to t − sin t."),
            ),
            answer="t − sin t",
            answer_latex=r"t - \sin t",
        ),
        Worked(
            "A repeated quadratic",
            "Find the inverse transform of 1/(s² + 1)².",
            (
                Step("This is (1/(s² + 1))², so the answer is sin t * sin t.",
                     r"\sin t * \sin t = \int_{0}^{t}\sin\tau\,\sin(t-\tau)\,d\tau"),
                Step("Use sin A sin B = (1/2)(cos(A − B) − cos(A + B)); here "
                     "A + B = t is constant in τ.",
                     r"= \frac{1}{2}\int_{0}^{t}\left(\cos(2\tau - t) - \cos t\right)d\tau"),
                Step("The first term integrates to (1/2) sin t, the second to "
                     "−(t/2) cos t.",
                     r"= \frac{1}{2}\left(\sin t - t\cos t\right)"),
            ),
            answer="(sin t − t cos t)/2",
            answer_latex=r"\frac{1}{2}\left(\sin t - t\cos t\right)",
        ),
        Para(
            "The second result has a factor t cos t that grows without bound, "
            "and that is exactly the resonant response of the vibrations unit: "
            "1/(s² + 1)² is what a spring with natural frequency 1 produces when "
            "it is forced at frequency 1."
        ),
    )),
    Section("The transfer function and the impulse response", (
        Para(
            "Now apply the theorem to a differential equation. Take a linear "
            "equation with constant coefficients, ay'' + by' + cy = f(t), and "
            "start it at rest, y(0) = y'(0) = 0. The transform is "
            "(as² + bs + c)Y = F, so Y is a product of the forcing's transform "
            "and a function of s that depends only on the equation."
        ),
        Box(
            "definition", "Transfer function and impulse response",
            "The transfer function of the equation is W(s) = 1/(as² + bs + c). "
            "Its inverse transform w(t) is the impulse response (also called "
            "the weight function) of the system — the name will be justified in "
            "the impulses lesson, where w turns out to be the response to a "
            "single sharp blow.",
            r"W(s) = \frac{1}{as^{2}+bs+c}, \qquad w(t) = \mathcal{L}^{-1}\{W(s)\}",
        ),
        Box(
            "theorem", "Duhamel's principle",
            "The solution of ay'' + by' + cy = f(t) with y(0) = y'(0) = 0 is the "
            "convolution of the impulse response with the forcing. It holds for "
            "every piecewise continuous forcing of exponential order, whether or "
            "not the forcing has a transform in closed form.",
            r"y(t) = (w * f)(t) = \int_{0}^{t} w(t - \tau)\,f(\tau)\,d\tau",
        ),
        Para(
            "The integral has a physical reading. At time τ the forcing delivers "
            "a small input f(τ)dτ; by time t that input has been evolving for "
            "t − τ units and contributes w(t − τ)f(τ)dτ to the response. The "
            "output now is the sum of everything the forcing did earlier, each "
            "part weighted by how long ago it happened. The system is described "
            "completely by one function w, found once."
        ),
    )),
    Section("First order: the integrating factor, rediscovered", (
        Para(
            "The simplest case is worth doing because its answer is already "
            "familiar. For y' + ky = f(t) with y(0) = 0, the transform gives "
            "(s + k)Y = F, so the transfer function is 1/(s + k) and the impulse "
            "response is e^(−kt). Duhamel's principle then says the solution is "
            "the integral below — which is exactly the formula the integrating "
            "factor e^(kt) produced in the first unit, written in a different "
            "order."
        ),
        Display(r"y(t) = \int_{0}^{t} e^{-k(t-\tau)}\,f(\tau)\,d\tau", "5.7"),
        Para(
            "The weight e^(−k(t − τ)) makes the idea of memory precise. An input "
            "delivered at time τ still counts at time t, but discounted by the "
            "factor e^(−k(t − τ)), so the system forgets its past at the rate k. "
            "A large k means a short memory and a response that follows the "
            "forcing closely; a small k means a long memory and a response that "
            "averages the forcing over a long stretch of its history. The "
            "undamped oscillator of the next section, whose impulse response sin t "
            "never decays, never forgets anything at all: an input delivered long ago "
            "still rings through the response with its full original strength."
        ),
        Worked(
            "A ramp through a first-order system",
            "Solve y' + y = t with y(0) = 0 using 5.7.",
            (
                Step("With k = 1 and f(τ) = τ, the convolution is the integral "
                     "below; take the factor e^(−t) outside.",
                     r"y(t) = \int_{0}^{t} e^{-(t-\tau)}\,\tau\,d\tau = "
                     r"e^{-t}\int_{0}^{t}\tau e^{\tau}\,d\tau"),
                Step("Integrate by parts: ∫₀ᵗ τe^τ dτ = (t − 1)e^t + 1.",
                     r"y(t) = e^{-t}\left((t-1)e^{t} + 1\right)"),
                Step("Simplify. The response lags the ramp by exactly one unit "
                     "of time, the memory length 1/k, once the transient e^(−t) "
                     "has died away."),
            ),
            equation="y' + y = t", conditions="y(0) = 0",
            answer="t - 1 + exp(-t)",
            answer_latex=r"y(t) = t - 1 + e^{-t}",
        ),
    )),
    Section("Solving with an arbitrary forcing", (
        Para(
            "For the undamped oscillator y'' + y = f(t), the transfer function is "
            "1/(s² + 1) and the impulse response is sin t. Every forced motion "
            "from rest is therefore given by one formula."
        ),
        Display(r"y'' + y = f(t),\; y(0)=y'(0)=0 \;\Longrightarrow\; "
                r"y(t) = \int_{0}^{t}\sin(t-\tau)\,f(\tau)\,d\tau", "5.8"),
        Worked(
            "A ramp forcing",
            "Solve y'' + y = t with y(0) = 0, y'(0) = 0 using 5.8.",
            (
                Step("Substitute f(τ) = τ. By commutativity this is the same "
                     "integral as in the product example above.",
                     r"y(t) = \int_{0}^{t}\tau\,\sin(t-\tau)\,d\tau"),
                Step("Evaluate: it equals t − sin t.",
                     r"y(t) = t - \sin t"),
            ),
            equation="y'' + y = t", conditions="y(0) = 0, y'(0) = 0",
            answer="t - sin(t)",
            answer_latex=r"y(t) = t - \sin t",
        ),
        Worked(
            "Forcing at the natural frequency",
            "Solve y'' + 4y = cos 2t with y(0) = 0, y'(0) = 0.",
            (
                Step("The transfer function is 1/(s² + 4), so the impulse "
                     "response is (1/2) sin 2t.",
                     r"y(t) = \frac{1}{2}\int_{0}^{t}\sin 2(t-\tau)\,\cos 2\tau\,d\tau"),
                Step("Use sin A cos B = (1/2)(sin(A + B) + sin(A − B)): the first "
                     "term is sin 2t, constant in τ, and the second integrates to "
                     "zero over [0, t].",
                     r"= \frac{1}{4}\int_{0}^{t}\left(\sin 2t + \sin(2t - 4\tau)"
                     r"\right)d\tau = \frac{t}{4}\sin 2t"),
            ),
            equation="y'' + 4*y = cos(2*t)", conditions="y(0) = 0, y'(0) = 0",
            answer="t*sin(2*t)/4",
            answer_latex=r"y(t) = \frac{t}{4}\sin 2t",
        ),
        Plot(
            "Resonance from a convolution",
            "y = (t/4) sin 2t between the lines ±t/4. Every past moment of the "
            "forcing cos 2τ arrives in phase with the system's own oscillation, "
            "so the contributions add rather than cancel and the amplitude grows "
            "linearly.",
            (Curve("t*sin(2*t)/4", "y(t)"), Curve("t/4", "±t/4"),
             Curve("-t/4", "")),
            t=(0.0, 20.0),
        ),
    )),
    Section("Impulse response and step response", (
        Para(
            "The response to a constant forcing of size 1, starting from rest, is "
            "called the step response. By Duhamel's principle it is w * 1, the "
            "running integral of the impulse response; equivalently, the impulse "
            "response is the derivative of the step response. Knowing either "
            "one determines the system."
        ),
        Worked(
            "An underdamped system",
            "Find the step response of y'' + 2y' + 2y = f(t) and check that its "
            "derivative is the impulse response.",
            (
                Step("W(s) = 1/((s + 1)² + 1), so the impulse response is "
                     "w(t) = e^(−t) sin t by the first shifting theorem.",
                     r"w(t) = e^{-t}\sin t"),
                Step("The step response has transform W(s)/s. The shifting "
                     "chapter found this for a forcing of 2; halve it.",
                     r"y(t) = \frac{1}{2}\left(1 - e^{-t}\left(\cos t + \sin t\right)\right)"),
                Step("Differentiate: the cosine terms cancel and y' = e^(−t) sin t, "
                     "which is w, as promised."),
            ),
            equation="y'' + 2*y' + 2*y = 1", conditions="y(0) = 0, y'(0) = 0",
            answer="(1 - exp(-t)*(cos(t) + sin(t)))/2",
            answer_latex=r"y(t) = \frac{1}{2}\left(1 - e^{-t}\left(\cos t + "
                         r"\sin t\right)\right)",
        ),
        Plot(
            "Impulse response and step response",
            "The impulse response w = e^(−t) sin t and the step response, its "
            "running integral. The step response rises fastest where w is "
            "largest and levels off at 1/2 = W(0) as w dies away.",
            (Curve("exp(-t)*sin(t)", "impulse response w(t)"),
             Curve("(1 - exp(-t)*(cos(t) + sin(t)))/2", "step response")),
            t=(0.0, 8.0),
        ),
    )),
    Section("Nonzero initial values", (
        Para(
            "When the system does not start at rest, the transformed equation "
            "has extra terms from the initial values, and Y splits into two "
            "parts: one from the initial values alone and one from the forcing "
            "alone. The first is the free response, which the table inverts as "
            "usual; the second is still w * f."
        ),
        Display(r"y(t) = y_{h}(t) + \int_{0}^{t} w(t-\tau)\,f(\tau)\,d\tau", "5.9"),
        Worked(
            "Starting displaced",
            "Solve y'' + y = t with y(0) = 1, y'(0) = 0.",
            (
                Step("The free response with y(0) = 1, y'(0) = 0 is cos t.",
                     r"y_{h}(t) = \cos t"),
                Step("The forced part from rest was found above: t − sin t. Add.",
                     r"y(t) = \cos t + t - \sin t"),
            ),
            equation="y'' + y = t", conditions="y(0) = 1, y'(0) = 0",
            answer="cos(t) + t - sin(t)",
            answer_latex=r"y(t) = \cos t + t - \sin t",
        ),
        Para(
            "This split — free response plus a zero-state response — is how "
            "engineers usually describe a linear system. It is the same "
            "decomposition as complementary function plus particular solution, "
            "but with a specific choice of particular solution: the one that "
            "starts at rest."
        ),
    )),
    Section("When the integral will not simplify", (
        Para(
            "Duhamel's principle gives an answer even when no closed form "
            "exists. For y'' + y = 1/(1 + t) from rest, 5.8 gives the solution "
            "below, and that integral is the answer. It can be evaluated "
            "numerically to any accuracy, differentiated under the integral "
            "sign, and bounded: since |sin| ≤ 1, |y(t)| ≤ ln(1 + t) for all t."
        ),
        Display(r"y(t) = \int_{0}^{t}\frac{\sin(t-\tau)}{1+\tau}\,d\tau", "5.10"),
        Para(
            "This particular integral can in fact be written with the special "
            "functions Si and Ci, the sine and cosine integrals, which is what "
            "the Laplace screen reports for the lesson's first example. But the "
            "special functions add nothing that 5.10 does not already say; they "
            "are names for integrals of exactly this kind. An unevaluated "
            "convolution is a finished answer, not an unfinished one."
        ),
        Para(
            "The same idea handles forcing known only as data. If f has been "
            "measured at a sequence of times, the convolution integral can be "
            "approximated by a sum over those times, and the response computed "
            "without ever writing down a formula for f. This is how linear "
            "systems are simulated in signal processing and control, where the "
            "impulse response is often measured directly by striking the system "
            "once and recording what it does."
        ),
    )),
    Section("Integral equations", (
        Para(
            "An equation in which the unknown function appears inside a "
            "convolution is called a Volterra integral equation. The convolution "
            "theorem turns it into algebra in exactly the way the derivative "
            "rule does for differential equations."
        ),
        Worked(
            "A Volterra equation",
            "Solve y(t) = t + ∫₀ᵗ (t − τ) y(τ) dτ.",
            (
                Step("The integral is t * y, so transforming gives an algebraic "
                     "equation for Y.",
                     r"Y = \frac{1}{s^{2}} + \frac{1}{s^{2}}Y"),
                Step("Solve: Y(1 − 1/s²) = 1/s², so Y = 1/(s² − 1).",
                     r"Y = \frac{1}{s^{2}-1}"),
                Step("Invert: 1/(s² − 1) = (1/2)(1/(s − 1) − 1/(s + 1)), the "
                     "transform of sinh t. Substituting back confirms it: "
                     "∫₀ᵗ (t − τ) sinh τ dτ = sinh t − t."),
            ),
            answer="sinh t",
            answer_latex=r"y(t) = \sinh t",
        ),
        Para(
            "Such equations arise when the rate of change of a quantity depends "
            "on its whole history rather than its present value — materials "
            "with memory, populations with delayed effects, and the renewal "
            "equations of probability."
        ),
    )),
    Section("Common errors", (
        Para(
            "The first error is the one this chapter began with: treating "
            "L{fg} as FG. The second is misplacing the shift — both functions "
            "evaluated at τ, or both at t − τ. The third is forgetting that the "
            "limits are 0 and t, not 0 and ∞: the transform only ever describes "
            "t ≥ 0, and both functions are taken to be zero before time 0, which "
            "is why the integral stops at t."
        ),
        Para(
            "Finally, 1 is not the identity for convolution: 1 * f is the running "
            "integral of f, not f. The function that does act as an identity is "
            "not a function at all — it is the delta impulse of the impulses "
            "lesson, whose transform is 1."
        ),
    )),
    Section("Summary", (
        Para(
            "The convolution f * g = ∫₀ᵗ f(τ)g(t − τ) dτ is the operation whose "
            "transform is the product F(s)G(s). It is commutative, associative "
            "and distributive, and convolving with 1 integrates. For a linear "
            "system at rest, Y = W(s)F(s), so the solution is w * f, where the "
            "impulse response w is the inverse of the transfer function "
            "W = 1/P(s). That formula works for any forcing, including ones "
            "with no closed-form transform, and an unevaluated convolution "
            "integral is a complete answer."
        ),
    )),
)


STEPFORCING = (
    Section("Forcing that changes its formula", (
        Para(
            "Real forcing is often switched. A voltage is applied at t = 2 and "
            "removed at t = 5; a load is placed on a beam and later lifted; a "
            "valve is opened for exactly one minute. Each is described by "
            "different formulas on different intervals of time, and none of "
            "the methods of the earlier units takes such a forcing in one "
            "piece. Undetermined coefficients needs a forcing whose "
            "derivatives form a finite family, and a function that jumps has "
            "no such family. Variation of parameters can be made to work, but "
            "only by splitting every integral at every switch."
        ),
        Para(
            "The honest alternative is to cut the problem into pieces: solve "
            "on the first interval, evaluate the solution and its derivative "
            "at the first switch, use those values as the initial conditions "
            "on the next interval, and repeat. With two switches that is three "
            "problems and two matchings. Nothing about it is difficult, but "
            "every matching is a chance to drop a sign, and the final answer "
            "comes out as a list of cases that is hard to read as one motion."
        ),
        Para(
            "The Laplace transform does all of that at once, and the reason is "
            "almost disappointingly simple: a switch has a perfectly ordinary "
            "transform. Once the act of switching is written as a function — "
            "the unit step — a piecewise forcing becomes a single expression, "
            "and a single expression passes through the transform method "
            "exactly as every forcing in the last three chapters did. The "
            "matching at the joins is still done, but the algebra does it, "
            "and it does not drop signs."
        ),
    )),
    Section("The unit step function", (
        Box(
            "definition", "Unit step function",
            "For a ≥ 0 the unit step function u(t − a), also called the "
            "Heaviside function after the engineer who used it to solve "
            "circuit equations, is zero before time a and one from time a on. "
            "Its value exactly at t = a does not affect any transform or any "
            "solution, and conventions for it differ.",
            r"u(t-a) = 0 \;\; (t < a), \qquad u(t-a) = 1 \;\; (t \geq a)",
        ),
        Para(
            "Multiplying a function by u(t − a) switches it on at time a: the "
            "product is zero before a and equal to the function after it. "
            "Subtracting a later step switches it off again, so the "
            "difference u(t − a) − u(t − b), for a < b, is a rectangular "
            "window — one on the interval a ≤ t < b and zero elsewhere. "
            "Multiplying by a window keeps a function on one interval and "
            "erases it everywhere else."
        ),
        Display(r"u(t-a) - u(t-b) = 1 \;\; (a \leq t < b), \qquad "
                r"0 \;\; \text{otherwise}", "5.11"),
        Para(
            "Any piecewise-defined function can therefore be written as a sum "
            "of pieces, each multiplied by the window of the interval it "
            "belongs to. The last piece of all has a window with no end, "
            "which is a single step. This is a purely mechanical translation, "
            "and it is worth doing carefully, because every later step works "
            "on the expression it produces."
        ),
        Worked(
            "A piecewise function in steps",
            "Write f(t) = 0 for t < 1, f(t) = t for 1 ≤ t < 3, f(t) = 2 for "
            "t ≥ 3 using unit steps.",
            (
                Step("The middle piece lives on the window from 1 to 3, and the "
                     "last piece is switched on at 3 and never switched off.",
                     r"f(t) = t\left(u(t-1) - u(t-3)\right) + 2\,u(t-3)"),
                Step("Collect by step. Each coefficient now says how much the "
                     "function changes when that switch is thrown: t is added "
                     "at t = 1, and t is taken away and 2 put in its place at "
                     "t = 3.",
                     r"f(t) = t\,u(t-1) + (2 - t)\,u(t-3)"),
            ),
            answer="t u(t − 1) + (2 − t) u(t − 3)",
            answer_latex=r"f(t) = t\,u(t-1) + (2-t)\,u(t-3)",
        ),
        Plot(
            "Steps, windows and a switched ramp",
            "The window u(t − 1) − u(t − 3), and the function of the worked "
            "example built from it. Each jump in the graph is one step in the "
            "formula, and the size of the jump is that step's coefficient "
            "evaluated at the switching time.",
            (Curve("Heaviside(t - 1) - Heaviside(t - 3)", "window on [1, 3)"),
             Curve("t*Heaviside(t - 1) + (2 - t)*Heaviside(t - 3)", "f(t)")),
            t=(0.0, 5.0), ylim=(-0.5, 3.5),
        ),
    )),
    Section("The transform of a step", (
        Para(
            "Transforming u(t − a) straight from the definition takes one "
            "line. The integrand is zero until t = a, so the integral simply "
            "starts later, and what is left is an integral of the exponential "
            "alone."
        ),
        Display(r"\mathcal{L}\{u(t-a)\} = \int_{a}^{\infty}e^{-st}\,dt = "
                r"\frac{e^{-as}}{s}, \qquad s > 0", "5.12"),
        Para(
            "With a = 0 the step is the constant 1 and the formula is the "
            "familiar 1/s. The effect of the delay is the factor e^(−as) and "
            "nothing else. That is not special to the constant function, and "
            "the next section shows that the same factor appears whenever any "
            "function is delayed by a."
        ),
    )),
    Section("The second shifting theorem", (
        Box(
            "theorem", "Second shifting theorem",
            "If F(s) is the transform of f(t) for s > c, and a ≥ 0, then the "
            "function f delayed by a and switched on at a has the transform "
            "below, for the same s. Read backwards, an exponential factor "
            "e^(−as) in a transform means a delay of a in time.",
            r"\mathcal{L}\left\{u(t-a)\,f(t-a)\right\} = e^{-as}F(s)",
        ),
        Box(
            "proof", "Proof",
            "The step makes the integrand zero before a, so the integral "
            "starts at a. Substitute τ = t − a: then t = τ + a, the lower "
            "limit becomes 0, and the exponential splits into e^(−as), which "
            "does not depend on τ, times e^(−sτ). What remains is the "
            "definition of F(s).",
            r"\int_{a}^{\infty}e^{-st}f(t-a)\,dt = \int_{0}^{\infty}e^{-s(\tau+a)}"
            r"f(\tau)\,d\tau = e^{-as}F(s)",
        ),
        Para(
            "Compare it with the first shifting theorem of the last chapter. "
            "There an exponential in t shifted the variable s; here a shift "
            "of the variable t produces an exponential in s. The two are "
            "mirror images, and the rule for telling them apart is the one "
            "given there: a shift in one variable always produces an "
            "exponential factor in the other."
        ),
        Para(
            "The theorem is a statement about f(t − a), not about f(t). The "
            "delayed function must be the same function evaluated at the "
            "shifted time, so that its graph is the graph of f slid a units "
            "to the right. A function that is merely switched on at a — "
            "u(t − a) times something that was already running — is a "
            "different thing, and the next section deals with it."
        ),
    )),
    Section("Switching on a function that was already running", (
        Para(
            "Forcing usually arrives in the form u(t − a)g(t): a ramp, a "
            "sinusoid or an exponential, switched on at a. To use the theorem, "
            "g(t) must first be rewritten as a function of t − a. The trick "
            "is to write t = (t − a) + a everywhere in g, which changes "
            "nothing, and then read the result as h(t − a) with h(t) = g(t + a). "
            "The theorem applies to h."
        ),
        Display(r"\mathcal{L}\left\{u(t-a)\,g(t)\right\} = e^{-as}\,"
                r"\mathcal{L}\left\{g(t+a)\right\}", "5.13"),
        Worked(
            "A ramp switched on at t = 1",
            "Find the transform of t u(t − 1).",
            (
                Step("Here g(t) = t and a = 1, so g(t + 1) = t + 1.",
                     r"\mathcal{L}\{t\,u(t-1)\} = e^{-s}\,\mathcal{L}\{t + 1\}"),
                Step("Transform t + 1 from the table and combine over s².",
                     r"= e^{-s}\left(\frac{1}{s^{2}} + \frac{1}{s}\right) = "
                     r"\frac{(s+1)\,e^{-s}}{s^{2}}"),
                Step("Check by writing the ramp as a delayed ramp plus a delayed "
                     "constant: t u(t − 1) = (t − 1)u(t − 1) + u(t − 1), whose "
                     "transforms are e^(−s)/s² and e^(−s)/s."),
            ),
            answer="(s + 1)e^(−s)/s²",
            answer_latex=r"\mathcal{L}\{t\,u(t-1)\} = \frac{(s+1)\,e^{-s}}{s^{2}}",
        ),
        Para(
            "Notice what the answer is not. It is not e^(−s)/s², which is the "
            "transform of the ramp (t − 1)u(t − 1) that starts from zero at "
            "the switch. The ramp t u(t − 1) jumps to height 1 when it is "
            "switched on, and the extra e^(−s)/s is exactly that jump."
        ),
    )),
    Section("Inverting a delay", (
        Para(
            "In a differential equation the theorem is used backwards, on a "
            "Y(s) that contains exponential factors. The procedure has three "
            "steps, and the order matters. First, group Y(s) by exponential "
            "factor, so that each group has the form e^(−as)G(s). Second, "
            "invert G(s) on its own, ignoring the exponential, with partial "
            "fractions if necessary; call the result g(t). Third, replace t "
            "by t − a everywhere in g and multiply by u(t − a)."
        ),
        Display(r"e^{-as}G(s) \;\longrightarrow\; u(t-a)\,g(t-a)", "5.14"),
        Box(
            "warning", "The exponential is never part of the partial fractions",
            "e^(−as) is not a rational function of s and has no place in a "
            "partial-fraction expansion. Peel it off first, decompose what is "
            "left, and put it back only as a delay at the end. The other "
            "common slip is to shift the step but not the function — to write "
            "u(t − a)g(t) instead of u(t − a)g(t − a). That answer switches on "
            "at the right moment but starts from the wrong place, as though "
            "the system had been running all along.",
            r"e^{-as}G(s) \;\not\longrightarrow\; u(t-a)\,g(t)",
        ),
        Worked(
            "Peel, invert, shift",
            "Find the inverse transform of e^(−2s)/(s(s + 1)).",
            (
                Step("Peel off e^(−2s) and invert what remains by partial "
                     "fractions.",
                     r"\frac{1}{s(s+1)} = \frac{1}{s} - \frac{1}{s+1} "
                     r"\;\longrightarrow\; g(t) = 1 - e^{-t}"),
                Step("Delay by 2: replace t by t − 2 everywhere, including "
                     "inside the exponential, and switch on at 2.",
                     r"\mathcal{L}^{-1}\left\{\frac{e^{-2s}}{s(s+1)}\right\} = "
                     r"u(t-2)\left(1 - e^{-(t-2)}\right)"),
            ),
            answer="u(t − 2)(1 − e^(−(t − 2)))",
            answer_latex=r"u(t-2)\left(1 - e^{-(t-2)}\right)",
        ),
    )),
    Section("A switch at first order", (
        Para(
            "The worked inversion above is already the answer to a "
            "differential equation. Transforming y' + y = u(t − 2) from rest "
            "gives (s + 1)Y = e^(−2s)/s, which is the Y(s) just inverted. "
            "The more instructive version starts away from rest, because then "
            "the answer has two parts that have to be kept apart."
        ),
        Worked(
            "A constant forcing switched on at t = 2",
            "Solve y' + y = u(t − 2) with y(0) = 1.",
            (
                Step("Transform, using L{y'} = sY − 1 and 5.12.",
                     r"sY - 1 + Y = \frac{e^{-2s}}{s}"),
                Step("Solve for Y. The first term comes from the initial value "
                     "and has no exponential; the second comes from the "
                     "forcing and carries the delay.",
                     r"Y = \frac{1}{s+1} + \frac{e^{-2s}}{s(s+1)}"),
                Step("Invert each group. The first is e^(−t); the second was "
                     "inverted in the previous section.",
                     r"y(t) = e^{-t} + u(t-2)\left(1 - e^{-(t-2)}\right)"),
                Step("Read it on each interval. Before t = 2 the step is zero and "
                     "y = e^(−t), free decay from 1. After t = 2 the solution is "
                     "1 − (e² − 1)e^(−t), which climbs towards the new "
                     "equilibrium 1."),
            ),
            equation="y' + y = Heaviside(t - 2)", conditions="y(0) = 1",
            answer="exp(-t) + Heaviside(t - 2)*(1 - exp(-(t - 2)))",
            answer_latex=r"y(t) = e^{-t} + u(t-2)\left(1 - e^{-(t-2)}\right)",
        ),
        Plot(
            "Decay, then a switch",
            "The solution of y' + y = u(t − 2), y(0) = 1, and the forcing. "
            "The solution decays freely until t = 2, reaching e^(−2) ≈ 0.135, "
            "and then turns and climbs towards 1. The graph has a corner at "
            "the switch but no jump.",
            (Curve("exp(-t) + Heaviside(t - 2)*(1 - exp(-(t - 2)))", "y(t)"),
             Curve("Heaviside(t - 2)", "forcing u(t − 2)")),
            t=(0.0, 8.0), ylim=(-0.1, 1.2),
        ),
    )),
    Section("What is continuous at a switch", (
        Para(
            "That corner is not an accident of this example. When the forcing "
            "jumps, something in the equation must jump to balance it, and "
            "it is always the highest derivative. The lower derivatives are "
            "integrals of the higher ones, and integrating a function with a "
            "jump produces a function that is continuous. So in a first-order "
            "equation y is continuous and y' jumps; in a second-order "
            "equation y and y' are both continuous and y'' jumps."
        ),
        Box(
            "theorem", "Continuity across a jump in the forcing",
            "Let y solve ay'' + by' + cy = f(t) with a ≠ 0, where f is "
            "piecewise continuous with a jump of size J at t = t₀. Then y and "
            "y' are continuous at t₀, and y'' jumps there by J/a.",
            r"y''(t_{0}^{+}) - y''(t_{0}^{-}) = \frac{f(t_{0}^{+}) - "
            r"f(t_{0}^{-})}{a}",
        ),
        Para(
            "This is the fact that the piece-by-piece method uses when it "
            "matches y and y' across each join, and it is the fact the "
            "transform builds in automatically. It also gives a quick check "
            "on any answer. In the example above, y' = −e^(−t) just before "
            "t = 2 and y' = (e² − 1)e^(−t) just after; the difference is "
            "e² · e^(−2) = 1, exactly the height of the step, as the theorem "
            "requires with a = 1. An answer that jumped in value at t = 2 "
            "would be wrong however well it fitted the equation on either "
            "side, and that is the error made by writing u(t − 2)(1 − e^(−t)): "
            "it satisfies the equation on both sides of the switch, but it "
            "jumps by 1 − e^(−2) at the switch itself."
        ),
    )),
    Section("A pulse on an oscillator", (
        Para(
            "A pulse is a window, and a window is one step minus another, so "
            "a pulse needs no new theory. Linearity carries each step through "
            "the method on its own. The answer is the response to the first "
            "step minus the same response delayed to the second — two copies "
            "of one function, each switched on at its own time."
        ),
        Worked(
            "A unit pulse from t = 1 to t = 2",
            "Solve y'' + 4y = u(t − 1) − u(t − 2) with y(0) = 0, y'(0) = 0.",
            (
                Step("Transform. The system starts at rest, so only the forcing "
                     "contributes.",
                     r"(s^{2}+4)\,Y = \frac{e^{-s} - e^{-2s}}{s}"),
                Step("Both groups share G(s) = 1/(s(s² + 4)), which the "
                     "convolution chapter inverted by dividing by s.",
                     r"G(s) = \frac{1}{s(s^{2}+4)} \;\longrightarrow\; "
                     r"g(t) = \frac{1}{4}\left(1 - \cos 2t\right)"),
                Step("Delay one copy to t = 1 and one to t = 2, and subtract.",
                     r"y(t) = u(t-1)\,g(t-1) - u(t-2)\,g(t-2)"),
            ),
            equation="y'' + 4*y = Heaviside(t - 1) - Heaviside(t - 2)",
            conditions="y(0) = 0, y'(0) = 0",
            answer="(Heaviside(t - 1)*(1 - cos(2*(t - 1)))"
                   " - Heaviside(t - 2)*(1 - cos(2*(t - 2))))/4",
            answer_latex=r"y(t) = \frac{1}{4}u(t-1)\left(1 - \cos 2(t-1)\right)"
                         r" - \frac{1}{4}u(t-2)\left(1 - \cos 2(t-2)\right)",
        ),
        Para(
            "After the pulse, when both steps are on, the constants cancel "
            "and what is left is a difference of two cosines. Using "
            "cos A − cos B = −2 sin((A + B)/2) sin((A − B)/2), it is a single "
            "oscillation whose amplitude depends only on how long the pulse "
            "lasted. For a pulse of length d on this system the amplitude "
            "left behind is (1/2)|sin d|; here d = 1, so the spring keeps "
            "ringing with amplitude (1/2) sin 1 ≈ 0.42 for ever, because "
            "nothing in the equation takes the energy away."
        ),
        Display(r"t \geq 2: \quad y(t) = \frac{1}{4}\left(\cos 2(t-2) - "
                r"\cos 2(t-1)\right) = \frac{\sin 1}{2}\,\sin(2t - 3)", "5.15"),
        Para(
            "The formula has a surprising consequence. If the pulse lasts "
            "exactly π, one full period of this oscillator, then sin d = 0 and "
            "the system is left perfectly still: the push it received while "
            "the forcing was on is undone, to the last decimal, by the "
            "oscillation it was already making. The solution with the second "
            "switch at 1 + π checks out by substitution just as the one "
            "above does, and after 1 + π it is identically zero."
        ),
        Plot(
            "Two pulses, two outcomes",
            "The response to a pulse from 1 to 2, which leaves the spring "
            "ringing with amplitude (sin 1)/2, and to a pulse from 1 to 1 + π, "
            "one full period, which leaves it at rest. Both are zero until "
            "the first switch.",
            (Curve("(Heaviside(t - 1)*(1 - cos(2*(t - 1)))"
                   " - Heaviside(t - 2)*(1 - cos(2*(t - 2))))/4", "pulse of length 1"),
             Curve("(Heaviside(t - 1)*(1 - cos(2*(t - 1)))"
                   " - Heaviside(t - 1 - pi)*(1 - cos(2*(t - 1 - pi))))/4",
                   "pulse of length π")),
            t=(0.0, 10.0), ylim=(-0.6, 0.7),
        ),
        Figure("pulse_response",
               "Set the damping to zero, put the switch-on at 2 and move the "
               "switch-off. This oscillator is y'' + 4y, so its period is π: "
               "with the switch-off near 2 + π ≈ 5.14 the ringing after the "
               "pulse almost vanishes, and it is largest when the pulse lasts "
               "half a period. Then add damping and watch every case die away."),
    )),
    Section("Switching a damped system off", (
        Para(
            "The same method handles forcing that is on from the start and "
            "switched off later. The forcing 1 − u(t − 1) is one until t = 1 "
            "and zero afterwards, so the answer is the step response minus "
            "the step response delayed to t = 1."
        ),
        Worked(
            "Forcing removed at t = 1",
            "Solve y'' + 3y' + 2y = 1 − u(t − 1) with y(0) = 0, y'(0) = 0.",
            (
                Step("Transform. The factor (1 − e^(−s)) multiplies the same "
                     "rational function twice.",
                     r"Y = \left(1 - e^{-s}\right)\frac{1}{s(s+1)(s+2)}"),
                Step("Decompose the rational part and invert it: this is the "
                     "step response g.",
                     r"\frac{1}{s(s+1)(s+2)} = \frac{1/2}{s} - \frac{1}{s+1} + "
                     r"\frac{1/2}{s+2} \;\longrightarrow\; g(t) = \frac{1}{2} - "
                     r"e^{-t} + \frac{1}{2}e^{-2t}"),
                Step("The answer is g(t) − u(t − 1)g(t − 1). At t = 1 the "
                     "solution has reached g(1) ≈ 0.200, two fifths of the way "
                     "to the equilibrium 1/2 it was heading for when the "
                     "forcing stopped.",
                     r"y(t) = g(t) - u(t-1)\,g(t-1)"),
            ),
            equation="y'' + 3*y' + 2*y = 1 - Heaviside(t - 1)",
            conditions="y(0) = 0, y'(0) = 0",
            answer="1/2 - exp(-t) + exp(-2*t)/2"
                   " - Heaviside(t - 1)*(1/2 - exp(-(t - 1)) + exp(-2*(t - 1))/2)",
            answer_latex=r"y(t) = g(t) - u(t-1)\,g(t-1), \quad g(t) = \frac{1}{2} "
                         r"- e^{-t} + \frac{1}{2}e^{-2t}",
        ),
        Para(
            "After the switch the constants 1/2 cancel, and y is a combination "
            "of e^(−t) and e^(−2t) alone: the system is overdamped, the forcing "
            "is gone, and it returns to rest without oscillating. Compare the "
            "undamped oscillator of the previous section, which kept its "
            "energy for ever. The difference is one term in the equation, and "
            "it is visible in the answer as the presence or absence of "
            "decaying exponentials after the last switch."
        ),
        Worked(
            "A ramp switched on",
            "Solve y' + 2y = t u(t − 1) with y(0) = 0.",
            (
                Step("Transform, using the result of the ramp example, and "
                     "solve for Y.",
                     r"Y = e^{-s}\,\frac{s+1}{s^{2}(s+2)}"),
                Step("Decompose the rational part. Setting s = 0 in "
                     "(s + 1)/(s + 2) gives the 1/s² coefficient 1/2; s = −2 "
                     "gives the 1/(s + 2) coefficient −1/4; and the s² "
                     "coefficients force the 1/s coefficient to be 1/4.",
                     r"\frac{s+1}{s^{2}(s+2)} = \frac{1/4}{s} + \frac{1/2}{s^{2}} - "
                     r"\frac{1/4}{s+2}"),
                Step("Invert, then delay by 1 and simplify: 1/4 + (t − 1)/2 is "
                     "t/2 − 1/4.",
                     r"y(t) = u(t-1)\left(\frac{t}{2} - \frac{1}{4} - "
                     r"\frac{1}{4}e^{-2(t-1)}\right)"),
            ),
            equation="y' + 2*y = t*Heaviside(t - 1)", conditions="y(0) = 0",
            answer="Heaviside(t - 1)*(t/2 - 1/4 - exp(-2*(t - 1))/4)",
            answer_latex=r"y(t) = u(t-1)\left(\frac{t}{2} - \frac{1}{4} - "
                         r"\frac{1}{4}e^{-2(t-1)}\right)",
        ),
        Para(
            "Check the continuity theorem on this answer. At t = 1 the bracket "
            "is 1/2 − 1/4 − 1/4 = 0, so y is continuous. But the forcing jumps "
            "from 0 to 1 there, because the ramp is switched on at height 1, "
            "and y' jumps by the same amount: its value just after the switch "
            "is 1/2 + 1/2 = 1."
        ),
    )),
    Section("Simplifying after the shift", (
        Para(
            "A delayed answer can often be tidied once the shift is done, and "
            "the tidy form can say something the shifted form hides. For "
            "y'' + y = u(t − π) from rest, Y = e^(−πs)/(s(s² + 1)); the "
            "rational part inverts to 1 − cos t, so the answer is "
            "u(t − π)(1 − cos(t − π)). Since cos(t − π) = −cos t, this is "
            "u(t − π)(1 + cos t). The oscillation after the switch is about the "
            "new equilibrium 1 and swings between 0 and 2 — the spring, "
            "suddenly loaded, overshoots to twice the static deflection."
        ),
        Para(
            "The same doubling happens for any undamped spring hit by a "
            "suddenly applied constant load, and it is the reason engineers "
            "treat a suddenly applied load as twice as dangerous as the same "
            "load applied slowly. Damping removes part of the overshoot, and "
            "the step response of the convolution chapter shows how much."
        ),
    )),
    Section("Periodic switching", (
        Para(
            "A square wave that is on for a units and off for a units, "
            "repeated for ever, is an infinite sum of steps with alternating "
            "signs: on at 0, off at a, on at 2a, and so on. Its transform is "
            "a geometric series in e^(−as), which sums in closed form."
        ),
        Display(r"f(t) = \sum_{n=0}^{\infty}(-1)^{n}u(t-na) \;\Longrightarrow\; "
                r"F(s) = \frac{1}{s}\sum_{n=0}^{\infty}\left(-e^{-as}\right)^{n} = "
                r"\frac{1}{s\left(1 + e^{-as}\right)}", "5.16"),
        Para(
            "Solving an equation driven by the square wave then produces a "
            "Y(s) with that geometric factor in it, and inverting term by term "
            "gives the response as an infinite sum of delayed step responses. "
            "At any finite time only finitely many of them are switched on, "
            "so the sum is really finite wherever it is evaluated. This is "
            "the route to the steady response of a circuit driven by a "
            "switched supply, and it is the transform's version of the "
            "Fourier series that a later course develops."
        ),
    )),
    Section("Common errors", (
        Para(
            "The commonest error by far is the one the warning box describes: "
            "inverting e^(−as)G(s) to u(t − a)g(t) instead of u(t − a)g(t − a). "
            "It is easy to catch, because the continuity theorem says the "
            "answer cannot jump, and the wrong answer usually does. Add up "
            "everything multiplied by u(t − a) and evaluate it at t = a: "
            "unless the forcing has an impulse there, which is the subject of "
            "the next chapter, the total must be zero."
        ),
        Para(
            "The second is transforming u(t − a)g(t) as if it were "
            "u(t − a)g(t − a), which gives e^(−as)G(s) when the correct answer "
            "is e^(−as) times the transform of g(t + a). The third is putting "
            "e^(−as) into the partial fractions. The fourth is dropping the "
            "step from the final answer: without it, the formula claims the "
            "system was moving before anything touched it, which for a system "
            "starting at rest is simply false."
        ),
    )),
    Section("Summary", (
        Para(
            "The unit step u(t − a) turns a case distinction into a function, "
            "so a piecewise forcing becomes one expression built from steps "
            "and windows. Its transform is e^(−as)/s, and the second shifting "
            "theorem, L{u(t − a)f(t − a)} = e^(−as)F(s), says that a delay in "
            "time is an exponential factor in s. To invert, peel the "
            "exponential off, invert the rest, then shift the argument and "
            "switch on. The solution and every derivative below the highest "
            "are continuous across a switch; the highest derivative jumps by "
            "the size of the jump in the forcing divided by the leading "
            "coefficient. After the last switch, what the system does is "
            "decided by its own equation alone: a damped system comes to "
            "rest, and an undamped one keeps whatever the forcing left it."
        ),
    )),
)
