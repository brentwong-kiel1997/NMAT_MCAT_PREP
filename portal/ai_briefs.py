"""Personalised AI briefs: short model-generated narratives layered over the
deterministic data views.

Three briefs, all sharing one contract:
  - grounded ONLY in the learner's real aggregates + chapter tutorial prose
    (prompts forbid invention, matching coach_insights)
  - at most ONE model call per (user, brief, day) per worker: results live
    in a process-level dict — NOT the Django cache, which locmem empties on
    every request (see portal/ratelimit.py for the same discovery); with
    gunicorn workers=2 worst-case limits are doubled
  - each call spends the shared GABAY_COACH_DAILY_LIMIT budget; over budget
    or without a configured model the brief degrades to "" and the template
    simply hides the card
"""

from __future__ import annotations

import time

from django.utils import timezone

from . import insights
from .ratelimit import hit

_BRIEF_CACHE: dict[tuple, str] = {}
_SNAPSHOT_TTL = 60.0  # seconds; consecutive page views reuse the aggregates
_SNAPSHOTS: dict[str, tuple[float, dict]] = {}


def _profile_for(username: str):
    from .learners import get_or_create_profile

    return get_or_create_profile(username)


def _snapshot(username: str) -> dict:
    now = time.monotonic()
    cached = _SNAPSHOTS.get(username)
    if cached and now - cached[0] < _SNAPSHOT_TTL:
        return cached[1]
    snap = _build_snapshot(username)
    _SNAPSHOTS[username] = (now, snap)
    return snap


def _build_snapshot(username: str) -> dict:
    """Learner aggregates shared by every brief (pure reads), memoized for a
    minute so dashboard → review back-to-back views don't re-aggregate."""
    from .models import ReviewNote

    profile = _profile_for(username)
    weak = insights.wrong_chapters(profile, limit=5)
    wrong = insights.wrong_questions(profile, limit=300)
    stored = {n.question_id: n.cause for n in ReviewNote.objects.filter(
        profile=profile, question_id__in=[it["question_id"] for it in wrong])}
    causes: dict[str, int] = {}
    for it in wrong:
        key = stored.get(it["question_id"], "unlabeled")
        causes[key] = causes.get(key, 0) + 1
    return {
        "profile": profile,
        "username": username,
        "weak": weak,
        "wrong": wrong,
        "stored_causes": stored,
        "wrong_count": len(wrong),
        "top_cause": (max(causes, key=causes.get) if causes else ""),
    }


def _cached(key: tuple, username: str, prompt: str, max_tokens: int,
            refresh: bool) -> str:
    from django.conf import settings

    if not refresh:
        cached = _BRIEF_CACHE.get(key)
        if cached is not None:
            return cached
    from .llm import chat_completion, coach_ready

    if not coach_ready():
        return ""
    if not hit(f"coach:{username}:{timezone.localdate()}",
               settings.GABAY_COACH_DAILY_LIMIT, 86400):
        return ""
    try:
        text = chat_completion([{"role": "user", "content": prompt}],
                               max_tokens=max_tokens, temperature=0.3)
    except Exception:
        return ""  # degraded: templates hide the card, deterministic data stands
    text = text.strip()
    if len(_BRIEF_CACHE) > 2048:
        _BRIEF_CACHE.clear()
    _BRIEF_CACHE[key] = text
    return text


def daily_brief(username: str, due_cards: int, today_tasks: list,
                refresh: bool = False) -> str:
    """Two-three sentence 'today' nudge for the dashboard."""
    snap = _snapshot(username)
    worst = snap["weak"][0] if snap["weak"] else None
    data = (
        f"Due flashcards today: {due_cards}. "
        f"Planned tasks today: {len(today_tasks)}. "
        + (f"Weakest chapter: {worst['title']} at {worst['pct']}% accuracy. "
           if worst else "No weak chapters on record yet. ")
        + f"Open wrong answers: {snap['wrong_count']}."
    )
    prompt = (
        "You are the Gabay study coach for NMAT/MCAT prep. Using ONLY the data "
        "below, write 2-3 sentences (max 60 words) in English for the learner's "
        "dashboard: what to focus on today and ONE concrete first action. Plain "
        "text, no markdown, no invented data.\n\n" + data
    )
    key = ("daily", username, str(timezone.localdate()), due_cards, len(today_tasks))
    return _cached(key, username, prompt, max_tokens=160, refresh=refresh)


