"""
Repositorio de Diagnóstico.
"""
from .base_repository import BaseRepository
from huertosmart.models import Diagnostico


class DiagnosticoRepository(BaseRepository):
    """Repositorio para gestionar diagnósticos de IA."""

    model = Diagnostico

    def get_diagnosticos_usuario(self, usuario, limite=None):
        """Diagnósticos de un usuario, opcionalmente limitados."""
        queryset = self.model.objects.filter(usuario=usuario).order_by('-fecha')
        if limite:
            queryset = queryset[:limite]
        return queryset

    def get_ultimos_diagnosticos(self, limite=10):
        """Últimos diagnósticos del sistema (para estadísticas globales)."""
        return self.model.objects.all().order_by('-fecha')[:limite]

    def diagnosticos_con_enfermedad(self, usuario):
        """Diagnósticos donde se detectó una enfermedad concreta."""
        return self.model.objects.filter(
            usuario=usuario,
            enfermedad_detectada__isnull=False
        )

    def fotos_validas(self, usuario):
        """Diagnósticos donde Rekognition validó que era una planta."""
        return self.model.objects.filter(usuario=usuario, es_planta_valida=True)
