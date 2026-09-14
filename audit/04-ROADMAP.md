# Phase 5 — Roadmap and Release Gate

Durations assume the **one part-time developer** inferred in `00-INVENTORY.md` §0.
"Week" means a working week of focused effort, not elapsed calendar time.

---

## 1. Milestones

### M1 — Correctness & safety · ~2 weeks · *nothing ships wrong*

Everything here is either a way for the app to hurt the user's machine, kill
itself, or state a falsehood about its own numerics.

| ID | Title | Effort |
|---|---|---|
| **SEC-01** | Validate the expression AST before sympy compiles it | M |
| TEST-01 | Regression tests for every defect in this audit | M |
| NUM-01 | Stop `Jet` recursing into an interpreter crash | S |
| NUM-02 | Fix Radau's tight-tolerance shortfall | S |
| NUM-03 | Fix RODAS4's first-order floor on non-autonomous problems | M |
| NUM-04 | Fail a fixed-step method immediately when it goes non-finite | S |
| NUM-07 | Expose `∂f/∂t` on `ODEProblem` | S |
| NUM-08 | Wrap exceptions raised by the user's RHS at `t0` | S |
| SEC-02 | Pin dependencies and add `pip-audit` to CI | S |
| TEST-02 | Add a coverage gate to CI | S |
| REL-05 | Add `SECURITY.md`, `CONTRIBUTING.md`, `CITATION.cff` | S |

**Ordering rationale.** TEST-01 comes *first*, not last: each regression test is
written against the reproduction already in `02-EXPERIMENTS.md` and must fail on
`66e7491`, so every subsequent fix is demonstrably the thing that closed it.
SEC-01 is the only P0 and gates any public distribution. NUM-07 lands before
NUM-03 finishes so the Rosenbrock fix has an exact `∂f/∂t` to prefer. SEC-02
before anything else changes behaviour, so the build becomes reproducible while
it is still known-good.

**Exit:** all P0 and all numerics-correctness P1/P2 closed; CI green with a
coverage gate; every defect in this audit has a test that fails without its fix.

---

### M2 — Release blockers · ~3 weeks · *fit to hand to a stranger*

The app is correct after M1. It is not yet something you would give an
undergraduate without standing next to them.

> **Correction.** This milestone originally led with PERF-01 and UX-01 on the
> strength of a startup measurement that was taken while a parallel test run was
> saturating the machine. Re-measured idle, the window is up in 1.44 s rather
> than 14–17 s. PERF-01 is withdrawn and UX-01 is P3; see the correction in
> `03-BACKLOG.md`. M2 now leads with ARCH-01, which is what actually unblocks
> the rest of it.

| ID | Title | Effort |
|---|---|---|
| ARCH-01 | Make `Solution` carry a structured diagnosis | M |
| NUM-05 | Report a tolerance shortfall instead of claiming success | M |
| PERF-02 | Detect stiffness and bail out in <1 s instead of 20 s | M |
| DYN-04 | Caveat non-hyperbolic classifications at the UI | S |
| DYN-05 | Detect and warn about missed event crossings | M |
| NUM-06 | Warn when uniqueness is not guaranteed | M |
| SYM-01 | Report the interval of validity with every symbolic solution | M |
| REL-02 | Test the platforms actually advertised | S |
| REL-03 | Write "when each method fails" | M |
| SEC-03 | Document the privacy position in the README | S |
| TEST-04 | Cover `dsolve_worker.py` and `solver.py` | M |

**Ordering rationale.** ARCH-01 first: it must precede NUM-05, PERF-02 and
DYN-05, all of which need somewhere structured to put a diagnosis, so it is the
one item here that unblocks others. The five honesty items
(NUM-05, NUM-06, DYN-04, DYN-05, SYM-01) ship together deliberately: they are one
change of posture, and landing them piecemeal makes the app inconsistent about
what it will and will not vouch for. REL-03 last in this milestone, because it
documents the limits that M1 and M2 have just changed.

