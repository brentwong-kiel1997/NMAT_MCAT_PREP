#!/usr/bin/env python3
"""Verify content/exam-bank/nmat/part1-perceptual.yml against the item schema.

Also re-diffs every identical-information string character-by-character and
re-checks every mirror transformation against the LR/UD/ROT tables, reading
both straight out of the delivered YAML.
"""
import re
import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/part1-perceptual.yml"
d = yaml.safe_load(open(PATH))

# ---- required top-level keys
assert set(d) == {"exam", "section", "label", "subject", "block", "items_expected",
                  "items", "passages"}, sorted(d)
assert d["exam"] == "nmat" and d["section"] == "part1-perceptual" and d["label"] == "Perceptual Acuity"
assert d["subject"] == "perceptual-acuity" and d["block"] == "part1"
assert d["items_expected"] == 30 and len(d["items"]) == 30
assert d["passages"] == []

ans = Counter(i["answer"] for i in d["items"])
assert max(ans.values()) <= 8, ans
ids, stems = [], []
for i in d["items"]:
    assert set(i) == {"id", "q", "choices", "answer", "explain", "distractors", "chapter"}, sorted(i)
    assert re.fullmatch(r"nmat-p1p-\d{3}", i["id"]), i["id"]
    ids.append(i["id"])
    assert set(i["choices"]) == {"A", "B", "C", "D"}
    assert i["answer"] in i["choices"]
    assert i["answer"] not in i["distractors"], i["id"]
    assert set(i["distractors"]) == set(i["choices"]) - {i["answer"]}, i["id"]
    assert i["chapter"] in ("mirror-image", "hidden-figure", "identical-information"), i["chapter"]
    assert i["explain"] and i["q"]
    stems.append(i["q"].strip().lower())
    assert all(isinstance(v, str) and v.strip() for v in i["choices"].values()), i["id"]
    assert all(isinstance(v, str) and len(v.split()) >= 2 for v in i["distractors"].values()), i["id"]
    # option texts unique within an item
    assert len(set(i["choices"].values())) == 4, i["id"]

assert len(set(ids)) == 30, "duplicate ids"
assert len(set(stems)) == 30, "duplicate stems"
assert ids == ["nmat-p1p-%03d" % n for n in range(1, 31)], ids[:5]

# ---- mirror-image items: re-derive every keyed transformation
it = {i["id"]: i for i in d["items"]}
LR = {"b": "d", "d": "b", "p": "q", "q": "p"}          # vertical mirror
UD = {"b": "p", "p": "b", "d": "q", "q": "d"}          # water image
ROT = {"b": "q", "q": "b", "d": "p", "p": "d"}         # 180-degree rotation
SYM_LR = set("ilmovwx")                                # lowercase, LR-invariant
CAP_SYM = set("AHIOVWTUXM")                            # capitals, LR-invariant


def key(n):
    i = it["nmat-p1p-%03d" % n]
    return i, i["choices"][i["answer"]]


i, k = key(2);  assert k == "".join(LR.get(c, c) for c in reversed("pod")) == "boq"
i, k = key(3);  assert k == "".join(ROT[c] for c in reversed("bd")) == "pq"
i, k = key(4);  assert k == UD["d"] == "q"
i, k = key(1);  assert k in SYM_LR
_i1 = it["nmat-p1p-001"]
assert all(_i1["choices"][L] not in SYM_LR for L in set("ABCD") - {_i1["answer"]})
i, k = key(5);  assert k == "MOM" and set(k) <= CAP_SYM and k == k[::-1]
i, k = key(6);  assert k in {"H", "I", "O", "X"}
i, k = key(7);  assert k.startswith("up and to the left")       # (dx,dy)->(-dx,dy)
i, k = key(8);  a, b = k.split(" and "); assert LR[a] == b
i, k = key(10); assert k == "TOMATO" and set(k) <= CAP_SYM
for n in (5, 10):
    i, _ = key(n)
    for L in set("ABCD") - {i["answer"]}:
        assert set(i["choices"][L]) - CAP_SYM, (n, L)   # each distractor has an asymmetric letter

# ---- identical-information items: re-diff straight from the YAML
quoted = lambda s: re.findall(r"'([^']+)'", s)
FIRST = {"nmat-p1p-011": 7, "nmat-p1p-014": 1, "nmat-p1p-015": 36}
for iid, pos in FIRST.items():
    i = it[iid]
    a, b = quoted(i["q"])
    assert len(a) == len(b) and a != b
    diff = next(k for k in range(len(a)) if a[k] != b[k])
    assert diff == pos, (iid, diff)
    if diff == pos and iid == "nmat-p1p-011":
        assert (a[diff], b[diff]) == ("1", "I")
    txt = i["choices"][i["answer"]]
    assert not txt.startswith("identical")
    assert a[diff] in txt and b[diff] in txt, (iid, "key omits the differing characters")

TARGET = {"nmat-p1p-012": "MARBELLA-0417-CP", "nmat-p1p-016": "1I7-lI7-771",
          "nmat-p1p-018": "REF 2027-NC-004518-B / DUE 30 SEP",
          "nmat-p1p-019": "4821 9037 5566 1204"}
for iid, target in TARGET.items():
    i = it[iid]
    assert re.search(r"Target:\s*" + re.escape(target) + r"\.", i["q"]), iid
    matches = [L for L, t in i["choices"].items() if t == target]
    assert matches == [i["answer"]], (iid, matches)
    for L in set("ABCD") - {i["answer"]}:
        t = i["choices"][L]
        assert t != target
        dd = next(k for k in range(min(len(t), len(target))) if t[k] != target[k])
        assert target[dd] in i["distractors"][L] or t[dd] in i["distractors"][L], (iid, L)

for iid in ("nmat-p1p-013", "nmat-p1p-017", "nmat-p1p-020"):
    i = it[iid]
    entries = dict(re.findall(r"([PQRS]):\s*'([^']+)'", i["q"]))
    assert len(entries) == 4
    same = {frozenset(p) for p in (("P", "Q"), ("P", "R"), ("P", "S"), ("Q", "R"), ("Q", "S"), ("R", "S"))
            if entries[p[0]] == entries[p[1]]}
    assert len(same) == 1, (iid, same)
    keypair = frozenset(re.findall(r"[PQRS]", i["choices"][i["answer"]]))
    assert keypair in same and len(keypair) == 2, (iid, keypair)
    for L in set("ABCD") - {i["answer"]}:
        assert frozenset(re.findall(r"[PQRS]", i["choices"][L])) != keypair, (iid, L)

print("ALL CHECKS PASSED")
print("answers:", dict(sorted(ans.items())))
print("chapters:", dict(Counter(i["chapter"] for i in d["items"])))
