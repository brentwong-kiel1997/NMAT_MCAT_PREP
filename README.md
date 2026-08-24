# Gabay — NMAT & MCAT Study Companion

A single-learner study site for two medical-school entrance exams:

- **NMAT** — National Medical Admission Test (Philippines, administered by CEM)
- **MCAT** — Medical College Admission Test (USA, administered by AAMC)

Gabay organizes the full journey: curriculum outlines mapped to the official
exam blueprints, teaching chapters, high-yield notes, practice questions with
explanations, a materials desk (glossary / formulas / exam tips / study paths /
checklists), a disease library for mechanism reading, per-chapter progress
tracking, and an AI study coach grounded in whichever chapter you are reading.

All content and UI are English. The curriculum itself is plain YAML in
`content/` — no database involved.

## Features

- **13 subjects** covering NMAT Part 1 & 2 and all four MCAT sections, with
  shared science subjects merged between the two exams
- **90-chapter outline** mapped to the CEM syllabus and AAMC foundational
  concepts / content categories
- **Tutorial chapters** (growing one by one): overview, teaching sections,
  worked examples, key points, pitfalls, and per-exam mapping — each citing
  its sources
- **790 high-yield note bullets**, 116 practice MCQs with explanations
- **Materials desk**: 105-term glossary with search, 108 formulas in per-subject
  sheets, exam tips, study paths, and checklists
- **Progress tracking**: per-chapter completion and practice attempts stored
  per learner account
- **AI study coach** (MiniMax-M3): explain / quiz / grade modes constrained to
  the current subject's outline
- **File-based content**: edit YAML, push, done — with structural validation
  as a deploy gate

## Quickstart

Requirements: Python 3.12+.

```bash
git clone https://github.com/brentwong-kiel1997/NMAT_MCAT_PREP.git
cd NMAT_MCAT_PREP
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# keep runtime data (user DB) inside the checkout
export GABAY_RUNTIME_DIR="$PWD/runtime"

.venv/bin/python manage.py migrate
.venv/bin/python manage.py ensure_admin --username admin --password <pick-one>
.venv/bin/python manage.py runserver
```

Then open http://127.0.0.1:8000/ and sign in with the admin account.

### Study coach (optional)

The tutor needs a MiniMax API key. Copy `.env.example` to `.env` and fill in
`MINIMAX_API_KEY` (the file is gitignored; `python manage.py env_status`
verifies it is found). Without a key everything else works — only the coach
is disabled.

## The content pack

Everything taught lives in `content/` as version-controlled YAML — subjects,
notes, questions, glossary, formulas, tips, paths, checklists, diseases, and
the exam structures — described standalone in
[`content/README.md`](content/README.md). Source attribution (edition, access
date, license, how each source was used) is tracked in
[`content/SOURCES.yml`](content/SOURCES.yml).

To edit curriculum content:

```bash
# edit content/**/*.yml, then:
.venv/bin/python manage.py validate_content    # structural self-check
.venv/bin/python manage.py refresh_manifest    # update MANIFEST.json (commit it too)
```

Stability rules (subject slugs, question ids, chapter order — they key the
progress records) are documented in the content README.

## Project layout

```
content/        curriculum content pack (YAML, standalone)
portal/         Django app: views, templates, static, content reader
config/         Django project settings
scripts/        reference deployment tooling (see DEPLOYMENT notes)
manage.py       standard Django entry point
```

## Sources & license

Tutorial chapters and practice items are original writing for this project.
External references (OpenStax textbooks, AAMC and CEM public outlines) are
consulted for facts and structure only, never copied — see the `relation`
field in `content/SOURCES.yml`. Exam names are trademarks of their respective
owners; this project is not affiliated with CEM or the AAMC.
