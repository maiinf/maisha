"""EL OBSERVATORIO DE LA AURORA (Sigilia), pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_observatorio.py

Genera en arte/mundos/sigilia/observatorio/:
  bobina.png    2 × 24×40  UNA BOBINA ASTRAL: pie de piedra lila, un carrete de hilo de cobre muy prieto y, arriba,
                una bola de latón. 0 apagada · 1 encendida (el hilo al rojo blanco, la bola con halo)
  diapason.png  2 × 24×48  UN DIAPASÓN ASTRAL de la Gran Cúpula: una horquilla alta de cobre sobre un pie de piedra
                con un aro grabado. 0 apagado · 1 cargado (los dos brazos vibran y brillan)
  saa.png       5 × 28×36  SAA, EL AUTÓMATA DE RELOJERÍA: barrigudo, de latón, con un ojo de lente azul, un mazo
                por brazo, patitas cortas y la llave de cuerda en la espalda. 0 y 1 anda · 2 mazazo (el mazo en
                alto) · 3 sobrecargado (el ojo en blanco, la tapa abierta, muelles fuera) · 4 golpeado (blanco)
  kengele.png   5 × 96×96  KENGELE, LA GRAN CAMPANA MUDA (jefe): campana colosal de bronce con constelaciones
                grabadas, un yugo de madera con herrajes y el badajo de tinta helada; dos ojos en la sombra de la
                boca. 0 y 1 flota (en el 1 parpadea) · 2 enfadada (los ojos encendidos, el badajo fuera) ·
                3 ATURDIDA (tumbada de lado, el badajo resquebrajado, ojos en espiral) · 4 aturdida y golpeada
  cupula_nyota.png  112×112  LA CÚPULA DE NYOTA: una torre redonda de sillares lila con la cúpula de cobre verdoso
                partida por la rendija, el telescopio de latón asomando, puerta de madera con farol y nieve encima
  telescopio.png    32×48    un telescopio de latón en su trípode, mirando arriba a la izquierda
  campanas.png      48×48    un bastidor de madera con tres campanas de bronce (la Galería de las Campanas)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "sigilia", "observatorio")
LUZ = (-0.6, -0.7, 0.5)
PIEDRA = ["#1c1830", "#2e2a4a", "#454068", "#605a88", "#8882ac", "#b4aed0"]
COBRE = ["#2a1208", "#5a2a12", "#8e4a20", "#c07a3a", "#e8ac62", "#ffe0a0"]
LATON = ["#2e2008", "#5c4416", "#94702a", "#c89a3e", "#f0d27a", "#fff4c4"]
BRONCE = ["#1e1408", "#3e2c12", "#6a4c1e", "#96702e", "#c49a48", "#eccc7c"]
VERDIN = ["#0e2a26", "#1c4a40", "#2e6e5c", "#4a9478", "#7abc9c", "#b4e0c4"]
MADERA = ["#1a100c", "#32201a", "#523426", "#724a34", "#946648"]
TINTA = ["#05030a", "#0e0818", "#1c1030", "#2e1c4a", "#4a3070", "#7a5aa8"]
HIELO = ["#3c6d93", "#7fb6d8", "#bfe3f3", "#eefaff"]
NIEVE = ["#9890ba", "#c8c2de", "#eeeaf8", "#ffffff"]


def _pie(lz, cx, base, ancho, alto):
    """Un pie de piedra: zócalo ancho y un tambor encima."""
    zoc = lz.poligono([(cx - ancho, base), (cx + ancho, base), (cx + ancho - 1, base - alto * 0.45), (cx - ancho + 1, base - alto * 0.45)])
    lz.sombrear(zoc, PIEDRA, 2.0, LUZ)
    tam = lz.poligono([(cx - ancho + 2.5, base - alto * 0.4), (cx + ancho - 2.5, base - alto * 0.4), (cx + ancho - 3, base - alto), (cx - ancho + 3, base - alto)])
    lz.sombrear(tam, PIEDRA[1:], 2.0, LUZ)
    lz.pintar(lz.trazo([(cx - ancho + 1, base - alto * 0.45), (cx + ancho - 1, base - alto * 0.45)], 0.35), PIEDRA[5], 0.7)
    return np.clip(zoc + tam, 0, 1)


def bobina(f):
    W, H = 24, 40
    lz = Lienzo(W, H, s=6, semilla=9600 + f)
    cx = 12
    _pie(lz, cx, 39, 8, 9)
    # el carrete: dos platos de latón y, entre ellos, el hilo de cobre vuelta a vuelta
    hilo = lz.poligono([(cx - 5.2, 29), (cx + 5.2, 29), (cx + 5.2, 13), (cx - 5.2, 13)])
    vueltas = ((lz.y % 2.0) < 0.9) * 1.0
    lz.sombrear(hilo, COBRE if f == 0 else COBRE[2:] + ["#ffffff"], 5.0, LUZ, textura=vueltas, fuerza_tex=-0.5)
    for y in (30, 12):
        plato = lz.elipse(cx, y, 7.2, 1.8)
        lz.sombrear(plato, LATON, 1.2, LUZ)
    # el mástil y la bola de arriba
    lz.sombrear(lz.poligono([(cx - 1, 11), (cx + 1, 11), (cx + 1, 6), (cx - 1, 6)]), LATON, 0.8, LUZ)
    bola = lz.circulo(cx, 4.5, 3.4)
    lz.sombrear(bola, LATON if f == 0 else LATON[2:] + ["#ffffff"], 2.2, LUZ)
    lz.pintar(lz.circulo(cx - 1.2, 3.3, 0.8), "#ffffff", 0.9)
    if f == 1:
        lz.pintar(hilo * (((lz.y + 1) % 4.0) < 0.9), "#fff6c8", 0.7)
        lz.sumar_luz(lz.desenfocar(bola, 1.6), "#bfe8ff", 0.9)
        lz.sumar_luz(lz.desenfocar(hilo, 1.2), "#ffd880", 0.45)
    return lz.sprite(contorno=0.5)


def diapason(f):
    W, H = 24, 48
    lz = Lienzo(W, H, s=6, semilla=9620 + f)
    cx = 12
    _pie(lz, cx, 47, 8, 8)
    aro = lz.elipse(cx, 39.5, 5.5, 1.3)
    lz.sombrear(aro, LATON, 1.0, LUZ)
    # el mango y la horquilla: dos brazos altos que se abren apenas (cargado: vibran, se ven dobles)
    mango = lz.poligono([(cx - 1.3, 39), (cx + 1.3, 39), (cx + 1.3, 30), (cx - 1.3, 30)])
    lz.sombrear(mango, COBRE, 1.0, LUZ)
    nudo = lz.circulo(cx, 30, 2.4)
    lz.sombrear(nudo, LATON, 1.6, LUZ)
    brazos = np.zeros_like(nudo)
    for lado in (-1, 1):
        b = lz.trazo([(cx + lado * 1.5, 30), (cx + lado * 4.6, 26), (cx + lado * 4.6, 4)], 2.3, 2.0)
        brazos = np.clip(brazos + b, 0, 1)
    lz.sombrear(brazos, COBRE if f == 0 else COBRE[2:] + ["#ffffff"], 1.3, LUZ)
    lz.pintar(lz.trazo([(cx - 5.2, 25), (cx - 5.2, 6)], 0.35) * brazos, COBRE[5], 0.8)
    if f == 1:
        for lado in (-1, 1):
            eco = lz.trazo([(cx + lado * 6.6, 24), (cx + lado * 6.8, 5)], 0.6, 0.4)
            lz.pintar(eco, "#fff0b0", 0.75)
        lz.sumar_luz(lz.desenfocar(brazos, 1.5), "#bfe8ff", 0.8)
        for y in (8, 15, 22):                                  # las ondas del zumbido, entre los brazos
            lz.pintar(lz.trazo([(cx - 2.6, y), (cx, y - 1.2), (cx + 2.6, y)], 0.4), "#ffffff", 0.85)
    return lz.sprite(contorno=0.5)


def saa(f):
    W, H = 28, 36
    lz = Lienzo(W, H, s=6, semilla=9640 + f)
    cx, base = 14, 35
    paso = {0: 1.0, 1: -1.0}.get(f, 0.0)
    # la llave de cuerda, detrás (asoma por arriba a la derecha): vástago y mariposa
    lz.sombrear(lz.trazo([(cx + 3, 14), (cx + 7.5, 7)], 1.3, 1.1), LATON, 0.8, LUZ)
    gira = {0: 0.0, 1: 1.2, 2: 0.6, 3: 0.3, 4: 0.3}[f]
    for a in (gira, gira + np.pi):
        ala = lz.elipse(cx + 8 + np.cos(a) * 2.6, 5.5 + np.sin(a) * 1.2, 2.8, 2.0, a)
        lz.sombrear(ala, LATON, 1.2, LUZ)
        lz.pintar(lz.circulo(cx + 8 + np.cos(a) * 2.6, 5.5 + np.sin(a) * 1.2, 0.8), LATON[0])
    # las patitas (andan: una delante y otra detrás) y los pies de plomo
    for lado in (-1, 1):
        px = cx + lado * 4.2
        sube = paso * lado * 1.2
        lz.sombrear(lz.trazo([(px, 27), (px, 32 - max(sube, 0))], 2.0), BRONCE, 1.0, LUZ)
        pie = lz.elipse(px + lado * 0.6, 33.2 - max(sube, 0), 3.0, 1.7)
        lz.sombrear(pie, BRONCE[:5], 1.2, LUZ)
    # la barriga: un tonel de latón con dos flejes y remaches
    cuerpo = lz.elipse(cx, 20, 9.6, 9.0)
    lz.sombrear(cuerpo, LATON, 5.5, LUZ)
    for y in (16.0, 24.0):
        fleje = lz.elipse(cx, y + 2.5, 9.6, 3.6) * (1 - lz.elipse(cx, y + 1.6, 9.6, 3.6)) * cuerpo
        lz.pintar(fleje, BRONCE[1], 0.75)
    for x in (cx - 7, cx - 3.5, cx + 3.5, cx + 7):
        lz.pintar(lz.circulo(x, 26.6 - abs(x - cx) * 0.16, 0.6) * cuerpo, LATON[5])
    # la esfera de reloj en la barriga (su «corazón»): con una sola aguja
    esfera = lz.circulo(cx - 0.5, 23.2, 3.4)
    lz.pintar(esfera, "#f4ecd0")
    lz.pintar(esfera * (1 - lz.circulo(cx - 0.5, 23.2, 2.7)), LATON[1])
    lz.pintar(lz.trazo([(cx - 0.5, 23.2), (cx + (1.6 if f != 3 else -1.6), 21.6 if f != 3 else 24.8)], 0.35), "#1a100c")
    # el ojo: una lente azul en su visera (sobrecargado: en blanco, con una espiral)
    visera = lz.elipse(cx - 1, 14.0, 6.0, 4.2)
    lz.sombrear(visera, BRONCE[1:], 2.2, LUZ)
    ojo = lz.circulo(cx - 1.5, 14.2, 3.0)
    if f == 3:
        lz.pintar(ojo, "#fff6c8")
        lz.pintar(lz.trazo([(cx - 1.5, 14.2), (cx - 0.3, 13.6), (cx - 1.0, 12.6), (cx - 2.8, 13.2), (cx - 3.0, 15.2), (cx - 1.2, 16.0)], 0.35), "#7a4a10")
    else:
        lz.sombrear(ojo, ["#0a1a30", "#184a78", "#3a8ac8", "#8ad0f8", "#ffffff"] if f != 2 else ["#3a0a08", "#8a2010", "#e05a20", "#ffb050", "#ffffff"], 2.0, LUZ)
        lz.pintar(lz.circulo(cx - 1.2, 14.4, 1.0), "#05030a")
        lz.pintar(lz.circulo(cx - 2.4, 13.2, 0.6), "#ffffff")
    # los brazos: el de la izquierda con el MAZO (en alto al dar el mazazo); el otro, una pinza corta
    if f == 2:
        brazo = [(cx - 8, 17), (cx - 11, 10), (cx - 9, 4)]
        mazo_c = (cx - 8.5, 3.0)
    else:
        brazo = [(cx - 8, 18), (cx - 11.5, 22 + paso * 0.6), (cx - 11.5, 27 + paso * 0.6)]
        mazo_c = (cx - 11.5, 29.0 + paso * 0.6)
    lz.sombrear(lz.trazo(brazo, 1.8, 1.5), BRONCE, 1.0, LUZ)
    mazo = lz.elipse(mazo_c[0], mazo_c[1], 3.4, 2.6)
    lz.sombrear(mazo, PIEDRA[:5], 1.6, LUZ)
    lz.pintar(lz.trazo([(mazo_c[0] - 3, mazo_c[1]), (mazo_c[0] + 3, mazo_c[1])], 0.35) * mazo, LATON[4], 0.8)
    lz.sombrear(lz.trazo([(cx + 8, 18), (cx + 11, 21 - paso * 0.6), (cx + 11, 24 - paso * 0.6)], 1.7, 1.3), BRONCE, 1.0, LUZ)
    lz.pintar(lz.trazo([(cx + 10, 24.5 - paso * 0.6), (cx + 9.4, 26.5 - paso * 0.6)], 0.5), LATON[4])
    lz.pintar(lz.trazo([(cx + 12, 24.5 - paso * 0.6), (cx + 12.6, 26.5 - paso * 0.6)], 0.5), LATON[4])
    # la chimenea-silbato de la coronilla
    lz.sombrear(lz.poligono([(cx - 3.5, 10.5), (cx - 1, 10.5), (cx - 1.2, 7.5), (cx - 3.3, 7.5)]), BRONCE[1:], 0.8, LUZ)
    if f == 3:
        # sobrecargado: la tapa de la barriga abierta y dos muelles fuera
        for (x0, y0, dx) in ((cx + 5, 18, 1), (cx - 6, 25, -1)):
            pts = [(x0 + dx * k * 1.1, y0 - k * 1.3 + (1.3 if k % 2 else -1.3)) for k in range(6)]
            lz.pintar(lz.trazo(pts, 0.5), LATON[5])
        lz.pintar(lz.trazo([(cx - 3.3, 7), (cx - 4.5, 4), (cx - 2.5, 2)], 0.6, 0.3), "#d8d4e8", 0.8)      # humo del silbato
    forma = lz.alfa > 0.5
    if f == 4:
        lz.pintar(forma * 1.0, "#ffffff", 0.82)
    return lz.sprite(contorno=0.5)


def _constelaciones(lz, cuerpo, cx, cy, semilla):
    """Las constelaciones grabadas en el bronce: estrellitas claras unidas por líneas finas."""
    rng = np.random.default_rng(semilla)
    for _ in range(5):
        x, y = cx + rng.uniform(-20, 20), cy + rng.uniform(-14, 18)
        pts = [(x, y)]
        for _k in range(3):
            pts.append((pts[-1][0] + rng.uniform(-8, 8), pts[-1][1] + rng.uniform(-6, 6)))
        lz.pintar(lz.trazo(pts, 0.3) * cuerpo, BRONCE[5], 0.5)
        for (px, py) in pts:
            lz.pintar(lz.circulo(px, py, 0.8) * cuerpo, "#fff4c4", 0.9)


def _ojo_k(lz, x, y, f, espiral=False):
    if espiral:
        lz.pintar(lz.circulo(x, y, 3.2), "#d8c8ff")
        lz.pintar(lz.trazo([(x, y), (x + 1.3, y - 0.6), (x + 0.6, y - 2.0), (x - 1.6, y - 1.4), (x - 2.0, y + 1.0), (x + 0.4, y + 2.2)], 0.4), "#2e1c4a")
        return
    if f == 1:
        lz.pintar(lz.elipse(x, y, 3.4, 0.7), "#b8a0f0")          # parpadea
        return
    col = "#ffffff" if f != 2 else "#fff0a0"
    lz.pintar(lz.elipse(x, y, 3.4, 2.6 if f != 2 else 3.2), col)
    lz.pintar(lz.circulo(x + 0.3, y + 0.2, 1.4), "#12061c")
    lz.sumar_luz(lz.desenfocar(lz.circulo(x, y, 3.4), 1.6), "#b8a0ff" if f != 2 else "#ffb040", 0.8)
    if f == 2:
        lz.pintar(lz.trazo([(x - 4, y - 3.6), (x + 3.4, y - 2.0 if x < 48 else y - 5.2)], 0.6), "#05030a")      # el ceño


def kengele(f):
    W, H = 96, 96
    lz = Lienzo(W, H, s=4, semilla=9700 + f)
    if f in (3, 4):
        # ATURDIDA: tumbada de lado (la boca a la izquierda), el yugo a la derecha, el badajo roto en el suelo
        cuerpo = lz.poligono([(22, 52), (30, 44), (60, 50), (76, 56), (80, 66), (76, 76), (60, 82), (30, 90), (22, 82)])
        lz.sombrear(cuerpo, BRONCE, 12, LUZ)
        _constelaciones(lz, cuerpo, 52, 66, 9731)
        for x in (36, 44):                                                             # los dos cordones del labio
            lz.pintar(lz.trazo([(x, 45 + (x - 30) * 0.2), (x, 89 - (x - 30) * 0.27)], 0.6) * cuerpo, BRONCE[1], 0.7)
        boca = lz.elipse(24, 67, 6.5, 16.5)
        lz.pintar(boca, TINTA[0])
        lz.pintar(boca * (1 - lz.elipse(25.5, 67, 5.8, 15.2)), BRONCE[4])
        _ojo_k(lz, 24, 60, f, espiral=True)
        _ojo_k(lz, 25, 73, f, espiral=True)
        yugo = lz.poligono([(78, 52), (86, 50), (88, 82), (80, 80)])
        lz.sombrear(yugo, MADERA, 2.5, LUZ, textura=((lz.y % 3) < 0.6) * 1.0, fuerza_tex=-0.25)
        for y in (56, 76):
            lz.sombrear(lz.poligono([(77, y - 2), (89, y - 2.5), (89, y + 1.5), (77, y + 2)]), LATON, 0.8, LUZ)
        # el badajo de tinta helada, fuera y resquebrajado, con su charquito
        lz.pintar(lz.elipse(12, 90, 11, 3.2), TINTA[2], 0.9)
        bad = lz.trazo([(21, 78), (13, 84), (8, 86)], 2.2, 3.6)
        lz.sombrear(bad, TINTA[1:], 2.0, LUZ)
        lz.pintar(bad * (lz.ruido(1.2, 2, semilla=9733) > 0.55), HIELO[1], 0.7)
        lz.pintar(lz.trazo([(10, 83), (8, 86), (10, 89)], 0.35), HIELO[3])
        for (x, y) in ((5, 80), (16, 91), (3, 88)):
            lz.pintar(lz.poligono([(x, y), (x + 2.2, y + 0.8), (x + 0.6, y + 2.4)]), HIELO[2])
        if f == 4:
            lz.pintar((lz.alfa > 0.5) * 1.0, "#ffffff", 0.8)
        return lz.sprite(contorno=0.5)
    cx = 48
    # el yugo: un madero grueso con herrajes de latón y dos argollas (de donde colgaba)
    yugo = lz.poligono([(cx - 20, 6), (cx + 20, 6), (cx + 22, 16), (cx - 22, 16)])
    lz.sombrear(yugo, MADERA, 3.0, LUZ, textura=((lz.x % 3) < 0.6) * 1.0, fuerza_tex=-0.25)
    for x in (cx - 15, cx + 15):
        lz.sombrear(lz.poligono([(x - 2.5, 5), (x + 2.5, 5), (x + 2.5, 17), (x - 2.5, 17)]), LATON, 0.9, LUZ)
        arg = lz.circulo(x, 3.5, 3.2) * (1 - lz.circulo(x, 3.5, 1.7))
        lz.sombrear(arg, LATON, 0.8, LUZ)
    # la corona (asas) y el hombro
    for x in (cx - 6, cx, cx + 6):
        asa = lz.elipse(x, 17.5, 3.0, 4.0) * (1 - lz.elipse(x, 18, 1.4, 2.2))
        lz.sombrear(asa, BRONCE, 1.0, LUZ)
    # la campana: hombro redondo, cintura y el labio que se abre
    cuerpo = lz.poligono([(cx - 13, 22), (cx + 13, 22), (cx + 18, 30), (cx + 21, 52), (cx + 27, 70), (cx + 34, 80), (cx - 34, 80), (cx - 27, 70), (cx - 21, 52), (cx - 18, 30)])
    cuerpo = np.clip(cuerpo + lz.elipse(cx, 26, 16, 7), 0, 1)
    lz.sombrear(cuerpo, BRONCE, 16, LUZ, rebote=("#5a3a8a", 0.35))
    for y in (33, 36, 68, 72):                                                         # los cordones
        lz.pintar(lz.trazo([(cx - 40, y), (cx + 40, y)], 0.6) * cuerpo, BRONCE[1], 0.7)
        lz.pintar(lz.trazo([(cx - 40, y + 0.9), (cx + 40, y + 0.9)], 0.3) * cuerpo, BRONCE[5], 0.5)
    _constelaciones(lz, cuerpo, cx, 50, 9730)
    lz.pintar(lz.trazo([(cx - 14, 27), (cx - 18, 42), (cx - 22, 60)], 1.4, 0.6) * cuerpo, BRONCE[5], 0.55)      # el brillo del costado
    # verdín en el labio y un poco de nieve en el hombro
    lz.pintar(cuerpo * (lz.y > 73) * (lz.ruido(2.2, 2, semilla=9734) > 0.5), VERDIN[3], 0.6)
    lz.pintar(lz.elipse(cx - 3, 22.5, 11, 2.4) * (lz.ruido(1.5, 2, semilla=9735) > 0.35), NIEVE[2], 0.9)
    # la boca: el borde y la sombra de dentro, con los dos ojos mirando
    labio = lz.elipse(cx, 80, 34, 7)
    lz.sombrear(labio, BRONCE[1:], 3, LUZ)
    dentro = lz.elipse(cx, 80.5, 30, 5.2)
    lz.pintar(dentro, TINTA[0])
    # la cara: dos ojos en una franja de sombra (como una visera), a media campana
    franja = lz.elipse(cx, 50, 15, 6.5) * cuerpo
    lz.pintar(franja, TINTA[0], 0.92)
    lz.pintar(franja * (1 - lz.elipse(cx, 50, 14, 5.6)), BRONCE[1])
    _ojo_k(lz, cx - 6.5, 50, f)
    _ojo_k(lz, cx + 6.5, 50, f)
    # el badajo de tinta helada: asoma por abajo (enfadada: más fuera, con carámbanos)
    baja = 8 if f == 2 else 4
    bad = lz.trazo([(cx, 78), (cx, 82 + baja)], 3.0, 5.0)
    bola = lz.circulo(cx, 84 + baja, 5.6)
    badajo = np.clip(bad + bola, 0, 1)
    lz.sombrear(badajo, TINTA[1:], 3.0, LUZ)
    lz.pintar(badajo * (lz.ruido(1.3, 2, semilla=9736) > 0.52), HIELO[1], 0.7)
    lz.pintar(lz.circulo(cx - 1.8, 82.5 + baja, 1.1), HIELO[3])
    if f == 2:
        for x in (cx - 3.5, cx + 2.5):
            lz.pintar(lz.trazo([(x, 88 + baja), (x - 0.3, 92 + baja * 0.4)], 0.9, 0.1), HIELO[2])
    return lz.sprite(contorno=0.5)


def cupula_nyota():
    W, H = 112, 112
    lz = Lienzo(W, H, s=4, semilla=9800)
    cx = 54
    # la torre: un tambor de sillares lila (más ancho abajo), con zócalo
    torre = lz.poligono([(cx - 36, 108), (cx + 36, 108), (cx + 33, 58), (cx - 33, 58)])
    hil = np.floor(lz.y / 7)
    sillar = (((lz.y % 7) < 0.9) | (((lz.x + (hil % 2) * 8) % 16) < 0.9)) * 1.0
    lz.sombrear(torre, PIEDRA, 26, LUZ, textura=sillar, fuerza_tex=-0.5)
    zoc = lz.poligono([(cx - 38, 110), (cx + 38, 110), (cx + 37, 102), (cx - 37, 102)])
    lz.sombrear(zoc, PIEDRA[:5], 4, LUZ, textura=(((lz.x % 12) < 0.9)) * 1.0, fuerza_tex=-0.4)
    # la cornisa de cobre donde apoya la cúpula
    corn = lz.poligono([(cx - 37, 60), (cx + 37, 60), (cx + 35, 54), (cx - 35, 54)])
    lz.sombrear(corn, COBRE, 2.5, LUZ)
    for x in range(cx - 33, cx + 35, 6):
        lz.pintar(lz.circulo(x, 57, 0.8), COBRE[5])
    # la cúpula: cobre con verdín, en gajos, partida por la rendija del telescopio
    cup = lz.elipse(cx, 55, 35, 40) * (lz.y < 55)
    gajo = (np.abs(np.sin((lz.x - cx) / (36.0 - (55 - lz.y) * 0.45).clip(4, 40) * 3.6)) < 0.08) * 1.0
    lz.sombrear(cup, VERDIN, 22, LUZ, textura=gajo, fuerza_tex=-0.45)
    lz.pintar(cup * (lz.ruido(7, 3, semilla=9801) > 0.62) * (lz.y > 34), COBRE[3], 0.4)              # donde el verdín no ha llegado
    lz.pintar(cup * gajo, VERDIN[0], 0.55)
    rend = lz.poligono([(cx + 6, 55), (cx + 16, 55), (cx + 9, 17), (cx + 3, 17)]) * cup
    lz.pintar(rend, "#07050f")
    lz.pintar(np.clip(rend - lz.poligono([(cx + 7.2, 55), (cx + 16, 55), (cx + 9, 17), (cx + 4.2, 17)]), 0, 1), COBRE[4])
    # el telescopio, asomando por la rendija hacia arriba a la derecha
    tubo = lz.trazo([(cx + 9, 40), (cx + 30, 12)], 7.5, 6.0, puntas=False)
    lz.sombrear(tubo, LATON, 3.2, LUZ)
    for t in (0.25, 0.6, 0.92):
        x, y = cx + 9 + 21 * t, 40 - 28 * t
        anillo = lz.trazo([(x - 3.4, y - 2.6), (x + 3.4, y + 2.6)], 1.3, puntas=False)
        lz.sombrear(anillo, COBRE[1:], 0.9, LUZ)
    lente = lz.elipse(cx + 30.5, 11.5, 2.2, 3.6, -0.93)
    lz.pintar(lente, "#8ad0f8")
    lz.pintar(lz.circulo(cx + 29.8, 10.4, 0.9), "#ffffff")
    # el remate: una veleta con estrella
    lz.sombrear(lz.trazo([(cx - 4, 16), (cx - 4, 6)], 1.0), LATON, 0.6, LUZ)
    est = lz.poligono([(cx - 4, 1), (cx - 2.6, 4.4), (cx + 0.5, 5), (cx - 2.6, 5.8), (cx - 4, 9), (cx - 5.4, 5.8), (cx - 8.5, 5), (cx - 5.4, 4.4)])
    lz.sombrear(est, LATON[2:], 1.0, LUZ)
    # nieve sobre la cúpula y en la cornisa
    nieve = cup * (lz.y < 21 + 3 * np.sin(lz.x * 0.5) + (np.abs(lz.x - cx) * 0.16)) * (1 - rend)
    lz.pintar(nieve, NIEVE[2], 0.95)
    lz.pintar(nieve * (lz.ruido(2, 2, semilla=9804) > 0.62), NIEVE[0], 0.5)
    lz.pintar(lz.trazo([(cx - 35, 53.5), (cx + 2, 53.5)], 1.3) * (lz.ruido(2, 2, semilla=9805) > 0.4), NIEVE[2], 0.9)
    # la puerta: arco de madera con herrajes, escalón, y su farol encendido
    arco = np.clip(lz.poligono([(cx - 8, 108), (cx + 8, 108), (cx + 8, 86), (cx - 8, 86)]) + lz.circulo(cx, 86, 8), 0, 1)
    lz.pintar(np.clip(lz.poligono([(cx - 10.5, 108), (cx + 10.5, 108), (cx + 10.5, 86), (cx - 10.5, 86)]) + lz.circulo(cx, 86, 10.5), 0, 1), PIEDRA[5])
    lz.sombrear(arco, MADERA, 5, LUZ, textura=((lz.x % 4) < 0.7) * 1.0, fuerza_tex=-0.35)
    for y in (90, 101):
        lz.sombrear(lz.poligono([(cx - 8, y - 1), (cx + 8, y - 1), (cx + 8, y + 1), (cx - 8, y + 1)]) * arco, LATON, 0.6, LUZ)
    lz.pintar(lz.circulo(cx + 5, 97, 1.1), LATON[5])
    esc = lz.poligono([(cx - 13, 111), (cx + 13, 111), (cx + 12, 107.5), (cx - 12, 107.5)])
    lz.sombrear(esc, PIEDRA[2:], 1.5, LUZ)
    far = lz.poligono([(cx + 14, 84), (cx + 19, 84), (cx + 19.6, 91), (cx + 13.4, 91)])
    lz.pintar(far, "#ffd880")
    lz.pintar(lz.poligono([(cx + 13, 84), (cx + 20, 84), (cx + 16.5, 80.5)]), COBRE[2])
    lz.pintar(lz.trazo([(cx + 13.4, 91.4), (cx + 19.6, 91.4)], 0.5), COBRE[1])
    lz.sumar_luz(lz.desenfocar(far, 4.5), "#ffb860", 0.7)
    # dos ventanas redondas con luz dentro y una placa con una estrella sobre la puerta
    for x in (cx - 22, cx + 24):
        marco = lz.circulo(x, 78, 5.6)
        lz.sombrear(marco, COBRE, 1.5, LUZ)
        cris = lz.circulo(x, 78, 4.0)
        lz.pintar(cris, "#ffcf7a")
        lz.pintar(lz.trazo([(x - 4, 78), (x + 4, 78)], 0.45), COBRE[1])
        lz.pintar(lz.trazo([(x, 74), (x, 82)], 0.45), COBRE[1])
        lz.sumar_luz(lz.desenfocar(cris, 3.5), "#ffb860", 0.55)
    placa = lz.elipse(cx, 70.5, 5, 3.6)
    lz.sombrear(placa, LATON, 1.5, LUZ)
    lz.pintar(lz.poligono([(cx, 68), (cx + 0.9, 70), (cx + 3, 70.5), (cx + 0.9, 71), (cx, 73), (cx - 0.9, 71), (cx - 3, 70.5), (cx - 0.9, 70)]), "#fff4c4")
    return lz.sprite(contorno=0.5)


def telescopio():
    W, H = 32, 48
    lz = Lienzo(W, H, s=6, semilla=9820)
    cx = 16
    for (x, giro) in ((cx - 9, 0), (cx + 9, 0), (cx + 1, 1)):                           # el trípode
        pata = lz.trazo([(cx, 26), (x, 46 - giro * 2)], 1.5, 1.1)
        lz.sombrear(pata, MADERA[1:], 0.8, LUZ)
        lz.pintar(lz.circulo(x, 46 - giro * 2, 1.2), LATON[2])
    lz.sombrear(lz.circulo(cx, 25.5, 3.0), LATON, 1.8, LUZ)                              # la rótula
    tubo = lz.trazo([(cx + 8, 32), (cx - 9, 9)], 6.0, 8.0, puntas=False)
    lz.sombrear(tubo, LATON, 3.0, LUZ)
    for t in (0.18, 0.55, 0.9):
        x, y = cx + 8 - 17 * t, 32 - 23 * t
        g = 3.2 + t * 1.2
        lz.sombrear(lz.trazo([(x - g * 0.8, y + g * 0.6), (x + g * 0.8, y - g * 0.6)], 1.3, puntas=False), COBRE[1:], 0.8, LUZ)
    lente = lz.elipse(cx - 9.6, 8.2, 3.2, 4.4, 0.93)
    lz.pintar(lente, "#3a8ac8")
    lz.pintar(lz.elipse(cx - 10.2, 7.4, 1.6, 2.4, 0.93), "#8ad0f8")
    lz.pintar(lz.circulo(cx - 10.8, 6.4, 0.7), "#ffffff")
    lz.sombrear(lz.trazo([(cx + 8, 32), (cx + 11, 36)], 2.6, 1.8), COBRE, 1.0, LUZ)        # el ocular
    lz.sombrear(lz.trazo([(cx - 2, 15), (cx - 5, 12)], 1.6, 1.4), COBRE[1:], 0.7, LUZ)     # el buscador, encima
    return lz.sprite(contorno=0.5)


def campanas():
    W, H = 48, 48
    lz = Lienzo(W, H, s=6, semilla=9840)
    for x in (5, 43):                                                                   # los dos postes
        poste = lz.poligono([(x - 2, 47), (x + 2, 47), (x + 1.6, 8), (x - 1.6, 8)])
        lz.sombrear(poste, MADERA, 1.6, LUZ, textura=((lz.y % 4) < 0.7) * 1.0, fuerza_tex=-0.3)
        lz.sombrear(lz.elipse(x, 46.5, 4, 1.6), PIEDRA[1:], 1.0, LUZ)
    viga = lz.poligono([(2, 6), (46, 6), (46, 11), (2, 11)])
    lz.sombrear(viga, MADERA[1:], 2.0, LUZ, textura=((lz.x % 5) < 0.7) * 1.0, fuerza_tex=-0.3)
    lz.pintar(lz.trazo([(2, 5.4), (46, 5.4)], 0.9) * (lz.ruido(1.5, 2, semilla=9841) > 0.35), NIEVE[2], 0.95)
    for (x, r, cuelga) in ((13.5, 5.2, 13), (24, 6.6, 15), (34.5, 4.6, 12)):
        lz.pintar(lz.trazo([(x, 11), (x, cuelga)], 0.5), LATON[1])
        c = lz.poligono([(x - r * 0.45, cuelga), (x + r * 0.45, cuelga), (x + r * 0.75, cuelga + r * 1.3), (x + r, cuelga + r * 2.0), (x - r, cuelga + r * 2.0), (x - r * 0.75, cuelga + r * 1.3)])
        c = np.clip(c + lz.elipse(x, cuelga + 1, r * 0.55, 1.6), 0, 1)
        lz.sombrear(c, BRONCE, r * 0.8, LUZ)
        lz.pintar(lz.trazo([(x - r, cuelga + r * 1.55), (x + r, cuelga + r * 1.55)], 0.35) * c, BRONCE[1], 0.8)
        lz.pintar(lz.elipse(x, cuelga + r * 2.0, r * 0.85, 1.0), TINTA[0])
        lz.pintar(lz.circulo(x, cuelga + r * 2.0 + 1.4, 1.2), TINTA[3])                  # el badajo, de tinta helada
        lz.pintar(lz.circulo(x - 0.4, cuelga + r * 2.0 + 1.0, 0.45), HIELO[2])
    return lz.sprite(contorno=0.5)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    tira("bobina", bobina, 2)
    tira("diapason", diapason, 2)
    tira("saa", saa, 5)
    tira("kengele", kengele, 5)
    for nombre, fn in (("cupula_nyota", cupula_nyota), ("telescopio", telescopio), ("campanas", campanas)):
        Image.fromarray(fn(), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))
    print("Observatorio pintado en", SALIDA)
