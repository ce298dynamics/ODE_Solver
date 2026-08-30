# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Lesson figures: three pictures you can move.** At the top of *Learn*,
  where the topic has one. A note can say that raising the harvest rate
  eventually wipes out both equilibria; a figure lets you raise it and watch
  the two dots slide together and vanish, which is a different kind of knowing.

  *Slope fields* draws the dashes `y' = a·y + b·t` demands at each point — no
  solving involved — and integrates a solution through anywhere you click,
  forwards and backwards. The curve comes out tangent to every dash it passes,
  and two curves never cross: uniqueness shown rather than stated.
  *Equilibria* plots `f(y)` for the harvested logistic equation, marks each
  equilibrium filled or hollow by which way its arrows point, and puts an arrow
  in every interval between them; push `h` past `r·K/4` and both equilibria are
  gone. *Euler's method* runs Euler and RK4 on `y' = y`, whose answer nobody
  has to take on trust, and reports both endpoint errors — printed as
  measured rather than as theory: 1.8 and 14.7 at `h = 0.2`, climbing towards
  2 and 16 as `h` shrinks, which is what an order statement actually claims.

  **No figure computes mathematics of its own.** The dashes come from
  `analysis.slope_field`, the equilibria from `analysis.phase_line`, the steps
  from `byhand.walk` and `byhand.refinement`, and the curves from the library's
  own `solve`, so a figure cannot disagree with the tool that teaches the same
  thing. A lesson names its figure by key, because `lessons/` holds content and
  no Qt; the tests check both directions of that indirection, so a typo is a
  failure rather than a lesson that silently lost its picture.

- **`analysis.phase_line`** — the equilibria of a scalar autonomous equation,
  with the sign of `f` on either side and the linearisation beside it.
  Deliberately not `find_fixed_points` with an axis thrown away: that routine
  classifies a planar equilibrium by the eigenvalues of a 2×2 Jacobian, and a
  scalar equation has no such thing. On a line the sign of `f` either side
  settles which way solutions move, which is what a course draws and what stays
  right where the linearisation says nothing — `y' = y²` has `f'(0) = 0`, so
  the derivative test calls it neutral and loses both arrows while the signs
  correctly call it semi-stable. Roots are found by refining every local
  minimum of `|f|` rather than only the sign changes, for the same reason: a
  root the curve touches without crossing has no sign change to bracket.

- **Three more techniques the Hub can narrate: exact equations, the
  homogeneous substitution `y = v·t`, and Bernoulli.** With them the first two
  units of the course are complete, and *Solve Step by Step* now writes out
  eight methods a move at a time rather than five.

  **Exactness is decided structurally, never from a hint.** Six exact equations
  were split into `M dt + N dy` and tested against `∂M/∂y = ∂N/∂t`:
  `classify_ode` misses `1st_exact` on three of them — precisely the three an
  exact-equations lesson is about, including `y' = −(2t+y)/(t+3y²)` — and
  offers it on `y' = −y/t²`, which that test says is not exact. It normalises
  `M` and `N` differently, so neither half is a sympy bug; it does mean the
  hint cannot be trusted, so the detector runs here, and only where no named
  technique applies. An equation that is both exact and linear therefore keeps
  the integrating factor, which is the method a course meets it by first.

  **The two substitutions reuse the narrators they reduce to** rather than
  copying them: each builds a real equation in a real `v`, hands it to the
  separable or integrating-factor narrator, then undoes the substitution and
  applies the initial condition once, to the answer in `y`. Those two narrators
  grew a parameter naming the letter to print, because a derivation that called
  `v` "y" while solving for `v` would misreport what it had just done. Where
  undoing an even root leaves a sign, the initial condition chooses it — and
  the negated branch is offered only once it has been checked to solve the
  equation too.

  **`dsolve` is no longer asked to reproduce an answer it had no hint for.** On
  `y' = −(2t+y)/(t+3y²)` it runs past forty seconds trying `lie_group`, so the
  whole twelve-second budget bought a timeout; the narrated answer has by then
  been substituted back and simplified to zero, which is a stronger warrant
  than `dsolve` returning would have been. The guard is narrow by design: where
  the hint list does name the technique, sympy is asked exactly as before.

