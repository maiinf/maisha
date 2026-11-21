"""LA CALZADA DE LOS OBELISCOS (el Valle del Ocaso, el camino del sureste de Jioni), pintada con detalle.

    python3 herramientas/pintar_calzada.py

Genera en arte/mundos/ocaso/calzada/:
  centinela.png 5 × 28×40  UN CENTINELA DE RELOJ: un guardián de bronce con un reloj de arena por cabeza y una
                           alabarda. 0-1 anda (en penumbra) · 2 golpea · 3 ESTATUA (al sol: piedra dorada, quieto)
                           · 4 volcado y roto
  saa.png       6 × 96×96  SAA-MCHANGA, EL AUTÓMATA RELOJ DE ARENA (jefe): un coloso de bronce con dos ampollas, la de
                           arriba de luz y la de abajo de sombra, dentro de un aro de relojería. 0 lleno · 1 vaciándose
                           (barre) · 2 vacío e INCLINADO · 3 VOLCADO (el aro al aire) · 4 volcado y golpeado
                           · 5 vencido
  peso.png      16×22      LA PESA DEL SUR: una pesa de bronce con un reloj de arena grabado
  pilar.png     40×56      UN PILAR DE LA CALZADA: un pilar de arenisca con su capitel y una lámpara apagada
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_mirador import LUZ, ARENISCA, BRONCE, SOMBRA, AMBAR, BLANCO  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "ocaso", "calzada")
PIEDRA = ["#4a3a2a", "#6e5a3e", "#94805a", "#b8a478", "#d8c89a"]
GRIS = ["#3a3640", "#5a5662", "#7e7a86", "#a29ea8", "#c6c2ca"]


def ampolla(lz, cx, cy, w, h, lleno, rampa_arena, vidrio="#2a1830"):
    """Un reloj de arena: dos conos de vidrio y la arena dentro (lleno: 0 vacío arriba … 1 lleno arriba)."""
    arriba = lz.poligono([(cx - w, cy - h), (cx + w, cy - h), (cx + 1, cy), (cx - 1, cy)])
    abajo = lz.poligono([(cx - 1, cy), (cx + 1, cy), (cx + w, cy + h), (cx - w, cy + h)])
    lz.pintar(np.clip(arriba + abajo, 0, 1), vidrio)
    if lleno > 0.02:
        lz.sombrear(arriba * (lz.y > cy - h * lleno), rampa_arena, 2.0, LUZ)
    if lleno < 0.98:
        lz.sombrear(abajo * (lz.y > cy + h * lleno), rampa_arena, 2.0, LUZ)
    lz.pintar(lz.trazo([(cx - w + 1, cy - h + 1), (cx - 2, cy - 2)], 0.5), "#ffffff", 0.35)
    return np.clip(arriba + abajo, 0, 1)


def centinela(f):
    W, H = 28, 40
    lz = Lienzo(W, H, s=4, semilla=16000 + f)
    roto = f == 4
    rampa = PIEDRA if f in (3, 4) else BRONCE
    if roto:
        # tumbado y partido en tres: el cuerpo, las piernas y la cabeza rota, con la arena derramada
        lz.sombrear(lz.poligono([(9, 39), (21, 39), (21, 31), (9, 31)]), rampa, 2.5, LUZ)
        lz.sombrear(lz.poligono([(1, 39), (8, 38), (8, 34), (1, 35)]), rampa, 1.5, LUZ)
        lz.sombrear(lz.poligono([(22, 38), (27, 37), (27, 32), (23, 31)]), rampa, 1.5, LUZ)
        lz.pintar(lz.trazo([(12, 33), (15, 37), (13, 39)], 0.5), PIEDRA[0], 0.8)
        lz.pintar(lz.elipse(20, 39, 7, 1.4), AMBAR[2], 0.9)
        lz.pintar(lz.trazo([(3, 30), (14, 26)], 0.8), PIEDRA[1])
        return lz.sprite(contorno=0.4)
    paso = (f == 1) * 2
    for x, d in ((11, -paso), (17, paso)):                                  # las piernas
        lz.sombrear(lz.trazo([(x, 26), (x + d * 0.5, 38)], 2.2, 1.8), rampa, 1.0, LUZ)
    cuerpo = lz.poligono([(8, 27), (20, 27), (21, 15), (7, 15)])
    lz.sombrear(cuerpo, rampa, 3.0, LUZ, textura=((lz.y % 4) < 0.7) * 1.0, fuerza_tex=-0.2)
    lz.pintar(lz.trazo([(8, 20), (20, 20)], 0.5), rampa[0], 0.7)
    lz.sombrear(lz.elipse(14, 15, 8, 2.4), rampa, 1.5, LUZ)               # las hombreras
    # la cabeza: un reloj de arena en su marco
    marco = np.clip(lz.poligono([(8, 2), (20, 2), (20, 4), (8, 4)]) + lz.poligono([(8, 13), (20, 13), (20, 15), (8, 15)])
                    + lz.trazo([(9, 3), (9, 14)], 0.7) + lz.trazo([(19, 3), (19, 14)], 0.7), 0, 1)
    vid = ampolla(lz, 14, 8.5, 4.4, 4.6, 0.6, AMBAR[1:] if f != 3 else PIEDRA[2:])
    lz.sombrear(marco, rampa, 1.0, LUZ)
    if f in (0, 1, 2):
        lz.sumar_luz(lz.desenfocar(vid, 3), "#b070e0", 0.35)
    # la alabarda
    if f == 2:
        asta = lz.trazo([(21, 22), (27, 6)], 0.8)
        hoja = lz.poligono([(25, 4), (28, 6), (27, 12), (24, 9)])
    else:
        asta = lz.trazo([(23, 38), (23, 4)], 0.8)
        hoja = lz.poligono([(21, 3), (26, 3), (25, 9), (22, 9)])
    lz.pintar(asta, rampa[1])
    lz.sombrear(hoja, rampa[1:] if f != 3 else PIEDRA[1:], 1.0, LUZ)
    if f == 3:
        lz.pintar(lz.trazo([(10, 18), (13, 24), (11, 26)], 0.4), PIEDRA[0], 0.7)   # una grieta
        lz.sumar_luz(lz.desenfocar(cuerpo, 4), AMBAR[3], 0.25)
    return lz.sprite(contorno=0.4)


def saa(f):
    W, H = 96, 96
    lz = Lienzo(W, H, s=3, semilla=16020 + f)
    vencido = f == 5
    rampa = GRIS if vencido else (BLANCO if f == 4 else BRONCE)
    cx = 48
    if f in (3, 4, 5):
        # VOLCADO: tumbado, el aro de relojería al aire, las ruedas dentadas a la vista
        base = lz.poligono([(10, 90), (86, 90), (80, 78), (16, 78)])
        lz.sombrear(base, rampa, 4.0, LUZ)
        aro = np.clip(lz.elipse(cx, 66, 28, 14) - lz.elipse(cx, 66, 22, 10), 0, 1)
        lz.sombrear(aro, rampa, 3.0, LUZ)
        for k in range(12):
            a = k * np.pi / 6
            lz.pintar(lz.circulo(cx + np.cos(a) * 25, 66 + np.sin(a) * 12, 1.4), rampa[4])
        for (x, y, r) in ((cx - 8, 66, 7), (cx + 7, 64, 5), (cx + 1, 72, 4)):
            rueda = np.clip(lz.circulo(x, y, r) - lz.circulo(x, y, r * 0.35), 0, 1)
            dientes = (np.abs(np.sin(np.arctan2(lz.y - y, lz.x - x) * 8)) > 0.6) * lz.circulo(x, y, r + 1.2) * (1 - lz.circulo(x, y, r))
            lz.sombrear(np.clip(rueda + dientes, 0, 1), AMBAR if f == 3 else rampa, 1.5, LUZ)
        ampolla_v = lz.poligono([(cx + 20, 56), (cx + 40, 50), (cx + 40, 62)])
        lz.pintar(ampolla_v, "#2a1830")
        if f == 3:
            lz.sumar_luz(lz.desenfocar(aro, 5), AMBAR[3], 0.8)
        if vencido:
            lz.pintar(lz.circulo(cx - 20, 84, 3) + lz.circulo(cx + 26, 86, 2), GRIS[2])
        return lz.sprite(contorno=0.4)
    inclina = f == 2
    dx = 6 if inclina else 0
    # el pedestal y las patas
    pie = lz.poligono([(18, 95), (78, 95), (72, 84), (24, 84)])
    lz.sombrear(pie, rampa, 4.0, LUZ, textura=((lz.x % 8) < 0.8) * 1.0, fuerza_tex=-0.2)
    for x in (30, 66):
        lz.sombrear(lz.trazo([(x, 84), (x + dx * 0.5, 70)], 4.0, 3.2), rampa, 2.0, LUZ)
    # el aro de relojería que lo rodea
    aro = np.clip(lz.elipse(cx + dx, 46, 36, 38) - lz.elipse(cx + dx, 46, 31, 33), 0, 1)
    lz.sombrear(aro, rampa, 3.0, LUZ)
    for k in range(12):
        a = k * np.pi / 6
        lz.pintar(lz.trazo([(cx + dx + np.cos(a) * 34, 46 + np.sin(a) * 36), (cx + dx + np.cos(a) * 39, 46 + np.sin(a) * 41)], 1.2), rampa[3])
    # el cuerpo: dos ampollas (luz arriba, sombra abajo) entre columnas
    lleno = {0: 1.0, 1: 0.45, 2: 0.0}[f]
    luzc = ["#8a5a1a", "#c88a2a", "#f0c050", "#fff0b0"]
    arriba = lz.poligono([(cx + dx - 18, 16), (cx + dx + 18, 16), (cx + dx + 2, 46), (cx + dx - 2, 46)])
    abajo = lz.poligono([(cx + dx - 2, 46), (cx + dx + 2, 46), (cx + dx + 18, 76), (cx + dx - 18, 76)])
    lz.pintar(np.clip(arriba + abajo, 0, 1), "#1a0e26")
    if lleno > 0:
        alto = 16 + 30 * (1 - lleno)
        lz.sombrear(arriba * (lz.y > alto), luzc, 3.0, LUZ)
        lz.sumar_luz(lz.desenfocar(arriba * (lz.y > alto), 6), AMBAR[3], 0.9)
    lz.sombrear(abajo * (lz.y > 76 - 30 * (1 - lleno) - 2), SOMBRA[1:], 3.0, LUZ)
    if f == 1:
        lz.pintar(lz.trazo([(cx + dx, 46), (cx + dx, 74)], 0.6), AMBAR[4])   # el chorro de arena
    for x in (-21, 21):
        lz.sombrear(lz.poligono([(cx + dx + x - 2.5, 76), (cx + dx + x + 2.5, 76), (cx + dx + x + 2.5, 16), (cx + dx + x - 2.5, 16)]), rampa, 1.5, LUZ)
    for y in (12, 76):
        lz.sombrear(lz.poligono([(cx + dx - 25, y), (cx + dx + 25, y), (cx + dx + 23, y + 5), (cx + dx - 23, y + 5)]), rampa, 2.0, LUZ)
    lz.pintar(lz.trazo([(cx + dx - 14, 19), (cx + dx - 5, 40)], 0.6), "#ffffff", 0.3)
    lz.pintar(lz.circulo(cx + dx, 46, 2.2), AMBAR[4] if f != 2 else "#6a4a8a")    # el ojo del cuello
    return lz.sprite(contorno=0.4)


def peso():
    W, H = 16, 22
    lz = Lienzo(W, H, s=5, semilla=16040)
    gancho = np.clip(lz.circulo(8, 3.5, 2.6) - lz.circulo(8, 3.5, 1.4), 0, 1)
    lz.sombrear(gancho, BRONCE[1:], 1.0, LUZ)
    cuerpo = lz.poligono([(4, 6), (12, 6), (14, 20), (2, 20)])
    lz.sombrear(cuerpo, BRONCE, 4.0, LUZ)
    lz.pintar(lz.trazo([(3, 9), (13, 9)], 0.4), BRONCE[1], 0.8)
    reloj = np.clip(lz.poligono([(5.5, 11), (10.5, 11), (8.3, 14.5), (7.7, 14.5)]) + lz.poligono([(7.7, 14.5), (8.3, 14.5), (10.5, 18), (5.5, 18)]), 0, 1)
    lz.pintar(reloj, AMBAR[3])
    lz.sumar_luz(lz.desenfocar(reloj, 2), AMBAR[2], 0.6)
    return lz.sprite(contorno=0.4)


def pilar():
    W, H = 40, 56
    lz = Lienzo(W, H, s=3, semilla=16050)
    lz.sombrear(lz.poligono([(4, 55), (36, 55), (34, 48), (6, 48)]), ARENISCA[1:], 3.0, LUZ)
    fuste = lz.poligono([(10, 48), (30, 48), (28, 12), (12, 12)])
    lz.sombrear(fuste, ARENISCA, 5.0, LUZ, textura=((np.abs((lz.x - 20) % 5) < 0.7)) * 1.0, fuerza_tex=-0.2)
    lz.sombrear(lz.poligono([(6, 12), (34, 12), (31, 5), (9, 5)]), ARENISCA, 3.0, LUZ)
    lampara = lz.elipse(20, 3, 5, 3)
    lz.sombrear(lampara, BRONCE, 1.5, LUZ)
    lz.pintar(lz.elipse(20, 2.4, 2.5, 1.2), "#3a2030")
    lz.pintar(lz.trazo([(14, 30), (18, 36), (16, 42)], 0.5), ARENISCA[0], 0.6)
    return lz.sprite(contorno=0.4)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    tira("centinela", centinela, 5)
    tira("saa", saa, 6)
    Image.fromarray(peso(), "RGBA").save(os.path.join(SALIDA, "peso.png"))
    Image.fromarray(pilar(), "RGBA").save(os.path.join(SALIDA, "pilar.png"))
    print("Calzada pintada en", SALIDA)
