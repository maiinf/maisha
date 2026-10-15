"""LAS RUINAS DEL PRIMER ÁRBOL, pintadas con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_primer_arbol.py

Genera en arte/mundos/raiz/ruinas/:
  primer_arbol.png  3 × 176×200 el PRIMER ÁRBOL: 0 enfermo (el tronco y las ramas medio vueltos piedra gris, las
                    hojas secas, vetas violetas de Giza que suben por la corteza y el hueco del tronco cerrado) ·
                    1 con el corazón de Giza al aire (el hueco abierto: dentro late una masa violeta; la dibuja el
                    juego, aquí solo el hueco) · 2 curado (la corteza viva y la copa de hojas doradas, como en los ecos)
  mauti.png         2 × 24×32 MAUTI (la misma forma que Maisha, porque son hermanos; en lo alto, en vez del brote,
                    una hoja seca de cobre): 0 de piedra, con escarcha y las vetas de Giza · 1 libre, plateada y lila
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ, rampa  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "ruinas")
LUZ = (-0.6, -0.7, 0.5)
PIEDRA = ["#26282a", "#3a3d40", "#525659", "#6b7073", "#878c8e", "#a5a9aa", "#c4c7c7"]
CORTEZA = ["#1e140e", "#33241a", "#4a3626", "#634a34", "#7e6146", "#9a7a5a"]
DORADO = ["#6a4a10", "#a07a20", "#d8aa3a", "#f0cc60", "#fbe49a", "#fff6d0"]
SECO = ["#3a3226", "#544834", "#6e6044", "#8a7a58"]
GIZA = "#8a4ad0"
NIEVE = ["#6e7f98", "#98a8bf", "#c2cfde", "#e2eaf3"]


def _nieve_encima(lz, forma, grosor=1.6, semilla=0):
    bajar = int(grosor * lz.s)
    encima = forma * (1 - np.roll(forma, bajar, axis=0))
    borde = np.clip(encima + (lz.ruido(0.8, 2, semilla=semilla) > 0.62) * np.roll(encima, int(lz.s), axis=0), 0, 1) * forma
    lz.sombrear(borde, NIEVE, 0.8, LUZ)


def _ramificar(lz, desde, angulo, largo, grosor, nivel, rng, salida):
    """Una rama que se tuerce un poco y se divide en dos o tres más finas (hasta 4 niveles)."""
    import math
    medio = (desde[0] + math.cos(angulo) * largo * 0.5 + rng.normal(0, largo * 0.08),
             desde[1] + math.sin(angulo) * largo * 0.5 + rng.normal(0, largo * 0.06))
    hasta = (desde[0] + math.cos(angulo) * largo, desde[1] + math.sin(angulo) * largo)
    salida.append((lz.trazo(lz.curva(desde, medio, hasta, n=24), grosor, grosor * 0.62), nivel))
    if nivel >= 3 or grosor < 1.2:
        return [hasta]
    puntas = []
    hijas = 2 if nivel < 2 else rng.integers(2, 4)
    for k in range(hijas):
        a = angulo + rng.uniform(-0.65, 0.65) + (k - (hijas - 1) / 2) * 0.35
        puntas += _ramificar(lz, hasta, a, largo * rng.uniform(0.55, 0.75), grosor * 0.62, nivel + 1, rng, salida)
    return puntas


def arbol(estado):
    """El Primer Árbol (176×200): ancho y viejo, con la base abierta en raíces, el tronco retorcido con nudos y estrías,
    y las ramas grandes que se dividen como brazos. 0 enfermo · 1 el corazón al aire · 2 curado."""
    import math
    W, H = 176, 200
    lz = Lienzo(W, H, s=3, semilla=1700)
    rng = np.random.default_rng(1701)
    cx, base = 88, 196
    curado = estado == 2
    # las raíces que se abren por el suelo, gruesas junto al tronco
    raices = np.zeros((lz.H, lz.W))
    for (dx, largo, alto, g) in ((-1, 74, 12, 9), (1, 78, 10, 9), (-1, 46, 5, 6), (1, 50, 4, 6), (-1, 26, 2, 5), (1, 30, 1, 5)):
        p0 = (cx + dx * 16, base - 18)
        p1 = (cx + dx * (largo * 0.42), base - alto - 4)
        p2 = (cx + dx * largo, base - alto * 0.2)
        raices = np.maximum(raices, lz.trazo(lz.curva(p0, p1, p2, n=40), g, 1.4))
    # el tronco: ancho abajo, se estrecha y se tuerce un poco hacia la izquierda y vuelve
    perfil = [(-34, 0), (-26, -10), (-21, -30), (-19, -50), (-22, -72), (-17, -96), (-14, -114)]
    puntos = [(cx + x + math.sin(-y / 40.0) * 4, base + y) for (x, y) in perfil]
    puntos += [(cx + (-x) * 0.95 + math.sin(-y / 40.0) * 4 + (3 if -60 < y < -40 else 0), base + y) for (x, y) in reversed(perfil)]
    tronco = lz.poligono(puntos)
    # las ramas: cuatro grandes como brazos, y de ellas, más finas
    piezas = []
    puntas = []
    for (ox, ang, largo, g) in ((-8, -2.6, 38, 11), (8, -0.56, 40, 11), (0, -1.62, 34, 9), (-4, -2.12, 30, 7), (5, -1.08, 31, 7)):
        puntas += _ramificar(lz, (cx + ox, base - 108), ang, largo, g, 0, rng, piezas)
    ramas = np.zeros((lz.H, lz.W))
    for (m, nivel) in piezas:
        ramas = np.maximum(ramas, m)
    madera = np.clip(tronco + ramas + raices, 0, 1)
    estrias = lz.desenfocar((np.abs(lz.ruido(1.6, 2, semilla=1709) - 0.5) < 0.06).astype(float), 0.4)
    estrias_v = np.clip(estrias * (lz.ruido(30, 2, semilla=1710) > 0.3), 0, 1)
    if curado:
        lz.sombrear(madera, CORTEZA, 7, LUZ, textura=1 - estrias_v * 0.5 + lz.ruido(1.0, 2, semilla=1702) * 0.2, fuerza_tex=0.45)
    else:
        lz.sombrear(madera, SECO + ["#a69676"], 7, LUZ, textura=1 - estrias_v * 0.5 + lz.ruido(1.0, 2, semilla=1702) * 0.2, fuerza_tex=0.45)
        # medio vuelto piedra: la piedra sube desde las raíces en manchas grandes
        piedra = (lz.desenfocar(lz.ruido(14, 3, semilla=1703), 2) + np.clip((lz.y - 70) / 130, 0, 1) * 0.9) > 0.85
        lz.sombrear(madera * piedra, PIEDRA[:6], 7, LUZ, textura=1 - estrias_v * 0.4 + lz.ruido(0.8, 3, semilla=1704) * 0.25, fuerza_tex=0.4)
        borde_p = np.clip(lz.desenfocar(piedra.astype(float), 1.2) - 0.25, 0, 1) * (1 - piedra) * madera
        lz.pintar(borde_p > 0.15, PIEDRA[1], 0.6)
    # nudos de la corteza
    for (nx, ny) in ((cx - 10, base - 44), (cx + 12, base - 82), (cx - 6, base - 98)):
        nudo = lz.elipse(nx, ny, 3.4, 2.2)
        lz.pintar(nudo, CORTEZA[2] if curado else SECO[1], 0.8)
        lz.pintar(lz.trazo([(nx - 2, ny + 0.4), (nx + 2, ny + 0.4)], 0.5), CORTEZA[0] if curado else SECO[0], 0.8)
    # el hueco del tronco (cerrado con piedra, abierto, o ya lleno de luz)
    hueco = lz.elipse(cx + 2, base - 62, 11, 17)
    if estado == 0:
        lz.sombrear(hueco, PIEDRA[1:], 3, LUZ)
        lz.pintar(lz.trazo([(cx - 4, base - 72), (cx + 4, base - 62), (cx - 1, base - 50)], 0.8) * hueco, PIEDRA[0])
    elif estado == 1:
        lz.pintar(hueco, "#120818")
        lz.pintar(np.clip(hueco - lz.elipse(cx + 2, base - 62, 8.5, 14.5), 0, 1), "#3a1a50")
    else:
        lz.pintar(hueco, "#3a2410")
        lz.sumar_luz(lz.desenfocar(lz.elipse(cx + 2, base - 62, 7, 12), 4), "#ffe39a", 0.8)
    if not curado:
        # las vetas violetas de Giza que suben por el tronco y las ramas, con su brillo
        for pts in ([(cx - 26, base - 4), (cx - 16, base - 40), (cx - 18, base - 80), (cx - 10, base - 108)],
                    [(cx + 26, base - 6), (cx + 16, base - 44), (cx + 18, base - 90)],
                    [(cx + 8, base - 108), (cx + 30, base - 124), (cx + 50, base - 140)],
                    [(cx - 60, base - 6), (cx - 36, base - 14), (cx - 22, base - 20)]):
            v = lz.trazo(lz.curva(pts[0], pts[1], pts[2], pts[3] if len(pts) > 3 else None, n=50), 1.1)
            lz.pintar(v * madera, GIZA)
            lz.sumar_luz(lz.desenfocar(v * madera, 2), "#b080ff", 0.35)
        # unas pocas hojas secas que aún cuelgan de las puntas, y nieve en las ramas
        for (px_, py_) in puntas[::2]:
            if rng.random() < 0.6:
                lz.sombrear(lz.elipse(px_ + rng.normal(0, 2), py_ + 3, 2.4, 1.2, rng.uniform(0, 180)), SECO, 0.8, LUZ)
        _nieve_encima(lz, np.clip(ramas + raices, 0, 1), 2.0, semilla=1706)
    else:
        # la copa de hojas doradas alrededor de las puntas de las ramas, y la luz que dan
        copa = np.zeros((lz.H, lz.W))
        for (px_, py_) in puntas:
            copa = np.maximum(copa, lz.elipse(px_ + rng.normal(0, 3), py_ + rng.normal(0, 2), 13 + rng.random() * 6, 9 + rng.random() * 4))
        lz.sumar_luz(lz.desenfocar(copa, 16), "#ffe9a8", 0.45)
        lz.sombrear(copa, DORADO, 10, (0.0, -1.0, 0.6), textura=lz.ruido(2.0, 3, semilla=1707), fuerza_tex=0.3)
        lz.sumar_luz(lz.desenfocar(copa, 8), "#ffe39a", 0.3)
    return lz.sprite(contorno=0.5)


def _recolorear(base, rampa_cuerpo, quitar_brote=True):
    """Toma el dibujo de Maisha y le cambia los colores por luminancia (el contorno se queda oscuro)."""
    a = np.asarray(base, dtype=np.float32) / 255.0
    sal = a.copy()
    lum = a[..., 0] * 0.3 + a[..., 1] * 0.55 + a[..., 2] * 0.15
    verde = (a[..., 1] > a[..., 0] + 0.08) & (a[..., 3] > 0.5)
    rampa_c = [np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)]) / 255.0 for c in rampa_cuerpo]
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            if a[y, x, 3] < 0.5:
                continue
            if quitar_brote and verde[y, x]:
                sal[y, x, 3] = 0.0
                continue
            t = np.clip((lum[y, x] - 0.18) / 0.75, 0, 1) * (len(rampa_c) - 1)
            i = int(t)
            f = t - i
            c = rampa_c[i] * (1 - f) + rampa_c[min(i + 1, len(rampa_c) - 1)] * f
            sal[y, x, :3] = c
    return Image.fromarray((np.clip(sal, 0, 1) * 255).astype(np.uint8), "RGBA")


def mauti(piedra):
    base = Image.open(os.path.join(RAIZ, "arte", "personajes", "maisha", "maisha_base_frente.png")).convert("RGBA")
    if piedra:
        cuerpo = _recolorear(base, ["#26282a", "#525659", "#6b7073", "#878c8e", "#a5a9aa"])
    else:
        cuerpo = _recolorear(base, ["#3a3260", "#6a5e9a", "#9a90c4", "#c4c0e0", "#eeeaf8"])
    img = Image.new("RGBA", (24, 32), (0, 0, 0, 0))
    img.alpha_composite(cuerpo, (0, 0))
    px = img.load()
    # la hoja seca de cobre en lo alto (en vez del brote)
    hoja = ["....kk", "..kCck", ".kCcck", "kCcck.", ".kk..."]
    col = {"k": (60, 30, 12), "c": (192, 106, 50) if not piedra else (110, 112, 116), "C": (244, 180, 112) if not piedra else (165, 169, 170)}
    for y, fila in enumerate(hoja):
        for x, ch in enumerate(fila):
            if ch in col:
                px[10 + x, 0 + y] = col[ch] + (255,)
    px[11, 5] = (60, 30, 12, 255)
    px[11, 6] = (60, 30, 12, 255)
    if piedra:
        # vetas de Giza, escarcha y los ojos cerrados
        for (x, y) in ((9, 14), (10, 15), (10, 16), (11, 17), (14, 22), (15, 23), (15, 24)):
            px[x, y] = (138, 74, 208, 255)
        for (x, y) in ((6, 9), (8, 8), (16, 10), (13, 20), (9, 25), (17, 27)):
            if px[x, y][3] > 0:
                px[x, y] = (226, 234, 243, 255)
    return img


def icono_semilla():
    """El icono de la Semilla del Primer Árbol (16×16): una semilla grande, dorada y tibia, con un brillo."""
    lz = Lienzo(16, 16, s=6, semilla=1800)
    semilla = lz.elipse(8, 9, 4.6, 5.6, 20)
    lz.sumar_luz(lz.desenfocar(semilla, 2.5), "#ffe39a", 0.6)
    lz.sombrear(semilla, DORADO, 2.5, LUZ)
    lz.pintar(lz.trazo([(8.6, 4), (9.6, 13.5)], 0.35), DORADO[1], 0.7)
    lz.pintar(lz.trazo([(7.8, 3.8), (9.2, 1.6)], 0.5), "#6fcf4f")
    lz.pintar(lz.elipse(10.4, 1.8, 1.6, 0.8, -30), "#8fe06a")
    return lz.sprite(contorno=0.6)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(np.concatenate([arbol(k) for k in range(3)], axis=1), "RGBA").save(os.path.join(SALIDA, "primer_arbol.png"))
    m = Image.new("RGBA", (48, 32), (0, 0, 0, 0))
    m.alpha_composite(mauti(True), (0, 0))
    m.alpha_composite(mauti(False), (24, 0))
    m.save(os.path.join(SALIDA, "mauti.png"))
    # el icono de la semilla en la mochila: el 27.º de objetos.png (índice 26)
    ruta = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    n = max(27, viejos.width // 16)
    iconos = Image.new("RGBA", (16 * n, 16), (0, 0, 0, 0))
    iconos.alpha_composite(viejos.crop((0, 0, min(viejos.width, 16 * 26), 16)), (0, 0))
    if viejos.width > 16 * 27:
        iconos.alpha_composite(viejos.crop((16 * 27, 0, viejos.width, 16)), (16 * 27, 0))
    iconos.alpha_composite(Image.fromarray(icono_semilla(), "RGBA"), (16 * 26, 0))
    iconos.save(ruta)
    print("Ruinas pintadas en", SALIDA)


if __name__ == "__main__":
    main()
