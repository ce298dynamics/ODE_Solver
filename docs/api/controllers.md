# Step control

A controller sees only a scalar error norm, the method's error order, and the
step just taken — never the method itself. That is what lets the same controller
drive an explicit pair and a Radau solve, and what lets you write your own.

Which controller a method gets by default is the *method's* choice, via
`Stepper.default_controller`: a step-size change is free for an explicit method
and costs an `O(n³)` refactorisation for an implicit one.

::: odesuite.Controller

::: odesuite.PIController

::: odesuite.PredictiveController

::: odesuite.IController

::: odesuite.error_norm

::: odesuite.initial_step_size
