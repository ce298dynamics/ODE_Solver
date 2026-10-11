"""Typesetting sympy expressions as images.

The symbolic engine returns things like ``exp(-t)*(cos(2*t) + sin(2*t)/2)``.
Printed that way they read as source code; the whole point of solving an
equation symbolically is that the answer should look like the answer. So
expressions go through ``sympy.latex`` and matplotlib's mathtext to a PNG, and
from there to a ``QPixmap``. No LaTeX installation is involved.

Three things were measured before this was written, and each one decided part
of the design:

**Mathtext has no environments.** It implements a large subset of LaTeX, but
``\\begin{...}`` is not in it -- ``cases``, ``matrix``, ``aligned`` and the
hypergeometric printer all raise. That matters because `dsolve` genuinely
returns `Piecewise` and `Matrix` results. Rather than discover this by catching
a `ValueError` from inside a worker thread, `is_renderable` rejects such input
up front and `rows` decomposes it into pieces that *can* be typeset, to be
stacked by a Qt layout. A column of separate rows is better typography than a
cramped ``cases`` brace in any case.

**pyplot is not thread-safe.** Its global figure registry is shared mutable
state, so this module drives `Figure` and `FigureCanvasAgg` directly. That path
was verified with sixteen concurrent renders across four threads.

**Rendering is fast but not free**: 11-25 ms for a typical expression, 74 ms for
a third-order forced general solution, plus about 100 ms once while matplotlib
builds its font cache. One expression inline is imperceptible; re-rendering a
whole screen -- which is exactly what a theme switch does, since the colour is
baked into the image -- is not. Hence the cache.

Everything above `pixmap` is free of Qt, so the rendering can be exercised
headlessly and run on a worker thread.
"""

from __future__ import annotations

import io
import re
import threading
from collections import OrderedDict
from dataclasses import dataclass

__all__ = [
    "Row",
    "DEFAULT_POINT_SIZE",
    "to_latex",
    "to_plain",
    "is_renderable",
    "equation_latex",
    "rows",
    "latex_to_png",
    "cached_png",
    "render_bytes",
    "pixmap",
    "to_pixmap",
    "clear_cache",
    "cache_size",
]

#: Body size for typeset mathematics, in points.
DEFAULT_POINT_SIZE = 15.0

#: Base resolution before the device-pixel-ratio multiplier.
_BASE_DPI = 110.0

#: Whitespace around a rendered equation at `DEFAULT_POINT_SIZE`, and scaled
#: with the point size from there.
#:
#: Fixed padding was the first version and it made the bitmap only *nearly*
#: proportional to the size asked for: at 15 pt it is about 40% of the image
#: height, so an equation rendered at twice the size came out 1.55x taller
#: rather than 2x, and the maths drifted relative to the prose as a reader
#: raised their text scale. Padding is part of the typography, so it grows
#: with the type.
_PAD_INCHES = 0.08

#: Computer Modern: the typeface mathematics is normally set in, and in
#: measurement also the fastest and most compact of matplotlib's four sets.
_FONTSET = "cm"

#: Expressions beyond this many characters are shown as text. Mathtext will
#: happily typeset them, but the result is an unreadable ribbon several times
#: wider than the window, and the fallback at least wraps.
_MAX_LATEX = 600

#: The constructs mathtext cannot render. All of them are LaTeX *environments*,
#: which its parser has no concept of.
_ENVIRONMENT = re.compile(r"\\begin\{|\\end\{|\\substack|\\middle")

#: Commands mathtext lacks that sympy never emits, and so only hand-written
#: LaTeX can contain. They matter because the failure is silent in the worst
#: way: the label falls back to plain text and prints the backslashes, which
#: looks like a typo in the content rather than a limit of the renderer.
#: ``\ge`` is here and ``\geq`` is not -- mathtext accepts only the long form,
#: which is the one sympy prints.
_UNSUPPORTED = re.compile(
    r"\\tfrac|\\dbinom|\\underbrace|\\overbrace|\\iff|\\implies"
    r"|\\ge(?![q])|\\le(?![qf])|\\[Bb]ig[lrm]?(?![a-z])"
)


@dataclass(frozen=True)
class Row:
    """One typesettable line: the expression, and what it is qualified by.

    `condition` carries the ``otherwise``/``for x < 1`` half of a `Piecewise`
    branch, or a matrix entry's position. It is plain text, not LaTeX, because
    it is set as an ordinary label beside the mathematics.
    """

    latex: str
    plain: str
    condition: str = ""


