"""SM-2-style spaced repetition scheduling + the daily review queue.

Card identity is a stable content hash (subject + chapter + text) so that
content edits never orphan scheduling state. New cards enter the queue
capped per day so a fresh subject doesn't dump 40 cards at once.
"""

from __future__ import annotations

import datetime as dt
import hashlib

from django.utils import timezone

from .content import flashcards_for
from .learners import get_or_create_profile
from .models import SrsCard

NEW_PER_DAY = 10  # per queue render (i.e. per session), not per calendar day


def card_key(subject_slug: str, chapter: str, text: str) -> str:
    digest = hashlib.sha1(f"{subject_slug}|{chapter}|{text}".encode()).hexdigest()
    return digest[:16]


def split_card(text: str) -> tuple[str, str]:
    """"Term: definition" renders as front/back; anything else is a
    front-only self-check card."""
    if ": " in text:
        front, back = text.split(": ", 1)
        return front.strip(), back.strip()
    return text.strip(), ""


def deck_for(subject_slug: str) -> list[dict]:
    """Every card for a subject with its content key (no 40-card cap —
    the whole curriculum belongs in rotation)."""
    out = []
    for card in flashcards_for(subject_slug, limit=None):
        text = card.get("text", "")
        front, back = split_card(text)
        out.append({
            "key": card_key(subject_slug, card.get("chapter", ""), text),
            "front": front,
            "back": back,
            "chapter": card.get("chapter", ""),
        })
    return out


def due_queue(username: str, subject_slug: str | None) -> dict:
    """Today's queue: due reviews first, then up to NEW_PER_DAY unseen cards."""
    profile = get_or_create_profile(username)
    today = timezone.localdate()
    # interval_days=0 cards (lapsed "again") are due immediately — the filter
    # is on due_date alone so they re-enter today's queue instead of vanishing
    reviews = SrsCard.objects.filter(profile=profile).filter(due_date__lte=today)
    if subject_slug:
        reviews = reviews.filter(subject_slug=subject_slug)
    # ghost guard: drop scheduling rows whose card left the content deck
    # (edited notes change their key; the row would otherwise be shown and
    # be ungradable forever)
    live_keys: set[str] = set()
    deck_cache: dict[str, list[dict]] = {}
    for subj in ([subject_slug] if subject_slug else _subjects_with_decks()):
        deck_cache[subj] = deck_for(subj)
        live_keys.update(c["key"] for c in deck_cache[subj])
    due = [c for c in reviews.order_by("due_date") if c.card_key in live_keys]
    # refresh stored text so edited notes show their current wording
    for c in due:
        for subj, deck in deck_cache.items():
            match = next((x for x in deck if x["key"] == c.card_key), None)
            if match:
                changed = (c.front != match["front"] or c.back != match["back"]
                           or c.chapter != match["chapter"])
                if changed:
                    c.front = match["front"][:400]
                    c.back = match["back"][:600]
                    c.chapter = match["chapter"][:200]
                    c.save(update_fields=["front", "back", "chapter"])
                break

    learned_keys = set(SrsCard.objects.filter(profile=profile)
                       .values_list("card_key", flat=True))
    subjects = [subject_slug] if subject_slug else _subjects_with_decks()
    new_cards = []
    for subj in subjects:
        for card in deck_for(subj):
            if card["key"] not in learned_keys:
                new_cards.append({**card, "subject_slug": subj})
    new_cards = new_cards[:NEW_PER_DAY]
    return {"due": due, "new": new_cards}


def _subjects_with_decks() -> list[str]:
    from .content import all_practice_slugs
    return all_practice_slugs()


def get_or_create_srs(username, subject_slug, card_key, front, back, chapter):
    profile = get_or_create_profile(username)
    card, _ = SrsCard.objects.get_or_create(
        profile=profile, card_key=card_key,
        defaults={"subject_slug": subject_slug, "front": front[:400],
                  "back": back[:600], "chapter": chapter[:200],
                  "due_date": timezone.localdate()})
    return card


def grade_card(username: str, subject_slug: str, key: str, front: str,
               back: str, chapter: str, grade: str) -> dict:
    """grade in {again, hard, good, easy}; classic SM-2 adaptation."""
    profile = get_or_create_profile(username)
    card, created = SrsCard.objects.get_or_create(
        profile=profile, card_key=key,
        defaults={"subject_slug": subject_slug, "front": front[:400],
                  "back": back[:600], "chapter": chapter[:200],
                  "ease": 2.5, "interval_days": 0,
                  "due_date": timezone.localdate()},
    )
    ease = card.ease
    interval = card.interval_days
    if grade == "again":
        ease = max(1.3, ease - 0.2)
        interval = 0
        card.lapses = (card.lapses or 0) + 1
    elif grade == "hard":
        ease = max(1.3, ease - 0.15)
        interval = max(1, int(interval * 1.2))
    elif grade == "easy":
        ease = min(3.2, ease + 0.15)
        interval = max(3, round(max(interval, 1) * ease * 1.3)) if interval == 0 else max(interval + 1, round(interval * ease * 1.3))
    else:  # good
        interval = 1 if interval == 0 else max(1, int(interval * ease))
    card.ease = ease
    interval = min(interval, 365)  # clamp BEFORE storing: interval_days and
    card.interval_days = interval  # due_date must never drift apart
    card.due_date = timezone.localdate() + dt.timedelta(days=interval)
    card.reps += 1
    card.save()
    return {"ok": True, "interval_days": interval, "due": card.due_date.isoformat()}


def srs_stats(username: str) -> dict:
    profile = get_or_create_profile(username)
    today = timezone.localdate()
    total = SrsCard.objects.filter(profile=profile).count()
    due = (SrsCard.objects.filter(profile=profile,
                                  due_date__lte=today).count())
    return {"total": total, "due_today": due}
