from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .unidad import Unidad


class Accion:
    """Acción básica realizada por una unidad."""

    def __init__(self, unidad: Unidad):
        self.unidad = unidad

    def ejecutar(self, *args, **kwargs):  # pragma: no cover - interfaz
        raise NotImplementedError


class AccionAtaque(Accion):
    """Ataque estándar que considera la defensa del objetivo."""

    def ejecutar(self, objetivo: Unidad) -> int:
        return objetivo.recibir_daño(self.unidad.ataque)


class AccionCurar(Accion):
    """Restaura una cantidad fija de salud a un aliado."""

    def __init__(self, unidad: Unidad, cantidad: int = 10):
        super().__init__(unidad)
        self.cantidad = cantidad

    def ejecutar(self, aliado: Unidad) -> int:
        aliado.salud += self.cantidad
        return self.cantidad


class AccionFortificar(Accion):
    """Incrementa temporalmente la defensa de la unidad."""

    def ejecutar(self) -> None:
        self.unidad.defensa += 2


class AccionDisparoPreciso(Accion):
    """Ataque que ignora la defensa del objetivo."""

    def ejecutar(self, objetivo: Unidad) -> int:
        objetivo.salud -= self.unidad.ataque
        return self.unidad.ataque


class AccionCargar(Accion):
    """Ataque de carga con daño aumentado."""

    def ejecutar(self, objetivo: Unidad) -> int:
        daño = self.unidad.ataque * 2
        return objetivo.recibir_daño(daño)


class AccionProteger(Accion):
    """Aumenta la defensa de un aliado."""

    def ejecutar(self, aliado: Unidad) -> None:
        aliado.defensa += 3
