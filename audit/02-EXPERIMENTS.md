# Phase 3 — Verification Experiments

Every number here was produced by a script under `C:\Users\Ediz\AppData\Local\Temp\ode-audit\`
(`/tmp/ode-audit/` in the Bash tool's view) run against the **installed editable
package**, i.e. the shipping code. Interpreter: CPython 3.10.11, numpy 2.2.6,
scipy 1.15.3, Windows 11.

Scripts: `exp1e.py` (order), `exp1_rodas2.py` (RODAS4 floor), `exp2.py`/`exp2b.py`/`exp2c.py`
(tolerance), `exp3b.py` (stiff + SciPy), `exp4.py`/`exp4b.py` (energy, fixed-step failure),
`exp5.py` (SciPy non-stiff), `exp6.py` (pathological), `exp789.py` (equilibria, events, chaos),
`exp10.py` (UI stress), `exp_sec*.py` (sandbox), `exp_contrast.py` (WCAG).

**Two methodological notes up front**, because both changed the answers:

1. **Absolute endpoint error is the wrong measure for order.** On `y'=-2y` over
   `[0,5]` the exact solution at `t=5` is `4.5e-5`, so absolute error saturates
   and a naive fit reports Euler at order **0.647**. Using *relative* error, and
   the *maximum over the trajectory* rather than the endpoint alone (endpoint
   error can pass through zero as `h` varies, making `log2(e_i/e_{i+1})`
   meaningless), Euler comes out at **0.998**. Every "failure" in my first pass
   was an artefact of the measure, not a defect in the library.
2. **Order must be read at the finest usable `h`.** Order is an `h→0` statement.
   Reading it at a fixed error level penalises high-order methods, which reach
   that level while still pre-asymptotic. The rule used below, applied
   identically to every method: the finest pair of step sizes for which both
   errors exceed `5e-14` — 25× the round-off floor of `≈2e-15` visible in the
   raw tables.

---

## Experiment 1 — Convergence order

Steppers driven directly in a fixed-step loop, bypassing `solve` and its
controller, so what is measured is the method.

**Problem A:** `y' = -2y, y(0)=1` on `[0,5]`, exact `e^{-2t}`.
**Problem B:** `y' = y·cos t, y(0)=1` on `[0,5]`, exact `e^{sin t}`.

| method | claimed | A observed | pair | B observed | pair | verdict |
|---|---:|---:|---|---:|---|---|
| euler | 1 | **0.998** | 8192→16384 | **1.000** | 8192→16384 | OK |
| rk4 | 4 | **4.014** | 4096→8192 | **3.982** | 1024→2048 | OK |
| rk23 | 3 | **3.001** | 8192→16384 | **3.002** | 8192→16384 | OK |
| rkf45 | 5 | **5.015** | 512→1024 | **5.012** | 256→512 | OK |
| cashkarp | 5 | **4.969** | 512→1024 | **5.005** | 256→512 | OK |
| dopri5 | 5 | **5.013** | 512→1024 | **4.975** | 128→256 | OK |
| tsit5 | 5 | **5.140** | 256→512 | **4.915** | 128→256 | OK |
| radau / radaudense | 5 | **4.988** | 512→1024 | **4.982** | 512→1024 | OK |
| rodas4 | 4 | **3.972** | 2048→4096 | *see below* | | **CHECK** |
| taylor8 | 8 | **8.203** | 32→64 | **8.003** | 32→64 | OK¹ |

¹ Taylor8 reaches round-off after three step sizes, so only 2–3 pairs are usable
and the estimate is correspondingly coarse; 8.00–8.20 is consistent with order 8.

The raw error tables show textbook ratios directly — no fitting required. Problem A:

