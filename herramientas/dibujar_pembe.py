"""
PEMBE, EL CIERVO DE HIERRO: el minijefe del Bosque Cobrizo (paleta oficial de Raíz).

Uso:  python3 herramientas/dibujar_pembe.py
Genera arte/zonas/raiz/pembe.png: 8 fotogramas de 74×66, mirando a la derecha (el juego lo voltea):
  0-1 anda      2 se prepara (baja las astas y escarba)      3-4 embiste al galope
  5 atascado (las astas clavadas: tira hacia atrás)          6 libre de Giza (astas de hojas cobrizas)
  7 se inclina ante Maisha antes de irse al bosque
Giza le ha convertido las astas en hierro con grietas de luz violeta y le ha cubierto el lomo de placas.
El blanco al recibir daño lo pone el juego.
"""
import math
import os
import random

import numpy as np
from PIL import Image

import dibujar_criaturas as dc
from dibujar_criaturas import Hoja, MAT, tira

MAT["cobre"] = ["Follaje cobre 1", "Follaje cobre 2", "Follaje cobre 3", "Follaje cobre 4"]
MAT["rojizo"] = ["Follaje rojizo 1", "Follaje rojizo 2", "Follaje rojizo 3", "Follaje rojizo 4"]
MAT["pelo"] = ["Madera 1", "Madera 2", "Madera 3", "Madera 4"]
MAT["vientre"] = ["Tierra 1", "Tierra 2", "Tierra 3", "Tierra 4"]
MAT["pezuna"] = ["Extremos 1", "Interfaz 1", "Piedra 1", "Piedra 2"]

W, H = 74, 66
SUELO = 64


def pata(h, x0, y0, x1, y1, rodilla, mat="pelo", oscuro=False):
    """Una pata fina con rodilla y pezuña."""
    kx, ky = rodilla
    m = h.trazo([(x0, y0), (kx, ky), (x1, y1)], [3.2, 2.3, 2.0])
    h.forma(m, mat, minimo=1, maximo=2 if oscuro else 3)
    h.px(x1, y1, "pezuna", 1)
    h.px(x1 + 1, y1, "pezuna", 1)
    h.px(x1, y1 - 1, "pezuna", 2)


def astas(h, cx, cy, vivas=False, giro=0.0):
    """Las astas: un tronco que sube curvándose y puntas que salen hacia delante.
    giro (en grados): las inclina hacia delante (al prepararse y embestir apuntan al frente)."""
    mat = "cobre" if vivas else "piedra"
    g = math.radians(giro)

    def rot(dx, dy):
        return (cx + dx * math.cos(g) - dy * math.sin(g), cy + dx * math.sin(g) + dy * math.cos(g))

    for desfase, sombra in ((-5.0, True), (0.0, False)):     # la de detrás, más oscura y algo atrás
        tronco = [(desfase + 0, 0), (desfase - 5, -6), (desfase - 9, -12), (desfase - 10, -19), (desfase - 7, -25)]
        pts = [rot(*p) for p in tronco]
        m = h.trazo(pts, [3.8, 3.2, 2.6, 2.0, 1.4])
        h.forma(m, mat, minimo=0 if sombra else 1, maximo=2 if sombra else 3)
        for k, largo in ((1, 9.0), (2, 10.0), (3, 7.0)):
            bx, by = tronco[k]
            fin = (bx + largo * 0.55, by - largo * 0.85)
            medio = (bx + largo * 0.4, by - largo * 0.35)
            mm = h.trazo([rot(bx, by), rot(*medio), rot(*fin)], [2.4, 1.8, 1.1])
            h.forma(mm, mat, minimo=0 if sombra else 1, maximo=2 if sombra else 3)
            if vivas and not sombra:
                fx, fy = rot(*fin)
                for (dx, dy, mt) in ((0, -1.4, "cobre"), (1.4, 0, "rojizo"), (-1.2, 0.4, "cobre")):
                    h.forma(h.elipse(fx + dx, fy + dy, 1.9, 1.4), mt, minimo=1)
        if vivas and not sombra:
            fx, fy = pts[-1]
            for (dx, dy, mt) in ((0, -1.5, "rojizo"), (1.5, 0, "cobre")):
                h.forma(h.elipse(fx + dx, fy + dy, 2.0, 1.5), mt, minimo=1)
        if not vivas and not sombra:
            h.grieta([pts[0], pts[1], pts[2]])
            h.grieta([pts[2], pts[3]])


