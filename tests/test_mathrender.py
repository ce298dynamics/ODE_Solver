"""Typesetting: the render core, the cache, and the widgets.

Runs headlessly through the offscreen platform set up in `conftest.py`.

The tests worth reading are the ones about *environments*. Matplotlib's
mathtext implements a large subset of LaTeX but has no notion of
``\\begin{...}``, and `dsolve` returns `Piecewise` and `Matrix` results that
sympy prints using exactly that. The guard and the row decomposition exist for
that single incompatibility, so they are pinned here from both directions: the
environment form must be refused, and the decomposed rows must all render.
"""

from __future__ import annotations

import time

import pytest
import sympy as sp

from odesuite_app import mathrender

T = sp.Symbol("t", real=True)
C1, C2 = sp.symbols("C1 C2")
INK = "#E6EDF3"


@pytest.fixture(autouse=True)
def _fresh_cache():
    mathrender.clear_cache()
    yield
    mathrender.clear_cache()


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


def _png(latex: str, colour: str = INK, pt: float = 15.0, dpi: float = 110.0) -> bytes:
    return mathrender.latex_to_png(latex, colour, pt, dpi)


# -- the render core -----------------------------------------------------

#: One representative of every construct the symbolic engine actually emits.
EXPRESSIONS = {
    "damped oscillator": sp.exp(-T) * (sp.cos(2 * T) + sp.sin(2 * T) / 2),
    "repeated root": (1 + 2 * T) * sp.exp(-T),
    "resonance": T * sp.sin(T) / 2,
    "general solution": C1 * sp.exp(-T) + C2 * T * sp.exp(-T),
    "Cauchy-Euler": T / 2 + 1 / (2 * T),
    "Airy": C1 * sp.airyai(T) + C2 * sp.airybi(T),
    "Bessel": C1 * sp.besselj(0, T) + C2 * sp.bessely(0, T),
    "error function": sp.sqrt(sp.pi) * sp.erf(T) / 2,
    "complex exponent": sp.exp((-1 + 2 * sp.I) * T),
    "derivative": sp.Derivative(sp.Function("y")(T), T, 2),
    "characteristic": sp.Eq(sp.Symbol("r") ** 3 + sp.Symbol("r") ** 2 - 1, 0),
}


@pytest.mark.parametrize("name", sorted(EXPRESSIONS))
def test_every_expression_the_engine_emits_is_typeset(name):
    data = _png(sp.latex(EXPRESSIONS[name]))
    assert data.startswith(b"\x89PNG"), f"{name} did not render"
    assert len(data) > 200, f"{name} rendered suspiciously small"


def test_the_symbolic_examples_all_render():
    """Every closed form the engine ships as an example must typeset."""
    from odesuite_app.custom import ParseError
    from odesuite_app.symbolic import EXAMPLES, parse_equation

    checked = 0
    for spec in EXAMPLES.values():
        try:
            parsed = parse_equation(spec)
        except ParseError:
            continue
        latex = sp.latex(parsed.equation)
        assert mathrender.is_renderable(latex)
        assert _png(latex).startswith(b"\x89PNG")
        checked += 1
    assert checked >= 8, "expected the example set to be substantial"


# -- the one real gap: LaTeX environments --------------------------------

def test_piecewise_is_refused_rather_than_raising():
    latex = sp.latex(sp.Piecewise((T, T < 1), (1, True)))
    assert "\\begin{cases}" in latex
    assert not mathrender.is_renderable(latex)
    assert _png(latex) == b""


def test_matrix_is_refused_rather_than_raising():
    latex = sp.latex(sp.Matrix([[0, 1], [-2, -3]]))
    assert not mathrender.is_renderable(latex)
    assert _png(latex) == b""


def test_piecewise_decomposes_into_renderable_rows():
    """The refusal above is only acceptable because this works."""
    rows = mathrender.rows(sp.Piecewise((T, T < 1), (sp.exp(-T), True)))
    assert len(rows) == 2
    assert rows[0].condition == "for t < 1"
    assert rows[1].condition == "otherwise"
    for row in rows:
        assert mathrender.is_renderable(row.latex)
        assert _png(row.latex).startswith(b"\x89PNG")


