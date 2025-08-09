import pygame
import random


def _clamp(valor, minimo=0, maximo=255):
    """Mantiene un valor dentro del rango [minimo, maximo]."""
    return max(minimo, min(maximo, valor))

# Configuración básica
ANCHO = 600                     # Área de terreno cuadrada
ALTO_PANEL = 120
ALTO = ALTO_PANEL + ANCHO       # Mantiene el terreno como un cuadrado
TAM_CELDA = 20

# Colores base
COLOR_SUELO   = (50, 50, 50)     # Gris oscuro y plano
COLOR_PANEL   = (200, 200, 200)
COLOR_TEXTO   = (20, 20, 20)

class Terreno:
    def __init__(self, ancho_tiles, alto_tiles, densidad=0.1):
        self.ancho_tiles = ancho_tiles
        self.alto_tiles = alto_tiles
        self.densidad = densidad
        self.mapa = []
        self.generar()

    def generar(self):
        self.mapa = []
        for _ in range(self.alto_tiles):
            fila = []
            for _ in range(self.ancho_tiles):
                rnd = random.random()
                if rnd < self.densidad:
                    # Obstáculo: pared o hueco
                    fila.append(random.choice(["PARED", "HUECO"]))
                else:
                    fila.append("SUELO")
            self.mapa.append(fila)

    def _color_tile(self, bloque, x, y):
        """Devuelve un color con variaciones oscuras para cada bloque."""
        rnd = random.Random(x * 1000 + y * 100 + ord(bloque[0]))
        if bloque == "SUELO":
            return COLOR_SUELO
        elif bloque == "PARED":
            base = (40, 40, 110)  # Azul oscuro
            return tuple(_clamp(base[i] + rnd.randint(-20, 20)) for i in range(3))
        else:  # HUECO
            base = (70, 20, 90)  # Morado oscuro
            return tuple(_clamp(base[i] + rnd.randint(-20, 20)) for i in range(3))

    def dibujar(self, surface, cam_x=0, cam_y=0):
        for y, fila in enumerate(self.mapa):
            for x, bloque in enumerate(fila):
                pos = (
                    x * TAM_CELDA + cam_x,
                    ALTO_PANEL + y * TAM_CELDA + cam_y,
                )
                color = self._color_tile(bloque, x, y)
                pygame.draw.rect(surface, color, (*pos, TAM_CELDA, TAM_CELDA))


class Jugador:
    def __init__(self, x, y, tamaño=TAM_CELDA - 4, velocidad=4):
        self.rect = pygame.Rect(x, y, tamaño, tamaño)
        self.velocidad = velocidad
        self.color = (60, 20, 120)

    def _bloque_en(self, px, py, terreno):
        tile_x = int(px // TAM_CELDA)
        tile_y = int((py - ALTO_PANEL) // TAM_CELDA)
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
            if self._bloque_en(px, py, terreno) in ("PARED", "HUECO"):
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
        texto = fuente.render(self.texto, True, COLOR_TEXTO)
        surface.blit(texto, texto.get_rect(center=self.rect.center))


def dibujar_panel(surface, botones, densidad):
    pygame.draw.rect(surface, COLOR_PANEL, (0, 0, ANCHO, ALTO_PANEL))
    for boton in botones:
        boton.dibujar(surface)
    fuente = pygame.font.SysFont(None, 24)
    texto = fuente.render(f"Densidad: {densidad:.2f}", True, COLOR_TEXTO)
    surface.blit(texto, (10, ALTO_PANEL - 30))


def posicion_inicial(terreno):
    for y, fila in enumerate(terreno.mapa):
        for x, bloque in enumerate(fila):
            if bloque == "SUELO":
                return x * TAM_CELDA, ALTO_PANEL + y * TAM_CELDA
    return 0, ALTO_PANEL


def main():
    global ANCHO, ALTO
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
    pygame.display.set_caption("Generador de Terreno 2D")
    reloj = pygame.time.Clock()

    ancho_tiles = ANCHO // TAM_CELDA
    alto_tiles = ancho_tiles
    densidad = 0.1

    terreno = Terreno(ancho_tiles, alto_tiles, densidad)
    px, py = posicion_inicial(terreno)
    jugador = Jugador(px, py)

    cam_x = cam_y = 0
    arrastrando = False
    ultimo_mouse = (0, 0)

    def limitar_camara():
        nonlocal cam_x, cam_y
        min_cam_x = ANCHO - ancho_tiles * TAM_CELDA
        min_cam_y = ALTO - (ALTO_PANEL + alto_tiles * TAM_CELDA)
        cam_x = min(0, max(min_cam_x, cam_x))
        cam_y = min(0, max(min_cam_y, cam_y))

    def regenerar():
        terreno.generar()
        jugador.rect.topleft = posicion_inicial(terreno)

    def densidad_mas():
        nonlocal densidad
        densidad = min(densidad + 0.05, 1.0)
        terreno.densidad = densidad
        regenerar()

    def densidad_menos():
        nonlocal densidad
        densidad = max(densidad - 0.05, 0.0)
        terreno.densidad = densidad
        regenerar()

    y_botones = ALTO_PANEL // 2 - 20
    botones = [
        Boton((10, y_botones, 40, 40), "-", densidad_menos),
        Boton((60, y_botones, 40, 40), "+", densidad_mas),
        Boton((120, y_botones, 120, 40), "Regenerar", regenerar),
    ]

    superficie_juego = pygame.Surface((ANCHO, ALTO))
    offset_x = offset_y = 0

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                evento = pygame.event.Event(evento.type, {**evento.dict, "pos": (evento.pos[0] - offset_x, evento.pos[1] - offset_y)})
            for boton in botones:
                boton.manejar_evento(evento)
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    regenerar()
                elif evento.key == pygame.K_PLUS or evento.key == pygame.K_EQUALS:
                    densidad_mas()
                elif evento.key == pygame.K_MINUS:
                    densidad_menos()
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 3:
                arrastrando = True
                ultimo_mouse = evento.pos
            elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 3:
                arrastrando = False
            elif evento.type == pygame.MOUSEMOTION and arrastrando:
                mx, my = evento.pos
                dx = mx - ultimo_mouse[0]
                dy = my - ultimo_mouse[1]
                cam_x += dx
                cam_y += dy
                ultimo_mouse = (mx, my)
                limitar_camara()
            elif evento.type == pygame.VIDEORESIZE:
                dimension = min(evento.w, evento.h - ALTO_PANEL)
                ANCHO = dimension
                ALTO = ALTO_PANEL + dimension
                pantalla = pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)
                superficie_juego = pygame.Surface((ANCHO, ALTO))
                offset_x = (evento.w - ANCHO) // 2
                offset_y = (evento.h - ALTO) // 2
                ancho_tiles = ANCHO // TAM_CELDA
                alto_tiles = ancho_tiles
                terreno = Terreno(ancho_tiles, alto_tiles, densidad)
                jugador.rect.topleft = posicion_inicial(terreno)
                limitar_camara()

        teclas = pygame.key.get_pressed()
        jugador.mover(teclas, terreno)

        superficie_juego.fill((0, 0, 0))
        dibujar_panel(superficie_juego, botones, densidad)
        terreno.dibujar(superficie_juego, cam_x, cam_y)
        jugador.dibujar(superficie_juego, cam_x, cam_y)

        pantalla.fill((0, 0, 0))
        pantalla.blit(superficie_juego, (offset_x, offset_y))

        pygame.display.flip()
        reloj.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
