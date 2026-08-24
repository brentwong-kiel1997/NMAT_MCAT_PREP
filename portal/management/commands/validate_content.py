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
                     "formulas", "tips", "paths", "checklists", "diseases")


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
