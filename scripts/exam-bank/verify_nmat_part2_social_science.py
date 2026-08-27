#!/usr/bin/env python3
"""Verify content/exam-bank/nmat/part2-social-science.yml against the item schema."""
import re
import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/part2-social-science.yml"
d = yaml.safe_load(open(PATH))

# ---- required top-level keys
assert set(d) == {"exam", "section", "label", "subject", "block", "items_expected",
                  "items", "passages"}, sorted(d)
assert d["exam"] == "nmat" and d["section"] == "part2-social-science" and d["label"] == "Social Science"
assert d["subject"] == "behavioral-social" and d["block"] == "part2"
assert d["items_expected"] == 30 and len(d["items"]) == 30
assert d["passages"] == []

ALLOWED_CHAPTERS = ("psychology", "sociology-and-anthropology", "fc6-perceive-think-react",
                    "fc7-behavior-and-behavior-change", "fc8-self-others-interactions",
                    "fc9-cultural-and-social-differences", "fc10-stratification-and-resources")

ans = Counter(i["answer"] for i in d["items"])
assert max(ans.values()) <= 8, ans
ids, stems = [], []
for i in d["items"]:
    assert set(i) == {"id", "q", "choices", "answer", "explain", "distractors", "chapter"}, sorted(i)
    assert re.fullmatch(r"nmat-p2s-\d{3}", i["id"]), i["id"]
    ids.append(i["id"])
    assert set(i["choices"]) == {"A", "B", "C", "D"}
    assert i["answer"] in i["choices"]
    assert i["answer"] not in i["distractors"], i["id"]
    # distractor keys are exactly the three NON-answer letters
    assert set(i["distractors"]) == set(i["choices"]) - {i["answer"]}, i["id"]
    assert i["chapter"] in ALLOWED_CHAPTERS, i["chapter"]
    assert i["explain"] and i["q"]
    assert len(i["q"].split()) >= 12, (i["id"], len(i["q"].split()))
    stems.append(i["q"].strip().lower())
    assert all(isinstance(v, str) and v.strip() for v in i["choices"].values()), i["id"]
    # every distractor note is a real sentence addressing that option
    assert all(isinstance(v, str) and len(v.split()) >= 5 for v in i["distractors"].values()), i["id"]
    # option texts unique within an item
    assert len(set(i["choices"].values())) == 4, i["id"]

assert len(set(ids)) == 30, "duplicate ids"
assert len(set(stems)) == 30, "duplicate stems"
assert ids == ["nmat-p2s-%03d" % n for n in range(1, 31)], ids[:5]

print("ALL CHECKS PASSED")
print("answers:", dict(sorted(ans.items())))
print("chapters:", dict(Counter(i["chapter"] for i in d["items"])))
