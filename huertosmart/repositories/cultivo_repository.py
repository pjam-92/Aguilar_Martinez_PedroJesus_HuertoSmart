# cultivo_repository.py — Repositorio de Cultivos
"""
Este repositorio gestiona todo el acceso a datos del modelo Cultivo.
Hereda los métodos básicos de BaseRepository (get_all, get_by_id, create,
update, delete, count) y añade métodos específicos para cultivos:
filtrado combinado por múltiples criterios, búsqueda por slug, etc.
"""

from .base_repository import BaseRepository
from huertosmart.models import Cultivo


class CultivoRepository(BaseRepository):
    """Repositorio para acceder y manipular cultivos."""

    # Indicamos a BaseRepository con qué modelo trabajamos
    model = Cultivo

    def buscar_por_nombre(self, nombre):
        """Busca cultivos cuyo nombre contenga el texto dado (sin distinguir mayúsculas)."""
        return self.model.objects.filter(nombre__icontains=nombre)



    def filtrar(self, busqueda=None, dificultad=None, exposicion=None,
                riego=None, mes_siembra=None):

        queryset = self.model.objects.all()

        if busqueda:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(nombre_cientifico__icontains=busqueda)
            )

        if dificultad:
            queryset = queryset.filter(dificultad=dificultad)
        if exposicion:
            queryset = queryset.filter(exposicion=exposicion)
        if riego:
            queryset = queryset.filter(riego=riego)
        if mes_siembra:
            # Los meses se guardan como CSV ("marzo,abril,mayo"), usamos icontains
            queryset = queryset.filter(meses_siembra__icontains=mes_siembra)

        return queryset

    def cultivos_de_temporada(self, mes):
        """Devuelve cultivos que se pueden sembrar en el mes dado."""
        return self.model.objects.filter(meses_siembra__icontains=mes)

    def cultivos_faciles(self):
        """Cultivos recomendados para principiantes (dificultad = fácil)."""
        return self.model.objects.filter(dificultad='facil')

    def get_by_slug(self, slug):
        """Busca un cultivo por su slug. Devuelve None si no existe."""
        return self.model.objects.filter(slug=slug).first()

