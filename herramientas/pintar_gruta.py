"""LO DE LA GRUTA DE LAS RAÍCES, pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_gruta.py

Genera (en arte/mundos/raiz/gruta/):
  semilla_dormida.png   3 × 24×26   una semilla grande dormida en su nicho de raíces, que respira: brilla verde por
                                    dentro (0 apagándose, 1 media, 2 encendida)
  huella.png            2 × 8×8     una huella de Mauti, de luz lila (dos pies)
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ, rampa  # noqa: E402
from pintar_pasarelas import tira, CONTORNO  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "gruta")
LUZ = (-0.6, -0.7, 0.5)


def semilla_dormida(k):
    W, H = 24, 26
    lz = Lienzo(W, H, s=8, semilla=501 + k)
    lz.pintar(lz.desenfocar(lz.elipse(12, 23, 10, 2.2), 0.6), "#050404", 0.6)
    # el nido de raíces
    nido = np.zeros((lz.H, lz.W))
    rng = np.random.default_rng(502)
    for j in range(9):
        a = rng.random() * np.pi
        nido = np.maximum(nido, lz.trazo(lz.curva((12 + np.cos(a) * 10, 22), (12 + np.cos(a) * 4, 14 + rng.random() * 3), (12 - np.cos(a) * 9, 22 - rng.random() * 3), n=14), 1.0, 0.6))
    lz.sombrear(nido, ["#1a120c", "#2e2016", "#463020", "#5e422c"], 1.2, LUZ)
    # la semilla: grande, lisa, con la luz verde por dentro que respira
    brillo = [0.25, 0.55, 0.95][k]
    semilla = lz.elipse(12, 14, 6.4, 7.6)
    lz.sombrear(semilla, ["#1a2414", "#2a3a1e", "#3e5228", "#566e34", "#6e8a40"], 5, LUZ)
    nucleo = lz.elipse(12, 15, 3.2, 4.2)
    lz.pintar(lz.desenfocar(nucleo, 1.5), "#6fcf4f", 0.35 + brillo * 0.5)
    lz.pintar(nucleo, rampa(["#3e9a35", "#6fcf4f", "#c8f0a0"], np.clip(1 - np.hypot(lz.x - 12, lz.y - 15) / 4.5, 0, 1)), brillo)
    lz.pintar(lz.trazo([(12, 6.5), (12.5, 22)], 0.3) * semilla, "#152010", 0.6)           # la costura
    lz.pintar(lz.elipse(9.5, 10.5, 1.4, 2.2) * semilla, "#c8f0a0", 0.35)                 # el brillo de arriba
    return lz.sprite(contorno=CONTORNO * 0.8)


def huella(k):
    lz = Lienzo(8, 8, s=10, semilla=511 + k)
    lz.alfa[:] = 0
    for (x, y) in ((2.6, 3.2 + k), (5.4, 4.8 - k)):
        pie = lz.elipse(x, y, 1.2, 1.7)
        lz.pintar(lz.desenfocar(pie, 0.8), "#a28ae0", 0.6)
        lz.pintar(pie, "#e0d0ff", 0.9)
    return lz.sprite(tramado=0.0, contorno=0.0)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    tira([semilla_dormida(k) for k in range(3)]).save(os.path.join(SALIDA, "semilla_dormida.png"))
    tira([huella(k) for k in range(2)]).save(os.path.join(SALIDA, "huella.png"))
    print("Lo de la Gruta en", SALIDA)


if __name__ == "__main__":
    main()
