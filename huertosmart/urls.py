from django.urls import path
from . import views

app_name = 'huertosmart'

urlpatterns = [
    path('', views.home, name='home'),

    # Biblioteca de cultivos (F3)
    path('cultivos/', views.lista_cultivos, name='lista_cultivos'),
    path('cultivos/<slug:cultivo_slug>/', views.detalle_cultivo, name='detalle_cultivo'),

    # Diagnóstico por foto (F1)
    path('diagnostico/', views.diagnostico_nuevo, name='diagnostico_nuevo'),
    path('diagnostico/historial/', views.diagnostico_historial, name='diagnostico_historial'),
    path('diagnostico/<int:diagnostico_id>/', views.diagnostico_detalle, name='diagnostico_detalle'),

    # Mi huerto (F4)
    path('mi-huerto/', views.mi_huerto, name='mi_huerto'),
    path('mi-huerto/crear/', views.crear_huerto, name='crear_huerto'),
    path('mi-huerto/<slug:huerto_slug>/', views.detalle_huerto, name='detalle_huerto'),
    path('mi-huerto/<slug:huerto_slug>/siembra/nueva/', views.nueva_siembra, name='nueva_siembra'),
    path('mi-huerto/<slug:huerto_slug>/eliminar/', views.eliminar_huerto, name='eliminar_huerto'),

    # Exportar
    path('exportar/excel/', views.exportar_excel, name='exportar_excel'),
]
