# Simulación

## Exportar datos del terreno

La clase `Terreno` permite guardar el estado del mapa y los caminos
calculados en un archivo JSON:

```python
from terreno import Terreno

terreno = Terreno(10, 10)
camino = terreno.calcular_camino((0, 0), (5, 5))
terreno.exportar_json("terreno.json")
```

El archivo generado contiene el mapa, la matriz de colisiones y una lista
de todas las rutas calculadas, de modo que pueda ser reutilizado por otros
módulos.

## Exportar datos del ejército

La clase `Ejercito` permite guardar la información de sus unidades en un
archivo JSON:

```python
from batalla.ejercito import crear_ejercito

config = [{"tipo": "Infanteria", "cantidad": 2}]
ejercito = crear_ejercito(config)
ejercito.exportar_json("ejercito.json")
```

El archivo generado contiene una lista de unidades con sus atributos básicos
e identificadores únicos.

## Generar terreno y ejército desde la línea de comandos

El script `generar_terreno.py` permite crear un mapa y un ejército de prueba
sin necesidad de escribir código adicional. Los parámetros requeridos son el
ancho, el alto y una semilla opcional para la generación:

```bash
python generar_terreno.py 20 15 42
```

El resultado se guarda en `terreno.json` y `ejercito.json` en el directorio
actual.

## Captura de pantalla inicial de batalla

Al confirmar una batalla desde `juego.py`, se guarda automáticamente la
superficie actual en una imagen llamada `captura_inicial.png` ubicada en el
directorio donde se ejecuta el juego.

## Identificadores de unidades

Cada instancia de ``Unidad`` y sus subclases genera automáticamente un
identificador único. Puede accederse a este valor desde el resto del
código mediante el atributo ``id``:

```python
from batalla.unidad import Infanteria

soldado = Infanteria()
print(soldado.id)
```

Este identificador es útil para referenciar unidades específicas durante
la simulación o el registro de eventos.
