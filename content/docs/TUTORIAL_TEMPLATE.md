# Tutorial chapter authoring template

Copy this skeleton to `content/tutorials/<subject>/<chapter-slug>.yml`, fill
every field, then run `python manage.py validate_content` and
`python manage.py refresh_manifest`. A complete worked example is
`content/tutorials/biology/unity-and-diversity-of-life.yml`.

Rules that the validation gate enforces automatically:

- `subject` must be an existing subject slug; `chapter` must be one of that
  subject's outline chapter titles (byte-identical, including punctuation).
- Every `sources[].ref` must exist in `content/SOURCES.yml`.
- Every section needs a `heading` and a non-empty `body`.

Authoring rules that the gate does NOT enforce, keep them anyway:

- Original prose only. Sources are consulted for facts and structure — never
  paste or lightly rewrite their sentences (see the `relation` field and the
  note in `SOURCES.yml`).
- Use `**bold**` for key terms and `==mark==` for must-not-miss takeaways;
  everything else is plain text.
- Author for one exam-specific pass over the outline: NMAT Part 2 depth is
  introductory college; MCAT demands passage-style reasoning on foundational
  science.

```yaml
subject: <subject-slug>
chapter: "<exact outline chapter title>"
title: "<short display title — may equal chapter>"

overview: >-
  Two to five sentences: why this chapter matters, what each exam does with
  it (cite the exam map below), and any prerequisites from earlier chapters.

sections:
  - heading: "Section 1 — main concept"
    body:
      - >-
        Paragraph 1 of the teaching body. Explain intuition first, then
        mechanism, then common pitfalls. Use **bold** sparingly for key
        terms and ==mark== for takeaways.

      - >-
        Paragraph 2 — continue the explanation, add an example, or contrast
        with a closely related concept (the NMAT/MCAT favorite contrast).

    # optional: include when the section has a comparative table
    table:
      caption: "Optional one-line caption"
      headers: [Column A, Column B, Column C]
      rows:
        - [value a1, value b1, value c1]
        - [value a2, value b2, value c2]

  - heading: "Section 2 — next concept"
    body:
      - "..."
    # repeat as needed (typical chapters have 4–6 sections)

examples:
  - prompt: >-
      A realistic exam-style prompt: a short passage or scenario plus the
      question being asked.
    solution:
      - "Step 1 of the worked reasoning (each step is a list item)."
      - "Step 2 — show the actual elimination/reasoning, not just the answer."
    answer: "Final answer in one sentence, why."

key_points:
  - >-
    Bullet 1 — must-not-miss takeaway 1. ==Wrap exam-critical facts like
    this==.

pitfalls:
  - "Common misconception 1, and the one-line correction."
  - "Common misconception 2, and the one-line correction."

exam_map:
  NMAT: >-
    What CEM tests here and the typical question style (recall / applied /
    companion-item). Keep NMAT's introductory-college depth in mind.
  MCAT: >-
    Which content categories this maps to (e.g. AAMC FC 1, CC 1B) and how
    passages typically use it.

sources:
  - ref: openstax-biology-2e
    used:
      - "Ch 1: The Study of Life"
    relation: consulted
  - ref: aamc-whatson-mcat
    used:
      - "Foundational Concept 1, Content Category 1B"
    relation: consulted
```

#### Extended fields (all optional, add per chapter as they earn their place)

```yaml
# a) Check yourself — 1–2 quick questions per section, answer hidden below
sections:
  - heading: "Section 1 — main concept"
    body: [...]
    check:
      - q: "Which level shows emergent properties that none of its parts have?"
        options: {A: Cell, B: Molecule, C: Atom, D: Electron}
        answer: A
        explain: "Cells are the lowest level at which all life-properties operate together."

# b) Mnemonics — short memory hooks worth capturing
mnemonics:
  - phrase: "Homology = History, Analogy = Adaptation"
    means: "Homologous structures share ancestry; analogous ones share function only."

# c) Concept maps / pathways — a vertical flow of steps (rendered with
#    arrows between steps; steps support **bold** / ==mark==)
maps:
  - title: Where diversity comes from
    steps:
      - "mutation and recombination → genetic variation"
      - "natural selection filters variation → adaptation"
      - "isolation over time → speciation"
    note: "Mutation creates new alleles; selection decides which persist."

# d) Worked-example distractors — why each wrong option is wrong (MCAT-style)
examples:
  - prompt: "..."
    solution: [...]
    answer: "..."
    distractors:
      A: "Confuses the cell with the biosphere — two levels off."
      B: "A property of populations, not of this structure."

# e) Passage — optional MCAT-style passage plus its questions
passage:
  text: >-
    One paragraph of passage-style prose the questions hang on.
  questions:
    - q: "..."
      options: {A: ..., B: ..., C: ..., D: ...}
      answer: B
      explain: "..."
      distractors:
        A: "Why A is tempting but wrong."

# f) Review questions — end-of-chapter set, AAMC-style with full analysis
review_questions:
  - q: "..."
    options: {A: ..., B: ..., C: ..., D: ...}
    answer: C
    explain: "..."
    distractors:
      A: "..."
      B: "..."
```

