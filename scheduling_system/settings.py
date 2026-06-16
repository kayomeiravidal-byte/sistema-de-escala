from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-557j9gb6&kyvykib^o=hut&1ltrr$6s+u8pu8a)(i_2@f3ezk9",
)

# Em ambientes serverless da Vercel (env VERCEL=1) o padrão é produção (False).
_debug_default = "False" if os.environ.get("VERCEL") else "True"
DEBUG = os.environ.get("DEBUG", _debug_default).lower() in ("true", "1", "yes")

_allowed = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
ALLOWED_HOSTS = [h.strip() for h in _allowed] + [".app.github.dev", ".vercel.app"]

# Vercel injeta o domínio do deploy em VERCEL_URL (sem o protocolo)
_vercel_host = os.environ.get("VERCEL_URL")
if _vercel_host:
    ALLOWED_HOSTS.append(_vercel_host)
# Domínio público estável do projeto (VERCEL_PROJECT_PRODUCTION_URL)
_vercel_prod = os.environ.get("VERCEL_PROJECT_PRODUCTION_URL")
if _vercel_prod:
    ALLOWED_HOSTS.append(_vercel_prod)

_csrf = os.environ.get(
    "CSRF_TRUSTED_ORIGINS",
    "https://*.app.github.dev,http://localhost:8000,https://localhost:8000,http://127.0.0.1:8000",
).split(",")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf]
CSRF_TRUSTED_ORIGINS += ["https://*.vercel.app"]
if _vercel_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_vercel_host}")
if _vercel_prod:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_vercel_prod}")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "django_filters",
    "shifts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "scheduling_system.urls"

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

WSGI_APPLICATION = "scheduling_system.wsgi.application"

# Database — SQLite padrão, PostgreSQL via DATABASE_URL em produção
_db_url = os.environ.get("DATABASE_URL", "")
if _db_url.startswith("postgres"):
    try:
        import dj_database_url
        DATABASES = {"default": dj_database_url.parse(_db_url, conn_max_age=600)}
    except ImportError:
        raise RuntimeError("dj-database-url is required when DATABASE_URL is set to a postgres URI")
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = os.environ.get("TIME_ZONE", "America/Sao_Paulo")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise: serve estáticos em produção.
# USE_FINDERS=True permite servir direto dos apps/pacotes, sem depender de
# `collectstatic` em build — essencial em ambientes serverless (Vercel).
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
WHITENOISE_USE_FINDERS = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Segurança em produção (atrás do proxy HTTPS do Render/Railway)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "True").lower() in ("true", "1", "yes")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# CORS
_cors = os.environ.get(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors]

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "shifts": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}
