# settings.py — Configuración global del proyecto HuertoSmart
"""
Este archivo es el centro de configuración de todo el proyecto Django.
Aquí se define todo lo que Django necesita saber para funcionar:
qué apps están instaladas, qué base de datos usar, dónde están los
templates y archivos estáticos, cómo funciona la autenticación, etc.

Es uno de los archivos más importantes del proyecto. Si algo falla
al arrancar, casi siempre hay que mirar aquí primero.

IMPORTANTE: Este archivo contiene configuración sensible (SECRET_KEY,
credenciales de Google y AWS). Por eso las variables secretas se leen
del archivo .env mediante python-dotenv, y el .env nunca se sube a GitHub.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# Cargamos las variables del archivo .env al arrancar Django
load_dotenv()


# BASE_DIR es la ruta absoluta a la carpeta raíz del proyecto (donde está manage.py)
# Se usa como referencia para construir todas las demás rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent



# SEGURIDAD

# La SECRET_KEY se usa para firmar cookies, tokens CSRF y otros datos sensibles
# Nunca debe escribirse directamente aquí — se lee del .env
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-development-key-change-me')


# DEBUG=True muestra errores detallados en el navegador — útil en desarrollo
# En producción siempre debe ser False
DEBUG = True

ALLOWED_HOSTS = []



# APLICACIONES INSTALADAS
# Django y sus librerías de terceros necesitan estar listadas aquí para funcionar

INSTALLED_APPS = [
    # Apps propias de Django — núcleo del framework
    'django.contrib.admin',          # Panel de administración
    'django.contrib.auth',           # Sistema de usuarios y autenticación
    'django.contrib.contenttypes',   # Sistema de tipos de contenido
    'django.contrib.sessions',       # Gestión de sesiones de usuario
    'django.contrib.messages',       # Sistema de mensajes flash
    'django.contrib.staticfiles',    # Gestión de archivos estáticos
    'django.contrib.sites',          # Necesario para allauth (gestión de sites)

    # Apps de terceros — django-allauth para autenticación con Google
    'allauth',
    'allauth.account',                           # Autenticación por email/contraseña
    'allauth.socialaccount',                     # Autenticación social (OAuth2)
    'allauth.socialaccount.providers.google',    # Proveedor específico de Google

    # Nuestra app
    'huertosmart',
]



# MIDDLEWARE
# Capas de procesamiento que se aplican a cada petición/respuesta

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',   # Requerido por allauth
]


# Archivo de configuración de URLs principal del proyecto
ROOT_URLCONF = 'miproyectodjango.urls'


# TEMPLATES — Configuración del sistema de plantillas HTML

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # DIRS indica dónde buscar templates fuera de las apps
        'DIRS': [BASE_DIR / 'templates'],
        # APP_DIRS=True permite que Django busque también en templates/ dentro de cada app
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



# AUTENTICACIÓN — Backends que Django usa para verificar credenciales

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',         # Login clásico usuario/contraseña
    'allauth.account.auth_backends.AuthenticationBackend',  # Login con Google via allauth
]

# SITE_ID es necesario para allauth — referencia al registro del sitio en la tabla Sites
# Tras migrate hay que ir a /admin/ → Sites y cambiar el dominio a 127.0.0.1:8000
SITE_ID = 1


WSGI_APPLICATION = 'miproyectodjango.wsgi.application'


# BASE DE DATOS — SQLite para desarrollo (no requiere instalación adicional)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}



# VALIDADORES DE CONTRASEÑA

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]



# INTERNACIONALIZACIÓN

LANGUAGE_CODE = 'es-es'       # Idioma español de España
TIME_ZONE = 'Europe/Madrid'   # Zona horaria de Madrid
USE_I18N = True               # Activar internacionalización
USE_TZ = True                 # Usar fechas con zona horaria


# ARCHIVOS ESTÁTICOS (CSS, JavaScript, imágenes del proyecto)

STATIC_URL = 'static/'
# Carpetas donde Django busca archivos estáticos
STATICFILES_DIRS = [BASE_DIR / 'static']
# Carpeta donde se copian todos los estáticos al ejecutar collectstatic (para producción)
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ARCHIVOS SUBIDOS POR USUARIOS (fotos de diagnóstico)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Tipo de campo automático para las claves primarias de los modelos
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# CONFIGURACIÓN DE AUTENTICACIÓN Y REDIRECCIONES

LOGIN_URL = 'account_login'                    # URL a la que redirigir si no está logueado
LOGIN_REDIRECT_URL = '/mi-huerto/'             # URL tras login exitoso
ACCOUNT_LOGOUT_REDIRECT_URL = '/'             # URL tras cerrar sesión


# CONFIGURACIÓN DE ALLAUTH (autenticación por email + OAuth2 Google)

ACCOUNT_LOGIN_METHODS = {'email'}                              # Solo login por email, no por username
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']  # Campos obligatorios en el registro
ACCOUNT_EMAIL_VERIFICATION = 'none'                            # No requiere verificar el email
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
SOCIALACCOUNT_AUTO_SIGNUP = True                               # Registro automático al entrar con Google



# CONFIGURACIÓN DEL PROVEEDOR GOOGLE OAUTH2

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',   # Acceso al nombre y foto del perfil
            'email',     # Acceso al email de la cuenta Google
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        # Las credenciales se leen del .env — nunca se escriben aquí directamente
        'APP': {
            'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_OAUTH_CLIENT_SECRET'),
            'key': '',
        },
    }
}

