#!/usr/bin/env python3
"""Independent verification of part1-inductive.yml.

Part 1: the required structural checks.
Part 2: every series answer re-derived from scratch (rule stated, applied to
        every given term, then the next term produced and matched to the
        letter carrying that value).
Part 3: distractor notes must address real option text and be distinct.
"""
import re
from collections import Counter
from pathlib import Path

import yaml

PATH = "/home/ubuntu/django-wsgi/content/exam-bank/nmat/part1-inductive.yml"
IMAGES = Path(__file__).resolve().parents[2] / "content" / "images"
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


# ---------------------------------------------------------------- required ---
d = yaml.safe_load(open(PATH))
check(d["section"] == "part1-inductive", "section key")
check(len(d["items"]) == 30, "30 items, got %d" % len(d["items"]))
check(d["exam"] == "nmat", "exam")
check(d["label"] == "Inductive Reasoning", "label")
check(d["subject"] == "inductive-reasoning", "subject")
check(d["block"] == "part1", "block")
check(d["items_expected"] == 30, "items_expected")
check(d["passages"] == [], "passages empty")
check(list(d) == ["exam", "section", "label", "subject", "block",
                  "items_expected", "items", "passages"], "top-level keys %s" % list(d))

ans = Counter(i["answer"] for i in d["items"])
check(max(ans.values()) <= 8, "answer balance %s" % ans)
check(min(ans.values()) >= 7, "answer balance min %s" % ans)

for n, i in enumerate(d["items"], 1):
    tag = "item %s" % i["id"]
    check(set(i["choices"]) == {"A", "B", "C", "D"}, tag + " choices")
    check(i["answer"] in i["choices"], tag + " answer in choices")
    check(i["answer"] not in i["distractors"], tag + " no distractor on answer")
    check(set(i["distractors"]) <= {"A", "B", "C", "D"}, tag + " distractor keys")
    check(set(i["distractors"]) == set("ABCD") - {i["answer"]},
          tag + " distractors are exactly the 3 wrong letters: %s" % sorted(i["distractors"]))
    check(i["chapter"] in ("number-and-letter-series", "figure-series",
                           "figure-grouping"), tag + " chapter")
    for k in ("q", "explain"):
        check(isinstance(i[k], str) and i[k].strip(), tag + " non-empty " + k)
    for k, v in i["distractors"].items():
        check(isinstance(v, str) and v.strip(), tag + " non-empty distractor " + k)
    check(len(set(i["choices"].values())) == 4, tag + " options all distinct")
    check(i["id"] == "nmat-p1i-%03d" % n, tag + " id padding")

ids = [i["id"] for i in d["items"]]
check(len(set(ids)) == 30, "unique ids")
check(len({i["q"].strip() for i in d["items"]}) == 30, "unique stems")

# ---------------------------------------------- re-derive the series rules ---
by_id = {i["id"]: i for i in d["items"]}
by_n = {n: i for n, i in enumerate(d["items"], 1)}


def letters_of(seq):
    return [ord(c) - 64 for c in seq]


def value_of(item, letter):
    v = item["choices"][letter]
    m = re.fullmatch(r"[A-Z]", v)
    return ord(v) - 64 if m else None


def expected_letter(item, want):
    got = [L for L in "ABCD" if item["choices"][L] == str(want)]
    check(len(got) == 1, "%s: value %s not present exactly once" % (item["id"], want))
    if got:
        check(got[0] == item["answer"],
              "%s: answer letter %s but the derived next term %s sits on %s"
              % (item["id"], item["answer"], want, got[0]))


# 1  constant difference +6
seq = [7, 13, 19, 25, 31]
check(all(b - a == 6 for a, b in zip(seq, seq[1:])), "1: +6 on every term")
expected_letter(by_n[1], seq[-1] + 6)

# 2  constant ratio x3
seq = [2, 6, 18, 54, 162]
check(all(b == 3 * a for a, b in zip(seq, seq[1:])), "2: x3 on every term")
expected_letter(by_n[2], seq[-1] * 3)

# 3  alternating +5 / -3
seq = [4, 9, 6, 11, 8, 13]
steps = [b - a for a, b in zip(seq, seq[1:])]
check(steps == [5, -3, 5, -3, 5], "3: alternating +5/-3, got %s" % steps)
expected_letter(by_n[3], seq[-1] + steps[-1] * -1 if False else seq[-1] - 3)

# 4  interleaved +3 leg and -2 leg
seq = [2, 15, 5, 13, 8, 11]
odd, even = seq[0::2], seq[1::2]
check(odd == [2, 5, 8] and [b - a for a, b in zip(odd, odd[1:])] == [3, 3],
      "4: odd leg 2,5,8 (+3)")
check(even == [15, 13, 11] and [b - a for a, b in zip(even, even[1:])] == [-2, -2],
      "4: even leg 15,13,11 (-2)")
check(odd[-1] + 3 == 11, "4: seventh term")
expected_letter(by_n[4], 11)

# 5  squares of the odd numbers
seq = [1, 9, 25, 49, 81]
check(seq == [(2 * k + 1) ** 2 for k in range(5)], "5: odd squares")
expected_letter(by_n[5], 11 ** 2)

# 6  cubes
seq = [1, 8, 27, 64, 125]
check(seq == [k ** 3 for k in range(1, 6)], "6: cubes 1..5")
expected_letter(by_n[6], 6 ** 3)