def test_matrix_decomposes_into_renderable_rows():
    rows = mathrender.rows(sp.Matrix([[T, 1], [0, sp.exp(T)]]))
    assert len(rows) == 4
    assert [r.condition for r in rows] == ["(1,1)", "(1,2)", "(2,1)", "(2,2)"]
    assert all(_png(r.latex).startswith(b"\x89PNG") for r in rows)


def test_a_list_of_solutions_becomes_one_row_each():
    rows = mathrender.rows([sp.exp(4 * T), sp.exp(-T)])
    assert len(rows) == 2
    assert all(mathrender.is_renderable(r.latex) for r in rows)


def test_scalar_expression_is_a_single_row():
    rows = mathrender.rows(T * sp.sin(T) / 2)
    assert len(rows) == 1 and not rows[0].condition


def test_absurdly_long_expressions_fall_back_instead_of_rendering():
    """A ribbon of mathematics wider than the screen is worse than text."""
    assert not mathrender.is_renderable("x + " * 400 + "1")


def test_empty_input_is_not_renderable():
    assert not mathrender.is_renderable("")
    assert not mathrender.is_renderable("   ")


def test_unanticipated_failure_returns_empty_not_an_exception():
    """The guard cannot know every construct; the renderer must still not raise."""
    assert _png(r"\frac{\unknownmacro{x}}{2}") == b""


# -- the cache -----------------------------------------------------------

def test_second_render_is_identical_and_free():
    latex = sp.latex(EXPRESSIONS["damped oscillator"])

    started = time.perf_counter()
    first = _png(latex)
    cold = time.perf_counter() - started

    started = time.perf_counter()
    second = _png(latex)
    warm = time.perf_counter() - started

    assert first == second
    assert warm < cold
    assert warm < 0.002, "a cache hit should not be doing any work"


def test_colour_is_part_of_the_key():
    """Otherwise a theme switch would serve the previous palette's glyphs."""
    latex = sp.latex(T ** 2)
    dark = _png(latex, "#E6EDF3")
    light = _png(latex, "#1F2328")
    assert dark != light
    assert mathrender.cache_size() == 2


def test_point_size_and_dpi_are_part_of_the_key():
    latex = sp.latex(T ** 2)
    assert _png(latex, INK, 15.0, 110.0) != _png(latex, INK, 22.0, 110.0)
    assert _png(latex, INK, 15.0, 110.0) != _png(latex, INK, 15.0, 220.0)


def test_cached_png_reports_a_miss_without_rendering():
    """The distinction the widget's non-blocking path is built on."""
    latex = sp.latex(sp.exp(T))
    assert mathrender.cached_png(latex, INK, 15.0, 110.0) is None
    assert mathrender.cache_size() == 0

    _png(latex)
    assert mathrender.cached_png(latex, INK, 15.0, 110.0) is not None


def test_untypesettable_input_is_cached_as_a_known_negative():
    """``b""`` means "known bad"; ``None`` means "not tried". They differ."""
    latex = sp.latex(sp.Matrix([[1, 0], [0, 1]]))
    assert _png(latex) == b""
    assert mathrender.cached_png(latex, INK, 15.0, 110.0) == b""


def test_cache_is_bounded():
    for index in range(mathrender._CACHE_LIMIT + 40):
        _png(f"x_{{{index}}}")
    assert mathrender.cache_size() <= mathrender._CACHE_LIMIT


def test_rendering_is_thread_safe():
    """No pyplot and no rc_context, so concurrent renders cannot corrupt one another."""
    from concurrent.futures import ThreadPoolExecutor

    latexes = [sp.latex(expr) for expr in EXPRESSIONS.values()]
    expected = {tex: _png(tex) for tex in latexes}
    mathrender.clear_cache()

    with ThreadPoolExecutor(4) as pool:
        results = list(pool.map(_png, latexes * 3))

    assert all(results)
    for tex, data in zip(latexes * 3, results):
        assert data == expected[tex]


