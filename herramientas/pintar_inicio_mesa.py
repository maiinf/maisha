"""LA MESA DE LA PANTALLA DE INICIO (pintada con el pintor de las cinemáticas).

    python3 herramientas/pintar_inicio_mesa.py

Genera arte/interfaz/inicio_mesa.png (640×360): la mesa de madera donde descansa el diario de Maisha,
de noche, a la luz de una vela. Encima, en el juego, se dibujan el diario cerrado (diario/tapa.png),
la llama de la vela, las motas de polvo y la tarjeta de papel con el menú.

  vela           en su palmatoria de latón, junto a la tarjeta del menú (la llama la pone el juego en 284,124)
  tintero        con su pluma, abajo, entre la tarjeta y el diario
  hoja prensada  una hoja del Gran Árbol, abajo a la izquierda
  semillas       unas pocas, sueltas junto al tintero
  mapa           la esquina de un mapa doblado que asoma bajo el diario
  sombra         la del diario cerrado (x 322..618, y 30..348)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa, desplazar, RAIZ  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "interfaz", "inicio_mesa.png")
VELA = (284.0, 124.0)          # la punta de la llama (la misma que en inicio.gd)
LUZ = (-0.2, -0.9, 0.5)
MADERA = ["#0e0705", "#1b0e08", "#2a160c", "#3b2012", "#4f2c18", "#663a20", "#7e4b2a", "#9a6036"]
LATON = ["#2e1c08", "#5a3a10", "#8a6420", "#b88a34", "#d6b46e", "#f0d89a"]
CERA = ["#7a6248", "#a88d6a", "#cdb48c", "#e6d3ad", "#f4e8cc"]
PAPEL = ["#6d5438", "#9a7e58", "#bfa477", "#d9c293", "#ebdcb4"]
HOJA = ["#2c3a18", "#46582a", "#5d793e", "#7c9450", "#9fb06a", "#c4c98a"]


def mesa(lz):
    # tablones horizontales con su veta, de alto distinto
    bordes = [0, 52, 118, 176, 244, 300, 360]
    v = np.zeros((lz.H, lz.W))
    for i in range(len(bordes) - 1):
        y0, y1 = bordes[i], bordes[i + 1]
        dentro = (lz.y >= y0) & (lz.y < y1)
        # la veta: rayas a lo largo del tablón (una fila de azar por altura) que se tuercen un poco
        filas = np.random.default_rng(90 + i).random(lz.H + 400)
        filas = np.convolve(filas, np.ones(2) / 2, mode="same")
        torcido = (lz.ruido(90, 3, semilla=20 + i) - 0.5) * 14 + (lz.ruido(22, 2, semilla=30 + i) - 0.5) * 3
        idx = np.clip(((lz.y + torcido) * lz.s).astype(int) + 200, 0, lz.H + 399)
        veta = filas[idx]
        oscuras = (veta > 0.78) * 0.12 + (veta < 0.2) * -0.04
        largo = lz.ruido(30, 2, semilla=50 + i)
        fina = lz.ruido(3, 2, semilla=40 + i)
        nudo_x, nudo_y = 80 + (i * 137) % 520, (y0 + y1) / 2
        dn = np.hypot((lz.x - nudo_x) / 9, (lz.y - nudo_y) / 4)
        nudo = np.clip(1 - dn, 0, 1)
        anillos = np.clip(1 - np.abs(np.sin(dn * 7)) * 3, 0, 1) * np.clip(1 - dn / 2.2, 0, 1)
        tono = 0.5 + (i % 3) * 0.035 + (veta - 0.5) * 0.26 - oscuras * 1.6 + (largo - 0.5) * 0.08 + (fina - 0.5) * 0.06 - nudo * 0.3 - anillos * 0.12
        tono = tono - np.clip(1 - np.abs(lz.y - y0) / 1.5, 0, 1) * 0.45      # la junta entre tablones
        tono = tono + np.clip(1 - np.abs(lz.y - y0 - 2) / 1.0, 0, 1) * 0.08   # el canto que coge la luz
        v = np.where(dentro, tono, v)
    lz.pintar(np.ones((lz.H, lz.W)), rampa(MADERA, np.clip(v, 0, 1)))
    # clavos en las juntas
    for i, y in enumerate(bordes[1:-1]):
        for x in (14 + i * 7, 626 - i * 5):
            lz.pintar(lz.circulo(x, y + 6, 1.6), "#0a0504")
            lz.pintar(lz.circulo(x - 0.4, y + 5.6, 0.7), "#6e5a40", 0.8)
    # marcas de uso: arañazos y una mancha de tinta vieja
    rng = np.random.default_rng(3)
    for _ in range(26):
        x, y = rng.random() * 640, rng.random() * 360
        largo, ang = 6 + rng.random() * 22, rng.random() * np.pi
        lz.pintar(lz.trazo([(x, y), (x + np.cos(ang) * largo, y + np.sin(ang) * largo * 0.3)], 0.6, 0.3), MADERA[6], 0.25)
    mancha = np.clip(lz.elipse(212, 330, 14, 6) + lz.elipse(226, 334, 5, 3) + lz.circulo(196, 326, 2.0), 0, 1)
    lz.pintar(mancha * (lz.ruido(3, 2, semilla=8) > 0.3), "#0c0a10", 0.55)


def sombra(lz, mascara, dx, dy, radio, fuerza=0.7):
    lz.pintar(lz.desenfocar(np.clip(desplazar(lz, mascara, dx, dy), 0, 1), radio), "#000000", fuerza)


def mapa(lz):
    # la esquina de un mapa doblado, bajo el diario (se ve lo que queda a la izquierda de la tapa)
    forma = lz.poligono([(250, 300), (340, 284), (346, 360), (262, 360)])
    sombra(lz, forma, 2, 3, 2.5, 0.55)
    v = 0.55 + (lz.ruido(20, 3, semilla=31) - 0.5) * 0.25
    lz.pintar(forma, rampa(PAPEL, np.clip(v, 0, 1)))
    pliegue = np.clip(1 - np.abs(lz.x - 300 - (lz.y - 300) * 0.12) / 0.8, 0, 1) * forma
    lz.pintar(pliegue, PAPEL[1], 0.7)
    # caminos de tinta y un río
    for pts in (((262, 340), (284, 318), (306, 330), (330, 306)), ((270, 356), (290, 344), (318, 352))):
        lz.pintar(lz.trazo(lz.curva(*pts, n=30), 0.8) * forma, "#5a3a22", 0.7)
    lz.pintar(lz.trazo(lz.curva((256, 312), (276, 296), (300, 308), (336, 292), n=30), 1.2) * forma, "#3d6a6a", 0.6)
    lz.pintar(lz.circulo(306, 330, 1.6) * forma, "#8c281e", 0.9)
    lz.pintar(np.clip(1 - np.abs(lz.distancia(forma) - 0.6) / 0.7, 0, 1) * forma, PAPEL[0], 0.6)


def hoja(lz):
    # una hoja del Gran Árbol prensada, un poco seca
    cx, cy, ang = 62, 322, -0.35
    c, s = np.cos(ang), np.sin(ang)
    u = (lz.x - cx) * c + (lz.y - cy) * s
    w = -(lz.x - cx) * s + (lz.y - cy) * c
    forma = ((np.abs(u) < 26) & (np.abs(w) < 13 * np.sqrt(np.clip(1 - (u / 26) ** 2, 0, 1)) * (1 + 0.15 * np.sin(u * 0.9)))).astype(float)
    forma = lz.desenfocar(forma, 0.4)
    sombra(lz, forma, 1.5, 2, 1.5, 0.5)
    v = 0.55 + u / 80 + (lz.ruido(6, 2, semilla=51) - 0.5) * 0.25
    lz.pintar(forma, rampa(HOJA, np.clip(v, 0, 1)))
    seco = np.clip((lz.ruido(10, 2, semilla=52) - 0.6) * 3, 0, 1) * forma
    lz.pintar(seco, "#8a6a34", 0.6)
    nervio = np.clip(1 - np.abs(w) / 0.6, 0, 1) * (np.abs(u) < 25) * forma
    lz.pintar(nervio, HOJA[5], 0.7)
    for k in (-16, -8, 0, 8, 16):
        lado = np.clip(1 - np.abs(w - (u - k) * 0.9) / 0.5, 0, 1) * (u > k) * (u < k + 9) * forma
        lz.pintar(lado + np.clip(1 - np.abs(-w - (u - k) * 0.9) / 0.5, 0, 1) * (u > k) * (u < k + 9) * forma, HOJA[4], 0.45)
    rabito = lz.trazo([(cx - 26 * c, cy - 26 * s), (cx - 34 * c, cy - 34 * s + 1)], 1.2, 0.6)
    lz.pintar(rabito, HOJA[1])


def vela(lz):
    x = VELA[0]
    dy = VELA[1] - 60
    # la palmatoria: un plato de latón con asa
    plato = lz.elipse(x, 134 + dy, 22, 7)
    sombra(lz, plato, 3, 4, 3, 0.7)
    lz.sombrear(plato, LATON, 5, LUZ)
    lz.pintar(lz.elipse(x, 132 + dy, 15, 4.5), LATON[2], 0.8)
    asa = np.clip(lz.elipse(x - 24, 132 + dy, 6, 5) - lz.elipse(x - 24, 132 + dy, 3.5, 2.8), 0, 1)
    lz.sombrear(asa, LATON, 2, LUZ)
    copa = lz.poligono([(x - 8, 132 + dy), (x - 6, 120 + dy), (x + 6, 120 + dy), (x + 8, 132 + dy)])
    lz.sombrear(copa, LATON, 3, LUZ)
    # la vela, gastada, con gotas de cera que han caído
    cuerpo = lz.poligono([(x - 6, 121 + dy), (x - 6, 72 + dy), (x - 3, 69 + dy), (x + 4, 70 + dy), (x + 6, 73 + dy), (x + 6, 121 + dy)])
    lz.sombrear(cuerpo, CERA, 5, (-0.5, -0.2, 0.6), textura=lz.ruido(3, 2, semilla=61), fuerza_tex=0.12)
    for (gx, g0, g1) in ((-5, 72, 92), (2, 71, 84), (5, 73, 104)):
        gota = lz.trazo([(x + gx, g0 + dy), (x + gx, g1 + dy)], 2.2, 1.6)
        lz.pintar(np.clip(gota + lz.circulo(x + gx, g1 + dy, 1.6), 0, 1), CERA[4], 0.85)
    lz.pintar(lz.elipse(x + 9, 129 + dy, 3, 1.2), CERA[3], 0.9)
    # la mecha (la llama la dibuja el juego, que se mueve)
    lz.pintar(lz.trazo([(x, 70 + dy), (x + 0.5, 64 + dy)], 1.0), "#1a1210")


def tintero(lz):
    x, y = 300, 312
    cuerpo = np.clip(lz.elipse(x, y + 6, 14, 10) + lz.poligono([(x - 6, y - 6), (x + 6, y - 6), (x + 7, y + 4), (x - 7, y + 4)]), 0, 1)
    sombra(lz, cuerpo, 4, 4, 3, 0.7)
    lz.sombrear(cuerpo, ["#05050a", "#10121c", "#1d2232", "#30384e", "#56628a"], 6, LUZ)
    brillo = lz.elipse(x - 6, y + 2, 2.2, 4)
    lz.pintar(brillo, "#b8c4e6", 0.7)
    boca = lz.elipse(x, y - 6, 6, 2)
    lz.sombrear(boca, LATON, 2, LUZ)
    lz.pintar(lz.elipse(x, y - 6, 3.5, 1.1), "#050308")
    # la pluma, que sale del tintero hacia arriba a la izquierda
    eje = lz.curva((x + 1, y - 6), (x - 14, y - 50), (x - 30, y - 96), n=50)
    pluma = np.zeros((lz.H, lz.W))
    rng = np.random.default_rng(7)
    for i in range(14, 50):
        px, py = eje[i]
        t = (i - 14) / 36
        ancho = 10 * np.sin(t * np.pi * 0.95 + 0.1) ** 0.7
        for lado in (-1, 1):
            barba = lz.trazo([(px, py), (px + lado * ancho - 1, py + lado * ancho * 0.25 + 4)], 1.1, 0.5)
            if rng.random() > 0.08:
                pluma = np.maximum(pluma, barba)
    sombra(lz, pluma, 8, 10, 3, 0.45)
    lz.pintar(pluma, rampa(["#4a3a30", "#8a7868", "#c8b8a4", "#efe4d2"], np.clip(0.4 + (lz.ruido(2, 2, semilla=71) - 0.5) * 0.9, 0, 1)))
    lz.pintar(lz.trazo(eje[6:], 1.2, 0.5), "#f4ead8")


def semillas(lz):
    for (x, y, a) in ((264, 286, 20), (272, 292, -40), (258, 296, 70), (330, 344, 10)):
        s = lz.elipse(x, y, 3.2, 2.0, a)
        sombra(lz, s, 1, 1.5, 1, 0.6)
        lz.sombrear(s, ["#2a1a0c", "#5a3a1c", "#8a6030", "#c09050"], 2, LUZ)


def sombra_diario(lz):
    libro = lz.poligono([(320, 30), (622, 30), (624, 352), (318, 352)])
    sombra(lz, libro, 6, 8, 7, 0.8)


def luz_vela(lz):
    # la luz cálida de la vela sobre la mesa y la penumbra en las esquinas
    d = np.hypot((lz.x - VELA[0]) / 1.15, lz.y - VELA[1] - 40)
    calor = np.clip(1 - d / 330, 0, 1) ** 1.8
    lz.img = lz.img * (0.35 + 0.65 * calor[..., None] ** 0.5 * 1.25)
    lz.sumar_luz(calor ** 1.5, "#ff9a3c", 0.22)
    vineta = np.clip(np.hypot((lz.x - 320) / 360, (lz.y - 170) / 230), 0, 1) ** 2.2
    lz.img = lz.img * (1 - vineta[..., None] * 0.4)


def main():
    lz = Lienzo(640, 360, s=2, semilla=5)
    mesa(lz)
    hoja(lz)
    mapa(lz)
    sombra_diario(lz)
    semillas(lz)
    tintero(lz)
    vela(lz)
    luz_vela(lz)
    lz.guardar(SALIDA)
    print("Mesa del inicio en", SALIDA)


if __name__ == "__main__":
    main()
