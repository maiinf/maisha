"""LOS OBJETOS DE LA CAÑADA DEL ECO, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_canada.py

Genera:
  arte/mundos/raiz/canada/aprisco.png    64×64       la casa de Mbuzi, la cabra montés pastora: una cabaña de piedra
                                                     seca con tejado de lajas, puerta de tablas y un cayado colgado;
                                                     al lado, el pesebre de heno tras el murete de piedra del
                                                     corral, con su portillo de palos
  arte/mundos/raiz/canada/escala.png     3 × 16×16   la ESCALA DE CUERDA de la cornisa: 0 enrollada arriba (cerrada),
                                                     1 un tramo colgando, 2 el último tramo (con las puntas de cuerda)
  arte/mundos/raiz/objetos/cencerro.png  2 × 12×12   un cencerro de Mbuzi
  y su icono (16×16) en arte/interfaz/objetos.png (el 23.º)
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_casa_shamba import vetas, rect  # noqa: E402
from pintar_pasarelas import tira, pixeles, MADERA, CONTORNO  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "canada")
LUZ = (-0.6, -0.7, 0.5)
# piedra gris de la cañada (la misma que la peña del suelo)
GRIS = ["#1a1c20", "#292c32", "#3a3e45", "#4d5259", "#62686e", "#7a8086", "#949a9e", "#b1b5b6", "#cfd2cf"]
LAJA = ["#16181c", "#23262c", "#32363d", "#454a52", "#5a6068", "#70767e"]
HENO = ["#3d3214", "#5c4a22", "#7a6431", "#958043", "#b09c5c", "#c9b77d"]
CUERDA = ["#3a2a18", "#5c4428", "#80643c", "#a48656", "#c4a874"]


def aprisco():
    W, H = 64, 64
    lz = Lienzo(W, H, s=6, semilla=161)
    suelo = 61
    lz.pintar(lz.desenfocar(lz.elipse(32, suelo, 30, 3.5), 1.2), "#0e0c0a", 0.5)
    # la cabaña: paredes de piedra seca (piedras planas apiladas, cada una con su luz)
    frente = rect(lz, 4, 24, 34, 50)
    lado = lz.poligono([(34, 24), (42, 19), (42, 45), (34, 50)])
    piedras = np.zeros((lz.H, lz.W))
    tono = np.zeros((lz.H, lz.W))
    rng = np.random.default_rng(162)
    for fila in range(10):
        y = 25 + fila * 2.6
        x = 3 + (fila % 2) * 2.2
        while x < 44:
            largo = 3 + rng.random() * 3
            p = lz.elipse(x + largo / 2, y + 1.1, largo / 2, 1.2)
            piedras = np.maximum(piedras, p)
            tono = np.where(p > 0.5, rng.random(), tono)
            x += largo + 0.4
    pared = np.clip(frente + lado, 0, 1)
    lz.pintar(pared, "#14161a")
    lz.sombrear(piedras * pared, GRIS[1:8], 1.2, LUZ, textura=tono, fuerza_tex=0.45)
    lz.pintar(lado * piedras, "#0b0c0e", 0.35)                    # el lado, en sombra
    # la puerta de tablas y un ventanuco
    puerta = rect(lz, 14, 33, 22, 50)
    lz.sombrear(puerta, MADERA[1:6], 2, LUZ, textura=vetas(lz, 0.4, 9, False, 163), fuerza_tex=0.45)
    lz.pintar(puerta * ((lz.x % 2.7) < 0.45), MADERA[0], 0.8)
    for y in (36, 46):
        lz.pintar(rect(lz, 14, y, 22, y + 0.9), MADERA[1], 0.9)
    lz.pintar(lz.circulo(20.5, 42, 0.6), "#c9b07e")
    ventana = rect(lz, 26, 31, 31, 36)
    lz.pintar(ventana, "#0c0a0a")
    lz.brillo(lz.elipse(28.5, 34, 1.6, 1.2), "#e6a852", 2.0, 0.6)    # un candil dentro
    # el cayado colgado junto a la puerta
    lz.pintar(lz.trazo([(10, 49), (10, 30)], 0.7), MADERA[5])
    lz.pintar(lz.trazo([tuple(p) for p in lz.curva((10, 30), (10, 27), (12.6, 26.5), (12.8, 29), n=20)], 0.7), MADERA[5])
    # el tejado de lajas, a dos aguas, con las lajas solapadas
    tejado = lz.poligono([(1, 25), (22, 9), (26, 9), (37, 25)])
    faldon = lz.poligono([(26, 9), (45, 5), (44, 20), (37, 25)])
    filas_l = ((lz.y + (lz.x * 0.15)) % 3.2) / 3.2
    juntas = np.abs(((lz.x + np.floor(lz.y / 3.2) * 2.3) % 5.0) - 2.5) < 0.35
    lz.sombrear(faldon, LAJA, 3, LUZ, textura=filas_l, fuerza_tex=0.4)
    lz.sombrear(tejado, LAJA[1:] + ["#888e96"], 5, LUZ, textura=filas_l, fuerza_tex=0.55)
    lz.pintar(np.clip(tejado + faldon, 0, 1) * (filas_l > 0.86), LAJA[0], 0.8)
    lz.pintar(np.clip(tejado + faldon, 0, 1) * juntas, LAJA[1], 0.6)
    musgo = np.clip((lz.ruido(1.5, 2, semilla=164) - 0.62) * 4, 0, 1) * np.clip(tejado + faldon, 0, 1)
    lz.pintar(musgo, "#4d6436", 0.8)
    lz.pintar(lz.trazo([(22, 9), (26, 9), (45, 5)], 1.2), LAJA[5])
    # dentro del corral: el pesebre de heno (de palos, lleno hasta arriba) y el abrevadero de piedra
    lz.pintar(lz.desenfocar(lz.elipse(53, 54, 9, 1.8), 0.8), "#0e0c0a", 0.6)
    pesebre = rect(lz, 46, 45, 60, 54)
    lz.sombrear(pesebre, MADERA[1:6], 2, LUZ, textura=vetas(lz, 0.4, 9, True, 167), fuerza_tex=0.4)
    lz.pintar(pesebre * ((lz.x % 3.5) < 0.6), MADERA[0], 0.7)
    heno = lz.elipse(53, 44.5, 8, 3.6)
    lz.sombrear(heno, HENO, 3, LUZ, textura=vetas(lz, 0.3, 7, True, 166), fuerza_tex=0.5)
    pajas = np.zeros((lz.H, lz.W))
    for k in range(9):
        x0 = 46.5 + k * 1.6
        pajas = np.maximum(pajas, lz.trazo([(x0, 43), (x0 + (k % 3 - 1) * 1.2, 40 + (k % 2))], 0.4))
    lz.pintar(pajas, HENO[5], 0.9)
    # el murete del corral, delante: piedra seca en tres hiladas, recto, con un portillo de palos a la izquierda
    piedras_m = np.zeros((lz.H, lz.W))
    for fila in range(3):
        x = 45 + (fila % 2) * 1.5
        y = 61.5 - fila * 2.2
        while x < 63:
            largo = 2.4 + rng.random() * 2.2
            piedras_m = np.maximum(piedras_m, lz.elipse(x + largo / 2, y, largo / 2, 1.3))
            x += largo + 0.3
    lz.pintar(lz.desenfocar(lz.elipse(54, 62.5, 10, 1.4), 0.8), "#0e0c0a", 0.6)
    lz.pintar(lz.desenfocar(np.clip(piedras_m, 0, 1), 0.5), "#14161a", 0.9)
    lz.sombrear(piedras_m, GRIS[2:9], 1.0, LUZ, textura=lz.ruido(0.5, 1, semilla=165), fuerza_tex=0.4)
    for xx in (39, 43.5):                                     # el portillo
        lz.pintar(lz.trazo([(xx, 60), (xx, 52)], 0.8), MADERA[5])
    for yy in (54, 57):
        lz.pintar(lz.trazo([(38.5, yy), (44, yy - 0.4)], 0.55), MADERA[4])
    return lz.sprite(contorno=CONTORNO)


def escala(k):
    """La escala de cuerda. 0: enrollada en lo alto de la cornisa, atada a una estaca (cerrada) ·
    1: un tramo colgando (dos cuerdas y un peldaño de madera) · 2: el último tramo, con las puntas sueltas."""
    W, H = 16, 16
    lz = Lienzo(W, H, s=8, semilla=171 + k)
    if k == 0:
        lz.pintar(lz.desenfocar(lz.elipse(8, 14, 7, 1.6), 0.6), "#0e0c0a", 0.6)
        for xx in (2.5, 13.5):                                    # las estacas
            estaca = lz.trazo([(xx, 14), (xx, 5)], 1.4)
            lz.sombrear(estaca, MADERA[1:7], 1, LUZ, textura=vetas(lz, 0.4, 7, False, 172), fuerza_tex=0.4)
        rollo = lz.elipse(8, 10, 6.2, 3.6)
        vueltas = (np.sin((lz.x - 8) * 2.2) * 0.5 + 0.5)
        lz.sombrear(rollo, CUERDA, 3, LUZ, textura=vetas(lz, 0.3, 5, False, 173) * 0.5 + vueltas * 0.5, fuerza_tex=0.5)
        for xx in (4.5, 7, 9.5, 12):                              # los peldaños asomando
            lz.sombrear(lz.trazo([(xx, 7.4), (xx + 0.6, 12.6)], 1.1), MADERA[2:7], 0.6, LUZ)
        lz.pintar(lz.trazo([(2.5, 8), (5, 9)], 0.6), CUERDA[3])     # los nudos a las estacas
        lz.pintar(lz.trazo([(13.5, 8), (11, 9)], 0.6), CUERDA[3])
        return lz.sprite(contorno=CONTORNO * 0.8)
    # la sombra de la escala sobre la peña
    for xx in (3.5, 12.5):
        lz.pintar(lz.trazo([(xx + 1.2, 0), (xx + 1.2, 16)], 1.0), "#0b0c0e", 0.45)
    largo = 16 if k == 1 else 11
    for xx in (3.5, 12.5):                                        # las dos cuerdas, trenzadas
        cuerda = lz.trazo([(xx, 0), (xx + (0.3 if k == 2 else 0), largo)], 1.2)
        trenza = ((lz.y + (lz.x - xx) * 1.3) % 1.8) / 1.8
        lz.sombrear(cuerda, CUERDA, 0.8, LUZ, textura=trenza, fuerza_tex=0.55)
    peldanos = (3.5, 11.5) if k == 1 else (3.5,)
    for yy in peldanos:                                           # los peldaños de madera, atados
        lz.pintar(lz.trazo([(3.8, yy + 1.1), (12.8, yy + 1.1)], 1.0), "#0b0c0e", 0.5)
        p = lz.trazo([(3, yy), (13, yy)], 1.5)
        lz.sombrear(p, MADERA[2:8], 0.8, LUZ, textura=vetas(lz, 0.4, 9, True, 174 + int(yy)), fuerza_tex=0.4)
        for xx in (3.5, 12.5):
            lz.pintar(lz.circulo(xx, yy, 0.9), CUERDA[1], 0.9)
    if k == 2:
        for xx in (3.5, 12.8):                                    # las puntas deshilachadas
            for d in (-0.6, 0, 0.6):
                lz.pintar(lz.trazo([(xx, 10.5), (xx + d * 1.6, 13.5)], 0.35), CUERDA[3])
    return lz.sprite(contorno=CONTORNO * 0.8)


# el cencerro: de cobre viejo, con su badajo y la correa de cuero
CENCERRO_COL = {"o": "3a1a0c", "c": "9a4e24", "C": "c06a32", "L": "f4b470", "B": "ffe0b0", "h": "5c3e26",
                "H": "a37036", "n": "1e1915"}
CENCERRO_1 = [
    "............",
    "...hHHHh....",
    "..h....H....",
    "...oooo.....",
    "..ocCLLo....",
    "..ocCLBo....",
    "..ocCCLo....",
    ".occCCLLo...",
    ".occCCCLo...",
    ".oooonooo...",
    ".....n......",
    "............",
]
CENCERRO_2 = [
    "............",
    "....hHHHh...",
    "....H....h..",
    ".....oooo...",
    "....oLLCco..",
    "....oBLCco..",
    "....oLCCco..",
    "...oLLCCcco.",
    "...oLCCCcco.",
    "...ooonoooo.",
    "......n.....",
    "............",
]
ICONO = [
    "................",
    "....hHHHHHh.....",
    "...h......H.....",
    "...H......h.....",
    "....oooooo......",
    "...ocCCLLLo.....",
    "...ocCCLLBo.....",
    "...ocCCLLBo.....",
    "..occCCLLLLo....",
    "..occCCCLLLo....",
    "..occcCCCLLLo...",
    ".occcCCCCLLLo...",
    ".oooooonnooooo..",
    ".......nn.......",
    "................",
    "................",
]


def main():
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(aprisco(), "RGBA").save(os.path.join(SALIDA, "aprisco.png"))
    tira([escala(k) for k in range(3)]).save(os.path.join(SALIDA, "escala.png"))
    hoja = Image.new("RGBA", (24, 12), (0, 0, 0, 0))
    hoja.alpha_composite(pixeles(CENCERRO_1, CENCERRO_COL), (0, 0))
    hoja.alpha_composite(pixeles(CENCERRO_2, CENCERRO_COL), (12, 0))
    hoja.save(os.path.join(RAIZ, "arte", "mundos", "raiz", "objetos", "cencerro.png"))
    # el icono de la mochila: el 23.º de objetos.png (índice 22)
    ruta = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    n = max(23, viejos.width // 16)
    iconos = Image.new("RGBA", (16 * n, 16), (0, 0, 0, 0))
    iconos.alpha_composite(viejos.crop((0, 0, min(viejos.width, 16 * 22), 16)), (0, 0))
    if viejos.width > 16 * 23:
        iconos.alpha_composite(viejos.crop((16 * 23, 0, viejos.width, 16)), (16 * 23, 0))
    iconos.alpha_composite(pixeles(ICONO, CENCERRO_COL), (16 * 22, 0))
    iconos.save(ruta)
    print("Objetos de la Cañada del Eco en", SALIDA)


if __name__ == "__main__":
    main()
