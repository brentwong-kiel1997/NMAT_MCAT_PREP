#!/usr/bin/env python3
"""Generate content/exam-bank/mcat/drill/chem-phys.yml (30 practice-only items).

Drill bank that leans on what the scored Chem/Phys bank underrepresents:
quantitative general chemistry and circuits solved with real numbers.

Every option list is written [correct, w1, w2, w3]; build() places the correct
option on the requested answer letter and the three wrong options on the
remaining letters in ascending order, so `distractors` keys are exactly the
three letters that are NOT the answer.

Quantitative stems compute their answer text from a Python expression and then
re-assert it against an independently written second expression, so the key
cannot drift from the arithmetic.
"""
import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/mcat/drill/chem-phys.yml"
LETTERS = "ABCD"
IDPREFIX = "mcat-d-cp"


def calc(n, got, want, rel=2e-3):
    """Recompute a quantity a second way and insist the two agree."""
    assert abs(got - want) <= rel * max(1.0, abs(want)), (n, got, want)
    return got


def build(n, q, correct, wrongs, key, explain, chapter):
    assert key in LETTERS, (n, key)
    assert len(wrongs) == 3, (n, len(wrongs))
    choices, distractors = {}, {}
    wi = 0
    for L in LETTERS:
        if L == key:
            choices[L] = correct
        else:
            text, why = wrongs[wi]
            wi += 1
            assert text != correct, (n, "duplicate option text")
            choices[L] = text
            distractors[L] = why
    assert wi == 3 and set(distractors) == set(LETTERS) - {key}
    assert key not in distractors
    return {
        "id": "%s-%03d" % (IDPREFIX, n),
        "q": q,
        "choices": choices,
        "answer": key,
        "explain": explain,
        "distractors": distractors,
        "chapter": chapter,
        "passage_id": "",
    }


# answer-letter plan (30 items): A:8 B:8 C:7 D:7 -> nothing over 8
KEYS = (["A", "B", "C", "D"] * 7 + ["A", "B"])
assert len(KEYS) == 30

items = []

# ------------------------------------------------------------------ 1-5 moles
# 1  gas stoichiometry at STP
n1 = calc(1, 11.2 / 22.4, 0.50)
m1 = calc(1, n1 * 100.0, 50.0)
items.append(build(
    1,
    "Calcium carbonate decomposes according to CaCO3(s) → CaO(s) + CO2(g). What mass of CaCO3 "
    "(100. g/mol) must decompose to give 11.2 L of CO2 measured at STP (22.4 L/mol)?",
    "%.1f g" % m1,
    [("25 g", "Halved the mole ratio, as if 2 mol CaCO3 were needed per mol CO2."),
     ("100. g", "Assumed 1.00 mol of gas was collected instead of 0.50 mol."),
     ("11.2 g", "Read the 11.2 L gas volume directly as grams of carbonate.")],
    KEYS[0],
    "n(CO2) = 11.2 L / 22.4 L/mol = %.2f mol. The 1:1 stoichiometry gives %.2f mol CaCO3, "
    "and %.2f mol x 100. g/mol = %.1f g." % (n1, n1, n1, m1),
    "general-chemistry"))

# 2  dilution
v2_ml = calc(2, 0.050 * 500.0 / 2.0, 12.5)
items.append(build(
    2,
    "What volume of a 2.0 M stock solution is needed to prepare 500 mL of a 0.050 M working "
    "solution?",
    "%.1f mL" % v2_ml,
    [("5.0 mL", "Inverted the dilution ratio and solved C1V1 = C2V2 with C1 and C2 swapped."),
     ("20. mL", "Used a 10-fold stock concentration (20. M) instead of 2.0 M."),
     ("25 mL", "Dropped a factor of two, using 250 mL as the target volume.")],
    KEYS[1],
    "V1 = C2V2/C1 = (0.050 M x 500 mL)/2.0 M = %.1f mL; the dilution is 1:40." % v2_ml,
    "analytical-chemistry"))

