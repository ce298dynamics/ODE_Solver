"""Unit 6 chapters -- linear systems (Edwards 4.1, 5.1-5.6, 6.1-6.2)."""

from __future__ import annotations

from ..chapter import Box, Curve, Display, Figure, Para, Plot, Section, Step, Worked

__all__ = ["INTRO", "DISTINCT", "COMPLEX", "REPEATED", "NONHOMOGENEOUS", "PORTRAITS"]


INTRO = (
    Section("Two unknowns that will not come apart", (
        Para(
            "Every equation in the course so far has had one unknown function. "
            "Very little in the world comes that way. Two tanks exchange brine "
            "through a pair of pipes, and the salt in each depends on the salt "
            "in the other. Two masses are joined by a spring, and each is pulled "
            "by where the other one is. A predator population grows on its prey "
            "while the prey shrinks under it; the currents in two loops of a "
            "circuit share a resistor. In every case there are two unknowns, and "
            "each one's rate of change depends on both."
        ),
        Para(
            "That dependence is what makes this genuinely new rather than two "
            "old problems side by side. Neither equation can be solved first, "
            "because each needs the answer to the other. This chapter sets up "
            "the language for such problems: what a first-order system is, why "
            "coupling is the whole difficulty, how a linear system becomes a "
            "single equation between vectors, and — the observation that gives "
            "the chapter its title — how every higher-order equation in the "
            "course, and every coupled set of them, turns into a first-order "
            "system without losing or adding anything. The rest of the unit is "
            "then one method, the eigenvalue method, applied to that single "
            "form."
        ),
    )),
    Section("What a first-order system is", (
        Para(
            "A first-order system in two unknowns x(t) and y(t) is a pair of "
            "equations, each giving the derivative of one unknown in terms of "
            "time and both unknowns. In general there are n unknowns x₁, …, xₙ "
            "and n equations, one for each derivative."
        ),
        Display(r"x_1' = f_1(t, x_1, \ldots, x_n), \quad \ldots, \quad "
                r"x_n' = f_n(t, x_1, \ldots, x_n)", "1"),
        Box(
            "definition", "Linear systems",
            "The system (1) is *linear* when every right-hand side is a linear "
            "combination of the unknowns plus a function of t alone. It is "
            "*homogeneous* when those functions of t are all zero, and has "
            "*constant coefficients* when the multipliers of the unknowns do not "
            "depend on t. A *solution* on an interval is a set of n "
            "differentiable functions that make every equation true at every "
            "point of the interval; an *initial value problem* also prescribes "
            "the value of every unknown at one time t = a.",
            r"x' = a(t)\,x + b(t)\,y + f(t), \qquad y' = c(t)\,x + d(t)\,y + g(t)",
        ),
        Para(
            "Almost the whole unit is about the homogeneous constant-coefficient "
            "case, x' = ax + by, y' = cx + dy, with numbers a, b, c, d. The "
            "functions f and g return in the forced-systems chapter, the fifth of the "
            "unit, and nonlinear right-hand sides — the predator and its "
            "prey — are the subject of the unit on nonlinear systems, which "
            "leans on everything built here."
        ),
        Para(
            "When b = 0 and c = 0 the system is not really a system at all. "
            "Each equation mentions only its own unknown, and the pair is two "
            "problems from the first unit printed next to each other. It is "
            "worth solving one such pair, if only to see what the rest of the "
            "unit is trying to get back to."
        ),
        Worked(
            "A system that is not coupled",
            "Solve x' = 2x, y' = −y with x(0) = 3, y(0) = 4.",
            (
                Step("Each equation involves one unknown, so each is the growth "
                     "equation y' = ky of the first unit, solved on its own.",
                     r"x = C_1 e^{2t}, \qquad y = C_2 e^{-t}"),
                Step("Each condition fixes its own constant: C₁ = 3 and C₂ = 4.",
                     r"x = 3e^{2t}, \qquad y = 4e^{-t}"),
            ),
            equation="x' = 2*x; y' = -y",
            conditions="x(0) = 3, y(0) = 4",
            answer="x = 3*exp(2*t)\ny = 4*exp(-t)",
            answer_latex=r"x = 3e^{2t}, \quad y = 4e^{-t}",
        ),
        Para(
            "Two things are worth noticing even here. There are two arbitrary "
            "constants, one per equation, and two conditions to fix them. And "
            "the answer is best thought of as a single moving point (x(t), y(t)) "
            "rather than as two unrelated graphs: this one heads off to the "
            "right while dropping towards the x-axis, since x grows and y "
            "decays."
        ),
    )),
    Section("Coupling: why neither can go first", (
        Para(
            "Now take the system that will serve as the running example of the "
            "unit."
        ),
        Display(r"x' = x + 2y, \qquad y' = 3x + 2y", "2"),
        Para(
            "The rate of x depends on y. To solve the first equation for x one "
            "would need y as a known function of t, and y is exactly what the "
            "second equation is still trying to find — while the second equation, "
            "in turn, needs x. That circularity is what *coupled* means, and "
            "everything in this unit exists because it has to be broken all at "
            "once rather than in order. The equations are perfectly linear; "
            "linearity is not the obstacle, it is what will make the obstacle "
            "surmountable."
        ),
        Para(
            "For two unknowns there is an old way through, the *method of "
            "elimination*. Use one equation to express one unknown in terms of "
            "the other and its derivative, and substitute into the other "
            "equation. What comes out is a single second-order equation, which "
            "the second-order unit already knows how to solve."
        ),
        Worked(
            "Solving by elimination",
            "Find the general solution of x' = x + 2y, y' = 3x + 2y.",
            (
                Step("The first equation gives y in terms of x and x'.",
                     r"y = \frac{x' - x}{2}"),
                Step("Differentiate that, and substitute both into the second "
                     "equation. Multiplying by 2 and collecting terms leaves one "
                     "equation in x alone.",
                     r"\frac{x'' - x'}{2} = 3x + (x' - x) \;\Longrightarrow\; "
                     r"x'' - 3x' - 4x = 0"),
                Step("Its characteristic polynomial is r² − 3r − 4 = (r − 4)(r + 1), "
                     "with roots 4 and −1.",
                     r"x = C_1 e^{4t} + C_2 e^{-t}"),
                Step("Recover y from the first step rather than solving for it "
                     "separately: doing so would introduce two more constants "
                     "that the system does not allow.",
                     r"y = \frac{x' - x}{2} = \frac{3}{2}C_1 e^{4t} - C_2 e^{-t}"),
            ),
            equation="x' = x + 2*y; y' = 3*x + 2*y",
            answer="x = C1*exp(4*t) + C2*exp(-t)\ny = 3*C1*exp(4*t)/2 - C2*exp(-t)",
            answer_latex=r"x = C_1 e^{4t} + C_2 e^{-t}, \quad "
                         r"y = \frac{3}{2}C_1 e^{4t} - C_2 e^{-t}",
        ),
        Para(
            "The last step deserves its warning. It is tempting to eliminate x "
            "as well, find a second equation y'' − 3y' − 4y = 0, and write "
            "y = C₃e^(4t) + C₄e^(−t). Each line would then satisfy its own "
            "second-order equation, but four constants cannot all be free: "
            "substituting back into x' = x + 2y ties C₃ and C₄ to C₁ and C₂."
        ),
        Para(
            "Elimination works, but it is laborious, it hides the structure, "
            "and it scales badly: with three unknowns the substitutions branch, "
            "and with ten they are hopeless. What it does reveal is worth "
            "keeping. Two numbers, 4 and −1, govern the whole solution, and "
            "they came from a quadratic. The next section finds that quadratic "
            "without eliminating anything."
        ),
    )),
    Section("Matrix form", (
        Para(
            "Write the two equations with their unknowns in the same order on "
            "the right, and notice that the coefficients form an array. Stack "
            "the unknowns into a column vector — printed in bold in the "
            "displays, and written plain as x in the text when no confusion is "
            "possible — and gather the coefficients into the matrix A whose "
            "rows are (a, b) and (c, d). Multiplying A by the vector (x, y) "
            "reproduces both right-hand sides at once, so the pair of equations "
            "becomes one equation between vectors. In the displays a "
            "superscript T, as in (x, y)ᵀ, means the row written as a column."
        ),
        Display(r"\mathbf{x} = (x,\ y)^{T}, \qquad \mathbf{x}' = (x',\ y')^{T} "
                r"= (ax + by,\ cx + dy)^{T} = A\mathbf{x}", "3"),
        Para(
            "For the running example (2), A has rows (1, 2) and (3, 2). The first "
            "row lists how x' depends on x and y; the second, how y' does. An "
            "off-diagonal entry is exactly a coupling: b says how strongly y "
            "drives x, and c how strongly x drives y. A matrix with zeros off "
            "its diagonal, like the one for the uncoupled example (rows (2, 0) "
            "and (0, −1)), is a system that falls apart into separate equations."
        ),
        Para(
            "The equation x' = Ax is worth staring at, because it is the equation the "
            "course opened with: a rate proportional to the amount. Only the "
            "constant of proportionality is now a matrix, and the entire "
            "difficulty of the unit is that multiplying by a matrix, unlike "
            "multiplying by a number, changes direction as well as size. The "
            "solution of y' = ky is Ce^(kt). The eigenvalue method of the next "
            "chapter looks for directions in which A acts like a number, and "
            "along those directions the old exponential comes straight back."
        ),
        Display(r"y' = ky \quad\longleftrightarrow\quad \mathbf{x}' = A\mathbf{x}",
                "4"),
        Para(
            "Two numbers built from A will keep appearing: its *trace*, "
            "tr A = a + d, the sum of the diagonal, and its *determinant*, "
            "det A = ad − bc. Running the elimination of the last section with "
            "letters instead of numbers shows why."
        ),
        Box(
            "theorem", "What elimination always produces",
            "For any constant-coefficient system x' = ax + by, y' = cx + dy, "
            "both x and y satisfy the second-order equation below, whose "
            "coefficients are the trace and the determinant of A.",
            r"x'' - (\operatorname{tr} A)\,x' + (\det A)\,x = 0",
        ),
        Box(
            "proof", "Proof",
            "Suppose first that b ≠ 0. From the first equation, "
            "y = (x' − ax)/b. Differentiate: y' = (x'' − ax')/b. Substitute "
            "both into y' = cx + dy and multiply through by b. The result is "
            "x'' − ax' = bcx + dx' − adx, which rearranges to the statement. "
            "If b = 0, then x' = ax, so x = Ce^(at), and the check is direct: "
            "a² − (a + d)a + ad = 0. The argument for y is the same with the "
            "roles of the equations exchanged, using c in place of b.",
            r"x'' - (a + d)\,x' + (ad - bc)\,x = 0",
        ),
        Para(
            "Check it on the running example: tr A = 1 + 2 = 3 and "
            "det A = 2 − 6 = −4, which gives x'' − 3x' − 4x = 0, exactly as "
            "found. The quadratic λ² − (tr A)λ + det A has a name in linear "
            "algebra, and so do its roots."
        ),
        Box(
            "definition", "Eigenvalues and eigenvectors",
            "A number λ is an *eigenvalue* of the square matrix A if Av = λv "
            "for some non-zero vector v, called an *eigenvector* for λ. Writing "
            "I for the identity matrix (ones on the diagonal, zeros elsewhere), "
            "that says (A − λI)v = 0 with v ≠ 0, which happens exactly when "
            "A − λI is singular. So the eigenvalues are the roots of the "
            "*characteristic polynomial* det(A − λI). For a 2 × 2 matrix with "
            "rows (a, b) and (c, d) it is (a − λ)(d − λ) − bc, which is the "
            "quadratic of the theorem above. The next chapter explains why "
            "these numbers govern the solutions.",
            r"\det(A - \lambda I) = \lambda^{2} - (\operatorname{tr} A)\,\lambda "
            r"+ \det A",
        ),
        Para(
            "For the running example the roots are 4 and −1, the two numbers "
            "elimination found. That is the secret of the unit in one line: the "
            "numbers that govern a linear system are the eigenvalues of its "
            "matrix, and they can be read from A without any substitution. The "
            "phase-portraits chapter will classify every two-by-two system by "
            "its trace and determinant, with only the sense of rotation and "
            "one borderline case needing a further look at A."
        ),
        Para(
            "When the coefficients depend on t, or the equations are forced, "
            "the same bookkeeping still applies: the multipliers of the unknowns "
            "go into a matrix P(t), and the functions of t alone into a vector "
            "f(t). This is the general linear system; the homogeneous "
            "constant-coefficient case is P = A, f = 0, and the forced-systems "
            "chapter at the end of the unit keeps P = A constant but allows "
            "any forcing f."
        ),
        Display(r"\mathbf{x}' = P(t)\,\mathbf{x} + \mathbf{f}(t)", "5"),
    )),
    Section("Every higher-order equation is a system", (
        Para(
            "The same form swallows every higher-order equation met so far. "
            "Take py'' + qy' + ry = 0, with p ≠ 0 (new letters, so as not to "
            "clash with the entries of A), and name the derivatives as new "
            "unknowns: x₁ = y and x₂ = y'. Then x₁' is x₂ by definition, and "
            "the equation itself supplies x₂' = y''. No information is added or "
            "lost."
        ),
        Display(r"x_1 = y,\ x_2 = y' \;\Longrightarrow\; x_1' = x_2, \quad "
                r"x_2' = -\frac{r}{p}x_1 - \frac{q}{p}x_2", "6"),
        Para(
            "The two rows are doing different jobs. The first is a definition — "
            "the second unknown *is* the derivative of the first — and only the "
            "second row carries any physics. That asymmetry means the matrix "
            "produced this way always has the same shape: first row (0, 1), "
            "second row (−r/p, −q/p). It is called the *companion matrix* of the "
            "equation, and its characteristic polynomial, "
            "λ² + (q/p)λ + r/p, is the characteristic polynomial of the "
            "original equation divided by p. So the eigenvalues of the "
            "companion matrix are exactly the characteristic roots."
        ),
        Box(
            "theorem", "Reduction to a first-order system",
            "The nth-order equation below is equivalent to the first-order "
            "system x₁' = x₂, x₂' = x₃, …, xₙ₋₁' = xₙ, xₙ' = f(t, x₁, …, xₙ), "
            "under the substitution x₁ = y, x₂ = y', …, xₙ = y⁽ⁿ⁻¹⁾. The n "
            "initial values of y, y', …, y⁽ⁿ⁻¹⁾ become the n initial values "
            "of x₁, …, xₙ. Every solution of one gives a solution of the other.",
            r"y^{(n)} = f\left(t, y, y', \ldots, y^{(n-1)}\right)",
        ),
        Para(
            "The proof is the construction itself. If y solves the equation, "
            "its derivatives solve the system by definition; if x₁, …, xₙ solve "
            "the system, the first n − 1 equations say that each xₖ is the "
            "(k − 1)th derivative of x₁, and the last one then says that x₁ "
            "solves the original equation."
        ),
        Worked(
            "An equation turned into a system",
            "Convert y'' + 3y' + 2y = 0, y(0) = 1, y'(0) = 0 into a first-order "
            "system and solve it.",
            (
                Step("Name x₁ = y and x₂ = y'. The first row is the naming; the "
                     "second is the equation solved for y''. The companion "
                     "matrix has rows (0, 1) and (−2, −3), and the conditions "
                     "carry over directly.",
                     r"x_1' = x_2, \quad x_2' = -2x_1 - 3x_2, \quad x_1(0) = 1, "
                     r"\; x_2(0) = 0"),
                Step("Its characteristic polynomial is λ² + 3λ + 2 = (λ + 1)(λ + 2): "
                     "the same polynomial as r² + 3r + 2, so the eigenvalues are "
                     "the characteristic roots −1 and −2.",
                     r"\det(A - \lambda I) = \lambda^{2} + 3\lambda + 2"),
                Step("Solve for x₁ = y as in the second-order unit: "
                     "y = C₁e^(−t) + C₂e^(−2t), and the conditions give "
                     "C₁ = 2, C₂ = −1.",
                     r"x_1 = 2e^{-t} - e^{-2t}"),
                Step("The second component is not solved for separately: it is "
                     "the derivative of the first.",
                     r"x_2 = x_1' = -2e^{-t} + 2e^{-2t}"),
            ),
            equation="x1' = x2; x2' = -2*x1 - 3*x2",
            conditions="x1(0) = 1, x2(0) = 0",
            answer="x1 = 2*exp(-t) - exp(-2*t)\nx2 = -2*exp(-t) + 2*exp(-2*t)",
            answer_latex=r"x_1 = 2e^{-t} - e^{-2t}, \quad x_2 = -2e^{-t} + 2e^{-2t}",
        ),
        Para(
            "Here the solution was reached by going round the long way — "
            "solving the scalar equation for x₁ and differentiating to get x₂; "
            "the next chapter reaches it from the matrix directly. The "
            "eigenvalue method is not an alternative to the second-order unit; "
            "it is the same computation with different notation around it."
        ),
        Para(
            "Forcing terms and variable coefficients change nothing in the "
            "construction. They ride along in the last row, which is why the "
            "general linear form (5) needs its P(t) and f(t)."
        ),
        Worked(
            "A forced third-order equation with a variable coefficient",
            "Write 2y''' − 4y'' + 6ty' + y = e^t, y(0) = 1, y'(0) = 0, "
            "y''(0) = −1 as a first-order system in the form (5).",
            (
                Step("Third order needs three unknowns: x₁ = y, x₂ = y', "
                     "x₃ = y''. The first two rows are the naming.",
                     r"x_1' = x_2, \quad x_2' = x_3"),
                Step("Divide the equation by the leading coefficient 2 and "
                     "solve for y''' = x₃'. Every term moves across except the "
                     "one being solved for, so every sign changes.",
                     r"x_3' = -\frac{1}{2}x_1 - 3t\,x_2 + 2x_3 + \frac{1}{2}e^{t}"),
                Step("Read off the pieces. P(t) has rows (0, 1, 0), (0, 0, 1) and "
                     "(−1/2, −3t, 2): the variable coefficient sits in the "
                     "matrix. The forcing goes into f(t) = (0, 0, e^t/2)ᵀ, and "
                     "the three conditions become the initial state.",
                     r"\mathbf{x}(0) = (1,\ 0,\ -1)^{T}"),
            ),
        ),
    )),
    Section("The state, and the plane it lives in", (
        Para(
            "Why should the pair (y, y') deserve to be treated as a single "
            "object? Because it is exactly the information needed to continue "
            "the motion from an instant. Knowing where a mass is does not say "
            "where it will be next; knowing where it is and how fast it is "
            "moving does, completely. The vector of a solution's value and its "
            "derivatives is called the *state*, and that is precisely why an "
            "equation of order n takes n conditions."
        ),
        Display(r"\text{order } n \;\Longleftrightarrow\; n \text{ components} "
                r"\;\Longleftrightarrow\; n \text{ conditions}", "7"),
        Para(
            "With two components, the state is a point in a plane — the *state "
            "plane*, or *phase plane* — and a solution traces a curve in it, a "
            "*trajectory*. The worked example above can be drawn two ways: as "
            "the two graphs of y and y' against t, or as the single curve "
            "(x₁(t), x₂(t)). Both pictures carry the same information, but the "
            "second shows the state moving as one thing."
        ),
        Plot(
            "Two graphs against time",
            "y = 2e^(−t) − e^(−2t) and its derivative y' for the worked example. "
            "The position falls steadily from 1; the velocity drops from 0 to "
            "its most negative value, −1/2, at t = ln 2 and then relaxes back "
            "towards zero.",
            (Curve("2*exp(-t) - exp(-2*t)", "y = x₁"),
             Curve("-2*exp(-t) + 2*exp(-2*t)", "y′ = x₂")),
            t=(0.0, 6.0), ylim=(-0.7, 1.1), ylabel="value",
        ),
        Plot(
            "The same solution as one curve",
            "The point (x₁, x₂) = (y, y') for the same solution, starting at "
            "(1, 0). It dips to (3/4, −1/2) at t = ln 2 and then approaches the "
            "origin along the line x₂ = −x₁, the direction of the slower "
            "eigenvalue −1 — a fact the next chapter explains. The second curve "
            "starts from (−1, 1) and runs straight in along that same line, "
            "from the other side. Straight-line trajectories like that one run "
            "along eigenvectors of A — a fixed eigenvector times e^(λt) — and "
            "the eigenvalues chapter is built on them.",
            (Curve("2*exp(-t) - exp(-2*t)", "from (1, 0)",
                   y="-2*exp(-t) + 2*exp(-2*t)"),
             Curve("-exp(-t)", "from (−1, 1)", y="exp(-t)")),
            t=(0.0, 8.0), xlabel="x₁ = y", ylabel="x₂ = y′", ylim=(-0.7, 1.1),
        ),
        Box(
            "theorem", "Existence and uniqueness for systems",
            "If each fᵢ in the system x' = F(t, x) and each partial derivative "
            "∂fᵢ/∂xⱼ is continuous near (a, x₀), then the initial value problem "
            "x' = F(t, x), x(a) = x₀ has exactly one solution on some interval "
            "around t = a. This covers nonlinear systems such as the pendulum; "
            "for linear systems a stronger, whole-interval version appears "
            "below.",
            r"\mathbf{x}' = \mathbf{F}(t, \mathbf{x}), \quad "
            r"\mathbf{x}(a) = \mathbf{x}_0",
        ),
        Para(
            "For a system x' = F(x) that does not involve t explicitly, a "
            "trajectory has a further property. At every point of the plane "
            "the system prescribes the velocity of the state, the vector "
            "Ax for a linear system. If two trajectories met at a point they "
            "would leave it with the same velocity and, by uniqueness, would "
            "be the same trajectory — even if they reached it at different "
            "times, because when F does not involve t a solution shifted in "
            "time is still a solution, so uniqueness applies after the shift. "
            "So distinct trajectories never cross, and "
            "the plane is filled with curves that fit together without "
            "intersecting — the picture the phase-portraits chapter learns to "
            "read without solving anything."
        ),
        Figure("state_plane",
               "The figure solves y″ + by′ + cy = 0 and shows the answer twice: "
               "y and y′ against time on the left, the point (y, y′) moving in "
               "the plane on the right. Keep the start near (1, 0), set b to 0 "
               "with c above about 0.3, and the curve closes into a loop — an "
               "undamped oscillation returns to its starting state. Raise b and "
               "the loop becomes a spiral into the origin; raise b and lower c "
               "until b² exceeds 4c, and the spiral straightens into a direct "
               "approach. Then move the y(0) and y′(0) sliders: every start "
               "gives a different curve, and no curve ever crosses itself."),
    )),
    Section("An oscillator in the plane", (
        Para(
            "Conversion is not only for overdamped examples. The undamped "
            "oscillator gives a system whose matrix has zeros on its diagonal, "
            "and that shape is worth recognising before any eigenvalue is "
            "computed."
        ),
        Worked(
            "The oscillator as a system",
            "Convert y'' + 4y = 0, y(0) = 0, y'(0) = 2 into a system, solve it, "
            "and describe the trajectory.",
            (
                Step("With x₁ = y and x₂ = y', the companion matrix has rows "
                     "(0, 1) and (−4, 0). Nothing damps the motion, and each "
                     "unknown drives only the other.",
                     r"x_1' = x_2, \quad x_2' = -4x_1"),
                Step("The characteristic polynomial λ² + 4 has no real roots: "
                     "the eigenvalues are ±2i. As a scalar equation, "
                     "y = C₁cos 2t + C₂sin 2t; y(0) = 0 removes the cosine and "
                     "y'(0) = 2C₂ = 2 gives C₂ = 1.",
                     r"x_1 = \sin 2t"),
                Step("Again the second component is the derivative of the first.",
                     r"x_2 = 2\cos 2t"),
                Step("Eliminate t: since sin² + cos² = 1, the state lies on an "
                     "ellipse, crossing the x₁-axis at ±1 and the x₂-axis at ±2, "
                     "and goes round it once every π time units.",
                     r"x_1^{2} + \frac{x_2^{2}}{4} = 1"),
            ),
            equation="x1' = x2; x2' = -4*x1",
            conditions="x1(0) = 0, x2(0) = 2",
            answer="x1 = sin(2*t)\nx2 = 2*cos(2*t)",
            answer_latex=r"x_1 = \sin 2t, \quad x_2 = 2\cos 2t",
        ),
        Para(
            "For a single equation, a characteristic polynomial with no real "
            "roots meant an oscillation. In the plane it means trajectories that "
            "go round the origin rather than into it or away from it — the same "
            "fact about the same numbers, seen as a picture rather than against "
            "time. Which way round? At (1, 0) the velocity is Ax = (0, −4), "
            "straight down, so the motion is clockwise. Hold on to this matrix: "
            "the chapter on complex eigenvalues calls closed orbits like this "
            "one centres, and the phase-portraits chapter returns to this very "
            "system as its example of one."
        ),
        Plot(
            "An undamped oscillation is a closed curve",
            "The state (sin 2t, 2cos 2t) of the worked example, over one "
            "period. It starts at the top, (0, 2), and runs clockwise round the "
            "ellipse x₁² + x₂²/4 = 1, coming back to its start at t = π and "
            "repeating for ever.",
            (Curve("sin(2*t)", "state", y="2*cos(2*t)"),),
            t=(0.0, 3.1416), xlabel="x₁ = y", ylabel="x₂ = y′", ylim=(-2.3, 2.3),
        ),
    )),
    Section("Larger systems, and coupled second-order equations", (
        Para(
            "Nothing in the conversion depended on the order being two. A "
            "third-order equation needs three unknowns, x₁ = y, x₂ = y', "
            "x₃ = y'', and becomes x₁' = x₂, x₂' = x₃, x₃' = whatever the "
            "equation says y''' is. Nor did it depend on linearity: the "
            "pendulum θ'' + (g/L) sin θ = 0 becomes x₁' = x₂, "
            "x₂' = −(g/L) sin x₁, a nonlinear system whose study belongs to "
            "the nonlinear unit. And it applies to several coupled equations at "
            "once, which is how a mechanical system with several masses reaches "
            "first-order form."
        ),
        Worked(
            "Two masses and two springs",
            "Masses m₁ = 2 and m₂ = 1 lie in a line on a frictionless table: "
            "a spring of constant "
            "k₁ = 4 joins the first to a wall and a spring of constant k₂ = 2 "
            "joins the two masses. With x and y the displacements from "
            "equilibrium, write the motion as a first-order system.",
            (
                Step("The first spring pulls the first mass back with force −4x; "
                     "the second spring is stretched by y − x and pulls the two "
                     "masses towards each other. With the numbers in, Newton's "
                     "law reads 2x'' = −6x + 2y and y'' = 2x − 2y.",
                     r"m_1 x'' = -k_1 x + k_2 (y - x), \qquad m_2 y'' = "
                     r"-k_2 (y - x)"),
                Step("Each second-order equation needs two unknowns, so there "
                     "are four: x₁ = x, x₂ = x', x₃ = y, x₄ = y'."),
                Step("Two rows are definitions and two carry the physics, "
                     "after dividing by the masses.",
                     r"x_1' = x_2, \quad x_2' = -3x_1 + x_3, \quad x_3' = x_4, "
                     r"\quad x_4' = 2x_1 - 2x_3"),
                Step("The 4 × 4 matrix has rows (0, 1, 0, 0), (−3, 0, 1, 0), "
                     "(0, 0, 0, 1) and (2, 0, −2, 0). Rather than expand its "
                     "determinant, use the structure. The positions alone satisfy "
                     "x'' = −3x + y, y'' = 2x − 2y, a system whose matrix M has "
                     "rows (−3, 1) and (2, −2). Trying a solution v·e^(λt) turns "
                     "the second derivative into λ², so λ² must be an eigenvalue "
                     "of M: det(M − λ²I) = (λ² + 3)(λ² + 2) − 2 = λ⁴ + 5λ² + 4.",
                     r"\lambda^{4} + 5\lambda^{2} + 4 = (\lambda^{2} + 1)"
                     r"(\lambda^{2} + 4)"),
                Step("So λ² = −1 or λ² = −4, and the eigenvalues of the 4 × 4 "
                     "matrix are ±i and ±2i. Expanding its determinant directly "
                     "gives the same polynomial.",
                     r"\det(A - \lambda I) = (\lambda^{2} + 1)(\lambda^{2} + 4)"),
            ),
        ),
        Para(
            "The last step is a glimpse of what the unit is for. The "
            "eigenvalues ±i and ±2i say that this pair of masses has two natural "
            "angular frequencies, 1 and 2 (periods 2π and π), and that every "
            "free motion is a combination of those two modes. Eliminating by "
            "hand would have reached a fourth-order equation for x with the "
            "same information buried in it; the matrix gives it directly."
        ),
    )),
    Section("Superposition, and counting constants", (
        Para(
            "Linearity survives the move to vectors intact, because matrix "
            "multiplication is linear. In this section a subscript names a "
            "whole solution vector, not a component: if x₁ and x₂ both solve "
            "x' = Ax, then differentiating c₁x₁ + c₂x₂ gives c₁Ax₁ + c₂Ax₂, "
            "and that is A(c₁x₁ + c₂x₂)."
        ),
        Box(
            "theorem", "Superposition",
            "Any linear combination of solutions of a homogeneous linear system "
            "x' = Ax is again a solution. This holds for A depending on t as "
            "well as for constant A.",
            r"(c_1\mathbf{x}_1 + c_2\mathbf{x}_2)' = c_1 A\mathbf{x}_1 + "
            r"c_2 A\mathbf{x}_2 = A(c_1\mathbf{x}_1 + c_2\mathbf{x}_2)",
        ),
        Para(
            "So the plan is the same as it was at second order: find enough "
            "independent solutions, combine them with constants, and fit the "
            "conditions. Only the meaning of *independent* needs restating, and "
            "linear algebra has the word already. Vector functions x₁, …, xₙ "
            "are linearly independent if no combination of them with constants "
            "not all zero is the zero function. For solutions of a linear "
            "system, independence can be tested at a single instant by the "
            "*Wronskian*, the determinant of the matrix whose columns are the "
            "solutions: it is either never zero or always zero. For the system "
            "that comes from a second-order equation, the columns are "
            "(y₁, y₁') and (y₂, y₂'), and this determinant is exactly the "
            "Wronskian of the second-order unit. Abel's formula carries over "
            "too, W(t) = W(a)·e^(∫ tr A dt) with the integral taken from a to t, "
            "and an exponential is never zero — which is why the Wronskian "
            "cannot vanish at one instant and not at another."
        ),
        Box(
            "theorem", "Existence, uniqueness and the general solution",
            "If the entries of A(t) are continuous on an open interval "
            "containing t = a, then for any initial vector x₀ the problem "
            "x' = Ax, x(a) = x₀ has exactly one solution, and it exists on the "
            "whole interval. If x₁, …, xₙ are n independent solutions of the "
            "n × n system, every solution is one of their combinations, so the "
            "general solution has exactly n arbitrary constants.",
            r"\mathbf{x} = c_1\mathbf{x}_1 + \cdots + c_n\mathbf{x}_n",
        ),
        Para(
            "The count of constants follows the number of equations, not the "
            "number of entries in A: a 3 × 3 system has 3 constants, one for "
            "each initial value, not 9."
        ),
        Worked(
            "Fitting constants to two known solutions",
            "Check that x₁ = (−e^(−t), e^(−t)) and x₂ = (2e^(4t), 3e^(4t)) solve "
            "x' = x + 2y, y' = 3x + 2y, check that they are independent, and "
            "find the solution with x(0) = 1, y(0) = 0.",
            (
                Step("For x₁: x' = e^(−t), and x + 2y = −e^(−t) + 2e^(−t) = e^(−t); "
                     "y' = −e^(−t), and 3x + 2y = −3e^(−t) + 2e^(−t) = −e^(−t). For "
                     "x₂: x' = 8e^(4t) = (2 + 6)e^(4t), and y' = 12e^(4t) = "
                     "(6 + 6)e^(4t). Both solve the system."),
                Step("The Wronskian is the determinant with these as columns. "
                     "It is never zero, so the two are independent. Abel's "
                     "formula agrees: tr A = 3 and W(0) = −5 give −5e^(3t).",
                     r"W(t) = (-e^{-t})(3e^{4t}) - (2e^{4t})(e^{-t}) = -5e^{3t}"),
                Step("The general solution is c₁x₁ + c₂x₂. At t = 0 the "
                     "conditions give −c₁ + 2c₂ = 1 and c₁ + 3c₂ = 0, so "
                     "c₁ = −3/5 and c₂ = 1/5.",
                     r"\mathbf{x}(0) = c_1(-1,\ 1)^{T} + c_2(2,\ 3)^{T} = "
                     r"(1,\ 0)^{T}"),
                Step("Assemble the two components.",
                     r"x = \frac{3}{5}e^{-t} + \frac{2}{5}e^{4t}, \quad "
                     r"y = -\frac{3}{5}e^{-t} + \frac{3}{5}e^{4t}"),
            ),
            equation="x' = x + 2*y; y' = 3*x + 2*y",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = 3*exp(-t)/5 + 2*exp(4*t)/5\ny = -3*exp(-t)/5 + 3*exp(4*t)/5",
            answer_latex=r"x = \frac{3}{5}e^{-t} + \frac{2}{5}e^{4t}, \quad "
                         r"y = -\frac{3}{5}e^{-t} + \frac{3}{5}e^{4t}",
        ),
        Para(
            "These are the solutions from the elimination example with "
            "particular constants: x₂ is C₁ = 2, C₂ = 0 there, and x₁ is "
            "C₁ = 0, C₂ = −1. Each of them is a fixed vector, (−1, 1) or (2, 3), "
            "multiplied by an exponential, so each moves along a straight line "
            "through the origin. Where those vectors come from, and why their "
            "exponents are the eigenvalues −1 and 4, is the whole content of "
            "the next chapter."
        ),
    )),
    Section("Two tanks", (
        Para(
            "Here is a coupled system from a physical problem, solved by a "
            "trick that is the eigenvalue method in disguise. Tank 1 holds 20 "
            "litres of water and tank 2 holds 10. Water is pumped from tank 1 "
            "to tank 2 at 10 litres per minute and back from tank 2 to tank 1 "
            "at the same rate, so both volumes stay fixed and both tanks are "
            "kept well stirred. Let x(t) and y(t) be the grams of salt in each."
        ),
        Para(
            "Salt leaves tank 1 at the flow rate times its concentration, "
            "10 · x/20 = x/2 grams per minute, and arrives at 10 · y/10 = y. "
            "Tank 2 gains what tank 1 loses and loses what tank 1 gains."
        ),
        Display(r"x' = -\frac{1}{2}x + y, \qquad y' = \frac{1}{2}x - y", "8"),
        Worked(
            "Salt shared between two tanks",
            "Tank 1 starts with 30 grams of salt and tank 2 with none: solve "
            "system (8) with x(0) = 30, y(0) = 0.",
            (
                Step("Add the equations. The total s = x + y has s' = 0, as it "
                     "must in a closed loop: salt moves but is never lost. So "
                     "x + y = 30 for all time.",
                     r"(x + y)' = 0 \;\Longrightarrow\; x + y = 30"),
                Step("Look for another combination αx + βy whose derivative is a "
                     "multiple μ of itself. Its derivative is "
                     "(−α/2 + β/2)x + (α − β)y, so −α/2 + β/2 = μα and "
                     "α − β = μβ. The choice μ = 0 gives α = β, the total "
                     "again; μ = −3/2 gives β = −2α, so take u = x − 2y."),
                Step("Check it: u' = x' − 2y' = (−x/2 + y) − 2(x/2 − y) = "
                     "−(3/2)x + 3y = −(3/2)u, so u satisfies the growth "
                     "equation on its own, with u(0) = 30.",
                     r"u' = -\frac{3}{2}u \;\Longrightarrow\; x - 2y = 30e^{-3t/2}"),
                Step("Two linear equations for x and y. Subtracting the second "
                     "from the first gives 3y = 30 − 30e^(−3t/2).",
                     r"y = 10 - 10e^{-3t/2}, \qquad x = 20 + 10e^{-3t/2}"),
            ),
            equation="x' = -x/2 + y; y' = x/2 - y",
            conditions="x(0) = 30, y(0) = 0",
            answer="x = 20 + 10*exp(-3*t/2)\ny = 10 - 10*exp(-3*t/2)",
            answer_latex=r"x = 20 + 10e^{-3t/2}, \quad y = 10 - 10e^{-3t/2}",
        ),
        Para(
            "In the long run x → 20 and y → 10, so both tanks reach the same "
            "concentration, one gram per litre — which is what stirring and "
            "exchange ought to do. The approach is exponential with rate 3/2 "
            "per minute; tank 1 is within a gram of its final amount after "
            "(2/3) ln 10 ≈ 1.54 minutes."
        ),
        Plot(
            "Salt evening out",
            "The salt in each tank. Tank 1 loses exactly what tank 2 gains, so "
            "the two curves are mirror images about the level 15, and both "
            "settle at one gram per litre: 20 grams in the larger tank, 10 in "
            "the smaller.",
            (Curve("20 + 10*exp(-3*t/2)", "x (tank 1)"),
             Curve("10 - 10*exp(-3*t/2)", "y (tank 2)")),
            t=(0.0, 5.0), ylim=(0.0, 31.0), ylabel="grams",
        ),
        Para(
            "The trick was to find two combinations of the unknowns, x + y and "
            "x − 2y, each of which obeys an uncoupled equation — the first with "
            "rate 0 and the second with rate −3/2. Those two rates are the "
            "eigenvalues of the matrix, whose rows are (−1/2, 1) and (1/2, −1): "
            "its trace is −3/2 and its determinant 0, so λ² + (3/2)λ = 0. "
            "Decoupling a system by a change of variables is exactly what the "
            "eigenvalue method does in general, and the next chapter shows how "
            "to find the right combinations without guessing."
        ),
    )),
    Section("Why solvers only take systems", (
        Para(
            "The conversion also pays off numerically. Every numerical "
            "method in the course was written for a first-order equation "
            "y' = f(t, y), and every one of them works unchanged when y is a "
            "vector and f a vector function. Euler's method, for instance, "
            "steps the whole state at once."
        ),
        Display(r"\mathbf{x}_{k+1} = \mathbf{x}_k + h\,\mathbf{F}(t_k, "
                r"\mathbf{x}_k)", "9"),
        Para(
            "For system (2) from (1, 0) with h = 0.1, the velocity at the start "
            "is (1 + 0, 3 + 0) = (1, 3), so one step lands at (1.1, 0.3). The "
            "exact solution found above has x(0.1) ≈ 1.140 and y(0.1) ≈ 0.352. "
            "The step undershoots both, as Euler's method does whenever the "
            "solution curves upwards, here like e^(4t); nothing about the "
            "error is new just because the state is a vector."
        ),
        Para(
            "So converting is how a fourth-order equation is handed to software "
            "that has never heard of fourth-order equations. Almost every "
            "general-purpose solver, this application's included, integrates "
            "first-order systems; when this one is asked for a pendulum or a "
            "pair of coupled springs, the conversion of this chapter is what "
            "happens first."
        ),
        Display(r"y^{(n)} = f\left(t, y, \ldots, y^{(n-1)}\right) "
                r"\;\Longrightarrow\; \mathbf{x}' = \mathbf{F}(t, \mathbf{x})", "10"),
    )),
    Section("Common errors", (
        Para(
            "The first is a sign slip in the conversion. From y'' + 5y' + 6y = 0 "
            "the second row is x₂' = −6x₁ − 5x₂: moving the terms across the "
            "equals sign changes both signs. The second is decoupling by "
            "mistake, writing x₁' = −5x₁, x₂' = −6x₂; the whole point of the "
            "conversion is that y'' depends on both y and y', and the first row "
            "x₁' = x₂ must always be there."
        ),
        Para(
            "The third is miscounting constants: solving each unknown's "
            "eliminated equation separately and keeping four constants in a "
            "two-by-two system, or counting the nine entries of a 3 × 3 matrix "
            "rather than its three rows. The fourth is putting the columns of A "
            "in a different order from the unknowns. The rows of A follow the "
            "equations and the columns follow the unknowns, in the same order "
            "as in the vector x; swap one and not the other and the matrix "
            "describes a different system."
        ),
    )),
    Section("Summary", (
        Para(
            "A first-order system gives each unknown's derivative in terms of "
            "time and all the unknowns. When each unknown's derivative involves "
            "the other unknowns the system is coupled, and neither equation can "
            "be solved first; if the dependence runs only one way, the "
            "independent equation can be solved first and substituted into the "
            "other. A linear system with constant coefficients is one equation "
            "x' = Ax between vectors, the matrix analogue of y' = ky, and "
            "elimination shows that its governing numbers are the roots of "
            "λ² − (tr A)λ + det A, the eigenvalues of A. Every nth-order "
            "equation becomes an n-component system by naming its derivatives "
            "as unknowns, with the companion matrix whose eigenvalues are the "
            "characteristic roots; the resulting state is exactly what n "
            "initial conditions specify. Superposition holds, and a system of "
            "n equations has n arbitrary constants. The next chapter finds the "
            "solutions to combine: fixed directions multiplied by exponentials, "
            "which is to say eigenvectors and eigenvalues."
        ),
    )),
)


