# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security

- **A typed equation could run arbitrary code.** Parsing already emptied
  `__builtins__` so that no *name* resolved to anything dangerous, and that part
  was right. It was not enough: a name whitelist says nothing about where an
  expression may go *from* a name that resolves legitimately. `sin` is
  whitelisted, and

      sin.__class__.__init__.__globals__["__builtins__"]

  is the real builtins, `__import__` included — reached without naming a single
  forbidden thing. Both places a user can type an expression were affected: the
  "build your own system" editor and the equation editor. In the latter the
  payload ran and its return value became the equation's right-hand side, so
  the only outward sign was an answer that looked odd.

  `custom.reject_unsafe_syntax` closes it by checking the text **as typed,
  before sympy compiles it** — after `parse_expr` returns, a payload has already
  run. It refuses the construct rather than the name: no attribute access, no
  subscripting, no lambdas or comprehensions, and calls only to a bare name.

  Refusing constructs rather than names is the whole design. A name is already
  harmless once `__builtins__` is empty — sympy's own `auto_symbol` turns an
  unknown one into a `Symbol` rather than resolving it — so the only way out is
  an attribute, and that is what is now gone. Going the other way would have
  meant every caller knowing about `y(t)`, `Heaviside`, `DiracDelta`, the
  derivative placeholders and every parameter a lesson happens to use, and a
  name wrongly left out is a lesson that stops working. A guard that rejected
  `sec(t)` would have been a worse bug than the one it fixed, which is why
  `tests/test_security.py` asserts in both directions: known escapes are
  refused and proved not to have run, using a canary file, *and* every equation
  the course itself contains still parses.

  `SECURITY.md` now records the reporting route and what is in scope.

### Fixed

- **Radau missed the tolerance it was asked for, and reported success.** Below
  `rtol = 1e-9` the achieved error stopped tracking the request: 15x too large
  at 1e-10, 30x at 1e-11, 54x at 1e-12, 103x at 1e-13, while DOPRI5 held 1.8x
  across the same range.

  Not the step controller — the step count was rising 1.78x per decade, more
  than the 1.58x a fifth-order method needs — and not the differenced Jacobian,
  since supplying an analytic one changed the answer in no significant figure.
  It was the Newton termination. The stage equations were solved to a fixed 3%
  of the integration tolerance, and a fixed fraction is the wrong shape: the
  per-step nonlinear error accumulates over a step count that itself grows like
  `rtol ** (-1/order)`, so holding the fraction constant lets the Newton error
  overtake the truncation error exactly when the caller has asked for accuracy.

  `newton_tol_factor` now scales it as `rtol ** (1/order)`, which cancels that
  growth, capped so loose tolerances keep the behaviour they had. Measured: the
  ratio at 1e-12 goes from 54.5x to 0.77x. Work at the default `rtol = 1e-6` is
  unchanged — 584 evaluations before and after — and the stiff set (Robertson,
  HIRES, OREGO, Van der Pol at mu=1000) is identical to the evaluation. Only
  the tight end pays, about 9% more evaluations for 50-70x the accuracy.

  The iteration budget moves with the target, which is not optional: tightening
  one without the other turns a converging solve into a reported failure. On the
  logistic equation at `rtol = 1e-13` the iteration was converging at a rate of
  0.013 — two decimal digits a pass — and still ran out of its eight iterations
  before reaching a target twenty-five times tighter. The step came back as not
  converged, and Radau's local-error test stopped measuring anything and skipped
  instead. `newton_iteration_budget` allows two further iterations per decade of
  tightening, which is what a linearly converging iteration needs.

  A caller who passes their own `NewtonSettings` chose those numbers and keeps
  them.

- **RODAS4 lost three orders of accuracy on any non-autonomous problem.** It
  held order 4 on `y' = y cos t` down to 2.8e-11 and then converged at order
  *one*, flattening out near 4e-13 — while on an autonomous problem the same
  method ran clean to 1.9e-14.

  The `df/dt` term enters a Rosenbrock stage as `h * d_i * f_t`, so an error `e`
  in that derivative contributes `O(h * e)` to the step: first order, whatever
  the order of the method around it. Differenced forward, `e ~ sqrt(eps)`, and
  three orders of accuracy were going to one difference quotient. On an
  autonomous problem the derivative is identically zero, the difference is
  exact, and nothing was visible — which is why this survived a suite that
  measures convergence order.

  Two changes. `ODEProblem` now accepts `dfdt`, so a caller who knows the
  derivative can supply it and skip the approximation entirely. Where it is not
  given, the difference is now central rather than forward, `O(eps**(2/3))`
  rather than `O(sqrt(eps))`. Order 4 now holds to round-off, 1.3e-14, a 60x
  improvement at fine steps. The central difference costs one extra right-hand
  side evaluation per step: on the stiff set that is 14% more evaluations and,
  step counts being identical, nothing else.

- **The Taylor method killed the interpreter.** `solve(problem, "taylor20")` on
  `y' = y * cos(t)` exited with no traceback and no Python exception — not a
  failure a caller could catch or report, and about the most ordinary
  non-autonomous right-hand side there is.

  `Jet` sets `__array_priority__` so that `array * jet` reaches it rather than
  being broadcast, which is right for an array of numbers. For an array of
  *jets* it was wrong twice over: the non-jet branch called `float()` on the
  array, which re-entered jet arithmetic, and `__array_ufunc__`'s handlers are
  written with Python operators, so `multiply(array, jet)` evaluated
  `array * jet` — the same ufunc again. Either recursion exhausts the C stack.

  Both paths now walk the array elementwise, which is what the expression meant
  in the first place, so these right-hand sides do not merely stop crashing:
  they work. `y' = y cos t` integrates to 5.8e-15 at order 20. Declining with
  `NotImplemented` was tried and is not enough — defining `__array_ufunc__` at
  all removes numpy's own object loop, so refusing yields a `TypeError` rather
  than the elementwise answer. Combining a jet with something that is neither a
  jet nor a number now says so, instead of failing inside numpy.

  The interface was never exposed: Taylor is offered only for catalogue entries
  that set `supports_taylor`, and all eighteen of them were checked.

- **A fixed-step method that overflowed spun until `max_steps`, then blamed the
  step count.** Euler on a harmonic oscillator is unconditionally unstable, so
  it overflows; the driver answered by halving the step, which does nothing for
  a method whose step is derived from the interval rather than from `h_abs`.
  The identical failing step was retried 909393 times over 13.7 seconds, and
  the solve then reported `exceeded max_steps` for an overflow it had already
  recorded.

  A fixed-step method cannot reduce its step — that is the caller's choice, not
  the solver's — so the first failure is now the last one, and the message says
  what happened, that the method runs at a constant step, and what to do about
  it. Adaptive methods are untouched: shrinking is the right answer for a method
  that can shrink.

- **A quiz test depended on when it was run.** The paper is seeded from the
  clock, which is right for a quiz — sitting it twice should not give the same
  questions — and wrong for a test. One test typed `"0"` and asserted it was
  marked wrong, on the strength of a comment reading "almost certainly wrong";
  once numeric drills existed, some questions have 0 as their answer, and the
  test failed on the runs that drew one. Reproducible under `pytest -n auto`,
  passing in isolation, which is the signature that makes such a flake expensive
  to chase.

  `QuizScreen.seed_override` is the seam — nothing in the application sets it,
  and a test that needs a particular paper can. The test now *finds* a question
  it can miss rather than assuming one, so it no longer depends on the content
  either.

- **A right-hand side that raised at `t0` escaped as a bare exception.**
  `ODEProblem` already checked that `f(t0, y0)` is finite, and the comment on
  that check says it exists so a singular starting point does not surface as "a
  bare ZeroDivisionError ... naming nothing the caller had written". It caught a
  right-hand side that *returned* `inf` and not one that raised on the way, so
  `y' = 1/t` started from `t = 0` produced exactly the message the check was
  written to prevent. It is now wrapped with the same wording.

### Removed

- **`radaudense` is no longer a method name.** It is the unsplit `3n × 3n`
  Radau solve — the oracle the fast path is validated against, about five times
  the linear algebra for an identical answer — and having it in the registry
  meant `make_stepper` offered a test oracle as a suggestion when you mistyped
  `radau`. Construct it directly with `RadauIIA(linear_solve="dense")`, which is
  the real interface and what `tests/test_radau.py` now uses.

- **`taylor` is no longer a method name.** It silently meant `taylor20`, and the
  order is the whole point of that family — a name that hides it is the one
  thing it cannot afford. `taylor8`, `taylor20` and `taylor30` are unchanged.
  `rk45` survives as an alias because it names a method people already know by
  that name; `taylor` named nothing.

- **Three unused density parameters.** `vector_field`, `streamlines` and
  `nullclines` each took a `resolution` argument with a different default that
  no caller ever overrode, which reads as a control the interface offers and
  does not. They are now named constants with a comment on what each trades
  against what. `slope_field` keeps its parameter: the lesson figures genuinely
  do vary it, to 19 and 17 against the default 21, so a small figure does not
  crowd. Checked by walking the call graph with `ast`, after a line-oriented
  grep missed the multi-line call sites and nearly took the wrong one away.

### Changed

- **"Open the tool for this topic" now opens it on the topic.** The button
  emitted a screen name and nothing else, so a tooltip promising "with an
  example loaded" landed on an empty screen. It carries the lesson's own
  example and conditions across, and says which screen it is opening and on
  what equation. Where the tool is catalogue-driven and has no box to type
  into — Methods by Hand, Worked Problems — it promises less, because it
  delivers less. A lesson writes a system as one string separated by
  semicolons, so the split happens on the way into the editor's fields.

- **A drill runs from the keyboard alone.** Enter marks what is in the box;
  Enter again draws the next question and puts the caret where the answer
  goes. It was the one part of this application somebody does forty times in
  a row and the one part that needed the mouse for every second action.

  Two things had to be got right. The grader now reports whether it actually
  marked anything, so an empty box or an unpicked option is not spent as a
  turn. And the key is taken once, by the card: a `QLineEdit` emits
  `returnPressed` *and* lets the event travel on, so wiring both checked and
  advanced on a single press. A `QShortcut` scoped to the card was the first
  attempt and is the wrong tool — shortcuts are matched against the window,
  so they do nothing until it is active, which makes the behaviour untestable
  and dependent on something the reader cannot see.

- **Rendered mathematics follows the operating system's text scale** (A11Y-04).
  Every font size in this application is written in pixels, and the OS text
  scale reaches Qt as a larger default font point size and nothing else — so
  raising it left the whole interface exactly where it was. Equations were
  the worst case, because they are matplotlib bitmaps and cannot inherit a
  font size at all, and would have been the smallest thing on a page whose
  prose had grown around them.

  `theme.text_scale` reads the factor and `theme.scaled` applies it to the
  application style sheet and to every inline one; `MathLabel` multiplies its
  point size by it and re-renders when the scale moves. Three things were
  found by measuring rather than reasoning. `QApplication.setFont` delivers
  only `FontChange` to a label that has never been shown, not the
  `ApplicationFontChange` the documentation suggests, so both are handled and
  the guard is that the scale actually moved. The render cache is keyed on
  point size, so the two scales cannot collide. And the fixed `pad_inches`
  around a rendered equation was about 40% of its height at 15 pt, which made
  a bitmap rendered at twice the size only 1.55× taller — padding is part of
  the typography, so it grows with the type, and the maths now tracks the
  body text to within 10% across the range.

