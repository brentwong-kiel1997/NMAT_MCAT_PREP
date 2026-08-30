#!/usr/bin/env python3
"""Verify content/exam-bank/mcat/drill/bio-biochem.yml (practice-only drill bank)."""
import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/mcat/drill/bio-biochem.yml"
ALLOWED = {"cells-and-cellular-processes", "development", "genetics",
           "life-processes-regulation-and-homeostasis", "organisms-and-their-environment",
           "the-world-of-plants-and-animals", "unity-and-diversity-of-life",
           "1c-heritable-information-genetic-diversity",
           "2a-assemblies-of-molecules-cells-and-cell-groups", "2b-prokaryotes-and-viruses",
           "2c-cell-division-differentiation-specialization", "3a-nervous-and-endocrine-systems",
           "3b-main-organ-systems", "1a-proteins-and-amino-acids", "1b-gene-to-protein",
           "1c-heritable-information-diversity", "1d-bioenergetics-and-fuel-metabolism",
           "chemistry-of-biochemistry-cem", "biochemistry"}

d = yaml.safe_load(open(PATH))
assert d["exam"] == "mcat" and d["section"] == "drill-bio-biochem"
assert d["subject"] == "bio-biochem" and d["block"] == "bio-biochem" and d.get("_drill") is True
all_items = list(d["items"]) + [i for p in d.get("passages") or [] for i in p["items"]]
assert len(all_items) == d["items_expected"] == 30, (len(all_items), d["items_expected"])
assert not d.get("passages")

ids = [i["id"] for i in all_items]
assert len(set(ids)) == len(ids)
assert ids == ["mcat-d-bb-%03d" % n for n in range(1, 31)], "id sequence"
assert max(Counter(i["answer"] for i in all_items).values()) <= 8

for i in all_items:
    assert set(i["choices"]) == {"A", "B", "C", "D"} and i["answer"] in i["choices"]
    assert i["answer"] not in i["distractors"], (i["id"], "answer letter carries a note")
    assert set(i["distractors"]) == set("ABCD") - {i["answer"]}, (i["id"], "distractor keys")
    assert i["chapter"] in ALLOWED, (i["id"], i["chapter"])
    assert i["passage_id"] == ""
    assert i["q"].strip() and i["explain"].strip()
    for L, note in i["distractors"].items():
        assert note.strip(), (i["id"], L)
        assert i["choices"][L] != i["choices"][i["answer"]], (i["id"], L, "duplicate option text")

# coverage checks: genetics probability and enzyme kinetics must be represented
chapters = Counter(i["chapter"] for i in all_items)
assert chapters["genetics"] >= 5, chapters
assert chapters["biochemistry"] >= 2, chapters
kinetics = [i for i in all_items if "Vmax" in i["q"] or "Km" in i["q"]]
assert len(kinetics) >= 3, [i["id"] for i in kinetics]

print("OK", PATH)
print(" answers:", dict(sorted(Counter(i["answer"] for i in all_items).items())))
print(" chapters:", dict(sorted(chapters.items())))
