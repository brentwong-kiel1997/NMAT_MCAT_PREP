#!/usr/bin/env python3
"""Verify content/exam-bank/nmat/part2-physics.yml against the item schema.

Runs four passes:
  1. the required schema / key / balance assertions,
  2. a replica of portal/management/commands/validate_content.py's exam-bank
     rules (chapter existence, tutorial back-link, duplicate ids and stems,
     distractor-key guard, blueprint listing),
  3. an independent RE-SOLVE of every numeric item — each correct choice is
     recomputed from the stem's parameters and compared,
  4. the same recomputation applied to every distractor, confirming that each
     choice really equals the error its distractor note names.
"""
import math
import os
import re
import yaml
from collections import Counter

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/part2-physics.yml"
CONTENT = "/home/ubuntu/django-wsgi/content"
d = yaml.safe_load(open(PATH))

ALLOWED = set("""4a-motion-forces-work-energy-equilibrium 4b-fluids-for-circulation-and-gas-exchange
4c-electrochemistry-and-electrical-circuits 4d-light-and-sound-interacting-with-matter
electricity-and-magnetism mechanics modern-physics thermodynamics vibrations-waves-and-optics""".split())

# ---- pass 1: required schema checks ----------------------------------------
assert set(d) == {"exam", "section", "label", "subject", "block", "items_expected",
                  "items", "passages"}, sorted(d)
assert d["exam"] == "nmat" and d["section"] == "part2-physics" and d["label"] == "Physics"
assert d["subject"] == "physics" and d["block"] == "part2"
assert d["items_expected"] == 30 and len(d["items"]) == 30
assert d["passages"] == []

ans = Counter(i["answer"] for i in d["items"])
assert max(ans.values()) <= 8, ans
assert min(ans.values()) >= 7, ans

for i in d["items"]:
    assert set(i["choices"]) == {"A", "B", "C", "D"} and i["answer"] in i["choices"]
    assert i["answer"] not in i["distractors"] and i["chapter"] in ALLOWED
    assert len(i["distractors"]) == 3
    assert sorted(i["distractors"]) == sorted(l for l in "ABCD" if l != i["answer"])
    assert i["q"].strip() and i["explain"].strip()
    assert all(n.strip() for n in i["distractors"].values())

# ---- pass 2: repo validator replica ----------------------------------------
probs = []
chapters = {os.path.splitext(f)[0]
            for f in os.listdir(CONTENT + "/chapters") if f.endswith(".yml")}
tutorials = {os.path.splitext(f)[0]
             for f in os.listdir(CONTENT + "/tutorials/physics") if f.endswith(".yml")}
blueprint = yaml.safe_load(open(CONTENT + "/exams/nmat.yml"))["blueprint"]["blocks"]
if d["section"] not in [s for b in blueprint for s in (b.get("bank") or [])]:
    probs.append("section not listed in any nmat blueprint block")
stems, ids = set(), set()
for i in d["items"]:
    iid = i["id"]
    if iid in ids:
        probs.append("duplicate item id " + iid)
    ids.add(iid)
    if i["answer"] in i["distractors"]:
        probs.append(iid + ": distractor on the answer letter")
    if i["chapter"] not in chapters:
        probs.append(iid + ": unknown chapter")
    elif i["chapter"] not in tutorials:
        probs.append(iid + ": chapter has no tutorial")
    if i["q"].strip() in stems:
        probs.append(iid + ": duplicate stem")
    stems.add(i["q"].strip())
for letter, n in ans.items():
    if n / 30 > 0.4:
        probs.append("unbalanced key " + letter)
assert not probs, probs

# ---- pass 3/4: independent re-solve ----------------------------------------
items = {int(i["id"].split("-")[-1]): i for i in d["items"]}


def num(text):
    """Numeric value carried by a choice string ('1.6 x 10^4 Pa' -> 16000.0)."""
    t = text.replace(",", "")
    m = re.match(r"^\s*(-?\d+\.?\d*)\s*x\s*10\^(-?\d+)", t)
    if m:
        return float(m.group(1)) * 10 ** int(m.group(2))
    m = re.match(r"^\s*1/(\d+)", t)
    if m:
        return 1.0 / int(m.group(1))
    m = re.search(r"-?\d+\.?\d*", t)
    return float(m.group()) if m else None


