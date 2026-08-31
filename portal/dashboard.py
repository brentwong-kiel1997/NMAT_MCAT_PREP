"""Dashboard, review notebook, and study-plan views."""

from __future__ import annotations

import datetime as dt
import json
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from . import insights, planner


def cause_distribution_local(profile):
    """Distribution over distinct wrong questions, batched."""
    wrong = insights.wrong_questions(profile, limit=1000)
    qids = [w["question_id"] for w in wrong]
    notes = {n.question_id: n.cause
             for n in ReviewNote.objects.filter(profile=profile,
                                                question_id__in=qids)}
    counts = {}
    for w in wrong:
        key = notes.get(w["question_id"], "unlabeled")
        counts[key] = counts.get(key, 0) + 1
    return counts
from .views import _json_for_script
from .content import all_bank_items, chapters_store, store
from .models import ChapterProgress, ExamAttempt, ReviewNote, StudyPlan


def _profile(request):
    from .learners import get_or_create_profile
    return get_or_create_profile(request.user.username)


@login_required
@require_GET
def dashboard(request):
    profile = _profile(request)
    history = insights.exam_history(profile)
    subjects = []
    for slug, label in [
        ("biology", "Biology"), ("chemistry", "Chemistry"), ("physics", "Physics"),
        ("biochemistry", "Biochemistry"), ("behavioral-social", "Behavioral & Social"),
        ("psych-soc", "Psychology & Sociology"), ("verbal", "Verbal"),
        ("quantitative", "Quantitative"), ("inductive-reasoning", "Inductive"),
        ("perceptual-acuity", "Perceptual"), ("cars", "CARS"),
    ]:
        prog = insights.subject_progress(profile, slug)
        if prog["total"]:
            subjects.append({"slug": slug, "label": label, **prog})
    causes = cause_distribution_local(profile)
    # subject accuracy merged from chapter_accuracy
    chs = insights.chapter_accuracy(profile)
    chapters_store = store()["chapters"]
    subj_acc: dict = {}
    for cid, slot in chs.items():
        ch = chapters_store.get(cid) or {}
        disc = ch.get("discipline", "")
        if not disc:
            continue
        agg = subj_acc.setdefault(disc, {"correct": 0, "total": 0})
        agg["correct"] += slot["correct"]
        agg["total"] += slot["total"]
    from .srs import srs_stats
    from .planner import build_plan
    sp = getattr(profile, "study_plan", None)
    today_tasks, mock_recommended = [], False
    if sp:
        done = {row.chapter_id for row in ChapterProgress.objects.filter(profile=profile)}
        full = planner.build_plan(exam_id=sp.exam, exam_date=sp.exam_date,
                                  weekly_hours=sp.weekly_hours, done=done)
        today_tasks = full[0]["tasks"] if full else []
    stats = srs_stats(request.user.username)
    has_real = ExamAttempt.objects.filter(profile=profile, exam__in=("nmat", "mcat"),
                                          mode="real").exclude(status="active").exists()
    ctx = {
        "history": history,
        "today_tasks": today_tasks,
        "due_cards": stats["due_today"],
        "has_real_mock": has_real,
        "mock_recommended": not has_real,
        "subject_accuracy": [{"discipline": d, **v,
                              "pct": round(100 * v["correct"] / v["total"]) if v["total"] else 0}
                             for d, v in sorted(subj_acc.items()) if v["total"]],
        "causes": causes,
        "subjects": subjects,
        "weak_chapters": insights.wrong_chapters(profile),
        "continue_learning": insights.continue_learning(profile),
        "wrong_count": len(insights.wrong_questions(profile, limit=1000)),
        "attempt_count": len(history),
    }
    return render(request, "portal/dashboard.html", ctx)


@login_required
@require_GET
def review(request):
    profile = _profile(request)
    index = all_bank_items()
    practice_store = {}
    for ch in store()["chapters"].values():
        for q in ch.get("practice") or []:
            if q.get("id"):
                practice_store[q["id"]] = q
    rows = insights.wrong_questions(profile)
    items = []
    for row in rows:
        q = practice_store.get(row["question_id"]) or index.get(row["question_id"]) or {}
        chs = chapters_store()
        ch = chs.get(row["chapter_id"]) or {}
        items.append({**row,
                      "stem": q.get("q", ""),
                      "choices": q.get("choices") or q.get("options") or {},
                      "answer": q.get("answer", ""),
                      "explain": q.get("explain", ""),
                      "chapter_title": ch.get("title", row["chapter_id"])})
    by_chapter: dict[str, list] = {}
    for it in items:
        by_chapter.setdefault(it["chapter_id"] or "other", []).append(it)
    # batch-fetch stored causes instead of per-item queries (were N+1)
    qids = [it["question_id"] for it in items]
    stored = {n.question_id: n.cause
              for n in ReviewNote.objects.filter(profile=profile,
                                                 question_id__in=qids)}
    for it in items:
        it["stored_cause"] = stored.get(it["question_id"])
    groups = []
    for chapter_id, group in sorted(by_chapter.items(), key=lambda kv: -len(kv[1])):
        first = group[0]
        groups.append({"chapter_id": chapter_id, "count": len(group),
                       "discipline": first["discipline"],
                       "chapter_title": first["chapter_title"] or chapter_id,
                       "items": group})
    causes = dict(ReviewNote.CAUSES)
    return render(request, "portal/review.html", {"groups": groups,
                                                  "total": len(items),
                                                  "cause_labels": causes.items(),
                                                  "cause_dist": cause_distribution_local(profile)})



