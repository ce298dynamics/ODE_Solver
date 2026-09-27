"""Unit 3 chapters -- second-order linear equations (Edwards ch. 3)."""

from __future__ import annotations

from ..chapter import Box, Curve, Display, Figure, Para, Plot, Section, Step, Worked

__all__ = ["SUPERPOSITION"]


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
