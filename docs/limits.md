# When each method fails

Every method here works. This page is about where each one stops working, which
for a solver is the more useful half and the harder half to find out by reading
the source.

Every number below was measured on the shipping code. Where a limit has since
been removed it is recorded as removed rather than deleted, because knowing that
something *used* to be a trap is how you avoid reintroducing it.

Wall-clock figures were taken on an idle machine. That caveat is here because an
earlier round of measurement was taken on a machine saturated by a parallel test
run and reported import times ten to twenty times too large; step counts, error
magnitudes and convergence orders do not depend on load, and those are what most
of this page rests on.

---

## The short version

| If you are here because… | Use |
|---|---|
| an explicit method is taking forever | `radau` or `rodas4` |
| the problem has a mass matrix, or is a DAE | `radau` or `rodas4` |
| energy drifts over a long orbit | `verlet`, `yoshida4/6/8` |
| you need accuracy near machine precision on a smooth problem | `taylor20` |
| a stiff linear operator plus a mild nonlinearity (a discretised PDE) | `etdrk4` |
| nothing above applies | `dopri5` (the default) |

---

## Forward Euler — `euler`

**First order, fixed step, no error estimate.** It cannot choose its own step:
`solve` requires `n_steps` or `first_step`, and says so —

```
ValueError: Euler runs at a fixed step size; pass n_steps or first_step
```

**It is unconditionally unstable on an oscillator.** Not slow, not inaccurate:
unstable. Euler's stability region is a disc tangent to the imaginary axis at
the origin, and a purely oscillatory problem sits exactly on that axis, so the
amplitude grows for *any* step size. On the harmonic oscillator over 10 000
periods it overflows to infinity, and because a fixed-step method cannot reduce
its step in response, the failure is immediate and final:

```
the solution became non-finite at t=… Euler runs at a fixed step size and
cannot reduce it: pass a smaller first_step or a larger n_steps, or use an
adaptive method (dopri5, tsit5) or an A-stable one (radau, rodas4) if the
problem is stiff
```

**Use it to learn what a step size costs**, which is what the Learning Hub uses
it for, and not to get an answer.

## Classical Runge–Kutta — `rk4`

**Fourth order, fixed step, no embedded pair.** Same requirement for `n_steps`
or `first_step`, for the same reason: this library declines to invent an error
estimate for a method that has none. A made-up estimate would let RK4 pretend to
adapt while the controller flew blind.

**Its energy error grows without bound.** Over 10 000 periods of the harmonic
oscillator at 50 steps per period, RK4's relative energy error is **−2.69e-2**
at the end and **2.69e-2** at its worst — the same number, which is the
signature of monotone drift. Störmer–Verlet over the identical run ends at
**−1.17e-3** having been as large as **3.95e-3**: the worst is larger than the
last, because the error oscillates instead of accumulating. If you are
integrating an orbit for a long time, order is not the property you want.

## The explicit adaptive pairs — `rk23`, `rkf45`, `cashkarp`, `dopri5`, `rk45`, `tsit5`

The general-purpose family, and `dopri5` is the default for good reason.

**They cannot solve a stiff problem.** An explicit method's step size is limited
by *stability*, not accuracy, so on a stiff problem it takes minute steps
indefinitely. `solve` now notices and stops:

```python
from odesuite import solve
from odesuite.problems import robertson
solve(robertson(t_end=1e11).problem, "dopri5", rtol=1e-6)
# failed after ~5000 steps, 0.26 s:
#   DOPRI5 covered 0.000% of the interval in 5000 steps and, at the step size
#   it is now taking, would need about 1.1e+14 to finish — past the
#   max_steps=1000000 limit.
```

Before that check existed the same call spent **499 996 steps and 33 seconds**
arriving at the same conclusion, and then blamed the step count. Radau solves
the same problem in **239 steps**. Pass `progress_check=False` if you want to
watch the grind.

**They reject a mass matrix outright.**

