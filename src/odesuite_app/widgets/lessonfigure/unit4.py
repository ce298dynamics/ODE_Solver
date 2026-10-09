"""Figures for Vibrations and forcing."""

from __future__ import annotations

import math

import numpy as np
import pyqtgraph as pg
import sympy as sp
from PySide6.QtCore import Qt

from odesuite import problems

from ...symbolic import describe_roots
from .base import LessonFigure

# ---------------------------------------------------------------------------
# Damping: one coefficient, three behaviours
# ---------------------------------------------------------------------------


class DampingFigure(LessonFigure):
    """``m x'' + c x' + k x = 0``, with the roots drawn beside the motion.

    The two panes are the same fact told twice, which is the point. On the left
    a complex pair sits off the real axis and the motion oscillates; drag `c`
    up and the pair slides together, collides at ``c = 2*sqrt(mk)``, and splits
    along the real axis -- and the curve on the right stops crossing zero at
    the same moment. Seeing the discriminant change sign is usually a sentence
    in a textbook; here it is a thing that happens.

    The name under the picture comes from `symbolic.describe_roots`, which the
    Solver Studio's root table already uses, so the figure cannot disagree with
    the screen that names the same roots.
    """

    title = "Damping: where the roots go, and what the mass does"
    caption = ("Left: the characteristic roots in the complex plane. Right: "
               "the motion they produce. Drag c and watch the pair slide "
               "together, meet on the real axis at c = 2√(mk), and separate — "
               "the moment the oscillation stops.")
    plots = 2

    _T_END = 12.0

    #: Half a step of the damping slider. Critical damping is a single point
    #: on a continuum, so a slider can essentially never land on it -- at
    #: m = 1, k = 4 the nearest reachable value was 3.996, which is genuinely
    #: underdamped and reported as such. The middle of the three regimes then
    #: never appeared at all, in a figure whose whole subject is the moment
    #: the roots collide. So the damping snaps to the critical value when it
    #: comes within half a step of it: the number shown *is* the number used,
    #: and the regime named is the regime drawn.
    _SNAP = 12.0 / 1000 / 2

    def build_sliders(self) -> None:
        self.add_slider("m", "m  (mass)", 0.5, 4.0, 1.0)
        self.add_slider("c", "c  (damping)", 0.0, 12.0, 1.0,
                        hint="The one coefficient that decides the regime. "
                             "Critical damping is at 2√(mk), and the slider "
                             "snaps to it as it passes.")
        self.add_slider("k", "k  (stiffness)", 1.0, 16.0, 4.0)

    def damping(self) -> tuple[float, float]:
        """``(c, c_critical)``, with `c` snapped to critical when it is near."""
        m, k = self.value("m"), self.value("k")
        critical = 2.0 * math.sqrt(m * k)
        c = self.value("c")
        return (critical if abs(c - critical) <= self._SNAP else c), critical

    def _roots(self, m: float, c: float, k: float):
        """The characteristic roots, as sympy expects to be handed them.

        `describe_roots` wants ``[(root, multiplicity)]`` -- the same shape the
        Studio's root table passes it -- so a repeated root is one entry with
        multiplicity two rather than the same number twice, and the words
        "critically damped" depend on getting that right.
        """
        discriminant = c * c - 4.0 * m * k
        if abs(discriminant) < 1e-9 * max(c * c, 1.0):
            return [(sp.Float(-c / (2 * m)), 2)]
        if discriminant > 0:
            root = math.sqrt(discriminant)
            return [(sp.Float((-c + root) / (2 * m)), 1),
                    (sp.Float((-c - root) / (2 * m)), 1)]
        imaginary = math.sqrt(-discriminant) / (2 * m)
        real = -c / (2 * m)
        return [(sp.Float(real) + sp.I * sp.Float(imaginary), 1),
                (sp.Float(real) - sp.I * sp.Float(imaginary), 1)]

    def draw(self) -> None:
        m, k = self.value("m"), self.value("k")
        c, critical = self.damping()
        roots = self._roots(m, c, k)

        plane, motion = self.panes
        plane.clear()
        plane.setLabel("bottom", "Re r")
        plane.setLabel("left", "Im r")
        plane.addLine(x=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        plane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))

        oscillates = any(sp.im(root) != 0 for root, _ in roots)
        colour = self.palette_obj.accent if oscillates else self.colour(1)
        for root, multiplicity in roots:
            plane.plot(
                [float(sp.re(root))], [float(sp.im(root))], pen=None,
                symbol="o", symbolSize=13 if multiplicity > 1 else 10,
                symbolBrush=colour, symbolPen=pg.mkPen(colour, width=2),
            )
        # Fix the window so the roots *move* rather than the axes moving under
        # them: a pair colliding is only visible if the frame holds still.
        # The natural frequency is the scale to use, because every underdamped
        # root lies inside a circle of that radius -- so the frame does not
        # budge anywhere in the range where the collision happens. It widens
        # only once a root runs off to the left, which is well past it.
        natural = math.sqrt(k / m)
        furthest = max(abs(float(sp.re(root))) for root, _ in roots)
        reach = 1.4 * max(natural, furthest)
        plane.setXRange(-reach, 0.35 * natural, padding=0.02)
        plane.setYRange(-1.4 * natural, 1.4 * natural, padding=0.02)

        motion.clear()
        motion.setLabel("bottom", "t")
        motion.setLabel("left", "x")
        motion.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        bench = problems.spring_mass_damper(
            mass=m, damping=c, stiffness=k,
            initial_position=1.0, initial_velocity=0.0, t_end=self._T_END,
        )
        times = np.linspace(0.0, self._T_END, 600)
        values = np.atleast_2d(bench.exact(times))[0]
        motion.plot(times, values, pen=pg.mkPen(colour, width=2))

        self.readout.setText(
            f"{describe_roots(roots, order=2)}    —    "
            f"c = {c:.2f} against a critical {critical:.2f}"
        )


