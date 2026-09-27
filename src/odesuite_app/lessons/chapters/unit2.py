"""Unit 2 chapters -- models and numerical methods (Edwards ch. 2)."""

from __future__ import annotations

from ..chapter import Box, Curve, Display, Figure, Para, Plot, Section, Step, Worked

__all__ = ["POPULATION", "EQUILIBRIA"]


EQUILIBRIA = (
    Section("Autonomous equations", (
        Para(
            "Every population model of the last lesson had a right-hand side "
            "that depended on P but not on t. The law of growth was the same "
            "on every day: only the population changed. Equations of that "
            "kind are called autonomous, and they are important enough — "
            "most physical laws are autonomous — to deserve a theory of their "
            "own. The theory is the phase line, and it answers the most "
            "useful questions about an autonomous equation without solving it."
        ),
        Box(
            "definition", "Autonomous equation",
            "A first-order equation is *autonomous* if its right-hand side "
            "depends on y alone.",
            r"\frac{dy}{dt} = f(y)",
        ),
        Para(
            "The defining property is that shifting a solution in time gives "
            "another solution. If y(t) solves y' = f(y), then so does y(t − c) "
            "for any constant c, because both sides of the equation are "
            "evaluated at the same shifted time and nothing in the equation "
            "notices. So the question 'what happens to a solution that starts "
            "at y₀?' has the same answer whenever it starts. Only the value "
            "matters, not the date."
        ),
        Box(
            "theorem", "Time-shift invariance",
            "If y(t) is a solution of y' = f(y) on an interval I, then for "
            "every constant c the function y(t − c) is a solution on the "
            "shifted interval I + c.",
        ),
        Para(
            "Geometrically, the slope field of an autonomous equation is the "
            "same along every horizontal line, since the slope depends only on "
            "the height. Every horizontal translate of a solution curve is "
            "another solution curve. That redundancy is what lets the whole "
            "picture be compressed onto a single vertical line."
        ),
    )),
    Section("Equilibrium solutions", (
        Box(
            "definition", "Equilibrium (critical point)",
            "A number c with f(c) = 0. The constant function y(t) ≡ c is then "
            "a solution — an *equilibrium solution* — because its derivative, "
            "zero, equals f(c).",
            r"f(c) = 0 \;\Longrightarrow\; y(t) \equiv c",
        ),
        Para(
            "Finding equilibria is algebra: solve f(y) = 0. For the logistic "
            "equation f(P) = kP(M − P), they are P = 0 and P = M. For "
            "y' = (y − 1)(y − 3) they are 1 and 3. For y' = sin y there are "
            "infinitely many, at every multiple of π. An autonomous equation "
            "may also have none, like y' = 1 + y², whose solutions all run off "
            "to infinity."
        ),
        Para(
            "Between two consecutive equilibria f has no zero, so, if f is "
            "continuous, it has a single sign there. Every solution starting "
            "in that interval therefore moves monotonically — always up if "
            "f > 0, always down if f < 0. And by uniqueness it can never reach "
            "either equilibrium, since that would mean two solution curves "
            "meeting. A solution trapped between two equilibria must "
            "therefore approach one of them: the one it is moving towards."
        ),
        Box(
            "theorem", "Solutions between equilibria",
            "Let f and f′ be continuous, and let a < b be consecutive "
            "equilibria of y' = f(y). A solution with a < y(0) < b stays in "
            "(a, b) for all t. If f > 0 on (a, b) it increases to b as t → ∞ "
            "and decreases to a as t → −∞; if f < 0 the roles swap.",
        ),
    )),
    Section("The phase line", (
        Para(
            "All of that can be drawn on one vertical line. Mark the "
            "equilibria as points. In each interval between them, draw an "
            "arrow up if f > 0 and down if f < 0. That picture — the *phase "
            "line* — is a complete qualitative description of every solution: "
            "start anywhere, follow the arrow, and you arrive at the "
            "equilibrium it points to, or run off to ±∞ if there is none in "
            "that direction."
        ),
        Para(
            "The quickest way to find the arrows is to sketch the graph of "
            "f(y) against y. Where the graph is above the axis, f > 0 and "
            "solutions increase; where it is below, they decrease. The "
            "equilibria are where the graph crosses the axis. The phase line "
            "is just the y-axis of that graph with arrows on it."
        ),
        Figure("phase_line",
               "The graph of f(y) for harvested logistic growth, with the "
               "phase line along its axis. Raise the harvest h and watch the "
               "two equilibria slide together and vanish."),
        Worked(
            "Reading, then confirming",
            "For y' = (y − 1)(y − 3), draw the phase line, predict the solution "
            "from y(0) = 2, and confirm by solving.",
            (
                Step("Equilibria 1 and 3. For y < 1 both factors are negative "
                     "and f > 0: arrows up. For 1 < y < 3, f < 0: arrows down. "
                     "For y > 3, f > 0: arrows up. So 1 attracts from both "
                     "sides and 3 repels.",
                     r"f(y) = (y - 1)(y - 3)"),
                Step("From y(0) = 2 the phase line predicts a decrease towards "
                     "1. To confirm, separate with partial fractions: "
                     "1/((y − 1)(y − 3)) = (1/2)(1/(y − 3) − 1/(y − 1)), so "
                     "(1/2)ln|(y − 3)/(y − 1)| = t + C.",
                     r"\frac{y - 3}{y - 1} = A e^{2t}"),
                Step("At t = 0 the left side is −1, so A = −1. Solving for y:"
                     " y − 3 = −(y − 1)e^(2t), so y(1 + e^(2t)) = 3 + e^(2t). As "
                     "t → ∞ the e^(2t) terms dominate and y → 1, as predicted."),
            ),
            equation="y' = (y - 1)*(y - 3)", conditions="y(0) = 2",
            answer="(3 + exp(2*t))/(1 + exp(2*t))",
            answer_latex=r"y(t) = \frac{3 + e^{2t}}{1 + e^{2t}}",
        ),
        Plot(
            "Solutions of y' = (y − 1)(y − 3)",
            "Starting values 0, 2 and 2.9 all end at y = 1, the stable "
            "equilibrium, approached from both sides. The solution from 3.1 "
            "leaves y = 3 upwards and blows up, as does every solution that "
            "starts above 3. The equilibria are the straight lines; nothing "
            "crosses them.",
            (Curve("(3 - 3*exp(2*t))/(1 - 3*exp(2*t))", "y(0) = 0"),
             Curve("(3 + exp(2*t))/(1 + exp(2*t))", "y(0) = 2"),
             Curve("(3 + 0.0526*exp(2*t))/(1 + 0.0526*exp(2*t))", "y(0) = 2.9"),
             Curve("Piecewise(((3 - 0.0476*exp(2*t))/(1 - 0.0476*exp(2*t)), "
                   "t < 1.3), (nan, True))", "y(0) = 3.1"),
             Curve("1 + 0*t", "y = 1"), Curve("3 + 0*t", "y = 3")),
            t=(0.0, 3.0), ylim=(-0.5, 5.0),
        ),
    )),
    Section("What happens beyond the last equilibrium", (
        Para(
            "Above y = 3 the phase line of y' = (y − 1)(y − 3) has an arrow "
            "pointing up and no equilibrium to stop at. The theorem between "
            "equilibria does not apply, and the phase line alone cannot say "
            "whether the solution grows for ever, levels off at infinity, or "
            "reaches infinity in finite time. Here f grows like y², and that "
            "is fast enough to escape in finite time, as y' = y² did."
        ),
        Worked(
            "Escape above an unstable equilibrium",
            "Solve y' = (y − 1)(y − 3) with y(0) = 4, and find when the "
            "solution blows up.",
            (
                Step("The same separation gives (y − 3)/(y − 1) = Ae^(2t), and "
                     "at t = 0 the left side is 1/3, so A = 1/3.",
                     r"\frac{y - 3}{y - 1} = \frac{1}{3}e^{2t}"),
                Step("Solving for y, y(1 − e^(2t)/3) = 3 − e^(2t)/3. The "
                     "denominator reaches zero when e^(2t) = 3, that is at "
                     "t = (ln 3)/2 ≈ 0.55, and the solution blows up there.",
                     r"t^{*} = \frac{\ln 3}{2} \approx 0.55"),
            ),
            equation="y' = (y - 1)*(y - 3)", conditions="y(0) = 4",
            answer="(3 - exp(2*t)/3)/(1 - exp(2*t)/3)",
            answer_latex=r"y(t) = \frac{3 - \frac{1}{3}e^{2t}}{1 - \frac{1}{3}e^{2t}}",
        ),
        Para(
            "Running time backwards is just as informative. As t → −∞ the "
            "exponential vanishes and y → 3: the solution came out of the "
            "unstable equilibrium in the infinite past. That is what "
            "'unstable' looks like from the solution's point of view — every "
            "solution near 3 either came from it or is leaving it, and none "
            "stays."
        ),
    )),
    Section("Phase lines of familiar models", (
        Para(
            "Most of the models met so far are autonomous, and each has a "
            "phase line that says, in a picture, what the model predicts. "
            "Newton's cooling law T' = −k(T − A) has one equilibrium, the "
            "room temperature A, with f′ = −k < 0: stable, and approached with "
            "time constant 1/k. Every cup of coffee ends at room temperature, "
            "and the phase line says so in one arrow on each side of A."
        ),
        Para(
            "A body falling with linear drag, v' = g − (c/m)v, has a single "
            "stable equilibrium at the terminal velocity mg/c. With quadratic "
            "drag, v' = g − kv², the equilibria are ±√(g/k), and only the "
            "positive one is physical for a falling body; it is stable, since "
            "f′ = −2kv < 0 there. The logistic equation has 0 unstable and M "
            "stable. The Allee model P' = kP(P − M) reverses them: 0 stable, "
            "M unstable, a threshold between extinction and explosion."
        ),
        Para(
            "In each case the stable equilibria are the states the system "
            "will be found in, the unstable ones are thresholds separating "
            "different fates, and the derivative f′ at each equilibrium is a "
            "rate that experiment can measure. Much of applied modelling "
            "consists of exactly these three questions, asked of equations "
            "far too complicated to solve."
        ),
    )),
    Section("Stability", (
        Para(
            "Equilibria differ in how they treat nearby solutions, and the "
            "difference is the whole practical content of the phase line. An "
            "equilibrium where nearby solutions stay nearby — and in fact move "
            "closer — is one the system can actually be observed in, because "
            "small disturbances die away. One that nearby solutions leave is "
            "unobservable in practice: like a pencil balanced on its point, it "
            "exists as a solution but never persists."
        ),
        Box(
            "definition", "Stable, unstable, semi-stable",
            "An equilibrium c is *stable* (an attractor, or sink) if solutions "
            "starting close enough to c approach c as t → ∞. It is *unstable* "
            "(a repeller, or source) if solutions starting arbitrarily close "
            "move away. It is *semi-stable* if it attracts from one side and "
            "repels from the other.",
        ),
        Para(
            "On the phase line these are read off the arrows: a stable "
            "equilibrium has arrows pointing towards it on both sides, an "
            "unstable one arrows pointing away on both sides, and a "
            "semi-stable one an arrow in on one side and out on the other. "
            "For y' = (y − 1)(y − 3), 1 is stable and 3 is unstable. For the "
            "logistic equation, 0 is unstable and M is stable, which is the "
            "whole story of logistic growth in one sentence."
        ),
        Worked(
            "A semi-stable equilibrium",
            "Analyse y' = (y − 1)² and solve it with y(0) = 0.",
            (
                Step("The only equilibrium is 1, and f = (y − 1)² ≥ 0 on both "
                     "sides of it: arrows up below 1 and up above 1. So 1 "
                     "attracts from below and repels above — semi-stable."),
                Step("Separate: dy/(y − 1)² = dt, so −1/(y − 1) = t + C. At "
                     "t = 0, y = 0 gives 1 = C, so y − 1 = −1/(t + 1).",
                     r"y = 1 - \frac{1}{t + 1}"),
                Step("The solution creeps up to 1 but only like 1/t, far more "
                     "slowly than the exponential approach to a stable "
                     "equilibrium. Started just above 1, it would instead "
                     "blow up in finite time."),
            ),
            equation="y' = (y - 1)**2", conditions="y(0) = 0",
            answer="t/(t + 1)", answer_latex=r"y(t) = \frac{t}{t + 1}",
        ),
        Box(
            "warning", "Semi-stable is not stable",
            "An equilibrium that attracts from one side is sometimes "
            "carelessly called stable. It is not: a disturbance on the wrong "
            "side, however small, sends the solution away. In applications a "
            "semi-stable equilibrium is usually a sign that a parameter is "
            "sitting exactly at a bifurcation, and the smallest change of it "
            "will destroy the equilibrium or split it in two.",
        ),
    )),
    Section("The derivative test", (
        Para(
            "Reading arrows is reliable, but there is a quicker test that "
            "needs only one derivative. Near an equilibrium c, write "
            "y = c + u with u small. Taylor's theorem gives f(c + u) ≈ "
            "f(c) + f′(c)u = f′(c)u, since f(c) = 0. So the small deviation "
            "u obeys u' ≈ f′(c)u, the natural growth equation, whose "
            "solutions grow if f′(c) > 0 and decay if f′(c) < 0."
        ),
        Box(
            "theorem", "Linearised stability",
            "Let c be an equilibrium of y' = f(y), with f′ continuous. If "
            "f′(c) < 0, c is stable and nearby solutions approach it "
            "exponentially, like e^(f′(c)t). If f′(c) > 0, c is unstable. If "
            "f′(c) = 0, the test decides nothing.",
            r"u' \approx f'(c)\, u \;\Longrightarrow\; u \approx u_0\, "
            r"e^{f'(c)\, t}",
        ),
        Para(
            "For y' = (y − 1)(y − 3), f′(y) = 2y − 4, so f′(1) = −2 < 0 "
            "(stable) and f′(3) = 2 > 0 (unstable), agreeing with the arrows. "
            "The number itself carries information too: near y = 1 the "
            "deviation shrinks like e^(−2t), so each time unit it falls by a "
            "factor of about 7.4. For the logistic equation f′(M) = −kM, so "
            "a population disturbed from its capacity returns with time "
            "constant 1/(kM)."
        ),
        Para(
            "The inconclusive case is exactly the semi-stable one above: for "
            "f(y) = (y − 1)², f′(1) = 0. And it is not only semi-stable "
            "equilibria that give f′(c) = 0. For y' = −y³, f′(0) = 0 and yet 0 "
            "is stable, attracting from both sides; for y' = y³ it is "
            "unstable. When the derivative vanishes, go back to the signs of f "
            "on either side, which always decide."
        ),
        Worked(
            "Three equilibria",
            "Classify the equilibria of y' = y³ − y and solve it from "
            "y(0) = 1/2.",
            (
                Step("f(y) = y(y − 1)(y + 1) vanishes at −1, 0 and 1. "
                     "f′(y) = 3y² − 1 gives f′(−1) = 2, f′(0) = −1 and "
                     "f′(1) = 2: the outer two are unstable, 0 is stable.",
                     r"f'(y) = 3y^{2} - 1"),
                Step("Between 0 and 1, f < 0, so y decreases towards 0. The "
                     "equation is Bernoulli with n = 3: v = y^(−2) satisfies "
                     "v' − 2v = −2, so v = 1 + Ce^(2t), and v(0) = 4 gives C = 3.",
                     r"v = 1 + 3e^{2t}"),
                Step("So y = 1/√(1 + 3e^(2t)), which decays to 0 like e^(−t) — "
                     "the rate f′(0) = −1 predicted."),
            ),
            equation="y' = y**3 - y", conditions="y(0) = 1/2",
            answer="1/sqrt(1 + 3*exp(2*t))",
            answer_latex=r"y(t) = \frac{1}{\sqrt{1 + 3e^{2t}}}",
        ),
    )),
    Section("A stable equilibrium in practice", (
        Para(
            "Stable equilibria are what systems settle into, and many "
            "practical questions are simply: where is the stable equilibrium, "
            "and how fast is it approached? The phase line answers both "
            "without solving, and solving confirms it."
        ),
        Worked(
            "Continuous infusion",
            "A drug is infused at 5 mg per hour and eliminated at a rate "
            "proportional to the amount present, 20% per hour: "
            "y' = 5 − y/5, y(0) = 0. Where does the amount settle, and how "
            "fast?",
            (
                Step("The equilibrium is y = 25 mg, and f′ = −1/5 < 0, so it "
                     "is stable, approached like e^(−t/5): a time constant of "
                     "5 hours."),
                Step("Solving (linear, integrating factor e^(t/5)) confirms "
                     "it: y = 25 + Ce^(−t/5), and y(0) = 0 gives C = −25.",
                     r"y = 25\left(1 - e^{-t/5}\right)"),
            ),
            equation="y' = 5 - y/5", conditions="y(0) = 0",
            answer="25 - 25*exp(-t/5)", answer_latex=r"y(t) = 25 - 25e^{-t/5}",
        ),
        Para(
            "The equilibrium level 25 mg is the infusion rate divided by the "
            "elimination rate, a formula a pharmacologist uses daily. The "
            "time constant says the level is within 5% of it after three time "
            "constants, fifteen hours, which is why a continuously infused "
            "drug takes most of a day to reach its steady effect. Neither "
            "number needed the solution; both are properties of the "
            "equilibrium."
        ),
    )),
    Section("When equilibria collide: bifurcation", (
        Para(
            "If the equation contains a parameter, the equilibria move as the "
            "parameter changes, and occasionally something qualitative "
            "happens: two equilibria meet and vanish, or one splits into "
            "three. Such a parameter value is a *bifurcation*. The harvested "
            "logistic equation of the last lesson is the standard example, "
            "and the phase line shows it plainly."
        ),
        Display(r"y' = y(1 - y) - h, \qquad y^{*} = \frac{1 \pm \sqrt{1 - 4h}}{2}"),
        Para(
            "For h < 1/4 there are two equilibria, the upper stable and the "
            "lower unstable. As h increases they move together; at h = 1/4 "
            "they coincide at y = 1/2, where f′ = 0 and the equilibrium is "
            "semi-stable; for h > 1/4 there are none, the graph of f lies "
            "wholly below the axis, and every solution decreases to −∞ — the "
            "population collapses. Plotting the equilibria against h gives a "
            "*bifurcation diagram*, the picture Unit 8 builds for systems."
        ),
        Plot(
            "Bifurcation diagram for y' = y(1 − y) − h",
            "The equilibria (1 ± √(1 − 4h))/2 against the harvest h. The upper "
            "branch is stable and the lower unstable; they meet at h = 1/4 and "
            "vanish. To the right of the fold there is no equilibrium at all — "
            "the phase line has one downward arrow.",
            (Curve("(1 + sqrt(1 - 4*t))/2", "stable"),
             Curve("(1 - sqrt(1 - 4*t))/2", "unstable")),
            t=(0.0, 0.3), xlabel="harvest h", ylabel="equilibrium y*",
            ylim=(-0.05, 1.05),
        ),
        Para(
            "Folds are not the only way equilibria can change. For "
            "y' = ry − y³ the origin is the only equilibrium when r < 0, and it "
            "is stable. As r passes 0 it becomes unstable, and two new stable "
            "equilibria ±√r appear on either side of it. One equilibrium has "
            "become three: a *pitchfork*. Physically it is a beam that buckles "
            "under a load — straight while the load is small, and bent to one "
            "side or the other once the load passes a critical value. Unit 8 "
            "gathers these patterns together and shows that, near any "
            "bifurcation, almost every equation looks like one of a handful "
            "of simple forms."
        ),
    )),
    Section("Summary", (
        Para(
            "An autonomous equation y' = f(y) is unchanged by shifting time, "
            "so its solutions are organised by their values alone. The "
            "equilibria are the zeros of f; between them f has one sign, and "
            "solutions move monotonically towards one equilibrium or off to "
            "infinity, never crossing another. The phase line records this "
            "with arrows. An equilibrium is stable if the arrows point in on "
            "both sides, unstable if out, semi-stable if mixed; the derivative "
            "test f′(c) < 0 or > 0 decides quickly and gives the rate, and "
            "f′(c) = 0 sends you back to the arrows. When a parameter moves "
            "two equilibria together, they can meet and vanish — a "
            "bifurcation — and the system's long-run behaviour changes all "
            "at once. None of this required solving the equation, which is "
            "the point: it works just as well when no solution formula exists."
        ),
    )),
)


