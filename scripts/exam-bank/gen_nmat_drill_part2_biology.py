#!/usr/bin/env python3
"""Generate content/exam-bank/nmat/drill/part2-biology.yml (25 practice drills).

Practice-only companion to part2-biology.yml: standalone MCQs, no passages, no
mock-blueprint role (the loader tags drill/ files _drill, so they never count
toward blueprint totals). Items drill the high-frequency / easy-to-miss angles
the main bank does not: cross-topic integration, scenario application, and
second-order effects.

Authoring form is (stem, correct_text, [(wrong_text, error_note) x 3], chapter).
A fixed balanced key pattern places the correct choice; the three wrong choices
fill the remaining letters in order, so an error note can never land on the
answer letter.
"""
import os
from collections import Counter

import yaml

OUT = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/drill/part2-biology.yml"

# 25 slots -> A:6 B:7 C:6 D:6
KEYS = ["A", "B", "C", "D", "D", "A", "B", "C",
        "C", "D", "A", "B", "B", "C", "D", "A",
        "A", "B", "C", "D", "D", "A", "B", "C",
        "B"]

GEN = "genetics"
C1C = "1c-heritable-information-genetic-diversity"
C2A = "2a-assemblies-of-molecules-cells-and-cell-groups"
C2B = "2b-prokaryotes-and-viruses"
C2C = "2c-cell-division-differentiation-specialization"
CELL = "cells-and-cellular-processes"
PLANT = "the-world-of-plants-and-animals"
ECO = "organisms-and-their-environment"
UNITY = "unity-and-diversity-of-life"
HOME = "life-processes-regulation-and-homeostasis"
NEURO = "3a-nervous-and-endocrine-systems"
ORGAN = "3b-main-organ-systems"
DEV = "development"

