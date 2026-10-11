"""LA CASA DE MZEE SHAMBA, pintada con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_casa_shamba.py

Genera en arte/mundos/kitovu/ (con las mismas medidas de antes, para que puertas y choques sigan igual):
  casa_granja.png           la casa por fuera (184×140; la base de la puerta en (100, 138))
  molino.png                la rueda del molino de agua: 2 fotogramas de 44×44
  interior_casa_shamba.png  la casa por dentro (320×208; suelo de (32, 72) a (288, 184), puerta abajo en x 148-172)
  cetro_pared.png           el Cetro de Raíz colgado en la pared (22×30)
"""
import os
import sys
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa, hex2, mezcla, bolas, iluminar, RAIZ  # noqa: E402
from cinematicas import (MADERA, PIEDRA, PAJA, FOLLAJE, HIERBA, COBRE, TIERRA, piedras, flores, cetro,  # noqa: E402
                         llamas, brillo_cetro, castor)

SALIDA = os.path.join(RAIZ, "arte", "mundos", "kitovu")
LUZ = (-0.6, -0.7, 0.5)                     # el sol del juego viene de arriba a la izquierda
TRONCO = ["#1a0f0b", "#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259"]
CORTE = ["#5a3a22", "#8a6440", "#b38c5c", "#d2ac78", "#e7c995"]       # la madera de los cortes de los troncos
VERDE_CONTRA = ["#152814", "#24401f", "#355029", "#4f6e35", "#6b8a44", "#8aa152"]
PIEDRA_C = ["#3a3b33", "#5a5d50", "#7a806d", "#9aa08c", "#b9bdaa", "#d6d8c8"]
VIDRIO_DIA = ["#1e2038", "#335777", "#4a7a93", "#97c1bf", "#e8f0dc"]


def vetas(lz, escala=1.0, largo=21, horizontal=True, semilla=0):
    """Textura de madera o corteza: ruido fino estirado en una dirección."""
    n = lz.ruido(escala, 3, semilla=semilla).astype(np.float32)
    k = np.ones((1, largo), np.float32) / largo if horizontal else np.ones((largo, 1), np.float32) / largo
    n = cv2.filter2D(n, -1, k)
    return (n - n.min()) / (np.ptp(n) + 1e-6)