POPULATION = (
    Section("From a sentence to an equation", (
        Para(
            "Population models are the oldest applications of differential "
            "equations outside physics, and they are the best place to learn "
            "modelling, because every assumption is a sentence you can "
            "question. The quantity is a population P(t) — of bacteria, of "
            "fish, of people — treated as a smoothly varying number, which is "
            "reasonable when it is large. Its rate of change is births minus "
            "deaths per unit time, and each modelling decision is a decision "
            "about how those two rates depend on P."
        ),
        Para(
            "Write the birth rate as β(t)P and the death rate as δ(t)P, where "
            "β and δ are rates *per individual*: births per person per year, "
            "deaths per person per year. Then the equation is P' = (β − δ)P. "
            "Everything in this lesson comes from different assumptions about "
            "β and δ — constant, falling as the population crowds, or rising "
            "as individuals meet more often — and each assumption gives a "
            "different equation with a different long-run fate."
        ),
        Display(r"\frac{dP}{dt} = (\beta - \delta)\, P", "1"),
        Box(
            "definition", "Per-capita rates",
            "The *per-capita* (per individual) birth and death rates β and δ "
            "are births and deaths per unit time divided by the population. "
            "Their difference r = β − δ is the per-capita growth rate: P'/P.",
            r"r = \frac{P'}{P} = \beta - \delta",
        ),
    )),
    Section("Natural growth", (
        Para(
            "The simplest assumption is that β and δ are constants: each "
            "individual has the same chance of reproducing or dying whatever "
            "the size of the population. Then r = β − δ is constant, and (1) "
            "is the natural growth equation P' = rP from Unit 1, whose "
            "solution is exponential."
        ),
        Box(
            "theorem", "Natural growth",
            "If P' = rP with r constant and P(0) = P₀, then P(t) = P₀e^(rt). "
            "For r > 0 the population doubles every ln 2 / r time units; for "
            "r < 0 it halves every ln 2 / |r|.",
            r"P(t) = P_0\, e^{r t}",
        ),
        Worked(
            "A growing colony",
            "A bacterial colony of 100 cells grows at 3% per hour with no "
            "limit on food. Find P(t) and the doubling time.",
            (
                Step("r = 0.03 per hour, so P' = 0.03P with P(0) = 100.",
                     r"P(t) = 100\, e^{0.03 t}"),
                Step("It doubles when e^(0.03t) = 2, that is after "
                     "t = ln 2/0.03 ≈ 23.1 hours — and doubles again every "
                     "23.1 hours after that, whatever its size.",
                     r"t_{2} = \frac{\ln 2}{0.03} \approx 23.1 \text{ h}"),
            ),
            equation="y' = 3*y/100", conditions="y(0) = 100",
            answer="100*exp(3*t/100)", answer_latex=r"P(t) = 100\, e^{0.03t}",
        ),
        Para(
            "Exponential growth is a good model for a short time and a "
            "terrible one for a long time. After ten days the colony above "
            "would have about 100·e^(7.2) ≈ 134,000 cells, which is plausible; "
            "after a year, 100·e^(262.8), a number with 116 digits, which is "
            "not. Something always runs out, and the next models are "
            "attempts to say what, and how its running out feeds back into "
            "the growth rate."
        ),
    )),
    Section("Doubling times and the rule of 70", (
        Para(
            "Exponential growth is so common, and so commonly misjudged, that "
            "it is worth having a feel for it. The doubling time ln 2 / r "
            "depends only on the rate, not on the size, and ln 2 ≈ 0.693. With "
            "r written as a percentage per year, the doubling time in years is "
            "about 70 divided by the percentage: 1% a year doubles in about 70 "
            "years, 2% in about 35, 7% in about 10. This *rule of 70* is the "
            "logarithm doing mental arithmetic for you."
        ),
        Display(r"t_{2} = \frac{\ln 2}{r} \approx \frac{70}{100 r}"),
        Para(
            "The rule makes the character of exponential growth vivid. A "
            "quantity growing at 7% a year is 2 times larger in a decade, 4 "
            "times in two decades, 1024 times in a century. Whatever fraction "
            "of a resource it uses now, ten doublings multiply that fraction "
            "by a thousand, so exponential growth in a finite world is always "
            "a temporary state. This is not an argument about ecology; it is "
            "arithmetic, and it is why the logistic and harvesting models "
            "that follow exist."
        ),
        Para(
            "Decay has the same structure run backwards. A quantity decaying "
            "at a rate r halves every ln 2 / r, and after ten half-lives about "
            "a thousandth of it is left. Radioactive dating, drug clearance "
            "from the bloodstream, the cooling of a cup of coffee towards room "
            "temperature — all are this one equation with a negative rate, "
            "and the half-life is the one number that characterises each."
        ),
    )),
    Section("The logistic equation", (
        Para(
            "Suppose the per-capita birth rate falls as the population "
            "grows, because individuals compete for food and space. The "
            "simplest such assumption is a linear decrease, β = β₀ − β₁P, "
            "with the death rate constant. Then the per-capita growth rate "
            "r = β₀ − δ − β₁P decreases linearly with P and reaches zero at "
            "some population M. That is the *logistic* model."
        ),
        Box(
            "definition", "Logistic equation",
            "The logistic equation has per-capita growth rate proportional to "
            "the room left, M − P. The constant M is the *carrying capacity*, "
            "the population the environment can sustain, and k > 0 measures "
            "how quickly the population responds.",
            r"\frac{dP}{dt} = k P (M - P)",
        ),
        Para(
            "It is often written P' = rP(1 − P/M) with r = kM, which shows the "
            "two regimes plainly. When P is small, 1 − P/M ≈ 1 and the "
            "population grows exponentially at rate r. As P approaches M, "
            "1 − P/M approaches 0 and growth stops. Before solving anything "
            "the equation already says a lot: P = 0 and P = M are equilibrium "
            "solutions, and any population strictly between them increases "
            "towards M without ever reaching it, by the non-crossing theorem."
        ),
        Box(
            "theorem", "Solution of the logistic equation",
            "The solution of P' = kP(M − P) with P(0) = P₀ > 0 is given below. "
            "For every P₀ > 0 it tends to M as t → ∞.",
            r"P(t) = \frac{M P_0}{P_0 + (M - P_0)\, e^{-kMt}}",
        ),
        Box(
            "proof", "",
            "The equation is separable. By partial fractions, "
            "1/(P(M − P)) = (1/M)(1/P + 1/(M − P)), so integrating gives "
            "(1/M) ln|P/(M − P)| = kt + C, that is P/(M − P) = Ae^(kMt). At "
            "t = 0 the left side is P₀/(M − P₀), which fixes A. Solving for P "
            "gives the formula; as t → ∞ the exponential e^(−kMt) → 0 and "
            "P → MP₀/P₀ = M.",
        ),
        Worked(
            "A population approaching its capacity",
            "A lake can support 200 fish. A population of 50 obeys "
            "P' = P(200 − P)/2500, with t in months. Find P(t) and the time "
            "at which it reaches 100.",
            (
                Step("Here M = 200 and k = 1/2500, so kM = 0.08 per month. The "
                     "formula gives",
                     r"P = \frac{200 \cdot 50}{50 + 150\, e^{-0.08t}} = "
                     r"\frac{200}{1 + 3e^{-0.08t}}"),
                Step("P = 100 when 1 + 3e^(−0.08t) = 2, so e^(−0.08t) = 1/3 and "
                     "t = ln 3/0.08 ≈ 13.7 months.",
                     r"t = \frac{\ln 3}{0.08} \approx 13.7"),
            ),
            equation="y' = y*(200 - y)/2500", conditions="y(0) = 50",
            answer="200/(1 + 3*exp(-2*t/25))",
            answer_latex=r"P(t) = \frac{200}{1 + 3e^{-0.08t}}",
        ),
        Para(
            "The time to reach M/2 = 100 is special. Differentiating P' = "
            "kP(M − P) with respect to P shows that the growth rate P' is "
            "largest when P = M/2, so the population curve has its inflection "
            "point there: it grows faster and faster until it is half full, "
            "and slower and slower afterwards. That S-shape is the signature "
            "of logistic growth, and it is what one looks for in data."
        ),
        Worked(
            "Starting above capacity",
            "The same lake is overstocked with 300 fish. Find P(t).",
            (
                Step("With P₀ = 300 the formula gives MP₀ = 60000 and "
                     "M − P₀ = −100:",
                     r"P = \frac{60000}{300 - 100\, e^{-0.08t}} = "
                     r"\frac{200}{1 - \frac{1}{3}e^{-0.08t}}"),
                Step("The denominator is less than 1 and increases to 1, so P "
                     "decreases from 300 towards 200: an overcrowded "
                     "population dies back to the capacity."),
            ),
            equation="y' = y*(200 - y)/2500", conditions="y(0) = 300",
            answer="200/(1 - exp(-2*t/25)/3)",
            answer_latex=r"P(t) = \frac{200}{1 - \frac{1}{3}e^{-0.08t}}",
        ),
        Plot(
            "Logistic populations approach the carrying capacity",
            "Solutions of P' = P(200 − P)/2500 from 10, 50, 150 and 300 fish. "
            "Those below 200 follow an S-curve, steepest where they pass "
            "100 = M/2; the one above 200 decays towards it. The equilibrium "
            "P = 200 attracts every positive start.",
            (Curve("200/(1 + 19*exp(-0.08*t))", "P₀ = 10"),
             Curve("200/(1 + 3*exp(-0.08*t))", "P₀ = 50"),
             Curve("200/(1 + exp(-0.08*t)/3)", "P₀ = 150"),
             Curve("200/(1 - exp(-0.08*t)/3)", "P₀ = 300"),
             Curve("200 + 0*t", "M = 200")),
            t=(0.0, 100.0), ylabel="population", ylim=(0.0, 320.0),
        ),
        Figure("growth_models",
               "Compare the models directly: natural growth, logistic growth "
               "and its capacity, with the parameters on sliders."),
    )),
    Section("Estimating the parameters", (
        Para(
            "A model is only useful once its constants are known, and they "
            "come from data. For the logistic equation there is a neat trick. "
            "Dividing by P gives P'/P = kM − kP: the per-capita growth rate is "
            "a *linear* function of P. So if the growth rate of a population "
            "is measured at a few different sizes and plotted against P, the "
            "points should lie on a line, whose intercept is kM = r and whose "
            "slope is −k. Where the line crosses zero is M."
        ),
        Display(r"\frac{P'}{P} = kM - kP"),
        Para(
            "Suppose, for instance, a population of 40 is found to be growing "
            "at 2.4 per month, and a population of 120 at 3.2 per month. The "
            "per-capita rates are 2.4/40 = 0.06 and 3.2/120 ≈ 0.0267. The "
            "line through (40, 0.06) and (120, 0.0267) has slope "
            "−0.0333/80 ≈ −0.000417, so k ≈ 0.000417, and it reaches zero at "
            "P = 40 + 0.06/0.000417 ≈ 184. The data suggest a carrying "
            "capacity of about 184."
        ),
        Box(
            "remark", "Models are tested against data, not the other way round",
            "If the per-capita growth rates do not lie close to a line, the "
            "logistic model is the wrong model, and no choice of k and M will "
            "rescue it. The linear plot is a test of the model as well as a way "
            "to fit it.",
        ),
    )),
    Section("Other assumptions, other fates", (
        Para(
            "The logistic model assumed the birth rate falls as the "
            "population grows. The opposite can happen. In a sparse "
            "population individuals may struggle to find mates, so the "
            "per-capita birth rate *rises* with P. If births are proportional "
            "to P² — to the number of encounters — and deaths are "
            "proportional to P, the equation becomes P' = kP² − δP = "
            "kP(P − M) with M = δ/k. The sign of the bracket has flipped, and "
            "so has everything else."
        ),
        Worked(
            "Extinction below a threshold",
            "Solve P' = P(P − 100)/1000 with P(0) = 50.",
            (
                Step("This is the logistic equation with time reversed, and "
                     "the same separation gives P/(P − M) = Ae^(kMt) with "
                     "kM = 0.1. At t = 0, 50/(−50) = −1, so A = −1.",
                     r"\frac{P}{P - 100} = -e^{0.1t}"),
                Step("Solving for P gives P = 100/(1 + e^(0.1t)), which "
                     "decreases to zero. A population below the threshold "
                     "M = 100 dies out."),
            ),
            equation="y' = y*(y - 100)/1000", conditions="y(0) = 50",
            answer="100/(1 + exp(t/10))",
            answer_latex=r"P(t) = \frac{100}{1 + e^{0.1t}}",
        ),
        Para(
            "Above the threshold the story is even more dramatic: the "
            "population does not level off but explodes in finite time. This "
            "*doomsday* behaviour is the same blow-up as y' = y² in Unit 1. "
            "Real populations do not reach infinity, of course, which says the "
            "model stops being valid before then; but the threshold "
            "behaviour below it is real, and is called the Allee effect in "
            "ecology. It is why a species reduced to a handful of individuals "
            "can go extinct even when conditions have improved."
        ),
        Worked(
            "Finite-time explosion",
            "With births proportional to P² and no deaths, P' = P²/2000 and "
            "P(0) = 20. Find P(t).",
            (
                Step("Separate: dP/P² = dt/2000, so −1/P = t/2000 + C, and "
                     "P(0) = 20 gives C = −1/20.",
                     r"-\frac{1}{P} = \frac{t}{2000} - \frac{1}{20}"),
                Step("So P = 20/(1 − t/100), which blows up at t = 100 — the "
                     "model's doomsday."),
            ),
            equation="y' = y**2/2000", conditions="y(0) = 20",
            answer="20/(1 - t/100)", answer_latex=r"P(t) = \frac{20}{1 - t/100}",
        ),
        Plot(
            "Three models from the same starting population",
            "From P(0) = 20: natural growth P' = 0.02P, logistic growth "
            "towards M = 200, and the doomsday model P' = P²/2000, which "
            "escapes to infinity at t = 100. All three start at 20, with "
            "slopes 0.4, 0.36 and 0.2, and for the first ten years they stay "
            "within 10% of each other; later they part company completely. "
            "Short-term data can barely tell them apart.",
            (Curve("20*exp(0.02*t)", "natural growth"),
             Curve("200/(1 + 9*exp(-0.02*t))", "logistic, M = 200"),
             Curve("Piecewise((20/(1 - t/100), t < 90), (nan, True))", "doomsday")),
            t=(0.0, 120.0), ylabel="population", ylim=(0.0, 250.0),
        ),
    )),
    Section("Which model is right?", (
        Para(
            "Since the models agree early on, the way to tell them apart is "
            "not to watch P but to watch the per-capita growth rate P'/P as "
            "the population changes. Natural growth predicts it stays "
            "constant; the logistic model predicts it falls linearly as P "
            "rises; the Allee model predicts it rises with P below a "
            "threshold. Each is a different straight or flat line on a plot of "
            "P'/P against P, and a handful of measurements at different "
            "population sizes decides between them long before the "
            "populations themselves diverge."
        ),
    )),
    Section("Epidemics: the same shape again", (
        Para(
            "The logistic curve appears far beyond ecology, and the spread of "
            "an infection is the most instructive case. Suppose a population "
            "of N people contains I infected ones and N − I susceptible ones, "
            "and that nobody recovers during the period of interest. New "
            "infections happen when an infected person meets a susceptible "
            "one, at a rate proportional to the number of such meetings, "
            "I(N − I). The equation is I' = βI(N − I): the logistic equation, "
            "with the carrying capacity N the whole population."
        ),
        Display(r"\frac{dI}{dt} = \beta\, I\, (N - I)"),
        Para(
            "So the early phase of an outbreak is exponential — each case "
            "produces cases at a steady rate while nearly everyone is "
            "susceptible — and the growth slows as the pool of susceptibles "
            "is used up, with the fastest spread when half the population is "
            "infected. The same equation describes the spread of a rumour, "
            "the adoption of a new technology and the progress of an "
            "autocatalytic chemical reaction: anything whose rate is "
            "proportional both to how much has happened and to how much is "
            "left to happen."
        ),
        Para(
            "Adding recovery turns this into the SIR model, a *system* of "
            "three equations for the susceptible, infected and recovered, "
            "which is in the application's catalogue and in the Solver Lab. "
            "Its infected curve rises and then falls, rather than levelling "
            "off, because recovered people stop spreading the infection. "
            "Systems like it are the subject of Units 6 and 8; the logistic "
            "equation is what the SIR model looks like in its first weeks."
        ),
    )),
    Section("Harvesting", (
        Para(
            "A population that is fished, hunted or harvested loses "
            "individuals at a rate set from outside. With a constant harvest "
            "h the logistic equation becomes P' = rP(1 − P/M) − h. The right "
            "side is a downward-shifted parabola in P, and its zeros — the "
            "equilibria — move together as h increases. At a critical harvest "
            "they meet, and above it they disappear: every population, however "
            "large, is driven to extinction."
        ),
        Box(
            "theorem", "Maximum sustainable harvest",
            "For P' = rP(1 − P/M) − h the equilibria are real exactly when "
            "h ≤ rM/4. The largest constant harvest the population can sustain "
            "is rM/4, taken with the population held at M/2.",
            r"h_{\max} = \frac{r M}{4}",
        ),
        Para(
            "The argument is the quadratic formula. Setting the right side to "
            "zero gives (r/M)P² − rP + h = 0, whose discriminant r² − 4rh/M is "
            "non-negative exactly when h ≤ rM/4. At the critical harvest the "
            "two equilibria merge at P = M/2 — where, as noted earlier, "
            "logistic growth is fastest. This is the simplest example of a "
            "*bifurcation*, a qualitative change as a parameter crosses a "
            "value, and the next lesson and Unit 8 return to it."
        ),
        Worked(
            "How much can the lake yield?",
            "For the lake of Example 2 (r = 0.08 per month, M = 200), find the "
            "maximum sustainable harvest, and the equilibria when 3 fish a "
            "month are taken.",
            (
                Step("The maximum is rM/4 = 0.08 × 200/4 = 4 fish per month.",
                     r"h_{\max} = \frac{0.08 \times 200}{4} = 4"),
                Step("With h = 3 the equilibria solve 0.08P(1 − P/200) = 3, "
                     "that is 0.0004P² − 0.08P + 3 = 0:",
                     r"P = \frac{0.08 \pm \sqrt{0.0064 - 0.0048}}{0.0008} = "
                     r"\frac{0.08 \pm 0.04}{0.0008}"),
                Step("So P = 150 and P = 50. Between them the right side is "
                     "positive, so a population in (50, 150) grows to 150; "
                     "above 150 it falls back to 150; below 50 it is driven to "
                     "extinction. 150 is stable and 50 is the threshold."),
            ),
        ),
        Para(
            "The example shows the price of harvesting in plain numbers. "
            "Without it the lake settles at 200 fish and recovers from any "
            "disturbance that leaves at least one. With 3 a month taken it "
            "settles at 150, and a disturbance that pushes it below 50 is "
            "fatal. At 4 a month the two equilibria have merged at 100 and the "
            "slightest shortfall is fatal; above 4, nothing survives."
        ),
        Box(
            "warning", "Harvesting close to the maximum is dangerous",
            "At h slightly below rM/4 the stable equilibrium and the unstable "
            "one are close together, and a bad year that knocks the population "
            "below the unstable one sends it to extinction. Fisheries managed "
            "at their calculated maximum have collapsed for exactly this "
            "reason.",
        ),
    )),
    Section("Summary", (
        Para(
            "Population models start from P' = (β − δ)P and differ in how "
            "the per-capita rates depend on P. Constant rates give natural "
            "growth, P₀e^(rt), fine for a short time. A birth rate falling "
            "linearly with P gives the logistic equation P' = kP(M − P), whose "
            "solutions approach the carrying capacity M along an S-curve with "
            "its inflection at M/2. A birth rate rising with P gives a "
            "threshold: extinction below it, explosion above. Constant "
            "harvesting shifts the logistic parabola down, and above rM/4 no "
            "equilibrium survives. In every case the equilibria and their "
            "stability tell most of the story before any formula is found — "
            "which is the subject of the next lesson."
        ),
    )),
)
