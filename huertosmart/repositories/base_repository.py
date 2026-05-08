"""
Repositorio base abstracto.

Define el contrato común que todos los repositorios deben implementar.
Este patrón Repository separa el acceso a datos de la lógica de negocio,
facilitando el mantenimiento y los tests del proyecto.
"""
from abc import ABC


class BaseRepository(ABC):
    """Clase abstracta base para todos los repositorios."""

    model = None

    def get_all(self):
        """Devuelve todos los objetos."""
        return self.model.objects.all()

    def get_by_id(self, obj_id):
        """Busca un objeto por su id. Devuelve None si no existe."""
        try:
            return self.model.objects.get(pk=obj_id)
        except self.model.DoesNotExist:
            return None

    def create(self, **kwargs):
        """Crea un nuevo objeto."""
        return self.model.objects.create(**kwargs)

    def update(self, obj_id, **kwargs):
        """Actualiza un objeto existente."""
        obj = self.get_by_id(obj_id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
        return obj

    def delete(self, obj_id):
        """Elimina un objeto."""
        obj = self.get_by_id(obj_id)
        if obj:
            obj.delete()
            return True
        return False

    def count(self):
        """Cuenta los objetos."""
        return self.model.objects.count()