DISTINCT = (
    Section("A matrix that turns vectors", (
        Para(
            "The previous chapter wrote every linear system with constant "
            "coefficients as a single equation, x' = Ax, where x is the column "
            "of unknowns and A is the square array of coefficients. Written "
            "that way it looks exactly like the first equation of the course, "
            "y' = ky, whose solution y = Ce^(kt) everybody knows. It is tempting "
            "to write down e^(At) and stop. The temptation is not wrong — the "
            "forced-systems chapter makes sense of it — but it hides the "
            "real difficulty, and nothing can be computed from it yet."
        ),
        Para(
            "The difficulty is that a matrix does two things to a vector where "
            "a number does one. Multiplying by k stretches a vector, or shrinks "
            "or reverses it, but leaves it on the same line. Multiplying by A "
            "usually turns it as well. So the velocity x' of a solution points "
            "somewhere other than x itself, the solution curves as it moves, "
            "and there is no single exponential rate to attach to it. For the "
            "system x' = x + 2y, y' = 3x + 2y, the vector (1, 0) is sent to "
            "(1, 3), which points in a quite different direction."
        ),
        Para(
            "But for most matrices a few directions are special: vectors along "
            "them come back from A unturned, stretched by some factor but "
            "still on their own line. Along such a direction the matrix really "
            "is just a number, and the vector equation collapses to the scalar "
            "one. This chapter finds those directions, shows that when there "
            "are enough of them they give every solution, and reads the "
            "behaviour of the system off the numbers that go with them. It "
            "treats the case in which those numbers, the eigenvalues, are real "
            "and different; the next two chapters deal with complex and "
            "repeated ones."
        ),
    )),
    Section("Solutions that keep their direction", (
        Para(
            "Look for a solution that never changes direction: a fixed, "
            "non-zero vector v whose length is scaled by a function of time. "
            "The guess is not arbitrary. It is the one shape of solution for "
            "which multiplying by A could possibly behave like multiplying by "
            "a number, because it is the one shape in which only a single "
            "direction is ever involved."
        ),
        Display(r"\mathbf{x}(t) = f(t)\,\mathbf{v}, \qquad \mathbf{v} \neq "
                r"\mathbf{0} \text{ fixed}", "1"),
        Para(
            "Substitute it into x' = Ax. Differentiation touches only the "
            "scalar factor, and the matrix touches only the vector, so the two "
            "sides separate cleanly."
        ),
        Display(r"f'(t)\,\mathbf{v} = f(t)\,A\mathbf{v}", "2"),
        Para(
            "At any instant where f is not zero this says that Av is a multiple "
            "of v, namely f'/f times it. The left side points along v, so the "
            "right side must too. Since v and A are constant, the multiple "
            "cannot depend on time either: call it λ. Then f' = λf, the "
            "simplest equation in the course, whose solution is an "
            "exponential. The differential equation has turned into two "
            "separate facts, one of pure algebra and one already solved."
        ),
        Display(r"A\mathbf{v} = \lambda\mathbf{v}, \qquad f' = \lambda f "
                r"\;\Longrightarrow\; \mathbf{x}(t) = e^{\lambda t}\,\mathbf{v}",
                "3"),
        Box(
            "theorem", "Straight-line solutions",
            "If Av = λv for a non-zero vector v and a number λ, then "
            "x(t) = e^(λt) v solves x' = Ax. Conversely, every solution of the "
            "form f(t)v with f not identically zero arises this way. Such a "
            "solution stays on the line through the origin in the direction "
            "of v for all time, moving outwards if λ > 0, inwards if λ < 0, "
            "and not at all if λ = 0.",
            r"A\mathbf{v} = \lambda\mathbf{v} \;\Longrightarrow\; "
            r"\left(e^{\lambda t}\mathbf{v}\right)' = \lambda e^{\lambda t}"
            r"\mathbf{v} = A\left(e^{\lambda t}\mathbf{v}\right)",
        ),
        Box(
            "proof", "Proof",
            "The displayed line is the first half: differentiate, then use "
            "Av = λv to replace λv by Av. The second half is the derivation "
            "just given, which divided by f only at an instant where f ≠ 0. "
            "Once f' = λf is known, f = Ce^(λt), and since e^(λt) is never "
            "zero, a straight-line solution that starts off the origin can "
            "never reach it in finite time.",
        ),
        Para(
            "Notice what the substitution achieved. Nothing differential is "
            "left in the condition Av = λv. Finding the straight-line solutions "
            "of a differential equation has become a question in linear "
            "algebra, and the answer to it is standard."
        ),
    )),
    Section("Eigenvalues and eigenvectors", (
        Box(
            "definition", "Eigenvalue and eigenvector, recalled",
            "As the previous chapter defined it, a number λ is an eigenvalue "
            "of the square matrix A if there is a "
            "non-zero vector v with Av = λv. Any such v is an eigenvector for "
            "λ. The zero vector is excluded, since A0 = λ0 for every λ and "
            "would make every number an eigenvalue.",
            r"A\mathbf{v} = \lambda\mathbf{v}, \qquad \mathbf{v} \neq \mathbf{0}",
        ),
        Para(
            "Rewrite the condition as (A − λI)v = 0, where I is the identity "
            "matrix. A square matrix sends some non-zero vector to zero exactly "
            "when it is singular, that is, when its determinant vanishes. So "
            "the eigenvalues are the roots of a polynomial, the characteristic "
            "polynomial of A, and they are found before any eigenvector is."
        ),
        Display(r"(A - \lambda I)\mathbf{v} = \mathbf{0},\ \mathbf{v} \neq "
                r"\mathbf{0} \;\Longleftrightarrow\; \det(A - \lambda I) = 0",
                "4"),
        Para(
            "For the two-by-two system x' = ax + by, y' = cx + dy, subtract λ "
            "down the diagonal and take the determinant: (a − λ)(d − λ) − bc. "
            "Multiplied out, the coefficient of λ is minus the trace "
            "τ = tr A = a + d, the sum of the diagonal, and the constant term "
            "is the determinant Δ = det A = ad − bc. Both can be read straight "
            "off the matrix, which is the quickest check on the polynomial."
        ),
        Display(r"\lambda^{2} - \tau\lambda + \Delta = 0, \qquad "
                r"\tau = a + d, \quad \Delta = ad - bc", "5"),
        Para(
            "The previous chapter met this quadratic already, by elimination, "
            "as λ² − (tr A)λ + det A, and showed that for a converted "
            "second-order equation it is the old characteristic equation. Its "
            "roots satisfy λ₁ + λ₂ = τ and λ₁λ₂ = Δ, "
            "since those are the coefficients of (λ − λ₁)(λ − λ₂). This "
            "chapter assumes the discriminant τ² − 4Δ is positive, which is "
            "exactly the condition for two real, different eigenvalues."
        ),
        Para(
            "Once λ is known, (A − λI)v = 0 is a pair of linear equations for "
            "the two entries of v. Because the determinant is zero the two "
            "rows of A − λI are proportional, so the two equations say the "
            "same thing (or one of them is the empty statement 0 = 0), and "
            "one non-trivial row is all that is needed. Subtract λ from the "
            "diagonal, write the rows out with numbers, and solve."
        ),
        Worked(
            "Eigenvalues and eigenvectors of a saddle matrix",
            "Find the eigenvalues and eigenvectors of the coefficient matrix of "
            "x' = x + 2y, y' = 3x + 2y, whose rows are (1, 2) and (3, 2).",
            (
                Step("Read off the trace and determinant: τ = 1 + 2 = 3 and "
                     "Δ = 1·2 − 2·3 = −4. The characteristic equation factors.",
                     r"\lambda^{2} - 3\lambda - 4 = (\lambda - 4)(\lambda + 1) = 0"),
                Step("So λ₁ = −1 and λ₂ = 4. Check: their sum is 3 = τ and their "
                     "product is −4 = Δ."),
                Step("For λ₂ = 4, A − 4I has rows (−3, 2) and (3, −2). The "
                     "second row is −1 times the first, as the zero determinant "
                     "promised, so the system reduces to the single equation "
                     "−3v₁ + 2v₂ = 0. Take v₁ = 2; then v₂ = 3.",
                     r"-3v_1 + 2v_2 = 0 \;\Longrightarrow\; "
                     r"\mathbf{v}_2 = \binom{2}{3}"),
                Step("For λ₁ = −1, A + I has rows (2, 2) and (3, 3). Both say "
                     "v₁ + v₂ = 0, so take v₁ = 1 and v₂ = −1.",
                     r"v_1 + v_2 = 0 \;\Longrightarrow\; "
                     r"\mathbf{v}_1 = \binom{1}{-1}"),
                Step("Check by multiplying, not by trusting the algebra. A sends "
                     "(1, −1) to (1 − 2, 3 − 2) = (−1, 1), which is −1 times it, "
                     "and sends (2, 3) to (2 + 6, 6 + 6) = (8, 12), which is 4 "
                     "times it.",
                     r"A\mathbf{v}_1 = -\mathbf{v}_1, \qquad "
                     r"A\mathbf{v}_2 = 4\mathbf{v}_2"),
            ),
        ),
        Para(
            "The computation always has the same shape, so it can be done "
            "once in letters. The first row of A − λI reads "
            "(a − λ)v₁ + bv₂ = 0, and when b ≠ 0 it is solved by "
            "v = (b, λ − a); on the saddle matrix that gives (2, 3) for λ = 4 "
            "and (2, −2), a multiple of (1, −1), for λ = −1. When b = 0 use the "
            "second row, cv₁ + (d − λ)v₂ = 0, which gives v = (λ − d, c) "
            "whenever c ≠ 0. If b = c = 0 the matrix is diagonal, the system "
            "is uncoupled (x' = ax, y' = dy), and the eigenvectors are simply "
            "(1, 0) for a and (0, 1) for d. Formula 6 is a shortcut, not a "
            "replacement: for a 3 × 3 matrix, or whenever in doubt, go back to "
            "the rows."
        ),
        Display(r"\mathbf{v} = \binom{b}{\lambda - a} \;\; (b \neq 0), "
                r"\qquad \mathbf{v} = \binom{\lambda - d}{c} \;\; (c \neq 0)",
                "6"),
        Box(
            "remark", "Eigenvectors are determined only up to scale",
            "If v is an eigenvector for λ then so is kv for any non-zero k, "
            "since A(kv) = kAv = λ(kv). In the solution e^(λt)v the constant "
            "in front absorbs the choice, so there is no need to normalise "
            "these vectors by hand: pick the multiple with the smallest "
            "integers. Software usually returns unit vectors, which are just "
            "as correct. Two correct answers can therefore look different, "
            "and an answer that differs from the book's only by the scaling "
            "of an eigenvector is not wrong.",
        ),
    )),
    Section("The general solution", (
        Para(
            "Each eigenvalue with its eigenvector gives one straight-line "
            "solution. The system is linear, so any combination of solutions "
            "is again a solution, and the question is whether two of them are "
            "enough to reach every starting point. They are, provided the "
            "eigenvectors point in genuinely different directions — and when "
            "the eigenvalues are different, they always do."
        ),
        Box(
            "theorem", "Distinct eigenvalues give independent eigenvectors",
            "If λ₁ ≠ λ₂ are eigenvalues of A with eigenvectors v₁ and v₂, then "
            "v₁ and v₂ are linearly independent. Consequently, for a 2×2 matrix "
            "with two distinct real eigenvalues every solution of x' = Ax is "
            "given by the formula below, for some constants c₁ and c₂.",
            r"\mathbf{x}(t) = c_1 e^{\lambda_1 t}\mathbf{v}_1 + "
            r"c_2 e^{\lambda_2 t}\mathbf{v}_2",
        ),
        Box(
            "proof", "Proof",
            "Suppose c₁v₁ + c₂v₂ = 0. Apply A to get c₁λ₁v₁ + c₂λ₂v₂ = 0, and "
            "subtract λ₂ times the first equation. The v₂ terms cancel, leaving "
            "c₁(λ₁ − λ₂)v₁ = 0. Neither λ₁ − λ₂ nor v₁ is zero, so c₁ = 0, and "
            "then c₂v₂ = 0 forces c₂ = 0. Independence means that v₁ and v₂ "
            "span the plane, so any initial vector x(0) can be written as "
            "c₁v₁ + c₂v₂; the combination above then has the right value at "
            "t = 0, and by uniqueness it is the solution through that point.",
        ),
        Para(
            "The count matches the rest of the course: two unknown functions, "
            "two constants, two initial conditions. Fitting the conditions "
            "means solving c₁v₁ + c₂v₂ = x(0), a pair of linear equations whose "
            "coefficient matrix V has the eigenvectors as its columns. That "
            "matrix is invertible precisely because the eigenvectors are "
            "independent."
        ),
        Para(
            "Independence can also be phrased with the Wronskian of the two "
            "solutions, the determinant of the matrix whose columns are the "
            "solution vectors. For straight-line solutions it is the constant "
            "det V times e^((λ₁ + λ₂)t), which is never zero. Since λ₁ + λ₂ = τ, "
            "this is the system form of Abel's formula from Unit 3, which the "
            "previous chapter quoted: the "
            "Wronskian grows or decays like e^(τt). The forced-systems chapter "
            "proves it for any fundamental matrix under the name "
            "Liouville's formula."
        ),
        Display(r"W(t) = \det V\; e^{(\lambda_1 + \lambda_2)t} = "
                r"\det V\; e^{\tau t} \neq 0", "7"),
    )),
    Section("A saddle", (
        Worked(
            "The general solution",
            "Solve x' = x + 2y, y' = 3x + 2y.",
            (
                Step("The eigenpairs were found above: λ₁ = −1 with (1, −1), and "
                     "λ₂ = 4 with (2, 3)."),
                Step("Combine the two straight-line solutions with one constant "
                     "each.",
                     r"\mathbf{x} = c_1 e^{-t}\binom{1}{-1} + "
                     r"c_2 e^{4t}\binom{2}{3}"),
                Step("Read off the components. This is the family the "
                     "previous chapter reached by elimination, with the "
                     "constants renamed, found now without eliminating "
                     "anything.",
                     r"x = c_1 e^{-t} + 2c_2 e^{4t}, \qquad "
                     r"y = -c_1 e^{-t} + 3c_2 e^{4t}"),
            ),
            equation="x' = x + 2*y; y' = 3*x + 2*y",
            answer="x = C1*exp(-t) + 2*C2*exp(4*t)\ny = -C1*exp(-t) + 3*C2*exp(4*t)",
            answer_latex=r"x = c_1 e^{-t} + 2c_2 e^{4t}, \quad "
                         r"y = -c_1 e^{-t} + 3c_2 e^{4t}",
        ),
        Worked(
            "Fitting initial values",
            "Solve the same system with x(0) = 3, y(0) = 2.",
            (
                Step("At t = 0 the exponentials are 1, so the conditions ask for "
                     "c₁v₁ + c₂v₂ = (3, 2).",
                     r"c_1 + 2c_2 = 3, \qquad -c_1 + 3c_2 = 2"),
                Step("Add the equations: 5c₂ = 5, so c₂ = 1, and then c₁ = 1. The "
                     "5 is det V, the Wronskian at t = 0, as formula 7 says. "
                     "The previous chapter found W = −5e^(3t) for the same "
                     "pair of solutions with the first eigenvector scaled as "
                     "(−1, 1) instead of (1, −1); rescaling a column only "
                     "rescales W."),
                Step("Substitute the constants.",
                     r"x = e^{-t} + 2e^{4t}, \qquad y = -e^{-t} + 3e^{4t}"),
            ),
            equation="x' = x + 2*y; y' = 3*x + 2*y",
            conditions="x(0) = 3, y(0) = 2",
            answer="x = exp(-t) + 2*exp(4*t)\ny = -exp(-t) + 3*exp(4*t)",
            answer_latex=r"x = e^{-t} + 2e^{4t}, \quad y = -e^{-t} + 3e^{4t}",
        ),
        Para(
            "Now read the answer geometrically, which is what a system offers "
            "that a single equation does not. The eigenvalues have opposite "
            "signs, and that alone settles the picture. On the line through "
            "(1, −1) the solution is c₁e^(−t)(1, −1), which slides into the "
            "origin; on the line through (2, 3) it is c₂e^(4t)(2, 3), which runs "
            "away. These are the only straight-line trajectories there are."
        ),
        Para(
            "Every other solution has both constants non-zero. For large "
            "negative t the e^(−t) term dominates, so the trajectory arrives "
            "from far out along the stable line; for large positive t the "
            "e^(4t) term dominates and it leaves along the unstable line. In "
            "between it passes the origin without reaching it. The solution "
            "just found shows how quickly the growing term takes over: at "
            "t = 1 it is at about (109.6, 163.4), with y/x ≈ 1.49, already very "
            "nearly the slope 3/2 of the unstable eigenvector. Such an "
            "equilibrium, "
            "which attracts only the points of a single line and repels "
            "everything else, is a *saddle*. A saddle is unstable: starting "
            "points arbitrarily close to the origin, but off the stable line, "
            "are carried away along the unstable one."
        ),
        Plot(
            "The saddle x' = x + 2y, y' = 3x + 2y",
            "Trajectories in the (x, y) plane for 0 ≤ t ≤ 1.75. The two "
            "straight lines are the eigendirections: along (1, −1) solutions "
            "fall into the origin, along (2, 3) they escape. Each curved "
            "trajectory starts near the stable line, is carried towards the "
            "origin, and is turned away along the unstable one.",
            (Curve("3 - 5*t", "stable line, v₁ = (1, −1)", y="5*t - 3"),
             Curve("5*t - 3", "unstable line, v₂ = (2, 3)", y="7.5*t - 4.5"),
             Curve("3*exp(-t) + 0.002*exp(4*t)", "c₁ = 3, c₂ = 0.001",
                   y="-3*exp(-t) + 0.003*exp(4*t)"),
             Curve("3*exp(-t) - 0.002*exp(4*t)", "c₁ = 3, c₂ = −0.001",
                   y="-3*exp(-t) - 0.003*exp(4*t)"),
             Curve("-3*exp(-t) + 0.002*exp(4*t)", "c₁ = −3, c₂ = 0.001",
                   y="3*exp(-t) + 0.003*exp(4*t)"),
             Curve("-3*exp(-t) - 0.002*exp(4*t)", "c₁ = −3, c₂ = −0.001",
                   y="3*exp(-t) - 0.003*exp(4*t)")),
            t=(0.0, 1.75), xlabel="x", ylabel="y", ylim=(-4.5, 4.5),
        ),
    )),
    Section("A stable node", (
        Para(
            "Change the signs and the same algebra draws a completely "
            "different picture. The system x' = −2x + y, y' = x − 2y has "
            "matrix rows (−2, 1) and (1, −2), trace τ = −4 and determinant "
            "Δ = 3, so its characteristic equation is λ² + 4λ + 3 = 0."
        ),
        Worked(
            "Both eigenvalues negative",
            "Solve x' = −2x + y, y' = x − 2y with x(0) = 3, y(0) = 1.",
            (
                Step("Factor the characteristic equation.",
                     r"\lambda^{2} + 4\lambda + 3 = (\lambda + 1)(\lambda + 3) = 0"),
                Step("For λ₁ = −1, formula 6 gives (1, 1); for λ₂ = −3 it gives "
                     "(1, −1). Check: A sends (1, 1) to (−1, −1) and (1, −1) to "
                     "(−3, 3).",
                     r"\mathbf{v}_1 = \binom{1}{1}, \qquad "
                     r"\mathbf{v}_2 = \binom{1}{-1}"),
                Step("Fit the conditions: c₁ + c₂ = 3 and c₁ − c₂ = 1, so c₁ = 2 "
                     "and c₂ = 1.",
                     r"\mathbf{x} = 2e^{-t}\binom{1}{1} + e^{-3t}\binom{1}{-1}"),
            ),
            equation="x' = -2*x + y; y' = x - 2*y",
            conditions="x(0) = 3, y(0) = 1",
            answer="x = 2*exp(-t) + exp(-3*t)\ny = 2*exp(-t) - exp(-3*t)",
            answer_latex=r"x = 2e^{-t} + e^{-3t}, \quad y = 2e^{-t} - e^{-3t}",
        ),
        Para(
            "The matrix is symmetric, and its eigenvectors (1, 1) and (1, −1) "
            "are perpendicular. That is a general fact about symmetric "
            "matrices, and a convenient one, but it is not typical: the "
            "eigenvectors of the saddle matrix, (1, −1) and (2, 3), are not "
            "perpendicular, and nothing in the method needs them to be."
        ),
        Para(
            "Both eigenvalues are negative, so both straight-line solutions "
            "decay and every trajectory ends at the origin. Such an "
            "equilibrium is a *stable node*. The formula hides one further "
            "detail, which is which of the two terms dominates. The term with "
            "the more negative eigenvalue dies first. In the solution just "
            "found the ratio of the fast term to the slow one is "
            "e^(−3t)/(2e^(−t)) = e^(−2t)/2, which is about 0.068 at t = 1 and "
            "0.0092 at t = 2. After a short while what is left is almost "
            "entirely the slow mode, so the trajectory runs into the origin "
            "along the direction (1, 1)."
        ),
        Para(
            "That is true of every trajectory except those on the fast line "
            "itself: whatever direction a solution sets out in, it arrives "
            "tangent to the *slower* eigendirection. The phase-portraits "
            "chapter builds its sketches on exactly this observation."
        ),
        Plot(
            "The stable node x' = −2x + y, y' = x − 2y",
            "Trajectories for 0 ≤ t ≤ 4, with the two eigendirections. Every "
            "curve ends at the origin, and every one not on the line through "
            "(1, −1) comes in tangent to the slow line through (1, 1), because "
            "the e^(−3t) part of the motion is spent first. The four curves "
            "that start on the axes begin 45° away from the slow line, yet "
            "have visibly bent onto it well before they arrive. The curve starting "
            "at (3, 1) is the worked example.",
            (Curve("1.5*t - 3", "slow line, λ = −1", y="1.5*t - 3"),
             Curve("1.5*t - 3", "fast line, λ = −3", y="3 - 1.5*t"),
             Curve("2*exp(-t) + exp(-3*t)", "from (3, 1)",
                   y="2*exp(-t) - exp(-3*t)"),
             Curve("1.5*exp(-t) - 1.5*exp(-3*t)", "from (0, 3)",
                   y="1.5*exp(-t) + 1.5*exp(-3*t)"),
             Curve("1.5*exp(-t) + 1.5*exp(-3*t)", "from (3, 0)",
                   y="1.5*exp(-t) - 1.5*exp(-3*t)"),
             Curve("-1.5*exp(-t) + 1.5*exp(-3*t)", "from (0, −3)",
                   y="-1.5*exp(-t) - 1.5*exp(-3*t)"),
             Curve("-1.5*exp(-t) - 1.5*exp(-3*t)", "from (−3, 0)",
                   y="-1.5*exp(-t) + 1.5*exp(-3*t)")),
            t=(0.0, 4.0), xlabel="x", ylabel="y", ylim=(-3.5, 3.5),
        ),
    )),
    Section("The eigenvalues decide what is left", (
        Para(
            "The two examples suggest the general rule. In the solution "
            "c₁e^(λ₁t)v₁ + c₂e^(λ₂t)v₂ the eigenvectors fix which directions "
            "are preserved, and the eigenvalues fix what happens along each. "
            "As t grows the term with the larger eigenvalue wins, provided its "
            "constant is not zero, because e^(λ₂t)/e^(λ₁t) = e^((λ₂ − λ₁)t) "
            "grows without bound when λ₂ > λ₁. (A solution with that constant "
            "zero lies on the other eigenline and never sees the larger "
            "eigenvalue at all; the stable line of a saddle is the example.) "
            "With both eigenvalues negative the origin is a stable node; with "
            "both positive every trajectory except the equilibrium itself "
            "leaves it, an unstable node; with opposite signs it is a saddle. A zero eigenvalue, "
            "treated below, gives a whole line of equilibria."
        ),
        Figure("eigen_modes",
               "The sliders set λ₁ and λ₂, the eigenvalues along the fixed "
               "directions (1, 1) and (1, −1), and c₁ and c₂, the weights of "
               "the two modes; the curves show the first component x against "
               "t. Start with λ₁ = −0.5 and λ₂ = −1.5, both negative: both "
               "dashed modes decay, and by t = 4 the slower one is about 98% "
               "of the answer. Then drag λ₁ above zero to make a saddle and "
               "watch that mode take over completely, and finally set c₁ = 0 "
               "to see that a solution started exactly on the other "
               "eigendirection never picks up the growing mode at all."),
        Para(
            "Two eigenvalues of the same sign do not have to be negative, and "
            "the method does not care. The next example is an unstable node."
        ),
        Worked(
            "An unstable node",
            "Solve x' = 4x + y, y' = 2x + 3y with x(0) = 0, y(0) = 3.",
            (
                Step("Here τ = 7 and Δ = 12 − 2 = 10.",
                     r"\lambda^{2} - 7\lambda + 10 = (\lambda - 2)(\lambda - 5) = 0"),
                Step("Formula 6 with b = 1 gives (1, λ − 4): (1, −2) for λ = 2 and "
                     "(1, 1) for λ = 5. Check: A sends (1, −2) to (2, −4) and "
                     "(1, 1) to (5, 5).",
                     r"\mathbf{v}_1 = \binom{1}{-2}, \qquad "
                     r"\mathbf{v}_2 = \binom{1}{1}"),
                Step("Fit the conditions: c₁ + c₂ = 0 and −2c₁ + c₂ = 3, so "
                     "c₁ = −1 and c₂ = 1.",
                     r"\mathbf{x} = -e^{2t}\binom{1}{-2} + e^{5t}\binom{1}{1}"),
            ),
            equation="x' = 4*x + y; y' = 2*x + 3*y",
            conditions="x(0) = 0, y(0) = 3",
            answer="x = -exp(2*t) + exp(5*t)\ny = 2*exp(2*t) + exp(5*t)",
            answer_latex=r"x = e^{5t} - e^{2t}, \quad y = e^{5t} + 2e^{2t}",
        ),
        Para(
            "Both terms grow, so the solution leaves every neighbourhood of "
            "the origin, and it does so along (1, 1), the direction of the "
            "faster eigenvalue 5. Run backwards in time the picture is a "
            "stable node, and the roles reverse: as t → −∞ it is the slower "
            "mode, e^(2t), that survives, so trajectories emerge from the "
            "origin tangent to (1, −2)."
        ),
    )),
    Section("A zero eigenvalue: the two tanks again", (
        Para(
            "The previous chapter solved a closed exchange between two tanks, "
            "20 litres and 10 litres, with 10 litres per minute pumped each "
            "way, x and y the grams of salt in each. It got there by a trick: "
            "it guessed two combinations of the unknowns that obey uncoupled "
            "equations, and promised that this chapter would show how to find "
            "them without guessing. Here is its system again, now solved by "
            "the eigenvalue method."
        ),
        Display(r"x' = -\frac{1}{2}x + y, \qquad y' = \frac{1}{2}x - y", "8"),
        Worked(
            "Salt shared between two tanks, by eigenvalues",
            "Tank 1 starts with 30 grams of salt and tank 2 with none. Solve "
            "x' = −x/2 + y, y' = x/2 − y with x(0) = 30, y(0) = 0.",
            (
                Step("The trace is −1/2 − 1 = −3/2 and the determinant is "
                     "1/2 − 1/2 = 0.",
                     r"\lambda^{2} + \frac{3}{2}\lambda = "
                     r"\lambda\left(\lambda + \frac{3}{2}\right) = 0"),
                Step("For λ₁ = 0, A itself has rows (−1/2, 1) and (1/2, −1), "
                     "both saying v₁ = 2v₂, so v₁ = (2, 1). For λ₂ = −3/2, "
                     "A + (3/2)I has rows (1, 1) and (1/2, 1/2), both saying "
                     "v₁ + v₂ = 0, so v₂ = (1, −1).",
                     r"\mathbf{v}_1 = \binom{2}{1}, \qquad "
                     r"\mathbf{v}_2 = \binom{1}{-1}"),
                Step("Fit the conditions: 2c₁ + c₂ = 30 and c₁ − c₂ = 0, so "
                     "c₁ = c₂ = 10.",
                     r"\mathbf{x} = 10\binom{2}{1} + 10e^{-3t/2}\binom{1}{-1}"),
            ),
            equation="x' = -x/2 + y; y' = x/2 - y",
            conditions="x(0) = 30, y(0) = 0",
            answer="x = 20 + 10*exp(-3*t/2)\ny = 10 - 10*exp(-3*t/2)",
            answer_latex=r"x = 20 + 10e^{-3t/2}, \quad y = 10 - 10e^{-3t/2}",
        ),
        Para(
            "This is the answer the previous chapter found, and now the "
            "guessed combinations can be seen for what they are. Any state "
            "can be written as x = c₁v₁ + c₂v₂, and the coordinates are "
            "c = V⁻¹x, where V has the eigenvectors (2, 1) and (1, −1) as its "
            "columns. Its inverse has rows (1/3)(1, 1) and (1/3)(1, −2), so "
            "c₁ = (x + y)/3 and c₂ = (x − 2y)/3. Those are, up to the factor "
            "1/3, exactly the combinations x + y and x − 2y that the previous "
            "chapter guessed. Along the solution c₁ stays at 10 and c₂ is "
            "10e^(−3t/2): each coordinate obeys an uncoupled equation, the "
            "first with rate 0 and the second with rate −3/2, the two "
            "eigenvalues. Decoupling by eigenvectors is what the trick was."
        ),
        Para(
            "A zero eigenvalue means Av = 0 for its eigenvector, so every "
            "multiple of (2, 1) is an equilibrium: there is a whole line of "
            "them rather than a single point. Physically these are the states "
            "in which both tanks have the same concentration, since 2 grams in "
            "20 litres and 1 gram in 10 litres are the same. The other mode "
            "decays with time constant 2/3 minute, a half-life of about 0.46 "
            "minutes, and carries the system to the equilibrium (20, 10), one "
            "gram per litre in each tank."
        ),
        Para(
            "The conservation law x + y = 30, which the previous chapter found "
            "by adding the equations, is the zero eigenvalue seen from the "
            "other side: x + y is 3c₁, the coordinate whose rate is 0. A closed system that loses nothing always has a zero "
            "eigenvalue for this reason, and the point on the line of "
            "equilibria at which it settles is fixed by the conserved total."
        ),
    )),
    Section("Second-order equations, seen again", (
        Para(
            "The previous chapter showed that converting u'' + pu' + qu = 0 "
            "into a system, with x₁ = u and x₂ = u', gives a matrix with rows "
            "(0, 1) and (−q, −p) whose characteristic polynomial is the old "
            "λ² + pλ + q, so the eigenvalues are the roots r of Unit 3. The "
            "new fact is the eigenvector. Formula 6, with b = 1, gives (1, λ), "
            "which is just the statement that for u = e^(λt) the second "
            "component u' is λ times the first."
        ),
        Worked(
            "A converted equation",
            "Solve x' = y, y' = 6x + y with x(0) = 2, y(0) = 1. This is "
            "u'' − u' − 6u = 0 written as a system with x = u and y = u'.",
            (
                Step("Here τ = 1 and Δ = −6, giving the familiar characteristic "
                     "equation.",
                     r"\lambda^{2} - \lambda - 6 = (\lambda - 3)(\lambda + 2) = 0"),
                Step("The eigenvectors are (1, λ): (1, 3) for λ = 3 and (1, −2) "
                     "for λ = −2.",
                     r"\mathbf{v}_1 = \binom{1}{3}, \qquad "
                     r"\mathbf{v}_2 = \binom{1}{-2}"),
                Step("Fit: c₁ + c₂ = 2 and 3c₁ − 2c₂ = 1, so c₁ = c₂ = 1. The "
                     "second component is the derivative of the first, as it "
                     "must be, and the scalar answer is u = e^(3t) + e^(−2t).",
                     r"x = e^{3t} + e^{-2t}, \qquad y = 3e^{3t} - 2e^{-2t}"),
            ),
            equation="x' = y; y' = 6*x + y",
            conditions="x(0) = 2, y(0) = 1",
            answer="x = exp(3*t) + exp(-2*t)\ny = 3*exp(3*t) - 2*exp(-2*t)",
            answer_latex=r"x = e^{3t} + e^{-2t}, \quad y = 3e^{3t} - 2e^{-2t}",
        ),
        Para(
            "The two routes agree, as they must, and each explains something "
            "about the other. The overdamped case of Unit 4, two negative real "
            "roots, is a stable node in the plane of position and velocity; an "
            "equation with roots of opposite signs, like this one, is a "
            "saddle. Since determinant −6 is negative, that could have been "
            "said before any root was found."
        ),
    )),
    Section("Three unknowns", (
        Para(
            "Nothing in the derivation of straight-line solutions used the "
            "size of the matrix. For an n × n matrix with n distinct real "
            "eigenvalues the independence proof, repeated one eigenvalue at a "
            "time (apply A − λI to a vanishing combination to remove one "
            "eigenvector, and argue by induction on the number left), gives n "
            "independent eigenvectors and a general solution with n constants. "
            "What changes is the work. The characteristic polynomial is a "
            "cubic for a 3 × 3 matrix, found by expanding a determinant, and "
            "each eigenvector comes from three equations of which only two "
            "are independent. There is no shortcut formula; the rows do the "
            "job."
        ),
        Worked(
            "A three-by-three system",
            "Solve x' = x + y, y' = x + 2y + z, z' = y + z with x(0) = 4, "
            "y(0) = 1, z(0) = 0. The matrix has rows (1, 1, 0), (1, 2, 1) and "
            "(0, 1, 1).",
            (
                Step("Expand det(A − λI) along the first row. The second term "
                     "is −1·(1 − λ), so (1 − λ) comes out of both terms, and "
                     "what is left, (2 − λ)(1 − λ) − 2, is λ² − 3λ.",
                     r"\det(A - \lambda I) = (1 - \lambda)\left[(2 - \lambda)"
                     r"(1 - \lambda) - 2\right] = -\lambda(\lambda - 1)"
                     r"(\lambda - 3)"),
                Step("So the eigenvalues are 0, 1 and 3, all distinct. Check: "
                     "they add to 4, the trace 1 + 2 + 1, and their product "
                     "0 is det A."),
                Step("For λ = 3, A − 3I has rows (−2, 1, 0), (1, −1, 1) and "
                     "(0, 1, −2). The first row says v₂ = 2v₁ and the third "
                     "says v₂ = 2v₃. Take v₁ = 1: then v₂ = 2 and v₃ = 1. The "
                     "middle row, v₁ − v₂ + v₃ = 1 − 2 + 1 = 0, holds "
                     "automatically; that is the dependence the zero "
                     "determinant promised.",
                     r"\lambda = 3:\ \mathbf{v}_3 = (1, 2, 1)"),
                Step("The same way, for λ = 1 the rows of A − I are (0, 1, 0), "
                     "(1, 1, 1) and (0, 1, 0), which force v₂ = 0 and "
                     "v₁ + v₃ = 0; for λ = 0 the rows of A give v₂ = −v₁ and "
                     "v₃ = −v₂. Check each by multiplying by A.",
                     r"\lambda = 0:\ (1, {-1}, 1), \qquad "
                     r"\lambda = 1:\ (1, 0, {-1})"),
                Step("Fit c₁(1, −1, 1) + c₂(1, 0, −1) + c₃(1, 2, 1) = (4, 1, 0). "
                     "Subtracting the third component from the first gives "
                     "2c₂ = 4; adding them gives c₁ + c₃ = 2; the second "
                     "component, −c₁ + 2c₃ = 1, then gives c₃ = 1 and c₁ = 1.",
                     r"c_1 = 1, \quad c_2 = 2, \quad c_3 = 1"),
                Step("Assemble the components.",
                     r"x = 1 + 2e^{t} + e^{3t}, \quad y = -1 + 2e^{3t}, \quad "
                     r"z = 1 - 2e^{t} + e^{3t}"),
            ),
            equation="x' = x + y; y' = x + 2*y + z; z' = y + z",
            conditions="x(0) = 4, y(0) = 1, z(0) = 0",
            answer="x = 1 + 2*exp(t) + exp(3*t)\ny = -1 + 2*exp(3*t)\n"
                   "z = 1 - 2*exp(t) + exp(3*t)",
            answer_latex=r"x = 1 + 2e^{t} + e^{3t}, \;\; y = -1 + 2e^{3t}, "
                         r"\;\; z = 1 - 2e^{t} + e^{3t}",
        ),
        Para(
            "The eigenvalue 0 contributes the constant vector (1, −1, 1), an "
            "equilibrium, and the two positive eigenvalues make every other "
            "part of the solution grow; after a short time the e^(3t) term, "
            "along (1, 2, 1), dominates all three components."
        ),
    )),
    Section("Three tanks in a row", (
        Para(
            "Finding the roots of a cubic is usually the hard step, but one "
            "class of matrices gives its eigenvalues away: for a triangular "
            "matrix, det(A − λI) is the product of the diagonal entries minus "
            "λ, so the eigenvalues are the diagonal."
        ),
        Para(
            "Such matrices arise from cascades. Fresh water runs at 6 litres "
            "per minute into a 6-litre tank, which drains into a 12-litre tank, "
            "which drains into an 18-litre tank, which drains away. Each tank "
            "loses salt at rate 6/V times its content and receives what the "
            "previous one loses, so the rate constants are 1, 1/2 and 1/3, and "
            "no tank feeds anything upstream."
        ),
        Worked(
            "A cascade of three tanks",
            "Solve x' = −x, y' = x − y/2, z' = y/2 − z/3 with x(0) = 6, "
            "y(0) = 0, z(0) = 0: 6 kg of salt in the first tank and none "
            "downstream.",
            (
                Step("The matrix is lower triangular, so the eigenvalues are "
                     "−1, −1/2 and −1/3, all distinct."),
                Step("Solve (A − λI)v = 0 from the top down, since each row "
                     "involves only its own entry of v and those before it. "
                     "For −1/3 the first two "
                     "rows force v₁ = v₂ = 0, giving (0, 0, 1). For −1/2 the first "
                     "row forces v₁ = 0 and the third gives (0, 1, −3). For −1 "
                     "choose v₁ = 2; the second row gives v₂ = −4, the third "
                     "v₃ = 3.",
                     r"\lambda = -1:\ (2, {-4}, 3), \quad \lambda = -\frac{1}{2}:"
                     r"\ (0, 1, {-3}), \quad \lambda = -\frac{1}{3}:\ (0, 0, 1)"),
                Step("Fit x(0): 2c₁ = 6 gives c₁ = 3, then −12 + c₂ = 0 gives "
                     "c₂ = 12, then 9 − 36 + c₃ = 0 gives c₃ = 27."),
                Step("Assemble the components.",
                     r"x = 6e^{-t}, \quad y = 12e^{-t/2} - 12e^{-t}, \quad "
                     r"z = 9e^{-t} - 36e^{-t/2} + 27e^{-t/3}"),
            ),
            equation="x' = -x; y' = x - y/2; z' = y/2 - z/3",
            conditions="x(0) = 6, y(0) = 0, z(0) = 0",
            answer="x = 6*exp(-t)\ny = 12*exp(-t/2) - 12*exp(-t)\n"
                   "z = 9*exp(-t) - 36*exp(-t/2) + 27*exp(-t/3)",
            answer_latex=r"x = 6e^{-t}, \;\; y = 12e^{-t/2} - 12e^{-t}, \;\; "
                         r"z = 9e^{-t} - 36e^{-t/2} + 27e^{-t/3}",
        ),
        Para(
            "The middle tank's salt rises and falls. Setting y' = 0 gives "
            "e^(−t/2) = 1/2, so y peaks at t = 2 ln 2 ≈ 1.39 minutes with exactly "
            "3 kg; the last tank peaks later, at t ≈ 3.66 minutes with "
            "about 2.43 kg. In the long run the slowest mode, e^(−t/3), "
            "carries everything that is left, and it lives entirely in the "
            "last tank, the one that drains most slowly."
        ),
        Plot(
            "Salt moving down the cascade",
            "The salt in the three tanks, in kilograms against minutes. Each "
            "tank's curve is a sum of the eigenmodes it can see: the first "
            "tank sees only e^(−t), the last tank all three.",
            (Curve("6*exp(-t)", "x, first tank"),
             Curve("12*exp(-t/2) - 12*exp(-t)", "y, second tank"),
             Curve("9*exp(-t) - 36*exp(-t/2) + 27*exp(-t/3)", "z, third tank")),
            t=(0.0, 15.0), ylabel="salt (kg)", xlabel="t (minutes)",
            ylim=(0.0, 6.5),
        ),
    )),
    Section("Where the method stops", (
        Box(
            "warning", "Linear, and constant coefficients",
            "The eigenvalue method solves x' = Ax for a constant matrix A and "
            "nothing else. If the entries of A depend on t, a solution e^(λt)v "
            "with a fixed v does not exist in general and there is no "
            "eigenvalue shortcut. A nonlinear system can only be linearised "
            "about an equilibrium; the eigenvalues of the linearisation then "
            "describe it near that point and say nothing far from it. That is "
            "the subject of the next unit, on nonlinear systems.",
            r"\mathbf{x}' = A\mathbf{x}, \quad A \text{ constant}",
        ),
        Para(
            "Within its scope the method has two further cases, which the "
            "next two chapters treat. If τ² − 4Δ < 0 the eigenvalues are a "
            "complex pair, the eigenvectors are complex, and a real answer "
            "has to be recovered from a complex one; the trajectories then "
            "rotate. If τ² − 4Δ = 0 there is one repeated eigenvalue, and "
            "usually only one eigendirection, so the theorem above no longer "
            "supplies two independent solutions and a second one must be "
            "built differently. Forcing terms, x' = Ax + f(t), come in the "
            "forced-systems chapter."
        ),
    )),
    Section("Common errors", (
        Para(
            "The first is an arithmetic slip in the characteristic "
            "polynomial, usually a sign on the λ term. The check costs "
            "nothing: the coefficient of λ is minus the trace, the constant "
            "is the determinant, and the eigenvalues must add to τ and "
            "multiply to Δ. The second is an eigenvector that is not one. "
            "Multiply it by A and see whether it comes back as a multiple of "
            "itself; if it does not, the eigenvalue or the vector is wrong. "
            "Solving the whole system (A − λI)v = 0 and getting only v = 0 is "
            "the same warning: a correct eigenvalue always makes the rows "
            "dependent. (A single row that reads 0 = 0, or a shortcut formula "
            "that returns the zero vector, is a different matter; use the "
            "other row, as formula 6 says.)"
        ),
        Para(
            "The third is attaching each eigenvector to the wrong exponential. "
            "The vector found from λ₁ goes with e^(λ₁t) and no other, and "
            "swapping them produces a pair of functions that in general "
            "satisfies neither equation. The fourth is fitting the constants "
            "to one component only, for instance choosing c₁ and c₂ to make "
            "x(0) right and forgetting y. The conditions are one vector "
            "equation, c₁v₁ + c₂v₂ = x(0), and both components must hold. "
            "Compare answers by substituting, not by looking."
        ),
    )),
    Section("Summary", (
        Para(
            "Guessing a solution that keeps its direction, x = e^(λt)v, turns "
            "x' = Ax into the eigenvalue problem Av = λv. The eigenvalues are "
            "the roots of det(A − λI) = 0, which for a 2×2 matrix is "
            "λ² − τλ + Δ = 0 with τ the trace and Δ the determinant; an "
            "eigenvector for each, determined only up to scale, is found from "
            "one row of (A − λI)v = 0 and checked by multiplying. Distinct "
            "eigenvalues give independent eigenvectors, so the general "
            "solution is c₁e^(λ₁t)v₁ + c₂e^(λ₂t)v₂, and the conditions fix the "
            "constants through one linear system. Geometrically the "
            "eigendirections are the only straight-line trajectories, and the "
            "signs of the eigenvalues name the origin: both negative a stable "
            "node, both positive an unstable node, opposite signs a saddle, "
            "and a zero eigenvalue a line of equilibria. Unless a solution "
            "starts exactly on the other eigenline, the larger eigenvalue owns "
            "the end of the story."
        ),
    )),
)


