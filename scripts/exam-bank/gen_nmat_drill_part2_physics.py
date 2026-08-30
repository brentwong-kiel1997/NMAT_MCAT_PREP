#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/drill/part2-physics.yml (25 practice drills).

Practice-only companion to part2-physics.yml: standalone MCQs, no passages, no
mock-blueprint role (drill/ files are tagged _drill by the loader). Angles the
main bank does not drill: energy methods, Lenz-law reasoning, second-order
circuit and thermodynamic questions, and biological-flavoured scenario items.

Authoring form is (stem, correct_text, [(wrong_text, error_note) x 3], chapter).
A fixed balanced key pattern places the correct choice; the three wrong choices
fill the remaining letters in order, so an error note can never land on the
answer letter.
"""
import os
from collections import Counter

import yaml

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/drill/part2-physics.yml"

# 25 slots -> A:6 B:7 C:6 D:6
KEYS = ["A", "B", "C", "D", "D", "A", "B", "C",
        "C", "D", "A", "B", "B", "C", "D", "A",
        "A", "B", "C", "D", "D", "A", "B", "C",
        "B"]

C4A = "4a-motion-forces-work-energy-equilibrium"
C4B = "4b-fluids-for-circulation-and-gas-exchange"
C4C = "4c-electrochemistry-and-electrical-circuits"
C4D = "4d-light-and-sound-interacting-with-matter"
EM = "electricity-and-magnetism"
MECH = "mechanics"
MOD = "modern-physics"
THERMO = "thermodynamics"
VWO = "vibrations-waves-and-optics"

ITEMS = [
    ("A 0.20-kg pendulum bob is released from rest 0.20 m above the lowest point of "
     "its swing. Ignoring air resistance (g = 9.8 m/s^2), what is its speed at the "
     "lowest point?",
     "2.0 m/s",
     [("1.4 m/s", "used sqrt(gh) instead of sqrt(2gh), dropping the factor of 2"),
      ("3.9 m/s", "reported 2gh = 3.9 directly, forgetting the square root"),
      ("1.0 m/s", "halved the energy drop (gh/2 under the root) instead of doubling it")],
     C4A),

    ("A 0.20-kg ball is whirled in a horizontal circle of radius 0.80 m at a steady "
     "4.0 m/s. What is the tension in the string supplying the centripetal force?",
     "4.0 N",
     [("3.2 N", "used mv^2 as the force and never divided by the radius"),
      ("1.0 N", "used mv/r instead of mv^2/r"),
      ("0.64 N", "multiplied by the radius instead of dividing by it (m v r)")],
     C4A),

    ("A uniform 400-N beam 4.0 m long is hinged to a wall and held horizontal by a "
     "vertical cable attached to its far end. What is the cable tension?",
     "200 N",
     [("400 N", "placed the beam's whole weight at the far end instead of at its midpoint"),
      ("800 N", "used W x L for the weight's torque, omitting the factor of 1/2"),
      ("0 N", "assumed the hinge carries everything, forgetting the beam would rotate about it")],
     C4A),

    ("A 0.10-kg ball strikes a wall at 10 m/s and rebounds along the same line at "
     "6.0 m/s, staying in contact for 0.050 s. What average force does the wall "
     "exert on the ball?",
     "32 N",
     [("1.6 N", "reported the impulse m(dv) = 1.6 N.s as if it were the force"),
      ("8.0 N", "subtracted the speeds (10 - 6.0) instead of adding them for a reversal"),
      ("320 N", "slipped a decimal in the contact time (0.0050 s)")],
     MECH),

    ("A 1000-kg car travelling at 20 m/s brakes to a stop with a steady friction "
     "force of 5000 N. How far does it travel while stopping?",
     "40 m",
     [("80 m", "used mv^2 instead of 1/2 mv^2 for the kinetic energy"),
      ("0.040 m", "inserted the braking force directly as the deceleration"),
      ("4.0 m", "dropped a factor of 10 from the kinetic energy (20,000 J)")],
     MECH),

    ("In a hydraulic lift a 150-N force is applied to a 0.0030-m^2 piston. What "
     "force does the 0.30-m^2 output piston exert?",
     "15,000 N",
     [("150 N", "assumed force itself is transmitted; Pascal's law transmits pressure"),
      ("1500 N", "slipped a decimal place in the piston area ratio of 100"),
      ("15 N", "inverted the area ratio, dividing by 100 instead of multiplying")],
     C4B),

    ("A block of density 600 kg/m^3 floats in water of density 1000 kg/m^3. What "
     "fraction of the block is submerged?",
     "60%",
     [("40%", "reported the fraction above the surface instead of below it"),
      ("167%", "inverted the density ratio (1000/600)"),
      ("100%", "assumed a floating body is fully immersed, ignoring Archimedes' condition")],
     C4B),

    ("A small hole sits 5.0 m below the water line of a large open tank. What is "
     "the efflux speed of the water? (g = 9.8 m/s^2)",
     "9.9 m/s",
     [("98 m/s", "reported 2gh = 98 directly, omitting the square root"),
      ("7.0 m/s", "used gh instead of 2gh under the root"),
      ("5.0 m/s", "set the speed equal to the depth rather than to sqrt(2gh)")],
     C4B),

    ("Two glass capillary tubes of inner radii 0.50 mm and 2.0 mm are dipped in the "
     "same water. How do the rises compare?",
     "The 0.50-mm tube rises 4 times higher, since height varies inversely with radius",
     [("The 2.0-mm tube rises 4 times higher, since it can carry more water",
       "judged by volume rather than by the balance of surface tension and weight"),
      ("Both tubes rise the same height, since capillary rise depends only on the liquid",
       "dropped the tube radius, which the Jurin-law expression contains"),
      ("The 0.50-mm tube rises 16 times higher, since height varies as 1/r^2",
       "squared the radius where the inverse is linear")],
     C4B),

    ("A battery of emf 12 V and internal resistance 0.50 ohm drives a 5.5-ohm "
     "resistor. What is the terminal voltage?",
     "11 V",
     [("12 V", "treated the battery as ideal and ignored the internal drop"),
      ("1.0 V", "subtracted the external resistor's 11-V drop instead of the internal one"),
      ("13 V", "added the internal drop to the emf instead of subtracting it")],
     C4C),

    ("A 4.0-microF capacitor is connected across a 12-V battery. What charge "
     "collects on each plate?",
     "48 microC",
     [("3.0 microC", "divided capacitance by voltage (C/V) instead of multiplying"),
      ("0.33 microC", "divided voltage by capacitance (V/C)"),
      ("48 mC", "slipped the micro-to-milli prefix by three orders of magnitude")],
     C4C),

    ("A copper wire has resistance 2.0 ohm. A second wire of the same material has "
     "twice the length and half the diameter. What is its resistance?",
     "16 ohm",
     [("4.0 ohm", "doubled for the length but ignored the smaller cross-section"),
      ("8.0 ohm", "took half the diameter to mean half the area instead of one quarter"),
      ("64 ohm", "applied the x4 area factor twice on top of the length doubling")],
     EM),

    ("Two identical 60-W bulbs are wired in parallel across an ideal 12-V battery. "
     "One bulb burns out. What happens to the other?",
     "It stays at 60 W, because each parallel branch still sees the full 12 V",
     [("It dims to 30 W, because the current must now be shared by one path",
       "treated the parallel pair as if they shared the supply current"),
      ("It brightens to 120 W, because the current that fed the other bulb now flows through it",
       "assumed the branches share a fixed current, as a series circuit would"),
      ("It goes out too, because the circuit is now broken",
       "confused an open parallel branch with an open series element")],
     EM),

    ("A bar magnet is dropped north-pole-down through a horizontal copper ring. As "
     "the north pole approaches, the induced current in the ring flows so that",
     "the top of the ring becomes a north pole, repelling the magnet and slowing its fall",
     [("the top of the ring becomes a south pole, attracting the magnet and speeding it up",
       "reversed the induced polarity; Lenz's law opposes the change in flux"),
      ("no current flows, because the magnet never touches the ring",
       "required contact for induction, but a changing magnetic flux is enough"),
      ("the current reverses direction continuously and so produces no net field",
       "assumed the motion is oscillatory; during the approach the flux only increases")],
     EM),

    ("A 1500-W space heater runs for 2.0 h. How much energy does it use?",
     "3.0 kWh (1.08 x 10^7 J)",
     [("1.5 kWh", "quoted the power rating as if it were the energy consumed"),
      ("6.0 kWh", "multiplied the power by the square of the time"),
      ("0.75 kWh", "divided the power by the time instead of multiplying")],
     EM),

    ("How much heat is needed to melt 0.10 kg of ice at 0 C and then warm the "
     "water to 20 C? (L_f = 3.34 x 10^5 J/kg, c = 4186 J/(kg C))",
     "4.2 x 10^4 J",
     [("3.3 x 10^4 J", "counted only the latent heat and ignored the warming stage"),
      ("8.4 x 10^3 J", "counted only the warming and ignored the latent heat of fusion"),
      ("4.2 x 10^7 J", "slipped three decimal places in the mass or the latent heat")],
     THERMO),

    ("A gas absorbs 500 J of heat and does 200 J of work as it expands. What is "
     "its change in internal energy?",
     "+300 J",
     [("+700 J", "added the work done by the gas instead of subtracting it"),
      ("-700 J", "reversed the sign of both terms in the first law"),
      ("0 J", "assumed an ideal gas keeps a constant internal energy under any process")],
     THERMO),

    ("An engine takes in 1000 J of heat per cycle from a 500-K reservoir and "
     "rejects heat to a 300-K sink. What is the maximum work it can deliver per "
     "cycle?",
     "400 J",
     [("600 J", "used the rejected fraction (1 - 0.40) as the work fraction"),
      ("200 J", "read the 200-K temperature difference between the reservoirs as the work in joules"),
      ("1000 J", "assumed the Carnot limit allows all the input heat to become work")],
     THERMO),

    ("A 1.5-m string fixed at both ends vibrates in its third harmonic. What is "
     "the wavelength of the standing wave?",
     "1.0 m",
     [("4.5 m", "multiplied the length by 3 instead of using 2L/3"),
      ("0.50 m", "divided the length by 3 and never doubled it"),
      ("3.0 m", "used 2L, the fundamental wavelength, not the third harmonic")],
     VWO),

    ("Tuning forks of 440 Hz and 443 Hz are struck together. What is heard?",
     "A tone of about 441.5 Hz whose loudness rises and falls 3 times per second",
     [("A steady tone at 883 Hz, the sum of the two frequencies",
       "added the frequencies instead of averaging them and taking the difference as the beat rate"),
      ("Two separate tones that do not interact, because the frequencies differ",
       "denied superposition; close frequencies always interfere in time"),
      ("A tone of 441.5 Hz whose loudness stays constant",
       "found the average frequency but missed the beat produced by the 3-Hz difference")],
     VWO),

    ("An object is placed 5.0 cm from a converging lens of focal length 10 cm. "
     "Where is the image and what is it like?",
     "10 cm from the lens on the same side as the object: virtual, upright and twice as tall",
     [("10 cm behind the lens, real and inverted",
       "dropped the minus sign from 1/di = 1/10 - 1/5, which turns the virtual image into a real one"),
      ("At infinity, because the object sits at the focal point",
       "read the 5.0-cm object distance as the 10-cm focal length"),
      ("5.0 cm from the lens on the same side, virtual and the same size",
       "took the image distance as the object distance and skipped the magnification")],
     C4D),

    ("Light travelling in glass (n = 1.5) strikes the glass-air surface at 30 "
     "degrees to the normal. What angle does the refracted ray make with the "
     "normal in air?",
     "49 degrees",
     [("19 degrees", "divided sin 30 by 1.5, putting the index on the wrong side of Snell's law"),
      ("30 degrees", "assumed the ray leaves at the angle it arrived, as if the media matched"),
      ("90 degrees, that is total internal reflection",
       "applied the critical-angle test without checking; the 42-degree critical angle exceeds 30 degrees")],
     C4D),

    ("An electron is accelerated from rest through a potential difference of 100 "
     "V. What kinetic energy does it gain?",
     "1.6 x 10^-17 J (100 eV)",
     [("1.6 x 10^-19 J", "used the elementary charge but forgot to scale by the 100 V"),
      ("1.6 x 10^-15 J", "slipped two places in the exponent"),
      ("100 J", "quoted the accelerating voltage as an energy in joules")],
     MOD),

    ("Light of frequency above the threshold shines on a metal and electrons are "
     "emitted. The intensity is doubled while the frequency is unchanged. What "
     "happens?",
     "The maximum kinetic energy is unchanged, and twice as many electrons are "
     "emitted each second",
     [("The maximum kinetic energy doubles, and the emission rate is unchanged",
       "tied the photon energy to the intensity rather than to the frequency"),
      ("The maximum kinetic energy doubles and so does the emission rate",
       "mixed the two independent roles of frequency and intensity"),
      ("Neither changes, because the number of photons does not affect emission",
       "denied that a higher photon flux ejects more electrons per second")],
     MOD),

    ("An electron moves at 2.0 x 10^6 m/s parallel to a uniform 0.50-T magnetic "
     "field. What magnetic force acts on it?",
     "zero, because the velocity is parallel to the field",
     [("1.6 x 10^-13 N", "evaluated qvB with sin 90 even though the motion is along the field"),
      ("3.2 x 10^-13 N", "doubled the charge as well as taking sin 90"),
      ("0.50 N", "quoted the field strength as though it were a force")],
     EM),
]

EXPLANATIONS = [
    "Only gravity does work, so mgh = 1/2 mv^2 and v = sqrt(2 x 9.8 x 0.20) = sqrt(3.92) = 2.0 m/s; "
    "the mass cancels.",
    "The tension is the centripetal force: mv^2/r = 0.20 x 16 / 0.80 = 4.0 N.",
    "Taking torques about the hinge, T x 4.0 = 400 x 2.0, because a uniform beam's weight acts at "
    "its centre, so T = 200 N.",
    "The velocity reverses, so dv = 6.0 - (-10) = 16 m/s and F = m dv / t = 0.10 x 16 / 0.050 = 32 N.",
    "1/2 mv^2 = 2.0 x 10^5 J of kinetic energy must equal the work done against friction, so d = "
    "200,000 / 5000 = 40 m.",
    "The pressure is the same in both pistons, so F = 150 x (0.30/0.0030) = 150 x 100 = 15,000 N.",
    "At equilibrium the submerged fraction equals the density ratio: 600/1000 = 0.60, or 60%.",
    "Torricelli's result gives v = sqrt(2gh) = sqrt(2 x 9.8 x 5.0) = sqrt(98) = 9.9 m/s.",
    "By Jurin's law h = 2gamma/(rho g r), so the rise varies as 1/r and the narrower tube rises "
    "2.0/0.50 = 4 times higher.",
    "I = emf/(R + r) = 12/6.0 = 2.0 A, and the terminal voltage is emf - Ir = 12 - 2.0(0.50) = 11 V, "
    "the same as IR.",
    "Q = CV = (4.0 x 10^-6)(12) = 4.8 x 10^-5 C = 48 microC on each plate.",
    "R varies as L/A: twice the length doubles it, and half the diameter quarters the area, so "
    "R = 2.0 x 2 x 4 = 16 ohm.",
    "Parallel branches are independent: the surviving bulb still has 12 V across it and still "
    "dissipates V^2/R = 60 W.",
    "Lenz's law opposes the increasing flux, so the ring's near face becomes a north pole that "
    "repels the falling north pole, damping the motion.",
    "Energy = Pt = 1500 x 2.0 = 3000 Wh = 3.0 kWh, which is 3.0 x 3.6 x 10^6 = 1.08 x 10^7 J.",
    "Melting takes mL = 0.10 x 3.34 x 10^5 = 3.34 x 10^4 J and warming takes mc(dT) = 0.10 x 4186 "
    "x 20 = 8.4 x 10^3 J, for a total of 4.2 x 10^4 J.",
    "The first law with the sign convention dU = Q - W gives 500 - 200 = +300 J, since the gas "
    "spends 200 J doing work.",
    "The Carnot efficiency is 1 - Tc/Th = 1 - 300/500 = 0.40, so the maximum work is 0.40 x 1000 = "
    "400 J.",
    "For a string fixed at both ends the nth harmonic has wavelength 2L/n = 2(1.5)/3 = 1.0 m.",
    "Superposition gives an average frequency of (440 + 443)/2 = 441.5 Hz, beat modulated at the "
    "difference 443 - 440 = 3 Hz.",
    "1/di = 1/10 - 1/5 = -1/10, so di = -10 cm: a virtual image 10 cm in front of the lens, "
    "upright and magnified m = 10/5 = 2x (a magnifying glass).",
    "Snell's law n(glass) sin 30 = n(air) sin t gives sin t = 1.5 x 0.50 = 0.75, so t = 49 degrees; "
    "the ray bends away from the normal.",
    "Energy = qV = (1.6 x 10^-19)(100) = 1.6 x 10^-17 J, which is 100 eV.",
    "Photon energy (hence Kmax) depends only on frequency; a brighter beam delivers more photons "
    "per second, so the emission rate doubles.",
    "The magnetic force is qvB sin(theta); with v parallel to B, theta = 0 and sin 0 = 0, so there "
    "is no force.",
]


def main() -> None:
    assert len(ITEMS) == 25 and len(KEYS) == 25
    assert len(EXPLANATIONS) == 25
    items = []
    for n, ((q, correct, wrongs, chapter), key, explain) in enumerate(
            zip(ITEMS, KEYS, EXPLANATIONS), 1):
        assert len(wrongs) == 3 and all(len(w) == 2 for w in wrongs)
        others = [letter for letter in "ABCD" if letter != key]
        choices = {key: correct}
        distractors = {}
        for letter, (text, note) in zip(others, wrongs):
            choices[letter] = text
            distractors[letter] = note
        assert set(choices) == {"A", "B", "C", "D"}
        assert key not in distractors
        items.append({
            "id": f"nmat-d-p2p-{n:03d}",
            "q": " ".join(q.split()),
            "choices": choices,
            "answer": key,
            "explain": " ".join(explain.split()),
            "distractors": distractors,
            "chapter": chapter,
        })

    doc = {
        "exam": "nmat",
        "section": "drill-part2-physics",
        "label": "Physics drill",
        "subject": "physics",
        "block": "part2",
        "_drill": True,
        "items_expected": 25,
        "passages": [],
        "items": items,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=False,
                       default_flow_style=False, width=95)
    print(OUT)
    print(Counter(i["answer"] for i in items))
    print(Counter(i["chapter"] for i in items))


if __name__ == "__main__":
    main()