def rect(lz, x0, y0, x1, y1):
    return lz.poligono([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def troncos(lz, x0, x1, y0, y1, alto=6.0, semilla=0, rampa_t=TRONCO, esquinas=True):
    """Pared de troncos horizontales: cada tronco redondo, con corteza, y los cortes en las esquinas."""
    corteza = vetas(lz, 0.8, 15, True, semilla)
    nudos = lz.ruido(3, 2, semilla=semilla + 1)
    y = y0
    k = 0
    while y < y1 - 0.5:
        h = min(alto, y1 - y)
        banda = rect(lz, x0, y, x1, y + h)
        t_ = np.clip((lz.y - y) / h, 0, 1)
        redondo = np.sin(t_ * np.pi) ** 0.7 * (1 - t_ * 0.45)
        v = 0.08 + redondo * 0.78 + (corteza - 0.5) * 0.4 - (nudos > 0.8) * 0.3
        lz.pintar(banda, rampa(rampa_t, np.clip(v, 0, 1)))
        # la junta de barro entre troncos
        lz.pintar(rect(lz, x0, y + h - 0.6, x1, y + h), "#120b08", 0.9)
        if esquinas:
            for cx in (x0 - 1.6, x1 + 1.6):
                r = h * 0.55
                corte = lz.circulo(cx, y + h / 2, r)
                d = np.hypot(lz.x - cx, lz.y - (y + h / 2)) / r
                anillos = (np.sin(d * 9) * 0.5 + 0.5) * 0.35
                lz.pintar(corte, rampa(CORTE, np.clip(0.75 - d * 0.5 - anillos + (lz.x < cx) * 0.15, 0, 1)))
                aro = np.clip(corte - lz.circulo(cx, y + h / 2, r - 0.7), 0, 1)
                lz.pintar(aro, "#47291c")
        y += h
        k += 1


def paja(lz, mascara, semilla=0, capas=6.0, y0=0.0, oscuro=0.0, luz=LUZ):
    """Tejado de paja a capas: briznas que caen hacia abajo, el borde de cada capa con sombra y musgo."""
    briznas = vetas(lz, 0.5, 13, False, semilla)
    gruesas = vetas(lz, 1.6, 9, False, semilla + 1)
    capa = ((lz.y - y0) % capas) / capas
    ola = np.sin(lz.x * 0.9 + np.floor((lz.y - y0) / capas) * 1.7) * 0.12
    borde = np.clip((capa + ola - 0.78) * 6, 0, 1)
    dif, _ = lz.volumen(mascara, 14, luz)
    v = 0.2 + dif * 0.55 + (briznas - 0.5) * 0.45 + (gruesas - 0.5) * 0.25 - borde * 0.35 + (1 - capa) * 0.08 - oscuro
    lz.pintar(mascara, rampa(["#2a1a0a", "#4a3012", "#704f25", "#a37036", "#d29a43", "#efc06a", "#f8dc96"], np.clip(v, 0, 1)))
    musgo = (lz.ruido(3, 3, semilla=semilla + 2) > 0.7) * mascara * (borde > 0.2)
    lz.pintar(lz.desenfocar(musgo, 0.4), rampa(["#24401f", "#3f5a2f", "#5d7a3c", "#7c9a4c"], lz.ruido(0.8, 2)), 0.75)


def flecos(lz, x0, x1, y, largo=3.0, semilla=0):
    """Briznas sueltas colgando del alero."""
    rng = np.random.default_rng(semilla)
    m = np.zeros((lz.H, lz.W))
    x = x0
    while x < x1:
        l_ = largo * (0.5 + rng.random())
        m = np.maximum(m, lz.trazo([(x, y - 1), (x + (rng.random() - 0.5) * 1.2, y + l_)], 0.7, 0.35))
        x += 0.8 + rng.random() * 0.6
    lz.pintar(m, rampa(["#4a3012", "#a37036", "#d29a43"], lz.ruido(0.6, 2)))


def ventana(lz, x0, y0, x1, y1, encendida=0.4, contras=True, semilla=0, luz=LUZ):
    """Ventana con marco, cruz, cristal (refleja el cielo y deja ver la luz de dentro), contraventanas y jardinera."""
    marco = rect(lz, x0 - 1.2, y0 - 1.2, x1 + 1.2, y1 + 1.2)
    lz.sombrear(marco, TRONCO, 1.2, luz, textura=vetas(lz, 0.6, 9), fuerza_tex=0.3)
    cristal = rect(lz, x0, y0, x1, y1)
    reflejo = np.clip((lz.y - y0) / (y1 - y0) - (lz.x - x0) / (x1 - x0) * 0.6, 0, 1)
    dentro = rampa(["#47291c", "#a8380f", "#ef8a26", "#f9b947"], np.clip(encendida + (lz.ruido(2, 2, semilla=semilla) - 0.5) * 0.4, 0, 1))
    cielo = rampa(VIDRIO_DIA, 1 - reflejo)
    mezcla_ = np.clip(0.45 + (1 - reflejo) * 0.3, 0, 1)[..., None]
    lz.pintar(cristal, dentro * (1 - mezcla_) + cielo * mezcla_)
    # un destello en diagonal
    destello = np.clip(1 - np.abs((lz.x - x0) + (lz.y - y0) - (x1 - x0) * 0.6) / 1.2, 0, 1) * cristal
    lz.pintar(destello, "#e8f0dc", 0.55)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cruz = np.maximum(rect(lz, cx - 0.6, y0, cx + 0.6, y1), rect(lz, x0, cy - 0.6, x1, cy + 0.6))
    lz.pintar(cruz, "#2a1a12")
    if contras:
        w = (x1 - x0) * 0.42
        for (a, b) in [(x0 - 1.4 - w, x0 - 1.4), (x1 + 1.4, x1 + 1.4 + w)]:
            c_ = rect(lz, a, y0 - 1, b, y1 + 1)
            tablas = (np.abs(np.sin((lz.x - a) / (b - a) * np.pi * 3)) < 0.12).astype(float)
            lz.sombrear(c_, VERDE_CONTRA, 1.2, luz, textura=1 - tablas, fuerza_tex=0.35)
            for yy in (y0 + 1.5, y1 - 1.5):
                lz.pintar(rect(lz, a + 0.4, yy - 0.4, b - 0.4, yy + 0.4), "#152814", 0.8)
    # jardinera con flores
    j = lz.poligono([(x0 - 2.5, y1 + 1.2), (x1 + 2.5, y1 + 1.2), (x1 + 1.8, y1 + 5.5), (x0 - 1.8, y1 + 5.5)])
    lz.sombrear(j, COBRE, 1.5, luz, textura=vetas(lz, 0.6, 9, semilla=semilla + 3), fuerza_tex=0.3)
    hojas = np.zeros((lz.H, lz.W))
    rng = np.random.default_rng(semilla)
    for k in range(16):
        hx = x0 - 2 + rng.random() * (x1 - x0 + 4)
        hojas = np.maximum(hojas, lz.elipse(hx, y1 + 0.6 - rng.random() * 1.6, 1.2, 0.7, rng.random() * 180))
    lz.sombrear(hojas, ["#152814", "#24401f", "#3e6a2a", "#6fa04a", "#b4c070"], 0.6, luz)
    for k in range(7):
        fx = x0 - 1 + rng.random() * (x1 - x0 + 2)
        col = [["#8f2532", "#d5525e", "#f4b39a"], ["#b2721a", "#df9022", "#fde27e"], ["#c4ddd0", "#e8f0dc", "#ffffff"]][k % 3]
        fl = lz.circulo(fx, y1 - 0.6 - rng.random() * 1.4, 0.9)
        lz.sombrear(fl, col, 0.6, luz)


# ---------------------------------------------------------------- la casa por fuera
def casa_granja():
    lz = Lienzo(184, 140, s=4, semilla=14)
    x0, x1 = 30, 170
    suelo = 132
    # --- canaleta y el chorro de agua que cae hacia la rueda (a la izquierda)
    canal = lz.poligono([(2, 81), (34, 81), (34, 85), (2, 85)])
    lz.sombrear(canal, TRONCO, 1.6, LUZ, textura=vetas(lz, 0.6, 9), fuerza_tex=0.3)
    chorro = lz.trazo([(6, 85), (6.5, 100), (7, 136)], 3.2, 4.2)
    agua = np.clip(np.sin(lz.y * 1.3 + lz.x * 0.4) * 0.5 + 0.5, 0, 1)
    lz.pintar(chorro, rampa(["#28536b", "#4a7a93", "#97c1bf", "#e8f0dc"], agua * 0.8 + 0.1))
    # --- zócalo de piedra con musgo
    zocalo = rect(lz, x0 - 4, 116, x1 + 4, suelo)
    piedras(lz, zocalo, tam=5.2, semilla=3, luz=LUZ, mortero="#525449", rampa_p=PIEDRA_C)
    musgo = (lz.ruido(2.5, 3, semilla=31) > 0.68) * zocalo * np.clip((lz.y - 120) / 10, 0, 1)
    lz.pintar(lz.desenfocar(musgo, 0.3), rampa(["#24401f", "#3f5a2f", "#5d7a3c"], lz.ruido(0.7, 2)), 0.8)
    # --- paredes de troncos (6 px cada uno), con los cortes redondos en las esquinas
    troncos(lz, x0, x1, 70, 116, alto=6.0, semilla=4)
    # sombra del alero sobre la pared y oscuridad junto al zócalo
    lz.pintar(np.clip((84 - lz.y) / 14, 0, 1) * rect(lz, x0 - 4, 70, x1 + 4, 116), "#120b08", 0.55)
    # --- chimenea de piedra (por detrás del tejado)
    chim = rect(lz, 140, 1.5, 152, 52)
    piedras(lz, chim, tam=3.6, semilla=8, luz=LUZ, mortero="#525449", rampa_p=PIEDRA_C)
    lz.pintar(np.clip((lz.x - 146) / 6, 0, 1) * chim, "#120b08", 0.35)
    cap = rect(lz, 138, 0, 154, 3)
    lz.sombrear(cap, PIEDRA, 1.2, LUZ)
    lz.pintar(rect(lz, 141, 0, 151, 1.2), "#0d0a0a")
    lz.pintar(lz.desenfocar(rect(lz, 141, 0, 151, 2.2), 1.0), "#3d2a1a", 0.0)
    # --- el tejado de paja, grueso y a capas
    tejado_pts = [(100, 8)]
    for k in range(25):
        tt = k / 24
        tejado_pts.append((100 + 10 + 80 * tt ** 0.95 + np.sin(tt * 8) * 0.6, 8 + 66 * tt))
    tejado_pts += [(193, 75), (193, 78)]
    tejado_pts += [(7, 78), (7, 75)]
    for k in range(24, -1, -1):
        tt = k / 24
        tejado_pts.append((100 - 10 - 80 * tt ** 0.95 - np.sin(tt * 8) * 0.6, 8 + 66 * tt))
    tejado = lz.poligono(tejado_pts) * (lz.x < 184)
    paja(lz, tejado, semilla=5, capas=6.0, y0=8)
    # el lado derecho del tejado, en sombra (la luz viene de la izquierda)
    lz.pintar(tejado * np.clip((lz.x - 118) / 60, 0, 1), "#2a1a0a", 0.35)
    # caballete de paja trenzada arriba
    cab = lz.elipse(100, 9, 13, 3.4)
    lz.sombrear(cab, PAJA, 2, LUZ, textura=vetas(lz, 0.5, 7, True), fuerza_tex=0.4)
    lz.pintar(np.clip(np.abs(np.sin(lz.x * 1.6)) - 0.85, 0, 1) * 6 * cab, "#4a3012", 0.7)
    flecos(lz, 8, 184, 77.5, 3.4, semilla=6)
    # --- buhardilla con su ventana redonda encendida
    bx = 100
    pared_b = rect(lz, bx - 11, 43, bx + 11, 61)
    troncos(lz, bx - 11, bx + 11, 43, 61, alto=4.5, semilla=9, esquinas=False)
    techito = lz.poligono([(bx - 17, 47), (bx, 25), (bx + 17, 47), (bx + 15, 49), (bx, 30), (bx - 15, 49)])
    techito = np.maximum(techito, lz.poligono([(bx - 15, 47), (bx, 27), (bx + 15, 47)]))
    paja(lz, techito, semilla=10, capas=4.0, y0=25)
    lz.pintar(techito * np.clip((lz.x - bx) / 15, 0, 1), "#2a1a0a", 0.3)
    flecos(lz, bx - 16, bx + 16, 48.5, 2.0, semilla=11)
    lz.pintar(lz.desenfocar(rect(lz, bx - 11, 61, bx + 11, 63), 0.6), "#2a1a0a", 0.6)
    aro = lz.circulo(bx, 52, 6.2)
    lz.sombrear(aro, TRONCO, 1.5, LUZ)
    vidrio = lz.circulo(bx, 52, 4.6)
    lz.pintar(vidrio, rampa(["#a8380f", "#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - bx + 1, lz.y - 51) / 5, 0, 1)))
    lz.pintar(np.maximum(rect(lz, bx - 4.6, 51.5, bx + 4.6, 52.5), rect(lz, bx - 0.5, 47.4, bx + 0.5, 56.6)) * vidrio, "#2a1a12")
    # --- ventanas grandes
    for vx in (44, 136):
        ventana(lz, vx, 81, vx + 16, 97, encendida=0.45, semilla=vx, luz=LUZ)
    # --- porche: tejadillo de tablillas, vigas, postes y tarima
    tejadillo = lz.poligono([(62, 80), (138, 80), (140, 90), (60, 90)])
    tablillas = (np.abs(np.sin((lz.x - 62) / 4 * np.pi)) < 0.12) | (np.abs(np.sin((lz.y - 80) / 3.4 * np.pi)) < 0.12)
    lz.sombrear(tejadillo, ["#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259"], 3, LUZ, textura=1 - tablillas.astype(float) * 0.8 + vetas(lz, 0.5, 5) * 0.2, fuerza_tex=0.45)
    viga = rect(lz, 60, 89.5, 140, 92)
    lz.sombrear(viga, TRONCO, 1.2, LUZ, textura=vetas(lz, 0.5, 13), fuerza_tex=0.3)
    lz.pintar(lz.desenfocar(rect(lz, 62, 92, 138, 97), 1.5) * rect(lz, x0, 92, x1, 116), "#120b08", 0.45)
    for px_ in (68, 131):
        poste = rect(lz, px_, 92, px_ + 3.6, 128)
        lz.sombrear(poste, TRONCO, 1.8, LUZ, textura=vetas(lz, 0.5, 11, False, semilla=px_), fuerza_tex=0.4)
        # tornapuntas
        lz.sombrear(lz.trazo([(px_ + 1.8, 99), (px_ + (7 if px_ < 100 else -4), 92)], 1.6), TRONCO, 0.8, LUZ)
    tarima = rect(lz, 58, 126, 142, 131.5)
    tabl = (np.abs(np.sin((lz.x - 58) / 6 * np.pi)) < 0.1).astype(float)
    lz.sombrear(tarima, COBRE, 2, LUZ, textura=1 - tabl * 0.9 + vetas(lz, 0.5, 13) * 0.2, fuerza_tex=0.5)
    # mazorcas, ajos y un manojo de hierbas colgando del porche
    for (hx, tipo) in [(75, "maiz"), (79, "maiz"), (83, "hierba"), (118, "ajo"), (122, "ajo"), (126, "maiz")]:
        lz.pintar(lz.trazo([(hx, 92), (hx, 95.5)], 0.5), "#2a1a12")
        if tipo == "maiz":
            m = lz.elipse(hx, 99.5, 1.7, 3.6)
            granos = (np.sin(lz.x * 5) * np.sin(lz.y * 5) > 0).astype(float)
            lz.sombrear(m, ["#704f25", "#c99d2a", "#e8c56a", "#fde27e"], 1, LUZ, textura=granos, fuerza_tex=0.3)
            lz.pintar(lz.trazo([(hx, 96), (hx - 1.6, 98.5)], 0.6) + lz.trazo([(hx, 96), (hx + 1.6, 98.5)], 0.6), "#c9a046")
        elif tipo == "ajo":
            m = lz.circulo(hx, 98.8, 2)
            lz.sombrear(m, ["#a3a4a6", "#e3d6c0", "#f3e0b8", "#ffffff"], 1, LUZ)
        else:
            m = lz.trazo([(hx, 95.5), (hx - 1.5, 101)], 1.2) + lz.trazo([(hx, 95.5), (hx + 1.2, 101.5)], 1.2)
            lz.sombrear(np.clip(m, 0, 1), ["#24401f", "#5d793e", "#8aa152"], 0.6, LUZ)
    # --- la puerta en arco, de tablas, con bisagras y su ventanita
    puerta = lz.poligono([(90, 126), (90, 104)] + [(100 + np.cos(a) * 10.5, 104 - np.sin(a) * 10.5) for a in np.linspace(np.pi, 0, 24)] + [(110.5, 104), (110.5, 126)])
    marco_p = np.clip(lz.desenfocar(puerta, 0.5) * 0 + lz.poligono([(88.5, 127), (88.5, 104)] + [(100 + np.cos(a) * 12, 104 - np.sin(a) * 12) for a in np.linspace(np.pi, 0, 24)] + [(112, 104), (112, 127)]) - puerta, 0, 1)
    lz.sombrear(marco_p, TRONCO, 1, LUZ, textura=vetas(lz, 0.5, 9, False), fuerza_tex=0.3)
    tablas_p = (np.abs(np.sin((lz.x - 90) / 4.2 * np.pi)) < 0.1).astype(float)
    lz.sombrear(puerta, ["#251812", "#3d2418", "#5a3826", "#7a4e35", "#9a6847"], 6, LUZ, textura=vetas(lz, 0.5, 15, False) * (1 - tablas_p * 0.8), fuerza_tex=0.45)
    for by_ in (107, 120):
        bis = lz.poligono([(90.5, by_ - 1), (98, by_ - 0.6), (98, by_ + 0.6), (90.5, by_ + 1)])
        lz.sombrear(bis, ["#1b1c1f", "#3d3f43", "#6a6c6f", "#a3a4a6"], 0.6, LUZ)
        lz.pintar(lz.circulo(96.5, by_, 0.5), "#a3a4a6")
    vent_p = lz.circulo(100, 104, 2.8)
    lz.pintar(np.clip(lz.circulo(100, 104, 3.6) - vent_p, 0, 1), "#2a1a12")
    lz.pintar(vent_p, rampa(["#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - 99, lz.y - 103) / 3, 0, 1)))
    pomo = lz.circulo(106.5, 115, 1.1)
    lz.sombrear(pomo, ["#704f25", "#c99d2a", "#fde27e"], 0.7, LUZ)
    # placa con los dos dientes de castor
    placa = lz.poligono([(95, 87.6), (105, 87.6), (105.5, 92.6), (94.5, 92.6)])
    lz.sombrear(placa, COBRE, 1, LUZ)
    for dx_ in (98.6, 101.4):
        d_ = rect(lz, dx_ - 1.1, 88.6, dx_ + 1.1, 91.8)
        lz.sombrear(d_, ["#8a7a58", "#d8cba6", "#f6efd8", "#fffdf4"], 0.6, LUZ)
    # escalones de piedra
    for (ya, yb, xa, xb) in [(131.5, 134.5, 87, 113), (134.5, 138, 85, 115)]:
        esc = rect(lz, xa, ya, xb, yb)
        lz.sombrear(esc, PIEDRA, 1.4, LUZ, textura=lz.ruido(0.7, 2), fuerza_tex=0.3)
    # farolillo junto a la puerta
    farol_v = rect(lz, 114, 98, 118.5, 104.5)
    lz.pintar(lz.trazo([(116.2, 94), (116.2, 98)], 0.6), "#1b1c1f")
    lz.pintar(farol_v, rampa(["#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - 116, lz.y - 101) / 3.4, 0, 1)))
    lz.sombrear(lz.poligono([(113.2, 98), (116.2, 95.6), (119.3, 98)]), ["#1b1c1f", "#3d3f43", "#6a6c6f"], 0.6, LUZ)
    lz.pintar(rect(lz, 113.6, 104.5, 118.8, 105.6), "#3d3f43")
    lz.sumar_luz(lz.desenfocar(farol_v, 3), "#ef8a26", 0.35)
    # --- cosas delante: tonel, caja de zanahorias, saco y rastrillo
    tonel = lz.elipse(150, 128.5, 6.2, 7.2)
    duelas = (np.abs(np.sin((lz.x - 150) / 2.2 * np.pi)) < 0.12).astype(float)
    lz.sombrear(tonel, TRONCO, 4, LUZ, textura=1 - duelas * 0.7, fuerza_tex=0.4)
    for yy in (124.2, 132.8):
        aro_t = np.clip(1 - np.abs(lz.y - yy - (np.abs(lz.x - 150) / 6.2) ** 2 * 0.7) / 0.7, 0, 1) * tonel
        lz.pintar(aro_t, "#3d3f43")
    tapa = lz.elipse(150, 121.8, 5.6, 1.6)
    lz.sombrear(tapa, CORTE, 1, LUZ)
    caja = rect(lz, 158, 123, 173, 134.5)
    lz.sombrear(caja, COBRE, 2.4, LUZ, textura=vetas(lz, 0.5, 11), fuerza_tex=0.35)
    lz.pintar(rect(lz, 158, 128.4, 173, 129.2) + rect(lz, 165.1, 123, 165.9, 134.5), "#47291c", 0.85)
    for (zx, zy, a_) in [(160.5, 121.5, -20), (164, 120.5, 10), (167.5, 121.2, -5), (170.5, 121.8, 25)]:
        z = lz.elipse(zx, zy, 1.4, 2.6, a_)
        lz.sombrear(z, ["#6e200c", "#a8380f", "#d45a17", "#ef8a26", "#f9b947"], 0.8, LUZ)
        lz.pintar(lz.trazo([(zx, zy - 2.4), (zx - 1, zy - 5)], 0.7) + lz.trazo([(zx, zy - 2.4), (zx + 1, zy - 5.2)], 0.7), "#5d793e")
    saco = lz.poligono([(34, 134), (33.5, 127), (36, 122), (38.5, 121), (41.5, 121), (44, 122), (46.5, 127), (46, 134)])
    lz.sombrear(saco, ["#5a4630", "#8a7454", "#b8a07a", "#d8c49c", "#efe0bf"], 4, LUZ, textura=(np.sin(lz.x * 4) * np.sin(lz.y * 4) > 0).astype(float), fuerza_tex=0.15)
    lz.pintar(lz.trazo([(36.5, 123.5), (43.5, 123.5)], 0.9), "#47291c")
    granos = lz.elipse(40, 121.2, 2.6, 0.9)
    lz.pintar(granos, "#c9a046")
    lz.sombrear(lz.trazo([(55, 137), (61, 103)], 1.3), TRONCO, 0.6, LUZ)
    rastr = rect(lz, 57, 101.2, 65.5, 102.6)
    lz.sombrear(rastr, ["#1b1c1f", "#3d3f43", "#6a6c6f", "#a3a4a6"], 0.6, LUZ)
    for xx in np.arange(57.5, 66, 1.6):
        lz.pintar(lz.trazo([(xx, 102.4), (xx, 104.6)], 0.5), "#6a6c6f")
    # hierba y florecitas al pie del zócalo
    hierba = np.zeros((lz.H, lz.W))
    rng = np.random.default_rng(15)
    for k in range(140):
        hx = 22 + rng.random() * 160
        if 84 < hx < 116 or 56 < hx < 144 and rng.random() < 0.7:
            continue
        hy = 132.5 + rng.random() * 5
        hierba = np.maximum(hierba, lz.trazo([(hx, hy), (hx + (rng.random() - 0.5) * 2.4, hy - 2 - rng.random() * 3)], 0.8, 0.3))
    lz.sombrear(hierba, HIERBA[1:7], 0.5, LUZ)
    flores(lz, 8, (24, 134, 56, 137), [["#8f2532", "#d5525e", "#e98378"], ["#b2721a", "#df9022", "#f1c27a"]], semilla=16, tam=0.7)
    return lz


def molino():
    """La rueda de madera del molino: 2 fotogramas (88×44) que se alternan al girar."""
    lzs = []
    for f in range(2):
        lz = Lienzo(44, 44, s=4, semilla=20 + f)
        mx, my, mr = 22, 22, 19.2
        giro = f * (2 * np.pi / 16)
        aro = np.clip(lz.circulo(mx, my, mr) - lz.circulo(mx, my, mr - 2.6), 0, 1)
        aro2 = np.clip(lz.circulo(mx, my, mr - 6) - lz.circulo(mx, my, mr - 7.6), 0, 1)
        radios = np.zeros((lz.H, lz.W))
        for k in range(8):
            a = k * np.pi / 4 + giro
            radios = np.maximum(radios, lz.trazo([(mx + np.cos(a) * 3, my + np.sin(a) * 3), (mx + np.cos(a) * (mr - 1), my + np.sin(a) * (mr - 1))], 1.8))
        lz.sombrear(radios, TRONCO, 0.9, LUZ, textura=vetas(lz, 0.4, 7), fuerza_tex=0.3)
        lz.sombrear(np.clip(aro + aro2, 0, 1), TRONCO, 1.2, LUZ, textura=vetas(lz, 0.4, 7), fuerza_tex=0.3)
        # las paletas que empujan el agua
        for k in range(12):
            a = k * 2 * np.pi / 12 + giro
            px_, py_ = mx + np.cos(a) * (mr - 0.4), my + np.sin(a) * (mr - 0.4)
            ca, sa = np.cos(a), np.sin(a)
            pal = lz.poligono([(px_ - sa * 2.4 - ca * 0.6, py_ + ca * 2.4 - sa * 0.6), (px_ + sa * 2.4 - ca * 0.6, py_ - ca * 2.4 - sa * 0.6),
                               (px_ + sa * 2.4 + ca * 2.6, py_ - ca * 2.4 + sa * 2.6), (px_ - sa * 2.4 + ca * 2.6, py_ + ca * 2.4 + sa * 2.6)])
            lz.sombrear(pal, COBRE, 1, LUZ)
        cubo = lz.circulo(mx, my, 3.4)
        lz.sombrear(cubo, ["#1b1c1f", "#3d3f43", "#6a6c6f", "#a3a4a6", "#c5c6c7"], 2, LUZ)
        lz.pintar(lz.circulo(mx, my, 1.1), "#1b1c1f")
        # gotas que salpican al subir
        rng = np.random.default_rng(f)
        gotas = np.zeros((lz.H, lz.W))
        for k in range(10):
            a = -np.pi / 2 - 0.5 + rng.random() * 1.0 - 1.2
            r = mr + 1 + rng.random() * 2
            gotas = np.maximum(gotas, lz.circulo(mx + np.cos(a) * r, my + np.sin(a) * r, 0.5 + rng.random() * 0.4))
        lz.pintar(gotas, "#c4ddd0")
        lzs.append(lz.sprite())
    return np.concatenate(lzs, axis=1)


# ---------------------------------------------------------------- la casa por dentro
def interior():
    """Vista de arriba, como las casas de la DS: pared de troncos al fondo con la chimenea, la ventana,
    el soporte del cetro, un retrato de la familia y los estantes de tarros; suelo de tablas con una
    alfombra trenzada, la mesa con la cena, los taburetes, la cama con su colcha y el saco de semillas."""
    lz = Lienzo(320, 208, s=3, semilla=33)
    X0, Y0, X1, Y1 = 32, 72, 288, 184
    luz_i = (-0.5, -0.6, 0.6)
    lz.pintar(np.ones((lz.H, lz.W)), "#100c0e")
    # --- el techo: vigas y paja vista por debajo
    techo = rect(lz, X0 - 8, 8, X1 + 8, 20)
    paja(lz, techo, semilla=40, capas=3.0, y0=8, oscuro=0.25, luz=(0, -1, 0.6))
    for vx in range(X0, X1 + 1, 40):
        viga = rect(lz, vx - 2, 8, vx + 2, 21)
        lz.sombrear(viga, TRONCO, 1.5, luz_i, textura=vetas(lz, 0.5, 9, False), fuerza_tex=0.3)
    lz.pintar(lz.desenfocar(rect(lz, X0 - 8, 19, X1 + 8, 23), 1.2), "#120b08", 0.6)
    # --- la pared del fondo: troncos
    troncos(lz, X0, X1, 20, Y0 - 3, alto=6.5, semilla=41, esquinas=False, rampa_t=["#1d1210", "#33201a", "#523328", "#714a3a", "#8c624f", "#a87d66", "#c49a80"])
    zocalo = rect(lz, X0, Y0 - 3.5, X1, Y0)
    lz.sombrear(zocalo, TRONCO[:5], 1.2, luz_i)
    # --- la ventana del fondo (de día se ve el cielo y la hierba)
    vx0, vy0, vx1, vy1 = 98, 30, 128, 54
    marco = rect(lz, vx0 - 2, vy0 - 2, vx1 + 2, vy1 + 3)
    lz.sombrear(marco, TRONCO, 1.5, luz_i, textura=vetas(lz, 0.5, 9), fuerza_tex=0.3)
    vidrio = rect(lz, vx0, vy0, vx1, vy1)
    exterior = lz.gradiente(["#6b9eab", "#97c1bf", "#c4ddd0"], desde=vy0, hasta=vy1)
    lz.pintar(vidrio, exterior)
    colina = vidrio * np.clip((lz.y - (vy1 - 7 - 2 * np.sin(lz.x / 6))) * 2, 0, 1)
    lz.pintar(colina, rampa(HIERBA[3:7], lz.ruido(1.5, 2)))
    lz.pintar(vidrio * lz.circulo(vx0 + 8, vy1 - 9, 3.4), "#5d793e")
    lz.pintar(np.maximum(rect(lz, (vx0 + vx1) / 2 - 0.8, vy0, (vx0 + vx1) / 2 + 0.8, vy1), rect(lz, vx0, (vy0 + vy1) / 2 - 0.8, vx1, (vy0 + vy1) / 2 + 0.8)), "#2a1a12")
    lz.pintar(np.clip(1 - np.abs((lz.x - vx0) + (lz.y - vy0) - 14) / 1.5, 0, 1) * vidrio, "#e8f0dc", 0.5)
    alfeizar = rect(lz, vx0 - 4, vy1 + 2, vx1 + 4, vy1 + 5)
    lz.sombrear(alfeizar, COBRE, 1.2, luz_i)
    maceta = lz.poligono([(vx0 + 2, vy1 + 2), (vx0 + 8, vy1 + 2), (vx0 + 7, vy1 - 3), (vx0 + 3, vy1 - 3)])
    lz.sombrear(maceta, ["#5a1820", "#8f2532", "#b03a44", "#d5525e"], 1.2, luz_i)
    planta = lz.circulo(vx0 + 5, vy1 - 5.5, 3)
    lz.sombrear(planta, FOLLAJE, 1.5, luz_i, textura=lz.ruido(0.6, 2), fuerza_tex=0.4)
    # cortinas
    for (a, b) in [(vx0 - 5, vx0 + 3), (vx1 - 3, vx1 + 5)]:
        cort = rect(lz, a, vy0 - 4, b, vy1 + 1)
        pliegues = np.sin((lz.x - a) * 1.8) * 0.5 + 0.5
        lz.sombrear(cort, ["#5a1820", "#8f2532", "#b03a44", "#d5525e", "#e98378"], 2, luz_i, textura=pliegues, fuerza_tex=0.5)
    lz.sombrear(rect(lz, vx0 - 7, vy0 - 5, vx1 + 7, vy0 - 3.6), TRONCO, 0.6, luz_i)
    # --- la chimenea de piedra con su olla (40-84, 26-74)
    chim = rect(lz, 40, 22, 84, Y0 + 2)
    piedras(lz, chim, tam=6, semilla=42, luz=luz_i, mortero="#3d3a33", rampa_p=PIEDRA_C)
    repisa = rect(lz, 37, 34, 87, 38)
    lz.sombrear(repisa, TRONCO, 1.5, luz_i, textura=vetas(lz, 0.5, 13), fuerza_tex=0.3)
    boca = lz.poligono([(49, Y0 + 2), (49, 54)] + [(62 + np.cos(a) * 13, 54 - np.sin(a) * 9) for a in np.linspace(np.pi, 0, 16)] + [(75, 54), (75, Y0 + 2)])
    lz.pintar(boca, lz.gradiente(["#120b08", "#2e1208", "#4a1a08"], desde=45, hasta=Y0))
    for (a0, a1) in [((51, 70), (73, 67)), ((52, 67), (72, 70))]:
        lz.sombrear(lz.trazo([a0, a1], 3), TRONCO[:5], 1.2, (0, -1, 0.5))
    fuego = llamas(lz, 62, 69.5, 12, 15, semilla=4, n=7)
    # la olla colgando de su gancho
    lz.pintar(lz.trazo([(62, 45), (62, 52)], 0.7), "#3d3f43")
    olla = lz.elipse(62, 57.5, 7, 5.2)
    lz.sombrear(olla, ["#0d0a0a", "#1b1c1f", "#2b2c30", "#525458", "#85878a"], 3, (-0.3, -0.9, 0.5))
    lz.pintar(lz.elipse(62, 53, 6, 1.3), "#d45a17", 0.7)
    for k in range(3):
        lz.pintar(lz.desenfocar(lz.trazo(lz.curva((60 + k * 2, 52), (58 + k * 3, 46), (61 + k * 2, 40), n=10), 1.2), 0.8), "#c4ddd0", 0.25)
    # cosas en la repisa: un reloj de arena, tarro y una vela
    for (tx, th, tc) in [(43, 6, COBRE), (81, 5, ["#152814", "#24401f", "#5d793e", "#a8b866"])]:
        lz.sombrear(lz.elipse(tx, 34 - th / 2, 2.4, th / 2), tc, 1.6, luz_i)
    vela = rect(lz, 52, 28, 54.4, 34)
    lz.sombrear(vela, ["#a3794f", "#e3c391", "#f3e0b8"], 1, luz_i)
    lz.pintar(lz.elipse(53.2, 26.5, 0.8, 1.6), "#fde27e")
    # --- el soporte del cetro (148-172, 28-60): tabla tallada con raíces
    tabla = lz.poligono([(147, 27), (173, 27), (174, 61), (146, 61)])
    lz.sombrear(tabla, ["#251812", "#3d2418", "#5a3826", "#7a4e35", "#9a6847", "#b88259"], 3, luz_i, textura=vetas(lz, 0.6, 15, False), fuerza_tex=0.4)
    for k in range(5):
        rz = lz.trazo(lz.curva((150 + k * 5, 60), (148 + k * 5 + (k - 2) * 2, 46), (152 + k * 4, 30), n=14), 0.9, 0.4)
        lz.pintar(rz, "#251812", 0.7)
    for (x, y) in [(150, 30.5), (170, 30.5), (150, 57.5), (170, 57.5)]:
        lz.sombrear(lz.circulo(x, y, 1), ["#704f25", "#c99d2a", "#fde27e"], 0.6, luz_i)
    for (x, y) in [(152, 42), (168, 42)]:
        lz.sombrear(lz.trazo([(x, y), (x + (2 if x < 160 else -2), y + 2)], 1.4), ["#1b1c1f", "#525458", "#a3a4a6"], 0.6, luz_i)
    # --- el retrato de la familia (180-196, 30-50)
    cuadro = rect(lz, 179, 29, 197, 51)
    lz.sombrear(cuadro, ["#3d2a10", "#704f25", "#c99d2a", "#e8c56a"], 1.4, luz_i)
    lienzo_c = rect(lz, 181, 31, 195, 49)
    lz.pintar(lienzo_c, lz.gradiente(["#97c1bf", "#e8f0dc", "#8aa152"], desde=31, hasta=49))
    for (cx_, cy_, r_) in [(185, 43, 3), (191, 42.5, 3.4), (188, 46, 2)]:
        lz.sombrear(lz.elipse(cx_, cy_, r_, r_ * 1.2) * lienzo_c, PELO_RET, r_ * 0.6, luz_i)
        lz.sombrear(lz.circulo(cx_, cy_ - r_ * 1.3, r_ * 0.75) * lienzo_c, PELO_RET, r_ * 0.4, luz_i)
    lz.pintar(lz.elipse(191, 37.6, 3.4, 0.9) * lienzo_c, "#d29a43")
    # --- estantes con tarros de semillas y hierbas colgadas (200-250)
    rng = np.random.default_rng(44)
    for (ey, cuantos) in [(37, 5), (54, 4)]:
        est = rect(lz, 199, ey, 251, ey + 2.2)
        lz.sombrear(est, TRONCO, 1, luz_i, textura=vetas(lz, 0.5, 13), fuerza_tex=0.3)
        for (sx,) in [(203,), (247,)]:
            lz.sombrear(lz.poligono([(sx - 1, ey + 2), (sx + 1, ey + 2), (sx + 1, ey + 5), (sx - 1, ey + 2.6)]), TRONCO, 0.6, luz_i)
        for k in range(cuantos):
            x = 204 + k * 10 + rng.random()
            alto_t = 7 + rng.random() * 3
            contenido = [["#704f25", "#c99d2a", "#e8c56a"], ["#6e200c", "#d45a17", "#f9b947"], ["#1f4a1a", "#3e9a35", "#6fcf4f"],
                         ["#5a1820", "#b03a44", "#e98378"], ["#3b2416", "#7c5843", "#c79a78"]][k % 5]
            tarro = rect(lz, x - 3, ey - alto_t, x + 3, ey)
            relleno = tarro * (lz.y > ey - alto_t * 0.75)
            lz.pintar(tarro, "#c4ddd0", 0.35)
            granos = lz.ruido(0.5, 2, semilla=k + ey)
            lz.pintar(relleno, rampa(contenido, granos * 0.8 + 0.1))
            lz.pintar(np.clip(1 - np.abs(lz.x - (x - 1.8)) / 0.6, 0, 1) * tarro, "#ffffff", 0.45)
            tapa = rect(lz, x - 2.6, ey - alto_t - 1.6, x + 2.6, ey - alto_t)
            lz.sombrear(tapa, ["#5a4630", "#b8a07a", "#efe0bf"], 0.6, luz_i)
            lz.pintar(rect(lz, x - 3.2, ey - alto_t - 0.4, x + 3.2, ey - alto_t + 0.4), "#8f2532")
    for hx in (206, 214, 222, 230, 238, 246):
        manojo = lz.trazo([(hx, 21), (hx - 1, 26)], 1.4, 2.2) + lz.trazo([(hx, 21), (hx + 1.2, 26.4)], 1.2, 2.0)
        lz.sombrear(np.clip(manojo, 0, 1), ["#24401f", "#3f5a2f", "#7c9a4c", "#b4c070"] if hx % 16 else ["#3a2238", "#6a3446", "#9c4b4a"], 0.8, luz_i)
    # --- el suelo de tablas
    suelo = rect(lz, X0, Y0, X1, Y1)
    filas = np.floor((lz.y - Y0) / 8)
    tabla_id = np.floor((lz.x + filas * 19) / 52)
    juntas = ((lz.y - Y0) % 8 > 7.2) | (((lz.x + filas * 19) % 52) < 0.8)
    tono = (np.sin(tabla_id * 12.9898 + filas * 78.233) * 43758.5453) % 1
    veta = vetas(lz, 0.6, 21, True, 45)
    lz.pintar(suelo, rampa(["#3d2418", "#5a3826", "#7a4e35", "#9a6847", "#b88259"], np.clip(0.35 + (tono - 0.5) * 0.25 + (veta - 0.5) * 0.35, 0, 1)))
    lz.pintar(suelo * juntas, "#251812", 0.9)
    clavos = (((lz.x + filas * 19) % 52 > 1.5) & ((lz.x + filas * 19) % 52 < 2.6) & ((lz.y - Y0) % 8 > 1) & ((lz.y - Y0) % 8 < 2.2)) * suelo
    lz.pintar(clavos, "#1b1c1f", 0.7)
    # sombra de la pared sobre el suelo
    lz.pintar(np.clip((Y0 + 8 - lz.y) / 8, 0, 1) * suelo, "#120b08", 0.45)
    # --- la alfombra trenzada (ovalada, delante de la chimenea)
    ax_, ay_, arx, ary = 100, 138, 50, 22
    alf = lz.elipse(ax_, ay_, arx, ary)
    d_a = np.hypot((lz.x - ax_) / arx, (lz.y - ay_) / ary)
    bandas = np.floor(d_a * 8) % 3
    trenza = (np.sin(np.arctan2(lz.y - ay_, lz.x - ax_) * 60 + d_a * 50) > 0).astype(float)
    cols = [rampa(["#5a1820", "#8f2532", "#b03a44"], 0.35 + trenza * 0.35), rampa(["#704f25", "#c68756", "#e2a978"], 0.35 + trenza * 0.35),
            rampa(["#24401f", "#355029", "#5d793e"], 0.35 + trenza * 0.35)]
    col = np.where((bandas == 0)[..., None], cols[0], np.where((bandas == 1)[..., None], cols[1], cols[2]))
    lz.pintar(lz.desenfocar(lz.elipse(ax_ + 1, ay_ + 1.5, arx, ary), 1), "#120b08", 0.4)
    lz.pintar(alf, col)
    # --- la mesa con la cena (120-176, 108-128) y los taburetes
    for (tx, ty) in [(108, 122), (188, 122)]:
        lz.pintar(lz.desenfocar(lz.elipse(tx + 1, ty + 5, 6.5, 2.2), 0.8), "#120b08", 0.5)
        for dx_ in (-4, 4):
            lz.sombrear(lz.trazo([(tx + dx_, ty + 1), (tx + dx_ * 1.1, ty + 6)], 1.4), TRONCO, 0.6, luz_i)
        asiento = lz.elipse(tx, ty, 6.2, 3.8)
        lz.sombrear(asiento, CORTE, 2.4, luz_i)
        d_t = np.hypot((lz.x - tx) / 6.2, (lz.y - ty) / 3.8)
        lz.pintar(asiento * (np.sin(d_t * 14) > 0.7), "#8a6440", 0.5)
    lz.pintar(lz.desenfocar(rect(lz, 121, 126, 178, 140), 1.5), "#120b08", 0.5)
    for (lx_,) in [(123,), (172,)]:
        lz.sombrear(rect(lz, lx_, 124, lx_ + 3.4, 138), TRONCO, 1.4, luz_i)
    frente = rect(lz, 120, 122, 176, 128)
    lz.sombrear(frente, TRONCO, 2, luz_i, textura=vetas(lz, 0.5, 15), fuerza_tex=0.3)
    sobre = rect(lz, 119, 106, 177, 122.5)
    lz.sombrear(sobre, ["#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259", "#d2a07c"], 3, luz_i, textura=vetas(lz, 0.6, 25, True, 46), fuerza_tex=0.4)
    mantel = lz.poligono([(132, 106.5), (164, 106.5), (162, 122.5), (134, 122.5)])
    cuadros = ((np.floor((lz.x - 132) / 3) + np.floor((lz.y - 106) / 3)) % 2)
    lz.pintar(mantel, rampa(["#c4ddd0", "#e8f0dc"], cuadros) * 0.5 + rampa(["#8f2532", "#d5525e"], cuadros) * 0.5)
    for (px_, py_) in [(141, 113.5), (155, 113.5)]:
        plato = lz.elipse(px_, py_, 6, 3.2)
        lz.sombrear(plato, ["#85878a", "#c5c6c7", "#eeeeea", "#ffffff"], 1.5, luz_i)
        sopa = lz.elipse(px_, py_, 4, 2)
        lz.pintar(sopa, rampa(["#a8380f", "#d45a17", "#ef8a26"], lz.ruido(0.6, 2)))
    for (zx, zy) in [(148, 109), (148.5, 117)]:
        z = lz.elipse(zx, zy, 2.6, 1.2, 15)
        lz.sombrear(z, ["#6e200c", "#a8380f", "#d45a17", "#ef8a26"], 0.8, luz_i)
    pan = lz.elipse(126, 111, 4, 2.6)
    lz.sombrear(pan, ["#704f25", "#a37036", "#d29a43", "#efc06a"], 1.8, luz_i)
    lz.pintar(lz.trazo([(124.5, 110), (127.5, 112)], 0.4), "#704f25")
    jarra = lz.elipse(170, 110, 2.6, 3.4)
    lz.sombrear(jarra, ["#3a2238", "#6a3446", "#9c4b4a", "#c96d4f"], 1.4, luz_i)
    # --- la cama con su colcha de retales (250-286, 70-112)
    lz.pintar(lz.desenfocar(rect(lz, 251, 104, 289, 117), 1.2), "#120b08", 0.5)
    cabecero = rect(lz, 249, 60, 287, 74)
    lz.sombrear(cabecero, TRONCO, 2.4, luz_i, textura=vetas(lz, 0.5, 15), fuerza_tex=0.3)
    for px_ in (249, 284):
        lz.sombrear(rect(lz, px_, 58, px_ + 3.4, 113), TRONCO, 1.5, luz_i)
        lz.sombrear(lz.circulo(px_ + 1.7, 58, 2.2), CORTE, 1.2, luz_i)
    lz.sombrear(rect(lz, 252, 72, 284, 112), ["#d8cba6", "#efe0bf", "#f6efd8"], 2, luz_i)
    almohada = lz.elipse(268, 77, 12.5, 4.6)
    lz.sombrear(almohada, ["#a3a4a6", "#d8cba6", "#efe6cf", "#ffffff"], 3, luz_i)
    colcha = lz.poligono([(251, 84), (285, 84), (285.5, 112), (250.5, 112)])
    rx_ = np.floor((lz.x - 251) / 6.8)
    ry_ = np.floor((lz.y - 84) / 7)
    retal = ((rx_ * 3 + ry_ * 5) % 4).astype(int)
    pal = [["#5a1820", "#b03a44", "#e98378"], ["#704f25", "#d29a43", "#f8dc96"], ["#24401f", "#5d793e", "#a8b866"], ["#28536b", "#4a7a93", "#97c1bf"]]
    lz.volumen(colcha, 4, luz_i)
    dif_c, _ = lz.volumen(colcha, 5, luz_i)
    col_c = np.zeros((lz.H, lz.W, 3))
    for k in range(4):
        col_c += (retal == k)[..., None] * rampa(pal[k], np.clip(0.2 + dif_c * 0.7, 0, 1))
    lz.pintar(colcha, col_c)
    costuras = colcha * ((((lz.x - 251) % 6.8) < 0.45) | (((lz.y - 84) % 7) < 0.45))
    lz.pintar(costuras, "#efe6cf", 0.5)
    lz.pintar(lz.desenfocar(rect(lz, 251, 84, 285, 86), 0.6), "#120b08", 0.3)
    # --- saco de semillas (44,160) y la azada apoyada (276-287, 133-176)
    lz.pintar(lz.desenfocar(lz.elipse(46, 170, 11, 3.5), 1), "#120b08", 0.5)
    saco = lz.poligono([(35, 170), (34, 158), (38, 150), (42, 148), (47, 148), (51, 150), (55, 158), (54, 170)])
    lz.sombrear(saco, ["#5a4630", "#8a7454", "#b8a07a", "#d8c49c", "#efe0bf"], 6, luz_i, textura=(np.sin(lz.x * 4) * np.sin(lz.y * 4) > 0).astype(float), fuerza_tex=0.15)
    lz.pintar(lz.trazo([(38.5, 151.5), (50.5, 151.5)], 1.2), "#47291c")
    lz.pintar(lz.elipse(44.5, 148.6, 4.4, 1.6), "#c9a046")
    for k in range(5):
        lz.pintar(lz.circulo(36 + k * 2.6, 172.5 + (k % 2), 0.6), "#c9a046")
    lz.pintar(lz.desenfocar(lz.trazo([(277, 177), (290, 175)], 1.6), 0.6), "#120b08", 0.5)
    lz.sombrear(lz.trazo([(277, 176), (285, 135)], 1.6), TRONCO, 0.7, luz_i)
    hoja = lz.poligono([(281, 133), (289, 133.6), (289.5, 137.4), (281.5, 137)])
    lz.sombrear(hoja, ["#1b1c1f", "#3d3f43", "#6a6c6f", "#a3a4a6"], 1, luz_i)
    # una cesta con zanahorias junto a la chimenea
    cesta_m = lz.poligono([(80, 160), (98, 160), (96, 172), (82, 172)])
    for k in range(6):
        cx_ = 83 + k * 2.6
        z = lz.trazo([(cx_, 160), (cx_ + 1.5, 154)], 2.2, 0.7)
        lz.sombrear(z, ["#6e200c", "#a8380f", "#d45a17", "#ef8a26"], 0.8, luz_i)
        lz.pintar(lz.trazo([(cx_ + 1.5, 154), (cx_ + 2.5, 151)], 0.8), "#5d793e")
    lz.sombrear(cesta_m, ["#3d2a10", "#704f25", "#a37036", "#d29a43", "#efc06a"], 3, luz_i,
                textura=(np.sin(lz.x * 3) * np.sin(lz.y * 3) > 0).astype(float), fuerza_tex=0.35)
    # --- paredes laterales, delantera y la salida
    for (a, b) in [(X0 - 8, X0), (X1, X1 + 8)]:
        lado = rect(lz, a, 8, b, Y1 + 8)
        lz.sombrear(lado, TRONCO[:5], 2.5, luz_i, textura=vetas(lz, 0.6, 15, False), fuerza_tex=0.3)
    for (a, b) in [(X0 - 8, 148), (172, X1 + 8)]:
        delante = rect(lz, a, Y1, b, Y1 + 8)
        lz.sombrear(delante, TRONCO[:5], 2.5, luz_i, textura=vetas(lz, 0.6, 15), fuerza_tex=0.3)
    hueco = rect(lz, 148, Y1, 172, 208)
    lz.pintar(hueco, lz.gradiente(["#f8dc96", "#fff4d6"], desde=Y1, hasta=208))
    felpudo = rect(lz, 150, Y1 - 10, 170, Y1 - 3)
    lz.sombrear(felpudo, ["#3d2a10", "#704f25", "#a37036", "#d29a43"], 2, luz_i, textura=(np.sin(lz.x * 3) > 0).astype(float), fuerza_tex=0.3)
    # --- la luz: el fuego (cálido, desde la chimenea) y la ventana (fresca)
    propia = np.clip(lz.desenfocar(fuego, 0.6) + hueco, 0, 1)
    iluminar(lz, "#e4dcd0", [(62, 66, 160, "#ef8a26", 0.5), (113, 80, 110, "#e8f0dc", 0.35), (160, 200, 70, "#f8dc96", 0.3)], propia=propia)
    lz.sumar_luz(lz.desenfocar(fuego, 10), "#d45a17", 0.5)
    lz.sumar_luz(lz.desenfocar(rect(lz, vx0, vy0, vx1, vy1), 6) * suelo * 0, "#c4ddd0", 0.0)
    # un rayo de sol de la ventana sobre el suelo
    rayo = lz.poligono([(vx0, Y0), (vx1, Y0), (vx1 + 22, Y0 + 40), (vx0 + 18, Y0 + 40)])
    lz.sumar_luz(lz.desenfocar(rayo, 4) * np.clip(1 - (lz.y - Y0) / 40, 0, 1), "#f8e1a6", 0.35)
    # todo lo de fuera de la casa, negro
    fuera = np.ones((lz.H, lz.W)) - np.clip(rect(lz, X0 - 8, 8, X1 + 8, Y1 + 8) + hueco, 0, 1)
    lz.pintar(fuera, "#140e18")
    return lz


PELO_RET = ["#2e1a10", "#4f2d1a", "#73432a", "#96603b", "#b7814f"]


def cetro_pared():
    """El Cetro de Raíz colgado de su soporte (22×30)."""
    lz = Lienzo(22, 30, s=6, semilla=50)
    cetro(lz, 10, 29.5, 6.5, e=0.95, luz=LUZ, brilla=0.6)
    return lz


def main():
    os.makedirs(SALIDA, exist_ok=True)
    casa_granja().guardar_sprite(os.path.join(SALIDA, "casa_granja.png"))
    print("pintada la casa")
    from PIL import Image
    Image.fromarray(molino(), "RGBA").save(os.path.join(SALIDA, "molino.png"))
    print("pintado el molino")
    interior().guardar(os.path.join(SALIDA, "interior_casa_shamba.png"))
    print("pintado el interior")
    cetro_pared().guardar_sprite(os.path.join(SALIDA, "cetro_pared.png"))
    print("pintado el cetro")




# ---------------------------------------------------------------- el retrato de Mzee Shamba (64×64)
def retrato_shamba():
    """(Prueba: no se usa. El retrato pintado quedaba más borroso que el de píxel a 64×64.)
    Retrato para la caja de diálogo: Mzee Shamba de tres cuartos, con su sombrero de paja, las gafas
    redondas, la barba blanca y el delantal verde, sobre el fondo cálido de su casa."""
    lz = Lienzo(64, 64, s=8, semilla=90)
    # fondo: la pared de troncos de su casa, desenfocada, con la luz del fuego
    troncos(lz, -2, 66, -2, 66, alto=9, semilla=91, esquinas=False)
    lz.img = lz.desenfocar(lz.img[..., 0], 1.2)[..., None] * 0 + np.stack([lz.desenfocar(lz.img[..., k], 1.2) for k in range(3)], -1)
    lz.sumar_luz(np.clip(1 - np.hypot(lz.x - 6, lz.y - 50) / 60, 0, 1) ** 2, "#ef8a26", 0.45)
    lz.img *= 0.75
    # Shamba, grande (solo cabeza y hombros caben)
    castor(lz, 23, 88, 1.62, 1, sombrero=True, gafas=True, delantal=True, barba=True, sem=92,
           luz=(-0.7, -0.5, 0.55), recorte=("#ef8a26", 0.5), recorte_dir=(-1, 0.2), mirada=(1, 0))
    # marco interior oscuro (viñeta)
    vin = np.clip(np.hypot((lz.x - 32) / 40, (lz.y - 32) / 40) - 0.6, 0, 1)
    lz.pintar(vin, "#120b08", 0.6)
    return lz


if __name__ == "__main__":
    main()
