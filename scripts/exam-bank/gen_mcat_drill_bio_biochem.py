#!/usr/bin/env python3
"""Generate content/exam-bank/mcat/drill/bio-biochem.yml (30 practice-only items).

Drill bank aimed at what the scored Bio/Biochem bank underrepresents: genetics
probability and enzyme-kinetics arithmetic worked with real numbers, plus a
spread of systems/biochem quantitative reasoning.

Every option list is written [correct, w1, w2, w3]; build() places the correct
option on the requested answer letter and the three wrong options on the
remaining letters in ascending order, so `distractors` keys are exactly the
three letters that are NOT the answer. Quantitative stems compute their answer
text from Python and re-assert it against a second independent expression.
"""
import math

import yaml
from collections import Counter

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/mcat/drill/bio-biochem.yml"
LETTERS = "ABCD"
IDPREFIX = "mcat-d-bb"


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


# answer-letter plan (30 items): A:8 B:8 C:7 D:7
KEYS = (["A", "B", "C", "D"] +       # 1-4
        ["B", "A", "D", "C"] +       # 5-8
        ["A", "B", "C", "D"] +       # 9-12
        ["D", "C", "B", "A"] +       # 13-16
        ["A", "B", "C", "D"] +       # 17-20
        ["B", "C", "D", "A"] +       # 21-24
        ["A", "B", "C", "D"] +       # 25-28
        ["A", "B"])                  # 29-30
assert len(KEYS) == 30

items = []

# ------------------------------------------------------ 1-5 genetics probability
# 1  autosomal recessive
items.append(build(
    1,
    "A and B are both heterozygous carriers of the same autosomal recessive allele. What is the "
    "probability that a child of theirs will be affected?",
    "1/4",
    [("1/2", "Treated the allele as dominant, in which case half the offspring would show it."),
     ("1/3", "That is the risk for a child known to be unaffected, a conditional that does not "
             "apply here."),
     ("0", "Assumed a carrier cannot transmit the allele to an affected child.")],
    KEYS[0],
    "Aa x Aa gives 1 AA : 2 Aa : 1 aa, so the probability of an affected (aa) child is 1/4.",
    "genetics"))

# 2  dihybrid self-cross
p2 = calc(2, 0.25 ** 2, 0.0625)
items.append(build(
    2,
    "Two individuals with genotype AaBb are crossed, and the two loci assort independently. What "
    "fraction of the offspring is expected to be aabb?",
    "1/16",
    [("1/4", "Squared nothing: this is the chance of one locus being homozygous recessive."),
     ("1/8", "Multiplied 1/4 by 1/2, mixing an incorrect single-locus probability into the product."),
     ("9/16", "That is the fraction showing both dominant phenotypes, not both recessive alleles.")],
    KEYS[1],
    "Each locus gives aa with probability 1/4, so aabb = 1/4 x 1/4 = %.4f = 1/16." % p2,
    "genetics"))

# 3  X-linked recessive
items.append(build(
    3,
    "A woman heterozygous for an X-linked recessive allele has children with a genotypically "
    "normal man. What fraction of their sons is expected to be affected?",
    "1/2",
    [("1/4", "That is the fraction of all children affected; the question asks only about sons."),
     ("all of them", "Boys receive their single X from the mother, not from the father."),
     ("none", "The mother's carrier status is enough to pass the allele to half her sons.")],
    KEYS[2],
    "Half the sons receive the mother's mutant X and half receive her normal X, so 1/2 of sons "
    "are affected (1/4 of all children).",
    "genetics"))

# 4  Hardy-Weinberg carriers
q4 = calc(4, math.sqrt(0.04), 0.20)
car4 = calc(4, 2 * 0.8 * 0.2, 0.32)
items.append(build(
    4,
    "In a population at Hardy-Weinberg equilibrium, 4% of individuals are born with an autosomal "
    "recessive condition. What fraction of the population consists of asymptomatic carriers?",
    "32%",
    [("4%", "That is q^2, the frequency of affected homozygotes, not of heterozygotes."),
     ("16%", "That is p^2, the frequency of homozygous normal individuals."),
     ("20%", "That is q, the allele frequency, rather than the heterozygote frequency.")],
    KEYS[3],
    "q^2 = 0.04 gives q = %.2f and p = 0.80, so 2pq = 2(0.80)(0.20) = %.2f, i.e. 32%%."
    % (q4, car4),
    "genetics"))

