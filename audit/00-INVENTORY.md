# Phase 1 — Orientation and Inventory

**Audit date:** 2026-09-05
**Repo:** `C:\Users\Ediz\documents\ODE_Solver` — `odesuite` 0.4.0, branch `main` at `66e7491`
**Scope of this document:** Phase 1 only (§2 of `ODE_AUDIT_BRIEF.md`). No judgments beyond
what the evidence forces; the lens-by-lens findings are Phase 2.

---

## 0. The brief's assumptions vs. what this repo actually is

The brief was written for a TypeScript/web application (`rk4.ts:41`, "bundle size",
"mobile Safari", `npm audit`, `dangerouslySetInnerHTML`). **This is not that.** It is a
Python 3.10+ project consisting of:

- **`odesuite`** — a from-scratch numerical ODE library (6,763 LOC, 24 modules), depending
  only on `numpy` and `scipy`.
- **`odesuite_app`** — a PySide6 desktop application (32,283 LOC, 68 modules) built on top
  of it, containing both a solver studio and a full first-course ODE curriculum.

Every web-specific lens in the brief (§E mobile/touch, §F reflow at 200% zoom, §H bundle
size / code splitting, §J CSP / XSS / `npm audit`) is therefore either **not applicable**
or must be **translated** to the desktop-Python equivalent. Where a lens translates, I will
translate it in Phase 2 and say so. Where it does not, I will mark it `N/A` with a reason
rather than inventing a finding to fill the slot.

### §0 table, filled in by inference

The brief requires these to be stated explicitly rather than assumed silently. **None of
these were given to me**; each is inferred from the artefact named.

| Field | Inferred value | Evidence for the inference |
|---|---|---|
| Repo path | `.` | given |
| Target audience | **Undergraduates in a first ODE course (MA 266 / Edwards–Penney–Calvis), plus self-learners.** Secondarily, numerical-methods learners. | `src/odesuite_app/lessons/__init__.py:78` — "The course, in the order Edwards, Penney and Calvis present it"; every `Unit` carries a `reference` like `"Edwards ch. 1"`; `pyproject.toml:32` classifier `Intended Audience :: Education` alongside `Science/Research` |
| Release target | **A pip-installable Python package (`odesuite`, MIT) plus a PyInstaller desktop executable.** No web target, no date evident. | `pyproject.toml:1-40`; `packaging/odesuite.spec`; `.gitignore:1-4` documents the PyInstaller rebuild command; `Development Status :: 4 - Beta` |
| Platforms that must work | **Linux + Windows, CPython 3.10 and 3.12** (tested); macOS is claimed by `Operating System :: OS Independent` but **is not in the CI matrix**. | `.github/workflows/ci.yml` `matrix.os: [ubuntu-latest, windows-latest]`, `matrix.python: ["3.10","3.12"]` vs. `pyproject.toml` classifiers listing 3.10–3.13 |
| Non-goals | **No PDEs as a subject** (two semilinear PDE *benchmarks* exist only as exponential-integrator test problems); **no accounts/backend/network**; **no telemetry**. | `src/odesuite/problems/__init__.py:793,841` (KS and Allen–Cahn exist purely as `SEMILINEAR` benchmarks); no HTTP/socket/`requests` import anywhere in `src/`; `src/odesuite_app/progress.py:3` — "This is the only thing the application stores on disk" |
| Team size / effort | **One person.** | `pyproject.toml` `authors = [{ name = "Ediz" }]`; `LICENSE` "Copyright (c) 2026 Ediz"; 35 commits, single author, 2026-08-17 → 2026-09-04 |

**Discrepancy worth recording now:** the classifier list advertises Python 3.11 and 3.13
and "OS Independent"; CI tests 3.10 and 3.12 on Linux and Windows only. Three of the five
advertised Python versions and macOS entirely are **claims without evidence**. Sized in
Phase 4.

---

## 1. Can it be built, run and tested? — yes, all three

The brief asks me to report blockers immediately. **There are none.** Everything runs.

### Toolchain

| Item | Value |
|---|---|
| Interpreter | `C:\Users\Ediz\AppData\Local\Programs\Python\Python310\python.exe` — CPython 3.10.11 |
| Package manager | pip; `odesuite` installed **editable** pointing at this tree |
| Build backend | `setuptools>=68`, PEP 621 metadata, version single-sourced from `odesuite.__version__` (`pyproject.toml:56`) |
| Lockfile | **none** — dependencies are floors only (`numpy>=1.24`, `scipy>=1.10`, `PySide6>=6.6`, …). See "Repo health" below. |
| Installed | numpy 2.2.6, scipy 1.15.3, sympy 1.14.0, PySide6 6.11.1, pyqtgraph 0.14.0, matplotlib 3.10.7, pytest 9.1.1, ruff 0.16.3, mypy 2.3.1 |

> **Note for anyone reproducing this audit:** `python` on this machine's `PATH` is the
> Windows Store stub and fails with *"Python was not found"*. Use the absolute path above,
> or `py -3.10`.

### Everything I ran, and what it did

