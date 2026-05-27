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

    """¡! Explicación (__icontains): Los lookups de Django se escriben con doble
    guión bajo. 'icontains' significa 'contiene este texto, ignorando mayúsculas'.
    nombre__icontains='tom' encontraría 'Tomate', 'tomate', 'TOMATE', etc.
    Otros lookups útiles: __exact (igual exacto), __startswith (empieza por),
    __gte (mayor o igual que), __in (está en la lista)."""

    def filtrar(self, busqueda=None, dificultad=None, exposicion=None,
                riego=None, mes_siembra=None):
        """Filtra cultivos combinando varios criterios opcionales.

        Cada parámetro es opcional. Solo se aplican los filtros que tienen valor.
        La búsqueda mira tanto en el nombre común como en el nombre científico.
        El mes de siembra se compara contra el campo CSV 'meses_siembra'.
        """
        queryset = self.model.objects.all()

        """¡! Explicación (queryset encadenado): Empezamos con todos los cultivos
        y vamos aplicando filtros uno a uno. Cada .filter() devuelve un nuevo
        queryset más reducido. Django no ejecuta la consulta SQL hasta que
        realmente se necesitan los datos (evaluación perezosa o lazy evaluation)."""

        if busqueda:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(nombre__icontains=busqueda) |
                Q(nombre_cientifico__icontains=busqueda)
            )

        """¡! Explicación (objeto Q): Q permite combinar condiciones con operadores
        lógicos. Q(a) | Q(b) significa 'a O b' (OR). Q(a) & Q(b) significa
        'a Y b' (AND). Sin Q, todos los filtros encadenados se comportan como AND.
        Aquí buscamos cultivos cuyo nombre O nombre científico contengan el texto."""

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

    """¡! Explicación (get_by_slug): Este método fue añadido durante la fase de
    corrección del proyecto para que la vista detalle_cultivo usara el repositorio
    en lugar de acceder directamente al ORM. Es el mismo tipo de consulta que
    hacía la vista, pero ahora centralizada en el repositorio."""
