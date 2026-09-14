# Phase 2 — Findings, by lens

Every finding cites a file:line or a reproducible experiment. Facts are stated as
facts; judgments are labelled and justified. Where a lens from the brief does not
apply to a Python desktop application, it is marked `N/A` with the reason rather
than filled with invented content.

Findings are tagged `[A-1]`, `[B-2]` … and referenced by those tags in
`03-BACKLOG.md`.

---

## A. Numerical correctness and solver quality

**Checked:** every integrator's coefficients and their provenance; adaptivity,
error norm, controllers; dense output; stiffness handling; Jacobian strategies;
Newton convergence; event detection; structure preservation; failure handling;
vector/complex/higher-order support; time direction; precision.
**Verified by experiment:** 1, 1b, 2, 3, 4, 4b, 5, 6.
**Could not check:** behaviour on very large systems (n > 10⁴); no such problem
ships and none was constructed.

### Strengths, stated once and not repeated

The coefficient layer is better defended than the brief anticipates.
`tests/test_tableaux.py` evaluates the rooted-tree order conditions to order 5
plus row-sum consistency, per tableau, and asserts the propagated order is
*maximal*. Radau's `T`/`T⁻¹` come from `numpy.linalg.eig` at import time
(`steppers/irk.py:104-116`) and the Yoshida composition weights from a closed-form
recursion (`steppers/symplectic.py:98-119`) — neither is transcribed, so neither
can be mistyped. `radaudense` exists solely as an oracle for the split solve. All
of this is why Experiment 1 found **zero** coefficient defects.

### [A-1] `Jet.__array_priority__` makes `ndarray * Jet` recurse until the interpreter dies — P1

**Fact.** `steppers/taylor.py:53` sets `__array_priority__ = 1000.0` and
`taylor.py:97` aliases `__rmul__ = __mul__`. For an object-dtype ndarray times a
`Jet`, numpy defers to `Jet.__rmul__`, whose non-`Jet` branch does
`Jet(self.c * float(other))`; with `other` an object array this recurses without
bound. At Python's default recursion limit the C stack overflows and **CPython
exits with no traceback and no Python exception** (observed exit code 127).

**Reproduction.**
```python
from odesuite import ODEProblem, solve
import numpy as np
p = ODEProblem(lambda t, y: y*np.cos(t), (0.0, 5.0), [1.0])
solve(p, "taylor20")          # process dies, exit 127
```
Isolated: with `sys.setrecursionlimit(300)`, `ys * np.cos(t)` raises
`RecursionError`; `np.cos(t) * ys` raises `TypeError: float() argument must be …
not 'Jet'`. Both orderings fail; only one crashes.

**Not reachable from the GUI.** Taylor is gated behind `CatalogEntry.supports_taylor`
(`catalog.py:101`, default `False`), and user-typed equations set it `False`
explicitly (`equationmodel.py:197`). I ran `solve(p, "taylor20")` against **all 18
catalogue entries that enable it** — all 18 completed successfully, including the
driven `forced_spring`. The allowlist is correct.

**Judgment — P1 not P0:** the crash is unreachable through the application, but
`odesuite` ships as a standalone library whose README advertises the Taylor
family, and `y' = y·cos(t)` is about the most ordinary non-autonomous RHS there
is. A documented public method that kills the interpreter without an exception is
worse than one that raises.

### [A-2] RODAS4 degrades to first order on non-autonomous problems — P2

**Fact.** Experiment 1b. On `y' = y·cos t` RODAS4 holds order 4 down to `2.8e-11`,
then collapses to **order ≈0.98** and floors at `3.9e-13`. On the autonomous
`y' = -2y` it holds order 4 to `1.9e-14`.

**Cause, established by elimination.** Supplying an analytic Jacobian changes
nothing (identical to four significant figures), so it is not `∂f/∂y`. It is
`Rosenbrock._time_derivative` (`steppers/rosenbrock.py`), which differences
`∂f/∂t` with `dt = sqrt(EPS)·max(|t|,1)`; its `O(√ε)` error enters as `h·d_i·f_t`,
an `O(h·√ε)` — first-order — contribution. On an autonomous problem `∂f/∂t ≡ 0`,
the difference is exact, and the floor vanishes.

**`ODEProblem` has no `∂f/∂t` slot** (`problem.py:47-72` accepts `jac`,
`jac_sparsity`, `mass`), so no caller can work around it.

### [A-3] Radau under-delivers by up to 100× at tight tolerances, silently — P2, honesty

**Fact.** Experiment 2. On `y' = -2y`, achieved-÷-requested error: 0.01 at
`rtol=1e-9`, then **15.1× / 29.6× / 54.5× / 103.1×** at `1e-10 … 1e-13`. DOPRI5
holds 1.55–2.04× over the same range. `Solution.success` is `True` throughout and
nothing reports the shortfall.

**Cause, established directly.** `NewtonSettings(max_iter=8, tol_factor=0.03,
max_rate=1.0)` in `RadauIIA.__init__` (`steppers/irk.py`) terminates the stage
solve at 3% of the integration tolerance. Varying only that constant at
`rtol=1e-12`: `0.03 → 54.5×`, `0.003 → 0.8×`, `1e-4 → 0.2×`, `1e-6 → 0.0×`.

**Judgment — this is an honesty defect as much as an accuracy one.** The work is
being spent (steps rise 1.78×/decade, above the 1.58× a 5th-order method needs);
the accuracy simply is not delivered, and the solver does not say so. The
Accuracy Lab screen offers tolerances down to `1e-13` (`screens/accuracy.py:81`
uses `rtol=1e-13` for its own reference solution).

