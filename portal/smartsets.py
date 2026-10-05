"""Smart sets: timed practice composed from the learner's weakest chapters.

Deterministic given (user, day, seed-param) so a reload or a shared link
shows the same set; grading flows through the existing bank fallback in
practice_attempt_api, so attempts still feed the accuracy aggregations.
"""

from __future__ import annotations

import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from . import insights
from .content import all_bank_items, chapters_store
from .learners import get_or_create_profile
from .views import _json_for_script

_SET_SIZE = 10
_SECONDS_PER_ITEM = 75


def _compose(username: str, count: int, seed_extra: str) -> tuple[list, list]:
    """(items, weak_used) — items drawn round-robin from the weakest
    chapters, bank items only (server-judged)."""
    profile = get_or_create_profile(username)
    weak = insights.wrong_chapters(profile, limit=5)
    bank = all_bank_items()
    by_chapter: dict[str, list] = {}
    for w in weak:
        pool = [b for b in bank.values()
                if b.get("chapter") == w["chapter_id"]
                and b.get("q") and b.get("answer") in (b.get("choices") or {})]
        rng = random.Random(f"{username}:{seed_extra}:{w['chapter_id']}")
        rng.shuffle(pool)
        if pool:
            by_chapter[w["chapter_id"]] = pool
    items, used = [], []
    pools = list(by_chapter.values())
    while len(items) < count and any(pools):
        for pool in pools:
            if pool and len(items) < count:
                b = pool.pop(0)
                items.append({"id": b["id"], "q": b["q"],
                              "choices": b.get("choices") or {},
                              "answer": b["answer"],
                              "explain": b.get("explain", ""),
                              "chapter": next(
                                  (w["title"] for w in weak
                                   if w["chapter_id"] == b.get("chapter")), "")})
        used = list(by_chapter.keys())
    # chapter titles for display
    chs = chapters_store()
    used_titles = [chs.get(cid, {}).get("title", cid) for cid in used]
    return items, used_titles


@login_required
@require_GET
def smart_set(request):
    username = request.user.username
    try:
        count = min(20, max(5, int(request.GET.get("count") or _SET_SIZE)))
    except (TypeError, ValueError):
        count = _SET_SIZE
    gen = request.GET.get("new")
    seed_extra = f"gen:{gen}" if gen else "default"
    items, used_titles = _compose(username, count, seed_extra)
    if not items:
        # no mock/practice history yet — send the learner to build some
        return redirect("exam_list")
    seconds = items and len(items) * _SECONDS_PER_ITEM
    return render(request, "portal/smart_set.html", {
        "items": items,
        "items_json": _json_for_script(items),
        "total": len(items),
        "seconds": seconds,
        "weak_used": used_titles,
    })
