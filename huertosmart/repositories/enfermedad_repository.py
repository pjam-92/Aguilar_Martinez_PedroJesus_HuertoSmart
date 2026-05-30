# enfermedad_repository.py — Repositorio de Enfermedades
"""
Este repositorio gestiona todo el acceso a datos del modelo Enfermedad.
Su método más importante es buscar_por_nombre_modelo, que es el puente
entre el resultado del modelo de IA y la base de datos del proyecto.

Cuando el modelo MobileNetV2 devuelve un nombre de clase como
'Tomato___Early_blight', este repositorio busca la enfermedad correspondiente
en la base de datos para obtener su descripción, síntomas y tratamiento
en español.
"""

from .base_repository import BaseRepository
from huertosmart.models import Enfermedad


class EnfermedadRepository(BaseRepository):
    """Repositorio para gestionar el catálogo de enfermedades."""

    model = Enfermedad

    def buscar_por_nombre_modelo(self, nombre_modelo):
        """Busca una enfermedad por el nombre exacto que devuelve el modelo IA.

        Devuelve None si no hay ninguna enfermedad en el catálogo que coincida.
        """
        try:
            return self.model.objects.get(nombre_modelo=nombre_modelo)
        except self.model.DoesNotExist:
            return None


    def filtrar_por_gravedad(self, gravedad):
        """Filtra enfermedades por su nivel de gravedad (leve, moderada, grave)."""
        return self.model.objects.filter(gravedad=gravedad)

    def enfermedades_de_cultivo(self, cultivo):
        """Devuelve todas las enfermedades que pueden afectar a un cultivo concreto."""
        return cultivo.enfermedades.all()