| Command | Result |
|---|---|
| `python -m pytest tests/ -q -n auto` | **3125 passed, 19 skipped, 1 warning in 407.79s** (6m48s), exit 0 |
| `python -m ruff check .` | **All checks passed!** |
| `python -m mypy` | **Success: no issues found in 24 source files** (1 informational note, `events.py:182`) |
| `python -m odesuite_app --selftest` | **11/11 passed** — 5 solver families, 5 custom equations, 1 typesetting check |
| Headless construction of all 13 screens | **13/13 OK** (script: `/tmp/ode-audit/screens.py`) |
| `import odesuite` with no Qt | **no PySide/shiboken/pyqtgraph/matplotlib in `sys.modules`** — the architectural promise holds |

**All 19 skips are capability guards, not disabled tests** — each is a parametrised case
asking a method for something it structurally does not have. Full breakdown from
`pytest -rs`:

| Count | Reason | Location |
|---:|---|---|
| 6 | "…has no native dense output" (CashKarp, Euler, RK23, RK4, RKF45, Tsit5) | `test_tableaux.py:155` |
| 4 | "order-6 conditions are not tabulated" | `test_tableaux.py:96` |
| 4 | "Euler/RK4 has no embedded pair" | `test_tableaux.py:108,122` |
| 2 | "Euler/RK4 carries no embedded estimate" | `test_convergence.py:215` |
| 1 | "error reaches round-off immediately at this order" | `test_taylor.py:178` |
| 1 | "Linear system: no scalar particular solution to compare" | `test_symbolic.py:317` |
| 1 | "harvested_population has no elementary closed form" | `test_textbook.py:54` |

Notably the `importorskip("PySide6"/"sympy")` guards did **not** fire — the full app stack
was exercised. Neither did the BLAS-performance guard at `test_radau.py:223`.

The single warning is expected and is itself the assertion of a test:
`test_app_equation.py::test_starting_at_a_singularity_says_so` triggers
`RuntimeWarning: divide by zero` from a `lambdify`-generated function, which is the
condition that test exists to prove is reported to the user.

---

## 2. Module map and dependency direction

### The layering, as designed

```
                    ┌───────────────────────────────────────────┐
  odesuite_app      │ screens/ (13)   widgets/ (16)   theme.py   │  Qt
  (PySide6)         └──────────────────┬────────────────────────┘
                                       │
                    ┌──────────────────┴────────────────────────┐
                    │ state.py  ← the view-model / single source │
                    │ solver.py (SolveRunner, threaded)          │
                    └──────────────────┬────────────────────────┘
                                       │
        ┌──────────────┬───────────────┼──────────────┬──────────────┐
        │ catalog.py   │ symbolic.py   │ analysis.py  │ lessons/ (9) │  no Qt
        │ (28 problems)│ steps.py      │ systems.py   │ progress.py  │  (mostly)
        │              │ laplace.py    │ byhand.py    │ custom.py    │
        │              │ series.py     │              │ mathrender.py│
        └──────────────┴───────┬───────┴──────────────┴──────────────┘
                               │                    ↓ dsolve_worker.py (subprocess)
  ─────────────────────────────┼──────────────────────────────────────
                               │
  odesuite            ┌────────┴──────────────────────────────────┐
  (numpy + scipy      │ driver.solve  ← owns time, and only time  │
   only, never Qt)    │ _loop.py: StepPlanner / Recorder /         │
                      │           EventTracker / validation        │
                      └────┬─────────┬──────────┬─────────┬───────┘
                           │         │          │         │
                      steppers/  controllers  dense.py  events.py
                           │      (I/PI/Pred)             │
              ┌────────────┼───────────────┐              │
           erk.py  irk.py rosenbrock.py    │          problem.py
        symplectic.py taylor.py exponential.py        solution.py
                           │
                   linalg.py + newton.py  (Jacobians, LU, simplified Newton)
                           │
              stability.py  sensitivity.py  bvp/shooting.py  problems/
```

### Responsibilities, file by file

**Library core — `src/odesuite/` (6,763 LOC)**

| File | LOC | Responsibility |
|---|---:|---|
| `problems/__init__.py` | 1431 | Benchmark zoo: 30 factories + the `NONSTIFF`/`STIFF`/`ANALYTIC`/`DAE`/`SEPARABLE`/`SEMILINEAR`/`BVPS`/`TEXTBOOK` groupings |
| `bvp/shooting.py` | 454 | Multiple shooting; each shot is an ordinary `solve` call |
| `steppers/irk.py` | 391 | Radau IIA collocation + simplified Newton; split (`T`-diagonalised) and dense linear-solve paths |
| `tableaux.py` | 387 | Butcher tableaux **as data**; one generic ERK stepper consumes all of them |
| `steppers/taylor.py` | 362 | Jet arithmetic (all-orders forward AD) → arbitrary-order Taylor method |
| `_loop.py` | 348 | The bookkeeping `solve` delegates to: validation, `StepPlanner`, `Recorder`, `EventTracker` |
| `steppers/rosenbrock.py` | 333 | RODAS4; linearly-implicit, one LU per step |
| `linalg.py` | 305 | 4 Jacobian strategies (analytic / complex-step / sparse-coloured FD / dense FD), LU dispatch, `M·c − J` |
| `controllers.py` | 287 | `error_norm`, `initial_step_size` (Hairer II.4), I / PI / Gustafsson-predictive controllers |
| `events.py` | 282 | Sign-change bracketing on the step interpolant + Brent refinement; optional sub-step scanning |
| `driver.py` | 277 | `solve` — the loop, and nothing else |
| `dense.py` | 257 | 5 interpolant kinds + `DenseOutput` (binary-search segment lookup) |
| `sensitivity.py` | 214 | Forward sensitivities by internal differentiation (variational equations) |
| `newton.py` | 186 | Simplified Newton with convergence-rate monitoring; `JacobianPolicy` (staleness / refactorisation) |
| `steppers/symplectic.py` | 185 | Störmer–Verlet + Yoshida triple-jump composition (orders 4/6/8, *derived* not transcribed) |
| `steppers/exponential.py` | 184 | ETDRK4 with Kassam–Trefethen contour-integral φ-functions |
| `problem.py` | 184 | `ODEProblem`; mass matrices incl. singular (DAE); up-front `f`/`y0` validation |
| `stability.py` | 178 | `R(z)`, stability grids, two independent evaluation paths |
| `steppers/base.py` | 121 | The `Stepper` contract |
| `solution.py` | 121 | `Solution` / `Stats` |
| `steppers/__init__.py` | 92 | Method registry (`METHODS`, 21 names) |
| `__init__.py` | 93 | Public surface, 34 exports |
| `steppers/erk.py` | 84 | The single generic explicit RK stepper |
| `bvp/__init__.py` | 7 | Re-export |

