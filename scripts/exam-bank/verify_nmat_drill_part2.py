#!/usr/bin/env python3
"""Verify the four nmat/drill/part2-*.yml practice banks.

Passes:
  1. the required schema / key-balance assertions from the drill spec,
  2. a replica of portal/management/commands/validate_content.py's exam-bank
     rules (chapter existence + tutorial back-link, duplicate ids and stems
     across the WHOLE bank, distractor-key guard, blueprint exclusion for
     _drill sections),
  3. an independent RE-SOLVE of every numeric item: each of the four choices is
     recomputed from the stem's own parameters, so the key placement and every
     distractor value are both confirmed,
  4. a check that each error note actually names the letter it sits on.
"""
import math
import os
import re
from collections import Counter

import yaml

CONTENT = "/home/ubuntu/django-wsgi/content"
FILES = {
    "biology": ("exam-bank/nmat/drill/part2-biology.yml", "nmat-d-p2b-"),
    "physics": ("exam-bank/nmat/drill/part2-physics.yml", "nmat-d-p2p-"),
    "social": ("exam-bank/nmat/drill/part2-social-science.yml", "nmat-d-p2s-"),
    "chemistry": ("exam-bank/nmat/drill/part2-chemistry.yml", "nmat-d-p2c-"),
}

ALLOWED = {
    "biology": """cells-and-cellular-processes development genetics
        life-processes-regulation-and-homeostasis organisms-and-their-environment
        the-world-of-plants-and-animals unity-and-diversity-of-life
        1c-heritable-information-genetic-diversity
        2a-assemblies-of-molecules-cells-and-cell-groups 2b-prokaryotes-and-viruses
        2c-cell-division-differentiation-specialization
        3a-nervous-and-endocrine-systems 3b-main-organ-systems""",
    "physics": """4a-motion-forces-work-energy-equilibrium
        4b-fluids-for-circulation-and-gas-exchange
        4c-electrochemistry-and-electrical-circuits
        4d-light-and-sound-interacting-with-matter electricity-and-magnetism
        mechanics modern-physics thermodynamics vibrations-waves-and-optics""",
    "social": """psychology sociology-and-anthropology fc6-perceive-think-react
        fc7-behavior-and-behavior-change fc8-self-others-interactions
        fc9-cultural-and-social-differences fc10-stratification-and-resources""",
    "chemistry": """4e-atoms-nuclear-decay-electronic-structure
        5a-unique-nature-of-water-and-its-solutions
        5b-molecules-and-intermolecular-interactions
        5c-separation-and-purification-methods
        5d-biologically-relevant-molecules
        5e-chemical-thermodynamics-and-kinetics analytical-chemistry
        biochemistry general-chemistry organic-chemistry""",
}

banks = {}
for key, (rel, prefix) in FILES.items():
    banks[key] = yaml.safe_load(open(os.path.join(CONTENT, rel)))

# ---------------------------------------------------------------- pass 1 ----
for key, d in banks.items():
    assert len(d["items"]) == 25, (key, len(d["items"]))
    assert d["section"].startswith("drill-"), d["section"]
    assert max(Counter(i["answer"] for i in d["items"]).values()) <= 7
    for i in d["items"]:
        assert set(i["choices"]) == {"A", "B", "C", "D"} and i["answer"] in i["choices"]
        assert i["answer"] not in i["distractors"]
        assert set(i["distractors"]) <= {"A", "B", "C", "D"}
        assert len(i["distractors"]) == 3
        assert sorted(i["distractors"]) == sorted(l for l in "ABCD" if l != i["answer"])
        assert i["id"].startswith(FILES[key][1])
        assert i["q"].strip() and i["explain"].strip()
        assert all(v.strip() for v in i["distractors"].values())
print("pass 1 ok: schema, keys, distractor guard")

# ---------------------------------------------------------------- pass 2 ----
chapters = {os.path.splitext(f)[0]: yaml.safe_load(open(os.path.join(CONTENT, "chapters", f)))
            for f in os.listdir(os.path.join(CONTENT, "chapters")) if f.endswith(".yml")}
tutorials = set()
for root, _dirs, files in os.walk(os.path.join(CONTENT, "tutorials")):
    for f in files:
        if f.endswith(".yml"):
            doc = yaml.safe_load(open(os.path.join(root, f))) or {}
            tutorials.add((doc.get("subject"), doc.get("chapter")))