COMPLEX = (
    Section("A real matrix with no real directions", (
        Para(
            "The previous chapter solved x' = Ax by looking for solutions that "
            "keep a fixed direction, x = e^(λt)v, and found that such a solution "
            "exists exactly when Av = λv. For a two-by-two matrix the eigenvalues "
            "are the roots of a quadratic, and the method went through smoothly "
            "because both roots were real and different. Nothing guarantees that. "
            "A matrix with entirely real entries can have a characteristic "
            "polynomial with no real roots at all."
        ),
        Para(
            "The simplest example is x' = −y, y' = x. Its matrix A has rows "
            "(0, −1) and (1, 0), and det(A − λI) = λ² + 1, which is positive for "
            "every real λ. There is no real eigenvalue, and so no real "
            "eigenvector and no straight-line solution."
        ),
        Para(
            "That is not a failure of the method; it is the algebra describing "
            "the picture correctly. At the point (x, y) this system moves with "
            "velocity (−y, x), which is at right angles to the position vector. "
            "Every point is pushed sideways, round the origin, and no line "
            "through the origin is carried into itself. A real eigenvector would "
            "be such a line. A system whose solutions circle the origin cannot "
            "have one, and the missing real roots are how the characteristic "
            "polynomial says so."
        ),
        Para(
            "The complex roots still produce solutions, by exactly the "
            "computation of the previous chapter. The only difficulty is that a "
            "real system with real initial data has a real answer, so the "
            "complex exponentials must be converted back into real functions. "
            "The conversion is the one Unit 3 used for complex characteristic "
            "roots, and Unit 4 for the underdamped oscillator: Euler's formula, "
            "now applied to a vector as well as to a scalar. That last clause is where nearly all the mistakes in this "
            "topic are made."
        ),
    )),
    Section("Complex roots come in conjugate pairs", (
        Para(
            "For a two-by-two matrix the characteristic polynomial is "
            "λ² − τλ + Δ, where τ = tr A is the sum of the diagonal entries and "
            "Δ = det A. The phase-portraits chapter will make much of these two "
            "numbers; for now only the quadratic formula is needed. The roots are "
            "non-real exactly when τ² − 4Δ < 0, and then they are"
        ),
        Display(r"\lambda = \alpha \pm i\beta, \qquad \alpha = \frac{\tau}{2}, "
                r"\qquad \beta = \frac{1}{2}\sqrt{4\Delta - \tau^{2}}", "1"),
        Para(
            "The real part α is half the trace; the imaginary part β is taken "
            "positive by convention. The pairing is not special to two "
            "dimensions. For a real matrix of any size, det(A − λI) is a "
            "polynomial p(λ) with real coefficients, and conjugating the "
            "equation p(λ) = 0 gives p(λ̄) = 0. So non-real eigenvalues always "
            "come in conjugate pairs. The eigenvectors pair up in the same way "
            "as the eigenvalues, which is what saves half the work."
        ),
        Box(
            "theorem", "Conjugate eigenpairs",
            "Let A be a real matrix. If v is an eigenvector of A with eigenvalue "
            "λ, then its complex conjugate v̄, obtained by conjugating each "
            "entry, is an eigenvector with eigenvalue λ̄.",
            r"A\mathbf{v} = \lambda\mathbf{v} \;\Longrightarrow\; "
            r"A\overline{\mathbf{v}} = \overline{\lambda}\,\overline{\mathbf{v}}",
        ),
        Box(
            "proof", "Proof",
            "Conjugate both sides of Av = λv. The conjugate of a product is the "
            "product of the conjugates, and conjugating A changes nothing because "
            "its entries are real.",
            r"\overline{A\mathbf{v}} = \overline{A}\,\overline{\mathbf{v}} = "
            r"A\overline{\mathbf{v}}, \qquad \overline{\lambda\mathbf{v}} = "
            r"\overline{\lambda}\,\overline{\mathbf{v}}",
        ),
        Para(
            "Finding an eigenvector for α + iβ is the same computation as "
            "before, done in complex arithmetic. Because A − λI is singular, its "
            "two rows are proportional, so a single row determines v. To keep "
            "the letters a and b free for the eigenvector later on, write the "
            "entries of A as a₁₁, a₁₂ in the first row and a₂₁, a₂₂ in the "
            "second. The second row of A − λI then reads "
            "a₂₁v₁ + (a₂₂ − λ)v₂ = 0, and v = (λ − a₂₂, a₂₁) is an eigenvector; "
            "a₂₁ cannot be zero when the eigenvalues are non-real, as the "
            "section on direction of rotation shows. The proportionality of the "
            "rows is by a *complex* factor, which is hard to see by eye, so it "
            "is worth checking once by multiplying out, as the second worked "
            "example below does. A final check that Av = λv catches any slip in "
            "the complex arithmetic."
        ),
    )),
    Section("One complex solution carries two real ones", (
        Para(
            "With λ = α + iβ and its eigenvector v, the function v e^(λt) solves "
            "x' = Ax. The derivation in the previous chapter never used the fact "
            "that λ was real: the derivative of e^(λt) is λe^(λt) for complex λ "
            "too. But the solution is complex, and the answer to a real problem "
            "must be real. The resolution is a short theorem."
        ),
        Box(
            "theorem", "Real and imaginary parts are solutions",
            "Let A be real. If x(t) = p(t) + i q(t), with p and q real vector "
            "functions, is a solution of x' = Ax, then p and q are each real "
            "solutions of x' = Ax.",
            r"\mathbf{x} = \mathbf{p} + i\mathbf{q} \;\Longrightarrow\; "
            r"\mathbf{p}' = A\mathbf{p}, \quad \mathbf{q}' = A\mathbf{q}",
        ),
        Box(
            "proof", "Proof",
            "Substitute. Since A is real, Ap and Aq are real vectors, so the two "
            "sides are each split into a real part and an imaginary part. Two "
            "complex vectors are equal only if their real parts agree and their "
            "imaginary parts agree.",
            r"\mathbf{p}' + i\mathbf{q}' = A\mathbf{p} + iA\mathbf{q}",
        ),
        Para(
            "To compute p and q, write the eigenvector in real and imaginary "
            "parts, v = a + ib, with a and b real vectors, and expand the "
            "exponential by Euler's formula. There are then two complex factors "
            "to multiply out, not one."
        ),
        Display(r"\mathbf{v}e^{\lambda t} = \left(\mathbf{a} + i\mathbf{b}\right)"
                r"e^{\alpha t}\left(\cos\beta t + i\sin\beta t\right)", "2"),
        Para(
            "The real part collects a cos βt from the product of the two real "
            "terms and −b sin βt from the product of the two imaginary ones, "
            "since i·i = −1. The imaginary part collects the two cross terms."
        ),
        Display(r"\mathbf{p}(t) = e^{\alpha t}\left(\mathbf{a}\cos\beta t - "
                r"\mathbf{b}\sin\beta t\right)", "3"),
        Display(r"\mathbf{q}(t) = e^{\alpha t}\left(\mathbf{a}\sin\beta t + "
                r"\mathbf{b}\cos\beta t\right)", "4"),
        Box(
            "warning", "Euler's formula applies to the vector too",
            "The eigenvector is complex, so its imaginary part b feeds into the "
            "real solution p. Taking the real part of the scalar factor alone "
            "and leaving the vector untouched, to get a e^(αt) cos βt, is the "
            "classic error. That function is not a solution, because a on its "
            "own is not an eigenvector.",
        ),
        Para(
            "The conjugate eigenvalue gives nothing new. Its solution is the "
            "complex conjugate of the first, with real part p and imaginary part "
            "−q. "
            "The two real solutions it would yield are the ones already in hand, "
            "up to a sign, which is why only one member of the pair is ever "
            "worked through."
        ),
    )),
    Section("The simplest case: a pure rotation", (
        Worked(
            "Circles",
            "Find the general solution of x' = −y, y' = x.",
            (
                Step("The characteristic polynomial has roots ±i, so α = 0 and "
                     "β = 1.",
                     r"\det(A - \lambda I) = \lambda^{2} + 1 = 0 "
                     r"\;\Longrightarrow\; \lambda = \pm i"),
                Step("Take λ = i. The first row of A − iI is (−i, −1), so "
                     "−i v₁ − v₂ = 0, and v₁ = 1 gives v₂ = −i. Split it into "
                     "real and imaginary parts.",
                     r"\mathbf{v} = \binom{1}{-i} = \binom{1}{0} + "
                     r"i\binom{0}{-1}"),
                Step("With α = 0 and β = 1, formulas (3) and (4) give the two "
                     "real solutions.",
                     r"\mathbf{p} = (\cos t,\ \sin t), \qquad "
                     r"\mathbf{q} = (\sin t,\ -\cos t)"),
                Step("The general solution is c₁p + c₂q, written out "
                     "component by component (the answer below spells the "
                     "constants C₁, C₂)."),
            ),
            equation="x' = -y; y' = x",
            answer="x = C1*cos(t) + C2*sin(t)\ny = C1*sin(t) - C2*cos(t)",
            answer_latex=r"x = C_1\cos t + C_2\sin t, \quad "
                         r"y = C_1\sin t - C_2\cos t",
        ),
        Para(
            "Every solution satisfies x² + y² = C₁² + C₂², so the trajectories "
            "are circles about the origin, traced at unit angular speed. The "
            "same fact follows without solving anything: along a solution, "
            "(x² + y²)' = 2x(−y) + 2y(x) = 0. Starting at (1, 0) gives "
            "C₁ = 1, C₂ = 0 and the solution (cos t, sin t), the unit circle "
            "traced anticlockwise; the velocity at (1, 0) is (0, 1), straight "
            "up, which confirms the direction. Every later example in this "
            "chapter is this one with the circle deformed and an exponential "
            "envelope wrapped round it."
        ),
    )),
    Section("Euler's formula applied to the whole product", (
        Para(
            "In the rotation the eigenvector was simple enough that the pitfall "
            "of the warning box could not bite. The next example has an "
            "eigenvector whose real and imaginary parts both matter, and it is "
            "worth doing slowly."
        ),
        Worked(
            "A spiral with a genuinely complex eigenvector",
            "Solve x' = x − 5y, y' = x − 3y with x(0) = 1, y(0) = 1.",
            (
                Step("A has rows (1, −5) and (1, −3), so τ = −2 and Δ = −3 + 5 = 2. "
                     "The discriminant τ² − 4Δ = −4 is negative.",
                     r"\lambda^{2} + 2\lambda + 2 = 0 \;\Longrightarrow\; "
                     r"\lambda = -1 \pm i"),
                Step("Take λ = −1 + i. Then A − λI has rows (2 − i, −5) and "
                     "(1, −2 − i). The first row is (2 − i) times the second, "
                     "since (2 − i)(−2 − i) = −5, so the second row alone is "
                     "enough: v₁ = (2 + i)v₂, and v₂ = 1 gives v.",
                     r"\mathbf{v} = \binom{2+i}{1} = \binom{2}{1} + "
                     r"i\binom{1}{0}"),
                Step("Check: Av = (2 + i − 5, 2 + i − 3) = (−3 + i, −1 + i), "
                     "and (−1 + i)(2 + i) = −3 + i, so Av = (−1 + i)v as it "
                     "should.",
                     r"A\mathbf{v} = (-3 + i,\ -1 + i) = (-1 + i)\,\mathbf{v}"),
                Step("So a = (2, 1) and b = (1, 0), with α = −1 and β = 1. "
                     "Formulas (3) and (4) give the real solutions. Notice that "
                     "b contributes the −sin t to the first component of p.",
                     r"\mathbf{p} = e^{-t}(2\cos t - \sin t,\ \cos t), \quad "
                     r"\mathbf{q} = e^{-t}(2\sin t + \cos t,\ \sin t)"),
                Step("At t = 0, p(0) = a and q(0) = b. The initial condition asks "
                     "for c₁(2, 1) + c₂(1, 0) = (1, 1), so c₁ = 1 and c₂ = −1.",
                     r"\mathbf{x} = \mathbf{p} - \mathbf{q}"),
            ),
            equation="x' = x - 5*y; y' = x - 3*y",
            conditions="x(0) = 1, y(0) = 1",
            answer="x = exp(-t)*(cos(t) - 3*sin(t))\ny = exp(-t)*(cos(t) - sin(t))",
            answer_latex=r"x = e^{-t}(\cos t - 3\sin t), \quad "
                         r"y = e^{-t}(\cos t - \sin t)",
        ),
        Para(
            "Now watch the pitfall produce a wrong answer. Someone who applies "
            "Euler's formula to the exponential alone takes the real part to be "
            "e^(−t) cos t times "
            "(2, 1), that is x = 2e^(−t) cos t, y = e^(−t) cos t. Substituting, "
            "x' − x + 5y comes to e^(−t)(cos t − 2 sin t) and y' − x + 3y to "
            "−e^(−t) sin t. Neither is zero, and the checker in this application "
            "rejects the pair. The missing ingredient is exactly the b terms."
        ),
        Plot(
            "Both components against time",
            "The solution of the example over one period. Each component is "
            "e^(−t) times an oscillation of period 2π: x = e^(−t)(cos t − 3 sin t) "
            "has amplitude √10 ≈ 3.16 times e^(−t), and y = e^(−t)(cos t − sin t) "
            "has amplitude √2 times it. The decay is so fast that the "
            "oscillation has almost died out after one swing. The two "
            "components are out of phase, and that phase difference is what "
            "makes the trajectory go round.",
            (Curve("exp(-t)*(cos(t) - 3*sin(t))", "x(t)"),
             Curve("exp(-t)*(cos(t) - sin(t))", "y(t)")),
            t=(0.0, 6.2832), ylim=(-0.8, 1.05),
        ),
        Plot(
            "The same solution in the plane",
            "The trajectory from (1, 1), spiralling anticlockwise into the "
            "origin. Each full turn takes 2π and multiplies the solution vector "
            "by e^(−2π) ≈ 0.0019, which is why only one turn is drawn: a second "
            "would be invisible.",
            (Curve("exp(-t)*(cos(t) - 3*sin(t))", "trajectory",
                   y="exp(-t)*(cos(t) - sin(t))"),),
            t=(0.0, 6.2832), xlabel="x", ylabel="y",
        ),
    )),
    Section("Why two real solutions are enough", (
        Para(
            "p and q are solutions, but the general solution needs two "
            "*independent* ones. They could conceivably be multiples of each "
            "other. They never are."
        ),
        Box(
            "theorem", "The real solutions form a fundamental set",
            "Let A be a real two-by-two matrix with eigenvalue α + iβ, β ≠ 0, and "
            "eigenvector v = a + ib. Then a and b are linearly independent, so p "
            "and q are independent solutions, and every real solution of x' = Ax "
            "is c₁p + c₂q for real constants c₁, c₂.",
            r"\mathbf{x}(t) = e^{\alpha t}\left[c_1\left(\mathbf{a}\cos\beta t "
            r"- \mathbf{b}\sin\beta t\right) + c_2\left(\mathbf{a}\sin\beta t "
            r"+ \mathbf{b}\cos\beta t\right)\right]",
        ),
        Box(
            "proof", "Proof",
            "Suppose instead that b = ka for a real number k (the case a = kb is "
            "the same). Then v = (1 + ik)a is a complex multiple of the real "
            "vector a, so a is itself an eigenvector: Aa = λa. The left side is "
            "real, while the right side has imaginary part βa, which is not zero "
            "since β ≠ 0 and a ≠ 0. That is a contradiction. So a and b are "
            "independent, and since p(0) = a and q(0) = b, the Wronskian of p and "
            "q is non-zero at t = 0.",
        ),
        Para(
            "Fitting an initial condition is therefore always the same small "
            "linear system: c₁a + c₂b = x(0), as in the example above. It also "
            "explains why two correct answers from two books can look different. "
            "Any non-zero complex multiple of v is also an eigenvector, and "
            "different choices give different pairs p, q. Multiplying v by −i, "
            "for instance, turns p into q and q into −p. The pairs always span "
            "the same solutions, and the answer to an initial value problem is "
            "the same whichever pair is used."
        ),
    )),
    Section("Rotation and scaling", (
        Para(
            "The cleanest matrices with eigenvalues α ± iβ are those of the "
            "system x' = αx − βy, y' = βx + αy. In polar coordinates, "
            "x = r cos θ and y = r sin θ, it separates completely."
        ),
        Box(
            "theorem", "Polar form of a spiral",
            "Along any solution of x' = αx − βy, y' = βx + αy other than the "
            "zero solution, the radius and angle satisfy r' = αr and θ' = β. So "
            "the radius grows or decays exponentially and the angle increases "
            "at a constant rate.",
            r"r(t) = r_0 e^{\alpha t}, \qquad \theta(t) = \theta_0 + \beta t",
        ),
        Box(
            "proof", "Proof",
            "Differentiate r² = x² + y² to get rr' = xx' + yy'. For the angle, "
            "differentiating tan θ = y/x gives sec²θ·θ' = (xy' − yx')/x², and "
            "sec²θ = r²/x², so r²θ' = xy' − yx'. Substitute "
            "the system into each: the cross terms cancel in the first and the "
            "diagonal terms in the second.",
            r"rr' = \alpha\left(x^{2} + y^{2}\right), \qquad "
            r"r^{2}\theta' = \beta\left(x^{2} + y^{2}\right)",
        ),
        Para(
            "Here the two parts of the eigenvalue are visibly doing different "
            "jobs. The imaginary part β is an angular velocity, the same at every "
            "point, so one turn takes 2π/β whatever the starting point. The real "
            "part α is a growth rate for the radius, so a full turn multiplies "
            "the radius by e^(2πα/β). Whether the spiral runs in or out depends "
            "on the sign of α alone; β only sets how tightly it winds."
        ),
        Worked(
            "A spiral read off in polar form",
            "Solve x' = 2x − 3y, y' = 3x + 2y with x(0) = 0, y(0) = 1.",
            (
                Step("This is the rotation-scaling form with α = 2 and β = 3, so "
                     "the eigenvalues are 2 ± 3i. The start (0, 1) is on the "
                     "positive y-axis, so r₀ = 1 and θ₀ = π/2.",
                     r"r(t) = e^{2t}, \qquad \theta(t) = \frac{\pi}{2} + 3t"),
                Step("Convert back with x = r cos θ, y = r sin θ, using "
                     "cos(π/2 + 3t) = −sin 3t and sin(π/2 + 3t) = cos 3t.",
                     r"x = -e^{2t}\sin 3t, \qquad y = e^{2t}\cos 3t"),
                Step("Cross-check with the eigenvector method. For λ = 2 + 3i "
                     "the second row of A − λI is (3, −3i), so v₁ = i v₂, "
                     "giving v = (i, 1), a = (0, 1) and b = (1, 0). The start "
                     "(0, 1) is a, so c₁ = 1, c₂ = 0, and the answer is "
                     "p = e^(2t)(a cos 3t − b sin 3t), the same as above."),
            ),
            equation="x' = 2*x - 3*y; y' = 3*x + 2*y",
            conditions="x(0) = 0, y(0) = 1",
            answer="x = -exp(2*t)*sin(3*t)\ny = exp(2*t)*cos(3*t)",
            answer_latex=r"x = -e^{2t}\sin 3t, \quad y = e^{2t}\cos 3t",
        ),
        Para(
            "One turn takes 2π/3 ≈ 2.09 time units and multiplies the radius by "
            "e^(4π/3) ≈ 65.9, so this spiral runs outwards fast. "
            "Rotation-scaling systems are more typical than they "
            "look. From Av = λv with v = a + ib, comparing real and imaginary "
            "parts gives Aa = αa − βb and Ab = βa + αb. So in coordinates "
            "measured along b and a, instead of along the axes, every real "
            "two-by-two matrix with eigenvalues α ± iβ acts exactly as this one "
            "does. For the matrix of the previous section, whose rows are (1, −5) "
            "and (1, −3), the change to those coordinates turns it into the "
            "matrix with rows (−1, −1) and (1, −1), the rotation-scaling matrix "
            "with α = −1 and β = 1. Back in the original coordinates the circles "
            "are stretched into ellipses, the spiral is distorted, and the sense "
            "of rotation may be reversed; but the period 2π/β and the factor by "
            "which each revolution scales the solution are unchanged."
        ),
        Figure("spiral",
               "Start with α negative and move the α slider slowly up through "
               "zero: every trajectory changes together from an inward spiral "
               "to closed circles to an outward spiral. Then hold α fixed and "
               "move β between 0.3 and 3. The spirals wind more or less tightly "
               "(at the bottom of the range less than one turn fits in the "
               "window), but none of them changes from inward to outward. The readout "
               "gives the time for one turn, 2π/β."),
    )),
    Section("In or out, and which way round", (
        Box(
            "definition", "Spiral points and centres",
            "Suppose the eigenvalues of the real two-by-two matrix A are α ± iβ "
            "with β ≠ 0. The origin is a stable spiral point of x' = Ax if α < 0: "
            "every trajectory winds round it infinitely often and tends to it. It "
            "is an unstable spiral point if α > 0: every trajectory other than "
            "the origin winds outwards without bound. It is a centre if α = 0: "
            "every trajectory is a closed curve round the origin, and the "
            "solutions are periodic with period 2π/β.",
            r"\alpha < 0 \text{ stable spiral}, \quad \alpha = 0 \text{ centre}, "
            r"\quad \alpha > 0 \text{ unstable spiral}",
        ),
        Para(
            "Since α = τ/2, the trace alone decides which, once the discriminant "
            "has shown the eigenvalues to be complex. The general solution also "
            "makes the per-turn behaviour exact for any matrix, not just "
            "rotation-scaling ones: p and q are e^(αt) times functions of period "
            "T = 2π/β, so every solution satisfies x(t + T) = e^(αT) x(t). After "
            "each full period the solution vector is the same vector scaled by "
            "e^(αT)."
        ),
        Para(
            "The direction of rotation is not in the eigenvalues at all, since "
            "β is positive by convention, but it is easy to read from the matrix."
        ),
        Box(
            "theorem", "Direction of rotation",
            "Let A have rows (a₁₁, a₁₂) and (a₂₁, a₂₂) and non-real "
            "eigenvalues. Then a₂₁ ≠ 0, and every trajectory of x' = Ax turns "
            "anticlockwise about the origin if a₂₁ > 0 and clockwise if "
            "a₂₁ < 0.",
            r"r^{2}\theta' = xy' - yx' = a_{21}x^{2} + (a_{22} - a_{11})xy "
            r"- a_{12}y^{2}",
        ),
        Box(
            "proof", "Proof",
            "The identity r²θ' = xy' − yx' was derived in the proof of the "
            "polar form above. Substituting x' = a₁₁x + a₁₂y and "
            "y' = a₂₁x + a₂₂y gives the quadratic form on the right. Its "
            "discriminant is (a₂₂ − a₁₁)² + 4a₁₂a₂₁, which equals τ² − 4Δ and is "
            "negative. A quadratic form with negative discriminant vanishes only "
            "at the origin, so it keeps one sign everywhere else, and that sign "
            "is its value at (1, 0), namely a₂₁. In particular a₂₁ cannot be "
            "zero. So θ' has the sign of a₂₁ at every point.",
        ),
        Para(
            "In practice this is the first column of A read as a velocity: at "
            "the point (1, 0) the velocity is (a₁₁, a₂₁). If it has a positive "
            "second component the flow crosses the positive x-axis upwards, "
            "which is anticlockwise. The same argument shows that the "
            "off-diagonal entries a₁₂ and a₂₁ must have opposite signs whenever "
            "the eigenvalues are complex."
        ),
        Worked(
            "Reading a spiral from the matrix",
            "Without solving it, describe the trajectories of x' = 3x − 4y, "
            "y' = 5x − y.",
            (
                Step("τ = 3 − 1 = 2 and Δ = −3 + 20 = 17, so τ² − 4Δ = 4 − 68 = −64 "
                     "and the eigenvalues are complex.",
                     r"\lambda = \frac{2 \pm \sqrt{-64}}{2} = 1 \pm 4i"),
                Step("α = 1 > 0, so the origin is an unstable spiral point. The "
                     "entry a₂₁ = 5 is positive, so trajectories turn "
                     "anticlockwise."),
                Step("One period is T = 2π/4 = π/2 ≈ 1.57, and over each period "
                     "every solution vector is multiplied by e^(π/2) ≈ 4.81.",
                     r"\mathbf{x}\left(t + \frac{\pi}{2}\right) = "
                     r"e^{\pi/2}\,\mathbf{x}(t)"),
            ),
        ),
    )),
    Section("An irrational frequency", (
        Para(
            "Nothing requires β to be a whole number, and the method goes "
            "through unchanged when it is irrational. Only the arithmetic "
            "gets heavier."
        ),
        Worked(
            "A stable spiral with β = √7/2",
            "Solve x' = −x − 2y, y' = x with x(0) = 1, y(0) = 0.",
            (
                Step("A has rows (−1, −2) and (1, 0). Then τ = −1, Δ = 2 and "
                     "τ² − 4Δ = −7.",
                     r"\lambda^{2} + \lambda + 2 = 0 \;\Longrightarrow\; "
                     r"\lambda = -\frac{1}{2} \pm \frac{\sqrt{7}}{2}\,i"),
                Step("A stable spiral, anticlockwise since a₂₁ = 1. For "
                     "λ = −1/2 + i√7/2, the second row of A − λI is (1, −λ), so "
                     "v = (λ, 1); doubling it clears the fractions.",
                     r"\mathbf{v} = (-1 + i\sqrt{7},\ 2) = (-1,\ 2) + "
                     r"i(\sqrt{7},\ 0)"),
                Step("Here a = (−1, 2) and b = (√7, 0), with α = −1/2 and "
                     "β = √7/2. The initial condition c₁a + c₂b = (1, 0) gives "
                     "c₁ = 0 and c₂ = 1/√7, so the answer is q/√7, with q from "
                     "formula (4).",
                     r"\mathbf{q} = e^{-t/2}(\sqrt{7}\cos\beta t - "
                     r"\sin\beta t,\ 2\sin\beta t)"),
            ),
            equation="x' = -x - 2*y; y' = x",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = exp(-t/2)*(cos(sqrt(7)*t/2) - sin(sqrt(7)*t/2)/sqrt(7))\n"
                   "y = 2*exp(-t/2)*sin(sqrt(7)*t/2)/sqrt(7)",
            answer_latex=r"x = e^{-t/2}\left(\cos\frac{\sqrt{7}}{2}t - "
                         r"\frac{1}{\sqrt{7}}\sin\frac{\sqrt{7}}{2}t\right), \quad "
                         r"y = \frac{2}{\sqrt{7}}e^{-t/2}\sin\frac{\sqrt{7}}{2}t",
        ),
        Para(
            "One period is 4π/√7 ≈ 4.75, and each period shrinks the solution by "
            "e^(−2π/√7) ≈ 0.093. Now set the first component beside Unit 4. "
            "Differentiating x' = −x − 2y and using y' = x gives "
            "x'' + x' + 2x = 0, an underdamped oscillator whose characteristic "
            "roots are the same −1/2 ± i√7/2, with x(0) = 1 and x'(0) = −1. "
            "Its solution is the x found above: a decaying exponential times a "
            "combination of a cosine and a sine, with the decay rate 1/2 in "
            "the exponent and the frequency √7/2 inside the cosine and sine."
        ),
    )),
    Section("The underdamped spring, seen in the plane", (
        Para(
            "That coincidence is really an identity, and it runs the other way "
            "too. The first chapter of this unit turned a second-order equation into a "
            "system by naming the velocity as a second unknown. Doing so for an "
            "underdamped spring produces a complex pair, and the trajectory of the "
            "system is the spring's motion drawn in the plane of position and "
            "velocity."
        ),
        Worked(
            "The spring x'' + 2x' + 5x = 0",
            "Write x'' + 2x' + 5x = 0, x(0) = 1, x'(0) = 0 as a system with "
            "y = x', and solve it by the eigenvalue method.",
            (
                Step("The system is x' = y, y' = −5x − 2y, whose matrix has rows "
                     "(0, 1) and (−5, −2). Its characteristic polynomial is the "
                     "spring's characteristic polynomial, as it must be.",
                     r"\lambda^{2} + 2\lambda + 5 = 0 \;\Longrightarrow\; "
                     r"\lambda = -1 \pm 2i"),
                Step("For λ = −1 + 2i the first row of A − λI is (−λ, 1), so "
                     "v = (1, λ).",
                     r"\mathbf{v} = \binom{1}{-1 + 2i} = \binom{1}{-1} + "
                     r"i\binom{0}{2}"),
                Step("Formulas (3) and (4) with α = −1, β = 2.",
                     r"\mathbf{p} = e^{-t}(\cos 2t,\ -\cos 2t - 2\sin 2t)"),
                Step("The imaginary part gives the second real solution.",
                     r"\mathbf{q} =e^{-t}(\sin 2t,\ 2\cos 2t - \sin 2t)"),
                Step("c₁(1, −1) + c₂(0, 2) = (1, 0) gives c₁ = 1 and c₂ = 1/2. "
                     "Form p + q/2 and simplify."),
            ),
            equation="x' = y; y' = -5*x - 2*y",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = exp(-t)*(cos(2*t) + sin(2*t)/2)\ny = -5*exp(-t)*sin(2*t)/2",
            answer_latex=r"x = e^{-t}\left(\cos 2t + \frac{1}{2}\sin 2t\right), "
                         r"\quad y = -\frac{5}{2}e^{-t}\sin 2t",
        ),
        Para(
            "The first component is Unit 4's answer, and the second is its "
            "derivative, as the system's first equation insists. Here a₂₁ = −5, "
            "so the trajectory turns clockwise. That holds for every "
            "underdamped spring: the system for x'' + cx' + kx = 0 (k > 0) has "
            "matrix rows (0, 1) and (−k, −c), so a₂₁ = −k < 0, and when c² < 4k "
            "the eigenvalues are complex, so the rule applies. (An overdamped "
            "spring has the same sign of a₂₁ but real eigenvalues, and does not "
            "turn round the origin at all.) Physically, a positive "
            "displacement makes the spring pull back, which makes the velocity "
            "negative, and in the position-velocity plane that is a clockwise "
            "turn. The envelope of the motion is decay at rate 1, the real part; "
            "the frequency 2, the imaginary part, sets the period π of one "
            "turn. (In this plane the angle does not advance at a constant "
            "rate: 2 is its average over a turn.)"
        ),
        Plot(
            "The spring against time",
            "The displacement x(t) inside its envelope ±(√5/2)e^(−t), where "
            "√5/2 ≈ 1.12 is the amplitude of cos 2t + ½ sin 2t. This is the "
            "picture Unit 4 drew of an underdamped oscillator.",
            (Curve("exp(-t)*(cos(2*t) + sin(2*t)/2)", "x(t)"),
             Curve("sqrt(5)/2*exp(-t)", "envelope"),
             Curve("-sqrt(5)/2*exp(-t)", "")),
            t=(0.0, 5.0), ylim=(-1.2, 1.2),
        ),
        Plot(
            "The spring in the phase plane",
            "The same motion as the curve (x, x'), starting at (1, 0). It spirals "
            "clockwise into the origin, crossing the x-axis each time the mass "
            "comes momentarily to rest, and crossing the y-axis each time it "
            "passes its equilibrium position.",
            (Curve("exp(-t)*(cos(2*t) + sin(2*t)/2)", "trajectory",
                   y="-5*exp(-t)*sin(2*t)/2"),),
            t=(0.0, 5.0), xlabel="x", ylabel="y = x'",
        ),
    )),
    Section("Centres, and the ellipses they trace", (
        Para(
            "When α = 0 the envelope is gone. Both p and q are periodic with "
            "period 2π/β, so every solution returns to its starting point and "
            "every trajectory is a closed curve. For a pure rotation the curves "
            "are circles. In general each solution has the form "
            "u cos βt + w sin βt for two fixed real vectors u and w, which "
            "parametrises an ellipse."
        ),
        Worked(
            "An elliptical orbit",
            "Solve x' = x − 2y, y' = x − y with x(0) = 1, y(0) = 0.",
            (
                Step("τ = 0 and Δ = −1 + 2 = 1, so the eigenvalues are ±i, α = 0, "
                     "β = 1: a centre, anticlockwise since a₂₁ = 1.",
                     r"\lambda^{2} + 1 = 0 \;\Longrightarrow\; \lambda = \pm i"),
                Step("For λ = i the second row of A − iI is (1, −1 − i), so "
                     "v₁ = (1 + i)v₂.",
                     r"\mathbf{v} = \binom{1+i}{1} = \binom{1}{1} + i\binom{1}{0}"),
                Step("The start (1, 0) is b, so c₁ = 0, c₂ = 1, and the answer is "
                     "q = a sin t + b cos t.",
                     r"\mathbf{x} = \binom{1}{1}\sin t + \binom{1}{0}\cos t"),
            ),
            equation="x' = x - 2*y; y' = x - y",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = cos(t) + sin(t)\ny = sin(t)",
            answer_latex=r"x = \cos t + \sin t, \quad y = \sin t",
        ),
        Para(
            "The ellipse can be found without the solution, from a quantity "
            "that the motion conserves."
        ),
        Box(
            "theorem", "A conserved quantity at a centre",
            "For the trace-zero system x' = a₁₁x + a₁₂y, y' = a₂₁x − a₁₁y, the "
            "quadratic H = a₂₁x² − 2a₁₁xy − a₁₂y² is constant along every "
            "solution. If the determinant −a₁₁² − a₁₂a₂₁ is positive, so that "
            "the eigenvalues are ±iβ, then H is definite and its level curves "
            "are ellipses centred at the origin.",
            r"H(x, y) = a_{21}x^{2} - 2a_{11}xy - a_{12}y^{2}, \qquad "
            r"\frac{dH}{dt} = 0",
        ),
        Box(
            "proof", "Proof",
            "By the chain rule dH/dt = (∂H/∂x)x' + (∂H/∂y)y'. Expanding "
            "(2a₂₁x − 2a₁₁y)(a₁₁x + a₁₂y) + (−2a₁₁x − 2a₁₂y)(a₂₁x − a₁₁y), "
            "every term cancels against another. The discriminant of H is "
            "4a₁₁² + 4a₁₂a₂₁ = −4 det A, which is negative, so H does not change "
            "sign and its level sets are ellipses.",
        ),
        Para(
            "For the example, a₁₁ = 1, a₁₂ = −2 and a₂₁ = 1, so "
            "H = x² − 2xy + 2y². At "
            "the start H = 1, and indeed (cos t + sin t)² − 2(cos t + sin t) sin t "
            "+ 2 sin² t simplifies to 1. The orbit is the ellipse "
            "x² − 2xy + 2y² = 1, reaching x = ±√2 ≈ ±1.41 and y = ±1."
        ),
        Plot(
            "A centre",
            "The orbit of the example, x² − 2xy + 2y² = 1, traced anticlockwise "
            "once every 2π. Nothing decays and nothing grows: the solution comes "
            "back exactly to (1, 0).",
            (Curve("cos(t) + sin(t)", "orbit", y="sin(t)"),),
            t=(0.0, 6.2832), xlabel="x", ylabel="y",
        ),
        Para(
            "The undamped spring of Unit 4 is a centre, and any friction at all "
            "gives the trace a non-zero value and turns its closed orbits into "
            "spirals. The phase-portraits chapter explains why a centre is "
            "fragile in this way, and the next unit why that matters."
        ),
    )),
    Section("Beyond two dimensions", (
        Para(
            "Nothing in the theorems above needs two dimensions. For an n-by-n "
            "real matrix, each complex pair α ± iβ contributes two real "
            "solutions, the real and imaginary parts of v e^(λt) for one member "
            "of the pair, and each real eigenvalue contributes as in the previous "
            "chapter. A three-by-three real matrix always has at least one real "
            "eigenvalue, since its characteristic polynomial has odd degree and "
            "a real cubic must cross zero. When the other two are a complex "
            "pair, every solution is the sum of a solution in the plane spanned "
            "by a and b (a spiral, or an ellipse if α = 0) and an exponential "
            "motion along the real eigenvector, and the two parts grow or decay "
            "at their own rates. A solution that starts on the real eigenvector "
            "has no rotating part and stays on that line."
        ),
        Worked(
            "One real eigenvalue and a complex pair",
            "Find the general solution of x' = x, y' = 2x + y − 2z, "
            "z' = 3x + 2y + z, whose matrix A has rows (1, 0, 0), (2, 1, −2) and "
            "(3, 2, 1).",
            (
                Step("Expand det(A − λI) along the first row, which has only one "
                     "non-zero entry. The remaining two-by-two block has rows "
                     "(1 − λ, −2) and (2, 1 − λ), with determinant "
                     "(1 − λ)² + 4 = λ² − 2λ + 5.",
                     r"\det(A - \lambda I) = (1 - \lambda)(\lambda^{2} - "
                     r"2\lambda + 5) = 0 \;\Longrightarrow\; \lambda = 1, "
                     r"\ \lambda = 1 \pm 2i"),
                Step("For λ = 1, A − I has rows (0, 0, 0), (2, 0, −2) and "
                     "(3, 2, 0). The second row gives v₃ = v₁ and the third "
                     "gives v₂ = −3v₁/2; v₁ = 2 clears the fraction.",
                     r"\mathbf{v}_1 = (2,\ -3,\ 2)"),
                Step("For λ = 1 + 2i, the first row of A − λI is (−2i, 0, 0), "
                     "which forces v₁ = 0. The third row then reads "
                     "2v₂ − 2i v₃ = 0, so v₂ = i v₃, and v₃ = 1 gives "
                     "v = (0, i, 1). So a = (0, 0, 1) and b = (0, 1, 0). Check "
                     "the unused second row: 2·0 − 2i·i − 2·1 = 2 − 2 = 0.",
                     r"\mathbf{v} = (0,\ i,\ 1) = (0,\ 0,\ 1) + i(0,\ 1,\ 0)"),
                Step("Formulas (3) and (4) with α = 1, β = 2 give the two real "
                     "solutions from the complex pair.",
                     r"\mathbf{p} = e^{t}(0,\ -\sin 2t,\ \cos 2t), \quad "
                     r"\mathbf{q} = e^{t}(0,\ \cos 2t,\ \sin 2t)"),
                Step("Add the real solution v₁e^t from the real eigenvalue. The "
                     "general solution is c₁v₁e^t + c₂p + c₃q, written out "
                     "component by component with the constants spelt C₁, C₂, "
                     "C₃.",
                     r"\mathbf{x} = c_1 e^{t}(2,\ -3,\ 2) + c_2\mathbf{p} + "
                     r"c_3\mathbf{q}"),
            ),
            equation="x' = x; y' = 2*x + y - 2*z; z' = 3*x + 2*y + z",
            answer="x = 2*C1*exp(t)\n"
                   "y = exp(t)*(-3*C1 - C2*sin(2*t) + C3*cos(2*t))\n"
                   "z = exp(t)*(2*C1 + C2*cos(2*t) + C3*sin(2*t))",
            answer_latex=r"x = 2C_1e^{t}, \quad y = e^{t}(-3C_1 - C_2\sin 2t + "
                         r"C_3\cos 2t), \quad z = e^{t}(2C_1 + C_2\cos 2t + "
                         r"C_3\sin 2t)",
        ),
        Para(
            "Here every eigenvalue has real part 1, so every solution grows "
            "like e^t. The plane of a and b is the (y, z)-plane, and within it "
            "the motion turns with period π. Setting c₁ = 0 gives a solution "
            "that spirals outwards in that plane; setting c₂ = c₃ = 0 gives the "
            "straight-line solution along (2, −3, 2)."
        ),
    )),
    Section("Common errors", (
        Para(
            "The first and commonest is the one the warning box describes: "
            "applying Euler's formula to e^(λt) and forgetting that the "
            "eigenvector is complex, so that the b terms go missing. The result "
            "is not a solution, and substituting it back, as this application "
            "does, shows at once that it is not. The second is working through "
            "both eigenvalues of the pair and then adding four real solutions "
            "where two are wanted. The conjugate supplies the same two again."
        ),
        Para(
            "The third is to judge stability from β. How fast a spiral turns "
            "says nothing about whether it comes in or goes out; only the sign "
            "of α, which is half the trace, does. The fourth is to read the "
            "direction of rotation off the eigenvalue, which carries none, "
            "instead of off the lower-left entry a₂₁. The fifth is fitting the "
            "initial condition to the complex eigenvector v, or to the full "
            "general solution at some general t, instead of at t = 0, where p "
            "and q are simply a and b and the constants come from "
            "c₁a + c₂b = x(0)."
        ),
    )),
    Section("Summary", (
        Para(
            "A real matrix can have complex eigenvalues α ± iβ, which then come "
            "with conjugate eigenvectors, and the absence of real eigenvectors "
            "means that no trajectory is a straight line. One complex solution "
            "v e^(λt) with v = a + ib has real part e^(αt)(a cos βt − b sin βt) and "
            "imaginary part e^(αt)(a sin βt + b cos βt), and these two are "
            "independent real solutions whose combinations are all the "
            "solutions. The real part α = τ/2 decides the character of the "
            "origin: a stable spiral when negative, a centre when zero, an "
            "unstable spiral when positive. The imaginary part β sets the period "
            "2π/β, and the sign of the lower-left entry a₂₁ sets the direction of turning. "
            "The underdamped oscillator of Unit 4 is the same mathematics seen "
            "against time instead of in the plane. The next chapter takes up the "
            "remaining case, a repeated eigenvalue, where the eigenvectors can "
            "run out altogether."
        ),
    )),
)


