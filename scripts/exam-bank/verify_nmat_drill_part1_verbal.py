#!/usr/bin/env python3
"""Verify content/exam-bank/nmat/drill/part1-verbal.yml against the drill schema."""
import glob
import re
import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/drill/part1-verbal.yml"
ALLOWED = {"analogies", "reading-comprehension"}

d = yaml.safe_load(open(PATH))

# ---- required top-level keys: a drill bank carries no blueprint, no passages
assert set(d) == {"exam", "section", "label", "subject", "block", "_drill", "items"}, sorted(d)
assert d["exam"] == "nmat" and d["section"] == "drill-part1-verbal"
assert d["label"] == "Verbal drill" and d["subject"] == "verbal" and d["block"] == "part1"
assert d["_drill"] is True
assert len(d["items"]) == 25
assert d["section"].startswith("drill-")

ans = Counter(i["answer"] for i in d["items"])
assert max(ans.values()) <= 7, ans
assert sum(ans.values()) == 25

ids, stems = [], []
chapters = Counter()
for i in d["items"]:
    assert set(i) == {"id", "q", "choices", "answer", "explain", "distractors", "chapter"}, sorted(i)
    assert re.fullmatch(r"nmat-d-p1v-\d{3}", i["id"]), i["id"]
    ids.append(i["id"])
    assert set(i["choices"]) == {"A", "B", "C", "D"}
    assert i["answer"] in i["choices"]
    assert i["answer"] not in i["distractors"], i["id"]
    assert set(i["distractors"]) <= {"A", "B", "C", "D"}, i["id"]
    assert set(i["distractors"]) == set(i["choices"]) - {i["answer"]}, i["id"]
    assert i["chapter"] in ALLOWED, i["chapter"]
    chapters[i["chapter"]] += 1
    assert i["q"] and i["explain"]
    stems.append(i["q"].strip())
    assert all(isinstance(v, str) and v.strip() for v in i["choices"].values()), i["id"]
    assert all(isinstance(v, str) and len(v.split()) >= 2 for v in i["distractors"].values()), i["id"]
    assert len(set(i["choices"].values())) == 4, i["id"]
    if i["chapter"] == "analogies":
        assert "::" in i["q"] and i["q"].strip().endswith("?"), i["q"]
    else:
        # a short self-contained passage must sit in the stem
        assert len(i["q"].split()) >= 40, (i["id"], len(i["q"].split()))

assert chapters == Counter({"analogies": 13, "reading-comprehension": 12}), chapters
assert len(set(ids)) == 25 and len(set(stems)) == 25
assert ids == ["nmat-d-p1v-%03d" % n for n in range(1, 26)], ids[:5]

# ---- global isolation: unique ids, no stem shared with any other bank file
all_ids, all_stems = set(), {}
for f in glob.glob("/home/ubuntu/django-wsgi/content/exam-bank/**/*.yml", recursive=True):
    for it in (yaml.safe_load(open(f)) or {}).get("items") or []:
        assert it["id"] not in all_ids, ("duplicate id across bank", it["id"], f)
        all_ids.add(it["id"])
        all_stems.setdefault(it["q"].strip(), []).append((it["id"], f))
for it in d["items"]:
    owners = all_stems.get(it["q"].strip()) or []
    assert len(owners) == 1, ("stem shared with another bank", it["id"], owners)

# ---- not a mock bank: the section id must appear in no blueprint
for f in glob.glob("/home/ubuntu/django-wsgi/content/exams/*.yml"):
    bp = ((yaml.safe_load(open(f)) or {}).get("blueprint") or {}).get("blocks") or []
    for b in bp:
        assert d["section"] not in (b.get("bank") or []), (f, b.get("id"))

print("ALL CHECKS PASSED (part1-verbal drill)")
print("answers:", dict(sorted(ans.items())))
print("chapters:", dict(chapters))
