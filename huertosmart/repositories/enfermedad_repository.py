"""
Repositorio de Enfermedad.
"""
from .base_repository import BaseRepository
from huertosmart.models import Enfermedad


class EnfermedadRepository(BaseRepository):
    """Repositorio para gestionar el catálogo de enfermedades."""

    model = Enfermedad

    def buscar_por_nombre_modelo(self, nombre_modelo):
        """Busca una enfermedad por el nombre que devuelve el modelo IA."""
        try:
            return self.model.objects.get(nombre_modelo=nombre_modelo)
        except self.model.DoesNotExist:
            return None

    def filtrar_por_gravedad(self, gravedad):
        """Filtra enfermedades por gravedad."""
        return self.model.objects.filter(gravedad=gravedad)

    def enfermedades_de_cultivo(self, cultivo):
        """Devuelve las enfermedades que afectan a un cultivo concreto."""
        return cultivo.enfermedades.all()
