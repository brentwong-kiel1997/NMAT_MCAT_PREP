"""Read textbook content from the content/ YAML directory.

content/ is the single source of truth for curriculum subjects, chapter
notes, practice MCQs, glossary, formulas, tips, study paths, checklists and
disease articles. All content is English. Files are parsed on demand and
cached on an mtime+size stamp (same pattern as envfile.py), so editing a
YAML file takes effect on the next request without restarting Gunicorn.

Layout::

    content/catalog.yml              subject order, formula order, labels
    content/exams/nmat.yml           NMAT hub meta + part-2 link entries
    content/exams/mcat.yml           MCAT hub meta
    content/subjects/<slug>.yml      full subject incl. chapter outline
    content/notes/<slug>.yml         canonical chapter note buckets
    content/practice/<slug>.yml      MCQ items
    content/diseases/<slug>.yml      disease article payload
    content/materials/*.yml          glossary/formulas/tips/paths/checklists
"""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path

import yaml

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"


class ContentError(RuntimeError):
    """content/ is missing, unreadable or malformed — fail loudly."""


# --------------------------------------------------------------------------
# loading + cache
# --------------------------------------------------------------------------

_cache: dict | None = None
_cache_stamp: tuple | None = None


def _stamp() -> tuple:
    try:
        files = sorted(CONTENT_DIR.rglob("*.yml"))
    except OSError as exc:
        raise ContentError(f"cannot read {CONTENT_DIR}: {exc}") from exc
    return tuple(
        (str(p.relative_to(CONTENT_DIR)), p.stat().st_mtime_ns, p.stat().st_size)
        for p in files
    )


def _read(path: str) -> dict:
    file = CONTENT_DIR / path
    try:
        text = file.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContentError(f"cannot read {file}: {exc}") from exc
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ContentError(f"invalid YAML in {file}: {exc}") from exc
    if not isinstance(doc, dict):
        raise ContentError(f"{file} must contain a YAML mapping")
    return doc


def store() -> dict:
    """Parsed content with derived indexes, refreshed when any file changes."""
    global _cache, _cache_stamp
    stamp = _stamp()
    if _cache is None or stamp != _cache_stamp:
        try:
            _cache = _build()
        except ContentError:
            raise
        except Exception as exc:  # defensive: surface the file context
            raise ContentError(f"failed to build content store: {exc}") from exc
        _cache_stamp = stamp
    return _cache


# --------------------------------------------------------------------------
# chapter ids + note attachment (stable derivation — learner progress keys)
# --------------------------------------------------------------------------


def _chapter_id(title: str, index: int) -> str:
    raw = re.sub(r"[^a-zA-Z0-9一-鿿]+", "-", title).strip("-").lower()
    raw = raw[:48] or "ch"
    return f"ch-{index}-{raw}"


def attach_notes(subject: dict) -> dict:
    """Return subject with study_notes and chapter_id on matching items."""
    if not subject:
        return subject
    slug = subject.get("slug") or ""
    idx = 0
    for group in subject.get("chapters") or []:
        for item in group.get("items") or []:
            title = item.get("title") or ""
            idx += 1
            item["chapter_id"] = _chapter_id(title, idx)
            notes = notes_for(slug, title)
            if notes:
                item["study_notes"] = notes
    return subject


# --------------------------------------------------------------------------
# store construction
# --------------------------------------------------------------------------

# Forward overlay from the original note sources: shared subject pages pick
# up MCAT chapter notes. Canonical buckets live in content/notes/; copies are
# made here at read time. chem-phys and bio-biochem merge from the
# ALREADY-STAGED physics/chemistry/biology buckets, exactly like the
# historical import ordering.
def _overlay(base: dict) -> dict:
    staged = dict(base)
    staged["biology"] = {**base["biology"], **base.get("bio-biochem", {})}
    staged["chemistry"] = {
        **base["chemistry"],
        **{
            k: v
            for k, v in base.get("chem-phys", {}).items()
            if k.startswith("5") or k.startswith("4E")
        },
    }
    staged["physics"] = {
        **base["physics"],
        **{k: v for k, v in base.get("chem-phys", {}).items() if k.startswith("4")},
    }
    staged["chem-phys"] = {
        **staged["physics"],
        **staged["chemistry"],
        **base.get("chem-phys", {}),
    }
    staged["bio-biochem"] = {
        **staged["biology"],
        **base.get("biochemistry", {}),
        **base.get("bio-biochem", {}),
    }
    staged["psych-soc"] = {
        **base.get("behavioral-social", {}),
        **base.get("psych-soc", {}),
    }
    return staged


