"""Unit 4 -- Vibrations and forcing.

Edwards, Penney and Calvis 6e, sections 3.4, 3.6 and 3.7. The chapter where the
second-order machinery stops being an exercise and starts being a mass on a
spring, a shock absorber, and a tuning circuit.

No new narrator is needed here, which is the point of putting it after Unit 3:
free vibration is characteristic roots, forced vibration is undetermined
coefficients, and the RLC circuit is the same equation with different letters.
What is new is a name for each behaviour -- underdamped, resonant, transient,
steady state -- and two figures to move.
"""

from __future__ import annotations

from .model import Choice, Example, Lesson, Note, Solve, Template

__all__ = ["FREE", "FORCED", "CIRCUITS", "LESSONS"]


FREE = Lesson(
    key="free-vibration",
    title="Free vibration: under-, critically and over-damped",
    summary="One equation, three behaviours, and a single coefficient that "
            "decides which one you get.",
    tool="steps",
    reference="Edwards 3.4",
    prerequisites=("roots",),
    figure="damping",
    objectives=(
        "Write the equation of a mass on a spring with a dashpot.",
        "Compute the critical damping coefficient for given m and k.",
        "Name the regime from the discriminant, without solving.",
        "Say what changes at critical damping and what does not.",
    ),
    examples=(
        Example(
            equation="y'' + 2*y' + 5*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            why="Underdamped: c = 2 against a critical value of 2√5 ≈ 4.47. "
                "The complex pair −1 ± 2i gives the oscillation inside a "
                "decaying envelope, which is what a real suspension does.",
        ),
        Example(
            equation="y'' + 4*y' + 4*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            why="Critically damped, exactly. c = 4 = 2√(1·4), the repeated "
                "root, and the factor of t that comes with it — the fastest "
                "return to rest with no overshoot at all.",
        ),
    ),
    notes=(
        Note(
            "The equation is Newton's second law",
            "Mass times acceleration equals the forces: a spring pulling back "
            "in proportion to displacement, and a dashpot resisting in "
            "proportion to velocity. Both act against the motion, which is "
            "why both terms move to the left with positive signs.",
            r"m x'' + c x' + k x = 0",
        ),
        Note(
            "One number decides everything",
            "The discriminant c² − 4mk is the whole story. Positive gives two "
            "real roots and no oscillation; zero gives the repeated root; "
            "negative gives a complex pair and oscillation. The boundary "
            "c = 2√(mk) is the critical damping.",
            r"c_{\text{crit}} = 2\sqrt{mk}",
            "formula",
        ),
        Note(
            "Underdamped is not undamped",
            "An underdamped system still settles — the real part of the root "
            "is −c/2m, which is negative for any positive damping. It simply "
            "oscillates on the way down. Undamped, c = 0, is the separate "
            "case where the roots are purely imaginary and it never stops.",
            r"r = -\frac{c}{2m} \pm i\omega_d,\qquad "
            r"\omega_d = \omega_0\sqrt{1-\zeta^{2}}",
            "pitfall",
        ),
        Note(
            "Critical damping is fastest, not gentlest",
            "The critically damped system returns to rest sooner than any "
            "overdamped one. More damping is not more settling: past critical, "
            "the slower root dominates and the system creeps. This is why "
            "door closers and galvanometers are tuned to critical rather than "
            "to as much damping as possible.",
            r"c > c_{\text{crit}}:\quad r = \frac{-c \pm \sqrt{c^{2}-4mk}}{2m}",
            "aside",
        ),
        Note(
            "The damping ratio",
            "Dividing by the critical value gives a dimensionless number that "
            "names the regime on its own: ζ < 1 underdamped, ζ = 1 critical, "
            "ζ > 1 overdamped. Engineers quote ζ rather than c because it "
            "means the same thing for any mass and any spring.",
            r"\zeta = \frac{c}{2\sqrt{mk}}",
            "formula",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="m = 1, k = 9. What is the critical damping coefficient?",
            options=("3", "6", "9", "18"),
            answer=1,
            becauses=(
                "That is √k, the undamped natural frequency ω₀ — related, but "
                "not the damping that makes the discriminant vanish.",
                "c_crit = 2√(mk) = 2√9 = 6. At exactly this value the "
                "discriminant c² − 4mk = 36 − 36 is zero, giving the repeated "
                "root.",
                "That is k itself. The critical damping depends on both the "
                "mass and the stiffness, through their product's square root.",
                "That is 2k. The factor of 2 belongs outside the square root, "
                "not multiplying k.",
            ),
        ),
        Choice(
            key="q2",
            prompt="x'' + 6x' + 5x = 0 describes a system that is…",
            latex=r"x'' + 6x' + 5x = 0",
            options=(
                "underdamped",
                "critically damped",
                "overdamped",
                "undamped",
            ),
            answer=2,
            becauses=(
                "Underdamped needs a negative discriminant. Here it is "
                "36 − 20 = 16, comfortably positive, so there is no "
                "oscillation at all.",
                "Critical needs the discriminant to be exactly zero, which "
                "would take c = 2√5 ≈ 4.47 rather than 6.",
                "The discriminant is 36 − 20 = 16 > 0, so the roots are real "
                "and distinct — −1 and −5. Two decaying exponentials, no "
                "oscillation: overdamped.",
                "Undamped means c = 0. There is a 6x' term, so energy is "
                "certainly being removed.",
            ),
        ),
        Choice(
            key="q3",
            prompt="A door closer overshoots and slams. What should change?",
            options=(
                "Increase the damping towards critical",
                "Decrease the damping",
                "Increase the spring stiffness",
                "Nothing — overshoot is unavoidable",
            ),
            answer=0,
            becauses=(
                "Overshoot means the system is underdamped, so the roots are "
                "a complex pair. Raising c towards 2√(mk) collides them on "
                "the real axis, and at critical damping there is no overshoot "
                "at all.",
                "Less damping makes the oscillation larger and slower to die "
                "away — exactly the wrong direction.",
                "A stiffer spring raises the critical damping too, so the "
                "same c becomes relatively *less* damping. It would slam "
                "harder and sooner.",
                "Overshoot is avoidable, and avoiding it is what critical "
                "damping is for.",
            ),
        ),
        Solve(
            key="q4",
            prompt="An underdamped system, released from rest.",
            equation="y'' + 2*y' + 5*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            hints=(
                "The discriminant is 4 − 20 = −16, so expect a complex pair.",
                "r = −1 ± 2i, giving e^{−t}(C₁cos 2t + C₂sin 2t).",
                "y(0) = 1 gives C₁ = 1. Differentiate: y′(0) = −C₁ + 2C₂ = 0, "
                "so C₂ = 1/2.",
            ),
        ),
        Solve(
            key="q5",
            prompt="Exactly critically damped.",
            equation="y'' + 4*y' + 4*y = 0",
            conditions="y(0) = 2, y'(0) = 0",
            hints=(
                "c² − 4mk = 16 − 16 = 0, the boundary case.",
                "(r + 2)² = 0, a repeated root at −2, so the second solution "
                "carries a factor of t.",
                "y = (C₁ + C₂t)e^{−2t}. y(0) = 2 gives C₁ = 2, and "
                "y′(0) = C₂ − 2C₁ = 0 gives C₂ = 4.",
            ),
        ),
    ),
    templates=(
        Template(
            key="which-regime",
            title="Damping across the three regimes",
            prompt="Find the roots, name the regime, then apply the "
                   "conditions.",
            equation="y'' + {c}*y' + {k}*y = 0",
            conditions="y(0) = {p}, y'(0) = 0",
            technique="nth_linear_constant_coeff_homogeneous",
            hints=(
                "Work out c² − 4k before anything else. Its sign names the "
                "regime and tells you which shape you are about to write.",
                "Negative means a complex pair, and so an oscillation inside "
                "a decaying envelope; zero means a repeated root and a factor "
                "of t; positive means two plain exponentials.",
                "Write the general solution for that case, then use y(0) and "
                "y'(0) = 0 — remember to differentiate before the second.",
            ),
            # Chosen so all three regimes appear and the roots stay readable:
            # (2,5) and (2,10) underdamped, (4,4) and (6,9) critical,
            # (5,6) and (6,5) overdamped.
            slots=(
                ("c,k", ((2, 5), (2, 10), (4, 4), (6, 9), (5, 6), (6, 5),
                         (0, 4), (0, 9), (4, 8))),
                ("p", (1, 2, 3)),
            ),
        ),
    ),
)


