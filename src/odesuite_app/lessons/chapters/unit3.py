"""Unit 3 chapters -- second-order linear equations (Edwards ch. 3)."""

from __future__ import annotations

from ..chapter import Box, Curve, Display, Figure, Para, Plot, Section, Step, Worked

__all__ = ["SUPERPOSITION", "ROOTS", "UNDETERMINED", "VARIATION",
           "REDUCTION"]


REDUCTION = (
    Section("Half an answer", (
        Para(
            "For constant coefficients the characteristic equation hands over "
            "both independent solutions at once. For variable coefficients "
            "there is no such recipe, and in general no formula at all. But "
            "surprisingly often *one* solution can be found — spotted by "
            "inspection, given by the physics, read from a table, or found by "
            "trying a power of t or an exponential — and the question becomes "
            "how to get the second. Reduction of order answers it completely: "
            "given one nonzero solution of a second-order linear equation, a "
            "second, independent one follows by solving a first-order "
            "equation, which Unit 1 always can."
        ),
        Para(
            "The idea is the same one variation of parameters used, applied "
            "to a single known solution. A constant multiple cy₁ is useless, "
            "since it is just y₁ again. So let the constant vary: look for a "
            "second solution y = v(t)y₁(t) and ask what equation v must "
            "satisfy. The answer turns out to be an equation in v' alone, "
            "which is why the order drops by one."
        ),
        Box(
            "definition", "Reduction of order",
            "Given one solution y₁ of y'' + p(t)y' + q(t)y = 0, the method of "
            "*reduction of order* seeks a second solution in the form v·y₁, "
            "and obtains a first-order equation for w = v'.",
            r"y_2 = v(t)\, y_1(t)",
        ),
    )),
    Section("The substitution, carried out", (
        Para(
            "With y = vy₁, the product rule gives y' = v'y₁ + vy₁' and "
            "y'' = v''y₁ + 2v'y₁' + vy₁''. Substitute into y'' + py' + qy = 0 "
            "and collect the terms by v, v' and v''."
        ),
        Display(r"v\,(y_1'' + p y_1' + q y_1) + v'\,(2y_1' + p\, y_1) + "
                r"v''\, y_1 = 0", "1"),
        Para(
            "The bracket multiplying v is the equation applied to y₁, and it "
            "is zero because y₁ is a solution. That single cancellation is the "
            "whole method. What remains contains v' and v'' but not v, so with "
            "w = v' it is a first-order equation — linear and separable at "
            "once."
        ),
        Display(r"y_1\, w' + (2y_1' + p\, y_1)\, w = 0", "2"),
        Para(
            "Separating (2): w'/w = −2y₁'/y₁ − p. Integrating gives "
            "ln w = −2 ln y₁ − ∫p dt, and exponentiating produces a formula "
            "that needs no further thought."
        ),
        Box(
            "theorem", "The second solution",
            "If y₁ is a solution of y'' + py' + qy = 0 that is nonzero on an "
            "interval I, then the function below is a second solution on I, "
            "independent of y₁.",
            r"y_2 = y_1 \int \frac{e^{-\int p\, dt}}{y_1^{2}}\, dt",
        ),
        Box(
            "proof", "",
            "The derivation above shows y₂ satisfies the equation. For "
            "independence, W(y₁, y₂) = y₁(v'y₁ + vy₁') − y₁'vy₁ = y₁²v' = "
            "e^(−∫p dt), an exponential, which is never zero. Both constants "
            "of integration can be dropped: one would multiply y₂ by a "
            "constant, the other would add a multiple of y₁.",
        ),
        Box(
            "warning", "Standard form, again",
            "p is the coefficient of y' after dividing by the coefficient of "
            "y''. For t·y'' − (t + 1)y' + y = 0 it is −(t + 1)/t, not −(t + 1). "
            "The mistake goes unnoticed through every later step and "
            "produces a y₂ that fails when substituted.",
        ),
    )),
    Section("Worked examples", (
        Worked(
            "An exponential and a polynomial",
            "One solution of t·y'' − (t + 1)y' + y = 0 is e^t. Find a second, "
            "and the solution with y(1) = 0, y'(1) = 1.",
            (
                Step("Standard form: p = −(t + 1)/t = −1 − 1/t, so "
                     "∫p dt = −t − ln t and e^(−∫p) = te^t (for t > 0). Divide "
                     "by y₁² = e^(2t):",
                     r"v' = \frac{t e^{t}}{e^{2t}} = t e^{-t}"),
                Step("Integrate by parts: v = −(t + 1)e^(−t), so "
                     "y₂ = v·e^t = −(t + 1). The second solution is a "
                     "polynomial — nothing about the equation suggested one.",
                     r"y = c_1 e^{t} + c_2 (t + 1)"),
                Step("The conditions give c₁e + 2c₂ = 0 and c₁e + c₂ = 1, so "
                     "c₂ = −1 and c₁ = 2/e."),
            ),
            equation="t*y'' - (t + 1)*y' + y = 0", conditions="y(1) = 0, y'(1) = 1",
            answer="-t + 2*exp(t - 1) - 1",
            answer_latex=r"y(t) = 2e^{t-1} - t - 1",
        ),
        Worked(
            "A power and an exponential",
            "y₁ = t solves t²y'' − t(t + 2)y' + (t + 2)y = 0. Find a second "
            "solution and the solution with y(1) = 1, y'(1) = 0.",
            (
                Step("p = −(t + 2)/t = −1 − 2/t, so e^(−∫p) = t²e^t. Dividing by "
                     "y₁² = t² leaves v' = e^t — the powers of t cancel, which "
                     "is the sign the arithmetic is right.",
                     r"v' = e^{t}, \qquad v = e^{t}, \qquad y_2 = t e^{t}"),
                Step("With y = c₁t + c₂te^t: y(1) = c₁ + c₂e = 1 and "
                     "y'(1) = c₁ + 2c₂e = 0, so c₂ = −1/e and c₁ = 2."),
            ),
            equation="t**2*y'' - t*(t + 2)*y' + (t + 2)*y = 0",
            conditions="y(1) = 1, y'(1) = 0",
            answer="2*t - t*exp(t - 1)", answer_latex=r"y(t) = 2t - t\,e^{t-1}",
        ),
        Plot(
            "Solutions of the two examples",
            "The solution 2e^(t−1) − t − 1 of the first example "
            "and 2t − te^(t−1) of the second, both on (0, 3]. Each passes "
            "through its initial point at t = 1 with the prescribed slope; "
            "their shapes come entirely from the second solutions that "
            "reduction of order found.",
            (Curve("2*exp(t - 1) - t - 1", "example 1"),
             Curve("2*t - t*exp(t - 1)", "example 2")),
            t=(0.05, 3.0), ylim=(-6.0, 6.0),
        ),
        Figure("reduction",
               "The family t²y″ − t(t + a)y′ + (t + a)y = 0, whose first solution "
               "is always t. The second comes from the narrator, and the dashed "
               "curve is v = y₂/y₁ — not constant, which is why y₂ is new."),
    )),
    Section("Where t·e^(rt) really comes from", (
        Para(
            "The characteristic-roots lesson asserted that a double root r "
            "gives a second solution te^(rt), and justified it by checking. "
            "Reduction of order *derives* it. For y'' − 2ry' + r²y = 0, whose "
            "characteristic polynomial is (λ − r)², take y₁ = e^(rt). Then "
            "p = −2r, so e^(−∫p) = e^(2rt), and dividing by y₁² = e^(2rt) "
            "leaves v' = 1."
        ),
        Display(r"v' = \frac{e^{2rt}}{e^{2rt}} = 1 \;\Longrightarrow\; "
                r"v = t \;\Longrightarrow\; y_2 = t e^{rt}"),
        Worked(
            "A double root, from first principles",
            "Solve y'' − 2y' + y = 0 with y(0) = 1, y'(0) = 2, using reduction "
            "of order from y₁ = e^t.",
            (
                Step("p = −2, so v' = e^(2t)/e^(2t) = 1, v = t and y₂ = te^t.",
                     r"y = (c_1 + c_2 t)\, e^{t}"),
                Step("y(0) = c₁ = 1; y'(0) = c₁ + c₂ = 2 gives c₂ = 1."),
            ),
            equation="y'' - 2*y' + y = 0", conditions="y(0) = 1, y'(0) = 2",
            answer="(1 + t)*exp(t)", answer_latex=r"y(t) = (1 + t)\, e^{t}",
        ),
        Para(
            "The same computation explains the Cauchy–Euler repeated root, "
            "where the second solution is t^r ln t: with y₁ = t^r the quantity "
            "v' comes out as 1/t, and its integral is ln t. In both cases the "
            "'extra factor' that looks like a trick is just the integral of "
            "the simplest possible v'."
        ),
    )),
    Section("Equations with no constant-coefficient shortcut", (
        Worked(
            "A Cauchy–Euler equation, reduced",
            "y₁ = t solves t²y'' + ty' − y = 0. Find a second solution for "
            "t > 0.",
            (
                Step("p = 1/t, so e^(−∫p) = 1/t, and v' = (1/t)/t² = 1/t³.",
                     r"v' = t^{-3} \;\Longrightarrow\; v = -\frac{1}{2t^{2}}"),
                Step("y₂ = t·(−1/(2t²)) = −1/(2t); dropping the constant "
                     "factor, y₂ = 1/t. Check: t²(2/t³) + t(−1/t²) − 1/t = "
                     "2/t − 1/t − 1/t = 0."),
            ),
            equation="t**2*y'' + t*y' - y = 0",
            answer="1/t", answer_latex=r"y_2 = \frac{1}{t}",
        ),
        Para(
            "Legendre's equation (1 − t²)y'' − 2ty' + n(n + 1)y = 0 is the "
            "classic example with no elementary shortcut. For n = 1 the "
            "polynomial y₁ = t is a solution, as substitution shows: "
            "0 − 2t + 2t = 0. Reduction of order produces the second, which "
            "is not a polynomial and blows up at t = ±1, the points where the "
            "leading coefficient 1 − t² vanishes."
        ),
        Worked(
            "Legendre's equation with n = 1",
            "Find a second solution of (1 − t²)y'' − 2ty' + 2y = 0 on (−1, 1), "
            "given y₁ = t.",
            (
                Step("p = −2t/(1 − t²), so ∫p dt = ln(1 − t²) and "
                     "e^(−∫p) = 1/(1 − t²). Then v' = 1/(t²(1 − t²)), which "
                     "splits into partial fractions.",
                     r"\frac{1}{t^{2}(1 - t^{2})} = \frac{1}{t^{2}} + "
                     r"\frac{1}{2}\left(\frac{1}{1 - t} + \frac{1}{1 + t}\right)"),
                Step("Integrating, v = −1/t + (1/2)ln((1 + t)/(1 − t)), and "
                     "y₂ = tv.",
                     r"y_2 = \frac{t}{2}\ln\frac{1 + t}{1 - t} - 1"),
            ),
            equation="(1 - t**2)*y'' - 2*t*y' + 2*y = 0",
            answer="t*log((1 + t)/(1 - t))/2 - 1",
            answer_latex=r"y_2 = \frac{t}{2}\ln\frac{1 + t}{1 - t} - 1",
        ),
        Plot(
            "The two Legendre solutions for n = 1",
            "y₁ = t, a polynomial, and y₂ = (t/2)ln((1 + t)/(1 − t)) − 1, which "
            "is even, equals −1 at the origin and grows without bound as t "
            "approaches ±1. In physics only the bounded solution is usually "
            "wanted, which is how the Legendre polynomials are selected.",
            (Curve("t", "y₁ = t"),
             Curve("t*log((1 + t)/(1 - t))/2 - 1", "y₂")),
            t=(-0.98, 0.98), ylim=(-1.5, 2.0),
        ),
    )),
    Section("Finding the first solution", (
        Para(
            "Everything above assumes y₁ is known, and that is the real "
            "restriction of the method. A textbook problem usually supplies "
            "it. When it does not, the practical approach is to try the "
            "obvious candidates: a power t^r (especially when the coefficients "
            "are powers of t, as in Cauchy–Euler equations), an exponential "
            "e^(rt) (when some combination of coefficients is constant), a "
            "low-degree polynomial, or e^(t²)-type functions when the "
            "coefficients grow linearly."
        ),
        Para(
            "For e^(rt) there is a quick test: substituting it into "
            "a(t)y'' + b(t)y' + c(t)y gives (a r² + b r + c)e^(rt), so e^(rt) is a "
            "solution exactly when a(t)r² + b(t)r + c(t) = 0 for every t. For "
            "t·y'' − (t + 1)y' + y = 0 that is tr² − (t + 1)r + 1 = "
            "t(r² − r) − (r − 1), zero for all t only when r = 1. Similar "
            "bookkeeping works for t^r. The narrator in this application does "
            "exactly this search — powers, exponentials, low-degree "
            "polynomials — and keeps the first candidate that substitutes to "
            "zero, checking rather than assuming."
        ),
        Box(
            "remark", "If no first solution can be found",
            "Then reduction of order cannot start, and the next resources are "
            "power series (Unit 7), which produce solutions near ordinary and "
            "regular singular points, and numerical methods, which always "
            "work. A second-order linear equation with variable coefficients "
            "is, in general, not solvable in closed form.",
        ),
    )),
    Section("A shortcut through the Wronskian", (
        Para(
            "There is a second way to reach the formula, and it shows why the "
            "method has to work. Abel's formula from the superposition lesson "
            "says that the Wronskian of *any* two solutions is a constant "
            "times e^(−∫p dt), and that constant can be chosen as 1. So if y₁ "
            "is known, a second solution y₂ must satisfy "
            "y₁y₂' − y₁'y₂ = e^(−∫p dt), which is a first-order linear "
            "equation for y₂ — the Wronskian is known before y₂ is."
        ),
        Para(
            "Divide that equation by y₁²: the left side becomes the derivative "
            "of the quotient y₂/y₁, by the quotient rule. So (y₂/y₁)' = "
            "e^(−∫p dt)/y₁², and integrating gives exactly the formula of the "
            "theorem. The two derivations are the same calculation seen "
            "from two angles: the substitution y = vy₁ finds v' directly, and "
            "the Wronskian identifies v' as W/y₁² before any substitution is "
            "made."
        ),
        Display(r"\left(\frac{y_2}{y_1}\right)' = \frac{W}{y_1^{2}} = "
                r"\frac{e^{-\int p\, dt}}{y_1^{2}}"),
        Para(
            "This view also explains why the constants of integration may be "
            "dropped. Changing the Wronskian's constant rescales y₂; adding a "
            "constant to the quotient y₂/y₁ adds a multiple of y₁ to y₂. "
            "Neither changes the pair's usefulness as a fundamental set, "
            "because the general solution c₁y₁ + c₂y₂ absorbs both."
        ),
    )),
    Section("Common errors", (
        Para(
            "The standard-form error has been warned about twice already, "
            "because it is by far the commonest: p must be read after dividing "
            "by the coefficient of y''. The second is to forget the square in "
            "y₁². The formula divides by y₁², not y₁, and the square is what "
            "makes the Wronskian come out as e^(−∫p); dividing by y₁ alone "
            "gives a function that, multiplied by y₁, does not solve the "
            "equation."
        ),
        Para(
            "The third is sloppiness with ln|t| and absolute values. On an "
            "interval where t > 0, e^(−∫p dt) with p = −1/t is t, not |t|, and "
            "the method should be carried out on one interval at a time — the "
            "interval where the coefficients are continuous and y₁ is not "
            "zero. Where y₁ vanishes the division by y₁² fails, and the "
            "second solution found on one side of the zero may need a "
            "different constant on the other. A final substitution of y₂ into "
            "the original equation settles all of these at once."
        ),
    )),
    Section("A little history", (
        Para(
            "The method is usually credited to Jean le Rond d'Alembert, who "
            "used it in the eighteenth century for equations with constant "
            "coefficients — "
            "exactly the repeated-root derivation above. It was one of the "
            "first systematic tricks in the subject, and the idea behind it, "
            "writing the unknown as a known function times a new unknown, "
            "runs through everything that followed: variation of parameters "
            "is Lagrange's generalisation of it, and the substitution "
            "y = ue^(kt) used in the undetermined-coefficients lesson is the "
            "same move again. When an equation is almost solved, factor out "
            "the part you know and see what equation the rest satisfies."
        ),
    )),
    Section("Reduction of order for forced equations", (
        Para(
            "The substitution y = vy₁ works for the nonhomogeneous equation "
            "y'' + py' + qy = f too. The term multiplying v still vanishes, so "
            "the equation becomes y₁w' + (2y₁' + py₁)w = f for w = v' — now a "
            "first-order linear equation with a forcing term, which the "
            "integrating factor solves. Its solution contains a constant of "
            "integration that produces the second homogeneous solution, and "
            "a particular part that produces a particular solution of the "
            "forced equation."
        ),
        Para(
            "A small example shows both appearing. For y'' − y = 1 with "
            "y₁ = e^t, the reduced equation is e^t w' + 2e^t w = 1, that is "
            "w' + 2w = e^(−t). Its solution is w = e^(−t) + Ce^(−2t), so "
            "v = −e^(−t) − (C/2)e^(−2t) + D and y = ve^t = −1 − (C/2)e^(−t) + De^t. "
            "The constant −1 is a particular solution (substitute it: "
            "0 − (−1) = 1), and the arbitrary multiples of e^(−t) and e^t are "
            "the complete homogeneous solution — all from one known solution "
            "and two first-order integrations."
        ),
        Para(
            "So with a single known homogeneous solution, reduction of order "
            "solves the forced equation completely — both the missing "
            "homogeneous solution and a particular solution come out of the "
            "same first-order equation. Variation of parameters needs both "
            "homogeneous solutions first; reduction of order needs only one. "
            "They are two routes through the same idea."
        ),
    )),
    Section("Reading the second solution", (
        Para(
            "The second solution produced by reduction of order is often "
            "qualitatively different from the first, and the difference "
            "carries information. Legendre's y₂ blows up at t = ±1 while y₁ = t "
            "does not; the Cauchy–Euler y₂ = 1/t blows up at 0 while y₁ = t "
            "does not. In each case the blow-up happens at a point where the "
            "leading coefficient of the equation vanishes — a *singular point* "
            "— and it is the second solution that feels the singularity."
        ),
        Para(
            "That pattern is general and important. Near a singular point, "
            "usually one solution is well behaved and the other is not, and "
            "a physical problem that requires the solution to stay finite "
            "there selects the well-behaved one. The temperature in a disc "
            "must be finite at the centre; the displacement of a drumhead "
            "must be finite at its middle. Unit 7's series methods are built "
            "to find the solutions near such points, and reduction of order "
            "is the tool that recovers the other one once the first is known."
        ),
    )),
    Section("Choosing among the methods of this unit", (
        Para(
            "Unit 3 now has four ways of producing solutions of a linear "
            "second-order equation, and it helps to know which to reach for. "
            "Constant coefficients and no forcing: characteristic roots, "
            "always. Constant coefficients with polynomial, exponential or "
            "sinusoidal forcing: characteristic roots for the complementary "
            "function and undetermined coefficients for the particular "
            "solution. Constant coefficients with any other forcing: "
            "variation of parameters for the particular solution."
        ),
        Para(
            "Variable coefficients: if the equation is Cauchy–Euler, the next "
            "lesson's trial y = t^r gives both solutions; otherwise, look for "
            "one solution by inspection or trial and use reduction of order "
            "for the second, then variation of parameters (or reduction of "
            "order again) for any forcing. And if no first solution can be "
            "found, move on to series or to numerical methods. Every one of "
            "these paths ends in the same place: a fundamental set, a "
            "particular solution, and constants fitted to the conditions."
        ),
    )),
    Section("Summary", (
        Para(
            "Given one nonzero solution y₁ of y'' + py' + qy = 0, set y = vy₁. "
            "The terms in v cancel because y₁ is a solution, leaving a "
            "first-order equation for w = v' whose solution is "
            "w = e^(−∫p dt)/y₁². Integrate once more for v, and y₂ = vy₁ is a "
            "second solution, independent of the first because their "
            "Wronskian is y₁²w = e^(−∫p dt). Divide by the leading coefficient "
            "before reading off p. The method derives the te^(rt) of the "
            "repeated root, produces non-elementary second solutions such as "
            "Legendre's, and, applied to a forced equation, gives the rest of "
            "the solution from one homogeneous solution. Its only real demand "
            "is that first solution, which is why the search for one — by "
            "inspection, by trial, or by series — is where the work usually "
            "lies."
        ),
    )),
)


