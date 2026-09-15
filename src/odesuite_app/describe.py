"""Saying in words what a solution curve does.

The rest of this application draws. A learner who cannot see the drawing gets
nothing from the Solver Lab at all, and that is the single largest gap between
what the product is and what it claims: it honours the rule of four --
analytic, numeric, graphical, verbal -- everywhere except the one
representation it is built around.

So every plotted solution gets a paragraph. It becomes the plot's accessible
description, which is what a screen reader announces in place of the picture,
and it is shown beside the data table as ordinary text, because the verbal
reading of a curve is useful to somebody who can see it too. *Oscillating with
decaying amplitude, settling to 0* is a sentence most students would not
produce unprompted from the same picture.

**Nothing here is asserted; all of it is measured.** The shape comes from
counting turning points, the limit from comparing the last tenth of the record
with the value at the end, and blow-up from the solver's own report that it
stopped early. A summary that guessed would be worse than none: it is the only
description its reader has, and they have no way to check it against the
picture.

No Qt, so it can be tested on arrays.
"""

from __future__ import annotations

import numpy as np

__all__ = ["summarise", "component_summary", "table_rows"]

#: Below this fraction of a component's own range, a wiggle is noise from the
#: integrator rather than a turning point of the solution. Measured against
#: the range rather than against an absolute size, because a component may be
#: of order 1e-6 (Robertson's second species) or 1e11 (its time axis).
_WIGGLE = 0.02

#: How much of the record counts as "the end", for deciding whether a solution
#: has settled. A tenth is long enough that one slow final step cannot decide
#: it and short enough that the transient is over.
_TAIL = 0.1


def _number(value: float) -> str:
    """A number in the form this application prints them.

    Three significant figures, and a plain integer where the value is one:
    "settling to 1" reads better than "settling to 1.00", and a reader
    listening to it rather than seeing it has fewer syllables to hold.
    """
    if not np.isfinite(value):
        return "not a finite number"
    if abs(value) < 5e-13:
        return "0"
    if float(value).is_integer() and abs(value) < 1e6:
        return f"{int(value)}"
    return f"{value:.3g}"


def _turning_points(values: np.ndarray) -> np.ndarray:
    """Indices where the curve changes direction, ignoring integrator noise.

    Two implementations were tried and the first was wrong in a way worth
    recording. Counting sign changes of `diff`, with small differences
    discarded, compares *one step* against a fraction of the whole range --
    so on a finely sampled curve every step is small, every step is discarded,
    and a decaying oscillation was reported as turning once. Step size is a
    property of the solver, not of the solution, and nothing about the shape
    of a curve may depend on it.

    What is measured instead is the *swing*: a turn is confirmed only once the
    curve has retraced by more than `_WIGGLE` of its own range from the
    extreme it reached, which is the same answer at any sampling density and
    still refuses to call a rounding wobble an oscillation.
    """
    finite = values[np.isfinite(values)]
    if finite.size < 3:
        return np.empty(0, dtype=int)
    span = float(np.max(finite) - np.min(finite))
    if span <= 0:
        return np.empty(0, dtype=int)
    threshold = _WIGGLE * span

    found: list[int] = []
    direction = 0               # +1 while rising, -1 while falling
    pivot = 0                   # the extreme reached since the last turn
    for index in range(1, values.size):
        value = values[index]
        if not np.isfinite(value):
            break
        if direction >= 0 and value >= values[pivot]:
            pivot = index
            direction = direction or (1 if value > values[0] else 0)
        elif direction <= 0 and value <= values[pivot]:
            pivot = index
            direction = direction or (-1 if value < values[0] else 0)
        elif direction >= 0 and value < values[pivot] - threshold:
            if direction > 0:
                found.append(pivot)
            direction, pivot = -1, index
        elif direction <= 0 and value > values[pivot] + threshold:
            if direction < 0:
                found.append(pivot)
            direction, pivot = 1, index
    return np.asarray(found, dtype=int)


def _amplitude_trend(values: np.ndarray, turns: np.ndarray) -> str:
    """Whether successive swings are getting bigger, smaller, or neither.

    Compares the first half of the turning points with the second half rather
    than the first extremum with the last: one anomalous swing at either end
    -- which a forced system routinely has -- would otherwise decide it.
    """
    if turns.size < 4:
        return ""
    middle = float(np.mean(values[np.isfinite(values)]))
    swings = np.abs(values[turns] - middle)
    half = swings.size // 2
    early = float(np.mean(swings[:half]))
    late = float(np.mean(swings[half:]))
    if early <= 0:
        return ""
    if late < 0.6 * early:
        return "decaying"
    if late > 1.6 * early:
        return "growing"
    return "steady"


