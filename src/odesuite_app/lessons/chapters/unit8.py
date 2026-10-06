"""Unit 8 chapters -- nonlinear systems and phenomena (Edwards ch. 6).

The file is unit8 after the lesson module; the course teaches this unit
seventh, before series, which is why the prose names units rather than
numbering them.
"""

from __future__ import annotations

from ..chapter import Box, Curve, Display, Figure, Para, Plot, Section, Step, Worked

__all__ = ["EQUILIBRIA", "ALMOST_LINEAR", "ECOLOGY", "MECHANICS", "CYCLES", "BIFURCATIONS"]


EQUILIBRIA = (
    Section("Where superposition ends", (
        Para(
            "A pendulum of length L swinging without friction obeys "
            "θ'' + (g/L) sin θ = 0, and choosing the unit of time so that "
            "g/L = 1 leaves x'' + sin x = 0, with x the angle from the "
            "downward vertical. It looks harmless, and it is the end of "
            "everything the course has built so far. Characteristic roots, "
            "undetermined coefficients, eigenvectors, the Laplace transform: "
            "every one of those methods rests on superposition, the fact that "
            "a sum of solutions is a solution. The sine destroys that. "
            "sin(x₁ + x₂) is not sin x₁ + sin x₂, so two pendulum motions "
            "cannot be added to make a third, and there is no formula for the "
            "motion in terms of the functions a first course has met. For "
            "most nonlinear systems there is no formula at all."
        ),
        Para(
            "What survives is the question a formula was only ever a means "
            "to: what does the system *do*? Where can it sit still? If it is "
            "nudged away from rest, does it come back, run away, or circle? "
            "Those questions have answers that need no solving, and this "
            "chapter gives the first two steps of the method the whole unit "
            "uses to find them."
        ),
        Para(
            "The first step is algebra. A state in which every rate is zero "
            "is an equilibrium, and finding the equilibria means setting the "
            "right-hand sides to zero and solving. The pendulum has two kinds, "
            "hanging straight down and balanced straight up, and everybody "
            "already knows that they behave completely differently. The "
            "second step is the idea the unit rests on. Very close to an "
            "equilibrium the nonlinear terms are tiny compared with the "
            "linear ones, so there the system behaves almost exactly like a "
            "linear system, and linear systems were solved completely in "
            "Unit 6. Linearising turns one hard question into several easy "
            "ones, one per equilibrium, and the picture of the whole system "
            "is assembled from the pieces."
        ),
    )),
    Section("Autonomous systems in the plane", (
        Para(
            "The systems of this unit have two unknowns, x(t) and y(t), and "
            "right-hand sides that may be any smooth functions of them. They "
            "are autonomous: the time t does not appear on the right."
        ),
        Display(r"x' = f(x, y), \qquad y' = g(x, y)", "1"),
        Para(
            "A second-order equation x'' = F(x, x') becomes a system of this "
            "form exactly as in Unit 6, by naming the velocity y = x'. The "
            "pendulum x'' + sin x = 0 becomes x' = y, y' = −sin x, and with "
            "a damping force proportional to the velocity, x'' + cx' + sin x "
            "= 0, it becomes x' = y, y' = −sin x − cy. The plane of the pair "
            "(x, y) is the phase plane, as it was in the phase-portraits "
            "chapter of Unit 6, and a solution traces a trajectory in it."
        ),
        Para(
            "Autonomy is what makes one picture describe every solution at "
            "once. Because f and g do not depend on t, the velocity the "
            "system prescribes at a point is the same whenever the point is "
            "visited, and a solution shifted in time is still a solution. "
            "So, exactly as for x' = Ax, a trajectory belongs to the system "
            "and a point on it, not to the moment of starting. The argument "
            "that trajectories cannot cross also carries over, with one new "
            "hypothesis: the existence and uniqueness theorem for nonlinear "
            "systems needs f and g to have continuous first partial "
            "derivatives, which every system in this unit has."
        ),
        Box(
            "theorem", "Trajectories do not cross",
            "If f and g have continuous first partial derivatives, then "
            "through each point of the phase plane passes exactly one "
            "trajectory of system 1. Two trajectories either coincide or have "
            "no point in common.",
        ),
        Box(
            "proof", "Proof",
            "Exactly as in the phase-portraits chapter. If two solutions pass "
            "through the same point at times t₁ and t₂, shift the second by "
            "t₂ − t₁. Autonomy makes the shifted function a solution, it "
            "agrees with the first at time t₁, and uniqueness makes them the "
            "same solution, so the two trajectories are one curve.",
        ),
    )),
    Section("Equilibria are algebra", (
        Para(
            "A constant function x(t) = x*, y(t) = y* has zero derivatives, "
            "so it solves system 1 exactly when both right-hand sides vanish "
            "at the point (x*, y*). That is two equations in two unknowns and "
            "nothing to integrate."
        ),
        Box(
            "definition", "Equilibrium",
            "A point (x*, y*) at which f and g both vanish is an equilibrium "
            "(also called a critical point, or fixed point) of system 1. The "
            "constant function sitting at it is a solution, and every "
            "constant solution arises this way.",
            r"f(x^{*}, y^{*}) = 0 \quad\text{and}\quad g(x^{*}, y^{*}) = 0",
        ),
        Para(
            "Geometrically, the curve f = 0 is where x' = 0, so trajectories "
            "cross it vertically, and the curve g = 0 is where y' = 0, so they "
            "cross it horizontally. These two curves are the nullclines, and "
            "the equilibria are exactly the points where a curve of the first "
            "kind meets a curve of the second. For a linear system with "
            "det A ≠ 0 the nullclines were two lines through the origin, "
            "which meet once. Nonlinear nullclines are curves, and curves can "
            "meet any number of times: a nonlinear system may have no "
            "equilibrium, several, or infinitely many."
        ),
        Para(
            "All three happen in simple examples. The pendulum x' = y, "
            "y' = −sin x needs y = 0 and sin x = 0, so it has an equilibrium "
            "at every (kπ, 0), k an integer: infinitely many, although "
            "physically only two, since angles differing by 2π are the same "
            "position. The system x' = 1 + y², y' = x has none, because "
            "1 + y² is never zero. And the system x' = y − x², y' = x − y, "
            "which serves as a running example in this chapter, has exactly "
            "two."
        ),
        Worked(
            "Two nullclines, two equilibria",
            "Find every equilibrium of x' = y − x², y' = x − y, and describe "
            "the nullclines.",
            (
                Step("The x-nullcline is y − x² = 0, the parabola y = x², where "
                     "trajectories cross vertically. The y-nullcline is "
                     "x − y = 0, the line y = x, where they cross "
                     "horizontally.",
                     r"x' = 0:\ y = x^{2}, \qquad y' = 0:\ y = x"),
                Step("Both must hold at once. Substituting y = x from the "
                     "second into the first gives x − x² = 0, so x(1 − x) = 0 "
                     "and x = 0 or x = 1. Each value of x gives y = x.",
                     r"x - x^{2} = x(1 - x) = 0"),
                Step("So there are two equilibria, (0, 0) and (1, 1), the two "
                     "points where the line meets the parabola. A quick check "
                     "in the original system: at (1, 1), x' = 1 − 1 = 0 and "
                     "y' = 1 − 1 = 0.",
                     r"(x^{*}, y^{*}) = (0, 0) \quad\text{and}\quad (1, 1)"),
            ),
        ),
        Plot(
            "Nullclines of the running example",
            "The nullclines of x' = y − x², y' = x − y. On the parabola "
            "y = x² the flow is vertical; on the line y = x it is horizontal. "
            "They meet at (0, 0) and (1, 1), and those two crossings are the "
            "only equilibria the system has. In each region between the "
            "curves, x' and y' keep fixed signs: above both, for instance "
            "at (0, 1), the velocity is (1, −1), down and to the right.",
            (Curve("t", "x' = 0:  y = x²", y="t**2"),
             Curve("t", "y' = 0:  y = x", y="t")),
            t=(-1.2, 1.8), xlabel="x", ylabel="y", ylim=(-1.3, 2.4),
        ),
        Para(
            "The algebra is not always as kind. Solving f = 0 for one "
            "variable and substituting into g = 0 is the general move, and "
            "it can produce a polynomial of high degree, or an equation "
            "involving a sine that must be solved numerically. The Phase "
            "Portrait screen of this application finds equilibria "
            "numerically, by Newton's method started from a grid of points "
            "across the window, and marks each one it finds. It is a good "
            "check on hand algebra, and a necessary one when the algebra "
            "cannot be finished."
        ),
    )),
    Section("Near an equilibrium: the Taylor step", (
        Para(
            "Now fix an equilibrium (x*, y*) and ask what happens close to "
            "it. Measure position from the equilibrium, writing "
            "x = x* + u and y = y* + v, so that u and v are small. Since x* "
            "and y* are constants, u' = x' and v' = y', and the system in the "
            "new variables is exact:"
        ),
        Display(r"u' = f(x^{*} + u, y^{*} + v), \qquad "
                r"v' = g(x^{*} + u, y^{*} + v)", "2"),
        Para(
            "Expand each right-hand side in a Taylor series about the "
            "equilibrium. The constant term f(x*, y*) is zero, because the "
            "point is an equilibrium, so the expansion begins with the first "
            "derivatives, and what follows them involves u², uv and v², which "
            "are smaller still when u and v are small."
        ),
        Display(r"f(x^{*} + u, y^{*} + v) = f_x u + f_y v + "
                r"O(u^{2} + v^{2})", "3"),
        Para(
            "Here f_x and f_y are the partial derivatives evaluated at "
            "(x*, y*), so they are numbers. The same expansion for g, with "
            "the quadratic remainders dropped, leaves a linear system with "
            "constant coefficients, and its matrix is made of the four first "
            "partial derivatives."
        ),
        Box(
            "definition", "The Jacobian and the linearisation",
            "The Jacobian matrix of system 1 at the point (x*, y*) has first "
            "row (f_x, f_y) and second row (g_x, g_y), all evaluated at "
            "(x*, y*). At an equilibrium, the linear system with matrix J, "
            "u' = f_x u + f_y v, v' = g_x u + g_y v, is the linearisation "
            "of system 1 there.",
            r"J_{11} = \frac{\partial f}{\partial x},\ \ "
            r"J_{12} = \frac{\partial f}{\partial y},\ \ "
            r"J_{21} = \frac{\partial g}{\partial x},\ \ "
            r"J_{22} = \frac{\partial g}{\partial y}",
        ),
        Display(r"\binom{u}{v}' \approx J\binom{u}{v}", "4"),
        Para(
            "For a polynomial system the linearisation can also be found "
            "without differentiating, by substituting directly, and then "
            "the dropped remainder is visible. For the running example "
            "x' = y − x², y' = x − y at its equilibrium (1, 1), put "
            "x = 1 + u and y = 1 + v. Then u' = (1 + v) − (1 + u)² = "
            "−2u + v − u² and v' = (1 + u) − (1 + v) = u − v, exactly. The "
            "linear part has rows (−2, 1) and (1, −1), which is the Jacobian "
            "at (1, 1) as the next section computes it, and the whole "
            "remainder is the single term −u², no larger than the squared "
            "distance u² + v², just as the theorem below promises."
        ),
        Box(
            "theorem", "The linearisation is right to first order",
            "If f and g have continuous second partial derivatives, then "
            "near an equilibrium the true velocity and the velocity of the "
            "linearisation differ by at most a constant times u² + v², the "
            "square of the distance from the equilibrium.",
            r"\mathbf{u}' = J\mathbf{u} + \mathbf{r}(\mathbf{u}), \qquad "
            r"|\mathbf{r}(\mathbf{u})| \leq M|\mathbf{u}|^{2}",
        ),
        Box(
            "proof", "Proof",
            "Taylor's theorem with remainder, applied to f along the segment "
            "from (x*, y*) to (x* + u, y* + v), says that f there equals "
            "f(x*, y*) + f_x u + f_y v plus a remainder of the form "
            "½(f_xx u² + 2f_xy uv + f_yy v²), with the second derivatives "
            "taken at some point of the segment. Those derivatives are "
            "continuous, so they are bounded near the equilibrium, and "
            "|uv| ≤ ½(u² + v²), so the remainder is at most a constant times "
            "u² + v². The first term is zero at an equilibrium. The same "
            "holds for g.",
        ),
        Para(
            "The theorem is the reason for the whole method. At distance 0.1 "
            "from the equilibrium the linear terms are of size about 0.1 and "
            "the neglected ones of size about 0.01; at distance 0.01, they "
            "are 0.01 and 0.0001. The closer the point, the more completely "
            "the linear part dominates, and in the limit the nonlinear field "
            "and the linear one point in the same direction. The figure at "
            "the end of the pendulum section measures exactly that."
        ),
        Para(
            "Each equilibrium has its own Jacobian, because the partial "
            "derivatives are evaluated at a different point. That is how one "
            "system can look like a saddle in one place and a spiral in "
            "another, which a linear system never can: its Jacobian is the "
            "same matrix A everywhere."
        ),
    )),
    Section("Classifying from the Jacobian", (
        Para(
            "Once J is a matrix of numbers, the phase-portraits chapter of "
            "Unit 6 takes over completely. The trace τ and determinant Δ of "
            "J give the characteristic polynomial, and the signs of Δ, τ and "
            "τ² − 4Δ name the picture of the linearisation: a saddle when "
            "Δ < 0; a node when Δ > 0 and τ² > 4Δ; a spiral when Δ > 0 and "
            "τ² < 4Δ; stable or unstable by the sign of τ; a centre when "
            "τ = 0 and Δ > 0. Two borderline cases complete the list: a "
            "proper or improper node, with a repeated eigenvalue, on the "
            "boundary τ² = 4Δ between nodes and spirals; and a degenerate "
            "case with a zero eigenvalue when Δ = 0, which the last section "
            "of this chapter returns to."
        ),
        Para(
            "Stable, asymptotically stable and unstable mean what the "
            "phase-portraits chapter defined them to mean. For a nonlinear "
            "system they are statements about solutions that start close "
            "enough to the equilibrium, so a stable node attracts its "
            "neighbourhood, not the whole plane: another equilibrium, a "
            "saddle say, may sit a short distance away with trajectories "
            "running off past it."
        ),
        Display(r"\lambda^{2} - (\operatorname{tr}J)\lambda + \det J = 0", "5"),
        Para(
            "The routine for a nonlinear system is therefore short. Find "
            "every equilibrium. Compute the Jacobian as a matrix of "
            "functions, once. Then evaluate it at each equilibrium in turn "
            "and classify the linear system that results. The type found is "
            "the type of the linearisation; the almost-linear chapter, next, "
            "is about when that is also the type of the equilibrium itself, "
            "and for every example in this section it is."
        ),
        Worked(
            "A saddle and a node in one system",
            "Classify the linearisation of x' = y − x², y' = x − y at each of "
            "its equilibria (0, 0) and (1, 1).",
            (
                Step("Differentiate once, in general. f = y − x² has f_x = −2x "
                     "and f_y = 1; g = x − y has g_x = 1 and g_y = −1. So J has "
                     "rows (−2x, 1) and (1, −1), a matrix that still depends "
                     "on where it is evaluated.",
                     r"J_{11} = -2x, \quad J_{12} = 1, \quad J_{21} = 1, "
                     r"\quad J_{22} = -1"),
                Step("At (0, 0), J has rows (0, 1) and (1, −1). Its determinant "
                     "is 0 − 1 = −1, negative, so the linearisation is a "
                     "saddle. Its eigenvalues are the roots of λ² + λ − 1 = 0, "
                     "(−1 ± √5)/2, about 0.618 and −1.618.",
                     r"\tau = -1,\ \ \Delta = -1 < 0: \quad \lambda = "
                     r"\frac{-1 \pm \sqrt{5}}{2}"),
                Step("At (1, 1), J has rows (−2, 1) and (1, −1). Now the "
                     "determinant is 2 − 1 = 1, the trace −3 and the "
                     "discriminant 9 − 4 = 5 > 0: a stable node. The "
                     "eigenvalues are (−3 ± √5)/2, about −0.382 and −2.618.",
                     r"\tau = -3,\ \ \Delta = 1,\ \ \tau^{2} - 4\Delta = 5: "
                     r"\quad \lambda = \frac{-3 \pm \sqrt{5}}{2}"),
                Step("Read it. The origin repels along one direction and "
                     "attracts along another; (1, 1) attracts everything near "
                     "it. The slow eigenvalue at (1, 1), −0.382, has "
                     "eigenvector ((√5 − 1)/2, 1), about (0.618, 1), so "
                     "most nearby trajectories settle into (1, 1) along a "
                     "line of slope about 1.618, steeper than the diagonal, "
                     "by the slow-direction rule of the phase-portraits "
                     "chapter. The Phase Portrait screen, given this system "
                     "as a typed equation, finds the same two equilibria "
                     "with the same eigenvalues."),
            ),
        ),
        Para(
            "One system, two quite different local pictures, and the only "
            "thing that changed between them was the value of −2x in the "
            "corner of the Jacobian. At the origin that entry is 0 and at "
            "(1, 1) it is −2, and it is enough to move the determinant from "
            "−1 to +1, across the line in the trace–determinant plane that "
            "separates saddles from everything else."
        ),
        Worked(
            "Four equilibria, and three kinds of picture",
            "The system x' = 2x − 4y + x², y' = x − 3y + y² has an equilibrium "
            "at the origin. Find all its equilibria and classify the "
            "linearisation at each.",
            (
                Step("The second equation gives x = 3y − y², and the first "
                     "can be written 4y = x² + 2x. Substituting the "
                     "expression for x into this and expanding gives the "
                     "quartic y⁴ − 6y³ + 7y² + 2y = 0, which is "
                     "y(y³ − 6y² + 7y + 2) = 0.",
                     r"(3y - y^{2})^{2} + 2(3y - y^{2}) - 4y = "
                     r"y^{4} - 6y^{3} + 7y^{2} + 2y"),
                Step("Try small integers in the cubic: y = 2 gives "
                     "8 − 24 + 14 + 2 = 0, so y − 2 is a factor, and "
                     "dividing it out leaves y² − 4y − 1.",
                     r"y^{4} - 6y^{3} + 7y^{2} + 2y = "
                     r"y(y - 2)(y^{2} - 4y - 1)"),
                Step("The roots are y = 0, y = 2 and y = 2 ± √5, and "
                     "x = 3y − y² gives the matching x. The equilibria are "
                     "(0, 0), (2, 2), (−3 − √5, 2 + √5) ≈ (−5.236, 4.236) and "
                     "(−3 + √5, 2 − √5) ≈ (−0.764, −0.236).",
                     r"y = 2 \pm \sqrt{5} \;\Longrightarrow\; "
                     r"x = 3y - y^{2} = -3 \pm \sqrt{5}"),
                Step("The Jacobian has rows (2x + 2, −4) and (1, 2y − 3). At "
                     "the origin it has rows (2, −4) and (1, −3): Δ = −6 + 4 "
                     "= −2, a saddle, with eigenvalues 1 and −2. At (2, 2) "
                     "it has rows (6, −4) and (1, 1): τ = 7, Δ = 10, "
                     "τ² − 4Δ = 9, an unstable node with eigenvalues 5 and 2.",
                     r"J(0,0):\ \Delta = -2, \qquad J(2,2):\ \tau = 7,\ "
                     r"\Delta = 10"),
                Step("At (−3 − √5, 2 + √5) the diagonal entries are −4 − 2√5 "
                     "and 1 + 2√5, so τ = −3 and Δ = −20 − 10√5 ≈ −42.4: a "
                     "saddle, with eigenvalues about 5.18 and −8.18.",
                     r"\Delta = (-4 - 2\sqrt{5})(1 + 2\sqrt{5}) + 4 = "
                     r"-20 - 10\sqrt{5}"),
                Step("At (−3 + √5, 2 − √5) the diagonal entries are −4 + 2√5 "
                     "≈ 0.472 and 1 − 2√5 ≈ −3.472, so τ = −3 again but "
                     "Δ = −20 + 10√5 ≈ 2.36 is positive. The discriminant "
                     "is 9 − 4Δ = 89 − 40√5 ≈ −0.443, just below zero: a "
                     "stable spiral, with eigenvalues about −1.5 ± 0.333i.",
                     r"\tau^{2} - 4\Delta = 89 - 40\sqrt{5} \approx -0.443"),
            ),
        ),
        Para(
            "Two saddles, a source and a sink, in one quadratic system. The "
            "last classification is worth a second look: the discriminant is "
            "negative, but only just, and the spiral turns so slowly compared "
            "with its decay (0.333 against 1.5) that it would look very like "
            "a node on a sketch. The classification is still exact, because "
            "the numbers are exact; only a picture drawn by eye would be in "
            "doubt."
        ),
    )),
    Section("The pendulum, hanging and balanced", (
        Para(
            "For the damped pendulum x' = y, y' = −sin x − cy, with c ≥ 0, "
            "the equilibria are the points (kπ, 0). The Jacobian needs one "
            "derivative that is not trivial, ∂(−sin x)/∂x = −cos x, and "
            "that entry decides everything."
        ),
        Display(r"J_{11} = 0, \;\; J_{12} = 1, \;\; J_{21} = -\cos x^{*}, "
                r"\;\; J_{22} = -c", "6"),
        Para(
            "At the bottom, x* = 0 (or any even multiple of π), cos x* = 1 "
            "and J has rows (0, 1) and (−1, −c). That is exactly the matrix "
            "of the damped oscillator x'' + cx' + x = 0: τ = −c and Δ = 1. "
            "The discriminant τ² − 4Δ is c² − 4, so the bottom is a centre "
            "of the linearisation when c = 0, a stable spiral when "
            "0 < c < 2, a stable node with the repeated eigenvalue −1 when "
            "c = 2, and a stable node when c > 2: the underdamped, "
            "critically damped and overdamped cases of Unit 4. The "
            "undamped centre is the one verdict here that needs confirming, "
            "and the nonlinear-mechanics chapter does it with the energy. "
            "At the top, x* = π (or any odd multiple), cos x* = −1 and J has "
            "rows (0, 1) and (1, −c), with Δ = −1. The sign of the restoring "
            "term has flipped, and with it the sign of the determinant: the "
            "top is a saddle whatever the damping. That one sign is the whole "
            "difference between hanging and balancing."
        ),
        Para(
            "Linearising a second-order equation can be done without "
            "writing the system at all, because the Jacobian of x' = y is "
            "always the row (0, 1). Near x = 0, sin x ≈ x, the tangent-line "
            "approximation, and x'' + cx' + sin x = 0 becomes "
            "x'' + cx' + x = 0. Near x = π, write u = x − π: then "
            "sin x = sin(π + u) = −sin u ≈ −u, and the equation becomes "
            "u'' + cu' − u = 0, a spring with a negative spring constant. "
            "The graph below is this approximation in one variable."
        ),
        Plot(
            "The restoring force and its two tangent lines",
            "The pendulum's restoring term −sin x, with its tangent line "
            "−x at the hanging position x = 0 and its tangent line x − π at "
            "the balanced position x = π. Near x = 0 the force points back "
            "towards the equilibrium; near x = π it points away from it. The "
            "tangent lines are what the linearisation keeps, and they are "
            "good only near their points of tangency: at x = 1 the line −x "
            "gives −1 where the true force is −sin 1 ≈ −0.84.",
            (Curve("-sin(t)", "−sin x"),
             Curve("-t", "linearisation at 0:  −x"),
             Curve("t - pi", "linearisation at π:  x − π")),
            t=(-1.6, 4.7), xlabel="x (angle)", ylabel="force",
            ylim=(-2.0, 2.0),
        ),
        Worked(
            "Small swings about the bottom",
            "The pendulum x'' + x' + sin x = 0, at rest hanging down, is "
            "given a small push: x(0) = 0, x'(0) = 0.1. Linearise at the "
            "hanging equilibrium, classify it, and solve the linearisation.",
            (
                Step("With c = 1 and cos 0 = 1 the Jacobian has rows (0, 1) "
                     "and (−1, −1). The first row is the definition x' = y, "
                     "carried over unchanged; of the sine, nothing survives "
                     "except its slope at the bottom.",
                     r"x' = y, \qquad y' = -x - y"),
                Step("τ = −1, Δ = 1, τ² − 4Δ = −3 < 0: a stable spiral. The "
                     "eigenvalues are −1/2 ± i√3/2.",
                     r"\lambda = \frac{-1 \pm i\sqrt{3}}{2}"),
                Step("The real solutions are e^(−t/2) times cos((√3/2)t) and "
                     "sin((√3/2)t). Only the sine vanishes at t = 0, and "
                     "matching x'(0) = 0.1 fixes its coefficient at "
                     "0.1/(√3/2) = √3/15.",
                     r"x = \frac{\sqrt{3}}{15}\,e^{-t/2}\sin\frac{\sqrt{3}\,t}{2}"),
                Step("Read it as a statement about the pendulum. A complex "
                     "pair with negative real part means small swings shrink "
                     "as they turn: the angle peaks at about 0.0546 at "
                     "t = 2√3π/9 ≈ 1.21, and each full swing, of duration "
                     "4π/√3 ≈ 7.26, multiplies the amplitude by e^(−2π/√3) "
                     "≈ 0.027. An integration of the true pendulum from the "
                     "same start peaks at 0.05463 as well, and never differs "
                     "from this formula by more than 0.00002."),
            ),
            equation="x' = y; y' = -x - y",
            conditions="x(0) = 0, y(0) = 1/10",
            answer="x = sqrt(3)/15*exp(-t/2)*sin(sqrt(3)*t/2)\n"
                   "y = exp(-t/2)*(cos(sqrt(3)*t/2) - sqrt(3)/3*sin(sqrt(3)*t/2))/10",
            answer_latex=r"x = \frac{\sqrt{3}}{15}e^{-t/2}\sin\frac{\sqrt{3}t}{2},"
                         r"\ \ y = \frac{e^{-t/2}}{10}\left(\cos\frac{\sqrt{3}t}{2} - "
                         r"\frac{1}{\sqrt{3}}\sin\frac{\sqrt{3}t}{2}\right)",
        ),
        Para(
            "The agreement degrades as the push grows, and it degrades in a "
            "particular way. Integrating the true damped pendulum and its "
            "linearisation from x(0) = 0 with x'(0) = 0.1, 1, 2 and 2.5, the "
            "largest difference between the two angles, as a fraction of the "
            "linear peak, comes out at about 0.03%, 3%, 14% and 24%. Ten "
            "times the push gave a hundred times the relative error. That is "
            "the sine's fault: sin x = x − x³/6 + …, so the neglected term is "
            "cubic, and relative to the linear term it is of size x²/6. The "
            "pendulum is better than the general theorem promises, because "
            "its quadratic term happens to vanish."
        ),
        Worked(
            "Balancing at the top",
            "Linearise the undamped pendulum x'' + sin x = 0 at the inverted "
            "position, in the variable u = x − π, and find the solution with "
            "u(0) = −0.1, u'(0) = 0.1: the pendulum 0.1 short of the top and "
            "moving towards it.",
            (
                Step("At x* = π, −cos π = +1, so J has rows (0, 1) and (1, 0). "
                     "In terms of u and v = u' the linearisation is u' = v, "
                     "v' = u.",
                     r"u' = v, \qquad v' = u"),
                Step("τ = 0 and Δ = −1: a saddle, settled before any "
                     "eigenvalue is computed. The eigenvalues are ±1; for "
                     "λ = 1 the eigenvector is (1, 1) and for λ = −1 it is "
                     "(1, −1).",
                     r"\lambda_1 = 1,\ \mathbf{v}_1 = \binom{1}{1}, \qquad "
                     r"\lambda_2 = -1,\ \mathbf{v}_2 = \binom{1}{-1}"),
                Step("The starting point (−0.1, 0.1) is −0.1 times the "
                     "eigenvector (1, −1) of the eigenvalue −1. It lies "
                     "exactly on the stable line, so there is no e^t term at "
                     "all.",
                     r"u = -0.1\,e^{-t}, \qquad v = 0.1\,e^{-t}"),
                Step("Read it. In the linearisation the point creeps up "
                     "towards the balance point, slowing all the way, and "
                     "approaches it without ever reaching it. Any other "
                     "start near the top has an e^t component and is "
                     "eventually thrown off: released from rest at "
                     "u(0) = 0.05, for instance, the linearisation gives "
                     "u = 0.05 cosh t, v = 0.05 sinh t, falling away ever "
                     "faster."),
                Step("The true pendulum from this start does not quite "
                     "creep up and stay. Its energy y²/2 − cos x is "
                     "0.005 − cos(π − 0.1) ≈ 1.000004, a hair above the "
                     "value 1 at the top, so it has just enough to get over. "
                     "An integration follows the formula closely at first "
                     "(at t = 2 the true u is −0.01328 against −0.01343), "
                     "then passes over the top at about t = 4.2 and keeps "
                     "rotating. Only a start on the true stable curve, which "
                     "is tangent to the stable line but bends away from it, "
                     "creeps up and stays; at u = −0.1 that curve has "
                     "velocity 2 sin 0.05 ≈ 0.09996 rather than 0.1. The "
                     "triangular saddle later in the chapter shows the same "
                     "thing with an exact formula."),
            ),
            equation="x' = y; y' = x",
            conditions="x(0) = -1/10, y(0) = 1/10",
            answer="x = -exp(-t)/10\ny = exp(-t)/10",
            answer_latex=r"u = -\frac{1}{10}e^{-t}, \qquad v = \frac{1}{10}e^{-t}",
        ),
        Para(
            "That the approach takes infinitely long is not an artefact of "
            "the linearisation. It is forced by the theorem that trajectories "
            "do not cross: the equilibrium is itself a trajectory, a single "
            "point, and no other trajectory can land on it in a finite time, "
            "since at the moment of landing two solutions would share a point "
            "and would have to be the same solution. Equilibria are "
            "approached, never reached."
        ),
        Para(
            "The two eigenlines at the top matter more than the eigenvalues. "
            "Along the stable one a pendulum given exactly the right push "
            "creeps up and stops; along the unstable one it falls away. For "
            "the true pendulum these lines bend into curves, and the curve "
            "that arrives at the top turns out to be the separatrix between "
            "swinging to and fro and rotating over the top, which the "
            "nonlinear-mechanics chapter derives from the energy. It can be "
            "drawn here, and it is tangent to the eigenlines at both ends."
        ),
        Plot(
            "The separatrix leaves and arrives along eigenlines",
            "The undamped pendulum's separatrices, x = ±2 arctan(sinh t), "
            "y = ±2 sech t, which run from the saddle at (−π, 0) to the saddle "
            "at (π, 0) above the axis and back below it. Beside them are all "
            "four of the linearisations' eigenlines, of slopes ±1 through "
            "each saddle. The upper curve leaves (−π, 0) tangent to the "
            "unstable line y = x + π and arrives at (π, 0) tangent to the "
            "stable line y = −(x − π); the lower curve leaves (π, 0) tangent "
            "to y = x − π and arrives at (−π, 0) tangent to y = −(x + π). "
            "Each bends away from its lines as the distance grows.",
            (Curve("2*atan(sinh(t))", "separatrices", y="2/cosh(t)"),
             Curve("-2*atan(sinh(t))", "", y="-2/cosh(t)"),
             Curve("-pi + 0.3*t", "eigenlines at (−π, 0)", y="0.3*t"),
             Curve("-pi + 0.3*t", "", y="-0.3*t"),
             Curve("pi + 0.3*t", "eigenlines at (π, 0)", y="-0.3*t"),
             Curve("pi + 0.3*t", "", y="0.3*t")),
            t=(-4.0, 4.0), xlabel="x (angle)", ylabel="y (angular velocity)",
            ylim=(-2.4, 2.4),
        ),
        Figure("linearise",
               "The figure opens at the hanging equilibrium with c = 0.3 and "
               "a window of half-width 1.5, and the readout gives the "
               "eigenvalues −0.150 ± 0.989i, a stable spiral, and a worst "
               "angle of 15.52° between the pendulum's field (grey) and the "
               "linear one (coloured). Drag the window half-width down. Near "
               "0.5 the worst angle is about 1.6°, near 0.1 it is below "
               "0.1°, and at the slider's smallest value, 0.05, the two sets "
               "of dashes are indistinguishable. Now widen it to 3: the angle rises to about "
               "80°, and near the edges, where x is close to ±3 and sin x has "
               "turned back towards zero, the two fields visibly disagree. "
               "Move the equilibrium slider past its midpoint to switch to "
               "the inverted position, x = π. The readout names a saddle, "
               "with eigenvalues +0.861 and −1.161, the roots of "
               "λ² + 0.3λ − 1 = 0, and at every window size it gives the "
               "same worst angle as at the bottom, because sin(π + u) = "
               "−sin u makes the error at the top a mirror image of the "
               "error at the bottom. Finally take c to 0: at the bottom the "
               "linearisation becomes a centre, ±1.000i, and at the top the "
               "eigenvalues become exactly ±1."),
    )),
    Section("Second-order equations in general", (
        Para(
            "The pendulum is one case of a pattern worth stating once. Any "
            "equation x'' = F(x, x') becomes x' = y, y' = F(x, y), and the "
            "structure of that system fixes where its equilibria can be and "
            "what their Jacobians look like."
        ),
        Box(
            "theorem", "Equilibria of x'' = F(x, x')",
            "The equilibria of x' = y, y' = F(x, y) all lie on the x-axis, at "
            "the points (x*, 0) with F(x*, 0) = 0. The Jacobian there has "
            "rows (0, 1) and (F_x, F_y), so its determinant is −F_x and its "
            "trace is F_y. In particular the equilibrium is a saddle whenever "
            "F_x(x*, 0) > 0.",
            r"\det J = -F_x(x^{*}, 0), \qquad \operatorname{tr} J = F_y(x^{*}, 0)",
        ),
        Box(
            "proof", "Proof",
            "An equilibrium needs x' = y = 0, so it lies on the x-axis, and "
            "then y' = F(x, 0) = 0. The partial derivatives of y are 0 and 1, "
            "which is the first row, and those of F(x, y) are the second. The "
            "determinant of the matrix with rows (0, 1) and (F_x, F_y) is "
            "0·F_y − 1·F_x, and its trace is 0 + F_y. A negative determinant "
            "is a saddle.",
        ),
        Para(
            "Physically, F is force per unit mass. F_x > 0 means that moving "
            "the particle a little to the right makes the force point further "
            "to the right, so displacements feed themselves: a repelling "
            "position, and a saddle, whatever the damping. F_x < 0 is a "
            "restoring force, and then the damping term F_y decides between "
            "a centre, a spiral and a node, exactly as the damping "
            "classification of Unit 4 did."
        ),
        Worked(
            "A particle between a well and a hilltop",
            "Find and classify the equilibria of x'' + x' + x² − 1 = 0.",
            (
                Step("Here F(x, y) = 1 − x² − y. Equilibria need y = 0 and "
                     "1 − x² = 0, so they are (−1, 0) and (1, 0).",
                     r"F(x, 0) = 1 - x^{2} = 0 \;\Longrightarrow\; x^{*} = \pm 1"),
                Step("F_x = −2x and F_y = −1. At (−1, 0), F_x = 2 > 0, so "
                     "det J = −2 and the point is a saddle. J has rows (0, 1) "
                     "and (2, −1), with characteristic equation "
                     "λ² + λ − 2 = 0 and eigenvalues 1 and −2; the "
                     "eigenvectors are (1, 1) and (1, −2).",
                     r"(-1, 0):\ \ \lambda^{2} + \lambda - 2 = 0,\ \ "
                     r"\lambda = 1,\ -2"),
                Step("At (1, 0), F_x = −2 < 0, a restoring force, so "
                     "det J = 2 and τ = −1. The discriminant is 1 − 8 = −7, "
                     "so the point is a stable spiral with eigenvalues "
                     "−1/2 ± (√7/2)i ≈ −0.5 ± 1.323i.",
                     r"(1, 0):\ \ \lambda^{2} + \lambda + 2 = 0,\ \ "
                     r"\lambda = -\frac{1}{2} \pm \frac{\sqrt{7}}{2}\,i"),
                Step("Read it. The force 1 − x² is minus the derivative of the "
                     "potential x³/3 − x, which has a hilltop at x = −1 and "
                     "a well at x = 1. A particle near the bottom of the well "
                     "oscillates and settles; one near the hilltop is pushed "
                     "off it unless it arrives along the stable line."),
            ),
        ),
    )),
    Section("Two populations", (
        Para(
            "Nonlinear terms arise in population models for a simple reason: "
            "the rate at which predators meet prey is proportional to the "
            "product of the two populations. The ecological-models chapter "
            "treats these models properly. Here they serve as one more "
            "exercise in the routine, with a result that sends a warning "
            "forward."
        ),
        Worked(
            "Predator and prey",
            "Find and classify the linearisations of x' = x − xy, y' = xy − y, "
            "in which x is a prey population, y a predator population, and "
            "each meeting helps the predator and harms the prey.",
            (
                Step("Factor both right-hand sides: x(1 − y) = 0 and "
                     "y(x − 1) = 0. The first holds when x = 0 or y = 1. If "
                     "x = 0 the second forces y = 0; if y = 1 it forces "
                     "x = 1. So the equilibria are (0, 0) and (1, 1), and a "
                     "point such as (1, 0) is not one: there y' = 0 but "
                     "x' = 1.",
                     r"x(1 - y) = 0, \quad y(x - 1) = 0"),
                Step("The Jacobian has rows (1 − y, −x) and (y, x − 1). At "
                     "the origin it has rows (1, 0) and (0, −1): a saddle, "
                     "with the prey growing along the x-axis and the "
                     "predators dying out along the y-axis.",
                     r"J(0, 0):\ \ \lambda = 1,\ -1"),
                Step("At (1, 1) the diagonal entries vanish and J has rows "
                     "(0, −1) and (1, 0): τ = 0, Δ = 1, eigenvalues ±i. The "
                     "linearisation is a centre, and the populations circle "
                     "the coexistence point anticlockwise, since the entry "
                     "in row 2, column 1 is positive.",
                     r"J(1, 1):\ \ \tau = 0,\ \ \Delta = 1,\ \ \lambda = \pm i"),
            ),
        ),
        Para(
            "The same calculation works for x' = ax − xy, y' = xy − cy with "
            "positive constants a and c. The coexistence point is (c, a), "
            "where the Jacobian, with rows (a − y, −x) and (y, x − c), "
            "becomes rows (0, −c) and (a, 0). Its determinant is ac and its "
            "trace 0, so the linearisation is again a centre, with "
            "eigenvalues ±i√(ac). The most common slip here is to use the "
            "Jacobian at the origin, rows (a, 0) and (0, −c), whose "
            "determinant is −ac: a saddle, and an answer about the wrong "
            "point."
        ),
        Para(
            "A centre is the one verdict of this chapter that should not be "
            "trusted without further work. In the phase-portraits chapter a "
            "centre sat on the boundary τ = 0 between inward and outward "
            "spirals, and a change to the matrix however small could push it "
            "off. The nonlinear terms dropped by the linearisation are such "
            "a change. For this predator–prey system the trajectories near "
            "(1, 1) really are closed, which the ecological-models chapter "
            "shows with a conserved quantity; but the almost-linear chapter "
            "exhibits a system with exactly the same Jacobian whose "
            "trajectories spiral slowly outwards."
        ),
    )),
    Section("How good is the linear picture?", (
        Para(
            "The Taylor theorem says the velocities agree to within a "
            "multiple of the squared distance. What that means for the "
            "trajectories is best seen in a system whose trajectories can be "
            "found exactly. The next one is triangular: the first equation "
            "involves x alone, so it can be solved first and its solution "
            "substituted into the second, which is then linear."
        ),
        Worked(
            "A saddle whose stable line bends",
            "The system x' = −x, y' = y + x² has one equilibrium, the "
            "origin. Classify its linearisation, then solve the nonlinear "
            "system exactly from x(0) = 1, y(0) = 0 and compare.",
            (
                Step("−x = 0 and y + x² = 0 force x = 0 and then y = 0, so "
                     "the origin is the only equilibrium. The Jacobian has "
                     "rows (−1, 0) and (2x, 1), which at the origin is "
                     "diagonal, rows (−1, 0) and (0, 1): a saddle, with the "
                     "x-axis as stable line and the y-axis as unstable line.",
                     r"u' = -u, \qquad v' = v"),
                Step("The linearisation puts the start (1, 0) on the stable "
                     "line, and predicts u = e^(−t), v = 0: straight into the "
                     "origin. Now the true system. The first equation gives "
                     "x = e^(−t), so the second is the linear equation "
                     "y' − y = e^(−2t).",
                     r"y' - y = e^{-2t}"),
                Step("A particular solution of the form Ae^(−2t) needs "
                     "−2A − A = 1, so A = −1/3. Adding Ce^t and imposing "
                     "y(0) = 0 gives C = 1/3.",
                     r"y = \frac{1}{3}e^{t} - \frac{1}{3}e^{-2t}"),
                Step("So the true trajectory from (1, 0) is *not* drawn into "
                     "the origin. The e^t term grows, and by t = 2 the point "
                     "has y ≈ 2.46 and is still climbing. The linear verdict "
                     "for this particular start was wrong, although its "
                     "classification of the origin as a saddle was right."),
            ),
            equation="x' = -x; y' = y + x**2",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = exp(-t)\ny = exp(t)/3 - exp(-2*t)/3",
            answer_latex=r"x = e^{-t}, \qquad y = \frac{1}{3}e^{t} - "
                         r"\frac{1}{3}e^{-2t}",
        ),
        Para(
            "Which starts do go into the origin? From a general start "
            "(x₀, y₀) the same steps give y = (y₀ + x₀²/3)e^t − (x₀²/3)e^(−2t), "
            "and the growing term is absent exactly when y₀ = −x₀²/3. So the "
            "trajectories that reach the origin are those on the parabola "
            "y = −x²/3. That parabola is the true stable curve of the saddle, "
            "and it is tangent to the linearisation's stable line, the "
            "x-axis, at the origin. The gap between them is x²/3: 0.0033 at "
            "x = 0.1, 0.083 at x = 0.5, a third at x = 1. The start (1, 0) "
            "lay a third above the true stable curve, on the side that is "
            "thrown upwards. The unstable line needs no correction here: on "
            "the y-axis x stays 0, and y' = y exactly."
        ),
        Plot(
            "The true stable curve and the linear one",
            "The saddle of x' = −x, y' = y + x². The x-axis is the "
            "linearisation's stable line and the y-axis its unstable "
            "line; the parabola y = −x²/3 is the true stable curve, tangent "
            "to the x-axis at the origin. Trajectories from (±1, 0), above "
            "the parabola, are thrown upwards; those from (±1, −2/3), below "
            "it, are thrown downwards. Near the origin the gap x²/3 is tiny, "
            "so the directions agree, but any start off the parabola, "
            "however close, is eventually thrown up or down.",
            (Curve("1.2*(t - 1.125)", "true stable curve  y = −x²/3",
                   y="-(1.2*(t - 1.125))**2/3"),
             Curve("1.2*(t - 1.125)", "linear stable line", y="0*t"),
             Curve("0*t", "unstable line", y="1.2*(t - 1.125)"),
             Curve("exp(-t)", "trajectories", y="exp(t)/3 - exp(-2*t)/3"),
             Curve("-exp(-t)", "", y="exp(t)/3 - exp(-2*t)/3"),
             Curve("exp(-t)", "", y="-exp(t)/3 - exp(-2*t)/3"),
             Curve("-exp(-t)", "", y="-exp(t)/3 - exp(-2*t)/3")),
            t=(-0.25, 2.5), xlabel="x", ylabel="y", ylim=(-1.6, 1.6),
        ),
        Para(
            "This is the general situation at a saddle, and it is the "
            "reason separatrices in nonlinear portraits are curves. The "
            "linearisation gets the directions right at the equilibrium "
            "itself and nothing more: the true stable and unstable curves "
            "leave the saddle tangent to its eigenlines and then bend, as "
            "the pendulum's separatrix did. The classification (saddle, "
            "node, spiral) is a statement about a neighbourhood and is "
            "robust; any particular trajectory predicted by the linear "
            "system is only approximately right, and only for as long as it "
            "stays close in. A start on the linear stable line but off the "
            "true stable curve is thrown away eventually, at any distance: "
            "from (0.01, 0) the formula gives y = (0.0001/3)(e^t − e^(−2t)), "
            "about 0.73 at t = 10 and 16 000 at t = 20. Starting closer "
            "only delays the escape."
        ),
    )),
    Section("When the linearisation is silent", (
        Para(
            "Almost every equilibrium in this chapter so far has had a "
            "Jacobian with no eigenvalue of zero real part; the exceptions "
            "were the centres. Such equilibria are called hyperbolic, and "
            "for them the linear verdict on stability is the true one, as "
            "is the type, apart from the borderline case τ² = 4Δ with a "
            "repeated eigenvalue; the almost-linear chapter states and "
            "explains the theorem that guarantees it. Two kinds of "
            "equilibrium are not hyperbolic. A centre, with eigenvalues "
            "±iω, has already been met, at the predator–prey coexistence "
            "point and at the bottom of the undamped pendulum. The other is "
            "a zero eigenvalue, Δ = 0, where the linearisation has a whole "
            "line of equilibria (or, if J is the zero matrix, a whole plane "
            "of them). A nonlinear system almost never does, and the next "
            "example shows what the neglected terms do instead."
        ),
        Worked(
            "A zero eigenvalue",
            "Linearise x' = x², y' = −y at the origin, then solve the "
            "nonlinear system from x(0) = −1, y(0) = 1, and from x(0) = 1.",
            (
                Step("x² = 0 and −y = 0 only at the origin, so it is the one "
                     "equilibrium. The Jacobian has rows (2x, 0) and (0, −1), "
                     "which at the origin is rows (0, 0) and (0, −1): "
                     "eigenvalues 0 and −1, Δ = 0.",
                     r"u' = 0, \qquad v' = -v"),
                Step("The linearisation says that every point of the x-axis "
                     "is at rest and that everything else drops vertically "
                     "onto it. The true system says neither. Separating "
                     "x' = x² gives −1/x = t + C, and x(0) = −1 makes C = 1; "
                     "the second equation gives y = e^(−t).",
                     r"x = -\frac{1}{1 + t}, \qquad y = e^{-t}"),
                Step("From x(0) = −1 the point does creep into the origin, "
                     "but slowly, like 1/t rather than exponentially. From "
                     "x(0) = 1 the same steps give x = 1/(1 − t), which "
                     "blows up at t = 1. The origin attracts from the left "
                     "and repels to the right, and the linearisation could "
                     "not see either: the x² term is the only thing deciding "
                     "the motion along the x-axis."),
            ),
            equation="x' = x**2; y' = -y",
            conditions="x(0) = -1, y(0) = 1",
            answer="x = -1/(1 + t)\ny = exp(-t)",
            answer_latex=r"x = -\frac{1}{1 + t}, \qquad y = e^{-t}",
        ),
        Box(
            "remark", "Linearise first, then ask whether to believe it",
            "When an eigenvalue of J lies on the imaginary axis (a centre, "
            "or a zero eigenvalue) the type of the linearisation is a "
            "question, not an answer. The Phase Portrait screen of this "
            "application still names a centre from its eigenvalues, but adds "
            "that it is classified from the linearisation only, since an "
            "eigenvalue lies on the imaginary axis and the higher-order "
            "terms decide. A zero eigenvalue is harder still for a computer, "
            "because Newton's method converges slowly to such a point. Run "
            "on the example above over the square from −5 to 5, the "
            "application's equilibrium finder stops at about (−0.000005, 0), "
            "computes eigenvalues −0.00001 and −1 there, and reports a "
            "stable node. Only the algebra shows that the eigenvalue is "
            "exactly zero.",
        ),
        Para(
            "Nothing in this chapter depends on the plane. A system of n "
            "equations has equilibria where all n right-hand sides vanish, "
            "an n × n Jacobian at each, and a linearisation whose "
            "eigenvalues are read exactly as in two dimensions: all real "
            "parts negative means locally attracting, any positive means "
            "locally unstable. The bifurcations chapter uses the same "
            "reading to watch an equilibrium lose stability as a parameter "
            "moves the trace of its Jacobian through zero."
        ),
    )),
    Section("Common errors", (
        Box(
            "warning", "Linearise at the equilibrium, not at the origin",
            "The partial derivatives must be evaluated at the equilibrium "
            "being studied. Using the Jacobian at (0, 0) for the running "
            "example's equilibrium (1, 1) gives rows (0, 1) and (1, −1), a "
            "saddle, for a point that is a stable node. The wrong point gives "
            "a confident wrong answer.",
        ),
        Para(
            "Other errors recur. The first is checking only one equation: an "
            "equilibrium needs f and g to vanish *together*, and (1, 0) in "
            "the predator–prey example satisfies the second but not the "
            "first. The second is confusing equal rates with zero rates: "
            "setting x' = y' and solving gives a curve on which both "
            "variables are, almost everywhere, still changing. The third is "
            "looking for equilibria where det J = 0; a singular Jacobian "
            "says the linearisation is degenerate at a point, and has "
            "nothing to do with where the equilibria are. The fourth is "
            "putting the derivatives in the wrong columns. The first column "
            "holds the derivatives with respect to x and the second those "
            "with respect to y; swapping the columns changes the sign of the "
            "determinant, and for the hanging pendulum, rows (1, 0) and "
            "(−c, −1) in place of (0, 1) and (−1, −c), it turns a spiral into "
            "a saddle. The fifth is a lost sign in a derivative: the "
            "derivative of −sin x is −cos x, and writing +cos x also turns "
            "the bottom of the pendulum into a saddle. The sixth is to look "
            "for equilibria as limits of solutions as t → ∞. That can only "
            "find attracting equilibria, never saddles or sources, and it "
            "needs the very solutions a nonlinear system usually does not "
            "have. And the last is to read the linearisation's trajectories "
            "as the true ones; the triangular saddle showed that the fate "
            "of a start on the linear stable line is wrong however close to "
            "the saddle it begins: from (0.01, 0) the true trajectory still "
            "escapes, only later."
        ),
    )),
    Section("Summary", (
        Para(
            "A nonlinear autonomous system x' = f(x, y), y' = g(x, y) rarely "
            "has a formula, but its equilibria are found by algebra, as the "
            "crossings of the nullclines f = 0 and g = 0, and there may be "
            "none, several or infinitely many. Near an equilibrium, Taylor's "
            "theorem makes the system equal to its linearisation, the "
            "linear system with matrix J, plus a remainder of the order of "
            "the squared distance, where "
            "the Jacobian J holds the four first partial derivatives "
            "evaluated at that equilibrium. Each equilibrium has its own "
            "Jacobian, classified by trace and determinant as in the "
            "phase-portraits chapter, so one system can have saddles, nodes "
            "and spirals in different places: hanging down, the pendulum "
            "linearises to a centre with no damping (a true centre, as the "
            "energy will show), a spiral for 0 < c < 2 and a node for "
            "c ≥ 2, and balanced up it is a saddle, because −cos x* "
            "changes sign. For x'' = F(x, x') the determinant is −F_x, so a "
            "repelling force always gives a saddle. The linearisation gets "
            "the local type right and the directions at the equilibrium "
            "right, while true stable curves and separatrices bend away from "
            "the eigenlines; and when an eigenvalue lies on the imaginary "
            "axis it decides nothing. The next chapter, the almost-linear "
            "chapter, makes precise when the linear verdict is guaranteed "
            "to be the truth."
        ),
    )),
)


ALMOST_LINEAR = (
    Section("What linearising throws away", (
        Para(
            "The equilibria chapter set up a routine. Find every point where "
            "both right-hand sides vanish; at each one, compute the four "
            "partial derivatives that make up the Jacobian; hand the resulting "
            "linear system to the phase-portraits chapter of Unit 6, which "
            "names it from its trace and determinant. The routine is quick, "
            "and it turns one question nobody can solve into several that "
            "anybody can."
        ),
        Para(
            "But it contains a sleight of hand. The quadratic, cubic and "
            "higher terms of the system were thrown away on purpose, because "
            "they are small near the equilibrium, and the verdict reached "
            "without them was then applied to the system that still has "
            "them. Small is not zero. A term that is small can still be the "
            "only thing acting in some direction, and then it decides "
            "everything. Whether dropping it can change the answer is not "
            "obvious, and this chapter settles it."
        ),
        Para(
            "The answer comes in two halves. The reassuring half is a "
            "theorem: when no eigenvalue of the Jacobian lies on the imaginary "
            "axis, the linear picture is the true picture near the point, "
            "saddles stay saddles, spirals stay spirals, and stability is "
            "exactly what the eigenvalues say. The warning half is the centre. "
            "When the eigenvalues are purely imaginary the linear part neither "
            "grows nor shrinks, and the discarded terms are left in sole "
            "charge of whether trajectories creep inwards, creep outwards or "
            "close up. The same Jacobian is compatible with all three, and "
            "the chapter builds one system that does each."
        ),
    )),
    Section("Almost linear systems", (
        Para(
            "Put the equilibrium (x*, y*) at the origin of new coordinates "
            "u = x − x*, v = y − y*, and collect the pair (u, v) in a vector, "
            "written u in bold in the equations. Nothing has been "
            "approximated yet: the system can be written exactly as its "
            "linearisation plus whatever is left over. The leftover, a vector "
            "R(u) with two components R₁ and R₂, is called the remainder. (The "
            "capital letter keeps it apart from r, which in this chapter "
            "always means the distance √(x² + y²) of polar coordinates.) It is "
            "zero at the equilibrium, because the constant term of the "
            "expansion is the value of the right-hand side there, which is "
            "zero."
        ),
        Display(r"\mathbf{u}' = J\mathbf{u} + \mathbf{R}(\mathbf{u}), \qquad "
                r"\mathbf{u} = \binom{x - x^{*}}{y - y^{*}}", "1"),
        Box(
            "definition", "Almost linear at an equilibrium",
            "The system is almost linear at the equilibrium if the remainder is "
            "small compared with the distance from the equilibrium: the ratio "
            "|R(u)|/|u| tends to zero as u tends to 0. Edwards adds the "
            "requirement det J ≠ 0, which makes the equilibrium isolated and "
            "keeps out the zero-eigenvalue case taken up near the end of this "
            "chapter. (Edwards also assumes that f and g have continuous first "
            "partial derivatives near the point.)",
            r"\frac{|\mathbf{R}(\mathbf{u})|}{|\mathbf{u}|} \to 0 \quad\text{as}"
            r"\quad \mathbf{u} \to \mathbf{0}",
        ),
        Para(
            "For the systems of this course the condition costs nothing to "
            "check, because it follows from smoothness. A remainder built out "
            "of squares, products and higher powers of u and v shrinks like "
            "the square of the distance, and anything that shrinks like the "
            "square is certainly small compared with the distance itself."
        ),
        Box(
            "theorem", "Smooth systems are almost linear",
            "If f and g have continuous second partial derivatives near the "
            "equilibrium, the system is almost linear there.",
            r"|\mathbf{R}(\mathbf{u})| \leq M|\mathbf{u}|^{2} \;\Longrightarrow\; "
            r"\frac{|\mathbf{R}(\mathbf{u})|}{|\mathbf{u}|} \leq M|\mathbf{u}| "
            r"\to 0",
        ),
        Box(
            "proof", "Proof",
            "Taylor's theorem with remainder, applied to f and to g about the "
            "equilibrium, writes each component of R(u) as a combination of "
            "u², uv and v² whose coefficients are second derivatives "
            "evaluated somewhere on the segment from the equilibrium to the "
            "point. On a small closed disc those derivatives are bounded, so "
            "|R(u)| is at most a constant M times |u|², and dividing by |u| "
            "leaves at most M|u|, which tends to zero.",
        ),
        Para(
            "Two examples show the sizes involved. For the pendulum "
            "x' = y, y' = −sin x at the hanging position, sin x = x − x³/6 + …, "
            "so the remainder is about x³/6 and its ratio to the linear term "
            "is x²/6: at a swing of 0.1 radians, about a sixth of one "
            "percent. For the system this "
            "chapter will lean on hardest, x' = −y + axr², y' = x + ayr² with "
            "r² = x² + y² the squared distance from the origin, the remainder R "
            "is the whole cubic part, of size |a|r³, and its ratio to the "
            "distance r is |a|r², which vanishes as r → 0. "
            "Both systems are almost linear. The definition guarantees that "
            "the remainder is as small as anyone likes, near enough to the "
            "point. It does not say that it is harmless, and that is the next "
            "question."
        ),
    )),
    Section("Hyperbolic equilibria, and why the linear term wins", (
        Box(
            "definition", "Hyperbolic equilibrium",
            "An equilibrium is hyperbolic if no eigenvalue of its Jacobian has "
            "real part zero. In the trace–determinant plane of Unit 6, that "
            "excludes exactly two sets: the τ-axis, where Δ = 0 and at least "
            "one eigenvalue is 0, and the centre line τ = 0, Δ > 0, where the "
            "eigenvalues are ±iω.",
            r"\mathrm{Re}\,\lambda_i \neq 0 \text{ for } i = 1, 2",
        ),
        Para(
            "Here is the intuition for why hyperbolic points behave. A real "
            "part α ≠ 0 means the linear term changes the distance from the "
            "equilibrium at a fixed exponential rate, |α| per unit time. The "
            "remainder is at most ε|u| near the point, where ε can be made as "
            "small as wished by shrinking the neighbourhood. A fixed rate "
            "against a rate that can be made arbitrarily small is not a "
            "contest: close enough to the equilibrium, the linear term wins."
        ),
        Para(
            "The argument can be made exact most easily for a spiral. A 2×2 "
            "real matrix with eigenvalues α ± iβ can always be brought, by a "
            "linear change of coordinates built from the real and imaginary "
            "parts of a complex eigenvector, to the form with rows (α, −β) and "
            "(β, α). In those coordinates write ρ = |u| for the distance and θ "
            "for the angle, and R₁, R₂ for the two components of the "
            "remainder in the new coordinates. The complex-eigenvalues chapter "
            "of Unit 6 found the two identities that turn a planar system into "
            "polar form: differentiating ρ² = u² + v² gives ρρ' = uu' + vv', "
            "and differentiating tan θ = v/u gives ρ²θ' = uv' − vu'. "
            "Substituting u' = αu − βv + R₁ and v' = βu + αv + R₂, the linear "
            "parts give αρ² and βρ², and dividing by ρ and ρ² gives the radial "
            "and angular speeds."
        ),
        Display(r"\rho' = \alpha\rho + \frac{u\,R_1 + v\,R_2}{\rho}, \qquad "
                r"\theta' = \beta + \frac{u\,R_2 - v\,R_1}{\rho^{2}}", "2"),
        Para(
            "Everything the linear part does is in the first term of each "
            "equation: it changes the distance at rate α and turns at rate β. "
            "Everything the nonlinearity does is in the fractions, and by the "
            "Cauchy–Schwarz inequality each fraction is at most |R(u)| in "
            "size, divided by ρ in the second case."
        ),
        Box(
            "theorem", "A spiral survives",
            "If the Jacobian at an equilibrium of an almost linear system has "
            "eigenvalues α ± iβ with α < 0 and β ≠ 0, the equilibrium is a "
            "stable spiral of the nonlinear system: every solution that starts "
            "close enough turns round it infinitely often and tends to it "
            "exponentially. With α > 0 it is an unstable spiral.",
        ),
        Box(
            "proof", "Proof",
            "Take β > 0 (otherwise reflect) and let ε be half the smaller of "
            "|α| and β. Because the system is almost linear there is a δ such "
            "that |R(u)| ≤ ερ whenever ρ < δ. Then by equation 2, "
            "ρ' ≤ (α + ε)ρ ≤ (α/2)ρ and θ' ≥ β − ε ≥ β/2. A solution that "
            "starts inside the disc ρ < δ therefore has ρ(t) ≤ ρ(0)e^(αt/2): "
            "it never leaves the disc, so the estimates keep holding, and it "
            "tends to the equilibrium while its angle grows at least as fast "
            "as βt/2. For α > 0 the same estimates give ρ' ≥ (α − ε)ρ ≥ "
            "(α/2)ρ in the disc, so every solution other than the "
            "equilibrium itself grows exponentially while it is in the disc "
            "and therefore leaves it: an unstable spiral.",
        ),
        Para(
            "Notice exactly where α ≠ 0 was used: ε had to be smaller than "
            "|α|. With α = 0 the same equation 2 says only that ρ' lies "
            "between −ερ and +ερ, and nothing in the linear part decides "
            "which. That single observation is the whole of the warning half "
            "of this chapter. The same kind of estimate, with more "
            "bookkeeping, handles nodes and saddles, and the result is the "
            "theorem the course uses."
        ),
        Box(
            "theorem", "Hartman–Grobman, in the form a course uses",
            "Near a hyperbolic equilibrium of a system whose right-hand sides "
            "have continuous first partial derivatives, the trajectories of "
            "the nonlinear system are a continuously distorted copy of the trajectories of "
            "its linearisation: there is a change of coordinates near the "
            "point, continuous in both directions, that carries one family of "
            "trajectories onto the other and preserves the direction of time. "
            "In particular the equilibrium has the same stability as the "
            "linearisation, and a linear saddle is a nonlinear saddle.",
            r"\mathrm{Re}\,\lambda_i \neq 0 \;\Longrightarrow\; \text{same "
            r"stability, saddle} \leftrightarrow \text{saddle}",
        ),
        Box(
            "remark", "What the continuous distortion cannot see",
            "A continuous change of coordinates can bend a stable node into a "
            "stable spiral, since both are just 'everything flows in', so "
            "Hartman–Grobman by itself does not say that a node stays a node. "
            "That finer statement is a separate theorem, stated next, and it "
            "is where the two borderline cases appear. Many courses, the "
            "lesson summary among them, fold the two theorems together and "
            "say that Hartman–Grobman preserves the type; strictly, the type "
            "comes from the classification theorem below, and the distortion "
            "Hartman–Grobman provides is continuous, not smooth.",
        ),
        Box(
            "theorem", "Almost linear equilibria (Edwards 6.2)",
            "Let the system be almost linear at an equilibrium whose Jacobian "
            "has eigenvalues λ₁, λ₂. If they are real, unequal and of one "
            "sign, the equilibrium is a node; if real and of opposite signs, "
            "a saddle; if complex with nonzero real part, a spiral; in each "
            "case with the stability of the linearisation. If λ₁ = λ₂ it is "
            "a node or a spiral, with the stability of the linearisation. If "
            "they are purely imaginary it is a centre or a spiral, and its "
            "stability is not determined by the linearisation.",
            r"\lambda_1 = \lambda_2: \text{ node or spiral}; \qquad "
            r"\lambda = \pm i\omega: \text{ centre or spiral, undecided}",
        ),
        Para(
            "Read against the trace–determinant plane, the theorem says that "
            "an equilibrium whose (τ, Δ) lies inside one of the open regions "
            "of Unit 6 keeps its linear name, and one that lies on a "
            "boundary may lose it. On the parabola τ² = 4Δ only the "
            "distinction between node and spiral is at risk, because both "
            "neighbouring regions have the same stability. On the centre line "
            "the two neighbouring regions are stable and unstable spirals, so "
            "stability itself is at risk."
        ),
    )),
    Section("The Duffing oscillator: three equilibria, all hyperbolic", (
        Para(
            "The chapter's running example is the damped Duffing oscillator "
            "x'' + x' − x + x³ = 0, a particle in the double-well potential "
            "V(x) = x⁴/4 − x²/2, whose force −V'(x) = x − x³ pushes it away "
            "from x = 0 and back from large |x|. With y = x' it becomes a "
            "planar system, and setting both right-hand sides to zero gives "
            "y = 0 and x(1 − x²) = 0: three equilibria, at (−1, 0), (0, 0) "
            "and (1, 0). The Jacobian is needed at all three, so compute it "
            "once as a function of the point. With f = y and g = x − x³ − y "
            "the four partial derivatives are f_x = 0, f_y = 1, g_x = 1 − 3x² "
            "and g_y = −1, so J(x, y) has rows (0, 1) and (1 − 3x², −1). Only "
            "the bottom-left entry depends on where it is evaluated."
        ),
        Display(r"x' = y, \qquad y' = x - x^{3} - y, \qquad "
                r"f_x = 0,\ \ f_y = 1,\ \ g_x = 1 - 3x^{2},\ \ g_y = -1", "3"),
        Plot(
            "The Duffing potential",
            "V(x) = x⁴/4 − x²/2. The hump at x = 0 is the unstable balance "
            "point and the two wells at x = ±1, where V = −1/4, are the rest "
            "states the damped particle settles into. The equilibria of the "
            "system are the flat points of this curve, where the force −V'(x) "
            "is zero.",
            (Curve("t**4/4 - t**2/2", "V(x)"),),
            t=(-1.7, 1.7), xlabel="x", ylabel="V(x)", ylim=(-0.4, 0.8),
        ),
        Worked(
            "The saddle between the wells",
            "Linearise the Duffing system x' = y, y' = x − x³ − y at the "
            "origin, classify the equilibrium, and say what the nonlinear "
            "system does there.",
            (
                Step("By equation 3 the Jacobian has rows (0, 1) and "
                     "(1 − 3x², −1). At (0, 0) the entry g_x = 1 − 3·0² is 1, "
                     "so J(0, 0) has rows (0, 1) and (1, −1): the cubic's "
                     "contribution −3x² is zero at the origin, and the "
                     "linearisation is the system x' = y, y' = x − y.",
                     r"\tau = -1, \qquad \Delta = 0 - 1 = -1 < 0"),
                Step("The determinant is negative, so the linearisation is a "
                     "saddle before any eigenvalue is computed. The "
                     "characteristic equation λ² + λ − 1 = 0 gives "
                     "λ = (−1 ± √5)/2, about 0.618 and −1.618. Because the first "
                     "row says x' = y, the eigenvector of each λ is (1, λ).",
                     r"\lambda = \frac{-1 \pm \sqrt{5}}{2}, \qquad "
                     r"\mathbf{v} = \binom{1}{\lambda}"),
                Step("Neither eigenvalue is zero or imaginary, so the origin is "
                     "hyperbolic and Hartman–Grobman applies: the Duffing "
                     "oscillator has a genuine saddle at its hump. Solutions "
                     "leave it along a curve tangent to (1, 0.618) and arrive "
                     "along a curve tangent to (1, −1.618)."),
            ),
        ),
        Worked(
            "The rest state in the right-hand well",
            "Linearise the same system at (1, 0), in coordinates centred "
            "there, classify it, and decide whether the classification is "
            "trustworthy.",
            (
                Step("Shift first: u = x − 1, v = y. In equation 3 the entry "
                     "g_x = 1 − 3x² at x = 1 is −2, while f_x = 0, f_y = 1 and "
                     "the damping entry g_y = −1 do not change, so J(1, 0) has "
                     "rows (0, 1) and (−2, −1). The linearisation is u' = v, "
                     "v' = −2u − v, which is the damped oscillator "
                     "u'' + u' + 2u = 0.",
                     r"\tau = -1, \qquad \Delta = 2, \qquad "
                     r"\tau^{2} - 4\Delta = -7 < 0"),
                Step("A negative discriminant with negative trace is a stable "
                     "spiral. The eigenvalues are −1/2 ± (√7/2)i, about "
                     "−0.5 ± 1.323i.",
                     r"\lambda = -\frac{1}{2} \pm \frac{\sqrt{7}}{2}\,i"),
                Step("The real parts are −1/2, a clear margin away from zero, "
                     "so the point is hyperbolic and the theorem that a "
                     "spiral survives makes the stable spiral real. Replacing "
                     "(x, y) by (−x, −y) leaves the system unchanged, so the "
                     "well at (−1, 0) is a stable spiral too, with the same "
                     "eigenvalues."),
            ),
        ),
        Para(
            "So the local picture of the damped Duffing oscillator is "
            "settled completely by linearisation: a saddle on the hump and "
            "two stable spirals in the wells, each guaranteed. The Phase "
            "Portrait screen reaches the same verdict. Its Duffing oscillator "
            "preset is x'' = −δx' − αx − βx³ with sliders α (stiffness, from "
            "−2 to 2, starting at −1), β (from 0.1 to 3, starting at 1) and "
            "δ (damping, from 0 to 1, starting at 0.2); moving δ to 1 gives "
            "exactly the system above. The report lists each equilibrium in "
            "the window with its name and eigenvalues, and the saddle and the "
            "two stable spirals appear with no caveat beside them."
        ),
    )),
    Section("Same type, bent: the stable and unstable curves", (
        Para(
            "'The same type' does not mean 'the same trajectories'. In a "
            "linear saddle the stable and unstable eigenlines are straight; "
            "in a nonlinear saddle they bend. The equilibria chapter already "
            "watched this happen. It solved x' = −x, y' = y + x², whose "
            "linearisation at the origin is a saddle with the x-axis as its "
            "stable line, and found that the solutions which really tend to "
            "the saddle are not those on the x-axis but those on the parabola "
            "y = −x²/3, which leaves the origin tangent to the x-axis and then "
            "bends away. The reason is a one-line computation: along any "
            "solution the quantity y + x²/3 obeys a linear equation of its "
            "own, so the parabola on which it is zero is made of trajectories."
        ),
        Display(r"\frac{d}{dt}\left(y + \frac{x^{2}}{3}\right) = y + x^{2} - "
                r"\frac{2x^{2}}{3} = y + \frac{x^{2}}{3}", "4"),
        Para(
            "Off that parabola, y + x²/3 grows like e^t and the solution is "
            "thrown up or down; on it, y + x²/3 stays zero, x = x₀e^(−t) tends "
            "to 0, and so does y = −x²/3. That example was a first case of "
            "the theorem below. Running it backwards in time and turning it "
            "upside down (t to −t, y to −y) gives x' = x, y' = −y + x², where "
            "the same parabola, reflected to y = x²/3, is the curve along "
            "which solutions leave the saddle: a bent unstable line instead "
            "of a bent stable one."
        ),
        Box(
            "definition", "Stable and unstable curves of a saddle",
            "At a saddle of a nonlinear system, the stable curve is the set of "
            "points whose solutions tend to the saddle as t → ∞, and the "
            "unstable curve is the set whose solutions tend to it as "
            "t → −∞. (Advanced texts call them the stable and unstable "
            "manifolds.)",
        ),
        Box(
            "theorem", "The stable curve theorem",
            "At a hyperbolic saddle of a smooth planar system, the stable and "
            "unstable curves are smooth curves through the saddle, each made "
            "of the equilibrium and two trajectories, and each tangent at the "
            "saddle to the corresponding eigenline of the linearisation.",
        ),
        Para(
            "This is what Hartman–Grobman buys in the Duffing oscillator. The "
            "saddle at the origin has a stable curve, tangent there to the "
            "direction (1, −1.618), made of the two trajectories that climb "
            "towards the top of the hump with exactly the right energy and "
            "arrive there only as t → ∞. It stretches out between the wells "
            "and divides the plane: a damped particle that starts "
            "on one side ends in one well, and one that starts on the other "
            "side ends in the other. No formula for that curve exists, but "
            "its existence and its direction at the saddle are guaranteed by "
            "a two-by-two eigenvalue computation. The nonlinear-mechanics "
            "chapter meets the same kind of curve, running from saddle to "
            "saddle, as the pendulum's separatrix."
        ),
    )),
    Section("Repeated eigenvalues: node or spiral", (
        Para(
            "The theorem's first soft spot is a repeated real eigenvalue, "
            "on the parabola τ² = 4Δ between nodes and spirals. Stability is "
            "safe there, because both neighbouring regions share it; the "
            "shape is not, as far as the theorem goes. A remainder can leave a "
            "node a node, or tip it into a slow spiral. Both happen, and both "
            "can be solved, though the second needs a remainder rougher than "
            "any in this course."
        ),
        Worked(
            "A star that stays a star",
            "The system x' = −x, y' = −y + x² linearises at the origin to "
            "J = −I, a proper node. Solve it with x(0) = 1, y(0) = 0, find "
            "every trajectory, and decide whether the nonlinear equilibrium "
            "is still a node.",
            (
                Step("At the origin the x² term has zero derivative, so J has "
                     "rows (−1, 0) and (0, −1): the eigenvalue −1 is repeated "
                     "and every direction is an eigendirection. This is the "
                     "borderline case of the theorem.",
                     r"\lambda_1 = \lambda_2 = -1"),
                Step("Again the system is triangular. x = e^(−t), so "
                     "y' + y = e^(−2t); with integrating factor e^t, "
                     "(ye^t)' = e^(−t), so ye^t = C − e^(−t), and y(0) = 0 "
                     "gives C = 1.",
                     r"x = e^{-t}, \qquad y = e^{-t} - e^{-2t}"),
                Step("From a general start (x₀, y₀) the same steps give "
                     "x = x₀e^(−t) and y = (y₀ + x₀²)e^(−t) − x₀²e^(−2t). "
                     "Eliminating t with e^(−t) = x/x₀ turns every trajectory "
                     "with x₀ ≠ 0 into part of a parabola through the origin.",
                     r"y = Cx - x^{2}, \qquad C = \frac{y_0 + x_0^{2}}{x_0}"),
                Step("Each parabola arrives at the origin with slope C, and C "
                     "can be any number, while the two halves of the y-axis "
                     "arrive vertically. Every direction of approach occurs "
                     "and no trajectory turns round the origin: the nonlinear "
                     "equilibrium is still a proper node, stable as the "
                     "linearisation said."),
            ),
            equation="x' = -x; y' = -y + x**2",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = exp(-t)\ny = exp(-t) - exp(-2*t)",
            answer_latex=r"x = e^{-t}, \qquad y = e^{-t} - e^{-2t}",
        ),
        Plot(
            "A nonlinear star",
            "Trajectories of x' = −x, y' = −y + x², the parabolas y = Cx − x² "
            "for C = −2, −1, 0, 1 and 2, with the y-axis. Each is travelled "
            "towards the origin, which it reaches with slope C: every "
            "direction of approach is taken by some trajectory, as in the "
            "linear star, although the straight rays have become curves.",
            (Curve("-2*t - t**2", "trajectories"),
             Curve("-t - t**2", ""),
             Curve("-t**2", ""),
             Curve("t - t**2", ""),
             Curve("2*t - t**2", ""),
             Curve("0*t", "", y="3*t")),
            t=(-1.2, 1.2), xlabel="x", ylabel="y", ylim=(-3.0, 2.0),
        ),
        Para(
            "Now a remainder that turns. Take x' = −x − y/ln r, "
            "y' = −y + x/ln r, with r = √(x² + y²), for 0 < r < 1. The "
            "remainder has size r/|ln r|, and its ratio to r is 1/|ln r|, "
            "which tends to zero as r → 0, so the system is almost linear with "
            "the same Jacobian −I. (It is not smooth enough for the theorem "
            "on smooth systems: 1/ln r goes to zero so slowly that the second "
            "derivatives of the remainder are unbounded near the origin, and "
            "even its first derivatives approach their value 0 only "
            "logarithmically.) In polar form the radial part is "
            "untouched and a slow rotation appears."
        ),
        Display(r"r' = -r, \qquad \theta' = \frac{1}{\ln r}", "5"),
        Worked(
            "A star tipped into a spiral",
            "Solve x' = −x − y/ln r, y' = −y + x/ln r with x(0) = e^(−1), "
            "y(0) = 0, and decide what kind of equilibrium the origin is.",
            (
                Step("From equation 5, r' = −r with r(0) = e^(−1), so "
                     "r = e^(−1−t), and ln r = −1 − t.",
                     r"r = e^{-1-t}, \qquad \ln r = -(1 + t)"),
                Step("Then θ' = −1/(1 + t), and with θ(0) = 0 the angle is "
                     "θ = −ln(1 + t).",
                     r"\theta = -\ln(1 + t) \;\to\; -\infty"),
                Step("Going back with x = r cos θ and y = r sin θ gives the "
                     "solution.",
                     r"x = e^{-1-t}\cos(\ln(1+t)), \qquad "
                     r"y = -e^{-1-t}\sin(\ln(1+t))"),
                Step("Read it. The distance decays exactly as in the linear "
                     "star, so the origin is asymptotically stable, as the "
                     "theorem promises. But the angle decreases without bound: "
                     "the trajectory turns clockwise round the origin "
                     "infinitely often, so the origin is a stable spiral, not "
                     "a node. The turning is very slow. The first full turn is "
                     "complete only when ln(1 + t) = 2π, at t = e^(2π) − 1 ≈ 534, "
                     "by which time r = e^(−1−t) is about 3 × 10⁻²³³."),
            ),
            equation="x' = -x - y/log(sqrt(x**2 + y**2)); "
                     "y' = -y + x/log(sqrt(x**2 + y**2))",
            conditions="x(0) = exp(-1), y(0) = 0",
            answer="x = exp(-1 - t)*cos(log(1 + t))\n"
                   "y = -exp(-1 - t)*sin(log(1 + t))",
            answer_latex=r"x = e^{-1-t}\cos(\ln(1+t)), \qquad "
                         r"y = -e^{-1-t}\sin(\ln(1+t))",
        ),
        Para(
            "Why only on the parabola? A remainder that is small compared "
            "with r acts, near the equilibrium, like a small and changing "
            "perturbation of the matrix J. A matrix inside an open region of "
            "the trace–determinant plane survives small perturbations with its "
            "type intact; a matrix on the parabola τ² = 4Δ can be nudged to "
            "either side of it, into the nodes or into the spirals. The "
            "logarithmic example nudges it into the spirals, by an amount "
            "that shrinks as the trajectory closes in, but never fast enough "
            "for the turning to stop."
        ),
        Para(
            "For a system with continuous second derivatives, which is every "
            "system in this course, that cannot happen. By the theorem on "
            "smooth systems the remainder is at most Mρ², so by equation 2 the "
            "rate of turning it causes, |θ'|, is at most |R|/ρ ≤ Mρ. Near a "
            "stable star ρ shrinks exponentially, so the total angle turned, "
            "the integral of |θ'|, is finite: the angle settles to a limit, "
            "every trajectory arrives from a definite direction, and a node "
            "stays a node. The flip needs a remainder that is small compared "
            "with r but not compared with r^(1+ε) for any ε > 0, and 1/ln r "
            "is exactly such a thing. The next example gives a smooth "
            "remainder the same rotating shape as the logarithmic one and "
            "shows the turning running out."
        ),
        Worked(
            "A smooth twist that runs out",
            "The system x' = −x − y(x² + y²), y' = −y + x(x² + y²) also has "
            "Jacobian −I at the origin. Solve it with x(0) = 1, y(0) = 0 and "
            "find how far the trajectory turns in total.",
            (
                Step("The cubic terms have zero derivatives at the origin, so "
                     "J = −I, the same star as before. In polar form, "
                     "rr' = xx' + yy' = −x² − y² because the cubic terms "
                     "cancel, and r²θ' = xy' − yx' = x²r² + y²r² = r⁴.",
                     r"r' = -r, \qquad \theta' = r^{2}"),
                Step("So r = e^(−t) and θ' = e^(−2t). With θ(0) = 0 the angle "
                     "is (1 − e^(−2t))/2, which increases to the limit 1/2 and "
                     "never passes it.",
                     r"r = e^{-t}, \qquad \theta = \frac{1 - e^{-2t}}{2} "
                     r"\;\to\; \frac{1}{2}"),
                Step("Going back to x = r cos θ and y = r sin θ gives the "
                     "solution.",
                     r"x = e^{-t}\cos\frac{1 - e^{-2t}}{2}, \qquad "
                     r"y = e^{-t}\sin\frac{1 - e^{-2t}}{2}"),
                Step("Read it. The trajectory turns anticlockwise through half "
                     "a radian, about 29°, and then comes straight in along "
                     "the ray θ = 1/2. From a start at distance r₀ the same "
                     "steps give a total turn of r₀²/2 (0.405 radians from "
                     "r₀ = 0.9, which a numerical integration reproduces), so "
                     "the turning shrinks to nothing near the origin. The "
                     "origin is still a stable node: the rays of the linear "
                     "star are bent, not wound up."),
            ),
            equation="x' = -x - y*(x**2 + y**2); y' = -y + x*(x**2 + y**2)",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = exp(-t)*cos((1 - exp(-2*t))/2)\n"
                   "y = exp(-t)*sin((1 - exp(-2*t))/2)",
            answer_latex=r"x = e^{-t}\cos\frac{1 - e^{-2t}}{2}, \qquad "
                         r"y = e^{-t}\sin\frac{1 - e^{-2t}}{2}",
        ),
        Para(
            "The other kind of repeated eigenvalue is the degenerate node of "
            "the Unit 6 repeated-eigenvalues chapter, where J has only one "
            "eigendirection and every trajectory of the linear system comes "
            "in tangent to it. The argument above was for the star, but a "
            "deeper theorem of Hartman covers this case too: for a system "
            "with continuous second derivatives the node stays a node, and "
            "the single eigendirection is still the direction in which "
            "trajectories arrive. As before, a remainder like 1/ln r could "
            "tip it into a spiral."
        ),
        Worked(
            "A degenerate node keeps its direction",
            "The system x' = −x + y + y², y' = −y has an equilibrium at the "
            "origin. Classify its linearisation, solve with x(0) = 0, "
            "y(0) = 1, and find the direction in which trajectories reach "
            "the origin.",
            (
                Step("The y² term has derivative 2y, zero at the origin, so J "
                     "has rows (−1, 1) and (0, −1): τ = −2 and Δ = 1, so "
                     "τ² = 4Δ and the eigenvalue −1 is repeated. (J + I)v = 0 "
                     "forces the second component of v to be 0, so the only "
                     "eigendirection is (1, 0): a degenerate node.",
                     r"\lambda_1 = \lambda_2 = -1, \qquad "
                     r"\mathbf{v} = \binom{1}{0}"),
                Step("The system is triangular the other way round: y = e^(−t) "
                     "at once, and then x' + x = e^(−t) + e^(−2t). With "
                     "integrating factor e^t, (xe^t)' = 1 + e^(−t), so "
                     "xe^t = t − e^(−t) + C, and x(0) = 0 gives C = 1.",
                     r"x = (1 + t)e^{-t} - e^{-2t}, \qquad y = e^{-t}"),
                Step("From a general start (x₀, y₀) the same steps give "
                     "y = y₀e^(−t) and the x below. The linear system alone "
                     "would give (x₀ + y₀t)e^(−t); the y² term adds "
                     "y₀²(e^(−t) − e^(−2t)), which is smaller than the "
                     "y₀te^(−t) term once t is large.",
                     r"x = (x_0 + y_0^{2} + y_0 t)\,e^{-t} - y_0^{2} e^{-2t}"),
                Step("Read it. For y₀ ≠ 0 the ratio y/x behaves like 1/t and "
                     "tends to 0; from (0, 1) it is exactly "
                     "1/(1 + t − e^(−t)), about 1/11 at t = 10. Solutions "
                     "with y₀ = 0 stay on the x-axis. So every trajectory "
                     "reaches the origin tangent to the x-axis, the single "
                     "eigendirection, just as in the linear degenerate node: "
                     "the nonlinear equilibrium is a stable degenerate node, "
                     "its trajectories bent but not turned round."),
            ),
            equation="x' = -x + y + y**2; y' = -y",
            conditions="x(0) = 0, y(0) = 1",
            answer="x = (1 + t)*exp(-t) - exp(-2*t)\ny = exp(-t)",
            answer_latex=r"x = (1 + t)e^{-t} - e^{-2t}, \qquad y = e^{-t}",
        ),
    )),
    Section("A centre is a question, not an answer", (
        Para(
            "The second soft spot is worse. A linear centre lies on the line "
            "τ = 0, Δ > 0, with stable spirals on one side and unstable spirals "
            "on the other, and the remainder can push it either way. Equation "
            "2 with α = 0 says the same thing directly: the linear part only "
            "rotates, so every bit of radial motion comes from the remainder."
        ),
        Display(r"\lambda = \pm i\omega \;\Longrightarrow\; \rho' = "
                r"\frac{u\,R_1 + v\,R_2}{\rho} \quad \text{(remainder only)}", "6"),
        Para(
            "The figure at the end of this section is built on a system that "
            "makes this "
            "exact, with a parameter a controlling the strength of a cubic "
            "term."
        ),
        Display(r"x' = -y + a x (x^{2} + y^{2}), \qquad "
                r"y' = x + a y (x^{2} + y^{2})", "7"),
        Para(
            "At the origin the cubic terms have zero derivatives, so for "
            "every value of a the Jacobian has rows (0, −1) and (1, 0), with "
            "eigenvalues ±i: the same linear centre. It is also the Jacobian "
            "of the predator–prey system x' = x − xy, y' = xy − y at (1, 1), "
            "so equation 7 is the system the equilibria chapter promised, "
            "with exactly the same Jacobian as that one. The predator–prey "
            "system "
            "really is a centre, as the ecological-models chapter will show, "
            "while equation 7 with a = 0.1 has the same Jacobian and spirals "
            "out. Now change to polar coordinates with the identities used "
            "for equation 2. The cross terms cancel in both."
        ),
        Display(r"rr' = x(-y + axr^{2}) + y(x + ayr^{2}) = ar^{2}(x^{2} + y^{2}) "
                r"= ar^{4}", "8"),
        Para(
            "In the same way r²θ' = xy' − yx' = x(x + ayr²) − y(−y + axr²) "
            "= x² + y² = r². The rotation is untouched, and the radius obeys "
            "a scalar equation that depends on a alone."
        ),
        Display(r"r' = a r^{3}, \qquad \theta' = 1", "9"),
        Para(
            "Trajectories turn anticlockwise at unit rate for every a, but "
            "for a > 0 the radius increases, for a < 0 it decreases, and only "
            "for a = 0 is it constant. One linearisation, three behaviours: an "
            "unstable spiral, a stable spiral, a genuine centre. The radial "
            "equation is separable, and from r(0) = r₀ its solution is "
            "explicit."
        ),
        Display(r"r(t) = \frac{r_0}{\sqrt{1 - 2 a r_0^{2}\, t}}", "10"),
        Worked(
            "The centre that is really a stable spiral",
            "Take a = −1 in equation 7, so that x' = −y − x(x² + y²), "
            "y' = x − y(x² + y²). Solve with x(0) = 1, y(0) = 0, and describe "
            "how the trajectory approaches the origin.",
            (
                Step("The linearisation is the rotation with eigenvalues ±i, "
                     "a centre, which decides nothing. The polar equations are "
                     "r' = −r³ and θ' = 1, with r(0) = 1 and θ(0) = 0.",
                     r"r' = -r^{3}, \qquad \theta' = 1"),
                Step("Separate: dr/r³ = −dt, so −1/(2r²) = −t + C, and "
                     "r(0) = 1 gives C = −1/2. Hence 1/r² = 1 + 2t, which is "
                     "equation 10 with a = −1 and r₀ = 1. The angle is simply "
                     "θ = t.",
                     r"r = \frac{1}{\sqrt{1 + 2t}}, \qquad \theta = t"),
                Step("Back in Cartesian coordinates, x = r cos θ and "
                     "y = r sin θ.",
                     r"x = \frac{\cos t}{\sqrt{1 + 2t}}, \qquad "
                     r"y = \frac{\sin t}{\sqrt{1 + 2t}}"),
                Step("Read it. The origin is asymptotically stable: every "
                     "trajectory spirals into it anticlockwise. But the decay "
                     "is algebraic, not exponential: r behaves like 1/√(2t) "
                     "for large t, and at t = 4, after almost two-thirds of a "
                     "turn, r is still 1/3. A stable spiral of a linear system "
                     "shrinks by a fixed factor on every turn; this one shrinks "
                     "by less and less, because the cubic term that drives it "
                     "weakens as r falls."),
            ),
            equation="x' = -y - x*(x**2 + y**2); y' = x - y*(x**2 + y**2)",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = cos(t)/sqrt(1 + 2*t)\ny = sin(t)/sqrt(1 + 2*t)",
            answer_latex=r"x = \frac{\cos t}{\sqrt{1 + 2t}}, \qquad "
                         r"y = \frac{\sin t}{\sqrt{1 + 2t}}",
        ),
        Para(
            "With a > 0 the same formula has a minus sign under the root, and "
            "the root reaches zero at t = 1/(2ar₀²). The trajectory spirals "
            "out and reaches infinity in finite time: with a = 1 and r₀ = 1 it "
            "is gone by t = 1/2. Both behaviours sit behind a Jacobian that "
            "cannot tell them apart."
        ),
        Plot(
            "One linearisation, three trajectories",
            "Equation 7 from (0.5, 0) for t from 0 to 18, the start and time "
            "the figure below uses. With a = 0.1 the radius grows to "
            "0.5/√0.1 ≈ 1.581; with a = 0 the orbit is the circle r = 0.5; "
            "with a = −0.1 it shrinks to 0.5/√1.9 ≈ 0.363. The three systems "
            "have the same Jacobian at the origin.",
            (Curve("0.5*cos(t)/sqrt(1 - 0.05*t)", "a = +0.1",
                   y="0.5*sin(t)/sqrt(1 - 0.05*t)"),
             Curve("0.5*cos(t)", "a = 0", y="0.5*sin(t)"),
             Curve("0.5*cos(t)/sqrt(1 + 0.05*t)", "a = −0.1",
                   y="0.5*sin(t)/sqrt(1 + 0.05*t)")),
            t=(0.0, 18.0), xlabel="x", ylabel="y", ylim=(-1.7, 1.7),
        ),
        Figure("almost_linear",
               "The figure draws equation 7 with its direction field and the "
               "trajectory from (0.5, 0) up to t = 18, and the readout gives "
               "two things on one line: the Jacobian's eigenvalues at the "
               "origin with the linearisation's name for it, and the radius "
               "the trajectory actually reaches. It starts at a = +0.100, "
               "where the readout says 'a centre' and then measures a radius "
               "of about 1.6: the trajectory spirals outwards. (It prints "
               "1.596 rather than the 1.581 of equation 10, because the "
               "slider's nearest step to 0.1 is 0.1002, and this close to the "
               "blow-up time a small change in a shows.) Drag a down through "
               "zero. The readout's eigenvalues stay at 0.000 ± 1.000i and "
               "the word centre never changes, but near a = 0 (the slider snaps "
               "values within "
               "0.006 of zero to exactly zero) the orbit closes at r = 0.500, "
               "and at a = −0.1 it spirals in to r = 0.363. Try the ends of "
               "the slider too: at a = −0.3 the radius falls to 0.260, and at "
               "a = +0.3 equation 10 blows up at t = 1/(2 · 0.3 · 0.25) ≈ 6.7. "
               "The figure integrates in steps of one time unit and stops at "
               "t = 6, when the next step fails; the drawn trajectory ends "
               "there, at radius 1.58 on the right-hand edge of the window and "
               "not yet round once, and the readout reports 'r = 1.581 after "
               "t = 6' accordingly."),
        Box(
            "warning", "A linear centre decides nothing",
            "Purely imaginary eigenvalues make the equilibrium non-hyperbolic. "
            "The nonlinear system may be a centre, a stable spiral or an "
            "unstable spiral, and the Jacobian cannot tell which. Report it as "
            "'a centre of the linearisation', and then settle it by one of the "
            "methods below.",
        ),
    )),
    Section("Settling a centre with a conserved quantity", (
        Para(
            "Two tools settle a linear centre, and they answer in opposite "
            "directions. The first proves that the centre is genuine. If some "
            "function E(x, y) is constant along every solution, each "
            "trajectory lies on a level curve of E; if those level curves are "
            "closed loops round the equilibrium, the trajectories have "
            "nowhere to go but round and round."
        ),
        Box(
            "theorem", "A conserved quantity with a strict minimum",
            "Suppose E has continuous second derivatives, dE/dt = E_x f + E_y g "
            "is identically zero, and E has a strict local minimum at an "
            "isolated equilibrium, with a positive-definite matrix of second "
            "derivatives there. Then the equilibrium is a centre of the "
            "nonlinear system: every trajectory starting close enough is a "
            "closed orbit round it.",
            r"\frac{dE}{dt} = E_x f + E_y g = 0",
        ),
        Box(
            "proof", "Proof",
            "Near a minimum with positive-definite second derivatives the "
            "level curves E = E(x*, y*) + c, for small c > 0, are closed curves "
            "round the point, shaped nearly like ellipses. A solution starting "
            "on one of them stays on it. There is no equilibrium on the curve, "
            "because the equilibrium is isolated, so the speed is bounded "
            "below by a positive number there and the solution cannot stall: "
            "it travels all the way round the loop and returns to its start. "
            "By uniqueness it then repeats, so it is periodic. Since the loops "
            "shrink to the point as c → 0, the equilibrium is stable but not "
            "asymptotically stable.",
        ),
        Worked(
            "The undamped Duffing wells are genuine centres",
            "Remove the damping: x' = y, y' = x − x³. Linearise at (1, 0), "
            "then use the energy E = y²/2 + x⁴/4 − x²/2 to decide what the "
            "nonlinear system does there.",
            (
                Step("The Jacobian at (1, 0) has rows (0, 1) and (−2, 0). Its "
                     "trace is 0 and its determinant 2, so the eigenvalues are "
                     "±√2 i: a linear centre, which decides nothing.",
                     r"\lambda^{2} + 2 = 0, \qquad \lambda = \pm\sqrt{2}\,i"),
                Step("The energy is kinetic plus potential, and its derivative "
                     "along solutions vanishes identically: the two terms "
                     "cancel exactly.",
                     r"\frac{dE}{dt} = (x^{3} - x)\,y + y\,(x - x^{3}) = 0"),
                Step("At (1, 0) the second derivatives are E_xx = 3x² − 1 = 2, "
                     "E_yy = 1 and E_xy = 0, a positive-definite matrix, so E "
                     "has a strict local minimum there, with value −1/4.",
                     r"E(1, 0) = -\frac{1}{4}, \qquad E_{xx} = 2,\ E_{yy} = 1,"
                     r"\ E_{xy} = 0"),
                Step("By the theorem, (1, 0) is a genuine centre: a particle "
                     "released near the bottom of the well oscillates for "
                     "ever. By symmetry so is (−1, 0). At the origin E_xx = −1, "
                     "so E has a saddle point there rather than a minimum, "
                     "consistent with the linearisation's eigenvalues ±1, a "
                     "hyperbolic saddle."),
            ),
        ),
        Plot(
            "Level curves of the Duffing energy",
            "Trajectories of the undamped system x' = y, y' = x − x³ lie on "
            "the level curves of E = y²/2 + x⁴/4 − x²/2. The loops at "
            "E = −0.2 circle the two wells, which are genuine centres; the "
            "figure-eight E = 0 passes through the saddle at the origin; the "
            "outer loop E = 0.2 goes round all three equilibria.",
            (Curve("2.8284*t - 1.4142", "E = 0",
                   y="(2.8284*t - 1.4142)*sqrt(1 - (2.8284*t - 1.4142)**2/2)"),
             Curve("2.8284*t - 1.4142", "",
                   y="-(2.8284*t - 1.4142)*sqrt(1 - (2.8284*t - 1.4142)**2/2)"),
             Curve("0.7435 + 0.4595*t", "E = −0.2",
                   y="sqrt((0.7435 + 0.4595*t)**2 - (0.7435 + 0.4595*t)**4/2"
                     " - 0.4)"),
             Curve("0.7435 + 0.4595*t", "",
                   y="-sqrt((0.7435 + 0.4595*t)**2 - (0.7435 + 0.4595*t)**4/2"
                     " - 0.4)"),
             Curve("-0.7435 - 0.4595*t", "",
                   y="sqrt((0.7435 + 0.4595*t)**2 - (0.7435 + 0.4595*t)**4/2"
                     " - 0.4)"),
             Curve("-0.7435 - 0.4595*t", "",
                   y="-sqrt((0.7435 + 0.4595*t)**2 - (0.7435 + 0.4595*t)**4/2"
                     " - 0.4)"),
             Curve("3.0604*t - 1.5302", "E = 0.2",
                   y="sqrt((3.0604*t - 1.5302)**2 - (3.0604*t - 1.5302)**4/2"
                     " + 0.4)"),
             Curve("3.0604*t - 1.5302", "",
                   y="-sqrt((3.0604*t - 1.5302)**2 - (3.0604*t - 1.5302)**4/2"
                     " + 0.4)")),
            t=(0.0, 1.0), xlabel="x", ylabel="y", ylim=(-1.2, 1.2),
        ),
        Para(
            "Set δ to 0 in the Phase Portrait screen's Duffing preset to see "
            "the same system. The report still names the two wells centres, "
            "because that is what their linearisations are, but it adds "
            "'from the linearisation only — an eigenvalue lies on the "
            "imaginary axis, so the higher-order terms decide' beside each. "
            "The energy is what removes that caveat. The next two chapters "
            "use the same tool twice more: the ecological-models chapter "
            "finds a conserved quantity for the predator–prey equations, "
            "which makes their linear centre a real one and their population "
            "cycles closed, and the nonlinear-mechanics chapter does the same "
            "for the pendulum."
        ),
        Box(
            "remark", "A shortcut: systems that can run backwards",
            "The undamped Duffing system is unchanged if t is replaced by −t "
            "and y by −y: with s = −t and Y = −y it reads dx/ds = Y, "
            "dY/ds = x − x³, the same equations again. A system with this "
            "symmetry is called reversible, and a linear centre that lies on "
            "the x-axis of a reversible system is a genuine centre, with or "
            "without an energy. Near the centre the linear rotation carries "
            "a solution that starts on the x-axis round through one "
            "half-plane to the x-axis again, on the other side of the "
            "equilibrium. Reflect that half-orbit in the x-axis and run it "
            "backwards: by the symmetry the result is also a solution, it "
            "joins the same two points of the axis, and by uniqueness it is "
            "the rest of the orbit. The two halves close up into a loop. The "
            "friction example below is not reversible, which is why it is "
            "free to spiral.",
            r"(x,\ y,\ t) \;\to\; (x,\ -y,\ -t)",
        ),
    )),
    Section("Settling a centre with a quantity that only decreases", (
        Para(
            "The second tool can prove the opposite. If a function V with a "
            "strict minimum at the equilibrium is not conserved but can only "
            "decrease along solutions, trajectories can only move to lower "
            "level curves, inwards. The simplest choice of V is half the "
            "squared distance from the equilibrium, and then dV/dt is nothing "
            "but ρρ', the radial motion of equation 6: the method is the "
            "polar-coordinate method in another form."
        ),
        Box(
            "definition", "Lyapunov function",
            "A function V(x, y) with continuous first partial derivatives and "
            "a strict local minimum at an equilibrium is a Lyapunov function "
            "there if its rate of change along solutions, V' = V_x f + V_y g, "
            "is never positive near the equilibrium. (V is the traditional "
            "letter; it has nothing to do with the Duffing potential earlier "
            "in the chapter.)",
            r"V' = V_x f + V_y g \leq 0",
        ),
        Box(
            "theorem", "Lyapunov's test",
            "If V is a Lyapunov function at the equilibrium p, then p is "
            "stable. If moreover V' < 0 at every point near p other than p "
            "itself, then p is asymptotically stable.",
            r"V' \leq 0 \;\Longrightarrow\; \text{stable}, \qquad "
            r"V' < 0 \text{ away from } p \;\Longrightarrow\; "
            r"\text{asymptotically stable}",
        ),
        Box(
            "proof", "Proof",
            "Subtract a constant so that V(p) = 0; then V > 0 near p except "
            "at p. Take a small ε > 0 and let m be the smallest value of V on "
            "the circle of radius ε round p, which is positive. By continuity "
            "there is a δ < ε with V < m on the disc of radius δ. A solution "
            "that starts in that disc has V < m, and V never increases along "
            "it, so it can never reach the circle, where V ≥ m: it stays "
            "within ε of p, which is stability. For the second part, V "
            "decreases along the solution and is bounded below by 0, so it "
            "tends to a limit L. If L were positive, the solution would never "
            "enter the region where V < L, which contains a small disc round "
            "p, so it would stay in a closed ring between that disc and the "
            "circle. There V' is continuous and negative, so V' ≤ −k for "
            "some k > 0, and V would fall by at least kt by time t, which is "
            "impossible. So L = 0, and because V is positive away from p, the "
            "solution tends to p.",
        ),
        Worked(
            "Nonlinear friction decides a centre",
            "The system x' = y, y' = −x − y³ is an oscillator with a friction "
            "force proportional to the cube of the velocity. Linearise at the "
            "origin, then use V = (x² + y²)/2 to decide what happens, and "
            "compare with the system x' = y, y' = −x + y³.",
            (
                Step("The y³ term has zero derivative at the origin, so both "
                     "systems linearise to rows (0, 1) and (−1, 0), with "
                     "eigenvalues ±i: the same linear centre.",
                     r"\lambda = \pm i"),
                Step("Along solutions of the first system the linear terms "
                     "cancel and only the friction is left.",
                     r"\frac{dV}{dt} = x y + y(-x - y^{3}) = -y^{4} \leq 0"),
                Step("So V is a Lyapunov function, and the first half of "
                     "Lyapunov's test makes the origin stable; here it is "
                     "plain anyway, since V is half the squared distance and "
                     "the distance never increases. The second half does not "
                     "apply, because dV/dt vanishes on the whole x-axis. A solution cannot "
                     "stay on the "
                     "x-axis except at the origin, because there y' = −x ≠ 0 "
                     "pushes it off at once, so V keeps strictly decreasing; "
                     "a further argument (LaSalle's invariance principle) "
                     "shows that it decreases all the way to 0. The origin is "
                     "asymptotically stable, and trajectories spiral in."),
                Step("The decay is slow. Integrating from (1, 0), the distance "
                     "from the origin is about 0.35 at t = 10, 0.25 at "
                     "t = 20 and 0.18 at t = 40, falling roughly like 1/√t "
                     "rather than exponentially, the signature of a spiral "
                     "driven by a nonlinear term alone."),
                Step("For x' = y, y' = −x + y³ the sign flips and "
                     "dV/dt = +y⁴ ≥ 0. Again dV/dt vanishes on the x-axis, so "
                     "the inequality alone proves nothing: a true centre has "
                     "dV/dt ≥ 0 too, with equality everywhere. The trick "
                     "of the remark on reversible systems finishes it. Changing t to "
                     "−t and y to −y turns this system into the first one, so "
                     "every trajectory here is a trajectory of the damped "
                     "system run backwards, and it spirals out. From (0.2, 0) "
                     "the distance passes 1 shortly before t = 33. Same "
                     "Jacobian, opposite verdict.",
                     r"\frac{dV}{dt} = x y + y(-x + y^{3}) = y^{4} \geq 0"),
            ),
        ),
        Para(
            "Friction that is linear in the velocity would have appeared in "
            "the Jacobian, shifted the eigenvalues off the imaginary axis, and "
            "made the point hyperbolic; that is the damped oscillator of Unit "
            "4. Cubic friction is invisible to the linearisation and decisive "
            "for the system. The nonlinear-mechanics chapter uses Lyapunov's "
            "test again, with the energy of a damped pendulum as the Lyapunov "
            "function, and states LaSalle's invariance principle, which turns "
            "the argument about the x-axis above into a theorem."
        ),
    )),
    Section("Zero eigenvalues decide nothing either", (
        Para(
            "The other non-hyperbolic case is an eigenvalue exactly zero, "
            "when det J = 0. The linear system then has a line of "
            "equilibria (the whole plane, if J is the zero matrix), as the "
            "phase-portraits chapter found, and along that "
            "line the linear part does nothing at all; the remainder alone "
            "moves the solution there. Edwards's definition of an almost "
            "linear system excludes this case outright."
        ),
        Worked(
            "Algebraic approach along a zero eigenvalue",
            "The system x' = −x³, y' = −y linearises at the origin to the "
            "matrix with rows (0, 0) and (0, −1). Solve it with x(0) = 1, "
            "y(0) = 1, and compare with x' = x³, y' = −y.",
            (
                Step("The eigenvalues are 0 and −1, so the origin is not "
                     "hyperbolic. The linear system x' = 0, y' = −y would leave "
                     "x fixed for ever: a whole line of equilibria.",
                     r"\lambda_1 = 0, \qquad \lambda_2 = -1"),
                Step("The equations are uncoupled. Separating x' = −x³ gives "
                     "1/x² = 1 + 2t, and y = e^(−t) directly.",
                     r"x = \frac{1}{\sqrt{1 + 2t}}, \qquad y = e^{-t}"),
                Step("Read it. Both components tend to zero, so the nonlinear "
                     "origin is asymptotically stable, but x does so "
                     "algebraically: at t = 10, x ≈ 0.218 while "
                     "y ≈ 4.5 × 10⁻⁵. The trajectory flattens onto the x-axis, "
                     "the zero eigenvalue's direction, and creeps along it."),
                Step("For x' = x³, y' = −y the Jacobian is the same, but "
                     "1/x² = 1 − 2t and x blows up at t = 1/2: the origin is "
                     "unstable. The linearisation could not tell these apart."),
            ),
            equation="x' = -x**3; y' = -y",
            conditions="x(0) = 1, y(0) = 1",
            answer="x = 1/sqrt(1 + 2*t)\ny = exp(-t)",
            answer_latex=r"x = \frac{1}{\sqrt{1 + 2t}}, \qquad y = e^{-t}",
        ),
        Para(
            "Zero eigenvalues are where the number of equilibria changes: "
            "as a parameter moves, two equilibria can approach each other, "
            "merge at a point with det J = 0, and vanish. That is a "
            "bifurcation, and it is the subject of the last chapter of this "
            "unit."
        ),
    )),
    Section("A routine, and the errors it prevents", (
        Para(
            "Put together, the chapter adds one step to the routine of the "
            "equilibria chapter. After computing the Jacobian at each "
            "equilibrium, check whether the equilibrium is hyperbolic: "
            "det J ≠ 0, and not both tr J = 0 and det J > 0. If it is, "
            "classify it from τ and Δ and trust the answer. (On the parabola "
            "τ² = 4Δ Edwards's theorem allows a node to be a spiral, but only "
            "for remainders rougher than any smooth system has; for the "
            "systems of this course a node there is a node.) If "
            "it is not, the linear name is a statement about the "
            "linearisation alone. Then look for a conserved quantity, a "
            "reversing symmetry, a quantity that only decreases, or a change "
            "to polar coordinates in which r' can be computed; failing those, "
            "integrate numerically and look, "
            "which is what the Phase Portrait screen is for."
        ),
        Box(
            "warning", "Common errors",
            "Calling a linear centre a centre of the nonlinear system, without "
            "a conserved quantity to back it. Calling a point with eigenvalue "
            "real parts 0 and −1 stable because no real part is positive: a "
            "zero real part is undecided, not neutral. Forgetting that the "
            "theorem is local: it promises nothing about how large the "
            "neighbourhood is, and in the Duffing oscillator the stable "
            "spiral at (1, 0) governs only one side of the saddle's stable "
            "curve. And linearising at the origin when the equilibrium is "
            "somewhere else, the error the equilibria chapter warned against, "
            "which gives a confident answer about the wrong point.",
        ),
        Para(
            "A quick test of the routine: an equilibrium with "
            "eigenvalues −3 and 2 is a saddle of the nonlinear system, "
            "guaranteed; one with −1 ± i is a stable spiral, guaranteed; one "
            "with ±2i is undecided, however the question is phrased; one "
            "with −2 and −5 is a stable node, guaranteed; and one with 0 and "
            "−1 is undecided too, however negative the other eigenvalue is."
        ),
    )),
    Section("Summary", (
        Para(
            "A system is almost linear at an equilibrium when its remainder "
            "after the Jacobian term is small compared with the distance, "
            "which every smooth system is. An equilibrium is hyperbolic when "
            "no eigenvalue of the Jacobian has real part zero, and then the "
            "linear term wins near the point: by Hartman–Grobman the nonlinear "
            "flow is a continuously distorted copy of the linear one, with the "
            "same stability, and, by the classification of almost linear "
            "equilibria, nodes, saddles and spirals keep their names. The "
            "eigenlines bend into stable and unstable curves, tangent to them "
            "at the point, which organise the flow further out, as the "
            "saddle of the Duffing oscillator divides its two wells. A "
            "repeated eigenvalue keeps its stability; the theorem allows a "
            "node to turn into a spiral there, but only for a remainder like "
            "r/ln r, and in a smooth system a star or a degenerate node stays "
            "a node, its trajectories bent but not wound up. Purely imaginary "
            "eigenvalues decide nothing: the system "
            "x' = −y + ax(x² + y²), y' = x + ay(x² + y²) has a linear centre "
            "for every a and radial equation r' = ar³, so it spirals in, "
            "closes up or spirals out according to the sign of a. Such a "
            "centre is settled by a conserved quantity with a strict minimum "
            "or a reversing symmetry, either of which proves a genuine "
            "centre, by a Lyapunov function, a quantity that only decreases, "
            "which proves stability (and attraction when the decrease is "
            "strict away from the point), or by computing r' in "
            "polar coordinates. Zero eigenvalues, the last non-hyperbolic "
            "case, lead to the bifurcations at the end of the unit."
        ),
    )),
)


ECOLOGY = (
    Section("Two populations in one plane", (
        Para(
            "The first two chapters of this unit built a method. Find the "
            "equilibria of x' = f(x, y), y' = g(x, y) by algebra, linearise at "
            "each one, classify the linear system by its trace and "
            "determinant as the phase-portraits chapter of Unit 6 did, and "
            "trust the answer whenever the equilibrium is hyperbolic. This "
            "chapter uses that method on the oldest nonlinear systems in "
            "applied mathematics, which are about animals, and turns the "
            "nullclines, met in the equilibria chapter, into the tool that "
            "makes the rest of the picture quick to draw."
        ),
        Para(
            "Two populations that affect each other are two unknowns, x(t) "
            "and y(t), each growing or shrinking at a rate that depends on "
            "both. Lotka in 1925 and Volterra in 1926 wrote down, "
            "independently, the simplest account of a predator eating its "
            "prey: prey multiply when left alone, predators starve when left "
            "alone, and every encounter is a meal for one and a loss for the "
            "other. Encounters happen at a rate proportional to the product "
            "xy, and that product is the whole of the nonlinearity. Make "
            "both interaction terms losses and give each species a crowding "
            "term of its own, and the same shape describes two species "
            "competing for one food supply, each held back by its own "
            "numbers and by the other."
        ),
        Para(
            "Neither system can be solved in closed form, and neither needs "
            "to be. For predator and prey the question is whether the "
            "populations settle, and the surprising answer is that they "
            "cycle for ever, on closed loops fixed by where they start. For "
            "competitors the question is which species survive, and the "
            "answer is a comparison that can be read off a sketch with a "
            "ruler: whether each species limits itself more than it limits "
            "the other. Both answers come from the nullclines."
        ),
    )),
    Section("Nullclines", (
        Para(
            "At every point of the phase plane the system gives a velocity "
            "(f, g). The equilibria chapter met the nullclines as the curves "
            "where one component of that velocity is zero, so that the flow "
            "is vertical or horizontal, and the phase-portraits chapter of "
            "Unit 6 drew them when sketching by hand. Collected together, "
            "the facts about them are these."
        ),
        Box(
            "definition", "Nullclines",
            "For the system x' = f(x, y), y' = g(x, y), the x-nullcline is the "
            "set of points where f(x, y) = 0, so that x is momentarily not "
            "changing, and the y-nullcline is the set where g(x, y) = 0. "
            "Either may consist of several separate curves.",
            r"x\text{-nullcline: } f(x, y) = 0, \qquad "
            r"y\text{-nullcline: } g(x, y) = 0",
        ),
        Para(
            "Three facts make the nullclines worth drawing first. The first "
            "two were in the equilibria chapter; the third is the one this "
            "chapter leans on. Each follows directly from the definition, "
            "but together they organise the whole portrait."
        ),
        Box(
            "theorem", "What the nullclines tell",
            "(i) The equilibria are exactly the points that lie on an "
            "x-nullcline and a y-nullcline at once. (ii) A trajectory crosses "
            "an x-nullcline vertically and a y-nullcline horizontally, except "
            "at an equilibrium. (iii) If f and g are continuous, then in each "
            "region into which the nullclines cut the plane, x' has one sign "
            "throughout and so does y'.",
        ),
        Box(
            "proof", "Proof",
            "(i) An equilibrium is a point where f = 0 and g = 0 together. "
            "(ii) On the x-nullcline the velocity is (0, g), which points "
            "straight up or straight down; on the y-nullcline it is (f, 0). "
            "(iii) A continuous function that changes sign along a path "
            "between two points must vanish somewhere on it, by the "
            "intermediate value theorem. Inside a region f never vanishes, "
            "so it cannot change sign there, and the same holds for g.",
        ),
        Para(
            "Fact (iii) is what turns nullclines into a sketching tool. In "
            "each region, one test point settles the signs of x' and y', "
            "and so which of the four diagonal directions (up and right, up "
            "and left, down and right, down and left) the flow runs in. The "
            "flow can only turn from one of these directions to another by "
            "crossing a nullcline, and fact (ii) says how it crosses."
        ),
        Para(
            "In the ecological models the right-hand sides factor, as "
            "x·(something) and y·(something), and each factor gives its own "
            "piece of nullcline. The factor x makes the whole y-axis part of "
            "the x-nullcline: where there is none of the first species it "
            "cannot change. Likewise the x-axis is part of the y-nullcline. "
            "The other pieces are where the bracketed per-capita rates "
            "vanish, and for the models in this chapter those are straight "
            "lines."
        ),
        Box(
            "warning", "The axes are nullclines too",
            "Setting x' = x(4 − 2x − y) to zero gives x = 0 or 2x + y = 4. "
            "Keeping only the line and forgetting x = 0 loses the "
            "equilibria on the y-axis, which are the states in which the "
            "first species is extinct, often the most important ones in the "
            "problem.",
        ),
    )),
    Section("The predator–prey model", (
        Para(
            "Let x be the number of prey, rabbits say, and y the number of "
            "predators, foxes, both in suitable units. Without foxes, "
            "rabbits breed at a per-capita rate a > 0. Without rabbits, "
            "foxes die at a per-capita rate c > 0. An encounter between a "
            "fox and a rabbit happens at a rate proportional to xy, removes "
            "rabbits at rate bxy and, by feeding foxes, adds foxes at rate "
            "dxy, with b, d > 0. Adding up the gains and losses gives the "
            "Lotka–Volterra system."
        ),
        Display(r"x' = a x - b x y, \qquad y' = -c y + d x y", "1"),
        Para(
            "The signs carry the roles. The species whose own term is "
            "positive and whose encounter term is negative is the prey; the "
            "species that starves alone and gains from encounters is the "
            "predator. Written per capita, x'/x = a − by and y'/y = −c + dx, "
            "the model says that the prey's growth rate falls linearly with "
            "the number of predators and the predators' growth rate rises "
            "linearly with the number of prey."
        ),
        Para(
            "The model has an obvious flaw, which is worth seeing before "
            "anything else. With no predators, x' = ax and the prey grow "
            "exponentially without limit, as x₀e^(at). The section on "
            "crowded prey repairs this, and finds that the repair changes "
            "the answer in an instructive way. With no prey, the predators simply die out, "
            "and that is the first worked example."
        ),
        Worked(
            "Predators without prey",
            "For x' = 2x − xy, y' = xy − 3y, find the solution with x(0) = 0 "
            "and y(0) = 5, and explain why no trajectory that starts with "
            "both populations positive can ever reach an axis.",
            (
                Step("With x = 0 the first equation reads x' = 0, which the "
                     "constant x = 0 satisfies. The second becomes y' = −3y, "
                     "exponential decay.",
                     r"x = 0, \qquad y' = -3y \;\Longrightarrow\; y = 5e^{-3t}"),
                Step("So the positive y-axis is a trajectory: the foxes decline "
                     "towards the origin and never reach it. In the same way, "
                     "setting y = 0 leaves x' = 2x, and the positive x-axis is a "
                     "trajectory running outwards, x = x₀e^(2t)."),
                Step("The right-hand sides are polynomials, so the existence "
                     "and uniqueness theorem applies and trajectories cannot "
                     "cross or touch. A trajectory that starts in the open "
                     "quadrant x > 0, y > 0 could only reach an axis by meeting "
                     "one of the axis trajectories or the equilibrium at the "
                     "origin, which it cannot do. So positive populations stay "
                     "positive for all time, as they should in a sensible "
                     "model."),
            ),
            equation="x' = 2*x - x*y; y' = x*y - 3*y",
            conditions="x(0) = 0, y(0) = 5",
            answer="x = 0\ny = 5*exp(-3*t)",
            answer_latex=r"x = 0, \qquad y = 5e^{-3t}",
        ),
    )),
    Section("Equilibria, and an undecided centre", (
        Para(
            "Factor each right-hand side of equation 1. The x-nullcline is "
            "x(a − by) = 0, which is the y-axis together with the horizontal "
            "line y = a/b. The y-nullcline is y(dx − c) = 0, the x-axis "
            "together with the vertical line x = c/d. The y-axis meets the "
            "x-axis at the origin, and the line y = a/b meets the line "
            "x = c/d at a single point. The other two pairings, the y-axis "
            "with x = c/d and the x-axis with y = a/b, are parallel lines and "
            "never meet."
        ),
        Display(r"(0, 0) \quad\text{and}\quad (x^{*}, y^{*}) = "
                r"\left(\frac{c}{d}, \frac{a}{b}\right)", "2"),
        Para(
            "The Jacobian has rows (a − by, −bx) and (dy, dx − c). At the "
            "origin it is diagonal, with entries a and −c: a saddle, with "
            "the x-axis as its unstable line and the y-axis as its stable "
            "line, which is exactly what the first worked example found by "
            "solving along the axes. The saddle is hyperbolic, so the "
            "almost-linear chapter guarantees that the nonlinear system has "
            "a saddle there too. Extinction of both species is not a state "
            "the populations approach, except along the knife-edge where "
            "there are no prey to begin with."
        ),
        Para(
            "The equilibria chapter found the centre at the coexistence "
            "point with b = d = 1; the general case is the same calculation. "
            "Both diagonal entries vanish there, because a − by* = 0 and "
            "dx* − c = 0. The off-diagonal entries are −bx* = −bc/d and "
            "dy* = ad/b, so the trace is 0 and the determinant is ac > 0."
        ),
        Display(r"\operatorname{tr}J = 0, \qquad \det J = 0 \cdot 0 - "
                r"\left(-\frac{bc}{d}\right)\left(\frac{ad}{b}\right) = ac > 0",
                "3"),
        Para(
            "Purely imaginary eigenvalues ±i√(ac): the linearisation is a "
            "centre, and a centre is precisely the case in which the "
            "almost-linear chapter said linearisation decides nothing. The "
            "nonlinear terms, however small, may turn the closed ellipses "
            "into slow spirals inwards or outwards. Something beyond the "
            "Jacobian is needed, and the next section supplies it."
        ),
        Worked(
            "Nullclines, equilibria and Jacobians",
            "For x' = 2x − xy, y' = xy − 3y, draw the nullclines, find the "
            "equilibria, classify each from its linearisation, and find the "
            "direction of the flow in each region of the open quadrant.",
            (
                Step("The x-nullcline is x(2 − y) = 0: the y-axis and the line "
                     "y = 2. The y-nullcline is y(x − 3) = 0: the x-axis and "
                     "the line x = 3. So a = 2, b = 1, c = 3, d = 1, and the "
                     "equilibria are the origin and (3, 2).",
                     r"(x^{*}, y^{*}) = \left(\frac{3}{1}, \frac{2}{1}\right) "
                     r"= (3, 2)"),
                Step("The Jacobian has rows (2 − y, −x) and (y, x − 3). At the "
                     "origin its rows are (2, 0) and (0, −3): determinant −6, "
                     "a saddle, with eigenvalues 2 and −3."),
                Step("At (3, 2) the rows are (0, −3) and (2, 0): trace 0, "
                     "determinant 6, eigenvalues ±i√6. A linear centre, which "
                     "on its own settles nothing.",
                     r"\lambda^{2} + 6 = 0, \qquad \lambda = \pm i\sqrt{6}"),
                Step("The lines x = 3 and y = 2 cut the open quadrant into four "
                     "regions. Below y = 2 the prey grow (x' > 0) and above it "
                     "they shrink; to the right of x = 3 the predators grow "
                     "(y' > 0) and to the left they shrink. So the flow runs "
                     "down and right in the lower left, up and right in the "
                     "lower right, up and left in the upper right, and down and "
                     "left in the upper left: anticlockwise round (3, 2)."),
            ),
        ),
        Plot(
            "Lotka–Volterra nullclines",
            "The nullclines of x' = 2x − xy, y' = xy − 3y. The prey stop "
            "changing on the y-axis and on the line y = 2, the predators on "
            "the x-axis and on the line x = 3, and the two equilibria are at "
            "the origin and at (3, 2). The small closed curve is the orbit "
            "of the linearisation through (3.5, 2), an ellipse. The true "
            "orbit through that point (not drawn) is close to it but "
            "egg-shaped: "
            "computed numerically, it reaches x = 2.55 on the left and y "
            "between 1.64 and 2.41, against 2.50 and 1.59 to 2.41 for the "
            "ellipse, so it is squashed on the sides facing the axes.",
            (Curve("t", "x-nullcline y = 2", y="2 + 0*t"),
             Curve("0*t", "x-nullcline x = 0", y="0.75*t"),
             Curve("3 + 0*t", "y-nullcline x = 3", y="0.75*t"),
             Curve("t", "y-nullcline y = 0", y="0*t"),
             Curve("3 + 0.5*cos(1.05*t)", "linearisation's orbit",
                   y="2 + 0.408*sin(1.05*t)")),
            t=(0.0, 6.0), xlabel="x  (prey)", ylabel="y  (predators)",
            ylim=(-0.2, 4.5),
        ),
        Para(
            "The linearisation at (3, 2) can be solved outright, and its "
            "solution is a good description of small oscillations about the "
            "coexistence point. Write u = x − 3 and v = y − 2 for the "
            "departures from equilibrium."
        ),
        Worked(
            "Small oscillations about coexistence",
            "Solve the linearisation u' = −3v, v' = 2u of the system above at "
            "(3, 2), starting from u(0) = 1, v(0) = 0, and find the period and "
            "the order in which the two populations peak.",
            (
                Step("Differentiate the first equation and use the second: "
                     "u'' = −3v' = −6u. So u oscillates with angular frequency "
                     "√6, and with u(0) = 1 and u'(0) = −3v(0) = 0 it is a "
                     "pure cosine.",
                     r"u'' + 6u = 0, \qquad u = \cos\sqrt{6}\,t"),
                Step("Then v = −u'/3 = (√6/3) sin √6 t. The trajectory is an "
                     "ellipse with semi-axes 1 in u and √6/3 ≈ 0.816 in v, "
                     "travelled anticlockwise.",
                     r"v = \frac{\sqrt{6}}{3}\sin\sqrt{6}\,t"),
                Step("The period is 2π/√6 ≈ 2.565. The prey departure u peaks "
                     "at t = 0 and the predator departure v peaks when "
                     "√6 t = π/2, a quarter of a period later. The predators "
                     "lag the prey: foxes are most numerous after rabbits have "
                     "been plentiful for a while, and rabbits are scarcest after "
                     "foxes have been plentiful.",
                     r"T = \frac{2\pi}{\sqrt{6}} \approx 2.565"),
                Step("How good is this? Integrating the nonlinear system "
                     "numerically from (3.1, 2) gives a period of 2.5654, "
                     "agreeing to four figures. From (4, 2) it is 2.590, and "
                     "from (6, 2) it is 2.732: larger cycles take longer, which "
                     "no linear system can show."),
            ),
            equation="x' = -3*y; y' = 2*x",
            conditions="x(0) = 1, y(0) = 0",
            answer="x = cos(sqrt(6)*t)\ny = sqrt(6)*sin(sqrt(6)*t)/3",
            answer_latex=r"u = \cos\sqrt{6}\,t, \qquad "
                         r"v = \frac{\sqrt{6}}{3}\sin\sqrt{6}\,t",
        ),
    )),
    Section("A conserved quantity", (
        Para(
            "The Lotka–Volterra system has a special structure: each "
            "per-capita rate depends on the other variable only. That lets "
            "time be eliminated and the result be separated. Away from the "
            "nullclines, divide y' by x'."
        ),
        Display(r"\frac{dy}{dx} = \frac{y(dx - c)}{x(a - by)} "
                r"\;\Longrightarrow\; \frac{a - by}{y}\,dy = "
                r"\frac{dx - c}{x}\,dx", "4"),
        Para(
            "Integrating both sides gives a ln y − by = dx − c ln x plus a "
            "constant. Collecting everything on one side produces a function "
            "of x and y that takes the same value all along each trajectory."
        ),
        Display(r"V(x, y) = d x - c \ln x + b y - a \ln y", "5"),
        Box(
            "theorem", "The Lotka–Volterra first integral",
            "Along every solution of equation 1 with x > 0 and y > 0, the "
            "function V of equation 5 is constant.",
            r"\frac{dV}{dt} = V_x\,x' + V_y\,y' = 0",
        ),
        Box(
            "proof", "Proof",
            "Separating variables is how V was found, but checking it needs "
            "only the chain rule. V_x = d − c/x = (dx − c)/x and "
            "V_y = b − a/y = (by − a)/y. Then V_x x' = (dx − c)(a − by) and "
            "V_y y' = (by − a)(dx − c), whose sum is zero.",
            r"\frac{dV}{dt} = (dx - c)(a - by) + (by - a)(dx - c) = 0",
        ),
        Para(
            "So V is a conserved quantity in the sense of the almost-linear "
            "chapter (another common name is *first integral*), the "
            "ecological counterpart of the energy of an undamped oscillator; "
            "the next chapter meets the energy of the pendulum, which does "
            "the same job. At (c/d, a/b) its second derivatives are "
            "V_xx = c/x² = d²/c, V_yy = a/y² = b²/a and V_xy = 0, which form a "
            "positive-definite matrix. So the almost-linear chapter's theorem "
            "on a conserved quantity with a strict minimum already makes the "
            "coexistence point a genuine centre: orbits close enough to it "
            "are closed. What is new here is that every orbit in the "
            "quadrant closes, however large. Its value is fixed by the "
            "starting point, and the "
            "trajectory is confined to the level curve V = V(x₀, y₀). The "
            "whole phase portrait is therefore the family of level curves "
            "of V, and the question of closed orbits becomes a question "
            "about the shape of those curves."
        ),
        Worked(
            "Finding and checking the first integral",
            "Find the conserved quantity of x' = 2x − xy, y' = xy − 3y, its "
            "value at the equilibrium, and its value on the orbits through "
            "(4, 2) and (6, 2).",
            (
                Step("Here a = 2, b = 1, c = 3, d = 1. The slope equation is "
                     "dy/dx = y(x − 3)/(x(2 − y)), which separates.",
                     r"\frac{2 - y}{y}\,dy = \frac{x - 3}{x}\,dx"),
                Step("Integrating, 2 ln y − y = x − 3 ln x + C, so the "
                     "conserved quantity is the one below. Checking by the "
                     "chain rule: (1 − 3/x)(2x − xy) + (1 − 2/y)(xy − 3y) = "
                     "(x − 3)(2 − y) + (y − 2)(x − 3) = 0.",
                     r"V = x - 3\ln x + y - 2\ln y"),
                Step("At (3, 2), V = 5 − 3 ln 3 − 2 ln 2 ≈ 0.318. On the orbit "
                     "through (4, 2) it is 6 − 3 ln 4 − 2 ln 2 ≈ 0.455, and "
                     "through (6, 2) it is ≈ 1.238. Larger cycles have larger "
                     "V, and the equilibrium has the smallest value of all."),
                Step("A numerical check: integrating the system from (4, 2) "
                     "for a full period with a tight tolerance changes V by "
                     "less than 10⁻¹¹, which is rounding error. The solver "
                     "knows nothing about V, so this is an independent "
                     "confirmation."),
            ),
        ),
    )),
    Section("Why the orbits close", (
        Para(
            "V is a sum of a function of x alone and a function of y alone, "
            "F(x) = dx − c ln x and G(y) = by − a ln y. Each is a bowl. "
            "F'(x) = d − c/x vanishes only at x = c/d, F''(x) = c/x² is "
            "positive, and F grows without bound both as x → 0⁺, where "
            "−c ln x → ∞, and as x → ∞, where the linear term wins. The same "
            "holds for G with its minimum at y = a/b. So V has a single "
            "minimum on the open quadrant, at the coexistence point, and "
            "rises to infinity towards the axes and far away."
        ),
        Plot(
            "The two halves of V",
            "F(x) = x − 3 ln x and G(y) = y − 2 ln y, the two parts of the "
            "conserved quantity for x' = 2x − xy, y' = xy − 3y, drawn against "
            "one variable t. Each is a convex bowl, with its minimum at the "
            "equilibrium value (t = 3 for F, t = 2 for G) and rising steeply "
            "towards 0. A level curve F(x) + G(y) = k therefore has, for each "
            "x in an interval, exactly two values of y, and the two branches "
            "join at the ends of the interval: a closed loop.",
            (Curve("t - 3*log(t)", "F(x) = x − 3 ln x"),
             Curve("t - 2*log(t)", "G(y) = y − 2 ln y")),
            t=(0.25, 9.0), xlabel="x or y", ylabel="value", ylim=(-0.5, 5.0),
        ),
        Box(
            "theorem", "Predator–prey orbits are closed",
            "Every trajectory of equation 1 that starts in the open quadrant "
            "x > 0, y > 0, other than the equilibrium (c/d, a/b) itself, is a "
            "closed curve round that equilibrium, travelled anticlockwise, "
            "and the solution on it is periodic.",
        ),
        Box(
            "proof", "Proof",
            "Let k = V(x₀, y₀), which exceeds the minimum value V* of V. Take "
            "any x with F(x) < k − G(a/b). Then G(y) = k − F(x) is above G's "
            "minimum, and since G decreases to its minimum and then increases, "
            "it has exactly two solutions y, one on each side of a/b. The x "
            "for which this works form an interval, at whose ends the two "
            "solutions merge. So the level set V = k is a single closed loop "
            "round the equilibrium. It contains no equilibrium, so, as in the "
            "almost-linear chapter's proof for small loops, a solution on it "
            "goes all the way round in a finite time and then repeats. The "
            "sense of travel is the anticlockwise one found from the sign "
            "regions.",
        ),
        Para(
            "So the linear centre was telling the truth this time, but for a "
            "reason the linearisation cannot see. The Jacobian alone is "
            "consistent with spirals either way; it is the conserved "
            "quantity that closes the orbits. Two consequences are worth "
            "stating. The cycles are not limit cycles: each starting point "
            "has its own loop, and a disturbance that moves the populations "
            "moves them onto a different loop, where they stay. And the "
            "coexistence point is stable but not asymptotically stable, "
            "since a solution that starts near it stays near it but never "
            "approaches it."
        ),
        Para(
            "The sign regions give the order of events round every loop. The "
            "prey peak where the loop crosses y = a/b on the right, the "
            "predators peak where it crosses x = c/d at the top, the prey "
            "bottom out on the left and the predators at the bottom. Each "
            "peak of prey is followed by a peak of predators. For small loops "
            "the delay is a quarter of a period, as in the linear worked "
            "example; for large loops it is a smaller fraction. Measured "
            "numerically on the loop through (4, 2) it is 0.215 of the "
            "period, and on the loop through (6, 2) it is 0.166. The stretch "
            "from the prey peak to the predator peak crosses the upper "
            "right, where both populations are large and everything changes "
            "fast, so it takes a shrinking share of the period."
        ),
        Para(
            "The lesson's Phase Portrait tool opens on the Lotka–Volterra "
            "system with a = 1.5 (set it to 2 to match the running example), "
            "and has sliders for a, b, c and d. It draws the nullclines "
            "dashed, marks the origin as a saddle and the coexistence point "
            "as a centre, and lets you click to launch a trajectory through "
            "any point. Its limit-cycle layer draws the orbit of the "
            "starting trajectory dotted and reports that it is a closed "
            "orbit but not an isolated one, which is the theorem above "
            "found by measurement."
        ),
    )),
    Section("Averages over a cycle, and Volterra's fishery", (
        Para(
            "The populations never settle, so what does the equilibrium "
            "(c/d, a/b) mean for them? A clean answer comes from integrating "
            "the per-capita equations over one period."
        ),
        Box(
            "theorem", "The equilibrium is the average",
            "On any periodic orbit of equation 1, with period T, the average "
            "number of prey over one period is c/d and the average number of "
            "predators is a/b, whatever the size of the orbit.",
            r"\frac{1}{T}\int_0^T x\,dt = \frac{c}{d}, \qquad "
            r"\frac{1}{T}\int_0^T y\,dt = \frac{a}{b}",
        ),
        Box(
            "proof", "Proof",
            "Divide the first equation by x: (ln x)' = a − by. Integrate from "
            "0 to T. The left side is ln x(T) − ln x(0) = 0, because the "
            "solution is periodic. So 0 = aT − b∫y dt, which is the second "
            "statement. Dividing the second equation by y and doing the same "
            "gives 0 = −cT + d∫x dt, the first.",
            r"0 = \ln x(T) - \ln x(0) = \int_0^T (a - by)\,dt",
        ),
        Para(
            "This is a strong statement, because the orbits can be large and "
            "lopsided. On the loop through (6, 2) for the running example "
            "the prey range from about 1.22 to 6 and the predators from 0.64 "
            "to 4.58, yet a numerical average over one period gives 3.000 and "
            "2.000 to four figures. The equilibrium is the average of the "
            "populations over a cycle, not a state they ever rest in."
        ),
        Para(
            "Volterra came to the model through a question from his "
            "son-in-law, the marine biologist Umberto D'Ancona. During the "
            "First World War fishing in the Adriatic was sharply reduced, "
            "and the proportion of predatory fish in the catches landed at "
            "the ports went up. Why should less fishing favour the "
            "predators? The averages theorem answers it."
        ),
        Worked(
            "Fishing both species",
            "Fishing removes both species at the same per-capita rate h, with "
            "0 < h < 2, from x' = 2x − xy, y' = xy − 3y. Find the average "
            "populations with fishing, and their values for h = 1/2.",
            (
                Step("Fishing adds −hx to the prey equation and −hy to the "
                     "predator equation. The system keeps its form, with a "
                     "replaced by 2 − h and c by 3 + h.",
                     r"x' = (2 - h)x - xy, \qquad y' = -(3 + h)y + xy"),
                Step("As long as 2 − h > 0 this is again a Lotka–Volterra "
                     "system, so its orbits are closed and its averages are its "
                     "equilibrium values.",
                     r"\bar{x} = 3 + h, \qquad \bar{y} = 2 - h"),
                Step("For h = 1/2 the averages move from (3, 2) to (3.5, 1.5): "
                     "fishing raises the average number of prey and lowers the "
                     "average number of predators. Read backwards, reducing the "
                     "fishing lowers the prey and raises the predators, which "
                     "is what D'Ancona saw."),
                Step("The same reasoning explains why an insecticide that "
                     "kills a crop pest and its natural predator alike can "
                     "leave the pest more numerous on average than before."),
            ),
        ),
    )),
    Section("When the prey crowd themselves", (
        Para(
            "The closed orbits depend on the exact form of equation 1, and "
            "the phase-portraits chapter warned that a centre sits on a "
            "boundary: the smallest change of the right kind turns it into a "
            "spiral. The model's flaw, unlimited prey growth, is a natural "
            "place to make that change. Give the prey logistic growth, so "
            "that they crowd each other even without foxes."
        ),
        Worked(
            "Crowded prey: the centre becomes a spiral",
            "Find and classify the equilibria of x' = x(3 − x − y), "
            "y' = y(x − 1), in which the prey alone would settle at 3.",
            (
                Step("The x-nullcline is the y-axis and the line x + y = 3; the "
                     "y-nullcline is the x-axis and the line x = 1. Their "
                     "crossings are (0, 0), (3, 0) and (1, 2).",
                     r"(0, 0), \quad (3, 0), \quad (1, 2)"),
                Step("The Jacobian has rows (3 − 2x − y, −x) and (y, x − 1). "
                     "At the origin it is diagonal with entries 3 and −1: a "
                     "saddle. At (3, 0) its rows are (−3, −3) and (0, 2), with "
                     "eigenvalues −3 and 2: another saddle, whose unstable "
                     "direction says that a few foxes introduced to a full "
                     "warren will grow."),
                Step("At (1, 2) the rows are (−1, −1) and (2, 0): trace −1, "
                     "determinant 2, discriminant 1 − 8 = −7. A stable spiral, "
                     "with eigenvalues −1/2 ± i√7/2.",
                     r"\lambda = -\frac{1}{2} \pm \frac{\sqrt{7}}{2}\,i"),
                Step("The real part is −1/2, not zero, so the equilibrium is "
                     "hyperbolic and by the almost-linear chapter the spiral is "
                     "real. The oscillations of predator and prey now die "
                     "away, and both populations settle at (1, 2). Numerical "
                     "runs from (0.5, 0.5), (3, 4), (0.2, 5) and (2.5, 0.1) all "
                     "end there."),
            ),
        ),
        Box(
            "remark", "A quantity that only decreases",
            "Mimic equation 5 with the new equilibrium: W = x − ln x + y − "
            "2 ln y. The chain rule gives W' = (x − 1)(3 − x − y) + "
            "(y − 2)(x − 1) = −(x − 1)², which is never positive. W is no "
            "longer conserved but slides downhill. It is a Lyapunov function "
            "in the sense of the almost-linear chapter, playing the part of "
            "the V in its test (here the letter V is taken by the conserved "
            "quantity): it has a strict "
            "minimum at (1, 2), with second derivatives 1 and 1/2 and no "
            "mixed term, and W' ≤ 0, so the point is stable. As in the "
            "cubic-friction example there, W' vanishes on a whole line, "
            "x = 1, but a trajectory cannot stay on it, since x' = 2 − y ≠ 0 "
            "there except at the equilibrium. So W keeps decreasing and the "
            "point is asymptotically stable. Because W, like V, grows "
            "without bound towards the axes and far away, every level curve "
            "is a closed loop that traps whatever starts inside it, so the "
            "argument covers every start in the open quadrant. That proves "
            "what the numerical runs suggested.",
            r"W' = -(x - 1)^{2} \leq 0",
        ),
        Para(
            "The coexistence point exists only because the prey's capacity "
            "3 exceeds the predators' break-even level c/d = 1. With "
            "y' = y(x − 4) instead, the lines x + y = 3 and x = 4 cross at "
            "(4, −1), outside the quadrant. The Jacobian at (3, 0) then has "
            "rows (−3, −3) and (0, −1), eigenvalues −3 and −1: a stable node, "
            "and numerical runs from (0.5, 0.5), (3, 4), (6, 2) and (1, 5) "
            "all end at (3, 0). The predators die out, because prey held "
            "below the level the predators need cannot support them. "
            "Stronger crowding changes the answer in a different way. For "
            "x' = x(4 − 3x − y), y' = y(x − 1) the coexistence point is "
            "(1, 1), where the Jacobian has rows (−3, −1) and (1, 0): trace "
            "−3, determinant 1, discriminant 9 − 4 = 5 > 0. The eigenvalues "
            "(−3 ± √5)/2 are real and negative, so the spiral has become a "
            "stable node, and the populations settle without oscillating."
        ),
        Para(
            "The comparison is the point. The Lotka–Volterra centre is "
            "real, but it is fragile: add a little self-limitation and every "
            "cycle becomes a spiral into equilibrium. A model meant to "
            "explain populations that cycle steadily, with an amplitude that "
            "does not depend on how they started, needs an isolated cycle of "
            "one particular size, a limit cycle, and those are the subject "
            "of the limit-cycles chapter."
        ),
    )),
    Section("Competing species", (
        Para(
            "Now suppose neither species eats the other, but both eat the "
            "same food. Each alone grows logistically, and each is held back "
            "by the other in proportion to the product of the populations. "
            "Written out with all its constants, the model is "
            "x' = a₁x − b₁x² − c₁xy, y' = a₂y − b₂y² − c₂xy, with all six "
            "constants positive."
        ),
        Display(r"x' = x(a_1 - b_1 x - c_1 y), \qquad "
                r"y' = y(a_2 - b_2 y - c_2 x)", "6"),
        Para(
            "Alone, species x settles at its carrying capacity a₁/b₁ and "
            "species y at a₂/b₂. Measure each population in units of its own "
            "carrying capacity, x = (a₁/b₁)X and y = (a₂/b₂)Y. Substituting, "
            "the system becomes X' = a₁X(1 − X − αY) and "
            "Y' = a₂Y(1 − Y − βX), where two dimensionless numbers carry "
            "all the competition."
        ),
        Display(r"\alpha = \frac{c_1 a_2}{a_1 b_2}, \qquad "
                r"\beta = \frac{c_2 a_1}{a_2 b_1}", "7"),
        Para(
            "Their product is αβ = c₁c₂/(b₁b₂), in which the growth rates "
            "cancel. So the condition αβ < 1, which will decide stability "
            "below, reads b₁b₂ > c₁c₂ in the original constants: the "
            "self-limitation coefficients together outweigh the "
            "cross-competition coefficients. This is the form in which "
            "Edwards and Penney state it."
        ),
        Para(
            "The factors a₁ and a₂ in front only set how fast each species "
            "responds. They change neither the nullclines nor the type of "
            "any equilibrium: the next section checks this for the "
            "coexistence point, and at the others the Jacobian is diagonal "
            "or triangular, so its eigenvalues are only multiplied by the "
            "positive numbers a₁ and a₂. The chapter therefore works with "
            "the scaled model in which both are 1."
        ),
        Display(r"x' = x(1 - x - \alpha y), \qquad y' = y(1 - y - \beta x)",
                "8"),
        Para(
            "Here α measures how hard y competes with x, relative to how "
            "hard x competes with itself, and β measures the effect of x on "
            "y in the same way. The nullclines are the two axes and two "
            "straight lines. The x-nullcline line x + αy = 1 runs from "
            "(1, 0) on the x-axis to (0, 1/α) on the y-axis; the y-nullcline "
            "line y + βx = 1 runs from (0, 1) to (1/β, 0). Below the first "
            "line x grows, and below the second y grows."
        ),
        Para(
            "So the survival question is a question about intercepts. On "
            "the y-axis, the x-nullcline is above the y-nullcline exactly "
            "when 1/α > 1, that is when α < 1. On the x-axis the "
            "y-nullcline is further out exactly when β < 1. The two lines "
            "cross inside the quadrant precisely when they are in opposite "
            "orders on the two axes, which happens when α and β are both "
            "below 1 or both above 1."
        ),
        Worked(
            "A competition model, unscaled",
            "Find every equilibrium of x' = x(4 − 2x − y), y' = y(5 − x − 2y), "
            "classify each, and find α and β.",
            (
                Step("The x-nullcline is x = 0 or 2x + y = 4, the y-nullcline "
                     "y = 0 or x + 2y = 5. Pairing the pieces: the axes meet at "
                     "(0, 0); x = 0 with x + 2y = 5 gives (0, 5/2); y = 0 with "
                     "2x + y = 4 gives (2, 0); and the two lines cross where "
                     "subtracting twice the second from the first leaves "
                     "−3y = −6, so y = 2 and x = 1.",
                     r"(0, 0), \quad \left(0, \frac{5}{2}\right), \quad (2, 0), "
                     r"\quad (1, 2)"),
                Step("The Jacobian has rows (4 − 4x − y, −x) and "
                     "(−y, 5 − x − 4y). At the origin it is diagonal with 4 "
                     "and 5: an unstable node. At (2, 0) its rows are (−4, −2) "
                     "and (0, 3), eigenvalues −4 and 3: a saddle. At (0, 5/2) "
                     "they are (3/2, 0) and (−5/2, −5), eigenvalues 3/2 and −5: "
                     "a saddle."),
                Step("At (1, 2) the rows are (−2, −1) and (−2, −4): trace −6, "
                     "determinant 8 − 2 = 6, discriminant 36 − 24 = 12. Two "
                     "negative real eigenvalues, −3 ± √3, about −1.27 and "
                     "−4.73: a stable node, and hyperbolic, so genuine.",
                     r"\lambda = -3 \pm \sqrt{3}"),
                Step("With a₁ = 4, b₁ = 2, c₁ = 1 and a₂ = 5, b₂ = 2, c₂ = 1, "
                     "equation 7 gives α = 5/8 and β = 2/5, both below 1; in "
                     "the original constants, b₁b₂ = 4 > c₁c₂ = 1. Each "
                     "species limits itself more than it limits the other, and "
                     "the two coexist at (1, 2), which in scaled units is "
                     "(1/2, 4/5).",
                     r"\alpha = \frac{1 \cdot 5}{4 \cdot 2} = \frac{5}{8}, "
                     r"\qquad \beta = \frac{1 \cdot 4}{5 \cdot 2} = \frac{2}{5}"),
                Step("Read the sign regions. Below both lines (test point "
                     "(0.5, 0.5)) both species grow: up and right. Above both "
                     "((3, 3)) both shrink: down and left. In the wedge "
                     "touching the x-axis ((2.2, 0.5)), 2x + y = 4.9 > 4 and "
                     "x + 2y = 3.2 < 5, so x' < 0 < y': up and left. In the "
                     "wedge touching the y-axis ((0.2, 2.6)), 2x + y = 3 < 4 "
                     "and x + 2y = 5.4 > 5, so x' > 0 > y': down and right. "
                     "Every region points towards the crossing (1, 2), and a "
                     "trajectory entering a wedge cannot leave it again, since "
                     "on its edges the flow points inwards: on 2x + y = 4 it is "
                     "vertical and on x + 2y = 5 horizontal, both into the "
                     "wedge. This is the global half of the coexistence "
                     "verdict, read off the nullclines."),
            ),
        ),
    )),
    Section("Coexistence or exclusion", (
        Para(
            "Return to the scaled model 8. Its equilibria are the origin, "
            "the two single-species states (1, 0) and (0, 1), and possibly "
            "a coexistence point where the two lines cross. Solving "
            "x + αy = 1 and βx + y = 1 together gives it."
        ),
        Display(r"(x^{*}, y^{*}) = \left(\frac{1 - \alpha}{1 - \alpha\beta}, "
                r"\frac{1 - \beta}{1 - \alpha\beta}\right)", "9"),
        Para(
            "Both coordinates are positive when α, β < 1, since then "
            "αβ < 1 too, and also when α, β > 1, since then numerators and "
            "denominator are all negative. When one coefficient is below 1 "
            "and the other above, the coordinates have opposite signs and "
            "there is no coexistence point in the quadrant. (If αβ = 1 in "
            "this case, for instance α = 1/2 and β = 2, the lines are "
            "parallel and do not meet at all, which gives the same "
            "conclusion. When α = β = 1 the two lines coincide and every "
            "point of the segment is an equilibrium, a boundary case like "
            "the lines of equilibria of the phase-portraits chapter. When "
            "exactly one coefficient equals 1, the coexistence point lands "
            "on an axis and merges with a single-species state, whose "
            "Jacobian then has a zero eigenvalue; for β = 1, formula 9 gives "
            "(1, 0).)"
        ),
        Box(
            "theorem", "Stability of coexistence",
            "Suppose the coexistence point 9 lies in the open quadrant. If "
            "α < 1 and β < 1 it is a stable node; if α > 1 and β > 1 it is a "
            "saddle. It is never a spiral.",
            r"\operatorname{tr}J = -(x^{*} + y^{*}) < 0, \qquad "
            r"\det J = x^{*}y^{*}(1 - \alpha\beta)",
        ),
        Box(
            "proof", "Proof",
            "The Jacobian of 8 has rows (1 − 2x − αy, −αx) and "
            "(−βy, 1 − 2y − βx). At the coexistence point 1 − x* − αy* = 0, "
            "so the top-left entry is −x*, and likewise the bottom-right is "
            "−y*. The rows are (−x*, −αx*) and (−βy*, −y*), with the trace "
            "and determinant shown. The trace is negative. If α, β < 1 the "
            "determinant is positive, so the point is stable; if α, β > 1 it "
            "is negative, a saddle. Finally the discriminant is "
            "(x* + y*)² − 4x*y*(1 − αβ) = (x* − y*)² + 4αβx*y*, which is "
            "positive, so the eigenvalues are real. Both cases are "
            "hyperbolic, so the nonlinear system agrees.",
        ),
        Para(
            "Restoring the rates a₁ and a₂ multiplies the first row of the "
            "Jacobian by a₁ and the second by a₂. The trace stays negative, "
            "the determinant is multiplied by the positive number a₁a₂, and "
            "the discriminant becomes (a₁x* − a₂y*)² + 4a₁a₂αβx*y*, still "
            "positive. So nothing in the theorem depends on the scaling."
        ),
        Para(
            "The single-species states answer a different question: can a "
            "rare species invade? At (1, 0) the Jacobian has rows (−1, −α) "
            "and (0, 1 − β), with eigenvalues −1 and 1 − β. The eigenvalue "
            "−1 is species x returning to its own carrying capacity; the "
            "eigenvalue 1 − β is the per-capita growth rate of a few y "
            "introduced into a world full of x. So y can invade exactly when "
            "β < 1, and in the same way, at (0, 1) with eigenvalues −1 and "
            "1 − α, x can invade exactly when α < 1."
        ),
        Box(
            "theorem", "The four cases of competition",
            "For model 8 with populations starting in the open quadrant: if "
            "α < 1 and β < 1 the species coexist at the point 9; if α < 1 < β, "
            "species x wins and the populations tend to (1, 0); if "
            "β < 1 < α, species y wins; if α > 1 and β > 1 one species wins, "
            "and which one depends on where the populations start (apart "
            "from starting points on a single dividing curve, which lead to "
            "the coexistence saddle).",
        ),
        Para(
            "The linearisations prove the local half of each statement, and "
            "the nullcline sketch makes the global half convincing: in each "
            "case the sign regions funnel the flow towards the stable "
            "equilibria, as the last step of the unscaled example showed for "
            "coexistence. In the mixed cases there is an argument that needs "
            "no sketch. Divide each equation by its population and "
            "subtract."
        ),
        Display(r"\frac{d}{dt}\ln\frac{x}{y} = \frac{x'}{x} - \frac{y'}{y} = "
                r"(\beta - 1)x + (1 - \alpha)y", "10"),
        Para(
            "If α < 1 < β, both terms on the right are positive in the open "
            "quadrant, so ln(x/y) increases. It cannot level off at a finite "
            "value: the right side is at least m(x + y), where m is the "
            "smaller of β − 1 and 1 − α, and x + y cannot stay small for "
            "ever, because near the origin both species grow. So ln(x/y) "
            "grows without bound and x/y → ∞. The populations stay bounded, "
            "so y → 0, and then x tends to its carrying capacity 1. The "
            "species that competes harder wins, even if it starts far "
            "behind. In the mirror case α = 3/2, β = 1/2, for instance, the "
            "start (0.1, 0.9) reaches (4 × 10⁻⁷, 0.9999996) by t = 25, y "
            "having won. "
            "When exactly one coefficient equals 1, say α < 1 = β, equation "
            "10 still decides: the right side is (1 − α)y > 0, x/y still "
            "grows without bound, and x still wins, though slowly, because "
            "of the zero eigenvalue at (1, 0). The "
            "mathematical content of the competitive exclusion principle of "
            "ecology is exactly this: two species that compete too strongly "
            "for the same resource cannot both persist."
        ),
        Plot(
            "Coexistence: α = β = 1/2",
            "Nullclines of x' = x(1 − x − y/2), y' = y(1 − y − x/2). The "
            "x-nullcline x + y/2 = 1 runs off the top of the picture towards "
            "its intercept at y = 2, above the y-nullcline's intercept at 1, "
            "and the y-nullcline y + x/2 = 1 likewise meets the x-axis at 2, "
            "beyond the x-nullcline's intercept at 1. So they cross, at the "
            "stable node (2/3, 2/3). Because the model is symmetric the "
            "diagonal is a trajectory, and the two curves "
            "drawn along it are exact solutions from (0.1, 0.1) and from "
            "(1.2, 1.2), both arriving at the coexistence point.",
            (Curve("1 - 0.5*(1.3*t/8)", "x-nullcline", y="1.3*t/8"),
             Curve("1.3*t/8", "y-nullcline", y="1 - 0.65*t/8"),
             Curve("2/(3 + 17*exp(-t))", "solution from (0.1, 0.1)",
                   y="2/(3 + 17*exp(-t))"),
             Curve("6/(9 - 4*exp(-t))", "solution from (1.2, 1.2)",
                   y="6/(9 - 4*exp(-t))")),
            t=(0.0, 8.0), xlabel="x", ylabel="y", ylim=(0.0, 1.3),
        ),
        Worked(
            "Along the diagonal, exactly",
            "For α = β = 1/2, show that the diagonal x = y is a trajectory and "
            "solve with x(0) = y(0) = 1/10.",
            (
                Step("On x = y both equations become the same logistic "
                     "equation, x' = x(1 − x − x/2) = x(1 − 3x/2). So if the "
                     "two populations start equal they stay equal, by "
                     "uniqueness: the solution of the logistic equation, used "
                     "for both, satisfies the system.",
                     r"x' = x\left(1 - \frac{3}{2}x\right), \qquad "
                     r"K = \frac{2}{3}"),
                Step("The logistic solution with rate 1 and capacity K is "
                     "K/(1 + Ce^(−t)). From x(0) = 1/10, 1 + C = 20/3, so "
                     "C = 17/3.",
                     r"x = \frac{2/3}{1 + \frac{17}{3}e^{-t}} = "
                     r"\frac{2}{3 + 17e^{-t}}"),
                Step("Both populations rise together along the diagonal to "
                     "2/3, the coexistence point, as the stability theorem "
                     "predicts. The Jacobian there has rows (−2/3, −1/3) and "
                     "(−1/3, −2/3), with eigenvalue −1 along (1, 1) and −1/3 "
                     "along (1, −1). So the diagonal is the *fast* eigenline, "
                     "and by the slow-direction theorem of the "
                     "phase-portraits chapter most other trajectories make "
                     "their final approach along (1, −1), across the "
                     "diagonal, not along it."),
            ),
            equation="x' = x*(1 - x - y/2); y' = y*(1 - y - x/2)",
            conditions="x(0) = 1/10, y(0) = 1/10",
            answer="x = 2/(3 + 17*exp(-t))\ny = 2/(3 + 17*exp(-t))",
            answer_latex=r"x = y = \frac{2}{3 + 17e^{-t}}",
        ),
    )),
    Section("Bistability and the separatrix", (
        Para(
            "The last case is the most interesting. With α, β > 1 each "
            "species harms the other more than itself. Both single-species "
            "states are stable nodes, since at (1, 0) the eigenvalues are −1 "
            "and 1 − β < 0; the coexistence point is a saddle; and the "
            "origin is unstable. Its Jacobian is the identity, a repeated "
            "eigenvalue and so the soft case of the almost-linear chapter, "
            "but here it cannot become a spiral: both axes are trajectories, "
            "and nothing can wind round the origin across them. It is an "
            "unstable node. Two stable states "
            "compete for the quadrant, and something must divide it between "
            "them."
        ),
        Para(
            "That something is the stable curve of the saddle: the pair of "
            "trajectories that run into it, the nonlinear version of a "
            "saddle's stable line. Starting on one side, the populations "
            "end at (1, 0); on the other side, at (0, 1). The stable curve "
            "is a *separatrix*, a curve dividing different fates, as the "
            "pendulum's was in the equilibria chapter, and its two sides "
            "are the *basins of attraction* of the two winners."
        ),
        Worked(
            "The separatrix of a symmetric contest",
            "For α = β = 3/2, find the equilibria and their types, show that "
            "the diagonal is the separatrix, and solve along it from "
            "x(0) = y(0) = 1/10.",
            (
                Step("Equation 9 gives x* = y* =(−1/2)/(−5/4) = 2/5. The "
                     "Jacobian there has rows (−2/5, −3/5) and (−3/5, −2/5), "
                     "trace −4/5 and determinant 4/25 − 9/25 = −1/5: a saddle, "
                     "with eigenvalues −1 along (1, 1) and 1/5 along (1, −1). "
                     "At (1, 0) and (0, 1) the eigenvalues are −1 and −1/2: "
                     "stable nodes.",
                     r"\lambda = -1 \;\text{along}\; \binom{1}{1}, \qquad "
                     r"\lambda = \frac{1}{5} \;\text{along}\; \binom{1}{-1}"),
                Step("On the diagonal both equations reduce to "
                     "x' = x(1 − 5x/2), logistic with capacity 2/5. So the "
                     "diagonal is made of trajectories, and those on either "
                     "side of the saddle run into it: it is the saddle's "
                     "stable curve, in its eigendirection (1, 1).",
                     r"x' = x\left(1 - \frac{5}{2}x\right), \qquad "
                     r"x = \frac{2}{5 + 15e^{-t}}"),
                Step("Off the diagonal, equation 10 with α = β = 3/2 gives "
                     "(ln(x/y))' = (x − y)/2. If x > y the ratio x/y grows, so "
                     "x stays ahead and its lead widens; if x < y the reverse. "
                     "The lead cannot fade out: with r₀ = x(0)/y(0) > 1, the "
                     "ratio stays above r₀, so x − y is at least the fixed "
                     "fraction 1 − 1/r₀ of x, and x cannot stay small for ever "
                     "because the origin repels. As in the mixed case, ln(x/y) "
                     "then grows without bound, y → 0 and x → 1: whoever starts "
                     "ahead wins. Numerically, from (0.31, 0.3) "
                     "the populations end at (1, 0) and from (0.3, 0.31) at "
                     "(0, 1): a difference of 0.01 decides the contest."),
            ),
            equation="x' = x*(1 - x - 3*y/2); y' = y*(1 - y - 3*x/2)",
            conditions="x(0) = 1/10, y(0) = 1/10",
            answer="x = 2/(5 + 15*exp(-t))\ny = 2/(5 + 15*exp(-t))",
            answer_latex=r"x = y = \frac{2}{5 + 15e^{-t}}",
        ),
        Plot(
            "Bistability: α = β = 3/2",
            "Nullclines of x' = x(1 − x − 3y/2), y' = y(1 − y − 3x/2). Now "
            "the intercepts come in the other order: the x-nullcline meets "
            "the y-axis at 2/3, below the y-nullcline's 1, and the "
            "y-nullcline meets the x-axis at 2/3, inside the x-nullcline's "
            "1. They cross at the saddle (2/5, 2/5). The two exact "
            "solutions along the diagonal, from (0.1, 0.1) and (1.2, 1.2), both run into the "
            "saddle: "
            "together they make up its stable curve, the separatrix. Every "
            "population starting above the diagonal ends at (0, 1), and "
            "every one starting below it ends at (1, 0).",
            (Curve("1 - t/8", "x-nullcline", y="2*t/24"),
             Curve("2*t/24", "y-nullcline", y="1 - t/8"),
             Curve("2/(5 + 15*exp(-t))", "separatrix from (0.1, 0.1)",
                   y="2/(5 + 15*exp(-t))"),
             Curve("6/(15 - 10*exp(-t))", "separatrix from (1.2, 1.2)",
                   y="6/(15 - 10*exp(-t))")),
            t=(0.0, 8.0), xlabel="x", ylabel="y", ylim=(0.0, 1.3),
        ),
        Para(
            "Without the symmetry the separatrix is no longer a straight line "
            "and has no formula, but it is still the stable curve of the "
            "saddle, arriving at the saddle tangent to the stable "
            "eigenvector, and it still divides the quadrant into the two "
            "basins. The lesson's figure shows how the whole arrangement "
            "moves as the coefficients change."
        ),
        Figure(
            "competition",
            "The figure draws the scaled model x' = x(1 − x − ay), "
            "y' = y(1 − y − bx), so its sliders a and b are this chapter's α "
            "and β; each runs from 0.2 to 2.0 and both start near 0.5. It "
            "draws the nullclines dashed, four trajectories from (0.1, 0.9), "
            "(0.9, 0.1), (0.05, 0.05) and (1.2, 1.2), and every equilibrium "
            "(filled if stable), and its readout names the outcome. At the "
            "start all four trajectories meet at the stable node near "
            "(0.667, 0.667). Drag a up to about 1.5 with b still near 0.5: "
            "once a passes 1 the coexistence point leaves the quadrant, the "
            "readout says y drives the other out, and every trajectory ends "
            "at (0, 1). Drag a back down and b up to 1.5 for the mirror "
            "image. Then set both to about 1.5: the crossing becomes a "
            "saddle near (0.4, 0.4), the trajectory from (0.1, 0.9) ends at "
            "(0, 1) and the one from (0.9, 0.1) at (1, 0). If a and b are "
            "exactly equal, the two that start on the diagonal stay on it, "
            "since it is then the separatrix, and stop at the saddle itself. "
            "Move either slider a notch and they head for the saddle first "
            "and then turn off, towards (1, 0) if b is the larger and "
            "towards (0, 1) if a is. Finally "
            "try a and b both near 0.9: the node is still stable, but "
            "its slow eigenvalue is about −0.05, close to zero, and the "
            "trajectories from (0.1, 0.9) and (0.9, 0.1) have not reached it "
            "by the end of the drawing.",
        ),
    )),
    Section("Competitors never cycle", (
        Para(
            "Predators and prey cycle; competitors, it turns out, cannot. "
            "The stability theorem already showed that the coexistence "
            "point is never a spiral, so small oscillations about it cannot "
            "occur. A short argument rules out closed orbits of any size."
        ),
        Box(
            "theorem", "No closed orbits in competition",
            "Model 8 has no closed trajectory in the open quadrant x > 0, "
            "y > 0.",
            r"\frac{\partial}{\partial x}\left(\frac{1 - x - \alpha y}{y}\right) + "
            r"\frac{\partial}{\partial y}\left(\frac{1 - y - \beta x}{x}\right) = "
            r"-\frac{1}{y} - \frac{1}{x} < 0",
        ),
        Box(
            "proof", "Proof",
            "Write P = x'/(xy) = (1 − x − αy)/y and Q = y'/(xy) = "
            "(1 − y − βx)/x. Then ∂P/∂x = −1/y and ∂Q/∂y = −1/x, so "
            "∂P/∂x + ∂Q/∂y is negative throughout the quadrant. Suppose a "
            "closed trajectory C enclosed a region R. Along C, dx = x' dt and "
            "dy = y' dt, so P dy − Q dx = (x'y' − y'x') dt/(xy) = 0 and the "
            "line integral of P dy − Q dx round C is zero. By Green's "
            "theorem that line integral equals, up to a sign fixed by the "
            "direction of travel, the double integral of ∂P/∂x + ∂Q/∂y over "
            "R, which is strictly negative. The contradiction shows there is "
            "no such C.",
        ),
        Para(
            "Dividing by xy before taking the divergence is Dulac's "
            "criterion. If B > 0 and the divergence of (Bf, Bg) has one sign "
            "in a region without holes, there is no closed orbit there; the "
            "proof above is the case B = 1/(xy). With B = 1 it is "
            "Bendixson's criterion, which the limit-cycles chapter states "
            "and uses. Applied to the Lotka–Volterra system, the "
            "same division gives ∂/∂x((a − by)/y) + ∂/∂y((dx − c)/x) = 0: "
            "the divergence vanishes identically, as it should for a system "
            "whose orbits are closed, and the argument has nothing to say. "
            "For competitors the populations stay bounded, since x' < 0 "
            "whenever x > 1 and y' < 0 whenever y > 1. With no cycles "
            "possible, the Poincaré–Bendixson theorem of the limit-cycles "
            "chapter leaves each trajectory, in this model, no destination "
            "but an equilibrium or a chain of equilibria joined by "
            "trajectories. The chain cannot occur either. A loop of "
            "trajectories inside the open quadrant is ruled out by the same "
            "Green's-theorem argument, since P dy − Q dx vanishes along each "
            "piece of it. A loop that uses the axes must pass through the "
            "origin, because the only axis trajectories joining two equilibria "
            "run out of the origin, and the origin repels everything near it, "
            "so no trajectory can return to it. That is why the four cases "
            "above account for every starting point."
        ),
    )),
    Section("Common errors", (
        Box(
            "warning", "A crossing arrow on a nullcline is vertical or horizontal",
            "On the x-nullcline x' = 0, so the flow there points straight up "
            "or down; on the y-nullcline it points straight left or right. "
            "Drawing a crossing arrow sloping sideways misplaces every "
            "turning point, and it is the most common sketching mistake.",
        ),
        Para(
            "Other errors recur. The first is to linearise the "
            "Lotka–Volterra system at its coexistence point, find a centre, "
            "and conclude from that alone that the orbits are closed; or, "
            "remembering the almost-linear chapter, to stop at \"nothing can "
            "be said\". The centre decides nothing; the conserved quantity "
            "decides it. The second is to call the "
            "Lotka–Volterra cycles limit cycles. They are a continuum, one "
            "through every point, and a disturbance moves the populations to "
            "another cycle rather than back to the old one. The third is to "
            "read α < 1 as \"species y is weak\". It means y harms x less than "
            "x harms itself; coexistence needs this for both species at once. "
            "The fourth is to forget the axes, and with them the equilibria "
            "in which a species is extinct, which in a competition model are "
            "often the stable ones. The fifth is to take a slow approach to "
            "equilibrium, as in the figure near α = β = 0.9, for a failure to "
            "converge: a small eigenvalue means a long wait, not a different "
            "answer."
        ),
    )),
    Section("Summary", (
        Para(
            "The nullclines f = 0 and g = 0 locate every equilibrium at "
            "their crossings, are crossed vertically and horizontally by the "
            "flow, and cut the plane into regions where the direction of "
            "motion is fixed. For predator and prey, x' = ax − bxy, "
            "y' = −cy + dxy, they are the axes and the lines y = a/b and "
            "x = c/d. The origin is a saddle and the coexistence point "
            "(c/d, a/b) linearises to an undecided centre, which the "
            "conserved quantity V = dx − c ln x + by − a ln y settles: its "
            "level curves are closed, so the populations cycle for ever, "
            "each on its own loop, with prey peaks leading predator peaks "
            "and the equilibrium equal to the average over a cycle. That is "
            "why fishing both species favours the prey. Self-limitation of "
            "the prey turns the centre into a stable spiral. For competitors "
            "scaled to x' = x(1 − x − αy), y' = y(1 − y − βx), the "
            "coexistence point is a stable node when α, β < 1 and a saddle "
            "when α, β > 1, never a spiral; when one coefficient exceeds 1 "
            "and the other does not, the stronger competitor excludes the "
            "weaker, and in the bistable case the saddle's stable curve "
            "divides the starting points by winner. The next chapter finds "
            "a conserved quantity of another kind, the energy of a "
            "pendulum, and its saddles' separatrices divide swinging from "
            "going over the top."
        ),
    )),
)


MECHANICS = (
    Section("Knowing what a swing does without solving it", (
        Para(
            "The pendulum equation x'' + sin x = 0 has no solution in "
            "elementary functions. The eigenvalue method, undetermined "
            "coefficients and the Laplace transform all rest on superposition, "
            "and superposition is lost the moment the unknown sits inside a "
            "sine. Yet anyone who has pushed a child on a swing knows exactly "
            "what the pendulum does. A small push gives a swing back and forth. "
            "A bigger push gives a bigger swing, which takes a little longer. "
            "A big enough push sends the swing over the top, and after that it "
            "keeps going round."
        ),
        Para(
            "None of that knowledge is a formula for x(t). It is a statement "
            "about energy: the push supplies kinetic energy, climbing converts "
            "it into potential energy, and whether the swing reaches the top "
            "depends only on whether it has enough energy to get there. This "
            "chapter turns that intuition into mathematics. For a whole class "
            "of nonlinear systems, those with no friction, the energy is "
            "constant along every solution, and so every trajectory lies on "
            "one curve E(x, y) = constant in the phase plane. The phase "
            "portrait is then a contour map of the energy, and a contour map "
            "can be drawn without solving any differential equation."
        ),
        Para(
            "The first two chapters of the unit found the equilibria of a "
            "nonlinear system and classified them by linearising, and the "
            "almost-linear chapter warned that a linearisation predicting a "
            "centre decides nothing. The pendulum's hanging position is "
            "exactly such a case. The energy settles it, and it does more: it "
            "draws the whole portrait, including the one special curve, the "
            "separatrix, that divides swinging from going over the top."
        ),
    )),
    Section("Conservative systems and their energy", (
        Para(
            "Consider a particle on a line whose acceleration depends only on "
            "its position, x'' = F(x). Any continuous F is minus the derivative "
            "of some function V, called the potential: take V(x) = −∫F(x) dx. "
            "Writing the equation with the potential and introducing the "
            "velocity y = x' as a second unknown gives a planar autonomous "
            "system of the kind this unit studies."
        ),
        Display(r"x' = y, \qquad y' = -V'(x)", "1"),
        Para(
            "Multiply the second equation by y. The left side, y y', is the "
            "derivative of y²/2. The right side, −V'(x) y, is −V'(x) x', which "
            "by the chain rule is the derivative of −V(x). Both sides are "
            "exact derivatives, so their difference is a derivative that "
            "vanishes."
        ),
        Display(r"y\,y' + V'(x)\,x' = 0 \;\Longrightarrow\; \frac{d}{dt}"
                r"\left(\frac{1}{2}y^{2} + V(x)\right) = 0", "2"),
        Box(
            "definition", "Energy, conservative system, first integral",
            "For the system x' = y, y' = −V'(x), the function "
            "E(x, y) = y²/2 + V(x) is the energy: y²/2 is the kinetic energy "
            "(per unit mass) and V(x) the potential energy. A system with a "
            "function of the state that is constant along every solution, and "
            "not constant on any open region of the plane, is called "
            "conservative, and such a function is a first integral or "
            "conserved quantity.",
            r"E(x, y) = \frac{1}{2}y^{2} + V(x)",
        ),
        Box(
            "theorem", "Energy is conserved",
            "Along every solution of x' = y, y' = −V'(x), the energy "
            "E(x(t), y(t)) is constant. Every trajectory therefore lies on a "
            "single level curve E(x, y) = E₀, where E₀ is the energy of its "
            "starting point.",
            r"\frac{dE}{dt} = E_x\,x' + E_y\,y' = V'(x)\,y + y\,(-V'(x)) = 0",
        ),
        Box(
            "proof", "Proof",
            "By the chain rule, dE/dt = E_x x' + E_y y'. Here E_x = V'(x) and "
            "x' = y, while E_y = y and y' = −V'(x), so the two products are "
            "V'(x) y and −y V'(x). They cancel for every x and y, so the "
            "derivative is identically zero and E is constant on each "
            "solution.",
        ),
        Para(
            "The pendulum is the case F(x) = −sin x, with V(x) = −cos x, and "
            "its energy is E = y²/2 − cos x. The constant in V can be chosen "
            "freely; this choice puts the bottom of the swing at V = −1 and "
            "the top at V = 1. The equation here is nondimensional. A real "
            "pendulum of length L obeys x'' + (g/L) sin x = 0, and measuring "
            "time in units of √(L/g) removes the constant, so a small swing, "
            "whose period is 2π in these units, takes 2π√(L/g) seconds."
        ),
        Para(
            "Conserved quantities are not special to mechanics. The "
            "ecological-models chapter found one for the predator–prey system by "
            "dividing its two equations and separating the variables, and its "
            "closed level curves proved that the populations cycle. Here the "
            "conserved quantity is the physical energy, and the level curves "
            "can be read off the graph of a function of one variable."
        ),
    )),
    Section("Orbits are level curves", (
        Para(
            "The same energy comes out of the orbit equation. Away from the "
            "x-axis, where y ≠ 0, dividing y' by x' eliminates the time and "
            "gives the slope of a trajectory as a function of position. That "
            "equation is separable, and separating it is the energy argument "
            "in another notation."
        ),
        Display(r"\frac{dy}{dx} = -\frac{V'(x)}{y} \;\Longrightarrow\; "
                r"y\,dy = -V'(x)\,dx \;\Longrightarrow\; \frac{1}{2}y^{2} = "
                r"-V(x) + C", "3"),
        Para(
            "So a single integration gives every orbit, even though no "
            "integration will give x(t). In the worked examples the "
            "independent variable of the orbit equation is the position x, "
            "which the course's solver writes as t because it writes every "
            "independent variable as t: an equation y' = −4t/y below is the "
            "slope equation dy/dx = −4x/y. The time has not come back; it has "
            "been renamed."
        ),
        Worked(
            "The harmonic oscillator's orbits are ellipses",
            "The linear oscillator x'' + 4x = 0 has V(x) = 2x². Find the orbit "
            "through (0, 2), the mass passing its rest position with speed 2, "
            "and describe it.",
            (
                Step("The orbit equation is dy/dx = −4x/y. Separating gives "
                     "y dy = −4x dx, and integrating gives y²/2 = −2x² + C.",
                     r"\frac{1}{2}y^{2} + 2x^{2} = C"),
                Step("At (0, 2) the left side is 2, so C = 2 and "
                     "y² = 4 − 4x². On the upper half, where y > 0, this is the "
                     "answer; the lower half is its reflection.",
                     r"y = 2\sqrt{1 - x^{2}}"),
                Step("Read it. The level curve y²/4 + x² = 1 is an ellipse "
                     "with semi-axes 1 along x and 2 along y. The mass swings "
                     "out to x = ±1, where y = 0 and it turns, and is fastest "
                     "at x = 0. This is the centre of the phase-portraits "
                     "chapter, found this time without any eigenvalue."),
            ),
            equation="y' = -4*t/y",
            conditions="y(0) = 2",
            answer="y = 2*sqrt(1 - t**2)",
            answer_latex=r"y = 2\sqrt{1 - x^{2}}",
        ),
        Para(
            "For a linear restoring force the potential is a parabola and "
            "every level curve is an ellipse. The interesting cases are the "
            "ones where the potential is not a parabola."
        ),
        Worked(
            "A hardening spring",
            "The oscillator x'' + x³ = 0 has a restoring force that grows "
            "faster than the displacement, like a spring that stiffens as it "
            "is stretched. Find its energy and the orbit through (0, 2), and "
            "say how far the mass swings.",
            (
                Step("Here −V'(x) = −x³, so V(x) = x⁴/4 and the energy is "
                     "y²/2 + x⁴/4. The orbit equation dy/dx = −x³/y separates "
                     "to y dy = −x³ dx.",
                     r"\frac{1}{2}y^{2} + \frac{1}{4}x^{4} = C"),
                Step("At (0, 2) the energy is 2, so y² = 4 − x⁴/2.",
                     r"y = \sqrt{4 - \frac{x^{4}}{2}}"),
                Step("The mass turns where y = 0, at x⁴ = 8, so x = ±8^(1/4) "
                     "≈ ±1.68. The orbit is a closed curve round the origin, "
                     "flatter at its ends than an ellipse, because the "
                     "quartic potential has a flat bottom and steep walls. "
                     "Notice what decides this. Here V''(0) = 0, and the "
                     "Jacobian at the origin, rows (0, 1) and (0, 0), has a "
                     "double zero eigenvalue, so the linearisation says "
                     "nothing (the almost-linear chapter's section 'Zero "
                     "eigenvalues decide nothing either'). The energy still "
                     "does: x⁴/4 has a strict minimum at 0, so the level "
                     "curves close and the origin is a centre."),
                Step("The equation also shows at once that the period "
                     "depends on the amplitude. If u(t) solves u'' + u³ = 0, "
                     "so does x(t) = A u(At), since x'' = A³u''(At) = "
                     "−A³u(At)³ = −x³. Swinging with amplitude A is swinging "
                     "with amplitude 1 run A times as fast, so the period is "
                     "T(1)/A. Numerically T(1) ≈ 7.42, so the orbit of this "
                     "example, amplitude 8^(1/4) ≈ 1.68, has period "
                     "7.42/1.68 ≈ 4.41, and an amplitude-2 swing takes only "
                     "≈ 3.71: the harder the spring is pushed, the faster it "
                     "oscillates. No linear oscillator does that. (T(1) is "
                     "exactly the pendulum's 90° period met later, 4K(1/√2) "
                     "in the notation of equation 8; the two integrals are "
                     "the same after a substitution, so this is no misprint.)",
                     r"T(A) = \frac{T(1)}{A}"),
                Step("The energy also gives the top speed without solving "
                     "anything. Released from rest at x = A in the general "
                     "hardening spring x'' + k x³ = 0, the energy is kA⁴/4, "
                     "all potential. At x = 0 it is all kinetic, so "
                     "y²/2 = kA⁴/4 and the greatest speed is A²√(k/2). For "
                     "k = 2 and A = 1 that is exactly 1; for this example's "
                     "k = 1 and A = 8^(1/4) it is √8/√2 = 2, the speed it "
                     "started with, as it must be.",
                     r"|y|_{\max} = A^{2}\sqrt{\frac{k}{2}}"),
            ),
            equation="y' = -t**3/y",
            conditions="y(0) = 2",
            answer="y = sqrt(4 - t**4/2)",
            answer_latex=r"y = \sqrt{4 - \frac{x^{4}}{2}}",
        ),
    )),
    Section("Reading the phase plane from the potential", (
        Para(
            "Since y²/2 is never negative, a trajectory with energy E can "
            "only visit positions where V(x) ≤ E. That turns the graph of V "
            "into a map of the motion. Draw the horizontal line at height E "
            "across the graph of the potential. The particle is confined to "
            "the intervals where the graph lies below the line; its speed at "
            "position x is √(2(E − V(x))), greatest where the potential is "
            "lowest; and where the line meets the graph the speed is zero, "
            "the particle stops and turns back. Those points are the turning "
            "points."
        ),
        Display(r"|y| = \sqrt{2\,(E - V(x))}, \qquad V(x) \leq E", "4"),
        Para(
            "Picture a bead sliding without friction on a wire bent into the "
            "shape of the graph of V. The bead rolls down into the valleys, "
            "up the slopes, and back, and a horizontal line at the level of "
            "its energy marks how high it can climb. Each level curve of E "
            "in the phase plane is the pair of graphs y = ±√(2(E − V(x))) over "
            "one allowed interval: the upper branch is the particle moving "
            "right, the lower branch moving left, and the two meet at the "
            "turning points, where the curve crosses the x-axis vertically."
        ),
        Plot(
            "The pendulum's potential and three energy levels",
            "The potential V(x) = −cos x over two full turns, with three "
            "energy levels. At E = −1/2 the line cuts the central well at "
            "x = ±π/3, so a pendulum with that energy hanging near x = 0 "
            "swings between −60° and 60°; the neighbouring wells are the same "
            "pendulum a full turn round. At "
            "E = 1 the line just touches the maxima at x = ±π, the inverted "
            "positions. At E = 3/2 the line is above the whole graph: no "
            "turning points, and the pendulum goes round for ever.",
            (Curve("-cos(t)", "V(x) = −cos x"),
             Curve("0*t - 0.5", "E = −1/2: swinging"),
             Curve("0*t + 1", "E = 1: separatrix"),
             Curve("0*t + 1.5", "E = 3/2: rotating")),
            t=(-6.2832, 6.2832), xlabel="x (angle)", ylabel="V(x) and E",
            ylim=(-1.3, 1.8),
        ),
        Para(
            "The equilibria of system 1 are the points where y = 0 and "
            "V'(x) = 0, the critical points of the potential on the x-axis. "
            "What kind of equilibrium each one is depends on whether the "
            "potential has a minimum or a maximum there, and the energy "
            "decides even the case the linearisation cannot."
        ),
        Box(
            "theorem", "Minima of V are centres, maxima are saddles",
            "Let V be twice continuously differentiable, with V'(x*) = 0 and "
            "no other critical point of V nearby. If V has a strict local "
            "minimum at x* (in particular if V''(x*) > 0), then (x*, 0) is a "
            "centre of the nonlinear system: every orbit near it is a closed "
            "curve round it, travelled periodically. If V''(x*) < 0, a strict "
            "maximum, then (x*, 0) is a saddle.",
            r"V \text{ has a strict minimum at } x^{*} \;\Longrightarrow\; "
            r"\text{centre}, \qquad V''(x^{*}) < 0 \;\Longrightarrow\; "
            r"\text{saddle}",
        ),
        Box(
            "proof", "Proof",
            "The Jacobian of x' = y, y' = −V'(x) at (x*, 0) has rows (0, 1) "
            "and (−V''(x*), 0), so its trace is 0 and its determinant is "
            "V''(x*). If V''(x*) < 0 the determinant is negative, the "
            "eigenvalues are ±√(−V''(x*)), real and of opposite signs, and the "
            "equilibrium is hyperbolic; by the almost-linear chapter's "
            "theorem it is a genuine saddle. At a minimum the Jacobian is no "
            "help: V''(x*) > 0 gives eigenvalues ±i√(V''(x*)), a linear "
            "centre, and V''(x*) = 0 gives a double zero eigenvalue, and "
            "neither decides anything. Use the energy instead. "
            "E(x, y) − E(x*, 0) = y²/2 + (V(x) − V(x*)), which is positive at "
            "every point near (x*, 0) except the point itself. Because V "
            "falls to its minimum on one side of x* and rises on the other, "
            "each level E = V(x*) + c with c small and positive is the pair "
            "of graphs y = ±√(2(V(x*) + c − V(x))) over a short interval "
            "round x*: a small closed loop round the point. A trajectory "
            "stays on its loop and the loop contains no equilibrium; even at "
            "the turning points, where y = 0, y' = −V'(x) ≠ 0. So the speed "
            "along the loop is bounded away from zero, and the trajectory "
            "goes round the whole loop in a finite time and repeats: a "
            "periodic orbit. This is the almost-linear chapter's "
            "conserved-quantity theorem, freed of its requirement of positive "
            "second derivatives, which the special form of E allows.",
        ),
        Para(
            "One consequence deserves its own statement, because it is the "
            "sharpest difference between a conservative system and one with "
            "friction."
        ),
        Box(
            "theorem", "A conservative system has no attracting equilibrium",
            "If E is a first integral of a planar system, no equilibrium can "
            "be asymptotically stable. In particular a conservative system "
            "has no stable nodes and no stable spirals.",
        ),
        Box(
            "proof", "Proof",
            "Suppose every solution starting in some disc round the "
            "equilibrium p tended to p. E is constant on each of those "
            "solutions and continuous, so its constant value is the limit "
            "E(p). Then E would equal E(p) at every point of the disc, "
            "contradicting the requirement that a first integral is not "
            "constant on any open region.",
        ),
    )),
    Section("The pendulum's phase plane", (
        Para(
            "For x'' + sin x = 0 the potential −cos x has minima at "
            "x = 0, ±2π, … and maxima at x = ±π, ±3π, … . The equilibria are "
            "therefore (2kπ, 0), the pendulum hanging straight down, and "
            "((2k + 1)π, 0), the pendulum balanced upright. The Jacobian at "
            "(x*, 0) has rows (0, 1) and (−cos x*, 0). At the bottom that is "
            "rows (0, 1) and (−1, 0), eigenvalues ±i; at the top it is rows "
            "(0, 1) and (1, 0), eigenvalues ±1. By the theorem of the previous "
            "section the bottom is a genuine centre and the top a saddle, "
            "which is what the Phase Portrait screen draws for the pendulum "
            "preset."
        ),
        Display(r"E(x, y) = \frac{1}{2}y^{2} - \cos x", "5"),
        Para(
            "Because the potential is periodic, the picture repeats every 2π "
            "in x, and it is enough to understand one cell, −π ≤ x ≤ π. The "
            "energy is at least −1, attained only at the bottom at rest, and "
            "the level E = 1 is the height of the maxima. That sorts every "
            "motion into one of three families."
        ),
        Para(
            "If −1 < E < 1 the horizontal line meets the cosine graph, the "
            "pendulum has turning points at ±x_max with cos x_max = −E, and "
            "it swings back and forth between them. These closed orbits nest "
            "round the centre; physicists call the motion libration. If "
            "E > 1 the line is above the graph, y never vanishes, and the "
            "pendulum goes over the top and round for ever, fastest at the "
            "bottom and slowest at the top: rotation. Since x and x + 2π are "
            "the same position, a rotation is also periodic: after each full "
            "turn the state repeats. Rolled up so that x = −π and x = π meet, "
            "the phase plane becomes a cylinder, and rotations are closed "
            "loops going round it. The time for one turn is "
            "∫ dx/√(2(E + cos x)) from −π to π; at E = 3/2 it is about 4.04. "
            "The dividing level "
            "E = 1 is the separatrix, and it has a section of its own below. "
            "Starting from the bottom with speed v, the energy is v²/2 − 1, "
            "so the dividing speed is exactly 2."
        ),
        Worked(
            "A pendulum released from horizontal",
            "A pendulum is held horizontal, x = π/2, and released from rest. "
            "Find its speed as a function of its angle and its speed at the "
            "bottom.",
            (
                Step("At release E = 0 − cos(π/2) = 0. So along the whole "
                     "motion y²/2 − cos x = 0.",
                     r"\frac{1}{2}y^{2} = \cos x"),
                Step("Equivalently, the orbit equation dy/dx = −sin x / y "
                     "separates to y²/2 = cos x + C, and passing through "
                     "(π/2, 0) or through the bottom with speed √2 gives "
                     "C = 0. The branch through the bottom moving right is "
                     "the positive root.",
                     r"y = \sqrt{2\cos x}"),
                Step("At the bottom the speed is √2 ≈ 1.41, below the "
                     "dividing speed 2, as it must be for E = 0 < 1. The "
                     "speed falls to zero at x = ±π/2, so the pendulum swings "
                     "between the two horizontals, and the orbit is a closed "
                     "curve inside the separatrix. The small-swing period is "
                     "2π; this swing, as a later section computes, takes "
                     "about 7.42, some 18% longer."),
            ),
            equation="y' = -sin(t)/y",
            conditions="y(0) = sqrt(2)",
            answer="y = sqrt(2*cos(t))",
            answer_latex=r"y = \sqrt{2\cos x}",
        ),
        Plot(
            "The pendulum's phase plane",
            "One cell of the pendulum's portrait, −π ≤ x ≤ π. The closed "
            "curves are swings with energy −0.5, 0.445 and 0.882 (amplitudes "
            "60°, about 116° and about 152°). The two arcs y = ±2 cos(x/2), "
            "meeting at the saddles (±π, 0), are the separatrix, E = 1. The "
            "wavy curves outside are rotations at E = 3/2: they never reach "
            "y = 0, and the lowest point of the upper one, speed 1 at x = ±π, "
            "is the pendulum passing over the top. Swings run clockwise: "
            "right along the top, left along the bottom. Each curve has its "
            "own colour, named in the legend.",
            (Curve("t", "separatrix, upper", y="2*cos(t/2)"),
             Curve("t", "separatrix, lower", y="-2*cos(t/2)"),
             Curve("2*asin(0.5*sin(t))", "swing, 60°", y="2*0.5*cos(t)"),
             Curve("2*asin(0.85*sin(t))", "swing, 116°", y="2*0.85*cos(t)"),
             Curve("2*asin(0.97*sin(t))", "swing, 152°", y="2*0.97*cos(t)"),
             Curve("t", "rotation, rightwards", y="sqrt(2*(1.5 + cos(t)))"),
             Curve("t", "rotation, leftwards", y="-sqrt(2*(1.5 + cos(t)))")),
            t=(-3.1416, 3.1416), xlabel="x (angle)", ylabel="y (angular velocity)",
            ylim=(-3.0, 3.0),
        ),
        Para(
            "The swings in the plot are drawn from a parametrisation worth "
            "knowing. Put k = sin(x_max/2), which lies between 0 and 1 for a "
            "swing. Then the curve x = 2 arcsin(k sin s), y = 2k cos s, as s "
            "runs from −π to π, has y²/2 − cos x = 2k² − 1 for every s, so it "
            "is the level curve of energy 2k² − 1, and it reaches x = ±x_max "
            "where sin s = ±1. For a start at the bottom with speed v, k is "
            "simply v/2."
        ),
    )),
    Section("The separatrix", (
        Para(
            "The level E = 1 passes through the saddles. On it "
            "y² = 2(1 + cos x), and the half-angle identity 1 + cos x = "
            "2 cos²(x/2) turns that into a clean formula. In the cell "
            "−π ≤ x ≤ π, cos(x/2) ≥ 0, so no absolute value is needed."
        ),
        Display(r"E = 1 \;\Longleftrightarrow\; y = \pm 2\cos\frac{x}{2}", "6"),
        Box(
            "definition", "Separatrix",
            "A separatrix is a trajectory, or a curve made of trajectories "
            "and equilibria, that divides the phase plane into regions of "
            "qualitatively different behaviour. For the pendulum it is the "
            "level curve E = 1: inside it the pendulum swings, outside it "
            "the pendulum rotates. Each of its arcs runs from one saddle to "
            "the next, so it is made of the stable and unstable curves of the "
            "saddles, joined up.",
        ),
        Worked(
            "The orbit on the separatrix",
            "Solve the pendulum's orbit equation through the bottom with "
            "speed exactly 2, and find where the speed vanishes.",
            (
                Step("Separate dy/dx = −sin x / y: y²/2 = cos x + C. At (0, 2), "
                     "2 = 1 + C, so C = 1 and the energy is y²/2 − cos x = 1.",
                     r"y^{2} = 2 + 2\cos x = 4\cos^{2}\frac{x}{2}"),
                Step("Take the positive root on −π < x < π, where cos(x/2) > 0.",
                     r"y = 2\cos\frac{x}{2}"),
                Step("The speed vanishes where cos(x/2) = 0, at x = ±π, the "
                     "inverted positions, and nowhere before. So an orbit "
                     "started here arrives at the balance point with no speed "
                     "left over. That is what E = 1 means: exactly enough "
                     "energy to reach the top, and none to spare."),
            ),
            equation="y' = -sin(t)/y",
            conditions="y(0) = 2",
            answer="y = 2*cos(t/2)",
            answer_latex=r"y = 2\cos\frac{x}{2}",
        ),
        Para(
            "Does the pendulum on the separatrix reach the top, stop, and "
            "fall back? It does not, and the reason is general. As the first "
            "chapter of the unit showed, uniqueness forbids a trajectory from "
            "reaching an equilibrium in finite time: at the moment of arrival "
            "it would share a point with the constant solution, and so would "
            "have been that constant solution all along. Equilibria are "
            "approached, never reached."
        ),
        Para(
            "For the pendulum the separatrix orbit can even be written down "
            "in time. On it x' = y = 2 cos(x/2), a separable equation for x "
            "alone, and its solution with x(0) = 0 turns out to be the one "
            "in the next example. The first chapter drew this curve against "
            "the saddle's eigenlines; here we verify it and measure the "
            "approach."
        ),
        Worked(
            "The separatrix in time",
            "Verify that x = 2 arctan(sinh t), y = 2 sech t solves the "
            "pendulum system x' = y, y' = −sin x with x(0) = 0, y(0) = 2, and "
            "use it to find how long the pendulum takes to come within 0.01 "
            "radian of the top.",
            (
                Step("Differentiate: x' = 2 cosh t / (1 + sinh² t) = "
                     "2/cosh t = y. Write u = arctan(sinh t), so sin u = tanh t "
                     "and cos u = sech t; then sin x = sin 2u = 2 tanh t sech t, "
                     "and y' = −2 sech t tanh t = −sin x. At t = 0 both "
                     "conditions hold.",
                     r"x = 2\arctan(\sinh t), \qquad y = \frac{2}{\cosh t}"),
                Step("As t → ∞, sinh t → ∞, so x → 2(π/2) = π and y → 0. The "
                     "pendulum creeps up to the inverted position, never "
                     "reaching it, exactly as uniqueness requires. For t > 0 "
                     "the remaining angle is π − x = 2 arctan(1/sinh t), which "
                     "is about 4e^(−t) once t is a few units.",
                     r"\pi - x = 2\arctan\frac{1}{\sinh t} \approx 4e^{-t}"),
                Step("So the gap shrinks by a factor e each unit of time, the "
                     "rate set by the saddle's stable eigenvalue −1, since the "
                     "orbit arrives along the stable direction. The angle is "
                     "about 99° at t = 1, 168.6° at t = 3 and 178.5° at t = 5, "
                     "and it is within 0.01 radian of π when 4e^(−t) = 0.01, "
                     "at t = ln 400 ≈ 5.99. At t = 10 it is still 0.00018 "
                     "short, and it is short for ever."),
            ),
            equation="x' = y; y' = -sin(x)",
            conditions="x(0) = 0, y(0) = 2",
            answer="x = 2*atan(sinh(t))\ny = 2/cosh(t)",
            answer_latex=r"x = 2\arctan(\sinh t), \qquad y = 2\,\mathrm{sech}\,t",
        ),
        Para(
            "Just below the separatrix the pendulum comes close to the top, "
            "lingers there for a long time and falls back. Just above it, it "
            "lingers and then creeps over. The two motions are almost the "
            "same for a long stretch, and then completely different, which is "
            "why the separatrix is called a boundary between fates. A "
            "trajectory that joins two different saddles, like each arc of "
            "the pendulum's separatrix, is called heteroclinic; one that "
            "leaves a saddle and returns to the same one is homoclinic, and "
            "the section on two wells has an example."
        ),
    )),
    Section("How long a swing takes", (
        Para(
            "The energy gives the orbit without the time, but the time can be "
            "recovered from it by one more integration. Along the upper "
            "branch dx/dt = y = √(2(E − V(x))), so dt = dx / y. A swing between "
            "turning points x₁ and x₂ covers the upper branch one way and the "
            "lower branch back, taking the same time on each."
        ),
        Display(r"T = 2\int_{x_1}^{x_2} \frac{dx}{\sqrt{2\,(E - V(x))}}", "7"),
        Para(
            "For the pendulum with amplitude x_max, the substitution "
            "sin(x/2) = k sin φ, with k = sin(x_max/2), removes the square-root "
            "singularities at the turning points and turns equation 7 into "
            "four times the complete elliptic integral of the first kind, a "
            "standard special function tabulated and built into every "
            "numerical library."
        ),
        Display(r"T = 4K(k), \qquad K(k) = \int_{0}^{\pi/2} "
                r"\frac{d\phi}{\sqrt{1 - k^{2}\sin^{2}\phi}}", "8"),
        Para(
            "When k is small the integrand is nearly 1, K is nearly π/2 and "
            "T is nearly 2π, the linear value. As the amplitude grows, so "
            "does the period: 6.295 at 10°, 6.534 at 45°, 7.416 at 90°, "
            "9.600 at 135°, 15.33 at 170° and 24.51 at 179°. These values "
            "agree to four figures with periods measured by integrating the "
            "pendulum numerically with the course's own solver. For small "
            "amplitudes A (in radians) a good approximation is "
            "T ≈ 2π(1 + A²/16), which gives 6.525 at 45° against the true "
            "6.534, but only 7.25 at 90° against 7.42."
        ),
        Para(
            "Near the separatrix the period grows without bound. As k → 1 the "
            "integrand of K blows up at φ = π/2, and K grows like "
            "ln(4/√(1 − k²)). In terms of the energy this is "
            "T ≈ 2 ln(32/(1 − E)): the period is logarithmic in how far the "
            "energy falls short of 1. At 170° the approximation gives 15.31 "
            "against the true 15.33. The logarithm is the time spent "
            "lingering near the saddle, the finite-time version of the "
            "separatrix orbit's infinite wait."
        ),
        Worked(
            "The swing at speed 1.9",
            "An undamped pendulum starts at the bottom with speed 1.9. How far "
            "does it swing, and how long does a full swing take?",
            (
                Step("The energy is 1.9²/2 − 1 = 0.805. That is less than 1, so "
                     "the orbit lies inside the separatrix and the pendulum "
                     "swings rather than going over.",
                     r"E = \frac{1.9^{2}}{2} - 1 = 0.805 < 1"),
                Step("The turning points satisfy cos x_max = −E = −0.805, so "
                     "x_max ≈ 2.506 radians ≈ 143.6°. The pendulum rises well "
                     "above the horizontal and stops about 36° short of "
                     "vertical.",
                     r"x_{\max} = \arccos(-0.805) \approx 2.506"),
                Step("The modulus is k = sin(x_max/2). Since "
                     "sin²(x_max/2) = (1 − cos x_max)/2 = (1 + E)/2 = v²/4, "
                     "k = v/2 = 0.95 without any trigonometry. Then "
                     "T = 4K(0.95) ≈ 10.36, which a numerical integration "
                     "confirms.",
                     r"T = 4K(0.95) \approx 10.36"),
                Step("The period is 1.65 times the small-swing period 2π. The "
                     "logarithmic estimate 2 ln(32/0.195) ≈ 10.20 is already "
                     "within 2%, because at E = 0.805 the orbit is close "
                     "enough to the separatrix that the time near the top "
                     "dominates."),
            ),
        ),
    )),
    Section("Two wells: a homoclinic orbit", (
        Para(
            "The pendulum's potential has one kind of valley repeated for "
            "ever. The potential V(x) = −x²/2 + x⁴/4 has two valleys and a "
            "hump between them, and it is the undamped form of the Duffing "
            "oscillator the almost-linear chapter linearised, x'' = x − x³. "
            "Think of a steel strip buckled by two magnets, which can rest "
            "bent towards either one. Its equilibria are the critical points "
            "of V: V'(x) = −x + x³ = 0 at x = 0 and x = ±1."
        ),
        Display(r"E(x, y) = \frac{1}{2}y^{2} - \frac{1}{2}x^{2} + "
                r"\frac{1}{4}x^{4}", "9"),
        Para(
            "The almost-linear chapter used exactly this energy to prove that "
            "the wells (±1, 0), at energy −1/4, are genuine centres and the "
            "origin, at energy 0, a saddle, and it drew the figure eight "
            "E = 0. On the Phase Portrait screen's Duffing preset, with the "
            "damping δ set to 0 (its default is 0.2), the fixed-point finder "
            "reports the same three points and types. What is new here is "
            "the figure eight in time, and what it is made of."
        ),
        Para(
            "The level E = 0 through the saddle is y² = x² − x⁴/2, which "
            "crosses the x-axis at the origin and at x = ±√2. It is a figure "
            "eight: two loops, each leaving the saddle, going round one well, "
            "and coming back to the same saddle. Energies between −1/4 and 0 "
            "give closed orbits inside one loop, oscillation in one well. "
            "Energies above 0 give large orbits round the whole figure eight, "
            "swinging over the hump from one well to the other and back."
        ),
        Worked(
            "The homoclinic orbit",
            "Show that x = √2 sech t, y = −√2 sech t tanh t solves x' = y, "
            "y' = x − x³ with x(0) = √2, y(0) = 0, and describe the orbit.",
            (
                Step("Differentiating x = √2/cosh t gives x' = −√2 sinh t / "
                     "cosh² t = y. Differentiating again and using "
                     "sinh² t = cosh² t − 1, y' = √2/cosh t − 2√2/cosh³ t, "
                     "which is x − x³, since x³ = 2√2/cosh³ t.",
                     r"y' = \frac{\sqrt{2}}{\cosh t} - \frac{2\sqrt{2}}"
                     r"{\cosh^{3} t} = x - x^{3}"),
                Step("The energy is 0: with s = sech t, y² = 2s²(1 − s²), "
                     "and −x²/2 + x⁴/4 = −s² + s⁴, so y²/2 − x²/2 + x⁴/4 = 0.",
                     r"E = s^{2} - s^{4} - s^{2} + s^{4} = 0"),
                Step("Read it. As t → −∞ and as t → +∞, x → 0 and y → 0: the "
                     "orbit leaves the saddle, swings out to x = √2 at t = 0, "
                     "and returns to the same saddle, taking infinitely long "
                     "at each end. It is the right loop of the figure eight, "
                     "a homoclinic orbit; −x(t), −y(t) is the left one."),
            ),
            equation="x' = y; y' = x - x**3",
            conditions="x(0) = sqrt(2), y(0) = 0",
            answer="x = sqrt(2)/cosh(t)\ny = -sqrt(2)*sinh(t)/cosh(t)**2",
            answer_latex=r"x = \sqrt{2}\,\mathrm{sech}\,t, \qquad "
                         r"y = -\sqrt{2}\,\mathrm{sech}\,t\,\tanh t",
        ),
        Worked(
            "An orbit round both wells",
            "Find the orbit of x'' = x − x³ through (0, 1), the strip passing "
            "its central position with speed 1, and find its turning points.",
            (
                Step("The orbit equation is dy/dx = (x − x³)/y. Separating, "
                     "y²/2 = x²/2 − x⁴/4 + C, and (0, 1) gives C = 1/2.",
                     r"y^{2} = 1 + x^{2} - \frac{x^{4}}{2}"),
                Step("On the upper branch take the positive root.",
                     r"y = \sqrt{1 + x^{2} - \frac{x^{4}}{2}}"),
                Step("The energy 1/2 is above the hump's 0, so the orbit "
                     "encloses the whole figure eight. The turning points "
                     "solve x⁴ − 2x² − 2 = 0, a quadratic in x², so "
                     "x² = 1 + √3 and x = ±√(1 + √3) ≈ ±1.65. The strip snaps "
                     "from one side to the other and back again, for ever.",
                     r"x = \pm\sqrt{1 + \sqrt{3}} \approx \pm 1.65"),
            ),
            equation="y' = (t - t**3)/y",
            conditions="y(0) = 1",
            answer="y = sqrt(1 + t**2 - t**4/2)",
            answer_latex=r"y = \sqrt{1 + x^{2} - \frac{x^{4}}{2}}",
        ),
        Plot(
            "The double well",
            "Orbits of x'' = x − x³. The figure eight is the homoclinic "
            "separatrix E = 0, drawn from the formula of the worked example "
            "and its mirror image, so this time it is drawn from the "
            "solution in time rather than from the level curve. It crosses "
            "the x-axis at ±√2. Outside is the orbit of "
            "energy 1/2 through (0, ±1), which goes round both wells between "
            "x ≈ ±1.65. Each curve has its own colour, named in the legend.",
            (Curve("sqrt(2)/cosh(t)", "right loop, E = 0",
                   y="-sqrt(2)*sinh(t)/cosh(t)**2"),
             Curve("-sqrt(2)/cosh(t)", "left loop, E = 0",
                   y="sqrt(2)*sinh(t)/cosh(t)**2"),
             Curve("sqrt(1 + sqrt(3))*sin(pi*t/12)", "E = 1/2, upper",
                   y="sqrt(1 + (1 + sqrt(3))*sin(pi*t/12)**2"
                     " - (1 + sqrt(3))**2*sin(pi*t/12)**4/2)"),
             Curve("sqrt(1 + sqrt(3))*sin(pi*t/12)", "E = 1/2, lower",
                   y="-sqrt(1 + (1 + sqrt(3))*sin(pi*t/12)**2"
                     " - (1 + sqrt(3))**2*sin(pi*t/12)**4/2)")),
            t=(-6.0, 6.0), xlabel="x", ylabel="y", ylim=(-1.4, 1.4),
        ),
    )),
    Section("A softening spring: motion that escapes", (
        Para(
            "Every potential so far has held the particle in: the pendulum's "
            "wells repeat, and the quartic walls of the hard spring and the "
            "double well rise for ever. Turn the sign of the cubic term round "
            "and the picture changes. The softening spring x'' + x − x³ = 0 "
            "has a restoring force x − x³ that weakens as the spring is "
            "stretched and reverses beyond |x| = 1, like a spring that gives "
            "way. Its potential V(x) = x²/2 − x⁴/4 is a single well at the "
            "origin between two humps at x = ±1, of height 1/4, and outside "
            "the humps it falls to −∞. Reading the energy lines on this graph "
            "shows at once which motions stay bounded and which do not."
        ),
        Worked(
            "A softening spring",
            "For x' = y, y' = −x + x³, find and classify the equilibria, find "
            "the level curve through the saddles, and solve for the motion "
            "along it through (0, √2/2). Then sort all the motions by energy.",
            (
                Step("V'(x) = x − x³ vanishes at x = 0 and x = ±1, and "
                     "V''(x) = 1 − 3x². At the origin V'' = 1 > 0, a minimum, "
                     "so the origin is a centre. At ±1, V'' = −2 < 0, maxima, "
                     "so (±1, 0) are saddles, with eigenvalues ±√2. The humps "
                     "have energy V(±1) = 1/2 − 1/4 = 1/4.",
                     r"V(x) = \frac{1}{2}x^{2} - \frac{1}{4}x^{4}, \qquad "
                     r"V(\pm 1) = \frac{1}{4}"),
                Step("On the level E = 1/4 the kinetic energy is "
                     "1/4 − x²/2 + x⁴/4, and doubling it gives a perfect "
                     "square. So the level curve is the pair of parabolas "
                     "y = ±(1 − x²)/√2. Between the saddles they are two arcs, "
                     "each joining (−1, 0) to (1, 0): a heteroclinic pair, "
                     "like one cell of the pendulum's separatrix.",
                     r"y^{2} = \frac{1}{2} - x^{2} + \frac{1}{2}x^{4} = "
                     r"\frac{(1 - x^{2})^{2}}{2}"),
                Step("On the upper arc x' = (1 − x²)/√2, a separable "
                     "equation for x alone. With x(0) = 0 it gives "
                     "x = tanh(t/√2), and then y = x' = sech²(t/√2)/√2. "
                     "Check: y' = −sech²(t/√2) tanh(t/√2) = −x(1 − x²) = "
                     "−x + x³. As t → ±∞, x → ±1: the spring creeps from one "
                     "saddle to the other and takes for ever to do it.",
                     r"x = \tanh\frac{t}{\sqrt{2}}, \qquad y = \frac{1}{\sqrt{2}}"
                     r"\,\mathrm{sech}^{2}\frac{t}{\sqrt{2}}"),
                Step("Now draw energy lines on the graph of V. If E < 1/4 and "
                     "the spring starts with |x| < 1, the line cuts the well "
                     "and the spring oscillates inside the separatrix: from "
                     "(0, 1/2), E = 1/8 and the turning points are "
                     "x = ±√(1 − √2/2) ≈ ±0.541. If E > 1/4 the line clears "
                     "both humps, there are no turning points, and the orbit "
                     "runs off to infinity: the spring breaks. Even a small "
                     "energy is not safe outside the humps: released from "
                     "rest at x = 1.2, E = 0.72 − 0.5184 = 0.2016 < 1/4, yet "
                     "the allowed region there is x ≥ 1.2, and the spring "
                     "falls outwards for ever. The hard spring, whose walls "
                     "rise for ever, keeps every orbit bounded; the soft one "
                     "keeps only those inside its separatrix."),
            ),
            equation="x' = y; y' = -x + x**3",
            conditions="x(0) = 0, y(0) = sqrt(2)/2",
            answer="x = tanh(t/sqrt(2))\ny = 1/(sqrt(2)*cosh(t/sqrt(2))**2)",
            answer_latex=r"x = \tanh\frac{t}{\sqrt{2}}, \qquad y = \frac{1}"
                         r"{\sqrt{2}}\,\mathrm{sech}^{2}\frac{t}{\sqrt{2}}",
        ),
        Plot(
            "The softening spring",
            "The potential V(x) = x²/2 − x⁴/4 and the phase portrait of "
            "x'' + x − x³ = 0 on the same x-axis; the vertical axis reads as "
            "y for the orbits and as V for the potential. The parabolas "
            "y = ±(1 − x²)/√2 make up the level E = 1/4: between the saddles "
            "(±1, 0) they are the heteroclinic separatrix, and outside they "
            "are the saddles' other stable and unstable curves, running off "
            "to infinity. Inside is the bounded orbit of energy 1/8 through "
            "(0, ±1/2), turning at x ≈ ±0.541 below the humps of V. The "
            "orbit of energy 1/2 through (0, ±1) passes over both humps and "
            "escapes. Each curve has its own colour, named in the legend.",
            (Curve("t", "potential V(x)", y="t**2/2 - t**4/4"),
             Curve("t", "separatrix, y = (1 − x²)/√2",
                   y="(1 - t**2)/sqrt(2)"),
             Curve("t", "separatrix, y = −(1 − x²)/√2",
                   y="-(1 - t**2)/sqrt(2)"),
             Curve("sqrt(1 - sqrt(2)/2)*sin(pi*t/2)", "bounded, E = 1/8",
                   y="sqrt(1 - sqrt(2)/2)*cos(pi*t/2)*sqrt((1 + sqrt(2)/2"
                     " - (1 - sqrt(2)/2)*sin(pi*t/2)**2)/2)"),
             Curve("t", "escaping, E = 1/2, upper",
                   y="sqrt(1 - t**2 + t**4/2)"),
             Curve("t", "escaping, E = 1/2, lower",
                   y="-sqrt(1 - t**2 + t**4/2)")),
            t=(-2.0, 2.0), xlabel="x", ylabel="y, and V for the potential",
            ylim=(-2.0, 2.0),
        ),
    )),
    Section("Friction: the energy as a Lyapunov function", (
        Para(
            "Add a friction force proportional to the velocity. The pendulum "
            "becomes x'' + c x' + sin x = 0 with c > 0, or x' = y, "
            "y' = −sin x − c y. The energy is no longer conserved, but its "
            "derivative along solutions is easy to compute, and it has a "
            "sign."
        ),
        Display(r"\frac{dE}{dt} = \sin x \cdot y + y\,(-\sin x - c\,y) = "
                r"-c\,y^{2} \leq 0", "10"),
        Para(
            "So the energy can only fall, and it falls whenever the pendulum "
            "is moving. In the phase plane the trajectories now cross the "
            "level curves of E, always from higher to lower energy, which "
            "means inwards across the closed swings. The energy is a Lyapunov "
            "function, and the almost-linear chapter's Lyapunov test applies "
            "with E as the Lyapunov function (in this chapter the letter V "
            "belongs to the potential): E has a strict minimum at the hanging "
            "position and dE/dt ≤ 0, so that position is stable. For the "
            "undamped pendulum, where dE/dt = 0, the test gives stability, "
            "the no-attractor theorem rules out asymptotic stability, and "
            "the closed level curves make the point a centre."
        ),
        Para(
            "With damping the test's second clause, dE/dt < 0 away from the "
            "equilibrium, fails: dE/dt = −cy² is zero on the whole x-axis. The "
            "almost-linear chapter met the same gap for cubic friction and "
            "closed it by hand, noting that a solution cannot stay on the "
            "x-axis. That remark is the heart of a general theorem, which "
            "says not only that the equilibrium attracts its neighbours but "
            "where every solution goes."
        ),
        Box(
            "theorem", "LaSalle's invariance principle",
            "Let E be continuously differentiable with dE/dt ≤ 0 along every "
            "solution of a planar autonomous system, and let a solution stay "
            "in a bounded region for t ≥ 0. Then as t → ∞ it approaches the "
            "largest invariant set contained in the set where dE/dt = 0, the "
            "largest set of points whose whole trajectories stay where "
            "dE/dt = 0.",
            r"\frac{dE}{dt} \leq 0 \;\Longrightarrow\; (x(t), y(t)) \to "
            r"\text{largest invariant set in } \left\{\frac{dE}{dt} = 0\right\}",
        ),
        Box(
            "proof", "Proof sketch",
            "E never increases along the solution and is bounded below on "
            "the bounded region, so E(x(t)) tends to a limit E∞. Every limit "
            "point of the solution therefore has energy E∞. The set of limit "
            "points is invariant: the solution through a limit point stays "
            "among the limit points, because the original solution passes "
            "near it again and again and solutions depend continuously on "
            "their starting points. So a solution starting at a limit point "
            "keeps the constant energy E∞, which means dE/dt = 0 all along "
            "it. The limit points lie in an invariant set inside "
            "{dE/dt = 0}, and the solution approaches them.",
        ),
        Para(
            "Apply it to the damped pendulum. The set where dE/dt = −cy² = 0 "
            "is the x-axis. A trajectory that stays on the x-axis has y = 0 "
            "for all time, so y' = −sin x = 0 as well, and x is a multiple of "
            "π: the only invariant sets on the axis are the equilibria. "
            "Every solution is bounded in y, since y²/2 ≤ E(0) + 1, and x "
            "matters only up to multiples of 2π, so on the cylinder every "
            "solution stays in a bounded region. LaSalle's principle then "
            "says that every solution of the damped pendulum tends to an "
            "equilibrium, and since the equilibria are isolated, to a single "
            "one. There are no periodic motions left at all. The hanging "
            "positions are asymptotically stable, and the only solutions "
            "that tend to an inverted position are the exceptional ones "
            "aimed exactly at a saddle."
        ),
        Para(
            "The linearisation agrees. At the bottom the Jacobian has rows "
            "(0, 1) and (−1, −c), with trace −c and determinant 1, so for "
            "0 < c < 2 its eigenvalues are complex with real part −c/2: a "
            "stable spiral, hyperbolic now, so the almost-linear chapter's "
            "theorem applies too. At the top the rows are (0, 1) and (1, −c), "
            "determinant −1: still a saddle. For c ≥ 2 the eigenvalues at "
            "the bottom are real and negative, since λ² + cλ + 1 = 0 then "
            "has discriminant c² − 4 ≥ 0. Damping turns centres into stable "
            "spirals (stable nodes once c ≥ 2, when the pendulum is "
            "overdamped) and leaves saddles as saddles."
        ),
        Worked(
            "A damped pendulum given a hard push",
            "With c = 0.3, a pendulum starts at the bottom with speed 2.8. "
            "Does it go over the top, and where does it end up?",
            (
                Step("The starting energy is 2.8²/2 − 1 = 2.92, well above "
                     "the separatrix level 1, so an undamped pendulum would "
                     "rotate for ever. With damping the energy drains at the "
                     "rate cy², fastest when the pendulum is fastest.",
                     r"E(0) = 2.92, \qquad \frac{dE}{dt} = -0.3\,y^{2}"),
                Step("Integrating numerically, the pendulum passes the "
                     "inverted position x = π at t ≈ 2.10. By then it has "
                     "lost enough energy that it cannot clear x = 3π: it "
                     "falls into the next well."),
                Step("There it spirals in to the equilibrium (2π, 0), the "
                     "same hanging position one full turn round. The "
                     "linearisation there has eigenvalues −0.15 ± 0.989i, so "
                     "each swing to the same side is smaller than the "
                     "previous one by a factor of about e^(0.15 × 6.36) ≈ 2.6 "
                     "(one full period, 2π/0.989 ≈ 6.36); from one side to "
                     "the other the factor is e^(0.15 × 3.18) ≈ 1.61.",
                     r"\lambda = -0.15 \pm 0.989\,i"),
                Step("Which well a damped pendulum ends in depends on its "
                     "start. Bisecting on the starting speed shows that with "
                     "c = 0.3 it goes over at all only above a speed of about "
                     "2.63 (energy about 2.47), not the undamped 2; with "
                     "c = 0.1 the threshold is about 2.20."),
            ),
        ),
        Para(
            "The separatrices do not disappear under damping, but they change "
            "their role. The stable curves of the saddles are the "
            "trajectories that arrive exactly at an inverted position. "
            "Followed backwards in time, they gain energy and stretch out to "
            "ever larger speeds. They divide the plane into bands, one for "
            "each hanging equilibrium, and every starting point strictly "
            "inside a band ends at that band's equilibrium; only the points "
            "on the dividing curves themselves go to a saddle. The boundary "
            "between swinging and rotating has become a boundary between "
            "basins of attraction."
        ),
    )),
    Section("Watching it happen", (
        Figure("pendulum_energy",
               "The figure starts at speed 1.5, with damping c = 0. The "
               "readout gives the energy at the start and after t = 30, and "
               "they agree to all four decimals shown (the slider's 1.5 is "
               "really 1.4992, so both read +0.1238): the coloured trajectory is a closed "
               "curve lying "
               "between the grey constant-energy curves. Drag the "
               "starting speed (its range is 0.4 to 2.8) up towards 2 and "
               "watch the swing fill out towards the heavy separatrix; at "
               "1.9 the readout still says it swings without going over, "
               "and just above 2 it says it goes over the top, and the "
               "trajectory becomes a wavy line across the window. Now set "
               "the speed to 1.5 and raise the damping c (its range is 0 to "
               "0.6) to 0.3: the trajectory crosses the grey curves inwards "
               "and spirals in, and the energy after t = 30 has fallen to "
               "within a thousandth of −1, the bottom of the well. Finally "
               "set the speed to 2.8 at c = 0.3 and see the pendulum go over "
               "once and settle in the next well, then raise c to 0.6, where "
               "no speed the slider allows is enough to go over at all."),
        Para(
            "The Phase Portrait screen has the same system as its pendulum "
            "preset, with a damping slider b from 0 to 2 and layers for the "
            "equilibria and the separatrices. Clicking anywhere launches the "
            "trajectory through that point, forwards and backwards, so a "
            "click just inside and just outside the separatrix shows the two "
            "fates side by side. With b = 0 the screen marks the hanging "
            "equilibria as centres classified from the linearisation only; "
            "this chapter's energy argument is what makes that label true."
        ),
    )),
    Section("Common errors", (
        Box(
            "warning", "The separatrix orbit never arrives",
            "A pendulum started at the bottom with speed exactly 2 does not "
            "reach the top and fall back. It approaches the inverted "
            "position as t → ∞ and never gets there, because no trajectory "
            "reaches an equilibrium in finite time.",
        ),
        Para(
            "Other errors recur. The first is the sign of the potential. For "
            "x'' + sin x = 0 the force is −sin x, so V = −cos x and the "
            "energy is y²/2 − cos x; writing y²/2 + cos x gives a quantity "
            "whose derivative is −2y sin x, not zero. A quick check is that "
            "V should have a minimum where the system has a stable rest "
            "position. The second is to drop the half in the kinetic energy, "
            "or the quarter in x⁴/4, and then compute speeds from the wrong "
            "energy: the greatest speed of x'' + kx³ = 0 released from rest "
            "at A is A²√(k/2), which needs both factors. The third is to "
            "trust the linearisation at a minimum of V: it gives a linear "
            "centre, which the almost-linear chapter showed decides nothing, "
            "and it is the energy that proves the centre genuine. The fourth "
            "is to expect a spiral or a node in a conservative system, which "
            "the no-attractor theorem forbids; if a numerical portrait of a "
            "frictionless system shows a slow spiral, the drift is the "
            "integrator's error, and tightening its tolerance shrinks it."
        ),
    )),
    Section("Summary", (
        Para(
            "For x'' = −V'(x), written as x' = y, y' = −V'(x), the energy "
            "E = y²/2 + V(x) is constant along every solution, so orbits are "
            "level curves of E and the phase portrait is its contour map. "
            "The orbit equation dy/dx = −V'(x)/y separates to the same "
            "energy. The graph of V shows everything: motion is confined to "
            "V(x) ≤ E, turning points are where V = E, minima of V are "
            "genuine centres and maxima are saddles, and a conservative "
            "system has no attracting equilibrium. For the pendulum, "
            "E = y²/2 − cos x; energies between −1 and 1 give swings, whose "
            "period 4K(k) grows from 2π without bound as the amplitude "
            "approaches 180°; energies above 1 give rotations; and the "
            "separatrix E = 1, y = ±2 cos(x/2), joins the saddles and takes "
            "infinitely long to traverse. A double-well potential gives a "
            "homoclinic figure eight instead. Friction makes dE/dt = −cy² ≤ 0, "
            "turning the energy into a Lyapunov function: centres become "
            "stable spirals or nodes, LaSalle's principle sends every "
            "solution to an equilibrium, and the separatrices become the "
            "edges of basins of attraction. A softening spring shows the "
            "other use of the energy lines: which motions stay bounded at "
            "all. The next chapter meets closed orbits of a different kind, "
            "limit cycles, which no conservative system can have: orbits "
            "approaching a cycle would, by continuity, all share its energy, "
            "making E constant on an open region, which a first integral "
            "cannot be."
        ),
    )),
)


CYCLES = (
    Section("Oscillators that choose their own size", (
        Para(
            "A heart beats at its own rhythm whether it starts slow or fast. A "
            "violin string driven by a steady bow settles to one amplitude "
            "however it was first plucked. Van der Pol's vacuum-tube circuit "
            "oscillates at a size set by the circuit, not by the switch-on "
            "transient. Each of these systems has a preferred oscillation, and "
            "it reaches that oscillation from any reasonable start."
        ),
        Para(
            "Nothing in the previous chapters behaves like this. A linear "
            "centre, from the phase-portraits chapter of Unit 6, has a closed "
            "orbit through every point, so its amplitude is whatever the "
            "starting point made it, and it remembers that for ever. The "
            "frictionless pendulum and the Lotka–Volterra populations of the "
            "last two chapters have closed orbits too, and for the same reason "
            "they come in continuous families: a conserved quantity picks out "
            "one level curve per starting point. Add friction to the pendulum "
            "and the oscillation dies instead. None of these has an "
            "oscillation that attracts."
        ),
        Para(
            "The one exception is an oscillator pushed from outside. The "
            "damped, forced oscillator of Unit 4, x'' + cx' + kx = F cos ωt, "
            "does settle to one steady periodic response from any start, "
            "because the transient dies away. But the forcing term sets both "
            "its rhythm, ω, and its size. The heart, the bowed string and Van "
            "der Pol's circuit have no clock driving them: their equations "
            "are autonomous, and the rhythm and the amplitude come from "
            "inside the system."
        ),
        Para(
            "The object that does is a *limit cycle*: a closed orbit that is "
            "isolated, with neighbouring trajectories winding onto it from the "
            "inside and from the outside. This chapter builds one in polar "
            "coordinates where everything can be solved, shows why the "
            "linearisation of the almost-linear chapter cannot see it, studies "
            "Van der Pol's oscillator where nothing can be solved, and then "
            "states the Poincaré–Bendixson theorem and draws its two "
            "consequences: a way to show that a cycle exists without finding "
            "it, and the fact that an autonomous system in the plane can "
            "never be chaotic."
        ),
    )),
    Section("Closed orbits and periodic solutions", (
        Para(
            "All the systems in this chapter are autonomous and planar, "
            "x' = f(x, y), y' = g(x, y), with f and g continuously "
            "differentiable, so that the existence and uniqueness theorem "
            "applies. As in the phase-portraits chapter, time shifts of "
            "solutions are solutions, and two trajectories either coincide or "
            "never meet. A trajectory that is a closed curve, and is not a "
            "single point, is a *closed orbit*."
        ),
        Box(
            "theorem", "A trajectory that returns is periodic",
            "If a solution of an autonomous system is at the same point p at "
            "two different times t₁ < t₂, then it is periodic with period "
            "T = t₂ − t₁, and its trajectory is a closed orbit (or the single "
            "point p, if p is an equilibrium).",
            r"\mathbf{x}(t_2) = \mathbf{x}(t_1) \;\Longrightarrow\; "
            r"\mathbf{x}(t + T) = \mathbf{x}(t) \text{ for all } t",
        ),
        Box(
            "proof", "Proof",
            "The function x(t + T) is a solution, because the system does not "
            "depend on t, and at time t₁ it is at x(t₂) = p, which is where "
            "x(t) is at time t₁. Two solutions agreeing at one time agree at "
            "all times, by uniqueness, so x(t + T) = x(t) for every t.",
        ),
        Para(
            "So closed orbits and periodic solutions are the same thing. The "
            "question of this chapter is which closed orbits a system can "
            "have, and whether its other trajectories are drawn onto them. "
            "For a linear system the answer is already fixed, and it is the "
            "reason a linear model can never choose an amplitude."
        ),
        Box(
            "theorem", "Linear closed orbits come in families",
            "If x' = Ax has a closed orbit, then every scaled copy of it, cx(t) "
            "for c ≠ 0, is a closed orbit as well. In particular no closed "
            "orbit of a linear system is isolated.",
        ),
        Box(
            "proof", "Proof",
            "If x(t) is a periodic solution then so is cx(t), since "
            "(cx)' = cAx = A(cx) and cx(t + T) = cx(t). Taking c close to 1 "
            "gives closed orbits as close to the original as desired.",
        ),
    )),
    Section("Limit cycles", (
        Box(
            "definition", "Limit cycle",
            "A limit cycle is a closed orbit with no other closed orbit "
            "arbitrarily near it: some band around it contains no other "
            "closed orbit. It is stable, or attracting, if every trajectory "
            "that starts close enough to it approaches it as t → ∞; unstable, "
            "or repelling, if nearby trajectories on both sides move away "
            "from it; and semistable if trajectories approach it from one "
            "side and leave it on the other.",
        ),
        Para(
            "Isolation is the whole content of the definition. A closed orbit "
            "on its own is not remarkable: every orbit of a centre is closed. "
            "What is remarkable is a closed orbit with nothing like it nearby, "
            "because then a trajectory that starts near it has nowhere else to "
            "settle. Push a trajectory off a stable limit cycle and it comes "
            "back; push it off one of a centre's orbits and it simply follows "
            "a different closed orbit, as happy there as it was before."
        ),
        Para(
            "Conserved quantities are what produce centres, and they rule out "
            "attracting cycles. Suppose E(x, y) is continuous, conserved, and "
            "not constant on any open set, as the energy of the pendulum and "
            "the quantity V of the ecological-models chapter are. A trajectory keeps "
            "its value of E, so if it approached a cycle on which E = c, "
            "continuity would force its value to be c already. Every "
            "trajectory starting near an "
            "attracting cycle approaches it, so E would equal c on a whole "
            "neighbourhood of the cycle, which is an open set: a "
            "contradiction. A conservative system can have closed orbits, "
            "but never a stable limit cycle."
        ),
        Box(
            "warning", "Closed is not isolated",
            "The Lotka–Volterra orbits are all closed, and none of them is a "
            "limit cycle: each is surrounded by other closed orbits. The same "
            "is true of the pendulum's swinging orbits. Calling a centre's "
            "orbit a limit cycle is the commonest confusion about this topic.",
        ),
        Para(
            "The application draws the distinction for you. The Phase "
            "Portrait screen has a limit-cycle layer, switched on by ticking "
            "'limit cycle' among the layers. It follows the "
            "starting trajectory until it settles, measures the closed orbit "
            "it settles onto and its period, and then pushes the orbit off "
            "and watches whether it comes back. An isolated cycle is drawn as "
            "a thick solid curve and described as attracting; a closed orbit "
            "that is one of a continuum, as around a centre, is drawn dotted."
        ),
    )),
    Section("A cycle built in polar coordinates", (
        Para(
            "The cleanest example is built so that the radius and the angle "
            "decouple. It depends on a parameter μ, and it is the system that "
            "the bifurcations chapter will call the normal form of a Hopf "
            "bifurcation."
        ),
        Display(r"x' = \mu x - y - x(x^{2} + y^{2}), \qquad y' = x + \mu y - "
                r"y(x^{2} + y^{2})", "1"),
        Para(
            "Write x = r cos θ and y = r sin θ. Differentiating r² = x² + y² "
            "gives rr' = xx' + yy', and differentiating tan θ = y/x gives "
            "r²θ' = xy' − yx'. Substituting equation 1, the terms −xy and +xy "
            "cancel in the first and the cubic terms cancel in the second."
        ),
        Display(r"r r' = \mu r^{2} - r^{4}, \qquad r^{2}\theta' = r^{2}", "2"),
        Display(r"r' = r(\mu - r^{2}), \qquad \theta' = 1", "3"),
        Para(
            "The angle turns at the constant rate 1, and the radius obeys a "
            "scalar autonomous equation of its own, which can be read with "
            "the phase line of Unit 2. Its equilibria are r = 0 and, when "
            "μ > 0, r = √μ. For 0 < r < √μ the right-hand side is positive, "
            "and for r > √μ it is negative, so every radius except zero moves "
            "towards √μ. In the plane an equilibrium of the radial equation "
            "is a circle travelled at constant angular speed, and this one "
            "attracts every trajectory except the equilibrium at the origin: "
            "a stable limit cycle of radius √μ and period 2π."
        ),
        Plot(
            "The radial phase line",
            "The right-hand side r(μ − r²) of the radial equation against r, "
            "for three values of μ. For μ = 1 it is positive below r = 1 and "
            "negative above, so r = 1 attracts from both sides: that zero is "
            "the limit cycle. For μ = 0 and μ = −1/2 it is negative for every "
            "r > 0, so every radius shrinks and there is no cycle.",
            (Curve("t*(1 - t**2)", "μ = 1"),
             Curve("-t**3", "μ = 0"),
             Curve("t*(-0.5 - t**2)", "μ = −1/2"),
             Curve("0*t", "")),
            t=(0.0, 1.5), xlabel="r", ylabel="r'", ylim=(-2.0, 1.0),
        ),
        Worked(
            "Onto the cycle from inside",
            "Take μ = 1, so the radial equation is r' = r(1 − r²). Solve it "
            "from r(0) = 1/2 (the checked equation below writes y for r) and "
            "describe what "
            "the radius does.",
            (
                Step("The equation is separable, and it is also a Bernoulli "
                     "equation, which is the quicker route. Put u = 1/r². "
                     "Then u' = −2r'/r³ = −2(1 − r²)/r² = −2u + 2, a linear "
                     "equation for u.",
                     r"u = \frac{1}{r^{2}}, \qquad u' = 2 - 2u"),
                Step("Its solution is u = 1 + Ce^(−2t), and u(0) = 4 gives "
                     "C = 3.",
                     r"u = 1 + 3e^{-2t}"),
                Step("So r = 1/√(1 + 3e^(−2t)), which multiplied through by "
                     "e^t is the form below. It starts at 1/2, increases for "
                     "all t, and tends to 1: it reaches 0.9 at t ≈ 1.27 and "
                     "0.99 at t ≈ 2.50.",
                     r"r = \frac{e^{t}}{\sqrt{e^{2t} + 3}} \;\longrightarrow\; 1"),
                Step("Now the other side, in your head. From r = 2, "
                     "r' = 2(1 − 4) = −6 < 0, so the radius shrinks towards 1 "
                     "instead. Both sides converging on one radius is exactly "
                     "what makes the circle r = 1 a limit cycle rather than "
                     "one closed orbit of many."),
            ),
            equation="y' = y*(1 - y**2)",
            conditions="y(0) = 1/2",
            answer="exp(t)/sqrt(exp(2*t) + 3)",
            answer_latex=r"r = \frac{e^{t}}{\sqrt{e^{2t} + 3}}",
        ),
        Para(
            "The same substitution solves the radial equation from any start "
            "r₀ > 0: r = 1/√(1 + Ce^(−2t)) with C = 1/r₀² − 1. The constant is "
            "positive inside the circle and negative outside it, and either "
            "way the exponential kills it."
        ),
        Plot(
            "The radius against time",
            "Solutions of r' = r(1 − r²) from r₀ = 0.1, 0.5, 1.5 and 2, that is "
            "C = 99, 3, −5/9 and −3/4. Those inside rise to 1 and those "
            "outside fall to it; the cycle r = 1 is the horizontal line every "
            "one of them approaches. The start at 0.1 grows at first like "
            "0.1e^t, the rate the linearisation at the origin gives, before "
            "the cubic term bends it over.",
            (Curve("1/sqrt(1 + 99*exp(-2*t))", "r₀ = 0.1"),
             Curve("1/sqrt(1 + 3*exp(-2*t))", "r₀ = 0.5"),
             Curve("1/sqrt(1 - (5/9)*exp(-2*t))", "r₀ = 1.5"),
             Curve("1/sqrt(1 - 0.75*exp(-2*t))", "r₀ = 2"),
             Curve("1 + 0*t", "the cycle, r = 1")),
            t=(0.0, 5.0), xlabel="t", ylabel="r", ylim=(0.0, 2.1),
        ),
        Para(
            "Because θ = θ₀ + t exactly, the radial solution gives the whole "
            "trajectory in the plane. That is rare for a nonlinear system, "
            "and worth checking against equation 1 directly."
        ),
        Worked(
            "The trajectory itself",
            "Solve x' = x − y − x(x² + y²), y' = x + y − y(x² + y²), which is "
            "equation 1 with μ = 1, from x(0) = 1/2, y(0) = 0.",
            (
                Step("In polar form r' = r(1 − r²) and θ' = 1. The start is at "
                     "r = 1/2, θ = 0, so θ = t, and r is the solution of the "
                     "previous example.",
                     r"r = \frac{e^{t}}{\sqrt{e^{2t} + 3}}, \qquad \theta = t"),
                Step("Convert back with x = r cos θ, y = r sin θ. Substituting "
                     "the result into both equations of the system confirms "
                     "it, and checks the polar computation at the same time."),
                Step("Read it. The point turns anticlockwise once every 2π "
                     "time units while its distance from the origin rises from "
                     "1/2 towards 1. After the first couple of turns it is "
                     "indistinguishable from the unit circle."),
            ),
            equation="x' = x - y - x*(x**2 + y**2); y' = x + y - y*(x**2 + y**2)",
            conditions="x(0) = 1/2, y(0) = 0",
            answer="x = exp(t)*cos(t)/sqrt(exp(2*t) + 3)\n"
                   "y = exp(t)*sin(t)/sqrt(exp(2*t) + 3)",
            answer_latex=r"x = \frac{e^{t}\cos t}{\sqrt{e^{2t} + 3}}, \qquad "
                         r"y = \frac{e^{t}\sin t}{\sqrt{e^{2t} + 3}}",
        ),
        Plot(
            "Winding onto the cycle from both sides",
            "Two trajectories of equation 1 with μ = 1, and the unit circle. "
            "The inner one starts at (0.1, 0) and spirals outwards; the outer "
            "one starts at (2, 0) and spirals inwards. Both are travelled "
            "anticlockwise, and both end on the same circle. The axes are "
            "drawn to different scales, so the circle may look like an "
            "ellipse.",
            (Curve("cos(t)/sqrt(1 + 99*exp(-2*t))", "from (0.1, 0)",
                   y="sin(t)/sqrt(1 + 99*exp(-2*t))"),
             Curve("cos(t)/sqrt(1 - 0.75*exp(-2*t))", "from (2, 0)",
                   y="sin(t)/sqrt(1 - 0.75*exp(-2*t))"),
             Curve("cos(t)", "the limit cycle", y="sin(t)")),
            t=(0.0, 12.0), xlabel="x", ylabel="y", ylim=(-1.6, 1.6),
        ),
    )),
    Section("What the linearisation sees", (
        Para(
            "Now forget the polar form and do what the almost-linear chapter "
            "taught: find the equilibria and linearise. The only equilibrium "
            "of equation 1 is the origin, since r' = 0 with θ' = 1 needs r = 0. "
            "Dropping the cubic terms leaves the Jacobian there, with rows "
            "(μ, −1) and (1, μ)."
        ),
        Display(r"\tau = 2\mu, \qquad \Delta = \mu^{2} + 1, \qquad "
                r"\lambda = \mu \pm i", "4"),
        Para(
            "For μ > 0 the origin is an unstable spiral, and the linearisation "
            "tells the truth about it: trajectories near the origin do spiral "
            "out. What it cannot say is where they go. The linear system "
            "x' = μx − y, y' = x + μy sends every trajectory to infinity; the "
            "cubic terms, which vanish to third order at the origin and are "
            "invisible to the Jacobian, are what stop them at radius √μ. A "
            "limit cycle is a global feature of the flow, and linearisation "
            "is a local tool."
        ),
        Worked(
            "How strongly the cycle attracts",
            "For equation 1, classify the origin for each sign of μ, and for "
            "μ > 0 find the rate at which trajectories near the cycle "
            "approach it.",
            (
                Step("From equation 4: for μ < 0 the origin is a stable "
                     "spiral, and since r' = r(μ − r²) < 0 for every r > 0 "
                     "there is no cycle at all; every trajectory spirals in. "
                     "For μ > 0 the origin is an unstable spiral, surrounded "
                     "by the cycle r = √μ."),
                Step("The stability of the cycle is the stability of the "
                     "equilibrium r = √μ of the radial equation, and the phase "
                     "line of Unit 2 decides that by the sign of the "
                     "derivative of the right-hand side.",
                     r"\frac{d}{dr}\left[r(\mu - r^{2})\right] = \mu - 3r^{2} "
                     r"= -2\mu \text{ at } r = \sqrt{\mu}"),
                Step("So a small displacement from the cycle decays like "
                     "e^(−2μt). One trip round takes 2π, so each circuit "
                     "multiplies the displacement by e^(−4πμ): at μ = 1 that "
                     "is about 3.5 × 10⁻⁶, a cycle that pulls hard. As μ "
                     "shrinks towards zero the pull weakens and the cycle's "
                     "radius √μ shrinks with it.",
                     r"\text{per circuit: } e^{-4\pi\mu}"),
            ),
        ),
        Para(
            "At μ = 0 the Jacobian has eigenvalues ±i, the case the "
            "almost-linear chapter could not decide: a linear centre, which "
            "the nonlinear terms may turn into a spiral either way. In fact "
            "equation 1 at μ = 0 is exactly the almost-linear chapter's "
            "equation 7 with a = −1, the centre that turned out to be a "
            "stable spiral. The next example repeats that radial computation "
            "in this chapter's notation, because the bifurcations chapter "
            "builds on it."
        ),
        Worked(
            "When the linearisation says centre",
            "At μ = 0 the radial equation is r' = −r³. Solve it from r(0) = 1 "
            "and say what the origin really is.",
            (
                Step("Separate: r⁻³ dr = −dt, so −1/(2r²) = −t + C, and "
                     "r(0) = 1 gives C = −1/2. Hence 1/r² = 1 + 2t.",
                     r"\frac{1}{r^{2}} = 1 + 2t"),
                Step("So r = 1/√(1 + 2t). The radius does tend to zero, and the "
                     "origin is a stable spiral, not a centre. But it decays "
                     "like a power of t, not an exponential: after 40 time "
                     "units the radius is still 1/9 ≈ 0.11, where a linear "
                     "spiral whose eigenvalues had real part only −0.1 would "
                     "already be down to e^(−4) ≈ 0.018.",
                     r"r = \frac{1}{\sqrt{1 + 2t}}"),
            ),
            equation="y' = -y**3",
            conditions="y(0) = 1",
            answer="1/sqrt(1 + 2*t)",
            answer_latex=r"r = \frac{1}{\sqrt{1 + 2t}}",
        ),
        Para(
            "Put together: as μ rises through zero, a complex pair of "
            "eigenvalues crosses the imaginary axis, the origin changes from "
            "a stable to an unstable spiral, and a stable limit cycle is born "
            "at the origin with radius √μ. That event is a Hopf bifurcation, "
            "and it is the subject of the bifurcations chapter."
        ),
        Figure("limit_cycle",
               "The figure draws equation 1 with one trajectory starting at "
               "(0.05, 0), just outside the origin, and one at (1.6, 0), far "
               "out, each run for 40 time units. At the default μ = 0.5 the "
               "readout gives the origin's eigenvalues as +0.500 ± 1.000i, an "
               "unstable spiral, and both trajectories end at r ≈ 0.707, "
               "which is √0.5. Drag μ up to its maximum, 1.2: the circle grows "
               "to r ≈ 1.095 = √1.2, and the two trajectories reach it "
               "within about one turn. Now drag μ slowly down towards zero. "
               "The circle shrinks, and the approach slows, as the rate "
               "e^(−2μt) predicts: near μ = 0.02 the two trajectories have "
               "only reached r ≈ 0.09 and 0.16 after 40 time units, either "
               "side of √0.02 ≈ 0.14. Just below zero the readout calls the "
               "origin a stable spiral, with the radii at about 0.045 and "
               "0.11, the algebraic decay of the last example. Take μ down "
               "to −0.3 and both trajectories reach the origin; there is no "
               "cycle to find."),
    )),
    Section("An unstable cycle: a boundary, not a destination", (
        Para(
            "Reverse the signs of the radial terms μx and μy and of the cubic "
            "terms, keep the rotation terms −y and +x as they are, and the "
            "picture turns inside out. The system x' = −x − y + x(x² + y²), "
            "y' = x − y + y(x² + y²) has, by the same computation as before, "
            "the polar form below."
        ),
        Display(r"r' = r(r^{2} - 1), \qquad \theta' = 1", "5"),
        Para(
            "Now r' < 0 inside the unit circle and r' > 0 outside it. The "
            "circle is still a closed orbit, and still isolated, but it "
            "repels: an unstable limit cycle. The origin, with Jacobian "
            "eigenvalues −1 ± i, is a stable spiral, and the circle is the "
            "edge of its basin of attraction."
        ),
        Worked(
            "Inside an unstable cycle",
            "Solve r' = r(r² − 1) from r(0) = 1/2, and then from r(0) = 2.",
            (
                Step("With u = 1/r² again, u' = −2r'/r³ = −2(1 − u) = 2u − 2, "
                     "so u = 1 + Ce^(2t), and u(0) = 4 gives C = 3.",
                     r"u = 1 + 3e^{2t}, \qquad r = \frac{1}{\sqrt{3e^{2t} + 1}}"),
                Step("The radius decays to zero: the trajectory spirals into "
                     "the origin. Near the end r ≈ e^(−t)/√3, the decay rate of "
                     "the linearisation, whose eigenvalues have real part −1."),
                Step("From r(0) = 2, u(0) = 1/4, so C = −3/4 and "
                     "u = 1 − (3/4)e^(2t). This reaches zero, and r reaches "
                     "infinity, at the finite time t = ½ ln(4/3) ≈ 0.144. "
                     "Outside the cycle trajectories do not merely grow; they "
                     "escape to infinity in finite time.",
                     r"t^{*} = \frac{1}{2}\ln\frac{4}{3} \approx 0.144"),
            ),
            equation="y' = y*(y**2 - 1)",
            conditions="y(0) = 1/2",
            answer="1/sqrt(3*exp(2*t) + 1)",
            answer_latex=r"r = \frac{1}{\sqrt{3e^{2t} + 1}}",
        ),
        Plot(
            "Leaving an unstable cycle",
            "Two trajectories of the reversed system, started just inside the "
            "unit circle at radius 0.95 and further in at radius 1/2, with "
            "the circle itself. Both spiral away from the cycle and into the "
            "stable spiral at the origin. A trajectory started exactly on the "
            "circle would stay there; any other one leaves it.",
            (Curve("cos(t)/sqrt(1 + 0.108*exp(2*t))", "from radius 0.95",
                   y="sin(t)/sqrt(1 + 0.108*exp(2*t))"),
             Curve("cos(t)/sqrt(1 + 3*exp(2*t))", "from radius 1/2",
                   y="sin(t)/sqrt(1 + 3*exp(2*t))"),
             Curve("cos(t)", "the unstable cycle", y="sin(t)")),
            t=(0.0, 8.0), xlabel="x", ylabel="y", ylim=(-1.2, 1.2),
        ),
        Para(
            "An unstable cycle is never seen by running trajectories forward "
            "in time, since every trajectory near it runs away. It is found "
            "by running time backwards, which turns the system into one with "
            "a stable cycle: replacing t by −t reverses every arrow, so "
            "equation 5 becomes r' = r(1 − r²). This is how unstable cycles "
            "are computed in practice. A semistable cycle is the borderline "
            "between the two, for instance r' = r(1 − r²)², where r' ≥ 0 on "
            "both sides of r = 1: trajectories inside approach the circle, "
            "and those outside leave it. Such a cycle is fragile, and the "
            "smallest change to the equation either removes it or splits it "
            "into a stable and an unstable one."
        ),
    )),
    Section("Van der Pol's oscillator", (
        Para(
            "The polar examples were built to be solvable. The system that "
            "made limit cycles famous is not. Balthasar van der Pol studied a "
            "triode circuit in the 1920s whose current obeyed a damped "
            "oscillator equation with a damping coefficient that depends on "
            "the amplitude."
        ),
        Display(r"x'' - \mu(1 - x^{2})x' + x = 0, \qquad \mu > 0", "6"),
        Para(
            "Compare it with x'' + cx' + x = 0. The damping coefficient here "
            "is c = −μ(1 − x²), which is negative for |x| < 1 and positive "
            "for |x| > 1. Small oscillations are pumped up, as if the circuit "
            "were pushing, and large ones are damped down. An oscillation "
            "that neither grows nor shrinks must spend just enough time in "
            "each region for the energy put in to balance the energy taken "
            "out, and that balance picks one amplitude. As a system, with "
            "y = x', it is x' = y, y' = −x + μ(1 − x²)y."
        ),
        Worked(
            "Van der Pol's equilibrium and energy",
            "Find the equilibria of x' = y, y' = −x + μ(1 − x²)y with μ > 0, "
            "classify them, and find how the energy E = (x² + y²)/2 of the "
            "undamped oscillator changes along solutions.",
            (
                Step("x' = 0 forces y = 0, and then y' = −x = 0. The origin "
                     "is the only equilibrium."),
                Step("The partial derivatives of −x + μ(1 − x²)y are "
                     "−1 − 2μxy and μ(1 − x²), which are −1 and μ at the "
                     "origin, so the Jacobian there has rows (0, 1) and "
                     "(−1, μ), with τ = μ and Δ = 1. For 0 < μ < 2, "
                     "τ² − 4Δ = μ² − 4 < 0: an unstable spiral. At μ = 1 the "
                     "eigenvalues are 1/2 ± (√3/2)i. At μ = 2 the eigenvalue 1 "
                     "is repeated and the origin is an unstable degenerate "
                     "node, and for μ > 2 it is an unstable node. In every "
                     "case, trajectories near it leave.",
                     r"\lambda = \frac{\mu \pm \sqrt{\mu^{2} - 4}}{2}"),
                Step("Along a solution E' = xx' + yy' = xy + y(−x + μ(1 − x²)y). "
                     "The xy terms cancel, leaving the rate at which the "
                     "damping does work.",
                     r"\frac{dE}{dt} = \mu(1 - x^{2})\,y^{2}"),
                Step("So the energy rises while |x| < 1 and falls while "
                     "|x| > 1. It is neither conserved, which would give a "
                     "centre, nor always decreasing, which would make it a "
                     "Lyapunov function, as the energy of the damped pendulum "
                     "is in the nonlinear-mechanics chapter, and send "
                     "everything to the origin. It does both, in "
                     "different places."),
            ),
        ),
        Para(
            "For small μ the balance can be computed. With μ ≈ 0 the system is "
            "nearly the harmonic oscillator, whose solutions are "
            "x = A cos t, y = −A sin t, so over one turn the orbit is nearly "
            "a circle of radius A. The net energy gained in a turn is the "
            "integral of dE/dt round that circle."
        ),
        Display(r"\int_{0}^{2\pi} \mu\,(1 - A^{2}\cos^{2}t)\,A^{2}\sin^{2}t\,dt "
                r"= \pi\mu A^{2}\left(1 - \frac{A^{2}}{4}\right)", "7"),
        Para(
            "This is positive for A < 2 and negative for A > 2, so small "
            "oscillations grow, large ones shrink, and the balance is at "
            "amplitude A = 2, whatever the value of μ, as long as it is "
            "small. The estimate is remarkably good. Measured on an accurate "
            "numerical solution, the cycle's largest x is 2.0001 at μ = 0.1, "
            "2.002 at μ = 0.5 and 2.009 at μ = 1, and it never goes far above "
            "2 even when μ is not small: 2.020 at μ = 2 and 2.014 at μ = 10."
        ),
        Para(
            "The period is another matter. At μ = 0.1 the measured period is "
            "6.287, very close to the harmonic oscillator's 2π ≈ 6.283. At "
            "μ = 1 it is 6.663, at μ = 2 it is 7.630, and at μ = 10 it is "
            "19.08. For large μ the motion becomes a *relaxation "
            "oscillation*: long slow stretches during which x creeps along, "
            "punctuated by sudden jumps. The largest value of |x'| on the "
            "cycle shows it: 2.68 at μ = 1 and about 14.2 at μ = 10. The "
            "period for large μ grows like "
            "(3 − 2 ln 2)μ ≈ 1.614μ, though the approach to that leading "
            "term is slow: at μ = 10 it predicts 16.1 against the measured "
            "19.1. This is also where Van der Pol becomes stiff, which is why "
            "the application's Stiffness screen uses it as its example."
        ),
        Para(
            "What the energy argument does not supply is a proof. It shows "
            "what the amplitude must be if there is a cycle, for small μ. "
            "That there is exactly one cycle for every μ > 0, and that it "
            "attracts every trajectory except the origin, is Liénard's "
            "theorem, whose proof is beyond this course but whose statement "
            "is easy to check. Write the equation as x'' + f(x)x' + g(x) = 0 "
            "and let F(x) be the integral of f from 0 to x. If f is even, g "
            "is odd with xg(x) > 0 for x ≠ 0, and F has exactly one positive "
            "zero a, is negative on (0, a), and is positive and increasing "
            "beyond a, tending to infinity, then there is exactly one limit "
            "cycle, and it is stable. For Van der Pol f(x) = μ(x² − 1), "
            "g(x) = x and F(x) = μ(x³/3 − x), with a = √3, and every "
            "condition holds. But existence alone can be proved with a much "
            "more general tool."
        ),
    )),
    Section("The Poincaré–Bendixson theorem", (
        Para(
            "Everything a trajectory of a planar system can do in the long "
            "run is covered by a single theorem, begun by Poincaré in the "
            "1880s and completed by Bendixson in 1901. It concerns trajectories "
            "that stay in a bounded region for all future time."
        ),
        Box(
            "definition", "Trapping region",
            "A closed, bounded region R of the plane is a trapping region if "
            "every trajectory that starts in R stays in R for all t ≥ 0. "
            "Usually this is checked on the boundary: if the vector field "
            "points into R, or along its edge, at every boundary point, no "
            "trajectory can leave.",
        ),
        Box(
            "theorem", "Poincaré–Bendixson",
            "Let x' = f(x, y), y' = g(x, y) have continuously differentiable "
            "right-hand sides, and suppose a trajectory stays in a closed, "
            "bounded region R for all t ≥ 0. If R contains no equilibrium, "
            "the trajectory is a closed orbit or spirals towards one as "
            "t → ∞, and in either case R contains a closed orbit. More "
            "generally, if R contains finitely many equilibria, the "
            "trajectory approaches an equilibrium, a closed orbit, or a "
            "closed chain of equilibria joined by trajectories that run from "
            "one to the next and back round to the first (for instance a "
            "saddle with a loop that leaves it and returns to it).",
            r"\text{trapping region} + \text{no equilibria} "
            r"\;\Longrightarrow\; \text{a closed orbit inside}",
        ),
        Box(
            "remark", "Why it is true",
            "The full proof is long, but its heart is short and is pure "
            "geometry of the plane. Because the trajectory is bounded, it "
            "keeps returning near some point q. Because R holds no "
            "equilibrium, q is not one, and the flow at q has a direction. "
            "Draw a short segment through q crossing the flow transversally; "
            "the trajectory crosses it again and again. Take two successive "
            "crossings, at p₁ and later at p₂. The arc of trajectory from p₁ "
            "to p₂, closed up by "
            "the piece of segment between them, is a closed curve, and by the "
            "Jordan curve theorem it divides the plane into an inside and an "
            "outside. The trajectory cannot cross its own arc, and it can "
            "cross the segment piece in one direction only, so once it has "
            "gone in, it can never come back out. Every later crossing of the "
            "segment is therefore further along it in the same direction: "
            "the crossings form a monotone sequence. A monotone bounded "
            "sequence converges. The trajectory through the limit point "
            "returns to that same point, so it is a closed orbit, and the "
            "original trajectory spirals towards it.",
        ),
        Para(
            "The theorem is used in two directions. As a construction, it "
            "turns a picture like Van der Pol's, an unstable origin inside "
            "bounded motion, into a proof: find a region the flow cannot leave, with no "
            "equilibrium inside, and a closed orbit must be there. Because "
            "every closed orbit of a planar system encloses at least one "
            "equilibrium (a fact from index theory, stated here without "
            "proof), a trapping region with no equilibrium in it cannot be a "
            "disc. It has a hole, and the typical one is an annulus around "
            "an unstable equilibrium: the flow leaves the inner edge because "
            "the equilibrium repels, and crosses the outer edge inwards "
            "because something bounds the motion far out. As a restriction, "
            "the theorem lists everything that can happen, and chaos is not "
            "on the list."
        ),
    )),
    Section("Proving a cycle exists", (
        Worked(
            "The annulus for the polar example",
            "Show with Poincaré–Bendixson that equation 1 with μ = 1 has a "
            "closed orbit, without solving anything.",
            (
                Step("Take the annulus 1/2 ≤ r ≤ 2. On the inner circle, "
                     "r' = (1/2)(1 − 1/4) = 3/8 > 0, so trajectories cross it "
                     "outwards, into the annulus. On the outer circle, "
                     "r' = 2(1 − 4) = −6 < 0, so they cross it inwards.",
                     r"r = \frac{1}{2}:\ r' = \frac{3}{8} > 0, \qquad "
                     r"r = 2:\ r' = -6 < 0"),
                Step("So the annulus is a trapping region. The only "
                     "equilibrium is the origin, which is outside it, so the "
                     "theorem gives a closed orbit in the annulus. Of course "
                     "here the polar form also says exactly where: r = 1."),
            ),
        ),
        Para(
            "The theorem earns its keep when the polar form does not "
            "decouple. The next system mixes x and y in its cubic terms "
            "unequally, so neither r' nor θ' is a function of r alone."
        ),
        Worked(
            "A cycle nobody can write down",
            "Show that x' = x − y − x(x² + 2y²), y' = x + y − y(x² + y²) has a "
            "closed orbit.",
            (
                Step("Compute rr' = xx' + yy'. The terms −xy and +xy cancel, "
                     "and the cubic terms give −x⁴ − 2x²y² − x²y² − y⁴, so "
                     "rr' = x² + y² − (x⁴ + 3x²y² + y⁴) = r² − r⁴ − x²y².",
                     r"r r' = r^{2} - r^{4} - x^{2}y^{2}"),
                Step("Compute r²θ' = xy' − yx'. The linear terms give "
                     "x² + y², and the cubic terms give −xy(x² + y²) + "
                     "xy(x² + 2y²) = xy³, so r²θ' = r² + xy³.",
                     r"r^{2}\theta' = r^{2} + x y^{3}"),
                Step("Divide the first by r and the second by r², and "
                     "substitute x²y² = r⁴ sin²2θ/4 and xy³ = r⁴ cos θ sin³θ:",
                     r"r' = r - r^{3}\left(1 + \frac{1}{4}\sin^{2}2\theta\right), "
                     r"\qquad \theta' = 1 + r^{2}\cos\theta\sin^{3}\theta"),
                Step("The bracket lies between 1 and 5/4. So r' ≥ r − (5/4)r³, "
                     "which is positive for r < 2/√5 ≈ 0.894; on the circle "
                     "r = 0.8 it is at least 0.8 − 1.25(0.512) = 0.16. And "
                     "r' ≤ r − r³, which is negative for r > 1; on the circle "
                     "r = 1.1 it is at most 1.1 − 1.331 = −0.231. The annulus "
                     "0.8 ≤ r ≤ 1.1 is a trapping region.",
                     r"0.8 \leq r \leq 1.1"),
                Step("Equilibria need θ' = 0. The largest value of "
                     "|cos θ sin³θ| is 3√3/16 ≈ 0.325, so in the annulus "
                     "θ' ≥ 1 − (1.21)(0.325) ≈ 0.61 > 0. There is no "
                     "equilibrium in it; the only one anywhere is the origin, "
                     "whose Jacobian has rows (1, −1) and (1, 1), eigenvalues "
                     "1 ± i, an unstable spiral.",
                     r"|\cos\theta\sin^{3}\theta| \leq \frac{3\sqrt{3}}{16}"),
                Step("By Poincaré–Bendixson the annulus contains a closed "
                     "orbit. Numerically, the limit-cycle finder confirms an "
                     "attracting cycle with period about 6.500, lying between "
                     "radii of about 0.91 and 0.97, inside the tighter annulus "
                     "0.894 ≤ r ≤ 1 that the same argument allows. Its period "
                     "is not 2π, because θ' is not constant."),
            ),
        ),
        Para(
            "Van der Pol can be treated the same way, though drawing the "
            "outer edge takes more work than a circle: a large circle is not "
            "crossed inwards everywhere, because the damping is negative in "
            "the strip |x| < 1 at every radius: on the circle r = R, "
            "rr' = μ(1 − x²)y², which is μR² > 0 at the top point (0, R). A "
            "suitable outer curve can be built from pieces of simpler curves, "
            "but for Van der Pol the construction is long and is not "
            "reproduced here. The inner edge is "
            "easy: a small circle round the unstable origin, which "
            "trajectories leave. With the outer curve in place, the annulus "
            "between them has no equilibrium and the theorem gives the cycle."
        ),
        Para(
            "Circles are not the only boundaries. When the flow has no polar "
            "structure, a trapping region is usually assembled from straight "
            "lines and nullclines, checking the sign of the flow across each "
            "piece, and the next example does exactly that. It also keeps a "
            "promise of the ecological-models chapter: a model of populations that "
            "cycle steadily, at an amplitude of their own choosing, needs a "
            "limit cycle. The Lotka–Volterra model has only a centre, and "
            "adding logistic growth to the prey alone turned its orbits into "
            "spirals. The missing ingredient is a predator that can only eat "
            "so fast: each predator takes prey at the rate x/(1 + x), which "
            "grows with x at first and then levels off at 1, a saturating "
            "appetite. In scaled units, with the prey's carrying capacity K "
            "and the predators' death rate d, this is the "
            "Rosenzweig–MacArthur model."
        ),
        Display(r"x' = x\left(1 - \frac{x}{K}\right) - \frac{xy}{1 + x}, "
                r"\qquad y' = y\left(\frac{x}{1 + x} - d\right)", "8"),
        Worked(
            "A predator–prey cycle",
            "Take K = 6 and d = 1/2 in equation 8. Find and classify the "
            "equilibria, build a trapping region from straight lines, and "
            "conclude that the populations settle onto a cycle.",
            (
                Step("Equilibria. y' = 0 needs y = 0 or x/(1 + x) = 1/2, "
                     "that is x = 1. With y = 0, x' = 0 gives x = 0 or x = 6. "
                     "With x = 1, x' = 0 needs y = (1 − x/6)(1 + x) = 5/3, the "
                     "prey nullcline. So the equilibria are (0, 0), (6, 0) "
                     "and (1, 5/3)."),
                Step("Classify. At (1, 5/3) the partial derivatives are "
                     "1 − 2x/6 − y/(1 + x)² = 1/4 and −x/(1 + x) = −1/2 for x', "
                     "and y/(1 + x)² = 5/12 and x/(1 + x) − 1/2 = 0 for y'. So "
                     "τ = 1/4, Δ = 5/24 and τ² − 4Δ = −37/48 < 0: an unstable "
                     "spiral, with λ = 1/8 ± (√111/24)i. At (0, 0) the Jacobian "
                     "has rows (1, 0) and (0, −1/2), and at (6, 0) rows "
                     "(−1, −6/7) and (0, 5/14): both are saddles.",
                     r"\tau = \frac{1}{4}, \qquad \Delta = \frac{5}{24}, "
                     r"\qquad \lambda = \frac{1}{8} \pm \frac{\sqrt{111}}{24}i"),
                Step("The boundary. The axes are made of trajectories, since "
                     "x = 0 gives x' = 0 and y = 0 gives y' = 0, so nothing "
                     "crosses them. On the line x = 6, x' = −6y/7 ≤ 0, so the "
                     "flow crosses it leftwards. For the slanted edge add the "
                     "two equations: the predation terms cancel, leaving "
                     "(x + y)' = x(1 − x/6) − y/2. On the line x + y = 10 this "
                     "is −x²/6 + 3x/2 − 5, whose largest value for "
                     "0 ≤ x ≤ 6 is −13/8, at x = 9/2. So x + y decreases "
                     "there. The quadrilateral with corners (0, 0), (6, 0), "
                     "(6, 4) and (0, 10) is a trapping region.",
                     r"(x + y)' = -\frac{x^{2}}{6} + \frac{3x}{2} - 5 "
                     r"\leq -\frac{13}{8} \text{ on } x + y = 10"),
                Step("The region contains all three equilibria, so use the "
                     "general form of the theorem. Start inside, anywhere but "
                     "(1, 5/3). The trajectory cannot approach (1, 5/3), which "
                     "repels everything near it. It cannot approach a saddle "
                     "either, since the only trajectories that reach (0, 0) "
                     "come down the y-axis and the only ones that reach "
                     "(6, 0) come along the x-axis, and it is on neither. For "
                     "the same reason there is no closed chain of equilibria: "
                     "the x-axis carries (0, 0) to (6, 0), but nothing "
                     "carries (6, 0) back to (0, 0). What is left is a closed "
                     "orbit, and it goes round (1, 5/3)."),
                Step("The limit-cycle finder confirms an attracting cycle "
                     "with period about 24.8, on which the prey range from "
                     "about 0.009 to 5.66 and the predators from about 0.074 "
                     "to 4.43. Starting from (5, 4) instead leads to the same "
                     "cycle. The swings are violent: at their lowest the prey "
                     "are below 1% of their equilibrium level."),
            ),
        ),
        Plot(
            "A trapping region built from lines",
            "The nullclines and the trapping region of the predator–prey "
            "example with K = 6 and d = 1/2. The prey nullcline "
            "y = (1 − x/6)(1 + x) is a hump, and the predator nullcline is "
            "the vertical line x = 1; they cross at the unstable spiral "
            "(1, 5/3). The region is bounded by the axes, the line x = 6 and "
            "the line x + y = 10, and the flow crosses the last two inwards.",
            (Curve("t", "prey nullcline", y="(1 - t/6)*(1 + t)"),
             Curve("1 + 0*t", "predator nullcline x = 1", y="t"),
             Curve("6 + 0*t", "edge x = 6", y="2*t/3"),
             Curve("t", "edge x + y = 10", y="10 - t")),
            t=(0.0, 6.0), xlabel="x (prey)", ylabel="y (predators)",
            ylim=(0.0, 10.5),
        ),
        Para(
            "The trace at the coexistence point, for d = 1/2 and any K > 1, "
            "is τ = (K − 3)/(2K), while Δ = (K − 1)/(4K) stays positive. For "
            "K < 3 the point is stable and the populations settle to it; as "
            "K passes 3 the trace changes sign, the point becomes an "
            "unstable spiral, and the cycle appears. Enriching the prey's "
            "environment destabilises the system, a result ecologists call "
            "the paradox of enrichment. It is also the Hopf bifurcation of "
            "the next chapter, met in a living system."
        ),
    )),
    Section("Ruling cycles out", (
        Para(
            "Proving that a system has no closed orbit is as useful as "
            "proving that it has one, and there is a simple test for it, "
            "based on how the flow stretches areas. The divergence of the "
            "field is ∂f/∂x + ∂g/∂y."
        ),
        Box(
            "theorem", "Bendixson's and Dulac's criteria",
            "Let B(x, y) be continuously differentiable on a region with no "
            "holes in it. If ∂(Bf)/∂x + ∂(Bg)/∂y is strictly positive "
            "throughout the region, or strictly negative throughout it, then "
            "no closed orbit lies entirely in that region. This is Dulac's "
            "criterion; Bendixson's criterion is the case B = 1, where the "
            "quantity is the divergence ∂f/∂x + ∂g/∂y itself.",
            r"\frac{\partial (Bf)}{\partial x} + \frac{\partial (Bg)}{\partial y} "
            r"> 0 \text{ (or } < 0) \;\Longrightarrow\; \text{no closed orbit}",
        ),
        Box(
            "proof", "Proof",
            "It is the Green's-theorem argument of the ecological-models chapter, "
            "which proved that competitors never cycle, with (Bf, Bg) in "
            "place of the fields used there. Suppose C were a closed orbit in "
            "the region, with period T, enclosing the domain D; D lies in the "
            "region because the region has no holes. By Green's theorem the "
            "integral of ∂(Bf)/∂x + ∂(Bg)/∂y over D equals the line integral "
            "of Bf dy − Bg dx round C. Along C, dx = f dt and dy = g dt, so "
            "the integrand is B(fg − gf) = 0 and the line integral is zero. "
            "But the integrand over D is continuous and strictly of one sign, "
            "so its integral over D is not zero.",
            r"\int\int_{D}\left(\frac{\partial (Bf)}{\partial x} + "
            r"\frac{\partial (Bg)}{\partial y}\right)dA = \int_{0}^{T}"
            r"B(f g - g f)\,dt = 0",
        ),
        Para(
            "The ecological-models chapter used B = 1/(xy) in the open quadrant, "
            "where it made the quantity −1/y − 1/x, negative everywhere. "
            "Choosing B is an art, and B = 1 is simply the first thing to "
            "try."
        ),
        Worked(
            "Three systems through Bendixson's test",
            "Apply the criterion to the damped pendulum x' = y, "
            "y' = −sin x − cy with c > 0; to equation 1; and to Van der Pol.",
            (
                Step("For the damped pendulum the divergence is "
                     "0 + (−c) = −c < 0 everywhere, so there is no closed "
                     "orbit anywhere in the plane. Friction has destroyed "
                     "every one of the frictionless pendulum's swinging "
                     "orbits, however small the friction, which is what "
                     "LaSalle's principle showed in the nonlinear-mechanics "
                     "chapter, reached here in one line.",
                     r"\nabla\cdot\mathbf{F} = -c"),
                Step("For equation 1 the divergence is (μ − 3x² − y²) + "
                     "(μ − x² − 3y²) = 2μ − 4r². It is positive in the disc "
                     "r² < μ/2 and negative outside it. The disc has no "
                     "holes, so no closed orbit lies inside it. The outside "
                     "has a hole, so there the criterion only rules out "
                     "closed orbits that do not go round the disc. Any closed "
                     "orbit must therefore meet the disc or enclose it, and "
                     "the cycle r = √μ encloses it, lying wholly where the "
                     "divergence is −2μ < 0. This is why the criterion needs "
                     "the no-holes hypothesis: without it, the cycle r = √μ "
                     "would be a counterexample.",
                     r"\nabla\cdot\mathbf{F} = 2\mu - 4r^{2}"),
                Step("For Van der Pol the divergence is 0 + μ(1 − x²), "
                     "positive in the strip |x| < 1 and negative outside it. A "
                     "closed orbit cannot lie inside the strip, so it must "
                     "reach |x| > 1: consistent with an amplitude of about 2.",
                     r"\nabla\cdot\mathbf{F} = \mu(1 - x^{2})"),
            ),
        ),
        Para(
            "The divergence is the rate at which the flow expands area, and a "
            "cycle needs expansion somewhere and contraction somewhere else "
            "to balance: that is the energy balance of Van der Pol in "
            "another language. Two other quick tests follow from facts "
            "already met. A closed orbit must enclose an equilibrium, so a "
            "region with none, and no holes, contains no closed orbit. And a "
            "system with a Lyapunov function that strictly decreases along "
            "every non-constant trajectory has no closed orbit, because the "
            "function would have to return to its starting value."
        ),
    )),
    Section("Why the plane forbids chaos", (
        Para(
            "Read the Poincaré–Bendixson theorem as a list. A bounded "
            "trajectory of an autonomous planar system with only finitely "
            "many equilibria approaches an equilibrium, a closed orbit, or a "
            "closed chain of equilibria joined by trajectories. That is all. "
            "A trajectory cannot wander for ever in a bounded region without "
            "settling into one of those three patterns, and in each of them "
            "its long-run behaviour is simple and predictable: nearby starts "
            "that settle onto the same attractor stay together. (With "
            "infinitely many equilibria there is one more possibility, a "
            "trajectory winding ever more slowly onto a whole curve of "
            "equilibria; that is not chaotic either.)"
        ),
        Para(
            "Chaos is the opposite: bounded motion that never settles into a "
            "pattern, with nearby starts separating exponentially, so that "
            "any small error eventually ruins a prediction. The theorem says "
            "this cannot happen for x' = f(x, y), y' = g(x, y), however "
            "nonlinear f and g are. The reason is the one fact at the heart "
            "of the proof sketch: in the plane a trajectory cannot cross "
            "itself, and a closed curve has an inside and an outside. To mix "
            "trajectories up, the flow would have to pass them over and under "
            "each other, and the plane has no over and under."
        ),
        Box(
            "theorem", "No chaos in the plane",
            "An autonomous system of two first-order equations with "
            "continuously differentiable right-hand sides cannot be chaotic. "
            "Chaos needs at least three dimensions, and an autonomous single "
            "equation x' = f(x) cannot even oscillate: on a phase line every "
            "solution is monotone.",
            r"\text{planar, autonomous} \;\Longrightarrow\; \text{no chaos}",
        ),
        Para(
            "Both hypotheses matter. With a third variable, trajectories can "
            "pass above and below each other, and Lorenz's three-equation "
            "model of convection, met in the bifurcations chapter, does "
            "exactly that. And a time-dependent forcing acts as a third "
            "dimension. The forced Duffing oscillator x'' + cx' − x + x³ = F cos ωt "
            "looks planar, but its right-hand side depends on t; adding "
            "θ = ωt as a variable with θ' = ω makes it an autonomous system in "
            "three dimensions, and for suitable parameters it is chaotic. "
            "The planar theorem simply does not apply to it."
        ),
        Para(
            "The application respects the theorem. The routine behind the "
            "Solver Lab's predictability horizon estimates the largest "
            "Lyapunov exponent, the rate at which neighbouring trajectories "
            "separate. Over a finite run that estimate can come out slightly "
            "positive for a planar system, because orbits speed up and slow "
            "down along a cycle. For an autonomous system in one or two "
            "dimensions the routine refuses to call such a value chaotic and "
            "treats it as indistinguishable from zero, so no horizon could "
            "ever be drawn for one."
        ),
    )),
    Section("Common errors", (
        Box(
            "warning", "The radius is the square root",
            "In r' = r(μ − r²) the cycle is where r² = μ, so its radius is "
            "√μ, not μ. For r' = r(4 − r²) the cycle has radius 2.",
        ),
        Para(
            "Other errors recur. The first is to look for a limit cycle in "
            "the Jacobian. Linearisation classifies equilibria, and a cycle "
            "is not an equilibrium; the most the Jacobian can do is show that "
            "an equilibrium repels, which is the inner edge of a trapping "
            "annulus. The second is to conclude that a trapping region "
            "contains a closed orbit when it contains an equilibrium the "
            "trajectories might simply be approaching: a disc around a stable "
            "spiral traps everything and holds no cycle at all. The hole in "
            "the annulus, cut round an equilibrium that repels, is what "
            "excludes that fate. The third is to apply Poincaré–Bendixson, or "
            "the no-chaos conclusion drawn from it, to a forced or "
            "three-dimensional system, where it does not hold. The fourth is to "
            "expect a cycle's period to be 2π because a polar example had "
            "θ' = 1; the period is set by the whole orbit, and in the "
            "example that nobody could solve it was about 6.500, while Van "
            "der Pol's grows with μ without bound."
        ),
    )),
    Section("Summary", (
        Para(
            "A limit cycle is an isolated closed orbit, and it is the only "
            "way an autonomous planar system can oscillate at an amplitude of "
            "its own choosing. "
            "Linear systems cannot have one, since their closed orbits come "
            "in scaled families, and conservative systems cannot have an "
            "attracting one, since their conserved quantity labels the "
            "orbits. In polar form the normal-form system becomes "
            "r' = r(μ − r²), θ' = 1, whose radial phase line shows a stable "
            "cycle of radius √μ for μ > 0, attracting at the rate e^(−2μt), "
            "around an origin whose Jacobian eigenvalues μ ± i see the spiral "
            "but not the cycle. Reversing the signs gives an unstable cycle, "
            "a boundary between basins rather than a destination. Van der "
            "Pol's equation pumps energy in at small amplitude and removes it "
            "at large amplitude, and the balance, amplitude close to 2, is "
            "its cycle. Poincaré–Bendixson proves a cycle exists whenever a "
            "trapping region holds no equilibrium, or only equilibria that "
            "trajectories cannot approach, as in the predator–prey model with "
            "a saturating appetite; Bendixson's divergence test and Dulac's "
            "weighted form of it rule cycles out; and together they explain "
            "why a planar autonomous system (with finitely many equilibria) "
            "can settle only to equilibria, cycles, or closed chains of "
            "equilibria, and never become chaotic. The next "
            "chapter follows what happens as a parameter moves: the Hopf "
            "bifurcation that created the cycle of equation 1, the "
            "bifurcations of equilibria, and the third dimension that lets "
            "chaos in."
        ),
    )),
)


BIFURCATIONS = (
    Section("A number moves, and the picture jumps", (
        Para(
            "Raise the harvest from a fish population a little and the "
            "population falls a little. Raise it a little more and the "
            "population collapses to nothing, not gradually but all at once. "
            "Nothing about the equation changed except a number, and the "
            "qualitative behaviour changed completely. Unit 2 met that sudden "
            "change on the phase line and called it a *bifurcation*. It is the "
            "most practically important thing "
            "nonlinear equations do: it is how a steady state that looked "
            "safe stops existing, how a quiet chemical mixture starts to "
            "oscillate, and how a beam that was straight buckles to one side."
        ),
        Para(
            "Every chapter of this unit so far has studied one system at a "
            "time: found its equilibria, linearised at each, drawn its "
            "nullclines, conserved its energy or trapped its limit cycle. "
            "This one studies a *family* of systems, one for each value of a "
            "parameter, and asks where in the family the picture changes. "
            "For the equilibria the answer turns out to be short. Near almost "
            "every parameter value nothing changes qualitatively near an "
            "equilibrium, and the exceptions are exactly the cases the "
            "almost-linear chapter could not decide: an eigenvalue at zero, "
            "or a complex pair on the imaginary axis. Four standard pictures, "
            "the saddle-node, transcritical, pitchfork and Hopf bifurcations, "
            "describe what happens at those exceptions in almost every system "
            "that has them. Changes that involve periodic orbits or whole "
            "regions of the phase space, called *global* bifurcations, can "
            "happen while every equilibrium stays hyperbolic; the Lorenz "
            "section meets one, but their theory is beyond this chapter."
        ),
        Para(
            "The chapter ends by leaving the plane. The limit-cycles chapter "
            "showed that an autonomous planar system can only settle down, "
            "cycle, or run away. With three variables that restriction goes, "
            "and past enough bifurcations lies *chaos*: deterministic "
            "equations whose solutions are so sensitive to their starting "
            "values that prediction beyond a certain horizon is impossible. "
            "One well-trodden road there is a cascade of period doublings, "
            "which the logistic map shows in its simplest form. Lorenz found "
            "chaos in a model of convection, and the last sections measure "
            "his system's horizon."
        ),
    )),
    Section("Where the picture can change", (
        Para(
            "Take a scalar equation x' = f(x, r) that depends on a parameter "
            "r, and suppose that at r = r₀ it has an equilibrium x₀ with "
            "f_x(x₀, r₀) ≠ 0. The phase-line test of Unit 2 says the "
            "equilibrium is stable if f_x < 0 and unstable if f_x > 0. Now "
            "change r slightly. Does the equilibrium survive, and does it "
            "keep its stability?"
        ),
        Box(
            "theorem", "Hyperbolic equilibria persist",
            "Let f be continuously differentiable, f(x₀, r₀) = 0 and "
            "f_x(x₀, r₀) ≠ 0. Then for every r close enough to r₀ there is "
            "exactly one equilibrium x*(r) near x₀, it depends smoothly on r, "
            "and f_x(x*(r), r) has the same sign as f_x(x₀, r₀), so the "
            "equilibrium keeps its stability.",
            r"f(x^{*}(r), r) = 0, \qquad \frac{dx^{*}}{dr} = "
            r"-\frac{f_r}{f_x}",
        ),
        Box(
            "proof", "Proof",
            "This is the implicit function theorem: the equation f(x, r) = 0 "
            "can be solved for x as a smooth function of r near (x₀, r₀) "
            "precisely because f_x is not zero there, and the solution is "
            "unique in a neighbourhood of x₀. Differentiating "
            "f(x*(r), r) = 0 with respect to r gives f_x·dx*/dr + f_r = 0, "
            "which is the displayed slope. Finally f_x is continuous and "
            "nonzero at (x₀, r₀), so it keeps its sign along the curve for r "
            "near r₀.",
        ),
        Para(
            "The same is true in the plane, with the Jacobian in place of "
            "f_x. An equilibrium whose Jacobian has no eigenvalue with zero "
            "real part is called hyperbolic, and the almost-linear chapter "
            "showed that its local picture is the linear one. A small change "
            "of parameter moves the Jacobian's trace and determinant a "
            "little, and the phase-portraits chapter of Unit 6 showed that "
            "the saddle, node and spiral regions of the trace–determinant "
            "plane are open: a point inside one of them stays inside it. So "
            "a hyperbolic equilibrium moves a little and keeps its "
            "stability, and a saddle stays a saddle. Only an equilibrium "
            "sitting exactly on the parabola τ² = 4Δ, a star or degenerate "
            "node, can change type under an arbitrarily small change, from "
            "node to spiral of the same stability, and that, as the Common "
            "errors section explains, is not a bifurcation. An equilibrium "
            "can appear, vanish or change stability only when it is *not* "
            "hyperbolic."
        ),
        Box(
            "definition", "Bifurcation",
            "A parameter value at which the qualitative picture of a family "
            "of systems changes: equilibria appear, disappear or change "
            "stability, or a periodic orbit is born or dies. The value is "
            "called a bifurcation point, and at a bifurcation of an "
            "equilibrium that equilibrium is non-hyperbolic.",
            r"\mathrm{Re}\,\lambda = 0 \text{ at the bifurcation}",
        ),
        Para(
            "In the trace–determinant plane there are two ways to be "
            "non-hyperbolic, and so two ways for a planar equilibrium to "
            "bifurcate. The point (τ, Δ) can cross the τ-axis, where Δ = 0: "
            "a real eigenvalue passes through zero. Or it can cross the "
            "positive Δ-axis, where τ = 0 and Δ > 0: a complex pair passes "
            "through the imaginary axis. The first kind happens already in "
            "one dimension and gives the saddle-node, transcritical and "
            "pitchfork bifurcations. The second needs two dimensions and "
            "gives the Hopf bifurcation. Crossing the parabola τ² = 4Δ, from "
            "node to spiral, is *not* a bifurcation: the equilibrium keeps "
            "its stability and trajectories merely start to turn."
        ),
    )),
    Section("Saddle-node: two equilibria collide and vanish", (
        Para(
            "The simplest family with a bifurcation is"
        ),
        Display(r"x' = r + x^{2}", "1"),
        Para(
            "For r < 0 the equilibria are x = ±√(−r). The derivative of the "
            "right-hand side is 2x, negative at −√(−r) and positive at "
            "+√(−r), so the lower equilibrium is stable and the upper one "
            "unstable. As r rises towards 0 the two move together, and at "
            "r = 0 they meet at x = 0, where the derivative is zero: the "
            "single equilibrium is semi-stable, attracting from below and "
            "repelling above. For r > 0 the right-hand side is positive "
            "everywhere, there are no equilibria at all, and every solution "
            "increases without bound. Two equilibria, one stable and one "
            "unstable, have collided and annihilated each other."
        ),
        Display(r"x^{*} = \pm\sqrt{-r}\quad (r < 0), \qquad "
                r"f_x(\pm\sqrt{-r}) = \pm 2\sqrt{-r}", "2"),
        Para(
            "Why this particular equation? Because almost every collision of "
            "two equilibria looks like this one when seen close up. Suppose f(x₀, r₀) = 0 "
            "and f_x(x₀, r₀) = 0, so that the implicit function theorem "
            "fails, but the next terms of the Taylor expansion do not "
            "vanish."
        ),
        Box(
            "theorem", "The saddle-node normal form",
            "If f(x₀, r₀) = 0 and f_x(x₀, r₀) = 0, while f_r(x₀, r₀) ≠ 0 and "
            "f_xx(x₀, r₀) ≠ 0, then near (x₀, r₀) the equation x' = f(x, r) "
            "has two equilibria on one side of r₀ and none on the other, "
            "and to leading order it is x' = r + x² after shifting, scaling "
            "and possibly reversing x and r.",
            r"f(x, r) \approx f_r\,(r - r_0) + \frac{1}{2}f_{xx}\,"
            r"(x - x_0)^{2}",
        ),
        Box(
            "proof", "Proof sketch",
            "Expand f about (x₀, r₀). The constant term and the x-term vanish "
            "by hypothesis, and the leading terms left are f_r(r − r₀) and "
            "½f_xx(x − x₀)², the mixed and higher terms being smaller near the "
            "point. Setting the displayed approximation to zero gives "
            "(x − x₀)² = −2f_r(r − r₀)/f_xx, which has two roots when the "
            "right side is positive and none when it is negative. Rescaling "
            "x − x₀ and r − r₀ by constants turns the approximation into "
            "r + x².",
        ),
        Para(
            "The lesson's first example is the same family seen from the "
            "other side. In y' = c − y² the equilibria ±√c exist for c > 0, "
            "and the substitution x = −y turns the equation into "
            "x' = −c + x², which is equation 1 with r = −c. So raising r "
            "through zero in equation 1 is lowering c through zero here."
        ),
        Worked(
            "The saddle-node form before the collision",
            "Solve y' = 4 − y² with y(0) = 0, and say what happens to the "
            "equilibria as the constant 4 is lowered through zero.",
            (
                Step("The equilibria are y = ±2. The derivative of 4 − y² is "
                     "−2y, which is −4 at y = 2 and +4 at y = −2, so 2 is "
                     "stable and −2 unstable. Between them 4 − y² > 0, so the "
                     "solution from 0 increases towards 2. Below −2 the "
                     "right-hand side is negative and grows like −y², so a "
                     "start just below −2 runs off to −∞ in finite time: the "
                     "unstable equilibrium is a threshold.",
                     r"f(y) = 4 - y^{2}, \qquad f'(2) = -4, \quad f'(-2) = 4"),
                Step("Separate with partial fractions. For |y| < 2 the "
                     "integral of 1/(4 − y²) is (1/4) ln((2 + y)/(2 − y)), "
                     "and the start y(0) = 0 makes the constant zero.",
                     r"\frac{1}{4}\ln\frac{2 + y}{2 - y} = t"),
                Step("Solve for y: (2 + y)/(2 − y) = e^(4t) gives "
                     "y = 2(e^(4t) − 1)/(e^(4t) + 1), which is 2 tanh 2t. It "
                     "tends to 2, the stable equilibrium.",
                     r"y = 2\tanh 2t \;\longrightarrow\; 2"),
                Step("Replace 4 by c. The equilibria ±√c move together as c "
                     "falls, meet at 0 when c = 0, and for c < 0 are gone: "
                     "then y' = c − y² < 0 everywhere and every solution "
                     "decreases without limit. The solution that settled at "
                     "√c now has nowhere to settle."),
            ),
            equation="y' = 4 - y**2",
            conditions="y(0) = 0",
            answer="y = 2*tanh(2*t)",
            answer_latex=r"y = 2\tanh 2t",
        ),
        Para(
            "The name comes from the plane. Add a second, uninteresting "
            "variable that simply decays, y' = −y. At an equilibrium (x*, 0) "
            "the Jacobian is diagonal with entries 2x* and −1, so the "
            "equilibrium at −√(−r) has two negative eigenvalues, a stable "
            "node, and the one at +√(−r) has eigenvalues of opposite signs, "
            "a saddle. The bifurcation is the collision of a saddle with a "
            "node, and at the moment of collision the determinant of the "
            "Jacobian, 2x*·(−1), passes through zero: the point (τ, Δ) "
            "crosses the τ-axis."
        ),
        Worked(
            "A saddle and a node about to merge",
            "Take r = −1 in x' = r + x², y' = −y. Classify both equilibria, "
            "and solve from (0, 1), a point between them.",
            (
                Step("The equilibria are (−1, 0) and (1, 0). At (−1, 0) the "
                     "Jacobian has rows (−2, 0) and (0, −1): a stable node. At "
                     "(1, 0) it has rows (2, 0) and (0, −1), determinant −2: a "
                     "saddle, whose stable line is the vertical line x = 1.",
                     r"\lambda = -2,\ -1 \text{ (node)}, \qquad "
                     r"\lambda = 2,\ -1 \text{ (saddle)}"),
                Step("The system is decoupled, so each equation can be solved "
                     "alone. y' = −y with y(0) = 1 gives y = e^(−t). For x, "
                     "separate x' = x² − 1: the integral of 1/(x² − 1) is "
                     "(1/2) ln|(x − 1)/(x + 1)|, and x(0) = 0 fixes the "
                     "constant at zero.",
                     r"\frac{1}{2}\ln\frac{1 - x}{1 + x} = t"),
                Step("So (1 − x)/(1 + x) = e^(2t), which solves to "
                     "x = (1 − e^(2t))/(1 + e^(2t)) = −tanh t. The trajectory "
                     "runs left and down into the node at (−1, 0).",
                     r"x = -\tanh t, \qquad y = e^{-t}"),
                Step("As r rises to 0 the node and the saddle slide together "
                     "along the x-axis, and at r = 0 they merge into one "
                     "equilibrium with a zero eigenvalue. For r > 0 there is "
                     "nothing left: every trajectory drifts off to the right "
                     "while its y decays."),
            ),
            equation="x' = x**2 - 1; y' = -y",
            conditions="x(0) = 0, y(0) = 1",
            answer="x = -tanh(t)\ny = exp(-t)",
            answer_latex=r"x = -\tanh t, \qquad y = e^{-t}",
        ),
        Para(
            "In that example nothing had to be located: the Jacobian was "
            "diagonal, and the zero eigenvalue could be read off. In a "
            "coupled system the saddle-node has to be found, and the way to "
            "find it is the one the trace–determinant plane suggests: follow "
            "det J along the equilibria and see where it reaches zero."
        ),
        Worked(
            "Locating a saddle-node in a coupled system",
            "Find the equilibria of x' = y − 2x, y' = μ + x² − y as functions "
            "of μ, classify them, and find where they collide.",
            (
                Step("At an equilibrium y = 2x from the first equation, and the "
                     "second becomes μ + x² − 2x = 0. So x = 1 ± √(1 − μ), "
                     "with y = 2x: two equilibria for μ < 1, one at μ = 1 and "
                     "none for μ > 1.",
                     r"x_{\pm} = 1 \pm \sqrt{1 - \mu}, \qquad y_{\pm} = 2x_{\pm}"),
                Step("The partial derivatives are ∂(y − 2x)/∂x = −2, "
                     "∂(y − 2x)/∂y = 1, ∂(μ + x² − y)/∂x = 2x and "
                     "∂(μ + x² − y)/∂y = −1. So J has rows (−2, 1) and "
                     "(2x, −1), with trace −3 and determinant 2 − 2x.",
                     r"\tau = -3, \qquad \Delta = 2 - 2x"),
                Step("At x₊ the determinant is −2√(1 − μ) < 0: a saddle. At x₋ "
                     "it is +2√(1 − μ) > 0 with τ < 0: stable, and a node "
                     "while τ² − 4Δ = 9 − 8√(1 − μ) stays positive, which is "
                     "for μ > −17/64. At μ = 3/4, for example, the equilibria "
                     "are (1/2, 1) with λ = (−3 ± √5)/2 ≈ −0.382, −2.618, a "
                     "stable node, and (3/2, 3) with λ = (−3 ± √13)/2 ≈ "
                     "0.303, −3.303, a saddle.",
                     r"\Delta_{\pm} = \mp 2\sqrt{1 - \mu}"),
                Step("Both determinants reach zero exactly when √(1 − μ) = 0, "
                     "at μ = 1, where the two equilibria meet at (1, 2). There "
                     "J has rows (−2, 1) and (2, −1), eigenvalues 0 and −3: a "
                     "real eigenvalue has reached zero while the other stays "
                     "negative, the saddle-node signature, and past μ = 1 "
                     "nothing is left.",
                     r"\mu = 1: \quad \lambda = 0,\ -3"),
            ),
        ),
    )),
    Section("Harvesting, and the ghost of an equilibrium", (
        Para(
            "Here is the fish population of the opening, which Unit 2 met on "
            "the phase line. With the population x measured in units of the "
            "carrying capacity and time in units of the reciprocal growth "
            "rate, the logistic equation is x' = x(1 − x), and fish are "
            "removed at a constant rate h."
        ),
        Display(r"x' = x(1 - x) - h, \qquad x_{\pm} = "
                r"\frac{1 \pm \sqrt{1 - 4h}}{2}, \qquad "
                r"f'(x_{\pm}) = \mp\sqrt{1 - 4h}", "3"),
        Para(
            "Unit 2 found the rest: the upper equilibrium x₊ is stable, the "
            "lower one x₋ unstable, and they meet at x = 1/2 when h = 1/4, "
            "the maximum sustainable harvest, and vanish beyond it. In this "
            "chapter's language that is a saddle-node, and the derivative in "
            "equation 3 is the saddle-node picture exactly: ∓√(1 − 4h), two "
            "slopes of opposite sign that shrink together to zero at the "
            "fold. The lower equilibrium is a threshold, since a population "
            "that falls below it dies out although the harvest has not "
            "changed. Two harvests show how the fold approaches. At h = 3/16 "
            "the equilibria are 1/4 and 3/4; at h = 0.2 they are about 0.276 "
            "and 0.724. The extra harvest has moved the stable population "
            "down only from 0.75 to 0.72, while the threshold has risen from "
            "0.25 to 0.28 to meet it. What is new here is what happens just "
            "past the fold."
        ),
        Plot(
            "The fold of a harvested population",
            "The equilibria of x' = x(1 − x) − h against the harvest h. The "
            "upper branch is the stable population, the lower one the "
            "unstable threshold; they meet at h = 1/4, x = 1/2, where the "
            "curves end, and for any larger h there is no equilibrium at "
            "all. A population "
            "sitting on the upper branch as h is raised slides gently down "
            "it and then, at the fold, falls off the end.",
            (Curve("(0.5 + 0.5*t)*(0.5 - 0.5*t)", "stable population",
                   y="0.5 + 0.5*t"),
             Curve("(0.5*t)*(1 - 0.5*t)", "unstable threshold", y="0.5*t"),
             Curve("0.25 + 0*t", "h = 1/4", y="t")),
            t=(0.0, 1.0), xlabel="harvest h", ylabel="equilibrium x",
            ylim=(0.0, 1.05),
        ),
        Para(
            "The warning in that picture is how little it gives. Up to the "
            "fold the stable population declines smoothly and not very far, "
            "from 1 at h = 0 to 1/2 at h = 1/4, and nothing in the steady "
            "state signals that the next increment is fatal. Past the fold "
            "the population does not decline to a lower level; it goes "
            "extinct."
        ),
        Worked(
            "Collapse in finite time",
            "Take h = 1/2, twice the critical harvest, and a population "
            "starting at the carrying capacity, x(0) = 1. Solve, and find "
            "when the population reaches zero.",
            (
                Step("Complete the square: x − x² − 1/2 = −(x − 1/2)² − 1/4. "
                     "With u = x − 1/2 the equation is u' = −(u² + 1/4), "
                     "negative everywhere.",
                     r"x' = -\left(x - \frac{1}{2}\right)^{2} - \frac{1}{4}"),
                Step("Separate: the integral of du/(u² + 1/4) is "
                     "2 arctan 2u, so 2 arctan 2u = −t + C, and u(0) = 1/2 "
                     "gives C = 2 arctan 1 = π/2.",
                     r"\arctan 2u = \frac{\pi}{4} - \frac{t}{2}"),
                Step("So u = (1/2) tan(π/4 − t/2). The population is 1/2 at "
                     "t = π/2 and reaches zero when tan(π/4 − t/2) = −1, that "
                     "is at t = π.",
                     r"x = \frac{1}{2} + \frac{1}{2}\tan\left(\frac{\pi}{4} "
                     r"- \frac{t}{2}\right), \qquad x(\pi) = 0"),
            ),
            equation="y' = y - y**2 - 1/2",
            conditions="y(0) = 1",
            answer="y = 1/2 + tan(pi/4 - t/2)/2",
            answer_latex=r"y = \frac{1}{2} + \frac{1}{2}\tan\left(\frac{\pi}{4} "
                         r"- \frac{t}{2}\right)",
        ),
        Para(
            "Just past the fold, the collapse is slow at first, and that "
            "slowness is itself a signature of the bifurcation. For h a "
            "little above 1/4 the right-hand side −(x − 1/2)² − (h − 1/4) is "
            "small near x = 1/2, where the two equilibria used to be. The "
            "solution crawls through that region, held up by the *ghost* of "
            "the vanished equilibria, before it accelerates away. The same "
            "arctangent integral gives the time to pass from x = +∞ to "
            "x = −∞ exactly, and it grows without bound as h comes down to "
            "the fold."
        ),
        Display(r"T = \int_{-\infty}^{\infty} \frac{du}{u^{2} + (h - 1/4)} = "
                r"\frac{\pi}{\sqrt{h - 1/4}}", "4"),
        Para(
            "At h = 0.26 that is π/0.1 ≈ 31.4 time units, and an integration "
            "of equation 3 from x = 1 takes about 27.5 of them to reach "
            "zero, about 24 of those with x between 1/4 and 3/4, crawling "
            "past the place where the equilibria used to be. At h = 0.2525 the "
            "full passage time T doubles to about 62.8, and the integration "
            "from 1 to 0 takes about 58.8. The inverse square-root law is characteristic of every "
            "saddle-node, and it is one reason a collapse can surprise the "
            "people watching: for a long time after the fold the population "
            "looks almost steady."
        ),
    )),
    Section("Transcritical: an exchange of stability", (
        Para(
            "Some equilibria cannot disappear, because the model forces "
            "them to exist for every parameter value. Zero is always an "
            "equilibrium of a population model without immigration, or of "
            "an epidemic model with nobody infected. When such an "
            "equilibrium meets another one, the two cannot annihilate. "
            "Instead they pass through each other and swap stability."
        ),
        Display(r"x' = rx - x^{2}: \quad x^{*} = 0,\ r, \qquad "
                r"f_x(0) = r,\ f_x(r) = -r", "5"),
        Para(
            "For r < 0 the origin is stable (f_x = r < 0) and the other "
            "equilibrium, at the negative value r, is unstable. For r > 0 the "
            "origin is unstable and x = r, now positive, is stable. At r = 0 "
            "the two coincide with f_x = 0. In the bifurcation diagram two "
            "straight lines cross, and the stable half of each continues "
            "into the stable half of the other."
        ),
        Plot(
            "A transcritical crossing",
            "The equilibria of x' = rx − x² against r. The line x = 0 and "
            "the line x = r cross at the origin. Stability passes from one "
            "line to the other: left of the crossing the axis is stable and "
            "the diagonal unstable, right of it the other way round.",
            (Curve("-(t + 1)/2", "x = 0, stable", y="0*t"),
             Curve("(t + 1)/2", "x = 0, unstable", y="0*t"),
             Curve("(t + 1)/2", "x = r, stable", y="(t + 1)/2"),
             Curve("-(t + 1)/2", "x = r, unstable", y="-(t + 1)/2")),
            t=(-1.0, 1.0), xlabel="r", ylabel="equilibrium x",
            ylim=(-1.1, 1.1),
        ),
        Para(
            "The standard example is an epidemic threshold. In a disease "
            "with no lasting immunity, the infected fraction I of a "
            "population is infected at rate βI(1 − I), from contacts between "
            "the infected and the susceptible, and recovers at rate γI. "
            "Collecting terms gives the transcritical form."
        ),
        Display(r"I' = \beta I(1 - I) - \gamma I = (\beta - \gamma)I - "
                r"\beta I^{2}, \qquad I^{*} = 0,\ 1 - \frac{\gamma}{\beta}", "6"),
        Para(
            "The disease-free state I = 0 is stable while β < γ and unstable "
            "once β > γ, when the endemic state 1 − γ/β becomes positive and "
            "takes over its stability. The bifurcation is at β/γ = 1, and "
            "β/γ is the basic reproduction number R₀: an infection spreads "
            "exactly when one case produces more than one new case."
        ),
        Worked(
            "An epidemic above threshold",
            "Take β = 2 and γ = 1, so R₀ = 2, and suppose a tenth of the "
            "population is infected at t = 0. Solve equation 6 (writing y "
            "for I) and find the level the infection settles at.",
            (
                Step("The equation is y' = y − 2y², with equilibria 0 "
                     "(unstable, since f'(0) = 1) and 1/2 (stable, since "
                     "f'(1/2) = −1).",
                     r"y' = y - 2y^{2}, \qquad y^{*} = 0,\ \frac{1}{2}"),
                Step("It is logistic, and also Bernoulli: with u = 1/y, "
                     "u' = −y'/y² = −1/y + 2, so u' = −u + 2, a linear "
                     "equation. Its solution with u(0) = 10 is "
                     "u = 2 + 8e^(−t).",
                     r"u = \frac{1}{y}, \qquad u' + u = 2, \qquad "
                     r"u = 2 + 8e^{-t}"),
                Step("So y = 1/(2 + 8e^(−t)), which rises from 1/10 to the "
                     "endemic level 1/2 = 1 − γ/β.",
                     r"y = \frac{1}{2 + 8e^{-t}} \;\longrightarrow\; \frac{1}{2}"),
            ),
            equation="y' = y - 2*y**2",
            conditions="y(0) = 1/10",
            answer="y = 1/(2 + 8*exp(-t))",
            answer_latex=r"y = \frac{1}{2 + 8e^{-t}}",
        ),
        Worked(
            "Below threshold",
            "Solve the normal form at r = −1, y' = −y − y², from y(0) = 1, "
            "and from y(0) = −2.",
            (
                Step("With u = 1/y, u' = −y'/y² = 1/y + 1 = u + 1, so "
                     "u = −1 + (u(0) + 1)e^t.",
                     r"u' - u = 1, \qquad u = -1 + (u_0 + 1)e^{t}"),
                Step("From y(0) = 1, u(0) = 1 and u = 2e^t − 1, so the "
                     "solution decays to the stable origin.",
                     r"y = \frac{1}{2e^{t} - 1} \;\longrightarrow\; 0"),
                Step("From y(0) = −2, below the unstable equilibrium −1, "
                     "u(0) = −1/2 and u = −1 + e^t/2, which reaches zero at "
                     "t = ln 2. There y runs off to −∞ in finite time, as the "
                     "solutions of y' = −y² do from a negative start. In the "
                     "population reading negative values are not physical, "
                     "and what matters is that the origin is stable."),
            ),
            equation="y' = -y - y**2",
            conditions="y(0) = 1",
            answer="y = 1/(2*exp(t) - 1)",
            answer_latex=r"y = \frac{1}{2e^{t} - 1}",
        ),
    )),
    Section("Pitchfork: symmetry, and a choice", (
        Para(
            "When the equation is symmetric, unchanged by x → −x, equilibria "
            "come in mirror pairs, and the origin is an equilibrium for every "
            "r. A saddle-node is then impossible at the origin, and what "
            "happens instead is that one equilibrium becomes three. Unit 2 "
            "introduced this pitchfork, y' = ry − y³, with a beam buckling "
            "under load; here its stability is worked out."
        ),
        Display(r"x' = rx - x^{3}: \quad x^{*} = 0,\ \pm\sqrt{r}\ (r > 0), "
                r"\qquad f_x(\pm\sqrt{r}) = r - 3r = -2r", "7"),
        Para(
            "For r ≤ 0 the origin is the only equilibrium, and it is stable. "
            "For r > 0 it is unstable, since f_x(0) = r, and two new stable "
            "equilibria ±√r have branched off it, one on each side. The "
            "diagram looks like a pitchfork lying on its side: a handle "
            "along the negative r-axis and three tines to the right, the "
            "middle one unstable."
        ),
        Plot(
            "A supercritical pitchfork",
            "The equilibria of x' = rx − x³ against r. The origin is stable "
            "to the left of r = 0 and unstable to the right, where the two "
            "stable branches ±√r have appeared. The branches leave the axis "
            "vertically: at r = 0.01 they are already at ±0.1.",
            (Curve("-(t + 1)/2", "x = 0, stable", y="0*t"),
             Curve("(t + 1)/2", "x = 0, unstable", y="0*t"),
             Curve("t**2", "x = ±√r, stable", y="t")),
            t=(-1.0, 1.0), xlabel="r", ylabel="equilibrium x",
            ylim=(-1.1, 1.1),
        ),
        Worked(
            "After the pitchfork: choosing a side",
            "Solve y' = y − y³, the normal form at r = 1, from y(0) = 1/2.",
            (
                Step("The equilibria are 0 (unstable) and ±1 (stable, with "
                     "f' = 1 − 3 = −2 there). A start at 1/2 lies between 0 "
                     "and 1, where y − y³ > 0, so it rises to 1.",
                     r"f(y) = y - y^{3}, \qquad f'(\pm 1) = -2"),
                Step("The equation is Bernoulli. With u = y^(−2), "
                     "u' = −2y^(−3)y' = −2u + 2, whose solution with u(0) = 4 "
                     "is u = 1 + 3e^(−2t).",
                     r"u = y^{-2}, \qquad u' = -2u + 2, \qquad "
                     r"u = 1 + 3e^{-2t}"),
                Step("So y = 1/√(1 + 3e^(−2t)) = e^t/√(e^(2t) + 3). It is "
                     "about 0.843 at t = 1 and 0.974 at t = 2, and tends to "
                     "1 = √r.",
                     r"y = \frac{e^{t}}{\sqrt{e^{2t} + 3}} \;\longrightarrow\; 1"),
                Step("A start at −1/2 gives the mirror image and goes to −1. "
                     "The equation keeps its symmetry through the pair of "
                     "branches, but each solution picks a side, and the side "
                     "is decided by the sign of the start. (The same equation, "
                     "read as r' = r(1 − r²), is the radial equation the "
                     "limit-cycles chapter solved; the Hopf section below "
                     "returns to it.)"),
            ),
            equation="y' = y - y**3",
            conditions="y(0) = 1/2",
            answer="y = exp(t)/sqrt(exp(2*t) + 3)",
            answer_latex=r"y = \frac{e^{t}}{\sqrt{e^{2t} + 3}}",
        ),
        Para(
            "That choice is the physical content of a pitchfork. Unit 2's "
            "beam, loaded along its length, stays straight until the load "
            "passes a critical value and then buckles, left or right. A "
            "magnet cooled "
            "below its critical temperature aligns up or down. The equation "
            "is symmetric, the outcome is not, and which way it goes is "
            "decided by a perturbation too small for the equation to "
            "contain. The Duffing oscillator of the almost-linear chapter, "
            "x'' + x' − x + x³ = 0, shows the same thing in mechanical form. "
            "Leave out its damping and replace the coefficient 1 of x by r: "
            "the equation x'' = rx − x³ has potential energy "
            "V = −rx²/2 + x⁴/4, which has "
            "one well for r < 0 and two for r > 0, with a hump at the origin "
            "between them."
        ),
        Plot(
            "The Duffing wells appearing",
            "The potential V(x) = −rx²/2 + x⁴/4 of x'' = rx − x³ for three "
            "values of r. At r = −1 there is one well; at r = 0 it has become "
            "flat-bottomed, since V is x⁴/4; at r = 1 the bottom has risen "
            "into a hump and two wells of depth 1/4 sit at x = ±1. The "
            "equilibria of the first-order equation 7 are the critical "
            "points of this potential.",
            (Curve("t**2/2 + t**4/4", "r = −1"),
             Curve("t**4/4", "r = 0"),
             Curve("-t**2/2 + t**4/4", "r = 1")),
            t=(-1.8, 1.8), xlabel="x", ylabel="V(x)", ylim=(-0.4, 1.4),
        ),
        Para(
            "For r < 0 the origin attracts with linear rate |r|: the "
            "linearisation is x' = rx, so a small disturbance decays like "
            "e^(rt) and takes a time of about ln 10/|r| to shrink tenfold. "
            "As r rises towards the bifurcation that time grows without "
            "bound, and exactly at r = 0 there is no linear restoring term "
            "at all; the decay that remains is only algebraic. The "
            "limit-cycles chapter solved this case as the radial equation "
            "r' = −r³: its solution 1/√(1 + 2t) takes 49.5 time units to "
            "fall from 1 to 0.1, where e^(−t) takes 2.3. Close "
            "to any bifurcation, the eigenvalue that is about to cross zero "
            "is small, so the equilibrium attracts slowly: the approach of a "
            "bifurcation can be detected before it arrives, as a system that "
            "takes longer and longer to recover from a disturbance. This is "
            "called *critical slowing down*."
        ),
        Worked(
            "Critical slowing down before a pitchfork",
            "In y' = ry − y³, disturb the stable origin to y(0) = 0.1 and find "
            "the time to recover to 0.01, at r = −0.1 and at r = −0.01.",
            (
                Step("The linearisation y' = ry gives y = 0.1e^(rt), which "
                     "reaches 0.01 when e^(rt) = 1/10, at t = ln 10/|r|: about "
                     "23.0 at r = −0.1 and 230 at r = −0.01. Ten times closer "
                     "to the bifurcation, ten times slower.",
                     r"t \approx \frac{\ln 10}{|r|}"),
                Step("The full equation is Bernoulli. With u = y^(−2), "
                     "u' = −2y^(−3)y' = −2r·u + 2. At r = −0.1 this is "
                     "u' = u/5 + 2, and u(0) = 100 gives u = 110e^(t/5) − 10.",
                     r"u = \frac{1}{y^{2}}, \qquad u' = \frac{u}{5} + 2, "
                     r"\qquad u = 110e^{t/5} - 10"),
                Step("So y = 1/√(110e^(t/5) − 10). It reaches 0.01 when "
                     "u = 10 000, that is when e^(t/5) = 91, at t = 5 ln 91 ≈ "
                     "22.6: the cubic term, which also pulls towards the "
                     "origin, shaves a little off the linear estimate.",
                     r"y = \frac{1}{\sqrt{110e^{t/5} - 10}}, \qquad "
                     r"t = 5\ln 91 \approx 22.6"),
                Step("At r = −0.01 the same steps give u' = u/50 + 2, "
                     "u = 200e^(t/50) − 100, and recovery at e^(t/50) = 50.5, "
                     "t = 50 ln 50.5 ≈ 196. Here the cubic matters more, "
                     "because y² = 0.01 at the start is as large as |r|, but "
                     "the recovery still takes almost nine times as long. At "
                     "r = 0 itself, 1/y² = 100 + 2t and it takes 4950.",
                     r"r = -0.01: \quad t = 50\ln 50.5 \approx 196"),
            ),
            equation="y' = -y/10 - y**3",
            conditions="y(0) = 1/10",
            answer="y = 1/sqrt(110*exp(t/5) - 10)",
            answer_latex=r"y = \frac{1}{\sqrt{110e^{t/5} - 10}}",
        ),
        Plot(
            "Recovery slows as the bifurcation nears",
            "Solutions of y' = ry − y³ from y(0) = 0.1 at r = −0.1, −0.01 and "
            "0, from the Bernoulli solutions 1/√(110e^(t/5) − 10), "
            "1/√(200e^(t/50) − 100) and 1/√(100 + 2t). Each is attracted to "
            "the origin, but the closer r is to the pitchfork at 0, the "
            "slower the return.",
            (Curve("1/sqrt(110*exp(t/5) - 10)", "r = −0.1"),
             Curve("1/sqrt(200*exp(t/50) - 100)", "r = −0.01"),
             Curve("1/sqrt(100 + 2*t)", "r = 0")),
            t=(0.0, 100.0), xlabel="t", ylabel="y", ylim=(0.0, 0.105),
        ),
    )),
    Section("When the branches bend back: subcritical bifurcations", (
        Para(
            "Change the sign of the cubic in equation 7 and the pitchfork "
            "turns round. In x' = rx + x³ the branches ±√(−r) exist for "
            "r < 0, and there f_x = r + 3x² = −2r > 0, so they are unstable. "
            "They surround the stable origin like walls. As r rises to 0 the "
            "walls close in, and for r > 0 the origin is unstable with "
            "nothing nearby to go to: every solution off the origin runs "
            "away. This is a *subcritical* pitchfork, and the one in "
            "equation 7 is *supercritical*."
        ),
        Para(
            "In a real system something further out usually stops the runaway, "
            "and the fifth-order model x' = rx + x³ − x⁵ shows what. Its "
            "nonzero equilibria satisfy x² = (1 ± √(1 + 4r))/2. For "
            "−1/4 < r < 0 there are five: the stable origin, the unstable "
            "pair with the minus sign, and a stable pair far out with the "
            "plus sign. At r = −0.1, for example, they are 0, ±0.336 and "
            "±0.942. For r > 0 only the origin (now unstable) and the outer "
            "pair remain, near ±1."
        ),
        Box(
            "warning", "Subcritical means a jump, and hysteresis",
            "Raise r slowly through 0 in x' = rx + x³ − x⁵ and the state, "
            "which sat at the origin, jumps to an outer branch near ±1. "
            "Lower r again and it does not jump back at 0: it stays on the "
            "outer branch until that branch meets the unstable one in a "
            "saddle-node at r = −1/4, x = ±1/√2 ≈ ±0.707, and only then "
            "falls to the origin. The state depends on the history of the "
            "parameter, not only on its current value.",
            r"x' = rx + x^{3} - x^{5}: \quad x^{2} = "
            r"\frac{1 \pm \sqrt{1 + 4r}}{2}",
        ),
        Plot(
            "A subcritical pitchfork with hysteresis",
            "The equilibria of x' = rx + x³ − x⁵ against r, drawn from "
            "r = x⁴ − x², which is what the nonzero equilibria satisfy. The "
            "origin is stable left of r = 0 and unstable right of it. The "
            "inner branches, unstable, run from the origin at r = 0 back to "
            "the folds at r = −1/4, x = ±1/√2, where they meet the stable "
            "outer branches. Raising r, the state jumps from the origin to an "
            "outer branch at r = 0; lowering it, the state rides the outer "
            "branch back to r = −1/4 and only then falls to the origin. The "
            "loop between −1/4 and 0 is the hysteresis.",
            (Curve("-0.3*t", "origin, stable", y="0*t"),
             Curve("0.3*t", "origin, unstable", y="0*t"),
             Curve("t**4/4 - t**2/2", "inner, unstable", y="t/sqrt(2)"),
             Curve("t**4/4 - t**2/2", "", y="-t/sqrt(2)"),
             Curve("(0.7071 + 0.41*t)**4 - (0.7071 + 0.41*t)**2",
                   "outer, stable", y="0.7071 + 0.41*t"),
             Curve("(0.7071 + 0.41*t)**4 - (0.7071 + 0.41*t)**2", "",
                   y="-(0.7071 + 0.41*t)")),
            t=(0.0, 1.0), xlabel="r", ylabel="equilibrium x",
            ylim=(-1.2, 1.2),
        ),
        Para(
            "Supercritical bifurcations are gentle: the new state grows "
            "continuously out of the old one, like √r. Subcritical ones are "
            "abrupt and are not reversed by undoing the change that caused "
            "them. The harvested fishery is a saddle-node, and it shares "
            "this feature in its own way: once the population has collapsed, "
            "cutting the harvest back below 1/4 does not bring it back, "
            "because a population of zero has no growth to recover with."
        ),
    )),
    Section("Reading a bifurcation diagram", (
        Para(
            "The harvesting, transcritical, pitchfork and subcritical "
            "sections each drew a bifurcation diagram: every "
            "equilibrium plotted against the parameter, with its stability "
            "marked. It is read in two directions. Read vertically, at a "
            "fixed r, it is the phase line of that one equation: the "
            "equilibria are the points on the vertical line, and between "
            "consecutive ones the flow runs towards the stable one. Read "
            "horizontally, along a branch, it follows one equilibrium as the "
            "parameter changes. The bifurcations are the points where "
            "branches meet, end, or change stability."
        ),
        Para(
            "Three shapes cover the one-dimensional cases. A branch that "
            "turns back on itself, a fold, is a saddle-node: stable meets "
            "unstable and both end. Two branches that cross and trade "
            "stability are a transcritical bifurcation. A branch that splits "
            "into three is a pitchfork, supercritical if the new branches "
            "are stable and lie on the side where the old branch lost "
            "stability, subcritical if they are unstable and lie on the "
            "other side."
        ),
        Figure("normal_forms",
               "The figure opens on the pitchfork, form 2, at r = 0.4, with "
               "three equilibria in the readout: two stable ones near ±0.632 "
               "and the unstable origin. On the left is the graph of f(x) at "
               "the current r, with its equilibria marked; on the right is "
               "the bifurcation diagram for r from −1 to 1, with a dashed "
               "line at the current r. Drag r down through zero and watch the "
               "two outer equilibria slide in and merge with the origin, "
               "which the readout calls stable at r = 0. Now set the form "
               "slider to 0, the saddle-node x' = r + x². At r = −1 the "
               "readout shows −1 stable and +1 unstable; move r up and they "
               "approach, meet at r = 0 as a single equilibrium the readout "
               "labels neutral, which is the semi-stable point of the "
               "saddle-node section, attracting from below and repelling "
               "above; for r above zero the readout says none. "
               "Finally set the form to 1, the transcritical x' = rx − x², "
               "and move r from −0.5 to +0.5: the equilibria are −0.5 "
               "(unstable) and 0 (stable) at the start and 0 (unstable) and "
               "0.5 (stable) at the end. In each case read the left pane as "
               "one vertical slice of the right one."),
    )),
    Section("Hopf: an oscillation switches on", (
        Para(
            "In the plane there is a second way to lose stability. A stable "
            "spiral has a complex pair of eigenvalues α ± iβ with α < 0. If "
            "a parameter pushes α up through zero while β stays nonzero, the "
            "spiral becomes unstable, but no equilibrium is created or "
            "destroyed, and the determinant α² + β² stays positive the whole "
            "time. In the trace–determinant plane the point crosses the "
            "positive Δ-axis, the line of centres. What is created is a "
            "periodic orbit."
        ),
        Para(
            "The limit-cycles chapter has already met the model example, "
            "the normal form of the Hopf bifurcation. In polar coordinates "
            "it reads"
        ),
        Display(r"r' = r(\mu - r^{2}), \qquad \theta' = 1", "8"),
        Display(r"x' = \mu x - y - x(x^{2} + y^{2}), \qquad "
                r"y' = x + \mu y - y(x^{2} + y^{2})", "9"),
        Para(
            "In equation 8, and from here to the end of this section, r is "
            "the distance from the origin, not a parameter; the parameter is "
            "μ. The Jacobian of equation 9 at the origin has rows (μ, −1) and "
            "(1, μ), so its trace is 2μ, its determinant μ² + 1, and its "
            "eigenvalues are μ ± i. For μ < 0 the origin is a stable spiral "
            "and the radial equation r' = r(μ − r²) is negative for every "
            "r > 0: everything spirals in. For μ > 0 the origin is an "
            "unstable spiral, but the radial equation now has a second "
            "equilibrium r = √μ, stable, which in the plane is a circle every "
            "other trajectory approaches: a stable limit cycle of radius √μ, "
            "travelled once every 2π time units. The radial equation itself "
            "has a pitchfork at μ = 0; in the plane the pitchfork of the "
            "radius is a cycle being born."
        ),
        Box(
            "theorem", "The Hopf bifurcation theorem",
            "Let a planar system depend smoothly on μ, and let its "
            "equilibrium have eigenvalues α(μ) ± iβ(μ) with α(μ₀) = 0, "
            "β(μ₀) = ω ≠ 0 and α′(μ₀) ≠ 0, so that the pair crosses the "
            "imaginary axis with nonzero speed (since the trace is 2α, this "
            "says d(tr J)/dμ ≠ 0). Then, provided a certain combination ℓ₁ "
            "of the second and third derivatives of the system at the "
            "equilibrium, the cubic coefficient, is not zero, a unique "
            "family of periodic orbits "
            "branches from the equilibrium on one side of μ₀. Their size "
            "grows like √|μ − μ₀| and their period tends to 2π/ω. If the "
            "orbits are stable and exist where the equilibrium is unstable, "
            "the bifurcation is supercritical; if they are unstable and exist "
            "where the equilibrium is stable, it is subcritical.",
            r"\mathrm{tr}\,J = 0,\ \det J = \omega^{2} > 0,\ "
            r"\frac{d\,\mathrm{tr}\,J}{d\mu} \neq 0,\ \ell_{1} \neq 0 \;"
            r"\Longrightarrow\; \text{cycle size} \propto "
            r"\sqrt{|\mu - \mu_{0}|}",
        ),
        Para(
            "The proof is long and is not given here. Its idea is that, near "
            "the bifurcation, a change of variables brings any such system "
            "to equation 8 plus terms too small to matter, with the cubic "
            "coefficient either −1 (supercritical) or +1 (subcritical). The "
            "extra condition in the theorem, ℓ₁ ≠ 0, says that coefficient is "
            "not zero."
        ),
        Para(
            "The limit-cycles chapter solved the radial equation at μ = 1, "
            "from r(0) = 1/2, and found r = 1/√(1 + 3e^(−2t)). Read now as "
            "one member of a family, that cycle has a lesson in it: nearer "
            "the bifurcation the cycle is smaller, and it is also slower to "
            "reach. Substituting r = √μ·R and s = μt turns r' = r(μ − r²) "
            "into dR/ds = R(1 − R²), so every member of the family is the "
            "μ = 1 solution shrunk by √μ in size and stretched by 1/μ in "
            "time."
        ),
        Worked(
            "A small cycle, slowly reached",
            "Solve equation 9 at μ = 1/4 from (1/4, 0), and compare how fast "
            "it reaches its cycle with the μ = 1 case.",
            (
                Step("In polar form θ' = 1 with θ(0) = 0 gives θ = t, and the "
                     "radius obeys r' = r(1/4 − r²) with r(0) = 1/4. With "
                     "u = 1/r², u' = −2r'/r³ = −u/2 + 2, and u(0) = 16 gives "
                     "u = 4 + 12e^(−t/2).",
                     r"u = \frac{1}{r^{2}}, \qquad u' = 2 - \frac{u}{2}, "
                     r"\qquad u = 4 + 12e^{-t/2}"),
                Step("So r = 1/(2√(1 + 3e^(−t/2))), which tends to 1/2 = √μ. "
                     "Return to Cartesian coordinates with x = r cos θ and "
                     "y = r sin θ.",
                     r"x = \frac{\cos t}{2\sqrt{1 + 3e^{-t/2}}}, \qquad "
                     r"y = \frac{\sin t}{2\sqrt{1 + 3e^{-t/2}}}"),
                Step("This is the μ = 1 solution with its radius halved and "
                     "its time stretched fourfold, as the scaling said. The "
                     "radius is about 0.345 at t = 2, 0.422 at t = 4 and "
                     "0.487 at t = 8, and reaches 99% of its final value at "
                     "t ≈ 10.0, where the μ = 1 solution needed only t ≈ 2.5. "
                     "The cycle's pull is its radial eigenvalue −2μ, so a "
                     "cycle born in a Hopf bifurcation is weakly attracting "
                     "while it is small: critical slowing down again."),
            ),
            equation="x' = x/4 - y - x*(x**2 + y**2); "
                     "y' = x + y/4 - y*(x**2 + y**2)",
            conditions="x(0) = 1/4, y(0) = 0",
            answer="x = cos(t)/(2*sqrt(1 + 3*exp(-t/2)))\n"
                   "y = sin(t)/(2*sqrt(1 + 3*exp(-t/2)))",
            answer_latex=r"x = \frac{\cos t}{2\sqrt{1 + 3e^{-t/2}}}, \qquad "
                         r"y = \frac{\sin t}{2\sqrt{1 + 3e^{-t/2}}}",
        ),
        Plot(
            "A small cycle approached from both sides",
            "Two trajectories of equation 9 at μ = 1/4: one from (1/4, 0), "
            "spiralling out, and one from (1, 0), spiralling in, whose "
            "radius is 1/√(4 − 3e^(−t/2)). Both turn anticlockwise once "
            "every 2π and both end on the circle of radius √μ = 1/2, taking "
            "several turns to get there. The axes are drawn to different "
            "scales, so the circle may look like an ellipse.",
            (Curve("cos(t)/(2*sqrt(1 + 3*exp(-t/2)))", "from inside",
                   y="sin(t)/(2*sqrt(1 + 3*exp(-t/2)))"),
             Curve("cos(t)/sqrt(4 - 3*exp(-t/2))", "from outside",
                   y="sin(t)/sqrt(4 - 3*exp(-t/2))"),
             Curve("cos(t)/2", "r = 1/2", y="sin(t)/2")),
            t=(0.0, 25.0), xlabel="x", ylabel="y", ylim=(-1.1, 1.1),
        ),
        Box(
            "warning", "A subcritical Hopf gives no warning cycle",
            "In r' = r(μ + r²) the cycle r = √(−μ) exists for μ < 0 and is "
            "unstable: it surrounds the stable origin as the boundary of its "
            "basin. As μ rises to 0 the cycle shrinks onto the origin, and "
            "for μ > 0 there is no small cycle at all. A trajectory that "
            "leaves the origin then goes wherever the rest of the system "
            "sends it, often far away. Seeing a Jacobian's trace pass "
            "through zero says there is a Hopf bifurcation; it does not say "
            "which kind.",
        ),
    )),
    Section("Finding a Hopf bifurcation from the Jacobian", (
        Para(
            "In practice the recipe is the one the definition suggests. Find "
            "the equilibrium as a function of the parameter, write down the "
            "Jacobian there, and look for the parameter value at which the "
            "trace is zero while the determinant is positive. Then check the "
            "trace really changes sign there, and find out by computation or "
            "experiment which side the cycle is on."
        ),
        Worked(
            "A Hopf bifurcation, and the size of its cycle",
            "The Rayleigh oscillator x' = y, y' = −x + μy − y³ has one "
            "equilibrium, the origin. Find where it bifurcates, and estimate "
            "the size of the cycle for small μ > 0.",
            (
                Step("The Jacobian at the origin has rows (0, 1) and (−1, μ), "
                     "so the trace is μ and the determinant 1. The "
                     "eigenvalues are μ/2 ± i√(1 − μ²/4): a complex pair whose "
                     "real part changes sign at μ = 0, with the determinant "
                     "positive. That is a Hopf bifurcation, with frequency "
                     "√Δ = 1.",
                     r"\tau = \mu, \quad \Delta = 1, \quad \lambda = "
                     r"\frac{\mu}{2} \pm i\sqrt{1 - \frac{\mu^{2}}{4}}"),
                Step("For the size, use the energy balance of Van der Pol's "
                     "oscillator in the limit-cycles chapter. With E = (x² + y²)/2, the rate "
                     "of change along "
                     "a solution is xy + y(−x + μy − y³) = μy² − y⁴. Small "
                     "velocities feed energy in, large ones take it out.",
                     r"E' = \mu y^{2} - y^{4}"),
                Step("For small μ the motion is nearly the harmonic x = A cos t, "
                     "y = −A sin t, and the energy barely changes in one "
                     "turn. A closed orbit needs no net gain over a turn. The "
                     "averages of sin² and sin⁴ over a period are 1/2 and "
                     "3/8, so the balance is μA²/2 = 3A⁴/8.",
                     r"\frac{\mu A^{2}}{2} = \frac{3A^{4}}{8} \;"
                     r"\Longrightarrow\; A = 2\sqrt{\frac{\mu}{3}}"),
                Step("Checked numerically with the app's limit-cycle finder: "
                     "at μ = 0.05, 0.1 and 0.2 the predicted amplitudes are "
                     "0.258, 0.365 and 0.516, and the computed cycles reach "
                     "y = 0.258, 0.365 and 0.516, with periods 6.284, 6.287 "
                     "and 6.299 against 2π ≈ 6.283. (Type the system into the "
                     "Solver Lab and take it to the Phase Portrait to see the "
                     "cycle and its period.) The cycle exists for μ > 0, "
                     "where the origin is unstable, and attracts its "
                     "neighbours: a supercritical Hopf, with the √μ growth "
                     "the theorem promises. At μ = −0.1 the finder instead "
                     "reports a spiral shrinking by a factor 0.73 per turn, "
                     "which is e^(−0.05·2π)."),
            ),
        ),
        Para(
            "That √μ law may seem to clash with the limit-cycles chapter, "
            "where Van der Pol's cycle had amplitude about 2 for every μ > 0 "
            "and did not shrink as μ came down to zero, although the trace "
            "of its Jacobian at the origin is μ too. The two oscillators are "
            "in fact the same. Differentiate Rayleigh's second equation and "
            "use x' = y: it becomes y'' − (μ − 3y²)y' + y = 0. Put "
            "y = √(μ/3)·w and this is w'' − μ(1 − w²)w' + w = 0, Van der "
            "Pol's equation. So Rayleigh's cycle is Van der Pol's amplitude-2 "
            "cycle scaled by √(μ/3), which is exactly the A = 2√(μ/3) found "
            "above. In Van der Pol's own variables the cycle does not "
            "shrink, because there the nonlinear damping is multiplied by μ "
            "and vanishes with it: at μ = 0 the system is the linear "
            "oscillator, whose cubic coefficient ℓ₁ is zero, and the "
            "theorem's extra condition fails. The theorem describes a family "
            "in which the nonlinearity stays put while the linear part "
            "crosses; Rayleigh's family is one, Van der Pol's is not."
        ),
    )),
    Section("A chemical clock: the Brusselator", (
        Para(
            "The Brusselator is a model of an autocatalytic reaction, one in "
            "which a product speeds up its own production. Two concentrations "
            "x and y are fed and consumed at rates set by positive constants "
            "a and b."
        ),
        Display(r"x' = a - (b + 1)x + x^{2}y, \qquad y' = bx - x^{2}y", "10"),
        Para(
            "Its equilibrium is easy to find. The second equation is "
            "x(b − xy) = 0, and x = 0 is impossible because the first "
            "equation would then read a = 0; so xy = b, the first equation "
            "becomes a − x = 0, and the only equilibrium is (a, b/a). At that "
            "point x² = a² and 2xy = 2b, so the Jacobian has rows (b − 1, a²) "
            "and (−b, −a²)."
        ),
        Display(r"\mathrm{tr}\,J = b - 1 - a^{2}, \qquad \det J = a^{2} > 0", "11"),
        Para(
            "The determinant never changes sign, so there is no saddle-node "
            "or pitchfork here. The trace is negative for b < 1 + a² and "
            "positive for b > 1 + a², and it passes through zero with the "
            "determinant positive. So at b = 1 + a² a complex pair crosses "
            "the imaginary axis at ±ia, and a chemical oscillation switches "
            "on with angular frequency near a. The discriminant "
            "τ² − 4Δ = (b − 1 − a²)² − 4a² vanishes at b = (1 ± a)², so the "
            "equilibrium is a spiral for (1 − a)² < b < (1 + a)², a band "
            "which always contains the Hopf value."
        ),
        Worked(
            "Where the Brusselator starts to oscillate",
            "Take a = 1. Find the Hopf value of b, the eigenvalues there and "
            "at b = 3, and describe the cycle just past onset.",
            (
                Step("With a = 1 the equilibrium is (1, b) and the Jacobian has "
                     "rows (b − 1, 1) and (−b, −1): trace b − 2, determinant 1. "
                     "The trace vanishes at b = 2 = 1 + a².",
                     r"\tau = b - 2, \qquad \Delta = 1, \qquad b_{H} = 2"),
                Step("At b = 2 the characteristic polynomial is λ² + 1, so "
                     "λ = ±i, and a small oscillation should have period near "
                     "2π ≈ 6.28. At b = 1.9 the eigenvalues are about "
                     "−0.05 ± 0.999i, a stable spiral, and at b = 3 they are "
                     "1/2 ± (√3/2)i, an unstable one.",
                     r"b = 3: \quad \lambda^{2} - \lambda + 1 = 0, \quad "
                     r"\lambda = \frac{1}{2} \pm \frac{\sqrt{3}}{2}\,i"),
                Step("The app's limit-cycle finder, run past onset, finds an "
                     "attracting cycle at b = 2.05, 2.1 and 2.2 with widths "
                     "(the widest separation of two points on the loop) of "
                     "about 0.848, 1.216 and 1.771, and periods 6.30, 6.32 and "
                     "6.37. Divided by √(b − 2) the widths give 3.79, 3.85 and "
                     "3.96, nearly constant: the square-root growth of a "
                     "supercritical Hopf, with the period starting at 2π."),
                Step("Further out the cycle stops being small. At b = 3 its "
                     "period is about 7.16, and x swings between about 0.37 "
                     "and 3.75 around the equilibrium value 1. Just past onset "
                     "the approach is slow as well: at b = 2.02, from the "
                     "catalogue's start (1.5, 3), the finder still sees a loop "
                     "changing size by a factor of about 0.997 per turn, and "
                     "declines to call it a cycle yet: critical slowing down "
                     "in its oscillatory form."),
            ),
        ),
        Para(
            "The lesson's Phase Portrait tool opens on the Brusselator with "
            "a = 1 and b = 3, and its limit-cycle layer draws the cycle and "
            "reports its period. Drag b below 2 and the trajectory spirals "
            "into the equilibrium instead. Its bifurcation-diagram panel "
            "does the whole computation of this section: choose b, draw the "
            "diagram, and it follows the equilibrium across the range, drawn "
            "solid where stable and dashed where not, and marks a Hopf "
            "bifurcation at b = 2 where a conjugate pair crosses the "
            "imaginary axis."
        ),
    )),
    Section("Period doubling: one road to chaos", (
        Para(
            "A Hopf bifurcation turns an equilibrium into a cycle. A cycle "
            "can bifurcate in its turn, and in three or more dimensions one "
            "common way is for it to *double*: the loop that closed after one "
            "turn now closes only after two, then after four, and so on. "
            "The standard way to watch a cycle is to mark where a trajectory "
            "crosses a fixed surface each time round, which turns the flow "
            "into a map, x_(n+1) = P(x_n), from one crossing to the next. A "
            "cycle is then a fixed point of the map, and a doubled cycle is "
            "a pair of points the map swaps. So the simplest place to see "
            "period doubling is a map, and the simplest map with the "
            "phenomenon is the logistic map, a population model for species "
            "whose generations do not overlap."
        ),
        Display(r"x_{n+1} = r\,x_{n}(1 - x_{n}), \qquad 0 < r \leq 4", "12"),
        Para(
            "Its fixed points solve x = rx(1 − x): x = 0 and x* = 1 − 1/r. "
            "Their stability works like the phase line of Unit 2, with one "
            "difference. A small deviation from a fixed point is multiplied "
            "by the slope f'(x*) at every step, so the fixed point is stable "
            "when |f'(x*)| < 1 and unstable when |f'(x*)| > 1. Here "
            "f'(x) = r(1 − 2x), which at x* is 2 − r. So x* is stable for "
            "1 < r < 3. For r between 2 and 3 the slope is negative, and the "
            "iterates approach x* from alternate sides: at r = 2.8, from "
            "x₀ = 0.2, they run 0.448, 0.692, 0.596, 0.674, 0.615, 0.663, "
            "closing in on 1 − 1/2.8 ≈ 0.643. At r = 3 the slope reaches −1. "
            "A differential equation has no counterpart to this: an "
            "eigenvalue of a flow can only reach zero or the imaginary axis, "
            "but a multiplier of a map can reach −1, and when it does the "
            "alternation stops decaying."
        ),
        Worked(
            "The first period doubling",
            "Find the 2-cycle of the logistic map, where it is stable, and "
            "its points at r = 3.2.",
            (
                Step("A 2-cycle is a pair p, q with f(p) = q and f(q) = p, so "
                     "both satisfy f(f(x)) = x. That quartic contains the "
                     "fixed points 0 and 1 − 1/r; dividing them out leaves a "
                     "quadratic.",
                     r"r^{2}x^{2} - r(r + 1)x + (r + 1) = 0"),
                Step("Its roots are real exactly when (r − 3)(r + 1) ≥ 0, that "
                     "is for r ≥ 3. So the 2-cycle is born at r = 3, from the "
                     "fixed point, at the moment its slope passes −1.",
                     r"x = \frac{r + 1 \pm \sqrt{(r - 3)(r + 1)}}{2r}"),
                Step("Two steps of the map multiply a deviation by "
                     "f'(p)f'(q) = r²(1 − 2p)(1 − 2q). Using p + q = (r + 1)/r "
                     "and pq = (r + 1)/r² from the quadratic, this is "
                     "4 + 2r − r². It is 1 at r = 3 and falls as r grows, "
                     "reaching −1 when r² − 2r − 5 = 0, at r = 1 + √6 ≈ "
                     "3.449. So the 2-cycle is stable for 3 < r < 1 + √6.",
                     r"f'(p)f'(q) = 4 + 2r - r^{2}, \qquad "
                     r"r_{2} = 1 + \sqrt{6} \approx 3.449"),
                Step("At r = 3.2 the cycle is 0.513 and 0.799, with "
                     "multiplier 0.16, strongly stable. From x₀ = 0.2 the "
                     "iterates are 0.512, 0.7995, 0.5129, 0.7995, 0.513, … "
                     "Meanwhile the fixed point 1 − 1/3.2 ≈ 0.688, with slope "
                     "−1.2, is still there but repels."),
            ),
        ),
        Para(
            "At r = 1 + √6 the 2-cycle's multiplier passes −1 in the same "
            "way, and a stable 4-cycle takes over. Then an 8-cycle, a "
            "16-cycle, and so on. Solving f^p(x) = x together with "
            "(f^p)'(x) = −1 numerically for p = 4, 8 and 16 gives the "
            "next onsets: r₃ ≈ 3.5441, r₄ ≈ 3.5644 and r₅ ≈ 3.5688. The "
            "gaps between them shrink, each about 4.7 times shorter than the "
            "one before, so the infinitely many doublings all fit below a "
            "finite limit, r∞ ≈ 3.5699. The ratios of successive gaps, 4.75, "
            "4.66, 4.668, 4.669, converge to a number Feigenbaum found in "
            "1975."
        ),
        Display(r"\delta = \lim_{n \to \infty} \frac{r_{n} - r_{n-1}}"
                r"{r_{n+1} - r_{n}} \approx 4.6692", "13"),
        Plot(
            "The start of the period-doubling cascade",
            "Fixed point and 2-cycle of the logistic map against r. The fixed "
            "point 1 − 1/r is stable up to r = 3; there it splits into the "
            "2-cycle (r + 1 ± √((r − 3)(r + 1)))/(2r), which is stable up to "
            "1 + √6 ≈ 3.449. The 4-cycle and later cycles have no formula "
            "and are not drawn; the markers show where the 8-cycle begins, "
            "r₃ ≈ 3.544, and where the doublings accumulate, r∞ ≈ 3.570.",
            (Curve("2.5 + 0.5*t", "fixed point, stable",
                   y="1 - 1/(2.5 + 0.5*t)"),
             Curve("3 + t", "fixed point, unstable", y="1 - 1/(3 + t)"),
             Curve("3 + (sqrt(6) - 2)*t", "2-cycle, stable",
                   y="(4 + (sqrt(6) - 2)*t + sqrt((sqrt(6) - 2)*t*(4 + (sqrt(6) - 2)*t)))"
                     "/(2*(3 + (sqrt(6) - 2)*t))"),
             Curve("3 + (sqrt(6) - 2)*t", "",
                   y="(4 + (sqrt(6) - 2)*t - sqrt((sqrt(6) - 2)*t*(4 + (sqrt(6) - 2)*t)))"
                     "/(2*(3 + (sqrt(6) - 2)*t))"),
             Curve("1 + sqrt(6) + (3 - sqrt(6))*t", "2-cycle, unstable",
                   y="(2 + sqrt(6) + (3 - sqrt(6))*t + sqrt((sqrt(6) - 2 + (3 - "
                     "sqrt(6))*t)*(2 + sqrt(6) + (3 - sqrt(6))*t)))"
                     "/(2*(1 + sqrt(6) + (3 - sqrt(6))*t))"),
             Curve("1 + sqrt(6) + (3 - sqrt(6))*t", "",
                   y="(2 + sqrt(6) + (3 - sqrt(6))*t - sqrt((sqrt(6) - 2 + (3 - "
                     "sqrt(6))*t)*(2 + sqrt(6) + (3 - sqrt(6))*t)))"
                     "/(2*(1 + sqrt(6) + (3 - sqrt(6))*t))"),
             Curve("3.5441 + 0*t", "r₃, 8-cycle begins", y="t"),
             Curve("3.5699 + 0*t", "r∞, doublings end", y="t")),
            t=(0.0, 1.0), xlabel="r", ylabel="x", ylim=(0.0, 1.0),
        ),
        Para(
            "Past r∞ the iterates, for most values of r, never settle into "
            "any cycle, and two starts a hair apart separate exponentially. "
            "For a map the growth rate is the average of ln|f'(x_n)| along "
            "the orbit: computed over 200 000 steps it is about +0.35 at "
            "r = 3.7 and +0.693 at r = 4, where it is known to be exactly "
            "ln 2, against −0.22 at r = 2.8 and −0.92 at r = 3.2, where the "
            "orbit is attracted to a fixed point or a cycle. Chaos is "
            "interrupted by windows of order; the widest begins at "
            "r = 1 + √8 ≈ 3.828, and at r = 3.83 the iterates settle on a "
            "3-cycle, about 0.156, 0.505 and 0.957."
        ),
        Para(
            "The striking fact is that δ is universal. Any family of maps "
            "with a single smooth hump, rounded like a parabola at the top, "
            "not only the logistic one, doubles "
            "its way to chaos with the same ratio 4.669…, and so do many "
            "flows, through their crossing maps. The forced Duffing oscillator "
            "x'' + cx' − x + x³ = F cos ωt, which becomes an autonomous "
            "system in three dimensions once θ = ωt is added as a third "
            "variable, and Rössler's three-variable system both reach chaos "
            "along such a cascade as a parameter is raised, and the same δ "
            "has been measured in experiments on convecting fluids. Lorenz's "
            "system, in the range of ρ studied next, takes a different road."
        ),
    )),
    Section("Beyond the plane: Lorenz and chaos", (
        Para(
            "The limit-cycles chapter proved, through the Poincaré–Bendixson "
            "theorem, that a bounded trajectory of an autonomous planar "
            "system approaches an equilibrium, a closed orbit, or a chain of "
            "equilibria joined by trajectories. Trajectories cannot cross, "
            "and in the plane a curve that cannot cross itself has no room "
            "to do anything else. In three dimensions a trajectory can pass "
            "over and under itself, and the list of possible long-term "
            "behaviours is no longer short. In 1963 Edward Lorenz, "
            "simplifying a model of convection in a layer of fluid heated "
            "from below, wrote down three equations."
        ),
        Display(r"x' = \sigma(y - x), \qquad y' = x(\rho - z) - y, \qquad "
                r"z' = xy - \beta z", "14"),
        Para(
            "The classic parameters are σ = 10 and β = 8/3, with ρ, which "
            "measures how strongly the layer is heated, as the bifurcation "
            "parameter. The origin, no convection, is always an equilibrium. "
            "The equations are unchanged by (x, y, z) → (−x, −y, z), so any "
            "equilibrium off the z-axis has a mirror image. The recipe of "
            "the Hopf section works in three dimensions too, with one more "
            "row in the Jacobian."
        ),
        Worked(
            "Lorenz's equilibria and where they lose stability",
            "Find the equilibria of equation 14, the value of ρ at which the "
            "origin bifurcates, and the value at which the other equilibria "
            "lose stability.",
            (
                Step("The partial derivatives give J row by row: (−σ, σ, 0) "
                     "from x', (ρ − z, −1, −x) from y', and (y, x, −β) from "
                     "z'. At the origin the rows are (−σ, σ, 0), (ρ, −1, 0) and "
                     "(0, 0, −β). The z-row and z-column hold only −β, so −β "
                     "is one eigenvalue, and the other two come from the "
                     "upper-left block, with trace −(σ + 1) and determinant "
                     "σ(1 − ρ).",
                     r"\lambda^{2} + (\sigma + 1)\lambda + \sigma(1 - \rho) = 0"),
                Step("The determinant σ(1 − ρ) passes through zero at ρ = 1: "
                     "a real eigenvalue crosses zero, and for ρ > 1 one "
                     "eigenvalue is positive and the origin is unstable. At "
                     "ρ = 28 the three eigenvalues are about 11.83, −22.83 "
                     "and −8/3 ≈ −2.67.",
                     r"\rho = 28: \quad \lambda \approx 11.83,\ -22.83,\ -2.67"),
                Step("For the other equilibria, x' = 0 gives y = x, then "
                     "y' = 0 gives x(ρ − 1 − z) = 0 and z' = 0 gives "
                     "x² = βz. Off the origin z = ρ − 1 and "
                     "x = ±√(β(ρ − 1)), real only for ρ > 1. So at ρ = 1 two "
                     "mirror-image equilibria C± leave the origin together: "
                     "the symmetry forces a pitchfork. They are steady "
                     "convection rolls turning one way or the other; at "
                     "ρ = 28, C₊ = (8.49, 8.49, 27).",
                     r"C_{\pm} = \left(\pm\sqrt{\beta(\rho - 1)},\ "
                     r"\pm\sqrt{\beta(\rho - 1)},\ \rho - 1\right)"),
                Step("At C± the Jacobian's characteristic polynomial, "
                     "expanded, is λ³ + a₂λ² + a₁λ + a₀ with a₂ = σ + β + 1, "
                     "a₁ = β(σ + ρ) and a₀ = 2σβ(ρ − 1).",
                     r"\lambda^{3} + (\sigma + \beta + 1)\lambda^{2} + "
                     r"\beta(\sigma + \rho)\lambda + 2\sigma\beta(\rho - 1)"),
                Step("A pair ±iω is a root when substituting λ = iω gives zero. "
                     "The imaginary part, ω(a₁ − ω²), gives ω² = a₁, and the "
                     "real part, a₀ − a₂ω², then gives a₀ = a₂a₁. For "
                     "Lorenz that is (σ + β + 1)β(σ + ρ) = 2σβ(ρ − 1), and "
                     "solving for ρ gives equation 15. With the classic values "
                     "ω² = 1760/19, so ω ≈ 9.62.",
                     r"a_{2}a_{1} = a_{0} \;\Longrightarrow\; "
                     r"\rho(\sigma - \beta - 1) = \sigma(\sigma + \beta + 3)"),
            ),
        ),
        Display(r"\rho_{H} = \frac{\sigma(\sigma + \beta + 3)}{\sigma - \beta - 1} "
                r"= \frac{470}{19} \approx 24.74", "15"),
        Para(
            "The numbers bear this out. At ρ = 24 the eigenvalues at C₊ are "
            "about −13.62 and −0.0225 ± 9.49i; at ρ = 25 they are about "
            "−13.68 and +0.0079 ± 9.67i. The rolls are stable below ρ_H and "
            "unstable above it. This Hopf bifurcation is subcritical, so no "
            "small stable cycle is born to take over. At ρ = 28, where C₊ "
            "has eigenvalues about −13.85 and 0.094 ± 10.19i and the origin "
            "is a saddle, every equilibrium is unstable and no stable cycle "
            "exists either. Trajectories stay bounded, circling one of C± "
            "and then the other in an irregular sequence that never repeats, "
            "on the butterfly-shaped set called the Lorenz attractor."
        ),
        Para(
            "Chaos does not wait for ρ_H, though. The unstable cycles that "
            "the subcritical Hopf absorbs at ρ_H were created much earlier, "
            "near ρ ≈ 13.93 by the standard computations, in a *global* "
            "bifurcation involving the origin's saddle, and the chaotic "
            "attractor itself appears at about ρ ≈ 24.06, while C± are still "
            "stable. Between those two values stable rolls and chaos "
            "coexist, and the start decides which one a trajectory finds. At "
            "ρ = 24.5, for instance, C₊ has eigenvalues about −13.65 and "
            "−0.0072 ± 9.58i, stable, and a start half a unit from it "
            "spirals in; yet from (1, 1, 1) the app's Lyapunov estimate is "
            "+0.80 ± 0.01, chaotic. That is the hysteresis of the "
            "subcritical pitchfork, now in three dimensions, and it happens "
            "with every equilibrium hyperbolic. At ρ = 28 the rolls are gone "
            "and chaos is all that is left."
        ),
        Para(
            "Why does everything stay bounded, and why is the attractor so "
            "thin? The divergence of the Lorenz field, "
            "∂x'/∂x + ∂y'/∂y + ∂z'/∂z, is −σ − 1 − β = −41/3 at the classic "
            "values, a constant. So every blob of initial conditions shrinks "
            "in volume like e^(−41t/3): the attractor has zero volume, and "
            "yet, within it, neighbouring trajectories separate."
        ),
        Para(
            "What makes that motion chaotic is not its irregularity but "
            "its sensitivity. Start two solutions at ρ = 28 from points on "
            "the attractor 10⁻⁸ apart and integrate both accurately. In one "
            "such run the separation stayed below 10⁻⁶ until t ≈ 3.7, "
            "passed 1 at t ≈ 19.7 and 10 at t ≈ 23.4, by which time the two "
            "solutions were on opposite sides of an attractor whose x ranges "
            "over roughly ±19. The difference grows, on average, "
            "exponentially."
        ),
        Box(
            "definition", "Lyapunov exponent",
            "The largest Lyapunov exponent λ of a bounded solution is the "
            "long-run average exponential rate at which a small perturbation "
            "of it grows: |δ(t)| ≈ |δ(0)|e^(λt). A solution with λ > 0 on a "
            "bounded attractor is called chaotic. At an attracting "
            "equilibrium λ is negative, and on a limit cycle it is zero.",
            r"\lambda = \lim_{t \to \infty} \frac{1}{t}\ln\frac{|\delta(t)|}"
            r"{|\delta(0)|}",
        ),
        Para(
            "For Lorenz at ρ = 28 the published value is about 0.906. The "
            "app's estimator, which follows two nearby solutions and "
            "renormalises their separation at regular intervals, gives "
            "0.913 ± 0.008 from five runs of 100 time units. At ρ = 15, "
            "below the Hopf value, the same routine returns −0.350 and calls "
            "the motion attracting: trajectories settle on one of C±, and "
            "the exponent is the real part of the slow pair of eigenvalues "
            "there."
        ),
        Para(
            "An exponential growth rate turns directly into a limit on "
            "prediction. If the initial state is known to within ε, the "
            "error reaches the size of the attractor itself, order one in "
            "relative terms, when εe^(λt) ≈ 1."
        ),
        Display(r"t_{\mathrm{horizon}} \approx \frac{\ln(1/\varepsilon)}{\lambda}",
                "16"),
        Worked(
            "The predictability horizon",
            "With λ = 0.906, find the horizon of equation 16 for initial "
            "errors of 10⁻⁴ and 10⁻⁸, and for the 10⁻¹⁶ of double-precision "
            "arithmetic.",
            (
                Step("ln(10⁴) ≈ 9.21, so ε = 10⁻⁴ gives about 9.21/0.906 ≈ 10.2 "
                     "time units.",
                     r"\frac{\ln 10^{4}}{0.906} \approx 10.2"),
                Step("ln(10⁸) is twice ln(10⁴), so ε = 10⁻⁸ gives about 20.3: "
                     "ten thousand times more accuracy has only doubled the "
                     "horizon. The run above, started 10⁻⁸ apart, reached "
                     "separation 1 at t ≈ 19.7, as close to this estimate as "
                     "an average rate can promise.",
                     r"\frac{\ln 10^{8}}{0.906} \approx 20.3"),
                Step("Even ε = 10⁻¹⁶, a start correct to the last bit a "
                     "computer can store, gives only about 40.7. Past that "
                     "time a computed Lorenz trajectory is a faithful sample "
                     "of the attractor but not a prediction of where this "
                     "particular solution is.",
                     r"\frac{\ln 10^{16}}{0.906} \approx 40.7"),
            ),
        ),
        Para(
            "The Solver Lab does this computation for Lorenz whenever a run "
            "is long enough to need it: it estimates λ, takes the solver's "
            "relative tolerance as ε, marks the horizon on the plot and draws "
            "the trajectory beyond it faintly. It estimates λ from a short "
            "run of 15 time units, so its value is rougher, about 0.8, and "
            "its horizon a little longer than the worked example's; a "
            "horizon is an order of magnitude, not a date. That is also, in "
            "outline, why weather forecasts have a range. The atmosphere is "
            "far more complicated than equation 14, but it shares the property that "
            "matters: errors in the initial state grow exponentially, so "
            "each gain in the accuracy of measurement buys only a fixed "
            "increment of forecast time."
        ),
        Box(
            "remark", "Chaos is not randomness",
            "A chaotic system is completely deterministic: the same start "
            "gives the same trajectory every time, and the Lorenz equations "
            "contain no randomness at all. What chaos lacks is "
            "predictability in practice, because any error in the start, "
            "however small, grows exponentially. The attractor, its shape "
            "and its long-run statistics are perfectly reproducible; only "
            "the path along it is not.",
        ),
    )),
    Section("Common errors", (
        Box(
            "warning", "Node to spiral is not a bifurcation",
            "When the discriminant τ² − 4Δ passes through zero, real "
            "eigenvalues become a complex pair and a node becomes a spiral. "
            "Stability does not change and no equilibrium appears or "
            "disappears. A Hopf bifurcation needs the real part of a complex "
            "pair to pass through zero, which is the trace, not the "
            "discriminant.",
        ),
        Para(
            "Several other slips recur. The first is to look for a "
            "bifurcation where the Jacobian merely changes, rather than "
            "where an eigenvalue's real part reaches zero; by the persistence "
            "theorem, no equilibrium can appear, vanish or change stability "
            "anywhere else (orbits far from the equilibria can still "
            "reorganise, as they do in Lorenz, but that is a global matter). "
            "The "
            "second is to confuse the saddle-node with the transcritical "
            "bifurcation: in a saddle-node two equilibria end, and in a "
            "transcritical one they cross and both continue. The third is "
            "to read the stability of the branches of r + x² the wrong way "
            "round; the derivative 2x decides it, so the negative root is "
            "the stable one. The fourth is to assume a Hopf bifurcation "
            "produces a small stable cycle; it may be subcritical, as in "
            "Lorenz. The fifth is to call a planar system chaotic because "
            "its trajectories look complicated: an autonomous system in the "
            "plane cannot be, whatever a finite computation suggests, and "
            "the app's Lyapunov estimate refuses to call one chaotic for "
            "that reason. The last is to think chaos means the equations "
            "are random. They are not; only the errors in using them grow."
        ),
    )),
    Section("Summary", (
        Para(
            "A bifurcation is a parameter value at which the qualitative "
            "picture of a family of systems changes. Hyperbolic equilibria "
            "persist with their stability under small changes, so a "
            "bifurcation of an equilibrium needs an eigenvalue with zero "
            "real part: a real eigenvalue through zero (the determinant "
            "crossing zero) or a complex pair through the imaginary axis "
            "(the trace crossing zero while the determinant is positive). "
            "The first gives the one-dimensional normal forms: the "
            "saddle-node r + x², where two equilibria collide and vanish, as "
            "a harvested population does at h = 1/4; the transcritical "
            "rx − x², where two cross and exchange stability, as at an "
            "epidemic threshold R₀ = 1; and the pitchfork rx − x³, where one "
            "becomes three in a symmetric system. The second is the Hopf "
            "bifurcation, whose radius obeys r' = r(μ − r²) in polar form, "
            "with r now the radius and μ the parameter: a limit cycle of "
            "size about √μ is born, as in the Rayleigh oscillator at μ = 0 "
            "and the Brusselator at b = 1 + a². Supercritical "
            "bifurcations are gentle, subcritical ones jump and show "
            "hysteresis, and all of them are heralded by critical slowing "
            "down. Changes away from the equilibria, global bifurcations, "
            "are not caught by this local test. A map can also lose "
            "stability through a multiplier of −1, and the logistic map "
            "doubles its period again and again, at gaps shrinking by "
            "Feigenbaum's δ ≈ 4.669, until chaos sets in at r ≈ 3.5699. In "
            "three dimensions the Poincaré–Bendixson restriction no longer "
            "applies, and the Lorenz system at ρ = 28 is chaotic, "
            "with largest Lyapunov exponent about 0.906: an initial error ε "
            "reaches the size of the attractor after about ln(1/ε)/λ, so "
            "prediction has a horizon that more accuracy extends only "
            "logarithmically. That ends the unit on nonlinear systems, and "
            "its lesson is the one to keep: when no formula exists, the "
            "equilibria, their linearisations, the conserved and decreasing "
            "quantities, and the parameter values where the picture changes "
            "still say what the solutions do. The series unit, which closes "
            "the course, returns to linear equations and finds solutions "
            "where the earlier methods found none."
        ),
    )),
)
