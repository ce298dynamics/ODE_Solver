# ODE Suite — Audit Summary

**Audited:** 2026-09-05 · `odesuite` 0.4.0 · branch `main` at `66e7491`
**Scope:** a from-scratch Python ODE library (6,763 LOC) and the PySide6 desktop
application built on it (32,283 LOC), containing a complete first-course ODE
curriculum.

---

## Is it releasable?

**Not today — but it is one fortnight of focused work away, and the reason is not
the mathematics.**

The numerics are the strongest part of this codebase, and I say that having tried
hard to break them. Every one of the eleven integrators converges at its
advertised order. Stiff performance matches published RADAU5 figures (Van der Pol
μ=1000 in 1,142 steps; Robertson to `t=1e11` in 239). Event times come back
accurate to machine precision — `5.55e-17` — at every tolerance. Symplectic
methods show bounded energy oscillation over 10,000 periods where RK4 drifts
monotonically, exactly as the theory says. Against SciPy the agreement is `1e-7`
or better on every non-chaotic problem in the catalogue. Coverage is 96.3% on the
library, 91.2% overall, across 3,125 tests with zero failures.

The blocker is a security defect, and there is exactly one.

## The single biggest risk

**Arbitrary code execution from a typed equation.** `odesuite_app/custom.py`
sandboxes user expressions by emptying `__builtins__` — a defence the author
clearly thought about, correctly, and which closes name lookup completely. It
does not close *attribute traversal from a whitelisted object*. Since `sin` is on
the function whitelist:

```
sin.__class__.__init__.__globals__["__builtins__"]   →  157 real builtins,
                                                        including __import__
```

I confirmed this reaches actual code execution with a canary file, through **both**
shipping UI paths: the Solver Lab's "type your own system" and the equation
editor. In the editor the payload executed and its return value silently became
the equation's right-hand side.

The practical threat model is narrower than a web app's — this is a local desktop
tool with no network input, and equations are normally typed by the person
running it. It is still P0 for two reasons: equations get *shared*, so "try this
equation" becomes a payload; and `odesuite` is packaged for PyPI, making
`custom.build` importable by code that may feed it untrusted input.

**The fix is prototyped and measured** (`02-EXPERIMENTS.md`, Experiment 11):
validate the expression's AST before sympy compiles it, rejecting `Attribute` and
`Subscript`. Against the payload set and the app's own equation shapes it blocks
**9 of 9** escapes and accepts **14 of 14** legitimate equations. Effort: under a
day.

## Shortest path to launch

**Five weeks**, along the critical path in `04-ROADMAP.md` §2:

1. **M1 — Correctness & safety (~2 weeks).** Write the failing regression tests
   first, then SEC-01, then four numerical fixes, then pin dependencies and gate
   coverage.
2. **M2 — Release blockers (~3 weeks).** Give
   `Solution` a structured diagnosis, and land the five honesty items together.

Deliberately **not** on that path: Unit 8 (the nonlinear curriculum, XL) and plot
text alternatives (L). Both matter — Unit 8 is the most valuable item in the whole
backlog — but making either a release gate moves the date by weeks. Ship on seven
honest units; land the eighth as its own release.

---

## What else the experiments found

Four defects that pass the current test suite, each with a measured number and an
identified cause:

| | |
|---|---|
| **Radau silently misses its tolerance by up to 100×** | Below `rtol=1e-9` the achieved error stops tracking the request: 54× at `1e-12`, 103× at `1e-13`, while DOPRI5 holds 1.8× across the same range. `success` is `True` throughout. Cause: `NewtonSettings(tol_factor=0.03)` terminates the stage solve at 3% of tolerance. Changing that one constant to `0.003` gives 0.8×. |
| **RODAS4 loses three orders of accuracy on any non-autonomous problem** | Order 4 down to `2.8e-11`, then collapses to order 0.98 and floors at `3.9e-13`. Not the Jacobian — supplying an analytic one changes nothing. It is the finite-differenced `∂f/∂t`, and `ODEProblem` gives no way to supply an exact one. On an autonomous problem the floor vanishes entirely. |
| **The Taylor method kills the interpreter** | `solve(problem, "taylor20")` on `y' = y·cos(t)` exits with code 127 — no traceback, no Python exception. `Jet.__array_priority__` plus `__rmul__ = __mul__` recurse until the C stack is exhausted. Unreachable from the GUI (the `supports_taylor` allowlist is correct — I verified all 18 entries), but reachable from the published library API. |
| **A fixed-step method that overflows spins for 13.7 seconds and blames the wrong thing** | Euler on a harmonic oscillator overflows, then retries the identical failing step **909,393 times** before reporting `exceeded max_steps` — when the driver already knows the state went non-finite. The step-halving response is structurally a no-op for a fixed-step method. |

