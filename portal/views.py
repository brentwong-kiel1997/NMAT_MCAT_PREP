from django.http import Http404
from django.shortcuts import redirect, render

from .diseases import all_diseases, get_disease
from . import exams


def home(request):
    return render(
        request,
        "portal/home.html",
        {
            "shared_subjects": exams.shared_list(),
            "nmat": exams.NMAT,
            "mcat": exams.MCAT,
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
    return render(
        request,
        "portal/subject_detail.html",
        {"subject": subject},
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
        # Part 2 aliases → shared pages
        aliases = {
            "biology": "biology",
            "physics": "physics",
            "chemistry": "chemistry",
            "social-science": "behavioral-social",
        }
        if slug in aliases:
            return redirect("subject_detail", slug=aliases[slug])
        raise Http404("NMAT subject not found")
    return render(
        request,
        "portal/nmat_subject.html",
        {"exam": exams.NMAT, "subject": subject},
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
    return render(
        request,
        "portal/mcat_section.html",
        {"exam": exams.MCAT, "section": section, "linked_subjects": linked},
    )
