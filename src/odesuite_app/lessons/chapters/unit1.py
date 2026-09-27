"""Unit 1 chapters -- first-order equations (Edwards ch. 1)."""

from __future__ import annotations

from ..chapter import Box, Curve, Display, Figure, Para, Plot, Section, Step, Worked

__all__ = ["SEPARABLE"]


SEPARABLE = (
    Section("What makes an equation separable", (
        Para(
            "A first-order differential equation says how fast an unknown "
            "function y(t) is changing, in terms of where it is and when: "
            "y' = F(t, y). For a general right-hand side F there is no method "
            "at all. Nobody knows how to solve y' = sin(t + y²) in closed form, "
            "and nobody expects to. What a first course does instead is pick "
            "out the *shapes* of F for which something can be done, learn a "
            "technique for each shape, and learn to recognise which shape an "
            "equation has. The first and most forgiving of those shapes is the "
            "product."
        ),
        Box(
            "definition", "Separable equation",
            "A first-order equation is *separable* if its right-hand side can "
            "be written as a function of t alone multiplied by a function of y "
            "alone.",
            r"\frac{dy}{dt} = f(t)\, g(y)",
        ),
        Para(
            "The test is whether F *factors*, and it is worth being careful "
            "about what that means. The factors may be anything at all — a "
            "polynomial, an exponential, a constant, a square root — but each "
            "must involve only one of the two variables. A constant counts as a "
            "function of t (or of y): the equation y' = 3y is separable with "
            "f(t) = 3 and g(y) = y, and y' = t² is separable with g(y) = 1."
        ),
        Para(
            "Some equations are separable only after a little algebra. The "
            "right-hand side of y' = e^(t + y) is not visibly a product, but "
            "e^(t + y) = e^t · e^y, and that is. Likewise y' = ty + t = t(y + 1) "
            "factors once the common t is taken out. Others never factor, "
            "however they are rearranged: y' = t + y is a sum of a t-part and "
            "a y-part, and no algebra turns a sum into a product. That equation "
            "is linear, and it is the subject of the next lesson."
        ),
        Display(r"y' = t e^{2y} \quad \text{(separable)}, \qquad "
                r"y' = t + y \quad \text{(not separable)}"),
        Para(
            "The shape turns out to cover a great deal of what arises in "
            "practice, and the reason is physical. A natural law usually says "
            "that a rate is *proportional* to some amount: a population grows "
            "at a rate proportional to its size, a hot object cools at a rate "
            "proportional to how much hotter it is than the room, a reactant "
            "is used up at a rate proportional to its concentration. "
            "Proportionality is multiplication, and multiplication is exactly "
            "what separability asks for."
        ),
    )),
    Section("The method, and why it works", (
        Para(
            "The recipe is short. Divide both sides by g(y) so that all the y "
            "is on the left, integrate both sides — the left with respect to "
            "y, the right with respect to t — and solve for y if you can. "
            "Written with Leibniz's notation the steps look like algebra on "
            "the symbols dy and dt:"
        ),
        Display(r"\frac{dy}{g(y)} = f(t)\, dt \quad\Longrightarrow\quad "
                r"\int \frac{dy}{g(y)} = \int f(t)\, dt", "1"),
        Para(
            "That notation is a convenience, and it is fair to ask whether "
            "moving dt across the equals sign is legitimate. It is, but the "
            "honest reason is the chain rule, not algebra on differentials. "
            "The theorem below says exactly what has been proved, and the "
            "proof is short enough to read in full."
        ),
        Box(
            "theorem", "Solutions of a separable equation",
            "Let G be an antiderivative of 1/g and H an antiderivative of f. "
            "If y(t) solves y' = f(t) g(y) on an interval where g(y(t)) is "
            "never zero, then there is a constant C with",
            r"G(y(t)) = H(t) + C",
        ),
        Box(
            "proof", "",
            "Divide the equation by g(y(t)), which is allowed because it is "
            "never zero: y'(t)/g(y(t)) = f(t). By the chain rule the left side "
            "is the derivative of G(y(t)), since G' = 1/g. The right side is "
            "the derivative of H(t). Two functions with the same derivative on "
            "an interval differ by a constant, so G(y(t)) − H(t) = C. Every "
            "step runs backwards as well, which is why the implicit equation "
            "G(y) = H(t) + C describes the solutions and nothing else.",
        ),
        Para(
            "Two things in that argument matter later. First, only *one* "
            "constant of integration appears. Integrating both sides of (1) "
            "seems to produce two, but they can be combined into one, and "
            "writing both is harmless but wasteful. Second, the division by "
            "g(y) is an assumption, and wherever g(y) = 0 the argument says "
            "nothing. Section 4 is about what hides there."
        ),
        Para(
            "The result G(y) = H(t) + C is an *implicit* solution: an equation "
            "that y satisfies, rather than a formula for y. Often it can be "
            "solved for y, and then it should be. Sometimes it cannot, and the "
            "implicit form is then the answer — a perfectly good one, since "
            "it determines y at every t and can be plotted as a level curve."
        ),
        Figure("separable_family",
               "The figure draws the solutions of a separable equation as a "
               "family, one curve for each value of the constant C. Change C "
               "and the whole curve moves; no two curves cross."),
    )),
    Section("Worked examples", (
        Para(
            "The examples below run from routine to delicate. Read each "
            "solution with a pencil, and check the answer before reading the "
            "next one: substituting a solution back into its equation is the "
            "one check that needs no trust in anybody's working, and every "
            "answer here has been checked that way."
        ),
        Worked(
            "Growth whose rate increases with time",
            "Solve y' = 2ty with y(0) = 3.",
            (
                Step("The right-hand side is the product of f(t) = 2t and "
                     "g(y) = y. Divide by y and integrate both sides:",
                     r"\int \frac{dy}{y} = \int 2t\, dt \quad\Longrightarrow"
                     r"\quad \ln|y| = t^{2} + C"),
                Step("Exponentiate. The constant e^C is positive, and the "
                     "absolute value allows either sign, so the two combine "
                     "into a single arbitrary constant A:",
                     r"y = A e^{t^{2}}"),
                Step("The condition y(0) = 3 gives A e⁰ = A = 3."),
            ),
            equation="y' = 2*t*y", conditions="y(0) = 3",
            answer="3*exp(t**2)", answer_latex=r"y(t) = 3 e^{t^{2}}",
        ),
        Para(
            "Notice how the constant changed identity on the way: C, then "
            "e^C, then ±e^C, then A. That is normal, and nothing is gained by "
            "keeping track of which is which. What matters is that one "
            "arbitrary constant survives to the end, and that the initial "
            "condition is used *after* the general solution is found."
        ),
        Worked(
            "An implicit solution, and choosing a branch",
            "Solve y' = t/y with y(0) = −2.",
            (
                Step("Separate and integrate:",
                     r"\int y\, dy = \int t\, dt \quad\Longrightarrow\quad "
                     r"\frac{y^{2}}{2} = \frac{t^{2}}{2} + C"),
                Step("So y² − t² = 2C: every solution lies on a hyperbola. "
                     "The condition gives 4 − 0 = 2C, so y² = t² + 4."),
                Step("Solving for y gives two branches, y = ±√(t² + 4). Only "
                     "one of them passes through (0, −2), and it is the "
                     "negative one. The positive branch is the solution through "
                     "(0, 2), a different problem."),
            ),
            equation="y' = t/y", conditions="y(0) = -2",
            answer="-sqrt(t**2 + 4)", answer_latex=r"y(t) = -\sqrt{t^{2} + 4}",
        ),
        Para(
            "The step that decided the sign is the one most often skipped. A "
            "square root has two signs, and the equation alone does not choose "
            "between them; the initial condition does. Writing +√ out of habit "
            "produces a function that satisfies the differential equation and "
            "misses the condition — right equation, wrong solution."
        ),
        Worked(
            "Newton's law of cooling",
            "A cup of coffee at 90 °C is left in a 20 °C room. Its temperature "
            "falls at a rate proportional to its excess over the room, "
            "y' = −0.2(y − 20), with t in minutes. Find y(t).",
            (
                Step("The right-hand side is a constant times a function of y, "
                     "so it is separable with f(t) = −0.2. Divide by y − 20:",
                     r"\int \frac{dy}{y - 20} = \int -0.2\, dt \quad"
                     r"\Longrightarrow\quad \ln|y - 20| = -0.2t + C"),
                Step("Exponentiate and absorb the sign into the constant:",
                     r"y - 20 = A e^{-0.2t}"),
                Step("At t = 0, 90 − 20 = A, so A = 70."),
            ),
            equation="y' = -0.2*(y - 20)", conditions="y(0) = 90",
            answer="20 + 70*exp(-0.2*t)",
            answer_latex=r"y(t) = 20 + 70 e^{-0.2t}",
        ),
        Plot(
            "Cooling towards the room, from three starting temperatures",
            "Each curve solves y' = −0.2(y − 20) from a different start: 90 °C, "
            "50 °C and 5 °C (a cold drink warming up). All three approach the "
            "room temperature 20 °C, the equilibrium solution, and the gap "
            "shrinks by the same factor e^(−0.2) every minute whatever it was "
            "to begin with.",
            (Curve("20 + 70*exp(-0.2*t)", "from 90 °C"),
             Curve("20 + 30*exp(-0.2*t)", "from 50 °C"),
             Curve("20 - 15*exp(-0.2*t)", "from 5 °C"),
             Curve("20 + 0*t", "room, 20 °C")),
            t=(0.0, 25.0), ylabel="temperature, °C",
        ),
        Worked(
            "A solution that stops existing",
            "Solve y' = y² with y(0) = 1, and say where the solution exists.",
            (
                Step("Separate and integrate:",
                     r"\int y^{-2}\, dy = \int dt \quad\Longrightarrow\quad "
                     r"-\frac{1}{y} = t + C"),
                Step("The condition gives −1 = C, so −1/y = t − 1 and y = "
                     "1/(1 − t)."),
                Step("The formula is fine for every t except t = 1, where it "
                     "blows up. A solution of an initial value problem lives on "
                     "one interval containing the initial time, so this one is "
                     "defined on (−∞, 1) and on no larger interval.",
                     r"y(t) = \frac{1}{1 - t}, \qquad -\infty < t < 1"),
            ),
            equation="y' = y**2", conditions="y(0) = 1",
            answer="1/(1 - t)", answer_latex=r"y(t) = \frac{1}{1 - t}",
        ),
        Para(
            "Nothing in the equation y' = y² looks dangerous. The right-hand "
            "side is a polynomial, smooth everywhere, and yet the solution "
            "reaches infinity in finite time. This is a genuinely nonlinear "
            "phenomenon: the larger y gets, the faster it grows, and the growth "
            "feeds itself fast enough to escape. A linear equation cannot do "
            "this — its solutions exist for as long as its coefficients are "
            "continuous — which is one reason the distinction between linear "
            "and nonlinear matters so much."
        ),
        Plot(
            "Blow-up in finite time",
            "Solutions of y' = y² from y(0) = 1 and y(0) = 1/2, which are "
            "1/(1 − t) and 1/(2 − t). Each runs off to infinity at a finite "
            "time — t = 1 and t = 2 — and a larger start escapes sooner. The "
            "graphs are cut at y = 12.",
            (Curve("Piecewise((1/(1 - t), t < 0.92), (nan, True))", "y(0) = 1"),
             Curve("Piecewise((1/(2 - t), t < 1.92), (nan, True))", "y(0) = 1/2")),
            t=(-2.0, 1.9), ylim=(0.0, 12.0),
        ),
        Worked(
            "The logistic equation",
            "Solve y' = y(1 − y) with y(0) = 1/2.",
            (
                Step("Divide by y(1 − y) and split into partial fractions, "
                     "since 1/(y(1 − y)) = 1/y + 1/(1 − y):",
                     r"\int \left(\frac{1}{y} + \frac{1}{1 - y}\right) dy "
                     r"= \int dt"),
                Step("Integrate. The second term gives −ln|1 − y|, so the left "
                     "side is ln|y/(1 − y)|:",
                     r"\ln\left|\frac{y}{1 - y}\right| = t + C"),
                Step("Exponentiate: y/(1 − y) = A eᵗ. At t = 0 the left side is "
                     "(1/2)/(1/2) = 1, so A = 1. Solving y = eᵗ(1 − y) for y "
                     "gives y = eᵗ/(1 + eᵗ), which is the same as "
                     "1/(1 + e^(−t)).",
                     r"y(t) = \frac{1}{1 + e^{-t}}"),
            ),
            equation="y' = y*(1 - y)", conditions="y(0) = 1/2",
            answer="1/(1 + exp(-t))", answer_latex=r"y(t) = \frac{1}{1 + e^{-t}}",
        ),
    )),
    Section("Solutions lost by dividing", (
        Para(
            "Every example so far began by dividing by g(y), and the theorem "
            "of Section 2 was careful to assume g(y(t)) is never zero. The "
            "assumption is not decoration. If g(c) = 0 for some number c, "
            "then the constant function y(t) = c satisfies the equation — its "
            "derivative is zero, and so is f(t)g(c) — and dividing by g(y) "
            "throws that solution away without a trace."
        ),
        Box(
            "definition", "Equilibrium solution",
            "A constant function y(t) = c that solves y' = f(t)g(y). For a "
            "separable equation these are exactly the zeros of g.",
            r"g(c) = 0 \;\Longrightarrow\; y(t) \equiv c \text{ is a solution}",
        ),
        Para(
            "In the logistic example, g(y) = y(1 − y) vanishes at y = 0 and y "
            "= 1, and both constants are solutions: a population of zero stays "
            "zero, and a population at capacity stays at capacity. Neither "
            "appears in the formula y/(1 − y) = Aeᵗ for any finite A. The "
            "solution y = 0 can be recovered by allowing A = 0, but y = 1 "
            "cannot be recovered at all — it corresponds to A = ∞. So the "
            "general solution of the logistic equation is the one-parameter "
            "family *together with* y = 1."
        ),
        Box(
            "warning", "Check g(y) = 0 before you divide",
            "Find the zeros of g first and write them down as solutions. Then "
            "divide. An answer that omits an equilibrium solution is "
            "incomplete, and on an exam it is marked that way.",
        ),
        Worked(
            "The solution the method misses",
            "Solve y' = y² with y(0) = 0.",
            (
                Step("The formula from Example 4, y = −1/(t + C), can never "
                     "equal zero, whatever C is. Taken on its own it says this "
                     "problem has no solution."),
                Step("But g(y) = y² vanishes at y = 0, so y(t) = 0 is an "
                     "equilibrium solution, and it satisfies the condition. "
                     "That is the answer.",
                     r"y(t) \equiv 0"),
            ),
            equation="y' = y**2", conditions="y(0) = 0",
            answer="0", answer_latex=r"y(t) = 0",
        ),
        Para(
            "A related and subtler failure happens when g is zero *and* fails "
            "to be smooth there. The equation y' = y^(1/3) with y(0) = 0 has "
            "the equilibrium solution y = 0, and it also has y = (2t/3)^(3/2) "
            "for t ≥ 0, which separation finds — and infinitely many more, "
            "which sit at zero for a while and then leave. Two different "
            "solutions through one point means the initial value problem does "
            "not determine its solution. The lesson on slope fields and "
            "uniqueness explains exactly when this can and cannot happen; for "
            "now, the point is that separation of variables is not what "
            "decides uniqueness."
        ),
    )),
    Section("Implicit solutions and where solutions live", (
        Para(
            "Solving G(y) = H(t) + C for y is not always possible, and it is "
            "not always necessary. Consider y' = (3t² + 1)/(1 + 2y). Separating "
            "gives (1 + 2y) dy = (3t² + 1) dt, and integrating gives y + y² = "
            "t³ + t + C. That is a quadratic in y and can be solved by the "
            "quadratic formula, but for an equation like y' = t/(y + eʸ) the "
            "implicit relation (y²/2 + eʸ = t²/2 + C) cannot be solved in "
            "elementary functions at all. The relation is the answer, and a "
            "computer can plot its level curves as easily as any formula."
        ),
        Para(
            "Every solution of an initial value problem lives on an "
            "*interval*, and the largest interval containing the initial time "
            "on which the formula is a valid solution is part of the answer. "
            "Three things end an interval: the formula blowing up, as for "
            "1/(1 − t); the formula stopping being real, as a square root of a "
            "negative number; and the division by g(y) becoming illegal, "
            "where the solution meets an equilibrium it was not supposed to "
            "touch."
        ),
        Worked(
            "A solution that ends because a square root does",
            "Solve y' = −t/y with y(0) = 2, and find its interval.",
            (
                Step("Separating: y dy = −t dt, so y²/2 = −t²/2 + C, that is "
                     "y² + t² = 2C. The condition gives 2C = 4.",
                     r"y^{2} + t^{2} = 4"),
                Step("The branch through (0, 2) is the upper half of the "
                     "circle. It is real only while t² < 4, and at t = ±2 the "
                     "slope −t/y becomes infinite: the solution reaches the "
                     "t-axis vertically and cannot be continued as a function.",
                     r"y(t) = \sqrt{4 - t^{2}}, \qquad -2 < t < 2"),
            ),
            equation="y' = -t/y", conditions="y(0) = 2",
            answer="sqrt(4 - t**2)", answer_latex=r"y(t) = \sqrt{4 - t^{2}}",
        ),
        Plot(
            "Solutions of y' = −t/y are semicircles",
            "Upper halves of the circles y² + t² = r² for r = 1, 2 and 3. Each "
            "solution exists only for −r < t < r, and ends where its tangent "
            "turns vertical — a solution with a domain set by its initial "
            "value, which linear equations never have.",
            (Curve("sqrt(1 - t**2)", "r = 1"), Curve("sqrt(4 - t**2)", "r = 2"),
             Curve("sqrt(9 - t**2)", "r = 3")),
            t=(-3.0, 3.0), ylim=(0.0, 3.3),
        ),
    )),
    Section("Separable models", (
        Para(
            "The equation y' = ky, with k a constant, is the most important "
            "separable equation of all, and it deserves a statement of its "
            "own. Separating gives ln|y| = kt + C, so every solution is a "
            "constant multiple of e^(kt). With y(0) = y₀ the constant is y₀."
        ),
        Box(
            "theorem", "Natural growth and decay",
            "The solution of y' = ky with y(0) = y₀ is y = y₀ e^(kt). For k > 0 "
            "it grows, doubling every ln 2 / k; for k < 0 it decays, halving "
            "every ln 2 / |k|.",
            r"y' = ky,\;\; y(0) = y_0 \;\Longrightarrow\; y(t) = y_0 e^{kt}",
        ),
        Para(
            "Radioactive decay is the textbook instance. A sample of carbon-14 "
            "loses a fixed fraction of its atoms per unit time, so its amount "
            "obeys y' = −ky, and the half-life T — the time for half of it to "
            "go — fixes k through e^(−kT) = 1/2, that is k = ln 2 / T. For "
            "carbon-14, T is about 5730 years."
        ),
        Worked(
            "Radiocarbon",
            "Carbon-14 has a half-life of 5730 years. Write the fraction of the "
            "original amount remaining after t years, and find how old a "
            "sample is that retains 30% of its carbon-14.",
            (
                Step("With k = ln 2/5730, the fraction obeys y' = −ky with "
                     "y(0) = 1, so y = e^(−kt), which can also be written "
                     "2^(−t/5730).",
                     r"y(t) = e^{-t \ln 2 / 5730} = 2^{-t/5730}"),
                Step("Set y = 0.3 and take logarithms: −t ln 2 / 5730 = ln 0.3, "
                     "so t = 5730 · ln(1/0.3)/ln 2, which is about 9950 "
                     "years.",
                     r"t = 5730\, \frac{\ln(10/3)}{\ln 2} \approx 9950 "
                     r"\text{ years}"),
            ),
            equation="y' = -log(2)/5730*y", conditions="y(0) = 1",
            answer="exp(-log(2)*t/5730)",
            answer_latex=r"y(t) = e^{-t\ln 2/5730}",
        ),
        Para(
            "Two features of that computation are worth keeping. The half-life "
            "does not depend on how much there is — every 5730 years half of "
            "whatever remains decays — which is what proportional decay "
            "means. And the answer to the dating question came from the "
            "*solution*, never from the differential equation directly: the "
            "equation says how fast, the solution says how much and when."
        ),
    )),
    Section("Summary", (
        Para(
            "To solve a separable equation: check that the right-hand side "
            "factors as f(t)g(y); find the zeros of g and record them as "
            "equilibrium solutions; divide by g(y) and integrate both sides; "
            "add one constant; solve for y if possible; use the initial "
            "condition to fix the constant and, where a root or a sign is "
            "involved, the branch; and state the interval on which the "
            "solution exists. Then substitute the answer back into the "
            "equation. It takes a minute, and it catches almost every error "
            "the method invites."
        ),
        Para(
            "The next lessons meet equations that do not separate. The "
            "integrating factor handles linear equations, which separation "
            "cannot touch; exact equations and substitutions handle others. "
            "All of them end, one way or another, with an integration like "
            "the ones in this lesson, which is why this technique comes first."
        ),
    )),
)