- **Eight more lessons, and Units 1 and 2 finished.** What a differential
  equation is; slope fields, existence and uniqueness; exact equations;
  substitutions (homogeneous and Bernoulli); population models and the logistic
  equation; equilibria, stability and the phase line; acceleration, velocity
  and drag; and Runge–Kutta, split out of the numerical lesson so that Euler's
  method and what order buys are no longer one page. Fifteen lessons now.

- **Learning Hub: `Lessons`** — notes and practice for seven topics: separable
  equations, integrating factors, characteristic roots, undetermined
  coefficients, Cauchy–Euler, Laplace transforms, and the numerical methods.
  The other four Hub screens are tools that work on an equation you bring; this
  is the part for someone who does not yet know which equation to bring.

  **Practice is graded by mathematics, not by an answer key.** A typed solution
  is substituted into the equation and simplified, through the same
  `check_answer` the Solve Step by Step screen uses, so every correct form
  passes and nothing is marked wrong for being spelled differently.
  Multiple-choice questions exist only for what that cannot reach — *which
  technique solves this* is what a course actually tests — and each one shows
  its reasoning whether you were right or wrong.

  **The worked examples are generated, not transcribed.** Each runs through the
  same narrator that powers the tool it belongs to, so a lesson cannot drift out
  of step with the screen that explains it, and `tests/test_lessons.py` runs the
  real narrator over every question to prove each has an answer the app can
  produce — and that the grader accepts the app's own answer, which is the worst
  failure this screen has available.

- **Progress is remembered between sessions**, in a small JSON file in the
  platform's config directory, with a reset button beside it. The first thing
  this application has ever stored on disk, so it is careful about it: a
  corrupt, hand-edited or truncated file reads as "nothing recorded" rather than
  raising, writes are atomic, and answering correctly and then mistyping does
  not take the tick away.

- **Learning Hub: `Drill` — practice that does not run out.** A fourth part of
  every lesson that has one, beside Learn, Examples and Practice. Each drill is
  a question with its numbers left open, so it can ask the same *method* in
  eleven to forty-eight different versions; three right in a row masters it, and
  one wrong answer starts the count again.

  **A generated question is an ordinary practice question.** `draw(template,
  seed)` returns the same `Solve` the hand-written questions use, so it is
  graded by the same substitution, hinted by the same ladder and worked by the
  same narrator. The drill adds no mathematics of its own and so cannot
  disagree with the rest of the Hub about what is correct.

  **Draws are enumerated, not sampled**, which is what makes the guarantee
  checkable rather than merely likely: `tests/test_templates.py` runs the real
  narrator over **every draw of every template** — 275 of them — and requires
  each to be narrated by the technique the drill claims to teach, to have every
  step verify, and to have its answer accepted by the grader. Nobody wrote
  these questions, so nobody read them either; that sweep is what stands in for
  having read them. Enumerating also means the same seed always gives the same
  question, so pressing Check cannot change it underneath you, and the drill can
  say "one of 18 versions" because it knows.

  Eleven drills across six lessons. The numerical lesson deliberately has none —
  Euler and RK4 have no closed form for the grader to substitute into, so a
  drill there could never say "right", and its button is absent rather than
  opening a page that cannot work.

- **Learning Hub: a `Course Map`, and lessons organised into units.** Seven
  lessons in a flat list was navigable; the whole of a first course is not. The
  lessons are now filed under the chapters of Edwards, Penney and Calvis —
  first-order equations, models and numerical methods, second-order linear
  equations, Laplace transforms — and the new screen shows the units, the
  lessons inside them, how far through each you are, and a *Continue* button
  that opens the earliest lesson with a question left.

  A unit appears on the map once it has lessons. There is no stand-in for a unit
  still to be written: this application removed its last placeholder
  deliberately, and a course map advertising empty units would put them back.

