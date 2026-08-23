from django.db import models


class LearnerProfile(models.Model):
    """App-side learner identity (separate from knowledge content DB).

    Can mirror nginx basic-auth usernames or future Django auth users.
    """

    username = models.CharField(max_length=150, unique=True)
    display_name = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.username


class ChapterProgress(models.Model):
    """Server-side chapter completion (optional; UI also keeps localStorage)."""

    profile = models.ForeignKey(
        LearnerProfile, on_delete=models.CASCADE, related_name="chapter_progress"
    )
    subject_slug = models.SlugField(max_length=80)
    chapter_id = models.CharField(max_length=120)
    done = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("profile", "subject_slug", "chapter_id")]
        indexes = [
            models.Index(fields=["profile", "subject_slug"]),
        ]

    def __str__(self) -> str:
        return f"{self.profile_id}:{self.subject_slug}:{self.chapter_id}"


class PracticeAttempt(models.Model):
    """Per-question practice attempt for a learner."""

    profile = models.ForeignKey(
        LearnerProfile, on_delete=models.CASCADE, related_name="practice_attempts"
    )
    subject_slug = models.SlugField(max_length=80)
    question_id = models.CharField(max_length=64)
    chosen = models.CharField(max_length=1)
    correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["profile", "subject_slug"]),
        ]

    def __str__(self) -> str:
        return f"{self.profile_id}:{self.question_id}:{self.chosen}"
