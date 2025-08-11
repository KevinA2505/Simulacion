"""Elementos de interfaz de usuario para el juego."""

import pygame

import constantes as const


class Boton:
    def __init__(self, rect, texto, accion):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.accion = accion

    def manejar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                self.accion()

    def dibujar(self, surface):
        pygame.draw.rect(surface, (230, 230, 230), self.rect)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2)
        fuente = pygame.font.SysFont(None, 24)
        texto = fuente.render(self.texto, True, const.COLOR_TEXTO)
        surface.blit(texto, texto.get_rect(center=self.rect.center))


class Selector(Boton):
    """Botón que rota entre varias opciones de texto."""

    def __init__(self, rect, opciones, callback, prefijo=""):
        self.opciones = opciones
        self.indice = 0
        self.callback = callback
        self.prefijo = prefijo
        super().__init__(rect, self._texto_actual(), self._cambiar)

    def _texto_actual(self):
        return f"{self.prefijo}{self.opciones[self.indice]}"

    def _cambiar(self):
        self.indice = (self.indice + 1) % len(self.opciones)
        self.texto = self._texto_actual()
        self.callback(self.opciones[self.indice])


def dibujar_panel(surface, botones, densidad, num_rios, densidad_bosque):
    pygame.draw.rect(surface, const.COLOR_PANEL, (0, 0, const.ANCHO, const.ALTO_PANEL))
    for boton in botones:
        boton.dibujar(surface)
    fuente = pygame.font.SysFont(None, 24)
    texto = fuente.render(f"Obstáculos: {densidad:.2f}", True, const.COLOR_TEXTO)
    surface.blit(texto, (10, const.ALTO_PANEL - 30))
    texto = fuente.render(f"Ríos: {num_rios}", True, const.COLOR_TEXTO)
    surface.blit(texto, (200, const.ALTO_PANEL - 30))
    texto = fuente.render(f"Bosque: {densidad_bosque:.2f}", True, const.COLOR_TEXTO)
    surface.blit(texto, (360, const.ALTO_PANEL - 30))
    texto = fuente.render(f"Celda: {const.TAM_CELDA}", True, const.COLOR_TEXTO)
    surface.blit(texto, (520, const.ALTO_PANEL - 30))


def mostrar_tooltip(surface, unidad, pos):
    """Renderiza un cuadro con información básica de ``unidad``.

    Parameters
    ----------
    surface:
        Superficie sobre la que se dibuja el tooltip.
    unidad:
        Objeto que posee atributos ``salud``, ``ataque``, ``defensa``,
        ``velocidad`` y ``alcance``.
    pos:
        Tupla ``(x, y)`` indicando la posición donde mostrar el tooltip.
    """

    fuente = pygame.font.SysFont(None, 20)
    lineas = [
        f"Salud: {unidad.salud}",
        f"Ataque: {unidad.ataque}",
        f"Defensa: {unidad.defensa}",
        f"Velocidad: {unidad.velocidad}",
        f"Alcance: {unidad.alcance}",
    ]
    textos = [fuente.render(t, True, const.COLOR_TEXTO) for t in lineas]
    ancho = max(t.get_width() for t in textos) + 10
    alto = sum(t.get_height() for t in textos) + 10
    x, y = pos
    x = min(x + 10, surface.get_width() - ancho)
    y = min(y + 10, surface.get_height() - alto)
    rect = pygame.Rect(x, y, ancho, alto)
    pygame.draw.rect(surface, (230, 230, 230), rect)
    pygame.draw.rect(surface, (50, 50, 50), rect, 1)
    offset_y = y + 5
    for texto in textos:
        surface.blit(texto, (x + 5, offset_y))
        offset_y += texto.get_height()


