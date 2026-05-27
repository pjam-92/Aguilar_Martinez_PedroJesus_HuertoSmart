# apps.py — Configuración de la aplicación HuertoSmart
"""
Este archivo registra la aplicación 'huertosmart' dentro del proyecto Django.
Es un archivo estándar que Django genera automáticamente al crear una app
con 'python manage.py startapp'. Rara vez necesita modificarse.

Para que Django reconozca esta app, debe estar listada en INSTALLED_APPS
dentro de miproyectodjango/settings.py como 'huertosmart.apps.HuertosmartConfig'.
"""

from django.apps import AppConfig


class HuertosmartConfig(AppConfig):
    """Clase de configuración de la app huertosmart."""

    # Tipo de campo automático para las claves primarias de los modelos
    default_auto_field = 'django.db.models.BigAutoField'

    """¡! Explicación (default_auto_field): Define el tipo de campo que Django
    usa para generar automáticamente el campo 'id' (clave primaria) de cada
    modelo. BigAutoField es un entero de 64 bits, suficiente para cualquier
    aplicación. Es el valor por defecto en versiones modernas de Django."""

    # Nombre interno de la app — debe coincidir con el nombre de la carpeta
    name = 'huertosmart'

    # Nombre legible que aparece en el panel de administración
    verbose_name = 'HuertoSmart'
