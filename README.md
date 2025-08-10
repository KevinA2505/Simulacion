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

## Generar terreno desde la línea de comandos

El script `generar_terreno.py` permite crear un mapa sin necesidad de
escribir código adicional. Los parámetros requeridos son el ancho, el alto y
una semilla opcional para la generación:

```bash
python generar_terreno.py 20 15 42
```

El resultado se guarda en `terreno.json` en el directorio actual.
