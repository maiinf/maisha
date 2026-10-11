"""LOS OBJETOS DE LAS PASARELAS, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_pasarelas.py

Genera:
  arte/mundos/raiz/pasarelas/palafito.png    64×60       la cabaña de Korongo sobre pilotes: tejado de juncos, paredes de
                                                         tablas, una red colgada, un farolillo y la escalerilla al agua
  arte/mundos/raiz/pasarelas/rana.png        6 × 22×20   la RANA DE PIEDRA (enemigo): sentada, agazapada, saltando,
                                                         aterrizando, atontada y golpeada (blanca)
  arte/mundos/raiz/objetos/nasa.png          2 × 12×12   una nasa de Korongo (cesta de mimbre para pescar)
  y su icono (16×16) en arte/interfaz/objetos.png (el 20.º)
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_casa_shamba import vetas, rect  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "pasarelas")
LUZ = (-0.6, -0.7, 0.5)
MADERA = ["#251812", "#3a261d", "#492e23", "#5b392b", "#6d4534", "#7f513d", "#905c45", "#a8735a"]
JUNCO = ["#3d3214", "#5c4a22", "#7a6431", "#958043", "#b09c5c", "#c9b77d", "#e2cea0"]
PIEDRA = ["#1f211c", "#2e302a", "#41443a", "#525649", "#666b5b", "#7a806d", "#8d9381", "#a0a596"]
GIZA = ["#2a0d3a", "#3a1650", "#6b2a8f", "#a855d6", "#d6a8f0"]
MUSGO = ["#1d2e18", "#2b4220", "#3f582f", "#526d38", "#6a8246"]
# la rana: piedra verdosa con musgo (que se distinga del suelo gris de las zonas de Giza)
RANA_P = ["#141c12", "#223020", "#34462c", "#4a5e3a", "#62784a", "#7e925c", "#9cac74", "#bcc896"]
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


def palafito():
    """La cabaña de Korongo: sobre cuatro pilotes que se meten en el agua, con plataforma de tablas, paredes de
    tablas verticales, un tejado de juncos a dos aguas (con el borde deshilachado), una ventanita con luz,
    una red de pesca colgada a secar, un farolillo y una escalerilla que baja al agua."""
    W, H = 64, 60
    lz = Lienzo(W, H, s=6, semilla=71)
    agua = 56
    # los pilotes y su reflejo en el agua
    for x in (12, 26, 40, 52):
        p = rect(lz, x - 1.6, 40, x + 1.6, agua + 1)
        lz.sombrear(p, MADERA[1:6], 1.6, LUZ, textura=vetas(lz, 0.5, 9, False, x), fuerza_tex=0.3)
        lz.pintar(rect(lz, x - 2.4, agua - 0.6, x + 2.4, agua + 1.4), "#9fd0d0", 0.7)          # ondita al pie
    # la plataforma de tablas
    plat = rect(lz, 6, 37, 58, 42)
    lz.sombrear(plat, MADERA[2:], 2, LUZ, textura=((lz.x % 4) < 0.7) * 1.0, fuerza_tex=-0.5)
    lz.pintar(rect(lz, 6, 41, 58, 42), MADERA[1], 0.9)
    # paredes de tablas verticales (en escorzo: frente y lado)
    frente = rect(lz, 12, 20, 46, 37.5)
    lz.sombrear(frente, MADERA[2:7], 6, LUZ, textura=vetas(lz, 0.45, 13, False, 72), fuerza_tex=0.4)
    lz.pintar(frente * ((lz.x % 4.5) < 0.6), MADERA[0], 0.8)
    lado = lz.poligono([(46, 20), (54, 16), (54, 34), (46, 37.5)])
    lz.sombrear(lado, MADERA[1:5], 3, LUZ, textura=vetas(lz, 0.45, 13, False, 73), fuerza_tex=0.4)
    # la puerta (oscura, con una cortina de cuentas) y la ventanita con luz
    puerta = rect(lz, 20, 25, 28, 37.5)
    lz.pintar(puerta, "#140e0a")
    for k in range(4):
        lz.pintar(lz.trazo([(21.5 + k * 2, 25.5), (21.5 + k * 2, 34)], 0.4), ["#4c8d8d", "#e6a852", "#de6771", "#c9b77d"][k], 0.8)
    ventana = rect(lz, 34, 25, 41, 30)
    lz.pintar(ventana, "#f9b947")
    lz.brillo(ventana, "#f9b947", 3, 0.5)
    lz.pintar(rect(lz, 37.2, 25, 37.8, 30) + rect(lz, 34, 27.2, 41, 27.8), MADERA[1])
    # el tejado de juncos a dos aguas, con el borde deshilachado
    hilos = np.sin(lz.x * 3.1 + lz.y * 0.9) * 0.5 + 0.5
    faldon = lz.poligono([(28, 5), (34, 2), (57, 18), (50, 22)])            # el faldón del lado (en sombra)
    lz.sombrear(faldon, JUNCO[:5], 4, LUZ, textura=hilos * 0.6 + vetas(lz, 0.3, 7, False, 75) * 0.4, fuerza_tex=0.5)
    tejado = lz.poligono([(5, 22.5), (28, 4.5), (51, 22.5)])                 # el hastial de delante
    lz.sombrear(tejado, JUNCO, 6, LUZ, textura=hilos * 0.6 + vetas(lz, 0.3, 7, False, 74) * 0.4, fuerza_tex=0.5)
    flecos = np.zeros((lz.H, lz.W))
    for k in range(26):
        x0 = 6 + k * 1.9
        y0 = 22 - abs(x0 - 28) * 0 if x0 < 28 else 22
        y0 = 22 - (28 - x0) * 0.77 if x0 < 28 else 5 + (x0 - 28) * 0.77
        flecos = np.maximum(flecos, lz.trazo([(x0, y0), (x0 + 0.4, y0 + 2.5 + (k % 3))], 0.5))
    lz.pintar(np.clip(flecos * (lz.y > 6), 0, 1), JUNCO[4], 0.9)
    lz.pintar(lz.trazo([(28, 5), (34, 3)], 1.2), JUNCO[1])
    # la red de pesca colgada en el lado (rombos) y unos peces secándose
    red = lz.poligono([(47, 21), (53, 18), (53, 31), (47, 34)])
    malla = ((np.abs((lz.x + lz.y) % 3) < 0.4) | (np.abs((lz.x - lz.y) % 3) < 0.4)) * red
    lz.pintar(malla, "#c9b77d", 0.85)
    for (x, y) in ((14, 18.5), (17, 19)):
        pez = lz.elipse(x, y + 3, 1.0, 2.2)
        lz.sombrear(pez, ["#346161", "#4c8d8d", "#9fd0d0"], 1, LUZ)
    lz.pintar(lz.trazo([(12, 18), (20, 18.5)], 0.4), "#c9b77d")
    # el farolillo en el poste de la esquina
    lz.pintar(lz.trazo([(8, 37), (8, 26)], 1.1), MADERA[3])
    farol = lz.elipse(8, 28, 1.8, 2.4)
    lz.pintar(farol, "#f9b947")
    lz.brillo(farol, "#fde27e", 3, 0.6)
    # la escalerilla que baja al agua
    for k in range(4):
        lz.pintar(lz.trazo([(31, 43 + k * 3.2), (37, 43 + k * 3.2)], 0.9), MADERA[4])
    lz.pintar(lz.trazo([(31, 42), (31, 56)], 0.8) + lz.trazo([(37, 42), (37, 56)], 0.8), MADERA[2])
    return lz.sprite(contorno=CONTORNO)


def rana(estado):
    """La RANA DE PIEDRA: una rana de roca gris con grietas por las que corre la luz violeta de Giza, ojos saltones
    y musgo en el lomo. 0 sentada · 1 agazapada (va a saltar) · 2 saltando (estirada) · 3 aterrizando (aplastada)
    · 4 atontada (ojos en espiral, panza arriba a medias) · 5 golpeada (se dibuja blanca en el juego, aquí igual que 4)."""
    W, H = 22, 20
    lz = Lienzo(W, H, s=8, semilla=81 + estado)
    suelo = 19
    alto = {0: 1.0, 1: 0.75, 2: 1.35, 3: 0.6, 4: 0.8, 5: 0.8}[estado]
    ancho = {0: 1.0, 1: 1.12, 2: 0.82, 3: 1.25, 4: 1.05, 5: 1.05}[estado]
    sube = 3.0 if estado == 2 else 0.0
    cy = suelo - 6 * alto - sube
    if estado != 2:
        lz.pintar(lz.desenfocar(lz.elipse(11, suelo, 8 * ancho, 1.6), 0.6), "#0e140c", 0.5)
    # patas traseras (dobladas a los lados; estiradas al saltar)
    if estado == 2:
        patas = lz.trazo([(7, cy + 4), (4, cy + 8), (3, cy + 11)], 2.2, 1.2) + lz.trazo([(15, cy + 4), (18, cy + 8), (19, cy + 11)], 2.2, 1.2)
    else:
        patas = lz.elipse(11 - 6.5 * ancho, suelo - 2.4, 3.2, 2.2) + lz.elipse(11 + 6.5 * ancho, suelo - 2.4, 3.2, 2.2)
    lz.sombrear(np.clip(patas, 0, 1), RANA_P[1:6], 1.4, LUZ)
    cuerpo = lz.elipse(11, cy, 7.5 * ancho, 6.2 * alto)
    lz.sombrear(cuerpo, RANA_P[1:], 4, LUZ, textura=lz.ruido(1.0, 3, semilla=82), fuerza_tex=0.35, recorte=("#d8e0b0", 0.35), recorte_dir=(-1, -0.5))
    panza = lz.elipse(11, cy + 3 * alto, 4.5 * ancho, 2.5 * alto) * cuerpo
    lz.pintar(panza, "#c9b07e", 0.85)
    # patas delanteras
    if estado != 2:
        for x in (11 - 3.2 * ancho, 11 + 3.2 * ancho):
            lz.sombrear(lz.elipse(x, suelo - 1.4, 1.5, 1.3), RANA_P[2:6], 1.0, LUZ)
    # grietas de Giza en el lomo
    for (pts, g) in (([(7, cy - 3), (9, cy - 1), (8, cy + 1)], 0.6), ([(14, cy - 4), (13, cy - 1), (15, cy + 1)], 0.5)):
        gr = lz.trazo(pts, g) * cuerpo
        lz.pintar(gr, GIZA[1])
        lz.pintar(lz.trazo(pts, g * 0.5) * cuerpo, GIZA[3])
        lz.brillo(gr, GIZA[3], 1.2, 0.8)
    # musgo en el lomo
    musgo = np.clip((lz.ruido(1.2, 2, semilla=83) - 0.6) * 5, 0, 1) * cuerpo * (lz.y < cy - 2 * alto)
    lz.pintar(musgo, MUSGO[3], 0.9)
    # ojos saltones (en espiral si está atontada)
    for x in (11 - 3.8 * ancho, 11 + 3.8 * ancho):
        ojo = lz.circulo(x, cy - 5.8 * alto, 2.7)
        lz.sombrear(ojo, RANA_P[3:], 1.2, LUZ)
        if estado in (4, 5):
            t = np.linspace(0, 3 * np.pi, 30)
            esp = lz.trazo([(x + np.cos(a) * a * 0.15, cy - 5.8 * alto + np.sin(a) * a * 0.15) for a in t], 0.4)
            lz.pintar(esp, GIZA[3])
        else:
            pupila = lz.elipse(x, cy - 5.6 * alto, 1.2, 1.7 if estado != 1 else 0.7)
            lz.pintar(pupila, "#140e18")
            lz.pintar(lz.elipse(x, cy - 5.6 * alto, 0.6, 1.0 if estado != 1 else 0.4), GIZA[3])
            lz.pintar(lz.circulo(x - 0.7, cy - 6.6 * alto, 0.45), "#fff8e8")
    # boca (ancha)
    lz.pintar(lz.trazo([(11 - 3.5 * ancho, cy - 1.6 * alto), (11, cy - 0.8 * alto), (11 + 3.5 * ancho, cy - 1.6 * alto)], 0.45) * cuerpo, "#1f211c", 0.9)
    return lz.sprite(contorno=CONTORNO)


NASA_COL = {"b": "3d3214", "m": "7a6431", "M": "b09c5c", "L": "e2cea0", "a": "346161", "A": "6db0b0"}
NASA_1 = [
    "............",
    "....bbbb....",
    "...bMLMLb...",
    "..bmMmMmMb..",
    "..bMmMmMmb..",
    ".bmMmMmMmMb.",
    ".bMmMmMmMmb.",
    ".bmMmMmMmMb.",
    "..bMmMmMmb..",
    "..bbmMmMbb..",
    "...aAaAa....",
    "............",
]
NASA_2 = [
    "............",
    "....bbbb....",
    "...bLMLMb...",
    "..bMmMmMmb..",
    "..bmMmMmMb..",
    ".bMmMmMmMmb.",
    ".bmMmMmMmMb.",
    ".bMmMmMmMmb.",
    "..bmMmMmMb..",
    "..bbMmMmbb..",
    "....aAaAa...",
    "............",
]
ICONO = [
    "................",
    "......bbbb......",
    ".....bMLMLb.....",
    "....bmMmMmMb....",
    "...bMmMmMmMmb...",
    "...bmMmMmMmMb...",
    "..bMmMmMmMmMmb..",
    "..bmMmMmMmMmMb..",
    "..bMmMmMmMmMmb..",
    "..bmMmMmMmMmMb..",
    "...bMmMmMmMmb...",
    "...bmMmMmMmMb...",
    "....bbmMmMbb....",
    ".....bbbbbb.....",
    "....aAaAaAa.....",
    "................",
]


def pixeles(filas, col):
    w, h = len(filas[0]), len(filas)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y, f in enumerate(filas):
        for x, ch in enumerate(f):
            if ch != ".":
                c = col[ch]
                img.putpixel((x, y), tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    return img


def main():
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(palafito(), "RGBA").save(os.path.join(SALIDA, "palafito.png"))
    tira([rana(k) for k in range(6)]).save(os.path.join(SALIDA, "rana.png"))
    hoja = Image.new("RGBA", (24, 12), (0, 0, 0, 0))
    hoja.alpha_composite(pixeles(NASA_1, NASA_COL), (0, 0))
    hoja.alpha_composite(pixeles(NASA_2, NASA_COL), (12, 0))
    hoja.save(os.path.join(RAIZ, "arte", "mundos", "raiz", "objetos", "nasa.png"))
    # el icono de la mochila: el 20.º de objetos.png (índice 19)
    ruta = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    n = max(20, viejos.width // 16)
    iconos = Image.new("RGBA", (16 * n, 16), (0, 0, 0, 0))
    iconos.alpha_composite(viejos.crop((0, 0, min(viejos.width, 16 * 19), 16)), (0, 0))
    if viejos.width > 16 * 20:
        iconos.alpha_composite(viejos.crop((16 * 20, 0, viejos.width, 16)), (16 * 20, 0))
    iconos.alpha_composite(pixeles(ICONO, NASA_COL), (16 * 19, 0))
    iconos.save(ruta)
    print("Objetos de Las Pasarelas en", SALIDA)


if __name__ == "__main__":
    main()
