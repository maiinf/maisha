"""Ilustraciones del Campo Segado (con el pintor de las cinemáticas; se pintan junto a las demás):

    python3 herramientas/cinematicas.py 11_cosecha_libre

  11_cosecha_libre   La Cosechadora, apagada para siempre, en medio de un mar de trigo dorado que acaba de crecer.
                     Las enredaderas y las flores le suben por la chapa; de la chimenea se escapa el último humo violeta
                     de Giza y se deshace en el cielo del atardecer. El molino vuelve a girar al fondo. Maisha la mira
                     desde el trigo, con el cetro.
"""
import math

import numpy as np

from pintor import Lienzo, rampa  # noqa: F401
import cinematicas as ci

W, H = ci.W, ci.H
LUZ = (0.7, -0.5, 0.5)              # el sol de la tarde, bajo, a la derecha
HORIZONTE = 120
TRIGO = ["#3d2a10", "#704f25", "#a37036", "#d29a43", "#efc06a", "#f8dc96", "#fff1c8"]
OXIDO = ["#1f0e08", "#3a1a0e", "#5a2a14", "#7a3a1c", "#9c4f24", "#bd6a34", "#d88a4c", "#eab07a"]
CHAPA = ["#16171a", "#26272b", "#3a3c40", "#55575c", "#74767a", "#9a9c9e", "#c2c3c4"]
VERDE = ["#1f2d17", "#2f4422", "#3f5a2f", "#5d793e", "#7c9a4c", "#a8b866"]


def _espigas(lz, n, zona, semilla, escala=1.0, delante=False):
    """Espigas de trigo: tallos finos con la espiga gruesa arriba, más grandes cuanto más cerca."""
    rng = np.random.default_rng(semilla)
    x0, y0, x1, y1 = zona
    for _ in range(n):
        x, y = x0 + rng.random() * (x1 - x0), y0 + rng.random() * (y1 - y0)
        e = escala * (0.4 + (y - y0) / max(1, (y1 - y0)) * 1.2)
        alto = (10 + rng.random() * 8) * e
        incl = (rng.random() - 0.3) * 4 * e
        lz.pintar(lz.trazo([(x, y), (x + incl * 0.5, y - alto * 0.6), (x + incl, y - alto)], 0.5 * e, 0.3 * e),
                  TRIGO[2] if not delante else TRIGO[1])
        esp = lz.elipse(x + incl, y - alto - 2.5 * e, 1.1 * e, 3.2 * e, 10 + incl * 8)
        lz.sombrear(esp, TRIGO[1:] if not delante else TRIGO[:6], 1.0 * e, LUZ)


