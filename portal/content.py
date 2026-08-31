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
        "strategy": _read("strategy.yml") if (CONTENT_DIR / "strategy.yml").exists() else {},
        "exam_defs": {
            f.stem: _read(f"exams/{f.name}")
            for f in sorted((CONTENT_DIR / "exams").glob("*.yml"))
        },
        "exam_bank": _load_exam_bank(),
        "bank_items_by_chapter": _bank_index(),
    }


def _bank_index() -> dict[str, list[dict]]:
    """chapter id -> keyless normalized bank items (id order), computed once
    per store build. Consumers on pre-answer pages must never re-add keys."""
    by_chapter: dict[str, list[dict]] = {}
    bank = _load_exam_bank()
    for exam_id, sections in (bank.get("exams") or {}).items():
        for section_id, doc in sections.items():
            for raw in doc.get("items") or []:
                item = _normalize_item(raw, exam_id=exam_id, section_id=section_id,
                                       block_id="", passage=None)
                by_chapter.setdefault(item["chapter"], []).append(_strip_key(item))
            for passage in doc.get("passages") or []:
                for raw in passage.get("items") or []:
                    item = _normalize_item(raw, exam_id=exam_id, section_id=section_id,
                                           block_id="", passage=passage)
                    by_chapter.setdefault(item["chapter"], []).append(_strip_key(item))
    for items in by_chapter.values():
        items.sort(key=lambda i: i["id"])
    return by_chapter


def _load_exam_bank() -> dict:
    """Load content/exam-bank/** defensively.

    A malformed bank file must never take the whole site down (the deploy
    poller refreshes the checkout before validation runs), so parse errors
    are collected under "errors" instead of raising.
    """
    bank_dir = CONTENT_DIR / "exam-bank"
    if not bank_dir.is_dir():
        return {}
    bank: dict[str, dict[str, dict]] = {}
    _seen_bank_keys: set[tuple[str, str]] = set()
    errors: list[str] = []
    for file in sorted(bank_dir.rglob("*.yml")):
        try:
            doc = _read(str(file.relative_to(CONTENT_DIR)))
        except ContentError as exc:
            errors.append(str(exc))
            continue
        # drill/ files are practice-only: never part of a mock blueprint
        if "drill" in file.relative_to(bank_dir).parts:
            doc["_drill"] = True
        key = (doc.get("exam", ""), doc.get("section", file.stem))
        if key in _seen_bank_keys:
            errors.append(f"duplicate exam-bank key {key!r} — files in one "
                          f"(exam, section) slot must be unique")
            continue
        _seen_bank_keys.add(key)
        bank.setdefault(doc.get("exam", ""), {})[doc.get("section", file.stem)] = doc
    out: dict[str, object] = {"exams": bank}
    if errors:
        out["errors"] = errors
    return out


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
        if limit is not None and len(cards) >= limit:
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
    """Parsed units.yml plus DERIVED per-unit chapter lists (mtime-cached).

    A unit is a discipline: its chapters are every library chapter of that
    discipline, filtered by the owning project's exam (NMAT units show the
    discipline's NMAT-annotated chapters, MCAT units the MCAT ones — shared
    chapters appear in both views by design). No chapter lists are stored.
    """
    global _units_cache, _units_stamp
    stamp = _units_stamp_value()
    if _units_cache is None or stamp != _units_stamp:
        data = store()
        doc = _read("units.yml") if (CONTENT_DIR / "units.yml").exists() else {}
        proj_exam = {"nmat": "NMAT", "mcat": "MCAT"}

        by_discipline: dict[str, list] = {}
        for slug, ch in data["chapters"].items():
            by_discipline.setdefault(ch.get("discipline", ""), []).append((slug, ch))

        units: dict[str, dict] = {}
        for proj_key, proj in (doc.get("projects") or {}).items():
            exam = proj_exam.get(proj_key, "NMAT")
            for u in (proj.get("units") or []):
                key = u["key"]
                chapters = [
                    {
                        "subject": disc,
                        "title": ch.get("title", ""),
                        "chapter_id": slug,
                        "group": "",
                        "exams": list(ch.get("exams") or []),
                    }
                    for disc in [u.get("source", "")]
                    for slug, ch in by_discipline.get(disc, [])
                    if exam in (ch.get("exams") or [])
                ]
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


