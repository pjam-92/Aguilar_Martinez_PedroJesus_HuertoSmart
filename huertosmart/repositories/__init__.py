# repositories/__init__.py — Punto de entrada del paquete de repositorios
"""
Este archivo convierte la carpeta 'repositories' en un paquete Python importable.
Al declarar aquí todos los repositorios, cualquier archivo del proyecto puede
importarlos de forma simplificada desde '.repositories' directamente,
sin necesidad de conocer en qué módulo interno está cada clase.

Ejemplo de uso desde views.py:
    from .repositories import CultivoRepository, HuertoRepository
"""

from .cultivo_repository import CultivoRepository
from .huerto_repository import HuertoRepository
from .siembra_repository import SiembraRepository
from .diagnostico_repository import DiagnosticoRepository
from .enfermedad_repository import EnfermedadRepository

# Lista pública del paquete — define qué se exporta al hacer 'from .repositories import *'
__all__ = [
    'CultivoRepository',
    'HuertoRepository',
    'SiembraRepository',
    'DiagnosticoRepository',
    'EnfermedadRepository',
]
