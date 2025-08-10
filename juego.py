"""Punto de entrada del juego y clase principal."""

import random

import pygame

import constantes as const
from terreno import Terreno
from jugador import Jugador
from ui import Boton, Selector, dibujar_panel, mostrar_tooltip, dibujar_minimapa
from batalla.campo import CampoBatalla
from batalla.facciones import EjercitoMagia, EjercitoAngeles, EjercitoDemonios
from batalla.carga import leer_ejercito


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
        opciones = list(self.facciones.keys()) + ["Archivo"]
        self.faccion_a = opciones[0]
        self.faccion_b = opciones[1]
        self.ruta_a = None
        self.ruta_b = None
        self.selector_a = Selector((650, y_botones, 120, 40), opciones, self.set_faccion_a, "A: ")
        self.selector_b = Selector((780, y_botones, 120, 40), opciones, self.set_faccion_b, "B: ")
        self.boton_batalla = Boton((910, y_botones, 80, 40), "Batalla", self.iniciar_batalla)
        self.botones.extend([self.selector_a, self.selector_b, self.boton_batalla])

        self.superficie_juego = pygame.Surface((const.ANCHO, const.ALTO))
        self.offset_x = self.offset_y = 0
        self.corriendo = True
        self.estado = "exploracion"
        self.campo = None
        self.ejercito_a = None
        self.ejercito_b = None
        self.simulando = False
        # Acciones pendientes devueltas por ``CampoBatalla.simular_turno``
        self.acciones: list[dict] = []
        self.pausado = False
        self.avanzar_un_turno = False

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
        if nombre == "Archivo":
            self.ruta_a = input("Ruta del archivo para el ejército A: ").strip()
        self.faccion_a = nombre

    def set_faccion_b(self, nombre):
        if nombre == "Archivo":
            self.ruta_b = input("Ruta del archivo para el ejército B: ").strip()
        self.faccion_b = nombre

    def iniciar_batalla(self):
        self.campo = CampoBatalla(self.terreno)
        if self.faccion_a == "Archivo" and self.ruta_a:
            self.ejercito_a = leer_ejercito(self.ruta_a)
        else:
            self.ejercito_a = self.facciones[self.faccion_a]()
        if self.faccion_b == "Archivo" and self.ruta_b:
            self.ejercito_b = leer_ejercito(self.ruta_b)
        else:
            self.ejercito_b = self.facciones[self.faccion_b]()
        self._colocar_ejercitos()
        # Calcular rutas iniciales entre los ejércitos (referencia de preparación)
        if self.ejercito_a.unidades and self.ejercito_b.unidades:
            pos_a = self.campo.posicion(self.ejercito_a.unidades[0])
            pos_b = self.campo.posicion(self.ejercito_b.unidades[0])
            self.terreno.calcular_camino(pos_a, pos_b, "A")
            self.terreno.calcular_camino(pos_b, pos_a, "B")

        # Preparar combate y mostrar cuenta atrás antes de simular
        self.estado = "combate"
        self.simulando = False
        self.pausado = False
        self.avanzar_un_turno = False
        self.boton_batalla.texto = "Batalla"
        self.boton_batalla.accion = self.iniciar_batalla

        # Captura de pantalla previa al inicio
        self.dibujar()
        pygame.image.save(self.superficie_juego, "captura_inicial.png")

        fuente = pygame.font.Font(None, 120)
        centro = (
            const.ANCHO // 2,
            const.ALTO_PANEL + (const.ALTO - const.ALTO_PANEL) // 2,
        )
        for contador in range(3, 0, -1):
            pygame.event.get()  # Limpiar eventos para bloquear la entrada
            self.dibujar()
            texto = fuente.render(str(contador), True, (255, 255, 255))
            rect = texto.get_rect(center=centro)
            self.superficie_juego.blit(texto, rect)
            self.pantalla.fill((0, 0, 0))
            self.pantalla.blit(self.superficie_juego, (self.offset_x, self.offset_y))
            pygame.display.flip()
            pygame.time.wait(1000)

        pygame.event.get()
        self.simulando = True

    def comenzar_combate(self):
        """Método obsoleto mantenido por compatibilidad."""
        self.iniciar_batalla()

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
        mx, my = pygame.mouse.get_pos()
        mx -= self.offset_x
        my -= self.offset_y
        unidad_hover = None
        for unidad in self.campo.unidades():
            x, y = self.campo.posicion(unidad)
            sx = x * const.TAM_CELDA + self.cam_x
            sy = const.ALTO_PANEL + y * const.TAM_CELDA + self.cam_y
            rect = pygame.Rect(sx, sy, const.TAM_CELDA, const.TAM_CELDA)
            color = (255, 0, 0) if unidad in self.ejercito_a.unidades else (0, 0, 255)
            pygame.draw.rect(self.superficie_juego, color, rect)
            # Barra de salud sobre la unidad
            salud_max = self.campo._salud_max.get(unidad, unidad.salud)
            ancho_barra = const.TAM_CELDA
            alto_barra = 4
            bx = sx
            by = sy - alto_barra - 2
            fondo = pygame.Rect(bx, by, ancho_barra, alto_barra)
            pygame.draw.rect(self.superficie_juego, (255, 0, 0), fondo)
            if salud_max > 0:
                ancho_salud = int(ancho_barra * max(unidad.salud, 0) / salud_max)
            else:
                ancho_salud = 0
            barra = pygame.Rect(bx, by, ancho_salud, alto_barra)
            pygame.draw.rect(self.superficie_juego, (0, 255, 0), barra)
            if rect.collidepoint((mx, my)):
                unidad_hover = unidad
        if unidad_hover:
            mostrar_tooltip(self.superficie_juego, unidad_hover, (mx, my))

    # ------------------------------------------------------------------
    # Animaciones de acciones de combate
    # ------------------------------------------------------------------
    def reproducir_accion(self, accion: dict) -> None:
        """Muestra una animación simple para la acción indicada.

        Las animaciones son deliberadamente sencillas: líneas que unen al
        actor con el objetivo o un pequeño punto que se desplaza al moverse
        una unidad. Se realiza un breve retardo para que el jugador pueda
        percibir la acción antes de continuar con la siguiente.
        """

        tipo = accion.get("tipo")
        ox, oy = accion.get("origen", (0, 0))
        dx, dy = accion.get("destino", (0, 0))

        inicio = (
            ox * const.TAM_CELDA + self.cam_x + const.TAM_CELDA // 2,
            const.ALTO_PANEL + oy * const.TAM_CELDA + self.cam_y + const.TAM_CELDA // 2,
        )
        fin = (
            dx * const.TAM_CELDA + self.cam_x + const.TAM_CELDA // 2,
            const.ALTO_PANEL + dy * const.TAM_CELDA + self.cam_y + const.TAM_CELDA // 2,
        )

        color = (255, 255, 0)
        if tipo == "atacar":
            color = (255, 0, 0)
        elif tipo == "curar":
            color = (0, 255, 0)

        pasos = 5
        for i in range(pasos):
            self.dibujar()
            if tipo == "mover":
                px = inicio[0] + (fin[0] - inicio[0]) * (i + 1) / pasos
                py = inicio[1] + (fin[1] - inicio[1]) * (i + 1) / pasos
                pygame.draw.circle(
                    self.superficie_juego, color, (int(px), int(py)), const.TAM_CELDA // 3
                )
            else:
                pygame.draw.line(self.superficie_juego, color, inicio, fin, 3)
            self.pantalla.blit(self.superficie_juego, (self.offset_x, self.offset_y))
            pygame.display.flip()
            pygame.time.wait(40)

    def mostrar_preparacion(self):
        self.terreno.dibujar(self.superficie_juego, self.cam_x, self.cam_y)
        posiciones = []
        if self.campo:
            self._dibujar_unidades()
            for unidad in self.campo.unidades():
                x, y = self.campo.posicion(unidad)
                color = (
                    (255, 0, 0)
                    if unidad in self.ejercito_a.unidades
                    else (0, 0, 255)
                )
                posiciones.append((x, y, color))
        # Resaltar las rutas calculadas para cada ejército
        colores = {"A": (255, 0, 0), "B": (0, 0, 255)}
        for ejercito, rutas in self.terreno.rutas.items():
            color = colores.get(ejercito, (255, 255, 0))
            for ruta in rutas:
                for x, y in ruta:
                    sx = x * const.TAM_CELDA + self.cam_x
                    sy = const.ALTO_PANEL + y * const.TAM_CELDA + self.cam_y
                    rect = pygame.Rect(sx, sy, const.TAM_CELDA, const.TAM_CELDA)
                    pygame.draw.rect(self.superficie_juego, color, rect, 2)
        dibujar_minimapa(self.superficie_juego, self.terreno, posiciones)

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
                elif evento.key == pygame.K_p and self.estado == "combate":
                    self.pausado = not self.pausado
                elif evento.key == pygame.K_n and self.estado == "combate":
                    self.avanzar_un_turno = True
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
        if self.estado == "combate":
            if self.simulando:
                if self.acciones:
                    if not self.pausado or self.avanzar_un_turno:
                        accion = self.acciones.pop(0)
                        self.reproducir_accion(accion)
                        if not self.acciones and self.avanzar_un_turno and self.pausado:
                            self.avanzar_un_turno = False
                elif not self.pausado or self.avanzar_un_turno:
                    self.acciones = self.campo.simular_turno(
                        self.ejercito_a, self.ejercito_b
                    )
                    if not self.ejercito_a.unidades or not self.ejercito_b.unidades:
                        self.estado = "exploracion"
                        self.boton_batalla.texto = "Batalla"
                        self.boton_batalla.accion = self.iniciar_batalla
                        self.simulando = False
        elif self.estado == "exploracion":
            teclas = pygame.key.get_pressed()
            self.jugador.mover(teclas, self.terreno)

    def dibujar(self):
        self.superficie_juego.fill((0, 0, 0))
        dibujar_panel(self.superficie_juego, self.botones, self.densidad, self.num_rios, self.densidad_bosque)
        if self.estado == "preparacion":
            self.mostrar_preparacion()
        else:
            self.terreno.dibujar(self.superficie_juego, self.cam_x, self.cam_y)
            if self.estado == "combate" and self.campo:
                posiciones = []
                self._dibujar_unidades()
                for unidad in self.campo.unidades():
                    x, y = self.campo.posicion(unidad)
                    color = (
                        (255, 0, 0)
                        if unidad in self.ejercito_a.unidades
                        else (0, 0, 255)
                    )
                    posiciones.append((x, y, color))
                dibujar_minimapa(self.superficie_juego, self.terreno, posiciones)
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

