"""Dashboard, review notebook, and study-plan views."""

from __future__ import annotations

import datetime as dt
import json

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from . import insights, planner
from .content import all_bank_items, chapters_store, store
from .models import StudyPlan


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
    ctx = {
        "history": history,
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
    groups = []
    for chapter_id, group in sorted(by_chapter.items(), key=lambda kv: -len(kv[1])):
        first = group[0]
        groups.append({"chapter_id": chapter_id, "count": len(group),
                       "discipline": first["discipline"],
                       "chapter_title": first["chapter_title"] or chapter_id,
                       "items": group})
    return render(request, "portal/review.html", {"groups": groups,
                                                  "total": len(items)})


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
                      "answer": q.get("answer", ""), "explain": q.get("explain", ""),
                      "chapter": ch_title})
    if not items:
        return redirect("review")
    items_json = json.dumps(items, ensure_ascii=False).replace("<", "\\u003c")
    return render(request, "portal/review_redo.html", {
        "chapter": ch, "chapter_id": chapter_id,
        "discipline": ch.get("discipline", ""),
        "items": items, "items_json": items_json,
        "count": len(items),
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
