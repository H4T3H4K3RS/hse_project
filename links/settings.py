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

ALLOWED_HOSTS = ["0.0.0.0", "localhost", "127.0.0.1", "links.cleverapps.io", "10.2.152.143", "hselyc.herokuapp.com"]
HOST = os.getenv('HOST', "https://hselyc.herokuapp.com")
BOT_HOST = os.getenv('BOT_HOST', "https://hselycbot.herokuapp.com")
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app.apps.AppConfig',
    'js_urls',
    'django_extensions'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

        'NAME': 'd4gvudgraqb03q',

        'USER': 'cgxxklumgdrzpi',

        'PASSWORD': '3e7e110cba255391cf5a01eed7bf13788de4526664e8aa0365a0262a694badaa',

        'HOST': 'ec2-54-247-79-178.eu-west-1.compute.amazonaws.com',

        'PORT': '5432',



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
        'NAME': 'app.validators.NumberValidator',
    },
    {
        'NAME': 'app.validators.UppercaseValidator',
    },
    {
        'NAME': 'app.validators.LowercaseValidator',
    },
    {
        'NAME': 'app.validators.SymbolValidator',
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
    'app.utils.PasswordlessAuthBackend',
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
    'api_search_view',
    'api_index_view',
    'api_account_view',
    'api_account_view_username',
    'api_folder_view',
    'link_delete',
    'link_vote',
    'favourite_delete',
    'favourite_save_alt',
    'favourite_save',
    'folder_delete',
    'account_login',
    'api_account_key'
)

RECAPTCHA_PRIVATE_KEY = '6Lfb0KIZAAAAADLS85en7FJNXjBATL0jgMtxVKcv'
RECAPTCHA_PUBLIC_KEY = '6Lfb0KIZAAAAAIqf2J9UsWj4jzsxLkiQ5sFTrPeG'
RECAPTCHA_DEFAULT_ACTION = 'generic'
RECAPTCHA_SCORE_THRESHOLD = 0.5