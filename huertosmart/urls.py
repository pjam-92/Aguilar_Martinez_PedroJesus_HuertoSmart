# urls.py — Mapa de URLs de la aplicación HuertoSmart
"""
Este archivo define las URLs de la aplicación: qué dirección web corresponde
a qué vista (función de views.py).

Cuando el usuario escribe una URL en el navegador, Django recorre este archivo
de arriba a abajo buscando un patrón que coincida. Cuando lo encuentra,
ejecuta la vista correspondiente y devuelve el resultado.

Este archivo solo gestiona las URLs de la app 'huertosmart'. Las URLs globales
del proyecto (incluidas las de allauth para login/logout) se definen en
miproyectodjango/urls.py.
"""

from django.urls import path
from . import views

# app_name define el espacio de nombres de esta app
# Permite referenciar las URLs como 'huertosmart:home', 'huertosmart:lista_cultivos', etc.
app_name = 'huertosmart'

urlpatterns = [

    # Página de inicio — pública
    path('', views.home, name='home'),

    # F3 — Biblioteca de cultivos — pública
    path('cultivos/', views.lista_cultivos, name='lista_cultivos'),
    path('cultivos/<slug:cultivo_slug>/', views.detalle_cultivo, name='detalle_cultivo'),

    # F1 — Diagnóstico por foto — requiere login
    path('diagnostico/', views.diagnostico_nuevo, name='diagnostico_nuevo'),
    path('diagnostico/historial/', views.diagnostico_historial, name='diagnostico_historial'),
    path('diagnostico/<int:diagnostico_id>/', views.diagnostico_detalle, name='diagnostico_detalle'),

    # F4 — Mi huerto — requiere login
    path('mi-huerto/', views.mi_huerto, name='mi_huerto'),
    path('mi-huerto/crear/', views.crear_huerto, name='crear_huerto'),
    path('mi-huerto/<slug:huerto_slug>/', views.detalle_huerto, name='detalle_huerto'),
    path('mi-huerto/<slug:huerto_slug>/siembra/nueva/', views.nueva_siembra, name='nueva_siembra'),
    path('mi-huerto/<slug:huerto_slug>/eliminar/', views.eliminar_huerto, name='eliminar_huerto'),

    # Exportación de datos a Excel — requiere login
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
]