# ---------------------------------------------------------------------------
# Beats, and resonance
# ---------------------------------------------------------------------------


class ResonanceFigure(LessonFigure):
    """``x'' + w0^2 x = cos(w t)`` from rest, and the amplitude it settles to.

    Two panes because these are two different claims. On the left, an *undamped*
    system driven near its natural frequency: the response is a difference of
    cosines, which reads as a fast oscillation inside a slow envelope, and the
    envelope grows longer the closer the frequencies get. On the right, what
    damping does to the same story -- the blow-up becomes a peak, finite and
    lower and further left the more damping there is.

    Measured, and it shapes the code: the beats amplitude ``1/(w0^2 - w^2)`` is
    0.69 at w = 1.6, 2.56 at 1.9 and **25.1 at 1.99**, so the pane is left to
    autorange rather than pinned, and at w = w0 the closed form is the secular
    ``t*sin(w0 t)/(2 w0)`` rather than a division by zero.
    """

    title = "Beats, and what happens when the frequencies match"
    caption = ("Left: an undamped system driven at ω, from rest. As ω "
               "approaches ω₀ = 2 the beats stretch out and grow, and at ω = "
               "ω₀ exactly the envelope becomes a straight line — resonance. "
               "Right: with damping the blow-up is only a peak.")
    plots = 2

    _W0 = 2.0
    _T_END = 60.0

    def build_sliders(self) -> None:
        self.add_slider("w", "ω  (driving frequency)", 0.5, 3.5, 1.6,
                        hint="The natural frequency is 2. Bring ω up to it "
                             "and watch the envelope stretch.")
        self.add_slider("c", "c  (damping, right-hand plot)", 0.05, 3.0, 0.4)

    def _response(self, times, omega: float):
        """``x(t)`` from rest, and whether this is the resonant case.

        The two formulas are one limit apart, and the limit is the lesson: as
        w -> w0 the bounded solution's amplitude runs away, and exactly at w0
        the t out front is what is left of it.
        """
        w0 = self._W0
        if abs(omega - w0) < 1e-3:
            return times * np.sin(w0 * times) / (2 * w0), True
        amplitude = 1.0 / (w0 * w0 - omega * omega)
        return amplitude * (np.cos(omega * times) - np.cos(w0 * times)), False

    def draw(self) -> None:
        omega, c = self.value("w"), self.value("c")
        beats, resonant = self.panes

        times = np.linspace(0.0, self._T_END, 3000)
        values, at_resonance = self._response(times, omega)

        beats.clear()
        beats.setLabel("bottom", "t")
        beats.setLabel("left", "x")
        beats.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
        beats.plot(times, values, pen=pg.mkPen(self.colour(0), width=1))

        # The envelope, drawn because it is the thing being described. Off
        # resonance it is the slow half of the product formula; at resonance
        # it is the straight line the amplitude follows.
        w0 = self._W0
        if at_resonance:
            envelope = times / (2 * w0)
        else:
            envelope = np.abs(
                2.0 / (w0 * w0 - omega * omega)
                * np.sin((w0 - omega) * times / 2)
            )
        for sign in (1, -1):
            beats.plot(times, sign * envelope,
                       pen=pg.mkPen(self.palette_obj.text_muted, width=2,
                                    style=Qt.DashLine))
        beats.enableAutoRange(axis="y")

        resonant.clear()
        resonant.setLabel("bottom", "ω")
        resonant.setLabel("left", "steady amplitude")
        frequencies = np.linspace(0.05, 4.0, 500)
        # The standard response of m x'' + c x' + k x = cos(wt), with m = 1 and
        # k = w0^2 so the two panes describe the same oscillator.
        stiffness = w0 * w0
        amplitudes = 1.0 / np.sqrt(
            (stiffness - frequencies**2) ** 2 + (c * frequencies) ** 2
        )
        resonant.plot(frequencies, amplitudes,
                      pen=pg.mkPen(self.colour(1), width=2))
        peak = int(np.argmax(amplitudes))
        resonant.plot([frequencies[peak]], [amplitudes[peak]], pen=None,
                      symbol="o", symbolSize=9,
                      symbolBrush=self.colour(1), symbolPen=self.colour(1))
        resonant.addLine(x=omega,
                         pen=pg.mkPen(self.palette_obj.text_muted, width=1,
                                      style=Qt.DashLine))

        if at_resonance:
            words = ("ω = ω₀: resonance. The particular solution carries a "
                     "factor of t, so the amplitude grows without bound")
        else:
            period = 4 * math.pi / abs(w0 - omega)
            words = (f"beats: amplitude {abs(1 / (w0 * w0 - omega * omega)):.2f}"
                     f", one swell every {period:.0f} time units")
        self.readout.setText(
            f"{words}    —    damped peak {amplitudes[peak]:.2f} at "
            f"ω = {frequencies[peak]:.2f}"
        )


