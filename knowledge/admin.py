from django.contrib import admin

from .models import ChapterNote, DiseaseArticle, PracticeQuestion, SubjectRef


@admin.register(SubjectRef)
class SubjectRefAdmin(admin.ModelAdmin):
    list_display = ("slug", "label_en", "label_zh", "kind", "updated_at")
    search_fields = ("slug", "label_en", "label_zh")


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
