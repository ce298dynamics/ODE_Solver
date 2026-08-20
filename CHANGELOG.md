# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
