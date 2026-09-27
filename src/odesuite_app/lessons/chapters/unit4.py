"""Unit 4 chapters -- vibrations and forcing (Edwards 3.4, 3.6-3.7)."""

from __future__ import annotations

from ..chapter import Box, Curve, Display, Figure, Para, Plot, Section, Step, Worked

__all__ = ["FREE", "FORCED"]


FORCED = (
    Section("Pushing a system that wants to vibrate", (
        Para(
            "The last lesson let a spring vibrate on its own. This one pushes "
            "it. A periodic external force F(t) = F₀cos ωt acts on the mass — "
            "an unbalanced motor, the bumps of a road, the wind shedding "
            "vortices off a chimney, the alternating voltage in a circuit — "
            "and the question is how the system responds. The answer depends "
            "on a comparison that runs through the whole lesson: the "
            "frequency ω at which the system is pushed against the natural "
            "frequency ω₀ at which it would vibrate if left alone."
        ),
        Display(r"m x'' + c x' + k x = F_0 \cos\omega t", "1"),
        Para(
            "Equation (1) is linear with constant coefficients and a "
            "sinusoidal forcing, so Unit 3 solves it: the general solution is "
            "the complementary function, which is the free vibration of the "
            "last lesson, plus a particular solution found by undetermined "
            "coefficients. The physics lies in reading the two parts. The "
            "complementary function depends on the initial conditions; the "
            "particular solution depends only on the forcing. With damping, "
            "the first dies away and the second is what remains."
        ),
        Box(
            "definition", "Transient and steady-state response",
            "For a damped system the complementary function decays and is "
            "called the *transient*. The particular solution that oscillates "
            "at the forcing frequency, and persists, is the *steady-state "
            "response*.",
            r"x(t) = x_c(t) + x_p(t), \qquad x_c(t) \to 0",
        ),
    )),
    Section("Undamped forcing away from resonance", (
        Para(
            "Start with no damping and ω ≠ ω₀. The trial A cos ωt works (the "
            "equation has no first derivative, so no sine is needed), and "
            "substituting gives A(k − mω²) = F₀. So the particular solution is "
            "a cosine at the forcing frequency with amplitude F₀/(k − mω²), "
            "or F₀/(m(ω₀² − ω²)) — large when ω is close to ω₀, and negative "
            "when ω > ω₀, meaning the mass moves opposite to the force."
        ),
        Display(r"x_p = \frac{F_0/m}{\omega_0^{2} - \omega^{2}}\cos\omega t", "2"),
        Worked(
            "Forcing below the natural frequency",
            "Solve x'' + 9x = 10 cos 2t from rest at equilibrium.",
            (
                Step("ω₀ = 3 and ω = 2. The trial A cos 2t gives (9 − 4)A = 10, "
                     "so A = 2 and x_p = 2 cos 2t.",
                     r"x = 2\cos 2t + c_1\cos 3t + c_2\sin 3t"),
                Step("x(0) = 2 + c₁ = 0 gives c₁ = −2; x'(0) = 3c₂ = 0 gives "
                     "c₂ = 0."),
            ),
            equation="y'' + 9*y = 10*cos(2*t)", conditions="y(0) = 0, y'(0) = 0",
            answer="2*cos(2*t) - 2*cos(3*t)",
            answer_latex=r"x(t) = 2\cos 2t - 2\cos 3t",
        ),
        Para(
            "Without damping the free vibration −2 cos 3t never dies, and the "
            "motion is a permanent mixture of the forcing frequency and the "
            "natural one. Since 2 and 3 are in the ratio 2 : 3 the pattern "
            "repeats every 2π, but for an irrational ratio it would never "
            "repeat exactly. Real systems always have some damping, which "
            "eventually removes the natural-frequency part and leaves the "
            "steady response alone."
        ),
    )),
    Section("Beats", (
        Para(
            "Something striking happens when the forcing frequency is close "
            "to, but not equal to, the natural one. Take x'' + ω₀²x = "
            "(F₀/m)cos ωt from rest. The solution is a difference of two "
            "cosines of nearly equal frequency, and the trigonometric identity "
            "for cos A − cos B turns it into a product."
        ),
        Display(r"x = \frac{2F_0/m}{\omega_0^{2} - \omega^{2}}\, "
                r"\sin\frac{(\omega_0 - \omega)t}{2}\, "
                r"\sin\frac{(\omega_0 + \omega)t}{2}", "3"),
        Para(
            "Read (3) as a fast oscillation at the average frequency "
            "(ω₀ + ω)/2 whose amplitude is itself a slow oscillation at half "
            "the difference frequency. The result swells and fades "
            "periodically: *beats*. It is what a piano tuner listens for — "
            "two strings nearly in tune produce a slow throb in loudness that "
            "vanishes as they come into tune — and it is what a child on a "
            "swing feels when pushed at not quite the right rhythm."
        ),
        Worked(
            "Beats",
            "Solve x'' + 100x = cos 9t from rest.",
            (
                Step("ω₀ = 10 and ω = 9, so A = 1/(100 − 81) = 1/19, and "
                     "starting from rest the complementary part is "
                     "−cos(10t)/19.",
                     r"x = \frac{\cos 9t - \cos 10t}{19}"),
                Step("By the identity, x = (2/19) sin(t/2) sin(19t/2): a fast "
                     "oscillation at 9.5 rad/s inside an envelope that rises "
                     "and falls with period 4π ≈ 12.6 s."),
            ),
            equation="y'' + 100*y = cos(9*t)", conditions="y(0) = 0, y'(0) = 0",
            answer="(cos(9*t) - cos(10*t))/19",
            answer_latex=r"x(t) = \frac{\cos 9t - \cos 10t}{19}",
        ),
        Plot(
            "Beats",
            "x = (cos 9t − cos 10t)/19 with its slow envelope ±(2/19)sin(t/2). "
            "The fast oscillation builds up as the forcing and the natural "
            "vibration fall into step, then dies away as they drift out of "
            "step, over and over.",
            (Curve("(cos(9*t) - cos(10*t))/19", "x(t)"),
             Curve("2*sin(t/2)/19", "envelope"),
             Curve("-2*sin(t/2)/19", "")),
            t=(0.0, 25.0),
        ),
    )),
    Section("Pure resonance", (
        Para(
            "At ω = ω₀ exactly, formula (2) divides by zero, and that is the "
            "modification rule of Unit 3 speaking: the forcing is itself a "
            "free vibration, so the trial must be multiplied by t. The "
            "response then grows linearly without bound. Physically, the "
            "force is always pushing in the direction the mass is already "
            "moving, so every cycle adds energy and none is removed."
        ),
        Box(
            "theorem", "Resonance",
            "For x'' + ω₀²x = (F₀/m) sin ω₀t or cos ω₀t, the particular solution "
            "is t times a sinusoid at ω₀, with amplitude growing like "
            "F₀t/(2mω₀).",
            r"x_p = \frac{F_0}{2 m \omega_0}\, t \sin\omega_0 t "
            r"\quad\text{for}\quad F_0\cos\omega_0 t",
        ),
        Worked(
            "Resonance from rest",
            "Solve x'' + 4x = 2 sin 2t from rest.",
            (
                Step("ω₀ = ω = 2, so try t(A cos 2t + B sin 2t). The t-terms "
                     "cancel, leaving −4A sin 2t + 4B cos 2t = 2 sin 2t: A = −1/2 "
                     "and B = 0.",
                     r"x_p = -\frac{t}{2}\cos 2t"),
                Step("Adding c₁cos 2t + c₂sin 2t: x(0) = c₁ = 0, and "
                     "x'(0) = −1/2 + 2c₂ = 0 gives c₂ = 1/4."),
            ),
            equation="y'' + 4*y = 2*sin(2*t)", conditions="y(0) = 0, y'(0) = 0",
            answer="-t*cos(2*t)/2 + sin(2*t)/4",
            answer_latex=r"x(t) = -\frac{t}{2}\cos 2t + \frac{1}{4}\sin 2t",
        ),
        Plot(
            "Resonance, and beats as its approach",
            "The resonant response −(t/2)cos 2t + sin(2t)/4 grows without "
            "bound. Beats are resonance seen from nearby: as ω → ω₀ the beat "
            "period grows without limit, and the first swell of the envelope "
            "becomes this unending linear growth.",
            (Curve("-t*cos(2*t)/2 + sin(2*t)/4", "x(t)"),
             Curve("t/2", "envelope t/2"), Curve("-t/2", "")),
            t=(0.0, 20.0),
        ),
    )),
    Section("Damped forcing and the steady state", (
        Para(
            "With damping, the trial must include both cos ωt and sin ωt, "
            "because the damping term turns one into the other. Substituting "
            "and matching coefficients gives two linear equations, and the "
            "steady-state response is a sinusoid at the forcing frequency, "
            "lagging behind the force by a phase angle α and with an "
            "amplitude C(ω) that depends on how close ω is to ω₀."
        ),
        Box(
            "theorem", "Steady-state response",
            "For mx'' + cx' + kx = F₀cos ωt with c > 0, the steady-state "
            "response is x_p = C cos(ωt − α), with the amplitude below and a "
            "phase lag α between 0 and π given by tan α = cω/(k − mω²).",
            r"C(\omega) = \frac{F_0}{\sqrt{(k - m\omega^{2})^{2} + (c\omega)^{2}}}",
        ),
        Worked(
            "Transient and steady state",
            "Solve x'' + 2x' + 5x = 10 cos t from rest.",
            (
                Step("Try A cos t + B sin t. Matching: 4A + 2B = 10 and "
                     "4B − 2A = 0, so A = 2B, then B = 1 and A = 2. The steady "
                     "state is 2 cos t + sin t, of amplitude √5.",
                     r"x_p = 2\cos t + \sin t"),
                Step("The complementary function is e^(−t)(c₁cos 2t + c₂sin 2t). "
                     "From rest: 2 + c₁ = 0, so c₁ = −2, and 1 − c₁ + 2c₂ = 0, "
                     "so c₂ = −3/2."),
            ),
            equation="y'' + 2*y' + 5*y = 10*cos(t)", conditions="y(0) = 0, y'(0) = 0",
            answer="2*cos(t) + sin(t) - exp(-t)*(2*cos(2*t) + 3*sin(2*t)/2)",
            answer_latex=r"x(t) = 2\cos t + \sin t - e^{-t}\left(2\cos 2t + "
                         r"\frac{3}{2}\sin 2t\right)",
        ),
        Plot(
            "The transient dies, the steady state remains",
            "The full solution from rest and the steady state 2 cos t + sin t. "
            "By t ≈ 4 the transient, which decays like e^(−t), is invisible, "
            "and the motion is the steady response alone — the same whatever "
            "the initial conditions were.",
            (Curve("2*cos(t) + sin(t) - exp(-t)*(2*cos(2*t) + 1.5*sin(2*t))",
                   "x(t)"),
             Curve("2*cos(t) + sin(t)", "steady state")),
            t=(0.0, 15.0),
        ),
    )),
    Section("The frequency response", (
        Para(
            "The amplitude formula C(ω) is the most useful single result of "
            "the unit, because it answers a design question directly: how "
            "strongly does this system respond to forcing at each frequency? "
            "Plotted against ω it is the *frequency response*. For small "
            "damping it has a sharp peak near ω₀; for large damping the peak "
            "flattens and eventually disappears."
        ),
        Plot(
            "Amplitude against forcing frequency",
            "C(ω) = 1/√((4 − ω²)² + (cω)²) for a system with m = 1, k = 4 "
            "(so ω₀ = 2) and F₀ = 1, for damping c = 0.25, 0.5 and 1. The "
            "lighter the damping, the taller and narrower the peak: at "
            "c = 0.25 the response at resonance is about eight times the "
            "static deflection 1/k = 0.25.",
            (Curve("1/sqrt((4 - t**2)**2 + (0.25*t)**2)", "c = 0.25"),
             Curve("1/sqrt((4 - t**2)**2 + (0.5*t)**2)", "c = 0.5"),
             Curve("1/sqrt((4 - t**2)**2 + (1.0*t)**2)", "c = 1")),
            t=(0.0, 4.0), xlabel="forcing frequency ω", ylabel="amplitude C",
            ylim=(0.0, 2.2),
        ),
        Para(
            "Setting the derivative of C(ω) to zero shows the peak is at "
            "ω_max = √(ω₀² − c²/(2m²)), slightly below ω₀, and exists only when "
            "c² < 2mk. This is *practical resonance*. At the peak, the "
            "amplitude is roughly Q times the static deflection F₀/k, where Q "
            "is the quality factor of the last lesson — which is why lightly "
            "damped structures are so dangerous to force near their natural "
            "frequency, and why a radio can pick one station out of many."
        ),
        Figure("resonance",
               "Sweep the forcing frequency and watch the response in time "
               "and the frequency-response curve together, with the damping "
               "on a slider."),
        Para(
            "For quick estimates, three facts about the curve are enough. At "
            "very low frequency the response is the static deflection F₀/k: "
            "the spring alone resists, as if the force were constant. At very "
            "high frequency it falls off like F₀/(mω²): inertia alone "
            "resists. Near resonance, for light damping, the peak height is "
            "about Q·F₀/k and its width — the band of frequencies over which "
            "the response exceeds 1/√2 of its peak — is about ω₀/Q. A system "
            "with Q = 100 therefore responds a hundred times more strongly at "
            "resonance than to a steady push, but only within a band 1% of "
            "its natural frequency wide."
        ),
        Para(
            "Measuring a frequency response is also how natural frequencies "
            "and damping are found in practice. Shake a structure over a "
            "range of frequencies, record the amplitude and phase of its "
            "response, and read ω₀ from where the phase passes π/2 and Q from "
            "the sharpness of the peak. Engineers do this to aircraft wings, "
            "bridges and car bodies before they are used, precisely to find "
            "the frequencies that must never be driven."
        ),
    )),
    Section("Phase", (
        Para(
            "The phase lag α says when the response peaks relative to the "
            "force. At low frequency α ≈ 0: the mass follows the force "
            "slowly, as if the spring alone were resisting. At resonance "
            "α = π/2: the displacement lags the force by a quarter cycle, "
            "which puts the *velocity* exactly in step with the force, and "
            "that is why energy flows in fastest there. At high frequency "
            "α → π: the mass moves opposite to the force, its inertia "
            "dominating."
        ),
        Para(
            "In the worked example, tan α = cω/(k − mω²) = 2/4 = 1/2, so the "
            "steady state lags the force cos t by arctan(1/2) ≈ 0.46 rad, "
            "which at ω = 1 is a delay of 0.46 time units. Written as "
            "C cos(t − α), 2 cos t + sin t has C = √5 and α = arctan(1/2), "
            "matching. The phase is often more informative experimentally than "
            "the amplitude, because it passes through π/2 exactly at the "
            "natural frequency whatever the damping."
        ),
    )),
    Section("Where the energy goes", (
        Para(
            "In the steady state the amplitude is constant, so the energy "
            "stored in the spring and the moving mass is the same at the "
            "start of every cycle. The energy the force puts in during a "
            "cycle must therefore equal the energy the damper takes out. The "
            "damper dissipates power cx'², which averages to (1/2)cω²C² over a "
            "cycle, so the force must supply exactly that much on average."
        ),
        Display(r"\overline{P} = \frac{1}{2} c\, \omega^{2} C^{2}"),
        Para(
            "This explains the shape of the frequency response from a "
            "different angle. A force can put in energy only when it pushes "
            "in the direction of motion, and it does that most effectively "
            "when it is in step with the *velocity* — which is what the phase "
            "lag of π/2 at resonance arranges. Away from resonance the force "
            "spends part of each cycle pushing against the motion, taking "
            "back some of what it gave, and the net transfer is smaller. With "
            "no damping at all there is nowhere for the energy to go at "
            "resonance, and it accumulates without limit, as the t in the "
            "resonant solution says."
        ),
    )),
    Section("Resonance in the world", (
        Para(
            "Resonance is useful as often as it is dangerous. A radio tuner "
            "is an electrical oscillator whose natural frequency is adjusted "
            "to match one station, so that station alone is amplified. A "
            "microwave oven heats food by driving water molecules near a "
            "frequency they absorb strongly. A musical instrument's body "
            "resonates to make a string's vibration audible. In each case a "
            "high quality factor is the goal, because it makes the response "
            "both large and selective."
        ),
        Para(
            "The dangers are just as real, though the famous stories need "
            "telling carefully. London's Millennium Bridge swayed alarmingly "
            "when it opened in 2000, because the footfalls of a crowd "
            "synchronised with the bridge's lateral motion and drove it near "
            "a natural frequency; it was closed and fitted with dampers. The "
            "Tacoma Narrows Bridge collapse of 1940 is often cited as "
            "resonance, but the wind that destroyed it was steady, not "
            "periodic, and the mechanism was aeroelastic flutter, a "
            "self-excited instability — closer to the negative damping of a "
            "growing oscillation than to forced resonance. Machines with "
            "rotating parts, such as a washing machine on its spin cycle, "
            "pass through resonance as they speed up, which is why they "
            "shudder briefly and then settle."
        ),
    )),
    Section("Vibration isolation", (
        Para(
            "The frequency response also tells an engineer how to *prevent* "
            "vibration from being transmitted. Mount a machine that shakes at "
            "frequency ω on springs of natural frequency ω₀. For ω much "
            "larger than ω₀ the amplitude C(ω) is small, roughly F₀/(mω²), "
            "because the mass's inertia stops it following fast forcing. "
            "Working out the force passed through the springs to the floor "
            "shows that isolation begins only when ω exceeds √2·ω₀; below "
            "that, the mounting makes things worse."
        ),
        Para(
            "So the design rule is to make the mounting's natural frequency "
            "low — soft springs, heavy base — well below the frequencies to be "
            "isolated. The same principle protects buildings in earthquake "
            "zones, which are set on flexible bearings that give the building "
            "a natural frequency far below the dominant frequencies of ground "
            "shaking, and it is why sensitive instruments sit on heavy tables "
            "floating on air springs."
        ),
    )),
    Section("Forcing that is periodic but not a sinusoid", (
        Para(
            "Real forcing is rarely a pure cosine: an engine's impulses, the "
            "bumps of a road with regularly spaced joints, a square-wave "
            "voltage. But any reasonable periodic function of period T can be "
            "written as a sum of sinusoids at frequencies 2π/T, 4π/T, 6π/T, "
            "… — its Fourier series — and because the equation is linear the "
            "steady-state response is the sum of the responses to each "
            "sinusoid, each scaled by C at its own frequency."
        ),
        Para(
            "That has a consequence worth knowing. Even when the fundamental "
            "frequency of the forcing is far below ω₀, one of its harmonics "
            "may land close to ω₀, and the system will then respond strongly "
            "at that harmonic. A forcing with period three times the natural "
            "period can still excite resonance through its third harmonic. "
            "The Laplace-transform unit develops tools for forcing that is "
            "switched on and off, which is the non-periodic version of the "
            "same idea."
        ),
    )),
    Section("Common errors", (
        Para(
            "With damping, the trial must contain both cos ωt and sin ωt even "
            "when the forcing has only one of them; leaving one out produces "
            "two equations that cannot both be satisfied. The resonance "
            "modification applies only without damping: with c > 0 the "
            "roots have negative real part, iω is never a root, and no factor "
            "of t is ever needed. And the steady state must not be confused "
            "with the full solution when initial conditions are asked for — "
            "the transient carries the initial conditions and must be "
            "included, even though it dies away."
        ),
        Para(
            "In reading answers, keep the frequency the response oscillates "
            "at separate from the frequency at which its amplitude peaks. "
            "The steady state always oscillates at the forcing frequency ω, "
            "never at ω₀ or ω₁; the natural frequency determines only *how "
            "large* the response is, through C(ω). The transient oscillates "
            "at the damped natural frequency ω₁, which is why the early "
            "motion can look like a mixture of two rhythms."
        ),
    )),
    Section("Summary", (
        Para(
            "A forced oscillator mx'' + cx' + kx = F₀cos ωt responds with the "
            "free vibration of the last lesson plus a particular solution at "
            "the forcing frequency. Undamped and off resonance, the two "
            "coexist for ever, and near resonance they produce beats. At "
            "resonance, ω = ω₀, the response grows without bound. With "
            "damping the free part is a transient that dies, leaving the "
            "steady state C cos(ωt − α) with C = F₀/√((k − mω²)² + (cω)²), "
            "peaking near ω₀ at about Q times the static deflection, and a "
            "phase lag that passes π/2 at the natural frequency. Design "
            "follows from that one curve: keep forcing away from ω₀, add "
            "damping where it cannot be kept away, and mount on soft springs "
            "to isolate what must not shake."
        ),
    )),
)


