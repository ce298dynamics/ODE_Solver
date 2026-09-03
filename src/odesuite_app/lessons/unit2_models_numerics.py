"""Unit 2 -- Models and numerical methods.

Edwards, Penney and Calvis 6e, chapter 2. Where the equations come from, and
what to do when none of the closed-form techniques applies -- which, outside a
textbook, is nearly always.

Five lessons: where the equations come from -- populations, equilibria, and
motion under resistance -- and then the two methods a first course computes
with when none of chapter 1's techniques applies.
"""

from __future__ import annotations

from .model import Choice, Example, Lesson, Note, Solve, Template

__all__ = ["POPULATION", "EQUILIBRIA", "MOTION", "NUMERICAL",
           "RUNGEKUTTA", "LESSONS"]


POPULATION = Lesson(
    key="population",
    title="Population models and the logistic equation",
    summary="Where the first interesting nonlinear equation comes from, and "
            "what its two parameters mean.",
    tool="worked",
    reference="Edwards 2.1",
    prerequisites=("separable",),
    objectives=(
        "Write down exponential growth from a statement about a rate.",
        "Say what the logistic term does that exponential growth does not.",
        "Identify the carrying capacity from the equation.",
        "Solve a logistic equation and read its long-run behaviour off the "
        "answer.",
    ),
    examples=(
        Example(
            equation="y' = 0.5*y",
            conditions="y(0) = 10",
            why="The model in its simplest form: a rate proportional to the "
                "population. Unbounded growth, which is what makes it wrong "
                "for anything real and right as a starting point.",
        ),
        Example(
            equation="y' = 0.5*y*(1 - y/20)",
            conditions="y(0) = 2",
            why="The same growth rate with a ceiling. Watch the answer rise "
                "almost exponentially at first and then flatten — and notice "
                "the capacity, 20, appearing in the answer without having been "
                "put there by hand.",
        ),
    ),
    notes=(
        Note(
            "Proportional growth",
            "If every individual reproduces at the same rate, the total rate "
            "is proportional to the population. That single sentence is the "
            "equation, and separating gives the exponential everybody expects.",
            r"\frac{dP}{dt} = kP \;\Longrightarrow\; P = P_0 e^{kt}",
            "formula",
        ),
        Note(
            "Nothing grows exponentially for long",
            "Unbounded growth is a statement about unlimited food and space. "
            "The fix is to let the *per-capita* rate fall as the population "
            "rises: k(1 − P/K) instead of k. When P is small this is almost k, "
            "and at P = K it is zero.",
            r"\frac{dP}{dt} = kP\left(1 - \frac{P}{K}\right)",
            "formula",
        ),
        Note(
            "K is the carrying capacity",
            "P = K makes the right-hand side vanish, so it is a constant "
            "solution — and every solution starting below it rises towards it, "
            "while any starting above falls towards it. You can read that off "
            "the equation without solving anything.",
            r"P \equiv 0,\ P \equiv K \text{ are the constant solutions}",
        ),
        Note(
            "The equilibria are what separating loses",
            "Solving the logistic equation means dividing by P(1 − P/K), which "
            "assumes neither factor is zero. P ≡ 0 and P ≡ K are genuine "
            "solutions that no choice of constant recovers from the general "
            "formula.",
            "pitfall",
        ),
        Note(
            "Where the sigmoid comes from",
            "Partial fractions turn the integral into two logarithms, and "
            "rearranging gives the S-shaped curve. Its inflection is at K/2, "
            "which is the population growing fastest — a fact worth knowing "
            "and easy to check by differentiating twice.",
            r"P(t) = \frac{K}{1 + Ae^{-kt}}",
            "formula",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="In P' = 0.3P(1 − P/500), what is the carrying capacity?",
            latex=r"P' = 0.3P\left(1 - \frac{P}{500}\right)",
            options=("0.3", "150", "500", "It depends on P(0)"),
            answer=2,
            becauses=(
                "0.3 is k, the growth rate when the population is small. It "
                "sets how fast, not how far.",
                "150 is 0.3 × 500, which is the maximum *rate* of growth "
                "rather than the capacity — a real quantity, but not this one.",
                "P = 500 makes the bracket zero, so it is a constant solution "
                "and the level every other solution approaches.",
                "The capacity is a property of the equation, not of where you "
                "start. The initial value decides which curve, not where it "
                "ends up.",
            ),
        ),
        Choice(
            key="q2",
            prompt="A population starts above its carrying capacity. What "
                   "happens?",
            options=(
                "It grows without bound",
                "It falls towards the capacity",
                "It stays where it is",
                "It oscillates about the capacity",
            ),
            answer=1,
            becauses=(
                "Growth would need P' > 0. Above K the bracket 1 − P/K is "
                "negative and P is positive, so P' is negative.",
                "Above K the bracket is negative, so P' < 0 and the population "
                "falls — towards K, where it stops.",
                "It stays put only exactly at K. Anywhere above it, the "
                "right-hand side is nonzero and it moves.",
                "A first-order autonomous equation cannot oscillate: P' has "
                "one sign on each side of an equilibrium, so P moves one way "
                "and keeps going.",
            ),
        ),
        Solve(
            key="q3",
            prompt="Exponential growth. A rate proportional to the amount.",
            equation="y' = 0.4*y",
            conditions="y(0) = 25",
            hints=(
                "The right-hand side is a constant times y, which separates "
                "with f(t) = 0.4.",
                "dy/y = 0.4 dt, so ln|y| = 0.4t + C.",
                "y = Ae^{0.4t}, and y(0) = 25 makes A = 25.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Radioactive decay is the same model with k negative.",
            equation="y' = -0.05*y",
            conditions="y(0) = 200",
            hints=(
                "Same shape as growth, opposite sign — so expect a decaying "
                "exponential.",
                "Separate and integrate: ln|y| = −0.05t + C.",
                "y = 200e^{−0.05t}. Its half-life is ln 2 / 0.05 ≈ 13.9.",
            ),
        ),
        Solve(
            key="q5",
            prompt="The logistic equation itself, with capacity 10.",
            equation="y' = 0.5*y*(1 - y/10)",
            conditions="y(0) = 1",
            hints=(
                "Separable, but the y integral needs partial fractions: "
                "1/(y(1 − y/10)) splits into 1/y and something in 1 − y/10.",
                "Integrating gives ln|y| − ln|1 − y/10| = 0.5t + C, which is "
                "one logarithm of a ratio.",
                "Rearranged, y = 10/(1 + Ae^{−0.5t}), and y(0) = 1 makes "
                "A = 9.",
            ),
        ),
    ),
    templates=(
        Template(
            key="growth-decay",
            title="Proportional growth and decay",
            prompt="A rate proportional to the amount. Separate and integrate.",
            equation="y' = {k}*y/10",
            conditions="y(0) = {p}",
            technique="separable",
            hints=(
                "A constant times y is a product with f(t) = 1, so it "
                "separates immediately.",
                "dy/y integrates to ln|y|; the right side integrates to a "
                "multiple of t.",
                "Exponentiate, and the initial value is the coefficient in "
                "front — no further work needed.",
            ),
            slots=(("k", (-5, -2, -1, 1, 2, 5)), ("p", (10, 25, 100))),
        ),
        Template(
            key="logistic",
            title="Logistic growth towards a capacity",
            prompt="Separate, split into partial fractions, and rearrange.",
            equation="y' = y*(1 - y/{K})",
            conditions="y(0) = {p}",
            technique="separable",
            hints=(
                "Setting y' = 0 gives two constant solutions. Note them before "
                "dividing by anything, because dividing is what loses them.",
                "Separating leaves an integral in y that needs partial "
                "fractions: one piece in y, one in the bracket.",
                "Rearranging gives the S-shaped form, and the initial value "
                "fixes the constant inside it.",
            ),
            slots=(("K", (10, 20, 50)), ("p", (1, 2, 5))),
        ),
    ),
)


EQUILIBRIA = Lesson(
    key="equilibria",
    title="Equilibria, stability and the phase line",
    summary="For an autonomous equation, the sign of the right-hand side tells "
            "you everything about the long run.",
    tool="worked",
    reference="Edwards 2.2",
    prerequisites=("population",),
    figure="phase_line",
    objectives=(
        "Find the equilibria of an autonomous equation.",
        "Decide the stability of each from the sign of f on either side.",
        "Sketch a phase line and read the long-run behaviour off it.",
        "Use f′ at an equilibrium as a test, and say when it fails.",
    ),
    examples=(
        Example(
            equation="y' = y**2 - 4",
            conditions="y(0) = 1",
            why="Two equilibria, one stable and one not. Starting between them "
                "the solution falls towards −2, which the phase line predicts "
                "before any of the algebra happens.",
        ),
        Example(
            equation="y' = 4 - y",
            conditions="y(0) = 10",
            why="One equilibrium, and everything approaches it. The simplest "
                "case, and the one where the exponential in the answer is "
                "visibly the approach to y = 4.",
        ),
    ),
    notes=(
        Note(
            "Autonomous means t does not appear",
            "y' = f(y), with no explicit t. The slope then depends only on "
            "where you are, not when — so the whole picture can be collapsed "
            "onto a single axis, the phase line, and studied without solving.",
            r"y' = f(y)",
        ),
        Note(
            "Equilibria are the roots of f",
            "Wherever f(y₀) = 0, the constant function y ≡ y₀ is a solution. "
            "These are the only constant solutions, and they divide the line "
            "into intervals on which f keeps one sign.",
            r"f(y_0) = 0 \;\Longrightarrow\; y \equiv y_0",
            "formula",
        ),
        Note(
            "Stability is the sign on either side",
            "If f > 0 below an equilibrium and f < 0 above it, nearby "
            "solutions move towards it: stable. Both signs pointing away: "
            "unstable. One of each: semi-stable, approached from one side "
            "only.",
            r"f'(y_0) < 0 \Rightarrow \text{stable}, \qquad "
            r"f'(y_0) > 0 \Rightarrow \text{unstable}",
            "formula",
        ),
        Note(
            "Solutions cannot pass an equilibrium",
            "A solution starting between two equilibria stays between them "
            "forever. Crossing one would mean two solutions through the same "
            "point — the constant one and the crossing one — which uniqueness "
            "forbids. So monotone approach is the only option.",
        ),
        Note(
            "f′ = 0 decides nothing",
            "The derivative test is a shortcut, and it is silent when f′(y₀) "
            "is zero. y' = y² has an equilibrium at 0 with f′(0) = 0, and it "
            "is semi-stable: approached from below, fled from above. Go back "
            "to the signs of f itself.",
            r"y' = y^{2} \text{ at } y = 0",
            "pitfall",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="What are the equilibria of y' = y² − 4 ?",
            latex=r"y' = y^{2} - 4",
            options=("y = 4 only", "y = 2 only", "y = 2 and y = −2", "None"),
            answer=2,
            becauses=(
                "4 is the constant in the equation, not a root of it. Setting "
                "y² − 4 = 0 is what finds the equilibria.",
                "y = 2 is one of them, but y² − 4 factors as (y−2)(y+2) and "
                "the second root is just as real.",
                "y² − 4 = 0 has both roots, so there are two constant "
                "solutions and the line is divided into three intervals.",
                "There are equilibria wherever the right-hand side vanishes, "
                "and a quadratic vanishing is not unusual.",
            ),
        ),
        Choice(
            key="q2",
            prompt="For y' = y² − 4, which equilibrium is stable?",
            latex=r"y' = y^{2} - 4",
            options=(
                "y = 2",
                "y = −2",
                "Both",
                "Neither",
            ),
            answer=1,
            becauses=(
                "Just above 2, y² − 4 is positive, so solutions move further "
                "away. f′(2) = 4 > 0, which says the same thing.",
                "Between −2 and 2 the right-hand side is negative and below "
                "−2 it is positive, so both sides move towards −2. "
                "f′(−2) = −4 < 0 agrees.",
                "They cannot both be stable with nothing between them: on the "
                "middle interval f has one sign, so it points towards one and "
                "away from the other.",
                "One of them is: on the middle interval the arrows point down, "
                "and below −2 they point up.",
            ),
        ),
        Solve(
            key="q3",
            prompt="One equilibrium, and everything approaches it.",
            equation="y' = 4 - y",
            conditions="y(0) = 10",
            hints=(
                "y' = 0 at y = 4, and the sign of 4 − y says solutions above "
                "it fall and solutions below it rise.",
                "Separate: dy/(4 − y) = dt.",
                "y = 4 + Ae^{−t}, and y(0) = 10 makes A = 6 — the initial gap "
                "from the equilibrium, decaying.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Two equilibria. Starting between them, which way?",
            equation="y' = y**2 - 4",
            conditions="y(0) = 1",
            hints=(
                "At y = 1 the right-hand side is 1 − 4 = −3, so the solution "
                "starts falling and the phase line says it keeps falling "
                "towards −2.",
                "Separating needs partial fractions: 1/((y−2)(y+2)) splits "
                "into pieces in y − 2 and y + 2.",
                "The answer is a ratio of exponentials that tends to −2, which "
                "is what the phase line predicted before any of this.",
            ),
        ),
        Choice(
            key="q5",
            prompt="Why can a solution of an autonomous equation never "
                   "oscillate?",
            options=(
                "Because f does not depend on t",
                "Because between equilibria f keeps one sign, so y moves "
                "monotonically and cannot turn round",
                "Because the equation is first order",
                "It can — autonomous equations oscillate all the time",
            ),
            answer=1,
            becauses=(
                "That is the definition of autonomous rather than the reason, "
                "and it is not enough on its own: a two-dimensional autonomous "
                "system oscillates happily.",
                "Turning round would need y' to change sign, and y' = f(y) can "
                "only do that at a root of f — which is an equilibrium the "
                "solution cannot reach in finite time.",
                "Order alone is not the reason: y' = −y·sin t is first order "
                "and not autonomous, and it can turn round.",
                "Systems of them do. A single scalar autonomous equation "
                "cannot: it is monotone on each interval between equilibria.",
            ),
        ),
    ),
)


MOTION = Lesson(
    key="motion",
    title="Acceleration, velocity and drag",
    summary="Newton's second law is a differential equation, and the "
            "interesting part is what the resistance term does.",
    tool="worked",
    reference="Edwards 2.3",
    prerequisites=("linear",),
    objectives=(
        "Turn a statement of forces into a differential equation.",
        "Solve for velocity, then integrate again for position.",
        "Find a terminal velocity without solving anything.",
        "Say what changes when the drag is proportional to v² rather than v.",
    ),
    examples=(
        Example(
            equation="y' = -9.8 - 0.2*y",
            conditions="y(0) = 0",
            why="Falling with linear drag. The equation is linear in v, and "
                "the answer is an exponential approach to a terminal velocity "
                "you can read off the equation beforehand: −49.",
        ),
        Example(
            equation="y' = -9.8",
            conditions="y(0) = 20",
            why="The same problem with no resistance. One integration, a "
                "straight line, and no terminal velocity at all — which is "
                "what the drag term is there to fix.",
        ),
    ),
    notes=(
        Note(
            "F = ma is a differential equation",
            "Acceleration is the derivative of velocity, so a statement about "
            "forces is a statement about v′. Write down the forces, divide by "
            "the mass, and the equation is already there.",
            r"m\frac{dv}{dt} = \sum F",
            "formula",
        ),
        Note(
            "Two integrations, two constants",
            "Solve for v first, then integrate v to get position. Each "
            "integration brings a constant, so you need both an initial "
            "velocity and an initial position — which is the order-two count "
            "showing up in a problem written as two first-order steps.",
        ),
        Note(
            "Terminal velocity is an equilibrium",
            "With drag proportional to speed, v′ = −g − kv is autonomous, and "
            "its equilibrium is v = −g/k. That is the terminal velocity, and "
            "you get it by setting v′ = 0 rather than by solving anything.",
            r"v' = -g - kv = 0 \;\Longrightarrow\; v_\infty = -\frac{g}{k}",
            "formula",
        ),
        Note(
            "Which power of v the drag uses matters",
            "Linear drag −kv keeps the equation linear and gives an "
            "exponential approach. Quadratic drag −kv|v| is the realistic one "
            "at everyday speeds, and it is separable rather than linear, with "
            "a tanh in the answer instead of an exponential.",
            r"v' = -g - \frac{k}{m}v|v|",
            "aside",
        ),
        Note(
            "Signs are where these go wrong",
            "Pick a positive direction and keep it. If up is positive then "
            "gravity is −g, and the drag term opposes motion, so it is "
            "negative while rising and positive while falling. Writing −kv "
            "handles both automatically; writing −k|v| does not.",
            "pitfall",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="For v' = −9.8 − 0.2v, what is the terminal velocity?",
            latex=r"v' = -9.8 - 0.2v",
            options=("−9.8", "−49", "−0.2", "There is none"),
            answer=1,
            becauses=(
                "−9.8 is the acceleration due to gravity, which is the whole "
                "of v′ only at the instant v = 0.",
                "Setting v′ = 0 gives 0.2v = −9.8, so v = −49. No solving "
                "needed: the terminal velocity is the equilibrium.",
                "−0.2 is the drag coefficient. It has units of 1/time and is "
                "not a velocity at all.",
                "There is one, and it is what makes this model different from "
                "the drag-free case where the speed grows without bound.",
            ),
        ),
        Choice(
            key="q2",
            prompt="An object is dropped from rest with linear drag. How does "
                   "its speed behave?",
            options=(
                "It grows linearly forever",
                "It rises towards the terminal speed and never exceeds it",
                "It overshoots the terminal speed and comes back",
                "It is constant",
            ),
            answer=1,
            becauses=(
                "That is the drag-free answer. With drag, v′ shrinks as the "
                "speed rises, so the growth flattens.",
                "The equation is autonomous with a stable equilibrium at the "
                "terminal velocity, and a first-order autonomous equation "
                "approaches an equilibrium monotonically.",
                "Overshooting would need the speed to pass the equilibrium, "
                "and a solution cannot cross an equilibrium of a first-order "
                "autonomous equation.",
                "It is constant only if it starts at the terminal velocity. "
                "Dropped from rest, it starts at zero and accelerates.",
            ),
        ),
        Solve(
            key="q3",
            prompt="Falling with linear drag, from rest.",
            equation="y' = -9.8 - 0.2*y",
            conditions="y(0) = 0",
            hints=(
                "This is v′, not position. Before solving, note the "
                "equilibrium: v′ = 0 at v = −49.",
                "It is linear with p = 0.2, so μ = e^{0.2t} — or separate it, "
                "which works just as well.",
                "v = −49 + Ae^{−0.2t}, and v(0) = 0 makes A = 49.",
            ),
        ),
        Solve(
            key="q4",
            prompt="No resistance at all. One integration.",
            equation="y' = -9.8",
            conditions="y(0) = 20",
            hints=(
                "The right-hand side is a constant, so y is a straight line.",
                "Integrate once and use the initial value.",
                "y = 20 − 9.8t. Thrown upward at 20 m/s, it is momentarily at "
                "rest at t ≈ 2.04.",
            ),
        ),
        Choice(
            key="q5",
            prompt="Why is quadratic drag not solved the same way as linear "
                   "drag?",
            options=(
                "It is — the method is identical",
                "v² makes the equation nonlinear, so an integrating factor "
                "does not apply; it is separable instead",
                "Quadratic drag has no terminal velocity",
                "It needs a second-order equation",
            ),
            answer=1,
            becauses=(
                "The integrating factor needs the equation linear in v, and a "
                "v² term is exactly what breaks that.",
                "v′ = −g − kv² is autonomous and separable, and the integral "
                "gives an inverse tangent or an inverse hyperbolic tangent "
                "rather than a logarithm.",
                "It has one: setting v′ = 0 gives v = −√(g/k), which is the "
                "terminal velocity for that model.",
                "It is still first order in v. Nothing about the drag term "
                "changes the order.",
            ),
        ),
    ),
)


NUMERICAL = Lesson(
    key="numerical",
    title="Euler's method",
    summary="What to do when there is no closed form — which is almost always "
            "— starting with the simplest thing that could work.",
    tool="byhand",
    reference="Edwards 2.4–2.5",
    prerequisites=("basics", "separable"),
    figure="euler_error",
    objectives=(
        "Take an Euler step by hand, and say what it approximates.",
        "Explain where the error in one step comes from.",
        "Read an order off a table of halved step sizes.",
        "Say what stiffness costs a fixed-step explicit method.",
    ),
    examples=(
        Example(
            equation="y' = y",
            conditions="y(0) = 1",
            why="The one equation whose exact answer everybody knows, so the "
                "error in each step can be read directly rather than "
                "estimated. Solved here in closed form; the numerical table is "
                "on Methods by Hand, beside this exact curve.",
        ),
    ),
    notes=(
        Note(
            "Euler's method",
            "The equation tells you the slope at any point. So take the slope "
            "where you are, follow it for a short step h, and repeat. That is "
            "the whole idea, and every other method here is a refinement of it.",
            r"y_{n+1} = y_n + h\,f(t_n, y_n)",
            "formula",
        ),
        Note(
            "Following the slope field",
            "Geometrically, Euler's method walks along the slope field one "
            "segment at a time. The error is the gap between a chord and the "
            "curve it should be following: small over a short step, and "
            "accumulating over many.",
        ),
        Note(
            "Order: what halving h buys you",
            "Euler is first order — halve the step and the error roughly halves. "
            "That is a poor return: ten times the work for ten times the "
            "accuracy. The order is the exponent in the error, and it is what "
            "separates a usable method from a toy.",
            r"\text{error} \approx C h^{p}, \qquad p = 1 \text{ for Euler}",
        ),
        Note(
            "Local error and global error are different",
            "One Euler step is wrong by about h²; taking 1/h of them to cross "
            "a fixed interval leaves an error of about h. Losing a power that "
            "way is why a method's *order* is quoted globally, and why the "
            "per-step error is not the number that matters.",
            r"\text{local } O(h^{2}) \;\Longrightarrow\; \text{global } O(h)",
            "pitfall",
        ),
        Note(
            "Why anyone bothers with adaptive steps",
            "A fixed h is either too small where the solution is calm or too "
            "large where it turns sharply. Real solvers estimate the error each "
            "step and change h to match — which is what the Solver Studio "
            "shows you happening.",
            kind="aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="One Euler step on y' = y from y(0) = 1 with h = 0.1. "
                   "What is y₁?",
            latex=r"y' = y,\quad y(0) = 1,\quad h = 0.1",
            options=("1.0", "1.1", "1.105", "1.21"),
            answer=1,
            becauses=(
                "1.0 is y₀ — the step was never taken. Euler adds h·f to it.",
                "y₁ = y₀ + h·f(t₀,y₀) = 1 + 0.1·1 = 1.1. The true value is "
                "e^{0.1} ≈ 1.10517, so this one step is already short by "
                "about 0.005.",
                "1.105 is roughly the true e^{0.1}, which is what Euler is "
                "*approximating*. A single Euler step never lands on it — the "
                "gap between them is the error.",
                "1.21 is 1.1², which is where two steps of a different rule "
                "would take you. One step adds h·f exactly once.",
            ),
        ),
        Choice(
            key="q2",
            prompt="You halve h and the error drops to a sixteenth. What order "
                   "is the method?",
            options=("First", "Second", "Fourth", "Sixteenth"),
            answer=2,
            becauses=(
                "First order would halve the error when h halves, not divide "
                "it by sixteen.",
                "Second order would quarter it, not sixteenth it: halving h "
                "scales the error by 2^{−2} = 1/4.",
                "Error ≈ Ch^p, so halving h scales it by 2^{−p}. A "
                "sixteenth means 2^p = 16, so p = 4 — which is not Euler.",
                "Sixteen is the factor the error fell by, not the order. The "
                "order is the exponent p, and 2^p = 16 gives p = 4.",
            ),
        ),
        Choice(
            key="q3",
            prompt="Euler's local error per step is about h². Why is it called "
                   "a first-order method?",
            options=(
                "Because the equation is first order",
                "Because crossing a fixed interval takes about 1/h steps, so "
                "the accumulated error is about h",
                "Because h² is approximately h for small h",
                "Because it uses one function evaluation per step",
            ),
            answer=1,
            becauses=(
                "The order of a method and the order of an equation are "
                "unrelated: Euler is first order on a second-order system too.",
                "One step is wrong by about h², and there are about 1/h of "
                "them, so the errors accumulate to about h. The quoted order "
                "is the global one.",
                "h² is very much smaller than h for small h — that is the "
                "point of the exponent, not something to round away.",
                "One evaluation per step is true and is about cost, not "
                "accuracy. RK2 uses two and is second order; RK4 uses four and "
                "is fourth.",
            ),
        ),
        Choice(
            key="q4",
            prompt="Which is true of a fixed-step method on a stiff problem?",
            options=(
                "It is more accurate than an adaptive one",
                "h must stay small enough for stability even where the solution "
                "is barely changing",
                "Stiffness only affects implicit methods",
                "It cannot be used at all",
            ),
            answer=1,
            becauses=(
                "Accuracy is not the issue. An adaptive method is usually more "
                "accurate for the same work, because it spends its steps where "
                "they are needed.",
                "Stiffness is a stability constraint, not an accuracy one. "
                "An explicit method has to keep h inside its stability "
                "region no matter how flat the solution has become — which "
                "is exactly what makes stiff problems expensive.",
                "It is the other way round: implicit methods exist because "
                "their stability regions are large enough not to be "
                "constrained this way.",
                "It can be used — at a cost. That cost is the whole point of "
                "the topic, and the Stiffness Explorer shows it directly.",
            ),
        ),
    ),
)


RUNGEKUTTA = Lesson(
    key="rungekutta",
    title="Runge–Kutta, and what order buys",
    summary="Four slopes instead of one, and why that is cheaper rather than "
            "dearer.",
    tool="byhand",
    reference="Edwards 2.6",
    prerequisites=("numerical",),
    objectives=(
        "Say what the four stages of RK4 are averaging.",
        "Compare methods by evaluations rather than by steps.",
        "Measure an order from a table of halved step sizes.",
        "Say why a higher order is not always the right choice.",
    ),
    examples=(
        Example(
            equation="y' = -2*y",
            conditions="y(0) = 1",
            why="A decay whose exact answer is one exponential, so the "
                "measured error at each step size can be compared against "
                "h⁴ directly. Methods by Hand halves the step four times "
                "beside this curve and prints the ratios.",
        ),
    ),
    notes=(
        Note(
            "Sample the slope more than once",
            "Euler commits to the slope at the start of the step. Runge–Kutta "
            "samples several across it and takes a weighted average — the two "
            "midpoint slopes counting double, because the midpoint is where a "
            "single slope best represents the whole step.",
            r"y_{n+1} = y_n + \frac{h}{6}\left(k_1 + 2k_2 + 2k_3 + k_4\right)",
            "formula",
        ),
        Note(
            "The four stages",
            "k₁ is the slope at the start; k₂ at the midpoint, using k₁ to get "
            "there; k₃ at the midpoint again, using the better k₂; and k₄ at "
            "the far end, using k₃. Each one is an ordinary evaluation of f — "
            "there is nothing implicit anywhere.",
            r"k_1 = f(t_n, y_n), \quad k_2 = f(t_n + \frac{h}{2}, "
            r"y_n + \frac{h}{2}k_1)",
            "formula",
        ),
        Note(
            "Cost is evaluations, not steps",
            "Comparing methods by how many steps they take is the mistake this "
            "topic produces. RK4 costs four times as much per step; it wins "
            "anyway, because to reach an error ε it needs about ε^{−1/4} steps "
            "against Euler's ε^{−1}.",
            r"\text{Euler: } N \sim \varepsilon^{-1} \qquad "
            r"\text{RK4: } N \sim \varepsilon^{-1/4}",
            "pitfall",
        ),
        Note(
            "Measuring the order",
            "Halve h and watch the error. The ratio between successive errors "
            "is 2^p, so a column of ratios reading 16, 16, 16 is a "
            "fourth-order method telling you its order directly. That column "
            "is what Methods by Hand prints.",
            r"\frac{E(h)}{E(h/2)} \approx 2^{p}",
        ),
        Note(
            "Order is not the only thing",
            "A high-order method run at a step too large for its stability "
            "region diverges just as an Euler step does, and on a stiff "
            "problem RK4's advantage disappears entirely — the constraint "
            "there is stability, which order does nothing about.",
            kind="aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="Why does RK4 usually beat Euler even at equal *cost*?",
            options=(
                "It takes larger steps, so it needs fewer of them",
                "Four evaluations per step, but the error falls so much faster "
                "with h that far fewer steps are needed for a given accuracy",
                "It does not — Euler is cheaper per unit accuracy",
                "It avoids rounding error",
            ),
            answer=1,
            becauses=(
                "It does take larger steps for the same accuracy, but that is "
                "the consequence rather than the reason. The reason is the "
                "exponent in the error.",
                "Cost is evaluations, not steps. RK4 costs four times as "
                "much per step, but to get error ε it needs about ε^{−1/4} "
                "steps against Euler's ε^{−1}. At any accuracy worth having, "
                "RK4 wins by orders of magnitude.",
                "Euler is cheaper per *step*, which is a different quantity. "
                "Per unit of accuracy it loses badly, and by more the more "
                "accuracy you ask for.",
                "Both methods are limited by rounding eventually. RK4 reaches "
                "that floor sooner precisely because it is more accurate — "
                "avoiding rounding is not what makes it better.",
            ),
        ),
        Choice(
            key="q2",
            prompt="In RK4, why do k₂ and k₃ carry twice the weight of k₁ and "
                   "k₄?",
            options=(
                "Because they are computed second and third",
                "Because they are midpoint slopes, and the midpoint slope "
                "represents the whole step better than either end does",
                "Because they are larger",
                "The weights are arbitrary",
            ),
            answer=1,
            becauses=(
                "The order they are computed in is forced by the fact that "
                "each uses the last, and has nothing to do with the weights.",
                "It is Simpson's rule in disguise: weighting the middle twice "
                "as heavily as the ends is what makes the average accurate to "
                "fourth order rather than second.",
                "They are not systematically larger. All four are slopes of "
                "the same size, evaluated at different places.",
                "They are forced: matching the Taylor expansion of the true "
                "solution to fourth order determines them, and there is a "
                "whole family of such conditions.",
            ),
        ),
        Choice(
            key="q3",
            prompt="A table of halved step sizes shows error ratios of about "
                   "4, 4, 4. What order is the method?",
            options=("First", "Second", "Fourth", "Cannot be told"),
            answer=1,
            becauses=(
                "First order would show ratios of about 2 — halving h halving "
                "the error.",
                "The ratio is 2^p, so 2^p = 4 gives p = 2. Steady ratios "
                "across several halvings are what makes the measurement "
                "trustworthy.",
                "Fourth order would show ratios of about 16, which is what "
                "RK4 produces.",
                "It can, and the point of the table is that the order is "
                "measured rather than assumed — including when it disagrees "
                "with what the method claims.",
            ),
        ),
        Choice(
            key="q4",
            prompt="On a stiff problem, what happens to RK4's advantage over "
                   "Euler?",
            options=(
                "It grows, because RK4 is more accurate",
                "It largely disappears: both are explicit, so both are "
                "limited by stability rather than accuracy",
                "It is unchanged",
                "RK4 becomes unstable and Euler does not",
            ),
            answer=1,
            becauses=(
                "Accuracy is not the binding constraint on a stiff problem. "
                "Being more accurate does not help when the step size is "
                "capped by stability.",
                "Both are explicit, so both have a bounded stability region "
                "and both must keep h small no matter how flat the solution "
                "is. The extra order buys accuracy nobody needed.",
                "It is very much changed: the whole reason implicit methods "
                "exist is that raising the order of an explicit method does "
                "not solve stiffness.",
                "RK4's stability region is actually the larger of the two. "
                "Neither is remotely large enough for a stiff problem.",
            ),
        ),
    ),
)


LESSONS = (POPULATION, EQUILIBRIA, MOTION, NUMERICAL, RUNGEKUTTA)
