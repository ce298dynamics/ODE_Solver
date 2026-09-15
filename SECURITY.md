# Security policy

## Reporting a vulnerability

Email **ce298.dynamics@gmail.com** with "odesuite security" in the subject.
Please include what you did, what happened, and the version
(`python -c "import odesuite; print(odesuite.__version__)"`).

This is a single-maintainer project, so please allow a few days for a first
reply. Do not open a public issue for something that lets an attacker run code
or read files; email first and we can decide together when to publish.

## What is in scope

The threat this project actually has is **untrusted input reaching a parser or
an evaluator**. Concretely:

- **Typed expressions.** Anything entered as an equation, a right-hand side, an
  initial condition or an answer — the Solver Lab's "build your own system", the
  equation editor, the Laplace screen, the lesson answer boxes. All of it
  reaches sympy, and sympy's parser *evaluates* what it is given.
- **Files the application reads.** `progress.json`, and any session file a
  future version learns to open.
- **The `dsolve` subprocess boundary** (`odesuite_app/dsolve_worker.py`), which
  exchanges JSON over a pipe.
- **Anything importable.** `odesuite` and `odesuite_app` are published packages;
  a caller may feed `odesuite_app.custom.build` input this application never
  would.

## What is not in scope

- **The user attacking their own machine.** This is a desktop application that
  runs your code on your computer at your request. If you type something into
  your own copy that deletes your own files, that is the tool working. What is
  in scope is the same thing arriving from *somewhere else* — an equation
  pasted from a classmate, a forum, or a handout.
- **Denial of service by an expensive computation.** Asking for a stiff problem
  at `rtol=1e-13` will take a long time on purpose. `dsolve` is bounded by a
  timeout (`symbolic.DSOLVE_TIMEOUT`) because it can hang forever; solvers are
  bounded by `max_steps`. Beyond that, slow is not a vulnerability.
- **Networked attack.** There is none to have: the application makes no network
  requests of any kind. See "Privacy" below.

## How expression parsing is defended

Worth stating plainly, because it is the part that matters and because it took
two goes to get right.

`sympy.sympify` and `sympy.parsing.parse_expr` **evaluate** their input. There
are two independent ways out of that, and both have to be closed:

1. **Names.** `sympify`'s `locals` argument adds names but removes none, so the
   ordinary builtins stay reachable and `sympify('__import__("os").system(...)')`
   runs the command. Every parse in this application goes through `parse_expr`
   with an explicit `global_dict` whose `__builtins__` is an **empty mapping** —
   emptied rather than omitted, because an absent `__builtins__` key makes
   Python reinstate the real one.

2. **Syntax.** A name whitelist controls what *resolves*; it says nothing about
   where an expression may go *from* a name that resolves legitimately. `sin` is
   whitelisted, and `sin.__class__.__init__.__globals__["__builtins__"]` is the
   real builtins — arbitrary code execution without naming anything forbidden.
   `odesuite_app.custom.reject_unsafe_syntax` therefore checks the text **as
   typed, before sympy compiles it**, and refuses the construct rather than the
   name: no attribute access, no subscripting, no lambdas or comprehensions, and
   calls only to a bare name. What is left is arithmetic.

Both checks are required and neither is sufficient alone. Any new call to
`parse_expr` must be preceded by `reject_unsafe_syntax`; there are two such
calls (`custom._parse` and `symbolic._parse_side`) and both are guarded.

`tests/test_security.py` is the record: it drives known escapes through both
entry points and proves, with a canary file, that nothing ran — and it asserts
that every equation the course itself contains still parses, because a guard
that rejected `sec(t)` would be a worse bug than the one it fixed.

## Privacy

The application makes **no network requests**, collects no telemetry, and has no
analytics or crash reporting. The only thing it writes is `progress.json` —
which lesson questions you have attempted and how they went — in your ordinary
per-user configuration directory. It is written atomically, an unreadable file
is treated as "no progress recorded" rather than an error, and there is a button
in the interface that deletes it.

## Supported versions

The latest released version is the supported one. This project has not yet
reached 1.0 and does not backport fixes.
