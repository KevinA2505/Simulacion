import types
import sys
import pathlib

sys.modules.setdefault("pygame", types.ModuleType("pygame"))
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import pytest

from batalla.campo import CampoBatalla
from batalla.ejercito import Ejercito
from batalla.unidad import Soporte, Infanteria, Arqueria
from terreno import Terreno


def crear_campo_simple():
    terreno = Terreno(6, 1, densidad=0.0, densidad_bosque=0.0, num_rios=0, semilla=1)
    campo = CampoBatalla(terreno)
    ejercito_a = Ejercito()
    ejercito_b = Ejercito()

    soporte = Soporte()
    herido = Infanteria()
    arquero = Arqueria()
    enemigo = Infanteria()

    ejercito_a.agregar_unidad(soporte)
    ejercito_a.agregar_unidad(herido)
    ejercito_a.agregar_unidad(arquero)
    ejercito_b.agregar_unidad(enemigo)

    campo.colocar_unidad(soporte, 0, 0)
    campo.colocar_unidad(herido, 1, 0)
    campo.colocar_unidad(arquero, 3, 0)
    campo.colocar_unidad(enemigo, 5, 0)
    herido.salud = 50

    return campo, ejercito_a, ejercito_b, herido, enemigo


def test_simular_turno_en_fases():
    campo, ej_a, ej_b, herido, enemigo = crear_campo_simple()
    acciones = campo.simular_turno(ej_a, ej_b)
    tipos = [a["tipo"] for a in acciones]
    # Solo el enemigo se mueve: el aliado está bloqueado por otra unidad
    assert tipos == ["curar", "atacar", "mover"]
    assert campo.posicion(herido) == (1, 0)
    assert campo.posicion(enemigo) == (4, 0)
    assert enemigo.salud == 93  # 100 - (12 - 5)


def test_movimiento_evita_obstaculos():
    """Las unidades deben rodear obstáculos utilizando la búsqueda de camino."""
    terreno = Terreno(3, 3, densidad=0.0, densidad_bosque=0.0, num_rios=0, semilla=1)
    # Bloquea la celda intermedia para forzar un desvío
    terreno.mapa[0][1] = "PARED"
    terreno.colisiones[0][1] = True
    campo = CampoBatalla(terreno)
    ej_a = Ejercito()
    ej_b = Ejercito()
    u1 = Infanteria()
    u2 = Infanteria()
    ej_a.agregar_unidad(u1)
    ej_b.agregar_unidad(u2)
    campo.colocar_unidad(u1, 0, 0)
    campo.colocar_unidad(u2, 2, 0)

    campo.simular_turno(ej_a, ej_b)

    assert campo.posicion(u1) == (0, 1)
    assert campo.posicion(u2) == (2, 1)
