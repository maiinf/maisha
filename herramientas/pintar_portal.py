"""EL ARCO DE RAÍZ, pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_portal.py

Genera arte/mundos/kitovu/portal.png: 2 fotogramas de 96×120 (dormido · abierto).
  - Un umbral de losas antiguas con un círculo de runas tallado (las runas brillan cuando está abierto).
  - Dos pilares de piedra rotos, cubiertos de musgo, y raíces gigantes que suben enroscándose en ellos
    (por delante y por detrás) y se trenzan arriba en un nudo.
  - En el nudo, la Semilla del Arco: un corazón de ámbar que late (dormido: apagado y agrietado).
  - Raicillas y enredaderas que cuelgan; dentro, los Prados del Eco con luz (o la oscuridad de Giza con espinas).
Los brillos que se mueven (el latido de la semilla, las runas, las motas) los dibuja scripts/mundo/kitovu/portal.gd.
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa, RAIZ  # noqa: E402
from cinematicas import hebra, HIERBA  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "kitovu")
W, H = 96, 120
CX = 48
SUELO = 117            # donde apoyan las losas
ARRANQUE = 50          # altura a la que las patas empiezan a curvarse
RX, RY = 31, 38        # radios del arco (por el centro de las raíces)
LUZ = (-0.6, -0.7, 0.5)
CONTORNO = 0.36

PIEDRA = ["#22231f", "#33352f", "#474a41", "#5d6155", "#74796a", "#8c917f", "#a6aa97", "#c2c4b2"]
PIEDRA_CLARA = ["#3a3a33", "#55564b", "#6f7163", "#898b7b", "#a3a593", "#bcbeab", "#d6d6c3"]
RAIZ_VIVA = ["#1f1009", "#3a2010", "#5b3519", "#7d4c27", "#9c6536", "#b98148", "#d5a066", "#ebc48c"]
RAIZ_DORMIDA = ["#16120f", "#251f1a", "#373029", "#4a4138", "#5e5449", "#72675a", "#877b6c", "#9d9180"]
MUSGO = ["#14240f", "#1f3a17", "#2f5520", "#41712a", "#5a8f36", "#79ad48", "#9fca62"]
MUSGO_SECO = ["#1d1b12", "#2e2a1b", "#423c26", "#585033", "#6e6641", "#857c51"]
AMBAR = ["#3a1606", "#6e2c0a", "#a84a12", "#d8751e", "#f2a33a", "#ffd26e", "#fff3c4"]
APAGADO = ["#0d0710", "#1a0f22", "#2a1838", "#3b2350", "#4e2f66", "#61407a"]


def _tramos(pts, delante, quiero):
    """Corta el camino en tramos seguidos que van por delante (o por detrás)."""
    tramos, actual = [], []
    for p, d in zip(pts, delante):
        if d == quiero:
            actual.append(p)
        elif actual:
            tramos.append(actual)
            actual = []
    if actual:
        tramos.append(actual)
    return [t for t in tramos if len(t) > 2]


def _pilar(lz, x0, x1, arriba, roto, abierto, semilla):
    """Un pilar de piedra antigua: fuste con sillares, capitel y basa; roto por arriba."""
    rng = np.random.default_rng(semilla)
    ancho = x1 - x0
    # el fuste, con el borde de arriba roto
    borde = [(x0, SUELO - 8)]
    pasos = 7
    for k in range(pasos + 1):
        x = x0 + ancho * k / pasos
        y = arriba + (rng.random() * 5 if roto else 0) + (3 if roto and k in (2, 3) else 0)
        borde.append((x, y))
    borde.append((x1, SUELO - 8))
    fuste = lz.poligono(borde)
    lz.sombrear(fuste, PIEDRA, ancho * 0.45, LUZ, textura=lz.ruido(1.6, 3, semilla=semilla), fuerza_tex=0.35)
    # juntas de los sillares
    y = SUELO - 8
    while y > arriba + 4:
        y -= 9 + rng.random() * 3
        junta = lz.trazo([(x0 + 0.5, y), (x1 - 0.5, y + rng.random() - 0.5)], 0.7) * fuste
        lz.pintar(junta, "#1b1c18", 0.75)
        lz.pintar(lz.trazo([(x0 + 0.5, y + 0.9), (x1 - 0.5, y + 0.9)], 0.5) * fuste, "#9ea290", 0.25)
    # runas talladas en el frente del fuste (brillan cuando el arco está abierto)
    cxp = (x0 + x1) / 2
    runas = np.zeros((lz.H, lz.W))
    formas = [[(-1.2, -1.5), (1.2, -1.5), (0, 1.5)], [(-1.2, 1.5), (0, -1.5), (1.2, 1.5)], [(0, -1.6), (0, 1.6), (1.2, 0.2)],
              [(-1.2, -1.2), (1.2, 1.2), (0, 0), (-1.2, 1.2)]]
    yr = arriba + 12
    k = 0
    while yr < SUELO - 18:
        f = formas[(k + semilla) % len(formas)]
        runas = np.maximum(runas, lz.trazo([(cxp + a, yr + b) for a, b in f], 0.55))
        yr += 8.5
        k += 1
    runas *= fuste
    lz.pintar(runas, "#191a16", 0.9)
    if abierto:
        lz.sumar_luz(lz.desenfocar(runas, 1.0), "#ffc35a", 0.8)
        lz.pintar(runas, "#ffe2a0", 0.75)
    # grietas
    for k in range(3):
        gx = x0 + 2 + rng.random() * (ancho - 4)
        gy = arriba + 8 + rng.random() * (SUELO - arriba - 24)
        pts = [(gx, gy)]
        for j in range(5):
            pts.append((pts[-1][0] + (rng.random() - 0.5) * 2.5, pts[-1][1] + 1.6 + rng.random()))
        lz.pintar(lz.trazo(pts, 0.7, 0.3) * fuste, "#141410", 0.85)
    # basa (más ancha) y capitel
    basa = lz.poligono([(x0 - 2, SUELO - 9), (x1 + 2, SUELO - 9), (x1 + 3, SUELO - 3), (x0 - 3, SUELO - 3)])
    lz.sombrear(basa, PIEDRA, 3.0, LUZ, textura=lz.ruido(1.5, 2, semilla=semilla + 1), fuerza_tex=0.3)
    if not roto:
        capitel = lz.poligono([(x0 - 2.5, arriba - 4), (x1 + 2.5, arriba - 4), (x1 + 1.5, arriba + 1), (x0 - 1.5, arriba + 1)])
        lz.sombrear(capitel, PIEDRA_CLARA, 2.5, LUZ, textura=lz.ruido(1.5, 2, semilla=semilla + 2), fuerza_tex=0.3)
        fuste = np.maximum(fuste, capitel)
    # musgo por arriba y por el lado de la luz
    alto = lz.ruido(3.0, 3, semilla=semilla + 5)
    arriba_m = np.clip(1 - (lz.y - arriba) / 14, 0, 1) + np.clip(1 - (lz.x - x0) / 3, 0, 1) * 0.6
    musgo = np.clip((alto * 0.9 + arriba_m * 0.7 - 0.95) * 4, 0, 1) * np.maximum(fuste, basa)
    lz.sombrear(musgo, MUSGO if abierto else MUSGO_SECO, 1.2, LUZ, textura=lz.ruido(0.8, 2, semilla=semilla + 6), fuerza_tex=0.5)
    return np.maximum(fuste, basa)


def _umbral(lz, abierto):
    """Las losas del umbral y el círculo de runas."""
    losa = lz.poligono([(10, SUELO - 9), (86, SUELO - 9), (93, SUELO), (3, SUELO)])
    tex = lz.ruido(1.8, 3, semilla=11)
    lz.sombrear(losa, PIEDRA, 3.0, LUZ, textura=tex, fuerza_tex=0.35)
    # cara de arriba más clara, cara de delante más oscura
    cara = losa * np.clip((SUELO - 4 - lz.y) * 2, 0, 1)
    lz.pintar(cara, rampa(PIEDRA_CLARA, np.clip(0.45 + (tex - 0.5) * 0.5, 0, 1)), 0.75)
    frente = losa * np.clip((lz.y - (SUELO - 4)) * 2, 0, 1)
    lz.pintar(frente, "#2a2b25", 0.55)
    # juntas entre losas
    for x in (24, 40, 57, 72):
        lz.pintar(lz.trazo([(x, SUELO - 9), (x + (x - CX) * 0.1, SUELO - 4)], 0.6) * losa, "#1b1c18", 0.8)
    # el círculo de runas tallado en el centro
    anillo = np.clip(lz.elipse(CX, SUELO - 6.4, 15, 2.6) - lz.elipse(CX, SUELO - 6.4, 13.4, 1.9), 0, 1)
    lz.pintar(anillo, "#1e1f1a", 0.9)
    rng = np.random.default_rng(12)
    runas = np.zeros((lz.H, lz.W))
    for k in range(9):
        a = k / 9 * 2 * np.pi
        x, y = CX + np.cos(a) * 11, SUELO - 6.4 + np.sin(a) * 1.4
        runas = np.maximum(runas, lz.trazo([(x - 0.6, y - 0.4), (x + 0.6 * (1 if k % 2 else -1), y + 0.4)], 0.45))
    lz.pintar(runas, "#1e1f1a", 0.9)
    if abierto:
        lz.sumar_luz(lz.desenfocar(np.maximum(anillo, runas), 0.8), "#ffcf6a", 0.9)
        lz.pintar(np.maximum(anillo, runas), "#ffd98a", 0.7)
    # hierba y musgo entre las losas
    juntas = losa * np.clip((lz.ruido(2.5, 3, semilla=13) - 0.62) * 5, 0, 1)
    lz.pintar(juntas, rampa(MUSGO if abierto else MUSGO_SECO, lz.ruido(0.8, 2, semilla=14)), 0.8)
    return losa


def _dentro(lz, abierto):
    """Lo que se ve por el arco."""
    pts = [(CX - RX + 6, SUELO - 9)]
    for a in np.linspace(np.pi, 0, 40):
        pts.append((CX + np.cos(a) * (RX - 4), ARRANQUE + 3 - np.sin(a) * (RY - 4)))
    pts.append((CX + RX - 6, SUELO - 9))
    dentro = lz.poligono(pts)
    if abierto:
        cielo = lz.gradiente(["#8fbcc0", "#bcd8d0", "#e7efd6", "#fbe6ac", "#ffd98a"], desde=ARRANQUE - RY + 6, hasta=SUELO - 30)
        lz.pintar(dentro, cielo)
        # nubes suaves
        nubes = np.clip((lz.ruido(9, 3, semilla=21) - 0.58) * 3, 0, 1) * np.clip((70 - lz.y) / 30, 0, 1)
        lz.pintar(nubes * dentro, "#fff8e6", 0.55)
        # colinas lejanas, azuladas, y luego verdes
        for (altura, amp, fase, col, sem) in ((76, 3.0, 0.3, ["#7a9e8f", "#94b6a2", "#b2ccb2"], 22),
                                              (84, 4.0, 1.7, ["#4d7d45", "#6f9b52", "#94b864"], 23),
                                              (93, 3.0, 2.9, HIERBA[2:7], 24)):
            colina = dentro * np.clip((lz.y - (altura + amp * np.sin(lz.x / 7 + fase))) * 2, 0, 1)
            lz.pintar(colina, rampa(col, np.clip(lz.ruido(1.3, 2, semilla=sem) * 0.8 + 0.1, 0, 1)))
        # árboles lejanos y un camino de tierra que se pierde
        for (tx, ty, r) in [(30, 82, 2.4), (36, 81, 2.0), (61, 83, 2.6), (66, 84, 2.0), (58, 88, 3.0)]:
            lz.sombrear(lz.circulo(tx, ty - r, r) * dentro, ["#23401f", "#355029", "#4f7038", "#6f9248"], r * 0.8, LUZ)
            lz.pintar(lz.trazo([(tx, ty - 0.5), (tx, ty + 1.5)], 0.7) * dentro, "#3a2a1a")
        # rayos de sol que entran desde arriba y una neblina dorada
        fuente = lz.desenfocar(lz.circulo(CX + 6, ARRANQUE - RY + 10, 6), 3)
        rayos = lz.rayos(fuente, (CX + 6, ARRANQUE - RY + 10), largo=1.03, pasos=24)
        lz.sumar_luz(np.clip(rayos * 2.0, 0, 1) * dentro, "#fff1c0", 0.35)
        lz.sumar_luz(lz.desenfocar(dentro, 5) * dentro * np.clip((lz.y - 60) / 60, 0, 1), "#ffe7a6", 0.25)
    else:
        lz.pintar(dentro, lz.gradiente(["#0b0612", "#140b20", "#1f0f30", "#2a1240"], desde=ARRANQUE - RY, hasta=SUELO))
        lz.sumar_luz(lz.desenfocar(lz.circulo(CX, 66, 10), 10) * dentro, "#4d1a6b", 0.9)
        # espinas de Giza que lo cierran, en capas
        rng = np.random.default_rng(31)
        for capa, (col, g) in enumerate((("#05030a", 1.8), ("#0e0716", 1.3))):
            esp = np.zeros((lz.H, lz.W))
            for k in range(11):
                a = np.pi * (0.05 + 0.9 * rng.random())
                p0 = (CX + np.cos(a) * (RX - 5), ARRANQUE - np.sin(a) * (RY - 5))
                p2 = (CX + (rng.random() - 0.5) * 40, SUELO - 10 - rng.random() * 50)
                curva = lz.curva(p0, (CX + (rng.random() - 0.5) * 24, 62), p2, n=18)
                esp = np.maximum(esp, lz.trazo(curva, g, 0.3))
                # pinchos
                for j in range(3, 16, 4):
                    px, py = curva[j]
                    lz_p = lz.trazo([(px, py), (px + (rng.random() - 0.5) * 4, py - 1.5 - rng.random() * 2)], 0.8, 0.1)
                    esp = np.maximum(esp, lz_p)
            lz.pintar(esp * dentro, col)
            lz.pintar(np.clip(esp - np.roll(esp, lz.s, axis=0), 0, 1) * dentro, "#7a3aa3", 0.45)
    return dentro


def _raices_arco(lz, abierto):
    """El arco de arriba: cuatro raíces trenzadas que salen de lo alto de los pilares."""
    cols = RAIZ_VIVA if abierto else RAIZ_DORMIDA
    total = np.zeros((lz.H, lz.W))
    for k in range(4):
        fase = k / 4 * 2 * np.pi + 0.4
        g = 6.0 - k * 0.6
        pts = []
        for a in np.linspace(np.pi + 0.12, -0.12, 90):
            giro = a * 7 + fase
            r = np.sin(giro) * 2.6
            pts.append((CX + np.cos(a) * (RX + r), ARRANQUE + 3 - np.sin(a) * (RY + r)))
        m = hebra(lz, pts, g, g, cols, LUZ, semilla=40 + k, fuerza_tex=0.45)
        lz.pintar(np.clip(lz.desenfocar(m, 0.8) - m, 0, 1), "#0d0a0a", 0.4)
        total = np.maximum(total, m)
    return total


def _trepadoras(lz, abierto, por_delante):
    """Raíces finas que suben enroscadas por los pilares (por detrás o por delante de la piedra)."""
    cols = RAIZ_VIVA if abierto else RAIZ_DORMIDA
    total = np.zeros((lz.H, lz.W))
    for i, pc in enumerate((CX - RX, CX + RX)):
        for k in range(2):
            fase = k * np.pi + i * 1.3
            pts, delante = [], []
            for u in np.linspace(0, 1, 80):
                giro = u * 2.3 * 2 * np.pi + fase
                pts.append((pc + np.sin(giro) * 8.6, SUELO - 3 - u * (SUELO - ARRANQUE - 2)))
                delante.append(np.cos(giro) > 0)
            for tramo in _tramos(pts, delante, por_delante):
                total = np.maximum(total, hebra(lz, tramo, 3.0 - k * 0.5, 2.6 - k * 0.5, cols, LUZ, semilla=44 + k + i * 2))
    if por_delante:
        lz.pintar(np.clip(lz.desenfocar(total, 0.8) - total, 0, 1), "#0d0a0a", 0.35)
    return total


def _pies(lz, abierto):
    """Raíces que se agarran a las losas al pie del arco."""
    cols = RAIZ_VIVA if abierto else RAIZ_DORMIDA
    rng = np.random.default_rng(50)
    for lado in (-1, 1):
        for k in range(3):
            x0 = CX + lado * (RX - 2 + rng.random() * 4)
            p1 = (x0 + lado * (5 + k * 4), SUELO - 4 + rng.random() * 2)
            p2 = (x0 + lado * (10 + k * 6), SUELO + rng.random() * 2)
            hebra(lz, lz.curva((x0, SUELO - 10), p1, p2, n=12), 3.2 - k * 0.6, 0.8, cols, LUZ, semilla=60 + k)


def _nudo_y_semilla(lz, abierto):
    """Arriba, las raíces se anudan alrededor de la Semilla del Arco."""
    cols = RAIZ_VIVA if abierto else RAIZ_DORMIDA
    cy = ARRANQUE - RY - 1
    # lazos del nudo
    for k, (a0, a1, r) in enumerate(((0.3, 2.8, 7.5), (3.5, 6.0, 7.0), (1.2, 4.4, 9.0))):
        pts = [(CX + np.cos(a) * r, cy + 3 + np.sin(a) * r * 0.7) for a in np.linspace(a0, a1, 24)]
        hebra(lz, pts, 3.2, 2.4, cols, LUZ, semilla=70 + k)
    # la semilla: un corazón de ámbar engastado
    semilla = lz.elipse(CX, cy + 4, 4.6, 5.8)
    if abierto:
        lz.sombrear(semilla, AMBAR, 3.5, LUZ, textura=lz.ruido(0.8, 2, semilla=75), fuerza_tex=0.2)
        lz.sumar_luz(lz.desenfocar(semilla, 3.0), "#ffc35a", 0.7)
        lz.pintar(lz.elipse(CX - 1.6, cy + 1.8, 1.2, 1.6), "#fff8dc", 0.9)
    else:
        lz.sombrear(semilla, APAGADO, 3.5, LUZ, textura=lz.ruido(0.8, 2, semilla=75), fuerza_tex=0.25)
        grieta = lz.trazo([(CX - 1, cy), (CX + 0.5, cy + 3), (CX - 0.8, cy + 5.5), (CX + 1, cy + 8)], 0.6, 0.3)
        lz.pintar(grieta * semilla, "#9a58c4", 0.7)
        lz.pintar(lz.elipse(CX - 1.6, cy + 1.8, 0.9, 1.2), "#8a6aa0", 0.5)
    # engarce: dos raicillas que la abrazan por delante
    for lado in (-1, 1):
        pts = lz.curva((CX + lado * 6, cy - 1), (CX + lado * 5.5, cy + 6), (CX + lado * 1.5, cy + 10.5), n=14)
        hebra(lz, pts, 1.8, 0.8, cols, LUZ, semilla=78 + lado)


def _colgantes(lz, abierto):
    """Raicillas y enredaderas que cuelgan del arco por dentro."""
    rng = np.random.default_rng(90)
    cols = RAIZ_VIVA if abierto else RAIZ_DORMIDA
    for k in range(9):
        a = np.pi * (0.12 + 0.76 * k / 8) + (rng.random() - 0.5) * 0.12
        x0, y0 = CX + np.cos(a) * (RX - 5), ARRANQUE - np.sin(a) * (RY - 5)
        largo = 5 + rng.random() * (12 if abierto else 8)
        pts = lz.curva((x0, y0), (x0 + (rng.random() - 0.5) * 4, y0 + largo * 0.6), (x0 + (rng.random() - 0.5) * 3, y0 + largo), n=10)
        if k % 3 == 0:
            hebra(lz, pts, 1.2, 0.4, cols, LUZ, semilla=91 + k)
        else:
            tallo = lz.trazo(pts, 0.7, 0.4)
            lz.pintar(tallo, "#2f5520" if abierto else "#4a4130")
            # hojitas
            for j in range(2, 10, 3):
                px, py = pts[j]
                lado = 1 if j % 2 else -1
                hoja = lz.elipse(px + lado * 1.4, py, 1.5, 0.8, 30 * lado)
                if abierto:
                    lz.sombrear(hoja, ["#1f4a1a", "#3e9a35", "#6fcf4f", "#b8ef8e"], 0.7, LUZ)
                else:
                    lz.sombrear(hoja, ["#2a2416", "#4a3f26", "#6b5c38", "#85744a"], 0.7, LUZ)
    if abierto:
        # florecillas y brotes nuevos sobre las raíces
        for (bx, by) in [(CX - RX - 2, 70), (CX - 20, 22), (CX + 22, 24), (CX + RX + 2, 66), (CX - RX + 1, 96), (CX + RX - 1, 92)]:
            lz.sombrear(np.maximum(lz.elipse(bx - 1.4, by, 1.7, 0.85, 30), lz.elipse(bx + 1.4, by - 0.6, 1.7, 0.85, -30)),
                        ["#1f4a1a", "#3e9a35", "#6fcf4f", "#b8ef8e"], 0.6, LUZ)
        for (fx, fy, col) in [(CX - RX + 3, 84, "#ffd7e0"), (CX + RX - 2, 78, "#fff3c4"), (CX - 12, 15, "#ffd7e0")]:
            for (dx, dy) in ((-0.9, 0), (0.9, 0), (0, -0.9), (0, 0.9)):
                lz.pintar(lz.circulo(fx + dx, fy + dy, 0.75), col)
            lz.pintar(lz.circulo(fx, fy, 0.55), "#f9b947")
        # setas al pie
        for (sx, sy, r) in [(12, SUELO - 8, 2.2), (15, SUELO - 7, 1.6), (84, SUELO - 8, 2.0)]:
            lz.pintar(lz.trazo([(sx, sy), (sx, sy - r * 1.2)], 0.9), "#e8dcc0")
            lz.sombrear(lz.elipse(sx, sy - r * 1.3, r, r * 0.6), ["#7a2a1a", "#b8422a", "#e0683e", "#f59a6a"], r * 0.6, LUZ)


def _musgo_raices(lz, raices, abierto):
    """Musgo encima de las raíces, por donde da la luz."""
    gy, gx = np.gradient(lz.desenfocar(raices, 1.2))
    arriba = np.clip(gy * 6 + gx * 3, 0, 1)
    manchas = np.clip((lz.ruido(2.5, 3, semilla=95) - 0.55) * 4, 0, 1)
    musgo = np.clip(arriba * 2.5, 0, 1) * manchas * raices
    lz.sombrear(musgo, MUSGO if abierto else MUSGO_SECO, 0.8, LUZ, textura=lz.ruido(0.6, 2, semilla=96), fuerza_tex=0.5)


def arco(abierto):
    lz = Lienzo(W, H, s=5, semilla=80)
    _dentro(lz, abierto)
    _umbral(lz, abierto)
    detras = _trepadoras(lz, abierto, por_delante=False)
    _pilar(lz, CX - RX - 7, CX - RX + 7, ARRANQUE + 1, True, abierto, semilla=101)
    _pilar(lz, CX + RX - 7, CX + RX + 7, ARRANQUE + 3, False, abierto, semilla=102)
    delante = _trepadoras(lz, abierto, por_delante=True)
    arriba = _raices_arco(lz, abierto)
    _musgo_raices(lz, np.maximum(np.maximum(detras, delante), arriba), abierto)
    _pies(lz, abierto)
    _nudo_y_semilla(lz, abierto)
    _colgantes(lz, abierto)
    if abierto:
        # la vida corre por las raíces: un hilo de luz dorada
        pts = [(CX + np.cos(a) * RX, ARRANQUE + 3 - np.sin(a) * RY) for a in np.linspace(np.pi, 0, 60)]
        vida = lz.trazo(pts, 0.7)
        lz.sumar_luz(lz.desenfocar(vida, 1.4), "#f9b947", 0.45)
    return lz.sprite(contorno=CONTORNO)


def main():
    tira = np.concatenate([arco(False), arco(True)], axis=1)
    ruta = os.path.join(SALIDA, "portal.png")
    Image.fromarray(tira, "RGBA").save(ruta)
    print("guardado:", ruta)


if __name__ == "__main__":
    main()
