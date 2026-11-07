"""EL CANAL DE TINTA (Sigilia), pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_canal.py

Genera en arte/mundos/sigilia/canal/:
  ruba.png   5 × 32×28  RUBA, LA SANGUIJUELA DE TINTA, asomando de la tinta (lo de abajo queda dentro): un cuerpo largo
             y brillante de anillos negro-violeta, una ventosa redonda con una corona de dientecitos y dos ojillos
             violetas. 0 y 1 asoma (se mece) · 2 se lanza (la ventosa abierta, estirada hacia delante) ·
             3 atrapada en el hielo (escarcha en la cabeza, ojos en espiral) · 4 golpeada (blanco)
  pweza.png  5 × 80×80  PWEZA, EL CALAMAR DEL TINTERO REAL (jefe de la Gran Dársena): un tintero enorme de cristal
             agrietado con su cuello y su base de latón, lleno de tinta, flotando; dentro, el calamar (dos ojos
             grandes que miran a través del cristal). 0 y 1 flota (la tinta se mece; en el 1 parpadea) ·
             2 enfadado (los ojos encendidos, la tinta hierve y rebosa) · 3 VOLCADO (el tintero tumbado hacia la
             izquierda, y el calamar medio fuera por la boca, mareado, sobre un charco) · 4 volcado y golpeado
  tentaculo.png  4 × 24×64  un tentáculo de Pweza (de pie, la punta arriba; el juego lo gira): violeta oscuro con
             ventosas claras y, en la punta, una PLUMILLA DE ORO. 0 asoma · 1 alzado · 2 azota (curvado) ·
             3 helado (con escarcha y carámbanos)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "sigilia", "canal")
LUZ = (-0.6, -0.7, 0.5)
PIEL = ["#05030a", "#0e0818", "#1c1030", "#2e1c4a", "#4a3070", "#7a5aa8", "#c0a8f0"]
BOCA = ["#1a0610", "#3a0c1e", "#6a1e34", "#a8405a"]
DIENTE = ["#8a8298", "#c8c2d4", "#f4f0fa"]
ESCARCHA = ["#3c6d93", "#7fb6d8", "#bfe3f3", "#eefaff"]


def ruba(f):
    W, H = 32, 28
    lz = Lienzo(W, H, s=6, semilla=9300 + f)
    base = 27                                     # la línea de la tinta
    mece = {0: -1.0, 1: 1.0}.get(f, 0.0)
    if f == 2:
        # se lanza: el cuello estirado hacia delante y arriba, la ventosa abierta mirando a Maisha
        puntos = [(8, base + 1), (10, base - 6), (15, base - 12), (21, base - 15)]
        cabeza = (23, base - 17)
        r_cab = 7.5
    else:
        puntos = [(13, base + 1), (13 + mece * 0.6, base - 5), (14 + mece, base - 9), (15 + mece, base - 12)]
        cabeza = (15.5 + mece, base - 14)
        r_cab = 7.2
    # el cuerpo: un tubo de anillos que sale de la tinta
    cuerpo = lz.trazo(puntos, 11.0, 9.0)
    lz.sombrear(cuerpo, PIEL, 4.0, LUZ, textura=((lz.y + lz.x * 0.5) % 4 < 0.9) * 1.0, fuerza_tex=-0.4)
    # el brillo húmedo a lo largo del lomo
    lomo = [(x - 1.6, y) for (x, y) in puntos]
    lz.pintar(lz.trazo(lomo, 0.5, 0.4) * cuerpo, PIEL[6], 0.55)
    # la cabeza y la ventosa
    cab = lz.circulo(cabeza[0], cabeza[1], r_cab)
    lz.sombrear(cab, PIEL, 3, LUZ)
    abre = 4.0 if f == 2 else 2.4
    vx, vy = (cabeza[0] + 2.4, cabeza[1] - 0.6) if f == 2 else (cabeza[0] + 0.3, cabeza[1] + 2.6)
    ventosa = lz.elipse(vx, vy, abre + 0.8, abre * 0.75 + 0.6)
    lz.sombrear(ventosa, BOCA, 1.0, LUZ)
    if f == 2:
        lz.pintar(lz.elipse(vx, vy, abre * 0.55, abre * 0.4), "#05020a")
    # la corona de dientecitos alrededor de la ventosa
    for k in range(10 if f == 2 else 7):
        a = k * 2 * np.pi / (10 if f == 2 else 7) + 0.3
        dx, dy = np.cos(a) * (abre + 0.3), np.sin(a) * (abre * 0.75 + 0.2)
        lz.pintar(lz.trazo([(vx + dx, vy + dy), (vx + dx * 0.7, vy + dy * 0.7)], 0.45, 0.1), DIENTE[2 if k % 2 else 1])
    # los ojillos violetas (en espiral si está atrapada)
    for ox in (-2.3, 2.3):
        ex, ey = cabeza[0] + ox * 1.3 - (1.6 if f == 2 else 0), cabeza[1] - 3.4
        if f == 3:
            lz.pintar(lz.trazo([(ex - 0.8, ey), (ex, ey - 0.8), (ex + 0.8, ey), (ex, ey + 0.6)], 0.3), "#d9a8ff")
        else:
            lz.sumar_luz(lz.desenfocar(lz.circulo(ex, ey, 1.8), 0.9), "#a24fd0", 1.0)
            lz.pintar(lz.circulo(ex, ey, 1.0), "#f0d8ff")
            lz.pintar(lz.circulo(ex + 0.3, ey + 0.3, 0.45), "#3a0c4a")
    # gotas de tinta que resbalan
    for (gx, gy) in ((cabeza[0] - 4, cabeza[1] + 3), (puntos[1][0] + 2.4, puntos[1][1] + 1)):
        lz.pintar(lz.trazo([(gx, gy), (gx + 0.1, gy + 2.2)], 0.5, 0.8), PIEL[2])
    forma = np.clip(cuerpo + cab, 0, 1)
    if f == 3:
        # escarcha: costra blanca en la cabeza y carámbanos en la barbilla
        costra = cab * (lz.ruido(1.2, 2, semilla=9399) > 0.45) * (lz.y < cabeza[1] + 1)
        lz.pintar(costra, ESCARCHA[2], 0.8)
        lz.pintar(lz.circulo(cabeza[0] - 2, cabeza[1] - 4, 0.8), ESCARCHA[3])
        for cx_ in (cabeza[0] - 3, cabeza[0] + 1, cabeza[0] + 3.5):
            lz.pintar(lz.trazo([(cx_, cabeza[1] + 3.5), (cx_, cabeza[1] + 6)], 0.6, 0.05), ESCARCHA[1])
    if f == 4:
        lz.pintar(forma, "#ffffff", 0.8)
    return lz.sprite(contorno=0.55)


LATON = ["#2a1c08", "#5a3e14", "#8a6224", "#c89a3e", "#f0d27a", "#fff2c0"]
CRISTAL = ["#06040c", "#120c1e", "#22183a", "#3a2a5a", "#6a5a9a", "#b8a8e8"]
CALAMAR = ["#1a0a24", "#341446", "#52226a", "#7a3a92", "#a862c0", "#e0b0f0"]


def _ojo(lz, x, y, r, f, mareado=False):
    lz.pintar(lz.circulo(x, y, r + 0.6), "#0a0410")
    if mareado:
        lz.pintar(lz.circulo(x, y, r), "#e8d8f4")
        lz.pintar(lz.trazo([(x - r * 0.6, y), (x, y - r * 0.6), (x + r * 0.6, y), (x, y + r * 0.4), (x - r * 0.2, y)], 0.35), "#3a0c4a")
        return
    lz.sumar_luz(lz.desenfocar(lz.circulo(x, y, r + 1.2), 1.2), "#ff4a8a" if f == 2 else "#c070ff", 0.9 if f == 2 else 0.6)
    lz.pintar(lz.circulo(x, y, r), "#f4e8ff" if f != 2 else "#ffd0e0")
    if f == 1:
        lz.pintar(lz.elipse(x, y, r, r * 0.3), CALAMAR[2])          # parpadea
        return
    lz.pintar(lz.elipse(x + 0.4, y + 0.3, r * 0.45, r * 0.75), "#12061c")
    lz.pintar(lz.circulo(x - r * 0.35, y - r * 0.4, r * 0.22), "#ffffff")


def pweza(f):
    W, H = 80, 80
    lz = Lienzo(W, H, s=4, semilla=9400 + f)
    if f in (3, 4):
        # VOLCADO: el globo tumbado, la boca a la izquierda, el calamar saliendo por ella sobre un charco de tinta
        lz.pintar(lz.desenfocar(lz.elipse(36, 70, 34, 7), 1.5), CRISTAL[1], 0.9)
        globo = lz.elipse(50, 54, 20, 16)
        lz.sombrear(globo, CRISTAL, 7, LUZ)
        lz.pintar(lz.elipse(50, 58, 17, 11) * globo, CRISTAL[2], 0.7)             # la tinta que queda dentro
        lz.pintar(lz.trazo([(40, 44), (55, 41), (62, 46)], 0.7) * globo, CRISTAL[5], 0.7)
        for g in ([(46, 40), (50, 48), (47, 56)], [(60, 45), (56, 52)]):          # las grietas
            lz.pintar(lz.trazo(g, 0.35), "#d8d0f0", 0.75)
        base = lz.poligono([(68, 42), (74, 44), (74, 66), (68, 68)])            # la base de latón, de lado
        lz.sombrear(base, LATON, 1.5, LUZ)
        cuello = lz.poligono([(22, 47), (31, 45), (31, 63), (22, 61)])           # el cuello y su aro, a la izquierda
        lz.sombrear(cuello, CRISTAL[1:], 2, LUZ)
        aro = lz.elipse(22, 54, 3, 9.5)
        lz.sombrear(aro, LATON, 1.5, LUZ)
        # el calamar, medio fuera: la cabeza y los tentáculos derramados
        for (pts, g) in (([(18, 58), (10, 64), (4, 62)], 2.4), ([(18, 61), (14, 69), (7, 72)], 2.2), ([(19, 56), (12, 52), (6, 54)], 2.0)):
            t = lz.trazo(pts, g, 0.8)
            lz.sombrear(t, CALAMAR, 1.2, LUZ)
        cab = lz.elipse(16, 52, 9, 8)
        lz.sombrear(cab, CALAMAR, 4, LUZ)
        _ojo(lz, 12, 50, 2.6, f, mareado=True)
        _ojo(lz, 19, 49, 2.6, f, mareado=True)
        forma = np.clip(globo + base + cuello + aro + cab, 0, 1)
        if f == 4:
            lz.pintar(forma, "#ffffff", 0.8)
        return lz.sprite(contorno=0.5)
    sube = 1 if f == 1 else 0
    # la base de latón con sus patas en garra (flota: la tinta le llega a media base)
    base = lz.poligono([(22, 70 - sube), (58, 70 - sube), (62, 77 - sube), (18, 77 - sube)])
    lz.sombrear(base, LATON, 2, LUZ, textura=((lz.x % 6) < 0.8) * 1.0, fuerza_tex=-0.25)
    # el globo de cristal lleno de tinta
    globo = lz.elipse(40, 50 - sube, 22, 21)
    lz.sombrear(globo, CRISTAL, 8, LUZ)
    tinta = lz.elipse(40, 54 - sube, 19, 16) * globo
    lz.pintar(tinta, CRISTAL[2], 0.6)
    if f == 2:
        burbujas = (lz.ruido(1.6, 2, semilla=9450) > 0.72) * tinta
        lz.pintar(burbujas, CRISTAL[4], 0.8)
    # el calamar dentro: la cabeza alargada y los ojos que miran por el cristal
    cab = lz.elipse(40, 46 - sube, 11, 13) * globo
    lz.sombrear(cab, CALAMAR[:5], 4, LUZ)
    lz.pintar(cab, CRISTAL[3], 0.35)                                               # (se ve a través del cristal)
    for k in range(4):                                                             # tentáculos enroscados abajo
        x0 = 30 + k * 6.5
        lz.pintar(lz.trazo([(x0, 56 - sube), (x0 + (2 if k % 2 else -2), 63 - sube), (x0 + (4 if k % 2 else -4), 61 - sube)], 1.6, 0.6) * globo, CALAMAR[2], 0.8)
    _ojo(lz, 34, 46 - sube, 3.6, f)
    _ojo(lz, 46, 46 - sube, 3.6, f)
    # brillo del cristal, grietas y una mancha de tinta seca
    lz.pintar(lz.trazo([(26, 38 - sube), (30, 33 - sube), (37, 31 - sube)], 1.0) * globo, CRISTAL[5], 0.8)
    lz.pintar(lz.circulo(27, 44 - sube, 1.0) * globo, "#ffffff", 0.8)
    for g in ([(50, 33 - sube), (54, 40 - sube), (52, 47 - sube)], [(54, 40 - sube), (59, 43 - sube)], [(24, 55 - sube), (28, 60 - sube)]):
        lz.pintar(lz.trazo(g, 0.35), "#d8d0f0", 0.75)
    # el cuello y el aro de latón de la boca
    cuello = lz.poligono([(31, 30 - sube), (49, 30 - sube), (47, 22 - sube), (33, 22 - sube)])
    lz.sombrear(cuello, CRISTAL[1:], 2, LUZ)
    aro = lz.elipse(40, 21 - sube, 10, 3.2)
    lz.sombrear(aro, LATON, 1.5, LUZ)
    lz.pintar(lz.elipse(40, 21 - sube, 7, 1.8), CRISTAL[0])
    if f == 2:
        # rebosa: chorretones por el cuello
        for x in (35, 43, 46):
            lz.pintar(lz.trazo([(x, 21 - sube), (x + 0.5, 28 - sube)], 1.0, 0.6), CRISTAL[2])
    # la corona de latón con remaches (el «Tintero Real»)
    for x in range(31, 50, 3):
        lz.pintar(lz.circulo(x, 70 - sube, 0.7), LATON[5])
    return lz.sprite(contorno=0.5)


def tentaculo(f):
    W, H = 24, 64
    lz = Lienzo(W, H, s=5, semilla=9500 + f)
    if f == 0:
        puntos = [(12, 64), (12, 54), (13, 47)]
    elif f == 2:
        puntos = [(12, 64), (10, 48), (12, 30), (17, 16), (19, 8)]
    else:
        puntos = [(12, 64), (12.5, 46), (11.5, 28), (12, 12)]
    cuerpo = lz.trazo(puntos, 8.5, 3.2)
    lz.sombrear(cuerpo, CALAMAR, 3, LUZ, textura=((lz.y % 5) < 0.8) * 1.0, fuerza_tex=-0.2)
    # ventosas claras por la cara de dentro
    for i in range(1, len(puntos)):
        ax, ay = puntos[i - 1]
        bx, by = puntos[i]
        for t in (0.3, 0.75):
            vx, vy = ax + (bx - ax) * t + 2.2, ay + (by - ay) * t
            lz.pintar(lz.circulo(vx, vy, 1.3 - i * 0.12) * cuerpo, CALAMAR[5], 0.8)
            lz.pintar(lz.circulo(vx, vy, 0.5) * cuerpo, CALAMAR[1])
    # la plumilla de oro en la punta
    px, py = puntos[-1]
    dx, dy = px - puntos[-2][0], py - puntos[-2][1]
    n = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / n, dy / n
    punta = (px + ux * 9, py + uy * 9)
    pluma = lz.poligono([(px - uy * 3.2, py + ux * 3.2), (px + uy * 3.2, py - ux * 3.2), punta])
    lz.sombrear(pluma, LATON, 1.2, LUZ)
    lz.pintar(lz.trazo([(px + ux * 2, py + uy * 2), (punta[0] - ux * 1.5, punta[1] - uy * 1.5)], 0.3), LATON[0])
    lz.pintar(lz.circulo(px + ux * 2.2, py + uy * 2.2, 0.8), LATON[0])
    forma = np.clip(cuerpo + pluma, 0, 1)
    if f == 3:
        lz.pintar(forma * (lz.ruido(1.0, 2, semilla=9599) > 0.4), ESCARCHA[2], 0.75)
        lz.pintar(forma, ESCARCHA[1], 0.25)
        for (x, y) in ((8, 40), (8, 24), (9, 50)):
            lz.pintar(lz.trazo([(x, y), (x - 0.4, y + 4)], 0.7, 0.05), ESCARCHA[3])
    return lz.sprite(contorno=0.5)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(np.concatenate([ruba(f) for f in range(5)], axis=1), "RGBA").save(os.path.join(SALIDA, "ruba.png"))
    Image.fromarray(np.concatenate([pweza(f) for f in range(5)], axis=1), "RGBA").save(os.path.join(SALIDA, "pweza.png"))
    Image.fromarray(np.concatenate([tentaculo(f) for f in range(4)], axis=1), "RGBA").save(os.path.join(SALIDA, "tentaculo.png"))
    print("Canal pintado en", SALIDA)
