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

"""¡! Explicación (@admin.register): El decorador @admin.register(Modelo) le dice
a Django que registre esa clase como la configuración del admin para ese modelo.
Es equivalente a admin.site.register(Cultivo, CultivoAdmin) pero más limpio."""


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

    """¡! Explicación (fieldsets): En lugar de mostrar todos los campos del modelo
    en una lista plana, fieldsets los organiza en secciones con título. Cada
    sección es una tupla con el nombre de la sección y un diccionario con los
    campos que contiene. Hace el formulario de edición mucho más legible."""


# ADMINISTRACIÓN DE ENFERMEDADES

@admin.register(Enfermedad)
class EnfermedadAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Enfermedad."""

    list_display = ('nombre', 'gravedad', 'numero_cultivos')
    list_filter = ('gravedad',)
    search_fields = ('nombre', 'nombre_modelo')

    # filter_horizontal muestra el ManyToMany con dos columnas y flechas para seleccionar
    filter_horizontal = ('cultivos_afectados',)

    """¡! Explicación (filter_horizontal): Por defecto, los campos ManyToMany
    en el admin se muestran como una lista de selección múltiple poco usable.
    filter_horizontal lo convierte en dos paneles con botones para mover elementos
    de un lado al otro, mucho más cómodo para gestionar las relaciones."""

    def numero_cultivos(self, obj):
        """Columna personalizada que muestra cuántos cultivos afecta esta enfermedad."""
        return obj.cultivos_afectados.count()
    numero_cultivos.short_description = 'Cultivos afectados'

    """¡! Explicación (columna personalizada): list_display puede mostrar no solo
    campos del modelo sino también métodos de la clase Admin. Aquí definimos
    numero_cultivos() que devuelve el número de cultivos afectados. short_description
    es el título que aparece en la cabecera de esa columna."""


# ADMINISTRACIÓN DE HUERTOS

@admin.register(Huerto)
class HuertoAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Huerto."""

    list_display = ('nombre', 'usuario', 'ubicacion', 'municipio', 'activo', 'fecha_creacion')
    list_filter = ('ubicacion', 'activo')
    search_fields = ('nombre', 'usuario__username', 'municipio')

    # date_hierarchy añade una navegación por fechas en la parte superior de la lista
    date_hierarchy = 'fecha_creacion'

    """¡! Explicación (search_fields con doble guión bajo): 'usuario__username'
    permite buscar por el nombre de usuario del propietario aunque username sea
    un campo del modelo User y no del modelo Huerto. Django resuelve
    automáticamente la relación ForeignKey con este tipo de lookup."""


# INLINE DE INCIDENCIAS
# Permite ver y editar las incidencias directamente desde el detalle de una siembra

class IncidenciaInline(admin.TabularInline):
    """Muestra las incidencias de una siembra embebidas en su página de edición."""
    model = Incidencia
    extra = 0  # No mostrar filas vacías para añadir nuevas incidencias por defecto

    """¡! Explicación (TabularInline): Un Inline permite editar objetos relacionados
    directamente desde la página del objeto padre. TabularInline los muestra en
    formato tabla (una fila por incidencia). extra=0 significa que no aparecen
    filas vacías adicionales para añadir registros nuevos."""


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

    """¡! Explicación (readonly_fields): Marca campos como no editables en el admin.
    La fecha, la confianza y si es planta válida los genera el sistema automáticamente
    durante el diagnóstico. No tiene sentido que un administrador los modifique a mano."""


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

"""¡! Explicación (personalización del header): Estas tres líneas cambian los
textos que aparecen en el panel de administración:
- site_header: el título grande en la parte superior de todas las páginas del admin.
- site_title: el texto que aparece en la pestaña del navegador.
- index_title: el subtítulo en la página principal del admin."""
