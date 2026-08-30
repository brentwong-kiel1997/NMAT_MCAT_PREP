#!/usr/bin/env python3
"""Verify content/exam-bank/mcat/drill/cars.yml (2 original passages, 10 items)."""
import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/mcat/drill/cars.yml"
ALLOWED = {"foundations-of-comprehension", "reasoning-within-the-text",
           "reasoning-beyond-the-text"}  # the CARS subject's own skill chapters

d = yaml.safe_load(open(PATH))
assert d["exam"] == "mcat" and d["section"] == "drill-cars"
assert d["subject"] == "cars" and d["block"] == "cars" and d.get("_drill") is True
assert d["items_expected"] == 10 and d["items"] == []
assert len(d["passages"]) == 2, len(d["passages"])

all_items = [i for p in d["passages"] for i in p["items"]]
assert len(all_items) == 10, len(all_items)
ids = [i["id"] for i in all_items]
assert len(set(ids)) == len(ids)
assert ids == ["mcat-d-ca-%03d" % n for n in range(1, 11)], "id sequence"
assert max(Counter(i["answer"] for i in all_items).values()) <= 3

seen = {"mcat-d-cars-p01", "mcat-d-cars-p02"}
for p in d["passages"]:
    assert p["id"] in seen
    seen.discard(p["id"])
    assert p["text"] and len(p["items"]) >= 4
    wc = len(p["text"].split())
    assert 450 <= wc <= 550, (p["id"], wc, "passage length out of spec")
    nparas = len([x for x in p["text"].splitlines() if x.strip()])
    assert nparas >= 4, (p["id"], nparas, "passage must keep its paragraphs")
    for i in p["items"]:
        assert i.get("passage_id") == p["id"], (i["id"], "passage_id mismatch")
        assert set(i["choices"]) == {"A", "B", "C", "D"} and i["answer"] in i["choices"]
        assert i["answer"] not in i["distractors"], (i["id"], "answer letter carries a note")
        assert set(i["distractors"]) == set("ABCD") - {i["answer"]}, (i["id"], "distractor keys")
        assert i["chapter"] in ALLOWED, (i["id"], i["chapter"])
        assert i["q"].strip() and i["explain"].strip()
        for L, note in i["distractors"].items():
            assert note.strip(), (i["id"], L)
            assert i["choices"][L] != i["choices"][i["answer"]], (i["id"], L, "duplicate option text")
assert not seen, seen

# every passage must have at least one Foundations-of-Comprehension item
for p in d["passages"]:
    assert any(i["chapter"] == "foundations-of-comprehension" for i in p["items"]), p["id"]

print("OK", PATH)
for p in d["passages"]:
    print(" %s: %d words, %d paragraphs, %d items"
          % (p["id"], len(p["text"].split()),
             len([x for x in p["text"].splitlines() if x.strip()]), len(p["items"])))
print(" answers:", dict(sorted(Counter(i["answer"] for i in all_items).items())))
print(" chapters:", dict(sorted(Counter(i["chapter"] for i in all_items).items())))
