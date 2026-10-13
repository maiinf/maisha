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
  altar_corteza.png     2 × 48×52   el santuario: un tocón enorme del Primer Árbol, con anillos y raíces, y encima un
                                    escudo de corteza que brilla (0 con el escudo, 1 ya sin él)
  escudo.png            16×20       el escudo de corteza (Maisha lo levanta con J mantenida)
  espino.png            3 × 30×30   el ESPINO DE GIZA (enemigo): 0 quieto, 1 cargando (se hincha y brilla), 2 escupiendo
  espina.png            10×5        la espina que escupe
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


def escudo_corteza(lz, cx, cy, e=1.0):
    """Un escudo ovalado de corteza del Primer Árbol, con su veta dorada en espiral."""
    forma = lz.elipse(cx, cy, 6.5 * e, 8.5 * e)
    lz.sombrear(forma, ["#2a1a0c", "#4a3016", "#6e4a22", "#946a34", "#b88a4a"], 3 * e, LUZ,
                textura=(np.abs(np.sin(lz.x * 1.4 + np.sin(lz.y * 0.8) * 1.5)) < 0.3).astype(float), fuerza_tex=-0.35)
    lz.pintar(np.clip(forma - lz.elipse(cx, cy, 5.6 * e, 7.6 * e), 0, 1), "#d6b46e", 0.9)
    espiral = np.zeros((lz.H, lz.W))
    pts = [(cx + np.cos(a) * a * 0.55 * e, cy + np.sin(a) * a * 0.7 * e) for a in np.linspace(0, 9, 40)]
    espiral = lz.trazo(pts, 0.45 * e)
    lz.pintar(espiral * forma, "#f9d77a", 0.9)
    lz.brillo(espiral * forma, "#f9d77a", 1.5 * e, 0.35)
    return forma


def altar_corteza(k):
    W, H = 48, 52
    lz = Lienzo(W, H, s=6, semilla=541 + k)
    lz.pintar(lz.desenfocar(lz.elipse(24, 48, 21, 3), 0.8), "#050404", 0.6)
    # las raíces que salen del tocón y se agarran al suelo
    for (x0, x1) in ((8, 1), (14, 6), (34, 42), (40, 47)):
        lz.sombrear(lz.trazo(lz.curva((x0 + (24 - x0) * 0.3, 38), ((x0 + x1) / 2, 44), (x1, 49), n=14), 2.4, 0.8), RAIZ_C, 1.6, LUZ)
    # el tocón: corteza gruesa por fuera y la cara de arriba con sus anillos
    tronco = lz.poligono([(8, 26), (40, 26), (42, 46), (6, 46)])
    lz.sombrear(tronco, RAIZ_C, 6, LUZ, textura=(np.abs(np.sin(lz.x * 0.9)) < 0.25).astype(float) * 0.6 + lz.ruido(0.6, 2, semilla=542) * 0.4, fuerza_tex=0.5)
    cara = lz.elipse(24, 26, 16, 5.5)
    lz.sombrear(cara, ["#5a3a20", "#7a5430", "#9a7044", "#b88c5a"], 2, LUZ)
    for r in range(2, 15, 2):
        lz.pintar(np.clip(lz.elipse(24, 26, r, r * 0.34) - lz.elipse(24, 26, r - 0.4, r * 0.34 - 0.15), 0, 1), "#4a3018", 0.7)
    lz.pintar(lz.trazo([(24, 26), (30, 21.5)], 0.4) * cara, "#2a1a0c", 0.8)              # una grieta
    lz.pintar((lz.ruido(1.2, 2, semilla=543) > 0.65) * tronco, "#2f4a2a", 0.7)            # musgo
    # unas semillas dormidas a los pies, pequeñas
    for (x, y) in ((10, 44), (39, 45)):
        lz.sombrear(lz.elipse(x, y, 2.4, 2.8), ["#1a2414", "#3e5228", "#6e8a40"], 2, LUZ)
        lz.pintar(lz.elipse(x, y + 0.5, 1, 1.4), "#6fcf4f", 0.8)
    if k == 0:
        # el escudo, de pie sobre el tocón, que brilla
        lz.sumar_luz(lz.desenfocar(lz.elipse(24, 15, 9, 11), 5), "#f9b947", 0.5)
        escudo_corteza(lz, 24, 15, 1.2)
    return lz.sprite(contorno=CONTORNO)


