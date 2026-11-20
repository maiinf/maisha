"""LAS DUNAS DE PENUMBRA (el Valle del Ocaso, el camino del oeste), pintadas con detalle.

    python3 herramientas/pintar_dunas.py

Genera en arte/mundos/ocaso/dunas/:
  vela.png      2 × 36×60  UNA VELA DE SOMBRA: un mástil de madera clavado en una peana de roca con una vela de tela
                           oscura y tensa. 0 de cara (la tela ancha: echa sombra larga si el sol le da de frente)
                           · 1 de canto (girada un cuarto: solo se ve el filo)
  enterrado.png 28×22      un espejo de bronce enterrado en la arena: solo asoma el borde (la Carga lo saca)
  peso.png      16×22      LA PESA DEL OESTE: una pesa de reloj de bronce con un sol grabado
  kivuli.png    6 × 84×64  KIVULI, EL ALACRÁN DE RELOJ DE ARENA (jefe): obsidiana, pinzas enormes y en el vientre un
                           reloj de arena dorado. 0 enterrado (un montículo que avanza) · 1 acecha (pinzas abiertas)
                           · 2 ataca (la cola en alto, el aguijón brillando) · 3 VOLCADO (panza arriba: el reloj al
                           aire) · 4 volcado y golpeado (blanco) · 5 vencido (gris, la arena del reloj cayendo)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_mirador import LUZ, ARENISCA, BRONCE, SOMBRA, AMBAR, BLANCO  # noqa: E402
from pintar_jioni import MADERA  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "ocaso", "dunas")
TELA = ["#100818", "#1e1030", "#2e1a46", "#40265c", "#583674"]
OBSIDIANA = ["#06040c", "#120c1e", "#22183a", "#34265a", "#4c3a7c", "#7a64a8"]
ARENA = ["#5a3a5e", "#7a527a", "#a07a98", "#c8a4b8"]
GRIS = ["#3a3640", "#5a5662", "#7e7a86", "#a29ea8", "#c6c2ca"]


def vela(f):
    W, H = 36, 60
    lz = Lienzo(W, H, s=4, semilla=14000 + f)
    peana = lz.poligono([(8, 59), (28, 59), (26, 52), (10, 52)])
    lz.sombrear(peana, ARENISCA[1:], 3.0, LUZ)
    mastil = lz.poligono([(16.8, 53), (19.2, 53), (19, 4), (17, 4)])
    lz.sombrear(mastil, MADERA[1:], 1.4, LUZ)
    lz.sombrear(lz.circulo(18, 4, 2), BRONCE[2:], 1.0, LUZ)
    if f == 0:
        tela = lz.poligono([(19, 8), (33, 12), (31, 44), (19, 46)])
        lz.sombrear(tela, TELA, 6.0, LUZ, textura=lz.ruido(2.0, 2, semilla=14001), fuerza_tex=0.2)
        lz.pintar(lz.trazo([(19, 8), (33, 12), (31, 44), (19, 46)], 0.5), BRONCE[2], 0.7)   # la relinga
        for y in (20, 32):
            lz.pintar(lz.trazo([(19, y), (32, y + 2)], 0.4) * tela, TELA[3], 0.7)
        verga = lz.trazo([(17, 8), (34, 12)], 0.8)
        lz.pintar(verga, MADERA[2])
    else:
        tela = lz.poligono([(19, 8), (22, 9), (22, 45), (19, 46)])
        lz.sombrear(tela, TELA, 1.5, LUZ)
        lz.pintar(lz.trazo([(16, 8), (23, 9)], 0.8), MADERA[2])
    return lz.sprite(contorno=0.4)


def enterrado():
    W, H = 28, 22
    lz = Lienzo(W, H, s=4, semilla=14020)
    monton = lz.elipse(14, 15, 13, 6)
    lz.sombrear(monton, ARENA, 4.0, LUZ, textura=lz.ruido(1.2, 2, semilla=14021), fuerza_tex=0.2)
    borde = np.clip(lz.elipse(14, 11, 8, 6) - lz.elipse(14, 11, 6.2, 4.6), 0, 1) * (lz.y < 13)
    lz.sombrear(borde, BRONCE, 2.0, LUZ)
    lz.pintar(lz.elipse(14, 11, 6.2, 4.6) * (lz.y < 13), "#6a4a5a")
    lz.pintar(lz.elipse(12, 9, 2, 1.2), "#c8a890", 0.7)
    return lz.sprite(contorno=0.4)


def peso():
    W, H = 16, 22
    lz = Lienzo(W, H, s=5, semilla=14030)
    gancho = np.clip(lz.circulo(8, 3.5, 2.6) - lz.circulo(8, 3.5, 1.4), 0, 1)
    lz.sombrear(gancho, BRONCE[1:], 1.0, LUZ)
    cuerpo = lz.poligono([(4, 6), (12, 6), (14, 20), (2, 20)])
    lz.sombrear(cuerpo, BRONCE, 4.0, LUZ)
    lz.pintar(lz.trazo([(3, 9), (13, 9)], 0.4), BRONCE[1], 0.8)
    sol = lz.circulo(8, 14, 2.4)
    lz.pintar(sol, AMBAR[3])
    for k in range(8):
        a = k * np.pi / 4
        lz.pintar(lz.trazo([(8 + np.cos(a) * 3, 14 + np.sin(a) * 3), (8 + np.cos(a) * 4.4, 14 + np.sin(a) * 4.4)], 0.35), AMBAR[2])
    lz.sumar_luz(lz.desenfocar(sol, 2), AMBAR[3], 0.6)
    return lz.sprite(contorno=0.4)


def kivuli(f):
    W, H = 84, 64
    lz = Lienzo(W, H, s=3, semilla=14040 + f)
    cx, cy = 42, 40
    if f == 0:
        monton = lz.elipse(cx, cy + 12, 26, 9)
        lz.sombrear(monton, ARENA, 6.0, LUZ, textura=lz.ruido(1.5, 3, semilla=14041), fuerza_tex=0.25)
        for k in range(5):                                                   # la arena que se aparta
            lz.pintar(lz.trazo([(cx - 24 + k * 12, cy + 6), (cx - 26 + k * 12, cy + 2)], 0.6), ARENA[3], 0.7)
        lz.pintar(lz.circulo(cx + 6, cy + 8, 1.6), "#ffd8ff")                # un ojo que asoma
        lz.pintar(lz.circulo(cx + 11, cy + 8, 1.6), "#ffd8ff")
        return lz.sprite(contorno=0.4)
    vencido = f == 5
    rampa = GRIS if vencido else (BLANCO if f == 4 else OBSIDIANA)
    if f in (3, 4, 5):
        # VOLCADO: panza arriba, las patas al aire y el reloj de arena dorado del vientre a la vista
        cuerpo = lz.elipse(cx, cy, 24, 14)
        lz.sombrear(cuerpo, rampa, 8.0, LUZ)
        for lado in (-1, 1):
            for k in range(4):
                x0 = cx + lado * (10 + k * 4)
                lz.pintar(lz.trazo([(x0, cy - 8), (x0 + lado * 6, cy - 18 - (k % 2) * 3), (x0 + lado * 10, cy - 14)], 1.0), rampa[1])
            pinza = lz.elipse(cx + lado * 30, cy + 6, 8, 5, 30 * lado)
            lz.sombrear(pinza, rampa, 3.0, LUZ)
        marco = np.clip(lz.poligono([(cx - 9, cy - 9), (cx + 9, cy - 9), (cx + 9, cy - 7), (cx - 9, cy - 7)])
                        + lz.poligono([(cx - 9, cy + 7), (cx + 9, cy + 7), (cx + 9, cy + 9), (cx - 9, cy + 9)]), 0, 1)
        vidrio = np.clip(lz.poligono([(cx - 7, cy - 7), (cx + 7, cy - 7), (cx + 1, cy), (cx - 1, cy)])
                         + lz.poligono([(cx - 1, cy), (cx + 1, cy), (cx + 7, cy + 7), (cx - 7, cy + 7)]), 0, 1)
        lz.pintar(vidrio, "#2a1830")
        arena = vidrio * ((lz.y < cy - 1) if not vencido else (lz.y > cy + 3))
        lz.sombrear(arena, ["#8a5a2a", "#c08a48", "#e8b870", "#f8d8a0"] if f != 4 else BLANCO, 2.0, LUZ)
        lz.sombrear(marco, BRONCE if not vencido else GRIS, 1.5, LUZ)
        if f == 3:
            lz.sumar_luz(lz.desenfocar(vidrio, 4), AMBAR[3], 0.7)
        cola = lz.curva((cx, cy + 12), (cx + 6, cy + 22), (cx + 20, cy + 22), (cx + 28, cy + 16))
        lz.pintar(lz.trazo(cola, 3.0, 1.5), rampa[2])
        return lz.sprite(contorno=0.4)
    # DE PIE (1 acecha · 2 ataca)
    for lado in (-1, 1):
        for k in range(4):                                                   # las patas
            x0 = cx + lado * (8 + k * 4)
            lz.pintar(lz.trazo([(x0, cy + 2), (x0 + lado * 8, cy + 8 + (k % 2) * 2), (x0 + lado * 11, cy + 16)], 1.1), rampa[1])
        brazo = lz.trazo([(cx + lado * 12, cy - 4), (cx + lado * 22, cy - 10), (cx + lado * 28, cy - 16)], 2.0)
        lz.pintar(brazo, rampa[2])
        abre = 0.35 if f == 1 else 0.15
        for s in (-1, 1):                                                    # la pinza, abierta
            dedo = lz.elipse(cx + lado * 31 + s * 3, cy - 20 + s * 2, 7, 3.2, (-40 + s * 40 * abre * 2) * lado)
            lz.sombrear(dedo, rampa, 2.5, LUZ)
    cuerpo = lz.elipse(cx, cy, 16, 11)
    lz.sombrear(cuerpo, rampa, 6.0, LUZ, textura=((lz.y % 5) < 0.7) * 1.0, fuerza_tex=-0.25)
    cabeza = lz.elipse(cx, cy - 9, 9, 6)
    lz.sombrear(cabeza, rampa, 3.5, LUZ)
    for lado in (-1, 1):
        lz.pintar(lz.circulo(cx + lado * 3.5, cy - 11, 1.6), "#ffd8ff")
    lz.sumar_luz(lz.desenfocar(lz.circulo(cx, cy - 11, 4), 3), "#b070e0", 0.5)
    # la cola de segmentos, curvada por encima: en el ataque, en alto y con el aguijón brillando
    alto = 26 if f == 2 else 18
    pts = [(cx, cy + 9), (cx + 8, cy + 14), (cx + 16, cy + 4), (cx + 14, cy - alto), (cx + 4, cy - alto - 6)]
    for i in range(len(pts) - 1):
        lz.sombrear(lz.trazo([pts[i], pts[i + 1]], 3.4 - i * 0.4), rampa, 2.0, LUZ)
    agu = lz.poligono([(cx + 4, cy - alto - 10), (cx + 8, cy - alto - 4), (cx, cy - alto - 4)])
    lz.sombrear(agu, AMBAR if f == 2 else rampa, 1.5, LUZ)
    if f == 2:
        lz.sumar_luz(lz.desenfocar(agu, 4), AMBAR[3], 0.9)
    return lz.sprite(contorno=0.4)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    tira("vela", vela, 2)
    Image.fromarray(enterrado(), "RGBA").save(os.path.join(SALIDA, "enterrado.png"))
    Image.fromarray(peso(), "RGBA").save(os.path.join(SALIDA, "peso.png"))
    tira("kivuli", kivuli, 6)
    print("Dunas pintadas en", SALIDA)
