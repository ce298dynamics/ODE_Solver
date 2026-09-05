"""The figure registry, and the one function that turns a key into a widget.

Split by unit -- see `base` for why. This module holds the mapping and nothing
else, so adding a figure means one import and one line here.
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from ...theme import Palette
from .base import LessonFigure
from .unit1 import ExactFigure, LinearFigure, SeparableFigure, SlopeFieldFigure
from .unit2 import (
    EulerErrorFigure,
    MotionFigure,
    OrderFigure,
    PhaseLineFigure,
)
from .unit3 import ForcedStructureFigure, PowersFigure
from .unit4 import DampingFigure, ResonanceFigure
from .unit5 import ConvolutionFigure, PolesFigure, PulseResponseFigure
from .unit6 import EigenlinesFigure, SpiralFigure
from .unit7 import PartialSumsFigure

__all__ = ["FIGURES", "LessonFigure", "build_figure"]

FIGURES: dict[str, type[LessonFigure]] = {
    # In course order, which is the order they are met.
    "slope_field": SlopeFieldFigure,
    "separable_family": SeparableFigure,
    "integrating_factor": LinearFigure,
    "level_curves": ExactFigure,
    "phase_line": PhaseLineFigure,
    "terminal_velocity": MotionFigure,
    "euler_error": EulerErrorFigure,
    "order_slope": OrderFigure,
    "forced_structure": ForcedStructureFigure,
    "powers": PowersFigure,
    "damping": DampingFigure,
    "resonance": ResonanceFigure,
    "poles": PolesFigure,
    "convolution": ConvolutionFigure,
    "pulse_response": PulseResponseFigure,
    "eigenlines": EigenlinesFigure,
    "spiral": SpiralFigure,
    "partial_sums": PartialSumsFigure,
}


def build_figure(key: str, palette: Palette, parent=None) -> QWidget | None:
    """The figure named by `key`, or None where there is no such figure.

    None rather than an exception: a lesson naming a figure that does not exist
    is a content bug, caught by the tests, and it should not take the whole
    lesson page down with it in the meantime.
    """
    figure = FIGURES.get(key)
    return None if figure is None else figure(palette, parent)
