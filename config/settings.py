"""Django settings for config project."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "86dc94006042cb484d3f130124e2e0dce567d371e8f8a79cd557b77ed4b114c5",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

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
    "knowledge",
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
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# User DB (default) and Knowledge DB are separate SQLite files under RUNTIME_DIR.
# Never point both aliases at the same path.
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
    # curriculum outlines, notes, practice, diseases
    "knowledge": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(
            os.environ.get("GABAY_KNOWLEDGE_DB", str(RUNTIME_DIR / "knowledge.sqlite3"))
        ),
    },
}

DATABASE_ROUTERS = ["knowledge.db_router.KnowledgeRouter"]

if str(DATABASES["default"]["NAME"]) == str(DATABASES["knowledge"]["NAME"]):
    raise RuntimeError("GABAY_USER_DB and GABAY_KNOWLEDGE_DB must be different files")

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
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
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