VARIATION = (
    Section("When there is nothing to guess", (
        Para(
            "Undetermined coefficients is fast, but it rests on a lucky "
            "property of the forcing: that its derivatives stay inside a "
            "finite family. For y'' + y = sec t they do not, and no trial "
            "function can be written down. The equation still has solutions — "
            "the existence theorem guarantees them on (−π/2, π/2), where sec t "
            "is continuous — and a method that finds a particular solution "
            "for *any* continuous forcing would close the gap completely. "
            "Variation of parameters is that method."
        ),
        Para(
            "The idea was met in Unit 1, where the integrating-factor formula "
            "was derived a second way by taking the homogeneous solution "
            "Ch(t) and letting the constant C vary. Here the homogeneous "
            "solution is c₁y₁ + c₂y₂, with two constants, and the idea is the "
            "same: look for a particular solution of the form u₁(t)y₁ + "
            "u₂(t)y₂, replacing the constants by unknown functions."
        ),
        Display(r"y_p = u_1(t)\, y_1(t) + u_2(t)\, y_2(t)", "1"),
        Para(
            "Forcing terms of that awkward kind are not exotic. A driving "
            "force that switches on smoothly but sharply, a voltage that "
            "falls off like 1/t, a load that grows like ln t — each is "
            "outside the closed families, and each is the kind of input a "
            "real model meets. A method restricted to polynomials, "
            "exponentials and sinusoids would leave them all unsolved."
        ),
    )),
    Section("Deriving the formula", (
        Para(
            "Differentiating (1) gives y_p' = u₁y₁' + u₂y₂' + u₁'y₁ + u₂'y₂. "
            "Two unknown functions u₁ and u₂ but only one equation to satisfy "
            "means there is room for one extra condition of our choosing, and "
            "the convenient one is to make the terms involving u' vanish."
        ),
        Display(r"u_1' y_1 + u_2' y_2 = 0", "2"),
        Para(
            "With (2), y_p' = u₁y₁' + u₂y₂', and differentiating again, "
            "y_p'' = u₁y₁'' + u₂y₂'' + u₁'y₁' + u₂'y₂'. Substitute into "
            "y'' + py' + qy = f. The terms containing u₁ collect into "
            "u₁(y₁'' + py₁' + qy₁), which is zero because y₁ is a homogeneous "
            "solution, and the same happens for u₂. All that survives is the "
            "second condition."
        ),
        Display(r"u_1' y_1' + u_2' y_2' = f(t)", "3"),
        Para(
            "Equations (2) and (3) are a linear system for u₁' and u₂', and "
            "its determinant is y₁y₂' − y₁'y₂, the Wronskian — nonzero because "
            "y₁ and y₂ are independent. Cramer's rule solves it, and "
            "integration gives u₁ and u₂."
        ),
        Box(
            "theorem", "Variation of parameters",
            "If y₁, y₂ are independent solutions of y'' + py' + qy = 0 and f is "
            "continuous, a particular solution of y'' + py' + qy = f is "
            "y_p = u₁y₁ + u₂y₂ with the u's below, W being the Wronskian.",
            r"u_1 = -\int \frac{y_2 f}{W}\, dt, \qquad "
            r"u_2 = \int \frac{y_1 f}{W}\, dt",
        ),
        Box(
            "warning", "f is the right side of the standard form",
            "The formula assumes the coefficient of y'' is 1. For "
            "t²y'' + … = g(t), divide first and use f = g/t². Forgetting to "
            "divide gives a y_p that is off by exactly that factor — it "
            "solves a different equation.",
        ),
        Figure("variation",
               "Left: sec t against the shapes a trial solution would have to "
               "be built from, running away from all of them. Right: the "
               "answer variation of parameters produces, with the homogeneous "
               "part on sliders."),
    )),
    Section("Why the extra condition is allowed", (
        Para(
            "Condition (2), u₁'y₁ + u₂'y₂ = 0, can look like a trick pulled "
            "from nowhere, and it is worth seeing why it is legitimate and why "
            "it is clever. It is legitimate because the method asks for *one* "
            "particular solution, and the form u₁y₁ + u₂y₂ has two unknown "
            "functions — twice as much freedom as needed. Any solution of the "
            "equation found in that form is good enough, so we are free to "
            "impose one further condition of our choosing and look for "
            "solutions that also satisfy it."
        ),
        Para(
            "It is clever because of what it does to the derivatives. Without "
            "it, y_p'' would contain u₁'' and u₂'', and substituting would give "
            "a second-order equation for the u's — no simpler than the "
            "original. With it, y_p' has the same form as the derivative of a "
            "combination with *constant* coefficients, second derivatives of "
            "the u's never appear, and the equation for them is first order "
            "and, in fact, just algebra for u₁' and u₂'. The condition is "
            "chosen to make y_p behave, for one derivative, exactly as if the "
            "parameters were not varying at all."
        ),
    )),
    Section("Worked examples", (
        Worked(
            "The canonical example",
            "Solve y'' + y = sec t with y(0) = 0, y'(0) = 0, on (−π/2, π/2).",
            (
                Step("y₁ = cos t, y₂ = sin t, W = cos²t + sin²t = 1. The "
                     "formula gives u₁' = −sin t · sec t = −tan t and "
                     "u₂' = cos t · sec t = 1.",
                     r"u_1' = -\tan t, \qquad u_2' = 1"),
                Step("Integrate: u₁ = ln|cos t| and u₂ = t. So "
                     "y_p = cos t ln(cos t) + t sin t, since cos t > 0 on the "
                     "interval.",
                     r"y_p = \cos t\, \ln(\cos t) + t\sin t"),
                Step("y_p(0) = 0 and y_p'(0) = 0 already, so the "
                     "complementary constants are both zero."),
            ),
            equation="y'' + y = sec(t)", conditions="y(0) = 0, y'(0) = 0",
            answer="cos(t)*log(cos(t)) + t*sin(t)",
            answer_latex=r"y(t) = \cos t\,\ln(\cos t) + t\sin t",
        ),
        Plot(
            "The response to sec t",
            "y = cos t ln(cos t) + t sin t on (−π/2, π/2), beside the forcing "
            "sec t. The forcing blows up at ±π/2 and the solution does not: "
            "near the ends cos t ln(cos t) → 0 and y → π/2. The solution "
            "exists exactly on the interval where the forcing is continuous, "
            "as the existence theorem promised.",
            (Curve("cos(t)*log(cos(t)) + t*sin(t)", "solution"),
             Curve("1/cos(t)", "forcing sec t")),
            t=(-1.5, 1.5), ylim=(-0.5, 6.0),
        ),
        Worked(
            "A tangent forcing",
            "Find a particular solution of y'' + y = tan t on (−π/2, π/2).",
            (
                Step("Again W = 1. u₁' = −sin t tan t = −sin²t/cos t = "
                     "cos t − sec t, and u₂' = cos t tan t = sin t.",
                     r"u_1' = \cos t - \sec t, \qquad u_2' = \sin t"),
                Step("Integrate: u₁ = sin t − ln(sec t + tan t) and "
                     "u₂ = −cos t. Then y_p = u₁cos t + u₂sin t, and the "
                     "sin t cos t terms cancel.",
                     r"y_p = -\cos t\, \ln(\sec t + \tan t)"),
            ),
            equation="y'' + y = tan(t)",
            answer="-cos(t)*log(1/cos(t) + tan(t))",
            answer_latex=r"y_p = -\cos t\,\ln(\sec t + \tan t)",
        ),
        Plot(
            "A particular solution for tan t forcing",
            "y_p = −cos t ln(sec t + tan t) on (−π/2, π/2), with the forcing "
            "tan t. The particular solution is odd, like the forcing, and "
            "stays bounded even though tan t does not: near ±π/2 the factor "
            "cos t goes to zero faster than the logarithm grows.",
            (Curve("-cos(t)*log(1/cos(t) + tan(t))", "y_p"),
             Curve("tan(t)", "forcing tan t")),
            t=(-1.5, 1.5), ylim=(-4.0, 4.0),
        ),
        Worked(
            "A repeated root and a 1/t forcing",
            "Find a particular solution of y'' − 2y' + y = e^t/t for t > 0.",
            (
                Step("The root 1 is double: y₁ = e^t, y₂ = te^t, and "
                     "W = e^t(e^t + te^t) − e^t · te^t = e^(2t).",
                     r"W(e^{t}, te^{t}) = e^{2t}"),
                Step("u₁' = −te^t(e^t/t)/e^(2t) = −1 and u₂' = e^t(e^t/t)/e^(2t) "
                     "= 1/t. So u₁ = −t and u₂ = ln t.",
                     r"u_1 = -t, \qquad u_2 = \ln t"),
                Step("y_p = −te^t + te^t ln t. The first term is a homogeneous "
                     "solution and could be dropped; keeping it does no harm."),
            ),
            equation="y'' - 2*y' + y = exp(t)/t",
            answer="-t*exp(t) + t*exp(t)*log(t)",
            answer_latex=r"y_p = t e^{t}\ln t - t e^{t}",
        ),
    )),
    Section("Agreement with undetermined coefficients", (
        Para(
            "Variation of parameters works for every continuous forcing, "
            "including the ones undetermined coefficients handles, and "
            "comparing the two on the same equation is a good check that the "
            "formula has been remembered correctly. The answers need not be "
            "identical — two particular solutions may differ by a homogeneous "
            "solution — but their difference must solve the homogeneous "
            "equation."
        ),
        Worked(
            "The same particular solution, the long way",
            "Use variation of parameters on y'' − y = e^(2t), and compare with "
            "undetermined coefficients, which gave e^(2t)/3.",
            (
                Step("y₁ = e^t, y₂ = e^(−t), W = −2. Then u₁' = −e^(−t)e^(2t)/(−2) "
                     "= e^t/2 and u₂' = e^t e^(2t)/(−2) = −e^(3t)/2.",
                     r"u_1 = \frac{e^{t}}{2}, \qquad u_2 = -\frac{e^{3t}}{6}"),
                Step("y_p = (e^t/2)e^t − (e^(3t)/6)e^(−t) = e^(2t)/2 − e^(2t)/6 = "
                     "e^(2t)/3, exactly the undetermined-coefficients answer — "
                     "found by two integrations instead of one line of algebra."),
            ),
            equation="y'' - y = exp(2*t)",
            answer="exp(2*t)/3", answer_latex=r"y_p = \frac{e^{2t}}{3}",
        ),
        Para(
            "That comparison is also the practical advice. When undetermined "
            "coefficients applies, use it: it is algebra, and algebra is "
            "quicker and less error-prone than integration. Reach for "
            "variation of parameters when the forcing has no finite trial "
            "family, or when the coefficients are not constant, where "
            "undetermined coefficients is not available at all."
        ),
    )),
    Section("Variable coefficients", (
        Para(
            "Nothing in the derivation used constant coefficients. As long as "
            "two independent homogeneous solutions are known — from the "
            "Cauchy–Euler method, from reduction of order, from a table, from "
            "a series — the formula gives a particular solution. This is the "
            "one general method for nonhomogeneous linear equations, and it "
            "reduces the forced problem completely to the homogeneous one."
        ),
        Para(
            "Take t²y'' − 2ty' + 2y = t³ for t > 0, whose homogeneous "
            "solutions t and t² were found in the superposition lesson. "
            "Standard form has f = t³/t² = t. With W = t², u₁' = −t² · t/t² = −t "
            "and u₂' = t · t/t² = 1, so u₁ = −t²/2 and u₂ = t, and "
            "y_p = −t³/2 + t³ = t³/2. Substituting confirms it: "
            "t² · 3t − 2t · (3t²/2) + 2 · t³/2 = 3t³ − 3t³ + t³ = t³."
        ),
        Display(r"t^{2} y'' - 2t y' + 2y = t^{3} \;\Longrightarrow\; "
                r"y_p = \frac{t^{3}}{2}"),
        Worked(
            "The full initial value problem",
            "Solve t²y'' − 2ty' + 2y = t³ with y(1) = 1, y'(1) = 0.",
            (
                Step("The general solution is y = c₁t + c₂t² + t³/2, so "
                     "y' = c₁ + 2c₂t + 3t²/2.",
                     r"y = c_1 t + c_2 t^{2} + \frac{t^{3}}{2}"),
                Step("At t = 1: c₁ + c₂ + 1/2 = 1 and c₁ + 2c₂ + 3/2 = 0. "
                     "Subtracting the first from the second, c₂ + 1 = −1/2, so "
                     "c₂ = −2 and then c₁ = 5/2.",
                     r"c_1 + c_2 = \frac{1}{2}, \qquad c_1 + 2c_2 = -\frac{3}{2}"),
                Step("The solution holds on (0, ∞), the interval where the "
                     "standard-form coefficients are continuous."),
            ),
            equation="t**2*y'' - 2*t*y' + 2*y = t**3", conditions="y(1) = 1, y'(1) = 0",
            answer="5*t/2 - 2*t**2 + t**3/2",
            answer_latex=r"y(t) = \frac{5t}{2} - 2t^{2} + \frac{t^{3}}{2}",
        ),
    )),
    Section("When the integrals cannot be done", (
        Para(
            "The formula always produces a particular solution, but only as "
            "integrals, and integrals do not always have elementary "
            "antiderivatives. For y'' − y = 1/t, for instance, u₂' = "
            "e^t/(2t), whose antiderivative is the exponential integral "
            "Ei(t), not an elementary function. That is not a failure of the "
            "method. The particular solution is still perfectly well defined — "
            "it can be written with a definite integral, evaluated "
            "numerically to any accuracy, and plotted."
        ),
        Para(
            "In practice this means the answer to a variation-of-parameters "
            "problem is sometimes left in the form y_p = −y₁∫y₂f/W dt + "
            "y₂∫y₁f/W dt with the integrals written out, or better, with the "
            "definite integrals of Section 9. The narrator in this "
            "application takes the honest line too: when the integrals for u "
            "have no closed form it says exactly that, rather than pretending "
            "to a formula."
        ),
    )),
    Section("Common errors", (
        Para(
            "Three mistakes account for most wrong answers with this method. "
            "The first is the one the warning above describes: using the "
            "forcing of an equation that is not in standard form. The second "
            "is a sign: u₁ carries the minus sign, u₂ does not, and swapping "
            "them — or computing the Wronskian as y₁'y₂ − y₁y₂' — flips the sign "
            "of y_p. A quick check is to substitute y_p and see whether f or −f "
            "comes back."
        ),
        Para(
            "The third is adding constants of integration to u₁ and u₂ and "
            "then forgetting them. They are harmless — they add c₁y₁ + c₂y₂, "
            "which the complementary function already contains — but carrying "
            "them through the algebra invites confusion when the initial "
            "conditions are applied. Drop them from the u's, add the "
            "complementary function once at the end, and fit its constants to "
            "the whole solution."
        ),
    )),
    Section("The formula as an integral", (
        Para(
            "Written with definite integrals from t₀, the particular solution "
            "is the one with zero initial values at t₀, and the two integrals "
            "combine into one. The result is a formula that expresses the "
            "response to any forcing as a weighted accumulation of the "
            "forcing's past values."
        ),
        Display(r"y_p(t) = \int_{t_0}^{t} G(t, s)\, f(s)\, ds, \qquad "
                r"G(t, s) = \frac{y_1(s) y_2(t) - y_1(t) y_2(s)}{W(s)}", "4"),
        Para(
            "The function G is the *Green's function* of the equation. For "
            "y'' + y it is sin(t − s): the response at time t to a unit kick "
            "at time s. So (4) says the response to a forcing spread over time "
            "is the sum of the responses to all the little kicks it is made "
            "of. That same idea is the convolution of the Laplace-transform "
            "unit, seen from the other side, and it is one of the most "
            "important ideas in the whole subject."
        ),
        Box(
            "remark", "Checking the Green's function for y'' + y",
            "With y₁ = cos, y₂ = sin and W = 1, G(t, s) = cos s sin t − cos t sin s "
            "= sin(t − s), by the subtraction formula. As a function of t it "
            "solves y'' + y = 0, is zero at t = s, and has slope 1 there — "
            "exactly the motion of a spring kicked from rest at time s.",
        ),
        Worked(
            "A constant force, through the Green's function",
            "Solve y'' + y = 1 with y(0) = 0, y'(0) = 0 using formula (4).",
            (
                Step("With G(t, s) = sin(t − s) and f = 1, the particular "
                     "solution with zero initial values is the integral of "
                     "sin(t − s) over s from 0 to t:",
                     r"y(t) = \int_{0}^{t} \sin(t - s)\, ds"),
                Step("Substituting w = t − s turns it into the integral of sin w "
                     "from 0 to t, which is 1 − cos t. No constants need "
                     "fitting: the definite integral starts at rest by "
                     "construction."),
            ),
            equation="y'' + y = 1", conditions="y(0) = 0, y'(0) = 0",
            answer="1 - cos(t)", answer_latex=r"y(t) = 1 - \cos t",
        ),
        Para(
            "Read the answer physically. A spring at rest is suddenly subject "
            "to a constant force equal to one unit of stiffness. Its new "
            "equilibrium is y = 1, and having started at 0 with no velocity it "
            "overshoots and oscillates about 1 between 0 and 2 for ever. The "
            "Green's function built that response by adding up the kicks "
            "delivered at every earlier moment, each one ringing on as a sine "
            "wave, and the sum of all those rings is the steady oscillation "
            "about the new rest position. The same computation with any other "
            "forcing is just a different weighting of the same rings."
        ),
    )),
    Section("The first-order case, seen again", (
        Para(
            "It is reassuring to run the method on the smallest possible "
            "case and watch it reproduce something already known. For the "
            "first-order equation y' + p(t)y = f(t) there is one homogeneous "
            "solution, h = e^(−∫p dt), and one parameter to vary. Writing "
            "y_p = u·h and substituting, the term u(h' + ph) vanishes because h "
            "is a homogeneous solution, leaving u'h = f."
        ),
        Display(r"u' = \frac{f}{h} = f\, e^{\int p\, dt} \;\Longrightarrow\; "
                r"y_p = e^{-\int p\, dt}\int f\, e^{\int p\, dt}\, dt"),
        Para(
            "That is precisely the integrating-factor formula of Unit 1, with "
            "e^(∫p dt) playing the part of μ. So variation of parameters is not "
            "a new idea introduced for second-order equations: it is the "
            "integrating factor, generalised. At first order there is one "
            "function to vary and no need for an extra condition; at second "
            "order there are two, one extra condition keeps the algebra "
            "first order, and the Wronskian appears as the determinant of the "
            "resulting two-by-two system. At order n there are n functions, "
            "n − 1 conditions and an n × n Wronskian, and the pattern is the "
            "same all the way up."
        ),
    )),
    Section("Higher order", (
        Para(
            "For an equation of order n the same argument gives n unknown "
            "functions and n − 1 extra conditions, one for each derivative "
            "below the highest, chosen to keep the u' terms out. The result is "
            "an n × n linear system for u₁', …, uₙ' whose matrix has the "
            "fundamental solutions and their derivatives as rows and whose "
            "determinant is the n × n Wronskian. It is solved by Cramer's rule "
            "or by elimination, and each uᵢ' is integrated. The narrator in "
            "this application does exactly that, for any order."
        ),
    )),
    Section("Summary", (
        Para(
            "To find a particular solution of y'' + py' + qy = f by variation "
            "of parameters: find two independent homogeneous solutions y₁, y₂ "
            "and their Wronskian W; make sure f is the right-hand side of the "
            "standard form; compute u₁ = −∫y₂f/W dt and u₂ = ∫y₁f/W dt, "
            "dropping constants of integration; and set y_p = u₁y₁ + u₂y₂. It "
            "works for any continuous forcing and any coefficients, costs two "
            "integrals, and agrees with undetermined coefficients wherever "
            "both apply. Written as an integral, it expresses the response to "
            "any forcing through the Green's function — the response to a "
            "single kick. And at first order it is nothing but the "
            "integrating factor, which is the best evidence that it is not a "
            "trick but the natural general method: whenever the homogeneous "
            "problem is solved, the forced one follows by integration."
        ),
    )),
)