### [A-4] A fixed-step method that overflows spins for `max_steps` and reports the wrong reason — P2

**Fact.** Experiment 4b. Euler on the harmonic oscillator overflows after 90,607
accepted steps, then records **909,393 consecutive rejections** over **13.7 s**
before failing with `exceeded max_steps=1000000`.

**Cause.** `driver.py`'s non-finite branch sets `planner.h_abs = h_abs * 0.5`,
but `StepPlanner.plan`'s fixed-step branch (`_loop.py`) ignores `h_abs` — it
derives the step from `_reference` and `naccepted` — and `driver.py` then
overwrites `planner.h_abs` with `plan()`'s return. The halving is a no-op, so the
same failing step is retried forever. The driver already knows the real cause: it
sets `nonfinite_at`, and `underflow_message` (`_loop.py`) is written to report it.

**Judgment.** A fixed-step method *cannot* shrink its step; a non-finite state is
immediately fatal for it and should be reported as such on the first occurrence.

### [A-5] Non-uniqueness is returned as unqualified success — P2, honesty

**Fact.** Experiment 6. `y' = y^{1/3}, y(0)=0` returns `y ≡ 0`,
`status="finished"`, `success=True`, 8 steps, no warning. The problem has two
solutions through the origin.

**Why this one matters more than the general case.** No solver can detect
non-uniqueness in general, and a library returning one valid branch is defensible.
But **this application teaches this exact counterexample**: `lessons/unit1_first_order.py`,
lesson `slopefields`, carries a `pitfall` note — *"y' = y^{1/3} with y(0) = 0 has
both y ≡ 0 and y = (2t/3)^{3/2} through the origin. ∂f/∂y blows up there, which is
exactly the hypothesis that fails."* The course teaches it and the tool then
contradicts it in silence.

### [A-6] `problem.py`'s singularity guard covers only half of what its comment claims — P3

**Fact.** `problem.py:95-110` carries an extended comment stating the guard exists
so an equation started at its own singularity does not surface as *"a bare
ZeroDivisionError from inside a step-size heuristic, naming nothing the caller had
written."* The check is `np.all(np.isfinite(f0))`, which catches a numpy-produced
`inf`/`nan` — but not a Python exception raised inside the user's callable before
it returns. `ODEProblem(lambda t, y: np.array([1.0/t]), (0.0, 1.0), [0.0])` raises
exactly the bare `ZeroDivisionError` the comment set out to prevent (Experiment 6).

### [A-7] Discontinuous right-hand sides are integrated across without comment — P3, honesty

**Fact.** `y' = sign(t-1)` over `[0,2]` returns `status="finished"`,
`success=True`, `y(2) = -9.38e-6` against an exact 0, having taken 22 rejected
steps to cross the jump (Experiment 6). Standard behaviour for an adaptive solver,
but the rejection cluster is a detectable signature and `Solution.rejected`
already records exactly the data needed to spot it (`solution.py:66-77`).

### What is right, and worth not breaking

- Mixed tolerance is correct: `atol + rtol·max(|y_old|,|y_new|)`, per component,
  RMS-normalised (`controllers.py:29-40`).
- Automatic initial step is the Hairer/Nørsett/Wanner two-stage estimate
  (`controllers.py:44-80`), not a fixed guess.
- Dense output is real: five interpolant kinds, DOPRI5's free 4th-order
  extension, Radau's own collocation polynomial (`dense.py`). Plotting does
  **not** linearly interpolate raw steps.
- Event location is on the interpolant with `brentq(xtol=1e-14)` — Experiment 8
  measured **machine-precision** event times at every tolerance.
- Rejected steps are returned to the caller (`solution.py:66-77`) — unusual and
  genuinely useful.
- Backward integration, complex states, systems of arbitrary dimension, mass
  matrices including singular (index-1 DAE) all supported and tested.
- Stiff performance is strong (Experiment 3): Van der Pol μ=1000 in 1142 steps,
  Robertson to `t=1e11` in 239.
- Structure preservation verified (Experiment 4): bounded energy oscillation for
  Verlet/Yoshida against monotone growth for RK4.

---

## B. Symbolic / analytical layer

**Checked:** which techniques are implemented; the classifier; arbitrary
constants; implicit solutions; verification; parsing; LaTeX fidelity.
**Verified by experiment:** 11 (parsing), plus reading `steps.py`, `symbolic.py`,
`systems.py`, `laplace.py`, `series.py`.

### [B-1] Reduction of order is absent from the entire repository — P2

**Fact.** `git grep -i "reduction of order"` returns **zero hits**. It is the only
standard second-order technique in a first course with no coverage anywhere —
not in `steps.py`'s `TECHNIQUES` (`steps.py:82-91`), not in the lessons, not in
the docs. Its natural home is unit 3, alongside `variation` and `cauchy`.

### [B-2] The verification step exists and is a genuine strength — no action

**Fact.** `symbolic._verify` (`symbolic.py:842`) and `_verify_system`
(`symbolic.py:868`) substitute the computed solution back into the equation.
`check_answer` (`symbolic.py:923`) grades the learner's answer by substitution
rather than string comparison, and returns a third verdict — *"cannot tell"* —
where simplification cannot decide, rather than a false "wrong". The brief lists
back-substitution as "a high-value, low-cost improvement"; it is already here.

