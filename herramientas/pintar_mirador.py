"""EL MIRADOR DEL OCASO (el Valle del Ocaso), pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_mirador.py

Genera en arte/mundos/ocaso/mirador/:
  obelisco.png   20×60      un obelisco de arenisca con remate de bronce y las horas grabadas (su sombra larga la
                            dibuja el juego)
  reloj.png      3 × 44×38  un RELOJ DE SOL sobre su pedestal: la esfera de bronce, el gnomon y una gema que marca
                            dónde está el sol. 0 oeste · 1 sur · 2 este
  espejo.png     8 × 28×38  un ESPEJO DE BRONCE en su pie, que gira: 0 norte · 1 este · 2 sur · 3 oeste (apagado);
                            4-7 lo mismo, encendido (lleno de luz)
  farol.png      14×22      un FAROL DE LA HORA (se recoge): latón y cristal de ámbar con la llama quieta
  arco.png       2 × 64×68  EL ARCO DEL ATARDECER: dos columnas de arenisca y un sol tallado en la clave.
                            0 cerrado (un velo violeta de Giza) · 1 abierto (el atardecer se ve dentro)
  arco_kitovu.png 2 × 48×52 el mismo arco, más pequeño, en el sur del Kitovu (0 frío · 1 encendido)
  kivuli.png     5 × 34×26  KIVULI MENOR, el alacrán de sombra: 0-1 anda · 2 en penumbra (casi invisible)
                            · 3 deslumbrado (al sol: pálido, encogido) · 4 golpeado (blanco)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "ocaso", "mirador")
LUZ = (-0.6, -0.7, 0.55)
ARENISCA = ["#3a1820", "#6a3030", "#944a40", "#b86a50", "#d48c66", "#ecb084", "#f8d0a4"]
BRONCE = ["#2a160c", "#5a3418", "#8a5a26", "#b8843a", "#e0b05a", "#f8dc96"]
SOMBRA = ["#0a0612", "#160c24", "#24143a", "#341e50", "#4a2c6a", "#6a4490"]
AMBAR = ["#6a300c", "#b8601a", "#e8962a", "#fcc860", "#fff0b0"]
BLANCO = ["#8a8090", "#b8b0c0", "#dcd6e4", "#f4f0f8", "#ffffff"]


def obelisco():
    W, H = 20, 60
    lz = Lienzo(W, H, s=4, semilla=12010)
    cuerpo = lz.poligono([(4, 58), (16, 58), (14, 14), (10, 6), (6, 14)])
    lz.sombrear(cuerpo, ARENISCA[1:], 5.0, LUZ, textura=lz.ruido(1.5, 3, semilla=12011), fuerza_tex=0.3)
    lz.pintar(cuerpo * (lz.x > 10.5), ARENISCA[1], 0.35)                      # la cara en sombra
    for y in (22, 30, 38, 46):                                                # las horas grabadas
        lz.pintar(lz.trazo([(7.5, y), (12.5, y)], 0.45) * cuerpo, ARENISCA[0], 0.8)
        lz.pintar(lz.circulo(10, y - 3, 0.9) * cuerpo, AMBAR[2], 0.8)
    remate = lz.poligono([(6, 14), (14, 14), (10, 3)])
    lz.sombrear(remate, BRONCE[1:], 2.5, LUZ)
    lz.sumar_luz(lz.desenfocar(lz.circulo(10, 6, 1.5), 2), AMBAR[3], 0.7)
    base = lz.poligono([(2, 59.5), (18, 59.5), (17, 54), (3, 54)])
    lz.sombrear(base, ARENISCA[:6], 2.0, LUZ)
    return lz.sprite(contorno=0.4)


def reloj(f):
    W, H = 44, 38
    lz = Lienzo(W, H, s=4, semilla=12020 + f)
    cx, cy = 22, 16
    pie = lz.poligono([(14, 37), (30, 37), (27, 22), (17, 22)])
    lz.sombrear(pie, ARENISCA[1:], 4.0, LUZ, textura=lz.ruido(1.5, 3, semilla=12021), fuerza_tex=0.25)
    for y in (27, 32):
        lz.pintar(lz.trazo([(16, y), (28, y)], 0.4) * pie, ARENISCA[0], 0.6)
    esfera = lz.elipse(cx, cy, 19, 9)
    lz.sombrear(esfera, BRONCE[1:], 5.0, LUZ)
    lz.pintar(lz.elipse(cx, cy, 15.5, 7) * esfera, BRONCE[2], 0.5)
    for k in range(12):                                                       # las marcas de las horas
        a = k * np.pi / 6
        p0 = (cx + np.cos(a) * 13, cy + np.sin(a) * 6)
        p1 = (cx + np.cos(a) * 16.5, cy + np.sin(a) * 7.6)
        lz.pintar(lz.trazo([p0, p1], 0.4), BRONCE[0], 0.8)
    # el gnomon: una aleta de bronce que apunta hacia el lado contrario del sol
    gn = lz.poligono([(cx - 1, cy + 1), (cx + 1, cy + 1), (cx, cy - 11)])
    lz.sombrear(gn, BRONCE[2:], 1.5, LUZ)
    # la sombra del gnomon sobre la esfera (opuesta al sol) y la gema del sol en el borde
    sol = {0: (-1.0, 0.0), 1: (0.0, 1.0), 2: (1.0, 0.0)}[f]
    sombra = lz.trazo([(cx, cy), (cx - sol[0] * 14, cy - sol[1] * 6)], 1.1)
    lz.pintar(sombra * esfera, "#1a0c10", 0.6)
    gx, gy = cx + sol[0] * 17.5, cy + sol[1] * 8
    lz.sombrear(lz.circulo(gx, gy, 2.4), AMBAR, 1.4, LUZ)
    lz.sumar_luz(lz.desenfocar(lz.circulo(gx, gy, 2.4), 3), AMBAR[3], 0.9)
    return lz.sprite(contorno=0.4)


def espejo(f):
    W, H = 28, 38
    lz = Lienzo(W, H, s=4, semilla=12040 + f)
    cx, cy = 14, 14
    lado = f % 4
    lleno = f >= 4
    pie = lz.poligono([(10, 37), (18, 37), (16, 26), (12, 26)])
    lz.sombrear(pie, ARENISCA[1:], 3.0, LUZ)
    lz.pintar(lz.trazo([(14, 24), (14, 30)], 1.2), BRONCE[1])
    # el disco, girado: de frente (sur), de espaldas (norte, se ve el dorso) o de canto (este / oeste)
    ancho = {0: 10.0, 1: 4.5, 2: 10.0, 3: 4.5}[lado]
    dx = {0: 0, 1: 2.5, 2: 0, 3: -2.5}[lado]
    marco = lz.elipse(cx + dx, cy, ancho, 11)
    lz.sombrear(marco, BRONCE, 4.0, LUZ)
    if lado == 0:                                                             # de espaldas: el dorso labrado
        lz.pintar(lz.trazo([(cx - 5, cy), (cx + 5, cy)], 0.5) * marco, BRONCE[0], 0.7)
        lz.pintar(lz.trazo([(cx, cy - 6), (cx, cy + 6)], 0.5) * marco, BRONCE[0], 0.7)
    else:
        cara = lz.elipse(cx + dx * 1.2, cy, ancho - 2.2, 9)
        lz.pintar(cara, "#f8e4c0" if lleno else "#8a6a5a")
        lz.pintar(cara * (lz.y < cy - 2) * (lz.x < cx + dx), "#ffffff" if lleno else "#c8a890", 0.6)
        if lleno:
            lz.sumar_luz(lz.desenfocar(cara, 6), AMBAR[3], 1.0)
    return lz.sprite(contorno=0.4)


def farol():
    W, H = 14, 22
    lz = Lienzo(W, H, s=5, semilla=12060)
    asa = np.clip(lz.elipse(7, 3.5, 3, 2.6) - lz.elipse(7, 3.5, 1.8, 1.6), 0, 1)
    lz.sombrear(asa, BRONCE[1:], 1.0, LUZ)
    cuerpo = lz.poligono([(3, 6), (11, 6), (12, 17), (2, 17)])
    lz.sombrear(cuerpo, BRONCE, 3.0, LUZ)
    vidrio = lz.poligono([(4.5, 8), (9.5, 8), (10, 16), (4, 16)])
    lz.sombrear(vidrio, AMBAR, 3.0, LUZ)
    llama = lz.elipse(7, 12.5, 1.4, 2.4)
    lz.pintar(llama, AMBAR[4])
    lz.sumar_luz(lz.desenfocar(llama, 4), AMBAR[3], 1.0)
    lz.pintar(lz.trazo([(7, 8), (7, 16)], 0.4), BRONCE[1], 0.8)
    base = lz.poligono([(2, 17), (12, 17), (11, 21), (3, 21)])
    lz.sombrear(base, BRONCE[:5], 1.5, LUZ)
    return lz.sprite(contorno=0.4)


def arco(f, W=64, H=68):
    lz = Lienzo(W, H, s=4, semilla=12080 + f + W)
    k = W / 64.0
    hueco = np.clip(lz.poligono([(14 * k, H - 1), (50 * k, H - 1), (50 * k, 30 * k), (14 * k, 30 * k)]) + lz.elipse(32 * k, 30 * k, 18 * k, 16 * k) * (lz.y <= 30 * k), 0, 1)
    todo = np.clip(lz.poligono([(2 * k, H - 1), (62 * k, H - 1), (62 * k, 30 * k), (2 * k, 30 * k)]) + lz.elipse(32 * k, 30 * k, 30 * k, 28 * k) * (lz.y <= 30 * k), 0, 1)
    piedra = np.clip(todo - hueco, 0, 1)
    if f == 0:
        lz.pintar(hueco, "#120a1e")
        velo = hueco * (np.sin(lz.y * 0.5 + lz.ruido(4, 2, semilla=12081) * 6) * 0.5 + 0.5)
        lz.pintar(velo, SOMBRA[4], 0.55)
        lz.pintar(hueco * (np.abs(lz.ruido(3, 3, semilla=12082) - 0.5) < 0.04), "#b070e0", 0.7)
    else:
        lz.pintar(hueco, lz.gradiente(["#4a2256", "#9a4462", "#e8885a", "#fcc870"], eje="y", desde=14 * k, hasta=H))
        sol = lz.circulo(32 * k, H - 16 * k, 8 * k)
        lz.pintar(sol * hueco, "#fff4c8")
        lz.sumar_luz(lz.desenfocar(hueco, 6), AMBAR[3], 0.5)
    lz.sombrear(piedra, ARENISCA[1:], 6.0 * k, LUZ, textura=lz.ruido(1.6, 3, semilla=12083), fuerza_tex=0.3)
    for y in np.arange(30 * k, H, 9 * k):                                     # las hiladas de las columnas
        lz.pintar(lz.trazo([(2 * k, y), (14 * k, y)], 0.4) * piedra, ARENISCA[0], 0.6)
        lz.pintar(lz.trazo([(50 * k, y), (62 * k, y)], 0.4) * piedra, ARENISCA[0], 0.6)
    clave = lz.circulo(32 * k, 8 * k, 5 * k)                                  # el sol tallado en la clave
    lz.sombrear(clave, BRONCE[1:], 3.0 * k, LUZ)
    for r in range(8):
        a = r * np.pi / 4
        lz.pintar(lz.trazo([(32 * k + np.cos(a) * 5.5 * k, 8 * k + np.sin(a) * 5.5 * k),
                            (32 * k + np.cos(a) * 7.5 * k, 8 * k + np.sin(a) * 7.5 * k)], 0.6) * piedra, BRONCE[3], 0.9)
    if f == 1:
        lz.sumar_luz(lz.desenfocar(clave, 4), AMBAR[3], 0.8)
    return lz.sprite(contorno=0.4)


def kivuli(f):
    W, H = 34, 26
    lz = Lienzo(W, H, s=5, semilla=12100 + f)
    E = 1.3
    paso = (f % 2) * 1.0
    rampa = BLANCO if f == 4 else (["#5a5068", "#7a7090", "#a098b4", "#c8c0d8", "#e8e4f0"] if f == 3 else SOMBRA[1:])
    encoge = 0.85 if f == 3 else 1.0
    cx, cy = 17, 16
    cuerpo = lz.elipse(cx, cy, 6.5 * E * encoge, 4.2 * E * encoge)
    for lado in (-1, 1):                                                      # las patas...
        for k in range(3):
            y = cy - 1 + k * 2 * E
            dy = (paso if k % 2 == 0 else -paso) * lado * 0.8
            lz.pintar(lz.trazo([(cx + lado * 4 * E, y), (cx + lado * 9 * E, y + 2 + dy)], 0.7), rampa[0])
        pinza = lz.elipse(cx + lado * 9 * E, cy - 5 * E, 2.4 * E, 1.7 * E, 20 * lado)        # ...y las pinzas
        lz.sombrear(pinza, rampa, 1.2, LUZ)
        lz.pintar(lz.trazo([(cx + lado * 5 * E, cy - 2), (cx + lado * 8.5 * E, cy - 4.5 * E)], 0.8), rampa[1])
    lz.sombrear(cuerpo, rampa, 3.0, LUZ)
    cola = lz.curva((cx, cy + 4), (cx + 1, cy + 9), (cx + 7, cy + 5), (cx + 5, cy - 2 - paso))
    lz.pintar(lz.trazo(cola, 1.4, 0.8), rampa[2])
    lz.pintar(lz.circulo(cx + 5, cy - 2.5 - paso, 1.5), "#f0c0ff" if f != 3 else "#ffffff")
    ojo = "#ffd8ff" if f in (0, 1, 2) else ("#5a5068" if f == 3 else "#8a8090")
    for lado in (-1, 1):
        if f == 3:
            lz.pintar(lz.trazo([(cx + lado * 3 - 1, cy - 2.5), (cx + lado * 3 + 1, cy - 2.5)], 0.35), ojo)
        else:
            lz.pintar(lz.circulo(cx + lado * 3, cy - 2.5, 1.1), ojo)
    if f in (0, 1):
        lz.sumar_luz(lz.desenfocar(lz.circulo(cx, cy - 2, 2.6), 3), "#b070e0", 0.5)
    img = lz.sprite(contorno=0.4)
    if f == 2:
        img = img.copy()
        img[..., 3] = (img[..., 3] * 0.45).astype(img.dtype)                  # en penumbra: casi no se ve
    return img


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    Image.fromarray(obelisco(), "RGBA").save(os.path.join(SALIDA, "obelisco.png"))
    tira("reloj", reloj, 3)
    tira("espejo", espejo, 8)
    Image.fromarray(farol(), "RGBA").save(os.path.join(SALIDA, "farol.png"))
    tira("arco", arco, 2)
    tira("arco_kitovu", lambda f: arco(f, 48, 52), 2)
    tira("kivuli", kivuli, 5)
    print("Mirador pintado en", SALIDA)