def escudo():
    lz = Lienzo(16, 20, s=8, semilla=551)
    escudo_corteza(lz, 8, 10, 1.05)
    return lz.sprite(contorno=CONTORNO)


def espino(k):
    """El espino de Giza: una mata de tallos de piedra con espinas, y en medio un capullo violeta que se hincha y escupe."""
    W, H = 30, 30
    lz = Lienzo(W, H, s=8, semilla=561 + k)
    lz.pintar(lz.desenfocar(lz.elipse(15, 27, 12, 2.4), 0.6), "#050404", 0.6)
    tallos = np.zeros((lz.H, lz.W))
    rng = np.random.default_rng(562)
    for j in range(9):
        a = -np.pi / 2 + (j - 4) * 0.32
        largo = 10 + rng.random() * 5
        x1, y1 = 15 + np.cos(a) * largo, 26 + np.sin(a) * largo
        tallos = np.maximum(tallos, lz.trazo([(15, 26), (x1, y1)], 1.2, 0.4))
        for t in (0.4, 0.7):
            px, py = 15 + np.cos(a) * largo * t, 26 + np.sin(a) * largo * t
            tallos = np.maximum(tallos, lz.trazo([(px, py), (px + np.cos(a + 1.2) * 2.2, py + np.sin(a + 1.2) * 2.2)], 0.4))
    lz.sombrear(tallos, ["#141218", "#24202a", "#3a3442", "#524a5a"], 1.4, LUZ)
    hincha = [1.0, 1.35, 0.85][k]
    capullo = lz.elipse(15, 16, 4.2 * hincha, 4.8 * hincha)
    lz.pintar(lz.desenfocar(capullo, 1.4), GIZA_V[3], 0.4 + 0.3 * k)
    lz.sombrear(capullo, GIZA_V[1:] + ["#f4e0ff"], 3, LUZ)
    if k == 2:
        lz.pintar(lz.elipse(15, 13, 1.6, 1.2), "#14081c")                                   # la boca abierta
    return lz.sprite(contorno=CONTORNO)


def espina():
    lz = Lienzo(10, 5, s=10, semilla=571)
    lz.sombrear(lz.poligono([(0, 1.5), (7, 2), (10, 2.5), (7, 3), (0, 3.5)]), ["#24202a", "#524a5a", "#a855d6", "#d6a8f0"], 1, LUZ)
    return lz.sprite(contorno=CONTORNO * 0.6)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    tira([semilla_dormida(k) for k in range(3)]).save(os.path.join(SALIDA, "semilla_dormida.png"))
    tira([huella(k) for k in range(2)]).save(os.path.join(SALIDA, "huella.png"))
    tira([raiz_dormida(k) for k in range(4)]).save(os.path.join(SALIDA, "raiz_dormida.png"))
    Image.fromarray(raiz_tapon()).save(os.path.join(SALIDA, "raiz_tapon.png"))
    tira([altar_corteza(k) for k in range(2)]).save(os.path.join(SALIDA, "altar_corteza.png"))
    Image.fromarray(escudo()).save(os.path.join(SALIDA, "escudo.png"))
    tira([espino(k) for k in range(3)]).save(os.path.join(SALIDA, "espino.png"))
    Image.fromarray(espina()).save(os.path.join(SALIDA, "espina.png"))
    print("Lo de la Gruta en", SALIDA)


if __name__ == "__main__":
    main()
