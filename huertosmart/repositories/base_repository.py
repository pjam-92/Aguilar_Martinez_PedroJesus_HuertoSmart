# base_repository.py — Repositorio base abstracto de HuertoSmart
"""
Este archivo define la clase base de la que heredan todos los repositorios
del proyecto. Es el núcleo del Patrón Repository (Requisito nº 7 del curso,
vale 2 puntos).

El Patrón Repository es una forma de organizar el código que separa dos
responsabilidades:
- Las VISTAS (views.py) se encargan de la lógica de negocio: qué hacer
  con los datos, qué mostrar al usuario, qué permisos comprobar.
- Los REPOSITORIOS se encargan del acceso a datos: cómo buscar, crear,
  actualizar o borrar registros en la base de datos.

Gracias a este patrón, si en el futuro se cambiara la base de datos de
SQLite a PostgreSQL, o el ORM de Django por otro sistema, solo habría
que tocar los repositorios — las vistas no cambiarían.
"""

from abc import ABC



class BaseRepository(ABC):
    """Clase abstracta base para todos los repositorios del proyecto.

    Define los métodos comunes que cualquier repositorio debe tener.
    Cada repositorio concreto hereda estos métodos y puede añadir
    los suyos propios específicos de su modelo.
    """


    # Cada repositorio hijo debe sobreescribir este atributo con su modelo concreto
    # Ejemplo: en CultivoRepository se define como model = Cultivo
    model = None

    def get_all(self):
        """Devuelve todos los objetos del modelo."""
        return self.model.objects.all()

    def get_by_id(self, obj_id):
        """Busca un objeto por su ID. Devuelve None si no existe."""
        try:
            return self.model.objects.get(pk=obj_id)
        except self.model.DoesNotExist:
            return None


    def create(self, **kwargs):
        """Crea y guarda un nuevo objeto en la base de datos."""
        return self.model.objects.create(**kwargs)


    def update(self, obj_id, **kwargs):
        """Actualiza los campos de un objeto existente."""
        obj = self.get_by_id(obj_id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            obj.save()
        return obj


    def delete(self, obj_id):
        """Elimina un objeto de la base de datos. Devuelve True si lo eliminó."""
        obj = self.get_by_id(obj_id)
        if obj:
            obj.delete()
            return True
        return False

    def count(self):
        """Cuenta el total de objetos del modelo en la base de datos."""
        return self.model.objects.count()
