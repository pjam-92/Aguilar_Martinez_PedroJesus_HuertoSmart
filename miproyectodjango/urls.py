# urls.py — Configuración de URLs del proyecto HuertoSmart
"""
Este archivo es el enrutador principal de todo el proyecto Django.
Cuando llega una petición al servidor, Django mira este archivo primero
para decidir a qué app o vista dirigirla.

A diferencia del urls.py de la app huertosmart (que define las URLs
específicas de la app), este archivo organiza las URLs a nivel de proyecto,
delegando en cada app o librería la gestión de sus propias URLs.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

"""¡! Explicación (imports):
- admin: el panel de administración de Django, disponible en /admin/.
- include: permite delegar un grupo de URLs a otro archivo urls.py.
- settings: para acceder a MEDIA_URL, STATIC_URL y DEBUG.
- static: función que genera las URLs para servir archivos estáticos y media."""

"""¡! Explicación (allauth.urls): Al incluir 'allauth.urls', Django registra
automáticamente todas las URLs que necesita allauth para funcionar:
/accounts/login/, /accounts/logout/, /accounts/signup/,
/accounts/google/login/, /accounts/google/login/callback/, etc.
No hay que definirlas manualmente."""

"""¡! Explicación (include con path vacío): Al usar path('', ...) la app
huertosmart gestiona las URLs desde la raíz del sitio. Así /cultivos/ llega
directamente a la vista lista_cultivos sin prefijo adicional.
Si usáramos path('huerto/', ...) todas las URLs tendrían ese prefijo."""

urlpatterns = [

    # Panel de administración de Django — Requisito nº 8 del curso
    path('admin/', admin.site.urls),

    # URLs de django-allauth: login, logout, registro, cambio de contraseña,
    # y todas las URLs de OAuth2 para Google
    path('accounts/', include('allauth.urls')),

    # URLs de la app huertosmart — incluye todas las rutas definidas en huertosmart/urls.py
    path('', include('huertosmart.urls')),
]

# En desarrollo, Django también sirve los archivos de media (fotos de diagnóstico)
# y los archivos estáticos directamente. En producción esto lo haría el servidor web.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

"""¡! Explicación (servir media en DEBUG): En producción, los archivos estáticos
y de media los sirve directamente el servidor web (Nginx, Apache) porque es
mucho más eficiente que hacerlo con Django. En desarrollo, como no tenemos
servidor web, añadimos estas URLs para que Django los sirva él mismo.
El if settings.DEBUG garantiza que esto solo ocurre en desarrollo."""
