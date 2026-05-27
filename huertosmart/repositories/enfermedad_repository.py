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

    """¡! Explicación (buscar_por_nombre_modelo): Este método es el enlace clave
    entre la IA y la base de datos. El modelo MobileNetV2 fue entrenado con el
    dataset PlantVillage y devuelve nombres de clase en ese formato, como
    'Tomato___Early_blight' o 'Pepper,_bell___Bacterial_spot'. El campo
    nombre_modelo de cada Enfermedad almacena ese nombre exacto para que
    la búsqueda funcione. Si el modelo devuelve una clase sin correspondencia
    en el catálogo, se devuelve None y el diagnóstico se guarda sin enfermedad."""

    def filtrar_por_gravedad(self, gravedad):
        """Filtra enfermedades por su nivel de gravedad (leve, moderada, grave)."""
        return self.model.objects.filter(gravedad=gravedad)

    def enfermedades_de_cultivo(self, cultivo):
        """Devuelve todas las enfermedades que pueden afectar a un cultivo concreto."""
        return cultivo.enfermedades.all()

    """¡! Explicación (cultivo.enfermedades.all()): La relación ManyToMany entre
    Enfermedad y Cultivo tiene related_name='enfermedades' definido en el modelo.
    Esto significa que desde un objeto Cultivo podemos acceder a sus enfermedades
    directamente con cultivo.enfermedades.all(), sin pasar por el ORM explícitamente.
    Django gestiona la tabla intermedia de la relación de forma transparente."""
