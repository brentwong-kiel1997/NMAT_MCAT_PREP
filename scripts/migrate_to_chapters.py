"""One-shot migration: build the unified chapter library.

Applies the hand-reviewed merge verdicts from
content/docs/RESTRUCTURE_PLAN.md (each group was reviewed side by side —
NOT matched by code). Produces:

  content/chapters/<slug>.yml   one file per unique chapter
  content/subjects/*.yml        rewritten as ordered reference lists
  content/units.yml             rewritten to reference chapter slugs
  /tmp/migration_report.txt     merge report + count reconciliation

Run once from the repo root with the CURRENT (pre-migration) reader:
    python scripts/migrate_to_chapters.py
The portal reader is switched separately; until then this script's output
is staged for review (chapters/ is written; subjects/units are written to
/tmp first — swap them in only together with the reader switch).
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

import yaml  # noqa: E402
from pathlib import Path  # noqa: E402

from portal import content  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

# Hand-reviewed merge verdicts (plan §Merge verdicts).
# canonical title → (discipline, [(subject, instance-title), ...])
MERGES: dict[str, tuple[str, list[tuple[str, str]]]] = {
    "1A · Proteins and amino acids": ("biochemistry", [("biochemistry", "1A · Proteins and amino acids"), ("bio-biochem", "1A · Proteins and amino acids")]),
    "1B · Gene to protein": ("biochemistry", [("biochemistry", "1B · Gene to protein"), ("bio-biochem", "1B · Gene to protein")]),
    "1C · Heritable information & genetic diversity": ("biology", [("biology", "1C · Heritable information & genetic diversity"), ("bio-biochem", "1C · Heritable information & diversity")]),
    "1D · Bioenergetics and fuel metabolism": ("biochemistry", [("biochemistry", "1D · Bioenergetics and fuel metabolism"), ("bio-biochem", "1D · Bioenergetics and fuel metabolism")]),
    "2A · Assemblies of molecules, cells, and cell groups": ("biology", [("biology", "2A · Assemblies of molecules, cells, and cell groups"), ("bio-biochem", "2A · Assemblies of molecules, cells, cell groups")]),
    "2B · Prokaryotes and viruses": ("biology", [("biology", "2B · Prokaryotes and viruses"), ("bio-biochem", "2B · Prokaryotes and viruses")]),
    "2C · Cell division, differentiation, specialization": ("biology", [("biology", "2C · Cell division, differentiation, specialization"), ("bio-biochem", "2C · Division, differentiation, specialization")]),
    "3A · Nervous and endocrine systems": ("biology", [("biology", "3A · Nervous & endocrine coordination"), ("bio-biochem", "3A · Nervous and endocrine systems")]),
    "4A · Motion, forces, work, energy, equilibrium": ("physics", [("physics", "4A · Motion, forces, work, energy, equilibrium"), ("chem-phys", "4A · Motion, forces, work, energy, equilibrium")]),
    "4B · Fluids for circulation and gas exchange": ("physics", [("physics", "4B · Fluids, circulation, gas exchange"), ("chem-phys", "4B · Fluids for circulation and gas exchange")]),
    "4C · Electrochemistry and electrical circuits": ("physics", [("physics", "4C · Electrochemistry and circuits"), ("chem-phys", "4C · Electrochemistry and electrical circuits")]),
    "4D · Light and sound interacting with matter": ("physics", [("physics", "4D · Light and sound with matter"), ("chem-phys", "4D · Light and sound interacting with matter")]),
    "4E · Atoms, nuclear decay, electronic structure": ("chemistry", [("physics", "4E · Atoms and electronic structure"), ("chem-phys", "4E · Atoms, nuclear decay, electronic structure")]),
    "5A · Unique nature of water and its solutions": ("chemistry", [("chemistry", "5A · Water and its solutions"), ("chem-phys", "5A · Unique nature of water and its solutions")]),
    "5B · Molecules and intermolecular interactions": ("chemistry", [("chemistry", "5B · Molecules and intermolecular interactions"), ("chem-phys", "5B · Molecules and intermolecular interactions")]),
    "5C · Separation and purification methods": ("chemistry", [("chemistry", "5C · Separation and purification methods"), ("chem-phys", "5C · Separation and purification methods")]),
    "5D · Biologically relevant molecules": ("chemistry", [("chemistry", "5D · Biologically relevant molecules"), ("chem-phys", "5D · Biologically relevant molecules")]),
    "5E · Chemical thermodynamics and kinetics": ("chemistry", [("chemistry", "5E · Chemical thermodynamics and kinetics"), ("chem-phys", "5E · Chemical thermodynamics and kinetics")]),
}

# instance (subject, title) → canonical title
TO_CANON = {
    (subj, inst): canon for canon, (_, insts) in MERGES.items() for subj, inst in insts
}

# Hand-reviewed re-homing for questions whose `chapter` references a
# note-bucket title that never matched an outline item (content reviewed,
# not matched): (question id → canonical chapter title).
QUESTION_REHOME = {
    "bioc-7": "1A · Proteins and amino acids",  # competitive inhibitor → enzymes live in 1A
    "bch-8": "1A · Proteins and amino acids",   # competitive inhibition
    "bch-9": "1D · Bioenergetics and fuel metabolism",  # glycolysis net ATP
    "quan-5": "Data Interpretation",            # median (basic statistics)
    "quan-6": "Fundamental Operations",         # ratio arithmetic
}


def slugify(title: str) -> str:
    raw = re.sub(r"[^a-zA-Z0-9一-鿿]+", "-", title).strip("-").lower()
    return raw[:48] or "ch"


def main() -> None:
    report: list[str] = []

    # ---- collect instances ------------------------------------------------
    subjects = {s["slug"]: s for s in content.subjects()}
    kinds = content.store()["subject_kinds"]
    instances: dict[tuple[str, str], dict] = {}
    for slug, subject in subjects.items():
        for group in subject.get("chapters") or []:
            for it in group.get("items") or []:
                instances[(slug, it["title"])] = {
                    "subject": slug,
                    "title": it["title"],
                    "points": list(it.get("points") or []),
                    "notes": list(content.notes_for(slug, it["title"])),
                    "exams": it.get("exams") or [],
                }

    canon_titles = {c for c in MERGES}
    merged_insts = set(TO_CANON)

    # ---- build unique chapters -------------------------------------------
    chapters: dict[str, dict] = {}
    used_slugs: set[str] = set()

    def unique_slug(title: str) -> str:
        base = slugify(title)
        s, n = base, 2
        while s in used_slugs:
            s = f"{base}-{n}"
            n += 1
        used_slugs.add(s)
        return s

    # merged groups first
    for canon, (discipline, insts) in MERGES.items():
        slug = unique_slug(canon)
        points, notes = [], []
        for subj, inst_title in insts:
            inst = instances[(subj, inst_title)]
            for p in inst["points"]:
                if p not in points:
                    points.append(p)
            for n in inst["notes"]:
                if n not in notes:
                    notes.append(n)
        chapters[slug] = {
            "id": slug,
            "title": canon,
            "discipline": discipline,
            "exams": ["NMAT", "MCAT"],
            "points": points,
            "notes": notes,
            "practice": [],
        }
        report.append(
            f"MERGE  {canon}\n       discipline={discipline} "
            f"points {sum(len(instances[s,t]['points']) for s,t in insts)}→{len(points)} "
            f"notes {sum(len(instances[s,t]['notes']) for s,t in insts)}→{len(notes)}"
        )

    # single-instance chapters
    for (subj, title), inst in instances.items():
        if (subj, title) in merged_insts:
            continue
        slug = unique_slug(title)
        exams = ["NMAT", "MCAT"] if kinds.get(subj) == "shared" else (["NMAT"] if kinds.get(subj) == "nmat" else ["MCAT"])
        chapters[slug] = {
            "id": slug,
            "title": title,
            "discipline": subj,
            "exams": exams,
            "points": inst["points"],
            "notes": inst["notes"],
            "practice": [],
        }
    report.append(f"\nunique chapters: {len(chapters)} (instances in: {len(instances)})")

    # ---- attach practice to chapters --------------------------------------
    title_to_slug = {c["title"]: s for s, c in chapters.items()}
    unassigned = []
    for slug_subj, items in content.store()["practice"].items():
        for q in items:
            ch_title = (q.get("chapter") or "").strip()
            if q.get("id") in QUESTION_REHOME:
                ch_title = QUESTION_REHOME[q["id"]]
            target = None
            if ch_title:
                if ch_title in title_to_slug:
                    target = title_to_slug[ch_title]
                else:
                    # resolve via merge table instance titles
                    target = None
                    for (s, inst_t), canon in TO_CANON.items():
                        if inst_t == ch_title:
                            target = title_to_slug[canon]
                            break
                    if target is None:
                        # fuzzy within same subject's outline
                        for s, c in chapters.items():
                            if c["discipline"] == slug_subj and (
                                ch_title.lower() in c["title"].lower()
                                or c["title"].lower() in ch_title.lower()
                            ):
                                target = s
                                break
            if target is None:
                unassigned.append((slug_subj, q.get("id"), ch_title))
                continue
            chapters[target]["practice"].append(
                {
                    "id": q["id"],
                    "q": q.get("q"),
                    "choices": q.get("choices") or {},
                    "answer": q.get("answer"),
                    "explain": q.get("explain"),
                    "chapter": chapters[target]["title"],
                }
            )
    report.append(f"practice assigned: {sum(len(c['practice']) for c in chapters.values())} / unassigned: {len(unassigned)}")
    for u in unassigned:
        report.append(f"  UNASSIGNED: {u}")

    # ---- write chapters/ ---------------------------------------------------
    chap_dir = CONTENT / "chapters"
    chap_dir.mkdir(exist_ok=True)
    for slug, c in chapters.items():
        (chap_dir / f"{slug}.yml").write_text(
            yaml.safe_dump(c, allow_unicode=True, sort_keys=False, width=100),
            encoding="utf-8",
        )

    # ---- stage new subjects (reference lists) to /tmp -----------------------
    inst_to_slug = {}
    for (subj, title), canon in TO_CANON.items():
        inst_to_slug[(subj, title)] = next(s for s, c in chapters.items() if c["title"] == canon)
    for (subj, title) in instances:
        if (subj, title) in merged_insts:
            continue
        inst_to_slug[(subj, title)] = next(s for s, c in chapters.items() if c["title"] == title)

    staged = Path("/tmp/new_subjects")
    staged.mkdir(exist_ok=True)
    for slug, subject in subjects.items():
        doc = {k: v for k, v in subject.items() if k != "chapters"}
        groups = []
        for group in subject.get("chapters") or []:
            refs = [inst_to_slug[(slug, it["title"])] for it in group.get("items") or []]
            groups.append({"heading": group.get("heading", ""), "chapters": refs})
        doc["chapters"] = groups
        (staged / f"{slug}.yml").write_text(
            yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=100),
            encoding="utf-8",
        )

    # ---- stage new units.yml -------------------------------------------------
    units_doc = yaml.safe_load((CONTENT / "units.yml").read_text(encoding="utf-8"))
    for proj in units_doc["projects"].values():
        for u in proj["units"]:
            codes = u.pop("chapters", None)
            if codes is None:
                continue
            refs = []
            src = u["source"]
            for (s, t), sl in inst_to_slug.items():
                if s != src:
                    continue
                if codes and not any(t == c or t.startswith(c + " ·") for c in codes):
                    continue
                refs.append(sl)
            u["chapters"] = refs
    Path("/tmp/new_units.yml").write_text(
        yaml.safe_dump(units_doc, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )

    Path("/tmp/migration_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    print(f"\nchapters/ written: {len(chapters)} files")
    print("staged: /tmp/new_subjects/*.yml, /tmp/new_units.yml (swap in with the reader switch)")


if __name__ == "__main__":
    main()
