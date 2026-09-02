"""Aggregations for the dashboard, review notebook, and plan generator.

Pure reads over indexed queries; personal-site scale (hundreds to low
thousands of rows per profile), so Python-side grouping is fine.
"""

from __future__ import annotations

from collections import defaultdict

from .content import all_bank_items, chapters_store, store, tutorial_for
from .models import ChapterProgress, ExamAttempt, ExamResponse, PracticeAttempt


def _chapter_index() -> dict[str, dict]:
    """question_id (practice or bank) -> {chapter_id, discipline}.

    Reads store() directly (no per-item deepcopy) — this used to deep-copy
    the whole chapter library once per bank item (~23 s per dashboard).
    """
    chs = store()["chapters"]
    out: dict[str, dict] = {}
    for ch in chs.values():
        for q in ch.get("practice") or []:
            if q.get("id"):
                out[q["id"]] = {"chapter_id": ch["id"], "discipline": ch.get("discipline", "")}
    for item in all_bank_items().values():
        if item.get("id") and item.get("chapter"):
            ch = chs.get(item["chapter"]) or {}
            out[item["id"]] = {"chapter_id": item["chapter"], "discipline": ch.get("discipline", "")}
    return out


def exam_history(profile) -> list[dict]:
    """Finished attempts, oldest first — dashboard trend input."""
    rows = (ExamAttempt.objects.filter(profile=profile)
            .exclude(status="active").order_by("started_at"))
    return [{"id": a.id, "exam": a.exam, "status": a.status,
             "correct": a.num_correct or 0, "items": a.num_items or 0,
             "pct": ((a.score or {}).get("pct") or 0.0),
             "date": a.finished_at or a.started_at}
            for a in rows]


def chapter_accuracy(profile) -> dict[str, dict]:
    """chapter_id -> {correct, total} merged over practice + exam responses."""
    qindex = _chapter_index()
    acc: dict[str, dict] = defaultdict(lambda: {"correct": 0, "total": 0})
    for r in PracticeAttempt.objects.filter(profile=profile):
        meta = qindex.get(r.question_id)
        if not meta:
            continue
        slot = acc[meta["chapter_id"]]
        slot["total"] += 1
        if r.correct:
            slot["correct"] += 1
    submitted = ExamAttempt.objects.filter(profile=profile).exclude(status="active")
    for resp in ExamResponse.objects.filter(attempt__in=submitted):
        if not resp.chapter_id:
            continue
        slot = acc[resp.chapter_id]
        slot["total"] += 1
        if resp.correct:
            slot["correct"] += 1
    return dict(acc)


def wrong_chapters(profile, limit: int = 8) -> list[dict]:
    """Weakest chapters first: lowest accuracy with at least one attempt."""
    chs = chapters_store()
    rows = []
    for chapter_id, slot in chapter_accuracy(profile).items():
        if not slot["total"]:
            continue
        ch = chs.get(chapter_id) or {}
        if not tutorial_for(ch.get("discipline", ""), ch.get("title", "")):
            continue  # only chapters we can link into the textbook
        rows.append({
            "chapter_id": chapter_id,
            "discipline": ch.get("discipline", ""),
            "title": ch.get("title", chapter_id),
            "correct": slot["correct"],
            "total": slot["total"],
            "pct": round(100 * slot["correct"] / slot["total"]),
        })
    rows.sort(key=lambda r: (r["pct"], -r["total"]))
    return rows[:limit]


def wrong_questions(profile, limit: int = 300) -> list[dict]:
    """All distinct wrong answers, newest first — the review notebook."""
    qindex = _chapter_index()
    chs = store()["chapters"]
    # Retire recovered items: an item is "still wrong" only if its LATEST
    # attempt is wrong. Latest-attempt resolution over both sources.
    latest: dict[str, tuple] = {}  # question_id -> (when, is_correct, row-info)

    def consider(qid, when, is_correct, info):
        prev = latest.get(qid)
        if prev is None or (when and when > (prev[0] or when)):
            latest[qid] = (when, is_correct, info)

    for r in PracticeAttempt.objects.filter(profile=profile).order_by("created_at"):
        consider(r.question_id, r.created_at, r.correct,
                 {"source": "practice", "question_id": r.question_id,
                  "chosen": r.chosen, "when": r.created_at})
    submitted = ExamAttempt.objects.filter(profile=profile).exclude(status="active")
    for resp in (ExamResponse.objects
                 .filter(attempt__in=submitted)
                 .select_related("attempt").order_by("attempt__finished_at")):
        consider(resp.item_id, resp.attempt.finished_at, resp.correct,
                 {"source": "exam", "question_id": resp.item_id,
                  "attempt_id": resp.attempt_id, "chosen": resp.chosen,
                  "when": resp.attempt.finished_at})

    wrong_rows = [info for (when, is_correct, info) in latest.values()
                  if not is_correct]
    wrong_rows.sort(key=lambda info: info.get("when") or info.get("when"), reverse=True)
    out: list[dict] = []
    for info in wrong_rows[:limit]:
        meta = qindex.get(info["question_id"]) or {}
        ch = chs.get(meta.get("chapter_id") or info.get("chapter_id", "")) or {}
        out.append({**info,
                    "chapter_id": meta.get("chapter_id") or info.get("chapter_id", ""),
                    "discipline": ch.get("discipline", "")})
    return out


def subject_progress(profile, subject_slug: str) -> dict:
    """{done, total, pct} over the subject's outline chapters."""
    from .content import get_subject
    from .learners import progress_map
    subject = get_subject(subject_slug)
    if not subject:
        return {"done": 0, "total": 0, "pct": 0.0}
    chapter_ids = []
    for group in subject.get("chapters") or []:
        for ref in group.get("chapters") or []:
            if ref not in chapter_ids:
                chapter_ids.append(ref)
    # Progress is keyed by chapter_id alone: a chapter ticked from any subject
    # page that contains it counts here too (6 chapters live in 2-3 outlines).
    done_rows = set(ChapterProgress.objects.filter(
        profile=profile, chapter_id__in=chapter_ids).values_list("chapter_id", flat=True))
    n_done = len(done_rows)
    total = len(chapter_ids)
    return {"done": n_done, "total": total,
            "pct": round(100 * n_done / total) if total else 0}


def continue_learning(profile) -> dict | None:
    """The most recently touched completed chapter with a tutorial."""
    chs = chapters_store()
    row = (ChapterProgress.objects.filter(profile=profile)
           .order_by("-updated_at").first())
    if not row:
        return None
    ch = chs.get(row.chapter_id)
    if not ch or not tutorial_for(ch.get("discipline", ""), ch.get("title", "")):
        return None
    return {"chapter_id": row.chapter_id, "discipline": ch["discipline"],
            "title": ch.get("title", row.chapter_id), "subject": row.subject_slug,
            "when": row.updated_at}


def item_difficulty_map(min_n: int = 5) -> dict[str, dict]:
    """Anonymised, data-driven difficulty per bank item.

    Aggregates every graded ExamResponse repo-wide (attempts of all
    learners) into a miss rate; items with fewer than `min_n` graded
    responses stay unlabeled — small samples lie. Purely aggregate data,
    never per-learner.
    """
    from django.db.models import Count, Q

    rows = (ExamResponse.objects
            .values("item_id")
            .annotate(n=Count("id"),
                      misses=Count("id", filter=Q(correct=False))))
    out: dict[str, dict] = {}
    for r in rows:
        if r["n"] >= min_n:
            out[r["item_id"]] = {
                "n": r["n"],
                "miss_pct": int(round(100 * r["misses"] / r["n"])),
            }
    return out