# 3  titration
c3 = calc(3, 0.100 * 20.0 / 25.0, 0.080)
items.append(build(
    3,
    "A 25.0 mL sample of HCl of unknown concentration requires 20.0 mL of 0.100 M NaOH to reach "
    "the equivalence point. What is [HCl]?",
    "%.3f M" % c3,
    [("0.125 M", "Divided by the base volume and multiplied by the acid volume, inverting the "
                 "ratio."),
     ("0.0500 M", "Used only half of the delivered base volume, as if the flask held 50.0 mL."),
     ("0.800 M", "Slipped a decimal place: 2.0 mmol / 25.0 mL is 0.0800, not 0.800.")],
    KEYS[2],
    "mmol NaOH = 0.100 M x 20.0 mL = 2.00 mmol. HCl and NaOH react 1:1, so [HCl] = "
    "2.00 mmol / 25.0 mL = %.3f M." % c3,
    "analytical-chemistry"))

# 4  strong base pH
ph4 = calc(4, 14.0 - 3.0, 11.0)
items.append(build(
    4,
    "What is the pH of a 1.0 x 10^-3 M solution of NaOH at 25 °C?",
    "%.0f" % ph4,
    [("3", "Reported the pOH instead of the pH."),
     ("2", "Treated the solution as 10^-3 M HCl and took -log(10^-2) after a decimal error."),
     ("13", "Used pOH = 1, as if [OH-] were 10^-1 M rather than 10^-3 M.")],
    KEYS[3],
    "NaOH fully dissociates, so [OH-] = 1.0 x 10^-3 M, pOH = 3.00 and pH = 14.00 - 3.00 = %.0f."
    % ph4,
    "general-chemistry"))

# 5  weak acid pH
h5 = calc(5, (1.0e-5 * 0.10) ** 0.5, 1.0e-3)
ph5 = calc(5, -__import__("math").log10(h5), 3.0)
items.append(build(
    5,
    "A 0.10 M solution of a weak monoprotic acid HA has Ka = 1.0 x 10^-5. What is the pH? "
    "(Approximate the equilibrium by x = sqrt(Ka C).)",
    "%.1f" % ph5,
    [("5.0", "Set [H+] equal to Ka itself instead of solving the equilibrium expression."),
     ("2.5", "Took -log(0.10) after dropping Ka from the expression."),
     ("6.0", "Solved for pKa - log C rather than for the hydrogen ion concentration.")],
    KEYS[4],
    "[H+] = sqrt(Ka C) = sqrt(1.0 x 10^-5 x 0.10) = 1.0 x 10^-3 M, so pH = %.1f." % ph5,
    "general-chemistry"))

# --------------------------------------------------------- 6-10 solutions/kin
# 6  freezing point depression
dt6 = calc(6, 2 * 1.86 * 1.0, 3.72)
items.append(build(
    6,
    "What is the freezing point of a 1.0 m solution of NaCl in water? (Kf = 1.86 °C kg/mol; "
    "assume ideal behavior.)",
    "-%.1f °C" % dt6,
    [("-1.9 °C", "Forgot that NaCl is a strong electrolyte and used i = 1 instead of i = 2."),
     ("3.7 °C", "Computed the magnitude of the depression but reported it as an elevation."),
     ("-5.6 °C", "Used i = 3, the van 't Hoff factor of a 2:1 salt such as CaCl2.")],
    KEYS[5],
    "ΔTf = i Kf m = 2 x 1.86 x 1.0 = %.2f °C, so the solution freezes at -%.1f °C." % (dt6, dt6),
    "5a-unique-nature-of-water-and-its-solutions"))

# 7  Gibbs free energy
dg7 = calc(7, -92.0 - 298.0 * (-0.198), -33.0)
items.append(build(
    7,
    "For the reaction N2(g) + 3 H2(g) → 2 NH3(g), ΔH° = -92.0 kJ/mol and ΔS° = -198 J/(mol·K). "
    "What is ΔG° at 298 K?",
    "%.1f kJ/mol" % dg7,
    [("-151 kJ/mol", "Added -TΔS° as if ΔS° were positive, subtracting another 59 kJ."),
     ("+33.0 kJ/mol", "Flipped the overall sign; the reaction is spontaneous as written."),
     ("-92.0 kJ/mol", "Reported ΔH° alone, ignoring the entropy term entirely.")],
    KEYS[6],
    "ΔG° = ΔH° - TΔS° = -92.0 kJ/mol - (298 K)(-0.198 kJ/mol·K) = -92.0 + 59.0 = "
    "%.1f kJ/mol, so the reaction is spontaneous at 298 K." % dg7,
    "5e-chemical-thermodynamics-and-kinetics"))

