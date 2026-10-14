"""KUVU, LA SETA QUE MANDA (el jefe de la cueva de las setas) y NUNGU, el erizo científico.

    python3 herramientas/dibujar_kuvu.py

Genera en arte/zonas/raiz/:
  kuvu.png    7 × 80×80  0-1 quieto (el sombrero cerrado, respira; los hilos de esporas cuelgan) · 2 lanza esporas
                         (el sombrero se hincha y suelta una nube) · 3 el SOMBRERO LEVANTADO (las láminas al aire,
                         brillando: ahí se le puede dar) · 4 golpeado · 5 tira del hilo (se inclina) · 6 marchito
  nungu.png  10 × 32×36  0-1 controlado, andando como una marioneta (brazos arriba, ojos violetas, el hilo en la
                         cabeza) · 2-3 bola de púas rodando (controlado, gris) · 4 mareado (sentado, con estrellitas)
                         · 5-6 libre (gafas, bata, la libreta) · 7-8 bola de púas libre (parda) · 9 libre, saludando
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_pasarelas import CONTORNO, GIZA  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "zonas", "raiz")
LUZ = (-0.6, -0.7, 0.5)
SOMBRERO = ["#24102e", "#3d1c50", "#5a2c74", "#7c4098", "#9c5ab6", "#c088d4"]
PIE = ["#3a3040", "#5a4c60", "#7e6e82", "#a898a8", "#cfc2cc"]
GRIS = ["#2a2830", "#46444e", "#66646e", "#8a8892", "#b0aeb6"]


def kuvu(f):
    W, H = 80, 80
    lz = Lienzo(W, H, s=5, semilla=801 + f)
    cx = 40
    marchito = f == 6
    respira = 0.8 if f == 1 else 0.0
    levanta = 9.0 if f in (3, 4) else (3.0 if f == 2 else 0.0)
    inclina = -4.0 if f == 5 else 0.0
    rng = np.random.default_rng(3)
    # hifas por el suelo
    for k in range(10):
        a = k / 10 * 2 * np.pi
        p0 = (cx + np.cos(a) * 7, 72 + np.sin(a) * 1.5)
        p1 = (cx + np.cos(a) * 30, 72 + np.sin(a) * 6 + rng.uniform(-1, 1))
        lz.pintar(lz.trazo(lz.curva(p0, ((p0[0] + p1[0]) / 2, p0[1] + 3), p1, n=12), 1.0, 0.3), "#7a6898" if marchito else "#9a7cc0", 0.8)
    # el pie
    base_som = 34 - levanta - respira
    pie = lz.poligono([(cx - 8, 73), (cx - 7 + inclina * 0.3, 46), (cx - 6 + inclina * 0.7, base_som),
                       (cx + 6 + inclina * 0.7, base_som), (cx + 7 + inclina * 0.3, 46), (cx + 9, 73)])
    lz.sombrear(pie, GRIS if marchito else PIE, 4, LUZ, textura=lz.ruido(0.6, 2, semilla=802), fuerza_tex=0.35)
    vena = [(cx - 2, 50), (cx + 1, 57), (cx - 1, 65)]
    if not marchito:
        lz.pintar(lz.trazo(vena, 0.7), GIZA[3])
        lz.brillo(lz.trazo(vena, 0.7), GIZA[3], 2, 0.5)
    anillo = lz.elipse(cx + inclina * 0.6, base_som + 8, 10, 2.8)
    lz.sombrear(anillo, ["#5a4c60", "#a898a8", "#e2d6dc"], 1.5, LUZ)
    # la cara, en el pie
    fy = 52 - levanta * 0.3
    for lado in (-1, 1):
        ox = cx + lado * 3 + inclina * 0.4
        lz.pintar(lz.elipse(ox, fy, 1.8, 2.4), "#120a18")
        if marchito:
            lz.pintar(lz.trazo([(ox - 1.2, fy), (ox + 1.2, fy)], 0.4), "#46444e")
        elif f == 4:
            lz.pintar(lz.trazo([(ox - 1.2, fy - 1.2), (ox + 1.2, fy + 1.2)], 0.45) + lz.trazo([(ox - 1.2, fy + 1.2), (ox + 1.2, fy - 1.2)], 0.45), GIZA[3])
        else:
            lz.pintar(lz.elipse(ox, fy, 1.2, 1.7), GIZA[3])
            lz.brillo(lz.elipse(ox, fy, 1.2, 1.7), GIZA[3], 1.5, 0.9)
    boca = lz.elipse(cx + inclina * 0.4, fy + 7, 2.6 if f in (2, 4) else 2.0, 1.4 if f in (2, 4) else 0.8)
    lz.pintar(boca, "#1a0e22")
    # el sombrero (y, levantado, las láminas que brillan debajo)
    sy = base_som + 1
    if marchito:
        som = lz.poligono([(cx - 26, sy + 14), (cx - 20, sy + 2), (cx, sy - 4), (cx + 20, sy + 2), (cx + 26, sy + 16), (cx, sy + 8)])
        lz.sombrear(som, GRIS, 6, LUZ, textura=lz.ruido(0.4, 2, semilla=803), fuerza_tex=0.4)
        for k in range(6):
            lz.pintar(lz.trazo([(cx - 18 + k * 7, sy + 2), (cx - 19 + k * 7, sy + 12)], 0.4), GRIS[0], 0.7)
        return lz.sprite(contorno=CONTORNO)
    laminas = lz.elipse(cx + inclina, sy, 27, 5 + levanta * 0.4)
    lz.pintar(laminas, "#2a1838")
    for k in range(-12, 13):
        lz.pintar(lz.trazo([(cx + inclina, sy - 1), (cx + inclina + k * 2.2, sy + 3 + levanta * 0.3)], 0.35) * laminas, GIZA[3], 0.8)
    lz.brillo(laminas, GIZA[3], 4 + levanta * 0.4, 0.5 + (0.4 if levanta > 5 else 0))
    top = sy - 2 - levanta * 0.4
    som = lz.poligono([(cx - 29 + inclina, sy), (cx - 24 + inclina, top - 11), (cx - 13 + inclina, top - 20), (cx + inclina, top - 23),
                       (cx + 13 + inclina, top - 20), (cx + 24 + inclina, top - 11), (cx + 29 + inclina, sy), (cx + inclina, sy + 2 - levanta * 0.5)])
    if f == 2:                                                       # se hincha
        som = np.maximum(som, lz.elipse(cx, top - 12, 30, 15))
    lz.sombrear(som, SOMBRERO, 8, LUZ, textura=lz.ruido(0.4, 2, semilla=803), fuerza_tex=0.3)
    for (x, y, r) in ((-13, -9, 2.8), (4, -15, 3.4), (16, -7, 2.4), (-4, -5, 2.0), (22, -1, 1.5), (-21, -2, 1.7)):
        lz.sombrear(lz.elipse(cx + inclina + x, top + y, r, r * 0.7) * som, ["#b8a0c0", "#e2d4e6", "#fff4ff"], 1, LUZ)
    # los hilos de esporas que cuelgan
    for (x0, x1) in ((cx - 24, cx - 28), (cx + 23, cx + 29)):
        hilo = lz.trazo(lz.curva((x0 + inclina, sy), (x0 - 1, sy + 13), (x1, sy + 24), n=20), 0.4)
        lz.pintar(hilo, "#e6c8ff", 0.9)
        lz.brillo(hilo, GIZA[3], 1.5, 0.6)
    # esporas
    n = 30 if f == 2 else 10
    for k in range(n):
        x, y = rng.uniform(8, 72), rng.uniform(2, sy)
        lz.brillo(lz.circulo(x, y, 0.6), GIZA[3], 1.2, 0.8)
        lz.pintar(lz.circulo(x, y, 0.45), "#f0e0ff")
    if f == 2:
        nube = lz.desenfocar(lz.elipse(cx, top - 26, 22, 8) * (lz.ruido(3, 3, semilla=805) > 0.4), 2)
        lz.sumar_luz(nube, "#a855d6", 0.6)
    return lz.sprite(contorno=CONTORNO)


def nungu(f):
    W, H = 32, 36
    lz = Lienzo(W, H, s=8, semilla=811 + f)
    cx = 16
    controlado = f in (0, 1, 2, 3)
    if f in (2, 3, 7, 8):
        # hecho una bola de púas, rodando
        PUA = (["#22202a", "#3a3846", "#56546a", "#7a788e", "#a09eb2"] if controlado
               else ["#2a2018", "#4a3a2a", "#6e5a42", "#94805e", "#bfae88"])
        cy = 26
        giro = 0.3 if f in (3, 8) else 0.0
        bola = lz.circulo(cx, cy, 8)
        lz.sombrear(bola, PUA, 3, LUZ)
        for k in range(18):
            a = k / 18 * 2 * np.pi + giro
            b = (cx + np.cos(a) * 6, cy + np.sin(a) * 6)
            p = (cx + np.cos(a) * 11.5, cy + np.sin(a) * 11.5)
            lz.sombrear(lz.trazo([b, p], 1.3, 0.2), PUA, 1, LUZ)
        lz.sombrear(lz.elipse(cx + 2 * np.cos(giro * 6), cy + 2, 2.4, 2), ["#9a7e60", "#d8c0a0", "#f0e0c8"], 1, LUZ)   # el hocico asoma
        if controlado:
            hilo = lz.trazo(lz.curva((cx, cy - 8), (cx + 1, 8), (cx + 4, 0), n=10), 0.35)
            lz.pintar(hilo, "#e6c8ff")
            lz.brillo(hilo, GIZA[3], 1.2, 0.7)
        return lz.sprite(contorno=CONTORNO)
    sentado = f == 4
    oy = 4 if sentado else 0
    PUA = ["#2a2018", "#4a3a2a", "#6e5a42", "#94805e", "#bfae88"] if not controlado else ["#22202a", "#3a3846", "#56546a", "#7a788e", "#a09eb2"]
    for k in range(13):
        a = np.pi * (0.95 + k / 12 * 1.1)
        b = (cx + np.cos(a) * 5, 12 + oy + np.sin(a) * 5)
        p = (cx + np.cos(a) * 11, 12 + oy + np.sin(a) * 9.5)
        lz.sombrear(lz.trazo([b, p], 1.3, 0.2), PUA, 1, LUZ)
    bata = lz.poligono([(cx - 6.5, 17 + oy), (cx + 6.5, 17 + oy), (cx + 8, 30 + oy * 0.5), (cx - 8, 30 + oy * 0.5)])
    lz.sombrear(bata, ["#8a8270", "#b4ac98", "#d8d0bc", "#f2ecdc"], 2, LUZ)
    lz.pintar(lz.trazo([(cx, 17 + oy), (cx, 30 + oy * 0.5)], 0.3), "#8a8270")
    lz.pintar(lz.trazo([(cx + 3, 23 + oy), (cx + 3.4, 25.5 + oy)], 0.35), "#3a5a9a")
    if controlado:
        alza = 1.5 if f == 1 else 0.0
        for lado in (-1, 1):
            lz.pintar(lz.trazo([(cx + lado * 6, 19), (cx + lado * 9, 12 - alza)], 1.1), "#8e7c64")
    elif f == 9:
        lz.pintar(lz.trazo([(cx + 6, 19), (cx + 10, 11)], 1.1), "#8e7c64")                          # saluda
        lz.sombrear(lz.poligono([(cx - 9, 20), (cx - 4, 20), (cx - 4, 26), (cx - 9, 26)]), ["#5a3a20", "#8a5a30", "#b07a42"], 1, LUZ)
    elif not sentado:
        lz.sombrear(lz.poligono([(cx - 9, 20 + (f == 6)), (cx - 4, 20 + (f == 6)), (cx - 4, 26 + (f == 6)), (cx - 9, 26 + (f == 6))]),
                    ["#5a3a20", "#8a5a30", "#b07a42"], 1, LUZ)
        lz.pintar(lz.trazo([(cx - 8, 21.5), (cx - 5, 21.5)], 0.25), "#efe0bf")
    cab = lz.elipse(cx, 11 + oy, 5.5, 5)
    lz.sombrear(cab, ["#6e5640", "#9a7e60", "#c2a682", "#e0caa6"], 2, LUZ)
    lz.sombrear(lz.elipse(cx, 14.5 + oy, 2.4, 2), ["#9a7e60", "#d8c0a0", "#f0e0c8"], 1, LUZ)
    lz.pintar(lz.circulo(cx, 15.8 + oy, 0.9), "#1a1010")
    for lado in (-1, 1):
        aro = np.clip(lz.circulo(cx + lado * 2.4, 10.5 + oy, 1.9) - lz.circulo(cx + lado * 2.4, 10.5 + oy, 1.4), 0, 1)
        lz.pintar(aro, "#c8a040")
        if controlado:
            lz.pintar(lz.circulo(cx + lado * 2.4, 10.5, 0.9), GIZA[3])
            lz.brillo(lz.circulo(cx + lado * 2.4, 10.5, 0.9), GIZA[3], 1.2, 0.9)
        elif sentado:
            ox = cx + lado * 2.4
            t = np.linspace(0, 3 * np.pi, 14)
            lz.pintar(lz.trazo([(ox + np.cos(a) * a * 0.08, 10.5 + oy + np.sin(a) * a * 0.08) for a in t], 0.25), "#1a1010")
        else:
            lz.pintar(lz.circulo(cx + lado * 2.4, 10.6, 0.6), "#1a1010")
            lz.pintar(lz.circulo(cx + lado * 2.4 - 0.4, 10.1, 0.3), "#ffffff")
    lz.pintar(lz.trazo([(cx - 0.5, 10.5 + oy), (cx + 0.5, 10.5 + oy)], 0.25), "#c8a040")
    if controlado:
        hilo = lz.trazo(lz.curva((cx, 6), (cx + 1, 2), (cx + 4, 0), n=10), 0.35)
        lz.pintar(hilo, "#e6c8ff")
        lz.brillo(hilo, GIZA[3], 1.2, 0.7)
    if sentado:
        for (x, y) in ((cx - 7, 3), (cx + 6, 2), (cx, 0.8)):
            lz.pintar(lz.trazo([(x - 1, y), (x + 1, y)], 0.3) + lz.trazo([(x, y - 1), (x, y + 1)], 0.3), "#f9d77a")
    for lado in (-1, 1):
        lz.pintar(lz.elipse(cx + lado * 3, 30.6 + oy * 0.4, 2, 1), "#4a3a2a")
    return lz.sprite(contorno=CONTORNO)


def hoja(fotos):
    h, w = fotos[0].shape[:2]
    t = np.zeros((h, w * len(fotos), 4), np.uint8)
    for i, a in enumerate(fotos):
        t[:, i * w:(i + 1) * w] = a
    return t


def main():
    Image.fromarray(hoja([kuvu(f) for f in range(7)]), "RGBA").save(os.path.join(SALIDA, "kuvu.png"))
    Image.fromarray(hoja([nungu(f) for f in range(10)]), "RGBA").save(os.path.join(SALIDA, "nungu.png"))
    print("Kuvu y Nungu pintados en", SALIDA)


if __name__ == "__main__":
    main()
