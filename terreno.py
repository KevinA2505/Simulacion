"""Generación y representación del terreno del juego."""

import json
import random
import pygame

import constantes as const


def _clamp(valor, minimo=0, maximo=255):
    """Mantiene un valor dentro del rango [minimo, maximo]."""
    return max(minimo, min(maximo, valor))


class Terreno:
    """Mapa del mundo compuesto por diferentes tipos de tiles."""

    def __init__(
        self,
        ancho_tiles,
        alto_tiles,
        densidad=0.1,
        densidad_bosque=0.1,
        num_rios=1,
        semilla=None,
    ):
        self.ancho_tiles = ancho_tiles
        self.alto_tiles = alto_tiles
        self.densidad = densidad
        self.densidad_bosque = densidad_bosque
        self.num_rios = num_rios
        self.mapa = []
        self.colisiones = []
        self.rutas = []
        if semilla is not None:
            random.seed(semilla)
        self.generar()

    # ------------------------------------------------------------------
    # Generación del terreno
    # ------------------------------------------------------------------
    def generar(self):
        self.mapa = []
        self.colisiones = [[False] * self.ancho_tiles for _ in range(self.alto_tiles)]
        self.rutas = []
        for y in range(self.alto_tiles):
            fila = []
            for x in range(self.ancho_tiles):
                if random.random() < self.densidad_bosque:
                    fila.append("BOSQUE")
                else:
                    fila.append("SUELO")
                # SUELO y BOSQUE son transitables por defecto
            self.mapa.append(fila)
        self._generar_paredes()
        self._generar_rios()

    def _generar_paredes(self):
        """Genera paredes conectadas en grupos."""
        total_celdas = self.ancho_tiles * self.alto_tiles
        objetivo = int(total_celdas * self.densidad)
        creadas = 0
        intentos = 0
        max_intentos = objetivo * 5 if objetivo > 0 else total_celdas
        while creadas < objetivo and intentos < max_intentos:
            intentos += 1
            x = random.randrange(self.ancho_tiles)
            y = random.randrange(self.alto_tiles)
            if self.mapa[y][x] != "SUELO":
                continue
            dx, dy = random.choice([(1, 0), (0, 1)])
            longitud = random.randint(2, 6)
            for i in range(longitud):
                nx = x + dx * i
                ny = y + dy * i
                if (
                    0 <= nx < self.ancho_tiles
                    and 0 <= ny < self.alto_tiles
                    and self.mapa[ny][nx] == "SUELO"
                ):
                    self.mapa[ny][nx] = "PARED"
                    self.colisiones[ny][nx] = True
                    creadas += 1
                    if creadas >= objetivo:
                        break
                else:
                    break

    def _generar_rios(self):
        """Crea ríos con orientación vertical, horizontal o diagonal.

        Tras generar cada río, coloca aleatoriamente entre 2 y 3 puentes
        (celdas "PUENTE") para permitir el cruce del mismo.
        """

        direcciones = ["vertical", "horizontal", "diagonal"]
        for _ in range(self.num_rios):
            orient = random.choice(direcciones)
            coords = []  # Coordenadas del río actual

            if orient == "vertical":
                x = random.randrange(self.ancho_tiles)
                y = 0
                while y < self.alto_tiles:
                    self.mapa[y][x] = "AGUA"
                    self.colisiones[y][x] = True
                    coords.append((x, y))
                    if x > 0 and random.random() < 0.3:
                        self.mapa[y][x - 1] = "AGUA"
                        self.colisiones[y][x - 1] = True
                        coords.append((x - 1, y))
                    if x < self.ancho_tiles - 1 and random.random() < 0.3:
                        self.mapa[y][x + 1] = "AGUA"
                        self.colisiones[y][x + 1] = True
                        coords.append((x + 1, y))
                    x += random.choice([-1, 0, 1])
                    x = max(0, min(self.ancho_tiles - 1, x))
                    y += 1

            elif orient == "horizontal":
                y = random.randrange(self.alto_tiles)
                x = 0
                while x < self.ancho_tiles:
                    self.mapa[y][x] = "AGUA"
                    self.colisiones[y][x] = True
                    coords.append((x, y))
                    if y > 0 and random.random() < 0.3:
                        self.mapa[y - 1][x] = "AGUA"
                        self.colisiones[y - 1][x] = True
                        coords.append((x, y - 1))
                    if y < self.alto_tiles - 1 and random.random() < 0.3:
                        self.mapa[y + 1][x] = "AGUA"
                        self.colisiones[y + 1][x] = True
                        coords.append((x, y + 1))
                    y += random.choice([-1, 0, 1])
                    y = max(0, min(self.alto_tiles - 1, y))
                    x += 1

            else:  # diagonal
                if random.choice([True, False]):
                    x = 0
                    dx_dir = 1
                else:
                    x = self.ancho_tiles - 1
                    dx_dir = -1
                y = 0
                while 0 <= x < self.ancho_tiles and y < self.alto_tiles:
                    self.mapa[y][x] = "AGUA"
                    self.colisiones[y][x] = True
                    coords.append((x, y))
                    for dx_off, dy_off in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx_off, y + dy_off
                        if (
                            0 <= nx < self.ancho_tiles
                            and 0 <= ny < self.alto_tiles
                            and random.random() < 0.3
                        ):
                            self.mapa[ny][nx] = "AGUA"
                            self.colisiones[ny][nx] = True
                            coords.append((nx, ny))
                    x += dx_dir + random.choice([-1, 0, 1])
                    x = max(0, min(self.ancho_tiles - 1, x))
                    y += 1

            coords = list(set(coords))
            if coords:
                num_puentes = random.randint(2, 3)
                for bx, by in random.sample(coords, min(num_puentes, len(coords))):
                    self.mapa[by][bx] = "PUENTE"
                    self.colisiones[by][bx] = False
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = bx + dx, by + dy
                        if (
                            0 <= nx < self.ancho_tiles
                            and 0 <= ny < self.alto_tiles
                            and self.mapa[ny][nx] == "AGUA"
                        ):
                            self.mapa[ny][nx] = "PUENTE"
                            self.colisiones[ny][nx] = False

    # ------------------------------------------------------------------
    # Representación
    # ------------------------------------------------------------------
    def _color_tile(self, bloque, x, y):
        """Devuelve un color con variaciones oscuras para cada bloque."""
        rnd = random.Random(x * 1000 + y * 100 + ord(bloque[0]))
        if bloque == "SUELO":
            return const.COLOR_SUELO
        elif bloque == "PARED":
            base = (40, 40, 110)
            return tuple(_clamp(base[i] + rnd.randint(-20, 20)) for i in range(3))
        elif bloque == "AGUA":
            base = (20, 70, 160)
            return tuple(_clamp(base[i] + rnd.randint(-15, 15)) for i in range(3))
        elif bloque == "PUENTE":
            base = (160, 100, 40)
            return tuple(_clamp(base[i] + rnd.randint(-15, 15)) for i in range(3))
        elif bloque == "BOSQUE":
            base = (20, 100, 20)
            return tuple(_clamp(base[i] + rnd.randint(-15, 15)) for i in range(3))
        else:  # HUECO
            base = (70, 20, 90)
            return tuple(_clamp(base[i] + rnd.randint(-20, 20)) for i in range(3))

    def dibujar(self, surface, cam_x=0, cam_y=0):
        for y, fila in enumerate(self.mapa):
            for x, bloque in enumerate(fila):
                pos = (
                    x * const.TAM_CELDA + cam_x,
                    const.ALTO_PANEL + y * const.TAM_CELDA + cam_y,
                )
                color = self._color_tile(bloque, x, y)
                pygame.draw.rect(surface, color, (*pos, const.TAM_CELDA, const.TAM_CELDA))

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def posicion_inicial(self):
        """Devuelve la primera celda de suelo disponible."""
        for y, fila in enumerate(self.mapa):
            for x, bloque in enumerate(fila):
                if bloque == "SUELO":
                    return x * const.TAM_CELDA, const.ALTO_PANEL + y * const.TAM_CELDA
        return 0, const.ALTO_PANEL

    def es_colision(self, x, y):
        """Indica si la celda dada no es transitable."""
        if 0 <= x < self.ancho_tiles and 0 <= y < self.alto_tiles:
            return self.colisiones[y][x]
        return True

    def calcular_camino(self, origen, destino):
        """Calcula un camino entre dos puntos usando el algoritmo A*.

        Los puntos se especifican como tuplas ``(x, y)`` en coordenadas de
        tiles. Si no existe un camino válido, devuelve ``None``.
        """

        from heapq import heappop, heappush

        if self.es_colision(*origen) or self.es_colision(*destino):
            return None

        def heuristica(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        abiertos = []
        heappush(abiertos, (0, origen))
        came_from = {}
        g_score = {origen: 0}

        while abiertos:
            _, actual = heappop(abiertos)
            if actual == destino:
                camino = [actual]
                while actual in came_from:
                    actual = came_from[actual]
                    camino.append(actual)
                camino.reverse()
                self.rutas.append(camino)
                return camino

            x, y = actual
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < self.ancho_tiles
                    and 0 <= ny < self.alto_tiles
                    and not self.colisiones[ny][nx]
                ):
                    vecino = (nx, ny)
                    tentativo = g_score[actual] + 1
                    if tentativo < g_score.get(vecino, float("inf")):
                        came_from[vecino] = actual
                        g_score[vecino] = tentativo
                        f_score = tentativo + heuristica(vecino, destino)
                        heappush(abiertos, (f_score, vecino))

        return None

    def exportar_json(self, ruta):
        """Guarda el estado del terreno en un archivo JSON."""
        datos = {
            "mapa": self.mapa,
            "colisiones": self.colisiones,
            "rutas": [[list(celda) for celda in ruta] for ruta in self.rutas],
        }
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)