ITEMS = [
    # ---------------- non-Mendelian / probability ----------------
    ("A woman whose mother died of a mitochondrial myopathy (a mutation in "
     "mitochondrial DNA) marries an unrelated, unaffected man. What is the risk "
     "that her first child inherits the disorder?",
     "100%, because all of her children inherit her mitochondria through the egg",
     [("50%, because the disorder is transmitted like an autosomal dominant allele",
       "treated cytoplasmic inheritance as Mendelian segregation, which mtDNA does not follow"),
      ("25%, because only one in four offspring of carrier parents is affected",
       "borrowed the 1:2:1 autosomal recessive ratio, but only one parent is a carrier here"),
      ("0%, because mitochondria are not inherited by offspring at all",
       "forgot that the egg contributes nearly all of the zygote's cytoplasm and mitochondria")],
     GEN),

    ("If nondisjunction of one homologous pair occurs during meiosis I of a human "
     "primary oocyte (n = 23), what chromosome counts do the four resulting gametes "
     "carry?",
     "two gametes with 24 and two with 22",
     [("two with 24, one with 23, and one with 22",
       "described meiosis II nondisjunction, where only two of the four products are aneuploid"),
      ("all four with 23, because meiosis II corrects the meiosis I error",
       "assumed the second division can repair a segregation failure; it cannot, it only splits what is present"),
      ("all four with 24, because both divisions fail to separate the affected pair",
       "applied the meiosis I error twice; meiosis II of the affected cell is a normal equational split")],
     C1C),

    ("A single base pair is deleted near the start of a bacterial gene's coding "
     "region. The most likely effect on the polypeptide is that",
     "every codon downstream is read in a new frame, so most amino acids after the "
     "deletion change",
     [("only one amino acid is missing and the rest of the protein is unchanged",
       "described an in-frame deletion; losing one base shifts the reading frame instead"),
      ("the deleted base is replaced by its partner on the complementary strand, so nothing changes",
       "confused base-pairing with mutation repair; the sequence itself is not restored"),
      ("translation stops immediately at the deletion, so no amino acids at all are added",
       "confused a frameshift with a nonsense codon; a new stop codon is only encountered further downstream")],
     C1C),

    ("Two pea plants heterozygous for round seeds (Rr) and yellow cotyledons (Yy), "
     "with the two genes on different chromosomes, are crossed. What fraction of the "
     "offspring is expected to be rrYY?",
     "1/16",
     [("1/4",
       "collapsed the two independent events into one; rr and YY must both occur"),
      ("1/8",
       "multiplied 1/4 by 1/2, as if the YY combination had the probability of Yy"),
      ("9/16",
       "took the fraction with both dominant phenotypes instead of both recessive alleles")],
     GEN),

    ("In a population of 10,000 people, 1,600 show a recessive phenotype (aa). "
     "Assuming Hardy-Weinberg equilibrium, what percentage is expected to be "
     "heterozygous (Aa)?",
     "48%",
     [("36%",
       "reported p^2, the homozygous dominant class, instead of 2pq"),
      ("40%",
       "reported q, the recessive allele frequency, as if it were the carrier rate"),
      ("84%",
       "added the recessive class to p^2 (0.36 + 0.48) instead of taking 2pq alone")],
     GEN),

    ("Genes A and B lie on the same chromosome 8 map units apart. A dihybrid "
     "testcross AB/ab x ab/ab yields 1000 offspring. What is the most likely number "
     "of ab/ab offspring?",
     "about 460",
     [("about 250",
       "assumed independent assortment, which would make the four classes equal"),
      ("about 40",
       "used the 8% recombination frequency as a single class, i.e. a recombinant class size"),
      ("about 80",
       "reported the total number of recombinant offspring (Ab plus aB) instead of the ab/ab class")],
     C1C),

    ("A man with type AB blood has children with a woman with type O blood (ii). "
     "Which blood types are possible in their children?",
     "Type A and type B only",
     [("Types A, B, AB, and O in equal proportions",
       "treated the cross as a 1:1:1:1 testcross; the father never passes both alleles at once"),
      ("Type AB only, because the father always passes both of his alleles",
       "forgot that homologous chromosomes separate at meiosis, so each gamete gets one allele"),
      ("Type O only, because the mother passes an i allele to every child",
       "counted only the maternal contribution; the father supplies an I^A or I^B allele")],
     GEN),

    # ---------------- cell division and differentiation ----------------
    ("A toxin blocks the actin-myosin contractile ring, so a human skin cell "
     "completes mitosis but never divides its cytoplasm. The result is",
     "one cell containing two nuclei, each with the diploid chromosome number",
     [("two daughter cells, each with half the usual chromosome number",
       "described normal cytokinesis, which the toxin prevented"),
      ("a single cell arrested in metaphase with its chromosomes aligned",
       "confused the cytokinesis block with a spindle-assembly checkpoint arrest"),
      ("one cell with a single nucleus holding 92 chromosomes",
       "forgot that the two nuclear envelopes re-formed separately around each chromosome set")],
     C2C),

    ("A neuron and a liver cell from the same person carry identical DNA yet make "
     "different proteins chiefly because",
     "different sets of genes are transcribed in the two cell types",
     [("the neuron has extra copies of the genes it needs most",
       "assumed gene amplification, which is not how ordinary differentiation works"),
      ("genes that are not needed are deleted from differentiated cells",
       "confused differential expression with DNA loss; the genome is retained"),
      ("each cell acquired different mutations during development",
       "relied on random mutation, but differentiation is a regulated change in expression")],
     C2C),

    ("A cell is treated with a drug that prevents tubulin polymerization, so "
     "spindle fibers cannot form. At which stage does the cell arrest?",
     "metaphase, because the chromosomes cannot attach to spindle fibers and separate",
     [("prophase I, because crossing-over cannot occur without spindle fibers",
       "tied recombination to the spindle; crossing-over is a homologous-pair event that needs no tubulin"),
      ("S phase, because DNA polymerase also requires tubulin",
       "linked replication to the cytoskeleton; DNA synthesis proceeds without microtubules"),
      ("telophase, because the nuclear envelope cannot re-form without tubulin",
       "picked a late stage; the cell never reaches the metaphase-to-anaphase transition")],
     C2C),

    # ---------------- prokaryotes, viruses, endosymbiosis ----------------
    ("A temperate bacteriophage infects E. coli and enters the lysogenic cycle. "
     "Which best describes the infected cell?",
     "Phage DNA is integrated into the bacterial chromosome and is copied whenever "
     "the cell divides",
     [("The cell lyses at once and releases hundreds of new virions",
       "described the lytic cycle, which a lysogenic phage postpones"),
      ("The phage replicates in the cytoplasm without killing the host cell",
       "put the phage genome in the cytoplasm; the prophage is inserted in the host chromosome"),
      ("The phage stays attached to the outside of the cell without injecting its DNA",
       "confused lysogeny with adsorption; the DNA has already entered and integrated")],
     C2B),

    ("Which observation supports the claim that mitochondria descend from "
     "free-living bacteria?",
     "Mitochondria have their own circular DNA, a double membrane, and divide by "
     "splitting in two",
     [("Mitochondrial genes use exactly the same codon table as the nuclear genome",
       "overstated the similarity; mitochondrial codon usage differs from the nuclear code in several cases"),
      ("Every mitochondrial protein is encoded by a nuclear gene",
       "denies the key evidence; mitochondria still encode some of their own proteins and rRNAs"),
      ("Mitochondria are surrounded by a single membrane, like a lysosome",
       "misstates the structure; the double membrane is part of the endosymbiotic evidence")],
     C2A),

    # ---------------- cells: enzymes and water relations ----------------
    ("An enzyme with a temperature optimum of 37 C is warmed to 45 C. What happens "
     "to the reaction rate, and why?",
     "It falls sharply, because the extra heat disrupts the hydrogen bonds that hold "
     "the active site's shape",
     [("It keeps rising, because higher temperature always increases enzyme activity",
       "extended the pre-optimum trend past the point where the protein begins to denature"),
      ("It is unchanged, because enzyme shape does not affect the active site",
       "denies the lock-and-key dependence of catalysis on the protein's three-dimensional shape"),
      ("It falls, but recovers completely when the enzyme is cooled back to 37 C",
       "treated denaturation as reversible like a simple rate change; the tertiary structure is destroyed")],
     CELL),

    ("An Elodea leaf is placed in 10% NaCl and, under the microscope, the cell "
     "membrane is seen pulling away from the cell wall. This happened because",
     "water left the vacuole by osmosis, so the protoplast shrank while the wall kept "
     "its shape",
     [("salt was pumped into the cell, pressing the membrane inward",
       "assumed active salt uptake; the movement seen is water leaving, not solute entering"),
      ("the cell wall dissolved in the salt solution and could no longer support the membrane",
       "blamed the wall; cellulose walls are not dissolved by salt, they simply separate from the protoplast"),
      ("water entered the cell by osmosis and pushed the membrane off the wall",
       "reversed the direction of osmosis; the outside solution is hypertonic, so water leaves")],
     CELL),

    # ---------------- plants ----------------
    ("On a sunny morning guard cells actively pump K+ into themselves. What follows?",
     "Water enters by osmosis, the guard cells become turgid and bow apart, and the "
     "stoma opens",
     [("Water leaves the guard cells, they go limp and the stoma closes",
       "reversed the osmotic consequence of raising the guard cells' solute concentration"),
      ("K+ enters with no water movement, because ions cross membranes freely",
       "ignored the osmotic pull that an accumulated ion creates across the membrane"),
      ("The stoma opens because the guard cell walls dissolve under turgor pressure",
       "blamed wall breakdown; the cellulose wall bows because of its uneven thickening")],
     PLANT),

    ("A gardener pinches off the shoot tip of a basil plant. The most likely result "
     "is that",
     "the lateral buds grow out and the plant becomes bushier, because tip-produced "
     "auxin no longer suppresses them",
     [("the plant stops producing leaves, since the tip was the only growing region",
       "forgot that lateral meristems and buds can resume growth once apical dominance is lifted"),
      ("the stem elongates faster, because auxin is now made along the whole stem",
       "reversed the effect; removing the tip lowers auxin and so slows stem elongation"),
      ("all lateral buds die, because they depended on auxin exported by the tip",
       "reversed auxin's role; auxin inhibits lateral buds rather than sustaining them")],
     PLANT),

    # ---------------- ecology and diversity ----------------
    ("In a chain grass -> grasshopper -> frog -> snake, the snakes are removed. "
     "What long-term change is expected?",
     "Frogs increase, grasshoppers decrease, and grass biomass increases",
     [("Frogs decrease and grass biomass falls",
       "traced the effects up only one level; losing the top predator releases the level below it"),
      ("All levels stay the same, because each level is regulated independently",
       "denied the linkage between trophic levels that a food chain describes"),
      ("Grasshoppers increase, because the frogs no longer compete with them",
       "treated predator and prey as competitors instead of a consumer-resource pair")],
     ECO),

    ("A farmer rotates legumes with cereal crops mainly because",
     "bacteria in the legumes' root nodules fix N2 into ammonium that enriches the soil",
     [("legume roots convert soil nitrates back into N2 gas, which cereals then absorb",
       "confused nitrogen fixation with denitrification, which removes usable nitrogen"),
      ("the rotation suppresses cereal root diseases, which is the nitrogen benefit sought",
       "cited a real side benefit as if it were the nitrogen economy the rotation provides"),
      ("legumes need no nitrogen, so the soil's reserves are left untouched for the cereal",
       "overstated it; legumes use the fixed nitrogen themselves and only the surplus reaches the soil")],
     UNITY),

    ("A microbe from saturated brine at pH 2 has a circular chromosome, no "
     "membrane-bound organelles, and ether-linked branched membrane lipids. It "
     "belongs to",
     "Domain Archaea",
     [("Domain Bacteria, because it lacks a nucleus",
       "used a trait shared by all prokaryotes; the ether-linked lipids point to archaea"),
      ("Kingdom Fungi, because it tolerates extreme conditions",
       "matched an ecological trait to a kingdom; fungi are eukaryotes with membrane-bound organelles"),
      ("Kingdom Protista, because it is unicellular",
       "equated single-celled organization with protists, ignoring the molecular evidence")],
     UNITY),

    # ---------------- homeostasis and control ----------------
    ("A panicking student breathes rapidly and deeply for several minutes. What "
     "happens to the blood, and what does the body do about it?",
     "CO2 falls, pH rises toward alkalosis, and the respiratory center temporarily "
     "reduces the drive to breathe",
     [("CO2 rises, pH falls, and breathing speeds up further to correct it",
       "described hypoventilation; fast deep breathing blows CO2 off rather than retaining it"),
      ("O2 rises so much that the blood becomes acidotic",
       "pinned the pH change on O2; the pH signal is set by dissolved CO2, not by oxygen"),
      ("Blood pH is unaffected, because ventilation cannot change pH",
       "denied the CO2-bicarbonate link that makes ventilation a powerful pH control")],
     HOME),

    ("A person exposed to the measles virus ten years after vaccination responds "
     "with",
     "memory B cells activating quickly to produce a faster, larger IgG response "
     "than at first exposure",
     [("naive B cells starting the whole selection process over at the original speed",
       "described the primary response; the memory population bypasses that slow first step"),
      ("antibodies secreted only by the plasma cells that survived from the vaccination",
       "overstated plasma cell lifespan; long-lived memory cells divide again to make new plasma cells"),
      ("a slower response, because memory cells must first turn into stem cells",
       "invented a de-differentiation step; memory lymphocytes are already committed")],
     HOME),

    # ---------------- nervous and organ systems ----------------
    ("A farm worker exposed to an organophosphate insecticide, an "
     "acetylcholinesterase inhibitor, develops fasciculations and salivation. The "
     "mechanism is that",
     "acetylcholine is no longer broken down in the synaptic cleft, so it keeps "
     "stimulating the muscle",
     [("acetylcholine is reabsorbed too quickly, so fewer receptors are stimulated",
       "reversed the effect; the enzyme's loss leaves ACh in the cleft longer, not shorter"),
      ("Ca2+ is pumped back into the sarcoplasmic reticulum too slowly, leaving the muscle contracted",
       "shifted the lesion into the muscle fiber; the insecticide acts at the synaptic cleft"),
      ("the motor neuron fires spontaneously because its Na+ channels stay open",
       "blamed the presynaptic membrane when the transmitter itself is the problem")],
     NEURO),

    ("In multiple sclerosis, myelin sheaths within the central nervous system are "
     "destroyed. The most direct effect on signaling is that",
     "action potentials travel more slowly and may fail to reach the terminal, since "
     "saltatory conduction is lost",
     [("the resting membrane potential is abolished, because myelin generates it",
       "credited myelin with the resting potential, which the Na+/K+ pump and leak channels maintain"),
      ("synaptic vesicles can no longer fuse with the presynaptic membrane",
       "moved the defect to transmitter release, which is unaffected by demyelination"),
      ("the axon stops making ATP and degenerates immediately",
       "confused electrical insulation with metabolic support of the fiber")],
     NEURO),

    ("A pregnant woman takes a drug known to be a teratogen. When is the embryo "
     "most vulnerable to major structural malformations?",
     "weeks 3 to 8, when the organs are being laid down",
     [("the first two weeks, before implantation is complete",
       "picked the all-or-none period, when damage usually kills the embryo or is fully repaired"),
      ("the fetal period after week 20, when organs only enlarge",
       "chose a stage of growth and maturation, when gross structure is already set"),
      ("at birth, when the organs first begin to function",
       "assumed structural defects appear at the time an organ starts working")],
     DEV),

    ("After a 400-m sprint an athlete keeps breathing hard for several minutes. The "
     "extra oxygen is used chiefly to",
     "convert the accumulated lactate back to glucose in the liver and restore ATP "
     "and creatine phosphate",
     [("flush out CO2 that built up inside the muscle fibers as carbonate",
       "attributed the debt to CO2; CO2 is exhaled, not stored as an oxygen-requiring debt"),
      ("re-oxygenate myoglobin alone, since that is the only store that was depleted",
       "took one small store for the whole recovery; ATP, phosphocreatine and lactate also must be restored"),
      ("digest the glycogen that piled up in the muscles during the sprint",
       "reversed the fuel flow; glycogen is broken down during the sprint and resynthesized afterwards")],
     ORGAN),
]


