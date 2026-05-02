from pathlib import Path

from config.env import boolean_env, csv_env, database_config, environment, integer_env, load_environment_file


BASE_DIR = Path(__file__).resolve().parent.parent

load_environment_file(BASE_DIR / ".env")

SECRET_KEY = environment("DJANGO_SECRET_KEY", "unsafe-local-development-key")
DEBUG = boolean_env("DJANGO_DEBUG", False)
ALLOWED_HOSTS = csv_env("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")
CSRF_TRUSTED_ORIGINS = csv_env("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "payments.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": database_config(BASE_DIR),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SECURE_SSL_REDIRECT = boolean_env("DJANGO_SECURE_SSL_REDIRECT", False)
SECURE_HSTS_SECONDS = integer_env("DJANGO_SECURE_HSTS_SECONDS", 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = boolean_env("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = boolean_env("DJANGO_SECURE_HSTS_PRELOAD", False)
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = boolean_env("DJANGO_SESSION_COOKIE_SECURE", False)
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = boolean_env("DJANGO_CSRF_COOKIE_SECURE", False)
X_FRAME_OPTIONS = "DENY"

CONTENT_SECURITY_POLICY = environment(
    "CONTENT_SECURITY_POLICY",
    "default-src 'self'; script-src 'self' https://js.stripe.com; style-src 'self'; img-src 'self' data:; connect-src 'self' https://*.stripe.com https://*.stripe.network; frame-src https://*.stripe.com; form-action 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'",
)

STRIPE_CURRENCY_KEYS = {
    "usd": {
        "public": environment("STRIPE_PUBLIC_KEY_USD") or environment("STRIPE_PUBLIC_KEY"),
        "secret": environment("STRIPE_SECRET_KEY_USD") or environment("STRIPE_SECRET_KEY"),
    },
    "eur": {
        "public": environment("STRIPE_PUBLIC_KEY_EUR") or environment("STRIPE_PUBLIC_KEY"),
        "secret": environment("STRIPE_SECRET_KEY_EUR") or environment("STRIPE_SECRET_KEY"),
    },
}
