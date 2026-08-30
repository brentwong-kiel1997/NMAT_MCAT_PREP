"""Chapter-page enrichment: the pedagogy layer.

Everything here is original to Gabay — the *formats* (key-terms panel,
bridge boxes, clinical links, high-yield flags, end-of-chapter drills,
strategy guides) mirror classic test-prep pedagogy, but all text and
mappings are ours.
"""

from __future__ import annotations

from .content import (
    bank_items_by_chapter, chapters_store, get_disease, get_subject,
    practice_for, store, tutorial_for,
)

# clinical mapping: chapter -> disease slugs whose science this chapter explains
# chapter -> diseases whose science this chapter explains (the Real-World
# layer). Skill subjects (reasoning/reading) intentionally have none.
CLINICAL: dict[str, list[str]] = {
    # biology core
    "cells-and-cellular-processes": ["type-2-diabetes"],
    "2a-assemblies-of-molecules-cells-and-cell-groups": ["type-2-diabetes", "asthma"],
    "2b-prokaryotes-and-viruses": ["tuberculosis", "pneumonia", "dengue"],
    "2c-cell-division-differentiation-specialization": ["type-2-diabetes"],
    "3a-nervous-and-endocrine-systems": ["type-2-diabetes", "asthma", "dengue"],
    "3b-main-organ-systems": ["tuberculosis", "pneumonia", "myocardial-infarction",
                              "acute-kidney-injury", "hypertension", "asthma"],
    "development": ["type-2-diabetes"],
    "genetics": ["type-2-diabetes"],
    "life-processes-regulation-and-homeostasis": ["acute-kidney-injury", "hypertension", "asthma"],
    "organisms-and-their-environment": ["dengue"],
    "unity-and-diversity-of-life": ["tuberculosis"],
    "the-world-of-plants-and-animals": ["dengue"],
    "1c-heritable-information-genetic-diversity": ["type-2-diabetes"],
    # chemistry / physics applied
    "4b-fluids-for-circulation-and-gas-exchange": ["myocardial-infarction", "hypertension",
                                                   "acute-kidney-injury", "asthma"],
    "4d-light-and-sound-interacting-with-matter": ["asthma"],
    "4c-electrochemistry-and-electrical-circuits": ["myocardial-infarction"],
    "4a-motion-forces-work-energy-equilibrium": ["myocardial-infarction"],
    "5a-unique-nature-of-water-and-its-solutions": ["acute-kidney-injury"],
    "5b-molecules-and-intermolecular-interactions": ["asthma"],
    "5c-separation-and-purification-methods": ["tuberculosis"],
    "5d-biologically-relevant-molecules": ["myocardial-infarction", "type-2-diabetes"],
    "5e-chemical-thermodynamics-and-kinetics": ["type-2-diabetes"],
    "analytical-chemistry": ["tuberculosis", "type-2-diabetes"],
    "general-chemistry": ["acute-kidney-injury"],
    "organic-chemistry": ["type-2-diabetes"],
    "biochemistry": ["type-2-diabetes", "myocardial-infarction"],
    "chemistry-of-biochemistry-cem": ["type-2-diabetes"],
    # biochemistry MCAT spine
    "1a-proteins-and-amino-acids": ["asthma"],
    "1d-bioenergetics-and-fuel-metabolism": ["type-2-diabetes", "myocardial-infarction"],
    # remaining MCAT-spine + social chapters
    "1b-gene-to-protein": ["type-2-diabetes"],
    "1c-heritable-information-diversity": ["type-2-diabetes"],
    "4e-atoms-nuclear-decay-electronic-structure": ["tuberculosis"],
    "mechanics": ["myocardial-infarction"],
    "electricity-and-magnetism": ["myocardial-infarction"],
    "thermodynamics": ["asthma"],
    "vibrations-waves-and-optics": ["asthma"],
    "modern-physics": ["tuberculosis"],
    "psychology": ["type-2-diabetes", "asthma"],
    "sociology-and-anthropology": ["hypertension"],
    "10a-social-inequality": ["hypertension", "tuberculosis", "type-2-diabetes"],
    "fc10-stratification-and-resources": ["hypertension", "asthma"],
    "fc6-perceive-think-react": ["asthma", "hypertension"],
    "fc7-behavior-and-behavior-change": ["asthma"],
    "fc8-self-others-interactions": ["hypertension"],
    "fc9-cultural-and-social-differences": ["tuberculosis"],
    "6a-sensing-the-environment": ["asthma"],
    "6b-making-sense-of-the-environment": ["asthma"],
    "6c-responding-to-the-world": ["asthma", "hypertension"],
    "7a-individual-influences-on-behavior": ["hypertension"],
    "7b-social-processes-that-influence-behavior": ["hypertension"],
    "7c-attitude-and-behavior-change": ["asthma"],
    "8a-self-identity": ["hypertension"],
    "8b-social-thinking": ["hypertension"],
    "8c-social-interactions": ["hypertension"],
    "9a-understanding-social-structure": ["hypertension", "tuberculosis"],
    "9b-demographic-characteristics-and-processes": ["tuberculosis", "dengue",
                                                     "myocardial-infarction", "type-2-diabetes"],
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
    """Keyless drill items for one chapter, from the amortized store index.

    Note: the drill page grades server-side through practice_attempt_api, so
    these keyless items plus the graded response are all it needs. Any future
    caller that needs keys must use content.exam_item_index instead."""
    return bank_items_by_chapter().get(chapter_id) or []


def drill_count(chapter_id: str, discipline: str) -> int:
    return len(bank_items_for_chapter(chapter_id)) or len(practice_for(discipline))


# glossary tags per tutorial subject: the subject itself plus the MCAT
# composite outlines that draw from it
GLOSSARY_TAGS: dict[str, list[str]] = {
    "biology": ["biology", "bio-biochem"],
    "biochemistry": ["biochemistry", "bio-biochem"],
    "chemistry": ["chemistry", "chem-phys"],
    "physics": ["physics", "chem-phys"],
    "behavioral-social": ["behavioral-social", "psych-soc"],
    "chem-phys": ["chem-phys", "chemistry", "physics"],
    "bio-biochem": ["bio-biochem", "biology", "biochemistry"],
    "psych-soc": ["psych-soc", "behavioral-social"],
}


def glossary_tags(subject_slug: str) -> list[str]:
    return GLOSSARY_TAGS.get(subject_slug, [subject_slug])


def glossary_for_subjects(subject_slugs: list[str], limit: int = 14) -> list[dict]:
    wanted = set(subject_slugs)
    out = [t for t in store().get("glossary") or [] if wanted & set(t.get("subjects") or [])]
    out.sort(key=lambda t: t.get("term", "").lower())
    return out[:limit]


def outline_neighbors(subject_slug: str, chapter_id: str) -> list[str]:
    """Adjacent chapters (prev/next with tutorials) in the subject outline —
    the universal bridge when no curated cross-discipline link exists."""
    subject = get_subject(subject_slug)
    if not subject:
        return []
    flat = [item for group in subject.get("chapters") or []
            for item in group.get("items") or []]
    idx = next((i for i, item in enumerate(flat)
                if item.get("chapter_id") == chapter_id), None)
    if idx is None:
        return []
    neighbors = []
    for j in (idx - 1, idx + 1):
        if 0 <= j < len(flat):
            cid = flat[j].get("chapter_id")
            ch = chapters_store().get(cid) or {}
            if tutorial_for(ch.get("discipline", ""), ch.get("title", "")):
                neighbors.append(cid)
    return neighbors


def chapter_bridges(chapter_id: str, subject_slug: str | None = None) -> list[dict]:
    """Curated cross-discipline bridges first, then outline neighbors —
    every chapter ends up with at least one bridge."""
    chs = chapters_store()
    seen: set[str] = {chapter_id}
    out = []
    for cid in BRIDGES.get(chapter_id, []):
        ch = chs.get(cid)
        if not ch:
            continue
        if tutorial_for(ch.get("discipline", ""), ch.get("title", "")):
            seen.add(cid)
            out.append({"chapter_id": cid, "discipline": ch.get("discipline", ""),
                        "title": ch.get("title", cid)})
    if subject_slug:
        for cid in outline_neighbors(subject_slug, chapter_id):
            if cid not in seen:
                ch = chs.get(cid) or {}
                seen.add(cid)
                out.append({"chapter_id": cid, "discipline": ch.get("discipline", ""),
                            "title": ch.get("title", cid)})
    return out


def clinical_links(chapter_id: str) -> list[dict]:
    out = []
    for slug in CLINICAL.get(chapter_id, []):
        d = get_disease(slug)
        if d:
            out.append({"slug": slug, "name": d.get("name", slug),
                        "short": d.get("short", "")})
    return out


def chapter_high_yield(chapter_id: str) -> bool:
    counts = {cid: len(items) for cid, items in
              bank_items_by_chapter().items()}
    values = sorted(counts.values(), reverse=True)
    if not values:
        return False
    cut = max(6, values[int(len(values) * 0.25)])
    return counts.get(chapter_id, 0) >= cut
