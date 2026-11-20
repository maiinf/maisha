"""JIONI, LA CIUDAD DE LOS FAROLES (el Valle del Ocaso), pintada con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_jioni.py

Genera en arte/mundos/ocaso/jioni/:
  casa.png      2 × 72×76  una casa de arenisca de los fénec: tejado de tejas corales en dos aguas, alero de madera,
                           puerta redonda y una ventana. 0 con las cortinas echadas (dentro, alguien que no duerme
                           intenta hacerse de noche) · 1 con las cortinas abiertas y una lucecita (ya descansa)
  puesto.png    2 × 60×52  un puesto del Mercado del Crepúsculo: toldo a rayas, mostrador y tarros. 0 cerrado (la
                           lona echada) · 1 abierto
  torre.png     96×168     LA TORRE DEL RELOJ DE ARENA: una torre de arenisca con un gran reloj de arena de latón en
                           la cara y, arriba, tres argollas de las que salen las cadenas que atan el sol
  poste.png     2 × 20×44  un poste de la Plaza de los Doce Faroles: 0 vacío (el gancho) · 1 con su farol encendido
  horizonte.png 80×84      LA PUERTA DEL HORIZONTE: dos hojas de bronce bajo un arco violeta, con tres huecos
                           redondos (los tres pesos del reloj); atrás asoma el morado de Giza
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_mirador import LUZ, ARENISCA, BRONCE, SOMBRA, AMBAR  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "ocaso", "jioni")
TEJA = ["#3a1218", "#6a2228", "#9a3a36", "#c45a48", "#e48a66", "#f8b48a"]
MADERA = ["#1e1210", "#3a2418", "#5a3a24", "#7a5634", "#9a7446"]
CORTINA = ["#1e0e2a", "#3a1a4e", "#5a2c72", "#7e4896", "#a46cba"]
LONA = ["#2a2a3e", "#4a4a66", "#6e6e8e", "#9696b2"]


def casa(f):
    W, H = 72, 76
    lz = Lienzo(W, H, s=4, semilla=13000 + f)
    muro = lz.poligono([(8, 75), (64, 75), (64, 34), (8, 34)])
    lz.sombrear(muro, ARENISCA[1:], 8.0, LUZ, textura=lz.ruido(1.8, 3, semilla=13001), fuerza_tex=0.3)
    for y in (44, 54, 64):                                                   # las hiladas
        lz.pintar(lz.trazo([(8, y), (64, y)], 0.35) * muro, ARENISCA[1], 0.5)
    lz.pintar(muro * (lz.x > 52), ARENISCA[1], 0.3)
    # la puerta redonda, de madera
    puerta = np.clip(lz.poligono([(28, 75), (44, 75), (44, 60), (28, 60)]) + lz.elipse(36, 60, 8, 7) * (lz.y <= 60), 0, 1)
    lz.sombrear(puerta, MADERA, 4.0, LUZ)
    for x in (32, 36, 40):
        lz.pintar(lz.trazo([(x, 54), (x, 75)], 0.35) * puerta, MADERA[0], 0.7)
    lz.pintar(lz.circulo(41, 67, 1.1), BRONCE[4])
    # la ventana: cortinas echadas (0) o abiertas con una lucecita (1)
    ventana = lz.elipse(53, 47, 6, 6)
    lz.sombrear(np.clip(lz.elipse(53, 47, 7.5, 7.5) - ventana, 0, 1), MADERA[1:], 2.0, LUZ)
    if f == 0:
        lz.sombrear(ventana, CORTINA, 3.0, LUZ)
        for x in (50, 53, 56):
            lz.pintar(lz.trazo([(x, 41), (x, 53)], 0.35) * ventana, CORTINA[0], 0.7)
    else:
        lz.pintar(ventana, "#3a1a10")
        lz.pintar(ventana, AMBAR[2], 0.6)
        lz.sumar_luz(lz.desenfocar(ventana, 3), AMBAR[3], 0.7)
        for lado in (-1, 1):                                                 # las cortinas recogidas a los lados
            lz.sombrear(lz.elipse(53 + lado * 5, 47, 2, 6) * lz.elipse(53, 47, 7, 7), CORTINA, 1.5, LUZ)
    # el tejado en dos aguas, de tejas corales, con su alero de madera
    tejado = lz.poligono([(2, 36), (70, 36), (60, 12), (12, 12)])
    filas = (np.sin(lz.y * 1.4) * 0.5 + 0.5)
    lz.sombrear(tejado, TEJA[1:], 6.0, LUZ, textura=filas, fuerza_tex=0.25)
    lz.pintar(tejado * ((lz.y % 4.5) < 0.6), TEJA[0], 0.6)
    lz.pintar(tejado * (((lz.x + np.floor(lz.y / 4.5) * 3) % 6) < 0.5), TEJA[1], 0.5)
    alero = lz.poligono([(1, 35), (71, 35), (71, 38), (1, 38)])
    lz.sombrear(alero, MADERA[1:], 1.5, LUZ)
    cumbre = lz.poligono([(12, 12), (60, 12), (58, 9), (14, 9)])
    lz.sombrear(cumbre, TEJA[:5], 1.5, LUZ)
    # una chimenea pequeña y un farolillo apagado junto a la puerta
    chim = lz.poligono([(48, 14), (54, 14), (54, 2), (48, 2)])
    lz.sombrear(chim, ARENISCA[1:], 2.0, LUZ)
    lz.pintar(lz.trazo([(20, 52), (20, 58)], 0.5), MADERA[1])
    lz.sombrear(lz.poligono([(18, 58), (22, 58), (22.5, 64), (17.5, 64)]), BRONCE, 1.2, LUZ)
    return lz.sprite(contorno=0.4)


def puesto(f):
    W, H = 60, 52
    lz = Lienzo(W, H, s=4, semilla=13020 + f)
    for x in (6, 54):                                                        # los postes
        lz.sombrear(lz.poligono([(x - 1.5, 51), (x + 1.5, 51), (x + 1.5, 12), (x - 1.5, 12)]), MADERA[1:], 1.0, LUZ)
    mostrador = lz.poligono([(4, 51), (56, 51), (56, 34), (4, 34)])
    lz.sombrear(mostrador, MADERA, 5.0, LUZ, textura=((lz.x % 7) < 0.6) * 1.0, fuerza_tex=-0.3)
    lz.sombrear(lz.poligono([(2, 34), (58, 34), (58, 31), (2, 31)]), MADERA[1:], 1.0, LUZ)
    if f == 1:
        for k, x in enumerate((12, 21, 30, 39, 48)):                         # los tarros de especias y aceite
            col = [AMBAR, TEJA[1:], CORTINA, AMBAR, TEJA[1:]][k]
            tarro = lz.elipse(x, 27, 3.4, 4.2)
            lz.sombrear(tarro, col, 2.0, LUZ)
            lz.pintar(lz.trazo([(x - 2, 22.5), (x + 2, 22.5)], 0.6), MADERA[2])
    # el toldo a rayas coral y crema
    toldo = lz.poligono([(0, 16), (60, 16), (54, 4), (6, 4)])
    rayas = ((lz.x // 6) % 2) * 1.0
    lz.sombrear(toldo, TEJA[2:], 4.0, LUZ)
    lz.pintar(toldo * rayas, "#f4dcb4", 0.85)
    lz.pintar(lz.poligono([(0, 16), (60, 16), (60, 19), (0, 19)]) * (np.sin(lz.x * 1.05) > -0.2), TEJA[2])
    if f == 0:                                                               # la lona echada
        lona = lz.poligono([(5, 19), (55, 19), (56, 46), (4, 46)])
        lz.sombrear(lona, LONA, 5.0, LUZ)
        for x in (15, 30, 45):
            lz.pintar(lz.trazo([(x, 20), (x + 1, 46)], 0.4) * lona, LONA[0], 0.6)
    return lz.sprite(contorno=0.4)


def torre():
    W, H = 96, 168
    lz = Lienzo(W, H, s=3, semilla=13040)
    cuerpo = lz.poligono([(14, 167), (82, 167), (76, 40), (20, 40)])
    lz.sombrear(cuerpo, ARENISCA[1:], 12.0, LUZ, textura=lz.ruido(2.0, 3, semilla=13041), fuerza_tex=0.3)
    for y in range(50, 167, 10):
        lz.pintar(lz.trazo([(14, y), (82, y)], 0.35) * cuerpo, ARENISCA[1], 0.5)
    lz.pintar(cuerpo * (lz.x > 62), ARENISCA[1], 0.3)
    # la puerta y dos ventanas estrechas
    puerta = np.clip(lz.poligono([(38, 167), (58, 167), (58, 146), (38, 146)]) + lz.elipse(48, 146, 10, 9) * (lz.y <= 146), 0, 1)
    lz.sombrear(puerta, MADERA, 4.0, LUZ)
    for x in (30, 66):
        lz.pintar(np.clip(lz.poligono([(x - 2, 128), (x + 2, 128), (x + 2, 116), (x - 2, 116)]) + lz.elipse(x, 116, 2, 2), 0, 1), "#2a1018")
    # EL RELOJ DE ARENA: un gran marco de latón con dos ampollas, la arena casi toda arriba (el tiempo, parado)
    marco = np.clip(lz.poligono([(30, 58), (66, 58), (66, 62), (30, 62)]) + lz.poligono([(30, 102), (66, 102), (66, 106), (30, 106)])
                    + lz.poligono([(31, 62), (34, 62), (34, 102), (31, 102)]) + lz.poligono([(62, 62), (65, 62), (65, 102), (62, 102)]), 0, 1)
    vidrio = np.clip(lz.poligono([(36, 63), (60, 63), (49, 82), (47, 82)]) + lz.poligono([(47, 82), (49, 82), (60, 101), (36, 101)]), 0, 1)
    lz.pintar(vidrio, "#3a2030")
    lz.pintar(vidrio, "#f8e0c8", 0.25)
    arena = vidrio * (((lz.y > 66) & (lz.y < 82)) | (lz.y > 98))
    lz.sombrear(arena, ["#8a5a2a", "#c08a48", "#e8b870", "#f8d8a0"], 3.0, LUZ)
    lz.pintar(lz.trazo([(48, 82), (48, 98)], 0.3), "#f8d8a0", 0.6)
    lz.pintar(vidrio * (lz.x < 42) * (lz.y < 80), "#ffffff", 0.3)
    lz.sombrear(marco, BRONCE, 3.0, LUZ)
    # el remate: almenas y las tres argollas de las cadenas
    remate = lz.poligono([(16, 42), (80, 42), (80, 30), (16, 30)])
    lz.sombrear(remate, ARENISCA[2:], 4.0, LUZ)
    for x in range(18, 80, 12):
        lz.sombrear(lz.poligono([(x, 31), (x + 7, 31), (x + 7, 22), (x, 22)]), ARENISCA[2:], 2.0, LUZ)
    for k, x in enumerate((30, 48, 66)):
        argolla = np.clip(lz.circulo(x, 18, 4.5) - lz.circulo(x, 18, 2.6), 0, 1)
        lz.sombrear(argolla, BRONCE[1:], 1.5, LUZ)
        # la cadena sube hacia el sol (sale por arriba, en diagonal)
        for e in range(6):
            cy = 12 - e * 3
            cx = x + (k - 1) * 2 + e * 2.2
            eslabon = np.clip(lz.elipse(cx, cy, 1.8 if e % 2 else 1.0, 1.5) - lz.elipse(cx, cy, 0.7 if e % 2 else 0.2, 0.6), 0, 1)
            lz.sombrear(eslabon, ["#3a3a4a", "#6a6a7e", "#9a9ab0", "#cacad8"], 1.0, LUZ)
    return lz.sprite(contorno=0.35)


def poste(f):
    W, H = 20, 44
    lz = Lienzo(W, H, s=4, semilla=13060 + f)
    palo = lz.poligono([(8.5, 43), (11.5, 43), (11, 8), (9, 8)])
    lz.sombrear(palo, MADERA[1:], 1.5, LUZ)
    lz.sombrear(lz.poligono([(5, 43.5), (15, 43.5), (14, 40), (6, 40)]), ARENISCA[1:], 1.5, LUZ)
    brazo = lz.trazo([(10, 9), (15, 9), (15, 13)], 0.7)
    lz.pintar(brazo, BRONCE[2])
    lz.sombrear(lz.circulo(10, 7, 1.6), BRONCE[2:], 1.0, LUZ)
    if f == 1:
        cuerpo = lz.poligono([(12, 14), (18, 14), (18.5, 24), (11.5, 24)])
        lz.sombrear(cuerpo, BRONCE, 2.0, LUZ)
        vidrio = lz.poligono([(13, 15.5), (17, 15.5), (17.3, 22.5), (12.7, 22.5)])
        lz.sombrear(vidrio, AMBAR, 2.0, LUZ)
        lz.pintar(lz.elipse(15, 19.5, 1.0, 1.8), AMBAR[4])
        lz.sumar_luz(lz.desenfocar(vidrio, 4), AMBAR[3], 1.0)
    return lz.sprite(contorno=0.4)


def horizonte():
    W, H = 80, 84
    lz = Lienzo(W, H, s=4, semilla=13080)
    arco = np.clip(lz.poligono([(2, 83), (78, 83), (78, 34), (2, 34)]) + lz.elipse(40, 34, 38, 32) * (lz.y <= 34), 0, 1)
    hueco = np.clip(lz.poligono([(12, 83), (68, 83), (68, 36), (12, 36)]) + lz.elipse(40, 36, 28, 24) * (lz.y <= 36), 0, 1)
    piedra = np.clip(arco - hueco, 0, 1)
    lz.pintar(hueco, "#120a1e")
    velo = hueco * (np.sin(lz.y * 0.4 + lz.ruido(4, 2, semilla=13081) * 6) * 0.5 + 0.5)
    lz.pintar(velo, SOMBRA[4], 0.5)
    lz.sombrear(piedra, ["#24123a", "#3e2058", "#5a3278", "#7a4a98", "#9a6ab4"], 6.0, LUZ, textura=lz.ruido(1.6, 3, semilla=13082), fuerza_tex=0.3)
    # las dos hojas de bronce, casi cerradas
    for lado in (-1, 1):
        hoja = lz.poligono([(40 + lado * 1, 83), (40 + lado * 27, 83), (40 + lado * 27, 40), (40 + lado * 1, 30)]) * hueco
        lz.sombrear(hoja, BRONCE, 6.0, LUZ)
        for y in (50, 64, 78):
            lz.pintar(lz.trazo([(40 + lado * 3, y), (40 + lado * 25, y)], 0.5) * hoja, BRONCE[0], 0.6)
    # los tres huecos de los pesos del reloj
    for x in (26, 40, 54):
        lz.sombrear(lz.circulo(x, 58, 5.2), BRONCE[1:], 2.0, LUZ)
        lz.pintar(lz.circulo(x, 58, 3.6), "#05030a")
    return lz.sprite(contorno=0.4)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    tira("casa", casa, 2)
    tira("puesto", puesto, 2)
    Image.fromarray(torre(), "RGBA").save(os.path.join(SALIDA, "torre.png"))
    tira("poste", poste, 2)
    Image.fromarray(horizonte(), "RGBA").save(os.path.join(SALIDA, "horizonte.png"))
    print("Jioni pintada en", SALIDA)
