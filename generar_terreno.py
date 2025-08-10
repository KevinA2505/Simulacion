"""Genera un terreno desde la línea de comandos."""

import argparse
from terreno import Terreno

def main():
    parser = argparse.ArgumentParser(
        description="Genera un terreno y lo exporta a un archivo JSON"
    )
    parser.add_argument("ancho", type=int, help="Ancho del terreno en tiles")
    parser.add_argument("alto", type=int, help="Alto del terreno en tiles")
    parser.add_argument(
        "semilla", type=int, nargs="?", default=None, help="Semilla para la generación"
    )
    args = parser.parse_args()

    terreno = Terreno(args.ancho, args.alto, semilla=args.semilla)
    terreno.exportar_json("terreno.json")
    print("Terreno exportado a terreno.json")


if __name__ == "__main__":
    main()
