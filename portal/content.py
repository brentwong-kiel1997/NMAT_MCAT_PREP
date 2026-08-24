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


def attach_notes(subject: dict) -> dict:
    """Resolve a subject's chapter REFERENCES against the chapter library.

    Each reference group becomes {heading, items:[...]}; items are views of
    library chapters: title/points/chapter_id(=slug)/exams/study_notes.
    """
    if not subject:
        return subject
    data = store()
    for group in subject.get("chapters") or []:
        items = []
        for slug in group.get("chapters") or []:
            ch = data["chapters"].get(slug)
            if not ch:
                raise ContentError(
                    f"subject {subject.get('slug')!r} references unknown chapter {slug!r}"
                )
            item = {
                "title": ch.get("title", ""),
                "points": list(ch.get("points") or []),
                "chapter_id": slug,
                "exams": list(ch.get("exams") or []),
            }
            if ch.get("notes"):
                item["study_notes"] = list(ch["notes"])
            items.append(item)
        group["items"] = items
    return subject


# --------------------------------------------------------------------------
# store construction
# --------------------------------------------------------------------------

def _build() -> dict:
    catalog = _read("catalog.yml")
    kinds = {kind: list(slugs) for kind, slugs in (catalog.get("kinds") or {}).items()}
    labels = {
        slug: (label if isinstance(label, str) else slug)
        for slug, label in (catalog.get("labels") or {}).items()
    }

    # unified chapter library — ONE instance per chapter (content/chapters/)
    chapters: dict[str, dict] = {}
    chap_dir = CONTENT_DIR / "chapters"
    if not chap_dir.is_dir():
        raise ContentError(f"missing directory {chap_dir}")
    for file in sorted(chap_dir.glob("*.yml")):
        doc = _read(f"chapters/{file.name}")
        doc.setdefault("id", file.stem)
        chapters[doc["id"]] = doc
    chapter_by_title = {c.get("title", ""): c for c in chapters.values()}

    # subjects = exam-facing ordered REFERENCE lists over the chapter library
    subjects: dict[str, dict] = {}
    subject_kinds: dict[str, str] = {}
    subj_dir = CONTENT_DIR / "subjects"
    if not subj_dir.is_dir():
        raise ContentError(f"missing directory {subj_dir}")
    for file in sorted(subj_dir.glob("*.yml")):
        doc = _read(f"subjects/{file.name}")
        subjects[doc["slug"]] = doc
        subject_kinds[doc["slug"]] = doc.get("kind", "shared")

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
        "chapters": chapters,
        "chapter_by_title": chapter_by_title,
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
    """Notes of the referenced chapter (exact title, then fuzzy)."""
    ch = store()["chapter_by_title"].get(chapter_title)
    if ch:
        return list(ch.get("notes") or [])
    title_l = chapter_title.lower()
    for title, ch2 in sorted(store()["chapter_by_title"].items()):
        k = title.lower()
        if k in title_l or title_l in k:
            return list(ch2.get("notes") or [])
    return []


def _subject_chapter_slugs(slug: str) -> list[str]:
    subject = store()["subjects"].get(slug) or {}
    return [
        s for group in subject.get("chapters") or [] for s in (group.get("chapters") or [])
    ]


def flashcards_for(slug: str, limit: int = 40) -> list[dict]:
    data = store()
    cards: list[dict] = []
    pairs = []
    for s in _subject_chapter_slugs(slug):
        ch = data["chapters"].get(s) or {}
        for note in ch.get("notes") or []:
            pairs.append((ch.get("title", ""), note))
    for title, note in sorted(pairs):
        cards.append({"chapter": title, "text": note})
        if len(cards) >= limit:
            return cards
    return cards


def practice_for(slug: str) -> list[dict]:
    data = store()
    items: list[dict] = []
    for s in _subject_chapter_slugs(slug):
        ch = data["chapters"].get(s) or {}
        items.extend(deepcopy(ch.get("practice") or []))
    return items


