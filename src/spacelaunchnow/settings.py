"""
Django settings for spacelaunchnow project.

Generated by 'django-admin startproject' using Django 1.11.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from datetime import timedelta

from celery.schedules import crontab
from . import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.DJANGO_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', config.DEBUG)
DEBUG_LOGGING = os.getenv('DEBUG_LOGGING')
LOGLEVEL = "DEBUG" if DEBUG_LOGGING else "INFO"

if DEBUG:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = ['*']

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'spacelaunchnow.pagination.SLNLimitOffsetPagination',
    'DEFAULT_MODEL_SERIALIZER_CLASS': 'drf_toolbox.serializers.ModelSerializer',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_RENDERER_CLASSES': config.API_RENDERER,
    'DEFAULT_THROTTLE_CLASSES': (
        'api.throttle.RoleBasedUserRateThrottle',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    )
}

DISABLE_THROTTLE = os.getenv('DISABLE_THROTTLE', False)

if DEBUG:
    DISABLE_THROTTLE = True

DISCORD_WEBHOOK = os.getenv('WEBHOOK_URL', None)

LOGIN_REDIRECT_URL = '/'

if DEBUG:
    import logging

    l = logging.getLogger(__name__)
    l.setLevel(logging.DEBUG)
    l.addHandler(logging.StreamHandler())

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%m-%d-%Y %H:%M:%S",
        },
    },
    'handlers': {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "standard",
        },
    },
    'loggers': {
        "": {"handlers": ["console"], "level": LOGLEVEL, "propogate": True},
        'django': {
            'handlers': ['console'],
            'level': LOGLEVEL,
            'propagate': True,
        },
    },
}

CELERY_IMPORTS = ('bot.tasks', 'autoscaler.tasks', 'api.tasks')

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    'rest_framework',
    'api',
    'bot',
    'web',
    'autoscaler',
    'configurations',
    'embed_video',
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django_user_agents',
    'django_filters',
    'rest_framework.authtoken',
    'storages',
    'collectfast',
    'robots',
    'app',
    'sorl.thumbnail',
    'sorl_thumbnail_serializer',
    'mathfilters',
    'django_tables2',
    'bootstrap4',
    'django_extensions',
    'tz_detect',
    'corsheaders',
    'django_celery_beat',
    'django_celery_results',
    'cachalot',
    'drf_yasg',
    'debug_toolbar',
    'django_cleanup.apps.CleanupConfig',
    'health_check',  # required
    'health_check.db',  # stock Django health checkers
    'health_check.cache',
    'health_check.storage',
    'health_check.contrib.migrations',
    'health_check.contrib.s3boto3_storage',  # requires boto3 and S3BotoStorage backend
]

if DEBUG:
    # INSTALLED_APPS.append('debug_toolbar')
    pass

JET_THEMES = [
    {
        'theme': 'default',  # theme folder name
        'color': '#47bac1',  # color of the theme's button in user menu
        'title': 'Default'  # theme title
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tz_detect.middleware.TimezoneMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'silk.middleware.SilkyMiddleware',
]

X_FRAME_OPTIONS = 'SAMEORIGIN'

CORS_ORIGIN_ALLOW_ALL = True

SILKY_PYTHON_PROFILER = True

GEOIP_DATABASE = 'GeoLiteCity.dat'
GEOIPV6_DATABASE = 'GeoLiteCityv6.dat'

ROOT_URLCONF = 'spacelaunchnow.urls'

AWS_DEFAULT_ACL = 'public-read'

JET_MODULE_GOOGLE_ANALYTICS_CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, 'client_secrets.json')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR + '/templates/'],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'spacelaunchnow.context_processor.ga_tracking_id',
                'spacelaunchnow.context_processor.use_google_analytics',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

ZINNIA_ENTRY_CONTENT_TEMPLATES = [
    ('zinnia/_short_entry_detail.html', 'Short entry template'),
]

ZINNIA_ENTRY_DETAIL_TEMPLATES = [
    ('zinnia/fullwidth_entry_detail.html', 'Fullwidth template'),
]

USE_GA = not config.DEBUG

WSGI_APPLICATION = 'spacelaunchnow.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
     'default': {
         'ENGINE': os.getenv('DATABASE_ENGINE', config.DATABASE['default']['ENGINE']),
         'NAME': os.getenv('DATABASE_NAME', config.DATABASE['default']['NAME']),
         'USER': os.getenv('DATABASE_USERNAME', config.DATABASE['default'].get('USER', None)),
         'PASSWORD': os.getenv('DATABASE_PASSWORD', config.DATABASE['default'].get('PASSWORD', None)),
         'HOST': os.getenv('DATABASE_HOST', config.DATABASE['default'].get('HOST', None)),
         'PORT': os.getenv('DATABASE_PORT', config.DATABASE['default'].get('PORT', None)),
     }
 }

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

ZINNIA_MARKUP_LANGUAGE = 'markdown'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

INTERNAL_IPS = [
    '127.0.0.1',
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DISCORD_WEBHOOK = os.getenv('WEBHOOK_URL', None)

GA_TRACKING_ID = config.GOOGLE_ANALYTICS_TRACKING_ID

# CELERY STUFF
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'amqp://slns-rabbitmq:5672')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Name of cache backend to cache user agents. If it not specified default
# cache alias will be used. Set to `None` to disable caching.
USER_AGENTS_CACHE = None

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config.EMAIL_HOST
EMAIL_PORT = config.EMAIL_PORT
EMAIL_HOST_USER = config.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = config.EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = config.EMAIL_HOST_TLS
DEFAULT_FROM_EMAIL = config.EMAIL_FROM_EMAIL

# AWS Storage Information

AWS_STORAGE_BUCKET_NAME = config.STORAGE_BUCKET_NAME

# Not using CloudFront?
# S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
# Using CloudFront?
# S3_CUSTOM_DOMAIN = CLOUDFRONT_DOMAIN
AWS_S3_CUSTOM_DOMAIN = config.S3_CUSTOM_DOMAIN

# Static URL always ends in /
STATIC_URL = config.S3_CUSTOM_DOMAIN + "/"

# If not using CloudFront, leave None in config.
CLOUDFRONT_DOMAIN = config.CLOUDFRONT_DOMAIN
CLOUDFRONT_ID = config.CLOUDFRONT_ID

AWS_ACCESS_KEY_ID = config.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
AWS_S3_URL_PROTOCOL = 'https'
AWS_LOCATION = 'static'
AWS_S3_ENDPOINT_URL = config.AWS_S3_ENDPOINT_URL
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',

}

STATIC_URL_AWS = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)

MEDIA_LOCATION = 'media'
PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))
STATICFILES_DIRS = [os.path.join(PROJECT_PATH, 'static')]
STATICFILES_LOCATION = 'static/home'
STATICFILES_STORAGE = 'custom_storages.StaticStorage'
AWS_PRELOAD_METADATA = True

LOGO_LOCATION = MEDIA_LOCATION + '/logo'  # type: str
LOGO_STORAGE = 'custom_storages.LogoStorage'

DEFAULT_LOCATION = MEDIA_LOCATION + '/default'  # type: str
DEFAULT_STORAGE = 'custom_storages.DefaultStorage'

AGENCY_IMAGE_LOCATION = MEDIA_LOCATION + '/agency_images'  # type: str
AGENCY_IMAGE_STORAGE = 'custom_storages.AgencyImageStorage'

AGENCY_NATION_LOCATION = MEDIA_LOCATION + '/agency_nation'  # type: str
AGENCY_NATION_STORAGE = 'custom_storages.AgencyNationStorage'

ORBITER_IMAGE_LOCATION = MEDIA_LOCATION + '/orbiter_images'  # type: str
ORBITER_IMAGE_STORAGE = 'custom_storages.OrbiterImageStorage'

LAUNCHER_IMAGE_LOCATION = MEDIA_LOCATION + '/launcher_images'  # type: str
LAUNCHER_IMAGE_STORAGE = 'custom_storages.LauncherImageStorage'

LAUNCH_IMAGE_LOCATION = MEDIA_LOCATION + '/launch_images'  # type: str
LAUNCH_IMAGE_STORAGE = 'custom_storages.LaunchImageStorage'

EVENT_IMAGE_LOCATION = MEDIA_LOCATION + '/event_images'  # type: str
EVENT_IMAGE_STORAGE = 'custom_storages.EventImageStorage'

PROGRAM_IMAGE_LOCATION = MEDIA_LOCATION + '/program_images'  # type: str
PROGRAM_IMAGE_STORAGE = 'custom_storages.ProgramImageStorage'

APP_IMAGE_LOCATION = MEDIA_LOCATION + '/app_images'  # type: str
APP_IMAGE_STORAGE = 'custom_storages.AppImageStorage'

ASTRONAUT_IMAGE_LOCATION = MEDIA_LOCATION + '/astronaut_images'  # type: str
ASTRONAUT_IMAGE_STORAGE = 'custom_storages.AstronautImageStorage'

SPACESTATION_IMAGE_LOCATION = MEDIA_LOCATION + '/spacestation_images'  # type: str
SPACESTATION_IMAGE_STORAGE = 'custom_storages.SpaceStationImageStorage'

LAUNCHER_CORE_IMAGE_LOCATION = MEDIA_LOCATION + '/launcher_core_images'  # type: str
LAUNCHER_CORE_IMAGE_STORAGE = 'custom_storages.LauncherCoreImageStorage'

DEFAULT_FILE_STORAGE = DEFAULT_STORAGE

AWS_IS_GZIPPED = True

if os.getenv('CACHE_BACKEND') and os.getenv('CACHE_LOCATION'):
    CACHES = {
        'default': {
            'BACKEND': os.getenv('CACHE_BACKEND'),
            'LOCATION': os.getenv('CACHE_LOCATION'),
        }
    }
else:
    CACHES = config.CACHE

CACHALOT_TIMEOUT = 60


IS_API = os.getenv('IS_API', config.IS_API)
IS_WEBSERVER = os.getenv('IS_WEBSERVER', config.IS_WEBSERVER)
IS_BOTSERVER = os.getenv('IS_BOTSERVER', config.IS_BOTSERVER)
IS_ADMIN = os.getenv('IS_ADMIN', config.IS_ADMIN)
IS_SLN = os.getenv('IS_SLN', True)
IS_LL = os.getenv('IS_LL', False)

GOOGLE_API_KEY = config.GOOGLE_API_KEY

if 'test' in sys.argv:
    TESTING = True
else:
    TESTING = False