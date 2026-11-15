"""MJI-JIWE, LA CIUDAD DEL CRÁTER (Asterhaul), pintada con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_mji_jiwe.py

Genera en arte/mundos/asterhaul/mji_jiwe/:
  gran_forja.png  144×132    LA GRAN FORJA DE MHUNZI: nave de sillares con la boca de la forja en arco (dentro, un
                  rescoldo), tejado de cobre a dos aguas, la gran chimenea con el fuelle de cuero, el yunque
                  delante y barras de hierro apoyadas
  casa.png        2 × 76×80  UNA CASA-TALLER de artesano: sillares, tejado de tablas, puerta, ventana y su banco
                  de trabajo. 0 de cantero (tejado rojizo, bloque a medio tallar) · 1 de afinador (tejado azulado,
                  diapasones colgados)
  mercado.png     2 × 112×88 EL MERCADO DE LA ESCORIA (el puesto de Chuma): 0 cerrado (el toldo recogido, el
                  mostrador tapado con una lona) · 1 abierto (toldo a rayas, lingotes, herramientas, un farol)
  horno.png       2 × 28×48  UN HORNO-DIAPASÓN de calle: horno de piedra abovedado con una horquilla de hierro
                  arriba. 0 frío · 1 encendido (fuego de ámbar en la boca, la horquilla vibra)
  yunque.png      2 × 24×26  UN YUNQUE DE MEMORIA: yunque de hierro sobre un tocón. 0 dormido · 1 despierto
                  (una runa de ámbar encendida en el costado, chispas)
  diapason.png    72×116     EL GRAN DIAPASÓN: una horquilla colosal de hierro meteórico sobre un pie de basalto,
                  con el corazón de ámbar apagado y argollas para las cadenas
  verja.png       56×64      UNA VERJA cerrada en su arco de sillares (las salidas que aún no se abren)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_desfiladero import LUZ, ROCA, BASALTO, AMBAR, HIERRO, MADERA, TEJA, _grietas_ambar  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "asterhaul", "mji_jiwe")
COBRE = ["#2a1208", "#5a2a12", "#8e4a20", "#c07a3a", "#e8ac62", "#ffe0a0"]
PIZARRA = ["#161a24", "#262c3c", "#3a4258", "#525c78", "#6e7a98", "#909cb8"]
CUERO = ["#24140c", "#40261a", "#5e3a26", "#7c5234", "#9c6c46"]
LONA = ["#5a4a36", "#7e6a4e", "#a08a68", "#c0aa86", "#dcc8a4"]


def _sillares(lz, masa, semilla, rampa=None, alto=8, largo=14):
    rampa = rampa or ROCA[1:]
    hilada = np.floor(lz.y / alto)
    junta = ((lz.y % alto) < 0.9) | (((lz.x + hilada * (largo / 2)) % largo) < 0.9)
    lz.sombrear(masa, rampa, 30.0, LUZ, textura=lz.ruido(1.8, 3, semilla=semilla), fuerza_tex=0.3)
    lz.pintar(masa * junta, ROCA[0], 0.7)
    lz.pintar(masa * (((lz.y - 1) % alto) < 0.5) * (1 - junta), ROCA[5], 0.3)


def _tejado(lz, cx, cumbre, alero, medio, rampa, grosor=7):
    """Dos aguas vistas de frente: dos alas con tablas (o planchas) y la cumbrera."""
    for lado in (-1, 1):
        ala = lz.poligono([(cx, cumbre), (cx + lado * medio, alero), (cx + lado * medio, alero + grosor), (cx, cumbre + grosor + 1)])
        tabla = (((lz.x * 0.82 * lado + lz.y) % 7) < 0.9) * 1.0
        lz.sombrear(ala, rampa, 5.0, LUZ, textura=tabla, fuerza_tex=-0.45)
        lz.pintar(lz.trazo([(cx, cumbre + grosor + 1), (cx + lado * medio, alero + grosor)], 0.7) * ala, rampa[0], 0.8)
    lz.sombrear(lz.trazo([(cx, cumbre - 0.5), (cx, cumbre + grosor + 1)], 1.6), rampa[3:], 0.8, LUZ)


def _ventana(lz, x0, y0, x1, y1, luz_dentro=0.75):
    hueco = lz.poligono([(x0, y1), (x1, y1), (x1, y0), (x0, y0)])
    lz.pintar(hueco, "#2a1206")
    lz.pintar(hueco, AMBAR[3], luz_dentro)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    lz.pintar(lz.trazo([(mx, y0), (mx, y1)], 0.5) + lz.trazo([(x0, my), (x1, my)], 0.5), MADERA[0])
    lz.sombrear(lz.trazo([(x0 - 1.5, y0 - 1), (x1 + 1.5, y0 - 1)], 1.6), ROCA[3:], 0.8, LUZ)
    lz.sombrear(lz.trazo([(x0 - 1.5, y1 + 1.4), (x1 + 1.5, y1 + 1.4)], 1.8), ROCA[3:], 0.9, LUZ)
    if luz_dentro > 0.3:
        lz.sumar_luz(lz.desenfocar(hueco, 3), AMBAR[3], 0.4)


def _yunque(lz, cx, base, e=1.0, rampa=None):
    rampa = rampa or HIERRO
    tocon = lz.poligono([(cx - 5 * e, base), (cx + 5 * e, base), (cx + 4.4 * e, base - 6 * e), (cx - 4.4 * e, base - 6 * e)])
    lz.sombrear(tocon, MADERA, 2.4 * e, LUZ, textura=((lz.x % 2.2) < 0.5) * 1.0, fuerza_tex=-0.25)
    lz.sombrear(lz.elipse(cx, base - 6 * e, 4.6 * e, 1.3 * e), MADERA[2:], 1.0, LUZ)
    pie = lz.poligono([(cx - 3.4 * e, base - 6 * e), (cx + 3.4 * e, base - 6 * e), (cx + 2 * e, base - 10 * e), (cx - 2 * e, base - 10 * e)])
    lz.sombrear(pie, rampa, 1.6 * e, LUZ)
    cara = lz.poligono([(cx - 6 * e, base - 10 * e), (cx + 5 * e, base - 10 * e), (cx + 9.5 * e, base - 13 * e), (cx + 5 * e, base - 14.5 * e), (cx - 6 * e, base - 14.5 * e)])
    lz.sombrear(cara, rampa[1:], 2.2 * e, LUZ)
    lz.pintar(lz.trazo([(cx - 6 * e, base - 14.3 * e), (cx + 5 * e, base - 14.3 * e)], 0.4), rampa[-1], 0.8)
    return cara


def gran_forja():
    W, H = 144, 132
    lz = Lienzo(W, H, s=4, semilla=10200)
    cx = 66
    # la gran chimenea, detrás a la derecha, con el fuelle de cuero colgado
    chim = lz.poligono([(100, 70), (122, 70), (119, 6), (103, 6)])
    _sillares(lz, chim, 10201, ROCA[1:], 7, 11)
    lz.sombrear(lz.poligono([(100, 8), (122, 8), (124, 2), (98, 2)]), ROCA[3:], 2.0, LUZ)
    lz.pintar(lz.elipse(111, 3, 8, 1.6), "#140a06")
    fuelle = lz.poligono([(124, 96), (142, 90), (142, 110), (124, 104)])
    lz.sombrear(fuelle, CUERO, 4.0, LUZ, textura=((lz.x % 3.4) < 0.7) * 1.0, fuerza_tex=-0.4)
    lz.sombrear(lz.trazo([(124, 95), (124, 105)], 1.6), MADERA, 0.8, LUZ)
    lz.sombrear(lz.trazo([(142, 89), (142, 111)], 1.6), MADERA, 0.8, LUZ)
    lz.sombrear(lz.trazo([(116, 100), (124, 100)], 1.4), HIERRO, 0.7, LUZ)
    # los muros
    muro = lz.poligono([(10, 128), (122, 128), (122, 62), (10, 62)])
    _sillares(lz, muro, 10202)
    _grietas_ambar(lz, muro * (lz.y > 104), 10203, 0.012)
    for x in (10, 116):
        esq = lz.poligono([(x, 128), (x + 6, 128), (x + 6, 62), (x, 62)])
        lz.sombrear(esq, ROCA[2:], 3.0, LUZ)
        lz.pintar(esq * ((lz.y % 8) < 0.9), ROCA[0], 0.7)
    # la boca de la forja: un arco grande, oscuro, con un rescoldo al fondo
    boca = lz.poligono([(44, 128), (88, 128), (88, 96), (80, 84), (66, 79), (52, 84), (44, 96)])
    lz.pintar(boca, "#0e0806")
    lz.pintar(boca * (lz.y > 112), "#1c100a")
    brasa = lz.elipse(66, 120, 9, 3.2)
    lz.pintar(brasa * (lz.ruido(1.4, 2, semilla=10204) > 0.45), AMBAR[1])
    lz.pintar(brasa * (lz.ruido(1.0, 1, semilla=10205) > 0.72), AMBAR[3])
    lz.sumar_luz(lz.desenfocar(brasa, 6) * boca, AMBAR[2], 0.5)
    arco = lz.trazo([(42, 128), (42, 96), (51, 82.5), (66, 77), (81, 82.5), (90, 96), (90, 128)], 3.4)
    lz.sombrear(arco * (1 - boca), ROCA[3:], 1.6, LUZ)
    a = np.arctan2(lz.y - 100, lz.x - 66)
    lz.pintar(arco * (1 - boca) * (((a * 5) % 1) < 0.1) * (lz.y < 98), ROCA[0], 0.7)
    lz.sombrear(lz.poligono([(62, 80), (70, 80), (68.5, 71), (63.5, 71)]), AMBAR[1:], 2.2, LUZ)                 # la clave de ámbar
    # ventanas a los lados
    _ventana(lz, 20, 92, 32, 108, 0.35)
    _ventana(lz, 98, 92, 110, 108, 0.35)
    # el tejado de cobre a dos aguas y el hastial
    hastial = lz.poligono([(10, 63), (122, 63), (66, 26)])
    _sillares(lz, hastial, 10206, ROCA[1:], 7, 12)
    ojo = lz.circulo(66, 48, 6)
    lz.pintar(ojo, "#2a1206")
    lz.pintar(ojo, AMBAR[2], 0.45)
    for k in range(6):
        ang = k * np.pi / 3
        lz.pintar(lz.trazo([(66, 48), (66 + np.cos(ang) * 6, 48 + np.sin(ang) * 6)], 0.4), ROCA[0])
    _tejado(lz, 66, 18, 62, 62, COBRE, 8)
    # delante: el yunque grande y unas barras de hierro apoyadas en la pared
    _yunque(lz, 26, 128, 1.15)
    for k, x in enumerate((100, 104, 108)):
        lz.sombrear(lz.trazo([(x, 127), (x + 5, 100 - k * 3)], 1.0), HIERRO, 0.5, LUZ)
    return lz.sprite(contorno=0.4)


def casa(f):
    W, H = 76, 80
    lz = Lienzo(W, H, s=5, semilla=10230 + f)
    cx = 36
    muro = lz.poligono([(6, 77), (66, 77), (66, 40), (6, 40)])
    _sillares(lz, muro, 10231 + f)
    for x in (6, 61):
        esq = lz.poligono([(x, 77), (x + 5, 77), (x + 5, 40), (x, 40)])
        lz.sombrear(esq, ROCA[2:], 3.0, LUZ)
        lz.pintar(esq * ((lz.y % 8) < 0.9), ROCA[0], 0.7)
    puerta = lz.poligono([(14, 77), (28, 77), (28, 56), (21, 51.5), (14, 56)])
    lz.sombrear(puerta, MADERA, 4.0, LUZ, textura=((lz.x % 4.2) < 0.6) * 1.0, fuerza_tex=-0.4)
    lz.sombrear(lz.trazo([(15, 64), (27, 64)], 1.1), HIERRO, 0.6, LUZ)
    lz.sombrear(lz.circulo(25, 68, 1.0), AMBAR[1:], 0.8, LUZ)
    marco = lz.trazo([(12.5, 77), (12.5, 56), (21, 50), (29.5, 56), (29.5, 77)], 2.0)
    lz.sombrear(marco * (1 - puerta), ROCA[3:], 1.2, LUZ)
    _ventana(lz, 40, 54, 54, 66, 0.3)
    chim = lz.poligono([(50, 30), (58, 30), (58, 10), (50, 10)])
    lz.sombrear(chim, ROCA[1:], 3.0, LUZ)
    lz.pintar(chim * ((lz.y % 6) < 0.8), ROCA[0], 0.6)
    lz.sombrear(lz.poligono([(49, 11), (59, 11), (59, 8), (49, 8)]), ROCA[3:], 1.0, LUZ)
    hastial = lz.poligono([(6, 41), (66, 41), (36, 18)])
    lz.sombrear(hastial, MADERA[1:], 10.0, LUZ, textura=((lz.x % 5) < 0.7) * 1.0, fuerza_tex=-0.35)
    _tejado(lz, cx, 12, 40, 35, TEJA if f == 0 else PIZARRA, 6)
    if f == 0:      # cantero: un bloque a medio tallar junto a la puerta
        bloque = lz.poligono([(62, 79), (75, 79), (75, 68), (69, 66), (62, 69)])
        lz.sombrear(bloque, ROCA[2:], 4.0, LUZ, textura=lz.ruido(1.4, 2, semilla=10235), fuerza_tex=0.2)
        _grietas_ambar(lz, bloque, 10236, 0.03)
    else:           # afinador: un travesaño con tres diapasones colgados
        lz.sombrear(lz.trazo([(38, 46), (58, 46)], 1.3), MADERA[1:], 0.7, LUZ)
        for x, largo in ((42, 5), (48, 7), (54, 4)):
            lz.pintar(lz.trazo([(x, 46.5), (x, 48)], 0.35), HIERRO[2])
            lz.sombrear(lz.trazo([(x - 1.2, 48 + largo), (x - 1.2, 49), (x + 1.2, 49), (x + 1.2, 48 + largo)], 0.8), HIERRO[2:], 0.5, LUZ)
    return lz.sprite(contorno=0.4)


def mercado(f):
    W, H = 112, 88
    lz = Lienzo(W, H, s=4, semilla=10260 + f)
    # los cuatro postes
    for x in (8, 104):
        poste = lz.poligono([(x - 2, 86), (x + 2, 86), (x + 1.6, 22), (x - 1.6, 22)])
        lz.sombrear(poste, MADERA, 1.6, LUZ, textura=((lz.y % 5) < 0.7) * 1.0, fuerza_tex=-0.3)
    # el fondo: una trasera de tablas con ganchos
    trasera = lz.poligono([(12, 62), (100, 62), (100, 30), (12, 30)])
    lz.sombrear(trasera, MADERA[:4], 14.0, LUZ, textura=((lz.x % 6) < 0.8) * 1.0, fuerza_tex=-0.35)
    # el mostrador de piedra con tablero
    mostr = lz.poligono([(10, 86), (102, 86), (102, 64), (10, 64)])
    _sillares(lz, mostr, 10261, ROCA[1:], 7, 12)
    tablero = lz.poligono([(7, 66), (105, 66), (105, 60), (7, 60)])
    lz.sombrear(tablero, MADERA[1:], 2.4, LUZ, textura=((lz.x % 7) < 0.7) * 1.0, fuerza_tex=-0.3)
    if f == 0:
        # cerrado: una lona atada tapa el mostrador y el toldo está recogido arriba
        lona = lz.poligono([(9, 62), (103, 62), (100, 46), (86, 42), (60, 47), (34, 41), (14, 46)])
        lz.sombrear(lona, LONA, 6.0, LUZ, textura=lz.ruido(3.0, 2, semilla=10262), fuerza_tex=0.3)
        for x in (30, 56, 82):
            lz.pintar(lz.trazo([(x, 44), (x + 1, 62)], 0.4) * lona, LONA[0], 0.7)
        rollo = lz.poligono([(6, 26), (106, 26), (106, 18), (6, 18)])
        lz.sombrear(rollo, LONA[1:], 3.6, LUZ, textura=((lz.x % 9) < 1.0) * 1.0, fuerza_tex=-0.3)
        for x in (24, 56, 88):
            lz.sombrear(lz.trazo([(x, 17), (x, 27)], 1.0), CUERO, 0.5, LUZ)
    else:
        # abierto: lingotes, herramientas colgadas, un farol y el toldo a rayas
        for k, x in enumerate((20, 30, 40)):
            ling = lz.poligono([(x - 4, 60), (x + 4, 60), (x + 3, 56), (x - 3, 56)])
            lz.sombrear(ling, HIERRO if k != 1 else AMBAR[1:], 1.6, LUZ)
        lz.sombrear(lz.poligono([(22, 56), (38, 56), (36, 52), (24, 52)]), HIERRO[1:], 1.6, LUZ)
        for x, alto in ((52, 12), (60, 16), (68, 10), (76, 14)):                         # martillos y tenazas colgados
            lz.pintar(lz.trazo([(x, 32), (x, 34)], 0.4), HIERRO[1])
            lz.sombrear(lz.trazo([(x, 34), (x, 34 + alto)], 1.0), MADERA[2:], 0.5, LUZ)
            lz.sombrear(lz.poligono([(x - 2.6, 34 + alto), (x + 2.6, 34 + alto), (x + 2.6, 38 + alto), (x - 2.6, 38 + alto)]), HIERRO[1:], 1.2, LUZ)
        geoda = lz.elipse(86, 56, 6, 4.4)
        lz.sombrear(geoda, ROCA[1:], 2.4, LUZ)
        dentro = lz.elipse(86, 55.4, 4, 2.6)
        lz.sombrear(dentro, AMBAR[1:], 1.4, LUZ)
        lz.sumar_luz(lz.desenfocar(dentro, 3), AMBAR[3], 0.5)
        farol = lz.poligono([(93, 36), (99, 36), (98, 45), (94, 45)])
        lz.pintar(lz.trazo([(96, 30), (96, 36)], 0.5), HIERRO[1])
        lz.sombrear(farol, AMBAR[2:], 1.8, LUZ)
        lz.sumar_luz(lz.desenfocar(farol, 5), AMBAR[3], 0.7)
        toldo = lz.poligono([(2, 34), (110, 34), (104, 12), (8, 12)])
        raya = (((lz.x + (lz.y - 12) * 0.25) % 16) < 8) * 1.0
        lz.sombrear(toldo, TEJA[1:], 9.0, LUZ)
        lz.sombrear(toldo * raya, LONA[1:], 9.0, LUZ)
        for x in range(4, 110, 8):                                                      # el festón
            lz.sombrear(lz.poligono([(x, 34), (x + 8, 34), (x + 4, 39)]), TEJA[1:] if (x // 8) % 2 else LONA[1:], 1.6, LUZ)
        lz.sombrear(lz.trazo([(8, 11.5), (104, 11.5)], 1.6), MADERA[1:], 0.8, LUZ)
    return lz.sprite(contorno=0.4)


def horno(f):
    W, H = 28, 48
    lz = Lienzo(W, H, s=6, semilla=10290 + f)
    cx = 14
    base = lz.poligono([(cx - 10, 47), (cx + 10, 47), (cx + 9, 40), (cx - 9, 40)])
    lz.sombrear(base, ROCA[1:], 2.0, LUZ)
    lz.pintar(base * (((lz.x + 3) % 7) < 0.6), ROCA[0], 0.6)
    domo = lz.elipse(cx, 36, 10, 11) * (lz.y < 41)
    lz.sombrear(domo, ROCA[1:], 6.0, LUZ, textura=lz.ruido(1.4, 2, semilla=10291), fuerza_tex=0.25)
    lz.pintar(domo * ((lz.y % 5) < 0.6), ROCA[0], 0.5)
    boca = lz.elipse(cx, 38, 5, 5.5) * (lz.y < 41) * (lz.y > 32)
    lz.pintar(boca, "#0e0806")
    if f == 1:
        fuego = boca * (lz.ruido(1.6, 2, semilla=10292) > 0.3)
        lz.pintar(boca, AMBAR[1])
        lz.pintar(fuego, AMBAR[3])
        lz.pintar(boca * (lz.ruido(1.0, 1, semilla=10293) > 0.7), AMBAR[5])
        lz.sumar_luz(lz.desenfocar(boca, 2.2), AMBAR[3], 0.9)
    cuello = lz.poligono([(cx - 3, 26), (cx + 3, 26), (cx + 2.2, 20), (cx - 2.2, 20)])
    lz.sombrear(cuello, ROCA[2:], 1.4, LUZ)
    brazos = np.zeros_like(cuello)
    for lado in (-1, 1):
        brazos = np.clip(brazos + lz.trazo([(cx + lado * 1.2, 20.5), (cx + lado * 4.6, 16.5), (cx + lado * 4.6, 2.5)], 2.2, 1.8), 0, 1)
    lz.sombrear(brazos, HIERRO if f == 0 else AMBAR[1:], 1.2, LUZ)
    if f == 1:
        lz.sumar_luz(lz.desenfocar(brazos, 1.6), AMBAR[3], 0.8)
        for y in (5, 9, 13):
            lz.pintar(lz.trazo([(cx - 2.4, y), (cx, y - 1.1), (cx + 2.4, y)], 0.4), "#ffffff", 0.85)
    return lz.sprite(contorno=0.5)


def yunque(f):
    W, H = 24, 26
    lz = Lienzo(W, H, s=6, semilla=10310 + f)
    cara = _yunque(lz, 11, 25, 1.0, HIERRO if f == 0 else HIERRO[1:] + ["#ffffff"])
    runa = lz.trazo([(7.5, 13.8), (9.5, 11.6), (11.5, 13.8)], 0.45) + lz.trazo([(9.5, 11.6), (9.5, 14.4)], 0.45)
    lz.pintar(runa * cara, HIERRO[0] if f == 0 else AMBAR[4])
    if f == 1:
        lz.sumar_luz(lz.desenfocar(runa * cara, 1.4), AMBAR[3], 1.0)
        for (x, y) in ((16, 6), (19, 9), (5, 7)):
            lz.pintar(lz.circulo(x, y, 0.6), AMBAR[5])
    return lz.sprite(contorno=0.5)


def diapason():
    W, H = 72, 116
    lz = Lienzo(W, H, s=4, semilla=10330)
    cx = 36
    for (ancho, y0, y1) in ((30, 115, 108), (25, 108, 101), (20, 101, 92)):                 # el pie escalonado de basalto
        esc = lz.poligono([(cx - ancho, y0), (cx + ancho, y0), (cx + ancho - 1.5, y1), (cx - ancho + 1.5, y1)])
        lz.sombrear(esc, BASALTO, 3.0, LUZ)
        lz.pintar(lz.trazo([(cx - ancho + 1.5, y1 + 0.4), (cx + ancho - 1.5, y1 + 0.4)], 0.4), BASALTO[5], 0.7)
    for lado in (-1, 1):                                                                    # argollas de las cadenas
        arg = (np.abs(np.hypot(lz.x - (cx + lado * 23), lz.y - 104) - 3.0) < 0.9) * 1.0
        lz.sombrear(arg, HIERRO[1:], 0.8, LUZ)
    mango = lz.poligono([(cx - 5, 93), (cx + 5, 93), (cx + 4, 70), (cx - 4, 70)])
    lz.sombrear(mango, HIERRO, 3.0, LUZ, textura=((lz.y % 5) < 0.7) * 1.0, fuerza_tex=-0.25)
    nudo = lz.elipse(cx, 68, 9, 6)
    lz.sombrear(nudo, HIERRO[1:], 4.0, LUZ)
    brazos = np.zeros_like(nudo)
    for lado in (-1, 1):
        brazos = np.clip(brazos + lz.trazo([(cx + lado * 5, 68), (cx + lado * 15, 56), (cx + lado * 15, 6)], 7.0, 5.0), 0, 1)
    lz.sombrear(brazos, HIERRO, 3.2, LUZ, textura=lz.ruido(1.6, 3, semilla=10331), fuerza_tex=0.25)
    lz.pintar(lz.trazo([(cx - 17.6, 54), (cx - 17.6, 10)], 0.5) * brazos, HIERRO[5], 0.7)
    for y in (20, 34, 48):                                                                  # anillas grabadas en los brazos
        lz.pintar(brazos * (np.abs(lz.y - y) < 0.6), HIERRO[0], 0.8)
    corazon = lz.poligono([(cx, 60), (cx + 5, 68), (cx, 76), (cx - 5, 68)])                  # el corazón de ámbar, apagado
    lz.sombrear(corazon, AMBAR[:4], 2.6, LUZ)
    lz.pintar(lz.circulo(cx - 1.4, 65.6, 0.9), AMBAR[4], 0.8)
    return lz.sprite(contorno=0.4)


def verja():
    W, H = 56, 64
    lz = Lienzo(W, H, s=5, semilla=10350)
    cx = 28
    arco = lz.poligono([(3, 63), (53, 63), (53, 24), (45, 9), (28, 3), (11, 9), (3, 24)])
    hueco = lz.poligono([(11, 63), (45, 63), (45, 27), (39, 16), (28, 11), (17, 16), (11, 27)])
    marco = arco * (1 - hueco)
    lz.sombrear(marco, ROCA[1:], 4.0, LUZ, textura=lz.ruido(1.6, 3, semilla=10351), fuerza_tex=0.3)
    lz.pintar(marco * ((lz.y % 8) < 0.9) * (lz.y >= 28), ROCA[0], 0.7)
    lz.pintar(hueco, "#0c0810")
    barras = hueco * ((((lz.x - cx) % 5.5) < 1.3) | (np.abs(lz.y - 30) < 0.9) | (np.abs(lz.y - 50) < 0.9))
    lz.sombrear(barras, HIERRO, 0.8, LUZ)
    candado = lz.poligono([(cx - 3, 37), (cx + 3, 37), (cx + 3, 43), (cx - 3, 43)])
    lz.sombrear(candado, AMBAR[1:], 1.6, LUZ)
    lz.pintar((np.abs(np.hypot(lz.x - cx, lz.y - 36.5) - 2.4) < 0.6) * (lz.y < 37), HIERRO[4])
    return lz.sprite(contorno=0.4)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    tira("casa", casa, 2)
    tira("mercado", mercado, 2)
    tira("horno", horno, 2)
    tira("yunque", yunque, 2)
    for nombre, fn in (("gran_forja", gran_forja), ("diapason", diapason), ("verja", verja)):
        Image.fromarray(fn(), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))
    print("Mji-Jiwe pintada en", SALIDA)
