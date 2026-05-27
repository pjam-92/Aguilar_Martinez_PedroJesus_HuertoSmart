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

"""¡! Explicación (load_dotenv): La librería python-dotenv lee el archivo .env
de la raíz del proyecto y carga todas las variables como variables de entorno
del sistema. A partir de este punto, os.getenv('SECRET_KEY') devuelve el valor
que está en el .env. Sin esta línea, todas las credenciales estarían vacías."""

# BASE_DIR es la ruta absoluta a la carpeta raíz del proyecto (donde está manage.py)
# Se usa como referencia para construir todas las demás rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

"""¡! Explicación (BASE_DIR): Path(__file__) es la ruta de este archivo settings.py.
.parent sube un nivel (a la carpeta miproyectodjango/), .parent.parent sube otro
nivel más (a la raíz del proyecto). Desde ahí construimos rutas como BASE_DIR / 'templates'
que funciona igual en Windows, Mac y Linux."""


# SEGURIDAD

# La SECRET_KEY se usa para firmar cookies, tokens CSRF y otros datos sensibles
# Nunca debe escribirse directamente aquí — se lee del .env
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-development-key-change-me')

"""¡! Explicación (SECRET_KEY): Esta clave es la base de la seguridad de Django.
Se usa para cifrar las sesiones de usuario, los tokens CSRF y otras operaciones
criptográficas. Si alguien la conoce, puede falsificar sesiones. Por eso se guarda
en el .env y nunca en el código. El valor por defecto solo vale para desarrollo."""

# DEBUG=True muestra errores detallados en el navegador — útil en desarrollo
# En producción siempre debe ser False
DEBUG = True

ALLOWED_HOSTS = []

"""¡! Explicación (ALLOWED_HOSTS): Lista de dominios desde los que se puede
acceder a la aplicación. En desarrollo está vacía porque DEBUG=True lo permite.
En producción habría que añadir el dominio real, como ['huertosmart.com']."""


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

"""¡! Explicación (INSTALLED_APPS): Django no carga automáticamente todas las
carpetas del proyecto. Cada app debe declararse aquí para que Django la reconozca,
procese sus modelos, registre sus URLs y cargue sus templates. Si una app no está
en esta lista, Django la ignora completamente."""


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

"""¡! Explicación (Middleware): El middleware es como una cadena de filtros.
Cada petición HTTP pasa por todos los middlewares de arriba a abajo antes de
llegar a la vista, y la respuesta pasa por todos de abajo a arriba antes de
llegar al navegador. Por ejemplo, CsrfViewMiddleware comprueba el token CSRF
en formularios POST para prevenir ataques, y SessionMiddleware gestiona las
sesiones de usuario."""

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

"""¡! Explicación (context_processors): Los context processors añaden variables
automáticamente a todos los templates sin que la vista tenga que pasarlas
explícitamente. Por ejemplo, auth añade la variable 'user' con el usuario actual,
y messages añade los mensajes flash. Por eso en los templates podemos usar
{{ user.username }} o {% for message in messages %} sin que la vista lo envíe."""


# AUTENTICACIÓN — Backends que Django usa para verificar credenciales

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',         # Login clásico usuario/contraseña
    'allauth.account.auth_backends.AuthenticationBackend',  # Login con Google via allauth
]

# SITE_ID es necesario para allauth — referencia al registro del sitio en la tabla Sites
# Tras migrate hay que ir a /admin/ → Sites y cambiar el dominio a 127.0.0.1:8000
SITE_ID = 1

"""¡! Explicación (SITE_ID): Django tiene un sistema de 'Sites' que permite
que una misma base de código sirva múltiples dominios. allauth lo usa para
saber desde qué dominio se están haciendo las redirecciones OAuth. Por eso
es imprescindible configurar el Site en el admin con el dominio correcto
(127.0.0.1:8000 en desarrollo) para que el login con Google funcione."""

WSGI_APPLICATION = 'miproyectodjango.wsgi.application'


# BASE DE DATOS — SQLite para desarrollo (no requiere instalación adicional)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

"""¡! Explicación (SQLite): SQLite guarda toda la base de datos en un único
archivo (db.sqlite3) en la raíz del proyecto. Es perfecta para desarrollo
porque no requiere instalar ni configurar ningún servidor de base de datos.
Para producción se usaría PostgreSQL o MySQL, cambiando solo este bloque."""


# VALIDADORES DE CONTRASEÑA

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

"""¡! Explicación (validadores de contraseña): Django comprueba automáticamente
las contraseñas nuevas contra estos validadores. MinimumLengthValidator exige
longitud mínima, CommonPasswordValidator rechaza contraseñas como '123456',
y UserAttributeSimilarityValidator evita contraseñas parecidas al nombre del usuario."""


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

"""¡! Explicación (STATIC vs MEDIA): Los archivos estáticos (STATIC) son los
que forman parte del código del proyecto: imágenes de cultivos, CSS, JS.
Los archivos de media (MEDIA) son los que suben los usuarios: las fotos de
diagnóstico. Se sirven y almacenan de forma diferente."""

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

"""¡! Explicación (ACCOUNT_EMAIL_VERIFICATION = 'none'): En un proyecto real
se enviaría un email de verificación al registrarse. Para este proyecto de curso
lo desactivamos para simplificar las pruebas. Si estuviera activado, cada vez
que un nuevo usuario se registra recibiría un email con un enlace de confirmación."""


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

"""¡! Explicación (OAuth2 con Google): Para que el login con Google funcione
hay que registrar la aplicación en Google Cloud Console y obtener un
client_id y un client_secret. Estas credenciales se guardan en el .env.
Google redirige al usuario de vuelta a la URL configurada en Cloud Console
(/accounts/google/login/callback/) tras autenticarse correctamente."""