def test_rendering_leaves_global_matplotlib_settings_alone():
    """Regression: `rc_context` swaps global rcParams, which threads race over.

    The font is selected per artist instead. If this ever reverts to
    `rc_context`, concurrent renders can reset the font under one another --
    a race that would show up as an occasional wrongly-typeset equation, which
    is exactly the kind of failure nobody reproduces.
    """
    import matplotlib

    before = dict(matplotlib.rcParams)
    _png(sp.latex(EXPRESSIONS["Airy"]))
    for key in ("mathtext.fontset", "mathtext.default", "font.size"):
        assert matplotlib.rcParams[key] == before[key]


def test_the_computer_modern_face_is_actually_used():
    """Otherwise the font choice is silently ignored and nothing looks wrong."""
    import matplotlib

    assert matplotlib.rcParams["mathtext.fontset"] != mathrender._FONTSET, (
        "test is vacuous unless the chosen face differs from the global default"
    )
    latex = sp.latex(EXPRESSIONS["general solution"])
    ours = _png(latex)

    import io as _io

    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    figure = Figure(figsize=(0.01, 0.01), dpi=110.0)
    FigureCanvasAgg(figure)
    figure.text(0, 0, f"${latex}$", fontsize=15.0, color=INK)   # global default
    buffer = _io.BytesIO()
    figure.savefig(buffer, format="png", bbox_inches="tight",
                   pad_inches=0.08, transparent=True)
    assert ours != buffer.getvalue()


# -- pixmaps and device pixel ratio --------------------------------------

def test_pixmap_is_produced_and_tagged(qapp):
    image = mathrender.pixmap(sp.latex(T ** 2), INK)
    assert image is not None and not image.isNull()
    assert image.hasAlphaChannel(), "must composite onto any surface"


def test_high_dpi_adds_pixels_without_changing_logical_size(qapp):
    latex = sp.latex(sp.exp(-T) * sp.cos(2 * T))
    normal = mathrender.pixmap(latex, INK, 15.0, 1.0)
    retina = mathrender.pixmap(latex, INK, 15.0, 2.0)

    assert retina.width() > normal.width()          # more real pixels
    logical_normal = normal.width() / normal.devicePixelRatio()
    logical_retina = retina.width() / retina.devicePixelRatio()
    assert logical_retina == pytest.approx(logical_normal, rel=0.05)


def test_cached_only_returns_nothing_on_a_miss(qapp):
    latex = sp.latex(sp.sin(T) ** 2)
    assert mathrender.pixmap(latex, INK, cached_only=True) is None
    mathrender.pixmap(latex, INK)
    assert mathrender.pixmap(latex, INK, cached_only=True) is not None


def test_pixmap_of_an_environment_is_none(qapp):
    assert mathrender.pixmap(sp.latex(sp.Matrix([[1, 2]])), INK) is None


# -- widgets -------------------------------------------------------------

def _settle(qapp, label, timeout: float = 20.0) -> None:
    """Wait for any background render to land."""
    from PySide6.QtCore import QThreadPool

    deadline = time.perf_counter() + timeout
    while time.perf_counter() < deadline:
        qapp.processEvents()
        if label.is_typeset:
            return
        QThreadPool.globalInstance().waitForDone(50)
    qapp.processEvents()


def test_mathlabel_typesets_an_expression(qapp):
    from odesuite_app.theme import DARK
    from odesuite_app.widgets.mathlabel import MathLabel

    label = MathLabel(DARK, EXPRESSIONS["damped oscillator"])
    _settle(qapp, label)
    assert label.is_typeset


def test_mathlabel_falls_back_to_text_and_does_not_raise(qapp):
    """A Piecewise handed straight to a label must still show something."""
    from odesuite_app.theme import DARK
    from odesuite_app.widgets.mathlabel import MathLabel

    label = MathLabel(DARK, sp.Piecewise((T, T < 1), (1, True)))
    qapp.processEvents()
    assert not label.is_typeset
    assert "Piecewise" in label.findChild(type(label._label)).text()


def test_mathlabel_retyping_discards_the_stale_render(qapp):
    from odesuite_app.theme import DARK
    from odesuite_app.widgets.mathlabel import MathLabel

    label = MathLabel(DARK, sp.exp(T))
    for power in range(2, 8):
        label.set_expression(T ** power)          # supersede repeatedly
    _settle(qapp, label)
    assert label.latex == sp.latex(T ** 7)
    assert label.is_typeset


