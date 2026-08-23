from django import template

register = template.Library()


@register.filter
def zip_en(points, points_en):
    """Pair zh points with en points; fall back to the zh string if en missing."""
    pts = list(points or [])
    ens = list(points_en or [])
    out = []
    for i, zh in enumerate(pts):
        en = ens[i] if i < len(ens) else zh
        out.append({"zh": zh, "en": en})
    return out