| method | n=128 | 256 | 512 | 1024 | 2048 | 4096 | 8192 | 16384 |
|---|---|---|---|---|---|---|---|---|
| euler | 3.38e-1 | 1.82e-1 | 9.42e-2 | 4.80e-2 | 2.42e-2 | 1.22e-2 | 6.09e-3 | 3.05e-3 |
| rk4 | 3.31e-6 | 2.00e-7 | 1.23e-8 | 7.64e-10 | 4.76e-11 | 2.97e-12 | 1.84e-13 | 1.79e-14 |
| rk23 | 2.11e-4 | 2.56e-5 | 3.15e-6 | 3.91e-7 | 4.87e-8 | 6.08e-9 | 7.59e-10 | 9.48e-11 |
| rkf45 | 2.81e-8 | 8.52e-10 | 2.62e-11 | 8.11e-13 | 2.42e-14 | 2.42e-15 | 4.56e-15 | 1.18e-14 |
| dopri5 | 9.22e-9 | 2.70e-10 | 8.16e-12 | 2.53e-13 | 8.00e-15 | 1.43e-15 | 4.42e-15 | 1.15e-14 |
| radau | 3.99e-9 | 1.25e-10 | 3.94e-12 | 1.24e-13 | 6.29e-15 | 1.56e-15 | 4.05e-15 | 1.15e-14 |
| taylor8 | 4.19e-14 | 7.03e-15 | — | — | — | — | — | — |

Euler halves (×2), rk23 ×8, rk4 ×16, the 5th-order pairs ×32. **Every integrator
in the library converges at its advertised order.** Given that `tests/test_tableaux.py`
already machine-checks the rooted-tree order conditions, this is confirmation
rather than discovery — but it is confirmation of the shipping code path, which
the tableau test alone does not give.

### 1b. RODAS4 loses three orders of accuracy on non-autonomous problems

`rodas4` is the one exception, and it is a real defect with a precise cause.

| n | AUTONOMOUS `y'=-2y` | order | NON-AUTONOMOUS `y'=y cos t` | order |
|---:|---|---:|---|---:|
| 128 | 2.731e-07 | — | 7.361e-09 | — |
| 256 | 1.699e-08 | 4.01 | 4.698e-10 | 3.97 |
| 512 | 1.059e-09 | 4.00 | 2.807e-11 | 4.06 |
| 1024 | 6.615e-11 | 4.00 | 5.834e-12 | **2.27** |
| 2048 | 4.142e-12 | 4.00 | 3.027e-12 | **0.95** |
| 4096 | 2.639e-13 | 3.97 | 1.533e-12 | **0.98** |
| 8192 | 1.917e-14 | 3.78 | 7.691e-13 | **0.99** |
| 16384 | 1.594e-14 | round-off | 3.895e-13 | **0.98** |

Autonomous: clean order 4 down to `1.9e-14`. Non-autonomous: order 4 until
`2.8e-11`, then **collapses to order 1** and floors at `3.9e-13` — a thousand
times worse than every other method reaches on the same problem.

**Cause, established by elimination.** Supplying an analytic Jacobian changes
nothing (`1.131e-07 / 1.131e-07`, `7.361e-09 / 7.363e-09`, … identical to four
significant figures), so it is not the differenced `∂f/∂y`. The remaining
approximation is `Rosenbrock._time_derivative` (`src/odesuite/steppers/rosenbrock.py`),
which computes `∂f/∂t` by forward differences with `dt = sqrt(EPS)·max(|t|,1)`.
Its `O(√ε) ≈ 1.5e-8` error enters the stage right-hand side as `h·d_i·f_t`,
contributing an `O(h·√ε)` — i.e. **first-order** — error term. On an autonomous
problem `∂f/∂t ≡ 0`, the difference is exact, and the floor vanishes. That is
exactly the pattern observed.

**`ODEProblem` accepts `jac` but has no slot for `∂f/∂t`**, so no caller can
work around this.

---

## Experiment 2 — Tolerance obedience

`rtol` swept `1e-3 … 1e-12`, `atol = rtol·1e-3`. Reported: achieved relative
error ÷ requested `rtol`. A roughly constant ratio across the sweep is the
desired behaviour.

**`y' = -2y`:**

| method | 1e-3 | 1e-5 | 1e-7 | 1e-9 | 1e-10 | 1e-11 | 1e-12 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rk23 | 19.9 | 20.2 | 21.6 | 22.2 | 22.3 | 22.3 | 22.3 |
| rkf45 | 1.6 | 2.1 | 2.8 | 3.3 | 3.6 | 3.7 | 3.8 |
| cashkarp | 0.1 | 0.7 | 1.7 | 2.4 | 2.8 | 2.9 | 3.1 |
| dopri5 | 1.3 | 1.3 | 1.6 | 1.7 | 1.8 | 1.8 | 1.8 |
| tsit5 | 0.8 | 0.8 | 0.7 | 0.6 | 0.6 | 0.6 | 0.6 |
| rodas4 | 2.4 | 2.5 | 2.3 | 2.4 | 2.4 | 2.4 | 2.1 |
| **radau** | 0.3 | 0.1 | 0.04 | 0.01 | **15.1** | **29.6** | **54.5** |

