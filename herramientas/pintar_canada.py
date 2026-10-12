"""LOS OBJETOS DE LA CAÑADA DEL ECO, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_canada.py

Genera:
  arte/mundos/raiz/canada/bloque.png     3 × 32×30   una roca caída de la peña (gris, con estratos, musgo y piedras al pie)
  arte/mundos/raiz/canada/tronco.png     2 × 40×18   un tronco seco caído, gris y pardo, con ramas rotas
  arte/mundos/raiz/canada/pedregal.png   8 × 16×16   el decorado del fondo de la garganta: grava, piedrecitas, una
                                                     losa, matojo seco, tomillo en flor, flor de roca, ramitas y una
                                                     mata de hierba verde
  arte/mundos/raiz/canada/cabras.png     8 × 18×16   las cabras de Mbuzi: blanca (pastando, andando ×2, mirando) y
                                                     Tumbo, la negra (lo mismo)
  arte/mundos/raiz/canada/aprisco.png    96×80       la casa de Mbuzi, la cabra montés pastora: una cabaña de piedra
                                                     seca con tejado de lajas, puerta de tablas y un cayado colgado;
                                                     al lado, el pesebre de heno tras el murete de piedra del
                                                     corral, con su portillo de palos
  arte/mundos/raiz/canada/escala.png     3 × 16×16   la ESCALA DE CUERDA de la cornisa: 0 enrollada arriba (cerrada),
                                                     1 un tramo colgando, 2 el último tramo (con las puntas de cuerda)
  arte/mundos/raiz/canada/murcielago.png 6 × 24×20   el MURCIÉLAGO DE ECO (enemigo): colgado, alas arriba, alas abajo,
                                                     gritando, aturdido en el suelo y golpeado (blanco en el juego)
  arte/mundos/raiz/objetos/cencerro.png  2 × 12×12   un cencerro de Mbuzi
  y su icono (16×16) en arte/interfaz/objetos.png (el 23.º)
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_casa_shamba import vetas, rect  # noqa: E402
from pintar_pasarelas import tira, pixeles, MADERA, CONTORNO, GIZA  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "canada")
LUZ = (-0.6, -0.7, 0.5)
# piedra gris de la cañada (la misma que la peña del suelo)
GRIS = ["#1a1c20", "#292c32", "#3a3e45", "#4d5259", "#62686e", "#7a8086", "#949a9e", "#b1b5b6", "#cfd2cf"]
LAJA = ["#16181c", "#23262c", "#32363d", "#454a52", "#5a6068", "#70767e"]
HENO = ["#3d3214", "#5c4a22", "#7a6431", "#958043", "#b09c5c", "#c9b77d"]
CUERDA = ["#3a2a18", "#5c4428", "#80643c", "#a48656", "#c4a874"]


def aprisco():
    W, H = 96, 80
    lz = Lienzo(W, H, s=6, semilla=161)
    suelo = 61
    lz.pintar(lz.desenfocar(lz.elipse(32, suelo, 30, 3.5), 1.2), "#0e0c0a", 0.5)
    # la cabaña: paredes de piedra seca (piedras planas apiladas, cada una con su luz)
    frente = rect(lz, 4, 24, 34, 50)
    lado = lz.poligono([(34, 24), (42, 19), (42, 45), (34, 50)])
    piedras = np.zeros((lz.H, lz.W))
    tono = np.zeros((lz.H, lz.W))
    rng = np.random.default_rng(162)
    for fila in range(10):
        y = 25 + fila * 2.6
        x = 3 + (fila % 2) * 2.2
        while x < 44:
            largo = 3 + rng.random() * 3
            p = lz.elipse(x + largo / 2, y + 1.1, largo / 2, 1.2)
            piedras = np.maximum(piedras, p)
            tono = np.where(p > 0.5, rng.random(), tono)
            x += largo + 0.4
    pared = np.clip(frente + lado, 0, 1)
    lz.pintar(pared, "#14161a")
    lz.sombrear(piedras * pared, GRIS[1:8], 1.2, LUZ, textura=tono, fuerza_tex=0.45)
    lz.pintar(lado * piedras, "#0b0c0e", 0.35)                    # el lado, en sombra
    # la puerta de tablas y un ventanuco
    puerta = rect(lz, 14, 33, 22, 50)
    lz.sombrear(puerta, MADERA[1:6], 2, LUZ, textura=vetas(lz, 0.4, 9, False, 163), fuerza_tex=0.45)
    lz.pintar(puerta * ((lz.x % 2.7) < 0.45), MADERA[0], 0.8)
    for y in (36, 46):
        lz.pintar(rect(lz, 14, y, 22, y + 0.9), MADERA[1], 0.9)
    lz.pintar(lz.circulo(20.5, 42, 0.6), "#c9b07e")
    ventana = rect(lz, 26, 31, 31, 36)
    lz.pintar(ventana, "#0c0a0a")
    lz.brillo(lz.elipse(28.5, 34, 1.6, 1.2), "#e6a852", 2.0, 0.6)    # un candil dentro
    # el cayado colgado junto a la puerta
    lz.pintar(lz.trazo([(10, 49), (10, 30)], 0.7), MADERA[5])
    lz.pintar(lz.trazo([tuple(p) for p in lz.curva((10, 30), (10, 27), (12.6, 26.5), (12.8, 29), n=20)], 0.7), MADERA[5])
    # el tejado de lajas, a dos aguas, con las lajas solapadas
    tejado = lz.poligono([(1, 25), (22, 9), (26, 9), (37, 25)])
    faldon = lz.poligono([(26, 9), (45, 5), (44, 20), (37, 25)])
    filas_l = ((lz.y + (lz.x * 0.15)) % 3.2) / 3.2
    juntas = np.abs(((lz.x + np.floor(lz.y / 3.2) * 2.3) % 5.0) - 2.5) < 0.35
    lz.sombrear(faldon, LAJA, 3, LUZ, textura=filas_l, fuerza_tex=0.4)
    lz.sombrear(tejado, LAJA[1:] + ["#888e96"], 5, LUZ, textura=filas_l, fuerza_tex=0.55)
    lz.pintar(np.clip(tejado + faldon, 0, 1) * (filas_l > 0.86), LAJA[0], 0.8)
    lz.pintar(np.clip(tejado + faldon, 0, 1) * juntas, LAJA[1], 0.6)
    musgo = np.clip((lz.ruido(1.5, 2, semilla=164) - 0.62) * 4, 0, 1) * np.clip(tejado + faldon, 0, 1)
    lz.pintar(musgo, "#4d6436", 0.8)
    lz.pintar(lz.trazo([(22, 9), (26, 9), (45, 5)], 1.2), LAJA[5])
    # dentro del corral: el pesebre de heno (de palos, lleno hasta arriba) y el abrevadero de piedra
    lz.pintar(lz.desenfocar(lz.elipse(53, 54, 9, 1.8), 0.8), "#0e0c0a", 0.6)
    pesebre = rect(lz, 46, 45, 60, 54)
    lz.sombrear(pesebre, MADERA[1:6], 2, LUZ, textura=vetas(lz, 0.4, 9, True, 167), fuerza_tex=0.4)
    lz.pintar(pesebre * ((lz.x % 3.5) < 0.6), MADERA[0], 0.7)
    heno = lz.elipse(53, 44.5, 8, 3.6)
    lz.sombrear(heno, HENO, 3, LUZ, textura=vetas(lz, 0.3, 7, True, 166), fuerza_tex=0.5)
    pajas = np.zeros((lz.H, lz.W))
    for k in range(9):
        x0 = 46.5 + k * 1.6
        pajas = np.maximum(pajas, lz.trazo([(x0, 43), (x0 + (k % 3 - 1) * 1.2, 40 + (k % 2))], 0.4))
    lz.pintar(pajas, HENO[5], 0.9)
    # el corral grande, a la derecha: hierba pisada y un murete de piedra seca irregular, con postes de madera
    borde = [(46, 54), (58, 49), (72, 47), (86, 46), (93, 49), (94, 60), (93, 70), (90, 76), (70, 78), (48, 77)]
    patio = lz.poligono(borde)
    lz.sombrear(patio, ["#3a4228", "#4a5432", "#5a663c", "#6c7646"], 4, LUZ, textura=lz.ruido(0.8, 2, semilla=169), fuerza_tex=0.35)
    lz.pintar(patio * (lz.ruido(1.2, 1, semilla=170) > 0.72), "#5c4a30", 0.6)          # tierra pisada
    rng_c = np.random.default_rng(172)
    piedras_c = np.zeros((lz.H, lz.W))
    for (a_, b_) in zip(borde[1:7], borde[2:8]):                                       # la parte de atrás y la derecha
        largo_t = float(np.hypot(b_[0] - a_[0], b_[1] - a_[1]))
        t = 0.0
        while t < largo_t:
            r = 1.0 + rng_c.random() * 1.0
            f = t / largo_t
            cx, cy = a_[0] + (b_[0] - a_[0]) * f, a_[1] + (b_[1] - a_[1]) * f + rng_c.random() - 0.5
            piedras_c = np.maximum(piedras_c, lz.elipse(cx, cy, r * 1.2, r * 0.85))
            if rng_c.random() < 0.5:
                piedras_c = np.maximum(piedras_c, lz.elipse(cx + 0.5, cy - 1.6, r, r * 0.7))
            t += r * 1.9
    lz.pintar(lz.desenfocar(np.clip(piedras_c, 0, 1), 0.5), "#14161a", 0.9)
    lz.sombrear(piedras_c, GRIS[2:9], 0.9, LUZ, textura=lz.ruido(0.5, 1, semilla=171), fuerza_tex=0.4)
    for (x, y) in ((72, 47), (93, 60), (90, 76)):                                       # postes de madera
        lz.pintar(lz.trazo([(x, y + 1), (x, y - 6)], 0.9), MADERA[5])
        lz.pintar(lz.circulo(x, y - 6, 0.6), MADERA[6])
    # un abrevadero de piedra en el corral y un poco de heno tirado
    pila = lz.poligono([(76, 64), (88, 62), (88, 66), (76, 68)])
    lz.sombrear(pila, GRIS[2:8], 2, LUZ)
    lz.pintar(lz.poligono([(77, 64.4), (87, 62.6), (87, 64), (77, 65.6)]), "#346161")
    for k in range(8):
        x0_, y0_ = 60 + k * 2.3, 70 + (k % 3)
        lz.pintar(lz.trazo([(x0_, y0_), (x0_ + 2, y0_ - 0.6)], 0.4), HENO[4], 0.9)
    # el murete del corral, delante: piedra seca irregular, con un portillo de palos a la izquierda
    piedras_m = np.zeros((lz.H, lz.W))
    x = 45.0
    while x < 91:
        r = 1.1 + rng_c.random() * 1.1
        y = 77.5 - (x - 45) * 0.02 + rng_c.random() * 0.8
        piedras_m = np.maximum(piedras_m, lz.elipse(x, y, r * 1.25, r * 0.9))
        if rng_c.random() < 0.6:
            piedras_m = np.maximum(piedras_m, lz.elipse(x + 0.8, y - 1.8, r * 0.9, r * 0.7))
        x += r * 2.0
    lz.pintar(lz.desenfocar(lz.elipse(70, 79, 26, 1.4), 0.8), "#0e0c0a", 0.6)
    lz.pintar(lz.desenfocar(np.clip(piedras_m, 0, 1), 0.5), "#14161a", 0.9)
    lz.sombrear(piedras_m, GRIS[2:9], 1.0, LUZ, textura=lz.ruido(0.5, 1, semilla=165), fuerza_tex=0.4)
    for xx in (39, 43.5):                                     # el portillo
        lz.pintar(lz.trazo([(xx, 78), (xx, 69)], 0.8), MADERA[5])
    for yy in (71, 74):
        lz.pintar(lz.trazo([(38.5, yy), (44, yy - 0.4)], 0.55), MADERA[4])
    return lz.sprite(contorno=CONTORNO)


def bloque(k):
    """Una roca caída de la peña: gris como las paredes, con estratos inclinados, una grieta, musgo encima y
    piedrecitas desprendidas al pie."""
    W, H = 32, 30
    lz = Lienzo(W, H, s=6, semilla=191 + k)
    rng = np.random.default_rng(192 + k)
    lz.pintar(lz.desenfocar(lz.elipse(16, 27, 15, 2.6), 0.8), "#0e0c0a", 0.6)
    formas = [
        [(3, 27), (2, 16), (6, 6), (11, 2), (17, 3), (22, 9), (24, 18), (26, 27)],          # una losa alta e inclinada
        [(1, 27), (2, 19), (8, 13), (18, 11), (27, 13), (31, 20), (30, 27)],                 # ancha y aplastada
        [(3, 27), (3, 15), (9, 7), (15, 7), (15, 27)],                                       # partida en dos: la mitad izq.
    ]
    roca = lz.poligono(formas[k])
    if k == 2:
        roca = np.maximum(roca, lz.poligono([(17, 27), (17, 10), (22, 6), (28, 11), (30, 20), (29, 27)]))
    estratos = np.sin((lz.y * 0.9 + lz.x * (0.25 + k * 0.1)) * 1.1) * 0.5 + 0.5
    lz.sombrear(roca, GRIS[1:8], 7, LUZ, textura=estratos * 0.5 + lz.ruido(1.2, 2, semilla=193 + k) * 0.5, fuerza_tex=0.45)
    # la cara de arriba, más clara (le da el sol), y el canto
    arriba = roca * (lz.y < (8, 16, 11)[k] + (lz.x - 16) * 0.08)
    lz.pintar(arriba, GRIS[6], 0.35)
    lz.pintar(roca * (np.abs(estratos - 0.5) < 0.05), GRIS[1], 0.6)
    grieta = lz.trazo([(8 + k * 5, 8 + k * 3), (11 + k * 4, 15 + k), (10 + k * 5, 23)], 0.6)
    lz.pintar(grieta * roca, "#0c0d10", 0.85)
    musgo = np.clip((lz.ruido(1.5, 2, semilla=194 + k) - 0.55) * 4, 0, 1) * arriba
    lz.pintar(musgo, "#4d6436", 0.85)
    for _ in range(4):
        x, y = 4 + rng.random() * 24, 26 + rng.random() * 2
        p = lz.elipse(x, y, 1.4 + rng.random(), 1.0)
        lz.sombrear(p, GRIS[2:8], 1, LUZ)
    return lz.sprite(contorno=CONTORNO)


def tronco(k):
    """Un tronco seco caído: corteza gris y parda agrietada, el corte del tronco con sus anillos y ramas rotas."""
    W, H = 40, 18
    lz = Lienzo(W, H, s=6, semilla=201 + k)
    lz.pintar(lz.desenfocar(lz.elipse(20, 15.5, 18, 2), 0.8), "#0e0c0a", 0.55)
    cuerpo = lz.trazo([(4, 11), (36, 9 + k)], 7.0, 5.5)
    corteza = vetas(lz, 0.4, 11, True, 202 + k)
    lz.sombrear(cuerpo, ["#2a2420", "#433a32", "#5e534a", "#7a6e62", "#968a7c"], 3.5, LUZ, textura=corteza, fuerza_tex=0.55)
    lz.pintar(cuerpo * (corteza > 0.78), "#1e1a16", 0.7)
    # el corte, con los anillos
    corte = lz.elipse(36, 9 + k, 2.4, 3.4)
    lz.sombrear(corte, ["#7a5a3a", "#a07a50", "#c49a6a"], 2, LUZ)
    for r in (1.0, 2.0):
        lz.pintar(np.clip(lz.elipse(36, 9 + k, r * 0.7, r) - lz.elipse(36, 9 + k, r * 0.7 - 0.3, r - 0.4), 0, 1), "#6a4a2a", 0.7)
    # ramas rotas
    for (x, y, dx, dy) in ((12, 8, -3, -6), (24, 7.5, 2, -5), (18, 13, 3, 3)):
        lz.sombrear(lz.trazo([(x, y), (x + dx, y + dy)], 1.6, 0.8), ["#433a32", "#5e534a", "#7a6e62"], 0.8, LUZ)
    return lz.sprite(contorno=CONTORNO)


def pedregal(k):
    """Las piezas del fondo de la garganta (16×16, no estorban): 0 grava, 1 piedrecitas, 2 una losa plana,
    3 matojo seco, 4 tomillo en flor, 5 flor de roca amarilla, 6 ramitas secas, 7 una mata de hierba verde."""
    lz = Lienzo(16, 16, s=8, semilla=211 + k)
    rng = np.random.default_rng(212 + k)
    if k == 0:
        for _ in range(14):
            x, y = 2 + rng.random() * 12, 6 + rng.random() * 8
            lz.sombrear(lz.elipse(x, y, 0.8 + rng.random() * 0.5, 0.6), GRIS[3:8], 0.6, LUZ)
    elif k == 1:
        for (x, y, r) in ((5, 11, 2.0), (9, 12, 1.5), (11, 9.5, 1.2)):
            lz.pintar(lz.desenfocar(lz.elipse(x + 0.6, y + 1.2, r, r * 0.4), 0.4), "#0e0c0a", 0.5)
            lz.sombrear(lz.elipse(x, y, r, r * 0.75), GRIS[2:8], r, LUZ)
    elif k == 2:
        lz.pintar(lz.desenfocar(lz.elipse(8.6, 12, 6, 2), 0.5), "#0e0c0a", 0.5)
        losa = lz.poligono([(2, 11), (5, 8.5), (12, 8), (14, 10.5), (11, 12.5), (4, 12.8)])
        lz.sombrear(losa, GRIS[2:8], 2, LUZ, textura=lz.ruido(0.6, 1, semilla=213), fuerza_tex=0.3)
        lz.pintar(lz.trazo([(6, 9.5), (9, 11.5)], 0.35), GRIS[1], 0.8)
    elif k in (3, 4):
        tallos = np.zeros((lz.H, lz.W))
        for j in range(9):
            a = -0.9 + j * 0.22
            tallos = np.maximum(tallos, lz.trazo([(8, 14), (8 + np.sin(a) * 6, 14 - np.cos(a) * (5 + rng.random() * 3))], 0.45))
        lz.pintar(tallos, "#8a7a4a" if k == 3 else "#5a6a3a")
        if k == 4:
            for j in range(7):
                lz.pintar(lz.circulo(4 + rng.random() * 8, 6 + rng.random() * 4, 0.7), "#b58ad6")
    elif k == 5:
        lz.pintar(lz.trazo([(8, 14), (8, 9)], 0.5), "#4d6436")
        for j in range(5):
            a = j * 2 * np.pi / 5
            lz.pintar(lz.elipse(8 + np.cos(a) * 1.6, 8 + np.sin(a) * 1.6, 1.1, 1.1), "#f1c27a")
        lz.pintar(lz.circulo(8, 8, 0.9), "#b2721a")
    elif k == 6:
        for (x0, y0, x1, y1) in ((3, 12, 12, 10), (6, 13, 9, 9), (9, 11, 13, 13)):
            lz.pintar(lz.trazo([(x0, y0), (x1, y1)], 0.5), "#5e4a36")
    else:
        mata = np.zeros((lz.H, lz.W))
        for j in range(12):
            a = -1.0 + j * 0.18
            mata = np.maximum(mata, lz.trazo([(8, 14), (8 + np.sin(a) * 6.5, 14 - np.cos(a) * (4 + rng.random() * 5))], 0.5, 0.25))
        lz.pintar(mata, "#5d793e")
        lz.pintar(mata * (lz.y < 10), "#90a153", 0.8)
    return lz.sprite(contorno=CONTORNO * 0.7)


def cabra(k):
    """Las cabras de Mbuzi (18×16, mirando a la derecha): 0-3 blanca con manchas grises, 4-7 Tumbo, la negra.
    0 pastando (cabeza abajo) · 1-2 andando · 3 mirando (cabeza alta)."""
    negra = k >= 4
    pose = k % 4
    lz = Lienzo(18, 16, s=8, semilla=221 + k)
    piel = ["#1a1a1e", "#2a2a30", "#3c3c44", "#52525c"] if negra else ["#7a7a72", "#b8b6aa", "#dcdad0", "#f4f2ea"]
    lz.pintar(lz.desenfocar(lz.elipse(9, 15, 7, 1.2), 0.5), "#0e0c0a", 0.5)
    # patas
    paso = {1: 1.0, 2: -1.0}.get(pose, 0.0)
    for (x, d) in ((5.5, paso), (7.5, -paso), (11.5, -paso), (13.5, paso)):
        lz.pintar(lz.trazo([(x, 10), (x + d * 0.6, 14.6)], 0.9), piel[1])
        lz.pintar(lz.trazo([(x + d * 0.6, 14.2), (x + d * 0.6, 15)], 0.9), "#2a2420")
    cuerpo = lz.elipse(9.5, 9, 5.6, 3.2)
    lz.sombrear(cuerpo, piel, 3, LUZ, textura=lz.ruido(0.6, 2, semilla=222 + k), fuerza_tex=0.3)
    if not negra:
        lz.pintar(lz.elipse(8, 8.5, 1.6, 1.2), "#9a988e", 0.8)
    lz.pintar(lz.trazo([(4.2, 7.5), (3, 6)], 0.7), piel[2])                    # el rabito
    # la cabeza: abajo pastando, alta mirando, al frente andando
    hx, hy = (15.5, 11.5) if pose == 0 else ((15.2, 4.5) if pose == 3 else (15.5, 6.5))
    lz.pintar(lz.trazo([(13.5, 8), (hx - 0.5, hy + 0.5)], 2.2), piel[2])
    cabeza = lz.elipse(hx, hy, 2.0, 1.6)
    lz.sombrear(cabeza, piel, 1.5, LUZ)
    lz.pintar(lz.trazo([(hx - 0.6, hy - 1.2), (hx - 2.2, hy - 3.2), (hx - 3.2, hy - 2.6)], 0.55), "#a59a80")   # cuernos
    lz.pintar(lz.trazo([(hx - 1.2, hy - 0.4), (hx - 2.4, hy + 0.4)], 0.6), piel[1])                           # oreja
    lz.pintar(lz.circulo(hx + 0.4, hy - 0.3, 0.35), "#0e0c0a")
    lz.pintar(lz.trazo([(hx + 1.2, hy + 1.2), (hx + 1.0, hy + 2.4)], 0.5), piel[3] if negra else "#c8c6bc")    # barbita
    return lz.sprite(contorno=CONTORNO * 0.8)


def escala(k):
    """La escala de cuerda. 0: enrollada en lo alto de la cornisa, atada a una estaca (cerrada) ·
    1: un tramo colgando (dos cuerdas y un peldaño de madera) · 2: el último tramo, con las puntas sueltas."""
    W, H = 16, 16
    lz = Lienzo(W, H, s=8, semilla=171 + k)
    if k == 0:
        lz.pintar(lz.desenfocar(lz.elipse(8, 14, 7, 1.6), 0.6), "#0e0c0a", 0.6)
        for xx in (2.5, 13.5):                                    # las estacas
            estaca = lz.trazo([(xx, 14), (xx, 5)], 1.4)
            lz.sombrear(estaca, MADERA[1:7], 1, LUZ, textura=vetas(lz, 0.4, 7, False, 172), fuerza_tex=0.4)
        rollo = lz.elipse(8, 10, 6.2, 3.6)
        vueltas = (np.sin((lz.x - 8) * 2.2) * 0.5 + 0.5)
        lz.sombrear(rollo, CUERDA, 3, LUZ, textura=vetas(lz, 0.3, 5, False, 173) * 0.5 + vueltas * 0.5, fuerza_tex=0.5)
        for xx in (4.5, 7, 9.5, 12):                              # los peldaños asomando
            lz.sombrear(lz.trazo([(xx, 7.4), (xx + 0.6, 12.6)], 1.1), MADERA[2:7], 0.6, LUZ)
        lz.pintar(lz.trazo([(2.5, 8), (5, 9)], 0.6), CUERDA[3])     # los nudos a las estacas
        lz.pintar(lz.trazo([(13.5, 8), (11, 9)], 0.6), CUERDA[3])
        return lz.sprite(contorno=CONTORNO * 0.8)
    # la sombra de la escala sobre la peña
    for xx in (3.5, 12.5):
        lz.pintar(lz.trazo([(xx + 1.2, 0), (xx + 1.2, 16)], 1.0), "#0b0c0e", 0.45)
    largo = 16 if k == 1 else 11
    for xx in (3.5, 12.5):                                        # las dos cuerdas, trenzadas
        cuerda = lz.trazo([(xx, 0), (xx + (0.3 if k == 2 else 0), largo)], 1.2)
        trenza = ((lz.y + (lz.x - xx) * 1.3) % 1.8) / 1.8
        lz.sombrear(cuerda, CUERDA, 0.8, LUZ, textura=trenza, fuerza_tex=0.55)
    peldanos = (3.5, 11.5) if k == 1 else (3.5,)
    for yy in peldanos:                                           # los peldaños de madera, atados
        lz.pintar(lz.trazo([(3.8, yy + 1.1), (12.8, yy + 1.1)], 1.0), "#0b0c0e", 0.5)
        p = lz.trazo([(3, yy), (13, yy)], 1.5)
        lz.sombrear(p, MADERA[2:8], 0.8, LUZ, textura=vetas(lz, 0.4, 9, True, 174 + int(yy)), fuerza_tex=0.4)
        for xx in (3.5, 12.5):
            lz.pintar(lz.circulo(xx, yy, 0.9), CUERDA[1], 0.9)
    if k == 2:
        for xx in (3.5, 12.8):                                    # las puntas deshilachadas
            for d in (-0.6, 0, 0.6):
                lz.pintar(lz.trazo([(xx, 10.5), (xx + d * 1.6, 13.5)], 0.35), CUERDA[3])
    return lz.sprite(contorno=CONTORNO * 0.8)


# el murciélago: cuerpo de piedra gris con grietas de Giza, alas de piel oscura violácea
PIEL_ALA = ["#120e16", "#1e1824", "#2c2434", "#3c3246", "#4e4258", "#62566c"]


def murcielago(estado):
    """El MURCIÉLAGO DE ECO, de frente. 0 colgado boca abajo, envuelto en las alas · 1 alas arriba · 2 alas abajo ·
    3 gritando (alas abiertas del todo, boca abierta con luz violeta) · 4 aturdido en el suelo (alas caídas, ojos
    en espiral) · 5 golpeado (igual que 4; se dibuja blanco en el juego)."""
    W, H = 24, 20
    lz = Lienzo(W, H, s=8, semilla=181 + estado)
    suelo = estado in (4, 5)
    cx = 12
    if estado == 0:
        # colgado de un saliente de roca, cabeza abajo, envuelto en las alas como un capullo
        roca = lz.elipse(cx, 1.5, 6, 2.2)
        lz.sombrear(roca, GRIS[1:7], 1.5, LUZ)
        for xx in (cx - 1.2, cx + 1.2):
            lz.pintar(lz.trazo([(xx, 3), (xx, 5)], 0.6), GRIS[2])
        capullo = lz.elipse(cx, 10, 4.2, 6)
        lz.sombrear(capullo, PIEL_ALA, 3, LUZ, textura=((lz.x - cx) % 2.2 < 0.6) * 1.0, fuerza_tex=0.4)
        cabeza = lz.circulo(cx, 15.5, 2.6)
        lz.sombrear(cabeza, GRIS[2:8], 1.5, LUZ, textura=lz.ruido(0.6, 1, semilla=182), fuerza_tex=0.3)
        for xx in (cx - 2, cx + 2):                                 # orejas, hacia abajo
            lz.pintar(lz.poligono([(xx - 1, 16.5), (xx + 1, 16.5), (xx + (0.6 if xx > cx else -0.6), 19)]), GRIS[3])
        for xx in (cx - 1, cx + 1):                                 # ojos cerrados
            lz.pintar(lz.trazo([(xx - 0.5, 14.8), (xx + 0.5, 14.8)], 0.3), GIZA[2])
        return lz.sprite(contorno=CONTORNO)
    cy = 15 if suelo else 11
    if suelo:
        lz.pintar(lz.desenfocar(lz.elipse(cx, 18.5, 9, 1.4), 0.6), "#0e0c0a", 0.6)
    # las alas: dedos largos y la membrana entre ellos (arriba, abajo, abiertas del todo o caídas)
    if estado == 1:
        puntas = [(-11, -7), (-9, -2), (-6, 1)]
    elif estado == 2:
        puntas = [(-10, 6), (-7, 8), (-4, 7)]
    elif estado == 3:
        puntas = [(-12, -7), (-12, -1), (-10, 4)]
    else:
        puntas = [(-10, 3), (-8, 4), (-5, 4)]
    for lado in (-1, 1):
        hombro = (cx + lado * 2.5, cy - 1.5)
        dedos = [(cx + lado * -dx, cy + dy) for (dx, dy) in puntas]
        codo = (cx + lado * (7.5 if estado == 3 else 6.5), cy - (4 if estado in (1, 3) else (-1 if estado == 2 else -2)))
        membrana = lz.poligono([hombro, codo] + dedos + [(cx + lado * 2.5, cy + 2.5)])
        lz.sombrear(membrana, PIEL_ALA, 3, LUZ, textura=lz.ruido(0.7, 2, semilla=183), fuerza_tex=0.3)
        # los dedos (huesos) y el borde ondulado
        for d in dedos:
            lz.pintar(lz.trazo([codo, d], 0.55), PIEL_ALA[5])
        lz.pintar(lz.trazo([hombro, codo], 0.8), GRIS[4])
        lz.pintar(lz.circulo(codo[0], codo[1], 0.8), GRIS[5])
        # rasgones de Giza en la membrana
        lz.pintar(lz.trazo([((codo[0] + dedos[0][0]) / 2, (codo[1] + dedos[0][1]) / 2), dedos[1]], 0.35), GIZA[3], 0.8)
    # el cuerpo de piedra y la cabeza con orejas grandes
    cuerpo = lz.elipse(cx, cy + 1, 3, 4)
    lz.sombrear(cuerpo, GRIS[2:8], 2, LUZ, textura=lz.ruido(0.6, 2, semilla=184), fuerza_tex=0.35)
    grieta = lz.trazo([(cx - 0.5, cy - 1.5), (cx + 0.6, cy + 0.5), (cx - 0.3, cy + 3)], 0.45)
    lz.pintar(grieta, GIZA[3], 0.9)
    lz.brillo(grieta, GIZA[3], 1.2, 0.5)
    hy = cy - 4.5
    for lado in (-1, 1):
        oreja = lz.poligono([(cx + lado * 0.4, hy - 1.5), (cx + lado * 3.2, hy - 7), (cx + lado * 4.6, hy - 0.2), (cx + lado * 2.5, hy + 0.8)])
        lz.sombrear(oreja, GRIS[2:7], 1.5, LUZ)
        lz.pintar(lz.poligono([(cx + lado * 1.6, hy - 1.6), (cx + lado * 3.1, hy - 5.2), (cx + lado * 3.7, hy - 0.8)]), "#6e4258", 0.9)
    cabeza = lz.circulo(cx, hy, 2.9)
    lz.sombrear(cabeza, GRIS[2:8], 1.6, LUZ, textura=lz.ruido(0.6, 1, semilla=185), fuerza_tex=0.3)
    # los ojos violetas (en espiral si está aturdido) y la boca
    for lado in (-1, 1):
        ox, oy = cx + lado * 1.2, hy - 0.3
        if suelo:
            t = np.linspace(0, 3 * np.pi, 16)
            lz.pintar(lz.trazo([(ox + np.cos(a) * a * 0.1, oy + np.sin(a) * a * 0.1) for a in t], 0.3), GIZA[3])
        else:
            lz.pintar(lz.circulo(ox, oy, 0.75), GIZA[3])
            lz.brillo(lz.circulo(ox, oy, 0.5), GIZA[3], 1.0, 0.8)
            lz.pintar(lz.circulo(ox - 0.2, oy - 0.25, 0.25), "#f4e8ff")
    if estado == 3:
        boca = lz.elipse(cx, hy + 1.9, 1.7, 1.5)
        lz.pintar(boca, "#1a0a20")
        lz.brillo(boca, GIZA[3], 2.5, 0.9)
        for lado in (-1, 1):
            lz.pintar(lz.trazo([(cx + lado * 0.7, hy + 1.0), (cx + lado * 0.6, hy + 1.8)], 0.3), "#e8e4dc")
    else:
        for lado in (-1, 1):                                     # colmillitos
            lz.pintar(lz.trazo([(cx + lado * 0.7, hy + 1.6), (cx + lado * 0.6, hy + 2.3)], 0.3), "#e8e4dc")
    # las patitas
    for lado in (-1, 1):
        lz.pintar(lz.trazo([(cx + lado * 1.2, cy + 4.5), (cx + lado * 1.6, cy + 6)], 0.45), GRIS[3])
    return lz.sprite(contorno=CONTORNO)


# el cencerro: de cobre viejo, con su badajo y la correa de cuero
CENCERRO_COL = {"o": "3a1a0c", "c": "9a4e24", "C": "c06a32", "L": "f4b470", "B": "ffe0b0", "h": "5c3e26",
                "H": "a37036", "n": "1e1915"}
CENCERRO_1 = [
    "............",
    "...hHHHh....",
    "..h....H....",
    "...oooo.....",
    "..ocCLLo....",
    "..ocCLBo....",
    "..ocCCLo....",
    ".occCCLLo...",
    ".occCCCLo...",
    ".oooonooo...",
    ".....n......",
    "............",
]
CENCERRO_2 = [
    "............",
    "....hHHHh...",
    "....H....h..",
    ".....oooo...",
    "....oLLCco..",
    "....oBLCco..",
    "....oLCCco..",
    "...oLLCCcco.",
    "...oLCCCcco.",
    "...ooonoooo.",
    "......n.....",
    "............",
]
ICONO = [
    "................",
    "....hHHHHHh.....",
    "...h......H.....",
    "...H......h.....",
    "....oooooo......",
    "...ocCCLLLo.....",
    "...ocCCLLBo.....",
    "...ocCCLLBo.....",
    "..occCCLLLLo....",
    "..occCCCLLLo....",
    "..occcCCCLLLo...",
    ".occcCCCCLLLo...",
    ".oooooonnooooo..",
    ".......nn.......",
    "................",
    "................",
]


def main():
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(aprisco(), "RGBA").save(os.path.join(SALIDA, "aprisco.png"))
    tira([escala(k) for k in range(3)]).save(os.path.join(SALIDA, "escala.png"))
    tira([bloque(k) for k in range(3)]).save(os.path.join(SALIDA, "bloque.png"))
    tira([tronco(k) for k in range(2)]).save(os.path.join(SALIDA, "tronco.png"))
    tira([pedregal(k) for k in range(8)]).save(os.path.join(SALIDA, "pedregal.png"))
    tira([cabra(k) for k in range(8)]).save(os.path.join(SALIDA, "cabras.png"))
    tira([murcielago(k) for k in range(6)]).save(os.path.join(SALIDA, "murcielago.png"))
    hoja = Image.new("RGBA", (24, 12), (0, 0, 0, 0))
    hoja.alpha_composite(pixeles(CENCERRO_1, CENCERRO_COL), (0, 0))
    hoja.alpha_composite(pixeles(CENCERRO_2, CENCERRO_COL), (12, 0))
    hoja.save(os.path.join(RAIZ, "arte", "mundos", "raiz", "objetos", "cencerro.png"))
    # el icono de la mochila: el 23.º de objetos.png (índice 22)
    ruta = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    n = max(23, viejos.width // 16)
    iconos = Image.new("RGBA", (16 * n, 16), (0, 0, 0, 0))
    iconos.alpha_composite(viejos.crop((0, 0, min(viejos.width, 16 * 22), 16)), (0, 0))
    if viejos.width > 16 * 23:
        iconos.alpha_composite(viejos.crop((16 * 23, 0, viejos.width, 16)), (16 * 23, 0))
    iconos.alpha_composite(pixeles(ICONO, CENCERRO_COL), (16 * 22, 0))
    iconos.save(ruta)
    print("Objetos de la Cañada del Eco en", SALIDA)


if __name__ == "__main__":
    main()
