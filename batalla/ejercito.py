"""Administración de grupos de unidades."""

from __future__ import annotations

from .unidad import Unidad


class Ejercito:
    """Colección de unidades con capacidad ofensiva."""

    def __init__(self):
        self.unidades = []

    def agregar_unidad(self, unidad: Unidad):
        """Añade una unidad al ejército."""
        self.unidades.append(unidad)

    def eliminar_unidad(self, unidad: Unidad):
        """Elimina una unidad del ejército si está presente."""
        if unidad in self.unidades:
            self.unidades.remove(unidad)

    def atacar(self, objetivo):
        """Ataca a una :class:`Unidad` o a otro :class:`Ejercito`.

        El ataque se ejecuta secuencialmente con cada unidad ofensiva.
        """
        for atacante in self.unidades:
            if isinstance(objetivo, Unidad):
                objetivo.recibir_daño(atacante.ataque)
                if not objetivo.esta_viva():
                    break
            elif isinstance(objetivo, Ejercito):
                if not objetivo.unidades:
                    break
                defensor = objetivo.unidades[0]
                defensor.recibir_daño(atacante.ataque)
                if not defensor.esta_viva():
                    objetivo.eliminar_unidad(defensor)
            else:
                raise ValueError("Objetivo no soportado")
