"""EL MERCADO DE LA ESCORIA por dentro (el puesto de Chuma, Mji-Jiwe, Asterhaul), con el pintor de las cinemáticas:
lo que se ve al abrir su tienda.

    python3 herramientas/pintar_tienda_chuma.py

Genera en arte/interfaz/:
  tienda_chuma_fondo.png  216×168  el puesto: pared de sillares ocres, la boca de una fragua encendida, martillos y
                                   tenazas colgados, una balda con lingotes y una geoda partida, y el mostrador de
                                   piedra con su tablero, un yunque pequeño y un fuelle
  tienda_chuma.png        4 × 96×84  Chuma detrás del mostrador:
                            0 quieto · 1 parpadea · 2 habla (señala con el martillo) · 3 contento (martillo en alto)
Chuma es el damán de roca de siempre (pardo, bigotazo blanco, gorra plana azul, chaleco rojo sobre el mandil), pero grande.
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ, guardar_png_ligero  # noqa: E402
from pintar_casa_shamba import rect, vetas  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "interfaz")
LUZ = (-0.6, -0.7, 0.5)
PIEDRA = ["#2a1a12", "#44291a", "#5e3a24", "#7a5032", "#966a44", "#b4885a"]
MADERA = ["#1a100c", "#32201a", "#523426", "#724a34", "#946648"]
HIERRO = ["#14161c", "#2a2e3a", "#464c5c", "#6a7284", "#949cae", "#c4cad8"]
AMBAR = ["#5a2406", "#9a4a0c", "#d8841c", "#f8b040", "#ffd878", "#fff4c8"]
PELO = ["#2e2018", "#4e3a2c", "#6e5444", "#9a7a62", "#c2a486", "#e0c8aa"]
CREMA = ["#8a7a5c", "#b8a47c", "#dccaa0", "#f2e6c4", "#fff8e8"]
ROJO = ["#3a0c10", "#6a1820", "#9a2a30", "#c84a4a", "#e87a70"]
AZUL = ["#14243a", "#1e3a5a", "#2e5a8a", "#4a82b8", "#8ab8e0"]
CUERO = ["#2a1a0c", "#4a3018", "#6e4a24", "#94683a", "#b88a54"]
CONTORNO = 0.42


def fondo():
    W, H = 216, 168
    lz = Lienzo(W, H, s=4, semilla=860)
    fila = np.floor(lz.y / 11)
    col = np.floor((lz.x + (fila % 2) * 10) / 20)
    tono = (np.sin(fila * 12.9 + col * 78.2) * 43758.5) % 1
    lz.sombrear(rect(lz, 0, 0, W, H), PIEDRA, 60, LUZ, textura=0.5 + (tono - 0.5) * 0.7, fuerza_tex=0.25)
    junta = ((lz.y % 11) < 0.8) | (((lz.x + (fila % 2) * 10) % 20) < 0.8)
    lz.pintar(rect(lz, 0, 0, W, H) * junta, PIEDRA[0], 0.6)
    # la boca de la fragua, al fondo a la derecha, con el rescoldo
    boca = np.maximum(rect(lz, 140, 50, 196, 112), lz.elipse(168, 50, 28, 16) * (lz.y < 52))
    lz.pintar(boca, "#120806")
    brasa = lz.elipse(168, 104, 22, 7)
    lz.pintar(brasa * (lz.ruido(1.6, 2, semilla=861) > 0.4), AMBAR[1])
    lz.pintar(brasa * (lz.ruido(1.0, 1, semilla=862) > 0.7), AMBAR[3])
    lz.sumar_luz(lz.desenfocar(brasa, 10) * boca, AMBAR[2], 0.8)
    arco = np.clip(np.maximum(rect(lz, 136, 48, 200, 116), lz.elipse(168, 48, 32, 20) * (lz.y < 50)) - boca, 0, 1)
    lz.sombrear(arco, PIEDRA[2:], 3, LUZ)
    lz.pintar(arco * ((np.floor(np.arctan2(lz.y - 56, lz.x - 168) * 4) % 2) < 0.1) * (lz.y < 56), PIEDRA[0], 0.6)
    lz.sumar_luz(np.clip(1 - np.hypot((lz.x - 168) / 130, (lz.y - 100) / 100), 0, 1) ** 1.6, "#ff9a40", 0.35)
    # martillos y tenazas colgados de un listón
    lz.sombrear(rect(lz, 8, 14, 124, 18), MADERA[1:], 1.5, LUZ)
    for k, x in enumerate(range(16, 120, 15)):
        largo = 26 + (k % 3) * 6
        lz.pintar(lz.trazo([(x, 18), (x, 22)], 0.6), HIERRO[1])
        if k % 2 == 0:
            lz.sombrear(lz.trazo([(x, 22), (x, 22 + largo)], 1.6), MADERA[2:], 1, LUZ)
            lz.sombrear(rect(lz, x - 5, 22 + largo, x + 5, 28 + largo), HIERRO[1:], 2, LUZ)
        else:
            for lado in (-1, 1):
                lz.sombrear(lz.trazo([(x, 22), (x + lado * 2.5, 22 + largo * 0.7), (x + lado * 1.2, 22 + largo)], 1.3), HIERRO, 1, LUZ)
    # la balda con lingotes y una geoda partida
    lz.sombrear(rect(lz, 8, 80, 124, 85), MADERA[2:], 2, LUZ, textura=vetas(lz, 0.4, 13, True, 863), fuerza_tex=0.4)
    for k, x in enumerate((14, 32, 50)):
        ling = lz.poligono([(x, 80), (x + 15, 80), (x + 12, 72), (x + 3, 72)])
        lz.sombrear(ling, HIERRO if k != 1 else AMBAR[1:], 2, LUZ)
    lz.sombrear(lz.poligono([(18, 72), (44, 72), (41, 65), (21, 65)]), HIERRO[1:], 2, LUZ)
    geoda = lz.elipse(96, 72, 14, 9)
    lz.sombrear(geoda, PIEDRA[1:], 4, LUZ)
    dentro = lz.elipse(96, 71, 9, 5.6)
    lz.sombrear(dentro, AMBAR[1:], 2, LUZ)
    lz.pintar(dentro * (lz.ruido(0.9, 1, semilla=864) > 0.75), AMBAR[5], 0.9)
    lz.sumar_luz(lz.desenfocar(dentro, 4), AMBAR[3], 0.5)
    # el mostrador de piedra con tablero, un yunque pequeño y un fuelle
    mostrador = rect(lz, 0, 128, W, H)
    lz.sombrear(mostrador, PIEDRA[:5], 18, LUZ, textura=0.5 + (tono - 0.5) * 0.6, fuerza_tex=0.25)
    lz.pintar(mostrador * junta, PIEDRA[0], 0.5)
    lz.sombrear(rect(lz, 0, 122, W, 130), MADERA[1:], 2, LUZ, textura=vetas(lz, 0.4, 25, True, 865), fuerza_tex=0.4)
    lz.pintar(rect(lz, 0, 130, W, 132), "#0a0606", 0.5)
    yunque = np.maximum.reduce([lz.poligono([(150, 122), (166, 122), (164, 116), (152, 116)]),
                                lz.poligono([(140, 116), (172, 116), (182, 112), (172, 108), (140, 108)])])
    lz.sombrear(yunque, HIERRO, 3, LUZ)
    fuelle = lz.poligono([(20, 122), (52, 116), (52, 106), (20, 112)])
    lz.sombrear(fuelle, CUERO, 4, LUZ, textura=((lz.x % 4) < 0.8) * 1.0, fuerza_tex=-0.4)
    lz.sombrear(lz.trazo([(52, 111), (64, 111)], 1.5), HIERRO, 0.7, LUZ)
    return lz.final(0.016)


def chuma(f):
    """f: 0 quieto · 1 parpadea · 2 habla · 3 contento"""
    W, H = 96, 84
    lz = Lienzo(W, H, s=4, semilla=870 + f)
    cx = 46
    sube = -2 if f == 3 else 0
    cuerpo = lz.elipse(cx, 66 + sube, 28, 22)
    lz.sombrear(cuerpo, PELO, 18, LUZ, textura=lz.ruido(1.5, 3, semilla=871), fuerza_tex=0.15)
    mandil = lz.poligono([(cx - 15, 56 + sube), (cx + 15, 56 + sube), (cx + 18, 84), (cx - 18, 84)])
    lz.sombrear(mandil, CUERO, 8, LUZ, textura=vetas(lz, 0.4, 7, True, 872), fuerza_tex=0.3)
    for lado in (-1, 1):                                                     # el chaleco rojo, abierto
        chaleco = lz.poligono([(cx + lado * 13, 52 + sube), (cx + lado * 25, 58 + sube), (cx + lado * 26, 84), (cx + lado * 16, 84)])
        lz.sombrear(chaleco, ROJO, 5, LUZ)
        lz.pintar(lz.circulo(cx + lado * 15, 66 + sube, 1.2) + lz.circulo(cx + lado * 16, 74 + sube, 1.2), "#f0cc60")
    if f == 3:
        brazos = [[(cx - 24, 58), (cx - 32, 46), (cx - 30, 36)], [(cx + 24, 58), (cx + 34, 44), (cx + 34, 30)]]
    elif f == 2:
        brazos = [[(cx - 24, 62), (cx - 28, 72), (cx - 24, 80)], [(cx + 24, 60), (cx + 38, 54), (cx + 44, 48)]]
    else:
        brazos = [[(cx - 24, 62), (cx - 28, 72), (cx - 24, 80)], [(cx + 24, 62), (cx + 28, 72), (cx + 24, 80)]]
    for pts in brazos:
        pts = [(x, y + sube) for (x, y) in pts]
        lz.sombrear(lz.trazo(pts, 10, 7), PELO, 4, LUZ)
        lz.sombrear(lz.circulo(pts[-1][0], pts[-1][1], 4.5), PELO[1:], 2, LUZ)
    if f in (2, 3):                                                           # el martillo, en la mano derecha
        px, py = brazos[1][-1][0], brazos[1][-1][1] + sube
        lz.sombrear(lz.trazo([(px, py + 4), (px + 2, py - 16)], 2.2), MADERA[2:], 1, LUZ)
        lz.sombrear(rect(lz, px - 5, py - 24, px + 9, py - 16), HIERRO[1:], 2, LUZ)
    cy = 30 + sube
    cabeza = lz.elipse(cx, cy, 23, 18)
    lz.sombrear(cabeza, PELO, 14, LUZ, textura=lz.ruido(1.5, 3, semilla=873), fuerza_tex=0.15)
    for ox in (cx - 17, cx + 17):
        oreja = lz.circulo(ox, cy - 13, 5)
        lz.sombrear(oreja, PELO, 3, LUZ)
        lz.pintar(lz.circulo(ox, cy - 12, 2.6), "#c87a80", 0.8)
    morro = lz.elipse(cx, cy + 8, 12, 7)
    lz.sombrear(morro, CREMA[1:], 6, LUZ)
    lz.sombrear(lz.elipse(cx, cy + 4, 3.4, 2.4), ["#140e10", "#2a1a1e", "#4a3236"], 1.5, LUZ)      # la nariz
    bigote = np.maximum(lz.elipse(cx - 7, cy + 9, 9, 3.4, 12), lz.elipse(cx + 7, cy + 9, 9, 3.4, -12))
    lz.sombrear(bigote, CREMA[2:], 3, LUZ)                                    # el bigotazo blanco
    for ox in (cx - 8, cx + 8):
        oy = cy - 3
        if f == 1:
            lz.pintar(lz.trazo([(ox - 3, oy + 1), (ox + 3, oy + 1)], 1.0), "#140e10")
        elif f == 3:
            lz.pintar(lz.trazo([(ox - 3, oy + 2), (ox, oy - 1), (ox + 3, oy + 2)], 1.0), "#140e10")
        else:
            lz.pintar(lz.elipse(ox, oy, 2.8, 3.2), "#140e10")
            lz.pintar(lz.circulo(ox - 1, oy - 1.2, 1.0), "#ffffff")
    if f in (2, 3):
        lz.pintar(lz.elipse(cx, cy + 14, 3.4, 2.2), "#3a1a1a")
    gorra = lz.elipse(cx - 1, cy - 15, 22, 7)                                 # la gorra plana azul y su visera
    lz.sombrear(gorra, AZUL, 5, LUZ, textura=lz.ruido(0.8, 2, semilla=874), fuerza_tex=0.15)
    lz.sombrear(lz.poligono([(cx - 18, cy - 10), (cx + 6, cy - 10), (cx + 2, cy - 6), (cx - 20, cy - 7)]), AZUL[:4], 2, LUZ)
    return lz.sprite(contorno=CONTORNO)


def main():
    out = (np.clip(fondo(), 0, 1) * 255).round().astype(np.uint8)
    guardar_png_ligero(os.path.join(SALIDA, "tienda_chuma_fondo.png"), out)
    hoja = np.concatenate([chuma(f) for f in range(4)], axis=1)
    Image.fromarray(hoja, "RGBA").save(os.path.join(SALIDA, "tienda_chuma.png"))
    print("Tienda de Chuma en", SALIDA)


if __name__ == "__main__":
    main()