# 5  gamete diversity
g5 = calc(5, 2 ** 3, 8)
items.append(build(
    5,
    "An individual is trihybrid (AaBbCc) at three unlinked loci. How many genetically different "
    "gametes can that individual produce with respect to these loci?",
    "%d" % g5,
    [("3", "Counted the loci rather than the independent combinations of alleles."),
     ("6", "Treated the three loci as pairs that must assort together."),
     ("64", "That is the number of diploid zygote genotypes in a trihybrid self-cross (4^3), not "
            "the number of haploid gametes.")],
    KEYS[4],
    "Independent assortment gives 2^n gamete types = 2^3 = %d." % g5,
    "genetics"))

# ------------------------------------------------------------- 6-8 proteins
# 6  coding capacity and molecular weight
aa6 = calc(6, 300 / 3, 100)
mw6 = calc(6, aa6 * 110, 11000)
items.append(build(
    6,
    "A eukaryotic mRNA has a coding region of 300 nucleotides between the start and stop codons. "
    "Taking the average amino acid as 110 Da, what is the approximate mass of the polypeptide "
    "produced?",
    "11,000 Da",
    [("33,000 Da", "Multiplied all 300 nucleotides by 110 Da, ignoring that three nucleotides "
                   "specify one amino acid."),
     ("300 Da", "Reported the nucleotide count with the units of mass."),
     ("330 Da", "Divided by 300 rather than by 3 before scaling by 110 Da.")],
    KEYS[5],
    "300 nt / 3 = %d codons, so the peptide is %d amino acids and about %d x 110 Da = %s."
    % (aa6, aa6, aa6, "11,000 Da"),
    "1b-gene-to-protein"))

# 7  net charge of a peptide
items.append(build(
    7,
    "A tetrapeptide has a free N-terminus, a free C-terminus, one Lys residue and one Asp residue, "
    "and no other ionizable groups. What is its net charge at pH 7?",
    "0",
    [("+1", "Counted the N-terminus and Lys but ignored the deprotonated C-terminal carboxylate."),
     ("+2", "Counted only the basic groups (N-terminus and Lys side chain)."),
     ("-1", "Counted only the acidic groups and ignored the basic ones.")],
    KEYS[6],
    "At pH 7: N-terminus +1, Lys side chain +1, Asp side chain -1, C-terminus -1; the four charges "
    "sum to 0, so pH 7 sits at this peptide's isoelectric point.",
    "1a-proteins-and-amino-acids"))

# 8  Henderson-Hasselbalch
r8 = calc(8, 10 ** (7.4 - 6.8), 3.98)
items.append(build(
    8,
    "A buffer has pKa = 6.8. At pH 7.4, what is the ratio of deprotonated base to protonated acid "
    "([A-]/[HA])?",
    "4 : 1",
    [("1 : 4", "Inverted the Henderson-Hasselbalch ratio."),
     ("6 : 1", "Used the pH-pKa difference itself as the ratio."),
     ("1.2 : 1", "Reported the difference in pH units as a ratio of 1.2 to 1.")],
    KEYS[7],
    "pH = pKa + log([A-]/[HA]) gives log([A-]/[HA]) = 0.6, so [A-]/[HA] = 10^0.6 = %.1f, about "
    "4 : 1." % r8,
    "1a-proteins-and-amino-acids"))