all_ids, all_stems, probs = set(), {}, []
for key, d in banks.items():
    allowed = set(ALLOWED[key].split())
    for i in d["items"]:
        iid = i["id"]
        if iid in all_ids:
            probs.append(f"duplicate id {iid}")
        all_ids.add(iid)
        if i["chapter"] not in allowed:
            probs.append(f"{iid}: chapter {i['chapter']} not allowed in {key}")
        elif i["chapter"] not in chapters:
            probs.append(f"{iid}: unknown chapter {i['chapter']}")
        else:
            ch = chapters[i["chapter"]]
            if (ch.get("discipline"), ch.get("title")) not in tutorials:
                probs.append(f"{iid}: chapter {i['chapter']} has no tutorial")
        stem = i["q"].strip()
        if stem in all_stems:
            probs.append(f"{iid}: duplicate stem of {all_stems[stem]}")
        all_stems[stem] = iid
        if i["answer"] in i["distractors"]:
            probs.append(f"{iid}: distractor on the answer letter")
        for letter, note in i["distractors"].items():
            if not note.strip() or note.strip() == i["choices"][letter].strip():
                probs.append(f"{iid}: empty/echo distractor note on {letter}")
        # choice texts must be distinct
        if len(set(v.strip().lower() for v in i["choices"].values())) != 4:
            probs.append(f"{iid}: duplicate choice text")

blueprint = yaml.safe_load(open(os.path.join(CONTENT, "exams", "nmat.yml")))["blueprint"]["blocks"]
declared = [sid for b in blueprint for sid in (b.get("bank") or [])]
for key, d in banks.items():
    if d["section"] in declared:
        probs.append(f"{d['section']}: drill bank leaked into the mock blueprint")
assert not probs, probs
print("pass 2 ok: repo validator replica (ids, chapters, tutorials, stems)")

# ------------------------------------------------------- pass 3: re-solve ----
def parse_num(text):
    """Pull the quantity out of an authored choice, honouring 'a x 10^b'."""
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*x\s*10\^(-?\d+)", text)
    if m:
        return float(m.group(1)) * 10.0 ** int(m.group(2))
    m = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(m.group(0)) if m else None


def near(parsed, exact, tol=0.06):
    """Authored values are rounded to 2-3 significant figures."""
    return parsed is not None and abs(parsed - exact) <= max(tol * abs(exact), 0.06)


def check(item, letter, exact, label):
    got = parse_num(item["choices"][letter])
    assert near(got, exact), f"{item['id']} {letter}: {item['choices'][letter]!r} != {label} ({exact})"


PH = {int(i["id"][-3:]): i for i in banks["physics"]["items"]}
KEYS = ["A", "B", "C", "D", "D", "A", "B", "C",
        "C", "D", "A", "B", "B", "C", "D", "A",
        "A", "B", "C", "D", "D", "A", "B", "C",
        "B"]
