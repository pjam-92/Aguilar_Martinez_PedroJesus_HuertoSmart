# diagnostico_repository.py — Repositorio de Diagnósticos
"""
Este repositorio gestiona todo el acceso a datos del modelo Diagnostico.
Los diagnósticos son los resultados de los análisis de IA realizados sobre
fotos de plantas. Este repositorio permite consultar el historial de un
usuario y obtener estadísticas sobre los diagnósticos realizados.
"""

from .base_repository import BaseRepository
from huertosmart.models import Diagnostico


class DiagnosticoRepository(BaseRepository):
    """Repositorio para gestionar diagnósticos de IA."""

    model = Diagnostico

    def get_diagnosticos_usuario(self, usuario, limite=None):
        """Devuelve los diagnósticos de un usuario, ordenados del más reciente al más antiguo.

        Si se especifica un límite, devuelve solo los N más recientes.
        """
        queryset = self.model.objects.filter(usuario=usuario).order_by('-fecha')
        if limite:
            queryset = queryset[:limite]
        return queryset


    def get_ultimos_diagnosticos(self, limite=10):
        """Últimos diagnósticos del sistema completo (para estadísticas globales)."""
        return self.model.objects.all().order_by('-fecha')[:limite]

    def diagnosticos_con_enfermedad(self, usuario):
        """Diagnósticos de un usuario donde el modelo IA detectó una enfermedad."""
        return self.model.objects.filter(
            usuario=usuario,
            enfermedad_detectada__isnull=False
        )


    def fotos_validas(self, usuario):
        """Diagnósticos donde AWS Rekognition confirmó que la imagen era una planta."""
        return self.model.objects.filter(usuario=usuario, es_planta_valida=True)
