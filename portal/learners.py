"""Learner progress helpers on the user database."""

from __future__ import annotations

from .models import ChapterProgress, LearnerProfile, PracticeAttempt


def get_or_create_profile(username: str) -> LearnerProfile:
    name = (username or "guest").strip()[:150] or "guest"
    profile, _ = LearnerProfile.objects.get_or_create(
        username=name, defaults={"display_name": name}
    )
    return profile


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
