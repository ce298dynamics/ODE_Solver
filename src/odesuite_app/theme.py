"""Colour palettes and Qt styling.

One place decides what the application looks like. Screens ask for semantic
colours -- ``accent``, ``surface``, ``danger`` -- rather than hex values, so a
palette swap needs no changes anywhere else.

The series palette is chosen for categorical distinguishability under both
themes and is safe for the common forms of colour vision deficiency: no
red/green pair carries meaning on its own, and the entries differ in lightness
as well as hue so they remain separable in greyscale.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

__all__ = [
    "Palette",
    "DARK",
    "LIGHT",
    "PALETTES",
    "BASELINE_POINT_SIZE",
    "text_scale",
    "scaled",
    "stylesheet",
    "apply_theme",
]


@dataclass(frozen=True)
class Palette:
    name: str
    background: str      # window backdrop
    surface: str         # panels, cards
    surface_alt: str     # hover / raised
    border: str
    text: str
    text_muted: str
    accent: str          # primary interactive colour
    accent_soft: str
    success: str
    warning: str
    danger: str
    grid: str
    plot_background: str
    series: tuple[str, ...] = field(default=())

    @property
    def is_dark(self) -> bool:
        return self.name == "dark"


#: Categorical series colours. Hue-spaced and lightness-varied, so they stay
#: distinguishable in greyscale and under deuteranopia.
_SERIES = (
    "#4C9BE8",   # blue
    "#F0883E",   # orange
    "#3FB950",   # green
    "#D2A8FF",   # violet
    "#E5C07B",   # sand
    "#56D4DD",   # cyan
    "#FF7B92",   # rose
    "#A5D6A7",   # pale green
)

DARK = Palette(
    name="dark",
    background="#0D1117",
    surface="#161B22",
    surface_alt="#21262D",
    border="#30363D",
    text="#E6EDF3",
    text_muted="#8B949E",
    accent="#4C9BE8",
    accent_soft="#1F3A5F",
    success="#3FB950",
    warning="#D29922",
    danger="#F85149",
    grid="#21262D",
    plot_background="#0D1117",
    series=_SERIES,
)

LIGHT = Palette(
    name="light",
    background="#FFFFFF",
    surface="#F6F8FA",
    surface_alt="#EAEEF2",
    border="#D0D7DE",
    text="#1F2328",
    text_muted="#636C76",
    accent="#0969DA",
    accent_soft="#DDF4FF",
    success="#1A7F37",
    warning="#9A6700",
    danger="#CF222E",
    grid="#E4E8EC",
    plot_background="#FFFFFF",
    series=(
        "#0969DA", "#BC4C00", "#1A7F37", "#8250DF",
        "#9A6700", "#1B7C83", "#CF222E", "#4C8B5B",
    ),
)

PALETTES = {"dark": DARK, "light": LIGHT}


#: The point size Qt reports for the default application font on a display at
#: 100% text scale. Every ``font-size`` written anywhere in this application is
#: a pixel count chosen against *that* font, so this is the number they are all
#: implicitly relative to -- and dividing by it is what turns the font Qt is
#: actually handing us into a factor everything else can be multiplied by.
BASELINE_POINT_SIZE = 9.0

#: How far the scale is allowed to move. The lower bound stops a machine
#: reporting an unexpectedly small default font from shrinking the whole
#: application into illegibility; the upper bound is where Windows' own text
#: scale stops.
_SCALE_RANGE = (0.85, 3.0)

#: A ``font-size`` in a style sheet or in an inline HTML ``style`` attribute.
#: Both forms are matched by one pattern because both are what this
#: application writes, and a reader raising their text scale does not care
#: which of the two a given caption happened to use.
_FONT_SIZE = re.compile(r"(font-size\s*:\s*)([0-9]*\.?[0-9]+)\s*px")


def text_scale(app=None) -> float:
    """How much larger the operating system wants text than we assume.

    Windows' "Make text bigger" -- and the equivalent on the other two
    platforms -- raises the *point size* of the default application font
    without touching the device pixel ratio. Qt therefore reports it here and
    nowhere else, and a style sheet written in pixels ignores it completely,
    which is precisely the bug this exists to fix.

    Returns 1.0 with no application running, so anything that renders
    headlessly -- the tests, the thumbnail generator -- gets the sizes it was
    written against.
    """
    if app is None:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
    if app is None:
        return 1.0
    size = float(app.font().pointSizeF())
    if size <= 0:
        return 1.0
    low, high = _SCALE_RANGE
    return min(high, max(low, size / BASELINE_POINT_SIZE))


def scaled(css: str, scale: float | None = None) -> str:
    """`css` with every pixel font size multiplied by the text scale.

    Applied to the whole application style sheet and to each of the inline
    ones, because a reader who has asked for larger text wants *all* of it
    larger: body and caption growing at different rates would be worse than
    neither growing at all.

    Only ``font-size`` is touched. Padding, borders and widths are device
    pixels and are already handled by Qt's own high-DPI scaling; multiplying
    them here as well would double-count it.
    """
    if scale is None:
        scale = text_scale()
    if abs(scale - 1.0) < 0.005:
        return css
    return _FONT_SIZE.sub(
        lambda found: f"{found.group(1)}{float(found.group(2)) * scale:.1f}px",
        css,
    )


def stylesheet(palette: Palette, scale: float | None = None) -> str:
    """Qt style sheet for the whole application."""
    p = palette
    return scaled(f"""
    QWidget {{
        background: {p.background};
        color: {p.text};
        font-family: "Segoe UI", "Inter", system-ui, sans-serif;
        font-size: 13px;
    }}
    /* Labels must not paint their own backdrop, or every caption inside a
       card punches a rectangle of window colour through the card surface. */
    QLabel {{ background: transparent; }}
    QLabel[role="title"] {{ font-size: 26px; font-weight: 600; }}
    QLabel[role="subtitle"] {{ font-size: 14px; color: {p.text_muted}; }}
    QLabel[role="heading"] {{ font-size: 15px; font-weight: 600; }}
    QLabel[role="muted"] {{ color: {p.text_muted}; }}
    QLabel[role="mono"] {{
        font-family: "Cascadia Mono", "Consolas", monospace;
        font-size: 12px;
    }}

    QFrame[role="panel"] {{
        background: {p.surface};
        border: 1px solid {p.border};
        border-radius: 10px;
    }}
    QFrame[role="card"] {{
        background: {p.surface};
        border: 1px solid {p.border};
        border-radius: 12px;
    }}
    QFrame[role="card"]:hover {{
        background: {p.surface_alt};
        border: 1px solid {p.accent};
    }}
    QFrame[role="separator"] {{ background: {p.border}; border: none; }}

    QPushButton {{
        background: {p.surface_alt};
        border: 1px solid {p.border};
        border-radius: 7px;
        padding: 7px 14px;
    }}
    QPushButton:hover {{ border-color: {p.accent}; }}
    QPushButton:pressed {{ background: {p.accent_soft}; }}
    QPushButton:disabled {{ color: {p.text_muted}; border-color: {p.border}; }}
    QPushButton[role="primary"] {{
        background: {p.accent};
        border: 1px solid {p.accent};
        color: {"#0D1117" if p.is_dark else "#FFFFFF"};
        font-weight: 600;
    }}
    QPushButton[role="primary"]:hover {{ background: {p.accent}; }}
    QPushButton[role="nav"] {{
        background: transparent;
        border: none;
        border-radius: 7px;
        padding: 9px 12px;
        text-align: left;
        color: {p.text_muted};
    }}
    QPushButton[role="nav"]:hover {{ background: {p.surface_alt}; color: {p.text}; }}
    QPushButton[role="nav"]:checked {{
        background: {p.accent_soft};
        color: {p.accent};
        font-weight: 600;
    }}
    /* The Learning Hub / Solver Studio switch. Deliberately quieter than a
       nav button when unselected and louder when selected: it is a mode, not a
       destination, and the eye should land on the current section first. */
    QPushButton[role="section"] {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 7px;
        padding: 7px 12px;
        text-align: left;
        color: {p.text_muted};
        font-size: 12px;
    }}
    QPushButton[role="section"]:hover {{ color: {p.text}; }}
    QPushButton[role="section"]:checked {{
        background: {p.surface_alt};
        border-color: {p.border};
        color: {p.text};
        font-weight: 700;
    }}
    QPushButton[role="chip"] {{
        border-radius: 11px;
        padding: 4px 11px;
        color: {p.text_muted};
        font-size: 12px;
    }}
    QPushButton[role="chip"]:checked {{
        background: {p.accent_soft};
        border-color: {p.accent};
        color: {p.accent};
    }}

    QComboBox {{
        background: {p.surface_alt};
        border: 1px solid {p.border};
        border-radius: 7px;
        padding: 6px 10px;
    }}
    QComboBox:hover {{ border-color: {p.accent}; }}
    QComboBox QAbstractItemView {{
        background: {p.surface};
        border: 1px solid {p.border};
        selection-background-color: {p.accent_soft};
        outline: none;
    }}

    QLineEdit, QPlainTextEdit, QTextEdit {{
        background: {p.surface_alt};
        border: 1px solid {p.border};
        border-radius: 7px;
        padding: 6px 9px;
        selection-background-color: {p.accent_soft};
    }}
    QLineEdit:focus, QPlainTextEdit:focus {{ border-color: {p.accent}; }}

    QSlider::groove:horizontal {{
        height: 4px; background: {p.border}; border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {p.accent}; width: 14px; height: 14px;
        margin: -6px 0; border-radius: 7px;
    }}
    QSlider::sub-page:horizontal {{ background: {p.accent}; border-radius: 2px; }}

    QScrollArea {{ border: none; }}
    QScrollBar:vertical {{
        background: transparent; width: 10px; margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {p.border}; border-radius: 5px; min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{ background: {p.text_muted}; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; }}
    QScrollBar::handle:horizontal {{
        background: {p.border}; border-radius: 5px; min-width: 30px;
    }}

    QCheckBox::indicator {{
        width: 15px; height: 15px; border-radius: 4px;
        border: 1px solid {p.border}; background: {p.surface_alt};
    }}
    QCheckBox::indicator:checked {{
        background: {p.accent}; border-color: {p.accent};
    }}
    /* Unstyled, a radio button drew Qt's own dark circle, and on the dark
       palette's cards the options of a multiple-choice question had no
       visible button at all. Muted text, not the border colour, for the ring:
       it is the thing to click, not a divider. */
    QRadioButton::indicator {{
        width: 14px; height: 14px; border-radius: 8px;
        border: 1px solid {p.text_muted}; background: {p.surface_alt};
    }}
    QRadioButton::indicator:hover {{ border-color: {p.accent}; }}
    QRadioButton::indicator:checked {{
        background: {p.accent}; border: 4px solid {p.surface_alt};
        outline: none;
    }}
    QToolTip {{
        background: {p.surface_alt}; color: {p.text};
        border: 1px solid {p.border}; padding: 5px;
    }}
    """, scale)


def apply_theme(app, palette: Palette) -> None:
    """Apply `palette` to the running application and to pyqtgraph."""
    import pyqtgraph as pg

    app.setStyleSheet(stylesheet(palette, text_scale(app)))
    pg.setConfigOption("background", palette.plot_background)
    pg.setConfigOption("foreground", palette.text_muted)
    pg.setConfigOptions(antialias=True)