### [B-3] `dsolve` runs in a killable subprocess — no action

**Fact.** `symbolic.DSOLVE_TIMEOUT = 12.0` (`symbolic.py:62`) and
`dsolve_worker.py` run sympy's `dsolve` out of process with JSON transport,
explicitly not pickle (`dsolve_worker.py:9`). This is the right design: `dsolve`
can hang unboundedly on `y' = sin(y)`, and a UI cannot be held hostage to it.

### [B-4] The technique classifier depends on sympy's `classify_ode` *naming* — P2

**Fact.** `steps.py:82-91` lists eight sympy hint strings
(`"1st_homogeneous_coeff_best"`, `"nth_linear_constant_coeff_undetermined_coefficients"`,
…) and `_BUILDERS` (`steps.py:1589`) dispatches on them. These are sympy internal
identifiers with no stability guarantee. Combined with `sympy>=1.12` and no upper
bound or lockfile (`pyproject.toml:44`), a sympy minor release that renames or
reorders a hint changes **which technique the app narrates to a student**, with
no test failure necessarily catching a mere reordering.

Partially mitigated already: `_DETECTORS` (`steps.py:1605`) exists precisely
because "`classify_ode` cannot be relied on to name" exact equations.

### [B-5] Interval of validity is not reported with a symbolic solution — P2, honesty

**Fact.** `SymbolicSolution` (`symbolic.py:128`) carries `general`, `particular`
and derivation data; there is no interval-of-existence field, and no screen
displays one. A learner solving `y' = y²`, `y(0)=1` is shown `y = 1/(1-t)` with
nothing to say it is valid only on `t < 1` — while the *numerical* side of the
same app fails honestly at exactly `t=1` (Experiment 6). The `slopefields` lesson
teaches that the existence theorem is local; the solver does not act on it.

---

## C. Nonlinear-specific tooling

**Checked:** slope/vector/stream fields, nullclines, equilibria, linearisation,
classification, separatrices, phase line, bifurcation, limit cycles, Poincaré,
Lyapunov, the canonical model set, discrete-vs-continuous conflation.
**Verified by experiment:** 7, 9.

### [C-1] The dynamical-systems layer above linearisation does not exist — P1

**Fact.** `analysis.py` (782 LOC) implements slope fields (`:101`), vector fields
(`:85`), streamlines (`:151`), nullclines (`:540`), multi-seed equilibrium finding
(`:265`), the Jacobian at a fixed point (`:216`), eigenvalue classification
(`:226`), separatrices (`:649`), the 1-D phase line (`:369`) and click-to-seed
trajectories (`:556`). It implements **none** of: bifurcation diagrams or
parameter continuation, limit-cycle detection, Poincaré maps or sections,
Lyapunov-exponent estimation. `git grep -inE "lyapunov|limit cycle|bifurcation|hopf|hartman|bendixson"`
over `src/` matches only *prose in catalogue blurbs and problem docstrings*
(`catalog.py:172-173,213,596`; `problems/__init__.py:242,302,1179`).

**Judgment — P1.** For an application whose stated differentiator is nonlinear
ODEs, this is the largest capability gap. It is also the most tractable, because
the primitives it needs (equilibrium finding, classification, event detection with
machine-precision timing, dense output) are all already present and correct.

### [C-2] A non-hyperbolic equilibrium is labelled with a definite classification — P2, honesty

**Fact.** Experiment 7. For `x' = -y + x(x²+y²)`, `y' = x + y(x²+y²)` the app
reports `(0,0)` as **"centre"**, stability *neutral*. The linearisation does give
a centre; the true flow spirals **outward**. `screens/portrait.py:421` renders
`point.kind` verbatim in bold with no caveat.

`analysis.classify`'s own docstring (`analysis.py:226-234`) is scrupulous about
this — *"'Non-hyperbolic' covers the cases where the linearisation decides nothing
and the true behaviour depends on higher-order terms — worth naming honestly
rather than guessing at"* — and it returns `NEUTRAL`. The honesty is present in
the code and lost at the UI boundary. Lotka–Volterra's centre is reported
correctly, but only because that system is conservative; the classifier cannot
distinguish the two cases and the screen does not admit it.

### [C-3] Event detection misses most crossings at its default setting — P2

**Fact.** Experiment 8. With `g = sin(20t)` over `[0,10]` (63 true roots), the
default `subdivisions=0` finds **7**; `subdivisions=8` finds **63**.
`events.py`'s `Event` docstring is candid about the mechanism and quotes a
measurement of its own. Nothing in the returned `Solution` indicates that
crossings may have been missed, and the app never sets `subdivisions`
(`git grep subdivisions -- src/odesuite_app/` → no hits).

### [C-4] Chaos is warned about on the gallery card, not at the plot — P3, honesty

**Fact.** Experiment 9. Lorenz's predictability horizon for a `1e-10` perturbation
is `t ≈ 27.5`; separation reaches `6.5` by `t=40`. The blurb *"two trajectories a
hair apart diverge exponentially"* lives in `catalog.py:226-227`, shown on the
home gallery card, and `widgets/cards.py:87` colours the `chaotic` tag as a
warning. Nothing appears on the plot itself. The default `t_end=20` sits just
inside the horizon, so the default view is honest — and the `t_end` slider silently
takes the user past it.

### [C-5] Canonical model coverage is nearly complete — P3

