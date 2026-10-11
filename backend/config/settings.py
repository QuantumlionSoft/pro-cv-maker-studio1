"""Django settings for Pro CV Maker Studio.

All secrets and environment-specific values come from environment variables
(or a local `.env` file at the project root). See `.env.example`.
"""
from pathlib import Path

import environ
from django.core.exceptions import ImproperlyConfigured

BACKEND_DIR = Path(__file__).resolve().parent.parent  # backend/
PROJECT_ROOT = BACKEND_DIR.parent                     # pro-cv-maker-studio/

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1", "[::1]"]),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:5173", "http://127.0.0.1:5173"]),
    CSRF_TRUSTED_ORIGINS=(list, []),
    MAX_IMAGE_UPLOAD_MB=(int, 5),
    DJANGO_SECURE_COOKIES=(bool, False),
    DJANGO_COOKIE_SAMESITE=(str, "Lax"),  # use "None" (with DJANGO_SECURE_COOKIES=true) when the app runs inside a cross-site iframe over HTTPS
)
environ.Env.read_env(PROJECT_ROOT / ".env", overwrite=False)

DEBUG = env("DJANGO_DEBUG")

_secret = env("DJANGO_SECRET_KEY", default="")
if not _secret:
    if not DEBUG:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set when DJANGO_DEBUG is false.")
    _secret = "dev-only-insecure-key-change-me"
SECRET_KEY = _secret

ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "apps.common",
    "apps.accounts",
    "apps.activity",
    "apps.resumes",
    "apps.portfolios",
    "apps.media",
    "apps.qr_codes",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
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

# Database: SQLite by default for zero-setup local development.
# Set DATABASE_URL=postgres://user:password@localhost:5432/pro_cv_maker to use PostgreSQL.
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BACKEND_DIR / 'db.sqlite3'}",
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BACKEND_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# User uploads live outside the code tree. They are NOT served by Django's static
# file handler; private files are returned only through authenticated API views.
MEDIA_URL = "/media/"
MEDIA_ROOT = PROJECT_ROOT / "media"
EXPORTS_ROOT = PROJECT_ROOT / "exports"
MAX_IMAGE_UPLOAD_BYTES = env("MAX_IMAGE_UPLOAD_MB") * 1024 * 1024

# Sessions and CSRF (SPA on the same site via the Vite dev proxy, or CORS if configured).
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = env("DJANGO_COOKIE_SAMESITE")
SESSION_COOKIE_SECURE = env("DJANGO_SECURE_COOKIES")
CSRF_COOKIE_SAMESITE = env("DJANGO_COOKIE_SAMESITE")
CSRF_COOKIE_SECURE = env("DJANGO_SECURE_COOKIES")
CSRF_COOKIE_HTTPONLY = False  # the SPA reads the token and echoes it in X-CSRFToken
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["apps.common.auth.CsrfEnforcingSessionAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "EXCEPTION_HANDLER": "apps.common.exceptions.api_exception_handler",
    "DEFAULT_THROTTLE_RATES": {"auth": "20/minute"},
}

# Email: console backend in development. Reset links are printed to the server log.
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="Pro CV Maker Studio <no-reply@localhost>")
PASSWORD_RESET_FRONTEND_URL = env("PASSWORD_RESET_FRONTEND_URL", default="http://localhost:5173/reset-password")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