And the headline **content** finding, which is not a defect so much as an absence:

**The nonlinear-systems curriculum does not exist.** `git grep -i` over all 35
lessons finds no mention of chaos, Lyapunov, limit cycles, bifurcation,
Hartman–Grobman, Poincaré–Bendixson or separatrices. Meanwhile the app
*implements* linearisation, eigenvalue classification and separatrices; *names*
Hopf and pitchfork bifurcations in slider tooltips; and *ships* Lorenz tagged
`chaotic`. A learner meets a Hopf bifurcation as a tooltip before being taught
what a bifurcation is. For an application whose differentiator is nonlinear ODEs,
Edwards ch. 6 having no unit is the gap.

---

## What is genuinely good, briefly

Worth stating because it changes what the remaining work costs.

- **The coefficient layer cannot be mistyped.** Radau's eigendecomposition comes
  from `numpy.linalg.eig` at import time; the Yoshida composition weights from a
  closed-form recursion. Neither is transcribed. `tests/test_tableaux.py`
  machine-checks rooted-tree order conditions to order 5 and asserts each
  method's order is *maximal*. This is why Experiment 1 found zero coefficient
  bugs — the highest-value bug class in this kind of app was designed out.
- **Convergence-order tests already exist.** The brief predicts they are usually
  absent. `tests/test_convergence.py` fits log(error) against log(h) across
  parametrised methods and problems.
- **The library/UI boundary is real and CI-enforced** — a dedicated job asserts
  `odesuite` imports no Qt, and a clean-venv wheel test re-checks it.
- **Zero TODO/FIXME/HACK** across `src/` and `tests/`. `ruff` and `mypy` clean.
  No dead code, no duplicated solvers, no competing state stores.
- **The pedagogy is careful.** Every misconception the brief lists is targeted.
  `pitfall` is a first-class note kind, used 34 times. Multiple-choice questions
  carry one reason *per option*, because — as `lessons/model.py` puts it — "the
  reason a wrong option was tempting is usually the thing the student actually
  got wrong". Answers are graded by substituting into the equation, with a third
  verdict "cannot tell" rather than a false "wrong".
- **The threading is right.** Under a simulated slider drag the GUI thread stayed
  free (5–6 ms median tick); superseded solves cancel at their next step boundary
  rather than running to completion.
- **A method was deleted rather than shipped wrong.** `rosenbrock.py:151-163`
  records that ROS3P's embedded error estimate vanished identically and that
  shipping it "would be silently wrong rather than slow". That is the standard
  the rest of the backlog should be held to.

One theme runs through the defects worth naming: **the code is more honest than
the interface.** `analysis.classify`'s docstring is scrupulous about
non-hyperbolic points — and the Phase Portrait renders "centre" in bold with no
caveat. `events.py` documents exactly how many crossings the default setting
misses — and nothing in the returned `Solution` says so. The `slopefields` lesson
teaches that `y' = y^{1/3}, y(0)=0` has two solutions — and the solver returns
`y ≡ 0` with a green "finished". The honesty exists; it just stops at the UI
boundary. Seven backlog items exist to carry it across.

---

## The deliverables

| File | Contents |
|---|---|
| `00-INVENTORY.md` | Module map, feature and math-content inventories, repo health, coverage |
| `01-FINDINGS.md` | 64 findings across lenses A–L, each evidenced |
| `02-EXPERIMENTS.md` | 12 experiments, methodology and numbers |
| `03-BACKLOG.md` | 57 items, all in the required format |
| `04-ROADMAP.md` | Milestones, critical path, release checklist, top 10, risks |

**A note on method.** Three of my own results were wrong and are corrected in
place rather than quietly dropped:

- Measuring convergence by absolute endpoint error made Euler look like order
  0.647 (it is 0.998).
- A hand-written Van der Pol that was both the wrong equation and missing its
  Jacobian made Radau look 1,000× slower than it is.
- **The startup finding [E-1] was measured while a parallel `pytest -n auto` was
  saturating all 14 cores.** It reported 14–17 s to a usable window; idle, it is
  **1.44 s**. Confirmed by reproducing the original numbers under a deliberate CPU
  load. PERF-01 is withdrawn and UX-01 drops to P3 — this was the audit's
  second-ranked item, so the correction matters.

All three were mine. The corrected methodology is stated at the top of
`02-EXPERIMENTS.md`. **Every wall-clock number in this audit should be read as an
upper bound unless it says the machine was idle**; step counts, error magnitudes
and convergence orders do not depend on load and are unaffected.
