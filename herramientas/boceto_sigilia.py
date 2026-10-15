"""Boceto de ambiente de SIGILIA (mundo 2), para decidir con Iam antes de construir nada.
La Ciudad-Archivo de los escribas, en el norte nevado: torres-biblioteca de piedra morada con tejados de cobre dorado,
puentes de papel entre ellas, ventanas encendidas, un río de tinta helado y páginas que vuelan con el viento.
Maisha llega por el paso de nieve, abajo a la izquierda.
Sale en documentacion/boceto_sigilia.png (600×256)."""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from pintor import Lienzo, rampa  # noqa: E402
import cinematicas as ci  # noqa: E402

W, H = 600, 256
MORADO = ["#120c1e", "#1e1430", "#2e1e46", "#42295e", "#5a3a78", "#7a5296", "#a07ab4"]
ORO = ["#3a2408", "#6a4614", "#a07020", "#d4a034", "#f0cc60", "#fff0b0"]
LUZ = (-0.6, -0.6, 0.55)


def torre(lz, x, base, alto, ancho, rng, lejos=0.0):
    """Una torre-biblioteca: cuerpo de piedra morada con hiladas, ventanas encendidas y tejado cónico dorado."""
    cuerpo = lz.poligono([(x - ancho, base), (x - ancho * 0.92, base - alto), (x + ancho * 0.92, base - alto), (x + ancho, base)])
    hiladas = ((lz.y % 5) < 0.7) * 1.0
    lz.sombrear(cuerpo, MORADO, ancho * 0.9, LUZ, textura=1 - hiladas * 0.5, fuerza_tex=0.25)
    # balcón de libros a media altura
    yb = base - alto * 0.55
    lz.sombrear(lz.poligono([(x - ancho * 1.25, yb), (x + ancho * 1.25, yb), (x + ancho * 1.1, yb + 3), (x - ancho * 1.1, yb + 3)]),
                ORO[:5], 2, LUZ)
    # ventanas en arco, encendidas
    for fila in range(int(alto / 16)):
        yv = base - 8 - fila * 16
        for dx in (-0.45, 0.45) if ancho > 9 else (0.0,):
            if rng.random() < 0.7:
                v = np.maximum(lz.elipse(x + dx * ancho, yv - 3, 1.8, 2.0), lz.poligono([(x + dx * ancho - 1.8, yv - 3), (x + dx * ancho + 1.8, yv - 3), (x + dx * ancho + 1.8, yv + 2), (x + dx * ancho - 1.8, yv + 2)]))
                lz.pintar(v, "#f9c46a")
                lz.sumar_luz(lz.desenfocar(v, 5), "#f0a040", 0.35)
    # tejado cónico de cobre dorado, con nieve en un lado
    tejado = lz.poligono([(x - ancho * 1.15, base - alto), (x, base - alto - ancho * 2.4), (x + ancho * 1.15, base - alto)])
    lz.sombrear(tejado, ORO, ancho * 0.8, LUZ, textura=((lz.x * 0.8 % 3) < 0.6) * 1.0, fuerza_tex=-0.15)
    nieve = tejado * (lz.x < x - ancho * 0.1) * (lz.ruido(1.2, 2, semilla=int(x)) > 0.35)
    lz.pintar(nieve, "#e8e4f0", 0.85)
    lz.pintar(lz.trazo([(x, base - alto - ancho * 2.4), (x, base - alto - ancho * 2.4 - 6)], 0.6), ORO[3])
    if lejos:
        lz.pintar(np.maximum(cuerpo, tejado), "#3a3056", lejos)


