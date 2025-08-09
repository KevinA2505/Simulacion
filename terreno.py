import pygame
import random


def _clamp(valor, minimo=0, maximo=255):
    """Mantiene un valor dentro del rango [minimo, maximo]."""
    return max(minimo, min(maximo, valor))

# Configuración básica
ANCHO, ALTO = 800, 600
ALTO_PANEL = 80
TAM_CELDA = 20

# Colores base para cada tipo de terreno. Se utilizan como punto de partida
# para generar variaciones que den un aspecto menos plano al mapa.
COLOR_SUELO   = (90, 180, 90)     # Verde hierba
COLOR_PARED   = (120, 120, 130)   # Piedra
COLOR_HUECO   = (5, 5, 20)        # Vacío oscuro
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
        """Devuelve un color con variaciones y gradientes según la posición."""
        rnd = random.Random(x * 1000 + y * 100 + ord(bloque[0]))
        if bloque == "SUELO":
            # Variar el tono de verde y agregar un gradiente vertical.
            grad = int(40 * y / self.alto_tiles)
            r = _clamp(COLOR_SUELO[0] + rnd.randint(-20, 20))
            g = _clamp(COLOR_SUELO[1] + grad + rnd.randint(-30, 30))
            b = _clamp(COLOR_SUELO[2] + rnd.randint(-20, 20))
            return (r, g, b)
        elif bloque == "PARED":
            # La piedra se oscurece ligeramente con la profundidad.
            brillo = int(30 * (self.alto_tiles - y) / self.alto_tiles)
            offset = rnd.randint(-15, 15) + brillo
            return tuple(_clamp(c + offset) for c in COLOR_PARED)
        else:  # HUECO
            # Tonos azulados que se aclaran levemente en profundidad.
            azul = int(50 * y / self.alto_tiles)
            r = _clamp(COLOR_HUECO[0] + rnd.randint(-10, 10))
            g = _clamp(COLOR_HUECO[1] + rnd.randint(-10, 10))
            b = _clamp(COLOR_HUECO[2] + azul + rnd.randint(-10, 10))
            return (r, g, b)

    def dibujar(self, surface):
        for y, fila in enumerate(self.mapa):
            for x, bloque in enumerate(fila):
                pos = (x * TAM_CELDA, ALTO_PANEL + y * TAM_CELDA)
                color = self._color_tile(bloque, x, y)
                pygame.draw.rect(surface, color, (*pos, TAM_CELDA, TAM_CELDA))


def dibujar_panel(surface, densidad):
    pygame.draw.rect(surface, COLOR_PANEL, (0, 0, ANCHO, ALTO_PANEL))
    fuente = pygame.font.SysFont(None, 30)
    texto = fuente.render(
        f"[Panel] densidad: {densidad:.2f}  |  +/- para ajustar, R para regenerar",
        True, COLOR_TEXTO
    )
    surface.blit(texto, (10, 25))


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Generador de Terreno 2D")
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont(None, 24)  # Carga una fuente para el panel

    ancho_tiles = ANCHO // TAM_CELDA
    alto_tiles = (ALTO - ALTO_PANEL) // TAM_CELDA
    densidad = 0.1

    terreno = Terreno(ancho_tiles, alto_tiles, densidad)

    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:          # Regenerar
                    terreno.generar()
                elif evento.key == pygame.K_PLUS or evento.key == pygame.K_EQUALS:
                    densidad = min(densidad + 0.05, 1.0)
                    terreno.densidad = densidad
                    terreno.generar()
                elif evento.key == pygame.K_MINUS:
                    densidad = max(densidad - 0.05, 0.0)
                    terreno.densidad = densidad
                    terreno.generar()

        pantalla.fill((0, 0, 0))
        dibujar_panel(pantalla, densidad)
        terreno.dibujar(pantalla)

        pygame.display.flip()
        reloj.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
