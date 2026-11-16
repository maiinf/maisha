"""LAS GALERÍAS DE ÁMBAR (Asterhaul), pintadas con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_galerias.py

Genera en arte/mundos/asterhaul/galerias/:
  aguja.png      3 × 24×30  UN CAMBIO DE AGUJAS: una palanca de hierro en su pie, con un disco que señala hacia
                 dónde va el desvío. 0 oeste · 1 norte · 2 sur
  mchimbaji.png  4 × 28×24  MCHIMBAJI, EL ESCARABAJO BARRENADOR DE ÁMBAR: 0 y 1 hecho una bola (rueda: dos
                 giros de los élitros a rayas de ámbar) · 2 PANZA ARRIBA (atontado, las patas al aire, el cuerno
                 de taladro torcido) · 3 panza arriba y golpeado (blanco)
  geoda.png      2 × 28×30  UNA GEODA RESONANTE: una piedra redonda partida. 0 dormida (el cristal, apagado) ·
                 1 encendida (el ámbar de dentro alumbra)
  barricada.png  2 × 48×44  UNA BARRICADA DE BASALTO: columnas negras de seis caras apuntaladas con tablones.
                 0 entera · 1 rota (cascotes)
  reja.png       2 × 28×40  LA REJA DE KITO: barrotes de hierro con un candado de ámbar en su marco de madera de
                 mina. 0 cerrada · 1 abierta (levantada)
  parachoques.png  20×22    el tope del final de una vía: dos postes y un travesaño con muelles
  pilar.png      2 × 32×60  UN PILAR DE BASALTO de la Cámara del Ancla. 0 entero · 1 roto (un muñón y cascotes)
  kifaru.png     6 × 112×76  EL KIFARU DE BASALTO Y GEODA (jefe): un rinoceronte colosal de placas de basalto negro
                 con un cuerno-taladro de ámbar y cristales en el lomo. 0 y 1 anda · 2 AVISA (cabeza gacha,
                 escarba, el cuerno encendido) · 3 EMBISTE (estirado, el cuerno por delante) · 4 ABIERTO (las placas
                 del lomo levantadas: se le ve la geoda; atontado) · 5 abierto y golpeado (blanco)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_desfiladero import LUZ, ROCA, BASALTO, AMBAR, HIERRO, MADERA, BLANCO, _penasco, _cascotes  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "asterhaul", "galerias")


def aguja(f):
    W, H = 24, 30
    lz = Lienzo(W, H, s=6, semilla=10400 + f)
    cx = 12
    pie = lz.poligono([(cx - 7, 29), (cx + 7, 29), (cx + 5.5, 24), (cx - 5.5, 24)])
    lz.sombrear(pie, HIERRO[:5], 2.0, LUZ)
    lz.pintar(lz.circulo(cx - 4, 26.5, 0.7) + lz.circulo(cx + 4, 26.5, 0.7), HIERRO[5])
    # la palanca, inclinada hacia donde manda (norte: recta)
    punta = {0: (cx - 6.5, 9), 1: (cx, 6.5), 2: (cx + 6.5, 9)}[f]
    lz.sombrear(lz.trazo([(cx, 24), punta], 1.6, 1.3), HIERRO[1:], 0.8, LUZ)
    lz.sombrear(lz.circulo(punta[0], punta[1], 2.3), AMBAR[1:], 1.6, LUZ)
    # el disco con la flecha
    disco = lz.circulo(cx, 17, 5.2)
    lz.sombrear(disco, ["#3a2408", "#6a4612", "#9a6c20", "#c4963a", "#f0cc78"], 3.0, LUZ)
    lz.pintar((np.abs(np.hypot(lz.x - cx, lz.y - 17) - 5.0) < 0.5) * 1.0, "#3a2408", 0.8)
    d = {0: (-1, 0), 1: (0, -1), 2: (0, 1)}[f]
    p = (-d[1], d[0])
    flecha = lz.poligono([(cx + d[0] * 3.6, 17 + d[1] * 3.6), (cx + p[0] * 2.6 - d[0] * 0.4, 17 + p[1] * 2.6 - d[1] * 0.4),
                          (cx - p[0] * 2.6 - d[0] * 0.4, 17 - p[1] * 2.6 - d[1] * 0.4)])
    flecha = np.clip(flecha + lz.trazo([(cx - d[0] * 3.2, 17 - d[1] * 3.2), (cx, 17)], 1.1), 0, 1)
    lz.pintar(flecha, "#2a1206")
    return lz.sprite(contorno=0.5)


def mchimbaji(f):
    W, H = 28, 24
    lz = Lienzo(W, H, s=6, semilla=10420 + f)
    cx = 14
    blanco = f == 3
    coraza = BLANCO + BLANCO[-2:] if blanco else ["#1c1008", "#3a2210", "#5e3a18", "#865a24", "#b07e38", "#d8a858"]
    if f < 2:
        bola = lz.circulo(cx, 13, 10)
        lz.sombrear(bola, coraza, 7.0, LUZ)
        giro = f * 0.9
        # los élitros, enroscados: franjas de ámbar que dan la vuelta a la bola
        a = np.arctan2(lz.y - 13, lz.x - cx) + giro
        r = np.hypot(lz.x - cx, lz.y - 13)
        raya = bola * ((((a * 3 / np.pi) + r * 0.25) % 1) < 0.28) * (r > 3)
        lz.sombrear(raya, AMBAR[1:], 6.0, LUZ)
        lz.pintar((np.abs(r - 3.4) < 0.5) * bola, coraza[0], 0.8)
        cuerno = lz.poligono([(cx + np.cos(-0.6 - giro) * 9, 13 + np.sin(-0.6 - giro) * 9), (cx + np.cos(-0.9 - giro) * 13.5, 13 + np.sin(-0.9 - giro) * 13.5),
                              (cx + np.cos(-1.2 - giro) * 9, 13 + np.sin(-1.2 - giro) * 9)])
        lz.sombrear(cuerno, AMBAR[2:], 1.4, LUZ)
        lz.pintar(lz.trazo([(cx - 5, 7), (cx - 1, 5.4)], 0.45) * bola, coraza[5], 0.7)
        return lz.sprite(contorno=0.5)
    # panza arriba: las seis patas al aire, la barriga clara, el cuerno torcido y los ojos en espiral
    for k, lado in enumerate((-1, -1, -1, 1, 1, 1)):
        x0 = cx + lado * (3 + (k % 3) * 3.2)
        lz.sombrear(lz.trazo([(x0, 12), (x0 + lado * 2.4, 6 + (k % 3)), (x0 + lado * 1.4, 3 + (k % 3))], 1.2, 0.8), coraza[:5], 0.6, LUZ)
    cuerpo = lz.elipse(cx, 16, 11.5, 6.5)
    lz.sombrear(cuerpo, coraza, 4.5, LUZ)
    panza = lz.elipse(cx, 14.6, 8.5, 3.8)
    lz.sombrear(panza, (BLANCO + BLANCO[-1:]) if blanco else ["#6a4a2a", "#96704a", "#c09a6e", "#e0c094", "#f4e0b8"], 2.6, LUZ)
    for x in (cx - 4, cx, cx + 4):
        lz.pintar(lz.trazo([(x, 11.4), (x, 17.6)], 0.35) * panza, coraza[1], 0.5)
    lz.sombrear(lz.poligono([(cx + 10, 17), (cx + 13.6, 21.5), (cx + 9, 20)]), AMBAR[2:] if not blanco else BLANCO, 1.2, LUZ)
    for lado in (-1, 1):
        ox = cx + lado * 4
        lz.pintar(lz.circulo(ox, 21, 1.5), "#ffffff")
        lz.pintar(lz.trazo([(ox - 0.8, 20.4), (ox + 0.8, 21.6)], 0.3) + lz.trazo([(ox + 0.8, 20.4), (ox - 0.8, 21.6)], 0.3), "#140e18")
    return lz.sprite(contorno=0.5)


def geoda(f):
    W, H = 28, 30
    lz = Lienzo(W, H, s=6, semilla=10450 + f)
    cx = 14
    lz.sombrear(lz.elipse(cx, 27.5, 11, 2.2), ROCA[:4], 1.2, LUZ)
    piedra = lz.elipse(cx, 16, 11.5, 12) * (lz.ruido(4, 2, semilla=10451) > 0.1)
    piedra = np.clip(piedra + lz.elipse(cx, 16.5, 10.2, 10.6), 0, 1)
    lz.sombrear(piedra, ["#16141a", "#2c2a32", "#46444e", "#63616c", "#85838e", "#acaab4"], 7.0, LUZ, textura=lz.ruido(1.4, 3, semilla=10452), fuerza_tex=0.3)
    # la boca: un tajo en la piedra por el que se ven los cristales
    boca = lz.poligono([(cx - 6, 10), (cx + 1, 7), (cx + 7, 12), (cx + 6, 21), (cx - 1, 24), (cx - 7, 18)])
    lz.pintar(boca, "#1c0e06" if f == 0 else AMBAR[1])
    cristales = boca * (lz.ruido(1.9, 2, semilla=10453) > 0.42)
    lz.sombrear(cristales, (["#3a2a1a", "#5a4226", "#7a5a32", "#9a7440"] if f == 0 else AMBAR[2:]), 1.8, LUZ)
    lz.pintar(boca * (lz.ruido(0.9, 1, semilla=10454) > 0.82), "#c0a070" if f == 0 else "#ffffff", 0.9)
    lz.pintar(np.clip(boca - lz.poligono([(cx - 5, 11), (cx + 1, 8.4), (cx + 6, 12.6), (cx + 5, 20), (cx - 1, 22.6), (cx - 6, 17.6)]), 0, 1), "#0e0806", 0.7)
    if f == 1:
        lz.sumar_luz(lz.desenfocar(boca, 3.0), AMBAR[3], 1.1)
    return lz.sprite(contorno=0.5)


def barricada(f):
    W, H = 48, 44
    lz = Lienzo(W, H, s=5, semilla=10470 + f)
    if f == 1:
        _cascotes(lz, W, 41, BASALTO, 10475, 12)
        lz.sombrear(lz.trazo([(8, 40), (22, 36)], 1.6), MADERA, 0.8, LUZ)
        return lz.sprite(contorno=0.5)
    # columnas de basalto de seis caras, de distinta altura
    for i, (x, alto) in enumerate(((5, 22), (12, 30), (19, 36), (26, 33), (33, 38), (40, 28), (45, 20))):
        col = lz.poligono([(x - 4, 42), (x + 4, 42), (x + 4, 42 - alto), (x, 40 - alto), (x - 4, 42 - alto)])
        lz.sombrear(col, BASALTO, 3.0, LUZ, textura=lz.ruido(1.3, 2, semilla=10471 + i), fuerza_tex=0.25)
        lz.pintar(lz.trazo([(x, 40 - alto), (x, 42)], 0.35) * col, BASALTO[0], 0.6)
        lz.sombrear(lz.poligono([(x - 4, 42 - alto), (x, 40 - alto), (x + 4, 42 - alto), (x, 44 - alto)]), BASALTO[2:], 1.4, LUZ)
    # los tablones que la apuntalan, en aspa, con sus clavos
    for (a, b) in (((3, 34), (45, 16)), ((3, 14), (45, 32))):
        tabla = lz.trazo([a, b], 3.4)
        lz.sombrear(tabla, MADERA, 1.6, LUZ, textura=((lz.x % 5) < 0.7) * 1.0, fuerza_tex=-0.3)
        for t in (0.15, 0.85):
            lz.pintar(lz.circulo(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 0.8), HIERRO[4])
    return lz.sprite(contorno=0.5)


def reja(f):
    W, H = 28, 40
    lz = Lienzo(W, H, s=6, semilla=10490 + f)
    cx = 14
    for x in (3, 25):                                                 # el marco de madera de mina
        lz.sombrear(lz.poligono([(x - 2.2, 39), (x + 2.2, 39), (x + 2, 6), (x - 2, 6)]), MADERA, 1.8, LUZ, textura=((lz.y % 5) < 0.7) * 1.0, fuerza_tex=-0.3)
    lz.sombrear(lz.poligono([(0, 8), (28, 8), (28, 3), (0, 3)]), MADERA[1:], 2.0, LUZ, textura=((lz.x % 6) < 0.7) * 1.0, fuerza_tex=-0.3)
    y0, y1 = (10, 39) if f == 0 else (4, 15)                          # los barrotes (abierta: levantada)
    hueco = lz.poligono([(5.4, y1), (22.6, y1), (22.6, y0), (5.4, y0)])
    barras = hueco * ((((lz.x - 5.4) % 4.3) < 1.3) | (np.abs(lz.y - (y0 + 3)) < 0.8) | (np.abs(lz.y - (y1 - 3)) < 0.8))
    lz.sombrear(barras, HIERRO, 0.8, LUZ)
    if f == 0:
        lz.sombrear(lz.poligono([(cx - 2.6, 22), (cx + 2.6, 22), (cx + 2.6, 27), (cx - 2.6, 27)]), AMBAR[1:], 1.4, LUZ)
        lz.pintar((np.abs(np.hypot(lz.x - cx, lz.y - 21.6) - 2.0) < 0.55) * (lz.y < 22), HIERRO[4])
    return lz.sprite(contorno=0.5)


def parachoques():
    W, H = 20, 22
    lz = Lienzo(W, H, s=6, semilla=10510)
    for x in (4, 16):
        lz.sombrear(lz.poligono([(x - 2, 21), (x + 2, 21), (x + 1.8, 5), (x - 1.8, 5)]), MADERA, 1.6, LUZ)
    viga = lz.poligono([(1, 12), (19, 12), (19, 6), (1, 6)])
    lz.sombrear(viga, MADERA[1:], 2.4, LUZ, textura=((lz.x % 5) < 0.7) * 1.0, fuerza_tex=-0.3)
    franja = viga * (((lz.x + lz.y) % 6) < 3)
    lz.pintar(franja, AMBAR[2], 0.75)
    for x in (6, 14):
        lz.sombrear(lz.circulo(x, 9, 1.8), HIERRO[1:], 1.2, LUZ)
    return lz.sprite(contorno=0.5)


def pilar(f):
    W, H = 32, 60
    lz = Lienzo(W, H, s=5, semilla=10530 + f)
    cx = 16
    base = lz.poligono([(cx - 12, 59), (cx + 12, 59), (cx + 10.5, 53), (cx - 10.5, 53)])
    lz.sombrear(base, BASALTO, 2.4, LUZ)
    if f == 1:
        muñon = lz.poligono([(cx - 8, 53), (cx + 8, 53), (cx + 7, 44), (cx + 2, 40), (cx - 3, 45), (cx - 7.5, 42)])
        lz.sombrear(muñon, BASALTO[1:], 4.0, LUZ, textura=lz.ruido(1.3, 2, semilla=10531), fuerza_tex=0.3)
        _penasco(lz, cx - 11, 56, 3.4, 2.6, BASALTO, 10532)
        _penasco(lz, cx + 12, 57, 3.0, 2.2, BASALTO, 10533)
        return lz.sprite(contorno=0.5)
    fuste = lz.poligono([(cx - 8.5, 53), (cx + 8.5, 53), (cx + 7.5, 10), (cx - 7.5, 10)])
    lz.sombrear(fuste, BASALTO[1:], 6.0, LUZ, textura=((lz.x % 3.8) < 0.6) * 1.0, fuerza_tex=-0.3)
    for y in (20, 32, 44):
        lz.pintar(lz.trazo([(cx - 8.2, y), (cx + 8.2, y)], 0.5) * fuste, BASALTO[0], 0.8)
    veta = fuste * (np.abs(lz.ruido(6, 3, semilla=10534) - 0.5) < 0.018)
    lz.pintar(veta, AMBAR[2])
    lz.sumar_luz(lz.desenfocar(veta, 1.2), AMBAR[3], 0.4)
    cap = lz.poligono([(cx - 11, 11), (cx + 11, 11), (cx + 9.5, 4), (cx - 9.5, 4)])
    lz.sombrear(cap, BASALTO[2:], 2.4, LUZ)
    return lz.sprite(contorno=0.5)


def kifaru(f):
    W, H = 112, 76
    lz = Lienzo(W, H, s=4, semilla=10560 + min(f, 4))
    blanco = f == 5
    abierto = f >= 4
    piel = BLANCO + BLANCO[-2:] if blanco else BASALTO
    ambar = BLANCO if blanco else AMBAR[1:]
    paso = {0: 1.0, 1: -1.0}.get(f, 0.0)
    baja = 6.0 if f == 2 else (3.0 if f == 3 else (5.0 if abierto else 0.0))     # cuánto agacha la cabeza
    estira = 5.0 if f == 3 else 0.0
    base = 72
    # las patas de atrás (las del lado de allá, más oscuras) y de delante
    for (x, fase, lejos) in ((24, 1, True), (58, -1, True), (32, -1, False), (66, 1, False)):
        dx = paso * fase * 2.5 + (estira * (1 if x > 45 else -1))
        if f == 2 and x == 66:
            dx -= 5                                                   # escarba con la de delante
        pata = lz.poligono([(x - 6 + dx * 0.3, 46), (x + 6 + dx * 0.3, 46), (x + 5.4 + dx, base), (x - 5.4 + dx, base)])
        lz.sombrear(pata, piel[:5] if lejos else piel[1:], 4.0, LUZ)
        lz.pintar(lz.trazo([(x - 5 + dx, base - 1), (x + 5 + dx, base - 1)], 1.0), piel[0])
        if not lejos:
            lz.sombrear(lz.elipse(x + dx * 0.4, 49, 6.6, 4), piel[2:], 2.4, LUZ)             # la rodillera de basalto
    # el cuerpo: un tonel enorme de placas
    cuerpo = lz.elipse(44 - estira * 0.3, 40, 30 + estira, 19)
    lz.sombrear(cuerpo, piel, 13.0, LUZ, textura=lz.ruido(2.2, 3, semilla=10561), fuerza_tex=0.22)
    for x in (30, 44, 57):                                            # las juntas entre placas
        lz.pintar(lz.trazo([(x - 2, 23), (x, 40), (x - 3, 57)], 0.7) * cuerpo, piel[0], 0.7)
        lz.pintar(lz.trazo([(x - 0.8, 23), (x + 1.2, 40), (x - 1.8, 57)], 0.4) * cuerpo, piel[5], 0.35)
    lz.sombrear(lz.trazo([(14, 34), (9, 40), (10, 47)], 2.0, 1.2), piel[1:], 1.0, LUZ)        # la cola
    # el lomo: cristales de ámbar (cerrado) o las placas levantadas con la geoda al aire (abierto)
    if abierto:
        geoda_ = lz.elipse(42, 25, 16, 7)
        lz.pintar(geoda_, "#5a2406" if not blanco else "#ffffff")
        if not blanco:
            lz.sombrear(geoda_ * (lz.ruido(2.4, 2, semilla=10562) > 0.4), AMBAR[1:], 2.4, LUZ)
            lz.pintar(geoda_ * (lz.ruido(1.0, 1, semilla=10563) > 0.8), "#ffffff", 0.9)
            lz.sumar_luz(lz.desenfocar(geoda_, 4), AMBAR[3], 0.8)
        for lado in (-1, 1):
            placa = lz.poligono([(42 + lado * 15, 27), (42 + lado * 26, 6), (42 + lado * 30, 12), (42 + lado * 21, 31)])
            lz.sombrear(placa, piel[1:], 3.0, LUZ)
    else:
        for (x, alto, ancho) in ((28, 13, 4.5), (38, 18, 5.5), (48, 15, 5), (57, 10, 4)):
            pico = lz.poligono([(x - ancho, 26), (x + ancho, 26), (x + 1.5, 26 - alto)])
            lz.sombrear(pico, ambar, 2.4, LUZ)
            if f == 2 and not blanco:
                lz.sumar_luz(lz.desenfocar(pico, 2), AMBAR[3], 0.5)
    # la cabeza, acorazada, y el cuerno-taladro
    hx, hy = 74 + estira, 40 + baja
    cabeza = lz.poligono([(hx - 12, hy - 10), (hx + 4, hy - 9), (hx + 14, hy - 2), (hx + 15, hy + 6), (hx + 4, hy + 11), (hx - 10, hy + 9)])
    lz.sombrear(cabeza, piel[1:], 7.0, LUZ, textura=lz.ruido(1.8, 2, semilla=10564), fuerza_tex=0.2)
    lz.sombrear(lz.poligono([(hx - 12, hy - 10), (hx - 16, hy - 17), (hx - 7, hy - 12)]), piel[1:], 1.6, LUZ)   # la oreja
    lz.sombrear(lz.poligono([(hx - 4, hy - 10), (hx + 6, hy - 8), (hx + 3, hy - 3), (hx - 6, hy - 5)]), piel[2:], 2.0, LUZ)   # la placa de la frente
    ang = -0.5 if f != 3 else -0.15                                    # el cuerno: hacia arriba; embistiendo, hacia delante
    cx0, cy0 = hx + 12, hy - 1
    largo = 31
    punta = (cx0 + np.cos(ang) * largo, cy0 + np.sin(ang) * largo)
    pn = (-np.sin(ang), np.cos(ang))
    cuerno = lz.poligono([(cx0 + pn[0] * 6.5, cy0 + pn[1] * 6.5), punta, (cx0 - pn[0] * 6.5, cy0 - pn[1] * 6.5)])
    lz.sombrear(cuerno, ambar, 3.0, LUZ)
    for t in (0.15, 0.32, 0.5, 0.68, 0.85):                            # la rosca del taladro
        mx, my = cx0 + np.cos(ang) * largo * t, cy0 + np.sin(ang) * largo * t
        lz.pintar(lz.trazo([(mx + pn[0] * 6.5 * (1 - t), my + pn[1] * 6.5 * (1 - t)), (mx - pn[0] * 6.5 * (1 - t) + np.cos(ang) * 3, my - pn[1] * 6.5 * (1 - t) + np.sin(ang) * 3)], 0.5) * cuerno,
                  "#5a2406" if not blanco else "#c8c8d0", 0.8)
    if f in (2, 3) and not blanco:
        lz.sumar_luz(lz.desenfocar(cuerno, 3), AMBAR[3], 0.9)
    lz.sombrear(lz.poligono([(hx + 9, hy - 5), (hx + 12, hy - 11), (hx + 14, hy - 4)]), ambar, 1.2, LUZ)      # el cuernecito de atrás
    # el ojo: pequeño y de ámbar; atontado, en espiral
    ox, oy = hx + 3, hy + 1
    if abierto:
        lz.pintar(lz.circulo(ox, oy, 2.6), "#ffffff")
        lz.pintar(lz.trazo([(ox - 1.5, oy - 1.2), (ox + 1.5, oy + 1.2)], 0.45) + lz.trazo([(ox + 1.5, oy - 1.2), (ox - 1.5, oy + 1.2)], 0.45), "#140e18")
    else:
        lz.pintar(lz.circulo(ox, oy, 2.2), "#140e18")
        lz.pintar(lz.circulo(ox, oy, 1.4), AMBAR[3] if f < 2 else "#ff5a20")
        lz.pintar(lz.trazo([(ox - 3.4, oy - 3.6), (ox + 2.6, oy - 1.8)], 0.8), piel[0])                         # el ceño
    lz.pintar(lz.circulo(hx + 12.5, hy + 4.5, 0.9), piel[0])           # el ollar
    if f == 2 and not blanco:                                          # el resoplido
        lz.pintar(lz.elipse(hx + 19, hy + 6, 3.4, 1.8) + lz.elipse(hx + 23, hy + 9, 2.4, 1.3), "#d8c8b8", 0.6)
    return lz.sprite(contorno=0.4)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    tira("aguja", aguja, 3)
    tira("mchimbaji", mchimbaji, 4)
    tira("geoda", geoda, 2)
    tira("barricada", barricada, 2)
    tira("reja", reja, 2)
    tira("pilar", pilar, 2)
    tira("kifaru", kifaru, 6)
    Image.fromarray(parachoques(), "RGBA").save(os.path.join(SALIDA, "parachoques.png"))
    print("Galerías pintadas en", SALIDA)