@login_required
@require_GET
def review_redo(request, chapter_id: str):
    profile = _profile(request)
    chs = chapters_store()
    ch = chs.get(chapter_id)
    if not ch:
        raise Http404("Unknown chapter")
    wrong_ids = {w["question_id"] for w in insights.wrong_questions(profile, limit=1000)}
    index = all_bank_items()
    # practice items store `chapter` as the chapter TITLE; build title -> id
    # so practice-source wrongs can be redone too (the old id-only filter
    # silently dropped them all)
    title_to_id = {c["title"]: cid for cid, c in store()["chapters"].items()}
    items = []
    for qid in sorted(wrong_ids):
        q = index.get(qid)
        item_chapter = (q or {}).get("chapter") or ""
        if not q or not item_chapter:
            for c2 in store()["chapters"].values():
                q = next((x for x in c2.get("practice") or [] if x.get("id") == qid), None)
                if q:
                    item_chapter = title_to_id.get(q.get("chapter", ""), c2["id"])
                    break
        if not q or item_chapter != chapter_id:
            continue
        ch_title = (chs.get(item_chapter) or {}).get("title", item_chapter)
        items.append({"id": qid, "q": q.get("q", ""),
                      "choices": q.get("choices") or q.get("options") or {},
                      "figure": f"/content-images/{q.get('figure','')}" if q.get("figure") else "",
                      "chapter": ch_title})
    if not items:
        return redirect("review")
    return render(request, "portal/review_redo.html", {
        "chapter": ch, "chapter_id": chapter_id,
        "discipline": ch.get("discipline", ""),
        "items": items, "items_json": _json_for_script(items),
        "count": len(items),
        "practice_key": f"gabay_redo_{chapter_id}",
    })


@login_required
@require_GET
def plan(request):
    profile = _profile(request)
    study_plan = getattr(profile, "study_plan", None)
    generated = None
    if study_plan:
        from .models import ChapterProgress
        done = {row.chapter_id for row in ChapterProgress.objects.filter(profile=profile)}
        generated = planner.build_plan(
            exam_id=study_plan.exam, exam_date=study_plan.exam_date,
            weekly_hours=study_plan.weekly_hours, done=done)
        total_tasks = sum(len(day["tasks"]) for day in generated)
        total_minutes = sum(day["minutes"] for day in generated)
        generated = {"days": generated, "total_tasks": total_tasks,
                     "total_hours": round(total_minutes / 60)}
    exams = [{"id": "nmat", "name": "NMAT"}, {"id": "mcat", "name": "MCAT"}]
    return render(request, "portal/plan.html",
                  {"study_plan": study_plan, "plan": generated, "exams": exams})


@login_required
@require_POST
def plan_save(request):
    profile = _profile(request)
    exam = request.POST.get("exam") or "nmat"
    if exam not in ("nmat", "mcat"):
        raise Http404("Unknown exam")
    try:
        exam_date = dt.date.fromisoformat(request.POST.get("exam_date") or "")
    except ValueError:
        raise Http404("Bad date")
    if exam_date <= dt.date.today():
        return redirect("plan")
    try:
        weekly_hours = max(1, min(80, int(request.POST.get("weekly_hours") or 10)))
    except ValueError:
        weekly_hours = 10
    StudyPlan.objects.update_or_create(
        profile=profile,
        defaults={"exam": exam, "exam_date": exam_date, "weekly_hours": weekly_hours})
    return redirect("plan")


@login_required
@require_POST
def review_cause_api(request):
    """Label the cause of a miss (the review-loop taxonomy)."""
    import json as _json

    from .models import ReviewNote

    try:
        payload = _json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)
    try:
        question_id = str(payload.get("question_id") or "").strip()[:64]
        cause = str(payload.get("cause") or "").strip()
        note_text = str(payload.get("note") or "")[:500]
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "Invalid payload"}, status=400)
    if not question_id or cause not in {"content", "misread", "careless", "trap"}:
        return JsonResponse({"ok": False, "error": "Invalid cause"}, status=400)
    if not question_id or cause not in {"content", "misread", "careless", "trap"}:
        return JsonResponse({"ok": False, "error": "Invalid cause"}, status=400)
    profile = _profile(request)
    # only questions recorded as wrong (or bank/practice-known) may be labeled —
    # prevents ghost rows for fabricated ids
    known_ids = {w["question_id"] for w in insights.wrong_questions(profile, limit=1000)}
    from .content import all_bank_items, store as _content_store
    known_ids |= set(all_bank_items().keys())
    for ch in _content_store()["chapters"].values():
        known_ids |= {q.get("id") for q in ch.get("practice") or [] if q.get("id")}
    if question_id not in known_ids:
        return JsonResponse({"ok": False, "error": "Unknown question"}, status=404)
    ReviewNote.objects.update_or_create(
        profile=profile, question_id=question_id,
        defaults={"cause": cause, "note": note_text})
    return JsonResponse({"ok": True})