**Exit:** window visible in under 4 s; no screen states a result more confidently
than the numerics justify; macOS and every advertised Python version green.

---

### M3 — Quality bar · ~6 weeks · *the product it is trying to be*

| ID | Title | Effort |
|---|---|---|
| **PED-01** | Write Unit 8 — nonlinear systems and phenomena | XL |
| DYN-01 | Add a parameter-continuation / bifurcation-diagram tool | L |
| DYN-02 | Add limit-cycle detection and a Poincaré section | L |
| DYN-03 | Add Lyapunov-exponent estimation with an honest error bar | M |
| UX-04 | Show the predictability horizon on chaotic systems | M |
| PED-04 | Add FitzHugh–Nagumo and promote SIR to the catalogue | S |
| PED-02 | Add figures to the 17 lessons that have none | L |
| A11Y-01 | Give every interactive control an accessible name | M |
| A11Y-02 | Give every plot a text alternative and a data table | L |
| SYM-02 | Add reduction of order | M |
| SYM-04 | Cut the classifier's dependence on sympy hint strings | M |
| UX-02 | Save and restore the full session | M |
| TEST-03 | Add property-based tests | M |

**Ordering rationale.** This milestone closes the gap the audit's headline
finding names: the app's differentiator is nonlinear ODEs and it neither teaches
nor tools them. PED-04 early — two catalogue entries are cheap and become
teaching material for everything after. DYN-01/02/03 before PED-01's lessons 5
and 6, so those lessons can link to working tools; lessons 1–4 of Unit 8 can be
written in parallel against `analysis.py` as it stands. UX-04 needs DYN-03's
exponent. SYM-04 belongs here rather than M1 because it is insurance against a
future sympy release, not a present defect.

**Exit:** Unit 8 shipped and structurally equal to the other seven; bifurcation,
limit-cycle and Lyapunov tools working and taught; every control has an
accessible name; every plot has a text alternative.

---

### M4 — Post-launch · ongoing

| ID | Title | Effort |
|---|---|---|
| PED-03 | Add a spaced-review queue driven by existing progress data | M |
| PED-05 | Teach why the numerical answer to `y'=y^{1/3}` is not the whole story | S |
| PED-06 | Add a "when this method fails" note to every method lesson | M |
| PED-07 | Name Lipschitz and Picard–Lindelöf | S |
| PED-08 | Flag a discontinuous RHS from the rejection pattern | M |
| UX-03 | Surface `as_code()` as a visible "copy reproducing code" button | S |
| UX-05 | Throttle replots to one per frame | S |
| UX-06 | Remove the duplicate `taylor` alias | S |
| A11Y-03 | Distinguish separatrices by dash pattern as well as colour | S |
| A11Y-04 | Make rendered maths follow the OS text scale | M |
| ARCH-02 | Correct the `state.py` layering docstring | S |
| ARCH-03 | Delete `radaudense` from the user-facing method list | S |
| ARCH-04 | Remove stale artefacts and the unused `slow` marker | S |
| ARCH-05 | Collapse the five background-job runners | M |
| PERF-03 | Hoist the ERK stage buffer out of the step loop | S |
| DYN-06 | Remove the unused `streamlines` resolution knobs | S |
| REL-04 | Add a local diagnostics log and "copy diagnostics" | M |
| REL-06 | Publish the docs | S |
| TEST-05 | Add a performance regression gate | M |

Several of these are S-effort and could be pulled forward into any milestone with
spare capacity — ARCH-02, ARCH-03, ARCH-04, UX-06, DYN-06 and PED-07 are each
under two hours and independent of everything else.

---

## 2. Critical path

The chain that determines the earliest possible release:

