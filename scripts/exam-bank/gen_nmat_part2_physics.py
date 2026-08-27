#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/part2-physics.yml (30 NMAT Physics items).

Each item is authored as (q, correct_text, [(wrong_text, error_note) x3], chapter).
A fixed balanced key pattern places the correct choice; the three wrong choices
fill the remaining letters in order, so distractor notes can never land on the
answer letter.
"""
import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/part2-physics.yml"

# Balanced key pattern, 30 slots -> A:8 B:7 C:7 D:8
KEYS = ["A", "B", "C", "D", "D", "A", "B", "C", "D", "B",
        "A", "C", "D", "A", "B", "C", "D", "A", "B", "C",
        "D", "B", "A", "D", "C", "B", "A", "D", "C", "A"]

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
    # ---------------- kinematics / projectiles ----------------
    ("A stone is dropped from rest from a bridge and strikes the water 3.0 s later. "
     "Ignoring air resistance (g = 9.8 m/s^2), how high is the bridge?",
     "44 m",
     [("29 m", "used the final speed v = gt as if it applied to the whole fall (v x t)"),
      ("88 m", "dropped the factor of 1/2 (gt^2 instead of 1/2 gt^2)"),
      ("15 m", "used t instead of t^2 (1/2 g t)")],
     C4A),

    ("A marble rolls horizontally off a 20-m-high bench at 15 m/s. Taking g = 10 m/s^2, "
     "how long is it in the air?",
     "2.0 s",
     [("1.5 s", "treated the 15 m/s launch speed as a vertical speed (t = v/g)"),
      ("1.4 s", "dropped the factor of 2 under the root (sqrt(h/g) = sqrt 2)"),
      ("4.0 s", "used t = 2h/g = 4 s, omitting the square root")],
     C4A),

    ("A 1200-kg car accelerates from rest to 24 m/s in 8.0 s. What net force acts on it?",
     "3600 N",
     [("9600 N", "read the 8.0 s as the acceleration (a = 8.0 m/s^2)"),
      ("28,800 N", "computed the momentum mv instead of the force ma"),
      ("450 N", "divided by t twice (a = v/t^2 = 24/64)")],
     C4A),

    ("A 40-kg crate is dragged at constant velocity across a level floor. "
     "If the coefficient of kinetic friction is 0.25 and g = 9.8 m/s^2, what horizontal "
     "force is needed?",
     "98 N",
     [("392 N", "used the full weight, taking the coefficient as 1"),
      ("9.8 N", "slipped a decimal in the coefficient (0.025)"),
      ("10 N", "multiplied the coefficient by the mass only, omitting g")],
     C4A),

    ("A 10-kg block is released on a frictionless incline angled 30 degrees above the "
     "horizontal. Taking g = 10 m/s^2, what is its acceleration down the slope?",
     "5.0 m/s^2",
     [("10 m/s^2", "used the full g, ignoring the incline angle"),
      ("8.7 m/s^2", "used cos 30 degrees instead of sin 30 degrees"),
      ("2.5 m/s^2", "squared the sine (sin^2 30 = 0.25) instead of using sin 30")],
     C4A),

    ("A rope pulls a sled 4.0 m with a steady 50-N force directed 60 degrees above the "
     "horizontal. How much work does the rope do on the sled?",
     "100 J",
     [("200 J", "ignored the angle and assumed the force is parallel to the motion"),
      ("173 J", "used sin 60 degrees in place of cos 60 degrees"),
      ("400 J", "divided by cos 60 degrees instead of multiplying by it")],
     C4A),

    ("A 50-kg athlete runs up a 4.0-m flight of stairs in 10 s. Taking g = 10 m/s^2, "
     "what is her average power output?",
     "200 W",
     [("20 W", "omitted g (used mh/t)"),
      ("400 W", "used t = 5.0 s, halving the time"),
      ("2000 W", "reported the energy mgh in watts, never dividing by the time")],
     C4A),

    # ---------------- momentum / torque ----------------
    ("A 1200-kg car travelling at 20 m/s rear-ends a stationary 800-kg car and the two "
     "lock together. How fast do they move just after impact?",
     "12 m/s",
     [("20 m/s", "assumed the striking car keeps its speed, ignoring momentum sharing"),
      ("10 m/s", "averaged the speeds as if the two masses were equal"),
      ("30 m/s", "divided by the struck car's mass alone (m1 v1 / m2)")],
     MECH),

    ("A 0.50-kg ball strikes a wall at 20 m/s and rebounds along its original line at "
     "10 m/s, staying in contact for 0.020 s. What is the magnitude of the average force "
     "on the ball?",
     "750 N",
     [("250 N", "used the speed difference 20 - 10 = 10 m/s, ignoring the reversal"),
      ("500 N", "counted only the incoming momentum (0.50 x 20)"),
      ("0.30 N", "multiplied by the contact time instead of dividing by it")],
     MECH),

    ("A wheel is acted on by a 20-N force at 0.30 m from the axle (counterclockwise) and "
     "a 15-N force at 0.50 m (clockwise). What is the magnitude of the net torque?",
     "1.5 N.m",
     [("13.5 N.m", "added the two torques, ignoring that they oppose each other"),
      ("6.0 N.m", "kept only the 20-N force's torque"),
      ("4.5 N.m", "paired the 15-N force with the 0.30-m radius")],
     MECH),

    # ---------------- fluids ----------------
    ("What is the gauge pressure 10 m below the surface of a freshwater lake? "
     "(rho = 1000 kg/m^3, g = 10 m/s^2)",
     "1.0 x 10^5 Pa",
     [("1.0 x 10^4 Pa", "slipped a decimal in the density (100 kg/m^3)"),
      ("2.0 x 10^5 Pa", "added atmospheric pressure, but the question asks for gauge"),
      ("1.0 x 10^6 Pa", "an extra factor of 10 (used a depth of 100 m)")],
     C4B),

    ("A 2.0-kg object of density 800 kg/m^3 hangs fully submerged in water "
     "(rho = 1000 kg/m^3, g = 10 m/s^2). What buoyant force acts on it?",
     "25 N",
     [("20 N", "quoted the object's own weight, not the weight of displaced water"),
      ("2.5 N", "slipped a decimal in the volume (2.5 x 10^-4 m^3)"),
      ("250 N", "slipped the other way (2.5 x 10^-2 m^3)")],
     C4B),

    ("Blood flows at 0.20 m/s through an artery of radius 3.0 mm that narrows to "
     "1.0 mm. What is the speed in the narrowed region?",
     "1.8 m/s",
     [("0.60 m/s", "scaled the speed with the radius linearly instead of with r^2"),
      ("0.022 m/s", "inverted the radius ratio (r2/r1 instead of r1/r2)"),
      ("0.20 m/s", "assumed the speed is conserved rather than the flow rate")],
     C4B),

    ("Water flows through a horizontal pipe and speeds up from 2.0 m/s to 6.0 m/s at a "
     "constriction. How much does the pressure fall? (rho = 1000 kg/m^3)",
     "1.6 x 10^4 Pa",
     [("3.2 x 10^4 Pa", "dropped the factor of 1/2"),
      ("8.0 x 10^3 Pa", "subtracted the speeds before squaring"),
      ("1.8 x 10^4 Pa", "took the inlet speed as zero")],
     C4B),

    ("An artery's radius falls to half its original value while the pressure difference "
     "along it stays the same. The flow rate becomes what fraction of the original? "
     "(Poiseuille flow)",
     "1/16",
     [("1/2", "scaled the flow linearly with the radius"),
      ("1/4", "used the area scaling, r^2, instead of r^4"),
      ("1/8", "used an r^3 dependence")],
     C4B),

    # ---------------- thermal physics ----------------
    ("How much heat is needed to raise 2.0 kg of water from 20 degrees C to 70 degrees C? "
     "(c = 4200 J/kg.degC)",
     "4.2 x 10^5 J",
     [("1.7 x 10^5 J", "used the initial 20 degrees C as the rise instead of 50 degrees C"),
      ("8.4 x 10^5 J", "doubled the mass"),
      ("4.2 x 10^2 J", "dropped three decimal places, confusing joules with kilojoules")],
     THERMO),

    ("A sealed rigid tank holds a gas at 1.0 atm and 300 K. It is warmed to 450 K. "
     "What is the new pressure?",
     "1.5 atm",
     [("0.67 atm", "inverted the temperature ratio (T1/T2)"),
      ("1.0 atm", "assumed the pressure is unchanged even though the volume is fixed"),
      ("4.5 atm", "divided T2 by 100 instead of by T1 = 300 K")],
     THERMO),

    ("A heat engine runs between a hot reservoir at 500 K and a cold reservoir at 300 K. "
     "What is its maximum possible efficiency?",
     "40%",
     [("60%", "quoted Tc/Th, the fraction rejected, as the efficiency"),
      ("67%", "divided the temperature difference by the cold temperature"),
      ("25%", "used a 400-K hot reservoir")],
     THERMO),

    # ---------------- waves and sound ----------------
    ("A sound wave has a frequency of 440 Hz and a wavelength of 0.75 m. What is its "
     "speed?",
     "330 m/s",
     [("587 m/s", "divided the frequency by the wavelength instead of multiplying"),
      ("0.0017 m/s", "inverted the ratio (wavelength / frequency)"),
      ("3.3 x 10^4 m/s", "took the wavelength in centimetres as metres (75)")],
     VWO),

    ("A 750-Hz siren approaches a stationary listener at 40 m/s. Taking the speed of "
     "sound as 340 m/s, what frequency does the listener hear?",
     "850 Hz",
     [("671 Hz", "used the receding-source denominator (v + vs)"),
      ("662 Hz", "inverted the fraction, putting (v - vs) in the numerator"),
      ("838 Hz", "added vs to the numerator instead of subtracting it from v")],
     VWO),

    # ---------------- light and sound with matter ----------------
    ("Light passes from air into a transparent medium of refractive index 1.50. "
     "What is its speed in that medium? (c = 3.0 x 10^8 m/s)",
     "2.0 x 10^8 m/s",
     [("4.5 x 10^8 m/s", "multiplied c by n instead of dividing"),
      ("3.0 x 10^8 m/s", "assumed the speed is unchanged on entering the medium"),
      ("1.5 x 10^8 m/s", "divided by 2 rather than by n = 1.50")],
     C4D),

    ("An object sits 15 cm from a converging lens of focal length 10 cm. How far from "
     "the lens is the image formed?",
     "30 cm on the far side of the lens",
     [("6.0 cm", "added the reciprocals (1/do + 1/f) instead of subtracting"),
      ("25 cm", "added the object distance and the focal length"),
      ("10 cm", "assumed the image forms at the focal point")],
     C4D),

    ("What is the critical angle for total internal reflection at a boundary between a "
     "transparent solid of refractive index 2.0 and air?",
     "30 degrees",
     [("60 degrees", "took arccos instead of arcsin"),
      ("27 degrees", "used tan instead of sin"),
      ("15 degrees", "treated the index as a factor on the angle (30 / 2)")],
     C4D),

    # ---------------- electricity and magnetism ----------------
    ("Point charges of +2.0 microC and +3.0 microC sit 0.30 m apart in air. What is the "
     "magnitude of the force between them? (k = 9.0 x 10^9 N.m^2/C^2)",
     "0.60 N",
     [("60 N", "used a separation of 3.0 cm instead of 0.30 m"),
      ("0.18 N", "divided by r instead of r^2"),
      ("1.2 N", "counted the single interacting pair twice")],
     EM),

    ("A 6.0-ohm and a 3.0-ohm resistor are connected in parallel, and that pair is in "
     "series with a 3.0-ohm resistor across a 12-V battery. What current does the battery "
     "supply?",
     "2.4 A",
     [("0.80 A", "treated all three resistors as a series chain (12/15)"),
      ("10 A", "put all three resistors in parallel (R = 1.2 ohm)"),
      ("6.0 A", "dropped the series 3.0-ohm resistor from the total")],
     C4C),

    ("A 4.0-ohm resistor is connected across a 12-V battery. What power does it "
     "dissipate?",
     "36 W",
     [("3.0 W", "used V/R, leaving the voltage unsquared"),
      ("48 W", "multiplied V by R instead of using V^2/R"),
      ("576 W", "multiplied by R instead of dividing by R")],
     EM),

    ("A 0.20-m straight wire carries 5.0 A at 30 degrees to a 0.40-T magnetic field. "
     "What is the magnitude of the force on the wire?",
     "0.20 N",
     [("0.40 N", "omitted the sin 30 factor and treated the wire as perpendicular to B"),
      ("2.0 N", "slipped a decimal in the length (2.0 m)"),
      ("5.0 N", "divided by the length instead of multiplying by it")],
     EM),

    ("A 50-turn coil of area 0.010 m^2 lies perpendicular to a magnetic field that rises "
     "uniformly from 0 to 0.40 T in 0.20 s. What emf is induced?",
     "1.0 V",
     [("0.020 V", "used a single turn, dropping the factor of 50"),
      ("10 V", "used the 0.10-m side length as the area"),
      ("0.040 V", "multiplied by the time interval instead of dividing by it")],
     EM),

    # ---------------- modern physics ----------------
    ("Photons of energy 3.0 eV strike a metal whose work function is 2.0 eV. What is the "
     "maximum kinetic energy of the ejected photoelectrons?",
     "1.0 eV",
     [("5.0 eV", "added the photon energy to the work function instead of subtracting"),
      ("6.0 eV", "multiplied the two energies"),
      ("2.0 eV", "quoted the work function itself")],
     MOD),

    ("A sample contains 80 g of a nuclide whose half-life is 5.0 days. How much remains "
     "after 15 days?",
     "10 g",
     [("40 g", "applied only one half-life instead of three"),
      ("5.0 g", "took four half-lives (80/16) instead of three"),
      ("32 g", "subtracted a fixed 16 g per half-life instead of halving")],
     MOD),
]

assert len(ITEMS) == 30, len(ITEMS)
counts = Counter(KEYS)
assert len(KEYS) == 30 and max(counts.values()) <= 8, counts

items = []
for n, (q, correct, wrongs, chapter) in enumerate(ITEMS, start=1):
    assert len(wrongs) == 3
    ans_letter = KEYS[n - 1]
    others = [l for l in "ABCD" if l != ans_letter]
    choices = {ans_letter: correct}
    distractors = {}
    for letter, (text, note) in zip(others, wrongs):
        choices[letter] = text
        distractors[letter] = note
    items.append({
        "id": "nmat-p2p-%03d" % n,
        "q": q,
        "choices": {k: choices[k] for k in ("A", "B", "C", "D")},
        "answer": ans_letter,
        "explain": None,  # filled below
        "distractors": distractors,
        "chapter": chapter,
    })

# One-line worked solutions, keyed by item number.
EXPLAIN = {
    1: "h = 1/2 g t^2 = 0.5 x 9.8 x (3.0)^2 = 44 m.",
    2: "Only h sets the fall time: t = sqrt(2h/g) = sqrt(2 x 20/10) = sqrt 4 = 2.0 s.",
    3: "a = delta v / t = 24/8.0 = 3.0 m/s^2; F = ma = 1200 x 3.0 = 3600 N.",
    4: "Constant velocity means F = friction = mu m g = 0.25 x 40 x 9.8 = 98 N.",
    5: "a = g sin 30 = 10 x 0.50 = 5.0 m/s^2 (the mass cancels).",
    6: "W = F s cos theta = 50 x 4.0 x cos 60 = 200 x 0.50 = 100 J.",
    7: "P = mgh/t = (50 x 10 x 4.0)/10 = 2000 J / 10 s = 200 W.",
    8: "Momentum is conserved: v = m1 v1/(m1+m2) = (1200 x 20)/2000 = 12 m/s.",
    9: "delta p = m(v_f - v_i) = 0.50 x (+10 - (-20)) = 15 N.s; F = 15/0.020 = 750 N.",
    10: "tau = 20 x 0.30 - 15 x 0.50 = 6.0 - 7.5 = 1.5 N.m, in the clockwise sense.",
    11: "P_gauge = rho g h = 1000 x 10 x 10 = 1.0 x 10^5 Pa.",
    12: "V = m/rho = 2.0/800 = 2.5 x 10^-3 m^3; F = rho_w g V = 1000 x 10 x 0.0025 = 25 N.",
    13: "A1 v1 = A2 v2, so v2 = v1 (r1/r2)^2 = 0.20 x (3.0/1.0)^2 = 1.8 m/s.",
    14: "delta P = 1/2 rho (v2^2 - v1^2) = 500 x (36 - 4) = 1.6 x 10^4 Pa.",
    15: "Poiseuille: Q is proportional to r^4, so (1/2)^4 = 1/16 of the original flow.",
    16: "Q = m c delta T = 2.0 x 4200 x 50 = 4.2 x 10^5 J.",
    17: "Constant V: P2/P1 = T2/T1, so P2 = 1.0 x 450/300 = 1.5 atm.",
    18: "e_max = 1 - Tc/Th = 1 - 300/500 = 0.40 = 40%.",
    19: "v = f lambda = 440 x 0.75 = 330 m/s.",
    20: "f' = f v/(v - vs) = 750 x 340/(340 - 40) = 255,000/300 = 850 Hz.",
    21: "v = c/n = (3.0 x 10^8)/1.50 = 2.0 x 10^8 m/s.",
    22: "1/di = 1/f - 1/do = 1/10 - 1/15 = 1/30, so di = 30 cm (real, inverted).",
    23: "sin theta_c = n_air/n_solid = 1/2.0 = 0.50, so theta_c = arcsin 0.50 = 30 degrees.",
    24: "F = k q1 q2/r^2 = (9.0 x 10^9 x 6.0 x 10^-12)/(0.30)^2 = 0.054/0.09 = 0.60 N.",
    25: "R_par = (6.0 x 3.0)/9.0 = 2.0 ohm; R = 2.0 + 3.0 = 5.0 ohm; I = 12/5.0 = 2.4 A.",
    26: "P = V^2/R = (12)^2/4.0 = 144/4.0 = 36 W.",
    27: "F = B I L sin theta = 0.40 x 5.0 x 0.20 x sin 30 = 0.40 x 0.20 = 0.20 N.",
    28: "emf = N A (delta B/delta t) = 50 x 0.010 x (0.40/0.20) = 50 x 0.010 x 2.0 = 1.0 V.",
    29: "KE_max = E_photon - phi = 3.0 - 2.0 = 1.0 eV.",
    30: "15 d / 5.0 d = 3 half-lives; 80 x (1/2)^3 = 80/8 = 10 g.",
}

for n, it in enumerate(items, start=1):
    it["explain"] = EXPLAIN[n]

doc = {
    "exam": "nmat",
    "section": "part2-physics",
    "label": "Physics",
    "subject": "physics",
    "block": "part2",
    "items_expected": 30,
    "items": items,
    "passages": [],
}

with open(OUT, "w") as fh:
    yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=False,
                   default_flow_style=False, width=100)

print("wrote", OUT)
print("answer keys:", dict(sorted(counts.items())))
print("chapters:", dict(Counter(i["chapter"] for i in items)))
