from django.http import Http404
from django.shortcuts import render

from .diseases import all_diseases, get_disease


def home(request):
    diseases = all_diseases()
    featured_slugs = [
        "tuberculosis",
        "dengue",
        "type-2-diabetes",
        "myocardial-infarction",
    ]
    featured = [get_disease(s) for s in featured_slugs if get_disease(s)]
    return render(
        request,
        "portal/home.html",
        {
            "featured": featured,
            "disease_count": len(diseases),
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
        {
            "disease": disease,
            "neighbors": others[:4],
        },
    )
