from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    CORS_ALLOW_CREDENTIALS=(bool, True),
    TELEGRAM_REQUEST_TIMEOUT=(int, 10),
    JWT_ACCESS_MINUTES=(int, 60),
    JWT_REFRESH_DAYS=(int, 7),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env.str(
    "SECRET_KEY",
    default="unsafe-development-key-change-it-through-an-environment-variable",
)
DEBUG = env.bool("DEBUG")
ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "testserver"]
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "users",
    "habits",
    "telegram_bot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        )
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = env.str("TIME_ZONE", default="Europe/Helsinki")
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "users.User"

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = env.bool("CORS_ALLOW_CREDENTIALS")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "habits.pagination.HabitPagination",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_MINUTES")),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_DAYS")),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Habit Tracker API",
    "DESCRIPTION": (
        "API для управления полезными и приятными привычками, "
        "включая напоминания в Telegram."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}


CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default="filesystem://")
CELERY_RESULT_BACKEND = env.str(
    "CELERY_RESULT_BACKEND",
    default="cache+memory://",
)
CELERY_FILESYSTEM_BROKER_DIR = BASE_DIR / ".celery" / "broker"
CELERY_FILESYSTEM_PROCESSED_DIR = BASE_DIR / ".celery" / "processed"
CELERY_FILESYSTEM_CONTROL_DIR = BASE_DIR / ".celery" / "control"

for celery_directory in (
    CELERY_FILESYSTEM_BROKER_DIR,
    CELERY_FILESYSTEM_PROCESSED_DIR,
    CELERY_FILESYSTEM_CONTROL_DIR,
):
    celery_directory.mkdir(parents=True, exist_ok=True)

CELERY_BROKER_TRANSPORT_OPTIONS = {
    "data_folder_in": str(CELERY_FILESYSTEM_BROKER_DIR),
    "data_folder_out": str(CELERY_FILESYSTEM_BROKER_DIR),
    "processed_folder": str(CELERY_FILESYSTEM_PROCESSED_DIR),
    "control_folder": str(CELERY_FILESYSTEM_CONTROL_DIR),
    "store_processed": False,
}
CELERY_TASK_IGNORE_RESULT = True
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_BEAT_SCHEDULE = {
    "send-habit-reminders-every-minute": {
        "task": "habits.tasks.send_habit_reminders",
        "schedule": 60.0,
    },
}

TELEGRAM_BOT_TOKEN = env.str("TELEGRAM_BOT_TOKEN", default="")
TELEGRAM_API_URL = env.str("TELEGRAM_API_URL", default="https://api.telegram.org")
TELEGRAM_REQUEST_TIMEOUT = env.int("TELEGRAM_REQUEST_TIMEOUT")