**Fact.** Present and correct: logistic, Lotka–Volterra, Van der Pol, Duffing,
Brusselator, damped/driven pendulum, Robertson (ODE *and* DAE), Lorenz, HIRES,
Oregonator, Kepler, Pleiades, bouncing ball, plus 8 textbook models.
**Absent from the catalogue:** FitzHugh–Nagumo. **SIR** exists only as a
`custom.py` preset, not a catalogue entry — the selftest exercises it
(`PASS custom: SIR epidemic`) but it does not appear in the gallery, so a learner
cannot find it.

### [C-6] No discrete/continuous conflation — verified clean

**Checked specifically** because the brief calls it out. The logistic *map* does
not appear anywhere; `logistic` (`problems/__init__.py:168`) is the ODE
`y' = r y (1 - y/K)` and is described as such. No finding.

---

## D. Pedagogy and learning design

**Checked:** prerequisite structure, the rule of four, scaffolding and fading,
diagnostic feedback, the brief's specific misconception list, retrieval practice
and progress, cognitive load, teaching failure modes, notation, assessment
validity. Extracted programmatically across all 35 lessons.

### Structure, measured

7 units · 35 lessons · 177 notes (49 idea, 65 formula, **34 pitfall**, 29 aside) ·
237 derivation passages · 68 worked examples · 172 questions (105 `Choice`,
67 `Solve`) · 42 drill templates. Every lesson has `objectives`, `motivation`,
`derivation` and `reference`; **32/35** declare `prerequisites`; **35/35** carry
at least one drill template.

### [D-1] The brief's misconception list is almost entirely covered — no action

Scanned across every lesson's prose, notes, derivation and question options:

| misconception the brief names | targeted? | where |
|---|---|---|
| solution curve vs slope field | yes | slopefields, numerical, phase-portraits |
| not every ODE has a closed form | yes | basics, slopefields, equilibria, motion, numerical, … |
| `C` is cosmetic | yes | basics, superposition, variation, higher, laplace, … |
| uniqueness always holds | yes | slopefields, population, equilibria, superposition, … |
| "equilibrium" = "the system stops" | yes | slopefields, separable, linear, population, equilibria, … |
| linear-in-`y` vs linear-in-`t` | yes | linear, superposition, repeated-eigenvalues |
| smaller `h` is always better | yes | numerical, rungekutta |
| a numerical solution is exact | yes | slopefields, exact, substitutions, equilibria, numerical, … |

The design intent is explicit: `pitfall` is a first-class note kind
(`lessons/model.py:60`), used 34 times, and `Choice` questions carry **one reason
per option** — `lessons/model.py:14-20` states why: *"the reason a wrong option
was tempting is usually the thing the student actually got wrong."* This is
distractor-based diagnostic feedback done properly, and it is rare.

### [D-2] The nonlinear-systems unit (Edwards ch. 6) is not taught — P1

**Fact.** `git grep -i "chaos\|chaotic"` over `src/odesuite_app/lessons/` returns
**nothing**. Neither do `lyapunov`, `limit cycle`, `bifurcation`, `hartman`,
`bendixson`, `separatri`. Unit 6 (`systems`) is *linear* systems, Edwards ch. 4–5;
unit 7 is series. There is no unit between them.

**The asymmetry is the point.** The app *implements* linearisation and
classification (`analysis.py`), *names* Hopf and pitchfork bifurcations in slider
hints (`catalog.py:172-173,213`), *ships* Lorenz tagged `chaotic`, and *renders*
separatrices — while never teaching any of it. A learner meets a Hopf bifurcation
as a tooltip before being taught what a bifurcation is.

### [D-3] 17 of 35 lessons have no figure — P2

**Fact.** `lesson.figure` is unset for: basics, substitutions, population,
superposition, roots, variation, higher, circuits, transform, laplace, impulses,
systems-intro, eigenvalues, repeated-eigenvalues, forced-systems, recurrence,
frobenius. The figure infrastructure exists and is good (`widgets/lessonfigure/`,
7 modules, 12 interactive figures). The rule of four is therefore complete for
18 lessons and missing its graphical leg for 17 — including `eigenvalues` and
`systems-intro`, where a phase portrait is close to indispensable.

### [D-4] "Lipschitz" and "Picard–Lindelöf" are never named — P3

**Fact.** Both return zero hits repo-wide. The *content* is taught, correctly and
well: `slopefields` states the ∂f/∂y-continuity form, notes that the theorem is
local and only sufficient, and gives both classic counterexamples. Only the
standard names are missing — which matters solely because a student who wants to
read further cannot search for what they were taught.

### [D-5] No spaced review or retrieval scheduling — P3

**Fact.** `progress.py` records per-question `state`, `right` and `tries`
(v2 format, `progress.py:28-34`) — everything a scheduler would need. Nothing
consumes it for review scheduling; the Course Map shows completion, not decay.
The drill templates (42 of them, "practice that does not run out") make unlimited
retrieval *possible* but never *prompted*.

### [D-6] Notation is consistent — verified clean

Checked across units for `y` vs `x` as the dependent variable, `'` vs `d/dt`, and
vector notation. Consistent throughout; unit 6 switches to `x, y` for planar
systems, which is standard and is introduced explicitly.

---

## E. UX and interaction design

### [E-1] ~~Cold start takes ~15 s to a usable window~~ — **RETRACTED, my measurement error**