- **A non-hyperbolic equilibrium is no longer labelled with a definite answer.**
  The Phase Portrait printed `kind` verbatim, in bold. For
  `x' = -y + x(x²+y²)`, `y' = x + y(x²+y²)` that reads "centre" — which is what
  the linearisation says and the opposite of what the flow does, since it
  spirals outward. Lotka–Volterra has the same eigenvalue signature and *is* a
  centre; nothing in the eigenvalues separates the two.

  `FixedPoint.hyperbolic` is the test — no eigenvalue on the imaginary axis, the
  Hartman–Grobman hypothesis — and where it fails the label now says so.
  `analysis.classify` was always scrupulous about this in its docstring; the
  honesty simply stopped at the screen.

- **`sympy` and `PySide6` now carry upper bounds** (`<2` and `<7`). Both are
  couplings that an API check would not catch: `odesuite_app.steps` dispatches on
  sympy's `classify_ode` hint strings, which are internal identifiers with no
  stability promise, so a major release could change which technique a student
  is shown a derivation for without anything failing. `numpy` and `scipy` are
  deliberately left open — the library uses their stable surface, numpy 2 was
  adopted without incident, and pinning them would make `odesuite` awkward to
  install alongside anything else.

### Added

- **A figure for every lesson — the seventeen that had none.** The course
  honoured the rule of four everywhere except its graphical leg, which
  eighteen lessons had and seventeen did not. All thirty-five have one now,
  and `tests/test_lessons.py` asserts it over the whole course rather than
  over a list, so a lesson added later without a picture fails rather than
  quietly being the only one missing a representation.

  The two the audit named as close to indispensable are there. `systems-intro`
  draws the same motion twice — two graphs against time, and one curve in the
  (y, y′) plane — because the reader is entitled to ask what rewriting a
  second-order equation as a pair bought, and that is the answer.
  `eigenvalues` draws the two modes against time with both eigenvalues on
  sliders and the eigenvectors held fixed, which is the one arrangement in
  which "the eigenvalue decides what survives" can be watched in isolation;
  the eigenvector half of the story already had `eigenlines`.

  The rest, in course order: the family of antiderivatives and the condition
  that picks one of it; `v = y/t` straightening a homogeneous family into
  parallel straight lines of slope 2, which is what "the substituted equation
  is separable" looks like drawn; exponential against logistic growth from
  identical r and P(0), with the moment they part company measured rather
  than asserted; two solutions of y″ − y = 0 and every combination of them;
  the b–c plane, whose parabola b² = 4c *is* the three-case distinction;
  sec t against the shapes a guess would have to be built from, with the
  answer variation of parameters produces beside it; three roots and the
  measured point where the largest takes the answer over; an RLC loop and its
  mass–spring twin driven from one set of sliders through L = m, R = c,
  1/C = k; the Laplace integral as the shaded area it actually is, with the
  region of convergence as a place on the axis rather than a proviso; the
  answer to y″ + 3y′ + 2y = sin t rebuilt one pole at a time; a rectangle of
  unit area narrowing onto a delta with the response converging faster than
  it does; the single eigendirection of a defective matrix and the t·e^(λt)
  that makes up the difference; three starts spiralling onto one forced loop;
  the Legendre recurrence as a stem per coefficient, with the stems past
  n = ℓ vanishing the moment ℓ lands on a whole number; and Bessel's leading
  power t^ν against the Frobenius series that corrects it.

  Two measurements changed what was drawn. The impulse pulse is **centred**
  on the instant rather than starting at it — both sequences converge, but a
  pulse that starts there also arrives half a width late, and that offset is
  first order in w, so it dominated the difference and made the convergence
  look far slower than it is; centred, a pulse of width 0.5 matches the
  impulse response to 1.05% of its peak and one of width 0.2 to 0.17%. And
  the higher-order readout reports the leading term's *share* at the end of
  the window rather than only where it crosses a threshold, because "it has
  not taken over yet" with no number attached is the least useful thing it
  could say.

- **A question can now be asked about a picture.** `Choice`, `Numeric` and
  `Solve` carry an optional `figure`, a key into the same registry a lesson's
  own figure comes from, shown above the prompt in Practice, in Drill and in
  the quiz. Until now every question here was about a formula or a number:
  reading a phase portrait — which is most of what the later units are for —
  could be demonstrated to a student and never asked of one.

  Seven questions use it, one per unit, and each is answered by moving the
  sliders on the figure rather than by remembering it: read the slope field
  with a = −1 and say where every solution goes; raise the harvest until the
  two equilibria vanish and say what has happened to the population; cross
  the parabola in the b–c plane and say what the solution does; drag the
  damping until the roots meet and type the value; push s below a and say
  what happens to the area; count the straight-line solutions in a phase
  portrait; read which coefficients the recurrence has just killed.

- **Every plot says in words what it shows, and offers its numbers.** The
  trajectory panel has three tabs — the curve, a paragraph, and a table of
  the output times and states, keyboard-navigable with Ctrl+C to copy. The
  paragraph is also the plot's accessible description, which is what a screen
  reader announces in place of the image, and it is generated by the new
  `describe` module rather than written: the shape comes from counting
  turning points, the limit from comparing the last tenth of the record with
  the endpoint, and blow-up from the solver's own report that it stopped
  early.

  The first turning-point counter was wrong in a way worth recording. It
  counted sign changes of `diff` with small steps discarded, which compares
  *one step* against a fraction of the whole range — so on a finely sampled
  curve every step is small, every step is discarded, and a decaying
  oscillation was reported as turning once. Step size is a property of the
  solver, not of the solution. What is measured now is the *swing*, and
  `tests/test_describe.py` renders the same curve at 200 and at 20 000
  samples and requires the same count.

  Lesson figures gained the same thing for free: each already wrote a readout
  in words, and that readout is now attached to its plots as alternative text
  by the base class, so a figure added later cannot forget to do it. The
  Phase Portrait describes its window, its equilibria and their
  classification from the same `analysis` results the report beside it uses.

- **Four kinds of question the drills could not ask.** Every drill in the
  Hub handed you an equation and asked what to do with it. That is one of the
  things a course examines and not the main one, so there are now twenty more
  drills across fifteen lessons, of four new kinds:

  * **Which method would you reach for first?** — over a pool of real
    equations, in units 1 and 3, with a reason attached to every option. The
    same shape asks which phase portrait a matrix makes and which damping
    regime a spring is in, because those are the same question about
    different nouns.
  * **Write the equation** — a stirred tank, a harvested fish stock, a parcel
    falling against the air, a mass on a spring, an RLC circuit. And the same
    question backwards: here is a family of curves, write the equation it
    solves. Modelling was a third of the applied content and none of the
    practice.
  * **Write one move of the method** — the integrating factor, the
    characteristic equation, the Wronskian, a transform, `det(A − rI)`. The
    only drill that asks what somebody can *produce* rather than what they can
    finish or recognise.
  * **What went wrong here?** — an equation, an answer somebody arrived at,
    and four diagnoses. The wrong answer is generated from the draw, and the
    test suite puts every one of them through `check_answer` and requires the
    verdict its named fault claims: a sign error does not satisfy the
    equation, a dropped constant does and fails only the initial condition.
    The worst question this application could ship is a *spot the mistake*
    whose mistake is not one, and that is what stands in front of it.

  **Two graders for what substitution cannot reach.** `symbolic.check_model`
  decides whether two *equations* are the same — up to a nonzero constant
  multiple, so `y' = 2 - y/20`, `y' + y/20 = 2` and `20y' + y = 40` are one
  answer — and names a multiple that is *not* constant rather than refusing
  it, because dividing `y' = 3y` by `y` is correct algebra one step too far
  and loses the solution `y = 0`. `symbolic.check_expression` does the same
  for a single expression, exactly or up to a constant where the mathematics
  only determines one: an integrating factor is not more right for being
  written without a factor of 5 in front.

  Both keep the discipline `check_answer` already had, and both verdicts are
  proofs. *Right* is proved symbolically, by a difference that simplifies to
  zero. *Wrong* is proved by evaluation: two expressions that agree everywhere
  agree at every point, so one point where they differ settles it — and where
  a constant multiple is allowed, two points whose ratios differ settle it
  just as firmly. Anything else is "cannot tell", never "wrong".

  **Nothing stored in the new questions is taken on trust.** A `Solve` needs
  no answer key because substituting *is* the grading; these four all store
  something, and `tests/test_drill_kinds.py` buys that property back by
  checking every draw against the routine in this application that owns the
  question — `classify_ode` and `steps.preferred_hint` for a method,
  `analysis.classify` for a portrait, the discriminant for a damping regime,
  and for each expression drill a property of the thing asked for: every
  integrating factor is differentiated back, every characteristic polynomial
  compared with the roots the equation actually has, every transform with
  sympy's own. So a question cannot quietly disagree with the tool that would
  answer it, and cannot go on claiming an answer the application has stopped
  giving.

- **Drills can be made easier or harder without becoming a different drill.**
  A template may now say which of `easier`, `typical` and `harder` each of its
  draws belongs to, and the card offers the choice where — and only where —
  the family really has a spread. Eight drills have one: the characteristic
  roots split by discriminant, with the repeated root filed as the hard case
  rather than the tidy one; the integrating factor by whether `p` is a
  constant, a power of `t`, or something that integrates to a logarithm.
  A drill that offered three difficulties over draws that were all the same
  would teach a student to distrust the label, so most templates still offer
  nothing.


- **A wrong answer is diagnosed, not dumped.** The Practice and Drill cards
  used to print what was left over after substitution, raw: `(1 - 2*t)*exp(t)`.
  That asks the person who has just got the question wrong to do the one piece
  of analysis they have shown they cannot do — and the residual almost always
  names the mistake outright. `symbolic.diagnose` is a ladder of tests over it,
  each of which either fires or does not:

  * the residual equals what substituting `y = 0` leaves → the left-hand side
    vanished, so this is the complementary function and no particular solution.
    The commonest miss in the course, and invisible in a cross;
  * some multiple of the answer is exact → the shape is right and a coefficient
    was dropped, or at `k = -1`, a sign, and nothing else;
  * some constant added to the answer is exact → a constant of integration went
    missing;
  * the answer contains no `t` at all;
  * the residual is zero and the conditions fail → the method is right and the
    constants are not. It names the condition that fails and what the answer
    gives there instead, because "solve for C1" is advice and "at t = 0 yours
    gives y = 2, where the condition asks for 1" is a place to start.

  For a system the same ladder says which equation came out zero and which did
  not — "half right" is a literal statement about a pair — and recognises the
  two components written the wrong way round, which is right mathematics and a
  transcription slip.

  **No rung guesses.** Each one ends in `simplify(...) == 0` or in a root sympy
  actually found, and where none fires the residual is still shown: it is worth
  less than a sentence and a great deal more than silence. `diagnose` cannot
  raise, because it is asked on every wrong answer and a rung that threw would
  turn a cross into a traceback. It costs 0.01–0.10 s against the 0.1–0.5 s the
  check itself already takes.

