"""LOS EDIFICIOS DE CUNA DE MUSGO, pintados con detalle (con el pintor de las cinemáticas), al nivel de la casa del
castor. Cada uno tiene 2 fotogramas: 0 en ruinas (como lo dejó Giza) y 1 reconstruido.

    python3 herramientas/pintar_aldea.py

Genera en arte/mundos/raiz/aldea/ (la base de la puerta, en el centro de abajo de cada fotograma):
  casa_seta.png   2 × 120×138  la casa-seta de PINO, el niño-seta vigía: una seta enorme de sombrero rojo con lunares,
                               ventanas redondas con luz, la puerta en arco, un puesto de vigía con banderín y catalejo,
                               una escalerita, setitas y un buzón
  taller.png      2 × 152×146  el taller de CORTEZA, la herrera: piedra y madera, tejado de tablillas, la chimenea de la
                               forja con humo y brasas, portalón, yunque y herraduras, muela de afilar, barril de agua
  cocina.png      2 × 132×128  la cocina de JUNCIA: cabaña de juncos con tejado de paja redondo, mostrador abierto, ollas
                               colgadas, el caldero al fuego, ristras de hierbas y cestos de bayas
  puesto.png      2 × 116×104  el puesto de TAWI, el pájaro comerciante: toldo a rayas, cajas de mercancía, cristales
                               del Nexo en un expositor, una balanza, farolillos y un cartel con una pluma
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa, RAIZ  # noqa: E402
from cinematicas import PIEDRA, HIERBA, COBRE, MADERA, flores  # noqa: E402
from cinematicas import piedras as _piedras  # noqa: E402
from pintar_casa_shamba import vetas, rect, troncos, paja, flecos, ventana, TRONCO, PIEDRA_C  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "aldea")
LUZ = (-0.6, -0.7, 0.5)
ROJO = ["#3a0a0e", "#5e1218", "#8a1c22", "#b42a2c", "#d6443c", "#ec6a58", "#f8a088"]
CREMA = ["#5a4a36", "#8a7658", "#b8a27c", "#dcc8a0", "#f0e2c0", "#fff6e0"]
GRIS_R = ["#2a2a2c", "#444446", "#626264", "#828284", "#a2a2a4"]        # lo que dejó Giza: sin color
LATON = ["#3a2a10", "#6a4e1e", "#9a7430", "#c89a44", "#e8c46a", "#fbe6a2"]


def _hierba_pie(lz, x0, x1, y, semilla, seco=False):
    rng = np.random.default_rng(semilla)
    h = np.zeros((lz.H, lz.W))
    for k in range(int((x1 - x0) * 1.3)):
        hx = x0 + rng.random() * (x1 - x0)
        hy = y + rng.random() * 4
        h = np.maximum(h, lz.trazo([(hx, hy), (hx + (rng.random() - 0.5) * 2.4, hy - 2 - rng.random() * 3.5)], 0.7, 0.3))
    lz.sombrear(h, (["#3a3418", "#5a5024", "#7a6e36", "#9a8c4c"] if seco else HIERBA[1:7]), 0.5, LUZ)


def _gris(lz, mascara=None):
    """Lo que toca Giza pierde el color: se pasa a gris (en las ruinas)."""
    pass


class _LienzoAlto(Lienzo):
    """Un lienzo con unos píxeles de más por ARRIBA del 0 (para lo que asoma: banderines, humo...): se dibuja con las
    mismas coordenadas de siempre y todo baja «arriba» píxeles."""

    def __init__(self, w, h, arriba, s=4, semilla=1):
        super().__init__(w, h + arriba, s=s, semilla=semilla)
        self.dy = arriba
        self.y = self.y - arriba

    def _p(self, puntos):
        return [(float(x), float(y) + self.dy) for (x, y) in np.array(puntos, float)]

    def poligono(self, puntos):
        return super().poligono(self._p(puntos))

    def elipse(self, cx, cy, rx, ry, angulo=0.0):
        return super().elipse(cx, cy + self.dy, rx, ry, angulo)

    def trazo(self, puntos, grosor_ini, grosor_fin=None, puntas=True):
        return super().trazo(self._p(puntos), grosor_ini, grosor_fin, puntas)


def piedras(lz, region, **kw):
    """Las piedras de cinematicas calculan su sitio en píxeles: en un lienzo alto, mientras tanto, no se desplaza."""
    dy = getattr(lz, "dy", 0)
    if dy:
        lz.dy, lz.y = 0, lz.y + dy
    _piedras(lz, region, **kw)
    if dy:
        lz.dy, lz.y = dy, lz.y - dy


def _lienzo(W, H, arriba, semilla):
    return _LienzoAlto(W, H, arriba, s=4, semilla=semilla)


def casa_seta(reconstruida):
    W, H = 120, 116
    lz = _lienzo(W, H, 22, 1001 + reconstruida)
    cx = 60
    suelo = 112
    lz.pintar(lz.desenfocar(lz.elipse(cx, suelo, 46, 5), 2), "#0a0a06", 0.45)
    # el pie de la seta: grueso, crema, con vetas y un zócalo de piedrecitas
    pie = lz.poligono([(cx - 30, suelo), (cx - 27, 70), (cx - 24, 52), (cx + 24, 52), (cx + 27, 70), (cx + 30, suelo)])
    tex = vetas(lz, 0.6, 15, False, semilla=1002)
    lz.sombrear(pie, CREMA if reconstruida else GRIS_R, 10, LUZ, textura=tex, fuerza_tex=0.3)
    zocalo = rect(lz, cx - 31, suelo - 8, cx + 31, suelo)
    piedras(lz, zocalo * pie, tam=3.6, semilla=1003, luz=LUZ, mortero="#3a3428", rampa_p=PIEDRA_C)
    musgo = (lz.ruido(2, 3, semilla=1004) > 0.62) * pie * np.clip((lz.y - 96) / 12, 0, 1)
    lz.pintar(lz.desenfocar(musgo, 0.4), rampa(["#24401f", "#3f5a2f", "#5d7a3c"], lz.ruido(0.7, 2)), 0.8)
    # ventanas redondas con luz (o tapiadas)
    for (vx, vy, r) in ((cx - 14, 68, 5.5), (cx + 15, 74, 4.5)):
        aro = np.clip(lz.circulo(vx, vy, r + 1.4) - lz.circulo(vx, vy, r), 0, 1)
        lz.sombrear(aro, TRONCO, 1, LUZ)
        vid = lz.circulo(vx, vy, r)
        if reconstruida:
            lz.pintar(vid, rampa(["#a8380f", "#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - vx + 1, lz.y - vy + 1) / r, 0, 1)))
            lz.pintar(np.maximum(rect(lz, vx - r, vy - 0.4, vx + r, vy + 0.4), rect(lz, vx - 0.4, vy - r, vx + 0.4, vy + r)) * vid, "#2a1a12")
            lz.sumar_luz(lz.desenfocar(vid, 3), "#ef8a26", 0.3)
            # jardinera con flores bajo la ventana grande
            if r > 5:
                j = rect(lz, vx - 7, vy + r + 1.5, vx + 7, vy + r + 5)
                lz.sombrear(j, COBRE, 1, LUZ, textura=vetas(lz, 0.5, 9), fuerza_tex=0.3)
                flores(lz, 7, (vx - 6, vy + r - 0.5, vx + 6, vy + r + 1.5), [["#8f2532", "#d5525e", "#f4b39a"], ["#b2721a", "#df9022", "#fde27e"]], semilla=1005, tam=0.8)
        else:
            lz.pintar(vid, "#141210")
            lz.sombrear(rect(lz, vx - r - 1, vy - 1.2, vx + r + 1, vy + 1.2), MADERA[2:], 0.8, LUZ)
    # la puerta en arco, de tablas, con su pomo y un farolillo
    pu = lz.poligono([(cx - 8, suelo - 1), (cx - 8, 92)] + [(cx + np.cos(a) * 8, 92 - np.sin(a) * 8) for a in np.linspace(np.pi, 0, 20)] + [(cx + 8, 92), (cx + 8, suelo - 1)])
    marco = np.clip(lz.poligono([(cx - 10, suelo), (cx - 10, 92)] + [(cx + np.cos(a) * 10, 92 - np.sin(a) * 10) for a in np.linspace(np.pi, 0, 20)] + [(cx + 10, 92), (cx + 10, suelo)]) - pu, 0, 1)
    lz.sombrear(marco, TRONCO, 1, LUZ, textura=vetas(lz, 0.5, 9, False), fuerza_tex=0.3)
    tablas = (np.abs(np.sin((lz.x - cx + 8) / 4 * np.pi)) < 0.1).astype(float)
    if reconstruida:
        lz.sombrear(pu, ["#251812", "#3d2418", "#5a3826", "#7a4e35", "#9a6847"], 5, LUZ, textura=vetas(lz, 0.5, 15, False) * (1 - tablas * 0.8), fuerza_tex=0.45)
        lz.sombrear(lz.circulo(cx + 5, 102, 1.0), LATON[2:], 0.6, LUZ)
        farol = rect(lz, cx + 13, 88, cx + 17, 94)
        lz.pintar(lz.trazo([(cx + 15, 84), (cx + 15, 88)], 0.5), "#1b1c1f")
        lz.pintar(farol, rampa(["#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - cx - 15, lz.y - 91) / 3, 0, 1)))
        lz.sumar_luz(lz.desenfocar(farol, 4), "#ef8a26", 0.35)
    else:
        lz.pintar(pu, "#0e0b0a")
        for (a, b) in (((cx - 9, 96), (cx + 9, 104)), ((cx - 9, 104), (cx + 9, 98))):
            lz.sombrear(lz.trazo([a, b], 1.6), MADERA[1:], 0.8, LUZ)
    # el sombrero: rojo, abombado, con lunares blancos; por debajo, las láminas
    lam = lz.elipse(cx, 52, 52, 7)
    lz.pintar(lam, "#d8c8a0" if reconstruida else "#6a6a6c")
    for k in range(-22, 23):
        lz.pintar(lz.trazo([(cx, 50), (cx + k * 2.3, 56)], 0.3) * lam, "#a89870" if reconstruida else "#4a4a4c", 0.8)
    if reconstruida:
        som = lz.poligono([(cx - 56, 52), (cx - 50, 34), (cx - 36, 18), (cx - 18, 8), (cx, 5), (cx + 18, 8), (cx + 36, 18), (cx + 50, 34), (cx + 56, 52), (cx, 56)])
    else:
        # roto: le falta un bocado y está gris y agrietado
        som = lz.poligono([(cx - 56, 52), (cx - 50, 34), (cx - 36, 18), (cx - 18, 8), (cx - 4, 6), (cx + 6, 16), (cx + 14, 12), (cx + 22, 22), (cx + 36, 20), (cx + 50, 34), (cx + 56, 52), (cx, 56)])
    lz.sombrear(som, ROJO if reconstruida else GRIS_R, 14, LUZ, textura=lz.ruido(0.8, 2, semilla=1006), fuerza_tex=0.25)
    rng = np.random.default_rng(1007)
    for (x, y, r) in ((-36, 32, 5), (-16, 18, 6.5), (8, 14, 4.5), (28, 24, 6), (44, 40, 4), (-46, 44, 3.5), (-2, 34, 4.5), (20, 42, 3.5), (-26, 44, 3)):
        lun = lz.elipse(cx + x, y, r, r * 0.75) * som
        lz.sombrear(lun, ["#c8b8a0", "#e8dcc8", "#fff8ee"] if reconstruida else ["#7a7a7c", "#9a9a9c", "#b2b2b4"], 1.2, LUZ)
    if not reconstruida:
        grietas = lz.trazo([(cx - 30, 20), (cx - 22, 32), (cx - 26, 44)], 0.6) + lz.trazo([(cx + 24, 26), (cx + 30, 38)], 0.6)
        lz.pintar(grietas * som, "#1a1a1c", 0.9)
        lz.pintar(lz.trazo([(cx - 8, 60), (cx - 12, 74), (cx - 9, 86)], 0.6) * pie, "#2a2a2c", 0.8)
    # el puesto de vigía de Pino, encima: una barandilla de ramas, el banderín y el catalejo
    if reconstruida:
        tabla = rect(lz, cx + 6, 9, cx + 30, 12)
        lz.sombrear(tabla, MADERA[2:], 1, LUZ, textura=vetas(lz, 0.5, 9), fuerza_tex=0.35)
        for x in (cx + 7, cx + 13, cx + 19, cx + 25, cx + 29):
            lz.sombrear(lz.trazo([(x, 10), (x, 3)], 0.8), MADERA[2:], 0.5, LUZ)
        lz.sombrear(lz.trazo([(cx + 6, 3), (cx + 30, 3)], 0.8), MADERA[2:], 0.5, LUZ)
        mastil = lz.trazo([(cx - 8, 6), (cx - 8, -18)], 0.9)
        lz.sombrear(mastil, MADERA[2:], 0.5, LUZ)
        bandera = lz.poligono([(cx - 7.5, -18), (cx + 6, -15), (cx - 7.5, -11)])
        lz.sombrear(bandera, ["#1e5a3a", "#2e8a52", "#4ab870", "#8fe06a"], 1, LUZ)
        lz.sombrear(lz.trazo([(cx + 20, 6), (cx + 31, 0)], 1.3, 1.0), LATON, 0.6, LUZ)        # el catalejo
        # una escalerita de cuerda que baja por el sombrero
        for k in range(6):
            y = 14 + k * 5
            x = cx + 33 + k * 2.2
            lz.sombrear(lz.trazo([(x - 3, y), (x + 3, y + 1)], 0.6), MADERA[2:], 0.4, LUZ)
        lz.pintar(lz.trazo([(cx + 29, 12), (cx + 42, 44)], 0.35) + lz.trazo([(cx + 35, 12), (cx + 48, 44)], 0.35), "#80643c")
    # cosas delante: un buzón de seta, setitas y un saco de explorador
    if reconstruida:
        lz.sombrear(lz.trazo([(cx - 38, suelo), (cx - 38, 96)], 1.0), MADERA[2:], 0.5, LUZ)
        buzon = lz.elipse(cx - 38, 95, 5, 3.5)
        lz.sombrear(buzon, ROJO[2:], 1.5, LUZ)
        lz.pintar(lz.circulo(cx - 40, 94, 0.8), "#fff8ee")
        lz.pintar(rect(lz, cx - 36, 94, cx - 33, 95.4), "#efe0bf")
        saco = lz.poligono([(cx + 28, suelo), (cx + 27, 104), (cx + 30, 99), (cx + 36, 99), (cx + 38, 104), (cx + 37, suelo)])
        lz.sombrear(saco, ["#5a4630", "#8a7454", "#b8a07a", "#d8c49c"], 2, LUZ)
        lz.pintar(lz.trazo([(cx + 29, 101), (cx + 36, 101)], 0.7), "#47291c")
    for (x, y, r, col) in ((cx - 46, suelo, 3.2, ROJO), (cx - 50, suelo + 1, 2.2, ROJO), (cx + 44, suelo, 2.6, ["#5a3a20", "#a87040", "#d8a868"]),
                           (cx + 48, suelo + 1, 1.8, ROJO)):
        lz.sombrear(lz.trazo([(x, y), (x, y - r * 1.4)], r * 0.35), CREMA[2:], 0.5, LUZ)
        lz.sombrear(lz.elipse(x, y - r * 1.5, r, r * 0.6), col if reconstruida else GRIS_R, 0.8, LUZ)
    _hierba_pie(lz, cx - 54, cx + 54, suelo - 2, 1008, seco=not reconstruida)
    if not reconstruida:
        for k in range(6):                                           # escombros y trozos de sombrero
            x = cx - 40 + k * 16 + rng.uniform(-3, 3)
            lz.sombrear(lz.elipse(x, suelo - 1, 3.5, 1.6, rng.uniform(0, 180)), GRIS_R, 0.8, LUZ)
    return lz.sprite(contorno=0.4)


def taller(reconstruido):
    W, H = 152, 120
    lz = _lienzo(W, H, 26, 1101 + reconstruido)
    suelo = 116
    gris = not reconstruido
    PIE = PIEDRA_C if reconstruido else GRIS_R
    MAD = MADERA if reconstruido else ["#141414", "#222224", "#343436", "#4a4a4c", "#5e5e60", "#727274", "#8a8a8c"]
    lz.pintar(lz.desenfocar(lz.elipse(76, suelo, 70, 5), 2), "#0a0a06", 0.45)
    # la chimenea de la forja, a la izquierda (de piedra; humo y chispas si está encendida)
    chim = rect(lz, 14, 4 if reconstruido else 30, 30, suelo)
    piedras(lz, chim, tam=3.6, semilla=1102, luz=LUZ, mortero="#2a2622", rampa_p=PIE)
    if reconstruido:
        lz.sombrear(rect(lz, 12, 0, 32, 5), PIEDRA[2:], 1, LUZ)
        humo = np.zeros((lz.H, lz.W))
        for k in range(7):
            humo = np.maximum(humo, lz.circulo(22 + k * 3 + np.sin(k) * 3, -2 - k * 3.4, 3.5 + k * 0.9))
        lz.pintar(lz.desenfocar(humo, 1.5), "#9a9490", 0.55)
        for (x, y) in ((20, -6), (26, -12), (18, -16), (28, -4)):
            lz.pintar(lz.circulo(x, y, 0.5), "#ffb050")
            lz.sumar_luz(lz.desenfocar(lz.circulo(x, y, 0.8), 1.5), "#ff8a30", 0.6)
        boca = lz.poligono([(17, 100), (17, 92), (22, 88), (27, 92), (27, 100)])
        lz.pintar(boca, rampa(["#a8380f", "#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - (100 - lz.y) / 12, 0, 1)))
        lz.sumar_luz(lz.desenfocar(boca, 5), "#ef8a26", 0.55)
    else:
        for (x, y) in ((16, 28), (24, 26), (29, 29)):
            lz.sombrear(lz.elipse(x, y, 2.4, 1.5), GRIS_R, 0.6, LUZ)
    # el cuerpo del taller: abajo piedra, arriba entramado de madera y yeso
    abajo = rect(lz, 30, 74, 118, suelo)
    piedras(lz, abajo, tam=5.0, semilla=1103, luz=LUZ, mortero="#2a2622", rampa_p=PIE)
    arriba = rect(lz, 30, 44, 118, 74)
    lz.sombrear(arriba, (CREMA if reconstruido else GRIS_R), 6, LUZ, textura=lz.ruido(0.8, 2, semilla=1104), fuerza_tex=0.2)
    for x in (30, 52, 74, 96, 116):
        lz.sombrear(rect(lz, x, 44, x + 2.5, 74), MAD[1:], 0.8, LUZ, textura=vetas(lz, 0.5, 9, False), fuerza_tex=0.3)
    lz.sombrear(rect(lz, 30, 58, 118, 60.5), MAD[1:], 0.8, LUZ, textura=vetas(lz, 0.5, 13), fuerza_tex=0.3)
    for (a, b) in (((33, 46), (50, 57)), ((99, 57), (114, 46))):
        lz.sombrear(lz.trazo([a, b], 1.6), MAD[1:], 0.6, LUZ)
    lz.sombrear(rect(lz, 28, 72, 120, 75), MAD[1:], 0.8, LUZ, textura=vetas(lz, 0.5, 13), fuerza_tex=0.3)
    # ventana con el resplandor de la forja (o rota)
    if reconstruido:
        ventana(lz, 58, 48, 72, 56, encendida=0.75, contras=False, semilla=1105, luz=LUZ)
        ventana(lz, 80, 48, 92, 56, encendida=0.6, contras=False, semilla=1106, luz=LUZ)
    else:
        for (a, b) in ((58, 72), (80, 92)):
            lz.pintar(rect(lz, a, 48, b, 56), "#121212")
    # el tejado de tablillas
    if reconstruido:
        tej = lz.poligono([(22, 46), (52, 18), (96, 18), (126, 46)])
    else:
        tej = lz.poligono([(22, 46), (52, 18), (66, 18), (74, 30), (84, 26), (96, 34), (126, 46)])
    tab = ((lz.y - 18) % 4 < 0.6) * 1.0 + (np.abs(np.sin((lz.x + np.floor((lz.y - 18) / 4) * 2.3) * 0.8)) < 0.07) * 1.0
    lz.sombrear(tej, ["#2a160e", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259"] if reconstruido else GRIS_R,
                6, LUZ, textura=1 - np.clip(tab, 0, 1) * 0.7 + vetas(lz, 0.5, 7) * 0.3, fuerza_tex=0.5)
    musgo = (lz.ruido(2.0, 3, semilla=1107) > 0.68) * tej
    lz.pintar(lz.desenfocar(musgo, 0.5), rampa(["#2a3a1e", "#3e5228", "#566c34"], lz.ruido(0.6, 2)), 0.6 if reconstruido else 0.3)
    lz.sombrear(rect(lz, 20, 45, 128, 48), MAD[1:], 1, LUZ, textura=vetas(lz, 0.5, 13), fuerza_tex=0.35)
    if not reconstruido:
        lz.pintar(lz.poligono([(66, 20), (74, 30), (84, 28), (80, 40), (70, 38)]), "#0e0e10")
        for (a, b) in (((64, 22), (84, 36)), ((70, 20), (78, 40))):
            lz.sombrear(lz.trazo([a, b], 1.6), MAD[1:], 0.6, LUZ)
    # el portalón de madera (doble, en arco), con herrajes
    pu = lz.poligono([(58, suelo - 1), (58, 90)] + [(70 + np.cos(a) * 12, 90 - np.sin(a) * 8) for a in np.linspace(np.pi, 0, 20)] + [(82, 90), (82, suelo - 1)])
    marco = np.clip(lz.poligono([(56, suelo), (56, 90)] + [(70 + np.cos(a) * 14, 90 - np.sin(a) * 10) for a in np.linspace(np.pi, 0, 20)] + [(84, 90), (84, suelo)]) - pu, 0, 1)
    lz.sombrear(marco, PIE, 1, LUZ)
    tablas = (np.abs(np.sin((lz.x - 58) / 4 * np.pi)) < 0.1).astype(float)
    if reconstruido:
        lz.sombrear(pu, ["#251812", "#3d2418", "#5a3826", "#7a4e35", "#9a6847"], 5, LUZ, textura=vetas(lz, 0.5, 15, False) * (1 - tablas * 0.8), fuerza_tex=0.45)
        lz.pintar(rect(lz, 69.6, 84, 70.4, suelo - 1), "#140c08")
        for y in (94, 108):
            lz.sombrear(rect(lz, 59, y - 0.8, 69, y + 0.8), ["#1b1c1f", "#3d3f43", "#6a6c6f"], 0.5, LUZ)
            lz.sombrear(rect(lz, 71, y - 0.8, 81, y + 0.8), ["#1b1c1f", "#3d3f43", "#6a6c6f"], 0.5, LUZ)
        for x in (67, 73):
            lz.sombrear(lz.circulo(x, 101, 1.1), ["#1b1c1f", "#6a6c6f", "#a3a4a6"], 0.5, LUZ)
    else:
        lz.pintar(pu, "#0c0a0a")
        lz.sombrear(lz.poligono([(58, 98), (66, 96), (67, suelo), (58, suelo)]), MAD[1:], 0.8, LUZ)
    # el cartel de Corteza: una tabla colgada con su marca (un martillo sobre un yunque)
    if reconstruido:
        lz.sombrear(lz.trazo([(84, 70), (100, 70)], 1.2), MAD[2:], 0.5, LUZ)
        for x in (88, 96):
            lz.pintar(lz.trazo([(x, 70), (x, 74)], 0.4), "#3d3f43")
        cart = rect(lz, 85, 74, 99, 84)
        lz.sombrear(cart, MADERA[2:], 1, LUZ, textura=vetas(lz, 0.5, 9), fuerza_tex=0.35)
        lz.pintar(rect(lz, 88, 80, 96, 81.5) + rect(lz, 90, 81.5, 94, 83), "#1a120c")
        lz.pintar(lz.trazo([(91, 78.6), (95, 76)], 0.6) + lz.trazo([(94, 75), (96.4, 77)], 1.0), "#e6a852")
    # el cobertizo de la derecha: el yunque sobre su tocón, herraduras colgadas, la muela de afilar y el barril
    techo = lz.poligono([(116, 72), (148, 80), (148, 84), (116, 76)])
    lz.sombrear(techo, MAD[1:], 1, LUZ, textura=vetas(lz, 0.5, 9), fuerza_tex=0.4)
    for x in (122, 144):
        lz.sombrear(lz.trazo([(x, 76 + (x - 116) * 0.25), (x, suelo)], 1.4), MAD[1:], 0.6, LUZ)
    toc = lz.elipse(132, 109, 6, 6)
    lz.sombrear(toc, MAD, 2, LUZ, textura=vetas(lz, 0.5, 9, False), fuerza_tex=0.4)
    yun = lz.poligono([(124, 101), (140, 101), (138, 104), (134, 104), (134, 107), (130, 107), (130, 104), (126, 104)])
    lz.sombrear(yun, ["#1b1c1f", "#2e3034", "#4a4c50", "#6a6c6f", "#9a9c9f"], 1, LUZ)
    lz.pintar(lz.trazo([(124, 101), (140, 101)], 0.5), "#c8cacd" if reconstruido else "#6a6c6f")
    if reconstruido:
        for (x, y) in ((126, 86), (132, 87), (138, 88)):
            her = np.clip(lz.circulo(x, y + 2, 2.2) - lz.circulo(x, y + 2, 1.3), 0, 1) * (lz.y > y + 1)
            lz.sombrear(her, ["#2e3034", "#6a6c6f", "#a3a4a6"], 0.5, LUZ)
        muela = lz.circulo(146, 104, 6)
        lz.sombrear(muela, ["#4a4440", "#6e665e", "#958b80", "#bfb4a6"], 2, LUZ)
        lz.pintar(lz.circulo(146, 104, 1), "#2a1a12")
        lz.sombrear(lz.trazo([(146, 104), (152, 98)], 0.8), MADERA[2:], 0.4, LUZ)
        barril = lz.elipse(42, 108, 6, 7.5)
        duelas = (np.abs(np.sin((lz.x - 42) / 2.2 * np.pi)) < 0.12).astype(float)
        lz.sombrear(barril, TRONCO, 3, LUZ, textura=1 - duelas * 0.7, fuerza_tex=0.4)
        lz.pintar(lz.elipse(42, 101.5, 5, 1.4), "#1e3a48")
        lz.pintar(lz.elipse(41, 101.2, 2, 0.5), "#6a9ab0")
        lz.sombrear(lz.trazo([(44, 96), (47, 108)], 0.6) + lz.trazo([(46, 96), (48, 108)], 0.6), ["#1b1c1f", "#3d3f43", "#6a6c6f"], 0.4, LUZ)
        for k in range(5):                                            # mineral y barras de hierro
            lz.sombrear(lz.elipse(100 + k * 3, suelo - 2 - (k % 2), 2.2, 1.6), ["#2a2a3a", "#4a4a6a", "#8a8ab0", "#c8c8e8"], 0.6, LUZ)
    else:
        for k in range(8):
            x = 36 + k * 13
            lz.sombrear(lz.elipse(x, suelo - 1, 4, 1.8, k * 23), GRIS_R, 0.8, LUZ)
    _hierba_pie(lz, 8, 150, suelo - 2, 1108, seco=gris)
    return lz.sprite(contorno=0.4)


JUNCO = ["#2a2410", "#4a4018", "#6e6024", "#958434", "#b8a64a", "#d8c86a", "#efe2a0"]


def cocina(reconstruida):
    W, H = 132, 104
    lz = _lienzo(W, H, 24, 1201 + reconstruida)
    suelo = 100
    cx = 62
    J = JUNCO if reconstruida else GRIS_R + ["#c2c2c4"]
    MAD = MADERA if reconstruida else ["#141414", "#222224", "#343436", "#4a4a4c", "#5e5e60", "#727274", "#8a8a8c"]
    lz.pintar(lz.desenfocar(lz.elipse(cx + 4, suelo, 60, 5), 2), "#0a0a06", 0.45)
    # las paredes: haces de juncos atados, verticales
    pared = rect(lz, cx - 36, 52, cx + 36, suelo)
    haces = (np.abs(np.sin((lz.x - cx) / 3.2 * np.pi)) < 0.18).astype(float)
    lz.sombrear(pared, J, 6, LUZ, textura=vetas(lz, 0.4, 13, False, semilla=1202) * (1 - haces * 0.6), fuerza_tex=0.5)
    for y in (64, 84):
        lz.sombrear(rect(lz, cx - 36, y - 1, cx + 36, y + 1), MAD[1:], 0.6, LUZ)
    # el mostrador abierto en el centro (dentro, la oscuridad y los estantes con tarros)
    hueco = rect(lz, cx - 20, 60, cx + 20, 80)
    lz.pintar(hueco, "#1a120c" if reconstruida else "#0e0e0e")
    if reconstruida:
        lz.sumar_luz(lz.desenfocar(hueco, 4) * hueco, "#ef8a26", 0.25)
        for k in range(6):
            x = cx - 16 + k * 6.4
            lz.sombrear(lz.elipse(x, 67, 2, 2.6), [["#5a2a6a", "#9a4ab0", "#d08ae0"], ["#6a4a10", "#b07a1a", "#f0c050"], ["#2a5a3a", "#4a9a5a", "#8ae08a"]][k % 3], 0.8, LUZ)
        lz.sombrear(rect(lz, cx - 19, 70, cx + 19, 71.5), MADERA[2:], 0.5, LUZ)
        for (x, r) in ((cx - 10, 4.5), (cx + 2, 3.6), (cx + 12, 4)):                     # ollas colgadas
            lz.pintar(lz.trazo([(x, 60), (x, 63)], 0.4), "#2a2a2a")
            lz.sombrear(lz.elipse(x, 64 + r * 0.6, r, r * 0.7), ["#1b1c1f", "#3d3f43", "#6a6c6f", "#a3a4a6"] if x != cx + 2 else COBRE[2:], 1, LUZ)
    mostr = rect(lz, cx - 24, 78, cx + 24, 84)
    lz.sombrear(mostr, MAD, 2, LUZ, textura=vetas(lz, 0.5, 15, semilla=1203), fuerza_tex=0.4)
    if reconstruida:
        for (x, col) in ((cx - 18, ["#3a1a4a", "#7a3a9a", "#c070e0"]), (cx + 16, ["#5a4a10", "#a08a20", "#e0c860"])):
            cesto = lz.elipse(x, 77, 5, 3)
            lz.sombrear(cesto, COBRE[1:], 1, LUZ, textura=((lz.x + lz.y) % 1.6 < 0.6) * 1.0, fuerza_tex=0.4)
            for k in range(5):
                lz.sombrear(lz.circulo(x - 3 + k * 1.5, 74.5 - (k % 2), 1.1), col, 0.5, LUZ)
        lz.sombrear(lz.elipse(cx, 76, 4, 1.4), ["#8a7a5a", "#d8c8a0", "#fff6e0"], 0.6, LUZ)                 # un cuenco
    else:
        lz.sombrear(lz.trazo([(cx - 22, 78), (cx + 4, 86)], 2.0), MAD[1:], 0.6, LUZ)
    # el tejado de paja redondo, con la punta atada
    if reconstruida:
        tej = lz.poligono([(cx - 46, 58), (cx - 30, 30), (cx - 10, 12), (cx, 6), (cx + 10, 12), (cx + 30, 30), (cx + 46, 58), (cx, 62)])
    else:
        tej = lz.poligono([(cx - 46, 62), (cx - 30, 40), (cx - 14, 30), (cx - 2, 38), (cx + 10, 30), (cx + 28, 42), (cx + 46, 62), (cx, 64)])
    paja(lz, tej, semilla=1204, capas=5.0, y0=6, oscuro=0.0 if reconstruida else 0.0)
    if not reconstruida:
        lz.pintar(tej, "#7a7a7c", 0.75)
    flecos(lz, cx - 44, cx + 44, 59 if reconstruida else 62, 3.0, semilla=1205)
    if reconstruida:
        lz.sombrear(lz.trazo([(cx - 3, 8), (cx + 3, 8)], 2.2), COBRE[2:], 0.5, LUZ)
        lz.sombrear(lz.trazo([(cx, 6), (cx + 1, -2)], 1.6, 0.8), J, 0.5, LUZ)
    # ristras de hierbas y ajos colgando del alero
    if reconstruida:
        for x in (cx - 32, cx - 27, cx + 28, cx + 33):
            lz.pintar(lz.trazo([(x, 58), (x, 62)], 0.4), "#2a1a12")
            m_ = lz.trazo([(x, 62), (x - 1.4, 68)], 1.2) + lz.trazo([(x, 62), (x + 1.2, 68.5)], 1.2)
            lz.sombrear(np.clip(m_, 0, 1), ["#24401f", "#5d793e", "#8aa152"], 0.6, LUZ)
    # el caldero al fuego, delante a la izquierda (con vapor), y un barreño con un nenúfar
    if reconstruida:
        kx = cx - 44
        for (a, b) in (((kx - 11, 99), (kx, 76)), ((kx + 11, 99), (kx, 76)), ((kx - 2, 99), (kx, 76))):
            lz.sombrear(lz.trazo([a, b], 1.1), MADERA[2:], 0.4, LUZ)
        lz.pintar(lz.trazo([(kx, 77), (kx, 82)], 0.5), "#2a2a2a")
        cal = lz.elipse(kx, 88, 8.5, 6.5)
        lz.sombrear(cal, ["#141416", "#2a2a2e", "#46464c", "#6e6e74", "#9a9aa2"], 2.5, LUZ)
        lz.pintar(lz.elipse(kx, 83, 7.4, 2.0), "#5a8a2a")
        lz.pintar(lz.elipse(kx - 2, 82.6, 2.4, 0.7), "#a8d060")
        fuego = lz.poligono([(kx - 8, 99), (kx - 5, 92), (kx - 2, 96), (kx, 90), (kx + 3, 95), (kx + 5, 91), (kx + 8, 99)])
        lz.pintar(fuego, rampa(["#a8380f", "#ef8a26", "#f9b947", "#fde27e"], np.clip((99 - lz.y) / 8, 0, 1)))
        lz.sumar_luz(lz.desenfocar(fuego, 6), "#ef8a26", 0.6)
        for k in range(4):
            lz.sombrear(lz.elipse(kx - 6 + k * 4, 99, 2.4, 1.0), MADERA[1:], 0.4, LUZ)
        vapor = np.zeros((lz.H, lz.W))
        for k in range(7):
            vapor = np.maximum(vapor, lz.circulo(kx + np.sin(k * 1.3) * 3, 78 - k * 5, 2.6 + k * 0.7))
        lz.pintar(lz.desenfocar(vapor, 1.2), "#f0f0e8", 0.5)
        bar = lz.elipse(cx + 40, 95, 8, 4.5)
        lz.sombrear(bar, TRONCO, 2, LUZ)
        lz.pintar(lz.elipse(cx + 40, 93.4, 6.4, 2.4), "#2a5a5a")
        lz.pintar(lz.elipse(cx + 39, 93.4, 3, 1.2), "#4a8a3a")
        lz.pintar(lz.circulo(cx + 41, 93, 0.9), "#f4b0c0")
    else:
        olla = lz.elipse(cx - 34, 95, 6, 4, -30)
        lz.sombrear(olla, GRIS_R, 1.5, LUZ)
        lz.pintar(lz.elipse(cx - 28, 98, 5, 1.4), "#3a3a3a", 0.8)
    _hierba_pie(lz, cx - 50, cx + 50, suelo - 2, 1206, seco=not reconstruida)
    for (x, y) in ((cx + 48, suelo), (cx - 52, suelo + 1)):
        if reconstruida:
            lz.sombrear(lz.trazo([(x, y), (x + 1, y - 9)], 0.6), ["#4a4018", "#958434", "#d8c86a"], 0.4, LUZ)
            lz.sombrear(lz.elipse(x + 1, y - 10, 0.8, 2.2), ["#5a3a1a", "#8a5a2a"], 0.4, LUZ)
    return lz.sprite(contorno=0.4)


def puesto(reconstruido):
    W, H = 116, 92
    lz = _lienzo(W, H, 12, 1301 + reconstruido)
    suelo = 88
    cx = 58
    MAD = MADERA if reconstruido else ["#141414", "#222224", "#343436", "#4a4a4c", "#5e5e60", "#727274", "#8a8a8c"]
    lz.pintar(lz.desenfocar(lz.elipse(cx, suelo, 54, 5), 2), "#0a0a06", 0.45)
    # los postes y el toldo a rayas (rojo y crema; en ruinas, jirones grises)
    for x in (cx - 44, cx + 44):
        lz.sombrear(lz.trazo([(x, suelo), (x, 18)], 2.0, 1.6), MAD[1:], 0.8, LUZ, textura=vetas(lz, 0.5, 9, False), fuerza_tex=0.3)
    if reconstruido:
        tol = lz.poligono([(cx - 50, 26), (cx - 40, 8), (cx + 40, 8), (cx + 50, 26)])
        rayas = (np.floor((lz.x - cx + 50) / 10) % 2).astype(float)
        col = rampa(["#5e1218", "#b42a2c", "#ec6a58"], lz.ruido(0.8, 2)) * rayas[..., None] + rampa(["#b8a27c", "#f0e2c0", "#fff6e0"], lz.ruido(0.8, 2)) * (1 - rayas[..., None])
        sombra = np.clip((lz.y - 8) / 18, 0, 1)[..., None]
        lz.pintar(tol, col * (1 - sombra * 0.3))
        for k in range(10):                                               # el volante de abajo, en ondas
            x0 = cx - 50 + k * 10
            onda = lz.elipse(x0 + 5, 26, 5, 3) * (lz.y > 26)
            lz.pintar(onda, "#b42a2c" if k % 2 == 0 else "#f0e2c0")
        lz.pintar(lz.trazo([(cx - 40, 8), (cx + 40, 8)], 1.0), "#5e1218")
        for (x, col_) in ((cx - 30, "#f9b947"), (cx, "#f9b947"), (cx + 30, "#f9b947")):     # farolillos
            lz.pintar(lz.trazo([(x, 29), (x, 32)], 0.4), "#2a1a12")
            f = lz.elipse(x, 35, 2.4, 3)
            lz.pintar(f, rampa(["#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - x, lz.y - 35) / 3, 0, 1)))
            lz.sumar_luz(lz.desenfocar(f, 4), "#ef8a26", 0.3)
    else:
        for k in range(5):
            x0 = cx - 46 + k * 19
            jir = lz.poligono([(x0, 10), (x0 + 12, 10), (x0 + 10 - k % 2 * 3, 26 + k % 3 * 4), (x0 + 3, 22)])
            lz.sombrear(jir, GRIS_R, 1.5, LUZ)
        lz.sombrear(lz.trazo([(cx - 44, 10), (cx + 44, 12)], 1.2), MAD[1:], 0.5, LUZ)
    # el mostrador de tablas, con su frontal
    if reconstruido:
        mostr = rect(lz, cx - 40, 56, cx + 40, 60)
        frente = rect(lz, cx - 38, 60, cx + 38, suelo - 2)
    else:
        mostr = lz.poligono([(cx - 40, 58), (cx - 4, 56), (cx + 2, 66), (cx + 40, 62), (cx + 40, 66), (cx - 40, 62)])
        frente = rect(lz, cx - 38, 64, cx + 38, suelo - 2)
    tabl = (np.abs(np.sin((lz.x - cx) / 6 * np.pi)) < 0.08).astype(float)
    lz.sombrear(frente, MAD, 3, LUZ, textura=vetas(lz, 0.5, 13, False, semilla=1302) * (1 - tabl * 0.7), fuerza_tex=0.45)
    lz.sombrear(mostr, MAD[1:], 1.5, LUZ, textura=vetas(lz, 0.5, 15), fuerza_tex=0.35)
    if reconstruido:
        # el cartel con una pluma
        cart = rect(lz, cx - 12, 64, cx + 12, 74)
        lz.sombrear(cart, CREMA[2:], 1, LUZ)
        pl = lz.trazo(lz.curva((cx - 7, 72), (cx - 2, 66), (cx + 8, 66)), 1.4, 0.4)
        lz.sombrear(pl, ["#1e4a7a", "#2e7ab0", "#6ac0e8", "#c8f0ff"], 0.6, LUZ)
        # la mercancía: cristales del Nexo en un expositor, frascos, una balanza, rollos de tela y plumas
        for k in range(4):
            x = cx - 32 + k * 5
            cri = lz.poligono([(x, 56), (x - 1.8, 52), (x, 47 - k % 2 * 2), (x + 1.8, 52)])
            lz.sombrear(cri, ["#3a2a6a", "#6a4ab0", "#a888e8", "#e8d8ff"], 0.6, LUZ)
            lz.brillo(cri, "#a888e8", 1.5, 0.5)
        for (x, col) in ((cx - 8, ["#2a5a3a", "#4a9a5a", "#8ae08a"]), (cx - 2, ["#6a2a2a", "#b04a4a", "#f08a8a"])):
            lz.sombrear(lz.elipse(x, 52, 2.4, 3.4), col, 0.8, LUZ)
            lz.pintar(rect(lz, x - 1, 47.5, x + 1, 49), "#8a6440")
        bal = lz.trazo([(cx + 12, 56), (cx + 12, 46)], 0.6)
        lz.pintar(bal, "#c89a44")
        lz.pintar(lz.trazo([(cx + 6, 47), (cx + 18, 47)], 0.5), "#c89a44")
        for x in (cx + 6, cx + 18):
            lz.sombrear(lz.elipse(x, 50, 2.6, 0.9), LATON[2:], 0.5, LUZ)
        for k in range(3):
            lz.sombrear(lz.elipse(cx + 28 + k * 2, 53 - k * 2.2, 5, 1.8), [["#1e4a7a", "#2e7ab0", "#6ac0e8"], ["#5a3a1a", "#a87040", "#e0b070"], ["#3a5a1a", "#6a9a3a", "#a8d060"]][k], 0.8, LUZ)
        for k, colp in enumerate(("#d84a4a", "#4a9ad8", "#e8c040")):
            lz.pintar(lz.trazo(lz.curva((cx + 36 + k * 2, 44), (cx + 33 + k * 2, 40), (cx + 35 + k * 2, 35)), 0.9, 0.3), colp)
    else:
        rng = np.random.default_rng(1303)
        for k in range(6):
            lz.sombrear(lz.elipse(cx - 34 + k * 13, suelo - 1, 3.5, 1.6, rng.uniform(0, 180)), GRIS_R, 0.7, LUZ)
        for k in range(4):
            lz.pintar(lz.trazo([(cx - 20 + k * 9, 60), (cx - 23 + k * 9, 64)], 0.5), ["#8a8a8c", "#a0a0a2"][k % 2])
    # cajas y un saco delante
    if reconstruido:
        caja = rect(lz, cx + 40, 72, cx + 54, suelo - 1)
        lz.sombrear(caja, COBRE, 2, LUZ, textura=vetas(lz, 0.5, 11), fuerza_tex=0.35)
        lz.pintar(rect(lz, cx + 40, 79.4, cx + 54, 80.2) + rect(lz, cx + 46.6, 72, cx + 47.4, suelo - 1), "#47291c", 0.85)
        for k in range(3):
            lz.sombrear(lz.circulo(cx + 43 + k * 4, 71, 1.8), [["#8f2532", "#d5525e", "#f4b39a"], ["#b2721a", "#df9022", "#fde27e"], ["#3e6a2a", "#6fa04a", "#b4c070"]][k], 0.6, LUZ)
        saco = lz.poligono([(cx - 54, suelo - 1), (cx - 55, 78), (cx - 52, 73), (cx - 46, 73), (cx - 43, 78), (cx - 44, suelo - 1)])
        lz.sombrear(saco, ["#5a4630", "#8a7454", "#b8a07a", "#d8c49c"], 2, LUZ)
    _hierba_pie(lz, cx - 54, cx + 54, suelo - 2, 1304, seco=not reconstruido)
    return lz.sprite(contorno=0.4)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    tira = lambda fotos: Image.fromarray(np.concatenate(fotos, axis=1), "RGBA")
    tira([casa_seta(False), casa_seta(True)]).save(os.path.join(SALIDA, "casa_seta.png"))
    tira([taller(False), taller(True)]).save(os.path.join(SALIDA, "taller.png"))
    tira([cocina(False), cocina(True)]).save(os.path.join(SALIDA, "cocina.png"))
    tira([puesto(False), puesto(True)]).save(os.path.join(SALIDA, "puesto.png"))
    print("Cuna de Musgo pintada en", SALIDA)


if __name__ == "__main__":
    main()