def all_practice_slugs() -> list[str]:
    data = store()
    return sorted(
        slug for slug in data["subjects"] if practice_for(slug)
    )


def practice_catalog() -> list[dict]:
    data = store()
    out = []
    for slug in all_practice_slugs():
        out.append(
            {
                "slug": slug,
                "label": data["labels"].get(slug, slug),
                "count": len(practice_for(slug)),
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


# --------------------------------------------------------------------------
# learning projects & study units (content/units.yml)
#
# One unified content library; two learning projects (NMAT / MCAT). A unit
# aggregates a prefix-filtered set of one source subject's chapters — MCAT
# exam-day sections like Chem/Phys are split into Chemical / Physical study
# units. Exam annotation per chapter instance is DERIVED from the subject's
# kind (shared → [NMAT, MCAT]; nmat → [NMAT]; mcat → [MCAT]), adjustable via
# exam_overrides.
# --------------------------------------------------------------------------

_units_cache: dict | None = None
_units_stamp: tuple | None = None


def _units_stamp_value() -> tuple:
    path = CONTENT_DIR / "units.yml"
    if not path.exists():
        return (("units.yml", -1, -1),)
    st = path.stat()
    return (("units.yml", st.st_mtime_ns, st.st_size),)


def units_store() -> dict:
    """Parsed units.yml plus resolved per-unit chapter lists (mtime-cached)."""
    global _units_cache, _units_stamp
    stamp = _units_stamp_value()
    if _units_cache is None or stamp != _units_stamp:
        data = store()
        doc = _read("units.yml") if (CONTENT_DIR / "units.yml").exists() else {}

        units: dict[str, dict] = {}
        for proj_key, proj in (doc.get("projects") or {}).items():
            for u in (proj.get("units") or []):
                key = u["key"]
                refs = list(u.get("chapters") or [])
                chapters = []
                for slug in refs:
                    ch = data["chapters"].get(slug)
                    if not ch:
                        raise ContentError(
                            f"units.yml: unit {key!r} references unknown chapter {slug!r}"
                        )
                    chapters.append(
                        {
                            "subject": ch.get("discipline", ""),
                            "title": ch.get("title", ""),
                            "chapter_id": slug,
                            "group": "",
                            "exams": list(ch.get("exams") or []),
                        }
                    )
                units[key] = {
                    "key": key,
                    "project": proj_key,
                    "label": u.get("label", key),
                    "group": u.get("group", ""),
                    "source": u.get("source", ""),
                    "cross": list(u.get("cross") or []),
                    "chapters": chapters,
                }
        _units_cache = {
            "projects": doc.get("projects") or {},
            "units": units,
            "subject_kinds": data.get("subject_kinds", {}),
        }
        _units_stamp = stamp
    return _units_cache


def projects() -> dict:
    return deepcopy(units_store()["projects"])


def unit(key: str) -> dict | None:
    u = units_store()["units"].get(key)
    return deepcopy(u) if u else None


def unit_chapters(key: str) -> list:
    u = units_store()["units"].get(key)
    return deepcopy(u["chapters"]) if u else []


def chapter_exams(subject_slug: str, chapter_title: str) -> list:
    ch = store()["chapter_by_title"].get(chapter_title)
    if ch:
        return list(ch.get("exams") or [])
    return []


def project_units() -> list:
    """Projects with their units resolved (for hub pages)."""
    store_v = units_store()
    out = []
    for proj_key, proj in (store_v["projects"] or {}).items():
        units = []
        for u in (proj.get("units") or []):
            resolved = store_v["units"].get(u["key"])
            if resolved:
                units.append(resolved)
        out.append({"key": proj_key, "name": proj.get("name", proj_key), "units": units})
    return out


def units_of(subject_slug: str) -> list:
    """Study units this subject participates in (source + cross), with project."""
    out = []
    for u in units_store()["units"].values():
        if u["source"] == subject_slug or subject_slug in u.get("cross", []):
            out.append({"key": u["key"], "project": u["project"], "label": u["label"]})
    return out
