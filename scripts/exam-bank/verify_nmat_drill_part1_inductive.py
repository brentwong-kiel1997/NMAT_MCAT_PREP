#!/usr/bin/env python3
"""Verify content/exam-bank/nmat/drill/part1-inductive.yml against the drill schema.

The series items are re-derived here a second time, independently of the
generator: the numbers are pulled back out of the YAML stem and the rule is
re-applied to them.
"""
import glob
import re
import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/drill/part1-inductive.yml"
ALLOWED = {"number-and-letter-series", "figure-series", "figure-grouping"}

d = yaml.safe_load(open(PATH))
assert set(d) == {"exam", "section", "label", "subject", "block", "_drill", "items"}, sorted(d)
assert d["exam"] == "nmat" and d["section"] == "drill-part1-inductive"
assert d["label"] == "Inductive Reasoning drill"
assert d["subject"] == "inductive-reasoning" and d["block"] == "part1"
assert d["_drill"] is True
assert len(d["items"]) == 25 and d["section"].startswith("drill-")

ans = Counter(i["answer"] for i in d["items"])
assert max(ans.values()) <= 7, ans
chapters = Counter()
ids = []
for i in d["items"]:
    assert set(i) == {"id", "q", "choices", "answer", "explain", "distractors", "chapter"}, sorted(i)
    assert re.fullmatch(r"nmat-d-p1i-\d{3}", i["id"]), i["id"]
    ids.append(i["id"])
    assert set(i["choices"]) == {"A", "B", "C", "D"} and i["answer"] in i["choices"]
    assert i["answer"] not in i["distractors"] and set(i["distractors"]) <= {"A", "B", "C", "D"}
    assert set(i["distractors"]) == set(i["choices"]) - {i["answer"]}, i["id"]
    assert i["chapter"] in ALLOWED, i["chapter"]
    chapters[i["chapter"]] += 1
    assert i["q"] and i["explain"]
    assert len(set(i["choices"].values())) == 4, i["id"]
assert chapters == Counter({"number-and-letter-series": 10,
                            "figure-series": 8, "figure-grouping": 7}), chapters
assert ids == ["nmat-d-p1i-%03d" % n for n in range(1, 26)], ids[:5]

# ---------------- independent re-derivation of every series answer ----------
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def P(ch):
    return ALPHA.index(ch) + 1


def L(n):
    return ALPHA[(n - 1) % 26]


def terms_of(stem):
    tail = stem.split("? ", 1)[1]
    return [t.strip() for t in tail.split(",") if t.strip() and t.strip() != "___"]


seen_rules = 0
# rule for each series item, applied to the terms pulled back out of the YAML
def rule_001(n):                      # alternating x2 then +3
    a = n[0]
    for k in range(len(n)):
        assert a == n[k], (a, n[k])
        a = a * 2 if k % 2 == 0 else a + 3
    return a


def rule_002(n):                      # gaps are the squares 1, 4, 9, 16
    for k in range(len(n) - 1):
        assert n[k + 1] - n[k] == (k + 1) ** 2, (n, k)
    return n[-1] + len(n) ** 2


def rule_003(n):                      # even indices +2, odd indices -10
    for k in range(len(n) - 2):
        assert n[k + 2] - n[k] == (2 if k % 2 == 0 else -10), (n, k)
    return n[-2] - 10                 # next term is the odd-index sub-series


def rule_004(n):                      # drops shrink by one: 8,7,6,5
    for k in range(len(n) - 1):
        assert n[k] - n[k + 1] == 8 - k, (n, k)
    return n[-1] - (8 - (len(n) - 1))


def rule_005(ps):                     # letter steps grow: +4,+5,+6,+7 (wrap)
    for k in range(len(ps) - 1):
        assert (ps[k + 1] - ps[k]) % 26 == 4 + k, (ps, k)
    return L((ps[-1] + 8 - 1) % 26 + 1)


def rule_006(t):                      # letter +2 places, number +3
    return L(P(t[0][0]) + 2 * len(t)) + str(3 * (len(t) + 1))


def rule_007(n):                      # x3 then +1
    for k in range(len(n) - 1):
        assert n[k + 1] == 3 * n[k] + 1, (n, k)
    return 3 * n[-1] + 1


def rule_008(n):                      # twice a prime
    primes = [2, 3, 5, 7, 11, 13]
    for k in range(len(n)):
        assert n[k] == 2 * primes[k], (n, k)
    return 2 * primes[len(n)]


def rule_009(n):                      # gaps grow by two: 2,4,6,8
    for k in range(len(n) - 1):
        assert n[k] - n[k + 1] == 2 * (k + 1), (n, k)
    return n[-1] - 2 * len(n)


def rule_010(ps):                     # letter steps alternate -3, -1
    for k in range(len(ps) - 1):
        assert ps[k] - ps[k + 1] == (3 if k % 2 == 0 else 1), (ps, k)
    return L(ps[-1] - 3)


RULES = {"nmat-d-p1i-001": rule_001, "nmat-d-p1i-002": rule_002,
         "nmat-d-p1i-003": rule_003, "nmat-d-p1i-004": rule_004,
         "nmat-d-p1i-005": rule_005, "nmat-d-p1i-006": rule_006,
         "nmat-d-p1i-007": rule_007, "nmat-d-p1i-008": rule_008,
         "nmat-d-p1i-009": rule_009, "nmat-d-p1i-010": rule_010}

for i in d["items"]:
    if i["chapter"] != "number-and-letter-series":
        continue
    t = terms_of(i["q"])
    key = i["choices"][i["answer"]]          # the answer TEXT, not the letter
    fn = RULES[i["id"]]
    if all(len(x) <= 1 for x in t):
        expect = fn([P(x) for x in t])
    elif all(re.fullmatch(r"[A-Z]\d+", x) for x in t):
        assert P(t[0][0]) == 1 and int(t[0][1:]) == 3, t
        for k in range(len(t) - 1):
            assert P(t[k + 1][0]) - P(t[k][0]) == 2, (i["id"], t)
            assert int(t[k + 1][1:]) - int(t[k][1:]) == 3, (i["id"], t)
        expect = fn(t)
    else:
        expect = fn([int(x) for x in t])
    assert key == str(expect), (i["id"], key, expect)
    seen_rules += 1
assert seen_rules == 10, seen_rules

# ---------------- global isolation ------------------------------------------
all_ids = set()
stems = {}
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

print("ALL CHECKS PASSED (part1-inductive drill)")
print("answers:", dict(sorted(ans.items())))
print("chapters:", dict(chapters))
print("series rules re-derived:", seen_rules)