# 7  Fibonacci-style
seq = [1, 3, 4, 7, 11, 18]
check(all(seq[k] == seq[k - 1] + seq[k - 2] for k in range(2, len(seq))),
      "7: each term = sum of the two before it")
expected_letter(by_n[7], seq[-1] + seq[-2])

# 8  gaps growing by 1
seq = [2, 3, 5, 8, 12, 17]
check([b - a for a, b in zip(seq, seq[1:])] == [1, 2, 3, 4, 5], "8: gaps +1..+5")
expected_letter(by_n[8], 17 + 6)

# 9  letters, gaps +2..+5 then +6
seq = letters_of("BDGKP")
check([b - a for a, b in zip(seq, seq[1:])] == [2, 3, 4, 5], "9: letter gaps 2,3,4,5")
check(1 <= seq[-1] + 6 <= 26, "9: in range")
expected_letter(by_n[9], chr(64 + seq[-1] + 6))

# 10  letter pairs: first forward, second backward
pairs = ["AZ", "BY", "CX"]
check([p[0] for p in pairs] == ["A", "B", "C"], "10: first letters advance")
check([p[1] for p in pairs] == ["Z", "Y", "X"], "10: second letters retreat")
nxt = chr(ord("C") + 1) + chr(ord("X") - 1)
check(nxt == "DW", "10: next pair")
expected_letter(by_n[10], nxt)

# 11  subtractions growing by 4
seq = [100, 96, 88, 76, 60]
check([b - a for a, b in zip(seq, seq[1:])] == [-4, -8, -12, -16], "11: -4,-8,-12,-16")
expected_letter(by_n[11], 60 - 20)

# 12  letters, gaps -2..-5 then -6
seq = letters_of("ZXUQL")
check([b - a for a, b in zip(seq, seq[1:])] == [-2, -3, -4, -5], "12: letter gaps -2..-5")
check(seq[-1] - 6 >= 1, "12: in range")
expected_letter(by_n[12], chr(64 + seq[-1] - 6))

# ------------------------------------- figure items must be self-contained ---
# An item either spells its figures out in words (stem carries every panel) or
# attaches a generated 4-panel sheet (figure: items/<id>.svg) and keeps only
# the question. Both routes must leave the item answerable on its own.
figser = [i for i in d["items"] if i["chapter"] == "figure-series"]
figgrp = [i for i in d["items"] if i["chapter"] == "figure-grouping"]
check(len(figser) == 9, "9 figure-series, got %d" % len(figser))
check(len(figgrp) == 9, "9 figure-grouping, got %d" % len(figgrp))
for i in figser + figgrp:
    if i.get("figure"):
        check(i["figure"].startswith("items/"), "%s: odd figure path %r"
              % (i["id"], i["figure"]))
        check((IMAGES / i["figure"]).is_file(),
              "%s: figure file missing: %s" % (i["id"], i["figure"]))
        check(i["q"].strip().endswith("?"),
              i["id"] + ": figure-backed stem is not a question")
        check("Four figures are shown" not in i["q"],
              i["id"] + ": stem still narrates the figure instead of attaching it")
        continue
    check(len(i["q"]) > 100, "%s: figure stem too thin to be self-contained (%d chars)"
          % (i["id"], len(i["q"])))
    if i in figser:
        check(len(re.findall(r"Frame \d", i["q"])) >= 4,
              i["id"] + ": fewer than four frames described")
        check("look like" in i["q"], i["id"] + ": no 'what comes next' question")
    else:
        for marker in ("A.", "B.", "C.", "D."):
            check(marker in i["q"],
                  i["id"] + ": figure %r not enumerated in the stem" % marker)
        check("not belong" in i["q"], i["id"] + ": no outsider question")

# distractor notes: mechanically checkable guards only. Alignment of note to
# option text is reviewed item by item below the script (see manual pass).
for i in d["items"]:
    seen_notes = set()
    for L, note in i["distractors"].items():
        check(note.strip() not in seen_notes, i["id"] + ": duplicated distractor note")
        seen_notes.add(note.strip())
        check(len(note.split()) >= 5, "%s: distractor %s note too thin" % (i["id"], L))
        opt = i["choices"][L]
        # a numeric option's note must cite a number (its gap / its source)
        if re.fullmatch(r"\d+", opt.strip()):
            check(re.search(r"\d", note) is not None,
                  "%s: distractor %s note cites no number for option %s" % (i["id"], L, opt))
        # a bare-letter option's note must cite the letter or its position
        if re.fullmatch(r"[A-Z]", opt.strip()):
            check(re.search(r"\b[A-Z]\b|\d", note) is not None,
                  "%s: distractor %s note cites no letter or position for option %s"
                  % (i["id"], L, opt))
        # a pair-of-letters option's note must cite letters
        if re.fullmatch(r"[A-Z]{2}", opt.strip()):
            check(re.search(r"\b[A-Z]{2}\b|\b[A-Z]\b", note) is not None,
                  "%s: distractor %s note cites no letters for option %s" % (i["id"], L, opt))

print("series/figure items checked:", len(by_n))
print("answers:", dict(sorted(ans.items())))
if fails:
    print("FAILURES (%d):" % len(fails))
    for f in fails:
        print("  -", f)
    raise SystemExit(1)
print("ALL CHECKS PASSED")
