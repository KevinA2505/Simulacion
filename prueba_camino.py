from terreno import Terreno


def main():
    # Mapa simple sin obstáculos para probar el cálculo de camino
    t = Terreno(10, 10, densidad=0.0, densidad_bosque=0.0, num_rios=0, semilla=1)
    origen = (0, 0)
    destino = (5, 5)
    camino = t.calcular_camino(origen, destino)
    print("Camino encontrado:", camino)


if __name__ == "__main__":
    main()
