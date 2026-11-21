"""EL JARDÍN DE LOS FAROLES (el Valle del Ocaso, el camino del este de Jioni), pintado con detalle.

    python3 herramientas/pintar_jardin.py

Genera en arte/mundos/ocaso/jardin/:
  fuente.png    24×44      EL PRISMA SOLAR: una columna de arenisca con un gran cristal ámbar que recoge el atardecer
  espejo.png    4 × 26×34  UN ESPEJO DE ÁNGULO: una luna de bronce en diagonal sobre su peana. 0 «/» · 1 «\»
                           · 2-3 lo mismo con el rayo encima (encendido)
  prisma.png    8 × 22×32  UN PRISMA DE CRISTAL: deja pasar la luz dorada y saca un haz VIOLETA por una cara (la que
                           brilla: 0 norte · 1 este · 2 sur · 3 oeste). 4-7 lo mismo, con luz
  verja.png     2 × 20×60  LA VERJA DEL INVERNADERO, con el disco de sol que abre la luz dorada. 0 cerrada · 1 abierta
  celosia.png   64×44      LA CELOSÍA ILUSORIA: parece un seto con celosía; con luz violeta, se deshace
  polilla.png   4 × 16×16  UNA POLILLA DE PAPEL: 0-1 vuela · 2 posada (alas plegadas) · 3 golpeada
  mondo.png     6 × 56×48  MONDO, EL SERVAL DE MIL REFLEJOS (jefe): bronce y orejas de cristal dorado. 0 sentado
                           · 1 salta · 2 zarpazo · 3 ATURDIDO (brilla con el rayo) · 4 aturdido y golpeado · 5 vencido
  espejo_alto.png 2 × 24×44 UN ESPEJO DEL INVERNADERO: luna ovalada en marco de bronce. 0 quieto · 1 echa su rayo
  peso.png      16×22      LA PESA DEL ESTE: una pesa de bronce con una luna creciente grabada
  pergola.png   64×58      LA PÉRGOLA DE ENTRADA: vigas de madera y una parra de flores de farol
  linterna.png  16×30      UNA LINTERNA DE PIEDRA del jardín, con su luz quieta
  pabellon.png  96×72      EL PABELLÓN DEL TÉ: tejado curvo de tejas moradas, celosías y faroles
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_mirador import LUZ, ARENISCA, BRONCE, AMBAR, BLANCO  # noqa: E402
from pintar_jioni import MADERA  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "ocaso", "jardin")
VIOLETA = ["#2a0e4a", "#4a1c78", "#7a3cb0", "#a86ce0", "#d4b0f8", "#f4e8ff"]
CRISTAL = ["#3a2a5a", "#5a4a8a", "#8a7ab8", "#c0b4e0", "#ece6fa"]
SETO = ["#0c1418", "#14242a", "#1e3436", "#2c4a44", "#3e6050", "#58785a"]
PAPEL = ["#6a5a5a", "#9a8a84", "#c8b8a8", "#e8dcc8", "#fff6e4"]
TEJA = ["#1a0c26", "#2e1640", "#46245c", "#62367a", "#82509a"]
GRIS = ["#3a3640", "#5a5662", "#7e7a86", "#a29ea8", "#c6c2ca"]


def peana(lz, cx, base, ancho=7, alto=7):
    p = lz.poligono([(cx - ancho, base), (cx + ancho, base), (cx + ancho - 2, base - alto), (cx - ancho + 2, base - alto)])
    lz.sombrear(p, ARENISCA[1:], 3.0, LUZ)
    lz.pintar(lz.trazo([(cx - ancho + 2, base - alto + 1), (cx + ancho - 2, base - alto + 1)], 0.5), ARENISCA[5], 0.6)


def fuente():
    W, H = 24, 44
    lz = Lienzo(W, H, s=4, semilla=15000)
    peana(lz, 12, 43, 9, 6)
    col = lz.poligono([(8, 38), (16, 38), (15, 18), (9, 18)])
    lz.sombrear(col, ARENISCA, 3.0, LUZ, textura=((lz.y % 6) < 0.8) * 1.0, fuerza_tex=-0.2)
    copa = lz.poligono([(5, 18), (19, 18), (16, 14), (8, 14)])
    lz.sombrear(copa, BRONCE, 2.0, LUZ)
    gema = lz.poligono([(12, 1), (18, 8), (12, 15), (6, 8)])
    lz.sombrear(gema, AMBAR, 3.0, LUZ)
    lz.pintar(lz.trazo([(12, 1), (12, 15)], 0.4), AMBAR[4], 0.6)
    lz.pintar(lz.trazo([(6, 8), (18, 8)], 0.4), AMBAR[1], 0.5)
    lz.sumar_luz(lz.desenfocar(gema, 6), AMBAR[3], 1.0)
    return lz.sprite(contorno=0.4)


def espejo(f):
    W, H = 26, 34
    lz = Lienzo(W, H, s=4, semilla=15010 + f)
    barra = f % 2 == 0                       # «/»
    lleno = f >= 2
    peana(lz, 13, 33)
    lz.pintar(lz.trazo([(13, 26), (13, 20)], 1.4), BRONCE[1])
    # la luna, en diagonal: un marco de bronce alargado y su cara de espejo
    a, b = ((4, 21), (22, 5)) if barra else ((4, 5), (22, 21))
    marco = lz.trazo([a, b], 4.2)
    lz.sombrear(marco, BRONCE, 2.0, LUZ)
    cara = lz.trazo([a, b], 2.6)
    lz.pintar(cara, "#fff0d0" if lleno else "#9a7c6a")
    lz.pintar(cara * (lz.y < 13), "#ffffff" if lleno else "#d0b8a4", 0.5)
    for p in (a, b):
        lz.sombrear(lz.circulo(p[0], p[1], 1.6), BRONCE[2:], 1.0, LUZ)
    if lleno:
        lz.sumar_luz(lz.desenfocar(cara, 6), AMBAR[3], 1.0)
    return lz.sprite(contorno=0.4)


def prisma(f):
    W, H = 22, 32
    lz = Lienzo(W, H, s=4, semilla=15020 + f)
    lado = f % 4
    lleno = f >= 4
    peana(lz, 11, 31, 8, 6)
    cuerpo = lz.poligono([(11, 3), (19, 22), (3, 22)])
    lz.sombrear(cuerpo, CRISTAL, 4.0, LUZ)
    lz.pintar(lz.trazo([(11, 3), (11, 22)], 0.4), CRISTAL[4], 0.5)
    # la cara violeta: hacia donde saca el haz
    cara = {0: lz.poligono([(11, 4), (15, 13), (7, 13)]), 1: lz.poligono([(12, 6), (19, 21), (14, 21)]),
            2: lz.poligono([(5, 18), (17, 18), (18, 22), (4, 22)]), 3: lz.poligono([(10, 6), (8, 21), (3, 21)])}[lado]
    lz.sombrear(cara, VIOLETA[1:], 2.0, LUZ)
    if lleno:
        lz.sumar_luz(lz.desenfocar(cuerpo, 5), AMBAR[3], 0.7)
        lz.sumar_luz(lz.desenfocar(cara, 5), VIOLETA[4], 1.0)
    return lz.sprite(contorno=0.4)


def verja(f):
    W, H = 20, 60
    lz = Lienzo(W, H, s=4, semilla=15030 + f)
    for x in (3, 17):
        poste = lz.poligono([(x - 2.5, 59), (x + 2.5, 59), (x + 2, 4), (x - 2, 4)])
        lz.sombrear(poste, ARENISCA, 2.0, LUZ)
        lz.sombrear(lz.circulo(x, 4, 2.6), BRONCE[1:], 1.0, LUZ)
    if f == 0:
        for k in range(6):
            y = 10 + k * 8
            lz.pintar(lz.trazo([(5, y), (15, y + 4)], 0.9), BRONCE[2])
        for x in (7, 10, 13):
            lz.pintar(lz.trazo([(x, 8), (x, 58)], 0.8), BRONCE[1])
        disco = lz.circulo(10, 30, 5)
        lz.sombrear(disco, BRONCE, 2.0, LUZ)
        lz.pintar(lz.circulo(10, 30, 2.6), AMBAR[2])
        for k in range(8):
            ang = k * np.pi / 4
            lz.pintar(lz.trazo([(10 + np.cos(ang) * 3, 30 + np.sin(ang) * 3), (10 + np.cos(ang) * 4.6, 30 + np.sin(ang) * 4.6)], 0.4), AMBAR[4])
    else:
        lz.pintar(lz.trazo([(5, 57), (15, 57)], 1.0), BRONCE[2])      # (la verja, recogida en el suelo)
        lz.sumar_luz(lz.desenfocar(lz.circulo(10, 56, 3), 4), AMBAR[3], 0.6)
    return lz.sprite(contorno=0.4)


def celosia():
    W, H = 64, 44
    lz = Lienzo(W, H, s=3, semilla=15040)
    seto = lz.poligono([(0, 43), (64, 43), (64, 8), (0, 8)]) * (lz.ruido(2.0, 3, semilla=15041) * 6 + lz.y > 10)
    lz.sombrear(seto, SETO, 6.0, LUZ, textura=lz.ruido(1.0, 3, semilla=15042), fuerza_tex=0.35)
    rombo = ((np.abs(((lz.x + lz.y) % 10) - 5) < 0.6) | (np.abs(((lz.x - lz.y) % 10) - 5) < 0.6)) * seto * (lz.y > 14) * (lz.y < 38)
    lz.pintar(rombo, VIOLETA[2], 0.8)
    lz.sumar_luz(lz.desenfocar(rombo * 1.0, 2), VIOLETA[3], 0.4)
    lz.pintar(seto * (lz.ruido(1.5, 2, semilla=15043) > 0.72), "#ffd0f0", 0.35)   # flores de farol
    return lz.sprite(contorno=0.4)


def polilla(f):
    W, H = 16, 16
    lz = Lienzo(W, H, s=6, semilla=15050 + f)
    rampa = BLANCO if f == 3 else PAPEL
    if f == 2:
        ala = lz.poligono([(8, 5), (13, 13), (3, 13)])
        lz.sombrear(ala, rampa, 2.0, LUZ)
        lz.pintar(lz.trazo([(8, 5), (8, 13)], 0.4), PAPEL[1], 0.8)
    else:
        abre = 6.5 if f == 0 else 4.5
        for lado in (-1, 1):
            ala = lz.poligono([(8, 7), (8 + lado * abre, 2 + (f == 1) * 2), (8 + lado * (abre + 1), 9), (8 + lado * 3, 13)])
            lz.sombrear(ala, rampa, 2.0, LUZ)
            lz.pintar(lz.trazo([(8, 8), (8 + lado * (abre - 1), 5)], 0.3), PAPEL[1], 0.8)   # (las letras del papel)
            lz.pintar(lz.trazo([(8 + lado * 2, 10), (8 + lado * (abre - 1), 8)], 0.3), PAPEL[1], 0.6)
    lz.sombrear(lz.elipse(8, 9, 1.3, 3.4), ["#2a1a1a", "#4a3430", "#6a5048"], 1.0, LUZ)
    lz.pintar(lz.trazo([(7.5, 6), (6, 3)], 0.3), "#4a3430")
    lz.pintar(lz.trazo([(8.5, 6), (10, 3)], 0.3), "#4a3430")
    return lz.sprite(contorno=0.4)


def mondo(f):
    W, H = 56, 48
    lz = Lienzo(W, H, s=3, semilla=15060 + f)
    vencido = f == 5
    pelo = GRIS if vencido else (BLANCO if f == 4 else BRONCE)
    cx, base = 28, 44
    if f == 3 or f == 4 or f == 5:
        # ATURDIDO: tumbado de lado, con estrellitas de luz
        cuerpo = lz.elipse(cx, base - 8, 16, 7)
        lz.sombrear(cuerpo, pelo, 5.0, LUZ, textura=((lz.ruido(1.2, 2, semilla=15061) > 0.6) * 1.0), fuerza_tex=-0.3)
        cabeza = lz.elipse(cx + 15, base - 12, 7, 6)
        lz.sombrear(cabeza, pelo, 3.0, LUZ)
        for dx in (12, 19):
            oreja = lz.poligono([(cx + dx - 3, base - 16), (cx + dx + 3, base - 16), (cx + dx + 1, base - 27)])
            lz.sombrear(oreja, GRIS if vencido else AMBAR, 2.0, LUZ)
        cola = lz.curva((cx - 15, base - 8), (cx - 22, base - 4), (cx - 26, base - 12), (cx - 24, base - 18))
        lz.pintar(lz.trazo(cola, 2.2, 1.4), pelo[2])
        for dx in (17, 21):
            lz.pintar(lz.trazo([(cx + dx - 1, base - 13), (cx + dx + 1, base - 11)], 0.5), "#2a160c")   # ojos en X
            lz.pintar(lz.trazo([(cx + dx + 1, base - 13), (cx + dx - 1, base - 11)], 0.5), "#2a160c")
        if f == 3:
            lz.sumar_luz(lz.desenfocar(cuerpo, 8), AMBAR[3], 0.8)
            for (x, y) in ((cx + 8, base - 30), (cx + 18, base - 34), (cx + 26, base - 29)):
                lz.pintar(lz.circulo(x, y, 1.3), AMBAR[4])
        return lz.sprite(contorno=0.4)
    salta = f == 1
    zarpa = f == 2
    dy = -6 if salta else 0
    # las patas
    for (x, largo) in ((cx - 10, 10), (cx - 5, 10), (cx + 6, 11), (cx + 11, 11)):
        if salta:
            pata = lz.trazo([(x, base - 14 + dy), (x + (6 if x > cx else -7), base - 6 + dy)], 2.0, 1.4)
        else:
            pata = lz.trazo([(x, base - 14), (x, base - 14 + largo)], 2.0, 1.5)
        lz.sombrear(pata, pelo, 1.0, LUZ)
    cuerpo = lz.elipse(cx, base - 18 + dy, 15, 7, -8 if salta else 0)
    manchas = (lz.ruido(1.4, 2, semilla=15062) > 0.62) * 1.0
    lz.sombrear(cuerpo, pelo, 5.0, LUZ, textura=manchas, fuerza_tex=-0.35)
    cola = lz.curva((cx - 14, base - 20 + dy), (cx - 22, base - 26 + dy), (cx - 24, base - 34 + dy), (cx - 20, base - 38 + dy))
    lz.pintar(lz.trazo(cola, 2.4, 1.6), pelo[3])
    lz.pintar(lz.trazo(cola[-6:], 2.0, 1.4), pelo[0])          # la punta oscura de la cola
    hx, hy = cx + 14, base - 26 + dy
    cabeza = lz.elipse(hx, hy, 7, 6)
    lz.sombrear(cabeza, pelo, 3.0, LUZ, textura=manchas, fuerza_tex=-0.2)
    lz.sombrear(lz.elipse(hx + 4, hy + 3, 3.2, 2.4), pelo[2:], 1.0, LUZ)      # el hocico
    for dx in (-3, 4):                                         # las orejas enormes, de cristal dorado
        oreja = lz.poligono([(hx + dx - 3.5, hy - 4), (hx + dx + 3.5, hy - 4), (hx + dx + 0.5, hy - 17)])
        lz.sombrear(oreja, AMBAR, 2.5, LUZ)
        lz.pintar(lz.poligono([(hx + dx - 1.5, hy - 5), (hx + dx + 1.5, hy - 5), (hx + dx + 0.3, hy - 13)]), AMBAR[4], 0.6)
    for dx in (1, 6):
        lz.pintar(lz.circulo(hx + dx, hy - 1, 1.2), "#fff0b0")
        lz.pintar(lz.circulo(hx + dx, hy - 1, 0.5), "#2a160c")
    if zarpa:
        brazo = lz.trazo([(cx + 10, base - 16), (cx + 22, base - 22), (cx + 26, base - 18)], 2.2, 1.6)
        lz.sombrear(brazo, pelo, 1.0, LUZ)
        for k in range(3):
            lz.pintar(lz.trazo([(cx + 26, base - 19 + k * 1.5), (cx + 29, base - 21 + k * 2)], 0.4), "#fff6e4")
    # el collar de cristal: un rombo que brilla
    gema = lz.poligono([(hx - 4, hy + 5), (hx - 2, hy + 3), (hx, hy + 5), (hx - 2, hy + 8)])
    lz.sombrear(gema, CRISTAL, 1.0, LUZ)
    return lz.sprite(contorno=0.4)


def espejo_alto(f):
    W, H = 24, 44
    lz = Lienzo(W, H, s=4, semilla=15070 + f)
    for x in (6, 18):
        lz.pintar(lz.trazo([(x, 34), (x - (2 if x < 12 else -2), 43)], 1.2), BRONCE[1])
    marco = lz.elipse(12, 18, 10, 16)
    lz.sombrear(marco, BRONCE, 3.0, LUZ)
    cara = lz.elipse(12, 18, 7.6, 13.4)
    lz.pintar(cara, "#fff0d0" if f else "#7a6a8a")
    lz.pintar(cara * (lz.y < 12) * (lz.x < 12), "#ffffff" if f else "#b0a0c0", 0.5)
    lz.sombrear(lz.circulo(12, 2, 2), AMBAR[1:], 1.0, LUZ)
    if f:
        lz.sumar_luz(lz.desenfocar(cara, 7), AMBAR[3], 1.1)
    return lz.sprite(contorno=0.4)


def peso():
    W, H = 16, 22
    lz = Lienzo(W, H, s=5, semilla=15080)
    gancho = np.clip(lz.circulo(8, 3.5, 2.6) - lz.circulo(8, 3.5, 1.4), 0, 1)
    lz.sombrear(gancho, BRONCE[1:], 1.0, LUZ)
    cuerpo = lz.poligono([(4, 6), (12, 6), (14, 20), (2, 20)])
    lz.sombrear(cuerpo, BRONCE, 4.0, LUZ)
    lz.pintar(lz.trazo([(3, 9), (13, 9)], 0.4), BRONCE[1], 0.8)
    luna = np.clip(lz.circulo(8, 14, 3.4) - lz.circulo(9.6, 13, 2.8), 0, 1)
    lz.pintar(luna, CRISTAL[4])
    lz.sumar_luz(lz.desenfocar(luna, 2), VIOLETA[4], 0.7)
    return lz.sprite(contorno=0.4)


def pergola():
    W, H = 64, 58
    lz = Lienzo(W, H, s=3, semilla=15090)
    for x in (6, 58):
        poste = lz.poligono([(x - 2.5, 57), (x + 2.5, 57), (x + 2, 14), (x - 2, 14)])
        lz.sombrear(poste, MADERA, 2.0, LUZ, textura=((lz.y % 7) < 0.7) * 1.0, fuerza_tex=-0.15)
        lz.sombrear(lz.poligono([(x - 4, 57), (x + 4, 57), (x + 3, 52), (x - 3, 52)]), ARENISCA[1:], 2.0, LUZ)
    for y in (10, 15):
        viga = lz.poligono([(0, y), (64, y), (64, y + 3), (0, y + 3)])
        lz.sombrear(viga, MADERA, 1.5, LUZ)
    for x in range(4, 64, 8):
        lz.sombrear(lz.poligono([(x, 6), (x + 3, 6), (x + 3, 19), (x, 19)]), MADERA[1:], 1.0, LUZ)
    parra = (lz.ruido(2.2, 3, semilla=15091) > 0.5) * (lz.y < 24 + lz.ruido(4, 2, semilla=15092) * 16) * (lz.y > 4)
    lz.sombrear(parra * 1.0, SETO[1:], 3.0, LUZ, textura=lz.ruido(0.8, 2, semilla=15093), fuerza_tex=0.3)
    lianas = sum(lz.trazo([(x, 18), (x + 1, 30 + (x * 7) % 14)], 0.6) for x in (5, 59))
    lz.pintar(np.clip(lianas, 0, 1), SETO[3])
    flor = parra * (lz.ruido(0.9, 2, semilla=15094) > 0.74)
    lz.pintar(flor, AMBAR[3])
    lz.sumar_luz(lz.desenfocar(flor, 3), AMBAR[2], 0.6)
    return lz.sprite(contorno=0.4)


def linterna():
    W, H = 16, 30
    lz = Lienzo(W, H, s=5, semilla=15100)
    peana(lz, 8, 29, 6, 4)
    lz.sombrear(lz.poligono([(6, 25), (10, 25), (10, 17), (6, 17)]), ARENISCA, 1.5, LUZ)
    caja = lz.poligono([(3, 17), (13, 17), (13, 9), (3, 9)])
    lz.sombrear(caja, ARENISCA, 2.0, LUZ)
    hueco = lz.poligono([(5.5, 15.5), (10.5, 15.5), (10.5, 10.5), (5.5, 10.5)])
    lz.pintar(hueco, AMBAR[3])
    lz.sumar_luz(lz.desenfocar(hueco, 4), AMBAR[3], 0.9)
    techo = lz.poligono([(0, 9), (16, 9), (11, 3), (5, 3)])
    lz.sombrear(techo, ARENISCA, 2.0, LUZ)
    lz.sombrear(lz.circulo(8, 2.4, 1.6), ARENISCA[2:], 1.0, LUZ)
    return lz.sprite(contorno=0.4)


def pabellon():
    W, H = 96, 72
    lz = Lienzo(W, H, s=3, semilla=15110)
    zocalo = lz.poligono([(8, 71), (88, 71), (86, 62), (10, 62)])
    lz.sombrear(zocalo, ARENISCA[1:], 3.0, LUZ)
    for x in (16, 36, 60, 80):
        col = lz.poligono([(x - 2.5, 63), (x + 2.5, 63), (x + 2.5, 32), (x - 2.5, 32)])
        lz.sombrear(col, MADERA, 1.5, LUZ)
    for (x0, x1) in ((19, 33), (63, 77)):                         # las celosías
        pan = lz.poligono([(x0, 62), (x1, 62), (x1, 36), (x0, 36)])
        lz.pintar(pan, "#2a1630")
        red = pan * (((np.abs(((lz.x + lz.y) % 6) - 3) < 0.45) | (np.abs(((lz.x - lz.y) % 6) - 3) < 0.45)))
        lz.pintar(red, MADERA[3])
        lz.sumar_luz(lz.desenfocar(pan, 4), AMBAR[2], 0.35)
    puerta = lz.poligono([(39, 62), (57, 62), (57, 38), (39, 38)])
    lz.pintar(puerta, "#3a1a28")
    lz.sumar_luz(lz.desenfocar(puerta, 6), AMBAR[3], 0.5)
    lz.pintar(lz.poligono([(41, 62), (55, 62), (55, 41), (41, 41)]) * ((lz.x % 7) < 0.8), MADERA[2])
    # el tejado curvo, de tejas moradas, con las puntas hacia arriba
    techo = lz.poligono([(0, 34), (96, 34), (82, 14), (14, 14)]) + lz.poligono([(0, 34), (6, 34), (-2, 26)]) + lz.poligono([(90, 34), (96, 34), (98, 26)])
    techo = np.clip(techo, 0, 1)
    lz.sombrear(techo, TEJA, 5.0, LUZ, textura=((lz.x % 5) < 0.8) * 1.0, fuerza_tex=-0.25)
    lz.pintar(lz.trazo([(0, 33), (96, 33)], 1.2), BRONCE[2])
    cumbre = lz.poligono([(10, 16), (86, 16), (80, 4), (16, 4)])
    lz.sombrear(cumbre, TEJA, 3.0, LUZ, textura=((lz.x % 5) < 0.8) * 1.0, fuerza_tex=-0.25)
    lz.pintar(lz.trazo([(14, 5), (82, 5)], 1.0), BRONCE[3])
    for x in (12, 84):                                            # los faroles de las esquinas
        f = lz.elipse(x, 40, 3, 4)
        lz.pintar(f, AMBAR[3])
        lz.sumar_luz(lz.desenfocar(f, 4), AMBAR[3], 0.9)
        lz.pintar(lz.trazo([(x, 34), (x, 36)], 0.4), BRONCE[1])
    return lz.sprite(contorno=0.4)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    def uno(nombre, fn):
        Image.fromarray(fn(), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    uno("fuente", fuente)
    tira("espejo", espejo, 4)
    tira("prisma", prisma, 8)
    tira("verja", verja, 2)
    uno("celosia", celosia)
    tira("polilla", polilla, 4)
    tira("mondo", mondo, 6)
    tira("espejo_alto", espejo_alto, 2)
    uno("peso", peso)
    uno("pergola", pergola)
    uno("linterna", linterna)
    uno("pabellon", pabellon)
    print("Jardín pintado en", SALIDA)