def to_latex(expr) -> str:
    """LaTeX for `expr`, which may already be a string."""
    if isinstance(expr, str):
        return expr
    import sympy as sp

    return sp.latex(expr)


def to_plain(expr) -> str:
    """The monospace form, used whenever typesetting is unavailable."""
    if isinstance(expr, str):
        return expr
    return str(expr)


def is_renderable(latex: str) -> bool:
    """Whether mathtext can be expected to typeset `latex`.

    A guard rather than a try/except: the failure would otherwise surface deep
    inside a worker thread, one render at a time, with no way to choose a
    better presentation.
    """
    if not latex or not latex.strip():
        return False
    if len(latex) > _MAX_LATEX:
        return False
    return (_ENVIRONMENT.search(latex) is None
            and _UNSUPPORTED.search(latex) is None)


#: ``y'``, ``y''``, ``y^(4)``: a derivative as a question writes it.
_DERIVATIVE = re.compile(r"\b([A-Za-z])('+|\^\((\d+)\))")


def equation_latex(equation: str, conditions: str = "") -> str | None:
    """A question's equation as typeset mathematics, in prime notation.

    Practice and the quiz showed a Solve question's equation as the code it is
    stored as -- ``y' = 2*t*y`` in a monospace font -- directly beside choice
    questions whose equations were typeset, so one page used two notations
    for the same thing. This reads the stored text rather than the parsed
    equation, because sympy would print the parsed one as
    ``\\frac{d}{dt} y{\\left(t \\right)}`` where a course writes ``y'``, and
    would reorder its terms. The terms are kept in the order they were written.

    `equation` may hold several, separated by ``;``. None if any part cannot be
    read, and the caller keeps the code: a plain equation beats a broken one.
    """
    import sympy as sp
    from sympy.parsing.sympy_parser import (
        convert_xor,
        parse_expr,
        standard_transformations,
    )

    from .custom import reject_unsafe_syntax

    names: dict = {}

    def derivative(match) -> str:
        name, primes, order = match.group(1), match.group(2), match.group(3)
        n = int(order) if order else len(primes)
        key = f"D{n}_{name}"
        names[sp.Symbol(key)] = name + ("'" * n if n <= 3 else f"^{{({n})}}")
        return key

    transformations = standard_transformations + (convert_xor,)
    local = {"Heaviside": sp.Function("u"), "DiracDelta": sp.Function("delta")}

    def drop_ones(expr):
        # Parsed unevaluated, 1/(1 + e^t) is Mul(1, Pow(1 + e^t, -1)), which
        # prints as "1 \frac{1}{1 + e^t}". Evaluating would fix that and also
        # rewrite what the question wrote: -0.2*(y - 20) becomes 4 - 0.2y.
        if expr.is_Atom:
            return expr
        args = [drop_ones(arg) for arg in expr.args]
        if isinstance(expr, sp.Mul):
            # Flattened, so the -1 of -y/t, parsed as (-1*y)*(1/t), comes first.
            args = [factor for arg in args
                    for factor in (arg.args if isinstance(arg, sp.Mul) else (arg,))]
            args = [arg for arg in args if arg != 1] or [sp.Integer(1)]
            return args[0] if len(args) == 1 else sp.Mul(*args, evaluate=False)
        if isinstance(expr, (sp.Add, sp.Pow)):
            return expr.func(*args, evaluate=False)
        return expr.func(*args)

    def term_latex(term) -> tuple[str, str]:
        """(sign, body): -y/t is Mul(-1, y, 1/t), which prints "(-1) y/t"."""
        if isinstance(term, sp.Mul) and term.args and term.args[0] == -1:
            rest = term.args[1:]
            body = rest[0] if len(rest) == 1 else sp.Mul(*rest, evaluate=False)
            return "-", sp.latex(body, order="none", symbol_names=names)
        piece = sp.latex(term, order="none", symbol_names=names)
        if piece.startswith("-"):
            return "-", piece[1:].lstrip()
        return "+", piece

    def side_latex(text: str) -> str:
        whole = drop_ones(parse_expr(text, local_dict=local, evaluate=False,
                                     transformations=transformations))
        terms = whole.args if isinstance(whole, sp.Add) else (whole,)
        out = ""
        for term in terms:
            sign, body = term_latex(term)
            if not out:
                out = body if sign == "+" else "-" + body
            else:
                out += f" {sign} {body}"
        return out

    # A which-portrait question about a nonlinear system names the point it
    # asks about: "x' = y; y' = -sin(x)     at (x, y) = (pi, 0)".
    where = ""
    if re.search(r"\s{2,}at\s", equation):
        equation, where = re.split(r"\s{2,}at\s+", equation, maxsplit=1)
        if not re.fullmatch(r"[\w\s(),.\-+=/*]+", where):
            return None
        where = re.sub(r"\bpi\b", r"\\pi", where.replace("*", ""))

    parts = []
    try:
        for text in (part for part in equation.split(";") if part.strip()):
            body = _DERIVATIVE.sub(derivative, text)
            reject_unsafe_syntax(body.replace("=", "+"))
            parts.append(" = ".join(side_latex(side) for side in body.split("=")))
    except Exception:
        return None
    latex = r",\quad ".join(parts)
    if conditions.strip():
        given = [c.strip().replace("*", "") for c in conditions.split(",") if c.strip()]
        latex += r",\qquad " + r",\quad ".join(given)
    if where:
        latex += r"\qquad \mathrm{at}\ " + where.strip()
    return latex if is_renderable(latex) else None


