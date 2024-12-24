"""
Django settings for myproject project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from datetime import timedelta
import environ
from celery.schedules import crontab

   # Read the .env file

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-g!tdd2wh+0%$6e@!fhxb2^@nzlht-uyn4fazkji-ggm4oy3n%a"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True



# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'users', #login/register users
    'cart', # cart, checkout flows
    'reviews', #reviews app
    "rest_framework",
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'channels',
    'silk', #  Profiling and monitoring Django application performance. /pip install django-silk
    'graphene_django',

]

MIDDLEWARE = [
    'silk.middleware.SilkyMiddleware',

    'corsheaders.middleware.CorsMiddleware', #add with cors

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


GRAPHENE = {
    "SCHEMA": "myproject.schema.schema",  # Replace `myproject` with your app name
}

from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + [
    'sentry-trace',  # Allow Sentry's tracing header
    'baggage',       # Allow Sentry's baggage header
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticated',
    # ],
}


STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_WEBHOOK_SECRET= os.getenv('STRIPE_WEBHOOK_SECRET', '')
# print('Stripe ', STRIPE_WEBHOOK_SECRET)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,  # Enables blacklisting of tokens
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

ROOT_URLCONF = "myproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
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
ASGI_APPLICATION = 'myproject.asgi.application'

WSGI_APPLICATION = "myproject.wsgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],   #later set up REDIS_HOST and REDIS_PORT environment variables
        },
    },
}

# CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

#later add to the .env file
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")



# settings.py

CRONITOR_API_KEY = '39129fe81203478988ea57ba1800ab66'  #put it in .env file later
ENVIRONMENT = 'development'  # or 'staging', 'production', etc.


CELERY_BEAT_SCHEDULE = {
    # "update_database": {
    #     "task": "update_data_in_databse",
    #     "schedule": crontab(minute="*/1"),  # every hour
    # },


    "send_heart_beat": {
        "task": "heat_beat_scheduler",
        "schedule": crontab(minute=0), # at the start of every hour
    },
    "check_health": {
        "task": "check_health",
        "schedule": crontab(minute=0),  # at the start of every hour
    },
    "clean_old_orders": {
        "task": "clean_old_orders",
        "schedule": crontab(hour=0, minute=0),  # daily at midnight
    },
}



import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://d8698bd8597ae1dc677b7ecf753d4ebc@o4508514431926272.ingest.us.sentry.io/4508514438086656",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    integrations=[
        DjangoIntegration(),
    ],
    traces_sample_rate=1.0,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
    send_default_pii=True,
)




LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'celery': {
            'format': '[{levelname}] Task: {task_name} | Time: {elapsed_time:.2f}s | Status: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'celery',
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}



# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#         },
#         'channels': {
#             'handlers': ['console'],
#             'level': 'DEBUG',
#         },
#     },
# }

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }


# This ensures the backend connects to PostgreSQL when running in Docker but falls back to SQLite if environment variables are not set.
# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
#         'NAME': os.getenv('DB_NAME', BASE_DIR / 'db.sqlite3'),
#         'USER': os.getenv('DB_USER', ''),
#         'PASSWORD': os.getenv('DB_PASSWORD', ''),
#         'HOST': os.getenv('DB_HOST', 'localhost'),
#         'PORT': os.getenv('DB_PORT', ''),
#     }
# }

from decouple import config #initially looks in .env file


DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE'),
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default=''),
        'PORT': config('DB_PORT', default=''),
    }
}
print("DB_ENGINE:", config('DB_ENGINE'))
print("DB_NAME:", config('DB_NAME'))
print("DB_USER:", config('DB_USER'))
print("DB_PASSWORD:", config('DB_PASSWORD'))
print("DB_HOST:", config('DB_HOST'))
print("DB_PORT:", config('DB_PORT'))


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'
LOGIN_URL = 'users:login' #if i am not logged in and try to go to the @login_required page, i will be redirected to the users:login page

#the field below is for email registration
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",#this built in backend authenticate by username and password
    'users.authentication.EmailAuthBackend',# our own created backend that authorises by email
]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend" #this line is for sending emails (signals, password resets, etc...)

#NEED TO SET UP LATER
#the lines below is for password reset by email, it finally works perfectly and sends email on my mail
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'artem.lems@yandex.ru'
EMAIL_HOST_PASSWORD = 'fsjmlstvaabhrbhp'
EMAIL_USE_SSL = True

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER #this line is important for sending messages such as password reset(doesnt work without it)
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_ADMIN = EMAIL_HOST_USER

AUTH_USER_MODEL = "users.User" #bcz we customized the base User model


MEDIA_ROOT = BASE_DIR / 'media' #creates one directory for all the media files , instead of two directories 'uploads'-forms upload and 'upload_models'-model upload, we have 'media' for any files and ways of upload
MEDIA_URL = '/media/'#to display pictures



DEFAULT_USER_IMAGE = MEDIA_URL + 'users/default.png' # we defined default url link for our photo profile ( also changes in profile.html and ProfileUser)