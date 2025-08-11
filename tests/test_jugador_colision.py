import types, sys, pathlib, collections

class Rect:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    @property
    def left(self):
        return self.x
    @property
    def right(self):
        return self.x + self.w
    @property
    def top(self):
        return self.y
    @property
    def bottom(self):
        return self.y + self.h
    @property
    def topleft(self):
        return (self.x, self.y)
    def move(self, dx, dy):
        return Rect(self.x + dx, self.y + dy, self.w, self.h)

pygame = types.ModuleType("pygame")
pygame.Rect = Rect
pygame.K_LEFT = 1
pygame.K_RIGHT = 2
pygame.K_UP = 3
pygame.K_DOWN = 4
sys.modules['pygame'] = pygame
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import constantes as const
from jugador import Jugador
from terreno import Terreno

def test_jugador_no_cruza_agua():
    terreno = Terreno(2, 1, densidad=0.0, densidad_bosque=0.0, num_rios=0, semilla=1)
    terreno.mapa[0][1] = "AGUA"
    jugador = Jugador(0, const.ALTO_PANEL, velocidad=const.TAM_CELDA)
    teclas = collections.defaultdict(bool)
    teclas[pygame.K_RIGHT] = True
    jugador.mover(teclas, terreno)
    assert jugador.rect.x == 0