def rows(expr) -> list[Row]:
    """Split `expr` into individually typesettable rows.

    Scalar expressions give a single row. `Piecewise` gives one row per branch
    with its condition alongside, and a matrix or a list one row per entry --
    both of which would otherwise need a LaTeX environment and fail outright.
    """
    import sympy as sp

    if isinstance(expr, str):
        return [Row(expr, expr)]

    if isinstance(expr, sp.Piecewise):
        out = []
        for value, condition in expr.args:
            label = "otherwise" if condition is sp.true else f"for {condition}"
            out.append(Row(sp.latex(value), str(value), label))
        return out

    if isinstance(expr, sp.MatrixBase):
        out = []
        for i in range(expr.rows):
            for j in range(expr.cols):
                entry = expr[i, j]
                label = f"row {i + 1}" if expr.cols == 1 else f"({i + 1},{j + 1})"
                out.append(Row(sp.latex(entry), str(entry), label))
        return out

    if isinstance(expr, (list, tuple)):
        return [Row(sp.latex(item), str(item)) for item in expr]

    return [Row(sp.latex(expr), str(expr))]


#: Rendered images, keyed by everything that affects the pixels. A plain
#: bounded dict rather than `functools.lru_cache`, because callers need to ask
#: *whether* something is cached without rendering it if it is not: a widget
#: paints a cached image immediately and defers a miss to a worker thread, and
#: with `lru_cache` there is no way to tell the two cases apart.
_CACHE: OrderedDict[tuple, bytes] = OrderedDict()
_CACHE_LIMIT = 512
_CACHE_LOCK = threading.Lock()


def cached_png(latex: str, colour: str, point_size: float, dpi: float) -> bytes | None:
    """The cached image for these arguments, or ``None`` if there is none.

    Never renders. ``b""`` is a real answer -- it means "known to be
    untypesettable" -- and is distinct from ``None``.
    """
    key = (latex, colour, float(point_size), float(dpi))
    with _CACHE_LOCK:
        if key not in _CACHE:
            return None
        _CACHE.move_to_end(key)
        return _CACHE[key]


def latex_to_png(latex: str, colour: str, point_size: float, dpi: float) -> bytes:
    """Typeset `latex` and return PNG bytes, or ``b""`` if it cannot be.

    The background is transparent and the colour is baked in, so one image
    composites correctly onto a card, a panel or a plot alike -- but it also
    means the colour has to be part of the cache key, or a theme switch would
    serve the previous palette's glyphs.
    """
    key = (latex, colour, float(point_size), float(dpi))
    hit = cached_png(*key)
    if hit is not None:
        return hit

    data = _render(latex, colour, point_size, dpi)
    with _CACHE_LOCK:
        _CACHE[key] = data
        _CACHE.move_to_end(key)
        while len(_CACHE) > _CACHE_LIMIT:
            _CACHE.popitem(last=False)
    return data


#: One render at a time. The choices below keep renders from racing over
#: pyplot and rcParams, but mathtext's own font handling is shared state too:
#: a Linux CI worker segfaulted with three threads inside it at once, two in
#: `savefig` and one in `_mathtext._get_font` (Ubuntu, Python 3.13,
#: 2026-10-11). A warm render takes 8 ms and the GIL serialises most of the
#: work anyway, so the lock gives up almost nothing concurrency was buying.
_RENDER_LOCK = threading.Lock()