- **The quiz report says how far each wrong answer got.** A column of crosses
  records that four questions were missed and throws away every distinction
  between them at the moment those distinctions are most useful. Each miss now
  carries the verdict it was given: the diagnosis above for a typed answer, the
  reason for the option picked for a multiple-choice one — the distractors are
  written as one misconception apiece — the value missed for a number, and
  *skipped* for a question left alone, which is not evidence about the
  mathematics and should not be filed with the ones that are. The note is
  pinned by the first answer, exactly as the verdict is, so the report cannot
  describe an attempt that was never scored.

- **Which option was picked is remembered, not just that one was.** Progress
  files gain a version 4 field, `picks`: the options chosen for a
  multiple-choice question, most recent last, capped at the last twelve. The
  Course Map's Review panel reads them back — *"A habit, not a slip: in
  Undamped or damped you have chosen “An oscillation inside a decaying
  envelope” 3 times out of 4"*, with that option's own reason after it. It is
  the third question about a record, after how much is done and how long ago,
  and the only one of the three that can be answered with a sentence rather
  than a bar.

  **A shown position is not an option.** Generated questions shuffle their
  options per draw, deliberately, so that a drill teaches content rather than
  position — which also means a tally of positions would count a different
  option every time. `Choice.origins` keeps the shuffle that produced the
  question and `Choice.canonical` inverts it, so what is stored is the option
  *the author wrote*, stable across every draw; `generate.option_written` turns
  it back into the words somebody clicked. Questions whose right answer moves
  from draw to draw — the classification drills — are skipped rather than
  guessed at.

  Older files load untouched and gain the field when next written; a `picks`
  list somebody has edited by hand loses the entries that are not option
  indices and keeps the record, because losing a tick that was earned over a
  field that only decides the wording of a hint would be the worse bug.

- **The largest Lyapunov exponent, with an error bar that means something.**
  Lorenz shipped tagged `chaotic` with no way to quantify the chaos — and
  without an exponent there is no predictability horizon to show either.
  `analysis.largest_lyapunov` walks two trajectories a hair apart, renormalising
  every half time unit, and reports the mean log growth rate. On Lorenz:
  **+0.9001 ± 0.0117**, against the literature's 0.9056.

  **The obvious error bar is wrong, and measurably so.** Treating the
  per-interval log growths as independent samples gives a standard error *8.5×
  too large*: over 12 replicates the estimates scatter with a standard deviation
  of 0.0281 while the naive iid formula reports 0.2404. Batch means over ten
  blocks is better and still 3.4× too large at 0.0960. The growths are strongly
  anti-correlated, so treating them as independent overstates the spread — and a
  26% "relative standard error" would have made the routine refuse to report a
  perfectly good answer. The bar is therefore the scatter across independent
  replicates, which measures the thing being reported rather than modelling it.

  Each replicate starts from a different point on the attractor *and* a
  different perturbation direction. Both matter: replicates sharing a start
  point agree with each other while being wrong together, and on a 15-time-unit
  Lorenz run that produced an error bar of exactly **0.0000** — the precise
  false negative an error bar exists to prevent.

  A verdict comes with it, and the reason is Lotka–Volterra. A conservative
  system's largest exponent *is* zero; measured, it comes out at +0.0039 ±
  0.0046, and a routine reporting "+0.0039, chaotic" would be confidently wrong
  about the most famous non-chaotic system in the catalogue. So the exponent is
  called `chaotic`, `attracting` or `indistinguishable from zero` according to
  whether its own error bar resolves the sign, and `predictability_horizon`
  returns None rather than an enormous number whenever it does not.

- **FitzHugh–Nagumo and SIR are in the catalogue.** FitzHugh–Nagumo is the
  standard excitable-medium model and the cleanest small slow–fast system here;
  it was absent entirely. SIR existed only as a preset inside the
  custom-equation editor, so it never appeared in the gallery and a learner
  could not find it.

  The oscillating window for FitzHugh–Nagumo is *derived*, not looked up:
  `hopf_window` solves `trace J = 0`, giving `I ∈ (0.331281, 1.418719)`. That is
  where the amplitude measurably turns on and off — 1.5e-2 at I = 0.30 against
  3.75 at I = 0.33, and 3.75 at I = 1.42 against 3.4e-5 at I = 1.50 — so the
  model and its own theory cannot drift apart. SIR conserves S+I+R to 1.5e-12
  and carries it as a `Benchmark.invariant`.

- **Sessions: the application reopens where you left it, and a configured
  starting point can be handed to someone else.** "Van der Pol at μ=800, radau,
  rtol=1e-9, on the Stiffness Explorer" could not be written down — closing lost
  it, and an instructor could describe a setup in prose and nothing more. It is
  now saved on close and restored on launch, and `odesuite-gui --session FILE`
  opens a named one. An explicit `--problem` or `--screen` still wins.

  A session stores the *request*, not the result: problem, method, tolerances,
  parameter values, screen. Not the solution, which is recomputed in a fraction
  of a second and would otherwise be a large file that goes stale the moment
  anything changes.

  **A typed equation is stored as its source text and re-parsed on the way back
  in**, which is the security question this feature raises. Every expression the
  parser has ever seen was typed by the person sitting there; a session file can
  arrive from anywhere, and is therefore a *less* trustworthy source than a
  keyboard, not a more trustworthy one. Loading goes through
  `symbolic.parse_equation` — the same door, and so the same
  `reject_unsafe_syntax` check — and a test feeds a hostile session file the
  sandbox-escape payload and asserts nothing ran.

  A bad file is never fatal: missing, truncated, not JSON, not an object, or
  written by a future format all read as "no session". One unusable *field*
  costs that field and not the restore, and a parameter from outside its
  slider's range is clamped rather than restoring a state the interface cannot
  represent.

- **`docs/limits.md` — where each method stops working.** The per-module
  documentation on *how* each method works was thorough; nothing said when each
  one fails, which for a teaching product is the more useful half and the harder
  half to discover by reading source. One section per family: the failure mode,
  a reproduction, the measured number, and what to use instead. Plus the limits
  that belong to the *problem* rather than to any solver — finite-time blow-up,
  a right-hand side returning NaN, uniqueness that does not hold, a
  discontinuous right-hand side, event crossings between steps, chaos, and the
  interval a symbolic answer is valid on.

  Where a limit has since been removed it is recorded as removed rather than
  deleted: Radau's tolerance shortfall, RODAS4's first-order floor and the
  Taylor method's interpreter crash are all on the page as things that *used* to
  be traps, because that is how they stay fixed.

  Two tests keep it honest rather than merely present. One fails if a method in
  `METHODS` gains no entry; the other provokes each error message the page
  quotes and checks the real text still contains it — a page that tells a reader
  to search for wording that no longer exists is worse than one that says
  nothing. The method picker gained a per-family tooltip saying the same thing
  in one line, since that is where the question is actually asked.

- **A solve that cannot finish now says so in under a second instead of half a
  minute.** An explicit method on a stiff problem is limited by stability rather
  than accuracy, so it takes minute steps forever: DOPRI5 on Robertson spent
  499 996 steps and 33 seconds reaching `max_steps`, and then reported the step
  count — the symptom, not the reason. `solve` now projects from the step size
  it is actually managing, and stops when that projection cannot cover the
  remaining interval within the budget. Robertson and Van der Pol at μ=1000 now
  fail in **0.23–0.33 s**, a seventy- to hundredfold improvement, with a message
  naming the fraction of the interval covered, what finishing would cost, and —
  for an explicit method — that an implicit one has no such limit.

  The Method Race test that stages this fell from 15 s to 0.54 s, and the file
  it lives in from 36 s to 5 s.

  **What this is not is a stiffness detector, and the restriction to explicit
  methods is the whole design.** The projection assumes the step size will not
  improve, which is exactly false for a stiff solver: it spends its transient
  taking tiny steps and then grows them by orders of magnitude. Measured on
  Robertson at `rtol = 1e-12`, RODAS4 has covered **0.0000%** of the interval
  after 5000 steps — indistinguishable from DOPRI5, which never finishes — and
  then finishes in 10 017 steps with its step size 1.7e8 times larger. Coverage
  cannot separate those two. Neither can step-size growth: RODAS4 on Van der Pol
  at the same tolerance has *flat* growth and still finishes, in 203 377 steps.

  Applying the projection to every adaptive method, as first written, aborted
  **eleven** solves across the benchmark suite that would all have succeeded.
  Restricted to methods whose step size is already as large as it is going to
  get, it aborts none — checked across every adaptive-solvable benchmark at
  `rtol` from 1e-3 to 1e-12. `progress_check=False` turns it off, for timing the
  grind or demonstrating it.

- **A symbolic answer now says where it is valid.** Solving `y' = y²`,
  `y(0) = 1` showed `y = 1/(1-t)` with nothing to say it means anything only for
  `t < 1` — while the *numerical* side of the same application stops at `t = 1`
  and reports that the solution may be blowing up there, and the `slopefields`
  lesson teaches that the existence theorem is local. Three parts of one
  product, one of them silent.

  `symbolic.interval_of_validity` finds the largest interval around the initial
  point on which the solution is defined, and — as much to the point — declines
  when it cannot. `tan(t)` has poles at every odd multiple of π/2 and no
  denominator to show for them; anything that looked only at the denominator
  would report "valid everywhere", which is worse than saying nothing. Only
  expressions built from functions with no real singularities, rational
  operations and integer powers are answered; the rest decline.

  `sympy.singularities` is the general answer and is not usable here: it did not
  return within ten minutes on `1/(1-t)`, against a twelve-second budget for the
  whole symbolic route. The denominator-based version answers in under 2 ms.

  The interval attaches to the *particular* solution only, and needs the point
  the conditions were given at — `1/(1-t)` is valid on `(-∞, 1)` from `t = 0`
  and on `(1, ∞)` from `t = 2`, so `SymbolicSolution.initial_point` carries it
  and nothing is shown when it is unknown.

- **The Solver Lab says when the answer on screen is not the whole answer.**
  Two things the solver knew and the plot could not show, both now surfaced as a
  caution beside the problem — and only when they apply, so that the label
  appearing means something.

  **Uniqueness.** `analysis.uniqueness_warning` differences `∂f/∂y` at the
  initial point over offsets four decades apart. A derivative that exists is
  about the same at all of them; one that does not grows without bound. The
  discriminator is *growth*, not size, because the two stiff problems in the
  catalogue have enormous and perfectly well-defined derivatives — Van der Pol
  at μ=1000 sits at 3e3 across the whole sweep, and Robertson's quotient
  actually falls. Measured margin between `y' = y^(1/3)` at the origin and
  every ordinary problem: four orders of magnitude.

  This closes a disagreement inside the application. The `slopefields` lesson
  teaches `y' = y^(1/3), y(0) = 0` as *the* case where uniqueness fails and
  names both solutions; solving it returned `y = 0` in eight steps with
  `success` set and no remark. The lesson and the tool now agree, and a test
  asserts they keep agreeing. The warning says the hypothesis is not satisfied,
  never that there are two solutions — the first is what was measured, the
  second would be a claim about the equation.

  **Missed events.** Endpoint bracketing loses any even number of crossings
  inside a step, silently: `g` has the same sign at both ends, so nothing looks
  wrong. On a smooth decay with `g = sin(20t)`, 63 roots exist and the default
  finds 7. `Event.subdivisions` has always been the cure; what was missing was
  any way to learn you needed it. One evaluation of `g` at the middle of each
  step is enough to *know* — a midpoint sign opposing both endpoints means at
  least two crossings happened and at most one was reported — and
  `Solution.incomplete_events` names the events it happened to.

  That detects rather than estimates: a flag raised is certain. It is not
  exhaustive, and `Solution.events_complete` documents the asymmetry — False is
  certain, True means only that nothing was caught going missing.

