# 20-Round Comprehensive Audit Plan

Protocol per round: **audit → fix (verified findings only) → full gate (tests + validate + verify scripts) → check the box**.
Gate = `manage.py test` (75+), `validate_content`, 15/15 `verify_*` scripts, deployed & probed.
Each round's findings and fixes are summarized under its entry after it completes. Started: 2026-10-08.

## Round plan

- [x] **R1 — 10-agent full-repo adversarial sweep** — ten lenses over everything; 3-vote refute verification. *(142 agents, 42 confirmed / 30 nits / 2 refuted-of-44-raw. Criticals: tutorial pages 500'd live — missing `{% load static %}` + bad url kwarg — hotfixed with render tests. Fixed: smart sets never graded & shipped answer keys (now keyless + per-item subject + verdicts), miss SRS cards unreachable (ghost guard + grade API now accept learner cards; was inflating due-counters forever), test-out off-by-one (verdict before last score), field_test dropped from persisted plan (unscored items got scored), retake distractor letters unfolded, readiness checkmark pct missing, bank-fallback miss cards blank-front/colliding keys, finalize ~8 s → hoisted per-item deepcopies, poller staging-collision (GitHub channel dead), repo gunicorn.service drift, apkg unstable deck id, plan-cache midnight freeze, ai_drill cap-before-filter, gps/binomial model contradicted interpreter (unified), localStorage cross-account leak (namespaced), PDF drops new fields (equations/callouts/anatomy), README 32→41 passages + figures honesty, all_bank_items re-normalized per call (stamp-cached). Reviewed & dismissed with rationale: MCAT break schedule (labels verified against AAMC order). 79/79 tests, 15/15 verify, validate green; deployed `2111481`+follow-up commit.)*
- [ ] **R2 — security deep-dive** — authz matrix re-walk (every route incl. newest), secrets handling, cookie/header flags, IDOR on new models (AiQuiz/SrsCard), SSRF surface of model-test.
- [ ] **R3 — exam engine state machine** — clock drift, finalize idempotency, variant maps with A–E, field-test exclusion, break flow, crossed-state folding.
- [ ] **R4 — content validator vs bank invariants** — new fields (skill, callouts, key_equations, 2-checks rule, A–E) vs actual YAML; validator blind spots.
- [ ] **R5 — JS/frontend contract** — practice shells, test-out settlement, smart-set timer, KaTeX init guards, figure rendering, localStorage keys.
- [ ] **R6 — performance & queries** — N+1 sweep on hot views, cache key correctness (_PLAN_CACHE/_SNAPSHOTS/_BRIEF_CACHE), WAL pragmas, index coverage.
- [ ] **R7 — SRS & planner math re-derivation** — SM-2 schedules by hand, ease floors, day-boundary math under Asia/Manila, plan-task allocation.
- [ ] **R8 — AI features** — budget double-charge, cache staleness, prompt-injection surface, degradation paths, ai_drill validation.
- [ ] **R9 — deploy/CI reproducibility** — fresh-clone run (no /home/ubuntu), CI lock parity, staging swap, graceful reload, .env lookup on a cold machine.
- [ ] **R10 — data growth & pruning** — AiQuiz/ExamAttempt/ExamResponse/SrsCard growth bounds; pruning or archival strategy.
- [ ] **R11 — templates & accessibility** — aria labels, focus management in dialogs (periodic table), contrast on badges, mobile media queries.
- [ ] **R12 — YAML/schema consistency** — subjects ↔ chapters ↔ units cross-refs, catalog ordering, exam blueprint vs bank counts.
- [ ] **R13 — answer-key balance & duplicates** — bank-wide letter distribution, duplicate stems/choices, practice back-links.
- [ ] **R14 — figure/art audit** — every referenced SVG parses and matches its stem; generator determinism (regenerate → byte-identical).
- [ ] **R15 — locale/timezone edges** — Asia/Manila day boundaries (SRS due, coach daily caps, planner dates), USE_TZ storage vs localdate.
- [ ] **R16 — error paths** — 404/500 hygiene, degraded modes (no model, no data, empty banks), message leaks.
- [ ] **R17 — docs vs reality** — README/DEPLOYMENT/content-README claims vs disk (counts, features, paths).
- [ ] **R18 — test-suite honesty** — vacuous assertions, mocked-past-the-bug patterns, missing coverage on newest features.
- [ ] **R19 — dependency & lock audit** — requirements.lock vs runtime venv vs CI, vendored KaTeX integrity, genanki pin.
- [ ] **R20 — final regression & wrap-up** — full gate, deploy, live probe suite, close-out summary.

## Standing rules

1. Findings need reproduction or a traced code path before fixing — no speculative edits.
2. Every fix lands with a regression test when testable.
3. The box only gets checked after the full gate passes post-fix.
4. Anything deliberately not fixed is recorded here with the reason.