```
ValueError: DOPRI5 cannot integrate a problem with a mass matrix; use an
implicit method (radau, rodas4)
```

**Only `dopri5` has a native continuous extension.** Its dense output is fourth
order and free. `rk23`, `rkf45`, `cashkarp` and `tsit5` fall back to a cubic
Hermite interpolant — third order, also free, but below the order of the step
itself. It is ample for event location and `t_eval` sampling; it is not what you
want if you are integrating at `rtol=1e-12` and reading the answer *between* the
steps.

**`rk23` under-delivers on tolerance by a roughly constant factor.** On
`y' = -2y` the achieved error is about **20×** the requested `rtol`, flat across
nine decades from 1e-3 to 1e-12. That is the ordinary gap between local error
control and global error for a low-order pair, not a defect — but if you asked
for 1e-6 and needed 1e-6, use a fifth-order pair, where the same measurement
gives 1.3–3.8×.

## Radau IIA — `radau`, `radau5`

Fifth order, L-stable, stiffly accurate: the reference method for stiff systems
and index-1 DAEs.

**Each step is expensive.** It solves genuinely nonlinear stage equations by
simplified Newton, so a step costs several right-hand side evaluations and,
periodically, an `O(n³)` factorisation. On Robertson: 239 steps, 2648 right-hand
side evaluations, **14** Jacobian evaluations and 250 factorisations. The low
Jacobian count is the point — a stale Jacobian costs Newton iterations but not
accuracy, so it can be reused across many steps.

**A step can fail to converge.** When simplified Newton diverges, the step is
reported as not completed, the driver shrinks `h` and retries with a fresh
Jacobian. This is handled, but it means a badly scaled problem can spend real
work on rejected steps. Supplying an analytic `jac` is the single best thing you
can do for it.

**Fixed — it used to miss tight tolerances silently.** Below `rtol = 1e-9` the
achieved error stopped tracking the request: **15×** too large at 1e-10, **30×**
at 1e-11, **54×** at 1e-12 and **103×** at 1e-13, while `success` stayed `True`.
The cause was the Newton termination being a fixed 3% of the integration
tolerance, which is negligible at loose tolerances and dominant at tight ones.
It now scales as `rtol**(1/order)`, and the ratio at 1e-12 is **0.77×**. Work at
the default `rtol=1e-6` is unchanged.

**The unsplit solve is no longer a method you can name.** It assembles and
factorises the full `3n × 3n` system instead of the diagonalised one — about
five times the linear algebra for an identical answer — and exists so the tests
can check the fast path against an obviously-correct one. It used to be
registered as `radaudense`, which meant `make_stepper` offered a test oracle as
a suggestion when you mistyped `radau`. Construct it directly if you want it:

```python
from odesuite.steppers import RadauIIA
solve(problem, RadauIIA(linear_solve="dense"))
```

## RODAS4 — `rodas4`

Fourth order, L-stable, stiffly accurate, and the cheapest correct way to solve
a stiff system: linearly implicit, so there is no Newton iteration and nothing
can fail to converge.

**It pays for that with a Jacobian every single step.** The coefficients are
only valid for the exact Jacobian, so unlike Radau it cannot reuse a stale one.
On Robertson: 246 steps, **249** Jacobian evaluations and 249 factorisations,
against Radau's 14 and 250. If your Jacobian is expensive — a large
finite-difference one especially — Radau will usually win.

**It needs `∂f/∂t`, and how well it knows it decides how accurate it can be.**
That term enters the step as `h·d_i·f_t`, so an error `e` in the derivative
contributes `O(h·e)` — *first order*, whatever the order of the method around
it. Differenced, this used to cost three orders of accuracy on any
non-autonomous problem: on `y' = y·cos t` RODAS4 held order 4 down to 2.8e-11
and then converged at order **0.98**, flattening near 4e-13, while on an
autonomous problem it ran clean to 1.9e-14. The difference is now central rather
than forward and order 4 holds to **1.3e-14** — but you can do better by
supplying it:

