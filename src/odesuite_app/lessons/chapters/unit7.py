"""Series-unit chapters -- series solutions (Edwards ch. 8).

The file is unit7 after the lesson module; the course teaches this unit
last, after nonlinear systems, which is why the prose names units rather
than numbering them.
"""

from __future__ import annotations

from ..chapter import Box, Curve, Display, Figure, Para, Plot, Section, Step, Worked

__all__ = ["POWERSERIES", "RECURRENCE", "FROBENIUS"]


POWERSERIES = (
    Section("When there is no formula", (
        Para(
            "Every method in this course so far has been a way of finding a "
            "formula: an integrating factor, a characteristic root, a "
            "transform to invert, an eigenvector. Each works on a particular "
            "family of equations, and the families are narrower than they "
            "look. Take y'' + y = 0, whose solutions are cos t and sin t, "
            "and change a single coefficient from a constant to t. The result, "
            "y'' + ty = 0, is still linear, still second order, still has "
            "coefficients that are polynomials and solutions that exist for "
            "every t — and not one technique of the earlier units produces a "
            "formula for it. It has no characteristic equation, since a "
            "coefficient is not constant; it is not of Cauchy–Euler type; the "
            "Laplace transform, through L{t f(t)} = −F'(s), only trades it "
            "for another differential equation, first order in s; and no "
            "guess built from exponentials, sines, powers and logarithms "
            "satisfies it."
        ),
        Para(
            "That is not an unlucky choice. The equations of mathematical "
            "physics that a second course meets first are almost all like "
            "this. Airy's equation y'' = ty describes light near a caustic "
            "and a quantum particle in a uniform field. Legendre's equation "
            "governs potentials and temperatures on a sphere, Hermite's the "
            "quantum harmonic oscillator, Bessel's the vibrations of a drum "
            "and the flow of heat in a cylinder. All of them are "
            "second-order linear equations with polynomial coefficients, and "
            "none of them, in general, has a solution in elementary "
            "functions. The equations with closed-form solutions are a thin "
            "and unrepresentative slice."
        ),
        Para(
            "So the last technique of the course changes what an answer is "
            "allowed to look like. Instead of searching for a formula among "
            "functions that already have names, it builds the solution one "
            "coefficient at a time as a power series, y = a₀ + a₁t + a₂t² + ⋯. "
            "The differential equation turns out to supply a rule that "
            "produces every coefficient from the first two, and that rule is "
            "a complete description of the solution — as complete as a "
            "formula, and available when no formula is. This chapter sets up "
            "the method and states the theorem that guarantees it works and "
            "says how far it reaches; the recurrence chapter makes the "
            "bookkeeping systematic and works out radii of convergence in "
            "detail, complex singular points included; and the Frobenius chapter "
            "deals with the points where a plain power series is not enough."
        ),
    )),
    Section("Power series: the three facts the method uses", (
        Para(
            "The method leans on a small amount of theory from calculus, and "
            "it is worth having it in one place, because each fact is used "
            "at a specific step and the method is only as sound as they are."
        ),
        Box(
            "definition", "Power series and radius of convergence",
            "A power series about t₀ is a series of the form below. There is "
            "a number ρ, with 0 ≤ ρ ≤ ∞, called its radius of convergence, "
            "such that the series converges absolutely when |t − t₀| < ρ and "
            "diverges when |t − t₀| > ρ. On the interval of convergence the "
            "sum is a function of t.",
            r"\sum_{n=0}^{\infty} a_n (t - t_0)^{n} = a_0 + a_1 (t - t_0) + "
            r"a_2 (t - t_0)^{2} + \cdots",
        ),
        Para(
            "The examples to keep in mind are the geometric series "
            "1 + t + t² + ⋯ = 1/(1 − t), with ρ = 1, and the exponential "
            "series 1 + t + t²/2! + ⋯ = e^t, with ρ = ∞. Most of this chapter "
            "takes t₀ = 0. A series about any other point is a series in the "
            "shifted variable s = t − t₀, so nothing new is needed in "
            "principle, but the shift is not free: every coefficient of the "
            "equation has to be rewritten in powers of s first, and the "
            "section on other centres shows what that does to a recurrence."
        ),
        Box(
            "theorem", "Term-by-term differentiation",
            "Inside its interval of convergence a power series may be "
            "differentiated term by term, and the differentiated series has "
            "the same radius of convergence. Consequently the sum has "
            "derivatives of every order there, each given by a series of the "
            "same kind.",
            r"y = \sum_{n=0}^{\infty} a_n t^{n} \;\Longrightarrow\; "
            r"y' = \sum_{n=1}^{\infty} n\,a_n t^{n-1}, \quad "
            r"y'' = \sum_{n=2}^{\infty} n(n-1)\,a_n t^{n-2}",
        ),
        Para(
            "This is the fact that lets a series be put into a differential "
            "equation at all, and the starting indices are worth noticing. "
            "Differentiating kills the constant term, so the sum for y' "
            "starts at n = 1 and the sum for y'' at n = 2. Setting t = 0 in "
            "those formulas leaves only their first terms: y(0) = a₀, "
            "y'(0) = a₁, y''(0) = 2a₂, and in general y⁽ⁿ⁾(0) = n!·aₙ. A "
            "power series is therefore the Taylor series of its own sum."
        ),
        Display(r"a_n = \frac{y^{(n)}(0)}{n!}", "1"),
        Box(
            "theorem", "Identity theorem",
            "If a power series sums to zero at every point of an interval "
            "around 0, then every one of its coefficients is zero. "
            "Equivalently, two power series that agree on such an interval "
            "have the same coefficients.",
            r"\sum_{n=0}^{\infty} c_n t^{n} = 0 \ \text{for } |t| < \rho "
            r"\;\Longrightarrow\; c_n = 0 \ \text{for every } n",
        ),
        Box(
            "proof", "Proof",
            "Call the sum f. It is identically zero on the interval, so all "
            "its derivatives are zero there too, and in particular at t = 0. "
            "By formula (1), cₙ = f⁽ⁿ⁾(0)/n! = 0 for every n.",
        ),
        Para(
            "The identity theorem is the engine of the whole method. After "
            "the series is substituted, the differential equation becomes a "
            "single power series set equal to zero, and the theorem splits "
            "that one equation into infinitely many: the coefficient of t⁰ "
            "is zero, the coefficient of t¹ is zero, and so on. Each of "
            "those is an ordinary algebraic equation among a few of the "
            "unknown coefficients."
        ),
        Box(
            "definition", "Analytic function",
            "A function is analytic at t₀ if it equals a power series about "
            "t₀ with positive radius of convergence on some interval around "
            "t₀. Polynomials, e^t, sin t and cos t are analytic everywhere; a "
            "rational function P/Q is analytic at every point where Q ≠ 0.",
        ),
    )),
    Section("A first example, one coefficient at a time", (
        Para(
            "Before any theory about when it works, here is the method on an "
            "equation whose answer is already known, so that every step can "
            "be checked against it. The equation is first order, which keeps "
            "the sums short; nothing in the procedure depends on that."
        ),
        Worked(
            "Rebuilding an exponential",
            "Solve y' = 2ty with y(0) = 1 by assuming a power series about "
            "t = 0, and identify the sum.",
            (
                Step("Write y = Σ aₙtⁿ. Then y' = Σ naₙtⁿ⁻¹ from n = 1, and "
                     "2ty = Σ 2aₙtⁿ⁺¹ from n = 0. The powers differ, so shift "
                     "each index until both sums run over the same power. In "
                     "the sum for y' put k = n − 1, so n = k + 1: the power "
                     "tⁿ⁻¹ becomes tᵏ, the coefficient naₙ becomes "
                     "(k + 1)aₖ₊₁, and the start n = 1 becomes k = 0. In the "
                     "sum for 2ty put k = n + 1, so n = k − 1: the power "
                     "becomes tᵏ, the coefficient 2aₖ₋₁, and the start n = 0 "
                     "becomes k = 1. Then rename k back to n. A shift moves "
                     "the exponent, the coefficient's subscript and the lower "
                     "limit together, and the lower limit is the half that "
                     "gets forgotten.",
                     r"\sum_{n=0}^{\infty} (n+1)a_{n+1} t^{n} = "
                     r"\sum_{n=1}^{\infty} 2a_{n-1} t^{n}"),
                Step("Compare coefficients. The power t⁰ appears only on the "
                     "left, so a₁ = 0. For n ≥ 1 the two sides must agree, "
                     "which gives a rule for each coefficient in terms of the "
                     "one two places back.",
                     r"a_1 = 0, \qquad a_{n+1} = \frac{2\,a_{n-1}}{n+1} "
                     r"\quad (n \geq 1)"),
                Step("Since a₁ = 0 every odd coefficient is zero. The even "
                     "ones are a₂ = a₀, a₄ = a₀/2, a₆ = a₀/6, a₈ = a₀/24: each "
                     "is the previous one divided by k when the power is 2k, "
                     "so a₂ₖ = a₀/k!.",
                     r"y = a_0\left(1 + t^{2} + \frac{t^{4}}{2!} + "
                     r"\frac{t^{6}}{3!} + \cdots\right)"),
                Step("That is the exponential series with t² in place of t. "
                     "The condition y(0) = 1 says a₀ = 1."),
            ),
            equation="y' = 2*t*y", conditions="y(0) = 1",
            answer="exp(t**2)", answer_latex=r"y(t) = e^{t^{2}}",
        ),
        Para(
            "Three things in that calculation recur in every example. The "
            "sums arrived with different powers of t and had to be re-indexed "
            "before anything could be compared; that renaming is pure "
            "bookkeeping, and it is the step the recurrence chapter "
            "systematises. The comparison produced a rule — a recurrence "
            "relation — rather than the coefficients themselves. And one "
            "coefficient, a₀, was never determined: it is y(0), the one free "
            "constant a first-order equation should have. The equation had "
            "no opinion about it, and the initial condition supplied it."
        ),
        Worked(
            "A geometric series",
            "Solve (1 − t)y' = y with y(0) = 1 by power series about t = 0.",
            (
                Step("Expand the left side: (1 − t)y' = Σ (n + 1)aₙ₊₁tⁿ − "
                     "Σ naₙtⁿ, both now over tⁿ from n = 0 (the second sum's "
                     "n = 0 term is zero anyway). Moving y = Σ aₙtⁿ across and "
                     "collecting, the coefficient of tⁿ factorises.",
                     r"\sum_{n=0}^{\infty} (n+1)\left(a_{n+1} - a_n\right) "
                     r"t^{n} = 0"),
                Step("By the identity theorem each coefficient is zero, so "
                     "aₙ₊₁ = aₙ for every n: all the coefficients equal a₀, "
                     "and a₀ = y(0) = 1.",
                     r"y = 1 + t + t^{2} + t^{3} + \cdots"),
                Step("That is the geometric series, whose sum on |t| < 1 is "
                     "1/(1 − t)."),
            ),
            equation="(1-t)*y' = y", conditions="y(0) = 1",
            answer="1/(1-t)", answer_latex=r"y(t) = \frac{1}{1 - t}",
        ),
        Para(
            "The second example already shows the limitation that the rest "
            "of the chapter is about. The series 1 + t + t² + ⋯ converges only "
            "for |t| < 1, although the function it sums is perfectly good "
            "for every t except 1. Divide the equation by its leading "
            "coefficient and it reads y' = y/(1 − t): the coefficient "
            "1/(1 − t) is undefined at t = 1, and the series cannot reach "
            "past that point. The series knows where the equation breaks "
            "down."
        ),
    )),
    Section("Partial sums, and how far they reach", (
        Para(
            "An infinite series cannot be evaluated, only its partial sums, "
            "so it matters how quickly they approach the answer and where. "
            "For the geometric series the error can be written down exactly. "
            "The sum of the first N terms is (1 − t^N)/(1 − t), which falls "
            "short of 1/(1 − t) by t^N/(1 − t) — a relative error of exactly "
            "t^N for 0 ≤ t < 1. Five terms are within one per cent of the "
            "answer as long as t⁵ ≤ 0.01, that is for t up to 0.01^(1/5) ≈ "
            "0.398; ten terms reach 0.01^(1/10) ≈ 0.631, and twenty-four "
            "0.01^(1/24) ≈ 0.825. Each "
            "extra term buys less, and no number of terms reaches t = 1."
        ),
        Figure(
            "partial_sums",
            "With 'terms kept' at its default of 5, the readout gives "
            "agreement within 1% out to t = 0.398, the 0.01^(1/N) of the "
            "text. Drag the slider up through 10 (0.631) to its maximum of "
            "24 (0.825) and watch the solid partial sum peel away from the "
            "dotted curve 1/(1 − t) later and later — but always before the "
            "dashed line at t = 1. Then look left, with many terms kept. The equation is "
            "perfectly regular at t = −1, yet a second dashed line sits there "
            "too, and past it the partial sums swing ever more wildly as the "
            "count goes between odd and even: "
            "convergence is decided by distance from the centre, not by "
            "which side the trouble is on.",
        ),
        Para(
            "The left half of the figure is the more surprising one. Nothing "
            "happens to the equation at t = −1, and the function 1/(1 − t) is "
            "a harmless 1/2 there. But a power series converges on an "
            "interval symmetric about its centre, so once the singularity at "
            "t = 1 limits the radius to 1, the series fails at t = −1 as "
            "well: the terms there are ±1 and do not shrink. Just inside, "
            "convergence is slow — at t = −0.9 even twenty-four terms give "
            "0.484 against the true 0.526. The section on the existence "
            "theorem below turns this observation into a rule."
        ),
    )),
    Section("Second order: two free coefficients", (
        Para(
            "The equations this unit is for are second order, and the same "
            "procedure applies with one more sum. Here it is on the simplest "
            "of them, whose answer the second-order unit found from "
            "characteristic roots, so that the series can be compared with "
            "cosine and sine."
        ),
        Worked(
            "y'' + y = 0 rebuilt from its series",
            "Solve y'' + y = 0 with y(0) = 2, y'(0) = 3 by power series about "
            "t = 0.",
            (
                Step("y'' = Σ n(n − 1)aₙtⁿ⁻² from n = 2. Shift the index by "
                     "two so that it runs over tⁿ from n = 0, then add "
                     "y = Σ aₙtⁿ.",
                     r"\sum_{n=0}^{\infty}\left[(n+2)(n+1)a_{n+2} + a_n\right]"
                     r" t^{n} = 0"),
                Step("Every bracket is zero, which gives the recurrence. It "
                     "links each coefficient to the one two places back, so "
                     "the even coefficients descend from a₀ and the odd ones "
                     "from a₁, and the two chains never mix.",
                     r"a_{n+2} = -\frac{a_n}{(n+2)(n+1)}"),
                Step("Running it: a₂ = −a₀/2, a₄ = a₀/24, a₆ = −a₀/720, and "
                     "a₃ = −a₁/6, a₅ = a₁/120, a₇ = −a₁/5040. The pattern is "
                     "a₂ₖ = (−1)ᵏa₀/(2k)! and a₂ₖ₊₁ = (−1)ᵏa₁/(2k + 1)!.",
                     r"y = a_0\left(1 - \frac{t^{2}}{2!} + \frac{t^{4}}{4!} "
                     r"- \cdots\right) + a_1\left(t - \frac{t^{3}}{3!} + "
                     r"\frac{t^{5}}{5!} - \cdots\right)"),
                Step("The brackets are the series of cos t and sin t. The "
                     "conditions need no solving: a₀ = y(0) = 2 and "
                     "a₁ = y'(0) = 3."),
            ),
            equation="y'' + y = 0", conditions="y(0) = 2, y'(0) = 3",
            answer="2*cos(t) + 3*sin(t)",
            answer_latex=r"y(t) = 2\cos t + 3\sin t",
        ),
        Para(
            "Two coefficients went undetermined this time, and that is "
            "exactly right. The recurrence expresses a₂ in terms of a₀, a₃ "
            "in terms of a₁, and every later coefficient in terms of earlier "
            "ones, but nothing fixes a₀ or a₁ themselves. A second-order "
            "equation has a two-parameter family of solutions, and the two "
            "free coefficients are the two parameters. Formula (1) says what "
            "they are."
        ),
        Box(
            "theorem", "The free coefficients are the initial conditions",
            "For a power series solution y = Σ aₙ(t − t₀)ⁿ of a second-order "
            "equation at an ordinary point, a₀ and a₁ are arbitrary and "
            "every later coefficient is determined by them. They are the "
            "initial values at the centre.",
            r"a_0 = y(t_0), \qquad a_1 = y'(t_0)",
        ),
        Para(
            "This is a convenience the series method shares with the Laplace "
            "transform and not with characteristic roots or variation of "
            "parameters. There the general solution comes first and the "
            "constants are found at the end by solving a linear system; here, "
            "as with the transform, the initial conditions are the constants "
            "and are written straight in. The general "
            "solution splits the same way: setting a₀ = 1, a₁ = 0 gives one "
            "solution y₁ (here cos t), setting a₀ = 0, a₁ = 1 gives a second "
            "y₂ (here sin t), and y = a₀y₁ + a₁y₂. Their Wronskian at 0 is "
            "1·1 − 0·0 = 1, so they are independent, by the test of the "
            "second-order unit."
        ),
        Para(
            "Formula (1) also offers a second route to the coefficients, "
            "useful when only the first few are wanted: differentiate the "
            "equation and evaluate at the centre. From y'' = −y, "
            "y''(0) = −y(0) = −2, so a₂ = −2/2! = −1, which is −a₀/2 as the "
            "recurrence said. Differentiating once more, y''' = −y' gives "
            "y'''(0) = −3 and a₃ = −3/3! = −1/2. The recurrence and the "
            "Taylor coefficients are the same numbers reached two ways."
        ),
        Plot(
            "Partial sums of the cosine series",
            "cos t against its series truncated after t⁴, t⁸ and t¹⁶. The "
            "radius is infinite, so every truncation is eventually wrong and "
            "the full series is never wrong. Every curve is even, and to the "
            "right of 0 the error first passes 0.05 at about t = 1.84 through "
            "t⁴, at about 3.39 through t⁸, and at about 6.43 through t¹⁶.",
            (Curve("cos(t)", "cos t"),
             Curve("1 - t**2/2 + t**4/24", "through t⁴"),
             Curve("1 - t**2/2 + t**4/24 - t**6/720 + t**8/40320",
                   "through t⁸"),
             Curve("1 - t**2/2 + t**4/24 - t**6/720 + t**8/40320"
                   " - t**10/3628800 + t**12/479001600"
                   " - t**14/87178291200 + t**16/20922789888000",
                   "through t¹⁶")),
            t=(-10.0, 10.0), ylim=(-2.0, 2.0),
        ),
    )),
    Section("Ordinary and singular points", (
        Para(
            "The examples so far worked because they had to — their answers "
            "were known to be analytic. For a new equation the assumption "
            "y = Σ aₙtⁿ is a genuine assumption, and it can fail. Whether it "
            "is safe depends on the coefficients of the equation near the "
            "centre, and the condition is stated in the same standard form "
            "as the integrating-factor lesson and the existence theorem of "
            "the second-order unit: divide through so that y'' stands alone."
        ),
        Display(r"P(t)\,y'' + Q(t)\,y' + R(t)\,y = 0 \;\Longrightarrow\; "
                r"y'' + p(t)\,y' + q(t)\,y = 0, \quad p = \frac{Q}{P},\ "
                r"q = \frac{R}{P}", "2"),
        Box(
            "definition", "Ordinary point and singular point",
            "The point t₀ is an ordinary point of equation (2) if p and q are "
            "both analytic at t₀. Otherwise it is a singular point. When P, "
            "Q and R are polynomials with no common factor, t₀ is ordinary "
            "exactly when the leading coefficient does not vanish there.",
            r"P(t_0) \neq 0",
        ),
        Para(
            "The polynomial test covers almost every equation of this unit "
            "(one example later has the coefficient eᵗ, and there p and q "
            "are checked directly). If "
            "P(t₀) ≠ 0 then Q/P and R/P are rational functions with non-zero "
            "denominators at t₀, hence analytic there. If P(t₀) = 0 and the "
            "factors have been cancelled, at least one of Q/P and R/P blows "
            "up at t₀, and that point is singular. Whether a point is "
            "ordinary is a property of the equation alone. Initial conditions "
            "choose which solution is wanted; they cannot make a singular "
            "point ordinary or an ordinary one singular."
        ),
        Box(
            "warning", "Cancel common factors first",
            "The test reads P(t₀), but only after any factor shared by P, Q "
            "and R has been cancelled. t·y'' + t·y' + t·y = 0 has P(0) = 0, "
            "yet dividing by t gives y'' + y' + y = 0, for which every point "
            "is ordinary. The definition in terms of p and q never has this "
            "problem, which is why it is the real definition.",
        ),
        Para(
            "Some classifications, each read off the leading coefficient. "
            "Legendre's equation (1 − t²)y'' − 2ty' + 6y = 0 has P = 1 − t², "
            "which is 1 at the origin: t = 0 is ordinary, and the singular "
            "points are t = ±1, where the standard-form coefficients "
            "−2t/(1 − t²) and 6/(1 − t²) blow up. Hermite's equation "
            "y'' − 2ty' + 4y = 0 and Airy's y'' − ty = 0 have P = 1, so "
            "every point of the line is ordinary. (1 + t²)y'' + y = 0 has no "
            "real singular point at all, but its leading coefficient "
            "vanishes at t = ±i — and that will matter. The Cauchy–Euler "
            "equation t²y'' + ty' − y = 0 has P = t², so t = 0 is singular, "
            "and the reduction-of-order chapter already found its solutions: "
            "t and 1/t — and no power series can be 1/t."
        ),
    )),
    Section("The existence theorem", (
        Para(
            "At an ordinary point the assumption is not a gamble. This is "
            "the theorem that turns the method into a procedure, and it says "
            "not only that series solutions exist but how far they reach."
        ),
        Box(
            "theorem", "Series solutions at an ordinary point",
            "Let t₀ be an ordinary point of y'' + p(t)y' + q(t)y = 0. Then "
            "every solution is analytic at t₀: for any a₀ and a₁ there is "
            "exactly one solution y = Σ aₙ(t − t₀)ⁿ with those first two "
            "coefficients, and the general solution is a₀y₁ + a₁y₂ with y₁, "
            "y₂ two independent series solutions. Each series converges at "
            "least for |t − t₀| < d, where d is the distance from t₀ to the "
            "nearest singular point s of the equation in the complex plane; "
            "the radius of convergence ρ of each series is therefore at "
            "least d.",
            r"\rho \geq d = \min_{s\ \mathrm{singular}} \left|s - t_0\right|",
        ),
        Box(
            "remark", "Where the proof goes",
            "Uniqueness of the coefficients is the calculation of the "
            "examples: the recurrence fixes a₂, a₃, … once a₀ and a₁ are "
            "chosen. The real content is convergence. The classical proof, "
            "by majorants, bounds the coefficients of p and q by those of a "
            "geometric series with ratio 1/r for any r < d, shows that the "
            "recurrence then cannot make the aₙ grow faster than a "
            "comparable geometric sequence, and concludes that the series "
            "converges for |t − t₀| < r. It is longer than it is "
            "illuminating, and the statement is what gets used.",
        ),
        Para(
            "Two phrases in the theorem deserve attention. *At least*: the "
            "guarantee is a lower bound, and a particular solution can do "
            "better. Legendre's equation at the origin has d = 1, a "
            "guaranteed radius of 1, yet one of its solutions, 1 − 3t², is a polynomial "
            "and converges everywhere. What the theorem promises is that no "
            "solution does worse, and later in this chapter a second "
            "solution of a Legendre equation turns out to need exactly the "
            "guaranteed radius and not a fraction more."
        ),
        Para(
            "*Complex plane*: the singular points are found among all roots "
            "of P, real or not, and distance is measured in the plane. The "
            "equation (1 + t²)y'' + y = 0 is well behaved on the whole real "
            "line, but P vanishes at ±i, a distance 1 from the origin, and "
            "its series about 0 are guaranteed only for |t| < 1. A real "
            "series cannot see past a complex singularity any more than a "
            "real one, and the recurrence chapter returns to this surprise "
            "with the equation y'' + y/(1 + t²) = 0."
        ),
        Para(
            "The centre matters as much as the singular points. For "
            "(t² − 2t + 5)y'' + ty' − y = 0 the leading coefficient has roots "
            "1 ± 2i, so every real point is ordinary, yet the guaranteed "
            "radius is d = √5 ≈ 2.236 about t₀ = 0 and only d = 2 about "
            "t₀ = 1, the real point directly below the singularities; the "
            "recurrence chapter works such radii out in detail."
        ),
        Para(
            "The guarantee is cheap: it costs one factorisation and is known "
            "before a single coefficient is computed. That is the habit worth "
            "forming — classify the point and find the radius first, then "
            "substitute — and it is the order the app follows when it works "
            "this lesson's examples step by step: it checks that t = 0 is "
            "ordinary, states how far the series reaches, substitutes and "
            "collects, prints the recurrence, and only then the solutions."
        ),
    )),
    Section("The method in six steps", (
        Box(
            "remark", "Power series about an ordinary point",
            "1. Write the equation as P y'' + Q y' + R y = 0, cancel any "
            "factor common to P, Q and R, and check that P(t₀) ≠ 0. 2. Find "
            "the roots of P, complex ones included; the distance d from t₀ to "
            "the nearest is the guaranteed radius. 3. Put s = t − t₀, write "
            "every coefficient in powers of s (nothing to do when t₀ = 0, "
            "where s = t), and substitute y = Σ aₙsⁿ and the term-by-term "
            "derivatives. 4. Re-index every sum so that each runs over the "
            "same power sⁿ, and note where each one starts. 5. Collect, set the coefficient of "
            "each power "
            "to zero, and solve for the highest-index coefficient: that is "
            "the recurrence. 6. Leave a₀ and a₁ free, or set them from "
            "y(t₀) and y'(t₀), and generate the rest.",
        ),
        Para(
            "Here is the procedure on Legendre's equation in its general "
            "form, (1 − t²)y'' − 2ty' + ℓ(ℓ + 1)y = 0. It is often written "
            "with n in place of ℓ; here n is busy as the summation index, and "
            "ℓ matches the slider of the recurrence chapter's figure. Steps 1 "
            "and 2 were done above: t = 0 is ordinary and d = 1, so ρ ≥ 1."
        ),
        Para(
            "For step 4, the product (1 − t²)y'' splits into Σ n(n − 1)aₙtⁿ⁻², "
            "which shifts to Σ (n + 2)(n + 1)aₙ₊₂tⁿ, and −Σ n(n − 1)aₙtⁿ, which "
            "is already over tⁿ. The second sum may as well start at n = 0, "
            "because its n = 0 and n = 1 terms are zero; likewise −2ty' is "
            "−Σ 2naₙtⁿ from n = 0. Collecting the coefficient of tⁿ and "
            "factorising:"
        ),
        Display(r"(n+2)(n+1)\,a_{n+2} = \left[n(n+1) - \ell(\ell+1)\right] a_n "
                r"= (n - \ell)(n + \ell + 1)\, a_n", "3"),
        Para(
            "So the Legendre recurrence is aₙ₊₂ = (n − ℓ)(n + ℓ + 1)aₙ / "
            "((n + 2)(n + 1)). It steps by two, so as before the even and odd "
            "coefficients form two independent chains. And it has a "
            "remarkable property when ℓ is a whole number: the factor n − ℓ "
            "vanishes at n = ℓ, so the recurrence turns the coefficient of t^ℓ "
            "into a zero coefficient of t^(ℓ+2), and every coefficient after "
            "that in the same chain is zero too."
        ),
        Worked(
            "Legendre's equation at ℓ = 2",
            "Solve (1 − t²)y'' − 2ty' + 6y = 0 with y(0) = 1, y'(0) = 0.",
            (
                Step("Here ℓ(ℓ + 1) = 6, so ℓ = 2 and recurrence (3) becomes the "
                     "rule below.",
                     r"a_{n+2} = \frac{(n-2)(n+3)}{(n+2)(n+1)}\, a_n"),
                Step("Even chain: n = 0 gives a₂ = (−2)(3)/2 · a₀ = −3a₀; "
                     "n = 2 gives a₄ = 0 · a₂ = 0, and so a₆ = a₈ = ⋯ = 0. The "
                     "even solution is the polynomial 1 − 3t².",
                     r"a_2 = -3a_0, \qquad a_4 = a_6 = \cdots = 0"),
                Step("Odd chain: a₃ = −2a₁/3, a₅ = −a₁/5, a₇ = −4a₁/35, … — "
                     "it never stops. But y'(0) = 0 means a₁ = 0, so the whole "
                     "odd chain is zero, and a₀ = y(0) = 1."),
            ),
            equation="(1-t**2)*y'' - 2*t*y' + 6*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            answer="1 - 3*t**2", answer_latex=r"y(t) = 1 - 3t^{2}",
        ),
        Para(
            "Nothing went wrong in that example: the method produced a "
            "series, and the series had a tail of zeros. That is exactly why "
            "the answer can be checked by substitution — "
            "(1 − t²)(−6) − 2t(−6t) + 6(1 − 3t²) = 0 — whereas a series that "
            "does not stop can only ever be checked through some power, as "
            "the section on truncation explains."
        ),
    )),
    Section("Polynomial solutions: Legendre and Hermite", (
        Para(
            "Whole-number ℓ always makes one chain of Legendre's recurrence "
            "terminate: the even chain when ℓ is even, the odd chain when ℓ is "
            "odd. The polynomial that results, scaled so that its value at "
            "t = 1 is 1, is the Legendre polynomial of degree ℓ: P₀ = 1, "
            "P₁ = t, P₂ = (3t² − 1)/2, P₃ = (5t³ − 3t)/2. The solution just "
            "found is −2 times P₂. These polynomials are the "
            "solutions that stay finite at both ends of [−1, 1] — the other "
            "chain's series diverges at t = ±1 — and that is why they, and "
            "not the general solution, describe potentials on a sphere, "
            "where t = cos θ and the poles are t = ±1."
        ),
        Worked(
            "The odd chain at ℓ = 3",
            "Solve (1 − t²)y'' − 2ty' + 12y = 0 with y(0) = 0, y'(0) = 1.",
            (
                Step("ℓ(ℓ + 1) = 12 gives ℓ = 3, so the recurrence is "
                     "aₙ₊₂ = (n − 3)(n + 4)aₙ/((n + 2)(n + 1)).",
                     r"a_{n+2} = \frac{(n-3)(n+4)}{(n+2)(n+1)}\, a_n"),
                Step("y(0) = 0 makes a₀ = 0 and kills the even chain (which "
                     "at ℓ = 3 would not have stopped: a₂ = −6a₀, a₄ = 3a₀, "
                     "a₆ = 4a₀/5, …)."),
                Step("Odd chain from a₁ = 1: n = 1 gives a₃ = (−2)(5)/6 = "
                     "−5/3, and n = 3 gives a₅ = 0 · a₃ = 0. Everything after "
                     "is zero.",
                     r"y = t - \frac{5}{3}t^{3} = -\frac{2}{3}P_3(t), \quad "
                     r"P_3(t) = \frac{5t^{3} - 3t}{2}"),
            ),
            equation="(1-t**2)*y'' - 2*t*y' + 12*y = 0",
            conditions="y(0) = 0, y'(0) = 1",
            answer="t - 5*t**3/3", answer_latex=r"y(t) = t - \frac{5t^{3}}{3}",
        ),
        Para(
            "Hermite's equation y'' − 2ty' + 2my = 0 behaves the same way, "
            "with one difference. Its leading coefficient is 1, so every "
            "point is ordinary and every series solution converges for all "
            "t. Substituting and collecting the coefficient of tⁿ gives "
            "(n + 2)(n + 1)aₙ₊₂ − 2naₙ + 2maₙ = 0:"
        ),
        Display(r"a_{n+2} = \frac{2(n - m)}{(n+2)(n+1)}\, a_n", "4"),
        Worked(
            "Hermite's equation at m = 2",
            "Solve y'' − 2ty' + 4y = 0 with y(0) = 1, y'(0) = 0.",
            (
                Step("P = 1 never vanishes: every point is ordinary and the "
                     "guaranteed radius is infinite. Here 2m = 4, so m = 2 in "
                     "recurrence (4).",
                     r"a_{n+2} = \frac{2(n-2)}{(n+2)(n+1)}\, a_n"),
                Step("Even chain: a₂ = 2(−2)/2 · a₀ = −2a₀, and n = 2 gives "
                     "a₄ = 0, so the chain stops. The odd chain (a₃ = −a₁/3, "
                     "a₅ = −a₁/30, a₇ = −a₁/210, …) does not, but y'(0) = 0 "
                     "removes it."),
                Step("With a₀ = y(0) = 1 the solution is a quadratic. It is "
                     "−1/2 times the Hermite polynomial H₂(t) = 4t² − 2.",
                     r"y = 1 - 2t^{2}"),
            ),
            equation="y'' - 2*t*y' + 4*y = 0", conditions="y(0) = 1, y'(0) = 0",
            answer="1 - 2*t**2", answer_latex=r"y(t) = 1 - 2t^{2}",
        ),
        Para(
            "Set the two recurrences side by side. Legendre's numerator is "
            "(n − ℓ)(n + ℓ + 1) and Hermite's is 2(n − m); they generate "
            "different numbers and come from different physics, but they "
            "terminate for the same structural reason — a factor that "
            "vanishes at one index and passes the zero down its chain. The "
            "difference between the families is visible before any "
            "coefficient is computed: Legendre's leading coefficient vanishes "
            "at ±1, so its non-terminating chain is only guaranteed on "
            "|t| < 1, while Hermite's never vanishes and its chains converge "
            "on the whole line. The recurrence chapter has a figure in which "
            "ℓ moves between 0 and 6 and one chain of coefficients can be "
            "watched collapsing to zero whenever ℓ reaches a whole number."
        ),
        Para(
            "A third classical family works the same way. Chebyshev's "
            "equation (1 − t²)y'' − ty' + α²y = 0 has singular points ±1 like "
            "Legendre's, and its recurrence has a numerator that vanishes "
            "when the index reaches α, so for whole-number α one chain stops "
            "and gives a polynomial. The recurrence chapter works it out."
        ),
    )),
    Section("A series that sums to a known function", (
        Para(
            "Terminating series are exact because they are finite. A series "
            "that does not terminate can still be exact if it happens to sum "
            "to a function with a name, as the cosine series did. Legendre's "
            "equation at ℓ = 1 has one of each, and the second connects to "
            "the reduction-of-order chapter, which found it by a completely "
            "different route."
        ),
        Worked(
            "Legendre's second solution at ℓ = 1",
            "Solve (1 − t²)y'' − 2ty' + 2y = 0 with y(0) = −1, y'(0) = 0, and "
            "identify the sum of the series.",
            (
                Step("ℓ = 1, so recurrence (3) is aₙ₊₂ = (n − 1)(n + 2)aₙ / "
                     "((n + 2)(n + 1)), and the factor n + 2 cancels.",
                     r"a_{n+2} = \frac{n - 1}{n + 1}\, a_n"),
                Step("The odd chain stops at once (n = 1 gives a₃ = 0), and "
                     "y'(0) = 0 removes it anyway. The even chain from "
                     "a₀ = −1: a₂ = −a₀ = 1, a₄ = a₂/3 = 1/3, a₆ = 3a₄/5 = 1/5, "
                     "a₈ = 5a₆/7 = 1/7, and in general a₂ₖ = 1/(2k − 1).",
                     r"y = -1 + t^{2} + \frac{t^{4}}{3} + \frac{t^{6}}{5} + "
                     r"\frac{t^{8}}{7} + \cdots"),
                Step("Factor out t: t + t³/3 + t⁵/5 + ⋯ is the series of "
                     "(1/2)ln((1 + t)/(1 − t)), the inverse hyperbolic tangent, "
                     "valid for |t| < 1.",
                     r"y = -1 + t\left(t + \frac{t^{3}}{3} + \frac{t^{5}}{5} + "
                     r"\cdots\right)"),
            ),
            equation="(1-t**2)*y'' - 2*t*y' + 2*y = 0",
            conditions="y(0) = -1, y'(0) = 0",
            answer="t*log((1 + t)/(1 - t))/2 - 1",
            answer_latex=r"y(t) = \frac{t}{2}\ln\frac{1 + t}{1 - t} - 1",
        ),
        Para(
            "This is the function the reduction-of-order chapter built from "
            "y₁ = t with an integral and partial fractions. Here it came from "
            "a recurrence with no integration at all — and the series makes "
            "plain something the formula shows less directly: the radius. "
            "The series converges for |t| < 1 and no further — exactly the "
            "guaranteed radius, not a fraction more — because the function "
            "it sums blows up at t = ±1, the singular points of the "
            "equation, and a power series cannot run through a point where "
            "its sum is infinite. The recurrence chapter shows how to read "
            "that radius off the coefficients themselves."
        ),
        Plot(
            "Legendre's second solution and its partial sums",
            "y = (t/2)ln((1 + t)/(1 − t)) − 1, defined only on (−1, 1), "
            "against its series truncated after t², t⁶ and t²⁰. Inside, the "
            "partial sums close in — at t = 0.5 the truncation through t⁶ "
            "is already within 0.0007 — but slowly near the ends: at t = 0.9 "
            "even the truncation through t²⁰ is still 0.019 short, and the "
            "one through t⁶ is 0.19 short. Outside "
            "|t| < 1 every partial sum climbs away, because the series "
            "diverges there.",
            (Curve("t*log((1 + t)/(1 - t))/2 - 1", "exact"),
             Curve("-1 + t**2", "through t²"),
             Curve("-1 + t**2 + t**4/3 + t**6/5", "through t⁶"),
             Curve("-1 + t**2 + t**4/3 + t**6/5 + t**8/7 + t**10/9"
                   " + t**12/11 + t**14/13 + t**16/15 + t**18/17 + t**20/19",
                   "through t²⁰")),
            t=(-1.4, 1.4), ylim=(-1.5, 3.0),
        ),
    )),
    Section("Airy's equation: a series with no name", (
        Para(
            "Everything so far could have been done another way. Airy's "
            "equation cannot: no combination of elementary functions solves "
            "it, and the series is not a route to the answer but the answer "
            "itself. This is the situation the method exists for."
        ),
        Worked(
            "The coefficients of Airy's equation",
            "Find the recurrence for y'' − ty = 0 about t = 0, the first "
            "terms of two independent solutions, and the radius.",
            (
                Step("P = 1, so every point is ordinary and the series "
                     "converges for all t. y'' gives Σ (n + 2)(n + 1)aₙ₊₂tⁿ "
                     "from n = 0, and ty = Σ aₙtⁿ⁺¹ = Σ aₙ₋₁tⁿ from n = 1.",
                     r"2a_2 + \sum_{n=1}^{\infty}\left[(n+2)(n+1)a_{n+2} - "
                     r"a_{n-1}\right] t^{n} = 0"),
                Step("The t⁰ coefficient is 2a₂ alone, so a₂ = 0. For n ≥ 1 "
                     "the recurrence links each coefficient to the one three "
                     "places back.",
                     r"a_2 = 0, \qquad a_{n+2} = \frac{a_{n-1}}{(n+2)(n+1)}"),
                Step("Running it from a₀ and a₁: a₃ = a₀/6, a₄ = a₁/12, "
                     "a₅ = a₂/20 = 0, a₆ = a₀/180, a₇ = a₁/504, a₉ = a₀/12960. "
                     "Setting a₀ = 1, a₁ = 0 and then a₀ = 0, a₁ = 1 gives two "
                     "independent solutions. (Why a₅, a₈, a₁₁, … all vanish is "
                     "the recurrence chapter's first piece of pattern-reading.)",
                     r"y_1 = 1 + \frac{t^{3}}{6} + \frac{t^{6}}{180} + "
                     r"\frac{t^{9}}{12960} + \cdots, \quad y_2 = t + "
                     r"\frac{t^{4}}{12} + \frac{t^{7}}{504} + \cdots"),
            ),
            answer_latex=r"y = a_0\,y_1(t) + a_1\,y_2(t), \qquad \rho = \infty",
        ),
        Para(
            "The rule generates as many terms as anyone asks for, which is "
            "the sense in which the recurrence, not any list of terms it "
            "happens to produce, is the answer."
        ),
        Para(
            "The functions y₁ and y₂ are as well defined as cos t and sin t, "
            "which are also, in the end, defined by their series. The "
            "standard Airy function Ai, the one tabulated and built into "
            "numerical libraries, is the particular combination "
            "Ai(t) = Ai(0)y₁(t) + Ai'(0)y₂(t), with Ai(0) ≈ 0.3550 and "
            "Ai'(0) ≈ −0.2588 — and summing the two series with those "
            "constants reproduces library values, for instance "
            "Ai(1) ≈ 0.1353. Having a name is a matter of convention; the "
            "series is the substance."
        ),
        Plot(
            "Airy's y₁ from its recurrence",
            "Truncations of y₁ = 1 + t³/6 + t⁶/180 + ⋯ after t⁶, t¹² and t²⁴, "
            "against the truncation after t⁶⁰, which agrees with the full "
            "series to within 0.01 everywhere on this range. For t > 0 the "
            "solution grows; for t < 0 the equation is y'' = −|t|y, a spring "
            "that stiffens with distance, and the solution oscillates ever "
            "faster. Each truncation follows it only so far left: within "
            "0.05 down to about t = −2, −3 and −4.6 respectively. The "
            "radius is infinite, so more terms always reach further.",
            (Curve("1 + t**3/6 + t**6/180", "through t⁶"),
             Curve("1 + t**3/6 + t**6/180 + t**9/12960 + t**12/1710720",
                   "through t¹²"),
             Curve("1 + t**3/6 + t**6/180 + t**9/12960 + t**12/1710720"
                   " + t**15/359251200 + t**18/109930867200"
                   " + t**21/46170964224000 + t**24/25486372251648000",
                   "through t²⁴"),
             Curve("1 + t**3/6 + t**6/180 + t**9/12960 + t**12/1710720"
                   " + t**15/359251200 + t**18/109930867200 + t**21/46170964224000"
                   " + t**24/25486372251648000 + t**27/17891433320656896000"
                   " + t**30/15565546988971499520000"
                   " + t**33/16437217620353903493120000"
                   " + t**36/20710894201645918401331200000"
                   " + t**39/30693545206839251070772838400000"
                   " + t**42/52854284846177190343870827724800000"
                   " + t**45/104651483995430836880864238895104000000"
                   " + t**48/236093747893691968003229722947354624000000"
                   " + t**51/602039057128914518408235793515754291200000000"
                   " + t**54/1723035781502953351684370841042088781414400000000"
                   " + t**57/5499930214557427098576511724606347390274764800000000"
                   " + t**60/19469752959533291928960851505106469761572667392000000000",
                   "through t⁶⁰")),
            t=(-8.0, 2.0), ylim=(-2.0, 3.0),
        ),
    )),
    Section("Other centres, other coefficients", (
        Para(
            "Every series so far has been centred at 0, and every coefficient "
            "of every equation has been a polynomial in t. Neither is needed. "
            "The existence theorem is stated for any ordinary point t₀ and "
            "for any p and q analytic there, and the method follows it — at "
            "the price of some extra algebra before the first substitution."
        ),
        Worked(
            "Airy's equation about t₀ = 1",
            "Find the recurrence and the first terms of two independent "
            "solutions of y'' − ty = 0 in powers of t − 1.",
            (
                Step("Put s = t − 1. Then t = s + 1, and since ds/dt = 1 the "
                     "derivatives with respect to s and t agree. The "
                     "coefficient of y has to be rewritten in powers of s "
                     "before anything is substituted.",
                     r"\frac{d^{2}y}{ds^{2}} - (s + 1)\,y = 0"),
                Step("Substitute y = Σ aₙsⁿ. The second derivative shifts to "
                     "Σ (n + 2)(n + 1)aₙ₊₂sⁿ from n = 0; y contributes "
                     "Σ aₙsⁿ from n = 0; and sy = Σ aₙ₋₁sⁿ from n = 1. The "
                     "power s⁰ gives 2a₂ − a₀ = 0, and every higher power "
                     "gives a recurrence with three terms where the series "
                     "about 0 had two.",
                     r"a_2 = \frac{a_0}{2}, \qquad a_{n+2} = "
                     r"\frac{a_n + a_{n-1}}{(n+2)(n+1)} \quad (n \geq 1)"),
                Step("Running it: a₃ = (a₁ + a₀)/6, a₄ = (a₂ + a₁)/12 = "
                     "a₀/24 + a₁/12, a₅ = (a₃ + a₂)/20 = a₀/30 + a₁/120. Each "
                     "coefficient now mixes a₀ and a₁, so there are no "
                     "separate chains, but a₀ = 1, a₁ = 0 and a₀ = 0, a₁ = 1 "
                     "still give two independent solutions.",
                     r"y_1 = 1 + \frac{s^{2}}{2} + \frac{s^{3}}{6} + "
                     r"\frac{s^{4}}{24} + \cdots, \quad y_2 = s + "
                     r"\frac{s^{3}}{6} + \frac{s^{4}}{12} + \cdots"),
                Step("P = 1 still never vanishes, so d is infinite and both "
                     "series converge for every t. As a check, Ai(t) is "
                     "Ai(1)y₁ + Ai'(1)y₂ with Ai(1) ≈ 0.1353 and "
                     "Ai'(1) ≈ −0.1591, and its Taylor coefficient of x³ is "
                     "(0.1353 − 0.1591)/6 ≈ −0.0040, as a library expansion "
                     "of Ai about 1 confirms."),
            ),
            answer_latex=r"y = a_0\,y_1 + a_1\,y_2, \quad s = t - 1, "
                         r"\quad \rho = \infty",
        ),
        Para(
            "The shift is the whole difference, and it is not cosmetic: a "
            "coefficient that is a single term in t becomes two terms in s, "
            "and the recurrence grows to match, with each coefficient now "
            "depending on both free constants. When the centre is not 0, "
            "the cleanest course is to shift first and only then follow the "
            "six steps."
        ),
        Para(
            "A coefficient that is not a polynomial needs its own series "
            "before it can be multiplied by Σ aₙtⁿ, and the product of two "
            "series is laborious. When only the first few terms are wanted, "
            "the route through formula (1) is quicker: differentiate the "
            "equation and evaluate at the centre."
        ),
        Worked(
            "A coefficient that is an exponential",
            "Find the series solution of y'' + eᵗy = 0 with y(0) = 1, "
            "y'(0) = 0 through t⁵, and its guaranteed radius.",
            (
                Step("p = 0 and q = eᵗ are analytic at every point, so every "
                     "point is ordinary, there is no singular point anywhere "
                     "and d is infinite: the series converges for all t."),
                Step("a₀ = 1 and a₁ = 0. From the equation, y'' = −eᵗy, so "
                     "y''(0) = −1 and a₂ = −1/2.",
                     r"y''(0) = -e^{0}\,y(0) = -1"),
                Step("Differentiate: y''' = −eᵗy − eᵗy', so y'''(0) = −1 and "
                     "a₃ = −1/6. Again: y'''' = −eᵗy − 2eᵗy' − eᵗy'', so "
                     "y''''(0) = −1 − 0 + 1 = 0 and a₄ = 0. One more "
                     "derivative gives y⁽⁵⁾(0) = 3 and a₅ = 3/120 = 1/40.",
                     r"y = 1 - \frac{t^{2}}{2} - \frac{t^{3}}{6} + "
                     r"\frac{t^{5}}{40} + \cdots"),
            ),
            answer_latex=r"y = 1 - \frac{t^{2}}{2} - \frac{t^{3}}{6} + "
                         r"0\cdot t^{4} + \frac{t^{5}}{40} + \cdots",
        ),
    )),
    Section("Truncation is not a mistake", (
        Para(
            "Any finite number of terms is an approximation, and it is wrong "
            "away from the centre. But the series is not an approximation, "
            "and neither is the recurrence that generates it. Truncating is "
            "a choice made when a number is wanted, and it should not be "
            "confused with the answer. What a truncation can honestly claim "
            "is agreement with the solution up to some power."
        ),
        Box(
            "definition", "Correct through t^N",
            "A polynomial is correct through t^N if its coefficients of "
            "t⁰, t¹, …, t^N are those of the solution's series. Equivalently, "
            "it differs from the solution by a series whose lowest power is "
            "t^(N+1) or higher.",
        ),
        Para(
            "Substituting a truncation back into the equation does not give "
            "zero, and it should not. Write the truncation as the solution "
            "minus its missing tail. The equation is linear and the solution "
            "gives zero, so what is left — the residual — is what the "
            "equation does to the tail, with the sign changed. The tail "
            "starts at t^(N+1), two derivatives bring it down to t^(N−1), and "
            "nothing lower can appear."
        ),
        Box(
            "theorem", "The residual of a truncation",
            "If a polynomial is correct through t^N for a second-order "
            "equation P y'' + Q y' + R y = 0 with polynomial coefficients, "
            "substituting it leaves a residual with no power of t below "
            "t^(N−1). A residual with a lower power means a coefficient was "
            "computed wrongly.",
            r"P y_N'' + Q y_N' + R y_N = O\!\left(t^{N-1}\right)",
        ),
        Para(
            "For y'' + y = 0, the truncation C₁(1 − t²/2 + t⁴/24) + "
            "C₂(t − t³/6) is correct through t⁴ — the next terms of the true "
            "series are C₂t⁵/120 and −C₁t⁶/720 — and substituting it leaves "
            "t³(C₁t − 4C₂)/24, which starts at t³ = t^(N−1) just as the theorem "
            "predicts. That residual is the truncation error, not a mistake. "
            "A real mistake looks different: with the sign of a₂ wrong, "
            "C₁(1 + t²/2) leaves C₁(2 + t²/2), with a constant term. Low "
            "powers in the residual mean a wrong coefficient; high powers "
            "mean only that the writing stopped."
        ),
        Worked(
            "Checking a truncation",
            "Show that 1 + t³/6 is correct through t⁵ for Airy's equation "
            "y'' − ty = 0, find its residual, and show how the residual "
            "exposes the slip a₃ = a₀/3.",
            (
                Step("From the Airy recurrence with a₀ = 1, a₁ = 0: a₂ = 0, "
                     "a₃ = 1/6, a₄ = a₅ = 0, and the first missing term is "
                     "a₆t⁶ = t⁶/180. So 1 + t³/6 is correct through t⁵."),
                Step("Substitute: y'' = t and ty = t + t⁴/6, so the residual "
                     "begins at t⁴ = t^(N−1) with N = 5. It is exactly "
                     "−(6·5)(1/180)t⁴, the effect of the missing t⁶/180.",
                     r"y'' - ty = t - t - \frac{t^{4}}{6} = -\frac{t^{4}}{6}"),
                Step("With the slip, 1 + t³/3 gives y'' = 2t and a residual "
                     "with a t¹ term — far below t⁴, and the signal that a "
                     "coefficient, not the truncation, is wrong.",
                     r"2t - t - \frac{t^{4}}{3} = t - \frac{t^{4}}{3}"),
            ),
            answer_latex=r"y'' - ty = -\frac{t^{4}}{6} \quad (\text{correct "
                         r"through } t^{5})",
        ),
        Para(
            "This is also why the course's checked answers in this unit are "
            "all exact — polynomials from terminating series, or series "
            "whose sums have names. A grader that substitutes and simplifies "
            "to zero must reject every truncation, however correct, because "
            "a truncation leaves its residual behind. When the app narrates "
            "a series that does not stop, it checks the truncation the way "
            "this section does: by the lowest power left in the residual."
        ),
    )),
    Section("Where the method stops", (
        Para(
            "The existence theorem says nothing at a singular point, and "
            "there a power series really can fail. Try one on the "
            "Cauchy–Euler equation 4t²y'' + 4ty' − y = 0. Each term maps tⁿ "
            "to a multiple of tⁿ, so the coefficient of tⁿ after substitution "
            "is [4n(n − 1) + 4n − 1]aₙ = (4n² − 1)aₙ. Since 4n² − 1 is never "
            "zero for a whole number n, every aₙ is zero: the only power "
            "series solution is y = 0. The Cauchy–Euler chapter explains "
            "why. The indicial equation 4r(r − 1) + 4r − 1 = 4r² − 1 = 0 has "
            "roots ±1/2, the solutions are t^(1/2) and t^(−1/2), and neither "
            "is a power series."
        ),
        Para(
            "Sometimes the failure is partial. For t²y'' + ty' − y = 0 the "
            "same calculation gives (n² − 1)aₙ = 0, so a₁ survives and the "
            "series method finds y = t — one solution of two. The other, "
            "1/t, which the reduction-of-order chapter found, is not analytic at 0, and no "
            "choice of coefficients can "
            "produce it. At a singular point it is frequently the second "
            "solution — the one a physical problem usually discards for "
            "being infinite there — that has no power series."
        ),
        Para(
            "Bessel's equation of order 1/2, t²y'' + ty' + (t² − 1/4)y = 0, "
            "is the model case: its solutions are sin t/√t and cos t/√t, and "
            "the first begins √t − t^(5/2)/6 + ⋯, a power series multiplied by "
            "√t. That shape — a power t^r in front of an ordinary series — is "
            "the whole of the Frobenius method, and the Frobenius chapter "
            "shows how r is found: by the same indicial equation as the "
            "Cauchy–Euler chapter, because near a regular singular point the "
            "equation looks like a Cauchy–Euler one."
        ),
        Display(r"y = t^{r}\sum_{n=0}^{\infty} a_n t^{n}, \qquad a_0 \neq 0", "5"),
    )),
    Section("Summary", (
        Para(
            "When no formula exists, build the solution as a power series "
            "y = Σ aₙ(t − t₀)ⁿ. First check that t₀ is ordinary — with "
            "polynomial coefficients and common factors cancelled, that the "
            "leading coefficient P(t₀) ≠ 0 — and find the guaranteed radius, "
            "the distance from t₀ to the nearest root of P in the complex "
            "plane. Then substitute, re-index so every sum runs over the same "
            "power, and set each coefficient to zero; the identity theorem "
            "licenses that step, and it produces a recurrence. Two "
            "coefficients stay free, and they are y(t₀) and y'(t₀), so "
            "initial conditions go straight in. Sometimes the recurrence "
            "terminates and the answer is a polynomial — the Legendre and "
            "Hermite polynomials arise exactly this way; sometimes the series "
            "sums to a familiar function; usually, as for Airy's equation, it "
            "is simply the answer. A truncation correct through t^N leaves a "
            "residual with nothing below t^(N−1), and that, not a residual of "
            "zero, is the honest way to check it. At a singular point a plain series "
            "may find only one solution or none, and that is where the "
            "Frobenius chapter takes over."
        ),
    )),
)