REPEATED = (
    Section("Half an answer", (
        Para(
            "The eigenvalue method of the last two chapters rests on a count. "
            "A system x' = Ax of two equations needs two independent "
            "solutions, because it must be able to meet any pair of initial "
            "values x(0), y(0). Each eigenvalue λ with eigenvector v supplies "
            "one solution v·e^(λt), and so long as the matrix "
            "has two different eigenvalues, real or complex, there are two "
            "eigenvectors pointing in different directions and the count "
            "comes out right."
        ),
        Para(
            "When the characteristic polynomial has a double root, that "
            "count can fail. There is then only one eigenvalue, and it may "
            "have only one line of eigenvectors. The method has produced one "
            "solution where two are needed: half an answer. This chapter is "
            "about the other half — when it is really missing, what shape it "
            "must have, and how to compute it."
        ),
        Para(
            "Nothing here is entirely new. In the second-order unit a repeated "
            "characteristic root r gave only the one exponential e^(rt), and "
            "the missing solution turned out to be t·e^(rt). The same factor "
            "of t appears here, for the same reason. The only new thing is "
            "that a vector has to come with it, and finding that vector is a "
            "small, pleasant piece of linear algebra."
        ),
    )),
    Section("When is an eigenvalue repeated?", (
        Para(
            "Write the matrix A by its entries: first row (a, b), second row "
            "(c, d). Its characteristic polynomial is λ² − τλ + Δ, where "
            "τ = a + d is the trace and Δ = ad − bc is the determinant, and "
            "the quadratic formula shows the root is repeated exactly when "
            "the discriminant vanishes."
        ),
        Display(r"\tau^{2} - 4\Delta = (a - d)^{2} + 4bc = 0, \qquad "
                r"\lambda = \frac{\tau}{2}", "1"),
        Para(
            "The middle form is worth having, because it makes the condition "
            "easy to see. If b or c is zero the matrix is triangular and the "
            "eigenvalues are its diagonal entries, so the root is repeated "
            "exactly when a = d. Otherwise bc must be negative, with "
            "(a − d)² = −4bc. For instance the matrix with rows (1, −1) and "
            "(1, 3) has (1 − 3)² + 4·(−1)·1 = 0, trace 4 and determinant 4, "
            "so its characteristic polynomial is (λ − 2)² and λ = 2 is a "
            "double root, although nothing about the entries suggests it."
        ),
        Para(
            "Equation 1 is a single equation in four entries, so a matrix "
            "chosen at random almost never satisfies it. Repeated eigenvalues "
            "are a borderline case, balanced between two real eigenvalues "
            "and a complex pair. The phase-portraits chapter will draw that "
            "border as the parabola τ² = 4Δ in the trace–determinant plane. "
            "Borderline cases matter all the same. The critically damped "
            "spring sits exactly on this border, and it is the setting a "
            "designer often aims for, the fastest return to rest without "
            "oscillation."
        ),
    )),
    Section("Repeated is not the same as defective", (
        Para(
            "It is tempting to say that a repeated eigenvalue means a "
            "shortage of eigenvectors. That is too strong. The matrix 2I, "
            "twice the identity, has the characteristic polynomial (λ − 2)², "
            "yet every non-zero vector is an eigenvector of it. The trouble "
            "lies in the kind of matrix, not the kind of polynomial, and two "
            "different counts are needed to say so precisely."
        ),
        Box(
            "definition", "Multiplicities, and defective matrices",
            "The *algebraic multiplicity* of an eigenvalue λ is its "
            "multiplicity as a root of the characteristic polynomial. Its "
            "*geometric multiplicity* is the number of independent "
            "eigenvectors it has, the dimension of the kernel of A − λI. The "
            "geometric multiplicity is at least one and never exceeds the "
            "algebraic one. A matrix is *defective* when some eigenvalue has "
            "geometric multiplicity strictly less than its algebraic "
            "multiplicity: it is short of eigenvectors.",
            r"1 \leq \dim\ker(A - \lambda I) \leq "
            r"\text{multiplicity of } \lambda \text{ as a root}",
        ),
        Para(
            "For a two-by-two matrix with a double eigenvalue there are only "
            "two possibilities, and one of them is very special indeed."
        ),
        Box(
            "theorem", "The two-by-two dichotomy",
            "Let A be 2×2 with a repeated eigenvalue λ. Then either A = λI, "
            "and every non-zero vector is an eigenvector, or A is defective, "
            "with exactly one line of eigenvectors. In particular a 2×2 "
            "matrix with a repeated eigenvalue and any non-zero off-diagonal "
            "entry is defective.",
            r"\dim\ker(A - \lambda I) = 2 \;\Longleftrightarrow\; "
            r"A - \lambda I = 0",
        ),
        Box(
            "proof", "Proof",
            "The kernel of A − λI is at least a line, because λ is an "
            "eigenvalue. If it is the whole plane, then A − λI sends every "
            "vector to zero, so it is the zero matrix and A = λI. If it is "
            "not the whole plane it is exactly a line, and the eigenvalue of "
            "algebraic multiplicity two has geometric multiplicity one.",
        ),
        Worked(
            "Three diagnoses",
            "Each matrix below has a repeated eigenvalue. Decide which are "
            "defective. (i) rows (3, 1) and (0, 3); (ii) rows (1, −1) and "
            "(1, 3); (iii) rows (2, 0) and (0, 2).",
            (
                Step("(i) is triangular with 3 twice on the diagonal. A − 3I "
                     "has rows (0, 1) and (0, 0): it is not zero, so the "
                     "matrix is defective. Its kernel is the line through "
                     "(1, 0).",
                     r"(A - 3I)\binom{v_1}{v_2} = \binom{v_2}{0} = \mathbf{0} "
                     r"\;\Longrightarrow\; \mathbf{v} = \binom{1}{0}"),
                Step("(ii) has τ = 4 and Δ = 4, so λ = 2 twice, as found above. "
                     "A − 2I has rows (−1, −1) and (1, 1), again not zero, so "
                     "it is defective. Both rows say v₁ + v₂ = 0, so the "
                     "eigenvectors are the multiples of (1, −1).",
                     r"\mathbf{v} = \binom{1}{-1}"),
                Step("(iii) is 2I itself. A − 2I is the zero matrix, every "
                     "vector is an eigenvector, and nothing new is needed: "
                     "(1, 0) and (0, 1) are two independent eigenvectors and "
                     "the previous chapters already finish the job."),
            ),
        ),
        Para(
            "The non-defective case is worth a moment, if only to see how "
            "little is in it. The system x' = 2x, y' = 2y is two separate "
            "equations that happen to share a rate, and each component grows "
            "by itself."
        ),
        Worked(
            "The complete case",
            "Solve x' = 2x, y' = 2y with x(0) = 3, y(0) = −1.",
            (
                Step("The matrix is 2I, so (1, 0) and (0, 1) are eigenvectors "
                     "for the one eigenvalue 2, and the general solution is a "
                     "combination of the two straight-line solutions.",
                     r"\mathbf{x} = c_1\binom{1}{0}e^{2t} + c_2\binom{0}{1}e^{2t}"),
                Step("At t = 0 this is (c₁, c₂), so c₁ = 3 and c₂ = −1. The "
                     "solution is the initial vector, scaled by e^(2t).",
                     r"\mathbf{x} = e^{2t}\binom{3}{-1}"),
            ),
            equation="x' = 2*x; y' = 2*y",
            conditions="x(0) = 3, y(0) = -1",
            answer="x = 3*exp(2*t)\ny = -exp(2*t)",
            answer_latex=r"x = 3e^{2t}, \quad y = -e^{2t}",
        ),
        Para(
            "Every trajectory of this system is a ray from the origin, "
            "because every direction is an eigendirection. The portrait is "
            "called a *star*, or a proper node. Everything else in this "
            "chapter concerns the other case, where the rays have collapsed "
            "to a single line."
        ),
    )),
    Section("Why one direction cannot carry two solutions", (
        Para(
            "Suppose A is defective, with eigenvalue λ and eigenvector v. "
            "The straight-line solution x₁ = v·e^(λt) is still a solution, "
            "and so is every multiple of it, but all of them lie on the one "
            "line through v. At t = 0 they can only start on that line, so "
            "they cannot meet an initial value off it. A second solution is "
            "needed, and it cannot be another straight-line solution, "
            "because every straight-line solution is c·v·e^(λt)."
        ),
        Para(
            "The most natural first guess is to keep the exponential and "
            "change the vector: try x = w·e^(λt) for some w that is not an "
            "eigenvector. Substituting gives λw·e^(λt) on the left and "
            "Aw·e^(λt) on the right, and these agree only if Aw = λw, which "
            "is to say only if w is an eigenvector after all. The guess "
            "fails, and it is worth seeing exactly how it fails. Whatever w "
            "is, the mismatch is the vector (A − λI)w times e^(λt): a "
            "leftover term, pointing somewhere, that nothing in the guess "
            "can cancel."
        ),
        Para(
            "So widen the guess, taking the hint from the second-order unit: "
            "an exponential multiplied by something linear in t. Leave both "
            "vectors unknown and let the equation decide them."
        ),
        Display(r"\mathbf{x} = \left(\mathbf{w} + t\,\mathbf{v}\right)e^{\lambda t}",
                "2"),
        Para(
            "Differentiate with the product rule and substitute. After "
            "dividing by e^(λt), which is never zero, the equation becomes an "
            "identity between two vector expressions that are linear in t."
        ),
        Display(r"\lambda\mathbf{w} + \mathbf{v} + \lambda t\,\mathbf{v} = "
                r"A\mathbf{w} + t\,A\mathbf{v}", "3"),
        Para(
            "Two expressions p + tq, with constant vectors p and q, agree for "
            "every t only if they agree term by term: t = 0 forces the "
            "constant parts to match, and then the coefficients of t must "
            "match as well. So one vector equation splits into two."
        ),
        Display(r"(A - \lambda I)\mathbf{v} = \mathbf{0}, \qquad "
                r"(A - \lambda I)\mathbf{w} = \mathbf{v}", "4"),
        Para(
            "The first says v is an eigenvector, which was already known. "
            "The second is the new content. It asks for a vector that A − λI "
            "sends not to zero but to the eigenvector — the leftover term "
            "from the failed guess, arranged on purpose. The t·v·e^(λt) term "
            "is there because, when it is differentiated, the product rule "
            "throws off exactly v·e^(λt), which is what cancels that leftover. "
            "The t is not decoration and not a convention. It is the smallest "
            "change to the guess that can cancel what the plain exponential "
            "leaves behind."
        ),
    )),
    Section("Generalised eigenvectors", (
        Box(
            "definition", "Generalised eigenvector",
            "Let v be an eigenvector of A for the eigenvalue λ. A vector w "
            "with (A − λI)w = v is a *generalised eigenvector* belonging to "
            "v. Applying A − λI once to w gives v, and applying it twice "
            "gives zero. It is one step further from the kernel than an "
            "eigenvector, which is what *generalised* means. The pair v, w "
            "is called a chain of length two.",
            r"(A - \lambda I)\mathbf{w} = \mathbf{v} \neq \mathbf{0}, \qquad "
            r"(A - \lambda I)^{2}\mathbf{w} = \mathbf{0}",
        ),
        Para(
            "The matrix A − λI is singular, so an equation (A − λI)w = v may "
            "well have no solution at all. For 2×2 matrices a solution exists "
            "exactly in the defective case (when A = λI, N is zero and "
            "Nw = v ≠ 0 has none). Write N = A − λI."
        ),
        Box(
            "theorem", "Existence of the generalised eigenvector",
            "If A is a defective 2×2 matrix with repeated eigenvalue λ and "
            "eigenvector v, then N = A − λI satisfies N² = 0, and the "
            "equation Nw = v has solutions. Any two of them differ by a "
            "multiple of v.",
            r"N = A - \lambda I \neq 0, \qquad N^{2} = 0",
        ),
        Box(
            "proof", "Proof",
            "Because λ = τ/2, N = A − λI has trace zero, so its rows are "
            "(p, q) and (r, −p) for some numbers p, q, r, and its determinant "
            "−p² − qr is the characteristic polynomial evaluated at λ, which "
            "is zero. Multiplying out, N² = (p² + qr)I = 0. (This is the 2×2 "
            "case of the Cayley–Hamilton theorem of linear algebra.) That says "
            "every vector Nu lies in the kernel of N, which is the line "
            "through v. Since N is not zero, some Nu is a non-zero multiple "
            "of v, and rescaling u gives Nw = v exactly. Finally, if Nw = v "
            "and Nw' = v then N(w − w') = 0, so w − w' is a multiple of v.",
        ),
        Para(
            "The proof also gives a second recipe, which is often quicker. "
            "Instead of choosing v and solving for w, choose any w that is "
            "not an eigenvector — one of (1, 0) and (0, 1) always works, "
            "since if both were eigenvectors A would be λI; in effect, use a "
            "column of A − λI that is not zero — and "
            "*define* v = (A − λI)w. Because N² = 0, this v is automatically "
            "an eigenvector, and the pair is a chain. No equation needs to be "
            "solved at all."
        ),
        Box(
            "remark", "Why the freedom in w does no harm",
            "Replacing w by w + kv changes the second solution by "
            "k·v·e^(λt), which is k times the first solution. That is already "
            "in the general solution, and the constant c₁ absorbs it. Two "
            "people can therefore find different generalised eigenvectors, "
            "write general solutions that look quite unlike each other, and "
            "both be right.",
            r"\mathbf{w} \to \mathbf{w} + k\mathbf{v} \;\Longrightarrow\; "
            r"\mathbf{x}_2 \to \mathbf{x}_2 + k\,\mathbf{v}e^{\lambda t}",
        ),
    )),
    Section("The general solution", (
        Box(
            "theorem", "Defective 2×2 systems",
            "Let A be a defective 2×2 matrix with repeated eigenvalue λ, "
            "eigenvector v and generalised eigenvector w, so that "
            "(A − λI)w = v. Then every solution of x' = Ax is a combination "
            "of the straight-line solution v·e^(λt) and the second solution "
            "(w + tv)e^(λt).",
            r"\mathbf{x}(t) = c_1\mathbf{v}e^{\lambda t} + "
            r"c_2\left(\mathbf{w} + t\,\mathbf{v}\right)e^{\lambda t}",
        ),
        Box(
            "proof", "Proof",
            "Both terms solve the system, the first because v is an "
            "eigenvector and the second by equations 3 and 4. At t = 0 they "
            "equal v and w, and these are independent: if w were a multiple "
            "of v then (A − λI)w would be zero, not v. So the Wronskian "
            "det[v w] is not zero at t = 0, and the two solutions form a "
            "fundamental set. By the existence and uniqueness theorem every "
            "solution is a combination of them.",
        ),
        Para(
            "In practice the method is four steps. Find λ from the trace and "
            "determinant. Check that A − λI is not zero, since otherwise "
            "there is nothing to do. Find an eigenvector v and a generalised "
            "eigenvector w, in either order. Write down the formula and, if "
            "there are initial values, solve c₁v + c₂w = x(0) for the "
            "constants."
        ),
    )),
    Section("A first defective system", (
        Worked(
            "A double eigenvalue at 3",
            "Find the general solution of x' = 3x + y, y' = 3y.",
            (
                Step("The matrix has rows (3, 1) and (0, 3). It is upper "
                     "triangular, so the eigenvalues are its diagonal entries: "
                     "λ = 3, twice."),
                Step("Count the eigenvectors rather than assume. A − 3I has rows "
                     "(0, 1) and (0, 0), which is not zero, so there is one line "
                     "of them, spanned by v = (1, 0).",
                     r"\mathbf{v} = \binom{1}{0}"),
                Step("Solve (A − 3I)w = v. The first row reads w₂ = 1 and the "
                     "second row says nothing, so w₁ is free. Take w₁ = 0.",
                     r"\binom{w_2}{0} = \binom{1}{0} \;\Longrightarrow\; "
                     r"\mathbf{w} = \binom{0}{1}"),
                Step("Assemble the general solution from equation 2 and the "
                     "theorem, then read off the components.",
                     r"\mathbf{x} = c_1\binom{1}{0}e^{3t} + "
                     r"c_2\binom{t}{1}e^{3t}"),
            ),
            equation="x' = 3*x + y; y' = 3*y",
            answer="x = (C1 + C2*t)*exp(3*t)\ny = C2*exp(3*t)",
            answer_latex=r"x = (C_1 + C_2 t)e^{3t}, \quad y = C_2 e^{3t}",
        ),
        Para(
            "The answer can be checked by eye, and for this system it could "
            "have been found without eigenvectors at all. The second equation "
            "involves y alone, so y = C₂e^(3t). Put that into the first and "
            "it becomes the linear equation x' − 3x = C₂e^(3t), whose forcing "
            "is at the equation's own rate. Unit 1's integrating factor, or "
            "the resonance rule of the undetermined-coefficients chapter, "
            "then gives x = (C₁ + C₂t)e^(3t). In that reading the t is "
            "resonance: the y-component drives the x-component at exactly "
            "its natural rate."
        ),
        Para(
            "Now suppose a classmate chose w₁ = 5 instead, so w = (5, 1). "
            "Their second solution is (t + 5, 1)·e^(3t), and their general "
            "solution has x = (C₁ + 5C₂ + C₂t)e^(3t). That is the same family "
            "with the constant C₁ + 5C₂ renamed, exactly as the remark on the "
            "freedom in w predicts. Both answers pass the substitution test."
        ),
        Para(
            "If the corner entry is b instead of 1, as in x' = 3x + by, "
            "y' = 3y, then (A − 3I)w = (1, 0) reads b·w₂ = 1 and gives "
            "w = (0, 1/b). The second recipe avoids the fraction: take "
            "w = (0, 1), so that v = (A − 3I)w = (b, 0), and the general "
            "solution is c₁(b, 0)e^(3t) + c₂(bt, 1)e^(3t)."
        ),
    )),
    Section("Decay, and the hump", (
        Para(
            "Change the sign of the eigenvalue and the structure is unchanged, "
            "but the factor of t now works against a decaying exponential, "
            "and a solution can rise in one component before it falls. That "
            "can happen with two eigenvectors as well, when two decaying "
            "exponentials compete; here the rise comes instead from the "
            "t·e^(λt) term, from a single rate."
        ),
        Worked(
            "The same shape, decaying",
            "Solve x' = −x + y, y' = −y with x(0) = 1, y(0) = 2.",
            (
                Step("The matrix has rows (−1, 1) and (0, −1): triangular, "
                     "λ = −1 twice. A + I has rows (0, 1) and (0, 0), so it is "
                     "defective with v = (1, 0), and as before w = (0, 1) solves "
                     "(A + I)w = v.",
                     r"\mathbf{x} = c_1\binom{1}{0}e^{-t} + "
                     r"c_2\binom{t}{1}e^{-t}"),
                Step("At t = 0 the solution is (c₁, c₂), so c₁ = 1 and c₂ = 2.",
                     r"c_1\binom{1}{0} + c_2\binom{0}{1} = \binom{1}{2}"),
                Step("Read off the components.",
                     r"x = (1 + 2t)e^{-t}, \qquad y = 2e^{-t}"),
            ),
            equation="x' = -x + y; y' = -y",
            conditions="x(0) = 1, y(0) = 2",
            answer="x = (1 + 2*t)*exp(-t)\ny = 2*exp(-t)",
            answer_latex=r"x = (1 + 2t)e^{-t}, \quad y = 2e^{-t}",
        ),
        Para(
            "Both components decay in the end, since t·e^(−t) tends to zero. "
            "But the first one does not start by decaying. Its derivative is "
            "x' = (1 − 2t)e^(−t), which is positive until t = 1/2, so x rises "
            "from 1 to a maximum of 2e^(−1/2) ≈ 1.21 before it turns back. "
            "From a general start (x₀, y₀) with y₀ ≠ 0 the same calculation "
            "puts the turning point of x at t = 1 − x₀/y₀. When "
            "0 ≤ x₀/y₀ < 1 that is a genuine hump: x grows in size before it "
            "decays, and from (0, 1) the curve x = t·e^(−t) is the purest "
            "hump of all, peaking at t = 1. When x₀ and y₀ have opposite "
            "signs, x instead passes through zero at t = −x₀/y₀ and turns "
            "back exactly one time unit later; from (0.5, −2), x reaches zero "
            "at t = 0.25 and its smallest value, −2e^(−1.25) ≈ −0.57, at "
            "t = 1.25."
        ),
        Plot(
            "Rise before fall",
            "The solution from (1, 2), against t, with the plain decay e^(−t) "
            "for comparison. The y-component is an ordinary exponential. The "
            "x-component is carried upward by the t·e^(−t) term, peaks at "
            "t = 1/2, and only then decays.",
            (Curve("(1 + 2*t)*exp(-t)", "x(t)"),
             Curve("2*exp(-t)", "y(t)"),
             Curve("exp(-t)", "e^(-t)")),
            t=(0.0, 6.0), ylabel="x, y", ylim=(-0.1, 2.2),
        ),
        Box(
            "warning", "A hump in a component is not a hump in distance",
            "It is natural to describe the rise as the trajectory moving away "
            "from the origin, but that is not true for this system. The rate "
            "of change of (x² + y²)/2 along solutions is λ(x² + y²) + xy, which "
            "for λ = −1 is −x² + xy − y², and that is negative at every point "
            "except the origin. The distance falls throughout; only the "
            "component along the eigendirection rises. In the family with "
            "rows (λ, 1) and (0, λ) and λ negative, some starts genuinely move "
            "away from the origin at first only when λ > −1/2, because the "
            "largest value of xy on the unit circle is 1/2.",
            r"\frac{d}{dt}\,\frac{x^{2}+y^{2}}{2} = \lambda\left(x^{2}+y^{2}\right)"
            r" + xy",
        ),
    )),
    Section("A matrix that hides its structure", (
        Para(
            "The triangular examples display their eigenvalue on the "
            "diagonal and their eigenvector on the axis. A general defective "
            "matrix hides both, and it is here that the two recipes for the "
            "chain earn their keep."
        ),
        Worked(
            "A disguised double root",
            "Solve x' = x − y, y' = x + 3y with x(0) = 1, y(0) = 0.",
            (
                Step("The trace is 4 and the determinant 3 + 1 = 4, so the "
                     "characteristic polynomial is λ² − 4λ + 4 = (λ − 2)² and "
                     "λ = 2 is a double root.",
                     r"\tau^{2} - 4\Delta = 16 - 16 = 0"),
                Step("A − 2I has rows (−1, −1) and (1, 1). It is not zero, so "
                     "the matrix is defective, and both rows say v₁ + v₂ = 0: "
                     "take v = (1, −1)."),
                Step("Solve (A − 2I)w = v. The first row reads −w₁ − w₂ = 1 and "
                     "the second is the same equation, so w = (−1, 0) will do.",
                     r"\mathbf{v} = \binom{1}{-1}, \qquad "
                     r"\mathbf{w} = \binom{-1}{0}"),
                Step("Fit the initial values: c₁v + c₂w = (c₁ − c₂, −c₁) must "
                     "equal (1, 0), so c₁ = 0 and c₂ = −1.",
                     r"\mathbf{x} = -\left(\binom{-1}{0} + t\binom{1}{-1}\right)"
                     r"e^{2t} = \binom{1 - t}{t}e^{2t}"),
            ),
            equation="x' = x - y; y' = x + 3*y",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = (1 - t)*exp(2*t)\ny = t*exp(2*t)",
            answer_latex=r"x = (1 - t)e^{2t}, \quad y = t\,e^{2t}",
        ),
        Para(
            "The second recipe reaches the same place with less effort. "
            "Choose w = (1, 0), which is not an eigenvector, and define "
            "v = (A − 2I)w. That is the first column of A − 2I, namely "
            "(−1, 1), and it is indeed an eigenvector. The second solution is "
            "then ((1, 0) + t(−1, 1))e^(2t) = (1 − t, t)·e^(2t), which already "
            "has the initial value (1, 0): the initial-value problem is "
            "solved without fitting any constants."
        ),
        Para(
            "It is worth substituting once by hand. With x = (1 − t)e^(2t) and "
            "y = te^(2t), the derivative x' = (1 − 2t)e^(2t) and x − y = "
            "(1 − 2t)e^(2t) agree; y' = (1 + 2t)e^(2t) and x + 3y = "
            "(1 + 2t)e^(2t) agree. Both components pick up a t, which is "
            "typical: only in the triangular examples does the t stay "
            "politely in one component."
        ),
    )),
    Section("The critically damped spring as a system", (
        Para(
            "The first chapter of this unit turned every second-order "
            "equation into a system. Doing that to a critically damped "
            "equation shows that the connection with the repeated roots of "
            "Unit 3 is not an analogy but an identity."
        ),
        Worked(
            "Critical damping, in the plane",
            "Convert the equation u'' + 2u' + u = 0, with u(0) = 1 and "
            "u'(0) = 0, to a system by naming the displacement x = u and the "
            "velocity y = u'. The result is x' = y, y' = −x − 2y with "
            "x(0) = 1, y(0) = 0. Solve it by the method of this chapter.",
            (
                Step("The matrix has rows (0, 1) and (−1, −2): trace −2, "
                     "determinant 1, so λ² + 2λ + 1 = (λ + 1)² and λ = −1 "
                     "twice, the same double root as the characteristic "
                     "equation r² + 2r + 1 = 0."),
                Step("A + I has rows (1, 1) and (−1, −1), not zero, so the "
                     "matrix is defective with v = (1, −1). The equation "
                     "(A + I)w = v reads w₁ + w₂ = 1; take w = (1, 0).",
                     r"\mathbf{v} = \binom{1}{-1}, \qquad "
                     r"\mathbf{w} = \binom{1}{0}"),
                Step("Fit x(0) = (1, 0): c₁ + c₂ = 1 and −c₁ = 0, so c₁ = 0 and "
                     "c₂ = 1.",
                     r"\mathbf{x} = \left(\binom{1}{0} + t\binom{1}{-1}\right)"
                     r"e^{-t} = \binom{1 + t}{-t}e^{-t}"),
            ),
            equation="x' = y; y' = -x - 2*y",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = (1 + t)*exp(-t)\ny = -t*exp(-t)",
            answer_latex=r"x = (1 + t)e^{-t}, \quad y = -t\,e^{-t}",
        ),
        Para(
            "The first component is (1 + t)e^(−t), exactly the critically "
            "damped motion of Unit 4, released from rest at displacement 1, "
            "and the second component is its velocity. "
            "The (C₁ + C₂t)e^(rt) of the characteristic-roots chapter and the "
            "generalised-eigenvector formula are one fact seen twice."
        ),
        Box(
            "remark", "Why a repeated root at second order always needs a t",
            "The system of y'' + py' + qy = 0 has the matrix with rows (0, 1) "
            "and (−q, −p), whose characteristic polynomial is λ² + pλ + q. Its "
            "top-right entry is 1, so it is never a multiple of the identity. "
            "By the dichotomy theorem, whenever its eigenvalue is repeated it "
            "is defective. That is why a repeated characteristic root of a "
            "second-order equation *always* brings in t·e^(rt), while a "
            "repeated eigenvalue of a general system brings it in only "
            "sometimes.",
        ),
    )),
    Section("The degenerate node", (
        Para(
            "Solve x' = −x + y, y' = −y from a general start (x₀, y₀) and the "
            "solution is x = (x₀ + y₀t)e^(−t), y = y₀e^(−t). If y₀ = 0 the "
            "point slides straight in along the x-axis, the one "
            "eigendirection. Otherwise the ratio y/x = y₀/(x₀ + y₀t) tends to "
            "zero, so every trajectory arrives at the origin tangent to that "
            "same axis. On the way it crosses the y-axis at most once, when "
            "x₀ + y₀t = 0, and so it arrives from one side or the other. "
            "For λ > 0 the picture is the same with every arrow reversed: an "
            "unstable degenerate node, whose trajectories leave the origin "
            "tangent to the eigendirection. For λ = 0, as in the matrix with "
            "rows (0, 1) and (0, 0), the solution is x = x₀ + y₀t, y = y₀: "
            "every point of the x-axis is an equilibrium and the other "
            "trajectories are horizontal lines, which is not a node at all."
        ),
        Plot(
            "A degenerate node",
            "Trajectories of x' = −x + y, y' = −y from (1, 2), (−1, −2), "
            "(0.5, −2) and (−0.5, 2), with the eigendirection along the "
            "x-axis. The last two cross the y-axis and swing round. Every "
            "trajectory turns to meet the origin tangent to that one line, "
            "arriving from the right when y₀ > 0 and from the left when "
            "y₀ < 0. There is no second straight line anywhere.",
            (Curve("(1 + 2*t)*exp(-t)", "from (1, 2)", y="2*exp(-t)"),
             Curve("-(1 + 2*t)*exp(-t)", "from (-1, -2)", y="-2*exp(-t)"),
             Curve("(0.5 - 2*t)*exp(-t)", "from (0.5, -2)", y="-2*exp(-t)"),
             Curve("-(0.5 - 2*t)*exp(-t)", "from (-0.5, 2)", y="2*exp(-t)"),
             Curve("(t - 5)/2", "eigendirection", y="0")),
            t=(0.0, 10.0), xlabel="x", ylabel="y", ylim=(-2.3, 2.3),
        ),
        Para(
            "Compare the nodes of the eigenvalues chapter, which have two "
            "straight-line directions. Here the two eigenvalues have merged, "
            "the two directions have merged with them, and what is left is a "
            "node with a single direction of approach, called a *degenerate* "
            "or improper node. The trajectories are pulled round towards that "
            "direction, and the turning can be read as a trace of the spirals "
            "on the other side of the border τ² = 4Δ: perturb the matrix "
            "slightly one way and the eigenvalues become a complex pair, "
            "slightly the other way and they split into two real ones. The "
            "phase-portraits chapter will place the degenerate node on that border, between "
            "the nodes and the spirals."
        ),
        Figure("defective",
               "Drag λ, the repeated eigenvalue, across its range from −1.2 to "
               "0.6. On the left, look for a second line through the origin "
               "that trajectories stay on: there is none, for any λ. On the "
               "right, set c₂, the weight on the t·e^(λt) solution, to zero "
               "and the hump disappears with it. The drawn sum "
               "(1 + c₂t)e^(λt) starts with slope λ + c₂, so with λ negative "
               "it rises before it falls only once c₂ is larger than −λ, and "
               "then its peak is at t = 1/(−λ) − 1/c₂; with c₂ below −λ the "
               "t-term is too weak to lift the start and the sum only decays. "
               "At the starting "
               "values λ = −0.5 and c₂ = 1 the drawn sum (1 + t)e^(−t/2) peaks "
               "at t = 1, while the t·e^(λt) term alone peaks at −1/λ = 2. With "
               "λ positive the t makes the growth faster still."),
    )),
    Section("Longer chains", (
        Para(
            "Nothing in the method is special to two dimensions. In a 3×3 "
            "system an eigenvalue of algebraic multiplicity three may have "
            "three, two or only one independent eigenvector. With only one, "
            "a chain of length three is needed: v, then w with (A − λI)w = v, "
            "then u with (A − λI)u = w. The third solution carries a t², and "
            "the factor ½ in front of it is what the product rule requires."
        ),
        Display(r"\mathbf{x}_3 = \left(\mathbf{u} + t\,\mathbf{w} + "
                r"\frac{t^{2}}{2}\,\mathbf{v}\right)e^{\lambda t}", "5"),
        Worked(
            "A chain of three",
            "Find the general solution of x' = 2x + y, y' = 2y + z, z' = 2z.",
            (
                Step("The matrix is upper triangular with 2 three times on the "
                     "diagonal. A − 2I shifts components up one place, "
                     "(v₁, v₂, v₃) to (v₂, v₃, 0), so its kernel is the line "
                     "through (1, 0, 0) alone."),
                Step("Build the chain by running the shift backwards: "
                     "v = (1, 0, 0), w = (0, 1, 0), u = (0, 0, 1). Each is sent "
                     "to the one before it, and v to zero."),
                Step("Assemble the three solutions v·e^(2t), (w + tv)e^(2t) and "
                     "(u + tw + ½t²v)e^(2t), and combine them.",
                     r"x = \left(C_1 + C_2 t + \frac{C_3 t^{2}}{2}\right)e^{2t}"),
            ),
            equation="x' = 2*x + y; y' = 2*y + z; z' = 2*z",
            answer="x = (C1 + C2*t + C3*t**2/2)*exp(2*t)\n"
                   "y = (C2 + C3*t)*exp(2*t)\n"
                   "z = C3*exp(2*t)",
            answer_latex=r"x = \left(C_1 + C_2 t + \frac{C_3 t^{2}}{2}\right)e^{2t}, "
                         r"\; y = (C_2 + C_3 t)e^{2t}, \; z = C_3 e^{2t}",
        ),
        Para(
            "Read from the bottom up, this is resonance twice over: z drives y "
            "at y's own rate and produces a t, and y then drives x at x's own "
            "rate and produces a t². The intermediate case, a triple eigenvalue "
            "with two eigenvectors, needs one chain of length two and one lone "
            "eigenvector, and so only a single power of t."
        ),
        Para(
            "That case has one trap. With two independent eigenvectors, "
            "(A − λI)w = v is solvable only for particular v, namely those "
            "that A − λI actually produces, and not for an arbitrary "
            "eigenvector. In the 2×2 case the kernel of A − λI and the set of "
            "its outputs are the same line, which is why the question never "
            "arose. Take x' = 2x + y, y' = 2y, z' = 2z, where A − 2I sends "
            "(w₁, w₂, w₃) to (w₂, 0, 0). Its kernel is spanned by (1, 0, 0) and "
            "(0, 0, 1), but choosing v = (0, 0, 1) makes the third component of "
            "(A − 2I)w = v read 0 = 1. The safe route is the second recipe: "
            "pick w with (A − 2I)w ≠ 0, here w = (0, 1, 0), and set "
            "v = (A − 2I)w = (1, 0, 0). Then (0, 0, 1) is the lone eigenvector, "
            "and the general solution is x = (C₁ + C₂t)e^(2t), y = C₂e^(2t), "
            "z = C₃e^(2t)."
        ),
        Para(
            "The case met most often in practice mixes the two worlds: a 3×3 "
            "matrix with a defective double eigenvalue and a separate simple "
            "one. Each eigenvalue is handled on its own terms, the simple one "
            "by an ordinary eigenvector and the double one by a chain of "
            "length two, and the three solutions are added."
        ),
        Worked(
            "A double eigenvalue beside a simple one",
            "Solve x' = x + y, y' = y, z' = −x + 2y + 2z with x(0) = 0, "
            "y(0) = 1, z(0) = 0.",
            (
                Step("Expanding det(A − λI) along the third column gives "
                     "(2 − λ)(1 − λ)², so λ = 1 is a double root and λ = 2 a "
                     "simple one.",
                     r"\det(A - \lambda I) = (2 - \lambda)(1 - \lambda)^{2}"),
                Step("For λ = 2, A − 2I has rows (−1, 1, 0), (0, −1, 0) and "
                     "(−1, 2, 0). The second row forces u₂ = 0, then the first "
                     "forces u₁ = 0, and u₃ is free: u = (0, 0, 1)."),
                Step("For λ = 1, A − I has rows (0, 1, 0), (0, 0, 0) and "
                     "(−1, 2, 1). Row reduction leaves the two equations "
                     "v₂ = 0 and v₁ − v₃ = 0, so the kernel is the single line "
                     "through v = (1, 0, 1): only one eigenvector for a double "
                     "root, so λ = 1 is defective.",
                     r"\mathbf{v} = (1, 0, 1)"),
                Step("Solve (A − I)w = v. The first row gives w₂ = 1 and the "
                     "third gives −w₁ + 2w₂ + w₃ = 1, that is w₃ = w₁ − 1. Take "
                     "w₁ = 1, so w = (1, 1, 0).",
                     r"\mathbf{w} = (1, 1, 0)"),
                Step("The general solution is c₁v·e^t + c₂(w + tv)e^t + "
                     "c₃u·e^(2t). At t = 0 it is c₁v + c₂w + c₃u = "
                     "(c₁ + c₂, c₂, c₁ + c₃), which must equal (0, 1, 0): so "
                     "c₂ = 1, c₁ = −1 and c₃ = 1.",
                     r"\mathbf{x} = -\mathbf{v}e^{t} + (\mathbf{w} + t\,\mathbf{v})"
                     r"e^{t} + \mathbf{u}e^{2t}"),
            ),
            equation="x' = x + y; y' = y; z' = -x + 2*y + 2*z",
            conditions="x(0) = 0, y(0) = 1, z(0) = 0",
            answer="x = t*exp(t)\ny = exp(t)\nz = (t - 1)*exp(t) + exp(2*t)",
            answer_latex=r"x = t\,e^{t}, \; y = e^{t}, \; "
                         r"z = (t - 1)e^{t} + e^{2t}",
        ),
        Para(
            "A substitution check on the last component: z' = t·e^t + 2e^(2t), "
            "and −x + 2y + 2z = −t·e^t + 2e^t + 2(t − 1)e^t + 2e^(2t) = "
            "t·e^t + 2e^(2t), as it should be. The t appears only with the "
            "defective eigenvalue; the simple eigenvalue 2 contributes a plain "
            "exponential. How to organise all of this in general is the "
            "subject of the Jordan form in linear algebra, and the course does "
            "not need it beyond this point."
        ),
    )),
    Section("A glimpse of the matrix exponential", (
        Para(
            "The next chapter defines e^(At), the fundamental "
            "matrix that equals I at t = 0. For most matrices computing it "
            "takes work, but for a defective 2×2 matrix it is almost free. "
            "Write A = λI + N with N² = 0. The two parts commute, so the "
            "exponential factorises, and the series for e^(Nt) stops after "
            "two terms because every higher power of N is zero."
        ),
        Display(r"e^{At} = e^{\lambda t}\,e^{Nt} = e^{\lambda t}\left(I + t\,N\right)",
                "6"),
        Para(
            "For the disguised example, N = A − 2I has rows (−1, −1) and "
            "(1, 1), so e^(At) has rows (1 − t, −t) and (t, 1 + t), all times "
            "e^(2t). Its first column, (1 − t, t)e^(2t), is precisely the "
            "solution found above from x(0) = (1, 0), as it must be. Once "
            "again the t is the whole story: it enters through the one "
            "surviving power of N."
        ),
    )),
    Section("Common errors", (
        Para(
            "The commonest error is assuming a repeated eigenvalue is defective "
            "without checking. For a 2×2 matrix the check costs nothing — "
            "is A − λI the zero matrix? — and when it is, there is no "
            "generalised eigenvector to find, since (A − λI)w is zero for every "
            "w. A second error, once the matrix is known to be defective, is "
            "solving (A − λI)w = 0 again and "
            "calling the result a second eigenvector. For a defective matrix "
            "it can only be a multiple of v, so the two solutions it gives "
            "are dependent and cannot meet general initial values."
        ),
        Para(
            "A third error is writing the second solution as t·v·e^(λt) alone, "
            "which borrows the second-order formula without its vector. "
            "Substituting leaves v·e^(λt) unmatched, because the product rule "
            "produces it and nothing else cancels it; w is not optional. A "
            "fourth is putting the vectors the wrong way round, (v + tw)e^(λt): "
            "the t must multiply the *eigenvector*, since equation 4 makes v "
            "the coefficient of t. A slip in the constants is just as easy: "
            "for x' = −x + y, y' = −y from (1, 2), x = (1 + t)e^(−t) meets "
            "both initial values but fails the first equation, because the "
            "t-term carries c₂ = 2. Finally, answers that differ from the back "
            "of the book are not necessarily wrong. A different w changes the "
            "look of the general solution but not the family, so compare by "
            "substitution, or by solving the same initial-value problem."
        ),
    )),
    Section("Summary", (
        Para(
            "A 2×2 matrix has a repeated eigenvalue λ = τ/2 exactly when "
            "τ² = 4Δ. If A = λI, every vector is an eigenvector and nothing new "
            "is needed. Otherwise A is defective: one line of eigenvectors, "
            "N = A − λI non-zero with N² = 0. Then a generalised eigenvector w "
            "with (A − λI)w = v exists, unique up to adding multiples of v, "
            "and the general solution is c₁v·e^(λt) + c₂(w + tv)e^(λt). The t "
            "is there to cancel the leftover v·e^(λt) that the plain "
            "exponential cannot. It can make a decaying solution rise in one "
            "component before it falls — a critically damped spring pushed "
            "outward does exactly this — and it turns the portrait into a degenerate "
            "node with a single direction of approach. Longer chains bring "
            "higher powers of t, and e^(At) = e^(λt)(I + tN) packages the "
            "whole 2×2 case in one line."
        ),
    )),
)