- **`Solution.diagnosis` says why a solve ended, in a form code can branch on.**
  Every diagnostic the solver produced was previously a prose string, so a
  caller — including this application's own screens — could not tell "blew up in
  finite time" from "hit `max_steps`" from "the right-hand side returned NaN"
  without matching on English. `Diagnosis` carries a `kind`, the time it
  happened, and a detail; `message` is unchanged and remains what to show a
  person.

  The kinds are deliberately no finer than the loop can actually tell. There is
  no `blow_up` and no `nan_right_hand_side`, because `y' = y²` and
  `y' = 1/(t-1)` are indistinguishable from inside the loop — both leave the
  state finite and the step collapsing — and a kind that named one of them would
  be a confident guess, which is the failure this type exists to remove. They
  share `step_underflow`, and the detail offers both readings. A state that
  actually goes non-finite is separate, because that the loop *can* see.

- **`ODEProblem` accepts `dfdt`**, the derivative of the right-hand side with
  respect to time at fixed `y`, as a callable or a constant vector. Only the
  Rosenbrock methods consume it and only on a non-autonomous problem, but there
  it is the difference between fourth order and first: see the RODAS4 entry
  under Fixed. Optional and keyword-only in effect, so nothing that built an
  `ODEProblem` before needs changing.

- **Coverage is measured and gated in CI.** The project had never had a coverage
  number; it is 96% for the library and 90% for the interface, 91% together.
  Two thresholds rather than one, because a single average would let the library
  — which is the product — slide while the total stayed green. Measured on one
  matrix leg, since the figure does not depend on the platform.

- **`pip-audit` runs in CI.** Nothing would otherwise have noticed an advisory
  against a dependency.

- **CI now tests every platform the package advertises.** `pyproject.toml`
  claims Python 3.10–3.13 and "Operating System :: OS Independent"; CI tested
  3.10 and 3.12 on Linux and Windows, leaving macOS and two Python versions as
  promises with nothing behind them. Eight legs now cover every advertised OS on
  at least one version and every advertised version on at least one OS — not the
  full 3×4 cross product, which buys little for twelve legs. A test compares the
  matrix against the classifiers, so adding one without the other fails.

- **The subprocess boundary and the threading layer are properly covered.**
  `dsolve_worker` went from 58% to 85% and `solver.py` from 79% to 95% — the two
  least-covered non-trivial modules, and the two where a bug is hardest to
  reproduce and most likely to hang the interface. What was covered in both was
  the happy path. Now covered: a malformed request answered rather than crashed,
  partials published before the final reply, `dsolve` failing without taking the
  classification down with it, a general solution surviving initial conditions
  that cannot be applied, an exception on a pool thread reaching a signal
  instead of vanishing, and a superseded solve stopping at its next step
  boundary rather than running to completion for an answer nobody will read.

  The coverage leg also gained a longer `dsolve` deadline. Measuring makes that
  subprocess several times slower, and combined with `-n auto` it missed even
  the 90 s test-session budget — a test with nothing to do with coverage failing
  on the coverage leg only. Reproduced deliberately before fixing.

- **Every lesson has a drill.** Ten had none, and the reason was grading
  rather than effort: a typed answer is marked by substituting it into its own
  equation, and Euler's method has no closed form to substitute into, so the
  verdict there could never be "right". `NumericTemplate` is the missing
  question type — a number, graded to a tolerance — and it reaches the seven
  lessons whose answer *is* a number: one Euler step, one Runge–Kutta step, a
  terminal velocity, an equilibrium, a slope, a determinant, a convolution.

  Two of the ten needed nothing new at all. `complex-eigenvalues` and
  `forced-systems` have closed forms, and an ordinary template with the
  systems narrator solves them — which also fixed a real limitation, since
  the drill's grader built its equation from a single line and so could not
  read the `x' = …; y' = …` a system is written as.

  The tolerance is a correctness question. The Runge–Kutta drill asks what the
  *method* lands on, so an Euler step must be marked wrong — but the exact
  solution must not be, because across these step sizes a fourth-order method
  agrees with it to four decimal places. That was assumed the other way round
  when the drill was written, and measuring it is what corrected the claim.

  The stored answer is an expression over the template's slots rather than a
  number, so every draw can be checked against the machinery the lesson
  teaches: `byhand.walk` for both steps, `analysis.phase_line` for the
  equilibria, `numpy.linalg.det` for the determinant. A `Solve` drill cannot
  disagree with the rest of the application because substitution *is* its
  grading; this type buys that property back.

- **Twelve more figures**, taking eighteen of the thirty-five lessons to one
  that moves. Where a lesson has a parameter worth turning: the two constant
  solutions separating divides away, with every curve crowding them and none
  crossing; the transient and the steady state drawn apart; the level curves
  of an exact equation's potential over its own slope field; error against
  step size on log axes with reference gradients of 1 and 4; a spiral whose
  direction reverses as the real part of the eigenvalue crosses zero; poles in
  the s-plane beside the response they invert to; partial sums converging with
  the radius marked; and the convolution — one curve reversed and slid across
  another with the overlap shaded, `t` on a slider, because dragging it *is*
  the animation and a timer could not be tested.

  Seventeen lessons still have none, deliberately. Superposition has nothing
  to turn.

  `lessonfigure.py` becomes a package, one module per unit. Six figures fitted
  in one file and eighteen do not — the same argument, at very nearly the same
  size, that made `lessons.py` a package.

- **Every lesson reads as a textbook section rather than a set of cards.**
  All thirty-five now open with *why this comes up* — where the equation
  arises, what goes wrong with the tools already in hand, and why the
  technique is the natural response — and then *where this comes from*, the
  argument that the method is legitimate, in numbered steps.

  The derivation is a new structural element (`Passage`) and not a longer
  note, because it is a different thing from what the narrator does. The
  narrator shows the mechanical moves for one particular equation; a
  derivation argues that the moves are allowed in general, and no number of
  worked examples adds up to that. So separable equations justify
  `∫dy/g(y) = ∫f dt` by the chain rule on `H(y(t))` instead of calling the
  `dy` loose shorthand, the integrating factor is derived from
  `(μy)' = μy' + μ'y` instead of produced, and exactness is shown to be the
  symmetry of mixed second partials instead of a test to remember.

  Every worked example also carries commentary: which line matters, what would
  have gone wrong a step earlier, what the answer's shape is telling you. It
  is checked against its own *why* — a commentary that restates the reason the
  example exists has spent its first paragraph saying nothing, which is how
  the first draft of all twelve read.

  Measured: about 198,000 characters of explanation across the curriculum,
  some 5,700 per lesson against 1,500 before. The list of what has been
  written up lives in `tests/test_lessons.py` and now names every lesson —
  which is what it was for. While the work was in progress it kept the
  remainder visible in the tests rather than in a plan, and it still gates:
  a lesson cannot be written up without being listed, or listed without being
  written.

  The derivations are the part worth reading. Separable equations justify
  their two integrals by the chain rule rather than by calling the `dy` loose
  shorthand; the integrating factor and the eigenvalue method are each derived
  from a single substitution; Abel's identity explains why testing the
  Wronskian at one instant settles every instant; undetermined coefficients
  says why a *finite* trial set can work at all, and resonance becomes the
  forcing lying inside what the operator annihilates; one integration by parts
  produces the whole Laplace method; and the convolution theorem comes out of
  exchanging the order of a double integral over a wedge. Where a derivation
  would be beyond a first course it says so and stops — the Runge–Kutta
  weights are stated as being chosen to match a Taylor expansion, not derived.

- **Typeset equations announce themselves to a screen reader.** `MathLabel`
  renders to an image, and an image with no alternative text is invisible —
  which, in an application whose content is mostly equations, was most of the
  content. The plain form was already computed for the fallback path, so
  exposing it as an accessible description cost nothing. Cards carry their
  heading as an accessible name, and each paragraph of prose is announced as
  one.

- **Progress you can take with you.** *Export* writes everything answered to
  a file; *Import* merges one back in. Merges rather than replaces, and the
  distinction is the whole point: importing a file from a machine where you
  had done less would otherwise delete work, which is the failure the feature
  exists to prevent. Where both files know a question the stronger record wins
  — more correct answers, then the longer streak, then the later date — and it
  is tested in both directions, so an older thinner file cannot undo a streak
  built since.

  The exported file *is* a progress file, written by the same serialiser the
  application saves with. There is no second schema to keep in step, and
  someone can copy it into place by hand instead if they prefer.

- **The Course Map says what has gone quiet**, beside what is weakest. Ranking
  by score can never surface a lesson finished in July and untouched since —
  it scores perfectly — so a second line asks the other question: what has not
  been seen in three weeks. Every answer now records the day it was last
  given, which is version 3 of the progress file; a version 2 file reads as
  "never seen", because that is honestly what it is.

  Deliberately **not** a spacing schedule. This application records one verdict
  per question and nothing about how hard each felt, so fitting an interval
  curve to it would be inventing data it does not have.

- **The window reopens where you left it** — size, position, and the screen you
  were on. Kept in `QSettings` rather than in the progress file, because it is
  preference and not achievement: a geometry has no business in a file you may
  export to a machine with a different screen. An explicit `--screen` or
  `--problem` still wins, and a remembered screen that no longer exists is
  ignored rather than opening nothing.

- **Generated multiple choice: `ChoiceTemplate`.** What `Template` is to
  `Solve`, for the lessons a substitution check cannot reach. Grading, not
  effort, was what left fifteen lessons with no drill: `check_answer` works by
  putting an answer into its equation and simplifying, which cannot decide a
  switched or impulsive answer, has nothing to substitute for Euler's method,
  and marks a truncated series wrong. Those lessons needed a question type
  graded some other way, and `Choice` already was one.

  **The options are shuffled per draw**, deterministically from the template's
  key and the draw index, with each reason moving alongside its own option.
  Leaving the answer where the author wrote it would put it at the same index
  in every version, so the drill would teach the position rather than the
  mathematics — the exact failure a generated question exists to avoid. Both
  that the answer moves and that a reason never drifts onto a neighbouring
  option are tests.

  Five drills so far. Three in the series unit — is this point ordinary, how
  far does the series converge, what is the indicial equation — and two in the
  Laplace unit, on the second shifting theorem and on the impulse transform
  against the step's. **Every one of the seven units can now be examined**:
  the series unit had no drills, so it offered no check-up at all, and a unit
  you cannot examine is one you cannot tell you have finished. Lessons without
  a drill: 15 → 10.

  The Unit Quiz gains its second question type with them, so the mix now asks
  both kinds of question — work the method out, and say which method it is.

