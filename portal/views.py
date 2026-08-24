from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST
import json

from .diseases import all_diseases, get_disease
from . import exams
from .learners import progress_map, record_practice, set_chapter_done
from .materials import (
    exam_checklists,
    exam_tips,
    formula_catalog,
    formulas_for,
    glossary_subject_slugs,
    glossary_terms,
    study_paths,
)
from .minimax import chat_completion, minimax_config
from .notes import flashcards_for
from .practice import practice_for, practice_catalog, all_practice_slugs, LABELS
from .study import build_curriculum_context, tutor_messages


def _learner_name(request) -> str:
    if getattr(request, "user", None) is not None and request.user.is_authenticated:
        return request.user.username
    return (
        request.META.get("HTTP_X_REMOTE_USER")
        or request.headers.get("X-Remote-User")
        or ""
    ).strip() or "guest"


def _json_for_script(data) -> str:
    return json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")


def _chapter_titles(entity: dict) -> list[str]:
    chapters = []
    for group in entity.get("chapters", []):
        for item in group.get("items", []):
            chapters.append(item["title"])
    return chapters


def _study_extras(slug: str, entity: dict) -> dict:
    cards = flashcards_for(slug, limit=60)
    items = practice_for(slug)
    formulas = formulas_for(slug)
    return {
        "chapters_for_toc": entity.get("chapters") or [],
        "progress_key": f"gabay_progress_{slug}",
        "progress_subject": slug,
        "practice_slug": slug if items else "",
        "practice_count": len(items),
        "flashcards": cards,
        "flashcards_json": _json_for_script(cards),
        "formula_count": len(formulas),
        "has_formulas": bool(formulas),
    }


def home(request):
    return render(
        request,
        "portal/home.html",
        {
            "shared_subjects": exams.shared_list(),
            "nmat": exams.nmat_exam(),
            "mcat": exams.mcat_exam(),
            "tutor_ready": bool(minimax_config()["api_key"]),
            "practice_catalog": practice_catalog()[:6],
        },
    )


def disease_list(request):
    return render(
        request,
        "portal/disease_list.html",
        {"diseases": all_diseases()},
    )


def disease_detail(request, slug):
    disease = get_disease(slug)
    if not disease:
        raise Http404("Disease not found")
    others = [d for d in all_diseases() if d["slug"] != slug]
    return render(
        request,
        "portal/disease_detail.html",
        {"disease": disease, "neighbors": others[:4]},
    )


def subject_list(request):
    return render(
        request,
        "portal/subject_list.html",
        {"subjects": exams.shared_list()},
    )


def subject_detail(request, slug):
    subject = exams.get_shared(slug)
    if not subject:
        raise Http404("Subject not found")
    ctx = {
        "subject": subject,
        "tutor_context": {
            "exam": "SHARED",
            "subject_slug": subject["slug"],
            "section_slug": "",
            "label": subject["name"],
            "chapters": _chapter_titles(subject),
        },
    }
    ctx.update(_study_extras(slug, subject))
    return render(request, "portal/subject_detail.html", ctx)


def nmat_hub(request):
    return render(
        request,
        "portal/nmat_hub.html",
        {"exam": exams.nmat_exam()},
    )


def nmat_subject(request, slug):
    subject = exams.get_nmat_unique(slug)
    if not subject:
        aliases = {
            "biology": "biology",
            "physics": "physics",
            "chemistry": "chemistry",
            "social-science": "behavioral-social",
        }
        if slug in aliases:
            return redirect("subject_detail", slug=aliases[slug])
        raise Http404("NMAT subject not found")
    ctx = {
        "exam": exams.nmat_exam(),
        "subject": subject,
        "tutor_context": {
            "exam": "NMAT",
            "subject_slug": subject["slug"],
            "section_slug": "",
            "label": f"NMAT · {subject['name']}",
            "chapters": _chapter_titles(subject),
        },
    }
    ctx.update(_study_extras(slug, subject))
    return render(request, "portal/nmat_subject.html", ctx)


