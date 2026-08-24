"""Load curriculum outlines, notes, practice, diseases, and textbook materials."""

from __future__ import annotations

from copy import deepcopy

from django.core.management.base import BaseCommand
from django.db import transaction

from knowledge.models import (
    ChapterNote,
    CurriculumSubject,
    DiseaseArticle,
    ExamTip,
    FormulaEntry,
    GlossaryTerm,
    OutlineChapter,
    PracticeQuestion,
    StudyPath,
    SubjectRef,
)
from portal import exams
from portal.diseases import DISEASES
from portal.materials_data import EXAM_TIPS, FORMULAS, GLOSSARY, STUDY_PATHS
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


def _upsert_curriculum(slug: str, kind: str, subject: dict) -> None:
    payload = deepcopy(subject)
    CurriculumSubject.objects.update_or_create(
        slug=slug,
        defaults={
            "kind": kind,
            "name": subject.get("name") or subject.get("short") or slug,
            "name_zh": subject.get("name_zh") or "",
            "summary": subject.get("summary") or subject.get("focus") or "",
            "payload": payload,
        },
    )
    OutlineChapter.objects.filter(subject_slug=slug).delete()
    order = 0
    for group in subject.get("chapters") or []:
        heading = group.get("heading") or ""
        for item in group.get("items") or []:
            OutlineChapter.objects.create(
                subject_slug=slug,
                group_heading=heading,
                title=item.get("title") or "",
                sort_order=order,
                points=list(item.get("points") or []),
            )
            order += 1


class Command(BaseCommand):
    help = "Seed / refresh the knowledge SQLite database from Python curriculum sources."

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
            OutlineChapter.objects.all().delete()
            CurriculumSubject.objects.all().delete()
            SubjectRef.objects.all().delete()
            GlossaryTerm.objects.all().delete()
            FormulaEntry.objects.all().delete()
            ExamTip.objects.all().delete()
            StudyPath.objects.all().delete()
            self.stdout.write("Flushed knowledge tables.")

        for slug, subject in exams.SHARED_SUBJECTS.items():
            _upsert_curriculum(slug, "shared", subject)
            SubjectRef.objects.update_or_create(
                slug=slug,
                defaults={
                    "label_zh": subject.get("name_zh") or subject.get("name") or slug,
                    "label_en": subject.get("name") or slug,
                    "kind": "shared",
                },
            )

        for subject in exams.NMAT["parts"][0]["subjects"]:
            slug = subject["slug"]
            _upsert_curriculum(slug, "nmat", subject)
            SubjectRef.objects.update_or_create(
                slug=slug,
                defaults={
                    "label_zh": subject.get("name_zh") or subject.get("name") or slug,
                    "label_en": subject.get("name") or slug,
                    "kind": "nmat",
                },
            )

        for subject in exams.MCAT["sections"]:
            slug = subject["slug"]
            _upsert_curriculum(slug, "mcat", subject)
            SubjectRef.objects.update_or_create(
                slug=slug,
                defaults={
                    "label_zh": subject.get("name_zh") or subject.get("short") or slug,
                    "label_en": subject.get("short") or subject.get("name") or slug,
                    "kind": "mcat",
                },
            )

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

        GlossaryTerm.objects.all().delete()
        for i, g in enumerate(GLOSSARY):
            GlossaryTerm.objects.create(
                term=g["term"],
                term_zh=g.get("term_zh") or "",
                def_zh=g["def_zh"],
                def_en=g["def_en"],
                subjects=list(g.get("subjects") or []),
                sort_order=i,
            )

        FormulaEntry.objects.all().delete()
        formula_rows = 0
        for slug, items in FORMULAS.items():
            for i, f in enumerate(items):
                FormulaEntry.objects.create(
                    subject_slug=slug,
                    title_zh=f["title_zh"],
                    title_en=f["title_en"],
                    formula=f["formula"],
                    note_zh=f.get("note_zh") or "",
                    note_en=f.get("note_en") or "",
                    sort_order=i,
                )
                formula_rows += 1

        ExamTip.objects.all().delete()
        for i, tip in enumerate(EXAM_TIPS):
            ExamTip.objects.create(
                exam=tip["exam"],
                title_zh=tip["title_zh"],
                title_en=tip["title_en"],
                body_zh=tip["body_zh"],
                body_en=tip["body_en"],
                sort_order=i,
            )

        StudyPath.objects.all().delete()
        for i, path in enumerate(STUDY_PATHS):
            StudyPath.objects.create(
                path_id=path["id"],
                title_zh=path["title_zh"],
                title_en=path["title_en"],
                blurb_zh=path["blurb_zh"],
                blurb_en=path["blurb_en"],
                steps=list(path.get("steps") or []),
                sort_order=i,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Knowledge DB ready: "
                f"curriculum={CurriculumSubject.objects.count()} "
                f"outline_chapters={OutlineChapter.objects.count()} "
                f"subjects={SubjectRef.objects.count()} "
                f"notes={note_rows} practice={practice_rows} diseases={disease_rows} "
                f"glossary={GlossaryTerm.objects.count()} "
                f"formulas={formula_rows} "
                f"tips={ExamTip.objects.count()} "
                f"paths={StudyPath.objects.count()}"
            )
        )
