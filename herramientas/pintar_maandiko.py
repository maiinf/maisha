"""MAANDIKO, la Ciudad-Archivo de Sigilia, pintada con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_maandiko.py

Genera en arte/mundos/sigilia/maandiko/:
  casa_escriba.png  2 × 72×80 casas de escribas: piedra morada en hiladas, tejado a dos aguas de cobre dorado con nieve,
                    ventana redonda encendida, puerta de madera con su farolito, una repisa con libros y chimenea
  casa_kalamu.png   96×104 la casa de Kalamu, la archivera mayor: más alta, con un torreón, un balcón con rollos de
                    pergamino y una ventana alta en arco
  taller_taa.png    80×80 el taller de Taa: faroles colgados en la fachada, una pértiga apoyada y un fuelle
  gran_archivo.png  192×160 el Gran Archivo: escalinata, columnas, puerta alta encendida y la cúpula dorada nervada
  puesto_tinta.png  2 × 56×48 un puesto del Mercado de Tinta: mostrador con tinteros de colores, plumas y papel, toldo
                    a rayas magenta
  fuente.png        64×52 la fuente de la Plaza del Índice, con la tinta helada en la taza (Tinta Quieta)
Y el dibujo de Mauti para la ciudad (arte/personajes/aldeanos/mauti_anim.png, 4 fotogramas, sacado de su dibujo de
las Ruinas).
  charco.png        3 × 48×28 un charco de TINTA QUIETA que tapa una calle: 0 entero (negro, brillante, carámbanos) ·
                    1 medio derretido · 2 casi nada
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "sigilia", "maandiko")
LUZ = (-0.6, -0.7, 0.5)
PIEDRA = ["#1e1828", "#2e2640", "#423856", "#584c6c", "#706484", "#8c809c", "#aaa0b8"]
COBRE = ["#3a2408", "#6a4614", "#a07020", "#d4a034", "#f0cc60", "#fff0b0"]
MADERA = ["#1e140c", "#33241a", "#4a3626", "#634a34", "#7e6146", "#9a7a5a"]
NIEVE = ["#4e4870", "#7e76a2", "#b0a9cd", "#c8c2de", "#e6e3f2", "#f6f5fb"]
TINTA = ["#06040c", "#120c1e", "#22183a", "#3a2a5a", "#5a4488", "#8a70c0"]
VENTANA = ["#7a3a10", "#d4782a", "#f9b947", "#fde27e", "#fff8d2"]
LIBROS = ["#8c2028", "#2e5a8a", "#3e7a3e", "#a07020", "#5a3480"]


def _nieve_encima(lz, forma, grosor=1.6, semilla=0):
    bajar = int(grosor * lz.s)
    encima = forma * (1 - np.roll(forma, bajar, axis=0))
    borde = np.clip(encima + (lz.ruido(0.8, 2, semilla=semilla) > 0.62) * np.roll(encima, int(lz.s), axis=0), 0, 1) * forma
    lz.sombrear(borde, NIEVE[2:], 0.8, LUZ, textura=lz.ruido(0.5, 2, semilla=semilla + 1), fuerza_tex=0.2)
    return borde


def _carambanos(lz, y, x0, x1, semilla, largo=4.0):
    """Carámbanos que cuelgan del alero (a lo largo de y, de x0 a x1)."""
    rng = np.random.default_rng(semilla)
    x = x0 + rng.uniform(0, 2)
    while x < x1:
        l = largo * rng.uniform(0.4, 1.0)
        c = lz.poligono([(x - 0.7, y), (x + 0.7, y), (x, y + l)])
        lz.sombrear(c, NIEVE[2:], 0.4, LUZ)
        lz.pintar(lz.trazo([(x - 0.2, y + 0.3), (x - 0.1, y + l * 0.6)], 0.15), "#ffffff", 0.8)
        x += rng.uniform(1.8, 3.6)


def _muro(lz, forma, semilla, alto_hilada=4.0, ancho_sillar=7.0):
    """Muro de sillares de piedra morada: hiladas, juntas desplazadas y cada sillar con su tono."""
    fila = np.floor(lz.y / alto_hilada)
    col = np.floor((lz.x + (fila % 2) * ancho_sillar / 2) / ancho_sillar)
    tono = (np.sin(fila * 12.9 + col * 78.2 + semilla) * 43758.5) % 1
    lz.sombrear(forma, PIEDRA, 3.0, LUZ, textura=0.5 + (tono - 0.5) * 0.8, fuerza_tex=0.22)
    junta = (((lz.y % alto_hilada) < 0.55) | (((lz.x + (fila % 2) * ancho_sillar / 2) % ancho_sillar) < 0.55)) * forma
    lz.pintar(junta, PIEDRA[0], 0.6)
    lz.pintar(np.clip(np.roll(junta, int(0.5 * lz.s), axis=0) - junta, 0, 1) * forma, PIEDRA[5], 0.25)


def _ventana_redonda(lz, cx, cy, r):
    marco = lz.circulo(cx, cy, r + 1.0)
    lz.sombrear(marco, COBRE[:4], 0.8, LUZ)
    vidrio = lz.circulo(cx, cy, r)
    lz.pintar(vidrio, VENTANA[2])
    lz.pintar(lz.circulo(cx - r * 0.3, cy - r * 0.3, r * 0.45) * vidrio, VENTANA[4], 0.8)
    lz.pintar((np.abs(lz.x - cx) < 0.3) * vidrio + (np.abs(lz.y - cy) < 0.3) * vidrio, COBRE[1], 0.9)
    lz.sumar_luz(lz.desenfocar(vidrio, 2.0), VENTANA[1], 0.35)


def _puerta(lz, cx, base, ancho, alto, encendida=False):
    hueco = np.maximum(lz.poligono([(cx - ancho / 2, base), (cx - ancho / 2, base - alto + ancho / 2), (cx + ancho / 2, base - alto + ancho / 2), (cx + ancho / 2, base)]),
                       lz.elipse(cx, base - alto + ancho / 2, ancho / 2, ancho / 2) * (lz.y < base - alto + ancho / 2 + 0.5))
    lz.sombrear(np.clip(lz.desenfocar(hueco, 0.5) * 1.6, 0, 1) - hueco * 0, PIEDRA[:3], 1, LUZ)
    puerta = hueco
    if encendida:
        lz.pintar(puerta, "#f9d78a")
        lz.sumar_luz(lz.desenfocar(puerta, 3), "#f0a040", 0.4)
        return puerta
    lz.sombrear(puerta, MADERA, 1.5, LUZ, textura=((lz.x % 2.5) < 0.5) * 1.0, fuerza_tex=-0.3)
    lz.pintar(lz.circulo(cx + ancho * 0.28, base - alto * 0.45, 0.6), COBRE[4])
    return puerta


def casa_escriba(k):
    W, H = 72, 80
    lz = Lienzo(W, H, s=5, semilla=7100 + k)
    base = 78
    # el muro
    muro = lz.poligono([(10, base), (10, 40), (62, 40), (62, base)])
    _muro(lz, muro, 7101 + k)
    # el zócalo, más oscuro, y la sombra bajo el alero
    lz.pintar(muro * (lz.y > base - 4), PIEDRA[1], 0.6)
    lz.pintar(lz.desenfocar(muro * (lz.y < 45), 1.5) * muro, PIEDRA[0], 0.45)
    # el tejado a dos aguas de cobre dorado, con tejas en escama y nieve
    tejado = lz.poligono([(4, 42), (36, 12 + k * 3), (68, 42)])
    escama = ((np.sin(lz.x * 1.4 + np.floor(lz.y / 3) * 1.6) > 0.2) * ((lz.y % 3) > 0.6)) * 1.0
    lz.sombrear(tejado, COBRE, 5, LUZ, textura=0.5 + escama * 0.3, fuerza_tex=0.4)
    lz.pintar(tejado * (lz.y > 39.5), COBRE[0], 0.9)
    _nieve_encima(lz, tejado, 5.0, semilla=7102 + k)
    _carambanos(lz, 42.5, 6, 66, 7105 + k)
    # la chimenea
    chim = lz.poligono([(48 - k * 26, 30), (48 - k * 26, 16), (54 - k * 26, 16), (54 - k * 26, 34)])
    _muro(lz, chim * (1 - tejado * 0), 7103 + k, 3, 4)
    _nieve_encima(lz, chim, 1.8, semilla=7104 + k)
    # la ventana redonda del desván y dos ventanas abajo
    _ventana_redonda(lz, 36, 30 + k * 2, 4.2)
    for vx in (20, 52):
        v = lz.poligono([(vx - 4, 62), (vx - 4, 52), (vx + 4, 52), (vx + 4, 62)])
        lz.sombrear(v, COBRE[:4], 0.8, LUZ)
        vid = lz.poligono([(vx - 3, 61), (vx - 3, 53), (vx + 3, 53), (vx + 3, 61)])
        lz.pintar(vid, VENTANA[2] if (vx == 20) != bool(k) else "#3a3456")
        lz.pintar(vid * ((np.abs(lz.x - vx) < 0.3) | (np.abs(lz.y - 57) < 0.3)), COBRE[1])
        if (vx == 20) != bool(k):
            lz.sumar_luz(lz.desenfocar(vid, 2.5), VENTANA[1], 0.35)
        # alféizar con nieve
        al = lz.poligono([(vx - 5, 63), (vx + 5, 63), (vx + 5, 64.5), (vx - 5, 64.5)])
        lz.sombrear(al, PIEDRA[3:], 0.6, LUZ)
        lz.pintar(al * (lz.y < 63.6), NIEVE[4])
    # la puerta y su farolito
    _puerta(lz, 36, base, 10, 18)
    lz.pintar(lz.trazo([(43, 60), (45, 60), (45, 62)], 0.4), "#2a2a30")
    f = lz.elipse(45, 64, 1.4, 1.8)
    lz.pintar(f, VENTANA[3])
    lz.sumar_luz(lz.desenfocar(f, 3), VENTANA[1], 0.5)
    # la repisa de libros junto a la puerta (los escribas sacan los libros a que les dé el aire)
    rep = lz.poligono([(12, 74), (24, 74), (24, 75.5), (12, 75.5)])
    lz.sombrear(rep, MADERA, 0.6, LUZ)
    for i in range(6):
        lb = lz.poligono([(12.5 + i * 1.9, 74), (12.5 + i * 1.9, 69 + (i % 3)), (14 + i * 1.9, 69 + (i % 3)), (14 + i * 1.9, 74)])
        lz.sombrear(lb, ["#140c14", LIBROS[(i + k) % 5], "#e8d8c0"], 0.5, LUZ)
    # nieve al pie
    pie = lz.elipse(36, 79, 32, 2.4) * (lz.y < 80)
    lz.sombrear(pie, NIEVE[1:], 1, LUZ)
    return lz.sprite(contorno=0.5)


def casa_kalamu():
    W, H = 96, 104
    lz = Lienzo(W, H, s=5, semilla=7200)
    base = 102
    muro = lz.poligono([(12, base), (12, 50), (70, 50), (70, base)])
    _muro(lz, muro, 7201)
    torre = lz.poligono([(62, base), (62, 30), (86, 30), (86, base)])
    _muro(lz, torre, 7202)
    lz.pintar(lz.desenfocar(torre, 1) * torre * (lz.x < 64), PIEDRA[0], 0.4)
    # tejados: el de la casa a dos aguas, el de la torre cónico y alto
    tejado = lz.poligono([(6, 52), (40, 22), (72, 52)])
    escama = ((np.sin(lz.x * 1.4 + np.floor(lz.y / 3) * 1.6) > 0.2) * ((lz.y % 3) > 0.6)) * 1.0
    lz.sombrear(tejado, COBRE, 5, LUZ, textura=0.5 + escama * 0.3, fuerza_tex=0.4)
    _nieve_encima(lz, tejado, 5.0, semilla=7203)
    _carambanos(lz, 52.5, 8, 62, 7205)
    cono = lz.poligono([(58, 32), (74, 2), (90, 32)])
    lz.sombrear(cono, COBRE, 4, LUZ, textura=0.5 + escama * 0.3, fuerza_tex=0.4)
    _nieve_encima(lz, cono, 2.5, semilla=7204)
    lz.pintar(lz.trazo([(74, 2), (74, -2)], 0.5), COBRE[3])
    # la ventana alta en arco de la torre (el estudio de Kalamu, siempre encendido)
    arco = np.maximum(lz.poligono([(70, 58), (70, 44), (78, 44), (78, 58)]), lz.elipse(74, 44, 4, 4) * (lz.y < 44.5))
    lz.sombrear(np.clip(lz.desenfocar(arco, 0.6) * 1.5, 0, 1), COBRE[:4], 0.8, LUZ)
    vid = np.maximum(lz.poligono([(71, 57), (71, 44.5), (77, 44.5), (77, 57)]), lz.elipse(74, 44.5, 3, 3) * (lz.y < 45))
    lz.pintar(vid, VENTANA[3])
    lz.pintar(vid * (np.abs(lz.x - 74) < 0.3), COBRE[1])
    lz.sumar_luz(lz.desenfocar(vid, 3), VENTANA[1], 0.45)
    # el balcón con rollos de pergamino colgados
    bal = lz.poligono([(18, 70), (56, 70), (56, 73), (18, 73)])
    lz.sombrear(bal, MADERA, 1, LUZ)
    for i in range(9):
        lz.pintar(lz.trazo([(19 + i * 4.2, 64), (19 + i * 4.2, 70)], 0.35), MADERA[1])
    for i in range(4):
        rx = 22 + i * 9
        rollo = lz.poligono([(rx, 73), (rx + 5, 73), (rx + 5, 84 + (i % 2) * 3), (rx, 84 + (i % 2) * 3)])
        lz.sombrear(rollo, ["#8a7454", "#c9b07e", "#e2cea0", "#fff3d8"], 1, LUZ)
        lz.pintar(lz.trazo([(rx + 1, 77), (rx + 4, 77)], 0.3) * rollo, TINTA[2], 0.8)
        lz.pintar(lz.trazo([(rx + 1, 79.5), (rx + 3.5, 79.5)], 0.3) * rollo, TINTA[2], 0.7)
    _ventana_redonda(lz, 38, 40, 4.5)
    _puerta(lz, 38, base, 12, 20)
    # el letrero: una pluma de cobre sobre la puerta
    lz.pintar(lz.trazo(lz.curva((32, 79), (38, 75), (44, 73), n=12), 1.0, 0.3), COBRE[3])
    pie = lz.elipse(48, base + 1, 42, 2.4) * (lz.y < H)
    lz.sombrear(pie, NIEVE[1:], 1, LUZ)
    return lz.sprite(contorno=0.5)


def taller_taa():
    W, H = 80, 80
    lz = Lienzo(W, H, s=5, semilla=7300)
    base = 78
    muro = lz.poligono([(10, base), (10, 42), (70, 42), (70, base)])
    _muro(lz, muro, 7301)
    tejado = lz.poligono([(4, 44), (40, 18), (76, 44)])
    escama = ((np.sin(lz.x * 1.4 + np.floor(lz.y / 3) * 1.6) > 0.2) * ((lz.y % 3) > 0.6)) * 1.0
    lz.sombrear(tejado, COBRE, 5, LUZ, textura=0.5 + escama * 0.3, fuerza_tex=0.4)
    _nieve_encima(lz, tejado, 5.0, semilla=7302)
    _carambanos(lz, 44.5, 6, 74, 7303)
    # el portalón del taller, abierto, con el fuego de la fragua dentro
    p = _puerta(lz, 32, base, 18, 22, encendida=True)
    lz.pintar(p * (lz.y > base - 6), "#c86a2a", 0.6)
    # faroles colgados de una barra en la fachada
    lz.pintar(lz.trazo([(12, 48), (68, 48)], 0.6), "#2a2a30")
    for i, fx in enumerate((16, 50, 58, 66)):
        lz.pintar(lz.trazo([(fx, 48), (fx, 51)], 0.3), "#2a2a30")
        jaula = lz.poligono([(fx - 2, 51), (fx + 2, 51), (fx + 2.4, 56), (fx - 2.4, 56)])
        lz.sombrear(jaula, COBRE[:4], 0.6, LUZ)
        luz = lz.elipse(fx, 53.5, 1.3, 1.8)
        lz.pintar(luz, VENTANA[3] if i % 2 == 0 else "#3a3456")
        if i % 2 == 0:
            lz.sumar_luz(lz.desenfocar(luz, 3), VENTANA[1], 0.45)
    # la pértiga apoyada y un fuelle
    lz.pintar(lz.trazo([(64, base), (58, 52)], 0.6), COBRE[2])
    fu = lz.poligono([(46, base), (54, base), (52, base - 6), (48, base - 6)])
    lz.sombrear(fu, MADERA, 1, LUZ)
    _ventana_redonda(lz, 40, 34, 3.8)
    pie = lz.elipse(40, base + 1, 34, 2.4) * (lz.y < H)
    lz.sombrear(pie, NIEVE[1:], 1, LUZ)
    return lz.sprite(contorno=0.5)


def gran_archivo():
    W, H = 192, 160
    lz = Lienzo(W, H, s=4, semilla=7400)
    base = 158
    cx = 96
    # la escalinata
    for i in range(5):
        esc = lz.poligono([(40 - i * 3, base - i * 3), (152 + i * 3, base - i * 3), (152 + i * 3, base - i * 3 - 3), (40 - i * 3, base - i * 3 - 3)])
        lz.sombrear(esc, PIEDRA[2:], 1.5, LUZ)
        lz.pintar(esc * (lz.y < base - i * 3 - 2.3), NIEVE[3], 0.7)
    cuerpo_base = base - 15
    cuerpo = lz.poligono([(30, cuerpo_base), (30, 72), (162, 72), (162, cuerpo_base)])
    _muro(lz, cuerpo, 7401, 5, 9)
    # las columnas del pórtico
    for xcol in (46, 66, 126, 146):
        col = lz.poligono([(xcol - 4, cuerpo_base), (xcol - 3.5, 80), (xcol + 3.5, 80), (xcol + 4, cuerpo_base)])
        lz.sombrear(col, PIEDRA[2:], 3, LUZ, textura=(np.abs(np.sin((lz.x - xcol) * 1.6)) > 0.7) * 1.0, fuerza_tex=-0.2)
        cap = lz.poligono([(xcol - 6, 80), (xcol + 6, 80), (xcol + 5, 76), (xcol - 5, 76)])
        lz.sombrear(cap, COBRE, 1, LUZ)
    # el friso con letras doradas
    friso = lz.poligono([(26, 76), (166, 76), (166, 70), (26, 70)])
    lz.sombrear(friso, COBRE, 2, LUZ)
    _nieve_encima(lz, friso, 1.5, semilla=7404)
    _carambanos(lz, 76.5, 28, 164, 7405, largo=5)
    for i in range(18):
        lz.pintar(lz.trazo([(40 + i * 6.4, 72), (42.5 + i * 6.4, 72 + (i % 2))], 0.4), COBRE[0], 0.9)
    # la puerta alta, encendida
    _puerta(lz, cx, cuerpo_base, 26, 44, encendida=True)
    for vx in (30 + 26, 162 - 26):
        pass
    # ventanas altas en arco a los lados
    for vx in (84 - 34, 108 + 34):
        arco = np.maximum(lz.poligono([(vx - 4, 118), (vx - 4, 98), (vx + 4, 98), (vx + 4, 118)]), lz.elipse(vx, 98, 4, 4) * (lz.y < 98.5))
        lz.pintar(arco, VENTANA[2])
        lz.sumar_luz(lz.desenfocar(arco, 3), VENTANA[1], 0.35)
        lz.pintar(arco * (np.abs(lz.x - vx) < 0.4), COBRE[1])
    # el tambor y la cúpula dorada nervada
    tambor = lz.poligono([(54, 72), (54, 60), (138, 60), (138, 72)])
    _muro(lz, tambor, 7402, 4, 6)
    for vx in range(62, 132, 12):
        v = lz.elipse(vx, 66, 2, 3)
        lz.pintar(v, VENTANA[2])
    cup = lz.elipse(cx, 60, 44, 42) * (lz.y < 60)
    nervios = (np.abs(np.sin(np.arctan2(lz.x - cx, 60 - lz.y + 1e-3) * 7)) < 0.12) * cup
    lz.sombrear(cup, COBRE, 26, LUZ, textura=0.5 + nervios * -0.4, fuerza_tex=0.4)
    lz.pintar(nervios, COBRE[1], 0.5)
    lz.sumar_luz(lz.desenfocar(lz.elipse(cx - 16, 34, 10, 14) * cup, 4), "#fff0b0", 0.35)
    _nieve_encima(lz, cup * (lz.x < cx + 10), 2.5, semilla=7403)
    # la linterna de arriba con la pluma
    lin = lz.poligono([(cx - 5, 19), (cx - 5, 12), (cx + 5, 12), (cx + 5, 19)])
    lz.sombrear(lin, COBRE, 2, LUZ)
    lz.pintar(lz.trazo([(cx, 12), (cx, 4)], 0.7), COBRE[3])
    lz.pintar(lz.trazo(lz.curva((cx, 4), (cx + 3, 1), (cx + 6, 0), n=8), 1.0, 0.3), COBRE[4])
    return lz.sprite(contorno=0.5)


def puesto_tinta(k):
    W, H = 56, 48
    lz = Lienzo(W, H, s=6, semilla=7500 + k)
    base = 46
    # los postes y el toldo a rayas
    for px in (6, 50):
        lz.sombrear(lz.trazo([(px, base), (px, 12)], 1.2), MADERA, 0.8, LUZ)
    toldo = lz.poligono([(2, 18), (8, 10), (48, 10), (54, 18), (50, 21), (6, 21)])
    rayas = (np.floor(lz.x / 4) % 2) * 1.0
    col = ["#5a1a4a", "#8a2a6a", "#b84a8a", "#e07ab0"] if k == 0 else ["#1e3a5a", "#2e5a8a", "#4a82b8", "#8ab8e0"]
    lz.sombrear(toldo, col, 2, LUZ, textura=0.3 + rayas * 0.5, fuerza_tex=0.5)
    flecos = toldo * (lz.y > 19.5) * (np.sin(lz.x * 1.6) > 0)
    lz.pintar(flecos, "#f4ece0", 0.8)
    _nieve_encima(lz, toldo, 1.5, semilla=7501 + k)
    # el mostrador
    mostrador = lz.poligono([(6, base), (6, 32), (50, 32), (50, base)])
    lz.sombrear(mostrador, MADERA, 2, LUZ, textura=((lz.y % 3) < 0.5) * 1.0, fuerza_tex=-0.3)
    tabla = lz.poligono([(4, 32), (52, 32), (52, 29.5), (4, 29.5)])
    lz.sombrear(tabla, MADERA[2:], 0.6, LUZ)
    # tinteros de colores, plumas y un rollo de papel
    tintas = ["#2a1e4a", "#8c2028", "#2e5a8a", "#3e7a3e", "#a07020"]
    for i in range(5):
        tx = 10 + i * 6
        bote = lz.poligono([(tx - 2, 29.5), (tx + 2, 29.5), (tx + 1.6, 25), (tx - 1.6, 25)])
        lz.sombrear(bote, ["#141020", tintas[(i + k) % 5], "#c8c0e0"], 0.6, LUZ)
        lz.pintar(lz.circulo(tx - 0.6, 26.5, 0.4) * bote, "#ffffff", 0.8)
        if i % 2 == 0:
            lz.pintar(lz.trazo(lz.curva((tx, 25), (tx + 1, 21), (tx + 3, 18), n=8), 0.8, 0.2), "#f0e8f0")
    rollo = lz.elipse(44, 27.5, 4, 2)
    lz.sombrear(rollo, ["#8a7454", "#c9b07e", "#e2cea0", "#fff3d8"], 0.8, LUZ)
    pie = lz.elipse(28, base + 1, 26, 2) * (lz.y < H)
    lz.sombrear(pie, NIEVE[1:], 0.8, LUZ)
    return lz.sprite(contorno=0.5)


def fuente():
    W, H = 64, 52
    lz = Lienzo(W, H, s=5, semilla=7600)
    cx = 32
    # la taza grande, de piedra
    taza = np.maximum(lz.elipse(cx, 38, 26, 9), lz.poligono([(6, 38), (58, 38), (56, 47), (8, 47)]))
    lz.sombrear(taza, PIEDRA, 4, LUZ)
    borde = lz.elipse(cx, 38, 26, 9) * (1 - lz.elipse(cx, 38, 23, 7))
    lz.sombrear(borde, PIEDRA[2:], 1, LUZ)
    _nieve_encima(lz, borde, 1.2, semilla=7601)
    # la tinta helada dentro: negra, brillante, con vetas violetas
    tinta = lz.elipse(cx, 38, 23, 7)
    lz.sombrear(tinta, TINTA[:5], 4, LUZ)
    lz.pintar(lz.trazo([(18, 36), (28, 34)], 0.8) * tinta, "#b8a8e8", 0.7)
    vetas = lz.trazo([(20, 41), (28, 38), (36, 40), (44, 36)], 0.35) * tinta
    lz.sumar_luz(lz.desenfocar(vetas, 0.8), "#7a2fa0", 0.6)
    lz.pintar(vetas, "#c27ce6", 0.8)
    # el pilar del centro con la pluma de cobre y el chorro, helado en el aire
    pilar = lz.poligono([(cx - 3, 38), (cx - 2.5, 14), (cx + 2.5, 14), (cx + 3, 38)])
    _muro(lz, pilar, 7602, 3, 5)
    lz.pintar(lz.trazo(lz.curva((cx, 14), (cx + 4, 8), (cx + 9, 6), n=10), 1.4, 0.4), COBRE[3])
    chorro = lz.trazo(lz.curva((cx + 2, 14), (cx + 10, 14), (cx + 14, 30), n=16), 1.6, 0.8)
    lz.sombrear(chorro, TINTA[:5], 1, LUZ)
    lz.pintar(lz.trazo(lz.curva((cx + 2, 13.5), (cx + 9.5, 13.5), (cx + 13.5, 29), n=16), 0.4), "#b8a8e8", 0.6)
    for i in range(5):
        cr = lz.poligono([(cx + 13 + i * 0.2, 30 + i), (cx + 14.5, 30 + i), (cx + 14, 33 + i * 0.8)])
        lz.sombrear(cr, TINTA, 0.5, LUZ)
    return lz.sprite(contorno=0.5)


def charco(estado):
    W, H = 48, 28
    lz = Lienzo(W, H, s=6, semilla=7700 + estado)
    cuanto = [1.0, 0.6, 0.25][estado]
    base = lz.elipse(24, 19, 22 * cuanto + 2, 6.5 * cuanto + 1)
    bulto = base * (lz.ruido(3, 2, semilla=7701) > 0.25 + (1 - cuanto) * 0.3)
    forma = np.clip(base * (0.6 if estado else 1.0) + bulto, 0, 1) > 0.5
    forma = forma.astype(float)
    if estado == 0:
        # entero: un montón de tinta helada que sube y tapa el paso
        monton = lz.elipse(24, 14, 18, 10) * (lz.y < 19)
        forma = np.maximum(forma, monton)
    lz.sombrear(forma, TINTA[:5], 5, LUZ, textura=lz.ruido(4, 2, semilla=7702), fuerza_tex=0.1)
    lz.pintar(lz.trazo([(10, 13 if estado == 0 else 17), (20, 10 if estado == 0 else 16)], 0.8) * forma, "#b8a8e8", 0.7)
    vetas = lz.trazo([(8, 20), (16, 16), (24, 19), (34, 14), (40, 18)], 0.35) * forma
    lz.sumar_luz(lz.desenfocar(vetas, 0.8), "#7a2fa0", 0.6 * cuanto)
    lz.pintar(vetas, "#c27ce6", 0.8 * cuanto)
    if estado == 0:
        for i in range(6):
            x0 = 12 + i * 5
            car = lz.poligono([(x0 - 1, 8 + (i % 2)), (x0 + 1, 8 + (i % 2)), (x0, 4 + (i % 3))])
            lz.sombrear(car, TINTA, 0.5, LUZ)
    return lz.sprite(contorno=0.5)


def main():
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def guardar(nombre, partes):
        Image.fromarray(np.concatenate(partes, axis=1) if len(partes) > 1 else partes[0], "RGBA").save(os.path.join(SALIDA, nombre))

    guardar("casa_escriba.png", [casa_escriba(0), casa_escriba(1)])
    guardar("casa_kalamu.png", [casa_kalamu()])
    guardar("taller_taa.png", [taller_taa()])
    guardar("gran_archivo.png", [gran_archivo()])
    guardar("puesto_tinta.png", [puesto_tinta(0), puesto_tinta(1)])
    guardar("fuente.png", [fuente()])
    guardar("charco.png", [charco(k) for k in range(3)])
    # Mauti, en la ciudad: su dibujo de las Ruinas (libre, el 2.º fotograma) con 4 fotogramas para el aldeano:
    # quieto, respira (todo baja un píxel menos los pies), brilla (un poco más claro) y respira otra vez
    m = Image.open(os.path.join(RAIZ, "arte", "mundos", "raiz", "ruinas", "mauti.png")).convert("RGBA").crop((24, 0, 48, 32))
    respira = Image.new("RGBA", (24, 32))
    respira.alpha_composite(m.crop((0, 0, 24, 29)), (0, 1))
    respira.alpha_composite(m.crop((0, 29, 24, 32)), (0, 29))
    brilla = Image.eval(m, lambda v: v)
    px = brilla.load()
    for y in range(32):
        for x in range(24):
            r, g, b, a_ = px[x, y]
            if a_:
                px[x, y] = (min(255, r + 18), min(255, g + 14), min(255, b + 24), a_)
    tira = Image.new("RGBA", (96, 32))
    for i, f in enumerate([m, respira, brilla, respira]):
        tira.alpha_composite(f, (i * 24, 0))
    ald = os.path.join(RAIZ, "arte", "personajes", "aldeanos")
    tira.save(os.path.join(ald, "mauti_anim.png"))
    m.save(os.path.join(ald, "mauti_frente.png"))
    print("Maandiko pintado en", SALIDA)


if __name__ == "__main__":
    main()
