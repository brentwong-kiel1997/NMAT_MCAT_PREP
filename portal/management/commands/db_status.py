"""Show the user SQLite database path and tables."""

from __future__ import annotations

import sqlite3

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Print the user DB path and its tables."

    def handle(self, *args, **options):
        user_path = settings.DATABASES["default"]["NAME"]
        self.stdout.write(f"user_db = {user_path}")
        tables = self._tables(user_path)
        self.stdout.write("tables: " + (", ".join(tables) or "(none)"))
        self.stdout.write(self.style.SUCCESS("OK"))

    def _tables(self, path) -> list[str]:
        con = sqlite3.connect(str(path))
        return [
            r[0]
            for r in con.execute(
                "select name from sqlite_master where type='table' order by 1"
            )
        ]
