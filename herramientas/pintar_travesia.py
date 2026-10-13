"""LO DE LA TRAVESÍA, pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_travesia.py

Genera:
  arte/mundos/raiz/travesia/anguila.png   5 × 44×24   la ANGUILA DE ÓXIDO (enemigo): 0-1 saltando (el cuerpo en S,
                                                      la boca abierta), 2-3 coleteando en la cubierta, 4 aturdida
                                                      (panza arriba). Hierro oscuro con manchas de óxido, una aleta a
                                                      lo largo del lomo y ojos violetas de Giza.
  arte/mundos/raiz/travesia/hoja_mauti.png 16×16      la hoja de cobre de Mauti (y su icono, el 25.º de
                                                      arte/interfaz/objetos.png)
"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ, rampa  # noqa: E402
from pintar_pasarelas import tira, CONTORNO, GIZA  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "travesia")
LUZ = (-0.6, -0.7, 0.5)
HIERRO = ["#14161a", "#22262c", "#343a42", "#4a525c", "#646e78", "#8a949c"]
OXIDO = ["#5e2c14", "#86401c", "#a85a2a", "#c87a40"]


def anguila(f):
    W, H = 44, 24
    lz = Lienzo(W, H, s=8, semilla=401 + f)
    if f in (0, 1):
        # saltando: el cuerpo en S, en el aire (la sombra la pone el juego)
        fase = 0.6 if f == 0 else -0.6
        pts = [(4 + t * 34, 13 + math.sin(t * math.pi * 1.6 + fase) * 6) for t in np.linspace(0, 1, 30)]
    elif f in (2, 3):
        fase = 0.9 if f == 2 else -0.9
        pts = [(4 + t * 34, 17 + math.sin(t * math.pi * 2.2 + fase) * 3) for t in np.linspace(0, 1, 30)]
    else:
        pts = [(4 + t * 34, 16 + math.sin(t * math.pi) * -2) for t in np.linspace(0, 1, 30)]
    if f >= 2:
        lz.pintar(lz.desenfocar(lz.elipse(22, 21, 18, 1.8), 0.6), "#0e0c0a", 0.5)
    grueso = [0.7 + 2.6 * (k / 29) ** 0.65 for k in range(30)]               # fina en la cola, gruesa en la cabeza
    cuerpo = np.zeros((lz.H, lz.W))
    for (x, y), g in zip(pts, grueso):
        cuerpo = np.maximum(cuerpo, lz.elipse(x, y, g * 1.1, g))
    vientre = f == 4
    lz.sombrear(cuerpo, HIERRO if not vientre else ["#4a3e2c", "#6e5e44", "#948062", "#b8a482", "#d0c0a0"], 3, LUZ,
                textura=lz.ruido(0.6, 2, semilla=402), fuerza_tex=0.35)
    if not vientre:
        manchas = (lz.ruido(0.7, 2, semilla=403 + f) > 0.62) * cuerpo
        lz.pintar(manchas, rampa(OXIDO, lz.ruido(0.4, 1, semilla=404)), 0.85)
        # la aleta a lo largo del lomo, con un brillo de Giza
        aleta = np.zeros((lz.H, lz.W))
        for (x, y), g in list(zip(pts, grueso))[3:26:2]:
            aleta = np.maximum(aleta, lz.trazo([(x, y - g + 0.3), (x - 0.8, y - g - 1.6)], 0.5))
        lz.pintar(aleta, OXIDO[1])
        lz.pintar(lz.trazo([p for p in pts[4:24]], 0.35) * cuerpo, GIZA[3], 0.55)
    # la cabeza (a la derecha): ojo violeta, boca
    hx, hy = pts[-1]
    lz.sombrear(lz.elipse(hx + 0.5, hy, 4.0, 3.0), HIERRO[1:] if not vientre else HIERRO[2:], 2, LUZ)
    # la aleta de la cola
    tx, ty = pts[0]
    lz.pintar(lz.poligono([(tx + 2, ty), (tx - 3, ty - 3), (tx - 2, ty), (tx - 3, ty + 3)]), OXIDO[0])
    if f == 4:
        for r in (1.2, 0.6):
            lz.pintar(np.clip(lz.circulo(hx + 1.5, hy - 0.8, r) - lz.circulo(hx + 1.5, hy - 0.8, r - 0.3), 0, 1), "#fff3c4")
    else:
        lz.pintar(lz.circulo(hx + 1.6, hy - 1, 0.8), GIZA[4])
        lz.brillo(lz.circulo(hx + 1.6, hy - 1, 0.8), GIZA[3], 1.5, 0.5)
    if f in (0, 1):
        lz.pintar(lz.poligono([(hx + 2, hy + 0.3), (hx + 5, hy - 0.6), (hx + 5, hy + 2)]), "#5a1e22")
        for k in range(3):
            lz.pintar(lz.trazo([(hx + 2.8 + k, hy - 0.3), (hx + 2.8 + k, hy + 0.4)], 0.2), "#e8dcb0")
    return lz.sprite(contorno=CONTORNO)


def hoja_mauti():
    """La hoja de Mauti: una hoja seca de cobre, con su rabito, que brilla un poco (16×16; sirve de icono y de dibujo)."""
    lz = Lienzo(16, 16, s=8, semilla=411)
    hoja = lz.elipse(8.5, 7.5, 5.2, 2.6, -35)
    lz.sumar_luz(lz.desenfocar(hoja, 2), "#f4b470", 0.0)
    lz.sombrear(hoja, ["#5a2410", "#8a3e1c", "#c06a32", "#e0904e", "#f4b470"], 2.2, LUZ)
    lz.pintar(lz.trazo([(4.5, 11), (12.5, 4.5)], 0.45), "#6a2a12")
    for (a, b) in (((7, 9), (6.5, 6.8)), ((9.5, 7), (9.6, 9.6)), ((8.2, 8), (10, 6))):
        lz.pintar(lz.trazo([a, b], 0.3), "#7a3418", 0.8)
    lz.pintar(lz.trazo([(4.5, 11), (2.5, 13.5)], 0.6), "#5a2410")
    return lz.sprite(contorno=CONTORNO)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    tira([anguila(f) for f in range(5)]).save(os.path.join(SALIDA, "anguila.png"))
    h = hoja_mauti()
    Image.fromarray(h).save(os.path.join(SALIDA, "hoja_mauti.png"))
    # el icono de la mochila: el 25.º de objetos.png (índice 24)
    ruta = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    n = max(25, viejos.width // 16)
    iconos = Image.new("RGBA", (16 * n, 16), (0, 0, 0, 0))
    iconos.alpha_composite(viejos.crop((0, 0, min(viejos.width, 16 * 24), 16)), (0, 0))
    if viejos.width > 16 * 25:
        iconos.alpha_composite(viejos.crop((16 * 25, 0, viejos.width, 16)), (16 * 25, 0))
    iconos.alpha_composite(Image.fromarray(h), (16 * 24, 0))
    iconos.save(ruta)
    print("Lo de La Travesía en", SALIDA)


if __name__ == "__main__":
    main()
