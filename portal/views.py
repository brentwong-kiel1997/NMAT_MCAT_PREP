from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST
import json

from .diseases import all_diseases, get_disease
from . import exams
from .minimax import chat_completion, minimax_config
from .study import build_curriculum_context, tutor_messages


def home(request):
    return render(
        request,
        "portal/home.html",
        {
            "shared_subjects": exams.shared_list(),
            "nmat": exams.NMAT,
            "mcat": exams.MCAT,
            "tutor_ready": bool(minimax_config()["api_key"]),
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
    chapters = []
    for group in subject.get("chapters", []):
        for item in group.get("items", []):
            chapters.append(item["title"])
    return render(
        request,
        "portal/subject_detail.html",
        {
            "subject": subject,
            "tutor_context": {
                "exam": "SHARED",
                "subject_slug": subject["slug"],
                "section_slug": "",
                "label": subject["name"],
                "chapters": chapters,
            },
        },
    )


def nmat_hub(request):
    return render(
        request,
        "portal/nmat_hub.html",
        {"exam": exams.NMAT, "shared": exams.SHARED_SUBJECTS},
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
    chapters = []
    for group in subject.get("chapters", []):
        for item in group.get("items", []):
            chapters.append(item["title"])
    return render(
        request,
        "portal/nmat_subject.html",
        {
            "exam": exams.NMAT,
            "subject": subject,
            "tutor_context": {
                "exam": "NMAT",
                "subject_slug": subject["slug"],
                "section_slug": "",
                "label": f"NMAT · {subject['name']}",
                "chapters": chapters,
            },
        },
    )


def mcat_hub(request):
    return render(
        request,
        "portal/mcat_hub.html",
        {"exam": exams.MCAT, "shared": exams.SHARED_SUBJECTS},
    )


def mcat_section(request, slug):
    section = exams.get_mcat_section(slug)
    if not section:
        raise Http404("MCAT section not found")
    linked = [
        exams.get_shared(s) for s in section.get("shared_links", []) if exams.get_shared(s)
    ]
    chapters = []
    for group in section.get("chapters", []):
        for item in group.get("items", []):
            chapters.append(item["title"])
    return render(
        request,
        "portal/mcat_section.html",
        {
            "exam": exams.MCAT,
            "section": section,
            "linked_subjects": linked,
            "tutor_context": {
                "exam": "MCAT",
                "subject_slug": "",
                "section_slug": section["slug"],
                "label": f"MCAT · {section['short']}",
                "chapters": chapters,
            },
        },
    )


@require_GET
def study_hub(request):
    return render(
        request,
        "portal/study.html",
        {
            "shared_subjects": exams.shared_list(),
            "nmat_unique": exams.nmat_unique_subjects(),
            "mcat_sections": exams.MCAT["sections"],
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
