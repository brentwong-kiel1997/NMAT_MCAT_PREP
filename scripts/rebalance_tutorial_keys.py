#!/usr/bin/env python3
"""Rebalance tutorial answer keys so A/B/C/D are equally likely.

Tutorial check / passage / review questions were authored with the key sitting
on A or B roughly 91% of the time, so a learner can guess their way through a
tutorial. This script re-labels choices — never content: the four option texts
of a question are permuted, the ``answer:`` letter follows its text, and every
``distractors:`` entry travels with the option it explains.

Guarantees
- deterministic: a fixed seed (plus the file path) drives every decision, so
  re-running reproduces byte-identical files.
- balance is set per FILE, so each tutorial is guess-proof on its own; the
  global distribution follows automatically (~25% per letter).
- minimal churn: a question only moves when its current letter is over the
  file's quota. Files that already land 3/3/3/3 are left byte-identical.
- content-preserving: option texts move verbatim — including values that wrap
  over several lines — and every rewritten file is re-parsed and checked
  against the original before the run is reported as clean.

Usage
    python3 scripts/rebalance_tutorial_keys.py            # dry run, prints plan
    python3 scripts/rebalance_tutorial_keys.py --write    # rewrite the files

Afterwards regenerate content/MANIFEST.json (validate_content hashes these
files) and run the gate:

    python3 manage.py refresh_manifest && python3 manage.py validate_content
"""

from __future__ import annotations

import argparse
import random
import re
from collections import Counter
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
TUTORIALS = REPO / "content" / "tutorials"
LETTERS = "ABCD"
LETTER_KEY_RE = re.compile(r"^(\s*)[A-D]: ")
VALUE_RE = re.compile(r"^\s*[A-D]: (.*)$")


class Question:
    """One question located in a file's text, as verbatim line groups."""

    def __init__(self) -> None:
        # letter -> (first line index, [lines]) covering the whole value,
        # continuation lines included
        self.opt_raw: dict[str, tuple[int, list[str]]] = {}
        self.dist_raw: dict[str, tuple[int, list[str]]] = {}
        self.answer_line: int | None = None
        self.answer: str | None = None
        self.new_answer: str | None = None      # set by the planner
        self.perm: dict[str, str] | None = None


def _read_question(node: yaml.MappingNode, lines: list[str]) -> Question:
    """Collect the line span of every option/answer/distractor of one question."""
    q = Question()
    for key_node, value_node in node.value:
        key = key_node.value
        if key in ("options", "distractors") and isinstance(value_node, yaml.MappingNode):
            target = q.opt_raw if key == "options" else q.dist_raw
            for letter_node, letter_value in value_node.value:
                letter_start = letter_node.start_mark.line
                # end_mark.line is INCLUSIVE (PyYAML) — wrapped values span it
                letter_end = max(letter_value.end_mark.line, letter_start) + 1
                target[letter_node.value] = (letter_start, lines[letter_start:letter_end])
        elif key == "answer" and isinstance(value_node, yaml.ScalarNode):
            q.answer_line = value_node.start_mark.line
            q.answer = value_node.value
    return q


