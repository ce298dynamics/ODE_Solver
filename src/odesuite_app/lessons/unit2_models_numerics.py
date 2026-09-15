"""Unit 2 -- Models and numerical methods.

Edwards, Penney and Calvis 6e, chapter 2. Where the equations come from, and
what to do when none of the closed-form techniques applies -- which, outside a
textbook, is nearly always.

Five lessons: where the equations come from -- populations, equilibria, and
motion under resistance -- and then the two methods a first course computes
with when none of chapter 1's techniques applies.
"""

from __future__ import annotations

from .model import (
    Choice,
    Example,
    Lesson,
    ModelTemplate,
    Note,
    NumericTemplate,
    Passage,
    Solve,
    Template,
)

__all__ = ["POPULATION", "EQUILIBRIA", "MOTION", "NUMERICAL",
           "RUNGEKUTTA", "LESSONS"]


POPULATION = Lesson(
    key="population",
    title="Population models and the logistic equation",
    summary="Where the first interesting nonlinear equation comes from, and "
            "what its two parameters mean.",
    tool="worked",
    reference="Edwards 2.1",
    motivation=(
        "Where the equations of the first unit came from was never asked. "
        "This unit asks it, because a differential equation is not handed "
        "down — it is *derived*, from a statement about a rate — and "
        "population is the first place that happens with nothing hidden.\n\n"
        "The observable fact about a colony is not its size as a function of "
        "time. It is that each individual reproduces at some rate; multiply "
        "by how many there are and the result is a statement about the "
        "derivative. That gives exponential growth, and exponential growth is "
        "wrong. Nothing grows without bound, because food and space run out.\n\n"
        "The fix is not to abandon the model but to question the one "
        "assumption that was made silently — that the per-capita rate is a "
        "constant. Let it fall as the population rises and the logistic "
        "equation appears. It is the first nonlinear equation in this course "
        "that anyone actually needs, and it is separable, so the previous "
        "unit already solves it."
    ),
    derivation=(
        Passage(
            prose="Start from what is observable. Each individual contributes births at "
                  "some rate, so with P of them the total rate is that rate times P. "
                  "Written out, that is a statement about the derivative and nothing "
                  "else.",
            latex=r"P' = r\,P",
        ),
        Passage(
            prose="That equation is separable, and the previous unit finishes it in two "
                  "lines: exponential growth, with every solution a multiple of a "
                  "single exponential and the constant turning out to be the starting "
                  "population.",
            latex=r"P(t) = P_0\,e^{rt}",
        ),
        Passage(
            prose="Now look at what was assumed rather than at what came out. The rate "
                  "r was taken to be the same at a population of ten and at a "
                  "population of a million — every individual reproducing as freely in "
                  "a crowd as alone. Written as a per-capita rate the assumption is "
                  "impossible to miss, and it is the one that fails.",
            latex=r"\frac{P'}{P} = r \quad \text{(the per-capita rate, assumed constant)}",
        ),
        Passage(
            prose="So let the per-capita rate fall as the population rises, and take "
                  "the simplest fall there is: linear, reaching zero at some population "
                  "K. Nothing about K has to be interpreted — it is defined as where "
                  "the per-capita rate runs out.",
            latex=r"\frac{P'}{P} = r\left(1 - \frac{P}{K}\right)",
        ),
        Passage(
            prose="Multiplying back gives the logistic equation, and K now needs no "
                  "explaining: it is where the right-hand side vanishes, so it is a "
                  "constant solution, and it is the only population at which growth "
                  "stops without the colony being empty. The carrying capacity was not "
                  "added to the model; it was already in the assumption.",
            latex=r"P' = r\,P\left(1 - \frac{P}{K}\right)",
        ),
        Passage(
            prose="It is separable, and the integral is where the S-shape comes from. "
                  "The left-hand side splits by partial fractions into two pieces, each "
                  "of which integrates to a logarithm; a difference of logarithms is "
                  "the logarithm of a ratio; and solving that for P gives the sigmoid. "
                  "The curve is a consequence of the algebra rather than a shape chosen "
                  "because it looks right.",
            latex=r"\int\frac{dP}{P\left(1 - P/K\right)} = \int r\,dt "
                  r"\;\Longrightarrow\; P = \frac{K}{1 + Ce^{-rt}}",
        ),
    ),
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
            commentary=(
                "Watch how little the working needs. One separation, one integration, "
                "and the constant of integration turns out to be the population you "
                "started with — which is why this answer can be written straight down "
                "once it has been derived a single time.\n\n"
                "Then ask the answer about doubling. Set it equal to twice its "
                "starting value and the starting value cancels off both sides, "
                "leaving a time that depends only on the rate. A colony of ten and a "
                "colony of a million take exactly as long to double. That is the "
                "signature of this model, and it is also the clearest statement of "
                "why it cannot hold for long."
            ),
        ),
        Example(
            equation="y' = 0.5*y*(1 - y/20)",
            conditions="y(0) = 2",
            why="The same growth rate with a ceiling. Watch the answer rise "
                "almost exponentially at first and then flatten — and notice "
                "the capacity, 20, appearing in the answer without having been "
                "put there by hand.",
            commentary=(
                "Two things to watch in the separation. The integral needs partial "
                "fractions, and the two logarithms it produces are what become the "
                "ratio in the final expression — so the S-shape is the algebra's "
                "doing, not a curve fitted because it looked plausible.\n\n"
                "Then check both ends against the equation rather than against the "
                "graph. Early on the bracket is close to one, so the equation is very "
                "nearly the previous example and the growth is very nearly "
                "exponential. As the population climbs, the same bracket closes on "
                "zero, so the rate does too — and it never crosses, since being above "
                "the ceiling is the only way to make that rate negative."
            ),
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
        ModelTemplate(
            key="harvested-logistic",
            title="Set up the equation: a harvested population",
            prompt="A fish stock grows logistically. Left alone, its "
                   "per-capita growth rate is {r} a year while the stock is "
                   "small, and it falls to zero at a carrying capacity of "
                   "{K} tonnes. Boats take {h} tonnes a year whatever the "
                   "stock is. Write the equation for y, the stock in tonnes.",
            equation="y' = {r}*y*(1 - y/{K}) - {h}",
            because="Growth minus harvest. The growth is a per-capita rate "
                    "times the stock, and the per-capita rate falls linearly "
                    "from {r} at no stock to zero at {K} tonnes — which is "
                    "the bracket. The harvest is a flat tonnage: it does not "
                    "scale with the stock, so it is subtracted whole rather "
                    "than becoming another factor of y.",
            hints=(
                "Write the growth first, as though nobody were fishing, and "
                "subtract the harvest at the end.",
                "Logistic growth is the per-capita rate times y, and the "
                "per-capita rate is what falls to zero at the carrying "
                "capacity — not the growth itself.",
                "The boats take the same tonnage whether the stock is large "
                "or small, so that term has no y in it at all.",
            ),
            slots=(("r", (2, 3, 5)), ("K", (100, 200, 400)),
                   ("h", (10, 20, 40))),
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
    motivation=(
        "The logistic equation was solved, and the answer was informative — "
        "but solving it was work, and most autonomous equations cannot be "
        "solved at all. Add a harvest term, or a threshold below which the "
        "colony fails, and the integral stops being elementary. So the "
        "question is whether the long-run behaviour actually needs the "
        "solution.\n\n"
        "It does not, and the reason is that an autonomous equation carries "
        "no clock. The slope depends on where you are and not on when you got "
        "there, so position alone determines the entire future — and a "
        "picture of the line, marked with which way the arrows point, holds "
        "every qualitative fact about every solution at once.\n\n"
        "This is the first genuinely different kind of answer in the course, "
        "and it is worth being clear that nothing about it is approximate. "
        "The claim that a solution starting just above zero rises towards the "
        "carrying capacity and never overshoots it is exact, and it is "
        "obtained without integrating anything."
    ),
    derivation=(
        Passage(
            prose="Autonomous means the right-hand side never mentions t. So the same "
                  "value of y gives the same slope whenever it occurs, and a solution "
                  "slid along in time is still a solution — which is why one curve's "
                  "shape describes a whole family rather than one member of it.",
            latex=r"y' = f(y) \;\Longrightarrow\; y(t - c) \text{ solves it too}",
        ),
        Passage(
            prose="Wherever f vanishes the slope is zero, so the constant function sits "
                  "there forever. Those are the equilibria, and they are the *only* "
                  "constant solutions there can be: a constant has zero derivative, "
                  "which the equation then forces f to match.",
            latex=r"f(y_0) = 0 \;\Longleftrightarrow\; y \equiv y_0 \text{ solves it}",
        ),
        Passage(
            prose="Between two consecutive equilibria f keeps one sign, because a "
                  "change of sign would be another root. So every solution in that "
                  "interval is monotone throughout, and it cannot leave: arriving at an "
                  "equilibrium would put two solutions through one point, which the "
                  "uniqueness theorem forbids.",
            latex=r"f > 0 \text{ on } (a,b) \;\Longrightarrow\; y \text{ "
                  r"rises, and stays in } (a,b)",
        ),
        Passage(
            prose="That is already the whole qualitative answer. The sign of f on each "
                  "side of an equilibrium settles its character — arrows in from both "
                  "sides is stable, out from both is unstable, one of each is semi-"
                  "stable — and a line marked with those arrows can be read off faster "
                  "than any solution can be computed.",
            latex=r"f(y_0) = 0,\ f > 0 \text{ below},\ f < 0 \text{ above} "
                  r"\;\Longrightarrow\; \text{stable}",
        ),
        Passage(
            prose="The derivative test is usually presented as a rule to remember, and "
                  "it is worth deriving instead. Stand just off the equilibrium: "
                  "put y = y₀ + ε for a small displacement ε, expand f about y₀, "
                  "and use f(y₀) = 0. What is left is the linear equation from the "
                  "first unit, whose solution grows or decays according to the "
                  "sign of a single number.",
            latex=r"\varepsilon' = f(y_0 + \varepsilon) \approx f'(y_0)\,\varepsilon "
                  r"\;\Longrightarrow\; \varepsilon \approx \varepsilon_0\,e^{f'(y_0)t}",
        ),
        Passage(
            prose="The same derivation says exactly when the test is useless. If "
                  "f'(y_0) is zero the linear term has vanished and the approximation "
                  "makes no claim at all, so the next term decides and the sign of f on "
                  "each side has to be looked at directly. That is not a gap in the "
                  "rule; it is the rule being honest about what it approximated away.",
            latex=r"f'(y_0) = 0 \;\Longrightarrow\; \varepsilon' \approx 0 "
                  r"\quad \text{(which says nothing)}",
        ),
    ),
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
            commentary=(
                "Draw the phase line on paper before reading a line of the working. "
                "The right-hand side factors, so its roots are immediate; it is "
                "positive outside them and negative in between; and those three signs "
                "already say which way every solution goes and where it ends up.\n\n"
                "Then treat the closed form as a check on the picture rather than the "
                "other way round. It confirms that the limit is approached and never "
                "attained, which is what an equilibrium being a limit means. And it "
                "adds the one thing the phase line cannot supply: a rate. The "
                "exponent in the answer is the derivative of the right-hand side at "
                "that equilibrium, exactly as the linearisation in the derivation "
                "predicts."
            ),
        ),
        Example(
            equation="y' = 4 - y",
            conditions="y(0) = 10",
            why="One equilibrium, and everything approaches it. The simplest "
                "case, and the one where the exponential in the answer is "
                "visibly the approach to y = 4.",
            commentary=(
                "This is the linearisation being exact rather than approximate, which "
                "makes it the right place to see the argument work. The right-hand "
                "side is already linear, so expanding it about the equilibrium "
                "changes nothing at all, and the small-displacement equation of the "
                "derivation is simply the original equation with the derivative equal "
                "to minus one.\n\n"
                "So read the exponent as a rate of approach. It says the gap between "
                "the solution and the equilibrium shrinks by a fixed proportion in "
                "every unit of time, whatever the gap happened to be — which is why "
                "one curve, shifted sideways, describes a start at ten and a start at "
                "four hundred equally well."
            ),
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
    templates=(
        NumericTemplate(
            key="find-the-equilibrium",
            title="Where the right-hand side vanishes",
            prompt="The equation y' = {a}*y - {b}*y**2 has an equilibrium at "
                   "y = 0. What is the other one?",
            answer="{a}/{b}",
            because="Factor the right-hand side as y({a} − {b}y). It vanishes "
                    "at y = 0 and where {b}y = {a}, and those are the only "
                    "constant solutions there are — a constant has zero "
                    "derivative, so the equation forces f to match.",
            latex=r"y' = {a}\,y - {b}\,y^{{2}}",
            hints=(
                "An equilibrium is a root of the right-hand side, so set it "
                "to zero.",
                "Factor out a y. The other factor is linear, and its root is "
                "the equilibrium wanted.",
            ),
            # No coefficient of 1: the reason above reads "y(6 - 1y)"
            # otherwise, which is how you can tell it was generated.
            slots=(("a", (2, 3, 4, 6, 8)), ("b", (2, 3, 4))),
            # a/b = 1 makes the two roots as close as they get and the
            # arithmetic disappears; the drill is for the reading, not for
            # spotting a coincidence.
            reject=lambda slots: slots["a"] == slots["b"],
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
    figure="terminal_velocity",
    motivation=(
        "Population produced one equation from one assumption. Mechanics "
        "produces most of the rest of this subject from a single law, and the "
        "law is already a differential equation: acceleration is the second "
        "derivative of position, so any statement about forces is a statement "
        "about a second derivative.\n\n"
        "What makes the problem interesting is not gravity but the "
        "resistance. With gravity alone a falling object accelerates forever, "
        "which is visibly false — a raindrop does not arrive at the speed of "
        "a bullet. Something removes the excess, and whatever it is must "
        "depend on the speed, because an object at rest feels no air "
        "resistance at all.\n\n"
        "The moment that term is written down, the equation turns into one "
        "already solved. In terms of velocity it is first order and linear, "
        "so the integrating factor ends it; and the terminal velocity "
        "everyone knows about turns out to be an equilibrium of exactly the "
        "kind the previous lesson classified. Nothing new is needed here — "
        "two earlier lessons meet."
    ),
    derivation=(
        Passage(
            prose="Newton's law is a statement about the second derivative of position. "
                  "Written in terms of velocity instead it is first order, which is why "
                  "every problem in this lesson is solved for the velocity first and "
                  "integrated for the position afterwards.",
            latex=r"m\,\frac{d^2y}{dt^2} = \sum F \;\Longrightarrow\; "
                  r"m\,\frac{dv}{dt} = \sum F",
        ),
        Passage(
            prose="Choose a positive direction and hold to it. This is where these "
                  "problems go wrong far more often than in any of the calculus: with "
                  "up positive, gravity contributes a fixed negative term whatever the "
                  "object is doing, while the resistance always opposes the motion and "
                  "so carries the sign opposite to the velocity.",
            latex=r"m\,v' = -mg - k\,v",
        ),
        Passage(
            prose="Divide through by the mass — the same first move as in the "
                  "integrating-factor lesson — and the shape is familiar. It is the "
                  "standard form with p and q both constant, so the factor is a plain "
                  "exponential and one integration finishes the problem.",
            latex=r"v' + \frac{k}{m}\,v = -g",
        ),
        Passage(
            prose="But it is also autonomous, so the previous lesson applies without "
                  "solving anything. Setting the right-hand side to zero gives the one "
                  "velocity at which the two forces balance, and the sign of the right-"
                  "hand side on either side of it shows every solution moving towards "
                  "it. Terminal velocity is a stable equilibrium, and it costs a "
                  "division to find.",
            latex=r"v' = 0 \;\Longrightarrow\; v_\infty = -\frac{mg}{k}",
        ),
        Passage(
            prose="The closed form agrees, and it is worth reading once for its shape. "
                  "The answer is the terminal velocity plus a decaying exponential, so "
                  "the starting speed is forgotten at a rate set by k/m — a heavier "
                  "object with the same drag coefficient forgets it more slowly, which "
                  "is the whole of why mass matters here.",
            latex=r"v(t) = -\frac{mg}{k} + \left(v_0 + \frac{mg}{k}\right)e^{-kt/m}",
        ),
        Passage(
            prose="Position takes one more integration, and that brings the second "
                  "constant, which is the starting height. Two integrations, two "
                  "constants, two conditions: the count from the very first lesson of "
                  "the course, now attached to something physical.",
            latex=r"y(t) = y_0 + \int_0^{t} v(s)\,ds",
        ),
        Passage(
            prose="All of that assumed drag proportional to the speed. At higher speeds "
                  "the resistance goes as the square instead, and then the equation is "
                  "no longer linear in v — the integrating factor simply does not "
                  "apply. It is separable rather than linear, which is why the two "
                  "cases are taught apart instead of as one.",
            latex=r"m\,v' = -mg + k\,v^{2} \qquad (v < 0)",
        ),
    ),
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
            commentary=(
                "Find the terminal velocity before looking at the working: set the "
                "right-hand side to zero and it is one division. Having that number "
                "in hand first turns the closed form into a confirmation instead of a "
                "revelation, and forming that habit is most of what this lesson is "
                "for.\n\n"
                "Then watch what the initial condition does to the shape. Starting "
                "from rest makes the exponential's coefficient the entire terminal "
                "value, so the answer is that value times one minus a decaying "
                "exponential — the object has the whole gap to close. And read the "
                "time scale off the exponent while you are there: with 0.2 in it, the "
                "gap is closed to within a percent in about twenty-five seconds, "
                "which nothing in the problem statement said out loud."
            ),
        ),
        Example(
            equation="y' = -9.8",
            conditions="y(0) = 20",
            why="The same problem with no resistance. One integration, a "
                "straight line, and no terminal velocity at all — which is "
                "what the drag term is there to fix.",
            commentary=(
                "Worth working precisely because nothing happens. Take the resistance "
                "away and what is left is the y' = f(t) of the very first lesson. It "
                "takes a single integration, and the velocity it gives is a line with "
                "no value on it anywhere at which the right-hand side vanishes.\n\n"
                "Then set it beside the previous example over a short interval. Early "
                "on the drag has removed almost nothing and the two velocities nearly "
                "coincide, which is why this model is not so much wrong as *early* — "
                "it is the first stretch of the other answer, and it stops being "
                "usable at exactly the speed where the resistance starts to count."
            ),
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
    templates=(
        NumericTemplate(
            key="terminal-velocity",
            title="Terminal velocity, without solving",
            # The mass appears as data and never inside the equation: writing
            # it there would substitute to "-2*9.8", which nothing tidies.
            prompt="A body of mass {m} kg falls under m*v' = -m*9.8 - {k}*v, "
                   "with up positive. What is its terminal velocity?",
            answer="-{m}*9.8/{k}",
            units="m/s",
            because="The equation is autonomous, so the previous lesson "
                    "applies: set the right-hand side to zero and the two "
                    "forces balance. It costs one division, and every "
                    "solution approaches it whatever the speed at the start.",
            latex=r"m\,v' = -m\,g - k\,v",
            hints=(
                "Nothing has to be solved. Terminal velocity is the one speed "
                "at which the acceleration is zero.",
                "Set the right-hand side to zero and divide by the drag "
                "coefficient.",
            ),
            slots=(("k", (0.2, 0.25, 0.4, 0.5, 0.7)), ("m", (1, 2, 4))),
        ),
        ModelTemplate(
            key="falling-with-drag",
            title="Set up the equation: falling against the air",
            prompt="A parcel of mass {m} kg falls from rest. Gravity pulls "
                   "it down with an acceleration of 9.8 m/s², and the air "
                   "resists with {k} newtons for every metre per second of "
                   "speed, against the motion. Write the equation for y, the "
                   "downward velocity in metres per second.",
            equation="{m}*y' = {m}*9.8 - {k}*y",
            because="Newton's second law with down counted positive: mass "
                    "times acceleration is the weight {m}·9.8 newtons minus "
                    "the drag, which is {k} newtons per metre per second "
                    "times the speed. Dividing through by the mass gives the "
                    "same equation, and the grader accepts either.",
            hints=(
                "Start from mass times acceleration equals the total force, "
                "and remember that y is a velocity, so its derivative is the "
                "acceleration.",
                "Two forces only: the weight, which does not change, and the "
                "drag, which grows with the speed and pulls the other way.",
                "Count down as positive and the weight is positive while the "
                "drag is negative. Getting that sign the other way round "
                "makes the parcel speed up forever.",
            ),
            slots=(("m", (2, 5, 10)), ("k", (2, 4, 5, 8))),
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
    motivation=(
        "Every technique so far has needed the equation to have a shape. Most "
        "equations do not have one. y' = y² − t is perfectly ordinary, has "
        "perfectly ordinary solutions, and has no elementary formula at all — "
        "and it is far more typical than anything in the first unit. The "
        "honest position is that closed forms are the exception.\n\n"
        "What is always available is the equation itself. It gives the slope "
        "at every point of the plane, which is exactly what the slope-field "
        "lesson used to trace solutions by eye. Following a slope with a "
        "ruler is something a machine can do far more patiently than a hand, "
        "and that is the whole idea here — the least clever idea in the "
        "subject, and the most used.\n\n"
        "The interesting part is not the method but its error. A step that "
        "follows one slope is wrong the moment the slope changes, so the "
        "question is how wrong, and how the wrongness accumulates over "
        "thousands of steps. Answering that is what separates a numerical "
        "method from a guess, and it is what this lesson is actually about."
    ),
    derivation=(
        Passage(
            prose="The equation names the slope at the point you are standing on. "
                  "Follow it for a short distance and you land somewhere near the "
                  "solution. That is the entire method: the tangent-line approximation "
                  "from first-year calculus, applied again at each new point.",
            latex=r"y_{n+1} = y_n + h\,f(t_n, y_n)",
        ),
        Passage(
            prose="To find the error, compare a step against the truth. Taylor's "
                  "theorem expands the exact solution about the current point, and its "
                  "first two terms are precisely the Euler step — so everything the "
                  "method throws away is sitting in the remainder, where it can be "
                  "looked at.",
            latex=r"y(t_n + h) = y_n + h\,y'(t_n) + \frac{h^{2}}{2}y''(\xi)",
        ),
        Passage(
            prose="So a single step is wrong by an amount proportional to the square of "
                  "the step. Halving the step makes one step four times as accurate, "
                  "which sounds far better than it turns out to be.",
            latex=r"\text{local error} = \frac{h^{2}}{2}y''(\xi) = O(h^{2})",
        ),
        Passage(
            prose="Here is why. Crossing a fixed interval takes more steps as the step "
                  "shrinks — about one over h of them — so the per-step error has to be "
                  "multiplied by a count that grows as h falls. One power of h is lost "
                  "in the multiplication, and that is where *first order* comes from. "
                  "It is a statement about the whole journey, not about one step.",
            latex=r"\frac{b - a}{h} \times O(h^{2}) = O(h)",
        ),
        Passage(
            prose="Which is a poor return: one more correct decimal digit costs a "
                  "tenfold smaller step and therefore tenfold the work. That arithmetic "
                  "is the honest reason nobody uses this method for real computation, "
                  "and it is the reason the next lesson exists.",
            latex=r"h \to h/10 \;\Longrightarrow\; \text{error} \to \text{error}/10",
        ),
        Passage(
            prose="One more thing that accounting quietly assumed: that the errors "
                  "merely add up. They need not. Each step sets out from a point "
                  "already slightly wrong, and the equation itself then amplifies or "
                  "damps that error along with everything else — which is why a step "
                  "size that behaves well on one equation can diverge on another just "
                  "as smooth.",
            latex=r"y' = -100y,\ h = 0.1 \;\Longrightarrow\; |1 + h\lambda| = 9 > 1",
        ),
    ),
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
            commentary=(
                "The closed form is the whole reason for this choice of equation, so "
                "use it as a ruler. Take one step of size 0.1 by hand: it lands on "
                "1.1, the true value is 1.10517, and the difference is 0.0052 — which "
                "is h²/2 to two figures, exactly what the second passage of the "
                "derivation says it should be.\n\n"
                "Then take ten such steps and compare again. They give 1.1 raised to "
                "the tenth, about 2.5937, against e at about 2.7183 — an error of "
                "0.125, some twenty-four times the single-step error rather than ten "
                "times it. That gap between the local picture and the global one is "
                "the thing to carry away, and it is why the count of steps has to "
                "enter the error estimate at all."
            ),
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
    templates=(
        NumericTemplate(
            key="one-euler-step",
            title="One step of Euler's method",
            prompt="For y' = {a}*y with y(0) = {y0}, take one Euler step of "
                   "size h = {h}. What is the value it lands on?",
            answer="{y0} + {h}*({a}*{y0})",
            because="Evaluate the right-hand side at the starting point to get "
                    "the slope, follow it for {h}, and add the rise to where "
                    "you started. That is the whole method — and the exact "
                    "solution has already curved away from it by about "
                    "h²y″/2.",
            latex=r"y_{{1}} = y_0 + h\,f(t_0, y_0)",
            hints=(
                "Evaluate the slope first: the equation gives it directly at "
                "the starting point.",
                "Then travel on that slope for a distance h, and add what you "
                "gain to y(0).",
            ),
            slots=(("a", (-2, -1, 2, 3)), ("y0", (1, 2, 4)),
                   ("h", (0.1, 0.2, 0.25, 0.5))),
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
    figure="order_slope",
    motivation=(
        "Euler's method works, and its error analysis is honest, and together "
        "they produce a discouraging piece of arithmetic: each additional "
        "decimal digit costs ten times the work. Anything that needs six "
        "digits is out of reach, and six digits is a modest request.\n\n"
        "The way out is not a smaller step but a better use of each one. "
        "Euler commits to the slope at the start of the interval and then "
        "travels the whole way on it, which is the crudest possible reading "
        "of a slope that is turning throughout. Sampling it more than once "
        "costs more per step, and the whole question is whether the accuracy "
        "bought exceeds what it cost.\n\n"
        "It does, by a wide margin. Four evaluations arranged carefully give "
        "a method whose error falls with the *fourth* power of the step, so "
        "halving the step divides the error by sixteen rather than by two. "
        "That trade is why essentially every general-purpose solver in "
        "existence is built this way — and it is also why methods have to be "
        "compared by evaluations rather than by steps."
    ),
    derivation=(
        Passage(
            prose="Euler travels on the slope at one end of the interval and uses "
                  "nothing else, which is exact only when the slope is constant. "
                  "Everything in this lesson follows from one question: what would be a "
                  "better single number to travel on?",
            latex=r"y_{n+1} = y_n + h\,f(t_n, y_n)",
        ),
        Passage(
            prose="The obvious candidate is the slope at the middle rather than at the "
                  "start, and it is already much better — a midpoint slope represents "
                  "an interval whose slope is turning far more faithfully than either "
                  "end does. The catch is that the midpoint is not known in advance, so "
                  "it has to be estimated first, and that pattern is what the whole "
                  "method is built from.",
            latex=r"k_1 = f(t_n, y_n), \qquad k_2 = f\left(t_n + \frac{h}{2},\ "
                  r"y_n + \frac{h}{2}k_1\right)",
        ),
        Passage(
            prose="Then repeat the idea. Use the better midpoint slope to make a better "
                  "estimate of the midpoint, and use that to reach the far end. Four "
                  "evaluations, each an ordinary use of f at a point already computed — "
                  "nothing here is implicit, and nothing has to be solved for.",
            latex=r"k_3 = f\left(t_n + \frac{h}{2},\ y_n + "
                  r"\frac{h}{2}k_2\right), \qquad k_4 = f(t_n + h,\ y_n + "
                  r"h\,k_3)",
        ),
        Passage(
            prose="Now combine them, with the two midpoint slopes counting double. The "
                  "weights come from a Taylor expansion: they are chosen so that the "
                  "combination agrees with the exact solution's expansion through the "
                  "h⁴ term, and everything up to that order cancels by construction. "
                  "Deriving them is a long and unilluminating calculation; knowing what "
                  "they were chosen to do is the part that matters.",
            latex=r"y_{n+1} = y_n + \frac{h}{6}\left(k_1 + 2k_2 + 2k_3 + k_4\right)",
        ),
        Passage(
            prose="The local error is therefore one order higher again, and the same "
                  "accumulation argument as before costs one power of h. That is the "
                  "whole claim, and note what kind of claim it is: *fourth order* says "
                  "how the error responds to a change in h, and says nothing about how "
                  "accurate any particular run happens to be.",
            latex=r"\frac{b - a}{h} \times O(h^{5}) = O(h^{4})",
        ),
        Passage(
            prose="Which brings the comparison that has to be made carefully. One step "
                  "here costs four evaluations, so it must be judged against four Euler "
                  "steps — that is, against Euler run at a quarter of the step, not at "
                  "the same one. Euler's error is then proportional to h/4 while this "
                  "method's is proportional to h⁴, and for any h small enough the "
                  "second is smaller by a factor that grows as h shrinks.",
            latex=r"h = 0.1: \quad \frac{h}{4} = 0.025 \quad \text{against} "
                  r"\quad h^{4} = 0.0001",
        ),
        Passage(
            prose="It is also how an order is measured rather than taken on trust. "
                  "Halve the step repeatedly and take the ratio of successive errors: "
                  "the ratio tends to two raised to the order, so a column of ratios "
                  "reading 2 identifies a first-order method and one reading 16 a "
                  "fourth-order one. They arrive at those values from below, because "
                  "the next term in the expansion is only negligible once h is small.",
            latex=r"\frac{E(h)}{E(h/2)} \longrightarrow 2^{\,p}",
        ),
    ),
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
            commentary=(
                "A decaying exponential is chosen deliberately: the exact answer is a "
                "single term, so there is nothing to disentangle and the error at any "
                "step size is one subtraction. It also has a real time scale — the "
                "solution loses half its size every 0.35 or so — which means a step "
                "of 0.5 is large for this equation and 0.05 is comfortable, and the "
                "tables show the difference plainly.\n\n"
                "Watch the ratios rather than the errors. Any single error is a "
                "number without a meaning attached; the ratio between two of them is "
                "the order, and here it should climb towards sixteen. That it climbs "
                "rather than landing exactly is expected — behind the leading term is "
                "a smaller one that is only negligible once the step is small — so an "
                "early row reading twelve is the method behaving correctly, not a "
                "mistake in the arithmetic."
            ),
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
    templates=(
        NumericTemplate(
            key="one-rk4-step",
            title="One step of RK4, to four decimal places",
            prompt="For y' = {a}*y with y(0) = 1, take one RK4 step of size "
                   "h = {h}. Give the value to four decimal places.",
            answer="1 + ({a}*{h}) + ({a}*{h})**2/2 + ({a}*{h})**3/6 "
                   "+ ({a}*{h})**4/24",
            # Loose enough for the four decimal places the prompt asks for,
            # and tight enough to reject an Euler step -- which is the wrong
            # answer this question actually produces, and sits a hundred
            # times further away than the tolerance.
            #
            # Not tight enough to reject the exact solution, and deliberately
            # so: for these step sizes the method agrees with it to between
            # seven and four decimal places, which is what fourth order buys.
            # A drill cannot mark somebody wrong for writing down a number the
            # method genuinely lands on.
            tolerance=1e-4,
            because="The four stages weighted 1, 2, 2, 1 over six reproduce "
                    "the exponential series as far as the h⁴ term — which is "
                    "what the weights were chosen to do. The exact answer is "
                    "close but not equal, and the gap is the local error.",
            latex=r"y_{{1}} = y_0 + \frac{{h}}{{6}}"
                  r"\left(k_1 + 2k_2 + 2k_3 + k_4\right)",
            hints=(
                "k₁ is the slope at the start, k₂ and k₃ at the midpoint, k₄ "
                "at the far end — each one an ordinary evaluation of f.",
                "For y' = ay every stage is a multiple of y₀, so the step "
                "comes out as y₀ times a polynomial in ah.",
            ),
            slots=(("a", (-2, -1, 1, 2)), ("h", (0.1, 0.2, 0.25))),
        ),
    ),
)


LESSONS = (POPULATION, EQUILIBRIA, MOTION, NUMERICAL, RUNGEKUTTA)
