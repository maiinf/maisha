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
    """La cabaña de Korongo, la garza pescadora (120×108, la base en el centro de abajo): sobre pilotes que se meten en
    el agua, con plataforma de tablas y barandilla; paredes de tablas verticales con una ventana encendida; tejado de
    juncos a dos aguas, con el borde deshilachado y un nido en la cumbrera; la red de pesca y dos nasas secándose;
    peces colgados ahumándose; una caña apoyada; un farolillo; y una escalerilla que baja al agua."""
    import pintar_aldea as pa
    W, H = 120, 100
    lz = pa._lienzo(W, H, 8, 21)
    suelo = 96
    cx = 58
    LUZ_ = (-0.6, -0.7, 0.5)
    AGUA = ["#1c3a3a", "#285050", "#346161", "#4c8d8d", "#6db0b0"]
    # el agua al pie (un charco que se funde con el suelo) y los reflejos
    agua = lz.elipse(cx, suelo - 2, 50, 7)
    lz.pintar(agua, pa.rampa(AGUA, np.clip(0.5 + (lz.ruido(1.2, 2, semilla=22) - 0.5), 0, 1)), 0.85)
    for k in range(6):
        lz.pintar(lz.trazo([(cx - 40 + k * 15, suelo - 3 + k % 2), (cx - 34 + k * 15, suelo - 3 + k % 2)], 0.4), "#c8f0f0", 0.6)
    # los pilotes
    for x in (cx - 30, cx - 10, cx + 10, cx + 30):
        lz.sombrear(pa.rect(lz, x - 2, 66, x + 2, suelo - 1), MADERA, 1.2, LUZ_, textura=pa.vetas(lz, 0.5, 9, False, semilla=x), fuerza_tex=0.4)
        lz.pintar(pa.rect(lz, x - 2.2, suelo - 6, x + 2.2, suelo - 1), MUSGO[2], 0.7)
    for (a, b) in (((cx - 30, 70), (cx - 10, 86)), ((cx + 10, 86), (cx + 30, 70))):
        lz.sombrear(lz.trazo([a, b], 1.0), MADERA[1:], 0.4, LUZ_)
    # la plataforma y la barandilla
    plat = pa.rect(lz, cx - 40, 64, cx + 40, 68)
    tab = (np.abs(np.sin((lz.x - cx) / 4 * np.pi)) < 0.1).astype(float)
    lz.sombrear(plat, MADERA, 1.5, LUZ_, textura=pa.vetas(lz, 0.5, 13) * (1 - tab * 0.6), fuerza_tex=0.4)
    for x in range(int(cx - 39), int(cx + 40), 6):
        if abs(x - cx - 30) > 4:
            lz.sombrear(lz.trazo([(x, 64), (x, 57)], 0.7), MADERA[2:], 0.3, LUZ_)
    lz.sombrear(lz.trazo([(cx - 40, 57), (cx + 26, 57)], 0.8), MADERA[2:], 0.4, LUZ_)
    # la cabaña: tablas verticales, ventana encendida y puerta
    pared = pa.rect(lz, cx - 26, 34, cx + 26, 64)
    tabv = (np.abs(np.sin((lz.x - cx) / 3.2 * np.pi)) < 0.1).astype(float)
    lz.sombrear(pared, MADERA, 5, LUZ_, textura=pa.vetas(lz, 0.5, 15, False, semilla=23) * (1 - tabv * 0.7), fuerza_tex=0.45)
    pa.ventana(lz, cx - 18, 42, cx - 6, 52, encendida=0.65, contras=False, semilla=24, luz=LUZ_)
    pu = pa.rect(lz, cx + 4, 44, cx + 16, 64)
    lz.sombrear(pu, ["#251812", "#3d2418", "#5a3826", "#7a4e35"], 2, LUZ_, textura=pa.vetas(lz, 0.5, 11, False), fuerza_tex=0.4)
    lz.pintar(lz.circulo(cx + 14, 55, 0.7), "#c89a44")
    # el tejado de juncos, con el borde deshilachado y un nido de garza arriba
    tej = lz.poligono([(cx - 34, 38), (cx, 12), (cx + 34, 38), (cx + 30, 40), (cx, 18), (cx - 30, 40)])
    tej = np.maximum(tej, lz.poligono([(cx - 34, 38), (cx, 12), (cx + 34, 38)]))
    pa.paja(lz, tej, semilla=25, capas=4.5, y0=12)
    lz.pintar(tej, "#4a6a3a", 0.18)
    pa.flecos(lz, cx - 34, cx + 34, 38.5, 3.0, semilla=26)
    nido = lz.elipse(cx, 12, 8, 3.4)
    lz.sombrear(nido, JUNCO[1:], 1.2, LUZ_, textura=pa.vetas(lz, 0.4, 7), fuerza_tex=0.6)
    for k in range(6):
        lz.pintar(lz.trazo([(cx - 8 + k * 3, 11), (cx - 9 + k * 3.4, 8)], 0.4), JUNCO[5])
    # la red de pesca colgada de la barandilla, y dos nasas
    red = pa.rect(lz, cx - 40, 57, cx - 28, 72)
    malla = ((np.abs(np.sin((lz.x + lz.y) * 1.6)) < 0.2) | (np.abs(np.sin((lz.x - lz.y) * 1.6)) < 0.2)).astype(float)
    lz.pintar(red * malla * np.clip(1 - np.abs(lz.x - (cx - 34)) / 8 + (lz.y - 57) / 30, 0, 1), "#c8b48a", 0.9)
    for (x, y) in ((cx + 34, 60), (cx - 22, 60)):
        nasa = lz.elipse(x, y, 3.6, 5)
        lz.sombrear(nasa, JUNCO, 1, LUZ_, textura=((lz.y % 1.6) < 0.5) * 1.0, fuerza_tex=0.5)
        lz.pintar(lz.circulo(x, y - 4, 1.2), "#2a1a12")
    # peces colgados ahumándose bajo el alero
    for x in (cx + 20, cx + 23, cx + 26):
        lz.pintar(lz.trazo([(x, 40), (x, 43)], 0.4), "#3a2a18")
        pez = lz.elipse(x, 46, 1.2, 3)
        lz.sombrear(pez, ["#3a4a5a", "#6a8aa0", "#a8c8d8", "#e0f0f8"], 0.5, LUZ_)
    # la caña de pescar y el farolillo
    lz.sombrear(lz.trazo([(cx + 36, 64), (cx + 52, 26)], 0.7, 0.4), MADERA[3:], 0.3, LUZ_)
    lz.pintar(lz.trazo(lz.curva((cx + 52, 26), (cx + 56, 50), (cx + 54, suelo - 4)), 0.35), "#e0e0d8", 0.9)
    lz.pintar(lz.trazo([(cx - 26, 36), (cx - 30, 36), (cx - 30, 41)], 0.5), "#2a1a12")
    far = pa.rect(lz, cx - 32, 41, cx - 28, 46)
    lz.pintar(far, pa.rampa(["#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - cx + 30, lz.y - 43.5) / 3, 0, 1)))
    lz.sumar_luz(lz.desenfocar(far, 4), "#ef8a26", 0.4)
    # la escalerilla que baja al agua
    for x in (cx + 28, cx + 33):
        lz.sombrear(lz.trazo([(x, 66), (x + 2, suelo - 2)], 0.8), MADERA[2:], 0.3, LUZ_)
    for k in range(5):
        y = 70 + k * 5
        lz.sombrear(lz.trazo([(cx + 28 + k * 0.4, y), (cx + 33 + k * 0.4, y)], 0.7), MADERA[2:], 0.3, LUZ_)
    # juncos en el agua
    for k in range(14):
        x = cx - 50 + k * 7.6 + (k % 3)
        if abs(x - cx) < 34:
            continue
        lz.sombrear(lz.trazo([(x, suelo), (x + (k % 2) * 2 - 1, suelo - 10 - k % 4 * 3)], 0.7, 0.3), JUNCO[1:], 0.3, LUZ_)
    return lz.sprite(contorno=0.4)


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