- **Nonhomogeneous systems, and the last lesson of the course.** `x' = Ax + f`
  by varying the constants, with the basis solutions as the columns of a
  fundamental matrix: `x_p = Φ ∫ Φ⁻¹f dt`. Variation of parameters with the
  bookkeeping done by a matrix, and it never needs the resonance correction
  that guessing a form would. `e^{At}` is shown for what it is — the
  fundamental matrix normalised so `x(t) = e^{At}x(0)`.

  With it Unit 6 is complete and so is the curriculum: **thirty-five lessons
  across seven units**, which is the whole of the plan.

  The basis is still checked against the *homogeneous* system, not the forced
  one — checking it against the forced one would report a correct fundamental
  set as wrong, which is the trap the second-order narrator documents.

- **`Unit Quiz` — a mixed set from one unit.** The Lessons screen asks about
  one topic at a time, which is how you learn a technique and not how you are
  examined on one. Working out *which* method a question wants is most of the
  difficulty of an exam, and it is the one thing lesson-by-lesson practice
  cannot rehearse.

  **A quiz question is an ordinary drill question** — the same `Solve`, graded
  by the same substitution, hinted by the same ladder, recorded through the
  same `progress`. The quiz adds no mathematics and so cannot disagree with
  the rest of the Hub about what is correct.

  Neither the lesson's name nor the drill's prompt is shown while answering,
  and that is the whole design: a drill prompt says "Separate it, integrate
  both sides", which is right in the Drill segment and fatal here. The report
  afterwards names the lessons the misses came from and offers to open them.

  **There is no countdown**, only a clock reported at the end. A timer
  counting down turns practice into an examination, and an interruption then
  costs something — which is wrong for a tool opened between other things.

- **Mastery on the Course Map.** Each unit shows its own standing — questions
  answered, drills mastered, lessons finished — and the summary says what is
  worth another look, weakest first. Only lessons already started: one never
  opened is not weak, it is simply next, and listing it would turn "what to
  review" into a second table of contents.

- **Series solutions: `series.py`, and the last unit.** Power series and
  ordinary points, recurrence relations and the radius of convergence, and
  regular singular points. **All seven units are now complete** — thirty-four
  lessons, the whole of a first course.

  **The recurrence is what is narrated**, because it is the lesson. sympy
  returns a truncation without the rule that generated it; building the rule
  here costs 0.01–0.02 s and gives the textbook coefficients, including the
  pattern of every third Airy coefficient vanishing that a list of terms only
  hints at. The radius of convergence comes from the nearest root of the
  leading coefficient **including complex ones** — `1/(1+t²)` is fine for
  every real t and its series still stops at 1.

  **A truncation is reported as a truncation.** Substituting a truncated
  series back leaves the terms that were never written down, so `verified` is
  decided by the residual being of high enough order and the check is named
  `truncation`. Where the series terminates the residual is exactly zero, the
  ordinary substitution check is used, and the answer is reported as exact.
  Unit 7's practice questions are all of the second kind — Legendre and
  Hermite at the parameters where the series stops — because `check_answer`
  grades a truncation as wrong, and a question whose model answer the grader
  rejects would be worse than no question.

- **Linear systems: `systems.py`, and Unit 6.** The eigenvalue method,
  narrated the way a course writes it — write it as `x′ = Ax`, form
  `det(A − λI) = 0`, find an eigenvector for each eigenvalue, and branch into
  the three cases. A **complex pair** is taken apart with Euler's formula
  applied to the eigenvector as well as the exponential, which is the step
  people get wrong and is therefore shown in full. A **defective** matrix gets
  a generalised eigenvector from `(A − λI)w = v`, and the `t` in
  `(vt + w)e^{λt}` is explained as cancelling a leftover term rather than as a
  convention.

  Everything is checked rather than asserted: the matrix is reconstructed into
  the equations it came from, the characteristic polynomial is expanded back,
  every eigenvector goes through `Av = λv`, and every basis solution is
  substituted into the system.

  Five lessons follow it — first-order systems and conversion, the three
  eigenvalue cases, and phase portraits — with an **eigendirections figure**
  whose two straight lines swing as you change a matrix entry and vanish when
  the eigenvalues go complex. Thirty-one lessons across six units.

- **Two refusals lifted.** A system reaching *Solve Step by Step* used to get a
  closed form and an empty working panel, because the narration gate asked for
  exactly one equation. And **check your answer now works on systems**,
  component by component: each typed line names its unknown and is substituted
  into *every* equation, because a pair can satisfy one and fail the other and
  checking them one at a time would miss it.

  The hand-over guard that skips `dsolve` where a technique came from no hint
  had to learn about systems too — it reads the hint list, and a system never
  has one, so without excluding them it would have fired every time and stopped
  the closed form being computed at all.

- **Convolution, and Unit 5 finished.** Five more Laplace lessons — the
  transform and reading the table, the shifting theorems with partial
  fractions, convolution, step functions and piecewise forcing, and impulses
  and the delta function. Twenty-six lessons across five units, and every unit
  before systems is now complete.

  **The convolution theorem is narrated where nothing splits.** `1/(1+t)`,
  `e^{-t²}` and `ln t` have no tabulated transform, so partial fractions has
  nothing to break apart. The derivation now recognises that Y(s) is a
  product, inverts the transfer function alone to get the impulse response,
  and writes the convolution integral — evaluating it where it evaluates
  (`y'' + y = 1/(1+t)` comes out in sine and cosine integrals, verified) and
  leaving it where it does not, which is what a textbook does and is a
  complete answer either way.

  Two rows joined the table: `F(s)G(s) ↔ (f*g)(t)`, and the periodic-forcing
  formula. Neither is auto-highlighted beside a derivation, deliberately —
  they describe a *route* rather than a shape, so there is nothing in a
  time-domain answer to recognise them by, and highlighting the wrong row
  would be worse than highlighting none.

  **Three lessons carry no drill, for a measured reason.** A switched or
  impulsive answer substituted back leaves `Heaviside` and `δ` terms that
  never cancel, so `check_answer` returns *cannot tell* — correct behaviour,
  but a verdict that is never "right" can never advance a mastery streak.

- **Six more lessons, and Units 3 and 4 finished.** Unit 3 gains superposition
  and the Wronskian, variation of parameters, and higher-order equations, so
  it now runs the length of Edwards chapter 3. Unit 4 is new — free vibration
  and the three damping regimes, forced oscillation with beats and resonance,
  and the RLC circuit analogy — and needs no new narrator, which is the point
  of placing it after Unit 3: free vibration is characteristic roots, forced
  vibration is undetermined coefficients, and a circuit is the same equation
  with different letters. Twenty-one lessons across five units.

- **Two more figures to move.** *Damping* puts the characteristic roots in the
  complex plane beside the motion they produce, so dragging `c` through
  `2√(mk)` collides the pair on the real axis and stops the oscillation in the
  same gesture. *Resonance* drives an undamped oscillator from rest: the beats
  envelope stretches and grows as `ω` approaches `ω₀` — measured, the
  amplitude runs 0.69, 2.56 and 25.1 at `ω` = 1.6, 1.9 and 1.99 — and at
  `ω = ω₀` the closed form becomes the secular `t·sin(ω₀t)/(2ω₀)` rather than
  a division by zero. A second pane shows what damping does to the same story.

  A slider quantises to 1000 steps, so it can essentially never land on a
  single point of a continuum: asking for critical damping gave 3.996, which
  is genuinely underdamped, and the middle of the three regimes never appeared
  in a figure whose whole subject is the moment the roots collide. The damping
  now snaps to critical within half a step, so the regime named is the regime
  drawn.

- **A driven spring in the problem gallery.** `forced_spring` —
  `m x'' + c x' + k x = F cos(ωt)` — with a closed form that is the steady
  state plus a transient matched to the initial conditions, agreeing with the
  numerical solution to 1e-11 across all three damping regimes and at
  resonance. Unit 4 had no forced model to open; now it does, and the
  transient giving way to the steady state is visible by dragging the driving
  frequency past `√(k/m)`.

- **`sec`, `csc` and `cot` can be typed** into any equation the app parses.
  They are exactly the forcing terms variation of parameters exists for, so
  `y'' + y = sec(t)` had to be expressible — it was rejected as unparseable
  before.

- **Variation of parameters**, the ninth technique the Hub can narrate and the
  one that reaches forcing undetermined coefficients cannot touch. `sec t`,
  `tan t` and `eᵗ/t` have no finite trial set to guess, so the other technique
  has nothing to say about them; before this, *Solve Step by Step* returned no
  derivation at all for any of them.

  **Where it sits in the order is measured.** sympy names the hint on *every*
  constant-coefficient forced equation — `y'' + 4y = sin t` as much as
  `y'' + y = sec t` — so listing it before undetermined coefficients would
  narrate Wronskians for every equation a first course solves by guessing.
  Listed after, it takes exactly the equations where sympy names it alone.

  **Written for order *n*, not for two.** The familiar `u₁' = −y₂g/W` pair is
  Cramer's rule on the *n*×*n* system, and writing the system costs nothing
  extra: `y''' + y' = tan t` is narrated by the same builder in 0.09 s rather
  than by a second implementation saying the same thing less generally. The
  Wronskian is shown as a step and checked non-zero, because dividing by it is
  the technique and its being non-zero is what makes the basis a basis.

