# Learning Studio: what to build next

Brainstormed 2026-09-26, after the nonlinear tools underneath the app were
corrected (`22aaa03`, `ba26fed`, `a1ef058`, `fbdfbc8`). Ordered by value to a
student taking MA 266, then by how much each one reuses code that already
exists and is already checked. Sizes: S = under a session, M = a session,
L = several, XL = a unit of content.

Status is kept in this table as work lands.

| # | Item | Size | Status |
|---|---|---|---|
| L1 | Unit 8, nonlinear systems (the audit's PED-01) | XL | **done** 2026-09-26 |
| L2 | One helper for what an `EquivalenceCheck` means | S | **done** 2026-09-26 |
| L3 | Reduction of order: narrator, lesson, drill (SYM-02) | M | **done** 2026-09-26 |
| L4 | Faded worked examples: the reader writes the next step | M | **done** 2026-09-26 |
| L5 | Diagnose a wrong *number*, not only a wrong formula | S–M | **done** 2026-09-26 |
| L6 | Glossary, with every term linked to where it is taught | M | open |
| L7 | "Linearise here": zoom into an equilibrium until the flow is linear | M | open |
| L8 | Exam-readiness report built from the Leitner boxes | M | open |

---

## L1 · Unit 8 — nonlinear systems and phenomena

The gap the audit ranked first among the pedagogy items and the one that
matches what the app is *for*. `analysis.py` classifies equilibria, draws
separatrices, finds limit cycles and Lyapunov exponents; `continuation.py`
draws bifurcation diagrams; the catalogue ships Lorenz tagged chaotic. No
lesson teaches any of it: a learner meets "Hopf" as a slider tooltip.

Edwards–Penney–Calvis ch. 6 (6.1–6.4 in the 6e). Six lessons, each held to
the `FULL_DEPTH` standard the other 35 are:

1. **Equilibria and linearisation** -- the Jacobian, `jacobian_at`.
2. **Classifying equilibria, and where the linearisation lies** --
   Hartman–Grobman; the centre that is really a spiral.
3. **Nullclines and the phase plane.**
4. **Predator–prey and conservative systems** -- a conserved quantity is
   why Lotka–Volterra's centre is real.
5. **Limit cycles and Poincaré–Bendixson** -- the finder fixed today, and
   *why* a planar autonomous flow cannot be chaotic, which the Lyapunov
   verdict now enforces.
6. **Bifurcations and the road to chaos** -- saddle-node, pitchfork, Hopf
   against the diagrams; Lorenz and the predictability horizon.

The rule that has held for every unit: each stored answer has an oracle in
the tests. Here the oracle is `analysis.classify`, `find_fixed_points`,
`largest_closed_orbit` and `continuation.sweep` -- the routines just
corrected against closed forms, which is why this waited for them.

## L2 · One helper for what an `EquivalenceCheck` means

`learn_lessons._check_model` / `_check_expression` and
`learn_quiz._check_equivalent` are two copies of the three-verdict rule
(right / wrong / cannot tell). Two copies is two places for it to drift.
One function beside `symbolic.py` that turns a check into the words and the
colour, called from both.

## L3 · Reduction of order (SYM-02)

The one standard second-order technique the app does not have. It is also
the bridge to variation of parameters, which Unit 3 teaches without it. It
needs a *known solution* supplied, which no other narrator does, so it is a
narrator and an input change. Acceptance: `t²y'' − 3ty' + 4y = 0` with
`y₁ = t²` gives `t²(C₁ + C₂ ln t)`, every step checked.

## L4 · Faded worked examples

The narrator already produces every step of a solution, and every step can
be checked by substitution. A faded example shows the first steps and asks
for the next, one more blank each time -- the best-evidenced bridge from
reading a solution to producing one. Built from `steps.narrate` output; no
new maths.

## L5 · Diagnose a wrong number

`Fault` names the mistake behind a wrong *formula*. A `Numeric` answer that
is wrong says only "not within tolerance". The common wrong numbers are
computable: an Euler drill answered with a backward-Euler step, a step size
off by one, degrees for radians, a period for a frequency. Compute each
candidate from the template's slots and say which one matched.

## L6 · Glossary

Wronskian, Lipschitz, separatrix, Hartman–Grobman, resonance -- each used in
several lessons, defined in one. A searchable glossary built from the
lessons' own `Note`s, each entry linking to the lesson that defines it and
the lessons that use it. The test is that every term links somewhere real.

## L7 · "Linearise here"

A figure for Unit 8 lesson 1: click an equilibrium and zoom; the nonlinear
flow and the linearised one are drawn together and converge as the window
shrinks. Makes Hartman–Grobman something seen rather than stated, and shows
the centre where it fails.

## L8 · Exam readiness

The Leitner boxes (`progress.LEITNER`) and `progress.weakest` already hold
what a readiness report needs: per unit, how much is mastered, how much is
due, and which questions keep failing. One page, in words, with the "try
these again" queue the quiz report already builds.
