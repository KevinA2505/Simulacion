"""Utilidades para cargar ejércitos desde archivos JSON.

Formato de archivo esperado::

    {
        "faccion": "Nombre descriptivo",
        "unidades": [
            {"tipo": "Infanteria", "cantidad": 3},
            {"tipo": "Arqueria", "cantidad": 2}
        ],
        "bonificaciones": {
            "ataque": 1,
            "defensa": 2
        }
    }

La lista ``unidades`` se pasa a :func:`crear_ejercito` y las claves en
``bonificaciones`` son opcionales. Las bonificaciones se aplican a todas las
unidades del ejército.
"""

from __future__ import annotations

import json
from pathlib import Path

from .ejercito import crear_ejercito
from .facciones import EjercitoFaccion


def leer_ejercito(ruta: str | Path) -> EjercitoFaccion:
    """Lee un archivo JSON y construye un :class:`EjercitoFaccion`.

    Parameters
    ----------
    ruta:
        Ruta al archivo JSON con la descripción del ejército.

    Returns
    -------
    EjercitoFaccion
        Ejército con las unidades y bonificaciones indicadas en el archivo.
    """

    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    configuracion = datos.get("unidades", [])
    bonificaciones = datos.get("bonificaciones", {})

    base = crear_ejercito(configuracion)
    return EjercitoFaccion(base.unidades, bonificaciones)
