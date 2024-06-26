"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 3.2.15.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
from os import environ

# from . import mysqlSettings
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-30kc0n7n10f+*%cnekqfr)m8y8pnfoh)d7($2ly!rnpxg+$lln'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '1.234.10.139', 'stockchartview.com', 'www.stockchartview.com']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'blog',  # 앱을 사용한다는 것을 django에게 알려주기
    'stocksimul',  # 앱을 사용한다는 것을 django에게 알려주기
    'django_apscheduler',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS 관련 추가
CORS_ORIGIN_WHITELIST = ['http://127.0.0.1:3000'
                         ,'http://localhost:3000']
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'backend.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"

APSCHEDULER_RUN_NOW_TIMEOUT = 25  # default is 25s

SCHEDULER_DEFAULT = True  # apps.py 참고

# DATABASES = mysqlSettings.DATABASES
# export DJANGO_DATABASE='mysql-local'과 같은 형식으로 환경변수 지정하여 기동
DATABASES = {
    'mysql-local': {
        'ENGINE': 'django.db.backends.mysql',  # 사용할 DB 종류
        'NAME': 'stock',  # DB 이름
        'USER': 'stock',  # DB 계정 이름
        'PASSWORD': 'stock',  # DB 계정 패스워드
        'HOST': 'localhost',  # IP
        'PORT': '3306'  # PORT
    },
    'mysql-docker': {
        'ENGINE': 'django.db.backends.mysql',  # 사용할 DB 종류
        'NAME': 'stock',  # DB 이름
        'USER': 'stock',  # DB 계정 이름
        'PASSWORD': 'stock',  # DB 계정 패스워드
        'HOST': '172.21.0.30',  # IP
        'PORT': '3306'  # PORT
    },
    'mysql-docker-out': {
        'ENGINE': 'django.db.backends.mysql',  # 사용할 DB 종류
        'NAME': 'stock',  # DB 이름
        'USER': 'stock',  # DB 계정 이름
        'PASSWORD': 'stock',  # DB 계정 패스워드
        'HOST': 'localhost',  # IP
        'PORT': '4306'  # PORT
    },
    'sqlite3': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

default_database = environ.get('DJANGO_DATABASE', 'mysql-local')
print('database name = ', default_database)
DATABASES['default'] = DATABASES[default_database]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
        # 로그 파일에 사용할 Formatter / asctime: 현재시간 , levelname : 로그레벨, name : 로거명, message: 출력내용
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            # 'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'INFO',  # 로그레벨
            # 'filters': ['require_debug_false'],  # DEBUG=False인 운영환경에서 사용
            # RotatingFileHandler는 파일 크기가 설정한 크기보다 커지면 파일 뒤에 인덱스를 붙여서 백업한다.
            # 이 핸들러의 장점은 로그가 무한히 증가되더라도 일정 개수의 파일로 롤링(Rolling)되기 때문에
            # 로그 파일이 너무 커져서 디스크가 꽉 차는 위험을 방지할 수 있다.
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/app.log',
            'maxBytes': 1024 * 1024 * 100,  # 100MB,
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'batch': {
            'handlers': ['console', 'mail_admins', 'file'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

# 관리자 화면을 한국어로 변경
# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'ko'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
