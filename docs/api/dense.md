# Continuous output

A solver's output times are chosen for the solver's convenience. With
`dense_output=True` the solution becomes a function you can evaluate anywhere,
and for a method with a native continuous extension the interpolant is nearly as
accurate as the steps themselves — so this is not resampling, it is the answer
the method already computed.

Event location is built on the same machinery: a root is found *on the
interpolant*, so its accuracy is set by the continuous extension rather than by
how large the steps happened to be.

::: odesuite.DenseOutput

::: odesuite.Interpolant

::: odesuite.HermiteInterpolant

::: odesuite.RKPolynomialInterpolant