Every explicit pair holds a flat ratio across nine decades — the controller and
error norm are doing their job. `rk23`'s constant ≈20× is the usual local-vs-global
gap for a low-order pair, not a defect.

**Radau is the exception and it is a real defect.** Below `rtol=1e-9` the
achieved accuracy stops tracking the request:

| rtol | achieved | ratio | accepted steps |
|---|---|---:|---:|
| 1e-9 | 1.359e-11 | 0.01 | 468 |
| 1e-10 | 1.510e-09 | **15.1** | 832 |
| 1e-11 | 2.959e-10 | **29.6** | 1481 |
| 1e-12 | 5.449e-11 | **54.5** | 2634 |
| 1e-13 | 1.031e-11 | **103.1** | 4684 |

DOPRI5 on the same problem holds 1.55–2.04× across the identical range. The work
*is* being spent — steps rise 1.78× per decade, more than the 1.58× a 5th-order
method needs — but accuracy improves only ~5× per decade.

**Cause, established directly.** Not the Jacobian (analytic and differenced give
identical results to four figures). It is `NewtonSettings(tol_factor=0.03)` in
`RadauIIA.__init__` (`src/odesuite/steppers/irk.py`), which terminates the stage
solve at 3% of the integration tolerance. At loose tolerances that is far below
the truncation error; at tight ones it dominates. Varying only that constant:

| rtol | tol_factor=0.03 (default) | 0.003 | 1e-4 | 1e-6 |
|---|---|---|---|---|
| 1e-10 | 1.51e-09 (**15.1×**) | 5.07e-11 (0.5×) | 6.75e-12 (0.1×) | 7.89e-13 (0.0×) |
| 1e-11 | 2.96e-10 (**29.6×**) | 5.68e-12 (0.6×) | 2.30e-12 (0.2×) | 8.09e-14 (0.0×) |
| 1e-12 | 5.45e-11 (**54.5×**) | 7.67e-13 (0.8×) | 2.07e-13 (0.2×) | 1.81e-14 (0.0×) |

A single constant, and the tolerance is obeyed. This is an **honesty** defect as
much as an accuracy one: the solver reports `success` and says nothing about
having missed the tolerance by 54×.

---

## Experiment 3 — Stiff benchmarks

Using the **library's own** problem definitions (`odesuite.problems`), which
supply analytic Jacobians. `rtol=1e-6, atol=1e-8, max_steps=500_000`.

> A first attempt used a hand-written Van der Pol, `mu*((1-y²)y' - y)`, which is
> a different and far stiffer equation than the standard `mu(1-y²)y' - y`, and
> omitted the Jacobian. It produced 890,419 steps and 162 s — a number that
> would have been reported as a catastrophic performance defect. It was my error,
> not the library's. The corrected figures follow.

| problem | method | status | wall | accepted | rejected | nfev | njev | nlu |
|---|---|---|---:|---:|---:|---:|---:|---:|
| **Van der Pol μ=1000** `[0,3000]` | radau | finished | **0.16 s** | **1142** | 24 | 12534 | 41 | 536 |
| | rodas4 | finished | 0.11 s | 1402 | 20 | 9936 | 1422 | 1422 |
| | dopri5 | failed | 19.4 s | 499987 | 13 | 3000002 | 0 | 0 |
| | tsit5 | failed | 20.8 s | 499984 | 16 | 3000002 | 0 | 0 |
| **Robertson** `[0,1e5]` | radau | finished | 0.03 s | 152 | 7 | 1643 | 8 | 144 |
| | rodas4 | finished | 0.02 s | 167 | 3 | 1189 | 170 | 170 |
| | dopri5 | failed | 22.6 s | 499996 | 4 | 3000002 | 0 | 0 |
| **Robertson** `[0,1e11]` | radau | finished | **0.05 s** | **239** | 8 | 2648 | 14 | 250 |
| | rodas4 | finished | 0.03 s | 246 | 3 | 1742 | 249 | 249 |
| **HIRES** | radau | finished | 0.03 s | 142 | 4 | 1418 | 14 | 112 |
| | rodas4 | finished | 0.02 s | 189 | 1 | 1331 | 190 | 190 |
| **OREGO** | radau | finished | 0.18 s | 947 | 54 | 11251 | 78 | 656 |
| | rodas4 | finished | 0.17 s | 1524 | 12 | 10742 | 1536 | 1536 |

