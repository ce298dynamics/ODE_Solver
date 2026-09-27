"""Unit 5 chapters -- the Laplace transform (Edwards ch. 7)."""

from __future__ import annotations

from ..chapter import Box, Curve, Display, Figure, Para, Plot, Section, Step, Worked

__all__ = ["TRANSFORM"]


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