NONHOMOGENEOUS = (
    Section("Something pushing on the system", (
        Para(
            "Every system in this unit so far has had nothing on the "
            "right-hand side. The same objection applies as it did at second "
            "order: an unforced system is a system with nothing happening to "
            "it. Two tanks exchanging brine are more interesting when fresh "
            "brine is pumped in; a circuit with two loops is more interesting "
            "with a battery or an alternating source in one of them; a pair of "
            "coupled masses is more interesting when one of them is shaken. In "
            "each case there is a vector of things pushing on the system, one "
            "entry per equation, and it may depend on time."
        ),
        Para(
            "The good news is that almost nothing already learned is lost. "
            "The structure of the answer only ever depended on linearity, and "
            "linearity is still there, so the general solution is again one "
            "particular solution plus the homogeneous family. All the "
            "eigenvalue work of the earlier chapters is the first half of the "
            "answer, unchanged. The only new question is how to find a single "
            "particular solution."
        ),
        Para(
            "Variation of parameters answers it, and in the matrix setting it "
            "is *tidier* than in the scalar one. At second order the method "
            "needed a Wronskian, two integrals with opposite signs and a side "
            "condition invented to make the unknowns determined. Here it is "
            "one matrix inverse and one integral, and no side condition is "
            "needed. Along the way one particular matrix of solutions, the "
            "matrix exponential e^(At), turns out to express the whole answer "
            "in a single formula that looks exactly like the first equation "
            "of the course."
        ),
    )),
    Section("The structure of the answer", (
        Para(
            "A nonhomogeneous linear system with constant coefficients has the "
            "form below, where A is a constant n × n matrix and f(t) is a "
            "vector of given functions, the *forcing*. The first job with any "
            "such system is to split it into those two pieces: everything "
            "multiplying an unknown goes into A, and everything else goes into "
            "f."
        ),
        Display(r"\mathbf{x}' = A\mathbf{x} + \mathbf{f}(t)", "1"),
        Para(
            "For example, the system x' = x + 2y + e^t, y' = 3x + 2y is the "
            "saddle of the eigenvalues chapter with something pushing on it. "
            "Its matrix A has rows (1, 2) and (3, 2), exactly as before, and "
            "the forcing is f(t) = (e^t, 0): the push acts on the first "
            "equation only. Dropping f gives the *associated homogeneous "
            "system* x' = Ax, which is the problem the rest of the unit has "
            "been solving."
        ),
        Box(
            "theorem", "General solution of a forced system",
            "Let x_p be any one solution of x' = Ax + f, and let x_h = "
            "c₁x₁ + ⋯ + cₙxₙ be the general solution of x' = Ax. Then every "
            "solution of the forced system is x_h + x_p for some choice of the "
            "constants, and every such sum is a solution.",
            r"\mathbf{x} = \mathbf{x}_h + \mathbf{x}_p",
        ),
        Box(
            "proof", "Proof",
            "If x solves the forced system, then (x − x_p)' = Ax + f − Ax_p − f "
            "= A(x − x_p), so the difference solves the homogeneous system and "
            "is therefore one of its combinations. Conversely, if x_h' = Ax_h "
            "then (x_h + x_p)' = Ax_h + Ax_p + f = A(x_h + x_p) + f, so the sum "
            "solves the forced system. The forcing cancels in the difference, "
            "which is the whole argument.",
            r"(\mathbf{x} - \mathbf{x}_p)' = A(\mathbf{x} - \mathbf{x}_p)",
        ),
        Para(
            "The existence and uniqueness theorem from the first chapter of "
            "the unit also carries over: when f is continuous on an interval, "
            "each initial vector x(t₀) determines exactly one solution on the "
            "whole interval. So the n constants in x_h are exactly enough, and "
            "fitting them to x(0) is always possible."
        ),
    )),
    Section("The fundamental matrix", (
        Para(
            "The homogeneous family is a combination of n solutions with n "
            "arbitrary constants. Bookkeeping becomes much easier if the "
            "solutions are collected into one matrix and the constants into "
            "one vector."
        ),
        Box(
            "definition", "Fundamental matrix",
            "If x₁, …, xₙ are n linearly independent solutions of x' = Ax, the "
            "matrix Φ(t) whose columns are x₁, …, xₙ is a *fundamental matrix* "
            "of the system. Because each column solves the system, the matrix "
            "does too, column by column, and the general homogeneous solution "
            "is Φ(t) times a constant vector c.",
            r"\Phi(t) = (\,\mathbf{x}_1 \;\; \cdots \;\; \mathbf{x}_n\,), \qquad "
            r"\Phi' = A\Phi, \qquad \mathbf{x}_h = \Phi(t)\,\mathbf{c}",
        ),
        Para(
            "Fitting initial conditions is now a single linear solve. Setting "
            "t = 0 in x = Φ(t)c gives Φ(0)c = x(0), so c = Φ(0)⁻¹x(0), and the "
            "solution of the initial value problem is Φ(t)Φ(0)⁻¹x(0). That "
            "product of matrices will return later in this chapter under a "
            "better name."
        ),
        Para(
            "Everything below divides by Φ(t), so it matters that Φ(t) is "
            "invertible at *every* t, not just at t = 0. Its determinant is the "
            "Wronskian of the n solutions, and the unit has met the formula it "
            "obeys twice already. The first chapter quoted Abel's formula, "
            "W(t) = W(a)·e^(∫ tr A dt), to show that the Wronskian is either "
            "never zero or always zero, and the eigenvalues chapter checked it "
            "for straight-line solutions as W = det V·e^(τt). Here it is proved "
            "for every fundamental matrix, and in that generality it is "
            "usually called Liouville's formula. The trace τ is written tr A "
            "below."
        ),
        Box(
            "theorem", "Liouville's formula",
            "For any fundamental matrix of x' = Ax, the determinant satisfies "
            "the scalar equation (det Φ)' = (tr A) det Φ. Hence det Φ(t) is "
            "det Φ(0) times an exponential: it is either zero for all t or "
            "never zero at all.",
            r"\det\Phi(t) = \det\Phi(0)\,e^{(\operatorname{tr}A)\,t}",
        ),
        Box(
            "proof", "Proof, for two equations",
            "Write r₁ and r₂ for the rows of Φ. A determinant is linear in each "
            "row, so (det Φ)' is the determinant with r₁ replaced by r₁' plus "
            "the determinant with r₂ replaced by r₂'. From Φ' = AΦ, r₁' = "
            "a₁₁r₁ + a₁₂r₂. The r₂ part gives a determinant with two equal "
            "rows, which is zero, leaving a₁₁ det Φ. Likewise the second term "
            "gives a₂₂ det Φ, and the sum is (a₁₁ + a₂₂) det Φ = (tr A) det Φ.",
        ),
        Worked(
            "The fundamental matrix of the saddle",
            "For x' = x + 2y, y' = 3x + 2y, build a fundamental matrix, check "
            "Liouville's formula, and find its inverse.",
            (
                Step("The eigenvalues chapter found λ₁ = −1 with eigenvector (1, −1) "
                     "and λ₂ = 4 with eigenvector (2, 3). Each eigenvector carries "
                     "its exponential into a column.",
                     r"\mathbf{x}_1 = e^{-t}\binom{1}{-1}, \qquad "
                     r"\mathbf{x}_2 = e^{4t}\binom{2}{3}"),
                Step("So Φ has rows (e^(−t), 2e^(4t)) and (−e^(−t), 3e^(4t)). Its "
                     "determinant is 3e^(3t) + 2e^(3t). The trace of A is 3 and "
                     "det Φ(0) = 5, exactly as Liouville's formula says.",
                     r"\det\Phi(t) = 5e^{3t} = \det\Phi(0)\,e^{3t}"),
                Step("For a 2 × 2 matrix, the inverse swaps the diagonal, negates "
                     "the off-diagonal and divides by the determinant. Φ⁻¹(t) has "
                     "rows (3e^t/5, −2e^t/5) and (e^(−4t)/5, e^(−4t)/5). Since Φ⁻¹ "
                     "will always be applied to a forcing vector, record its "
                     "effect on a general one, (g, h).",
                     r"\Phi^{-1}(t)\binom{g}{h} = \frac{1}{5}"
                     r"\binom{e^{t}\,(3g - 2h)}{e^{-4t}\,(g + h)}"),
            ),
        ),
    )),
    Section("Varying the constants", (
        Para(
            "Now vary the constants exactly as at second order. Look for a "
            "particular solution of the form x_p = Φ(t)u(t), with the constant "
            "vector replaced by an unknown vector function u. The product rule "
            "gives two terms, and the first is already what the homogeneous "
            "part of the equation asks for."
        ),
        Display(r"\left(\Phi\mathbf{u}\right)' = \Phi'\mathbf{u} + "
                r"\Phi\mathbf{u}' = A\Phi\mathbf{u} + \Phi\mathbf{u}'", "2"),
        Para(
            "Setting this equal to AΦu + f, the AΦu terms cancel on both "
            "sides, and what is left is one equation for u'. There are n "
            "unknown functions in u and n scalar equations in Φu' = f, so the "
            "count already matches. The scalar derivation had two unknown "
            "functions and only one equation, which is why it had to invent a "
            "side condition; here none is needed. Since Φ is invertible, u' is "
            "found by one matrix multiplication."
        ),
        Display(r"\Phi\,\mathbf{u}' = \mathbf{f}(t) \;\Longrightarrow\; "
                r"\mathbf{u}' = \Phi^{-1}(t)\,\mathbf{f}(t)", "3"),
        Box(
            "theorem", "Variation of parameters for systems",
            "If Φ is a fundamental matrix of x' = Ax and f is continuous, then "
            "the formula below is a particular solution of x' = Ax + f. The "
            "solution with x(t₀) = x₀ is obtained by using a definite integral "
            "and adding the homogeneous solution that matches x₀.",
            r"\mathbf{x}_p = \Phi(t)\int \Phi^{-1}(t)\,\mathbf{f}(t)\,dt, \qquad "
            r"\mathbf{x}(t) = \Phi(t)\Phi(t_0)^{-1}\mathbf{x}_0 + "
            r"\Phi(t)\int_{t_0}^{t}\Phi^{-1}(s)\,\mathbf{f}(s)\,ds",
        ),
        Box(
            "remark", "No constant of integration",
            "When the integral is taken, no constant vector is added, for the "
            "reason it never was in the scalar case. A constant k in the "
            "integral contributes Φ(t)k to x_p, which is a homogeneous "
            "solution, and the homogeneous part already carries every one of "
            "those with an arbitrary coefficient. Adding one would be harmless "
            "but pointless.",
            r"\Phi(t)\left(\int \Phi^{-1}\mathbf{f}\,dt + \mathbf{k}\right) = "
            r"\mathbf{x}_p + \Phi(t)\,\mathbf{k}",
        ),
        Para(
            "In practice the recipe has four steps: solve the homogeneous "
            "system and assemble Φ; compute Φ⁻¹f; integrate each entry; "
            "multiply back by Φ. The first step is the eigenvalue method, "
            "complex or repeated as the case may be. Only the last three are "
            "new, and they involve no guessing."
        ),
    )),
    Section("A driven saddle", (
        Worked(
            "The saddle pushed by e^t",
            "Find the general solution of x' = x + 2y + e^t, y' = 3x + 2y.",
            (
                Step("Split the system. A has rows (1, 2) and (3, 2), and "
                     "f(t) = (e^t, 0). The homogeneous half is the saddle, whose "
                     "Φ and Φ⁻¹ were found above.",
                     r"\mathbf{f}(t) = \binom{e^{t}}{0}"),
                Step("Apply Φ⁻¹ with g = e^t and h = 0.",
                     r"\mathbf{u}' = \Phi^{-1}\mathbf{f} = "
                     r"\binom{\frac{3}{5}e^{2t}}{\frac{1}{5}e^{-3t}}"),
                Step("Integrate each entry, adding no constants.",
                     r"\mathbf{u} = \binom{\frac{3}{10}e^{2t}}{-\frac{1}{15}e^{-3t}}"),
                Step("Multiply back by Φ, one row at a time.",
                     r"x_p = e^{-t}\cdot\frac{3}{10}e^{2t} + 2e^{4t}\cdot"
                     r"\left(-\frac{1}{15}\right)e^{-3t} = \frac{e^{t}}{6}, \quad "
                     r"y_p = -\frac{3}{10}e^{t} - \frac{1}{5}e^{t} = -\frac{e^{t}}{2}"),
                Step("Add the homogeneous family.",
                     r"\mathbf{x} = C_1e^{-t}\binom{1}{-1} + C_2e^{4t}\binom{2}{3} + "
                     r"e^{t}\binom{1/6}{-1/2}"),
            ),
            equation="x' = x + 2*y + exp(t); y' = 3*x + 2*y",
            answer="x = C1*exp(-t) + 2*C2*exp(4*t) + exp(t)/6\n"
                   "y = -C1*exp(-t) + 3*C2*exp(4*t) - exp(t)/2",
            answer_latex=r"x = C_1e^{-t} + 2C_2e^{4t} + \frac{e^{t}}{6}, \quad "
                         r"y = -C_1e^{-t} + 3C_2e^{4t} - \frac{e^{t}}{2}",
        ),
        Para(
            "Watch where the two halves separated. Everything up to Φ was the "
            "homogeneous problem, lifted from the eigenvalues chapter without "
            "change; everything after it concerned the forcing alone. That "
            "division of labour is the practical content of the structure "
            "theorem."
        ),
        Para(
            "Notice also why the particular solution came out as a plain "
            "multiple of e^t. The forcing's exponent, 1, matches neither "
            "eigenvalue, so the entries of Φ⁻¹f were exponentials with non-zero "
            "exponents, e^(2t) and e^(−3t), and integrated to exponentials. Had "
            "the forcing been e^(−t), one of those exponents would have been "
            "zero, and the integral would have produced a factor of t. That is "
            "the collision the undetermined-coefficients chapter described, "
            "arriving here as an integral that changes character. It is taken "
            "up again in the section on resonance below."
        ),
    )),
    Section("Where the scalar formula came from", (
        Para(
            "The claim that the matrix method is the tidier one can be made "
            "precise. Take y'' + p(t)y' + q(t)y = f(t) and turn it into a "
            "system in the usual way, with x₁ = y and x₂ = y'. The forcing "
            "vector is (0, f), because the forcing appears only in the equation "
            "for y''. If y₁ and y₂ are independent homogeneous solutions, the "
            "fundamental matrix has rows (y₁, y₂) and (y₁', y₂'), and its "
            "determinant is precisely the Wronskian W."
        ),
        Para(
            "The inverse of a 2 × 2 matrix is its adjugate divided by its "
            "determinant: swap the diagonal, negate the off-diagonal. Applied "
            "to (0, f), only the second column of the adjugate survives, and "
            "its entries are −y₂ and y₁."
        ),
        Display(r"\Phi^{-1}\binom{0}{f} = \frac{1}{W}\binom{-y_2 f}{y_1 f}", "4"),
        Para(
            "Integrate, multiply back by Φ, and read off the first component, "
            "which is y. The result is the scalar variation-of-parameters "
            "formula, term for term: the Wronskian in the denominator is the "
            "determinant of Φ, and the one minus sign that had to be "
            "remembered is the sign change the adjugate puts on the "
            "off-diagonal entry y₂. The adjugate's other sign change, on y₁', "
            "sits in the first column, which multiplies the zero in (0, f), so "
            "it never reaches the formula. The side condition "
            "u₁'y₁ + u₂'y₂ = 0 of the scalar derivation is simply the first "
            "row of Φu' = (0, f)."
        ),
        Display(r"y_p = -y_1\int\frac{y_2 f}{W}\,dt + y_2\int\frac{y_1 f}{W}\,dt",
                "5"),
    )),
    Section("Constant forcing and a new equilibrium", (
        Para(
            "When the forcing is constant there is a much quicker route to a "
            "particular solution, and it is worth doing by hand as well as by "
            "formula. Look for a *constant* solution x*. Its derivative is "
            "zero, so the system becomes Ax* + f = 0, an ordinary linear "
            "system with no calculus in it. When det A ≠ 0 it has exactly one "
            "solution, x* = −A⁻¹f, which is an equilibrium of the forced "
            "system, displaced from the origin. When det A = 0, zero is an "
            "eigenvalue and constant forcing is resonant: a constant solution "
            "exists only if f lies in the column space of A, and otherwise the "
            "next section's (at + b) guess, with exponent zero, is needed."
        ),
        Worked(
            "A stable node pushed off the origin",
            "Solve x' = −2x + y + 1, y' = x − 2y with x(0) = 0, y(0) = 0.",
            (
                Step("The homogeneous system is the stable node of the eigenvalue "
                     "chapter: λ = −1 with eigenvector (1, 1) and λ = −3 with "
                     "eigenvector (1, −1).",
                     r"\mathbf{x}_h = C_1e^{-t}\binom{1}{1} + C_2e^{-3t}\binom{1}{-1}"),
                Step("For a constant solution, set both derivatives to zero: "
                     "−2x + y + 1 = 0 and x − 2y = 0. The second gives x = 2y, and "
                     "then −3y + 1 = 0.",
                     r"\mathbf{x}^{*} = \binom{2/3}{1/3}"),
                Step("Fit the conditions at t = 0: C₁ + C₂ + 2/3 = 0 and "
                     "C₁ − C₂ + 1/3 = 0. Adding, 2C₁ = −1; subtracting, "
                     "2C₂ = −1/3.",
                     r"C_1 = -\frac{1}{2}, \qquad C_2 = -\frac{1}{6}"),
                Step("Assemble.",
                     r"x = \frac{2}{3} - \frac{1}{2}e^{-t} - \frac{1}{6}e^{-3t}, \quad "
                     r"y = \frac{1}{3} - \frac{1}{2}e^{-t} + \frac{1}{6}e^{-3t}"),
            ),
            equation="x' = -2*x + y + 1; y' = x - 2*y",
            conditions="x(0) = 0, y(0) = 0",
            answer="x = 2/3 - exp(-t)/2 - exp(-3*t)/6\n"
                   "y = 1/3 - exp(-t)/2 + exp(-3*t)/6",
            answer_latex=r"x = \frac{2}{3} - \frac{e^{-t}}{2} - \frac{e^{-3t}}{6}, "
                         r"\quad y = \frac{1}{3} - \frac{e^{-t}}{2} + "
                         r"\frac{e^{-3t}}{6}",
        ),
        Para(
            "Where the system goes is decided by the eigenvalues, not by the "
            "forcing. Both are negative, so the homogeneous part dies and only "
            "the constant survives: from any starting point the trajectory "
            "ends at (2/3, 1/3). In the language of the eigenvalues chapter, "
            "A has trace −4 and determinant 3, so the forced system has a "
            "stable node, but centred at x* instead of at the origin. "
            "Move the forcing and the destination moves; change the matrix "
            "and the whole picture may stop settling at all."
        ),
        Para(
            "Starting instead at x(0) = 1, y(0) = 0 gives x = 2/3 + e^(−3t)/3, "
            "y = 1/3 − e^(−3t)/3, with no e^(−t) term at all. The reason is "
            "geometric: the starting offset (1, 0) − (2/3, 1/3) = (1/3, −1/3) "
            "lies exactly along the fast eigenvector (1, −1), so only the fast "
            "mode is excited and the approach is along a straight line."
        ),
        Plot(
            "Settling to the displaced equilibrium",
            "The solution from rest of x' = −2x + y + 1, y' = x − 2y. Both "
            "components level off at the equilibrium (2/3, 1/3) set by the "
            "forcing; the slow mode e^(−t) is what is still visible at t = 3.",
            (Curve("2/3 - exp(-t)/2 - exp(-3*t)/6", "x(t)"),
             Curve("1/3 - exp(-t)/2 + exp(-3*t)/6", "y(t)"),
             Curve("2/3 + 0*t", "x* = 2/3"),
             Curve("1/3 + 0*t", "y* = 1/3")),
            t=(0.0, 6.0), ylim=(-0.05, 0.8),
        ),
    )),
    Section("Undetermined coefficients, and resonance", (
        Para(
            "For forcing built from exponentials, polynomials, sines and "
            "cosines, the method of undetermined coefficients also works for "
            "systems, with one change: the unknown coefficients are *vectors*. "
            "For f = e^(kt)f₀ one tries x_p = e^(kt)a. Substituting gives "
            "ka = Aa + f₀, that is (A − kI)a = −f₀, which has a unique solution "
            "whenever k is not an eigenvalue of A. For the driven saddle, k = 1 "
            "and (A − I)a = −(1, 0) gives a = (1/6, −1/2), confirming the "
            "variation-of-parameters answer in two lines."
        ),
        Para(
            "Polynomial forcing works the same way, with one rule to keep: the "
            "trial contains every power of t up to the degree of the forcing, "
            "each with its own vector, even when the forcing has only the top "
            "power. For forcing linear in t the trial is at + b."
        ),
        Worked(
            "A ramp pushing the stable node",
            "Find the general solution of x' = −2x + y + t, y' = x − 2y.",
            (
                Step("Here A has rows (−2, 1) and (1, −2) and f = t(1, 0). Try "
                     "x_p = at + b. Its derivative is the constant a, so the t "
                     "terms and the constant terms must balance separately.",
                     r"\mathbf{a} = A(\mathbf{a}t + \mathbf{b}) + t\binom{1}{0}"),
                Step("The t terms give Aa = −(1, 0): −2a₁ + a₂ = −1 and "
                     "a₁ − 2a₂ = 0, so a₁ = 2a₂ and −3a₂ = −1.",
                     r"\mathbf{a} = \binom{2/3}{1/3}"),
                Step("The constant terms give Ab = a: −2b₁ + b₂ = 2/3 and "
                     "b₁ − 2b₂ = 1/3. Doubling the first and adding the second "
                     "gives −3b₁ = 5/3.",
                     r"\mathbf{b} = \binom{-5/9}{-4/9}"),
                Step("Add the homogeneous family of the stable node.",
                     r"x = \frac{2}{3}t - \frac{5}{9} + C_1e^{-t} + C_2e^{-3t}, "
                     r"\quad y = \frac{1}{3}t - \frac{4}{9} + C_1e^{-t} - C_2e^{-3t}"),
            ),
            equation="x' = -2*x + y + t; y' = x - 2*y",
            answer="x = 2*t/3 - 5/9 + C1*exp(-t) + C2*exp(-3*t)\n"
                   "y = t/3 - 4/9 + C1*exp(-t) - C2*exp(-3*t)",
            answer_latex=r"x = \frac{2t}{3} - \frac{5}{9} + C_1e^{-t} + "
                         r"C_2e^{-3t}, \quad y = \frac{t}{3} - \frac{4}{9} + "
                         r"C_1e^{-t} - C_2e^{-3t}",
        ),
        Para(
            "The constant vector b is not optional. The forcing t(1, 0) has no "
            "constant part, but the trial at alone would leave the term a with "
            "nothing to balance it."
        ),
        Para(
            "When k *is* an eigenvalue, A − kI is singular, and (A − kI)a = −f₀ "
            "has a solution only if f₀ happens to lie in the column space of "
            "A − kI. In the usual case it does not, the guess fails, and this "
            "is resonance in a system. The exception is a real difference from "
            "the scalar case: forcing the saddle with e^(−t)(2, 3) instead of "
            "e^(−t)(1, 0) is not resonant at all. A + I has rows (2, 2) and "
            "(3, 3), whose column space is spanned by (2, 3), and the plain "
            "guess works: a = (−1, 0) gives x_p = (−e^(−t), 0), with no t "
            "anywhere."
        ),
        Para(
            "In the resonant case the cure is not quite the scalar one. It is "
            "not enough to multiply by t: the guess must be (at + b)e^(kt) with "
            "two unknown vectors. The trial te^(kt)a alone can balance the "
            "terms carrying t, but it leaves a plain e^(kt) term, a − f₀, that "
            "only b can cancel."
        ),
        Box(
            "warning", "Multiply by t, and keep the lower term",
            "With f = e^(λt)f₀ and λ a simple eigenvalue (multiplicity one), "
            "try x_p = (at + b)e^(λt). Matching the t terms forces (A − λI)a = 0, so a is an eigenvector; "
            "matching the rest gives (A − λI)b = a − f₀, which is solvable only "
            "for the right multiple of that eigenvector. The guess te^(λt)a "
            "alone, without b, almost always fails. If λ is a repeated "
            "eigenvalue of a defective matrix, the guess needs one more power "
            "of t, (at² + bt + c)e^(λt); variation of parameters handles that "
            "case with no guessing at all.",
            r"(A - \lambda I)\,\mathbf{a} = \mathbf{0}, \qquad "
            r"(A - \lambda I)\,\mathbf{b} = \mathbf{a} - \mathbf{f}_0",
        ),
        Worked(
            "Forcing the saddle at its own eigenvalue",
            "Find the general solution of x' = x + 2y + e^(−t), y' = 3x + 2y.",
            (
                Step("Variation of parameters needs no guess. With g = e^(−t) and "
                     "h = 0, the first entry of Φ⁻¹f loses its exponential "
                     "entirely: that is the collision.",
                     r"\mathbf{u}' = \binom{3/5}{\frac{1}{5}e^{-5t}}, \qquad "
                     r"\mathbf{u} = \binom{\frac{3}{5}t}{-\frac{1}{25}e^{-5t}}"),
                Step("Multiply back by Φ.",
                     r"x_p = \left(\frac{3}{5}t - \frac{2}{25}\right)e^{-t}, \qquad "
                     r"y_p = -\left(\frac{3}{5}t + \frac{3}{25}\right)e^{-t}"),
                Step("Tidy by adding the homogeneous solution (2/25)e^(−t)(1, −1), "
                     "which is allowed because it is already in the family.",
                     r"x_p = \frac{3}{5}t\,e^{-t}, \qquad "
                     r"y_p = -\left(\frac{3}{5}t + \frac{1}{5}\right)e^{-t}"),
                Step("Compare with the warning. Here a = (3/5)(1, −1), an "
                     "eigenvector for −1, and b = (0, −1/5). The lower term b is "
                     "essential: substituting (3/5)te^(−t)(1, −1) alone leaves the "
                     "mismatch e^(−t)(−2/5, −3/5), and (A + I)b = (−2/5, −3/5) is "
                     "exactly what b supplies to cancel it."),
            ),
            equation="x' = x + 2*y + exp(-t); y' = 3*x + 2*y",
            answer="x = C1*exp(-t) + 2*C2*exp(4*t) + 3*t*exp(-t)/5\n"
                   "y = -C1*exp(-t) + 3*C2*exp(4*t) - (3*t/5 + 1/5)*exp(-t)",
            answer_latex=r"x = C_1e^{-t} + 2C_2e^{4t} + \frac{3}{5}te^{-t}, \quad "
                         r"y = -C_1e^{-t} + 3C_2e^{4t} - \left(\frac{3}{5}t + "
                         r"\frac{1}{5}\right)e^{-t}",
        ),
    )),
    Section("The matrix exponential", (
        Para(
            "Any fundamental matrix can be multiplied on the right by a "
            "constant invertible matrix and still be one, since its columns "
            "are then new combinations of the old solutions, still "
            "independent. So there is a whole family of fundamental matrices, "
            "and it is natural to ask for the best-behaved member. The answer "
            "comes from taking the scalar e^(at) = 1 + at + a²t²/2! + ⋯ "
            "literally with a matrix in place of a."
        ),
        Box(
            "definition", "The matrix exponential",
            "For a square matrix A, e^(At) is the sum of the series below. The "
            "series converges for every A and every t, entry by entry, by "
            "comparison with the scalar series for e^(nm|t|), where m is the "
            "largest entry of A in absolute value (each entry of Aᵏ is at most "
            "(nm)ᵏ in size).",
            r"e^{At} = I + At + \frac{A^{2}t^{2}}{2!} + \frac{A^{3}t^{3}}{3!} + "
            r"\cdots = \sum_{k=0}^{\infty}\frac{A^{k}t^{k}}{k!}",
        ),
        Box(
            "theorem", "e^(At) is the fundamental matrix normalised at zero",
            "e^(At) is a fundamental matrix of x' = Ax, and it is the one that "
            "equals the identity at t = 0. For any fundamental matrix Φ, "
            "e^(At) = Φ(t)Φ(0)⁻¹, and the solution with x(0) = x₀ is e^(At)x₀.",
            r"\frac{d}{dt}e^{At} = Ae^{At}, \quad \left.e^{At}\right|_{t=0} = I, "
            r"\quad \mathbf{x}(t) = e^{At}\mathbf{x}(0)",
        ),
        Box(
            "proof", "Proof",
            "Differentiate the series term by term: the derivative of "
            "Aᵏtᵏ/k! is A·Aᵏ⁻¹tᵏ⁻¹/(k − 1)!, so the derivative series is A "
            "times the original. At t = 0 every term but I vanishes, so the "
            "determinant is 1 and by Liouville's formula never zero. Finally, "
            "Φ(t)Φ(0)⁻¹ also solves M' = AM with M(0) = I; each column of "
            "the two matrices solves the same initial value problem, so by "
            "uniqueness they are equal.",
        ),
        Para(
            "The last line is the one worth remembering: x(t) = e^(At)x(0) has "
            "exactly the shape of y = e^(at)y(0), the solution of the very "
            "first equation of the course, y' = ay, and that resemblance is "
            "the reason for the notation. The series is the definition, but "
            "it is rarely the way to compute; the formula Φ(t)Φ(0)⁻¹ usually "
            "is."
        ),
        Worked(
            "e^(At) for the saddle",
            "Compute e^(At) for A with rows (1, 2) and (3, 2).",
            (
                Step("Take the fundamental matrix already found and evaluate it "
                     "at zero: Φ(0) has rows (1, 2) and (−1, 3), determinant 5, "
                     "so Φ(0)⁻¹ has rows (3/5, −2/5) and (1/5, 1/5)."),
                Step("Multiply Φ(t)Φ(0)⁻¹. The first column is the solution that "
                     "starts at (1, 0), the second the one that starts at (0, 1).",
                     r"e^{At}\binom{1}{0} = \frac{1}{5}\binom{3e^{-t} + 2e^{4t}}"
                     r"{3e^{4t} - 3e^{-t}}, \quad e^{At}\binom{0}{1} = "
                     r"\frac{1}{5}\binom{2e^{4t} - 2e^{-t}}{2e^{-t} + 3e^{4t}}"),
                Step("The first column is an old friend: it is the solution from "
                     "(1, 0) already found in the first chapter of the unit, "
                     "x = (3e^(−t) + 2e^(4t))/5, y = (3e^(4t) − 3e^(−t))/5. "
                     "The second column is the trajectory through (0, 1), "
                     "which the next chapter reads off the saddle's phase "
                     "portrait."),
                Step("Check at t = 0: the columns become (1, 0) and (0, 1), the "
                     "identity. Liouville's formula gives a second check: "
                     "det e^(At) should be 1·e^(3t), since the trace of A is 3, "
                     "and multiplying out the entries confirms it."),
            ),
        ),
        Para(
            "The recipe has a standard name. When the columns of Φ are "
            "eigenvector solutions, Φ(0) is the eigenvector matrix P and Φ(t) "
            "is P times the diagonal matrix e^(Dt) of the exponentials e^(λt). "
            "So e^(At) = P e^(Dt) P⁻¹ for any diagonalisable A, which is how "
            "most textbooks state it."
        ),
        Para(
            "e^(At) is not the matrix of exponentials of the entries of A. At "
            "t = 1 the top-left entry above is (3e^(−1) + 2e^4)/5 ≈ 22.06, "
            "nothing like e¹. Only for a diagonal A is the exponential taken "
            "entry by entry."
        ),
        Worked(
            "Two exponentials that the series gives directly",
            "Compute e^(At) for A with rows (3, 1) and (0, 3), and for A with "
            "rows (0, −1) and (1, 0).",
            (
                Step("The first is the shortcut previewed in the "
                     "repeated-eigenvalues chapter, now justified by the series. "
                     "Write A = 3I + N, where N has rows (0, 1) and (0, 0). Then "
                     "N² = 0, so the series for e^(Nt) stops after two terms, and "
                     "because I commutes with N the exponential splits.",
                     r"e^{At} = e^{3t}\,(I + Nt), \qquad e^{At}\binom{1}{0} = "
                     r"e^{3t}\binom{1}{0}, \quad e^{At}\binom{0}{1} = "
                     r"e^{3t}\binom{t}{1}"),
                Step("The two columns are the solutions v·e^(3t) and "
                     "(w + tv)e^(3t) that that chapter found for "
                     "x' = 3x + y, y' = 3y, and the series explains why its "
                     "factor t appears: it is the one surviving power of N."),
                Step("For the second, the powers of A cycle with period four, "
                     "A² = −I, and the even and odd terms of the series collect "
                     "into the series for cosine and sine.",
                     r"e^{At}\binom{1}{0} = \binom{\cos t}{\sin t}, \qquad "
                     r"e^{At}\binom{0}{1} = \binom{-\sin t}{\cos t}"),
                Step("This is rotation through angle t: the solutions of "
                     "x' = −y, y' = x from the complex-eigenvalues chapter, "
                     "collected into one matrix."),
            ),
        ),
    )),
    Section("Rules for the exponential", (
        Para(
            "Several scalar rules survive. Since e^(A(t+s)) and e^(At)e^(As) "
            "both solve M' = AM as functions of t and agree at t = 0, "
            "uniqueness makes them equal; taking s = −t gives e^(At)e^(−At) = I, "
            "so the inverse of e^(At) is e^(−At), found by changing the sign "
            "of t. That is often the easiest way to get the Φ⁻¹ that "
            "variation of parameters needs."
        ),
        Display(r"e^{A(t+s)} = e^{At}e^{As}, \qquad \left(e^{At}\right)^{-1} = "
                r"e^{-At}", "6"),
        Box(
            "warning", "e^(A+B) is not e^A e^B in general",
            "The product rule for exponentials uses ab = ba, and matrices need "
            "not commute. With P having rows (0, 1), (0, 0) and Q having rows "
            "(0, 0), (1, 0), the product e^P e^Q has rows (2, 1) and (1, 1), "
            "while e^(P+Q) has rows (cosh 1, sinh 1) and (sinh 1, cosh 1). The "
            "rule holds when AB = BA, which is why 3I + N split cleanly above.",
        ),
        Para(
            "The Laplace transform of the previous unit sees e^(At) too. "
            "Transforming x' = Ax with x(0) = x₀ gives sX − x₀ = AX, so "
            "X = (sI − A)⁻¹x₀, and comparing with x = e^(At)x₀ shows that the "
            "transform of e^(At) is the inverse of sI − A. For the saddle, "
            "sI − A has determinant s² − 3s − 4 = (s − 4)(s + 1): the "
            "characteristic polynomial appears as the denominator, and its "
            "roots are the eigenvalues, just as the roots of as² + bs + c were "
            "the poles of a transfer function."
        ),
        Display(r"\mathcal{L}\{e^{At}\} = (sI - A)^{-1}", "7"),
    )),
    Section("Forcing that no guess can match", (
        Para(
            "Every forcing so far could also have been handled by undetermined "
            "coefficients, so it is fair to ask what the matrix method is for. "
            "The answer is the same as at second order: forcing such as sec t, "
            "tan t or 1/t has no finite family of derivatives, so there is "
            "nothing sensible to guess. Variation of parameters does not care "
            "what f is, as long as the integral can be done."
        ),
        Worked(
            "The rotation pushed by sec t",
            "Find the general solution of x' = −y, y' = x + sec t on "
            "−π/2 < t < π/2.",
            (
                Step("The homogeneous half is the rotation whose exponential was "
                     "found above, so take Φ = e^(At), with rows (cos t, −sin t) "
                     "and (sin t, cos t). By the rules just proved, its inverse "
                     "is found by changing the sign of t: Φ⁻¹ has rows "
                     "(cos t, sin t) and (−sin t, cos t).",
                     r"\mathbf{f}(t) = \binom{0}{\sec t}"),
                Step("Apply Φ⁻¹ to f. The first entry is sin t · sec t and the "
                     "second is cos t · sec t.",
                     r"\mathbf{u}' = \binom{\tan t}{1}"),
                Step("Integrate. The antiderivative of tan t is −ln|cos t|, and "
                     "cos t > 0 on the interval, so the absolute value can go.",
                     r"\mathbf{u} = \binom{-\ln(\cos t)}{t}"),
                Step("Multiply back by Φ.",
                     r"x_p = -\cos t\,\ln(\cos t) - t\sin t, \qquad "
                     r"y_p = -\sin t\,\ln(\cos t) + t\cos t"),
                Step("Add the homogeneous family, the two columns of Φ with "
                     "constants C₁ and C₂.",
                     r"\mathbf{x} = C_1\binom{\cos t}{\sin t} + "
                     r"C_2\binom{-\sin t}{\cos t} + \mathbf{x}_p"),
            ),
            equation="x' = -y; y' = x + sec(t)",
            answer="x = C1*cos(t) - C2*sin(t) - cos(t)*log(cos(t)) - t*sin(t)\n"
                   "y = C1*sin(t) + C2*cos(t) - sin(t)*log(cos(t)) + t*cos(t)",
            answer_latex=r"x = C_1\cos t - C_2\sin t - \cos t\,\ln(\cos t) - "
                         r"t\sin t, \quad y = C_1\sin t + C_2\cos t - "
                         r"\sin t\,\ln(\cos t) + t\cos t",
        ),
        Para(
            "Two features of the answer are out of reach of any guess. The "
            "integral produced a logarithm, a function that appears nowhere in "
            "the forcing; and the solution lives only on the interval where "
            "sec t is continuous, exactly as the existence theorem promises "
            "and no further."
        ),
    )),
    Section("The solution formula", (
        Para(
            "Put e^(At) into the variation-of-parameters theorem with t₀ = 0. "
            "Its inverse is e^(−As), and e^(At)e^(−As) = e^(A(t−s)) by the "
            "addition rule above, so the whole initial value problem is "
            "solved by one line."
        ),
        Display(r"\mathbf{x}(t) = e^{At}\mathbf{x}_0 + \int_{0}^{t}e^{A(t-s)}\,"
                r"\mathbf{f}(s)\,ds", "8"),
        Para(
            "Read it as two contributions. The first is the free motion from "
            "the initial state. The second is a convolution, exactly as in "
            "the Laplace unit: the push f(s)ds delivered at each earlier time "
            "s is carried forward for the remaining time t − s by the free "
            "dynamics, and linearity adds the results. e^(At) plays the part "
            "the impulse response w(t) played for a single equation."
        ),
        Worked(
            "The driven saddle from rest",
            "Solve x' = x + 2y + e^t, y' = 3x + 2y with x(0) = 0, y(0) = 0.",
            (
                Step("x₀ = 0, so only the integral in the solution formula "
                     "remains, and since f has only a first entry, only the "
                     "first column of e^(A(t−s)) is needed.",
                     r"\mathbf{x}(t) = \int_{0}^{t}\frac{1}{5}\binom{3e^{-(t-s)} + "
                     r"2e^{4(t-s)}}{3e^{4(t-s)} - 3e^{-(t-s)}}\,e^{s}\,ds"),
                Step("Each term is an exponential in s. For instance "
                     "∫₀ᵗ 3e^(−t+2s) ds = (3/2)(e^t − e^(−t)) and "
                     "∫₀ᵗ 2e^(4t−3s) ds = (2/3)(e^(4t) − e^t).",
                     r"x = \frac{1}{5}\left[\frac{3}{2}(e^{t} - e^{-t}) + "
                     r"\frac{2}{3}(e^{4t} - e^{t})\right]"),
                Step("The second row works the same way: ∫₀ᵗ 3e^(4t−3s) ds = "
                     "e^(4t) − e^t and ∫₀ᵗ 3e^(−t+2s) ds = (3/2)(e^t − e^(−t)).",
                     r"y = \frac{1}{5}\left[(e^{4t} - e^{t}) - "
                     r"\frac{3}{2}(e^{t} - e^{-t})\right]"),
                Step("Collect terms in both.",
                     r"x = \frac{2}{15}e^{4t} + \frac{1}{6}e^{t} - \frac{3}{10}e^{-t}, "
                     r"\quad y = \frac{1}{5}e^{4t} - \frac{1}{2}e^{t} + "
                     r"\frac{3}{10}e^{-t}"),
                Step("Check against the general solution: this is C₁ = −3/10 and "
                     "C₂ = 1/15 there, and at t = 0 both components are zero."),
            ),
            equation="x' = x + 2*y + exp(t); y' = 3*x + 2*y",
            conditions="x(0) = 0, y(0) = 0",
            answer="x = 2*exp(4*t)/15 + exp(t)/6 - 3*exp(-t)/10\n"
                   "y = exp(4*t)/5 - exp(t)/2 + 3*exp(-t)/10",
            answer_latex=r"x = \frac{2}{15}e^{4t} + \frac{e^{t}}{6} - "
                         r"\frac{3}{10}e^{-t}, \quad y = \frac{e^{4t}}{5} - "
                         r"\frac{e^{t}}{2} + \frac{3}{10}e^{-t}",
        ),
        Para(
            "The system started at the origin, the saddle point of the "
            "unforced system, and was pushed only gently, yet the answer grows "
            "like e^(4t). The forcing nudged the state off the stable line, and "
            "the unstable eigenvalue did the rest. A forced system inherits its "
            "long-term behaviour from A: forcing can move a stable system's "
            "destination, but it cannot make an unstable one settle from a "
            "typical start. With constant forcing (1, 0), for instance, the "
            "saddle has the equilibrium x* = −A⁻¹f = (1/2, −3/4), and starts on "
            "the stable line through x* do settle there; every other start "
            "still grows like e^(4t)."
        ),
    )),
    Section("Periodic forcing and the steady loop", (
        Para(
            "The most important case in applications is a stable system with "
            "periodic forcing. Then the homogeneous part decays, whatever the "
            "starting point, and what remains is a periodic particular "
            "solution, traced in the phase plane as a closed loop. Every "
            "trajectory is drawn onto the same loop, spiralling in when the "
            "eigenvalues are complex. It is the steady state of the "
            "forced-oscillations chapter, seen in the plane."
        ),
        Worked(
            "A damped oscillator as a forced system",
            "Find the general solution of x' = y, y' = −x − y + cos t, and "
            "identify the steady loop.",
            (
                Step("This is x'' + x' + x = cos t written as a system. A has rows "
                     "(0, 1) and (−1, −1): trace −1, determinant 1, eigenvalues "
                     "(−1 ± i√3)/2. A stable spiral.",
                     r"\lambda = -\frac{1}{2} \pm \frac{\sqrt{3}}{2}\,i"),
                Step("Try x_p = a cos t + b sin t with constant vectors a and b. "
                     "Both are needed even though the forcing has only a cosine, "
                     "because A mixes the components and differentiation turns "
                     "each into the other. Substituting, the cos t terms give "
                     "b = Aa + (0, 1) and the sin t terms give −a = Ab.",
                     r"\mathbf{b} = A\mathbf{a} + \binom{0}{1}, \qquad "
                     r"-\mathbf{a} = A\mathbf{b}"),
                Step("Written out, these are four scalar equations: b₁ = a₂, "
                     "b₂ = −a₁ − a₂ + 1, a₁ = −b₂ and a₂ = b₁ + b₂. The first "
                     "and fourth give b₂ = 0, then the third gives a₁ = 0, the "
                     "second gives a₂ = 1, and the first gives b₁ = 1. So "
                     "a = (0, 1) and b = (1, 0).",
                     r"\mathbf{x}_p = \binom{\sin t}{\cos t}"),
                Step("Add the homogeneous family in real form, as in the "
                     "complex-eigenvalues chapter; y is then the derivative of "
                     "x.",
                     r"x = \sin t + e^{-t/2}\left(C_1\cos\frac{\sqrt{3}}{2}t + "
                     r"C_2\sin\frac{\sqrt{3}}{2}t\right)"),
                Step("The steady loop is x_p itself: x² + y² = sin²t + cos²t = 1, "
                     "the unit circle, traversed clockwise once every 2π."),
            ),
            equation="x' = y; y' = -x - y + cos(t)",
            answer="x = sin(t) + exp(-t/2)*(C1*cos(sqrt(3)*t/2) + "
                   "C2*sin(sqrt(3)*t/2))\n"
                   "y = cos(t) + exp(-t/2)*((sqrt(3)*C2 - C1)/2*cos(sqrt(3)*t/2) "
                   "- (sqrt(3)*C1 + C2)/2*sin(sqrt(3)*t/2))",
            answer_latex=r"x = \sin t + e^{-t/2}\left(C_1\cos\frac{\sqrt{3}t}{2} + "
                         r"C_2\sin\frac{\sqrt{3}t}{2}\right), \quad y = x'",
        ),
        Plot(
            "Two starts, one loop",
            "Solutions of x' = y, y' = −x − y + cos t starting at (2, 0) and at "
            "the origin, with the steady loop, the unit circle. The transient "
            "is e^(−t/2) times an oscillation, and by t = 12 it has shrunk by a "
            "factor e^(−6) ≈ 0.0025; both trajectories are then indistinguishable "
            "from the circle.",
            (Curve("sin(t) + 2*exp(-t/2)*cos(sqrt(3)*t/2)", "from (2, 0)",
                   y="cos(t) - exp(-t/2)*(cos(sqrt(3)*t/2) + "
                     "sqrt(3)*sin(sqrt(3)*t/2))"),
             Curve("sin(t) - 2*exp(-t/2)*sin(sqrt(3)*t/2)/sqrt(3)", "from (0, 0)",
                   y="cos(t) + exp(-t/2)*(sin(sqrt(3)*t/2)/sqrt(3) - "
                     "cos(sqrt(3)*t/2))"),
             Curve("sin(t)", "steady loop", y="cos(t)")),
            t=(0.0, 12.0), xlabel="x", ylabel="y",
        ),
        Figure("forced_system",
               "The figure draws x' = y, y' = −x − 2d·y + F cos ωt, a damped "
               "spring shaken in its second equation, from three different "
               "starts. The example above is d = 1/2, F = 1, ω = 1. Lower the "
               "damping slider and the transient lingers, still visible at "
               "the end of the window; the readout reports how far apart the "
               "three final states are. Move ω towards 1 with small damping and "
               "the loop grows: its amplitude in x is F/√((1 − ω²)² + 4d²ω²), "
               "which is 2 at the default damping 0.25 with ω moved to 1, and "
               "10 at d = 0.05, well outside the window. Set the amplitude "
               "to zero and the loop collapses to the origin: with no forcing "
               "the particular solution is zero, and only the decaying "
               "transient is left."),
        Para(
            "The lesson of the figure is the structure theorem in visual "
            "form. Everything that distinguished the three starts was "
            "homogeneous, and it decayed; what is left belongs to the forcing. "
            "The closed loop here should not be confused with the *limit "
            "cycles* of the nonlinear-systems unit. Those are closed orbits "
            "that an unforced nonlinear system produces by itself; this loop "
            "exists only because something outside keeps pushing, and its "
            "size is proportional to the push."
        ),
    )),
    Section("Common errors", (
        Para(
            "The first is to put the forcing into A, or into the wrong row "
            "of f. A term with no unknown in it belongs in f, and it "
            "belongs in the row of the equation it appears in: x' = x + 2y + e^t "
            "has f = (e^t, 0), not (0, e^t). The second is to build Φ from the "
            "eigenvectors alone. The columns must be *solutions*, functions of "
            "t, so each eigenvector carries its e^(λt), and the inverse must be "
            "taken of Φ(t), not of the constant eigenvector matrix."
        ),
        Para(
            "The third is to cancel Φ against Φ⁻¹. Φ(t) outside the integral "
            "and Φ⁻¹(s) inside it are taken at different times, so Φ∫Φ⁻¹f is "
            "not ∫f, even for a single equation. And because matrices do not "
            "commute, Φ⁻¹ must stand to the left of f inside the integral, and "
            "Φ to the left of the integral outside. The fourth is to treat e^(At) as the entrywise exponential of At, and "
            "the fifth is to use e^(A+B) = e^A e^B without checking that A and "
            "B commute. The last is the resonant guess te^(λt)a without the "
            "companion term b."
        ),
    )),
    Section("Summary", (
        Para(
            "A forced linear system x' = Ax + f has general solution x_h + x_p: "
            "the homogeneous family, found by the eigenvalue methods of the "
            "earlier chapters, plus any one solution of the forced system. "
            "Collecting basis solutions as the columns of a fundamental matrix "
            "Φ, which is invertible at every t by Liouville's formula, variation "
            "of parameters gives x_p = Φ∫Φ⁻¹f dt with no side condition and no "
            "constant of integration, and it contains the scalar formula as "
            "the special case of a converted second-order equation. Constant "
            "forcing gives a displaced equilibrium x* = −A⁻¹f; exponential and "
            "trigonometric forcing can be guessed with vector coefficients, "
            "with (at + b)e^(λt) when the exponent is an eigenvalue."
        ),
        Para(
            "Among all fundamental matrices, e^(At) is the one equal to the "
            "identity at t = 0. It is defined by the exponential series, "
            "computed as Φ(t)Φ(0)⁻¹, inverted by changing the sign of t, and "
            "transformed to (sI − A)⁻¹. With it the whole problem is one "
            "line, x(t) = e^(At)x₀ + ∫₀ᵗ e^(A(t−s))f(s) ds: free motion plus a "
            "convolution with the forcing. For a stable A the free motion "
            "dies, and so does the memory of the early forcing inside the "
            "integral; the state is left tracking whatever the forcing "
            "dictates."
        ),
    )),
)