```
TEST-01 (write failing tests)          M   ✓ done
   └─> SEC-01 (AST validation)         M   ✓ done  ← the P0; gated distribution
          └─> REL-05 (SECURITY.md)     S   ✓ done  ← needed before publishing
   └─> NUM-07 (∂f/∂t on ODEProblem)    S   ✓ done
          └─> NUM-03 (RODAS4 fix)      M   ✓ done
   └─> SEC-02 (pin + audit)            S   ✓ done
          └─> TEST-02 (coverage gate)  S   ✓ done
                 └─> REL-02 (macOS + 3.11/3.13 in CI)   S
                        └─> ARCH-01 (structured diagnosis) M   ← M2 starts here
                               └─> NUM-05, PERF-02, DYN-05
                                      └─> REL-03 ("when each method fails")  M
```

**M1 is closed.** What remains on the path is REL-02, then ARCH-01 and the items
that depend on it. **Remaining length ≈ 3 weeks**, down from 5.

PERF-01 and UX-01 were on this path and are not any more — see the correction at
the head of M2. Removing them takes an M and an S off the chain, which is most of
the difference.

Two things are *not* on it and should not be allowed onto it:

- **PED-01 (Unit 8) is XL and does not gate a release.** The app ships today with
  seven honest units; it should not wait on an eighth. It is the most valuable
  item in the backlog and the one most likely to slip a date if made a blocker.
- **A11Y-02 (plot text alternatives) is L.** Genuinely important, and if it is
  made a release gate the date moves by a fortnight. Decide it as a policy
  question (see the risk register), not by default.

The single hard dependency is **SEC-01 before any public distribution** — PyPI,
a shared executable, or a link to the docs. Everything else on the path is a
quality gate the author can choose to relax.

---

## 3. Release checklist

Binary go/no-go. Every line must be checkable by a command or a named artefact.

**Correctness**
- [ ] `pytest tests/ -q -n auto` green on ubuntu + windows + macOS, Python 3.10 / 3.11 / 3.12 / 3.13
- [ ] `ruff check .` clean
- [ ] `mypy` clean
- [ ] `python -m odesuite_app --selftest` reports 11/11 (or its current full count)
- [ ] library coverage ≥ 95%, total ≥ 88%, enforced by CI
- [ ] every integrator's observed convergence order within 0.15 of claimed, on both a linear and a non-autonomous problem (`tests/test_convergence.py`)
- [ ] every adaptive integrator's achieved/requested error ratio ≤ 5 across `rtol` from `1e-3` to `1e-12`
- [ ] stiff baselines within 25% of `benchmarks/baseline.json` (radau: VdP μ=1000 ≤ 1428 steps, Robertson-1e11 ≤ 299, HIRES ≤ 178, OREGO ≤ 1184)

**Safety**
- [ ] **all P0 closed** — currently: SEC-01
- [ ] `tests/test_security.py` green: 9 escape payloads rejected through both entry points, canary absent, 14 legitimate equations accepted
- [ ] `pip-audit` reports no HIGH or CRITICAL advisory
- [ ] no `eval`/`exec`/`compile` on any user-input path (`git grep` clean)
- [ ] no process-terminating failure reachable from any public API (NUM-01)

**Honesty** — the gate this project specifically needs
- [ ] no screen reports `success` for a solve whose tolerance was not met
- [ ] non-hyperbolic equilibria are labelled as linearisation-only
- [ ] chaotic systems show a predictability horizon, or the default view stays inside it
- [ ] `docs/limits.md` exists and names a failure mode with a reproduction for every method in `METHODS`

**Build & release**
- [ ] `python -m build` byte-identical across two runs on one machine
- [ ] `twine check dist/*` clean
- [ ] wheel installs into a clean venv and solves without Qt (already in CI)
- [ ] lockfile committed and one CI leg installs from it
- [ ] PyInstaller executable builds and its `--selftest` passes
- [ ] version bumped in `odesuite.__version__`; `CHANGELOG.md` has a dated section; tag pushed

