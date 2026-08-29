"""Unit 2 -- Models and numerical methods.

Edwards, Penney and Calvis 6e, chapter 2. Where the equations come from, and
what to do when none of the closed-form techniques applies -- which, outside a
textbook, is nearly always.

The population, equilibrium and acceleration-velocity lessons belong here and
arrive with the figures that make them worth reading; this unit currently
carries the numerical half, which is the part the Solver Studio already
supports end to end.
"""

from __future__ import annotations

from .model import Choice, Example, Lesson, Note

__all__ = ["NUMERICAL", "LESSONS"]


NUMERICAL = Lesson(
    key="numerical",
    title="Euler and Runge–Kutta",
    summary="What to do when there is no closed form — which is almost always.",
    tool="byhand",
    reference="Edwards 2.4–2.6",
    prerequisites=("separable",),
    objectives=(
        "Take an Euler step by hand, and say what it approximates.",
        "Read an order off a table of halved step sizes.",
        "Explain why four evaluations per step can still be cheaper than one.",
        "Say what stiffness costs a fixed-step explicit method.",
    ),
    examples=(
        Example(
            equation="y' = y",
            conditions="y(0) = 1",
            why="The one equation whose exact answer everybody knows, so the "
                "error in each step can be read directly rather than "
                "estimated. Solved here in closed form first — the numerical "
                "table is on Methods by Hand, beside this exact curve.",
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
            "Order: what halving h buys you",
            "Euler is first order — halve the step and the error roughly halves. "
            "That is a poor return: ten times the work for ten times the "
            "accuracy. The order is the exponent in the error, and it is what "
            "separates a usable method from a toy.",
            r"\text{error} \approx C h^{p}, \qquad p = 1 \text{ for Euler}",
        ),
        Note(
            "Runge–Kutta 4",
            "Instead of one slope, sample four across the step and take a "
            "weighted average — the midpoint slopes counting double. Four times "
            "the work per step, but fourth order: halve h and the error drops "
            "by sixteen.",
            r"y_{n+1} = y_n + \tfrac{h}{6}\left(k_1 + 2k_2 + 2k_3 + k_4\right)",
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
                "sixteenth means 2^p = 16, so p = 4 — the behaviour of RK4.",
                "Sixteen is the factor the error fell by, not the order. The "
                "order is the exponent p, and 2^p = 16 gives p = 4.",
            ),
        ),
        Choice(
            key="q3",
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


LESSONS = (NUMERICAL,)