# ---- mock-exam engine accessors -------------------------------------------

def strategy_guides() -> list[dict]:
    """Original test-strategy guides (content/strategy.yml)."""
    doc = store().get("strategy") or {}
    return deepcopy(doc.get("guides") or [])


def bank_items_by_chapter() -> dict[str, list[dict]]:
    """chapter id -> keyless items (amortized: precomputed per store build).

    Returns the store's own mapping WITHOUT copying — treat as read-only.
    Every current caller only reads/scans it; hand out copies if that ever
    changes. This keeps chapter pages from re-deepcopying 470 items each hit.
    """
    return store().get("bank_items_by_chapter") or {}


def chapters_store() -> dict:
    """id → chapter doc (from the unified library)."""
    return deepcopy(store()["chapters"])


def exam_defs() -> dict:
    """Every content/exams/*.yml keyed by file stem (nmat, mcat, demo, ...)."""
    return deepcopy(store().get("exam_defs") or {})


def exam_blueprint(exam_id: str) -> dict | None:
    doc = store().get("exam_defs", {}).get(exam_id)
    if not doc:
        return None
    bp = doc.get("blueprint") or {}
    return deepcopy(bp) if bp else None


def exam_bank_errors() -> list[str]:
    return list((store().get("exam_bank") or {}).get("errors") or [])


def _bank_docs(exam_id: str) -> dict[str, dict]:
    return dict((store().get("exam_bank") or {}).get("exams", {}).get(exam_id) or {})


def exam_bank_section(exam_id: str, section_id: str) -> dict | None:
    doc = _bank_docs(exam_id).get(section_id)
    return deepcopy(doc) if doc else None


def _normalize_item(raw: dict, *, exam_id: str, section_id: str, block_id: str,
                    passage: dict | None) -> dict:
    return {
        "id": raw.get("id", ""),
        "exam": exam_id,
        "section_id": section_id,
        "block_id": block_id,
        "q": raw.get("q", ""),
        "choices": dict(raw.get("choices") or {}),
        "answer": raw.get("answer", ""),
        "explain": raw.get("explain", ""),
        "distractors": dict(raw.get("distractors") or {}),
        "chapter": raw.get("chapter", ""),
        "passage_id": (passage or {}).get("id", ""),
        "passage_text": (passage or {}).get("text", ""),
    }


def exam_items(exam_id: str, *, with_key: bool = False) -> list[dict]:
    """Flatten the bank into blueprint block order, normalized items."""
    bp = exam_blueprint(exam_id)
    if not bp:
        return []
    docs = _bank_docs(exam_id)
    out: list[dict] = []
    for block in bp.get("blocks") or []:
        for section_id in block.get("bank") or []:
            doc = docs.get(section_id) or {}
            for raw in doc.get("items") or []:
                item = _normalize_item(raw, exam_id=exam_id, section_id=section_id,
                                       block_id=block["id"], passage=None)
                out.append(item if with_key else _strip_key(item))
            for passage in doc.get("passages") or []:
                for raw in passage.get("items") or []:
                    item = _normalize_item(raw, exam_id=exam_id, section_id=section_id,
                                           block_id=block["id"], passage=passage)
                    out.append(item if with_key else _strip_key(item))
    return out


def _strip_key(item: dict) -> dict:
    return {k: v for k, v in item.items()
            if k not in ("answer", "explain", "distractors")}


def exam_item_index(exam_id: str) -> dict[str, dict]:
    """id → item WITH answer/explain. Server-side only — never ship to a
    pre-submit page."""
    return {i["id"]: i for i in exam_items(exam_id, with_key=True)}


def all_bank_items() -> dict[str, dict]:
    """Cross-exam item index (with keys) for the attempt/redo APIs."""
    out: dict[str, dict] = {}
    for exam_id in (store().get("exam_bank") or {}).get("exams", {}):
        out.update(exam_item_index(exam_id))
    return out


def render_item(item: dict, *, with_key: bool) -> dict:
    return dict(item) if with_key else _strip_key(dict(item))