def mcat_hub(request):
    return render(
        request,
        "portal/mcat_hub.html",
        {"exam": exams.mcat_exam()},
    )


def mcat_section(request, slug):
    section = exams.get_mcat_section(slug)
    if not section:
        raise Http404("MCAT section not found")
    linked = [
        exams.get_shared(s) for s in section.get("shared_links", []) if exams.get_shared(s)
    ]
    ctx = {
        "exam": exams.mcat_exam(),
        "section": section,
        "linked_subjects": linked,
        "tutor_context": {
            "exam": "MCAT",
            "subject_slug": "",
            "section_slug": section["slug"],
            "label": f"MCAT · {section['short']}",
            "chapters": _chapter_titles(section),
        },
    }
    ctx.update(_study_extras(slug, section))
    return render(request, "portal/mcat_section.html", ctx)


@require_GET
def study_hub(request):
    return render(
        request,
        "portal/study.html",
        {
            "shared_subjects": exams.shared_list(),
            "nmat_unique": exams.nmat_unique_subjects(),
            "mcat_sections": exams.mcat_exam()["sections"],
            "practice_catalog": practice_catalog(),
            "study_paths": study_paths(),
            "tutor_ready": bool(minimax_config()["api_key"]),
            "tutor_context": {
                "exam": "",
                "subject_slug": "",
                "section_slug": "",
                "label": "General",
                "chapters": [],
            },
        },
    )


@require_GET
def materials_hub(request):
    return render(
        request,
        "portal/materials_hub.html",
        {
            "paths": study_paths(),
            "tips": exam_tips()[:6],
            "checklists": exam_checklists(),
            "formula_catalog": formula_catalog(),
            "glossary_count": len(glossary_terms()),
            "practice_catalog": practice_catalog()[:8],
        },
    )


@require_GET
def materials_glossary(request):
    q = (request.GET.get("q") or "").strip()
    subject = (request.GET.get("subject") or "").strip()
    return render(
        request,
        "portal/materials_glossary.html",
        {
            "terms": glossary_terms(q, subject),
            "q": q,
            "subject": subject,
            "subject_filters": glossary_subject_slugs(),
        },
    )


@require_GET
def materials_formulas(request, slug: str):
    items = formulas_for(slug)
    if not items:
        raise Http404("Formula sheet not found")
    label = LABELS.get(slug, {"zh": slug, "en": slug})
    return render(
        request,
        "portal/materials_formulas.html",
        {
            "slug": slug,
            "label_zh": label["zh"],
            "label_en": label["en"],
            "items": items,
            "catalog": formula_catalog(),
        },
    )


@require_GET
def materials_tips(request):
    exam = (request.GET.get("exam") or "").strip().upper()
    tips = exam_tips(exam) if exam in {"NMAT", "MCAT", "BOTH"} else exam_tips()
    return render(
        request,
        "portal/materials_tips.html",
        {"tips": tips, "exam": exam},
    )


@require_GET
def materials_checklists(request):
    exam = (request.GET.get("exam") or "").strip().upper()
    items = exam_checklists(exam) if exam in {"NMAT", "MCAT", "BOTH"} else exam_checklists()
    return render(
        request,
        "portal/materials_checklists.html",
        {"checklists": items, "exam": exam},
    )


@require_GET
def practice_hub(request):
    return render(
        request,
        "portal/practice_hub.html",
        {"catalog": practice_catalog()},
    )


@require_GET
def practice_detail(request, slug):
    items = practice_for(slug)
    if not items:
        raise Http404("Practice set not found")

    label = LABELS.get(slug, {"zh": slug, "en": slug})
    back = None
    if exams.get_shared(slug):
        back = ("subject_detail", slug)
    elif exams.get_nmat_unique(slug):
        back = ("nmat_subject", slug)
    elif exams.get_mcat_section(slug):
        back = ("mcat_section", slug)

    return render(
        request,
        "portal/practice_detail.html",
        {
            "slug": slug,
            "label_zh": label["zh"],
            "label_en": label["en"],
            "items": items,
            "items_json": _json_for_script(items),
            "back": back,
            "all_slugs": all_practice_slugs(),
        },
    )