**Application — `src/odesuite_app/` (32,283 LOC).** 7 lesson modules (10,897 LOC, 34% of
the app), 13 screens (5,378 LOC), 16 widgets (3,600 LOC), and a non-Qt logic layer:
`steps.py` (1607, symbolic narration), `symbolic.py` (1389, parse/solve/verify/grade),
`analysis.py` (782, phase-plane numerics), `catalog.py` (771), `laplace.py` (742),
`systems.py` (597), `progress.py` (529), `series.py` (475), `custom.py` (323),
`mathrender.py` (304), `solver.py` (287), `dsolve_worker.py` (262), `state.py` (221),
`byhand.py`, `equationmodel.py`, `richtext.py`, `theme.py`, `thumbnails.py`.

### Dependency direction — verified, not assumed

| Claim | Verdict | Evidence |
|---|---|---|
| `odesuite` never imports Qt | **HOLDS** | `import odesuite, odesuite.problems` → zero `PySide*`/`shiboken*`/`pyqtgraph`/`matplotlib` in `sys.modules`. Also enforced by a dedicated CI job (`ci.yml`, `library-only`) and re-checked against the built wheel in a clean venv (`ci.yml`, `package`) |
| `odesuite` never imports `odesuite_app` | **HOLDS** | `git grep odesuite_app -- 'src/odesuite/**'` → no matches |
| `lessons/` is content-only, no Qt | **HOLDS** | no `PySide6`/`pyqtgraph` import in `src/odesuite_app/lessons/**`. `lessons/model.py:3` also claims "no sympy" and that holds for `model.py`; `lessons/generate.py:190` imports sympy inside a function, which is the drill generator, not the content model |
| The solver core is testable headlessly | **HOLDS** | `tests/test_convergence.py` drives steppers directly in a fixed-step loop, bypassing `solve` entirely |
| **"Screens never talk to `odesuite` directly"** (`state.py:5`) | **DOES NOT HOLD** | 4 of 13 screens import the library directly: `screens/accuracy.py:35` (`from odesuite import make_stepper, solve`), `screens/stiffness.py:35,74,369`, `screens/portrait.py:270`, `screens/learn_problems.py:181` |

That last row is the only layering violation found, and it is a **documentation-vs-code
mismatch rather than a tangle** — the four screens that bypass `state` are precisely the
ones doing method-comparison and stability work that the view-model does not model. Sized
in Phase 2 §G.

---

## 3. Feature inventory

### 3a. Screens — 13 registered, 13 construct, 13 have tests

Status legend: `complete` = feature-complete and covered by tests; `partial` = works but a
named capability is missing.

| # | Screen | id | Shortcut | LOC | Status | Test file |
|---|---|---|---|---:|---|---|
| 1 | Home | `home` | `Ctrl+0` | 218 | complete | `test_app.py` |
| — | **Learning Hub** | | | | | |
| 2 | Course Map | `course` | `Ctrl+1` | 363 | complete | `test_sections.py` |
| 3 | Lessons | `lessons` | `Ctrl+2` | 1333 | complete | `test_lessons.py` (99 tests) |
| 4 | Solve Step by Step | `steps` | `Ctrl+3` | 208 | complete | `test_steps.py` (74 tests) |
| 5 | Laplace Transforms | `laplace` | `Ctrl+4` | 241 | complete | `test_laplace.py` (45 tests) |
| 6 | Methods by Hand | `byhand` | `Ctrl+5` | 252 | complete | `test_byhand.py` |
| 7 | Worked Problems | `worked` | `Ctrl+6` | 215 | complete | `test_app.py` |
| 8 | Unit Quiz | `quiz` | `Ctrl+7` | 536 | complete | `test_quiz.py` (24 tests) |
| — | **Solver Studio** | | | | | |
| 9 | Solver Lab | `lab` | `Ctrl+Shift+1` | 434 | complete | `test_app_lab.py` (31 tests) |
| 10 | Phase Portrait | `portrait` | `Ctrl+Shift+2` | 486 | **partial** — no bifurcation/continuation, no limit-cycle detection, no Poincaré section | `test_app_portrait.py` |
| 11 | Stiffness Explorer | `stiffness` | `Ctrl+Shift+3` | 577 | complete | `test_app_stiffness.py` |
| 12 | Method Race | `race` | `Ctrl+Shift+4` | 454 | complete | `test_app_stiffness.py` |
| 13 | Accuracy Lab | `accuracy` | `Ctrl+Shift+5` | 521 | complete | `test_app_accuracy.py` |