UNDETERMINED = (
    Section("Guessing, done systematically", (
        Para(
            "The general solution of a forced equation ay'' + by' + cy = f(t) "
            "is the complementary function plus *one* particular solution y_p, "
            "and the last lesson found the complementary function from the "
            "characteristic roots. What remains is to find y_p. For a large "
            "and important class of forcing terms, it can be found by an "
            "educated guess: write down a function of the right *form* with "
            "unknown coefficients, substitute it, and solve for the "
            "coefficients. That is the method of undetermined coefficients."
        ),
        Para(
            "Why should a guess work? Because the left-hand side of the "
            "equation only ever differentiates y and multiplies by constants. "
            "If the forcing is a polynomial, an exponential, a sine or cosine, "
            "or a product of these, then differentiating a function of the "
            "same kind gives back a function of the same kind. The family is "
            "*closed* under differentiation, so a trial solution drawn from it "
            "turns the equation into an identity between members of the "
            "family, and matching coefficients gives ordinary linear algebra."
        ),
        Box(
            "definition", "Trial solution",
            "A function of the same form as the forcing term — the same kind "
            "of polynomial, exponential or sinusoid, with every coefficient "
            "left unknown — substituted into the equation to find a "
            "particular solution.",
        ),
        Para(
            "The family must be complete. A forcing term 4t is a polynomial of "
            "degree one, so the trial is At + B, including the constant term "
            "even though the forcing has none: differentiating At + B produces "
            "a constant, and the trial must have room for it. Likewise a "
            "forcing cos t needs the trial A cos t + B sin t, because "
            "differentiating a cosine produces a sine."
        ),
    )),
    Section("The trial forms", (
        Para(
            "For f(t) a polynomial of degree n, try a general polynomial of "
            "degree n. For f(t) = e^(kt), try Ae^(kt). For f(t) = cos ωt or "
            "sin ωt — or any combination — try A cos ωt + B sin ωt. For a "
            "product such as a polynomial times e^(kt), or e^(αt) times a "
            "cosine, try the product of the corresponding forms, with a full "
            "set of unknown coefficients."
        ),
        Display(r"f = P_n(t) \;\to\; y_p = A_n t^{n} + \cdots + A_0, \qquad "
                r"f = e^{kt} \;\to\; y_p = A e^{kt}"),
        Display(r"f = \cos\omega t \;\text{or}\; \sin\omega t \;\to\; "
                r"y_p = A\cos\omega t + B\sin\omega t"),
        Display(r"f = e^{\alpha t}\cos\beta t \;\to\; "
                r"y_p = e^{\alpha t}(A\cos\beta t + B\sin\beta t)"),
        Para(
            "One rule overrides the table, and it is the part of the method "
            "that needs thought rather than bookkeeping. If any term of the "
            "trial solution already solves the homogeneous equation, the "
            "trial must be multiplied by t — or by t² if that is still not "
            "enough. Section 5 explains why, and it is the source of "
            "resonance."
        ),
    )),
    Section("Worked examples", (
        Worked(
            "A polynomial forcing term",
            "Solve y'' + 3y' + 2y = 4t with y(0) = 0, y'(0) = 0.",
            (
                Step("Complementary function: r² + 3r + 2 = (r + 1)(r + 2), so "
                     "y_c = c₁e^(−t) + c₂e^(−2t). Neither root is zero, so no "
                     "polynomial is a homogeneous solution and the plain "
                     "trial is fine.",
                     r"y_p = At + B, \quad y_p' = A, \quad y_p'' = 0"),
                Step("Substitute: 0 + 3A + 2(At + B) = 4t. Match coefficients: "
                     "t-terms 2A = 4, constants 3A + 2B = 0. So A = 2, B = −3.",
                     r"y_p = 2t - 3"),
                Step("Fit the conditions to y = 2t − 3 + c₁e^(−t) + c₂e^(−2t): "
                     "c₁ + c₂ = 3 and 2 − c₁ − 2c₂ = 0, so c₂ = −1 and c₁ = 4."),
            ),
            equation="y'' + 3*y' + 2*y = 4*t", conditions="y(0) = 0, y'(0) = 0",
            answer="2*t - 3 + 4*exp(-t) - exp(-2*t)",
            answer_latex=r"y(t) = 2t - 3 + 4e^{-t} - e^{-2t}",
        ),
        Worked(
            "An exponential forcing term",
            "Solve y'' − y = e^(2t) with y(0) = 0, y'(0) = 0.",
            (
                Step("y_c = c₁e^t + c₂e^(−t). The forcing e^(2t) is not among "
                     "them, so try y_p = Ae^(2t): substituting gives "
                     "4Ae^(2t) − Ae^(2t) = e^(2t), so A = 1/3.",
                     r"y_p = \frac{1}{3} e^{2t}"),
                Step("The conditions on y = e^(2t)/3 + c₁e^t + c₂e^(−t) give "
                     "c₁ + c₂ = −1/3 and c₁ − c₂ = −2/3, so c₁ = −1/2 and "
                     "c₂ = 1/6."),
            ),
            equation="y'' - y = exp(2*t)", conditions="y(0) = 0, y'(0) = 0",
            answer="exp(2*t)/3 - exp(t)/2 + exp(-t)/6",
            answer_latex=r"y(t) = \frac{e^{2t}}{3} - \frac{e^{t}}{2} + "
                         r"\frac{e^{-t}}{6}",
        ),
        Para(
            "For exponential forcing there is a shortcut worth knowing. "
            "Substituting Ae^(kt) into ay'' + by' + cy gives A(ak² + bk + c)e^(kt) "
            "— the characteristic polynomial evaluated at k. So "
            "y_p = e^(kt)/p(k), where p is the characteristic polynomial, "
            "provided p(k) ≠ 0. In the example p(2) = 4 − 1 = 3. The proviso "
            "is exactly the exceptional case of Section 5."
        ),
        Worked(
            "A cosine forcing term",
            "Solve y'' + 4y = cos t with y(0) = 0, y'(0) = 0.",
            (
                Step("y_c = c₁cos 2t + c₂sin 2t, natural frequency 2. The "
                     "forcing has frequency 1, so try A cos t + B sin t: "
                     "substituting gives 3A cos t + 3B sin t = cos t, so "
                     "A = 1/3, B = 0.",
                     r"y_p = \frac{1}{3}\cos t"),
                Step("y(0) = 1/3 + c₁ = 0 gives c₁ = −1/3; y'(0) = 2c₂ = 0 "
                     "gives c₂ = 0."),
            ),
            equation="y'' + 4*y = cos(t)", conditions="y(0) = 0, y'(0) = 0",
            answer="(cos(t) - cos(2*t))/3",
            answer_latex=r"y(t) = \frac{\cos t - \cos 2t}{3}",
        ),
        Plot(
            "A forced oscillation that never settles",
            "y = (cos t − cos 2t)/3: the response at the forcing frequency, "
            "cos t/3, plus the natural oscillation −cos 2t/3 set going by the "
            "initial conditions. With no damping neither part decays, and "
            "their sum repeats with period 2π without ever becoming a pure "
            "cosine.",
            (Curve("(cos(t) - cos(2*t))/3", "solution"),
             Curve("cos(t)/3", "particular part")),
            t=(0.0, 18.0),
        ),
        Figure("forced_structure",
               "Separate the two halves of a forced solution: the particular "
               "part fixed by the forcing, and the homogeneous part whose "
               "constants the initial conditions set."),
    )),
    Section("When the guess is already a solution", (
        Para(
            "Try the method on y'' − y = e^t. The trial Ae^t gives "
            "Ae^t − Ae^t = 0 on the left, whatever A is — and the right side "
            "is e^t, not zero. No value of A works. The reason is that e^t "
            "solves the homogeneous equation, so the operator annihilates it, "
            "and a trial made only of homogeneous solutions can never produce "
            "a nonzero right side."
        ),
        Box(
            "theorem", "The modification rule",
            "If some term of the trial solution solves the homogeneous "
            "equation, multiply the entire trial by t^s, where s is the "
            "smallest power of t — 1 or 2 for a second-order equation — that "
            "leaves no term of the trial a homogeneous solution. Then the "
            "coefficients can be found.",
            r"y_p = t^{s} \times (\text{standard trial})",
        ),
        Para(
            "In the language of the last lesson, s is the multiplicity of the "
            "forcing's exponent as a characteristic root. The rule is the same "
            "phenomenon as the repeated-root case, where te^(rt) appeared "
            "because the second solution had to be different from the first; "
            "and it is the same as the integrating-factor example in Unit 1 "
            "where forcing that matched the natural behaviour produced a "
            "factor of t."
        ),
        Worked(
            "Forcing at a characteristic root",
            "Solve y'' − y = e^t with y(0) = 0, y'(0) = 0.",
            (
                Step("1 is a simple root of r² − 1, so s = 1: try y_p = Ate^t. "
                     "Then y_p' = A(1 + t)e^t and y_p'' = A(2 + t)e^t, and "
                     "y_p'' − y_p = 2Ae^t = e^t gives A = 1/2.",
                     r"y_p = \frac{1}{2} t e^{t}"),
                Step("With y = te^t/2 + c₁e^t + c₂e^(−t): c₁ + c₂ = 0 and "
                     "1/2 + c₁ − c₂ = 0, so c₁ = −1/4 and c₂ = 1/4."),
            ),
            equation="y'' - y = exp(t)", conditions="y(0) = 0, y'(0) = 0",
            answer="t*exp(t)/2 - exp(t)/4 + exp(-t)/4",
            answer_latex=r"y(t) = \frac{te^{t}}{2} - \frac{e^{t}}{4} + "
                         r"\frac{e^{-t}}{4}",
        ),
        Worked(
            "A double root needs t²",
            "Find a particular solution of y'' + 2y' + y = te^(−t), and the "
            "solution with y(0) = 0, y'(0) = 0.",
            (
                Step("The characteristic roots are −1, −1: a double root. The "
                     "standard trial (At + B)e^(−t) consists entirely of "
                     "homogeneous solutions, and so does t(At + B)e^(−t) in "
                     "part, so s = 2.",
                     r"y_p = t^{2}(At + B)\, e^{-t}"),
                Step("Writing y_p = u e^(−t), the operator becomes u'' for this "
                     "equation, so u'' = t and u = t³/6: A = 1/6, B = 0.",
                     r"y_p = \frac{t^{3}}{6} e^{-t}"),
                Step("This y_p already has y(0) = 0 and y'(0) = 0, so the "
                     "homogeneous constants are both zero."),
            ),
            equation="y'' + 2*y' + y = t*exp(-t)", conditions="y(0) = 0, y'(0) = 0",
            answer="t**3*exp(-t)/6", answer_latex=r"y(t) = \frac{t^{3}}{6} e^{-t}",
        ),
    )),
    Section("Resonance", (
        Para(
            "The modification rule has a dramatic physical meaning when the "
            "forcing is a sinusoid at the natural frequency of an undamped "
            "system. For y'' + 4y = cos 2t the natural oscillations are cos 2t "
            "and sin 2t, and the forcing is one of them. The trial must be "
            "multiplied by t, and the factor t means the response grows "
            "without bound."
        ),
        Worked(
            "Resonance",
            "Solve y'' + 4y = cos 2t with y(0) = 0, y'(0) = 0.",
            (
                Step("s = 1, so try y_p = t(A cos 2t + B sin 2t). Substituting, "
                     "all the terms with a factor t cancel (they are "
                     "homogeneous solutions), leaving −4A sin 2t + 4B cos 2t = "
                     "cos 2t: A = 0 and B = 1/4.",
                     r"y_p = \frac{t}{4}\sin 2t"),
                Step("This y_p is zero at t = 0 and so is its derivative, so "
                     "the homogeneous part is zero and y = y_p."),
            ),
            equation="y'' + 4*y = cos(2*t)", conditions="y(0) = 0, y'(0) = 0",
            answer="t*sin(2*t)/4", answer_latex=r"y(t) = \frac{t}{4}\sin 2t",
        ),
        Plot(
            "Resonance: an oscillation with a growing amplitude",
            "y = (t/4) sin 2t between its envelope ±t/4. Forcing at the "
            "natural frequency pumps energy in on every cycle, in step with "
            "the motion, and with no damping to remove it the amplitude grows "
            "linearly for ever. Compare the bounded response to cos t above.",
            (Curve("t*sin(2*t)/4", "solution"), Curve("t/4", "envelope ±t/4"),
             Curve("-t/4", "")),
            t=(0.0, 30.0),
        ),
        Box(
            "warning", "Real systems have damping",
            "Unbounded growth is a property of the undamped model. With any "
            "damping at all the characteristic roots have negative real part, "
            "the forcing frequency is never exactly a root, and the response "
            "stays bounded — but it can be very large when the damping is "
            "small, which is what breaks glasses and, occasionally, bridges. "
            "The vibrations unit measures how large.",
        ),
    )),
    Section("Sums and products of forcing terms", (
        Para(
            "Because the equation is linear, a forcing term that is a sum can "
            "be handled one piece at a time. If y₁ solves L[y] = f₁ and y₂ "
            "solves L[y] = f₂, then y₁ + y₂ solves L[y] = f₁ + f₂. So for "
            "y'' + y = t + e^t, find a particular solution for t (it is t "
            "itself) and one for e^t (it is e^t/2) and add them: "
            "y_p = t + e^t/2. Each piece gets its own trial and its own check "
            "for the modification rule."
        ),
        Para(
            "Products are handled by product trials. For f = te^(3t) try "
            "(At + B)e^(3t); for f = e^(−t)sin 2t try e^(−t)(A cos 2t + "
            "B sin 2t); for f = t cos t try (At + B)cos t + (Ct + D)sin t. The "
            "number of unknowns grows, but the algebra is always a linear "
            "system, and the modification rule still applies to the product "
            "as a whole: it is the exponent α + iβ of the forcing that is "
            "compared with the characteristic roots."
        ),
        Worked(
            "A sum of forcing terms",
            "Solve y'' + y = t + e^t with y(0) = 0, y'(0) = 0.",
            (
                Step("For the forcing t, try At + B: then At + B = t, so the "
                     "particular solution is t. For e^t, the shortcut gives "
                     "e^t/p(1) with p(r) = r² + 1, so e^t/2.",
                     r"y_p = t + \frac{e^{t}}{2}"),
                Step("With y = t + e^t/2 + c₁cos t + c₂sin t: y(0) = 1/2 + c₁ = 0 "
                     "gives c₁ = −1/2, and y'(0) = 1 + 1/2 + c₂ = 0 gives "
                     "c₂ = −3/2."),
            ),
            equation="y'' + y = t + exp(t)", conditions="y(0) = 0, y'(0) = 0",
            answer="t + exp(t)/2 - cos(t)/2 - 3*sin(t)/2",
            answer_latex=r"y(t) = t + \frac{e^{t}}{2} - \frac{\cos t}{2} - "
                         r"\frac{3\sin t}{2}",
        ),
        Worked(
            "A polynomial times an exponential",
            "Find a particular solution of y'' − y = te^(2t).",
            (
                Step("2 is not a characteristic root (they are ±1), so the "
                     "trial is (At + B)e^(2t). Writing y = ue^(2t) turns y'' − y "
                     "into (u'' + 4u' + 3u)e^(2t), which is a convenient way to "
                     "differentiate a product trial.",
                     r"u'' + 4u' + 3u = t, \qquad u = At + B"),
                Step("With u = At + B: 4A + 3At + 3B = t, so 3A = 1 and "
                     "4A + 3B = 0. Hence A = 1/3 and B = −4/9.",
                     r"y_p = \left(\frac{t}{3} - \frac{4}{9}\right) e^{2t}"),
            ),
            equation="y'' - y = t*exp(2*t)",
            answer="(t/3 - 4/9)*exp(2*t)",
            answer_latex=r"y_p = \left(\frac{t}{3} - \frac{4}{9}\right) e^{2t}",
        ),
        Para(
            "The substitution y = ue^(kt) used there is worth remembering on "
            "its own. It turns a forcing of the form (polynomial)·e^(kt) into "
            "a pure polynomial forcing for u, with a new constant-coefficient "
            "operator whose coefficients come from shifting the "
            "characteristic polynomial by k. It also explains the modification "
            "rule: if k is a root, the shifted operator has no u term, and u "
            "must be a polynomial of higher degree than the forcing — the "
            "extra factor of t."
        ),
    )),
    Section("Why matching coefficients is legitimate", (
        Para(
            "Every example ended with a step like 'match the coefficients of "
            "t and of the constants', and it is worth knowing why that is "
            "allowed. An identity 2At + (3A + 2B) = 4t must hold for every t. "
            "Two polynomials that agree at every point have the same "
            "coefficients — their difference is a polynomial with infinitely "
            "many roots, which must be zero. So the t-coefficients agree and "
            "the constants agree, and there are exactly as many equations as "
            "unknowns."
        ),
        Para(
            "The same holds for cosines and sines, and for exponentials with "
            "different exponents: the functions 1, t, t², …, cos ωt, sin ωt, "
            "e^(kt) with distinct k are linearly independent, so an identity "
            "among combinations of them can only hold coefficient by "
            "coefficient. That is the independence of the last lesson doing "
            "quiet work. And it is exactly why the modification rule is "
            "needed: when a trial term is a homogeneous solution, it "
            "contributes nothing to the left side, the corresponding equation "
            "reads 0 = something, and the linear system has no solution."
        ),
        Box(
            "remark", "Checking a particular solution",
            "A particular solution can be checked on its own, before any "
            "initial condition is applied: substitute it and see whether the "
            "forcing comes back exactly. The drill in this lesson grades the "
            "final answer by substitution, and a wrong y_p shows up there as "
            "a leftover that is usually recognisable — the forcing term, or "
            "part of it, surviving the substitution.",
        ),
    )),
    Section("Choosing the trial: six quick cases", (
        Para(
            "Choosing the trial is the part of the method that exams test "
            "most, and it can be practised without solving anything. Take "
            "y'' + 4y (roots ±2i) with six different forcing terms. For "
            "f = 3t², try At² + Bt + C: a full quadratic. For f = 5e^(−t), try "
            "Ae^(−t). For f = sin 3t, try A cos 3t + B sin 3t, since 3 is not "
            "the natural frequency 2."
        ),
        Para(
            "For f = sin 2t, the standard trial A cos 2t + B sin 2t is made of "
            "homogeneous solutions, so multiply by t: t(A cos 2t + B sin 2t). "
            "For f = te^t, try (At + B)e^t. For f = e^t cos 2t, the exponent is "
            "1 ± 2i, not a root, so try e^t(A cos 2t + B sin 2t) — the factor "
            "e^t moves the exponent off the imaginary axis and the "
            "modification rule does not apply, even though cos 2t by itself "
            "would have triggered it."
        ),
        Para(
            "Now change the operator to y'' − 2y' + 5y, whose roots are "
            "1 ± 2i. The forcing sin 2t is now harmless and needs no factor "
            "of t, while e^t cos 2t has become resonant and needs "
            "te^t(A cos 2t + B sin 2t). The lesson of the six cases is that "
            "the trial depends on the forcing *and* on the characteristic "
            "roots together, and the only reliable way to decide is to "
            "compare the forcing's exponent with the roots every time."
        ),
    )),
    Section("Where the method stops", (
        Para(
            "Undetermined coefficients works only when the forcing belongs to "
            "a family closed under differentiation. For f(t) = sec t, the "
            "derivatives are sec t tan t, sec t tan² t + sec³ t, and so on — "
            "an endless list with no finite trial able to contain it. The same "
            "is true of ln t, 1/t, tan t and most other functions. The method "
            "also needs constant coefficients, since for variable "
            "coefficients the derivatives of the trial are multiplied by "
            "functions of t and leave the family."
        ),
        Para(
            "For everything outside its reach there is variation of "
            "parameters, the next lesson, which always works when the "
            "complementary function is known, at the price of two integrals "
            "that may be hard. The practical rule is: undetermined "
            "coefficients when it applies, because it is algebra rather than "
            "integration; variation of parameters otherwise."
        ),
    )),
    Section("Summary", (
        Para(
            "To find a particular solution of ay'' + by' + cy = f by "
            "undetermined coefficients: find the complementary function first; "
            "choose the trial of the same form as f, with every coefficient "
            "unknown and the full family included (a cosine needs a sine, a "
            "polynomial all lower powers); multiply by t or t² if any term of "
            "the trial solves the homogeneous equation; substitute and match "
            "coefficients; then add the complementary function and fit the "
            "initial conditions to the sum. For sums of forcing terms, add the "
            "particular solutions. Forcing at a natural frequency of an "
            "undamped system produces resonance, a response that grows "
            "without bound."
        ),
    )),
)


