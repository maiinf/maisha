"""LO DE LA GRUTA DE LAS RAÍCES, pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_gruta.py

Genera (en arte/mundos/raiz/gruta/):
  semilla_dormida.png   3 × 24×26   una semilla grande dormida en su nicho de raíces, que respira: brilla verde por
                                    dentro (0 apagándose, 1 media, 2 encendida)
  huella.png            2 × 8×8     una huella de Mauti, de luz lila (dos pies)
  raiz_dormida.png      4 × 56×36   una raíz enorme atravesada en el pasillo: 0-1 dormida (respira: se hincha y se
                                    deshincha, con el «ojo» de su nudo cerrado), 2 despertando (el ojo violeta
                                    entreabierto), 3 azotando (se levanta en arco, el ojo abierto)
  raiz_tapon.png        48×56       la maraña de raíces que tapa el atajo del pasillo al fondo
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


RAIZ_C = ["#140c08", "#22160e", "#342216", "#4a3220", "#62442c", "#7c583a", "#9a724c"]
GIZA_V = ["#2a0d3a", "#3a1650", "#6b2a8f", "#a855d6", "#d6a8f0"]


def raiz_dormida(k):
    """La raíz del pasillo: un tronco de raíz gordo y nudoso que cruza de pared a pared, con musgo y un nudo con forma de
    ojo cerrado. Respira (0-1), abre el ojo (2) o se levanta en arco para azotar (3)."""
    W, H = 56, 36
    lz = Lienzo(W, H, s=6, semilla=521 + k)
    alza = 14 if k == 3 else 0
    hincha = 0.6 if k == 1 else 0.0
    lz.pintar(lz.desenfocar(lz.elipse(28, 31, 26, 3.4), 0.8), "#050404", 0.6)
    pts = []
    for j in range(30):
        t = j / 29
        x = 1 + t * 54
        y = 26 - np.sin(t * np.pi) * (4 + alza) + np.sin(t * 9) * 1.2
        pts.append((x, y))
    cuerpo = np.zeros((lz.H, lz.W))
    for j, (x, y) in enumerate(pts):
        g = 5.0 + hincha + np.sin(j / 29 * np.pi) * 2.0
        cuerpo = np.maximum(cuerpo, lz.elipse(x, y, g, g * 0.8))
    vetas_ = (np.abs(np.sin(lz.x * 0.25 + np.sin(lz.y * 0.6) * 2)) < 0.12).astype(float)
    lz.sombrear(cuerpo, RAIZ_C, 5, LUZ, textura=lz.ruido(0.7, 2, semilla=522) * 0.6 + (1 - vetas_) * 0.4, fuerza_tex=0.5)
    lz.pintar(cuerpo * (lz.ruido(1.2, 2, semilla=523) > 0.66) * (lz.y < 24 - alza * 0.5), "#2f4a2a", 0.75)   # musgo
    # raicillas que se clavan en el suelo a los lados
    for (x0, lado) in ((4, -1), (9, -1), (47, 1), (52, 1)):
        lz.pintar(lz.trazo([(x0, 27), (x0 + lado * 3, 33)], 0.8, 0.3), RAIZ_C[2])
    # el nudo con forma de ojo, en medio
    ox, oy = 28, 22 - alza - 2
    nudo = lz.elipse(ox, oy, 5.5, 3.6)
    lz.sombrear(nudo, RAIZ_C[1:], 2.5, LUZ)
    if k in (0, 1):
        lz.pintar(lz.trazo([(ox - 3.5, oy + 0.3), (ox, oy + 1.2), (ox + 3.5, oy + 0.3)], 0.5), "#0a0604")
    else:
        abre = 1.2 if k == 2 else 2.2
        ojo = lz.elipse(ox, oy, 3.6, abre)
        lz.pintar(ojo, "#0a0604")
        lz.pintar(lz.elipse(ox, oy, 1.6, min(abre, 1.6)), GIZA_V[3])
        lz.brillo(lz.elipse(ox, oy, 1.6, min(abre, 1.6)), GIZA_V[4], 2.0, 0.7)
        lz.pintar(lz.elipse(ox, oy, 0.5, min(abre, 1.4)), "#0a0604")
    return lz.sprite(contorno=CONTORNO)


def raiz_tapon():
    W, H = 48, 56
    lz = Lienzo(W, H, s=6, semilla=531)
    rng = np.random.default_rng(532)
    lz.pintar(lz.desenfocar(lz.elipse(24, 52, 22, 3), 0.8), "#050404", 0.6)
    marana = np.zeros((lz.H, lz.W))
    for j in range(30):
        a = (4 + rng.random() * 40, rng.random() * 8)
        b = (rng.random() * 48, 18 + rng.random() * 18)
        c = (4 + rng.random() * 40, 50 + rng.random() * 4)
        marana = np.maximum(marana, lz.trazo(lz.curva(a, b, c, n=24), 3.0 + rng.random() * 2.6, 1.6))
    lz.sombrear(marana, RAIZ_C, 3, LUZ, textura=lz.ruido(0.6, 2, semilla=533), fuerza_tex=0.45)
    lz.pintar(marana * (lz.ruido(1.2, 2, semilla=534) > 0.7), "#2f4a2a", 0.7)
    return lz.sprite(contorno=CONTORNO)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    tira([semilla_dormida(k) for k in range(3)]).save(os.path.join(SALIDA, "semilla_dormida.png"))
    tira([huella(k) for k in range(2)]).save(os.path.join(SALIDA, "huella.png"))
    tira([raiz_dormida(k) for k in range(4)]).save(os.path.join(SALIDA, "raiz_dormida.png"))
    Image.fromarray(raiz_tapon()).save(os.path.join(SALIDA, "raiz_tapon.png"))
    print("Lo de la Gruta en", SALIDA)


if __name__ == "__main__":
    main()
