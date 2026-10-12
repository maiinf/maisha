"""LOS OBJETOS DEL LAGO ESPEJO, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_lago.py

Genera:
  arte/mundos/raiz/lago/barca.png     48×26       una barca de remos vieja, varada en la orilla de lado: tablas de
                                                  madera, la pintura turquesa desconchada, un remo y una cuerda
  arte/mundos/raiz/lago/altar.png     34×36       el altar de Kimya: piedras planas apiladas con un cuenco de agua
                                                  quieta encima, la piedra de la espiral apoyada delante y ofrendas
                                                  (conchas y flores) al pie
  arte/mundos/raiz/lago/menhir.png    3 × 18×36   las piedras talladas de la isla: altas y con aristas, inclinadas,
                                                  con espirales y rayas, musgo y líquenes
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_casa_shamba import vetas  # noqa: E402
from pintar_pasarelas import tira, MADERA, CONTORNO  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "lago")
LUZ = (-0.6, -0.7, 0.5)
GRIS = ["#1a1c20", "#292c32", "#3a3e45", "#4d5259", "#62686e", "#7a8086", "#949a9e", "#b1b5b6", "#cfd2cf"]
TURQUESA = ["#1c3535", "#285050", "#346161", "#4c8d8d", "#6db0b0"]


def barca():
    W, H = 48, 26
    lz = Lienzo(W, H, s=6, semilla=231)
    lz.pintar(lz.desenfocar(lz.elipse(24, 23, 23, 2.4), 0.8), "#0e0c0a", 0.6)
    # el casco, de lado (un poco volcado hacia nosotros): la quilla abajo y la borda arriba
    casco = lz.poligono([(2, 12), (8, 21), (40, 22), (46, 11), (40, 13), (8, 14)])
    tablas = (np.sin(lz.y * 1.6) * 0.5 + 0.5)
    lz.sombrear(casco, MADERA[1:7], 4, LUZ, textura=tablas * 0.5 + vetas(lz, 0.4, 11, True, 232) * 0.5, fuerza_tex=0.5)
    lz.pintar(casco * (np.abs(np.sin(lz.y * 1.6)) < 0.15), MADERA[0], 0.8)
    # la pintura turquesa, desconchada
    pintura = casco * (lz.ruido(1.4, 2, semilla=233) > 0.48) * (lz.y > 15)
    lz.pintar(pintura, TURQUESA[3], 0.85)
    lz.pintar(pintura * (lz.ruido(0.6, 1, semilla=234) > 0.7), TURQUESA[4], 0.8)
    # el interior, que se ve por arriba, y los bancos
    dentro = lz.poligono([(8, 14), (40, 13), (44, 11.5), (6, 12.5)])
    lz.pintar(dentro, MADERA[1])
    for x in (16, 28):
        lz.pintar(lz.trazo([(x, 12.5), (x + 1, 14)], 1.2), MADERA[4])
    # la borda, clara
    lz.pintar(lz.trazo([(2, 12), (8, 14), (40, 13), (46, 11)], 0.9), MADERA[6])
    # un remo apoyado y la cuerda de amarre, enrollada en la arena
    remo = lz.trazo([(14, 8), (36, 18)], 0.8)
    lz.sombrear(remo, MADERA[3:8], 0.6, LUZ)
    pala = lz.elipse(37.5, 18.6, 3.2, 1.4, 25)
    lz.sombrear(pala, MADERA[3:8], 1.2, LUZ)
    for r in (2.4, 1.6):
        lz.pintar(np.clip(lz.elipse(6, 22, r * 1.6, r * 0.7) - lz.elipse(6, 22, r * 1.6 - 0.5, r * 0.7 - 0.4), 0, 1), "#a48656")
    return lz.sprite(contorno=CONTORNO)


def altar():
    """El altar de Kimya: piedras planas apiladas (como hacen los caminantes) con un cuenco de agua quieta encima;
    delante, apoyada, una piedra con la espiral tallada que brilla un poco; al pie, conchas y flores."""
    W, H = 34, 36
    lz = Lienzo(W, H, s=6, semilla=241)
    rng = np.random.default_rng(245)
    lz.pintar(lz.desenfocar(lz.elipse(17, 33, 15, 2.4), 0.8), "#0e0c0a", 0.55)
    # el montón de piedras planas, cada una más pequeña, un poco torcidas
    y = 32.0
    for k, (ancho, alto) in enumerate(((12, 3.6), (10.5, 3.2), (9, 3.0), (7.5, 2.8))):
        dx = (rng.random() - 0.5) * 2.0
        losa = lz.elipse(17 + dx, y - alto * 0.5, ancho, alto * 0.62)
        lz.sombrear(losa, GRIS[2:8], alto, LUZ, textura=lz.ruido(0.8, 2, semilla=246 + k), fuerza_tex=0.4)
        lz.pintar(np.clip(losa - lz.elipse(17 + dx, y - alto * 0.5 - 0.6, ancho - 0.4, alto * 0.5), 0, 1), GRIS[1], 0.6)
        y -= alto * 0.95
    # el cuenco de agua quieta, encima
    cuenco = lz.elipse(17, y - 0.6, 5.4, 2.2)
    lz.sombrear(cuenco, ["#4a3a2a", "#6a5238", "#8a6e4c"], 1.5, LUZ)
    agua = lz.elipse(17, y - 1.0, 4.2, 1.2)
    lz.pintar(agua, "#9fd0d0")
    lz.pintar(lz.elipse(15.5, y - 1.2, 1.4, 0.4), "#e8f4f0", 0.9)
    # la piedra de la espiral, apoyada delante (inclinada)
    disco = lz.elipse(24.5, 26.5, 4.2, 5.2, 12)
    lz.sombrear(disco, GRIS[3:9], 3, LUZ, textura=lz.ruido(0.8, 2, semilla=247), fuerza_tex=0.3)
    t = np.linspace(0, 2.6 * np.pi, 40)
    espiral = lz.trazo([(24.5 + np.cos(a) * a * 0.38, 26.5 + np.sin(a) * a * 0.46) for a in t], 0.5)
    lz.pintar(espiral * disco, GRIS[1], 0.95)
    lz.brillo(espiral * disco, "#6db0b0", 1.8, 0.45)
    musgo = np.clip((lz.ruido(1.2, 2, semilla=248) - 0.6) * 4, 0, 1) * (lz.y > 26) * (lz.y < 33)
    lz.pintar(musgo * lz.elipse(17, 29, 12, 4), "#4d6436", 0.8)
    # las ofrendas, al pie: conchas y un ramito de flores
    for (x, y_) in ((6, 31.5), (9, 32.8), (28.5, 32.5)):
        concha = lz.elipse(x, y_, 1.6, 1.1)
        lz.sombrear(concha, ["#a89a80", "#d8ccb0", "#f4ecd8"], 1, LUZ)
    for (x, y_, c) in ((11.5, 30.5, "#de6771"), (13, 30, "#fff3c4"), (14.3, 30.6, "#e6a852")):
        lz.pintar(lz.trazo([(x, y_ + 2.4), (x, y_)], 0.3), "#4d6436")
        lz.pintar(lz.circulo(x, y_, 0.8), c)
    return lz.sprite(contorno=CONTORNO)


def menhir(k):
    W, H = 18, 36
    lz = Lienzo(W, H, s=6, semilla=251 + k)
    lz.pintar(lz.desenfocar(lz.elipse(9, 33.5, 7, 1.8), 0.6), "#0e0c0a", 0.6)
    alto = (4, 2, 8)[k]
    formas = [
        [(4, 34), (3, 20), (5, 9), (8, alto), (11, alto + 3), (13, 15), (14, 34)],        # alta, con la punta torcida
        [(5, 34), (4, 24), (6, 12), (9, alto), (12, 6), (14, 18), (13, 34)],              # fina, inclinada
        [(3, 34), (3, 22), (6, alto + 2), (11, alto), (15, 16), (15, 34)],                # ancha, con el canto partido
    ]
    piedra = lz.poligono(formas[k])
    lz.sombrear(piedra, GRIS[2:9], 5, LUZ, textura=lz.ruido(1.0, 2, semilla=252 + k), fuerza_tex=0.4)
    # lo tallado: una espiral, o rayas en zigzag, o un círculo con un punto
    cy = alto + 12
    if k == 0:
        t = np.linspace(0, 2.6 * np.pi, 40)
        talla = lz.trazo([(9 + np.cos(a) * a * 0.42, cy + np.sin(a) * a * 0.42) for a in t], 0.55)
    elif k == 1:
        talla = lz.trazo([(5, cy - 4), (8, cy - 1), (5, cy + 2), (8, cy + 5), (5, cy + 8)], 0.55)
        talla = np.maximum(talla, lz.trazo([(10, cy - 4), (13, cy - 1), (10, cy + 2), (13, cy + 5)], 0.55))
    else:
        talla = np.clip(lz.elipse(9, cy, 3.4, 3.4) - lz.elipse(9, cy, 2.6, 2.6), 0, 1)
        talla = np.maximum(talla, lz.circulo(9, cy, 0.7))
    lz.pintar(talla * piedra, GRIS[1], 0.95)
    lz.brillo(talla * piedra, "#6db0b0", 1.5, 0.35)
    # musgo abajo y líquenes amarillos
    musgo = np.clip((lz.ruido(1.2, 2, semilla=253 + k) - 0.5) * 4, 0, 1) * piedra * (lz.y > 28)
    lz.pintar(musgo, "#4d6436", 0.85)
    liquen = (lz.ruido(0.5, 1, semilla=254 + k) > 0.88) * piedra
    lz.pintar(liquen, "#c9b77d", 0.8)
    return lz.sprite(contorno=CONTORNO)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(barca()).save(os.path.join(SALIDA, "barca.png"))
    Image.fromarray(altar()).save(os.path.join(SALIDA, "altar.png"))
    tira([menhir(k) for k in range(3)]).save(os.path.join(SALIDA, "menhir.png"))
    print("Objetos del Lago Espejo en", SALIDA)


if __name__ == "__main__":
    main()
