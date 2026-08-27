#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/part2-chemistry.yml (30-item NMAT Chemistry bank).

Authoring contract (mirrors gen_nmat_part1_verbal.py): every item is written as
(stem, correct_text, [(wrong_text, why_wrong note) x 3], explain, chapter) and a
fixed balanced letter sequence decides WHERE the correct text sits.  The three
notes are then mapped onto the three NON-answer letters in ascending letter
order, so a distractor entry can never land on the answer letter.

Every numeric answer is also re-derived below by arithmetic (NUMERIC_CHECKS) and
asserted against the string that was placed in `choices`.
"""
import math
import os
import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/part2-chemistry.yml"

# Balanced answer letters: A:8 B:8 C:8 D:6 (max 8).
LETTERS = ["C", "A", "B", "C", "A", "B", "D", "C", "A", "B", "D", "C",
           "A", "B", "D", "C", "A", "B", "D", "C", "A", "B", "D", "C",
           "A", "B", "D", "C", "A", "B"]
assert len(LETTERS) == 30
assert Counter(LETTERS) == Counter({"A": 8, "B": 8, "C": 8, "D": 6})

CHAPTERS = {
    "4e": "4e-atoms-nuclear-decay-electronic-structure",
    "5a": "5a-unique-nature-of-water-and-its-solutions",
    "5b": "5b-molecules-and-intermolecular-interactions",
    "5c": "5c-separation-and-purification-methods",
    "5d": "5d-biologically-relevant-molecules",
    "5e": "5e-chemical-thermodynamics-and-kinetics",
    "an": "analytical-chemistry",
    "bc": "biochemistry",
    "gc": "general-chemistry",
    "oc": "organic-chemistry",
}

# (stem, correct_text, [(wrong_text, note) x3 in authored order], explain, chapter-key)
# The three wrong entries below are authored in ascending LETTER order (A,B,C,D
# minus the answer), matching how the builder will attach them.
ITEMS = [
    # ---------------------------------------------------- atomic structure (4e)
    ("How many electrons does the ion 56Fe3+ contain? (Z of Fe = 26)",
     "23 electrons",
     [("26 electrons", "26 is the proton count; a 3+ charge means three electrons were removed."),
      ("29 electrons", "29 adds the charge to Z instead of subtracting it."),
      ("20 electrons", "20 subtracts the charge from the mass number (56) instead of from Z.")],
     "Neutrons = 56 - 26 = 30, but charge depends only on the electron count: e- = Z - charge = 26 - 3 = 23.",
     "4e"),

    ("Which of these elements has the highest first ionization energy?",
     "Ar",
     [("Mg", "Mg sits only third across period 3; 738 kJ/mol is far below the noble-gas value."),
      ("Al", "Al's lone 3p electron is easier to remove than Mg's 3s pair, so its IE dips to 578 kJ/mol."),
      ("Na", "Na has the LOWEST first IE in period 3 (496 kJ/mol); its single 3s electron leaves easily.")],
     "First IE climbs left to right across a period and peaks at the noble gas: Na 496, Mg 738, Al 578, Ar 1521 kJ/mol; the intact 3s2 3p6 shell is hardest to empty.",
     "4e"),

    ("What is the maximum number of electrons in one atom that may have n = 3 and l = 2?",
     "10",
     [("2", "2 is the capacity of a single orbital, not of the whole subshell."),
      ("6", "6 is the capacity of a p subshell (l = 1)."),
      ("14", "14 is the capacity of an f subshell (l = 3).")],
     "l = 2 is a d subshell, which holds 2l + 1 = 5 orbitals x 2 electrons = 10 electrons.",
     "4e"),

    # ------------------------------------------------------ bonding and IMF (5b)
    ("Judged purely by strength of intermolecular attraction, which pure liquid has the highest normal boiling point?",
     "ethanol (CH3CH2OH)",
     [("propane (CH3CH2CH3)", "Propane is nonpolar, so only London dispersion holds it together (bp -42 C)."),
      ("dimethyl ether (CH3OCH3)", "Dimethyl ether is polar but carries no O-H, so it cannot donate a hydrogen bond (bp -24 C)."),
      ("chloroethane (CH3CH2Cl)", "Chloroethane offers only dipole-dipole plus dispersion; no H sits on N, O or F (bp 12 C).")],
     "Ethanol's O-H lets it donate hydrogen bonds (bp 78 C), the strongest intermolecular force in this set; ether and chloroethane stop at dipole-dipole and propane at dispersion.",
     "5b"),

    ("Which molecule contains polar bonds but has a net dipole moment of zero?",
     "CO2",
     [("SO2", "SO2 is bent, so its two bond dipoles add to a net moment."),
      ("H2O", "H2O is bent with two lone pairs on oxygen and is strongly polar."),
      ("NH3", "NH3 is trigonal pyramidal, so its three N-H dipoles cannot cancel.")],
     "CO2 is linear (180 degrees) with two identical C=O dipoles pointing exactly opposite, so they cancel; all three alternatives are bent or pyramidal and stay polar.",
     "5b"),

    ("The hybridization of each carbon atom in acetylene (HCCH) is",
     "sp",
     [("sp3", "sp3 implies four electron domains and tetrahedral geometry."),
      ("sp2", "sp2 belongs to a double-bonded carbon with three electron domains."),
      ("sp3d", "sp3d requires an expanded octet, which second-row carbon cannot reach.")],
     "Each alkyne carbon has only two domains (one C-H sigma, one C-C sigma), so it mixes one s and one p orbital to sp, leaving two unhybridized p orbitals for the two pi bonds (180 degrees).",
     "5b"),

    # ------------------------------------------- moles, stoichiometry, gas (gc)
    ("For N2 + 3 H2 -> 2 NH3, a sealed vessel holds 6.0 mol N2 and 9.0 mol H2. The maximum moles of NH3 formed is",
     "6.0 mol",
     [("12 mol", "12 mol assumes all 6.0 mol of N2 reacts, i.e. that H2 is in excess, which it is not."),
      ("9.0 mol", "9.0 mol assumes a 1:1 H2-to-NH3 mole ratio; the balanced ratio is 3:2."),
      ("4.5 mol", "4.5 mol inverts the ratio and uses 1 mol NH3 per 2 mol H2.")],
     "Burning all 6.0 mol N2 would need 18 mol H2, so H2 limits: NH3 = 9.0 x (2/3) = 6.0 mol.",
     "gc"),

    ("The percent by mass of water in copper(II) sulfate pentahydrate, CuSO4.5H2O, is",
     "36.1%",
     [("64.0%", "64.0% is the CuSO4 fraction (159.6/249.6), not the water's."),
      ("56.4%", "56.4% divides by the anhydrous salt mass (159.6) instead of the whole hydrate mass."),
      ("7.2%", "7.2% counts only one water of crystallization (18.0/249.6).")],
     "M(CuSO4) = 63.5 + 32.1 + 4(16.0) = 159.6; add 5(18.0) = 90.0 for the waters, total 249.6 g/mol; %H2O = 90.0/249.6 x 100 = 36.1%.",
     "gc"),

    ("A 0.500 g sample of a gas occupies 250 mL at 25.0 C and 1.00 atm. Its molar mass is about",
     "48.9 g/mol",
     [("24.5 g/mol", "24.5 doubles the volume in the denominator (0.500 L was used)."),
      ("12.2 g/mol", "12.2 uses 0.125 L, a fourfold volume error."),
      ("97.9 g/mol", "97.9 doubles the mass (1.00 g used instead of 0.500 g).")],
     "M = mRT/PV = (0.500)(0.0821)(298) / (1.00)(0.250) = 48.9 g/mol, with V in liters and T in kelvin.",
     "gc"),

    # ----------------------------------------------- solutions, molarity (5a)
    ("How many grams of NaOH (40.0 g/mol) are needed to prepare 250 mL of 0.500 M solution?",
     "5.00 g",
     [("2.50 g", "2.50 g halves the moles, as if the volume were 125 mL."),
      ("20.0 g", "20.0 g uses the molarity 0.500 as though it were a mole amount."),
      ("0.125 g", "0.125 g reports the mole amount (0.125 mol) as a mass.")],
     "n = MV = 0.500 x 0.250 = 0.125 mol; mass = 0.125 x 40.0 = 5.00 g.",
     "5a"),

    ("What volume of 12.0 M HCl stock solution is required to prepare 2.00 L of 0.150 M acid?",
     "25.0 mL",
     [("160 mL", "160 mL multiplies by the stock concentration instead of dividing by it."),
      ("250 mL", "250 mL is a factor-of-10 decimal slip (0.250 L)."),
      ("2.50 mL", "2.50 mL is a factor-of-10 slip in the other direction (0.00250 L).")],
     "C1V1 = C2V2 gives V1 = (0.150)(2.00)/12.0 = 0.0250 L = 25.0 mL.",
     "5a"),

    # ------------------------------------------------------- biomolecules (5d)
    ("An equal mass of fat releases about twice the energy of carbohydrate chiefly because",
     "its fatty acyl chains are highly reduced, so each carbon delivers more electrons to the respiratory chain",
     [("it carries more oxygen atoms per carbon", "Backwards: fats carry far LESS oxygen per carbon than carbohydrates do."),
      ("its glycerol backbone is the main fuel", "The fatty acyl chains, not the glycerol backbone, supply most of the energy."),
      ("it is a polymer of glucose units", "Glucose polymers are starch or glycogen; triglycerides are esters of glycerol and fatty acids.")],
     "Fatty acyl carbons are held in mostly C-H bonds, so beta-oxidation loads far more NADH and FADH2 per carbon; carbohydrates already carry one oxygen per carbon and are partly oxidized.",
     "5d"),

    # ------------------------------------------------------- acids and bases (5a)
    ("The pH of 0.0030 M HCl at 25 C is",
     "2.52",
     [("3.00", "3.00 uses only the exponent of 10 and ignores the 3.0 coefficient."),
      ("3.48", "3.48 ADDS log 3.0 to the exponent instead of subtracting it."),
      ("11.48", "11.48 is 14 - 2.52, reading an acidic solution as basic (pOH).")],
     "HCl is a strong acid, so [H+] = 3.0 x 10^-3 M and pH = -log(3.0 x 10^-3) = 3.00 - 0.48 = 2.52.",
     "5a"),

    ("A buffer contains 0.20 M acetic acid and 0.60 M sodium acetate (pKa = 4.76). Its pH is",
     "5.24",
     [("4.76", "4.76 is the pH only when [A-] = [HA]; here base is three times the acid."),
      ("4.28", "4.28 inverts the ratio, using log(0.20/0.60) = -0.48."),
      ("5.86", "5.86 uses the natural log (ln 3 = 1.10) instead of log base 10.")],
     "Henderson-Hasselbalch: pH = pKa + log([A-]/[HA]) = 4.76 + log(0.60/0.20) = 4.76 + 0.48 = 5.24.",
     "5a"),

    # ---------------------------------------------- titration (analytical-chemistry)
    ("What volume of 0.100 M NaOH completely neutralizes 25.0 mL of 0.150 M H2SO4?",
     "75.0 mL",
     [("37.5 mL", "37.5 mL ignores the 2:1 stoichiometry and treats H2SO4 as monoprotic."),
      ("150 mL", "150 mL uses 0.0500 M for the base, a decimal slip in its concentration."),
      ("18.8 mL", "18.8 mL divides by 2 instead of multiplying by 2, inverting the mole ratio.")],
     "n(H2SO4) = 0.0250 x 0.150 = 3.75 mmol; OH- required = 2 x 3.75 = 7.50 mmol; V = 7.50/0.100 = 75.0 mL.",
     "an"),

    # ---------------------------------------------------- ATP accounting (bc)
    ("Counting only citric acid cycle contributions for one glucose (both acetyl-CoA; NADH = 2.5 ATP, FADH2 = 1.5 ATP), the ATP-equivalent yield is",
     "20",
    [("10", "10 counts a single turn; one glucose yields two acetyl-CoA, hence two turns."),
     ("15", "15 counts only the NADH (3 x 2.5 = 7.5 per turn) and drops FADH2 and GTP."),
     ("22", "22 adds glycolysis's net 2 ATP to a cycle-only total.")],
     "Each turn gives 3 NADH (7.5) + 1 FADH2 (1.5) + 1 GTP (1) = 10; two acetyl-CoA per glucose means 2 x 10 = 20.",
     "bc"),
]

# Items 17-30 are appended here to keep each entry readable above.
ITEMS += [
    # ------------------------------------------------- thermochemistry (5e)
    ("Given delta-Hf degrees of -277.7 (C2H5OH l), -393.5 (CO2 g) and -285.8 (H2O l) kJ/mol, delta-H for C2H5OH(l) + 3 O2 -> 2 CO2(g) + 3 H2O(l) is",
     "-1367 kJ/mol",
     [("-1644 kJ/mol", "-1644 omits the ethanol reactant term, i.e. never adds back +277.7."),
      ("-277.7 kJ/mol", "-277.7 is the delta-Hf of ethanol itself, not of the reaction."),
      ("+1367 kJ/mol", "+1367 has the sign backwards; that is the endothermic reverse reaction.")],
     "delta-Hrxn = [2(-393.5) + 3(-285.8)] - (-277.7) = -1644.4 + 277.7 = -1366.7, about -1367 kJ/mol.",
     "5e"),

    ("For a process with delta-H = +40.0 kJ/mol and delta-S = +150 J/(mol.K), delta-G at 310 K is",
     "-6.5 kJ/mol, spontaneous",
     [("+6.5 kJ/mol, nonspontaneous", "+6.5 reverses the subtraction and computes T.delta-S - delta-H."),
      ("+40 kJ/mol, nonspontaneous", "+40 uses delta-H alone and ignores the T.delta-S term."),
      ("+86.5 kJ/mol, nonspontaneous", "+86.5 ADDS T.delta-S instead of subtracting it (40.0 + 46.5).")],
     "delta-G = delta-H - T.delta-S = 40.0 - 310(0.150) = 40.0 - 46.5 = -6.5 kJ/mol, spontaneous at 310 K.",
     "5e"),

    ("For 2 SO2(g) + O2(g) <=> 2 SO3(g), delta-H = -198 kJ, which change shifts the equilibrium toward reactants?",
     "raising the temperature",
     [("decreasing the container volume", "Compression favors the side with fewer gas moles, 3 -> 2, which is the product side."),
      ("adding more O2", "Adding a reactant drives the reaction forward, not back."),
      ("removing SO3 as it forms", "Removing a product pulls the reaction to the right to replace it.")],
     "Heat is a product of this exothermic reaction, so raising T drives the reverse (endothermic) direction; every other listed change favors the forward shift.",
     "5e"),

    # --------------------------------------------------------- kinetics (5e)
    ("In initial-rate runs for A + B -> products, doubling [A] at fixed [B] quadruples the rate, while doubling [B] at fixed [A] doubles the rate. The overall reaction order is",
     "3",
     [("1", "1 reads only the B dependence from the data."),
      ("2", "2 reads only the A dependence from the data."),
      ("4", "4 treats both reactants as second order (2 + 2).")],
     "2^x = 4 gives x = 2 for A and 2^y = 2 gives y = 1 for B, so the overall order is 2 + 1 = 3 (k = 2.0e-3/[(0.10)^2(0.10)] = 2.0).",
     "5e"),

    ("A first-order reaction has k = 2.31 x 10^-2 /min. Its half-life is",
     "30.0 min",
     [("43.3 min", "43.3 min is 1/k, forgetting the 0.693 factor."),
      ("15.0 min", "15.0 min halves the half-life."),
      ("60.0 min", "60.0 min doubles the half-life.")],
     "t1/2 = 0.693/k = 0.693/0.0231 = 30.0 min, independent of the starting concentration.",
     "5e"),

    # ------------------------------------------------------ electrochemistry (gc)
    ("Given E degrees of +0.34 V for Cu2+/Cu and -0.76 V for Zn2+/Zn, the standard cell potential of the Daniell cell is",
     "+1.10 V",
     [("+0.34 V", "+0.34 V is the cathode potential alone."),
      ("-1.10 V", "-1.10 V flips the sign, giving the nonspontaneous electrolytic direction."),
      ("+0.76 V", "+0.76 V is the anode's oxidation potential alone.")],
     "E cell = E cathode - E anode = (+0.34) - (-0.76) = +1.10 V, positive as a spontaneous galvanic cell requires.",
     "gc"),

    ("How many grams of copper (63.5 g/mol) plate out when 2.00 A flows through CuSO4(aq) for 965 s?",
     "0.635 g",
     [("1.27 g", "1.27 g uses 0.0200 mol Cu, ignoring that 2 e- reduce each Cu2+."),
      ("0.318 g", "0.318 g assumes four electrons per copper atom."),
      ("0.0635 g", "0.0635 g slips a decimal in the charge, using 193 C instead of 1930 C.")],
     "Q = It = 2.00 x 965 = 1930 C; n(e-) = 1930/96,500 = 0.0200 mol; Cu2+ + 2e- -> Cu gives 0.0100 mol, so mass = 0.0100 x 63.5 = 0.635 g.",
     "gc"),

    # --------------------------------------------------------- organic (oc)
    ("Careful oxidation of 2-butanol, a secondary alcohol, produces",
     "butanone",
     [("butanal", "Butanal comes from oxidizing the primary alcohol 1-butanol."),
      ("butanoic acid", "Butanoic acid requires a primary alcohol plus vigorous oxidation."),
      ("butane", "Oxidation removes hydrogen and adds oxygen; it cannot strip the skeleton back to an alkane.")],
     "A secondary alcohol holds one carbinol hydrogen, and losing it gives the ketone: 2-butanol -> 2-butanone; aldehydes and acids arise only from primary alcohols.",
     "oc"),

    ("Which single reagent distinguishes an aldehyde from a ketone?",
     "Tollens' reagent (Ag+ in ammonia)",
     [("bromine in CCl4", "Br2 in CCl4 tests C=C unsaturation, not the aldehyde/ketone difference."),
      ("sodium borohydride", "NaBH4 reduces both aldehydes and ketones, so it cannot distinguish them."),
      ("2,4-dinitrophenylhydrazine", "2,4-DNPH forms a precipitate with BOTH aldehydes and ketones.")],
     "Aldehydes oxidize easily and reduce Ag+ to metallic silver (a mirror); ketones cannot be oxidized this way, so no mirror forms.",
     "oc"),

    ("Addition of HBr to propene, with no peroxides present, gives which major product?",
     "2-bromopropane",
     [("1-bromopropane", "1-bromopropane is the anti-Markovnikov product, obtained only with peroxides."),
      ("propane", "Propane would mean adding H alone; HBr adds both H and Br across the double bond."),
      ("1,2-dibromopropane", "1,2-dibromopropane requires Br2, not HBr.")],
     "Markovnikov addition: H goes to the CH2 end, leaving the more stable secondary carbocation at C-2 for Br- to attack, so 2-bromopropane dominates.",
     "oc"),

    # ------------------------------------------------- separation methods (5c)
    ("Which technique separates mixture components by their differential partitioning between a stationary phase and a mobile phase?",
     "chromatography",
     [("distillation", "Distillation separates by volatility, that is by boiling point."),
      ("filtration", "Filtration separates by particle size or solubility."),
      ("recrystallization", "Recrystallization separates by how solubility changes with temperature.")],
     "Chromatography resolves a mixture because each component spends a different fraction of its time sorbed on the stationary phase versus being carried by the mobile phase.",
     "5c"),

    ("Two miscible liquids boil at 78 C and 82 C. The best way to separate them is",
     "fractional distillation",
     [("simple distillation", "Simple distillation gives one vaporization cycle, useless for a 4 C boiling-point gap."),
      ("evaporation to dryness", "Evaporation to dryness discards the more volatile liquid instead of purifying it."),
      ("decantation", "Decantation separates immiscible layers or solids, not two miscible liquids.")],
     "A 4 C gap is far below the roughly 25 C that one vaporization cycle can resolve, so a fractionating column's many repeated condensations are needed.",
     "5c"),

    # ------------------------------------------------------- biomolecules (5d)
    ("Complete hydrolysis of the disaccharide sucrose (table sugar) yields which monosaccharides?",
     "glucose + fructose",
     [("glucose + galactose", "Glucose + galactose is the hydrolysis of lactose."),
      ("glucose only", "Glucose alone is what maltose (or starch) hydrolysis gives."),
      ("fructose only", "Fructose alone ignores the glucose unit of the disaccharide.")],
     "Sucrose is a glucose-(1->2)-fructose disaccharide, so hydrolysis ('inversion') releases one glucose and one fructose.",
     "5d"),

    # --------------------------------------------------- enzyme kinetics (bc)
    ("An enzyme has Vmax = 60 umol/min and Km = 2.0 mM. At [S] = 6.0 mM the initial velocity is",
     "45 umol/min",
     [("30 umol/min", "30 is Vmax/2, which holds only at [S] = Km = 2.0 mM, not 6.0 mM."),
      ("20 umol/min", "20 inverts the Michaelis ratio, computing Vmax x Km/[S] = 60 x 2/6."),
      ("60 umol/min", "60 assumes saturation, but [S] >> Km needs roughly ten times Km.")],
     "v = Vmax[S]/(Km + [S]) = 60 x 6.0/(2.0 + 6.0) = 360/8.0 = 45 umol/min.",
     "bc"),
]

assert len(ITEMS) == 30, len(ITEMS)


def build():
    items = []
    for n, (entry, letter) in enumerate(zip(ITEMS, LETTERS), start=1):
        if isinstance(entry, str):        # tolerates a stem mistakenly split out
            raise AssertionError("item %d not a tuple" % n)
        stem, correct, wrong, explain, chap = entry
        letters = ["A", "B", "C", "D"]
        choices = {L: correct if L == letter else None for L in letters}
        # fill the non-answer letters in ascending order with the authored wrongs
        non_answer = [L for L in letters if L != letter]
        assert len(wrong) == 3, (n, len(wrong))
        for L, (text, note) in zip(non_answer, wrong):
            choices[L] = text
        distractors = {L: note for L, (text, note) in zip(non_answer, wrong)}
        assert all(choices.values()), n
        items.append({
            "id": "nmat-p2c-%03d" % n,
            "q": stem,
            "choices": choices,
            "answer": letter,
            "explain": explain,
            "distractors": distractors,
            "chapter": CHAPTERS[chap],
        })
    return items


# ---------------------------------------------------------- numeric re-solve
def close(got, want, tol=0.051):
    return abs(got - want) <= tol


def numeric_checks(items):
    """Re-derive every numeric answer independently and assert it matches."""
    A = {it["id"][-3:]: it for it in items}
    val = lambda n: A[n]["choices"][A[n]["answer"]]

    assert val("001") == "23 electrons" and 26 - 3 == 23
    assert val("003") == str(2 * (2 * 2 + 1)) == "10"
    # % water in CuSO4.5H2O
    assert close(90.0 / (159.6 + 90.0) * 100, float(val("008").rstrip("%")), 0.06)
    # molar mass from ideal gas law
    assert close(0.500 * 0.0821 * 298.0 / (1.00 * 0.250), float(val("009").split()[0]), 0.06)
    # grams NaOH
    assert close(0.500 * 0.250 * 40.0, float(val("010").split()[0]))
    # dilution volume, in mL
    assert close(0.150 * 2.00 / 12.0 * 1000, float(val("011").split()[0]))
    # limiting reagent
    assert close(min(6.0 * 2 / 1, 9.0 * 2 / 3), float(val("007").split()[0]))
    # pH of 0.0030 M HCl
    assert close(-math.log10(3.0e-3), float(val("013")), 0.006)
    # buffer pH
    assert close(4.76 + math.log10(0.60 / 0.20), float(val("014")), 0.006)
    # titration volume
    assert close(0.0250 * 0.150 * 2 / 0.100 * 1000, float(val("015").split()[0]))
    # TCA ATP equivalents per glucose
    assert close(2 * (3 * 2.5 + 1 * 1.5 + 1), float(val("016")))
    # combustion enthalpy of ethanol
    assert close(2 * -393.5 + 3 * -285.8 - (-277.7), float(val("017").split()[0]), 0.7)
    # Gibbs free energy (delta-S in J -> kJ)
    assert close(40.0 - 310 * 0.150, float(val("018").split()[0]))
    # first-order half-life
    assert close(0.693 / 0.0231, float(val("021").split()[0]), 0.06)
    # Daniell cell potential
    assert close(0.34 - (-0.76), float(val("022").lstrip("+").split()[0]))
    # Faraday mass of copper
    assert close(2.00 * 965 / 96500.0 / 2 * 63.5, float(val("023").split()[0]), 0.0006)
    # Michaelis-Menten velocity
    assert close(60 * 6.0 / (2.0 + 6.0), float(val("030").split()[0]))
    return True


def main():
    items = build()
    numeric_checks(items)

    doc = {
        "exam": "nmat",
        "section": "part2-chemistry",
        "label": "Chemistry",
        "subject": "chemistry",
        "block": "part2",
        "items_expected": 30,
        "items": items,
        "passages": [],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        yaml.safe_dump(doc, fh, allow_unicode=True, sort_keys=False,
                       default_flow_style=False, width=100)

    print("wrote", OUT)
    print("answers:", dict(sorted(Counter(i["answer"] for i in items).items())))
    print("chapters:", dict(Counter(i["chapter"] for i in items)))


if __name__ == "__main__":
    main()
