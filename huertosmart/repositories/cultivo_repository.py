"""
Repositorio de Cultivo.
"""
from .base_repository import BaseRepository
from huertosmart.models import Cultivo


class CultivoRepository(BaseRepository):
    """Repositorio para acceder y manipular cultivos."""

    model = Cultivo

    def buscar_por_nombre(self, nombre):
        """Busca cultivos cuyo nombre contenga el texto dado."""
        return self.model.objects.filter(nombre__icontains=nombre)

    def filtrar(self, busqueda=None, dificultad=None, exposicion=None,
                riego=None, mes_siembra=None):
        """Filtra cultivos combinando varios criterios opcionales.

        La búsqueda mira tanto en el nombre común como en el nombre científico.
        El mes de siembra se compara contra el campo CSV `meses_siembra`.
        """
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
            queryset = queryset.filter(meses_siembra__icontains=mes_siembra)

        return queryset

    def cultivos_de_temporada(self, mes):
        """Devuelve cultivos que se pueden sembrar en el mes dado."""
        return self.model.objects.filter(meses_siembra__icontains=mes)

    def cultivos_faciles(self):
        """Cultivos recomendados para principiantes."""
        return self.model.objects.filter(dificultad='facil')
