"""EL NÚCLEO DE LA ESTRELLA (Asterhaul), pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_nucleo.py

Genera en arte/mundos/asterhaul/nucleo/:
  corazon.png       5 × 72×72  EL CORAZÓN DEL METEORITO (jefe; los tres aros de hierro y las cadenas los dibuja el
                    juego): un núcleo poliédrico de ámbar vivo. 0 latiendo (las facetas encendidas) · 1 contraído (el
                    latido: más pequeño y más brillante) · 2 EXPUESTO (sin aros: grietas de luz blanca, una semilla
                    dorada se adivina dentro) · 3 expuesto y golpeado (blanco) · 4 CALMADO (ámbar tibio, la semilla
                    a la vista, rodeada de un brote)
  puerta_triple.png 2 × 72×84  LA PUERTA TRIPLE: tres hojas de basalto en un arco con tres ojos (uno por sello: los
                    enciende el juego). 0 cerrada · 1 abierta (las hojas recogidas, luz de ámbar dentro)
  pozo.png          64×56      EL POZO DEL NÚCLEO, abierto en la Losa de Mji-Jiwe: una escalera de caracol de basalto
                    que baja hacia la luz
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_desfiladero import LUZ, ROCA, BASALTO, AMBAR, HIERRO, BLANCO  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "asterhaul", "nucleo")
BROTE = ["#1c3a14", "#2e6a20", "#4e9a32", "#7fd04a", "#c0f08a"]


def corazon(f):
    W, H = 72, 72
    lz = Lienzo(W, H, s=5, semilla=11200 + f)
    cx, cy = 36, 36
    blanco = f == 3
    calmado = f == 4
    r = {1: 17.0}.get(f, 20.0)
    # un poliedro: un decágono irregular con facetas
    pts = []
    for k in range(10):
        a = k * np.pi / 5 + 0.15
        rr = r * (1.0 if k % 2 == 0 else 0.86)
        pts.append((cx + np.cos(a) * rr, cy + np.sin(a) * rr * 1.08))
    cuerpo = lz.poligono(pts)
    amb = (BLANCO + BLANCO[-2:]) if blanco else (["#4a1e06", "#8a3e0c", "#c06a18", "#e8963a", "#f8c068", "#fff0c0"] if calmado else AMBAR)
    lz.sombrear(cuerpo, amb, r * 0.8, LUZ)
    if not blanco:
        for k in range(10):                                            # las aristas de las facetas, hacia el centro
            lz.pintar(lz.trazo([pts[k], (cx + (pts[k][0] - cx) * 0.35, cy + (pts[k][1] - cy) * 0.35)], 0.45) * cuerpo, amb[0], 0.6)
        brillo = lz.poligono([pts[6], pts[7], (cx, cy)])
        lz.pintar(brillo, amb[5], 0.45)
    if f in (0, 1):
        lz.sumar_luz(lz.desenfocar(cuerpo, 5), AMBAR[3], 0.9 if f == 1 else 0.6)
    if f in (2, 3) and not blanco:
        grieta = cuerpo * (np.abs(lz.ruido(5, 3, semilla=11210) - 0.5) < 0.035)
        lz.pintar(grieta, "#ffffff")
        lz.sumar_luz(lz.desenfocar(grieta, 2), "#fff4c8", 0.9)
    if f in (2, 4):
        # la semilla mayor, dentro: un grano dorado con su brote
        semilla = lz.elipse(cx, cy + 3, 6, 7.5)
        lz.sombrear(semilla, ["#5a3a10", "#9a6a20", "#d8a840", "#f8d878", "#fff8d0"], 4.0, LUZ)
        lz.pintar(lz.trazo([(cx, cy - 4), (cx, cy + 9)], 0.4) * semilla, "#5a3a10", 0.6)
        if f == 4:
            for lado in (-1, 1):
                hoja = lz.elipse(cx + lado * 6, cy - 10, 5.5, 2.6, -30 * lado)
                lz.sombrear(hoja, BROTE, 2.0, LUZ)
            lz.sombrear(lz.trazo([(cx, cy - 3), (cx, cy - 9)], 1.2), BROTE[1:], 0.6, LUZ)
            lz.sumar_luz(lz.desenfocar(semilla, 6), "#fff0a0", 0.6)
    return lz.sprite(contorno=0.4)


def puerta_triple(f):
    W, H = 72, 84
    lz = Lienzo(W, H, s=4, semilla=11250 + f)
    cx = 36
    arco = lz.poligono([(2, 83), (70, 83), (70, 28), (60, 10), (36, 2), (12, 10), (2, 28)])
    hueco = lz.poligono([(12, 83), (60, 83), (60, 32), (52, 18), (36, 12), (20, 18), (12, 32)])
    marco = arco * (1 - hueco)
    lz.sombrear(marco, BASALTO[1:], 5.0, LUZ, textura=lz.ruido(1.6, 3, semilla=11251), fuerza_tex=0.3)
    lz.pintar(marco * ((lz.y % 9) < 0.9) * (lz.y >= 34), BASALTO[0], 0.7)
    # los tres engastes de los ojos (vacíos: la luz la pone el juego)
    for (x, y) in ((cx - 22, 18), (cx, 7), (cx + 22, 18)):
        lz.sombrear(lz.circulo(x, y, 4.2), HIERRO[:5], 2.0, LUZ)
        lz.pintar(lz.circulo(x, y, 2.6), "#05030a")
    if f == 0:
        hojas = hueco
        lz.sombrear(hojas, BASALTO, 12.0, LUZ, textura=((lz.x % 6) < 0.7) * 1.0, fuerza_tex=-0.25)
        for x in (cx - 8, cx + 8):
            lz.pintar(lz.trazo([(x, 16), (x, 83)], 0.7), BASALTO[0])
        # los tres sellos grabados: una onda, un imán y una horquilla
        for k, x in enumerate((cx - 16, cx, cx + 16)):
            y = 52
            if k == 0:
                g = lz.trazo([(x - 4, y), (x - 2, y - 3), (x, y), (x + 2, y + 3), (x + 4, y)], 0.7)
            elif k == 1:
                g = (np.abs(np.hypot(lz.x - x, lz.y - y + 1) - 3.6) < 0.7) * (lz.y < y) + lz.trazo([(x - 3.6, y - 1), (x - 3.6, y + 3)], 0.7) + lz.trazo([(x + 3.6, y - 1), (x + 3.6, y + 3)], 0.7)
            else:
                g = lz.trazo([(x - 3, y - 4), (x - 3, y + 1), (x, y + 3), (x + 3, y + 1), (x + 3, y - 4)], 0.7)
            lz.pintar(np.clip(g, 0, 1) * hojas, AMBAR[2], 0.9)
    else:
        lz.pintar(hueco, "#2a1206")
        lz.pintar(hueco, AMBAR[3], 0.5)
        lz.pintar(hueco * (lz.y > 60), AMBAR[4], 0.3)
        lz.sumar_luz(lz.desenfocar(hueco, 5), AMBAR[3], 0.6)
        for lado in (-1, 1):
            hoja = lz.poligono([(cx + lado * 24, 83), (cx + lado * 18, 80), (cx + lado * 18, 30), (cx + lado * 24, 33)])
            lz.sombrear(hoja * hueco, BASALTO, 3.0, LUZ)
    return lz.sprite(contorno=0.4)


def pozo():
    W, H = 64, 56
    lz = Lienzo(W, H, s=4, semilla=11280)
    cx, cy = 32, 26
    boca = lz.elipse(cx, cy, 28, 20)
    lz.pintar(boca, "#05030a")
    # los peldaños: un caracol de cuñas que baja y se estrecha hacia el centro
    for k in range(14):
        a0 = k * 0.62 - 1.2
        rr = 26 - k * 1.5
        a1 = a0 + 0.55
        p = [(cx + np.cos(a0) * rr, cy + np.sin(a0) * rr * 0.7), (cx + np.cos(a1) * rr, cy + np.sin(a1) * rr * 0.7),
             (cx + np.cos(a1) * (rr - 8), cy + np.sin(a1) * (rr - 8) * 0.7 + k * 0.6), (cx + np.cos(a0) * (rr - 8), cy + np.sin(a0) * (rr - 8) * 0.7 + k * 0.6)]
        pel = lz.poligono(p) * boca
        osc = k / 14.0
        lz.sombrear(pel, BASALTO[:5] if osc > 0.5 else BASALTO[1:], 2.0, LUZ)
        lz.pintar(pel, "#05030a", osc * 0.6)
        lz.pintar(lz.trazo([p[0], p[1]], 0.5) * boca, AMBAR[2], 0.55 * (1 - osc))
    fondo = lz.elipse(cx, cy + 4, 7, 5)
    lz.pintar(fondo, AMBAR[3])
    lz.sumar_luz(lz.desenfocar(fondo, 6), AMBAR[3], 0.8)
    borde = np.clip(lz.elipse(cx, cy, 31, 23) - boca, 0, 1)
    lz.sombrear(borde, BASALTO[2:], 2.4, LUZ)
    lz.pintar(borde * (np.abs(((np.arctan2(lz.y - cy, lz.x - cx) * 6 / np.pi) % 1) - 0.5) < 0.05), BASALTO[0], 0.8)
    return lz.sprite(contorno=0.3)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    tira("corazon", corazon, 5)
    tira("puerta_triple", puerta_triple, 2)
    Image.fromarray(pozo(), "RGBA").save(os.path.join(SALIDA, "pozo.png"))
    print("Núcleo pintado en", SALIDA)
