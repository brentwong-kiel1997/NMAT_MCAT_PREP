#!/usr/bin/env python3
"""Rebalance chapter-library practice answer keys so A/B/C/D are equally likely.

Sibling of scripts/rebalance_tutorial_keys.py for content/chapters/*.yml
practice items (flat list, optional distractors). Re-labels choices — never
content: the four option texts are permuted, the ``answer:`` letter follows
its text, and every ``distractors:`` entry travels with the option it
explains. Deterministic: seed + file path drive every decision.

usage: rebalance_chapter_keys.py            # dry run, prints plan
       rebalance_chapter_keys.py --write    # apply
"""
from __future__ import annotations

import argparse
import random
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CHAPTERS = REPO / "content" / "chapters"
LETTERS = ["A", "B", "C", "D"]


def permute(item: dict, target: str, rng: random.Random) -> dict:
    """Move the correct answer's text to `target`; carry distractor notes."""
    correct_text = item["choices"][item["answer"]]
    wrong_old = [k for k in LETTERS if k != item["answer"]]
    others = [item["choices"][k] for k in wrong_old]
    rng.shuffle(others)
    remaining = [k for k in LETTERS if k != target]
    # every old letter maps to exactly one new letter (3 wrong slots + target)
    mapping = {item["answer"]: target}
    for old, new in zip(wrong_old, remaining):
        mapping[old] = new
    new_choices = {target: correct_text}
    for old, text in zip(wrong_old, others):
        new_choices[mapping[old]] = text
    item["choices"] = {k: new_choices[k] for k in LETTERS}
    old_answer = item["answer"]
    item["answer"] = target
    if item.get("distractors"):
        notes = {mapping[old]: note for old, note in item["distractors"].items()}
        item["distractors"] = {k: notes[k] for k in LETTERS if k in notes}
    return old_answer


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260902)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    files = sorted(CHAPTERS.glob("*.yml"))
    items: dict[Path, list] = {}
    before: Counter[str] = Counter()
    for path in files:
        doc = yaml.safe_load(open(path))
        plist = doc.get("practice") or []
        items[path] = plist
        before.update(p["answer"] for p in plist)
    total = sum(before.values())
    quota = total // 4
    extra = total - quota * 4  # first `extra` letters get one more slot
    caps = {l: quota + (1 if i < extra else 0) for i, l in enumerate(LETTERS)}

    counts = Counter(before)
    plan: list[tuple[Path, dict, str]] = []
    for path in files:  # deterministic order
        rng = random.Random(f"{args.seed}:{path.name}")
        used = Counter(p["answer"] for p in items[path])
        for p in items[path]:
            cur = p["answer"]
            if counts[cur] <= caps[cur]:
                continue  # letter not over quota — leave alone
            under = [l for l in LETTERS if counts[l] < caps[l]]
            if not under:
                continue
            # prefer a letter unused elsewhere in this file (distinct keys per file)
            free = [l for l in under if used[l] == 0] or under
            target = free[rng.randrange(len(free))]
            plan.append((path, p, target))
            counts[cur] -= 1
            counts[target] += 1
            used[cur] -= 1
            used[target] += 1

    print(f"{total} items across {len(files)} files; caps {caps}")
    print("before: " + " ".join(f"{l}={before[l]} ({100 * before[l] / total:.1f}%)" for l in LETTERS))
    print(f"plan: {len(plan)} items move")
    after = Counter({l: before[l] for l in LETTERS})
    for _, p, t in plan:
        after[p["answer"]] -= 1
        after[t] += 1
    print("after:  " + " ".join(f"{l}={after[l]} ({100 * after[l] / total:.1f}%)" for l in LETTERS))

    if not args.write:
        print("dry run — rerun with --write to apply")
        return 0

    for path, p, target in plan:
        permute(p, target, random.Random(f"{args.seed}:{path.name}"))
        doc = yaml.safe_load(open(path))
        for i, existing in enumerate(doc.get("practice") or []):
            if existing["id"] == p["id"]:
                doc["practice"][i] = p
                break
        yaml.safe_dump(doc, open(path, "w"), allow_unicode=True, sort_keys=False, width=100)
    print(f"wrote {len(plan)} rebalanced items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
