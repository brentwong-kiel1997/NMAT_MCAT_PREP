"""AI-powered weak-point analysis: aggregates the learner's data, asks the
configured coach model for a study plan critique, and degrades gracefully
to a plain data report when no model is configured."""

from __future__ import annotations

import json
import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_GET

from . import insights
from .llm import chat_completion, coach_ready
from .models import ReviewNote


def _aggregate(username: str) -> dict:
    profile = __import__("portal.learners", fromlist=["get_or_create_profile"]).get_or_create_profile(username)
    weak = insights.wrong_chapters(profile, limit=10)
    causes = {}
    wrong = insights.wrong_questions(profile, limit=1000)
    stored = {n.question_id: n.cause for n in ReviewNote.objects.filter(
        profile=profile, question_id__in=[it["question_id"] for it in wrong])}
    for it in wrong:
        key = stored.get(it["question_id"], "unlabeled")
        causes[key] = causes.get(key, 0) + 1
    history = insights.exam_history(profile)
    trend = [h["pct"] for h in history]
    return {
        "weak_chapters": weak,
        "causes": causes,
        "mock_count": len(history),
        "trend": trend,
        "trend_direction": ("up" if len(trend) >= 2 and trend[-1] > trend[0]
                            else "down" if len(trend) >= 2 and trend[-1] < trend[0] else "flat"),
    }


def _prompt(data: dict) -> str:
    # enrich with tutorial key_points/pitfalls for weak chapters so the coach
    # can reference specific misconceptions, not just chapter names
    from .content import tutorial_for, chapters_store
    chs = chapters_store()
    prose_bits = []
    for w in data.get("weak_chapters", [])[:3]:
        ch = chs.get(w.get("chapter_id") or "")
        if not ch:
            continue
        tut = tutorial_for(ch.get("discipline", ""), ch.get("title", ""))
        if tut:
            kp = "; ".join(tut.get("key_points") or [])[:300]
            pf = "; ".join(tut.get("pitfalls") or [])[:300]
            prose_bits.append(f"{ch['title']}: key points: {kp}. Pitfalls: {pf}")
    prose_block = "\n".join(prose_bits) if prose_bits else "(no tutorial prose available)"

    return (
        "You are an MCAT/NMAT study coach. Based ONLY on the learner data below, "
        "write a focused study recommendation in English: (1) which 2-3 chapters to "
        "prioritize and why, (2) what the miss-cause pattern says about study habits, "
        "(3) one concrete next action. Do not invent data that is not listed.\n\n"
        f"Weak chapters (accuracy %): {json.dumps(data['weak_chapters'])}\n"
        f"Miss causes: {json.dumps(data['causes'])}\n"
        f"Mock attempts: {data['mock_count']}\n"
        f"Score trend: {data['trend']} ({data['trend_direction']})\n\n"
        f"Tutorial content for the weak chapters:\n{prose_block}\n"
    )


@login_required
@require_GET
def coach_insights(request):
    data = _aggregate(request.user.username)
    ai_text = ""
    ai_error = ""
    if coach_ready():
        try:
            ai_text = chat_completion([{"role": "user", "content": _prompt(data)}],
                                      max_tokens=700, temperature=0.3)
        except Exception:  # network/API failure — degrade, don't 500
            # no upstream URL/body on screen; the real error goes to the log
            logging.getLogger("portal.coach").exception(
                "coach insights generation failed")
            ai_error = "The study coach is unavailable right now — your data report is below."
    else:
        ai_error = "No AI model configured — showing your data report only."
    return render(request, "portal/coach_insights.html", {
        "data": data, "ai_text": ai_text, "ai_error": ai_error,
    })
