from django.db import models
from django.utils import timezone


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


class AIProvider(models.Model):
    """A chat-completion backend the study coach can use.

    Managed by staff in the admin UI: add, delete, and pick the active one.
    Exactly one row should be active at a time; the coach calls that row.
    """

    STYLE_CHOICES = [
        ("openai", "OpenAI-compatible"),
        ("anthropic", "Anthropic"),
    ]

    name = models.CharField(max_length=120, unique=True, help_text="Display label")
    api_style = models.CharField(max_length=16, choices=STYLE_CHOICES, default="openai")
    base_url = models.CharField(
        max_length=300, help_text="API root, e.g. https://api.openai.com/v1"
    )
    model_id = models.CharField(max_length=120, help_text="Model id sent to the API")
    api_key = models.CharField(
        max_length=400, blank=True, help_text="Stored server-side only; masked in UI"
    )
    is_active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_active", "name"]
        verbose_name = "AI provider"

    def __str__(self) -> str:
        return f"{self.name} ({self.model_id})"


class ExamAttempt(models.Model):
    """One full-length mock-exam sitting.

    `plan` freezes the exam blueprint (block → ordered item ids) at start so
    later bank edits can't shift a running exam. `sections` carries per-block
    clocks as epoch ints (started_ts/finished_ts) — display datetimes live in
    real columns. `answers` stores captured state only ({item_id: {c, f}});
    correctness is derived once at finalize, never stored twice.
    """

    STATUS = [("active", "active"), ("submitted", "submitted"), ("expired", "expired")]

    profile = models.ForeignKey(
        LearnerProfile, on_delete=models.CASCADE, related_name="exam_attempts"
    )
    exam = models.SlugField(max_length=20)  # nmat | mcat | demo
    mode = models.CharField(max_length=12, default="real")
    status = models.CharField(max_length=12, choices=STATUS, default="active")
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    plan = models.JSONField(default=dict)
    sections = models.JSONField(default=list)
    answers = models.JSONField(default=dict)
    num_correct = models.IntegerField(null=True)
    num_items = models.IntegerField(null=True)
    score = models.JSONField(null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["profile", "exam"]),
            models.Index(fields=["profile", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "exam"],
                condition=models.Q(status="active"),
                name="uniq_active_attempt_per_exam",
            )
        ]

    def __str__(self) -> str:
        return f"{self.profile_id}:{self.exam}:{self.status}"


class ExamResponse(models.Model):
    """Immutable per-item graded record, written once at finalize."""

    attempt = models.ForeignKey(
        ExamAttempt, on_delete=models.CASCADE, related_name="responses"
    )
    item_id = models.CharField(max_length=64)
    block_id = models.CharField(max_length=40)
    chapter_id = models.CharField(max_length=120, blank=True)
    position = models.IntegerField()
    chosen = models.CharField(max_length=1, blank=True)  # "" = unanswered
    correct = models.BooleanField(default=False)
    flagged = models.BooleanField(default=False)
    time_spent = models.IntegerField(null=True, blank=True)  # seconds on the item

    class Meta:
        unique_together = [("attempt", "position")]
        indexes = [
            models.Index(fields=["attempt", "correct"]),
            models.Index(fields=["chapter_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.attempt_id}:{self.position}:{self.chosen or '-'}"


class StudyPlan(models.Model):
    """Exam-date + hours config; the day-by-day plan itself is derived."""

    profile = models.OneToOneField(
        LearnerProfile, on_delete=models.CASCADE, related_name="study_plan"
    )
    exam = models.SlugField(max_length=20)
    exam_date = models.DateField()
    weekly_hours = models.PositiveIntegerField(default=10)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.profile_id}:{self.exam}:{self.exam_date}"


class SrsCard(models.Model):
    """Spaced-repetition state for one flashcard, per learner (SM-2 style).

    card_key is a stable content hash (chapter + card text) so content edits
    never orphan scheduling state.
    """

    profile = models.ForeignKey(
        LearnerProfile, on_delete=models.CASCADE, related_name="srs_cards"
    )
    subject_slug = models.SlugField(max_length=80)
    card_key = models.CharField(max_length=40)
    front = models.CharField(max_length=400)
    back = models.CharField(max_length=600, blank=True)
    chapter = models.CharField(max_length=200, blank=True)
    ease = models.FloatField(default=2.5)
    interval_days = models.IntegerField(default=0)
    due_date = models.DateField(default=timezone.localdate)
    reps = models.IntegerField(default=0)
    lapses = models.IntegerField(default=0)

    class Meta:
        unique_together = [("profile", "card_key")]
        indexes = [models.Index(fields=["profile", "due_date"])]

    def __str__(self) -> str:
        return f"{self.profile_id}:{self.card_key[:12]} @{self.due_date}"


class ReviewNote(models.Model):
    """Per-learner miss-cause label for a wrong answer (the review-loop
    taxonomy: content gap / misread / careless slip / trap option)."""

    CAUSES = [
        ("content", "Content gap"),
        ("misread", "Misread the stem"),
        ("careless", "Careless slip"),
        ("trap", "Trap option"),
    ]

    profile = models.ForeignKey(
        LearnerProfile, on_delete=models.CASCADE, related_name="review_notes"
    )
    question_id = models.CharField(max_length=64)
    cause = models.CharField(max_length=12, choices=CAUSES)
    note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("profile", "question_id")]

    def __str__(self) -> str:
        return f"{self.profile_id}:{self.question_id}:{self.cause}"