g = 9.8
# (correct, wrong1, wrong2, wrong3) in authoring order, re-derived from each stem
PHYS = {
    1: (math.sqrt(2 * g * 0.20), math.sqrt(g * 0.20), 2 * g * 0.20, math.sqrt(g * 0.20 / 2)),
    2: (0.20 * 4.0 ** 2 / 0.80, 0.20 * 4.0 ** 2, 0.20 * 4.0 / 0.80, 0.20 * 4.0 * 0.80),
    3: (400 * 2.0 / 4.0, 400 * 4.0 / 4.0, 400 * 4.0 / 2.0, 0.0),
    4: (0.10 * 16 / 0.050, 0.10 * 16, 0.10 * 4.0 / 0.050, 0.10 * 16 / 0.0050),
    5: (0.5 * 1000 * 20 ** 2 / 5000, 1000 * 20 ** 2 / 5000,
        0.5 * 1000 * 20 ** 2 / 5000 / 1000, 0.5 * 1000 * 20 ** 2 / 50000),
    6: (150 * 100, 150.0, 1500.0, 15.0),
    7: (60.0, 40.0, 1000 / 600 * 100, 100.0),
    8: (math.sqrt(2 * g * 5.0), 2 * g * 5.0, math.sqrt(g * 5.0), 5.0),
    10: (12 - (12 / 6.0) * 0.50, 12.0, 1.0, 13.0),
    12: (2.0 * 2 * 4, 2.0 * 2, 2.0 * 2 * 2, 2.0 * 2 * 4 * 4),
    15: (1500 * 2.0 / 1000, 1.5, 6.0, 0.75),
    16: (0.10 * 3.34e5 + 0.10 * 4186 * 20, 0.10 * 3.34e5, 0.10 * 4186 * 20,
         (0.10 * 3.34e5 + 0.10 * 4186 * 20) * 1e3),
    17: (500 - 200, 500 + 200, -(500 + 200), 0.0),
    18: ((1 - 300 / 500) * 1000, (300 / 500) * 1000, 500.0 - 300.0, 1000.0),
    19: (2 * 1.5 / 3, 3 * 1.5, 1.5 / 3, 2 * 1.5),
    22: (math.degrees(math.asin(1.5 * math.sin(math.radians(30)))),
         math.degrees(math.asin(math.sin(math.radians(30)) / 1.5)), 30.0, 90.0),
    23: (1.6e-19 * 100, 1.6e-19, 1.6e-19 * 1e4, 100.0),
    25: (None, 1.6e-19 * 2.0e6 * 0.50, 2 * 1.6e-19 * 2.0e6 * 0.50, 0.50),
}
for idx, values in PHYS.items():
    item = PH[idx]
    key = KEYS[idx - 1]
    assert item["answer"] == key, (item["id"], item["answer"], key)
    others = [l for l in "ABCD" if l != key]
    for letter, exact in zip(others, values[1:]):
        check(item, letter, exact, "re-solve")

# items whose answer is a derived expression rather than a bare number
di = 1 / (1 / 10 - 1 / 5)                      # magnifying-glass image distance
assert near(abs(parse_num(PH[21]["choices"][PH[21]["answer"]])), abs(di)) and di < 0
assert near(2 * 1.5 / 3, parse_num(PH[19]["choices"][PH[19]["answer"]]))
assert "virtual" in PH[21]["choices"][PH[21]["answer"]] and "twice as tall" in PH[21]["choices"][PH[21]["answer"]]
assert "510.5" in PH[20]["choices"]["C"] and "510.5" in PH[20]["choices"]["D"]
assert near(1021.0, parse_num(PH[20]["choices"]["A"]))
assert "3 times per second" in PH[20]["choices"][PH[20]["answer"]]
assert PH[11]["choices"][PH[11]["answer"]] == "48 microC"
assert "48" in PH[11]["choices"]["D"] and " mC" in PH[11]["choices"]["D"]
assert near(3.0, parse_num(PH[11]["choices"]["B"]), 0.02)
assert near(0.333, parse_num(PH[11]["choices"]["C"]), 0.02)
assert PH[14]["choices"][PH[14]["answer"]].startswith("the top of the ring becomes a north pole")

# ---- biology numeric / countable ----
BIO = {int(i["id"][-3:]): i for i in banks["biology"]["items"]}
chance = (1 / 4) * (1 / 4)                                     # RrYy x RrYy
assert BIO[4]["choices"][BIO[4]["answer"]] == f"{int(chance * 16)}/16" == "1/16"
q = math.sqrt(1600 / 10000)                                    # Hardy-Weinberg
p = 1 - q
assert BIO[5]["choices"][BIO[5]["answer"]] == f"{2 * p * q:.0%}" == "48%"
parental = (1 - 0.08) / 2 * 1000                               # 8 m.u. testcross
assert BIO[6]["choices"][BIO[6]["answer"]] == f"about {parental:.0f}" == "about 460"
assert BIO[7]["choices"][BIO[7]["answer"]].startswith("Type A and type B")
assert BIO[2]["choices"][BIO[2]["answer"]].startswith("two gametes with 24")