# 8  first-order kinetics
th8 = calc(8, 0.693 / 0.0693, 10.0)
t8 = calc(8, 2 * th8, 20.0)
items.append(build(
    8,
    "A drug is eliminated by first-order kinetics with a rate constant of 0.0693 min^-1. How long "
    "does it take for the plasma concentration to fall to 25% of its initial value?",
    "%.0f min" % t8,
    [("10 min", "Stopped after one half-life, at which point 50% remains."),
     ("5.0 min", "Inverted the expression and used 0.5/k instead of 0.693/k."),
     ("40. min", "Allowed four half-lives, which would leave only 6% of the drug.")],
    KEYS[7],
    "t1/2 = 0.693/k = 0.693/0.0693 = %.0f min. Falling to 25%% takes two half-lives, so "
    "t = %.0f min." % (th8, t8),
    "5e-chemical-thermodynamics-and-kinetics"))

# 9  rate law scaling
r9 = calc(9, 2 * 3 ** 2, 18)
items.append(build(
    9,
    "A reaction obeys the rate law rate = k[A][B]^2. If [A] is doubled and [B] is tripled, by what "
    "factor does the initial rate increase?",
    "%d" % r9,
    [("6", "Treated [B] as first order and computed 2 x 3."),
     ("9", "Doubled nothing: 3^2 accounts for B but [A] was left out of the factor."),
     ("36", "Squared both concentration changes, as if the law were k[A]^2[B]^2.")],
    KEYS[8],
    "The rate scales as (2)(3)^2 = 2 x 9 = %d." % r9,
    "5e-chemical-thermodynamics-and-kinetics"))

# 10 chromatography Rf
rf10 = calc(10, 3.0 / 6.0, 0.50)
items.append(build(
    10,
    "On a thin-layer chromatography plate the solvent front travels 6.0 cm from the origin while a "
    "spot travels 3.0 cm. What is the Rf of the compound?",
    "%.2f" % rf10,
    [("2.0", "Divided the solvent-front distance by the spot distance, inverting Rf."),
     ("0.25", "Used half of the spot distance, as if the solvent front were at 12 cm."),
     ("3.0 cm", "Reported a raw distance; Rf is dimensionless by definition.")],
    KEYS[9],
    "Rf = distance moved by spot / distance moved by solvent front = 3.0/6.0 = %.2f." % rf10,
    "5c-separation-and-purification-methods"))

# ------------------------------------------------------------ 11-15 chem/phys
# 11 enthalpy of vaporization
q11 = calc(11, 0.50 * 40.7, 20.35)
items.append(build(
    11,
    "How much heat is required to vaporize 0.50 mol of water at 100 °C? (ΔHvap = 40.7 kJ/mol)",
    "%.1f kJ" % q11,
    [("81.4 kJ", "Doubled the amount, as if 1.0 mol were being vaporized."),
     ("10.2 kJ", "Halved ΔHvap before multiplying by the moles."),
     ("40.7 kJ", "Reported the molar enthalpy instead of scaling it by the amount present.")],
    KEYS[10],
    "q = nΔHvap = 0.50 mol x 40.7 kJ/mol = %.1f kJ." % q11,
    "5b-molecules-and-intermolecular-interactions"))

# 12 hydrogenation stoichiometry
mh12 = calc(12, 2 * 2.0, 4.0)
items.append(build(
    12,
    "Complete hydrogenation of 1.0 mol of linoleic acid (C18H32O2), which contains two "
    "carbon-carbon double bonds, requires what mass of H2 (2.0 g/mol)?",
    "%.1f g" % mh12,
    [("2.0 g", "Counted only one of the two double bonds."),
     ("8.0 g", "Assumed four double bonds and consumed 4 mol of hydrogen."),
     ("1.0 g", "Took 0.5 mol of H2, as if one H2 molecule reduced two double bonds.")],
    KEYS[11],
    "Each C=C consumes 1 mol H2, so 2 mol H2 = 2 x 2.0 g = %.1f g of hydrogen per mol of acid."
    % mh12,
    "5d-biologically-relevant-molecules"))

