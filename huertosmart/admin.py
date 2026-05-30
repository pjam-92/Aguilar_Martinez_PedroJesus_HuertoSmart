# admin.py — Panel de administración personalizado de HuertoSmart
"""
Este archivo configura el panel de administración de Django (/admin/).
Django incluye un panel de administración automático y gratuito que permite
gestionar todos los datos de la aplicación sin escribir una sola línea de HTML.

Aquí personalizamos cómo se ve y se comporta ese panel para cada modelo:
qué columnas se muestran en las listas, qué filtros hay disponibles,
cómo se agrupan los campos al editar un registro, etc.

El panel de administración es el Requisito nº 8 del curso de Django.
"""

from django.contrib import admin
from .models import Cultivo, Enfermedad, Huerto, Siembra, Diagnostico, Incidencia

# ADMINISTRACIÓN DE CULTIVOS

@admin.register(Cultivo)
class CultivoAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Cultivo."""

    # Columnas visibles en la lista de cultivos
    list_display = ('nombre', 'nombre_cientifico', 'dificultad', 'exposicion', 'riego')

    # Panel de filtros lateral en la lista
    list_filter = ('dificultad', 'exposicion', 'riego')

    # Campos en los que funciona el buscador
    search_fields = ('nombre', 'nombre_cientifico')

    ordering = ('nombre',)

    # fieldsets agrupa los campos en secciones al editar un cultivo
    fieldsets = (
        ('Información básica', {
            'fields': ('nombre', 'nombre_cientifico', 'descripcion', 'imagen')
        }),
        ('Características de cultivo', {
            'fields': ('dificultad', 'exposicion', 'riego')
        }),
        ('Calendario', {
            'fields': ('meses_siembra', 'meses_cosecha', 'dias_germinacion', 'dias_cosecha')
        }),
    )

# ADMINISTRACIÓN DE ENFERMEDADES

@admin.register(Enfermedad)
class EnfermedadAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Enfermedad."""

    list_display = ('nombre', 'gravedad', 'numero_cultivos')
    list_filter = ('gravedad',)
    search_fields = ('nombre', 'nombre_modelo')

    # filter_horizontal muestra el ManyToMany con dos columnas y flechas para seleccionar
    filter_horizontal = ('cultivos_afectados',)

    def numero_cultivos(self, obj):
        """Columna personalizada que muestra cuántos cultivos afecta esta enfermedad."""
        return obj.cultivos_afectados.count()
    numero_cultivos.short_description = 'Cultivos afectados'

# ADMINISTRACIÓN DE HUERTOS

@admin.register(Huerto)
class HuertoAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Huerto."""

    list_display = ('nombre', 'usuario', 'ubicacion', 'municipio', 'activo', 'fecha_creacion')
    list_filter = ('ubicacion', 'activo')
    search_fields = ('nombre', 'usuario__username', 'municipio')

    # date_hierarchy añade una navegación por fechas en la parte superior de la lista
    date_hierarchy = 'fecha_creacion'

# INLINE DE INCIDENCIAS
# Permite ver y editar las incidencias directamente desde el detalle de una siembra

class IncidenciaInline(admin.TabularInline):
    """Muestra las incidencias de una siembra embebidas en su página de edición."""
    model = Incidencia
    extra = 0  # No mostrar filas vacías para añadir nuevas incidencias por defecto

# ADMINISTRACIÓN DE SIEMBRAS

@admin.register(Siembra)
class SiembraAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Siembra."""

    list_display = ('cultivo', 'huerto', 'fecha_siembra', 'estado', 'cantidad')
    list_filter = ('estado', 'cultivo')
    search_fields = ('cultivo__nombre', 'huerto__nombre')
    date_hierarchy = 'fecha_siembra'

    # El inline hace que las incidencias aparezcan dentro de la página de la siembra
    inlines = [IncidenciaInline]

# ADMINISTRACIÓN DE DIAGNÓSTICOS

@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Diagnóstico."""

    list_display = ('usuario', 'enfermedad_detectada', 'confianza', 'es_planta_valida', 'fecha')
    list_filter = ('es_planta_valida', 'enfermedad_detectada')
    search_fields = ('usuario__username',)
    date_hierarchy = 'fecha'

    # Estos campos son de solo lectura — no tiene sentido modificarlos manualmente
    readonly_fields = ('fecha', 'confianza', 'es_planta_valida')

# ADMINISTRACIÓN DE INCIDENCIAS

@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Incidencia."""

    list_display = ('siembra', 'tipo', 'fecha', 'resuelto')
    list_filter = ('tipo', 'resuelto')
    date_hierarchy = 'fecha'

# PERSONALIZACIÓN DEL ENCABEZADO DEL PANEL DE ADMINISTRACIÓN
admin.site.site_header = "HuertoSmart Administración"
admin.site.site_title = "HuertoSmart"
admin.site.index_title = "Panel de gestión"