No stubs. No placeholder screens. No dead nav entries. Shortcut scheme is documented at
`app.py:62-72` and every binding is globally unique.

### 3b. Integrators — 21 registered names, 14 distinct methods

| Name(s) | Method | Order | Adaptive | Implicit | Mass/DAE | Interp. order | Coefficients live at |
|---|---|---:|---|---|---|---:|---|
| `euler` | Forward Euler | 1 | no | no | no | 3 (Hermite) | `tableaux.py` `EULER` |
| `rk4` | Classical RK4 | 4 | no | no | no | 3 (Hermite) | `tableaux.py` `RK4` |
| `rk23` | Bogacki–Shampine 3(2), FSAL | 3 | yes | no | no | 3 | `tableaux.py` `RK23` |
| `rkf45` | Fehlberg 4(5), local extrapolation | 5 | yes | no | no | 3 | `tableaux.py` `RKF45` |
| `cashkarp` | Cash–Karp 5(4) | 5 | yes | no | no | 3 | `tableaux.py` `CASHKARP` |
| `dopri5`, `rk45` | Dormand–Prince 5(4), FSAL | 5 | yes | no | no | **4 (native)** | `tableaux.py` `DOPRI5` + `_DOPRI5_P` |
| `tsit5` | Tsitouras 5(4), FSAL | 5 | yes | no | no | 3 | `tableaux.py` `TSIT5` |
| `rodas4` | RODAS4, L-stable, stiffly accurate | 4 | yes | **yes** | **yes** | 3 | `rosenbrock.py` `RODAS4` |
| `radau`, `radau5` | Radau IIA (3-stage), split solve | 5 | yes | **yes** | **yes** | 3 (collocation) | `irk.py` `_radau_iia_5()` — **closed form, not transcribed** |
| `radaudense` | Same, unsplit 3n×3n solve | 5 | yes | yes | yes | 3 | ditto |
| `verlet` | Störmer–Verlet | 2 | no (by design) | no | no | 3 | `symplectic.py` |
| `yoshida4/6/8` | Triple-jump composition | 4/6/8 | no (by design) | no | no | 3 | **derived** by `triple_jump_weights()` |
| `etdrk4` | ETDRK4, contour φ-functions | 4 | no | no | no | 3 | `exponential.py` |
| `taylor`, `taylor8/20/30` | Taylor series via jet arithmetic | 8/20/30 | yes | no | no | = order | **derived** — no coefficients at all |

**Two design decisions worth recording as strengths, because they eliminate the brief's
single highest-value bug class before it can occur:** Radau's `T`/`T⁻¹` come from
`numpy.linalg.eig` at import time (`irk.py:104-116`), and the Yoshida weights come from
the closed-form recursion (`symplectic.py:98-119`). Neither is transcribed, so neither can
be mistyped.

### 3c. Adaptivity, dense output, events, structure — present

