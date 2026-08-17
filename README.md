# odesuite

A from-scratch ODE solver library in Python, and a desktop studio built on it. Adaptive
Runge–Kutta, stiff solvers, differential-algebraic systems, event location, boundary
value problems, parameter sensitivities, and two uncommon methods — an arbitrary-order
Taylor integrator built on automatic differentiation, and an exponential integrator for
stiff semilinear PDEs.

SciPy is used for LU factorisation, sparse storage and root-finding. **No integration is
delegated to it.** Every method here is implemented from the coefficients up, and its
correctness is established independently of SciPy — see [Verification](#verification).

```python
from odesuite import ODEProblem, solve, Event

prob = ODEProblem(f=vdp, t_span=(0, 3000), y0=[2.0, 0.0], jac=vdp_jac, args=(1000.0,))
sol  = solve(prob, method="radau", rtol=1e-8, atol=1e-10,
             dense_output=True, events=[Event(g, terminal=True, direction=-1)])

sol.y_at(1234.5)      # continuous solution, vectorised over t
sol.t_events[0]       # where g(t, y) = 0
sol.stats             # nfev / njev / nlu / steps / rejections / runtime
```

```
pip install -e ".[app]"     # then:
odesuite-gui
```

![home screen](figures/app/home.png)

---

## Methods

| Method | Order | Kind | Notes |
|---|---|---|---|
| `rk23` | 3(2) | explicit RK | Bogacki–Shampine, FSAL |
| `rkf45` | 5(4) | explicit RK | Fehlberg, local extrapolation |
| `cashkarp` | 5(4) | explicit RK | Cash–Karp |
| `dopri5` / `rk45` | 5(4) | explicit RK | Dormand–Prince, FSAL, free 4th-order dense output — **default** |
| `tsit5` | 5(4) | explicit RK | Tsitouras, minimised leading error |
| `rodas4` | 4(3) | Rosenbrock | L-stable, stiffly accurate, solves index-1 DAEs |
| `radau` | 5(3) | implicit RK | Radau IIA, L-stable, stiffly accurate, collocation dense output |
| `radaudense` | 5(3) | implicit RK | Radau via the full 3n×3n solve — the oracle the fast path is tested against |
| `taylor{N}` | N | Taylor series | Arbitrary order via jet arithmetic; `taylor8/20/30` preregistered |
| `etdrk4` | 4 | exponential | For `u' = Lu + N(u)`; fixed step |
| `verlet` | 2 | symplectic | Störmer–Verlet; fixed step |
| `yoshida4/6/8` | 4/6/8 | symplectic | Composition of Verlet; fixed step |

Beyond the IVP solver: `solve_bvp` (multiple shooting), `forward_sensitivities`
(`dy/dp` by internal differentiation), mass matrices `M y' = f` including singular `M`
(index-1 DAEs), and event location to machine precision.

---

## Verification

Correctness evidence is the point of this project, so it is worth being specific about
what is actually checked. **998 tests**, of which the load-bearing ones are:

**Order conditions, algebraically.** `tests/test_tableaux.py` evaluates the rooted-tree
order conditions through order 5 for every Butcher tableau, and asserts that the
conditions *fail* at order p+1 — so each declared order is neither overstated nor
understated. A single mistyped digit fails this instantly and exactly, rather than
surfacing later as a slightly wrong convergence slope.

**Order, numerically.** Local truncation error is measured with a geometric step sweep
that self-terminates at the round-off floor, and the slope is read from the finest valid
pair. Every method is held to its own theoretical order — the tests do not simply
reproduce SciPy's behaviour.

**Error estimators are checked directly.** `test_error_estimate_is_nondegenerate` exists
because a Rosenbrock pair transcribed into this library once had an embedded weight
vector that annihilated the stage vector exactly, giving an error estimate of ~1e-17 on
every problem. Every accuracy test still passed — the solution was fine — while the
adaptive controller was blind and accepting every step. That method was removed; the test
that catches it is permanent.

**Constants are derived, not transcribed, wherever possible.** Radau's eigendecomposition
comes from `numpy.linalg.eig` at import (and matches the published `MU_REAL`/`MU_COMPLEX`
to 1e-12); the symplectic composition weights come from the triple-jump recursion; the
stability functions below are measured by running the actual steppers.

**The step controller and the Newton iteration are tested directly**, not only through
the solves they drive. `tests/test_controllers.py` checks the PI and I formulas against
the arithmetic they document, the clamps, and the rule that a rejected step never
enters the PI history; `tests/test_newton.py` pins the termination test to the
*remaining geometric series* rather than the last correction, by constructing an
iteration that converges slowly enough for the two to disagree. Both modules used to
be covered only indirectly — which, given that the worst bug recorded below was a
controller running blind, was the wrong place to have a gap.

**Cross-validation** against `scipy.integrate.solve_ivp` on shared problems, used as an
oracle only — never as the basis of an order or accuracy claim.

```
py -3.10 -m pytest tests/ -q          # 988 passed, 10 skipped, ~6 min
py -3.10 -m pytest tests/ -q -m 'not slow'   # the fast loop, ~3.5 min
py -3.10 -m ruff check . && py -3.10 -m mypy # lint and types, both clean
py -3.10 benchmarks/run_all.py        # regenerate every static figure below
```

The interface is tested too, headlessly, and not only for smoke: the phase-plane
analysis is checked against closed forms, the two independent routes to `R(z)` are
checked against each other, and the "copy as code" button's output is **executed** to
prove it runs.

---

## Results

### Stability regions

![stability regions](figures/stability_regions.png)

`R(z)` is measured by running each stepper for one step on `y' = λy` with `h = 1`, rather
than deriving a formula per method family. The measured classification matches theory:

| Method | Real-axis limit `\|hλ\|` | A-stable | L-stable | `\|R(-∞)\|` |
|---|---|---|---|---|
| rk23 | 2.52 | no | no | ∞ |
| dopri5 | 3.32 | no | no | ∞ |
| tsit5 | 3.53 | no | no | ∞ |
| cashkarp | 3.76 | no | no | ∞ |
| **rodas4** | ∞ | **yes** | **yes** | 8.8e-10 |
| **radau** | ∞ | **yes** | **yes** | 3.0e-10 |

The bounded region for explicit methods *is* the stiffness restriction: on Robertson,
`dopri5` reaches only `t = 54` out of `1e11` after 50 000 steps.

### Work-precision

![work-precision](figures/work_precision.png)

Relative error at the endpoint against RHS evaluations and against wall time, sweeping
tolerance over eight decades. Selected results at the tightest tolerance:

| Problem | Method | error | nfev |
|---|---|---|---|
| Lotka–Volterra | **taylor20** | **7.7e-13** | **2 682** |
| | scipy DOP853 | 2.5e-13 | 5 162 |
| | dopri5 | 1.2e-12 | 24 086 |
| Kepler (e=0.5) | **taylor20** | **1.5e-12** | **1 462** |
| | scipy DOP853 | 5.7e-12 | 2 318 |
| Robertson | radau | 9.3e-15 | 49 286 |
| | scipy Radau | 5.6e-15 | 37 112 |
| HIRES | radau | 3.7e-10 | 31 762 |
| | scipy Radau | 1.0e-12 | 23 136 |

Read honestly: **the Taylor method is the standout**, reaching higher accuracy than
SciPy's best explicit integrator with roughly half the evaluations on smooth problems.
The explicit RK pairs are competitive with SciPy's (within ~1.3× on evaluations). The
stiff solvers are respectable but not leading — `radau` uses about 1.3–1.5× SciPy's
Radau evaluations and ~1.7× its wall time. SciPy's `LSODA` and `BDF` are faster still on
stiff problems; they are BDF-based, a family deliberately excluded here (see
[Scope](#scope)). `rodas4` needs 2–3× `radau`'s work on stiff problems, as expected: it
recomputes the Jacobian every step and is an order lower.

### Symplectic energy drift

![energy drift](figures/energy_drift.png)

Kepler at e=0.3 for 3000 orbits, at matched work. The diagnostic is the worst energy
error in the second half of the run divided by the worst in the first half:

| Method | nfev | 1st-half max | 2nd-half max | ratio |
|---|---|---|---|---|
| verlet | 360 001 | 6.03e-03 | 6.03e-03 | **1.00** — bounded |
| yoshida4 | 360 001 | 1.30e-02 | 1.30e-02 | **1.00** — bounded |
| dopri5 | 1 388 930 | 2.70e-05 | 5.41e-05 | **2.00** — linear growth |

DOPRI5 is far more accurate in absolute terms and stays so for a long time — but its
energy error *doubles as the interval doubles*, while the symplectic methods' error is a
bounded oscillation, the same size after three thousand orbits as after ten. Accuracy and
qualitative fidelity are different properties.

### Exponential integrator on a stiff PDE

![Kuramoto-Sivashinsky](figures/ks_spacetime.png)

Kuramoto–Sivashinsky, `u_t = -u_xx - u_xxxx - u u_x`, spectrally discretised. At 256 modes
`|L|max ≈ 4032`, so an explicit method is stability-bound at `h < 5e-4`:

| Method | steps | nfev | error | time |
|---|---|---|---|---|
| **etdrk4** | **1 001** | 4 005 | 9.5e-09 | **76 ms** |
| etdrk4 | 2 000 | 8 001 | 8.0e-10 | 153 ms |
| dopri5 | 24 384 | 146 318 | 2.6e-11 | 4 085 ms |
| tsit5 | 22 991 | 137 960 | 3.0e-11 | 4 484 ms |

**24× fewer steps, 54× faster.** ETDRK4 treats `exp(hL)` exactly, so the stiffness of the
linear part imposes no step restriction at all.

---

## The studio

A PySide6 desktop application over the same library — `odesuite-gui`, or
`python -m odesuite_app`. Six screens, dark and light themes, everything solved on a
worker thread so the interface never blocks.

The guiding idea is to show **what the solver is doing**, not just the answer. That is
what a generic plotting front-end cannot do, and what this library has the data for.

### Solver Lab

![solver lab](figures/app/solver-lab.png)

Problem and method pickers, live tolerance and parameter sliders, work counters — and
the **step-size timeline** underneath, which is the signature view. On Robertson it
spans 1.3e+14×, with the 11 rejected attempts marked in red exactly where the controller
misjudged the problem. Trajectories are drawn from the **dense output**, so a 73-step
Taylor solve of a Kepler orbit renders as a smooth ellipse rather than a polygon.

### Phase Portrait Studio

![phase portrait](figures/app/phase-portrait.png)

Streamlines, nullclines, equilibria classified by the Jacobian's eigenvalues, and the
separatrices out of every saddle. Click anywhere to launch a trajectory — integrated
forwards *and* backwards, which is what makes it the curve *through* a point. Parameter
sliders recompute the whole analysis, so a pitchfork bifurcation happens as you drag.

Everything here is checked against closed forms in `tests/test_analysis.py`: the
pendulum's separatrix is verified to lie on the energy level **E = 1** to 1e-6 across all
700 sampled points.

### Stiffness Explorer

| explicit | implicit |
|---|---|
| ![dopri5](figures/app/stiffness-explicit.png) | ![radau](figures/app/stiffness-implicit.png) |

The clearest argument in the project. Left panel: the method's stability region. Right:
the solve. As it plays, the Jacobian's eigenvalues scaled by the current step, `h·λ`, move
across the complex plane.

On Van der Pol at μ=30, DOPRI5's readout shows `hλ = −3.120` against a boundary at
**3.33** — the step is pinned by *stability*, not accuracy, and 1579 steps are needed.
Switch to Radau: the whole left half-plane turns stable, `h·λ` roams out to −150, and the
same solve takes 650 steps.

### Method Race and Accuracy Lab

| ![race](figures/app/method-race.png) | ![accuracy](figures/app/accuracy-lab.png) |
|---|---|

The race replays several methods against integration time with live counters. On
Robertson, Radau and RODAS4 finish in 397 and 410 steps while DOPRI5 burns **399,996 and
fails** — the Phase 2 acceptance result as a spectator sport.

The Accuracy Lab runs the verification harness interactively: work-precision sweeps,
energy drift, and convergence-order fitting. The screenshot shows four methods fitted at
**3.00, 5.00, 5.02 and 4.00** against claims of 3, 5, 5 and 4.

### Your own equation

![the closed form of a typed equation](figures/app/equation-symbolic.png)

The Solver Lab takes a typed equation as readily as a built-in problem — one equation of
any order, `y'' - mu*(1 - y**2)*y' + y = 0`, or several first-order ones. sympy parses it
and **differentiates it symbolically**, so a hand-written right-hand side reaches the
solver with an exact Jacobian and every implicit method works on it.

It is registered as an ordinary catalogue entry, which is what makes it go further than
its own screen: the phase portrait, the stiffness explorer and the method race select
problems by key and cannot tell the difference, so **an equation you typed can be raced
against seven methods** or swept for stiffness with nothing added to those screens.

Alongside the trajectory there is the **closed form**, where one exists: the
characteristic polynomial, its roots and multiplicities, the `e^{rt}` / `t·e^{rt}` /
`e^{at}cos bt` each contributes, the general and particular solutions typeset, and a
verification that substituting the answer back into the equation gives *exactly* zero.
Give a coefficient a slider and the roots follow it live — drag `c` in
`y'' + 2c·y' + y = 0` and watch the complex pair collide at `c = 1` and split onto the
real axis: underdamped, critically damped, overdamped.

Two limits are enforced rather than glossed. `dsolve` does not merely stall on some
equations, it **hangs** — `y' = sin(y)` never returns — so it runs in a subprocess under
a hard timeout. And a **static vector field is only meaningful for an autonomous
system**: a forced equation is kept out of the phase portrait instead of being drawn
against a field it does not obey.

Parsing is locked down. `sympy.sympify` *evaluates* its input with the ordinary builtins
in scope, so `sympify("__import__('os').system(...)")` runs the command — a hole this
project had until a test caught it. Expressions now go through `parse_expr` with an
explicitly emptied `__builtins__` (explicitly, because an absent key makes Python
reinstate the real one) and a whitelist of elementary functions.

### Packaging

```
py -3.10 -m PyInstaller packaging/odesuite.spec --noconfirm
dist/odesuite-studio/odesuite-studio.exe --selftest report.txt
```

A one-folder build, **235 MB**, verified by a `--selftest` flag that solves across every
method family and returns a non-zero exit code on failure — necessary because a frozen
GUI application on Windows has no stdout to report through.

Two things the build needed. PyInstaller aimed at `__main__.py` compiles fine and then
fails at runtime with *"attempted relative import with no known parent package"*, so the
spec points at an absolute-import launcher. And sympy's `lambdify` probes for optional
torch/tensorflow/jax backends behind `try/except`, which static analysis cannot
distinguish from real dependencies — **torch alone was 263 MB**, more than everything else
combined.

---

## Design

Five concerns are kept strictly separate, and that separation is what keeps the library
at ~5 700 lines rather than three times that: events, dense output, mass matrices, DAE
support and sensitivities are each written **once** and work with every method.

| Concern | Responsibility | Must not |
|---|---|---|
| `ODEProblem` | `f`, `y0`, `t_span`, `jac`, mass matrix, params | know about steppers |
| `Stepper` | advance **one** step, report an error estimate | own the loop or choose `h` |
| `Controller` | error norm → next `h`, accept/reject | know method internals |
| driver `solve` | the loop, events, `t_eval`, termination, stats | contain method-specific math |
| `linalg` / `newton` | Jacobians, LU caching, θ-monitoring | be duplicated per method |

Consequences worth noting:

- **Butcher tableaux are data.** One generic explicit-RK stepper yields five named
  methods; adding a sixth is coefficients, not code.
- **Mass matrices are supported from day one.** A singular `M` turns the same code path
  into an index-1 DAE solver, needing only stiff accuracy from the method.
- **Four Jacobian strategies**, shared by every implicit method: analytic, finite
  differences with Shampine scaling, complex-step (`Im f(y + ihe_j)/h` — exact to
  machine precision, verified bit-for-bit against analytic Jacobians), and sparse via
  greedy graph colouring (a tridiagonal 1000×1000 Jacobian costs **3** evaluations
  instead of 1000).

### Bugs worth recording

Each produced *plausible* wrong answers rather than an error, and each is now covered by
a test named after it:

1. **An error estimator that was identically zero.** ROS3P's embedded pair annihilated
   the stage vector exactly (~1e-17 on every problem). All accuracy tests passed while
   the step controller ran blind. The method was removed and
   `test_error_estimate_is_nondegenerate` added.
2. **Differentiating an integrated map with the wrong epsilon.** The multiple-shooting
   Jacobian used `sqrt(EPS)`, but a shot is only accurate to the *integration tolerance*,
   so the right step is `sqrt(rtol)`. With a node component at zero the perturbation was
   1.5e-16 — pure noise — and every Bratu solve failed reporting only "line search
   failed".
3. **Silent complex truncation.** The FD Jacobian and Radau's stage arrays were allocated
   as `float` and assigned complex values, discarding the imaginary part. Spectral PDE
   states are complex, so Radau was quietly returning wrong answers on them.
4. **Fixed-step methods that were not fixed-step.** Time was accumulated by repeated
   addition, so the last step fell a rounding error short of `t_end` and left a crumb
   step orders of magnitude smaller than the rest — a symplectic method reporting a
   1.4e+10× step-size spread. Now `t0 + k·h`, exact to the last bit.
5. **`sympify` executes its input.** The custom-system editor was documented as safe
   because it passed a restricted `locals`; `locals` adds names but removes none, and a
   test proved the point by running a shell command.
6. **A shared placeholder collapsed a system into one equation.** The prime-notation
   parser rewrote every variable's derivatives to the same token, so in `x' = …, y' = …`
   the two unknowns became one. It parsed, solved, and returned a confident wrong answer.
7. **An asynchronous path that could never run.** The typesetting widget was written to
   paint a cached image immediately and hand a miss to a worker — but the function it
   asked rendered on a miss instead of reporting one, so the branch was unreachable.
   `functools.lru_cache` cannot be asked whether it holds a key without computing it;
   telling a *miss* from a *known-negative* needs a cache you own.
8. **A singularity reported as a division by zero.** `t²y'' + ty' - y = 0` started at
   `t = 0` made `f(t₀, y₀)` infinite, which drove the automatic starting step to zero and
   then divided by it — surfacing as a bare `ZeroDivisionError` from inside a step-size
   heuristic, naming nothing the user had written. `ODEProblem` already validated the
   *shape* of `f(t₀, y₀)` up front for exactly this reason; it now validates finiteness
   too.
9. **A controller instance carried its history between solves.** `make_controller`
   returns a caller-supplied `Controller` unchanged, so the error norm from the end of
   one solve became the PI history for the *first* step of the next — a step that has no
   history by definition. Reusing one object across two identical solves gave 82 steps
   and then 83. Nothing raised, both answers were within tolerance, and the only symptom
   was that the same computation run twice was not reproducible. Found by writing
   `tests/test_controllers.py`, which existed because `controllers.py` had no direct
   tests at all.
10. **Floating-point substitution hid the repeated root.** Putting `c = 1.0` into
   `y'' + 2c·y' + y = 0` as a float gave two roots that were numerically equal, each with
   a whisker of imaginary part, so the critically damped case — the one interesting point
   on the whole slider — was reported as underdamped. Substituting exact rationals lets
   sympy see `(r + 1)²` and return one root of multiplicity two.

A recurring theme, worth stating plainly: **the tests that mattered most were the ones
checking a claim rather than an output.** Every one of these passed every accuracy test
while being wrong.

### Scope

Deliberately **not** included, and why:

- **BDF / multistep methods.** Variable-step-variable-order BDF is the most bug-prone
  code in a solver of this kind, and Radau plus RODAS4 already cover the stiff case.
  SciPy's `BDF` and `LSODA` outperform this library on stiff problems partly as a result;
  that trade is intentional.
- **BVP collocation.** Multiple shooting reuses the IVP solver wholesale and reaches the
  same problems; collocation would have been a second, parallel implementation.
- **Adjoint sensitivities.** Forward sensitivities cover parameter fitting at the scale
  this library targets; adjoint needs backward integration with checkpointing.
- **ROS3P**, removed for the reason above.

---

## Install

```
py -3.10 -m pip install -e .          # library only: numpy, scipy
py -3.10 -m pip install -e ".[app]"   # + PySide6, pyqtgraph, matplotlib, sympy
py -3.10 -m pip install -e ".[dev]"   # + pytest
```

Requires Python 3.10+. Tested on 3.10.11 with numpy 2.2.6 and scipy 1.15.3.

The library never imports Qt. `odesuite` and `odesuite_app` are separate packages, and
the application talks to the library through a view-model that imports no widget — so the
solver stays usable, testable and installable with no interface attached.

## Layout

```
src/odesuite/                                        the library (~5 700 lines)
  problem.py solution.py driver.py controllers.py    core
  tableaux.py dense.py events.py                     coefficients, interpolants, roots
  linalg.py newton.py stability.py                   Jacobians, LU cache, Newton, R(z)
  steppers/  erk irk rosenbrock symplectic
             exponential taylor                      the methods
  bvp/shooting.py  sensitivity.py                    BVPs, dy/dp
  problems/                                          ~28 benchmark problems

src/odesuite_app/                                    the studio
  theme.py catalog.py state.py solver.py             palette, metadata, view-model
  analysis.py custom.py                              phase-plane maths, sympy systems
  symbolic.py dsolve_worker.py                       closed forms, in a killable process
  equationmodel.py mathrender.py                     typed equations, LaTeX typesetting
  screens/   home lab portrait stiffness
             race accuracy                           the six screens
  widgets/                                           sliders, cards, plots, maths

tests/         998 tests
benchmarks/    the four static figures
packaging/     PyInstaller spec and launcher
```

## License

MIT — see [LICENSE](LICENSE).

The library itself depends only on numpy and scipy, both BSD-licensed, so `odesuite` is
unencumbered. Note that the **studio** additionally pulls in PySide6, which is LGPLv3:
that has no bearing on this project's own terms, but redistributing the frozen
`odesuite-studio` bundle carries the LGPL's relinking obligations for the Qt parts.

## References

Hairer, Nørsett & Wanner, *Solving Ordinary Differential Equations I & II* — the source
for the Radau, RODAS and step-control algorithms. Kassam & Trefethen, *Fourth-order
time-stepping for stiff PDEs*, SIAM J. Sci. Comput. 26 (2005) — the contour-integral
evaluation of the φ functions. Tsitouras, Comput. Math. Appl. 62 (2011); Bogacki &
Shampine, Appl. Math. Lett. 2 (1989); Cash & Karp, ACM TOMS 16 (1990).
