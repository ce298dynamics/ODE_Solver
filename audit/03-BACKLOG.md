# Phase 4 — Improvement Backlog

**57 items.** Every one traces to a finding in `01-FINDINGS.md` or an experiment in
`02-EXPERIMENTS.md`. No item is a split of another; no item is "add more tests".

---

## Status — M1 is closed

| Item | State | Evidence |
|---|---|---|
| **SEC-01** Validate the expression AST | **done** | `custom.reject_unsafe_syntax`; `tests/test_security.py`, 53 tests |
| **NUM-01** Stop `Jet` crashing the interpreter | **done** | elementwise object-array handling in `taylor.py`; `y' = y cos t` now integrates to 5.8e-15 |
| **NUM-02** Radau's tolerance shortfall | **done** | `newton_tol_factor` + `newton_iteration_budget`; 54.5× → 0.77× at `rtol=1e-12` |
| **NUM-03** RODAS4's first-order floor | **done** | central-difference `∂f/∂t`; order 4 now holds to 1.3e-14 |
| **NUM-04** Fixed-step overflow | **done** | `fixed_step_message`; 909,393 rejections → 1, correct diagnosis |
| **NUM-07** `dfdt` on `ODEProblem` | **done** | new keyword, validated at point of use |
| **NUM-08** Wrap RHS exceptions at `t0` | **done** | `y' = 1/t` from 0 now names `t0` and the cause |
| **SEC-02** Pin dependencies, add `pip-audit` | **done** | `sympy<2`, `PySide6<7`, `pip-audit --strict` in the `checks` job |
| **TEST-01** Regression tests | **done** | `tests/test_regressions.py`, 45 tests, each failed before its fix |
| **TEST-02** Coverage gate | **done** | 95% library / 88% total, gated on one CI leg |
| **REL-05** `SECURITY.md`, `CONTRIBUTING.md`, `CITATION.cff` | **done** | all three present |

Suite after the above: **3221 passed, 19 skipped, 0 failed** — the same 19
capability skips as before the work, `ruff` and `mypy` clean, selftest 11/11.

One regression was introduced and caught during this work: tightening Radau's
Newton target without lengthening its iteration budget turned a converging step
into a reported failure, which silently disabled Radau's local-error test (20
skips instead of 19). Fixed by `newton_iteration_budget`, and pinned by
`test_the_newton_budget_grows_with_the_tightened_target`.

### Correction — PERF-01 is withdrawn

**The audit's startup finding was wrong and the error was mine.** [E-1] reported
14–17 s to a usable window and ~21 s of eager imports; those measurements were
taken while a parallel `pytest -n auto` run was saturating all 14 cores. On an
idle machine the window is up in **1.44 s** with **3.5 s** of total process time,
and the imports the item was about cost 0.29–0.40 s each rather than 3.6–7.0 s.
The cause was confirmed by reproducing the original numbers under a deliberate
CPU load (sympy 7.19 s against 7.02 s reported), not merely inferred.

**PERF-01 is therefore withdrawn** — not a defect — and **UX-01 drops to P3**.
[H-2] was re-checked at the same time and survives: explicit-on-stiff really does
take ~17 s to fail on an idle machine, against the 19–23 s reported.

Every wall-clock number in this audit should be read as an upper bound unless it
says the machine was idle. Step counts, error magnitudes and convergence orders
are unaffected — they do not depend on load.

### M2 in progress — the honesty items are done

| Item | State | Evidence |
|---|---|---|
| **ARCH-01** Structured diagnosis | **done** | `Solution.diagnosis`; kinds deliberately no finer than the loop can tell |
| **DYN-04** Caveat non-hyperbolic classifications | **done** | `FixedPoint.hyperbolic`; the Phase Portrait no longer prints "centre" unqualified |
| **DYN-05** Warn about missed event crossings | **done** | midpoint probe; `Solution.incomplete_events`, `events_complete` |
| **NUM-06** Warn when uniqueness is not guaranteed | **done** | `analysis.uniqueness_warning`; four orders of magnitude of margin |
| **SYM-01** Interval of validity | **done** | `symbolic.interval_of_validity`; declines rather than guessing |
| **NUM-05** Report a tolerance shortfall | **deferred** | its premise was Radau's 54× shortfall, which NUM-02 fixed. Worth having as a general mechanism; no longer urgent, and calibrating it without false alarms is the bulk of the work |
| **PERF-02** Stop grinding on a stiff problem | **done, redesigned** | 17–33 s → **0.23–0.33 s**; the Method Race test 15 s → 0.54 s |
| **REL-03** Write "when each method fails" | **done** | `docs/limits.md`; every name in `METHODS` covered, quoted messages checked against the real ones, `mkdocs build --strict` green |
| **REL-02** Test the platforms advertised | **done** | 8 CI legs; macOS + 3.11 + 3.13 added; a test compares the matrix to the classifiers |
| **TEST-04** Cover the worker and the runner | **done** | `dsolve_worker` 58% → **85%**, `solver.py` 79% → **95%** |
| **UX-02** Save and restore the session | **done** | `session.py`, `--session FILE`, auto-save on close; a hostile session file is re-parsed through `reject_unsafe_syntax` |
| **SEC-03** Document the privacy position | **done** | README "Privacy"; a test asserts no network imports anywhere in `src/` |

Three of these needed their design changed by measurement rather than reasoning:

* **PERF-02** was specified as a *stiffness detector* — "track the ratio of
  accepted to attempted steps and the step size against the interval". Two of
  those three signals turned out to be useless. Rejections are near zero on a
  stiff explicit run (4 in 500 000 on Robertson): the tiny steps are all
  *accepted*. And neither coverage nor step-size growth can separate a doomed
  explicit run from a stiff solver mid-transient — RODAS4 on Robertson at
  `rtol=1e-12` has covered 0.0000% after 5000 steps, exactly like DOPRI5, and
  then finishes. The first version aborted **eleven** solves that would have
  succeeded. What shipped is a *projection*, restricted to methods whose step
  size is already as large as it will get, and it claims nothing about
  stiffness.


* **SYM-01** was specified against `sympy.singularities`. That function **did not
  return within ten minutes** on `1/(1-t)`, against a twelve-second budget for
  the whole symbolic route. The shipped version works from the denominator and
  answers in under 2 ms — and, importantly, *declines* on `tan(t)`, where a
  denominator-only reading would have claimed "valid everywhere".
* **NUM-06**'s threshold could not be a magnitude. Van der Pol at μ=1000 has
  ∂f/∂y ≈ 3e3 and Robertson ≈ 3e5, both perfectly well defined. The test is
  *growth* under refinement, which separates them from `y^(1/3)` by four orders
  of magnitude.

### M3 in progress (updated 2026-09-23)

| Item | State | Evidence |
|---|---|---|
| **PED-04** FitzHugh–Nagumo and SIR in the catalogue | **done** | Hopf window *derived* from trace J = 0 → `I ∈ (0.331281, 1.418719)`, matching the measured onset (1.5e-2 at I=0.30 vs 3.75 at I=0.33) and collapse (3.75 at 1.42 vs 3.4e-5 at 1.50); SIR conserves S+I+R to 1.5e-12 |
| **DYN-03** Lyapunov exponent with an honest error bar | **done** | Lorenz **+0.9001 ± 0.0117** against literature 0.9056; damped pendulum −0.1497; Lotka–Volterra "indistinguishable from zero" |
| **DYN-01** continuation / bifurcation | **done** | `bb0b8eb` |
| **DYN-02** limit cycles / Poincaré | **done** | `bb0b8eb` |
| **PED-02** figures for the 17 lessons without | **done** | all 35 lessons have one; `test_lessons.py` asserts it over the course |
| **A11Y-02** text alternative and data table | **done** | `describe.py`; Plot / In words / Data tabs |
| **UX-04** predictability horizon | **done** | Lorenz at rtol 1e-8: horizon ≈ 20–23 from a 15-unit, ~3 s background estimate; none at ρ = 15 |
| **PED-08** flag a discontinuous RHS | **done** | `analysis.rough_spots`: sign, kink and switch located at 1e-6 and 1e-9; every catalogue problem clean; silent at 1e-3, and says why |
| **PED-07** name Lipschitz and Picard–Lindelöf | **done** | aside in `slopefields` |
| **TEST-03** property-based tests | **done, redesigned** | property 4 is invisible through `solve`; fixed-step with exact Jacobians it fails `66e7491` (2.6e-10 against a 1e-11 bound) |
| **A11Y-03** separatrices by pattern | **done** | stable solid, unstable dash-dot (nullclines own the dash) |
| PED-01, SYM-02/03/04, A11Y-01 | open | |

**DYN-03's error bar is the part worth reading.** The obvious one is wrong by a
factor of 8.5, and the measurement that shows it is in the docstring: over 12
replicates the estimates scatter with sd 0.0281 while the naive iid formula
reports 0.2404, because consecutive log growths are anti-correlated. A 26%
"relative standard error" would have refused a perfectly good answer. Two audit
assumptions died here too — "a short run must say not-converged" is false (a
15-time-unit Lorenz run gives 0.9197 ± 0.0438, which is fine), and the case the
guard actually exists for is a *conservative* system, where the exponent
genuinely is zero and "chaotic" would be confidently wrong about Lotka–Volterra.

### M4 removals — done

| Item | State | Evidence |
|---|---|---|
| **ARCH-02** Correct the `state.py` layering docstring | **done** | rewritten to describe the boundary that exists: ownership, not imports |
| **ARCH-03** Delete `radaudense` from the registry | **done** | 21 → 19 method names; `tests/test_radau.py` constructs the oracle directly |
| **UX-06** Remove the bare `taylor` alias | **done** | it silently meant `taylor20` |
| **DYN-06** Remove the unused resolution knobs | **done** | three parameters → named constants; `slope_field` keeps its, which *is* used |
| **ARCH-04** Stale artefacts and the `slow` marker | **withdrawn** | the marker claim was false — 24 tests carry it and `-m "not slow"` deselects 80. See the item. |
| **ARCH-05** Collapse the five job runners | open | M-effort refactor across five screens |

`DYN-06` nearly went wrong: a line-oriented grep reported all four knobs unused,
because three of the call sites pass `resolution=` on a continuation line. An
`ast` walk of the call graph found `slope_field`'s is used at three sites. The
removal was then applied by `perl` and landed on the wrong call — `streamlines`
got the nullcline constant and `nullclines` was left referencing a name that no
longer existed. Both caught by reading the result rather than trusting the edit.

**Next: REL-02** (macOS and Python 3.11/3.13 in CI), then TEST-04, UX-02, SEC-03.

Writing `docs/limits.md` was worth doing *after* the fixes rather than before:
most of its numbers are the ones this work measured, and three of its entries
record limits that were removed in the course of it. A page written first would
have documented the defects instead.

---

Ranked within each severity by **user impact ÷ effort**.

Legend — Severity: `P0` blocker · `P1` high · `P2` medium · `P3` polish.
Effort: `S` <2h · `M` <1d · `L` <1w · `XL` >1w.

---

## Summary table

### P0 — nothing ships until these close (1)

| ID | Title | Effort | Category |
|---|---|---|---|
| **SEC-01** | Validate the expression AST before sympy compiles it | M | Security |

### P1 — high (8)   *(PERF-01 withdrawn — see the correction above)*

| ID | Title | Effort | Category |
|---|---|---|---|
| NUM-01 | Stop `Jet` recursing into an interpreter crash | S | Numerics |
| PED-01 | Write Unit 8 — nonlinear systems and phenomena | XL | Pedagogy |
| DYN-01 | Add a parameter-continuation / bifurcation-diagram tool | L | Nonlinear |
| TEST-01 | Regression tests for every defect in this audit | M | Testing |
| DYN-02 | Add limit-cycle detection and a Poincaré section | L | Nonlinear |
| NUM-02 | Fix Radau's tight-tolerance shortfall | S | Numerics |
| NUM-03 | Fix RODAS4's first-order floor on non-autonomous problems | M | Numerics |
| DYN-03 | Add Lyapunov-exponent estimation with an honest error bar | M | Nonlinear |

### P2 — medium (29)   *(UX-01 moved to P3)*

| ID | Title | Effort | Category |
|---|---|---|---|
| NUM-04 | Fail a fixed-step method immediately when it goes non-finite | S | Numerics |
| SEC-02 | Pin dependencies and add `pip-audit` to CI | S | Security |
| SYM-04 | Cut the classifier's dependence on sympy hint strings | M | Symbolic |
| TEST-02 | Add a coverage gate to CI | S | Testing |
| NUM-05 | Report a tolerance shortfall instead of claiming success | M | Numerics |
| DYN-04 | Caveat non-hyperbolic classifications at the UI | S | Nonlinear |
| NUM-06 | Warn when uniqueness is not guaranteed | M | Numerics |
| SYM-01 | Report the interval of validity with every symbolic solution | M | Symbolic |
| PED-02 | Add figures to the 17 lessons that have none | L | Pedagogy |