# 13 percent yield
y13 = calc(13, 7.5 / 10.0 * 100.0, 75.0)
items.append(build(
    13,
    "A synthesis has a theoretical yield of 10.0 g. If 7.5 g of purified product is isolated, what "
    "is the percent yield?",
    "%.0f%%" % y13,
    [("133%", "Inverted the ratio and divided theoretical by actual yield."),
     ("25%", "Reported the mass shortfall instead of the fraction obtained."),
     ("50.%", "Compared the product to twice the theoretical yield.")],
    KEYS[12],
    "Percent yield = actual/theoretical x 100 = 7.5/10.0 x 100 = %.0f%%." % y13,
    "organic-chemistry"))

# 14 ideal gas law
p14 = calc(14, round(0.50 * 0.0821 * 300.0 / 12.3, 1), 1.0)
items.append(build(
    14,
    "What is the pressure exerted by 0.50 mol of an ideal gas held at 300 K in a 12.3 L vessel? "
    "(R = 0.0821 L·atm/mol·K)",
    "%.1f atm" % p14,
    [("0.50 atm", "Reported the number of moles rather than solving for pressure."),
     ("2.0 atm", "Halved the volume, as if the vessel held 6.15 L."),
     ("24.6 atm", "Multiplied nRT and never divided by the volume.")],
    KEYS[13],
    "P = nRT/V = (0.50 mol)(0.0821 L·atm/mol·K)(300 K)/12.3 L = %.1f atm." % p14,
    "general-chemistry"))

# 15 electrochemical cell potential
e15 = calc(15, 0.34 + 0.76, 1.10)
items.append(build(
    15,
    "A galvanic cell couples Cu2+/Cu (E°red = +0.34 V) with Zn2+/Zn (E°red = -0.76 V), with copper "
    "reduced at the cathode. What is E°cell?",
    "+%.2f V" % e15,
    [("+0.42 V", "Subtracted the zinc reduction potential from copper's instead of adding the "
                 "cathode potential to the anode oxidation potential."),
     ("+0.76 V", "Reported the zinc electrode potential alone."),
     ("-1.10 V", "Kept the correct magnitude but assigned the sign of a non-spontaneous cell.")],
    KEYS[14],
    "E°cell = E°cathode - E°anode(reduction) = 0.34 - (-0.76) = +%.2f V; zinc is oxidized."
    % e15,
    "4c-electrochemistry-and-electrical-circuits"))

# --------------------------------------------------------- 16-20 circuits/energy
# 16 parallel resistors
req16 = calc(16, 4.0 / 2, 2.0)
i16 = calc(16, 12.0 / req16, 6.0)
items.append(build(
    16,
    "Two identical 4.0 Ω resistors are connected in parallel across a 12 V battery of negligible "
    "internal resistance. What is the total current delivered by the battery?",
    "%.1f A" % i16,
    [("1.5 A", "Added the resistances as if they were in series (8.0 Ω) before applying Ohm's law."),
     ("12. A", "Took the equivalent resistance to be 1.0 Ω rather than 2.0 Ω."),
     ("3.0 A", "Found the correct 6.0 A but divided by the number of parallel branches.")],
    KEYS[15],
    "R_eq = 4.0/2 = %.1f Ω for two equal parallel resistors, so I = V/R_eq = 12/2.0 = %.1f A."
    % (req16, i16),
    "4c-electrochemistry-and-electrical-circuits"))

# 17 electric power
p17 = calc(17, 120.0 ** 2 / 15.0, 960.0)
items.append(build(
    17,
    "A 15 Ω heating element is connected to a 120 V supply. At what rate does it dissipate energy?",
    "%.0f W" % p17,
    [("8.0 W", "Used V/R, which gives the current in amperes, not the power in watts."),
     ("1800 W", "Multiplied V by R instead of dividing V^2 by R."),
     ("14400 W", "Squared the voltage but never divided by the resistance.")],
    KEYS[16],
    "P = V^2/R = (120 V)^2/15 Ω = %.0f W (equivalently I = 8.0 A and P = IV)." % p17,
    "electricity-and-magnetism"))

