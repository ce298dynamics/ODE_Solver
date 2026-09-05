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

from .model import (
    Choice,
    Example,
    Lesson,
    Note,
    NumericTemplate,
    Passage,
    Solve,
    Template,
)

__all__ = ["FIRSTORDER", "DISTINCT", "COMPLEX", "REPEATED",
           "NONHOMOGENEOUS", "PORTRAITS", "LESSONS"]


FIRSTORDER = Lesson(
    key="systems-intro",
    title="First-order systems, and how everything becomes one",
    summary="Why a system is not two problems, and how a higher-order "
            "equation turns into one.",
    tool="steps",
    reference="Edwards 4.1",
    motivation=(
        "Every equation so far has had one unknown function. Very little in "
        "the world comes that way. Two tanks exchanging brine, two masses "
        "joined by a spring, a predator and its prey, the currents in two "
        "coupled loops — in each case there are two unknowns, and each one's "
        "rate of change depends on both.\n\n"
        "Coupling is what makes this genuinely new rather than two problems "
        "side by side. Neither equation can be solved first, because each "
        "needs the answer to the other. Substituting one into the other "
        "sometimes works and produces a single higher-order equation, but it "
        "is laborious and it fails as soon as there are three unknowns "
        "instead of two.\n\n"
        "What works instead is to stop treating the unknowns separately. "
        "Collect them into a vector and the coupling becomes a matrix, at "
        "which point the equation looks exactly like the very first one in "
        "the course — a rate proportional to the amount — and the whole of "
        "linear algebra is available to say what a matrix does. That change "
        "of viewpoint is the unit."
    ),
    derivation=(
        Passage(
            prose="Write the two equations with their unknowns collected on the right, "
                  "and notice that the coefficients form an array. Stacking the "
                  "unknowns into a column turns the pair into a single equation between "
                  "vectors.",
            latex=r"x_1' = a x_1 + b x_2, \quad x_2' = c x_1 + d x_2 "
                  r"\;\Longrightarrow\; \mathbf{x}' = A\mathbf{x}",
        ),
        Passage(
            prose="That form is worth staring at, because it is the equation the course "
                  "opened with. A rate proportional to the amount — only the constant "
                  "of proportionality is now a matrix, and the entire difficulty of "
                  "this unit is that multiplying by a matrix, unlike multiplying by a "
                  "number, changes direction as well as size.",
            latex=r"y' = ky \quad\longleftrightarrow\quad \mathbf{x}' = A\mathbf{x}",
        ),
        Passage(
            prose="The same form also swallows every higher-order equation met so far. "
                  "Name the derivatives as new unknowns: each one's rate is the next in "
                  "the list, and the equation itself supplies the last. No information "
                  "is added or lost.",
            latex=r"x_1 = y,\ x_2 = y' \;\Longrightarrow\; x_1' = x_2, \quad "
                  r"x_2' = -\frac{c}{a}x_1 - \frac{b}{a}x_2",
        ),
        Passage(
            prose="This is not a trick for exam questions, and it is worth saying why. "
                  "The vector of a solution's value and its derivative is precisely the "
                  "information needed to continue from an instant — it is the *state* — "
                  "which is exactly why an equation of order n takes n conditions. The "
                  "conversion turns one statement about that count into another.",
            latex=r"\text{order } n \;\Longleftrightarrow\; n \text{ "
                  r"components} \;\Longleftrightarrow\; n \text{ conditions}",
        ),
        Passage(
            prose="It also runs the other way, which is what makes the unit worth "
                  "learning rather than merely possible. Every numerical method in the "
                  "course was written for first-order equations, and every general "
                  "solver in existence takes a system — so converting is how a "
                  "fourth-order equation is handed to software that has never heard of "
                  "fourth-order equations.",
            latex=r"y^{(n)} = f\left(t, y, \ldots, y^{(n-1)}\right) "
                  r"\;\Longrightarrow\; \mathbf{x}' = \mathbf{F}(t, "
                  r"\mathbf{x})",
        ),
        Passage(
            prose="Superposition survives the move intact, since matrix multiplication "
                  "is linear. So the plan is the same as it was at second order: find "
                  "enough independent solutions, combine them with constants, and fit "
                  "the conditions. Only the meaning of *independent* needs restating, "
                  "and linear algebra has that word already.",
            latex=r"A(c_1\mathbf{x}_1 + c_2\mathbf{x}_2) = c_1 A\mathbf{x}_1 + "
                  r"c_2 A\mathbf{x}_2",
        ),
    ),
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
            commentary=(
                "Do the conversion by hand and keep track of what each row is saying. "
                "The first row is a definition — the second unknown *is* the "
                "derivative of the first — and only the second row carries any "
                "physics. That asymmetry is worth noticing, because it means the "
                "matrix produced this way always has the same shape whatever the "
                "equation.\n\n"
                "Then compute the eigenvalues of that matrix and set them beside the "
                "characteristic roots from the second-order unit. They are the same "
                "two numbers, and they must be: the determinant of A minus lambda I "
                "comes out as the characteristic polynomial itself. The eigenvalue "
                "method is not an alternative to that unit, it is the same "
                "computation with different notation around it."
            ),
        ),
        Example(
            equation="y'' + 4*y = 0",
            conditions="y(0) = 0, y'(0) = 2",
            why="An oscillator, whose system form has a complex pair of "
                "eigenvalues. Worth holding on to for the lesson on complex "
                "eigenvalues, where the same matrix reappears.",
            commentary=(
                "Convert this one too, and note that the matrix has zeros on its "
                "diagonal — nothing damps it, and each unknown drives only the other. "
                "That is a rotation written out, and it is worth recognising as such "
                "before any eigenvalue is computed.\n\n"
                "Then hold on to the matrix, because it returns in the lesson on "
                "complex eigenvalues and it is easier to meet twice than once. Its "
                "characteristic polynomial has no real roots at all, which for a "
                "single equation meant an oscillation. Here it will mean trajectories "
                "that go round the origin instead of into or away from it — the same "
                "fact about the same numbers, seen in the plane rather than against "
                "time."
            ),
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
            r"x_2' = -\frac{c}{a}x_1 - \frac{b}{a}x_2",
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
    motivation=(
        "The system is written as a matrix times a vector, and the difficulty "
        "is entirely that a matrix changes direction. Multiply a vector by a "
        "number and it stretches; multiply it by a matrix and it usually "
        "turns as well, so the neat exponential answer from the first lesson "
        "of the course has nothing obvious to attach itself to.\n\n"
        "Unless the direction happens to survive. For any matrix there are "
        "usually a few special directions that come back unturned — stretched "
        "perhaps, or reversed, but pointing the same way. Along one of those, "
        "the matrix *is* just a number, and the vector equation collapses to "
        "the scalar one the course began with.\n\n"
        "So the method is to look for solutions that keep a fixed direction "
        "and only change in length. That single guess turns the differential "
        "equation into an eigenvalue problem, which is a piece of linear "
        "algebra with nothing differential left in it — and after that the "
        "whole unit is bookkeeping."
    ),
    derivation=(
        Passage(
            prose="Guess a solution that never changes direction: a fixed vector whose "
                  "length is scaled by a function of time. Nothing about this is "
                  "arbitrary — it is the only shape for which multiplying by A can "
                  "possibly behave like multiplying by a number.",
            latex=r"\mathbf{x}(t) = \mathbf{v}\,f(t), \qquad \mathbf{v} \text{ fixed}",
        ),
        Passage(
            prose="Substitute it. The derivative touches only the scalar factor, and "
                  "the matrix touches only the vector, so the equation separates into a "
                  "statement that A applied to that vector must point along the vector "
                  "again — with the ratio of the two sides equal to the logarithmic "
                  "derivative of the scalar.",
            latex=r"\mathbf{v}f'(t) = f(t)\,A\mathbf{v}",
        ),
        Passage(
            prose="For that to hold at every instant, A applied to the vector must be a "
                  "constant multiple of it, and the scalar factor must satisfy the "
                  "simplest equation in the course. So the exponential comes back, and "
                  "the direction question is now pure linear algebra.",
            latex=r"A\mathbf{v} = \lambda\mathbf{v}, \qquad f' = \lambda f "
                  r"\;\Longrightarrow\; \mathbf{x} = \mathbf{v}e^{\lambda t}",
        ),
        Passage(
            prose="Finding those directions is the standard eigenvalue computation. A "
                  "non-zero vector sent to zero by a matrix exists exactly when that "
                  "matrix is singular, so the eigenvalues are the roots of a "
                  "determinant — and for a two-by-two system that determinant is a "
                  "quadratic, which is why this unit looks so much like the "
                  "second-order one.",
            latex=r"(A - \lambda I)\mathbf{v} = \mathbf{0},\ \mathbf{v} \neq "
                  r"\mathbf{0} \;\Longleftrightarrow\; \det(A - \lambda I) = 0",
        ),
        Passage(
            prose="Each eigenvector is determined only up to scale, and that is not a "
                  "defect. Rescaling it multiplies the solution by a constant, and a "
                  "constant is exactly what the general solution already carries — so "
                  "any convenient multiple may be taken, and choosing the one with "
                  "small integers in it is the only sensible thing to do.",
            latex=r"\mathbf{v} \to k\mathbf{v} \;\Longrightarrow\; "
                  r"c\,\mathbf{v}e^{\lambda t} \text{ unchanged in form}",
        ),
        Passage(
            prose="Distinct eigenvalues give independent eigenvectors, so two of them "
                  "give the general solution by superposition. The count matches: two "
                  "unknowns, two constants, two conditions — the same accounting as "
                  "everywhere else in the course.",
            latex=r"\mathbf{x} = c_1\mathbf{v}_1 e^{\lambda_1 t} + "
                  r"c_2\mathbf{v}_2 e^{\lambda_2 t}",
        ),
        Passage(
            prose="The geometry is worth reading off, because it is what a system "
                  "offers that a single equation does not. Starting exactly on an "
                  "eigenvector, the solution never leaves that line — the "
                  "eigendirections are the only straight-line trajectories there are. "
                  "Every other solution is a mix, and the sign of each eigenvalue says "
                  "whether its line runs in or out.",
            latex=r"\lambda_1 < 0 < \lambda_2 \;\Longrightarrow\; \text{one "
                  r"line in, one line out}",
        ),
    ),
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
            commentary=(
                "Compute the determinant and factor it before looking at the working. "
                "The two eigenvalues have opposite signs, and that alone settles the "
                "picture: one direction along which everything falls into the origin, "
                "one along which everything runs away, and no starting point except "
                "the origin itself that stays put.\n\n"
                "Then find each eigenvector and check it by multiplying rather than "
                "by trusting the algebra: A applied to it should come back as a plain "
                "multiple. Take whichever scaling makes the entries small integers, "
                "since the constant absorbs the choice. Starting exactly on either "
                "line, the solution stays on it forever — which is the geometric fact "
                "the closed form encodes and the reason these two lines organise the "
                "whole plane."
            ),
        ),
        Example(
            equation="x' = -2*x + y; y' = x - 2*y",
            narrator="systems",
            why="Both eigenvalues negative, so every trajectory runs into the "
                "origin — a stable node. Compare the picture with the saddle "
                "above; the algebra is identical and only the signs differ.",
            commentary=(
                "The algebra here is identical to the previous example and only the "
                "signs of the answers differ, which is exactly why the two are set "
                "together. Compute the eigenvalues and note that both are negative, "
                "so both directions run inwards and every trajectory reaches the "
                "origin.\n\n"
                "Then ask which of the two dominates, because that is the detail the "
                "formula hides. The term with the more negative eigenvalue dies "
                "first, so after a short while what is left is almost entirely the "
                "other one — every trajectory ends up nearly parallel to the *slower* "
                "eigendirection, whatever direction it set out in. That is the "
                "observation the phase portrait lesson is built on."
            ),
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
    figure="spiral",
    motivation=(
        "The eigenvalue method works whenever the eigenvalues are real and "
        "distinct. Nothing guarantees that. A matrix with entirely real "
        "entries can perfectly well have a characteristic polynomial with no "
        "real roots — the rotation that sends the first axis to the second is "
        "the simplest example, and there is no direction it leaves alone.\n\n"
        "Which is the point, geometrically. Real eigenvalues gave "
        "straight-line trajectories, and a system whose solutions circle the "
        "origin cannot have any. So the absence of real eigenvalues is not a "
        "defect of the method; it is the algebra reporting that the picture "
        "has no straight lines in it.\n\n"
        "The complex roots still work, and they still produce solutions. The "
        "only difficulty is that a real system with real initial data must "
        "have a real answer, so the complex exponentials have to be converted "
        "back — and the conversion is the same one the second-order unit "
        "used, applied now to a vector as well as to a scalar."
    ),
    derivation=(
        Passage(
            prose="A real matrix has a real characteristic polynomial, so complex roots "
                  "arrive in conjugate pairs — and the eigenvectors do too, since "
                  "conjugating the whole eigenvalue equation gives the conjugate one "
                  "back. Nothing has to be computed twice.",
            latex=r"A\mathbf{v} = \lambda\mathbf{v} \;\Longrightarrow\; "
                  r"A\overline{\mathbf{v}} = "
                  r"\overline{\lambda}\,\overline{\mathbf{v}}",
        ),
        Passage(
            prose="So one complex eigenvalue and its eigenvector give a solution in the "
                  "usual way. It is complex, so it is not the answer — but it does "
                  "satisfy the equation, and that is enough to extract two real "
                  "solutions from it.",
            latex=r"\mathbf{x}(t) = \mathbf{v}e^{\lambda t} \text{ solves } "
                  r"\mathbf{x}' = A\mathbf{x}",
        ),
        Passage(
            prose="Here is why. Split it into its real and imaginary parts and "
                  "substitute. Since A is real, applying it never mixes the two halves, "
                  "so the equation holds separately for each — and both halves are real "
                  "solutions of the original system.",
            latex=r"\mathbf{x} = \mathbf{p} + i\mathbf{q} \;\Longrightarrow\; "
                  r"\mathbf{p}' = A\mathbf{p}, \quad \mathbf{q}' = A\mathbf{q}",
        ),
        Passage(
            prose="Computing them means expanding the complex exponential, and the "
                  "pitfall is here: Euler's formula applies to the scalar factor, but "
                  "the *eigenvector* is complex too, so its real and imaginary parts "
                  "have to be separated as well. Both products contribute to both "
                  "halves.",
            latex=r"\left(\mathbf{a} + i\mathbf{b}\right)e^{\alpha "
                  r"t}\left(\cos\beta t + i\sin\beta t\right)",
        ),
        Passage(
            prose="Multiplying out and collecting gives the two real solutions. Each is "
                  "a combination of two fixed real vectors with a cosine and a sine, "
                  "wrapped in one exponential envelope — and the conjugate eigenvalue "
                  "produces nothing new, which is why only one of the pair is ever "
                  "used.",
            latex=r"\mathbf{p} = e^{\alpha t}\left(\mathbf{a}\cos\beta t - "
                  r"\mathbf{b}\sin\beta t\right)",
        ),
        Passage(
            prose="The geometry follows directly from the two parts of the root. The "
                  "imaginary part turns the solution round the origin, at a rate that "
                  "does not depend on where it started; the real part scales it, so the "
                  "sign of that part alone decides whether the spiral runs inwards or "
                  "outwards, and a zero real part gives closed loops.",
            latex=r"\alpha < 0 \text{ inwards}, \quad \alpha = 0 \text{ "
                  r"closed}, \quad \alpha > 0 \text{ outwards}",
        ),
        Passage(
            prose="Which is the underdamped spring of Unit 4 in a different picture. "
                  "There the real part was the decay of an envelope and the imaginary "
                  "part the frequency; here they are the tightening of a spiral and its "
                  "rate of turning. Same roots, same numbers, and the same equation "
                  "underneath.",
            latex=r"e^{\alpha t}\cos\beta t \quad\longleftrightarrow\quad "
                  r"\text{a spiral of rate } \alpha \text{ and turn } \beta",
        ),
    ),
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
            commentary=(
                "Look at the matrix before computing anything: each unknown drives "
                "the other and nothing drives itself. That is a rotation, and its "
                "eigenvalues have to be purely imaginary — a rotation leaves no "
                "direction fixed and changes no length, so the real part has nowhere "
                "to come from.\n\n"
                "Then check that what the derivation extracts is the obvious pair. "
                "With no envelope to complicate matters it produces a cosine in one "
                "component against a sine in the other, and the trajectory is a "
                "circle traced at constant speed. Every later example in this lesson "
                "is this one with an envelope on it, so it is worth being able to see "
                "this case without any algebra at all."
            ),
        ),
        Example(
            equation="x' = -x - 2*y; y' = 2*x - x",
            narrator="systems",
            why="A spiral rather than a circle: the real part of the "
                "eigenvalue is negative, so the rotation is inside a decaying "
                "envelope. Compare the answer with the underdamped spring "
                "from Unit 4 — it is the same shape.",
            commentary=(
                "Compute the eigenvalues and read the two parts separately. The real "
                "part is negative, so whatever happens is shrinking; the imaginary "
                "part is non-zero, so it is also turning. Those two facts fix the "
                "picture as an inward spiral before a single eigenvector has been "
                "found.\n\n"
                "Then do the comparison this example exists for. Take the answer's "
                "first component alone and set it beside the underdamped spring: a "
                "decaying exponential multiplying a combination of a cosine and a "
                "sine, with the same two numbers in the same two places. Watching one "
                "motion in time and one trajectory in the plane makes them look "
                "unrelated, and the algebra says they are the same thing."
            ),
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
    templates=(
        Template(
            key="spiral-system",
            title="A complex pair, back to real form",
            prompt="Find the eigenvalues, and give a real general solution.",
            equation="x' = {a}*x - {b}*y; y' = {b}*x + {a}*y",
            technique="systems",
            narrator="systems",
            hints=(
                "The characteristic polynomial has no real roots. Work out "
                "the pair anyway: it is {a} ± {b}i.",
                "Take the eigenvector for {a} + {b}i and form one complex "
                "solution. Its real and imaginary parts each solve the "
                "system, because the matrix is real.",
                "Both come out as e^({a}t) times a combination of cos {b}t "
                "and sin {b}t. The real part sets the envelope; the "
                "imaginary part sets how fast it turns.",
            ),
            # Neither may be 1: the hints say "e^(1t)" and "2 + 1i"
            # otherwise, and both read as generated rather than
            # written.
            slots=(("a", (-3, -2, 2, 3)), ("b", (2, 3, 4))),
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
    motivation=(
        "A two-by-two system needs two independent solutions, and the "
        "eigenvalue method supplies one per eigenvector. When the "
        "characteristic polynomial has a repeated root there may be only one "
        "direction to be had, and then the method has produced half an "
        "answer.\n\n"
        "It is worth being precise about when this actually happens, because "
        "the usual statement is too strong. A repeated eigenvalue does *not* "
        "mean a shortage of eigenvectors — a multiple of the identity has one "
        "eigenvalue twice and leaves every direction fixed, so it has as many "
        "independent eigenvectors as anyone could want. The trouble is a "
        "particular kind of matrix, not a particular kind of polynomial.\n\n"
        "When the shortage is real, the repair follows the second-order unit "
        "exactly. There a repeated characteristic root gave one exponential "
        "and the missing solution came with a factor of t; here the same "
        "factor appears, for the same reason, and the only new thing is that "
        "a vector has to come with it."
    ),
    derivation=(
        Passage(
            prose="First distinguish the two cases, since they look identical from the "
                  "polynomial. Solve for the eigenvectors of the repeated eigenvalue "
                  "and count them: if two independent ones exist there is no problem at "
                  "all and the previous lesson finishes the job.",
            latex=r"\dim\ker(A - \lambda I) = 2 \;\Longrightarrow\; \text{two "
                  r"eigenvectors, nothing new}",
        ),
        Passage(
            prose="The awkward case is a single line of eigenvectors where two "
                  "dimensions are needed. Such a matrix is called defective, and the "
                  "name is apt: the deficiency is in the matrix, and no amount of "
                  "cleverness will find a second straight-line solution that is not "
                  "there.",
            latex=r"\dim\ker(A - \lambda I) = 1 \;\text{ with } \lambda \text{ repeated}",
        ),
        Passage(
            prose="So look for the next simplest shape instead, taking the hint from "
                  "the second-order unit: an exponential multiplied by something linear "
                  "in t. Leave both vectors unknown and let the equation determine "
                  "them.",
            latex=r"\mathbf{x} = \left(\mathbf{w} + t\,\mathbf{v}\right)e^{\lambda t}",
        ),
        Passage(
            prose="Substitute and collect. The terms without a t and the terms with one "
                  "must balance separately, because a function and t times a function "
                  "cannot cancel each other at every instant. Two vector equations fall "
                  "out of one.",
            latex=r"\lambda\mathbf{w} + \mathbf{v} + \lambda t\mathbf{v} = "
                  r"A\mathbf{w} + t\,A\mathbf{v}",
        ),
        Passage(
            prose="The equation carrying the t says the second vector is an "
                  "eigenvector, which was already known. The other one is the new "
                  "content: it asks for a vector that A sends to the eigenvector rather "
                  "than to zero — one step further out than an eigenvector, which is "
                  "what *generalised* means.",
            latex=r"(A - \lambda I)\mathbf{v} = \mathbf{0}, \qquad (A - "
                  r"\lambda I)\mathbf{w} = \mathbf{v}",
        ),
        Passage(
            prose="Such a vector exists precisely when the matrix is defective, which "
                  "is the tidy part of the story: the same shortage that removed the "
                  "second eigenvector is what makes the second equation solvable. It is "
                  "determined only up to adding a multiple of the eigenvector, and that "
                  "freedom changes the answer by a multiple of the first solution — "
                  "already in the family.",
            latex=r"\mathbf{w} \to \mathbf{w} + k\mathbf{v} "
                  r"\;\Longrightarrow\; \mathbf{x} \to \mathbf{x} + "
                  r"k\mathbf{v}e^{\lambda t}",
        ),
        Passage(
            prose="So the factor of t appears here for exactly the reason it appeared "
                  "at second order — a solution is missing and this is the next shape "
                  "available — and it has the same effect on the motion. Against a "
                  "decaying exponential it makes the solution grow before it falls, "
                  "which is the critically damped spring, drawn in the plane.",
            latex=r"\mathbf{x} = c_1\mathbf{v}e^{\lambda t} + "
                  r"c_2\left(\mathbf{w} + t\mathbf{v}\right)e^{\lambda t}",
        ),
    ),
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
            commentary=(
                "Confirm the shortage rather than assuming it. The eigenvalue is "
                "repeated, but that alone decides nothing — solve for the "
                "eigenvectors and count the independent ones. Here there is a single "
                "line of them where two dimensions are needed, and that is what makes "
                "the extra machinery necessary.\n\n"
                "Then watch the generalised vector being found. It solves a system "
                "whose matrix is singular, so it is not unique, and any choice "
                "differing by a multiple of the eigenvector is as good — the "
                "difference is absorbed into the first constant. This is a place "
                "where two people's answers can look unlike each other and both be "
                "right, which is worth seeing once."
            ),
        ),
        Example(
            equation="x' = -x + y; y' = -y",
            narrator="systems",
            why="The same shape with a negative eigenvalue, so it decays. The "
                "t makes the solution rise before it falls, exactly as in the "
                "critically damped spring.",
            commentary=(
                "The structure is the same as the previous example and only the sign "
                "of the eigenvalue has changed, so run the same check and then read "
                "what the sign does. Everything decays now, and the question is what "
                "the extra factor does on the way.\n\n"
                "The extra factor pushes the trajectory outward first. A t against a "
                "decaying exponential has a single maximum, so a start off the "
                "eigendirection moves *away* from the origin for a while before "
                "turning back — which is the same algebra that gives a critically "
                "damped spring its detour on the way to rest."
            ),
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
    motivation=(
        "The eigenvalue method produces a formula, and a formula for a system "
        "is harder to read than a formula for a single equation. Two "
        "components, each a combination of two exponentials with vector "
        "coefficients: it is correct, and almost nothing about the behaviour "
        "is visible in it.\n\n"
        "What is wanted is the picture — not the two components against time, "
        "but the path traced in the plane they live in. A trajectory shows "
        "the whole history at once, and a sketch of several of them shows "
        "what happens from every possible start, which is the question a "
        "designer actually asks.\n\n"
        "The remarkable thing is how little that picture costs. Not the "
        "eigenvectors, not even the eigenvalues — two numbers taken straight "
        "from the matrix are enough to classify it completely, because those "
        "two numbers determine the characteristic polynomial and therefore "
        "everything that follows from it."
    ),
    derivation=(
        Passage(
            prose="Expand the characteristic determinant for a two-by-two matrix and "
                  "look at what the coefficients actually are. The linear one is the "
                  "sum of the diagonal and the constant one is the determinant — so the "
                  "polynomial depends on the matrix only through those two numbers.",
            latex=r"\det(A - \lambda I) = \lambda^{2} - \tau\lambda + \Delta, "
                  r"\qquad \tau = \operatorname{tr}A, \;\; \Delta = \det A",
        ),
        Passage(
            prose="Everything about the solutions comes from the eigenvalues, and the "
                  "eigenvalues come from that polynomial, so the entire classification "
                  "is a statement about two numbers. Two quite different-looking "
                  "matrices with the same trace and determinant have qualitatively "
                  "identical portraits.",
            latex=r"\lambda = \frac{\tau \pm \sqrt{\tau^{2} - 4\Delta}}{2}",
        ),
        Passage(
            prose="Take the determinant first. It is the product of the eigenvalues, so "
                  "a negative determinant forces them to have opposite signs — one "
                  "direction in, one out, and every other trajectory sweeping past the "
                  "origin. That is a saddle, and it is settled by the sign of one "
                  "number.",
            latex=r"\Delta < 0 \;\Longrightarrow\; \lambda_1 < 0 < \lambda_2 "
                  r"\;\;\text{(saddle)}",
        ),
        Passage(
            prose="With a positive determinant the eigenvalues share a sign, and the "
                  "trace — their sum — says which. Negative trace means everything runs "
                  "in, positive means everything runs out. Stability is decided by two "
                  "signs, with no eigenvalue computed.",
            latex=r"\Delta > 0: \quad \tau < 0 \text{ stable}, \qquad \tau > 0 "
                  r"\text{ unstable}",
        ),
        Passage(
            prose="Whether it is a node or a spiral is the discriminant, which is the "
                  "same quantity that separated overdamped from underdamped in Unit 4 — "
                  "and it is the same statement, since that unit's equation converts to "
                  "a system whose trace and determinant are its damping and stiffness.",
            latex=r"\tau^{2} - 4\Delta > 0 \text{ node}, \qquad \tau^{2} - "
                  r"4\Delta < 0 \text{ spiral}",
        ),
        Passage(
            prose="For a node the eigendirections do more than sit there. The faster "
                  "exponential dies first, so after a short time every trajectory is "
                  "dominated by the slower one — which means they all arrive at the "
                  "origin tangent to the slow eigendirection, whatever direction they "
                  "set off in. That detail is invisible in the formula and obvious in "
                  "the picture.",
            latex=r"\left|\lambda_1\right| < \left|\lambda_2\right| "
                  r"\;\Longrightarrow\; \text{tangent to } \mathbf{v}_1",
        ),
        Passage(
            prose="One last thing worth noticing about all these pictures: the origin "
                  "is the only place where nothing moves. A linear system has exactly "
                  "one equilibrium unless the matrix is singular, so the whole portrait "
                  "is organised around a single point — which is precisely what stops "
                  "being true the moment the system is nonlinear.",
            latex=r"A\mathbf{x} = \mathbf{0},\ \det A \neq 0 "
                  r"\;\Longrightarrow\; \mathbf{x} = \mathbf{0}",
        ),
    ),
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
            commentary=(
                "Classify it from the trace and the determinant alone, without "
                "touching an eigenvalue. The determinant is negative, so the "
                "eigenvalues have opposite signs and the picture is settled — one "
                "line in, one line out. Two arithmetic operations have replaced the "
                "whole computation.\n\n"
                "Then find the eigendirections and note what they organise. They "
                "divide the plane into four regions, and no trajectory can cross "
                "either line, because a solution starting on one stays on it and two "
                "solutions cannot meet. So a trajectory's region is decided at the "
                "start and never changes, which is why the picture looks the way it "
                "does."
            ),
        ),
        Example(
            equation="x' = -2*x + y; y' = x - 2*y",
            narrator="systems",
            why="A stable node. Both eigendirections point inwards, and "
                "trajectories arrive tangent to the slower one — which is the "
                "detail a formula never makes obvious.",
            commentary=(
                "Run the same two checks. The determinant is positive, so the "
                "eigenvalues share a sign; the trace is negative, so that sign is "
                "negative and everything runs inwards. Then take the discriminant to "
                "separate node from spiral — it is positive here, so the trajectories "
                "arrive without turning.\n\n"
                "Then look for the detail this example is set for. The two "
                "eigenvalues are not equal, so one term dies faster, and near the "
                "origin every trajectory is almost entirely the slower one — they all "
                "come in tangent to that direction and only the two straight-line "
                "solutions do anything else. No amount of staring at the closed form "
                "suggests it, and the picture makes it unmistakable."
            ),
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
    templates=(
        NumericTemplate(
            key="determinant-decides",
            title="The determinant, and what it settles",
            prompt="For the system x' = {a}*x + {b}*y, y' = {c}*x + {d}*y, "
                   "what is the determinant of its matrix?",
            answer="{a}*{d} - {b}*{c}",
            because="It is the product of the eigenvalues, so its sign alone "
                    "decides whether they share one: negative means opposite "
                    "signs, which is a saddle. No eigenvalue has to be found.",
            latex=r"\Delta = \det A = ad - bc",
            hints=(
                "The matrix has the coefficients of x along the top row and "
                "the coefficients of y down the second column.",
                "For a two-by-two matrix the determinant is the product of "
                "the diagonal minus the product of the other two.",
            ),
            # No zero entries. `tidy` clears "1*x" and "+ -y" but will not
            # drop a term, and rightly so -- "0*x" would have to disappear
            # rather than be tidied, which is a different claim about the
            # equation.
            slots=(("a,b", ((1, 2), (-2, 1), (3, -1), (2, 3))),
                   ("c,d", ((3, 2), (1, -2), (1, 1), (-1, 2)))),
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
    motivation=(
        "Everything in this unit so far has had nothing on the right-hand "
        "side, and the same objection applies as at second order: an unforced "
        "system is a system with nothing happening to it. Real ones have "
        "inflows, applied voltages, injected currents — a vector of things "
        "pushing on them, which may depend on time.\n\n"
        "The structure carries over unchanged, because it only ever depended "
        "on linearity. One particular solution plus the homogeneous family is "
        "still the general answer, so all the eigenvalue work stays and the "
        "only new question is how to find a single particular solution.\n\n"
        "Variation of parameters answers it, and the matrix setting turns out "
        "to be *tidier* than the scalar one. There the method needed a "
        "determinant and two sign-carrying integrals; here it is one matrix "
        "inverse and one integral, and the awkward chosen condition of the "
        "scalar derivation is not needed at all."
    ),
    derivation=(
        Passage(
            prose="Collect the homogeneous solutions as the columns of a matrix. Each "
                  "column satisfies the system, so the matrix satisfies it as a whole — "
                  "and its determinant is non-zero exactly when the solutions are "
                  "independent, which is the Wronskian idea in matrix form.",
            latex=r"\Phi(t) = \left[\ \mathbf{x}_1 \ \ \mathbf{x}_2\ \right], "
                  r"\qquad \Phi' = A\Phi",
        ),
        Passage(
            prose="The homogeneous family is then that matrix times a constant vector, "
                  "which is a tidier way of writing a combination with two constants in "
                  "it. Fitting initial conditions becomes solving one linear system.",
            latex=r"\mathbf{x}_h = \Phi(t)\,\mathbf{c}",
        ),
        Passage(
            prose="Now vary the constants, exactly as at second order: let the constant "
                  "vector depend on t and substitute. The product rule gives two terms, "
                  "and the first cancels against the right-hand side because the matrix "
                  "already solves the homogeneous system.",
            latex=r"\left(\Phi\mathbf{u}\right)' = \Phi'\mathbf{u} + "
                  r"\Phi\mathbf{u}' = A\Phi\mathbf{u} + \Phi\mathbf{u}'",
        ),
        Passage(
            prose="What is left is one equation for the derivative of the varying "
                  "vector, and it needs no chosen side condition — the scalar "
                  "derivation had to invent one because it had two unknown functions "
                  "and one equation, and here the count already matches.",
            latex=r"\Phi\,\mathbf{u}' = \mathbf{f}(t) \;\Longrightarrow\; "
                  r"\mathbf{u}' = \Phi^{-1}\mathbf{f}",
        ),
        Passage(
            prose="Integrate and multiply back. That is the whole formula, and it is "
                  "shorter than the scalar one it generalises — the determinant in the "
                  "denominator there is the matrix inverse here, and the two minus "
                  "signs are the two entries of the adjugate.",
            latex=r"\mathbf{x}_p = \Phi(t)\int \Phi^{-1}(t)\,\mathbf{f}(t)\,dt",
        ),
        Passage(
            prose="No constant is added at that integration, for the reason it never "
                  "is: a constant vector there contributes the matrix times a constant "
                  "vector, which is a homogeneous solution and already in the family.",
            latex=r"\int \to \int + \mathbf{k} \;\Longrightarrow\; "
                  r"\mathbf{x}_p + \Phi\mathbf{k}",
        ),
        Passage(
            prose="One normalisation is worth naming. Any fundamental matrix may be "
                  "multiplied on the right by a constant invertible matrix and still be "
                  "one, so there is a choice — and choosing the one that is the "
                  "identity at time zero gives the matrix exponential. With that choice "
                  "the solution of the unforced system is that matrix applied to the "
                  "starting vector, which is the first equation of the course with a "
                  "matrix in the exponent.",
            latex=r"\left.e^{At}\right|_{t=0} = I, \qquad \mathbf{x}(t) = e^{At}\mathbf{x}(0)",
        ),
    ),
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
            commentary=(
                "The homogeneous half is a saddle already solved two lessons ago, so "
                "lift it rather than redoing it, and assemble the two solutions into "
                "the columns of a matrix. Everything after that point is the forcing, "
                "and watching where the two halves separate is the point of this "
                "example.\n\n"
                "Then look at the forcing's exponent against the eigenvalues. It "
                "matches neither, so nothing resonates and the particular solution is "
                "an ordinary exponential — had it matched, the integral would have "
                "produced a logarithm or a factor of t, which is the same collision "
                "the undetermined-coefficients lesson described, arriving here as an "
                "integral that changes character."
            ),
        ),
        Example(
            equation="x' = -2*x + y + 1; y' = x - 2*y",
            narrator="systems",
            why="Constant forcing on a stable node, which is the case with a "
                "constant particular solution — the system settles to a new "
                "equilibrium away from the origin rather than to zero.",
            commentary=(
                "Constant forcing is the case worth doing by hand as well as by "
                "formula. Look for a constant solution: its derivative vanishes, so "
                "it solves an ordinary linear system with no calculus in it, and the "
                "answer is a fixed point away from the origin.\n\n"
                "That is where the system now settles, and the reason is the "
                "eigenvalues rather than the forcing. Both are negative, so the "
                "homogeneous part dies and only the constant survives — the "
                "trajectory ends at the new fixed point from wherever it began. Move "
                "the forcing and the destination moves; change the matrix and the "
                "whole picture may stop settling at all."
            ),
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
            r"\Phi(t) = \left[\ \mathbf{x}_1 \ \ \mathbf{x}_2\ \right]",
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
            r"\left.e^{At}\right|_{t=0} = I, \qquad \mathbf{x}(t) = "
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
    templates=(
        Template(
            key="constant-forcing",
            title="A stable system pushed off the origin",
            prompt="Solve the homogeneous system first, then the forcing.",
            equation="x' = -2*x + y + {f}; y' = x - 2*y",
            conditions="x(0) = {p}, y(0) = 0",
            technique="systems",
            narrator="systems",
            hints=(
                "The matrix has eigenvalues −1 and −3, so the homogeneous "
                "part dies and the answer settles somewhere.",
                "The forcing is constant, so look for a constant particular "
                "solution: its derivative is zero, which leaves an ordinary "
                "linear system with no calculus in it.",
                "Add the homogeneous family to that constant, then use "
                "x(0) = {p} and y(0) = 0 to fix the two constants.",
            ),
            slots=(("f", (1, 2, 3)), ("p", (0, 1, 2))),
        ),
    ),
)


LESSONS = (FIRSTORDER, DISTINCT, COMPLEX, REPEATED,
           NONHOMOGENEOUS, PORTRAITS)
