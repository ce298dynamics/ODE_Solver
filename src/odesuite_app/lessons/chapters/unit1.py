"""Unit 1 chapters -- first-order equations (Edwards ch. 1)."""

from __future__ import annotations

from ..chapter import Box, Curve, Display, Figure, Para, Plot, Section, Step, Worked

__all__ = ["SEPARABLE", "LINEAR"]


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


LINEAR = (
    Section("Linear equations, and why separation fails on them", (
        Para(
            "Separation asks the right-hand side of y' = F(t, y) to be a "
            "product. The plainest equations that break that rule are the ones "
            "where two influences on the rate are *added*: y' = −2y + t says "
            "the quantity decays at a rate proportional to itself and is "
            "topped up at a rate that grows with time. The two contributions "
            "are summed, and no rearrangement turns a sum into a product. Yet "
            "this is the shape of a huge number of models — a tank with an "
            "inflow, a circuit with a source, a population with immigration — "
            "because physical influences on a rate usually add."
        ),
        Box(
            "definition", "First-order linear equation",
            "An equation is *linear* in y if y and y' appear only to the first "
            "power, are not multiplied together, and are not inside any other "
            "function. Dividing by the coefficient of y' puts it in standard "
            "form, and p and q may be any functions of t.",
            r"y' + p(t)\, y = q(t)",
        ),
        Para(
            "The word linear refers to y alone. The coefficients may be as "
            "nonlinear in t as they like: t² y' + (sin t) y = e^t is linear, and "
            "so is y' = y/t + ln t. What is forbidden is y², √y, sin y, "
            "e^y, or a product y·y'. So y' = y² + t is not linear (and not "
            "separable either — it is a Riccati equation, for which there is "
            "no general method), while y' = 3y + t is linear."
        ),
        Para(
            "When q(t) = 0 the equation is called *homogeneous*, and then it is "
            "separable after all: y' = −p(t)y separates into dy/y = −p dt. "
            "It is the forcing term q that spoils separation. The method of "
            "this lesson handles the forcing, and as a by-product it recovers "
            "the homogeneous solution too."
        ),
        Display(r"y' + 2y = t \;\;\text{(linear)}, \qquad "
                r"y' + 2y = y^{2} \;\;\text{(not linear)}"),
    )),
    Section("The integrating factor", (
        Para(
            "The idea comes from staring at the product rule. The derivative "
            "of a product μ(t)y(t) is μy' + μ'y. The left-hand side of a "
            "linear equation, multiplied by μ, is μy' + μpy. These two agree "
            "exactly when μ' = μp — and when they agree, the whole left side "
            "is the derivative of a single thing, μy, and one integration "
            "finishes the job."
        ),
        Display(r"\mu y' + \mu p\, y = (\mu y)' \quad\Longleftrightarrow\quad "
                r"\mu' = p\, \mu", "1"),
        Para(
            "Equation (1) for μ is itself separable, and its simplest solution "
            "is an exponential of the integral of p. That function is the "
            "*integrating factor*. Any constant multiple would do as well, so "
            "the constant of integration in ∫p dt is simply dropped."
        ),
        Display(r"\mu(t) = e^{\int p(t)\, dt}", "2"),
        Box(
            "theorem", "Solution of a linear first-order equation",
            "If p and q are continuous on an open interval I, then for every "
            "t₀ in I and every y₀ the problem y' + py = q, y(t₀) = y₀ has "
            "exactly one solution, it exists on the whole of I, and every "
            "solution of the equation is given by the formula below for some "
            "constant C.",
            r"y(t) = \frac{1}{\mu(t)}\left(\int \mu(t)\, q(t)\, dt + C\right)",
        ),
        Box(
            "proof", "",
            "Multiply the equation by μ = e^(∫p dt), which is never zero. By "
            "(1) the left side becomes (μy)', so (μy)' = μq. Integrating, "
            "μy = ∫μq dt + C, and dividing by μ gives the formula. Conversely, "
            "differentiating the formula shows that it satisfies the "
            "equation. On I the integrals exist because p and q are "
            "continuous, which is why the solution lives on all of I, and the "
            "initial condition fixes C uniquely.",
        ),
        Para(
            "Two parts of that theorem are unusually strong, and worth "
            "noticing because nonlinear equations lack them. The solution "
            "exists on the *whole* interval where the coefficients are "
            "continuous — there is no blow-up of the kind y' = y² showed in "
            "the last lesson. And it is unique, with no exceptional initial "
            "values. Linear equations are the well-behaved ones, and knowing "
            "that an equation is linear tells you a great deal about it "
            "before you solve it."
        ),
        Box(
            "warning", "Standard form first",
            "p is the coefficient of y *after* dividing by the coefficient of "
            "y'. For t·y' + 2y = t the integrating factor comes from p = 2/t, "
            "not from 2. Reading p off an equation that is not in standard "
            "form is the most common error with this method, and it produces "
            "a wrong μ that still looks reasonable.",
        ),
        Figure("integrating_factor",
               "The figure shows the method at work on one equation: the "
               "solution, the integrating factor, and the product μy whose "
               "derivative is the right-hand side μq."),
    )),
    Section("Worked examples", (
        Worked(
            "Constant coefficients",
            "Solve y' + 2y = t with y(0) = 1.",
            (
                Step("Here p = 2, so μ = e^(2t). Multiply through and recognise "
                     "the left side as a derivative:",
                     r"(e^{2t} y)' = t\, e^{2t}"),
                Step("Integrate by parts, with u = t and dv = e^(2t) dt:",
                     r"e^{2t} y = \frac{t}{2} e^{2t} - \frac{1}{4} e^{2t} + C"),
                Step("Divide by e^(2t), then apply y(0) = 1: 1 = 0 − 1/4 + C, "
                     "so C = 5/4.",
                     r"y = \frac{t}{2} - \frac{1}{4} + C e^{-2t}"),
            ),
            equation="y' + 2*y = t", conditions="y(0) = 1",
            answer="t/2 - 1/4 + 5*exp(-2*t)/4",
            answer_latex=r"y(t) = \frac{t}{2} - \frac{1}{4} + \frac{5}{4} e^{-2t}",
        ),
        Para(
            "Look at the shape of that answer. The term (5/4)e^(−2t) dies "
            "away, and what remains, t/2 − 1/4, does not depend on the initial "
            "value at all. The first part is called the *transient*, the "
            "second the *steady state*. Every solution, whatever its start, "
            "ends up following the same line — a property of the equation, "
            "not of any one solution, and Section 4 returns to it."
        ),
        Worked(
            "A variable coefficient",
            "Solve t·y' + y = t for t > 0, with y(1) = 1.",
            (
                Step("Divide by t for standard form: y' + y/t = 1. So p = 1/t, "
                     "and μ = e^(ln t) = t for t > 0.",
                     r"y' + \frac{1}{t}\, y = 1, \qquad \mu = t"),
                Step("The left side of the original equation was already "
                     "(ty)' — this equation came with its integrating factor "
                     "built in. Integrate:",
                     r"(t y)' = t \;\Longrightarrow\; t y = \frac{t^{2}}{2} + C"),
                Step("So y = t/2 + C/t, and y(1) = 1 gives 1/2 + C = 1, "
                     "so C = 1/2."),
            ),
            equation="t*y' + y = t", conditions="y(1) = 1",
            answer="t/2 + 1/(2*t)",
            answer_latex=r"y(t) = \frac{t}{2} + \frac{1}{2t}",
        ),
        Para(
            "The theorem promises a solution on the whole interval where p "
            "and q are continuous. Here p = 1/t is continuous on (0, ∞) but "
            "not at 0, so the solution through t = 1 lives on (0, ∞) — and "
            "indeed 1/(2t) blows up at t = 0. The interval was predictable "
            "from the equation before it was solved, which is never true of a "
            "nonlinear equation."
        ),
        Worked(
            "An integrating factor that is a negative power",
            "Solve y' = y/t + t for t > 0, with y(1) = 0.",
            (
                Step("Move the y term across: y' − y/t = t. Now p = −1/t, "
                     "with its minus sign, so ∫p dt = −ln t and μ = "
                     "e^(−ln t) = 1/t.",
                     r"y' - \frac{1}{t}\, y = t, \qquad \mu = \frac{1}{t}"),
                Step("Multiply through by 1/t. The left side is (y/t)', and "
                     "the right side is t · (1/t) = 1:",
                     r"\left(\frac{y}{t}\right)' = 1 \;\Longrightarrow\; "
                     r"\frac{y}{t} = t + C"),
                Step("So y = t² + Ct, and y(1) = 0 gives C = −1."),
            ),
            equation="y' = y/t + t", conditions="y(1) = 0",
            answer="t**2 - t", answer_latex=r"y(t) = t^{2} - t",
        ),
        Para(
            "The sign of p is where this example is usually lost. Moving y/t "
            "to the left changes its sign, and forgetting to do so gives "
            "μ = t instead of 1/t — after which the left side is not a "
            "derivative of anything, and the working quietly goes wrong. "
            "Writing the equation out in standard form, sign included, before "
            "computing μ costs one line and prevents it."
        ),
        Worked(
            "Forcing that matches the natural behaviour",
            "Solve y' − y = e^t with y(0) = 2.",
            (
                Step("p = −1, so μ = e^(−t), and the right-hand side becomes "
                     "e^(−t)·e^t = 1:",
                     r"(e^{-t} y)' = 1"),
                Step("Integrate: e^(−t)y = t + C, so y = (t + C)e^t. The "
                     "condition gives C = 2."),
            ),
            equation="y' - y = exp(t)", conditions="y(0) = 2",
            answer="(t + 2)*exp(t)", answer_latex=r"y(t) = (t + 2)\, e^{t}",
        ),
        Para(
            "The factor t in front of e^t appeared because the forcing e^t is "
            "itself a solution of the homogeneous equation y' − y = 0. The "
            "system is being pushed exactly the way it already wants to move, "
            "and the response grows faster than either alone. The same "
            "phenomenon returns at second order as *resonance*, where it "
            "breaks bridges."
        ),
        Worked(
            "A periodic forcing",
            "Solve y' + y = sin t with y(0) = 0.",
            (
                Step("μ = e^t, so (e^t y)' = e^t sin t. The integral of "
                     "e^t sin t is found by integrating by parts twice:",
                     r"\int e^{t} \sin t\, dt = \frac{e^{t}}{2}(\sin t - \cos t)"),
                Step("So e^t y = e^t(sin t − cos t)/2 + C, that is",
                     r"y = \frac{\sin t - \cos t}{2} + C e^{-t}"),
                Step("y(0) = 0 gives −1/2 + C = 0, so C = 1/2."),
            ),
            equation="y' + y = sin(t)", conditions="y(0) = 0",
            answer="(sin(t) - cos(t))/2 + exp(-t)/2",
            answer_latex=r"y(t) = \frac{\sin t - \cos t}{2} + \frac{1}{2} e^{-t}",
        ),
        Plot(
            "Every solution settles onto the same oscillation",
            "Solutions of y' + y = sin t from y(0) = −2, 0 and 2, with the "
            "forcing sin t for comparison. The terms Ce^(−t) die away within "
            "a few time units, and all three follow the steady state "
            "(sin t − cos t)/2: an oscillation with the forcing's period, a "
            "smaller amplitude 1/√2, and lagging behind the forcing by an "
            "eighth of a cycle.",
            (Curve("(sin(t) - cos(t))/2 - 1.5*exp(-t)", "y(0) = −2"),
             Curve("(sin(t) - cos(t))/2 + 0.5*exp(-t)", "y(0) = 0"),
             Curve("(sin(t) - cos(t))/2 + 2.5*exp(-t)", "y(0) = 2"),
             Curve("sin(t)", "forcing sin t")),
            t=(0.0, 15.0),
        ),
    )),
    Section("Transients, steady states, and the structure of the answer", (
        Para(
            "Every example has produced an answer of the same form: a function "
            "with no arbitrary constant, plus C times e^(−∫p dt). That is not "
            "a coincidence. It is what the formula of Theorem 2 says when it "
            "is split in two."
        ),
        Display(r"y(t) = y_p(t) + C\, e^{-\int p\, dt}", "3"),
        Para(
            "The first part, y_p, is one particular solution of the full "
            "equation — any one will do. The second is the general solution "
            "of the homogeneous equation y' + py = 0. So *every* solution of a "
            "linear equation is one particular solution plus a solution of the "
            "homogeneous equation. That sentence is the organising principle "
            "of Unit 3, where second-order linear equations are solved in "
            "exactly this two-part way."
        ),
        Box(
            "remark", "Why the answer comes in two parts",
            "If y₁ and y₂ both solve y' + py = q, their difference solves "
            "y' + py = 0, because the q's cancel. So any two solutions differ "
            "by a homogeneous solution — and once one particular solution is "
            "fixed, all the others are found by adding homogeneous ones.",
        ),
        Para(
            "When p is a positive constant the homogeneous part Ce^(−pt) "
            "decays, and every solution approaches the particular one. The "
            "initial condition then affects only the *transient*; the "
            "long-run behaviour, the steady state, is fixed by the forcing "
            "alone. This is why an engineer describing a circuit or a "
            "thermostat asks for the steady-state response to an input: after "
            "the transient has died, it is all that remains."
        ),
    )),
    Section("A second derivation: varying the constant", (
        Para(
            "The integrating factor is not the only way to reach Theorem 2, "
            "and a second derivation is worth seeing because it is the one "
            "that generalises. Start from the homogeneous equation y' + py = "
            "0, whose solutions are C·h(t) with h(t) = e^(−∫p dt). A constant "
            "multiple of h cannot solve the forced equation — plug it in and "
            "the left side is zero, not q. So let the constant vary: look for "
            "a solution of the form y = u(t)·h(t)."
        ),
        Display(r"y = u\, h \;\Longrightarrow\; y' + p\, y = u' h + "
                r"u\,(h' + p\, h) = u' h", "5"),
        Para(
            "The bracket h' + ph is zero because h solves the homogeneous "
            "equation, and that cancellation is the whole trick. What remains "
            "is u'h = q, so u' = q/h = qμ, since 1/h is exactly the integrating "
            "factor. Integrating gives u = ∫μq dt + C, and y = uh is the "
            "formula of Theorem 2 again."
        ),
        Para(
            "This route is called *variation of parameters*, and it returns in "
            "Unit 3 for second-order equations, where no integrating factor "
            "exists but the same idea — take the homogeneous solutions and let "
            "their constants vary — still produces a particular solution. "
            "Seeing it first here, where the algebra is one line, makes the "
            "second-order version much less mysterious."
        ),
    )),
    Section("Two methods, one equation", (
        Para(
            "Some equations are both separable and linear, and then either "
            "method works. Newton's law of cooling, y' = −k(y − A), is one: "
            "separable because the right side is a constant times a function "
            "of y, linear because it reads y' + ky = kA. Whichever method is "
            "used, the answer must be the same function, and comparing the two "
            "is a good check on both."
        ),
        Worked(
            "Solved as a linear equation",
            "Solve y' + 2ty = t with y(0) = 1.",
            (
                Step("p = 2t, so μ = e^(t²), and (e^(t²) y)' = t e^(t²). The "
                     "right side integrates by the substitution w = t²:",
                     r"e^{t^{2}} y = \frac{1}{2} e^{t^{2}} + C"),
                Step("So y = 1/2 + Ce^(−t²), and y(0) = 1 gives C = 1/2."),
                Step("As a check, the equation is also separable: "
                     "y' = t(1 − 2y), so dy/(1 − 2y) = t dt, and "
                     "−ln|1 − 2y|/2 = t²/2 + c leads to the same function.",
                     r"1 - 2y = -e^{-t^{2}}"),
            ),
            equation="y' + 2*t*y = t", conditions="y(0) = 1",
            answer="1/2 + exp(-t**2)/2",
            answer_latex=r"y(t) = \frac{1}{2} + \frac{1}{2} e^{-t^{2}}",
        ),
        Para(
            "When both apply, the linear method is usually the safer choice. "
            "Separation divides by g(y) and can lose an equilibrium solution; "
            "the integrating factor divides only by μ, which is never zero, so "
            "it cannot lose anything. Here separation divided by 1 − 2y and "
            "would have lost y = 1/2, which the linear method produced as the "
            "C = 0 member of the family without any special care."
        ),
        Para(
            "Knowing where a solution lives is the other place the theory "
            "pays. For y' + y/(t − 3) = 1 the coefficient p = 1/(t − 3) is "
            "continuous on (−∞, 3) and on (3, ∞) but not at 3. A solution with "
            "y(0) = 1 is guaranteed on (−∞, 3) and on no interval crossing 3; "
            "one with y(5) = 1 lives on (3, ∞). The equation is saying that t = "
            "3 is a wall, and it says so before anything is integrated."
        ),
        Box(
            "remark", "The interval comes from the coefficients",
            "For a linear equation the interval of existence is read off the "
            "standard form: the largest open interval containing t₀ on which "
            "p and q are both continuous. For a nonlinear equation there is no "
            "such rule, and the interval has to be found from the solution.",
        ),
    )),
    Section("Mixing problems", (
        Para(
            "The classic application of linear equations is a tank. Brine of "
            "concentration c_in flows in at rate r, the tank is kept stirred so "
            "that its concentration is uniform, and the mixture flows out at "
            "the same rate r, so the volume V stays constant. Let x(t) be the "
            "mass of salt in the tank. Its rate of change is the rate at which "
            "salt comes in minus the rate at which it goes out."
        ),
        Display(r"\frac{dx}{dt} = r\, c_{in} - \frac{r}{V}\, x", "4"),
        Para(
            "The outflow term needs a moment's thought. The concentration in "
            "the tank is x/V, and liquid leaves at rate r, so salt leaves at "
            "rate r·x/V. The equation is linear with constant coefficients, "
            "and its steady state is the salt the tank would hold if its "
            "concentration matched the inflow: x = V·c_in."
        ),
        Worked(
            "A stirred tank",
            "A 100-litre tank holds 5 kg of salt dissolved in water. Brine "
            "with 0.4 kg of salt per litre flows in at 5 L/min, and the "
            "mixture flows out at 5 L/min. Find the salt x(t) after t minutes.",
            (
                Step("Salt enters at 5 × 0.4 = 2 kg/min and leaves at "
                     "5·x/100 = x/20 kg/min:",
                     r"x' = 2 - \frac{x}{20}, \qquad x(0) = 5"),
                Step("In standard form x' + x/20 = 2, so μ = e^(t/20) and "
                     "(e^(t/20) x)' = 2e^(t/20). Integrating gives "
                     "e^(t/20) x = 40e^(t/20) + C.",
                     r"x = 40 + C e^{-t/20}"),
                Step("x(0) = 5 gives C = −35."),
            ),
            equation="y' = 2 - y/20", conditions="y(0) = 5",
            answer="40 - 35*exp(-t/20)",
            answer_latex=r"x(t) = 40 - 35\, e^{-t/20}",
        ),
        Plot(
            "Salt in the tank",
            "x(t) = 40 − 35e^(−t/20): it rises from 5 kg towards the 40 kg "
            "that 100 L at the inflow concentration of 0.4 kg/L would hold. "
            "The time constant is V/r = 20 minutes: after 20 minutes about 63% "
            "of the gap has closed, and after an hour 95%.",
            (Curve("40 - 35*exp(-t/20)", "salt, kg"),
             Curve("40 + 0*t", "steady state")),
            t=(0.0, 120.0), ylabel="salt, kg", ylim=(0.0, 45.0),
        ),
        Para(
            "If the inflow and outflow rates differ the volume changes, "
            "V(t) = V₀ + (r_in − r_out)t, and the coefficient of x becomes "
            "r_out/V(t), which depends on t. The equation is still linear and "
            "the integrating factor still works — it is simply a power of "
            "V(t) rather than an exponential. Linear equations with variable "
            "coefficients are exactly as solvable as constant ones, provided "
            "the integrals can be done."
        ),
    )),
    Section("Summary", (
        Para(
            "To solve a linear first-order equation: divide by the coefficient "
            "of y' to reach standard form y' + py = q; compute μ = e^(∫p dt), "
            "dropping the constant; multiply through and write the left side "
            "as (μy)'; integrate, remembering the constant this time; divide "
            "by μ; apply the initial condition. The solution lives on the "
            "largest interval containing t₀ on which p and q are continuous."
        ),
        Para(
            "The answer always splits into a particular solution plus C times "
            "the homogeneous solution, and when the homogeneous solution "
            "decays, the particular part is the steady state that every "
            "solution approaches. That split — particular plus homogeneous — "
            "is the idea from this lesson that the rest of the course uses "
            "most."
        ),
    )),
)