# 18 RC time constant
tau18 = calc(18, 1.0e5 * 1.0e-5, 1.0)
items.append(build(
  18,
  "A 10 µF capacitor charges through a 100 kΩ resistor. What is the time constant of the circuit?",
    "%.1f s" % tau18,
    [("1.0 x 10^6 s", "Divided R by C, inverting the time-constant expression."),
     ("1.0 x 10^-1 s", "Used R = 10 kΩ, a thousandfold slip on the resistor value."),
     ("10. s", "Took C = 100 µF, swapping the resistance and capacitance values.")],
    KEYS[17],
    "τ = RC = (1.0 x 10^5 Ω)(1.0 x 10^-5 F) = %.1f s; the capacitor reaches 63%% of full charge in "
    "that time." % tau18,
    "4c-electrochemistry-and-electrical-circuits"))

# 19 free fall
v19 = calc(19, (2 * 10.0 * 20.0) ** 0.5, 20.0)
items.append(build(
    19,
    "A stone is dropped from rest from a 20 m cliff. Ignoring air resistance and taking "
    "g = 10 m/s^2, what is its speed just before impact?",
    "%.0f m/s" % v19,
    [("40. m/s", "Computed 2gh but never took the square root."),
     ("14 m/s", "Dropped the factor of two and used v = sqrt(gh)."),
     ("200 m/s", "Used the distance as the acceleration, giving gh = 2000 under the root.")],
    KEYS[18],
    "v = sqrt(2gh) = sqrt(2 x 10 x 20) = sqrt(400) = %.0f m/s." % v19,
    "4a-motion-forces-work-energy-equilibrium"))

# 20 work-energy theorem
w20 = calc(20, 10.0 * 5.0, 50.0)
v20 = calc(20, (2 * w20 / 2.0) ** 0.5, 7.07, rel=1e-3)
items.append(build(
    20,
    "A 2.0 kg block at rest on a frictionless surface is pushed by a constant 10 N force through "
    "5.0 m. What is its final speed?",
    "%.1f m/s" % v20,
    [("5.0 m/s", "Omitted the factor of two and used v = sqrt(W/m)."),
     ("10. m/s", "Ignored the mass and used v = sqrt(2W)."),
     ("50. m/s", "Substituted the work in joules directly as the speed.")],
    KEYS[19],
    "W = Fd = 10 x 5.0 = %.0f J, and W = ½mv^2 gives v = sqrt(2 x %.0f/2.0) = %.1f m/s."
    % (w20, w20, v20),
    "mechanics"))

# ------------------------------------------------------------- 21-25 fluids/EM
# 21 equation of continuity
v21 = calc(21, 30.0 * 3.0 / 900.0, 0.10)
items.append(build(
    21,
    "Blood flowing at 30 cm/s through a vessel of cross-sectional area 3.0 cm² enters a bed whose "
    "total cross-sectional area is 900 cm². What is the flow speed in the bed?",
    "%.2f cm/s" % v21,
    [("300 cm/s", "Inverted the area ratio, using A2/A1 instead of A1/A2."),
     ("3.0 cm/s", "Divided by the area ratio only once instead of computing 30 x (3.0/900)."),
     ("9000 cm/s", "Multiplied the speed by the total area rather than dividing.")],
    KEYS[20],
    "A1v1 = A2v2, so v2 = v1(A1/A2) = 30 x (3.0/900) = %.2f cm/s." % v21,
    "4b-fluids-for-circulation-and-gas-exchange"))

# 22 buoyancy
frac22 = calc(22, 0.92 / 1.00 * 100.0, 92.0)
items.append(build(
    22,
    "Ice has a density of 0.92 g/cm³ and freshwater 1.00 g/cm³. What fraction of a floating ice "
    "cube's volume is submerged?",
    "%.0f%%" % frac22,
    [("8.0%", "Reported the fraction above the surface rather than below it."),
     ("46%", "Took half of the correct value, as if only half the weight were supported."),
     ("108%", "Divided the water density by the ice density, giving a physically impossible "
              "value above 100%.")],
    KEYS[21],
    "For a floating body, V_sub/V = ρ_object/ρ_fluid = 0.92/1.00 = %.0f%%." % frac22,
    "4b-fluids-for-circulation-and-gas-exchange"))

