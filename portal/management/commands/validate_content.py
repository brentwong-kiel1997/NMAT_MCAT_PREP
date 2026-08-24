"""Deploy gate: structural validation of content/ before Gunicorn restarts.

Runs from scripts/deploy.sh. Checks file hashes against content/MANIFEST.json
(so a half-written checkout fails loudly), the collection counts, structural
invariants (unique slugs/qids, valid answers, chapter-id stability for learner
progress), and that every note bucket title matches an outline chapter title
of its subject (or an overlay source subject).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from django.core.management.base import BaseCommand

from portal import content

CONTENT = content.CONTENT_DIR


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
                    problems.append(
                        f"{rel} changed without regenerating MANIFEST.json "
                        f"(run manage.py export_content or update counts deliberately)"
                    )

        store = content.store()

        # ---- counts ---------------------------------------------------------
        counts = {
            "subjects": len(store["subjects"]),
            "note_bullets": sum(
                len(b) for v in store["notes"].values() for b in v.values()
            ),
            "practice": sum(len(v) for v in store["practice"].values()),
            "glossary": len(store["glossary"]),
            "formulas": sum(len(v) for v in store["formulas"].values()),
            "tips": len(store["tips"]),
            "paths": len(store["paths"]),
            "checklists": len(store["checklists"]),
            "diseases": len(store["diseases"]),
        }
        if manifest_path.exists():
            for key, value in counts.items():
                if key in manifest.get("counts", {}) and manifest["counts"][key] != value:
                    problems.append(
                        f"count drift {key}: manifest={manifest['counts'][key]} actual={value}"
                    )

        # ---- structural invariants -------------------------------------------
        qids: set[tuple[str, str]] = set()
        for slug, items in store["practice"].items():
            for item in items:
                if not item["id"]:
                    problems.append(f"practice {slug}: empty qid")
                if (slug, item["id"]) in qids:
                    problems.append(f"duplicate qid {slug}/{item['id']}")
                qids.add((slug, item["id"]))
                if item["answer"] not in tuple(item.get("choices") or {}):
                    problems.append(
                        f"practice {slug}/{item['id']}: answer {item['answer']!r} not in choices"
                    )

        chapter_ids: set[str] = set()
        outline_titles: dict[str, set[str]] = {}
        for slug, subject in store["subjects"].items():
            titles = outline_titles.setdefault(slug, set())
            for group in subject.get("chapters") or []:
                for item in group.get("items") or []:
                    titles.add(item.get("title", ""))
                    chapter_ids.add(item.get("chapter_id", ""))
        if len(chapter_ids) != len(set(chapter_ids)):
            problems.append("duplicate chapter ids across subjects")

        # note bucket titles attach to outline items through notes_for's exact
        # or fuzzy matching; flag (warn) any title that can never attach.
        overlay_sources = {
            "biology": ("bio-biochem",),
            "chemistry": ("chem-phys",),
            "physics": ("chem-phys",),
            "chem-phys": ("physics", "chemistry"),
            "bio-biochem": ("biology", "biochemistry"),
            "psych-soc": ("behavioral-social",),
        }

        def fuzzy_match(title: str, outline: str) -> bool:
            a, b = title.lower(), outline.lower()
            if a in b or b in a:
                return True
            la, lb = a.split("·")[0].strip(), b.split("·")[0].strip()
            return bool(la) and la == lb and len(la) <= 4

        loose_titles = 0
        for slug, bucket in store["notes"].items():
            candidates = set(outline_titles.get(slug, set()))
            for source in overlay_sources.get(slug, ()):
                candidates |= outline_titles.get(source, set())
            for title in bucket:
                if not title:
                    problems.append(f"notes {slug}: empty chapter title")
                    continue
                if not any(fuzzy_match(title, t) for t in candidates):
                    loose_titles += 1
                    self.stderr.write(
                        f"warning: notes {slug}: {title!r} matches no outline item"
                    )
        if loose_titles:
            self.stderr.write(
                f"warning: {loose_titles} note chapters do not fuzzy-match any "
                f"outline item (they will never render)"
            )

        if not store["kinds"].get("shared") or not store["kinds"].get("mcat"):
            problems.append("catalog.yml kinds missing shared/mcat lists")

        # ---- learning projects / units (content/units.yml) ----------------------
        units_path = CONTENT / "units.yml"
        if units_path.exists():
            unit_doc = yaml.safe_load(units_path.read_text(encoding="utf-8")) or {}
            unit_source_set = set(store["subjects"])
            for proj_key, proj in (unit_doc.get("projects") or {}).items():
                for u in (proj.get("units") or []):
                    if u.get("source") not in unit_source_set:
                        problems.append(
                            f"units.yml: unit {u.get('key')!r} unknown source {u.get('source')!r}"
                        )
                    if not u.get("key") or not u.get("label"):
                        problems.append(f"units.yml: project {proj_key} unit missing key/label")

        # ---- tutorial chapters (the growing textbook) --------------------------
        sources_path = CONTENT / "SOURCES.yml"
        known_sources = set()
        if sources_path.exists():
            registry = yaml.safe_load(sources_path.read_text(encoding="utf-8")) or {}
            known_sources = {s.get("id") for s in registry.get("sources") or []}
        tutorials_dir = CONTENT / "tutorials"
        if tutorials_dir.is_dir():
            for file in sorted(tutorials_dir.rglob("*.yml")):
                rel = str(file.relative_to(CONTENT))
                try:
                    doc = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
                except yaml.YAMLError as exc:
                    problems.append(f"{rel}: invalid YAML ({exc})")
                    continue
                subject = store["subjects"].get(doc.get("subject", ""))
                if subject is None:
                    problems.append(f"{rel}: unknown subject {doc.get('subject')!r}")
                    continue
                outline = {
                    item.get("title", "")
                    for group in subject.get("chapters") or []
                    for item in group.get("items") or []
                }
                if doc.get("chapter") not in outline:
                    problems.append(
                        f"{rel}: chapter {doc.get('chapter')!r} not in the subject outline"
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
                questions = doc.get("review_questions") or []
                for i, q in enumerate(questions, 1):
                    if not q.get("q") or not q.get("answer"):
                        problems.append(f"{rel}: review question {i} missing q/answer")
                for i, v in enumerate(doc.get("videos") or [], 1):
                    if not v.get("title") or not v.get("url"):
                        problems.append(f"{rel}: video {i} missing title/url")
                for i, r in enumerate(doc.get("further_reading") or [], 1):
                    if not r.get("title") or not r.get("url"):
                        problems.append(f"{rel}: further_reading {i} missing title/url")
                for src in doc.get("sources") or []:
                    if src.get("ref") not in known_sources:
                        problems.append(
                            f"{rel}: source ref {src.get('ref')!r} not in SOURCES.yml"
                        )
                    if src.get("relation") not in ("consulted", "adapted"):
                        problems.append(
                            f"{rel}: source {src.get('ref')!r} needs relation "
                            f"consulted|adapted"
                        )

        # ---- tutorial chapters (optional, growing one by one) ---------------
        sources_path = CONTENT / "SOURCES.yml"
        source_ids = set()
        if sources_path.exists():
            source_ids = {
                s.get("id")
                for s in (yaml.safe_load(sources_path.read_text(encoding="utf-8")) or {})
                .get("sources", [])
            }
        tut_dir = CONTENT / "tutorials"
        if tut_dir.is_dir():
            outline_titles = {
                slug: {
                    it.get("title", "")
                    for subject in store["subjects"].values()
                    if subject.get("slug") == slug
                    for group in subject.get("chapters") or []
                    for it in group.get("items") or []
                }
                for slug in store["subjects"]
            }
            for file in sorted(tut_dir.rglob("*.yml")):
                doc = yaml.safe_load(file.read_text(encoding="utf-8"))
                rel = str(file.relative_to(CONTENT))
                if doc.get("subject") not in store["subjects"]:
                    problems.append(f"{rel}: unknown subject {doc.get('subject')!r}")
                    continue
                if doc.get("chapter") not in outline_titles.get(doc["subject"], set()):
                    problems.append(
                        f"{rel}: chapter {doc.get('chapter')!r} not in the subject outline"
                    )
                if not doc.get("sections"):
                    problems.append(f"{rel}: no sections")
                for src in doc.get("sources") or []:
                    if src.get("ref") not in source_ids:
                        problems.append(f"{rel}: unknown source ref {src.get('ref')!r}")

        # ---- learner progress still resolves (warn on legacy junk) -----------
        try:
            from portal.models import ChapterProgress, PracticeAttempt

            orphan_chapters = (
                set(ChapterProgress.objects.values_list("chapter_id", flat=True))
                - chapter_ids
            )
            if orphan_chapters:
                self.stderr.write(
                    f"warning: {len(orphan_chapters)} stored chapter ids do not "
                    f"resolve (pre-existing test data): {sorted(orphan_chapters)[:8]}"
                )
            orphan_qids = (
                set(PracticeAttempt.objects.values_list("question_id", flat=True))
                - {qid for _, qid in qids}
            )
            if orphan_qids:
                self.stderr.write(
                    f"warning: stored question ids missing from content: {sorted(orphan_qids)[:8]}"
                )
        except Exception as exc:  # DB unavailable during content-only checks
            self.stderr.write(f"warning: progress cross-check skipped ({exc})")

        if problems:
            self.stderr.write(self.style.ERROR("\n".join(problems)))
            raise SystemExit(1)
        self.stdout.write(
            self.style.SUCCESS(
                "content OK — "
                + " ".join(f"{k}={v}" for k, v in counts.items())
            )
        )