def scan(path: Path) -> tuple[list[str], list[Question]]:
    """Locate the check/passage/review questions of a tutorial file.

    Line spans come from ``yaml.compose`` (so examples[].distractors, which have
    no answer letter, are never mistaken for question options), while the edits
    are applied line-by-line: untouched text stays byte-identical and the
    hand-wrapped style survives.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    root = yaml.compose(text)
    assert isinstance(root, yaml.MappingNode), f"{path}: unexpected document"

    question_nodes: list[yaml.MappingNode] = []
    for key_node, value_node in root.value:
        if key_node.value == "sections" and isinstance(value_node, yaml.SequenceNode):
            for section in value_node.value:
                for key2, value2 in section.value:
                    if key2.value == "check" and isinstance(value2, yaml.SequenceNode):
                        question_nodes += value2.value
        elif key_node.value == "passage" and isinstance(value_node, yaml.MappingNode):
            for key2, value2 in value_node.value:
                if key2.value == "questions" and isinstance(value2, yaml.SequenceNode):
                    question_nodes += value2.value
        elif key_node.value == "review_questions" and isinstance(value_node, yaml.SequenceNode):
            question_nodes += value_node.value

    return lines, [_read_question(node, lines) for node in question_nodes]


def plan_file(questions: list[Question], rng: random.Random) -> list[Question]:
    """Assign new answer letters so each letter lands on its per-file quota."""
    movable = [q for q in questions
               if q.answer in LETTERS and set(q.opt_raw) == set(LETTERS)]
    total = len(movable)
    if total < 4:
        return []

    target = {letter: total // 4 + (1 if n < total % 4 else 0)
              for n, letter in enumerate(LETTERS)}
    counts = Counter(q.answer for q in movable)
    deficit = {l: max(0, target[l] - counts[l]) for l in LETTERS}
    surplus = {l: max(0, counts[l] - target[l]) for l in LETTERS}
    if not any(surplus.values()):
        return []  # already balanced — leave the file untouched

    for q in movable:
        if surplus[q.answer] <= 0:
            continue  # this letter is still wanted — keep it, zero churn
        pool = [l for l in LETTERS for _ in range(deficit[l])]
        dest = rng.choice(pool)
        deficit[dest] -= 1
        surplus[q.answer] -= 1

        src = [l for l in LETTERS if l != q.answer]
        dst = [l for l in LETTERS if l != dest]
        rng.shuffle(dst)
        q.perm = dict(zip([q.answer] + src, [dest] + dst))
        q.new_answer = dest

    assert not any(deficit.values()) and not any(surplus.values()), "quota leak"
    return [q for q in movable if q.perm]


def relabel(lines: list[str], q: Question) -> None:
    """Rewrite one question's option/answer/distractor lines in place.

    A block is a contiguous run of lines, so its letter groups are re-emitted
    in ascending letter order into the block's own slots — bodies stay
    verbatim (wrapped values included), only the key letters change.
    """
    assert q.perm is not None
    for raw in (q.opt_raw, q.dist_raw):
        if not raw:
            continue
        groups = [(q.perm[letter], start, body) for letter, (start, body) in raw.items()]
        block_start = min(start for _, start, _ in groups)
        span = sum(len(body) for _, _, body in groups)
        groups.sort(key=lambda group: group[0])           # keys ascend A → D

        flat: list[str] = []
        for new_letter, _, body in groups:
            body = list(body)
            body[0] = LETTER_KEY_RE.sub(lambda m: f"{m.group(1)}{new_letter}: ",
                                        body[0], count=1)
            flat += body
        assert len(flat) == span, "block line count changed"
        for slot, text in zip(range(block_start, block_start + span), flat):
            lines[slot] = text

    if q.answer_line is not None:
        line = lines[q.answer_line]
        indent = line[: len(line) - len(line.lstrip())]
        lines[q.answer_line] = f"{indent}answer: {q.new_answer}"


def collect(doc: dict) -> list[dict]:
    """The question dicts of a parsed tutorial, in document order."""
    out: list[dict] = []
    for section in doc.get("sections") or []:
        out += section.get("check") or []
    out += (doc.get("passage") or {}).get("questions") or []
    out += doc.get("review_questions") or []
    return out


def _value_key(group: tuple[int, list[str]]) -> tuple:
    """A value's identity: its text (key letter stripped) plus wrapped lines."""
    body = list(group[1])
    match = LETTER_KEY_RE.match(body[0])
    if match:
        body[0] = body[0][match.end():]
    return tuple(body)


def _bodies(q: Question, attr: str) -> Counter:
    return Counter(_value_key(group) for group in getattr(q, attr).values())


def _text(group: tuple[int, list[str]]) -> str:
    match = VALUE_RE.match(group[1][0])
    return match.group(1) if match else ""


def _values(q: Question, attr: str) -> dict:
    """letter -> parsed value, read back from the file's own lines."""
    out: dict = {}
    for letter, (_, body) in getattr(q, attr).items():
        try:
            doc = yaml.safe_load("\n".join(body))
        except yaml.YAMLError:
            continue
        if isinstance(doc, dict):
            out.update(doc)
    return out


