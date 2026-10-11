"""LOS OBJETOS DE LOS PRADOS DEL ECO (y de todo Raíz), pintados con detalle.

    python3 herramientas/pintar_prados.py

Mismas medidas que antes, en arte/mundos/raiz/objetos/:
  arbol_a.png, arbol_b.png   árboles de copa redonda (32×40): tronco con raíces, copa de grupos de hojas
  roca_grande.png            roca con musgo (20×16)
  roca_pequena.png           piedra (12×9)
  columna.png                columna en ruinas (12×30)
  muro.png                   muro en ruinas (24×12)
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa, bolas, RAIZ  # noqa: E402
from pintar_casa_shamba import vetas, rect  # noqa: E402
from cinematicas import piedras  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "objetos")
LUZ = (-0.6, -0.7, 0.5)
CONTORNO = 0.42
COPA = ["#122012", "#1b3418", "#28481f", "#3a5f2a", "#527a37", "#6f9545", "#93b25a", "#bccb7a"]
COPA_B = ["#1a1f10", "#2a3314", "#3f4a1c", "#5a6426", "#7a8232", "#9aa043", "#bcbd62", "#dad889"]
TRONCO = ["#1a100b", "#2c1b12", "#45291b", "#5f3a26", "#7a4d33", "#966243", "#b07a56"]
ROCA = ["#24261f", "#363a2f", "#4b5042", "#626858", "#7a806d", "#939884", "#adb19c", "#c9ccb8"]
MUSGO = ["#1f3a16", "#2f5a20", "#4d7a30", "#6f9a44", "#97b85e"]


def arbol(semilla, bultos, copa=COPA):
    lz = Lienzo(32, 40, s=6, semilla=semilla)
    rng = np.random.default_rng(semilla)
    # sombra en el suelo
    lz.pintar(lz.desenfocar(lz.elipse(17, 38, 11, 2.4), 0.6), "#0c140c", 0.0)
    # tronco con raíces que se abren al pie
    tronco = lz.poligono([(13.2, 39.5), (14.4, 26), (17.8, 26), (19.2, 39.5)])
    for (dx, l_) in [(-4.5, 1), (4.2, 1), (-2, 0.6), (2.6, 0.6)]:
        tronco = np.maximum(tronco, lz.trazo(lz.curva((16 + dx * 0.2, 36), (16 + dx * 0.7, 38.6), (16 + dx, 39.6), n=8), 2.0, 0.7))
    lz.sombrear(tronco, TRONCO, 1.8, LUZ, textura=vetas(lz, 0.3, 9, False, semilla), fuerza_tex=0.45)
    # ramas que asoman entre las hojas
    for (p0, p1) in [((16, 28), (11, 21)), ((16.5, 27), (22, 20))]:
        lz.sombrear(lz.trazo([p0, p1], 1.6, 0.8), TRONCO, 0.6, LUZ)
    # la copa: los bultos grandes, cada uno lleno de grupitos de hojas
    grupos = []
    for (cx, cy, r) in bultos:
        for k in range(14):
            a = rng.random() * 2 * np.pi
            d = np.sqrt(rng.random()) * r * 0.75
            grupos.append((cx + np.cos(a) * d, cy + np.sin(a) * d * 0.9, r * (0.34 + rng.random() * 0.22)))
    grupos.sort(key=lambda g: g[1])
    hojas = lz.ruido(0.5, 2, semilla=semilla + 5)
    bolas(lz, grupos, copa, luz=LUZ, ruido_borde=0.55, textura=hojas, fuerza_tex=0.4, ambiente=0.12,
          filo=(copa[-1], 0.35), filo_dir=(-0.6, -0.8), plano=1.4, suave=0.6)
    # unas hojas claras sueltas y alguna fruta o flor
    for k in range(5):
        x, y = 8 + rng.random() * 16, 6 + rng.random() * 16
        lz.pintar(lz.circulo(x, y, 0.5), copa[-1], 0.8)
    return lz


def roca(ancho, alto, semilla, musgo=True):
    lz = Lienzo(ancho, alto, s=8, semilla=semilla)
    rng = np.random.default_rng(semilla)
    pts = []
    for k in range(10):
        a = np.pi + k / 9 * np.pi
        r = 1.0 + (rng.random() - 0.5) * 0.18
        pts.append((ancho / 2 + np.cos(a) * ancho * 0.46 * r, alto * 0.82 + np.sin(a) * alto * 0.72 * r))
    pts += [(ancho * 0.94, alto - 0.6), (ancho * 0.06, alto - 0.6)]
    m = lz.poligono(pts)
    lz.sombrear(m, ROCA, min(ancho, alto) * 0.4, LUZ, textura=lz.ruido(0.8, 3, semilla=semilla), fuerza_tex=0.3)
    # grietas y facetas
    for k in range(2):
        x0 = ancho * (0.3 + rng.random() * 0.4)
        lz.pintar(lz.trazo([(x0, alto * 0.25), (x0 + (rng.random() - 0.5) * 3, alto * 0.6), (x0 + (rng.random() - 0.5) * 4, alto * 0.9)], 0.45, 0.25) * m, "#24261f", 0.7)
    if musgo:
        arriba = m * np.clip((alto * 0.55 - lz.y) / (alto * 0.3), 0, 1) * (lz.ruido(1.0, 3, semilla=semilla + 1) > 0.42)
        lz.sombrear(arriba, MUSGO, 1.0, LUZ, textura=lz.ruido(0.3, 2), fuerza_tex=0.4)
    # hierbitas al pie
    for k in range(int(ancho / 2.5)):
        x = 0.5 + rng.random() * (ancho - 1)
        lz.sombrear(lz.trazo([(x, alto - 0.2), (x + (rng.random() - 0.5), alto - 1.4 - rng.random() * 1.6)], 0.5, 0.25), MUSGO, 0.3, LUZ)
    return lz


def columna():
    lz = Lienzo(12, 30, s=8, semilla=40)
    fuste = lz.poligono([(2.6, 28), (3, 6.5), (4.4, 4.2), (6, 6), (7.4, 3.6), (9, 6.4), (9.4, 28)])
    acanalado = (np.abs(np.sin((lz.x - 2.6) / 6.8 * np.pi * 3)) < 0.2).astype(float)
    lz.sombrear(fuste, ROCA, 3, LUZ, textura=1 - acanalado * 0.6 + lz.ruido(0.5, 2) * 0.3, fuerza_tex=0.35)
    base = rect(lz, 1, 26.5, 11, 30)
    lz.sombrear(base, ROCA, 1.5, LUZ)
    musgo = fuste * (lz.ruido(1.0, 3, semilla=41) > 0.6) * np.clip((lz.y - 14) / 10, 0, 1)
    lz.sombrear(musgo, MUSGO, 0.5, LUZ)
    lz.pintar(lz.trazo([(5.5, 10), (6.4, 15), (5.8, 20)], 0.4) * fuste, "#24261f", 0.8)
    return lz


def muro():
    lz = Lienzo(24, 12, s=8, semilla=50)
    m = lz.poligono([(0.5, 12), (0.5, 4), (5, 2.4), (9, 3.6), (13, 1.6), (17, 4.4), (20.5, 5.6), (23.5, 7.4), (23.5, 12)])
    piedras(lz, m, tam=3.4, semilla=51, rampa_p=ROCA, luz=LUZ, mortero="#2e302a")
    musgo = m * (lz.ruido(1.2, 3, semilla=52) > 0.62)
    lz.sombrear(musgo, MUSGO, 0.6, LUZ)
    return lz


def main():
    os.makedirs(SALIDA, exist_ok=True)
    piezas = {
        "arbol_a": arbol(1, [(16, 14, 12), (9, 18, 7), (23, 17, 7.5)]),
        "arbol_b": arbol(2, [(13, 13, 10), (20, 11, 9), (17, 20, 9)], COPA_B),
        "roca_grande": roca(20, 16, 3),
        "roca_pequena": roca(12, 9, 4, musgo=False),
        "columna": columna(),
        "muro": muro(),
    }
    for nombre, lz in piezas.items():
        lz.guardar_sprite(os.path.join(SALIDA, nombre + ".png"), contorno=CONTORNO)
        print("pintado", nombre)


if __name__ == "__main__":
    main()
