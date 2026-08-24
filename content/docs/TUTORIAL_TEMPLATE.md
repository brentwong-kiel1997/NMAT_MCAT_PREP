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

# c) Concept maps / pathways — monospace arrow flow lines (text only)
maps:
  - title: Where diversity comes from
    lines:
      - "mutation → new alleles"
      - "recombination → new combinations"
      - "   └→ variation → natural selection → adaptation → speciation"

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