"""The subprocess that runs `sympy.dsolve`.

Separate process rather than a thread, for one reason: `dsolve` can hang. Not
take a long time -- hang. ``y' = sin(y)`` and ``y'' + sin(y) = 0`` never return,
and a Python thread cannot be killed from outside, so the only way to impose a
time limit is to own a process and terminate it.

Communication is JSON over stdin/stdout carrying `sympy.srepr` strings, which
round-trip exactly and, unlike pickle, cannot execute anything on the way back.

Invoked through the ordinary CLI (``--dsolve-worker``) so it works identically
from source and inside a frozen build, where ``sys.executable`` is the
application rather than an interpreter.
"""

from __future__ import annotations

import json
import sys

__all__ = ["run", "solve_payload"]


def derivation_reply(equation, function, ics: dict) -> dict | None:
    """`steps.derive` reduced to plain JSON-able data, or None if nothing applies."""
    import sympy as sp

    from .steps import derive

    hints = sp.classify_ode(equation, function)
    return _as_dict(derive(equation, function.func, hints=hints, ics=ics))


def systems_reply(equations, functions, ics: dict) -> dict | None:
    """The same, for a system solved by eigenvalues.

    `systems.derive` returns a `steps.Derivation` as well, so a system's
    working travels the same wire and renders in the same panel as every other
    technique -- which is the whole reason that shape was fixed early.
    """
    from .systems import derive

    return _as_dict(derive(equations, [f.func for f in functions], ics=ics))


def laplace_reply(equation, function, ics: dict) -> dict | None:
    """The same, for the transform method.

    `laplace.derive` returns a `steps.Derivation` too, so it travels over the
    same wire format and renders through the same panel.
    """
    from .laplace import derive

    return _as_dict(derive(equation, function.func, ics=ics))


def _as_dict(derivation) -> dict | None:
    import sympy as sp

    if derivation is None:
        return None
    return {
        "technique": derivation.technique,
        "title": derivation.title,
        "message": derivation.message,
        "verified": derivation.verified,
        "check": derivation.check,
        "result": None if derivation.result is None else sp.srepr(derivation.result),
        "steps": [
            {"title": s.title, "latex": s.latex, "note": s.note,
             "verified": s.verified}
            for s in derivation.steps
        ],
    }


def _right_hand_side(solved) -> str:
    """`sp.srepr` of a `dsolve` answer, which is not always one equation.

    For a single equation `dsolve` usually returns one `Eq`, but where solving
    for y leaves branches it returns a *list* of them -- ``y' + y = t*y**3``
    comes back as the plus and minus square roots. Reading `.rhs` off the list
    raised `AttributeError`, which the caller then reported as "no method",
    throwing away an answer sympy had actually found. The first branch is the
    one taken, as everywhere else here that a rearrangement produces two.
    """
    import sympy as sp

    if isinstance(solved, (list, tuple)):
        if not solved:
            raise ValueError("dsolve returned no solutions")
        solved = solved[0]
    return sp.srepr(solved.rhs)


