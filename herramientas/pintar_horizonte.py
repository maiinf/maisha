"""EL HORIZONTE INMÓVIL (el Valle del Ocaso, el final del juego), pintado con detalle.

    python3 herramientas/pintar_horizonte.py

Genera en arte/mundos/ocaso/horizonte/:
  jua_giza.png   6 × 128×128  JUA-GIZA, EL SOL ENCADENADO (jefe final): el sol del atardecer, atado al altar por tres
                              cadenas (oeste, este, sur), con la cara cansada y asustada.
                              0 encadenado · 1 LLAMARADA (blanco ardiente) · 2 con el VELO de Giza (morado, el broche
                              tapado) · 3 el velo abierto: el BROCHE de oro a la vista · 4 golpeado (blanco)
                              · 5 en CALMA (sin cadenas, los ojos cerrados, una luz suave)
  contrapeso.png 2 × 36×48    EL CONTRAPESO DEL OESTE: un bloque de basalto colgado de la cadena. 0 entero · 1 roto
  candado.png    2 × 32×36    EL CANDADO DEL SUR: un cerrojo de bronce con un ojo de Giza. 0 cerrado · 1 brilla
                              (se le puede dar)
  pilar.png      2 × 20×44    UN PILAR DE LA PASARELA. 0 apagado · 1 encendido (dorado)
  pedestal.png   2 × 48×34    EL PEDESTAL DE LAS TRES PESAS. 0 vacío · 1 con las tres pesas
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_mirador import LUZ, ARENISCA, BRONCE, SOMBRA, AMBAR, BLANCO  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "ocaso", "horizonte")
SOL = ["#a83a10", "#d8641c", "#f09030", "#f8b848", "#ffd878", "#fff0b0"]
VIOLETA = ["#1a0a2a", "#3a1858", "#5e2a88", "#8a4ab8", "#b87ce0", "#e0c0f8"]
BASALTO = ["#0e0c14", "#1c1a26", "#2e2c3c", "#464458", "#62607a", "#8a88a4"]
HIERRO = ["#14161c", "#2a2e3a", "#464c5c", "#6a7284", "#949cae", "#c4cad8"]


def cadena(lz, a, b, grosor=2.0):
    """Una cadena de eslabones de hierro de a a b."""
    linea = lz.trazo([a, b], grosor)
    lz.pintar(linea, HIERRO[1])
    d = np.hypot(b[0] - a[0], b[1] - a[1])
    n = max(2, int(d / 5))
    for k in range(n):
        t = (k + 0.5) / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        lz.sombrear(np.clip(lz.circulo(x, y, grosor * 1.3) - lz.circulo(x, y, grosor * 0.6), 0, 1), HIERRO, 1.0, LUZ)


def jua_giza(f):
    W, H = 128, 128
    lz = Lienzo(W, H, s=3, semilla=17000 + f)
    cx, cy, r = 64, 60, 34
    calma = f == 5
    rampa = BLANCO if f in (1, 4) else SOL
    # el halo y los rayos
    halo = lz.circulo(cx, cy, r + (16 if f == 1 else 9))
    lz.sumar_luz(lz.desenfocar(halo, 10), "#ffe0a0" if not calma else "#ffd0a0", 0.9 if f == 1 else 0.6)
    for k in range(16):
        a = k * np.pi / 8 + (0.1 if f % 2 else 0)
        largo = r + (20 if f == 1 else 12) + (k % 2) * 6
        rayo = lz.poligono([(cx + np.cos(a - 0.08) * (r - 2), cy + np.sin(a - 0.08) * (r - 2)), (cx + np.cos(a) * largo, cy + np.sin(a) * largo),
                            (cx + np.cos(a + 0.08) * (r - 2), cy + np.sin(a + 0.08) * (r - 2))])
        lz.sombrear(rayo, rampa[2:] if not calma else ["#d88a50", "#f0b070", "#ffd8a0"], 2, LUZ)
    disco = lz.circulo(cx, cy, r)
    lz.sombrear(disco, rampa, 14, LUZ, textura=lz.ruido(3, 3, semilla=17001), fuerza_tex=0.15)
    lz.pintar(np.clip(disco - lz.circulo(cx, cy, r - 2.5), 0, 1), SOL[1] if not calma else "#d88a50", 0.7)
    # la cara: asustada y cansada (cejas hacia arriba, ojos grandes); en calma, dormida y con media sonrisa
    for lado in (-1, 1):
        ox, oy = cx + lado * 12, cy - 4
        if calma:
            lz.pintar(lz.trazo([(ox - 5, oy), (ox, oy + 3), (ox + 5, oy)], 1.2), "#8a3a10")
        elif f == 1:
            lz.pintar(lz.trazo([(ox - 5, oy), (ox + 5, oy)], 1.4), "#c86020")
        else:
            lz.pintar(lz.elipse(ox, oy, 4.5, 5.5), "#5a1a08")
            lz.pintar(lz.circulo(ox - 1.4, oy - 2, 1.4), "#fff8e0")
            lz.pintar(lz.trazo([(ox - lado * 5, oy - 12), (ox + lado * 5, oy - 9)], 1.0), "#8a3a10")     # (cejas de susto)
    if calma:
        lz.pintar(lz.trazo([(cx - 6, cy + 12), (cx, cy + 15), (cx + 6, cy + 12)], 1.0), "#8a3a10")
    else:
        lz.pintar(lz.elipse(cx, cy + 14, 4, 2.6 if f != 1 else 4), "#5a1a08")
    # las tres cadenas (oeste, este y sur) hasta sus argollas, y el broche que las junta en el pecho
    if not calma:
        cadena(lz, (cx - r + 4, cy + 6), (4, cy + 22))
        cadena(lz, (cx + r - 4, cy + 6), (W - 4, cy + 22))
        cadena(lz, (cx, cy + r - 2), (cx, H - 4))
        broche = lz.poligono([(cx, cy + 22), (cx + 7, cy + 29), (cx, cy + 36), (cx - 7, cy + 29)])
        lz.sombrear(broche, BRONCE if f != 3 else AMBAR, 2, LUZ)
        lz.pintar(lz.circulo(cx, cy + 29, 2.2), VIOLETA[3] if f != 3 else "#fff4c8")
        if f == 3:
            lz.sumar_luz(lz.desenfocar(broche, 6), AMBAR[3], 1.0)
    # el velo de Giza: jirones morados que lo envuelven
    if f == 2:
        velo = lz.circulo(cx, cy + 6, r + 14) * (lz.desenfocar(lz.ruido(9, 2, semilla=17002), 2) > 0.4)
        lz.sombrear(velo * 1.0, VIOLETA, 6, LUZ)
        lz.pintar(velo * (lz.ruido(1.2, 2, semilla=17003) > 0.7), VIOLETA[5], 0.5)
    elif f == 3:
        jirones = np.clip(lz.circulo(cx, cy + 6, r + 14) - lz.circulo(cx, cy + 6, r + 4), 0, 1) * (lz.desenfocar(lz.ruido(9, 2, semilla=17002), 2) > 0.45)
        lz.sombrear(jirones * 1.0, VIOLETA[:4], 4, LUZ)
    return lz.sprite(contorno=0.4)


def contrapeso(f):
    W, H = 36, 48
    lz = Lienzo(W, H, s=4, semilla=17010 + f)
    if f == 0:
        cadena(lz, (18, 0), (18, 12), 1.6)
        bloque = lz.poligono([(5, 14), (31, 14), (33, 46), (3, 46)])
        lz.sombrear(bloque, BASALTO, 6, LUZ, textura=((lz.y % 8) < 0.8) * 1.0, fuerza_tex=-0.25)
        lz.sombrear(lz.circulo(18, 30, 6), BRONCE, 2, LUZ)
        lz.pintar(lz.trazo([(14, 30), (22, 30)], 0.8) + lz.trazo([(18, 26), (18, 34)], 0.8), BRONCE[0], 0.9)
        lz.pintar(lz.trazo([(8, 20), (12, 34), (9, 40)], 0.6), VIOLETA[3], 0.6)        # (grietas de Giza)
    else:
        for (x0, y0, x1, y1) in ((2, 46, 15, 34), (17, 46, 33, 38), (8, 33, 20, 26)):
            lz.sombrear(lz.poligono([(x0, y0), (x1, y1), (x1 + 3, y1 + 3), (x0 + 3, y0)]), BASALTO, 2, LUZ)
        cadena(lz, (18, 0), (22, 10), 1.6)
    return lz.sprite(contorno=0.4)


def candado(f):
    W, H = 32, 36
    lz = Lienzo(W, H, s=4, semilla=17020 + f)
    arco = np.clip(lz.elipse(16, 12, 10, 10) - lz.elipse(16, 12, 6.5, 6.5), 0, 1) * (lz.y < 16)
    lz.sombrear(arco, HIERRO, 2, LUZ)
    cuerpo = lz.poligono([(3, 14), (29, 14), (27, 34), (5, 34)])
    lz.sombrear(cuerpo, BRONCE if f == 0 else AMBAR, 5, LUZ)
    ojo = lz.elipse(16, 24, 5, 3.6)
    lz.pintar(ojo, VIOLETA[1])
    lz.pintar(lz.circulo(16, 24, 1.8), VIOLETA[4] if f == 0 else "#fff4c8")
    if f == 1:
        lz.sumar_luz(lz.desenfocar(cuerpo, 6), AMBAR[3], 0.9)
    return lz.sprite(contorno=0.4)


def pilar(f):
    W, H = 20, 44
    lz = Lienzo(W, H, s=4, semilla=17030 + f)
    lz.sombrear(lz.poligono([(2, 43), (18, 43), (16, 38), (4, 38)]), ARENISCA[1:], 2, LUZ)
    fuste = lz.poligono([(5, 38), (15, 38), (14, 10), (6, 10)])
    lz.sombrear(fuste, ARENISCA if f == 0 else AMBAR, 3, LUZ, textura=((lz.y % 6) < 0.7) * 1.0, fuerza_tex=-0.2)
    copa = lz.poligono([(3, 10), (17, 10), (14, 4), (6, 4)])
    lz.sombrear(copa, BRONCE, 2, LUZ)
    llama = lz.elipse(10, 3, 3, 3.6)
    if f == 1:
        lz.pintar(llama, AMBAR[4])
        lz.sumar_luz(lz.desenfocar(llama, 6), AMBAR[3], 1.0)
        lz.sumar_luz(lz.desenfocar(fuste, 4), AMBAR[3], 0.4)
    else:
        lz.pintar(lz.elipse(10, 5, 4, 1.4), "#2a1420")
    return lz.sprite(contorno=0.4)


def pedestal(f):
    W, H = 48, 34
    lz = Lienzo(W, H, s=4, semilla=17040 + f)
    base = lz.poligono([(2, 33), (46, 33), (42, 20), (6, 20)])
    lz.sombrear(base, ARENISCA, 5, LUZ, textura=((lz.x % 9) < 0.8) * 1.0, fuerza_tex=-0.2)
    for k, x in enumerate((13, 24, 35)):
        hueco = lz.elipse(x, 21, 4.4, 2.2)
        lz.pintar(hueco, "#2a1420")
        if f == 1:
            pesa = lz.poligono([(x - 4, 21), (x + 4, 21), (x + 3, 9), (x - 3, 9)])
            lz.sombrear(pesa, BRONCE, 2, LUZ)
            lz.pintar(lz.circulo(x, 15, 1.6), (AMBAR[3], "#d4b0f8", AMBAR[4])[k])
            lz.sombrear(np.clip(lz.circulo(x, 7, 2.2) - lz.circulo(x, 7, 1.1), 0, 1), BRONCE[1:], 1, LUZ)
    if f == 1:
        lz.sumar_luz(lz.desenfocar(lz.poligono([(6, 20), (42, 20), (40, 10), (8, 10)]), 6), AMBAR[3], 0.5)
    return lz.sprite(contorno=0.4)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    tira("jua_giza", jua_giza, 6)
    tira("contrapeso", contrapeso, 2)
    tira("candado", candado, 2)
    tira("pilar", pilar, 2)
    tira("pedestal", pedestal, 2)
    print("El Horizonte Inmóvil pintado en", SALIDA)
