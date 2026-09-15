"""What the application was looking at, saved and restored.

Van der Pol at mu = 800, radau, rtol = 1e-9, on the Stiffness Explorer, could
not be written down. Closing the application lost it, and there was no way to
hand a class a configured starting point — an instructor could describe one in
prose and nothing more.

Two decisions worth stating.

**A session is a request, not a result.** Only what the user *chose* is stored:
the problem, the method, the tolerances, the parameter values, the screen. Not
the solution, which is recomputed in a fraction of a second and would otherwise
be a large file that goes stale the moment anything changes. Reproducibility of
the *answer* is `SolveRequest.as_code`'s job and is a separate feature.

**A user equation is stored as its source text, and is re-validated on the way
back in.** That is the whole security question here. Until now every expression
the parser saw had just been typed by the person sitting there; a session file
can arrive from anywhere. Loading re-parses it through `symbolic.parse_equation`,
which is the same door the keyboard uses and therefore the same
`reject_unsafe_syntax` check, so a file cannot smuggle an expression past a
guard that a person cannot. See `SECURITY.md`.

The write is atomic and a bad file is never fatal, both for the reasons
`progress.py` gives at length: losing a saved session is a small harm, refusing
to start is a large one.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from . import catalog, progress

__all__ = ["FORMAT", "capture", "apply", "save", "load", "default_path"]

#: Bumped when a stored field changes meaning. A file from a future version is
#: declined rather than half-read.
FORMAT = 1

_FILENAME = "session.json"


def default_path() -> Path:
    """Where the session is kept between runs.

    Beside `progress.json`, in the same per-user directory, because it is the
    same kind of thing: small, yours, and disclosed in the README.
    """
    return progress.directory() / _FILENAME


def capture(state, screen: str = "", equation=None) -> dict[str, Any]:
    """The session as plain data.

    `equation` is the `symbolic.EquationSpec` behind a typed equation, when the
    current problem is one. The caller has it; `catalog` keeps only the built
    entry, from which the text the user wrote cannot be recovered.
    """
    session: dict[str, Any] = {
        "format": FORMAT,
        "problem": state.problem_key,
        "method": state.method,
        "rtol": float(state.rtol),
        "atol": float(state.atol),
        "n_steps": int(state.n_steps),
        "params": {name: float(value) for name, value in state.params.items()},
    }
    if screen:
        session["screen"] = screen

    # A typed equation is not in the catalogue, so the key alone would restore
    # nothing. Store the text the user wrote and re-parse it on load.
    if state.problem_key == catalog.USER_KEY and equation is not None:
        session["equation"] = {
            "equations": list(equation.equations),
            "initial_conditions": equation.initial_conditions,
            "variables": list(equation.variables),
            "parameters": {k: float(v) for k, v in equation.parameters.items()},
            "t_span": [float(equation.t_span[0]), float(equation.t_span[1])],
            "name": equation.name,
        }
    return session


def apply(state, session: dict[str, Any]) -> str:
    """Put `session` back into `state`. Returns the screen id, or "".

    Every field is applied defensively. A session file is ordinary user data
    that may have been edited, truncated or written by another version, and one
    unusable field should cost that field rather than the whole restore.
    """
    if not isinstance(session, dict) or session.get("format") != FORMAT:
        return ""

    key = session.get("problem")

    equation = session.get("equation")
    if key == catalog.USER_KEY and isinstance(equation, dict):
        key = _restore_equation(equation)
        if key is None:
            return ""       # the equation was the session; without it there is none

    if not isinstance(key, str) or key not in catalog.keys(include_user=True):
        return ""

    state.set_problem(key)

    method = session.get("method")
    from .state import methods_for

    available = {
        name for group in methods_for(catalog.get(key)).values() for name in group
    }
    if isinstance(method, str) and method in available:
        state.set_method(method)

    rtol, atol = session.get("rtol"), session.get("atol")
    if isinstance(rtol, (int, float)) and isinstance(atol, (int, float)):
        if rtol > 0 and atol >= 0:
            state.set_tolerances(float(rtol), float(atol))

    n_steps = session.get("n_steps")
    if isinstance(n_steps, int) and n_steps > 0:
        state.set_n_steps(n_steps)

    params = session.get("params")
    if isinstance(params, dict):
        known = {spec.name: spec for spec in catalog.get(key).params}
        for name, value in params.items():
            if name in known and isinstance(value, (int, float)):
                # Clamped to the slider's own range: a value from outside it
                # would restore a state the interface cannot represent, and the
                # first touch of the control would jump.
                state.set_param(name, known[name].clamp(float(value)))

    screen = session.get("screen")
    return screen if isinstance(screen, str) else ""


def _restore_equation(equation: dict[str, Any]) -> str | None:
    """Rebuild a typed equation, through the parser's own front door.

    `parse_equation` is called rather than bypassed, so the text in a session
    file goes through `reject_unsafe_syntax` exactly as text from the keyboard
    does. A file is not a more trustworthy source than a person -- it is a less
    trustworthy one, because it can arrive from somewhere else.
    """
    from .custom import ParseError
    from .equationmodel import build_entry
    from .symbolic import EquationSpec, parse_equation

    try:
        spec = EquationSpec(
            equations=[str(e) for e in equation["equations"]],
            initial_conditions=str(equation.get("initial_conditions") or ""),
            variables=[str(v) for v in equation.get("variables") or ["y"]],
            parameters={
                str(k): float(v)
                for k, v in (equation.get("parameters") or {}).items()
            },
            t_span=(float(equation["t_span"][0]), float(equation["t_span"][1])),
            name=str(equation.get("name") or "equation"),
        )
        entry = build_entry(parse_equation(spec))
    except (KeyError, TypeError, ValueError, ParseError):
        return None
    catalog.register_user_equation(entry)
    return catalog.USER_KEY


def save(state, screen: str = "", path: Path | None = None, equation=None) -> Path | None:
    """Write the session. Returns the path, or None if it could not be written.

    Never raises. A session that fails to save is a small loss and not a reason
    to interrupt anyone, which is the rule `progress.py` sets for the only other
    file this application writes.
    """
    destination = Path(path) if path is not None else default_path()
    try:
        payload = capture(state, screen, equation)
        destination.parent.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(dir=destination.parent, suffix=".tmp")
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=1, sort_keys=True)
            os.replace(temporary, destination)
        except BaseException:
            Path(temporary).unlink(missing_ok=True)
            raise
    except Exception:
        return None
    return destination


def load(path: Path | None = None) -> dict[str, Any] | None:
    """Read a session file. Returns None for anything unusable.

    Anything at all: missing, truncated, not JSON, not an object, written by a
    version that stored something else. All of them mean "no session", never an
    error, for the same reason `progress.load` does.
    """
    source = Path(path) if path is not None else default_path()
    try:
        with source.open(encoding="utf-8") as stream:
            session = json.load(stream)
    except Exception:
        return None
    if not isinstance(session, dict) or session.get("format") != FORMAT:
        return None
    return session
