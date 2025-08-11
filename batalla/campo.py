"""Módulo que gestiona el campo de batalla y el avance de la simulación."""

from __future__ import annotations

import json
from typing import Dict, Iterable, Tuple, Set, List

from terreno import Terreno

from .unidad import Unidad
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
        self._replay: list[dict] = []
        # Caché de rutas calculadas por unidad. Cada entrada almacena la
        # posición de destino y la lista de pasos pendientes para alcanzarlo.
        self._ruta_cache: Dict[Unidad, Tuple[Tuple[int, int], List[Tuple[int, int]]]] = {}

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
        self._ruta_cache.pop(unidad, None)

    def posicion(self, unidad: Unidad) -> Tuple[int, int]:
        """Devuelve la posición actual de una unidad."""

        return self._posiciones[unidad]

    def unidades(self) -> Iterable[Unidad]:
        """Itera sobre todas las unidades presentes."""

        return list(self._posiciones.keys())

    def cola_iniciativa(self) -> List[Unidad]:
        """Devuelve las unidades ordenadas por su ``velocidad``.

        La lista resultante representa la cola de iniciativas donde las
        unidades con mayor valor de ``velocidad`` actúan antes durante un
        turno de simulación.
        """

        return sorted(self._posiciones.keys(), key=lambda u: u.velocidad, reverse=True)

    # ------------------------------------------------------------------
    # Simulación
    # ------------------------------------------------------------------

    def _buscar_camino(
        self, origen: Tuple[int, int], destino: Tuple[int, int]
    ) -> List[Tuple[int, int]] | None:
        """Calcula un camino entre dos puntos evitando obstáculos y unidades.

        Se utiliza el algoritmo A* considerando como no transitables tanto
        las celdas marcadas en el terreno como las ocupadas por otras
        unidades (excepto el propio destino, que puede contener un enemigo).
        Devuelve una lista de coordenadas ``[(x, y), ...]`` que incluyen el
        origen y el destino. Si no existe camino, retorna ``None``.
        """

        from heapq import heappush, heappop

        if origen == destino:
            return [origen]

        def heuristica(a: Tuple[int, int], b: Tuple[int, int]) -> int:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        abiertos: List[Tuple[int, Tuple[int, int]]] = []
        heappush(abiertos, (0, origen))
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], int] = {origen: 0}

        while abiertos:
            _, actual = heappop(abiertos)
            if actual == destino:
                camino = [actual]
                while actual in came_from:
                    actual = came_from[actual]
                    camino.append(actual)
                camino.reverse()
                return camino

            x, y = actual
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.ancho and 0 <= ny < self.alto):
                    continue
                if not self.es_transitable(nx, ny):
                    continue
                if self._grid[ny][nx] is not None and (nx, ny) != destino:
                    continue

                vecino = (nx, ny)
                tentativo = g_score[actual] + 1
                if tentativo < g_score.get(vecino, float("inf")):
                    came_from[vecino] = actual
                    g_score[vecino] = tentativo
                    f_score = tentativo + heuristica(vecino, destino)
                    heappush(abiertos, (f_score, vecino))

        return None
    def _objetivo_cercano(self, unidad: Unidad, candidatos: Iterable[Unidad]) -> Unidad:
        ux, uy = self.posicion(unidad)
        return min(
            candidatos,
            key=lambda u: abs(self.posicion(u)[0] - ux) + abs(self.posicion(u)[1] - uy),
        )

    def resolver_curaciones(
        self, ejercito_a: Ejercito, ejercito_b: Ejercito, orden: Iterable[Unidad]
    ) -> tuple[list[dict], Set[Unidad]]:
        """Gestiona las acciones de curación de las unidades."""

        acciones: list[dict] = []
        actuaron: Set[Unidad] = set()
        for unidad in orden:
            accion_curar = unidad.acciones.get("curar")
            if accion_curar is None or not unidad.esta_viva():
                continue

            aliados = (
                ejercito_a.unidades if unidad in ejercito_a.unidades else ejercito_b.unidades
            )
            heridos = [
                a
                for a in aliados
                if a.esta_viva() and a.salud < self._salud_max.get(a, a.salud)
            ]
            if not heridos:
                continue

            aliado = self._objetivo_cercano(unidad, heridos)
            ux, uy = self.posicion(unidad)
            ax, ay = self.posicion(aliado)
            if abs(ux - ax) + abs(uy - ay) <= unidad.alcance:
                cantidad = accion_curar.ejecutar(aliado)
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
                actuaron.add(unidad)

        return acciones, actuaron

    def resolver_ataques(
        self,
        ejercito_a: Ejercito,
        ejercito_b: Ejercito,
        orden: Iterable[Unidad],
        unidades_excluidas: Set[Unidad],
    ) -> tuple[list[dict], Set[Unidad]]:
        """Resuelve los ataques de las unidades que no han actuado."""

        acciones: list[dict] = []
        actuaron: Set[Unidad] = set()
        for unidad in orden:
            if unidad in unidades_excluidas or not unidad.esta_viva():
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
            if dist > unidad.alcance:
                continue

            accion_atacar = unidad.acciones.get("atacar")
            if accion_atacar is None:
                continue
            daño = accion_atacar.ejecutar(objetivo)
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
            actuaron.add(unidad)

        return acciones, actuaron

    def resolver_movimientos(
        self,
        ejercito_a: Ejercito,
        ejercito_b: Ejercito,
        orden: Iterable[Unidad],
        unidades_excluidas: Set[Unidad],
    ) -> list[dict]:
        """Mueve las unidades restantes hacia su objetivo más cercano.

        Cada unidad calcula una ruta completa mediante búsqueda de caminos y
        avanza un único paso siguiendo dicha ruta. Las rutas se almacenan en
        una caché para reutilizarlas entre turnos mientras sigan siendo
        válidas.
        """

        acciones: list[dict] = []
        for unidad in orden:
            if unidad in unidades_excluidas or not unidad.esta_viva():
                continue

            enemigos = (
                ejercito_b.unidades if unidad in ejercito_a.unidades else ejercito_a.unidades
            )
            enemigos = [e for e in enemigos if e.esta_viva()]
            if not enemigos:
                continue

            objetivo = self._objetivo_cercano(unidad, enemigos)
            destino = self.posicion(objetivo)
            actual = self.posicion(unidad)

            # Recuperar o calcular la ruta hacia el objetivo
            cache = self._ruta_cache.get(unidad)
            if not cache or cache[0] != destino or not cache[1]:
                ruta = self._buscar_camino(actual, destino)
                if ruta and len(ruta) > 1:
                    ruta = ruta[1:]  # Excluir la posición actual
                    self._ruta_cache[unidad] = (destino, ruta)
                else:
                    self._ruta_cache.pop(unidad, None)
                    continue

            destino_cache, ruta = self._ruta_cache[unidad]
            siguiente = ruta[0]
            dx = siguiente[0] - actual[0]
            dy = siguiente[1] - actual[1]

            if self.mover_unidad(unidad, dx, dy):
                acciones.append(
                    {
                        "tipo": "mover",
                        "unidad": unidad,
                        "origen": actual,
                        "destino": (actual[0] + dx, actual[1] + dy),
                    }
                )
                ruta.pop(0)
                if ruta:
                    self._ruta_cache[unidad] = (destino_cache, ruta)
                else:
                    self._ruta_cache.pop(unidad, None)
            else:
                # Si el movimiento falla (p.ej., celda ocupada), recalcular ruta
                self._ruta_cache.pop(unidad, None)

        return acciones

    def simular_turno(self, ejercito_a: Ejercito, ejercito_b: Ejercito) -> list[dict]:
        """Avanza un turno completo para ambos ejércitos.

        Devuelve una lista de acciones realizadas durante el turno. Cada
        acción es un diccionario con una clave ``"tipo"`` que puede tomar los
        valores ``"mover"``, ``"atacar"`` o ``"curar"`` y otros campos
        relacionados con la acción.
        """

        acciones: list[dict] = []
        self._estadisticas["turno_actual"] += 1

        # Limpiar unidades que hayan muerto en turnos previos
        for unidad in list(self.unidades()):
            if not unidad.esta_viva():
                self.eliminar_unidad(unidad)
                ejercito_a.eliminar_unidad(unidad)
                ejercito_b.eliminar_unidad(unidad)
        # Cola de iniciativas basada en la velocidad de las unidades
        orden = self.cola_iniciativa()

        curaciones, actuaron = self.resolver_curaciones(ejercito_a, ejercito_b, orden)
        acciones.extend(curaciones)
        ataques, atacantes = self.resolver_ataques(
            ejercito_a, ejercito_b, orden, actuaron
        )
        acciones.extend(ataques)
        actuaron.update(atacantes)
        movimientos = self.resolver_movimientos(
            ejercito_a, ejercito_b, orden, actuaron
        )
        acciones.extend(movimientos)

        self._replay.append(
            {
                "turno": self._estadisticas["turno_actual"],
                "acciones": list(acciones),
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

    def exportar_replay(self, ruta: str) -> None:
        """Guarda en ``ruta`` el registro completo de acciones realizadas.

        El archivo generado es una lista de turnos, cada uno con las acciones
        ocurridas en orden. Las unidades se representan mediante su clase e
        identificador único para que otros módulos puedan reconstruir la
        batalla paso a paso.
        """

        datos = []
        for turno in self._replay:
            acciones = []
            for acc in turno["acciones"]:
                item = dict(acc)
                if "unidad" in item:
                    u = item["unidad"]
                    item["unidad"] = {"id": str(u.id), "tipo": u.__class__.__name__}
                if "objetivo" in item:
                    o = item["objetivo"]
                    item["objetivo"] = {"id": str(o.id), "tipo": o.__class__.__name__}
                if "origen" in item:
                    item["origen"] = list(item["origen"])
                if "destino" in item:
                    item["destino"] = list(item["destino"])
                acciones.append(item)
            datos.append({"turno": turno["turno"], "acciones": acciones})

        with open(ruta, "w", encoding="utf-8") as fh:
            json.dump(datos, fh, ensure_ascii=False, indent=2)
