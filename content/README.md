# NMAT & MCAT Curriculum Content Pack

A file-based curriculum library for two medical-school entrance exams:

- **NMAT** — National Medical Admission Test (Philippines, administered by CEM)
- **MCAT** — Medical College Admission Test (USA, administered by AAMC)

Everything here is plain YAML, in English, version-controlled, and organized so
that any application can read it without a database or build step. Files are
the single source of truth — there is no generated artifact to keep in sync.

## What's inside

| Path | Contents | Scale |
| --- | --- | --- |
| `catalog.yml` | Subject ordering per exam kind, formula-sheet order, subject display labels | 13 labels |
| `exams/nmat.yml` | NMAT structure: parts, timing, item counts, Part-2 subject links | 2 parts |
| `exams/mcat.yml` | MCAT structure: sections, timing, discipline mix | 4 sections |
| `subjects/*.yml` | One file per subject: positioning, exam roles, chapter outline | 13 subjects |
| `notes/*.yml` | Chapter note buckets (high-yield bullets) — canonical, see Overlay below | 545 bullets |
| `practice/*.yml` | Multiple-choice questions (4 options, answer, explanation) | 116 items |
| `diseases/*.yml` | Disease articles (enrichment reading, not a clinical syllabus) | 8 articles |
| `materials/glossary.yml` | Terms with definitions and subject tags | 105 terms |
| `materials/formulas.yml` | Formula sheets grouped by subject | 108 entries |
| `materials/tips.yml` | Exam strategy tips (NMAT / MCAT / BOTH) | 21 tips |
| `materials/paths.yml` | Suggested study paths with step links | 7 paths |
| `materials/checklists.yml` | Exam-day and study checklists | 3 lists |
| `tutorials/<subject>/<chapter>.yml` | Full textbook chapters: overview, teaching sections, tables, worked examples, key points, pitfalls, exam map, sources | 1 → 90 (growing) |
| `docs/TUTORIAL_TEMPLATE.md` | Authoring template + field reference for new chapters | — |
| `MANIFEST.json` | Counts and SHA-256 hashes of every file, for integrity checks | — |

## Editing rules

**Stable identifiers.** Three kinds of keys are referenced by learner-progress
records and must not change casually:

1. `slug` fields (subjects, diseases, paths)
2. Question `id` values (globally unique, e.g. `bio-1`)
3. The order and titles of chapter outline items — chapter IDs are derived as
   `ch-{index}-{slugified-title}` (index counts continuously across groups
   within a subject). Renaming a chapter title or reordering items changes its
   ID and orphans recorded progress.

**Bilingual history.** This pack was originally bilingual (Chinese/English) and
is now English-only. Do not reintroduce paired-language fields; write plain
English scalars.

**Ordering is meaningful.** List order in `notes/`, `practice/`, `glossary`,
`formulas`, `tips`, and `paths` files is display order. Do not sort entries
when editing.

**Escaping.** Use `allow_unicode: false`-safe plain text. Strings containing
`: ` (colon + space) must be quoted in YAML.

## Schema highlights

A subject file (`subjects/biology.yml`):

```yaml
slug: biology
kind: shared            # shared | nmat | mcat
name: Biology
summary: Cells, genetics, homeostasis...
exams: [NMAT, MCAT]
exam_notes:
  NMAT: How CEM frames this subject...
  MCAT: How AAMC frames this subject...
chapters:               # outline; order defines chapter IDs
  - heading: NMAT · CEM BOI chapters
    items:
      - title: Unity and Diversity of Life
        points:
          - Shared traits: cells, metabolism, homeostasis, reproduction, adaptation
```

A practice item (`practice/biology.yml`):

```yaml
- id: bio-1
  q: Which organelle packages proteins for secretion?
  choices:
    A: Rough endoplasmic reticulum
    B: Golgi apparatus
    C: Lysosome
    D: Peroxisome
  answer: B
  explain: The Golgi apparatus modifies, sorts, and packages proteins...
  chapter: Cells and Cellular Processes
```

## Tutorial chapters

Full textbook chapters live in `tutorials/<subject-slug>/<title-slug>.yml`.
A chapter is keyed to exactly one outline chapter (`subject` + `chapter`
must match an item in `subjects/`), so progress records and navigation stay
consistent. The URL shape is `/tutorials/<subject>/<chapter-id>/`, where
`chapter-id` is the derived `ch-N-slugified-title` value from the outline.

Each chapter file carries the fields:

| Field | Purpose |
| --- | --- |
| `overview` | Why this chapter matters, what each exam tests with it, prerequisites |
| `sections` | Teaching body: `heading` + `body` (paragraphs) + optional `table` (`caption`, `headers`, `rows`) |
| `examples` | Worked examples: `prompt` + `solution` steps + optional `answer` |
| `key_points` | Must-not-miss bullet takeaways |
| `pitfalls` | Common wrong answers and misconceptions |
| `exam_map` | Map of `NMAT:` / `MCAT:` — how each exam tests this chapter |
| `sources` | Every reference cited: `ref` (an id from `SOURCES.yml`), `used` (chapters/sections), `relation` |

Inline prose supports two markers (everything else is plain text):
`**bold**` for key terms and `==mark==` for must-not-miss exam takeaways.
Facts and structure may follow the referenced sources, but prose must stay
original — the content pack maintains its own copyright, and `sources`
records exactly what was consulted and how.

A fill-in template with every field documented is in
[`docs/TUTORIAL_TEMPLATE.md`](docs/TUTORIAL_TEMPLATE.md); a complete worked
example is `tutorials/biology/unity-and-diversity-of-life.yml`. The
validation gate checks that every tutorial keys to a real outline chapter
and cites only registered sources, so writing a chapter is: copy the
template → fill it → run `validate_content` → `refresh_manifest` → commit.

## Note overlay (read-time copies)

Note files are canonical: each subject owns only its own bullets. Some shared
subject pages intentionally show another subject's notes. Consumers should
apply this overlay when reading (later sources override per chapter title):

```
biology      <- biology + bio-biochem
chemistry    <- chemistry + chem-phys{titles starting 5 or 4E}
physics      <- physics   + chem-phys{titles starting 4}
chem-phys    <- physics(staged) + chemistry(staged) + chem-phys
bio-biochem  <- biology(staged) + biochemistry + bio-biochem
psych-soc    <- behavioral-social + psych-soc
```

After the overlay the corpus renders as 150 chapter buckets / 790 bullets.

## Integrity checks

`MANIFEST.json` records per-collection counts and a SHA-256 per file. After
editing, regenerate it (consumers ship a `refresh_manifest` command) and commit
it together with your changes. Consumers typically verify, before serving:

- manifest hashes match the files on disk
- expected collection counts (see manifest)
- question ids unique per subject; `answer` is one of the choice keys
- every stored learner chapter-id still resolves to an outline item

## License

This content pack is licensed **CC BY-NC-SA 4.0** — see
[LICENSE.md](LICENSE.md) in this directory. The surrounding project code is
MIT-licensed (repository root `LICENSE`).

## Sourcing disclaimer

Outlines follow the public exam blueprints (CEM's Board-of-Interior guidance
for NMAT, AAMC's "What's on the MCAT" foundational concepts). Percentages are
study-prep approximations, not official figures. Practice questions are
original items written for this pack, not past-paper reproductions. Disease
articles are enrichment reading for mechanism intuition, not a clinical
syllabus.