**Accessibility**
- [ ] every focusable widget has a non-empty `accessibleName()` (tree-walking test)
- [ ] every plot has a text alternative *(policy decision — see Risk 3)*
- [ ] contrast: all text and series colours ≥ 4.5 / 3.0 AA in both themes *(currently passing)*
- [ ] no meaning carried by colour alone *(markers done; separatrices A11Y-03)*

**Docs & licensing**
- [ ] `LICENSE` present, MIT, and `license-files` declared *(currently true)*
- [ ] content provenance documented as original in the README *(author confirmed; not yet written down)*
- [ ] `SECURITY.md`, `CONTRIBUTING.md`, `CITATION.cff` present
- [ ] `mkdocs build --strict` passes
- [ ] README states what is stored on disk, where, and how to delete it

**Operations**
- [ ] local diagnostics log writes on a failed solve and rotates
- [ ] "copy diagnostics" produces a pasteable report with version and platform
- [ ] rollback tested: previous version installs cleanly over the new one and reads the current `progress.json`

---

## 4. Definition of done

An issue in this project is done when **all** of the following hold. This is
written to match the standard the codebase already sets for itself — see
`steppers/rosenbrock.py:151-163`, where a method was removed rather than shipped
with an unverifiable error estimate.

1. **The change is covered by a test that fails without it.** For a numerical
   change, the test asserts a *number* — an observed order, an error ratio, a
   step count — not merely that the code runs.
2. **A claim in a docstring is backed by a test or is not made.** If the
   docstring says a method is fifth order, `test_convergence.py` measures it.
3. **`ruff`, `mypy` and the full suite are green**, and coverage has not fallen.
4. **Any behavioural change is in `CHANGELOG.md`** under the right heading, with
   removals under Removed.
5. **The reason is recorded where the next reader will find it** — in a comment
   at the code, not only in a commit message. This project already does this
   unusually well; it is the practice most worth protecting.
6. **If the change alters what the app tells a learner**, the corresponding lesson
   or blurb is updated in the same commit. The `y'=y^{1/3}` case is the standing
   example of what happens otherwise: the lesson and the tool disagreed.
7. **No new magic number** without a named constant and a comment saying what it
   trades.

---

## 5. Top 10 — if only ten of these are ever done

Ranked by user impact ÷ effort, with the reason each earns its place.

| # | ID | Why this one |
|---|---|---|
| 1 | **SEC-01** | The only P0. Arbitrary code execution from a typed equation, reachable from two shipping UI paths, demonstrated with a canary. The fix is prototyped and measured: 9/9 escapes blocked, 14/14 legitimate equations accepted. Nothing should be distributed until it lands. |
| 2 | ~~**PERF-01**~~ → **PERF-02** | PERF-01 is withdrawn: its 15-seconds-of-blank-screen premise was a measurement taken on a saturated machine, and the real figure is 1.4 s. Its place goes to **PERF-02** — an explicit method on a stiff problem really does grind for ~17 s before failing, re-verified idle, and a learner watches a spinner for all of it to be told something a heuristic could say in under a second. |
| 3 | **TEST-01** | Every defect in this audit passes the current 3,125-test suite. Without a failing test each, they all come back. Write these first and the rest of M1 becomes verifiable. |
| 4 | **NUM-02** | A one-constant change turns a silent 54× tolerance shortfall into 0.8×. The cheapest correctness win here, and it is an honesty defect: the solver reports success while missing the tolerance by two orders of magnitude. |
| 5 | **PED-01** | The app's stated differentiator is nonlinear ODEs and it does not teach them. It implements linearisation, names Hopf bifurcations in tooltips and ships Lorenz tagged `chaotic` — while Edwards ch. 6 has no unit. XL, and worth it. |
| 6 | **NUM-01** | A documented public method kills the interpreter — no exception, no traceback — on `y' = y·cos(t)`. Unreachable from the GUI, but `odesuite` ships as a library and this is the most ordinary non-autonomous RHS there is. S effort. |
| 7 | **NUM-03** | RODAS4 silently loses three orders of accuracy on every non-autonomous problem and no caller can work around it. The cause is a single finite-difference step size. |
| 8 | **DYN-01** | The bifurcation diagram is the highest-value missing tool: every primitive it needs already exists and works, and it makes three shipped models (Duffing, Brusselator, harvested population) teach something they currently only hint at. |
| 9 | **ARCH-01** | Small, and it unblocks four other items. Every diagnostic the solver produces is currently a prose string, so no caller can react to *why* a solve failed. |
| 10 | **A11Y-02** | The product is graphical and a non-visual learner currently gets nothing from half of it. It is also the missing verbal leg of the rule of four the app otherwise honours — the summaries help sighted learners too. |