**This finding was wrong, and the error was mine.** It reported 27.3 / 28.1 /
30.8 s of process time and 14.4–16.7 s to a usable window, with a breakdown of
sympy 7.0 s, scipy 4.5 s, pyqtgraph 4.3 s, matplotlib 3.6 s. Those measurements
were taken **while a parallel `pytest -n auto` run was saturating all 14 cores**.
They describe a contended machine, not the application.

**Re-measured on an idle machine:**

| | audit (contended) | idle | |
|---|---:|---:|---|
| sympy | 7.02 s | **0.40 s** | |
| `odesuite` (≈scipy) | 4.48 s | **0.35 s** | |
| pyqtgraph | 4.27 s | **0.29 s** | |
| matplotlib.pyplot | 3.62 s | **0.29 s** | |
| PySide6.QtWidgets | 0.95 s | **0.09 s** | |
| `MainWindow()` | 2.94 s | **0.40 s** | |
| **to a usable window** | 14.4–16.7 s | **1.44–1.46 s** | warm |
| **total process** | 27.3–30.8 s | **3.5 s** warm, 6.3 s cold | |

**The cause is confirmed, not assumed.** Re-running the identical measurement
under a deliberate 14-process CPU load reproduces the original numbers exactly —
sympy 7.19 s against 7.02 s reported. The finding measured the load.

**Corrected judgment: this is not a defect.** ~1.4 s to a window and ~3.5 s of
process time is ordinary for a desktop scientific application, and there is
nothing here worth the risk of restructuring the import graph. The eager imports
are real — sympy, matplotlib and pyqtgraph are all pulled in at module scope —
but they cost about a second between them, not twenty.

`PERF-01` and `UX-01` are demoted accordingly in `03-BACKLOG.md`, and the M2
milestone in `04-ROADMAP.md` no longer leads with them. The lesson for the rest
of this audit: every wall-clock number in it should be read as an upper bound
unless it says the machine was idle. The step counts, error magnitudes and
convergence orders are unaffected — they do not depend on load.

### [E-2] Worst-case replot stall of 104 ms during a slider drag — P3

**Fact.** Experiment 10. Median GUI-thread gap 5–6 ms (i.e. free), but max gap
81.9 ms (brusselator), 83.0 ms (Kuramoto–Sivashinsky), **104.1 ms** (Pleiades).
Solves are correctly off-thread; the stall is on the result-delivery/redraw path.
Measured offscreen, so on-screen figures can only be worse.

### [E-3] No permalink, no session save, no undo — P2

**Fact.** `QSettings` stores only window geometry (`app.py:294-311`).
`progress.py` stores only lesson answers and is explicit that it is "the only
thing the application stores on disk" (`progress.py:3`). There is no way to save
or restore "Van der Pol at μ=800, radau, rtol=1e-9, this window", and no undo
anywhere. Mitigating: `SolveRequest.as_code()` (`solver.py:55`) emits the
`odesuite` snippet that reproduces the current solve, which is a genuinely good
partial answer — reproducibility via copy-paste rather than via app state.

### [E-4] Forgiving input parsing is implemented — no action

**Fact.** `_insert_multiplication` (`symbolic.py:172`) handles `3y'` and `2(t+1)`;
`convert_xor` (`custom.py:60`) makes `^` mean exponentiation; `_rewrite_derivatives`
(`symbolic.py:184`) accepts `y'`, `y''`, `y^(3)` and the Unicode prime `′`. The
restraint is also right: it deliberately does **not** insert a `*` between two
identifiers, so `sin t` stays an error rather than silently becoming `sin*t`
(`symbolic.py:174-177`).

### [E-5] First-run experience is a gallery, and it is the right choice — no action

`screens/home.py` renders a thumbnail gallery of the catalogue with blurbs and
tags, built asynchronously on the thread pool (`home.py:30`, `_ThumbJob`). A new
user sees named, pictured problems within one screen. No finding, recorded because
the brief asks.

---

## F. Accessibility

### [F-1] Screen-reader support is confined to the maths widget — P2

**Fact.** Across 68 app modules: **7** `setAccessibleName` and **3**
`setAccessibleDescription` calls in total, and 6 of those 10 are in
`widgets/mathlabel.py:181-184`. Maths is rendered to a **bitmap** (matplotlib
mathtext → `QImage`), which would be entirely opaque to a screen reader — and
`mathlabel.py:174-184` correctly sets the plain-text form as both tooltip and
accessible description. That one widget is handled well.

Everything else — the 13 screens, the plot panels, the control widgets, the
lesson cards — carries no accessible naming. 45 `setToolTip` calls provide hover
help, which is not the same thing.

### [F-2] Plots have no text alternative — P2

**Fact.** No accessible data table, no textual summary of a trajectory, no
`setAccessibleDescription` on any pyqtgraph widget. For an app whose product is
graphical, a non-visual learner gets nothing from the Solver Studio.

### [F-3] Separatrices are distinguished by red/green alone — P3

**Fact.** `screens/portrait.py:364` draws `palette.danger if label == "unstable"
else palette.success`. Equilibrium *markers* correctly encode type as **shape** as
well as colour — `portrait.py:39` records the reason: *"as colour, so it survives
greyscale and colour-vision deficiency"*, implemented in `_MARKERS`
(`portrait.py:46-47`). The lines did not get the same treatment; no dash pattern
distinguishes them.

### [F-4] Contrast passes AA throughout — no action

**Fact.** Experiment 12. Dark theme: `text` 16.02, `text_muted` 6.15, `accent`
6.45, `success` 7.45, `warning` 7.50, `danger` 5.65. Light: 15.80 / 5.33 / 5.19 /
5.08 / 4.87 / 5.36. All eight series colours clear 3.0 against the background in
both themes. Two full palettes with a runtime toggle (`theme.py:95`).