```python
ODEProblem(f, t_span, y0, jac=..., dfdt=lambda t, y: ...)
```

**A Rosenbrock method that is not stiffly accurate cannot solve a DAE**, and the
library refuses rather than returning a drifting answer. RODAS4 is stiffly
accurate, so it can. ROS3P was implemented for this slot and **deleted**: its
embedded error estimate vanished identically on every test problem, which makes
an adaptive solver accept every step it is offered — silently wrong rather than
merely slow.

## Symplectic — `verlet`, `yoshida4`, `yoshida6`, `yoshida8`

For a separable Hamiltonian system, these preserve the structure exactly rather
than approximately. Energy error stays *bounded* forever instead of
accumulating.

**They need a separable second-order system, and will not guess.**

```
ValueError: symplectic methods need a separable second-order system; build the
problem with odesuite.second_order_problem(...)
```

**The step size must be constant.** Adaptive stepping destroys symplecticity,
so a variable-step "symplectic" method is neither. These declare themselves
non-adaptive, carry no error estimate, and require `n_steps` or `first_step`.
There is no way to ask them for a tolerance, and that is deliberate.

**Verlet is only second order.** Over one orbit `dopri5` is far more accurate.
The trade is the one shown above: bounded oscillation against monotone drift.
Choose on the length of the integration, not the order.

**Higher orders cost proportionally more.** `yoshida4/6/8` are compositions of
Verlet substeps — 3, 9 and 27 of them respectively. Over the 10 000-period run:
Verlet 9.0 s, `yoshida4` 22.6 s, `yoshida6` 54.3 s, for end-of-run energy errors
of 1.17e-3, 1.43e-5 and **1.08e-11**.

## Exponential — `etdrk4`

For a semilinear problem `u' = L u + N(u)`, this treats the stiff linear
operator *exactly* via `exp(hL)` and applies Runge–Kutta only to the mild
nonlinearity. The stability restriction from `L` disappears entirely: no
Jacobian, no Newton, no linear solves.

**It needs the splitting, given explicitly.**

```
ValueError: ETDRK4 needs a semilinear splitting u' = L u + N(u); build the
problem with odesuite.semilinear_problem(...)
```

**Fixed step.** The φ-function coefficients are built for a particular `h`, so
`h` cannot vary; `n_steps` or `first_step` is required. Changing `h` means
rebuilding the coefficients, which is why it is not merely inconvenient but
expensive.

**It only helps when the problem really is semilinear** — the stiffness has to
live in `L`. A nonlinearity that is itself stiff gets no benefit, because that
part is still integrated explicitly.

## Taylor series — `taylor8`, `taylor20`, `taylor30`

Arbitrary order by jet arithmetic: it computes the Taylor coefficients of the
solution directly, exactly, with no coefficient tables to mistype. On a smooth
problem this is remarkable — `taylor20` reaches machine precision on
`y' = y·cos t` in a handful of steps.

**The right-hand side has to be expressible in jet arithmetic.** `+ - * / **`,
`exp`, `log`, `sqrt`, `sin`, `cos`, `tanh` and negation are supported. `abs`,
comparisons, `min`/`max`, and anything that branches on the state are not:

```
TypeError: bad operand type for abs(): 'Jet'
```

**Complex states are refused**, because jet coefficients are real:

```
ValueError: Taylor8 does not support complex states; jet arithmetic is
real-valued. Use an explicit method or ETDRK4.
```

**High order reaches the round-off floor almost at once**, which is the point
but also a trap when measuring it: `taylor8` on `y' = -2y` has a relative error
of 3.3e-9 at 32 steps, 1.1e-11 at 64, and 4.2e-14 at 128 — after which
refinement buys nothing and a convergence-order measurement becomes meaningless.

**Fixed — it used to kill the interpreter.** `solve(problem, "taylor20")` on
`y' = y * np.cos(t)`, written the obvious way with the whole state array at
once, exited with no traceback and no Python exception: `Jet`'s array
interoperability recursed until the C stack was exhausted. Both routes now walk
the array elementwise, so that right-hand side does not merely stop crashing —
it works, to 5.8e-15 at order 20.