def _cosechadora(lz, x, y, e):
    """La Cosechadora apagada, de lado, mirando a la izquierda (hacia Maisha), cubierta de enredaderas."""
    def X(dx):
        return x - dx * e
    def Y(dy):
        return y - dy * e
    tex = lz.ruido(6, 3, semilla=71)
    lz.pintar(lz.desenfocar(lz.elipse(x, y, 52 * e, 4 * e), 2), "#2a1c10", 0.6)
    # caldera (detrás, a la derecha porque mira a la izquierda)
    cal = np.maximum(lz.elipse(X(-36), Y(26), 14 * e, 17 * e), lz.poligono([(X(-36), Y(43)), (X(-24), Y(43)), (X(-24), Y(9)), (X(-36), Y(9))]))
    lz.sombrear(cal, OXIDO, 10 * e, LUZ, textura=tex, fuerza_tex=0.25, recorte=("#ffd98a", 0.7), recorte_dir=(1, -0.6))
    lz.sombrear(lz.elipse(X(-38), Y(26), 6 * e, 7 * e), CHAPA, 3 * e, LUZ)
    # cuerpo
    cuerpo = np.maximum(lz.poligono([(X(-26), Y(46)), (X(22), Y(46)), (X(22), Y(10)), (X(-26), Y(10))]), lz.elipse(X(-2), Y(46), 24 * e, 6 * e))
    lz.sombrear(cuerpo, OXIDO, 14 * e, LUZ, textura=tex, fuerza_tex=0.25, recorte=("#ffd98a", 0.7), recorte_dir=(1, -0.8),
                rebote=("#3a1a0e", 0.35))
    for (a, b, c_, d) in ((-22, 42, -6, 28), (-4, 42, 18, 28), (-22, 25, 0, 13), (2, 25, 18, 13)):
        placa = lz.poligono([(X(a), Y(b)), (X(c_), Y(b)), (X(c_), Y(d)), (X(a), Y(d))])
        lz.sombrear(placa, CHAPA if (a + b) % 3 else OXIDO, 3 * e, LUZ, textura=tex, fuerza_tex=0.3)
    # chimenea (con el último humo de Giza) y tolva
    chim = lz.poligono([(X(-12), Y(66)), (X(-6), Y(66)), (X(-6), Y(46)), (X(-12), Y(46))])
    lz.sombrear(chim, CHAPA, 2.5 * e, LUZ)
    lz.sombrear(lz.poligono([(X(2), Y(48)), (X(4), Y(58)), (X(16), Y(58)), (X(18), Y(48))]), CHAPA, 3 * e, LUZ)
    # ruedas
    for (cx, cy, r) in ((-10, 12, 13), (20, 7, 7)):
        aro = np.clip(lz.elipse(X(cx), Y(cy), r * e, r * e) - lz.elipse(X(cx), Y(cy), (r - 2.4) * e, (r - 2.4) * e), 0, 1)
        lz.sombrear(aro, OXIDO, 1.6 * e, LUZ)
        for k in range(8):
            a = k * math.pi / 4 + 0.2
            lz.pintar(lz.trazo([(X(cx), Y(cy)), (X(cx) + math.cos(a) * (r - 2) * e, Y(cy) + math.sin(a) * (r - 2) * e)], 1.0 * e, 0.8 * e), OXIDO[3])
    # el molinete parado, con las palas caídas
    mx, my = X(36), Y(26)
    for k in range(6):
        a = 0.3 + k * math.pi / 3
        px, py = mx + math.cos(a) * 14 * e, my + math.sin(a) * 14 * e
        lz.sombrear(lz.trazo([(mx, my), (px, py)], 1.4 * e, 1.1 * e), OXIDO, 0.8 * e, LUZ)
        t = (-math.sin(a), math.cos(a))
        lz.sombrear(lz.trazo([(px - t[0] * 4 * e, py - t[1] * 4 * e), (px + t[0] * 4 * e, py + t[1] * 4 * e)], 2.4 * e, 2.4 * e),
                    ["#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259"], 1.0 * e, LUZ)
    lz.sombrear(lz.trazo([(X(18), Y(4)), (X(52), Y(2))], 2.4 * e, 2.4 * e), CHAPA, 1.2 * e, LUZ)
    # faros apagados
    for dy in (34, 27):
        lz.sombrear(lz.circulo(X(24), Y(dy), 2.6 * e), CHAPA, 1.2 * e, LUZ)
    # enredaderas que suben por la chapa, con flores, y espigas que asoman por todas partes
    rng = np.random.default_rng(73)
    for k in range(16):
        bx = X(-30 + k * 4.4)
        alto = (22 + (k % 5) * 7) * e
        pts = [(bx + math.sin(j * 1.3 + k) * 3.5 * e, y - alto * j / 5) for j in range(6)]
        lz.sombrear(lz.trazo(pts, 1.2 * e, 0.5 * e), VERDE, 0.8 * e, LUZ)
        pts = [pts[2], pts[4], pts[5]]
        for (hx, hy) in pts[1:]:
            lz.sombrear(lz.elipse(hx + 2 * e, hy, 2.6 * e, 1.3 * e, 20 + k * 25), VERDE[2:], 1 * e, LUZ)
        if k % 2 == 0:
            fx, fy = pts[-1]
            col = ["#f4b39a", "#fff3c4", "#e6a852", "#de6771"][k % 4]
            for p in range(5):
                a = p * 2 * math.pi / 5
                lz.pintar(lz.circulo(fx + math.cos(a) * 1.6 * e, fy - 1.5 * e + math.sin(a) * 1.6 * e, 1.1 * e), col)
            lz.pintar(lz.circulo(fx, fy - 1.5 * e, 0.7 * e), "#e6a852")
    # el último humo violeta, que se deshace hacia el cielo
    for k in range(10):
        hx, hy = X(-9) + k * 5 * e + math.sin(k * 1.4) * 5, Y(70) - k * 6 * e
        r = (2.5 + k * 1.1) * e
        lz.pintar(lz.desenfocar(lz.circulo(hx, hy, r), 1.5 + k * 0.6), "#8f3ec0", max(0.0, 0.45 - k * 0.045))


