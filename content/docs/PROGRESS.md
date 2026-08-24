# Tutorial Fill Progress (content/tutorials)

> 72 unique chapters (unified library) · **2 published tutorials** (Biology · ch 1–2).
   Update this file **together with** every chapter you publish.

Legend: **✅ Published** · 🟨 Drafting · ⬜ Not started

## Production plan — Biology unit first (user order: sequential)

Write the 13 Biology-unit chapters in unit-list order. Each chapter:
sources consulted → full template (sections+checks, example+distractors,
mnemonics, maps, passage, review questions, exam map, further reading) →
`validate_content` → `refresh_manifest` → flip ✅ here → commit (videos parked).

| # | Chapter (slug) | Status | OpenStax consulted |
|---|---|---|---|
| 1 | Unity and Diversity of Life ([tutorial](tutorials/biology/unity-and-diversity-of-life.yml)) | ✅ Published | Ch 1 The Study of Life; Ch 12 Diversity; Ch 20 Phylogenies |
| 2 | Cells and Cellular Processes ([tutorial](tutorials/biology/cells-and-cellular-processes.yml)) | ✅ Published | Ch 4 Cell Structure; Ch 5 Membranes; Ch 7 Cellular Respiration |
| 3 | Genetics (—) | ⬜ Not started | Ch 11 Meiosis; Ch 12 Mendel; Ch 13 Inheritance; Ch 14 DNA |
| 4 | The World of Plants and Animals (—) | ⬜ Not started | Ch 25–26 Plants; Ch 27–29 Animal diversity |
| 5 | Development (—) | ⬜ Not started | Reproduction & development chapters |
| 6 | Life Processes: Regulation and Homeostasis (—) | ⬜ Not started | Homeostasis / nervous / endocrine chapters |
| 7 | Organisms and Their Environment (—) | ⬜ Not started | Ecology: populations, communities, ecosystems |
| 8 | 1C · Heritable information & genetic diversity (—) | ⬜ Not started | Ch 14 DNA; Ch 16 Expression; Ch 19 Populations |
| 9 | 2A · Assemblies of molecules, cells, and cell groups (—) | ⬜ Not started | Ch 4 Cell Structure; tissues overview |
| 10 | 2B · Prokaryotes and viruses (—) | ⬜ Not started | Ch 21 Viruses; Ch 22 Prokaryotes |
| 11 | 2C · Cell division, differentiation, specialization (—) | ⬜ Not started | Ch 10 Cell Reproduction; cell-cycle control |
| 12 | 3A · Nervous and endocrine systems (—) | ⬜ Not started | Nervous & endocrine system chapters |
| 13 | 3B · Main organ systems (—) | ⬜ Not started | Circulatory / respiratory / digestive / immune / excretory |

## All units (chapter counts)

- **NMAT**: Verbal (2), Inductive Reasoning (3), Quantitative (3), Perceptual Acuity (3), Biology (13), Chemistry (10), Physics (10), Behavioral & Social (7)
- **MCAT**: Chemical Foundations (6), Physical Foundations (4), Biology (6), Biochemistry (3), Psychology (6), Sociology (6), CARS (3)

## How to update

1. Write the chapter from `docs/TUTORIAL_TEMPLATE.md` (park videos).
2. `python manage.py validate_content` + `refresh_manifest`.
3. Flip this table's status to ✅ and link the file.
4. Commit the tutorial + manifest + this file together.