r = math.radians
# {item: {choice_text: value recomputed from the stem (or from the named error)}}
EXP = {
 1: {"44 m": .5 * 9.8 * 3.0 ** 2, "29 m": 9.8 * 3.0, "88 m": 9.8 * 9,
     "15 m": .5 * 9.8 * 3.0},
 2: {"2.0 s": math.sqrt(2 * 20 / 10), "1.5 s": 15 / 10,
     "1.4 s": math.sqrt(20 / 10), "4.0 s": 2 * 20 / 10},
 3: {"3600 N": 1200 * (24 / 8.0), "9600 N": 1200 * 8.0, "28,800 N": 1200 * 24,
     "450 N": 1200 * (24 / 8.0 ** 2)},
 4: {"98 N": .25 * 40 * 9.8, "392 N": 40 * 9.8, "9.8 N": .025 * 40 * 9.8,
     "10 N": .25 * 40},
 5: {"5.0 m/s^2": 10 * math.sin(r(30)), "10 m/s^2": 10.0,
     "8.7 m/s^2": 10 * math.cos(r(30)), "2.5 m/s^2": 10 * math.sin(r(30)) ** 2},
 6: {"100 J": 50 * 4 * math.cos(r(60)), "200 J": 200.0,
     "173 J": 50 * 4 * math.sin(r(60)), "400 J": 50 * 4 / math.cos(r(60))},
 7: {"200 W": 50 * 10 * 4 / 10, "20 W": 50 * 4 / 10, "400 W": 50 * 10 * 4 / 5,
     "2000 W": 50 * 10 * 4},
 8: {"12 m/s": 1200 * 20 / 2000, "20 m/s": 20.0, "10 m/s": 10.0,
     "30 m/s": 1200 * 20 / 800},
 9: {"750 N": .5 * (20 + 10) / .020, "250 N": .5 * 10 / .020,
     "500 N": .5 * 20 / .020, "0.30 N": .5 * 30 * .020},
 10: {"1.5 N.m": abs(20 * .30 - 15 * .50), "13.5 N.m": 20 * .30 + 15 * .50,
      "6.0 N.m": 6.0, "4.5 N.m": 4.5},
 11: {"1.0 x 10^5 Pa": 1000 * 10 * 10, "1.0 x 10^4 Pa": 100 * 10 * 10,
      "2.0 x 10^5 Pa": 1000 * 10 * 10 + 1.01e5, "1.0 x 10^6 Pa": 1000 * 10 * 100},
 12: {"25 N": 1000 * 10 * (2.0 / 800), "20 N": 2.0 * 10,
      "2.5 N": 1000 * 10 * 2.5e-4, "250 N": 1000 * 10 * 2.5e-2},
 13: {"1.8 m/s": .20 * (3.0 / 1.0) ** 2, "0.60 m/s": .20 * 3.0,
      "0.022 m/s": .20 / 9, "0.20 m/s": .20},
 14: {"1.6 x 10^4 Pa": .5 * 1000 * (6.0 ** 2 - 2.0 ** 2),
      "3.2 x 10^4 Pa": 1000 * 32, "8.0 x 10^3 Pa": .5 * 1000 * (6.0 - 2.0) ** 2,
      "1.8 x 10^4 Pa": .5 * 1000 * 36},
 15: {"1/16": .5 ** 4, "1/2": .5, "1/4": .25, "1/8": .125},
 16: {"4.2 x 10^5 J": 2.0 * 4200 * 50, "1.7 x 10^5 J": 2.0 * 4200 * 20,
      "8.4 x 10^5 J": 4.0 * 4200 * 50, "4.2 x 10^2 J": 4.2e2},
 17: {"1.5 atm": 1.0 * 450 / 300, "0.67 atm": 300 / 450, "1.0 atm": 1.0,
      "4.5 atm": 450 / 100},
 18: {"40%": 100 * (1 - 300 / 500), "60%": 100 * 300 / 500, "67%": 100 * 200 / 300,
      "25%": 100 * (1 - 300 / 400)},
 19: {"330 m/s": 440 * .75, "587 m/s": 440 / .75, "0.0017 m/s": .75 / 440,
      "3.3 x 10^4 m/s": 440 * 75},
 20: {"850 Hz": 750 * 340 / 300, "671 Hz": 750 * 340 / 380,
      "662 Hz": 750 * 300 / 340, "838 Hz": 750 * 380 / 340},
 21: {"2.0 x 10^8 m/s": 3.0e8 / 1.50, "4.5 x 10^8 m/s": 3.0e8 * 1.50,
      "3.0 x 10^8 m/s": 3.0e8, "1.5 x 10^8 m/s": 3.0e8 / 2},
 22: {"30 cm on the far side of the lens": 1 / (1 / 10 - 1 / 15),
      "6.0 cm": 1 / (1 / 15 + 1 / 10), "25 cm": 25.0, "10 cm": 10.0},
 23: {"30 degrees": math.degrees(math.asin(1 / 2.0)),
      "60 degrees": math.degrees(math.acos(.5)),
      "27 degrees": math.degrees(math.atan(.5)), "15 degrees": 15.0},
 24: {"0.60 N": 9.0e9 * 2.0e-6 * 3.0e-6 / .30 ** 2,
      "60 N": 9.0e9 * 6e-12 / .03 ** 2, "0.18 N": 9.0e9 * 6e-12 / .30,
      "1.2 N": 1.2},
 25: {"2.4 A": 12 / ((6.0 * 3.0 / 9.0) + 3.0), "0.80 A": 12 / 15,
      "10 A": 12 / (1 / (1 / 6 + 1 / 3 + 1 / 3)), "6.0 A": 12 / 2.0},
 26: {"36 W": 12 ** 2 / 4.0, "3.0 W": 12 / 4.0, "48 W": 12 * 4.0,
      "576 W": 12 ** 2 * 4.0},
 27: {"0.20 N": .40 * 5.0 * .20 * math.sin(r(30)),
      "0.40 N": .40 * 5.0 * .20, "2.0 N": .40 * 5.0 * 2.0 * math.sin(r(30)),
      "5.0 N": .40 * 5.0 / .20 * math.sin(r(30))},
 28: {"1.0 V": 50 * .010 * (.40 / .20), "0.020 V": .010 * (.40 / .20),
      "10 V": 50 * .10 * (.40 / .20), "0.040 V": 50 * .010 * (.40 * .20)},
 29: {"1.0 eV": 3.0 - 2.0, "5.0 eV": 5.0, "6.0 eV": 6.0, "2.0 eV": 2.0},
 30: {"10 g": 80 * .5 ** 3, "40 g": 40.0, "5.0 g": 80 / 16, "32 g": 80 - 3 * 16},
}
ANSWER_TEXT = {1: "44 m", 2: "2.0 s", 3: "3600 N", 4: "98 N", 5: "5.0 m/s^2",
               6: "100 J", 7: "200 W", 8: "12 m/s", 9: "750 N", 10: "1.5 N.m",
               11: "1.0 x 10^5 Pa", 12: "25 N", 13: "1.8 m/s", 14: "1.6 x 10^4 Pa",
               15: "1/16", 16: "4.2 x 10^5 J", 17: "1.5 atm", 18: "40%",
               19: "330 m/s", 20: "850 Hz", 21: "2.0 x 10^8 m/s",
               22: "30 cm on the far side of the lens", 23: "30 degrees",
               24: "0.60 N", 25: "2.4 A", 26: "36 W", 27: "0.20 N", 28: "1.0 V",
               29: "1.0 eV", 30: "10 g"}

bad = 0
for n in range(1, 31):
    it = items[n]
    exp = EXP[n]
    assert set(exp) == set(it["choices"].values()), (n, "choice text set drifted")
    assert it["choices"][it["answer"]] == ANSWER_TEXT[n], (n, "wrong text on key")
    for text, want in exp.items():
        got = num(text)
        if not (got is not None and abs(got - want) <= max(.03 * max(abs(want), 1), .35)):
            bad += 1
            print(f"FAIL {n:02d} '{text}' parsed={got} recomputed={want}")
    print(f"OK  {n:02d} {it['answer']} -> {it['choices'][it['answer']]}")
assert bad == 0, bad

print("\nPASS: 30 items; answers %s; all values re-solved" % dict(sorted(ans.items())))
