"""Administración de grupos de unidades."""

from __future__ import annotations

import json

from .unidad import (
    Unidad,
    Infanteria,
    Arqueria,
    Caballeria,
    Defensa,
    Soporte,
)


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

    def exportar_json(self, ruta):
        """Guarda la lista de unidades en un archivo JSON.

        Parameters
        ----------
        ruta: str
            Ruta del archivo donde se almacenará la información.
        """

        datos = [
            {
                "id": str(u.id),
                "tipo": type(u).__name__,
                "salud": u.salud,
                "ataque": u.ataque,
                "defensa": u.defensa,
                "velocidad": u.velocidad,
                "alcance": u.alcance,
            }
            for u in self.unidades
        ]
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)


def crear_ejercito(config):
    """Crea un :class:`Ejercito` a partir de una configuración.

    Parameters
    ----------
    config:
        Lista de diccionarios con dos claves: ``tipo`` y ``cantidad``. El
        ``tipo`` debe ser el nombre de la clase de unidad como ``"Infanteria"`` y
        ``cantidad`` la cantidad de unidades de ese tipo que se desean crear.

    Returns
    -------
    Ejercito
        Objeto de ejército poblado con las unidades especificadas.
    """

    mapa_unidades = {
        "Infanteria": Infanteria,
        "Arqueria": Arqueria,
        "Caballeria": Caballeria,
        "Defensa": Defensa,
        "Soporte": Soporte,
    }

    ejercito = Ejercito()

    for elemento in config:
        tipo = elemento.get("tipo")
        cantidad = elemento.get("cantidad", 0)
        clase_unidad = mapa_unidades.get(tipo)
        if clase_unidad is None:
            raise ValueError(f"Tipo de unidad desconocido: {tipo}")
        for _ in range(cantidad):
            ejercito.agregar_unidad(clase_unidad())

    return ejercito
