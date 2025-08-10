"""Módulo que gestiona el campo de batalla y el avance de la simulación."""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

from terreno import Terreno

from .unidad import Unidad, Soporte
from .ejercito import Ejercito


class CampoBatalla:
    """Cuadrícula de combate ligada a un :class:`Terreno`.

    La clase mantiene la posición de cada unidad y permite avanzar turnos
    simulando movimiento, ataques y acciones de soporte. Las dimensiones y
    obstáculos provienen directamente del objeto :class:`Terreno` recibido en
    el constructor.
    """

    def __init__(self, terreno: Terreno):
        self.terreno = terreno
        self.ancho = terreno.ancho_tiles
        self.alto = terreno.alto_tiles
        self._grid: list[list[Unidad | None]] = [
            [None for _ in range(self.ancho)] for _ in range(self.alto)
        ]
        self._posiciones: Dict[Unidad, Tuple[int, int]] = {}
        self._salud_max: Dict[Unidad, int] = {}
        self._estadisticas = {
            "turno_actual": 0,
            "daño_total": 0,
            "curacion_total": 0,
            "daño_por_unidad": {},
        }

    # ------------------------------------------------------------------
    # Gestión de unidades
    # ------------------------------------------------------------------
    def es_transitable(self, x: int, y: int) -> bool:
        """Indica si una celda puede ser ocupada por una unidad."""

        if 0 <= x < self.ancho and 0 <= y < self.alto:
            bloque = self.terreno.mapa[y][x]
            return bloque not in ("PARED", "AGUA", "HUECO")
        return False

    def colocar_unidad(self, unidad: Unidad, x: int, y: int) -> None:
        """Ubica una unidad en la celda indicada."""

        if not self.es_transitable(x, y) or self._grid[y][x] is not None:
            raise ValueError("Posición inválida para la unidad")
        self._grid[y][x] = unidad
        self._posiciones[unidad] = (x, y)
        self._salud_max.setdefault(unidad, unidad.salud)

    def mover_unidad(self, unidad: Unidad, dx: int, dy: int) -> bool:
        """Intenta mover la unidad una casilla en la dirección dada."""

        x, y = self._posiciones[unidad]
        nx, ny = x + dx, y + dy
        if not self.es_transitable(nx, ny) or self._grid[ny][nx] is not None:
            return False
        self._grid[y][x] = None
        self._grid[ny][nx] = unidad
        self._posiciones[unidad] = (nx, ny)
        return True

    def eliminar_unidad(self, unidad: Unidad) -> None:
        """Retira una unidad del campo de batalla."""

        pos = self._posiciones.pop(unidad, None)
        if pos:
            x, y = pos
            self._grid[y][x] = None
        self._salud_max.pop(unidad, None)

    def posicion(self, unidad: Unidad) -> Tuple[int, int]:
        """Devuelve la posición actual de una unidad."""

        return self._posiciones[unidad]

    def unidades(self) -> Iterable[Unidad]:
        """Itera sobre todas las unidades presentes."""

        return list(self._posiciones.keys())

    # ------------------------------------------------------------------
    # Simulación
    # ------------------------------------------------------------------
    def _objetivo_cercano(self, unidad: Unidad, candidatos: Iterable[Unidad]) -> Unidad:
        ux, uy = self.posicion(unidad)
        return min(
            candidatos,
            key=lambda u: abs(self.posicion(u)[0] - ux) + abs(self.posicion(u)[1] - uy),
        )

    def simular_turno(self, ejercito_a: Ejercito, ejercito_b: Ejercito) -> list[dict]:
        """Avanza un turno completo para ambos ejércitos.

        Devuelve una lista de acciones realizadas durante el turno. Cada
        acción es un diccionario con una clave ``"tipo"`` que puede tomar los
        valores ``"mover"``, ``"atacar"`` o ``"curar"`` y otros campos
        relacionados con la acción.
        """

        acciones: list[dict] = []
        self._estadisticas["turno_actual"] += 1

        for unidad in list(self.unidades()):
            if not unidad.esta_viva():
                # Limpiamos la unidad caída del campo de batalla
                self.eliminar_unidad(unidad)
                ejercito_a.eliminar_unidad(unidad)
                ejercito_b.eliminar_unidad(unidad)
                continue

            enemigos = (
                ejercito_b.unidades if unidad in ejercito_a.unidades else ejercito_a.unidades
            )
            enemigos = [e for e in enemigos if e.esta_viva()]
            if not enemigos:
                continue
            objetivo = self._objetivo_cercano(unidad, enemigos)
            ux, uy = self.posicion(unidad)
            ox, oy = self.posicion(objetivo)
            dist = abs(ux - ox) + abs(uy - oy)

            # Acción de soporte
            if isinstance(unidad, Soporte):
                aliados = (
                    ejercito_a.unidades if unidad in ejercito_a.unidades else ejercito_b.unidades
                )
                heridos = [
                    a
                    for a in aliados
                    if a.esta_viva() and a.salud < self._salud_max.get(a, a.salud)
                ]
                if heridos:
                    aliado = self._objetivo_cercano(unidad, heridos)
                    ax, ay = self.posicion(aliado)
                    if abs(ux - ax) + abs(uy - ay) <= unidad.alcance:
                        cantidad = unidad.curar(aliado)
                        self._estadisticas["curacion_total"] += cantidad
                        acciones.append(
                            {
                                "tipo": "curar",
                                "unidad": unidad,
                                "objetivo": aliado,
                                "origen": (ux, uy),
                                "destino": (ax, ay),
                                "cantidad": cantidad,
                            }
                        )
                        continue

            # Ataque si está en alcance
            if dist <= unidad.alcance:
                daño = objetivo.recibir_daño(unidad.ataque)
                self._estadisticas["daño_total"] += daño
                self._estadisticas["daño_por_unidad"][unidad] = (
                    self._estadisticas["daño_por_unidad"].get(unidad, 0) + daño
                )
                acciones.append(
                    {
                        "tipo": "atacar",
                        "unidad": unidad,
                        "objetivo": objetivo,
                        "origen": (ux, uy),
                        "destino": (ox, oy),
                        "daño": daño,
                    }
                )
                if not objetivo.esta_viva():
                    self.eliminar_unidad(objetivo)
                    ejercito_a.eliminar_unidad(objetivo)
                    ejercito_b.eliminar_unidad(objetivo)
                continue

            # Movimiento básico hacia el objetivo
            dx = 1 if ox > ux else -1 if ox < ux else 0
            dy = 1 if oy > uy else -1 if oy < uy else 0
            if dx and self.mover_unidad(unidad, dx, 0):
                acciones.append(
                    {
                        "tipo": "mover",
                        "unidad": unidad,
                        "origen": (ux, uy),
                        "destino": (ux + dx, uy),
                    }
                )
                continue
            if dy and self.mover_unidad(unidad, 0, dy):
                acciones.append(
                    {
                        "tipo": "mover",
                        "unidad": unidad,
                        "origen": (ux, uy),
                        "destino": (ux, uy + dy),
                    }
                )

        return acciones

    def simular(self, ejercito_a: Ejercito, ejercito_b: Ejercito, turnos: int = 10) -> None:
        """Ejecuta varios turnos hasta que un ejército sea derrotado."""

        for _ in range(turnos):
            self.simular_turno(ejercito_a, ejercito_b)
            if not ejercito_a.unidades or not ejercito_b.unidades:
                break

    def obtener_estadisticas(self) -> dict:
        """Devuelve un resumen de la simulación realizada."""
        stats = dict(self._estadisticas)
        stats["daño_por_unidad"] = dict(self._estadisticas["daño_por_unidad"])
        return stats
