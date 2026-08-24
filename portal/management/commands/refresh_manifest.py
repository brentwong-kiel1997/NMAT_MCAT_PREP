"""Regenerate content/MANIFEST.json after editing content files.

Run this after any content change and commit it together with the edited
files — validate_content (the deploy gate) compares against the manifest.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from django.core.management.base import BaseCommand

from portal import content

CONTENT = content.CONTENT_DIR


class Command(BaseCommand):
    help = "Recompute content/MANIFEST.json counts and file hashes."

    def handle(self, *args, **options):
        content._cache = None
        content._cache_stamp = None
        store = content.store()
        rev = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=CONTENT.parent,
        ).stdout.strip() or "unknown"
        manifest = {
            "source_rev": rev,
            "counts": {
                "subjects": len(store["subjects"]),
                "note_buckets": sum(len(v) for v in store["notes"].values()),
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
            },
            "files": {
                str(p.relative_to(CONTENT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(CONTENT.rglob("*.yml"))
            },
        }
        (CONTENT / "MANIFEST.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        self.stdout.write(self.style.SUCCESS(f"manifest refreshed at {CONTENT}"))
        for key, count in manifest["counts"].items():
            self.stdout.write(f"  {key}: {count}")
