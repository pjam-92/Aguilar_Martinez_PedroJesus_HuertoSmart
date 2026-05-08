from django.contrib import admin
from .models import Cultivo, Enfermedad, Huerto, Siembra, Diagnostico, Incidencia


@admin.register(Cultivo)
class CultivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nombre_cientifico', 'dificultad', 'exposicion', 'riego')
    list_filter = ('dificultad', 'exposicion', 'riego')
    search_fields = ('nombre', 'nombre_cientifico')
    ordering = ('nombre',)
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


@admin.register(Enfermedad)
class EnfermedadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'gravedad', 'numero_cultivos')
    list_filter = ('gravedad',)
    search_fields = ('nombre', 'nombre_modelo')
    filter_horizontal = ('cultivos_afectados',)

    def numero_cultivos(self, obj):
        return obj.cultivos_afectados.count()
    numero_cultivos.short_description = 'Cultivos afectados'


@admin.register(Huerto)
class HuertoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'ubicacion', 'municipio', 'activo', 'fecha_creacion')
    list_filter = ('ubicacion', 'activo')
    search_fields = ('nombre', 'usuario__username', 'municipio')
    date_hierarchy = 'fecha_creacion'


class IncidenciaInline(admin.TabularInline):
    model = Incidencia
    extra = 0


@admin.register(Siembra)
class SiembraAdmin(admin.ModelAdmin):
    list_display = ('cultivo', 'huerto', 'fecha_siembra', 'estado', 'cantidad')
    list_filter = ('estado', 'cultivo')
    search_fields = ('cultivo__nombre', 'huerto__nombre')
    date_hierarchy = 'fecha_siembra'
    inlines = [IncidenciaInline]


@admin.register(Diagnostico)
class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'enfermedad_detectada', 'confianza', 'es_planta_valida', 'fecha')
    list_filter = ('es_planta_valida', 'enfermedad_detectada')
    search_fields = ('usuario__username',)
    date_hierarchy = 'fecha'
    readonly_fields = ('fecha', 'confianza', 'es_planta_valida')


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ('siembra', 'tipo', 'fecha', 'resuelto')
    list_filter = ('tipo', 'resuelto')
    date_hierarchy = 'fecha'


admin.site.site_header = "HuertoSmart Administración"
admin.site.site_title = "HuertoSmart"
admin.site.index_title = "Panel de gestión"
