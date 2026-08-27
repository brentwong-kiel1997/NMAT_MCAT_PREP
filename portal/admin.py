from django.contrib import admin

from .models import (
    ChapterProgress,
    ExamAttempt,
    ExamResponse,
    LearnerProfile,
    PracticeAttempt,
    StudyPlan,
)


@admin.register(LearnerProfile)
class LearnerProfileAdmin(admin.ModelAdmin):
    list_display = ("username", "display_name", "created_at", "updated_at")
    search_fields = ("username", "display_name")


@admin.register(ChapterProgress)
class ChapterProgressAdmin(admin.ModelAdmin):
    list_display = ("profile", "subject_slug", "chapter_id", "done", "updated_at")
    list_filter = ("subject_slug", "done")


@admin.register(PracticeAttempt)
class PracticeAttemptAdmin(admin.ModelAdmin):
    list_display = ("profile", "subject_slug", "question_id", "chosen", "correct", "created_at")
    list_filter = ("subject_slug", "correct")

@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "exam", "status", "num_correct", "num_items", "started_at")
    list_filter = ("exam", "status")
    search_fields = ("profile__username",)


@admin.register(ExamResponse)
class ExamResponseAdmin(admin.ModelAdmin):
    list_display = ("attempt", "position", "item_id", "chosen", "correct", "chapter_id")
    list_filter = ("block_id", "correct")


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = ("profile", "exam", "exam_date", "weekly_hours")