# -------------------------------------------------------- 9-12 enzyme kinetics
v9 = calc(9, 90.0 * 2.0 / (1.0 + 2.0), 60.0)
items.append(build(
    9,
    "An enzyme has Vmax = 90 µmol/min. If the substrate concentration is twice the Km, what is the "
    "initial velocity?",
    "%.0f µmol/min" % v9,
    [("30. µmol/min", "Used Vmax/3 as if [S] were 0.5 Km rather than 2 Km."),
     ("90 µmol/min", "That is the velocity at saturating substrate, not at 2 Km."),
     ("45 µmol/min", "Reported Vmax/2, the velocity at [S] = Km, not at 2 Km.")],
    KEYS[8],
    "v = Vmax[S]/(Km + [S]); with [S] = 2Km, v = 90 x 2/(1 + 2) = %.0f µmol/min, two-thirds of "
    "Vmax." % v9,
    "biochemistry"))

# 10 glycolytic ATP
items.append(build(
    10,
    "How many ATP are produced per glucose by substrate-level phosphorylation in glycolysis alone?",
    "2",
    [("4", "That is the gross ATP made by the two payoff-phase phosphoglycerate kinases and "
           "pyruvate kinases, before subtracting the two invested in the priming phase."),
     ("36", "That is the order of complete oxidative phosphorylation of one glucose."),
     ("0", "Glycolysis does produce ATP; fermentation regenerates NAD+ without consuming it.")],
    KEYS[9],
    "Four ATP are made (1,3-BPG and PEP steps, x2) but two are spent by hexokinase and "
    "phosphofructokinase, leaving a net of 2 per glucose.",
    "1d-bioenergetics-and-fuel-metabolism"))

# 11 ATP per acetyl-CoA
atp11 = calc(11, 3 * 2.5 + 1 * 1.5 + 1, 10.0)
items.append(build(
    11,
    "One acetyl-CoA is oxidized completely through the citric acid cycle, yielding 3 NADH, "
    "1 FADH2 and 1 GTP. Using 2.5 ATP per NADH and 1.5 ATP per FADH2, what is the total ATP "
    "yield?",
    "%.0f ATP" % atp11,
    [("12.5 ATP", "That is the yield for one turn counted with the older 3/2 ATP-per-coenzyme "
                  "values plus GTP."),
     ("7.5 ATP", "Counted the three NADH only and dropped FADH2 and GTP."),
     ("4.0 ATP", "Counted only FADH2 and GTP, omitting the NADH contribution.")],
    KEYS[10],
    "3 x 2.5 + 1 x 1.5 + 1 = 7.5 + 1.5 + 1 = %.0f ATP per acetyl-CoA." % atp11,
    "1d-bioenergetics-and-fuel-metabolism"))

# 12 Michaelis-Menten arithmetic
v12 = calc(12, 100.0 * 0.80 / (0.20 + 0.80), 80.0)
items.append(build(
    12,
    "An enzyme has Vmax = 100 µmol/min and Km = 0.20 mM. At a substrate concentration of 0.80 mM, "
    "what is the reaction velocity?",
    "%.0f µmol/min" % v12,
    [("100 µmol/min", "That is Vmax; 0.80 mM is only four times Km, not saturating in this "
                      "framework."),
     ("50. µmol/min", "That is the velocity at [S] = Km, not at 0.80 mM."),
     ("20. µmol/min", "Reported the Km value in place of the velocity.")],
    KEYS[11],
    "v = Vmax[S]/(Km + [S]) = 100 x 0.80/(0.20 + 0.80) = %.0f µmol/min, i.e. 80%% of Vmax."
    % v12,
    "biochemistry"))

# --------------------------------------------------- 13-16 replication/maps/mitosis
# 13 Meselson-Stahl
frac13 = calc(13, 2 / 8, 0.25)
items.append(build(
    13,
    "DNA labeled with heavy nitrogen (15N) is shifted into a 14N medium and allowed to replicate "
    "for three rounds by the semiconservative mechanism. What fraction of the resulting duplexes "
    "still contains 15N?",
    "1/4",
    [("3/4", "That is the fraction containing only 14N, the complement of what was asked."),
     ("1/8", "Treated the heavy strands as diluted across eight duplexes as if each kept a whole "
             "15N molecule per duplex."),
     ("1/2", "Assumed semiconservative replication keeps the heavy strands paired together.")],
    KEYS[12],
    "Three rounds give 8 duplexes; the two 15N/14N hybrids persist forever, so 2/8 = %.2f."
    % frac13,
    "1c-heritable-information-diversity"))

