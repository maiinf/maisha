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
from pintor import Lienzo, RAIZ, rampa  # noqa: E402
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
    """El campamento de Msafiri, el pangolín viajero y cronista (120×94, la base en el centro de abajo): una tienda
    canadiense grande de lona ocre con remiendos y la entrada abierta (dentro, una manta y una lucecita); un mapa
    clavado en la lona; banderines de los sitios que ha visitado; un farol colgado del mástil; una mesita plegable
    con su diario abierto, el tintero y la pluma; la mochila enorme con la manta enrollada y mapas; a la derecha, el
    trípode con el cazo (el fuego lo pone el juego, animado, en la base + (26, -1))."""
    import pintar_aldea as pa
    from cinematicas import flores
    W, H = 120, 84
    lz = pa._lienzo(W, H, 10, 61)
    suelo = 80
    cx = 44
    LUZ_ = (-0.6, -0.7, 0.5)
    LONA = ["#3a2a14", "#5a4420", "#7e6230", "#a08044", "#c0a05c", "#dcc07c", "#f0dca0"]
    lz.pintar(lz.desenfocar(lz.elipse(cx + 6, suelo, 56, 5), 2), "#0e0c0a", 0.45)
    # los vientos de la tienda, atados a estacas
    for (a, b) in (((cx - 30, 30), (cx - 46, suelo - 2)), ((cx + 30, 30), (cx + 44, suelo - 2)), ((cx - 4, 12), (cx - 30, 14))):
        lz.pintar(lz.trazo([a, b], 0.7), "#c8b48a", 0.9)
    for x in (cx - 46, cx + 44):
        lz.sombrear(lz.trazo([(x, suelo), (x + 1, suelo - 5)], 0.9), pa.MADERA[2:], 0.4, LUZ_)
    # la tienda: dos faldones de lona con caída, el canto de arriba y la entrada abierta
    izq = lz.poligono([(cx - 36, suelo - 2), (cx, 14), (cx, suelo)])
    der = lz.poligono([(cx, 14), (cx + 36, suelo - 2), (cx, suelo)])
    tex = pa.vetas(lz, 0.5, 11, False, semilla=62)
    lz.sombrear(izq, LONA, 8, LUZ_, textura=tex, fuerza_tex=0.25)
    lz.sombrear(der, LONA, 8, LUZ_, textura=tex, fuerza_tex=0.25)
    lz.pintar(der, "#1a1208", 0.25)
    for k in range(5):                                                   # pliegues
        lz.pintar(lz.trazo([(cx - 6 * k - 3, 22 + k * 10), (cx - 8 * k - 6, suelo - 2)], 0.4) * izq, LONA[1], 0.5)
    for (x0, y0, w, h, col) in ((cx - 24, 52, 9, 7, ["#5a2a1a", "#8a4a2a", "#b06a3a"]), (cx + 14, 40, 7, 8, ["#3a4a2a", "#5a7a3a", "#7a9a4a"])):
        rem = lz.poligono([(x0, y0), (x0 + w, y0 + 1), (x0 + w - 1, y0 + h), (x0 - 1, y0 + h - 1)])
        lz.sombrear(rem * np.maximum(izq, der), col, 1, LUZ_)
        for k in range(4):
            lz.pintar(lz.circulo(x0 + 1 + k * (w - 2) / 3, y0 + 0.6, 0.3), "#efe0bf")
    entrada = lz.poligono([(cx - 9, suelo), (cx, 38), (cx + 9, suelo)])
    lz.pintar(entrada, "#140e08")
    lz.sumar_luz(lz.desenfocar(lz.circulo(cx, 66, 4), 4) * entrada, "#ef8a26", 0.5)
    lz.sombrear(lz.elipse(cx, suelo - 3, 7, 2.4), ["#5a2a2a", "#8a3a3a", "#b05a4a"], 0.8, LUZ_)
    for lado in (-1, 1):                                              # las solapas recogidas
        sol = lz.poligono([(cx, 38), (cx + lado * 9, suelo), (cx + lado * 13, suelo - 2), (cx + lado * 4, 40)])
        lz.sombrear(sol, LONA[1:], 1.5, LUZ_)
    lz.sombrear(lz.trazo([(cx, 8), (cx, 15)], 1.0), pa.MADERA[2:], 0.4, LUZ_)              # el mástil
    # el farol colgado del mástil y los banderines de sitios visitados
    lz.pintar(lz.trazo([(cx + 1, 10), (cx + 8, 12), (cx + 8, 16)], 0.6), "#2a1a12")
    farol = pa.rect(lz, cx + 6, 16, cx + 10, 21)
    lz.pintar(farol, rampa(["#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - cx - 8, lz.y - 18.5) / 3, 0, 1)))
    lz.sumar_luz(lz.desenfocar(farol, 4), "#ef8a26", 0.35)
    for k, col in enumerate(("#d84a4a", "#e8c040", "#4a9ad8", "#6ab04a", "#c070d0")):
        x = cx - 30 + k * 6
        y = 30 - k * 3.4
        lz.pintar(lz.poligono([(x, y), (x + 4, y - 0.8), (x + 2, y + 4)]), col)
    lz.pintar(lz.trazo([(cx - 32, 31), (cx - 1, 12)], 0.7), "#8a7454")
    # un mapa clavado en la lona
    mapa = lz.poligono([(cx + 16, 54), (cx + 26, 52), (cx + 27, 62), (cx + 17, 64)])
    lz.sombrear(mapa, ["#a08a5a", "#c8b080", "#e2cea0", "#f4e4c0"], 1, LUZ_)
    lz.pintar(lz.trazo([(cx + 18, 57), (cx + 21, 60), (cx + 25, 56)], 0.4) * mapa, "#8c281e", 0.8)
    lz.pintar(lz.circulo(cx + 17.4, 55, 0.6), "#c89a44")
    # la mesita plegable con el diario, el tintero y la pluma (a la izquierda, delante)
    mx = 12
    for (a, b) in (((mx - 6, suelo), (mx + 5, 66)), ((mx + 6, suelo), (mx - 5, 66))):
        lz.sombrear(lz.trazo([a, b], 0.8), pa.MADERA[2:], 0.4, LUZ_)
    lz.sombrear(pa.rect(lz, mx - 9, 63, mx + 9, 66), pa.MADERA[1:], 0.8, LUZ_, textura=pa.vetas(lz, 0.5, 9), fuerza_tex=0.3)
    lib = lz.poligono([(mx - 7, 63), (mx, 61), (mx + 7, 63), (mx, 64.5)])
    lz.sombrear(lib, ["#a8987a", "#d8c8a6", "#f4ecd8"], 0.5, LUZ_)
    lz.pintar(lz.trazo([(mx, 61), (mx, 64.5)], 0.3), "#5a4a3a")
    for k in range(2):
        lz.pintar(lz.trazo([(mx - 5, 62.6 + k * 0.6), (mx - 1.5, 62 + k * 0.6)], 0.2), "#5a4a3a", 0.8)
    lz.sombrear(lz.elipse(mx + 6, 62, 1.4, 1.2), ["#0a0a14", "#1e1e3a", "#3a3a6a"], 0.4, LUZ_)
    lz.pintar(lz.trazo([(mx + 6, 61.5), (mx + 9, 56)], 0.4), "#efe0bf")
    # la mochila enorme, apoyada a la derecha de la tienda, con la manta enrollada y mapas
    mo = lz.poligono([(102, suelo), (101, 62), (104, 56), (114, 56), (117, 62), (116, suelo)])
    lz.sombrear(mo, ["#3a2414", "#5a3a20", "#7e5430", "#a07040", "#c08a54"], 3, LUZ_)
    lz.sombrear(pa.rect(lz, 103, 66, 115, 72), ["#3a2414", "#5a3a20", "#7e5430"], 1, LUZ_)
    lz.sombrear(lz.elipse(109, 54, 9, 3), ["#2a3a5a", "#3a5a8a", "#5a7ab0", "#8aa8d0"], 1.2, LUZ_)
    for k in range(3):
        lz.sombrear(lz.trazo([(106 + k * 2.6, 56), (104 + k * 3, 46)], 1.2), ["#a08a5a", "#e2cea0", "#f4e4c0"], 0.5, LUZ_)
    # el trípode con el cazo, a la derecha (el fuego lo pone el juego debajo)
    tx = 86
    for (a, b) in (((tx - 7, suelo), (tx, 62)), ((tx + 7, suelo), (tx, 62))):
        lz.sombrear(lz.trazo([a, b], 0.9), pa.MADERA[2:], 0.4, LUZ_)
    lz.pintar(lz.trazo([(tx, 62), (tx, 67)], 0.35), "#2a2a2a")
    lz.sombrear(lz.elipse(tx, 70, 4, 3), ["#141416", "#2a2a2e", "#46464c", "#6e6e74"], 1, LUZ_)
    for k in range(5):
        a = k / 5 * 2 * np.pi
        lz.sombrear(lz.elipse(tx + np.cos(a) * 6, suelo - 1 + np.sin(a) * 1.5, 1.8, 1.2), ["#3a3a3a", "#6a6a6a", "#9a9a9a"], 0.4, LUZ_)
    flores(lz, 8, (2, suelo - 4, 30, suelo), [["#b2721a", "#df9022", "#fde27e"], ["#8f2532", "#d5525e", "#f4b39a"]], semilla=63, tam=0.6)
    pa._hierba_pie(lz, 4, 116, suelo - 2, 64)
    return lz.sprite(contorno=0.4)


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