PORTRAITS = (
    Section("Formulas that hide the behaviour", (
        Para(
            "The last three chapters produced formulas. For a two-by-two "
            "system x' = Ax the eigenvalue method gives two components, each a "
            "combination of two exponentials, or of an exponential times a "
            "sine and a cosine, or of e^(λt) and te^(λt), with vector "
            "coefficients fixed by the "
            "eigenvectors and the initial values. Every such formula is "
            "correct, and very little about the behaviour it describes can be "
            "read from it. Does the solution settle down? Along which line? "
            "Does it overshoot, turn, or run away, and from which starting "
            "points?"
        ),
        Para(
            "These are the questions a designer asks, and they are questions "
            "about all solutions at once rather than about one. This chapter "
            "answers them with a picture. Instead of drawing x and y against "
            "time, it draws the path the point (x, y) traces in the plane, "
            "for many starting points together. The remarkable thing is how "
            "little the picture costs. Two numbers read straight off the "
            "matrix, its trace and its determinant, decide which of a handful "
            "of pictures it is, before any eigenvalue has been computed and "
            "long before any solution has."
        ),
    )),
    Section("The phase plane", (
        Para(
            "A solution of x' = ax + by, y' = cx + dy is a pair of functions "
            "x(t), y(t). Plotting the point (x(t), y(t)) as t runs traces a "
            "curve in the xy-plane, with time as the parameter along it. Time "
            "is no longer on an axis, so an arrow is drawn on the curve to "
            "show which way it is travelled. The right-hand side of the "
            "system is the velocity of the moving point: at every point of "
            "the plane the system says which way to go and how fast, and a "
            "solution is a curve that follows those instructions everywhere."
        ),
        Para(
            "The time can also be eliminated altogether. Dividing y' by x', "
            "a trajectory away from the line ax + by = 0 satisfies the "
            "first-order equation dy/dx = (cx + dy)/(ax + by), which gives "
            "its slope at each point without mentioning t. The slope is "
            "vertical where the denominator vanishes and horizontal where "
            "the numerator does. Those two lines, ax + by = 0 where x' = 0 "
            "and cx + dy = 0 where y' = 0, are the nullclines, and they "
            "return in the sketching routine at the end of the chapter."
        ),
        Box(
            "definition", "Trajectories and phase portraits",
            "The xy-plane of a two-dimensional system is its phase plane. The "
            "path of one solution, (x(t), y(t)) drawn as a curve with an arrow "
            "for increasing t, is a trajectory. A phase portrait is a sketch "
            "of enough trajectories to show what happens from every starting "
            "point. A point where the right-hand side vanishes is an "
            "equilibrium, or critical point: a solution starting there stays "
            "there for all time.",
            r"\mathbf{x}' = A\mathbf{x}, \qquad \mathbf{x}(t) = "
            r"\binom{x(t)}{y(t)}",
        ),
        Para(
            "Because A does not depend on t, the instructions at a point are "
            "the same at every time, and that has two consequences which "
            "shape every portrait in this chapter. First, a time-shifted "
            "solution is still a solution: if x(t) solves the system then so "
            "does x(t − t₀), and it traces the same trajectory, only later. "
            "So a trajectory is a property of the system and a point on it, "
            "not of the moment of starting. Second, trajectories cannot "
            "cross."
        ),
        Box(
            "theorem", "Trajectories do not cross",
            "Two trajectories of x' = Ax either coincide or have no point in "
            "common.",
        ),
        Box(
            "proof", "Proof",
            "Suppose one solution passes through the point p at time t₁ and "
            "another passes through p at time t₂. Shift the second in time by "
            "t₂ − t₁. The shifted function is still a solution, and it is at p "
            "at time t₁, as the first is. By the existence and uniqueness "
            "theorem for linear systems they are the same solution, so the "
            "two trajectories are the same curve.",
        ),
        Para(
            "The equilibria of x' = Ax are the solutions of Ax = 0, and the "
            "origin is always one of them. Whether it is the only one is a "
            "question about the determinant."
        ),
        Box(
            "theorem", "The origin is the only equilibrium when det A ≠ 0",
            "If det A ≠ 0 the origin is the one and only equilibrium of "
            "x' = Ax. If det A = 0 and A is not the zero matrix, there is a "
            "whole line of equilibria through the origin.",
            r"A\mathbf{x} = \mathbf{0},\ \det A \neq 0 "
            r"\;\Longrightarrow\; \mathbf{x} = A^{-1}\mathbf{0} = \mathbf{0}",
        ),
        Para(
            "So an invertible linear system is organised around a single "
            "point, and the whole portrait is a description of what happens "
            "near it, which by the scaling of a linear system is also what "
            "happens far from it. That is the first thing to stop being true "
            "for nonlinear systems, which can have several equilibria, each "
            "with its own local picture. The next unit takes up that case, and its "
            "first move is to borrow the pictures of this chapter."
        ),
    )),
    Section("Two numbers decide the picture", (
        Para(
            "Write the matrix by its entries, with rows (a, b) and (c, d). "
            "Expanding the characteristic determinant, the "
            "coefficient of λ is minus the sum of the diagonal, and the "
            "constant term is the determinant. Call these τ = tr A = a + d "
            "and Δ = det A = ad − bc."
        ),
        Display(r"\det(A - \lambda I) = (a-\lambda)(d-\lambda) - bc = "
                r"\lambda^{2} - \tau\lambda + \Delta", "1"),
        Display(r"\lambda = \frac{\tau \pm \sqrt{\tau^{2} - 4\Delta}}{2}", "2"),
        Para(
            "The characteristic polynomial depends on the matrix only "
            "through τ and Δ, and everything about the solutions comes from "
            "its roots. So the classification is, apart from the boundary "
            "case of a repeated eigenvalue and the sense of rotation, a "
            "statement about two numbers. Two quite different-looking matrices with the same "
            "trace and determinant, such as the one with rows (−2, 1), "
            "(1, −2) and the triangular one with rows (−1, 5), (0, −3), have "
            "the same eigenvalues −1 and −3 and qualitatively identical "
            "portraits, though their eigendirections point different ways."
        ),
        Box(
            "theorem", "Trace and determinant from the eigenvalues",
            "If λ₁ and λ₂ are the eigenvalues of a 2×2 matrix A, counted "
            "with multiplicity, then their sum is the trace and their product "
            "is the determinant.",
            r"\lambda_1 + \lambda_2 = \tau = \operatorname{tr}A, \qquad "
            r"\lambda_1 \lambda_2 = \Delta = \det A",
        ),
        Box(
            "proof", "Proof",
            "The characteristic polynomial is monic with roots λ₁ and λ₂, so "
            "it factors as (λ − λ₁)(λ − λ₂) = λ² − (λ₁ + λ₂)λ + λ₁λ₂. "
            "Comparing coefficients with equation 1 gives both statements.",
        ),
        Para(
            "Everything that follows is this theorem read three ways: the "
            "sign of the product, the sign of the sum, and the sign of the "
            "discriminant τ² − 4Δ, which decides whether the eigenvalues are "
            "real at all."
        ),
    )),
    Section("Saddles: a negative determinant", (
        Para(
            "Take the determinant first. If Δ < 0, the product of the "
            "eigenvalues is negative. A complex pair α ± iβ has product "
            "α² + β², which is never negative, so the eigenvalues are real, "
            "and their product can only be negative if they have opposite "
            "signs. One eigendirection carries solutions in, the other "
            "carries them out. That picture is called a saddle, and it is "
            "settled by the sign of a single number."
        ),
        Display(r"\Delta < 0 \;\Longrightarrow\; \lambda_1 < 0 < \lambda_2 "
                r"\;\;\text{(saddle)}", "3"),
        Para(
            "Along each eigendirection the motion is a straight line: a "
            "solution v e^(λt) is a fixed vector scaled by a positive "
            "number, so it stays on the line through v, moving outwards if λ "
            "is positive and inwards if λ is negative. Every other solution "
            "is a combination of the two, and the two terms pull it in "
            "different ways at different times."
        ),
        Para(
            "For a real eigenvalue with eigenvector v, the line through the "
            "origin in the direction of v is called an eigenline. Each of its "
            "two halves is a trajectory, so by the theorem that trajectories "
            "do not cross, a solution that starts on an eigenline stays on it "
            "for all time, and a solution that starts off it never lands on "
            "it. In a saddle the eigenline of the negative eigenvalue is the "
            "stable line and that of the positive one is the unstable line."
        ),
        Worked(
            "A saddle, read and then solved",
            "Classify the origin of x' = x + 2y, y' = 3x + 2y, the running "
            "example of the unit, from the trace and determinant, then find "
            "the trajectory through (0, 1) and describe it.",
            (
                Step("The matrix has rows (1, 2) and (3, 2). Its determinant is "
                     "2 − 6 = −4, negative, so the origin is a saddle. No "
                     "eigenvalue has been computed yet.",
                     r"\tau = 3, \qquad \Delta = 2 - 6 = -4 < 0"),
                Step("For the details, solve λ² − 3λ − 4 = 0: the eigenvalues "
                     "are 4 and −1, of opposite signs as promised. For "
                     "λ = 4, A − 4I has rows (−3, 2) and (3, −2); the first "
                     "row says −3v₁ + 2v₂ = 0, so v = (2, 3). For λ = −1, "
                     "A + I has rows (2, 2) and (3, 3), so v₁ + v₂ = 0 and "
                     "v = (−1, 1).",
                     r"\lambda_1 = 4,\ \mathbf{v}_1 = \binom{2}{3}, \qquad "
                     r"\lambda_2 = -1,\ \mathbf{v}_2 = \binom{-1}{1}"),
                Step("Write (0, 1) in terms of the eigenvectors: "
                     "(0, 1) = (1/5)(2, 3) + (2/5)(−1, 1). Each coefficient "
                     "then carries its own exponential.",
                     r"\mathbf{x}(t) = \frac{1}{5}\binom{2}{3}e^{4t} + "
                     r"\frac{2}{5}\binom{-1}{1}e^{-t}"),
                Step("Read it. For large negative t the e^(−t) term dominates, "
                     "so the trajectory comes in from far away along the "
                     "stable line, from the upper left. It sweeps past the "
                     "origin, crossing the y-axis at (0, 1), and for large t "
                     "the e^(4t) term takes over and carries it out towards "
                     "the upper right, parallel to (2, 3)."),
            ),
            equation="x' = x + 2*y; y' = 3*x + 2*y",
            conditions="x(0) = 0, y(0) = 1",
            answer="x = 2*exp(4*t)/5 - 2*exp(-t)/5\n"
                   "y = 3*exp(4*t)/5 + 2*exp(-t)/5",
            answer_latex=r"x = \frac{2}{5}e^{4t} - \frac{2}{5}e^{-t}, \qquad "
                         r"y = \frac{3}{5}e^{4t} + \frac{2}{5}e^{-t}",
        ),
        Para(
            "The two eigenlines divide the plane into four regions. By the "
            "theorem that trajectories do not cross, no trajectory can pass "
            "from one region to another, so the region a solution starts in "
            "decides its whole future: which way along the unstable line it "
            "eventually leaves, and which end of the stable line it came "
            "from. The stable line is a knife-edge. Starting exactly on it, "
            "a solution decays to the origin; starting anywhere else, however "
            "close, it is eventually thrown out. Lines that separate "
            "qualitatively different behaviour in this way are called "
            "separatrices."
        ),
        Plot(
            "A saddle",
            "Trajectories of x' = x + 2y, y' = 3x + 2y. The two straight lines "
            "are the eigendirections: along (2, 3) solutions run out, along "
            "(−1, 1) they run in. Every other trajectory arrives along the "
            "stable line, bends past the origin like a hyperbola, and leaves "
            "along the unstable line, staying in the region between the "
            "eigenlines where it started.",
            (Curve("2*t", "unstable line, λ = 4", y="3*t"),
             Curve("-2.5*t", "stable line, λ = −1", y="2.5*t"),
             Curve("0.04*exp(4*t) - exp(-t)", "trajectories",
                   y="0.06*exp(4*t) + exp(-t)"),
             Curve("0.04*exp(4*t) + exp(-t)", "",
                   y="0.06*exp(4*t) - exp(-t)"),
             Curve("-0.04*exp(4*t) - exp(-t)", "",
                   y="-0.06*exp(4*t) + exp(-t)"),
             Curve("-0.04*exp(4*t) + exp(-t)", "",
                   y="-0.06*exp(4*t) - exp(-t)")),
            t=(-1.0, 1.0), xlabel="x", ylabel="y", ylim=(-3.2, 3.2),
        ),
    )),
    Section("Nodes: real eigenvalues of one sign", (
        Para(
            "With a positive determinant the eigenvalues share a sign, or "
            "are a complex pair. Suppose first that they are real, which by "
            "equation 2 means τ² − 4Δ > 0 (the equal case is left to the "
            "section on boundaries). Their sum is τ, so a negative "
            "trace makes both negative and every solution decays; a positive "
            "trace makes both positive and every solution grows. The picture "
            "is a node, stable or unstable. Stability has been decided by the "
            "sign of τ, again with no eigenvalue computed."
        ),
        Display(r"\Delta > 0,\ \tau^{2} - 4\Delta > 0: \quad \tau < 0 "
                r"\text{ stable node}, \qquad \tau > 0 \text{ unstable node}", "4"),
        Para(
            "In a node the flow along both eigenlines runs the same way, "
            "both in or both out, and the interesting question is how the other "
            "trajectories arrive. The answer is a detail that is invisible in "
            "the formula and obvious in the picture."
        ),
        Box(
            "theorem", "Trajectories arrive along the slow direction",
            "Let the real eigenvalues satisfy λ₂ < λ₁ < 0, with eigenvectors "
            "v₁ and v₂. Every trajectory not on the v₂ line approaches the "
            "origin tangent to v₁, the direction of the eigenvalue nearer "
            "zero. Only the two halves of the v₂ line come in any other way.",
            r"\lambda_2 < \lambda_1 < 0,\ c_1 \neq 0:\quad "
            r"\frac{\mathbf{x}(t)}{|\mathbf{x}(t)|} \to "
            r"\pm\frac{\mathbf{v}_1}{|\mathbf{v}_1|} \text{ as } t \to \infty",
        ),
        Box(
            "proof", "Proof",
            "Write the solution as c₁v₁e^(λ₁t) + c₂v₂e^(λ₂t) and factor out "
            "the slower exponential. The bracket tends to c₁v₁ as t grows, "
            "because λ₂ − λ₁ < 0, so if c₁ ≠ 0 the direction of x(t) from the "
            "origin tends to that of ±v₁.",
            r"\mathbf{x}(t) = e^{\lambda_1 t}\left(c_1\mathbf{v}_1 + "
            r"c_2\mathbf{v}_2\,e^{(\lambda_2 - \lambda_1)t}\right)",
        ),
        Para(
            "The faster exponential dies first, and that is exactly why it "
            "does *not* dominate near the origin: by the time a trajectory "
            "gets close, the fast component has already collapsed and only "
            "the slow one is left. Far from the origin, at large negative t, "
            "the roles reverse, and trajectories come in from infinity "
            "parallel to the fast direction. So each one bends from being "
            "parallel to v₂ to being tangent to v₁."
        ),
        Worked(
            "A stable node and its direction of approach",
            "Classify the origin of x' = −2x + y, y' = x − 2y, the stable "
            "node of the eigenvalues chapter, solve it from a new start, "
            "x(0) = 2, y(0) = 0, and find the direction in which the solution "
            "reaches the origin.",
            (
                Step("Trace −4, determinant 4 − 1 = 3, discriminant "
                     "16 − 12 = 4. The determinant is positive, the trace "
                     "negative and the discriminant positive: a stable node.",
                     r"\tau = -4, \quad \Delta = 3, \quad \tau^{2} - 4\Delta = 4"),
                Step("The eigenvalues are −1 and −3. A + I has rows (−1, 1) "
                     "and (1, −1), so v₁ = v₂ and the eigenvector for −1 is "
                     "(1, 1); A + 3I has rows (1, 1) and (1, 1), so "
                     "v₁ + v₂ = 0 and the eigenvector for −3 is (1, −1). The "
                     "slow direction is (1, 1).",
                     r"\lambda_1 = -1,\ \mathbf{v}_1 = \binom{1}{1}, \qquad "
                     r"\lambda_2 = -3,\ \mathbf{v}_2 = \binom{1}{-1}"),
                Step("The starting point (2, 0) is v₁ + v₂, so both coefficients "
                     "are 1.",
                     r"\mathbf{x}(t) = \binom{1}{1}e^{-t} + \binom{1}{-1}e^{-3t}"),
                Step("The ratio y/x is (1 − e^(−2t))/(1 + e^(−2t)) = tanh t, "
                     "which is 0 at the start, about 0.76 at t = 1 and 0.96 at "
                     "t = 2, and tends to 1. The trajectory leaves (2, 0) "
                     "heading up and to the left, with velocity (−4, 2), and "
                     "turns to come into the origin along the line y = x.",
                     r"\frac{y}{x} = \tanh t \;\longrightarrow\; 1"),
            ),
            equation="x' = -2*x + y; y' = x - 2*y",
            conditions="x(0) = 2, y(0) = 0",
            answer="x = exp(-t) + exp(-3*t)\ny = exp(-t) - exp(-3*t)",
            answer_latex=r"x = e^{-t} + e^{-3t}, \qquad y = e^{-t} - e^{-3t}",
        ),
        Plot(
            "A stable node",
            "Trajectories of x' = −2x + y, y' = x − 2y, with eigenvalues −1 "
            "and −3. Far out they run parallel to the fast direction (1, −1); "
            "close in, every one of them turns to arrive along the slow "
            "direction (1, 1). Only the two halves of the fast line come in "
            "straight along it.",
            (Curve("1.3*(t - 1.85)", "slow line, λ = −1", y="1.3*(t - 1.85)"),
             Curve("1.3*(t - 1.85)", "fast line, λ = −3", y="-1.3*(t - 1.85)"),
             Curve("0.5*exp(-t) + exp(-3*t)", "trajectories",
                   y="0.5*exp(-t) - exp(-3*t)"),
             Curve("0.5*exp(-t) - exp(-3*t)", "",
                   y="0.5*exp(-t) + exp(-3*t)"),
             Curve("-0.5*exp(-t) + exp(-3*t)", "",
                   y="-0.5*exp(-t) - exp(-3*t)"),
             Curve("-0.5*exp(-t) - exp(-3*t)", "",
                   y="-0.5*exp(-t) + exp(-3*t)"),
             Curve("0.1*exp(-t) + exp(-3*t)", "",
                   y="0.1*exp(-t) - exp(-3*t)")),
            t=(-0.3, 4.0), xlabel="x", ylabel="y", ylim=(-3.0, 3.0),
        ),
        Para(
            "An unstable node is the same picture with every arrow reversed. "
            "Replacing A by −A negates both eigenvalues, keeps the "
            "eigenvectors, and runs each trajectory backwards in time. So in "
            "an unstable node trajectories *leave* the origin tangent to the "
            "slow direction, the one whose eigenvalue is nearer zero, and "
            "bend away until they run parallel to the fast one."
        ),
        Worked(
            "An unstable node",
            "Find the general solution of x' = 2x + y, y' = x + 2y and "
            "describe how trajectories leave the origin.",
            (
                Step("Trace 4, determinant 3, discriminant 16 − 12 = 4: a "
                     "positive determinant and trace with real eigenvalues, so "
                     "an unstable node.",
                     r"\tau = 4, \quad \Delta = 3, \quad \tau^{2} - 4\Delta = 4"),
                Step("The eigenvalues are 3 and 1. Found the same way, A − 3I "
                     "has rows (−1, 1) and (1, −1), giving (1, 1), and A − I "
                     "has rows (1, 1) and (1, 1), giving (1, −1).",
                     r"\mathbf{x}(t) = C_1\binom{1}{1}e^{3t} + "
                     r"C_2\binom{1}{-1}e^{t}"),
                Step("Near the origin means t large and negative, where e^t is "
                     "much bigger than e^(3t). So trajectories leave the origin "
                     "tangent to (1, −1), the slow direction, and far out, "
                     "where e^(3t) dominates, they run parallel to (1, 1)."),
            ),
            equation="x' = 2*x + y; y' = x + 2*y",
            answer="x = C1*exp(3*t) + C2*exp(t)\ny = C1*exp(3*t) - C2*exp(t)",
            answer_latex=r"x = C_1e^{3t} + C_2e^{t}, \qquad "
                         r"y = C_1e^{3t} - C_2e^{t}",
        ),
    )),
    Section("Spirals and centres: complex eigenvalues", (
        Para(
            "If τ² − 4Δ < 0 the eigenvalues are the complex pair of equation "
            "2, and their real part is τ/2. The complex-eigenvalues chapter "
            "showed what the real solutions look like: e^(αt) times sines and "
            "cosines of βt. The trigonometric factor turns the point round "
            "the origin and the exponential scales it, so trajectories are "
            "spirals, inwards if τ < 0 and outwards if τ > 0. There are no "
            "straight-line solutions at all, because there is no real "
            "eigenvector: every trajectory turns."
        ),
        Display(r"\tau^{2} - 4\Delta < 0: \quad \lambda = \frac{\tau}{2} \pm "
                r"i\,\frac{\sqrt{4\Delta - \tau^{2}}}{2}", "5"),
        Para(
            "When τ = 0 as well, the real part vanishes and nothing grows or "
            "shrinks. The trajectories close up into ellipses, travelled "
            "round for ever, and the origin is a centre. Which way a spiral or "
            "centre turns is not decided by τ and Δ, but it is easy to read "
            "off the matrix: at the point (1, 0) the velocity is (a, c), so "
            "if c > 0 trajectories cross the positive x-axis upwards and turn "
            "anticlockwise, and if c < 0 they turn clockwise."
        ),
        Worked(
            "A stable spiral",
            "Classify the origin of x' = −x − 2y, y' = 2x − y and solve with "
            "x(0) = 1, y(0) = 0.",
            (
                Step("Trace −2, determinant 1 + 4 = 5, discriminant 4 − 20 = "
                     "−16. Complex eigenvalues with negative real part: a "
                     "stable spiral. The entry c = 2 is positive, so it turns "
                     "anticlockwise.",
                     r"\lambda = \frac{-2 \pm \sqrt{-16}}{2} = -1 \pm 2i"),
                Step("A − (−1 + 2i)I has first row (−2i, −2), so v₂ = −iv₁ "
                     "and the eigenvector is v = (i, 1). Multiplying it by "
                     "the complex exponential and splitting into real and "
                     "imaginary parts, as in the complex-eigenvalues chapter, "
                     "gives two real solutions: e^(−t)(−sin 2t, cos 2t) and "
                     "e^(−t)(cos 2t, sin 2t).",
                     r"\binom{i}{1}e^{(-1+2i)t} = e^{-t}\binom{-\sin 2t}"
                     r"{\cos 2t} + i\,e^{-t}\binom{\cos 2t}{\sin 2t}"),
                Step("At t = 0 the two real solutions are (0, 1) and (1, 0). "
                     "The start (1, 0) is the second of them, so its "
                     "coefficient is 1 and the first one's is 0.",
                     r"x = e^{-t}\cos 2t, \qquad y = e^{-t}\sin 2t"),
                Step("Read it. The point is at angle 2t and distance e^(−t) "
                     "from the origin: it goes round anticlockwise once every "
                     "π time units, and each turn shrinks its distance by the "
                     "factor e^(−π) ≈ 0.043.",
                     r"x^{2} + y^{2} = e^{-2t}"),
            ),
            equation="x' = -x - 2*y; y' = 2*x - y",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = exp(-t)*cos(2*t)\ny = exp(-t)*sin(2*t)",
            answer_latex=r"x = e^{-t}\cos 2t, \qquad y = e^{-t}\sin 2t",
        ),
        Worked(
            "A centre, and what it conserves",
            "Classify the origin of x' = y, y' = −4x, solve with x(0) = 1, "
            "y(0) = 0, and show that the trajectories are ellipses.",
            (
                Step("This is the undamped oscillator y'' + 4y = 0 that the "
                     "first chapter of the unit converted, now started from "
                     "rest at displacement 1. "
                     "Trace 0, determinant 0 − (−4) = 4. The eigenvalues are "
                     "±2i, purely imaginary: a centre. Here c = −4 < 0, so "
                     "the motion is clockwise.",
                     r"\lambda^{2} + 4 = 0, \qquad \lambda = \pm 2i"),
                Step("A − 2iI has first row (−2i, 1), so v₂ = 2iv₁ and the "
                     "eigenvector for 2i is (1, 2i). The real part of "
                     "(1, 2i)e^(2it) is (cos 2t, −2 sin 2t), which already "
                     "starts at (1, 0). (More directly: x'' = y' = −4x, so "
                     "x = cos 2t, and then y = x' = −2 sin 2t.)",
                     r"x = \cos 2t, \qquad y = -2\sin 2t"),
                Step("For any solution the quantity 4x² + y² is constant, since "
                     "its derivative is 8xx' + 2yy' = 8xy − 8xy = 0. So every "
                     "trajectory lies on an ellipse 4x² + y² = constant; this "
                     "one has constant 4, with semi-axes 1 and 2. "
                     "Equivalently, the slope equation dy/dx = −4x/y "
                     "separates to y dy = −4x dx, whose integral is the same "
                     "family 4x² + y² = C.",
                     r"\frac{d}{dt}\left(4x^{2} + y^{2}\right) = 8xy + "
                     r"2y(-4x) = 0"),
            ),
            equation="x' = y; y' = -4*x",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = cos(2*t)\ny = -2*sin(2*t)",
            answer_latex=r"x = \cos 2t, \qquad y = -2\sin 2t",
        ),
        Plot(
            "A spiral and a centre",
            "Two systems on one set of axes. The spiral is the trajectory of "
            "x' = −x − 2y, y' = 2x − y through (1, 0), drawn from t = −1: "
            "it winds anticlockwise into the origin. The ellipse is the "
            "trajectory of x' = y, y' = −4x through (1, 0), which closes up "
            "and is travelled clockwise for ever. Its semi-axes are 1 along x "
            "and 2 along y; the two axes are drawn to different scales, so "
            "its proportions on screen are not its true ones.",
            (Curve("exp(-t)*cos(2*t)", "stable spiral", y="exp(-t)*sin(2*t)"),
             Curve("cos(2*t)", "centre", y="-2*sin(2*t)")),
            t=(-1.0, 6.0), xlabel="x", ylabel="y", ylim=(-2.8, 2.8),
        ),
        Para(
            "The centre deserves a warning in advance. It sits on the "
            "boundary τ = 0 between two open regions, inward spirals and "
            "outward spirals, and the smallest change to the matrix that "
            "makes τ nonzero turns every closed orbit into a spiral. When "
            "the next unit approximates nonlinear systems by linear ones, that "
            "fragility is exactly why a linearisation that predicts a centre "
            "decides nothing."
        ),
    )),
    Section("The trace–determinant plane", (
        Para(
            "Collecting the cases gives a map. Plot τ horizontally and Δ "
            "vertically, so that every 2×2 matrix is a point. The τ-axis, "
            "where Δ = 0, and the parabola τ² = 4Δ, where the eigenvalues "
            "are repeated, divide the plane into the regions below."
        ),
        Box(
            "theorem", "Classification by trace and determinant",
            "For x' = Ax with τ = tr A and Δ = det A: if Δ < 0 the origin is "
            "a saddle. If Δ > 0 and τ² > 4Δ it is a node, stable when τ < 0 "
            "and unstable when τ > 0. If Δ > 0 and τ² < 4Δ it is a spiral, "
            "stable when τ < 0 and unstable when τ > 0, or a centre when "
            "τ = 0. The boundary cases are Δ = 0 with A ≠ 0, a line of "
            "equilibria, and τ² = 4Δ, a repeated eigenvalue.",
            r"\Delta < 0 \text{ saddle}; \quad \Delta > 0:\ \tau^{2} "
            r"\gtrless 4\Delta \text{ node or spiral}, \ \operatorname{sign}\tau "
            r"\text{ decides stability}",
        ),
        Para(
            "The names vary between books. Many texts, including Edwards, call "
            "an asymptotically stable node or spiral a sink (a nodal sink or "
            "spiral sink) and an unstable one a source (a nodal source or "
            "spiral source). A repeated eigenvalue gives a proper node, also "
            "called a star, or an improper node, which this chapter also "
            "calls degenerate."
        ),
        Plot(
            "Where each picture lives",
            "The trace–determinant plane. Below the τ-axis every matrix gives "
            "a saddle. Above it, the parabola Δ = τ²/4 separates nodes "
            "(between the parabola and the axis) from spirals (above the "
            "parabola); the left half is stable and the right half unstable, "
            "and the positive Δ-axis between the two spiral regions is where "
            "the centres lie.",
            (Curve("t**2/4", "τ² = 4Δ"),
             Curve("t", "Δ = 0", y="0*t"),
             Curve("0*t", "centres", y="t + 4")),
            t=(-4.0, 4.0), xlabel="τ = tr A", ylabel="Δ = det A",
            ylim=(-2.0, 5.0),
        ),
        Para(
            "The regions are open sets, and a matrix inside one of them can "
            "be changed a little without changing its picture. That is what "
            "makes the classification robust: a saddle measured with small "
            "errors in its coefficients is still a saddle. The boundaries are "
            "the opposite. A matrix on the τ-axis, on the parabola or on the "
            "centre line can be pushed into different regions by arbitrarily "
            "small changes, and those are the cases in which the details of "
            "a model, and not just its broad shape, decide the answer."
        ),
    )),
    Section("On the boundaries", (
        Para(
            "On the parabola τ² = 4Δ the eigenvalue τ/2 is repeated. The "
            "repeated-eigenvalues chapter showed that two things can then "
            "happen. If A is a multiple of the identity, every direction is "
            "an eigendirection and every trajectory is a straight ray into "
            "or out of the origin, a *proper* node or star. Otherwise A is "
            "defective, there is one eigendirection only, and the solutions "
            "(w + tv)e^(λt) all arrive tangent to that one line, turning as "
            "they do: a *degenerate* or improper node, the picture halfway "
            "between a node and a spiral."
        ),
        Para(
            "On the τ-axis away from the origin (Δ = 0, τ ≠ 0), one "
            "eigenvalue is zero. Its eigendirection is then a line of "
            "equilibria, and the other eigenvalue is τ. Solutions have the "
            "form c₁v₀ + c₂v e^(τt), where v₀ spans the line of equilibria "
            "and v is the eigenvector for τ: every trajectory is a straight "
            "half-line parallel to v, moving towards the line of equilibria "
            "if τ < 0 and away from it if τ > 0. This is the picture of an "
            "eigenvalue caught in the act of changing sign, and it is the "
            "transition between a node and a saddle. If τ = 0 as well, both "
            "eigenvalues are 0. Then either A = 0 and every point is an "
            "equilibrium, or A is defective and the solutions x₀ + tAx₀ run "
            "along straight lines parallel to the line of equilibria at "
            "constant speed, in opposite directions on its two sides, never "
            "approaching it or leaving it. For x' = y, y' = 0, for instance, "
            "the solutions are x = x₀ + y₀t, y = y₀: the x-axis is at rest, "
            "points above it slide right and points below it slide left."
        ),
        Worked(
            "An eigenvalue crossing zero",
            "For which values of k is the origin of x' = −2x + y, "
            "y' = x + ky a saddle, and for which is it a node? Describe the "
            "portrait at the "
            "value that separates them.",
            (
                Step("The trace and determinant depend on k.",
                     r"\tau = k - 2, \qquad \Delta = -2k - 1"),
                Step("The discriminant is (k − 2)² + 4(2k + 1) = k² + 4k + 8 "
                     "= (k + 2)² + 4, which is always positive: whatever k is, "
                     "the eigenvalues are real, so no value of k gives a "
                     "spiral.",
                     r"\tau^{2} - 4\Delta = (k+2)^{2} + 4 > 0"),
                Step("Δ < 0 exactly when k > −1/2: a saddle. For k < −1/2, "
                     "Δ > 0 and τ = k − 2 < 0, so the origin is a stable "
                     "node. At k = 0, for instance, the eigenvalues are "
                     "−1 ± √2, about 0.41 and −2.41: a saddle."),
                Step("At k = −1/2 the eigenvalues are 0 and −5/2. The first "
                     "equation gives y = 2x, and the second, x − y/2 = 0, gives "
                     "the same line, which is a line of equilibria. Every "
                     "other solution runs straight in along the direction "
                     "(−2, 1) of the eigenvalue −5/2 and stops on it.",
                     r"k = -\frac{1}{2}: \quad \lambda = 0,\ -\frac{5}{2}"),
                Step("So as k increases through −1/2, the slow eigenvalue of "
                     "the stable node rises through zero and becomes positive. "
                     "Its direction turns from the one every trajectory "
                     "arrived along into the one along which every "
                     "trajectory off the stable line eventually leaves, and "
                     "the node becomes a saddle."),
            ),
        ),
        Figure("eigenlines",
               "The figure starts at the saddle of the first worked example, "
               "rows (1, 2) and (3, 2), with the readout giving λ = 4 and −1. "
               "Drag c, the entry in row 2, column 1, slowly down from 3. "
               "The trace stays 3 while the determinant 2 − 2c rises, and at "
               "c = 1 it reaches zero: one eigenvalue is 0 and its eigenline, "
               "along (2, −1), becomes a line of equilibria, drawn grey and "
               "without an arrow because every point on it is at rest. Below "
               "c = 1 both eigenvalues are positive and the "
               "saddle has become an unstable node. Keep going: between "
               "c = −0.12 and c = −0.13 (the exact value is −1/8, where the "
               "discriminant 8c + 1 is zero, and the slider steps over it) the "
               "two lines swing together and merge, and below that they "
               "vanish and the curves begin to turn: an unstable spiral. Stop "
               "at c = −1, where the readout gives λ = 1.50 ± 1.32i, and drag "
               "d down from 2. The determinant d + 2 stays positive while the "
               "trace 1 + d falls; at d = −1 it is zero and the eigenvalues "
               "are ±i, a centre. Each drawn curve is then an arc of a closed "
               "ellipse, travelled without growing or shrinking (the arcs "
               "are a little shorter than a full turn), and the readout names "
               "the origin a centre. Just below d = −1 the curves spiral in."),
    )),
    Section("It is the damping picture again", (
        Para(
            "Unit 4 classified the free motion of m x'' + c x' + k x = 0 by "
            "the discriminant c² − 4mk into overdamped, critically damped and "
            "underdamped motion. The phase plane contains that "
            "classification. Convert the equation to a system in the way the "
            "first chapter of this unit did, with y = x' the velocity."
        ),
        Display(r"x' = y, \qquad y' = -\frac{k}{m}\,x - \frac{c}{m}\,y", "6"),
        Para(
            "The matrix has rows (0, 1) and (−k/m, −c/m), so its trace is "
            "−c/m and its determinant is k/m. For a physical system with "
            "m, k > 0 the determinant is positive, so the origin is never a "
            "saddle; positive damping makes the trace negative, so it is "
            "stable. And the discriminant of the phase-plane classification "
            "is the old one divided by m²."
        ),
        Display(r"\tau^{2} - 4\Delta = \frac{c^{2}}{m^{2}} - \frac{4k}{m} = "
                r"\frac{c^{2} - 4mk}{m^{2}}", "7"),
        Para(
            "So the two classifications are one. Overdamped motion is a "
            "stable node, critical damping is a degenerate node on the "
            "parabola, underdamped motion is a stable spiral, and undamped "
            "motion is a centre. Holding m and k fixed and raising c moves "
            "the point (τ, Δ) = (−c/m, k/m) leftwards along a horizontal "
            "line, from the centre line, across the spiral region, through "
            "the parabola at c² = 4mk, and into the nodes. The spiral in the "
            "phase plane is the decaying oscillation against time: each turn "
            "round the origin is one swing of the mass."
        ),
        Worked(
            "An overdamped oscillator in the phase plane",
            "Write x'' + 4x' + 3x = 0 as a system with y = x', solve it with "
            "x(0) = 0, y(0) = 2, a mass kicked from its rest position, and say "
            "how the trajectory approaches the origin.",
            (
                Step("The system is x' = y, y' = −3x − 4y. Its trace is −4 and "
                     "determinant 3, with discriminant 16 − 12 = 4 > 0: a "
                     "stable node, which is the overdamped case c² > 4mk.",
                     r"\tau = -4, \quad \Delta = 3, \quad \tau^{2} - 4\Delta = 4"),
                Step("The eigenvalues are −1 and −3, the roots of "
                     "r² + 4r + 3 = 0 from Unit 4. A + I has rows (1, 1) and "
                     "(−3, −3) and A + 3I has rows (3, 1) and (−3, −1), so the "
                     "eigenvectors are (1, −1) and (1, −3): on an eigenline "
                     "of this system "
                     "the velocity is always λ times the position.",
                     r"\lambda_1 = -1,\ \mathbf{v}_1 = \binom{1}{-1}, \qquad "
                     r"\lambda_2 = -3,\ \mathbf{v}_2 = \binom{1}{-3}"),
                Step("Fitting the start (0, 2) = v₁ − v₂ gives the solution. "
                     "Its first component is the familiar overdamped motion, "
                     "and the second is its derivative.",
                     r"x = e^{-t} - e^{-3t}, \qquad y = -e^{-t} + 3e^{-3t}"),
                Step("The slow direction is (1, −1), so the trajectory arrives "
                     "along the line y = −x: late in the motion the velocity "
                     "is minus the displacement. The trajectory leaves (0, 2) "
                     "with velocity (2, −8), so it heads right and steeply "
                     "down; x reaches its largest value, 2√3/9 ≈ 0.38, at "
                     "t = (ln 3)/2 ≈ 0.55, where the curve crosses the x-axis. "
                     "Since x = e^(−t)(1 − e^(−2t)) is positive for all t > 0, "
                     "the trajectory never comes back across the y-axis, which "
                     "is the phase-plane form of the statement that this mass "
                     "never passes through equilibrium again."),
            ),
            equation="x' = y; y' = -3*x - 4*y",
            conditions="x(0) = 0, y(0) = 2",
            answer="x = exp(-t) - exp(-3*t)\ny = -exp(-t) + 3*exp(-3*t)",
            answer_latex=r"x = e^{-t} - e^{-3t}, \qquad y = -e^{-t} + 3e^{-3t}",
        ),
        Para(
            "Keep the damping and stiffen the spring from k = 3 to k = 4. Now "
            "c² = 4mk, the point (τ, Δ) has risen straight up from (−4, 3) to "
            "(−4, 4) on the parabola, the two eigenvalues of the overdamped node have "
            "merged at −2, and the node has lost one of its eigenlines."
        ),
        Worked(
            "Critical damping: a degenerate node",
            "Write x'' + 4x' + 4x = 0 as a system with y = x', solve it with "
            "x(0) = 0, y(0) = 1, and describe how the trajectory reaches the "
            "origin.",
            (
                Step("The system is x' = y, y' = −4x − 4y. Its trace is −4 and "
                     "its determinant 4, so τ² − 4Δ = 16 − 16 = 0: the point is "
                     "on the parabola, which is the critical case "
                     "c² = 4mk = 16.",
                     r"\tau = -4, \quad \Delta = 4, \quad \tau^{2} - 4\Delta = 0"),
                Step("The eigenvalue τ/2 = −2 is repeated. A + 2I has rows "
                     "(2, 1) and (−4, −2), so 2v₁ + v₂ = 0 and the only "
                     "eigendirection is v = (1, −2). A is not a multiple of "
                     "the identity, so it is defective and the origin is a "
                     "degenerate node.",
                     r"\lambda = -2 \text{ (twice)}, \qquad "
                     r"\mathbf{v} = \binom{1}{-2}"),
                Step("As in the repeated-eigenvalues chapter, solve "
                     "(A + 2I)w = v. Its first row reads 2w₁ + w₂ = 1, and "
                     "w = (0, 1) will do. The general solution is "
                     "C₁v e^(−2t) + C₂(w + tv)e^(−2t), and the start (0, 1) is "
                     "w itself, so C₁ = 0 and C₂ = 1.",
                     r"\mathbf{x}(t) = \left(\binom{0}{1} + "
                     r"t\binom{1}{-2}\right)e^{-2t}"),
                Step("Read it. The ratio y/x = 1/t − 2 is −1 at t = 1, −1.5 at "
                     "t = 2 and −1.75 at t = 4, and tends to −2. So the "
                     "trajectory leaves (0, 1) heading right and down, with "
                     "velocity (1, −4), reaches its largest x, e^(−1)/2 ≈ 0.18, "
                     "at t = 1/2, and turns to come into the origin along the "
                     "one eigenline y = −2x. Since x = te^(−2t) stays positive "
                     "for t > 0, the mass again never passes back through "
                     "equilibrium.",
                     r"\frac{y}{x} = \frac{1}{t} - 2 \;\longrightarrow\; -2"),
            ),
            equation="x' = y; y' = -4*x - 4*y",
            conditions="x(0) = 0, y(0) = 1",
            answer="x = t*exp(-2*t)\ny = (1 - 2*t)*exp(-2*t)",
            answer_latex=r"x = te^{-2t}, \qquad y = (1 - 2t)e^{-2t}",
        ),
        Plot(
            "A degenerate node",
            "Trajectories of x' = y, y' = −4x − 4y, the critically damped "
            "oscillator, through (1, 0), (0, 1), (−1, 0) and (0, −1). There is "
            "only one straight line of solutions, y = −2x, and every other "
            "trajectory turns as it goes in until it arrives tangent to it. "
            "The turning is what places this picture between a node and a "
            "spiral: a little less damping, or a little more stiffness, and "
            "the curves would keep turning round the origin.",
            (Curve("0.3*(t - 3.75)", "eigenline, λ = −2",
                   y="-0.6*(t - 3.75)"),
             Curve("(1 + 2*t)*exp(-2*t)", "trajectories", y="-4*t*exp(-2*t)"),
             Curve("t*exp(-2*t)", "", y="(1 - 2*t)*exp(-2*t)"),
             Curve("-(1 + 2*t)*exp(-2*t)", "", y="4*t*exp(-2*t)"),
             Curve("-t*exp(-2*t)", "", y="(2*t - 1)*exp(-2*t)")),
            t=(-0.2, 8.0), xlabel="x", ylabel="y", ylim=(-2.6, 2.6),
        ),
    )),
    Section("Sketching a portrait by hand", (
        Para(
            "Put together, the chapter gives a routine for sketching a "
            "portrait with very little computation. It is worth doing by "
            "hand a few times, because each step checks the one before."
        ),
        Para(
            "First, compute τ and Δ and name the picture from the "
            "classification theorem. Second, if the eigenvalues are real, "
            "find the eigenvectors and draw the eigenlines through the "
            "origin, with arrows inwards for a negative eigenvalue and "
            "outwards for a positive one. Third, draw the nullclines: the "
            "line ax + by = 0, where x' = 0 and trajectories cross "
            "vertically, and the line cx + dy = 0, where y' = 0 and they "
            "cross horizontally. Checking the sign of x' and y' in the "
            "regions between them shows which way the flow runs there. "
            "Fourth, fill in trajectories that never cross each other or the "
            "eigenlines, following the tangency rules: for a node, tangent to "
            "the slow direction at the origin and parallel to the fast one "
            "far away; for a saddle, asymptotic to the stable line in the "
            "past and to the unstable line in the future; for a spiral, "
            "turning in the sense given by the sign of c."
        ),
        Para(
            "For the saddle x' = x + 2y, y' = 3x + 2y, the nullclines are "
            "y = −x/2, where trajectories cross vertically, and y = −3x/2, "
            "where they cross horizontally; the stable line y = −x runs "
            "between them. Above both nullclines x' and y' are both positive "
            "(at (0, 1) the velocity is (2, 2)), so the flow runs up and to "
            "the right; below both it runs down and to the left. In the two "
            "thin wedges between the nullclines x' and y' have opposite "
            "signs: at (1, −1) the velocity is (−1, 1), straight back "
            "towards the origin, as it must be on the stable line. The point "
            "(0, 1), the starting point of the first worked example, lies in "
            "the upper region, which is why that trajectory was found to be "
            "leaving up and to the right."
        ),
    )),
    Section("Stability", (
        Para(
            "The portraits sort themselves into those in which solutions "
            "stay near the origin and those in which some run away. The "
            "words for this are worth making precise, because the next unit uses "
            "them for systems that cannot be solved at all."
        ),
        Box(
            "definition", "Stability of an equilibrium",
            "An equilibrium is stable if, for any prescribed distance, every "
            "solution that starts close enough to it (how close depending on "
            "that distance) stays within that distance of it for all later "
            "time. It is asymptotically stable if in addition every "
            "solution that starts close enough tends to it as t → ∞. It is "
            "unstable if it is not stable.",
        ),
        Box(
            "theorem", "Stability of x' = Ax from τ and Δ",
            "Suppose det A ≠ 0. The origin is asymptotically stable exactly "
            "when τ < 0 and Δ > 0. It is stable but not asymptotically "
            "stable when τ = 0 and Δ > 0, a centre, and unstable otherwise.",
            r"\text{asymptotically stable} \;\Longleftrightarrow\; "
            r"\operatorname{tr}A < 0 \text{ and } \det A > 0",
        ),
        Box(
            "proof", "Proof",
            "Every solution decays exactly when both eigenvalues have negative "
            "real part. If they are real, that means both negative, which by "
            "the sum-and-product theorem is λ₁ + λ₂ < 0 and λ₁λ₂ > 0. If they "
            "are a complex pair, the real part is τ/2, so it means τ < 0; and "
            "a complex pair always has Δ = α² + β² > 0. A centre keeps each "
            "solution on a fixed ellipse, which stays close but never "
            "decays, and in every remaining case some eigenvalue has "
            "positive real part and its solution grows.",
        ),
        Para(
            "In the trace–determinant plane the asymptotically stable "
            "matrices fill the whole open quadrant τ < 0, Δ > 0, nodes and "
            "spirals together. So a linear system whose coefficients are "
            "known only approximately can still be certified stable, as long "
            "as its point is not on the edge of that quadrant."
        ),
    )),
    Section("Common errors", (
        Box(
            "warning", "The fast direction is not the approach direction",
            "In a stable node with eigenvalues −1 and −5, most trajectories "
            "arrive along the −1 eigendirection, not the −5 one. The faster "
            "component is the first to vanish, which is why it is not what "
            "remains near the origin.",
        ),
        Para(
            "Other errors recur. The first is to name the picture from the "
            "trace alone. A zero trace suggests a centre, but the matrix with "
            "rows (1, 4) and (2, −1) has trace zero and determinant −9; its "
            "eigenvalues are ±3 and the origin is a saddle. Likewise a "
            "negative trace means nothing about stability until the "
            "determinant is known to be positive. The determinant is always "
            "checked first. The second is to add the off-diagonal product "
            "instead of subtracting it: det A is ad − bc. The third is to "
            "expect straight-line solutions in a spiral; with complex "
            "eigenvalues there are none, and every line through the origin "
            "is crossed by the flow. The fourth is to treat every line "
            "through the origin as invariant in a saddle or in a node with two "
            "distinct eigenvalues. Only the eigendirections are (in a star, "
            "every direction is one), which is precisely what makes them "
            "worth drawing."
        ),
    )),
    Section("Summary", (
        Para(
            "A phase portrait draws the trajectories of x' = Ax in the "
            "phase plane, where they cannot cross, and for invertible A they "
            "are organised around the single equilibrium at the origin. The "
            "characteristic polynomial is λ² − τλ + Δ, so the trace τ and "
            "determinant Δ decide the picture: Δ < 0 is a saddle; Δ > 0 with "
            "τ² > 4Δ is a node and with τ² < 4Δ a spiral, stable or unstable "
            "by the sign of τ, and a centre when τ = 0. Real eigendirections "
            "are the only straight-line trajectories; in a node the others "
            "arrive tangent to the slow direction; in a saddle they sweep "
            "past between the stable and unstable lines. When an eigenvalue "
            "crosses zero, the determinant does too, and a node turns into a "
            "saddle through a line of equilibria. For a mass on a spring "
            "the same classification is the damping classification of "
            "Unit 4. The previous chapter added a forcing term to x' = Ax, "
            "and the portraits drawn here describe the part of every forced "
            "solution that the forcing does not decide. The nonlinear unit "
            "takes them further: near an equilibrium, a nonlinear system "
            "usually looks like one of these."
        ),
    )),
)
