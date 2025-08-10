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


class Infanteria(Unidad):
    """Unidad equilibrada de combate cuerpo a cuerpo."""

    def __init__(self):
        super().__init__(salud=100, ataque=10, defensa=5, velocidad=4, alcance=1)

    def fortificar(self):
        """Aumenta la defensa temporalmente."""
        self.defensa += 2


class Arqueria(Unidad):
    """Unidad especializada en ataques a distancia."""

    def __init__(self):
        super().__init__(salud=80, ataque=12, defensa=3, velocidad=4, alcance=5)

    def disparo_preciso(self, objetivo: Unidad):
        """Ataque que ignora la defensa del objetivo."""
        objetivo.salud -= self.ataque
        return self.ataque


class Caballeria(Unidad):
    """Unidad móvil con gran capacidad ofensiva."""

    def __init__(self):
        super().__init__(salud=120, ataque=14, defensa=4, velocidad=8, alcance=1)

    def cargar(self, objetivo: Unidad):
        """Ataque de carga con daño aumentado."""
        daño = self.ataque * 2
        return objetivo.recibir_daño(daño)


class Defensa(Unidad):
    """Unidad enfocada en proteger a sus aliados."""

    def __init__(self):
        super().__init__(salud=150, ataque=6, defensa=12, velocidad=3, alcance=1)

    def proteger(self, aliado: Unidad):
        """Incrementa la defensa de un aliado."""
        aliado.defensa += 3


class Soporte(Unidad):
    """Unidad encargada de asistir y curar a sus aliados."""

    def __init__(self):
        super().__init__(salud=70, ataque=4, defensa=3, velocidad=5, alcance=1)

    def curar(self, aliado: Unidad):
        """Restaura salud a un aliado."""
        curacion = 10
        aliado.salud += curacion
        return curacion