ROOTS = (
    Section("Trying an exponential", (
        Para(
            "The last lesson reduced solving y'' + py' + qy = 0 to finding two "
            "independent solutions. When p and q are constants there is a "
            "way to find them that never fails, and it rests on one "
            "observation: the derivative of e^(rt) is a constant multiple of "
            "e^(rt). Substitute y = e^(rt) into ay'' + by' + cy = 0 and every "
            "term carries the same factor e^(rt), which is never zero and can "
            "be cancelled. What is left is an equation for the number r "
            "alone."
        ),
        Display(r"a r^{2} e^{rt} + b r e^{rt} + c\, e^{rt} = 0 "
                r"\;\Longrightarrow\; a r^{2} + b r + c = 0", "1"),
        Box(
            "definition", "Characteristic equation",
            "For ay'' + by' + cy = 0 with constant coefficients, the "
            "*characteristic equation* is the quadratic ar² + br + c = 0, "
            "read straight off the coefficients. Its roots are the "
            "*characteristic roots*, and e^(rt) solves the differential "
            "equation exactly when r is one of them.",
            r"a r^{2} + b r + c = 0",
        ),
        Para(
            "So a differential equation has become an algebra problem, "
            "which is the whole point. A quadratic has two roots, and the "
            "three kinds of pair it can have — two distinct real numbers, one "
            "repeated real number, or a complex conjugate pair — give three "
            "forms of the general solution. The discriminant b² − 4ac decides "
            "which, and in the vibrations unit it will turn out to decide "
            "whether a spring oscillates."
        ),
        Figure("root_cases",
               "Move the coefficients and watch the roots move in the complex "
               "plane, and the solution change shape as they pass from two "
               "real roots through a double root to a complex pair."),
    )),
    Section("Distinct real roots", (
        Box(
            "theorem", "Distinct real roots",
            "If the characteristic equation has two different real roots r₁ "
            "and r₂, then e^(r₁t) and e^(r₂t) are independent solutions, and "
            "the general solution is their combination.",
            r"y = c_1 e^{r_1 t} + c_2 e^{r_2 t}",
        ),
        Para(
            "Independence follows from the Wronskian: W = (r₂ − r₁)e^((r₁+r₂)t), "
            "which is never zero when r₁ ≠ r₂. The long-run behaviour is read "
            "off the signs of the roots: if both are negative every solution "
            "decays to zero; if either is positive, almost every solution "
            "grows; the slower-decaying or faster-growing exponential "
            "eventually dominates."
        ),
        Worked(
            "Two decaying exponentials",
            "Solve y'' + 5y' + 6y = 0 with y(0) = 1, y'(0) = 0.",
            (
                Step("The characteristic equation r² + 5r + 6 = 0 factors as "
                     "(r + 2)(r + 3) = 0, so r = −2 and r = −3.",
                     r"y = c_1 e^{-2t} + c_2 e^{-3t}"),
                Step("The conditions give c₁ + c₂ = 1 and −2c₁ − 3c₂ = 0. From "
                     "the second c₁ = −3c₂/2, and then c₂ = −2, c₁ = 3.",
                     r"c_1 + c_2 = 1, \qquad -2c_1 - 3c_2 = 0"),
            ),
            equation="y'' + 5*y' + 6*y = 0", conditions="y(0) = 1, y'(0) = 0",
            answer="3*exp(-2*t) - 2*exp(-3*t)",
            answer_latex=r"y(t) = 3e^{-2t} - 2e^{-3t}",
        ),
        Worked(
            "One growing, one decaying",
            "Solve y'' − 4y = 0 with y(0) = 0, y'(0) = 4.",
            (
                Step("r² − 4 = 0 gives r = ±2, so y = c₁e^(2t) + c₂e^(−2t)."),
                Step("c₁ + c₂ = 0 and 2c₁ − 2c₂ = 4 give c₁ = 1, c₂ = −1 — "
                     "that is, 2 sinh 2t.",
                     r"y = e^{2t} - e^{-2t} = 2\sinh 2t"),
            ),
            equation="y'' - 4*y = 0", conditions="y(0) = 0, y'(0) = 4",
            answer="exp(2*t) - exp(-2*t)", answer_latex=r"y(t) = e^{2t} - e^{-2t}",
        ),
        Para(
            "The two examples show the two physical faces of real roots. In "
            "the first, both roots are negative: the system returns to rest "
            "without oscillating, the faster exponential dying first and the "
            "slower one, e^(−2t), setting the pace of the final approach. A "
            "heavily damped door-closer behaves this way. In the second, a "
            "positive root makes the zero solution unstable: a small push "
            "grows exponentially, as for a pencil balanced on its tip, whose "
            "linearised equation is exactly θ'' − (g/L)θ = 0. Both are "
            "predictable from the signs of the roots before any constant is "
            "fitted, and on an exam that sign reading is often worth doing "
            "first as a check on the final answer."
        ),
    )),
    Section("A repeated root", (
        Para(
            "When b² − 4ac = 0 the quadratic has only one root, r = −b/(2a), "
            "and the method produces only one exponential, e^(rt). A second, "
            "independent solution is still needed, and it cannot be another "
            "multiple of e^(rt). The surprise is that te^(rt) works."
        ),
        Box(
            "theorem", "Repeated root",
            "If r is a double root of the characteristic equation, then e^(rt) "
            "and te^(rt) are independent solutions, and the general solution "
            "is below.",
            r"y = (c_1 + c_2 t)\, e^{r t}",
        ),
        Box(
            "proof", "",
            "Write the characteristic polynomial as a(r − r₀)², so b = −2ar₀ "
            "and c = ar₀². For y = te^(r₀t), y' = (1 + r₀t)e^(r₀t) and "
            "y'' = (2r₀ + r₀²t)e^(r₀t). Substituting, the t-terms give "
            "a(r₀² − 2r₀² + r₀²)t = 0 and the rest give a(2r₀ − 2r₀) = 0. "
            "The Wronskian of e^(r₀t) and te^(r₀t) is e^(2r₀t), never zero.",
        ),
        Para(
            "Where does the t come from? One way to see it: when two roots r₁ "
            "and r₂ are close, (e^(r₂t) − e^(r₁t))/(r₂ − r₁) is a solution, and "
            "as r₂ → r₁ it becomes the derivative of e^(rt) with respect to r, "
            "which is te^(rt). The second solution of the repeated case is the "
            "limit of the two solutions of the distinct case as they merge. "
            "Reduction of order, later in this unit, derives it a third way."
        ),
        Worked(
            "A double root",
            "Solve y'' + 4y' + 4y = 0 with y(0) = 1, y'(0) = 1.",
            (
                Step("r² + 4r + 4 = (r + 2)² = 0, a double root r = −2.",
                     r"y = (c_1 + c_2 t)\, e^{-2t}"),
                Step("y(0) = c₁ = 1. y' = (c₂ − 2c₁ − 2c₂t)e^(−2t), so "
                     "y'(0) = c₂ − 2 = 1 and c₂ = 3."),
            ),
            equation="y'' + 4*y' + 4*y = 0", conditions="y(0) = 1, y'(0) = 1",
            answer="(1 + 3*t)*exp(-2*t)", answer_latex=r"y(t) = (1 + 3t)\, e^{-2t}",
        ),
        Box(
            "warning", "Two copies of one root are one solution",
            "Writing c₁e^(rt) + c₂e^(rt) for a double root is the commonest "
            "error in this unit. It is (c₁ + c₂)e^(rt), a single solution with "
            "a single effective constant, and it cannot satisfy two arbitrary "
            "initial conditions. The second solution needs the factor t.",
        ),
    )),
    Section("Complex roots", (
        Para(
            "When b² − 4ac < 0 the roots are complex: r = α ± iβ with "
            "α = −b/(2a) and β = √(4ac − b²)/(2a). The exponential e^(rt) is "
            "then complex-valued, and making sense of it needs Euler's "
            "formula, which says that the exponential of an imaginary number "
            "is a point on the unit circle."
        ),
        Display(r"e^{i\theta} = \cos\theta + i \sin\theta", "2"),
        Para(
            "With it, e^((α + iβ)t) = e^(αt)(cos βt + i sin βt). A complex "
            "solution of an equation with real coefficients has real and "
            "imaginary parts that are each real solutions — take the real "
            "and imaginary parts of L[y] = 0 separately. So the conjugate "
            "pair of roots yields two real solutions, e^(αt)cos βt and "
            "e^(αt)sin βt, and they are independent."
        ),
        Box(
            "theorem", "Complex roots",
            "If the characteristic roots are α ± iβ with β ≠ 0, the general "
            "real solution is an oscillation of angular frequency β inside an "
            "envelope e^(αt).",
            r"y = e^{\alpha t}\left(c_1 \cos\beta t + c_2 \sin\beta t\right)",
        ),
        Worked(
            "A decaying oscillation",
            "Solve y'' + 2y' + 5y = 0 with y(0) = 1, y'(0) = 1.",
            (
                Step("r² + 2r + 5 = 0 gives r = −1 ± 2i, so α = −1, β = 2.",
                     r"y = e^{-t}\left(c_1 \cos 2t + c_2 \sin 2t\right)"),
                Step("y(0) = c₁ = 1. Differentiating, y'(0) = −c₁ + 2c₂ = 1, "
                     "so c₂ = 1."),
            ),
            equation="y'' + 2*y' + 5*y = 0", conditions="y(0) = 1, y'(0) = 1",
            answer="exp(-t)*(cos(2*t) + sin(2*t))",
            answer_latex=r"y(t) = e^{-t}(\cos 2t + \sin 2t)",
        ),
        Plot(
            "An oscillation inside its envelope",
            "y = e^(−t)(cos 2t + sin 2t) between the curves ±√2·e^(−t). The "
            "imaginary part of the roots, 2, sets the frequency; the real "
            "part, −1, sets how fast the envelope shrinks.",
            (Curve("exp(-t)*(cos(2*t) + sin(2*t))", "solution"),
             Curve("sqrt(2)*exp(-t)", "envelope"),
             Curve("-sqrt(2)*exp(-t)", "")),
            t=(0.0, 5.0),
        ),
        Worked(
            "Pure oscillation",
            "Solve y'' + 9y = 0 with y(0) = 0, y'(0) = 6.",
            (
                Step("r² + 9 = 0 gives r = ±3i: α = 0, β = 3. With no real "
                     "part there is no envelope, and the solution oscillates "
                     "for ever.",
                     r"y = c_1 \cos 3t + c_2 \sin 3t"),
                Step("y(0) = c₁ = 0 and y'(0) = 3c₂ = 6, so c₂ = 2."),
            ),
            equation="y'' + 9*y = 0", conditions="y(0) = 0, y'(0) = 6",
            answer="2*sin(3*t)", answer_latex=r"y(t) = 2\sin 3t",
        ),
    )),
    Section("A reminder about complex numbers", (
        Para(
            "Complex roots are unavoidable here, so it is worth being "
            "comfortable with the few facts about complex numbers the course "
            "uses. A complex number is α + iβ with i² = −1; α is its real part "
            "and β its imaginary part. Complex numbers add and multiply like "
            "polynomials in i, with i² replaced by −1 wherever it appears. The "
            "*conjugate* of α + iβ is α − iβ, and the product of a number with "
            "its conjugate is the real number α² + β², the square of its "
            "*modulus*."
        ),
        Para(
            "Two facts do most of the work. First, a polynomial with real "
            "coefficients has complex roots in conjugate pairs: if α + iβ is a "
            "root, so is α − iβ, because conjugating the equation p(r) = 0 "
            "changes nothing but r. That is why complex roots of a "
            "characteristic equation always arrive two at a time, and why "
            "they produce two real solutions. Second, Euler's formula (2), "
            "which follows by comparing the Taylor series of e^(iθ), cos θ and "
            "sin θ term by term: the even powers of iθ are real and alternate "
            "in sign like cos θ, and the odd powers are imaginary and "
            "alternate like sin θ."
        ),
        Display(r"e^{(\alpha + i\beta)t} = e^{\alpha t}\left(\cos\beta t + "
                r"i \sin\beta t\right)"),
        Para(
            "The practical upshot is that in the final answer i never "
            "appears. Complex numbers are used on the way — to find the roots "
            "and to see why cosines and sines come out — and then the real "
            "solutions e^(αt)cos βt and e^(αt)sin βt are all that is written "
            "down."
        ),
    )),
    Section("A growing oscillation", (
        Para(
            "Complex roots with a positive real part give oscillations that "
            "grow. Physically this needs a source of energy — negative "
            "damping, like a child pumping a swing in time with its motion, or "
            "an electronic amplifier feeding its output back — and it is the "
            "start of the instability that the nonlinear unit will show being "
            "tamed into a limit cycle."
        ),
        Worked(
            "Roots with positive real part",
            "Solve y'' − 2y' + 5y = 0 with y(0) = 0, y'(0) = 2.",
            (
                Step("r² − 2r + 5 = 0 gives r = 1 ± 2i: α = 1, β = 2.",
                     r"y = e^{t}\left(c_1\cos 2t + c_2 \sin 2t\right)"),
                Step("y(0) = c₁ = 0. Then y = c₂e^t sin 2t, so y'(0) = 2c₂ = 2 "
                     "and c₂ = 1. The oscillation's amplitude grows by a factor "
                     "e every unit of time."),
            ),
            equation="y'' - 2*y' + 5*y = 0", conditions="y(0) = 0, y'(0) = 2",
            answer="exp(t)*sin(2*t)", answer_latex=r"y(t) = e^{t}\sin 2t",
        ),
        Plot(
            "Decaying, steady and growing oscillations",
            "e^(−t/2) sin 2t, sin 2t and e^(t/2) sin 2t: the same imaginary part "
            "2 of the roots, and real parts −1/2, 0 and +1/2. The real part "
            "alone decides whether the oscillation dies, persists or grows.",
            (Curve("exp(-t/2)*sin(2*t)", "α = −1/2"),
             Curve("sin(2*t)", "α = 0"),
             Curve("exp(t/2)*sin(2*t)", "α = +1/2")),
            t=(0.0, 6.0), ylim=(-6.0, 6.0),
        ),
    )),
    Section("The operator view, and where t·e^(rt) comes from", (
        Para(
            "There is a way of seeing the whole method that also explains "
            "the repeated root without guessing. Write D for differentiation, "
            "so Dy = y'. Then y'' − (r₁ + r₂)y' + r₁r₂y can be written "
            "(D − r₁)(D − r₂)y: applying D − r₂ first and then D − r₁ gives "
            "exactly those terms. A constant-coefficient operator factors "
            "exactly as its characteristic polynomial does."
        ),
        Display(r"a r^{2} + b r + c = a(r - r_1)(r - r_2) \;\Longrightarrow\; "
                r"L = a(D - r_1)(D - r_2)"),
        Para(
            "So L[y] = 0 can be solved as two first-order equations in turn. "
            "Put u = (D − r₂)y. Then (D − r₁)u = 0 says u' = r₁u, so "
            "u = Ae^(r₁t). What remains is the first-order linear equation "
            "y' − r₂y = Ae^(r₁t), which the integrating factor of Unit 1 "
            "solves. When r₁ ≠ r₂ it produces the two exponentials. When "
            "r₁ = r₂ = r, the forcing Ae^(rt) matches the natural behaviour, "
            "and — exactly as in the linear-equations lesson's example — the "
            "answer picks up a factor of t."
        ),
        Worked(
            "The second step of the factored equation",
            "For a double root r = 3, the second step is y' − 3y = e^(3t). "
            "Solve it with y(0) = 1.",
            (
                Step("Integrating factor e^(−3t): (e^(−3t)y)' = 1, so "
                     "e^(−3t)y = t + C and y = (t + C)e^(3t).",
                     r"y = (t + C)\, e^{3t}"),
                Step("y(0) = 1 gives C = 1. The factor t has appeared by itself, "
                     "which is where te^(rt) in the repeated-root theorem comes "
                     "from."),
            ),
            equation="y' - 3*y = exp(3*t)", conditions="y(0) = 1",
            answer="(t + 1)*exp(3*t)", answer_latex=r"y(t) = (t + 1)\, e^{3t}",
        ),
    )),
    Section("Amplitude and phase", (
        Para(
            "A combination c₁cos βt + c₂sin βt is a single cosine in disguise, "
            "and writing it that way shows the amplitude directly. Any such "
            "combination equals A cos(βt − φ) with A = √(c₁² + c₂²) and the "
            "angle φ chosen so that cos φ = c₁/A and sin φ = c₂/A."
        ),
        Display(r"c_1\cos\beta t + c_2\sin\beta t = A\cos(\beta t - \varphi), "
                r"\quad A = \sqrt{c_1^{2} + c_2^{2}}", "3"),
        Para(
            "For the decaying oscillation above, c₁ = c₂ = 1, so A = √2 and "
            "φ = π/4: y = √2 e^(−t) cos(2t − π/4), which is why the envelope in "
            "the graph was ±√2 e^(−t). The amplitude-phase form is the natural "
            "one in physics, where A is how far the spring stretches and φ "
            "says when in the cycle it started."
        ),
        Para(
            "Going the other way is just the addition formula for cosine: "
            "A cos(βt − φ) = A cos φ cos βt + A sin φ sin βt, so c₁ = A cos φ "
            "and c₂ = A sin φ. Either form is a correct general solution, and "
            "they carry the same two arbitrary constants, just packaged "
            "differently — (c₁, c₂) as Cartesian coordinates, (A, φ) as polar "
            "ones. Use whichever the question needs: fitting initial "
            "conditions is easier with c₁ and c₂, and questions about how far "
            "or when are easier with A and φ."
        ),
        Box(
            "warning", "The quadrant of the phase",
            "tan φ = c₂/c₁ has two solutions in [0, 2π). Choose the one that "
            "puts (cos φ, sin φ) in the same quadrant as (c₁, c₂). For "
            "c₁ = −1, c₂ = 1 the angle is 3π/4, not −π/4.",
        ),
    )),
    Section("The three cases together", (
        Para(
            "The discriminant sorts every constant-coefficient second-order "
            "equation into one of three shapes, and it is worth holding them "
            "side by side. Positive discriminant: two real exponentials, no "
            "oscillation. Zero: one exponential times a linear factor, the "
            "boundary case. Negative: an oscillation, growing, steady or "
            "decaying according to the sign of the real part."
        ),
        Display(r"b^{2} - 4ac > 0: \; c_1 e^{r_1 t} + c_2 e^{r_2 t}, \qquad "
                r"= 0: \; (c_1 + c_2 t)e^{rt}"),
        Display(r"b^{2} - 4ac < 0: \; e^{\alpha t}(c_1\cos\beta t + "
                r"c_2\sin\beta t)"),
        Plot(
            "The three cases, from the same start",
            "Solutions from y(0) = 1, y'(0) = 0 of y'' + by' + y = 0 for "
            "b = 3 (distinct roots, slow return), b = 2 (double root, the "
            "fastest return without overshoot) and b = 0.5 (complex roots, "
            "oscillation). This is the damping picture of the next unit, "
            "seen first as algebra.",
            (Curve("((3 + sqrt(5))/(2*sqrt(5)))*exp((-3 + sqrt(5))*t/2) + "
                   "((sqrt(5) - 3)/(2*sqrt(5)))*exp((-3 - sqrt(5))*t/2)",
                   "b = 3"),
             Curve("(1 + t)*exp(-t)", "b = 2"),
             Curve("exp(-t/4)*(cos(sqrt(15)*t/4) + sin(sqrt(15)*t/4)/sqrt(15))",
                   "b = 0.5")),
            t=(0.0, 12.0), ylim=(-0.6, 1.05),
        ),
        Para(
            "Stability can be read off the roots without solving anything: "
            "every solution decays to zero exactly when both roots have "
            "negative real part, which for a quadratic with a > 0 happens "
            "exactly when b > 0 and c > 0. That test — every coefficient "
            "positive — is the simplest case of the Routh–Hurwitz criterion "
            "that control engineers use for equations of any order."
        ),
    )),
    Section("Common errors", (
        Para(
            "Most mistakes with this method are small and predictable. "
            "Reading the characteristic equation off an equation that is not "
            "written with every term on one side: y'' = 4y has characteristic "
            "equation r² − 4 = 0, not r² + 4 = 0, and the difference is between "
            "exponentials and oscillations. Using the coefficient of y' "
            "instead of the coefficient of y as the constant term. Forgetting "
            "the factor t for a double root. Writing the complex case as "
            "c₁e^(αt)cos βt + c₂e^(βt)sin αt, with α and β crossed."
        ),
        Para(
            "And in the initial conditions: differentiating the general "
            "solution carelessly, particularly the product rule in the "
            "repeated and complex cases, where y' has two terms for each "
            "constant. The derivative of (c₁ + c₂t)e^(rt) is "
            "(c₂ + rc₁ + rc₂t)e^(rt), and dropping the c₂ gives a wrong "
            "second constant. Checking the final answer against both "
            "conditions takes a minute and catches every one of these."
        ),
    )),
    Section("Higher-order equations", (
        Para(
            "The method carries over to any order. Substituting e^(rt) into a "
            "constant-coefficient equation of order n gives a polynomial of "
            "degree n, with n roots counted with multiplicity. Each simple "
            "real root r gives e^(rt); a root of multiplicity k gives e^(rt), "
            "te^(rt), …, t^(k−1)e^(rt); each complex pair gives a cosine and a "
            "sine, multiplied by powers of t if the pair is repeated. "
            "Altogether that is exactly n independent solutions."
        ),
        Para(
            "For y''' − y' = 0 the characteristic equation r³ − r = "
            "r(r − 1)(r + 1) = 0 gives 1, e^t and e^(−t). For y⁗ + 2y'' + y = 0 "
            "it is (r² + 1)² = 0, a repeated pair ±i, and the solutions are "
            "cos t, sin t, t cos t and t sin t. The only hard part is finding "
            "the roots of a polynomial of high degree, which for degree five "
            "and above cannot be done by a formula in general — so in practice "
            "the roots are found numerically."
        ),
    )),
    Section("Summary", (
        Para(
            "For ay'' + by' + cy = 0, substitute e^(rt) to get the "
            "characteristic equation ar² + br + c = 0. Two distinct real roots "
            "give c₁e^(r₁t) + c₂e^(r₂t); a double root r gives (c₁ + c₂t)e^(rt); "
            "complex roots α ± iβ give e^(αt)(c₁cos βt + c₂sin βt), which can be "
            "rewritten as Ae^(αt)cos(βt − φ). Fit the constants with the "
            "initial conditions, and read the long-run behaviour from the "
            "roots: negative real parts mean decay, a nonzero imaginary part "
            "means oscillation. The same recipe, with multiplicities, handles "
            "equations of any order."
        ),
    )),
)