| Capability | Present? | Where |
|---|---|---|
| Embedded-pair error estimation | yes, `e = b − b̂` used directly | `tableaux.py:88`, `erk.py:70` |
| Mixed tolerance `atol + rtol·max(|y_old|,|y_new|)`, RMS-normalised, per component | yes | `controllers.py:29-40` |
| Step controllers | I, PI (Gustafsson), **Predictive** (radau5's `FACL`/`FACR`/`QUOT2`) | `controllers.py` |
| Automatic initial step | yes — Hairer/Nørsett/Wanner II.4 two-stage | `controllers.py:44-80` |
| Step rejection, growth/shrink caps, safety factor | yes — `min_factor`, `max_factor`, `safety` | `controllers.py:88-91` |
| Minimum-step floor + honest failure message | yes, and it **distinguishes two causes** | `_loop.py:206-224`, `driver.py:150-160` |
| `max_steps` safety valve (default 1e6) | yes | `driver.py:55` |
| **Dense output / continuous extension** | yes — 5 interpolant kinds, incl. DOPRI5's free 4th-order and Radau's collocation polynomial | `dense.py` |
| **Rejected steps recorded and returned** | yes — `Solution.rejected` as `(t,h)` pairs | `solution.py:66-77` |
| Event detection | bracketed **on the interpolant**, refined by `brentq(xtol=1e-14)`; direction filtering; k-th-occurrence terminal events; optional sub-step scanning for even-numbered crossings | `events.py` |
| Stiff / implicit methods | Radau IIA + RODAS4 | `irk.py`, `rosenbrock.py` |
| Jacobians | analytic / complex-step / sparse-coloured FD / dense FD, Shampine-scaled, exactly-representable increment | `linalg.py` |
| Newton convergence checking + fallback | yes — rate monitoring, `θ/(1−θ)` remaining-error test, fresh-Jacobian retry | `newton.py`, `irk.py:317-327` |
| Symplectic / structure-preserving | Verlet, Yoshida 4/6/8; constant step **enforced** | `symplectic.py` |
| Backward integration (`t_end < t_0`) | yes, "supported everywhere in the library" | `problem.py:32`, `direction` threaded throughout |
| Complex-valued states | yes, including a Radau path that drops the conjugate shortcut | `problem.py:74`, `irk.py:196-206` |
| Higher-order → first-order reduction | yes, both numerically and symbolically | `symbolic.py:1201` `to_first_order`, `symplectic.py:56` `second_order_problem` |
| Mass matrices, incl. singular (index-1 DAE) | yes | `problem.py:154-176` |
| Forward sensitivities | yes | `sensitivity.py` |
| BVPs | multiple shooting | `bvp/shooting.py` |
| Cancellation / progress callback | yes — `callback(t,y,stats) -> bool` | `driver.py:80-98` |

### 3d. Symbolic and analytical layer

| Technique | Narrated step-by-step? | Where |
|---|---|---|
| Separation of variables | yes | `steps.py:442` `_separable` |
| Integrating factor (1st-order linear) | yes | `steps.py:567` |
| Exact equations | yes (with own detector, sympy can't be relied on to name it) | `steps.py:1306`, `_DETECTORS` at `steps.py:1605` |
| Bernoulli | yes | `steps.py:1453` |
| Homogeneous substitution | yes | `steps.py:1530` |
| Characteristic roots (nth-order const. coeff.) | yes | `steps.py:747` |
| Undetermined coefficients | yes | `steps.py:801` |
| Variation of parameters | yes | `steps.py:1059` |
| Cauchy–Euler | yes | `steps.py:1143` |
| Laplace transform / inverse | yes, separate module | `laplace.py` (742 LOC) |
| Linear systems by eigenvalues (distinct / complex / defective) | yes | `systems.py:300,317,366` |
| Nonhomogeneous systems, fundamental matrix, matrix exponential | yes | `systems.py:446,456,537` |
| Power series / recurrence / Frobenius | yes | `series.py` (475 LOC) |
| **Reduction of order** | **NO — absent from the entire repo** | `git grep -i "reduction of order"` → 0 hits |

Supporting machinery: parsing is **sympy `parse_expr` with an explicit whitelist**
(`symbolic.py:208`, `_SAFE_GLOBALS`, `_TRANSFORMATIONS`) — **not `eval`, not `exec`**;
`dsolve` runs in a **killable subprocess** with a 12s UI deadline
(`symbolic.py:62`, `dsolve_worker.py`); solutions are **substituted back into the
equation to verify** (`symbolic.py:842` `_verify`, `:868` `_verify_system`); answers are
graded by mathematics rather than string comparison (`symbolic.py:923` `check_answer`),
with a third verdict "cannot tell" rather than a false "wrong".

### 3e. Nonlinear / dynamical-systems tooling (`analysis.py`, 782 LOC)

| Capability | Present? | Where |
|---|---|---|
| Slope fields | yes | `analysis.py:101` |
| Vector fields | yes | `analysis.py:85` |
| Streamlines | yes | `analysis.py:151` |
| Nullclines | yes | `analysis.py:540` |
| Fixed-point finding | yes, multi-seed | `analysis.py:265` `find_fixed_points(seeds=11)` |
| Jacobian at a fixed point | yes | `analysis.py:216` |
| Eigenvalue classification (node/saddle/spiral/…) | yes, with a `NEUTRAL` category | `analysis.py:226`, constants at `:42-44` |
| Separatrices | yes | `analysis.py:649` |
| Phase line (1-D autonomous) | yes | `analysis.py:369` |
| Click-to-seed trajectories | yes | `analysis.py:556` `trajectory_through` |
| **Bifurcation tooling / continuation** | **NO** | no continuation code anywhere in `src/` |
| **Limit-cycle detection** | **NO** | — |
| **Poincaré map / section** | **NO** | — |
| **Lyapunov exponent estimation** | **NO** | — |

The library-level analysis is strong; the *dynamical-systems* layer above it (bifurcation,
limit cycles, Poincaré, Lyapunov) is entirely absent. Since the brief calls nonlinear
tooling "the app's differentiator", this is the largest single gap in the Studio half and
will be sized in Phase 2 §C.

### 3f. Problem catalogue — 28 entries, and the canonical systems the brief asks for

`catalog.py` exposes 28 problems over 28 tags. Against the brief's §C checklist:

| Canonical system | Present? | Key |
|---|---|---|
| Logistic | yes | `logistic` |
| Lotka–Volterra | yes | `lotka_volterra` |
| Van der Pol | yes (μ slider, log scale) | `van_der_pol` |
| Duffing | yes | `duffing` |
| Brusselator | yes | `brusselator` |
| Damped/driven pendulum | yes | `pendulum`, `forced_spring` |
| Robertson | yes, **both ODE and DAE form** | `robertson`, `robertson_dae` |
| Lorenz | yes | `lorenz` |
| **SIR** | **not in the catalogue** — but present as a `custom.py` preset (selftest: `PASS custom: SIR epidemic`) | — |
| **FitzHugh–Nagumo** | **NO** | — |
| Others present | HIRES, Oregonator, Kepler (×2), Pleiades, KS, Allen–Cahn, bouncing ball, 8 textbook models | |

---

## 4. Math-content inventory

### 4a. What the course covers — 7 units, 35 lessons

Extracted programmatically (`/tmp/ode-audit/inventory.py`), not read off by eye.

| Unit | Key | Reference | Lessons | Lesson keys |
|---|---|---|---:|---|
| First-order equations | `first-order` | Edwards ch. 1 | 6 | basics, slopefields, separable, linear, exact, substitutions |
| Models and numerical methods | `models` | Edwards ch. 2 | 5 | population, equilibria, motion, numerical, rungekutta |
| Second-order linear | `second-order` | Edwards ch. 3 | 6 | superposition, roots, undetermined, variation, cauchy, higher |
| Vibrations and forcing | `vibrations` | Edwards 3.4, 3.6–3.7 | 3 | free-vibration, forced-vibration, circuits |
| Laplace transforms | `laplace` | Edwards ch. 7 | 6 | transform, laplace, shifting, convolution, step-forcing, impulses |
| Linear systems | `systems` | Edwards ch. 4–5 | 6 | systems-intro, eigenvalues, complex-eigenvalues, repeated-eigenvalues, forced-systems, phase-portraits |
| Series solutions | `series` | Edwards ch. 8 | 3 | power-series, recurrence, frobenius |

**Totals:** 35 lessons · 177 notes (49 idea, 65 formula, 34 pitfall, 29 aside) ·
237 derivation passages · 68 worked examples · **172 practice questions**
(105 `Choice`, 67 `Solve`) · **42 drill templates**.

**Structural completeness of the lesson model** — every one of the 35 lessons has
`objectives`, `motivation`, `derivation`, `reference`, and at least one `Template`.
32/35 declare `prerequisites`. **18/35 have a `figure`**; the 17 without are: basics,
substitutions, population, superposition, roots, variation, higher, circuits, transform,
laplace, impulses, systems-intro, eigenvalues, repeated-eigenvalues, forced-systems,
recurrence, frobenius. 24 lessons link to the `steps` tool, 6 to `laplace`, 3 to `worked`,
2 to `byhand`.

That a `pitfall` note kind exists at all (`lessons/model.py:60`) and is used 34 times —
and that `Choice` questions carry *one reason per option* rather than one per question —
is direct evidence of misconception-targeting design. Phase 2 §D will check whether the
specific misconceptions the brief lists are the ones actually targeted.

### 4b. Topic coverage against a standard first course

Keyword-scanned across every lesson's title, summary, objectives, notes, derivation
passages and question prompts (`/tmp/ode-audit/topics.py`).

**Covered (36 topics):** existence & uniqueness; separable; integrating
factor; exact; Bernoulli; homogeneous substitution; slope/direction fields; autonomous
equations & phase line; Euler's method; Runge–Kutta; local vs. global truncation error;
logistic & population models; cooling/mixing; characteristic equation; Wronskian & linear
independence; undetermined coefficients; variation of parameters; Cauchy–Euler;
under/over/critically damped; resonance & beats; RLC circuits; Laplace transform;
Heaviside/unit step; Dirac delta & impulses; convolution; partial fractions; eigenvalue
method; complex eigenvalues; defective/repeated eigenvalues; matrix exponential;
fundamental matrix; node/saddle/spiral classification; power series; recurrence relations;
Frobenius & regular singular points; Bessel/Legendre.

**Missing entirely from the taught course:**

| Missing topic | Note |
|---|---|
| **Reduction of order** | Absent from the whole repo, not just the lessons. The only standard ch. 3 technique with no coverage at all. |
| The *names* "Lipschitz" and "Picard–Lindelöf" | `git grep -i lipschitz` and `picard` both return **zero hits repo-wide**. The *content* is taught correctly and well — `slopefields` states the ∂f/∂y-continuity form, and both classic counterexamples (`y'=y²` blow-up, `y'=y^{1/3}` non-uniqueness) appear as `pitfall` notes — so this is a vocabulary gap, not a knowledge gap. Corrected from an earlier draft of this table, which wrongly credited "Lipschitz". |
| **The entire nonlinear-systems unit (Edwards ch. 6)** | linearisation at a fixed point, Hartman–Grobman, Lyapunov stability, separatrices, limit cycles, Poincaré–Bendixson, bifurcation, chaos — **none of these words appear anywhere in `lessons/`**. |
| Fourier series / PDEs (Edwards ch. 9–10) | Consistent with the inferred non-goal; recording it as a boundary, not a defect. |

The nonlinear gap is the headline content finding of Phase 1, and it is *asymmetric* in a
specific way worth stating precisely:

- `analysis.py` **implements** linearisation, eigenvalue classification and separatrices.
- `catalog.py:172-173,213` **names** Hopf and pitchfork bifurcations in blurbs.
- `problems/__init__.py:242,302,1179` **names** limit cycles and saddle-node bifurcations
  in docstrings.
- The Lorenz attractor is in the catalogue and tagged `chaotic`.
- **The course never teaches any of it.** `git grep -i "chaos\|chaotic" -- src/odesuite_app/lessons/` returns nothing.

So a learner meets a Hopf bifurcation as a *slider hint* before ever being taught what a
bifurcation is. Unit 6 stops at linear systems; unit 7 goes to series. There is no unit
between them.

---

## 5. Repo health

### Signals that are unusually good

| Signal | Measurement |
|---|---|
| **TODO / FIXME / HACK / XXX** | **0** across `src/` and `tests/` (`git grep -nE 'TODO\|FIXME\|HACK\|XXX'` → 0) |
| Lint | `ruff check .` clean, with a **documented, reasoned** rule selection and per-file ignores (`pyproject.toml:96-127`) |
| Types | `mypy` clean on 24 modules; `py.typed` shipped (PEP 561) with the reason recorded (`pyproject.toml:70-72`) |
| Test suite | 3125 tests, 0 failures, ~6m48s parallel |
| **Convergence-order tests** | **present** — `tests/test_convergence.py`, 6 test functions × parametrised methods/problems, fitting log(err) vs log(h) with a round-off floor at ≈450·ε |
| **Machine-checked Butcher coefficients** | **present** — `tests/test_tableaux.py` evaluates rooted-tree order conditions to order 5 plus row-sum consistency, per tableau, and asserts the propagated order is *maximal* (i.e. that the method is not secretly lower order) |
| Cross-validation of a fast path against an oracle | `radaudense` exists solely so `tests/test_radau.py` can assert the split solve agrees to round-off |
| Commented-out code blocks | none found |
| Duplicate solver implementations | none — `byhand.py:9-12` explicitly delegates to the library stepper and `tests/test_byhand.py` asserts bit-for-bit agreement with `solve` |
| Dead code | none surfaced by ruff `F`; no unreferenced modules found |
| Build artefacts tracked in git | none (`dist/`, `site/`, caches all gitignored). 13 `figures/*.png` are tracked, which is intentional — they are regenerated by `benchmarks/run_all.py` and consumed by the docs |
| CI | real and comprehensive: 5 jobs — library-without-Qt (2 Pythons), ruff+mypy, full suite (2 OS × 2 Pythons) + selftest with artefact upload, wheel build + **clean-venv install test** + console-script check, `mkdocs build --strict` |

The brief predicts that convergence-order tests "are usually absent" and that transcription
errors in tableaux are "the single highest-value bug class". **Both are already defended
here**, by tests that exist for exactly that reason (`tableaux.py:14-21` says so
explicitly). That materially changes what Phase 3 should spend its time on: re-deriving
what `test_tableaux.py` already proves is low-yield, so my verification experiments should
target the things *no* existing test covers — tolerance obedience across a wide sweep,
energy drift over 10,000 periods, stiff wall-clock on the UI thread, pathological inputs,
and cross-checking against SciPy.

### Signals that are weak

| Signal | Measurement | Why it matters |
|---|---|---|
| **No lockfile / no upper bounds** | `pyproject.toml:44` — `numpy>=1.24`, `scipy>=1.10`, `PySide6>=6.6`, `sympy>=1.12`, all floors only. No `requirements.txt`, no lock. | The build is not reproducible. `numpy` 2.x already broke API for many projects; `sympy` behaviour changes between minors and this app depends on `dsolve`/`classify_ode` *naming* techniques (`steps.py:82-91`). A `sympy` bump can silently change which technique is narrated. |
| **No coverage measurement** | `pytest-cov` not in `[dev]`, not in CI, no `.coveragerc`. *Resolved during the audit:* installed into the interpreter (not the repo) at the user's instruction and measured — see below. | The tool was absent, so the project itself has never had a coverage number. |
| **Advertised platforms exceed tested ones** | classifiers claim 3.10–3.13 + OS Independent; CI runs 3.10/3.12 on Linux/Windows | macOS and 3.11/3.13 are untested claims. |
| ~~**Startup latency**~~ | **RETRACTED — my measurement error.** Reported as ~14–17 s to a window and ~27–31 s of process time. Those runs were made **while a parallel `pytest -n auto` was saturating all 14 cores**. | Re-measured idle: **1.44 s** to a window, **3.5 s** process (6.3 s cold). Imports: sympy 0.40s, scipy 0.35s, pyqtgraph 0.29s, matplotlib 0.29s, PySide6 0.09s, `MainWindow()` 0.40s. Cause confirmed by reproducing the original figures under a deliberate CPU load (sympy 7.19s vs 7.02s reported). **Not a defect.** See `01-FINDINGS.md` [E-1]. |
| **No `CONTRIBUTING`, `SECURITY`, `ARCHITECTURE`, `CITATION.cff`, pre-commit** | all absent | `README.md` is 1016 lines and `CHANGELOG.md` 1028, so documentation *volume* is not the problem; the missing files are the collaboration/citation surface. |
| **No docs deployment** | `mkdocs.yml:11-12` — "No site_url / repo_url: this is built and served locally" | Docs build in CI (`--strict`) but are never published. |
| Stale local artefacts | `dist/` holds `odesuite-0.3.0` wheels while the source is 0.4.0 | Untracked and gitignored; cosmetic, but a stale wheel is an easy thing to install by accident. |

### Test coverage — measured

`pytest-cov` 7.1.0, full suite under `-n auto`, 3125 passed / 19 skipped.

| Area | Statements | Covered | % |
|---|---:|---:|---:|
| **LIBRARY** `src/odesuite` | 2,542 | 2,448 | **96.3%** |
| **APP** `src/odesuite_app` | 10,145 | 9,121 | **89.9%** |
|   app `lessons/` | 289 | 283 | 97.9% |
|   app `screens/` | 3,513 | 3,151 | 89.7% |
|   app `widgets/` | 2,553 | 2,362 | 92.5% |
|   app logic (rest) | 3,790 | 3,325 | 87.7% |
| **TOTAL** | **12,687** | **11,569** | **91.2%** |

Least-covered files with ≥25 statements: `odesuite_app/cli.py` 50.0% (60 missed),
`odesuite_app/dsolve_worker.py` 57.7% (44), `odesuite_app/thumbnails.py` 74.0% (20),
`odesuite_app/solver.py` 80.3% (27), `odesuite/problem.py` 81.2% (16),
`screens/accuracy.py` 81.7% (61), `screens/home.py` 82.9% (20),
`widgets/plotpanel.py` 83.6% (46), `screens/stiffness.py` 84.7% (55).

Only five library files sit below 95%: `problem.py` 81.2%, `tableaux.py` 90.0%,
`stability.py` 92.1%, `bvp/shooting.py` 92.8%, `events.py` 94.1%. For a
hand-written numerics library, 96.3% is a strong figure.

### History

35 commits, single author, **2026-08-17 → 2026-09-04** (19 days). Distribution:
204 file-touches under `src/odesuite_app`, 62 under `src/odesuite`. Commit messages are
prose describing intent ("A drill for every lesson, and twelve figures that move"),
not mechanical. Nothing looks abandoned or half-migrated.

### Contradictions and half-migrations — searched for, and what turned up

The brief asks specifically for "two implementations of the same solver, two state stores".

- **Two Radau linear-solve paths** (`split`, `dense`) — *deliberate*, documented at
  `irk.py:19-32`, and the second exists to validate the first. Not a duplication defect.
- **Two Robertson entries** (`robertson`, `robertson_dae`) — *deliberate*, ODE and DAE
  formulations of the same chemistry.
- **`ROS3P` removed rather than shipped** — `rosenbrock.py:151-163` records that its
  embedded pair produced an identically-vanishing error estimate and that shipping it would
  be "silently wrong rather than slow". This is a removal made for the right reason and
  documented in place.
- **One state store**, `state.SessionState`, with a documented rationale
  (`state.py:1-13`). No competing store found.
- **The only genuine mismatch found** is the `state.py:5` claim that screens never touch
  `odesuite` directly, contradicted by 4 screens (§2 above).

---

## 6. What I could not verify in Phase 1

Recorded here so it does not get lost; each is scheduled.

| Item | Why not yet | Scheduled |
|---|---|---|
| ~~Test coverage % (core vs UI)~~ | **RESOLVED** — `pytest-cov` 7.1.0 installed at the user's instruction; full suite re-run under coverage. Results below. | done |
| Whether the app is usable *interactively* | Every measurement here is under `QT_QPA_PLATFORM=offscreen`. Frame drops, slider latency and pinch/drag cannot be measured offscreen. | Phase 3 §10, on-screen |
| ~~Content provenance (§K)~~ | **RESOLVED** — the author states all content is original; the Edwards references are chapter pointers for the reader, not transcriptions. No longer a release blocker. | done |
| macOS behaviour | no macOS available | will be reported as an untested claim, not a defect |
| Real numerical accuracy of the solvers | needs the Phase 3 experiments | Phase 3 |

---

## 7. Phase 1 verdict

The premise the brief is written against — a plausible UI over numerics of unknown
quality — **is not this repo's situation**. The numerics core is the strongest part of the
codebase: coefficient-level order conditions are machine-checked, convergence order is
measured, the fast Radau path is validated against an oracle, structure-preserving methods
enforce their own constant-step requirement, and two whole families of coefficients are
*derived at import time* specifically so they cannot be mistyped. Lint, types, CI and the
test suite are all clean and genuinely thorough.

The three things Phase 1 surfaces as most likely to matter are, in order:

1. **The nonlinear-systems curriculum does not exist.** The tooling for it does
   (`analysis.py`), the vocabulary appears in slider hints and docstrings, and the app's
   own catalogue tags a problem `chaotic` — but Edwards ch. 6 is simply not taught. For an
   app whose differentiator is nonlinear ODEs, that is the gap.
2. ~~**~15 s to a usable window, ~30 s of process time.**~~ **Retracted** — measured on a
   machine saturated by a parallel test run. It is 1.44 s idle. Not a defect; see the
   Startup row above and `01-FINDINGS.md` [E-1]. Its place on this list is taken by
   **an explicit method grinding for ~17 s before failing on a stiff problem**, which was
   re-verified idle and does hold.
3. **No lockfile, and a hard behavioural dependency on sympy's `classify_ode` naming.**
   The build is not reproducible and an upstream minor version can change what the app
   teaches. *(Partly addressed: `sympy<2` and `PySide6<7` are now capped and `pip-audit`
   runs in CI; the `classify_ode` coupling itself remains, as SYM-04.)*

Nothing found in Phase 1 is a correctness blocker. Whether that survives Phase 3's
experiments is the question the rest of this audit exists to answer.

> **It did not.** Phase 2 found one **P0**: the expression sandbox in
> `odesuite_app/custom.py` can be escaped by attribute traversal from a
> whitelisted sympy function, giving arbitrary code execution from a typed
> equation, reachable from two shipping UI paths. See `01-FINDINGS.md` §J and
> `02-EXPERIMENTS.md` Experiment 11. Phase 3 also found a hard interpreter
> crash in the Taylor method and three quantified accuracy/honesty defects.
> The numerics verdict above stands — every integrator matched its claimed
> order — but "no correctness blocker" was a Phase 1 statement, not a final one.
