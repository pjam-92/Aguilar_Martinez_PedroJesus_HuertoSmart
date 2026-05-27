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

    """¡! Explicación (filtrar por objeto relacionado): En lugar de filtrar por
    huerto_id (el campo entero del ID), pasamos directamente el objeto Huerto.
    Django resuelve automáticamente la comparación usando el ID del objeto.
    Ambas formas funcionan: filter(huerto=huerto) y filter(huerto_id=huerto.pk)."""

    def get_siembras_activas(self, huerto):
        """Siembras en curso: excluye las que están cosechadas o perdidas."""
        return self.model.objects.filter(
            huerto=huerto
        ).exclude(estado__in=['cosechada', 'perdida'])

    """¡! Explicación (.exclude con __in): .exclude() es el contrario de .filter(),
    devuelve los registros que NO cumplen la condición. __in permite comparar
    contra una lista de valores: estado__in=['cosechada', 'perdida'] significa
    'cuyo estado sea cosechada O perdida'. La combinación devuelve las siembras
    que aún están activas."""

    def get_siembras_usuario(self, usuario):
        """Todas las siembras de todos los huertos de un usuario."""
        return self.model.objects.filter(huerto__usuario=usuario)

    """¡! Explicación (lookup con doble guión bajo en ForeignKey): huerto__usuario
    navega la relación ForeignKey de Siembra a Huerto, y de Huerto a User.
    Django genera automáticamente el JOIN necesario en SQL. Es una de las
    características más potentes del ORM de Django."""

    def filtrar_por_estado(self, huerto, estado):
        """Devuelve las siembras de un huerto que tienen un estado concreto."""
        return self.model.objects.filter(huerto=huerto, estado=estado)

    """¡! Explicación (filtrar_por_estado): Este método es el que usa la vista
    detalle_huerto cuando el usuario selecciona un filtro de estado en el panel.
    El estado llega como parámetro GET en la URL y se pasa directamente aquí."""
