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
    """El granero en ruinas del Campo Segado (128×112, la base en el centro de abajo), de frente y un poco desde arriba:
    el hastial alto de tablas rojizas con la pintura desconchada; el portón grande de dos hojas (una colgando torcida)
    con el heno viejo dentro; el pajar de arriba con su trampilla abierta y la polea; el tejado de tablillas hundido
    por un lado (se ven las vigas); la veleta de gallo oxidada y torcida; una carreta rota y dos cuervos de óxido."""
    import pintar_aldea as pa
    W, H = 128, 104
    lz = pa._lienzo(W, H, 10, 31)
    suelo = 100
    cx = 62
    LUZ_ = (-0.6, -0.7, 0.5)
    ROJO_ = ["#2a0e0a", "#4a1810", "#6e2418", "#8e3420", "#a8482c", "#c0603e"]
    MAD = ["#1e140e", "#33231a", "#4a3424", "#634733", "#7d5c42", "#977452"]
    lz.pintar(lz.desenfocar(lz.elipse(cx, suelo, 58, 5), 2), "#0e0c0a", 0.45)
    # la fachada: hastial de tablas verticales rojizas, con la pintura desconchada
    fach = lz.poligono([(cx - 40, suelo), (cx - 40, 44), (cx, 16), (cx + 40, 44), (cx + 40, suelo)])
    tabv = (np.abs(np.sin((lz.x - cx) / 3.6 * np.pi)) < 0.1).astype(float)
    lz.sombrear(fach, ROJO_, 8, LUZ_, textura=pa.vetas(lz, 0.5, 15, False, semilla=32) * (1 - tabv * 0.7), fuerza_tex=0.45)
    desconchon = fach * (lz.ruido(2.4, 3, semilla=33) > 0.66)
    lz.sombrear(desconchon, MAD[2:], 1, LUZ_, textura=pa.vetas(lz, 0.5, 11, False), fuerza_tex=0.4)
    for (a, b) in (((cx - 40, 44), (cx, 16)), ((cx, 16), (cx + 40, 44))):         # el canto blanco del hastial
        lz.sombrear(lz.trazo([a, b], 1.6), ["#8a8270", "#b4ac98", "#d8d0bc"], 0.5, LUZ_)
    # el tejado de tablillas de lado (a la izquierda) hundido, con vigas a la vista
    tej = lz.poligono([(cx - 40, 44), (cx - 58, 64), (cx - 58, 70), (cx - 40, 52)])
    lz.sombrear(tej, ["#2a160e", "#47291c", "#643a26", "#7f4d33"], 2, LUZ_, textura=pa.vetas(lz, 0.5, 7), fuerza_tex=0.5)
    lz.sombrear(pa.rect(lz, cx - 58, 64, cx - 40, suelo), ROJO_, 3, LUZ_, textura=pa.vetas(lz, 0.5, 15, False, semilla=34), fuerza_tex=0.4)
    lz.pintar(pa.rect(lz, cx - 58, 64, cx - 40, suelo), "#0e0a08", 0.4)
    hueco = lz.poligono([(cx + 10, 30), (cx + 22, 34), (cx + 28, 46), (cx + 18, 50), (cx + 8, 42)])
    lz.pintar(hueco, "#0a0806")
    for (a, b) in (((cx + 8, 34), (cx + 28, 46)), ((cx + 14, 30), (cx + 18, 50))):
        lz.sombrear(lz.trazo([a, b], 1.4), MAD[1:], 0.5, LUZ_)
    # el pajar: la trampilla abierta con heno asomando y la polea
    pajar = pa.rect(lz, cx - 8, 30, cx + 6, 42)
    lz.pintar(pajar, "#120c08")
    heno = lz.poligono([(cx - 8, 42), (cx - 6, 36), (cx, 34), (cx + 4, 37), (cx + 6, 42)])
    lz.sombrear(heno, ["#3d3214", "#5c4a22", "#7a6431", "#958043", "#b09c5c"], 1, LUZ_, textura=pa.vetas(lz, 0.4, 7, False), fuerza_tex=0.6)
    lz.sombrear(lz.trazo([(cx - 1, 22), (cx - 1, 28)], 1.0), MAD[2:], 0.4, LUZ_)
    lz.sombrear(lz.circulo(cx - 1, 29, 1.6), HIERRO, 0.5, LUZ_)
    lz.pintar(lz.trazo([(cx - 1, 30), (cx - 1, 50)], 0.4), "#a48656")
    # el portón: una hoja cerrada y la otra colgando torcida; dentro, heno viejo
    vano = pa.rect(lz, cx - 22, 58, cx + 22, suelo)
    lz.pintar(vano, "#0e0a08")
    lz.sombrear(lz.elipse(cx + 6, suelo - 3, 14, 5), ["#3d3214", "#5c4a22", "#7a6431", "#958043"], 2, LUZ_, textura=pa.vetas(lz, 0.4, 7, False), fuerza_tex=0.6)
    hoja1 = pa.rect(lz, cx - 22, 58, cx - 1, suelo)
    lz.sombrear(hoja1, ROJO_, 2, LUZ_, textura=pa.vetas(lz, 0.5, 13, False) * (1 - tabv * 0.6), fuerza_tex=0.45)
    for (a, b) in (((cx - 22, 60), (cx - 1, suelo - 2)), ((cx - 22, suelo - 2), (cx - 1, 60))):
        lz.sombrear(lz.trazo([a, b], 1.6), ["#8a8270", "#b4ac98", "#d8d0bc"], 0.4, LUZ_)
    hoja2 = lz.poligono([(cx + 2, 60), (cx + 20, 64), (cx + 26, suelo + 1), (cx + 6, suelo - 1)])
    lz.sombrear(hoja2, ROJO_, 2, LUZ_, textura=pa.vetas(lz, 0.5, 13, False), fuerza_tex=0.4)
    lz.pintar(lz.trazo([(cx + 2, 64), (cx + 6, 66)], 0.8), "#2e2f33")
    # la veleta de gallo oxidada y torcida
    lz.sombrear(lz.trazo([(cx, 16), (cx + 2, 4)], 0.8), OXIDO_ if "OXIDO_" in globals() else ["#4a1e0e", "#7a3418", "#a84e24"], 0.4, LUZ_)
    gallo = lz.poligono([(cx - 3, 3), (cx + 2, -2), (cx + 4, -6), (cx + 6, -3), (cx + 8, 0), (cx + 6, 3)])
    lz.sombrear(gallo, ["#4a1e0e", "#7a3418", "#a84e24", "#d07a3a"], 0.6, LUZ_)
    # la carreta rota, a la derecha
    car = lz.poligono([(cx + 44, 86), (cx + 64, 84), (cx + 64, 92), (cx + 46, 94)])
    lz.sombrear(car, MAD, 1, LUZ_, textura=pa.vetas(lz, 0.5, 9), fuerza_tex=0.4)
    rueda = np.clip(lz.circulo(cx + 50, 95, 5) - lz.circulo(cx + 50, 95, 3.6), 0, 1)
    lz.sombrear(rueda, MAD, 0.6, LUZ_)
    for a in np.linspace(0, np.pi, 4):
        lz.pintar(lz.trazo([(cx + 50 - np.cos(a) * 4, 95 - np.sin(a) * 4), (cx + 50 + np.cos(a) * 4, 95 + np.sin(a) * 4)], 0.5), MAD[3])
    lz.sombrear(lz.elipse(cx + 60, suelo, 4.5, 1.6, 20), MAD[1:], 0.4, LUZ_)             # la otra rueda, caída
    # dos cuervos de óxido: uno en el tejado, otro en la carreta
    for (x, y, m) in ((cx - 30, 52, 1), (cx + 58, 82, -1)):
        cuerpo = lz.elipse(x, y, 3.4, 2.2)
        lz.sombrear(cuerpo, ["#141418", "#22222a", "#3a3a46", "#5a5a6a"], 0.8, LUZ_)
        lz.sombrear(lz.circulo(x + m * 3, y - 2, 1.6), ["#141418", "#3a3a46"], 0.5, LUZ_)
        lz.pintar(lz.poligono([(x + m * 4.4, y - 2.4), (x + m * 6.4, y - 1.8), (x + m * 4.4, y - 1.4)]), "#c87a40")
        lz.pintar(lz.circulo(x + m * 3.4, y - 2.4, 0.5), "#a855d6")
    pa._hierba_pie(lz, 2, 126, suelo - 2, 35, seco=True)
    return lz.sprite(contorno=0.4)

