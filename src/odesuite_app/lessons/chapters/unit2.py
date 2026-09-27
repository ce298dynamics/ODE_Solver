"""Unit 2 chapters -- models and numerical methods (Edwards ch. 2)."""

from __future__ import annotations

from ..chapter import Box, Curve, Display, Figure, Para, Plot, Section, Step, Worked

__all__ = ["POPULATION"]


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
