"""LOS OBJETOS DE LA SENDA DE LOS SURCOS, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_senda.py

Genera:
  arte/mundos/raiz/senda/horreo.png      64×64       la casa de Sungura, la liebre guardasemillas: un hórreo (granero
                                                     alzado sobre pies de piedra con sus losas para que no suban los
                                                     ratones), paredes de tablas, tejado de paja, ristras de mazorcas
                                                     colgadas a secar, sacos de semillas y una escalerita
  arte/mundos/raiz/senda/cuervo.png      6 × 26×22   el CUERVO DE ÓXIDO (enemigo): alas arriba, alas abajo, en picado,
                                                     posado picoteando, atontado y golpeado (blanco en el juego)
  arte/mundos/raiz/objetos/mazorca.png   2 × 12×12   una mazorca de maíz antiguo de Sungura
  y su icono (16×16) en arte/interfaz/objetos.png (el 22.º)
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_casa_shamba import vetas, rect  # noqa: E402
from pintar_pasarelas import tira, pixeles, MADERA, GIZA, CONTORNO, JUNCO, PIEDRA  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "senda")
LUZ = (-0.6, -0.7, 0.5)
MAIZ = ["#5a2a10", "#8a4418", "#c0702a", "#e09a3a", "#f2c45a", "#fde27e"]
MAIZ_ROJO = ["#4a1418", "#7a2028", "#a8343a", "#cc5a52"]
SACO = ["#4a3a24", "#6e5836", "#94784c", "#b89c6a", "#d6c090"]
# el cuervo: plumas de hierro oscuro con óxido
PLUMA = ["#0e0e12", "#1a1a20", "#2a2a32", "#3c3c46", "#52525e", "#6c6c78"]
OXIDO = ["#4a1e0e", "#7a3418", "#a84e24", "#d07a3a"]


def horreo():
    """El hórreo de Sungura, la liebre guardasemillas (116×104, la base en el centro de abajo): un granero alto sobre
    cuatro pies de piedra con sus losas redondas (para que no suban los ratones); paredes de listones con rendijas;
    tejado de paja a dos aguas con una cruz de madera; ristras de mazorcas (amarillas y rojas) colgadas; una
    escalera de piedra suelta; tarros de semillas con etiquetas en un estante; sacos; y un semillero con brotes."""
    import pintar_aldea as pa
    W, H = 116, 96
    lz = pa._lienzo(W, H, 8, 121)
    suelo = 92
    cx = 56
    LUZ_ = (-0.6, -0.7, 0.5)
    MAD = ["#1e140e", "#33231a", "#4a3424", "#634733", "#7d5c42", "#977452", "#b08c66"]
    PIE = ["#3a3630", "#5e5850", "#868070", "#aaa392", "#c8c0ac"]
    lz.pintar(lz.desenfocar(lz.elipse(cx, suelo, 52, 5), 2), "#0e0c0a", 0.45)
    # los cuatro pies de piedra con sus losas redondas
    for x in (cx - 28, cx - 10, cx + 10, cx + 28):
        lz.sombrear(pa.rect(lz, x - 3, 66, x + 3, suelo - 1), PIE, 1.5, LUZ_, textura=lz.ruido(0.6, 2, semilla=int(x)), fuerza_tex=0.35)
        losa = lz.elipse(x, 65, 6.5, 2.4)
        lz.sombrear(losa, PIE, 1.2, LUZ_)
    # la caja del hórreo: listones verticales con rendijas
    caja = pa.rect(lz, cx - 34, 36, cx + 34, 64)
    list_ = (np.abs(np.sin((lz.x - cx) / 3 * np.pi)) < 0.14).astype(float)
    lz.sombrear(caja, MAD, 6, LUZ_, textura=pa.vetas(lz, 0.5, 15, False, semilla=122) * (1 - list_ * 0.85), fuerza_tex=0.5)
    for y in (36, 50, 63):
        lz.sombrear(pa.rect(lz, cx - 35, y - 1, cx + 35, y + 1), MAD[1:], 0.6, LUZ_)
    for x in (cx - 34, cx, cx + 34):
        lz.sombrear(pa.rect(lz, x - 1.2, 36, x + 1.2, 64), MAD[1:], 0.6, LUZ_)
    lz.sombrear(pa.rect(lz, cx - 6, 44, cx + 6, 62), ["#251812", "#3d2418", "#5a3826", "#7a4e35"], 1.5, LUZ_, textura=pa.vetas(lz, 0.5, 9, False), fuerza_tex=0.4)
    lz.pintar(lz.circulo(cx + 4, 53, 0.7), "#c89a44")
    # el tejado de paja a dos aguas con la cruz de madera
    tej = lz.poligono([(cx - 42, 40), (cx, 10), (cx + 42, 40), (cx + 38, 42), (cx, 16), (cx - 38, 42)])
    tej = np.maximum(tej, lz.poligono([(cx - 42, 40), (cx, 10), (cx + 42, 40)]))
    pa.paja(lz, tej, semilla=123, capas=5.0, y0=10)
    pa.flecos(lz, cx - 42, cx + 42, 40.5, 3.0, semilla=124)
    lz.sombrear(lz.trazo([(cx, 10), (cx, 0)], 1.2) + lz.trazo([(cx - 4, 4), (cx + 4, 4)], 1.2), MAD[2:], 0.4, LUZ_)
    # ristras de mazorcas colgando del alero
    for x, col in ((cx - 28, MAIZ), (cx - 22, MAIZ_ROJO + ["#e8806a"]), (cx + 20, MAIZ), (cx + 26, MAIZ), (cx + 31, MAIZ_ROJO + ["#e8806a"])):
        lz.pintar(lz.trazo([(x, 41), (x, 43)], 0.4), "#3a2a18")
        for k in range(3):
            maz = lz.elipse(x + (k % 2) * 1.2 - 0.6, 45.5 + k * 4, 1.6, 2.4)
            lz.sombrear(maz, col, 0.6, LUZ_, textura=(np.sin(lz.x * 5) * np.sin(lz.y * 5) > 0).astype(float), fuerza_tex=0.3)
    # la escalera de piedra suelta (no toca el hórreo: así no suben los ratones)
    for k in range(4):
        y = suelo - 4 - k * 6
        lz.sombrear(pa.rect(lz, cx - 8 - k * 0.6, y, cx + 8 + k * 0.6, y + 4), PIE, 1, LUZ_)
    # el estante con tarros de semillas y los sacos
    lz.sombrear(pa.rect(lz, cx - 54, 72, cx - 36, 74), MAD[2:], 0.5, LUZ_)
    for (a, b) in (((cx - 52, 74), (cx - 52, suelo)), ((cx - 38, 74), (cx - 38, suelo))):
        lz.sombrear(lz.trazo([a, b], 0.8), MAD[2:], 0.3, LUZ_)
    for k, col in enumerate((["#3a5a1a", "#6a9a3a", "#a8d060"], ["#6a3a1a", "#b07040", "#e0a070"], ["#4a3a6a", "#7a6ab0", "#b0a0e0"], ["#7a6a1a", "#c0a838", "#f0e070"])):
        x = cx - 51 + k * 4.4
        lz.sombrear(lz.elipse(x, 69, 1.8, 2.6), ["#8ab0b0", "#c8e0e0"] + col[1:], 0.5, LUZ_)
        lz.pintar(pa.rect(lz, x - 1, 65.6, x + 1, 66.6), "#8a6440")
        lz.pintar(pa.rect(lz, x - 1.2, 68.4, x + 1.2, 70), "#efe0bf")
    for (x, y) in ((cx + 40, suelo), (cx + 47, suelo + 1)):
        saco = lz.poligono([(x - 4.5, y), (x - 5, y - 8), (x - 2, y - 11), (x + 2, y - 11), (x + 5, y - 8), (x + 4.5, y)])
        lz.sombrear(saco, SACO, 1.5, LUZ_)
        lz.pintar(lz.trazo([(x - 2.4, y - 9.6), (x + 2.4, y - 9.6)], 0.5), "#47291c")
    # el semillero con brotes
    sem = pa.rect(lz, cx + 18, suelo - 6, cx + 34, suelo)
    lz.sombrear(sem, MAD, 1, LUZ_, textura=pa.vetas(lz, 0.5, 9), fuerza_tex=0.4)
    lz.pintar(pa.rect(lz, cx + 19, suelo - 6, cx + 33, suelo - 4.6), "#3a2a1a")
    for k in range(6):
        x = cx + 20 + k * 2.4
        lz.pintar(lz.trazo([(x, suelo - 5), (x, suelo - 8)], 0.4), "#3e9a35")
        lz.pintar(lz.elipse(x - 0.8, suelo - 8.4, 1.0, 0.5, 30), "#8fe06a")
        lz.pintar(lz.elipse(x + 0.8, suelo - 8.6, 1.0, 0.5, -30), "#6fcf4f")
    pa._hierba_pie(lz, cx - 54, cx + 56, suelo - 2, 125)
    return lz.sprite(contorno=0.4)


def cuervo(estado):
    """El CUERVO DE ÓXIDO: un cuervo de plumas de hierro, con manchas de óxido, pico de hierro y un ojo violeta de
    Giza. 0 alas arriba · 1 alas abajo · 2 en picado (alas recogidas, pico delante) · 3 posado, picoteando ·
    4 atontado (plumas revueltas, ojo en espiral) · 5 golpeado (igual que 4; se dibuja blanco en el juego).
    Mira a la derecha."""
    W, H = 26, 22
    lz = Lienzo(W, H, s=8, semilla=131 + estado)
    posado = estado in (3, 4, 5)
    cy = 14 if posado else 11
    # el cuerpo (un huso), la cabeza y la cola
    ang = -18 if estado == 2 else (20 if estado == 3 else 0)
    cuerpo = lz.elipse(12, cy, 7, 4.2, ang)
    cabeza = lz.circulo(18 + (1.5 if estado == 2 else 0), cy - (2.5 if estado != 3 else -1.5), 3.4)
    cola = lz.poligono([(6, cy - 1), (1, cy - 3 + (2 if estado == 2 else 0)), (0, cy + 1), (5, cy + 2)])
    forma = np.clip(cuerpo + cabeza + cola, 0, 1)
    lz.sombrear(forma, PLUMA, 3, LUZ, textura=lz.ruido(0.8, 2, semilla=132), fuerza_tex=0.35,
                recorte=("#9a8aa8", 0.35), recorte_dir=(-0.6, -1))
    oxido = np.clip((lz.ruido(1.5, 2, semilla=133) - 0.6) * 4, 0, 1) * forma
    lz.pintar(oxido, OXIDO[2], 0.75)
    lz.pintar((lz.ruido(0.5, 1, semilla=134) > 0.85) * oxido, OXIDO[3], 0.8)
    # el pico de hierro
    hx, hy = (19.5 + (1.5 if estado == 2 else 0), cy - (2.5 if estado != 3 else -1.5))
    if estado == 3:
        pico = lz.poligono([(hx + 2, hy - 1), (hx + 5, hy + 3.5), (hx + 1.5, hy + 1.2)])
    else:
        pico = lz.poligono([(hx + 2, hy - 1.2), (hx + 7, hy + 0.4), (hx + 2, hy + 1.2)])
    lz.sombrear(pico, ["#1a1a1c", "#45474d", "#80838a", "#c0c2c6"], 0.8, LUZ)
    # el ojo violeta (en espiral si está atontado)
    ox, oy = hx + 0.3, hy - 0.8
    if estado in (4, 5):
        t = np.linspace(0, 3 * np.pi, 20)
        lz.pintar(lz.trazo([(ox + np.cos(a) * a * 0.12, oy + np.sin(a) * a * 0.12) for a in t], 0.35), GIZA[3])
    else:
        lz.pintar(lz.circulo(ox, oy, 0.9), GIZA[3])
        lz.brillo(lz.circulo(ox, oy, 0.6), GIZA[3], 1.0, 0.9)
        lz.pintar(lz.circulo(ox + 0.2, oy - 0.2, 0.3), "#f4e8ff")
    # las alas
    if estado == 0:
        ala = lz.poligono([(7, cy - 1), (15, cy - 1), (14, cy - 6), (9, cy - 11), (2, cy - 11), (5, cy - 6)])
    elif estado == 1:
        ala = lz.poligono([(7, cy), (15, cy), (13, cy + 5), (8, cy + 9), (2, cy + 9), (5, cy + 4)])
    elif estado == 2:
        ala = lz.elipse(11, cy - 0.5, 6, 2.2, -18)
    elif estado == 3:
        ala = lz.elipse(10, cy - 1, 5.5, 2.6, 20)
    else:
        ala = lz.poligono([(8, cy - 1), (14, cy - 2), (12, cy - 7), (6, cy - 6)]) + lz.poligono([(10, cy + 1), (14, cy), (13, cy + 5), (8, cy + 5)])
    ala = np.clip(ala, 0, 1)
    lz.sombrear(ala, PLUMA[1:], 2, LUZ, textura=((lz.x + lz.y * 0.3) % 2.2 < 0.8) * 1.0, fuerza_tex=0.4)
    if estado in (0, 1):
        # las plumas largas de la punta del ala, separadas
        for k in range(4):
            px_ = 2.5 + k * 1.8
            py_ = cy - 11 if estado == 0 else cy + 9
            lz.pintar(lz.trazo([(px_ + 1.5, py_ + (2.5 if estado == 0 else -2.5)), (px_, py_ + (-0.5 if estado == 0 else 0.5))], 0.9, 0.4), PLUMA[2])
    lz.pintar(np.clip((lz.ruido(1.2, 2, semilla=135) - 0.65) * 4, 0, 1) * ala, OXIDO[1], 0.7)
    # las patas (posado) y las plumas revueltas (atontado)
    if posado:
        for x in (11, 14):
            lz.pintar(lz.trazo([(x, cy + 3.5), (x + 0.5, 20.5)], 0.6), "#5f626a")
            lz.pintar(lz.trazo([(x - 1, 20.8), (x + 2, 20.8)], 0.5), "#5f626a")
        lz.pintar(lz.desenfocar(lz.elipse(13, 21, 7, 1.2), 0.6), "#0e0c0a", 0.5)
    if estado in (4, 5):
        for (x, y) in ((10, cy - 5), (13, cy - 6), (16, cy - 6)):
            lz.pintar(lz.trazo([(x, y + 2), (x + 0.6, y - 1)], 0.5), PLUMA[4])
    return lz.sprite(contorno=CONTORNO)


MAZORCA_COL = {"o": "5a2a10", "c": "c0702a", "C": "e09a3a", "L": "f2c45a", "B": "fde27e", "h": "3e6a2a", "H": "6a8246", "r": "a8343a"}
MAZORCA_1 = [
    "............",
    ".......h....",
    "......hH....",
    ".....oLBo...",
    ".....cCLB...",
    "....ocLCLo..",
    "....crCLCh..",
    "...ocLCLCH..",
    "...cCLrLHh..",
    "...hcCLCH...",
    "....hhHh....",
    "............",
]
MAZORCA_2 = [
    "............",
    "....h.......",
    "....Hh......",
    "...oBLo.....",
    "...BLCc.....",
    "..oLCLco....",
    "..hCLCrc....",
    "..HCLCLco...",
    "..hHLrLCc...",
    "...HCLCch...",
    "....hHhh....",
    "............",
]
ICONO = [
    "................",
    ".........hH.....",
    "........hH......",
    ".......oLBo.....",
    "......ocLBLo....",
    "......cCLCLc....",
    ".....ocLCrCLo...",
    ".....cCLCLCLc...",
    ".....crLCLCLh...",
    "....ocCLCLrCH...",
    "....cCLrLCLHh...",
    "....hcCLCLCH....",
    "...hHcCLCLHh....",
    "...hHhcCLHh.....",
    "....hHhhHh......",
    "................",
]


def main():
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(horreo(), "RGBA").save(os.path.join(SALIDA, "horreo.png"))
    tira([cuervo(k) for k in range(6)]).save(os.path.join(SALIDA, "cuervo.png"))
    hoja = Image.new("RGBA", (24, 12), (0, 0, 0, 0))
    hoja.alpha_composite(pixeles(MAZORCA_1, MAZORCA_COL), (0, 0))
    hoja.alpha_composite(pixeles(MAZORCA_2, MAZORCA_COL), (12, 0))
    hoja.save(os.path.join(RAIZ, "arte", "mundos", "raiz", "objetos", "mazorca.png"))
    # el icono de la mochila: el 22.º de objetos.png (índice 21)
    ruta = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    n = max(22, viejos.width // 16)
    iconos = Image.new("RGBA", (16 * n, 16), (0, 0, 0, 0))
    iconos.alpha_composite(viejos.crop((0, 0, min(viejos.width, 16 * 21), 16)), (0, 0))
    if viejos.width > 16 * 22:
        iconos.alpha_composite(viejos.crop((16 * 22, 0, viejos.width, 16)), (16 * 22, 0))
    iconos.alpha_composite(pixeles(ICONO, MAZORCA_COL), (16 * 21, 0))
    iconos.save(ruta)
    print("Objetos de la Senda de los Surcos en", SALIDA)


if __name__ == "__main__":
    main()
