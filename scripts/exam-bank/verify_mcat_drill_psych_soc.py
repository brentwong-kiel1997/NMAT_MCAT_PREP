#!/usr/bin/env python3
"""Verify content/exam-bank/mcat/drill/psych-soc.yml (practice-only drill bank)."""
import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/mcat/drill/psych-soc.yml"
ALLOWED = {"psychology", "sociology-and-anthropology", "fc6-perceive-think-react",
           "fc7-behavior-and-behavior-change", "fc8-self-others-interactions",
           "fc9-cultural-and-social-differences", "fc10-stratification-and-resources",
           "6a-sensing-the-environment", "6b-making-sense-of-the-environment",
           "6c-responding-to-the-world", "7a-individual-influences-on-behavior",
           "7b-social-processes-that-influence-behavior", "7c-attitude-and-behavior-change",
           "8a-self-identity", "8b-social-thinking", "8c-social-interactions",
           "9a-understanding-social-structure", "9b-demographic-characteristics-and-processes",
           "10a-social-inequality"}

d = yaml.safe_load(open(PATH))
assert d["exam"] == "mcat" and d["section"] == "drill-psych-soc"
assert d["subject"] == "psych-soc" and d["block"] == "psych-soc" and d.get("_drill") is True
all_items = list(d["items"]) + [i for p in d.get("passages") or [] for i in p["items"]]
assert len(all_items) == d["items_expected"] == 30, (len(all_items), d["items_expected"])
assert not d.get("passages")

ids = [i["id"] for i in all_items]
assert len(set(ids)) == len(ids)
assert ids == ["mcat-d-ps-%03d" % n for n in range(1, 31)], "id sequence"
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

# research-methods weighting: most stems must describe a study or a researcher
chapters = Counter(i["chapter"] for i in all_items)
assert chapters["psychology"] >= 10, chapters
methods = [i for i in all_items
           if any(w in i["q"] for w in ("stud", "research", "experiment", "sample",
                                        "participants", "measur", "journal"))]
assert len(methods) >= 12, len(methods)

print("OK", PATH)
print(" answers:", dict(sorted(Counter(i["answer"] for i in all_items).items())))
print(" chapters:", dict(sorted(chapters.items())))