def cuerpo(h, f, vivo=False):
    """Fotograma f (ver arriba)."""
    corre = f in (3, 4)
    prep = f == 2
    atascado = f == 5
    inclina = f == 7
    paso = {0: 0, 1: 1, 3: 0, 4: 1}.get(f, 0)
    by = 43 - (1 if f == 3 else 0) + (1 if prep or atascado else 0)
    # --- patas de atrás (las del otro lado, oscuras)
    if corre:
        if paso == 0:
            pata(h, 18, by + 4, 9, SUELO - 3, (13, by + 10), oscuro=True)
            pata(h, 38, by + 4, 47, SUELO - 4, (44, by + 10), oscuro=True)
        else:
            pata(h, 18, by + 4, 22, SUELO, (16, by + 11), oscuro=True)
            pata(h, 38, by + 4, 34, SUELO, (39, by + 11), oscuro=True)
    elif atascado:
        pata(h, 18, by + 4, 10, SUELO, (14, by + 11), oscuro=True)       # tira hacia atrás
        pata(h, 38, by + 4, 42, SUELO, (40, by + 11), oscuro=True)
    else:
        dx = 2 if paso else -1
        pata(h, 18, by + 4, 17 + dx, SUELO, (19, by + 11), oscuro=True)
        pata(h, 38, by + 4, 38 - dx, SUELO, (37, by + 11), oscuro=True)
    # --- cuerpo: grupa, tronco y pecho
    mat = "pelo"
    grupa = h.elipse(17, by, 9, 7.5)
    tronco = h.elipse(27, by + 0.5, 12, 7)
    pecho = h.elipse(37, by - 0.5, 8, 8)
    h.forma(grupa | tronco | pecho, mat, esfera=(28, by - 3, 20, 11))
    vientre = h.elipse(27, by + 6, 11, 2.2) & (grupa | tronco | pecho)
    h.forma(vientre, "vientre", plano=1, separar=False)
    # rabo
    h.forma(h.trazo([(9, by - 4), (7, by - 2), (7, by)], [2.2, 2.0, 1.4]), "vientre", minimo=1)
    # placas de hierro por el lomo (no cuando ya es libre)
    if not vivo:
        for i, x in enumerate((15, 20, 25, 30, 35)):
            pl = h.elipse(x, by - 6.5 + (i % 2) * 0.5, 3.6, 2.6)
            h.forma(pl, "piedra", esfera=(x - 1, by - 8, 4, 3))
        h.grieta([(22, by - 7), (24, by - 5), (27, by - 6)])
    else:
        # musgo y hojitas donde estaban las placas
        for x in (16, 22, 29, 34):
            h.forma(h.elipse(x, by - 6.5, 2.4, 1.6), "liquen", minimo=1)
    # --- patas de delante (las de este lado, claras)
    if corre:
        if paso == 0:
            pata(h, 20, by + 4, 12, SUELO - 2, (15, by + 10))
            pata(h, 40, by + 3, 52, SUELO - 5, (48, by + 7))
        else:
            pata(h, 20, by + 4, 25, SUELO, (19, by + 11))
            pata(h, 40, by + 3, 37, SUELO, (42, by + 11))
    elif prep:
        pata(h, 20, by + 4, 19, SUELO, (21, by + 11))
        pata(h, 40, by + 3, 46, SUELO - 3, (45, by + 8))                # escarba
    elif atascado:
        pata(h, 20, by + 4, 12, SUELO, (16, by + 11))
        pata(h, 40, by + 3, 36, SUELO, (40, by + 11))
    else:
        dx = -1 if paso else 2
        pata(h, 20, by + 4, 20 + dx, SUELO, (21, by + 11))
        pata(h, 40, by + 3, 40 - dx, SUELO, (41, by + 11))
    # --- cuello y cabeza (baja al prepararse, embestir o inclinarse)
    baja = 9 if (prep or atascado or inclina) else (6 if corre else 0)
    hx, hy = 49, 27 + baja
    cuello = h.poligono([(36, by - 6), (41, by - 9), (hx - 2, hy - 3), (hx + 1, hy + 2), (42, by + 2)])
    h.forma(cuello, "pelo", esfera=(42, hy, 8, 12))
    cabeza = h.elipse(hx, hy, 5.2, 4.2)
    hocico = h.poligono([(hx + 2, hy - 2), (hx + 9, hy + 1), (hx + 8, hy + 4), (hx + 2, hy + 4)])
    h.forma(cabeza | hocico, "pelo", esfera=(hx + 1, hy - 1, 8, 6))
    h.px(hx + 8, hy + 1, "pezuna", 1)                    # nariz
    h.px(hx + 7, hy + 4, "vientre", 2)
    # oreja
    oreja = h.poligono([(hx - 3, hy - 2), (hx - 7, hy - 6), (hx - 2, hy - 4)])
    h.forma(oreja, "pelo", minimo=1)
    # ojo
    if vivo:
        h.px(hx + 1, hy - 1, "pezuna", 0)
        h.px(hx + 2, hy - 2, "blanco", 2)
    else:
        h.px(hx + 1, hy - 1, "giza", 3)
        h.px(hx + 2, hy - 1, "giza", 2)
    # astas
    giro = 62.0 if (prep or corre or atascado) else 0.0
    if inclina:
        giro = 45.0
    astas(h, hx - 2, hy - 3, vivas=vivo, giro=giro)
    # al escarbar: terrón compacto levantado junto a la pezuña delantera
    if prep:
        terron = h.elipse(49.5, SUELO - 1.5, 2.4, 1.4)
        h.forma(terron, "tierra", minimo=1, maximo=3)
        h.px(48, SUELO - 2, "tierra", 3)


def fotograma(f):
    h = Hoja(W, H)
    vivo = f >= 6
    cuerpo(h, f, vivo=vivo)
    return h.imagen()


def main():
    hoja = tira([fotograma(f) for f in range(8)])
    ruta = os.path.join(dc.RAIZ, "arte", "zonas", "raiz", "pembe.png")
    hoja.save(ruta)
    print("guardado:", ruta, hoja.size)


if __name__ == "__main__":
    main()
