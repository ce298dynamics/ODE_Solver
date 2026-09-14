# ODE Learning App — Audit & Release-Readiness Brief

You are auditing an educational application about **ordinary differential equations** that also ships **numerical and symbolic tools for solving nonlinear ODEs**. Your job has two halves: (1) understand the app deeply and honestly, and (2) produce a concrete, prioritized backlog of **at least 50 improvements** that would take it from its current state to release quality.

Treat this as a senior review from three people at once: a numerical analyst, a learning-design specialist, and a staff engineer preparing a launch.

---

## 0. Fill these in before starting

If any of these are unknown, infer them from the repo and **state your inference explicitly** in the audit rather than silently assuming.

| Field | Value |
|---|---|
| Repo path | `.` (current directory) |
| Target audience | (e.g. undergraduate sophomores in a first ODE course / self-learners / instructors) |
| Release target | (e.g. public web app, free, launch in 6 weeks) |
| Platforms that must work | (e.g. desktop Chrome/Firefox/Safari + mobile Safari) |
| Non-goals | (e.g. no PDEs, no account system in v1) |
| Team size / effort available | |

---

## 1. Ground rules

- **Do not modify application code during Phases 1–4.** This is an audit. The only files you create are the deliverables in §7, plus throwaway verification scripts in a `/tmp/ode-audit/` scratch directory.
- **Verify, don't guess.** Run the app. Run the test suite. Write small scripts to check numerical claims. If you cannot verify something, label it `UNVERIFIED` and say exactly what you'd need.
- **Cite evidence.** Every finding references `path/to/file.ts:123` or a reproducible command. Findings without evidence are worthless to me.
- **No fabricated file paths, function names, or line numbers.** If you didn't read it, don't cite it.
- **Distinguish fact from judgment.** "RK4 is implemented with a wrong `b` coefficient at `rk4.ts:41`" is a fact. "The onboarding is confusing" is a judgment — say why and on what basis.
- **Severity is about the user, not about your taste.** A silently wrong solver output is P0. A missing `README` badge is P3.
- Work in order. Do not skip to writing the backlog before you've done the verification experiments in §4 — the experiments are where the most valuable findings come from.

---

## 2. Phase 1 — Orientation and inventory

Produce an internal map before judging anything.

1. Identify the stack, build system, package manager, entry points, and how to run the app and its tests locally. Actually run all of it.
2. Produce a **module map**: what each directory/file is responsible for, and the dependency direction between the numerics core, the symbolic layer, state management, and the UI.
3. Produce a **feature inventory**: every lesson, topic, interactive widget, solver, plot type, and exercise the app currently contains. Mark each as `complete` / `partial` / `stub` / `broken`.
4. Produce a **math-content inventory**: which ODE topics are covered, in what order, and which standard first-course topics are missing entirely.
5. Report repo health signals: last-modified spread, TODO/FIXME/HACK counts with locations, dead code, commented-out blocks, duplicated logic, dependency count and staleness, lockfile presence, bundle size if measurable.
6. Note anything that looks abandoned, half-migrated, or contradictory (two implementations of the same solver, two state stores, etc.).

---

## 3. Phase 2 — Deep examination

Go lens by lens. For each lens, list what you checked, what you found, and what you could not check.

### A. Numerical correctness and solver quality

- Identify every integrator implemented. For each: name, order, explicit/implicit, fixed/adaptive, and where the coefficients live.
- **Check the Butcher tableaux / coefficients line by line against reference values.** Transcription errors here are the single highest-value bug class in an app like this.
- Adaptive stepping: is there error estimation (embedded pair vs step doubling)? What controller (elementary, PI, PID)? Safety factor, min/max step growth, rejection handling, minimum step floor, maximum step count. Is `atol`/`rtol` mixing done correctly (`atol + rtol*|y|`, per component, RMS-normalized)?
- Is there **dense output / continuous extension**, or does plotting linearly interpolate raw adaptive steps? (The latter produces visibly wrong curves near sharp features while claiming high accuracy.)
- Stiffness: is any implicit or stiffness-aware method available (BDF, Radau IIA, Rosenbrock, TR-BDF2)? If the app offers explicit methods only, does it *detect and warn* about stiffness, or does it just spin?
- Jacobians: analytic, automatic differentiation, or finite-difference? If FD, what step size rule? Is the Newton iteration inside implicit steps convergence-checked, with a fallback?
- Event detection / root finding (e.g. bouncing ball, threshold crossings, Poincaré sections): does it exist, is it bracketed and refined, or does it just check sign at step endpoints?
- Structure preservation: for Hamiltonian/conservative systems, are symplectic options offered (Störmer–Verlet, leapfrog, Yoshida)? Does the app show or ignore energy drift over long integrations?
- Failure handling: what happens on `NaN`, `Inf`, overflow, blow-up in finite time, division by zero in the RHS, and singularities on the integration path? Silent garbage, or an honest error?
- Vector/system support: does the solver handle systems of arbitrary dimension, complex-valued states, higher-order ODEs via reduction to first-order?
- Time direction: backward integration, `t_end < t_0`, and non-monotonic output grids.
- Precision: any accumulation errors, catastrophic cancellation, or `float32` where `float64` is needed?

