"""
Repositorio de Huerto.
"""
from .base_repository import BaseRepository
from huertosmart.models import Huerto


class HuertoRepository(BaseRepository):
    """Repositorio para gestionar huertos de usuarios."""

    model = Huerto

    def get_huertos_usuario(self, usuario):
        """Devuelve todos los huertos activos de un usuario."""
        return self.model.objects.filter(usuario=usuario, activo=True)

    def get_huerto_principal(self, usuario):
        """Devuelve el huerto más reciente de un usuario."""
        return self.model.objects.filter(
            usuario=usuario, activo=True
        ).order_by('-fecha_creacion').first()

    def desactivar(self, huerto_id):
        """Soft delete: marca un huerto como inactivo en lugar de borrarlo."""
        huerto = self.get_by_id(huerto_id)
        if huerto:
            huerto.activo = False
            huerto.save()
        return huerto