@require_GET
def progress_api(request):
    subject_slug = (request.GET.get("subject_slug") or "").strip()
    if not subject_slug:
        return JsonResponse({"ok": False, "error": "subject_slug required"}, status=400)
    username = _learner_name(request)
    return JsonResponse(
        {
            "ok": True,
            "username": username,
            "subject_slug": subject_slug,
            "done": progress_map(username, subject_slug),
        }
    )


@require_POST
def progress_update_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    subject_slug = (payload.get("subject_slug") or "").strip()
    chapter_id = (payload.get("chapter_id") or "").strip()
    if not subject_slug or not chapter_id:
        return JsonResponse(
            {"ok": False, "error": "subject_slug and chapter_id required"}, status=400
        )
    done = bool(payload.get("done", True))
    username = _learner_name(request)
    set_chapter_done(username, subject_slug, chapter_id, done)
    return JsonResponse(
        {
            "ok": True,
            "username": username,
            "done": progress_map(username, subject_slug),
        }
    )


@require_POST
def practice_attempt_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    subject_slug = (payload.get("subject_slug") or "").strip()
    question_id = (payload.get("question_id") or "").strip()
    chosen = (payload.get("chosen") or "").strip().upper()[:1]
    if not subject_slug or not question_id or chosen not in "ABCD":
        return JsonResponse({"ok": False, "error": "Invalid attempt"}, status=400)

    items = {q["id"]: q for q in practice_for(subject_slug)}
    item = items.get(question_id)
    if not item:
        return JsonResponse({"ok": False, "error": "Unknown question"}, status=404)
    correct = chosen == item["answer"]
    username = _learner_name(request)
    record_practice(username, subject_slug, question_id, chosen, correct)
    return JsonResponse(
        {
            "ok": True,
            "correct": correct,
            "answer": item["answer"],
            "username": username,
        }
    )


@require_POST
def study_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)

    mode = (payload.get("mode") or "ask").strip().lower()
    if mode not in {"ask", "explain", "quiz", "grade"}:
        return JsonResponse({"ok": False, "error": "Unsupported mode"}, status=400)

    user_text = (payload.get("message") or "").strip()
    if mode in {"ask", "grade"} and not user_text:
        return JsonResponse({"ok": False, "error": "Message required"}, status=400)
    if len(user_text) > 4000:
        return JsonResponse({"ok": False, "error": "Message too long"}, status=400)

    exam = (payload.get("exam") or "").strip()
    subject_slug = (payload.get("subject_slug") or "").strip()
    section_slug = (payload.get("section_slug") or "").strip()
    chapter_title = (payload.get("chapter") or "").strip()
    lang = (payload.get("lang") or "zh").strip().lower()
    if lang not in {"zh", "en"}:
        lang = "zh"

    curriculum = build_curriculum_context(
        exam=exam,
        subject_slug=subject_slug,
        section_slug=section_slug,
        chapter_title=chapter_title,
    )
    messages = tutor_messages(
        mode=mode,
        user_text=user_text,
        curriculum=curriculum,
        chapter_title=chapter_title,
    )
    if lang == "en":
        messages[0]["content"] += (
            "\nRespond in clear English; keep technical terms standard."
        )
    else:
        messages[0]["content"] += (
            "\n默认中文作答；保留必要英文术语。"
        )

    try:
        answer = chat_completion(messages, max_tokens=1400 if mode == "explain" else 900)
    except RuntimeError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=502)

    return JsonResponse(
        {
            "ok": True,
            "mode": mode,
            "answer": answer,
            "model": minimax_config()["model"],
        }
    )
