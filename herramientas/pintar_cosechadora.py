"""LA COSECHADORA OXIDADA, el jefe de Raíz, pintada POR CAPAS (con el pintor de las cinemáticas).

    python3 herramientas/pintar_cosechadora.py

Genera en arte/zonas/raiz/cosechadora/ una hoja por pieza. Todas las piezas miden 128×96 por fotograma y
están ya en su sitio (se ponen una encima de otra y encajan), mirando a la derecha (el juego las voltea):
  chasis.png      3: normal · tolva abierta (lanza tuercas) · reventado (sin chapas: se ve el hueco del corazón)
  caldera.png     3: cerrada · abierta (atascada: el fuego de dentro a la vista) · rota
  dep_techo.png   4: lleno (el fuego líquido se mueve) ×2 · agrietado · roto
  dep_frontal.png 4: lleno ×2 · agrietado · roto
  rueda_g.png     4: la rueda grande girando (8 radios) · rueda_p.png 4: la pequeña (6 radios)
  piston.png      4: la biela que empuja la rueda grande
  molinete.png    5: el molinete de cuchillas girando ×4 · enredado en brotes
  corazon.png     4: el corazón de Giza que late (se ve cuando el chasis revienta)
  enredaderas.png 1: enredaderas y flores (al vencerla)
Así la máquina se anima con detalle (ruedas, molinete y pistón de verdad) y cada parte se ve romperse.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_casa_shamba import rect  # noqa: E402

W, H = 128, 96
SUELO = 94
S = 4
LUZ = (-0.6, -0.7, 0.5)
OXIDO = ["#1f0e08", "#3a1a0e", "#5a2a14", "#7a3a1c", "#9c4f24", "#bd6a34", "#d88a4c", "#eab07a"]
CHAPA = ["#16171a", "#26272b", "#3a3c40", "#55575c", "#74767a", "#9a9c9e", "#c2c3c4"]
LATON = ["#2a1a08", "#4a3010", "#7a5418", "#a87a26", "#d0a440", "#efcf78"]
VERDE = ["#1f2d17", "#2f4422", "#3f5a2f", "#5d793e", "#7c9a4c", "#a8b866"]
GIZA = ["#2a0d3a", "#4a1a63", "#6b2a8f", "#8f3ec0", "#b56ae0", "#dcaaf2"]
FUEGO = ["#5a1a08", "#a8320c", "#e05a14", "#f99a2a", "#fde27e", "#fff8d2"]
MADERA = ["#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259"]
CONTORNO = 0.42
SALIDA = os.path.join(RAIZ, "arte", "zonas", "raiz", "cosechadora")


def nuevo(semilla):
    return Lienzo(W, H, s=S, semilla=semilla)


def remaches(lz, puntos, r=0.8):
    for (x, y) in puntos:
        lz.sombrear(lz.circulo(x, y, r), CHAPA[3:], 0.6, LUZ)


def grietas_giza(lz, lista, ancho=1.3, col=GIZA):
    for pts in lista:
        g = lz.trazo(pts, ancho, ancho * 0.5)
        lz.pintar(g, col[3])
        lz.sumar_luz(lz.desenfocar(g, 1.6), col[4], 0.55)


# ------------------------------------------------------------------ chasis
def chasis(estado):
    """estado: 0 normal · 1 tolva abierta · 2 reventado (el hueco del corazón a la vista)"""
    lz = nuevo(70 + estado)
    tex = lz.ruido(5.0, 3, semilla=71)
    lz.pintar(lz.desenfocar(lz.elipse(66, SUELO - 1, 60, 4), 0.8), "#0c0807", 0.6)
    # el cuerpo de la trilladora: chapa remachada con el techo redondeado
    cuerpo = np.maximum(rect(lz, 34, 34, 96, 84), lz.elipse(65, 35, 31, 8))
    lz.sombrear(cuerpo, OXIDO, 16, LUZ, textura=tex, fuerza_tex=0.22, recorte=("#eab07a", 0.55), recorte_dir=(-0.6, -1),
                rebote=("#3a1a0e", 0.4))
    placas = ((38, 38, 58, 56), (60, 38, 92, 56), (38, 59, 62, 80), (64, 59, 92, 80))
    for i, (x0, y0, x1, y1) in enumerate(placas):
        if estado == 2 and i in (1, 2):
            continue                                             # arrancadas por la explosión
        placa = rect(lz, x0, y0, x1, y1)
        lz.sombrear(placa, CHAPA if i % 2 == 0 else OXIDO, 4, LUZ, textura=tex, fuerza_tex=0.4)
        remaches(lz, [(x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2), ((x0 + x1) / 2, y0 + 2)])
    # chorretones de óxido
    chorro = (lz.ruido(2.4, 3, semilla=72) > 0.6) * cuerpo * np.clip((lz.y - 38) / 40, 0, 1)
    lz.pintar(chorro, OXIDO[5], 0.45)
    if estado == 2:
        # el hueco donde late el corazón: chapa retorcida, oscuridad y brillo violeta dentro
        hueco = np.maximum(lz.elipse(64, 58, 20, 15), rect(lz, 50, 46, 80, 70))
        lz.pintar(hueco, "#0c0608")
        lz.sumar_luz(lz.desenfocar(lz.elipse(64, 58, 16, 12), 4), "#8f3ec0", 0.5)
        for (a, b) in (((46, 44), (52, 50)), ((80, 46), (74, 52)), ((48, 72), (54, 66)), ((82, 70), (76, 64))):
            lz.sombrear(lz.poligono([a, b, (b[0] + 2, b[1] + 3), (a[0] + 3, a[1] + 1)]), CHAPA, 1, LUZ)
    else:
        grietas_giza(lz, [[(44, 37), (47, 45), (45, 52), (49, 60)], [(78, 60), (74, 68), (77, 76)]])
    # chimenea
    chim = np.maximum(rect(lz, 60, 6, 68, 36), lz.elipse(64, 6, 5, 2))
    lz.sombrear(chim, CHAPA, 3, LUZ, textura=tex, fuerza_tex=0.4)
    for y in (14, 24):
        lz.pintar(lz.trazo([(59.5, y), (68.5, y)], 1.2, 1.2), CHAPA[1])
    lz.pintar(lz.elipse(64, 6, 3.4, 1.2), "#0c0807")
    # tolva
    if estado == 1:
        tolva = lz.poligono([(72, 34), (76, 14), (94, 10), (92, 34)])
        lz.sombrear(tolva, CHAPA, 4, LUZ, textura=tex, fuerza_tex=0.4)
        lz.pintar(lz.elipse(85, 12, 8, 2.4), "#120708")
        for k in range(3):
            lz.sombrear(lz.circulo(81 + k * 4, 11.5, 1.6), CHAPA[2:], 1, LUZ)       # tuercas asomando
        lz.sumar_luz(lz.desenfocar(lz.elipse(85, 12, 6, 2), 2), "#f99a2a", 0.5)
    else:
        tolva = lz.poligono([(72, 34), (75, 22), (90, 22), (93, 34)])
        lz.sombrear(tolva, CHAPA, 4, LUZ, textura=tex, fuerza_tex=0.4)
        lz.pintar(lz.trazo([(75, 23), (90, 23)], 1.0, 1.0), CHAPA[1])
    # brazo del molinete y barra de cuchillas con sus dientes
    lz.sombrear(lz.trazo([(92, 44), (112, 60)], 3.2, 2.6), OXIDO, 1.5, LUZ, textura=tex, fuerza_tex=0.4)
    lz.sombrear(lz.trazo([(86, 86), (126, 89)], 3.0, 3.0), CHAPA, 1.5, LUZ)
    for k in range(11):
        x = 87 + k * 3.6
        diente = lz.poligono([(x, 88), (x + 1.8, 94), (x + 3.6, 88)])
        lz.sombrear(diente, CHAPA[3:], 0.7, LUZ)
        lz.pintar(lz.trazo([(x + 0.7, 88.5), (x + 1.7, 93)], 0.4, 0.3), CHAPA[6], 0.8)
    # los faros (ojos)
    for (fx, fy) in ((96, 42), (96, 51)):
        lz.sombrear(lz.circulo(fx, fy, 3.6), CHAPA, 1.4, LUZ)
        if estado != 2:
            lz.pintar(lz.circulo(fx + 0.4, fy, 2.6), GIZA[2])
            lz.pintar(lz.circulo(fx + 0.8, fy - 0.3, 1.5), GIZA[5])
            lz.sumar_luz(lz.desenfocar(lz.circulo(fx + 1.5, fy, 3.5), 3), GIZA[4], 0.5)
        else:
            lz.pintar(lz.circulo(fx + 0.4, fy, 2.4), "#120708")
    # el cilindro del pistón (la biela va aparte)
    cil = rect(lz, 60, 64, 76, 73)
    lz.sombrear(cil, LATON, 3, LUZ)
    remaches(lz, [(62, 66), (74, 66), (62, 71), (74, 71)], 0.6)
    return lz.sprite(contorno=CONTORNO)


# ------------------------------------------------------------------ caldera
def caldera(estado):
    """estado: 0 cerrada · 1 abierta (el fuego de dentro a la vista: ¡golpéala!) · 2 rota"""
    lz = nuevo(80 + estado)
    tex = lz.ruido(5.0, 3, semilla=81)
    cal = np.maximum(lz.elipse(22, 58, 17, 21), rect(lz, 22, 38, 40, 79))
    if estado == 2:
        # reventada: media caldera arrancada, chapa retorcida y brasas dentro
        resto = cal * (lz.x > 14 + (lz.y - 40) * 0.12) * (lz.ruido(3, 2, semilla=83) > 0.25)
        lz.sombrear(resto, OXIDO[:6], 8, LUZ, textura=tex, fuerza_tex=0.4)
        lz.pintar(np.clip(cal - resto, 0, 1) * (lz.x > 10), "#140806", 0.9)
        lz.pintar(lz.elipse(24, 60, 8, 10) * (lz.ruido(1.2, 2, semilla=84) > 0.55), FUEGO[2], 0.9)
        lz.pintar(lz.elipse(24, 62, 5, 6) * (lz.ruido(1.0, 2, semilla=85) > 0.6), FUEGO[4], 0.9)
        for (a, b) in (((8, 44), (14, 40)), ((10, 72), (16, 76)), ((30, 36), (36, 32))):
            lz.sombrear(lz.poligono([a, b, (b[0] + 1, b[1] + 3), (a[0] + 2, a[1] + 2)]), CHAPA, 1, LUZ)
        return lz.sprite(contorno=CONTORNO)
    lz.sombrear(cal, OXIDO, 12, LUZ, textura=tex, fuerza_tex=0.3, recorte=("#eab07a", 0.45), recorte_dir=(-1, -0.6))
    for y in (42, 58, 74):                                        # flejes de latón remachados
        lz.pintar(lz.trazo([(6, y), (40, y)], 1.6, 1.6) * cal, LATON[2], 0.9)
        for x in range(8, 40, 5):
            lz.pintar(lz.circulo(x, y, 0.7) * cal, LATON[5], 0.9)
    # el manómetro (reloj de presión) con la aguja en rojo
    lz.sombrear(lz.circulo(33, 46, 3.6), LATON, 1.5, LUZ)
    lz.pintar(lz.circulo(33, 46, 2.6), "#efe6cf")
    lz.pintar(lz.trazo([(33, 46), (35, 44)], 0.6, 0.5), "#b03a44")
    esc = lz.elipse(18, 58, 9, 10)
    if estado == 1:
        lz.pintar(esc, "#120708")
        lz.pintar(lz.elipse(18, 58, 7, 8), FUEGO[1])
        lz.pintar(lz.elipse(18, 59, 5.4, 6.2), FUEGO[3])
        lz.pintar(lz.elipse(18, 59, 3.4, 4.2), FUEGO[4])
        lz.pintar(lz.elipse(17.5, 58, 1.8, 2.4), GIZA[5])
        lz.sumar_luz(lz.desenfocar(lz.elipse(18, 58, 11, 12), 4), "#ffb060", 0.7)
        tapa = lz.poligono([(5, 46), (10, 42), (10, 72), (5, 68)])   # la tapa abierta hacia fuera
        lz.sombrear(tapa, CHAPA, 2, LUZ)
        remaches(lz, [(7, 50), (7, 64)], 0.6)
    else:
        lz.sombrear(esc, CHAPA, 4, LUZ, textura=tex, fuerza_tex=0.3)
        for k in range(5):
            lz.pintar(lz.trazo([(11, 52 + k * 3), (25, 52 + k * 3)], 0.8, 0.8) * esc, CHAPA[0], 0.9)
        lz.pintar(lz.elipse(18, 58, 4.4, 5) * (lz.ruido(0.5, 2, semilla=82) > 0.5), GIZA[3], 0.55)
    # la válvula de escape de arriba
    lz.sombrear(rect(lz, 18, 32, 23, 40), LATON, 1.5, LUZ)
    lz.sombrear(lz.elipse(20.5, 32, 4, 1.6), LATON, 1, LUZ)
    return lz.sprite(contorno=CONTORNO)


# ------------------------------------------------------------------ depósitos de fuego
def deposito(cual, estado):
    """cual: «techo» (cilindro tumbado sobre el lomo) o «frontal» (de pie, delante, con su boquilla).
    estado: 0-1 lleno (el fuego líquido se mueve) · 2 agrietado · 3 roto"""
    lz = nuevo(90 + estado + (10 if cual == "frontal" else 0))
    tex = lz.ruido(4.0, 3, semilla=91)
    if cual == "techo":
        cuerpo = np.maximum(rect(lz, 36, 21, 58, 33), np.maximum(lz.elipse(36, 27, 4, 6), lz.elipse(58, 27, 4, 6)))
        ventana = rect(lz, 40, 24, 54, 30)
        soporte = [rect(lz, 39, 33, 42, 37), rect(lz, 52, 33, 55, 37)]
        nivel_y = 26.0 + (1.0 if estado == 1 else 0.0)
        tubo = [(58, 30), (61, 34)]
    else:
        cuerpo = np.maximum(rect(lz, 96, 63, 108, 84), np.maximum(lz.elipse(102, 63, 6, 3), lz.elipse(102, 84, 6, 3)))
        ventana = rect(lz, 99, 67, 105, 80)
        soporte = [rect(lz, 94, 70, 97, 74)]
        nivel_y = 71.0 + (1.5 if estado == 1 else 0.0)
        tubo = [(108, 78), (116, 80)]
    for s_ in soporte:
        lz.sombrear(s_, CHAPA, 1, LUZ)
    if estado == 3:
        # reventado: chapa abierta en pétalos, ennegrecida, con brasas
        roto = cuerpo * (lz.ruido(2.2, 2, semilla=93) > 0.4)
        lz.sombrear(roto, ["#120b0a", "#2a1c18", "#3d2a22", "#55575c"], 3, LUZ)
        lz.pintar(ventana * (lz.ruido(0.8, 2, semilla=94) > 0.6), FUEGO[2], 0.9)
        lz.pintar(ventana * (lz.ruido(0.6, 2, semilla=95) > 0.75), FUEGO[4], 0.9)
        return lz.sprite(contorno=CONTORNO)
    lz.sombrear(cuerpo, LATON, 4, LUZ, textura=tex, fuerza_tex=0.25, recorte=("#fff1c8", 0.5), recorte_dir=(-0.8, -1))
    # la ventana de cristal con el fuego líquido dentro (ondulando)
    lz.pintar(ventana, "#1a0c08")
    liquido = ventana * (lz.y > nivel_y + np.sin(lz.x * 0.9 + estado * 2.0) * 0.8)
    lz.pintar(liquido, FUEGO[2])
    lz.pintar(liquido * (lz.ruido(0.8, 2, semilla=96 + estado) > 0.55), FUEGO[4], 0.9)
    lz.pintar(liquido * (lz.ruido(0.7, 2, semilla=98 + estado) > 0.8), GIZA[4], 0.9)
    lz.sumar_luz(lz.desenfocar(liquido, 2.5), "#ffb060", 0.45)
    lz.pintar(lz.trazo([(ventana.nonzero()[1].min() / S + 1, ventana.nonzero()[0].min() / S + 1),
                        (ventana.nonzero()[1].min() / S + 3, ventana.nonzero()[0].min() / S + 1)], 0.6, 0.6), "#fff8d2", 0.7)
    lz.sombrear(lz.trazo(tubo, 1.6, 1.4), LATON, 0.8, LUZ)
    if estado == 2:
        # agrietado: grietas que dejan escapar el brillo
        if cual == "techo":
            gs = [[(44, 21), (46, 25), (45, 29)], [(52, 22), (50, 26)]]
        else:
            gs = [[(97, 66), (100, 70), (99, 74)], [(106, 76), (103, 80)]]
        grietas_giza(lz, gs, 1.0, FUEGO)
    return lz.sprite(contorno=CONTORNO)


# ------------------------------------------------------------------ ruedas, pistón y molinete
def rueda(cx, cy, r, radios, giro, semilla):
    lz = nuevo(semilla)
    tex = lz.ruido(1.2, 2, semilla=semilla)
    aro = np.clip(lz.elipse(cx, cy, r, r) - lz.elipse(cx, cy, r - 2.6, r - 2.6), 0, 1)
    lz.sombrear(aro, OXIDO, 1.8, LUZ, textura=tex, fuerza_tex=0.4)
    for k in range(radios):
        a = giro + k * 2 * math.pi / radios
        lz.sombrear(lz.trazo([(cx, cy), (cx + math.cos(a) * (r - 2.2), cy + math.sin(a) * (r - 2.2))], 1.3, 1.0), OXIDO[1:6], 0.6, LUZ)
    lz.sombrear(lz.circulo(cx, cy, r * 0.24), LATON, 1.3, LUZ)
    lz.pintar(lz.circulo(cx, cy, r * 0.09), "#120708")
    for k in range(radios * 2):                                   # tacos del aro (giran con la rueda)
        a = giro + k * math.pi / radios
        lz.sombrear(lz.circulo(cx + math.cos(a) * (r - 0.4), cy + math.sin(a) * (r - 0.4), 1.2), OXIDO[1:5], 0.8, LUZ)
    return lz.sprite(contorno=CONTORNO)


def piston(f):
    lz = nuevo(110 + f)
    a = f * math.pi / 2
    manivela = (48 + math.cos(a) * 7, 80 + math.sin(a) * 7)
    lz.sombrear(lz.trazo([(68, 68), manivela], 2.2, 2.0), CHAPA[1:], 1, LUZ)
    lz.sombrear(lz.circulo(manivela[0], manivela[1], 1.8), LATON, 1, LUZ)
    lz.sombrear(lz.circulo(68, 68, 1.6), LATON, 1, LUZ)
    return lz.sprite(contorno=CONTORNO)


def molinete(f):
    """f 0-3: girando · 4: enredado en los brotes (parado)"""
    lz = nuevo(120 + f)
    mx, my, mr = 112, 62, 18
    giro = (f * math.pi / 12) if f < 4 else 0.35
    disco = np.clip(lz.elipse(mx, my, mr - 4, mr - 4) - lz.elipse(mx, my, mr - 6, mr - 6), 0, 1)
    lz.sombrear(disco, OXIDO, 1, LUZ)
    for k in range(6):
        a = giro + k * math.pi / 3
        px, py = mx + math.cos(a) * mr, my + math.sin(a) * mr
        lz.sombrear(lz.trazo([(mx, my), (px, py)], 1.7, 1.3), OXIDO, 0.8, LUZ)
        t = (-math.sin(a), math.cos(a))
        pala = lz.trazo([(px - t[0] * 5, py - t[1] * 5), (px + t[0] * 5, py + t[1] * 5)], 3.0, 3.0)
        lz.sombrear(pala, MADERA, 1.2, LUZ)
        for d in (-4, 0, 4):
            q = (px + t[0] * d, py + t[1] * d)
            lz.pintar(lz.trazo([q, (q[0] + math.cos(a) * 3.4, q[1] + math.sin(a) * 3.4)], 0.7, 0.4), CHAPA[5])
    lz.sombrear(lz.circulo(mx, my, 3.6), LATON, 2, LUZ)
    lz.pintar(lz.circulo(mx - 1, my - 1, 1.0), LATON[5])
    if f == 4:
        for k in range(9):
            a = k * 0.8
            pts = [(mx - 18 + k * 4.4, 92), (mx - 15 + k * 4.4 + math.sin(a) * 4, 72), (mx - 12 + k * 3.6, 52 + (k % 3) * 4)]
            lz.sombrear(lz.trazo(pts, 1.4, 0.7), VERDE, 1, LUZ)
            lz.sombrear(lz.elipse(pts[1][0] + 2.5, pts[1][1], 2.8, 1.4, 30), VERDE[2:], 1.2, LUZ)
            if k % 3 == 0:
                lz.sombrear(lz.elipse(pts[2][0] + 2, pts[2][1], 2.4, 1.2, -20), VERDE[2:], 1, LUZ)
    return lz.sprite(contorno=CONTORNO)


# ------------------------------------------------------------------ corazón y enredaderas
def corazon(f):
    lz = nuevo(130 + f)
    late = [1.0, 1.12, 1.2, 1.08][f]
    cx, cy = 64, 58
    lz.sumar_luz(lz.desenfocar(lz.elipse(cx, cy, 13 * late, 10 * late), 4), "#a855d6", 0.7)
    nucleo = lz.elipse(cx, cy, 9 * late, 8 * late)
    lz.sombrear(nucleo, GIZA, 6, LUZ, recorte=("#dcaaf2", 0.6), recorte_dir=(-1, -1))
    # raíces de piedra que lo sujetan
    for k in range(6):
        a = k * math.pi / 3 + 0.3
        lz.sombrear(lz.trazo([(cx + math.cos(a) * 7, cy + math.sin(a) * 6), (cx + math.cos(a) * 15, cy + math.sin(a) * 11)], 2.0, 1.0),
                    ["#2b2c30", "#3d3f43", "#525458", "#6a6c6f"], 1, LUZ)
    # el ojo (pupila de Giza) que mira
    lz.pintar(lz.elipse(cx, cy, 4.2 * late, 3.2), "#fff3fb")
    lz.pintar(lz.elipse(cx + 0.6, cy, 1.6, 2.8), "#120712")
    lz.pintar(lz.circulo(cx - 1.4, cy - 1.2, 0.7), "#ffffff")
    return lz.sprite(contorno=0.3)


def enredaderas():
    lz = nuevo(140)
    for k in range(16):
        x = 12 + k * 7
        alto = 26 + (k % 5) * 8
        pts = [(x + math.sin(j * 1.3 + k) * 3.5, SUELO - 2 - alto * j / 5) for j in range(6)]
        lz.sombrear(lz.trazo(pts, 1.6, 0.6), VERDE, 0.9, LUZ)
        for (hx, hy) in pts[1::2]:
            lz.sombrear(lz.elipse(hx + 2, hy, 2.8, 1.4, 20 + k * 25), VERDE[2:], 1.2, LUZ)
        if k % 2 == 0:
            fx, fy = pts[-1]
            col = ["#f4b39a", "#fff3c4", "#e6a852", "#de6771"][k % 4]
            for p in range(5):
                a = p * 2 * math.pi / 5
                lz.pintar(lz.circulo(fx + math.cos(a) * 1.8, fy - 1.5 + math.sin(a) * 1.8, 1.3), col)
            lz.pintar(lz.circulo(fx, fy - 1.5, 0.9), "#e6a852")
    return lz.sprite(contorno=CONTORNO)


def guardar(nombre, imgs):
    hoja = np.concatenate(imgs, axis=1)
    Image.fromarray(hoja, "RGBA").save(os.path.join(SALIDA, nombre + ".png"), optimize=True)
    print("guardado:", nombre, len(imgs), "fotogramas")


def main():
    os.makedirs(SALIDA, exist_ok=True)
    guardar("chasis", [chasis(e) for e in range(3)])
    guardar("caldera", [caldera(e) for e in range(3)])
    guardar("dep_techo", [deposito("techo", e) for e in range(4)])
    guardar("dep_frontal", [deposito("frontal", e) for e in range(4)])
    guardar("rueda_g", [rueda(48, 80, 15, 8, f * math.pi / 16, 100 + f) for f in range(4)])
    guardar("rueda_p", [rueda(92, 86, 8, 6, -f * math.pi / 12, 105 + f) for f in range(4)])
    guardar("piston", [piston(f) for f in range(4)])
    guardar("molinete", [molinete(f) for f in range(5)])
    guardar("corazon", [corazon(f) for f in range(4)])
    guardar("enredaderas", [enredaderas()])


if __name__ == "__main__":
    main()
