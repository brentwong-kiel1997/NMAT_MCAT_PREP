# Restructure plan: unified chapter library (总库 → 合并 → 标注)

**Status: PROPOSED — awaiting approval. Do not execute yet.**

## Why

The current data layer stores chapters per exam-subject, so the same
chapter exists as multiple instances (90 instances / 78 unique titles, plus
8 near-duplicate titles). Consequences, verified by audit:

1. Same chapter, two different `chapter_id`s (physics/4A = `ch-6-4a-…`,
   chem-phys/4A = `ch-1-4a-…`) — cross-exam progress is silently broken
   for those chapters.
2. Contradictory exam annotations for the same content (physics/4A shows
   `[NMAT, MCAT]`, chem-phys/4A shows `[MCAT]`) because annotation derives
   from the SUBJECT's kind, not the content.
3. The note overlay (245 copied bullets) exists only to paper over this.

## Target model

```
STEP 1  chapter library (one instance per chapter)
        content/chapters/<slug>.yml
          id, title, discipline, exams[], points[], notes bullets,
          (tutorials already live at tutorials/<subject>/<slug>.yml)

STEP 2  merge — subjects become ordered REFERENCE lists
        subjects/*.yml → chapters: [{ref: <slug>}, …] under group headings
        units.yml     → references chapter slugs (no more prefix filters)
        overlay       → retired (merged chapters own all their bullets)

STEP 3  annotate
        each chapter carries exams: [NMAT, MCAT] | [NMAT] | [MCAT]
        progress key = chapter slug (globally unique) → cross-project
        progress is exact, not mapped
```

## Merge verdicts — reviewed chapter by chapter, not by code matching

18 groups reviewed side by side (points + notes). All 18 are the same
chapter; 6 are word-for-word duplicates (overlay copies), 12 are
complementary (union on merge). None is a false positive.

**A. Duplicates — dedupe, keep one copy (6)**

| Chapter | Copies found | Keep |
|---|---|---|
| 2B · Prokaryotes and viruses | biology = bio-biochem (6/6 identical) | one set |
| 4A · Motion, forces, work, energy, equilibrium | physics = chem-phys (4/4) | one set |
| 5B · Molecules and intermolecular interactions | chemistry = chem-phys (4/4) | one set |
| 5C · Separation and purification methods | chemistry = chem-phys (5/5) | one set |
| 5D · Biologically relevant molecules | chemistry = chem-phys (5/5) | one set |
| 5E · Chemical thermodynamics and kinetics | chemistry = chem-phys (5/5) | one set |

**B. Complementary — merge with union of points/notes (12)**

| Canonical title (kept) | Sides merged | Content union |
|---|---|---|
| 1A · Proteins and amino acids | biochemistry (6) + bio-biochem (7) | basics + MCAT depth |
| 1B · Gene to protein | biochemistry (6) + bio-biochem (7) | central dogma + regulation |
| 1C · Heritable information & genetic diversity | biology (6) + bio-biochem (6) | replication/meiosis + CRISPR/aneuploidy |
| 1D · Bioenergetics and fuel metabolism | biochemistry (7) + bio-biochem (6) | pathways + regulation |
| 2A · Assemblies of molecules, cells, and cell groups | biology (5) + bio-biochem (6) | hierarchy + membrane/tissue |
| 2C · Cell division, differentiation, specialization | biology (6) + bio-biochem (4) | cycle/stem + MPF/apoptosis |
| 3A · Nervous and endocrine systems | biology (6) + bio-biochem (4) | signaling + HPA/BBB |
| 4B · Fluids for circulation and gas exchange | physics (6) + chem-phys (4) | equations + concepts |
| 4C · Electrochemistry and electrical circuits | physics (6) + chem-phys (4) | circuits + electrochem |
| 4D · Light and sound interacting with matter | physics (6) + chem-phys (5) | optics/sound + imaging |
| 4E · Atoms, nuclear decay, electronic structure | physics (4) + chem-phys (5) | spectra + half-life |
| 5A · Unique nature of water and its solutions | chemistry (6) + chem-phys (4) | H-bond/pH + buffers |

**C. Deliberately NOT merged**

- behavioral-social's coarse chapters (FC6–FC10) vs psych-soc's fine
  chapters (6A–10A): different granularity of the same idea — the coarse
  ones are NMAT-facing summaries, the fine ones are per content-category
  MCAT chapters. Both stay; each keeps its own exam annotation
  (`[NMAT]`… behavioral FC6-10 actually serve BOTH — they mirror MCAT
  foundations, so they will be annotated `[NMAT, MCAT]` as review
  chapters, with the fine chapters as the MCAT deep path).
- All no-code chapters (NMAT BOI titles, CARS skills, Part-1 subjects) are
  naturally unique — no action.

## Resulting library

- 90 instances → **72 unique chapters** (18 merges).
- Every chapter: `exams` from actual usage — merged groups → `[NMAT,
  MCAT]`; NMAT-only (Part 1, NMAT BOI titles) → `[NMAT]`; MCAT-only
  (CARS skills, psych-soc fine chapters not mirrored by NMAT titles,
  remaining bio-biochem) → `[MCAT]`.
- Practice questions: both sides' items follow the chapter (deduped by
  question id; ids are already globally unique).
- Tutorials: file names already equal chapter slugs — `tutorial_for`
  re-keys to chapter id, the existing chapter-001 file moves to
  `chapters/biology/unity-and-diversity-of-life` linkage unchanged.

## New IDs

`slug(title)` — same derivation as tutorial filenames today, e.g.
`4a-motion-forces-work-energy-equilibrium`. Stable, readable, no index
component (index was the drift source). Progress migration: the user DB
holds only 6 junk test rows — drop them; no real progress to carry.

## Execution steps (each a deployable commit)

1. **C1 generator**: script builds `content/chapters/` from current data
   applying the verdict table above (union/dedupe), writes
   `subjects/*.yml` as reference lists, rewrites `units.yml` refs, migrates
   `notes/`+`practice/` ownership into chapters, deletes overlay logic
   from `portal/content.py` (reader rebuilt around chapter store). Diff
   the generated files by hand before commit.
2. **C2 reader/views**: content.py resolves subjects/units from chapter
   refs; chapter_id = slug everywhere; validate_content updated (unique
   chapter ids, ref integrity, exams ∈ {NMAT, MCAT}); crawl gate.
3. **C3 cleanup**: junk progress rows dropped; docs (README, content
   README) rewritten to the new model; CHAPTER_LOG entry.

## Risks & mitigations

- Biggest risk is silent content loss in union/dedupe → the generator
  emits a merge report (counts in vs out per chapter); parity check:
  total bullets before == after (790+245 overlay copies reconciled by
  design); review diff before commit.
- chapter_id change orphans progress → only junk rows exist; they are
  dropped explicitly in C3.
- Rollback: pure file change; `git revert` restores the previous model
  (poller redeploys).
