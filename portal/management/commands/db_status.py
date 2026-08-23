"""Show that user and knowledge SQLite databases stay separated."""

from __future__ import annotations

import sqlite3

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Print user DB vs knowledge DB paths, tables, and separation checks."

    def handle(self, *args, **options):
        user_path = settings.DATABASES["default"]["NAME"]
        know_path = settings.DATABASES["knowledge"]["NAME"]
        self.stdout.write(f"user_db      = {user_path}")
        self.stdout.write(f"knowledge_db = {know_path}")

        if str(user_path) == str(know_path):
            self.stderr.write(self.style.ERROR("SEPARATION BROKEN: both aliases point to the same file"))
            raise SystemExit(1)

        user_tables = self._tables(user_path)
        know_tables = self._tables(know_path)
        self.stdout.write("user tables: " + (", ".join(user_tables) or "(none)"))
        self.stdout.write("knowledge tables: " + (", ".join(know_tables) or "(none)"))

        leaks_k = [t for t in user_tables if t.startswith("knowledge_")]
        leaks_u = [
            t
            for t in know_tables
            if t.startswith(("portal_", "auth_", "django_session", "django_admin", "django_content"))
        ]
        if leaks_k or leaks_u:
            self.stderr.write(self.style.ERROR(f"SEPARATION BROKEN: {leaks_k=} {leaks_u=}"))
            raise SystemExit(1)

        self.stdout.write(self.style.SUCCESS("OK — user DB and knowledge DB are separated"))

    def _tables(self, path) -> list[str]:
        con = sqlite3.connect(str(path))
        return [
            r[0]
            for r in con.execute(
                "select name from sqlite_master where type='table' order by 1"
            )
        ]