- **A lesson is now three parts rather than one page** — *Learn*, *Examples* and
  *Practice* — with the lesson's title and the part you are in staying put while
  the rest scrolls. Each lesson also states what you should be able to do
  afterwards, cites its textbook section, and names the lessons worth having met
  first. The prerequisites are advice, not a gate; nothing is locked.

- **Notes come in kinds, and a common mistake does not read like an idea.** The
  same card, with a warning stripe down it and a label above it, because the
  thing that catches people is worth setting apart from the thing that is merely
  true. Five of them are new: reading `p` off an equation whose `y'` still
  carries a coefficient, the two branches a rearrangement can produce, `r(r−1)`
  rather than `r²` in the indicial equation, `y(0)` carrying the factor of `s`
  and `y'(0)` not, and guessing only the top power of a polynomial.

- **Hints come one rung at a time.** A nudge, then the first move, then the
  next, with "Show me" — the real narrator — at the end of the ladder. Every
  practice question has at least two rungs; a single hint is either useless or
  the answer.

- **Every multiple-choice question explains every option**, not just the right
  one, and the reason shown is the reason for the option *picked*. Explaining
  the right answer back at somebody who did not choose it teaches nothing: the
  reason a wrong option was tempting is usually what was actually
  misunderstood.

- **Six more worked examples**, so most lessons now show a plain case and then
  one that breaks the plain rule — `y' = y²` running to infinity in finite time,
  a complex root pair becoming a cosine and a sine, a repeated indicial root
  bringing in `ln t`, a switch thrown at two seconds. Each says what it is there
  to show, and all thirteen are generated and checked by the narrator, which
  `tests/test_lessons.py` now verifies for every example rather than only the
  first.

### Changed

- **`lessons.py` is now a package**, one module per unit plus the shared model.
  Seven lessons was 837 lines; a whole course is not something one file should
  carry. Nothing that imported it needs to change.

- **Drill progress is kept in its own bucket**, `<lesson>/drill`, and counted by
  a streak rather than by an ever-answered-correctly. Mixing it with the
  practice questions would have made "3 of 5" meaningless: one number is out of
  a fixed denominator and the other is not.

- **The progress file records attempts as well as outcomes** (format version 2),
  because a course map that can only say "answered" cannot tell steady work from
  a lucky guess. A version 1 file — one written by any earlier build — still
  loads with its ticks intact and is rewritten in the new shape; refusing to
  read it, or quietly dropping it, would take away work already done. Answering
  correctly and then mistyping still keeps the tick, and now counts the attempt,
  because it happened.

- **The Learning Hub takes `Ctrl+1` to `Ctrl+6`**, the Course Map first. Solver
  Studio is unchanged on `Ctrl+Shift+N`.

- **Home offers every Learning Hub screen.** `Lessons` never had a tile and was
  reachable only from the sidebar, a shortcut or `--screen`; it and the Course
  Map now have one.

- **Shortcuts are numbered per section**, `Ctrl+N` for the Learning Hub and
  `Ctrl+Shift+N` for Solver Studio. Eleven screens no longer fit a single run of
  digits, and the flat run had the odd effect that `Ctrl+5` jumped out of the
  section you were in. Every binding is still globally unique, which is the
  property that mattered.

### Fixed

- **A `dsolve` answer with several branches is no longer thrown away.** Where
  solving for `y` leaves branches — `y' + y = t·y³` comes back as the plus and
  minus square roots — `dsolve` returns a *list* rather than one equation, and
  reading `.rhs` off the list raised `AttributeError`. The worker reported that
  as "sympy has no method for this equation", discarding an answer sympy had
  actually found.

- **A separable equation with two branches showed the wrong one.** ``y' = t/y``
  with ``y(0) = 2`` rearranges to ±√(t² + 2C), and the first root was taken
  regardless — the negative branch, which satisfies the equation but passes
  through no point the condition allows. Nothing complained, because the answer
  *was* a solution. The branch the condition sits on is now the one shown.

