"""Definiciones de unidades de combate."""


class Unidad:
    """Representa una unidad de combate básica."""

    def __init__(self, salud, ataque, defensa, velocidad, alcance):
        self.salud = salud
        self.ataque = ataque
        self.defensa = defensa
        self.velocidad = velocidad
        self.alcance = alcance

    def recibir_daño(self, daño):
        """Aplica daño a la unidad considerando su defensa."""
        daño_efectivo = max(daño - self.defensa, 0)
        self.salud -= daño_efectivo
        return daño_efectivo

    def esta_viva(self):
        """Indica si la unidad sigue en combate."""
        return self.salud > 0
