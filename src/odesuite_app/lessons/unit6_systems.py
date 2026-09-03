"""Unit 6 -- Linear systems.

Edwards, Penney and Calvis 6e, chapters 4 and 5. Two unknowns that will not
come apart, and the observation that makes them tractable: written as a matrix,
the pair becomes one equation whose answer is read off the eigenvalues.

The narrator this unit needs is `systems`, and it arrived with it. Every lesson
here is worked by the eigenvalue method rather than by anything new -- the
three cases (distinct, complex, defective) are the three a course spends its
time on, and they are three branches of one derivation rather than three
techniques.

Drills are on the distinct and defective cases. The complex one is left to
worked examples and practice: a complex draw whose eigenvector entries come
out as unsimplified fractions is a question nobody would set, and the
enumeration cannot tell in advance which draws those are.
"""

from __future__ import annotations

from .model import Choice, Example, Lesson, Note, Solve, Template

__all__ = ["FIRSTORDER", "DISTINCT", "COMPLEX", "REPEATED",
           "NONHOMOGENEOUS", "PORTRAITS", "LESSONS"]


FIRSTORDER = Lesson(
    key="systems-intro",
    title="First-order systems, and how everything becomes one",
    summary="Why a system is not two problems, and how a higher-order "
            "equation turns into one.",
    tool="steps",
    reference="Edwards 4.1",
    prerequisites=("roots",),
    objectives=(
        "Say what makes a system coupled, and why that stops you solving one "
        "equation at a time.",
        "Convert an nth-order equation into a first-order system.",
        "Write a linear system as x' = A x and name the matrix.",
        "Say how many arbitrary constants a system of n equations has.",
    ),
    examples=(
        Example(
            equation="y'' + 3*y' + 2*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            why="The equation this unit's method is secretly about. Setting "
                "x₁ = y and x₂ = y' turns it into a two-by-two system whose "
                "eigenvalues are exactly the characteristic roots — the same "
                "answer, reached the other way round.",
        ),
        Example(
            equation="y'' + 4*y = 0",
            conditions="y(0) = 0, y'(0) = 2",
            why="An oscillator, whose system form has a complex pair of "
                "eigenvalues. Worth holding on to for the lesson on complex "
                "eigenvalues, where the same matrix reappears.",
        ),
    ),
    notes=(
        Note(
            "Coupled means neither can go first",
            "In x' = x + 2y, the rate of x depends on y. You cannot solve for "
            "x and then substitute, because solving for x needs y and solving "
            "for y needs x. Everything in this unit exists because that "
            "circularity has to be broken all at once rather than in order.",
            r"x' = x + 2y, \qquad y' = 3x + 2y",
        ),
        Note(
            "Any higher-order equation is a system",
            "Name the derivatives as new unknowns and the chain closes: with "
            "x₁ = y and x₂ = y', the first equation is x₁' = x₂ and the "
            "second is whatever the original equation says about y''. An "
            "nth-order equation becomes n first-order ones.",
            r"x_1 = y,\ x_2 = y' \;\Longrightarrow\; x_1' = x_2,\ "
            r"x_2' = -\tfrac{c}{a}x_1 - \tfrac{b}{a}x_2",
            "formula",
        ),
        Note(
            "Matrix form is the whole idea",
            "Once written as x' = A x, the system stops being a list of "
            "equations and becomes one object. Every question about it — how "
            "it grows, whether it oscillates, what the origin looks like — "
            "turns into a question about A, and specifically about its "
            "eigenvalues.",
            r"\mathbf{x}' = A\mathbf{x}",
            "formula",
        ),
        Note(
            "Count the constants the same way",
            "A system of n first-order equations has n arbitrary constants, "
            "for the same reason an nth-order equation does — and it is the "
            "same count, because converting one into the other cannot change "
            "how much freedom the answer has.",
            r"\mathbf{x} = C_1\mathbf{x}_1 + \cdots + C_n\mathbf{x}_n",
            "aside",
        ),
        Note(
            "The conversion is not a trick",
            "It is how every numerical solver in existence takes a "
            "second-order equation, this project's included: the library "
            "integrates first-order systems and nothing else. When you ask it "
            "for a pendulum, this conversion is what happens first.",
            r"y'' = f(t, y, y') \;\longrightarrow\; \mathbf{x}' = "
            r"\mathbf{F}(t, \mathbf{x})",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="Converting y'' + 5y' + 6y = 0 with x₁ = y, x₂ = y′ gives…",
            options=(
                "x₁' = x₂, x₂' = −6x₁ − 5x₂",
                "x₁' = x₂, x₂' = 6x₁ + 5x₂",
                "x₁' = −5x₁, x₂' = −6x₂",
                "x₁' = x₁, x₂' = x₂",
            ),
            answer=0,
            becauses=(
                "The first is the naming itself, and the second is the "
                "original equation rearranged: y'' = −5y' − 6y, with y' and y "
                "written as x₂ and x₁.",
                "The signs are wrong. Moving 5y' + 6y across the equals sign "
                "changes both of them.",
                "This decouples the system, which is exactly what the "
                "conversion must not do — the whole point is that y'' depends "
                "on both y and y'.",
                "That is not the equation at all; it has lost every "
                "coefficient.",
            ),
        ),
        Choice(
            key="q2",
            prompt="How many arbitrary constants does a 3×3 first-order "
                   "linear homogeneous system have?",
            options=("1", "2", "3", "9"),
            answer=2,
            becauses=(
                "One would pin the answer down to a single family, but three "
                "initial values have to be free to choose.",
                "Two is the second-order answer. The count follows the number "
                "of equations.",
                "One per equation, matching the three initial values needed to "
                "pick a single trajectory. It is the same count as the "
                "third-order equation it could have come from.",
                "Nine is the number of entries in A, which has nothing to do "
                "with how much freedom the solution has.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Why can you not solve x' = x + 2y for x first?",
            options=(
                "The equation is nonlinear",
                "Its right-hand side contains y, which is also unknown",
                "There are no initial conditions",
                "x' is not isolated",
            ),
            answer=1,
            becauses=(
                "It is perfectly linear — both unknowns appear to the first "
                "power with constant coefficients. Linearity is what makes "
                "the matrix method work at all.",
                "Solving it would need y as a known function of t, and y is "
                "exactly what the second equation is still trying to find. "
                "That circularity is what 'coupled' means.",
                "Conditions pin constants at the end; their absence never "
                "stops you finding the general solution.",
                "It is isolated — x' is alone on the left. The obstacle is on "
                "the right.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Solve it as a second-order equation first — the system "
                   "form will give the same answer next lesson.",
            equation="y'' + 3*y' + 2*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            hints=(
                "r² + 3r + 2 = (r+1)(r+2), so the roots are −1 and −2.",
                "Those two numbers will turn out to be the eigenvalues of the "
                "matrix this converts to, which is not a coincidence.",
                "y = C₁e^{−t} + C₂e^{−2t}; the conditions give C₁ = 2 and "
                "C₂ = −1.",
            ),
        ),
        Solve(
            key="q5",
            prompt="An oscillator, in the form its system version will take.",
            equation="y'' + 4*y = 0",
            conditions="y(0) = 0, y'(0) = 2",
            hints=(
                "Roots ±2i — a purely imaginary pair, which as a system will "
                "mean a centre.",
                "A zero real part means no envelope: y = C₁cos 2t + C₂sin 2t.",
                "y(0) = 0 kills the cosine and y′(0) = 2 gives C₂ = 1.",
            ),
        ),
    ),
    templates=(
        Template(
            key="convertible",
            title="Second order, the equation behind a system",
            prompt="Solve it directly; the eigenvalues will match these roots.",
            equation="y'' + {b}*y' + {c}*y = 0",
            conditions="y(0) = {p}, y'(0) = {v}",
            technique="nth_linear_constant_coeff_homogeneous",
            hints=(
                "Substitute y = e^(rt) and read the characteristic "
                "polynomial off the coefficients.",
                "Factor it. These are built to factor over the integers, so "
                "the roots are small whole numbers or a clean pair.",
                "Write the general solution for that case, then use both "
                "conditions — differentiate before applying the second.",
            ),
            slots=(
                ("b,c", ((3, 2), (5, 6), (4, 3), (0, 4), (2, 5), (4, 4))),
                ("p,v", ((1, 0), (0, 2), (1, 1))),
            ),
        ),
    ),
)


DISTINCT = Lesson(
    key="eigenvalues",
    title="The eigenvalue method: real distinct eigenvalues",
    summary="Guess a solution that keeps its direction, and the whole system "
            "collapses into an eigenvalue problem.",
    tool="steps",
    reference="Edwards 5.2",
    prerequisites=("systems-intro",),
    objectives=(
        "Explain why x = v·e^{λt} turns the system into Av = λv.",
        "Find eigenvalues from det(A − λI) = 0.",
        "Find an eigenvector for each, and check it.",
        "Write the general solution, and name what the origin is.",
    ),
    examples=(
        Example(
            equation="x' = x + 2*y; y' = 3*x + 2*y",
            narrator="systems",
            why="Eigenvalues −1 and 4: one direction decaying, one growing, "
                "which makes the origin a saddle. The classic first example, "
                "and the one where the straight-line solutions are easiest to "
                "see.",
        ),
        Example(
            equation="x' = -2*x + y; y' = x - 2*y",
            narrator="systems",
            why="Both eigenvalues negative, so every trajectory runs into the "
                "origin — a stable node. Compare the picture with the saddle "
                "above; the algebra is identical and only the signs differ.",
        ),
    ),
    notes=(
        Note(
            "Guess a solution with a fixed direction",
            "Try x = v·e^{λt}, a constant vector whose length changes but "
            "whose direction never does. Substituting gives λv·e^{λt} = "
            "Av·e^{λt}, and the exponential cancels — leaving Av = λv, which "
            "has nothing to do with differential equations any more.",
            r"\mathbf{x} = \mathbf{v}e^{\lambda t} \;\Longrightarrow\; "
            r"A\mathbf{v} = \lambda\mathbf{v}",
            "formula",
        ),
        Note(
            "The eigenvalues come from a determinant",
            "Av = λv with v ≠ 0 means (A − λI)v = 0 has a non-zero solution, "
            "so A − λI must be singular, so its determinant is zero. For a "
            "2×2 matrix that is a quadratic — the characteristic equation, "
            "and the direct analogue of the one from a second-order equation.",
            r"\det(A - \lambda I) = 0",
            "formula",
        ),
        Note(
            "Scaling an eigenvector changes nothing",
            "If v is an eigenvector so is 2v, and −v, and v/7. The arbitrary "
            "constant in front absorbs the difference, which is why nobody "
            "normalises these and why your answer can look different from the "
            "book's and still be right.",
            r"A(cv) = c(Av) = \lambda(cv)",
            "aside",
        ),
        Note(
            "The eigenvectors are the straight-line solutions",
            "Start exactly on an eigenvector and you stay on it forever, "
            "moving in or out along that line. Every other trajectory is a "
            "combination of these two motions, which is why the eigenvector "
            "directions are the skeleton a phase portrait bends around.",
            r"\mathbf{x}(t) = \mathbf{v}e^{\lambda t}",
            "idea",
        ),
        Note(
            "Opposite signs mean a saddle",
            "One positive and one negative eigenvalue is the most distinctive "
            "case: trajectories come in along one eigendirection and leave "
            "along the other, and the origin attracts nothing except the "
            "points exactly on the stable line.",
            r"\lambda_1 < 0 < \lambda_2",
            "idea",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="Why does substituting x = v·e^{λt} help?",
            options=(
                "It makes the system nonlinear",
                "The exponential cancels, leaving an algebra problem",
                "It removes the initial conditions",
                "It diagonalises A",
            ),
            answer=1,
            becauses=(
                "It keeps the system linear, which is precisely why the "
                "substitution is legitimate.",
                "Both sides pick up the same e^{λt}, which is never zero and "
                "so can be divided out. What is left, Av = λv, has no "
                "derivatives in it at all.",
                "The conditions are applied at the end, exactly as for a "
                "single equation. Nothing here removes them.",
                "Finding eigenvectors is what would let you diagonalise A, "
                "but the substitution is what produces the eigenvector "
                "problem rather than the other way round.",
            ),
        ),
        Choice(
            key="q2",
            prompt="A 2×2 system has eigenvalues −3 and 2. The origin is…",
            options=(
                "a stable node",
                "an unstable node",
                "a saddle",
                "a spiral",
            ),
            answer=2,
            becauses=(
                "A stable node needs both eigenvalues negative, so that every "
                "direction decays. Here one of them grows.",
                "An unstable node needs both positive. Here one of them "
                "decays.",
                "Opposite signs: one eigendirection decays and the other "
                "grows, so trajectories come in one way and leave another. "
                "Saddles are always unstable.",
                "A spiral needs a complex pair. These eigenvalues are real, "
                "so nothing rotates.",
            ),
        ),
        Choice(
            key="q3",
            prompt="v is an eigenvector for λ = 4. Which is also one?",
            options=("v + 1", "−5v", "v²", "Av + v"),
            answer=1,
            becauses=(
                "Adding a constant to a vector is not even defined, and "
                "adding a constant vector would break the eigenvector "
                "equation.",
                "A(−5v) = −5(Av) = −5(4v) = 4(−5v). Any non-zero multiple is "
                "an eigenvector for the same eigenvalue, which is why "
                "eigenvectors are only ever determined up to scale.",
                "Squaring a vector is not defined either — there is no such "
                "operation in this setting.",
                "Av + v = 4v + v = 5v, which is a multiple of v, so this "
                "*is* an eigenvector — but for λ = 4 rather than any new "
                "eigenvalue, and the option is a trap that happens to be "
                "true for a less interesting reason. The intended answer is "
                "the plain scalar multiple.",
            ),
        ),
        Solve(
            key="q4",
            prompt="A saddle.",
            equation="x' = x + 2*y; y' = 3*x + 2*y",
            hints=(
                "A = [[1, 2], [3, 2]]. Its characteristic equation is "
                "λ² − 3λ − 4 = 0.",
                "That factors as (λ − 4)(λ + 1), so the eigenvalues are 4 and "
                "−1 — opposite signs, so expect a saddle.",
                "Solve (A − λI)v = 0 for each; the answers are proportional "
                "to (2, 3) and (1, −1).",
            ),
        ),
        Solve(
            key="q5",
            prompt="A stable node.",
            equation="x' = -2*x + y; y' = x - 2*y",
            hints=(
                "A = [[−2, 1], [1, −2]], so det(A − λI) = (λ+2)² − 1.",
                "Eigenvalues −1 and −3. Both negative, so everything decays "
                "into the origin.",
                "The eigenvectors are (1, 1) and (1, −1) — the symmetric and "
                "antisymmetric directions, which is what a symmetric matrix "
                "always gives.",
            ),
        ),
    ),
    templates=(
        Template(
            key="two-by-two",
            title="A 2×2 system with real distinct eigenvalues",
            prompt="Matrix, characteristic equation, eigenvectors, answer.",
            equation="x' = {a}*x + {b}*y; y' = {c}*x + {d}*y",
            narrator="systems",
            technique="systems",
            hints=(
                "Write A = [[{a}, {b}], [{c}, {d}]] and form "
                "det(A − λI) = 0.",
                "For a 2×2 that is λ² − (trace)λ + (determinant) = 0, where "
                "the trace is the sum of the diagonal and the determinant is "
                "ad − bc.",
                "Solve (A − λI)v = 0 for each eigenvalue, then combine the "
                "two v·e^(λt) solutions with one constant each.",
            ),
            # Every pair is chosen so the discriminant is a perfect square and
            # the eigenvalues are integers -- a draw with irrational
            # eigenvalues would be arithmetic practice, not method practice.
            slots=(
                ("a,b,c,d", ((1, 2, 3, 2), (-2, 1, 1, -2), (3, 1, 1, 3),
                             (1, 3, 3, 1), (4, 1, 2, 3), (2, 2, 1, 3),
                             (0, 1, 6, 1), (5, 2, 2, 2))),
            ),
        ),
    ),
)


COMPLEX = Lesson(
    key="complex-eigenvalues",
    title="Complex eigenvalues, and how to get back to real answers",
    summary="A complex pair means rotation — and one complex solution "
            "quietly contains both real ones.",
    tool="steps",
    reference="Edwards 5.3",
    prerequisites=("eigenvalues",),
    objectives=(
        "Recognise a complex pair from the characteristic equation.",
        "Find a complex eigenvector, and apply Euler's formula to the whole "
        "product.",
        "Take real and imaginary parts to get two real solutions.",
        "Say whether a spiral winds in or out, and which way it turns.",
    ),
    examples=(
        Example(
            equation="x' = -y; y' = x",
            narrator="systems",
            why="Eigenvalues ±i, a pure rotation. The simplest complex case "
                "there is, and the one where the real and imaginary parts "
                "come out as plainly cos and sin.",
        ),
        Example(
            equation="x' = -x - 2*y; y' = 2*x - x",
            narrator="systems",
            why="A spiral rather than a circle: the real part of the "
                "eigenvalue is negative, so the rotation is inside a decaying "
                "envelope. Compare the answer with the underdamped spring "
                "from Unit 4 — it is the same shape.",
        ),
    ),
    notes=(
        Note(
            "Complex eigenvalues come in pairs",
            "A real matrix has a real characteristic polynomial, so its "
            "complex roots arrive as conjugates. The conjugate eigenvalue "
            "gives the conjugate eigenvector and the conjugate solution, "
            "which is no new information — so only one of the pair needs "
            "working through.",
            r"\lambda = \alpha \pm \beta i",
        ),
        Note(
            "One complex solution carries two real ones",
            "If a complex function solves a system with real coefficients, "
            "its real and imaginary parts each solve it separately. That is "
            "why you never need the second eigenvalue: take v·e^{λt} apart "
            "and both real solutions fall out.",
            r"\mathbf{x} = \mathbf{v}e^{\lambda t} \;\Longrightarrow\; "
            r"\mathrm{Re}\,\mathbf{x},\ \mathrm{Im}\,\mathbf{x} "
            r"\text{ both solve it}",
            "formula",
        ),
        Note(
            "Euler's formula applies to the vector too",
            "This is the step people get wrong. The eigenvector has complex "
            "entries, so multiplying it by cos βt + i sin βt mixes real and "
            "imaginary parts together — you cannot take the real part of the "
            "exponential and leave the vector alone.",
            r"(\mathbf{p} + i\mathbf{q})(\cos\beta t + i\sin\beta t)",
            "pitfall",
        ),
        Note(
            "The real part decides in or out",
            "α is the whole story for stability: negative and the spiral "
            "winds in, positive and it winds out, zero and it closes into a "
            "centre. β only sets how fast it goes round, which no amount of "
            "watching will tell you about stability.",
            r"\alpha < 0 \text{ in},\quad \alpha > 0 \text{ out},\quad "
            r"\alpha = 0 \text{ a centre}",
            "idea",
        ),
        Note(
            "It is the underdamped case again",
            "A complex pair here is the same phenomenon as a complex pair of "
            "characteristic roots in Unit 4: oscillation inside an "
            "exponential envelope. The system view adds the direction of "
            "rotation, which the scalar equation could not show.",
            r"e^{\alpha t}(\cos\beta t, \sin\beta t)",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="Eigenvalues are −1 ± 3i. The origin is…",
            options=(
                "a stable spiral",
                "an unstable spiral",
                "a centre",
                "a saddle",
            ),
            answer=0,
            becauses=(
                "The real part is −1, so the amplitude decays; the imaginary "
                "part 3 makes it rotate on the way in. Winding inwards is a "
                "stable spiral.",
                "That would need a positive real part. This one is negative.",
                "A centre needs a real part of exactly zero, so that orbits "
                "close rather than shrinking.",
                "A saddle needs two real eigenvalues of opposite sign. "
                "Complex eigenvalues never give one.",
            ),
        ),
        Choice(
            key="q2",
            prompt="Why is the second (conjugate) eigenvalue not worked "
                   "through?",
            options=(
                "It has no eigenvector",
                "It gives the conjugate solution, which is no new information",
                "It is always zero",
                "It gives the same solution exactly",
            ),
            answer=1,
            becauses=(
                "It has one — the conjugate of the first eigenvector. That is "
                "the point.",
                "Conjugating the whole solution gives a solution whose real "
                "part is the same and whose imaginary part is negated. The "
                "two real solutions you would extract are the ones you "
                "already have.",
                "It is the conjugate of the first, which is zero only if the "
                "first is.",
                "Not exactly the same — it is the conjugate. But it spans the "
                "same two real solutions, which is why it adds nothing.",
            ),
        ),
        Choice(
            key="q3",
            prompt="x' = −y; y' = x describes…",
            options=(
                "decay to the origin",
                "growth away from the origin",
                "rotation on circles",
                "motion along a straight line",
            ),
            answer=2,
            becauses=(
                "Nothing decays: the eigenvalues are ±i with zero real part, "
                "so amplitude is preserved exactly.",
                "Nothing grows either, for the same reason.",
                "Eigenvalues ±i — a pure rotation with no envelope. x² + y² "
                "is constant along every trajectory, so the orbits are "
                "circles.",
                "Straight-line solutions need real eigenvectors, and there "
                "are none here — which is exactly what having no real "
                "eigenvalues means.",
            ),
        ),
        Solve(
            key="q4",
            prompt="A pure rotation.",
            equation="x' = -y; y' = x",
            hints=(
                "A = [[0, −1], [1, 0]] and det(A − λI) = λ² + 1.",
                "So λ = ±i — zero real part, meaning a centre.",
                "Take v·e^{it} for λ = i, multiply out with Euler's formula, "
                "and the real and imaginary parts are the cosine and sine "
                "solutions.",
            ),
        ),
        Solve(
            key="q5",
            prompt="A stable spiral.",
            equation="x' = -x - 2*y; y' = 2*x - x",
            hints=(
                "Simplify the second equation first: 2x − x is just x.",
                "The characteristic equation has a complex pair with negative "
                "real part, so expect a spiral winding inwards.",
                "Work through one eigenvalue only, then split the product "
                "into real and imaginary parts.",
            ),
        ),
    ),
)


REPEATED = Lesson(
    key="repeated-eigenvalues",
    title="Repeated eigenvalues and defective matrices",
    summary="When one eigenvalue has to supply two solutions and only "
            "provides one direction.",
    tool="steps",
    reference="Edwards 5.4",
    prerequisites=("eigenvalues",),
    objectives=(
        "Tell a defective matrix from a repeated eigenvalue that is not.",
        "Solve (A − λI)w = v for a generalised eigenvector.",
        "Write the second solution as (vt + w)e^{λt}.",
        "Say why the t appears, in terms of the equation rather than the "
        "formula.",
    ),
    examples=(
        Example(
            equation="x' = 3*x + y; y' = 3*y",
            narrator="systems",
            why="A double eigenvalue at 3 with only one eigenvector — the "
                "defective case. Watch the generalised eigenvector arrive, "
                "and the t with it.",
        ),
        Example(
            equation="x' = -x + y; y' = -y",
            narrator="systems",
            why="The same shape with a negative eigenvalue, so it decays. The "
                "t makes the solution rise before it falls, exactly as in the "
                "critically damped spring.",
        ),
    ),
    notes=(
        Note(
            "A repeated eigenvalue need not be defective",
            "Some matrices with a double eigenvalue still have two "
            "independent eigenvectors — the identity matrix is the extreme "
            "case, where every vector is one. Count the eigenvectors before "
            "assuming you need the generalised machinery.",
            r"\dim\ker(A - \lambda I) = 2 \;\Rightarrow\; \text{not defective}",
            "pitfall",
        ),
        Note(
            "Defective means short of directions",
            "When the multiplicity is two but the eigenspace is only "
            "one-dimensional, a single direction has to carry two independent "
            "solutions, and it cannot. That shortfall is the entire "
            "difficulty, and the generalised eigenvector is the repair.",
            r"\dim\ker(A - \lambda I) = 1 < 2",
        ),
        Note(
            "The generalised eigenvector",
            "Solve (A − λI)w = v rather than = 0. It is one step away from "
            "being an eigenvector: applying A − λI once lands you on v, and "
            "twice lands you on zero. Any solution will do, because they "
            "differ by multiples of v, which the first constant covers.",
            r"(A - \lambda I)\mathbf{w} = \mathbf{v}",
            "formula",
        ),
        Note(
            "Why the second solution needs a t",
            "Try w·e^{λt} alone and substituting gives λw·e^{λt} on the left "
            "and Aw·e^{λt} on the right, which do not match — Aw is λw + v, "
            "so there is a leftover v·e^{λt}. Adding vt·e^{λt} produces "
            "exactly that leftover when differentiated. The t is there to "
            "cancel something.",
            r"\mathbf{x}_2 = (\mathbf{v}t + \mathbf{w})e^{\lambda t}",
            "formula",
        ),
        Note(
            "It is the repeated root again",
            "This is the systems version of the repeated characteristic root "
            "and its extra factor of t. Same phenomenon, same repair, and the "
            "same picture: a degenerate node, where trajectories approach "
            "along one direction only.",
            r"(C_1 + C_2 t)e^{rt} \;\longleftrightarrow\; "
            r"(C_1\mathbf{v} + C_2(\mathbf{v}t + \mathbf{w}))e^{\lambda t}",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="λ = 5 has multiplicity 2 but only one eigenvector. You "
                   "need…",
            options=(
                "another eigenvalue",
                "a generalised eigenvector solving (A − 5I)w = v",
                "a complex eigenvector",
                "nothing more; one solution is enough",
            ),
            answer=1,
            becauses=(
                "There is no other eigenvalue — the multiplicity is two and "
                "it accounts for the whole matrix.",
                "Solving (A − λI)w = v gives the vector that supplies the "
                "second solution, (vt + w)e^{λt}. It is not an eigenvector, "
                "but it is one step from being one.",
                "The eigenvalue is real, so its eigenvectors are real too. "
                "Nothing complex enters this case.",
                "One solution cannot meet two independent initial conditions, "
                "so a 2×2 system needs two.",
            ),
        ),
        Choice(
            key="q2",
            prompt="Why does the second solution carry a factor of t?",
            options=(
                "By convention",
                "To cancel a leftover v·e^{λt} when differentiated",
                "To make it decay faster",
                "Because the eigenvalue is repeated, and repeated things get "
                "a t",
            ),
            answer=1,
            becauses=(
                "Nothing here is conventional — the t is forced by the "
                "equation, and leaving it out gives something that simply "
                "does not solve the system.",
                "Substituting w·e^{λt} leaves an unmatched v·e^{λt}, because "
                "Aw = λw + v. Differentiating vt·e^{λt} produces exactly that "
                "term, which is why w had to solve (A − λI)w = v.",
                "The t makes it grow relative to the plain exponential, not "
                "decay — though for a negative eigenvalue the exponential "
                "still wins in the end.",
                "True as a rule of thumb, and it is the same rule as the "
                "repeated characteristic root. But the reason underneath is "
                "the cancellation, which is what makes it a fact rather than "
                "a pattern.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Which matrix has a repeated eigenvalue but is NOT "
                   "defective?",
            options=(
                "[[3, 1], [0, 3]]",
                "[[3, 0], [0, 3]]",
                "[[0, 1], [0, 0]]",
                "[[2, 1], [0, 2]]",
            ),
            answer=1,
            becauses=(
                "λ = 3 twice, but A − 3I = [[0,1],[0,0]] has rank 1, so only "
                "one eigenvector. This one is defective.",
                "Three times the identity: A − 3I is the zero matrix, so "
                "*every* vector is an eigenvector and there are plenty. "
                "Repeated does not have to mean defective.",
                "λ = 0 twice, and A − 0I has rank 1, so one eigenvector. "
                "Defective.",
                "λ = 2 twice with the same shape as the first option. "
                "Defective.",
            ),
        ),
        Solve(
            key="q4",
            prompt="A defective matrix, growing.",
            equation="x' = 3*x + y; y' = 3*y",
            hints=(
                "A = [[3, 1], [0, 3]] is upper triangular, so the eigenvalues "
                "are on the diagonal: 3 twice.",
                "A − 3I = [[0, 1], [0, 0]], whose kernel is spanned by (1, 0) "
                "alone — one eigenvector for a double root.",
                "Solve (A − 3I)w = (1, 0) to get w = (0, 1), and the second "
                "solution is ((1,0)t + (0,1))e^{3t}.",
            ),
        ),
        Solve(
            key="q5",
            prompt="The same shape, decaying.",
            equation="x' = -x + y; y' = -y",
            hints=(
                "Upper triangular again, so λ = −1 twice.",
                "A + I = [[0, 1], [0, 0]] — one eigenvector, (1, 0).",
                "The t makes the first component rise before the e^{−t} "
                "pulls it back, which is what a degenerate node looks like.",
            ),
        ),
    ),
    templates=(
        Template(
            key="defective",
            title="A defective 2×2 system",
            prompt="One eigenvector short. Find the generalised one.",
            equation="x' = {a}*x + {b}*y; y' = {a}*y",
            narrator="systems",
            technique="systems",
            hints=(
                "The matrix is upper triangular, so both eigenvalues sit on "
                "the diagonal — read them straight off.",
                "Work out A − λI with λ = {a}. Its kernel is "
                "one-dimensional, which is what makes the matrix defective.",
                "Solve (A − λI)w = v for the generalised eigenvector, then "
                "write the second solution as (vt + w)·e^(λt).",
            ),
            slots=(("a", (1, 2, 3, -1, -2, -3)), ("b", (1, 2, 3))),
        ),
    ),
)


PORTRAITS = Lesson(
    key="phase-portraits",
    title="Phase portraits, and reading a system without solving it",
    summary="Everything the eigenvalues tell you about the picture, before "
            "any trajectory is drawn.",
    tool="steps",
    reference="Edwards 6.1–6.2",
    prerequisites=("eigenvalues", "complex-eigenvalues"),
    figure="eigenlines",
    objectives=(
        "Name the origin from the trace and determinant alone.",
        "Sketch the eigendirections and the flow along them.",
        "Say what changes as an eigenvalue crosses zero.",
        "Connect the classification to the damping regimes of Unit 4.",
    ),
    examples=(
        Example(
            equation="x' = x + 2*y; y' = 3*x + 2*y",
            narrator="systems",
            why="The saddle again, now for the picture rather than the "
                "formula: the two eigendirections are the only straight-line "
                "trajectories, and every other curve bends between them.",
        ),
        Example(
            equation="x' = -2*x + y; y' = x - 2*y",
            narrator="systems",
            why="A stable node. Both eigendirections point inwards, and "
                "trajectories arrive tangent to the slower one — which is the "
                "detail a formula never makes obvious.",
        ),
    ),
    notes=(
        Note(
            "Trace and determinant are enough",
            "For a 2×2 matrix the characteristic equation is "
            "λ² − (tr A)λ + det A = 0, so the two numbers decide everything. "
            "A negative determinant forces opposite signs and a saddle; a "
            "positive one with negative trace gives something stable.",
            r"\lambda^{2} - (\mathrm{tr}\,A)\lambda + \det A = 0",
            "formula",
        ),
        Note(
            "The discriminant decides node or spiral",
            "(tr A)² − 4 det A is the same discriminant as ever. Positive "
            "gives two real eigenvalues and a node or saddle; negative gives "
            "a complex pair and a spiral or centre; zero is the degenerate "
            "boundary between them.",
            r"(\mathrm{tr}\,A)^{2} - 4\det A",
            "formula",
        ),
        Note(
            "Trajectories arrive tangent to the slow direction",
            "In a stable node both directions decay, but one decays faster. "
            "Far out, the fast direction has already collapsed, so almost "
            "every trajectory comes in along the *slower* eigendirection. "
            "Expecting them to arrive along the faster one is the usual "
            "mistake.",
            r"|\lambda_{\text{slow}}| < |\lambda_{\text{fast}}|",
            "pitfall",
        ),
        Note(
            "It is the damping picture again",
            "Node, degenerate node, spiral, centre — these are overdamped, "
            "critically damped, underdamped and undamped, drawn in the phase "
            "plane instead of against time. The same discriminant crossing "
            "produces both.",
            r"b^{2}-4ac \;\longleftrightarrow\; (\mathrm{tr}\,A)^{2}-4\det A",
            "aside",
        ),
        Note(
            "The origin is the only equilibrium",
            "For x' = Ax with A invertible, Ax = 0 has only the zero "
            "solution, so the origin is the sole equilibrium. If det A = 0 "
            "there is a whole line of them, which is the degenerate case "
            "worth noticing rather than the one worth studying.",
            r"A\mathbf{x} = 0",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="det A < 0 for a 2×2 system. The origin is…",
            options=("a node", "a saddle", "a spiral", "a centre"),
            answer=1,
            becauses=(
                "A node needs both eigenvalues the same sign, so their "
                "product — the determinant — would be positive.",
                "The determinant is the product of the eigenvalues, so a "
                "negative one forces opposite signs. That is a saddle, and "
                "you know it without computing either eigenvalue.",
                "A spiral needs a complex pair, whose product is the squared "
                "modulus and therefore positive.",
                "A centre is a special spiral, so the same argument rules it "
                "out.",
            ),
        ),
        Choice(
            key="q2",
            prompt="tr A = −4, det A = 5. What is the origin?",
            options=(
                "a stable spiral",
                "an unstable spiral",
                "a stable node",
                "a saddle",
            ),
            answer=0,
            becauses=(
                "The discriminant is 16 − 20 = −4 < 0, so the eigenvalues are "
                "complex; their real part is tr A / 2 = −2 < 0, so it winds "
                "inwards.",
                "Winding outwards would need a positive trace.",
                "A node needs a non-negative discriminant. This one is "
                "negative, so the eigenvalues rotate rather than merely "
                "shrinking.",
                "A saddle needs a negative determinant, and this one is "
                "positive.",
            ),
        ),
        Choice(
            key="q3",
            prompt="In a stable node with eigenvalues −1 and −5, most "
                   "trajectories approach along…",
            options=(
                "the λ = −5 eigendirection",
                "the λ = −1 eigendirection",
                "a straight line between them",
                "neither; they spiral in",
            ),
            answer=1,
            becauses=(
                "The −5 component dies fastest, so it is the first thing to "
                "vanish — which is exactly why it does *not* dominate near "
                "the origin.",
                "e^{−5t} collapses long before e^{−t}, so close to the origin "
                "only the slow component is left and trajectories arrive "
                "tangent to its direction.",
                "The approach direction is one of the eigendirections, not "
                "some average of them.",
                "Spiralling needs complex eigenvalues; both of these are "
                "real.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Classify it, then confirm by solving.",
            equation="x' = x + 2*y; y' = 3*x + 2*y",
            hints=(
                "tr A = 3 and det A = 2 − 6 = −4. A negative determinant "
                "already tells you it is a saddle.",
                "The eigenvalues are 4 and −1, confirming opposite signs.",
                "The eigendirections are the two straight-line trajectories: "
                "outwards along the λ = 4 one, inwards along the other.",
            ),
        ),
        Solve(
            key="q5",
            prompt="A stable node, and the direction of approach.",
            equation="x' = -2*x + y; y' = x - 2*y",
            hints=(
                "tr A = −4, det A = 3, discriminant 16 − 12 = 4 > 0 — real "
                "eigenvalues, both negative.",
                "They are −1 and −3, so the slow direction is the λ = −1 one.",
                "That eigenvector is (1, 1), and almost every trajectory "
                "arrives tangent to it.",
            ),
        ),
    ),
)


NONHOMOGENEOUS = Lesson(
    key="forced-systems",
    title="Nonhomogeneous systems and the matrix exponential",
    summary="What to do when something is driving the system, and the one "
            "matrix that expresses the whole answer.",
    tool="steps",
    reference="Edwards 5.5–5.6",
    prerequisites=("eigenvalues", "variation"),
    objectives=(
        "Split a forced system into its matrix and its forcing.",
        "Build the fundamental matrix from the basis solutions.",
        "Find a particular solution by varying the constants.",
        "Say what e^{At} is, and why it is the natural fundamental matrix.",
    ),
    examples=(
        Example(
            equation="x' = x + 2*y + exp(t); y' = 3*x + 2*y",
            narrator="systems",
            why="The saddle from two lessons ago, now with something pushing "
                "on it. Watch the homogeneous work happen unchanged, and the "
                "forcing handled entirely afterwards.",
        ),
        Example(
            equation="x' = -2*x + y + 1; y' = x - 2*y",
            narrator="systems",
            why="Constant forcing on a stable node, which is the case with a "
                "constant particular solution — the system settles to a new "
                "equilibrium away from the origin rather than to zero.",
        ),
    ),
    notes=(
        Note(
            "Homogeneous first, forcing second",
            "The structure is the one every linear problem has: the general "
            "solution is the homogeneous family plus any one solution of the "
            "forced system. So none of the eigenvalue work is wasted — it is "
            "the first half of the answer, unchanged.",
            r"\mathbf{x} = \mathbf{x}_h + \mathbf{x}_p",
        ),
        Note(
            "The fundamental matrix",
            "Put the basis solutions in as columns. Φ(t) is invertible at "
            "every t precisely because those columns are independent, which "
            "is what the eigenvector work established — and everything below "
            "divides by it.",
            r"\Phi(t) = \big[\ \mathbf{x}_1 \ \ \mathbf{x}_2\ \big]",
            "formula",
        ),
        Note(
            "Vary the constants, again",
            "Replace the constant vector c by a function of t. Requiring "
            "Φc′ = f is what makes the derivative come out right, and it "
            "leaves c′ = Φ⁻¹f — one integral per constant. It is variation of "
            "parameters with the bookkeeping done by a matrix.",
            r"\mathbf{x}_p = \Phi(t)\int \Phi^{-1}(t)\,\mathbf{f}(t)\,dt",
            "formula",
        ),
        Note(
            "No constants when you integrate",
            "As in the scalar case: a constant of integration would only add "
            "a multiple of a basis solution back in, and the homogeneous part "
            "already carries every one of those with an arbitrary "
            "coefficient.",
            r"\int \Phi^{-1}\mathbf{f}\,dt \quad (\text{no } +\mathbf{c})",
            "pitfall",
        ),
        Note(
            "e^{At} is the fundamental matrix normalised at zero",
            "Any two fundamental matrices differ by a constant matrix on the "
            "right, so there is a whole family of them. The exponential is "
            "the one that is the identity at t = 0, which makes the answer to "
            "the homogeneous problem simply x(t) = e^{At}x(0) — the same "
            "shape as the scalar e^{at}y(0), and the reason it is written "
            "that way.",
            r"e^{At}\big|_{t=0} = I, \qquad \mathbf{x}(t) = "
            r"e^{At}\mathbf{x}(0)",
            "idea",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="For x′ = Ax + f, the general solution is…",
            options=(
                "any solution of x′ = Ax",
                "the homogeneous family plus one solution of the forced system",
                "any solution of x′ = Ax + f",
                "e^{At} times the forcing",
            ),
            answer=1,
            becauses=(
                "That solves the wrong equation — it ignores f entirely, and "
                "substituting it leaves f behind.",
                "The same structure as every linear problem: x_h carries the "
                "arbitrary constants and x_p accounts for the forcing. Both "
                "halves are needed, and neither alone is general.",
                "One solution of the forced system is *particular*, not "
                "general — it has no constants and so cannot meet an "
                "arbitrary initial condition.",
                "e^{At} solves the homogeneous system. Multiplying it by f is "
                "not a solution of anything in particular.",
            ),
        ),
        Choice(
            key="q2",
            prompt="What is Φ(t) built from?",
            options=(
                "the eigenvalues, down the diagonal",
                "the basis solutions, as columns",
                "the eigenvectors alone, as columns",
                "the forcing term",
            ),
            answer=1,
            becauses=(
                "A diagonal matrix of eigenvalues is A in a different basis, "
                "not a matrix of solutions. Φ has to solve the system column "
                "by column.",
                "Each column is one solution of x′ = Ax, so Φ′ = AΦ. Its "
                "determinant is non-zero for every t because the solutions "
                "are independent, which is what lets the formula divide by "
                "it.",
                "The eigenvectors are constant; the columns must be "
                "*functions* of t, so each carries its e^{λt} with it.",
                "Φ describes the system, not what is driving it. The forcing "
                "enters only in the integral.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Why is there no constant of integration in "
                   "∫Φ⁻¹f dt?",
            options=(
                "The integral is definite",
                "It would only re-add multiples of the basis solutions",
                "Φ⁻¹f always integrates to zero",
                "Constants are added at the end instead",
            ),
            answer=1,
            becauses=(
                "You may write it as a definite integral, but that is a "
                "choice of form; the reason the constant is harmless is the "
                "one below.",
                "A constant vector c₀ contributes Φc₀, which is exactly a "
                "combination of the basis solutions — and the homogeneous "
                "part already carries every one of those with an arbitrary "
                "coefficient.",
                "It does not. It integrates to whatever it integrates to, and "
                "that is the particular solution.",
                "The arbitrary constants are the homogeneous ones, and they "
                "were there before the integral was taken.",
            ),
        ),
        Choice(
            key="q4",
            prompt="What distinguishes e^{At} from any other fundamental "
                   "matrix?",
            options=(
                "It is the only invertible one",
                "It equals the identity at t = 0",
                "It is diagonal",
                "It is the only one whose columns solve the system",
            ),
            answer=1,
            becauses=(
                "Every fundamental matrix is invertible at every t — that is "
                "what makes it fundamental.",
                "Any two differ by a constant matrix on the right, so the "
                "family is large; e^{At} is the member normalised so that "
                "x(t) = e^{At}x(0) with no extra factor to work out.",
                "It is diagonal only when A is. For the saddle in this unit "
                "it is emphatically not.",
                "Every fundamental matrix has that property, by definition.",
            ),
        ),
        Solve(
            key="q5",
            prompt="A driven saddle.",
            equation="x' = x + 2*y + exp(t); y' = 3*x + 2*y",
            hints=(
                "Solve the homogeneous system first — it is the saddle from "
                "the eigenvalue lesson, with eigenvalues −1 and 4.",
                "Put the two basis solutions in as columns to get Φ(t), then "
                "form Φ⁻¹f with f = (eᵗ, 0).",
                "Integrate each entry, multiply back by Φ, and add the result "
                "to the homogeneous solution.",
            ),
        ),
    ),
)


LESSONS = (FIRSTORDER, DISTINCT, COMPLEX, REPEATED,
           NONHOMOGENEOUS, PORTRAITS)
