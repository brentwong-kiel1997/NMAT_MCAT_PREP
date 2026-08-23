from django.db import models


class SubjectRef(models.Model):
    """Catalog entry for a studyable slug (shared / NMAT / MCAT)."""

    KIND_CHOICES = (
        ("shared", "Shared"),
        ("nmat", "NMAT unique"),
        ("mcat", "MCAT section"),
    )

    slug = models.SlugField(max_length=80, unique=True)
    label_zh = models.CharField(max_length=120)
    label_en = models.CharField(max_length=120)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES, default="shared")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self) -> str:
        return self.slug


class CurriculumSubject(models.Model):
    """Full subject/section outline stored in the knowledge database."""

    KIND_CHOICES = SubjectRef.KIND_CHOICES

    slug = models.SlugField(max_length=80, unique=True)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES, default="shared")
    name = models.CharField(max_length=160)
    name_zh = models.CharField(max_length=160, blank=True)
    summary = models.TextField(blank=True)
    payload = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["kind", "slug"]

    def __str__(self) -> str:
        return f"{self.kind}:{self.slug}"

    def as_dict(self) -> dict:
        data = dict(self.payload or {})
        data.setdefault("slug", self.slug)
        data.setdefault("name", self.name)
        if self.name_zh:
            data.setdefault("name_zh", self.name_zh)
        if self.summary:
            data.setdefault("summary", self.summary)
        return data


class OutlineChapter(models.Model):
    """Normalized chapter row for SQL queries / joins with notes."""

    subject_slug = models.SlugField(max_length=80, db_index=True)
    group_heading = models.CharField(max_length=240, blank=True)
    title = models.CharField(max_length=240)
    sort_order = models.PositiveSmallIntegerField(default=0)
    points = models.JSONField(default=list)

    class Meta:
        ordering = ["subject_slug", "sort_order", "id"]
        indexes = [
            models.Index(fields=["subject_slug", "title"]),
        ]

    def __str__(self) -> str:
        return f"{self.subject_slug}:{self.title[:40]}"


class ChapterNote(models.Model):
    """High-yield bilingual note under a chapter title."""

    subject_slug = models.SlugField(max_length=80, db_index=True)
    chapter_title = models.CharField(max_length=240, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    text_zh = models.TextField()
    text_en = models.TextField()

    class Meta:
        ordering = ["subject_slug", "chapter_title", "sort_order", "id"]
        indexes = [
            models.Index(fields=["subject_slug", "chapter_title"]),
        ]

    def __str__(self) -> str:
        return f"{self.subject_slug}:{self.chapter_title[:40]}"


class PracticeQuestion(models.Model):
    """Static practice MCQ (not official past papers)."""

    subject_slug = models.SlugField(max_length=80, db_index=True)
    qid = models.CharField(max_length=64)
    chapter = models.CharField(max_length=240, blank=True)
    q_zh = models.TextField()
    q_en = models.TextField()
    choices = models.JSONField(default=dict)
    answer = models.CharField(max_length=1)
    explain_zh = models.TextField(blank=True)
    explain_en = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["subject_slug", "sort_order", "id"]
        unique_together = [("subject_slug", "qid")]

    def __str__(self) -> str:
        return self.qid

    def as_dict(self) -> dict:
        return {
            "id": self.qid,
            "q_zh": self.q_zh,
            "q_en": self.q_en,
            "choices": self.choices,
            "answer": self.answer,
            "explain_zh": self.explain_zh,
            "explain_en": self.explain_en,
            "chapter": self.chapter,
        }


class DiseaseArticle(models.Model):
    """Enrichment disease page payload stored as JSON."""

    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=160)
    name_zh = models.CharField(max_length=160)
    short = models.TextField(blank=True)
    payload = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self) -> str:
        return self.slug

    def as_dict(self) -> dict:
        data = dict(self.payload or {})
        data.setdefault("slug", self.slug)
        data.setdefault("name", self.name)
        data.setdefault("name_zh", self.name_zh)
        data.setdefault("short", self.short)
        return data