# 14 map distance
d14 = calc(14, 120 / 1000 * 100.0, 12.0)
items.append(build(
    14,
    "A testcross of a dihybrid produces 1000 progeny, of which 120 show recombinant phenotypes. "
    "What is the map distance between the two genes?",
    "12 cM",
    [("0.12 cM", "Reported the recombinant fraction without converting it to map units."),
     ("88 cM", "Used the parental fraction instead of the recombinant fraction."),
     ("120 cM", "Skipped the division by the total progeny.")],
    KEYS[13],
    "Map distance = recombinants/total x 100 = 120/1000 x 100 = %.0f cM." % d14,
    "1c-heritable-information-genetic-diversity"))

# 15 meiosis products
items.append(build(
    15,
    "A diploid cell has 2n = 24. What does each gamete contain after meiosis II is complete?",
    "12 chromosomes, each with one chromatid",
    [("24 chromosomes, each with one chromatid", "That is the chromosome number of the parent in "
                                                 "G1, not of a gamete."),
     ("12 chromosomes, each with two chromatids", "That describes a meiosis I product before "
                                                  "sister chromatids separate."),
     ("6 chromosomes, each with one chromatid", "Halved the haploid number as well as the ploidy.")],
    KEYS[14],
    "Meiosis halves the chromosome number to n = 12 and meiosis II separates sister chromatids, "
    "so each gamete has 12 unreplicated chromosomes.",
    "2c-cell-division-differentiation-specialization"))

# 16 tonicity
items.append(build(
    16,
    "A cell whose cytosol is 300 mOsm/L is placed in a 300 mM NaCl solution (assume NaCl "
    "dissociates completely). What happens to the cell?",
    "It shrinks, because the solution is about 600 mOsm/L and water leaves the cell",
    [("It stays the same size, because 300 mM NaCl is 300 mOsm/L",
      "Confused molarity with osmolarity: each NaCl gives two osmotically active particles."),
     ("It swells and may lyse, because the solution is 150 mOsm/L",
      "Divided the sodium concentration by two instead of multiplying it."),
     ("It shrinks, because NaCl cannot cross the membrane and the solution is 300 mOsm/L",
      "Reached the right direction but with an osmolarity that is half the true value.")],
    KEYS[15],
    "Complete dissociation makes the solution 2 x 300 = 600 mOsm/L, twice the cytosol, so it is "
    "hypertonic and osmosis draws water out of the cell.",
    "cells-and-cellular-processes"))

# ------------------------------------------------------------ 17-20 scale/growth
# 17 surface-to-volume
sa17 = calc(17, 6 * 2.0 ** 2 / 2.0 ** 3, 3.0)
items.append(build(
    17,
    "A spherical cell doubles its diameter. Its surface-area-to-volume ratio changes by what "
    "factor?",
    "It is halved",
    [("It doubles", "Both surface area and volume grow, but not by the same power of the radius."),
     ("It is unchanged", "The ratio depends on radius, so it cannot stay constant while the cell "
                         "grows."),
     ("It quadruples", "Surface area grows fourfold, but volume grows eightfold.")],
    KEYS[16],
    "SA/V scales as r^2/r^3 = 1/r, so doubling the radius (or diameter) halves the ratio; for a "
    "cube it goes from 6 to %.0f." % sa17,
    "2a-assemblies-of-molecules-cells-and-cell-groups"))

# 18 bacterial exponential growth
n18 = calc(18, 100 * 2 ** 5, 3200)
items.append(build(
    18,
    "A culture starts with 100 bacteria that divide every 20 minutes. Ignoring cell death, how "
    "many bacteria are present after 100 minutes?",
    "%d" % n18,
    [("600", "Assumed linear growth of 100 per division cycle instead of doubling."),
     ("1600", "Counted four doublings (80 minutes) instead of five."),
     ("500", "Added one cell per generation rather than doubling the population.")],
    KEYS[17],
    "100 minutes / 20 minutes = 5 doublings, so N = 100 x 2^5 = %d." % n18,
    "2b-prokaryotes-and-viruses"))

