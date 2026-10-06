"""The names a question can ask for, and what each one means.

Four tables of prose. Three are vocabularies -- sets of labels a `Case` can
claim, with the criterion for each -- and the fourth is the list of ways an
answer goes wrong. All of them exist so that a drill is built out of the
application's own words rather than out of an author's memory of them.

**Every vocabulary has an oracle, and the tests use it.** That is the whole
reason these are keyed the way they are:

* `METHODS` is keyed by the technique names `steps.TECHNIQUES` uses -- the
  sympy spellings, not the textbook ones -- because those are what the
  narrator dispatches on. A case claiming `1st_linear` is put through
  `classify_ode` and `steps.preferred_hint`, the same route the narrator
  takes, and has to come back as `1st_linear`.
* `PORTRAITS` is keyed by the strings `analysis.classify` returns, so a case
  claiming a stable spiral is checked by taking the matrix's eigenvalues and
  asking the application what it would call them.
* `DAMPING` is keyed by the four regimes, checked against the sign of the
  discriminant.

So a question here cannot quietly disagree with the tool that would answer it.
A case whose classification changed under a sympy upgrade becomes a failing
test rather than a drill that marks the right answer wrong.

`FAULTS` is keyed by names of its own, because a mistake is not a technique.
Each says what that mistake *looks like*, phrased as something to check rather
than as a verdict, since the same line is shown whichever option was picked.

Prose only -- no sympy, no Qt -- like every other module in this package.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Label", "METHODS", "PORTRAITS", "DAMPING", "EQUILIBRIA", "VOCABULARIES",
           "Fault", "FAULTS"]


@dataclass(frozen=True)
class Label:
    """One name a question can ask for, and the criterion for it."""

    #: What it is called. For `METHODS` this must agree with `steps.TITLES`,
    #: and for `PORTRAITS` the key itself is what `analysis.classify` says.
    title: str
    #: When it applies, in one sentence.
    #:
    #: This is the content of the question rather than decoration on it. The
    #: name is a label; the criterion is the thing that has to become
    #: automatic, and it is what the drill shows for an option that was picked
    #: and was wrong.
    requires: str


#: In teaching order, which is `steps.TECHNIQUES` order.
METHODS: dict[str, Label] = {
    "separable": Label(
        title="Separation of variables",
        requires="Separation is for equations that can be written "
                 "y' = f(t)·g(y) — every y in one factor and every t in the "
                 "other, with nothing mixing the two.",
    ),
    "1st_linear": Label(
        title="Integrating factor",
        requires="An integrating factor is for equations linear in y: "
                 "y' + p(t)·y = q(t), where y and y' appear to the first "
                 "power and are never multiplied by each other.",
    ),
    "1st_exact": Label(
        title="Exact equation",
        requires="An equation is exact when it reads M(t, y) + N(t, y)·y' = 0 "
                 "with ∂M/∂y = ∂N/∂t, so the left-hand side is already the "
                 "derivative of some F(t, y).",
    ),
    "1st_homogeneous_coeff_best": Label(
        title="Homogeneous substitution",
        requires="A homogeneous equation depends on t and y only through the "
                 "ratio y/t — divide the top and bottom by the highest power "
                 "of t and see whether anything but y/t is left. Then "
                 "v = y/t separates it.",
    ),
    "Bernoulli": Label(
        title="Bernoulli substitution",
        requires="Bernoulli is y' + p(t)·y = q(t)·yⁿ with n neither 0 nor 1: "
                 "linear apart from that one power of y, which the "
                 "substitution v = y¹⁻ⁿ removes.",
    ),
    "nth_linear_constant_coeff_homogeneous": Label(
        title="Characteristic roots",
        requires="Constant coefficients and nothing on the right-hand side: "
                 "try y = e^(rt) and the equation becomes a polynomial in r.",
    ),
    "nth_linear_constant_coeff_undetermined_coefficients": Label(
        title="Undetermined coefficients",
        requires="For constant coefficients forced by a polynomial, an "
                 "exponential, a sine or cosine, or a product of those — the "
                 "forms whose derivatives stay inside a finite family, so a "
                 "trial solution can be written down and its coefficients "
                 "solved for.",
    ),
    "nth_linear_constant_coeff_variation_of_parameters": Label(
        title="Variation of parameters",
        requires="For a forcing term with no finite trial family — sec t, "
                 "tan t, a quotient. It costs two integrals and needs the "
                 "homogeneous solutions first, since it builds the particular "
                 "one out of them.",
    ),
    "nth_linear_euler_eq_homogeneous": Label(
        title="Cauchy-Euler equation",
        requires="Each derivative carries the matching power of t: "
                 "t²·y'' + a·t·y' + b·y. Try y = t^r and it becomes a "
                 "polynomial in r.",
    ),
    "reduction_of_order": Label(
        title="Reduction of order",
        requires="Linear and homogeneous with coefficients that change with "
                 "t in no pattern a trial fits — but with one solution you "
                 "can find. Set y = v·y₁ and the equation drops to first "
                 "order in v'.",
    ),
}


#: Keyed by what `analysis.classify` returns, so the Phase Portrait screen and
#: this drill cannot call the same picture different things.
PORTRAITS: dict[str, Label] = {
    "saddle": Label(
        title="Saddle",
        requires="A saddle has real eigenvalues of opposite sign — one "
                 "direction runs in, the other runs out, and every other "
                 "trajectory turns away. The determinant is negative, which "
                 "is enough on its own.",
    ),
    "stable node": Label(
        title="Stable node",
        requires="A stable node has two real negative eigenvalues: every "
                 "trajectory comes in without turning, tangent to the "
                 "direction of the slower one.",
    ),
    "unstable node": Label(
        title="Unstable node",
        requires="An unstable node has two real positive eigenvalues — the "
                 "stable node run backwards, with everything leaving along "
                 "the faster direction.",
    ),
    "stable spiral": Label(
        title="Stable spiral",
        requires="A stable spiral has a complex pair with negative real "
                 "part: the imaginary part turns the trajectory and the real "
                 "part shrinks it, so it winds inwards.",
    ),
    "unstable spiral": Label(
        title="Unstable spiral",
        requires="An unstable spiral has a complex pair with positive real "
                 "part — turning, and growing as it turns.",
    ),
    "centre": Label(
        title="Centre",
        requires="A centre has a purely imaginary pair: turning with nothing "
                 "shrinking or growing, so the trajectories close. Trace "
                 "zero and determinant positive.",
    ),
}


#: The four regimes of a free vibration, by the sign of c² − 4mk.
DAMPING: dict[str, Label] = {
    "undamped": Label(
        title="Undamped",
        requires="No damping term at all: the roots are a pure imaginary "
                 "pair and the motion is a sine that never decays.",
    ),
    "underdamped": Label(
        title="Underdamped",
        requires="c² < 4mk. The roots are complex, and the motion oscillates "
                 "inside a decaying envelope — it crosses the equilibrium "
                 "infinitely often.",
    ),
    "critically damped": Label(
        title="Critically damped",
        requires="c² = 4mk exactly. One repeated real root, and the fastest "
                 "return to equilibrium that does not overshoot. The knife "
                 "edge: any less damping and it oscillates.",
    ),
    "overdamped": Label(
        title="Overdamped",
        requires="c² > 4mk. Two distinct real negative roots, two decaying "
                 "exponentials, and no oscillation — the heavier the damping "
                 "the slower the return.",
    ),
}


#: What linearising says about one equilibrium of a nonlinear system.
#:
#: The five hyperbolic pictures, which the linearisation decides, and the one
#: answer it cannot give. A linear centre is not on the menu as a centre: for
#: a nonlinear system it is the case where the Jacobian is silent, and calling
#: it a centre is the mistake the almost-linear lesson exists to prevent.
EQUILIBRIA: dict[str, Label] = {
    **{key: PORTRAITS[key] for key in ("saddle", "stable node", "unstable node",
                                        "stable spiral", "unstable spiral")},
    "undecided": Label(
        title="Not decided by linearising",
        requires="The Jacobian at the point has an eigenvalue with zero real "
                 "part — a purely imaginary pair, as for a linear centre, or "
                 "a zero eigenvalue. The equilibrium is then not hyperbolic, "
                 "and the nonlinear terms decide: a true centre, a spiral "
                 "either way, or something else.",
    ),
}


#: What a `ClassifyTemplate.table` may name.
VOCABULARIES: dict[str, dict[str, Label]] = {
    "methods": METHODS,
    "portraits": PORTRAITS,
    "damping": DAMPING,
    "equilibria": EQUILIBRIA,
}


@dataclass(frozen=True)
class Fault:
    """One way an answer goes wrong, named."""

    #: As it appears among the options.
    label: str
    #: What that fault looks like wherever it happens. Shown for whichever
    #: option was picked, so it reads as a thing to check rather than as a
    #: verdict on this particular answer.
    tell: str
    #: Whether an answer carrying this fault still satisfies the equation.
    #:
    #: The distinction is the whole difference between the two kinds of
    #: mistake here, and `tests/test_templates.py` holds every generated wrong
    #: answer to it: a sign error does not satisfy the equation, and a dropped
    #: constant does — it fails only the initial condition. A drill that got
    #: this backwards would be showing an answer that is actually right and
    #: asking what is wrong with it.
    solves_equation: bool = False


FAULTS: dict[str, Fault] = {
    "sign-in-exponent": Fault(
        label="The sign of an exponent is wrong.",
        tell="A sign that flips in an exponent turns decay into growth. "
             "Substituting an answer like that does not give zero: the "
             "y-term comes back with the wrong sign and nothing cancels.",
    ),
    "no-constant": Fault(
        label="The constant of integration was dropped.",
        tell="A general solution carries one arbitrary constant per order. "
             "An answer missing it can still satisfy the equation — what it "
             "cannot do is meet an initial condition, which is where this "
             "one shows itself.",
        solves_equation=True,
    ),
    "missing-particular": Fault(
        label="Only the complementary function — the particular solution is "
              "missing.",
        tell="A forced equation needs both halves. The complementary "
             "function on its own leaves exactly the forcing term behind "
             "when it is substituted, which is the residual to look for.",
    ),
    "missing-complementary": Fault(
        label="Only the particular solution — the complementary function is "
              "missing.",
        tell="A particular solution does satisfy the equation, and that is "
             "what makes this one hard to see. It carries no arbitrary "
             "constants, so there is nothing left to fit the initial "
             "conditions with.",
        solves_equation=True,
    ),
    "repeated-root": Fault(
        label="A repeated root was used twice without the factor of t.",
        tell="C₁e^(rt) + C₂e^(rt) is (C₁ + C₂)e^(rt) — one solution wearing "
             "two constants. A double root contributes e^(rt) and t·e^(rt), "
             "and without the second there is nothing to fit a second "
             "condition with.",
        solves_equation=True,
    ),
    "undivided-factor": Fault(
        label="The integrating factor was multiplied in but never divided "
              "out.",
        tell="The method ends by dividing through by μ. An answer still "
             "carrying it is the integral of μ·q rather than that integral "
             "divided by μ, and it is wrong by a factor that changes with t.",
    ),
    "real-roots-for-complex": Fault(
        label="Complex roots were written as real exponentials.",
        tell="Roots a ± bi give e^(at)·cos(bt) and e^(at)·sin(bt). Treating "
             "the imaginary part as though it were a real rate loses the "
             "oscillation entirely, and the answer no longer satisfies the "
             "equation.",
    ),
    "forcing-not-reduced": Fault(
        label="A coefficient was read off without dividing by the leading "
              "one.",
        tell="Everything the method asks for — p, q, the trial coefficients "
             "— is read off the equation written with the highest derivative "
             "alone in front. Read from 2y'' + … instead and every constant "
             "is out by that factor of 2.",
    ),
}
