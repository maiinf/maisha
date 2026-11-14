"""EL DESFILADERO DEL METEORITO (Asterhaul), pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_desfiladero.py

Genera en arte/mundos/asterhaul/desfiladero/:
  kaa_jiwe.png   5 × 32×28  KAA-JIWE, EL CANGREJO DE GEODA: una piedra redonda y agrietada con patas; dos ojos en
                 palitos y dos pinzas de roca. 0 y 1 anda · 2 embiste (pinzas delante, ojos fieros) · 3 VOLCADO
                 (panza arriba: se le ve la geoda de ámbar, patas al aire) · 4 volcado y golpeado (blanco)
  muro.png       2 × 48×44  UN MURO AGRIETADO: un tapón de roca con grietas por las que brilla el ámbar.
                 0 entero · 1 roto (cascotes en el suelo)
  derrumbe.png   2 × 48×44  UN DERRUMBE: un montón de peñascos grises. 0 entero · 1 apartado (cascotes)
  vagoneta.png   2 × 28×28  UNA VAGONETA DE ÁMBAR: caja de tablones con herrajes, llena de trozos de ámbar.
                 0 de lado (rueda por una vía este-oeste) · 1 de frente (vía norte-sur)
  pilar.png      2 × 24×52  UN PILAR-DIAPASÓN de la Puerta del Cráter: columna de basalto con una horquilla de
                 hierro meteórico arriba. 0 dormido · 1 sonando (ámbar encendido, ondas)
  estela.png     24×38      LA ESTELA DE LA CARGA: una laja naranja con una embestida grabada
  esquirla.png   2 × 16×16  UNA ESQUIRLA DE ESTRELLA: un trozo de ámbar vivo en forma de estrella rota
  taller.png     120×108    EL TALLER DE MWAMBA: sillares ocres, tejado de tablas a dos aguas, portón, un bloque a
                 medio tallar en su banco, la grúa de cuerda y un farol de ámbar
  puerta.png     2 × 72×84  LA PUERTA DEL CRÁTER: dos hojas de basalto con un sol de ámbar partido en dos, en un
                 arco de sillares. 0 cerrada · 1 abierta (las hojas a los lados, dentro luz de ámbar)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "asterhaul", "desfiladero")
LUZ = (-0.6, -0.7, 0.5)
ROCA = ["#1e1410", "#38241a", "#54382a", "#72503a", "#92704e", "#b89468"]
GRIS = ["#16141a", "#2c2a32", "#46444e", "#63616c", "#85838e", "#acaab4"]
BASALTO = ["#0e0c14", "#1c1a26", "#2e2c3c", "#444256", "#5e5c74", "#807e98"]
AMBAR = ["#5a2406", "#9a4a0c", "#d8841c", "#f8b040", "#ffd878", "#fff4c8"]
HIERRO = ["#14161c", "#2a2e3a", "#464c5c", "#6a7284", "#949cae", "#c4cad8"]
MADERA = ["#1a100c", "#32201a", "#523426", "#724a34", "#946648", "#b88a62"]
TEJA = ["#3a160c", "#6a2c14", "#9a4a1e", "#c46c2c", "#e4944a", "#f8c07a"]
BLANCO = ["#c8c8d0", "#e0e0e8", "#f4f4f8", "#ffffff"]


def _grietas_ambar(lz, masa, semilla, corte=0.02):
    """Grietas por las que asoma el ámbar (y su resplandor)."""
    g = (np.abs(lz.ruido(7, 3, semilla=semilla) - 0.5) < corte) * masa
    lz.pintar(g, AMBAR[2])
    lz.pintar(g * (lz.ruido(2, 1, semilla=semilla + 1) > 0.5), AMBAR[4], 0.9)
    lz.sumar_luz(lz.desenfocar(g, 1.2), AMBAR[3], 0.5)
    return g


def _penasco(lz, cx, cy, rx, ry, rampa, semilla):
    """Una piedra facetada: un óvalo mordido por el ruido, con una arista de luz."""
    p = lz.elipse(cx, cy, rx, ry) * (lz.ruido(3.5, 2, semilla=semilla) > 0.2)
    p = np.clip(p + lz.elipse(cx, cy, rx * 0.8, ry * 0.8), 0, 1)
    lz.sombrear(p, rampa, min(rx, ry) * 0.8, LUZ, textura=lz.ruido(1.2, 2, semilla=semilla + 3), fuerza_tex=0.25)
    lz.pintar(lz.trazo([(cx - rx * 0.5, cy - ry * 0.5), (cx + rx * 0.2, cy - ry * 0.75)], 0.35) * p, rampa[-1], 0.7)
    lz.pintar(lz.trazo([(cx - rx * 0.1, cy - ry * 0.2), (cx + rx * 0.3, cy + ry * 0.5)], 0.3) * p, rampa[0], 0.6)
    return p


def _cascotes(lz, W, base, rampa, semilla, n=9):
    rng = np.random.default_rng(semilla)
    for i in range(n):
        x = 5 + rng.random() * (W - 10)
        y = base - rng.random() * 7
        _penasco(lz, x, y, 2.0 + rng.random() * 3.0, 1.4 + rng.random() * 2.0, rampa, semilla + 10 * i)


def kaa_jiwe(f):
    W, H = 32, 28
    lz = Lienzo(W, H, s=6, semilla=9900 + f)
    cx = 16
    volcado = f >= 3
    blanco = f == 4
    roca = BLANCO + BLANCO[-2:] if blanco else ROCA
    paso = {0: 1.0, 1: -1.0}.get(f, 0.0)
    if volcado:
        # panza arriba: las patas al aire, la geoda a la vista
        for k, lado in enumerate((-1, -1, 1, 1)):
            x0 = cx + lado * (5 + (k % 2) * 4)
            pata = lz.trazo([(x0, 15), (x0 + lado * 3, 9 + (k % 2) * 2), (x0 + lado * 2.4, 5 + (k % 2) * 2)], 1.5, 0.9)
            lz.sombrear(pata, roca, 0.8, LUZ)
        cuerpo = lz.elipse(cx, 18, 12.5, 7.5)
        lz.sombrear(cuerpo, roca, 5.0, LUZ, textura=lz.ruido(1.5, 2, semilla=9910), fuerza_tex=0.2)
        geoda = lz.elipse(cx, 16.5, 8.5, 4.6)
        lz.pintar(geoda, AMBAR[0] if not blanco else "#ffffff")
        if not blanco:
            cristales = geoda * (lz.ruido(2.2, 2, semilla=9911) > 0.42)
            lz.sombrear(cristales, AMBAR[1:], 1.5, LUZ)
            lz.pintar(geoda * (lz.ruido(1.0, 1, semilla=9912) > 0.8), AMBAR[5], 0.9)
            lz.sumar_luz(lz.desenfocar(geoda, 1.5), AMBAR[3], 0.45)
        for lado in (-1, 1):                                  # los ojos, mareados, colgando abajo
            lz.pintar(lz.trazo([(cx + lado * 4, 23), (cx + lado * 5, 25.5)], 0.7), roca[1])
            lz.pintar(lz.circulo(cx + lado * 5.2, 26, 1.5), "#ffffff")
            lz.pintar(lz.trazo([(cx + lado * 5.2 - 0.8, 25.4), (cx + lado * 5.2 + 0.8, 26.6)], 0.3), "#140e18")
            lz.pintar(lz.trazo([(cx + lado * 5.2 + 0.8, 25.4), (cx + lado * 5.2 - 0.8, 26.6)], 0.3), "#140e18")
        return lz.sprite(contorno=0.5)
    # las patas (tres a cada lado) y las pinzas
    for lado in (-1, 1):
        for k in range(3):
            x0 = cx + lado * (6 + k * 2.2)
            sube = paso * lado * (1 if k % 2 else -1) * 0.8
            pata = lz.trazo([(x0, 19), (x0 + lado * 3.4, 21.5 + sube), (x0 + lado * 4.2, 26 + sube * 0.5)], 1.5, 0.9)
            lz.sombrear(pata, roca[:5], 0.8, LUZ)
        ax = cx + lado * (11.5 if f != 2 else 9.5)
        ay = 15 if f != 2 else 20
        brazo = lz.trazo([(cx + lado * 8, 17), (ax, ay)], 1.8, 1.6)
        lz.sombrear(brazo, roca[:5], 0.9, LUZ)
        pinza = lz.elipse(ax + lado * 1.5, ay - 0.5, 3.6, 2.8, 20 * lado)
        pinza = pinza * (1 - lz.poligono([(ax + lado * 1.2, ay - 0.6), (ax + lado * 6, ay - 2.2), (ax + lado * 6, ay + 0.6)]))
        lz.sombrear(pinza, roca[1:], 1.6, LUZ)
    # la coraza: una piedra redonda, agrietada, con el ámbar asomando por las grietas
    coraza = lz.elipse(cx, 14.5 + abs(paso) * 0.0, 11.5, 8.6)
    coraza = np.clip(coraza * (lz.ruido(5, 2, semilla=9901) > 0.12) + lz.elipse(cx, 15, 10.4, 7.6), 0, 1)
    lz.sombrear(coraza, roca, 6.0, LUZ, textura=lz.ruido(1.4, 3, semilla=9902), fuerza_tex=0.3)
    _grietas_ambar(lz, coraza * (lz.y < 19), 9903, 0.05)
    lz.pintar(lz.trazo([(cx - 8, 10), (cx - 2, 7.6), (cx + 4, 7.4)], 0.4) * coraza, roca[5], 0.6)
    # los ojos, en dos palitos que asoman por debajo de la coraza
    for lado in (-1, 1):
        ox, oy = cx + lado * 3.4, 20.5
        lz.pintar(lz.trazo([(ox, 18), (ox, oy)], 0.8), roca[1])
        lz.pintar(lz.circulo(ox, oy + 1.2, 1.9), "#ffffff")
        lz.pintar(lz.circulo(ox + (0.3 * lado if f != 2 else 0), oy + 1.5, 1.0), "#140e18" if f != 2 else AMBAR[2])
        if f == 2:
            lz.pintar(lz.trazo([(ox - lado * 2.2, oy - 0.6), (ox + lado * 1.6, oy + 0.6)], 0.5), roca[0])
    return lz.sprite(contorno=0.5)


def _tapon(f, rampa, semilla, con_ambar):
    W, H = 48, 44
    lz = Lienzo(W, H, s=5, semilla=semilla)
    if f == 1:
        _cascotes(lz, W, 41, rampa, semilla + 50, 11)
        return lz.sprite(contorno=0.5)
    masa = np.zeros((lz.H, lz.W))
    rng = np.random.default_rng(semilla)
    piedras = [(8, 34, 8, 8), (24, 35, 10, 8), (40, 34, 8, 8), (15, 24, 9, 8), (33, 24, 10, 8), (24, 13, 11, 9), (9, 15, 6, 6), (40, 15, 6, 6)]
    for i, (x, y, rx, ry) in enumerate(piedras):
        masa = np.clip(masa + _penasco(lz, x + rng.random() - 0.5, y, rx, ry, rampa, semilla + 7 * i), 0, 1)
    if con_ambar:
        _grietas_ambar(lz, masa, semilla + 90, 0.03)
    return lz.sprite(contorno=0.5)


def muro(f):
    return _tapon(f, ROCA, 9930, True)


def derrumbe(f):
    return _tapon(f, GRIS, 9950, False)


def vagoneta(f):
    W, H = 28, 28
    lz = Lienzo(W, H, s=6, semilla=9970 + f)
    cx = 14
    if f == 0:
        caja = lz.poligono([(2, 9), (26, 9), (23.5, 21), (4.5, 21)])
        lz.sombrear(caja, MADERA, 3.0, LUZ, textura=((lz.x % 4.5) < 0.6) * 1.0, fuerza_tex=-0.35)
        for y in (9.6, 20.4):
            lz.sombrear(lz.trazo([(2.4 if y < 12 else 4.6, y), (25.6 if y < 12 else 23.4, y)], 1.0), HIERRO, 0.6, LUZ)
        for x in (5, 23):
            lz.pintar(lz.circulo(x, 15, 0.7), HIERRO[4])
        for x in (8, 20):
            rueda = lz.circulo(x, 23, 3.4)
            lz.sombrear(rueda, HIERRO, 1.6, LUZ)
            lz.pintar(lz.circulo(x, 23, 1.2), HIERRO[0])
        monton = lz.poligono([(3, 9), (25, 9), (21, 4), (14, 2.5), (7, 4.5)])
    else:
        caja = lz.poligono([(4, 10), (24, 10), (22, 22), (6, 22)])
        lz.sombrear(caja, MADERA, 3.0, LUZ, textura=((lz.x % 4.5) < 0.6) * 1.0, fuerza_tex=-0.35)
        lz.sombrear(lz.trazo([(4.4, 10.6), (23.6, 10.6)], 1.0), HIERRO, 0.6, LUZ)
        lz.sombrear(lz.trazo([(6.4, 21.4), (21.6, 21.4)], 1.0), HIERRO, 0.6, LUZ)
        for x in (5.5, 22.5):
            rueda = lz.poligono([(x - 1.4, 19), (x + 1.4, 19), (x + 1.4, 26.5), (x - 1.4, 26.5)])
            lz.sombrear(rueda, HIERRO, 1.0, LUZ)
        lz.sombrear(lz.circulo(cx, 16, 1.8), HIERRO[1:], 1.0, LUZ)                 # el enganche
        monton = lz.poligono([(5, 10), (23, 10), (20, 5), (14, 3), (8, 5.5)])
    trozos = monton * (lz.ruido(2.4, 2, semilla=9975) > 0.3)
    lz.pintar(monton, AMBAR[0])
    lz.sombrear(trozos, AMBAR, 2.0, LUZ)
    lz.pintar(monton * (lz.ruido(0.9, 1, semilla=9976) > 0.82), AMBAR[5], 0.9)
    lz.sumar_luz(lz.desenfocar(monton, 1.5), AMBAR[3], 0.4)
    return lz.sprite(contorno=0.5)


def pilar(f):
    W, H = 24, 52
    lz = Lienzo(W, H, s=6, semilla=9990 + f)
    cx = 12
    zoc = lz.poligono([(cx - 8, 51), (cx + 8, 51), (cx + 7, 46), (cx - 7, 46)])
    lz.sombrear(zoc, BASALTO, 2.0, LUZ)
    fuste = lz.poligono([(cx - 5, 46), (cx + 5, 46), (cx + 4.2, 20), (cx - 4.2, 20)])
    lz.sombrear(fuste, BASALTO[1:], 3.5, LUZ, textura=((lz.x % 2.6) < 0.5) * 1.0, fuerza_tex=-0.25)
    for y in (26, 34, 42):                                            # aros grabados
        lz.pintar(lz.trazo([(cx - 4.6, y), (cx + 4.6, y)], 0.45) * fuste, AMBAR[2] if f else BASALTO[0], 0.9)
    capitel = lz.poligono([(cx - 6, 21), (cx + 6, 21), (cx + 5, 17.5), (cx - 5, 17.5)])
    lz.sombrear(capitel, BASALTO[2:], 1.4, LUZ)
    brazos = np.zeros_like(fuste)
    for lado in (-1, 1):                                              # la horquilla de hierro meteórico
        brazos = np.clip(brazos + lz.trazo([(cx + lado * 1.2, 18), (cx + lado * 4.4, 14.5), (cx + lado * 4.4, 2.5)], 2.2, 1.8), 0, 1)
    lz.sombrear(brazos, HIERRO if f == 0 else AMBAR[1:], 1.2, LUZ)
    gema = lz.poligono([(cx, 15.5), (cx + 2.2, 18), (cx, 20.5), (cx - 2.2, 18)])
    lz.sombrear(gema, AMBAR[:4] if f == 0 else AMBAR[2:], 1.4, LUZ)
    if f == 1:
        lz.sumar_luz(lz.desenfocar(brazos + gema, 1.6), AMBAR[3], 0.9)
        for lado in (-1, 1):
            lz.pintar(lz.trazo([(cx + lado * 6.6, 13), (cx + lado * 6.9, 3.5)], 0.5, 0.3), AMBAR[5], 0.8)
        for y in (5, 9, 13):
            lz.pintar(lz.trazo([(cx - 2.4, y), (cx, y - 1.1), (cx + 2.4, y)], 0.4), "#ffffff", 0.85)
    return lz.sprite(contorno=0.5)


def estela():
    W, H = 24, 38
    lz = Lienzo(W, H, s=6, semilla=10010)
    cx = 12
    lz.sombrear(lz.elipse(cx, 36, 9, 2), ROCA[:4], 1.0, LUZ)
    laja = lz.poligono([(cx - 7, 36), (cx + 7, 36), (cx + 6, 12), (cx + 1.5, 2), (cx - 4, 6), (cx - 6.5, 16)])
    lz.sombrear(laja, TEJA, 4.5, LUZ, textura=lz.ruido(1.6, 3, semilla=10011), fuerza_tex=0.25)
    # la embestida grabada: una punta de flecha gruesa y tres ondas delante
    glifo = lz.poligono([(cx - 3.5, 26), (cx + 1.5, 20), (cx - 3.5, 14), (cx - 1.5, 20)])
    for k, r in enumerate((5.0, 7.0)):
        arco = (np.abs(np.hypot(lz.x - (cx - 2), lz.y - 20) - r) < 0.45) * (lz.x > cx + 1.0)
        glifo = np.clip(glifo + arco, 0, 1)
    lz.pintar(glifo * laja, TEJA[0])
    lz.pintar(glifo * laja * (lz.ruido(1.2, 1, semilla=10012) > 0.35), AMBAR[4], 0.95)
    lz.sumar_luz(lz.desenfocar(glifo * laja, 1.2), AMBAR[3], 0.5)
    return lz.sprite(contorno=0.5)


def esquirla(f=0):
    W, H = 16, 16
    lz = Lienzo(W, H, s=8, semilla=10030)
    cx, cy = 8, 8
    a = np.arctan2(lz.y - cy, lz.x - cx)
    d = np.hypot(lz.x - cx, lz.y - cy)
    estrella = (d < 2.6 + 4.6 * np.abs(np.cos(a * 2.0)) ** 3) * 1.0                 # cuatro puntas gordas
    estrella = estrella * (1 - lz.poligono([(cx + 2.5, cy + 1.5), (16, cy + 0.5), (16, 16), (cx + 1, 16)]))     # le falta un trozo
    lz.sombrear(estrella, AMBAR[1:], 2.2, LUZ)
    lz.pintar(lz.circulo(cx - 0.8, cy - 0.8, 1.1), "#ffffff", 0.9)
    lz.sumar_luz(lz.desenfocar(estrella, 1.6), AMBAR[4], 0.6 if f == 0 else 1.1)
    if f == 1:
        lz.pintar(lz.circulo(cx + 2.4, cy - 2.6, 0.7), "#ffffff", 0.9)
    return lz.sprite(contorno=0.5)


def taller():
    W, H = 120, 108
    lz = Lienzo(W, H, s=4, semilla=10050)
    # la grúa de madera, detrás a la derecha: mástil, brazo y cuerda con gancho
    mastil = lz.poligono([(98, 104), (102, 104), (101.4, 22), (98.6, 22)])
    lz.sombrear(mastil, MADERA, 1.8, LUZ, textura=((lz.y % 5) < 0.7) * 1.0, fuerza_tex=-0.3)
    brazo = lz.trazo([(100, 26), (116, 14)], 3.0, 2.2)
    lz.sombrear(brazo, MADERA[1:], 1.4, LUZ)
    lz.pintar(lz.trazo([(100, 40), (112, 18)], 0.6), MADERA[1])
    lz.pintar(lz.trazo([(115, 15), (115, 58)], 0.45), "#c8b088")
    lz.sombrear(lz.trazo([(115, 58), (116.5, 61), (114, 63)], 0.9), HIERRO, 0.6, LUZ)
    # los muros de sillares ocres
    muro_ = lz.poligono([(10, 104), (92, 104), (92, 48), (10, 48)])
    hilada = np.floor(lz.y / 8)
    junta = ((lz.y % 8) < 0.9) | (((lz.x + hilada * 7) % 14) < 0.9)
    lz.sombrear(muro_, ROCA[1:], 30.0, LUZ, textura=lz.ruido(1.8, 3, semilla=10051), fuerza_tex=0.3)
    lz.pintar(muro_ * junta, ROCA[0], 0.7)
    lz.pintar(muro_ * (((lz.y - 1) % 8) < 0.5) * (1 - junta), ROCA[5], 0.35)
    _grietas_ambar(lz, muro_ * (lz.y > 80), 10052, 0.012)
    # esquineras de piedra más clara
    for x in (10, 86):
        esq = lz.poligono([(x, 104), (x + 6, 104), (x + 6, 48), (x, 48)])
        lz.sombrear(esq, ROCA[2:], 3.0, LUZ)
        lz.pintar(esq * ((lz.y % 8) < 0.9), ROCA[0], 0.7)
    # el portón de tablones con herrajes y su dintel de piedra
    porton = lz.poligono([(38, 104), (64, 104), (64, 70), (51, 62), (38, 70)])
    lz.sombrear(porton, MADERA, 6.0, LUZ, textura=((lz.x % 4.4) < 0.6) * 1.0, fuerza_tex=-0.4)
    lz.pintar(lz.trazo([(51, 63), (51, 104)], 0.4), MADERA[0])
    for y in (76, 94):
        lz.sombrear(lz.trazo([(39, y), (63, y)], 1.3), HIERRO, 0.7, LUZ)
    lz.sombrear(lz.circulo(55, 86, 1.5), AMBAR[1:], 1.0, LUZ)
    arco = lz.trazo([(36.5, 104), (36.5, 70), (51, 60.5), (65.5, 70), (65.5, 104)], 2.6)
    lz.sombrear(arco * (1 - porton), ROCA[3:], 1.4, LUZ)
    # una ventana con contraventana y luz de ámbar dentro
    hueco = lz.poligono([(72, 84), (84, 84), (84, 68), (72, 68)])
    lz.pintar(hueco, "#2a1206")
    lz.pintar(hueco, AMBAR[3], 0.75)
    lz.pintar(lz.trazo([(78, 68), (78, 84)], 0.5) + lz.trazo([(72, 76), (84, 76)], 0.5), MADERA[0])
    lz.sombrear(lz.trazo([(70.5, 67), (85.5, 67)], 1.6), ROCA[3:], 0.8, LUZ)
    lz.sombrear(lz.trazo([(70.5, 85.4), (85.5, 85.4)], 1.8), ROCA[3:], 0.9, LUZ)
    lz.sumar_luz(lz.desenfocar(hueco, 3), AMBAR[3], 0.5)
    # el tejado de tablas a dos aguas, con el hastial de madera y la chimenea de piedra
    chim = lz.poligono([(74, 30), (84, 30), (84, 8), (74, 8)])
    lz.sombrear(chim, ROCA[1:], 4.0, LUZ)
    lz.pintar(chim * ((lz.y % 6) < 0.8), ROCA[0], 0.6)
    lz.sombrear(lz.poligono([(72.5, 9), (85.5, 9), (85.5, 5.5), (72.5, 5.5)]), ROCA[3:], 1.2, LUZ)
    hastial = lz.poligono([(10, 49), (92, 49), (51, 20)])
    lz.sombrear(hastial, MADERA[1:], 12.0, LUZ, textura=((lz.x % 5) < 0.7) * 1.0, fuerza_tex=-0.35)
    ojo = lz.circulo(51, 38, 4.5)
    lz.pintar(ojo, "#2a1206")
    lz.pintar(ojo, AMBAR[2], 0.7)
    lz.pintar(lz.trazo([(51, 33.5), (51, 42.5)], 0.45) + lz.trazo([(46.5, 38), (55.5, 38)], 0.45), MADERA[0])
    for lado in (-1, 1):
        ala = lz.poligono([(51, 14), (51 + lado * 48, 48), (51 + lado * 48, 55), (51, 22)])
        tabla = (((lz.x * 0.82 * lado + lz.y) % 7) < 0.9) * 1.0
        lz.sombrear(ala, TEJA, 5.0, LUZ, textura=tabla, fuerza_tex=-0.45)
        lz.pintar(lz.trazo([(51, 22), (51 + lado * 48, 55)], 0.7) * ala, TEJA[0], 0.8)
    lz.sombrear(lz.trazo([(51, 13.5), (51, 22)], 1.6), TEJA[3:], 0.8, LUZ)
    # el farol de ámbar junto a la puerta
    lz.pintar(lz.trazo([(30, 66), (30, 72)], 0.5), HIERRO[1])
    farol = lz.poligono([(27.5, 72), (32.5, 72), (31.8, 79), (28.2, 79)])
    lz.sombrear(farol, AMBAR[2:], 1.6, LUZ)
    lz.sombrear(lz.trazo([(27, 71.6), (33, 71.6)], 0.9), HIERRO, 0.5, LUZ)
    lz.sumar_luz(lz.desenfocar(farol, 4), AMBAR[3], 0.7)
    # delante, a la izquierda: el banco con un bloque a medio tallar (y el cincel clavado)
    banco = lz.poligono([(0, 104), (26, 104), (26, 97), (0, 97)])
    lz.sombrear(banco, MADERA, 2.5, LUZ, textura=((lz.x % 5) < 0.7) * 1.0, fuerza_tex=-0.3)
    bloque = lz.poligono([(3, 97), (22, 97), (22, 84), (14, 82), (3, 86)])
    lz.sombrear(bloque, ROCA[2:], 5.0, LUZ, textura=lz.ruido(1.4, 2, semilla=10053), fuerza_tex=0.2)
    _grietas_ambar(lz, bloque, 10054, 0.03)
    lz.sombrear(lz.trazo([(16, 82), (19.5, 74)], 0.9), HIERRO[2:], 0.5, LUZ)
    return lz.sprite(contorno=0.4)


def puerta(f):
    W, H = 72, 84
    lz = Lienzo(W, H, s=4, semilla=10070 + f)
    cx = 36
    # el arco de sillares
    arco = lz.poligono([(4, 83), (68, 83), (68, 30), (58, 12), (36, 4), (14, 12), (4, 30)])
    hueco = lz.poligono([(14, 83), (58, 83), (58, 34), (50, 20), (36, 14), (22, 20), (14, 34)])
    marco = arco * (1 - hueco)
    lz.sombrear(marco, ROCA[1:], 5.0, LUZ, textura=lz.ruido(1.6, 3, semilla=10071), fuerza_tex=0.3)
    a = np.arctan2(lz.y - 50, lz.x - cx)
    lz.pintar(marco * ((np.floor(a * 6) % 2) < 0.12) * (lz.y < 40), ROCA[0], 0.7)
    lz.pintar(marco * ((lz.y % 9) < 0.9) * (lz.y >= 40), ROCA[0], 0.7)
    lz.sombrear(lz.poligono([(cx - 5, 12), (cx + 5, 12), (cx + 3.5, 3), (cx - 3.5, 3)]), AMBAR[1:], 2.5, LUZ)      # la clave de ámbar
    if f == 0:
        hojas = hueco
        lz.sombrear(hojas, BASALTO, 14.0, LUZ, textura=((lz.x % 6) < 0.7) * 1.0, fuerza_tex=-0.25)
        lz.pintar(lz.trazo([(cx, 14), (cx, 83)], 0.6), BASALTO[0])
        sol = lz.circulo(cx, 50, 9)
        rayos = (np.hypot(lz.x - cx, lz.y - 50) < 17) * (np.abs(np.sin(a * 6)) > 0.86) * (np.hypot(lz.x - cx, lz.y - 50) > 10.5)
        lz.sombrear(sol, AMBAR[:5], 5.0, LUZ)
        lz.pintar(rayos * hojas, AMBAR[2])
        lz.pintar(lz.trazo([(cx, 41), (cx, 59)], 0.5), BASALTO[0])
        for y in (28, 72):
            lz.sombrear(lz.trazo([(15, y), (57, y)], 1.5) * hojas, HIERRO, 0.8, LUZ)
    else:
        lz.pintar(hueco, "#2a1206")
        lz.pintar(hueco, AMBAR[3], 0.55 + 0.0)
        lz.pintar(hueco * (lz.y > 60), AMBAR[4], 0.35)
        for lado in (-1, 1):                                         # las hojas, abiertas hacia dentro
            hoja = lz.poligono([(cx + lado * 22, 83), (cx + lado * 14, 80), (cx + lado * 14, 30), (cx + lado * 22, 34)])
            lz.sombrear(hoja * hueco, BASALTO, 3.0, LUZ)
        lz.sumar_luz(lz.desenfocar(hueco, 5), AMBAR[3], 0.6)
    return lz.sprite(contorno=0.4)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    tira("kaa_jiwe", kaa_jiwe, 5)
    tira("muro", muro, 2)
    tira("derrumbe", derrumbe, 2)
    tira("vagoneta", vagoneta, 2)
    tira("pilar", pilar, 2)
    tira("puerta", puerta, 2)
    tira("esquirla", esquirla, 2)
    for nombre, fn in (("estela", estela), ("taller", taller)):
        Image.fromarray(fn(), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))
    print("Desfiladero pintado en", SALIDA)