def exam_eve_brief(username: str, refresh: bool = False) -> str:
    """Countdown briefing for the plan page; empty when no future exam date."""
    profile = _profile_for(username)
    sp = getattr(profile, "study_plan", None)
    if not sp or not sp.exam_date:
        return ""
    days = (sp.exam_date - timezone.localdate()).days
    if days < 0:
        return ""
    snap = _snapshot(username)
    weak_txt = "; ".join("%s %d%%" % (w["title"], w["pct"])
                         for w in snap["weak"][:3]) or "none on record"
    prompt = (
        f"You are the Gabay study coach. The learner sits {sp.exam.upper()} on "
        f"{sp.exam_date} (in {days} day(s)). Using ONLY the data below, write a "
        f"short exam-week briefing in English: three priority topics, one classic "
        f"trap to avoid, and tonight's single action. Max 110 words, plain text, "
        f"three '-' bullets then one 'Tonight:' line, no invented data.\n\n"
        f"Weakest chapters (accuracy): {weak_txt}. "
        f"Top miss cause: {snap['top_cause'] or 'unlabeled'}. "
        f"Open wrong answers: {snap['wrong_count']}."
    )
    key = ("eve", username, str(timezone.localdate()))
    return _cached(key, username, prompt, max_tokens=280, refresh=refresh)


def miss_autopsy(username: str, snap: dict | None = None,
                 refresh: bool = False) -> dict | None:
    """A paragraph tying the biggest weak chapter's cause pattern to its
    tutorial pitfalls; None when there is nothing to autopsy."""
    snap = snap or _snapshot(username)
    worst = snap["weak"][0] if snap["weak"] else None
    if not worst:
        return None
    from .content import chapters_store, tutorial_for

    chs = chapters_store()
    ch = chs.get(worst["chapter_id"]) or {}
    title = ch.get("title") or worst.get("title") or worst["chapter_id"]
    tut = tutorial_for(ch.get("discipline", ""), ch.get("title", ""))
    pitfalls = "; ".join((tut or {}).get("pitfalls") or [])[:400] or "(none recorded)"
    causes: dict[str, int] = {}
    for it in snap["wrong"]:
        if it.get("chapter_id") != worst["chapter_id"]:
            continue
        key = snap["stored_causes"].get(it["question_id"], "unlabeled")
        causes[key] = causes.get(key, 0) + 1
    cause_txt = ", ".join("%s ×%d" % (k, v) for k, v in causes.items()) or "unlabeled"
    prompt = (
        "You are the Gabay study coach. Using ONLY the data below, write one "
        "short autopsy paragraph (max 90 words, English, plain text) explaining "
        "why this chapter keeps costing the learner points, connecting their "
        "miss-cause pattern to the recorded pitfalls of the chapter. No invented "
        "content.\n\n"
        f"Chapter: {title} — accuracy {worst['pct']}%.\n"
        f"Miss causes in this chapter: {cause_txt}.\n"
        f"Recorded pitfalls: {pitfalls}"
    )
    key = ("autopsy", username, str(timezone.localdate()))
    text = _cached(key, username, prompt, max_tokens=220, refresh=refresh)
    return {"title": title, "text": text} if text else None


def bridge_brief(username: str, snap: dict | None = None,
                 refresh: bool = False) -> dict | None:
    """Connect the top TWO weak chapters: how the concepts support each other
    and one integrated example; None when fewer than two weak chapters."""
    snap = snap or _snapshot(username)
    if len(snap["weak"]) < 2:
        return None
    from .content import chapters_store, tutorial_for

    chs = chapters_store()
    a, b = snap["weak"][:2]
    prose_bits = []
    for w in (a, b):
        ch = chs.get(w["chapter_id"]) or {}
        tut = tutorial_for(ch.get("discipline", ""), ch.get("title", "")) or {}
        kps = "; ".join((tut.get("key_points") or [])[:2])[:300]
        prose_bits.append(f"{w['title']} ({w['pct']}%): {kps}")
    prompt = (
        "You are the Gabay study coach. Using ONLY the data below, write one "
        "short paragraph (max 100 words, English, plain text) showing how these "
        "two weak chapters support each other — one integrated idea the learner "
        "can use on both. No invented content.\n\n"
        + "\n".join(prose_bits)
    )
    key = ("bridge", username, str(timezone.localdate()))
    text = _cached(key, username, prompt, max_tokens=240, refresh=refresh)
    if not text:
        return None
    return {"title": f'{a["title"]} ↔ {b["title"]}', "text": text}