### [F-5] No `prefers-reduced-motion` equivalent — P3, low impact

**Fact.** No `QPropertyAnimation` or timed animation found in the app, so there is
little motion to reduce. Recorded for completeness: if the phase-portrait tracing
or lesson figures gain animation, a setting must come with it.

### [F-6] Text scaling untested — `UNVERIFIED`

Qt inherits the OS font scale, but nothing pins layout behaviour at 200%, and
maths is a rendered bitmap sized from `devicePixelRatio` (`mathlabel.py:138-139`)
rather than from the font scale — so equations plausibly do **not** scale with
system text size. I could not verify this under the offscreen platform; it needs
a real display.

---

## G. Architecture and code quality

### [G-1] The library/UI boundary is real and enforced — no action

`odesuite` imports no Qt (verified: zero `PySide*`/`shiboken*`/`pyqtgraph`/
`matplotlib` in `sys.modules` after import), imports nothing from `odesuite_app`,
and CI enforces both — a dedicated `library-only` job plus a clean-venv wheel test
(`.github/workflows/ci.yml`). The solver core is testable headlessly and
`tests/test_convergence.py` does exactly that.

### [G-2] `state.py` documents a layering rule that four screens break — P3

**Fact.** `state.py:5` states *"Screens never talk to `odesuite` directly."* Four
do: `screens/accuracy.py:35`, `screens/stiffness.py:35,74,369`,
`screens/portrait.py:270`, `screens/learn_problems.py:181`.

**Judgment.** Not a tangle — those four do method-comparison and stability work
the view-model does not model, and routing it through `SessionState` would bloat
it. The defect is the docstring, which should describe the boundary that exists.

### [G-3] Type and lint hygiene are exemplary — no action

`ruff check .` clean; `mypy` clean on 24 modules; `py.typed` shipped;
**zero** TODO/FIXME/HACK/XXX across `src/` and `tests/`; no commented-out code;
no duplicated solver implementations (`byhand.py:9-12` delegates to the library
stepper and `tests/test_byhand.py` asserts bit-for-bit agreement). The ruff rule
selection is itself justified in a comment (`pyproject.toml:96-127`).

### [G-4] Two "duplications" are deliberate and correctly justified — no action

`radaudense` is an oracle for the split Radau solve; `robertson`/`robertson_dae`
are two formulations of one system. Both documented in place. Recorded because the
brief asks specifically about duplicate solver implementations.

### [G-5] ROS3P was removed rather than shipped — worth preserving as precedent

`steppers/rosenbrock.py:151-163` records that ROS3P's embedded pair produced an
identically-vanishing error estimate and that shipping it would be "silently wrong
rather than slow". That is the correct call, documented where the next person will
find it. Noted as the standard the rest of the backlog should be held to.

---

## H. Performance

### [H-1] ~~Startup~~ — **RETRACTED**, see [E-1]

Reported as "the single largest performance defect, ~21 s of eager imports". The
imports cost about **1.8 s** on an idle machine; the original figure was measured
under a saturating parallel test run. Not a defect.

### [H-2] Explicit-on-stiff takes ~17 s to fail — P2

*(Re-verified on an idle machine after [E-1] was retracted: Robertson 17.6 s,
Van der Pol μ=1000 16.5 s, against the 22.6 s and 19.4 s originally reported.
Contention inflated these too, but only by ~25% — the finding stands, and the
`test_race_shows_an_explicit_method_failing_on_robertson` test still costs 15 s.)*

**Fact.** Experiment 3: dopri5 on Van der Pol μ=1000 fails after 19.4 s / 499,987
steps; on Robertson after 22.6 s / 499,996 steps.
`tests/test_app_stiffness.py::test_race_shows_an_explicit_method_failing_on_robertson`
was the 6th-slowest test in the suite at **34 s**, so the app stages this
demonstration deliberately — which is pedagogically right. The problem is that the
learner watches a spinner for 20 s to be told what a stiffness-detection heuristic
could say in 200 ms.

### [H-3] No allocation reuse in the ERK inner loop — P3

**Fact.** `steppers/erk.py:56` allocates `K = np.empty((s, y.size))` on **every
step**. For DOPRI5 that is a 7×n array per step; at 500,000 steps that is 500,000
allocations. `RadauIIA` already does the opposite and says why — it hoists one
`F` buffer per step with a comment explaining that it never escapes
(`steppers/irk.py`). The same treatment applies to `erk.py`.

### [H-4] Test suite takes 6m48s; coverage run 13m — P3

Parallel with `-n auto`. The five slowest tests are 30–62 s each and are all
symbolic (`test_exponential` 62 s, two `test_templates` at 52/43 s,
`test_symbolic` 43 s, `test_lessons` 38 s). Acceptable for CI, slow for local
iteration; no per-test budget or `-m slow` split is applied to them (the `slow`
marker is declared in `pyproject.toml:84` but these tests do not carry it).

---

## I. Testing and verification infrastructure

### Coverage, measured

| area | statements | covered | % |
|---|---:|---:|---:|
| `src/odesuite` (library) | 2,542 | 2,448 | **96.3%** |
| `src/odesuite_app` | 10,145 | 9,121 | **89.9%** |
| **total** | **12,687** | **11,569** | **91.2%** |

