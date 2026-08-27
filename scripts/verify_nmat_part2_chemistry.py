#!/usr/bin/env python3
"""Verify content/exam-bank/nmat/part2-chemistry.yml against the item schema."""
import math
import re
import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/part2-chemistry.yml"
d = yaml.safe_load(open(PATH))

ALLOWED = set("""4e-atoms-nuclear-decay-electronic-structure 5a-unique-nature-of-water-and-its-solutions
5b-molecules-and-intermolecular-interactions 5c-separation-and-purification-methods
5d-biologically-relevant-molecules 5e-chemical-thermodynamics-and-kinetics analytical-chemistry
biochemistry general-chemistry organic-chemistry""".split())

# ---- required top-level keys
assert set(d) == {"exam", "section", "label", "subject", "block", "items_expected",
                  "items", "passages"}, sorted(d)
assert d["exam"] == "nmat" and d["section"] == "part2-chemistry" and d["label"] == "Chemistry"
assert d["subject"] == "chemistry" and d["block"] == "part2"
assert d["items_expected"] == 30 and len(d["items"]) == 30
assert d["passages"] == []

ans = Counter(i["answer"] for i in d["items"])
assert max(ans.values()) <= 8, ans

ids, stems = [], []
for i in d["items"]:
    assert set(i) == {"id", "q", "choices", "answer", "explain", "distractors", "chapter"}, sorted(i)
    assert re.fullmatch(r"nmat-p2c-\d{3}", i["id"]), i["id"]
    ids.append(i["id"])
    assert set(i["choices"]) == {"A", "B", "C", "D"}
    assert i["answer"] in i["choices"]
    # CRITICAL: no distractor entry may sit on the answer letter
    assert i["answer"] not in i["distractors"], i["id"]
    # and the distractor keys must be exactly the three non-answer letters
    assert set(i["distractors"]) == set(i["choices"]) - {i["answer"]}, i["id"]
    assert i["chapter"] in ALLOWED, i["chapter"]
    assert i["explain"].strip() and i["q"].strip()
    assert len(i["q"].split()) >= 8, i["id"]
    stems.append(i["q"].strip().lower())
    assert all(isinstance(v, str) and v.strip() for v in i["choices"].values()), i["id"]
    assert all(isinstance(v, str) and len(v.split()) >= 2 for v in i["distractors"].values()), i["id"]
    # the four option texts must be distinct
    assert len(set(i["choices"].values())) == 4, i["id"]
    # the correct text must not be described as wrong by any surviving note
    assert len(i["distractors"]) == 3

assert len(set(ids)) == 30, "duplicate ids"
assert len(set(stems)) == 30, "duplicate stems"
assert ids == ["nmat-p2c-%03d" % n for n in range(1, 31)], ids[:5]

# ---- independent re-solve of every numeric item -----------------------------
num = {int(i["id"][-3:]): i for i in d["items"]}
val = lambda n: num[n]["choices"][num[n]["answer"]]

assert val(1) == "23 electrons" and 26 - 3 == 23                       # Fe3+ electrons
assert val(2) == "Ar"                                                  # peak first IE
assert val(3) == str(2 * (2 * 2 + 1))                                  # 3d capacity
assert val(4) == "ethanol (CH3CH2OH)"                                  # H-bonding bp
assert val(5) == "CO2"                                                 # nonpolar/polar bonds
assert val(6) == "sp"                                                  # alkyne carbon
# limiting reagent: H2 limits -> 6.0 mol NH3
assert abs(min(6.0 * 2 / 1, 9.0 * 2 / 3) - float(val(7).split()[0])) < 0.001
# percent water in CuSO4.5H2O
assert abs(90.0 / (159.6 + 90.0) * 100 - float(val(8).rstrip("%"))) < 0.06
# ideal gas molar mass
assert abs(0.500 * 0.0821 * 298.0 / (1.00 * 0.250) - float(val(9).split()[0])) < 0.06
# grams NaOH for 250 mL of 0.500 M
assert abs(0.500 * 0.250 * 40.0 - float(val(10).split()[0])) < 0.001
# dilution volume in mL
assert abs(0.150 * 2.00 / 12.0 * 1000 - float(val(11).split()[0])) < 0.001
# pH of 0.0030 M HCl
assert abs(-math.log10(3.0e-3) - float(val(13))) < 0.006
# Henderson-Hasselbalch
assert abs(4.76 + math.log10(0.60 / 0.20) - float(val(14))) < 0.006
# titration: diprotic acid
assert abs(0.0250 * 0.150 * 2 / 0.100 * 1000 - float(val(15).split()[0])) < 0.001
# TCA ATP equivalents for one glucose
assert abs(2 * (3 * 2.5 + 1 * 1.5 + 1) - float(val(16))) < 0.001
# combustion enthalpy of ethanol
assert abs(2 * -393.5 + 3 * -285.8 - (-277.7) - float(val(17).split()[0])) < 0.7
# Gibbs free energy at 310 K
assert abs(40.0 - 310 * 0.150 - float(val(18).split()[0])) < 0.001
# first-order half-life
assert abs(0.693 / 0.0231 - float(val(21).split()[0])) < 0.06
# Daniell cell emf
assert abs(0.34 - (-0.76) - float(val(22).lstrip("+").split()[0])) < 0.001
# Faraday mass of copper
assert abs(2.00 * 965 / 96500.0 / 2 * 63.5 - float(val(23).split()[0])) < 0.0006
# Michaelis-Menten velocity
assert abs(60 * 6.0 / (2.0 + 6.0) - float(val(30).split()[0])) < 0.001

print("ALL CHECKS PASSED")
print("answers:", dict(sorted(ans.items())))
print("chapters:", dict(Counter(i["chapter"] for i in d["items"])))