**The stiff solvers are genuinely good.** 1142 steps for Van der Pol μ=1000 and
239 for Robertson to `t=1e11` are in line with published RADAU5 figures. The
explicit methods fail on the stiff problems, as they must.

**The cost of that failure is the finding.** An explicit method on a stiff
problem burns **19–23 seconds** before giving up. `tests/test_app_stiffness.py::test_race_shows_an_explicit_method_failing_on_robertson`
was the 6th-slowest test in the suite at **34 s**, so the app deliberately
stages this demonstration. It is pedagogically right and operationally slow;
sizing in the backlog.

---

## Experiment 4 — Energy drift over 10,000 periods

Harmonic oscillator, `H=(p²+q²)/2`, exact energy 0.5, 500,000 fixed steps
(`h = 2π/50`).

| method | type | E(end) | relative drift | max &#124;ΔE&#124;/E | wall |
|---|---|---|---:|---:|---:|
| verlet | symplectic | 0.49941689 | −1.17e-03 | 3.95e-03 | 9.0 s |
| yoshida4 | symplectic | 0.50000713 | +1.43e-05 | 1.92e-05 | 22.6 s |
| yoshida6 | symplectic | 0.50000000 | **−1.08e-11** | 3.60e-07 | 54.3 s |
| rk4 | non-symplectic | 0.48653843 | −2.69e-02 | 2.69e-02 | 16.2 s |
| euler | non-symplectic | **overflowed** | — | — | — |

Exactly the textbook contrast the library's docstring promises. For the
symplectic methods the *worst* error over the run exceeds the *final* error
(verlet 3.95e-3 vs 1.17e-3; yoshida6 3.6e-7 vs 1.1e-11) — bounded oscillation.
For rk4 the final error **equals** the worst (2.69e-2 both) — monotone growth.
The claim in `symplectic.py`'s module docstring is verified.

### 4b. A fixed-step method that overflows spins for `max_steps` and misreports why

Euler on the harmonic oscillator is unconditionally unstable, so it overflows.
What happens then is a driver bug:

| max_steps | status | wall | accepted | rejected |
|---|---|---:|---:|---:|
| 10,000 | failed | 0.10 s | 10000 | 0 |
| 100,000 | failed | 1.16 s | 90607 | 9393 |
| 1,000,000 | failed | **13.71 s** | 90607 | **909,393** |

After 90,607 accepted steps the state goes non-finite. `driver.solve`'s
non-finite branch responds by halving `planner.h_abs` — but `StepPlanner.plan`'s
**fixed-step branch ignores `h_abs` entirely** (it derives the step from
`_reference` and the accepted-step count), and the driver then overwrites
`planner.h_abs` with what `plan()` returned. The halving is a no-op, the
identical failing step is retried 909,393 times, and the reported message is
`exceeded max_steps=1000000` — not the overflow, which the driver already knows
about (it set `nonfinite_at`).

The adaptive path handles the same situation correctly:
`step size underflow at t=1: required h=2.16e-15 is below the local floating-point
resolution. The solution may be singular or blowing up there`.

---

## Experiment 5 — Cross-check against SciPy `solve_ivp`

`rtol=1e-10, atol=1e-12` (non-stiff) / `1e-8, 1e-10` (stiff), 50 shared output
times, max relative deviation.

**Non-stiff:**

| problem | dopri5 / RK45 | radau / Radau | rodas4 / LSODA |
|---|---|---|---|
| lotka_volterra | 8.59e-10 | 6.22e-09 | 2.86e-08 |
| van_der_pol | 6.59e-09 | 1.51e-08 | 9.88e-08 |
| brusselator | 1.62e-09 | 1.07e-09 | 1.82e-08 |
| pendulum | 8.86e-08 | 1.61e-07 | 2.54e-07 |
| duffing | 2.90e-07 | 3.14e-07 | 3.90e-07 |
| logistic | 1.50e-09 | 5.27e-11 | 3.40e-10 |
| sine_cosine | 9.98e-11 | 1.11e-09 | 9.32e-10 |
| *lorenz* | *1.08e+01* | *4.29e+00* | *3.66e+01* |
| *kepler* | *7.92e-01* | *8.35e+01* | *1.00e+00* |

