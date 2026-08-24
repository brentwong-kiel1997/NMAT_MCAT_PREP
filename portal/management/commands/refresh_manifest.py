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
        from portal.management.commands.validate_content import current_counts

        counts = current_counts(store)
        manifest = {
            "source_rev": rev,
            "counts": counts,
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
