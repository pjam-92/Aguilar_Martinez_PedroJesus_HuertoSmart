# siembra_repository.py — Repositorio de Siembras
"""
Este repositorio gestiona todo el acceso a datos del modelo Siembra.
Proporciona métodos para obtener las siembras de un huerto, filtrarlas
por estado y obtener las siembras activas (no finalizadas).
"""

from .base_repository import BaseRepository
from huertosmart.models import Siembra


class SiembraRepository(BaseRepository):
    """Repositorio para gestionar siembras."""

    model = Siembra

    def get_siembras_huerto(self, huerto):
        """Devuelve todas las siembras de un huerto concreto."""
        return self.model.objects.filter(huerto=huerto)


    def get_siembras_activas(self, huerto):
        """Siembras en curso: excluye las que están cosechadas o perdidas."""
        return self.model.objects.filter(
            huerto=huerto
        ).exclude(estado__in=['cosechada', 'perdida'])


    def get_siembras_usuario(self, usuario):
        """Todas las siembras de todos los huertos de un usuario."""
        return self.model.objects.filter(huerto__usuario=usuario)


    def filtrar_por_estado(self, huerto, estado):
        """Devuelve las siembras de un huerto que tienen un estado concreto."""
        return self.model.objects.filter(huerto=huerto, estado=estado)

