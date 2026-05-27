# huerto_repository.py — Repositorio de Huertos
"""
Este repositorio gestiona todo el acceso a datos del modelo Huerto.
Incluye métodos para obtener los huertos de un usuario, búsqueda por slug
y el soft delete (borrado lógico mediante el campo 'activo').
"""

from .base_repository import BaseRepository
from huertosmart.models import Huerto


class HuertoRepository(BaseRepository):
    """Repositorio para gestionar huertos de usuarios."""

    model = Huerto

    def get_huertos_usuario(self, usuario):
        """Devuelve todos los huertos activos de un usuario concreto."""
        return self.model.objects.filter(usuario=usuario, activo=True)

    """¡! Explicación (activo=True en el filtro): Solo devolvemos huertos activos.
    Los huertos eliminados por el usuario tienen activo=False (soft delete) y
    no deben aparecer en ninguna lista ni ser accesibles. Este filtro garantiza
    que un huerto eliminado no vuelva a aparecer aunque alguien conozca su slug."""

    def get_huerto_principal(self, usuario):
        """Devuelve el huerto más reciente del usuario (el primero creado según orden)."""
        return self.model.objects.filter(
            usuario=usuario, activo=True
        ).order_by('-fecha_creacion').first()

    def desactivar(self, huerto_id):
        """Soft delete: marca un huerto como inactivo en lugar de borrarlo físicamente."""
        huerto = self.get_by_id(huerto_id)
        if huerto:
            huerto.activo = False
            huerto.save()
        return huerto

    """¡! Explicación (soft delete vs delete real): La vista eliminar_huerto usa
    huerto.delete() directamente, que borra el registro de la base de datos.
    Este método desactivar() es una alternativa que solo marca el campo activo=False,
    conservando el registro. Está disponible en el repositorio para usarlo si en
    el futuro se quisiera cambiar el comportamiento de eliminación."""

    def get_by_slug(self, slug):
        """Busca un huerto activo por su slug. Devuelve None si no existe."""
        return self.model.objects.filter(slug=slug, activo=True).first()

    """¡! Explicación (activo=True en get_by_slug): Importante: solo buscamos
    entre huertos activos. Si un usuario accede a la URL de un huerto que ya
    eliminó, este método devuelve None y la vista lo redirige correctamente,
    como si el huerto no existiera."""
