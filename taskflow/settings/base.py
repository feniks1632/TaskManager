import os
from decouple import config

# Базовые пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Безопасность
SECRET_KEY = config('SECRET_KEY', default='your-default-secret-key')
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])


# Приложения
INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tasks.apps.TasksConfig',
    'django_extensions',  # Удобные команды

    # Локальные приложения
    'channels',
    'notifications',
    'analytics',
    'core',
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

ROOT_URLCONF = 'taskflow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'taskflow.wsgi.application'
ASGI_APPLICATION = 'taskflow.asgi.application'

# Redis для Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],  # если в Docker
            # "hosts": [('127.0.0.1', 6379)],  # если локально
        },
    },
}


# База данных — PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='taskflow'),
        'USER': config('DB_USER', default='taskflow'),
        'PASSWORD': config('DB_PASSWORD', default='taskflow'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Аутентификация
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Локализация
LANGUAGE_CODE = config('LANGUAGE_CODE', default='ru-ru')
TIME_ZONE = config('TIME_ZONE', default='Asia/Yekaterinburg')
USE_I18N = config('USE_I18N', default=True, cast=bool)
USE_TZ = config('USE_TZ', default=True, cast=bool)

# Статика
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Дефолтный авто-филд
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media (если будем загружать файлы)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Логирование
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console'],
            'level': 'INFO',
        },
        'notifications': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Базовые урлы
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'tasks:list'
LOGOUT_REDIRECT_URL = 'login'

# Настройки Celery
CELERY_BROKER_URL = 'amqp://taskflow:taskflow@rabbitmq:5672//'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = config('CELERY_TIMEZONE', default='')

# Периодические задачи (Celery Beat)
CELERY_BEAT_SCHEDULE = {
    'send-overdue-task-reminders': {
        'task': 'tasks.celery_tasks.check_overdue_tasks',
        'schedule': 120.0,
    },
}
