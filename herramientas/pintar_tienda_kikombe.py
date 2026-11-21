"""EL MERCADO DEL CREPÚSCULO por dentro (el puesto de té de Kikombe, Jioni, el Valle del Ocaso), con el pintor de
las cinemáticas: lo que se ve al abrir su tienda. Y los iconos de lo que vende.

    python3 herramientas/pintar_tienda_kikombe.py

Genera en arte/interfaz/:
  tienda_kikombe_fondo.png  216×168  el puesto: toldo a rayas arena y coral, tres farolillos colgados, una balda con
                                     teteras, tazas, una lente de prisma y un relojito; el mostrador de madera con un
                                     hornillo de té humeando y la Capa del Farolillero doblada
  tienda_kikombe.png        4 × 96×84  Kikombe, fénec, detrás del mostrador con su tetera:
                            0 quieto · 1 parpadea · 2 habla (sirve) · 3 contenta (la tetera en alto)
  objetos.png (iconos 28-31) reloj de bolsillo · lente de prisma · botas de arena firme · Capa del Farolillero
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
ADOBE = ["#3a1a20", "#5a2a2c", "#7a3e38", "#9a5844", "#b87454", "#d49668"]
MADERA = ["#1a100c", "#32201a", "#523426", "#724a34", "#946648"]
LATON = ["#3a2408", "#6a4614", "#a07024", "#d0a040", "#f0d070", "#fff0b0"]
AMBAR = ["#5a2406", "#9a4a0c", "#d8841c", "#f8b040", "#ffd878", "#fff4c8"]
ARENA = ["#5a3a24", "#8a6040", "#b88a5c", "#dcb486", "#f2d4a8", "#fff0d8"]
CORAL = ["#4a1418", "#7a2428", "#b04038", "#d86a50", "#f0986e"]
NOCHE = ["#0a1024", "#162248", "#22346a", "#3a5292", "#6a86c0"]
CRISTAL = ["#3a2a5a", "#5a4a8a", "#8a7ab8", "#c0b4e0", "#ece6fa"]
VIOLETA = ["#2a0e4a", "#4a1c78", "#7a3cb0", "#a86ce0", "#d4b0f8"]
CONTORNO = 0.42


def farolillo(lz, x, y):
    lz.pintar(lz.trazo([(x, 0), (x, y - 6)], 0.5), LATON[1])
    cuerpo = lz.elipse(x, y, 5, 7)
    lz.sombrear(cuerpo, AMBAR[1:], 3, LUZ)
    lz.sombrear(rect(lz, x - 4, y - 8, x + 4, y - 6), LATON[1:], 1, LUZ)
    lz.sombrear(rect(lz, x - 3, y + 6, x + 3, y + 8), LATON[1:], 1, LUZ)
    lz.sumar_luz(lz.desenfocar(cuerpo, 14), AMBAR[3], 0.7)


def tetera(lz, x, y, r=7):
    cuerpo = lz.elipse(x, y, r, r * 0.8)
    lz.sombrear(cuerpo, LATON, 3, LUZ)
    lz.sombrear(lz.trazo([(x + r - 1, y), (x + r + 5, y - 4), (x + r + 7, y - 6)], 1.4, 0.8), LATON[1:], 1, LUZ)
    asa = np.clip(lz.elipse(x - r - 1, y - 1, 3.5, 4) - lz.elipse(x - r - 1, y - 1, 2, 2.6), 0, 1)
    lz.sombrear(asa, LATON[1:], 1, LUZ)
    lz.sombrear(lz.elipse(x, y - r * 0.8, r * 0.45, 1.6), LATON[2:], 1, LUZ)
    lz.sombrear(lz.circulo(x, y - r * 0.8 - 2, 1.4), CORAL[2:], 1, LUZ)


def taza(lz, x, y):
    lz.sombrear(lz.poligono([(x - 4, y - 5), (x + 4, y - 5), (x + 3, y), (x - 3, y)]), ARENA[2:], 1.5, LUZ)
    lz.pintar(lz.elipse(x, y - 5, 4, 1.2), CORAL[1])


def fondo():
    W, H = 216, 168
    lz = Lienzo(W, H, s=4, semilla=880)
    # la pared de adobe, cálida
    fila = np.floor(lz.y / 9)
    tono = (np.sin(fila * 12.9 + np.floor((lz.x + (fila % 2) * 8) / 16) * 78.2) * 43758.5) % 1
    lz.sombrear(rect(lz, 0, 0, W, H), ADOBE, 60, LUZ, textura=0.5 + (tono - 0.5) * 0.6, fuerza_tex=0.2)
    lz.sumar_luz(np.clip(1 - np.hypot((lz.x - 108) / 150, (lz.y - 60) / 110), 0, 1) ** 1.4, "#ffb060", 0.35)
    # una ventana con el atardecer parado
    ven = rect(lz, 150, 34, 200, 92)
    lz.pintar(ven, "#e8885a")
    lz.pintar(ven * (lz.y < 60), "#b05a6a")
    lz.pintar(ven * (lz.y < 46), "#6a3a6a")
    lz.sumar_luz(lz.desenfocar(lz.circulo(176, 78, 6) * ven, 3), "#fff0b0", 0.9)
    marco = np.clip(rect(lz, 146, 30, 204, 96) - ven, 0, 1) + rect(lz, 173, 34, 177, 92) * ven
    lz.sombrear(np.clip(marco, 0, 1), MADERA[1:], 2, LUZ)
    # el toldo a rayas arena y coral
    toldo = lz.poligono([(0, 0), (W, 0), (W, 20), (0, 20)])
    raya = ((lz.x // 27) % 2) == 0
    lz.sombrear(toldo * raya, ARENA[1:], 6, LUZ)
    lz.sombrear(toldo * (1 - raya), CORAL, 6, LUZ)
    festón = lz.poligono([(0, 20), (W, 20), (W, 22), (0, 22)]) + sum(lz.circulo(x, 21, 6) * (lz.y > 20) for x in range(13, W, 27))
    lz.sombrear(np.clip(festón, 0, 1) * (lz.y < 28), CORAL[1:], 2, LUZ)
    for x in (40, 108, 176):
        farolillo(lz, x, 40)
    # la balda: teteras, tazas, una lente de prisma y un relojito
    lz.sombrear(rect(lz, 6, 84, 138, 89), MADERA[2:], 2, LUZ, textura=vetas(lz, 0.4, 13, True, 881), fuerza_tex=0.4)
    tetera(lz, 22, 76)
    tetera(lz, 54, 77, 6)
    for x in (72, 82):
        taza(lz, x, 84)
    lente = np.clip(lz.circulo(104, 75, 7) - lz.circulo(104, 75, 5.2), 0, 1)
    lz.sombrear(lente, LATON, 1.5, LUZ)
    lz.sombrear(lz.circulo(104, 75, 5.2), CRISTAL[1:], 2, LUZ)
    lz.sumar_luz(lz.desenfocar(lz.circulo(104, 75, 3), 3), VIOLETA[3], 0.6)
    reloj = lz.circulo(126, 77, 6)
    lz.sombrear(reloj, LATON, 2, LUZ)
    lz.pintar(lz.circulo(126, 77, 4.4), ARENA[5])
    lz.pintar(lz.trazo([(126, 77), (126, 74)], 0.5) + lz.trazo([(126, 77), (128.5, 78)], 0.5), MADERA[0])
    # el mostrador de madera con el hornillo de té y la capa doblada
    mostrador = rect(lz, 0, 128, W, H)
    lz.sombrear(mostrador, MADERA, 18, LUZ, textura=vetas(lz, 0.5, 9, True, 882), fuerza_tex=0.35)
    lz.sombrear(rect(lz, 0, 122, W, 130), MADERA[1:], 2, LUZ, textura=vetas(lz, 0.4, 25, True, 883), fuerza_tex=0.4)
    lz.pintar(rect(lz, 0, 130, W, 132), "#0a0606", 0.5)
    hornillo = rect(lz, 160, 110, 188, 122)
    lz.sombrear(hornillo, LATON[:5], 3, LUZ)
    lz.sumar_luz(lz.desenfocar(rect(lz, 164, 118, 184, 122), 4), AMBAR[3], 0.8)
    tetera(lz, 174, 102, 8)
    vapor = sum(lz.trazo(lz.curva((183 + k * 4, 94), (178 + k * 4, 84), (190 + k * 4, 76), (184 + k * 4, 64)), 1.4, 0.4) for k in range(2))
    lz.pintar(np.clip(vapor, 0, 1), "#fff0e0", 0.22)
    capa = lz.poligono([(18, 122), (58, 122), (54, 112), (22, 112)])
    lz.sombrear(capa, NOCHE, 3, LUZ)
    lz.pintar(lz.trazo([(22, 112), (54, 112)], 0.8), LATON[4])
    return lz.final(0.016)


def kikombe(f):
    """f: 0 quieto · 1 parpadea · 2 habla (sirve) · 3 contenta"""
    W, H = 96, 84
    lz = Lienzo(W, H, s=4, semilla=890 + f)
    cx = 46
    sube = -2 if f == 3 else 0
    cuerpo = lz.elipse(cx, 70 + sube, 24, 20)
    lz.sombrear(cuerpo, ARENA, 16, LUZ, textura=lz.ruido(1.5, 3, semilla=891), fuerza_tex=0.12)
    vestido = lz.poligono([(cx - 18, 56 + sube), (cx + 18, 56 + sube), (cx + 24, 84), (cx - 24, 84)])
    lz.sombrear(vestido, CORAL, 8, LUZ)
    lz.pintar(vestido * ((lz.y % 6) < 0.8), CORAL[0], 0.35)
    lz.pintar(lz.trazo([(cx - 16, 58 + sube), (cx + 16, 58 + sube)], 1.2), LATON[3])
    if f == 3:
        brazos = [[(cx - 20, 60), (cx - 30, 48), (cx - 28, 38)], [(cx + 20, 60), (cx + 30, 48), (cx + 28, 36)]]
    elif f == 2:
        brazos = [[(cx - 20, 62), (cx - 26, 72), (cx - 20, 80)], [(cx + 20, 60), (cx + 34, 62), (cx + 40, 66)]]
    else:
        brazos = [[(cx - 20, 62), (cx - 26, 72), (cx - 20, 80)], [(cx + 20, 62), (cx + 26, 72), (cx + 20, 80)]]
    for pts in brazos:
        pts = [(x, y + sube) for (x, y) in pts]
        lz.sombrear(lz.trazo(pts, 8, 6), ARENA, 4, LUZ)
        lz.sombrear(lz.circulo(pts[-1][0], pts[-1][1], 4), ARENA[1:], 2, LUZ)
    if f == 2:
        tetera(lz, brazos[1][-1][0] + 8, brazos[1][-1][1] + sube, 7)        # sirve
        lz.pintar(lz.trazo([(brazos[1][-1][0] + 22, brazos[1][-1][1] - 2), (brazos[1][-1][0] + 24, 84)], 0.8), AMBAR[2], 0.8)
    cy = 36 + sube
    # las orejas enormes de fénec
    for lado in (-1, 1):
        oreja = lz.poligono([(cx + lado * 6, cy - 8), (cx + lado * 18, cy - 4), (cx + lado * 26, cy - 34)])
        lz.sombrear(oreja, ARENA, 5, LUZ)
        lz.pintar(lz.poligono([(cx + lado * 9, cy - 8), (cx + lado * 16, cy - 6), (cx + lado * 23, cy - 28)]), "#e0a0a0", 0.75)
    cabeza = lz.elipse(cx, cy, 16, 13)
    lz.sombrear(cabeza, ARENA, 12, LUZ, textura=lz.ruido(1.5, 3, semilla=893), fuerza_tex=0.12)
    morro = lz.poligono([(cx - 8, cy + 2), (cx + 8, cy + 2), (cx + 2, cy + 13), (cx - 2, cy + 13)])
    lz.sombrear(morro, ARENA[3:], 4, LUZ)
    lz.sombrear(lz.elipse(cx, cy + 12, 2.6, 1.8), ["#140e10", "#2a1a1e", "#4a3236"], 1, LUZ)
    for ox in (cx - 7, cx + 7):
        oy = cy - 1
        if f == 1:
            lz.pintar(lz.trazo([(ox - 3, oy + 1), (ox + 3, oy + 1)], 1.0), "#140e10")
        elif f == 3:
            lz.pintar(lz.trazo([(ox - 3, oy + 2), (ox, oy - 1), (ox + 3, oy + 2)], 1.0), "#140e10")
        else:
            lz.pintar(lz.elipse(ox, oy, 2.6, 3.0), "#140e10")
            lz.pintar(lz.circulo(ox - 1, oy - 1.2, 0.9), "#ffffff")
        lz.pintar(lz.trazo([(ox - 3, oy + 4.5), (ox + 3, oy + 4.5)], 0.5), "#8a5a50", 0.4)   # (las ojeras, ya flojas)
    if f in (2, 3):
        lz.pintar(lz.elipse(cx, cy + 15, 2.6, 1.6), "#3a1a1a")
    lz.sombrear(lz.circulo(cx + 13, cy - 9, 3), CORAL[2:], 1.5, LUZ)        # una flor en la oreja
    if f == 3:
        tetera(lz, brazos[1][-1][0] + 4, brazos[1][-1][1] + sube - 4, 7)     # la tetera, en alto
    return lz.sprite(contorno=CONTORNO)


def icono(cual):
    lz = Lienzo(16, 16, s=8, semilla=900 + cual)
    if cual == 0:                                                            # reloj de bolsillo
        lz.pintar(lz.trazo([(8, 1), (8, 3)], 0.8), LATON[2])
        lz.sombrear(lz.circulo(8, 9.5, 6), LATON, 2, LUZ)
        lz.pintar(lz.circulo(8, 9.5, 4.4), ARENA[5])
        lz.pintar(lz.trazo([(8, 9.5), (8, 6.5)], 0.5) + lz.trazo([(8, 9.5), (10.5, 10.5)], 0.5), MADERA[0])
    elif cual == 1:                                                          # lente de prisma
        lz.sombrear(np.clip(lz.circulo(8, 8, 6.5) - lz.circulo(8, 8, 4.8), 0, 1), LATON, 1.5, LUZ)
        lz.sombrear(lz.circulo(8, 8, 4.8), CRISTAL[1:], 2, LUZ)
        lz.sombrear(lz.poligono([(8, 5), (10.5, 8), (8, 11), (5.5, 8)]), VIOLETA[2:], 1, LUZ)
    elif cual == 2:                                                          # botas de arena firme
        for x in (3, 9):
            bota = lz.poligono([(x, 3), (x + 4, 3), (x + 4.5, 12), (x + 6, 12.5), (x + 6, 14.5), (x - 0.5, 14.5)])
            lz.sombrear(bota, ARENA[:5], 2, LUZ)
            lz.pintar(lz.trazo([(x - 0.5, 14), (x + 6, 14)], 0.6), MADERA[1])
            lz.pintar(lz.trazo([(x, 5), (x + 4, 5)], 0.4), CORAL[2])
    else:                                                                    # Capa del Farolillero
        capa = lz.poligono([(5, 2), (11, 2), (14, 14), (2, 14)])
        lz.sombrear(capa, NOCHE, 3, LUZ)
        lz.pintar(lz.trazo([(2.5, 13.6), (13.5, 13.6)], 0.6) + lz.trazo([(5, 2.4), (11, 2.4)], 0.6), LATON[4])
        lz.sombrear(lz.elipse(11, 10, 1.8, 2.4), AMBAR[2:], 1, LUZ)
        lz.sumar_luz(lz.desenfocar(lz.circulo(11, 10, 1.5), 2), AMBAR[3], 0.8)
    return lz.sprite(contorno=0.3)


def main():
    out = (np.clip(fondo(), 0, 1) * 255).round().astype(np.uint8)
    guardar_png_ligero(os.path.join(SALIDA, "tienda_kikombe_fondo.png"), out)
    hoja = np.concatenate([kikombe(f) for f in range(4)], axis=1)
    Image.fromarray(hoja, "RGBA").save(os.path.join(SALIDA, "tienda_kikombe.png"))
    # los iconos, en los huecos 28-31 de objetos.png (sin tocar los demás)
    ruta = os.path.join(SALIDA, "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    n = max(32, viejos.width // 16)
    iconos = Image.new("RGBA", (16 * n, 16), (0, 0, 0, 0))
    iconos.alpha_composite(viejos, (0, 0))
    for k in range(4):
        iconos.paste(Image.new("RGBA", (16, 16), (0, 0, 0, 0)), (16 * (28 + k), 0))
        iconos.alpha_composite(Image.fromarray(icono(k), "RGBA"), (16 * (28 + k), 0))
    iconos.save(ruta)
    print("Tienda de Kikombe en", SALIDA)


if __name__ == "__main__":
    main()
