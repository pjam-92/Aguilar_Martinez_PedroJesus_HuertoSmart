"""
Repositorio de Siembra.
"""
from .base_repository import BaseRepository
from huertosmart.models import Siembra


class SiembraRepository(BaseRepository):
    """Repositorio para gestionar siembras."""

    model = Siembra

    def get_siembras_huerto(self, huerto):
        """Siembras de un huerto concreto."""
        return self.model.objects.filter(huerto=huerto)

    def get_siembras_activas(self, huerto):
        """Siembras que no están cosechadas ni perdidas."""
        return self.model.objects.filter(
            huerto=huerto
        ).exclude(estado__in=['cosechada', 'perdida'])

    def get_siembras_usuario(self, usuario):
        """Todas las siembras de todos los huertos de un usuario."""
        return self.model.objects.filter(huerto__usuario=usuario)

    def filtrar_por_estado(self, huerto, estado):
        """Siembras de un huerto en un estado concreto."""
        return self.model.objects.filter(huerto=huerto, estado=estado)
