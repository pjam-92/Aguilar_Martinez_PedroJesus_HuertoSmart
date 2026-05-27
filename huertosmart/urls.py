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

"""¡! Explicación (from . import views): El punto (.) hace referencia al paquete
actual, es decir, la carpeta huertosmart/. Esta importación relativa es la forma
estándar de importar vistas dentro de la misma app en Django."""

# app_name define el espacio de nombres de esta app
# Permite referenciar las URLs como 'huertosmart:home', 'huertosmart:lista_cultivos', etc.
app_name = 'huertosmart'

"""¡! Explicación (app_name y namespaces): Al definir app_name, todas las URLs
de esta lista quedan agrupadas bajo el espacio de nombres 'huertosmart'. Esto
permite usar nombres como 'huertosmart:lista_cultivos' en lugar de solo
'lista_cultivos', evitando conflictos si hubiera otra app con URLs del mismo nombre.
En los templates se usa con {% url 'huertosmart:lista_cultivos' %}."""

"""¡! Explicación (parámetros dinámicos en URLs): Las partes entre < > en las
URLs son parámetros dinámicos que Django captura y pasa a la vista:
- <slug:cultivo_slug>: solo acepta letras, números y guiones. Ej: /cultivos/tomate/
- <int:diagnostico_id>: solo acepta números enteros. Ej: /diagnostico/5/
- <slug:huerto_slug>: igual que el primero. Ej: /mi-huerto/mi-primer-huerto-1/
Django valida automáticamente el tipo antes de llamar a la vista."""

"""¡! Explicación (name en cada path): El parámetro name asigna un nombre a cada
URL. Esto permite referenciarla desde el código o los templates sin escribir la
URL completa. Por ejemplo, redirect('huertosmart:lista_cultivos') o
{% url 'huertosmart:detalle_huerto' huerto_slug=huerto.slug %}. Si la URL cambia,
solo hay que actualizarla aquí y el resto del código sigue funcionando."""

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
