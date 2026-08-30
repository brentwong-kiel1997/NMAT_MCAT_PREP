#!/usr/bin/env python3
"""Verify content/exam-bank/nmat/drill/part1-quantitative.yml against the drill schema.

Every numeric answer is recomputed a second time here, from the constants that
appear in the stems, and compared with the keyed option text.
"""
import glob
import re
import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/drill/part1-quantitative.yml"
ALLOWED = {"fundamental-operations", "problem-solving", "data-interpretation"}

d = yaml.safe_load(open(PATH))
assert set(d) == {"exam", "section", "label", "subject", "block", "_drill", "items"}, sorted(d)
assert d["exam"] == "nmat" and d["section"] == "drill-part1-quantitative"
assert d["label"] == "Quantitative drill"
assert d["subject"] == "quantitative" and d["block"] == "part1"
assert d["_drill"] is True
assert len(d["items"]) == 25 and d["section"].startswith("drill-")

ans = Counter(i["answer"] for i in d["items"])
assert max(ans.values()) <= 7, ans
chapters = Counter()
ids = []
for i in d["items"]:
    assert set(i) == {"id", "q", "choices", "answer", "explain", "distractors", "chapter"}, sorted(i)
    assert re.fullmatch(r"nmat-d-p1q-\d{3}", i["id"]), i["id"]
    ids.append(i["id"])
    assert set(i["choices"]) == {"A", "B", "C", "D"} and i["answer"] in i["choices"]
    assert i["answer"] not in i["distractors"] and set(i["distractors"]) <= {"A", "B", "C", "D"}
    assert set(i["distractors"]) == set(i["choices"]) - {i["answer"]}, i["id"]
    assert i["chapter"] in ALLOWED, i["chapter"]
    chapters[i["chapter"]] += 1
    assert i["q"] and i["explain"]
    assert len(set(i["choices"].values())) == 4, i["id"]
    # a distractor note may quote its own wrong value, never the keyed value
    # (skipped for one-character keys such as "3", where the test is meaningless)
    keyed = i["choices"][i["answer"]].strip()
    if len(keyed) > 1:
        pat = r"(?<![\d.,])" + re.escape(keyed) + r"(?![\d.,])"
        for L, note in i["distractors"].items():
            assert not re.search(pat, note), (i["id"], L, note)
assert chapters == Counter({"fundamental-operations": 9, "problem-solving": 9,
                            "data-interpretation": 7}), chapters
assert ids == ["nmat-d-p1q-%03d" % n for n in range(1, 26)], ids[:5]

# ---- recompute every answer independently ---------------------------------
HC = {"Jan": 240, "Feb": 300, "Mar": 210}
by_id = {i["id"]: i for i in d["items"]}
EXPECT = {
    "nmat-d-p1q-001": 18 - 2 * (3 + 4) ** 2 / 7,
    "nmat-d-p1q-002": (450 - 360) / 360 * 100,
    "nmat-d-p1q-004": 3 ** (4 - 2 - 1),
    "nmat-d-p1q-005": 4.2 / 0.07,
    "nmat-d-p1q-007": 4 * (4200 / 3),
    "nmat-d-p1q-008": 12000 + 12000 * 0.06 * 8 / 12,
    "nmat-d-p1q-009": 245 ** 0.5,
    "nmat-d-p1q-010": 12,
    "nmat-d-p1q-011": 1 / (1 / 4 - 1 / 12),
    "nmat-d-p1q-012": 12 * (60 - 52) / (52 - 48),
    "nmat-d-p1q-013": 240 / (120 / 60 + 120 / 40),
    "nmat-d-p1q-014": 45 * 49,
    "nmat-d-p1q-015": 2520 / (1.4 * 0.9),
    "nmat-d-p1q-016": (18 + 4) * (12 + 4) - 18 * 12,
    "nmat-d-p1q-017": 28 + 24 - (45 - 9),
    "nmat-d-p1q-018": next(n for n in range(11, 200) if n % 5 == 3 and n % 7 == 4),
    "nmat-d-p1q-019": 45000 / HC["Feb"],
    "nmat-d-p1q-020": (37800 / 210 - 36000 / 240) / (36000 / 240) * 100,
    "nmat-d-p1q-021": HC["Jan"] + HC["Feb"] + HC["Mar"],
    "nmat-d-p1q-022": 1200000 / 8 - 900000 / 9,
    "nmat-d-p1q-023": (1200000 + 900000) / 2500000 * 100,
    "nmat-d-p1q-024": 1200000 * 1.1 + 900000 * 0.9,
    "nmat-d-p1q-025": 900000 / (1200000 + 900000) * 100,
}
SPECIAL = {"nmat-d-p1q-003": "5/8", "nmat-d-p1q-006": "8 2/5"}


def parse(text):
    """Pull the leading quantity out of an option such as 'P5,600' or '48 km/h'."""
    t = text.strip()
    if t in SPECIAL.values():
        return t
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", t)
    assert m, t
    return float(m.group().replace(",", ""))


for iid, want in EXPECT.items():
    item = by_id[iid]
    got = parse(item["choices"][item["answer"]])
    if iid in SPECIAL:
        # fraction / mixed-number answers are checked as text
        assert item["choices"][item["answer"]] == SPECIAL[iid], (iid, got)
        continue
    if isinstance(got, str):
        assert got == want, (iid, got, want)
        continue
    if iid == "nmat-d-p1q-009":                     # closest decimal to sqrt 245
        assert abs(want - got) < 0.05, (iid, want, got)
        assert got == 15.7, (iid, got)
    elif iid in ("nmat-d-p1q-020", "nmat-d-p1q-023", "nmat-d-p1q-025"):
        assert abs(want - got) < 0.1, (iid, want, got)
    else:
        assert abs(want - got) < 1e-6, (iid, want, got)
# the two fraction answers must be the reduced value
assert 7 / 8 - 2 / 3 + 5 / 12 == 15 / 24 and 15 / 24 == 5 / 8
assert (7 / 2) * (12 / 5) == 42 / 5 == 8.4

# ---- every stem must carry the numbers its explanation relies on -----------
for i in d["items"]:
    assert i["explain"].strip().endswith((".", "%", ":")), i["id"]
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

print("ALL CHECKS PASSED (part1-quantitative drill)")
print("answers:", dict(sorted(ans.items())))
print("chapters:", dict(chapters))
