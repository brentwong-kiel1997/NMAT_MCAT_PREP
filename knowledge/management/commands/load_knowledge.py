"""Load curriculum notes, practice, and diseases into the knowledge database."""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from knowledge.models import ChapterNote, DiseaseArticle, PracticeQuestion, SubjectRef
from portal.diseases import DISEASES
from portal.notes import NOTES
from portal.practice import LABELS, PRACTICE


KIND_HINTS = {
    "verbal": "nmat",
    "inductive-reasoning": "nmat",
    "quantitative": "nmat",
    "perceptual-acuity": "nmat",
    "chem-phys": "mcat",
    "cars": "mcat",
    "bio-biochem": "mcat",
    "psych-soc": "mcat",
}


class Command(BaseCommand):
    help = "Seed / refresh the knowledge SQLite database from Python source modules."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing knowledge rows before insert.",
        )

    @transaction.atomic(using="knowledge")
    def handle(self, *args, **options):
        if options["flush"]:
            ChapterNote.objects.all().delete()
            PracticeQuestion.objects.all().delete()
            DiseaseArticle.objects.all().delete()
            SubjectRef.objects.all().delete()
            self.stdout.write("Flushed knowledge tables.")

        slugs = set(NOTES) | set(PRACTICE) | set(LABELS)
        for slug in sorted(slugs):
            label = LABELS.get(slug, {"zh": slug, "en": slug})
            kind = KIND_HINTS.get(slug, "shared")
            SubjectRef.objects.update_or_create(
                slug=slug,
                defaults={
                    "label_zh": label["zh"],
                    "label_en": label["en"],
                    "kind": kind,
                },
            )

        note_rows = 0
        for slug, chapters in NOTES.items():
            ChapterNote.objects.filter(subject_slug=slug).delete()
            for title, notes in chapters.items():
                for i, note in enumerate(notes):
                    ChapterNote.objects.create(
                        subject_slug=slug,
                        chapter_title=title,
                        sort_order=i,
                        text_zh=note["zh"],
                        text_en=note["en"],
                    )
                    note_rows += 1

        practice_rows = 0
        for slug, items in PRACTICE.items():
            PracticeQuestion.objects.filter(subject_slug=slug).delete()
            for i, item in enumerate(items):
                PracticeQuestion.objects.create(
                    subject_slug=slug,
                    qid=item["id"],
                    chapter=item.get("chapter") or "",
                    q_zh=item["q_zh"],
                    q_en=item["q_en"],
                    choices=item["choices"],
                    answer=item["answer"],
                    explain_zh=item.get("explain_zh") or "",
                    explain_en=item.get("explain_en") or "",
                    sort_order=i,
                )
                practice_rows += 1

        disease_rows = 0
        for slug, disease in DISEASES.items():
            DiseaseArticle.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": disease.get("name") or slug,
                    "name_zh": disease.get("name_zh") or "",
                    "short": disease.get("short") or "",
                    "payload": disease,
                },
            )
            disease_rows += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Knowledge DB ready: subjects={SubjectRef.objects.count()} "
                f"notes={note_rows} practice={practice_rows} diseases={disease_rows}"
            )
        )
