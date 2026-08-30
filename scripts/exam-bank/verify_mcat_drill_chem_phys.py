#!/usr/bin/env python3
"""Verify content/exam-bank/mcat/drill/chem-phys.yml (practice-only drill bank)."""
import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/mcat/drill/chem-phys.yml"
ALLOWED = {"4a-motion-forces-work-energy-equilibrium", "4b-fluids-for-circulation-and-gas-exchange",
           "4c-electrochemistry-and-electrical-circuits", "4d-light-and-sound-interacting-with-matter",
           "electricity-and-magnetism", "mechanics", "modern-physics", "thermodynamics",
           "vibrations-waves-and-optics", "5a-unique-nature-of-water-and-its-solutions",
           "5b-molecules-and-intermolecular-interactions", "5c-separation-and-purification-methods",
           "5d-biologically-relevant-molecules", "5e-chemical-thermodynamics-and-kinetics",
           "analytical-chemistry", "biochemistry", "general-chemistry", "organic-chemistry"}

d = yaml.safe_load(open(PATH))
assert d["exam"] == "mcat" and d["section"] == "drill-chem-phys"
assert d["label"] == "Chem/Phys drill" and d["subject"] == "chem-phys" and d["block"] == "chem-phys"
assert d.get("_drill") is True
all_items = list(d["items"]) + [i for p in d.get("passages") or [] for i in p["items"]]
assert len(all_items) == d["items_expected"], (len(all_items), d["items_expected"])
assert d["items_expected"] == 30
assert not d.get("passages"), "standalone bank must have no passages"

ids = [i["id"] for i in all_items]
assert len(set(ids)) == len(ids)
assert ids == ["mcat-d-cp-%03d" % n for n in range(1, 31)], "id sequence"
assert max(Counter(i["answer"] for i in all_items).values()) <= 8

for i in all_items:
    assert set(i["choices"]) == {"A", "B", "C", "D"} and i["answer"] in i["choices"]
    assert i["answer"] not in i["distractors"], (i["id"], "answer letter carries a note")
    assert set(i["distractors"]) == set("ABCD") - {i["answer"]}, (i["id"], "distractor keys")
    assert i["chapter"] in ALLOWED, (i["id"], i["chapter"])
    assert i["passage_id"] == "", (i["id"], "standalone item must have empty passage_id")
    assert i["q"].strip() and i["explain"].strip()
    for L, note in i["distractors"].items():
        assert note.strip(), (i["id"], L)
        assert i["choices"][L] != i["choices"][i["answer"]], (i["id"], L, "duplicate option text")

# quantitative answers must appear inside their explanation
import re
mismatch = []
for i in all_items:
    key_text = i["choices"][i["answer"]]
    tail = re.sub(r"[^0-9./x^]", " ", key_text).split()
    if tail and not any(tok in i["explain"] for tok in tail if any(c.isdigit() for c in tok)):
        mismatch.append((i["id"], key_text, i["explain"]))
assert not mismatch, mismatch

print("OK", PATH)
print(" answers:", dict(sorted(Counter(i["answer"] for i in all_items).items())))
print(" chapters:", dict(Counter(i["chapter"] for i in all_items)))
