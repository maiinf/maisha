"""LA SECCIÓN PROHIBIDA (Sigilia), pintada con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_seccion_prohibida.py

Genera en arte/mundos/sigilia/seccion/:
  grimorio.png  5 × 128×104  EL GRIMORIO DE TINTA (jefe final de Sigilia; opción A): un códice colosal de cuero
                púrpura con cantoneras y broches de oro, abierto de par en par y flotando; en el lomo, clavada, la
                PLUMA DEL PRIMER NOMBRE (dorada); dos ojos en las páginas y renglones de tinta que gotean.
                0 y 1 flota (en el 1 parpadea) · 2 furioso (los ojos encendidos, las páginas se levantan, la tinta
                rebosa) · 3 ATURDIDO (caído boca arriba en el suelo, una página rasgada, ojos en espiral) ·
                4 aturdido y golpeado (blanco)
  mano.png      2 × 48×56    una MANO DE TINTA del Grimorio, con garras de plumilla de oro: 0 alzada (abierta,
                amenazando) · 1 golpe (plana contra el suelo, con su charco)
  sombra.png    5 × 32×28    SOMBRA DE RENGLÓN: una tira de tinta viva con letras que le corren por el lomo y dos
                ojos blancos. 0 y 1 repta · 2 se lanza (se alza, la boca abierta) · 3 FIJADA (sólida y pálida, con
                brillo: ahí se le puede dar) · 4 golpeada (blanco)
  pedestal.png  6 × 24×36    los PEDESTALES de los sigilos: columna corta de mármol con un cuenco de oro y su runa.
                0 fuego apagado · 1 fuego encendido · 2 hielo apagado · 3 hielo encendido · 4 rayo apagado ·
                5 rayo encendido
  atril.png     2 × 16×30    un ATRIL DEL ÍNDICE con su ficha: 0 apagado · 1 encendido (la ficha brilla)
  sello.png     2 × 64×48    el TRIPLE SELLO: una verja de oro con tres discos de runa. 0 cerrado · 1 abierto
                (las dos hojas recogidas a los lados)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "sigilia", "seccion")
LUZ = (-0.6, -0.7, 0.5)
CUERO = ["#12061c", "#241038", "#3c1c5a", "#582e80", "#7848a4", "#a070c8"]
ORO = ["#2e2008", "#5c4416", "#94702a", "#c89a3e", "#f0d27a", "#fff4c4"]
PAPEL = ["#5a4a3a", "#8a765c", "#b8a482", "#dccba8", "#f2e6c8", "#fffaea"]
TINTA = ["#05030a", "#0e0818", "#1c1030", "#2e1c4a", "#4a3070", "#7a5aa8"]
MARMOL = ["#1c1230", "#2e2048", "#463468", "#62508a", "#8472aa", "#b0a2d0"]
ELEMENTO = {"fuego": ["#7a1408", "#c83a10", "#ff6a20", "#ffc070"], "hielo": ["#1f4a70", "#4a94c8", "#a0dcf4", "#f4fcff"],
            "rayo": ["#6a5208", "#d8b020", "#ffe860", "#ffffe0"]}
RUNAS = {"fuego": [[(0, 1), (0, -0.8)], [(-0.7, -0.1), (0, 0.35), (0.7, -0.1)], [(-0.45, 0.75), (0.45, 0.75)]],
         "hielo": [[(0, -1), (0.65, 0), (0, 1), (-0.65, 0), (0, -1)], [(-0.95, -0.55), (0.95, 0.55)], [(-0.95, 0.55), (0.95, -0.55)]],
         "rayo": [[(0.45, -1), (-0.45, -0.1), (0.4, 0.05), (-0.4, 1)], [(-0.7, -1), (0.7, -1)], [(-0.7, 1), (0.7, 1)]]}


def _runa(lz, tipo, cx, cy, escala, color, grosor=0.4):
    for tramo in RUNAS[tipo]:
        lz.pintar(lz.trazo([(cx + x * escala, cy + y * escala) for (x, y) in tramo], grosor), color)


def _ojo(lz, x, y, r, f, espiral=False):
    if espiral:
        lz.pintar(lz.circulo(x, y, r), "#d8c8ff")
        lz.pintar(lz.trazo([(x, y), (x + r * 0.4, y - r * 0.2), (x + r * 0.2, y - r * 0.6), (x - r * 0.5, y - r * 0.4), (x - r * 0.6, y + r * 0.3), (x + r * 0.1, y + r * 0.7)], 0.4), TINTA[2])
        return
    if f == 1:
        lz.pintar(lz.elipse(x, y, r, 0.7), TINTA[1])
        return
    lz.pintar(lz.elipse(x, y, r, r * 1.25), TINTA[0])
    lz.pintar(lz.elipse(x, y, r * 0.72, r * 0.95), "#ffffff" if f != 2 else "#ffd060")
    lz.pintar(lz.elipse(x + 0.3, y + 0.4, r * 0.3, r * 0.5), TINTA[0])
    if f == 2:
        lz.sumar_luz(lz.desenfocar(lz.circulo(x, y, r), 1.6), "#ff7a30", 0.8)
        lz.pintar(lz.trazo([(x - r * 1.3, y - r * 1.7), (x + r * 1.0, y - r * (0.9 if x < 64 else 2.3))], 0.7), TINTA[0])


def _pagina(lz, puntos, sombra_lado):
    pag = lz.poligono(puntos)
    lz.sombrear(pag, PAPEL, 9, LUZ)
    return pag


def grimorio(f):
    W, H = 128, 104
    lz = Lienzo(W, H, s=4, semilla=9900 + f)
    cx = 64
    if f in (3, 4):
        # ATURDIDO: caído boca arriba, abierto y plano en el suelo, visto desde arriba en 3/4
        lz.pintar(lz.desenfocar(lz.elipse(cx, 92, 50, 8), 2), TINTA[2], 0.85)                 # el charco
        tapa = lz.poligono([(12, 66), (116, 66), (122, 96), (6, 96)])
        lz.sombrear(tapa, CUERO, 6, LUZ)
        for (x, y) in ((14, 68), (114, 68), (9, 94), (119, 94)):
            lz.sombrear(lz.circulo(x, y, 3.6), ORO, 2, LUZ)
        izq = lz.poligono([(18, 62), (cx - 1, 66), (cx - 1, 92), (12, 90)])
        der = lz.poligono([(cx + 1, 66), (110, 62), (116, 90), (cx + 1, 92)])
        lz.sombrear(izq, PAPEL, 10, LUZ)
        lz.sombrear(der, PAPEL[:5], 10, LUZ)
        for k in range(6):                                                                    # renglones
            y = 69 + k * 3.6
            lz.pintar(lz.trazo([(22 - k * 0.8, y), (cx - 6, y + 1.0)], 0.35) * izq, TINTA[2], 0.8)
            lz.pintar(lz.trazo([(cx + 6, y + 1.0), (106 + k * 0.8, y)], 0.35) * der, TINTA[2], 0.8)
        # la página rasgada: un desgarrón en zigzag y el trozo levantado
        lz.pintar(lz.trazo([(84, 63), (88, 70), (83, 76), (90, 83), (86, 90)], 0.7), TINTA[0])
        trozo = lz.poligono([(88, 62), (104, 54), (108, 62), (92, 70)])
        lz.sombrear(trozo, PAPEL[2:], 3, LUZ)
        _ojo(lz, 40, 78, 4.4, f, espiral=True)
        _ojo(lz, 100, 78, 4.4, f, espiral=True)
        lomo = lz.poligono([(cx - 2.5, 64), (cx + 2.5, 64), (cx + 2.5, 94), (cx - 2.5, 94)])
        lz.sombrear(lomo, CUERO[1:], 2, LUZ)
        # la Pluma del Primer Nombre, medio salida del lomo
        pluma = lz.trazo([(cx, 70), (cx + 10, 44), (cx + 13, 30)], 1.2, 4.2)
        lz.sombrear(pluma, ORO[2:], 2.0, LUZ)
        lz.pintar(lz.trazo([(cx, 70), (cx + 12, 32)], 0.3), ORO[1])
        lz.sumar_luz(lz.desenfocar(pluma, 2.5), "#ffe890", 0.6)
        if f == 4:
            lz.pintar((lz.alfa > 0.5) * 1.0, "#ffffff", 0.8)
        return lz.sprite(contorno=0.5)
    sube = 1.5 if f == 1 else 0.0
    abre = 6 if f == 2 else 0
    # las tapas: dos alas de cuero púrpura, con cantoneras y un filete de oro
    for lado in (-1, 1):
        tapa = lz.poligono([(cx + lado * 2, 34 - sube), (cx + lado * (54 + abre), 20 - sube - abre * 0.6), (cx + lado * (58 + abre), 78 - sube),
                            (cx + lado * 2, 92 - sube)])
        lz.sombrear(tapa, CUERO if lado < 0 else CUERO[:5], 12, LUZ, rebote=("#7a3aa8", 0.3))
        for (x, y) in ((cx + lado * (53 + abre), 22 - sube - abre * 0.6), (cx + lado * (57 + abre), 76 - sube)):
            lz.sombrear(lz.circulo(x, y, 4.2), ORO, 2.4, LUZ)
            lz.pintar(lz.circulo(x, y, 1.3), CUERO[1])
        broche = lz.poligono([(cx + lado * (55 + abre), 44 - sube), (cx + lado * (62 + abre), 46 - sube), (cx + lado * (62 + abre), 54 - sube),
                              (cx + lado * (56 + abre), 56 - sube)])
        lz.sombrear(broche, ORO, 2, LUZ)
    # las páginas: un bloque de hojas a cada lado, que se comban hacia el lomo
    paginas = np.zeros((lz.H, lz.W))
    for lado in (-1, 1):
        for k in range(3):                                                                    # el canto de las hojas
            d = k * 1.6
            hoja = lz.poligono([(cx + lado * 1.5, 31 - sube + d), (cx + lado * (50 + abre - d), 19 - sube - abre * 0.6 + d),
                                (cx + lado * (53 + abre - d), 73 - sube + d * 0.4), (cx + lado * 1.5, 87 - sube + d * 0.4)])
            lz.sombrear(hoja, PAPEL[k:k + 4] if k else PAPEL, 14, LUZ)
            if k == 0:
                paginas = np.clip(paginas + hoja, 0, 1)
        lz.pintar(lz.trazo([(cx + lado * 4, 34 - sube), (cx + lado * 5, 84 - sube)], 2.6) * paginas, PAPEL[1], 0.55)     # la sombra del lomo
    # renglones de tinta (los de abajo, gotean) y una letra capital dorada
    for lado in (-1, 1):
        for k in range(8):
            y = 30 - sube + k * 6.2
            if 44 < y + sube < 62:
                continue                                                                      # (ahí van los ojos)
            largo = 38 - (k % 3) * 6
            lz.pintar(lz.trazo([(cx + lado * 9, y + 0.6), (cx + lado * (9 + largo), y - 2.2 - abre * 0.2)], 0.45) * paginas, TINTA[2], 0.85)
        for x in (cx + lado * 20, cx + lado * 34):
            lz.pintar(lz.trazo([(x, 79 - sube), (x + 0.3, 86 - sube + (4 if f == 2 else 0))], 0.9, 0.3), TINTA[1])
    cap = lz.poligono([(cx - 46, 26 - sube), (cx - 38, 24 - sube), (cx - 38, 33 - sube), (cx - 46, 35 - sube)])
    lz.sombrear(cap * paginas, ORO[1:], 2, LUZ)
    # los ojos, uno en cada página
    _ojo(lz, cx - 24, 53 - sube, 5.2, f)
    _ojo(lz, cx + 24, 53 - sube, 5.2, f)
    if f == 2:
        # furioso: la tinta rebosa por el pliegue y dos hojas se levantan
        lz.pintar(lz.trazo([(cx, 40), (cx - 1, 60), (cx + 1, 88)], 3.0, 1.6), TINTA[1])
        for lado in (-1, 1):
            vuela = lz.poligono([(cx + lado * 8, 26), (cx + lado * 40, 6), (cx + lado * 46, 16), (cx + lado * 12, 34)])
            lz.sombrear(vuela, PAPEL[1:], 4, LUZ)
            lz.pintar(lz.trazo([(cx + lado * 14, 27), (cx + lado * 40, 12)], 0.4) * vuela, TINTA[2], 0.8)
    # el lomo, con nervios de oro
    lomo = lz.poligono([(cx - 3.5, 28 - sube), (cx + 3.5, 28 - sube), (cx + 3.5, 94 - sube), (cx - 3.5, 94 - sube)])
    lz.sombrear(lomo, CUERO[1:], 2.5, LUZ)
    for y in (38, 56, 74):
        lz.sombrear(lz.poligono([(cx - 4, y - sube), (cx + 4, y - sube), (cx + 4, y + 2.4 - sube), (cx - 4, y + 2.4 - sube)]), ORO, 1, LUZ)
    # la PLUMA DEL PRIMER NOMBRE, clavada en el lomo: el cañón, las barbas doradas y su halo
    canon = lz.trazo([(cx, 32 - sube), (cx + 1.5, 6 - sube)], 1.1, 0.6)
    barbas = lz.poligono([(cx + 0.5, 24 - sube), (cx - 5.5, 16 - sube), (cx - 4.5, 6 - sube), (cx + 2, -1 - sube + 2), (cx + 7.5, 7 - sube), (cx + 6.5, 17 - sube)])
    lz.sombrear(barbas, ORO[2:], 3, LUZ)
    for k in range(5):
        y = 20 - sube - k * 3.6
        lz.pintar(lz.trazo([(cx + 1, y), (cx - 4.4, y - 3)], 0.25) * barbas, ORO[1], 0.8)
        lz.pintar(lz.trazo([(cx + 1, y), (cx + 6, y - 3)], 0.25) * barbas, ORO[1], 0.8)
    lz.pintar(canon, ORO[5])
    lz.sumar_luz(lz.desenfocar(barbas, 3.0), "#ffe890", 0.55)
    return lz.sprite(contorno=0.5)


def mano(f):
    W, H = 48, 56
    lz = Lienzo(W, H, s=5, semilla=9940 + f)
    if f == 1:
        # golpe: la palma plana en el suelo, los dedos abiertos hacia delante, su charco
        lz.pintar(lz.desenfocar(lz.elipse(24, 46, 22, 7), 1.2), TINTA[2], 0.9)
        palma = lz.elipse(24, 42, 12, 7)
        lz.sombrear(palma, TINTA[1:], 4, LUZ)
        for (x, y) in ((8, 36), (15, 30), (24, 28), (33, 30), (40, 36)):
            dedo = lz.trazo([(24 + (x - 24) * 0.45, 40), (x, y)], 4.0, 2.4)
            lz.sombrear(dedo, TINTA[1:], 1.8, LUZ)
            dx, dy = x - 24, y - 40
            n = (dx * dx + dy * dy) ** 0.5
            garra = lz.poligono([(x - dy / n * 1.8, y + dx / n * 1.8), (x + dy / n * 1.8, y - dx / n * 1.8), (x + dx / n * 7, y + dy / n * 7)])
            lz.sombrear(garra, ORO[1:], 1.0, LUZ)
        return lz.sprite(contorno=0.5)
    # alzada: el antebrazo sale del suelo (de un charco), la mano abierta arriba con las garras de plumilla
    lz.pintar(lz.elipse(24, 53, 13, 3), TINTA[2], 0.9)
    brazo = lz.trazo([(24, 54), (22, 40), (24, 28)], 9.0, 7.0)
    lz.sombrear(brazo, TINTA[1:], 4, LUZ)
    lz.pintar(lz.trazo([(21, 50), (20, 38), (21.5, 30)], 0.6) * brazo, TINTA[5], 0.6)
    palma = lz.elipse(24, 23, 9.5, 8)
    lz.sombrear(palma, TINTA[1:], 5, LUZ)
    for (x, y) in ((9, 22), (13, 10), (23, 5), (33, 9), (39, 20)):
        dedo = lz.trazo([(24 + (x - 24) * 0.5, 22 + (y - 22) * 0.35), (x, y)], 4.2, 2.4)
        lz.sombrear(dedo, TINTA[1:], 1.8, LUZ)
        dx, dy = x - 24, y - 24
        n = (dx * dx + dy * dy) ** 0.5
        garra = lz.poligono([(x - dy / n * 1.9, y + dx / n * 1.9), (x + dy / n * 1.9, y - dx / n * 1.9), (x + dx / n * 7.5, y + dy / n * 7.5)])
        lz.sombrear(garra, ORO[1:], 1.0, LUZ)
        lz.pintar(lz.trazo([(x, y), (x + dx / n * 5, y + dy / n * 5)], 0.25), ORO[0])
    for (x, y) in ((18, 44), (28, 48)):                                                       # gotas que le caen
        lz.pintar(lz.trazo([(x, y), (x, y + 3.5)], 0.9, 0.3), TINTA[1])
    return lz.sprite(contorno=0.5)


def sombra(f):
    W, H = 32, 28
    lz = Lienzo(W, H, s=6, semilla=9960 + f)
    base = 25
    onda = {0: 0.0, 1: 1.6}.get(f, 0.8)
    if f == 2:
        puntos = [(4, base), (10, base - 1), (15, base - 6), (19, base - 14), (23, base - 17)]
    else:
        puntos = [(3, base), (8, base - 2 - onda), (13, base + 0.5), (18, base - 3 + onda), (23, base - 5), (26, base - 9)]
    cuerpo = lz.trazo(puntos, 4.4, 6.6)
    solida = f == 3
    lz.sombrear(cuerpo, (["#4a4460", "#77709a", "#a8a2c8", "#d8d4ec", "#ffffff"] if solida else TINTA), 2.6, LUZ)
    # las letras que le corren por el lomo (renglón): rayitas claras
    for i in range(1, len(puntos)):
        ax, ay = puntos[i - 1]
        bx, by = puntos[i]
        for t in (0.25, 0.6, 0.9):
            x, y = ax + (bx - ax) * t, ay + (by - ay) * t - 0.6
            lz.pintar(lz.trazo([(x - 0.9, y), (x + 0.9, y - 0.3)], 0.3) * cuerpo, "#2e1c4a" if solida else "#b8a0f0", 0.85)
    cab = puntos[-1]
    cabeza = lz.circulo(cab[0], cab[1], 4.4)
    lz.sombrear(cabeza, (["#4a4460", "#77709a", "#a8a2c8", "#d8d4ec", "#ffffff"] if solida else TINTA[:5]), 2.6, LUZ)
    for dx in (-1.6, 1.6):
        lz.pintar(lz.circulo(cab[0] + dx + 0.6, cab[1] - 0.6, 1.0), "#12061c" if solida else "#ffffff")
    if f == 2:
        boca = lz.elipse(cab[0] + 1.6, cab[1] + 2.2, 2.2, 1.6)
        lz.pintar(boca, "#a8405a")
        for dx in (-1.0, 0.6, 2.2):
            lz.pintar(lz.poligono([(cab[0] + dx + 0.6, cab[1] + 1.0), (cab[0] + dx + 1.6, cab[1] + 1.0), (cab[0] + dx + 1.1, cab[1] + 2.4)]), "#ffffff")
    if solida:
        lz.pintar(lz.trazo([(puntos[1][0], puntos[1][1] - 2.4), (puntos[3][0], puntos[3][1] - 2.6)], 0.35), "#ffffff", 0.9)
    if not solida:
        for (x, y) in ((6, base + 1.5), (16, base + 2)):                                      # el rastro de tinta
            lz.pintar(lz.elipse(x, y, 3.0, 0.9), TINTA[2], 0.8)
    if f == 4:
        lz.pintar((lz.alfa > 0.5) * 1.0, "#ffffff", 0.85)
    return lz.sprite(contorno=0.5)


def pedestal(tipo, encendido):
    W, H = 24, 36
    lz = Lienzo(W, H, s=6, semilla=9980)
    cx = 12
    zoc = lz.poligono([(cx - 9, 35), (cx + 9, 35), (cx + 8, 30), (cx - 8, 30)])
    lz.sombrear(zoc, MARMOL, 2, LUZ)
    fuste = lz.poligono([(cx - 5.5, 30), (cx + 5.5, 30), (cx + 4.8, 14), (cx - 4.8, 14)])
    lz.sombrear(fuste, MARMOL[1:], 4, LUZ, textura=((lz.x % 3.4) < 0.7) * 1.0, fuerza_tex=-0.3)
    capitel = lz.poligono([(cx - 8, 14), (cx + 8, 14), (cx + 7, 10.5), (cx - 7, 10.5)])
    lz.sombrear(capitel, MARMOL[2:], 1.5, LUZ)
    cuenco = lz.elipse(cx, 9.5, 8.5, 3.6)
    lz.sombrear(cuenco, ORO, 2.2, LUZ)
    dentro = lz.elipse(cx, 9.0, 6.6, 2.3)
    col = ELEMENTO[tipo]
    lz.pintar(dentro, col[2] if encendido else TINTA[1])
    # la runa del sigilo, grabada en el fuste
    _runa(lz, tipo, cx, 22, 4.2, col[3] if encendido else col[0], 0.45)
    if encendido:
        llama = lz.poligono([(cx - 5, 9), (cx - 3, 3), (cx - 1.5, 6), (cx, 0.5), (cx + 1.5, 6), (cx + 3.2, 3.2), (cx + 5, 9)])
        lz.pintar(llama, col[2])
        lz.pintar(lz.poligono([(cx - 2.6, 9), (cx - 1, 5), (cx, 3), (cx + 1.2, 5.4), (cx + 2.6, 9)]), col[3])
        lz.sumar_luz(lz.desenfocar(llama, 2.2), col[2], 0.7)
        lz.sumar_luz(lz.desenfocar(lz.circulo(cx, 22, 4), 1.5), col[2], 0.5)
    return lz.sprite(contorno=0.5)


def atril(f):
    W, H = 16, 30
    lz = Lienzo(W, H, s=6, semilla=9990 + f)
    cx = 8
    lz.sombrear(lz.elipse(cx, 28, 5.5, 1.8), MARMOL[:5], 1.2, LUZ)
    lz.sombrear(lz.poligono([(cx - 1.3, 28), (cx + 1.3, 28), (cx + 1.0, 13), (cx - 1.0, 13)]), ORO[:5], 1.0, LUZ)
    tabla = lz.poligono([(cx - 6.5, 14), (cx + 6.5, 14), (cx + 5.5, 4), (cx - 5.5, 4)])
    lz.sombrear(tabla, ["#1a100c", "#32201a", "#523426", "#724a34", "#946648"], 3, LUZ)
    ficha = lz.poligono([(cx - 4, 12.5), (cx + 4, 12.5), (cx + 3.4, 5.5), (cx - 3.4, 5.5)])
    lz.sombrear(ficha, PAPEL[2:] if f else ["#5a566a", "#77738a", "#9692a8", "#b4b0c4"], 2, LUZ)
    lz.pintar(lz.poligono([(cx + 1, 5.5), (cx + 3.4, 5.5), (cx + 3.5, 4.2), (cx + 1.2, 4.2)]), "#7a52a6" if f else "#4a465a")   # la pestaña morada
    for y in (7.6, 9.4, 11.2):
        lz.pintar(lz.trazo([(cx - 2.6, y), (cx + 2.4, y)], 0.25), TINTA[2] if f else "#6a667a", 0.9)
    if f:
        lz.sumar_luz(lz.desenfocar(ficha, 2.2), "#ffe890", 0.75)
    return lz.sprite(contorno=0.5)


def sello(f):
    W, H = 64, 48
    lz = Lienzo(W, H, s=5, semilla=9995 + f)
    for x in (3, 61):                                                                         # las dos jambas de mármol
        jamba = lz.poligono([(x - 3, 47), (x + 3, 47), (x + 3, 6), (x - 3, 6)])
        lz.sombrear(jamba, MARMOL, 2.4, LUZ)
        lz.sombrear(lz.circulo(x, 5, 3.4), ORO, 2, LUZ)
    if f == 1:
        for x in (8, 56):                                                                     # abierto: las hojas, recogidas
            hoja = lz.poligono([(x - 2, 46), (x + 2, 46), (x + 2, 10), (x - 2, 10)])
            lz.sombrear(hoja, ORO[1:], 1.2, LUZ)
        return lz.sprite(contorno=0.5)
    for x in range(8, 58, 5):                                                                 # cerrado: barrotes de oro
        barrote = lz.poligono([(x - 0.9, 46), (x + 0.9, 46), (x + 0.9, 9), (x - 0.9, 9)])
        lz.sombrear(barrote, ORO, 0.8, LUZ)
        lz.pintar(lz.poligono([(x - 1.5, 9), (x + 1.5, 9), (x, 5)]), ORO[4])
    for y in (14, 40):
        lz.sombrear(lz.poligono([(6, y - 1.2), (58, y - 1.2), (58, y + 1.2), (6, y + 1.2)]), ORO[1:], 0.8, LUZ)
    for (tipo, x) in (("fuego", 16), ("hielo", 32), ("rayo", 48)):                            # los tres discos de runa
        disco = lz.circulo(x, 27, 7.4)
        lz.sombrear(disco, ORO, 4, LUZ)
        lz.pintar(lz.circulo(x, 27, 5.6), TINTA[1])
        _runa(lz, tipo, x, 27, 3.6, ELEMENTO[tipo][2], 0.45)
    return lz.sprite(contorno=0.5)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fotos):
        Image.fromarray(np.concatenate(fotos, axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    tira("grimorio", [grimorio(f) for f in range(5)])
    tira("mano", [mano(f) for f in range(2)])
    tira("sombra", [sombra(f) for f in range(5)])
    tira("pedestal", [pedestal(t, e) for t in ("fuego", "hielo", "rayo") for e in (False, True)])
    tira("atril", [atril(f) for f in range(2)])
    tira("sello", [sello(f) for f in range(2)])
    print("Sección Prohibida pintada en", SALIDA)
