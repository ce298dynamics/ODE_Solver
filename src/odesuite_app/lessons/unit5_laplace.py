"""Unit 5 -- Laplace transforms.

Edwards, Penney and Calvis 6e, chapter 7. The one technique in a first course
that turns the equation into algebra, and the only one that copes with forcing
switched on partway through or delivered as an impulse.

The transform table, the shifting theorems, convolution, and the step and
impulse lessons belong here in full; this unit currently carries the lesson on
solving initial value problems, which is the one the Laplace screen already
narrates end to end.
"""

from __future__ import annotations

from .model import Choice, Example, Lesson, Note, Solve

__all__ = ["LAPLACE", "LESSONS"]


LAPLACE = Lesson(
    key="laplace",
    title="Laplace transforms",
    summary="Turn the differential equation into algebra — and handle forcing "
            "that switches on partway through.",
    tool="laplace",
    reference="Edwards 7.1–7.6",
    prerequisites=("roots", "undetermined"),
    objectives=(
        "Transform a derivative, and place the initial conditions where they "
        "actually enter.",
        "Solve the transformed equation for Y(s) — it is only algebra.",
        "Split Y(s) into pieces that match rows of the table, and invert them.",
        "Handle a forcing term that switches on at t = a, using the second "
        "shifting theorem.",
    ),
    examples=(
        Example(
            equation="y'' + 3*y' + 2*y = sin(t)",
            conditions="y(0) = 1, y'(0) = 0",
            narrator="laplace",
            why="Smooth forcing and nonzero conditions — the case that shows "
                "the conditions entering at the *start*, through the transform "
                "of y'', rather than arriving at the end as constants to pin.",
        ),
        Example(
            equation="y' + y = Heaviside(t - 2)",
            conditions="y(0) = 0",
            narrator="laplace",
            why="A switch thrown at two seconds. Not separable, no integrating "
                "factor worth writing, and not what undetermined coefficients "
                "is for — this is the problem the transform exists for.",
        ),
    ),
    notes=(
        Note(
            "What it does",
            "The transform turns a function of t into a function of s, and — "
            "this is the point — it turns differentiation into multiplication. "
            "A differential equation becomes an algebraic one, which you solve "
            "with ordinary algebra and then transform back.",
            r"\mathcal{L}\{y'\} = sY(s) - y(0)",
            "formula",
        ),
        Note(
            "The initial conditions come in at the start",
            "Look at where y(0) appears: in the transform of the derivative "
            "itself. No arbitrary constants are ever introduced, so there is "
            "nothing to pin down at the end. This is the real difference from "
            "every other method here.",
            r"\mathcal{L}\{y''\} = s^{2}Y(s) - s\,y(0) - y'(0)",
            "formula",
        ),
        Note(
            "y(0) carries the s, y'(0) does not",
            "In s²Y − s·y(0) − y'(0) the two conditions enter differently, and "
            "swapping them is the mistake this topic produces. Count powers: "
            "the term that came from differentiating twice keeps one factor of "
            "s for the condition it consumed first.",
            r"\mathcal{L}\{y''\} = s^{2}Y - s\,y(0) - y'(0)",
            "pitfall",
        ),
        Note(
            "Getting back",
            "Solve for Y(s), split it into partial fractions until every piece "
            "matches a row of the table, and read each one backwards. Partial "
            "fractions exist in this subject for exactly this purpose.",
            r"Y(s) = \frac{1}{(s+1)(s+2)} = \frac{1}{s+1} - \frac{1}{s+2}",
        ),
        Note(
            "Why it is worth the trouble: switches and impulses",
            "A step u(t−a) transforms to e^{−as}/s and an impulse δ(t−a) to "
            "e^{−as}. Neither is something separation, integrating factors or "
            "undetermined coefficients can handle at all — a switch thrown at "
            "t = 2 has no shape to guess. Here it is one more factor.",
            r"\mathcal{L}\{u(t-a)g(t-a)\} = e^{-as}G(s)",
            "formula",
        ),
        Note(
            "The transform integrates from zero",
            "Every condition has to be given at t = 0. A condition at t = 1 "
            "cannot be used at all — not because the algebra is harder, but "
            "because the transform never sees the interval it applies to. "
            "Restate the problem before transforming.",
            r"\mathcal{L}\{f\}(s) = \int_{0}^{\infty} e^{-st} f(t)\,dt",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="What is L{y''} for an equation with y(0) = 2, y'(0) = 0 ?",
            options=(
                r"s^{2}Y(s)",
                r"s^{2}Y(s) - 2s",
                r"s^{2}Y(s) - 2",
                r"s^{2}Y(s) - 2s - 2",
            ),
            answer=1,
            becauses=(
                "s²Y alone is the transform of y'' only when both initial "
                "values are zero. Here y(0) = 2.",
                "s²Y − s·y(0) − y'(0) = s²Y − 2s − 0. The y(0) term carries "
                "the factor of s; it is y'(0) that does not. Swapping them "
                "is the usual slip.",
                "This attaches y(0) to the term with no s, which is where "
                "y'(0) goes. That is exactly the swap the rule is written to "
                "prevent.",
                "This subtracts something for y'(0) as well, but y'(0) = 0 "
                "here, so there is nothing to subtract for it.",
            ),
        ),
        Choice(
            key="q2",
            prompt="Which problem is the transform the *only* practical method "
                   "here for?",
            options=(
                "y' + 2y = 0, y(0) = 1",
                "y'' + y = cos t, at rest",
                "y' + y = u(t − 2), y(0) = 0",
                "t²y'' + ty' − y = 0",
            ),
            answer=2,
            becauses=(
                "This separates in one line. The transform works too, but it "
                "is not the only route, nor the shortest.",
                "This is exactly what undetermined coefficients is for — and "
                "it is the resonant case, which that method handles by "
                "multiplying the guess by t.",
                "A forcing term switched on at t = 2 has no shape to guess "
                "and does not separate, so undetermined coefficients and "
                "separation both fail. The transform takes it as one extra "
                "factor e^{−2s}. The others all have simpler routes.",
                "Variable coefficients turn the transform into a *differential* "
                "equation in s rather than an algebraic one. The transform is "
                "the wrong tool here, not the only one — this is Cauchy–Euler.",
            ),
        ),
        Solve(
            key="q3",
            prompt="Transform, solve for Y(s), invert.",
            equation="y'' + 4*y = 0",
            conditions="y(0) = 0, y'(0) = 2",
            hints=(
                "L{y''} = s²Y − s·y(0) − y'(0), and here that is s²Y − 2.",
                "So (s² + 4)Y = 2, giving Y = 2/(s² + 4).",
                "That is the row for sin bt with b = 2, on sight: y = sin 2t.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Needs partial fractions on the way back.",
            equation="y' + 2*y = t",
            conditions="y(0) = 0",
            hints=(
                "L{y'} = sY − y(0) = sY, and L{t} = 1/s².",
                "So (s + 2)Y = 1/s², giving Y = 1/(s²(s+2)).",
                "Split it into A/s + B/s² + C/(s+2) and read each row "
                "backwards.",
            ),
        ),
        Solve(
            key="q5",
            prompt="A switch thrown at t = 2. Type Heaviside(t-2) for the step.",
            equation="y' + y = Heaviside(t - 2)",
            conditions="y(0) = 0",
            hints=(
                "L{u(t−2)} = e^{−2s}/s. The delay is a factor, not something "
                "to expand.",
                "Y = e^{−2s}/(s(s+1)). Invert 1/(s(s+1)) first — it is "
                "1 − e^{−t}.",
                "Then shift it: multiply by u(t−2) and replace t by t−2, "
                "giving u(t−2)(1 − e^{−(t−2)}).",
            ),
        ),
    ),
)


LESSONS = (LAPLACE,)
