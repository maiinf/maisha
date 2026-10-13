"""LOS HECHICEROS DE GIZA: dos enemigos nuevos que no pelean cuerpo a cuerpo.

    python3 herramientas/pintar_hechiceros.py

  BUNDI, el búho-mago (24×30): un búho de piedra con manto de musgo violeta y un bastón de rama con una gema de Giza.
      0-1 quieto (respira, la gema late) · 2 conjura (bastón arriba, alas abiertas) · 3 lanza · 4 se desvanece (plumas)
      · 5 golpeado
  BUIBUI, la araña-bruja (30×28): una araña de piedra con chal de telaraña, ocho patas y un cesto-nido a la espalda
      del que salen los bichos. 0-1 quieta · 2 invoca (patas delanteras arriba, el nido brilla) · 3 golpeada
  MENDE, el bicho de óxido (12×10): el escarabajo que invoca la bruja. 0-1 corre · 2 golpeado
  ORBE (12×12): la bola de Giza que lanza el búho. 0-1 late
  RESCOLDO (22×28): lo que queda de un jefe en su arena: un anillo de piedras rotas con una llama violeta y dorada
      que flota encima. Si Maisha lo toca, revive el eco del jefe para pelear otra vez. 0-1 la llama baila
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ, rampa  # noqa: E402
from pintar_pasarelas import CONTORNO, GIZA  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "hechiceros")
LUZ = (-0.6, -0.7, 0.5)
PIEDRA = ["#1c1a20", "#2b2830", "#3c3843", "#4f4a57", "#645e6c", "#7b7483", "#958e9c", "#b1aab6"]
MUSGO_V = ["#1a0f24", "#2a1838", "#3d2350", "#53306a", "#6c4084", "#8a56a0", "#a874bc"]
RAMA = ["#1e140c", "#33231a", "#4a3424", "#634733", "#7d5c42"]
TELA = ["#3a3a48", "#6a6a7a", "#a0a0b0", "#d8d8e4"]
OXIDO = ["#2a1208", "#4a2010", "#6e3218", "#934a24", "#b8673a", "#d68a52"]


def _ojo(lz, x, y, r, mirada=(0, 0)):
    lz.pintar(lz.circulo(x, y, r + 0.5), "#120c18")
    lz.pintar(lz.circulo(x, y, r), GIZA[3])
    lz.brillo(lz.circulo(x, y, r * 0.8), GIZA[3], 1.2, 0.8)
    lz.pintar(lz.circulo(x + mirada[0] * 0.4, y + mirada[1] * 0.4, r * 0.45), "#1a0a22")
    lz.pintar(lz.circulo(x - r * 0.35, y - r * 0.4, r * 0.28), "#f4e8ff")


def bundi(f):
    W, H = 24, 30
    lz = Lienzo(W, H, s=8, semilla=701 + f)
    cx = 12
    respira = 0.4 if f == 1 else 0.0
    if f == 4:
        # se desvanece: la silueta se deshace en humo violeta y un remolino de plumas
        lz.pintar(lz.desenfocar(lz.elipse(cx, 17, 5.5, 9), 1.8), GIZA[1], 0.5)
        lz.brillo(lz.elipse(cx, 17, 3, 6), GIZA[3], 3, 0.5)
        for k in range(10):
            a = k * 0.63
            r = 4 + k * 0.55
            px, py = cx + np.cos(a) * r, 16 + np.sin(a) * r * 0.9
            lz.sombrear(lz.elipse(px, py, 1.8, 0.7, np.degrees(a) + 90), PIEDRA[3:] if k % 2 else MUSGO_V[3:], 1, LUZ)
        for lado in (-1, 1):
            _ojo(lz, cx + lado * 2.3, 8, 1.2)
        return lz.sprite(contorno=CONTORNO)
    # el bastón (detrás si está quieto, en alto si conjura)
    if f in (2, 3):
        b0, b1 = (cx + 7, 25), (cx + 9, 2 if f == 2 else 6)
    else:
        b0, b1 = (cx + 8, 28), (cx + 9, 7)
    lz.sombrear(lz.trazo([b0, b1], 0.9, 0.7), RAMA, 1, LUZ)
    lz.pintar(lz.trazo([b1, (b1[0] - 2, b1[1] - 2)], 0.4) + lz.trazo([b1, (b1[0] + 2, b1[1] - 1.5)], 0.4), RAMA[3])
    gema = lz.circulo(b1[0], b1[1] + 0.5, 1.6 if f != 2 else 2.2)
    lz.brillo(gema, GIZA[3], 3.5 if f == 2 else 2.0, 0.9 if f in (0, 2) else 0.6)
    lz.sombrear(gema, GIZA, 1, LUZ)
    # las alas: plegadas, o abiertas al conjurar
    for lado in (-1, 1):
        if f == 2:
            ala = lz.poligono([(cx + lado * 4, 12), (cx + lado * 11, 8), (cx + lado * 11.5, 15), (cx + lado * 9, 21), (cx + lado * 4, 20)])
        elif f == 3:
            ala = lz.poligono([(cx + lado * 4, 12), (cx + lado * 9, 13), (cx + lado * 10, 19), (cx + lado * 6, 23), (cx + lado * 4, 21)])
        else:
            ala = lz.poligono([(cx + lado * 3.5, 12), (cx + lado * 6.5, 14), (cx + lado * 6.5, 23), (cx + lado * 4, 25)])
        lz.sombrear(ala, PIEDRA[1:], 2, LUZ, textura=((lz.y + lz.x * 0.3 * lado) % 2.2 < 0.7) * 1.0, fuerza_tex=0.35)
    # el cuerpo: un huevo de piedra con plumas grabadas
    cuerpo = lz.elipse(cx, 18 - respira, 5.5, 7.5)
    lz.sombrear(cuerpo, PIEDRA, 3, LUZ, textura=lz.ruido(0.6, 2, semilla=702), fuerza_tex=0.3)
    for k in range(4):
        for j in range(3):
            x = cx - 2.5 + j * 2.5 + (k % 2) * 1.2
            y = 16 + k * 2.2
            lz.pintar(lz.trazo(lz.curva((x - 1, y), (x, y + 1), (x + 1, y), n=6), 0.3) * cuerpo, PIEDRA[2], 0.8)
    # el manto de musgo violeta sobre los hombros, que gotea
    manto = lz.poligono([(cx - 6.5, 11.5), (cx + 6.5, 11.5), (cx + 6, 16), (cx + 3, 15), (cx + 1, 18), (cx - 1.5, 15.5), (cx - 4, 17.5), (cx - 6, 15)])
    lz.sombrear(manto, MUSGO_V, 2, LUZ, textura=lz.ruido(0.4, 2, semilla=703), fuerza_tex=0.5)
    lz.brillo(lz.trazo([(cx + 1, 17), (cx + 1, 18.5)], 0.4), GIZA[3], 1, 0.6)
    # patas
    for lado in (-1, 1):
        lz.pintar(lz.trazo([(cx + lado * 2, 25), (cx + lado * 2.6, 27.2)], 0.6), "#3a2e1a")
        for d in (-1, 0, 1):
            lz.pintar(lz.trazo([(cx + lado * 2.6, 27.2), (cx + lado * 2.6 + d, 28)], 0.3), "#3a2e1a")
    # la cabeza: disco facial y orejas de pluma (cuernitos)
    hy = 8 - respira
    cabeza = lz.elipse(cx, hy, 5.5, 4.6)
    lz.sombrear(cabeza, PIEDRA, 2, LUZ, textura=lz.ruido(0.6, 1, semilla=704), fuerza_tex=0.3)
    for lado in (-1, 1):
        oreja = lz.poligono([(cx + lado * 2.5, hy - 3.5), (cx + lado * 5.5, hy - 7.5), (cx + lado * 5, hy - 2.5)])
        lz.sombrear(oreja, PIEDRA[2:], 1, LUZ)
        disco = lz.circulo(cx + lado * 2.3, hy + 0.3, 2.6)
        lz.sombrear(disco, PIEDRA[4:], 1, LUZ)
    lz.pintar(lz.trazo([(cx - 2, hy - 2.6), (cx, hy - 1.2), (cx + 2, hy - 2.6)], 0.5), PIEDRA[1])      # ceño
    for lado in (-1, 1):
        if f == 5:
            lz.pintar(lz.trazo([(cx + lado * 2.3 - 1, hy - 0.5), (cx + lado * 2.3 + 1, hy + 1)], 0.35), GIZA[3])
            lz.pintar(lz.trazo([(cx + lado * 2.3 - 1, hy + 1), (cx + lado * 2.3 + 1, hy - 0.5)], 0.35), GIZA[3])
        else:
            _ojo(lz, cx + lado * 2.3, hy + 0.3, 1.6)
    lz.pintar(lz.poligono([(cx - 0.8, hy + 1.6), (cx + 0.8, hy + 1.6), (cx, hy + 3.4)]), "#c89a3a")
    return lz.sprite(contorno=CONTORNO)


def buibui(f):
    W, H = 32, 28
    lz = Lienzo(W, H, s=8, semilla=721 + f)
    cx = 16
    sube = 0.5 if f == 1 else 0.0
    ay, cy = 10.5 - sube, 17.5           # el abdomen (detrás, arriba) y la cabeza (delante, abajo)
    # las ocho patas: salen de la cabeza, suben a la rodilla (alta) y bajan al suelo
    for lado in (-1, 1):
        for k in range(4):
            base = (cx + lado * 2.2, cy - 2.6 + k * 1.1)
            if f == 2 and k == 0:
                rod, pie = (cx + lado * 6, cy - 10), (cx + lado * 4.5, cy - 14)
            else:
                abre = [5.5, 8.5, 9.5, 7.5][k]
                alto = [-6, -6.8, -5.8, -4][k] - (0.7 if (f == 1 and k % 2) else 0)
                rod = (cx + lado * abre, cy + alto)
                pie = (cx + lado * (abre + [3.5, 5.5, 5.5, 4][k]), cy + [-3, 2.5, 5.5, 7][k])
            lz.sombrear(lz.trazo([base, rod], 1.9, 1.5), PIEDRA[2:], 1, LUZ)
            lz.sombrear(lz.trazo([rod, pie], 1.5, 0.6), PIEDRA[2:], 1, LUZ)
            lz.pintar(lz.circulo(rod[0], rod[1], 0.9), MUSGO_V[3])
            lz.pintar(lz.circulo(rod[0] - 0.3, rod[1] - 0.3, 0.4), MUSGO_V[5])
    # el abdomen, grande y redondo, con la marca de Giza y musgo violeta
    abd = lz.elipse(cx, ay, 6.8, 5.6)
    lz.sombrear(abd, PIEDRA, 3, LUZ, textura=lz.ruido(0.6, 2, semilla=722), fuerza_tex=0.3)
    musgo = abd * np.clip((lz.ruido(0.35, 2, semilla=723) - 0.62) * 4, 0, 1)
    lz.sombrear(musgo, MUSGO_V, 1, LUZ)
    # el cesto-nido atado encima del abdomen, con bichos asomando
    nido = lz.elipse(cx, ay - 3.2, 4.3, 3)
    lz.sombrear(nido, RAMA, 1.5, LUZ, textura=((lz.x * 0.9 + lz.y) % 1.5 < 0.55) * 1.0, fuerza_tex=0.5)
    for k in range(-3, 4):
        lz.pintar(lz.trazo([(cx + k * 1.1, ay - 5.8), (cx + k * 1.2 + 0.3, ay - 0.6)], 0.2) * nido, RAMA[0], 0.6)
    boca = lz.elipse(cx, ay - 5, 3, 1.1)
    lz.pintar(boca, "#120a0a")
    lz.brillo(boca, GIZA[3], 3.5 if f == 2 else 1.2, 1.0 if f == 2 else 0.5)
    for (bx, by) in ((cx - 1.4, ay - 5.4), (cx + 1.5, ay - 5.7)) if f != 3 else ():
        lz.sombrear(lz.elipse(bx, by, 0.9, 0.7), OXIDO[2:], 1, LUZ)
        lz.pintar(lz.circulo(bx, by - 0.3, 0.25), GIZA[3])
    lz.pintar(lz.trazo([(cx - 4.5, ay - 2), (cx - 6, ay + 2)], 0.35) + lz.trazo([(cx + 4.5, ay - 2), (cx + 6, ay + 2)], 0.35), "#a08a5a")
    marca = lz.poligono([(cx, ay + 0.8), (cx + 1.5, ay + 2.6), (cx, ay + 4.4), (cx - 1.5, ay + 2.6)])
    lz.pintar(marca, GIZA[3])
    lz.brillo(marca, GIZA[3], 1.5, 1.0 if f == 2 else 0.5)
    # la cabeza, delante, con el chal de telaraña por encima y los hilos colgando
    cab = lz.elipse(cx, cy, 4.2, 3.4)
    lz.sombrear(cab, PIEDRA, 2, LUZ)
    chal = lz.poligono([(cx - 5.5, cy + 0.5), (cx - 4.5, cy - 3.2), (cx, cy - 4.6), (cx + 4.5, cy - 3.2), (cx + 5.5, cy + 0.5),
                        (cx + 3.5, cy - 0.8), (cx, cy - 1.6), (cx - 3.5, cy - 0.8)])
    lz.sombrear(chal, TELA, 1.5, LUZ)
    for r in (1.6, 3.2):
        lz.pintar(np.clip(1 - np.abs(np.hypot(lz.x - cx, lz.y - (cy - 4.5)) - r) / 0.18, 0, 1) * chal, TELA[0], 0.6)
    for a in (-0.9, 0, 0.9):
        lz.pintar(lz.trazo([(cx, cy - 4.5), (cx + np.sin(a) * 5, cy - 4.5 + np.cos(a) * 4)], 0.15) * chal, TELA[0], 0.5)
    for (a, b) in (((cx - 5.5, cy + 0.5), (cx - 5.8, cy + 3.5)), ((cx + 5.5, cy + 0.5), (cx + 5.9, cy + 3))):
        lz.pintar(lz.trazo([a, b], 0.22), TELA[3], 0.8)
    # los ojos: dos grandes y cuatro pequeños, que brillan bajo el chal
    for (ox, oy, r) in ((cx - 1.5, cy + 0.3, 1.0), (cx + 1.5, cy + 0.3, 1.0), (cx - 3, cy - 0.3, 0.55), (cx + 3, cy - 0.3, 0.55),
                        (cx - 0.7, cy - 1.1, 0.45), (cx + 0.7, cy - 1.1, 0.45)):
        if f == 3:
            lz.pintar(lz.trazo([(ox - r, oy), (ox + r, oy)], 0.3), GIZA[3])
        else:
            lz.pintar(lz.circulo(ox, oy, r + 0.3), "#120c18")
            lz.pintar(lz.circulo(ox, oy, r), GIZA[3])
            lz.brillo(lz.circulo(ox, oy, r), GIZA[3], 0.9, 0.7)
            lz.pintar(lz.circulo(ox - r * 0.3, oy - r * 0.35, r * 0.3), "#f4e8ff")
    for lado in (-1, 1):                                                       # los colmillos
        lz.pintar(lz.trazo([(cx + lado * 0.9, cy + 2.2), (cx + lado * 0.5, cy + 4)], 0.5, 0.15), "#d8d0c0")
    return lz.sprite(contorno=CONTORNO)


def mende(f):
    W, H = 12, 10
    lz = Lienzo(W, H, s=8, semilla=741 + f)
    cx, cy = 6, 5
    for lado in (-1, 1):
        for k in range(3):
            d = (0.8 if (f == 1) == (k % 2 == 0) else -0.4)
            lz.pintar(lz.trazo([(cx + lado * 1.5, cy - 1 + k * 1.3), (cx + lado * 4.2, cy - 1.5 + k * 1.8 + d)], 0.35), OXIDO[0])
    caparazon = lz.elipse(cx, cy, 3, 2.6)
    lz.sombrear(caparazon, OXIDO, 1.5, LUZ, textura=lz.ruido(0.5, 2, semilla=742), fuerza_tex=0.35)
    lz.pintar(lz.trazo([(cx, cy - 2.4), (cx, cy + 2.4)], 0.25) * caparazon, OXIDO[0])
    lz.pintar(lz.elipse(cx, cy - 2.8, 1.6, 1), "#1e1012")
    for lado in (-1, 1):
        lz.pintar(lz.circulo(cx + lado * 0.8, cy - 3, 0.4), GIZA[3] if f != 2 else "#ffffff")
    return lz.sprite(contorno=CONTORNO)


def orbe(f):
    W, H = 12, 12
    lz = Lienzo(W, H, s=8, semilla=751 + f)
    r = 3.0 if f == 0 else 3.6
    lz.brillo(lz.circulo(6, 6, r), GIZA[3], 2.5, 0.9)
    lz.sombrear(lz.circulo(6, 6, r), GIZA, 1.5, LUZ)
    lz.pintar(lz.circulo(5, 5, 0.9), "#f4e8ff")
    return lz.sprite(contorno=0.0)


def rescoldo(f):
    W, H = 22, 28
    lz = Lienzo(W, H, s=8, semilla=761 + f)
    cx, cy = 11, 23
    # el anillo de piedras rotas, con brasas violetas entre ellas
    for k in range(7):
        a = k / 7 * 2 * np.pi + 0.3
        px, py = cx + np.cos(a) * 7.5, cy + np.sin(a) * 3
        piedra = lz.elipse(px, py, 2.2, 1.6, np.degrees(a))
        lz.sombrear(piedra, PIEDRA[1:], 1.2, LUZ, textura=lz.ruido(0.5, 1, semilla=762 + k), fuerza_tex=0.3)
    brasas = lz.elipse(cx, cy, 5.5, 2)
    lz.pintar(brasas, "#1a0c22")
    lz.brillo(brasas, GIZA[3], 2.5, 0.8)
    # la llama: violeta por fuera, dorada por dentro, que se mece
    m = 0.9 if f else -0.9
    llama = lz.poligono([(cx - 4, cy - 1), (cx - 3.5 + m * 0.3, cy - 8), (cx - 1 + m, cy - 14), (cx + m * 1.4, cy - 20),
                         (cx + 1.6 + m, cy - 13), (cx + 4, cy - 7), (cx + 4, cy - 1)])
    lz.brillo(llama, GIZA[3], 4, 0.7)
    lz.pintar(llama, rampa(["#3a1450", "#7a3aa8", "#b070e0"], np.clip(1 - (cy - lz.y) / 22, 0, 1)))
    dentro = lz.poligono([(cx - 2, cy - 1), (cx - 1 + m * 0.6, cy - 8), (cx + m * 0.8, cy - 12), (cx + 1.6, cy - 7), (cx + 2, cy - 1)])
    lz.pintar(dentro, rampa(["#f4b040", "#f9d77a", "#fff4c8"], np.clip(1 - (cy - lz.y) / 12, 0, 1)))
    lz.brillo(dentro, "#f9d77a", 2, 0.6)
    for (x, y) in ((cx - 5 + m, cy - 16), (cx + 4 - m, cy - 19)):                  # chispas
        lz.pintar(lz.circulo(x, y, 0.5), "#f9d77a")
    return lz.sprite(contorno=0.0)


def hoja(fotos):
    w, h = fotos[0].shape[1], fotos[0].shape[0]
    t = np.zeros((h, w * len(fotos), 4), np.uint8)
    for i, a in enumerate(fotos):
        t[:, i * w:(i + 1) * w] = a
    return t


def main():
    os.makedirs(SALIDA, exist_ok=True)
    for nombre, fn, n in (("bundi", bundi, 6), ("buibui", buibui, 4), ("mende", mende, 3), ("orbe", orbe, 2), ("rescoldo", rescoldo, 2)):
        Image.fromarray(hoja([fn(k) for k in range(n)]), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))
    print("hechiceros pintados en", SALIDA)


if __name__ == "__main__":
    main()
