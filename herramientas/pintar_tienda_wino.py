"""EL PUESTO DE WINO por dentro (Maandiko, Sigilia), con el pintor de las cinemáticas: lo que se ve al abrir su tienda.

    python3 herramientas/pintar_tienda_wino.py

Genera en arte/interfaz/:
  tienda_wino_fondo.png  216×168  el puesto de tinta: pared de piedra morada, una ventana con nieve, estantes con
                                  tinteros de colores, rollos de papel en su casillero, plumas en un tarro, tiras de
                                  papel colgando y el mostrador oscuro, manchado de tinta, con un libro de cuentas
  tienda_wino.png        4 × 96×84  Wino detrás del mostrador:
                           0 quieto · 1 parpadea · 2 habla (señala con una pluma) · 3 contento (brazos arriba)
Wino es el armiño de siempre (blanco con sombras lilas, boina morada, delantal de cuero manchado de tinta y una pluma
detrás de la oreja), pero grande.
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ, guardar_png_ligero  # noqa: E402
from pintar_casa_shamba import rect, vetas  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "interfaz")
LUZ = (-0.6, -0.7, 0.5)
PIEDRA = ["#1e1828", "#2e2640", "#423856", "#584c6c", "#706484", "#8c809c"]
MADERA = ["#140c10", "#261820", "#3a2630", "#523642", "#6e4a58", "#8a6070"]
PELO = ["#5a5280", "#8a84b0", "#b8b2d4", "#dcd8ec", "#f2f0f8", "#ffffff"]
CREMA = ["#a08a68", "#c8b08a", "#e2cea0", "#f4e6c4", "#fff6e0"]
MORADO = ["#2e1a44", "#4a2a6a", "#6a3e90", "#8a5ab0", "#ac80cc"]
CUERO = ["#2a1a0c", "#4a3018", "#6e4a24", "#94683a", "#b88a54"]
TINTAS = [["#140c20", "#2a1e4a", "#4a3a7a", "#8a7ab8"], ["#3a0c10", "#8c2028", "#c84a50", "#f08a8a"],
          ["#0c1e30", "#2e5a8a", "#4a82b8", "#8ab8e0"], ["#0c2010", "#3e7a3e", "#6aa85a", "#a8d890"],
          ["#3a2408", "#a07020", "#d4a034", "#f0cc60"]]
CONTORNO = 0.42


def fondo():
    W, H = 216, 168
    lz = Lienzo(W, H, s=4, semilla=820)
    # la pared de sillares de piedra morada, con la luz fría de la ventana y la cálida del farolillo
    fila = np.floor(lz.y / 9)
    col = np.floor((lz.x + (fila % 2) * 8) / 16)
    tono = (np.sin(fila * 12.9 + col * 78.2) * 43758.5) % 1
    lz.sombrear(rect(lz, 0, 0, W, H), PIEDRA, 60, LUZ, textura=0.5 + (tono - 0.5) * 0.7, fuerza_tex=0.25)
    junta = ((lz.y % 9) < 0.7) | (((lz.x + (fila % 2) * 8) % 16) < 0.7)
    lz.pintar(rect(lz, 0, 0, W, H) * junta, PIEDRA[0], 0.6)
    # la ventana (con nieve que cae fuera)
    ven = rect(lz, 88, 30, 128, 70)
    lz.sombrear(rect(lz, 85, 27, 131, 73), MADERA[1:], 2, LUZ)
    lz.pintar(ven, lz.gradiente(["#2a2a50", "#5a5a8a", "#a8a4cc"], desde=30, hasta=70))
    rng = np.random.default_rng(821)
    for k in range(26):
        lz.pintar(lz.circulo(88 + rng.random() * 40, 30 + rng.random() * 40, 0.6), "#ffffff", 0.9)
    lz.pintar(ven * ((np.abs(lz.x - 108) < 0.8) | (np.abs(lz.y - 50) < 0.8)), MADERA[2])
    lz.sombrear(rect(lz, 84, 70, 132, 75), PIEDRA[2:], 1.5, LUZ)
    lz.pintar(rect(lz, 86, 68, 130, 70.5), "#eeeaf8")                                    # nieve en el alféizar
    lz.sumar_luz(np.clip(1 - np.hypot((lz.x - 108) / 70, (lz.y - 60) / 60), 0, 1) ** 2, "#a8b0e0", 0.25)
    # estantes con tinteros de colores (izquierda) y el casillero de rollos (derecha)
    for (y, x0, x1) in ((58, 6, 76), (96, 6, 76)):
        lz.sombrear(rect(lz, x0, y, x1, y + 4), MADERA[2:], 2, LUZ, textura=vetas(lz, 0.4, 13, True, y), fuerza_tex=0.4)
        lz.pintar(rect(lz, x0, y + 4, x1, y + 6), "#0a0610", 0.6)
        x = x0 + 3
        k = 0
        while x < x1 - 8:
            c = TINTAS[(k + int(y)) % 5]
            if k % 3 == 2:          # un tintero redondo y bajo
                w = 9
                bote = np.maximum(lz.elipse(x + w / 2, y - 4, w / 2, 4), rect(lz, x + 2.5, y - 10, x + w - 2.5, y - 6))
                lz.sombrear(bote, ["#0a0610"] + c, 3, LUZ)
                lz.pintar(lz.trazo([(x + 2, y - 6), (x + 3, y - 2)], 0.6), "#ffffff", 0.45)
            else:                   # un frasco alto con tapón de corcho
                w = 7
                bote = np.maximum(rect(lz, x, y - 14, x + w, y), lz.elipse(x + w / 2, y - 14, w / 2, 1.5))
                lz.sombrear(bote, ["#0a0610"] + c, 2.5, LUZ)
                lz.pintar(rect(lz, x + 2, y - 17, x + w - 2, y - 14), CUERO[3])
                lz.pintar(lz.trazo([(x + 1.5, y - 12), (x + 1.5, y - 3)], 0.6), "#ffffff", 0.4)
                lz.pintar(rect(lz, x + 1, y - 9, x + w - 1, y - 6), CREMA[3], 0.85)     # la etiqueta
            x += w + 3
            k += 1
    # el casillero de rollos de papel
    lz.sombrear(rect(lz, 144, 30, 210, 112), MADERA[:5], 6, LUZ, textura=vetas(lz, 0.4, 13, True, 822), fuerza_tex=0.4)
    for fy in range(3):
        for fx in range(4):
            x0, y0 = 147 + fx * 16, 33 + fy * 26
            lz.pintar(rect(lz, x0, y0, x0 + 14, y0 + 24), "#0a0610", 0.85)
            for r in range(rng.integers(2, 5)):
                rx = x0 + 3 + (r % 2) * 7
                ry = y0 + 6 + (r // 2) * 9
                rollo = lz.circulo(rx, ry, 3.2)
                lz.sombrear(rollo, CREMA, 2, LUZ)
                lz.pintar(lz.circulo(rx, ry, 1.0), CREMA[0])
                if r == 0:
                    lz.pintar(lz.trazo([(rx - 3, ry), (rx + 3, ry)], 0.5), TINTAS[(fx + fy) % 5][1], 0.9)    # la cinta
    # tiras de papel y un ramillete de plumas colgando del techo, y el farolillo
    for k in range(5):
        hx = 20 + k * 14
        lz.pintar(lz.trazo([(hx, 0), (hx, 10)], 0.5), "#2a2a30")
        tira = rect(lz, hx - 3, 10, hx + 3, 26 + (k % 2) * 4)
        lz.sombrear(tira, CREMA, 1.5, LUZ)
        for j in range(3):
            lz.pintar(lz.trazo([(hx - 2, 14 + j * 4), (hx + 2, 14 + j * 4)], 0.4) * tira, TINTAS[k % 5][1], 0.8)
    lz.pintar(lz.trazo([(140, 0), (140, 12)], 0.7), "#1b1c1f")
    farol = np.maximum(rect(lz, 134, 12, 146, 26), lz.elipse(140, 12, 6, 2))
    lz.sombrear(farol, ["#1b1c1f", "#3d3f43", "#6a6c6f"], 1.5, LUZ)
    lz.pintar(rect(lz, 136, 14, 144, 24), "#f9b947")
    lz.sumar_luz(lz.desenfocar(lz.circulo(140, 19, 10), 6), "#ffc060", 0.6)
    lz.sumar_luz(np.clip(1 - np.hypot((lz.x - 140) / 110, (lz.y - 40) / 90), 0, 1) ** 1.6, "#ffb860", 0.25)
    # el mostrador oscuro, con manchas de tinta, un libro de cuentas abierto y un tintero con su pluma
    mostrador = rect(lz, 0, 128, W, H)
    lz.sombrear(mostrador, MADERA, 18, LUZ, textura=vetas(lz, 0.4, 25, True, 823), fuerza_tex=0.45)
    lz.sombrear(rect(lz, 0, 124, W, 131), MADERA[2:], 2, LUZ, textura=vetas(lz, 0.4, 25, True, 824), fuerza_tex=0.4)
    lz.pintar(rect(lz, 0, 131, W, 133), "#0a0610", 0.5)
    for (mx, my, r, c) in ((40, 145, 4, 0), (120, 150, 3, 1), (170, 140, 5, 2), (80, 158, 3, 3)):
        lz.pintar(lz.elipse(mx, my, r * 1.4, r * 0.7), TINTAS[c][1], 0.55)
    libro = lz.poligono([(150, 124), (198, 124), (194, 116), (154, 116)])
    lz.sombrear(libro, CREMA, 2, LUZ)
    lz.pintar(lz.trazo([(174, 116), (174, 124)], 0.5), CREMA[0])
    for j in range(3):
        lz.pintar(lz.trazo([(158, 118 + j * 2), (171, 118 + j * 2)], 0.35), TINTAS[0][1], 0.8)
        lz.pintar(lz.trazo([(177, 118 + j * 2), (190, 118 + j * 2)], 0.35), TINTAS[0][1], 0.8)
    tintero = np.maximum(lz.elipse(30, 121, 7, 4), rect(lz, 26, 112, 34, 120))
    lz.sombrear(tintero, ["#0a0610"] + TINTAS[0], 3, LUZ)
    pluma = lz.trazo(lz.curva((30, 114), (34, 102), (40, 92), n=16), 2.2, 0.4)
    lz.sombrear(pluma, ["#a8a4c0", "#d8d4e8", "#ffffff"], 1, LUZ)
    return lz.final(0.016)


def wino(f):
    """f: 0 quieto · 1 parpadea · 2 habla · 3 contento"""
    W, H = 96, 84
    lz = Lienzo(W, H, s=4, semilla=830 + f)
    cx = 46
    sube = -2 if f == 3 else 0
    # el cuerpo rechoncho y la tripa crema, con el delantal de cuero manchado de tinta
    cuerpo = lz.elipse(cx, 66 + sube, 26, 22)
    lz.sombrear(cuerpo, PELO, 18, LUZ, textura=lz.ruido(1.5, 3, semilla=831), fuerza_tex=0.12, recorte=("#ffffff", 0.4), recorte_dir=(-1, -0.6))
    tripa = lz.elipse(cx, 70 + sube, 15, 14)
    lz.sombrear(tripa, CREMA, 10, LUZ)
    delantal = lz.poligono([(cx - 15, 58 + sube), (cx + 15, 58 + sube), (cx + 17, 84), (cx - 17, 84)])
    lz.sombrear(delantal, CUERO, 8, LUZ, textura=vetas(lz, 0.4, 7, True, 832), fuerza_tex=0.3)
    for (mx, my, c) in ((cx - 6, 66, 1), (cx + 7, 72, 2), (cx - 2, 78, 3), (cx + 9, 62, 0)):
        lz.pintar(lz.elipse(mx, my + sube, 2.2, 1.6) * delantal, TINTAS[c][1], 0.85)
    lz.pintar(lz.trazo([(cx - 15, 58 + sube), (cx - 10, 50 + sube)], 1.4) + lz.trazo([(cx + 15, 58 + sube), (cx + 10, 50 + sube)], 1.4), CUERO[1])
    # los brazos: quietos, uno señalando con una pluma (habla) o los dos arriba (contento)
    if f == 3:
        brazos = [[(cx - 22, 58), (cx - 32, 44), (cx - 30, 36)], [(cx + 22, 58), (cx + 32, 44), (cx + 30, 36)]]
    elif f == 2:
        brazos = [[(cx - 22, 60), (cx - 36, 54), (cx - 42, 48)], [(cx + 22, 62), (cx + 26, 72), (cx + 22, 80)]]
    else:
        brazos = [[(cx - 22, 60), (cx - 26, 70), (cx - 22, 80)], [(cx + 22, 62), (cx + 26, 72), (cx + 22, 80)]]
    for pts in brazos:
        pts = [(x, y + sube) for (x, y) in pts]
        lz.sombrear(lz.trazo(pts, 9, 6), PELO, 4, LUZ)
        lz.sombrear(lz.circulo(pts[-1][0], pts[-1][1], 4), PELO[1:], 2, LUZ)
    if f == 2:
        px, py = brazos[0][-1][0], brazos[0][-1][1] + sube
        lz.sombrear(lz.trazo(lz.curva((px, py), (px - 4, py - 8), (px - 6, py - 16), n=12), 2.4, 0.4), ["#a8a4c0", "#d8d4e8", "#ffffff"], 1, LUZ)
    # el cuello y la cabeza (morro claro, orejas redondas)
    cy = 30 + sube
    lz.sombrear(lz.elipse(cx, cy + 16, 10, 9), PELO, 6, LUZ)
    cabeza = lz.elipse(cx, cy, 21, 17)
    lz.sombrear(cabeza, PELO, 14, LUZ, textura=lz.ruido(1.5, 3, semilla=833), fuerza_tex=0.12, recorte=("#ffffff", 0.4), recorte_dir=(-1, -0.7))
    for ox in (cx - 17, cx + 17):
        oreja = lz.circulo(ox, cy - 13, 6)
        lz.sombrear(oreja, PELO, 4, LUZ)
        lz.pintar(lz.circulo(ox, cy - 12, 3.2), "#e8a0b0", 0.85)
    morro = lz.elipse(cx, cy + 8, 11, 7)
    lz.sombrear(morro, CREMA[1:], 6, LUZ)
    lz.sombrear(lz.elipse(cx, cy + 4, 3.2, 2.4), ["#5a2030", "#a04a60", "#e08aa0"], 1.5, LUZ)      # la nariz
    for k in (-1, 1):                                                                              # los bigotes
        for j in range(2):
            lz.pintar(lz.trazo([(cx + k * 8, cy + 7 + j * 2), (cx + k * 18, cy + 5 + j * 4)], 0.4), "#ffffff", 0.85)
    # los ojos
    for ox in (cx - 8, cx + 8):
        oy = cy - 2
        if f == 1:
            lz.pintar(lz.trazo([(ox - 3, oy + 1), (ox + 3, oy + 1)], 1.0), "#1a0f1b")
        elif f == 3:
            lz.pintar(lz.trazo([(ox - 3, oy + 2), (ox, oy - 1), (ox + 3, oy + 2)], 1.0), "#1a0f1b")
        else:
            lz.pintar(lz.elipse(ox, oy, 3.0, 3.6), "#1a0f1b")
            lz.pintar(lz.circulo(ox - 1, oy - 1.4, 1.1), "#ffffff")
    for ox in (cx - 13, cx + 13):
        lz.pintar(lz.desenfocar(lz.elipse(ox, cy + 5, 3.4, 2), 1.0), "#e98a9a", 0.55)
    # la boca: sonrisa; abierta al hablar o de contento
    if f in (2, 3):
        lz.pintar(lz.elipse(cx, cy + 12, 3.4, 2.4), "#4a1a24")
        lz.pintar(lz.elipse(cx, cy + 13, 2, 1), "#e07a8a")
    else:
        lz.pintar(lz.trazo([(cx - 4, cy + 11), (cx, cy + 13), (cx + 4, cy + 11)], 0.6), "#4a1a24")
    # la boina morada, ladeada, con su rabito; y la pluma detrás de la oreja
    boina = lz.elipse(cx - 2, cy - 14, 18, 6)
    lz.sombrear(boina, MORADO, 5, LUZ, textura=lz.ruido(0.8, 2, semilla=834), fuerza_tex=0.15)
    lz.pintar(lz.trazo([(cx - 2, cy - 19), (cx + 1, cy - 23)], 1.2, 0.6), MORADO[1])
    lz.sombrear(lz.trazo(lz.curva((cx + 15, cy - 4), (cx + 22, cy - 14), (cx + 26, cy - 24), n=14), 2.6, 0.5), ["#a8a4c0", "#d8d4e8", "#ffffff"], 1, LUZ)
    return lz.sprite(contorno=CONTORNO)


def main():
    out = (np.clip(fondo(), 0, 1) * 255).round().astype(np.uint8)
    guardar_png_ligero(os.path.join(SALIDA, "tienda_wino_fondo.png"), out)
    hoja = np.concatenate([wino(f) for f in range(4)], axis=1)
    Image.fromarray(hoja, "RGBA").save(os.path.join(SALIDA, "tienda_wino.png"))
    print("Tienda de Wino en", SALIDA)


if __name__ == "__main__":
    main()