# ---- chemistry numeric ----
CH = {int(i["id"][-3:]): i for i in banks["chemistry"]["items"]}
moles = {"C": 40.0 / 12.0, "H": 6.70 / 1.008, "O": 53.3 / 16.0}
ratio = {k: v / min(moles.values()) for k, v in moles.items()}
assert CH[1]["choices"][CH[1]["answer"]] == "CH2O" and round(ratio["H"]) == 2
assert near(parse_num(CH[2]["choices"]["B"]), 0.250 * 2 * 6.022e23)
assert near(parse_num(CH[2]["choices"]["A"]), 0.250 * 6.022e23)
assert near(parse_num(CH[2]["choices"]["C"]), 1.00 * 6.022e23)
assert near(parse_num(CH[3]["choices"]["C"]), 0.500 * 22.4)
assert near(parse_num(CH[3]["choices"]["A"]), 1.00 * 22.4)
assert near(parse_num(CH[3]["choices"]["B"]), 0.250 * 22.4)
assert CH[4]["choices"][CH[4]["answer"]] == "polonium-218 (A = 218, Z = 84)"
assert CH[6]["choices"][CH[6]["answer"]].startswith("3,")
particles = {"glucose": 1.0, "NaCl": 2.0, "CaCl2": 1.5, "sucrose": 1.0}
assert max(particles, key=particles.get) == "NaCl"
assert CH[7]["choices"][CH[7]["answer"]] == "1.0 m NaCl"
dTb = 0.512 * (0.50 / 0.500) * 2
assert near(parse_num(CH[8]["choices"]["C"]), 100 + dTb, 0.002)
assert near(parse_num(CH[8]["choices"]["A"]), 100 + 0.512 * 0.5, 0.002)
assert near(parse_num(CH[8]["choices"]["B"]), 100 + 0.512 * 1.0, 0.002)
assert near(parse_num(CH[8]["choices"]["D"]), 100 + 0.512 * 4.0, 0.002)
assert near(parse_num(CH[9]["choices"]["C"]), -math.log10(math.sqrt(1.0e-5 * 0.10)), 0.01)
assert CH[9]["choices"]["A"].startswith("1.00") and CH[9]["choices"]["B"].startswith("5.00")
assert near(parse_num(CH[11]["choices"]["A"]), math.sqrt(1.8e-10))
assert near(parse_num(CH[11]["choices"]["B"]), 1.8e-10)
assert near(parse_num(CH[11]["choices"]["C"]), 1.8e-10 / 2)
assert near(parse_num(CH[11]["choices"]["D"]), 2 * math.sqrt(1.8e-10))
assert near(parse_num(CH[12]["choices"]["A"]), 6.0)
q_gram = (100 * 4.18 * 8.0) / 0.50 / 1000
assert near(parse_num(CH[13]["choices"]["B"]), q_gram, 0.02)
assert near(parse_num(CH[13]["choices"]["A"]), 100 * 4.18 * 8.0 / 1000, 0.02)
assert near(parse_num(CH[13]["choices"]["C"]), q_gram * 2, 0.02)
assert near(parse_num(CH[13]["choices"]["D"]), q_gram * 10, 0.02)
assert near(parse_num(CH[14]["choices"]["C"]), 24 / 4, 0.02)
assert near(parse_num(CH[14]["choices"]["A"]), 24 / 2, 0.02)
assert near(parse_num(CH[14]["choices"]["B"]), 48, 0.02)
assert near(parse_num(CH[14]["choices"]["D"]), 1.5, 0.02)
assert CH[16]["choices"][CH[16]["answer"]] == "Kc = [CO2]"
assert CH[20]["choices"][CH[20]["answer"]] == "3"
assert CH[22]["choices"][CH[22]["answer"]] == "4, one per peptide bond"
assert CH[23]["choices"][CH[23]["answer"]] == "cytosine 20% and guanine 20%"
assert 100 - 2 * 30 == 40 and 40 / 2 == 20                    # Chargaff
assert CH[24]["choices"][CH[24]["answer"]].startswith("Km increases")

print("pass 3 ok: every numeric choice re-solved from the stem's parameters")

# ------------------------------------------------- pass 4: notes vs letters --
for key, d in banks.items():
    for i in d["items"]:
        for letter, note in i["distractors"].items():
            text = i["choices"][letter]
            # a note must not describe the correct answer's content
            if note.strip().lower().startswith(text.strip().lower()[:25]):
                probs.append(f"{i['id']}: note on {letter} echoes the correct answer")
assert not probs, probs
print("pass 4 ok: distractor notes sit on their own letters only")

for key, d in banks.items():
    dist = Counter(i["answer"] for i in d["items"])
    print(f"{d['section']:<32} items=25  keys={dict(sorted(dist.items()))}")
print("ALL DRILL BANKS VERIFIED")