def component_summary(t: np.ndarray, values: np.ndarray, name: str,
                      *, complete: bool = True) -> str:
    """One sentence about one component.

    `complete` is the solver's own verdict on whether it reached the end of
    the interval. It is passed in rather than inferred, because a run that
    stopped early and a run that finished can leave identical arrays behind --
    the difference is in `Solution.status`, and guessing at it from the values
    is exactly the kind of assertion this module refuses to make.
    """
    values = np.asarray(values, dtype=float)
    t = np.asarray(t, dtype=float)
    if values.size == 0:
        return f"{name}: nothing was computed."

    start, end = float(values[0]), float(values[-1])
    finite = np.isfinite(values)
    if not finite.all():
        where = float(t[~finite][0]) if (~finite).any() else float(t[-1])
        return (f"{name} starts at {_number(start)} and stops being a number "
                f"at t = {_number(where)}.")

    lo, hi = float(np.min(values)), float(np.max(values))
    turns = _turning_points(values)

    # The shape.
    if turns.size == 0:
        if hi - lo <= _WIGGLE * (abs(hi) + abs(lo) + 1e-30):
            shape = "holds steady"
        elif end > start:
            shape = "rises without turning back"
        else:
            shape = "falls without turning back"
    elif turns.size == 1:
        peak = "a maximum" if values[turns[0]] >= 0.5 * (lo + hi) else "a minimum"
        shape = (f"turns once, reaching {peak} of "
                 f"{_number(float(values[turns[0]]))} at "
                 f"t = {_number(float(t[turns[0]]))}")
    else:
        trend = _amplitude_trend(values, turns)
        qualifier = {"decaying": " with decaying amplitude",
                     "growing": " with growing amplitude",
                     "steady": " at a steady amplitude"}.get(trend, "")
        shape = f"oscillates{qualifier}, turning {turns.size} times"

    # Where it ends up.
    tail = values[t >= t[-1] - _TAIL * (t[-1] - t[0] or 1.0)]
    settled = tail.size > 1 and (
        float(np.max(tail) - np.min(tail)) <= _WIGGLE * max(hi - lo, 1e-30)
    )
    if not complete:
        ending = f"and the solve stopped at t = {_number(float(t[-1]))}"
    elif settled:
        ending = f"and settles to {_number(end)}"
    elif abs(end) > 10 * max(abs(start), abs(lo), abs(hi) - abs(end), 1e-30):
        ending = f"and is still growing, reaching {_number(end)}"
    else:
        ending = f"and ends at {_number(end)}"

    return (f"{name} starts at {_number(start)}, {shape}, {ending}. "
            f"It stays between {_number(lo)} and {_number(hi)}.")


def summarise(solution, labels=(), *, title: str = "", limit: int = 4) -> str:
    """A paragraph describing a whole solution, for a plot's alt text.

    `limit` caps how many components are described one by one. Pleiades has
    twenty-eight and a paragraph naming all of them is not a description, it
    is the data table read aloud -- which is what the data table is for.
    """
    t = _real(solution.t)
    y = _real(solution.y)
    if t.size == 0 or y.size == 0:
        return "Nothing was plotted: the solve produced no output."

    # `success` rather than the status string: a terminal event is a complete
    # answer to the question that was asked, and only the library knows which
    # of its four statuses mean that.
    complete = bool(getattr(solution, "success", True))
    lead = f"{title}: " if title else ""
    span = (f"{y.shape[0]} component{'s' if y.shape[0] != 1 else ''} over "
            f"t from {_number(float(t[0]))} to {_number(float(t[-1]))}, "
            f"at {t.size} output points.")

    described = min(y.shape[0], max(1, int(limit)))
    sentences = [
        component_summary(
            t, y[index],
            labels[index] if index < len(labels) else f"y[{index}]",
            complete=complete,
        )
        for index in range(described)
    ]
    if y.shape[0] > described:
        sentences.append(
            f"The remaining {y.shape[0] - described} components are in the "
            "data table."
        )
    if not complete:
        sentences.append(
            "The solver did not reach the end of the interval: "
            f"{getattr(solution, 'message', '') or 'it stopped early'}."
        )
    return lead + span + " " + " ".join(sentences)


def _real(values) -> np.ndarray:
    """`values` as floats, taking the real part of a complex state.

    The spectral problems integrate complex Fourier coefficients, and numpy
    casts those to float with a warning rather than an error. Saying so here
    is the difference between a considered choice and a silent truncation:
    what these views show of a complex state is its real part, which is what
    the spacetime image shows too.
    """
    values = np.asarray(values)
    if np.iscomplexobj(values):
        return np.real(values).astype(float)
    return values.astype(float)


def table_rows(solution, limit: int = 2000):
    """``(t, y)`` thinned to at most `limit` rows, for the data table.

    Thinned by taking every n-th output point rather than by resampling: a
    table is read a row at a time and every row in it should be a number the
    solver actually produced, not an interpolation of two that it did. The
    first and last rows are always kept, because they are the two anybody
    looks for.
    """
    t = _real(solution.t)
    y = _real(solution.y)
    if t.size <= limit:
        return t, y
    stride = int(np.ceil(t.size / limit))
    keep = np.arange(0, t.size, stride)
    if keep[-1] != t.size - 1:
        keep = np.append(keep, t.size - 1)
    return t[keep], y[:, keep]
