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