- **Lesson figures: three pictures you can move.** At the top of *Learn*,
  where the topic has one. A note can say that raising the harvest rate
  eventually wipes out both equilibria; a figure lets you raise it and watch
  the two dots slide together and vanish, which is a different kind of knowing.

  *Slope fields* draws the dashes `y' = a·y + b·t` demands at each point — no
  solving involved — and integrates a solution through anywhere you click,
  forwards and backwards. The curve comes out tangent to every dash it passes,
  and two curves never cross: uniqueness shown rather than stated.
  *Equilibria* plots `f(y)` for the harvested logistic equation, marks each
  equilibrium filled or hollow by which way its arrows point, and puts an arrow
  in every interval between them; push `h` past `r·K/4` and both equilibria are
  gone. *Euler's method* runs Euler and RK4 on `y' = y`, whose answer nobody
  has to take on trust, and reports both endpoint errors — printed as
  measured rather than as theory: 1.8 and 14.7 at `h = 0.2`, climbing towards
  2 and 16 as `h` shrinks, which is what an order statement actually claims.

  **No figure computes mathematics of its own.** The dashes come from
  `analysis.slope_field`, the equilibria from `analysis.phase_line`, the steps
  from `byhand.walk` and `byhand.refinement`, and the curves from the library's
  own `solve`, so a figure cannot disagree with the tool that teaches the same
  thing. A lesson names its figure by key, because `lessons/` holds content and
  no Qt; the tests check both directions of that indirection, so a typo is a
  failure rather than a lesson that silently lost its picture.

- **`analysis.phase_line`** — the equilibria of a scalar autonomous equation,
  with the sign of `f` on either side and the linearisation beside it.
  Deliberately not `find_fixed_points` with an axis thrown away: that routine
  classifies a planar equilibrium by the eigenvalues of a 2×2 Jacobian, and a
  scalar equation has no such thing. On a line the sign of `f` either side
  settles which way solutions move, which is what a course draws and what stays
  right where the linearisation says nothing — `y' = y²` has `f'(0) = 0`, so
  the derivative test calls it neutral and loses both arrows while the signs
  correctly call it semi-stable. Roots are found by refining every local
  minimum of `|f|` rather than only the sign changes, for the same reason: a
  root the curve touches without crossing has no sign change to bracket.

- **Three more techniques the Hub can narrate: exact equations, the
  homogeneous substitution `y = v·t`, and Bernoulli.** With them the first two
  units of the course are complete, and *Solve Step by Step* now writes out
  eight methods a move at a time rather than five.

  **Exactness is decided structurally, never from a hint.** Six exact equations
  were split into `M dt + N dy` and tested against `∂M/∂y = ∂N/∂t`:
  `classify_ode` misses `1st_exact` on three of them — precisely the three an
  exact-equations lesson is about, including `y' = −(2t+y)/(t+3y²)` — and
  offers it on `y' = −y/t²`, which that test says is not exact. It normalises
  `M` and `N` differently, so neither half is a sympy bug; it does mean the
  hint cannot be trusted, so the detector runs here, and only where no named
  technique applies. An equation that is both exact and linear therefore keeps
  the integrating factor, which is the method a course meets it by first.

  **The two substitutions reuse the narrators they reduce to** rather than
  copying them: each builds a real equation in a real `v`, hands it to the
  separable or integrating-factor narrator, then undoes the substitution and
  applies the initial condition once, to the answer in `y`. Those two narrators
  grew a parameter naming the letter to print, because a derivation that called
  `v` "y" while solving for `v` would misreport what it had just done. Where
  undoing an even root leaves a sign, the initial condition chooses it — and
  the negated branch is offered only once it has been checked to solve the
  equation too.

  **`dsolve` is no longer asked to reproduce an answer it had no hint for.** On
  `y' = −(2t+y)/(t+3y²)` it runs past forty seconds trying `lie_group`, so the
  whole twelve-second budget bought a timeout; the narrated answer has by then
  been substituted back and simplified to zero, which is a stronger warrant
  than `dsolve` returning would have been. The guard is narrow by design: where
  the hint list does name the technique, sympy is asked exactly as before.

- **Eight more lessons, and Units 1 and 2 finished.** What a differential
  equation is; slope fields, existence and uniqueness; exact equations;
  substitutions (homogeneous and Bernoulli); population models and the logistic
  equation; equilibria, stability and the phase line; acceleration, velocity
  and drag; and Runge–Kutta, split out of the numerical lesson so that Euler's
  method and what order buys are no longer one page. Fifteen lessons now.

- **Learning Hub: `Lessons`** — notes and practice for seven topics: separable
  equations, integrating factors, characteristic roots, undetermined
  coefficients, Cauchy–Euler, Laplace transforms, and the numerical methods.
  The other four Hub screens are tools that work on an equation you bring; this
  is the part for someone who does not yet know which equation to bring.

  **Practice is graded by mathematics, not by an answer key.** A typed solution
  is substituted into the equation and simplified, through the same
  `check_answer` the Solve Step by Step screen uses, so every correct form
  passes and nothing is marked wrong for being spelled differently.
  Multiple-choice questions exist only for what that cannot reach — *which
  technique solves this* is what a course actually tests — and each one shows
  its reasoning whether you were right or wrong.

  **The worked examples are generated, not transcribed.** Each runs through the
  same narrator that powers the tool it belongs to, so a lesson cannot drift out
  of step with the screen that explains it, and `tests/test_lessons.py` runs the
  real narrator over every question to prove each has an answer the app can
  produce — and that the grader accepts the app's own answer, which is the worst
  failure this screen has available.

- **Progress is remembered between sessions**, in a small JSON file in the
  platform's config directory, with a reset button beside it. The first thing
  this application has ever stored on disk, so it is careful about it: a
  corrupt, hand-edited or truncated file reads as "nothing recorded" rather than
  raising, writes are atomic, and answering correctly and then mistyping does
  not take the tick away.

- **Learning Hub: `Drill` — practice that does not run out.** A fourth part of
  every lesson that has one, beside Learn, Examples and Practice. Each drill is
  a question with its numbers left open, so it can ask the same *method* in
  eleven to forty-eight different versions; three right in a row masters it, and
  one wrong answer starts the count again.

  **A generated question is an ordinary practice question.** `draw(template,
  seed)` returns the same `Solve` the hand-written questions use, so it is
  graded by the same substitution, hinted by the same ladder and worked by the
  same narrator. The drill adds no mathematics of its own and so cannot
  disagree with the rest of the Hub about what is correct.

  **Draws are enumerated, not sampled**, which is what makes the guarantee
  checkable rather than merely likely: `tests/test_templates.py` runs the real
  narrator over **every draw of every template it solves** — 476 of them — and requires
  each to be narrated by the technique the drill claims to teach, to have every
  step verify, and to have its answer accepted by the grader. Nobody wrote
  these questions, so nobody read them either; that sweep is what stands in for
  having read them. Enumerating also means the same seed always gives the same
  question, so pressing Check cannot change it underneath you, and the drill can
  say "one of 18 versions" because it knows.

  Thirty-two drills across twenty-five lessons. The numerical lesson deliberately
  has none —
  Euler and RK4 have no closed form for the grader to substitute into, so a
  drill there could never say "right", and its button is absent rather than
  opening a page that cannot work.

- **Learning Hub: a `Course Map`, and lessons organised into units.** Seven
  lessons in a flat list was navigable; the whole of a first course is not. The
  lessons are now filed under the chapters of Edwards, Penney and Calvis —
  first-order equations, models and numerical methods, second-order linear
  equations, Laplace transforms — and the new screen shows the units, the
  lessons inside them, how far through each you are, and a *Continue* button
  that opens the earliest lesson with a question left.

  A unit appears on the map once it has lessons. There is no stand-in for a unit
  still to be written: this application removed its last placeholder
  deliberately, and a course map advertising empty units would put them back.

- **A lesson is now three parts rather than one page** — *Learn*, *Examples* and
  *Practice* — with the lesson's title and the part you are in staying put while
  the rest scrolls. Each lesson also states what you should be able to do
  afterwards, cites its textbook section, and names the lessons worth having met
  first. The prerequisites are advice, not a gate; nothing is locked.

- **Notes come in kinds, and a common mistake does not read like an idea.** The
  same card, with a warning stripe down it and a label above it, because the
  thing that catches people is worth setting apart from the thing that is merely
  true. Five of them are new: reading `p` off an equation whose `y'` still
  carries a coefficient, the two branches a rearrangement can produce, `r(r−1)`
  rather than `r²` in the indicial equation, `y(0)` carrying the factor of `s`
  and `y'(0)` not, and guessing only the top power of a polynomial.

- **Hints come one rung at a time.** A nudge, then the first move, then the
  next, with "Show me" — the real narrator — at the end of the ladder. Every
  practice question has at least two rungs; a single hint is either useless or
  the answer.

- **Every multiple-choice question explains every option**, not just the right
  one, and the reason shown is the reason for the option *picked*. Explaining
  the right answer back at somebody who did not choose it teaches nothing: the
  reason a wrong option was tempting is usually what was actually
  misunderstood.

- **Six more worked examples**, so most lessons now show a plain case and then
  one that breaks the plain rule — `y' = y²` running to infinity in finite time,
  a complex root pair becoming a cosine and a sine, a repeated indicial root
  bringing in `ln t`, a switch thrown at two seconds. Each says what it is there
  to show, and all thirteen are generated and checked by the narrator, which
  `tests/test_lessons.py` now verifies for every example rather than only the
  first.

### Changed

- **`lessons.py` is now a package**, one module per unit plus the shared model.
  Seven lessons was 837 lines; a whole course is not something one file should
  carry. Nothing that imported it needs to change.

- **Drill progress is kept in its own bucket**, `<lesson>/drill`, and counted by
  a streak rather than by an ever-answered-correctly. Mixing it with the
  practice questions would have made "3 of 5" meaningless: one number is out of
  a fixed denominator and the other is not.

- **The progress file records attempts as well as outcomes** (format version 2),
  because a course map that can only say "answered" cannot tell steady work from
  a lucky guess. A version 1 file — one written by any earlier build — still
  loads with its ticks intact and is rewritten in the new shape; refusing to
  read it, or quietly dropping it, would take away work already done. Answering
  correctly and then mistyping still keeps the tick, and now counts the attempt,
  because it happened.

- **The Learning Hub takes `Ctrl+1` to `Ctrl+6`**, the Course Map first. Solver
  Studio is unchanged on `Ctrl+Shift+N`.

- **Home offers every Learning Hub screen.** `Lessons` never had a tile and was
  reachable only from the sidebar, a shortcut or `--screen`; it and the Course
  Map now have one.

- **Shortcuts are numbered per section**, `Ctrl+N` for the Learning Hub and
  `Ctrl+Shift+N` for Solver Studio. Eleven screens no longer fit a single run of
  digits, and the flat run had the odd effect that `Ctrl+5` jumped out of the
  section you were in. Every binding is still globally unique, which is the
  property that mattered.

### Fixed

- **A drawn coefficient of zero left its whole term in the equation.**
  `y'' + 0*y' + 9*y = 0` is how nobody writes an undamped oscillator, and five
  templates were producing it — the undamped and missing-root draws, which are
  the pedagogically interesting ones and so could not just be dropped from the
  slots. `tidy` removes the term now. The guard that should have caught it
  looked for `0s` and `1t` but not `0*y'`, and it now covers every kind of
  template rather than only the ones graded by substitution: a generated
  prompt, hint or reason gives itself away exactly as an equation does.

- **The order figure logged its data twice**, once itself and once through
  pyqtgraph's log mode, which turned every negative exponent into a NaN and
  warned on each redraw.

- **Seventeen stored equations were printing their own LaTeX.** Mathtext
  implements a large subset of LaTeX and `is_renderable` only guarded against
  the environments sympy can produce, so hand-written content could contain
  `\tfrac`, `\underbrace`, `\iff`, `\big[` or `\ge` — none of which sympy
  ever emits — and fall silently back to plain text, backslashes and all. It
  read as a typo in the lesson rather than a limit of the renderer. The guard
  now refuses those too, every one of them is rewritten in a form mathtext
  accepts, and the test renders each stored equation instead of asking whether
  it looks renderable. One narrated step in the Laplace unit had the same bug.

- **The accent stripe on a card was drawn down every label inside it.**
  `QLabel` is a `QFrame`, so a stylesheet rule written as `QFrame { ... }` and
  set on the card applied to all of its descendants: a blue rule appeared
  beside every equation and over the first character of every line of text.
  Harmless when a card held four short bullets, and glaring once it held four
  paragraphs. The rule is scoped by object name now.

- **Emphasis written as `*this*` was printed with the asterisks**, in eleven
  lessons. Prose labels are rich text now and the markers become italics. The
  conversion escapes the content first, so nothing in a lesson can introduce
  markup, and it deliberately does not match a marker with a space against it
  — which is what keeps `f * g and g * f`, in the convolution lesson, from
  being read as emphasis across the middle of a sentence.