Everything else — including all 17 P3 items — can wait indefinitely without the
app being wrong, unsafe, or dishonest.

---

## 6. Risk register

### Risk 1 — Unit 8 (PED-01) is XL and becomes the reason nothing ships

**Likelihood: high. Impact: high.** It is the most valuable item in the backlog,
the most interesting to work on, and the one with no natural stopping point:
six lessons, each needing objectives, motivation, derivation passages, five
notes, two worked examples, four questions, a template and a figure to match the
existing 35. Its lessons 5 and 6 also depend on DYN-01 and DYN-02, so it can
absorb three other L-items with it.

**Mitigation.** Keep it out of M1 and M2 entirely — it is explicitly off the
critical path above. Ship the release on seven honest units. Then land Unit 8 as
its own release, lessons 1–4 first (they need only today's `analysis.py`), with
5–6 following DYN-01/DYN-02. Set a per-lesson definition of done equal to the
existing structural tests, so "finished" is a green test rather than a judgment.

### Risk 2 — The security fix (SEC-01) over-restricts and breaks real equations

**Likelihood: medium. Impact: high.** An AST allowlist that rejects
`Attribute` and `Subscript` is the right shape, but the app's own equation corpus
is wide: `sec(t)` is whitelisted specifically because variation of parameters is
taught on it; `Max(0, y)`, `atan2(y, x)` and `3*t^2 + 1` all have to keep
working; the `symbolic` path rewrites derivatives into tokens before parsing, so
the validator sees text no user typed. A too-strict validator turns a P0 fix into
a functional regression, and the failure mode is a student's equation being
rejected with a security error.

**Mitigation.** The acceptance criteria already require all 14 legitimate forms to
pass, and the prototype in Experiment 11 clears them. Extend that list with every
entry in `custom.EXAMPLES` and `symbolic.EXAMPLES` and every equation appearing in
the 35 lessons and 42 templates before merging — that corpus is enumerable
programmatically. Run the validator over it in CI as a permanent test. On the
`symbolic` path, validate *after* `_rewrite_derivatives` with the tokens
permitted, and test that specific ordering.

### Risk 3 — Accessibility slips from "planned" to "never", quietly

**Likelihood: medium. Impact: medium-high.** A11Y-01 and A11Y-02 sit in M3 behind
Unit 8 and three L-effort tooling items. There is no external forcing function —
no procurement review, no legal requirement stated for this project — and the
app's contrast and colour-independence are already good enough that the gap is
easy to believe is smaller than it is. Today a screen-reader user gets one widget
(`MathLabel`) done well and nothing else, and there is no text alternative for
any plot.

**Mitigation.** Make it a policy decision now rather than a default. Either put
"every plot has a text alternative" on the release checklist and accept the date
moving by roughly a fortnight, or strike it from the checklist and state plainly
in the README that the app is not currently usable without sight. Both are
defensible; drifting between them is not. In either case land A11Y-01 in M2 — it
is M-effort, the tree-walking test makes it self-enforcing, and it prevents the
gap widening as screens are added.