RECURRENCE = (
    Section("From an equation in sums to a rule", (
        Para(
            "The power-series chapter made one assumption and drew one "
            "consequence from it. The assumption was that near an ordinary "
            "point the solution is a power series y = ∑ aₙtⁿ; the consequence "
            "was that the two free coefficients a₀ and a₁ are the two initial "
            "conditions. Between those two facts lies the part of the method "
            "that does the real work: substituting the series into the "
            "equation and turning what comes back into a rule for every other "
            "coefficient. That rule is the subject of this chapter."
        ),
        Para(
            "What comes back from the substitution is not yet usable. Each "
            "term of the equation contributes its own infinite sum — one from "
            "y'', one from y', one from y, more if the coefficients are "
            "polynomials with several terms — and those sums arrive with "
            "different powers of t and different starting indices. Nothing "
            "can be compared with anything until they are rewritten over a "
            "common power. The difficulty is bookkeeping, not mathematics, "
            "but it is where almost every error in this topic is made, so it "
            "gets a section of its own."
        ),
        Para(
            "Once the sums are aligned, the identity theorem does everything: "
            "a power series that is zero on an interval has every coefficient "
            "zero. That converts one differential equation into infinitely "
            "many algebraic ones, each linking a coefficient to earlier ones. "
            "Read together they form a *recurrence relation*, and the "
            "recurrence — not any list of numbers it produces — is the "
            "answer. It generates as many coefficients as anyone wants, it "
            "often shows a pattern that a printed list hides, and in the "
            "best cases it can be solved outright, giving a closed form or "
            "a polynomial."
        ),
        Para(
            "There is a second dividend. Before a single coefficient is "
            "computed, the equation itself says how far the series will be "
            "good for: at least as far as the nearest point, real or "
            "complex, where its leading coefficient vanishes. The power-series "
            "chapter stated that guarantee; the last third of this chapter "
            "puts it to work, shows the recurrence confirming it, and asks "
            "what a truncated series can and cannot be trusted to do inside "
            "it."
        ),
    )),
    Section("Shifting the index", (
        Para(
            "Take y = ∑ aₙtⁿ. Differentiating term by term, which is allowed "
            "inside the interval of convergence, gives the two series below. "
            "The starting indices change because the constant term "
            "differentiates to zero, and the term a₁t is killed by the "
            "second derivative; writing the sums from n = 1 and n = 2 "
            "records that, although starting them at 0 would only add zero "
            "terms."
        ),
        Display(r"y' = \sum_{n=1}^{\infty} n\,a_n t^{n-1}, \qquad "
                r"y'' = \sum_{n=2}^{\infty} n(n-1)\,a_n t^{n-2}", "1"),
        Para(
            "Three operations move exponents around. Differentiating lowers "
            "the exponent by one. Multiplying by t raises it by one, and "
            "multiplying by t² raises it by two. So t·y' and t²·y'' are "
            "already in the power tⁿ — the two shifts cancel — while a bare "
            "y'' is two powers low and a product such as t·y is one power "
            "high. Before collecting, decide on a common power (tⁿ is the "
            "usual choice) and rename the summation variable in every sum "
            "that is not already in it."
        ),
        Display(r"\sum_{n=2}^{\infty} n(n-1)a_n t^{n-2} = "
                r"\sum_{k=0}^{\infty} (k+2)(k+1)a_{k+2} t^{k}", "2"),
        Para(
            "Equation (2) is the substitution k = n − 2, which is only a "
            "renaming of the variable of summation: the same terms are added "
            "in the same order. Every n becomes k + 2, so the exponent n − 2 "
            "becomes k, the coefficient n(n − 1)aₙ becomes (k + 2)(k + 1)aₖ₊₂, "
            "and the lower limit n = 2 becomes k = 0. Afterwards the letter "
            "k can be renamed n again, since a summation variable is a dummy."
        ),
        Box(
            "warning", "Shift the limit with the exponent",
            "A shift moves three things at once: the exponent, the subscript "
            "and the starting index. Changing the first two and leaving the "
            "lower limit where it was either adds terms that were never in "
            "the sum or drops terms that were, and the error surfaces later "
            "as a wrong value for a₂ or a₃ — far from where it was made.",
        ),
        Para(
            "After the shift the sums may still start at different indices. "
            "In Airy's equation y'' − ty = 0, for example, the shifted y'' "
            "starts at n = 0, while ty, rewritten as the sum of a_(n−1)·tⁿ, "
            "starts at n = 1. The cure is "
            "to peel off the low terms of the sum that starts earlier and "
            "write them separately, so that what remains is one sum over a "
            "common range. Those peeled-off terms are not a nuisance; they "
            "carry equations of their own, and the Airy section shows one of "
            "them deciding a coefficient outright."
        ),
    )),
    Section("A series that vanishes has no coefficients", (
        Para(
            "Once every sum runs over tⁿ and over the same range, the "
            "equation reads ∑ cₙtⁿ = 0, where each cₙ is a small combination "
            "of the unknown coefficients. By the identity theorem of the "
            "power-series chapter, ∑ cₙtⁿ = 0 on an interval forces every "
            "cₙ = 0."
        ),
        Para(
            "That theorem is what turns the series method into arithmetic. "
            "One equation that has to hold for all t becomes a list of "
            "equations c₀ = 0, c₁ = 0, c₂ = 0, …, each involving only a few "
            "coefficients. For an equation P y'' + Q y' + R y = 0 whose "
            "coefficients are polynomials, the n-th of them always contains "
            "aₙ₊₂ with the factor (n + 2)(n + 1)P(0), which is non-zero at "
            "an ordinary point — so each equation can be solved for aₙ₊₂. "
            "That is exactly where the ordinary-point condition of the "
            "previous chapter is used."
        ),
        Box(
            "definition", "Recurrence relation",
            "A recurrence relation for the coefficients is a formula that "
            "expresses the highest-index coefficient (aₙ₊₂ for a second-order "
            "equation, aₙ₊₁ for a first-order one), for every n from some "
            "point on, in terms of coefficients with smaller indices. It is "
            "a two-term recurrence if only one earlier coefficient appears, "
            "and the gap between the two indices is its step; with two "
            "earlier coefficients it is a three-term recurrence.",
            r"a_{n+2} = F(n)\,a_{n} \quad \text{or} \quad "
            r"a_{n+2} = F(n)\,a_{n} + G(n)\,a_{n-1}",
        ),
    )),
    Section("Reading off the recurrence", (
        Para(
            "The procedure is the same every time: find the radius, "
            "substitute, shift, peel off any low terms, collect the "
            "coefficient of tⁿ, set it to zero and solve for the "
            "highest-index coefficient. The power-series chapter ran it on "
            "y'' + y = 0 and recovered cosine and sine; the first example here "
            "changes one sign, so that every step can again be checked "
            "against the second-order unit's characteristic roots, which for "
            "y'' − y = 0 are ±1."
        ),
        Worked(
            "The exponential pair by series",
            "Find the recurrence for y'' − y = 0 about t = 0, solve it, and "
            "find the solution with y(0) = 2, y'(0) = 3.",
            (
                Step("The leading coefficient is 1 and never vanishes, so "
                     "every point is ordinary and the series will converge "
                     "for every t.",
                     r"\rho = \infty"),
                Step("Substitute and shift y'' with (2). Both sums now run over "
                     "tⁿ from n = 0, so they combine at once.",
                     r"\sum_{n=0}^{\infty}\left[(n+2)(n+1)a_{n+2} - a_n\right]"
                     r"t^{n} = 0"),
                Step("By the identity theorem each bracket is zero, which is "
                     "the recurrence. It has step two, so the even "
                     "coefficients come from a₀ and the odd ones from a₁.",
                     r"a_{n+2} = \frac{a_n}{(n+2)(n+1)}"),
                Step("Apply it repeatedly: a₂ = a₀/2, a₄ = a₂/12 = a₀/24, "
                     "a₆ = a₀/720, and in general each step divides by the "
                     "next two integers. Likewise a₃ = a₁/6, a₅ = a₁/120. It "
                     "is the recurrence of y'' + y = 0 without the alternating "
                     "sign.",
                     r"a_{2k} = \frac{a_0}{(2k)!}, \qquad "
                     r"a_{2k+1} = \frac{a_1}{(2k+1)!}"),
                Step("These are the Maclaurin coefficients of cosh t and "
                     "sinh t, so the series sums to a₀cosh t + a₁sinh t — the "
                     "combinations (eᵗ + e⁻ᵗ)/2 and (eᵗ − e⁻ᵗ)/2 of the "
                     "characteristic-root solutions. With a₀ = y(0) = 2 and "
                     "a₁ = y'(0) = 3:",
                     r"y = 2\cosh t + 3\sinh t"),
            ),
            equation="y'' - y = 0", conditions="y(0) = 2, y'(0) = 3",
            answer="2*cosh(t) + 3*sinh(t)",
            answer_latex=r"y(t) = 2\cosh t + 3\sinh t",
        ),
        Para(
            "Notice what was and was not used. Nowhere did the computation "
            "need to know that cosh and sinh exist; it produced their "
            "coefficients from the equation alone, and the recognition came "
            "afterwards. The series method also hands over the pair that "
            "the initial conditions prefer: cosh t and sinh t, with values "
            "1, 0 and 0, 1 at the origin, rather than eᵗ and e⁻ᵗ. For an "
            "equation whose solutions have no names the computation is "
            "identical and only the recognition is missing."
        ),
        Para(
            "Nothing about the method is special to second order. A "
            "first-order equation has one free coefficient instead of two, "
            "and the lowest powers of the shifted sums often carry equations "
            "of their own. The power-series chapter's y' = 2ty had one such "
            "peeled-off term, which made a₁ = 0; raising the power of t in "
            "the coefficient by one gives two."
        ),
        Worked(
            "A first-order equation, and two peeled-off terms",
            "Solve y' = t²y with y(0) = 1 by a power series about 0.",
            (
                Step("Write y' − t²y = 0. The derivative is one power low and "
                     "t²y is two powers high, so shift both into tⁿ: "
                     "y' becomes a sum of (n + 1)aₙ₊₁tⁿ from n = 0, and t²y a "
                     "sum of a_(n−2)·tⁿ from n = 2.",
                     r"\sum_{n=0}^{\infty}(n+1)a_{n+1}t^{n} - "
                     r"\sum_{n=2}^{\infty}a_{n-2}t^{n} = 0"),
                Step("The first sum starts two indices earlier. Its n = 0 and "
                     "n = 1 terms, a₁ and 2a₂, stand alone, and the identity "
                     "theorem makes both zero. The rest gives the recurrence "
                     "for n ≥ 2, a two-term recurrence of step 3.",
                     r"a_1 = a_2 = 0, \qquad a_{n+1} = \frac{a_{n-2}}{n+1}"),
                Step("The step is three, so a₁ = a₂ = 0 makes every "
                     "coefficient zero except a₀, a₃, a₆, …. Those are "
                     "a₃ = a₀/3, a₆ = a₃/6 = a₀/18, a₉ = a₆/9 = a₀/162: each "
                     "step divides by 3k, and so a₃ₖ = a₀/(3ᵏk!).",
                     r"y = a_0\sum_{k=0}^{\infty}\frac{1}{k!}"
                     r"\left(\frac{t^{3}}{3}\right)^{k} = a_0\,e^{t^{3}/3}"),
                Step("y(0) = a₀ = 1. The separable-equations method of the "
                     "first-order unit gives the same answer in one line, "
                     "which is a useful check that the bookkeeping was "
                     "right."),
            ),
            equation="y' = t**2*y", conditions="y(0) = 1",
            answer="exp(t**3/3)", answer_latex=r"y(t) = e^{t^{3}/3}",
        ),
    )),
    Section("Recurrences that skip: Airy's equation", (
        Para(
            "The examples so far had closed forms waiting at the end. "
            "Airy's equation y'' = ty does not: no combination of "
            "exponentials, sines, powers or logarithms solves it. It is "
            "the standard first example of an equation whose solutions are "
            "new functions, and the recurrence is the only description of "
            "them that the method offers. The power-series chapter derived "
            "its recurrence and the first few terms and left one question "
            "open — why a₅, a₈, a₁₁, … are all zero. The answer is the same "
            "step of three that y' = t²y just showed, and it is where the "
            "structure of a recurrence becomes more informative than its "
            "numbers."
        ),
        Worked(
            "Airy's equation",
            "Find the recurrence for y'' − ty = 0 about t = 0 and the "
            "coefficients through a₁₀ in terms of a₀ and a₁.",
            (
                Step("P = 1 never vanishes, so every point is ordinary and the "
                     "series converges for every t — even though, as will "
                     "appear, its sum has no closed form. Converging "
                     "everywhere and having a formula are different "
                     "questions.",
                     r"\rho = \infty"),
                Step("Shift y'' with (2). Multiplying by t raises each power "
                     "by one, so ty, renamed onto tⁿ, starts at n = 1. Peel "
                     "off the n = 0 term of the first sum.",
                     r"t\,y = \sum_{n=1}^{\infty} a_{n-1}t^{n}, \qquad "
                     r"2a_2 + \sum_{n=1}^{\infty}\left[(n+2)(n+1)a_{n+2} "
                     r"- a_{n-1}\right]t^{n} = 0"),
                Step("The peeled-off term gives 2a₂ = 0, so a₂ = 0 — a "
                     "coefficient decided by the bookkeeping, not left free. "
                     "The bracket gives the recurrence for n ≥ 1.",
                     r"a_{n+2} = \frac{a_{n-1}}{(n+2)(n+1)}"),
                Step("The step is three, not two. So the coefficients fall "
                     "into three chains: a₀, a₃, a₆, … starting from a₀; "
                     "a₁, a₄, a₇, … from a₁; and a₂, a₅, a₈, … from a₂ = 0, "
                     "which therefore stays zero for ever.",
                     r"a_2 = a_5 = a_8 = \cdots = 0"),
                Step("Running the other two chains: a₃ = a₀/6, a₆ = a₀/180, "
                     "a₉ = a₀/12960, and a₄ = a₁/12, a₇ = a₁/504, "
                     "a₁₀ = a₁/45360.",
                     r"y = a_0\left(1 + \frac{t^{3}}{6} + \frac{t^{6}}{180} "
                     r"+ \cdots\right) + a_1\left(t + \frac{t^{4}}{12} "
                     r"+ \frac{t^{7}}{504} + \cdots\right)"),
            ),
        ),
        Para(
            "A list of these numbers shows a scattering of zeros with no "
            "evident cause. The recurrence shows why they are there and "
            "which ones come next: each coefficient is tied to the one three "
            "places back, and one of the three chains begins with a zero. "
            "Each chain can even be written as a product — the a₀ chain is "
            "a₃ₖ = a₀ / [(2·3)(5·6)⋯((3k − 1)(3k))] — which is as close to a "
            "formula as these functions come."
        ),
        Para(
            "The step of the recurrence is the difference between the "
            "exponents that meet. y'' lowers the power by two and t·y raises "
            "it by one, so they differ by three — as y' and t²y did. For "
            "y'' ± y = 0 the difference was two, and for a coefficient such "
            "as 1 + t the two parts of R·y arrive at different powers and the "
            "recurrence acquires a third term. Thus y'' − (1 + t)y = 0 gives "
            "(n + 2)(n + 1)aₙ₊₂ = aₙ + aₙ₋₁ for n ≥ 1, with a₂ = a₀/2, "
            "a₃ = (a₀ + a₁)/6 and a₄ = a₀/24 + a₁/12 — the numbers the "
            "power-series chapter found for Airy's equation about t₀ = 1, "
            "which after the shift s = t − 1 is exactly this equation in s. "
            "A three-term "
            "recurrence still generates every coefficient, but its chains "
            "mix, and it rarely has a solution in closed form."
        ),
    )),
    Section("Solving a two-term recurrence", (
        Para(
            "A two-term recurrence of step 2, aₙ₊₂ = F(n)aₙ, can always be "
            "solved, in the sense that the coefficients can be written as "
            "products. Starting from a₀ and applying it k times gives the "
            "product below, and the same with odd indices starting from a₁. "
            "Whether the product simplifies into something recognisable is a "
            "matter of luck — but whether it ever becomes zero is not, and "
            "that question runs through the rest of this section and the "
            "next."
        ),
        Display(r"a_{2k} = F(2k-2)\,F(2k-4)\cdots F(2)\,F(0)\;a_0", "3"),
        Para(
            "For y'' + y = 0, F(n) = −1/((n + 2)(n + 1)) and the product is "
            "(−1)ᵏ/(2k)!. For y'' + ty' + y = 0 the recurrence is "
            "aₙ₊₂ = −aₙ/(n + 2), the product is (−1)ᵏ/(2·4·6⋯2k) = "
            "(−1)ᵏ/(2ᵏk!), and the even solution is e^(−t²/2). Hermite's "
            "equation y'' − 2ty' + 2my = 0, which describes the quantum "
            "harmonic oscillator, shows the third possibility: a factor of F "
            "that vanishes. The power-series chapter derived its recurrence, "
            "aₙ₊₂ = 2(n − m)aₙ/((n + 2)(n + 1)), and solved the case m = 2; "
            "here is the next even case."
        ),
        Worked(
            "Hermite's equation with a terminating branch",
            "For y'' − 2ty' + 8y = 0, find the recurrence and the solution "
            "with y(0) = 1, y'(0) = 0.",
            (
                Step("P = 1 never vanishes: every point is ordinary and the "
                     "series converges for every t. Here 2m = 8, so m = 4.",
                     r"\rho = \infty"),
                Step("y'' shifts as in (2); t·y' = ∑ naₙtⁿ is already in tⁿ "
                     "and starts harmlessly at n = 0. Collecting the "
                     "coefficient of tⁿ:",
                     r"(n+2)(n+1)a_{n+2} - 2n\,a_n + 8a_n = 0"),
                Step("Solve for the highest coefficient. The numerator has the "
                     "factor n − 4.",
                     r"a_{n+2} = \frac{2(n-4)}{(n+2)(n+1)}\,a_n"),
                Step("y'(0) = a₁ = 0 makes every odd coefficient zero. On the "
                     "even branch, with a₀ = 1: a₂ = 2(−4)/2 = −4, then "
                     "a₄ = 2(−2)(−4)/12 = 4/3, then a₆ = 2(0)a₄/30 = 0, and "
                     "every later even coefficient inherits the zero.",
                     r"a_0 = 1,\ a_2 = -4,\ a_4 = \frac{4}{3},\ "
                     r"a_6 = a_8 = \cdots = 0"),
                Step("The series is a polynomial, and therefore an exact "
                     "solution with nothing truncated. It is the Hermite "
                     "polynomial H₄(t) = 16t⁴ − 48t² + 12 divided by 12.",
                     r"y = 1 - 4t^{2} + \frac{4}{3}t^{4}"),
            ),
            equation="y'' - 2*t*y' + 8*y = 0", conditions="y(0) = 1, y'(0) = 0",
            answer="1 - 4*t**2 + 4*t**4/3",
            answer_latex=r"y(t) = 1 - 4t^{2} + \frac{4}{3}t^{4}",
        ),
        Para(
            "When m is a whole number, the branch of the same parity as m "
            "stops after the term in tᵐ; the other branch runs on for ever. "
            "That one observation is the whole theory of Hermite polynomials "
            "as far as this course needs it, and the same mechanism, applied "
            "to Legendre's equation, is the subject of the next section."
        ),
    )),
    Section("When the rule stops: Legendre's equation", (
        Para(
            "Legendre's equation (1 − t²)y'' − 2ty' + ℓ(ℓ + 1)y = 0 arises "
            "when Laplace's equation is separated in spherical coordinates, "
            "with t = cos θ. It is the equation drawn in this chapter's "
            "figure. The power-series chapter derived its recurrence — only "
            "the bare y'' needs shifting, since −t²y'' and −2ty' are already "
            "in tⁿ — and it is repeated here because the rest of the chapter "
            "leans on it. Here ℓ ≥ 0 need not be a whole number."
        ),
        Display(r"a_{n+2} = \frac{(n-\ell)(n+\ell+1)}{(n+2)(n+1)}\,a_n", "4"),
        Box(
            "theorem", "Termination",
            "Let aₙ₊₂ = F(n)aₙ be a two-term recurrence of step 2. If the "
            "numerator of F vanishes at n = j, then aⱼ₊₂ = 0, and so are "
            "aⱼ₊₄, aⱼ₊₆, …: the branch containing aⱼ is a polynomial of "
            "degree j (if aⱼ ≠ 0). For Legendre's equation this happens "
            "exactly when ℓ is a whole number, at j = ℓ.",
            r"\ell \in \{0, 1, 2, \ldots\} \;\Longrightarrow\; "
            r"a_{\ell+2} = a_{\ell+4} = \cdots = 0",
        ),
        Para(
            "The proof is one line: aⱼ₊₂ = F(j)aⱼ = 0, and each later "
            "coefficient of that parity is a multiple of the one two places "
            "back. Only one parity is affected, because the other branch "
            "never visits n = j. So at whole-number ℓ Legendre's equation has "
            "one polynomial solution, of degree ℓ, and one genuinely infinite "
            "series — a fact the figure at the end of this section shows "
            "directly. The power-series chapter worked the polynomials at "
            "ℓ = 2 and ℓ = 3, and at ℓ = 1 it summed the infinite branch, "
            "(t/2)ln((1 + t)/(1 − t)) − 1. The polynomial partner of that "
            "solution is the smallest non-constant case, and quicker still."
        ),
        Worked(
            "A branch that stops at once",
            "Solve (1 − t²)y'' − 2ty' + 2y = 0 with y(0) = 0, y'(0) = 1.",
            (
                Step("The leading coefficient 1 − t² vanishes at t = ±1, both "
                     "at distance 1 from the origin, so a series about 0 is "
                     "guaranteed for |t| < 1 before anything is computed.",
                     r"\rho \geq 1"),
                Step("Here ℓ(ℓ + 1) = 2, so ℓ = 1, and (4) becomes the "
                     "recurrence below.",
                     r"a_{n+2} = \frac{(n-1)(n+2)}{(n+2)(n+1)}\,a_n "
                     r"= \frac{n-1}{n+1}\,a_n"),
                Step("y(0) = a₀ = 0 kills the even branch. On the odd branch "
                     "a₁ = 1, and the factor n − 1 vanishes at the very first "
                     "step: a₃ = 0·a₁/2 = 0, so a₅ = a₇ = ⋯ = 0 too."),
                Step("One term is left. The rule did not fail — it generated "
                     "zeros, which a rule is entitled to do. This is the "
                     "Legendre polynomial P₁(t) = t.",
                     r"y = t"),
            ),
            equation="(1-t**2)*y'' - 2*t*y' + 2*y = 0",
            conditions="y(0) = 0, y'(0) = 1",
            answer="t", answer_latex=r"y(t) = t",
        ),
        Para(
            "Why should anyone care whether a series stops? Because in the "
            "physical problem t = cos θ runs over the whole interval "
            "[−1, 1], including its endpoints, and the next section shows "
            "that a Legendre series that does not stop is unbounded as "
            "t → ±1. Requiring the solution to stay finite at the poles of a "
            "sphere therefore forces ℓ to be a whole number — a quantisation "
            "condition, produced by nothing more than a numerator that can "
            "vanish."
        ),
        Para(
            "Legendre and Hermite are not the only families built this way. "
            "Chebyshev's equation (1 − t²)y'' − ty' + α²y = 0, which the "
            "power-series chapter only mentioned and which differs "
            "from Legendre's only in the coefficient of y', gives in the same "
            "way a two-term recurrence of step 2 whose numerator vanishes "
            "at n = α."
        ),
        Worked(
            "Chebyshev's equation",
            "Find the recurrence for (1 − t²)y'' − ty' + α²y = 0 about 0, and "
            "the solution with α = 2, y(0) = −1, y'(0) = 0.",
            (
                Step("P = 1 − t² vanishes at ±1, so the guaranteed radius "
                     "about 0 is 1.",
                     r"\rho \geq 1"),
                Step("Shift the bare y''; −t²y'' contributes −n(n − 1)aₙ and "
                     "−ty' contributes −naₙ, and −n(n − 1) − n = −n². "
                     "Collecting tⁿ:",
                     r"(n+2)(n+1)a_{n+2} - n^{2}a_n + \alpha^{2}a_n = 0"),
                Step("So the recurrence is the one below. Its numerator "
                     "(n − α)(n + α) vanishes at n = α, and for whole α the "
                     "branch of that parity is a polynomial of degree α.",
                     r"a_{n+2} = \frac{(n-\alpha)(n+\alpha)}{(n+2)(n+1)}\,a_n"),
                Step("At α = 2, with a₁ = 0 and a₀ = −1: a₂ = (0 − 4)(−1)/2 = 2, "
                     "and a₄ = (4 − 4)a₂/12 = 0, so the even branch stops.",
                     r"y = 2t^{2} - 1"),
                Step("This is the Chebyshev polynomial T₂(t). The Chebyshev "
                     "polynomial of whole-number degree α has the closed form "
                     "cos(α cos⁻¹ t) on [−1, 1], and the identity cos 2θ = 2cos²θ − 1 with "
                     "t = cos θ confirms the answer without any series."),
            ),
            equation="(1-t**2)*y'' - t*y' + 4*y = 0",
            conditions="y(0) = -1, y'(0) = 0",
            answer="2*t**2 - 1", answer_latex=r"y(t) = 2t^{2} - 1 = T_2(t)",
        ),
        Figure("recurrence",
               "The figure draws the recurrence (4), starting from "
               "a₀ = a₁ = 1: the left pane shows a₀ to a₁₅ as "
               "stems, the right pane the even and odd partial sums on "
               "−1 ≤ t ≤ 1. The ℓ slider runs from 0 to 6 and snaps onto "
               "whole numbers. Set ℓ = 3 and compare the ℓ = 3 example of "
               "the power-series chapter: a₃ is −5/3 and every odd stem from "
               "a₅ on collapses, while the even stems run on, starting from "
               "the tall a₂ = −6 and a₄ = 3 (the pane grows to fit them). "
               "Move to ℓ = 4 and the collapse switches "
               "parity, starting at a₆. Then pick a value between whole "
               "numbers, such as 2.5, and watch every stem survive, "
               "shrinking only slowly — the sign, explained next, that the "
               "series reaches no further than |t| = 1."),
    )),
    Section("How far the series reaches: the ratio test", (
        Para(
            "A recurrence carries its own convergence test. Take a branch of "
            "a two-term recurrence of step 2 whose coefficients are never "
            "zero (a branch that stops is a polynomial and converges "
            "everywhere). For the even branch ∑ a₂ₖt²ᵏ the ratio of one term "
            "to the one before is F(2k)·t². If |F(n)| tends to a limit L as "
            "n → ∞, the ratio test says the branch converges when L·t² < 1 "
            "and diverges when L·t² > 1, so its radius is 1/√L — infinite "
            "when L = 0. The same holds for the odd branch."
        ),
        Display(r"\lim_{n\to\infty}\left|\frac{a_{n+2}}{a_n}\right| = L "
                r"\;\Longrightarrow\; \rho = \frac{1}{\sqrt{L}}", "5"),
        Para(
            "For y'' + y = 0, |F(n)| = 1/((n + 2)(n + 1)) → 0, and the series "
            "converge for every t, as cosine and sine must. For Hermite's "
            "equation |F(n)| behaves like 2/n → 0: infinite radius again. "
            "For Legendre's equation, (4) gives F(n) → 1, so every "
            "non-terminating Legendre series has radius exactly 1. In the "
            "ℓ = 3 case the even branch's ratio a₁₂/a₁₀ = F(10) is already "
            "0.74, and the ratio at n = 200 is 0.99 — the coefficients barely "
            "shrink, which is what the figure's stems show between whole "
            "values of ℓ."
        ),
        Para(
            "At |t| = 1 itself the ratio test is silent, since there L·t² = 1. "
            "Legendre's recurrence says more if F is expanded a step "
            "further: F(n) = 1 − 2/n + ⋯, which is also how n/(n + 2) "
            "behaves, the ratio of the sequence C/n. So the coefficients of a "
            "branch that does not stop behave like C/n with C ≠ 0 (no factor "
            "of the product (3) is zero). By computation, n·aₙ approaches "
            "about 1.50 on the even branch at ℓ = 3 and about 0.985 at "
            "ℓ = 2.5, with a₀ = 1. The even branch therefore behaves like "
            "C times the sum of t²ᵏ/(2k), which is −(C/2)ln(1 − t²), and the "
            "odd branch like C·tanh⁻¹ t: both are unbounded as t → ±1. The "
            "next example is the case where this is exact."
        ),
        Worked(
            "A Legendre series that reaches exactly to 1",
            "Solve (1 − t²)y'' − 2ty' = 0, Legendre's equation with ℓ = 0, "
            "with y(0) = 0 and y'(0) = 1, and find the radius of the series.",
            (
                Step("With ℓ = 0, (4) becomes aₙ₊₂ = n(n + 1)aₙ/((n + 2)(n + 1)) "
                     "= n·aₙ/(n + 2). The even branch stops at once (a₂ = 0); "
                     "with a₀ = 0 it is absent anyway.",
                     r"a_{n+2} = \frac{n}{n+2}\,a_n"),
                Step("Odd branch from a₁ = 1: a₃ = 1/3, a₅ = (3/5)(1/3) = 1/5, "
                     "a₇ = 1/7, and in general the coefficient of t to an odd "
                     "power is one over that power.",
                     r"y = t + \frac{t^{3}}{3} + \frac{t^{5}}{5} + \cdots "
                     r"= \sum_{k=0}^{\infty}\frac{t^{2k+1}}{2k+1}"),
                Step("The ratio n/(n + 2) tends to L = 1, so by (5) the radius "
                     "is 1. The series is that of the inverse hyperbolic "
                     "tangent, ½ ln((1 + t)/(1 − t)), which is infinite at "
                     "t = ±1 — exactly where the leading coefficient 1 − t² "
                     "vanishes.",
                     r"y = \tanh^{-1} t = \frac{1}{2}\ln\frac{1+t}{1-t}"),
                Step("A check without series: (1 − t²)y'' − 2ty' is the "
                     "derivative of (1 − t²)y', which here equals 1, a "
                     "constant."),
            ),
            equation="(1-t**2)*y'' - 2*t*y' = 0", conditions="y(0) = 0, y'(0) = 1",
            answer="log((1 + t)/(1 - t))/2",
            answer_latex=r"y(t) = \tanh^{-1} t = \frac{1}{2}\ln\frac{1+t}{1-t}",
        ),
        Para(
            "So the ℓ = 0 example is the quantisation argument in miniature: "
            "only the polynomials stay finite on all of [−1, 1]. The "
            "Frobenius chapter comes back to this same solution from the "
            "other end, at the singular point t = 1, where its logarithm is "
            "what matters."
        ),
    )),
    Section("The radius from the equation", (
        Para(
            "The ratio test needs the recurrence, and only works cleanly "
            "for two-term ones. The existence theorem of the power-series "
            "chapter gives the radius without any of that, from the equation "
            "alone: about an ordinary point t₀ every series solution "
            "converges at least out to the nearest singular point, real or "
            "complex. More generally, if p and q in y'' + p y' + q y = 0 "
            "have Taylor series about t₀ that converge for |t − t₀| < ρ, so "
            "does every solution."
        ),
        Display(r"\rho \;\geq\; \min_{P(s)=0}\,|s - t_0|", "6"),
        Para(
            "One point the theorem hides in its hypotheses needs stressing: "
            "P, Q and R must have no factor common to all three. The "
            "equation (1 − t²)y'' + (1 − t²)y = 0 is just y'' + y = 0 in "
            "disguise: its apparent singular points at ±1 cancel, and its "
            "solutions converge everywhere. Reduce the equation before "
            "reading off the zeros of P."
        ),
        Worked(
            "Radii, real and complex",
            "Find the guaranteed radius ρ, the distance to the nearest "
            "singular point, of a series solution about the given point: "
            "(a) (1 − t²)y'' + y = 0 about 0; (b) (t² + 4)y'' + y = 0 about "
            "0 and about 2; (c) y'' + y/(1 + t²) = 0 about 0 and about 1.",
            (
                Step("(a) P = 1 − t² vanishes at ±1, distance 1 from 0.",
                     r"\rho \geq 1"),
                Step("(b) P = t² + 4 has no real zeros; its zeros are ±2i. "
                     "From 0 their distance is 2; from 2 it is "
                     "|2 − 2i| = √8 = 2√2 ≈ 2.83.",
                     r"t = \pm 2i: \quad \rho_0 \geq 2, \qquad "
                     r"\rho_2 \geq 2\sqrt{2}"),
                Step("(c) Multiplied through by 1 + t², the equation is "
                     "(1 + t²)y'' + y = 0, and P = 1 + t² vanishes at ±i. "
                     "From 0 the distance is 1; from 1 it is |1 − i| = √2.",
                     r"t = \pm i: \quad \rho_0 \geq 1, \qquad "
                     r"\rho_1 \geq \sqrt{2}"),
                Step("In (c) the recurrence confirms the first answer and "
                     "shows it is exact. Collecting tⁿ gives "
                     "aₙ₊₂ = −(n² − n + 1)aₙ/((n + 2)(n + 1)), so a₂ = −a₀/2, "
                     "a₄ = a₀/8, a₃ = −a₁/6, a₅ = 7a₁/120, and the ratio tends "
                     "to 1: radius exactly 1, by (5).",
                     r"a_{n+2} = -\frac{n^{2} - n + 1}{(n+2)(n+1)}\,a_n"),
            ),
        ),
        Para(
            "The radius is a distance, so it can be read off from wherever "
            "the centre is, with no substitution at all; that is why (b) and "
            "(c) give different answers about different centres even though "
            "nothing about the equation changed. The coefficients are "
            "another matter. A series about t₀ ≠ 0 is a series in powers of "
            "t − t₀, and the substitution s = t − t₀ turns the problem into "
            "one about s = 0, which the method already handles. Every "
            "coefficient of the equation has to be rewritten in s first."
        ),
        Worked(
            "A series about t = 1",
            "Find the recurrence for ty'' + y = 0 about t = 1, the guaranteed "
            "radius, and the solution with y(1) = 1, y'(1) = 0 through the "
            "fifth power.",
            (
                Step("P = t vanishes only at 0, a distance 1 from the centre. "
                     "So t = 1 is ordinary and ρ ≥ 1; the series about 1 "
                     "cannot be expected to reach t = 0 or t = 2.",
                     r"\rho \geq 1"),
                Step("Put s = t − 1, so t = 1 + s and d/dt = d/ds. The "
                     "equation becomes (1 + s)y'' + y = 0, and the series is "
                     "y = ∑ aₙsⁿ with a₀ = y(1) and a₁ = y'(1).",
                     r"(1+s)\,y'' + y = 0, \qquad y = \sum_{n=0}^{\infty} a_n s^{n}"),
                Step("The bare y'' shifts by (2). The product s·y'' is one "
                     "power low, so it shifts by one: the sum of "
                     "n(n − 1)aₙsⁿ⁻¹ becomes the sum of (n + 1)n·a_(n+1)·sⁿ. "
                     "Collecting sⁿ gives a three-term recurrence.",
                     r"(n+2)(n+1)a_{n+2} + n(n+1)a_{n+1} + a_n = 0"),
                Step("With a₀ = 1, a₁ = 0: n = 0 gives a₂ = −1/2; n = 1 gives "
                     "6a₃ = −(2a₂ + a₁) = 1, so a₃ = 1/6; then a₄ = −1/24 and "
                     "a₅ = 1/60.",
                     r"y = 1 - \frac{(t-1)^{2}}{2} + \frac{(t-1)^{3}}{6} "
                     r"- \frac{(t-1)^{4}}{24} + \frac{(t-1)^{5}}{60} - \cdots"),
                Step("The answer is in powers of t − 1, not of t, and it "
                     "should be left that way. Nor could an ordinary series "
                     "in powers of t replace it: t = 0 is a singular point of "
                     "the equation, which is the Frobenius chapter's "
                     "business."),
            ),
        ),
    )),
    Section("Coefficients that are not polynomials", (
        Para(
            "The theorem asks only that p and q be analytic, not that they "
            "be polynomials, and an equation such as y'' + eᵗy = 0 is "
            "solved by the same method. The power-series chapter found its "
            "first coefficients by differentiating the equation at the "
            "centre, which gives numbers but no rule; this section finds the "
            "rule. The difference from the polynomial case is that eᵗ is itself "
            "an infinite series, so the term eᵗy is a product of two series, "
            "and its coefficient of tⁿ collects every pair of powers that "
            "adds up to n. That product rule (the Cauchy product) replaces the "
            "single shift of the polynomial case."
        ),
        Worked(
            "An exponential coefficient",
            "Find the equations for the coefficients of y'' + eᵗy = 0 about "
            "0, compute a₂ to a₄ in terms of a₀ and a₁, and give the radius.",
            (
                Step("P = 1, and eᵗ has a Taylor series that converges for "
                     "every t, so every solution's series does too.",
                     r"\rho = \infty"),
                Step("Write eᵗ as the sum of tᵏ/k!. The coefficient of tⁿ in "
                     "eᵗy is then a₀/n! + a₁/(n − 1)! + ⋯ + aₙ/0!, so the "
                     "identity theorem gives, for each n:",
                     r"(n+2)(n+1)a_{n+2} = -\sum_{k=0}^{n}\frac{a_k}{(n-k)!}"),
                Step("n = 0: 2a₂ = −a₀. n = 1: 6a₃ = −(a₀ + a₁). n = 2: "
                     "12a₄ = −(a₀/2 + a₁ + a₂) = −a₁, the a₀ terms cancelling.",
                     r"a_2 = -\frac{a_0}{2}, \quad a_3 = -\frac{a_0 + a_1}{6}, "
                     r"\quad a_4 = -\frac{a_1}{12}"),
                Step("This is not a two-term or three-term recurrence: every "
                     "new coefficient involves all the earlier ones, so no "
                     "product formula is in sight. With y(0) = 1, y'(0) = 0 "
                     "the series begins as below; the next coefficient, from "
                     "n = 3, is a₅ = 1/40.",
                     r"y = 1 - \frac{t^{2}}{2} - \frac{t^{3}}{6} "
                     r"+ \frac{t^{5}}{40} + \cdots"),
                Step("These agree with the power-series chapter's route, "
                     "successive differentiation: y'' = −eᵗy gives "
                     "y''(0) = −1, and y''' = −eᵗ(y + y') gives y'''(0) = −1, "
                     "so a₂ = −1/2 and a₃ = −1/3! = −1/6, as found."),
            ),
        ),
        Para(
            "For a coefficient like eᵗ or cos t the Cauchy product is the "
            "only real change; the radius still comes from the theorem, and "
            "since both functions are analytic everywhere it is infinite. "
            "What is lost is the short recurrence. When the coefficients are "
            "polynomials, each power of t in them shifts the sums once and "
            "the recurrence has a fixed, small number of terms; when they are "
            "full series, the recurrence reaches back to a₀ every time."
        ),
    )),
    Section("A complex singularity stops a real series", (
        Para(
            "Case (c) of the radii example deserves a second look, because "
            "it is the surprise of this chapter. The equation "
            "(1 + t²)y'' + y = 0 has nothing wrong with it anywhere on the "
            "real line — its leading coefficient is never smaller than 1 — "
            "and yet its series about 0 reaches only to |t| < 1. The "
            "simplest function with the same behaviour shows that this is "
            "not the theorem being cautious."
        ),
        Display(r"\frac{1}{1+t^{2}} = 1 - t^{2} + t^{4} - t^{6} + \cdots "
                r"\qquad (|t| < 1)", "7"),
        Para(
            "The function 1/(1 + t²) is smooth and bounded for every real t, "
            "but the geometric series (7) diverges for |t| ≥ 1, since its "
            "terms do not even tend to zero there. At t = 0.5 the sum "
            "through t¹⁶ is 0.8000031 against the true value 0.8; at t = 1.1 "
            "the partial sums through t⁸, t¹⁶ and t³² are 1.63, 2.97 and "
            "12.01, running away from the true 0.452. Nothing on the real "
            "line explains "
            "this. In the complex plane, 1/(1 + t²) is infinite at t = ±i, "
            "and a power series converges on a disc — so the disc about 0 "
            "cannot reach past ±i, and its trace on the real axis is the "
            "interval (−1, 1)."
        ),
        Box(
            "remark", "Discs, not intervals",
            "A power series in t converges inside a circle in the complex "
            "plane and diverges outside it. The interval of convergence a "
            "real-variable course talks about is only where that circle "
            "crosses the real line, which is why a singular point off the "
            "line limits a real series exactly as firmly as one on it.",
        ),
        Worked(
            "A closed form with a complex wall",
            "Show that (1 + t²)y'' + 2ty' − 2y = 0 has the recurrence "
            "aₙ₊₂ = −(n − 1)aₙ/(n + 1), and find the solution with "
            "y(0) = 1, y'(0) = 0 together with its radius.",
            (
                Step("Here t²y'' and 2ty' are already in tⁿ. Collecting the "
                     "coefficient of tⁿ and factoring:",
                     r"(n+2)(n+1)a_{n+2} + (n^{2}+n-2)a_n = 0, \quad "
                     r"n^{2}+n-2 = (n+2)(n-1)"),
                Step("The factor n + 2 cancels, leaving a short recurrence. "
                     "(The odd branch stops at once, since n = 1 gives a₃ = 0; "
                     "so y = t is a solution, as substitution confirms.)",
                     r"a_{n+2} = -\frac{n-1}{n+1}\,a_n"),
                Step("With a₀ = 1, a₁ = 0: a₂ = 1, a₄ = −1/3, a₆ = 1/5, "
                     "a₈ = −1/7, and the general even coefficient is below.",
                     r"a_{2k} = \frac{(-1)^{k+1}}{2k-1} \quad (k \geq 1), \qquad "
                     r"y = 1 + t^{2} - \frac{t^{4}}{3} + \frac{t^{6}}{5} - \cdots"),
                Step("Apart from the 1, this is t times the series "
                     "t − t³/3 + t⁵/5 − ⋯ of tan⁻¹ t. The ratio tends to 1, "
                     "so the radius is 1 — set by the zeros ±i of 1 + t², "
                     "where tan⁻¹ has its singularities — although "
                     "1 + t·tan⁻¹ t itself is smooth for every real t.",
                     r"y = 1 + t\tan^{-1} t"),
            ),
            equation="(1+t**2)*y'' + 2*t*y' - 2*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            answer="1 + t*atan(t)", answer_latex=r"y(t) = 1 + t\tan^{-1} t",
        ),
        Plot(
            "Partial sums stopped by an invisible wall",
            "y = 1 + t·tan⁻¹ t, the solution of the last example, and its "
            "series truncated after t⁸ and after t¹⁶. Inside |t| < 1 the "
            "longer sum is the better one; past |t| = 1 both break away, "
            "and the longer one breaks away harder. The function itself is "
            "perfectly smooth there — the wall is at ±i, off the picture.",
            (Curve("1 + t*atan(t)", "1 + t·tan⁻¹ t"),
             Curve("1 + t**2 - t**4/3 + t**6/5 - t**8/7",
                   "through t⁸"),
             Curve("1 + t**2 - t**4/3 + t**6/5 - t**8/7 + t**10/9 - t**12/11"
                   " + t**14/13 - t**16/15", "through t¹⁶")),
            t=(-1.5, 1.5), ylim=(-1.0, 3.5),
        ),
    )),
    Section("Using a truncated series", (
        Para(
            "In practice a series solution is evaluated by summing finitely "
            "many terms, and the radius governs how many are needed. Deep "
            "inside the disc the terms shrink geometrically and a handful "
            "suffice; near its edge they shrink slowly and many are needed; "
            "outside it no number of terms will do. The solution "
            "1 + t·tan⁻¹ t shows all three regimes."
        ),
        Para(
            "At t = 0.5, summing through t⁸ gives 1.2317336 against the true "
            "value 1.2318238, an error of 9.0 × 10⁻⁵; through t¹⁶ the error "
            "is 1.8 × 10⁻⁷. Because the series alternates with terms "
            "decreasing in size, the error is smaller than the first term "
            "omitted — 1.1 × 10⁻⁴ and 2.2 × 10⁻⁷ respectively — and that "
            "bound can be stated before the true value is known. At t = 0.9 "
            "the same two sums are off by 2.3 × 10⁻² and 5.1 × 10⁻³, and it "
            "takes the sum through t³² to bring the error down to "
            "4.8 × 10⁻⁴: doubling the terms gains less than one digit, where "
            "at t = 0.5 it gained nearly three. At t = 1.2 the sum through "
            "t¹⁶ gives 1.36 and the sum through t³² gives −4.28, for a "
            "function whose value is 2.05: past the radius, more terms make "
            "things worse."
        ),
        Para(
            "An infinite radius does not make every truncation good "
            "everywhere, only eventually good. The series of cos t "
            "converges for all t, but at t = 3 the sum through t⁸ is −0.9748 "
            "against cos 3 ≈ −0.9900, while through t¹² the error is down to "
            "5 × 10⁻⁵. Far from the centre the early terms are huge and "
            "cancel each other, so the number of terms needed grows with "
            "|t|. The power-series chapter's graph of the cosine partial sums "
            "shows it: each one follows the cosine for a while and then "
            "leaves for good."
        ),
        Para(
            "Airy's equation sits at the good end of this scale. Its radius "
            "is infinite and each step of its recurrence divides by a product "
            "of two growing integers, so near the origin very few terms "
            "are needed. The standard Airy function Ai is the combination "
            "with a₀ = Ai(0) ≈ 0.35503 and a₁ = Ai'(0) ≈ −0.25882, and the "
            "power-series chapter quoted Ai(1) ≈ 0.1353 from it. How few "
            "terms that takes is now easy to say: using "
            "the coefficients of the Airy example through t¹² and t¹³ — five "
            "non-zero terms in each chain — gives Ai(1) ≈ 0.1352924155, "
            "against the true 0.1352924163."
        ),
        Para(
            "The step-by-step solver for this chapter's examples follows the "
            "same chain for a homogeneous second-order equation about t = 0: "
            "it classifies the point, reports the guaranteed radius from the "
            "zeros of the leading coefficient (complex ones included, after "
            "cancelling any factor common to all three coefficients), "
            "substitutes the series, "
            "and lists the first few coefficients in terms of a₀ and a₁. "
            "When the series terminates it says so and checks the "
            "polynomial exactly; when it does not, it says the result is a "
            "truncation and checks that the residual only contains the "
            "powers that were never written down."
        ),
    )),
    Section("Common errors", (
        Para(
            "The first error is shifting the exponent but not the starting "
            "index, or shifting a sum that did not need it. Before shifting "
            "anything, write each term's exponent next to it: tⁿ⁻² for y'', "
            "tⁿ for t²y'' and ty', tⁿ⁺¹ for ty. Only those not already in tⁿ "
            "move. The second is losing the low terms when sums start at "
            "different indices. The n = 0 equation of Airy's equation is "
            "2a₂ = 0, and dropping it leaves a₂ apparently free — which "
            "would give a second-order equation three arbitrary constants."
        ),
        Para(
            "The third is solving the recurrence for the wrong coefficient. "
            "The equation for tⁿ should be solved for the highest-index "
            "coefficient, aₙ₊₂, so that it expresses new coefficients through "
            "known ones; solving for aₙ produces a rule that runs backwards. "
            "The fourth is treating a list of coefficients as the answer and "
            "missing the structure: Airy's zeros, a terminating branch, a "
            "product formula. The fifth is computing the radius from the "
            "real zeros of P only. The equation y'' + y/(1 + t²) = 0 looks "
            "fine on the whole real line and has radius 1, because of ±i. "
            "The sixth, about a centre other than 0, is expanding in powers "
            "of t instead of t − t₀, or forgetting to rewrite the "
            "coefficients in s = t − t₀."
        ),
        Para(
            "The last is reading a guaranteed radius as an exact one, or the "
            "other way round. The theorem gives a lower bound; a particular "
            "solution may do better, as every polynomial does. And a radius "
            "is a statement about convergence, not about accuracy: an "
            "infinite radius does not mean that six terms are good at "
            "t = 10."
        ),
    )),
    Section("Summary", (
        Para(
            "Substituting y = ∑ aₙtⁿ produces several sums in different powers "
            "of t. Shift each — exponent, subscript and starting index "
            "together — so that all run over tⁿ, peel off the low terms where "
            "the starting indices differ, and collect. By the identity "
            "theorem every coefficient of the result is zero, and solving "
            "the n-th equation for aₙ₊₂ gives the recurrence relation, which "
            "is the answer: a₀ and a₁ stay free as the initial conditions, "
            "and the rule produces the rest. About a centre t₀ ≠ 0 the same "
            "steps run in s = t − t₀, and a coefficient that is a full series "
            "brings in the Cauchy product."
        ),
        Para(
            "A two-term recurrence of step 2, aₙ₊₂ = F(n)aₙ, splits the "
            "coefficients into even and odd branches, can be solved as a "
            "product, and terminates when the numerator of F vanishes — which "
            "is where the Legendre, Hermite and Chebyshev polynomials come "
            "from. A recurrence with a larger step, such as Airy's, splits "
            "the coefficients into more chains, and a peeled-off equation can "
            "start one of them at zero."
        ),
        Para(
            "The series converges at least as far as the nearest zero of "
            "the leading coefficient, measured in the complex plane; for a "
            "non-terminating branch of a step-2 recurrence the ratio "
            "|aₙ₊₂/aₙ| → L gives the radius 1/√L directly. Complex "
            "singularities limit real series, as 1/(1 + t²) and "
            "1 + t·tan⁻¹ t show. The Frobenius chapter, which follows, takes "
            "up the points this chapter has excluded: those where the "
            "leading coefficient vanishes at the centre itself."
        ),
    )),
)


