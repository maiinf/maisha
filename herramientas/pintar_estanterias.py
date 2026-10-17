"""LAS ESTANTERÍAS COLGANTES (Sigilia), pintadas con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_estanterias.py

Genera en arte/mundos/sigilia/estanterias/:
  escalera.png   36×76  una ESCALERA RODANTE de biblioteca, tumbada sobre el hueco (vista desde arriba): dos largueros
                 de madera oscura con sus peldaños, herrajes de latón y una ruedecita en cada esquina, que corre por
                 los raíles del borde del hueco
  tintero.png    6 × 24×24  el TINTERO RABIOSO: un tintero de cristal oscuro lleno de tinta de Giza, con tapón de corcho,
                 una etiqueta con dos ojos enfadados y patitas. 0 y 1 anda · 2 se agacha (va a embestir) ·
                 3 embiste (inclinado, salpica) · 4 aturdido (bizco, el tapón torcido) · 5 golpeado (blanco)
  mancha.png     32×16  la mancha de tinta que deja al embestir (pringa: frena)
  atril.png      40×44  el atril de la sala de lectura, con un libro enorme abierto
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "sigilia", "estanterias")
LUZ = (-0.6, -0.7, 0.5)
MADERA = ["#140a0c", "#24141a", "#3a2228", "#523632", "#6e4a3e", "#8c6450"]
LATON = ["#3a2a10", "#6a5020", "#9a7430", "#e8c46a", "#fbe6a2"]
CRISTAL = ["#06040c", "#120c1e", "#22183a", "#3a2a5a", "#6a5a9a", "#b8a8e8"]
CORCHO = ["#4a3018", "#6e4a24", "#94683a", "#b88a54"]
PAPEL = ["#8a7454", "#c9b07e", "#e2cea0", "#fff3d8"]


def escalera():
    W, H = 36, 76
    lz = Lienzo(W, H, s=5, semilla=9100)
    # la sombra que cae al hueco, a un lado
    lz.pintar(lz.desenfocar(lz.poligono([(9, 6), (33, 6), (33, 74), (9, 74)]), 2), "#000000", 0.45)
    # los dos largueros
    for x0 in (5, 26):
        lar = lz.poligono([(x0, 2), (x0 + 5, 2), (x0 + 5, 74), (x0, 74)])
        lz.sombrear(lar, MADERA, 2, LUZ, textura=((lz.y % 7) < 0.6) * 1.0, fuerza_tex=-0.25)
    # los peldaños
    for y in range(8, 72, 7):
        pel = lz.poligono([(9, y), (27, y), (27, y + 3), (9, y + 3)])
        lz.sombrear(pel, MADERA[1:], 1, LUZ)
        lz.pintar(lz.trazo([(10, y + 0.6), (26, y + 0.6)], 0.3), MADERA[5], 0.6)
        for xr in (8, 27.5):
            lz.pintar(lz.circulo(xr, y + 1.5, 0.7), LATON[3])
    # las ruedecitas de latón en las esquinas
    for (x, y) in ((7.5, 3), (28.5, 3), (7.5, 73), (28.5, 73)):
        r = lz.circulo(x, y, 2.6)
        lz.sombrear(r, LATON, 1.2, LUZ)
        lz.pintar(lz.circulo(x, y, 0.8), LATON[0])
    return lz.sprite(contorno=0.5)


def tintero(f):
    W, H = 24, 24
    lz = Lienzo(W, H, s=6, semilla=9200 + f)
    cx, base = 12, 23
    inclina = {3: -3, 2: 1}.get(f, 0)
    baja = 2 if f == 2 else 0
    paso = (1 if f == 0 else -1) if f in (0, 1) else 0
    # patitas
    for (dx, k) in ((-4, 1), (4, -1)):
        pie = lz.trazo([(cx + dx + inclina * 0.3, base - 4), (cx + dx + paso * k + inclina * 0.5, base)], 1.4, 1.0)
        lz.sombrear(pie, CRISTAL[:4], 0.6, LUZ)
    # el cuerpo de cristal: redondo y achaparrado, lleno de tinta con vetas violetas
    cuerpo = lz.elipse(cx + inclina * 0.5, base - 9 + baja, 8, 7 - baja * 0.5)
    lz.sombrear(cuerpo, CRISTAL, 5, LUZ)
    lz.pintar(lz.trazo([(cx - 5 + inclina * 0.5, base - 13 + baja), (cx - 2 + inclina * 0.5, base - 15 + baja)], 0.8) * cuerpo, CRISTAL[5], 0.8)
    vetas = lz.trazo([(cx - 6, base - 6 + baja), (cx - 1, base - 9 + baja), (cx + 5, base - 7 + baja)], 0.3) * cuerpo
    lz.sumar_luz(lz.desenfocar(vetas, 0.6), "#a24fd0", 0.6)
    # el cuello y el tapón de corcho (torcido si está aturdido)
    cuello = lz.poligono([(cx - 3 + inclina, base - 15 + baja), (cx + 3 + inclina, base - 15 + baja), (cx + 2.5 + inclina, base - 18 + baja), (cx - 2.5 + inclina, base - 18 + baja)])
    lz.sombrear(cuello, CRISTAL[1:], 1, LUZ)
    gira = 2.5 if f == 4 else 0.0
    tapon = lz.poligono([(cx - 3 + inclina + gira, base - 18 + baja), (cx + 3 + inclina + gira, base - 18 + baja - gira * 0.6), (cx + 2.5 + inclina + gira, base - 22 + baja - gira * 0.6), (cx - 2.5 + inclina + gira, base - 22 + baja)])
    lz.sombrear(tapon, CORCHO, 1, LUZ)
    # la etiqueta con los ojos enfadados
    eti = lz.poligono([(cx - 5 + inclina * 0.5, base - 12 + baja), (cx + 5 + inclina * 0.5, base - 12 + baja), (cx + 5 + inclina * 0.5, base - 6 + baja), (cx - 5 + inclina * 0.5, base - 6 + baja)])
    lz.sombrear(eti, PAPEL, 1, LUZ)
    ex = cx + inclina * 0.5
    ey = base - 9 + baja
    if f == 4:
        for ox in (-2.5, 2.5):
            lz.pintar(lz.trazo([(ex + ox - 1, ey - 1), (ex + ox + 1, ey + 1)], 0.35) + lz.trazo([(ex + ox - 1, ey + 1), (ex + ox + 1, ey - 1)], 0.35), "#140c20")
    else:
        for ox in (-2.5, 2.5):
            lz.pintar(lz.circulo(ex + ox, ey, 1.0), "#140c20")
            lz.pintar(lz.circulo(ex + ox - 0.3, ey - 0.4, 0.35), "#ffffff")
            lz.pintar(lz.trazo([(ex + ox - 1.4 * (1 if ox < 0 else -1), ey - 2.2), (ex + ox + 1.2 * (1 if ox < 0 else -1), ey - 1.4)], 0.35), "#140c20")   # el ceño
    if f == 3:
        # salpica tinta hacia atrás
        for k in range(5):
            gx, gy = cx + 9 + k * 1.6, base - 10 + (k % 2) * 3
            lz.sombrear(lz.circulo(gx, gy, 0.9 - k * 0.1), CRISTAL[:4], 0.4, LUZ)
    forma = np.clip(cuerpo + cuello + tapon, 0, 1)
    if f == 5:
        lz.pintar(forma, "#ffffff", 0.8)
    return lz.sprite(contorno=0.55)


def mancha():
    W, H = 32, 16
    lz = Lienzo(W, H, s=5, semilla=9300)
    m = lz.elipse(16, 8, 13, 5.5) * (lz.ruido(2, 2, semilla=9301) > 0.3)
    m = np.clip(m + lz.elipse(16, 8, 9, 4), 0, 1)
    for (x, y, r) in ((3, 6, 1.4), (29, 9, 1.2), (6, 12, 1.0), (26, 3, 0.9)):
        m = np.maximum(m, lz.circulo(x, y, r))
    lz.sombrear(m, CRISTAL[:5], 3, LUZ)
    lz.pintar(lz.trazo([(10, 6), (15, 5)], 0.5) * m, CRISTAL[5], 0.6)
    return lz.sprite(contorno=0.0)


def atril():
    W, H = 40, 44
    lz = Lienzo(W, H, s=5, semilla=9400)
    pie = lz.poligono([(17, 43), (23, 43), (22, 24), (18, 24)])
    lz.sombrear(pie, MADERA, 2, LUZ, textura=((lz.y % 5) < 0.5) * 1.0, fuerza_tex=-0.2)
    base = lz.elipse(20, 42, 9, 2.5)
    lz.sombrear(base, MADERA, 2, LUZ)
    tabla = lz.poligono([(6, 26), (34, 26), (30, 14), (10, 14)])
    lz.sombrear(tabla, MADERA, 3, LUZ)
    # el libro enorme, abierto
    for (x0, x1, lado) in ((8, 20, -1), (20, 32, 1)):
        hoja = lz.poligono([(x0, 24), (x1, 24), (x1 - lado * 0.5, 12), (x0 + lado * 0.5, 11)])
        lz.sombrear(hoja, PAPEL, 2, LUZ)
        for j in range(5):
            y = 14 + j * 2
            lz.pintar(lz.trazo([(x0 + 2, y), (x1 - 2, y)], 0.3) * hoja, CRISTAL[2], 0.7)
    lz.pintar(lz.trazo([(20, 11), (20, 24)], 0.4), PAPEL[0])
    lz.sumar_luz(lz.desenfocar(lz.circulo(20, 17, 6), 3), "#fff0b0", 0.25)
    return lz.sprite(contorno=0.5)


def main():
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(escalera(), "RGBA").save(os.path.join(SALIDA, "escalera.png"))
    Image.fromarray(np.concatenate([tintero(f) for f in range(6)], axis=1), "RGBA").save(os.path.join(SALIDA, "tintero.png"))
    Image.fromarray(mancha(), "RGBA").save(os.path.join(SALIDA, "mancha.png"))
    Image.fromarray(atril(), "RGBA").save(os.path.join(SALIDA, "atril.png"))
    print("Estanterías pintadas en", SALIDA)


if __name__ == "__main__":
    main()