def main() -> None:
    assert len(ITEMS) == 25 and len(KEYS) == 25
    items = []
    for n, (q, correct, wrongs, chapter) in enumerate(ITEMS, 1):
        assert len(wrongs) == 3 and all(len(w) == 2 for w in wrongs)
        key = KEYS[n - 1]
        others = [letter for letter in "ABCD" if letter != key]
        choices = {key: correct}
        distractors = {}
        for letter, (text, note) in zip(others, wrongs):
            choices[letter] = text
            distractors[letter] = note
        assert set(choices) == {"A", "B", "C", "D"}
        items.append({
            "id": f"nmat-d-p2b-{n:03d}",
            "q": " ".join(q.split()),
            "choices": choices,
            "answer": key,
            "explain": "",
            "distractors": distractors,
            "chapter": chapter,
        })

    # explanations are authored separately so they can mirror the correct choice
    EXPLAIN = EXPLANATIONS
    assert len(EXPLAIN) == 25
    for item, text in zip(items, EXPLAIN):
        item["explain"] = text

    doc = {
        "exam": "nmat",
        "section": "drill-part2-biology",
        "label": "Biology drill",
        "subject": "biology",
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


EXPLANATIONS = [
    "Mitochondria and their mutated DNA travel in the egg's cytoplasm, so every child of an "
    "affected mother inherits the disorder, while an affected father passes on none.",
    "Nondisjunction in meiosis I sends both homologues to one pole, so two gametes get an extra "
    "chromosome (n+1 = 24) and two get none (n-1 = 22); meiosis II then divides normally.",
    "Losing a single base shifts every downstream codon into a new frame, changing most amino "
    "acids from that point on and usually introducing a premature stop codon.",
    "Independent assortment gives rr = 1/4 and YY = 1/4, and the two probabilities multiply to "
    "1/16 (one genotype out of the 16 equally likely combinations).",
    "q^2 = 1600/10000 = 0.16, so q = 0.4 and p = 0.6; the carrier frequency 2pq = 2(0.6)(0.4) = 0.48, "
    "or 48%.",
    "The parental classes share 100% - 8% = 92% of the offspring, about 460 each, while the two "
    "recombinant classes split the 8%, about 40 each.",
    "The father passes I^A or I^B and the mother always passes i, so every child is I^A i (type A) "
    "or I^B i (type B); neither AB nor O is possible.",
    "Blocking the contractile ring prevents cytokinesis only, so mitosis finishes and two diploid "
    "nuclei share one cytoplasm: a binucleate cell.",
    "Every nucleated cell keeps the full genome; cell identity comes from transcription factors "
    "and epigenetic marks that switch different gene sets on.",
    "Microtubules make up the spindle, so a tubulin poison leaves the kinetochores unattached and "
    "the spindle-assembly checkpoint holds the cell at metaphase.",
    "In lysogeny the phage genome integrates as a prophage and is replicated along with the host "
    "chromosome each time the bacterium divides.",
    "Circular DNA, a double membrane, ribosomes, and binary fission are bacterial hallmarks that "
    "mitochondria retain from their free-living ancestor.",
    "Above the optimum, thermal agitation breaks the hydrogen and ionic bonds of the tertiary "
    "structure, the active site deforms, and the rate collapses irreversibly.",
    "A hypertonic external solution draws water out of the vacuole, so the protoplast contracts "
    "and pulls away from the rigid cellulose wall (plasmolysis).",
    "Accumulated K+ raises guard-cell solute concentration, water follows by osmosis, turgor "
    "pressure builds against the thinner outer wall, and the pore opens.",
    "Apical dominance depends on auxin flowing down from the shoot tip; removing the tip removes "
    "that inhibition, so lateral buds sprout.",
    "Removing the top predator frees the frogs, more frogs eat more grasshoppers, and the "
    "released grass increases: a trophic cascade.",
    "Rhizobium in legume nodules reduces atmospheric N2 to ammonium; residues left behind add "
    "nitrogen that the following cereal crop can use.",
    "Ether-linked branched membrane lipids plus a circular chromosome and no organelles identify "
    "an archaeon, the domain of halophiles and acidophiles.",
    "Hyperventilation lowers arterial CO2, so carbonic acid falls and pH rises; the medullary "
    "center responds by reducing the ventilatory drive until CO2 recovers.",
    "The secondary response draws on pre-existing memory cells, so IgG rises within days to a much "
    "higher level than the primary response and blocks infection.",
    "Acetylcholinesterase normally clears ACh from the cleft; inhibiting it lets ACh accumulate "
    "and fire the motor end plate repeatedly (SLUDGE plus fasciculations).",
    "Myelin lets the impulse jump between nodes of Ranvier; losing it forces slow continuous "
    "propagation and conduction often fails altogether.",
    "Organogenesis (weeks 3-8) is when organ primordia form, so a teratogen then produces major "
    "structural malformations.",
    "Repaying the oxygen debt oxidizes lactate (mostly via gluconeogenesis in the liver) and "
    "replenishes ATP and phosphocreatine stores.",
]


if __name__ == "__main__":
    main()
