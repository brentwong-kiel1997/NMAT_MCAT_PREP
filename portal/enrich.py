"""Chapter-page enrichment: the TPR-style pedagogy layer.

Everything here is original to Gabay — the *formats* (key-terms panel,
bridge boxes, clinical links, high-yield flags, end-of-chapter drills,
strategy guides) mirror classic test-prep pedagogy, but all text and
mappings are ours.
"""

from __future__ import annotations

from .content import (
    all_bank_items, chapters_store, get_disease, practice_for, store, tutorial_for,
)

# clinical mapping: disease -> chapter ids whose science explains it
CLINICAL_BRIDGES: dict[str, list[str]] = {
    "tuberculosis": ["2b-prokaryotes-and-viruses", "3b-main-organ-systems",
                     "life-processes-regulation-and-homeostasis"],
    "pneumonia": ["3b-main-organ-systems", "2b-prokaryotes-and-viruses"],
    "myocardial-infarction": ["3b-main-organ-systems", "4b-fluids-for-circulation-and-gas-exchange",
                              "5d-biologically-relevant-molecules"],
    "acute-kidney-injury": ["3b-main-organ-systems", "life-processes-regulation-and-homeostasis",
                            "4b-fluids-for-circulation-and-gas-exchange"],
    "dengue": ["2b-prokaryotes-and-viruses", "3a-nervous-and-endocrine-systems",
               "organisms-and-their-environment"],
    "type-2-diabetes": ["1d-bioenergetics-and-fuel-metabolism", "3a-nervous-and-endocrine-systems",
                        "biochemistry", "3b-main-organ-systems"],
    "hypertension": ["4b-fluids-for-circulation-and-gas-exchange", "3b-main-organ-systems",
                     "10a-social-inequality"],
    "asthma": ["3b-main-organ-systems", "4d-light-and-sound-interacting-with-matter"],
}

# cross-discipline bridges: chapter -> related chapters elsewhere (TPR "Bridge")
BRIDGES: dict[str, list[str]] = {
    "4b-fluids-for-circulation-and-gas-exchange": [
        "3b-main-organ-systems", "4a-motion-forces-work-energy-equilibrium", "biochemistry"],
    "4c-electrochemistry-and-electrical-circuits": [
        "4a-motion-forces-work-energy-equilibrium", "3a-nervous-and-endocrine-systems"],
    "4e-atoms-nuclear-decay-electronic-structure": ["modern-physics", "5a-unique-nature-of-water-and-its-solutions"],
    "5d-biologically-relevant-molecules": ["1a-proteins-and-amino-acids", "cells-and-cellular-processes"],
    "5e-chemical-thermodynamics-and-kinetics": ["1d-bioenergetics-and-fuel-metabolism", "thermodynamics"],
    "biochemistry": ["1d-bioenergetics-and-fuel-metabolism", "5d-biologically-relevant-molecules",
                     "organic-chemistry"],
    "1d-bioenergetics-and-fuel-metabolism": ["5e-chemical-thermodynamics-and-kinetics",
                                             "3b-main-organ-systems", "1a-proteins-and-amino-acids"],
    "3a-nervous-and-endocrine-systems": ["4c-electrochemistry-and-electrical-circuits",
                                         "fc6-perceive-think-react"],
    "mechanics": ["4a-motion-forces-work-energy-equilibrium", "4b-fluids-for-circulation-and-gas-exchange"],
    "thermodynamics": ["5e-chemical-thermodynamics-and-kinetics", "1d-bioenergetics-and-fuel-metabolism"],
}


def bank_items_for_chapter(chapter_id: str) -> list[dict]:
    """Normalized drill items for one chapter (with keys — server-side only)."""
    items = [i for i in all_bank_items().values() if i.get("chapter") == chapter_id]
    items.sort(key=lambda i: i["id"])
    return items


def drill_count(chapter_id: str, discipline: str) -> int:
    return len(bank_items_for_chapter(chapter_id)) or len(practice_for(discipline))


def glossary_for_subjects(subject_slugs: list[str], limit: int = 14) -> list[dict]:
    wanted = set(subject_slugs)
    out = [t for t in store().get("glossary") or [] if wanted & set(t.get("subjects") or [])]
    out.sort(key=lambda t: t.get("term", "").lower())
    return out[:limit]


def chapter_bridges(chapter_id: str) -> list[dict]:
    chs = chapters_store()
    out = []
    for cid in BRIDGES.get(chapter_id, []):
        ch = chs.get(cid)
        if not ch:
            continue
        if tutorial_for(ch.get("discipline", ""), ch.get("title", "")):
            out.append({"chapter_id": cid, "discipline": ch.get("discipline", ""),
                        "title": ch.get("title", cid)})
    return out


def clinical_links(chapter_id: str) -> list[dict]:
    out = []
    for slug, chapter_ids in CLINICAL_BRIDGES.items():
        if chapter_id in chapter_ids:
            d = get_disease(slug)
            if d:
                out.append({"slug": slug, "name": d.get("name", slug),
                            "short": d.get("short", "")})
    return out


def high_yield_threshold() -> int:
    return 6


def chapter_high_yield(chapter_id: str) -> bool:
    return len(bank_items_for_chapter(chapter_id)) >= high_yield_threshold()
