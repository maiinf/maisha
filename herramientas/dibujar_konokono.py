"""
KONOKONO, LA CARACOLA DE ÓXIDO: el minijefe de la Ciénaga Quieta (paleta oficial de Raíz).

Uso:  python3 herramientas/dibujar_konokono.py
Genera arte/zonas/raiz/konokono.png: 8 fotogramas de 100×74 (se dibuja en coordenadas de 76×56 y se escala ×1,3), mirando a la derecha (el juego lo voltea):
  0-1 se arrastra      2 boca abierta (se traga lo que pilla)      3 escondida en la concha
  4 aturdida (la semilla le ha estallado dentro)                   5 la concha que rueda (para girarla)
  6 libre de Giza (concha limpia, con musgo y flores)              7 libre, contenta (antenas arriba)
Giza le ha llenado la concha de herrumbre y placas de hierro, con grietas de luz violeta.
"""
import math
import os

import numpy as np

import dibujar_criaturas as dc
from dibujar_criaturas import Hoja, MAT, tira

MAT["oxido"] = ["Madera 1", "Madera 2", "Flor ambar 1", "Flor ambar 3"]
MAT["concha"] = ["Madera 1", "Madera 3", "Flor ambar 2", "Flor ambar 4"]
MAT["babosa"] = ["Extremos 1", "Piedra 2", "Piedra 3", "Piedra 4"]
MAT["viva"] = ["Follaje 1", "Follaje 3", "Hierba 3", "Hierba 4"]
MAT["flor"] = ["Flor roja 1", "Flor roja 2", "Flor roja 3", "Flor roja 4"]

E = 1.3                     # Konokono es un 30 % más grande que el primer boceto
W, H = 76, 56               # coordenadas del dibujo (la hoja real mide W*E × H*E)
SUELO = 54


class HojaE(Hoja):
    """Una Hoja que escala todas las coordenadas por E (para dibujar más grande sin rehacer cada número)."""

    def elipse(self, cx, cy, rx, ry):
        return super().elipse(cx * E, cy * E, rx * E, ry * E)

    def poligono(self, puntos):
        return super().poligono([(x * E, y * E) for (x, y) in puntos])

    def trazo(self, puntos, grosores):
        return super().trazo([(x * E, y * E) for (x, y) in puntos], [g * E for g in grosores])

    def forma(self, mascara, mat, esfera=None, **kw):
        if esfera is not None:
            esfera = tuple(v * E for v in esfera)
        return super().forma(mascara, mat, esfera=esfera, **kw)

    def px(self, x, y, mat, tono):
        return super().px(x * E, y * E, mat, tono)

    def linea(self, puntos, mat, tono, solo_encima=False):
        return super().linea([(x * E, y * E) for (x, y) in puntos], mat, tono, solo_encima)

    def grieta(self, puntos, ancha=False, brillo=3):
        return super().grieta([(x * E, y * E) for (x, y) in puntos], ancha, brillo)


