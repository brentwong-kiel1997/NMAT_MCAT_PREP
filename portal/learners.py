"""Learner progress helpers on the user database."""

from __future__ import annotations

from django.contrib.auth.models import User
from django.db.models import Count, Q

from .models import ChapterProgress, LearnerProfile, PracticeAttempt


def get_or_create_profile(username: str, display_name: str = "") -> LearnerProfile:
    name = (username or "guest").strip()[:150] or "guest"
    profile, created = LearnerProfile.objects.get_or_create(
        username=name,
        defaults={"display_name": (display_name or name)[:150]},
    )
    if not created and display_name and not profile.display_name:
        profile.display_name = display_name[:150]
        profile.save(update_fields=["display_name"])
    return profile


def ensure_profile_for_user(user: User, display_name: str = "") -> LearnerProfile:
    return get_or_create_profile(
        user.username,
        display_name=display_name or user.get_full_name() or user.username,
    )


def progress_map(username: str, subject_slug: str) -> dict[str, int]:
    profile = get_or_create_profile(username)
    rows = ChapterProgress.objects.filter(
        profile=profile, subject_slug=subject_slug, done=True
    ).values_list("chapter_id", flat=True)
    return {cid: 1 for cid in rows}


def set_chapter_done(username: str, subject_slug: str, chapter_id: str, done: bool) -> None:
    profile = get_or_create_profile(username)
    if done:
        ChapterProgress.objects.update_or_create(
            profile=profile,
            subject_slug=subject_slug,
            chapter_id=chapter_id,
            defaults={"done": True},
        )
    else:
        ChapterProgress.objects.filter(
            profile=profile, subject_slug=subject_slug, chapter_id=chapter_id
        ).delete()


def record_practice(
    username: str, subject_slug: str, question_id: str, chosen: str, correct: bool
) -> None:
    profile = get_or_create_profile(username)
    PracticeAttempt.objects.create(
        profile=profile,
        subject_slug=subject_slug,
        question_id=question_id,
        chosen=chosen[:1].upper(),
        correct=correct,
    )


def learner_stats(profile: LearnerProfile) -> dict:
    chapters = ChapterProgress.objects.filter(profile=profile, done=True).count()
    attempts = PracticeAttempt.objects.filter(profile=profile)
    total = attempts.count()
    correct = attempts.filter(correct=True).count()
    by_subject = list(
        ChapterProgress.objects.filter(profile=profile, done=True)
        .values("subject_slug")
        .annotate(n=Count("id"))
        .order_by("-n")
    )
    return {
        "chapters_done": chapters,
        "attempts": total,
        "correct": correct,
        "accuracy": round(100.0 * correct / total, 1) if total else 0.0,
        "by_subject": by_subject,
    }
