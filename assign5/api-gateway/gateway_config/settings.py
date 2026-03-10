import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'api-gateway-secret-key')
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'gateway',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'gateway_config.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [],
               'APP_DIRS': True, 'OPTIONS': {'context_processors': [
                   'django.template.context_processors.request',
                   'django.contrib.auth.context_processors.auth',
                   'django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'gateway_config.wsgi.application'

# Không cần DB cho gateway, nhưng Django yêu cầu khai báo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'gateway.sqlite3',
    }
}

# Service URLs
STAFF_SERVICE_URL = os.environ.get('STAFF_SERVICE_URL', 'http://staff-service:8001')
MANAGER_SERVICE_URL = os.environ.get('MANAGER_SERVICE_URL', 'http://manager-service:8002')
CUSTOMER_SERVICE_URL = os.environ.get('CUSTOMER_SERVICE_URL', 'http://customer-service:8003')
CATALOG_SERVICE_URL = os.environ.get('CATALOG_SERVICE_URL', 'http://catalog-service:8004')
BOOK_SERVICE_URL = os.environ.get('BOOK_SERVICE_URL', 'http://book-service:8005')
CART_SERVICE_URL = os.environ.get('CART_SERVICE_URL', 'http://cart-service:8006')
ORDER_SERVICE_URL = os.environ.get('ORDER_SERVICE_URL', 'http://order-service:8007')
SHIP_SERVICE_URL = os.environ.get('SHIP_SERVICE_URL', 'http://ship-service:8008')
PAY_SERVICE_URL = os.environ.get('PAY_SERVICE_URL', 'http://pay-service:8009')
COMMENT_SERVICE_URL = os.environ.get('COMMENT_SERVICE_URL', 'http://comment-rate-service:8010')
RECOMMENDER_SERVICE_URL = os.environ.get('RECOMMENDER_SERVICE_URL', 'http://recommender-ai-service:8011')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
}
CORS_ALLOW_ALL_ORIGINS = True
LANGUAGE_CODE = 'vi-vn'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