- **A system's answer was shown unchecked, and its structure not shown at
  all.** `_verify` skipped systems outright, so the Studio presented a closed
  form with no verdict on it; `characteristic_analysis` returned nothing, so
  the root table was blank — which reads as "this equation has no structure"
  rather than as "we did not look". Both now work: the polynomial is
  `det(A − λI)`, whose roots are the eigenvalues, and the answer is verified
  with every component substituted into every equation at once. A pair that
  satisfies the first equation and fails the second is caught, which
  substituting one equation at a time would not do.

- **sympy's unevaluated `InverseLaplaceTransform` was shown as the answer.**
  Where the inverse transform has no elementary form, sympy either returns
  that object or raises `NotImplementedError`, depending on the forcing term:
  `e^{-t²}` gave the object, `1/(1+t)` raised. The object reached the screen
  as the solution, marked unverified — a student was shown sympy giving up,
  dressed as mathematics. Both routes now fall through to the convolution
  theorem, and `y'' + y = 1/(1+t)` produces a verified closed form where it
  previously produced nothing usable at all.

- **A forced Cauchy–Euler equation produced an empty derivation.**
  `t²y'' + ty' − y = t³` substituted `y = tʳ` into `lhs − rhs` with the forcing
  term still in it, so `t` survived the division by `tʳ`, the indicial equation
  was rejected, and the builder gave up having appended *no steps at all* — the
  screen showed a technique name with nothing under it. The forcing is now set
  aside first and the Euler basis handed to variation of parameters, which is
  what Edwards 3.6 does: guessing a form has no theory behind it once the
  coefficients stop being constant. Fixed in passing: the fundamental set was
  checked against the *forced* equation, which would have reported a correct
  basis as wrong.

- **A `dsolve` answer with several branches is no longer thrown away.** Where
  solving for `y` leaves branches — `y' + y = t·y³` comes back as the plus and
  minus square roots — `dsolve` returns a *list* rather than one equation, and
  reading `.rhs` off the list raised `AttributeError`. The worker reported that
  as "sympy has no method for this equation", discarding an answer sympy had
  actually found.

- **A separable equation with two branches showed the wrong one.** ``y' = t/y``
  with ``y(0) = 2`` rearranges to ±√(t² + 2C), and the first root was taken
  regardless — the negative branch, which satisfies the equation but passes
  through no point the condition allows. Nothing complained, because the answer
  *was* a solution. The branch the condition sits on is now the one shown.

- **A decimal coefficient poisoned the answer**, the same way a decimal initial
  condition did before it. ``y' = 2 - 0.05*y`` produced a constant whose
  imaginary part was the *number* 3.14159… rather than `pi`, which sympy cannot
  cancel, so a mixing-tank answer that should read ``40 - 35e^{-t/20}`` came out
  carrying a complex exponential. Coefficients are rationalised along with the
  conditions.


## [0.4.0] — 2026-08-19

### Added

- **Learning Hub: `Laplace Transforms`**, and with it the Learning Hub is
  complete — no screen in the application is a placeholder any more.

  The transform is the one technique in a first course that turns the equation
  into *algebra*, and the only one that copes with forcing switched on partway
  through or delivered as an impulse. ``y' + y = u(t-2)`` — a switch thrown at
  two seconds — is not separable, has no integrating factor worth writing, and
  is not what undetermined coefficients is for. It comes out here as the
  textbook ``u(t-2)(1 - e^{-(t-2)})``, and ``y'' + y = δ(t-1)`` as
  ``sin(t-1)u(t-1)``.

  Six steps, each a real move of the method, and the initial conditions enter at
  the *start* through ``L{y''} = s²Y - s·y(0) - y'(0)`` rather than arriving at
  the end as constants to be pinned down — which is the point of the technique
  and what separates it from everything else in the Hub. A transform table sits
  alongside with the rows the answer actually needed highlighted.

  It reuses rather than rebuilds: the result is a `steps.Derivation`, so it
  renders through the panel L2 already built and travels over the wire format
  L2 already defined, and it runs in the subprocess `dsolve` already owns. That
  subprocess grew a mode rather than a twin; `dsolve` itself is not run at all
  here, since the derivation carries the answer and checks it.

- **`Heaviside` and `DiracDelta` are typeable — on the Laplace screen only.**
  Without them a user could not type the forcing that motivates the entire
  topic. With them everywhere, the Solver Lab would accept a `DiracDelta` that
  cannot be lambdified at all (`NameError` at solve time) and a discontinuous
  right-hand side that an adaptive step can cross without noticing, which is a
  failure this project already documents. So `parse_equation` takes an explicit
  widening and exactly one caller passes it.

- **Learning Hub: `Solve Step by Step` narrates the derivation.** Five techniques
  — separation of variables, integrating factors, characteristic roots,
  undetermined coefficients, Cauchy–Euler — written out a move at a time, with
  the reason each move is legal. That is what a first course is about, and it is
  the one thing `dsolve` cannot be asked for: it returns an answer and does not
  expose the moves it made.

  **Every step is checked, not merely printed.** The antiderivatives are
  differentiated back and compared with their integrands; each basis function is
  substituted into the equation and required to give exactly zero; the
  particular solution has to reproduce the forcing term. A card carries a tick
  only where its own claim was verified, and a step that fails verification is
  shown failing rather than hidden. A derivation that quietly prints a wrong
  line is the one thing worse than no derivation.

  Equations outside the five get no derivation at all rather than a vague one —
  the same degradation `SymbolicSolution` already makes between *timed out*, *no
  method*, and *found but unverified*.

- **The technique is now named the way a course names it.** This was the finding
  the whole phase turned on. `classify_ode` orders its hints by what sympy would
  rather *solve* with, which is not the order a course *teaches*:

  | equation | sympy's first hint | what it is called |
  |---|---|---|
  | `T' = -k(T - 20)` | `factorable` | separable |
  | `y' + 2y = t` | `1st_exact` | integrating factor |
  | `y'' + 3y' + 2y = 0` | `factorable` | characteristic roots |
  | `t²y'' + ty' - y = 0` | `factorable` | Cauchy–Euler |

  The app stored `hints[0]`, so **four of the five techniques would never have
  dispatched**. The worker now returns the whole tuple and the teaching name is
  preferred. That also fixes the Solver Studio's Symbolic tab, which had been
  labelling `y'' + 3y' + 2y = 0` as "factorable" — true, and useless.

- **The app is split into two sections: Learning Hub and Solver Studio**, over a
  shared Home. The Studio holds the five screens that already existed — Solver
  Lab, Phase Portrait, Stiffness Explorer, Method Race, Accuracy Lab — and the
  Hub is a new section for learning to solve ODEs, currently four placeholders
  being filled in by phase: Solve Step by Step, Laplace Transforms, Methods by
  Hand, Worked Problems.

  The split is presentation only. Both sections drive the same `SessionState`
  and select from the same catalogue by key, which is what lets a problem —
  including one the user typed — appear on either side without either knowing
  about the other.

  `go(key)` still takes a bare screen key and now resolves the section itself,
  because every caller passes one that way: `cli.py --screen`, the Home tiles,
  and the tests. Shortcuts stay globally unique rather than restarting per
  section, so one never means two different screens.

  Verified by the same 42-render offscreen comparison used for the
  control-panel refactor: the five existing screens render **pixel-identically**
  to before the split. A navigation change must not disturb what it navigates
  to.

- **`euler` and `rk4` are real methods.** The method list previously started at
  Bogacki–Shampine, so a learner could not select either of the two methods they
  had just been taught. Both are tableaux like every other explicit method, and
  both are verified by the machinery that already existed: the rooted-tree order
  conditions hold at their claimed order and *fail* one higher, and the measured
  slopes are 1.00 and 4.00.

  Neither carries an embedded pair, so `ButcherTableau.e` may now be None and
  such a method runs fixed-step — the driver requires `n_steps` or `first_step`,
  exactly as it does for the symplectic methods. Inventing an error estimate for
  them would have let the controller adapt on a meaningless number, which is the
  failure this project has a recorded bug for.

- **Learning Hub: `Methods by Hand`.** Euler and RK4 written out the way a course
  teaches them — one row per step with the slope, the stages, the increment, the
  new value and the error — plus a halve-the-step table whose ratio column is the
  order, measured. Every number comes from the library's own stepper, and
  `tests/test_byhand.py` asserts the walkthrough matches `solve` at the same step
  size bit-for-bit.

- **Learning Hub: `Solve Step by Step`**, with **"check your answer"**. A student
  types their own solution; it is substituted into their equation and simplified.
  The same check the library already applies to sympy's answer, pointed at the
  user's instead — so equivalent forms pass, initial conditions are checked
  separately from the equation, and "cannot decide" is reported as such rather
  than as "wrong".

- **Learning Hub: `Worked Problems`**, and six textbook models behind it: mixing
  tank, Newton's cooling, RC circuit, falling with drag, harvested population,
  spring–mass–damper. The catalogue previously held only integrator benchmarks;
  these are what a first course is actually about, and each carries where its
  equation comes from and what the letters mean, in real units. They are ordinary
  catalogue entries, so they appear in the Solver Studio's pickers too.

### Changed

- **A check is never named unless it is the one performed.** Most answers in the
  Hub are decided by substituting them back and simplifying to zero, and the
  panel said so. A switched answer cannot be decided that way — differentiating
  a Heaviside leaves Dirac terms that never cancel *even when the answer is
  right* — so those are decided against this project's own integrator instead.
  `Derivation.check` records which route decided it, and the verdict line says
  what actually happened rather than claiming a substitution that never ran.

  An impulse can be decided by neither route and is reported unchecked. Never
  wrong: "cannot decide" is not "incorrect", the rule `check_answer` and
  `steps._conditions_hold` already follow.

- **`apart` is not asked to do the impossible.** It raises `PolynomialError` on
  an ``e^{-as}`` factor — on exactly the switched and impulsive problems this
  technique exists for. The delay is split off first and narrated as the second
  shifting theorem, so the obstacle and the teaching turn out to agree and the
  derivation gains a step rather than losing one.