def _build() -> dict:
    catalog = _read("catalog.yml")
    kinds = {kind: list(slugs) for kind, slugs in (catalog.get("kinds") or {}).items()}
    labels = {
        slug: (label if isinstance(label, str) else slug)
        for slug, label in (catalog.get("labels") or {}).items()
    }

    subjects: dict[str, dict] = {}
    subject_kinds: dict[str, str] = {}
    subj_dir = CONTENT_DIR / "subjects"
    if not subj_dir.is_dir():
        raise ContentError(f"missing directory {subj_dir}")
    for file in sorted(subj_dir.glob("*.yml")):
        doc = _read(f"subjects/{file.name}")
        subjects[doc["slug"]] = doc
        subject_kinds[doc["slug"]] = doc.get("kind", "shared")

    # canonical note buckets → forward overlay
    base_notes: dict[str, dict] = {}
    notes_dir = CONTENT_DIR / "notes"
    if notes_dir.is_dir():
        for file in sorted(notes_dir.glob("*.yml")):
            doc = _read(f"notes/{file.name}")
            base_notes[doc["slug"]] = {
                ch["title"]: list(ch.get("bullets") or [])
                for ch in doc.get("chapters") or []
            }
    staged_notes = _overlay(base_notes)

    practice: dict[str, list] = {}
    prac_dir = CONTENT_DIR / "practice"
    if prac_dir.is_dir():
        for file in sorted(prac_dir.glob("*.yml")):
            doc = _read(f"practice/{file.name}")
            practice[doc["slug"]] = list(doc.get("items") or [])

    glossary = [
        {
            "term": t.get("term", ""),
            "def": t.get("def", ""),
            "subjects": list(t.get("subjects") or []),
        }
        for t in (_read("materials/glossary.yml").get("terms") or [])
    ]

    formulas: dict[str, list] = {}
    for sheet in (_read("materials/formulas.yml").get("sheets") or []):
        formulas[sheet["slug"]] = list(sheet.get("entries") or [])

    tips = list(_read("materials/tips.yml").get("tips") or [])
    paths = list(_read("materials/paths.yml").get("paths") or [])
    checklists = list(_read("materials/checklists.yml").get("checklists") or [])

    diseases: dict[str, dict] = {}
    dis_dir = CONTENT_DIR / "diseases"
    if not dis_dir.is_dir():
        raise ContentError(f"missing directory {dis_dir}")
    for file in sorted(dis_dir.glob("*.yml")):
        doc = _read(f"diseases/{file.name}")
        diseases[doc["slug"]] = doc

    # tutorial chapters: subject → chapter title → doc (the growing textbook)
    tutorials: dict[str, dict[str, dict]] = {}
    tut_dir = CONTENT_DIR / "tutorials"
    if tut_dir.is_dir():
        for file in sorted(tut_dir.rglob("*.yml")):
            doc = _read(str(file.relative_to(CONTENT_DIR)))
            tutorials.setdefault(doc.get("subject", ""), {})[
                doc.get("chapter", "")
            ] = doc

    sources: dict[str, dict] = {}
    sources_file = CONTENT_DIR / "SOURCES.yml"
    if sources_file.exists():
        registry = _read("SOURCES.yml")
        sources = {s.get("id", ""): s for s in registry.get("sources") or []}

    return {
        "catalog": catalog,
        "kinds": kinds,
        "labels": labels,
        "subjects": subjects,
        "subject_kinds": subject_kinds,
        "notes": staged_notes,
        "practice": practice,
        "glossary": glossary,
        "formulas": formulas,
        "tips": tips,
        "paths": paths,
        "checklists": checklists,
        "diseases": diseases,
        "tutorials": tutorials,
        "source_registry": sources,
        "nmat": _read("exams/nmat.yml"),
        "mcat": _read("exams/mcat.yml"),
    }


# --------------------------------------------------------------------------
# public accessors
# --------------------------------------------------------------------------


def kinds() -> dict:
    return deepcopy(store()["kinds"])


def labels() -> dict:
    return dict(store()["labels"])


def _kind_subjects(kind: str) -> list[dict]:
    data = store()
    out = []
    for slug in data["kinds"].get(kind, []):
        subject = data["subjects"].get(slug)
        if subject:
            out.append(attach_notes(deepcopy(subject)))
    return out


def subjects(kind: str | None = None) -> list[dict]:
    if kind:
        return _kind_subjects(kind)
    out = []
    for kind_key in ("shared", "nmat", "mcat"):
        out.extend(_kind_subjects(kind_key))
    return out


def get_subject(slug: str) -> dict | None:
    subject = store()["subjects"].get(slug)
    return attach_notes(deepcopy(subject)) if subject else None


def shared_list() -> list[dict]:
    return _kind_subjects("shared")


def get_shared(slug: str) -> dict | None:
    data = store()
    subject = data["subjects"].get(slug)
    if subject and data["subject_kinds"].get(slug) == "shared":
        return attach_notes(deepcopy(subject))
    return None


def nmat_unique_subjects() -> list[dict]:
    return _kind_subjects("nmat")


