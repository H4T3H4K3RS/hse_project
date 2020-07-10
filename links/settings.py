"""
Django settings for links project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2i$oqu0zz2j4ih5*rb#4$du=ks0safg^!a$*(f7z_^%arfj$%m'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', True)

ALLOWED_HOSTS = ["0.0.0.0", "localhost", "127.0.0.1", "links.cleverapps.io", "10.2.152.143", "hselyc.herokuapp.com",
                 "192.168.1.72"]
HOST = os.getenv('HOST', "http://127.0.0.1:8000")
BOT_HOST = os.getenv('BOT_HOST', "https://hselycbot.herokuapp.com")
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'snowpenguin.django.recaptcha2',
    'account.apps.AccountConfig',
    'api.apps.ApiConfig',
    'app.apps.AppConfig',
    'js_urls',
    'django_extensions',
    'widget_tweaks'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "disable_cache_headers.middleware.DisableCacheControl",
]

ROOT_URLCONF = 'links.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'links.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
LOGIN_URL = '/account/login/'
DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'dea1sfd7vdq6ci',
        'USER': 'dvtimbsbwrgxgz',
        'PASSWORD': '2491e909cf55fb6e184f45a9045739bc294a5a66847fe7743e7f23be1a4712d7',
        'HOST': 'ec2-54-247-79-178.eu-west-1.compute.amazonaws.com',
        'PORT': '5432',
        'OPTIONS': {'sslmode': 'require'},
    }

}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
        'NAME': 'account.validators.NumberValidator',
    },
    {
        'NAME': 'account.validators.UppercaseValidator',
    },
    {
        'NAME': 'account.validators.LowercaseValidator',
    },
    {
        'NAME': 'account.validators.SymbolValidator',
    }
]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'linkitservice@yandex.ru'
EMAIL_HOST_PASSWORD = 'OntolService2020'
DEFAULT_FROM_EMAIL = 'linkitservice@yandex.ru'
EMAIL_USE_TLS = True

AUTHENTICATION_BACKENDS = (
    'account.utils.PasswordlessAuthBackend',
)

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'templates/static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
JS_URLS = (
    'api:search_view',
    'api:index_view',
    'api:account_links',
    'api:account_links_username',
    'api:account_folder',
    'api:account_folder_username',
    'api:account_saved',
    'api:account_saved_username',
    'api:folder_view',
    'api:account_key',
    "api:account_avatar",
    'api:account_rating',
    'link_delete',
    'link_vote',
    'favourite_delete',
    'favourite_save_alt',
    'favourite_save',
    'folder_delete',
    'account:login',
    "account:delete",
    "api:account_new_api_key",
)

RECAPTCHA_PRIVATE_KEY = '6Lf3xa8ZAAAAAPVLUClGyFUd2ONvb0d2TF7anwfs'
RECAPTCHA_PUBLIC_KEY = '6Lf3xa8ZAAAAAMfsWeb0mzmnJQGYN60gn-Rxnh06'
RECAPTCHA_DEFAULT_ACTION = 'generic'
RECAPTCHA_SCORE_THRESHOLD = 0.5
BOT_KEY = "1169232934:AAHFXUE6Fq02RUn0gi7hHrY0KDRm9kx8KDI"
SECURE_SSL_REDIRECT = os.getenv('SSL', False)
if SECURE_SSL_REDIRECT:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