- **A decimal coefficient poisoned the answer**, the same way a decimal initial
  condition did before it. ``y' = 2 - 0.05*y`` produced a constant whose
  imaginary part was the *number* 3.14159… rather than `pi`, which sympy cannot
  cancel, so a mixing-tank answer that should read ``40 - 35e^{-t/20}`` came out
  carrying a complex exponential. Coefficients are rationalised along with the
  conditions.


## [0.4.0] — 2026-08-19

### Added

- **Learning Hub: `Laplace Transforms`**, and with it the Learning Hub is
  complete — no screen in the application is a placeholder any more.

  The transform is the one technique in a first course that turns the equation
  into *algebra*, and the only one that copes with forcing switched on partway
  through or delivered as an impulse. ``y' + y = u(t-2)`` — a switch thrown at
  two seconds — is not separable, has no integrating factor worth writing, and
  is not what undetermined coefficients is for. It comes out here as the
  textbook ``u(t-2)(1 - e^{-(t-2)})``, and ``y'' + y = δ(t-1)`` as
  ``sin(t-1)u(t-1)``.

  Six steps, each a real move of the method, and the initial conditions enter at
  the *start* through ``L{y''} = s²Y - s·y(0) - y'(0)`` rather than arriving at
  the end as constants to be pinned down — which is the point of the technique
  and what separates it from everything else in the Hub. A transform table sits
  alongside with the rows the answer actually needed highlighted.

  It reuses rather than rebuilds: the result is a `steps.Derivation`, so it
  renders through the panel L2 already built and travels over the wire format
  L2 already defined, and it runs in the subprocess `dsolve` already owns. That
  subprocess grew a mode rather than a twin; `dsolve` itself is not run at all
  here, since the derivation carries the answer and checks it.

- **`Heaviside` and `DiracDelta` are typeable — on the Laplace screen only.**
  Without them a user could not type the forcing that motivates the entire
  topic. With them everywhere, the Solver Lab would accept a `DiracDelta` that
  cannot be lambdified at all (`NameError` at solve time) and a discontinuous
  right-hand side that an adaptive step can cross without noticing, which is a
  failure this project already documents. So `parse_equation` takes an explicit
  widening and exactly one caller passes it.

- **Learning Hub: `Solve Step by Step` narrates the derivation.** Five techniques
  — separation of variables, integrating factors, characteristic roots,
  undetermined coefficients, Cauchy–Euler — written out a move at a time, with
  the reason each move is legal. That is what a first course is about, and it is
  the one thing `dsolve` cannot be asked for: it returns an answer and does not
  expose the moves it made.

  **Every step is checked, not merely printed.** The antiderivatives are
  differentiated back and compared with their integrands; each basis function is
  substituted into the equation and required to give exactly zero; the
  particular solution has to reproduce the forcing term. A card carries a tick
  only where its own claim was verified, and a step that fails verification is
  shown failing rather than hidden. A derivation that quietly prints a wrong
  line is the one thing worse than no derivation.

  Equations outside the five get no derivation at all rather than a vague one —
  the same degradation `SymbolicSolution` already makes between *timed out*, *no
  method*, and *found but unverified*.

- **The technique is now named the way a course names it.** This was the finding
  the whole phase turned on. `classify_ode` orders its hints by what sympy would
  rather *solve* with, which is not the order a course *teaches*:

  | equation | sympy's first hint | what it is called |
  |---|---|---|
  | `T' = -k(T - 20)` | `factorable` | separable |
  | `y' + 2y = t` | `1st_exact` | integrating factor |
  | `y'' + 3y' + 2y = 0` | `factorable` | characteristic roots |
  | `t²y'' + ty' - y = 0` | `factorable` | Cauchy–Euler |

  The app stored `hints[0]`, so **four of the five techniques would never have
  dispatched**. The worker now returns the whole tuple and the teaching name is
  preferred. That also fixes the Solver Studio's Symbolic tab, which had been
  labelling `y'' + 3y' + 2y = 0` as "factorable" — true, and useless.

