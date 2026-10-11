"""LOS OBJETOS DEL CAMPO SEGADO, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_campo.py

Genera en arte/mundos/raiz/campo/:
  granero.png     72×60      granero de tablas rojizas con el tejado hundido y la puerta colgando
  molino.png      52×88      molino de viento de piedra con el capuchón de madera y dos aspas rotas
  maquina.png     2 × 46×30  máquinas viejas oxidadas: un arado de discos y una trilladora volcada
  paca.png        2 × 16×14  pacas de paja (una entera, otra deshecha) — píxel a píxel
  chatarra.png    2 × 16×20  bloque de chatarra que crea la Cosechadora (entero / roto) — píxel a píxel
  tuerca.png      2 × 8×8    la tuerca que lanza la Cosechadora (dos giros) — píxel a píxel
Todos con contorno selectivo, como el resto de sprites.
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_casa_shamba import CORTE, vetas, rect  # noqa: E402
from pintar_granja import PAJA, HIERRO, tablon, poste  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "campo")
LUZ = (-0.6, -0.7, 0.5)
ROJIZO = ["#2a1210", "#4a1d16", "#6e2a1e", "#8f3a26", "#ab5031", "#c26a44", "#d88a60"]
TABLA = ["#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259", "#d2a07c"]
PIEDRA = ["#2a2b26", "#45473f", "#5f6256", "#7a806d", "#999e8a", "#b9bdaa", "#d6d8c8"]
OXIDO = ["#2a120a", "#4a1e10", "#6e3218", "#9c4f24", "#c67238", "#e09a5c"]
HIERRO_V = ["#16171a", "#2b2c30", "#45474c", "#65676c", "#8a8c90", "#b0b2b4"]
TEJA = ["#1f1712", "#33261c", "#4a3826", "#614a32", "#7a5e40"]
CONTORNO = 0.42


def tira(imgs):
    w = sum(i.shape[1] for i in imgs)
    h = max(i.shape[0] for i in imgs)
    out = np.zeros((h, w, 4), np.uint8)
    x = 0
    for i in imgs:
        out[h - i.shape[0]:, x:x + i.shape[1]] = i
        x += i.shape[1]
    return Image.fromarray(out, "RGBA")


# ---------------------------------------------------------------- granero
def granero():
    """De frente (un poco desde arriba): fachada con el hastial, tablas verticales rojizas, la puerta
    grande de dos hojas (una colgando torcida), el tejado de tablillas hundido con un agujero y paja dentro."""
    W, H = 72, 60
    lz = Lienzo(W, H, s=6, semilla=31)
    suelo = 58
    lz.pintar(lz.desenfocar(lz.elipse(36, suelo, 34, 2.2), 0.8), "#140e0a", 0.55)
    # el lado del granero (en escorzo, a la derecha) y la fachada
    lado = lz.poligono([(56, 26), (68, 20), (68, 48), (56, suelo)])
    lz.sombrear(lado, ROJIZO[:5], 4, LUZ, textura=vetas(lz, 0.5, 15, False, 2), fuerza_tex=0.4)
    fachada = lz.poligono([(8, suelo), (8, 28), (32, 10), (56, 28), (56, suelo)])
    tablas = vetas(lz, 0.45, 19, False, 3)
    junta = ((lz.x - 8) % 5.0 < 0.7)
    lz.sombrear(fachada, ROJIZO, 14, LUZ, textura=tablas, fuerza_tex=0.45)
    lz.pintar(fachada * junta, "#2a1210", 0.55)
    # las vigas blancas en cruz (pintadas, desconchadas)
    for (a, b) in (((10, 30), (54, 30)), ((32, 12), (32, 30))):
        t = lz.trazo([a, b], 1.6, 1.6)
        lz.pintar(t * (lz.ruido(0.6, 2, semilla=4) > 0.35), "#d8cdb4", 0.85)
    # tejado: dos aguas de tablillas, hundido por la derecha (con un agujero oscuro)
    for (pts, k) in (([(4, 30), (32, 6), (36, 9), (10, 33)], 0), ([(32, 6), (60, 30), (70, 22), (42, 2)], 1)):
        agua = lz.poligono(pts)
        filas = np.sin(lz.y * 1.6 + lz.x * (0.6 if k == 0 else -0.6))
        lz.sombrear(agua, TEJA, 3, LUZ, textura=(filas * 0.5 + 0.5) * 0.7 + vetas(lz, 0.4, 7, True, 5 + k) * 0.3, fuerza_tex=0.55)
    agujero = lz.poligono([(48, 14), (58, 22), (54, 25), (46, 19)])
    lz.pintar(agujero, "#120b08")
    for (x0, y0, x1, y1) in ((47, 15, 52, 22), (52, 17, 56, 24)):           # tablillas rotas que cuelgan
        tablon(lz, [(x0, y0), (x1, y1)], 1.0, TEJA + ["#93745a"])
    # la puerta grande: el hueco oscuro con paja dentro, una hoja abierta y otra torcida colgando
    hueco = rect(lz, 20, 36, 44, suelo)
    lz.pintar(hueco, "#120b08")
    paja_d = lz.poligono([(21, suelo), (24, 48), (32, 44), (40, 47), (43, suelo)])
    lz.sombrear(paja_d, PAJA[:5], 4, LUZ, textura=vetas(lz, 0.3, 5, False, 9), fuerza_tex=0.6)
    lz.pintar(paja_d, "#000000", 0.35)
    hoja_i = lz.poligono([(12, 37), (20, 36), (20, suelo), (12, suelo - 1)])
    lz.sombrear(hoja_i, TABLA, 4, LUZ, textura=vetas(lz, 0.4, 13, False, 10), fuerza_tex=0.45)
    hoja_d = lz.poligono([(44, 40), (52, 43), (51, suelo + 0.5), (43, suelo)])
    lz.sombrear(hoja_d, TABLA, 4, LUZ, textura=vetas(lz, 0.4, 13, False, 11), fuerza_tex=0.45)
    for (a, b) in (((12, 41), (20, 52)), ((44, 44), (51, 54))):              # cruces de refuerzo de las hojas
        tablon(lz, [a, b], 1.1, TABLA)
    # el ventanuco del pajar
    lz.pintar(rect(lz, 29, 18, 35, 25), "#120b08")
    tablon(lz, [(29, 18), (35, 18)], 1.0, TABLA)
    # matojos secos al pie
    rng = np.random.default_rng(12)
    for k in range(26):
        x = 6 + rng.random() * 62
        alto = 2 + rng.random() * 4
        lz.pintar(lz.trazo([(x, suelo), (x + rng.random() * 2 - 1, suelo - alto)], 0.8, 0.3), PAJA[rng.integers(2, 5)])
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- molino
def molino():
    """Torre de piedra que se estrecha hacia arriba, puerta de madera, ventanuco, capuchón de madera
    y las aspas de celosía en X: dos enteras y dos partidas (una colgando)."""
    W, H = 52, 88
    lz = Lienzo(W, H, s=6, semilla=41)
    suelo = 86
    cx = 26
    lz.pintar(lz.desenfocar(lz.elipse(cx, suelo, 16, 2), 0.8), "#140e0a", 0.55)
    torre = lz.poligono([(cx - 13, suelo), (cx - 9, 36), (cx + 9, 36), (cx + 13, suelo)])
    # piedras: hiladas con juntas
    hilada = np.abs(((lz.y - suelo) % 5.0) - 2.5) < 0.5
    desf = ((lz.y // 5) % 2) * 3.5
    junta_v = np.abs(((lz.x + desf) % 7.0) - 3.5) < 0.45
    tex = lz.ruido(1.2, 3, semilla=42)
    lz.sombrear(torre, PIEDRA, 10, LUZ, textura=tex, fuerza_tex=0.35)
    lz.pintar(torre * np.maximum(hilada, junta_v), "#2a2b26", 0.5)
    # musgo y grietas
    lz.pintar(torre * (lz.ruido(3, 3, semilla=43) > 0.68) * (lz.y > 60), "#4d6436", 0.6)
    lz.pintar(lz.trazo([(cx + 4, 44), (cx + 6, 52), (cx + 4, 58), (cx + 7, 66)], 0.8, 0.4), "#1b1c1a", 0.9)
    # puerta y ventanuco
    puerta = np.maximum(rect(lz, cx - 4, 72, cx + 4, suelo), lz.elipse(cx, 72, 4, 3))
    lz.sombrear(puerta, TABLA, 3, LUZ, textura=vetas(lz, 0.4, 11, False, 44), fuerza_tex=0.45)
    lz.pintar(lz.trazo([(cx - 4, 73), (cx + 4, 73)], 0.6, 0.6), "#1a0f0b")
    lz.sombrear(lz.circulo(cx + 2.5, 79, 0.6), HIERRO, 0.4, LUZ)
    lz.pintar(np.maximum(rect(lz, cx - 2, 50, cx + 2, 56), lz.elipse(cx, 50, 2, 1.6)), "#120b08")
    # el capuchón de madera (cúpula) sobre la torre
    cap = np.maximum(lz.elipse(cx, 36, 12, 9) * (lz.y < 37), rect(lz, cx - 11, 34, cx + 11, 38))
    lz.sombrear(cap, TABLA, 7, LUZ, textura=vetas(lz, 0.5, 5, False, 45), fuerza_tex=0.4)
    for k in range(-2, 3):
        lz.pintar(lz.trazo([(cx + k * 4.5, 28 + abs(k) * 1.6), (cx + k * 5.2, 37)], 0.5, 0.5), "#2a1a12", 0.8)
    # el eje de las aspas
    eje = (cx - 1, 30)
    lz.sombrear(lz.circulo(eje[0], eje[1], 2.6), TABLA, 1.5, LUZ)
    # las aspas: celosía de madera (dos largas, una partida, una colgando)
    aspas = [(-40, 31, False), (50, 28, False), (140, 15, True), (230, 27, False)]
    for (ang, largo, rota) in aspas:
        a = math.radians(ang)
        fin = (eje[0] + math.cos(a) * largo, eje[1] + math.sin(a) * largo)
        brazo = lz.trazo([eje, fin], 1.3, 1.0)
        lz.sombrear(brazo, TABLA, 0.8, LUZ)
        # la celosía (rejilla a un lado del brazo)
        n = (math.cos(a + math.pi / 2), math.sin(a + math.pi / 2))
        ancho = 5.5
        ini = 5.0
        p0 = (eje[0] + math.cos(a) * ini, eje[1] + math.sin(a) * ini)
        borde = [(p0[0] + n[0] * ancho, p0[1] + n[1] * ancho), (fin[0] + n[0] * ancho, fin[1] + n[1] * ancho)]
        lz.pintar(lz.trazo(borde, 0.7, 0.7), TABLA[3])
        pasos = int((largo - ini) / 3.2)
        for k in range(pasos + 1):
            t = ini + k * 3.2
            q = (eje[0] + math.cos(a) * t, eje[1] + math.sin(a) * t)
            lz.pintar(lz.trazo([q, (q[0] + n[0] * ancho, q[1] + n[1] * ancho)], 0.6, 0.6), TABLA[4])
        if rota:
            # la punta partida: astillas
            lz.pintar(lz.trazo([fin, (fin[0] + 2, fin[1] + 3)], 0.7, 0.3), TABLA[2])
    # un trozo de aspa caído al pie de la torre
    tablon(lz, [(cx + 10, suelo - 1), (cx + 22, suelo - 3)], 1.2, TABLA)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- máquinas viejas
def maquina(variante):
    W, H = 46, 30
    lz = Lienzo(W, H, s=8, semilla=51 + variante)
    suelo = 28
    lz.pintar(lz.desenfocar(lz.elipse(23, suelo, 21, 1.6), 0.6), "#140e0a", 0.55)
    tex = lz.ruido(1.0, 3, semilla=52 + variante)
    if variante == 0:
        # arado de discos: el bastidor, cinco discos en fila y una rueda grande de radios
        bastidor = lz.trazo([(4, 14), (40, 12)], 2.6, 2.4)
        lz.sombrear(bastidor, OXIDO, 1.2, LUZ, textura=tex, fuerza_tex=0.5)
        for k in range(5):
            x = 10 + k * 6
            disco = lz.elipse(x, 19, 2.6, 6.2)
            lz.sombrear(disco, HIERRO_V, 2, LUZ, textura=tex, fuerza_tex=0.4)
            lz.pintar(disco * (tex > 0.55), OXIDO[3], 0.7)
            lz.pintar(lz.trazo([(x, 13), (x, 16)], 0.8, 0.8), OXIDO[2])
        rueda = np.clip(lz.elipse(38, 18, 8, 9) - lz.elipse(38, 18, 6.6, 7.6), 0, 1)
        lz.sombrear(rueda, OXIDO, 1, LUZ, textura=tex, fuerza_tex=0.5)
        for k in range(8):
            a = k * math.pi / 4
            lz.pintar(lz.trazo([(38, 18), (38 + math.cos(a) * 6.8, 18 + math.sin(a) * 7.8)], 0.7, 0.6), OXIDO[2])
        lz.sombrear(lz.circulo(38, 18, 1.6), HIERRO_V, 1, LUZ)
        # timón (lanza) apoyado en el suelo
        lz.sombrear(lz.trazo([(4, 14), (1, 26)], 1.6, 1.4), TABLA, 0.8, LUZ)
    else:
        # trilladora volcada: la caja de madera ladeada, la chimenea torcida y una rueda en el aire
        caja = lz.poligono([(5, 26), (8, 9), (34, 6), (38, 24)])
        lz.sombrear(caja, ROJIZO[:6], 6, LUZ, textura=vetas(lz, 0.4, 15, True, 53), fuerza_tex=0.45)
        for k in range(4):
            y = 11 + k * 4
            tablon(lz, [(7.5, y + 0.5), (35, y - 2)], 0.6, ROJIZO)
        tolva = lz.poligono([(20, 7), (24, 1), (32, 1), (31, 6)])
        lz.sombrear(tolva, OXIDO, 2, LUZ, textura=tex, fuerza_tex=0.5)
        chimenea = lz.trazo([(12, 8), (10, 2), (6, 0)], 2.2, 1.8)
        lz.sombrear(chimenea, HIERRO_V, 1, LUZ, textura=tex, fuerza_tex=0.4)
        rueda = np.clip(lz.elipse(40, 14, 5.5, 6.5) - lz.elipse(40, 14, 4.2, 5.2), 0, 1)
        lz.sombrear(rueda, OXIDO, 1, LUZ, textura=tex, fuerza_tex=0.5)
        for k in range(6):
            a = k * math.pi / 3
            lz.pintar(lz.trazo([(40, 14), (40 + math.cos(a) * 4.5, 14 + math.sin(a) * 5.4)], 0.6, 0.5), OXIDO[2])
        lz.sombrear(lz.circulo(14, 25, 3.6), OXIDO, 1.5, LUZ, textura=tex, fuerza_tex=0.5)
    # hierbajos que han crecido entre los hierros
    rng = np.random.default_rng(54 + variante)
    for k in range(16):
        x = 3 + rng.random() * 40
        lz.pintar(lz.trazo([(x, suelo), (x + rng.random() * 2 - 1, suelo - 2 - rng.random() * 4)], 0.7, 0.25),
                  ["#3f582f", "#526d38", "#a37036"][rng.integers(3)])
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- píxel a píxel
def mapa(filas, leyenda):
    h, w = len(filas), max(len(f) for f in filas)
    out = np.zeros((h, w, 4), np.uint8)
    for y, f in enumerate(filas):
        for x, ch in enumerate(f):
            if ch in leyenda:
                col = leyenda[ch].lstrip("#")
                out[y, x] = [int(col[i:i + 2], 16) for i in (0, 2, 4)] + [255]
    return out


PAJA_L = {"o": "#3d2a10", "d": "#704f25", "m": "#a37036", "c": "#d29a43", "l": "#efc06a", "b": "#f8dc96",
          "t": "#5a3a22", "s": "#1d140f"}
PACA = [
    "................",
    "...odddddddddo..",
    "..odmmmcmmmmmdo.",
    ".odmcclcllcclmdo",
    ".dmclbllblbllcmd",
    ".dmcllcllcllcmmd",
    ".dtttttttttttttd",
    ".dmcllcllcllcmmd",
    ".dmcclclllclcmmd",
    ".dtttttttttttttd",
    ".dmcllcllcllcmmd",
    ".odmmcmcmmcmmmdo",
    "..oddddddddddoo.",
    "...ssssssssss...",
]
PACA_ROTA = [
    "................",
    "................",
    "................",
    "......c.l.......",
    "....clb.lc..l...",
    "...dmclllcmc.c..",
    "..dmcllcllclmd..",
    ".dmcllbllcllcmd.",
    ".dmmcllcclllcmd.",
    "odmcmclcmcmcmmdo",
    "omd.l.mc.cm.l.mo",
    ".o.c..m.l..c.do.",
    "..o.dddd..ddo...",
    "...ssssssssss...",
]
CHATARRA_L = {"o": "#2a120a", "x": "#4a1e10", "r": "#6e3218", "R": "#9c4f24", "n": "#c67238", "N": "#e09a5c",
              "h": "#2b2c30", "H": "#45474c", "g": "#65676c", "G": "#8a8c90", "v": "#6b2a8f", "V": "#a855d6",
              "s": "#1d140f"}
CHATARRA = [
    "......hHg.......",
    "....hhGGgHh.....",
    "...oxRRnHGgh....",
    "..oxRnnNRrHgh...",
    ".oxrRRnNnRrxhh..",
    ".oRnNhHgRnRrxo..",
    "oxRnhGGgHrRnRxo.",
    "oRnRhHgVhRnNnRxo",
    "orRrxhvVvhrRnRro",
    "oRnRrxhvhxRnNRxo",
    "oxRnnRrxrRnnRrxo",
    "orRhHgRnRRhHgRro",
    "oxrhGGgnNRhGGgxo",
    "oRrxhHgRnRrhHgro",
    "oxRRrxrRnNRrxRxo",
    "orRnRRrxrRnRRrro",
    ".oxrRnRRnRRrrxo.",
    "..ooxrrxxrrxoo..",
    "...ssssssssss...",
    "................",
]
CHATARRA_ROTA = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "......hG........",
    "..or.hGg..xRn...",
    ".oRn.....oRNr.h.",
    "oxRr..hHg.xRro.G",
    "orR.xRn.hGg..rxo",
    ".oxrRRn.xRnRr.o.",
    "..ooxrr..rrxoo..",
    "...ssssssssss...",
    "................",
    "................",
]
TUERCA = [
    "..hHGh..",
    ".hGGgGh.",
    "hGgssgGh",
    "HGs..sGH",
    "HGs..sgH",
    "hgGssGgh",
    ".hgGGgh.",
    "..hhhh..",
]
TUERCA_2 = [
    "...hh...",
    ".hhGGhh.",
    "hGGssgGh",
    "hGs..sgH",
    "hgs..sGh",
    "hGgssGGh",
    ".hhggHh.",
    "...hh...",
]
TUERCA_L = {"h": "#2b2c30", "H": "#45474c", "g": "#65676c", "G": "#b0b2b4", "s": "#16171a"}


def main():
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(granero(), "RGBA").save(os.path.join(SALIDA, "granero.png"))
    Image.fromarray(molino(), "RGBA").save(os.path.join(SALIDA, "molino.png"))
    tira([maquina(0), maquina(1)]).save(os.path.join(SALIDA, "maquina.png"))
    tira([mapa(PACA, PAJA_L), mapa(PACA_ROTA, PAJA_L)]).save(os.path.join(SALIDA, "paca.png"))
    tira([mapa(CHATARRA, CHATARRA_L), mapa(CHATARRA_ROTA, CHATARRA_L)]).save(os.path.join(SALIDA, "chatarra.png"))
    tira([mapa(TUERCA, TUERCA_L), mapa(TUERCA_2, TUERCA_L)]).save(os.path.join(SALIDA, "tuerca.png"))
    print("Objetos del Campo Segado en", SALIDA)


if __name__ == "__main__":
    main()
