"""Mock-exam engine state machine.

Pure domain logic — no HTTP imports. exam_views.py calls into this; every
exam GET re-runs maybe_finalize() so a deadline passing is enforced
server-side regardless of what the browser does. All block-clock math uses
epoch ints inside ExamAttempt.sections; display datetimes stay in real
columns (USE_TZ=True).
"""

from __future__ import annotations

import time

from django.db import transaction
from django.db import IntegrityError
from django.utils import timezone

from .content import all_bank_items, exam_blueprint, exam_item_index
from .learners import get_or_create_profile
from .models import ExamAttempt, ExamResponse


class ExamError(Exception):
    pass


def _learner(username: str):
    return get_or_create_profile(username)


def _blocks(exam_id: str) -> list[dict]:
    bp = exam_blueprint(exam_id)
    if not bp:
        raise ExamError(f"unknown exam {exam_id!r}")
    return list(bp.get("blocks") or [])


def build_plan(exam_id: str) -> dict:
    """Freeze blueprint + ordered item ids at start time."""
    index = exam_item_index(exam_id)
    blocks = []
    for block in _blocks(exam_id):
        ids = [i["id"] for i in index.values()
               if i["block_id"] == block["id"]]
        # exam_items() flattens in blueprint order; preserve that order
        ordered = [i["id"] for i in exam_item_list(exam_id) if i["block_id"] == block["id"]]
        ids = ordered or ids
        blocks.append({
            "id": block["id"],
            "label": block.get("label", block["id"]),
            "seconds": block.get("seconds", 0),
            "items": ids,
        })
    return {"blocks": blocks}


def exam_item_list(exam_id: str) -> list[dict]:
    from .content import exam_items
    return exam_items(exam_id, with_key=True)