def boceto():
    lz = Lienzo(W, H, semilla=600)
    rng = np.random.default_rng(601)
    # cielo de crepúsculo nórdico: morado arriba, oro pálido abajo, y una aurora
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#0c0818", "#1e1434", "#3e2a5a", "#7a5280", "#c88a8a", "#f0c890"], desde=0, hasta=150))
    ci.estrellas(lz, 90, 80, semilla=602, color="#f0e8ff")
    aurora = np.zeros((lz.H, lz.W))
    for k in range(5):
        c = lz.curva((40 + k * 30, 20 + k * 6), (300, 60 - k * 4), (580, 18 + k * 8), n=60)
        aurora = np.maximum(aurora, lz.trazo(c, 6, 3) * (0.5 + 0.1 * k))
    lz.sumar_luz(lz.desenfocar(aurora, 6), "#8ad0b0", 0.35)
    lz.sumar_luz(lz.desenfocar(aurora, 2) * (lz.ruido(2, 2, semilla=603) > 0.5), "#c8a0f0", 0.25)
    # montañas nevadas al fondo
    for (base, amp, col, sem) in ((120, 40, "#6a5a86", 604), (138, 30, "#4a3c66", 605)):
        m = ci.mascara_bajo(lz, ci.linea_horizonte(lz, base - amp * 0.5, amp, 70, sem))
        lz.pintar(m, col)
        lz.pintar(lz.desenfocar(m * (lz.ruido(10, 2, semilla=sem + 1) > 0.5) * (lz.y < base - amp * 0.3), 1.0), "#c8c0dc", 0.5)
    # la ciudad: torres lejanas (veladas) y cercanas
    for k in range(9):
        torre(lz, 230 + k * 40 + rng.uniform(-8, 8), 160, rng.uniform(40, 80), rng.uniform(6, 9), rng, lejos=0.45)
    # puentes de papel colgantes entre torres
    for (x0, x1, y) in ((300, 380, 112), (420, 500, 104), (380, 420, 124)):
        c = lz.curva((x0, y), ((x0 + x1) / 2, y + 10), (x1, y), n=40)
        lz.pintar(lz.trazo(c, 1.6), "#e8dcc0")
        for t in range(0, 40, 5):
            lz.pintar(lz.trazo([c[t], (c[t][0], c[t][1] + 3)], 0.5), "#a08a60")
    # la muralla de la ciudad, de piedra morada con almenas y nieve encima
    muro = lz.poligono([(200, 196), (200, 172), (600, 168), (600, 196)])
    almenas = (np.sin(lz.x * 0.9) > 0) * (lz.y < 174) * (lz.y > 166)
    muro = np.clip(muro + almenas * (lz.x > 200), 0, 1)
    lz.sombrear(muro, MORADO[:6], 6, LUZ, textura=1 - ((lz.y % 5) < 0.7) * 0.5 - ((lz.x + (lz.y // 5) * 5) % 12 < 0.7) * 0.4, fuerza_tex=0.25)
    lz.pintar(muro * (np.abs(lz.y - 168.5) < 1.2), "#e8e4f0", 0.8)
    torre(lz, 340, 190, 110, 14, rng)
    torre(lz, 470, 184, 130, 16, rng)
    torre(lz, 560, 196, 90, 12, rng)
    # el gran Archivo, al centro: cúpula dorada
    cuerpo = lz.poligono([(380, 196), (382, 130), (430, 130), (432, 196)])
    lz.sombrear(cuerpo, MORADO, 18, LUZ, textura=1 - ((lz.y % 6) < 0.8) * 0.5, fuerza_tex=0.25)
    cupula = lz.elipse(406, 130, 28, 26) * (lz.y < 130)
    lz.sombrear(cupula, ORO, 20, LUZ, textura=(np.abs(np.sin((lz.x - 406) * 0.5)) > 0.9) * 1.0, fuerza_tex=-0.2)
    puerta = lz.elipse(406, 182, 8, 12) * (lz.y < 196)
    lz.pintar(puerta, "#f9c46a")
    lz.sumar_luz(lz.desenfocar(puerta, 14), "#f0a040", 0.5)
    # el suelo nevado y el río de tinta helado que baja serpenteando
    suelo = ci.mascara_bajo(lz, ci.linea_horizonte(lz, 192, 4, 60, 606))
    lz.pintar(suelo, rampa(["#7a72a0", "#aaa4c8", "#d4d0e8", "#f0eef8"], np.clip(0.35 + (lz.y - 192) / 80 + (lz.ruido(24, 2, semilla=607) - 0.5) * 0.25, 0, 1)))
    ondas = (np.sin((lz.y + lz.ruido(20, 2, semilla=610) * 14) * 0.7) > 0.93) * suelo
    lz.pintar(ondas, "#8a82b0", 0.35)
    t = np.clip((lz.y - 196) / 60, 0, 1)
    centro = 300 + np.sin(t * 3 + 1) * 40 - t * 60
    rio = (lz.y > 196) * (np.abs(lz.x - centro) < 4 + t * 26)
    lz.pintar(rio, rampa(["#0a0814", "#18122a", "#2a1e46", "#3e2a5e"], np.clip(0.8 - t * 0.6 + (lz.ruido(2, 2, semilla=608) - 0.5) * 0.3, 0, 1)))
    grietas = rio * (np.abs(np.sin(lz.x * 0.6 + lz.y * 0.3 + lz.ruido(3, 2, semilla=609) * 5)) < 0.06)
    lz.pintar(grietas, "#a090d0", 0.7)
    # runas que brillan en el hielo de tinta (los sigilos)
    for (rx, ry, col) in ((250, 236, "#ff8a4a"), (282, 214, "#8ad8ff"), (236, 250, "#f0e060")):
        r = lz.trazo([(rx - 3, ry), (rx, ry - 4), (rx + 3, ry), (rx, ry + 4), (rx - 3, ry)], 0.7)
        lz.sumar_luz(lz.desenfocar(r, 4), col, 0.6)
        lz.pintar(r, col)
    # Maisha en el paso de nieve, abajo a la izquierda, mirando la ciudad
    ci.maisha_luz(lz, 120, 226, e=1.8)
    lz.pintar(lz.desenfocar(lz.elipse(122, 228, 14, 2.5), 1.5), "#2a2440", 0.5)
    # páginas que vuelan y nieve que cae
    for k in range(26):
        px, py = rng.random() * W, rng.random() * 180
        hoja = lz.poligono([(px - 2.4, py - 1.6), (px + 2.4, py - 2.2), (px + 2.2, py + 1.6), (px - 2.6, py + 2.0)])
        lz.sombrear(hoja, ["#a89a80", "#d8ccb0", "#f4ecd8"], 1.2, LUZ)
        lz.pintar(lz.trazo([(px - 1.5, py - 0.2), (px + 1.5, py - 0.6)], 0.3), "#5a4a6a", 0.6)
    copos = np.zeros((lz.H, lz.W))
    for k in range(160):
        copos = np.maximum(copos, lz.circulo(rng.random() * W, rng.random() * H, 0.4 + rng.random() * 0.5) * rng.uniform(0.5, 1))
    lz.sumar_luz(copos, "#f4f0ff", 0.8)
    return lz


if __name__ == "__main__":
    salida = os.path.join(os.path.dirname(__file__), "..", "documentacion", "boceto_sigilia.png")
    boceto().guardar(salida)
    print("hecho", os.path.abspath(salida))
