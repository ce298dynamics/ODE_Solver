# Beyond the initial value problem

Boundary value problems by multiple shooting, and parameter sensitivities by
internal differentiation. Both reuse the IVP solver rather than reimplementing
an integrator.

## Boundary value problems

::: odesuite.BVProblem

::: odesuite.solve_bvp

::: odesuite.BVPSolution

## Sensitivities

`dy/dp` integrated alongside the state, so it comes out to the same tolerance as
the state. Note the practical warning in
[`examples/06`](../examples.md#06-parameter-sensitivities): at tight tolerances
you must supply a Jacobian, or the finite-difference approximation's `sqrt(eps)`
noise floor makes the Newton iteration thrash.

::: odesuite.forward_sensitivities

::: odesuite.SensitivitySolution
