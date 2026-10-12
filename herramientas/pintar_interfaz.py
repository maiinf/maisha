"""LA INTERFAZ COMO UN DIARIO DE CUERO (pintada con el pintor de las cinemáticas).

    python3 herramientas/pintar_interfaz.py

Genera en arte/interfaz/diario/:
  libro.png          640×360   el diario abierto, «noche mágica»: tapas de cuero azul noche cosidas con hilo de oro,
                               dos páginas de cielo nocturno (nebulosa, polvo de estrellas, constelaciones tenues) con
                               un borde de filigrana dorada, y el lomo cosido con hilo de oro que brilla
  tapa.png           296×318   la tapa de delante (para la animación de abrir): cuero azul noche con el Gran Árbol,
                               una luna y estrellas en oro repujado
  cintas.png         5 × 100×44 las cintas de marcapáginas de cada pestaña (rojo, ocre, verde, verde-agua, ciruela),
                               de seda, con el remate dorado y una estrellita
  pergamino.png      48×48     caja de pergamino con borde de cuero cosido (se estira en 9 trozos: márgenes de 12)
  papel.png          48×48     papel suelto con el borde rasgado (pensamientos; márgenes de 12)
  cuero.png          32×32     etiqueta de cuero cosida (nombres, pestañas pequeñas; márgenes de 8)
  noche.png          48×48     el panel del narrador: azul de noche con filigrana dorada (márgenes de 14)
  sello.png          16×16     sello de lacre (misiones de la historia)
  arbol_ramas.png    640×360   el árbol de habilidades (pestaña Habilidades): el tronco de raíz dorada en el lomo y
                               las tres ramas (Raíz a la izquierda, Cetro hacia arriba, Aliento a la derecha), con
                               corteza, vetas de luz y hojitas; y dos ramitas dormidas, plateadas, hacia Runa y Tierra.
                               Los nodos se dibujan encima en el juego (mochila.gd, NODOS_ARBOL: mismas posiciones)
  nodos.png          5 × 16×16 los iconos de los nodos: semilla, cetro, aliento (hoja y viento), runa y tierra
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa, desplazar, RAIZ  # noqa: E402
from pintar_casa_shamba import vetas  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "interfaz", "diario")
LUZ = (-0.6, -0.7, 0.5)
CUERO = ["#170a06", "#2a130b", "#3d1d12", "#552a19", "#6e3a22", "#874c2e", "#a0613c"]
CUERO_NOCHE = ["#06070f", "#0c0e1e", "#14172e", "#1c2140", "#262c54", "#323a68", "#40497c"]
NOCHE = ["#05060f", "#0a0d1e", "#10142c", "#171c3a", "#1f2648", "#2a3158", "#3a426c"]
PAPEL = ["#7d6443", "#a68a62", "#c4a97c", "#d9c293", "#e6d3a8", "#f0e2bf", "#f8efd6"]
ORO = ["#5a3a10", "#8a6420", "#b88a34", "#d6b46e", "#f0d89a", "#fff1c8"]


def _cuero(lz, mascara, radio=8, semilla=0, tonos=None):
    tonos = tonos or CUERO
    poros = lz.ruido(0.7, 2, semilla=semilla)
    arrugas = np.clip(1 - np.abs(lz.ruido(10, 3, semilla=semilla + 1) - 0.5) * 14, 0, 1)
    lz.sombrear(mascara, tonos, radio, LUZ, textura=lz.desenfocar(poros, 0.4) * 0.6 + (1 - arrugas) * 0.4, fuerza_tex=0.22)
    lz.pintar(arrugas * mascara * (poros > 0.4), tonos[1], 0.35)


def _costura(lz, mascara, dentro=4.0, color="#d6b46e", paso=5.0):
    d = lz.distancia(mascara)
    linea = np.clip(1 - np.abs(d - dentro) / 0.7, 0, 1) * mascara
    largo = (lz.x + lz.y) % paso
    lz.pintar(linea * (largo < paso * 0.55), "#1a0c06", 0.6)
    lz.pintar(np.clip(desplazar(lz, linea * (largo < paso * 0.55), -0.3, -0.3), 0, 1), color, 0.95)


def _papel(lz, mascara, lomo_x=None, semilla=0, manchas=True):
    v = 0.78 + (lz.ruido(40, 3, semilla=semilla) - 0.5) * 0.08 + (lz.ruido(1.0, 2, semilla=semilla + 1) - 0.5) * 0.05
    if lomo_x is not None:
        v = v - np.clip(1 - np.abs(lz.x - lomo_x) / 40, 0, 1) ** 1.6 * 0.42
    lz.pintar(mascara, rampa(PAPEL, np.clip(v, 0, 1)))
    if manchas:
        m = np.clip((lz.ruido(30, 3, semilla=semilla + 2) - 0.84) * 3, 0, 1) * mascara
        lz.pintar(lz.desenfocar(m, 3), "#c9ae80", 0.18)
        aro = np.clip(1 - np.abs(np.hypot(lz.x - 560, lz.y - 290) - 14) / 1.2, 0, 1) * (lz.ruido(3, 2, semilla=9) > 0.35)
        lz.pintar(aro * mascara, "#b8986a", 0.25)                  # la marca de una taza de té
    # las fibras del papel
    fibras = (lz.ruido(0.5, 1, semilla=semilla + 3) > 0.86) * mascara
    lz.pintar(fibras, PAPEL[2], 0.25)


def _cielo(lz, mascara, lomo_x, semilla=0):
    """Una página de cielo nocturno: azul de noche, más claro en el centro y más oscuro en los bordes, con una
    neblina de nebulosa muy suave (violeta y verde-agua), polvo de estrellas, estrellas de varios tamaños con su
    brillo, constelaciones tenues y la curva de la página hacia el lomo."""
    rng = np.random.default_rng(semilla)
    ys, xs = np.nonzero(mascara > 0.5)
    cx, cy = xs.mean() / lz.s, ys.mean() / lz.s
    centro = np.clip(1 - np.hypot((lz.x - cx) / 170, (lz.y - cy) / 150), 0, 1)
    v = 0.3 + centro * 0.22 + (lz.ruido(120, 2, semilla=semilla) - 0.5) * 0.08
    v = v - np.clip(1 - np.abs(lz.x - lomo_x) / 44, 0, 1) ** 1.5 * 0.35
    lz.pintar(mascara, rampa(NOCHE, np.clip(v, 0, 1)))
    neb = lz.desenfocar(np.clip((lz.ruido(90, 3, semilla=semilla + 1) - 0.48) * 1.6, 0, 1), 14) * mascara
    lz.sumar_luz(neb, "#4a3478", 0.2)
    neb2 = lz.desenfocar(np.clip((lz.ruido(70, 3, semilla=semilla + 2) - 0.55) * 1.8, 0, 1), 12) * mascara
    lz.sumar_luz(neb2, "#24605e", 0.16)
    polvo = (lz.ruido(0.4, 1, semilla=semilla + 3) > 0.94) * mascara
    lz.sumar_luz(polvo, "#c8d8ff", 0.35)
    estrellas = np.zeros((lz.H, lz.W))
    grandes = np.zeros((lz.H, lz.W))
    for k in range(40):
        x, y = rng.random() * lz.w, rng.random() * lz.h
        r = 0.4 + rng.random() ** 3 * 1.2
        estrellas = np.maximum(estrellas, lz.circulo(x, y, r))
        if r > 1.1:
            grandes = np.maximum(grandes, lz.trazo([(x - 4, y), (x + 4, y)], 0.3) + lz.trazo([(x, y - 4), (x, y + 4)], 0.3))
    estrellas = estrellas * mascara
    lz.sumar_luz(lz.desenfocar(estrellas, 2.5), "#9fb8ff", 0.45)
    lz.sumar_luz(estrellas, "#fff8e8", 0.9)
    lz.sumar_luz(np.clip(grandes, 0, 1) * mascara, "#dfe8ff", 0.5)
    # constelaciones tenues: tres o cuatro puntos unidos por una línea fina
    for k in range(3):
        cx2, cy2 = rng.random() * (lz.w - 80) + 40, rng.random() * (lz.h - 80) + 40
        pts = [(cx2 + (rng.random() - 0.5) * 70, cy2 + (rng.random() - 0.5) * 50) for _ in range(4)]
        linea = lz.trazo(pts, 0.35) * mascara
        lz.sumar_luz(linea, "#8a9ad8", 0.2)
        for (x, y) in pts:
            lz.sumar_luz(lz.circulo(x, y, 0.8) * mascara, "#e8f0ff", 0.8)


def _filigrana(lz, pag, semilla=0):
    """El borde dorado de la página: una línea doble, con hojitas de oro en espiral en las esquinas."""
    d = lz.distancia(pag)
    for (dentro, grosor, tono) in ((6.0, 1.1, ORO[3]), (9.5, 0.6, ORO[2]), (11.5, 0.35, ORO[1])):
        linea = np.clip(1 - np.abs(d - dentro) / grosor, 0, 1) * pag
        lz.pintar(linea, tono, 0.9)
    lz.sumar_luz(lz.desenfocar(np.clip(1 - np.abs(d - 6.0) / 1.1, 0, 1) * pag, 2.0), "#f9d77a", 0.25)
    ys, xs = np.nonzero(pag > 0.5)
    x0, x1 = xs.min() / lz.s, xs.max() / lz.s
    y0, y1 = ys.min() / lz.s, ys.max() / lz.s
    for (cx, cy, sx, sy) in ((x0 + 7, y0 + 7, 1, 1), (x1 - 7, y0 + 7, -1, 1), (x0 + 7, y1 - 7, 1, -1), (x1 - 7, y1 - 7, -1, -1)):
        t = np.linspace(0, 2.4 * np.pi, 40)
        espiral = lz.trazo([(cx + sx * (6 + np.cos(a) * a * 1.5), cy + sy * (6 + np.sin(a) * a * 1.5)) for a in t], 0.9)
        hoja1 = lz.elipse(cx + sx * 20, cy + sy * 4, 5.0, 1.8, 20 * sx * sy)
        hoja2 = lz.elipse(cx + sx * 4, cy + sy * 20, 1.8, 5.0, 20 * sx * sy)
        hoja1 = np.maximum(hoja1, lz.elipse(cx + sx * 29, cy + sy * 2.5, 3.2, 1.2, 10 * sx * sy))
        hoja2 = np.maximum(hoja2, lz.elipse(cx + sx * 2.5, cy + sy * 29, 1.2, 3.2, 10 * sx * sy))
        adorno = np.clip(espiral + hoja1 + hoja2, 0, 1) * pag
        lz.pintar(adorno, rampa(ORO, np.clip(0.6 + (lz.ruido(1, 1, semilla=semilla) - 0.5), 0, 1)))
        lz.sumar_luz(lz.desenfocar(adorno, 2), "#f9d77a", 0.25)


def libro():
    lz = Lienzo(640, 360, s=2, semilla=1)
    lz.alfa[:] = 0
    tapa = lz.poligono([(18, 30), (622, 30), (624, 348), (16, 348)])
    lz.pintar(lz.desenfocar(np.clip(desplazar(lz, tapa, 3, 6), 0, 1), 4), "#000000", 0.65)
    _cuero(lz, tapa, 12, semilla=3, tonos=CUERO_NOCHE)
    _costura(lz, tapa, 5.5)
    # cantoneras de oro en las esquinas, con una estrellita grabada
    for (cx, cy, sx, sy) in ((18, 30, 1, 1), (622, 30, -1, 1), (624, 348, -1, -1), (16, 348, 1, -1)):
        c = lz.poligono([(cx, cy), (cx + 24 * sx, cy), (cx, cy + 24 * sy)])
        lz.sombrear(c, ORO, 3, LUZ)
        lz.pintar(lz.circulo(cx + 7 * sx, cy + 7 * sy, 1.4), ORO[0])
        lz.sumar_luz(lz.desenfocar(lz.circulo(cx + 7 * sx, cy + 7 * sy, 1.0), 2), "#fff1c8", 0.5)
    # el canto de las hojas (azul pálido, como papel teñido de noche)
    for k in range(3):
        canto = lz.poligono([(30 - k, 44 + k * 2), (610 + k, 44 + k * 2), (610 + k, 338 + k), (30 - k, 338 + k)])
        lz.pintar(canto, NOCHE[4 + k] if k < 3 else NOCHE[5], 1.0)
        lz.pintar(canto * ((lz.y % 2) < 1), NOCHE[3], 0.5)
        lz.pintar(canto * ((lz.y % 2) < 1) * (lz.x > 600), ORO[2], 0.4)                 # el canto dorado
    # las dos páginas de cielo, combadas hacia el lomo, con su filigrana
    for (x0, x1) in ((30, 319), (321, 610)):
        if x0 < 320:
            pag = lz.poligono([(x0, 42), (x1, 40), (x1, 334), (x0, 336)])
        else:
            pag = lz.poligono([(x0, 40), (x1, 42), (x1, 336), (x0, 334)])
        _cielo(lz, pag, 320, semilla=5 if x0 < 320 else 6)
        _filigrana(lz, pag, semilla=7 if x0 < 320 else 8)
    # el lomo: sombra honda y un hilo de oro cosido que brilla un poco
    lomo = np.clip(1 - np.abs(lz.x - 320) / 6, 0, 1) * (lz.y > 40) * (lz.y < 336)
    lz.pintar(lomo, "#02030a", 0.7)
    hilo = np.clip(1 - np.abs(lz.x - 320) / 0.8, 0, 1) * (lz.y > 44) * (lz.y < 332) * ((lz.y % 12) < 7)
    lz.pintar(hilo, ORO[4], 0.9)
    lz.sumar_luz(lz.desenfocar(hilo, 2), "#f9d77a", 0.35)
    out = lz.sprite(tramado=0.008, umbral=0.5)
    return out


def tapa():
    W, H = 296, 318
    lz = Lienzo(W, H, s=2, semilla=2)
    forma = lz.poligono([(0, 0), (W - 2, 0), (W, H), (0, H)])
    _cuero(lz, forma, 14, semilla=11, tonos=CUERO_NOCHE)
    _costura(lz, forma, 6.0)
    # un marco grabado y el Gran Árbol en el centro, con pan de oro gastado
    marco = np.clip(1 - np.abs(lz.distancia(forma) - 16) / 0.9, 0, 1) * forma
    lz.pintar(marco, ORO[2], 0.85)
    lz.pintar(np.clip(1 - np.abs(lz.distancia(forma) - 19) / 0.6, 0, 1) * forma, ORO[1], 0.6)
    cx, cy = W / 2, 150
    tronco = lz.poligono([(cx - 9, cy + 60), (cx - 5, cy + 10), (cx + 5, cy + 10), (cx + 9, cy + 60)])
    ramas = np.zeros_like(tronco)
    for (a, b, c) in (((cx, cy + 14), (cx - 30, cy - 6), (cx - 56, cy - 18)), ((cx, cy + 14), (cx + 30, cy - 6), (cx + 56, cy - 18)),
                      ((cx, cy + 10), (cx - 6, cy - 30), (cx - 2, cy - 54)), ((cx, cy + 10), (cx + 16, cy - 26), (cx + 30, cy - 44))):
        ramas = np.maximum(ramas, lz.trazo(lz.curva(a, b, c, n=20), 3.4, 1.0))
    raices = np.zeros_like(tronco)
    for dx in (-30, -14, 14, 30):
        raices = np.maximum(raices, lz.trazo(lz.curva((cx, cy + 56), (cx + dx * 0.6, cy + 64), (cx + dx * 1.4, cy + 72), n=16), 2.4, 0.8))
    copa = np.zeros_like(tronco)
    rng = np.random.default_rng(4)
    for k in range(18):
        a = rng.random() * np.pi
        r = 26 + rng.random() * 30
        copa = np.maximum(copa, lz.elipse(cx + np.cos(a) * r * 1.3, cy - 20 - np.sin(a) * r * 0.7, 12 + rng.random() * 6, 9 + rng.random() * 4))
    dibujo = np.clip(np.maximum.reduce([tronco, ramas, raices]), 0, 1)
    grabado = np.clip(copa - lz.desenfocar(copa, 1.2) * 0.0, 0, 1)
    contorno_copa = np.clip(1 - np.abs(lz.distancia(copa) - 1.2) / 0.8, 0, 1)
    lz.pintar(np.clip(desplazar(lz, dibujo + contorno_copa, 0.6, 0.8), 0, 1), CUERO[0], 0.8)      # hundido
    lz.pintar(np.clip(dibujo + contorno_copa, 0, 1), rampa(ORO, np.clip(0.55 + (lz.ruido(2, 2, semilla=12) - 0.5) * 0.8, 0, 1)), 0.95)
    hojas = (lz.ruido(1.5, 2, semilla=13) > 0.6) * copa
    lz.pintar(hojas, ORO[3], 0.55)
    # una luna creciente y estrellas en oro, sobre la copa
    luna = np.clip(lz.circulo(cx + 56, 52, 13) - lz.circulo(cx + 62, 47, 11), 0, 1)
    lz.pintar(np.clip(desplazar(lz, luna, 0.6, 0.8), 0, 1), CUERO_NOCHE[0], 0.8)
    lz.pintar(luna, rampa(ORO, np.clip(0.6 + (lz.ruido(2, 2, semilla=16) - 0.5) * 0.6, 0, 1)), 0.95)
    rng_t = np.random.default_rng(17)
    for k in range(11):
        x, y = 30 + rng_t.random() * (W - 60), 28 + rng_t.random() * 70
        r = 1.0 + rng_t.random() * 1.2
        estrella = np.clip(lz.trazo([(x - r * 2, y), (x + r * 2, y)], 0.5) + lz.trazo([(x, y - r * 2), (x, y + r * 2)], 0.5) + lz.circulo(x, y, r * 0.6), 0, 1)
        lz.pintar(estrella, ORO[4], 0.9)
        lz.sumar_luz(lz.desenfocar(estrella, 2), "#f9d77a", 0.25)
    # el desgaste del oro y del cuero en los bordes
    gastado = np.clip((lz.ruido(3, 3, semilla=14) - 0.62) * 4, 0, 1)
    lz.pintar(gastado * forma, CUERO_NOCHE[3], 0.5)
    # cantoneras
    for (x0, y0, sx, sy) in ((W, 0, -1, 1), (W, H, -1, -1)):
        c = lz.poligono([(x0, y0), (x0 + 24 * sx, y0), (x0, y0 + 24 * sy)])
        lz.sombrear(c, ORO, 3, LUZ)
    # el cierre: una correa con su hebilla en el borde
    correa = lz.poligono([(W - 30, 140), (W, 140), (W, 172), (W - 30, 172)])
    _cuero(lz, correa, 4, semilla=15, tonos=CUERO_NOCHE)
    _costura(lz, correa, 2.5, paso=4)
    hebilla = np.clip(lz.elipse(W - 30, 156, 9, 12) - lz.elipse(W - 30, 156, 6, 9), 0, 1)
    lz.sombrear(hebilla, ORO, 2, LUZ)
    return lz.sprite(tramado=0.008)


def cintas():
    cols = [["#2a0806", "#5a1410", "#8c2a20", "#b44634", "#d0624a"], ["#2a1806", "#5a3a10", "#8a5a1a", "#b47a2a", "#d49a44"],
            ["#0a1a0a", "#1e3a1a", "#33582a", "#4e7a3a", "#6e9a52"], ["#06181a", "#103a3a", "#1e5a5a", "#2e7a78", "#4a9a94"],
            ["#1a0612", "#3a1028", "#5a1e40", "#7e305a", "#a04a78"]]
    tiras = []
    for i, c in enumerate(cols):
        W, H = 100, 44
        lz = Lienzo(W, H, s=4, semilla=20 + i)
        # la cinta cuelga del libro: el extremo de arriba en cola de golondrina
        forma = lz.poligono([(2, 6), (50, 0), (98, 6), (98, H), (2, H)])
        muesca = lz.poligono([(30, -1), (70, -1), (50, 9)])
        forma = np.clip(forma - muesca, 0, 1)
        tejido = (np.sin(lz.x * 6.0) * 0.5 + 0.5) * 0.4 + lz.ruido(0.6, 2) * 0.6
        lz.sombrear(forma, c, 8, LUZ, textura=tejido, fuerza_tex=0.3)
        brillo = np.clip(1 - np.abs(lz.x - 30) / 8, 0, 1) * forma
        lz.pintar(brillo, c[4], 0.35)
        hilo = np.clip(1 - np.abs(lz.distancia(forma) - 2.5) / 0.4, 0, 1) * forma * ((lz.x + lz.y) % 3 < 1.6)
        lz.pintar(hilo, ORO[3], 0.7)
        remate = np.clip(lz.poligono([(2, H - 6), (98, H - 6), (98, H), (2, H)]), 0, 1) * forma
        lz.sombrear(remate, ORO, 2, LUZ)
        estrella = np.clip(lz.trazo([(50, 13), (50, 25)], 0.8) + lz.trazo([(44, 19), (56, 19)], 0.8) + lz.circulo(50, 19, 1.6), 0, 1)
        lz.pintar(estrella, ORO[4], 0.9)
        lz.sumar_luz(lz.desenfocar(estrella, 2), "#f9d77a", 0.3)
        tiras.append(lz.sprite(tramado=0.008))
    out = np.zeros((44, 500, 4), np.uint8)
    for i, t in enumerate(tiras):
        out[:, i * 100:(i + 1) * 100] = t
    return out


def nueve(tipo):
    """Cajas que se estiran en 9 trozos."""
    if tipo == "pergamino":
        W = H = 48
        lz = Lienzo(W, H, s=4, semilla=30)
        borde = lz.poligono([(0, 0), (W, 0), (W, H), (0, H)])
        _cuero(lz, borde, 5, semilla=31)
        dentro = lz.poligono([(6, 6), (W - 6, 6), (W - 6, H - 6), (6, H - 6)])
        lz.pintar(np.clip(desplazar(lz, dentro, 0.5, 0.8), 0, 1) - dentro * 0 , "#0a0503", 0.0)
        _papel(lz, dentro, None, semilla=32, manchas=False)
        lz.pintar(np.clip(1.4 - lz.distancia(dentro), 0, 1) * dentro, PAPEL[1], 0.7)
        lz.pintar(np.clip(1 - np.abs(lz.distancia(borde) - 2.6) / 0.5, 0, 1) * (1 - dentro) * ((lz.x + lz.y) % 4 < 2), ORO[3], 0.9)
        return lz.sprite(tramado=0.006)
    if tipo == "papel":
        W = H = 48
        lz = Lienzo(W, H, s=4, semilla=33)
        rasgado = lz.ruido(2.0, 3, semilla=34)
        d = np.minimum.reduce([lz.x, lz.y, W - lz.x, H - lz.y])
        forma = (d > 1.5 + rasgado * 2.5).astype(float)
        _papel(lz, forma, None, semilla=35, manchas=False)
        lz.pintar(np.clip(1.2 - lz.distancia(forma), 0, 1) * forma, PAPEL[1], 0.8)
        return lz.sprite(tramado=0.006)
    if tipo == "cuero":
        W = H = 32
        lz = Lienzo(W, H, s=4, semilla=36)
        forma = lz.poligono([(0, 0), (W, 0), (W, H), (0, H)])
        _cuero(lz, forma, 5, semilla=37)
        _costura(lz, forma, 2.4, paso=3.5)
        return lz.sprite(tramado=0.006)
    if tipo == "noche":
        W = H = 48
        lz = Lienzo(W, H, s=4, semilla=38)
        forma = lz.poligono([(0, 0), (W, 0), (W, H), (0, H)])
        lz.pintar(forma, rampa(["#0a0a18", "#12142a", "#1c1f3c"], lz.ruido(10, 3, semilla=39)))
        lz.pintar(np.clip(1 - np.abs(lz.distancia(forma) - 2.5) / 0.6, 0, 1), ORO[3], 0.9)
        lz.pintar(np.clip(1 - np.abs(lz.distancia(forma) - 5) / 0.4, 0, 1), ORO[1], 0.6)
        # filigrana en las esquinas: una espiral pequeña
        for (cx, cy) in ((9, 9), (W - 9, 9), (W - 9, H - 9), (9, H - 9)):
            t = np.linspace(0, 3.2 * np.pi, 40)
            pts = [(cx + np.cos(a) * (0.4 + a * 0.45), cy + np.sin(a) * (0.4 + a * 0.45)) for a in t]
            lz.pintar(lz.trazo(pts, 0.8), ORO[4], 0.95)
        return lz.sprite(tramado=0.006)


def sello():
    lz = Lienzo(16, 16, s=8, semilla=40)
    forma = lz.elipse(8, 8, 7, 7)
    borde = (lz.ruido(1.2, 2, semilla=41) - 0.5) * 1.6
    forma = np.clip(forma + (np.hypot(lz.x - 8, lz.y - 8) < 7.6 + borde) * 1.0, 0, 1)
    lz.sombrear(forma, ["#2a0404", "#5a0e0c", "#8c1e18", "#b43a2c", "#d4604a"], 3, LUZ)
    hoja = lz.poligono([(8, 3.5), (10.5, 8), (8, 12.5), (5.5, 8)])
    lz.pintar(np.clip(desplazar(lz, hoja, 0.4, 0.4), 0, 1), "#3a0806", 0.8)
    lz.pintar(hoja, "#a8302a", 0.9)
    lz.pintar(lz.trazo([(8, 4), (8, 12)], 0.4), "#3a0806", 0.8)
    return lz.sprite(tramado=0.004)


## Las posiciones de los nodos (las mismas que NODOS_ARBOL en scripts/interfaz/mochila.gd): la raíz de cada rama
## (la habilidad básica) y sus seis nodos
TRONCO = (320, 252)
RAMAS = {
    "raiz": [(262, 236), (220, 222), (182, 204), (150, 180), (124, 152), (104, 120), (92, 84)],
    "cetro": [(320, 214), (320, 186), (320, 160), (320, 134), (320, 108), (320, 84), (320, 60)],
    "aliento": [(378, 236), (420, 222), (458, 204), (490, 180), (516, 152), (536, 120), (548, 84)],
}
DORMIDAS = {"runa": [(262, 236), (180, 250), (100, 248), (64, 236)], "tierra": [(378, 236), (460, 250), (540, 248), (576, 236)]}


def arbol_ramas():
    lz = Lienzo(640, 360, s=2, semilla=301)
    lz.alfa[:] = 0
    corteza = vetas(lz, 0.5, 9, False, 302)
    # las ramitas dormidas, plateadas y con niebla
    for pts in DORMIDAS.values():
        r = lz.trazo(pts, 4.0, 1.4)
        lz.sombrear(r, ["#20243a", "#363c58", "#4e5674", "#6a7290"], 1.2, LUZ, textura=corteza, fuerza_tex=0.4)
        lz.sumar_luz(lz.desenfocar(r, 5), "#8a9ad8", 0.15)
    # el tronco: de la base del lomo hasta la raíz de la rama del Cetro, ancho y con raíces abajo
    tronco = lz.trazo([(320, 306), TRONCO, RAMAS["cetro"][0]], 24, 13)
    for dx in (-34, -18, 18, 34):
        tronco = np.maximum(tronco, lz.trazo([(320 + dx * 0.15, 292), (320 + dx * 0.6, 304), (320 + dx * 1.3, 318)], 7.0, 1.5))
    ramas = np.zeros((lz.H, lz.W))
    for nombre, pts in RAMAS.items():
        ramas = np.maximum(ramas, lz.trazo([TRONCO] + pts, 11.0, 3.0))
        # ramitas a los lados, que salen entre nodo y nodo
        for (a, b) in zip(pts[1:], pts[2:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            dx, dy = b[0] - a[0], b[1] - a[1]
            largo = max(1.0, (dx * dx + dy * dy) ** 0.5)
            nx, ny = -dy / largo, dx / largo
            lado = 1 if (int(mx) // 7) % 2 else -1
            punta = (mx + nx * 13 * lado + dx * 0.2, my + ny * 13 * lado + dy * 0.2)
            ramas = np.maximum(ramas, lz.trazo([(mx, my), punta], 2.6, 0.8))
    madera = np.clip(tronco + ramas, 0, 1)
    lz.sumar_luz(lz.desenfocar(madera, 10), "#8a6420", 0.35)
    lz.sombrear(madera, ["#2a1a08", "#4a3010", "#6e4a18", "#946a24", "#b88a34", "#d6b46e"], 3, LUZ, textura=corteza, fuerza_tex=0.55)
    # vetas de luz que suben por la madera
    vetas_luz = (np.abs(np.sin(lz.x * 0.9 + lz.ruido(6, 2, semilla=303) * 8)) < 0.12) * madera
    lz.sumar_luz(vetas_luz, "#f9d77a", 0.5)
    # hojitas a los lados de las ramas
    rng = np.random.default_rng(304)
    hojas = np.zeros((lz.H, lz.W))
    for pts in RAMAS.values():
        for (a, b) in zip(pts, pts[1:]):
            for k in range(2):
                t = rng.random()
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                lado = 1 if rng.random() < 0.5 else -1
                hojas = np.maximum(hojas, lz.elipse(x + lado * 6, y - 2, 3.2, 1.4, 30 * lado))
    lz.pintar(hojas, rampa(["#2e5a24", "#4e8a3a", "#6fcf4f"], np.clip(lz.ruido(1, 1, semilla=305), 0, 1)), 0.9)
    lz.sumar_luz(lz.desenfocar(hojas, 2), "#6fcf4f", 0.2)
    return lz.sprite(tramado=0.006, umbral=0.3)


def nodos():
    tiras = []
    for k in range(5):
        lz = Lienzo(16, 16, s=8, semilla=311 + k)
        if k == 0:                                     # semilla con brote
            lz.sombrear(lz.elipse(8, 10, 3.6, 4.2), ["#3a2414", "#6e4a28", "#a07a50", "#c8a070"], 3, LUZ)
            lz.pintar(lz.trazo([(8, 6.5), (8.5, 3)], 0.7), "#6fcf4f")
            lz.pintar(lz.elipse(6.2, 3.2, 2, 1, 25), "#6fcf4f"); lz.pintar(lz.elipse(10.6, 2.8, 2, 1, -25), "#8fe06a")
        elif k == 1:                                   # el cetro
            lz.pintar(lz.trazo([(4, 14), (11, 4)], 1.3), "#a07a50")
            lz.sombrear(lz.circulo(11.5, 3.5, 2.6), ["#2e7a20", "#4ea83a", "#8fe06a", "#d8ffc0"], 2, LUZ)
            for (x, y) in ((9, 6), (13, 5.5), (12, 1.5)):
                lz.pintar(lz.trazo([(11.5, 3.5), (x, y)], 0.5), "#6e4a28")
        elif k == 2:                                   # aliento: una hoja y el viento
            lz.sombrear(lz.elipse(7, 8, 4.5, 2.4, -35), ["#2e6a6a", "#4c8d8d", "#6db0b0", "#c8f0f0"], 2, LUZ)
            for y in (11.5, 13.5):
                lz.pintar(lz.trazo([(4, y), (9, y - 0.6), (12.5, y + 0.3)], 0.45), "#c8f0f0")
        elif k == 3:                                   # runa: un sigilo
            lz.pintar(np.clip(lz.circulo(8, 8, 5.5) - lz.circulo(8, 8, 4.6), 0, 1), "#9aa8d8")
            lz.pintar(lz.trazo([(8, 4), (8, 12)], 0.6) + lz.trazo([(5, 7), (11, 9)], 0.6), "#9aa8d8")
        else:                                          # tierra: una roca con veta
            lz.sombrear(lz.poligono([(3, 12), (4, 6), (9, 3), (13, 6), (13, 12)]), ["#2a2420", "#4a4038", "#6e6052", "#9a8a74"], 3, LUZ)
            lz.pintar(lz.trazo([(6, 10), (9, 7), (11, 8)], 0.5), "#e09a5a")
        tiras.append(lz.sprite(tramado=0.004, contorno=0.4))
    out = np.zeros((16, 80, 4), np.uint8)
    for i, t in enumerate(tiras):
        out[:, i * 16:(i + 1) * 16] = t
    return out


def main():
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(libro(), "RGBA").save(os.path.join(SALIDA, "libro.png"))
    Image.fromarray(tapa(), "RGBA").save(os.path.join(SALIDA, "tapa.png"))
    Image.fromarray(cintas(), "RGBA").save(os.path.join(SALIDA, "cintas.png"))
    for n in ("pergamino", "papel", "cuero", "noche"):
        Image.fromarray(nueve(n), "RGBA").save(os.path.join(SALIDA, n + ".png"))
    Image.fromarray(sello(), "RGBA").save(os.path.join(SALIDA, "sello.png"))
    Image.fromarray(arbol_ramas(), "RGBA").save(os.path.join(SALIDA, "arbol_ramas.png"))
    Image.fromarray(nodos(), "RGBA").save(os.path.join(SALIDA, "nodos.png"))
    print("Interfaz de diario en", SALIDA)


if __name__ == "__main__":
    main()
