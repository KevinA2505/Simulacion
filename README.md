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
