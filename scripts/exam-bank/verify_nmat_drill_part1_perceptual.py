#!/usr/bin/env python3
"""Verify content/exam-bank/nmat/drill/part1-perceptual.yml against the drill schema.

The identical-information items are re-diffed here character by character,
straight from the YAML: the target is pulled out of the stem, every option is
compared against it, and exactly one option may match.
"""
import glob
import re
from pathlib import Path

import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/drill/part1-perceptual.yml"
ALLOWED = {"mirror-image", "identical-information", "hidden-figure"}
IMAGES = Path("/home/ubuntu/django-wsgi/content/images")

d = yaml.safe_load(open(PATH))
assert set(d) == {"exam", "section", "label", "subject", "block", "_drill", "items"}, sorted(d)
assert d["exam"] == "nmat" and d["section"] == "drill-part1-perceptual"
assert d["label"] == "Perceptual Acuity drill"
assert d["subject"] == "perceptual-acuity" and d["block"] == "part1"
assert d["_drill"] is True
assert len(d["items"]) == 25 and d["section"].startswith("drill-")

ans = Counter(i["answer"] for i in d["items"])
assert max(ans.values()) <= 7, ans
chapters = Counter()
ids = []
for i in d["items"]:
    BASE = {"id", "q", "choices", "answer", "explain", "distractors", "chapter"}
    # figure is optional: mirror-plate items carry a shared demonstration SVG
    assert BASE <= set(i) <= BASE | {"figure"}, sorted(i)
    if i.get("figure"):
        assert i["figure"].startswith("items/"), i["id"]
        assert (IMAGES / i["figure"]).is_file(), f"{i['id']}: missing {i['figure']}"
    assert re.fullmatch(r"nmat-d-p1p-\d{3}", i["id"]), i["id"]
    ids.append(i["id"])
    assert set(i["choices"]) == {"A", "B", "C", "D"} and i["answer"] in i["choices"]
    assert i["answer"] not in i["distractors"] and set(i["distractors"]) <= {"A", "B", "C", "D"}
    assert set(i["distractors"]) == set(i["choices"]) - {i["answer"]}, i["id"]
    assert i["chapter"] in ALLOWED, i["chapter"]
    chapters[i["chapter"]] += 1
    assert i["q"] and i["explain"]
    assert len(set(i["choices"].values())) == 4, i["id"]
assert chapters == Counter({"mirror-image": 9, "identical-information": 8,
                            "hidden-figure": 8}), chapters
assert ids == ["nmat-d-p1p-%03d" % n for n in range(1, 26)], ids[:5]

# ---- identical information: re-diff every option against its target --------
n_target = 0
for i in d["items"]:
    if i["chapter"] != "identical-information":
        continue
    q = i["q"]
    if q.startswith("Target: "):
        head, rest = q.split(" Which option is an exact", 1)
        target = head[len("Target: "):].strip()
        opts = list(i["choices"].values())
        assert len(target) > 4
        n_target += 1
        matches = [o for o in opts if o == target]
        assert len(matches) == 1, (i["id"], matches)
        assert i["choices"][i["answer"]] == target, (i["id"], i["answer"])
        # every other option is a near miss of 1 or 2 characters
        for L, o in i["choices"].items():
            if o == target:
                continue
            assert len(o) == len(target), (i["id"], L)
            diffs = [k for k in range(len(target)) if target[k] != o[k]]
            assert 1 <= len(diffs) <= 2, (i["id"], L, diffs)
            note = i["distractors"][L]
            # the note must name the true position(s)
            for k in diffs:
                assert "position %d" % (k + 1) in note, (i["id"], L, k + 1, note)
            assert ("Off by one character" if len(diffs) == 1
                    else "Off by two characters") in note, (i["id"], L, note)
            # and the true characters
            for k in diffs:
                assert "'%s'" % target[k] in note, (i["id"], L, k, note)
    else:
        # two-string comparison: the stem quotes both strings
        quoted = re.findall(r"'([^']+)'", q)
        assert len(quoted) == 2, (i["id"], quoted)
        a, b = quoted
        assert len(a) == len(b), i["id"]
        diffs = [k for k in range(len(a)) if a[k] != b[k]]
        assert len(diffs) == 1, (i["id"], diffs)
        assert i["choices"][i["answer"]].startswith("not identical, because they differ in one"), i["id"]
        wrong = [o for o in i["choices"].values() if o != i["choices"][i["answer"]]]
        assert any(o.startswith("identical, character for character") for o in wrong), i["id"]
        assert any(o.startswith("not identical, because they differ in two") for o in wrong), i["id"]
assert n_target == 6, n_target

# ---- mirror-image items: sanity on the word answers ------------------------
MIRROR_SAFE_LR = set("AHIMOTUVWXY")     # capitals unchanged by a left-right flip
MIRROR_SAFE_UD = set("BCDEHIKOX")       # capitals unchanged by an up-down flip
word_items = [i for i in d["items"] if i["chapter"] == "mirror-image"
              and i["choices"][i["answer"]].isupper()
              and len(i["choices"][i["answer"]]) > 1
              and i["choices"][i["answer"]].isalpha()]
assert len(word_items) == 2, [i["choices"][i["answer"]] for i in word_items]
for i in word_items:
    key = i["choices"][i["answer"]]
    if "vertical mirror" in i["q"] and "reads exactly the same" in i["q"]:
        # must be a palindrome built only of left-right-safe capitals
        assert key == key[::-1], (i["id"], key)
        assert set(key) <= MIRROR_SAFE_LR, (i["id"], key)
        for L, note in i["distractors"].items():
            other = i["choices"][L]
            assert other != key
            # every distractor must fail one of the two conditions
            assert other != other[::-1] or not set(other) <= MIRROR_SAFE_LR, (i["id"], L)
    elif "up-down flip" in i["q"]:
        # every letter must survive an up-down flip
        assert set(key) <= MIRROR_SAFE_UD, (i["id"], key)
        for L, note in i["distractors"].items():
            other = i["choices"][L]
            assert not set(other) <= MIRROR_SAFE_UD, (i["id"], L, other)
    else:
        raise AssertionError(("unclassified mirror word item", i["id"]))

# ---- hidden-figure: one keyed panel, three panels with a reason ------------
for i in d["items"]:
    if i["chapter"] != "hidden-figure":
        continue
    assert i["q"].startswith("Target:") and i["q"].rstrip().endswith("Which panel contains it?"), i["id"]
    assert len(i["explain"].split()) >= 8, i["id"]

# ---- global isolation ------------------------------------------------------
all_ids, stems = set(), {}
for f in glob.glob("/home/ubuntu/django-wsgi/content/exam-bank/**/*.yml", recursive=True):
    for it in (yaml.safe_load(open(f)) or {}).get("items") or []:
        assert it["id"] not in all_ids, ("duplicate id across bank", it["id"], f)
        all_ids.add(it["id"])
        stems.setdefault(it["q"].strip(), []).append(it["id"])
for i in d["items"]:
    assert len(stems[i["q"].strip()]) == 1, ("stem shared", i["id"])

for f in glob.glob("/home/ubuntu/django-wsgi/content/exams/*.yml"):
    bp = ((yaml.safe_load(open(f)) or {}).get("blueprint") or {}).get("blocks") or []
    for b in bp:
        assert d["section"] not in (b.get("bank") or []), (f, b.get("id"))

print("ALL CHECKS PASSED (part1-perceptual drill)")
print("answers:", dict(sorted(ans.items())))
print("chapters:", dict(chapters))
print("identical-information targets re-diffed:", n_target)
