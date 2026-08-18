# Core

The four objects a solve is made of. `ODEProblem` says *what* to integrate,
`solve` runs the loop, and `Solution` is what comes back.

`solve` takes a `callback(t, y, stats)` called after every accepted step;
returning `False` stops it and the solve comes back with
`status="cancelled"`. That one parameter covers progress reporting, live
plotting, streaming output to disk, and cancellation from another thread —
they are the same problem, which is that nothing else in the loop offers a
way in. See
[`examples/09`](../examples.md#09-progress-cancellation-and-hidden-events).

::: odesuite.ODEProblem

::: odesuite.solve

::: odesuite.Solution

::: odesuite.Stats

::: odesuite.Event