- **The app is split into two sections: Learning Hub and Solver Studio**, over a
  shared Home. The Studio holds the five screens that already existed — Solver
  Lab, Phase Portrait, Stiffness Explorer, Method Race, Accuracy Lab — and the
  Hub is a new section for learning to solve ODEs, currently four placeholders
  being filled in by phase: Solve Step by Step, Laplace Transforms, Methods by
  Hand, Worked Problems.

  The split is presentation only. Both sections drive the same `SessionState`
  and select from the same catalogue by key, which is what lets a problem —
  including one the user typed — appear on either side without either knowing
  about the other.

  `go(key)` still takes a bare screen key and now resolves the section itself,
  because every caller passes one that way: `cli.py --screen`, the Home tiles,
  and the tests. Shortcuts stay globally unique rather than restarting per
  section, so one never means two different screens.

  Verified by the same 42-render offscreen comparison used for the
  control-panel refactor: the five existing screens render **pixel-identically**
  to before the split. A navigation change must not disturb what it navigates
  to.

- **`euler` and `rk4` are real methods.** The method list previously started at
  Bogacki–Shampine, so a learner could not select either of the two methods they
  had just been taught. Both are tableaux like every other explicit method, and
  both are verified by the machinery that already existed: the rooted-tree order
  conditions hold at their claimed order and *fail* one higher, and the measured
  slopes are 1.00 and 4.00.

  Neither carries an embedded pair, so `ButcherTableau.e` may now be None and
  such a method runs fixed-step — the driver requires `n_steps` or `first_step`,
  exactly as it does for the symplectic methods. Inventing an error estimate for
  them would have let the controller adapt on a meaningless number, which is the
  failure this project has a recorded bug for.

- **Learning Hub: `Methods by Hand`.** Euler and RK4 written out the way a course
  teaches them — one row per step with the slope, the stages, the increment, the
  new value and the error — plus a halve-the-step table whose ratio column is the
  order, measured. Every number comes from the library's own stepper, and
  `tests/test_byhand.py` asserts the walkthrough matches `solve` at the same step
  size bit-for-bit.

- **Learning Hub: `Solve Step by Step`**, with **"check your answer"**. A student
  types their own solution; it is substituted into their equation and simplified.
  The same check the library already applies to sympy's answer, pointed at the
  user's instead — so equivalent forms pass, initial conditions are checked
  separately from the equation, and "cannot decide" is reported as such rather
  than as "wrong".

- **Learning Hub: `Worked Problems`**, and six textbook models behind it: mixing
  tank, Newton's cooling, RC circuit, falling with drag, harvested population,
  spring–mass–damper. The catalogue previously held only integrator benchmarks;
  these are what a first course is actually about, and each carries where its
  equation comes from and what the letters mean, in real units. They are ordinary
  catalogue entries, so they appear in the Solver Studio's pickers too.

### Changed

- **A check is never named unless it is the one performed.** Most answers in the
  Hub are decided by substituting them back and simplifying to zero, and the
  panel said so. A switched answer cannot be decided that way — differentiating
  a Heaviside leaves Dirac terms that never cancel *even when the answer is
  right* — so those are decided against this project's own integrator instead.
  `Derivation.check` records which route decided it, and the verdict line says
  what actually happened rather than claiming a substitution that never ran.

  An impulse can be decided by neither route and is reported unchecked. Never
  wrong: "cannot decide" is not "incorrect", the rule `check_answer` and
  `steps._conditions_hold` already follow.

- **`apart` is not asked to do the impossible.** It raises `PolynomialError` on
  an ``e^{-as}`` factor — on exactly the switched and impulsive problems this
  technique exists for. The delay is split off first and narrated as the second
  shifting theorem, so the obstacle and the teaching turn out to agree and the
  derivation gains a step rather than losing one.