def get_nmat_unique(slug: str) -> dict | None:
    data = store()
    subject = data["subjects"].get(slug)
    if subject and data["subject_kinds"].get(slug) == "nmat":
        return attach_notes(deepcopy(subject))
    return None


def get_mcat_section(slug: str) -> dict | None:
    data = store()
    subject = data["subjects"].get(slug)
    if subject and data["subject_kinds"].get(slug) == "mcat":
        return attach_notes(deepcopy(subject))
    return None


def nmat_exam() -> dict:
    data = store()
    exam = deepcopy(data["nmat"])
    if exam.get("parts"):
        refs = exam["parts"][0].pop("subject_refs", None) or []
        exam["parts"][0]["subjects"] = [
            attach_notes(deepcopy(data["subjects"][slug]))
            for slug in refs
            if slug in data["subjects"]
        ]
    return exam


def mcat_exam() -> dict:
    data = store()
    exam = deepcopy(data["mcat"])
    refs = exam.pop("section_refs", None) or []
    exam["sections"] = [
        attach_notes(deepcopy(data["subjects"][slug]))
        for slug in refs
        if slug in data["subjects"]
    ]
    return exam


def notes_for(slug: str, chapter_title: str) -> list[str]:
    bucket = store()["notes"].get(slug) or {}
    if chapter_title in bucket:
        return list(bucket[chapter_title])
    title_l = chapter_title.lower()
    left = chapter_title.split("·")[0].strip().lower()
    for key in sorted(bucket):
        k = key.lower()
        if k in title_l or title_l in k:
            return list(bucket[key])
        kleft = key.split("·")[0].strip().lower()
        if left and kleft == left and len(left) <= 4:
            return list(bucket[key])
    return []


def flashcards_for(slug: str, limit: int = 40) -> list[dict]:
    bucket = store()["notes"].get(slug) or {}
    cards: list[dict] = []
    for title in sorted(bucket):
        for note in bucket[title]:
            cards.append({"chapter": title, "text": note})
            if len(cards) >= limit:
                return cards
    return cards


def practice_for(slug: str) -> list[dict]:
    return deepcopy(store()["practice"].get(slug) or [])


def all_practice_slugs() -> list[str]:
    return sorted(store()["practice"])


def practice_catalog() -> list[dict]:
    data = store()
    out = []
    for slug in all_practice_slugs():
        out.append(
            {
                "slug": slug,
                "label": data["labels"].get(slug, slug),
                "count": len(data["practice"].get(slug) or []),
            }
        )
    return out


def glossary_terms(q: str = "", subject: str = "") -> list:
    rows = store()["glossary"]
    if q:
        ql = q.lower()
        rows = [
            g
            for g in rows
            if ql in g["term"].lower() or ql in g["def"].lower()
        ]
    if subject:
        rows = [g for g in rows if subject in (g.get("subjects") or [])]
    return deepcopy(rows)


def glossary_subject_slugs() -> list[str]:
    slugs: set[str] = set()
    for g in glossary_terms():
        slugs.update(g.get("subjects") or [])
    return sorted(slugs)


def formulas_for(slug: str) -> list:
    return deepcopy(store()["formulas"].get(slug) or [])


def formula_catalog() -> list[dict]:
    data = store()
    out = []
    for slug in data["catalog"].get("formula_slugs") or []:
        out.append(
            {
                "slug": slug,
                "label": data["labels"].get(slug, slug),
                "count": len(data["formulas"].get(slug) or []),
            }
        )
    return out


def exam_tips(exam: str = "") -> list:
    rows = store()["tips"]
    if exam:
        el = exam.upper()
        rows = [t for t in rows if t["exam"].upper() == el]
    return deepcopy(rows)


def study_paths() -> list:
    return deepcopy(store()["paths"])


def exam_checklists(exam: str = "") -> list:
    rows = store()["checklists"]
    if not exam:
        return deepcopy(rows)
    el = exam.upper()
    return deepcopy(
        [c for c in rows if c["exam"].upper() == el or c["exam"].upper() == "BOTH"]
    )


def all_diseases() -> list[dict]:
    rows = list(store()["diseases"].values())
    return sorted(deepcopy(rows), key=lambda d: d["name"].lower())


def get_disease(slug: str) -> dict | None:
    row = store()["diseases"].get(slug)
    return deepcopy(row) if row else None


def tutorial_for(subject_slug: str, chapter_title: str) -> dict | None:
    """Full tutorial chapter document, or None when not yet written."""
    doc = store()["tutorials"].get(subject_slug, {}).get(chapter_title)
    return deepcopy(doc) if doc else None


def tutorial_titles(subject_slug: str) -> set[str]:
    """Outline chapter titles of this subject that have a tutorial."""
    return set(store()["tutorials"].get(subject_slug, {}))


def source_info(source_id: str) -> dict:
    return deepcopy(store()["source_registry"].get(source_id, {}))