| DYN-05 | Detect and warn about missed event crossings | M | Nonlinear |
| PERF-02 | Detect stiffness and bail out in <1 s instead of 20 s | M | Performance |
| SYM-02 | Add reduction of order | M | Symbolic |
| A11Y-01 | Give every interactive control an accessible name | M | Accessibility |
| A11Y-02 | Give every plot a text alternative and a data table | L | Accessibility |
| REL-02 | Test the platforms actually advertised | S | Release |
| TEST-03 | Add property-based tests | M | Testing |
| UX-02 | Save and restore the full session | M | UX |
| REL-03 | Write "when each method fails" | M | Docs |
| PED-03 | Add a spaced-review queue driven by existing progress data | M | Pedagogy |
| NUM-07 | Expose `∂f/∂t` on `ODEProblem` | S | Numerics |
| TEST-04 | Cover `dsolve_worker.py` and `solver.py` | M | Testing |
| REL-04 | Add a local diagnostics log and a "copy diagnostics" action | M | Release |
| PED-04 | Add FitzHugh–Nagumo and promote SIR to the catalogue | S | Pedagogy |
| SYM-03 | Present implicit solutions as implicit | S | Symbolic |
| UX-03 | Surface `as_code()` as a visible "copy reproducing code" button | S | UX |
| PED-05 | Teach why the numerical answer to `y'=y^{1/3}` is not the whole story | S | Pedagogy |
| ARCH-01 | Make `Solution` carry a structured diagnosis, not just a string | M | Architecture |
| UX-04 | Show the predictability horizon on chaotic systems | M | UX |
| PED-06 | Add a "when this method fails" note to every method lesson | M | Pedagogy |

### P3 — polish (18)

| ID | Title | Effort | Category |
|---|---|---|---|
| SEC-03 | Document the privacy position in the README | S | Security |
| UX-01 | Add a splash screen while the window builds | S | UX |
| ARCH-02 | Correct the `state.py` layering docstring | S | Architecture |
| PERF-03 | Hoist the ERK stage buffer out of the step loop | S | Performance |
| NUM-08 | Wrap exceptions raised by the user's RHS at `t0` | S | Numerics |
| A11Y-03 | Distinguish separatrices by dash pattern as well as colour | S | Accessibility |
| PED-07 | Name Lipschitz and Picard–Lindelöf | S | Pedagogy |
| REL-05 | Add `SECURITY.md`, `CONTRIBUTING.md`, `CITATION.cff` | S | Docs |
| TEST-05 | Add a performance regression gate | M | Testing |
| UX-05 | Throttle replots to one per frame | S | UX |
| PED-08 | Flag a discontinuous RHS from the rejection pattern | M | Pedagogy |
| ARCH-03 | Delete `radaudense` from the user-facing method list | S | Architecture |
| A11Y-04 | Make rendered maths follow the OS text scale | M | Accessibility |
| REL-06 | Publish the docs | S | Release |
| ARCH-04 | Remove the stale `dist/` artefacts and the unused `slow` marker | S | Architecture |
| UX-06 | Remove the duplicate `taylor` alias from the method registry | S | UX |
| ARCH-05 | Collapse the three near-identical `_ThumbJob`/`_StudyJob`/`_AnalysisJob` runners | M | Architecture |
| DYN-06 | Remove the unused `streamlines` resolution knob and fix its default | S | Nonlinear |

**Category counts against the brief's minimums:**

| Category | Required | Delivered | IDs |
|---|---:|---:|---|
| Numerical correctness & solver quality | 8 | **8** | NUM-01…08 |
| Nonlinear / dynamical-systems tooling | 6 | **6** | DYN-01…06 |
| Symbolic & analytical layer | 4 | **4** | SYM-01…04 |
| Pedagogy & content | 8 | **8** | PED-01…08 |
| UX & interaction | 6 | **6** | UX-01…06 |
| Accessibility | 4 | **4** | A11Y-01…04 |
| Architecture & code quality | 5 | **5** | ARCH-01…05 |
| Performance | 3 | **3** | PERF-01…03 |
| Testing & CI | 5 | **5** | TEST-01…05 |
| Security & privacy | 3 | **3** | SEC-01…03 |
| Release ops, docs & licensing | 4 | **5** | REL-02…06 |
| **Total** | **56** | **57** | |

