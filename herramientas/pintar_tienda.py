"""EL PUESTO DE TAWI por dentro (con el pintor de las cinemáticas): lo que se ve al abrir su tienda.

    python3 herramientas/pintar_tienda.py

Genera en arte/interfaz/:
  tienda_fondo.png   216×168  el puesto: toldo de rayas, estantes con tarros, sacos y hierbas, un farolillo,
                              y el mostrador de madera delante (Tawi se dibuja entre los estantes y el mostrador)
  tienda_tawi.png    4 × 96×84  Tawi detrás del mostrador:
                       0 quieto · 1 parpadea · 2 habla (pico abierto, un ala señala) · 3 contento (alas arriba)
Tawi es el de siempre (pájaro naranja de pecho claro, copete y una mochila enorme), pero grande.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ, guardar_png_ligero  # noqa: E402
from pintar_casa_shamba import rect, vetas  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "interfaz")
LUZ = (-0.6, -0.7, 0.5)
PLUMA = ["#5a2a08", "#8a420e", "#b85f16", "#d97f22", "#eda03a", "#f6c060", "#fbdc8c"]
PECHO = ["#8a6a48", "#b8946a", "#dcbc8e", "#efd8b0", "#fbefd6"]
PICO = ["#6a2a08", "#a8420c", "#d86a18", "#f09030"]
MOCHILA = ["#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259"]
MADERA = ["#1f140e", "#3a2418", "#5a3826", "#7d5034", "#a0704a", "#c09068"]
TOLDO_R = ["#5a1820", "#8f2532", "#b03a44", "#d5525e"]
TOLDO_C = ["#a89878", "#d6c8a8", "#efe6cf", "#fffaf0"]
CONTORNO = 0.42


# ---------------------------------------------------------------- el puesto por dentro
def fondo():
    W, H = 216, 168
    lz = Lienzo(W, H, s=4, semilla=81)
    # pared de tablas del fondo, con la luz cálida del farolillo
    pared = np.ones((lz.H, lz.W))
    lz.pintar(pared, MADERA[1])
    tablas = vetas(lz, 0.5, 21, False, 82)
    lz.sombrear(rect(lz, 0, 0, W, H), MADERA[:5], 60, LUZ, textura=tablas, fuerza_tex=0.5)
    lz.pintar(rect(lz, 0, 0, W, H) * ((lz.x % 18) < 0.8), MADERA[0], 0.8)
    luz_farol = np.clip(1 - np.hypot((lz.x - 168) / 120, (lz.y - 60) / 90), 0, 1)
    lz.sumar_luz(luz_farol ** 1.6, "#ffb860", 0.35)
    # estantes con tarros, sacos y botellas
    rng = np.random.default_rng(83)
    for (y, x0, x1) in ((62, 6, 70), (100, 6, 70), (62, 146, 210), (100, 146, 210)):
        lz.sombrear(rect(lz, x0, y, x1, y + 4), MADERA[1:], 2, LUZ, textura=vetas(lz, 0.4, 13, True, y), fuerza_tex=0.4)
        lz.pintar(rect(lz, x0, y + 4, x1, y + 6), "#120b08", 0.6)
        x = x0 + 3
        while x < x1 - 8:
            tipo = rng.integers(4)
            if tipo == 0:      # tarro de cristal con tapa de tela
                w, h = 9, 13
                cuerpo = np.maximum(rect(lz, x, y - h, x + w, y), lz.elipse(x + w / 2, y - h, w / 2, 2))
                col = [["#2f5a3a", "#4c7d4a", "#77a35e"], ["#6e3218", "#9c4f24", "#c67238"], ["#3a1650", "#6b2a8f", "#a855d6"],
                       ["#a37036", "#d29a43", "#efc06a"]][rng.integers(4)]
                lz.sombrear(cuerpo, ["#1a1a20"] + col + ["#e8f0dc"], 3, LUZ)
                lz.pintar(lz.trazo([(x + 2, y - h + 2), (x + 2, y - 2)], 0.8, 0.8), "#ffffff", 0.35)
                lz.sombrear(lz.elipse(x + w / 2, y - h - 1, w / 2 + 0.5, 2), TOLDO_R, 1, LUZ)
            elif tipo == 1:    # saquito atado
                w, h = 11, 12
                saco = lz.poligono([(x, y), (x + 1, y - h + 4), (x + w / 2, y - h), (x + w - 1, y - h + 4), (x + w, y)])
                lz.sombrear(saco, ["#4a3a26", "#6e5a40", "#9a8462", "#bfa982", "#ddc8a0"], 4, LUZ)
                lz.pintar(lz.trazo([(x + 2, y - h + 4), (x + w - 2, y - h + 4)], 0.8, 0.8), "#3b2416")
            elif tipo == 2:    # botella fina
                w, h = 6, 16
                bot = np.maximum(rect(lz, x, y - h + 6, x + w, y), rect(lz, x + 2, y - h, x + w - 2, y - h + 6))
                lz.sombrear(bot, ["#0e1c1a", "#24433f", "#3a615a", "#5d8074", "#a8c8b4"], 2, LUZ)
                lz.pintar(rect(lz, x + 2, y - h - 1, x + w - 2, y - h + 1), "#7f4d33")
            else:              # piedras brillantes (rarezas de otros mundos)
                w, h = 10, 6
                for k in range(3):
                    cx, cy = x + 2 + k * 3, y - 2 - (k % 2) * 2
                    lz.sombrear(lz.circulo(cx, cy, 2.2), [["#1e2038", "#335777", "#97c1bf", "#e8f0dc"],
                                                          ["#5a1a08", "#d86a18", "#f9b947", "#fff3c4"]][k % 2], 1.5, LUZ)
                lz.sumar_luz(lz.desenfocar(lz.circulo(x + 5, y - 3, 3), 2), "#97c1bf", 0.3)
            x += w + 3 + rng.integers(3)
    # hierbas secas colgando y el farolillo
    for k in range(5):
        hx = 82 + k * 12
        lz.pintar(lz.trazo([(hx, 22), (hx, 36)], 0.6, 0.6), "#3b2416")
        manojo = lz.poligono([(hx - 4, 36), (hx + 4, 36), (hx + 1, 50), (hx - 1, 50)])
        lz.sombrear(manojo, [["#2f4422", "#4d6436", "#6a8246", "#9aa95f"], ["#5a3a22", "#a37036", "#d29a43", "#efc06a"]][k % 2], 2, LUZ,
                    textura=vetas(lz, 0.3, 5, False, 84 + k), fuerza_tex=0.6)
    lz.pintar(lz.trazo([(168, 22), (168, 34)], 0.7, 0.7), "#1b1c1f")
    farol = np.maximum(rect(lz, 162, 34, 174, 48), lz.elipse(168, 34, 6, 2))
    lz.sombrear(farol, ["#1b1c1f", "#3d3f43", "#6a6c6f"], 1.5, LUZ)
    lz.pintar(rect(lz, 164, 36, 172, 46), "#f9b947")
    lz.pintar(rect(lz, 166, 38, 170, 44), "#fff3c4")
    lz.sumar_luz(lz.desenfocar(lz.circulo(168, 41, 10), 6), "#ffc060", 0.7)
    # el toldo de rayas, arriba, con el borde festoneado
    for k in range(int(W / 12) + 1):
        x0 = k * 12
        franja = lz.poligono([(x0, 0), (x0 + 12, 0), (x0 + 12, 22), (x0, 22)])
        festo = lz.elipse(x0 + 6, 22, 6, 4) * (lz.y > 21)
        m = np.maximum(franja, festo)
        lz.sombrear(m, TOLDO_R if k % 2 == 0 else TOLDO_C, 4, LUZ, textura=vetas(lz, 0.3, 9, False, 90 + k), fuerza_tex=0.25)
    lz.pintar(rect(lz, 0, 0, W, 4), "#120b08", 0.4)
    lz.pintar(np.clip((26 - lz.y) / 8, 0, 1) * (lz.y > 22) * (lz.y < 30), "#120b08", 0.35)    # sombra del toldo
    # el mostrador
    mostrador = rect(lz, 0, 128, W, H)
    lz.sombrear(mostrador, MADERA, 18, LUZ, textura=vetas(lz, 0.4, 25, True, 95), fuerza_tex=0.45)
    lz.sombrear(rect(lz, 0, 124, W, 131), MADERA[2:], 2, LUZ, textura=vetas(lz, 0.4, 25, True, 96), fuerza_tex=0.4)
    lz.pintar(rect(lz, 0, 131, W, 133), "#120b08", 0.5)
    for x in range(14, W, 40):
        lz.pintar(rect(lz, x, 133, x + 1.2, H), MADERA[0], 0.8)
    # sobre el mostrador: una balanza y una cesta de setas
    lz.sombrear(rect(lz, 20, 118, 22, 124), ["#3d3f43", "#6a6c6f", "#a3a4a6"], 1, LUZ)
    lz.pintar(lz.trazo([(12, 112), (30, 112)], 0.9, 0.9), "#6a6c6f")
    for bx in (12, 30):
        lz.sombrear(lz.elipse(bx, 116, 5, 1.6), ["#5a1a08", "#a8693a", "#e8b860"], 1, LUZ)
        lz.pintar(lz.trazo([(bx, 112), (bx - 4, 116)], 0.4, 0.4), "#3d3f43")
        lz.pintar(lz.trazo([(bx, 112), (bx + 4, 116)], 0.4, 0.4), "#3d3f43")
    cesta = np.maximum(lz.elipse(190, 122, 14, 4), rect(lz, 177, 116, 203, 124) * (lz.y > 117))
    lz.sombrear(cesta, ["#3d2a10", "#704f25", "#a37036", "#d29a43"], 3, LUZ, textura=vetas(lz, 0.3, 3, False, 97), fuerza_tex=0.6)
    for k in range(4):
        sx = 182 + k * 5
        lz.sombrear(lz.elipse(sx, 114 - (k % 2), 3.2, 2.2), ["#5a1820", "#b03a44", "#e98378"], 1.2, LUZ)
        lz.pintar(lz.circulo(sx - 1, 113 - (k % 2), 0.6), "#fff3c4")
    return lz.final(0.016)


# ---------------------------------------------------------------- Tawi grande
def tawi(f):
    """f: 0 quieto · 1 parpadea · 2 habla · 3 contento"""
    W, H = 96, 84
    lz = Lienzo(W, H, s=4, semilla=100 + f)
    cx, base = 48, 84
    sube = -2 if f == 3 else 0
    # la mochila enorme, detrás (con cosas que asoman: una seta, musgo, un mapa enrollado, un cazo)
    moch = lz.elipse(cx + 16, 34 + sube, 22, 26)
    lz.sombrear(moch, MOCHILA, 14, LUZ, textura=vetas(lz, 0.5, 9, False, 101), fuerza_tex=0.35, recorte=("#e0a060", 0.5), recorte_dir=(1, -0.6))
    lz.pintar(lz.trazo([(cx - 2, 26 + sube), (cx + 34, 30 + sube)], 1.6, 1.6), MOCHILA[0], 0.8)          # costura
    for (x, y) in ((cx + 10, 46), (cx + 26, 44)):
        lz.sombrear(rect(lz, x - 3, y - 4 + sube, x + 3, y + 3 + sube), MOCHILA[1:], 1.5, LUZ)
        lz.sombrear(lz.circulo(x, y + sube, 1.2), ["#3d3f43", "#a3a4a6", "#fff3c4"], 0.6, LUZ)
    seta = lz.elipse(cx + 6, 8 + sube, 9, 6) * (lz.y < 10 + sube)
    lz.sombrear(seta, ["#5a1820", "#8f2532", "#d5525e", "#e98378"], 4, LUZ)
    for (x, y) in ((cx + 3, 5), (cx + 9, 6), (cx + 6, 3)):
        lz.pintar(lz.circulo(x, y + sube, 1.0), "#fff3c4")
    lz.sombrear(rect(lz, cx + 4, 9 + sube, cx + 8, 14 + sube), PECHO, 1, LUZ)
    mapa = lz.trazo([(cx + 22, 14 + sube), (cx + 34, 2 + sube)], 4, 4)
    lz.sombrear(mapa, ["#6d4a30", "#a3794f", "#e3c391", "#f3e0b8"], 2, LUZ)
    lz.pintar(lz.trazo([(cx + 24, 13 + sube), (cx + 26, 11 + sube)], 0.5, 0.5), "#b03a44")
    lz.sombrear(lz.elipse(cx + 32, 20 + sube, 7, 4), ["#2f4422", "#4d6436", "#6a8246", "#9aa95f"], 2, LUZ,
                textura=lz.ruido(0.8, 2, semilla=102), fuerza_tex=0.5)
    # el cuerpo redondo y el pecho claro
    cuerpo = lz.elipse(cx - 2, 64 + sube, 26, 24)
    lz.sombrear(cuerpo, PLUMA, 18, LUZ, textura=lz.ruido(1.5, 3, semilla=103), fuerza_tex=0.18,
                recorte=("#ffe6a0", 0.5), recorte_dir=(-1, -0.6))
    pecho = lz.elipse(cx - 4, 68 + sube, 15, 15)
    lz.sombrear(pecho, PECHO, 10, LUZ)
    for k in range(3):                                            # plumitas del pecho
        y = 62 + k * 7 + sube
        for j in range(-2, 3):
            lz.pintar(lz.trazo([(cx - 4 + j * 5 - 2, y), (cx - 4 + j * 5, y + 2), (cx - 4 + j * 5 + 2, y)], 0.5, 0.5) * pecho,
                      PECHO[1], 0.6)
    # la correa de la mochila, cruzada
    lz.sombrear(lz.trazo([(cx + 14, 44 + sube), (cx - 14, 78 + sube)], 3, 3), MOCHILA[1:], 1.5, LUZ)
    # alas: quieta, señalando (habla) o arriba (contento)
    if f == 3:
        alas = [[(cx - 24, 56), (cx - 36, 40), (cx - 30, 30)], [(cx + 20, 56), (cx + 34, 40), (cx + 30, 30)]]
    elif f == 2:
        alas = [[(cx - 24, 58), (cx - 40, 52), (cx - 46, 44)], [(cx + 20, 60), (cx + 24, 72), (cx + 20, 80)]]
    else:
        alas = [[(cx - 24, 56), (cx - 28, 68), (cx - 24, 80)], [(cx + 20, 60), (cx + 24, 72), (cx + 20, 80)]]
    for pts in alas:
        pts = [(x, y + sube) for (x, y) in pts]
        ala = lz.trazo(pts, 12, 4.5)
        lz.sombrear(ala, PLUMA[:6], 4, LUZ, textura=vetas(lz, 0.4, 5, False, 104), fuerza_tex=0.3)
        for k in range(3):                                        # puntas de las plumas
            px, py = pts[-1]
            lz.pintar(lz.trazo([(px - 2 + k * 2, py - 2), (px - 3 + k * 2.5, py + 2)], 0.8, 0.4), PLUMA[1])
    # la cabeza redonda
    cy = 28 + sube
    cabeza = lz.elipse(cx - 6, cy, 20, 18)
    lz.sombrear(cabeza, PLUMA, 14, LUZ, textura=lz.ruido(1.5, 3, semilla=105), fuerza_tex=0.15,
                recorte=("#ffe6a0", 0.5), recorte_dir=(-1, -0.7))
    cara = lz.elipse(cx - 8, cy + 6, 13, 10)
    lz.sombrear(cara, PECHO, 8, LUZ)
    # el copete (tres plumas)
    for k, (dx, alto, ang) in enumerate(((-12, 16, -0.5), (-6, 19, -0.1), (0, 15, 0.35))):
        x0, y0 = cx + dx, cy - 15
        punta = (x0 + math.sin(ang) * alto, y0 - math.cos(ang) * alto)
        pl = lz.trazo([(x0, y0), ((x0 + punta[0]) / 2 + 2, (y0 + punta[1]) / 2), punta], 4.6, 1.2)
        lz.sombrear(pl, PLUMA[2:], 1.5, LUZ)
    # los ojos (brillantes; cerrados al parpadear; arcos de alegría si está contento)
    for ox in (cx - 15, cx - 1):
        oy = cy - 1
        if f == 1:
            lz.pintar(lz.trazo([(ox - 3, oy + 1), (ox + 3, oy + 1)], 1.0, 1.0), "#1a0f0b")
        elif f == 3:
            lz.pintar(lz.trazo([(ox - 3, oy + 2), (ox, oy - 1), (ox + 3, oy + 2)], 1.0, 1.0), "#1a0f0b")
        else:
            lz.pintar(lz.elipse(ox, oy, 3.2, 3.8), "#1a0f0b")
            lz.pintar(lz.circulo(ox - 1, oy - 1.4, 1.2), "#ffffff")
            lz.pintar(lz.circulo(ox + 1.2, oy + 1.4, 0.5), "#ffffff", 0.7)
    # mofletes
    for ox in (cx - 19, cx + 3):
        lz.pintar(lz.desenfocar(lz.elipse(ox, cy + 6, 3.4, 2), 1.0), "#e98378", 0.55)
    # el pico (abierto al hablar o de contento)
    px, py = cx - 8, cy + 6
    if f in (2, 3):
        arriba = lz.poligono([(px - 5, py - 2), (px + 5, py - 2), (px, py + 2)])
        abajo = lz.poligono([(px - 4, py + 3), (px + 4, py + 3), (px, py + 7)])
        lz.pintar(lz.elipse(px, py + 2.5, 3.5, 2), "#5a1a14")
        lz.sombrear(arriba, PICO, 2, LUZ)
        lz.sombrear(abajo, PICO, 2, LUZ)
    else:
        pico = lz.poligono([(px - 5, py - 2), (px + 5, py - 2), (px, py + 4)])
        lz.sombrear(pico, PICO, 2, LUZ)
        lz.pintar(lz.trazo([(px - 4, py), (px + 4, py)], 0.4, 0.4), PICO[0], 0.6)
    return lz.sprite(contorno=CONTORNO)


def main():
    out = (np.clip(fondo(), 0, 1) * 255).round().astype(np.uint8)
    guardar_png_ligero(os.path.join(SALIDA, "tienda_fondo.png"), out)
    hoja = np.concatenate([tawi(f) for f in range(4)], axis=1)
    Image.fromarray(hoja, "RGBA").save(os.path.join(SALIDA, "tienda_tawi.png"))
    print("Tienda de Tawi en", SALIDA)


if __name__ == "__main__":
    main()
