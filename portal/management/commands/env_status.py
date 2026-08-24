"""Show which .env file supplies the MiniMax study-tutor keys."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from portal.envfile import env_files, env_source, env_value

KEYS = ("MINIMAX_API_KEY", "MINIMAX_BASE_URL", "MINIMAX_MODEL")


def _mask(value: str) -> str:
    if not value:
        return "(missing)"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}…{value[-4:]}"


class Command(BaseCommand):
    help = "Print .env lookup paths and whether tutor keys resolve (values masked)."

    def handle(self, *args, **options):
        self.stdout.write("env file lookup order:")
        for path in env_files():
            mark = "found" if path.exists() else "missing"
            self.stdout.write(f"  [{mark}] {path}")

        missing = []
        for key in KEYS:
            value = env_value(key)
            source = env_source(key) or "(default)"
            shown = _mask(value) if key.endswith("KEY") else (value or "(missing)")
            self.stdout.write(f"{key} = {shown}  ← {source}")
            if key == "MINIMAX_API_KEY" and not value:
                missing.append(key)

        if missing:
            self.stderr.write(
                self.style.WARNING(
                    "MINIMAX_API_KEY not found in any .env file; the study tutor stays disabled."
                )
            )
            return
        self.stdout.write(self.style.SUCCESS("OK — tutor keys load from .env"))
