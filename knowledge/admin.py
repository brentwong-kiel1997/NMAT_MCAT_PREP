from django.contrib import admin

from .models import (
    ChapterNote,
    CurriculumSubject,
    DiseaseArticle,
    OutlineChapter,
    PracticeQuestion,
    SubjectRef,
)


@admin.register(SubjectRef)
class SubjectRefAdmin(admin.ModelAdmin):
    list_display = ("slug", "label_en", "label_zh", "kind", "updated_at")
    search_fields = ("slug", "label_en", "label_zh")


@admin.register(CurriculumSubject)
class CurriculumSubjectAdmin(admin.ModelAdmin):
    list_display = ("slug", "kind", "name", "name_zh", "updated_at")
    list_filter = ("kind",)
    search_fields = ("slug", "name", "name_zh")


@admin.register(OutlineChapter)
class OutlineChapterAdmin(admin.ModelAdmin):
    list_display = ("subject_slug", "sort_order", "title", "group_heading")
    list_filter = ("subject_slug",)
    search_fields = ("title", "group_heading")


@admin.register(ChapterNote)
class ChapterNoteAdmin(admin.ModelAdmin):
    list_display = ("subject_slug", "chapter_title", "sort_order")
    list_filter = ("subject_slug",)
    search_fields = ("chapter_title", "text_zh", "text_en")


@admin.register(PracticeQuestion)
class PracticeQuestionAdmin(admin.ModelAdmin):
    list_display = ("qid", "subject_slug", "answer", "chapter")
    list_filter = ("subject_slug",)
    search_fields = ("qid", "q_zh", "q_en")


@admin.register(DiseaseArticle)
class DiseaseArticleAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "name_zh", "updated_at")
    search_fields = ("slug", "name", "name_zh")
