"""Crawl every public page and write normalized HTML for before/after diffs.

Run against COPIES of both databases so nothing writes into live data:

    GABAY_USER_DB=/tmp/crawl/users.sqlite3 \
    GABAY_KNOWLEDGE_DB=/tmp/crawl/knowledge.sqlite3 \
    python manage.py crawl_pages --out /tmp/crawl/before --login

Then re-run with --out /tmp/crawl/after and `diff -r` the two directories:
content is static, so every file should be byte-identical after a migration.
"""

from __future__ import annotations

import json
import re

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.test import Client

from portal import content

SHARED = ("biology", "chemistry", "physics", "behavioral-social", "biochemistry")
NMAT = ("verbal", "inductive-reasoning", "quantitative", "perceptual-acuity")
MCAT = ("chem-phys", "cars", "bio-biochem", "psych-soc")
PRACTICE_SLUGS = tuple(content.all_practice_slugs())
FORMULA_SLUGS = tuple(s["slug"] for s in content.formula_catalog())
DISEASE_SLUGS = ("tuberculosis", "dengue", "pneumonia", "asthma", "hypertension",
                 "myocardial-infarction", "type-2-diabetes", "acute-kidney-injury")


def urls() -> list[str]:
    out = [
        "/",
        "/study/",
        "/materials/",
        "/materials/glossary/",
        "/materials/glossary/?q=acid",
        "/materials/glossary/?q=ATP",
        "/materials/glossary/?q=%E6%AF%94%E4%BE%8B",  # 比例
        "/materials/glossary/?subject=biology",
        "/materials/glossary/?q=acid&subject=biochemistry",
        "/materials/tips/",
        "/materials/tips/?exam=NMAT",
        "/materials/tips/?exam=MCAT",
        "/materials/tips/?exam=BOTH",
        "/materials/checklists/",
        "/materials/checklists/?exam=NMAT",
        "/materials/checklists/?exam=MCAT",
        "/practice/",
        "/subjects/",
        "/nmat/",
        "/mcat/",
        "/diseases/",
        "/login/",
        "/nope/",
    ]
    for slug in SHARED:
        out.append(f"/subjects/{slug}/")
    for slug in NMAT:
        out.append(f"/nmat/{slug}/")
    out.append("/nmat/biology/")     # shared-link redirect
    out.append("/nmat/social-science/")
    for slug in MCAT:
        out.append(f"/mcat/{slug}/")
    for slug in PRACTICE_SLUGS:
        out.append(f"/practice/{slug}/")
    for slug in FORMULA_SLUGS:
        out.append(f"/materials/formulas/{slug}/")
    for slug in DISEASE_SLUGS:
        out.append(f"/diseases/{slug}/")
    return out


CSRF = re.compile(r"name=[\"']csrfmiddlewaretoken[\"'] value=[\"'][^\"']+[\"']")
TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}T[\d:.+\-]+")


def normalize(body: str) -> str:
    body = CSRF.sub('name="csrfmiddlewaretoken" value="X"', body)
    body = TIMESTAMP.sub("TIMESTAMP", body)
    return "\n".join(line.rstrip() for line in body.splitlines()) + "\n"


class Command(BaseCommand):
    help = "Crawl all pages into normalized files under --out for diffing."

    def add_arguments(self, parser):
        parser.add_argument("--out", required=True)
        parser.add_argument("--login", action="store_true",
                            help="also crawl pages that need a staff session")

    def handle(self, *args, **options):
        from pathlib import Path

        out = Path(options["out"])
        out.mkdir(parents=True, exist_ok=True)
        client = Client()

        if options["login"]:
            User = get_user_model()
            user, _ = User.objects.get_or_create(
                username="crawl-bot", defaults={"is_staff": True, "is_superuser": True}
            )
            user.is_staff = True
            user.save()
            client.force_login(user)

        failures = []
        for url in urls():
            resp = client.get(url)
            name = url.strip("/").replace("/", "_").replace("?", "-") or "home"
            (out / f"{name}.html").write_text(
                f"STATUS {resp.status_code}\n" + normalize(resp.content.decode("utf-8")),
                encoding="utf-8",
            )
            if options["login"] and resp.status_code >= 500:
                failures.append(f"{url} → {resp.status_code}")
            elif not options["login"] and resp.status_code >= 400 and resp.status_code != 404:
                failures.append(f"{url} → {resp.status_code}")

        if options["login"]:
            # exercise the study API with a quiz request (no external tutor call
            # in quiz mode; pins loader behavior through build_curriculum_context)
            resp = client.post(
                "/api/study/",
                data=json.dumps({"mode": "quiz", "subject_slug": "biology"}),
                content_type="application/json",
            )
            (out / "api_study.html").write_text(
                f"STATUS {resp.status_code}\n" + normalize(resp.content.decode("utf-8")),
                encoding="utf-8",
            )
            if resp.status_code >= 400:
                failures.append(f"/api/study/ → {resp.status_code}")

        if failures:
            self.stderr.write(self.style.ERROR("\n".join(failures)))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS(f"crawled {len(list(out.glob('*.html')))} pages → {out}"))