**Removals / simplifications (6):** ARCH-03 (delete `radaudense` from the public
registry), ARCH-04 (delete stale artefacts and the unused marker), ARCH-05
(collapse five job runners into one), UX-06 (remove the `taylor` alias), DYN-06
(remove three unused resolution parameters), SYM-04 (remove the dependence on
sympy's internal hint names).

**Honesty items (7)** — places the app currently overstates the reliability of a
result: NUM-02 (Radau's silent 54× shortfall), NUM-05 (report a shortfall instead
of claiming success), NUM-06 (warn when uniqueness is not guaranteed), DYN-04
(caveat non-hyperbolic classifications), DYN-05 (warn about missed event
crossings), SYM-01 (state the interval of validity), UX-04 (show the
predictability horizon).

---

# Items

## Security & privacy

### [SEC-01] Validate the expression AST before sympy compiles it

- **Severity:** P0 blocker
- **Effort:** M
- **Confidence:** high — demonstrated end to end with a canary file through both shipping entry points, and the fix was prototyped and measured against 23 cases.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 11; `01-FINDINGS.md` [J-1]. `src/odesuite_app/custom.py:41-72` (`ALLOWED_FUNCTIONS`, `_SAFE_GLOBALS`), `src/odesuite_app/symbolic.py:208-221` (`_parse_side`).
- **Problem:** `sin` is on the function whitelist, so `sin.__class__.__init__.__globals__["__builtins__"]` reaches the real builtins (157 names, `__import__` present). Writing a canary file succeeded. Reachable from `custom.build` (Solver Lab → type your own system) and from `symbolic.parse_equation` (equation editor) — in the latter the payload executed and its return value silently became the equation's right-hand side. The existing `__builtins__ = {}` defence is correct but closes only name lookup, not attribute traversal.
- **Proposed change:** add `custom.validate_expression(text, names)` that `ast.parse(text, mode="eval")`s and walks the tree *before* handing anything to sympy. Reject `ast.Attribute` and `ast.Subscript` outright; permit only `Expression, Constant, Name, Load, Call, BinOp, UnaryOp, Tuple` plus `Add, Sub, Mult, Div, Pow, Mod, USub, UAdd, BitXor`; require every `Name.id` to be a declared variable, a declared parameter, or a key of `ALLOWED_FUNCTIONS`; require every `Call.func` to be a bare `Name`; reject `keywords` and `Starred`. Call it from `custom.build` and from `symbolic._parse_side`. On the `symbolic` path run it on the text *after* `_rewrite_derivatives`, with the derivative tokens added to the permitted names.
- **Acceptance criteria:** a new `tests/test_security.py` asserts (a) each of these raises `ParseError` through both `custom.build` and `symbolic.parse_equation`: `sin.__class__.__init__.__globals__["__builtins__"]["open"]("x","w")`, `().__class__.__base__.__subclasses__()`, `(1).__class__.__mro__[1].__subclasses__()`, `sin(t).__reduce__()`, `Symbol.__subclasshook__`, `sin.__globals__`, `__import__("os")`, `eval("1+1")`, `[x for x in ().__class__.__mro__]`; (b) a canary path does not exist after each attempt; (c) all 14 legitimate forms still parse: `-2*y`, `y*cos(t)`, `mu*(1-x**2)*v - x`, `sigma*(y-x)`, `r*y*(1-y/K)`, `sec(t)`, `exp(-t)*sin(3*t)`, `sqrt(Abs(y))`, `-(g/L)*sin(theta) - c*omega`, `a*x - b*x*y`, `3*t^2 + 1`, `Max(0, y)`, `atan2(y, x)`, `1/(1+t**2)`; (d) the full existing suite still passes.
- **Dependencies / risks:** none blocking. Risk: over-restriction breaking a legitimate equation shape the catalogue uses — mitigated by (c), which should be extended with every `EXAMPLES` entry in `custom.py` and `symbolic.py`.

### [SEC-02] Pin dependencies and add `pip-audit` to CI

- **Severity:** P2
- **Effort:** S
- **Confidence:** high — `pyproject.toml:44` is a floors-only declaration and no lockfile exists in the tree.
- **Evidence:** `01-FINDINGS.md` [J-2], [L-1]. `pyproject.toml:44`, `pyproject.toml:46-58`.
- **Problem:** `numpy>=1.24`, `scipy>=1.10`, `PySide6>=6.6`, `sympy>=1.12` with no upper bounds and no lock. The build is not reproducible, and nothing would notice a CVE. This compounds [REL-01]: the app depends on sympy's *internal hint names*, so an unpinned sympy can change what the app teaches.
- **Proposed change:** commit a `requirements-dev.lock` produced by `pip freeze` from a clean install, and have CI's `tests` job install from it in one matrix leg (keeping one unpinned leg to catch upstream breakage early). Add upper bounds for the two dependencies with behavioural coupling: `sympy>=1.12,<2` and `PySide6>=6.6,<7`. Add a `pip-audit` step to the `checks` job.
- **Acceptance criteria:** CI has a job that installs from the lockfile and passes; `pip-audit` runs and fails the build on a HIGH/CRITICAL advisory; `python -m build` output is byte-identical across two runs on the same machine.
- **Dependencies / risks:** the unpinned leg will occasionally break on upstream releases — that is the point, but mark it `continue-on-error: false` only after one quiet cycle.

### [SEC-03] Document the privacy position in the README

- **Severity:** P3
- **Effort:** S
- **Confidence:** high — verified by search: no `requests`/`urllib`/`socket`/`http` anywhere in `src/`, no telemetry, no analytics.
- **Evidence:** `01-FINDINGS.md` [J-3]. `src/odesuite_app/progress.py:1-40`.
- **Problem:** the app makes no network calls, collects nothing, and writes exactly one file (`progress.json`: lesson answers, per-user config dir, atomic write, corruption-tolerant, in-app delete). That is a strong position and no user-facing document states it, so a cautious user or an institution has to read the source to find out.
- **Proposed change:** a short "Privacy" section in `README.md`: what is stored, where, how to delete it, and an explicit statement that there is no telemetry and no network access. Add the same as a paragraph in `SECURITY.md` (see REL-05).
- **Acceptance criteria:** README states the storage location, the file's contents, the deletion route, and the no-network/no-telemetry commitment. A test asserts no `import requests|urllib|socket|http.client` appears under `src/`.
- **Dependencies / risks:** the test becomes a constraint on future features; that is intentional.

---

## Numerical correctness & solver quality

### [NUM-01] Stop `Jet` recursing into an interpreter crash

- **Severity:** P1
- **Effort:** S
- **Confidence:** high — reproduced deterministically; exit 127 with no traceback.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 1 sidebar; `01-FINDINGS.md` [A-1]. `src/odesuite/steppers/taylor.py:53` (`__array_priority__ = 1000.0`), `taylor.py:97` (`__rmul__ = __mul__`), `taylor.py:66-77` (`__mul__`).
- **Problem:** `solve(ODEProblem(lambda t,y: y*np.cos(t), (0,5), [1.0]), "taylor20")` kills the interpreter — no Python exception, no traceback. `__array_priority__` makes numpy defer `ndarray.__mul__` to `Jet.__rmul__`, whose non-`Jet` branch does `Jet(self.c * float(other))`; with an object-dtype array on the other side this recurses until the C stack is exhausted. `y' = y·cos(t)` is an entirely ordinary non-autonomous RHS. Not reachable from the GUI (all 18 `supports_taylor` catalogue entries verified working), but `odesuite` ships as a standalone library that advertises the Taylor family.
- **Proposed change:** in `Jet.__mul__`, `__add__`, `__sub__`, `__truediv__`, `__pow__` and their reflected forms, return `NotImplemented` when `other` is an `np.ndarray` of `dtype == object`, so numpy falls back to elementwise dispatch and each element multiplies as `Jet * Jet`. Add a guard in `Jet._lift` that raises `TypeError(f"cannot combine a Jet with {type(other).__name__}; a jet-arithmetic right-hand side must operate componentwise")` for anything that is neither a `Jet` nor a real scalar.
- **Acceptance criteria:** `tests/test_taylor.py` gains a test that `solve(problem, "taylor20")` on `y' = y*np.cos(t)` **either** integrates correctly to `exp(sin t)` within `1e-10` **or** raises `TypeError` with a message naming jet arithmetic — and in no case terminates the process. A second test asserts `np.empty(1, dtype=object) * Jet(...)` and `Jet(...) * np.empty(1, dtype=object)` both behave identically.
- **Dependencies / risks:** `__array_priority__` exists so `array * jet` reaches `Jet`; returning `NotImplemented` for object arrays only must not disturb the float-array path, which the existing Taylor tests cover.

### [NUM-02] Fix Radau's tight-tolerance shortfall

- **Severity:** P1
- **Effort:** S
- **Confidence:** high — cause isolated by varying one constant; 54.5× → 0.8× at `rtol=1e-12`.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 2; `01-FINDINGS.md` [A-3]. `src/odesuite/steppers/irk.py` (`NewtonSettings(max_iter=8, tol_factor=0.03, max_rate=1.0)`), `src/odesuite/newton.py` (`tol_factor` semantics).
- **Problem:** below `rtol=1e-9` Radau's achieved error stops tracking the request: 15.1× / 29.6× / 54.5× / 103.1× at `1e-10 … 1e-13`, while DOPRI5 holds 1.55–2.04× over the same range. The stage solve terminates at 3% of the integration tolerance, which is negligible at loose tolerances and dominant at tight ones. The Accuracy Lab drives `rtol` down to `1e-13` (`screens/accuracy.py:81`).
- **Proposed change:** make the Newton termination scale with the tolerance rather than being a fixed fraction of it. Replace the constant with `tol_factor = min(0.03, 0.3 * rtol**0.25)` computed in `RadauIIA.set_tolerances`, or simply lower the default to `0.003` (measured: 0.8× at `1e-12`, 1.8× at `1e-13`) and note the extra iterations in the docstring. Prefer the scaled form so loose-tolerance work is unaffected.
- **Acceptance criteria:** a test sweeps `rtol` from `1e-6` to `1e-12` on `y' = -2y` with `radau` and asserts `achieved/requested <= 5` at every point (currently 54.5 at `1e-12`). A second asserts `nfev` at `rtol=1e-6` grows by no more than 15% against the current value, so loose-tolerance efficiency is not traded away.
- **Dependencies / risks:** more Newton iterations per step at tight tolerance; the predictive controller may need its `freeze_below` revisited. Run `benchmarks/work_precision.py` before and after.

### [NUM-03] Fix RODAS4's first-order floor on non-autonomous problems

- **Severity:** P1
- **Effort:** M
- **Confidence:** high — order collapse reproduced across eight step sizes; cause isolated by showing an analytic Jacobian changes nothing while an autonomous problem removes the floor entirely.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 1b; `01-FINDINGS.md` [A-2]. `src/odesuite/steppers/rosenbrock.py` (`_time_derivative`).
- **Problem:** on `y' = y·cos t`, RODAS4 holds order 4 to `2.8e-11` then collapses to order 0.98 and floors at `3.9e-13`; on the autonomous `y'=-2y` it holds order 4 to `1.9e-14`. `_time_derivative` differences `∂f/∂t` with `dt = sqrt(EPS)·max(|t|,1)`; its `O(√ε)` error enters as `h·d_i·f_t`, an `O(h·√ε)` first-order term. A user asking for `rtol=1e-12` on any non-autonomous problem cannot get it and is not told.
- **Proposed change:** two parts. (1) Use a central difference, `(f(t+dt,y) - f(t-dt,y)) / (2 dt)` with `dt = EPS**(1/3) * max(|t|,1)`, which is `O(dt²) = O(ε^{2/3}) ≈ 4e-11` instead of `O(√ε) ≈ 1.5e-8` — one extra RHS evaluation per step. (2) Land NUM-07 so an exact `∂f/∂t` can be supplied and this path skipped entirely.
- **Acceptance criteria:** a convergence test on `y' = y cos t` with `rodas4` asserts observed order ≥ 3.85 at the finest step pair above `1e-13` (currently 0.98), and that the achieved error at `n=8192` is below `1e-13` (currently `7.7e-13`).
- **Dependencies / risks:** one extra RHS evaluation per step, ~10% more `nfev` on cheap problems. Benchmark against `benchmarks/work_precision.py` and state the trade in the docstring. Enables NUM-07.

### [NUM-04] Fail a fixed-step method immediately when it goes non-finite

- **Severity:** P2
- **Effort:** S
- **Confidence:** high — 909,393 no-op rejections measured, cause read directly from the code path.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 4b; `01-FINDINGS.md` [A-4]. `src/odesuite/driver.py` (non-finite branch setting `planner.h_abs = h_abs * 0.5`), `src/odesuite/_loop.py` (`StepPlanner.plan` fixed branch ignoring `h_abs`).
- **Problem:** Euler on the harmonic oscillator overflows after 90,607 steps, then retries the identical failing step **909,393 times** over **13.7 s** before reporting `exceeded max_steps=1000000` — the wrong reason, when the driver already set `nonfinite_at` and `underflow_message` exists to report the right one. A fixed-step method cannot shrink its step, so the halving is structurally a no-op.
- **Proposed change:** in `driver.solve`'s non-finite branch, test `planner.fixed`; if so, break immediately with `status="failed"` and a message built from `nonfinite_at` — e.g. *"the solution became non-finite at t=…; {name} runs at a fixed step size and cannot reduce h. Reduce first_step/increase n_steps, or use an adaptive or A-stable method."* Apply the same to the `not result.ok` branch.
- **Acceptance criteria:** `solve(harmonic, "euler", n_steps=500_000)` returns in under 2 s (currently 13.7 s) with `status="failed"`, `stats.nrejected <= 1`, and a message containing both the time of the overflow and the words "fixed step".
- **Dependencies / risks:** none. Small behavioural change to `nrejected` for fixed-step failures; no test currently asserts the old value.

### [NUM-05] Report a tolerance shortfall instead of claiming success

- **Severity:** P2 · **honesty**
- **Effort:** M
- **Confidence:** medium — the mechanism is clear, but choosing a shortfall criterion that does not cry wolf needs calibration against the benchmark suite.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 2; `01-FINDINGS.md` [A-3]. `src/odesuite/solution.py:81-92` (`success`), `src/odesuite/driver.py` (error-norm loop).
- **Problem:** Radau at `rtol=1e-12` delivers `5.4e-11` and reports `success=True` with no qualification. More generally the library has no way to say "I finished, but I do not believe I met your tolerance." A learner comparing methods in the Accuracy Lab is shown a number the solver privately cannot stand behind.
- **Proposed change:** accumulate the local error norms already computed in `driver.solve` and attach a summary to `Stats`: `err_max` (worst accepted `err`) and `err_mean`. Add `Solution.tolerance_met: bool` set False when the accepted-step error norm exceeded 1.0 on more than a small fraction of steps, or when a stepper reports a saturating estimate. Surface it in `Solution.__repr__` and in `widgets/stats.py`.
- **Acceptance criteria:** `solve(decay, "radau", rtol=1e-12)` returns `tolerance_met=False` while `solve(decay, "dopri5", rtol=1e-12)` returns `True`; no benchmark in `NONSTIFF` or `STIFF` reports `False` at `rtol=1e-6` (the no-false-alarm check).
- **Dependencies / risks:** best landed *after* NUM-02 and NUM-03, so the flag reports genuine limits rather than defects being fixed anyway.

### [NUM-06] Warn when uniqueness is not guaranteed

- **Severity:** P2 · **honesty**
- **Effort:** M
- **Confidence:** medium — the detection is a heuristic; the pedagogical case for it is strong and specific.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 6; `01-FINDINGS.md` [A-5]. `src/odesuite_app/lessons/unit1_first_order.py`, lesson `slopefields`, `pitfall` note on `y'=y^{1/3}`.
- **Problem:** `y' = y^{1/3}, y(0)=0` returns `y ≡ 0`, `status="finished"`, `success=True`, silently — while this application's own lesson teaches that this exact equation has two solutions through the origin. The course says "uniqueness fails here"; the tool then shows one answer with no caveat.
- **Proposed change:** in `odesuite_app` (not the library — this is a teaching affordance), add `analysis.uniqueness_warning(problem)`: estimate `∂f/∂y` at `(t0, y0)` by finite differences at three decreasing offsets; if the magnitude grows without bound as the offset shrinks, return a warning string naming the Picard–Lindelöf hypothesis that fails. Display it as a banner in the Solver Lab and Phase Portrait, linking to the `slopefields` lesson.
- **Acceptance criteria:** `y' = y^{1/3}, y(0)=0` produces a warning; `y' = -2y`, `y' = y*cos(t)`, and every `NONSTIFF` benchmark produce none. A test asserts both directions.
- **Dependencies / risks:** false positives on a genuinely stiff-but-Lipschitz problem; keep the threshold conservative and word the banner as "uniqueness is not guaranteed here", never "there are two solutions".

### [NUM-07] Expose `∂f/∂t` on `ODEProblem`

- **Severity:** P2
- **Effort:** S
- **Confidence:** high — the gap is structural and visible in the signature.
- **Evidence:** `01-FINDINGS.md` [A-2]. `src/odesuite/problem.py:47-72` (constructor accepts `jac`, `jac_sparsity`, `mass`, but no `dfdt`), `src/odesuite/steppers/rosenbrock.py` (`_time_derivative`).
- **Problem:** Rosenbrock methods need `∂f/∂t` and there is no way to supply it, so the differenced approximation and its accuracy floor (NUM-03) are unavoidable. Users who *can* supply it — every catalogue problem, and every equation typed into the app, since `custom.py` already differentiates symbolically — are forced through the approximation.
- **Proposed change:** add `dfdt=None` to `ODEProblem.__init__`, validated like `jac` (callable or constant, shape-checked against `y0`), with `has_dfdt` and a `dfdt(t, y)` accessor. Have `Rosenbrock._time_derivative` use it when present. Populate it in `custom.build` (sympy already has the expression, so `sp.diff(rhs, t)` is free) and in the catalogue problems that have a closed form.
- **Acceptance criteria:** `rodas4` on `y' = y cos t` with an analytic `dfdt` holds order ≥ 3.9 down to `1e-13`; `ODEProblem(..., dfdt=<wrong shape>)` raises at construction with a message naming the expected shape.
- **Dependencies / risks:** public API addition — keyword-only with a default, so no caller breaks. Pairs with NUM-03.

### [NUM-08] Wrap exceptions raised by the user's RHS at `t0`

- **Severity:** P3
- **Effort:** S
- **Confidence:** high — reproduced; the module's own comment states the intent that is half-met.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 6; `01-FINDINGS.md` [A-6]. `src/odesuite/problem.py:95-110`.
- **Problem:** `problem.py:95-110` explains at length that its guard exists so an equation started at its own singularity does not surface as *"a bare ZeroDivisionError … naming nothing the caller had written."* The check is `np.all(np.isfinite(f0))`, which catches a numpy `inf` but not a Python exception thrown inside the callable. `ODEProblem(lambda t,y: np.array([1.0/t]), (0.0,1.0), [0.0])` raises exactly that bare `ZeroDivisionError`.
- **Proposed change:** wrap the initial `self.f(t0, y0)` probe in `try/except Exception as exc` and re-raise as `ValueError(f"the right-hand side raised {type(exc).__name__} at t0={t0:g}: {exc}. The problem may be singular there — try starting from a different t0.") from exc`.
- **Acceptance criteria:** the `y'=1/t` construction raises `ValueError` whose message contains `t0=0` and `ZeroDivisionError`; the existing non-finite test still passes unchanged.
- **Dependencies / risks:** none. Do not wrap RHS calls inside the step loop — an exception mid-solve should still propagate.

---

## Nonlinear / dynamical-systems tooling

### [DYN-01] Add a parameter-continuation / bifurcation-diagram tool

- **Severity:** P1
- **Effort:** L
- **Confidence:** high — the gap is verified absent, and every primitive it needs is present and correct.
- **Evidence:** `01-FINDINGS.md` [C-1]. `src/odesuite_app/analysis.py:265` (`find_fixed_points`), `:216` (`jacobian_at`), `:226` (`classify`). `catalog.py:172-173,213` already name Hopf and pitchfork bifurcations in slider hints.
- **Problem:** the app names bifurcations in tooltips and ships Duffing (pitchfork in α), Brusselator (Hopf at `b = 1+a²`) and `harvested_population` (saddle-node at `H = rK/4`) — with no way to see one. This is the largest capability gap in the half of the app the project calls its differentiator.
- **Proposed change:** new `odesuite_app/continuation.py`: `sweep(entry, param, lo, hi, steps)` walking the parameter and, at each value, seeding `find_fixed_points` from the previous value's solutions (pseudo-arclength is not needed for a first version; natural parameter continuation with previous-point seeding is). Return branches tagged stable/unstable from `classify`. New screen or a Phase Portrait tab plotting equilibrium coordinate against parameter, solid for stable, dashed for unstable.
- **Acceptance criteria:** for `x' = mu - x^2` the diagram shows two branches meeting at `mu=0` with the upper stable and the lower unstable; for Brusselator the stable equilibrium loses stability within 1% of `b = 1 + a²`; for Duffing the pitchfork appears at `α = 0`. A headless test asserts each of those three numbers.
- **Dependencies / risks:** naive re-solving misses folds; the acceptance criteria above are all non-degenerate. Document the limitation and file pseudo-arclength as follow-up. Best after PED-01 so the teaching and the tool land together.

### [DYN-02] Add limit-cycle detection and a Poincaré section

- **Severity:** P1
- **Effort:** L
- **Confidence:** high — absent, and the event machinery needed is already machine-precision accurate.
- **Evidence:** `01-FINDINGS.md` [C-1]; `02-EXPERIMENTS.md` Experiment 8 (event times exact to 5.55e-17).
- **Problem:** the catalogue ships Van der Pol, Brusselator and Duffing and describes their limit cycles in prose, with no way to find one, measure its period, or take a section. Poincaré–Bendixson is the central theorem of planar nonlinear dynamics and the app has no expression of it.
- **Proposed change:** in `analysis.py`, `poincare_section(problem, point, normal, span)` built on `odesuite.Event` with a direction filter — the event machinery already returns crossing times to machine precision. `limit_cycle(problem, seed)`: integrate long enough to shed the transient, take successive section crossings, and report convergence of the return map plus the period. Draw the section and the cycle in the Phase Portrait; show the return-map points.
- **Acceptance criteria:** Van der Pol at μ=1 reports a period within 0.1% of 6.6633; Brusselator at `a=1, b=3` reports a closed orbit; the damped pendulum reports none. Tests assert all three.
- **Dependencies / risks:** transient-shedding heuristics can mislead on a slowly-converging spiral — require the return map to contract over at least five crossings before declaring a cycle.

### [DYN-03] Add Lyapunov-exponent estimation with an honest error bar

- **Severity:** P1 · touches honesty
- **Effort:** M
- **Confidence:** high — absent; my own crude estimate (0.837 vs 0.906 literature) shows both that it is straightforward and that it needs an error bar.
- **Evidence:** `01-FINDINGS.md` [C-1]; `02-EXPERIMENTS.md` Experiment 9.
- **Problem:** Lorenz ships tagged `chaotic` with no way to quantify the chaos. Worse, without an exponent the app cannot compute the predictability horizon it ought to be displaying (see UX-04).
- **Proposed change:** `analysis.largest_lyapunov(problem, t_transient, t_total)` by the standard Benettin renormalisation: integrate a reference trajectory and a perturbed one, renormalise the separation at fixed intervals, accumulate `log` growth. Report the running estimate **and** its standard error over the second half of the run; refuse to report a value whose relative standard error exceeds 20%, returning "not converged" instead.
- **Acceptance criteria:** Lorenz at standard parameters returns `0.906 ± 0.05` over `t=1000`; the damped pendulum returns a negative exponent; a short run (`t=20`) returns "not converged" rather than a number.
- **Dependencies / risks:** cost — a 1000-time-unit Lorenz run must go through `SolveRunner` with cancellation, not block the UI. Enables UX-04.

### [DYN-04] Caveat non-hyperbolic classifications at the UI

- **Severity:** P2 · **honesty**
- **Effort:** S
- **Confidence:** high — demonstrated with an explicit counterexample.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 7 case 4; `01-FINDINGS.md` [C-2]. `src/odesuite_app/analysis.py:226-234` (`classify`, whose docstring is already scrupulous), `src/odesuite_app/screens/portrait.py:421` (renders `point.kind` verbatim).
- **Problem:** for `x' = -y + x(x²+y²)`, `y' = x + y(x²+y²)` the app labels the origin **"centre"** in bold. The linearisation does give a centre; the true flow spirals outward. Hartman–Grobman does not apply at a non-hyperbolic point and the screen does not say so. Lotka–Volterra's centre is right only because that system is conservative — the classifier cannot tell the two apart.
- **Proposed change:** add `FixedPoint.hyperbolic: bool` (no eigenvalue with real part within tolerance of zero) in `analysis.py`. In `portrait.py`, when `hyperbolic` is False, render the label as e.g. *"centre (linearisation only — higher-order terms decide)"* and attach a tooltip naming Hartman–Grobman. Apply to `centre` and `non-hyperbolic` alike.
- **Acceptance criteria:** a test asserts `hyperbolic is False` for the two systems above and `True` for the damped pendulum's spiral and the saddle-node's node; a widget test asserts the caveat text appears for the former and not the latter.
- **Dependencies / risks:** none. Cheap, and it converts a quietly-wrong label into a teaching moment.

### [DYN-05] Detect and warn about missed event crossings

- **Severity:** P2 · **honesty**
- **Effort:** M
- **Confidence:** high — measured: 7 of 63 roots found at the default setting.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 8; `01-FINDINGS.md` [C-3]. `src/odesuite/events.py` (`Event.subdivisions`, default 0).
- **Problem:** with `g = sin(20t)` over `[0,10]` the default finds **7 of 63** crossings. The docstring is candid, `subdivisions=8` finds all 63, and the app never sets it. Nothing in the returned `Solution` hints that crossings were missed — the caller sees seven event times and no reason to doubt them.
- **Proposed change:** cheap post-hoc check in `EventTracker`: track the sign of `g` at both step endpoints *and* its magnitude; if `|g|` at the midpoint of a step exceeds both endpoint magnitudes by a wide margin (a bump inside the step), or if the number of detections is small relative to the number of steps in which `g` changed sharply, set `Solution.events_may_be_incomplete = True` with a message suggesting `subdivisions`. Alternatively — and more simply — make `subdivisions` default to 2, which costs two extra `g` evaluations per step and catches the common double-crossing.
- **Acceptance criteria:** the `sin(20t)` case sets the flag at `subdivisions=0`; a single-crossing event (bouncing ball) does not. If the default is changed instead, `tests/test_events.py` asserts ≥ 60 of 63 roots at the default and measures the `nfev` cost on a single-crossing problem at under 5%.
- **Dependencies / risks:** changing the default alters event counts for existing callers — decide deliberately and record it in the changelog.

### [DYN-06] Remove the unused `streamlines` resolution knob and fix its default

- **Severity:** P3 · **removal**
- **Effort:** S
- **Confidence:** medium — the parameter is exposed but I found no caller varying it.
- **Evidence:** `src/odesuite_app/analysis.py:151` (`streamlines(..., resolution: int = 33, ...)`), `:85` (`vector_field(..., resolution: int = 33)`), `:540` (`nullclines(..., resolution: int = 140)`).
- **Problem:** three related functions take a `resolution` parameter with three different defaults (33, 33, 140) and no caller in `screens/portrait.py` passes any of them. Three magic numbers configurable in principle and fixed in practice.
- **Proposed change:** hoist the three into named module constants (`VECTOR_FIELD_RESOLUTION`, `STREAMLINE_RESOLUTION`, `NULLCLINE_RESOLUTION`) with a comment saying what each trades, and drop the parameters that no caller uses. If the Phase Portrait should offer a density control, add it deliberately as one setting rather than three unused ones.
- **Acceptance criteria:** `git grep "resolution=" -- src/odesuite_app/` returns no call sites; the constants carry comments; phase-portrait tests pass unchanged.
- **Dependencies / risks:** they are public-ish within the app package; nothing outside `odesuite_app` imports `analysis`.

---

## Symbolic & analytical layer

### [SYM-01] Report the interval of validity with every symbolic solution

- **Severity:** P2 · **honesty**
- **Effort:** M
- **Confidence:** medium — sympy can find the singularities; deciding which interval contains `t0` is the fiddly part.
- **Evidence:** `01-FINDINGS.md` [B-5]. `src/odesuite_app/symbolic.py:128` (`SymbolicSolution`, no interval field); `02-EXPERIMENTS.md` Experiment 6 (the numerical side fails honestly at `t=1` on the same equation).
- **Problem:** a learner solving `y' = y²`, `y(0)=1` is shown `y = 1/(1-t)` with nothing to say it is valid only for `t < 1`. The same app's numerical solver stops at `t=1` and says the solution "may be singular or blowing up there", and the `slopefields` lesson teaches that existence is local. Three parts of one product disagree.
- **Proposed change:** add `SymbolicSolution.interval`. Compute it with `sympy.singularities(expr, t)` (plus the denominators of the particular solution), take the maximal open interval containing `t0` that excludes them, and render it beneath the answer in `widgets/symbolicpanel.py` as e.g. *"valid on (−∞, 1)"*. Where sympy cannot decide, show nothing rather than a guess.
- **Acceptance criteria:** `y'=y², y(0)=1` reports `(-oo, 1)`; `y'=-2y, y(0)=1` reports `(-oo, oo)`; `t y' + y = 0, y(1)=1` reports `(0, oo)`. A test asserts all three.
- **Dependencies / risks:** `singularities` can return unevaluated sets for messy expressions — fall back to showing nothing, never to a wrong interval.

### [SYM-02] Add reduction of order

- **Severity:** P2
- **Effort:** M
- **Confidence:** high — verified absent repo-wide.
- **Evidence:** `01-FINDINGS.md` [B-1]. `git grep -i "reduction of order"` → zero hits. `src/odesuite_app/steps.py:82-91` (`TECHNIQUES`), `:1589` (`_BUILDERS`).
- **Problem:** the only standard second-order technique in a first course with no coverage anywhere — not in the narrator, not in the lessons, not in the docs. It is also the bridge to variation of parameters, which unit 3 teaches without it.
- **Proposed change:** add `_reduction_of_order` to `steps.py` following the shape of `_variation` — given `y'' + p y' + q y = 0` and one known solution `y₁`, substitute `y = v y₁`, reduce to a first-order equation in `v'`, integrate twice. Register in `_BUILDERS` and `TITLES`. Add a `Lesson` to `unit3_second_order.py` between `variation` and `cauchy`, with a `Template` for drill.
- **Acceptance criteria:** the narrator solves `t² y'' - 3t y' + 4y = 0` given `y₁ = t²`, producing `y = t²(c₁ + c₂ ln t)`, and every step passes its own `check_answer`. The new lesson satisfies the existing structural tests in `tests/test_lessons.py` (objectives, motivation, derivation, reference, ≥1 template, ≥4 questions).
- **Dependencies / risks:** the technique needs a known solution supplied, unlike every other entry in `_BUILDERS` — the UI must ask for it, so this is a narrator *and* a screen change.

### [SYM-03] Present implicit solutions as implicit

- **Severity:** P2
- **Effort:** S
- **Confidence:** medium — `_pick_branch` and `_signed_branch` exist, suggesting the force-solve path is already partly handled; needs a read of what reaches the panel.
- **Evidence:** `src/odesuite_app/steps.py:527` (`_pick_branch`), `:1405` (`_signed_branch`), `:1306` (`_exact_equation`). `01-FINDINGS.md` §B.
- **Problem:** exact equations and many separable ones have solutions that are naturally implicit (`F(t,y) = C`). Forcing them into `y = …` either loses branches or produces an expression with a sign ambiguity the learner is not warned about. The code has branch-selection machinery, which implies the force-solve is happening.
- **Proposed change:** have `_exact_equation` and `_separable` return the implicit relation as the primary answer when `sympy.solve` yields more than one branch or a branch containing a `sqrt` of an expression that changes sign on the domain. Render `F(t,y) = C` and offer the explicit branch as a secondary line labelled with the condition under which it holds.
- **Acceptance criteria:** `2ty + (t² + 2y) y' = 0` is presented as `t²y + y² = C`, not as a quadratic-formula branch; `y' = -t/y` with `y(0)=2` is presented as `t² + y² = 4` with the explicit branch `y = +sqrt(4-t²)` labelled "for y > 0". Tests assert the rendered form.
- **Dependencies / risks:** `check_answer` must accept both the implicit and explicit forms so a learner is not marked wrong for either — extend `tests/test_check_answer.py`.

### [SYM-04] Pin the technique classifier against sympy version drift

*(cross-listed as REL-01 in the summary table; counted once, here, under Symbolic)*

- **Severity:** P2
- **Effort:** M
- **Confidence:** high — the coupling is explicit in the source and the dependency is unbounded.
- **Evidence:** `01-FINDINGS.md` [B-4]. `src/odesuite_app/steps.py:82-91` (eight sympy hint strings), `:1589` (`_BUILDERS` keyed on them), `:1605` (`_DETECTORS`, which exists because `classify_ode` is already unreliable). `pyproject.toml:44` (`sympy>=1.12`, no ceiling).
- **Problem:** the app dispatches on sympy's internal `classify_ode` hint names — `"1st_homogeneous_coeff_best"`, `"nth_linear_constant_coeff_undetermined_coefficients"`, and six more. These carry no stability guarantee. A sympy minor release that renames or merely *reorders* a hint changes which technique the app narrates to a student, and a reordering would not necessarily fail any test.
- **Proposed change:** invert the dependency. Make `_DETECTORS` — the app's own recognisers — the primary path for all eight techniques, with `classify_ode` consulted only as a fallback for equations none of them claims. Add a test that asserts, for a fixed corpus of ~30 equations, exactly which technique is chosen, so any drift fails loudly. Cap `sympy<2` (see SEC-02).
- **Acceptance criteria:** a `tests/test_steps.py` table test maps 30 named equations to expected technique titles and passes; temporarily monkeypatching `classify_ode` to return `[]` still yields the correct technique for all 30.
- **Dependencies / risks:** writing eight recognisers is real work, but `_is_exact` shows the pattern and the sympy round trip is already the slowest part of the test suite — this should make it faster.

---

## Pedagogy & content

### [PED-01] Write Unit 8 — nonlinear systems and phenomena

- **Severity:** P1
- **Effort:** XL
- **Confidence:** high — verified absent by keyword scan across all 35 lessons.
- **Evidence:** `01-FINDINGS.md` [D-2]. `git grep -i "chaos\|chaotic\|lyapunov\|limit cycle\|bifurcation\|bendixson\|hartman\|separatri" -- src/odesuite_app/lessons/` → **nothing**. `src/odesuite_app/lessons/__init__.py:78-…` (`UNITS`, seven entries, none for Edwards ch. 6).
- **Problem:** the app implements linearisation, classification and separatrices (`analysis.py`), names Hopf and pitchfork bifurcations in slider hints (`catalog.py:172-173,213`), ships Lorenz tagged `chaotic`, and teaches none of it. Unit 6 is *linear* systems; unit 7 is series. A learner meets a Hopf bifurcation as a tooltip before being taught what a bifurcation is. For an application whose differentiator is nonlinear ODEs, this is the gap.
- **Proposed change:** a new `lessons/unit8_nonlinear.py` registered in `UNITS` between `systems` and `series`, referencing Edwards ch. 6, with six lessons matching the existing structure (objectives, motivation, derivation passages, ≥5 notes including a `pitfall`, 2 worked examples, ≥4 questions, ≥1 template, a figure): **(1)** linearisation at an equilibrium and the Jacobian; **(2)** classification, and where Hartman–Grobman fails; **(3)** nullclines and the phase plane; **(4)** predator–prey and the conservative centre; **(5)** limit cycles and Poincaré–Bendixson; **(6)** bifurcations and the route to chaos.
- **Acceptance criteria:** `len(UNITS) == 8`; the new unit passes every structural test in `tests/test_lessons.py`; each lesson's `tool` links to the Phase Portrait; the misconception scan in this audit finds Hartman–Grobman, limit cycle, bifurcation and Lyapunov all targeted.
- **Dependencies / risks:** largest single item in the backlog. Lessons 5 and 6 are much stronger with DYN-01/DYN-02 landed, so sequence them together; lessons 1–4 can be written against `analysis.py` as it stands today.

### [PED-02] Add figures to the 17 lessons that have none

- **Severity:** P2
- **Effort:** L
- **Confidence:** high — enumerated programmatically.
- **Evidence:** `00-INVENTORY.md` §4a. Lessons with `figure` unset: basics, substitutions, population, superposition, roots, variation, higher, circuits, transform, laplace, impulses, systems-intro, eigenvalues, repeated-eigenvalues, forced-systems, recurrence, frobenius. Infrastructure: `src/odesuite_app/widgets/lessonfigure/` (7 modules, 12 interactive figures).
- **Problem:** the rule of four is complete for 18 lessons and missing its graphical leg for 17 — including `eigenvalues` and `systems-intro`, where a phase portrait is close to indispensable, and `roots`, where the three damping regimes are a picture.
- **Proposed change:** prioritise the eight where a figure carries the most: `eigenvalues` and `systems-intro` (phase portrait with eigendirections), `roots` (three characteristic-root cases side by side), `superposition` (two solutions and their sum), `transform` and `laplace` (the `t`-domain/`s`-domain pair), `impulses` (the response to a delta), `circuits` (RLC against the mass–spring analogue). Follow the existing `lessonfigure/unitN.py` pattern.
- **Acceptance criteria:** at least 8 of the 17 gain a figure; `tests/test_lessons.py` gains an assertion that every lesson in units 1–4 has one; the thumbnail/figure tests pass.
- **Dependencies / risks:** none technical. Time-consuming and best spread across releases; take the eight above first.

### [PED-03] Add a spaced-review queue driven by existing progress data

- **Severity:** P2
- **Effort:** M
- **Confidence:** high — the data model already records exactly what a scheduler needs.
- **Evidence:** `01-FINDINGS.md` [D-5]. `src/odesuite_app/progress.py:28-34` (v2 format records `state`, `right`, `tries` per question).
- **Problem:** the progress file records attempts and outcomes; nothing consumes them for review. The Course Map shows completion, not decay. 42 drill templates make unlimited retrieval *possible* but never *prompted* — the learner must decide what to revisit, which is the decision they are least equipped to make.
- **Proposed change:** add `progress.due_for_review(now)` implementing a simple Leitner schedule from the existing counters (correct-first-try → long interval; correct-after-tries → medium; wrong → short), storing a `last_seen` timestamp alongside the existing fields (a v3 format, with the same forward-compatible loader v2 already has). Surface it as a "Review" card on the Course Map showing what is due, drawing questions from the lesson's templates so it never runs out.
- **Acceptance criteria:** `due_for_review` returns nothing for a fresh profile; after recording a wrong answer with a backdated timestamp, that question is due; a v2 file loads without error and gains timestamps on next write. Tests assert all three, including the v2→v3 migration.
- **Dependencies / risks:** touches the one file the app persists — `progress.py`'s three stated rules (never fatal, atomic, plain) must survive. It already handles v1→v2, so the pattern is established.

### [PED-04] Add FitzHugh–Nagumo and promote SIR to the catalogue

- **Severity:** P2
- **Effort:** S
- **Confidence:** high — verified against the brief's canonical list.
- **Evidence:** `01-FINDINGS.md` [C-5]. `odesuite_app/custom.py` `EXAMPLES` contains SIR (selftest prints `PASS custom: SIR epidemic`); `catalog.CATALOG` (28 entries) contains neither SIR nor FitzHugh–Nagumo.
- **Problem:** SIR exists but only as a preset inside the custom-equation editor, so it never appears in the home gallery and a learner cannot find it. FitzHugh–Nagumo — the standard excitable-medium model and the cleanest teaching example of a slow–fast system — is absent entirely.
- **Proposed change:** add `fitzhugh_nagumo` to `odesuite/problems/__init__.py` (with an analytic Jacobian and its `SEPARABLE`/`NONSTIFF` grouping) and a `CatalogEntry` with sliders for `a`, `b`, `tau`, `I_ext` and tags `nonlinear, oscillator, 2d, biology`. Promote SIR to a full `CatalogEntry` with sliders for `beta`, `gamma`, `N`, tagged `nonlinear, biology, 3d`.
- **Acceptance criteria:** both appear in `catalog.keys()`; both render a home thumbnail; `--list-problems` shows them; FitzHugh–Nagumo at `I_ext` above threshold produces a limit cycle detectable by DYN-02.
- **Dependencies / risks:** none. Cheap, and both are strong Unit 8 teaching material (PED-01).

### [PED-05] Teach why the numerical answer to `y'=y^{1/3}` is not the whole story

- **Severity:** P2
- **Effort:** S
- **Confidence:** high — the lesson and the contradicting behaviour both verified.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 6; `01-FINDINGS.md` [A-5]. `lessons/unit1_first_order.py`, lesson `slopefields`, `pitfall` note.
- **Problem:** the lesson tells the student that `y'=y^{1/3}, y(0)=0` has two solutions. If the student then types it into the Solver Lab, they get `y ≡ 0` and a green "finished". The most memorable thing available here — *watch the tool get it half-right, and understand why* — is currently just a contradiction.
- **Proposed change:** turn it into a worked exercise. Add a `Example` (or a `tool`-linked exercise) to `slopefields` that walks the learner through solving it numerically, observing `y ≡ 0`, plotting `(2t/3)^{3/2}` alongside, and confirming both satisfy the equation. Pair with NUM-06 so the banner appears at the moment the lesson predicts it.
- **Acceptance criteria:** the `slopefields` lesson gains an example whose narration references both solution branches; a test asserts both branches satisfy the ODE under `check_answer`.
- **Dependencies / risks:** best landed with NUM-06.

### [PED-06] Add a "when this method fails" note to every method lesson

- **Severity:** P2
- **Effort:** M
- **Confidence:** high — the `pitfall` note kind exists and is used 34 times, so the pattern is established; the gap is specifically failure *of the method*.
- **Evidence:** `01-FINDINGS.md` [D-1] (misconceptions well covered), §K-5 (no document on method limits). The brief: *"Does the app teach when a method fails, not just when it works? Nonlinear ODEs are mostly failure cases."*
- **Problem:** the existing pitfalls target *student errors*. What is thinner is the honest statement of each method's domain: undetermined coefficients has no finite trial set for `sec t`; series solutions diverge past the nearest singularity; Laplace needs exponential order; Euler is unconditionally unstable on an oscillator (verified: it overflows, Experiment 4); explicit RK dies on stiff problems (verified: 19–23 s to failure, Experiment 3).
- **Proposed change:** add one `pitfall` note per method lesson stating the failure boundary and, where the app can show it, linking to the tool that demonstrates it — `undetermined` → why `sec t` forces variation of parameters; `power-series` → radius of convergence; `numerical`/`rungekutta` → stability and stiffness, linking to the Stiffness Explorer; `laplace` → exponential order.
- **Acceptance criteria:** each of the 12 method-teaching lessons has at least one `kind="pitfall"` note whose body names a condition under which the method does not apply; a test asserts the count.
- **Dependencies / risks:** none. Several of these can quote this audit's measured numbers directly.

### [PED-07] Name Lipschitz and Picard–Lindelöf

- **Severity:** P3
- **Effort:** S
- **Confidence:** high — both return zero hits repo-wide.
- **Evidence:** `01-FINDINGS.md` [D-4]. `git grep -i lipschitz` and `git grep -i picard` → nothing. `lessons/unit1_first_order.py`, lesson `slopefields`.
- **Problem:** the content is taught correctly — the ∂f/∂y-continuity form, "local and only sufficient", and both classic counterexamples. Only the standard names are missing, which matters solely because a student who wants to read further cannot search for what they were taught.
- **Proposed change:** add one `aside` note to `slopefields` naming the theorem (Picard–Lindelöf) and the stronger hypothesis it is usually stated with (Lipschitz continuity in `y`), and noting that the ∂f/∂y condition taught here implies it.
- **Acceptance criteria:** `git grep -i "picard\|lipschitz" -- src/odesuite_app/lessons/` returns hits; the note is `kind="aside"` so it reads as optional context.
- **Dependencies / risks:** none. Keep it an aside — the existing choice to teach the ∂f/∂y form first is pedagogically right and should not change.

### [PED-08] Flag a discontinuous RHS from the rejection pattern

- **Severity:** P3
- **Effort:** M
- **Confidence:** medium — the signature is real and the data is already recorded, but the threshold needs calibration.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 6 (`y'=sign(t-1)`: 22 rejected steps clustered at `t=1`, reported as unqualified success); `01-FINDINGS.md` [A-7]. `src/odesuite/solution.py:66-77` (`Solution.rejected` already records `(t, h)` pairs, and the docstring says these "mark exactly where the solution got hard").
- **Problem:** the solver already collects precisely the data needed to spot a discontinuity, and its own docstring says so — a dense cluster of rejections at one `t`. It is not used. A learner integrating a switched forcing term gets `success=True` and no hint that anything unusual happened at the switch.
- **Proposed change:** in `odesuite_app`, a small `analysis.rough_spots(solution)` that clusters `solution.rejected[:, 0]` and returns times where rejections concentrate beyond a threshold. Mark them on the Solver Lab plot with a vertical rule and a tooltip: *"the solver struggled here — the right-hand side may be discontinuous or the solution may be nearly singular."*
- **Acceptance criteria:** `y' = sign(t-1)` flags `t ≈ 1`; a smooth decay flags nothing; `y' = y²` to `t=2` flags `t ≈ 1`. Tests assert all three.
- **Dependencies / risks:** false positives on a genuinely hard-but-smooth problem; word the tooltip as an observation about the solver, not a claim about the equation.

---

## UX & interaction

### [UX-01] Add a splash screen while the window builds

- **Severity:** ~~P2~~ → **P3**
- **Effort:** S
- **Confidence:** high — the startup figure it rested on was wrong; see [E-1].
- **Evidence:** `01-FINDINGS.md` [E-1], retracted. The window is up in **1.44 s** warm and about 3.5 s of process time cold, not the 14–17 s originally reported.
- **Problem, restated honestly:** at 1.4 s there is a brief gap where nothing is on screen, and on a machine slower than this one or under load it will be longer — the audit's own bad measurement is a demonstration of what a loaded machine does to it. That is worth a splash for reassurance, and no more than that. It is not the "15 s of blank screen" this item was written for.
- **Proposed change:** a `QSplashScreen` shown immediately after `QApplication` construction and closed when `MainWindow` is ready. Progress *stages* are not worth the plumbing at this duration; a name and a spinner are.
- **Acceptance criteria:** something visible within 0.5 s of `QApplication` construction; `--selftest`, `--list-problems` and `--rebuild-thumbnails` do not show it.
- **Dependencies / risks:** none. No longer depends on PERF-01, which is withdrawn.

### [UX-02] Save and restore the full session

- **Severity:** P2
- **Effort:** M
- **Confidence:** high — verified: `QSettings` stores only geometry.
- **Evidence:** `01-FINDINGS.md` [E-3]. `src/odesuite_app/app.py:294-311` (geometry only), `src/odesuite_app/progress.py:3` ("the only thing the application stores on disk").
- **Problem:** "Van der Pol at μ=800, radau, rtol=1e-9, this window, this screen" cannot be saved, restored or shared. Close the app and it is gone. For a study tool used across sittings, and for an instructor wanting to hand a class a configured starting point, that is a real limit.
- **Proposed change:** serialise `SessionState` (problem key, method, rtol/atol, params, plot window, current screen) to JSON. Restore on launch behind a preference; add File → Save Session / Open Session; accept a session file as a CLI argument alongside the existing `--problem` and `--screen`. Reuse `progress.py`'s atomic-write and corruption-tolerance pattern rather than inventing a second one.
- **Acceptance criteria:** round-tripping a session reproduces problem, method, tolerances, parameters and screen exactly; a corrupted session file is ignored with a message, never fatal; `odesuite-gui session.json` opens it.
- **Dependencies / risks:** a user equation in the session means storing its source text — which must go back through the SEC-01 validator on load, not be trusted because it came from a file.

### [UX-03] Surface `as_code()` as a visible "copy reproducing code" button

- **Severity:** P2
- **Effort:** S
- **Confidence:** high — the method exists and is well designed; the question is discoverability.
- **Evidence:** `src/odesuite_app/solver.py:55` (`SolveRequest.as_code()`), `src/odesuite_app/catalog.py:110-117` (`CatalogEntry.code`, with a comment that the snippet "can never disagree" with what was run).
- **Problem:** the app can already emit the exact `odesuite` snippet reproducing the current solve — an unusually good feature for reproducibility and for the transition from GUI to library. If it is not a visible button on the Solver Lab, most users will never find it.
- **Proposed change:** a "Copy code" button in the Solver Lab's control panel that puts `as_code()` on the clipboard and confirms with a brief status message. Show the snippet in a collapsible panel beneath the plot.
- **Acceptance criteria:** the button exists, the clipboard receives a snippet that runs unmodified and reproduces the plotted result to solver tolerance, and a test executes the emitted snippet and compares against the in-app solution.
- **Dependencies / risks:** the round-trip test is the valuable part — it turns a documentation claim into a checked one.

### [UX-04] Show the predictability horizon on chaotic systems

- **Severity:** P2 · **honesty**
- **Effort:** M
- **Confidence:** medium — depends on DYN-03 for the exponent; the display decision is straightforward.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 9; `01-FINDINGS.md` [C-4]. `catalog.py:226-227` (the warning, on the gallery card), `widgets/cards.py:87` (chaotic tag coloured as a warning).
- **Problem:** Lorenz's predictability horizon for a `1e-10` perturbation is `t ≈ 27.5`; separation reaches 6.5 by `t=40`. The app's honest warning lives on the *gallery card*. Once the trajectory is plotted, nothing distinguishes the meaningful early part from the meaningless late part — and the `t_end` slider goes well past the horizon with no change in presentation. The default `t_end=20` is inside the horizon, so the default view is honest and any increase silently is not.
- **Proposed change:** for entries tagged `chaotic`, compute the horizon from DYN-03's exponent and the solve's own tolerance (`t_horizon ≈ ln(1/rtol)/λ`), draw a vertical rule at it, and fade or hatch the trajectory beyond it with a caption: *"beyond here a single trajectory is not a prediction — the attractor is, the path is not."*
- **Acceptance criteria:** Lorenz at `rtol=1e-8` marks a horizon in `t ∈ [18, 24]`; a non-chaotic system marks none; the caption appears only when `t_end` exceeds the horizon.
- **Dependencies / risks:** requires DYN-03. Make the rule dismissible — it should teach, not nag.

### [UX-05] Throttle replots to one per frame

- **Severity:** P3
- **Effort:** S
- **Confidence:** medium — the stall is measured, the attribution to redraw is inferred from the solve being off-thread.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 10. Max GUI-thread gap 81.9 ms (brusselator), 83.0 ms (KS), **104.1 ms** (Pleiades), against a 5–6 ms median.
- **Problem:** solves are correctly off-thread and the token/cancellation scheme works — during the Van der Pol drag *zero* stale results were delivered, exactly as designed. What remains costly is delivering and drawing the results that do land: 104 ms on Pleiades (28 state components) is one visible freeze. Measured offscreen, so on-screen is at least this bad.
- **Proposed change:** in `widgets/plotpanel.py`, coalesce incoming results behind a ~16 ms `QTimer` so at most one redraw happens per frame regardless of how many results land, and decimate before drawing: for a curve with more than ~4,000 points, downsample with a min/max-per-pixel-column scheme that preserves visual extremes (pyqtgraph's `setDownsampling(auto=True, mode='peak')` does exactly this).
- **Acceptance criteria:** the Experiment 10 harness reports max GUI-thread gap below 50 ms on all six problems, with Pleiades specifically under 50 ms (currently 104 ms).
- **Dependencies / risks:** peak-mode downsampling must not hide a genuine spike — verify against a stiff transient that the plotted extremes match the data's.

### [UX-06] Remove the duplicate `taylor` alias from the method registry

- **Severity:** P3 · **removal**
- **Effort:** S
- **Confidence:** high — read directly from the registry.
- **Evidence:** `src/odesuite/steppers/__init__.py` (`SPECIAL_METHODS` maps `"taylor"`, `"taylor8"`, `"taylor20"`, `"taylor30"`); enumerated: `make_stepper("taylor").name == "Taylor20"`.
- **Problem:** `"taylor"` silently means `"taylor20"`. Of 21 registered method names, three are aliases (`rk45`→DOPRI5, `radau5`→radau, `taylor`→taylor20) and one is an internal oracle (`radaudense`). `rk45` is a genuinely familiar alias worth keeping; `taylor` is a bare name whose order is invisible, and order is the whole point of the method.
- **Proposed change:** remove `"taylor"` from `SPECIAL_METHODS`, keeping the explicit orders. Update `KeyError` guidance in `make_stepper` (it already lists available names) and any docs or examples using the bare name.
- **Acceptance criteria:** `make_stepper("taylor")` raises `KeyError` listing the explicit alternatives; `git grep '"taylor"' -- src tests examples docs` returns no live uses; the suite passes.
- **Dependencies / risks:** a breaking change to a public name — do it before 1.0 and note it in the changelog under Removed.

---

## Accessibility

### [A11Y-01] Give every interactive control an accessible name

- **Severity:** P2
- **Effort:** M
- **Confidence:** high — counted: 7 `setAccessibleName` and 3 `setAccessibleDescription` across 68 modules, 6 of the 10 in one widget.
- **Evidence:** `01-FINDINGS.md` [F-1]. `src/odesuite_app/widgets/mathlabel.py:181-184` (the one place it is done, and done well).
- **Problem:** `MathLabel` correctly exposes the plain-text form of a rendered equation bitmap as its accessible description — the hardest case, handled. Everything else — 13 screens, the plot panels, the sliders, the method picker, the lesson cards — has none. 45 `setToolTip` calls give hover help, which a screen reader does not announce as a label.
- **Proposed change:** sweep `widgets/controls.py`, `widgets/cards.py`, `widgets/stats.py`, `widgets/stepspanel.py` and the 13 screens, setting `setAccessibleName` on every focusable control and `setAccessibleDescription` where the tooltip carries meaning. Where a tooltip already exists, reuse its text rather than writing new copy.
- **Acceptance criteria:** a test walks the widget tree of each constructed screen and asserts every widget with `focusPolicy() != Qt.NoFocus` has a non-empty `accessibleName()`. It should fail today on all 13.
- **Dependencies / risks:** the tree-walking test is the durable part — it prevents regression as screens grow.

### [A11Y-02] Give every plot a text alternative and a data table

- **Severity:** P2
- **Effort:** L
- **Confidence:** high — verified absent.
- **Evidence:** `01-FINDINGS.md` [F-2]. No `setAccessibleDescription` on any pyqtgraph widget; no data-table view anywhere.
- **Problem:** the product is largely graphical and a non-visual learner gets nothing from the Solver Studio. This is also the single biggest gap between the app and the "rule of four" it otherwise honours: the graphical representation is unavailable, and there is no verbal substitute for it.
- **Proposed change:** two parts. (1) Generate a one-paragraph summary for each plotted solution — monotonic or oscillating, extrema and where, limiting behaviour, number of equilibria crossed — and set it as the plot widget's accessible description. (2) Add a "Data" tab beside each plot showing a `QTableView` of `(t, y₁, …, yₙ)` at the output times, keyboard-navigable and copyable. The summary doubles as the verbal leg of the rule of four for sighted learners too.
- **Acceptance criteria:** every plot panel has a non-empty accessible description that names at least the qualitative behaviour and the endpoint value; the data table is reachable by keyboard alone and its contents match `solution.t` / `solution.y`.
- **Dependencies / risks:** the summary generator is the interesting part and risks being vacuous — write it against three concrete cases (decay, oscillation, blow-up) and test the wording for each.

### [A11Y-03] Distinguish separatrices by dash pattern as well as colour

- **Severity:** P3
- **Effort:** S
- **Confidence:** high — read from the drawing code; the fix mirrors a decision the same file already made.
- **Evidence:** `01-FINDINGS.md` [F-3]. `src/odesuite_app/screens/portrait.py:364` (`palette.danger if label == "unstable" else palette.success`), against `portrait.py:39,46-47` (`_MARKERS`, shape-encoded "so it survives greyscale and colour-vision deficiency").
- **Problem:** equilibrium markers correctly encode type as shape *and* colour, for a stated reason. Separatrices are lines and got only colour — red for unstable, green for stable, the exact pairing that red–green colour blindness collapses.
- **Proposed change:** draw the stable manifold solid and the unstable manifold dashed (`pg.mkPen(colour, width=2.2, style=Qt.DashLine)`), and say so in the legend at `portrait.py:391-393`.
- **Acceptance criteria:** the two manifold families differ in dash style; the legend states the convention; a test asserts the pen styles differ.
- **Dependencies / risks:** none. Small, and it completes a decision the file already made for markers.

### [A11Y-04] Make rendered maths follow the OS text scale

- **Severity:** P3
- **Effort:** M
- **Confidence:** low — I could not verify the current behaviour under the offscreen platform; the code path suggests the problem but a real display is needed to confirm.
- **Evidence:** `01-FINDINGS.md` [F-6] (`UNVERIFIED`). `src/odesuite_app/widgets/mathlabel.py:138-139` (size taken from `devicePixelRatio()`), `:186` (image height divided by it).
- **Problem:** equations are matplotlib-rendered bitmaps sized from the device pixel ratio, not from the application font size. If a user raises their OS text scale to 200%, surrounding text should grow and the equations plausibly will not — leaving the maths, which is the content, smallest on the page. This needs confirming on a real display before it is fixed.
- **Proposed change:** first, verify at 100/150/200% on a real display. If confirmed, multiply the render DPI by `QApplication.font().pointSizeF() / <baseline>` so the bitmap tracks the text, and invalidate the `MathLabel` cache on `QEvent.ApplicationFontChange`.
- **Acceptance criteria:** at 200% OS text scale, rendered equation height is within 10% of the surrounding body text's line height; changing the scale while running re-renders rather than showing a stale bitmap.
- **Dependencies / risks:** the render cache is keyed on expression and palette; adding font scale to the key increases misses. Measure the cost — `mathlabel.py` already renders off-thread, so the risk is memory, not latency.

---

## Architecture & code quality

### [ARCH-01] Make `Solution` carry a structured diagnosis, not just a string

- **Severity:** P2
- **Effort:** M
- **Confidence:** high — three separate findings all reduce to "the caller cannot tell *why* programmatically".
- **Evidence:** `01-FINDINGS.md` [A-3], [A-4], [A-5], [A-7]. `src/odesuite/solution.py:52-92` (`status` is one of four strings; `message` is free text).
- **Problem:** every diagnostic the solver produces is a prose string. A caller — including the app's own screens — cannot distinguish "blew up in finite time" from "hit max_steps" from "the RHS returned NaN" without parsing English. NUM-04's better message, NUM-05's tolerance flag and DYN-05's incompleteness flag each want a place to live, and adding three unrelated booleans is the wrong shape.
- **Proposed change:** add `Solution.diagnosis: Diagnosis | None`, a small frozen dataclass with `kind: Literal["blowup","singularity","nonfinite_rhs","max_steps","step_underflow","fixed_step_overflow","newton_failure"]`, `t: float`, and `detail: str`. Keep `message` as the human-readable rendering of it, so nothing breaks. Populate at each `break` in `driver.solve`.
- **Acceptance criteria:** each of the six pathological inputs in Experiment 6 yields the expected `diagnosis.kind` and a `diagnosis.t` within `1e-6` of the true event; `message` remains unchanged for cases that already have good text.
- **Dependencies / risks:** additive, so no caller breaks. Land before NUM-05 and DYN-05 so they have somewhere to go.

### [ARCH-02] Correct the `state.py` layering docstring

- **Severity:** P3
- **Effort:** S
- **Confidence:** high — four counterexamples.
- **Evidence:** `01-FINDINGS.md` [G-2]. `src/odesuite_app/state.py:5` claims *"Screens never talk to `odesuite` directly."* Counterexamples: `screens/accuracy.py:35`, `screens/stiffness.py:35,74,369`, `screens/portrait.py:270`, `screens/learn_problems.py:181`.
- **Problem:** the docstring states a rule the code does not follow. In a codebase whose comments are otherwise exact and load-bearing, a false architectural claim is worse than none — the next reader will either believe it or lose trust in the rest.
- **Proposed change:** rewrite the paragraph to describe the boundary that exists: screens route *problem selection, method, tolerances and the main solve* through `SessionState`; screens doing method comparison or stability analysis (Accuracy Lab, Stiffness Explorer, Phase Portrait, Worked Problems) call `odesuite` directly, because those computations are not session state. State that as the rule.
- **Acceptance criteria:** the docstring matches the code; the four modules are named in it so a future reader can check.
- **Dependencies / risks:** none. Alternatively route them through `state` — but that would bloat the view-model to serve four callers, and the current split is the better design.

### [ARCH-03] Delete `radaudense` from the user-facing method list

- **Severity:** P3 · **removal**
- **Effort:** S
- **Confidence:** high — its own docstring says it is not for users.
- **Evidence:** `src/odesuite/steppers/__init__.py` (`IMPLICIT_METHODS` includes `"radaudense"`, commented *"kept as the oracle the fast path is validated against rather than as a method anyone should choose"*); `src/odesuite/steppers/irk.py:19-32`.
- **Problem:** a test oracle is exposed as one of 21 public method names. `make_stepper`'s `KeyError` lists every registered name, so a user who mistypes is offered `radaudense` as a suggestion, and it is 5× slower than `radau` for identical results (verified: identical to machine precision in Experiment 1).
- **Proposed change:** remove it from `METHODS`/`IMPLICIT_METHODS`; have `tests/test_radau.py` construct `RadauIIA(linear_solve="dense")` directly, which is what it is testing anyway. Keep the constructor argument — it is the real interface.
- **Acceptance criteria:** `"radaudense" not in METHODS`; `tests/test_radau.py` still cross-validates both paths; `make_stepper`'s error message no longer offers it.
- **Dependencies / risks:** a public-name removal; note it under Removed in the changelog.

### [ARCH-04] ~~Remove the stale `dist/` artefacts and the unused `slow` marker~~ — **half WITHDRAWN, my error**

- **Severity:** ~~P3~~ → nothing to do
- **Confidence:** high, in the withdrawal — re-measured.
- **The `slow` marker is not unused.** This item claimed `git grep "mark.slow" -- tests/` "finds no test carrying it". That is simply false: **24 tests across 16 files** carry `@pytest.mark.slow`, and `pytest -m "not slow"` deselects **80 of 3358** tests. I do not know how the original grep came back empty; the claim should not have been made without the collection count behind it, which is what settles it:

  ```
  pytest --collect-only            -> 3358 tests collected
  pytest --collect-only -m "not slow" -> 3278 collected, 80 deselected
  ```

  The facility works. Nothing to remove and nothing to annotate.
- **The stale `dist/` half stands but is not actionable in the repository.** `dist/` holds `odesuite-0.3.0` wheels against a 0.4.0 source, and it is gitignored — so this is local hygiene on one machine, not a change anyone can commit. Recorded and closed.
- **Lesson, since this is the third measurement error in this audit:** a claim of the form "X does not exist" needs the *positive* check that would have found it, not a grep that came back empty. The two other retractions ([E-1] startup, and PERF-01 built on it) were the same shape — a number taken once, under conditions I did not verify.
- **Dependencies / risks:** if the marker is adopted, CI must still run the full set — deselecting is for local iteration only.

### [ARCH-05] Collapse the three near-identical background-job runners

- **Severity:** P3 · **removal**
- **Effort:** M
- **Confidence:** medium — they are structurally similar; whether one abstraction fits all three needs a read of each.
- **Evidence:** `src/odesuite_app/screens/home.py:30` (`_ThumbJob`), `screens/accuracy.py:53` (`_StudyJob`), `screens/portrait.py:55` (`_AnalysisJob`), `screens/learn_laplace.py:52` (`_LaplaceJob`), `screens/learn_lessons.py:70` (`_WorkingJob`). All five are `QRunnable` subclasses with a signals object, a token, and a `run()` that catches exceptions and emits.
- **Problem:** five hand-rolled implementations of one pattern — worker plus token plus staleness plus error capture — which `solver.py` already implements carefully and documents (`solver.py:10-19` explains the token discipline and the cancellation callback). Each copy is a place for the discipline to be got subtly wrong, and `solver.py` is at 80.3% coverage while these are lower.
- **Proposed change:** extract `odesuite_app/jobs.py` with a generic `TokenJob(QRunnable)` carrying the signals object, token comparison and exception capture; reduce the five to a callable plus a result type. Keep `SolveRunner` as the ODE-specific layer on top.
- **Acceptance criteria:** the five classes become one; `git grep "class _.*Job(QRunnable)" -- src/` returns one hit; all screen tests pass; coverage of the shared runner exceeds 90%.
- **Dependencies / risks:** touches five screens at once. Do it after the P0/P1 work, and only with the screen tests green before and after.

---

## Performance

### [PERF-01] ~~Defer sympy, matplotlib and pyqtgraph imports off the startup path~~ — **WITHDRAWN**

- **Severity:** ~~P1~~ → **not a defect**
- **Effort:** —
- **Confidence:** high, in the withdrawal — re-measured on an idle machine and the original cause reproduced deliberately.
- **Evidence:** `01-FINDINGS.md` [E-1], retracted. The figures this item rested on (sympy 7.02 s, scipy 4.48 s, pyqtgraph 4.27 s, matplotlib 3.62 s, 14.4–16.7 s to a window) were measured while a parallel `pytest -n auto` run was saturating all 14 cores. On an idle machine the same imports cost 0.40 / 0.35 / 0.29 / 0.29 s, `MainWindow()` 0.40 s, and the window is up in **1.44 s** with **3.5 s** of total process time. Re-running the measurement under a deliberate 14-process load reproduces the original numbers (sympy 7.19 s against 7.02 s reported), which confirms contention as the cause rather than merely suggesting it.
- **Why it is withdrawn rather than downgraded:** ~1.4 s to a usable window is ordinary for a desktop scientific application. The eager imports are real — sympy, matplotlib and pyqtgraph are all pulled in at module scope — but they cost about a second between them. Restructuring the import graph and making screen construction lazy carries a genuine risk (a screen built late has to reconcile with `SessionState` on first show) for a saving nobody would notice.
- **If it is ever revisited:** the cheap half is lazy screen construction in `MainWindow.__init__`, which is self-contained and worth ~0.4 s. The rest is not worth the risk.

### [PERF-02] Detect stiffness and bail out in <1 s instead of 20 s

- **Severity:** P2
- **Effort:** M
- **Confidence:** high — failure times measured.
- **Evidence:** `02-EXPERIMENTS.md` Experiment 3; `01-FINDINGS.md` [H-2]. dopri5 on Van der Pol μ=1000: 19.4 s, 499,987 steps. On Robertson: 22.6 s, 499,996 steps. `tests/test_app_stiffness.py::test_race_shows_an_explicit_method_failing_on_robertson` takes 34 s.
- **Problem:** when an explicit method meets a stiff problem it grinds to `max_steps` and only then fails. The app deliberately stages this in the Stiffness Explorer and Method Race, which is pedagogically right — but the learner watches a spinner for 20 s to be told something detectable in a fraction of a second, and the same 20 s is spent in CI on every run.
- **Proposed change:** add stiffness detection to `driver.solve`: track the ratio of accepted to attempted steps and the step size against the interval; when an explicit method has taken more than N steps whose size is below `span/1e4` with a high rejection ratio, stop with `status="failed"` and a diagnosis (ARCH-01) of kind `"stiffness_suspected"`, message naming the symptom and recommending `radau`/`rodas4`. Expose as `stiffness_detection=True` so the pedagogical screens can *opt out* and show the grind deliberately, with a progress bar.
- **Acceptance criteria:** dopri5 on Robertson fails in under 1 s (currently 22.6 s) with a diagnosis naming stiffness; no `NONSTIFF` benchmark triggers it at `rtol` from `1e-3` to `1e-12`; the Method Race test drops below 10 s.
- **Dependencies / risks:** false positives would be worse than the current slowness — the no-false-alarm criterion above is the gate. Best after ARCH-01.

### [PERF-03] Hoist the ERK stage buffer out of the step loop

- **Severity:** P3
- **Effort:** S
- **Confidence:** high — read directly; the same file family already does the right thing elsewhere.
- **Evidence:** `01-FINDINGS.md` [H-3]. `src/odesuite/steppers/erk.py:56` (`K = np.empty((s, y.size), dtype=y.dtype)` per step), against `src/odesuite/steppers/irk.py` (hoists one `F` buffer per step with a comment explaining that it is fully overwritten and never escapes).
- **Problem:** every ERK step allocates a fresh `(s, n)` array — 7×n for DOPRI5. Over the 500,000-step runs in Experiment 4 that is 500,000 allocations of pure churn. Radau already avoids exactly this and documents why.
- **Proposed change:** cache `self._K` on the stepper, reallocating only when `s`, `n` or dtype changes. `interpolant` already reads `self._K` immediately after `step`, so lifetime is unchanged — but `RKPolynomialInterpolant.__init__` computes `Q = K.T @ P`, which copies, and `HermiteInterpolant` copies its inputs, so no interpolant retains the buffer. Add the same "never escapes" comment `irk.py` carries.
- **Acceptance criteria:** a benchmark of 500,000 fixed Euler/RK4 steps shows measurably fewer allocations (via `tracemalloc`) and no regression in wall time; every existing convergence and dense-output test passes bit-for-bit.
- **Dependencies / risks:** the real risk is an interpolant outliving the buffer. Verify by asserting that a `DenseOutput` built over many steps still evaluates correctly after further stepping — `tests/test_dense.py` should gain that assertion explicitly.

---

## Testing & CI

### [TEST-01] Regression tests for every defect in this audit

- **Severity:** P1
- **Effort:** M
- **Confidence:** high — each defect has a reproduction already written.
- **Evidence:** `02-EXPERIMENTS.md` Experiments 1b, 2, 4b, 6, 8, 11. All of these pass the current suite.
- **Problem:** the suite is strong (3,125 tests, 96.3% library coverage) and every defect found here slipped through it. Without a failing test each, any of them can return.
- **Proposed change:** one test per defect, each failing today: SEC-01 (sandbox escapes, both entry points, canary absent); NUM-01 (Taylor with `y*np.cos(t)` does not kill the process); NUM-02 (Radau achieved/requested ≤ 5 at `rtol=1e-12`); NUM-03 (RODAS4 order ≥ 3.85 on `y'=y cos t`); NUM-04 (fixed-step overflow returns in <2 s with ≤1 rejection); NUM-08 (`y'=1/t` raises `ValueError` naming `t0`); DYN-05 (`sin(20t)` incompleteness flagged). Group them in `tests/test_regressions.py` with a comment naming the audit item, or place each beside its module's existing tests — the latter is better for discoverability.
- **Acceptance criteria:** each test fails on `66e7491` and passes after its fix; CI runs them.
- **Dependencies / risks:** none — these should be written *before* the fixes, so each fix is demonstrably the thing that closed it.

### [TEST-02] Add a coverage gate to CI

- **Severity:** P2
- **Effort:** S
- **Confidence:** high — measured 96.3% library / 89.9% app / 91.2% total.
- **Evidence:** `01-FINDINGS.md` [I-1]. `pytest-cov` absent from `pyproject.toml:46-58` and from `ci.yml`.
- **Problem:** the project has never had a coverage number; the figures in this audit exist only because the tool was installed for it. A 96.3% library figure is a real asset and nothing currently defends it.
- **Proposed change:** add `pytest-cov` to `[dev]`; in the `tests` job run with `--cov=odesuite --cov=odesuite_app --cov-fail-under=88`, plus a separate stricter check `--cov=odesuite --cov-fail-under=95` so the library cannot regress behind the app's average. Upload the HTML report as an artefact.
- **Acceptance criteria:** CI fails on a PR that drops library coverage below 95% or total below 88%; the report is downloadable from the run.
- **Dependencies / risks:** coverage under `-n auto` needs `--cov-append` handling — verify the combined figure matches a serial run before setting the gate (this audit's run used `-n auto` successfully).

### [TEST-03] Add property-based tests

- **Severity:** P2
- **Effort:** M
- **Confidence:** high — verified absent, and one of the properties would have caught [A-2] directly.
- **Evidence:** `01-FINDINGS.md` [I-3]. No `hypothesis` dependency; no reversibility, superposition or translation-invariance test.
- **Problem:** the suite tests specific problems well and structural invariants not at all. RODAS4's autonomous-vs-non-autonomous split (NUM-03) is exactly the shape a property test finds and an example-based test misses.
- **Proposed change:** add `hypothesis` to `[dev]` and four properties: **(1) time-reversibility** — for the symplectic methods, integrating forward `n` steps then backward `n` returns to `y0` within `1e-10`; **(2) superposition** — for a linear ODE, `solve(a·y₀ + b·z₀) == a·solve(y₀) + b·solve(z₀)` to solver tolerance; **(3) time-translation invariance** — for an autonomous problem, solving on `[0,T]` and on `[s, s+T]` from the same `y0` gives the same trajectory; **(4) autonomisation** — a non-autonomous problem and its autonomised form (state extended by `t`) agree, which is the direct check on NUM-03. Draw coefficients and initial conditions from bounded strategies with a fixed seed.
- **Acceptance criteria:** all four pass on fixed seeds after NUM-03 lands; property (4) fails on `66e7491` for `rodas4`.
- **Dependencies / risks:** flakiness. Fix the seed, bound the strategies, and mark the suite `slow` if it costs more than ~30 s.

### [TEST-04] Cover `dsolve_worker.py` and `solver.py`

- **Severity:** P2
- **Effort:** M
- **Confidence:** high — measured.
- **Evidence:** `01-FINDINGS.md` [I-6]. `dsolve_worker.py` 57.7% (44 statements missed), `solver.py` 80.3% (27 missed), `cli.py` 50.0% (60 missed).
- **Problem:** the two least-covered non-trivial modules are the subprocess boundary and the threading/cancellation layer — precisely where bugs are hardest to reproduce and most likely to hang the UI. `solver.py`'s docstring describes a careful token-and-cancellation discipline (`solver.py:10-19`); a fifth of it is unexercised.
- **Proposed change:** for `dsolve_worker`, test the paths that are not the happy one: timeout kill, a worker that dies mid-reply, malformed JSON on the wire, an expression sympy raises `NotImplementedError` on (`dsolve_worker.py:219`). For `solver.py`, test that a superseded token stops its solve at the next step boundary (assert `nfev` is far below a full solve), that an exception inside a job reaches `SolveResult` rather than escaping the pool thread, and that results arriving out of order are discarded by token.
- **Acceptance criteria:** both modules above 85%; a test asserts a cancelled solve consumed under 20% of the `nfev` of an uncancelled one.
- **Dependencies / risks:** timing-dependent tests are a flakiness risk — assert on `nfev` and token order, never on wall clock.

### [TEST-05] Add a performance regression gate

- **Severity:** P3
- **Effort:** M
- **Confidence:** high — the benchmarks exist and nothing runs them.
- **Evidence:** `01-FINDINGS.md` [I-5]. `benchmarks/` (5 scripts, `run_all.py`); no CI job invokes them.
- **Problem:** `benchmarks/work_precision.py`, `energy_drift.py` and `stability_regions.py` produce exactly the figures that would catch a performance or accuracy regression, and they run only when someone remembers. A change that doubled Radau's step count on Robertson, or halved RODAS4's accuracy, would pass CI.
- **Proposed change:** a `bench` CI job running a fast subset — step counts and `nfev` for `radau`/`rodas4` on Robertson, HIRES, OREGO and Van der Pol μ=1000 at `rtol=1e-6` — asserting each against a committed baseline with a 25% tolerance band. Store baselines in `benchmarks/baseline.json`; make updating them a deliberate, reviewed commit. Step counts, not wall time, so it is robust to runner variability.
- **Acceptance criteria:** the job runs in under 2 minutes and fails when a baseline is exceeded by more than 25%; baselines match this audit's Experiment 3 figures (radau: VdP 1142, Robertson-1e11 239, HIRES 142, OREGO 947).
- **Dependencies / risks:** step counts vary slightly with BLAS — validate the band across both CI operating systems before enforcing.

---

## Release ops, docs & licensing

### [REL-02] Test the platforms actually advertised

- **Severity:** P2
- **Effort:** S
- **Confidence:** high — compared classifiers against the CI matrix.
- **Evidence:** `01-FINDINGS.md` [L-2]. `pyproject.toml` classifiers advertise Python 3.10–3.13 and `Operating System :: OS Independent`; `.github/workflows/ci.yml` tests 3.10 and 3.12 on `ubuntu-latest` and `windows-latest`.
- **Problem:** Python 3.11 and 3.13, and macOS entirely, are advertised and untested. macOS is the likeliest gap to bite — Qt, matplotlib font handling and the PyInstaller build all differ there, and `conftest.py:14-16` already carries a Windows-specific font workaround, which is evidence that platform differences in this area are real.
- **Proposed change:** add `macos-latest` to the `tests` matrix and add 3.11 and 3.13 to at least one OS leg. If macOS proves problematic, the honest alternative is to narrow the classifiers rather than leave the claim unbacked.
- **Acceptance criteria:** every advertised Python version and OS appears in a green CI leg, or the classifier list is reduced to what CI covers.
- **Dependencies / risks:** macOS runners are slower and may surface real failures — that is the point, but budget time for the first green run.

### [REL-03] Write "when each method fails"

- **Severity:** P2
- **Effort:** M
- **Confidence:** high — the material now exists; only assembly is needed.
- **Evidence:** `01-FINDINGS.md` [K-5]. `docs/` has `index.md`, `examples.md`, `license.md` and five API pages; none states a method's limits in one place.
- **Problem:** the per-module documentation on *how* each method works is excellent. There is no page saying *when each one fails* — which for a teaching product is the more useful document, and is exactly what this audit's experiments measured: explicit methods on stiff problems (19–23 s to failure), RODAS4 on non-autonomous problems (order 1 below `2.8e-11`), Radau below `rtol=1e-9` (54× shortfall), event detection at the default setting (7 of 63 crossings), Taylor's jet-arithmetic requirement, Euler's unconditional instability on an oscillator.
- **Proposed change:** `docs/limits.md`, one section per method family, each with the failure mode, a reproduction, the measured number, and the recommended alternative. Link it from `README.md` and from the in-app method picker's tooltip. Update it as NUM-02 and NUM-03 land — a limit that has been fixed should be recorded as fixed, not deleted.
- **Acceptance criteria:** every method in `METHODS` has a named failure mode with a reproduction; `mkdocs build --strict` passes; the page is in the nav.
- **Dependencies / risks:** must be revised alongside NUM-02/NUM-03 or it will document defects that no longer exist.

### [REL-04] Add a local diagnostics log and a "copy diagnostics" action

- **Severity:** P2
- **Effort:** M
- **Confidence:** high — verified: no logging, no crash capture, no feedback route.
- **Evidence:** `01-FINDINGS.md` [L-3], [J-3]. No `sentry`/`telemetry`/`analytics`, and no `logging` configuration in `src/`.
- **Problem:** the no-telemetry stance is right and worth keeping. But there is then *no* route by which the author learns a solver failed for a user, and no way for a user to report usefully — `solver.py` captures a traceback into `SolveResult` and it goes nowhere durable.
- **Proposed change:** a rotating local log in the per-user data directory recording solve failures (problem, method, tolerances, diagnosis from ARCH-01, traceback) — no personal data, never transmitted. A Help → "Copy diagnostics" action putting the last N entries plus version and platform on the clipboard, so a bug report can be pasted. Document it in the README's privacy section (SEC-03) so the log's existence is disclosed.
- **Acceptance criteria:** a failed solve appends one entry; the log rotates at a bounded size; the copied text contains version, platform, method and diagnosis and no filesystem paths outside the app's own directory; nothing is sent anywhere.
- **Dependencies / risks:** logging must never itself fail the app — reuse `progress.py`'s "a broken file is never fatal" discipline. Better after ARCH-01.

### [REL-05] Add `SECURITY.md`, `CONTRIBUTING.md` and `CITATION.cff`

- **Severity:** P3
- **Effort:** S
- **Confidence:** high — verified absent.
- **Evidence:** `01-FINDINGS.md` [K-3]. Absent: `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `ARCHITECTURE.md`, `CITATION.cff`, `.pre-commit-config.yaml`.
- **Problem:** `README.md` (1,016 lines) and `CHANGELOG.md` (1,028 lines) are thorough, so this is a gap in kind rather than volume. `SECURITY.md` matters most: after SEC-01 there should be a stated route for reporting the next one. `CITATION.cff` matters for an educational tool that may be cited in coursework or a paper.
- **Proposed change:** `SECURITY.md` with a reporting address and a scope statement (what is in scope: expression evaluation, file parsing; what is not: the user attacking their own machine). `CONTRIBUTING.md` covering the dev install, `pytest -n auto`, `ruff`, `mypy`, and the project's evident standard that a numerical claim ships with the test that verifies it. `CITATION.cff` with author, title, version, license. Optionally `ARCHITECTURE.md` — the module map in `00-INVENTORY.md` §2 can be lifted almost verbatim.
- **Acceptance criteria:** all three exist; GitHub renders the security policy and citation widget; `CONTRIBUTING.md` names the three checks CI runs.
- **Dependencies / risks:** none. Write `SECURITY.md` as part of the SEC-01 fix.

### [REL-06] Publish the docs

- **Severity:** P3
- **Effort:** S
- **Confidence:** high — the deliberate choice is recorded in the config.
- **Evidence:** `01-FINDINGS.md` [K-4]. `mkdocs.yml:11-12`: *"No site_url / repo_url: this is built and served locally. Add them, plus a deploy workflow, if the project is ever published."*
- **Problem:** the docs build under `--strict` in CI on every push and are then discarded. The API reference, the examples and (after REL-03) the method-limits page reach nobody who has not cloned the repo. The config anticipates this exactly.
- **Proposed change:** do what the comment says — set `site_url` and `repo_url`, add a `gh-pages` deploy step to the existing `docs` job on pushes to `main` (`mkdocs gh-deploy --force`), and link the published site from the README and from `pyproject.toml`'s project URLs.
- **Acceptance criteria:** pushing to `main` publishes; the README links it; `mkdocs build --strict` still passes with the new `repo_url` cross-references resolving.
- **Dependencies / risks:** publishing makes the docs public — worth confirming the author wants that before enabling. Do it after SEC-01, so the published docs do not describe a vulnerable parser.
