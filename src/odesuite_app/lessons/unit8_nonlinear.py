"""Unit 8 -- Nonlinear systems and phenomena.

Edwards, Penney and Calvis 6e, chapter 6. Everything before this unit solved
equations; this one mostly cannot, and says so. A nonlinear system almost
never has a formula, and the chapter's whole method is to learn what the
solutions do without one: find the equilibria, linearise at each, read the
picture, and know exactly where that reading stops being trustworthy.

**Why the worked examples are what they are.** No narrator in this
application solves a nonlinear system, and none should pretend to. What the
chapter actually *computes* by hand is always one of three things: a
linearisation, which is a linear system the `systems` narrator works in full;
an orbit equation dy/dx, which is a first-order equation the `steps` narrator
separates; or a radial or normal-form equation, which is scalar. So every
worked example is one of those, generated and checked like every other
example in the course -- the nonlinear system itself is what the figure and
the Phase Portrait show.

**Every drill has an oracle in the application.** The coexistence
determinant is checked against `analysis.jacobian_at`, the nullcline
crossing against `analysis.find_fixed_points`, the limit-cycle radius against
`analysis.largest_closed_orbit`, the Hopf value against the eigenvalues, the
peak speed against an integration -- in `tests/test_unit8.py`. Those routines
were corrected against closed forms before this unit was written, which is
why it waited for them.
"""

from __future__ import annotations

from .model import (
    Choice,
    ChoiceTemplate,
    Example,
    Lesson,
    Note,
    NumericTemplate,
    Passage,
    Solve,
)

__all__ = ["EQUILIBRIA", "ALMOST_LINEAR", "ECOLOGY", "MECHANICS",
           "CYCLES", "BIFURCATIONS", "LESSONS"]


EQUILIBRIA = Lesson(
    key="nonlinear-equilibria",
    title="Equilibria of a nonlinear system, and linearising at each",
    summary="Where a nonlinear system rests, and the linear system that "
            "describes it near each resting place.",
    tool="portrait",
    portrait="pendulum",
    reference="Edwards 6.1–6.2",
    figure="linearise",
    prerequisites=("phase-portraits",),
    motivation=(
        "A pendulum obeys x'' + sin x = 0, and that sine is the end of "
        "everything the course has built. Characteristic roots, undetermined "
        "coefficients, eigenvectors, Laplace transforms — every one of them "
        "depends on superposition, and superposition fails the moment the "
        "unknown sits inside a sine. There is no formula for the pendulum in "
        "terms of anything a first course has met, and for most nonlinear "
        "systems there is no formula at all.\n\n"
        "What survives is the question a formula was only ever a means to: "
        "what does the system do? And the first part of that answer needs no "
        "solving. An equilibrium is a state where every rate is zero, so "
        "finding them is algebra — set the right-hand sides to zero and solve. "
        "The pendulum has two kinds, hanging straight down and balanced "
        "straight up, and everyone already knows they behave completely "
        "differently.\n\n"
        "The second part is the idea this unit rests on. Very close to an "
        "equilibrium the nonlinear terms are tiny compared with the linear "
        "ones, so the system behaves almost exactly like a linear system — "
        "one Unit 6 can solve completely. Linearising turns one hard question "
        "into several easy ones, one per equilibrium, and the picture is "
        "assembled from the pieces."
    ),
    derivation=(
        Passage(
            prose="Write the system with its unknowns collected in a vector. It is "
                  "autonomous — t does not appear on the right — which is what makes "
                  "a single picture in the plane describe every solution at once.",
            latex=r"x' = f(x, y), \qquad y' = g(x, y)",
        ),
        Passage(
            prose="An equilibrium is a point where both rates vanish together. The "
                  "constant function sitting there is a solution, and it is found by "
                  "algebra alone: the two curves f = 0 and g = 0 are drawn, and "
                  "their crossings are the equilibria. A linear system had one; a "
                  "nonlinear one may have none, several, or infinitely many.",
            latex=r"f(x^{*}, y^{*}) = 0 \quad\text{and}\quad g(x^{*}, y^{*}) = 0",
        ),
        Passage(
            prose="Move a small distance u, v away from the equilibrium and expand "
                  "each right-hand side in Taylor series. The constant terms are zero "
                  "because the point is an equilibrium, so what is left starts with "
                  "the first derivatives — and the squares and products of u and v "
                  "that follow are smaller still.",
            latex=r"f(x^{*} + u, y^{*} + v) = f_x u + f_y v + O(u^{2} + v^{2})",
        ),
        Passage(
            prose="Dropping those higher terms leaves a linear system whose matrix is "
                  "the Jacobian: the four partial derivatives evaluated at the "
                  "equilibrium. Every equilibrium gets its own Jacobian, and so its "
                  "own linear system, which is why the same pendulum can spiral in "
                  "one place and be a saddle in another.",
            latex=r"J = \left(\frac{\partial(f, g)}{\partial(x, y)}\right)"
                  r"_{(x^{*}, y^{*})}, \qquad \mathbf{u}' \approx J\mathbf{u}",
        ),
        Passage(
            prose="For the pendulum x' = y, y' = −sin x − cy the derivatives are "
                  "easy, and cos x decides everything. At the bottom cos 0 = 1 and the "
                  "linear system is the damped oscillator; at the top cos π = −1 and "
                  "the sign of the restoring term flips, which is the whole difference "
                  "between hanging and balancing.",
            latex=r"J_{11} = 0, \;\; J_{12} = 1, \;\; J_{21} = -\cos x^{*}, "
                  r"\;\; J_{22} = -c",
        ),
        Passage(
            prose="From there Unit 6 takes over: trace, determinant, eigenvalues, "
                  "portrait. The answer is a description of the flow *near* the "
                  "equilibrium only, and how near is a question the next lesson "
                  "answers — the figure measures it directly, as the angle between "
                  "the true field and the linear one.",
            latex=r"\lambda^{2} - (\mathrm{tr}\,J)\lambda + \det J = 0",
        ),
    ),
    objectives=(
        "Find every equilibrium of a planar system by solving f = 0, g = 0.",
        "Compute the Jacobian at an equilibrium and write the linear system.",
        "Classify each equilibrium from its linearisation.",
        "Explain why different equilibria of one system look different.",
    ),
    examples=(
        Example(
            equation="x' = y; y' = -x - y",
            narrator="systems",
            why="The damped pendulum x'' + x' + sin x = 0 near its hanging rest "
                "state. With cos 0 = 1 the Jacobian is the matrix of a damped "
                "oscillator, and the narrator finds a stable spiral.",
            commentary=(
                "Before any eigenvalue, check where this matrix came from. The "
                "derivative of −sin x at x = 0 is −cos 0 = −1, the derivative "
                "of −y with respect to y is −1, and the first row is the "
                "identity x' = y carried over unchanged. Nothing about the "
                "sine survives except its slope at the bottom.\n\n"
                "Then read the result as a statement about the pendulum. A "
                "complex pair with negative real part means small swings "
                "shrink as they turn — the familiar decaying oscillation. It "
                "says nothing yet about large swings, which the linear system "
                "was never asked about."
            ),
        ),
        Example(
            equation="x' = y; y' = x",
            narrator="systems",
            why="The undamped pendulum near the inverted position, written in "
                "u = x − π. There cos π = −1 flips the sign of the restoring "
                "term, and the linearisation is a saddle.",
            commentary=(
                "The algebra is the same as at the bottom; only the value of "
                "cos changes. That single sign turns a restoring force into a "
                "repelling one, and the determinant goes negative — a saddle, "
                "settled before the eigenvalues ±1 are even computed.\n\n"
                "The two eigendirections matter more here than the numbers. "
                "Along one of them a pendulum given exactly the right push "
                "creeps up to the balance point and stops there; along the "
                "other it falls away. Those two directions are where the "
                "separatrix of Lesson 4 starts."
            ),
        ),
    ),
    notes=(
        Note(
            "Equilibria are algebra",
            "Set every right-hand side to zero at once and solve. No "
            "integration is involved, and every constant solution of the "
            "system is found this way — which is why it is always the first "
            "step.",
            r"f(x^{*}, y^{*}) = g(x^{*}, y^{*}) = 0",
            "idea",
        ),
        Note(
            "The Jacobian at a point",
            "The four first partial derivatives of f and g, evaluated at the "
            "equilibrium. Its trace and determinant classify the equilibrium "
            "exactly as they classified the origin of a linear system in "
            "Unit 6.",
            r"J_{11} = f_x, \;\; J_{12} = f_y, \;\; J_{21} = g_x, \;\; "
            r"J_{22} = g_y",
            "formula",
        ),
        Note(
            "One Jacobian per equilibrium",
            "Evaluate the derivatives at each equilibrium separately. The "
            "matrix changes from point to point, and so does the "
            "classification: the pendulum is a spiral at the bottom and a "
            "saddle at the top.",
            r"J(0, 0) \neq J(\pi, 0)",
            "idea",
        ),
        Note(
            "Linearise at the equilibrium, not at the origin",
            "The Taylor expansion is taken about the equilibrium. Using the "
            "derivatives at (0, 0) for an equilibrium somewhere else answers "
            "a question about the wrong point, and gives a confident wrong "
            "classification.",
            r"J \text{ at } (x^{*}, y^{*})",
            "pitfall",
        ),
        Note(
            "Local means local",
            "The linearisation describes the flow in a neighbourhood of the "
            "equilibrium and nowhere else. How large that neighbourhood is "
            "depends on the size of the neglected terms, and the figure "
            "shows the agreement degrading as the window widens.",
            r"\mathbf{u}' = J\mathbf{u} + O(|\mathbf{u}|^{2})",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="How are the equilibria of x' = f(x, y), y' = g(x, y) found?",
            options=(
                "Solve f = 0 and g = 0 simultaneously",
                "Solve the system and let t go to infinity",
                "Find where the Jacobian's determinant is zero",
                "Set x' = y' and solve",
            ),
            answer=0,
            becauses=(
                "An equilibrium is a constant solution, so both derivatives are "
                "zero there — which is two algebraic equations in two unknowns.",
                "Limits of solutions can find stable equilibria, but never "
                "unstable ones, and it needs the solutions this unit usually "
                "cannot find.",
                "A zero determinant says the linearisation is degenerate at a "
                "point; it has nothing to do with where the equilibria are.",
                "Equal rates are not zero rates: along x' = y' both variables "
                "are still changing.",
            ),
        ),
        Choice(
            key="q2",
            prompt="x' = x − xy, y' = xy − y. Which point is NOT an equilibrium?",
            options=("(0, 0)", "(1, 1)", "(1, 0)", "all three are equilibria"),
            answer=2,
            becauses=(
                "Both right-hand sides contain a factor that vanishes at the "
                "origin, so (0, 0) is an equilibrium.",
                "At (1, 1): 1 − 1 = 0 and 1 − 1 = 0. Both rates vanish.",
                "At (1, 0) the second equation gives 0 − 0 = 0 but the first "
                "gives 1 − 0 = 1, so x is still changing. Both have to vanish.",
                "One of them fails the first equation: check each point in "
                "both right-hand sides, not just one.",
            ),
        ),
        Choice(
            key="q3",
            prompt="The pendulum x' = y, y' = −sin x. Its Jacobian at an "
                   "equilibrium (x*, 0) has bottom-left entry…",
            options=("−cos x*", "−sin x*", "cos x*", "−1 always"),
            answer=0,
            becauses=(
                "∂/∂x of −sin x is −cos x, evaluated at the equilibrium: −1 at "
                "the bottom and +1 at the top.",
                "That is the function itself, not its derivative — and at an "
                "equilibrium sin x* = 0, so it would always be zero.",
                "The sign is lost: the derivative of −sin x is −cos x.",
                "−1 is the value at the bottom only. At x* = π the entry is "
                "+1, which is exactly why the top is a saddle.",
            ),
        ),
        Solve(
            key="q4",
            prompt="x' = 2x − 4y + x², y' = x − 3y + y² has an equilibrium at "
                   "the origin. Its linearisation there is the system below — "
                   "solve it, and name the equilibrium.",
            equation="x' = 2*x - 4*y; y' = x - 3*y",
            hints=(
                "At the origin the derivatives of x² and y² are zero, so the "
                "quadratic terms leave no trace in the Jacobian.",
                "tr J = −1 and det J = −6 + 4 = −2. A negative determinant is "
                "a saddle before anything else is computed.",
                "The eigenvalues are 1 and −2, with eigenvectors (4, 1) and "
                "(1, 1).",
            ),
        ),
        Solve(
            key="q5",
            prompt="The damped pendulum x'' + 2x' + 2 sin x = 0 near its hanging "
                   "position linearises to the system below. Solve it.",
            equation="x' = y; y' = -2*x - 2*y",
            hints=(
                "sin x ≈ x near x = 0, so 2 sin x becomes 2x and the second "
                "equation is y' = −2x − 2y.",
                "tr J = −2, det J = 2, discriminant 4 − 8 < 0: a stable "
                "spiral.",
                "The eigenvalues are −1 ± i, so the solution is e^(−t) times "
                "sines and cosines of t.",
            ),
        ),
    ),
    templates=(
        NumericTemplate(
            key="coexistence-determinant",
            title="The Jacobian at a coexistence point",
            prompt="Linearise x' = {a}*x - x*y, y' = x*y - {c}*y at its "
                   "equilibrium ({c}, {a}), where both populations are positive. "
                   "What is the determinant of the Jacobian there?",
            answer="{a}*{c}",
            because="The Jacobian is (a − y, −x; y, x − c), which at (c, a) is "
                    "(0, −c; a, 0). Its determinant is ac, positive, and its "
                    "trace is zero — the linearisation is a centre.",
            latex=r"\det J = (a - y)(x - c) + xy",
            hints=(
                "Differentiate each right-hand side with respect to x and to "
                "y; the four results are the entries of the Jacobian.",
                "Evaluate at the equilibrium: the diagonal entries both vanish "
                "there, which makes the determinant a single product.",
            ),
            slots=(("a", (1, 2, 3)), ("c", (1, 2, 3, 4))),
        ),
    ),
)