def concha(h, cx, cy, r, libre=False, giro=0.0):
    """La concha en espiral: anillos que se enroscan hacia el centro."""
    m = h.elipse(cx, cy, r, r * 0.92)
    h.forma(m, "concha" if libre else "oxido", esfera=(cx - r * 0.3, cy - r * 0.35, r * 1.2, r * 1.1))
    # la espiral: una línea oscura que da vueltas hacia dentro
    pts = []
    for k in range(90):
        t = k / 89
        a = giro + t * 2.6 * 2 * math.pi
        rr = r * (0.95 - t * 0.85)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.92))
    h.linea(pts, "concha" if libre else "oxido", 0, solo_encima=True)
    if not libre:
        # placas de hierro remachadas y grietas de luz violeta
        for (a, d) in ((0.6, 0.62), (2.2, 0.55), (3.9, 0.66), (5.3, 0.5)):
            px, py = cx + math.cos(a + giro) * r * d, cy + math.sin(a + giro) * r * d * 0.92
            h.forma(h.elipse(px, py, 4.2, 3.2), "piedra", esfera=(px - 1, py - 1, 4.5, 3.5))
            h.px(px, py, "piedra", 3)
        h.grieta([(cx - r * 0.2, cy - r * 0.6), (cx, cy - r * 0.3), (cx + r * 0.1, cy)], ancha=True)
        h.grieta([(cx + r * 0.5, cy + r * 0.2), (cx + r * 0.3, cy + r * 0.45)])
    else:
        # musgo y florecillas
        for (a, d) in ((1.0, 0.7), (2.6, 0.75), (4.2, 0.6)):
            px, py = cx + math.cos(a) * r * d, cy + math.sin(a) * r * d * 0.92
            h.forma(h.elipse(px, py, 3.5, 2.2), "viva", minimo=1)
        for (fx, fy) in ((cx - r * 0.3, cy - r * 0.85), (cx + r * 0.45, cy - r * 0.6)):
            h.px(fx, fy, "flor", 3)
            h.px(fx + 1, fy, "flor", 2)
            h.px(fx, fy - 1, "flor", 2)
            h.px(fx, fy + 1, "brote", 1)


def cuerpo(h, f):
    libre = f >= 6
    if f == 5:
        concha(h, W / 2, H / 2 + 2, 22, libre=False, giro=0.0)
        return
    escondida = f == 3
    estira = {0: 0, 1: 3, 2: 1, 4: -1, 6: 0, 7: 2}.get(f, 0)
    # el pie (cuerpo blando): una franja larga y baja
    if not escondida:
        pie = h.poligono([(8 - estira, SUELO - 1), (14, SUELO - 9), (54 + estira, SUELO - 12), (66 + estira, SUELO - 8),
                          (70 + estira, SUELO - 2), (62 + estira, SUELO)])
        h.forma(pie, "babosa" if not libre else "viva", esfera=(40, SUELO - 10, 34, 10))
        # cabeza y antenas
        hx = 62 + estira
        cabeza = h.elipse(hx, SUELO - 10, 7, 6)
        h.forma(cabeza, "babosa" if not libre else "viva", esfera=(hx - 2, SUELO - 12, 7, 6))
        if f == 2:
            # boca abierta, oscura
            h.forma(h.elipse(hx + 5, SUELO - 6, 3.2, 2.6), "sombra", plano=0)
        antenas_arriba = f in (7,)
        for (dx, alto) in ((-2, 14 if not antenas_arriba else 18), (3, 12 if not antenas_arriba else 17)):
            punta = (hx + dx + (2 if f != 4 else -1), SUELO - 12 - alto)
            m = h.trazo([(hx + dx, SUELO - 14), punta], [2.0, 1.4])
            h.forma(m, "babosa" if not libre else "viva", minimo=1)
            if f == 4:
                h.px(punta[0], punta[1], "blanco", 2)               # ojos mareados
            elif libre:
                h.px(punta[0], punta[1], "pezuna" if "pezuna" in MAT else "sombra", 0)
            else:
                h.px(punta[0], punta[1], "giza", 3)
                h.px(punta[0] + 1, punta[1], "giza", 2)
        # gotas de baba
        for x in (20, 34, 48):
            h.px(x, SUELO, "babosa" if not libre else "viva", 3)
    # la concha encima
    concha(h, 30 if not escondida else 34, SUELO - 24 if not escondida else SUELO - 20, 20 if not escondida else 21, libre=libre)


def fotograma(f):
    h = HojaE(round(W * E), round(H * E))
    cuerpo(h, f)
    return h.imagen()


def main():
    if "pezuna" not in MAT:
        MAT["pezuna"] = ["Extremos 1", "Interfaz 1", "Piedra 1", "Piedra 2"]
    hoja = tira([fotograma(f) for f in range(8)])
    ruta = os.path.join(dc.RAIZ, "arte", "zonas", "raiz", "konokono.png")
    hoja.save(ruta)
    print("guardado:", ruta, hoja.size)


if __name__ == "__main__":
    main()
