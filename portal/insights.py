"""Aggregations for the dashboard, review notebook, and plan generator.

Pure reads over indexed queries; personal-site scale (hundreds to low
thousands of rows per profile), so Python-side grouping is fine.
"""

from __future__ import annotations

from collections import defaultdict

from .content import all_bank_items, chapters_store, store, tutorial_for
from .models import ChapterProgress, ExamAttempt, ExamResponse, PracticeAttempt


def _chapter_index() -> dict[str, dict]:
    """question_id (practice or bank) -> {chapter_id, discipline}."""
    out: dict[str, dict] = {}
    for ch in store()["chapters"].values():
        for q in ch.get("practice") or []:
            if q.get("id"):
                out[q["id"]] = {"chapter_id": ch["id"], "discipline": ch.get("discipline", "")}
    for item in all_bank_items().values():
        if item.get("id") and item.get("chapter"):
            disc = (chapters_store().get(item["chapter"]) or {}).get("discipline", "")
            out[item["id"]] = {"chapter_id": item["chapter"], "discipline": disc}
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
    chs = chapters_store()
    seen: set[str] = set()
    out: list[dict] = []
    for r in (PracticeAttempt.objects.filter(profile=profile, correct=False)
              .order_by("-created_at")[:limit]):
        if r.question_id in seen:
            continue
        seen.add(r.question_id)
        meta = qindex.get(r.question_id) or {}
        out.append({"source": "practice", "question_id": r.question_id,
                    "chosen": r.chosen, "chapter_id": meta.get("chapter_id", ""),
                    "discipline": meta.get("discipline", ""), "when": r.created_at})
    submitted = ExamAttempt.objects.filter(profile=profile).exclude(status="active")
    for resp in (ExamResponse.objects
                 .filter(attempt__in=submitted, correct=False)
                 .select_related("attempt").order_by("-attempt__finished_at")):
        if resp.item_id in seen:
            continue
        seen.add(resp.item_id)
        ch = chapters_store().get(resp.chapter_id) or {}
        out.append({"source": "exam", "question_id": resp.item_id,
                    "attempt_id": resp.attempt_id,
                    "chosen": resp.chosen, "chapter_id": resp.chapter_id,
                    "discipline": ch.get("discipline", ""), "when": resp.attempt.finished_at})
    return out[:limit]


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
    done = progress_map(profile.username, subject_slug)
    n_done = sum(1 for cid in chapter_ids if done.get(cid))
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
