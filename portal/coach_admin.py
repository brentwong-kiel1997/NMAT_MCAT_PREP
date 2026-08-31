"""Staff views to manage the study coach's AI providers (add/delete/switch)."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .models import AIProvider


def _staff_required(user) -> bool:
    return bool(user.is_authenticated and user.is_staff)


@require_http_methods(["GET", "POST"])
@login_required
@user_passes_test(_staff_required)
def manage_models(request):
    error = ""
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        api_style = request.POST.get("api_style") or ""
        base_url = (request.POST.get("base_url") or "").strip().rstrip("/")
        model_id = (request.POST.get("model_id") or "").strip()
        api_key = (request.POST.get("api_key") or "").strip()
        if (
            not name
            or api_style not in dict(AIProvider.STYLE_CHOICES)
            or not base_url.startswith(("http://", "https://"))
            or not model_id
        ):
            error = "invalid"
        elif AIProvider.objects.filter(name=name).exists():
            error = "exists"
        else:
            make_active = request.POST.get("make_active") == "on" or not AIProvider.objects.exists()
            if make_active:
                AIProvider.objects.update(is_active=False)
            provider = AIProvider.objects.create(
                name=name,
                api_style=api_style,
                base_url=base_url,
                model_id=model_id,
                is_active=make_active,
            )
            provider.set_api_key(api_key)
            provider.save(update_fields=["api_key_enc", "updated_at"])
            messages.success(request, f"Added model {name}.")
            return redirect("manage_models")

    providers = list(AIProvider.objects.all())
    return render(
        request,
        "portal/manage_models.html",
        {
            "providers": providers,
            "create_error": error,
            "styles": AIProvider.STYLE_CHOICES,
            "coach_label": "",  # context processor overrides
        },
    )


@require_POST
@login_required
@user_passes_test(_staff_required)
def manage_model_action(request, provider_id: int):
    provider = get_object_or_404(AIProvider, id=provider_id)
    action = request.POST.get("action") or ""
    if action == "activate":
        AIProvider.objects.update(is_active=False)
        provider.is_active = True
        provider.save(update_fields=["is_active", "updated_at"])
        messages.success(request, f"Study coach now uses {provider.name}.")
    elif action == "delete":
        was_active = provider.is_active
        name = provider.name
        provider.delete()
        if was_active:
            next_one = AIProvider.objects.first()
            if next_one:
                next_one.is_active = True
                next_one.save(update_fields=["is_active", "updated_at"])
                messages.warning(
                    request,
                    f"Deleted {name}; coach switched to {next_one.name}.",
                )
            else:
                messages.warning(
                    request, f"Deleted {name}; no models remain — coach is offline."
                )
        else:
            messages.success(request, f"Deleted {name}.")
    return redirect("manage_models")
