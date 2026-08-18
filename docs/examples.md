# Examples

Eight runnable scripts in [`examples/`](https://github.com/), one per capability.
Every one of them is executed by the test suite (`tests/test_examples.py`) and
asserts something about its own result, so they cannot quietly rot — and they
check the library rather than merely proving they do not crash.

```
py -3.10 examples/01_getting_started.py
```

## 01 · Getting started

An initial value problem, then evaluating the answer *between* the steps.
Introduces `dense_output=True`, the `Stats` counters, and the cheapest honest
accuracy check available: a conserved quantity, which needs no reference
solution.

## 02 · Events

Locating where `g(t, y) = 0` to machine precision. A dropped ball's impact time
comes out to 2e-16 of the closed form in six steps, because the root is found on
the step's interpolant rather than at a step boundary. Shows `terminal` and
`direction`, and that the integration stops *at* the event.

## 03 · Stiff problems and Jacobians

Robertson's kinetics over eleven decades. First the failure: an explicit method
is not slow here, it is stability-bound, and more steps do not help. Then the
same problem implicitly, with the analytic and finite-difference Jacobian routes
agreeing to 5e-14.

## 04 · DAEs via a singular mass matrix

`M y' = f` with `M` singular turns the same code path into an index-1 DAE
solver. Shows why the method must be stiffly accurate — the constraint residual
comes out at 1e-16 rather than merely small — and that an explicit method
refuses the problem instead of drifting off the constraint manifold.

## 05 · Boundary value problems

`y'' = -36y` with both ends pinned, by multiple shooting. Every segmentation
from 1 to 10 nodes finds the same curve, which is the point: more segments is a
conditioning choice, not a different answer. The residual history shows Newton
solving a linear problem in a single step.

## 06 · Parameter sensitivities

`dy/dp` by internal differentiation, checked against a differentiated closed
form, then used to drive a Gauss-Newton fit that recovers both parameters to ten
digits in five iterations.

Contains a measured warning worth reading before you use this at tight
tolerances: **supply a Jacobian.** Without one the augmented system is
differenced, and a finite-difference Jacobian is accurate to about `sqrt(eps)`.
Ask for `rtol=1e-12` and the Newton iteration is being asked for an accuracy its
iteration matrix does not have — 29 000 steps and 3 800 rejections, against
1 156 steps and one rejection with the derivative written down.

## 07 · Symplectic integration

Accuracy and qualitative fidelity are different properties. Over 200 Kepler
orbits, DOPRI5 is three orders of magnitude more accurate than Verlet and its
energy error *doubles as the interval doubles*, while Verlet's is a bounded
oscillation — the same size at the end as at the start.

## 08 · A method and a controller of your own

Registering Ralston's third-order method as a `ButcherTableau` — coefficients,
not code — and then *measuring* its order rather than trusting the label: 3.00
against a claim of 3.

Also two custom controllers, which is the whole contract in four lines each: one
that never changes the step (what a convergence study needs, since `first_step`
only sets the first step) and one that refuses to grow it by more than 20%.

!!! note "A bug this example caught while being written"

    The embedded weights were first borrowed from a *different*, four-stage
    tableau and summed to 0.875 rather than 1 — not a consistent method at any
    order. The error estimate became a constant offset that no step size could
    satisfy, and the solver ground to a halt after a million steps rather than
    returning a wrong answer. The example now asserts both weight vectors sum to
    one, which is the cheapest check there is and catches the most common way of
    getting an embedded pair wrong.
