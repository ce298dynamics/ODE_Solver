"""One place that knows which narrator explains what.

This dispatch used to be written out in four separate spots across
`test_lessons.py` and `test_templates.py` -- once for a lesson, once for a
worked example, once for a template's solvability and again for its claimed
technique. Adding the systems narrator missed two of them; adding the series
narrator missed a third. Every one of those failures read as "no technique
applies" about content that was perfectly fine, which is the most misleading
way a test can fail.

The screen keeps its own dispatch and should: it runs the symbolic solve in a
subprocess with a timeout, which the tests deliberately bypass in order to
narrate directly and quickly.
"""

from __future__ import annotations

#: Every narrator a lesson, example or template may name.
NARRATORS = {"steps", "laplace", "systems", "series"}


def narrate(narrator: str, parsed):
    """The derivation `narrator` produces for an already-parsed equation."""
    import sympy as sp

    from odesuite_app import laplace, series, steps, systems

    if narrator == "laplace":
        return laplace.derive(parsed.equation, parsed.function, ics=parsed.ics)
    if narrator == "systems":
        return systems.derive(parsed.equations, parsed.functions,
                              ics=parsed.ics)
    if narrator == "series":
        return series.derive(parsed.equation, parsed.function, ics=parsed.ics)
    return steps.derive(
        parsed.equation, parsed.function,
        hints=sp.classify_ode(parsed.equation,
                              parsed.function(sp.Symbol("t", real=True))),
        ics=parsed.ics,
    )