FORCED = Lesson(
    key="forced-vibration",
    title="Forced oscillation, beats and resonance",
    summary="What happens when something drives the system, and why matching "
            "its natural frequency is destructive.",
    tool="steps",
    reference="Edwards 3.6",
    prerequisites=("undetermined", "free-vibration"),
    figure="resonance",
    objectives=(
        "Split a forced response into transient and steady state.",
        "Recognise beats, and say what frequency difference produces them.",
        "Explain why undamped resonance produces a t in the solution.",
        "Read the amplitude response off m, c, k and the driving frequency.",
    ),
    examples=(
        Example(
            equation="y'' + 4*y = cos(t)",
            conditions="y(0) = 0, y'(0) = 0",
            why="Driven off resonance: ω = 1 against ω₀ = 2. The particular "
                "solution is an ordinary cosine, and the two frequencies "
                "together produce the beating envelope.",
        ),
        Example(
            equation="y'' + 4*y = cos(2*t)",
            conditions="y(0) = 0, y'(0) = 0",
            why="Pure resonance: the forcing is already a solution of the "
                "homogeneous equation, so the guess has to be multiplied by "
                "t. That t is the amplitude growing without bound.",
        ),
    ),
    notes=(
        Note(
            "Transient plus steady state",
            "The homogeneous part carries the initial conditions and decays "
            "whenever there is damping — it is the transient. The particular "
            "part is driven by the forcing and persists — the steady state. "
            "After a few time constants only the second is left, which is why "
            "the long-run behaviour does not depend on how the system "
            "started.",
            r"x(t) = x_h(t) + x_p(t) \qquad "
            r"\text{transient} \;+\; \text{steady state}",
        ),
        Note(
            "Beats",
            "Drive an undamped system near, but not at, its natural "
            "frequency and the response is a difference of two cosines. "
            "Rewritten as a product, it is a fast oscillation inside a slow "
            "envelope: the beat frequency is the difference of the two, so "
            "the closer they are the longer each swell lasts.",
            r"\cos\omega t - \cos\omega_0 t = "
            r"2\sin\frac{(\omega_0-\omega)t}{2}\,"
            r"\sin\frac{(\omega_0+\omega)t}{2}",
            "formula",
        ),
        Note(
            "Resonance is the guess failing",
            "At ω = ω₀ the forcing term already solves the homogeneous "
            "equation, so no multiple of it can produce a right-hand side. "
            "Multiply the guess by t — the same correction as any other "
            "resonant case — and the t is exactly the amplitude growing "
            "without bound.",
            r"x_p = \frac{t}{2\omega_0}\sin\omega_0 t",
            "formula",
        ),
        Note(
            "Unbounded growth needs zero damping",
            "The t in the resonant solution is a consequence of c = 0, which "
            "no real system has. With damping the response stays bounded and "
            "resonance becomes a peak in the amplitude rather than a "
            "blow-up — large, but finite, and larger the smaller c is.",
            r"A(\omega) = \frac{F_0}{\sqrt{(k-m\omega^{2})^{2} + "
            r"(c\omega)^{2}}}",
            "pitfall",
        ),
        Note(
            "The peak is not quite at the natural frequency",
            "The amplitude response peaks slightly below ω₀ once there is "
            "damping, and it moves further down and flattens as c grows. "
            "Enough damping and there is no peak at all — the largest "
            "response is at zero frequency, and the system merely follows "
            "the forcing.",
            r"\omega_{\text{peak}} = \omega_0\sqrt{1 - 2\zeta^{2}}",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="x'' + 9x = cos 3t. Which trial form is right?",
            latex=r"x'' + 9x = \cos 3t",
            options=(
                "A cos 3t + B sin 3t",
                "t(A cos 3t + B sin 3t)",
                "A e^{3t}",
                "A cos 3t only",
            ),
            answer=1,
            becauses=(
                "That is already a solution of x'' + 9x = 0, so substituting "
                "it gives zero, never cos 3t. This is the resonant case and "
                "the naive guess cannot work.",
                "ω₀ = 3 matches the driving frequency, so the naive guess is "
                "in the fundamental set. Multiply by t — and that t is the "
                "growing amplitude resonance is named for.",
                "An exponential guess belongs to exponential forcing. "
                "Trigonometric forcing needs trigonometric trial terms.",
                "Even off resonance you need both the cosine and the sine, "
                "because differentiating twice can produce either.",
            ),
        ),
        Choice(
            key="q2",
            prompt="An undamped system with ω₀ = 5 is driven at ω = 4.9. What "
                   "do you see?",
            options=(
                "Resonance: unbounded growth",
                "Slow beats with a long envelope",
                "Rapid decay to zero",
                "A constant-amplitude oscillation at ω₀",
            ),
            answer=1,
            becauses=(
                "Unbounded growth needs ω to equal ω₀ exactly. Near it the "
                "amplitude is large but bounded — 1/(ω₀² − ω²) is big, not "
                "infinite.",
                "Two close frequencies beat. The envelope oscillates at half "
                "their difference, so 0.1 apart makes swells lasting about "
                "2π/0.05 ≈ 126 time units — long and slow.",
                "There is no damping, so nothing decays. That is what makes "
                "the beats persist rather than settle.",
                "The response contains both frequencies, not just ω₀, and it "
                "is their interference that produces the changing amplitude.",
            ),
        ),
        Choice(
            key="q3",
            prompt="After a long time, a damped forced system's motion "
                   "depends on…",
            options=(
                "the initial conditions",
                "the forcing alone",
                "neither",
                "the initial conditions, but only their signs",
            ),
            answer=1,
            becauses=(
                "The initial conditions live entirely in the transient, and "
                "the transient decays. They decide the early motion and "
                "nothing about the late motion.",
                "Only the steady state survives, and it is set by the forcing "
                "amplitude and frequency against m, c and k. This is why a "
                "machine's vibration can be predicted without knowing how it "
                "was switched on.",
                "Something survives: the steady state persists for as long as "
                "the forcing does.",
                "Nothing of the initial conditions survives — not their "
                "magnitudes and not their signs.",
            ),
        ),
        Solve(
            key="q4",
            prompt="Driven off resonance, from rest.",
            equation="y'' + 4*y = cos(t)",
            conditions="y(0) = 0, y'(0) = 0",
            hints=(
                "ω₀ = 2 and ω = 1 differ, so the naive guess A cos t is not "
                "in the fundamental set and needs no correction.",
                "Substituting gives −A cos t + 4A cos t = cos t, so A = 1/3.",
                "y = C₁cos 2t + C₂sin 2t + (cos t)/3, and starting from rest "
                "gives C₁ = −1/3, C₂ = 0.",
            ),
        ),
        Solve(
            key="q5",
            prompt="Pure resonance.",
            equation="y'' + 4*y = cos(2*t)",
            conditions="y(0) = 0, y'(0) = 0",
            hints=(
                "ω = ω₀ = 2, so cos 2t already solves the homogeneous "
                "equation and the naive guess is useless.",
                "Multiply by t: try t(A cos 2t + B sin 2t).",
                "Substituting gives A = 0 and B = 1/4, so "
                "y_p = t·sin(2t)/4 — an amplitude growing linearly.",
            ),
        ),
    ),
    templates=(
        Template(
            key="driven-oscillator",
            title="Driven, on and off resonance",
            prompt="Guess, correct for resonance if you must, then start from "
                   "rest.",
            equation="y'' + {k}*y = cos({w}*t)",
            conditions="y(0) = 0, y'(0) = 0",
            technique="nth_linear_constant_coeff_undetermined_coefficients",
            hints=(
                "The natural frequency is √k. Compare it with the driving "
                "frequency before writing any guess down.",
                "If they differ, A cos(ωt) will do. If they match, that guess "
                "solves the homogeneous equation and must be multiplied by t.",
                "Substitute, match the coefficient of the cosine, then use "
                "both conditions — starting from rest usually kills the sine.",
            ),
            # k a perfect square so the natural frequency is an integer, and
            # w chosen to hit resonance in some draws and miss it in others:
            # that contrast is the lesson.
            slots=(
                ("k", (1, 4, 9, 16)),
                ("w", (1, 2, 3, 4)),
            ),
        ),
    ),
)


