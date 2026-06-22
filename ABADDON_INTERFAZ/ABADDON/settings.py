"""
Configuración principal del proyecto ABADDON.
Versión preparada para trabajar en local, en host y con Cloudinary para imágenes de productos.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary

BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables del archivo .env en local
load_dotenv(BASE_DIR / '.env')


def env_bool(nombre, valor_default=False):
    valor = os.getenv(nombre)

    if valor is None:
        return valor_default

    return valor.lower() in ['true', '1', 'yes', 'si']


def env_list(nombre, valor_default=''):
    valor = os.getenv(nombre, valor_default)
    return [item.strip() for item in valor.split(',') if item.strip()]


# =========================
# CONFIGURACIÓN GENERAL
# =========================

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-b*0&@yyuz61bb^09-g71p5vqd1-#^b-02_+rwged0rv5#fy_1i'
)

DEBUG = env_bool('DEBUG', True)

ALLOWED_HOSTS = env_list(
    'ALLOWED_HOSTS',
    '127.0.0.1,localhost'
)


# =========================
# APLICACIONES
# =========================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Librerías externas
    'cloudinary',
    'crispy_forms',
    'crispy_bootstrap4',

    # Apps del proyecto
    'General',
    'Productos',
    'Usuarios',
    'Ventas',
    'Autenticar',
    'Auditoria',
    'Reportes',
]


# =========================
# MIDDLEWARE
# =========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # Permite servir archivos estáticos en host
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'ABADDON.urls'


# =========================
# TEMPLATES
# =========================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'General' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'ABADDON.wsgi.application'


# =========================
# BASE DE DATOS
# =========================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =========================
# VALIDACIÓN DE CONTRASEÑAS
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =========================
# IDIOMA Y ZONA HORARIA
# =========================

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True


# =========================
# ARCHIVOS ESTÁTICOS
# =========================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# =========================
# ARCHIVOS MEDIA LOCALES
# =========================
# Se conserva por compatibilidad con archivos locales.
# Las imágenes de productos pasarán a Cloudinary desde Productos/models.py.

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'ABADDON' / 'media'


# =========================
# CLOUDINARY
# =========================

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)


# =========================
# CRISPY FORMS
# =========================

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"


# =========================
# CONFIGURACIÓN DE CORREO
# =========================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)


# =========================
# USUARIO PERSONALIZADO Y LOGIN
# =========================

AUTH_USER_MODEL = 'Usuarios.Usuario'

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'


# =========================
# DEFAULT FIELD
# =========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'