def verify(path: Path, before: list[Question]) -> list[str]:
    """Re-parse the rewritten file and check that nothing but letters moved.

    Compared question-by-question in document order, on both the raw line text
    (quoting and wrapping intact) and the parsed document (what the app serves).
    """
    problems: list[str] = []
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    parsed = collect(doc)
    _, after = scan(path)

    if len(parsed) != len(before) or len(after) != len(before):
        return [f"{path.name}: question count changed "
                f"{len(before)} -> {len(parsed)}/{len(after)}"]

    for i, (old, new, nq) in enumerate(zip(before, after, parsed)):
        if _bodies(new, "opt_raw") != _bodies(old, "opt_raw"):
            problems.append(f"{path.name} q{i}: option texts changed")
        if _bodies(new, "dist_raw") != _bodies(old, "dist_raw"):
            problems.append(f"{path.name} q{i}: distractor texts changed")
        if new.answer not in new.opt_raw:
            problems.append(f"{path.name} q{i}: answer {new.answer!r} not an option letter")
        elif _values(new, "opt_raw").get(new.answer) != _values(old, "opt_raw").get(old.answer):
            problems.append(f"{path.name} q{i}: key no longer sits on its own text")
        if set(new.dist_raw) - set(new.opt_raw):
            problems.append(f"{path.name} q{i}: distractor key off the option letters")
        if nq.get("answer") != new.answer:
            problems.append(f"{path.name} q{i}: parsed answer disagrees with the line")
        if _values(new, "opt_raw") != (nq.get("options") or {}):
            problems.append(f"{path.name} q{i}: parsed option texts disagree with the line")
        if _values(new, "dist_raw") != (nq.get("distractors") or {}):
            problems.append(f"{path.name} q{i}: parsed distractor texts disagree with the line")

    counts = Counter(q.answer for q in after if q.answer)
    if counts and max(counts.values()) - min(counts.values()) > 2:  # soft guard
        problems.append(f"{path.name}: unbalanced {dict(counts)}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=20260831)
    ap.add_argument("--write", action="store_true", help="apply edits (default: dry run)")
    args = ap.parse_args()

    files = sorted(TUTORIALS.glob("*/*.yml"))
    before_global: Counter[str] = Counter()
    after_global: Counter[str] = Counter()
    moved_total = kept_total = touched_files = 0
    problems: list[str] = []

    for path in files:
        lines, questions = scan(path)
        before_global.update(q.answer for q in questions if q.answer)
        rng = random.Random(f"{args.seed}:{path.relative_to(REPO)}")
        moves = plan_file(questions, rng)
        kept_total += sum(1 for q in questions if q.answer and q.new_answer is None)
        if not moves:
            continue

        for q in moves:
            relabel(lines, q)
        moved_total += len(moves)
        touched_files += 1

        if args.write:
            path.write_text("\n".join(lines), encoding="utf-8")
            problems += verify(path, questions)

        after = Counter(q.new_answer or q.answer for q in questions)
        after_global.update(after)
        if moves:
            print(f"{path.relative_to(REPO)}: moved {len(moves)}/{len(questions)} "
                  f"({' '.join(f'{l}={after[l]}' for l in LETTERS)})")

    print(f"\nseed={args.seed} files={len(files)} touched={touched_files} "
          f"moved={moved_total} left-alone={kept_total}")
    total = max(1, sum(before_global.values()))
    print("before: " + " ".join(f"{l}={before_global[l]} "
                                f"({100 * before_global[l] / total:.1f}%)" for l in LETTERS))
    if args.write:
        total = max(1, sum(after_global.values()))
        print("after:  " + " ".join(f"{l}={after_global[l]} "
                                    f"({100 * after_global[l] / total:.1f}%)" for l in LETTERS))
    else:
        print("dry run — rerun with --write to apply")
    for p in problems:
        print("VERIFY FAIL:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