# 19 Nernst potential for potassium
e19 = calc(19, 61.0 * math.log10(5.0 / 150.0), -90.1)
items.append(build(
    19,
    "For a neuron at 37 °C with [K+]out = 5 mM and [K+]in = 150 mM, the potassium equilibrium "
    "potential is E = 61 mV x log10([K+]out/[K+]in). What is E?",
    "%.0f mV" % e19,
    [("+90 mV", "Inverted the concentration ratio, which flips the sign of the logarithm."),
     ("-45 mV", "Reported half the calculated potential."),
     ("-1.5 mV", "Reported the logarithm itself (-1.48) without multiplying by 61 mV.")],
    KEYS[18],
    "E = 61 x log10(5/150) = 61 x (-1.477) = %.0f mV, close to a typical resting potential."
    % e19,
    "3a-nervous-and-endocrine-systems"))

# 20 cardiac output
co20 = calc(20, 72 * 70 / 1000.0, 5.04)
items.append(build(
    20,
    "A patient has a heart rate of 72 beats/min and a stroke volume of 70 mL. What is the cardiac "
    "output?",
    "5.0 L/min",
    [("5040 L/min", "Never converted milliliters to liters."),
     ("0.98 L/min", "Divided the stroke volume by the heart rate instead of multiplying."),
     ("142 mL/min", "Added the two numbers instead of multiplying them.")],
    KEYS[19],
    "Cardiac output = heart rate x stroke volume = 72 x 70 mL = %.0f mL/min ≈ %.1f L/min."
    % (co20 * 1000, co20),
    "3b-main-organ-systems"))

# ---------------------------------------------------------- 21-24 systems/ecology
# 21 ADH feedback
items.append(build(
    21,
    "After several hours of heavy sweating, plasma osmolarity rises. Which change follows through "
    "the normal homeostatic response?",
    "ADH secretion increases, and the collecting ducts reabsorb more water to produce a small "
    "volume of concentrated urine",
    [("ADH secretion decreases, and the collecting ducts reabsorb more water",
      "Reabsorption and ADH secretion move together; a fall in ADH would dilute the urine."),
     ("Aldosterone secretion increases, and the kidneys excrete a large volume of dilute urine",
      "Excreting dilute urine would worsen the water loss that raised osmolarity."),
     ("ADH secretion increases, and the loop of Henle is bypassed so that dilute urine is released",
      "ADH does not bypass the loop of Henle; it increases water permeability distal to it.")],
    KEYS[20],
    "Raised osmolarity is sensed by hypothalamic osmoreceptors, which increase ADH release from "
    "the posterior pituitary; ADH inserts aquaporins in the collecting duct, so water is retained "
    "and the urine becomes concentrated. This is negative feedback restoring osmolarity.",
    "life-processes-regulation-and-homeostasis"))

# 22 cleavage divisions
cells22 = calc(22, 2 ** 4, 16)
items.append(build(
    22,
    "After four cleavage divisions of a zygote, how many cells does the embryo contain, and how "
    "does each cell's volume compare with that of the zygote?",
    "%d cells, each one-sixteenth the volume of the zygote" % cells22,
    [("16 cells, each 16 times the volume of the zygote", "Reversed the volume relationship; "
                                                          "cleavage divides the cytoplasm."),
     ("8 cells, each one-eighth the volume of the zygote", "Counted three divisions, not four."),
     ("16 cells, each the same volume as the zygote", "Ignored that cleavage occurs without "
                                                      "growth between divisions.")],
    KEYS[21],
    "Four divisions give 2^4 = %d cells, and because the embryo does not grow during cleavage each "
    "blastomere holds 1/%d of the original cytoplasm." % (cells22, cells22),
    "development"))