# ---------------------------------------------------------------- molino
def molino():
    """El molino roto del Campo Segado (96×150, la base en el centro de abajo): una torre de piedra encalada que se
    estrecha hacia arriba, con grietas y el yeso caído a trozos; la puerta de tablas entornada, un ventanuco y un
    balcón de madera; el capuchón de tablas con la veleta torcida; las aspas de celosía: dos enteras con la lona hecha
    jirones y dos partidas (una colgando); al pie, sacos de harina viejos y una muela de piedra caída."""
    import pintar_aldea as pa
    W, H = 96, 150
    lz = Lienzo(W, H, s=4, semilla=41)
    suelo = 146
    cx = 48
    LUZ_ = (-0.6, -0.7, 0.5)
    CAL = ["#3a3630", "#5e5850", "#868070", "#aaa392", "#c8c0ac", "#e0d8c4", "#f0ead8"]
    MAD = ["#1e140e", "#33231a", "#4a3424", "#634733", "#7d5c42", "#977452"]
    lz.pintar(lz.desenfocar(lz.elipse(cx, suelo, 40, 4), 2), "#0e0c0a", 0.45)
    # la torre
    torre = lz.poligono([(cx - 22, suelo), (cx - 15, 52), (cx + 15, 52), (cx + 22, suelo)])
    lz.sombrear(torre, CAL, 10, LUZ_, textura=lz.ruido(0.8, 3, semilla=42), fuerza_tex=0.25)
    caido = torre * (lz.ruido(3.5, 3, semilla=43) > 0.72)
    pa.piedras(lz, caido, tam=2.6, semilla=44, luz=LUZ_, mortero="#3a3428", rampa_p=pa.PIEDRA_C)
    for g in ([(cx - 6, 60), (cx - 2, 78), (cx - 7, 96)], [(cx + 10, 110), (cx + 6, 126), (cx + 12, 140)]):
        lz.pintar(lz.trazo(g, 0.6) * torre, "#2a2620", 0.85)
    musgo = (lz.ruido(2, 3, semilla=45) > 0.68) * torre * np.clip((lz.y - 120) / 20, 0, 1)
    lz.pintar(lz.desenfocar(musgo, 0.4), pa.rampa(["#24401f", "#3f5a2f", "#5d7a3c"], lz.ruido(0.7, 2)), 0.7)
    # la puerta entornada, el ventanuco y el balconcito
    pu = pa.rect(lz, cx - 8, 122, cx + 8, suelo - 1) * np.clip(1 - np.maximum(0, 128 - lz.y) * 0, 0, 1)
    pu = np.maximum(pu * (lz.y > 126), lz.elipse(cx, 126, 8, 5) * (lz.y <= 126))
    lz.pintar(pu, "#0e0a08")
    hoja = lz.poligono([(cx - 8, 124), (cx - 2, 126), (cx - 2, suelo - 1), (cx - 8, suelo - 1)])
    lz.sombrear(hoja, MAD, 1.5, LUZ_, textura=pa.vetas(lz, 0.5, 11, False), fuerza_tex=0.4)
    lz.sombrear(pa.rect(lz, cx - 4, 84, cx + 4, 94), ["#0e0a08", "#1a1410", "#2a2018"], 0.5, LUZ_)
    lz.sombrear(pa.rect(lz, cx - 5, 83, cx + 5, 84.5), MAD[2:], 0.4, LUZ_)
    bal = pa.rect(lz, cx - 20, 100, cx + 20, 103)
    lz.sombrear(bal, MAD, 1, LUZ_, textura=pa.vetas(lz, 0.5, 9), fuerza_tex=0.4)
    for x in range(int(cx - 19), int(cx + 20), 5):
        if abs(x - cx) > 3 or True:
            lz.sombrear(lz.trazo([(x, 100), (x, 94)], 0.7), MAD[2:], 0.3, LUZ_)
    lz.sombrear(lz.trazo([(cx - 20, 94), (cx + 4, 94)], 0.7) + lz.trazo([(cx + 9, 95.5), (cx + 20, 94)], 0.7), MAD[2:], 0.3, LUZ_)
    # el capuchón de tablas y la veleta torcida
    cap = lz.poligono([(cx - 18, 54), (cx - 14, 40), (cx, 32), (cx + 14, 40), (cx + 18, 54)])
    tab = (np.abs(np.sin((lz.x - cx) / 3 * np.pi)) < 0.1).astype(float)
    lz.sombrear(cap, MAD, 5, LUZ_, textura=pa.vetas(lz, 0.5, 9, False) * (1 - tab * 0.7), fuerza_tex=0.45)
    lz.sombrear(pa.rect(lz, cx - 19, 52, cx + 19, 55), MAD[1:], 0.6, LUZ_)
    lz.sombrear(lz.trazo([(cx, 32), (cx + 2, 20)], 0.8), HIERRO, 0.4, LUZ_)
    lz.sombrear(lz.poligono([(cx + 2, 20), (cx + 10, 18), (cx + 3, 23)]), HIERRO, 0.5, LUZ_)
    # el eje y las aspas (delante de la torre): dos enteras con lona en jirones, una partida y otra colgando
    ex, ey = cx, 48
    def aspa(angulo, largo, lona=True, rota=0.0):
        d = np.array([math.cos(angulo), math.sin(angulo)])
        n = np.array([-d[1], d[0]])
        base = np.array([ex, ey])
        punta = base + d * largo
        lz.sombrear(lz.trazo([tuple(base), tuple(punta)], 1.6, 1.2), MAD[1:], 0.5, LUZ_)
        for k in range(1, int(largo / 5)):
            p0 = base + d * k * 5
            lz.sombrear(lz.trazo([tuple(p0), tuple(p0 + n * 6)], 0.6), MAD[2:], 0.3, LUZ_)
        lz.sombrear(lz.trazo([tuple(base + d * 8 + n * 6), tuple(punta + n * 6)], 0.6), MAD[2:], 0.3, LUZ_)
        if lona:
            q = [tuple(base + d * 10), tuple(punta - d * 2), tuple(punta - d * 2 + n * 5), tuple(base + d * 10 + n * 5)]
            tela = lz.poligono(q) * (lz.ruido(1.2, 2, semilla=int(abs(angulo) * 10)) > 0.3 + rota)
            lz.sombrear(tela, ["#5a5040", "#8a7e64", "#b8aa88", "#d8ccaa"], 0.8, LUZ_)
    aspa(-0.62, 54, True, 0.0)
    aspa(2.52, 54, True, 0.12)
    aspa(0.95, 20, False)                           # la partida
    aspa(1.72, 44, False)                           # la que cuelga, casi vertical
    lz.sombrear(lz.circulo(ex, ey, 3.2), HIERRO, 1, LUZ_)
    lz.pintar(lz.circulo(ex, ey, 1), HIERRO[0])
    # al pie: sacos de harina viejos y la muela caída
    for (x, y) in ((cx - 30, suelo), (cx - 24, suelo + 1), (cx - 27, suelo - 7)):
        saco = lz.poligono([(x - 4, y), (x - 4.5, y - 7), (x - 2, y - 10), (x + 2, y - 10), (x + 4.5, y - 7), (x + 4, y)])
        lz.sombrear(saco, ["#5a4630", "#8a7454", "#b8a07a", "#d8c49c", "#efe0bf"], 1.5, LUZ_)
        lz.pintar(lz.trazo([(x - 2, y - 8.6), (x + 2, y - 8.6)], 0.5), "#47291c")
    muela = lz.elipse(cx + 30, suelo - 2, 10, 4.5)
    lz.sombrear(muela, ["#3a3630", "#5e5850", "#868070", "#aaa392", "#c8c0ac"], 2, LUZ_)
    lz.pintar(lz.elipse(cx + 30, suelo - 3, 2.4, 1.1), "#1e1a14")
    pa._hierba_pie(lz, cx - 44, cx + 44, suelo - 2, 46, seco=True)
    return lz.sprite(contorno=0.4)

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