**Stiff:**

| problem | pair | deviation | ours | scipy |
|---|---|---|---:|---:|
| van_der_pol μ=1000 | radau / Radau | 4.84e-08 | 0.66 s (3592 steps) | 0.40 s |
| | rodas4 / LSODA | 2.42e-05 | 0.61 s | 0.02 s |
| robertson [0,1e5] | radau / Radau | 3.10e-08 | 0.09 s (456) | 0.05 s |
| hires | radau / Radau | 5.07e-07 | 0.11 s (435) | 0.08 s |
| orego | radau / Radau | 3.09e-06 | 0.62 s (2975) | 0.35 s |

**Agreement is 1e-7 or better on every non-chaotic problem.** The two italicised
rows are *not* defects: Lorenz is chaotic and Kepler at e=0.6 is highly
sensitive, so at these horizons two correct implementations must diverge — see
Experiment 9. Reporting them as accuracy failures would be the mistake.

**Speed:** ours is 1.6× SciPy's Radau — respectable for pure Python against a
tuned implementation. `rodas4` vs LSODA is 30× slower, but LSODA is compiled
Fortran; the comparison is not like-for-like.

---

## Experiment 6 — Pathological inputs: what the user actually sees

| input | status | what the user gets |
|---|---|---|
| `y'=y²`, `y(0)=1`, to `t=2` (blows up at `t=1`) | **failed** | *"step size underflow at t=1 … The solution may be singular or blowing up there"*; partial trajectory to `t=1`, `y=6.2e13`. **Honest.** |
| `y'=y^{1/3}`, `y(0)=0` (**non-unique**) | **finished, success=True** | **`y ≡ 0`, 8 steps, no warning of any kind.** |
| `y'=1/(t-1)` through the pole | **failed** | *"step size underflow at t=1 …"*; partial trajectory. **Honest.** |
| `y'=sign(t-1)` (discontinuous RHS) | finished, success=True | `y(2) = -9.38e-6` (exact 0), 22 rejected steps. No note that the RHS is discontinuous. |
| RHS returns `NaN` for `t>1` | **failed** | *"the solution became non-finite at t=1 and did not recover as the step was cut to h=9.8e-16. Either the right-hand side returns NaN or inf there, or the solution blows up in finite time"*. **Excellent — it distinguishes the two causes.** |
| RHS is `inf` at `t0` (`y'=1/t` from 0) | raises | bare **`ZeroDivisionError: float division by zero`** |
| `y'=y²` with `radau` | failed | honest underflow message; 801 ms, 635 steps |

Two findings:

**(a) The non-uniqueness case is silently wrong-by-omission.** `y' = y^{1/3}, y(0)=0`
has *two* solutions through the origin — `y≡0` and `y=(2t/3)^{3/2}`. The solver
returns the first, reports `status="finished"`, `success=True`, and says nothing.
No numerical method can detect this in general — but **this app teaches the
counterexample**. `lessons/unit1_first_order.py`, lesson `slopefields`, carries a
`pitfall` note reading: *"y' = y^{1/3} with y(0) = 0 has both y ≡ 0 and
y = (2t/3)^{3/2} through the origin. ∂f/∂y blows up there…"*. The course teaches
it; the tool contradicts it without comment.

**(b) The guard in `problem.py` covers only half its stated purpose.**
`src/odesuite/problem.py` carries a long comment saying it exists so that an
equation started at its own singularity does not come out as *"a bare
ZeroDivisionError from inside a step-size heuristic, naming nothing the caller
had written."* It checks `np.all(np.isfinite(f0))` — which catches a numpy-produced
`inf`, but not a Python-level `ZeroDivisionError` raised inside the user's own
callable before it can return. `y' = 1/t` from `t=0` produces exactly the bare
`ZeroDivisionError` the comment set out to prevent.

---

## Experiment 7 — Equilibria and classification