**There is no adaptive-order logic.** `taylor30` is order 30 on every step,
whether the solution needs it or not.

**There is no bare `taylor`.** It used to exist and silently meant `taylor20`.
The order is the whole point of this family, so a name that hides it is the one
thing it cannot afford — `rk45` survives as an alias because it names a method
people already know by that name, and `taylor` named nothing.

---

## Limits that are not a method's fault

These belong to the problem, not the solver, and no choice of method removes
them. They are here because the solver is where you will meet them.

### A solution that blows up in finite time

`y' = y²`, `y(0) = 1` runs to infinity at `t = 1`. The solve stops there and
says so:

```
step size underflow at t=1: required h=2.16e-15 is below the local
floating-point resolution. The solution may be singular or blowing up there
```

`Solution.diagnosis.kind` is `"step_underflow"`, and `diagnosis.t` locates it to
1e-6. Note what the diagnosis does *not* claim: a singularity on the path
(`y' = 1/(t-1)`) produces the identical kind, because from inside the loop the
two are indistinguishable — finite state, collapsing step. A kind called
`blow_up` would have been a guess.

### A right-hand side that returns `NaN`

Distinct from the above, because the loop *can* tell this apart: the state
itself goes non-finite rather than the step collapsing. `diagnosis.kind` is
`"nonfinite"`.

### Uniqueness that does not hold

`y' = y^(1/3)`, `y(0) = 0` has **two** solutions through the origin: `y ≡ 0` and
`y = (2t/3)^(3/2)`. A numerical method returns one of them — here `y ≡ 0`, in
eight steps, with `success` set. No method can do better, because there is no
answer to be right about. What the application does now is *notice*:
`analysis.uniqueness_warning` differences `∂f/∂y` at the initial point over
offsets four decades apart and reports that it is unbounded. The discriminator
is *growth* rather than size — Van der Pol at μ=1000 has `∂f/∂y ≈ 3e3` and
Robertson `≈ 3e5`, both perfectly well defined.

### A discontinuous right-hand side

`y' = sign(t-1)` is integrated across the jump and reports success. The answer
is good — `y(2) = -9.4e-6` against an exact 0 at `rtol=1e-6` — but it cost 22
rejected steps clustered at `t = 1`, and `Solution.rejected` records exactly
where the solver struggled.

### Event crossings between steps

Endpoint bracketing loses any *even* number of crossings inside one step, and
loses them without a trace: `g` has the same sign at both ends. On a smooth
decay with `g = sin(20t)` over `[0, 10]`, **63** roots exist and the default
finds **7**. The step size is chosen to resolve the solution, not the event.

`Event(g, subdivisions=8)` finds all 63. And `Solution.incomplete_events` now
names any event for which a mid-step probe *proved* crossings were missed — so
you can find out you needed it. `Solution.events_complete` being False is
certain; True means only that nothing was caught going missing.

### Chaos

Lorenz at standard parameters, two initial conditions `1e-10` apart, both at
`rtol=1e-12`: the separation is 1.8e-10 at `t = 10`, 2.1e-3 at `t = 30` and
**6.5** at `t = 40`. The fitted largest Lyapunov exponent is 0.84 against the
literature's 0.9056, giving a predictability horizon around `t ≈ 27`. Past that,
a single trajectory carries no information about where the system actually is —
the attractor is the prediction, the path is not. No tolerance fixes this; a
tighter one buys a logarithmically longer horizon.

### The interval a symbolic answer is valid on

`y' = y²`, `y(0) = 1` has the closed form `y = 1/(1-t)`, which means nothing for
`t ≥ 1`. `symbolic.interval_of_validity` reports `(-∞, 1)`, and declines rather
than guessing where it cannot tell: `tan(t)` has poles at every odd multiple of
π/2 and no denominator to show for them, so anything reading only the
denominator would claim "valid everywhere".
