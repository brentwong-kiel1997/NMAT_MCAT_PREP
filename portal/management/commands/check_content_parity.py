"""Parity gate: compare portal.content (content/ YAML) with the live loaders.

Every collection the site renders is compared row-for-row, in order, between
the current DB-backed loaders (portal.notes/exams/materials/practice/diseases)
and the content/ reader. Also re-derives every chapter_id and checks it against
the ChapterProgress rows in the user DB, so learner progress can never orphan.

Exit 0 = identical; exit 1 prints a per-collection diff.
"""

from __future__ import annotations

import json

from django.core.management.base import BaseCommand
from django.db.models import Q

from portal import content, diseases, exams, materials, notes, practice


def ser(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)


class Command(BaseCommand):
    help = "Compare content/ reader output against the live knowledge DB loaders."

    def handle(self, *args, **options):
        failures: list[str] = []
        checked = 0

        def cmp(name, expected, actual):
            nonlocal checked
            checked += 1
            if ser(expected) != ser(actual):
                failures.append(name)
                self.stderr.write(f"MISMATCH {name}")
                import difflib

                e, a = ser(expected), ser(actual)
                # align on a stable token split so the diff is readable
                hint = difflib.unified_diff(
                    e.split(","), a.split(","), "db", "yaml", n=0, lineterm=""
                )
                for line in list(hint)[:12]:
                    self.stderr.write(f"  {line.strip()[:240]}")

        # ---- subjects ------------------------------------------------------
        for slug in ("biology", "chemistry", "physics", "behavioral-social", "biochemistry"):
            cmp(f"get_shared({slug})", exams.get_shared(slug), content.get_subject(slug))
        for slug in ("verbal", "inductive-reasoning", "quantitative", "perceptual-acuity"):
            cmp(f"get_nmat_unique({slug})", exams.get_nmat_unique(slug), content.get_subject(slug))
        for slug in ("chem-phys", "cars", "bio-biochem", "psych-soc"):
            cmp(f"get_mcat_section({slug})", exams.get_mcat_section(slug), content.get_subject(slug))
        cmp("get_shared(unknown)", exams.get_shared("nope"), content.get_subject("nope"))

        cmp("shared_list", exams.shared_list(), content.shared_list())
        cmp("nmat_unique_subjects", exams.nmat_unique_subjects(), content.nmat_unique_subjects())
        cmp("nmat_exam", exams.nmat_exam(), content.nmat_exam())
        cmp("mcat_exam", exams.mcat_exam(), content.mcat_exam())

        # ---- notes ----------------------------------------------------------
        from knowledge.models import ChapterNote, CurriculumSubject

        buckets = set(
            ChapterNote.objects.values_list("subject_slug", "chapter_title")
        )
        for slug, title in sorted(buckets):
            cmp(
                f"notes_for({slug}, {title!r})",
                notes.notes_for(slug, title),
                content.notes_for(slug, title),
            )
        outline_titles = {
            (row.payload.get("slug") or row.slug, item.get("title", ""))
            for row in CurriculumSubject.objects.all()
            for group in row.payload.get("chapters") or []
            for item in group.get("items") or []
        }
        for slug, title in sorted(outline_titles):
            cmp(
                f"notes_for~outline({slug}, {title!r})",
                notes.notes_for(slug, title),
                content.notes_for(slug, title),
            )
        for slug in sorted({s for s, _ in buckets}):
            cmp(
                f"flashcards_for({slug})",
                notes.flashcards_for(slug, 60),
                content.flashcards_for(slug, 60),
            )

        # ---- practice --------------------------------------------------------
        from knowledge.models import PracticeQuestion

        for slug in sorted(
            PracticeQuestion.objects.values_list("subject_slug", flat=True).distinct()
        ):
            cmp(f"practice_for({slug})", practice.practice_for(slug), content.practice_for(slug))
        cmp("all_practice_slugs", practice.all_practice_slugs(), content.all_practice_slugs())
        cmp("practice_catalog", practice.practice_catalog(), content.practice_catalog())

        # ---- materials ---------------------------------------------------------
        from knowledge.models import GlossaryTerm

        def db_glossary(q: str = "", subject: str = "") -> list:
            qs = GlossaryTerm.objects.all()
            if q:
                qs = qs.filter(
                    Q(term__icontains=q)
                    | Q(term_zh__icontains=q)
                    | Q(def_zh__icontains=q)
                    | Q(def_en__icontains=q)
                )
            rows = [
                {
                    "term": r.term,
                    "term_zh": r.term_zh,
                    "def_zh": r.def_zh,
                    "def_en": r.def_en,
                    "subjects": list(r.subjects or []),
                }
                for r in qs
            ]
            if subject:
                rows = [r for r in rows if subject in r["subjects"]]
            return rows

        for q in ("", "acid", "ATP", "atp", "比例", "Km"):
            for subject in ("", "biology", "biochemistry"):
                cmp(
                    f"glossary(q={q!r}, subject={subject!r})",
                    db_glossary(q, subject),
                    content.glossary_terms(q, subject),
                )
        cmp(
            "glossary_subject_slugs",
            materials.glossary_subject_slugs(),
            content.glossary_subject_slugs(),
        )
        for slug in ("biology", "chemistry", "physics", "biochemistry", "chem-phys",
                     "bio-biochem", "quantitative", "verbal", "cars"):
            cmp(f"formulas_for({slug})", materials.formulas_for(slug), content.formulas_for(slug))
        cmp("formula_catalog", materials.formula_catalog(), content.formula_catalog())

        from knowledge.models import ExamTip, StudyPath

        def db_tips(exam: str = "") -> list:
            qs = ExamTip.objects.all()
            if exam:
                qs = qs.filter(exam__iexact=exam)
            return [
                {
                    "exam": t.exam,
                    "title_zh": t.title_zh,
                    "title_en": t.title_en,
                    "body_zh": t.body_zh,
                    "body_en": t.body_en,
                }
                for t in qs
            ]

        for exam in ("", "NMAT", "MCAT", "BOTH", "nmat"):
            cmp(f"exam_tips({exam!r})", db_tips(exam), content.exam_tips(exam))

        db_paths = [
            {
                "id": p.path_id,
                "title_zh": p.title_zh,
                "title_en": p.title_en,
                "blurb_zh": p.blurb_zh,
                "blurb_en": p.blurb_en,
                "steps": list(p.steps or []),
            }
            for p in StudyPath.objects.all().order_by("sort_order", "id")
        ]
        cmp("study_paths", db_paths, content.study_paths())
        for exam in ("", "NMAT", "MCAT", "BOTH"):
            cmp(f"exam_checklists({exam!r})", materials.exam_checklists(exam), content.exam_checklists(exam))

        # ---- diseases ------------------------------------------------------------
        cmp("all_diseases", diseases.all_diseases(), content.all_diseases())
        for slug in ("tuberculosis", "dengue", "pneumonia", "asthma", "hypertension",
                     "myocardial-infarction", "type-2-diabetes", "acute-kidney-injury"):
            cmp(f"get_disease({slug})", diseases.get_disease(slug), content.get_disease(slug))
        cmp("get_disease(unknown)", diseases.get_disease("nope"), content.get_disease("nope"))

        # ---- chapter ids: reader must resolve at least what the old loader did ----
        from portal.models import ChapterProgress

        def ids_of(subjects: list[dict]) -> set[str]:
            out: set[str] = set()
            for subject in subjects:
                for group in subject.get("chapters") or []:
                    for item in group.get("items") or []:
                        out.add(item.get("chapter_id", ""))
            return out

        old_ids = ids_of(
            exams.shared_list()
            + exams.nmat_unique_subjects()
            + exams.mcat_exam()["sections"]
        )
        new_ids = ids_of(content.subjects())
        stored = set(ChapterProgress.objects.values_list("chapter_id", flat=True))
        # ids the old site could resolve but the new reader cannot = regression
        regression = (stored & old_ids) - new_ids
        # pre-existing junk (never resolved before either) is reported separately
        junk = stored - old_ids - new_ids
        checked += 1
        if regression:
            failures.append("chapter_ids")
            self.stderr.write(f"ORPHANED chapter ids (regression): {sorted(regression)}")
        if junk:
            self.stderr.write(
                f"note: {len(junk)} stored chapter ids never matched any curriculum "
                f"chapter (pre-existing test data): {sorted(junk)}"
            )

        # ---- qid stability ----------------------------------------------------------
        from portal.models import PracticeAttempt

        stored_qids = set(PracticeAttempt.objects.values_list("question_id", flat=True))
        content_qids = {q["id"] for items in content.store()["practice"].values() for q in items}
        checked += 1
        if not stored_qids <= content_qids:
            failures.append("question_ids")
            self.stderr.write(
                f"ORPHANED question ids: {sorted(stored_qids - content_qids)}"
            )

        if failures:
            self.stderr.write(self.style.ERROR(f"\n{len(failures)}/{checked} checks FAILED"))
            raise SystemExit(1)
        self.stdout.write(self.style.SUCCESS(f"parity OK — {checked} checks"))