FREE = (
    Section("The mass–spring–damper", (
        Para(
            "A mass m hangs from a spring, or slides on a frictionless table "
            "attached to one. Pull it away from its resting position and let "
            "go, and it vibrates. The whole of this unit is about that "
            "picture, because it is the model for an astonishing range of "
            "things: a car on its suspension, a building swaying in the wind, "
            "a tuning fork, the atoms in a crystal, the current in a radio "
            "receiver. Anything that is pushed back towards equilibrium when "
            "disturbed, and that has inertia carrying it past, vibrates in "
            "the same way."
        ),
        Para(
            "Let x(t) be the displacement of the mass from equilibrium. Three "
            "forces act on it. The spring pushes back with force −kx, "
            "proportional to the displacement — Hooke's law, with k the "
            "spring constant. A damper, such as a dashpot or air resistance, "
            "resists motion with force −cx', proportional to the velocity. "
            "And any external force F(t) acts as given. Newton's second law "
            "adds them up."
        ),
        Display(r"m x'' + c x' + k x = F(t)", "1"),
        Box(
            "definition", "Free vibration",
            "Motion with no external force, F = 0: the system is set going by "
            "its initial displacement and velocity and then left alone. The "
            "motion is *undamped* if c = 0 and *damped* if c > 0.",
            r"m x'' + c x' + k x = 0",
        ),
        Para(
            "Equation (1) is a second-order linear equation with constant "
            "coefficients, so Unit 3 solves it completely. What this lesson "
            "adds is the physics: which of the three root cases corresponds "
            "to which kind of motion, what the constants mean, and how to "
            "read the frequency, the decay rate and the amplitude straight "
            "off the numbers m, c and k."
        ),
    )),
    Section("Vertical springs, and why gravity disappears", (
        Para(
            "A mass hanging from a vertical spring also feels its weight, mg, "
            "and it might seem that (1) needs an extra term. It does not, "
            "provided x is measured from the right place. Hanging at rest, "
            "the mass stretches the spring by a distance s at which the spring "
            "force balances the weight: ks = mg. If x is measured from that "
            "stretched equilibrium rather than from the spring's natural "
            "length, the spring force is −k(s + x) and the weight is +mg, and "
            "the two constant parts cancel exactly."
        ),
        Display(r"m x'' = mg - k(s + x) - c x' = -k x - c x' \quad "
                r"\text{since } ks = mg"),
        Para(
            "So gravity only moves the equilibrium; it does not change the "
            "vibration about it. That observation also gives the easiest way "
            "to measure k in practice. Hang a known mass, measure how far the "
            "spring stretches, and divide: k = mg/s. A 4 kg mass that "
            "stretches a spring 0.49 m gives k = 4 × 9.8/0.49 = 80 N/m, and "
            "then ω₀ = √(80/4) = √20 ≈ 4.47 rad/s, without ever setting the "
            "mass in motion."
        ),
        Box(
            "remark", "Units",
            "In SI units m is in kilograms, k in newtons per metre, c in "
            "newton-seconds per metre, and ω₀ = √(k/m) comes out in radians per "
            "second. The frequency in cycles per second (hertz) is ω₀/(2π), "
            "and the period 2π/ω₀. Mixing up angular frequency and frequency "
            "is an error by a factor of 2π, and an easy one to make.",
        ),
    )),
    Section("Undamped motion", (
        Para(
            "With no damping, mx'' + kx = 0. Dividing by m and writing "
            "ω₀² = k/m, the characteristic roots are ±iω₀, and every solution "
            "is a sinusoid of angular frequency ω₀. This is *simple harmonic "
            "motion*, and ω₀ is the *natural frequency* of the system — "
            "natural because it belongs to the system itself, not to how it "
            "was set going."
        ),
        Box(
            "theorem", "Simple harmonic motion",
            "The solution of mx'' + kx = 0 is a sinusoid of angular frequency "
            "ω₀ = √(k/m), with amplitude and phase fixed by the initial "
            "conditions. Its period is 2π/ω₀, whatever the amplitude.",
            r"x(t) = C\cos(\omega_0 t - \varphi), \qquad \omega_0 = "
            r"\sqrt{\frac{k}{m}}",
        ),
        Para(
            "Two consequences are worth stating plainly. A stiffer spring "
            "(larger k) vibrates faster, a heavier mass (larger m) more "
            "slowly, and the dependence is on the square root of their "
            "ratio: quadrupling the mass halves the frequency. And the period "
            "does not depend on the amplitude at all — a property called "
            "*isochronism*, which is why a spring-driven watch keeps time "
            "whether it is fully wound or nearly run down."
        ),
        Worked(
            "A mass on a spring",
            "A 2 kg mass on a spring with k = 50 N/m is displaced 0.1 m and "
            "given a velocity of 1 m/s. Find its motion, amplitude and "
            "period.",
            (
                Step("2x'' + 50x = 0, so ω₀ = √25 = 5 rad/s, and "
                     "x = c₁cos 5t + c₂sin 5t. The conditions give c₁ = 0.1 "
                     "and 5c₂ = 1, so c₂ = 0.2.",
                     r"x = 0.1\cos 5t + 0.2 \sin 5t"),
                Step("The amplitude is √(0.1² + 0.2²) = √0.05 ≈ 0.224 m, "
                     "larger than the initial displacement because the mass "
                     "was also moving. The period is 2π/5 ≈ 1.26 s.",
                     r"C = \sqrt{0.1^{2} + 0.2^{2}} \approx 0.224, \quad "
                     r"T = \frac{2\pi}{5} \approx 1.26"),
            ),
            equation="2*y'' + 50*y = 0", conditions="y(0) = 1/10, y'(0) = 1",
            answer="cos(5*t)/10 + sin(5*t)/5",
            answer_latex=r"x(t) = 0.1\cos 5t + 0.2\sin 5t",
        ),
        Worked(
            "A pendulum, linearised",
            "A pendulum of length 2.45 m (so g/L = 4 s⁻²) is released from rest "
            "at 0.1 rad. Using the small-angle approximation sin θ ≈ θ, find "
            "θ(t).",
            (
                Step("The pendulum equation θ'' + (g/L) sin θ = 0 becomes "
                     "θ'' + 4θ = 0 for small angles, simple harmonic with "
                     "ω₀ = 2 rad/s.",
                     r"\theta'' + 4\theta = 0"),
                Step("Released from rest: θ = 0.1 cos 2t, with period π ≈ 3.14 s. "
                     "The approximation is good while θ stays small; Unit 8 "
                     "shows what happens when it does not."),
            ),
            equation="y'' + 4*y = 0", conditions="y(0) = 1/10, y'(0) = 0",
            answer="cos(2*t)/10", answer_latex=r"\theta(t) = 0.1\cos 2t",
        ),
    )),
    Section("Energy", (
        Para(
            "An undamped spring conserves energy, and seeing this directly "
            "gives a second view of the motion. Multiply mx'' + kx = 0 by x' "
            "and recognise both terms as derivatives: mx'x'' is the derivative "
            "of (1/2)mx'², and kxx' of (1/2)kx². So their sum — kinetic plus "
            "potential energy — is constant."
        ),
        Display(r"E = \frac{1}{2} m x'^{2} + \frac{1}{2} k x^{2}, \qquad "
                r"\frac{dE}{dt} = x'(m x'' + k x) = 0", "2"),
        Para(
            "Energy explains the amplitude formula without any trigonometry. "
            "At the extreme of the swing the velocity is zero and all the "
            "energy is in the spring, (1/2)kC²; initially it is "
            "(1/2)mv₀² + (1/2)kx₀². Setting them equal gives "
            "C² = x₀² + (m/k)v₀², which for the example is 0.01 + 0.04, as "
            "found. With damping the same calculation gives "
            "dE/dt = −cx'², so energy drains away at a rate proportional to the "
            "square of the speed, and the damper is where it goes, as heat."
        ),
        Para(
            "The energy picture also explains why damped oscillations decay "
            "at a steady *rate* rather than stopping at a definite moment. "
            "Energy is lost fastest when the mass moves fastest, near "
            "equilibrium, and the loss per cycle is proportional to the energy "
            "the cycle has. A quantity whose loss is proportional to itself "
            "decays exponentially, so the energy falls like e^(−ct/m) and the "
            "amplitude, which goes like the square root of the energy, like "
            "e^(−ct/(2m)) — exactly the envelope the characteristic roots give. "
            "Two completely different routes, one through forces and one "
            "through energy, arrive at the same decay rate, which is a good "
            "sign that both are right."
        ),
        Para(
            "In the phase plane of position against velocity, the energy "
            "picture becomes geometry. Undamped motion traces an ellipse, a "
            "level curve of E; damped motion crosses the ellipses inwards, "
            "spiralling to the origin. Unit 6 draws these portraits for "
            "linear systems in general, and Unit 8 uses the same energy "
            "argument to study the pendulum at large amplitudes."
        ),
    )),
    Section("Damping: three regimes", (
        Para(
            "With damping, the characteristic equation mr² + cr + k = 0 has "
            "roots r = (−c ± √(c² − 4mk))/(2m), and the sign of the "
            "discriminant c² − 4mk sorts every damped spring into one of "
            "three regimes. The dividing value of the damping is the *critical "
            "damping* c_cr = 2√(mk), and the ratio ζ = c/c_cr, the *damping "
            "ratio*, is the single number that describes a system's "
            "character."
        ),
        Box(
            "definition", "The damping regimes",
            "A damped system is *underdamped* if c² < 4mk (ζ < 1): complex "
            "roots, decaying oscillation. *Critically damped* if c² = 4mk "
            "(ζ = 1): a repeated real root. *Overdamped* if c² > 4mk (ζ > 1): "
            "two distinct negative real roots, no oscillation.",
            r"\zeta = \frac{c}{2\sqrt{m k}}",
        ),
        Figure("damping",
               "Drag the damping through its critical value and watch the "
               "motion change from a decaying oscillation, through the "
               "fastest non-oscillating return, to a slow creep."),
    )),
    Section("Underdamped motion", (
        Para(
            "For c² < 4mk the roots are −p ± iω₁ with p = c/(2m) and "
            "ω₁ = √(4mk − c²)/(2m). The motion is an oscillation at the "
            "*damped* frequency ω₁, inside an envelope e^(−pt). Note that "
            "ω₁ < ω₀: damping slows the oscillation down as well as shrinking "
            "it, though for light damping the change is tiny — ω₁ = "
            "ω₀√(1 − ζ²)."
        ),
        Display(r"x(t) = C e^{-p t}\cos(\omega_1 t - \varphi), \qquad "
                r"\omega_1 = \omega_0\sqrt{1 - \zeta^{2}}", "3"),
        Worked(
            "A decaying oscillation",
            "Solve x'' + 2x' + 10x = 0 with x(0) = 1, x'(0) = 0.",
            (
                Step("r² + 2r + 10 = 0 gives r = −1 ± 3i: p = 1 and ω₁ = 3. "
                     "(Here ω₀ = √10 ≈ 3.16 and ζ = 2/(2√10) ≈ 0.32.)",
                     r"x = e^{-t}(c_1\cos 3t + c_2\sin 3t)"),
                Step("x(0) = c₁ = 1; x'(0) = −c₁ + 3c₂ = 0 gives c₂ = 1/3."),
            ),
            equation="y'' + 2*y' + 10*y = 0", conditions="y(0) = 1, y'(0) = 0",
            answer="exp(-t)*(cos(3*t) + sin(3*t)/3)",
            answer_latex=r"x(t) = e^{-t}\left(\cos 3t + \frac{1}{3}\sin 3t\right)",
        ),
        Para(
            "A convenient way to measure damping in an experiment is to "
            "compare successive peaks. Each period 2π/ω₁ multiplies the "
            "amplitude by e^(−2πp/ω₁), so the *logarithmic decrement* "
            "δ = ln(xₙ/xₙ₊₁) = 2πp/ω₁ can be read off a recording, and p "
            "follows. In the example, δ = 2π/3 ≈ 2.09: each peak is about "
            "e^(−2.09) ≈ 0.12 of the one before, so the oscillation is nearly "
            "gone after two swings."
        ),
        Plot(
            "Underdamped motion inside its envelope",
            "x = e^(−t)(cos 3t + sin 3t/3) with the envelope ±√(10)/3 · e^(−t). "
            "The oscillation keeps its period 2π/3 while its size shrinks by a "
            "factor e every unit of time — a steady rhythm and a steady fade, "
            "set by the imaginary and real parts of the roots.",
            (Curve("exp(-t)*(cos(3*t) + sin(3*t)/3)", "x(t)"),
             Curve("sqrt(10)*exp(-t)/3", "envelope"),
             Curve("-sqrt(10)*exp(-t)/3", "")),
            t=(0.0, 5.0),
        ),
    )),
    Section("Light damping and the quality factor", (
        Para(
            "Many systems that matter — a tuning fork, a pendulum clock, a "
            "quartz crystal, a guitar string — are very lightly damped, with "
            "ζ far below 1. Then ω₁ is almost exactly ω₀, and the only visible "
            "effect of damping is a slow decay of the amplitude over many "
            "cycles. A single number describes how slow: the *quality factor* "
            "Q = 1/(2ζ), roughly the number of radians of oscillation over "
            "which the energy falls by a factor e."
        ),
        Display(r"Q = \frac{1}{2\zeta} = \frac{\sqrt{m k}}{c}"),
        Para(
            "A tuning fork has Q in the thousands and rings for seconds; a "
            "quartz watch crystal has Q around ten thousand or more, which is "
            "part of why it keeps such good time; a car's suspension has Q "
            "below 1, by design. The quality factor will matter even more in "
            "the next lesson, because it also measures how sharply a system "
            "responds to forcing near its natural frequency — a high-Q system "
            "is both slow to stop ringing and extremely selective about what "
            "sets it ringing."
        ),
    )),
    Section("Common errors", (
        Para(
            "Most errors in vibration problems are errors of translation "
            "rather than of solving. Using a weight in newtons where a mass in "
            "kilograms is needed, or the reverse, changes ω₀ by a factor of "
            "√9.8. Taking the damping coefficient from a problem that states "
            "the damping *force* at some speed without dividing by that speed "
            "is another. And measuring the displacement from the spring's "
            "natural length for a vertical spring, then forgetting the "
            "gravity term, gives an equation whose equilibrium is in the "
            "wrong place."
        ),
        Para(
            "In the solving itself, the usual slips are the ones of Unit 3: a "
            "wrong root case (check the sign of c² − 4mk before anything "
            "else), a missing t in the critically damped case, and the "
            "product rule when differentiating e^(−pt)cos ω₁t to apply the "
            "initial velocity. The regime can always be predicted from ζ "
            "before solving, and a solution that oscillates when ζ > 1, or "
            "does not when ζ < 1, is wrong whatever the algebra says."
        ),
    )),
    Section("Critically damped and overdamped motion", (
        Worked(
            "Critical damping",
            "Solve x'' + 6x' + 9x = 0 with x(0) = 1, x'(0) = 0.",
            (
                Step("r² + 6r + 9 = (r + 3)²: a double root −3, and c² = 36 = "
                     "4mk exactly.",
                     r"x = (c_1 + c_2 t)\, e^{-3t}"),
                Step("x(0) = c₁ = 1; x'(0) = c₂ − 3c₁ = 0 gives c₂ = 3."),
            ),
            equation="y'' + 6*y' + 9*y = 0", conditions="y(0) = 1, y'(0) = 0",
            answer="(1 + 3*t)*exp(-3*t)", answer_latex=r"x(t) = (1 + 3t)\, e^{-3t}",
        ),
        Worked(
            "Overdamping",
            "Solve x'' + 10x' + 16x = 0 with x(0) = 1, x'(0) = 0.",
            (
                Step("r² + 10r + 16 = (r + 2)(r + 8): roots −2 and −8.",
                     r"x = c_1 e^{-2t} + c_2 e^{-8t}"),
                Step("c₁ + c₂ = 1 and −2c₁ − 8c₂ = 0, so c₁ = 4/3 and "
                     "c₂ = −1/3. The slow root −2 dominates after a short time."),
            ),
            equation="y'' + 10*y' + 16*y = 0", conditions="y(0) = 1, y'(0) = 0",
            answer="4*exp(-2*t)/3 - exp(-8*t)/3",
            answer_latex=r"x(t) = \frac{4}{3}e^{-2t} - \frac{1}{3}e^{-8t}",
        ),
        Plot(
            "The three regimes, from the same release",
            "x'' + cx' + 9x = 0 released from x = 1 at rest, with c = 1 "
            "(underdamped), c = 6 (critical) and c = 15 (overdamped). The "
            "critically damped mass returns fastest without overshooting; "
            "the overdamped one creeps back, held up by its own damping; the "
            "underdamped one overshoots and rings.",
            (Curve("exp(-t/2)*(cos(sqrt(35)*t/2) + sin(sqrt(35)*t/2)/sqrt(35))",
                   "c = 1"),
             Curve("(1 + 3*t)*exp(-3*t)", "c = 6, critical"),
             Curve("((15 + sqrt(189))/(2*sqrt(189)))*exp((-15 + sqrt(189))*t/2)"
                   " + ((sqrt(189) - 15)/(2*sqrt(189)))*exp((-15 - sqrt(189))*t/2)",
                   "c = 15")),
            t=(0.0, 6.0), ylim=(-0.8, 1.05),
        ),
        Para(
            "Critical damping has a claim to be the *best* damping for many "
            "purposes: it returns to equilibrium faster than any overdamped "
            "setting and without the overshoot of an underdamped one. Door "
            "closers, the needles of analogue meters and a car's shock "
            "absorbers are designed near it. It is not the fastest to "
            "*first reach* equilibrium — an underdamped system gets there "
            "sooner, but overshoots — and in practice a damping ratio a "
            "little below 1 is often chosen, trading a small overshoot for "
            "speed."
        ),
        Box(
            "warning", "More damping is not always faster",
            "Increasing the damping beyond critical makes the return "
            "*slower*, not faster, because the slow root −p + √(p² − ω₀²) "
            "approaches zero as c grows. A heavily overdamped door takes a "
            "long time to close. The fastest non-oscillating return is at "
            "ζ = 1 exactly.",
        ),
    )),
    Section("From measurements to motion", (
        Para(
            "Put the pieces together on one realistic problem, of the kind an "
            "exam sets: the constants are not handed over, they have to be "
            "extracted from a description, and the regime has to be decided "
            "before the equation is solved."
        ),
        Worked(
            "A measured system",
            "A 4 kg mass stretches a spring 0.49 m. A dashpot provides 16 N "
            "of resistance for each m/s of speed. The mass is pulled 0.5 m "
            "below equilibrium and released. Find its motion.",
            (
                Step("k = mg/s = 4 × 9.8/0.49 = 80 N/m and c = 16 N·s/m, so "
                     "4x'' + 16x' + 80x = 0. The damping ratio is "
                     "16/(2√(4 × 80)) ≈ 0.447: underdamped.",
                     r"x'' + 4x' + 20x = 0, \qquad \zeta \approx 0.447"),
                Step("The roots are −2 ± 4i, so x = e^(−2t)(c₁cos 4t + c₂sin 4t). "
                     "Released from 0.5 m at rest: c₁ = 0.5, and "
                     "−2c₁ + 4c₂ = 0 gives c₂ = 0.25.",
                     r"x = e^{-2t}\left(0.5\cos 4t + 0.25\sin 4t\right)"),
                Step("The damped frequency is 4 rad/s, a little below the "
                     "natural √20 ≈ 4.47, exactly ω₀√(1 − ζ²). The envelope "
                     "halves every ln 2/2 ≈ 0.35 s."),
            ),
            equation="4*y'' + 16*y' + 80*y = 0", conditions="y(0) = 1/2, y'(0) = 0",
            answer="exp(-2*t)*(cos(4*t)/2 + sin(4*t)/4)",
            answer_latex=r"x(t) = e^{-2t}\left(\frac{1}{2}\cos 4t + "
                         r"\frac{1}{4}\sin 4t\right)",
        ),
        Para(
            "Real damping is rarely exactly proportional to velocity. Dry "
            "friction between sliding surfaces is roughly constant in size, "
            "air drag grows like the square of the speed, and the internal "
            "friction of a metal spring depends on how fast it is flexed in a "
            "complicated way. The linear model cx' is used because it is "
            "solvable, because it is accurate for fluid dampers such as a "
            "car's shock absorber, and because for small vibrations most kinds "
            "of damping behave approximately linearly. When a measured decay "
            "is not exponential — equal *amounts* lost per cycle rather than "
            "equal *fractions* — that is the sign of dry friction, and a "
            "different model is needed."
        ),
    )),
    Section("Reading a vibration from its equation", (
        Para(
            "With practice the behaviour of mx'' + cx' + kx = 0 can be read "
            "without solving anything. The natural frequency is √(k/m). The "
            "damping ratio is c/(2√(mk)), and it says whether the motion "
            "oscillates. If it does, the envelope decays like e^(−ct/(2m)), "
            "with time constant 2m/c, and the damped frequency is "
            "ω₀√(1 − ζ²). If it does not, the slowest decay rate is the "
            "smaller root in absolute value. These few numbers are what an "
            "engineer specifying a suspension, or a physicist designing an "
            "instrument, actually works with."
        ),
        Para(
            "They also make clear which physical changes do what. Adding mass "
            "lowers the natural frequency and the damping ratio together — a "
            "loaded car wallows more than an empty one. Stiffening the spring "
            "raises the frequency and lowers the damping ratio. Only the "
            "damper changes ζ without changing ω₀, which is why it is the "
            "component adjusted to tune a system's response."
        ),
    )),
    Section("Summary", (
        Para(
            "A mass on a spring with damping obeys mx'' + cx' + kx = 0. "
            "Undamped, it performs simple harmonic motion at the natural "
            "frequency ω₀ = √(k/m), with an amplitude fixed by the initial "
            "energy and a period independent of amplitude. Damped, its "
            "behaviour depends on the damping ratio ζ = c/(2√(mk)): below 1 it "
            "oscillates at ω₀√(1 − ζ²) inside a decaying envelope e^(−ct/2m); at "
            "1 it returns fastest without overshoot; above 1 it creeps back "
            "without oscillating. Energy (1/2)mx'² + (1/2)kx² is conserved "
            "without damping and drains at rate cx'² with it. The next lesson "
            "adds the external force F(t)."
        ),
    )),
)