# 23 thin lens
di23 = calc(23, 1.0 / (1.0 / 10.0 - 1.0 / 30.0), 15.0)
items.append(build(
    23,
    "An object stands 30 cm from a converging lens of focal length 10 cm. How far from the lens "
    "does the image form?",
    "%.0f cm" % di23,
    [("7.5 cm", "Took half the focal length, misreading 2f as the image distance for 2f-object."),
     ("20. cm", "Subtracted the reciprocals in the wrong order, using 1/do - 1/f."),
     ("30. cm", "Assumed the image forms at the object distance.")],
    KEYS[22],
    "1/f = 1/do + 1/di gives 1/di = 1/10 - 1/30 = 2/30, so di = %.0f cm; m = -di/do = -0.5, so the "
    "image is real, inverted and half size." % di23,
    "vibrations-waves-and-optics"))

# 24 speed of light in a medium
v24 = calc(24, 3.0e8 / 1.5, 2.0e8)
items.append(build(
    24,
    "Light passes from vacuum into glass of refractive index 1.5. What is its speed in the glass?",
    "2.0 x 10^8 m/s",
    [("4.5 x 10^8 m/s", "Multiplied c by n instead of dividing, exceeding the vacuum speed of "
                        "light."),
     ("1.5 x 10^8 m/s", "Halved c twice, once for n = 1.5 and once more for no reason."),
     ("3.0 x 10^8 m/s", "Assumed the speed is unchanged; only the frequency stays constant.")],
    KEYS[23],
    "v = c/n = (3.0 x 10^8 m/s)/1.5 = 2.0 x 10^8 m/s (the frequency, not the speed, is fixed).",
    "4d-light-and-sound-interacting-with-matter"))

# 25 wavelength of sound
lam25 = calc(25, 340.0 / 170.0, 2.0)
items.append(build(
    25,
    "A tuning fork emits a 170 Hz tone in air, where the speed of sound is 340 m/s. What is the "
    "wavelength?",
    "%.1f m" % lam25,
    [("0.50 m", "Inverted the wave equation and computed f/v."),
     ("170 m", "Reported the frequency with the units of wavelength."),
     ("57800 m", "Multiplied v by f instead of dividing.")],
    KEYS[24],
    "λ = v/f = 340/170 = %.1f m." % lam25,
    "vibrations-waves-and-optics"))

# ------------------------------------------------------------- 26-30 modern
# 26 Doppler shift
f26 = calc(26, 440.0 * 340.0 / (340.0 - 34.0), 488.9, rel=1e-3)
items.append(build(
    26,
    "A 440 Hz ambulance siren drives directly toward a stationary listener at 34 m/s. Taking the "
    "speed of sound as 340 m/s, what frequency does the listener hear?",
    "%.0f Hz" % f26,
    [("400 Hz", "Applied the receding-source formula with (v + vs) in the denominator."),
     ("396 Hz", "Multiplied by 0.9 instead of dividing by 0.9 when the source approached."),
     ("440 Hz", "Assumed a shift requires motion of the listener rather than of the source.")],
    KEYS[25],
    "f' = f v/(v - vs) = 440 x 340/(340 - 34) = 440 x 340/306 ≈ %.0f Hz, an upward shift."
    % f26,
    "4d-light-and-sound-interacting-with-matter"))

# 27 photoelectric effect
e27 = calc(27, 1240.0 / 400.0, 3.1)
ke27 = calc(27, e27 - 2.1, 1.0)
items.append(build(
    27,
    "Light of wavelength 400 nm (E = 1240 eV·nm/λ) strikes a metal whose work function is 2.1 eV. "
    "What is the maximum kinetic energy of the emitted photoelectrons?",
    "%.1f eV" % ke27,
    [("3.1 eV", "Reported the photon energy and ignored the work function."),
     ("5.2 eV", "Added the photon energy to the work function instead of subtracting."),
     ("2.1 eV", "Subtracted the photon energy from the work function, reversing KE = hf - φ.")],
    KEYS[26],
    "hf = 1240/400 = %.1f eV and KEmax = hf - φ = %.1f - 2.1 = %.1f eV." % (e27, e27, ke27),
    "modern-physics"))

