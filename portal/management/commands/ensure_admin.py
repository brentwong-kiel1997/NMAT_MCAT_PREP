"""Ensure a Django staff admin exists in the user database."""

from __future__ import annotations

import os
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from portal.learners import ensure_profile_for_user


def _read_access_password() -> str:
    env = os.environ.get("GABAY_ADMIN_PASSWORD", "").strip()
    if env:
        return env
    access = Path("/home/ubuntu/runtime/django-wsgi/ACCESS.txt")
    if access.exists():
        for line in access.read_text(encoding="utf-8").splitlines():
            if line.lower().startswith("password:"):
                return line.split(":", 1)[1].strip()
    pwd_file = Path("/home/ubuntu/runtime/django-wsgi/auth/password.txt")
    if pwd_file.exists():
        return pwd_file.read_text(encoding="utf-8").strip()
    return ""


class Command(BaseCommand):
    help = "Create/update the Gabay admin user in users.sqlite3"

    def add_arguments(self, parser):
        parser.add_argument("--username", default=os.environ.get("GABAY_ADMIN_USER", "admin"))
        parser.add_argument(
            "--password",
            default="",
            help="Override password (default: GABAY_ADMIN_PASSWORD or ACCESS.txt)",
        )

    def handle(self, *args, **options):
        username = options["username"] or "admin"
        password = options["password"] or _read_access_password()
        if not password:
            self.stderr.write("No admin password found; skip ensure_admin.")
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"is_staff": True, "is_superuser": True, "is_active": True},
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        # Only (re)set the password when it doesn't match: an admin who changed
        # their password in the UI must not be silently reverted on next deploy.
        if created or not user.check_password(password):
            user.set_password(password)
            user.save()
            action = "created" if created else "password reset"
        else:
            user.save()
            action = "already up to date"
        ensure_profile_for_user(user, display_name="Admin")
        self.stdout.write(self.style.SUCCESS(f"Admin user {action}: {username}"))
