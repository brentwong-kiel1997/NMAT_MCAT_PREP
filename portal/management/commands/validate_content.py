"""Deploy gate: structural validation of content/ before Gunicorn restarts.

Validates the unified chapter library model:
- file hashes against MANIFEST.json (half-written checkouts fail loudly)
- one chapter per file; unique ids; non-empty exams ∈ {NMAT, MCAT}
- subject reference lists resolve; unit reference lists resolve
- practice answers are one of the choice keys; question ids unique
- tutorials key to a real chapter title and cite registered sources
- stored learner progress resolves against chapter ids (warns on legacy junk)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from django.core.management.base import BaseCommand

from portal import content

CONTENT = content.CONTENT_DIR

COLLECTION_COUNTS = ("chapters", "note_bullets", "practice", "glossary",
                     "formulas", "tips", "paths", "checklists", "diseases",
                     "exam_items", "exam_passages")


def current_counts(store: dict) -> dict:
    chapters = store["chapters"]
    return {
        "chapters": len(chapters),
        "note_bullets": sum(len(c.get("notes") or []) for c in chapters.values()),
        "practice": sum(len(c.get("practice") or []) for c in chapters.values()),
        "glossary": len(store["glossary"]),
        "formulas": sum(len(v) for v in store["formulas"].values()),
        "tips": len(store["tips"]),
        "paths": len(store["paths"]),
        "checklists": len(store["checklists"]),
        "diseases": len(store["diseases"]),
        "exam_items": sum(len(b.get("items") or []) + sum(len(p.get("items") or [])
                          for p in (b.get("passages") or []))
                          for exam in (store.get("exam_bank") or {}).get("exams", {}).values()
                          for b in exam.values()),
        "exam_passages": sum(len(b.get("passages") or [])
                             for exam in (store.get("exam_bank") or {}).get("exams", {}).values()
                             for b in exam.values()),
    }


class Command(BaseCommand):
    help = "Validate content/ files; exit 1 if anything is broken."

    def handle(self, *args, **options):
        problems: list[str] = []

        # ---- manifest hashes ------------------------------------------------
        manifest_path = CONTENT / "MANIFEST.json"
        if not manifest_path.exists():
            problems.append("content/MANIFEST.json is missing")
        else:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for rel, digest in manifest.get("files", {}).items():
                file = CONTENT / rel
                if not file.exists():
                    problems.append(f"missing content file: {rel}")
                elif hashlib.sha256(file.read_bytes()).hexdigest() != digest:
                    problems.append(f"{rel} changed without regenerating MANIFEST.json")

        store = content.store()
        chapters = store["chapters"]

        # ---- chapter library invariants --------------------------------------
        seen_qids: set[str] = set()
        for slug, ch in chapters.items():
            exams = ch.get("exams") or []
            if not exams or not set(exams) <= {"NMAT", "MCAT"}:
                problems.append(f"chapter {slug}: bad exams {exams}")
            if not ch.get("title"):
                problems.append(f"chapter {slug}: missing title")
            for q in ch.get("practice") or []:
                if not q.get("id"):
                    problems.append(f"chapter {slug}: practice item without id")
                elif q["id"] in seen_qids:
                    problems.append(f"duplicate question id {q['id']}")
                else:
                    seen_qids.add(q["id"])
                if q.get("answer") not in (q.get("choices") or {}):
                    problems.append(
                        f"practice {q.get('id')}: answer {q.get('answer')!r} not in choices"
                    )

        # ---- subject & unit reference lists ----------------------------------
        for slug, subject in store["subjects"].items():
            for group in subject.get("chapters") or []:
                for ref in group.get("chapters") or []:
                    if ref not in chapters:
                        problems.append(f"subject {slug}: unknown chapter ref {ref!r}")
        units_path = CONTENT / "units.yml"
        if units_path.exists():
            unit_doc = yaml.safe_load(units_path.read_text(encoding="utf-8")) or {}
            unit_keys = set()
            for proj_key, proj in (unit_doc.get("projects") or {}).items():
                for u in (proj.get("units") or []):
                    unit_keys.add(u.get("key"))
                    if u.get("source") not in store["subjects"]:
                        problems.append(
                            f"units.yml: unit {u.get('key')!r} unknown source {u.get('source')!r}"
                        )
                    for ref in u.get("chapters") or []:
                        if ref not in chapters:
                            problems.append(
                                f"units.yml: unit {u.get('key')!r} unknown chapter ref {ref!r}"
                            )
        else:
            problems.append("content/units.yml is missing")

        # ---- counts ------------------------------------------------------------
        counts = current_counts(store)
        if manifest_path.exists():
            for key in COLLECTION_COUNTS:
                if key in manifest.get("counts", {}) and manifest["counts"][key] != counts[key]:
                    problems.append(
                        f"count drift {key}: manifest={manifest['counts'][key]} actual={counts[key]}"
                    )

        # ---- exam bank -----------------------------------------------------------
        exam_problems = _validate_exam_bank(store, seen_qids)
        problems.extend(exam_problems)

        # ---- tutorials -----------------------------------------------------------
        sources_path = CONTENT / "SOURCES.yml"
        known_sources = set()
        if sources_path.exists():
            registry = yaml.safe_load(sources_path.read_text(encoding="utf-8")) or {}
            known_sources = {s.get("id") for s in registry.get("sources") or []}
        titles = {c.get("title", "") for c in chapters.values()}
        tutorials_dir = CONTENT / "tutorials"
        if tutorials_dir.is_dir():
            for file in sorted(tutorials_dir.rglob("*.yml")):
                rel = str(file.relative_to(CONTENT))
                try:
                    doc = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
                except yaml.YAMLError as exc:
                    problems.append(f"{rel}: invalid YAML ({exc})")
                    continue
                if doc.get("subject") not in store["subjects"]:
                    problems.append(f"{rel}: unknown subject {doc.get('subject')!r}")
                    continue
                if doc.get("chapter") not in titles:
                    problems.append(
                        f"{rel}: chapter {doc.get('chapter')!r} not a library chapter title"
                    )
                if not doc.get("sections"):
                    problems.append(f"{rel}: no sections")
                for section in doc.get("sections") or []:
                    if not section.get("heading") or not section.get("body"):
                        problems.append(f"{rel}: section missing heading/body")
                    for check in section.get("check") or []:
                        if not check.get("q") or not check.get("answer"):
                            problems.append(f"{rel}: section check missing q/answer")
                    for i, v in enumerate(section.get("videos") or [], 1):
                        if not v.get("title") or not v.get("url"):
                            problems.append(f"{rel}: section {i} video missing title/url")
                if not doc.get("sources"):
                    problems.append(f"{rel}: no sources block")
                for src in doc.get("sources") or []:
                    if src.get("ref") not in known_sources:
                        problems.append(f"{rel}: unknown source ref {src.get('ref')!r}")
                for i, v in enumerate(doc.get("videos") or [], 1):
                    if not v.get("title") or not v.get("url"):
                        problems.append(f"{rel}: video {i} missing title/url")
                for i, r in enumerate(doc.get("further_reading") or [], 1):
                    if not r.get("title") or not r.get("url"):
                        problems.append(f"{rel}: further_reading {i} missing title/url")
                for mn in doc.get("mnemonics") or []:
                    if not mn.get("phrase"):
                        problems.append(f"{rel}: mnemonic missing phrase")
                for mp in doc.get("maps") or []:
                    if not mp.get("title") or not mp.get("steps"):
                        problems.append(f"{rel}: map missing title/steps")
                passage = doc.get("passage")
                if passage is not None:
                    if not passage.get("text"):
                        problems.append(f"{rel}: passage missing text")
                    for q in passage.get("questions") or []:
                        if not q.get("q") or not q.get("answer"):
                            problems.append(f"{rel}: passage question missing q/answer")
                for i, q in enumerate(doc.get("review_questions") or [], 1):
                    if not q.get("q") or not q.get("answer"):
                        problems.append(f"{rel}: review question {i} missing q/answer")

        # ---- learner progress vs chapter ids --------------------------------------
        try:
            from portal.models import ChapterProgress, PracticeAttempt

            orphan = (
                set(ChapterProgress.objects.values_list("chapter_id", flat=True))
                - set(chapters)
            )
            if orphan:
                self.stderr.write(
                    f"warning: {len(orphan)} stored chapter ids do not resolve "
                    f"(legacy/test rows): {sorted(orphan)[:8]}"
                )
            orphan_q = (
                set(PracticeAttempt.objects.values_list("question_id", flat=True))
                - seen_qids
            )
            if orphan_q:
                self.stderr.write(
                    f"warning: stored question ids missing from content: {sorted(orphan_q)[:8]}"
                )
        except Exception as exc:
            self.stderr.write(f"warning: progress cross-check skipped ({exc})")

        if problems:
            self.stderr.write(self.style.ERROR("\n".join(problems)))
            raise SystemExit(1)
        self.stdout.write(
            self.style.SUCCESS(
                "content OK — " + " ".join(f"{k}={v}" for k, v in counts.items())
            )
        )


def _parse_duration_minutes(text: str) -> int | None:
    """Parse '2 hours 15 minutes' / '95 minutes' / '~35 minutes (...)' -> minutes."""
    import re
    if not text:
        return None
    total = 0
    for value, unit in re.findall(r"(\d+)\s*(hours?|hrs?|h|minutes?|mins?|m)\b", text.lower()):
        n = int(value)
        total += n * 60 if unit.startswith(("hour", "hr", "h")) else n
    return total or None


def _validate_exam_bank(store: dict, seen_qids: set[str]) -> list[str]:
    problems: list[str] = []
    bank = (store.get("exam_bank") or {}).get("exams") or {}
    for err in (store.get("exam_bank") or {}).get("errors") or []:
        problems.append(f"exam-bank parse error: {err}")
    exam_defs = store.get("exam_defs") or {}
    chapters = store.get("chapters") or {}

    for exam_id, sections in sorted(bank.items()):
        bp = ((exam_defs.get(exam_id) or {}).get("blueprint") or {})
        blocks = bp.get("blocks") or []
        declared_banks = [sid for b in blocks for sid in (b.get("bank") or [])]
        seen_section_items: dict[str, int] = {}

        for section_id, doc in sorted(sections.items()):
            # identity
            # the loader groups by doc["exam"], so a file lying about its exam
            # silently overwrites — compare against the DIRECTORY instead
            if doc.get("exam") != exam_id:
                problems.append(f"exam-bank {section_id}: exam {doc.get('exam')!r} != directory exam {exam_id!r}")
            is_drill = bool(doc.get("_drill"))
            if doc.get("section") != section_id:
                problems.append(f"exam-bank {section_id}: section key mismatch")
            if not is_drill and section_id not in declared_banks:
                problems.append(f"exam-bank {section_id}: not listed in any {exam_id} blueprint block")

            raw_items = list(doc.get("items") or [])
            for passage in doc.get("passages") or []:
                if not (passage.get("text") or "").strip():
                    problems.append(f"exam-bank {section_id} passage {passage.get('id')}: empty text")
                raw_items.extend(passage.get("items") or [])

            expected = doc.get("items_expected")
            if not is_drill and expected is not None and len(raw_items) != expected:
                problems.append(f"exam-bank {section_id}: {len(raw_items)} items, expected {expected}")
            if is_drill:
                seen_section_items[section_id] = 0  # never counts toward blueprint totals
            else:
                seen_section_items[section_id] = len(raw_items)

            letters_count = {"A": 0, "B": 0, "C": 0, "D": 0}
            stems: dict[str, str] = {}
            for item in raw_items:
                iid = item.get("id")
                if not iid:
                    problems.append(f"exam-bank {section_id}: item without id")
                elif iid in seen_qids:
                    problems.append(f"exam-bank duplicate item id {iid}")
                else:
                    seen_qids.add(iid)
                choices = item.get("choices") or {}
                if set(choices.keys()) != {"A", "B", "C", "D"}:
                    problems.append(f"exam-bank {iid}: choices keys {sorted(choices)} != A-D")
                if item.get("answer") not in choices:
                    problems.append(f"exam-bank {iid}: answer {item.get('answer')!r} not in choices")
                elif isinstance(item.get("answer"), str):
                    letters_count[item["answer"]] = letters_count.get(item["answer"], 0) + 1
                if not (item.get("q") or "").strip():
                    problems.append(f"exam-bank {iid}: empty stem")
                if not (item.get("explain") or "").strip():
                    problems.append(f"exam-bank {iid}: missing explain")
                distractors = item.get("distractors") or {}
                bad_keys = set(distractors) - set(choices)
                if bad_keys:
                    problems.append(f"exam-bank {iid}: distractor keys {sorted(bad_keys)} not option letters")
                if item.get("answer") and item["answer"] in distractors:
                    problems.append(f"exam-bank {iid}: distractor entry on the answer letter "
                                    f"(misalignment guard)")
                chapter_id = item.get("chapter")
                if not chapter_id:
                    problems.append(f"exam-bank {iid}: missing chapter back-link")
                elif chapter_id not in chapters:
                    problems.append(f"exam-bank {iid}: unknown chapter {chapter_id!r}")
                else:
                    tut = content.tutorial_for(chapters[chapter_id].get("discipline", ""),
                                               chapters[chapter_id].get("title", ""))
                    if not tut:
                        problems.append(f"exam-bank {iid}: chapter {chapter_id} has no tutorial to link")
                stem = (item.get("q") or "").strip()
                if stem and stems.get(stem) and stems[stem] != iid:
                    problems.append(f"exam-bank: duplicate stem {stem[:40]!r} ({stems[stem]} / {iid})")
                stems[stem] = iid

            # soft warning: answer-letter balance
            total_letters = sum(letters_count.values())
            if total_letters >= 8:
                for letter, n in letters_count.items():
                    if n / total_letters > 0.4:
                        problems.append(f"exam-bank {section_id}: WARNING answer '{letter}' on "
                                        f"{n}/{total_letters} items (unbalanced key)")

        # blueprint coverage: block item totals
        for b in blocks:
            got = sum(seen_section_items.get(sid, 0) for sid in (b.get("bank") or []))
            want = b.get("items")
            if want and got != want:
                problems.append(f"exam-bank {exam_id} block {b.get('id')}: {got} items banked, "
                                f"blueprint expects {want}")

    # blueprint seconds vs prose time (NMAT parts / MCAT subjects)
    def _check_seconds(exam_id: str, prose_minutes: int | None, block_seconds: int | None, label: str):
        if prose_minutes and block_seconds and prose_minutes * 60 != block_seconds:
            problems.append(f"exam {exam_id} {label}: blueprint {block_seconds}s vs prose "
                            f"{prose_minutes}min mismatch")

    nmat = exam_defs.get("nmat") or {}
    bp = (nmat.get("blueprint") or {}).get("blocks") or []
    prose = {}
    for part in nmat.get("parts") or []:
        prose[part.get("id")] = _parse_duration_minutes(part.get("time") or "")
    for b in bp:
        _check_seconds("nmat", prose.get(b.get("id")), b.get("seconds"), b.get("id"))

    mcat = exam_defs.get("mcat") or {}
    subj = store.get("subjects") or {}
    for b in (mcat.get("blueprint") or {}).get("blocks") or []:
        s = subj.get(b.get("id")) or {}
        _check_seconds("mcat", _parse_duration_minutes(s.get("time") or ""),
                       b.get("seconds"), b.get("id"))
        if s.get("questions") and b.get("items") and s["questions"] != b["items"]:
            problems.append(f"exam mcat {b.get('id')}: blueprint items {b['items']} vs subject "
                            f"questions {s['questions']}")
    return problems