# 23 energy pyramid
e23 = calc(23, 10000 * 0.1 ** 3, 10.0)
items.append(build(
    23,
    "Producers in an ecosystem capture 10,000 kJ of energy per square meter per year. Using the "
    "10% rule, how much energy reaches the tertiary consumer level?",
    "%.0f kJ" % e23,
    [("1000 kJ", "Stopped at the primary consumer level, one transfer in."),
     ("100 kJ", "Stopped at the secondary consumer level, two transfers in."),
     ("100,000 kJ", "Multiplied by 10 at each step instead of dividing by 10.")],
    KEYS[22],
    "Three transfers from producer to tertiary consumer give 10,000 x (0.1)^3 = %.0f kJ."
    % e23,
    "organisms-and-their-environment"))

# 24 cladistics
items.append(build(
    24,
    "Characters are scored for four species. Species 1 and 2 have fur; species 3 and 4 have scales. "
    "Which statement is consistent with cladistic analysis?",
    "Species 1 and 2 share a more recent common ancestor with each other than either shares with "
    "species 3, because fur is a shared derived character",
    [("Species 1 and 2 are closest because fur is ancestral to all four species",
      "An ancestral (plesiomorphic) character cannot diagnose a clade, and scales rather than fur "
      "are ancestral here."),
     ("Species 3 and 4 are closest because scales are a shared derived character unique to them",
      "Scales are the ancestral state shared with the outgroup, so they do not group 3 with 4 as "
      "a derived clade."),
     ("All four species are equally related because they share a common ancestor",
      "True in principle but uninformative; cladistics ranks recency of common ancestry using "
      "shared derived characters.")],
    KEYS[23],
    "Only shared derived characters (synapomorphies) define clades. Fur is derived within this "
    "set and is shared by 1 and 2, so they form a clade separate from the scaled species.",
    "unity-and-diversity-of-life"))

# ----------------------------------------------------- 25-28 photosynthesis/enzymes
# 25 photosynthetic stoichiometry
co225 = calc(25, 90.0 / 180.0 * 6 * 44.0, 132.0)
items.append(build(
    25,
    "In photosynthesis, 6 CO2 + 6 H2O → C6H12O6 + 6 O2. What mass of CO2 (44 g/mol) is required "
    "to produce 90 g of glucose (180 g/mol)?",
    "%.0f g" % co225,
    [("44 g", "Assumed a 1:1 ratio of CO2 to glucose rather than 6:1."),
     ("264 g", "Scaled for a full mole of glucose (6 mol CO2) rather than 0.5 mol."),
     ("30. g", "Divided the glucose mass by 3, as if the ratio were 2:1.")],
    KEYS[24],
    "90 g glucose = 0.50 mol, needing 6 x 0.50 = 3.0 mol CO2 = 3.0 x 44 = %.0f g." % co225,
    "the-world-of-plants-and-animals"))

# 26 Lineweaver-Burk
km26 = calc(26, 1.0 / 5.0, 0.20)
items.append(build(
    26,
    "A Lineweaver-Burk plot of an uncatalyzed-free enzyme gives a y-intercept of 0.010 "
    "(min·µmol^-1) and an x-intercept of -5.0 mM^-1. What is Km?",
    "%.2f mM" % km26,
    [("5.0 mM", "Reported the x-intercept itself; Km is -1/slope-intercept, i.e. -1/x-intercept."),
     ("100 µmol/min", "That is Vmax, read from the y-intercept."),
     ("0.010 mM", "Used the y-intercept value as if it were the x-intercept.")],
    KEYS[25],
    "The x-intercept equals -1/Km = -5.0 mM^-1, so Km = 1/5.0 = %.2f mM." % km26,
    "biochemistry"))

# 27 peptide bonds
bonds27 = calc(27, 51 - 1, 50)
items.append(build(
    27,
    "How many peptide bonds are formed when a 51-residue polypeptide is assembled from its free "
    "amino acids?",
    "%d" % bonds27,
    [("51", "Counted the residues; the number of bonds is one less than the number of residues."),
     ("49", "Subtracted twice instead of once."),
     ("102", "Doubled the count, as if each bond involved two residues on both sides.")],
    KEYS[26],
    "N residues are joined by N - 1 peptide bonds = 51 - 1 = %d, releasing %d water molecules."
    % (bonds27, bonds27),
    "chemistry-of-biochemistry-cem"))

