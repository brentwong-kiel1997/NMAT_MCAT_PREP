"""App login, account, and staff user management (user DB)."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .learners import ensure_profile_for_user, learner_stats


def _staff_required(user) -> bool:
    return bool(user.is_authenticated and user.is_staff)


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get("next") or "account")

    error = ""
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=username, password=password)
        if user is None:
            error = "invalid"
        elif not user.is_active:
            error = "inactive"
        else:
            login(request, user)
            ensure_profile_for_user(user)
            next_url = request.POST.get("next") or request.GET.get("next") or ""
            if next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            return redirect("account")

    return render(
        request,
        "portal/login.html",
        {
            "error": error,
            "next": request.GET.get("next") or request.POST.get("next") or "",
            "username_prefill": request.POST.get("username") or "",
        },
    )


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")


@require_http_methods(["GET", "POST"])
def register_view(request):
    """Self-service sign-up — replaces staff-only account creation."""
    if request.user.is_authenticated:
        return redirect("account")

    error = ""
    if request.method == "POST":
        from .ratelimit import client_ip, hit

        # account farming guard: 5 signups per hour per network
        if not hit(f"register:{client_ip(request)}", 5, 3600):
            return render(
                request,
                "portal/register.html",
                {"error": "rate",
                 "next": request.POST.get("next") or "",
                 "username_prefill": ""},
            )

        from django.contrib.auth.validators import UnicodeUsernameValidator
        from django.core.exceptions import ValidationError as _VE

        username = str(request.POST.get("username") or "").strip()
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""
        # the real username validator (create_user skips full_clean), so
        # "<", "/", "%" and friends can't sneak into a username
        try:
            if not username or len(username) > 150:
                raise _VE("empty")
            UnicodeUsernameValidator()(username)
        except _VE:
            error = "username"

        if not error and User.objects.filter(username__iexact=username).exists():
            error = "exists"
        if not error and password1 != password2:
            error = "mismatch"
        if not error:
            from django.contrib.auth.password_validation import validate_password
            from django.core.exceptions import ValidationError

            try:
                validate_password(password1)
            except ValidationError:
                error = "weak"

        if not error:
            user = User.objects.create_user(username=username, password=password1)
            ensure_profile_for_user(user)
            # multiple auth backends (axes first) require an explicit backend
            login(request, user,
                  backend="django.contrib.auth.backends.ModelBackend")
            next_url = request.POST.get("next") or request.GET.get("next") or ""
            if next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            return redirect("account")

    return render(
        request,
        "portal/register.html",
        {
            "error": error,
            "next": request.GET.get("next") or "",
            "username_prefill": request.POST.get("username") or "",
        },
    )


@login_required
@require_GET
def account_view(request):
    profile = ensure_profile_for_user(request.user)
    stats = learner_stats(profile)
    return render(
        request,
        "portal/account.html",
        {"profile": profile, "stats": stats},
    )


@login_required
@require_http_methods(["GET", "POST"])
def password_change_view(request):
    error = ""
    ok = False
    if request.method == "POST":
        current = request.POST.get("current_password") or ""
        new1 = request.POST.get("new_password") or ""
        new2 = request.POST.get("new_password2") or ""
        if not request.user.check_password(current):
            error = "current"
        elif len(new1) < 8:
            error = "short"
        elif new1 != new2:
            error = "mismatch"
        else:
            request.user.set_password(new1)
            request.user.save()
            update_session_auth_hash(request, request.user)
            ok = True
    return render(
        request,
        "portal/password_change.html",
        {"error": error, "ok": ok},
    )


@user_passes_test(_staff_required)
@require_http_methods(["GET", "POST"])
def manage_users(request):
    create_error = ""
    if request.method == "POST" and request.POST.get("action") == "create":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        display = (request.POST.get("display_name") or "").strip()
        is_staff = request.POST.get("is_staff") == "on"
        if not username or len(password) < 8:
            create_error = "invalid"
        elif User.objects.filter(username=username).exists():
            create_error = "exists"
        else:
            user = User.objects.create_user(username=username, password=password)
            user.is_staff = is_staff
            user.save()
            ensure_profile_for_user(user, display_name=display or username)
            messages.success(request, f"created:{username}")
            return redirect("manage_users")

    users = User.objects.order_by("username")
    return render(
        request,
        "portal/manage_users.html",
        {"users": users, "create_error": create_error},
    )


@user_passes_test(_staff_required)
@require_POST
def manage_user_action(request, user_id: int):
    target = get_object_or_404(User, pk=user_id)
    action = (request.POST.get("action") or "").strip()

    if target.pk == request.user.pk and action in {"deactivate", "remove_staff"}:
        messages.error(request, "self")
        return redirect("manage_users")

    if action == "activate":
        target.is_active = True
        target.save(update_fields=["is_active"])
    elif action == "deactivate":
        target.is_active = False
        target.save(update_fields=["is_active"])
    elif action == "make_staff":
        target.is_staff = True
        target.save(update_fields=["is_staff"])
    elif action == "remove_staff":
        target.is_staff = False
        target.is_superuser = False
        target.save(update_fields=["is_staff", "is_superuser"])
    elif action == "reset_password":
        new_password = request.POST.get("new_password") or ""
        if len(new_password) < 8:
            messages.error(request, "short")
        else:
            target.set_password(new_password)
            target.save()
            messages.success(request, f"reset:{target.username}")
    return redirect("manage_users")