### B. Symbolic / analytical layer

- Which analytical methods are implemented (separable, linear first-order via integrating factor, exact + integrating factors, Bernoulli, homogeneous, constant-coefficient linear, undetermined coefficients, variation of parameters, reduction of order, Laplace transforms, series/Frobenius, Euler–Cauchy)?
- Correctness of the classifier that decides which method applies, and behavior when nothing applies.
- Is the arbitrary constant handled correctly? Are implicit solutions presented as implicit rather than force-solved?
- Domain of validity: does the app state the interval of existence, or hand back a formula that is wrong past a singularity?
- Existence and uniqueness: is Picard–Lindelöf / Lipschitz continuity taught and *checked*? Are the classic counterexamples present — non-uniqueness for `y' = y^(1/3)`, finite-time blow-up for `y' = y²`?
- Verification: does the app substitute its own symbolic answer back into the ODE to confirm it? (If not, that's a high-value, low-cost improvement.)
- Expression parsing: what parses user input? **If it is `eval`, `new Function`, or equivalent, that is a P0 security finding** — write it up in §J too.
- Simplification quality, LaTeX rendering fidelity, and whether the displayed steps match the computation actually performed.

### C. Nonlinear-specific tooling

This is the app's differentiator; scrutinize it hardest.

- Slope/direction fields: grid density, arrow normalization (are arrows scaled by slope magnitude in a way that misleads?), behavior near vertical slopes and singularities, aspect-ratio distortion.
- Phase-plane tooling: trajectories, nullclines, separatrices, click-to-seed initial conditions, forward/backward integration.
- Equilibrium finding: what root-finder, what starting guesses, does it find *all* equilibria in the window or just some? Does it report failure honestly?
- Linearization and classification: Jacobian at fixed points, eigenvalue computation, classification into node/saddle/spiral/center/degenerate. **Does it correctly caveat the borderline cases** — purely imaginary eigenvalues where Hartman–Grobman does not apply, zero eigenvalues, non-hyperbolic points?
- Stability language: is asymptotic vs Lyapunov vs orbital stability used precisely, or loosely?
- Bifurcation tools: parameter sweeps, saddle-node/transcritical/pitchfork/Hopf, continuation vs naive re-solving, branch labeling for stable/unstable, hysteresis.
- Limit cycles: detection method, Poincaré map/section, Poincaré–Bendixson discussion for planar systems.
- Chaos: Lorenz/Rössler/driven pendulum, sensitivity demos, Lyapunov exponent estimation (method, convergence, is it honest about error?), and whether the app warns that a single trajectory is meaningless past the predictability horizon.
- Does the app anywhere conflate discrete maps with continuous flows (e.g. logistic map vs logistic ODE)? That's a common and serious pedagogical bug.
- Are the canonical model systems present and correct (logistic, Lotka–Volterra, SIR, Van der Pol, Duffing, FitzHugh–Nagumo, Brusselator, damped/driven pendulum, Robertson, Lorenz)?

### D. Pedagogy and learning design

- Prerequisite structure: is there an explicit concept map, or an implicit one that's out of order? Does anything use a concept before defining it?
- The "rule of four": are solutions presented symbolically, numerically, graphically, *and* verbally? Where is a representation missing?
- Worked examples and fading: does scaffolding decrease as the learner progresses, or is it constant?
- Practice: are there exercises with immediate, *diagnostic* feedback — distractors that map to specific known misconceptions rather than generic "incorrect"?
- Known misconceptions to check whether the app targets: confusing the solution curve with the slope field; believing every ODE has a closed form; treating `C` as cosmetic; assuming uniqueness always holds; reading "equilibrium" as "the system stops"; confusing linear-in-`y` with linear-in-`t`; assuming smaller step size always means more accurate (roundoff); believing a numerical solution is exact.
- Retrieval practice, spaced review, and any progress/mastery model.
- Cognitive load: information density per screen, simultaneous animated elements, progressive disclosure of controls.
- Does the app teach *when a method fails*, not just when it works? Nonlinear ODEs are mostly failure cases.
- Notation consistency across every lesson (`y` vs `x` for the dependent variable, `'` vs `d/dt`, vector notation).
- Assessment validity: do the exercises measure understanding or button-pushing?

### E. UX and interaction design

- First-run experience: what does a new user see, and do they know what to do within 10 seconds?
- Information architecture and navigation; can a learner find a specific topic?
- Input ergonomics for entering an ODE: error messages, autocomplete, syntax help, examples, forgiving parsing (`2x` vs `2*x`, `^` vs `**`).
- Parameter controls: sliders vs numeric entry, sensible ranges, real-time re-solve vs explicit "run".
- Plot interaction: pan, zoom, reset, hover readout, legend, axis labels with units, export.
- State management: is the learner's work saved? Is app state shareable by URL/permalink? Is there undo?
- Empty, loading, and error states for every view.
- Mobile and touch: do phase portraits work with pinch/drag? Are tap targets adequate?
- Latency: is any interaction perceptibly slow enough to break the sense of direct manipulation?

### F. Accessibility

- Keyboard operability of every control, including plots and canvas widgets; visible focus rings; logical tab order.
- Screen readers: are math expressions accessible (MathML / KaTeX + `aria-label` / MathJax speech), or images and raw LaTeX?
- Are plots given text alternatives — a summary of what the curve does, or an accessible data table?
- Color: contrast ratios, and whether meaning is ever carried by color alone (stable = green / unstable = red is a very common failure for red–green color blindness).
- `prefers-reduced-motion` for animations and phase-portrait tracing.
- Text scaling to 200%, zoom, and responsive reflow.
- Any timing-dependent interaction that can't be paused.

### G. Architecture and code quality

- Is there a clean boundary between the numerics core, the symbolic layer, and the UI? Could the solver core be extracted and tested headlessly?
- Type safety: coverage, `any`/`@ts-ignore` counts, runtime validation at boundaries.
- Error handling strategy: exceptions vs result types vs silent `NaN` propagation; error boundaries in the UI.
- State management coherence; prop drilling; unnecessary re-renders driving re-solves.
- Naming and mathematical fidelity of the code (does `h`, `y0`, `tspan`, `atol` mean what a numerical analyst expects?).
- Duplication across solvers that should share a common driver.
- Configuration and magic numbers — tolerances and step limits hardcoded in the middle of functions.
- Dependency hygiene: unused, duplicated, unmaintained, or oversized deps; licenses.

### H. Performance

- Where does the solve run? If it's on the main thread, it blocks the UI — quantify the freeze on a stiff or long-horizon problem.
- Allocation churn in inner loops; array reallocation per step; whether typed arrays are used.
- Plot rendering: SVG with thousands of points vs canvas/WebGL; downsampling strategy that preserves visual features.
- Debouncing of slider-driven re-solves.
- Bundle size, code splitting, lazy loading of heavy math/plot libraries, time-to-interactive.
- Memory growth over a long session (leaked listeners, retained trajectory history).

### I. Testing and verification infrastructure

- Current coverage, honestly measured, split by numerics core vs UI.
- **Are there convergence-order tests?** These are the definitive correctness tests for an integrator and are usually absent.
- Golden/reference tests against a trusted implementation (SciPy `solve_ivp`, published benchmark values).
- Property-based tests: time-reversibility for symplectic methods, linearity, superposition for linear ODEs, invariance under time translation for autonomous systems.
- Regression tests for every bug fixed.
- Deterministic seeding wherever randomness appears.
- Visual regression tests for plots.
- End-to-end tests of the core learner journeys.
- Performance benchmarks with regression gates in CI.
- Is CI actually running, and does it block merge?

### J. Security and privacy

- **User expression evaluation.** If arbitrary user input reaches `eval`/`new Function`/`vm`, treat as P0: sandboxing or a real parser+AST evaluator is required.
- XSS via rendered content, including LaTeX and any user-supplied strings; `dangerouslySetInnerHTML` usage.
- CSP headers, dependency vulnerabilities (`npm audit` / equivalent), supply-chain pinning.
- Any data collection: what, where does it go, is there consent, is it disclosed? What's stored in `localStorage`?
- If there's a backend: authn/authz, rate limiting, input validation, secrets in the repo or bundle.

### K. Content, docs, and licensing

- Mathematical writing quality: precision of definitions, correct hypotheses stated with theorems, spelling of names (Lipschitz, Poincaré, Lyapunov, Bendixson, Runge–Kutta).
- **Provenance of every problem, figure, and passage.** Anything copied from a textbook or another site is a legal blocker for release. Flag anything whose origin you can't establish.
- Attribution and license files for third-party code, datasets, and icons; the project's own `LICENSE`.
- `README`, contribution guide, architecture doc, and a doc explaining the numerical methods and their limits.
- Instructor-facing material, if teachers are part of the audience.

### L. Release engineering and operations

- Reproducible build, pinned toolchain, deploy pipeline, rollback plan.
- Environment config, staging environment, feature flags.
- Error monitoring and a way to learn that a solver is failing in production.
- Versioning and changelog; a support/feedback channel.
- Browser/device support matrix, actually tested.
- Offline behavior / PWA, if relevant.
- SEO/meta/social cards; favicon; page titles that aren't "React App".
- Analytics that respect privacy, or a documented decision not to have any.

---

## 4. Phase 3 — Verification experiments you must actually run

Write scripts under `/tmp/ode-audit/` that import the app's real solver code. Report the numbers, not impressions. If the code can't be imported headlessly, that itself is a finding.

1. **Convergence order.** For each fixed-step integrator, solve `y' = -2y, y(0)=1` and `y' = y·cos(t), y(0)=1` over `[0,5]` at halving step sizes. Fit log(error) vs log(h) and report the observed order. It must match the claimed order to within ~0.15. Anything off means a coefficient bug.
2. **Tolerance obedience.** For each adaptive integrator, sweep `rtol` from `1e-3` to `1e-12` on a problem with a known solution and confirm the achieved error tracks the requested tolerance roughly linearly on a log–log plot.
3. **Stiff benchmark.** Van der Pol with `μ = 1000`, and the Robertson problem over `[0, 1e5]`. Record step counts, wall time, and whether the solver completes at all. Report the timing hit on the UI thread.
4. **Energy drift.** Undamped pendulum and harmonic oscillator over 10,000 periods. Plot energy vs time for each integrator. Quantify drift.
5. **Reference cross-check.** Compare against SciPy `solve_ivp` (RK45, Radau, LSODA) on the app's own model library. Report max deviation per system.
6. **Pathological inputs.** `y' = y²` with `y(0)=1` past `t=1` (finite-time blow-up); `y' = y^(1/3)` with `y(0)=0` (non-unique); `y' = 1/(t-1)` through the singularity; a discontinuous RHS; an RHS that returns `NaN`. Record exactly what the user sees in each case.
7. **Equilibrium/classification spot-check.** Hand-verify the app's fixed points and eigenvalue classifications for Lotka–Volterra (center — the borderline case), the damped pendulum, and a saddle-node normal form.
8. **Event detection.** Bouncing ball or threshold crossing: measure the error in the reported event time vs the analytic value.
9. **Long-horizon chaos.** Lorenz at standard parameters, two initial conditions differing by `1e-10`, integrated to `t=100`. Confirm the app doesn't present a late-time trajectory as a reliable prediction.
10. **UI stress.** Slider drag with continuous re-solve on the heaviest model; measure dropped frames and main-thread block time.

---

## 5. Phase 4 — The improvement backlog (≥ 50 items)

Produce **at least 50** improvements. Quality bar: each one must be something a developer could pick up and finish without asking you a follow-up question.

**Required distribution** (minimums; exceed them freely):

| Category | Min items |
|---|---|
| Numerical correctness & solver quality | 8 |
| Nonlinear / dynamical-systems tooling | 6 |
| Symbolic & analytical layer | 4 |
| Pedagogy & content | 8 |
| UX & interaction | 6 |
| Accessibility | 4 |
| Architecture & code quality | 5 |
| Performance | 3 |
| Testing & CI | 5 |
| Security & privacy | 3 |
| Release ops, docs & licensing | 4 |

**Format for every item:**

```
### [CAT-##] Short imperative title

- **Severity:** P0 blocker | P1 high | P2 medium | P3 polish
- **Effort:** S (<2h) | M (<1d) | L (<1w) | XL (>1w)
- **Confidence:** high | medium | low — and why
- **Evidence:** file:line, or the command/experiment that revealed it
- **Problem:** what's wrong and who it hurts
- **Proposed change:** specific enough to implement; name files, functions, algorithms
- **Acceptance criteria:** testable conditions, ideally as a test that would fail today
- **Dependencies / risks:** what must land first, what could break
```

Rules for the backlog:

- No duplicates and no near-duplicates. Merge related work into one item with sub-tasks rather than padding the count.
- No filler. "Add more tests" is filler; "Add convergence-order tests for `dopri5` asserting observed order ≥ 4.85 on `y'=-2y`" is not.
- Every P0 must be traceable to concrete evidence.
- Include at least 5 items that are **removals or simplifications**, not additions.
- Include at least 3 items that would improve the app's *honesty* — places where it currently overstates the reliability of a numerical result.
- Rank by (user impact ÷ effort), and present a summary table sorted by severity at the top of the file.

---

## 6. Phase 5 — Roadmap and release gate

1. **Milestones.** Group the backlog into: `M1 — Correctness & safety` (nothing ships wrong), `M2 — Release blockers`, `M3 — Quality bar`, `M4 — Post-launch`. Give each a rough duration and an ordering rationale.
2. **Critical path.** Identify the dependency chain that determines the earliest possible release date.
3. **Release checklist.** A concrete go/no-go list with binary checks — build reproducible, CI green, all P0s closed, license audit clean, a11y audit passing, browser matrix verified, error monitoring live, rollback tested, content provenance documented.
4. **Definition of done** for this project's issues, so future work matches the bar.
5. **Top 10 list.** If only ten of these items are ever done, which ten, and why.
6. **Risk register.** The three things most likely to go wrong at launch, with mitigations.

---

## 7. Deliverables

Write these files to the repo root (create the directory `audit/` and put them there):

| File | Contents |
|---|---|
| `audit/00-INVENTORY.md` | Phase 1 output: module map, feature and math-content inventories, repo health |
| `audit/01-FINDINGS.md` | Phase 2 output, organized by lens A–L, every finding evidenced |
| `audit/02-EXPERIMENTS.md` | Phase 3: methodology, scripts used, tables of numbers, plots if produced |
| `audit/03-BACKLOG.md` | Phase 4: summary table + all ≥50 items in the required format |
| `audit/04-ROADMAP.md` | Phase 5: milestones, critical path, release checklist, top 10, risks |
| `audit/README.md` | 1-page executive summary: is this app releasable, what's the single biggest risk, what's the shortest path to launch |

Also print to the terminal, at the end: the item count per category, the P0 list, and anything you were unable to verify.

---

## 8. Quality bar — what a bad audit looks like

Avoid all of these:

- Generic advice that would apply to any codebase ("add error handling", "improve documentation").
- Praise padding. Note strengths briefly in the summary; the body is for problems.
- Restating the code back to me instead of judging it.
- Claiming numerical correctness without running a convergence test.
- Hedging every finding into meaninglessness. Commit to a severity.
- Inventing line numbers or files.
- Hitting 50 items by splitting one idea into six.
- Ignoring the math. The mathematics is the product here; a beautiful UI over a wrong integrator is a worse app than the reverse.

---

## 9. Start here

1. Confirm you can build, run, and test the app; report any blockers immediately.
2. Do Phase 1 and show me the inventory before going further.
3. Then proceed through Phases 2–5 without stopping, and write all six deliverables.
4. Ask me questions only if a blocker actually prevents progress; otherwise record assumptions in `audit/00-INVENTORY.md` and continue.