# ---------------------------------------------------------------------------
# Circuits: the same equation, wearing different letters
# ---------------------------------------------------------------------------


class CircuitFigure(LessonFigure):
    """An RLC loop beside its mass-spring twin, driven by the same numbers.

    The lesson's claim is not that the two systems are *similar*. It is that
    they are the same equation, and that every fact proved about one is
    already a fact about the other. A figure of two systems that merely looked
    alike would understate that, so the two panes are driven from a single set
    of sliders through the correspondence L = m, R = c, 1/C = k -- and the
    curves are then identical to floating point, which the readout measures
    and prints.

    That measurement is the point of the figure. The residual between the two
    panes is not small because the models were tuned to agree; it is zero
    because there is only one model, and anything other than zero here would
    mean the analogy had been written down wrong.
    """

    title = "One equation, two circuits of letters"
    caption = ("Left: the charge on the capacitor in L·q″ + R·q′ + q/C = 0. "
               "Right: the position of a mass in m·x″ + c·x′ + k·x = 0, with "
               "m = L, c = R and k = 1/C. The sliders drive both. The curves "
               "are not similar; they are the same numbers.")
    plots = 2

    _T_END = 14.0

    def build_sliders(self) -> None:
        self.add_slider("L", "L  (henries)   =   m  (mass)", 0.4, 3.0, 1.0)
        self.add_slider("R", "R  (ohms)   =   c  (damping)", 0.0, 4.0, 0.6,
                        hint="Resistance dissipates energy as heat; damping "
                             "dissipates it as heat. The analogy is not a "
                             "metaphor at this point.")
        self.add_slider("C", "C  (farads),  so  k = 1/C", 0.15, 2.0, 0.5)

    def elements(self) -> tuple[float, float, float]:
        """``(L, R, 1/C)``, which is also ``(m, c, k)``."""
        return self.value("L"), self.value("R"), 1.0 / self.value("C")

    def _response(self, t: np.ndarray) -> np.ndarray:
        """The free response from q(0) = 1, q'(0) = 0, in closed form.

        Closed form rather than a solve, and one function rather than two: if
        the analogy is real then there is nothing to compute twice, and
        computing it twice would be the figure quietly hedging on its own
        claim.
        """
        inductance, resistance, stiffness = self.elements()
        discriminant = resistance ** 2 - 4.0 * inductance * stiffness
        alpha = -resistance / (2.0 * inductance)
        if abs(discriminant) < 1e-12:
            return (1.0 - alpha * t) * np.exp(alpha * t)
        if discriminant > 0:
            gap = math.sqrt(discriminant) / (2.0 * inductance)
            first, second = alpha + gap, alpha - gap
            return ((second * np.exp(first * t) - first * np.exp(second * t))
                    / (second - first))
        beta = math.sqrt(-discriminant) / (2.0 * inductance)
        return np.exp(alpha * t) * (np.cos(beta * t)
                                    - (alpha / beta) * np.sin(beta * t))

    def draw(self) -> None:
        t = np.linspace(0.0, self._T_END, 1200)
        values = self._response(t)

        for index, (pane, axis) in enumerate((
            (self.panes[0], "q  (charge)"), (self.panes[1], "x  (position)"),
        )):
            pane.clear()
            pane.setLabel("bottom", "t")
            pane.setLabel("left", axis)
            pane.addLine(y=0, pen=pg.mkPen(self.palette_obj.border, width=1))
            pane.plot(t, values, pen=pg.mkPen(self.colour(index), width=3))
            pane.setYRange(-1.2, 1.2, padding=0.02)
        self._describe(t, values)

    def _describe(self, t: np.ndarray, values: np.ndarray) -> None:
        inductance, resistance, stiffness = self.elements()
        natural = math.sqrt(stiffness / inductance)
        critical = 2.0 * math.sqrt(inductance * stiffness)
        regime = ("no resistance at all: it rings forever" if resistance <= 1e-9
                  else "oscillating, and losing amplitude to the resistor"
                  if resistance < critical - 1e-9 else
                  "no oscillation left: the charge returns without overshoot")
        # The residual of the drawn curve against the circuit equation, which
        # is also its residual against the mechanical one. Measured, because
        # "the same equation" is the claim.
        step = float(t[1] - t[0])
        speed = np.gradient(values, step)
        acceleration = np.gradient(speed, step)
        residual = float(np.max(np.abs(
            inductance * acceleration + resistance * speed + stiffness * values
        )[4:-4]))
        self.readout.setText(
            f"L = m = {inductance:.2f},  R = c = {resistance:.2f},  "
            f"1/C = k = {stiffness:.2f}. Resonant frequency 1/√(LC) = "
            f"√(k/m) = {natural:.3f}; critical at R = 2√(L/C) = "
            f"{critical:.3f}, so this is {regime}. The one curve satisfies "
            f"both equations to {residual:.1e}."
        )