def test_mathlabel_retypesets_for_a_new_theme(qapp):
    from odesuite_app.theme import DARK, LIGHT
    from odesuite_app.widgets.mathlabel import MathLabel

    label = MathLabel(DARK, T ** 2)
    _settle(qapp, label)
    before = mathrender.cache_size()

    label.set_palette_colours(LIGHT)
    _settle(qapp, label)
    assert label.colour == LIGHT.text
    assert mathrender.cache_size() > before, "the light glyphs are a new image"


def test_mathblock_stacks_one_row_per_branch(qapp):
    from odesuite_app.theme import DARK
    from odesuite_app.widgets.mathlabel import MathBlock

    block = MathBlock(DARK, sp.Piecewise((T, T < 1), (sp.exp(-T), True)),
                      lead="y(t) =")
    for label in block._rows:
        _settle(qapp, label)
    assert len(block._rows) == 2
    assert all(label.is_typeset for label in block._rows)


def test_math_widgets_do_not_paint_their_own_backdrop(qapp):
    """Regression: the generic ``QWidget`` style rule.

    Without an explicit transparent background these widgets paint the window
    colour, punching a rectangle of backdrop through the card the equation is
    sitting on -- the same trap the theme's ``QLabel`` rule already guards.
    """
    from PySide6.QtCore import Qt

    from odesuite_app.theme import DARK
    from odesuite_app.widgets.mathlabel import MathBlock, MathLabel

    label = MathLabel(DARK, T ** 2)
    block = MathBlock(DARK, T ** 2)
    for widget in (label, block):
        assert widget.testAttribute(Qt.WA_TranslucentBackground)
        assert "transparent" in widget.styleSheet()


def test_the_lead_in_is_wide_enough_for_its_text(qapp):
    """Regression: measured from raw font metrics it came out clipped."""
    from PySide6.QtWidgets import QLabel

    from odesuite_app.theme import DARK
    from odesuite_app.widgets.mathlabel import MathBlock

    lead_text = "y(t) ="
    block = MathBlock(DARK, [sp.exp(-T), sp.exp(T)], lead=lead_text)
    line = block._rows[0].parentWidget()
    leads = [w for w in line.findChildren(QLabel) if w.text() == lead_text]
    assert leads, "the first row should carry the lead-in"
    assert leads[0].width() >= leads[0].sizeHint().width()


def test_typeset_rows_reserve_their_full_height(qapp):
    """Regression: word wrap left on for a pixmap clipped equations."""
    from odesuite_app.theme import DARK
    from odesuite_app.widgets.mathlabel import MathLabel

    label = MathLabel(DARK, sp.exp(-T) * (sp.cos(2 * T) + sp.sin(2 * T) / 2))
    _settle(qapp, label)
    image = label._label.pixmap()
    logical = image.height() / image.devicePixelRatio()
    assert not label._label.wordWrap()
    assert label._label.minimumHeight() >= logical - 1


def test_mathblock_rebuild_removes_the_previous_rows(qapp):
    from odesuite_app.theme import DARK
    from odesuite_app.widgets.mathlabel import MathBlock

    block = MathBlock(DARK, [T, T ** 2, T ** 3])
    assert len(block._rows) == 3
    block.set_expression(sp.exp(T))
    qapp.processEvents()
    assert len(block._rows) == 1


def test_mathblock_handles_a_system(qapp):
    from odesuite_app.theme import DARK
    from odesuite_app.widgets.mathlabel import MathBlock

    block = MathBlock(DARK, [2 * sp.exp(4 * T) / 5, 3 * sp.exp(-T) / 5])
    for label in block._rows:
        _settle(qapp, label)
    assert all(label.is_typeset for label in block._rows)


def test_copying_latex_and_python_put_different_text_on_the_clipboard(qapp):
    from PySide6.QtGui import QGuiApplication

    from odesuite_app.theme import DARK
    from odesuite_app.widgets.mathlabel import MathLabel, _copy

    label = MathLabel(DARK, sp.exp(-T) / 2)
    _copy(label.latex)
    assert QGuiApplication.clipboard().text() == sp.latex(sp.exp(-T) / 2)
    _copy(label._plain)
    assert QGuiApplication.clipboard().text() == str(sp.exp(-T) / 2)
