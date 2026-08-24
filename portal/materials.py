"""Textbook companion materials (glossary, formulas, tips, paths, checklists)."""

from __future__ import annotations

from knowledge.models import ExamTip, FormulaEntry, GlossaryTerm, StudyPath
from portal.materials_data import CHECKLISTS, EXAM_TIPS, FORMULAS, GLOSSARY, STUDY_PATHS
from portal.practice import LABELS


def glossary_terms(q: str = "", subject: str = "") -> list:
    try:
        from django.db.models import Q

        qs = GlossaryTerm.objects.all()
        if q:
            qs = qs.filter(
                Q(term__icontains=q)
                | Q(term_zh__icontains=q)
                | Q(def_zh__icontains=q)
                | Q(def_en__icontains=q)
            )
        rows = list(qs)
        if rows or GlossaryTerm.objects.exists():
            if subject:
                return [r for r in rows if subject in (r.subjects or [])]
            return rows
    except Exception:
        pass
    rows = GLOSSARY
    if q:
        ql = q.lower()
        rows = [
            g
            for g in rows
            if ql in g["term"].lower()
            or ql in (g.get("term_zh") or "").lower()
            or ql in g["def_zh"].lower()
            or ql in g["def_en"].lower()
        ]
    if subject:
        rows = [g for g in rows if subject in (g.get("subjects") or [])]
    return rows


def glossary_subject_slugs() -> list[str]:
    slugs: set[str] = set()
    for g in glossary_terms():
        subjects = getattr(g, "subjects", None)
        if subjects is None and isinstance(g, dict):
            subjects = g.get("subjects") or []
        for s in subjects or []:
            slugs.add(s)
    return sorted(slugs)


def formulas_for(slug: str) -> list:
    try:
        rows = list(FormulaEntry.objects.filter(subject_slug=slug))
        if rows:
            return [
                {
                    "title_zh": r.title_zh,
                    "title_en": r.title_en,
                    "formula": r.formula,
                    "note_zh": r.note_zh,
                    "note_en": r.note_en,
                }
                for r in rows
            ]
    except Exception:
        pass
    return list(FORMULAS.get(slug) or [])


def formula_catalog() -> list[dict]:
    out = []
    for slug in FORMULAS:
        label = LABELS.get(slug, {"zh": slug, "en": slug})
        out.append(
            {
                "slug": slug,
                "label_zh": label["zh"],
                "label_en": label["en"],
                "count": len(formulas_for(slug)),
            }
        )
    return out


def exam_tips(exam: str = "") -> list:
    try:
        qs = ExamTip.objects.all()
        if exam:
            qs = qs.filter(exam__iexact=exam)
        rows = list(qs)
        if rows or ExamTip.objects.exists():
            return rows
    except Exception:
        pass
    if not exam:
        return EXAM_TIPS
    el = exam.upper()
    return [t for t in EXAM_TIPS if t["exam"].upper() == el]


def study_paths() -> list:
    try:
        rows = list(StudyPath.objects.all())
        if rows:
            return rows
    except Exception:
        pass
    return STUDY_PATHS


def exam_checklists(exam: str = "") -> list:
    if not exam:
        return CHECKLISTS
    el = exam.upper()
    return [c for c in CHECKLISTS if c["exam"].upper() == el or c["exam"].upper() == "BOTH"]
