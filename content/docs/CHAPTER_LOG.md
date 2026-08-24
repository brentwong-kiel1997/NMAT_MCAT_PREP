# Chapter development log

One entry per tutorial chapter, appended top-first. Each entry records what
was actually done to get the chapter from outline item to published page:
decisions, source verification, schema notes, YAML landmines hit, the
rendering pipeline it exercised, and the docs it produced. Keep entries
factual and short enough to scan — this is the audit trail and the reference
for how to run the same process again.

---

## 001 · Unity and Diversity of Life (biology)

**Status:** ✅ Published · URL
`/tutorials/biology/ch-1-unity-and-diversity-of-life/`
**Date:** 2026-08-24

### What was done

1. **Chosen as the first tutorial chapter.** User picked the order
   (start with Biology, full-textbook depth, KaTeX for formulas) and this
   is Biology's first outline item — also the entry-point chapter with no
   prerequisites, so it doubles as the authoring pilot.

2. **Verified the primary source on the live site.** Web search claimed
   OpenStax was CC BY 4.0; fetching the official page showed Biology 2e is
   actually **CC BY-NC-SA 4.0** (publish 2018-03-28, PDF updated
   2025-07-31, ISBN 978-1-947172-52-4). That single check changed the
   production strategy: chapters **consult** OpenStax for facts and
   coverage only, all prose stays original, so the pack keeps its own
   copyright and nothing propagates the ShareAlike.

3. **Registered the source.** `content/SOURCES.yml` records three sources
   (OpenStax Biology 2e, AAMC What's on the MCAT, CEM NMAT description)
   with edition, access date, license, and `relation: consulted`.

4. **Fixed the chapter schema.** Final fields (validated by the gate):
   `subject, chapter, title, overview, sections[heading/body/table],
   examples, key_points, pitfalls, exam_map{NMAT,MCAT}, sources[{ref, used,
   relation}]`. A `sources` block is mandatory per chapter.

5. **Wrote the chapter** (full-textbook depth, EN): overview, five teaching
   sections (definition of life, levels/organization, taxonomy & three
   domains incl. comparison table, molecular unity, diversity & tree
   reading), one worked example, key points, pitfalls, exam map, sources.
   Inline markup uses `**bold**` and `==mark==` (the `rich` filter), which
   the renderer turns into `<strong>`/`<mark>`.

6. **Hit and fixed three YAML landmines** (all now in the writing rules):
   - raw `: ` inside a plain scalar (e.g. `Life's checklist: order…`)
     parses as a mapping key → wrap such values in `> -`/quotes;
   - ASCII colons inside list items are legal but need consistent quoting
     when the value also contains a space after the colon;
   - table cells containing `, `+multiple values must be quoted as one
     string (a quoted "row" with a stray token desyncs the column count).

7. **Rendering pipeline (already in the repo, exercised by this chapter):**
   - `portal/content.py` — `tutorials` section of the store; `tutorial_for`
     (by subject+chapter title) and `tutorial_titles` (written set);
   - `portal/views.py` `tutorial_detail` — resolves subject, matches the
     outline `chapter_id`, attaches `source_info` per citation, computes
     prev/next among written chapters, picks the back-link per exam kind;
   - `config/urls.py` — `tutorials/<slug>/<chapter_id>/`;
   - `portal/templates/portal/tutorial_detail.html` — on-page TOC, section
     blocks with tables, worked-example steps, key-point grid, pitfalls,
     exam-map cards, source list, prev/next nav;
   - `portal/templatetags/rich.py` — the inline-markup filter.

8. **Extended the validation gate** (`validate_content.py`): every tutorial
   must key to a real outline chapter title of an existing subject and cite
   only registered `SOURCES.yml` ids; sections need heading+body.

9. **Documented the process for reuse**:
   - `content/docs/TUTORIAL_TEMPLATE.md` — fill-in skeleton with field docs,
     gate rules, file naming, when-to-skip matrix, progress contract;
   - `content/docs/PROGRESS.md` — generated 90-chapter table, this chapter
     marked published (1/90);
   - `content/README.md` — "Tutorial chapters" section + inventory rows;
   - root `README.md` — feature line + progress link.

### Decisions worth keeping

- **Original prose, consulted sources.** Facts and outline structure follow
  the references; sentences never copy OpenStax/AAMC/CEM. License math:
  consulting + original writing keeps `content/` under CC BY-NC-SA without
  importing OpenStax's ShareAlike into unrelated terms.
- **`chapter` binds to the outline title byte-for-byte**; the file name is
  informational. Renaming a title or reordering outline items changes
  `chapter_id`s and orphans learner progress.
- **Depth = full-textbook** for this pilot (user's call): intuition →
  mechanism → pitfalls per section, one worked example minimum.

### Open items for next chapters

- KaTeX was approved but only lands with the next chapter that has real
  formulas (biology ch. 2 will not; chem/physics will) — the `rich` filter
  deliberately has no math syntax yet.
- Progress row must be flipped to ✅ and the file linked in `PROGRESS.md`
  whenever a chapter ships (this entry is the checked pattern for #002).