SUPERPOSITION = (
    Section("Second-order linear equations", (
        Para(
            "Most of the physics of vibration, and a great deal of "
            "engineering, is described by one family of equations: linear, "
            "second order. A mass on a spring, a pendulum swinging through "
            "small angles, the current in a circuit with a coil and a "
            "capacitor, the deflection of a loaded beam — each obeys an "
            "equation relating a quantity, its rate of change and its "
            "acceleration, linearly. This unit is about solving them, and "
            "this lesson is about the structure every solution has before "
            "any particular method is applied."
        ),
        Box(
            "definition", "Second-order linear equation",
            "An equation of the form below, where the coefficients p, q and "
            "the forcing f are functions of t alone. It is *homogeneous* if "
            "f = 0 and *nonhomogeneous* otherwise. Dividing by the "
            "coefficient of y'' puts any linear second-order equation in "
            "this standard form.",
            r"y'' + p(t)\, y' + q(t)\, y = f(t)",
        ),
        Para(
            "A mass m on a spring of stiffness k with damping c obeys "
            "my'' + cy' + ky = F(t), where F is an external force; dividing by "
            "m gives the standard form with constant coefficients. An "
            "equation like t²y'' + ty' + (t² − 1)y = 0, Bessel's equation, has "
            "coefficients that vary with t and is still linear. What is not "
            "allowed is anything nonlinear in y: y'' + sin y = 0, the exact "
            "pendulum, is not linear, and none of this lesson applies to it."
        ),
    )),
    Section("Linearity and superposition", (
        Para(
            "It helps to think of the left-hand side as a machine L that "
            "takes a function y and returns another function: L[y] = y'' + "
            "py' + qy. The machine is *linear*: it respects sums and constant "
            "multiples, because differentiation does. That one property is "
            "the source of everything in this unit."
        ),
        Display(r"L[c_1 y_1 + c_2 y_2] = c_1 L[y_1] + c_2 L[y_2]", "1"),
        Box(
            "theorem", "Superposition",
            "If y₁ and y₂ are solutions of the homogeneous equation "
            "L[y] = 0 on an interval, then so is every linear combination "
            "c₁y₁ + c₂y₂, for any constants c₁ and c₂.",
        ),
        Box(
            "proof", "",
            "By (1), L[c₁y₁ + c₂y₂] = c₁L[y₁] + c₂L[y₂] = c₁·0 + c₂·0 = 0. The "
            "linearity of L is itself just the linearity of differentiation: "
            "(c₁y₁ + c₂y₂)' = c₁y₁' + c₂y₂', and the same for the second "
            "derivative, while multiplying by p(t) or q(t) distributes over "
            "the sum.",
        ),
        Para(
            "So solutions of a homogeneous linear equation form a *vector "
            "space*: they can be added and scaled, and the result is still a "
            "solution. For nonlinear equations this fails completely — the "
            "sum of two solutions of y' = y² is not a solution — and that "
            "failure is why nonlinear equations need the entirely different "
            "tools of Unit 8."
        ),
        Worked(
            "Building solutions from solutions",
            "Check that cos t and sin t solve y'' + y = 0, and find the "
            "combination with y(0) = 2 and y'(0) = 3.",
            (
                Step("(cos t)'' = −cos t and (sin t)'' = −sin t, so each "
                     "satisfies y'' + y = 0, and by superposition so does "
                     "y = c₁cos t + c₂sin t.",
                     r"y = c_1\cos t + c_2\sin t, \qquad "
                     r"y' = -c_1\sin t + c_2\cos t"),
                Step("At t = 0: y = c₁ = 2 and y' = c₂ = 3."),
            ),
            equation="y'' + y = 0", conditions="y(0) = 2, y'(0) = 3",
            answer="2*cos(t) + 3*sin(t)", answer_latex=r"y(t) = 2\cos t + 3\sin t",
        ),
        Plot(
            "Combinations of cos t and sin t",
            "Solutions of y'' + y = 0 with (c₁, c₂) = (1, 0), (0, 1), (2, 3) "
            "and (−1, 1). Every combination is another oscillation of period "
            "2π; the constants set its amplitude and where in the cycle it "
            "starts. The curve for (2, 3) has amplitude √13 ≈ 3.6.",
            (Curve("cos(t)", "cos t"), Curve("sin(t)", "sin t"),
             Curve("2*cos(t) + 3*sin(t)", "2cos t + 3sin t"),
             Curve("-cos(t) + sin(t)", "−cos t + sin t")),
            t=(0.0, 12.6),
        ),
    )),
    Section("Existence and uniqueness", (
        Para(
            "A second-order equation needs two conditions to single out a "
            "solution — typically the position and the velocity at one "
            "instant. For linear equations the corresponding theorem is as "
            "strong as the first-order one from Unit 1: the solution exists "
            "on the whole interval where the coefficients are continuous, and "
            "it is unique."
        ),
        Box(
            "theorem", "Existence and uniqueness for linear equations",
            "If p, q and f are continuous on an open interval I containing "
            "t₀, then for any numbers b₀ and b₁ the problem below has exactly "
            "one solution, and it exists on the whole of I.",
            r"y'' + p y' + q y = f, \qquad y(t_0) = b_0,\;\; y'(t_0) = b_1",
        ),
        Para(
            "The interval is read off the coefficients. For "
            "t²y'' − 2ty' + 2y = 0, standard form has p = −2/t and q = 2/t², "
            "continuous except at t = 0, so a problem posed at t₀ = 1 has a "
            "unique solution on (0, ∞). That is exactly the information "
            "needed to trust the formula once it is found."
        ),
    )),
    Section("Independence and the Wronskian", (
        Para(
            "Superposition produces a two-parameter family c₁y₁ + c₂y₂ from "
            "two solutions. Two parameters are what two initial conditions "
            "need — but only if y₁ and y₂ are genuinely different. If "
            "y₂ = 3y₁, then c₁y₁ + c₂y₂ = (c₁ + 3c₂)y₁ is a one-parameter "
            "family wearing two constants, and it cannot meet two arbitrary "
            "conditions. The notion that rules this out is independence."
        ),
        Box(
            "definition", "Linear independence",
            "Two functions are *linearly independent* on an interval if "
            "neither is a constant multiple of the other there — "
            "equivalently, if c₁y₁ + c₂y₂ = 0 for every t forces c₁ = c₂ = 0.",
        ),
        Para(
            "For two functions, independence can usually be seen at a "
            "glance: e^t and e^(2t) are independent because their ratio e^t "
            "is not constant; t and 3t are dependent. For solutions of a "
            "linear equation there is also a test that is mechanical, and "
            "that generalises to any number of functions: the Wronskian."
        ),
        Box(
            "definition", "Wronskian",
            "The Wronskian of two differentiable functions is the determinant "
            "of the matrix whose rows are the functions and their "
            "derivatives.",
            r"W(y_1, y_2) = y_1 y_2' - y_1' y_2",
        ),
        Box(
            "theorem", "The Wronskian test",
            "Let y₁ and y₂ be solutions of y'' + py' + qy = 0 on I, with p and "
            "q continuous. Then either W(y₁, y₂) is zero at every point of I, "
            "and the solutions are dependent, or it is zero at no point of I, "
            "and they are independent.",
        ),
        Para(
            "The all-or-nothing behaviour comes from Abel's formula: "
            "differentiating W and using the equation shows W' = −pW, so "
            "W(t) = W(t₀)e^(−∫p dt). An exponential is never zero, so W is "
            "either zero everywhere or nowhere. In practice this means the "
            "Wronskian can be checked at the single most convenient point, "
            "usually t = 0."
        ),
        Worked(
            "Two exponentials",
            "Show that e^t and e^(2t) are independent solutions of "
            "y'' − 3y' + 2y = 0, and find the solution with y(0) = 1, "
            "y'(0) = 0.",
            (
                Step("Substituting e^t gives 1 − 3 + 2 = 0 times e^t, and e^(2t) "
                     "gives 4 − 6 + 2 = 0 times e^(2t). The Wronskian is "
                     "e^t · 2e^(2t) − e^t · e^(2t) = e^(3t), never zero.",
                     r"W(e^{t}, e^{2t}) = e^{3t} \neq 0"),
                Step("With y = c₁e^t + c₂e^(2t): y(0) = c₁ + c₂ = 1 and "
                     "y'(0) = c₁ + 2c₂ = 0. Subtracting, c₂ = −1 and c₁ = 2.",
                     r"c_1 + c_2 = 1, \qquad c_1 + 2c_2 = 0"),
            ),
            equation="y'' - 3*y' + 2*y = 0", conditions="y(0) = 1, y'(0) = 0",
            answer="2*exp(t) - exp(2*t)", answer_latex=r"y(t) = 2e^{t} - e^{2t}",
        ),
        Para(
            "The linear system for c₁ and c₂ had a unique solution because "
            "its determinant, 1·2 − 1·1 = 1, is the Wronskian at t = 0. That "
            "is the real meaning of the Wronskian: it is the determinant of "
            "the system that initial conditions produce, so a nonzero "
            "Wronskian is exactly the statement that every pair of initial "
            "conditions can be met."
        ),
    )),
    Section("Abel's formula", (
        Para(
            "The claim that the Wronskian of two solutions is either never "
            "zero or always zero deserves its short derivation, because the "
            "argument is a pleasant use of the equation itself. Differentiate "
            "W = y₁y₂' − y₁'y₂. The product rule produces four terms, and two "
            "of them, y₁'y₂' and −y₁'y₂', cancel."
        ),
        Display(r"W' = y_1 y_2'' - y_1'' y_2", "2"),
        Para(
            "Now use the equation to replace the second derivatives: "
            "yᵢ'' = −pyᵢ' − qyᵢ for each solution. The q terms cancel, and what "
            "remains is −p times the Wronskian. So W satisfies a first-order "
            "linear equation of its own, and Unit 1 solves it."
        ),
        Display(r"W' = -p(t)\, W \;\Longrightarrow\; W(t) = W(t_0)\, "
                r"e^{-\int_{t_0}^{t} p(s)\, ds}", "3"),
        Para(
            "Formula (3) is Abel's formula. It is a check as well as a "
            "theorem: for y'' − 3y' + 2y = 0, p = −3, so the Wronskian of any "
            "two solutions must be a constant times e^(3t) — and the Wronskian "
            "of e^t and e^(2t) computed above was exactly e^(3t). It also "
            "shows that the Wronskian can be known without knowing the "
            "solutions, which is the starting point for reduction of order "
            "later in this unit."
        ),
    )),
    Section("Why two conditions, and which two", (
        Para(
            "The theorems of this lesson answer a question that is easy to "
            "take for granted: why does a second-order equation need exactly "
            "two conditions, and why are y and y' at one point the right two? "
            "The answer is that the pair (y(t₀), y'(t₀)) is the *state* of the "
            "system: given it, the equation determines y'' at t₀, and with it "
            "the entire future and past. One condition leaves a whole family "
            "of solutions; three would generally be contradictory."
        ),
        Para(
            "Other pairs of conditions are possible but behave differently. "
            "Conditions at two different points — y(0) = 0 and y(π) = 0, say — "
            "make a *boundary value problem*, and for y'' + y = 0 that "
            "particular pair is satisfied by c sin t for every c: infinitely "
            "many solutions. Change the second point to y(π/2) = 0 and only "
            "y = 0 fits. Boundary value problems can have no solution, one, "
            "or infinitely many, and the clean theorem above is special to "
            "conditions at a single point."
        ),
    )),
    Section("The general solution", (
        Box(
            "theorem", "General solution of the homogeneous equation",
            "If y₁ and y₂ are independent solutions of y'' + py' + qy = 0 on "
            "I, then every solution on I is c₁y₁ + c₂y₂ for exactly one "
            "choice of the constants.",
            r"y = c_1 y_1 + c_2 y_2",
        ),
        Box(
            "proof", "",
            "Let Y be any solution and pick t₀ in I. Because W(y₁, y₂)(t₀) ≠ 0, "
            "the constants can be chosen so that c₁y₁ + c₂y₂ has the same "
            "value and derivative as Y at t₀. Then c₁y₁ + c₂y₂ and Y solve the "
            "same initial value problem, so by uniqueness they are the same "
            "function.",
        ),
        Para(
            "The theorem says the solution space is exactly two-dimensional, "
            "and any two independent solutions form a *basis* — a "
            "*fundamental set*. Different bases describe the same space. For "
            "y'' − y = 0 both {e^t, e^(−t)} and {cosh t, sinh t} are "
            "fundamental sets, and which to use is a matter of convenience: "
            "the hyperbolic functions suit conditions at t = 0, as the next "
            "example shows."
        ),
        Worked(
            "Choosing a convenient basis",
            "Solve y'' − y = 0 with y(0) = 1 and y'(0) = 0.",
            (
                Step("e^t and e^(−t) are solutions with Wronskian −2, so "
                     "y = c₁e^t + c₂e^(−t). The conditions give c₁ + c₂ = 1 and "
                     "c₁ − c₂ = 0, so c₁ = c₂ = 1/2.",
                     r"y = \frac{e^{t} + e^{-t}}{2}"),
                Step("That is cosh t. Had the basis been {cosh t, sinh t}, "
                     "whose values at 0 are (1, 0) and derivatives (0, 1), the "
                     "constants could have been read off directly: 1 and 0."),
            ),
            equation="y'' - y = 0", conditions="y(0) = 1, y'(0) = 0",
            answer="(exp(t) + exp(-t))/2", answer_latex=r"y(t) = \cosh t",
        ),
        Plot(
            "Two bases for the same solutions of y'' − y = 0",
            "e^t and e^(−t), and cosh t and sinh t built from them. Any "
            "solution is a combination of either pair; cosh and sinh are "
            "the combinations that start at (1, 0) and (0, 1).",
            (Curve("exp(t)", "e^t"), Curve("exp(-t)", "e^(−t)"),
             Curve("cosh(t)", "cosh t"), Curve("sinh(t)", "sinh t")),
            t=(-2.0, 2.0), ylim=(-4.0, 5.0),
        ),
    )),
    Section("Variable coefficients", (
        Para(
            "Nothing in the theory needs constant coefficients. The equation "
            "t²y'' − 2ty' + 2y = 0 has the solutions t and t², as substituting "
            "shows: for y = t², 2t² − 4t² + 2t² = 0. Their Wronskian is "
            "t·2t − 1·t² = t², nonzero on (0, ∞), so on that interval every "
            "solution is c₁t + c₂t². Where the solutions come from is the "
            "Cauchy–Euler lesson's business; that the pair spans everything "
            "is this lesson's."
        ),
        Worked(
            "An initial value problem away from t = 0",
            "Solve t²y'' − 2ty' + 2y = 0 with y(1) = 3, y'(1) = 5.",
            (
                Step("With y = c₁t + c₂t², y' = c₁ + 2c₂t. At t = 1: "
                     "c₁ + c₂ = 3 and c₁ + 2c₂ = 5, so c₂ = 2, c₁ = 1.",
                     r"c_1 + c_2 = 3, \qquad c_1 + 2c_2 = 5"),
                Step("The solution is valid on (0, ∞), where the coefficients "
                     "of the standard form are continuous."),
            ),
            equation="t**2*y'' - 2*t*y' + 2*y = 0", conditions="y(1) = 3, y'(1) = 5",
            answer="t + 2*t**2", answer_latex=r"y(t) = t + 2t^{2}",
        ),
        Para(
            "Variable coefficients are where the general theory earns its "
            "keep. For constant coefficients the next lesson produces two "
            "independent solutions by a recipe, and the theory mostly "
            "confirms what the recipe already gave. For variable coefficients "
            "there is no recipe in general, and the theory is what makes a "
            "pair of solutions found by any means — guessing, a table, a "
            "series — into a complete answer, and tells you on which interval "
            "that answer holds."
        ),
        Box(
            "warning", "The Wronskian test needs the equation",
            "t and t² have Wronskian t², which is zero at t = 0 and nonzero "
            "elsewhere — apparently contradicting the all-or-nothing theorem. "
            "It does not: the theorem applies on an interval where p and q "
            "are continuous, and p = −2/t is not continuous at 0. For "
            "arbitrary functions, a Wronskian vanishing at some points proves "
            "nothing.",
        ),
    )),
    Section("Nonhomogeneous equations", (
        Para(
            "With a forcing term the solutions no longer form a vector space "
            "— the sum of two solutions of L[y] = f solves L[y] = 2f — but "
            "they have a structure just as simple. The difference of two "
            "solutions of L[y] = f solves L[y] = 0. So once one solution of "
            "the forced equation is known, all the others are it plus a "
            "homogeneous solution."
        ),
        Box(
            "theorem", "Structure of the general solution",
            "If y_p is any one solution of L[y] = f and y₁, y₂ is a fundamental "
            "set for L[y] = 0, then every solution of L[y] = f is given below. "
            "The homogeneous part y_c = c₁y₁ + c₂y₂ is called the "
            "complementary function; y_p a particular solution.",
            r"y = y_c + y_p = c_1 y_1 + c_2 y_2 + y_p",
        ),
        Worked(
            "A forced oscillator",
            "Solve y'' + y = 2t with y(0) = 0, y'(0) = 0.",
            (
                Step("y_p = 2t is a particular solution: its second derivative "
                     "is zero, so y_p'' + y_p = 2t. The complementary function "
                     "is c₁cos t + c₂sin t.",
                     r"y = c_1\cos t + c_2 \sin t + 2t"),
                Step("y(0) = c₁ = 0. y'(0) = c₂ + 2 = 0, so c₂ = −2. The "
                     "constants are fitted to the *whole* solution, not to "
                     "the complementary function alone."),
            ),
            equation="y'' + y = 2*t", conditions="y(0) = 0, y'(0) = 0",
            answer="2*t - 2*sin(t)", answer_latex=r"y(t) = 2t - 2\sin t",
        ),
        Plot(
            "Particular solution plus oscillation",
            "y = 2t − 2 sin t, the solution of y'' + y = 2t from rest, beside "
            "the particular solution 2t. The complementary part −2 sin t makes "
            "the solution wind around the line for ever, because y'' + y = 0 "
            "has no damping to remove it.",
            (Curve("2*t - 2*sin(t)", "solution"), Curve("2*t", "y_p = 2t")),
            t=(0.0, 15.0),
        ),
        Box(
            "warning", "Fit the constants last",
            "The initial conditions apply to y_c + y_p, not to y_c. Fitting "
            "them to the complementary function first and then adding y_p "
            "produces a function that solves the equation and misses the "
            "conditions. The residual check in the drills catches exactly "
            "this mistake.",
        ),
        Figure("superposition",
               "Build a solution from a particular solution and two "
               "homogeneous ones, and watch the combination change as the "
               "constants move."),
    )),
    Section("Higher order", (
        Para(
            "Everything above extends to linear equations of order n. The "
            "solutions of a homogeneous equation of order n form an "
            "n-dimensional space; n independent solutions form a fundamental "
            "set; the Wronskian becomes an n × n determinant of the functions "
            "and their first n − 1 derivatives; and n initial conditions — y "
            "and its first n − 1 derivatives at one point — determine a "
            "unique solution on the interval where the coefficients are "
            "continuous."
        ),
        Worked(
            "A third-order equation",
            "Given that 1, e^t and e^(−t) solve y''' − y' = 0, find the "
            "solution with y(0) = 1, y'(0) = 0, y''(0) = 1.",
            (
                Step("y = c₁ + c₂e^t + c₃e^(−t), y' = c₂e^t − c₃e^(−t), "
                     "y'' = c₂e^t + c₃e^(−t). At t = 0 the three conditions "
                     "read:",
                     r"c_1 + c_2 + c_3 = 1, \quad c_2 - c_3 = 0, \quad "
                     r"c_2 + c_3 = 1"),
                Step("So c₂ = c₃ = 1/2 and c₁ = 0: three conditions, three "
                     "constants, one solution — cosh t again."),
            ),
            equation="y''' - y' = 0", conditions="y(0) = 1, y'(0) = 0, y''(0) = 1",
            answer="exp(t)/2 + exp(-t)/2", answer_latex=r"y(t) = \cosh t",
        ),
    )),
    Section("Summary", (
        Para(
            "A linear second-order equation y'' + py' + qy = f is governed by "
            "the linearity of its left-hand side. For the homogeneous "
            "equation, any combination of solutions is a solution, and two "
            "independent solutions — checked by a nonzero Wronskian at a "
            "single point — combine into the general solution c₁y₁ + c₂y₂, "
            "which contains every solution. Two initial conditions fix the "
            "constants uniquely, on the whole interval where p and q are "
            "continuous. For the forced equation, every solution is one "
            "particular solution plus the complementary function, and the "
            "constants are fitted to the sum. The rest of the unit is about "
            "finding y₁, y₂ and y_p: from characteristic roots, from "
            "undetermined coefficients, from variation of parameters, and "
            "from reduction of order."
        ),
    )),
)
