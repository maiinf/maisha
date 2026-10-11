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
    W, H = 64, 64
    lz = Lienzo(W, H, s=6, semilla=121)
    suelo = 61
    lz.pintar(lz.desenfocar(lz.elipse(33, suelo, 28, 3.5), 1.2), "#0e0c0a", 0.5)
    # los pies de piedra (pegollos) con sus losas redondas encima (las «mueles»)
    for x in (12, 26, 40, 54):
        pie = lz.poligono([(x - 3, suelo), (x - 2, 44), (x + 2, 44), (x + 3, suelo)])
        lz.sombrear(pie, PIEDRA[1:], 2.5, LUZ, textura=lz.ruido(1.2, 2, semilla=x), fuerza_tex=0.4)
        losa = lz.elipse(x, 43.5, 5, 1.8)
        lz.sombrear(losa, PIEDRA[2:], 1.5, LUZ)
    # la caja de tablas verticales (frente y lado en escorzo)
    frente = rect(lz, 6, 22, 52, 42)
    lz.sombrear(frente, MADERA[2:], 6, LUZ, textura=vetas(lz, 0.45, 13, False, 122), fuerza_tex=0.4)
    lz.pintar(frente * ((lz.x % 3.5) < 0.5), MADERA[0], 0.75)
    lado = lz.poligono([(52, 22), (60, 18), (60, 38), (52, 42)])
    lz.sombrear(lado, MADERA[1:5], 3, LUZ, textura=vetas(lz, 0.45, 13, False, 123), fuerza_tex=0.4)
    lz.pintar(lado * ((lz.y % 3.5) < 0.5), MADERA[0], 0.6)
    # una puertecita y un ventanuco con celosía
    puerta = rect(lz, 26, 28, 33, 42)
    lz.sombrear(puerta, MADERA[1:5], 2, LUZ, textura=vetas(lz, 0.4, 9, False, 124), fuerza_tex=0.4)
    lz.pintar(lz.circulo(31.5, 35, 0.6), "#c9b07e")
    reja = rect(lz, 39, 27, 47, 33)
    lz.pintar(reja, "#140e0a")
    lz.pintar(reja * (((lz.x - lz.y) % 2.4) < 0.6), MADERA[4])
    # el tejado de paja a cuatro aguas, con el borde deshilachado
    hilos = np.sin(lz.x * 3.1 + lz.y * 0.9) * 0.5 + 0.5
    faldon = lz.poligono([(30, 4), (36, 3), (63, 18), (54, 23)])
    lz.sombrear(faldon, JUNCO[:5], 4, LUZ, textura=hilos * 0.6 + vetas(lz, 0.3, 7, False, 126) * 0.4, fuerza_tex=0.5)
    tejado = lz.poligono([(2, 23.5), (30, 4), (36, 3), (56, 23.5)])
    lz.sombrear(tejado, JUNCO, 6, LUZ, textura=hilos * 0.6 + vetas(lz, 0.3, 7, False, 125) * 0.4, fuerza_tex=0.5)
    flecos = np.zeros((lz.H, lz.W))
    for k in range(28):
        x0 = 3 + k * 1.9
        flecos = np.maximum(flecos, lz.trazo([(x0, 23), (x0 + 0.4, 25.5 + (k % 3))], 0.5))
    lz.pintar(flecos, JUNCO[4], 0.9)
    lz.pintar(lz.trazo([(30, 4), (36, 3)], 1.4), JUNCO[1])
    # ristras de mazorcas colgadas a secar bajo el alero (amarillas y alguna roja)
    for (x, n) in ((10, 4), (16, 3), (48, 4)):
        for k in range(n):
            col = MAIZ_ROJO if (x + k) % 5 == 0 else MAIZ
            m = lz.elipse(x + (k % 2) * 1.2, 27 + k * 3.1, 1.5, 1.9)
            lz.sombrear(m, col, 1, LUZ, textura=((lz.y % 1.2) < 0.5) * 1.0, fuerza_tex=0.3)
        lz.pintar(lz.trazo([(x + 0.5, 24.5), (x + 0.5, 26)], 0.4), JUNCO[5])
    # sacos de semillas al pie, y una escalerita de mano apoyada
    for (x, y, r) in ((14, suelo - 3, 4.2), (20, suelo - 2.5, 3.6), (46, suelo - 3, 4.0)):
        saco = lz.elipse(x, y, r, r * 1.05)
        lz.sombrear(saco, SACO, r, LUZ, textura=lz.ruido(0.6, 2, semilla=int(x)), fuerza_tex=0.3)
        lz.pintar(lz.trazo([(x - 1.4, y - r * 0.9), (x + 1.4, y - r * 0.9)], 0.6), "#8a3a1a")
        lz.pintar(lz.elipse(x, y - r * 0.95, 1.6, 0.8), MAIZ[4], 0.9)
    for xx in (33, 37):
        lz.pintar(lz.trazo([(xx, suelo), (xx + 1, 42)], 0.8), MADERA[4])
    for k in range(5):
        y = suelo - 2 - k * 3.6
        lz.pintar(lz.trazo([(33 + k * 0.05, y), (37 + k * 0.1, y)], 0.7), MADERA[5])
    return lz.sprite(contorno=CONTORNO)


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
