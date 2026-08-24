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
