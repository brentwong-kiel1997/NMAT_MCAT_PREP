#!/usr/bin/env python3
"""Verify content/exam-bank/nmat/part1-verbal.yml against the item schema."""
import re
import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/part1-verbal.yml"
d = yaml.safe_load(open(PATH))

# ---- required top-level keys
assert set(d) == {"exam", "section", "label", "subject", "block", "items_expected",
                  "items", "passages"}, sorted(d)
assert d["exam"] == "nmat" and d["section"] == "part1-verbal" and d["label"] == "Verbal"
assert d["subject"] == "verbal" and d["block"] == "part1"
assert d["items_expected"] == 30 and len(d["items"]) == 30
assert d["passages"] == []

ans = Counter(i["answer"] for i in d["items"])
assert max(ans.values()) <= 8, ans
ids, stems = [], []
for i in d["items"]:
    assert set(i) == {"id", "q", "choices", "answer", "explain", "distractors", "chapter"}, sorted(i)
    assert re.fullmatch(r"nmat-p1v-\d{3}", i["id"]), i["id"]
    ids.append(i["id"])
    assert set(i["choices"]) == {"A", "B", "C", "D"}
    assert i["answer"] in i["choices"]
    assert i["answer"] not in i["distractors"], i["id"]
    assert set(i["distractors"]) == set(i["choices"]) - {i["answer"]}, i["id"]
    assert i["chapter"] in ("analogies", "reading-comprehension"), i["chapter"]
    assert i["explain"] and i["q"] and len(i["explain"].split(".")) >= 1
    min_words = 5 if i["chapter"] == "analogies" else 40
    assert len(i["q"].split()) >= min_words, (i["id"], len(i["q"].split()))
    stems.append(i["q"].strip().lower())
    # no empty / placeholder option text
    assert all(isinstance(v, str) and v.strip() for v in i["choices"].values()), i["id"]
    assert all(isinstance(v, str) and len(v.split()) >= 2 for v in i["distractors"].values()), i["id"]
    # option texts unique within an item
    assert len(set(i["choices"].values())) == 4, i["id"]
    # analogy stems must use the A : B :: C : ? form
    if i["chapter"] == "analogies":
        assert "::" in i["q"] and i["q"].strip().endswith("?"), i["q"]

assert len(set(ids)) == 30, "duplicate ids"
assert len(set(stems)) == 30, "duplicate stems"
# ids strictly 001..030 in order
assert ids == ["nmat-p1v-%03d" % n for n in range(1, 31)], ids[:5]

print("ALL CHECKS PASSED")
print("answers:", dict(sorted(ans.items())))
print("chapters:", dict(Counter(i["chapter"] for i in d["items"])))
