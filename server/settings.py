from pathlib import Path

from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    "SECRET_KEY", default="o540n_s!nfi3u)!y34^pa!*p#e6b(a@fpddgif=8+pald%vcli", cast=str
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost", cast=Csv())

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party
    "graphene_django",
    # own
    "server.catflap",
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
]

ROOT_URLCONF = "server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "server.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = config("LANGUAGE_CODE", default="en-us", cast=str)

TIME_ZONE = config("TIME_ZONE", default="UTC", cast=str)

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

GRAPHENE = {"SCHEMA": "server.catflap.schema.schema"}

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_ROOT.mkdir(parents=True, exist_ok=True)

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

PUSHOVER_USER_KEY = config("PUSHOVER_USER_KEY", default="", cast=str)
PUSHOVER_API_TOKEN = config("PUSHOVER_API_TOKEN", default="", cast=str)

NOTIFICATION_BASE_URL = config(
    "NOTIFICATION_BASE_URL", default="http://localhost:8000", cast=str
)

COLOR_INSIDE = config("COLOR_INSIDE", default="#c7489b", cast=str)
COLOR_OUTSIDE = config("COLOR_OUTSIDE", default="#48c774", cast=str)

PICTURE_URL_CAT = config(
    "PICTURE_URL_CAT", default="https://i.imgur.com/ABrhLTn.png", cast=str
)
PICTURE_URL_CAT_INSIDE = config(
    "PICTURE_URL_CAT_INSIDE", default="https://i.imgur.com/iQPfFax.png", cast=str
)
PICTURE_URL_CAT_OUTSIDE = config(
    "PICTURE_URL_CAT_OUTSIDE", default="https://i.imgur.com/GE0u2vj.png", cast=str
)