3,125 tests, 0 failures, 19 skips — all 19 capability guards ("Euler has no
embedded pair"), none disabled.

### [I-1] Coverage is never measured by the project — P2

`pytest-cov` is not in `[dev]` (`pyproject.toml:46-58`), not in CI, and there is
no coverage config. The figures above exist only because this audit installed the
tool. A 96.3% library figure is worth defending with a gate.

### [I-2] Convergence-order and order-condition tests already exist — no action

`tests/test_convergence.py` fits log(error) against log(h) across parametrised
methods and problems, driving steppers directly in a fixed-step loop.
`tests/test_tableaux.py` evaluates rooted-tree order conditions to order 5, plus
row-sum consistency, and asserts the propagated order is **maximal**. The brief
predicts both are usually absent; both are here, and `tableaux.py:14-21` says they
exist precisely to catch transcription errors. Experiment 1 confirms they work.

### [I-7] The quiz seeds its paper from the wall clock, making a test non-deterministic — P2

*(Found after the audit, while running the suite during M1/M2 work. The brief's
§I asks for "deterministic seeding wherever randomness appears" and Phase 2
recorded nothing — this is the gap.)*

**Fact.** `screens/learn_quiz.py` built its paper with
`seed=int(time.time()) % 100_000`, so which questions appear depends on *when*
the quiz is started. `tests/test_quiz.py::test_a_second_press_of_check_cannot_turn_a_miss_into_a_hit`
typed `"0"` and asserted it was marked wrong, on the strength of a comment
reading *"almost certainly wrong"*. Since the numeric drills arrived, some
questions have 0 as their answer, and the test failed on exactly the runs that
drew one — reproducibly under `pytest -n auto`, passing in isolation, which is
the signature that makes this kind of flake expensive to chase.

**Judgment.** The clock is the right seed for a *quiz* — sitting it twice should
not give the same paper — and the wrong one for a test. The fix is a seam
(`QuizScreen.seed_override`) rather than a change of behaviour, plus a test that
*finds* a question it can miss instead of assuming one.

**Fixed** during this work; `learn_quiz.py` and `tests/test_quiz.py` both changed.

### [I-3] No property-based tests — P3

**Fact.** No `hypothesis` dependency; no test asserting time-reversibility of the
symplectic methods, superposition for linear ODEs, or time-translation invariance
for autonomous problems. These are cheap to add and would have caught [A-2]
(RODAS4's autonomous-vs-non-autonomous split) directly.

### [I-4] Regression tests for the defects in this audit do not exist — P2

By construction: [A-1] through [A-5] all pass the current suite. Each needs a test
that fails today.

### [I-5] No performance regression gate — P3

`benchmarks/` (5 scripts, `run_all.py`) produce work-precision and energy-drift
figures, but nothing runs them in CI and nothing asserts a bound. A change that
doubled Radau's step count on Robertson would not be noticed.

### [I-6] Least-covered modules are the operational ones — P3

`cli.py` 50.0% (60 statements missed), `dsolve_worker.py` 57.7% (44),
`thumbnails.py` 74.0% (20), `solver.py` 80.3% (27). `dsolve_worker` is the
subprocess boundary and `solver.py` the threading/cancellation layer — the two
places where a bug is hardest to reproduce and most likely to hang the UI.

---

## J. Security and privacy

### [J-1] Arbitrary code execution from a typed equation — **P0**

**Fact.** Experiment 11. `sin` is on the function whitelist
(`custom.py:41-56`), and
`sin.__class__.__init__.__globals__["__builtins__"]` yields the real builtins
(157 names, `__import__` present). Executing a canary write **created the file**.

**Reachable from two shipping UI paths**, both confirmed by canary:
- `odesuite_app.custom.build` — Solver Lab, "type your own system".
- `odesuite_app.symbolic.parse_equation` — the equation editor. The payload
  executed and `write()`'s return value silently became the equation's right-hand
  side (`Eq(Derivative(y(t), t), 6)`).

**What the existing defence does and does not cover.** `custom.py:9-16` shows the
author identified the danger precisely and closed the **name-lookup** hole —
`_SAFE_GLOBALS` sets `__builtins__` to an empty mapping rather than omitting it,
for exactly the right reason. All name-based payloads (`__import__`, `eval`,
`exec`, `open`, `globals`, `compile`, …) are correctly rejected with `NameError`.
The hole is **attribute traversal from a whitelisted object**, which no name
whitelist can close. The `dsolve` subprocess does not help: parsing is in-process.

**Threat model, stated fairly.** A local desktop app, no network input, equations
normally typed by the person running it. It is P0 because (i) equations get
shared — pasted from a classmate, a forum, a handout — so "try this equation" is a
payload; and (ii) `odesuite` is packaged for PyPI, making `custom.build`
importable by code that may feed it untrusted input. The brief's rule for this
class is explicit and it is the right rule.

**Fix, prototyped and measured** (Experiment 11): validate the AST before sympy
compiles it — reject `Attribute` and `Subscript`, allow only whitelisted `Name`s
and direct calls to them. **9/9 escapes blocked, 14/14 legitimate equations
accepted.**

### [J-2] No dependency vulnerability scanning or pinning — P2

**Fact.** `pyproject.toml:44` declares floors only (`numpy>=1.24`, `scipy>=1.10`,
`PySide6>=6.6`, `sympy>=1.12`); no lockfile, no `requirements.txt`, no
`pip-audit`/Dependabot, no upper bounds. The build is not reproducible and no
process would notice a CVE in PySide6.

### [J-3] Privacy posture is good and should be documented — P3

**Fact.** No network calls anywhere in `src/` (no `requests`, `urllib`, `socket`,
`http`). No telemetry, no analytics, no crash reporting (`git grep -i
"sentry|telemetry|analytics"` → nothing). The only disk write is
`progress.json` — lesson answers only, in the per-user config directory, written
atomically, tolerant of corruption, with an in-app delete button
(`progress.py:1-40`). This is a genuinely good privacy position that no
user-facing document currently states.

---

## K. Content, docs, and licensing

### [K-1] Provenance — **cleared**

The author confirms all content is original; the Edwards–Penney–Calvis references
carried by every `Unit` and `Lesson` are chapter pointers for the reader, not
transcriptions. This was Phase 1's only open release blocker and it is closed.
Recommended follow-up is documentary, not legal: state it in the README so the
question is not re-raised by a contributor or reviewer.

### [K-2] Mathematical writing is precise, including its hypotheses — no action

Spot-checked against the brief's list. Names are spelled correctly throughout
(Poincaré, Lyapunov, Runge–Kutta, Bendixson appear correctly in library
docstrings; Lipschitz and Picard do not appear at all, see [D-4]). Theorem
statements carry their hypotheses — the `slopefields` existence/uniqueness note
distinguishes the continuity condition from the ∂f/∂y condition and states which
half buys what, then adds a `pitfall` that the theorem is *local and only
sufficient*.

### [K-3] Missing collaboration and citation files — P3

Absent: `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `ARCHITECTURE.md`,
`CITATION.cff`, `.pre-commit-config.yaml`. `README.md` (1,016 lines) and
`CHANGELOG.md` (1,028 lines, 5 releases, Keep-a-Changelog format) are thorough, so
this is a gap in *kind*, not in volume. `SECURITY.md` matters most given [J-1].

### [K-4] Docs build in CI but are never published — P3

`mkdocs build --strict` runs in CI; `mkdocs.yml:11-12` records the deliberate
choice: *"No site_url / repo_url: this is built and served locally."* Consistent,
but it means the API reference and the numerical-methods documentation reach
nobody who has not cloned the repo.

### [K-5] No document explains the methods' limits to a user — P2

There is excellent per-module documentation of *how* each method works. There is
no single page saying *when each fails* — which is the question this audit's
experiments answer (explicit methods on stiff problems, RODAS4 on non-autonomous
problems, Radau below `rtol=1e-9`, the default event-detection setting, Taylor's
jet-arithmetic requirement). For a teaching product this is the highest-value
document not yet written.

---

## L. Release engineering and operations

### [L-1] Build reproducibility — P2

No lockfile and no pinned toolchain (see [J-2]). `python -m build` +
`twine check` + a clean-venv install test all run in CI, which is more than most
projects do — but "reproducible" requires pinned inputs, and there are none.

### [L-2] Advertised platform support exceeds tested support — P2

`pyproject.toml` classifiers advertise Python 3.10–3.13 and "OS Independent".
CI (`ci.yml`) tests **3.10 and 3.12 on ubuntu-latest and windows-latest**.
Python 3.11 and 3.13, and macOS entirely, are untested claims.

### [L-3] No error monitoring or feedback channel — P2

No crash reporting, no log file, no "report a problem" affordance. Combined with
[J-3]'s no-telemetry stance this is coherent — but there is then *no* route by
which the author learns that a solver failed for a user. For a desktop app the
proportionate answer is a local log plus a one-click "copy diagnostics", not
remote telemetry.

### [L-4] No staging, feature flags, or rollback plan — P3

Single-branch (`main`), no tags visible in the 35-commit history, no release
workflow (CI builds artefacts but does not publish). Rollback today means
"install the previous version from PyPI", which is adequate for a library and
undefined for the PyInstaller executable.

### [L-5] Packaging exists and is tested — no action

`packaging/odesuite.spec` + `launch.py` build a PyInstaller executable; the
`--selftest` flag exists specifically so a windowed build with no console can be
verified (`cli.py:60-67`), CI runs it and uploads the report. That is a
thoughtful arrangement.

### [L-6] Stale `dist/` artefacts on disk — P3

`dist/` holds `odesuite-0.3.0` wheels while the source is 0.4.0. Untracked and
gitignored; cosmetic, but an easy thing to install by accident.

---

## Lenses that do not apply

| Brief lens | Status | Reason |
|---|---|---|
| §E mobile/touch, pinch-zoom, tap targets | **N/A** | Desktop Qt application; no mobile target |
| §F text reflow at 200% zoom (web sense) | **partial → [F-6]** | No web layout; the Qt equivalent is OS font scaling, `UNVERIFIED` |
| §H bundle size, code splitting, TTI | **translated → [E-1]** | No bundle; the equivalent is import time, measured |
| §H SVG-vs-canvas plot rendering | **N/A** | pyqtgraph draws to a native Qt surface |
| §J XSS, CSP headers, `dangerouslySetInnerHTML` | **N/A** | No HTML rendering surface, no browser |
| §J `npm audit` | **translated → [J-2]** | Python equivalent is `pip-audit`, absent |
| §J backend authn/authz, rate limiting, secrets | **N/A** | No backend, no network code, no secrets in the repo |
| §L SEO, meta tags, social cards, favicon | **N/A** | Not a web property |
| §L offline behaviour / PWA | **N/A** | Desktop app; offline is the only mode |
