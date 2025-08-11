"""Módulo que define el comportamiento del jugador."""

import pygame

import constantes as const


class Jugador:
    """Entidad controlada por el usuario dentro del terreno."""

    def __init__(self, x, y, tamaño=const.TAM_CELDA - 4, velocidad=4):
        self.rect = pygame.Rect(x, y, tamaño, tamaño)
        self.velocidad = velocidad
        self.color = (60, 20, 120)

    def _bloque_en(self, px, py, terreno):
        tile_x = int(px // const.TAM_CELDA)
        tile_y = int((py - const.ALTO_PANEL) // const.TAM_CELDA)
        if tile_y < 0:
            return "PARED"
        if 0 <= tile_x < terreno.ancho_tiles and 0 <= tile_y < terreno.alto_tiles:
            return terreno.mapa[tile_y][tile_x]
        return "PARED"

    def _colisiona(self, rect, terreno):
        puntos = [
            rect.topleft,
            (rect.right - 1, rect.top),
            (rect.left, rect.bottom - 1),
            (rect.right - 1, rect.bottom - 1),
        ]
        for px, py in puntos:
            # Evita que el jugador atraviese cualquier bloque considerado
            # no transitable dentro del terreno.
            if self._bloque_en(px, py, terreno) in ("PARED", "HUECO", "AGUA"):
                return True
        return False

    def mover(self, teclas, terreno):
        dx = dy = 0
        if teclas[pygame.K_LEFT]:
            dx -= self.velocidad
        if teclas[pygame.K_RIGHT]:
            dx += self.velocidad
        if teclas[pygame.K_UP]:
            dy -= self.velocidad
        if teclas[pygame.K_DOWN]:
            dy += self.velocidad

        if dx != 0:
            nuevo = self.rect.move(dx, 0)
            if not self._colisiona(nuevo, terreno):
                self.rect = nuevo
        if dy != 0:
            nuevo = self.rect.move(0, dy)
            if not self._colisiona(nuevo, terreno):
                self.rect = nuevo

    def dibujar(self, surface, cam_x=0, cam_y=0):
        pygame.draw.rect(surface, self.color, self.rect.move(cam_x, cam_y))

