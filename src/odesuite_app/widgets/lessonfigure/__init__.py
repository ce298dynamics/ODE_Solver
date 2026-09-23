"""The figure registry, and the one function that turns a key into a widget.

Split by unit -- see `base` for why. This module holds the mapping and nothing
else, so adding a figure means one import and one line here.
"""

from __future__ import annotations

from PySide6.QtWidgets import QWidget

from ...theme import Palette
from .base import LessonFigure
from .unit1 import (
    ExactFigure,
    FamilyFigure,
    LinearFigure,
    SeparableFigure,
    SlopeFieldFigure,
    SubstitutionFigure,
)
from .unit2 import (
    EulerErrorFigure,
    MotionFigure,
    OrderFigure,
    PhaseLineFigure,
    PopulationFigure,
)
from .unit3 import (
    ForcedStructureFigure,
    HigherOrderFigure,
    PowersFigure,
    RootCasesFigure,
    SuperpositionFigure,
    VariationFigure,
)
from .unit4 import CircuitFigure, DampingFigure, ResonanceFigure
from .unit5 import (
    ConvolutionFigure,
    ImpulseLimitFigure,
    PartialFractionFigure,
    PolesFigure,
    PulseResponseFigure,
    TransformFigure,
)
from .unit6 import (
    DefectiveFigure,
    EigenlinesFigure,
    EigenModesFigure,
    ForcedSystemFigure,
    SpiralFigure,
    StatePlaneFigure,
)
from .unit7 import IndicialFigure, PartialSumsFigure, RecurrenceFigure

__all__ = ["FIGURES", "LessonFigure", "build_figure"]

FIGURES: dict[str, type[LessonFigure]] = {
    # In course order, which is the order they are met.
    "solution_family": FamilyFigure,
    "slope_field": SlopeFieldFigure,
    "separable_family": SeparableFigure,
    "integrating_factor": LinearFigure,
    "level_curves": ExactFigure,
    "substitution": SubstitutionFigure,
    "growth_models": PopulationFigure,
    "phase_line": PhaseLineFigure,
    "terminal_velocity": MotionFigure,
    "euler_error": EulerErrorFigure,
    "order_slope": OrderFigure,
    "superposition": SuperpositionFigure,
    "root_cases": RootCasesFigure,
    "forced_structure": ForcedStructureFigure,
    "variation": VariationFigure,
    "powers": PowersFigure,
    "higher_order": HigherOrderFigure,
    "damping": DampingFigure,
    "resonance": ResonanceFigure,
    "circuit_analogue": CircuitFigure,
    "transform_area": TransformFigure,
    "partial_fractions": PartialFractionFigure,
    "poles": PolesFigure,
    "convolution": ConvolutionFigure,
    "pulse_response": PulseResponseFigure,
    "impulse_limit": ImpulseLimitFigure,
    "state_plane": StatePlaneFigure,
    "eigen_modes": EigenModesFigure,
    "spiral": SpiralFigure,
    "defective": DefectiveFigure,
    "forced_system": ForcedSystemFigure,
    "eigenlines": EigenlinesFigure,
    "partial_sums": PartialSumsFigure,
    "recurrence": RecurrenceFigure,
    "indicial": IndicialFigure,
}


def build_figure(key: str, palette: Palette, parent=None) -> QWidget | None:
    """The figure named by `key`, or None where there is no such figure.

    None rather than an exception: a lesson naming a figure that does not exist
    is a content bug, caught by the tests, and it should not take the whole
    lesson page down with it in the meantime.
    """
    figure = FIGURES.get(key)
    return None if figure is None else figure(palette, parent)
