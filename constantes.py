"""Constantes globales para la simulación del terreno.

Se mantienen en un módulo separado para permitir que otras partes del
programa las reutilicen y modifiquen fácilmente.
"""

# Dimensiones iniciales de la ventana y del panel superior
ANCHO = 1000
ALTO_PANEL = 120
ALTO = ALTO_PANEL + ANCHO

# Tamaño de cada celda de terreno (puede modificarse en tiempo de ejecución)
TAM_CELDA = int(20 * 1.15)

# Factor de escala para el tamaño inicial del mapa
FACTOR_MAPA = 2

# Colores utilizados en distintos elementos del juego
COLOR_SUELO = (50, 50, 50)
COLOR_PANEL = (200, 200, 200)
COLOR_TEXTO = (20, 20, 20)

