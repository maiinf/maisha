"""
KITOVU Y LA GRANJA DE MZEE SHAMBA dibujados píxel a píxel (paleta oficial de Raíz).

Uso:  python3 herramientas/dibujar_kitovu.py
Genera en arte/mundos/kitovu/:
  (la casa del castor, su molino, su interior y el cetro de la pared los pinta pintar_casa_shamba.py)
  zanahoria.png            2 fotogramas: plantada, arrancada (el hoyo)
  cerca.png                2 fotogramas: rota, arreglada (32x16)
  tronco.png               2 fotogramas: con tablas, sin tablas
  espantapajaros.png       para probar el golpe del cetro
  arbol_seco.png           árbol muerto, gris
  portal.png               el Arco de Raíz: 2 fotogramas (dormido, abierto)
  crater.png               el hoyo donde cae Maisha
  cetro_pared.png          el cetro de la familia, colgado en la pared de la casa
  interior_casa_shamba.png la casa por dentro (320x208, como las demás casas)
  pez.png                  sombra de pez para el minijuego de pesca
Y en arte/interfaz/:
  objetos.png              iconos de la mochila (16x16 cada uno): zanahoria, pez, tablas, mapa, cetro,
                           seta luminosa, mineral, madera
  mapa_mundo.png           el mapa del mundo, roto: le falta el trozo de Sigilia
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont
from dibujar_aldea import Lienzo, c, tira, habitacion, _fondo_negro, RAIZ, PAL, MAT

MAT.update({
    "paja": ["Flor ambar 1", "Flor ambar 2", "Flor ambar 3", "Flor ambar 4"],
    "naranja": ["Follaje rojizo 1", "Follaje rojizo 2", "Follaje rojizo 3", "Follaje rojizo 4"],
    "gris": ["Piedra 1", "Piedra 2", "Piedra 3", "Piedra 4"],
    "giza": ["Giza 1", "Giza 2", "Giza 3", "Giza 4"],
    "papel": ["Pergamino 1", "Pergamino 2", "Pergamino 3", "Extremos 2"],
})


CASA_W, CASA_H = 184, 140
CASA_BASE = (100, 138)       # dónde está la base de la puerta dentro del dibujo


def casa_granja():
    """La gran casa de Mzee Shamba: troncos sobre un zócalo de piedra, tejado de paja a capas
    con buhardilla, chimenea, porche con mazorcas colgadas, jardineras, molino de agua y aperos."""
    W, H = CASA_W, CASA_H
    l = Lienzo(W, H)
    azar = random.Random(14)
    x0, x1 = 30, 170              # paredes
    suelo = 132                   # donde acaba el zócalo
    # --- el molino de agua va aparte (molino.png), para que gire
    # agua que cae de la canaleta
    l.rect(4, 82, 34, 84, "corteza", 2)
    for y in range(85, 136):
        for x in (6, 7, 8):
            if (y + x) % 5 != 0:
                l.px(x, y, "agua", 3 if x == 7 else 2)
    # --- zócalo de piedra
    for y in range(116, suelo + 1):
        fila = (y - 116) // 5
        for x in range(x0 - 4, x1 + 5):
            junta = (y - 116) % 5 == 4 or (x + fila * 5) % 11 == 0
            l.px(x, y, "gris", 1 if junta else (3 if (x // 11 + fila) % 3 == 0 else 2))
    # --- paredes de troncos, con las puntas redondas en las esquinas
    for y in range(70, 116):
        tronco = (y - 70) // 6
        for x in range(x0, x1 + 1):
            borde = (y - 70) % 6 in (0, 5)
            tono = 1 if borde else (3 if (y - 70) % 6 == 1 else 2)
            if (x + tronco * 13) % 29 == 0 and not borde:
                tono = 1
            l.px(x, y, "corteza", tono)
    for y in range(70, 116, 6):
        for (cx_, lado) in ((x0 - 2, -1), (x1 + 2, 1)):
            l.ovalo(cx_, y + 3, 3.2, 3.2, "cobre", plano=3)
            l.ovalo(cx_, y + 3, 1.8, 1.8, "cobre", plano=2)
            l.px(cx_, y + 3, "cobre", 1)
    # --- tejado de paja a capas, con buhardilla
    cumbre, alero = 10, 74
    for y in range(cumbre, alero + 1):
        t = (y - cumbre) / (alero - cumbre)
        medio = 10 + 80 * t
        for x in range(int(100 - medio), int(100 + medio) + 1):
            capa = (y - cumbre) // 6
            borde_capa = (y - cumbre) % 6 == 5
            ola = math.sin((x + capa * 7) * 0.7) > 0.6
            u = (x - (100 - medio)) / (2 * medio)
            tono = 3 if u < 0.22 else (2 if u < 0.62 else 1)
            if borde_capa or (ola and (y - cumbre) % 6 == 4):
                tono = max(0, tono - 1) if tono > 1 else 0
            if (x * 7 + y * 3) % 17 == 0 and tono > 0:
                tono -= 1                                          # pajas sueltas
            l.px(x, y, "paja", tono)
    for x in range(12, 189):
        if x % 2 == 0 and l.get(x, alero):
            l.px(x, alero + 1, "paja", 1)                      # flecos del alero
    l.rect(88, cumbre - 2, 112, cumbre, "paja", 1)               # caballete
    l.rect(90, cumbre - 3, 110, cumbre - 3, "paja", 2)
    # buhardilla con ventana redonda encendida
    bx = 100
    l.rect(bx - 11, 44, bx + 11, 60, "corteza", 2)              # pared de la buhardilla
    for y in range(44, 61, 4):
        l.rect(bx - 11, y, bx + 11, y, "corteza", 1)
    for y in range(26, 47):                                      # su tejadillo a dos aguas
        t = (y - 26) / 20
        medio = 3 + 13 * t
        for x in range(int(bx - medio), int(bx + medio) + 1):
            borde = abs(x - bx) > medio - 2
            l.px(x, y, "paja", 0 if borde else (3 if x < bx - 2 else (2 if x < bx + 4 else 1)))
    for x in range(bx - 11, bx + 12):
        l.px(x, 61, "paja", 0)                                   # sombra bajo la buhardilla
    l.ovalo(bx, 51, 6, 6, "corteza", plano=1)
    l.ovalo(bx, 51, 4.6, 4.6, "ambar", plano=2)
    l.ovalo(bx - 1, 50, 2.6, 2.6, "luz", plano=2)
    l.rect(bx - 4, 51, bx + 4, 51, "corteza", 1)
    l.rect(bx, 47, bx, 55, "corteza", 1)
    # --- chimenea de piedra a la derecha, por encima del tejado
    for y in range(0, 52):
        fila = y // 4
        for x in range(140, 152):
            junta = y % 4 == 3 or (x + fila * 3) % 6 == 0
            l.px(x, y, "gris", 1 if junta else (3 if x < 143 else 2))
    l.rect(138, 0, 153, 2, "gris", 3)
    # --- ventanas con contraventanas y jardineras
    for vx in (44, 136):
        l.rect(vx - 1, 80, vx + 17, 98, "corteza", 1)
        l.rect(vx, 81, vx + 16, 97, "ambar", 2)
        l.rect(vx + 1, 89, vx + 15, 97, "luz", 1)
        l.rect(vx + 8, 81, vx + 8, 97, "corteza", 1)
        l.rect(vx, 89, vx + 16, 89, "corteza", 1)
        for lado in (vx - 7, vx + 18):                           # contraventanas
            l.rect(lado, 80, lado + 5, 98, "hoja", 2)
            l.rect(lado, 80, lado + 5, 80, "hoja", 3)
            for y in range(83, 98, 4):
                l.rect(lado + 1, y, lado + 4, y, "hoja", 1)
        l.rect(vx - 3, 99, vx + 19, 104, "cobre", 2)             # jardinera
        l.rect(vx - 3, 99, vx + 19, 99, "cobre", 3)
        for k in range(6):
            fx = vx - 1 + k * 4
            l.px(fx, 97, "hoja", 3); l.px(fx + 1, 98, "hoja", 2)
            l.px(fx, 96, ["seta", "ambar", "papel"][k % 3], 3)
    # --- porche: tejadillo de tablillas sobre dos postes, y la tarima
    l.rect(64, 82, 136, 90, "cobre", 2)
    for x in range(64, 137, 4):
        l.rect(x, 82, x, 90, "cobre", 1)
    l.rect(62, 90, 138, 91, "cobre", 1)
    l.rect(64, 82, 136, 82, "cobre", 3)
    for px_ in (68, 130):
        l.rect(px_, 91, px_ + 3, 128, "corteza", 3)
        l.rect(px_ + 3, 91, px_ + 3, 128, "corteza", 1)
    l.rect(60, 126, 140, 131, "cobre", 3)                       # tarima
    for x in range(60, 141, 6):
        l.rect(x, 126, x, 131, "cobre", 1)
    # mazorcas y ajos colgados del porche
    for (hx, mat) in [(76, "paja"), (80, "paja"), (120, "papel"), (124, "papel"), (84, "paja")]:
        l.linea(hx, 91, hx, 95, "corteza", 1)
        l.ovalo(hx, 99, 1.6, 3.4, mat, plano=3 if mat == "papel" else 2)
    # --- la puerta, en arco, con ventanita redonda y emblema de dientes de castor encima
    for y in range(94, 126):
        for x in range(90, 111):
            dx = (x + 0.5 - 100) / 10.5
            dy = (y - 104) / 10.5
            if y >= 104 or dx * dx + dy * dy <= 1:
                borde = abs(dx) > 0.86 or (y < 104 and dx * dx + dy * dy > 0.75)
                l.px(x, y, "corteza", 1 if borde else (2 if (x - 90) % 5 == 0 else 3))
    l.ovalo(100, 104, 3, 3, "ambar", plano=2)
    l.px(99, 103, "luz", 3)
    l.px(106, 114, "ambar", 3)
    l.rect(96, 88, 104, 92, "cobre", 3)                         # placa sobre la puerta
    l.rect(98, 89, 99, 91, "papel", 3); l.rect(101, 89, 102, 91, "papel", 3)   # dos dientes
    # escalones
    l.rect(88, 132, 112, 134, "gris", 3)
    l.rect(86, 135, 114, 137, "gris", 2)
    # farolillo junto a la puerta
    l.rect(114, 96, 117, 97, "oscuro", 3)
    l.rect(113, 98, 118, 104, "ambar", 2)
    l.rect(114, 99, 117, 102, "luz", 3)
    # --- aperos y cosas del huerto delante: barril, cajas, saco, rastrillo
    l.ovalo(150, 128, 6, 7, "corteza")
    l.rect(144, 124, 156, 124, "gris", 2); l.rect(144, 131, 156, 131, "gris", 2)
    l.rect(158, 122, 172, 134, "cobre", 2); l.rect(158, 122, 172, 123, "cobre", 3)
    l.linea(158, 128, 172, 128, "cobre", 1); l.linea(165, 122, 165, 134, "cobre", 1)
    for (zx, zy) in [(160, 120), (164, 119), (168, 121)]:
        l.ovalo(zx, zy, 1.6, 2.2, "naranja", plano=3)            # zanahorias en la caja
        l.px(zx, zy - 3, "brote", 2)
    l.ovalo(40, 128, 6, 6, "papel")                             # saco de grano
    l.rect(37, 122, 43, 123, "corteza", 1)
    l.linea(54, 136, 60, 104, "corteza", 3)                     # rastrillo
    l.rect(57, 102, 64, 103, "gris", 3)
    for x in range(57, 65, 2):
        l.px(x, 104, "gris", 2)
    l.sin_contorno = {"luz", "ambar", "agua"}
    return l.imagen()


def zanahoria(arrancada):
    l = Lienzo(12, 12)
    # tierra removida
    l.ovalo(6, 10, 5, 2, "tierra", plano=1)
    if arrancada:
        l.ovalo(6, 10, 2.5, 1.2, "oscuro", plano=0)
        return l.imagen()
    l.ovalo(6, 9, 1.8, 1.4, "naranja", plano=3)              # la parte de arriba asoma
    for (x, y, t) in [(4, 4, 3), (5, 5, 2), (6, 3, 3), (6, 6, 2), (7, 4, 3), (8, 5, 2), (5, 3, 2), (7, 2, 3)]:
        l.px(x, y, "brote", t)
    l.linea(6, 7, 6, 4, "brote", 1)
    return l.imagen()


def cerca(arreglada):
    l = Lienzo(32, 16)
    for x in (2, 15, 28):
        l.rect(x, 2, x + 1, 15, "corteza", 3 if x == 2 else 2)
    if arreglada:
        for y in (5, 10):
            l.rect(0, y, 31, y + 1, "corteza", 2)
            l.rect(0, y, 31, y, "corteza", 3)
    else:
        l.rect(0, 5, 14, 6, "corteza", 2); l.rect(0, 5, 14, 5, "corteza", 3)
        l.linea(17, 13, 30, 9, "corteza", 1, grosor=2)       # tabla caída
        l.rect(0, 10, 6, 11, "corteza", 2)
        l.linea(18, 15, 26, 14, "corteza", 2)
    return l.imagen()


def tronco(con_tablas):
    l = Lienzo(36, 18)
    l.ovalo(16, 12, 15, 5, "corteza")
    l.ovalo(30, 12, 3, 5, "cobre", plano=3)                 # corte del tronco, con anillos
    l.ovalo(30, 12, 1.6, 2.8, "cobre", plano=2)
    l.px(30, 12, "cobre", 1)
    for x in range(4, 28, 5):
        l.px(x, 10, "corteza", 1); l.px(x + 1, 11, "corteza", 1)
    for (x, y) in [(8, 7), (9, 7), (16, 7), (20, 8)]:
        l.px(x, y, "musgo", 3)
    if con_tablas:
        for k in range(3):
            x0 = 3 + k * 4
            l.rect(x0, 2 + k, x0 + 2, 14, "cobre", 3 if k % 2 == 0 else 2)
            l.rect(x0, 2 + k, x0 + 2, 2 + k, "cobre", 3)
    return l.imagen()


def espantapajaros():
    l = Lienzo(18, 32)
    l.rect(8, 10, 9, 31, "corteza", 2)                       # palo
    l.rect(1, 13, 16, 14, "corteza", 2)                      # brazos
    l.rect(4, 12, 13, 22, "seta", 2)                         # camisa remendada
    l.rect(4, 12, 13, 12, "seta", 3)
    l.rect(7, 16, 9, 18, "papel", 2)                         # remiendo
    for (x, y) in [(1, 15), (0, 16), (16, 15), (17, 16), (6, 23), (11, 23)]:
        l.px(x, y, "paja", 3)                                # paja que asoma
    l.ovalo(8.5, 7, 4, 4, "papel")                           # cabeza de saco
    l.px(7, 6, "oscuro", 0); l.px(10, 6, "oscuro", 0)
    l.rect(7, 9, 10, 9, "oscuro", 2)
    l.rect(3, 2, 14, 3, "paja", 2); l.rect(5, 0, 12, 2, "paja", 3)   # sombrero
    return l.imagen()


def arbol_seco():
    l = Lienzo(28, 40)
    azar = random.Random(5)
    for y in range(18, 40):
        ancho = 2 + (y - 18) // 8
        for x in range(14 - ancho, 14 + ancho):
            l.px(x, y, "gris", 3 if x < 14 else 2)
    ramas = [(14, 20, 4, 6), (14, 22, 23, 9), (13, 26, 3, 15), (15, 18, 18, 2), (14, 19, 9, 1), (18, 12, 24, 6), (8, 10, 2, 4)]
    for (x0, y0, x1, y1) in ramas:
        l.linea(x0, y0, x1, y1, "gris", 2, grosor=2 if y0 > 15 else 1)
    l.rect(10, 38, 18, 39, "gris", 1)
    return l.imagen()


def portal(abierto):
    """El Arco de Raíz: dos raíces gigantes que se trenzan. Abierto, dentro hay un remolino verde."""
    W, H = 72, 88
    l = Lienzo(W, H)
    cx, base = 36, 86
    # interior del arco
    for y in range(14, base):
        for x in range(10, 63):
            dx = (x + 0.5 - cx) / 24
            dy = (y - 40) / 26
            if (y >= 40 and abs(dx) <= 1) or dx * dx + dy * dy <= 1:
                if abierto:
                    r = math.hypot(dx, (y - 52) / 34)
                    ang = math.atan2(y - 52, x - cx)
                    remolino = math.sin(ang * 3 + r * 9)
                    tono = ("brote", 2) if remolino > 0.5 else (("brote", 1) if remolino > -0.3 else ("hoja", 1))
                    if r < 0.18:
                        tono = ("luz", 3)
                    l.px(x, y, *tono)
                else:
                    tono = ("giza", 1) if (x * 3 + y * 7) % 11 else ("giza", 2)
                    l.px(x, y, *tono)
    # las dos raíces que forman el arco (se trenzan arriba)
    for lado in (-1, 1):
        for k in range(160):
            t = k / 159
            ang = math.pi * (1 - t) if lado < 0 else math.pi * t
            # recorre el arco de abajo a arriba por cada lado
            if t < 0.5:
                y = base - (base - 40) * (t / 0.5)
                x = cx + lado * 27
            else:
                a = (t - 0.5) / 0.5 * (math.pi / 2)
                x = cx + lado * 27 * math.cos(a)
                y = 40 - 28 * math.sin(a)
            g = 5.5 - 1.5 * t + math.sin(k * 0.4 + lado) * 0.8
            for gx in range(-int(g), int(g) + 1):
                u = (gx + g) / (2 * g)
                tono = 3 if u < 0.3 else (2 if u < 0.75 else 1)
                if (k + gx * 3) % 9 == 0:
                    tono = 1
                l.px(x + gx, y + math.sin(k * 0.3) * 0.8, "corteza", tono)
    # pies de raíz que se hunden en el suelo
    for lado in (-1, 1):
        for k in range(10):
            l.rect(cx + lado * (30 + k), base - 2 + k // 4, cx + lado * (30 + k), base, "corteza", 2)
    # runas en las raíces: apagadas o encendidas
    for (rx, ry) in [(cx - 27, 72), (cx - 27, 56), (cx + 27, 64), (cx + 27, 48), (cx - 10, 13), (cx + 12, 14)]:
        l.px(rx, ry, "luz" if abierto else "gris", 3 if abierto else 1)
        l.px(rx, ry + 1, "luz" if abierto else "gris", 2 if abierto else 1)
    # hojas nuevas si está abierto
    if abierto:
        for (x, y) in [(cx - 31, 30), (cx + 30, 26), (cx - 2, 8), (cx + 8, 9)]:
            l.ovalo(x, y, 2.4, 1.6, "brote")
    l.sin_contorno = {"luz", "brote", "giza"}
    return l.imagen()


def crater():
    l = Lienzo(56, 26)
    l.ovalo(28, 13, 26, 11, "gris", plano=1)
    l.ovalo(28, 14, 22, 8.5, "tierra", plano=1)
    l.ovalo(28, 15, 18, 6, "tierra", plano=0)
    l.ovalo(27, 11, 21, 6, "gris", plano=2, recorte=lambda x, y: y < 9)
    for (x, y) in [(6, 8), (50, 10), (12, 20), (44, 21), (3, 14)]:
        l.px(x, y, "gris", 3)
    # una chispa de luz: algo cayó aquí
    l.px(28, 15, "luz", 3); l.px(27, 15, "luz", 2); l.px(29, 15, "luz", 2)
    l.sin_contorno = {"luz", "gris", "tierra"}
    return l.imagen(contorno=False)


def cetro_pared():
    """El cetro de la familia, en su soporte de madera."""
    cetro = Image.open(os.path.join(RAIZ, "arte", "personajes", "maisha", "prendas", "cetro_raiz.png")).convert("RGBA")
    l = Lienzo(22, 30)
    l.rect(1, 22, 20, 25, "corteza", 2)
    l.rect(1, 22, 20, 22, "corteza", 3)
    l.rect(3, 26, 4, 29, "corteza", 1); l.rect(17, 26, 18, 29, "corteza", 1)
    img = l.imagen()
    grande = cetro.resize((cetro.width, cetro.height), Image.NEAREST)
    img.alpha_composite(grande, (7, 3))
    return img


def interior_casa_shamba():
    """La casa del castor por dentro: chimenea con una olla, mesa, cama, tarros de semillas,
    y en la pared del fondo, el soporte del cetro de la familia (el cetro es un dibujo aparte)."""
    azar = random.Random(3)

    def pared(x, y):
        tronco = (y - 20) // 6
        if (y - 20) % 6 == 5:
            return ("corteza", 1)
        return ("corteza", 3 if (x + tronco * 11) % 37 < 30 else 2)

    techo = lambda x, y: ("paja", 1 if y < 12 else 2)

    def suelo(x, y):
        tabla = (y - 72) // 8
        if (y - 72) % 8 == 7 or (x + tabla * 19) % 52 == 0:
            return ("cobre", 1)
        return ("cobre", 2) if azar.random() < 0.97 else ("cobre", 1)

    l = habitacion(pared, techo, suelo)
    # chimenea de piedra con olla
    l.rect(40, 26, 84, 74, "gris", 2)
    for y in range(26, 75, 6):
        l.rect(40, y, 84, y, "gris", 1)
    l.rect(40, 26, 41, 74, "gris", 3)
    for y in range(52, 72):
        for x in range(50, 75):
            if y > 56 or abs(x - 62) < 9:
                l.px(x, y, "oscuro", 0)
    for x in range(51, 74):
        alto = 4 + int(3 * abs(math.sin(x * 0.7)))
        for k in range(alto):
            l.px(x, 71 - k, "luz" if k < 2 else "ambar", 2 if k < 2 else 2)
    l.ovalo(62, 60, 7, 5, "gris", plano=1)                   # olla
    l.rect(55, 56, 69, 56, "gris", 3)
    # soporte del cetro en la pared (el cetro va aparte)
    l.rect(148, 28, 172, 60, "corteza", 1)
    l.rect(150, 30, 170, 58, "cobre", 1)
    for (x, y) in [(152, 32), (167, 32), (152, 55), (167, 55)]:
        l.px(x, y, "ambar", 3)
    # tarros de semillas en estantes
    for (ey, cuantos) in [(36, 5), (52, 4)]:
        l.rect(200, ey, 250, ey + 1, "corteza", 1)
        for k in range(cuantos):
            x = 203 + k * 10
            mat = ["paja", "naranja", "brote", "papel", "seta"][k % 5]
            l.rect(x, ey - 9, x + 6, ey - 1, mat, 2)
            l.rect(x + 1, ey - 11, x + 5, ey - 10, "corteza", 3)
    # mesa con dos taburetes y un plato
    l.rect(120, 108, 176, 128, "corteza", 3)
    l.rect(120, 108, 176, 109, "cobre", 3)
    l.rect(122, 129, 125, 138, "corteza", 1); l.rect(171, 129, 174, 138, "corteza", 1)
    l.ovalo(140, 116, 7, 3, "papel", plano=3)
    l.ovalo(140, 116, 4, 1.6, "naranja", plano=2)            # zanahorias en el plato
    for tx in (108, 188):
        l.ovalo(tx, 122, 6, 4, "corteza")
    # cama con manta de cuadros
    l.rect(250, 70, 286, 112, "corteza", 1)
    for y in range(76, 110):
        for x in range(252, 285):
            cuadro = ((x - 252) // 5 + (y - 76) // 5) % 2
            l.px(x, y, "seta" if cuadro else "papel", 2)
    l.ovalo(268, 74, 12, 4, "papel")
    # saco de semillas y azada
    l.ovalo(44, 160, 9, 11, "papel")
    l.rect(40, 150, 48, 151, "corteza", 1)
    l.linea(276, 176, 284, 136, "corteza", 3)
    l.rect(281, 133, 287, 136, "gris", 3)
    return _fondo_negro(l)


def pez():
    img = Image.new("RGBA", (12, 6), (0, 0, 0, 0))
    px = img.load()
    for x in range(1, 9):
        for y in range(1, 5):
            if ((x - 5) / 4.2) ** 2 + ((y - 2.5) / 2) ** 2 <= 1:
                px[x, y] = c("Agua 1", 200)
    for (x, y) in [(9, 1), (10, 0), (9, 4), (10, 5), (9, 2), (9, 3)]:
        px[x, y] = c("Agua 1", 200)
    return img


def molino(fotograma):
    """La rueda del molino de agua: 2 fotogramas con los radios girados (parece que da vueltas)."""
    l = Lienzo(44, 44)
    mx, my, mr = 22, 22, 19
    giro = fotograma * (math.tau / 16)
    for y in range(44):
        for x in range(44):
            d = math.hypot(x + 0.5 - mx, y + 0.5 - my)
            if d <= mr:
                ang = (math.atan2(y + 0.5 - my, x + 0.5 - mx) - giro) % math.tau
                radio = (ang * 8 / math.tau) % 1 < 0.2
                if d > mr - 3:
                    l.px(x, y, "corteza", 2 if d > mr - 1 else 3)
                elif radio or d < 4:
                    l.px(x, y, "corteza", 1 if d < 4 else 2)
    for k in range(12):
        a = k * math.tau / 12 + giro
        px_, py_ = mx + math.cos(a) * (mr + 0.5), my + math.sin(a) * (mr + 0.5)
        l.rect(px_ - 1, py_ - 1, px_ + 1, py_ + 1, "cobre", 2)
    l.ovalo(mx, my, 2, 2, "gris", plano=3)
    return l.imagen()


# --- La aldea antigua y otras ruinas del Kitovu ---------------------------------------------

def ruina_casa(variante):
    """Casas de la aldea antigua: muros de piedra caídos, vigas y tejado hundido."""
    l = Lienzo(60, 50)
    azar = random.Random(30 + variante)
    x0, x1 = 6, 54
    for x in range(x0, x1 + 1):
        alto = 22 + int(10 * abs(math.sin(x * (0.21 if variante else 0.15) + variante))) + (6 if variante and 20 < x < 34 else 0)
        for y in range(48 - alto, 49):
            fila = (y - 10) // 5
            junta = y % 5 == 0 or (x + fila * 4) % 9 == 0
            l.px(x, y, "gris", 1 if junta else (3 if x < 12 or (x // 9 + fila) % 4 == 0 else 2))
    # hueco de la puerta y una ventana
    l.rect(24, 34, 33, 48, "oscuro", 0)
    l.rect(40, 30, 46, 36, "oscuro", 0) if variante == 0 else l.rect(12, 30, 17, 35, "oscuro", 0)
    # vigas del tejado caídas
    l.linea(2, 26, 30, 40, "corteza", 1, grosor=2)
    l.linea(32, 18 if variante else 24, 58, 34, "corteza", 2, grosor=2)
    # paja vieja y musgo
    for _ in range(14):
        x, y = azar.randint(6, 54), azar.randint(16, 30)
        v = l.get(x, y)
        if v and v[0] == "gris":
            l.px(x, y, "musgo", 2)
    for _ in range(10):
        x = azar.randint(2, 58)
        l.ovalo(x, 48, 1.8, 1.2, "gris")
    return l.imagen()


def pozo():
    l = Lienzo(30, 38)
    l.ovalo(15, 30, 12, 6, "gris")
    l.rect(3, 24, 27, 33, "gris", 2)
    for y in range(24, 34, 3):
        for x in range(3, 28):
            if (x + y) % 6 == 0:
                l.px(x, y, "gris", 1)
    l.rect(3, 24, 27, 24, "gris", 3)
    l.ovalo(15, 24, 10, 3, "oscuro", plano=0)
    for x in (4, 25):
        l.rect(x, 4, x + 1, 25, "corteza", 3 if x == 4 else 2)
    l.rect(2, 3, 28, 5, "corteza", 2)                          # travesaño
    l.linea(1, 4, 9, 0, "corteza", 1); l.linea(29, 4, 21, 0, "corteza", 1)   # tejadillo roto
    l.linea(15, 5, 15, 16, "papel", 1)                          # cuerda
    l.rect(12, 16, 18, 21, "corteza", 2)                       # cubo
    l.rect(12, 16, 18, 16, "gris", 3)
    return l.imagen()


def torre():
    """Atalaya de piedra en ruinas, con la parte de arriba rota."""
    l = Lienzo(44, 92)
    for y in range(14, 90):
        ancho = 14 + (y - 14) // 16
        for x in range(22 - ancho, 22 + ancho + 1):
            fila = y // 6
            if y < 26 and x > 22 + int(10 * math.sin(x * 0.7)) - 6 + (26 - y):
                continue                                         # borde de arriba roto
            junta = y % 6 == 0 or (x + fila * 5) % 11 == 0
            u = (x - (22 - ancho)) / (2 * ancho)
            l.px(x, y, "gris", 1 if junta else (3 if u < 0.25 else (2 if u < 0.75 else 1)))
    for (wx, wy) in [(20, 34), (20, 56)]:
        l.rect(wx, wy, wx + 3, wy + 7, "oscuro", 0)
        l.rect(wx, wy, wx + 3, wy, "gris", 3)
    l.rect(17, 76, 26, 89, "oscuro", 0)                        # puerta
    for (x, y) in [(10, 40), (12, 41), (32, 62), (31, 63), (9, 72), (30, 22)]:
        l.px(x, y, "musgo", 2)
    for k in range(6):
        l.ovalo(4 + k * 7, 89, 2, 1.4, "gris")                  # piedras caídas
    return l.imagen()


def monumento():
    """El Monumento de las Raíces: un pilar tallado con raíces en espiral y un cristal apagado arriba."""
    l = Lienzo(44, 72)
    # escalones de la base
    l.rect(2, 62, 41, 70, "gris", 2); l.rect(2, 62, 41, 62, "gris", 3)
    l.rect(7, 56, 36, 62, "gris", 2); l.rect(7, 56, 36, 56, "gris", 3)
    # pilar
    for y in range(18, 57):
        for x in range(14, 30):
            u = (x - 14) / 16
            l.px(x, y, "gris", 3 if u < 0.25 else (2 if u < 0.75 else 1))
    # raíces talladas en espiral alrededor del pilar
    for k in range(80):
        t = k / 80
        y = 56 - t * 38
        x = 22 + math.sin(t * math.tau * 2.5) * 7
        if math.cos(t * math.tau * 2.5) > -0.2:
            l.px(x, y, "corteza", 2)
            l.px(x + 1, y, "corteza", 1)
    # cristal agrietado arriba (apagado: el gris de Giza)
    for y in range(4, 19):
        medio = 6 - abs(y - 11) * 0.8
        for x in range(int(22 - medio), int(22 + medio) + 1):
            l.px(x, y, "gris", 3 if x < 22 else 2)
    l.linea(20, 6, 24, 16, "gris", 1)
    l.rect(16, 17, 28, 19, "gris", 1)
    for (x, y) in [(16, 30), (27, 44), (15, 50)]:
        l.px(x, y, "musgo", 3)
    return l.imagen()


def raiz_gigante(variante):
    """Un trozo de raíz del mundo, seca y agrietada, que asoma del suelo y se vuelve a hundir."""
    l = Lienzo(100, 30)
    for x in range(100):
        t = x / 99
        cy = 18 + math.sin(t * math.pi * (1.4 if variante else 1.0) + variante) * 5
        grosor = 3 + 8 * math.sin(t * math.pi) ** 0.7
        for y in range(int(cy - grosor), int(cy + grosor) + 1):
            u = (y - (cy - grosor)) / (2 * grosor)
            tono = 3 if u < 0.22 else (2 if u < 0.68 else 1)
            veta = math.sin((y - cy) * 1.3 + math.sin(x * 0.15) * 2.0)
            if veta > 0.85 and 0.2 < u < 0.9:
                tono = max(1, tono - 1)                           # vetas a lo largo
            if x % 17 == variante * 5 and 0.15 < u < 0.85:
                tono = 0 if tono > 1 else 1                       # grietas de través
            l.px(x, y, "corteza", tono)
    # restos de musgo seco
    for x in range(8, 92, 9):
        cy = 18 + math.sin(x / 99 * math.pi * (1.4 if variante else 1.0) + variante) * 5
        grosor = 3 + 8 * math.sin(x / 99 * math.pi) ** 0.7
        l.px(x, cy - grosor + 1, "gris", 3)
    return l.imagen()


def carro():
    l = Lienzo(44, 28)
    l.linea(4, 10, 36, 16, "corteza", 2, grosor=3)               # caja del carro, inclinada
    l.rect(8, 8, 34, 14, "corteza", 3)
    for x in range(8, 35, 5):
        l.rect(x, 8, x, 14, "corteza", 1)
    l.ovalo(12, 20, 6, 6, "corteza")                            # rueda entera
    l.ovalo(12, 20, 3.5, 3.5, None) if False else None
    for k in range(8):
        a = k * math.tau / 8
        l.linea(12, 20, 12 + math.cos(a) * 5, 20 + math.sin(a) * 5, "corteza", 1)
    l.ovalo(33, 25, 6, 2, "corteza", plano=1)                   # rueda caída
    l.linea(36, 12, 43, 6, "corteza", 3)                        # lanza rota
    return l.imagen()


def farol_apagado():
    l = Lienzo(10, 28)
    l.rect(4, 6, 5, 27, "gris", 2)
    l.rect(4, 6, 4, 27, "gris", 3)
    l.rect(1, 1, 8, 6, "gris", 1)
    l.rect(2, 2, 7, 5, "oscuro", 2)
    l.px(3, 3, "gris", 3)
    l.rect(2, 26, 7, 27, "gris", 2)
    return l.imagen()


def trigo(fotograma):
    """Una mata de trigo que se mece (2 fotogramas)."""
    l = Lienzo(16, 18)
    for k, x in enumerate((3, 6, 9, 12)):
        inclina = (1 if fotograma else -1) * (1 if k % 2 else 0)
        l.linea(x, 17, x + inclina, 7, "hoja", 2 if k % 2 else 3)
        l.px(x - 1, 12, "hoja", 3); l.px(x + 1, 13, "hoja", 2)      # hojas
        l.ovalo(x + inclina + 0.5, 4, 1.6, 3.2, "paja")
        l.px(x + inclina, 0, "paja", 3)
    return l.imagen()


def gallina(fotograma):
    l = Lienzo(10, 10)
    l.ovalo(5, 6, 3.6, 2.8, "papel")
    l.ovalo(2.5, 3.5, 1.8, 1.8, "papel")
    l.px(1, 2, "seta", 2); l.px(2, 1, "seta", 2)                 # cresta
    l.px(0, 4, "paja", 2)                                        # pico
    l.px(2, 3, "oscuro", 0)
    l.ovalo(8, 5, 1.6, 1.6, "papel", plano=2)                    # cola
    pata = (4, 6) if fotograma == 0 else (5, 5)
    l.px(pata[0], 9, "paja", 1); l.px(pata[1], 9, "paja", 1)
    return l.imagen()


# --- Mzee Shamba: más grande que los demás aldeanos, y su retrato para los diálogos ----------

def shamba():
    """MZEE SHAMBA (32x40): castor anciano y agricultor. Sombrero de paja, gafas, cejas y barba
    blancas, delantal de trabajo con una zanahoria en el bolsillo, bastón y la cola plana."""
    l = Lienzo(32, 40)
    # cola plana detrás, con escamas
    l.ovalo(26, 33, 5.5, 4.2, "corteza")
    for (x, y) in [(24, 32), (26, 31), (28, 33), (25, 34), (27, 35), (29, 31), (23, 34)]:
        l.px(x, y, "corteza", 1)
    # cuerpo grande y barriga
    l.ovalo(16, 29, 9.5, 9.5, "tierra")
    l.ovalo(16, 30.5, 6, 6.5, "papel", plano=2)
    # delantal verde con bolsillo y una zanahoria asomando
    l.rect(10, 24, 22, 36, "hoja", 2)
    l.rect(10, 24, 22, 24, "hoja", 3)
    l.rect(22, 24, 22, 36, "hoja", 1)
    l.linea(11, 24, 13, 20, "hoja", 1); l.linea(21, 24, 19, 20, "hoja", 1)   # tirantes
    l.rect(13, 29, 19, 33, "hoja", 1)
    l.rect(13, 29, 19, 29, "hoja", 3)
    l.px(17, 27, "naranja", 3); l.px(17, 28, "naranja", 2); l.px(16, 26, "brote", 2); l.px(18, 26, "brote", 1)
    # patas
    l.rect(10, 37, 13, 39, "tierra", 1); l.rect(19, 37, 22, 39, "tierra", 1)
    # cabeza
    l.ovalo(9, 11, 2.4, 2.4, "tierra"); l.ovalo(23, 11, 2.4, 2.4, "tierra")   # orejas
    l.ovalo(16, 16.5, 8, 7, "tierra")
    l.ovalo(16, 20, 4.8, 3.3, "papel")                             # hocico
    l.rect(15, 17, 17, 18, "oscuro", 0)                            # nariz
    l.px(15, 17, "gris", 3)
    l.rect(15, 22, 17, 24, "papel", 3)                             # dientes de castor
    l.rect(16, 22, 16, 24, "papel", 1)
    for (x, y) in [(11, 21), (12, 22), (13, 23), (20, 23), (19, 22), (21, 21), (14, 24), (18, 24)]:
        l.px(x, y, "papel", 3)                                     # barba blanca
    # ojos con gafas redondas
    for cx in (12, 20):
        for (dx, dy) in [(-1, -2), (0, -2), (1, -2), (-2, -1), (2, -1), (-2, 0), (2, 0), (-2, 1), (2, 1), (-1, 2), (0, 2), (1, 2)]:
            l.px(cx + dx, 15 + dy, "gris", 3)
        l.rect(cx - 1, 14, cx, 15, "oscuro", 0)
        l.px(cx - 1, 14, "papel", 3)
    l.rect(14, 14, 18, 14, "gris", 3)                              # puente de las gafas
    for (x, y) in [(9, 12), (10, 11), (11, 11), (12, 11), (20, 11), (21, 11), (22, 11), (23, 12)]:
        l.px(x, y, "papel", 3)                                     # cejas pobladas
    # sombrero de paja de ala ancha con cinta roja
    l.rect(10, 3, 22, 8, "paja", 2)
    l.rect(10, 3, 22, 3, "paja", 3)
    l.rect(21, 4, 22, 8, "paja", 1)
    l.rect(10, 7, 22, 8, "seta", 1)
    l.rect(4, 9, 28, 10, "paja", 2)
    l.rect(4, 9, 28, 9, "paja", 3)
    for x in range(5, 28, 3):
        l.px(x, 10, "paja", 1)
    l.px(12, 5, "brote", 2); l.px(13, 4, "brote", 2)               # una ramita en el sombrero
    # bastón de madera con una hoja atada, y las manos
    for y in range(16, 40):
        l.px(4, y, "corteza", 3 if y % 4 else 2)
        l.px(5, y, "corteza", 2)
    l.ovalo(4.5, 15, 2, 2, "corteza")
    l.px(6, 13, "hoja", 3); l.px(7, 12, "hoja", 3)
    l.ovalo(5.5, 26, 2.2, 2.6, "tierra")
    l.ovalo(25, 27, 2.2, 2.8, "tierra")
    return l.imagen()


def retrato_shamba(cara="normal"):
    """Retrato de Mzee Shamba para la caja de diálogo (64x64).
    cara: normal, sonrisa, sorpresa, triste o pensativo (en los diálogos: «[sonrisa] texto»)."""
    l = Lienzo(64, 64)
    # hombros con el delantal
    l.ovalo(32, 66, 30, 20, "tierra")
    l.rect(16, 52, 48, 63, "hoja", 2)
    l.rect(16, 52, 48, 53, "hoja", 3)
    l.rect(46, 52, 48, 63, "hoja", 1)
    l.linea(18, 52, 22, 46, "hoja", 1, grosor=2); l.linea(46, 52, 42, 46, "hoja", 1, grosor=2)
    # orejas y cabeza
    l.ovalo(15, 22, 5, 5, "tierra"); l.ovalo(49, 22, 5, 5, "tierra")
    l.ovalo(15, 22, 2.5, 2.5, "corteza", plano=1); l.ovalo(49, 22, 2.5, 2.5, "corteza", plano=1)
    l.ovalo(32, 33, 19, 17, "tierra")
    # pelo con mechones (algunas líneas más oscuras)
    for (x0, y0, x1, y1) in [(18, 30, 20, 34), (45, 30, 43, 35), (22, 44, 24, 47), (41, 44, 40, 47), (26, 19, 27, 22), (37, 19, 36, 22)]:
        l.linea(x0, y0, x1, y1, "tierra", 1)
    # hocico claro
    l.ovalo(32, 41, 11, 7.5, "papel")
    l.ovalo(32, 36.5, 4, 2.8, "oscuro", plano=0)                   # nariz
    l.px(30, 35, "gris", 3); l.px(31, 35, "gris", 3)
    l.linea(32, 39, 32, 42, "papel", 1)
    l.linea(28, 43, 32, 42, "papel", 1); l.linea(36, 43, 32, 42, "papel", 1)
    # boca y dientes de castor (dos paletas separadas)
    for x in range(27, 38):
        borde = x in (27, 37)
        if cara == "sonrisa":
            dy = -1 if borde else 0                                 # las comisuras suben
        elif cara == "triste":
            dy = 2 if borde else (1 if x in (28, 36) else 0)        # y aquí bajan
        else:
            dy = 1 if borde else 0
        l.px(x, 43 + dy, "corteza", 1)
    if cara == "sonrisa":
        l.px(26, 41, "corteza", 1); l.px(38, 41, "corteza", 1)
    for x0 in (29, 33):
        l.rect(x0, 44, x0 + 2, 49, "papel", 3)
        l.rect(x0 + 2, 45, x0 + 2, 49, "papel", 2)
    l.rect(32, 44, 32, 49, "corteza", 1)
    l.rect(28, 44, 28, 49, "corteza", 1); l.rect(36, 44, 36, 49, "corteza", 1)
    l.rect(29, 50, 35, 50, "corteza", 1)
    # barba blanca: mechones en las mejillas y una perilla bajo los dientes
    for (x, y) in [(20, 42), (19, 43), (21, 44), (18, 45), (20, 46), (44, 42), (45, 43), (43, 44), (46, 45), (44, 46)]:
        l.px(x, y, "papel", 3)                                     # pelos blancos en las mejillas
    l.ovalo(32, 54, 5, 3, "papel", plano=3)                        # perilla
    for (x0, y0, x1, y1) in [(30, 53, 29, 57), (34, 53, 35, 57), (32, 55, 32, 58)]:
        l.linea(x0, y0, x1, y1, "papel", 2)
    # gafas grandes y ojos con brillo
    for cx in (24, 40):
        for k in range(36):
            a = k * math.tau / 36
            l.px(cx + math.cos(a) * 5.6, 30 + math.sin(a) * 5.0, "gris", 3)
        l.ovalo(cx, 30, 4.4, 3.8, "agua", plano=3)                 # cristal
        if cara == "sonrisa":
            # ojos cerrados de alegría: un arco hacia arriba
            for (dx, dy) in [(-2, 31), (-1, 30), (0, 29), (1, 30), (2, 31)]:
                l.px(cx + dx, dy, "oscuro", 0)
        elif cara == "sorpresa":
            l.ovalo(cx, 30, 3.4, 3.2, "papel", plano=3)            # ojos muy abiertos
            l.ovalo(cx, 30, 1.5, 1.7, "oscuro", plano=0)          # con la pupila pequeña
        elif cara == "triste":
            l.ovalo(cx, 31.2, 2.2, 2.2, "oscuro", plano=0)         # mira abajo
            l.px(cx - 1, 30, "papel", 3)
        elif cara == "pensativo":
            l.ovalo(cx + 1.6, 29.6, 2.2, 2.4, "oscuro", plano=0)   # mira a un lado
            l.px(cx + 1, 28, "papel", 3)
        else:
            l.ovalo(cx, 30.5, 2.4, 2.6, "oscuro", plano=0)
            l.px(cx - 1, 29, "papel", 3); l.px(cx - 2, 29, "papel", 3); l.px(cx - 1, 28, "papel", 3)
    l.rect(29, 29, 35, 29, "gris", 3)
    # cejas blancas pobladas, arrugas
    for lado, (x0, x1, y) in enumerate([(17, 28, 22), (36, 47, 22)]):
        if cara == "sorpresa":
            y += 0
        if cara == "pensativo" and lado == 1:
            y -= 2
        for x in range(x0, x1 + 1):
            inclina = 0
            if cara == "triste":
                # el lado de dentro sube: cara de pena
                interior = x1 if lado == 0 else x0
                inclina = -int(round(2 * (1 - abs(x - interior) / (x1 - x0))))
            l.px(x, y + inclina + (1 if x in (x0, x1) else 0), "papel", 3)
            if x % 2 == 0:
                l.px(x, y + inclina - 1, "papel", 3)
    l.linea(20, 37, 23, 38, "tierra", 1); l.linea(44, 37, 41, 38, "tierra", 1)
    if cara == "sonrisa":
        for cx in (19, 45):
            l.ovalo(cx, 39, 2.2, 1.2, "seta", plano=3)               # mejillas sonrojadas
    if cara == "triste":
        l.px(19, 36, "agua", 3); l.px(19, 37, "agua", 3); l.px(19, 38, "agua", 2)   # una lágrima
    # sombrero de paja: copa y ala, con cinta roja y ramita
    l.rect(18, 3, 46, 15, "paja", 2)
    l.rect(18, 3, 46, 4, "paja", 3)
    l.rect(43, 5, 46, 15, "paja", 1)
    for x in range(19, 46, 3):
        l.linea(x, 5, x + 1, 12, "paja", 1)
    l.rect(18, 12, 46, 15, "seta", 2)
    l.rect(18, 12, 46, 12, "seta", 3)
    l.rect(4, 16, 60, 19, "paja", 2)
    l.rect(4, 16, 60, 16, "paja", 3)
    l.rect(4, 19, 60, 19, "paja", 1)
    l.ovalo(24, 9, 3, 1.6, "hoja"); l.ovalo(28, 7, 2.6, 1.4, "brote")
    return l.imagen()


# --- Iconos de la mochila (16x16) ---------------------------------------------------------

def icono(dibujo):
    l = Lienzo(16, 16)
    dibujo(l)
    return l.imagen()


def i_zanahoria(l):
    for k in range(9):
        r = 2.6 - k * 0.25
        l.ovalo(7 + k * 0.6, 6 + k, r, 1.6, "naranja", recorte=None)
    for (x, y) in [(5, 6), (8, 9), (9, 12)]:
        l.px(x, y, "naranja", 1)
    for (x, y) in [(5, 1), (6, 2), (7, 1), (8, 3), (4, 3), (6, 4)]:
        l.px(x, y, "brote", 2 if (x + y) % 2 else 1)
    l.ovalo(6.5, 3.5, 1.4, 1.4, "brote")


def i_pez(l):
    l.ovalo(7, 8, 5.5, 3.2, "agua")
    l.ovalo(6, 9, 3.5, 1.5, "papel", plano=3)
    for (x, y) in [(12, 6), (13, 5), (12, 10), (13, 11), (12, 7), (12, 9), (13, 8)]:
        l.px(x, y, "agua", 2)
    l.px(4, 7, "oscuro", 0)


def i_tablas(l):
    for k in range(3):
        y = 4 + k * 3
        l.rect(2 + k, y, 13 + k % 2, y + 2, "cobre", 3 if k % 2 == 0 else 2)
        l.rect(2 + k, y, 13 + k % 2, y, "cobre", 3)


def i_mapa(l):
    l.rect(2, 3, 13, 12, "papel", 2)
    l.rect(2, 3, 13, 3, "papel", 3)
    for x in (5, 9):
        l.rect(x, 3, x, 12, "papel", 1)
    l.linea(3, 10, 6, 6, "seta", 1); l.linea(6, 6, 10, 9, "seta", 1)
    l.px(11, 5, "seta", 1); l.px(12, 6, "seta", 1)
    # esquina rota
    l.m[12][13] = None; l.m[11][13] = None; l.m[12][12] = None


def i_cetro(l):
    cetro = Image.open(os.path.join(RAIZ, "arte", "personajes", "maisha", "prendas", "cetro_raiz.png")).convert("RGBA")
    return cetro


def iconos():
    lista = [icono(i_zanahoria), icono(i_pez), icono(i_tablas), icono(i_mapa)]
    # cetro: el dibujo del juego, centrado
    cetro = Image.open(os.path.join(RAIZ, "arte", "personajes", "maisha", "prendas", "cetro_raiz.png")).convert("RGBA")
    hoja = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    hoja.alpha_composite(cetro.crop((0, 1, 7, 17)), (4, 0))
    lista.append(hoja)
    # seta luminosa y mineral: los dibujos del prado
    for nombre in ("seta_luminosa", "mineral", "madera"):
        ruta = os.path.join(RAIZ, "arte", "mundos", "raiz", "objetos", nombre + ".png")
        if not os.path.exists(ruta):
            continue
        im = Image.open(ruta).convert("RGBA")
        im = im.crop((0, 0, im.width // 2, im.height))
        hoja = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        hoja.alpha_composite(im, ((16 - im.width) // 2, 16 - im.height - 1))
        lista.append(hoja)
    sheet = Image.new("RGBA", (16 * len(lista), 16), (0, 0, 0, 0))
    for i, im in enumerate(lista):
        sheet.alpha_composite(im, (i * 16, 0))
    return sheet


# --- El mapa del mundo, roto ------------------------------------------------------------

def mapa_mundo():
    """Pergamino con los mundos alrededor del Kitovu. El trozo de Sigilia está arrancado."""
    W, H = 300, 190
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    azar = random.Random(12)
    # pergamino con el borde irregular
    for y in range(H):
        for x in range(W):
            borde = min(x, y, W - 1 - x, H - 1 - y)
            ruido = math.sin(x * 0.31) + math.sin(y * 0.27 + x * 0.05)
            if borde < 3 + ruido:
                continue
            tono = "Pergamino 3" if borde > 12 else "Pergamino 2"
            if azar.random() < 0.03:
                tono = "Pergamino 2"
            px[x, y] = c(tono)
    d = ImageDraw.Draw(img)

    def mancha(cx, cy, rx, ry, color, borde):
        for y in range(int(cy - ry - 3), int(cy + ry + 4)):
            for x in range(int(cx - rx - 3), int(cx + rx + 4)):
                ang = math.atan2(y - cy, x - cx)
                r = 1 + 0.15 * math.sin(ang * 5 + cx) + 0.08 * math.sin(ang * 11)
                q = ((x - cx) / (rx * r)) ** 2 + ((y - cy) / (ry * r)) ** 2
                if 0 <= x < W and 0 <= y < H and px[x, y][3]:
                    if q <= 0.82:
                        px[x, y] = c(color)
                    elif q <= 1.0:
                        px[x, y] = c(borde)

    # los mundos alrededor del centro
    mundos = [(78, 120, 52, 36, "Hierba 3", "Hierba 1", "Raíz"),
              (150, 48, 50, 26, "Agua 4", "Agua 1", "Sigilia"),
              (232, 110, 44, 34, "Flor ambar 3", "Flor ambar 1", "Asterhaul"),
              (170, 160, 36, 18, "Giza 4", "Giza 1", "Valle del Ocaso")]
    for (x, y, rx, ry, col, bor, _) in mundos:
        mancha(x, y, rx, ry, col, bor)
    # el Kitovu en el centro y las raíces que lo unen a cada mundo (líneas de puntos)
    centro = (152, 108)
    for (x, y, rx, ry, col, bor, _) in mundos:
        pasos = int(math.hypot(x - centro[0], y - centro[1]) / 3)
        for k in range(pasos):
            t = k / pasos
            qx = centro[0] + (x - centro[0]) * t
            qy = centro[1] + (y - centro[1]) * t
            if k % 2 == 0:
                d.point((qx, qy), fill=c("Madera 2"))
    mancha(centro[0], centro[1], 12, 8, "Piedra 3", "Piedra 1")
    d.point(centro, fill=c("Flor roja 2"))
    # rótulos
    fuente = ImageFont.truetype(os.path.join(RAIZ, "fuentes", "pixelify_sans.woff"), 12)
    d.fontmode = "1"
    for (x, y, rx, ry, col, bor, nombre) in mundos + [(centro[0], centro[1] + 14, 0, 0, "", "", "Kitovu")]:
        w = d.textlength(nombre, font=fuente)
        pos = (x - w / 2, y - 6 if nombre != "Kitovu" else y - 1)
        d.text(pos, nombre, font=fuente, fill=c("Pergamino 1"), stroke_width=1, stroke_fill=c("Pergamino 3"))
    # rosa de los vientos
    rx, ry = 270, 30
    d.line([(rx, ry - 10), (rx, ry + 10)], fill=c("Pergamino 1"))
    d.line([(rx - 10, ry), (rx + 10, ry)], fill=c("Pergamino 1"))
    d.polygon([(rx, ry - 12), (rx - 2, ry - 6), (rx + 2, ry - 6)], fill=c("Flor roja 2"))
    # los rótulos con borde dejan algún color de mezcla: se pasan al color de la paleta más cercano
    colores = list(PAL.values())
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a and (r, g, b) not in colores:
                px[x, y] = min(colores, key=lambda q: (q[0] - r) ** 2 + (q[1] - g) ** 2 + (q[2] - b) ** 2) + (255,)
    # el trozo arrancado: el norte (Sigilia) falta, con el borde roto
    for y in range(0, 82):
        for x in range(92, 214):
            corte = 70 + 9 * math.sin(x * 0.21) + 5 * math.sin(x * 0.53 + 1) + 4 * math.sin(x * 1.3)
            izq = 96 + 6 * math.sin(y * 0.4)
            der = 210 + 5 * math.sin(y * 0.33 + 2)
            if y < corte and izq < x < der:
                px[x, y] = (0, 0, 0, 0)
            elif y < corte + 2 and izq - 2 < x < der + 2 and px[x, y][3]:
                px[x, y] = c("Pergamino 1")
    return img


if __name__ == "__main__":
    destino = os.path.join(RAIZ, "arte", "mundos", "kitovu")
    os.makedirs(destino, exist_ok=True)
    # la casa de Shamba (fuera y dentro), su molino y el cetro de la pared se pintan con detalle
    # en herramientas/pintar_casa_shamba.py
    import pintar_casa_shamba
    pintar_casa_shamba.main()
    # y los objetos de la granja (zanahorias, cerca, tronco, espantapájaros, trigo, gallinas), en pintar_granja.py
    import pintar_granja
    pintar_granja.main()
    # y las ruinas, la torre, el pozo, el monumento, las raíces gigantes, el Arco y el cráter, en pintar_ruinas.py
    import pintar_ruinas
    pintar_ruinas.main()
    carro().save(os.path.join(destino, "carro.png"))
    pez().save(os.path.join(destino, "pez.png"))
    shamba().save(os.path.join(RAIZ, "arte", "personajes", "aldeanos", "shamba_frente.png"))
    retratos = os.path.join(RAIZ, "arte", "retratos")
    os.makedirs(retratos, exist_ok=True)
    retrato_shamba().save(os.path.join(retratos, "shamba.png"))
    for cara in ("sonrisa", "sorpresa", "triste", "pensativo"):
        retrato_shamba(cara).save(os.path.join(retratos, "shamba_%s.png" % cara))
    interfaz = os.path.join(RAIZ, "arte", "interfaz")
    iconos().save(os.path.join(interfaz, "objetos.png"))
    mapa_mundo().save(os.path.join(interfaz, "mapa_mundo.png"))
    print("Kitovu dibujado en", destino)