`odesuite_app.analysis.find_fixed_points` + `classify`, hand-checked.

| system | found | classification | correct? |
|---|---|---|---|
| **Lotka–Volterra** (1.5,1,3,1) | `(0,0)` | saddle, eig `+1.5, -3.0` | ✔ |
| | `(3, 1.5)` | **centre**, neutral, eig `±2.1213i` | ✔ — the borderline case, named honestly |
| **Damped pendulum** c=0.3 | `(0,0)` | stable spiral, eig `-0.15±0.9887i` | ✔ |
| | `(±π, 0)` | saddle, eig `+0.8612, -1.1612` | ✔ (both found) |
| **Saddle-node** `x'=1-x², y'=-y` | `(-1,0)` | saddle | ✔ |
| | `(+1,0)` | stable node, eig `-2, -1` | ✔ |
| **Non-hyperbolic** `x'=-y+x(x²+y²)`, `y'=x+y(x²+y²)` | `(0,0)` | **centre**, neutral, eig `±1i` | linearly correct — **but the true flow spirals outward** |

Every equilibrium was found, at full precision, with correct eigenvalues and
correct linear classification — including Lotka–Volterra's centre, the exact
case the brief flags as the one implementations get wrong.

**The gap is presentation, not mathematics.** `analysis.classify`'s docstring is
scrupulous ("*'Non-hyperbolic' covers the cases where the linearisation decides
nothing … worth naming honestly rather than guessing at*"), and it returns
`NEUTRAL` for a centre. But `screens/portrait.py` renders `point.kind` verbatim
in bold — so the fourth system above is labelled simply **"centre"**, with
nothing to say that Hartman–Grobman does not apply at a non-hyperbolic point and
that the nonlinear flow may do the opposite. Lotka–Volterra gets the right answer
only because that system happens to be conservative; the classifier cannot tell
the two apart, and the UI does not admit it.

---

## Experiment 8 — Event detection

**Accuracy.** Free fall `y''=-g`, `h0=1`, `g=9.81`; analytic impact time
`√(2h₀/g) = 0.451523640985731`.

| rtol | reported event time | absolute error |
|---|---|---|
| 1e-3 | 0.451523640985731 | **5.55e-17** |
| 1e-5 | 0.451523640985731 | **0** |
| 1e-7 | 0.451523640985731 | **0** |
| 1e-9 | 0.451523640985731 | 5.55e-17 |
| 1e-11 | 0.451523640985731 | 1.67e-16 |

Machine precision at every tolerance, including the loosest. Locating the root on
the interpolant with `brentq(xtol=1e-14)` rather than at step endpoints is
working exactly as designed. This is better than the brief expects to find.

**Completeness.** `g = sin(20t)` on a smooth decay over `[0,10]` — 63 true roots:

| `subdivisions` | roots found |
|---|---|
| **0 (the default)** | **7 of 63** |
| 8 | **63 of 63** |

The default silently misses 89% of the crossings. `events.py`'s docstring is
candid about this and gives a measured figure of its own, and the opt-in fix
works perfectly. But the default is the lossy one, and nothing in the returned
`Solution` hints that crossings may have been missed.

---

## Experiment 9 — Long-horizon chaos

Lorenz at σ=10, ρ=28, β=8/3; two initial conditions differing by `1e-10`; both at
`rtol=1e-12, atol=1e-14`.

| t | separation |
|---:|---|
| 0 | 1.000e-10 |
| 10 | 1.762e-10 |
| 20 | 9.201e-08 |
| 25 | 1.959e-05 |
| 30 | 2.130e-03 |
| **40** | **6.473e+00** — trajectories now unrelated |
| 80 | 2.883e+01 — separation ≈ attractor diameter |

Fitted largest Lyapunov exponent **0.8368** against the literature value 0.9056
(a crude single-window fit; the agreement confirms the dynamics are right).
Predictability horizon for a `1e-10` perturbation: **t ≈ 27.5**.

The app's Lorenz catalogue blurb reads *"The butterfly. Deterministic but chaotic
— two trajectories a hair apart diverge exponentially"*, and `widgets/cards.py`
colours the `chaotic` tag as a warning. **That warning lives on the gallery card,
not on the plot.** Once a Lorenz trajectory is on screen in the Solver Lab or
Phase Portrait, nothing distinguishes the reliable early part from the
meaningless late part, and the default horizon is `t_end=20` — just inside the
predictability limit, so the default view is honest and any increase silently
is not.

---

## Experiment 10 — UI stress

60 parameter updates ~16 ms apart (≈1 s of slider dragging), then 1.5 s for
in-flight solves to land. A 5 ms timer on the GUI thread; the largest gap between
ticks is the longest the UI was unresponsive. `QT_QPA_PLATFORM=offscreen`.

| problem | param | median gap | p99 | max gap | results delivered |
|---|---|---:|---:|---:|---:|
| van_der_pol | mu | 5.7 ms | 30.6 ms | 42.4 ms | 0 |
| lorenz | sigma | 5.1 ms | 30.5 ms | 37.6 ms | 1 |
| robertson | log_t_end | 5.6 ms | 32.1 ms | 37.0 ms | 0 |
| brusselator | a | 5.9 ms | 70.1 ms | **81.9 ms** | 32 |
| pleiades | t_end | 6.0 ms | 80.7 ms | **104.1 ms** | 9 |
| kuramoto_sivashinsky | n_modes | 5.8 ms | 66.0 ms | 83.0 ms | 0 |

**The threading architecture works.** Median 5–6 ms is the timer's own interval,
i.e. the GUI thread was free throughout. Solves genuinely run on `QThreadPool`
workers, and the token-plus-cancellation scheme in `solver.py` visibly does its
job — van der Pol delivered *zero* results during the drag because every solve
was superseded and cancelled at its next step boundary, exactly as designed.

**The stalls are on the replot path, not the solve.** Worst case 104 ms on
Pleiades (a 7-body problem, 28 state components) — one visible freeze. Since the
solve is off-thread, what costs 100 ms is delivering and drawing the result on
the GUI thread.

*Caveat:* measured under the offscreen platform, which does no real painting.
**Second caveat, added after the fact:** these are wall-clock numbers, and the
audit's startup finding was later shown to have been measured on a machine
saturated by a parallel test run (see [E-1], retracted). This experiment was run
without that load, but the millisecond figures should still be read as upper
bounds. The *shape* of the result — median at the timer's own interval, i.e. the
GUI thread free, with occasional replot stalls — is what the experiment
establishes, and that does not depend on load.
On-screen figures can only be worse.

---

## Experiment 11 — Expression sandbox (added; not in the brief's list)

The brief's §J says: *"If arbitrary user input reaches `eval`/`new Function`/`vm`,
treat as P0."* The Python equivalent is `sympify`/`parse_expr`, and
`odesuite_app/custom.py` is explicitly aware of the danger — its module docstring
explains that `sympify` evaluates with real builtins in scope and that
`_SAFE_GLOBALS` sets `__builtins__` to an *empty mapping* rather than omitting it,
"because an absent `__builtins__` key makes Python reinstate the real one."

That reasoning is correct, and it closes the **name-lookup** hole. It does not
close **attribute traversal from a whitelisted object**.

**Step 1 — name lookup is genuinely blocked.** All of these are rejected with
`NameError`: `__import__("os")…`, `eval("1+1")`, `exec(…)`, `open(…)`,
`globals()`, `locals()`, `vars()`, `type(1)`, `print(…)`, `compile(…)`.

**Step 2 — but `sin` is on the whitelist, and objects carry their class.**

```
sin.__class__.__init__.__globals__
    -> a real module globals() mapping, 91 names
    -> contains '__builtins__': True
    -> real builtins reachable: 157 names, '__import__' present: True
```

**Step 3 — this reaches arbitrary code execution.** A harmless canary
(`…__globals__["__builtins__"]["open"](path,"w").write("canary")`) **created the
file.** Confirmed.

**Step 4 — it is reachable from two shipping UI paths:**

| entry point | user-facing route | result |
|---|---|---|
| `odesuite_app.custom.build` | Solver Lab → "type your own system" | **accepted the payload; canary written** |
| `odesuite_app.symbolic.parse_equation` | the equation editor | **accepted; canary written.** The parsed equation came back as `Eq(Derivative(y(t), t), 6)` — the payload executed and `write()`'s return value (6, the byte count) silently became the right-hand side. |

The `dsolve` subprocess isolation does not help: parsing happens in-process,
before the worker is spawned.

**Threat model, stated plainly.** This is a local desktop app with no network
input, and the equation is normally typed by the person running it — attacking
yourself is not an attack. It matters because (i) equations get *shared* — pasted
from a classmate, a forum, a handout — and a one-line "try this equation" is now
a payload; and (ii) `odesuite` is packaged for PyPI, so `odesuite_app.custom.build`
is importable by other code that may well feed it untrusted input. By the brief's
own rule this is **P0**.

### The fix, prototyped and verified

Validate the expression's AST *before* sympy compiles it: allow only
`Expression, Constant, Name, Load, Call, BinOp, UnaryOp, Tuple` and the
arithmetic operators; reject `Attribute` and `Subscript` outright; require every
`Name` to be a declared variable/parameter or a whitelisted function; require
every `Call` target to be a bare whitelisted `Name`; reject keywords and starred
args.

Measured against the payload set and the app's own equation shapes:

| | result |
|---|---|
| 9 escape payloads (incl. all four gadget chains above) | **9 / 9 rejected** |
| 14 legitimate equations (`-2*y`, `y*cos(t)`, `mu*(1-x**2)*v - x`, `sec(t)`, `sqrt(Abs(y))`, `atan2(y,x)`, `3*t^2 + 1`, `Max(0,y)`, …) | **14 / 14 accepted** |

Note for implementation: on the `symbolic.parse_equation` path the validator must
run on the text *after* `_rewrite_derivatives` has substituted the derivative
tokens, with those tokens added to the permitted names.

---

## Experiment 12 — WCAG contrast (added)

Computed WCAG 2.1 contrast ratios for both shipped palettes.

**All text and data colours pass AA in both themes.** Dark: `text` 16.02,
`text_muted` 6.15, `accent` 6.45, `success` 7.45, `warning` 7.50, `danger` 5.65.
Light: `text` 15.80, `text_muted` 5.33, `accent` 5.19, `success` 5.08,
`warning` 4.87, `danger` 5.36. All eight series colours clear 3.0 against the
background in both themes (dark 6.45–11.51, light 4.08–5.36).

The tokens that "fail" a naive check — `surface_alt`, `border`, `grid`,
`accent_soft`, `plot_background` — are backgrounds and hairlines, which are not
required to meet a text contrast ratio. **This palette is in good shape**, and
`screens/portrait.py:39` records a deliberate decision to encode equilibrium type
as *marker shape* as well as colour "so it survives greyscale and colour-vision
deficiency" — verified in `_MARKERS`.

The remaining colour issue is narrower: separatrices are drawn
`palette.danger if unstable else palette.success` (`portrait.py:364`) — red/green
with no shape or dash distinction, since they are lines rather than markers.

---

## Summary of what the experiments established

| # | Experiment | Verdict |
|---|---|---|
| 1 | Convergence order | **All 11 integrators match their claimed order.** |
| 1b | RODAS4 non-autonomous | **Defect** — order 4 → 1, floor at 4e-13, cause identified |
| 2 | Tolerance obedience | Explicit pairs: flat across 9 decades. **Radau: 54× shortfall at 1e-12**, cause identified |
| 3 | Stiff benchmarks | **Strong** — VdP μ=1000 in 1142 steps, Robertson→1e11 in 239 |
| 4 | Energy drift | **Textbook** — bounded for symplectic, monotone for RK4 |
| 4b | Fixed-step overflow | **Defect** — 909,393 no-op rejections, 13.7 s, wrong message |
| 5 | SciPy cross-check | ≤1e-7 on every non-chaotic problem |
| 6 | Pathological inputs | 4 of 6 honest; **non-uniqueness silent**; one bare `ZeroDivisionError` |
| 7 | Equilibria | **All correct**, incl. the LV centre; UI does not caveat non-hyperbolic |
| 8 | Events | **Machine-precision timing**; default misses 89% of dense crossings |
| 9 | Chaos | Lyapunov 0.837 vs 0.906; warning is on the card, not the plot |
| 10 | UI stress | UI thread stays free; **104 ms worst replot stall** |
| 11 | **Sandbox** | **P0 — arbitrary code execution from a typed equation.** Fix prototyped |
| 12 | Contrast | Passes AA throughout; one red/green line-colour issue |
