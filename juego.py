"""Punto de entrada del juego y clase principal."""

import random

import pygame

import constantes as const
from terreno import Terreno
from jugador import Jugador
from ui import Boton, Selector, dibujar_panel
from batalla.campo import CampoBatalla
from batalla.facciones import EjercitoMagia, EjercitoAngeles, EjercitoDemonios


class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((const.ANCHO, const.ALTO), pygame.RESIZABLE)
        pygame.display.set_caption("Generador de Terreno 2D")
        self.reloj = pygame.time.Clock()

        self.ancho_tiles = const.ANCHO // const.TAM_CELDA
        self.alto_tiles = self.ancho_tiles
        self.densidad = 0.1
        self.densidad_bosque = 0.1
        self.num_rios = 1

        self.terreno = Terreno(self.ancho_tiles, self.alto_tiles, self.densidad, self.densidad_bosque, self.num_rios)
        px, py = self.terreno.posicion_inicial()
        self.jugador = Jugador(px, py, tamaño=const.TAM_CELDA - 4)

        self.cam_x = self.cam_y = 0
        self.arrastrando = False
        self.ultimo_mouse = (0, 0)

        y_botones = const.ALTO_PANEL // 2 - 20
        self.botones = [
            Boton((10, y_botones, 40, 40), "-", self.densidad_menos),
            Boton((60, y_botones, 40, 40), "+", self.densidad_mas),
            Boton((140, y_botones, 40, 40), "R-", self.rios_menos),
            Boton((190, y_botones, 40, 40), "R+", self.rios_mas),
            Boton((270, y_botones, 40, 40), "B-", self.densidad_bosque_menos),
            Boton((320, y_botones, 40, 40), "B+", self.densidad_bosque_mas),
            Boton((380, y_botones, 120, 40), "Regenerar", self.regenerar),
            Boton((520, y_botones, 40, 40), "C-", self.tam_celda_menos),
            Boton((570, y_botones, 40, 40), "C+", self.tam_celda_mas),
        ]

        # Selección de facciones y control de batalla
        self.facciones = {
            "Magia": EjercitoMagia,
            "Ángeles": EjercitoAngeles,
            "Demonios": EjercitoDemonios,
        }
        opciones = list(self.facciones.keys())
        self.faccion_a = opciones[0]
        self.faccion_b = opciones[1]
        self.selector_a = Selector((650, y_botones, 120, 40), opciones, self.set_faccion_a, "A: ")
        self.selector_b = Selector((780, y_botones, 120, 40), opciones, self.set_faccion_b, "B: ")
        self.boton_batalla = Boton((910, y_botones, 80, 40), "Batalla", self.iniciar_batalla)
        self.botones.extend([self.selector_a, self.selector_b, self.boton_batalla])

        self.superficie_juego = pygame.Surface((const.ANCHO, const.ALTO))
        self.offset_x = self.offset_y = 0
        self.corriendo = True
        self.simulando = False
        self.campo = None
        self.ejercito_a = None
        self.ejercito_b = None

    # ------------------------------------------------------------------
    # Métodos de utilidades
    # ------------------------------------------------------------------
    def limitar_camara(self):
        min_cam_x = const.ANCHO - self.ancho_tiles * const.TAM_CELDA
        min_cam_y = const.ALTO - (const.ALTO_PANEL + self.alto_tiles * const.TAM_CELDA)
        self.cam_x = min(0, max(min_cam_x, self.cam_x))
        self.cam_y = min(0, max(min_cam_y, self.cam_y))

    def regenerar(self, semilla=None):
        if semilla is not None:
            random.seed(semilla)
        self.terreno.generar()
        self.jugador.rect.topleft = self.terreno.posicion_inicial()

    def densidad_mas(self):
        self.densidad = min(self.densidad + 0.01, 1.0)
        self.terreno.densidad = self.densidad
        self.regenerar()

    def densidad_menos(self):
        self.densidad = max(self.densidad - 0.01, 0.0)
        self.terreno.densidad = self.densidad
        self.regenerar()

    def rios_mas(self):
        self.num_rios = min(self.num_rios + 1, 3)
        self.terreno.num_rios = self.num_rios
        self.regenerar()

    def rios_menos(self):
        self.num_rios = max(self.num_rios - 1, 1)
        self.terreno.num_rios = self.num_rios
        self.regenerar()

    def densidad_bosque_mas(self):
        self.densidad_bosque = min(self.densidad_bosque + 0.01, 1.0)
        self.terreno.densidad_bosque = self.densidad_bosque
        self.regenerar()

    def densidad_bosque_menos(self):
        self.densidad_bosque = max(self.densidad_bosque - 0.01, 0.0)
        self.terreno.densidad_bosque = self.densidad_bosque
        self.regenerar()

    def ajustar_celda(self, delta):
        const.TAM_CELDA = max(5, const.TAM_CELDA + delta)
        self.ancho_tiles = const.ANCHO // const.TAM_CELDA
        self.alto_tiles = self.ancho_tiles
        self.terreno = Terreno(self.ancho_tiles, self.alto_tiles, self.densidad, self.densidad_bosque, self.num_rios)
        px, py = self.terreno.posicion_inicial()
        self.jugador = Jugador(px, py, tamaño=const.TAM_CELDA - 4)
        self.limitar_camara()

    def tam_celda_mas(self):
        self.ajustar_celda(1)

    def tam_celda_menos(self):
        self.ajustar_celda(-1)

    def set_faccion_a(self, nombre):
        self.faccion_a = nombre

    def set_faccion_b(self, nombre):
        self.faccion_b = nombre

    def iniciar_batalla(self):
        self.campo = CampoBatalla(self.terreno)
        self.ejercito_a = self.facciones[self.faccion_a]()
        self.ejercito_b = self.facciones[self.faccion_b]()
        self._colocar_ejercitos()
        self.simulando = True

    def _buscar_posicion(self, desde_derecha=False):
        rango_x = (
            range(self.campo.ancho - 1, -1, -1)
            if desde_derecha
            else range(self.campo.ancho)
        )
        for x in rango_x:
            for y in range(self.campo.alto):
                if self.campo.es_transitable(x, y) and self.campo._grid[y][x] is None:
                    return x, y
        raise ValueError("No hay posiciones disponibles")

    def _colocar_ejercitos(self):
        for unidad in self.ejercito_a.unidades:
            x, y = self._buscar_posicion()
            self.campo.colocar_unidad(unidad, x, y)
        for unidad in self.ejercito_b.unidades:
            x, y = self._buscar_posicion(desde_derecha=True)
            self.campo.colocar_unidad(unidad, x, y)

    def _dibujar_unidades(self):
        for unidad in self.campo.unidades():
            x, y = self.campo.posicion(unidad)
            sx = x * const.TAM_CELDA + self.cam_x
            sy = const.ALTO_PANEL + y * const.TAM_CELDA + self.cam_y
            color = (255, 0, 0) if unidad in self.ejercito_a.unidades else (0, 0, 255)
            pygame.draw.rect(
                self.superficie_juego,
                color,
                (sx, sy, const.TAM_CELDA, const.TAM_CELDA),
            )

    # ------------------------------------------------------------------
    # Bucle principal
    # ------------------------------------------------------------------
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                evento = pygame.event.Event(
                    evento.type,
                    {**evento.dict, "pos": (evento.pos[0] - self.offset_x, evento.pos[1] - self.offset_y)},
                )
            for boton in self.botones:
                boton.manejar_evento(evento)
            if evento.type == pygame.QUIT:
                self.corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    self.regenerar()
                elif evento.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    self.densidad_mas()
                elif evento.key == pygame.K_MINUS:
                    self.densidad_menos()
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 3:
                self.arrastrando = True
                self.ultimo_mouse = evento.pos
            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 3:
                self.arrastrando = False
            elif evento.type == pygame.MOUSEMOTION and self.arrastrando:
                mx, my = evento.pos
                self.cam_x += mx - self.ultimo_mouse[0]
                self.cam_y += my - self.ultimo_mouse[1]
                self.ultimo_mouse = (mx, my)
                self.limitar_camara()
            elif evento.type == pygame.VIDEORESIZE:
                dimension = min(evento.w, evento.h - const.ALTO_PANEL)
                const.ANCHO = dimension
                const.ALTO = const.ALTO_PANEL + dimension
                self.pantalla = pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)
                self.superficie_juego = pygame.Surface((const.ANCHO, const.ALTO))
                self.offset_x = (evento.w - const.ANCHO) // 2
                self.offset_y = (evento.h - const.ALTO) // 2
                self.ancho_tiles = const.ANCHO // const.TAM_CELDA
                self.alto_tiles = self.ancho_tiles
                self.terreno = Terreno(self.ancho_tiles, self.alto_tiles, self.densidad, self.densidad_bosque, self.num_rios)
                self.jugador.rect.topleft = self.terreno.posicion_inicial()
                self.limitar_camara()

    def actualizar(self):
        if self.simulando:
            self.campo.simular_turno(self.ejercito_a, self.ejercito_b)
            if not self.ejercito_a.unidades or not self.ejercito_b.unidades:
                self.simulando = False
        else:
            teclas = pygame.key.get_pressed()
            self.jugador.mover(teclas, self.terreno)

    def dibujar(self):
        self.superficie_juego.fill((0, 0, 0))
        dibujar_panel(self.superficie_juego, self.botones, self.densidad, self.num_rios, self.densidad_bosque)
        self.terreno.dibujar(self.superficie_juego, self.cam_x, self.cam_y)
        if self.simulando and self.campo:
            self._dibujar_unidades()
        else:
            self.jugador.dibujar(self.superficie_juego, self.cam_x, self.cam_y)
        self.pantalla.fill((0, 0, 0))
        self.pantalla.blit(self.superficie_juego, (self.offset_x, self.offset_y))

    def run(self):
        while self.corriendo:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            pygame.display.flip()
            self.reloj.tick(30)
        pygame.quit()


def main():
    Juego().run()


if __name__ == "__main__":
    main()