def _diagnostic_plan(exam_id: str, plan: dict) -> dict:
    """Half-length: for each block, round-robin one item per chapter until
    half the block's items are taken — even coverage across the syllabus."""
    index = exam_item_index(exam_id)
    for b in plan["blocks"]:
        items = b["items"]
        target = max(4, len(items) // 2)
        by_chapter: dict[str, list[str]] = {}
        for iid in items:
            by_chapter.setdefault((index.get(iid) or {}).get("chapter") or "", []).append(iid)
        picked: list[str] = []
        pools = [ids for ids in by_chapter.values() if ids]
        while len(picked) < target and pools:
            for pool in pools:
                if pool and len(picked) < target:
                    picked.append(pool.pop(0))
        b["items"] = picked
    return plan


def _variant_map(item_ids: list[str], seed: str) -> dict:
    """Retake variant for one block: shuffled item order + a per-item letter
    permutation. Deterministic from (seed, item ids) so a rebuilt plan stays
    stable. Scores map back to the canonical key, so scoring never changes."""
    import random

    rng = random.Random(seed)
    order = list(item_ids)
    rng.shuffle(order)
    letters = ["A", "B", "C", "D"]
    vmap = {}
    for iid in order:
        perm = letters[:]
        rng.shuffle(perm)
        vmap[iid] = {shown: original for shown, original in zip(letters, perm)}
    return {"order": order, "vmap": vmap}


def start_attempt(username: str, exam_id: str, mode: str = "real") -> ExamAttempt:
    profile = _learner(username)
    plan = build_plan(exam_id)
    if mode == "diagnostic":
        plan = _diagnostic_plan(exam_id, plan)
    # retake variant: anyone who already finished a REAL attempt of this exam
    # gets a reshuffled form — item order and option letters permuted, scored
    # on canonical keys. Diagnostics never permute (they are one-shot).
    seen_before = ExamAttempt.objects.filter(
        profile=profile, exam=exam_id, mode="real").exclude(status="active").exists()
    variant_seed = (f"{username}:{exam_id}:{timezone.now().timestamp():.0f}"
                    if seen_before and mode == "real" else "")
    blocks = []
    for b in plan["blocks"]:
        entry = {"id": b["id"], "label": b.get("label", b["id"]),
                 "seconds": b.get("seconds", 0), "items": b["items"]}
        if variant_seed:
            v = _variant_map(b["items"], f"{variant_seed}:{b['id']}")
            entry["items"] = v["order"]
            entry["vmap"] = v["vmap"]
        if mode == "diagnostic":
            entry["seconds"] = max(300, entry["seconds"] // 2)
        blocks.append(entry)
    plan = {"blocks": blocks}
    try:
        # inner atomic: contains the IntegrityError so a live active attempt
        # (or the test-runner's outer transaction) doesn't get poisoned
        with transaction.atomic():
            return ExamAttempt.objects.create(
                profile=profile,
                exam=exam_id,
                mode=mode,
                plan=plan,
                sections=[{"id": b["id"], "started_ts": None, "seconds": b["seconds"],
                           "finished_ts": None, "pos": 0}
                          for b in plan["blocks"]],
                answers={},
            )
    except IntegrityError:
        # one active attempt per (profile, exam) — resume the winner's attempt
        existing = ExamAttempt.objects.filter(profile=profile, exam=exam_id,
                                              status="active").first()
        if existing:
            if existing.mode != mode:
                raise ExamError(
                    f"an active {existing.mode} attempt is already running — "
                    f"finish it before starting a {mode} one")
            return existing
        raise


def get_attempt(username: str, attempt_id: int) -> ExamAttempt | None:
    attempt = (ExamAttempt.objects.select_related("profile")
               .filter(id=attempt_id).first())
    if not attempt or attempt.profile.username != username:
        return None
    return attempt


def active_attempt(username: str, exam_id: str) -> ExamAttempt | None:
    profile = _learner(username)
    return ExamAttempt.objects.filter(profile=profile, exam=exam_id,
                                      status="active").first()


def _now_ts() -> int:
    return int(time.time())


def _section_state(attempt: ExamAttempt, block_id: str) -> dict:
    for s in attempt.sections or []:
        if s.get("id") == block_id:
            return s
    raise ExamError(f"block {block_id!r} not in attempt")


def block_index(attempt: ExamAttempt, block_id: str) -> int:
    for i, s in enumerate(attempt.sections or []):
        if s.get("id") == block_id:
            return i
    raise ExamError(f"block {block_id!r} not in attempt")


def remaining_seconds(attempt: ExamAttempt, block_id: str) -> int:
    s = _section_state(attempt, block_id)
    if not s.get("started_ts"):
        return s.get("seconds", 0)
    elapsed = _now_ts() - int(s["started_ts"])
    return max(0, int(s.get("seconds", 0)) - elapsed)


def current_block(attempt: ExamAttempt) -> str | None:
    """First unfinished block (no started_ts → upcoming; started → current)."""
    for s in attempt.sections or []:
        if not s.get("finished_ts"):
            return s["id"]
    return None


def block_started(attempt: ExamAttempt, block_id: str) -> bool:
    return bool(_section_state(attempt, block_id).get("started_ts"))


def block_position(attempt: ExamAttempt, block_id: str) -> int:
    return int(_section_state(attempt, block_id).get("pos") or 0)


def set_position(attempt: ExamAttempt, block_id: str, pos: int) -> None:
    with transaction.atomic():
        locked = ExamAttempt.objects.select_for_update().get(id=attempt.id)
        s = _section_state(locked, block_id)
        if s.get("pos") != pos:
            s["pos"] = pos
            locked.save(update_fields=["sections", "updated_at"])
            attempt.sections = locked.sections


def maybe_finalize(attempt: ExamAttempt) -> ExamAttempt:
    """Enforce deadlines server-side; safe to call on every request."""
    if attempt.status != "active":
        return attempt
    for s in attempt.sections or []:
        if s.get("started_ts") and not s.get("finished_ts"):
            if remaining_seconds(attempt, s["id"]) <= 0:
                _close_block(attempt, s["id"])
    started = [s for s in (attempt.sections or []) if s.get("started_ts")]
    if (started and len(started) == len(attempt.sections)
            and all(s.get("finished_ts") for s in started)):
        return finalize(attempt, reason="expired")
    return attempt


def _close_block(attempt: ExamAttempt, block_id: str) -> None:
    s = _section_state(attempt, block_id)
    if s.get("started_ts") and not s.get("finished_ts"):
        s["finished_ts"] = _now_ts()
        attempt.save(update_fields=["sections", "updated_at"])


def begin_block(attempt: ExamAttempt, block_id: str) -> None:
    # sequence guard: only the first unfinished block may begin (no skipping)
    first = current_block(attempt)
    if first != block_id:
        raise ExamError(f"block {block_id!r} is not the next block ({first!r})")
    s = _section_state(attempt, block_id)
    if not s.get("started_ts"):
        s["started_ts"] = _now_ts()
        attempt.save(update_fields=["sections", "updated_at"])


def save_answer(attempt: ExamAttempt, block_id: str, pos: int,
                chosen: str | None, flagged: bool,
                elapsed_seconds: int | None = None,
                crossed: list | None = None) -> dict:
    """Autosave one item's captured state. Row-locked so concurrent saves
    from two tabs cannot clobber each other's answers."""
    with transaction.atomic():
        locked = ExamAttempt.objects.select_for_update().get(id=attempt.id)
        if locked.status != "active":
            return {"ok": False, "error": "closed"}
        s = _section_state(locked, block_id)
        if not s.get("started_ts"):
            return {"ok": False, "error": "not-started"}
        if s.get("finished_ts") or remaining_seconds(locked, block_id) <= 0:
            _close_block(locked, block_id)
            return {"ok": False, "error": "expired"}
        # pos -> item from the FROZEN plan (bank edits mid-attempt must not
        # shift which question an answer lands on)
        block = next((b for b in locked.plan.get("blocks") or []
                      if b["id"] == block_id), None)
        if not block or not (1 <= pos <= len(block["items"])):
            return {"ok": False, "error": "bad-pos"}
        item_id = block["items"][pos - 1]
        answers = locked.answers or {}
        entry = answers.get(item_id) or {}
        if chosen is not None:
            chosen = str(chosen).strip().upper()[:1]
            # retake variant: the page shows permuted letters — fold the
            # shown letter back to the canonical one before storing
            shown_map = ((block.get("vmap") or {}).get(item_id) or {})
            if shown_map:
                chosen = shown_map.get(chosen)
            if chosen not in ("A", "B", "C", "D"):
                return {"ok": False, "error": "bad-choice"}
            entry["c"] = chosen
        entry["f"] = 1 if flagged else 0
        if crossed is not None:
            # eliminated choices (shown letters); UI-only, never scored
            clean = sorted({str(c).strip().upper()[:1] for c in crossed} & {"A", "B", "C", "D"})
            if clean:
                entry["x"] = clean
            else:
                entry.pop("x", None)
        if elapsed_seconds is not None:
            # accumulate visits to the same item (last-visit-only made the
            # average undercount multi-visit questions)
            prior = int(entry.get("s") or 0)
            entry["s"] = max(0, min(prior + int(elapsed_seconds), 3600))
        answers[item_id] = entry
        locked.answers = answers
        if s.get("pos") != pos:
            s["pos"] = pos
        locked.save(update_fields=["answers", "sections", "updated_at"])
    attempt.answers = locked.answers
    attempt.sections = locked.sections
    return {"ok": True, "item_id": item_id}


def finish_block(attempt: ExamAttempt, block_id: str) -> None:
    _close_block(attempt, block_id)
    remaining_blocks = [s for s in attempt.sections
                        if not s.get("finished_ts")]
    if not remaining_blocks:
        finalize(attempt, reason="submitted")


def _chapter_discipline(chapter_id: str) -> str:
    from .content import chapters_store
    return (chapters_store().get(chapter_id) or {}).get("discipline", "")


def score_attempt(attempt: ExamAttempt) -> dict:
    """Pure scoring: bank index + captured answers → snapshot dict."""
    index = exam_item_index(attempt.exam)
    blocks = attempt.plan.get("blocks") or []
    out_blocks = []
    total = correct_total = answered_total = 0
    weak: dict[str, dict] = {}
    for b in blocks:
        subtests: dict[str, dict] = {}
        b_correct = b_items = 0
        b_seconds = 0
        n_items = len(b.get("items") or [])
        fair_share = max(1, b.get("seconds", 0) // n_items) if n_items else 0
        for pos, item_id in enumerate(b.get("items") or [], start=1):
            item = index.get(item_id)
            if not item:
                continue
            b_items += 1
            entry = (attempt.answers or {}).get(item_id) or {}
            chosen = entry.get("c")
            is_correct = bool(chosen) and chosen == item["answer"]
            if chosen:
                answered_total += 1
            if is_correct:
                b_correct += 1
            sec = subtests.setdefault(
                item["section_id"],
                {"id": item["section_id"], "label": section_label(attempt.exam, item["section_id"]),
                 "items": 0, "correct": 0})
            sec["items"] += 1
            if is_correct:
                sec["correct"] += 1
            b_seconds += entry.get("s") or 0
            chapter = item.get("chapter") or ""
            if chapter:
                agg = weak.setdefault(chapter, {"chapter_id": chapter, "items": 0, "correct": 0,
                                                "discipline": _chapter_discipline(chapter)})
                agg["items"] += 1
                if is_correct:
                    agg["correct"] += 1
        total += b_items
        correct_total += b_correct
        out_blocks.append({
            "id": b["id"], "label": b.get("label", b["id"]),
            "items": b_items, "correct": b_correct,
            "pct": round(100 * b_correct / b_items, 1) if b_items else 0.0,
            "seconds_used": _seconds_used(attempt, b["id"]),
            "seconds_on_items": b_seconds,
            "avg_seconds_per_item": round(b_seconds / b_items, 1) if b_items else 0.0,
            "fair_share": fair_share,
            "subtests": list(subtests.values()),
        })
    weak_list = [w for w in weak.values() if w["correct"] < w["items"]]
    weak_list.sort(key=lambda w: (w["correct"] / w["items"], -w["items"]))
    return {
        "exam": attempt.exam,
        "items": total,
        "answered": answered_total,
        "correct": correct_total,
        "pct": round(100 * correct_total / total, 1) if total else 0.0,
        "blocks": out_blocks,
        "weak_chapters": weak_list[:10],
    }


def section_label(exam_id: str, section_id: str) -> str:
    from .content import exam_bank_section
    doc = exam_bank_section(exam_id, section_id)
    return (doc or {}).get("label", section_id)


def _seconds_used(attempt: ExamAttempt, block_id: str) -> int:
    s = _section_state(attempt, block_id)
    if not s.get("started_ts"):
        return 0
    end = s.get("finished_ts") or _now_ts()
    return max(0, min(int(end) - int(s["started_ts"]), int(s.get("seconds", 0))))


@transaction.atomic
def finalize(attempt: ExamAttempt, *, reason: str) -> ExamAttempt:
    """Idempotent close: score, snapshot, bulk-write ExamResponse rows."""
    reloaded = ExamAttempt.objects.select_for_update().get(id=attempt.id)
    if reloaded.status != "active":
        return reloaded
    snapshot = score_attempt(reloaded)
    snapshot["reason"] = reason
    reloaded.status = "expired" if reason == "expired" else "submitted"
    reloaded.finished_at = timezone.now()
    reloaded.num_correct = snapshot["correct"]
    reloaded.num_items = snapshot["items"]
    reloaded.score = snapshot
    reloaded.save(update_fields=["status", "finished_at", "num_correct",
                                 "num_items", "score", "updated_at"])
    index = exam_item_index(reloaded.exam)
    rows = []
    position = 0
    for b in reloaded.plan.get("blocks") or []:
        for pos, item_id in enumerate(b.get("items") or [], start=1):
            position += 1
            item = index.get(item_id) or {}
            entry = (reloaded.answers or {}).get(item_id) or {}
            chosen = entry.get("c") or ""
            rows.append(ExamResponse(
                attempt=reloaded, item_id=item_id, block_id=b["id"],
                chapter_id=item.get("chapter") or "", position=position,
                chosen=chosen, correct=bool(chosen) and chosen == item.get("answer"),
                flagged=bool(entry.get("f")),
                time_spent=entry.get("s"),
            ))
    ExamResponse.objects.bulk_create(rows, batch_size=500)
    return reloaded


def navigator(attempt: ExamAttempt, block_id: str) -> list[dict]:
    """Per-item flags for the question grid: answered / flagged / current."""
    block = next((b for b in attempt.plan.get("blocks") or []
                  if b["id"] == block_id), None)
    if not block:
        return []
    out = []
    for pos, item_id in enumerate(block.get("items") or [], start=1):
        entry = (attempt.answers or {}).get(item_id) or {}
        out.append({"pos": pos, "answered": bool(entry.get("c")),
                    "flagged": bool(entry.get("f"))})
    return out
