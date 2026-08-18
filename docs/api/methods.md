# Methods

Every method is a `Stepper`: it advances the solution by exactly one step of a
given size and reports what happened. It does not choose the step size, decide
whether to accept, or know about events or output — those belong to the
controller and the driver. That boundary is why events, dense output, mass
matrices and sensitivities are each written once rather than once per method.

## The contract

::: odesuite.Stepper

::: odesuite.StepResult

::: odesuite.make_stepper

## Explicit Runge–Kutta

One generic stepper driven entirely by a Butcher tableau — adding a method is
coefficients, not code. See
[`examples/08`](../examples.md#08-a-method-and-a-controller-of-your-own).

::: odesuite.ExplicitRungeKutta

## Implicit and stiff

::: odesuite.RadauIIA

::: odesuite.Rosenbrock

## Structure-preserving and special

::: odesuite.StormerVerlet

::: odesuite.CompositionMethod

::: odesuite.TaylorMethod

::: odesuite.ETDRK4

::: odesuite.Jet

## Problem shapes these methods require

::: odesuite.second_order_problem

::: odesuite.semilinear_problem

## Coefficients

::: odesuite.ButcherTableau

::: odesuite.get_tableau