def cosecha_libre():
    """«La caldera se apaga con un último suspiro de humo violeta... En un instante, el Campo Segado se cubre
    de trigo dorado, como si hubiera estado esperando todo este tiempo.»"""
    lz = Lienzo(W, H, semilla=111)
    # cielo de la tarde: azul arriba, dorado y rosado junto al horizonte (el sol a la derecha)
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#3b5b78", "#6f8fa8", "#c9b6a0", "#f2c890", "#f8dfb0"], desde=0, hasta=HORIZONTE))
    calido = np.clip(1 - np.hypot((lz.x - 520) / 280, (lz.y - HORIZONTE) / 110), 0, 1)
    lz.sumar_luz(calido ** 1.5, "#ffc878", 0.6)
    lz.sumar_luz(lz.desenfocar(lz.circulo(530, HORIZONTE - 14, 12), 4), "#fff6dc", 0.95)
    ci.cumulos(lz, [(120, 40, 70, 10), (250, 26, 60, 8), (420, 52, 80, 11), (560, 30, 50, 7)], luz=(1, -0.4),
               colores=("#8d7f90", "#c9a6a0", "#f2c8a0", "#fff1d6"), semilla=112, alfa=0.85, suave=1.0)
    # colinas lejanas con campos, en la neblina de la tarde
    lejos = ci.mascara_bajo(lz, ci.linea_horizonte(lz, HORIZONTE - 6, 6, 200, 113))
    lz.pintar(lejos, "#8a8a62")
    ci.campos(lz, HORIZONTE - 4, HORIZONTE + 14, semilla=114,
              colores=[["#9c7a2a", "#c9a046", "#e8c56a"], ["#7c8a4c", "#a8b866", "#c8cc8a"], ["#b08a3a", "#d6b05a", "#f0d27a"]])
    lz.pintar(np.clip((lz.y - (HORIZONTE - 20)) / 40, 0, 1) * (lz.y < HORIZONTE + 16), "#f6dcb0", 0.35)
    # el molino al fondo, girando otra vez
    mx, my = 150, HORIZONTE - 2
    torre = lz.poligono([(mx - 7, my), (mx - 5, my - 30), (mx + 5, my - 30), (mx + 7, my)])
    lz.sombrear(torre, ci.PIEDRA[1:6], 4, LUZ)
    lz.sombrear(lz.elipse(mx, my - 31, 6, 4) * (lz.y < my - 30), ci.MADERA[1:6], 2, LUZ)
    for k in range(4):
        a = 0.5 + k * math.pi / 2
        fin = (mx + math.cos(a) * 18, my - 31 + math.sin(a) * 18)
        lz.pintar(lz.trazo([(mx, my - 31), fin], 0.9, 0.7), ci.MADERA[2])
        n = (math.cos(a + math.pi / 2) * 3, math.sin(a + math.pi / 2) * 3)
        lz.pintar(lz.poligono([(mx + math.cos(a) * 4, my - 31 + math.sin(a) * 4), fin, (fin[0] + n[0], fin[1] + n[1]),
                               (mx + math.cos(a) * 4 + n[0], my - 31 + math.sin(a) * 4 + n[1])]), "#e8dcc0", 0.85)
    # el mar de trigo: bandas que ondulan, con la luz rasante del sol
    suelo = lz.y > HORIZONTE + 12
    ola = (lz.ruido(30, 3, semilla=115) - 0.5) * 0.3 + np.sin(lz.x * 0.05 + lz.y * 0.12) * 0.12
    prof = np.clip((lz.y - HORIZONTE) / (H - HORIZONTE), 0, 1)
    lz.pintar(suelo, rampa(TRIGO[1:6], np.clip(0.55 + ola - prof * 0.15 + (lz.ruido(1.2, 2, semilla=116) - 0.5) * 0.25, 0, 1)))
    _espigas(lz, 900, (0, HORIZONTE + 14, 600, 200), 117, 0.8)
    # la Cosechadora, en medio del trigo
    _cosechadora(lz, 390, 208, 1.55)
    # trigo delante de la máquina y de Maisha (para que queden «dentro» del campo)
    _espigas(lz, 500, (0, 205, 600, 262), 118, 1.2)
    # Maisha, en el trigo, mirándola (a la izquierda, mirando a la derecha)
    ci.maisha(lz, 150, 236, 2.2, "lado", 1, luz=LUZ, recorte=("#ffd98a", 0.9), recorte_dir=(1, -0.5), brillo=0.8)
    _espigas(lz, 160, (100, 236, 210, 262), 119, 1.4, delante=True)
    # pájaros que vuelven
    for (bx, by, e) in ((260, 60, 1.0), (280, 52, 0.8), (300, 66, 0.9), (470, 80, 0.7)):
        lz.pintar(lz.trazo([(bx - 4 * e, by - 2 * e), (bx, by), (bx + 4 * e, by - 2 * e)], 0.8 * e, 0.5 * e), "#3a2a2a")
    # luz rasante y viñeta suave
    lz.sumar_luz(np.clip(1 - np.hypot((lz.x - 540) / 420, (lz.y - 110) / 200), 0, 1) ** 2, "#ffcf8a", 0.25)
    vin = np.clip(np.hypot((lz.x - 300) / 360, (lz.y - 140) / 190) - 0.72, 0, 1) ** 1.5
    lz.pintar(vin, "#1a0e08", 0.45)
    return lz


PIEZAS = {"11_cosecha_libre": cosecha_libre}
