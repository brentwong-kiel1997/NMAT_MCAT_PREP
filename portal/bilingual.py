"""Attach English mirrors onto exam/subject dicts for bilingual templates."""

from __future__ import annotations

from copy import deepcopy

from .zh_en import t


def _map_points(points: list | None) -> list[str]:
    return [t(p) for p in (points or [])]


def enrich_item(item: dict) -> dict:
    out = deepcopy(item)
    out["points_en"] = _map_points(out.get("points"))
    if "title" in out:
        out["title_en"] = t(out["title"]) if any("\u4e00" <= c <= "\u9fff" for c in out["title"]) else out["title"]
    return out


def enrich_chapters(chapters: list | None) -> list:
    result = []
    for group in chapters or []:
        g = deepcopy(group)
        heading = g.get("heading", "")
        g["heading_en"] = t(heading) if any("\u4e00" <= c <= "\u9fff" for c in heading) else heading
        # common bilingual headings
        heading_map = {
            "NMAT · CEM BOI 章节": "NMAT · CEM BOI chapters",
            "MCAT · 相关 Content Categories（AAMC）": "MCAT · related Content Categories (AAMC)",
            "MCAT · Foundational Concept 4（AAMC）": "MCAT · Foundational Concept 4 (AAMC)",
            "MCAT · Foundational Concepts 6–10（AAMC）": "MCAT · Foundational Concepts 6–10 (AAMC)",
            "NMAT 对照": "NMAT crosswalk",
            "MCAT · Foundational Concept 1（AAMC）": "MCAT · Foundational Concept 1 (AAMC)",
            "大知识点 / 章节": "Major topics / chapters",
            "CARS 技能章节（AAMC）": "CARS skill chapters (AAMC)",
            "Foundational Concept 1（约 55%）": "Foundational Concept 1 (~55%)",
            "Foundational Concept 2（约 20%）": "Foundational Concept 2 (~20%)",
            "Foundational Concept 3（约 25%）": "Foundational Concept 3 (~25%)",
            "Foundational Concept 4（约 40%）": "Foundational Concept 4 (~40%)",
            "Foundational Concept 5（约 60%）": "Foundational Concept 5 (~60%)",
            "Foundational Concept 6（约 25%）": "Foundational Concept 6 (~25%)",
            "Foundational Concept 7（约 35%）": "Foundational Concept 7 (~35%)",
            "Foundational Concept 8（约 20%）": "Foundational Concept 8 (~20%)",
            "Foundational Concept 9（约 15%）": "Foundational Concept 9 (~15%)",
            "Foundational Concept 10（约 5%）": "Foundational Concept 10 (~5%)",
        }
        g["heading_en"] = heading_map.get(heading, g.get("heading_en", heading))
        g["items"] = [enrich_item(it) for it in g.get("items", [])]
        result.append(g)
    return result


def enrich_subject(subject: dict | None) -> dict | None:
    if not subject:
        return None
    out = deepcopy(subject)
    for key in ("summary", "focus", "nmat_role", "mcat_role", "source_note", "format"):
        if key in out and isinstance(out[key], str):
            out[f"{key}_en"] = t(out[key])
    notes = out.get("exam_notes")
    if isinstance(notes, dict):
        out["exam_notes_en"] = {k: t(v) for k, v in notes.items()}
    if "chapters" in out:
        out["chapters"] = enrich_chapters(out["chapters"])
    # bilingual name display helpers
    out["label_zh"] = out.get("name_zh") or out.get("name")
    out["label_en"] = out.get("name") or out.get("name_zh")
    from .notes import attach_notes

    return attach_notes(out)

def enrich_exam(exam: dict) -> dict:
    out = deepcopy(exam)
    if "format" in out:
        out["format_en"] = t(out["format"])
    if "discipline_mix_note" in out:
        out["discipline_mix_note_en"] = t(out["discipline_mix_note"])
    if "parts" in out:
        for part in out["parts"]:
            part["name_en"] = part.get("name")
            part["subjects"] = [enrich_subject(s) for s in part.get("subjects", [])]
    if "sections" in out:
        out["sections"] = [enrich_subject(s) for s in out["sections"]]
    return out