# 28 radioactive decay
m28 = calc(28, 20.0 / 2 ** 3, 2.5)
items.append(build(
    28,
    "A 20 g sample of a radionuclide has a half-life of 5.0 days. What mass remains undecayed "
    "after 15 days?",
    "%.1f g" % m28,
    [("10. g", "Counted only one half-life rather than three."),
     ("1.25 g", "Allowed four half-lives, one more than 15 days contains."),
     ("5.0 g", "Counted two half-lives, as if the half-life were 7.5 days.")],
    KEYS[27],
    "15 days = 3 half-lives, so m = 20 g x (1/2)^3 = 20/8 = %.1f g." % m28,
    "modern-physics"))

# 29 Carnot efficiency
eta29 = calc(29, 1.0 - 300.0 / 600.0, 0.50)
w29 = calc(29, eta29 * 1000.0, 500.0)
items.append(build(
    29,
    "A reversible heat engine absorbs 1000 J per cycle from a reservoir at 600 K and rejects heat "
    "to a reservoir at 300 K. How much work does it do per cycle?",
    "%.0f J" % w29,
    [("1000 J", "Assumed all the absorbed heat becomes work, which violates the second law."),
     ("250 J", "Applied the efficiency formula twice, using η² instead of η."),
     ("300 J", "Used the cold-reservoir temperature as the efficiency and applied it to 1000 J.")],
    KEYS[28],
    "η = 1 - Tc/Th = 1 - 300/600 = %.2f, so W = η Qh = %.2f x 1000 J = %.0f J."
    % (eta29, eta29, w29),
    "thermodynamics"))

# 30 Beer-Lambert law
a30 = calc(30, 5.0e3 * 2.0e-5 * 1.0, 0.10)
items.append(build(
    30,
    "A protein solution in a 1.0 cm cuvette has molar absorptivity 5.0 x 10^3 M^-1 cm^-1 and "
    "concentration 2.0 x 10^-5 M. What absorbance does a spectrophotometer read?",
    "%.2f" % a30,
    [("1.0", "Dropped a factor of ten in the concentration."),
     ("0.010", "Slipped two decimal places when multiplying ε by c."),
     ("100.", "Inverted the law and divided ε by the concentration path product.")],
    KEYS[29],
    "A = εcl = (5.0 x 10^3 M^-1 cm^-1)(2.0 x 10^-5 M)(1.0 cm) = %.2f." % a30,
    "biochemistry"))

# --------------------------------------------------------------------- assemble
doc = {
    "exam": "mcat",
    "section": "drill-chem-phys",
    "label": "Chem/Phys drill",
    "subject": "chem-phys",
    "block": "chem-phys",
    "_drill": True,
    "items_expected": len(items),
    "items": items,
    "passages": [],
}
assert len(items) == 30 == doc["items_expected"], len(items)
assert len({i["id"] for i in items}) == 30
allowed = {"4a-motion-forces-work-energy-equilibrium", "4b-fluids-for-circulation-and-gas-exchange",
           "4c-electrochemistry-and-electrical-circuits", "4d-light-and-sound-interacting-with-matter",
           "electricity-and-magnetism", "mechanics", "modern-physics", "thermodynamics",
           "vibrations-waves-and-optics", "5a-unique-nature-of-water-and-its-solutions",
           "5b-molecules-and-intermolecular-interactions", "5c-separation-and-purification-methods",
           "5d-biologically-relevant-molecules", "5e-chemical-thermodynamics-and-kinetics",
           "analytical-chemistry", "biochemistry", "general-chemistry", "organic-chemistry"}
assert {i["chapter"] for i in items} <= allowed
letters = Counter(i["answer"] for i in items)
assert max(letters.values()) <= 8, letters
assert len({i["q"] for i in items}) == 30

with open(OUT, "w") as fh:
    yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=True, width=100)

print("wrote", OUT)
print("answers:", dict(sorted(letters.items())))
print("chapters:", dict(Counter(i["chapter"] for i in items)))