CIRCUITS = Lesson(
    key="circuits",
    title="Electrical circuits: the RLC analogy",
    summary="The same equation with different letters — and why an engineer "
            "who knows springs already knows circuits.",
    tool="steps",
    reference="Edwards 3.7",
    prerequisites=("free-vibration", "forced-vibration"),
    objectives=(
        "Write the RLC equation from Kirchhoff's voltage law.",
        "Match each electrical quantity to its mechanical counterpart.",
        "Compute the resonant frequency of an LC pair.",
        "Say what critical damping means for a circuit.",
    ),
    examples=(
        Example(
            equation="y'' + 4*y' + 3*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            why="L = 1, R = 4, 1/C = 3 — an overdamped circuit, the charge "
                "decaying without ringing. The same equation as an "
                "overdamped spring, and it is solved the same way.",
        ),
        Example(
            equation="y'' + 2*y' + 26*y = 0",
            conditions="y(0) = 0, y'(0) = 1",
            why="A ringing circuit: roots −1 ± 5i. The oscillation is the "
                "charge sloshing between the capacitor and the inductor, "
                "with the resistance draining it.",
        ),
    ),
    notes=(
        Note(
            "Kirchhoff gives the equation",
            "The voltages around a loop sum to the source. The inductor "
            "contributes L·dI/dt, the resistor R·I, and the capacitor q/C. "
            "Writing I = dq/dt makes it one second-order equation in the "
            "charge — and the same equation you have been solving all "
            "chapter.",
            r"L q'' + R q' + \frac{1}{C} q = E(t)",
        ),
        Note(
            "The dictionary",
            "Every term has a mechanical counterpart. Inductance resists "
            "changes in current the way mass resists changes in velocity; "
            "resistance dissipates like a dashpot; the reciprocal of "
            "capacitance pulls charge back like a spring pulls displacement.",
            r"m \leftrightarrow L,\quad c \leftrightarrow R,\quad "
            r"k \leftrightarrow 1/C,\quad F(t) \leftrightarrow E(t)",
            "formula",
        ),
        Note(
            "It is 1/C, not C",
            "Capacitance sits in the denominator, so a *larger* capacitor is "
            "a *weaker* spring. Reading C straight across as the stiffness "
            "inverts every conclusion about the circuit, and it is the one "
            "place this analogy catches people out.",
            r"k \leftrightarrow \frac{1}{C}\quad\text{— not } C",
            "pitfall",
        ),
        Note(
            "Resonance is how a radio tunes",
            "The resonant frequency of an LC pair is 1/√(LC). A receiver "
            "varies C until that matches the station's carrier, so one "
            "signal is amplified far above the rest — the same amplitude "
            "peak as a driven spring, put to work.",
            r"\omega_0 = \frac{1}{\sqrt{LC}}",
            "formula",
        ),
        Note(
            "Critical damping, electrically",
            "R = 2√(L/C) is the critical resistance: below it the circuit "
            "rings, above it the charge creeps back. The design question is "
            "the same as the door closer's, and the discriminant answering it "
            "is the same discriminant.",
            r"R_{\text{crit}} = 2\sqrt{L/C}",
            "aside",
        ),
    ),
    questions=(
        Choice(
            key="q1",
            prompt="In the RLC analogy, what plays the part of the mass?",
            options=("Resistance R", "Inductance L", "Capacitance C", "1/C"),
            answer=1,
            becauses=(
                "Resistance dissipates energy, which is the dashpot's job — "
                "it matches c, not m.",
                "L multiplies the second derivative, exactly as m does. It "
                "resists changes in current the way mass resists changes in "
                "velocity, and it stores energy rather than dissipating it.",
                "Capacitance is a spring, and inversely at that: the "
                "stiffness is 1/C.",
                "1/C multiplies q itself, which is the spring term k — the "
                "zeroth derivative, not the second.",
            ),
        ),
        Choice(
            key="q2",
            prompt="L = 1 H, C = 1/25 F. What is the resonant frequency?",
            options=("5 rad/s", "25 rad/s", "1/5 rad/s", "1/25 rad/s"),
            answer=0,
            becauses=(
                "ω₀ = 1/√(LC) = 1/√(1/25) = 5. Equivalently the stiffness is "
                "1/C = 25 and the mass is 1, so ω₀ = √(k/m) = 5 — the same "
                "sum in mechanical clothing.",
                "That is 1/C, the stiffness, not its square root. The "
                "frequency is the square root of stiffness over mass.",
                "That is √C. The capacitance goes into the formula "
                "reciprocally, so a small C gives a *high* frequency.",
                "That is C itself, and it inverts the relationship twice "
                "over.",
            ),
        ),
        Choice(
            key="q3",
            prompt="A circuit rings when it should settle. What raises the "
                   "damping?",
            options=(
                "More resistance",
                "More inductance",
                "More capacitance",
                "Less resistance",
            ),
            answer=0,
            becauses=(
                "Resistance is the dashpot. Ringing means R < 2√(L/C), so "
                "raising R towards that value collides the complex roots on "
                "the real axis and stops the oscillation.",
                "More inductance raises the critical resistance too — it is "
                "more mass, so the same R becomes relatively less damping. It "
                "would ring longer.",
                "A larger capacitor is a weaker spring, which lowers the "
                "frequency but does not stop the ringing.",
                "Less resistance is less damping, which makes the ringing "
                "worse and longer-lived.",
            ),
        ),
        Solve(
            key="q4",
            prompt="An overdamped circuit: L = 1, R = 4, 1/C = 3.",
            equation="y'' + 4*y' + 3*y = 0",
            conditions="y(0) = 1, y'(0) = 0",
            hints=(
                "The discriminant is 16 − 12 = 4 > 0, so the charge decays "
                "without ringing.",
                "r² + 4r + 3 = (r+1)(r+3), so the roots are −1 and −3.",
                "y = C₁e^{−t} + C₂e^{−3t}, and starting from rest at charge 1 "
                "gives C₁ = 3/2, C₂ = −1/2.",
            ),
        ),
        Solve(
            key="q5",
            prompt="A ringing circuit, from zero charge.",
            equation="y'' + 2*y' + 26*y = 0",
            conditions="y(0) = 0, y'(0) = 1",
            hints=(
                "4 − 104 < 0, so expect a complex pair and oscillation.",
                "r = −1 ± 5i: the charge rings at 5 rad/s inside an e^{−t} "
                "envelope.",
                "y(0) = 0 removes the cosine, and y′(0) = 1 gives 5C₂ = 1.",
            ),
        ),
    ),
    templates=(
        Template(
            key="rlc-regimes",
            title="An RLC circuit, across its regimes",
            prompt="L·q'' + R·q' + q/C = 0. Find the charge.",
            equation="y'' + {r}*y' + {s}*y = 0",
            conditions="y(0) = {q0}, y'(0) = 0",
            technique="nth_linear_constant_coeff_homogeneous",
            hints=(
                "With L = 1 the coefficients are R and 1/C directly, so the "
                "characteristic polynomial is r² + R·r + 1/C.",
                "Compare R with 2√(1/C): below it the circuit rings, above it "
                "the charge creeps back without oscillating.",
                "Write the general solution for that regime, then apply the "
                "initial charge and zero initial current.",
            ),
            # R and 1/C for a realistic spread of circuits: ringing, exactly
            # critical, and overdamped.
            slots=(
                ("r,s", ((2, 26), (2, 5), (4, 3), (4, 4), (6, 5), (10, 25),
                         (1, 17), (5, 4))),
                ("q0", (1, 2)),
            ),
        ),
    ),
)


LESSONS = (FREE, FORCED, CIRCUITS)