def solve_payload(payload: dict, emit=None) -> dict:
    """Do the symbolic work described by `payload` and return a plain-dict reply.

    `emit`, when given, is called with the reply as soon as the classification
    and any derivation are ready and **before** `dsolve` is attempted. That
    ordering is deliberate: `dsolve` is the part that hangs, and a derivation
    already computed should not die with it. ``y' = sin(y)`` is the case that
    motivates it -- `dsolve` never returns, while separation of variables
    solves it in a few seconds.
    """
    import sympy as sp

    equations = [sp.sympify(text) for text in payload["equations"]]
    functions = [sp.sympify(text) for text in payload["functions"]]
    ics = {
        sp.sympify(key): sp.sympify(value)
        for key, value in payload.get("ics", {}).items()
    }

    reply: dict = {"ok": False}

    # The transform method is a different question, not a variation on this
    # one: it wants the derivation and nothing else. `dsolve` is not run at all
    # -- the derivation already carries the answer and checks it, and skipping
    # the one part of this module that can hang costs nothing here.
    if payload.get("mode") == "laplace" and len(equations) == 1:
        try:
            reply["derivation"] = laplace_reply(equations[0], functions[0], ics)
            reply["ok"] = True
        except Exception as exc:
            reply["error"] = f"{type(exc).__name__}: {exc}"
        if emit is not None:
            emit(dict(reply, partial=True))
        return reply

    # Classification first: it is fast, it is useful even when no closed form
    # comes out, and it is what tells the user *why* their equation is easy or
    # hard.
    #
    # The whole tuple is returned, not just its head. `classify_ode` orders
    # hints by what sympy would rather solve with, which is not the order a
    # course teaches: `y'' + 3y' + 2y = 0` leads with `factorable` and
    # `y' + 2y = t` with `1st_exact`. Choosing among them is the caller's job
    # (`symbolic.preferred_hint`), and it cannot choose from one string.
    if len(equations) == 1:
        try:
            hints = sp.classify_ode(equations[0], functions[0])
            reply["hints"] = [h for h in hints if not h.endswith("_Integral")]
            reply["classification"] = hints[0] if hints else ""
        except Exception:
            reply["hints"] = []
            reply["classification"] = ""

    # Published in two stages, cheapest first. Classification takes
    # milliseconds and narration can take seconds, so emitting only once -- at
    # the end of both -- meant that asking for steps could lose the
    # classification a caller would otherwise have kept when the timeout fired.
    if emit is not None:
        emit(dict(reply, partial=True))

    # Systems narrate too, by a different route. `classify_ode` has nothing to
    # say about a system -- there are no hints above -- so the technique is not
    # chosen from a hint list but from the shape of the equations, and
    # `systems.derive` declines anything that is not a homogeneous
    # constant-coefficient first-order system.
    if payload.get("steps"):
        try:
            reply["derivation"] = (
                derivation_reply(equations[0], functions[0], ics)
                if len(equations) == 1
                else systems_reply(equations, functions, ics)
            )
        except Exception as exc:                  # narration is never fatal
            reply["derivation"] = None
            reply["derivation_error"] = f"{type(exc).__name__}: {exc}"
        if emit is not None:
            emit(dict(reply, partial=True))

    # Where the derivation found and *verified* an answer by a technique
    # `classify_ode` never named, asking `dsolve` is asking the one part of
    # this module that can hang to reproduce something already in hand.
    #
    # This is not hypothetical. Exact equations are recognised structurally
    # rather than from a hint, because sympy misses them; and on
    # `y' = -(2t + y)/(t + 3y²)` -- a plain exact equation -- `dsolve` runs
    # past forty seconds trying `lie_group`, so the entire twelve-second
    # budget buys a timeout. The narrated answer was substituted back and
    # simplified to zero before it got here, which is a stronger warrant than
    # `dsolve` returning would have been.
    #
    # Deliberately narrow: if the technique *is* in the hint list, sympy knows
    # it too and is asked as usual, so nothing that worked before changes.
    found = reply.get("derivation")
    if (found and len(equations) == 1
            and found.get("technique") not in set(reply.get("hints") or ())):
        if found.get("verified") is True and found.get("result"):
            reply["particular" if ics else "general"] = found["result"]
            reply["ok"] = True
        else:
            # No answer to hand over, but the same fact holds: sympy named no
            # technique, so `dsolve` is being asked to find something out of
            # nowhere, and on these equations that means the full timeout.
            reply["error"] = (
                "sympy has no method for this equation; the working shown was "
                "produced without it"
            )
        return reply

    try:
        if len(equations) == 1:
            general = sp.dsolve(equations[0], functions[0])
            reply["general"] = _right_hand_side(general)
            if ics:
                particular = sp.dsolve(equations[0], functions[0], ics=ics)
                reply["particular"] = _right_hand_side(particular)
        else:
            general = sp.dsolve(equations)
            reply["general"] = [_right_hand_side(item) for item in general]
            if ics:
                particular = sp.dsolve(equations, ics=ics)
                reply["particular"] = [_right_hand_side(item)
                                       for item in particular]
        reply["ok"] = True
    except NotImplementedError:
        reply["error"] = "sympy has no method for this equation"
    except Exception as exc:
        # An initial-value problem can fail where the general solution
        # succeeded -- inconsistent or insufficient conditions. Keep whatever
        # was obtained rather than discarding it.
        if "general" in reply:
            reply["ok"] = True
            reply["message"] = (
                f"general solution found, but the initial conditions could not "
                f"be applied ({type(exc).__name__})"
            )
        else:
            reply["error"] = f"{type(exc).__name__}: {exc}"
    return reply


def run() -> int:
    """Read one request from stdin, write one reply to stdout."""
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"bad request: {exc}"}))
        return 1

    def emit(partial: dict) -> None:
        """Publish what is already known, in case `dsolve` never returns.

        Flushed immediately: the parent reads this back out of the killed
        process's captured output when the timeout fires.
        """
        print(json.dumps(partial), flush=True)

    try:
        reply = solve_payload(payload, emit=emit)
    except Exception as exc:                              # never crash silently
        reply = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    print(json.dumps(reply))
    return 0


if __name__ == "__main__":
    sys.exit(run())
