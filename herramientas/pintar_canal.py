"""EL CANAL DE TINTA (Sigilia), pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_canal.py

Genera en arte/mundos/sigilia/canal/:
  ruba.png   5 × 32×28  RUBA, LA SANGUIJUELA DE TINTA, asomando de la tinta (lo de abajo queda dentro): un cuerpo largo
             y brillante de anillos negro-violeta, una ventosa redonda con una corona de dientecitos y dos ojillos
             violetas. 0 y 1 asoma (se mece) · 2 se lanza (la ventosa abierta, estirada hacia delante) ·
             3 atrapada en el hielo (escarcha en la cabeza, ojos en espiral) · 4 golpeada (blanco)
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


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(np.concatenate([ruba(f) for f in range(5)], axis=1), "RGBA").save(os.path.join(SALIDA, "ruba.png"))
    print("Canal pintado en", SALIDA)