- **A variable-coefficient equation is declined with its reason.** ``L{t·y'}``
  is a derivative in s, so transforming ``t·y' + y = 0`` produces another
  differential equation rather than an algebraic one. It previously produced an
  unevaluated `InverseLaplaceTransform` on screen and claimed the answer was
  *wrong*; it now says the transform does not simplify this equation, which is
  true and useful.

- **`_Placeholder` is gone.** It existed so a screen that was missing looked
  different from one that was broken, and every phase of the Learning Hub
  removed one. With the last replaced it was dead code, and the test that pinned
  the remaining set now asserts something stronger and permanent: no screen is a
  stand-in.


- **A derivation now outlives a `dsolve` that hangs.** The worker publishes the
  classification and the derivation *before* attempting `dsolve`, and the parent
  recovers that line from the killed process's captured output when the timeout
  fires. `y' = sin(y)` is the case: it is the equation this project records
  `dsolve` hanging on — not stalling, hanging — and separation of variables
  solves it in about four seconds. The Hub shows a complete verified derivation
  where the Studio can only report a timeout.

  What is published happens in two stages, cheapest first: the classification
  costs milliseconds, the derivation can cost seconds. Emitting only once, at
  the end of both, was a regression found by the test for it — a slow
  derivation took the classification down with it, so *asking* for steps made
  the reply worse than not asking.

  The remaining cost is stated rather than hidden: narration and `dsolve` share
  one hard budget, so a derivation slower than the timeout is lost with it. On
  a busy machine that happens — narrating `y' = sin(y)` takes about four
  seconds idle and can exceed thirty under a fully parallel test run. The
  classification always survives; the derivation is best-effort.


- **`driver.solve` split into the loop and its bookkeeping.** It had reached 408
  lines: the loop plus argument validation, step-endpoint arithmetic, output
  accumulation and event tracking. Those four now live in `odesuite/_loop.py`
  as `prepare_tolerances`, `StepPlanner`, `Recorder` and `EventTracker`, and
  `solve` is 237 lines of which 51 are its docstring. It is no longer the
  longest function in the project.

  Purely structural: the refactor was gated on 78 solves — every method family,
  dense output, `t_eval`, events with and without sub-step scanning, fixed-step
  runs, backward integration, DAEs, both failure paths and the callback —
  hashing **bit-identically** before and after, states, event times, work
  counters, messages and sampled dense output included.

- The extracted pieces have unit tests for the first time (`tests/test_loop.py`,
  36 of them). That was the point of extracting them: rules like "a fixed-step
  run lands on `t0 + k*h` computed afresh, never on an accumulated sum" — the
  arithmetic behind recorded bug #4 — could previously only be checked by
  inference from a finished trajectory.

- **`solve_bvp` split the same way**, 262 lines to 126 (96 of code). The
  shooting machinery — five closures over the function's own arguments — is now
  a `_ShootingSystem` holding the problem, the nodes and the inner solver's
  settings, exposing the three things Newton asks for: residual, Jacobian, and
  the spliced continuous solution. The Armijo backtracking is `_line_search`,
  which isolates the awkward part: a diverged shot raises rather than returning
  a large residual, and has to be read as "step too long". What remains in
  `solve_bvp` is the damped Newton iteration, which is its job.

  Gated on 32 BVP solves hashing bit-identically: linear and oscillatory
  problems at 1/2/5/10/20 nodes, all three guess forms, both Bratu branches,
  the iteration limit, a custom `fd_floor`, a stiff inner method, an
  unintegrable guess, and the three argument-validation errors.

  13 new tests check the machinery directly, the sharpest being the assembled
  Jacobian against a brute-force dense difference of the whole residual — the
  `-I` coupling blocks are written in analytically rather than differenced, and
  an error there converges fine on easy problems and fails mysteriously on hard
  ones.

- **The five screens no longer each rebuild their control column.** Every one of
  them opened `_build_controls` with the same seventeen lines of Qt scaffolding
  and closed it with the same five, and between them repeated a three-line
  heading idiom twenty-one times. Both are now `control_panel()` and
  `add_heading()` in `widgets/controls.py`, and `_build_controls` across the
  five drops from 441 lines to 322.

  Deliberately a helper and not a base class: the middles of those functions are
  genuinely different screens, and forcing them into one shape would be worse
  than the duplication. The panel width stays a caller's argument for the same
  reason — the five differ (238 to 258 px), which looks like drift rather than
  design, but unifying it would change the layout, and that is not what
  extracting boilerplate is for.

  Gated on 42 offscreen renders — every screen, both palettes, whole and
  per-panel — hashing **pixel-identically**.

### Fixed

- **An unparseable equation crashed the handler instead of reporting itself.**
  `show_message(..., error=True)` — the parameter is `kind` — so typing
  ``y' = foo(t)`` into `Solve Step by Step` raised a `TypeError` inside the
  signal handler and left the screen silent with a traceback on stderr. The
  editor only checks that a derivative is present, so anything it does not know
  about reaches `parse_equation` and fails there; this was reachable by typing.
  Shipped in L2 and found by writing the equivalent test for the Laplace screen.

- **A decimal initial condition poisoned the answer.** `y(0) = 0.1` parses to a
  float, which propagates through `solve` into a constant whose imaginary part
  is the *number* 3.14159… rather than `pi`. sympy cannot recognise that as pi,
  so `e^(t + 3.14159…i)` never collapsed to `-e^t`: the built-in logistic example
  displayed a complex exponential it did not need, and its conditions step was
  marked **failed** — a red cross on a correct step. Conditions are rationalised
  before solving, and the logistic now reads `e^t / (e^t + 9)`.

- **"Cannot decide" is no longer reported as "wrong"** when checking that a
  solution meets its initial conditions, matching the rule `check_answer`
  already follows. False has to mean demonstrably wrong; a floating-point
  residual or an unresolved parameter means undecided, and says so.

## [0.3.0] — 2026-08-17

### Added

- **`solve(..., callback=...)`** — called after every accepted step with
  ``(t, y, stats)``; returning ``False`` stops the integration and the solve
  returns ``status="cancelled"``. Progress reporting, live plotting, streaming
  output and cancellation from another thread were all previously impossible
  because nothing in the loop offered a way in.
- **`Solution.cancelled`**, distinguishing a deliberate stop from a failure.
  ``success`` stays False for a cancelled solve: the trajectory is valid but
  the requested interval was not integrated, and code checking ``success``
  before reading ``y[:, -1]`` as an endpoint must not treat a partial result as
  a complete one.
- **`Event(..., subdivisions=k)`** — samples the event function inside each step
  instead of only at its ends. Endpoint comparison misses any *even* number of
  crossings within a step, silently; measured on a smooth decay with
  ``g = sin(20t)``, 63 roots exist and endpoint comparison finds 5. With
  ``subdivisions=16`` all 63 are found, each to 2e-14. Off by default, since an
  event that changes sign once gains nothing. `scipy.integrate.solve_ivp` has no
  equivalent.
- **`SolveRunner.submit(..., supersede=True)`** and `cancel_all()` in the studio.
  A superseded solve now stops at its next step boundary instead of running to
  completion for an answer that will be discarded. Opt-in, because concurrency
  is not always supersession — the Method Race submits one solve per method
  through the same runner and wants every one of them.
- `examples/09_progress_and_hidden_events.py`.

### Documented

- **Where `PredictiveController` loses.** The Tier 2 measurements that made it
  the default for implicit methods all used problems supplying an analytic
  Jacobian. Differenced, it still wins on HIRES (0.83x), Van der Pol (0.84x) and
  OREGO (0.87x), but costs 2.10x on Robertson, whose own finite-difference
  Jacobian is notoriously poor — one component near 1e-8 against entries of `J`
  reaching 3e7. Supplying `jac`, as its catalogue entry does, reverses it. The
  docstring now carries the table and two tests pin it.

## [0.2.0] — 2026-08-17

The first release that can be installed, and the first with a measured
performance claim behind it.

### Added

- **`PredictiveController`** — Gustafsson's predictive step-size controller, and
  the default for the implicit methods. It adds a term reading how the error
  responded to the last step-size change rather than the current error alone,
  and declines any proposed growth under 1.2× outright, keeping `h`
  bit-for-bit identical so the iteration matrix stays valid.
- **`Stepper.default_controller`** — a method now states which controller suits
  it. A step-size change is free for an explicit method and costs an `O(n³)`
  refactorisation for an implicit one; that is a property of the method, not a
  caller preference.
- `examples/` — eight runnable scripts, every one executed by the test suite.
- A documentation site (`mkdocs.yml`, `docs/`) with an API reference generated
  from the docstrings.
- `py.typed` — the library has been fully annotated and `mypy`-clean for a while,
  and without this marker none of that was visible to a downstream type checker.
- `ruff` and `mypy` configuration, and GitHub Actions CI across Linux and
  Windows on Python 3.10 and 3.12, including a job asserting that the library
  never imports Qt.
- `tests/test_controllers.py` and `tests/test_newton.py` — the two modules that
  had no direct tests at all.
- `figures/work_precision.json`, written beside the figure so a change in
  performance is a reviewable diff rather than something spotted by eye.

### Changed

- **Stiff solvers are 1.18–1.32× faster**, using 19% fewer RHS evaluations and
  10% fewer LU factorisations. Against SciPy's Radau the gap closed from
  1.3–1.5× evaluations to 1.08–1.22×, and from ~1.7× wall time to 1.2–1.5×.
  Explicit methods are unaffected, and a test asserts their output is bitwise
  identical.
- `irk.py` now uses `simplified_newton` and `JacobianPolicy` instead of
  reimplementing both inline. Verified bit-identical on the stiff benchmarks.
- `ODEProblem.f` fast-paths a right-hand side that already returns a 1-D array;
  `is_dae` is cached instead of running an SVD on every access.
- `solve(controller=...)` now defaults to `None`, meaning "let the method
  choose". Passing a name or instance still overrides it.
- The work-precision figure wraps into a grid; it was previously a 3 806 px-wide
  strip in which no legend was legible.
- The version is declared once, in `odesuite.__version__`. It had drifted across
  three files.

### Fixed

- **A reused `Controller` instance carried its error history between solves**, so
  the same problem solved twice gave 82 steps and then 83. Nothing raised and
  both answers were within tolerance; the only symptom was that an identical
  computation was not reproducible.
- **`thumbnails.render_thumbnail` drove pyplot from a worker thread** while its
  own docstring promised thread-safety. pyplot's figure registry is global and
  `matplotlib.use` swaps the global backend.
- A non-finite state is now reported as such instead of surfacing as step-size
  underflow, which named nothing the caller had written.
- `_solve_event` returned the end of the step as a root when the bracket did not
  survive interpolation — a fabricated detection, which could also consume a
  terminal event's allowance. It now reports none.
- `DSOLVE_TIMEOUT` was bound as a default argument at import and could not be
  changed at runtime; `symbolicpanel` had imported the value rather than the
  module, freezing it twice over.
- `odesuite-gui` printed a bare PySide6 traceback when the `app` extra was not
  installed. It now says which extra to install. `--list-problems` and
  `--selftest` work without Qt.
- A docstring in `steppers/exponential.py` had a prose paragraph inside its
  `Parameters` block, so every numpydoc tool read the first word of each line as
  a parameter name.
- `test_split_solve_is_cheaper_on_a_large_system` compared two ~4 ms wall-clock
  samples and inverted under `pytest -n auto`. It now times the factorisation
  the claim is actually about (a ~9x margin rather than 1.5x), and skips where
  the platform BLAS has a pathologically slow complex `getrf` — measured at
  1300x slower than the real path for n >= 100 with numpy 2.2.6 on Windows,
  which makes the split path lose for reasons that have nothing to do with this
  library. The deterministic half of the old test, that the two linear-solve
  paths agree, is now its own test.

## [0.1.0] — 2026-08-16

The state of the project when it came under version control: the library, the
studio, and 943 tests. Its development is narrated in the README — the adaptive
Runge–Kutta core, stiff solvers and DAEs, events and dense output, the Taylor
and exponential integrators, the symbolic equation solver, and the typeset
closed forms.

[0.2.0]: https://keepachangelog.com/
[0.1.0]: https://keepachangelog.com/
