"""Definiciones de unidades de combate."""

from uuid import uuid4

from .acciones import (
    AccionAtaque,
    AccionCurar,
    AccionFortificar,
    AccionDisparoPreciso,
    AccionCargar,
    AccionProteger,
)


class Unidad:
    """Representa una unidad de combate básica.

    Cada unidad posee un identificador único accesible a través del
    atributo :pyattr:`id`, útil para referenciarla desde otras partes del
    programa.
    """

    def __init__(self, salud, ataque, defensa, velocidad, alcance, id=None):
        self.id = id or uuid4()
        self.salud = salud
        self.ataque = ataque
        self.defensa = defensa
        self.velocidad = velocidad
        self.alcance = alcance
        # Acciones disponibles por la unidad. Por defecto todas pueden atacar.
        self.acciones = {"atacar": AccionAtaque(self)}

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

    def __init__(self, id=None):
        super().__init__(
            salud=100, ataque=10, defensa=5, velocidad=4, alcance=1, id=id
        )
        self.acciones["fortificar"] = AccionFortificar(self)


class Arqueria(Unidad):
    """Unidad especializada en ataques a distancia."""

    def __init__(self, id=None):
        super().__init__(
            salud=80, ataque=12, defensa=3, velocidad=4, alcance=5, id=id
        )
        self.acciones["disparo_preciso"] = AccionDisparoPreciso(self)


class Caballeria(Unidad):
    """Unidad móvil con gran capacidad ofensiva."""

    def __init__(self, id=None):
        super().__init__(
            salud=120, ataque=14, defensa=4, velocidad=8, alcance=1, id=id
        )
        self.acciones["cargar"] = AccionCargar(self)


class Defensa(Unidad):
    """Unidad enfocada en proteger a sus aliados."""

    def __init__(self, id=None):
        super().__init__(
            salud=150, ataque=6, defensa=12, velocidad=3, alcance=1, id=id
        )
        self.acciones["proteger"] = AccionProteger(self)


class Soporte(Unidad):
    """Unidad encargada de asistir y curar a sus aliados."""

    def __init__(self, id=None):
        super().__init__(
            salud=70, ataque=4, defensa=3, velocidad=5, alcance=1, id=id
        )
        self.acciones["curar"] = AccionCurar(self)
