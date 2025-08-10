"""Configuraciones predefinidas de ejércitos por facción."""

from __future__ import annotations

from .ejercito import Ejercito
from .unidad import (
    Infanteria,
    Arqueria,
    Caballeria,
    Defensa,
    Soporte,
)


class EjercitoFaccion(Ejercito):
    """Ejército con bonificaciones globales.

    Las bonificaciones se aplican a todas las unidades presentes al
    momento de la creación del ejército.
    """

    def __init__(self, unidades=None, bonificaciones=None):
        super().__init__()
        self.bonificaciones = bonificaciones or {}
        unidades = unidades or []
        for unidad in unidades:
            self.agregar_unidad(unidad)
        self._aplicar_bonificaciones()

    def _aplicar_bonificaciones(self):
        for unidad in self.unidades:
            unidad.ataque += self.bonificaciones.get("ataque", 0)
            unidad.defensa += self.bonificaciones.get("defensa", 0)
            unidad.salud += self.bonificaciones.get("salud", 0)
            unidad.velocidad += self.bonificaciones.get("velocidad", 0)
            unidad.alcance += self.bonificaciones.get("alcance", 0)


class EjercitoMagia(EjercitoFaccion):
    """Ejército enfocado en el uso de la magia.

    Unidades: Soporte y Arquería.
    Bonificaciones: +2 ataque, +1 alcance.
    """

    def __init__(self):
        unidades = [Soporte(), Arqueria(), Soporte()]
        bonificaciones = {"ataque": 2, "alcance": 1}
        super().__init__(unidades, bonificaciones)


class EjercitoAngeles(EjercitoFaccion):
    """Ejército de seres angelicales.

    Unidades: Infantería, Caballería y Soporte.
    Bonificaciones: +2 defensa, +20 salud.
    """

    def __init__(self):
        unidades = [Infanteria(), Caballeria(), Soporte()]
        bonificaciones = {"defensa": 2, "salud": 20}
        super().__init__(unidades, bonificaciones)


class EjercitoDemonios(EjercitoFaccion):
    """Ejército de criaturas demoníacas.

    Unidades: Infantería, Arquería y Caballería.
    Bonificaciones: +3 ataque.
    """

    def __init__(self):
        unidades = [Infanteria(), Arqueria(), Caballeria()]
        bonificaciones = {"ataque": 3}
        super().__init__(unidades, bonificaciones)