FROBENIUS = (
    Section("Where the power-series method stops", (
        Para(
            "The two chapters before this one built solutions coefficient by "
            "coefficient, and the whole construction rested on one hypothesis: "
            "the point t₀ about which the series is expanded must be *ordinary*. "
            "Divide the equation P(t)y'' + Q(t)y' + R(t)y = 0 by P to reach the "
            "standard form y'' + p(t)y' + q(t)y = 0; if p and q are analytic at "
            "t₀, two independent power-series solutions exist there, and the "
            "recurrence chapter showed how far they reach. This chapter is about "
            "the points where that hypothesis fails — and about why those "
            "points, far from being a nuisance to be avoided, are usually the "
            "ones a problem is really about."
        ),
        Para(
            "A singular point of an equation is rarely an accident of algebra. "
            "Separate variables in a problem with circular symmetry — a "
            "vibrating drumhead, heat flowing in a cylinder, a waveguide — and "
            "the radial equation is Bessel's equation, singular at the centre "
            "of the disc, where the radius is zero. Do the same on a sphere and Legendre's "
            "equation "
            "appears, singular at t = ±1, the poles. The physically essential "
            "condition, that the solution stay finite at the centre or at the "
            "pole, is stated precisely at the singular point. A method that "
            "cannot work there cannot answer the question that was asked."
        ),
        Para(
            "The power-series chapter ended by watching a plain series fail on "
            "a Cauchy–Euler equation: every coefficient was forced to zero, "
            "because the solutions were t^(±1/2), not power series. The same "
            "thing happens to 2t²y'' + 3ty' − y = 0, whose solutions the "
            "Cauchy–Euler chapter found to be √t and 1/t; substituting y = ∑ aₙtⁿ gives the "
            "single sum (1), and since (2n − 1)(n + 1) is never zero for a "
            "whole number n, every aₙ vanishes. This chapter returns to that "
            "equation below, with the assumption corrected."
        ),
        Display(r"\sum_{n=0}^{\infty}\left[2n(n-1) + 3n - 1\right]a_n t^{n} "
                r"= \sum_{n=0}^{\infty}(2n-1)(n+1)\,a_n t^{n} = 0", "1"),
    )),
    Section("Ordinary, regular singular, irregular", (
        Para(
            "The first task is to sort the singular points into those that can "
            "be handled and those that cannot. As in the power-series chapter, "
            "write the equation in standard form, y'' + p(t)y' + q(t)y = 0 with "
            "p = Q/P and q = R/P. A point t₀ where p or q fails to be analytic "
            "is a singular point. When P, Q and R are polynomials with no "
            "common factor, the singular points are simply the roots of P, "
            "complex ones included."
        ),
        Box(
            "definition", "Regular and irregular singular points",
            "A singular point t₀ of y'' + p(t)y' + q(t)y = 0 is *regular* if "
            "the two functions below are both analytic at t₀ — that is, if p "
            "blows up no faster than 1/(t − t₀) and q no faster than "
            "1/(t − t₀)². A singular point that is not regular is *irregular*.",
            r"(t - t_0)\,p(t) \text{ and } (t - t_0)^{2}q(t) \text{ analytic at } t_0",
        ),
        Para(
            "For the rational coefficients a first course meets, the test is a "
            "pair of limits. If both of the limits below are finite, the "
            "point is regular, and the two limits have names: they are the "
            "numbers p₀ and q₀ that will control everything that follows. "
            "If either limit is infinite, the point is irregular."
        ),
        Display(r"p_0 = \lim_{t\to t_0}(t - t_0)\,p(t), \qquad "
                r"q_0 = \lim_{t\to t_0}(t - t_0)^{2}q(t)", "2"),
        Para(
            "A Cauchy–Euler equation at²y'' + bty' + cy = 0 is the model case. "
            "In standard form p = b/(at) and q = c/(at²), so tp = b/a and "
            "t²q = c/a are constants: t = 0 is a regular singular point with "
            "p₀ = b/a and q₀ = c/a, and nothing else happens anywhere. "
            "Bessel's equation t²y'' + ty' + (t² − ν²)y = 0 has tp = 1 and "
            "t²q = t² − ν², both polynomials, so t = 0 is regular with p₀ = 1 "
            "and q₀ = −ν². By contrast t³y'' + y = 0 has q = 1/t³ and "
            "t²q = 1/t, which blows up: t = 0 is irregular."
        ),
        Para(
            "Two more classical equations belong on the list. Laguerre's "
            "equation ty'' + (1 − t)y' + λy = 0 has tp = 1 − t and t²q = λt, "
            "so t = 0 is regular with p₀ = 1 and q₀ = 0. Chebyshev's equation "
            "(1 − t²)y'' − ty' + α²y = 0 is singular at t = ±1, and at either "
            "point the limits (2) give p₀ = 1/2 and q₀ = 0: both are regular."
        ),
        Para(
            "Most of what follows takes t₀ = 0. That costs nothing: the "
            "substitution s = t − t₀ moves any singular point to the origin, "
            "and Legendre's equation below is worked exactly that way."
        ),
        Worked(
            "Two singular points of different kinds",
            "Locate and classify the singular points of "
            "t(t − 1)²y'' + 3y' − y = 0.",
            (
                Step("P = t(t − 1)² vanishes at t = 0 and t = 1, so those are "
                     "the singular points. In standard form "
                     "p = 3/(t(t − 1)²) and q = −1/(t(t − 1)²).",
                     r"p(t) = \frac{3}{t(t-1)^{2}}, \qquad q(t) = \frac{-1}{t(t-1)^{2}}"),
                Step("At t = 0: tp = 3/(t − 1)² → 3 and t²q = −t/(t − 1)² → 0. "
                     "Both limits are finite, so t = 0 is a regular singular "
                     "point with p₀ = 3 and q₀ = 0. (The indicial equation "
                     "defined below will be r(r − 1) + 3r = r(r + 2) = 0, so "
                     "the exponents here are 0 and −2: a whole-number "
                     "difference, the case the later sections take up.)",
                     r"p_0 = 3, \qquad q_0 = 0"),
                Step("At t = 1: (t − 1)p = 3/(t(t − 1)), which is unbounded as "
                     "t → 1. One infinite limit is enough: t = 1 is an "
                     "irregular singular point, and the methods of this "
                     "chapter do not apply there.",
                     r"\lim_{t\to 1}(t-1)\,p(t) = \infty"),
            ),
        ),
        Worked(
            "Legendre's equation at the poles",
            "Classify the singular points of Legendre's equation "
            "(1 − t²)y'' − 2ty' + ℓ(ℓ + 1)y = 0.",
            (
                Step("P = 1 − t² vanishes at t = ±1. Take t = 1 first and set "
                     "s = t − 1, so 1 − t² = −s(s + 2). Then "
                     "sp = 2(1 + s)/(s + 2) → 1 as s → 0.",
                     r"(t-1)\,p(t) = \frac{2t}{t+1} \to 1"),
                Step("Likewise s²q = −ℓ(ℓ + 1)s/(s + 2) → 0. Both limits are "
                     "finite: t = 1 is regular, with p₀ = 1 and q₀ = 0.",
                     r"(t-1)^{2}q(t) = \frac{-\ell(\ell+1)(t-1)}{t+1} \to 0"),
                Step("The equation is unchanged by t → −t, so t = −1 is regular "
                     "for the same reason, again with p₀ = 1 and q₀ = 0. Every "
                     "other point, including t = 0, is ordinary — which is why "
                     "the power-series chapter could expand about the origin."),
            ),
        ),
    )),
    Section("Why regular is the right condition", (
        Para(
            "The definition can look arbitrary — why one power of (t − t₀) "
            "for p and two for q? The reason is worth seeing. Multiply the "
            "standard form through by (t − t₀)² and group the factors."
        ),
        Display(r"(t-t_0)^{2}y'' + (t-t_0)\left[(t-t_0)p\right]y' + "
                r"\left[(t-t_0)^{2}q\right]y = 0", "3"),
        Para(
            "At a regular singular point the two brackets are analytic, so "
            "near t₀ each is close to its value there, p₀ and q₀. Replacing "
            "them by those constants gives (t − t₀)²y'' + p₀(t − t₀)y' + "
            "q₀y = 0, which is a Cauchy–Euler equation. So near a regular "
            "singular point the equation *looks like* a Cauchy–Euler "
            "equation, and the exponents of 1 and 2 in the definition are "
            "exactly the ones that make that true: they match t² in front of "
            "y'' and t in front of y'. The Cauchy–Euler chapter already knows "
            "what such an equation does — its solutions are powers of t − t₀, "
            "with the exponent fixed by a quadratic and no reason at all to "
            "be a whole number."
        ),
        Para(
            "At an irregular point the comparison fails: some bracket is "
            "unbounded, the leading behaviour is not Cauchy–Euler, and the "
            "solutions can behave in ways no power describes. The cleanest "
            "illustration is first order. The equation t²y' + y = t has "
            "p = 1/t², a double pole where a regular point allows a simple "
            "one. Substitute y = ∑ aₙtⁿ and compare coefficients: a₀ = 0, "
            "a₁ = 1, and aₙ₊₁ = −n·aₙ, so the coefficients are factorials."
        ),
        Display(r"y \sim t - t^{2} + 2t^{3} - 6t^{4} + 24t^{5} - \cdots"
                r" = \sum_{n=1}^{\infty}(-1)^{n-1}(n-1)!\,t^{n}", "4"),
        Box(
            "remark", "A series with radius of convergence zero",
            "The ratio of successive terms in (4) is n|t|, which grows "
            "without bound for every t ≠ 0, so the series diverges everywhere "
            "except at the origin: its radius of convergence is zero. The "
            "equation does have solutions; they simply are not of this form. "
            "That is what irregular means in practice, and it is why a first "
            "course stops at regular singular points.",
        ),
    )),
    Section("The Frobenius form and the indicial equation", (
        Para(
            "If the solution near a regular singular point behaves like a "
            "power of t, assume that behaviour and correct it with an "
            "ordinary series. That is the whole of Frobenius's idea: one "
            "factor t^r in front of a power series. Take t₀ = 0 and t > 0, "
            "where every real power of t is defined."
        ),
        Display(r"y = t^{r}\sum_{n=0}^{\infty}a_n t^{n} = "
                r"\sum_{n=0}^{\infty}a_n t^{n+r}, \qquad a_0 \neq 0", "5"),
        Box(
            "warning", "Why a₀ ≠ 0",
            "Without that condition r would mean nothing: a series starting "
            "at t^(r+3) could equally be written with exponent r + 3 and a "
            "leading coefficient at n = 0. Requiring a₀ ≠ 0 makes r the exact "
            "power with which the solution leaves the singular point, and it "
            "is what lets the lowest power of the substituted equation be "
            "solved for r rather than for a₀.",
        ),
        Para(
            "To substitute, expand the two analytic brackets as power "
            "series, tp(t) = ∑ pₖtᵏ and t²q(t) = ∑ qₖtᵏ, whose constant terms "
            "are the p₀ and q₀ of (2). Equation (3) with t₀ = 0 reads "
            "t²y'' + [tp]·ty' + [t²q]·y = 0. Differentiating (5) term by term, "
            "t²y'' contributes (n + r)(n + r − 1)aₙ and ty' contributes "
            "(n + r)aₙ to the coefficient of t^(n+r), before the brackets "
            "multiply them."
        ),
        Para(
            "The lowest power is t^r, and only a₀ contributes to it: the "
            "brackets can supply only their constant terms. Its coefficient "
            "is a₀[r(r − 1) + p₀r + q₀], and since a₀ ≠ 0, the bracket must "
            "vanish."
        ),
        Box(
            "definition", "Indicial equation at a regular singular point",
            "The indicial equation of y'' + py' + qy = 0 at the regular "
            "singular point t = 0 is the quadratic below, with p₀ and q₀ the "
            "limits (2). Its roots r₁ and r₂ are the *exponents* of the "
            "singular point. When they are real they are labelled r₁ ≥ r₂.",
            r"F(r) = r(r-1) + p_0\,r + q_0 = 0",
        ),
        Para(
            "This is word for word the indicial equation of the Cauchy–Euler "
            "chapter for the equation t²y'' + p₀ty' + q₀y = 0 — and it has to "
            "be, because that is the Cauchy–Euler equation the original "
            "equation resembles near the point. The two chapters share one "
            "quadratic because they are looking at the same leading "
            "behaviour. The same warning applies: it is r(r − 1), not r², "
            "because t²(t^r)'' = r(r − 1)t^r."
        ),
        Para(
            "The two classical equations added to the list above show both "
            "outcomes at once. Laguerre's equation, with p₀ = 1 and q₀ = 0, "
            "has F(r) = r², a repeated exponent 0. Chebyshev's, with p₀ = 1/2 "
            "and q₀ = 0 at each of t = ±1, has F(r) = r(r − 1/2), exponents "
            "0 and 1/2, which differ by 1/2; the theorem below will give two "
            "Frobenius series at each pole."
        ),
        Para(
            "The higher powers give the recurrence. In general the brackets "
            "are whole series, not polynomials, so each product is a product "
            "of two series — the Cauchy product the recurrence chapter used "
            "for y'' + eᵗy = 0. Multiplying them term by term and collecting "
            "the coefficient of t^(n+r) — every pair of indices that adds up "
            "to n contributes — gives the two sums below."
        ),
        Display(r"[tp]\,ty' = \sum_{n=0}^{\infty}\left(\sum_{k=0}^{n}p_{n-k}"
                r"(k+r)a_k\right)t^{n+r}, \qquad [t^{2}q]\,y = "
                r"\sum_{n=0}^{\infty}\left(\sum_{k=0}^{n}q_{n-k}a_k\right)t^{n+r}"),
        Para(
            "The k = n terms, p₀(n + r)aₙ and q₀aₙ, join (n + r)(n + r − 1)aₙ "
            "from t²y'' to make [(n + r)(n + r − 1) + p₀(n + r) + q₀]aₙ, "
            "which is F(r + n)aₙ. Everything with k < n involves earlier "
            "coefficients and goes to the right side. For n ≥ 1 that is the "
            "recurrence."
        ),
        Display(r"F(r+n)\,a_n = -\sum_{k=0}^{n-1}\left[(r+k)\,p_{n-k} + "
                r"q_{n-k}\right]a_k, \qquad n \geq 1", "6"),
        Para(
            "For the equations of this chapter (6) is much shorter than it "
            "looks, because most of the pₖ and qₖ are zero. In Bessel's "
            "equation tp = 1 and t²q = t² − ν², so the only non-zero ones "
            "are p₀ = 1, q₀ = −ν² and q₂ = 1, and (6) collapses to "
            "F(r + n)aₙ = −aₙ₋₂. Whatever its length, (6) can be solved for aₙ "
            "exactly when F(r + n) ≠ 0 — and that single observation is the "
            "whole theory of when Frobenius works."
        ),
    )),
    Section("Frobenius's theorem, and why integers are special", (
        Box(
            "theorem", "Frobenius's theorem",
            "Let t = 0 be a regular singular point of y'' + py' + qy = 0, let "
            "ρ > 0 be the smaller of the radii of convergence of tp and t²q, "
            "and let the indicial roots be real, r₁ ≥ r₂. Then (a) there is a "
            "solution of the form (5) with r = r₁, and its series converges "
            "on 0 < t < ρ. (b) If r₁ − r₂ is not a whole number (0, 1, 2, …), "
            "there is a second, independent solution of the form (5) with "
            "r = r₂, converging on the same interval.",
            r"r_1 - r_2 \notin \{0, 1, 2, \ldots\} \;\Longrightarrow\; "
            r"y = c_1 t^{r_1}\sum a_n t^{n} + c_2 t^{r_2}\sum b_n t^{n}",
        ),
        Box(
            "proof", "Why the larger root always works",
            "F is a monic quadratic with roots r₁ and r₂, so "
            "F(x) = (x − r₁)(x − r₂). With r = r₁, F(r₁ + n) = n(n + r₁ − r₂), "
            "which is a positive number for every n ≥ 1 because r₁ ≥ r₂. So "
            "(6) determines every aₙ from a₀, and the series exists. With "
            "r = r₂ instead, F(r₂ + n) = n(n − (r₁ − r₂)), which vanishes at "
            "n = r₁ − r₂ — possible only when that difference is a positive "
            "integer. At that one step (6) reads 0·aₙ = (something), and "
            "either the something is also zero and aₙ is free, or it is not "
            "and the series cannot exist. Convergence on 0 < t < ρ is proved "
            "by comparing with a geometric series, the majorant argument "
            "sketched with the existence theorem in the power-series chapter.",
            r"F(r_2 + n) = n\left(n - (r_1 - r_2)\right)",
        ),
        Para(
            "The theorem does not say the smaller root fails when the "
            "difference is an integer — only that it *may*. When r₁ − r₂ = N "
            "is a positive integer the smaller exponent's series reaches "
            "the step n = N, where its exponent r₂ + N has caught up with r₁. "
            "There the two series collide, and whether the right side of (6) "
            "happens to vanish decides everything. Both outcomes occur, and "
            "the next sections show one of each. When r₁ = r₂ there is only "
            "one exponent to begin with, and the second solution can never "
            "be of the form (5)."
        ),
        Para(
            "Complex exponents α ± iβ can also arise — the Cauchy–Euler "
            "chapter met them, as oscillations in ln t; t²y'' + ty' + y = 0, "
            "with p₀ = q₀ = 1 and F(r) = r² + 1, has exponents ±i. They differ "
            "by 2iβ, never by a "
            "whole number, so the method goes through with complex "
            "coefficients, and real and imaginary parts give real solutions. "
            "The theorem is stated for real roots because that is the case "
            "every classical equation of this chapter presents."
        ),
    )),
    Section("Two exponents that do not differ by an integer", (
        Para(
            "The first case of the theorem is the straightforward one: two "
            "exponents, two recurrences, two series. The first example "
            "returns to the equation whose plain series collapsed in (1) and "
            "adds a term that makes it a genuine series problem."
        ),
        Worked(
            "Two Frobenius series",
            "Find the Frobenius solutions of 2t²y'' + 3ty' − (t² + 1)y = 0 "
            "about t = 0.",
            (
                Step("Dividing by 2t², tp = 3/2 and t²q = −(t² + 1)/2, so "
                     "p₀ = 3/2 and q₀ = −1/2. The indicial equation is "
                     "r(r − 1) + (3/2)r − 1/2 = 0, that is 2r² + r − 1 = 0.",
                     r"(2r - 1)(r + 1) = 0 \;\Longrightarrow\; r_1 = \frac{1}{2}, "
                     r"\quad r_2 = -1"),
                Step("The difference r₁ − r₂ = 3/2 is not a whole number, so the "
                     "theorem promises two series. Substitute (5). The three "
                     "terms 2t²y'', 3ty' and −y keep the power: each sends "
                     "aₙt^(n+r) to a multiple of t^(n+r), and the bracket "
                     "factorises.",
                     r"\sum_{n=0}^{\infty}\left[2(n+r)(n+r-1) + 3(n+r) - 1\right]"
                     r"a_n t^{n+r} = \sum_{n=0}^{\infty}(2(n+r)-1)(n+r+1)\,a_n t^{n+r}"),
                Step("The term −t²y raises the power by two. Put n → n − 2 so "
                     "that it too is written with t^(n+r); it then starts at "
                     "n = 2, and the convention a₋₂ = a₋₁ = 0 lets it run over "
                     "all n with the other sum.",
                     r"-t^{2}y = -\sum_{n=0}^{\infty}a_n t^{n+r+2} = "
                     r"-\sum_{n=2}^{\infty}a_{n-2}t^{n+r}"),
                Step("Setting the total coefficient of t^(n+r) to zero gives "
                     "the recurrence. At n = 0 it is the indicial equation "
                     "again.",
                     r"(2(n+r) - 1)(n + r + 1)\,a_n = a_{n-2}"),
                Step("At n = 1 the right side is a₋₁ = 0, so a₁ = 0, and with "
                     "it every odd coefficient. For r = 1/2 the factor is "
                     "n(2n + 3), so a₂ = a₀/14, a₄ = a₂/44 = a₀/616, "
                     "a₆ = a₄/90 = a₀/55440.",
                     r"y_1 = t^{1/2}\left(1 + \frac{t^{2}}{14} + "
                     r"\frac{t^{4}}{616} + \frac{t^{6}}{55440} + \cdots\right)"),
                Step("For r = −1 the factor is n(2n − 3), never zero for "
                     "n ≥ 2, so a₂ = a₀/2, a₄ = a₂/20 = a₀/40, "
                     "a₆ = a₄/54 = a₀/2160.",
                     r"y_2 = t^{-1}\left(1 + \frac{t^{2}}{2} + "
                     r"\frac{t^{4}}{40} + \frac{t^{6}}{2160} + \cdots\right)"),
                Step("tp and t²q are polynomials, so ρ = ∞ and both series "
                     "converge for every t > 0. Near the origin y₁ ≈ √t and "
                     "y₂ ≈ 1/t: the Cauchy–Euler solutions of the leading "
                     "part, corrected by the series."),
            ),
        ),
        Para(
            "The general solution is c₁y₁ + c₂y₂, and the picture near t = 0 "
            "is the one the Cauchy–Euler chapter drew: y₂ blows up like 1/t, "
            "y₁ vanishes like √t. If the problem demands a solution bounded "
            "at the origin, c₂ = 0, and one condition has been spent on "
            "boundedness instead of on a value."
        ),
        Para(
            "Sometimes a Frobenius series sums to something familiar. The "
            "next example has exponents 0 and 1/2, and both series turn out "
            "to be old friends with √t in place of t."
        ),
        Worked(
            "Series that sum to cos √t and sin √t",
            "Solve 4ty'' + 2y' + y = 0 by Frobenius about t = 0, and find the "
            "solution with y(0) = 1 whose slope stays finite at the origin.",
            (
                Step("Here tp = 1/2 and t²q = t/4, so p₀ = 1/2, q₀ = 0 and the "
                     "indicial equation is r(r − 1) + r/2 = r(r − 1/2) = 0. The "
                     "exponents 0 and 1/2 differ by 1/2.",
                     r"r_1 = \frac{1}{2}, \qquad r_2 = 0"),
                Step("Substitute y = ∑ aₙt^(n+r). The terms 4ty'' and 2y' both "
                     "lower the power by one, to t^(n+r−1); the term y does "
                     "not, so shift it: y = ∑ aₙt^(n+r) = ∑ aₙ₋₁t^(n+r−1) after "
                     "n → n − 1, with a₋₁ = 0. The coefficient of t^(n+r−1) is "
                     "then [4(n + r)(n + r − 1) + 2(n + r)]aₙ + aₙ₋₁, which "
                     "gives a one-step recurrence.",
                     r"2(n+r)(2n + 2r - 1)\,a_n = -a_{n-1}"),
                Step("For r = 0: aₙ = −aₙ₋₁/(2n(2n − 1)), so with a₀ = 1, "
                     "aₙ = (−1)ⁿ/(2n)!. That is the cosine series with √t in "
                     "place of t.",
                     r"y_2 = \sum_{n=0}^{\infty}\frac{(-1)^{n}t^{n}}{(2n)!} = "
                     r"1 - \frac{t}{2} + \frac{t^{2}}{24} - \cdots = \cos\sqrt{t}"),
                Step("For r = 1/2: aₙ = −aₙ₋₁/((2n + 1)(2n)), so "
                     "aₙ = (−1)ⁿ/(2n + 1)!, and t^(1/2) times that series is the "
                     "sine series.",
                     r"y_1 = t^{1/2}\sum_{n=0}^{\infty}\frac{(-1)^{n}t^{n}}{(2n+1)!}"
                     r" = \sin\sqrt{t}"),
                Step("y(0) = 1 forces the coefficient of cos √t to be 1 and says "
                     "nothing about sin √t, which is 0 there. But sin √t has "
                     "slope cos(√t)/(2√t), unbounded as t → 0⁺, so a finite "
                     "slope removes it."),
            ),
            equation="4*t*y'' + 2*y' + y = 0", conditions="y(0) = 1",
            answer="cos(sqrt(t))", answer_latex=r"y(t) = \cos\sqrt{t}",
        ),
        Para(
            "Notice what the initial condition did. At an ordinary point y(0) "
            "and y'(0) are two free numbers; here y'(0) = −1/2 is not free at "
            "all: it is forced by the equation once the unbounded solution is "
            "excluded. Initial-value problems posed *at* a regular singular "
            "point are different in kind, and the existence and uniqueness "
            "theorem of the second-order unit does not cover them."
        ),
        Plot(
            "A Frobenius series and its partial sums",
            "cos √t, the r = 0 solution of 4ty'' + 2y' + y = 0, against its "
            "partial sums with 2, 3 and 5 terms. The 2-term sum stays within "
            "0.05 of the solution only up to t ≈ 1.1, the 3-term sum to about "
            "3.4 and the 5-term sum to about 11.5; with 8 terms the error is "
            "under 0.05 across the whole window. The series converges for "
            "every t, since tp and t²q are polynomials.",
            (Curve("cos(sqrt(t))", "cos √t"),
             Curve("1 - t/2", "2 terms"),
             Curve("1 - t/2 + t**2/24", "3 terms"),
             Curve("1 - t/2 + t**2/24 - t**3/720 + t**4/40320", "5 terms")),
            t=(0.0, 30.0), ylim=(-1.5, 1.5),
        ),
    )),
    Section("Bessel's equation of order one half", (
        Para(
            "Bessel's equation t²y'' + ty' + (t² − ν²)y = 0 has p₀ = 1 and "
            "q₀ = −ν², so its indicial equation is r(r − 1) + r − ν² = r² − ν² "
            "= 0 and its exponents are ±ν. For ν = 1/2 they are ±1/2, and as "
            "the power-series chapter showed, no plain series can produce "
            "t^(1/2). Frobenius can."
        ),
        Worked(
            "Bessel of order 1/2: a closed form",
            "Solve t²y'' + ty' + (t² − 1/4)y = 0 on t > 0 by Frobenius.",
            (
                Step("p₀ = 1 and q₀ = −1/4, so F(r) = r² − 1/4 and the exponents "
                     "are r₁ = 1/2 and r₂ = −1/2. The recurrence (6) is "
                     "F(r + n)aₙ = −aₙ₋₂.",
                     r"\left((n+r)^{2} - \frac{1}{4}\right)a_n = -a_{n-2}"),
                Step("For r = 1/2 the factor is n(n + 1), so a₁ = 0 and "
                     "a₂ = −a₀/6, a₄ = −a₂/20 = a₀/120, a₆ = −a₀/5040 — the "
                     "coefficients of sin t / t. So y₁ = t^(1/2)·(sin t)/t.",
                     r"y_1 = t^{1/2}\left(1 - \frac{t^{2}}{6} + "
                     r"\frac{t^{4}}{120} - \cdots\right) = \frac{\sin t}{\sqrt{t}}"),
                Step("For r = −1/2 the factor is n(n − 1), which vanishes at "
                     "n = 1: the exponents differ by 1 and the series collide "
                     "there. But the right side is −a₋₁ = 0, so the equation "
                     "reads 0·a₁ = 0 and a₁ is simply free.",
                     r"0\cdot a_1 = 0"),
                Step("Take a₁ = 0. Then a₂ = −a₀/2, a₄ = a₀/24, a₆ = −a₀/720, "
                     "the cosine coefficients, so y₂ = t^(−1/2)cos t. (Keeping "
                     "a₁ ≠ 0 only adds a multiple of y₁.)",
                     r"y_2 = t^{-1/2}\left(1 - \frac{t^{2}}{2} + "
                     r"\frac{t^{4}}{24} - \cdots\right) = \frac{\cos t}{\sqrt{t}}"),
            ),
            equation="t**2*y'' + t*y' + (t**2 - 1/4)*y = 0",
            answer="C1*sin(t)/sqrt(t) + C2*cos(t)/sqrt(t)",
            answer_latex=r"y(t) = \frac{C_1\sin t + C_2\cos t}{\sqrt{t}}",
        ),
        Para(
            "This is the example to remember when someone says that integer "
            "differences break the method. The exponents ±1/2 differ by 1, the "
            "smaller one's series reached the collision at n = 1, and nothing "
            "broke, because the equation only links coefficients two steps "
            "apart and so the right side of (6) at n = 1 was zero. The "
            "theorem's warning is a warning, not a verdict."
        ),
        Plot(
            "The two solutions of Bessel's equation of order 1/2",
            "sin t/√t and cos t/√t. Both oscillate with an amplitude that "
            "decays like 1/√t, a quarter-period apart. At the origin they "
            "part company: sin t/√t ≈ √t → 0, following the exponent +1/2, "
            "while cos t/√t ≈ 1/√t is unbounded, following −1/2. A solution "
            "required to be finite at t = 0 must be a multiple of the first.",
            (Curve("sin(t)/sqrt(t)", "sin t / √t"),
             Curve("cos(t)/sqrt(t)", "cos t / √t")),
            t=(0.04, 12.0), ylim=(-1.5, 3.0),
        ),
    )),
    Section("When the smaller exponent breaks: Bessel of order one", (
        Para(
            "Change ν from 1/2 to 1 and the outcome changes. The exponents "
            "are ±1, differing by 2, and the collision happens at n = 2 — "
            "exactly where Bessel's two-step recurrence does reach back to "
            "a₀."
        ),
        Worked(
            "The smaller root's series cannot exist",
            "For t²y'' + ty' + (t² − 1)y = 0, find the Frobenius series with "
            "the larger exponent and show that the smaller exponent gives "
            "none.",
            (
                Step("p₀ = 1 and q₀ = −1, so F(r) = r² − 1 and the exponents are "
                     "r₁ = 1 and r₂ = −1. The recurrence is F(r + n)aₙ = −aₙ₋₂.",
                     r"\left((n+r)^{2} - 1\right)a_n = -a_{n-2}"),
                Step("For r = 1 the factor is n(n + 2): a₁ = 0, a₂ = −a₀/8, "
                     "a₄ = −a₂/24 = a₀/192, a₆ = −a₄/48 = −a₀/9216. With "
                     "a₀ = 1/2 this is the Bessel function J₁.",
                     r"y_1 = t\left(1 - \frac{t^{2}}{8} + \frac{t^{4}}{192} - "
                     r"\frac{t^{6}}{9216} + \cdots\right)"),
                Step("For r = −1 the factor is n(n − 2). At n = 1 it is −1, so "
                     "a₁ = 0. At n = 2 it is 0, and the recurrence demands "
                     "0·a₂ = −a₀.",
                     r"0\cdot a_2 = -a_0"),
                Step("That forces a₀ = 0, contradicting the requirement a₀ ≠ 0 "
                     "that gave r its meaning. There is no Frobenius solution "
                     "with exponent −1. The second solution exists — every "
                     "second-order linear equation has two — but it is not of "
                     "the form (5)."),
            ),
        ),
        Para(
            "Compare the Cauchy–Euler equation t²y'' + ty' − y = 0, which has "
            "the same exponents ±1. There every pₖ and qₖ beyond the first is "
            "zero, the right side of (6) is identically zero, and the "
            "collision at n = 2 reads 0·a₂ = 0: no contradiction, and the "
            "smaller exponent gives 1/t. Same exponents, opposite verdicts; "
            "the difference is entirely in the rest of the equation."
        ),
        Worked(
            "For a Cauchy–Euler equation, Frobenius gives the powers exactly",
            "Solve t²y'' + ty' − y = 0 with y(1) = 2, y'(1) = 0 and compare "
            "with Frobenius.",
            (
                Step("p₀ = 1, q₀ = −1, and the indicial equation r² − 1 = 0 is the "
                     "one the substitution y = t^r gives in the Cauchy–Euler "
                     "chapter, because it is the same substitution.",
                     r"r(r-1) + r - 1 = (r-1)(r+1) = 0"),
                Step("The recurrence is F(r + n)aₙ = 0. For r = 1, F(1 + n) ≠ 0, "
                     "so every aₙ with n ≥ 1 is zero and y₁ = t. For r = −1, "
                     "aₙ = 0 except at n = 2, where a₂ is free and only adds a "
                     "multiple of t. Frobenius returns t and 1/t.",
                     r"y = C_1 t + \frac{C_2}{t}"),
                Step("y(1) = C₁ + C₂ = 2 and y'(1) = C₁ − C₂ = 0, so "
                     "C₁ = C₂ = 1."),
            ),
            equation="t**2*y'' + t*y' - y = 0", conditions="y(1) = 2, y'(1) = 0",
            answer="t + 1/t", answer_latex=r"y(t) = t + \frac{1}{t}",
        ),
    )),
    Section("The logarithm, and where it comes from", (
        Para(
            "When the second series is missing, what replaces it? The course "
            "has answered this question twice already. A repeated "
            "characteristic root gave one exponential where two were needed, "
            "and the second solution was te^(rt); a repeated Cauchy–Euler "
            "exponent gave one power, and the second was t^r ln t. Frobenius "
            "follows the same pattern, and the reduction-of-order chapter "
            "supplies the proof."
        ),
        Box(
            "theorem", "The second solution in the exceptional cases",
            "Let r₁ ≥ r₂ be the exponents at a regular singular point t = 0, "
            "and y₁ the Frobenius solution with exponent r₁. If r₁ = r₂, a "
            "second solution has the form y₁ ln t + t^(r₁+1)∑ bₙtⁿ: the "
            "logarithm is always present. If r₁ − r₂ = N is a positive "
            "integer, a second solution has the form below, with b₀ ≠ 0 and a "
            "constant C that may or may not be zero.",
            r"y_2 = C\,y_1\ln t + t^{r_2}\sum_{n=0}^{\infty}b_n t^{n}",
        ),
        Box(
            "proof", "Sketch, by reduction of order",
            "Reduction of order gives y₂ = y₁∫ e^(−∫p dt)/y₁² dt. Since "
            "p = p₀/t + (analytic), e^(−∫p) = t^(−p₀)g(t) with g analytic and "
            "g(0) ≠ 0; and y₁² = t^(2r₁)h(t) with h(0) = a₀² ≠ 0. The sum of the "
            "roots of r² + (p₀ − 1)r + q₀ is r₁ + r₂ = 1 − p₀, so "
            "−p₀ − 2r₁ = r₂ − r₁ − 1 = −1 − N, and the integrand is t^(−1−N) "
            "times the power series of g/h. Integrating term by term, the term "
            "of index N becomes a multiple of ln t and every other term a "
            "power t^(k−N). Multiplying by y₁ gives a multiple of y₁ ln t plus "
            "t^(r₂) times a series. When N = 0 the logarithm's coefficient is "
            "g(0)/h(0) ≠ 0, so it cannot vanish.",
            r"\frac{e^{-\int p\,dt}}{y_1^{2}} = t^{-1-N}\sum_{k=0}^{\infty}c_k t^{k}",
        ),
        Para(
            "In the order-1/2 example the logarithm's coefficient C turned out "
            "to be zero, which is why a plain second series existed; in the "
            "order-one example it is not, and that is why the series failed. "
            "The Cauchy–Euler case is the one where everything is visible at "
            "once, because y₁ is a pure power and nothing has to be summed."
        ),
        Worked(
            "A repeated exponent",
            "Solve t²y'' − 3ty' + 4y = 0 with y(1) = 1, y'(1) = 0.",
            (
                Step("p₀ = −3 and q₀ = 4, so the indicial equation is "
                     "r(r − 1) − 3r + 4 = r² − 4r + 4 = 0, a perfect square. "
                     "The exponents coincide: the extreme case of an integer "
                     "difference, N = 0.",
                     r"(r - 2)^{2} = 0 \;\Longrightarrow\; r_1 = r_2 = 2"),
                Step("Frobenius gives y₁ = t² and nothing more; the theorem "
                     "promises y₁ ln t, and for a pure Cauchy–Euler equation the "
                     "series part is zero. This is the Cauchy–Euler chapter's "
                     "repeated-root rule, and the same equation it solved with "
                     "y(1) = 0, y'(1) = 1; only the conditions are new.",
                     r"y = t^{2}\left(C_1 + C_2\ln t\right)"),
                Step("y(1) = C₁ = 1. Differentiating, y' = 2t(C₁ + C₂ ln t) + "
                     "C₂t, so y'(1) = 2C₁ + C₂ = 0 and C₂ = −2."),
            ),
            equation="t**2*y'' - 3*t*y' + 4*y = 0", conditions="y(1) = 1, y'(1) = 0",
            answer="t**2*(1 - 2*log(t))",
            answer_latex=r"y(t) = t^{2}\left(1 - 2\ln t\right)",
        ),
        Para(
            "For Bessel's equation of order zero the exponents are 0 and 0, "
            "so the second solution is logarithmic whatever else happens. "
            "Unlike the Cauchy–Euler case, its series part is not zero, and "
            "computing it is the standard technique for a logarithmic "
            "solution: substitute the form the theorem promises and match "
            "powers."
        ),
        Worked(
            "Bessel of order zero: the logarithmic solution",
            "The first solution of t²y'' + ty' + t²y = 0 at t = 0 is "
            "J₀(t) = 1 − t²/4 + t⁴/64 − t⁶/2304 + ⋯. Find the series part of "
            "the second solution y₂ = J₀ ln t + ∑ bₙtⁿ up to t⁶.",
            (
                Step("Write L[y] = t²y'' + ty' + t²y. For y = u ln t, "
                     "y' = u' ln t + u/t and y'' = u'' ln t + 2u'/t − u/t², and "
                     "the terms without a logarithm reduce to 2tu'. So the "
                     "ln t terms collect into (ln t)L[u].",
                     r"L[u\ln t] = (\ln t)\,L[u] + 2t\,u'"),
                Step("With u = J₀, L[J₀] = 0 and the logarithm drops out "
                     "entirely. What is left is an equation for the series "
                     "part alone, with a known right side.",
                     r"L\left[\sum b_n t^{n}\right] = -2t\,J_0'(t) = t^{2} - "
                     r"\frac{t^{4}}{8} + \frac{t^{6}}{192} - \cdots"),
                Step("t²y'' + ty' sends bₙtⁿ to n²bₙtⁿ, and t²y shifts by two, "
                     "so after n → n − 2 the left side is ∑(n²bₙ + bₙ₋₂)tⁿ. "
                     "At n = 0 the coefficient is 0·b₀ = 0, so b₀ is free; it "
                     "only adds a multiple of J₀, so take b₀ = 0. At n = 1, "
                     "b₁ = 0, and every odd bₙ follows it.",
                     r"n^{2}b_n + b_{n-2} = \left[t^{n}\right]\left(-2tJ_0'\right)"),
                Step("The even coefficients: 4b₂ = 1, 16b₄ + b₂ = −1/8, "
                     "36b₆ + b₄ = 1/192.",
                     r"b_2 = \frac{1}{4}, \qquad b_4 = -\frac{3}{128}, \qquad "
                     r"b_6 = \frac{11}{13824}"),
            ),
        ),
        Display(r"y_2 = J_0(t)\ln t + \frac{t^{2}}{4} - \frac{3t^{4}}{128} + "
                r"\frac{11t^{6}}{13824} - \cdots", "7"),
        Para(
            "Near t = 0, J₀ → 1, so y₂ behaves like ln t and is unbounded. "
            "That is the solution a vibrating drumhead throws away: the "
            "displacement at the centre must be finite, so only J₀ survives."
        ),
        Worked(
            "A logarithm at the pole of a sphere",
            "Legendre's equation with ℓ = 0 is (1 − t²)y'' − 2ty' = 0. Its "
            "exponents at t = 1 are both 0. The recurrence chapter found its "
            "solution with y(0) = 0, y'(0) = 1 as the series t + t³/3 + t⁵/5 "
            "+ ⋯ about the ordinary point 0, with radius exactly 1. Find the "
            "same solution again, now seen from the pole, and locate the "
            "logarithm.",
            (
                Step("From the classification above, p₀ = 1 and q₀ = 0 at t = 1, "
                     "so F(r) = r² and the exponent 0 is repeated. One solution "
                     "is analytic there — here it is the constant 1, the "
                     "Legendre polynomial P₀ — and the other must carry "
                     "ln(1 − t).",
                     r"F(r) = r^{2}"),
                Step("The equation is first order in y': ((1 − t²)y')' = 0, so "
                     "(1 − t²)y' = C and y' = C/(1 − t²). With y'(0) = 1, C = 1.",
                     r"y' = \frac{1}{1 - t^{2}}"),
                Step("Integrating by partial fractions with y(0) = 0 gives the "
                     "answer, which contains −(1/2)ln(1 − t): the logarithm the "
                     "repeated exponent promised, and by symmetry another at "
                     "t = −1. That logarithm is why the series about 0 could "
                     "reach no further than |t| = 1.",
                     r"y = \frac{1}{2}\ln\frac{1 + t}{1 - t}"),
            ),
            equation="(1 - t**2)*y'' - 2*t*y' = 0", conditions="y(0) = 0, y'(0) = 1",
            answer="log((1 + t)/(1 - t))/2",
            answer_latex=r"y(t) = \frac{1}{2}\ln\frac{1+t}{1-t}",
        ),
        Plot(
            "Bounded and logarithmic at a regular singular point",
            "The two solutions of Legendre's equation with ℓ = 0 on −1 < t < 1: "
            "the constant P₀ = 1, analytic at both poles, and "
            "(1/2)ln((1 + t)/(1 − t)), which grows without bound like a "
            "logarithm as t → ±1. A problem on the whole sphere needs a "
            "solution finite at both poles, and that requirement is what "
            "selects the Legendre polynomials.",
            (Curve("1 + 0*t", "P₀ = 1"),
             Curve("log((1 + t)/(1 - t))/2", "second solution")),
            t=(-0.995, 0.995), ylim=(-3.5, 3.5),
        ),
    )),
    Section("Bessel's equation in general", (
        Para(
            "With ν ≥ 0 the exponents of Bessel's equation are ±ν, and the "
            "larger one always produces a series. With r = ν the factor in "
            "the recurrence is F(ν + n) = n(n + 2ν), so a₁ = 0, every odd "
            "coefficient vanishes, and the even ones follow from the "
            "two-step recurrence below. Applying it m times gives (8)."
        ),
        Display(r"a_{2m} = -\frac{a_{2m-2}}{2m(2m+2\nu)} = "
                r"-\frac{a_{2m-2}}{4m(m+\nu)}"),
        Display(r"a_{2m} = \frac{(-1)^{m}a_0}{2^{2m}\,m!\,(\nu+1)(\nu+2)\cdots(\nu+m)}",
                "8"),
        Para(
            "The product (ν + 1)(ν + 2)⋯(ν + m) is a factorial that has lost "
            "its way: for ν = 0 it is m!, but for ν = 1/2 it is "
            "(3/2)(5/2)⋯. The function that makes sense of such products for "
            "every ν is the Gamma function, and the standard normalisation "
            "of the Bessel functions is written with it."
        ),
        Box(
            "definition", "The Gamma function",
            "For x > 0, Γ(x) is the integral below. Integrating by parts "
            "gives Γ(x + 1) = xΓ(x), and Γ(1) = 1, so Γ(n + 1) = n! for every "
            "whole number n: Γ extends the factorial. The substitution "
            "s = u² turns Γ(1/2) into the Gaussian integral, so Γ(1/2) = √π "
            "and Γ(3/2) = (1/2)Γ(1/2) = √π/2. For negative x that are not "
            "whole numbers, Γ is defined by running the rule backwards, "
            "Γ(x) = Γ(x + 1)/x; it has poles at 0, −1, −2, …, so 1/Γ is zero "
            "there, and it is negative between −1 and 0 (Γ(−1/2) = −2√π).",
            r"\Gamma(x) = \int_{0}^{\infty}s^{x-1}e^{-s}\,ds, \qquad "
            r"\Gamma(x+1) = x\,\Gamma(x)",
        ),
        Para(
            "Applying Γ(x + 1) = xΓ(x) m times gives "
            "Γ(ν + m + 1) = (ν + m)⋯(ν + 1)Γ(ν + 1), so the standard choice "
            "a₀ = 1/(2^ν Γ(ν + 1)) turns the product in (8) into a single "
            "Gamma value. The result is the Bessel function of the first "
            "kind, the solution that behaves like (t/2)^ν/Γ(ν + 1) at the "
            "origin."
        ),
        Display(r"J_\nu(t) = \sum_{m=0}^{\infty}\frac{(-1)^{m}}{m!\,\Gamma(m+\nu+1)}"
                r"\left(\frac{t}{2}\right)^{2m+\nu}", "9"),
        Para(
            "For ν = 1/2, (9) is (t/2)^(1/2)/Γ(3/2) times the series "
            "1 − t²/6 + t⁴/120 − ⋯ found in the order-1/2 example, which is "
            "(sin t)/t. With Γ(3/2) = √π/2 that is the closed form below, the "
            "y₁ of the order-1/2 example up to a constant."
        ),
        Display(r"J_{1/2}(t) = \sqrt{\frac{t}{2}}\cdot\frac{2}{\sqrt{\pi}}"
                r"\cdot\frac{\sin t}{t} = \sqrt{\frac{2}{\pi t}}\,\sin t"),
        Para(
            "For ν = 1, (9) is the series found for order one with a₀ = 1/2. "
            "When ν is not a whole number, the smaller exponent −ν gives a "
            "second solution J_(−ν) by the same formula with ν replaced by "
            "−ν — even when 2ν is an odd integer, as the order-1/2 example "
            "showed: the collision then falls at an odd step, where the "
            "right side of (6) holds only odd coefficients, all of them "
            "zero. When ν is a whole number n the collision is real: the "
            "terms with m < n have 1/Γ(m − n + 1) = 0, the formula gives "
            "J_(−n) = (−1)ⁿJₙ, no new solution at all, and the second "
            "solution carries a logarithm, as (7) does for ν = 0."
        ),
        Para(
            "Tables and later courses use one standard second solution, the "
            "Bessel function of the second kind Yν. For order zero it is a "
            "fixed combination of (7) and J₀, Y₀ = (2/π)[y₂ + (γ − ln 2)J₀] "
            "with Euler's constant γ ≈ 0.5772, so that its leading part is "
            "(2/π)(ln(t/2) + γ)J₀(t); for whole ν it contains Jν ln t in the "
            "same way. Every solution of Bessel's equation is c₁Jν + c₂Yν, and "
            "Yν is unbounded at t = 0 for every ν ≥ 0, which is the precise "
            "form of the drumhead's 'only J₀ survives'."
        ),
        Figure("indicial",
               "Bessel's equation, with the two halves of a Frobenius solution "
               "drawn separately. The dashed curve is the leading power "
               "(t/2)^ν/Γ(ν + 1) alone, which is all the indicial equation "
               "claims; the solid curve is the series (9) summed term by term; "
               "the dotted curve is the leading power of the other exponent, "
               "−ν. Drag ν between 0.25 and 3 and watch the solid and dashed "
               "curves agree near t = 0 and part further out — the readout "
               "reports how far the leading power alone stays within 5% of the "
               "series, and that distance grows as ν does. Set the terms "
               "slider to 1 and the solid curve is the dashed one; with the "
               "default 14 terms the sum drifts from the true Bessel function "
               "only near the right-hand end of the window, and at 22 it is "
               "accurate across it. Near ν = 0.5 the solid curve is "
               "sin t/√t up to a constant, and the dotted one blows up at the "
               "origin like 1/√t. For ν between 1 and 2 the dotted curve is "
               "drawn below the axis, because 1/Γ(1 − ν) is negative there; "
               "only its size matters. As ν approaches a whole number the "
               "dotted curve flattens towards the axis away from the origin, "
               "because its factor 1/Γ(1 − ν) vanishes there: the leading term "
               "of J_(−ν) is disappearing, and at a whole number the figure "
               "stops drawing it, since the second solution is the "
               "logarithmic one instead."),
    )),
    Section("How far the series reach, and what a few terms are worth", (
        Para(
            "Frobenius's theorem promises convergence on 0 < t < ρ, where ρ "
            "is governed by the power series of tp and t²q — in practice, by "
            "the distance from t = 0 to the nearest *other* singular point, "
            "complex ones included, exactly as in the recurrence chapter. The "
            "singular point at the centre does not limit the series; it is "
            "absorbed by t^r. For Bessel's equation and the examples above "
            "with polynomial brackets, ρ = ∞. For t(t − 1)²y'' + 3y' − y = 0 "
            "the exponents at t = 0 are 0 and −2, and only one of them gives a "
            "series: for r = −2, (6) yields a₁ = −13a₀ at n = 1 and then "
            "0·a₂ = −71a₀ at n = 2, the breakdown Bessel's order one showed, "
            "so the second solution carries a logarithm. The series with "
            "exponent 0, 1 + t/3 + t²/24 + t³/72 + ⋯, is guaranteed only on "
            "0 < t < 1, because the irregular point t = 1 is at distance 1. For Legendre's "
            "equation "
            "expanded about t = 1, the other pole t = −1 is at distance 2."
        ),
        Para(
            "Because the factorials in (8) grow so quickly, a handful of "
            "terms is very accurate near the origin. The alternating-series "
            "bound makes that quantitative whenever the terms decrease."
        ),
        Worked(
            "J₀(1) from three terms",
            "Estimate J₀(1) from the first three terms of (9) with ν = 0, and "
            "bound the error.",
            (
                Step("With ν = 0, (9) is ∑(−1)ᵐ(t/2)^(2m)/(m!)², that is "
                     "1 − t²/4 + t⁴/64 − t⁶/2304 + ⋯. At t = 1 the first three "
                     "terms give 1 − 0.25 + 0.015625.",
                     r"J_0(1) \approx 1 - \frac{1}{4} + \frac{1}{64} = 0.765625"),
                Step("The terms alternate and decrease in size, so the error is "
                     "less than the first omitted term, 1/2304 ≈ 4.34 × 10⁻⁴.",
                     r"\left|J_0(1) - 0.765625\right| < \frac{1}{2304} "
                     r"\approx 4.34\times 10^{-4}"),
                Step("The true value is J₀(1) ≈ 0.7651977, an error of about "
                     "4.27 × 10⁻⁴ — inside the bound, and almost equal to it, "
                     "as it should be when the next term is much smaller "
                     "again (1/147456 ≈ 6.8 × 10⁻⁶)."),
            ),
        ),
    )),
    Section("What Frobenius is for", (
        Para(
            "It is worth stating plainly what the method delivers. Frobenius tells you, before "
            "any series is summed, how every "
            "solution behaves at the singular point: like t^(r₁), like t^(r₂), "
            "or — in the exceptional cases — with a logarithm. Those exponents "
            "come from a quadratic that takes a minute to write down."
        ),
        Para(
            "In applications that is usually the decisive information. A "
            "drumhead, a cylinder, a sphere: the problem contains the "
            "singular point, the boundary condition there is 'finite', and "
            "the exponents say at once which solutions are finite. For Bessel "
            "of order ν > 0 it is the one behaving like t^ν; for order zero, "
            "the one without ln t; for Legendre at the poles, the one without "
            "ln(1 ∓ t). The other solution is discarded unseen, and the one "
            "that remains is the larger exponent's series, which the theorem "
            "guarantees always exists. That is why the hard case of the "
            "theory — the second solution when exponents differ by an "
            "integer — matters less in practice than its reputation suggests."
        ),
        Box(
            "remark", "What the app narrates",
            "Given an equation whose singular point is t = 0, the app's "
            "series narration classifies the point, forms the indicial "
            "equation and lists its roots, and then stops. The two examples "
            "the lesson itself solves, t²y'' + ty' − y = 0 and "
            "t²y'' − 3ty' + 4y = 0, are Cauchy–Euler equations, which the "
            "app can carry to an answer. The Frobenius series themselves are "
            "past what the app works out, and this chapter is where they are "
            "done by hand.",
        ),
    )),
    Section("Common errors", (
        Para(
            "The commonest slip is the one the Cauchy–Euler chapter warned "
            "about: writing r² + p₀r + q₀ instead of r(r − 1) + p₀r + q₀. The "
            "second is reading p₀ and q₀ off the wrong form of the equation. "
            "They are the limits of tp and t²q, where p and q come from the "
            "*standard* form; for 2t²y'' + 3ty' − y = 0 they are 3/2 and −1/2, "
            "not 3 and −1. Equivalently, divide through so that t²y'' has "
            "coefficient 1 before reading the others off."
        ),
        Para(
            "The third is classifying by the wrong criterion. A singular point "
            "is regular when tp and t²q are analytic — not p and q "
            "themselves, at least one of which is not — and one infinite "
            "limit makes it irregular. "
            "The fourth is concluding too much from an integer difference: "
            "it means the smaller exponent's series *may* fail, as for Bessel "
            "of order one, not that it does, as the order-1/2 example shows. "
            "The test is the recurrence itself at the step n = r₁ − r₂."
        ),
        Para(
            "Finally, keep track of where the series live. A Frobenius "
            "series with a fractional or negative exponent is a solution on "
            "t > 0; on t < 0 replace t^r by |t|^r, as the Cauchy–Euler chapter "
            "did, and treat the two half-lines as separate intervals."
        ),
    )),
    Section("Summary", (
        Para(
            "A singular point t₀ is regular when (t − t₀)p and (t − t₀)²q are "
            "analytic there; near such a point the equation looks like the "
            "Cauchy–Euler equation (t − t₀)²y'' + p₀(t − t₀)y' + q₀y = 0, and "
            "its solutions look like powers. Frobenius's method assumes "
            "y = t^r∑aₙtⁿ with a₀ ≠ 0; the lowest power gives the indicial "
            "equation r(r − 1) + p₀r + q₀ = 0, the same quadratic as the "
            "Cauchy–Euler chapter's, and the higher powers give the "
            "recurrence F(r + n)aₙ = (earlier terms). The larger exponent "
            "always yields a series. The smaller one does too unless the "
            "exponents differ by a whole number, where the two series can "
            "collide; then the second solution may carry y₁ ln t, and for a "
            "repeated exponent it always does. The series are guaranteed to "
            "converge at least out to the nearest other singular point, "
            "complex ones included. In practice the exponents "
            "alone decide which solutions are finite at the singular point, "
            "and that is usually the question the singular point was asking."
        ),
        Para(
            "That is also where the course ends, and it ends on the theme it "
            "has been circling since the first-order unit. The early units "
            "looked for formulas — an integrating factor, a characteristic "
            "root, a transform to invert, an eigenvector — and found them for "
            "families narrower than they looked. The nonlinear-systems unit "
            "gave formulas up and still read off what the solutions do from "
            "equilibria and their linearisations. This unit gave them up in a "
            "different way: the answer became a rule for coefficients, and "
            "at a singular point two exponents from a quadratic. Each step "
            "traded some explicitness for reach. The equations met here — "
            "Legendre's, Hermite's, Bessel's — are where a course on partial "
            "differential equations begins, when separating variables in a "
            "sphere, an oscillator or a drum hands back exactly these "
            "ordinary equations. The habit to carry there is the one every "
            "unit practised: before solving, ask what the equation already "
            "says — its singular points, its exponents, its radius, its "
            "equilibria — and let that decide what kind of answer to look for."
        ),
    )),
)