def _render(latex: str, colour: str, point_size: float, dpi: float) -> bytes:
    """The actual typesetting. Serialised; no Qt, no pyplot, no caching."""
    if not is_renderable(latex):
        return b""
    with _RENDER_LOCK:
        return _render_unlocked(latex, colour, point_size, dpi)


def _render_unlocked(latex: str, colour: str, point_size: float,
                     dpi: float) -> bytes:
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    # Two deliberate choices, both about shared state:
    #
    # * A bare `Figure`, never pyplot -- pyplot keeps a global registry of
    #   figures, which several threads cannot safely mutate at once.
    # * `math_fontfamily` on the artist, never `rc_context` -- the latter
    #   swaps the *global* rcParams and restores them on exit, so two
    #   concurrent renders would race and one could reset the font under the
    #   other. Per-artist, there is no shared state left to race over.
    figure = Figure(figsize=(0.01, 0.01), dpi=dpi)
    FigureCanvasAgg(figure)
    try:
        figure.text(0, 0, f"${latex}$", fontsize=point_size, color=colour,
                    math_fontfamily=_FONTSET)
        buffer = io.BytesIO()
        figure.savefig(
            buffer, format="png", bbox_inches="tight",
            pad_inches=_PAD_INCHES * point_size / DEFAULT_POINT_SIZE,
            transparent=True,
        )
    except Exception:
        # A construct the guard did not anticipate. The caller falls back to
        # text; an unreadable equation is much better than a broken screen.
        return b""
    return buffer.getvalue()


def clear_cache() -> None:
    """Drop every cached image. For tests, and for a font-setting change."""
    with _CACHE_LOCK:
        _CACHE.clear()


def cache_size() -> int:
    """How many images are currently held."""
    with _CACHE_LOCK:
        return len(_CACHE)


def pixmap(latex: str, colour: str, point_size: float = DEFAULT_POINT_SIZE,
           device_pixel_ratio: float = 1.0, *, cached_only: bool = False):
    """A `QPixmap` of `latex`, or ``None`` if it cannot be typeset.

    Rendered at `device_pixel_ratio` times the nominal resolution and tagged
    with it, so the glyphs are sharp on a high-density display while the layout
    still sees the logical size.

    With `cached_only`, returns ``None`` rather than rendering on a miss --
    which is how a widget distinguishes "paint this now" from "hand it to a
    worker and show text meanwhile".
    """
    ratio = max(1.0, float(device_pixel_ratio))
    dpi = _BASE_DPI * ratio
    if cached_only:
        data = cached_png(latex, colour, float(point_size), dpi)
        if data is None:
            return None
    else:
        data = latex_to_png(latex, colour, float(point_size), dpi)
    return to_pixmap(data, ratio)


def warm_up() -> None:
    """Typeset one throwaway symbol, so the first real equation is not the one
    that pays for loading matplotlib's mathtext and its fonts.

    Called off the GUI thread at launch, while the reader is still looking at
    the first screen. Measured opening a lesson three seconds after launch,
    two runs each: the last of its 30 equations landed at 2.2-2.4 s without
    this and 1.8 s with it. A render costs 8 ms once warm.
    """
    latex_to_png("x", "#000000", DEFAULT_POINT_SIZE, _BASE_DPI)


def render_bytes(latex: str, colour: str, point_size: float,
                 device_pixel_ratio: float = 1.0) -> bytes:
    """PNG bytes at the resolution `pixmap` would use. Safe off the GUI thread.

    The Qt-free half of `pixmap`, for workers: they produce the bytes, the GUI
    thread turns them into a `QPixmap` with `to_pixmap`.
    """
    ratio = max(1.0, float(device_pixel_ratio))
    return latex_to_png(latex, colour, float(point_size), _BASE_DPI * ratio)


def to_pixmap(data: bytes, device_pixel_ratio: float = 1.0):
    """Wrap PNG bytes as a `QPixmap`. Must be called on the GUI thread."""
    if not data:
        return None
    from PySide6.QtGui import QPixmap

    image = QPixmap()
    if not image.loadFromData(data, "PNG"):
        return None
    image.setDevicePixelRatio(max(1.0, float(device_pixel_ratio)))
    return image
