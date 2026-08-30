#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/drill/part2-chemistry.yml (25 practice drills).

Practice-only companion to part2-chemistry.yml: standalone MCQs, no passages, no
mock-blueprint role (drill/ files carry _drill). Angles the main bank does not
drill: second-step colligative arithmetic, ICE-square-root weak acids, Ksp,
heterogeneous equilibrium expressions, conduction-vs-dissociation traps, and
cross-links between organic mechanism and biochemistry.

Authoring form is (stem, correct_text, [(wrong_text, error_note) x 3], chapter).
A fixed balanced key pattern places the correct choice; the three wrong choices
fill the remaining letters in order, so an error note can never land on the
answer letter.
"""
import os
from collections import Counter

import yaml

OUT = ("/home/ubuntu/django-wsgi/"
       "content/exam-bank/nmat/drill/part2-chemistry.yml")

# 25 slots -> A:6 B:7 C:6 D:6
KEYS = ["A", "B", "C", "D", "D", "A", "B", "C",
        "C", "D", "A", "A", "B", "C", "D", "D",
        "A", "B", "C", "D", "D", "A", "B", "C",
        "B"]

C4E = "4e-atoms-nuclear-decay-electronic-structure"
C5A = "5a-unique-nature-of-water-and-its-solutions"
C5B = "5b-molecules-and-intermolecular-interactions"
C5C = "5c-separation-and-purification-methods"
C5D = "5d-biologically-relevant-molecules"
C5E = "5e-chemical-thermodynamics-and-kinetics"
ANAL = "analytical-chemistry"
BIO = "biochemistry"
GEN = "general-chemistry"
ORG = "organic-chemistry"

ITEMS = [
    ("A compound is found by analysis to contain 40.0% C, 6.70% H and 53.3% O by "
     "mass. What is its empirical formula?",
     "CH2O",
     [("C2H4O2", "doubled every ratio before reducing it to the simplest whole numbers"),
      ("C3H6O3", "kept the 1:2:1 ratio tripled instead of reducing it to the smallest whole numbers"),
      ("CH2O2", "rounded the oxygen ratio up instead of dividing all three by the smallest")],
     GEN),

    ("How many oxygen atoms are present in 0.250 mol of CO2?",
     "3.01 x 10^23",
     [("1.51 x 10^23", "forgot that each CO2 molecule carries two oxygen atoms"),
      ("6.02 x 10^23", "treated 0.250 mol as if it were 1.00 mol"),
      ("0.500 x 10^23", "reported the moles of oxygen atoms as a count of atoms")],
     GEN),

    ("How many liters of H2, measured at STP, are produced when 0.500 mol of zinc "
     "reacts completely with excess hydrochloric acid? (Zn + 2 HCl -> ZnCl2 + H2)",
     "11.2 L",
     [("22.4 L", "read the coefficient 2 in front of HCl as applying to the hydrogen gas"),
      ("5.60 L", "divided by 2 as if 2 mol of H2 came from 1 mol of Zn"),
      ("0.500 L", "quoted the mole number as though it were a molar volume")],
     GEN),

    ("Radon-222 (Z = 86) decays by alpha emission. What is the daughter nuclide?",
     "polonium-218 (A = 218, Z = 84)",
     [("radon-218 (A = 218, Z = 86)", "subtracted 4 from the mass number but not from the atomic number"),
      ("astatine-218 (A = 218, Z = 85)", "treated alpha decay as the loss of a single proton"),
      ("radon-226 (A = 226, Z = 86)", "added the alpha particle to the nucleus instead of ejecting it")],
     C4E),

    ("O2-, F-, Na+ and Mg2+ all contain 10 electrons. Which is the largest?",
     "O2-",
     [("Mg2+", "assumed that more protons means a larger ion, when they pull the same 10 electrons in tighter"),
      ("Na+", "reasoned from the size of the neutral sodium atom rather than its ion"),
      ("F-", "judged by atomic size in the periodic table instead of by charge among isoelectronic species")],
     C4E),

    ("How many unpaired electrons does a ground-state nitrogen atom (1s2 2s2 2p3) "
     "have?",
     "3, one in each of the three 2p orbitals",
     [("1", "paired two of the 2p electrons before each 2p orbital held one, violating Hund's rule"),
      ("0", "assumed the 2p subshell is fully occupied; it holds only three of six possible electrons"),
      ("5", "counted the 2s pair as unpaired along with the three 2p electrons")],
     C4E),

    ("Which 1.0-m aqueous solution has the LOWEST freezing point?",
     "1.0 m NaCl",
     [("1.0 m glucose", "treated a nonelectrolyte as if it supplied as many particles as an electrolyte"),
      ("0.50 m CaCl2", "compared molalities instead of total particles (0.50 x 3 = 1.5 m)"),
      ("1.0 m sucrose", "assumed sucrose, a nonelectrolyte, splits into several particles")],
     C5A),

    ("What is the boiling point of a solution made by dissolving 0.50 mol of NaCl "
     "in 500 g of water? (Kb = 0.512 C/m)",
     "101.0 C",
     [("100.3 C", "used 0.50 as the molality and never divided by the 0.500 kg of water"),
      ("100.5 C", "forgot to double for dissociation, using i = 1"),
      ("102.0 C", "took i = 4, as if NaCl dissociated into four particles")],
     C5A),

    ("A 0.10 M solution of a weak acid HA has Ka = 1.0 x 10^-5. What is its pH?",
     "3.00",
     [("1.00", "assumed complete dissociation, as for a strong acid"),
      ("5.00", "quoted pKa as though it were the solution's pH"),
      ("2.00", "guessed 10% dissociation, giving 0.010 M H+ instead of 0.0010 M")],
     C5A),

    ("When 25.0 mL of 0.100 M acetic acid is titrated with 0.100 M NaOH, the pH at "
     "the equivalence point is",
     "greater than 7, because the acetate ion hydrolyzes to produce OH-",
     [("exactly 7, because the acid and base neutralize one another",
       "that holds for strong acid plus strong base; here the conjugate base is weakly basic"),
      ("less than 7, because some acetic acid remains unreacted",
       "at the equivalence point the acid is fully converted to acetate"),
      ("equal to pKa = 4.76, because the acid and base are present in equal amounts",
       "that is the half-equivalence point; at equivalence only the conjugate base remains")],
     ANAL),

    ("The Ksp of AgCl is 1.8 x 10^-10. What is its molar solubility in pure water?",
     "1.3 x 10^-5 M",
     [("1.8 x 10^-10 M", "quoted Ksp itself as the molar solubility"),
      ("9.0 x 10^-11 M", "halved Ksp instead of taking its square root"),
      ("2.7 x 10^-5 M", "doubled the square root, writing Ksp = 2s^2 rather than s^2")],
     ANAL),

    ("In acidic solution, how many moles of Fe2+ can 1.0 mol of dichromate ion "
     "(Cr2O7^2- -> 2 Cr3+) oxidize?",
     "6.0 mol",
     [("2.0 mol", "matched the two chromium atoms instead of the electrons they absorb"),
      ("3.0 mol", "used the 3-electron change per chromium but forgot there are two chromium atoms"),
      ("1.0 mol", "matched the ions one to one without balancing the electron transfer")],
     ANAL),

    ("Burning 0.50 g of a fuel raises the temperature of 100 g of water by 8.0 C. "
     "What is the heat of combustion per gram of fuel? (c_water = 4.18 J/(g C))",
     "6.7 kJ/g",
     [("3.3 kJ/g", "reported the total heat released as if it were the per-gram value"),
      ("13.4 kJ/g", "divided the heat by 0.25 g instead of by the 0.50 g burned"),
      ("67 kJ/g", "used 1.0 kg of water instead of 100 g")],
     C5E),

    ("A reaction takes 24 h at 20 C, and its rate doubles for every 10 C rise. "
     "How long should it take at 40 C?",
     "about 6.0 h",
     [("about 12 h", "applied the doubling for only one 10-C step instead of two"),
      ("about 48 h", "reversed the effect of temperature and slowed the reaction down"),
      ("about 1.5 h", "halved the time for each step, multiplying the rate by 16")],
     C5E),

    ("A catalyst is added to a gaseous reaction mixture. Which statement is "
     "correct?",
     "It lowers the activation energy in both directions, so equilibrium is reached "
     "faster while K is unchanged",
     [("It shifts the equilibrium toward products and raises the yield",
       "a catalyst cannot change the position of equilibrium, only the time to reach it"),
      ("It lowers the activation energy of the forward reaction only, so K increases",
       "a catalyst must accelerate the reverse step equally, or it would violate thermodynamics"),
      ("It raises the temperature of the mixture, which speeds the reaction",
       "the rate gain comes from a lower Ea, not from added heat")],
     C5E),

    ("For the equilibrium CaCO3(s) <=> CaO(s) + CO2(g), the correct expression for "
     "Kc is",
     "Kc = [CO2]",
     [("Kc = [CaO][CO2]/[CaCO3]",
       "included the pure solids, whose concentrations are constant and omitted from Kc"),
      ("Kc = 1/([CaO][CO2])", "inverted the expression and still kept the solid CaO"),
      ("Kc = [CaCO3]/([CaO][CO2])", "wrote the reverse reaction's form and kept the solid in it")],
     C5E),

    ("Molten NaCl is electrolyzed using inert electrodes. What forms at each "
     "electrode?",
     "sodium at the cathode and chlorine gas at the anode",
     [("chlorine at the cathode and sodium at the anode",
       "reversed the electrode polarities' roles; reduction, not oxidation, happens at the cathode"),
      ("hydrogen at the cathode and oxygen at the anode",
       "there is no water in a molten salt, so no H+ or OH- exists to discharge"),
      ("nothing, because a molten salt does not conduct electricity",
       "molten salts conduct well, since the ions are mobile without a crystal lattice")],
     GEN),

    ("Glycerol, with three -OH groups per molecule, is far more viscous than "
     "ethanol, with one. The best explanation is that",
     "the extra -OH groups let glycerol form far more hydrogen bonds to neighboring "
     "molecules",
     [("glycerol molecules are partly ionized, so ionic attractions hold the liquid together",
       "alcohol -OH groups hydrogen-bond but do not ionize appreciably in the pure liquid"),
      ("viscosity rises with molar mass alone, and glycerol is simply heavier",
       "molar mass matters only insofar as it brings more interaction sites, which is the real cause"),
      ("ethanol's single -OH forms stronger hydrogen bonds than glycerol's three",
       "one -OH cannot outweigh three; ethanol simply offers fewer bonding opportunities")],
     C5B),

    ("2-bromo-2-methylpropane, a tertiary halide, reacts with water as the only "
     "nucleophile in a polar protic solvent. The mechanism and outcome are",
     "SN1, giving a planar carbocation so the alcohol forms as a racemic mixture",
     [("SN2, with back-side attack and inversion at the carbon",
       "a tertiary carbon blocks back-side attack, and the polar protic solvent favors ionization"),
      ("SN1, with complete inversion because the leaving group shields one face",
       "the free carbocation is planar, so attack comes from both faces equally"),
      ("SN2, with retention because water attacks from the leaving group's side",
       "SN2 attack is from the side opposite the leaving group, giving inversion")],
     ORG),

    ("How many constitutional isomers does C5H12 have?",
     "3",
     [("2", "missed the most-branched isomer, 2,2-dimethylpropane"),
      ("5", "took the number of carbons in the formula as the number of skeletons"),
      ("12", "counted every hydrogen position as though it were a distinct skeleton")],
     ORG),

    ("2-bromobutane is heated with ethanolic KOH, which promotes elimination. "
     "Which alkene is the major product?",
     "2-butene, the more substituted alkene",
     [("1-butene, because elimination removes the nearest beta hydrogen",
       "Zaitsev's rule favors the alkene with more alkyl substituents, not the nearer beta carbon"),
      ("butane, because KOH replaces the bromine with hydrogen",
       "ethanolic KOH promotes elimination rather than reduction"),
      ("2-methylpropene, because a rearranged skeleton is more substituted",
       "the carbon skeleton is conserved in E2 elimination; no rearrangement occurs")],
     ORG),

    ("How many water molecules are required to hydrolyze a pentapeptide completely "
     "into five free amino acids?",
     "4, one per peptide bond",
     [("5, one per amino acid produced",
       "the last residue is released without breaking a bond; only the links between residues need water"),
      ("3, one fewer than the number of residues",
       "a pentapeptide contains four peptide bonds, not three"),
      ("1, since a single water molecule can split the whole chain",
       "each peptide bond needs its own water molecule")],
     C5D),

    ("Analysis of a sample of double-stranded DNA shows that 30% of its bases are "
     "adenine. What are the percentages of cytosine and guanine?",
     "cytosine 20% and guanine 20%",
     [("cytosine 35% and guanine 35%",
       "forgot that thymine must equal adenine, leaving only 40% for G plus C"),
      ("cytosine 30% and guanine 30%",
       "assumed all four bases occur equally, contradicting the 30% adenine given"),
      ("cytosine 15% and guanine 15%",
       "split the 30% adenine figure between C and G instead of working from the 100% total")],
     BIO),

    ("A competitive inhibitor is added to an enzyme reaction. How do the apparent "
     "Km and Vmax change?",
     "Km increases and Vmax is unchanged",
     [("Km is unchanged and Vmax decreases, which is what happens with a noncompetitive inhibitor",
       "that describes noncompetitive inhibition, which lowers the active enzyme's effective amount"),
      ("both Km and Vmax decrease",
       "a competitive inhibitor can be overcome at high substrate, so Vmax survives"),
      ("Km decreases and Vmax increases",
       "an inhibitor cannot raise the enzyme's apparent affinity or its maximum rate")],
     BIO),

    ("A solid sample consists of benzoic acid contaminated with sand and a little "
     "sodium chloride. The best purification is to",
     "dissolve in hot water, filter off the sand, and cool the filtrate so the "
     "benzoic acid recrystallizes",
     [("heat the mixture strongly and distill the benzoic acid over",
       "benzoic acid sublimes and decomposes near its boiling point, and the salt is nonvolatile"),
      ("dissolve everything in water and evaporate to dryness, leaving pure acid",
       "evaporation keeps the salt with the acid; it cannot separate them"),
      ("separate the dry powder by filtration, since the salt crystals are larger than the acid crystals",
       "dry filtration cannot part two solids; a separation needs a difference in solubility or volatility")],
     C5C),
]

EXPLANATIONS = [
    "Dividing each mass by its atomic mass gives 3.33 mol C, 6.65 mol H and 3.33 mol O; dividing "
    "all by 3.33 yields 1 : 2 : 1, so the empirical formula is CH2O.",
    "0.250 mol x 2 O atoms per molecule = 0.500 mol of O atoms, and 0.500 x 6.02 x 10^23 = 3.01 x "
    "10^23 atoms.",
    "The equation shows 1 mol Zn -> 1 mol H2, so 0.500 mol Zn gives 0.500 mol H2 = 0.500 x 22.4 L "
    "= 11.2 L at STP.",
    "An alpha particle carries away 2 protons and 2 neutrons, so A drops from 222 to 218 and Z from "
    "86 to 84, which is polonium.",
    "All four species hold 10 electrons; with equal electron counts, the nucleus with the fewest "
    "protons (oxygen, 8) attracts them least, so O2- is largest.",
    "Hund's rule puts the three 2p electrons into separate orbitals with parallel spins, so all "
    "three are unpaired and the 2s pair is not.",
    "Freezing point depression tracks total dissolved particles: glucose and sucrose give 1.0 m, "
    "CaCl2 gives 1.5 m, and NaCl gives 2.0 m, so NaCl freezes lowest.",
    "The molality is 0.50 mol/0.500 kg = 1.0 m, so the effective particle molality is 2.0 m and "
    "dTb = 0.512 x 2.0 = 1.0 C, giving 101.0 C.",
    "For a weak acid [H+] = sqrt(Ka C) = sqrt(1.0 x 10^-5 x 0.10) = sqrt(1.0 x 10^-6) = 1.0 x "
    "10^-3 M, so pH = 3.00.",
    "At the equivalence point only sodium acetate remains; acetate hydrolyzes to give OH-, so the "
    "solution is basic (about pH 8.7).",
    "Ksp = s^2 for a 1:1 salt, so s = sqrt(1.8 x 10^-10) = 1.3 x 10^-5 M.",
    "Each chromium drops from +6 to +3, taking 3 electrons, and there are two chromium atoms, so 6 "
    "Fe2+ are oxidized per dichromate.",
    "q = (100 g)(4.18 J/g C)(8.0 C) = 3.34 kJ for 0.50 g, which is 3.34/0.50 = 6.7 kJ per gram.",
    "Two 10-degree steps quadruple the rate, and 24 h / 4 = 6.0 h.",
    "A catalyst lowers Ea for both forward and reverse steps by the same amount, so equilibrium "
    "arrives sooner but K and the yield are untouched.",
    "Pure solids and pure liquids have constant concentrations and are excluded, leaving only the "
    "gas: Kc = [CO2].",
    "In molten NaCl the mobile ions carry current; Na+ is reduced at the cathode and Cl- is "
    "oxidized at the anode.",
    "More -OH groups mean more hydrogen-bonding sites per molecule, so the liquid's internal "
    "friction (viscosity) rises sharply.",
    "A tertiary halide in a polar protic solvent ionizes to a planar tertiary carbocation; water "
    "then attacks either face, giving equal enantiomers.",
    "C5H12 has three skeletons: n-pentane, 2-methylbutane and 2,2-dimethylpropane.",
    "In an E2 elimination the more substituted alkene is favored (Zaitsev), so 2-butene "
    "(trans-major) exceeds 1-butene.",
    "A pentapeptide has four peptide bonds, and hydrolysis consumes one water per bond, so four "
    "water molecules are needed.",
    "Chargaff's rules give T = A = 30%, so G plus C = 40% and, being equal, C = G = 20%.",
    "A competitive inhibitor competes for the active site, so more substrate is needed to reach "
    "half-maximal velocity (higher Km) while the ceiling (Vmax) is still attainable.",
    "Benzoic acid is much more soluble in hot water than cold, salt stays dissolved on cooling, "
    "and the sand is removed by hot filtration: recrystallization.",
]


def main() -> None:
    assert len(ITEMS) == 25 and len(KEYS) == 25 and len(EXPLANATIONS) == 25
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
            "id": f"nmat-d-p2c-{n:03d}",
            "q": " ".join(q.split()),
            "choices": choices,
            "answer": key,
            "explain": " ".join(explain.split()),
            "distractors": distractors,
            "chapter": chapter,
        })

    doc = {
        "exam": "nmat",
        "section": "drill-part2-chemistry",
        "label": "Chemistry drill",
        "subject": "chemistry",
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