ALMOST_LINEAR = Lesson(
    key="almost-linear",
    title="Almost linear systems: when the linearisation tells the truth",
    summary="The cases where the linear picture is guaranteed to be the real "
            "one, and the one case where it guarantees nothing.",
    tool="portrait",
    portrait="duffing",
    reference="Edwards 6.2",
    figure="almost_linear",
    prerequisites=("nonlinear-equilibria",),
    motivation=(
        "Linearising throws information away on purpose. The quadratic and "
        "cubic terms are dropped because they are small near the equilibrium, "
        "and the conclusion drawn from what is left is then applied to a "
        "system that still has them. That is only honest if dropping them "
        "cannot change the answer, and whether it can is not obvious at "
        "all.\n\n"
        "The reassuring half is a theorem. When no eigenvalue of the Jacobian "
        "lies on the imaginary axis the equilibrium is called hyperbolic, and "
        "near a hyperbolic equilibrium the nonlinear flow is a smoothly "
        "distorted copy of the linear one: saddles stay saddles, spirals stay "
        "spirals, and stability is exactly what the eigenvalues say. Most "
        "equilibria in practice are hyperbolic, which is why linearisation is "
        "so useful.\n\n"
        "The warning half is the centre. Purely imaginary eigenvalues mean the "
        "linear terms produce no growth and no decay at all, so the neglected "
        "terms — however small — are the only thing left to decide whether "
        "trajectories creep inwards, outwards, or close up. A centre in the "
        "linearisation is a question, not an answer, and the figure shows the "
        "same linearisation hiding three different behaviours."
    ),
    derivation=(
        Passage(
            prose="Call the system almost linear at an equilibrium when the remainder "
                  "after the Jacobian term is small compared with the distance from "
                  "the equilibrium — which is true whenever f and g have continuous "
                  "second derivatives, so for every system in this course.",
            latex=r"\frac{|\mathbf{r}(\mathbf{u})|}{|\mathbf{u}|} \to 0 "
                  r"\quad\text{as}\quad \mathbf{u} \to \mathbf{0}",
        ),
        Passage(
            prose="A real part that is strictly negative or strictly positive "
                  "produces exponential decay or growth, and an exponential rate "
                  "beats any remainder that shrinks faster than the distance. So "
                  "near the equilibrium the linear term wins, and the sign of each "
                  "real part is the truth about the nonlinear system too.",
            latex=r"\mathrm{Re}\,\lambda \neq 0 \;\Longrightarrow\; "
                  r"\text{the linear term dominates}",
        ),
        Passage(
            prose="That is the content of the Hartman–Grobman theorem, stated in "
                  "the form a course uses: a hyperbolic equilibrium has the same "
                  "type and the same stability as its linearisation. Nodes, saddles "
                  "and spirals all carry over.",
            latex=r"\text{hyperbolic} \;\Longrightarrow\; \text{same type, "
                  r"same stability}",
        ),
        Passage(
            prose="Now take eigenvalues ±iω. The linear part only rotates, so in "
                  "polar coordinates it contributes nothing to r'. Whatever the "
                  "remainder puts into r' is the entire radial motion — and a "
                  "remainder of either sign is consistent with the same Jacobian.",
            latex=r"\lambda = \pm i\omega \;\Longrightarrow\; r' = "
                  r"\text{(remainder terms only)}",
        ),
        Passage(
            prose="The figure's system makes this exact. Its Jacobian at the origin "
                  "is a pure rotation for every a, and in polar form the radial "
                  "equation is r' = a r³: outward for a > 0, inward for a < 0, and "
                  "a genuine centre only at a = 0.",
            latex=r"x' = -y + a x r^{2}, \quad y' = x + a y r^{2} "
                  r"\;\Longrightarrow\; r' = a r^{3}",
        ),
        Passage(
            prose="Repeated real eigenvalues are the other borderline case: the "
                  "stability survives but the node may be perturbed into a spiral, "
                  "because the boundary between the two is a single curve the "
                  "remainder can push the eigenvalues across.",
            latex=r"\lambda_1 = \lambda_2 \;\Longrightarrow\; \text{node or "
                  r"spiral, same stability}",
        ),
    ),
    objectives=(
        "Decide whether an equilibrium is hyperbolic from its eigenvalues.",
        "State what the linearisation guarantees at a hyperbolic equilibrium.",
        "Explain why a linear centre decides nothing about the nonlinear system.",
        "Use a conserved quantity or a polar equation to settle a centre.",
    ),
    examples=(
        Example(
            equation="x' = y; y' = x - y",
            narrator="systems",
            why="The Duffing oscillator x'' + x' − x + x³ = 0 at the origin. "
                "The Jacobian has a negative determinant, the equilibrium is "
                "hyperbolic, and Hartman–Grobman makes the saddle real.",
            commentary=(
                "The cubic term contributes 3x² to the Jacobian, which is zero "
                "at the origin, so the linear system is read straight off the "
                "linear terms. Its determinant is −1: one eigenvalue positive, "
                "one negative, neither zero.\n\n"
                "That is enough for the theorem to apply, and it is worth "
                "noticing how much it gives. The real Duffing flow near the "
                "origin has a stable and an unstable curve through it — "
                "tangent to the eigenvectors, bent by the cubic — and those "
                "curves divide the two wells of the potential."
            ),
        ),
        Example(
            equation="x' = y; y' = -2*x - y",
            narrator="systems",
            why="The same Duffing oscillator at its right-hand rest state "
                "(1, 0), in coordinates centred there. Here 1 − 3x² = −2 and "
                "the linearisation is a stable spiral, which is also genuine.",
            commentary=(
                "Shift the origin to the equilibrium first: u = x − 1. The "
                "entry −1 + 3x² evaluated at x = 1 becomes 2, entering the "
                "second equation with a minus sign, and the damping term is "
                "unchanged at −1.\n\n"
                "Trace −1 and determinant 2 put it in the stable spiral "
                "region with a margin — the real parts are −1/2, nowhere near "
                "zero. Nothing the cubic does can undo a margin like that "
                "near the point, which is precisely what hyperbolic means."
            ),
        ),
    ),
    notes=(
        Note(
            "Hyperbolic",
            "An equilibrium whose Jacobian has no eigenvalue with zero real "
            "part. At a hyperbolic equilibrium the nonlinear flow has the "
            "same type and stability as the linear one.",
            r"\mathrm{Re}\,\lambda_i \neq 0 \text{ for every } i",
            "formula",
        ),
        Note(
            "A linear centre is undecided",
            "Purely imaginary eigenvalues make the linear part rotate without "
            "growing or shrinking, so the nonlinear terms decide. The real "
            "system may be a centre, a stable spiral or an unstable spiral — "
            "and the Jacobian cannot tell which.",
            r"\lambda = \pm i\omega",
            "pitfall",
        ),
        Note(
            "Settling a centre",
            "Two tools do it. A conserved quantity whose level curves are "
            "closed around the point proves a genuine centre; a polar "
            "equation for r' shows directly whether trajectories creep in or "
            "out.",
            r"\frac{d}{dt}E(x, y) = 0",
            "idea",
        ),
        Note(
            "Zero eigenvalues decide nothing either",
            "An eigenvalue exactly zero is the other non-hyperbolic case, and "
            "it is where equilibria appear, merge and vanish as a parameter "
            "moves — the subject of the last lesson of the unit.",
            r"\det J = 0",
            "aside",
        ),
        Note(
            "The Phase Portrait says so too",
            "The Phase Portrait screen marks a non-hyperbolic equilibrium as "
            "classified from the linearisation only, with this lesson's "
            "caveat beside it, rather than printing the word centre alone.",
            r"\text{centre} \;\to\; \text{centre (linearisation only)}",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="The Jacobian at an equilibrium has eigenvalues −3 and 2. "
                   "What is the equilibrium of the nonlinear system?",
            options=("a saddle", "undecided", "a stable node", "a centre"),
            answer=0,
            becauses=(
                "Both real parts are nonzero, so the equilibrium is hyperbolic "
                "and Hartman–Grobman carries the saddle over to the nonlinear "
                "system.",
                "Undecided is the verdict for eigenvalues on the imaginary "
                "axis. These are real and nonzero, so the theorem applies.",
                "A stable node needs both eigenvalues negative; the 2 sends "
                "trajectories out along its eigendirection.",
                "A centre needs purely imaginary eigenvalues, and these are "
                "real.",
            ),
        ),
        Choice(
            key="q2",
            prompt="The Jacobian at an equilibrium has eigenvalues ±2i. The "
                   "nonlinear system near it is…",
            options=(
                "a centre",
                "not determined by the linearisation",
                "a stable spiral",
                "unstable, because the real part is not negative",
            ),
            answer=1,
            becauses=(
                "The linear system is a centre, but the neglected terms are the "
                "only thing that can move a trajectory in or out, so they "
                "decide. The linearisation cannot vouch for the centre.",
                "Purely imaginary eigenvalues are the non-hyperbolic case: no "
                "linear growth or decay, so the higher-order terms settle it — "
                "centre, stable spiral or unstable spiral.",
                "It may be — if the higher-order terms pull inwards — but "
                "nothing in the Jacobian says so.",
                "A zero real part means neutral at the linear level, not "
                "unstable; the true behaviour could go either way.",
            ),
        ),
        Choice(
            key="q-figure",
            prompt="Set a to +0.100 in the figure. The readout names the "
                   "linearisation and measures the trajectory. What does it "
                   "show?",
            figure="almost_linear",
            options=(
                "The linearisation says centre, and the trajectory spirals "
                "outwards",
                "The linearisation says unstable spiral, matching the "
                "trajectory",
                "Both say centre: the orbit closes",
                "The linearisation says stable spiral and the trajectory "
                "grows",
            ),
            answer=0,
            becauses=(
                "The Jacobian at the origin is the same rotation for every a, "
                "so it reads ±i, a centre, while r' = a r³ > 0 drives the "
                "radius from 0.5 to about 1.6. The two disagree, which is the "
                "whole point.",
                "The linearisation cannot see a: the cubic terms have zero "
                "derivative at the origin. Only the trajectory can.",
                "Only a = 0 closes the orbit. At +0.1 the measured radius "
                "grows with every turn.",
                "The eigenvalues printed are ±1.000i — no real part at all, "
                "so the linearisation claims neither stable nor unstable.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Which equilibrium does Hartman–Grobman NOT cover?",
            options=(
                "eigenvalues ±i",
                "eigenvalues −1 ± i",
                "eigenvalues 3 and −1",
                "eigenvalues −2 and −5",
            ),
            answer=0,
            becauses=(
                "Zero real parts make it non-hyperbolic, which is exactly the "
                "case the theorem excludes.",
                "The real part −1 is nonzero, so the stable spiral is genuine.",
                "Two nonzero real eigenvalues of opposite sign: a hyperbolic "
                "saddle.",
                "Two negative real eigenvalues: a hyperbolic stable node.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Linearise x'' + x' − x + x³ = 0 at its left-hand rest state "
                   "(−1, 0), in coordinates centred there, and solve the linear "
                   "system.",
            equation="x' = y; y' = -2*x - y",
            hints=(
                "The Jacobian's bottom-left entry is 1 − 3x², which is −2 at "
                "x = −1 exactly as at x = +1: the potential is symmetric.",
                "tr J = −1, det J = 2, discriminant 1 − 8 < 0. A stable "
                "spiral, and hyperbolic.",
                "The eigenvalues are −1/2 ± (√7/2)i.",
            ),
        ),
    ),
    templates=(
        ChoiceTemplate(
            key="centre-undecided",
            title="Does the linearisation decide?",
            prompt="At an equilibrium of a nonlinear system the Jacobian has "
                   "eigenvalues ±{w}i. What can be concluded about the "
                   "nonlinear system there?",
            options=(
                "Nothing definite from the Jacobian: a centre, or a spiral "
                "turning either way",
                "It is a centre, with closed orbits around it",
                "It is a stable spiral",
                "It is a saddle",
            ),
            answer=0,
            becauses=(
                "Imaginary eigenvalues make the equilibrium non-hyperbolic, so "
                "the neglected terms decide the radial motion and any of the "
                "three is possible.",
                "The linear system is a centre; the nonlinear one need not be. "
                "Settling it takes a conserved quantity or a polar equation.",
                "Possible, if the nonlinear terms pull inwards, but the "
                "Jacobian contains no such information.",
                "A saddle needs real eigenvalues of opposite sign; these are "
                "an imaginary pair.",
            ),
            latex=r"\lambda = \pm {w} i",
            slots=(("w", (2, 3, 4, 5, 6, 7)),),
        ),
    ),
)


ECOLOGY = Lesson(
    key="ecological-models",
    title="Predators, competitors, and reading the nullclines",
    summary="Two populations that affect each other, and how the curves "
            "where each stops changing organise the whole picture.",
    tool="portrait",
    portrait="lotka_volterra",
    reference="Edwards 6.3",
    figure="competition",
    prerequisites=("almost-linear",),
    motivation=(
        "The oldest nonlinear systems in applied mathematics are about "
        "animals. Lotka and Volterra wrote down, independently, the simplest "
        "possible account of foxes eating rabbits: rabbits grow when left "
        "alone, foxes starve when left alone, and every encounter helps one "
        "and costs the other. Encounters happen at a rate proportional to the "
        "product of the two populations, and that product is the "
        "nonlinearity.\n\n"
        "Change one sign and the same shape describes competition instead: two "
        "species eating the same food, each held back by its own crowding and "
        "by the other. Here the question is not whether populations cycle but "
        "which species survive — and the answer turns out to depend on a "
        "comparison between how hard each species competes with itself and "
        "how hard with the other.\n\n"
        "Neither system can be solved in closed form, and neither needs to be. "
        "The tool this lesson adds is the nullcline: the curve on which one of "
        "the two populations is momentarily not changing. Drawn together, the "
        "nullclines locate every equilibrium, divide the plane into regions "
        "where the direction of the flow is known at a glance, and make the "
        "survival question something you can answer with a ruler."
    ),
    derivation=(
        Passage(
            prose="Predator and prey: x rabbits, y foxes. Each population has its "
                  "own rate when alone, and the interaction term xy enters the two "
                  "equations with opposite signs, because an encounter is a meal "
                  "for one and a loss for the other.",
            latex=r"x' = a x - b x y, \qquad y' = -c y + d x y",
        ),
        Passage(
            prose="Setting each right-hand side to zero gives the nullclines. The "
                  "x-nullclines are x = 0 and y = a/b; the y-nullclines are y = 0 "
                  "and x = c/d. Their crossings are the equilibria: extinction at "
                  "the origin, and coexistence where the two non-trivial lines "
                  "meet.",
            latex=r"(x^{*}, y^{*}) = \left(\frac{c}{d}, \frac{a}{b}\right)",
        ),
        Passage(
            prose="The Jacobian at the coexistence point has zero trace and a "
                  "positive determinant ac — a linear centre, which the previous "
                  "lesson says decides nothing. What decides it here is a "
                  "conserved quantity: dividing the two equations and separating "
                  "gives one, and its level curves are closed.",
            latex=r"V(x, y) = d x - c \ln x + b y - a \ln y = \text{const}",
        ),
        Passage(
            prose="So the predator–prey orbits really are closed loops: populations "
                  "cycle forever, the prey peak coming a quarter-cycle before the "
                  "predator peak. The cycles are not limit cycles — each starting "
                  "point has its own loop, which is what the conserved quantity "
                  "forces.",
            latex=r"\frac{dV}{dt} = V_x x' + V_y y' = 0",
        ),
        Passage(
            prose="Competition: each species has logistic growth, and each is "
                  "harmed by the other. Scaled so that each alone settles at 1, the "
                  "nullclines are the axes and two straight lines, and coexistence "
                  "requires those lines to cross inside the positive quadrant.",
            latex=r"x' = x(1 - x - \alpha y), \qquad y' = y(1 - y - \beta x)",
        ),
        Passage(
            prose="Solving the two line equations gives the coexistence point, and "
                  "the Jacobian there is stable exactly when both coefficients are "
                  "below one — each species limits itself more than it limits the "
                  "other. When both exceed one the point is a saddle, and which "
                  "species wins depends on where the populations start.",
            latex=r"\left(\frac{1 - \alpha}{1 - \alpha\beta}, "
                  r"\frac{1 - \beta}{1 - \alpha\beta}\right), \qquad "
                  r"\alpha, \beta < 1 \;\Longrightarrow\; \text{coexistence}",
        ),
    ),
    objectives=(
        "Write down a predator–prey or competition model from its assumptions.",
        "Draw the nullclines and locate every equilibrium from their crossings.",
        "Show that predator–prey orbits are closed using a conserved quantity.",
        "Predict coexistence or exclusion from the competition coefficients.",
    ),
    examples=(
        Example(
            equation="x' = -y; y' = x",
            narrator="systems",
            why="Lotka–Volterra x' = x − xy, y' = xy − y at its coexistence "
                "point (1, 1). The Jacobian is a pure rotation — a linear "
                "centre, which on its own would settle nothing.",
            commentary=(
                "Compute the four derivatives and evaluate at (1, 1): 1 − y "
                "and x − 1 vanish there, leaving −x = −1 in the top right and "
                "y = 1 in the bottom left. The diagonal is empty, so the trace "
                "is zero.\n\n"
                "The narrator's circles are the linear picture. The real "
                "orbits are the level curves of V = x − ln x + y − ln y, "
                "which are closed but not circular — egg-shaped, squashed "
                "towards the axes. The conserved quantity is what upgrades "
                "the undecided centre into a real one."
            ),
        ),
        Example(
            equation="x' = -2*x - y; y' = -2*x - 4*y",
            narrator="systems",
            why="Competition x' = x(4 − 2x − y), y' = y(5 − x − 2y) at its "
                "coexistence point (1, 2). Both species limit themselves more "
                "than each other, and the linearisation is a stable node.",
            commentary=(
                "Find the point from the nullclines first: 2x + y = 4 and "
                "x + 2y = 5 cross at (1, 2). Then the Jacobian entries are "
                "4 − 4x − y = −2, −x = −1, −y = −2 and 5 − x − 4y = −4.\n\n"
                "Trace −6, determinant 6, discriminant 12: two real negative "
                "eigenvalues, −3 ± √3. Hyperbolic, so the node is genuine, "
                "and every population starting in the positive quadrant ends "
                "at (1, 2) — the two species coexist."
            ),
        ),
    ),
    notes=(
        Note(
            "Nullclines",
            "The x-nullcline is where x' = 0 and the y-nullcline is where "
            "y' = 0. Equilibria are exactly the points on both, and between "
            "them the signs of x' and y' — and so the rough direction of the "
            "flow — are constant.",
            r"f(x, y) = 0, \qquad g(x, y) = 0",
            "formula",
        ),
        Note(
            "Predator–prey cycles are closed",
            "The conserved quantity V = dx − c ln x + by − a ln y has closed "
            "level curves around the coexistence point, so populations cycle "
            "and never settle. Each starting point has its own cycle.",
            r"V(x, y) = dx - c\ln x + by - a\ln y",
            "formula",
        ),
        Note(
            "A trajectory crosses an x-nullcline vertically",
            "On the x-nullcline x' = 0, so the flow there is purely up or "
            "down. Drawing a crossing arrow sloping sideways is the usual "
            "sketching mistake, and it misplaces every turning point.",
            r"x' = 0 \;\Longrightarrow\; \text{vertical flow}",
            "pitfall",
        ),
        Note(
            "Self-limitation beats competition",
            "In the scaled competition model the species coexist when both "
            "coefficients are below one. When both are above one, one "
            "species drives the other out, and which one depends on where "
            "the populations start.",
            r"\alpha < 1, \;\beta < 1",
            "idea",
        ),
        Note(
            "Volterra's fishery puzzle",
            "Moderate fishing lowers both growth rates, which moves the "
            "coexistence point towards more prey and fewer predators — the "
            "observation from the Adriatic that started the subject.",
            r"x^{*} = \frac{c}{d}, \quad y^{*} = \frac{a}{b}",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="In x' = ax − bxy, y' = −cy + dxy, which variable is the "
                   "predator?",
            options=("y", "x", "neither — the model is symmetric",
                     "whichever is larger"),
            answer=0,
            becauses=(
                "Alone (x = 0) y decays at rate c, and encounters (the xy "
                "term) add to it. It starves without the other species, which "
                "is what a predator does.",
                "x grows at rate a when alone and loses by encounters — the "
                "behaviour of prey.",
                "The signs are not symmetric: one species gains from "
                "encounters and the other loses.",
                "The roles are fixed by the signs of the terms, not by the "
                "sizes of the populations.",
            ),
        ),
        Choice(
            key="q2",
            prompt="Why are the Lotka–Volterra orbits closed, when the "
                   "linearisation at coexistence is only a centre?",
            options=(
                "A conserved quantity has closed level curves there",
                "Hartman–Grobman guarantees it",
                "Every centre of a linear system stays a centre",
                "Because the populations are positive",
            ),
            answer=0,
            becauses=(
                "V(x, y) is constant along every trajectory, and its level "
                "curves around the coexistence point are closed loops — so "
                "the orbits are those loops.",
                "Hartman–Grobman needs a hyperbolic equilibrium. A centre is "
                "exactly the case it does not cover.",
                "That is the claim the almost-linear lesson refutes: a linear "
                "centre can hide a spiral either way.",
                "Positivity keeps orbits in the quadrant but says nothing "
                "about whether they close.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Scaled competition x' = x(1 − x − 1.5y), "
                   "y' = y(1 − y − 1.5x). What happens?",
            options=(
                "One species wins, and which depends on the starting point",
                "Both coexist at a stable equilibrium",
                "Both die out",
                "The populations cycle",
            ),
            answer=0,
            becauses=(
                "Both coefficients exceed one, so the coexistence point (0.4, "
                "0.4) is a saddle. Its stable curve divides the quadrant into "
                "two basins, one for each winner.",
                "Stable coexistence needs both coefficients below one; here "
                "each species harms the other more than itself.",
                "The origin is an unstable node — each species alone grows "
                "towards 1 — so extinction of both never happens.",
                "Competition models of this form have no cycles: the "
                "equilibria and their basins account for every trajectory.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Lotka–Volterra x' = 2x − xy, y' = xy − 3y has coexistence "
                   "point (3, 2). The linearisation there, with u = x − 3 and "
                   "v = y − 2, is below. Solve it.",
            equation="x' = -3*y; y' = 2*x",
            hints=(
                "At (3, 2): 2 − y = 0 and x − 3 = 0 empty the diagonal. The "
                "off-diagonal entries are −x = −3 and y = 2.",
                "tr J = 0 and det J = 6 — a linear centre with frequency √6.",
                "The solutions are sines and cosines of √6·t; the true orbits "
                "are closed because of the conserved quantity.",
            ),
        ),
    ),
    templates=(
        NumericTemplate(
            key="nullcline-crossing",
            title="Where the nullclines cross",
            prompt="Two species compete: x' = x*({p} - x - y), "
                   "y' = y*({r} - x - 2*y). Their non-trivial nullclines "
                   "x + y = {p} and x + 2y = {r} cross at the coexistence "
                   "point. What is its x-coordinate?",
            answer="2*{p} - {r}",
            because="Subtracting the first line from the second gives y = r − p, "
                    "and then x = p − y = 2p − r. Both are positive, so the "
                    "crossing is inside the quadrant and is an equilibrium of "
                    "the system.",
            hints=(
                "An equilibrium with both species present has to lie on both "
                "non-trivial nullclines, so solve the two line equations "
                "together.",
                "Subtract one line equation from the other to eliminate x.",
            ),
            slots=(("p,r", ((3, 4), (3, 5), (4, 5), (4, 6), (4, 7), (5, 6),
                            (5, 7), (5, 8), (5, 9))),),
        ),
    ),
)


MECHANICS = Lesson(
    key="nonlinear-mechanics",
    title="Conservative systems: the pendulum, energy and the separatrix",
    summary="How a conserved energy turns a system you cannot solve into "
            "curves you can draw.",
    tool="portrait",
    portrait="pendulum",
    reference="Edwards 6.4",
    figure="pendulum_energy",
    prerequisites=("almost-linear",),
    motivation=(
        "A frictionless pendulum never solves in elementary functions, yet "
        "anyone who has pushed a swing knows exactly what it does: small "
        "pushes give swings, and a big enough push sends it over the top. "
        "That knowledge is not a formula for x(t). It is a statement about "
        "energy, and energy is what makes a whole class of nonlinear systems "
        "readable.\n\n"
        "A mechanical system with no friction conserves its energy, so every "
        "trajectory stays on one curve E(x, y) = constant in the phase plane. "
        "The picture of the flow is then just the picture of those level "
        "curves — a contour map — and a contour map can be drawn without "
        "solving any differential equation. The equilibria are the critical "
        "points of the energy: minima are centres, and saddle points of the "
        "energy are saddles of the flow.\n\n"
        "One level curve is special. It passes through the saddles and "
        "separates the orbits that swing back and forth from the orbits that "
        "rotate over the top — the separatrix. It is the boundary between two "
        "qualitatively different fates, and it is why a pendulum given a push "
        "just below the critical speed and one given a push just above behave "
        "completely differently."
    ),
    derivation=(
        Passage(
            prose="Write the second-order equation x'' = −V'(x) as a system with "
                  "y = x'. Multiply the second equation by y and notice that both "
                  "sides are exact derivatives — the kinetic energy on the left and "
                  "the potential on the right.",
            latex=r"y y' = -V'(x)\, x' \;\Longrightarrow\; \frac{d}{dt}"
                  r"\left(\frac{1}{2}y^{2} + V(x)\right) = 0",
        ),
        Passage(
            prose="So E = y²/2 + V(x) is constant along every solution, and every "
                  "orbit lies on a level curve of E. For the pendulum V(x) = −cos x, "
                  "and the level curves can be sketched from the graph of the "
                  "cosine alone.",
            latex=r"E(x, y) = \frac{1}{2}y^{2} - \cos x",
        ),
        Passage(
            prose="The same fact comes out of the orbit equation. Dividing y' by x' "
                  "eliminates t and gives dy/dx = −V'(x)/y, which is separable; "
                  "separating and integrating recovers the energy. This is the route "
                  "the worked examples take, with the narrator's t standing for x.",
            latex=r"\frac{dy}{dx} = -\frac{\sin x}{y} \;\Longrightarrow\; "
                  r"\frac{1}{2}y^{2} = \cos x + C",
        ),
        Passage(
            prose="Minima of V are centres, and here the centre is genuine rather "
                  "than undecided: near a minimum the level curves of E are closed "
                  "loops, and the orbits have no choice but to follow them.",
            latex=r"V'(x^{*}) = 0, \;\; V''(x^{*}) > 0 \;\Longrightarrow\; "
                  r"\text{centre}",
        ),
        Passage(
            prose="Maxima of V are saddles. The level curve through them is the "
                  "separatrix: for the pendulum E = 1, which at the bottom is a "
                  "speed of exactly 2. Below it the pendulum swings, above it the "
                  "pendulum rotates, and on it the pendulum takes infinitely long "
                  "to creep up to the balance point.",
            latex=r"E = 1 \;\Longleftrightarrow\; y = \pm 2\cos\frac{x}{2}",
        ),
        Passage(
            prose="Friction breaks the conservation, and the energy becomes a "
                  "Lyapunov function instead: it can only decrease, so trajectories "
                  "cross the level curves inwards and settle at a minimum. The "
                  "centres become stable spirals, which is what the linearisation "
                  "said too.",
            latex=r"x'' + c x' + \sin x = 0 \;\Longrightarrow\; "
                  r"\frac{dE}{dt} = -c\, y^{2} \leq 0",
        ),
    ),
    objectives=(
        "Derive the energy of x'' = −V'(x) and show it is conserved.",
        "Sketch the phase plane of a conservative system from its potential.",
        "Find the separatrix and say which orbits lie on each side of it.",
        "Explain how damping turns the energy into a decreasing quantity.",
    ),
    examples=(
        Example(
            equation="y' = -sin(t)/y",
            conditions="y(0) = 2",
            why="The pendulum's orbit equation dy/dx = −sin x / y, with the "
                "narrator's t standing for the angle x. Starting at the bottom "
                "with speed 2 puts the orbit exactly on the separatrix.",
            commentary=(
                "Read the variable change first. The pendulum's state is "
                "(x, y) and time has been eliminated, so the independent "
                "variable here is the angle; the narrator calls it t because "
                "it calls every independent variable t.\n\n"
                "The answer √(2 cos t + 2) equals 2|cos(t/2)|, and it reaches "
                "zero exactly at t = ±π — the inverted position. That is the "
                "separatrix: an orbit that arrives at the balance point with "
                "no speed left, which is what E = 1 means."
            ),
        ),
        Example(
            equation="y' = -4*t/y",
            conditions="y(0) = 2",
            why="The orbit equation of the linear oscillator x'' + 4x = 0, "
                "where V = 2x² and every level curve is an ellipse. The "
                "harmonic case to compare the pendulum against.",
            commentary=(
                "Here the potential is exactly quadratic, so the energy "
                "y²/2 + 2x² has ellipses for level curves, and the narrator "
                "finds 2√(1 − t²) — the upper half of the ellipse through "
                "(0, 2) with semi-axes 1 and 2.\n\n"
                "Compare it with the pendulum: near the bottom cos x ≈ "
                "1 − x²/2, so small pendulum orbits are nearly ellipses too. "
                "They stop being ellipses as the amplitude grows, and stop "
                "closing at all at the separatrix. That departure is the "
                "nonlinearity, drawn."
            ),
        ),
    ),
    notes=(
        Note(
            "Energy for x'' = −V'(x)",
            "E = y²/2 + V(x), with y = x', is constant along every solution. "
            "Orbits are its level curves, so the phase plane is its contour "
            "map.",
            r"E(x, y) = \frac{1}{2}y^{2} + V(x)",
            "formula",
        ),
        Note(
            "Minima are centres, maxima are saddles",
            "At a minimum of V the level curves of E close around the point, "
            "so the centre is genuine. At a maximum they cross, making a "
            "saddle whose level curve is the separatrix.",
            r"V''(x^{*}) > 0 \text{ centre}, \quad V''(x^{*}) < 0 \text{ saddle}",
            "idea",
        ),
        Note(
            "The pendulum's separatrix",
            "E = 1, reached from the bottom with speed exactly 2. Below it "
            "the pendulum swings; above it the pendulum goes over the top and "
            "keeps rotating.",
            r"y = \pm 2\cos\frac{x}{2}",
            "formula",
        ),
        Note(
            "A separatrix orbit takes forever",
            "Starting on the separatrix, the pendulum approaches the inverted "
            "position but never reaches it in finite time — the saddle is an "
            "equilibrium, and no trajectory arrives at one in finite time. "
            "Expecting it to get there and fall back is the usual mistake.",
            r"t \to \infty \text{ as } x \to \pi",
            "pitfall",
        ),
        Note(
            "Damping makes the energy a Lyapunov function",
            "With friction, dE/dt = −cy² ≤ 0, so the energy only falls and "
            "trajectories spiral into a minimum. A quantity that decreases "
            "along the flow proves stability without any linearisation.",
            r"\frac{dE}{dt} = -c\,y^{2}",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="For x'' + sin x = 0, which quantity is conserved?",
            options=(
                "y²/2 − cos x",
                "y²/2 + cos x",
                "y² + x²",
                "y − sin x",
            ),
            answer=0,
            becauses=(
                "Here V'(x) = sin x, so V = −cos x and E = y²/2 − cos x; "
                "differentiating gives y y' + sin x · x' = y(−sin x) + sin x · y "
                "= 0.",
                "The sign of the potential is wrong: its derivative gives "
                "y y' − sin x · y = −2y sin x, which is not zero.",
                "That is the harmonic oscillator's energy (times two). It is "
                "only approximately conserved for small swings.",
                "Differentiating gives y' − cos x · x' = −sin x − y cos x, "
                "which is not zero.",
            ),
        ),
        Choice(
            key="q2",
            prompt="An undamped pendulum starts at the bottom with speed 1.9. "
                   "What does it do?",
            options=(
                "Swings back and forth, just below the top",
                "Goes over the top and keeps rotating",
                "Stops at the top",
                "Spirals into the bottom",
            ),
            answer=0,
            becauses=(
                "E = 1.9²/2 − 1 = 0.805 < 1, so the orbit is inside the "
                "separatrix: it swings, turning back before the inverted "
                "position.",
                "Going over needs E > 1, a starting speed above 2.",
                "Only an orbit exactly on the separatrix approaches the top, "
                "and it needs speed exactly 2.",
                "Spiralling needs damping. With none, the energy is conserved "
                "and the orbit closes.",
            ),
        ),
        Choice(
            key="q3",
            prompt="What does the separatrix of the pendulum separate?",
            options=(
                "Swinging orbits from rotating orbits",
                "Stable equilibria from unstable ones",
                "Positive from negative velocities",
                "Damped from undamped motion",
            ),
            answer=0,
            becauses=(
                "Inside it the energy is below 1 and the pendulum oscillates; "
                "outside it the pendulum has enough energy to go over the top "
                "and rotates.",
                "The equilibria are points, not regions. The separatrix passes "
                "through the saddles but separates families of orbits.",
                "The x-axis does that, and trajectories cross it all the time.",
                "Damping is a property of the equation, not of a region of the "
                "phase plane.",
            ),
        ),
        Solve(
            key="q4",
            prompt="The oscillator x'' + x³ = 0 has orbit equation "
                   "dy/dx = −x³/y. With the narrator's t standing for x, solve "
                   "it through (0, 1).",
            equation="y' = -t**3/y",
            conditions="y(0) = 1",
            hints=(
                "Separate the variables: y dy = −x³ dx.",
                "Integrate: y²/2 = −x⁴/4 + C, and (0, 1) gives C = 1/2.",
                "So y² = 1 − x⁴/2 — a level curve of the energy "
                "y²/2 + x⁴/4, closed around the origin.",
            ),
        ),
        Solve(
            key="q5",
            prompt="Solve the pendulum's orbit equation through the bottom "
                   "with speed 1, and check that the orbit stays inside the "
                   "separatrix.",
            equation="y' = -sin(t)/y",
            conditions="y(0) = 1",
            hints=(
                "Separating gives y²/2 = cos x + C, as in the worked example.",
                "At x = 0, y = 1 gives C = −1/2, so E = −1/2 < 1.",
                "y = √(2 cos x − 1) vanishes at x = ±π/3: the pendulum turns "
                "back at 60°.",
            ),
        ),
    ),
    templates=(
        NumericTemplate(
            key="peak-speed",
            title="Top speed from the energy",
            prompt="The hardening spring x'' + {k}*x**3 = 0 is released from rest "
                   "at x = {A}. Using its conserved energy, what is its greatest "
                   "speed |x'|?",
            answer="{A}**2*sqrt({k}/2)",
            tolerance=1e-3,
            because="The energy is y²/2 + k x⁴/4. At release it is k A⁴/4, all "
                    "potential; at x = 0 it is all kinetic, so y²/2 = k A⁴/4 and "
                    "the speed is A² √(k/2).",
            hints=(
                "Write the energy as kinetic plus potential, with the "
                "potential the integral of k x³.",
                "The speed is greatest where the potential is least, at "
                "x = 0.",
            ),
            slots=(("k", (1, 2, 4, 8)), ("A", (1, 2, 3))),
        ),
    ),
)


CYCLES = Lesson(
    key="limit-cycles",
    title="Limit cycles, and why the plane forbids chaos",
    summary="Isolated closed orbits that trajectories are drawn onto, and "
            "the theorem that limits what a planar system can do.",
    tool="portrait",
    portrait="van_der_pol",
    reference="Edwards 6.4 (extended)",
    figure="limit_cycle",
    prerequisites=("nonlinear-mechanics",),
    motivation=(
        "A heart beats at its own rhythm whether it starts slow or fast. A "
        "violin string driven by the bow settles to one amplitude however it "
        "was first plucked. Van der Pol's vacuum-tube circuit oscillates at a "
        "size set by the circuit, not by the switch-on transient. None of "
        "these is a centre — a centre has a different orbit for every "
        "starting point, and forgets nothing about how it started.\n\n"
        "What they have instead is a limit cycle: one closed orbit, isolated, "
        "which neighbouring trajectories approach from inside and from "
        "outside. It is the nonlinear system's way of choosing an amplitude, "
        "and no linear system can do it: a linear system's closed orbits come "
        "in continuous families, scaled copies of each other.\n\n"
        "Planar systems turn out to be tightly constrained. A bounded "
        "trajectory in the plane can only approach an equilibrium, a closed "
        "orbit, or a chain of equilibria and the orbits linking them — the "
        "Poincaré–Bendixson theorem. That is a strong statement about what "
        "cannot happen: nothing chaotic, ever, in an autonomous planar system. "
        "It is also a tool, because trapping a trajectory in a region with no "
        "equilibria proves a limit cycle is there."
    ),
    derivation=(
        Passage(
            prose="The cleanest example is built in polar coordinates, where the "
                  "radius and the angle decouple. The angle turns at a constant "
                  "rate, and the radius obeys a scalar equation of its own.",
            latex=r"r' = r(\mu - r^{2}), \qquad \theta' = 1",
        ),
        Passage(
            prose="The radial equation is a phase line. For μ > 0 it has equilibria "
                  "r = 0 and r = √μ, with r' positive between them and negative "
                  "beyond, so every radius except zero moves towards √μ. In the "
                  "plane that is a circle every trajectory approaches: a stable "
                  "limit cycle.",
            latex=r"\mu > 0: \quad r \to \sqrt{\mu} \text{ from both sides}",
        ),
        Passage(
            prose="In Cartesian coordinates the same system has a Jacobian at the "
                  "origin with eigenvalues μ ± i: an unstable spiral. The "
                  "linearisation sees trajectories leave the origin and cannot see "
                  "where they go; the cubic terms, invisible to the Jacobian, are "
                  "what stop them.",
            latex=r"x' = \mu x - y - x(x^{2} + y^{2}), \quad y' = x + \mu y - "
                  r"y(x^{2} + y^{2})",
        ),
        Passage(
            prose="Isolation is what distinguishes a limit cycle from a centre's "
                  "orbit. Push a trajectory off a limit cycle and it comes back; "
                  "push it off a centre's orbit and it settles on a different closed "
                  "orbit. The Phase Portrait's limit-cycle layer makes exactly this "
                  "test and draws the two differently.",
            latex=r"\text{limit cycle} = \text{isolated closed orbit}",
        ),
        Passage(
            prose="Poincaré–Bendixson turns that into a method. Find a region the "
                  "flow cannot leave — an annulus with the field pointing inwards on "
                  "both edges — that contains no equilibrium. A trajectory trapped "
                  "there has nothing to approach except a closed orbit.",
            latex=r"\text{trapping region} + \text{no equilibria} "
                  r"\;\Longrightarrow\; \text{a closed orbit inside}",
        ),
        Passage(
            prose="The same theorem is why chaos needs three dimensions. In the "
                  "plane a trajectory cannot cross itself, which confines it to the "
                  "three fates above. With a third variable — or a time-dependent "
                  "forcing, which acts as one — trajectories can pass over and "
                  "under each other, and Lorenz's system does exactly that.",
            latex=r"\text{planar, autonomous} \;\Longrightarrow\; "
                  r"\text{no chaos}",
        ),
    ),
    objectives=(
        "Tell a limit cycle from a centre's closed orbit by isolation.",
        "Find the limit cycle of a system from its polar radial equation.",
        "State Poincaré–Bendixson and use a trapping region to prove a cycle.",
        "Explain why an autonomous planar system cannot be chaotic.",
    ),
    examples=(
        Example(
            equation="y' = y*(1 - y**2)",
            conditions="y(0) = 1/2",
            why="The radial equation r' = r(1 − r²) of the normal form at μ = 1, "
                "with the narrator's y standing for r. A trajectory starting "
                "inside the cycle at radius 1/2 grows onto it.",
            commentary=(
                "It is separable as well as Bernoulli, and the narrator "
                "separates it, but the answer to look at is its limit: "
                "e^t/√(e^(2t) + 3) tends to 1 as t grows. The radius goes to "
                "the cycle and stops there.\n\n"
                "Try the other side in your head: start at r = 2 and r' = "
                "2(1 − 4) < 0, so the radius shrinks towards 1 instead. Both "
                "sides converging on one radius is precisely what makes the "
                "circle a limit cycle rather than one orbit of many."
            ),
        ),
        Example(
            equation="y' = y*(y**2 - 1)",
            conditions="y(0) = 1/2",
            why="The reversed system r' = r(r² − 1), whose circle r = 1 repels. "
                "Inside it trajectories fall to the origin; the cycle is "
                "unstable, and exists without ever being approached.",
            commentary=(
                "The narrator's answer 1/√(3e^(2t) + 1) decays to zero, so a "
                "trajectory starting inside the circle spirals into the "
                "origin, which here is a stable spiral. Outside, r grows "
                "without bound.\n\n"
                "An unstable limit cycle is a boundary rather than a "
                "destination — the edge of the origin's basin of attraction. "
                "It cannot be seen by running trajectories forward, only by "
                "running them backward in time, which is how it is computed "
                "in practice."
            ),
        ),
    ),
    notes=(
        Note(
            "Limit cycle",
            "A closed orbit with no other closed orbits nearby. Stable when "
            "nearby trajectories approach it from both sides, unstable when "
            "they leave it.",
            r"r' = r(\mu - r^{2}) \;\Longrightarrow\; r = \sqrt{\mu}",
            "formula",
        ),
        Note(
            "Poincaré–Bendixson",
            "A bounded trajectory of an autonomous planar system approaches "
            "an equilibrium, a closed orbit, or a cycle of equilibria joined "
            "by trajectories. A trapping region with no equilibria therefore "
            "contains a closed orbit.",
            r"\text{no equilibria in a trapping region} \;\Longrightarrow\; "
            r"\text{closed orbit}",
            "formula",
        ),
        Note(
            "A centre is not a limit cycle",
            "Lotka–Volterra's orbits are all closed, and none is a limit "
            "cycle: each is surrounded by other closed orbits. Calling one of "
            "them a limit cycle is the most common confusion in this chapter.",
            r"\text{closed} \neq \text{isolated}",
            "pitfall",
        ),
        Note(
            "Van der Pol",
            "x'' − μ(1 − x²)x' + x = 0: negative damping for small x pumps "
            "energy in, positive damping for large x takes it out, and the "
            "balance is one limit cycle. At μ = 1 its period is 6.663.",
            r"x'' - \mu(1 - x^{2})x' + x = 0",
            "idea",
        ),
        Note(
            "The plane cannot be chaotic",
            "The Lyapunov estimate in this application refuses to call a "
            "planar autonomous system chaotic for exactly this reason, "
            "however its numbers come out over a finite run.",
            r"n \leq 2 \;\Longrightarrow\; \lambda_{\max} \leq 0",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="What makes a closed orbit a limit cycle?",
            options=(
                "It is isolated: no other closed orbits lie arbitrarily close",
                "It is closed",
                "It surrounds an equilibrium",
                "Its period does not depend on the amplitude",
            ),
            answer=0,
            becauses=(
                "Isolation is the defining property, and it is what lets "
                "trajectories approach it from nearby — there is nowhere else "
                "for them to settle.",
                "Every orbit of a centre is closed too, and none of them is a "
                "limit cycle.",
                "A centre's orbits surround an equilibrium as well; that does "
                "not distinguish the two.",
                "Harmonic oscillator orbits all share one period and form a "
                "continuous family, the opposite of isolated.",
            ),
        ),
        Choice(
            key="q2",
            prompt="Can an autonomous system x' = f(x, y), y' = g(x, y) be "
                   "chaotic?",
            options=(
                "No — Poincaré–Bendixson rules it out",
                "Yes, if f and g are nonlinear enough",
                "Yes, if it has a limit cycle",
                "Only if it has more than two equilibria",
            ),
            answer=0,
            becauses=(
                "A bounded planar trajectory can only approach an equilibrium, "
                "a closed orbit or a cycle of equilibria. Chaos needs a third "
                "dimension, or forcing that supplies one.",
                "No amount of nonlinearity escapes the theorem; it depends "
                "only on the dimension and on f and g not depending on t.",
                "A limit cycle is the opposite of chaos: every nearby "
                "trajectory becomes the same periodic motion.",
                "The number of equilibria has nothing to do with it.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Van der Pol's origin is an unstable spiral, and every "
                   "trajectory stays bounded. What must lie around the "
                   "origin?",
            options=(
                "A closed orbit",
                "Another equilibrium",
                "A separatrix",
                "Nothing: trajectories wander forever",
            ),
            answer=0,
            becauses=(
                "Take an annulus between a small circle (flow leaving the "
                "origin) and a large one (flow bounded inwards). It traps "
                "trajectories and holds no equilibrium, so Poincaré–Bendixson "
                "gives a closed orbit inside.",
                "Van der Pol has only the one equilibrium, at the origin.",
                "Separatrices come from saddles, and there is no saddle here.",
                "Wandering forever without settling is exactly what the "
                "theorem forbids in the plane.",
            ),
        ),
        Solve(
            key="q4",
            prompt="The radial equation of a system is r' = r(4 − r²). Solve it "
                   "from r(0) = 1 (the narrator's y is r) and read off the "
                   "radius of the limit cycle.",
            equation="y' = y*(4 - y**2)",
            conditions="y(0) = 1",
            hints=(
                "Equilibria of the radial equation are r = 0 and r = 2; the "
                "positive one is the cycle's radius.",
                "Between them r' > 0, so r = 1 grows towards 2.",
                "The solution is 2e^(4t)/√(e^(8t) + 3), which tends to 2.",
            ),
        ),
    ),
    templates=(
        NumericTemplate(
            key="cycle-radius",
            title="The radius of a limit cycle",
            prompt="x' = {mu}*x - y - x*(x**2 + y**2), y' = x + {mu}*y - "
                   "y*(x**2 + y**2). In polar form r' = r({mu} − r²). What is the "
                   "radius of its limit cycle?",
            answer="sqrt({mu})",
            tolerance=1e-3,
            because="The radial equation has equilibria r = 0 and r = √μ. "
                    "Between them r' > 0 and beyond √μ r' < 0, so every "
                    "trajectory except the origin approaches the circle of "
                    "radius √μ.",
            hints=(
                "A limit cycle of this system is a circle where r' = 0 "
                "without r being zero.",
                "Solve μ − r² = 0 for the positive r.",
            ),
            slots=(("mu", (1, 2, 3, 4, 5, 6, 7, 9)),),
        ),
    ),
)


BIFURCATIONS = Lesson(
    key="bifurcations-chaos",
    title="Bifurcations, and the road to chaos",
    summary="How the picture changes suddenly as a parameter moves, and what "
            "happens when a third dimension frees the flow.",
    tool="portrait",
    portrait="brusselator",
    reference="Edwards 6.5",
    figure="normal_forms",
    prerequisites=("limit-cycles",),
    motivation=(
        "Raise the harvest from a fish population a little and the population "
        "falls a little. Raise it a little more and the population collapses "
        "to nothing — not gradually, but all at once. Nothing about the "
        "equation changed except a number, and the qualitative behaviour "
        "changed completely. That sudden change is a bifurcation, and it is "
        "the most practically important thing nonlinear equations do.\n\n"
        "Bifurcations are rare in one sense and inevitable in another. For "
        "almost every parameter value, nudging it changes the picture only "
        "slightly — that is what hyperbolic equilibria guarantee. The "
        "exceptions are exactly the non-hyperbolic values: an eigenvalue "
        "passing through zero, or a complex pair crossing the imaginary axis. "
        "So the two cases the almost-linear lesson could not decide are "
        "precisely where the picture reorganises.\n\n"
        "And past enough bifurcations, in three dimensions, lies chaos: "
        "deterministic equations whose solutions are so sensitive to their "
        "starting values that prediction beyond a horizon is impossible. "
        "Lorenz found it in a model of convection; it is why weather forecasts "
        "have a range, and the Solver Lab measures that horizon for his "
        "system directly."
    ),
    derivation=(
        Passage(
            prose="Saddle-node: two equilibria approach each other, merge, and "
                  "vanish. The normal form x' = r + x² has ±√(−r) for r < 0 and none "
                  "for r > 0; at r = 0 they coincide and the derivative of the "
                  "right-hand side is zero there.",
            latex=r"x' = r + x^{2}: \quad x^{*} = \pm\sqrt{-r}\; (r < 0)",
        ),
        Passage(
            prose="Transcritical: two equilibria pass through each other and swap "
                  "stability. In x' = rx − x² the equilibria 0 and r cross at r = 0, "
                  "and the one that was stable becomes unstable as they pass.",
            latex=r"x' = r x - x^{2}: \quad x^{*} = 0, \; r",
        ),
        Passage(
            prose="Pitchfork: one equilibrium becomes three. In x' = rx − x³ the "
                  "origin is stable for r < 0; at r = 0 it loses stability and two "
                  "new stable equilibria ±√r branch off symmetrically — the Duffing "
                  "oscillator's two wells appearing.",
            latex=r"x' = r x - x^{3}: \quad x^{*} = 0, \; \pm\sqrt{r}\; (r > 0)",
        ),
        Passage(
            prose="Hopf: in two dimensions a complex pair of eigenvalues crosses "
                  "the imaginary axis and a limit cycle is born. The normal form is "
                  "the previous lesson's system: for μ < 0 a stable spiral, for "
                  "μ > 0 an unstable one surrounded by a cycle of radius √μ.",
            latex=r"\lambda = \mu \pm i, \qquad r = \sqrt{\mu}",
        ),
        Passage(
            prose="The Brusselator shows a Hopf in a real model. Its only "
                  "equilibrium is (a, b/a), and the trace of the Jacobian there "
                  "changes sign when b passes 1 + a², where a chemical oscillation "
                  "switches on.",
            latex=r"\mathrm{tr}\,J = b - 1 - a^{2} = 0 \;\Longrightarrow\; "
                  r"b = 1 + a^{2}",
        ),
        Passage(
            prose="Chaos is measured by the largest Lyapunov exponent: the rate at "
                  "which neighbouring trajectories separate. Positive means errors "
                  "grow exponentially, and an initial uncertainty ε becomes order "
                  "one after about ln(1/ε)/λ — the predictability horizon.",
            latex=r"|\delta(t)| \approx |\delta(0)| e^{\lambda t}, \qquad "
                  r"t_{\mathrm{horizon}} \approx \frac{\ln(1/\varepsilon)}{\lambda}",
        ),
    ),
    objectives=(
        "Name saddle-node, transcritical, pitchfork and Hopf bifurcations.",
        "Locate a bifurcation where an eigenvalue crosses the imaginary axis.",
        "Read a bifurcation diagram: branches, stability, and where they meet.",
        "Explain sensitive dependence and the predictability horizon.",
    ),
    examples=(
        Example(
            equation="y' = 4 - y**2",
            conditions="y(0) = 0",
            why="The saddle-node normal form on the side where its two "
                "equilibria still exist, ±2. The solution from 0 climbs to the "
                "stable one; lower the constant through zero and both vanish.",
            commentary=(
                "The narrator separates it and finds 2 tanh 2t, which tends "
                "to 2 — the stable equilibrium. The other one, −2, repels: "
                "start just below it and the solution runs off to minus "
                "infinity in finite time.\n\n"
                "Now replace 4 by a parameter r. The equilibria ±√r move "
                "together as r falls, meet at zero, and are gone for r < 0, "
                "when every solution runs off. The figure's saddle-node form "
                "is this with the sign conventions flipped."
            ),
        ),
        Example(
            equation="y' = y - y**3",
            conditions="y(0) = 1/2",
            why="The pitchfork normal form at r = 1, after the bifurcation. The "
                "origin is now unstable and the solution from 1/2 moves to the "
                "new stable equilibrium at +1.",
            commentary=(
                "The narrator's answer e^t/√(e^(2t) + 3) tends to 1, which is "
                "√r at r = 1. A start at −1/2 would go to −1: the symmetry of "
                "the equation is kept by the pair of branches even though "
                "each individual solution picks a side.\n\n"
                "That choice is the physical content of a pitchfork. A "
                "buckling beam goes left or right, a magnet aligns up or "
                "down, and which one is decided by a perturbation too small "
                "for the equation to contain."
            ),
        ),
    ),
    notes=(
        Note(
            "Bifurcation",
            "A parameter value at which the qualitative picture changes: "
            "equilibria appear, disappear or change stability, or a cycle is "
            "born. It happens only where an equilibrium is non-hyperbolic.",
            r"\mathrm{Re}\,\lambda = 0 \text{ at the bifurcation}",
            "idea",
        ),
        Note(
            "The four normal forms",
            "Saddle-node r + x², transcritical rx − x², pitchfork rx − x³, "
            "and in the plane Hopf, r' = r(μ − r²). Near a bifurcation, "
            "almost every system looks like one of these.",
            r"r + x^{2}, \quad rx - x^{2}, \quad rx - x^{3}",
            "formula",
        ),
        Note(
            "Hopf in a Jacobian",
            "A complex pair crosses the imaginary axis: the trace passes "
            "through zero while the determinant stays positive. That is where "
            "an oscillation switches on.",
            r"\mathrm{tr}\,J = 0, \quad \det J > 0",
            "formula",
        ),
        Note(
            "Chaos is not randomness",
            "A chaotic system is completely deterministic: the same start "
            "gives the same trajectory every time. What it lacks is "
            "predictability, because any error in the start grows "
            "exponentially.",
            r"\lambda_{\max} > 0",
            "pitfall",
        ),
        Note(
            "Lorenz",
            "x' = σ(y − x), y' = x(ρ − z) − y, z' = xy − βz. At σ = 10, "
            "β = 8/3 its non-trivial equilibria lose stability in a Hopf "
            "bifurcation at ρ = 24.74, and at ρ = 28 the motion is chaotic, "
            "with largest Lyapunov exponent about 0.906.",
            r"\rho_{H} = \frac{\sigma(\sigma + \beta + 3)}{\sigma - \beta - 1}",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="In x' = r + x², what happens as r increases through 0?",
            options=(
                "Two equilibria merge and disappear",
                "One equilibrium splits into three",
                "Two equilibria exchange stability",
                "A limit cycle is born",
            ),
            answer=0,
            becauses=(
                "For r < 0 the equilibria are ±√(−r); they meet at r = 0 and "
                "for r > 0 there are none. That is a saddle-node.",
                "One equilibrium becoming three is a pitchfork, rx − x³, not a saddle-node.",
                "Exchanging stability is a transcritical bifurcation, "
                "rx − x².",
                "A cycle needs two dimensions and a complex pair — a Hopf "
                "bifurcation, not a scalar equation.",
            ),
        ),
        Choice(
            key="q2",
            prompt="At a Hopf bifurcation, the eigenvalues of the Jacobian…",
            options=(
                "form a complex pair crossing the imaginary axis",
                "pass through zero one at a time",
                "become equal and real",
                "change from real to complex",
            ),
            answer=0,
            becauses=(
                "The real part of a complex pair changes sign while the "
                "imaginary part stays nonzero, so an oscillation of that "
                "frequency switches on.",
                "A real eigenvalue through zero is a steady-state bifurcation "
                "— saddle-node, transcritical or pitchfork — with no "
                "oscillation.",
                "Equal real eigenvalues mark the boundary between node and "
                "spiral, which changes nothing qualitative about stability.",
                "Real to complex is the node-to-spiral boundary again, not a "
                "change of stability.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Which of these can be chaotic?",
            options=(
                "The Lorenz system, three autonomous equations",
                "A pendulum with no forcing",
                "Van der Pol's oscillator",
                "Any system with a limit cycle",
            ),
            answer=0,
            becauses=(
                "Three dimensions give trajectories room to pass over and "
                "under each other, and at ρ = 28 Lorenz's do, with a positive "
                "Lyapunov exponent.",
                "An unforced pendulum is autonomous and planar, so "
                "Poincaré–Bendixson rules chaos out.",
                "Van der Pol is autonomous and planar: its trajectories settle "
                "on the limit cycle.",
                "A limit cycle is periodic, the opposite of chaotic.",
            ),
        ),
        Choice(
            key="q4",
            prompt="A chaotic system has λ = 0.9. How does the predictability "
                   "horizon change if the initial error shrinks from 10⁻⁴ to "
                   "10⁻⁸?",
            options=(
                "It roughly doubles",
                "It grows ten thousand times",
                "It does not change",
                "It becomes infinite",
            ),
            answer=0,
            becauses=(
                "The horizon is ln(1/ε)/λ, and ln(10⁸) is twice ln(10⁴). "
                "Squaring the accuracy only doubles how far ahead you can "
                "see.",
                "That would be true if error grew linearly. It grows "
                "exponentially, so accuracy buys time only logarithmically.",
                "A smaller error does delay the moment it reaches order one; "
                "the delay is just small.",
                "Only a perfect start avoids error growth, and no measurement "
                "is perfect.",
            ),
        ),
        Solve(
            key="q5",
            prompt="The saddle-node form x' = r − x² at r = 9. Solve it from "
                   "x(0) = 0 (the narrator's y is x) and name the equilibrium "
                   "it approaches.",
            equation="y' = 9 - y**2",
            conditions="y(0) = 0",
            hints=(
                "The equilibria are ±3. The right-hand side is positive "
                "between them, so a start at 0 increases.",
                "Separating with partial fractions gives the hyperbolic "
                "tangent.",
                "The solution is 3 tanh 3t, which tends to the stable "
                "equilibrium 3.",
            ),
        ),
    ),
    templates=(
        NumericTemplate(
            key="hopf-value",
            title="Where the oscillation switches on",
            prompt="The Brusselator x' = {a} - (b + 1)*x + x**2*y, "
                   "y' = b*x - x**2*y has one equilibrium, ({a}, b/{a}). For "
                   "which value of b does it undergo a Hopf bifurcation?",
            answer="1 + {a}**2",
            because="At (a, b/a) the Jacobian is (b − 1, a²; −b, −a²). Its "
                    "determinant a² is always positive, and its trace "
                    "b − 1 − a² passes through zero at b = 1 + a², where the "
                    "complex pair crosses the imaginary axis.",
            hints=(
                "Evaluate the Jacobian at the equilibrium; x² = a² and "
                "2xy = 2b there.",
                "A Hopf bifurcation happens where the trace is zero while the "
                "determinant is positive.",
            ),
            slots=(("a", (1, 2, 3, 4, 5, 6)),),
        ),
    ),
)


LESSONS = (EQUILIBRIA, ALMOST_LINEAR, ECOLOGY, MECHANICS, CYCLES, BIFURCATIONS)