All five sub-blocks reuse the same question shape
(`q / options / answer / explain / distractors`). `distractors` only makes
sense for multiple-choice; omit it for conceptually-open questions.

### A section, element by element (the checklist)

Every `section` exists to teach **one concept fully**. Build each section
from this checklist — elements in **bold** are required, the rest optional
but expected when the concept calls for them:

| # | Element | YAML | What it must contain |
|---|---------|------|----------------------|
| 1 | **Title** | `heading` | The concept in plain exam language; appears in the page TOC and anchor. One concept per section — split, don't cram. |
| 2 | **Body** | `body[]` (2–4 paragraphs) | Intuition first: what is it, why care, what comes to mind. Then mechanism: how it works, step by step. Then exam angle: how a question would test it. End each paragraph the way a candidate reads it. |
| 3 | **Key terms** | `**term**` in body | Bold every term the exam asks for by name (homologous, binomial, clade). Readers scan bolds for revision. |
| 4 | **Must-not-miss** | `==takeaway==` in body | At least one per section: the single fact/relationship that is most commonly tested in this section. If a section has no such candidate, you have not found the crux yet. |
| 5 | Contrast (as needed) | a body paragraph | The classic exam discriminator: what is this NOT? Compare against its closest confusable (homology vs analogy, virus vs cell, pre-renal vs ATN). Every section should name its main confusable. |
| 6 | Table | `table` (optional) | Use when 2+ parallel items must be compared (domains, hormones, methods). 4 no more than 6 rows reads best. |
| 7 | Check yourself | `check` (1 question ideally) | One quick A–D recall or classification item on the section's crux, answer hidden below the fold. |
| 8 | Exam tag | inside body or check | One sentence (implicit or explicit) on how NMAT/MCAT would use this — recall here, reasoning there. The full exam map lives at chapter level; each section should still earn its place in it. |

A section that fills 1–5 fully is already useful; add 6–8 when the concept
has natural comparisons, a single crux worth self-testing, or a clear
exam-side usage.

### The five out-of-section blocks (short forms)

Same expectation rules for the chapter-level blocks:

- `examples` — **one per chapter minimum**: a realistic stem, explicit
  reasoning steps, and `distractors` explaining every wrong option.
- `key_points` — the revision cheat-sheet: 5–8 bullets that stand alone.
- `mnemonics` — only real hooks that stick (skip forced ones).
- `maps` — 1 per chapter when a pathway/flow benefits from a visual chain.
- `passage` — optional; include when the concept is passage-style by nature.
- `review_questions` — 4 minimum at chapter level, always with distractors
  on the choices that are actually tempting.

## File naming

Place the file at `content/tutorials/<subject>/<title-slug>.yml` where
`<title-slug>` is the chapter title lowercased, spaces → dashes (e.g.
`unity-and-diversity-of-life.yml`). The filename is informational only —
routing and identity are driven by `subject` + `chapter`, so renaming a file
never touches progress records.

### When to skip a field

| Field | Skip when |
| --- | --- |
| `overview` | never — it is the chapter's hook and prerequisites |
| `sections[].table` | the section has no comparative structure |
| `examples` | a purely conceptual chapter that benefits from none (rare — most chapters want at least one) |
| `pitfalls` | cannot think of a recurring wrong answer (usually means you have not looked — write at least two) |
| `exam_map.MCAT` | chapter belongs to NMAT-only material (unusual) |

### Progress & navigation contract

- `chapter` title changes → chapter-id changes → recorded learner progress on
  that chapter orphans. Fix titles in the outline FIRST, keep old titles only
  when progress must survive.
- The tutorial renderer shows prev/next navigation only between chapters that
  already have tutorials — partially written subjects render cleanly.