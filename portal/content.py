"""Read textbook content from the content/ YAML directory.

content/ is the single source of truth for curriculum subjects, chapter
notes, practice MCQs, glossary, formulas, tips, study paths, checklists and
disease articles. Files are parsed on demand and cached on an mtime+size
stamp (same pattern as envfile.py), so editing a YAML file takes effect on
the next request without restarting Gunicorn.

Bilingual convention: a value is either a plain scalar (identical in both
languages) or a ``{zh: ..., en: ...}`` mapping, expanded here into the flat
``<key>`` / ``<key>_en`` names the templates already consume.

Layout::

    content/catalog.yml              kinds/formula order + subject labels
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
# bilingual expansion
# --------------------------------------------------------------------------


def _flat(value):
    """Expand a scalar or {zh, en} mapping into (value, value_en)."""
    if isinstance(value, dict):
        return value.get("zh", ""), value.get("en", "")
    return value, value


def _pair_field(doc: dict, key: str, out: dict) -> None:
    if key in doc:
        out[key], out[f"{key}_en"] = _flat(doc[key])


def _expand_points(items) -> tuple[list, list]:
    zh: list = []
    en: list = []
    for item in items or []:
        a, b = _flat(item)
        zh.append(a)
        en.append(b)
    return zh, en


def _expand_chapters(raw: list) -> list:
    groups: list = []
    for group in raw or []:
        heading, heading_en = _flat(group.get("heading", ""))
        out = dict(group)
        out["heading"] = heading
        out["heading_en"] = heading_en
        items = []
        for item in group.get("items") or []:
            it = dict(item)
            it["points"], it["points_en"] = _expand_points(item.get("points"))
            if "title" in it:
                it["title"], it["title_en"] = _flat(item["title"])
            items.append(it)
        out["items"] = items
        groups.append(out)
    return groups


def _expand_subject(doc: dict) -> dict:
    out = {k: v for k, v in doc.items() if k != "kind"}
    for key in (
        "summary",
        "focus",
        "nmat_role",
        "mcat_role",
        "source_note",
        "format",
    ):
        _pair_field(doc, key, out)
    if isinstance(doc.get("exam_notes"), dict):
        notes = {}
        notes_en = {}
        for exam, value in doc["exam_notes"].items():
            notes[exam], notes_en[exam] = _flat(value)
        out["exam_notes"] = notes
        out["exam_notes_en"] = notes_en
    if "chapters" in doc:
        out["chapters"] = _expand_chapters(doc["chapters"])
    out["label_zh"] = out.get("name_zh") or out.get("name")
    out["label_en"] = out.get("name") or out.get("name_zh")
    return out


# --------------------------------------------------------------------------
# chapter ids + note attachment (identical derivation to the old notes.py)
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

# Forward overlay, line-for-line from the old portal/notes.py import-time
# block: shared subject pages pick up MCAT chapter notes. Canonical buckets
# live in content/notes/; the copies are made here at read time. Note that
# chem-phys and bio-biochem merge from the ALREADY-STAGED physics/chemistry/
# biology buckets, exactly like the original ordering.
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
        slug: {"zh": pair.get("zh", slug), "en": pair.get("en", slug)}
        for slug, pair in (catalog.get("labels") or {}).items()
    }

    subjects: dict[str, dict] = {}
    subject_kinds: dict[str, str] = {}
    subj_dir = CONTENT_DIR / "subjects"
    if not subj_dir.is_dir():
        raise ContentError(f"missing directory {subj_dir}")
    for file in sorted(subj_dir.glob("*.yml")):
        doc = _read(f"subjects/{file.name}")
        subjects[doc["slug"]] = _expand_subject(doc)
        subject_kinds[doc["slug"]] = doc.get("kind", "shared")

    # canonical note buckets → forward overlay
    base_notes: dict[str, dict] = {}
    notes_dir = CONTENT_DIR / "notes"
    if notes_dir.is_dir():
        for file in sorted(notes_dir.glob("*.yml")):
            doc = _read(f"notes/{file.name}")
            base_notes[doc["slug"]] = {
                ch["title"]: [dict(b) for b in ch.get("bullets") or []]
                for ch in doc.get("chapters") or []
            }
    staged_notes = _overlay(base_notes)

    practice: dict[str, list] = {}
    prac_dir = CONTENT_DIR / "practice"
    if prac_dir.is_dir():
        for file in sorted(prac_dir.glob("*.yml")):
            doc = _read(f"practice/{file.name}")
            items = []
            for item in doc.get("items") or []:
                q_zh, q_en = _flat(item.get("q", ""))
                ex_zh, ex_en = _flat(item.get("explain", ""))
                choices = {}
                for key, value in (item.get("choices") or {}).items():
                    choices[key] = dict(_flat_dict(value))
                items.append(
                    {
                        "id": item.get("id", ""),
                        "q_zh": q_zh,
                        "q_en": q_en,
                        "choices": choices,
                        "answer": item.get("answer", ""),
                        "explain_zh": ex_zh,
                        "explain_en": ex_en,
                        "chapter": item.get("chapter", ""),
                    }
                )
            practice[doc["slug"]] = items

    glossary = []
    for term in (_read("materials/glossary.yml").get("terms") or []):
        def_zh, def_en = _flat(term.get("def", ""))
        glossary.append(
            {
                "term": term.get("term", ""),
                "term_zh": term.get("term_zh", ""),
                "def_zh": def_zh,
                "def_en": def_en,
                "subjects": list(term.get("subjects") or []),
            }
        )

    formulas: dict[str, list] = {}
    for sheet in (_read("materials/formulas.yml").get("sheets") or []):
        entries = []
        for entry in sheet.get("entries") or []:
            title_zh, title_en = _flat(entry.get("title", ""))
            note_zh, note_en = _flat(entry.get("note", ""))
            entries.append(
                {
                    "title_zh": title_zh,
                    "title_en": title_en,
                    "formula": entry.get("formula", ""),
                    "note_zh": note_zh,
                    "note_en": note_en,
                }
            )
        formulas[sheet["slug"]] = entries

    tips = []
    for tip in (_read("materials/tips.yml").get("tips") or []):
        title_zh, title_en = _flat(tip.get("title", ""))
        body_zh, body_en = _flat(tip.get("body", ""))
        tips.append(
            {
                "exam": tip.get("exam", ""),
                "title_zh": title_zh,
                "title_en": title_en,
                "body_zh": body_zh,
                "body_en": body_en,
            }
        )

    paths = []
    for path in (_read("materials/paths.yml").get("paths") or []):
        title_zh, title_en = _flat(path.get("title", ""))
        blurb_zh, blurb_en = _flat(path.get("blurb", ""))
        steps = []
        for step in path.get("steps") or []:
            label_zh, label_en = _flat(step)
            steps.append({"label_zh": label_zh, "label_en": label_en, "href": step.get("href", "")})
        paths.append(
            {
                "id": path.get("id", ""),
                "title_zh": title_zh,
                "title_en": title_en,
                "blurb_zh": blurb_zh,
                "blurb_en": blurb_en,
                "steps": steps,
            }
        )

    checklists = []
    for cl in (_read("materials/checklists.yml").get("checklists") or []):
        title_zh, title_en = _flat(cl.get("title", ""))
        items_zh, items_en = _expand_points(cl.get("items"))
        checklists.append(
            {
                "id": cl.get("id", ""),
                "exam": cl.get("exam", ""),
                "title_zh": title_zh,
                "title_en": title_en,
                "items_zh": items_zh,
                "items_en": items_en,
            }
        )

    diseases: dict[str, dict] = {}
    dis_dir = CONTENT_DIR / "diseases"
    if not dis_dir.is_dir():
        raise ContentError(f"missing directory {dis_dir}")
    for file in sorted(dis_dir.glob("*.yml")):
        doc = _read(f"diseases/{file.name}")
        diseases[doc["slug"]] = doc

    nmat = _expand_exam(_read("exams/nmat.yml"))
    mcat = _expand_exam(_read("exams/mcat.yml"))

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
        "nmat": nmat,
        "mcat": mcat,
    }


def _flat_dict(value):
    if isinstance(value, dict):
        return {"zh": value.get("zh", ""), "en": value.get("en", "")}
    return {"zh": value, "en": value}


def _expand_exam(doc: dict) -> dict:
    out = dict(doc)
    _pair_field(doc, "format", out)
    _pair_field(doc, "discipline_mix_note", out)
    parts = []
    for part in doc.get("parts") or []:
        p = dict(part)
        p["name_en"] = p.get("name")
        p["subjects"] = [
            _expand_inline_subject(s) for s in part.get("subjects") or []
        ]
        parts.append(p)
    if parts:
        out["parts"] = parts
    return out


def _expand_inline_subject(doc: dict) -> dict:
    """Exam-hub entries that are not full subjects (NMAT part-2 links)."""
    out = _expand_subject(doc)
    return out


# --------------------------------------------------------------------------
# public accessors — shapes match the loaders they replace
# --------------------------------------------------------------------------


def kinds() -> dict:
    return deepcopy(store()["kinds"])


def labels() -> dict:
    return deepcopy(store()["labels"])


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
    data = store()
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


def notes_for(slug: str, chapter_title: str) -> list[dict[str, str]]:
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
            cards.append({"chapter": title, "zh": note["zh"], "en": note["en"]})
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
        label = data["labels"].get(slug, {"zh": slug, "en": slug})
        out.append(
            {
                "slug": slug,
                "label_zh": label["zh"],
                "label_en": label["en"],
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
            if ql in g["term"].lower()
            or ql in (g.get("term_zh") or "").lower()
            or ql in g["def_zh"].lower()
            or ql in g["def_en"].lower()
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
        label = data["labels"].get(slug, {"zh": slug, "en": slug})
        out.append(
            {
                "slug": slug,
                "label_zh": label["zh"],
                "label_en": label["en"],
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
