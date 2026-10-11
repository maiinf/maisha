"""LOS OBJETOS DEL SENDERO DEL PUENTE, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_sendero.py

Genera:
  arte/mundos/raiz/sendero/eco.png          2 × 26×40   el ECO PERDIDO: una piedra alta tallada con una espiral
                                                         que guarda una voz (apagada / encendida)
  arte/mundos/raiz/sendero/campamento.png   64×44       el campamento de Msafiri: tienda de lona remendada,
                                                         mochila, mapas enrollados y un trípode con su cazo
  arte/mundos/raiz/objetos/pagina.png       2 × 12×12   una página del diario de Msafiri (se agita con el viento)
  y su icono (16×16) en arte/interfaz/objetos.png (el 19.º)
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_casa_shamba import vetas, rect  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "sendero")
LUZ = (-0.6, -0.7, 0.5)
PIEDRA = ["#1f211c", "#2e302a", "#41443a", "#525649", "#666b5b", "#7a806d", "#8d9381", "#a0a596"]
MUSGO = ["#1d2e18", "#2b4220", "#3f582f", "#526d38", "#6a8246", "#829856"]
ECO = ["#1c3535", "#346161", "#4c8d8d", "#6db0b0", "#9fd0d0", "#d8f0ec"]
LONA = ["#3d3214", "#5c4a22", "#7a6431", "#958043", "#b09c5c", "#c9b77d"]
REMIENDO = ["#3a1a14", "#5e2a22", "#7f3d30", "#a35548"]
MADERA = ["#251812", "#3a261d", "#492e23", "#5b392b", "#6d4534", "#7f513d", "#905c45"]
CONTORNO = 0.42


def tira(imgs):
    w = sum(i.shape[1] for i in imgs)
    h = max(i.shape[0] for i in imgs)
    out = np.zeros((h, w, 4), np.uint8)
    x = 0
    for i in imgs:
        out[h - i.shape[0]:, x:x + i.shape[1]] = i
        x += i.shape[1]
    return Image.fromarray(out, "RGBA")


def eco(encendido):
    """Un menhir de piedra gris, algo inclinado, con una espiral tallada que brilla verde-agua (la voz),
    musgo en la base, piedrecitas alrededor y líquenes. Encendido: la espiral y las grietas brillan mucho más."""
    W, H = 26, 40
    lz = Lienzo(W, H, s=6, semilla=51)
    suelo = 38
    lz.pintar(lz.desenfocar(lz.elipse(13, suelo, 11, 2.4), 0.8), "#0e140c", 0.55)
    forma = lz.poligono([(6, suelo), (5, 22), (7, 10), (11, 3.5), (15, 3), (19, 8), (21, 20), (20, suelo)])
    textura = lz.ruido(1.2, 3, semilla=52) * 0.6 + vetas(lz, 0.6, 9, False, 53) * 0.4
    lz.sombrear(forma, PIEDRA, 7, LUZ, textura=textura, fuerza_tex=0.4, recorte=("#a0a596", 0.3), recorte_dir=(-1, -0.4))
    # vetas y grietas de la piedra
    grieta = lz.trazo([(9, 12), (10, 18), (9, 24)], 0.6) + lz.trazo([(17, 27), (16, 33)], 0.5)
    lz.pintar(np.clip(grieta, 0, 1) * forma, "#1f211c", 0.8)
    # la espiral tallada (surco oscuro con el brillo de la voz dentro)
    t = np.linspace(0, 3.4 * np.pi, 80)
    r = 0.55 + t * 0.42
    puntos = [(13 + np.cos(a) * rr, 18 + np.sin(a) * rr * 1.05) for a, rr in zip(t, r)]
    surco = lz.trazo(puntos, 1.4) * forma
    lz.pintar(surco, "#1c3535", 0.95)
    nucleo = lz.trazo(puntos, 0.6) * forma
    lz.pintar(nucleo, ECO[3] if encendido else ECO[2], 1.0)
    # tres marcas pequeñas debajo (como palabras antiguas)
    for k, x in enumerate((10, 13, 16)):
        m = lz.trazo([(x, 29 + (k % 2)), (x, 31 + (k % 2))], 0.7) * forma
        lz.pintar(m, ECO[2] if encendido else "#2e302a", 0.9)
    if encendido:
        lz.brillo(nucleo, ECO[4], 1.6, 0.9)
        lz.brillo(nucleo, ECO[5], 0.5, 0.6)
    else:
        lz.brillo(nucleo, ECO[3], 1.0, 0.35)
    # líquenes y musgo en la base y en los salientes
    musgo = np.clip((lz.ruido(1.6, 3, semilla=54) - 0.55) * 4, 0, 1) * forma * np.clip((lz.y - 28) / 6, 0, 1)
    lz.pintar(musgo, MUSGO[3], 0.9)
    lz.pintar(musgo * (lz.ruido(0.6, 2, semilla=55) > 0.55), MUSGO[5], 0.7)
    liquen = np.clip((lz.ruido(0.9, 2, semilla=56) - 0.8) * 6, 0, 1) * forma
    lz.pintar(liquen, "#c9b77d", 0.6)
    # piedrecitas alrededor
    for (x, y, rr) in ((4, 37, 1.6), (22, 37.5, 1.8), (8, 39, 1.1), (19, 39.2, 1.0)):
        p = lz.elipse(x, y, rr * 1.3, rr)
        lz.sombrear(p, PIEDRA[1:], 1.2, LUZ)
    return lz.sprite(contorno=CONTORNO)


def campamento():
    """El campamento de Msafiri: tienda canadiense de lona ocre con dos remiendos rojizos, la entrada abierta
    (oscura, con una manta dentro), los vientos atados a estacas, la mochila enorme apoyada con mapas enrollados
    y un trípode de palos con un cazo encima (el fuego lo pone el juego, animado)."""
    W, H = 64, 44
    lz = Lienzo(W, H, s=6, semilla=61)
    suelo = 42
    lz.pintar(lz.desenfocar(lz.elipse(30, suelo, 28, 3), 0.9), "#0e140c", 0.5)
    # la tienda: dos faldones en escorzo (el de la derecha, en sombra) y la cumbrera
    izq = lz.poligono([(4, suelo - 2), (22, 8), (26, 8), (18, suelo)])
    der = lz.poligono([(26, 8), (22, 8), (18, suelo), (44, suelo - 1), (46, 12)])
    pliegues = np.sin(lz.x * 0.9 - lz.y * 0.4) * 0.5 + 0.5
    lz.sombrear(der, LONA[:5], 6, LUZ, textura=pliegues * 0.5 + vetas(lz, 0.5, 9, False, 62) * 0.5, fuerza_tex=0.35)
    lz.sombrear(izq, LONA[1:], 5, LUZ, textura=vetas(lz, 0.5, 9, False, 63), fuerza_tex=0.3)
    # la entrada abierta (en el faldón de la izquierda) con la manta dentro
    puerta = lz.poligono([(10, suelo - 1), (21, 14), (18, suelo)])
    lz.pintar(puerta, "#140e0a")
    manta = lz.poligono([(12, suelo - 1), (17, 32), (18, suelo)])
    lz.sombrear(manta, ["#1c3535", "#346161", "#4c8d8d"], 2, LUZ)
    solapa = lz.poligono([(10, suelo - 1), (21, 14), (8, 30)])
    lz.sombrear(solapa, LONA[2:], 3, LUZ)
    # remiendos cosidos
    for (x, y, w, h) in ((30, 22, 6, 5), (37, 31, 5, 4)):
        rr = rect(lz, x, y, x + w, y + h)
        lz.sombrear(rr, REMIENDO, 1.5, LUZ)
        costura = np.clip(rr - lz.desenfocar(rr, 0.3) * 0.0, 0, 1) * ((lz.x * 2 + lz.y * 2) % 2 < 0.6)
        lz.pintar(costura * (np.clip(lz.distancia(rr), 0, 1) < 0.6), "#e2cea0", 0.7)
    # el palo de la cumbrera y los vientos
    lz.pintar(lz.trazo([(24, 8), (24, 4)], 1.2), MADERA[3])
    for (a, b) in (((22, 9), (2, 30)), ((46, 13), (58, 34))):
        lz.pintar(lz.trazo([a, b], 0.4), "#c9b77d", 0.9)
    for (x, y) in ((2, 31), (58, 35)):
        lz.pintar(lz.trazo([(x, y - 2), (x, y + 2)], 1.0), MADERA[4])
    # la mochila enorme apoyada a la derecha, con mapas enrollados
    mochila = lz.elipse(51, 34, 7, 8)
    lz.sombrear(mochila, MADERA[1:], 5, LUZ, textura=vetas(lz, 0.4, 7, True, 64), fuerza_tex=0.3)
    correa = lz.trazo([(46, 30), (55, 31)], 0.9) * mochila
    lz.pintar(correa, MADERA[0], 0.9)
    for (x0, y0, x1, y1, c) in ((47, 25, 53, 22, "#e2cea0"), (50, 26, 58, 24, "#c9b77d")):
        rollo = lz.trazo([(x0, y0), (x1, y1)], 2.4)
        lz.sombrear(rollo, ["#5c3e26", "#a57559", c, "#fff8e8"], 1.2, LUZ)
    # el trípode con el cazo (delante, a la izquierda de la mochila)
    for (a, b) in (((36, 41), (40, 30)), ((44, 41), (40, 30)), ((40, 42), (40, 30))):
        lz.pintar(lz.trazo([a, b], 0.9), MADERA[3])
    cazo = lz.elipse(40, 34.5, 3.2, 2.4)
    lz.sombrear(cazo, ["#16171a", "#2b2c30", "#45474c", "#65676c"], 2, LUZ)
    lz.pintar(lz.trazo([(40, 30), (40, 32)], 0.4), "#2b2c30")
    # piedras del fuego
    for k in range(6):
        a = k / 6 * 2 * np.pi
        p = lz.elipse(40 + np.cos(a) * 4.2, 41.5 + np.sin(a) * 1.6, 1.4, 1.0)
        lz.sombrear(p, PIEDRA[1:], 1.0, LUZ)
    return lz.sprite(contorno=CONTORNO)


PAG_COL = {"b": "5c3e26", "n": "c9b77d", "N": "e2cea0", "B": "fff8e8", "t": "533b2d", "a": "4c8d8d"}
PAGINA_1 = [
    "............",
    "...bbbbbb...",
    "..bNNNBBBb..",
    "..bNttNBBb..",
    "..bNNNNNBb..",
    "..bNttttNb..",
    "..bnNNNNNb..",
    "..bnNtttNb..",
    "..bnNNaNNb..",
    "..bnnNNNNb..",
    "...bbbbbb...",
    "............",
]
PAGINA_2 = [
    "............",
    "....bbbbbb..",
    "...bNNNBBBb.",
    "..bNttNBBb..",
    "..bNNNNNBb..",
    "..bNttttNb..",
    "..bnNNNNNb..",
    "..bnNtttNb..",
    "..bnNNaNNb..",
    "..bnnNNNNb..",
    "..bbbbbbb...",
    "............",
]
ICONO = [
    "................",
    "................",
    "....bbbbbbbb....",
    "...bNNNNNBBBb...",
    "...bNttNNNBBb...",
    "...bNNNNNNNBb...",
    "...bNtttttNNb...",
    "...bNNNNNNNNb...",
    "...bnNttttNNb...",
    "...bnNNNNNNNb...",
    "...bnNtttNaNb...",
    "...bnNNNNaaNb...",
    "...bnnNNNNNNb...",
    "....bbbbbbbb....",
    "................",
    "................",
]


def pixeles(filas):
    w, h = len(filas[0]), len(filas)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y, f in enumerate(filas):
        for x, ch in enumerate(f):
            if ch != ".":
                c = PAG_COL[ch]
                img.putpixel((x, y), tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    return img


def main():
    os.makedirs(SALIDA, exist_ok=True)
    tira([eco(False), eco(True)]).save(os.path.join(SALIDA, "eco.png"))
    Image.fromarray(campamento(), "RGBA").save(os.path.join(SALIDA, "campamento.png"))
    hoja = Image.new("RGBA", (24, 12), (0, 0, 0, 0))
    hoja.alpha_composite(pixeles(PAGINA_1), (0, 0))
    hoja.alpha_composite(pixeles(PAGINA_2), (12, 0))
    hoja.save(os.path.join(RAIZ, "arte", "mundos", "raiz", "objetos", "pagina.png"))
    # el icono de la mochila: el 19.º de objetos.png (índice 18)
    ruta = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    n = max(19, viejos.width // 16)
    iconos = Image.new("RGBA", (16 * n, 16), (0, 0, 0, 0))
    iconos.alpha_composite(viejos.crop((0, 0, min(viejos.width, 16 * 18), 16)), (0, 0))
    if viejos.width > 16 * 19:
        iconos.alpha_composite(viejos.crop((16 * 19, 0, viejos.width, 16)), (16 * 19, 0))
    iconos.alpha_composite(pixeles(ICONO), (16 * 18, 0))
    iconos.save(ruta)
    print("Objetos del Sendero del Puente en", SALIDA)


if __name__ == "__main__":
    main()
