from django.contrib import admin

from .models import ChapterProgress, LearnerProfile, PracticeAttempt


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