- **A variable-coefficient equation is declined with its reason.** ``L{t·y'}``
  is a derivative in s, so transforming ``t·y' + y = 0`` produces another
  differential equation rather than an algebraic one. It previously produced an
  unevaluated `InverseLaplaceTransform` on screen and claimed the answer was
  *wrong*; it now says the transform does not simplify this equation, which is
  true and useful.

- **`_Placeholder` is gone.** It existed so a screen that was missing looked
  different from one that was broken, and every phase of the Learning Hub
  removed one. With the last replaced it was dead code, and the test that pinned
  the remaining set now asserts something stronger and permanent: no screen is a
  stand-in.


- **A derivation now outlives a `dsolve` that hangs.** The worker publishes the
  classification and the derivation *before* attempting `dsolve`, and the parent
  recovers that line from the killed process's captured output when the timeout
  fires. `y' = sin(y)` is the case: it is the equation this project records
  `dsolve` hanging on — not stalling, hanging — and separation of variables
  solves it in about four seconds. The Hub shows a complete verified derivation
  where the Studio can only report a timeout.

  What is published happens in two stages, cheapest first: the classification
  costs milliseconds, the derivation can cost seconds. Emitting only once, at
  the end of both, was a regression found by the test for it — a slow
  derivation took the classification down with it, so *asking* for steps made
  the reply worse than not asking.

  The remaining cost is stated rather than hidden: narration and `dsolve` share
  one hard budget, so a derivation slower than the timeout is lost with it. On
  a busy machine that happens — narrating `y' = sin(y)` takes about four
  seconds idle and can exceed thirty under a fully parallel test run. The
  classification always survives; the derivation is best-effort.


- **`driver.solve` split into the loop and its bookkeeping.** It had reached 408
  lines: the loop plus argument validation, step-endpoint arithmetic, output
  accumulation and event tracking. Those four now live in `odesuite/_loop.py`
  as `prepare_tolerances`, `StepPlanner`, `Recorder` and `EventTracker`, and
  `solve` is 237 lines of which 51 are its docstring. It is no longer the
  longest function in the project.

  Purely structural: the refactor was gated on 78 solves — every method family,
  dense output, `t_eval`, events with and without sub-step scanning, fixed-step
  runs, backward integration, DAEs, both failure paths and the callback —
  hashing **bit-identically** before and after, states, event times, work
  counters, messages and sampled dense output included.

- The extracted pieces have unit tests for the first time (`tests/test_loop.py`,
  36 of them). That was the point of extracting them: rules like "a fixed-step
  run lands on `t0 + k*h` computed afresh, never on an accumulated sum" — the
  arithmetic behind recorded bug #4 — could previously only be checked by
  inference from a finished trajectory.

- **`solve_bvp` split the same way**, 262 lines to 126 (96 of code). The
  shooting machinery — five closures over the function's own arguments — is now
  a `_ShootingSystem` holding the problem, the nodes and the inner solver's
  settings, exposing the three things Newton asks for: residual, Jacobian, and
  the spliced continuous solution. The Armijo backtracking is `_line_search`,
  which isolates the awkward part: a diverged shot raises rather than returning
  a large residual, and has to be read as "step too long". What remains in
  `solve_bvp` is the damped Newton iteration, which is its job.

  Gated on 32 BVP solves hashing bit-identically: linear and oscillatory
  problems at 1/2/5/10/20 nodes, all three guess forms, both Bratu branches,
  the iteration limit, a custom `fd_floor`, a stiff inner method, an
  unintegrable guess, and the three argument-validation errors.

  13 new tests check the machinery directly, the sharpest being the assembled
  Jacobian against a brute-force dense difference of the whole residual — the
  `-I` coupling blocks are written in analytically rather than differenced, and
  an error there converges fine on easy problems and fails mysteriously on hard
  ones.

- **The five screens no longer each rebuild their control column.** Every one of
  them opened `_build_controls` with the same seventeen lines of Qt scaffolding
  and closed it with the same five, and between them repeated a three-line
  heading idiom twenty-one times. Both are now `control_panel()` and
  `add_heading()` in `widgets/controls.py`, and `_build_controls` across the
  five drops from 441 lines to 322.

  Deliberately a helper and not a base class: the middles of those functions are
  genuinely different screens, and forcing them into one shape would be worse
  than the duplication. The panel width stays a caller's argument for the same
  reason — the five differ (238 to 258 px), which looks like drift rather than
  design, but unifying it would change the layout, and that is not what
  extracting boilerplate is for.

  Gated on 42 offscreen renders — every screen, both palettes, whole and
  per-panel — hashing **pixel-identically**.

### Fixed

- **An unparseable equation crashed the handler instead of reporting itself.**
  `show_message(..., error=True)` — the parameter is `kind` — so typing
  ``y' = foo(t)`` into `Solve Step by Step` raised a `TypeError` inside the
  signal handler and left the screen silent with a traceback on stderr. The
  editor only checks that a derivative is present, so anything it does not know
  about reaches `parse_equation` and fails there; this was reachable by typing.
  Shipped in L2 and found by writing the equivalent test for the Laplace screen.

- **A decimal initial condition poisoned the answer.** `y(0) = 0.1` parses to a
  float, which propagates through `solve` into a constant whose imaginary part
  is the *number* 3.14159… rather than `pi`. sympy cannot recognise that as pi,
  so `e^(t + 3.14159…i)` never collapsed to `-e^t`: the built-in logistic example
  displayed a complex exponential it did not need, and its conditions step was
  marked **failed** — a red cross on a correct step. Conditions are rationalised
  before solving, and the logistic now reads `e^t / (e^t + 9)`.

- **"Cannot decide" is no longer reported as "wrong"** when checking that a
  solution meets its initial conditions, matching the rule `check_answer`
  already follows. False has to mean demonstrably wrong; a floating-point
  residual or an unresolved parameter means undecided, and says so.

## [0.3.0] — 2026-08-17

### Added

- **`solve(..., callback=...)`** — called after every accepted step with
  ``(t, y, stats)``; returning ``False`` stops the integration and the solve
  returns ``status="cancelled"``. Progress reporting, live plotting, streaming
  output and cancellation from another thread were all previously impossible
  because nothing in the loop offered a way in.
- **`Solution.cancelled`**, distinguishing a deliberate stop from a failure.
  ``success`` stays False for a cancelled solve: the trajectory is valid but
  the requested interval was not integrated, and code checking ``success``
  before reading ``y[:, -1]`` as an endpoint must not treat a partial result as
  a complete one.
- **`Event(..., subdivisions=k)`** — samples the event function inside each step
  instead of only at its ends. Endpoint comparison misses any *even* number of
  crossings within a step, silently; measured on a smooth decay with
  ``g = sin(20t)``, 63 roots exist and endpoint comparison finds 5. With
  ``subdivisions=16`` all 63 are found, each to 2e-14. Off by default, since an
  event that changes sign once gains nothing. `scipy.integrate.solve_ivp` has no
  equivalent.
- **`SolveRunner.submit(..., supersede=True)`** and `cancel_all()` in the studio.
  A superseded solve now stops at its next step boundary instead of running to
  completion for an answer that will be discarded. Opt-in, because concurrency
  is not always supersession — the Method Race submits one solve per method
  through the same runner and wants every one of them.
- `examples/09_progress_and_hidden_events.py`.

### Documented

- **Where `PredictiveController` loses.** The Tier 2 measurements that made it
  the default for implicit methods all used problems supplying an analytic
  Jacobian. Differenced, it still wins on HIRES (0.83x), Van der Pol (0.84x) and
  OREGO (0.87x), but costs 2.10x on Robertson, whose own finite-difference
  Jacobian is notoriously poor — one component near 1e-8 against entries of `J`
  reaching 3e7. Supplying `jac`, as its catalogue entry does, reverses it. The
  docstring now carries the table and two tests pin it.

## [0.2.0] — 2026-08-17

The first release that can be installed, and the first with a measured
performance claim behind it.

### Added

- **`PredictiveController`** — Gustafsson's predictive step-size controller, and
  the default for the implicit methods. It adds a term reading how the error
  responded to the last step-size change rather than the current error alone,
  and declines any proposed growth under 1.2× outright, keeping `h`
  bit-for-bit identical so the iteration matrix stays valid.
- **`Stepper.default_controller`** — a method now states which controller suits
  it. A step-size change is free for an explicit method and costs an `O(n³)`
  refactorisation for an implicit one; that is a property of the method, not a
  caller preference.
- `examples/` — eight runnable scripts, every one executed by the test suite.
- A documentation site (`mkdocs.yml`, `docs/`) with an API reference generated
  from the docstrings.
- `py.typed` — the library has been fully annotated and `mypy`-clean for a while,
  and without this marker none of that was visible to a downstream type checker.
- `ruff` and `mypy` configuration, and GitHub Actions CI across Linux and
  Windows on Python 3.10 and 3.12, including a job asserting that the library
  never imports Qt.
- `tests/test_controllers.py` and `tests/test_newton.py` — the two modules that
  had no direct tests at all.
- `figures/work_precision.json`, written beside the figure so a change in
  performance is a reviewable diff rather than something spotted by eye.

### Changed

- **Stiff solvers are 1.18–1.32× faster**, using 19% fewer RHS evaluations and
  10% fewer LU factorisations. Against SciPy's Radau the gap closed from
  1.3–1.5× evaluations to 1.08–1.22×, and from ~1.7× wall time to 1.2–1.5×.
  Explicit methods are unaffected, and a test asserts their output is bitwise
  identical.
- `irk.py` now uses `simplified_newton` and `JacobianPolicy` instead of
  reimplementing both inline. Verified bit-identical on the stiff benchmarks.
- `ODEProblem.f` fast-paths a right-hand side that already returns a 1-D array;
  `is_dae` is cached instead of running an SVD on every access.
- `solve(controller=...)` now defaults to `None`, meaning "let the method
  choose". Passing a name or instance still overrides it.
- The work-precision figure wraps into a grid; it was previously a 3 806 px-wide
  strip in which no legend was legible.
- The version is declared once, in `odesuite.__version__`. It had drifted across
  three files.

### Fixed

- **A reused `Controller` instance carried its error history between solves**, so
  the same problem solved twice gave 82 steps and then 83. Nothing raised and
  both answers were within tolerance; the only symptom was that an identical
  computation was not reproducible.
- **`thumbnails.render_thumbnail` drove pyplot from a worker thread** while its
  own docstring promised thread-safety. pyplot's figure registry is global and
  `matplotlib.use` swaps the global backend.
- A non-finite state is now reported as such instead of surfacing as step-size
  underflow, which named nothing the caller had written.
- `_solve_event` returned the end of the step as a root when the bracket did not
  survive interpolation — a fabricated detection, which could also consume a
  terminal event's allowance. It now reports none.
- `DSOLVE_TIMEOUT` was bound as a default argument at import and could not be
  changed at runtime; `symbolicpanel` had imported the value rather than the
  module, freezing it twice over.
- `odesuite-gui` printed a bare PySide6 traceback when the `app` extra was not
  installed. It now says which extra to install. `--list-problems` and
  `--selftest` work without Qt.
- A docstring in `steppers/exponential.py` had a prose paragraph inside its
  `Parameters` block, so every numpydoc tool read the first word of each line as
  a parameter name.
- `test_split_solve_is_cheaper_on_a_large_system` compared two ~4 ms wall-clock
  samples and inverted under `pytest -n auto`. It now times the factorisation
  the claim is actually about (a ~9x margin rather than 1.5x), and skips where
  the platform BLAS has a pathologically slow complex `getrf` — measured at
  1300x slower than the real path for n >= 100 with numpy 2.2.6 on Windows,
  which makes the split path lose for reasons that have nothing to do with this
  library. The deterministic half of the old test, that the two linear-solve
  paths agree, is now its own test.

## [0.1.0] — 2026-08-16

The state of the project when it came under version control: the library, the
studio, and 943 tests. Its development is narrated in the README — the adaptive
Runge–Kutta core, stiff solvers and DAEs, events and dense output, the Taylor
and exponential integrators, the symbolic equation solver, and the typeset
closed forms.

[0.2.0]: https://keepachangelog.com/
[0.1.0]: https://keepachangelog.com/
