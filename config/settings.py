"""Django settings for config project."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

# No committed fallback: a secret in git history is a leaked secret. The key
# comes from the process env or from the .env files portal.envfile scans
# (production keeps it in /home/ubuntu/runtime/.env, outside any checkout).
from portal.envfile import env_value as _env_value  # noqa: E402  (plain module, app-free)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or _env_value("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "DJANGO_SECRET_KEY is not set — export it or add it to a .env file "
        f"scanned by portal.envfile (e.g. {BASE_DIR / '.env'})"
    )

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "localhost,127.0.0.1,*",
    ).split(",")
    if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "portal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "portal.llm.coach_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# The user DB (accounts, sessions, learner progress) lives under RUNTIME_DIR.
# Curriculum knowledge is file-based now: content/*.yml read by portal/content.py.
RUNTIME_DIR = Path(
    os.environ.get("GABAY_RUNTIME_DIR", "/home/ubuntu/runtime/django-wsgi")
)
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

DATABASES = {
    # learners / Django auth / sessions / progress
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(
            os.environ.get("GABAY_USER_DB", str(RUNTIME_DIR / "users.sqlite3"))
        ),
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "account"
LOGOUT_REDIRECT_URL = "home"

LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Behind Nginx TLS termination on :8888
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
# Secure cookies only when actually serving over TLS; DEBUG/dev runserver is
# plain HTTP, where the old always-on flags turned login into a redirect loop.
# Override with GABAY_SECURE_COOKIES=0/1 when testing prod mode locally.
_secure_cookies = os.environ.get("GABAY_SECURE_COOKIES", "").strip()
if _secure_cookies not in {"0", "1"}:
    _secure_cookies = "0" if DEBUG else "1"
SESSION_COOKIE_SECURE = _secure_cookies == "1"
CSRF_COOKIE_SECURE = _secure_cookies == "1"
SECURE_SSL_REDIRECT = False  # Nginx enforces HTTPS; avoid redirect loops

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "https://127.0.0.1:8888,https://localhost:8888,https://124.222.115.8:8888,https://10.0.0.14:8888",
    ).split(",")
    if o.strip()
]

# MiniMax study tutor keys are read from a .env file by portal.envfile.
# Override the file location with GABAY_ENV_FILE; see `manage.py env_status`.
GABAY_ENV_FILE = os.environ.get("GABAY_ENV_FILE", str(BASE_DIR / ".env"))