# 28 signal amplification
amp28 = calc(28, 80 * 1000, 80000)
items.append(build(
    28,
    "One activated epinephrine receptor activates 80 G proteins. Each G protein activates an "
    "adenylyl cyclase that produces 1000 molecules of cAMP. Approximately how many cAMP molecules "
    "result from a single activated receptor?",
    "{:,}".format(amp28),
    [("1000", "Counted one cyclase product and ignored the 80-fold branch at the G-protein step."),
     ("80", "Counted the G proteins but not the second messenger each generates."),
     ("80,000,000", "Multiplied by an extra factor of 1000, as if each cAMP generated another "
                    "1000 molecules.")],
    KEYS[27],
    "Amplification multiplies at each step: 80 G proteins x 1000 cAMP each = %s cAMP."
    % "{:,}".format(amp28),
    "cells-and-cellular-processes"))

# --------------------------------------------------------------- 29-30 expression
# 29 coding capacity after splicing
cod29 = calc(29, 501 // 3 - 1, 166)
items.append(build(
    29,
    "A pre-mRNA contains two introns totalling 700 nucleotides. After splicing, the mature mRNA's "
    "coding region is 501 nucleotides from start codon to and including the stop codon. How many "
    "amino acids does the protein contain?",
    "%d" % cod29,
    [("167", "Divided by three but forgot that the last codon is a stop signal."),
     ("501", "Reported the nucleotide count as an amino acid count."),
     ("100", "Subtracted the introns a second time, as if they were still in the mature RNA.")],
    KEYS[28],
    "501 nt = 167 codons; the last one is the stop codon, leaving 167 - 1 = %d amino acids."
    % cod29,
    "1b-gene-to-protein"))

# 30 binomial probability
p30 = calc(30, 0.75 ** 3, 0.4219)
items.append(build(
    30,
    "Two carriers of an autosomal recessive condition have three children. What is the probability "
    "that all three are unaffected?",
    "27/64",
    [("3/4", "That is the probability for one child, not for three independent births."),
     ("1/64", "That is the probability that all three are affected, (1/4)^3."),
     ("9/16", "Multiplied 3/4 by 3/4, covering only two of the three births.")],
    KEYS[29],
    "Each child has a 3/4 chance of being unaffected, so (3/4)^3 = %d/%d = %.4f."
    % (27, 64, p30),
    "genetics"))

# --------------------------------------------------------------------- assemble
doc = {
    "exam": "mcat",
    "section": "drill-bio-biochem",
    "label": "Bio/Biochem drill",
    "subject": "bio-biochem",
    "block": "bio-biochem",
    "_drill": True,
    "items_expected": len(items),
    "items": items,
    "passages": [],
}
assert len(items) == 30 == doc["items_expected"], len(items)
assert len({i["id"] for i in items}) == 30
allowed = {"cells-and-cellular-processes", "development", "genetics",
           "life-processes-regulation-and-homeostasis", "organisms-and-their-environment",
           "the-world-of-plants-and-animals", "unity-and-diversity-of-life",
           "1c-heritable-information-genetic-diversity",
           "2a-assemblies-of-molecules-cells-and-cell-groups", "2b-prokaryotes-and-viruses",
           "2c-cell-division-differentiation-specialization", "3a-nervous-and-endocrine-systems",
           "3b-main-organ-systems", "1a-proteins-and-amino-acids", "1b-gene-to-protein",
           "1c-heritable-information-diversity", "1d-bioenergetics-and-fuel-metabolism",
           "chemistry-of-biochemistry-cem", "biochemistry"}
assert {i["chapter"] for i in items} <= allowed
letters = Counter(i["answer"] for i in items)
assert max(letters.values()) <= 8, letters
assert len({i["q"] for i in items}) == 30

with open(OUT, "w") as fh:
    yaml.safe_dump(doc, fh, sort_keys=False, allow_unicode=True, width=100)

print("wrote", OUT)
print("answers:", dict(sorted(letters.items())))
print("chapters:", dict(Counter(i["chapter"] for i in items)))
