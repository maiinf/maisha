"""
CONSTRUIR UN MAPA a partir de su archivo de texto.

Cada mapa es un archivo de texto en datos/mapas/ donde CADA LETRA ES UNA CASILLA (16x16 píxeles).
Se puede editar a mano con cualquier editor (en el Mac, TextEdit en modo texto sin formato).
Después hay que ejecutar este programa para regenerar el dibujo del suelo:

    python3 herramientas/construir_mapa.py prados_del_eco

(Genera el dibujo del suelo y datos/mapas/<mapa>.json, que es lo que lee el juego.)

Letras del suelo (se dibujan en el suelo):
    .  hierba          ,  hierba con flores      #  camino de tierra
    ~  agua            =  puente de madera       %  losas de piedra (la plaza de la aldea)
Letras de objetos (el juego los coloca encima, con colisión):
    T  árbol A         t  árbol B                R  roca grande       r  roca pequeña
    M  matorral (se rompe con una semilla)       C  columna en ruinas W  muro en ruinas
    E  piedra-eco      Q  roca que se aparta al encender las piedras-eco
    X  secreto (esencia)                         L  cartel
    u  seta luminosa (encargo de Pino)           Y  roca con mineral (se rompe con una semilla)
    S  donde despierta Maisha
    1-9  centro de una zona corrupta (su tamaño, y el aldeano de piedra que hay a su lado,
         están en datos/mapas/<mapa>.zonas)
Letras de la aldea:
    G  el Gran Árbol (la letra marca la base del tronco, en el centro; deja sitio alrededor)
    h  casa-seta de Pino    f  taller de Corteza    k  cocina de Juncia    n  puesto de Tawi
    l  farolillo            v  valla                m  setas pequeñas de adorno (no estorban)
    b  Bibi                 p  Pino                 o  Corteza   (Pino y Corteza solo si se les ha rescatado)
Letras del Kitovu (la granja de Mzee Shamba):
    K  casa del castor     z  zanahoria del huerto  q  hueco de la cerca (se arregla con tablas)
    Z  tronco con tablas   w  sitio de pesca        e  espantapájaros     d  árbol seco
    O  cráter donde cae Maisha y  trigo (se mece)     c  gallina
    A  casa en ruinas      B  pozo seco             D  torre de la campana
    F  monumento de la leyenda                      N  raíz gigante seca
    V  carro volcado       i  farol apagado         (A B D F N V se pueden mirar: cuentan algo)
Portales (P): se definen en datos/mapas/<mapa>.puertas con un quinto campo «portal» o «portal:marca»
    (la marca es la que lo abre; sin marca, siempre está abierto).
    Una puerta normal con quinto campo «cerrada:marca» no deja pasar hasta que se pone esa marca.
    !  espinas de Giza que tapan un paso (se marchitan con la marca de la puerta cerrada más cercana)
Letras del Bosque Cobrizo:
    J  árbol cobrizo       j  árbol rojizo          I  árbol alto (bosque cerrado)
    U  tronco podrido (se rompe con una semilla y deja madera)   H  tocón hueco (se puede mirar)
    g  helechos (adorno, no estorban)
Letras de la Ciénaga Quieta:
    s  sauce llorón         x  árbol muerto          ;  juncos (adorno)      *  nenúfar (sobre el agua)
    $  bayas del pantano    :  junco dulce (ingredientes de Juncia, se recogen al pasar)
Letras del Campo Segado:
    /  surco de tierra labrada (suelo)              [  granero en ruinas (se puede mirar)
    ]  molino de viento roto (se puede mirar)        &  máquina vieja oxidada (se puede mirar)
    +  paca de paja      (y del Kitovu: y trigo, e espantapájaros, d árbol seco, v valla)
Puertas a otras escenas: cualquier otro signo (por ejemplo > o <) que aparezca en
datos/mapas/<mapa>.puertas. Las casillas seguidas con el mismo signo forman una sola puerta.
Debajo de cada objeto el suelo es hierba.

Este programa también puede crear el mapa inicial de los Prados del Eco:
    python3 herramientas/construir_mapa.py prados_del_eco --crear     (¡sobrescribe el texto!)
"""
import math
import os
import random
import sys
from PIL import Image

CASILLA = 16
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COL = {
    "H2": (0x3F, 0x58, 0x2F), "H3": (0x6A, 0x82, 0x46), "H4": (0x9A, 0xA9, 0x5F),
    "T2": (0x53, 0x3B, 0x2D), "T3": (0x7C, 0x58, 0x43), "T4": (0xA5, 0x75, 0x59),
    "A1": (0x1C, 0x35, 0x35), "A2": (0x34, 0x61, 0x61), "A3": (0x4C, 0x8D, 0x8D), "A4": (0x6D, 0xB0, 0xB0),
    "M1": (0x25, 0x18, 0x12), "M2": (0x49, 0x2E, 0x23), "M3": (0x6D, 0x45, 0x34), "M4": (0x90, 0x5C, 0x45),
    "F_A": (0xE6, 0xA8, 0x52), "F_R": (0xDE, 0x67, 0x71), "F_L": (0xFF, 0xF3, 0xC4),
    "P2": (0x52, 0x56, 0x49), "P3": (0x7A, 0x80, 0x6D), "P4": (0xA0, 0xA5, 0x96),
}
SUELO_AGUA = "~"
SUELO_CAMINO = "#"
SUELO_PUENTE = "="
SUELO_LOSAS = "%"


# ---------------------------------------------------------------------------
# Crear el mapa inicial de los Prados del Eco
# ---------------------------------------------------------------------------

def crear_prados():
    ANCHO, ALTO = 120, 68
    azar = random.Random(12)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    # río al este (Arroyo de las Corrientes), de norte a sur
    for y in range(ALTO):
        cx = 108 + int(3 * math.sin(y * 0.12) + 1.5 * math.sin(y * 0.31))
        for x in range(cx - 2, cx + 3):
            poner(x, y, "~")
    # puente hacia la aldea
    for y in (33, 34):
        for x in range(100, 116):
            if m[y][x] == "~":
                poner(x, y, "=")

    # zonas corruptas: centro y semiejes en casillas (se guardan en el archivo .zonas)
    zonas = {"1": (26, 18, 11, 8), "2": (62, 50, 13, 9), "3": (84, 16, 12, 8)}

    def en_zona(x, y, margen=2):
        for (zx, zy, rx, ry) in zonas.values():
            if ((x - zx) / (rx + margen)) ** 2 + ((y - zy) / (ry + margen)) ** 2 <= 1.0:
                return True
        return False

    # caminos: del despertar al puente, con ramales a las tres zonas
    def camino(puntos, ancho=2):
        for (a, b) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
            for i in range(pasos + 1):
                t = i / pasos
                x = a[0] + (b[0] - a[0]) * t + math.sin(t * 6.0) * 1.2
                y = a[1] + (b[1] - a[1]) * t
                for dx in range(ancho):
                    for dy in range(ancho):
                        if m[int(y) + dy][int(x) + dx] not in "~=":
                            poner(int(x) + dx, int(y) + dy, "#")

    camino([(14, 55), (24, 50), (38, 44), (52, 38), (66, 34), (82, 33), (106, 33)])
    camino([(38, 44), (34, 34), (28, 27)])
    camino([(52, 38), (58, 42)])
    camino([(82, 33), (84, 25)])

    # sitios que deben quedar despejados: el claro del despertar, el escondite y el secreto de la esquina
    reservados = [(14, 55, 8), (51, 12, 5), (10, 9, 3), (49, 22, 7)]

    def libre(x, y):
        if m[y][x] not in ".," or en_zona(x, y):
            return False
        return all((x - rx) ** 2 + (y - ry) ** 2 > rr * rr for (rx, ry, rr) in reservados)

    # bosque cerrado en los bordes (paredes naturales), con el borde irregular
    for y in range(ALTO):
        for x in range(ANCHO):
            borde = min(x, y, ANCHO - 1 - x, ALTO - 1 - y)
            grosor = 3 + 2 * math.sin(x * 0.3 + y * 0.2) + azar.random()
            if borde < grosor and m[y][x] == "." and (x + y) % 2 == 0:
                poner(x, y, "T" if azar.random() < 0.6 else "t")
    # el borde este (pasado el río) también cerrado salvo la salida del puente
    for y in range(ALTO):
        for x in range(113, ANCHO):
            if m[y][x] == "." and y not in (32, 33, 34, 35) and (x + y) % 2 == 0:
                poner(x, y, "T")

    # claro del despertar: círculo de columnas en ruinas
    sx, sy = 14, 55
    for k in range(8):
        a = k * math.tau / 8 + 0.3
        if k in (2, 5):
            continue
        cx, cy = sx + round(math.cos(a) * 6), sy + round(math.sin(a) * 4)
        poner(cx, cy, "C" if k % 2 == 0 else "W")
    poner(sx, sy, "S")
    poner(sx, sy - 2, "P")       # el Arco de Raíz: por aquí se llega desde el Kitovu

    # piedras-eco y el escondite que abren (rocas alrededor de un secreto; Q se aparta)
    for (x, y) in [(46, 22), (52, 18), (56, 25)]:
        poner(x, y, "E")
    ex, ey = 51, 12
    for (dx, dy) in [(-2, -1), (-1, -2), (0, -2), (1, -2), (2, -1), (-2, 0), (2, 0), (-2, 1), (2, 1), (-1, 2), (1, 2)]:
        poner(ex + dx, ey + dy, "R")
    poner(ex, ey + 2, "Q")
    poner(ex, ey, "X")
    # secreto tras un matorral, en una esquina: árboles alrededor y un matorral que hace de puerta
    # (se rompe con una semilla desde el prado, a la derecha)
    poner(8, 9, "X")
    for (dx, dy) in [(-1, -1), (0, -1), (1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]:
        poner(8 + dx, 9 + dy, "T")
    poner(9, 9, "M")
    for (dx, dy) in [(2, 0), (3, 0), (2, -1), (2, 1)]:
        poner(8 + dx, 9 + dy, ".")

    # arboledas (grupos de 3-7 árboles) y grupos de rocas: dan estructura al prado
    for _ in range(16):
        cx, cy = azar.randrange(8, 104), azar.randrange(6, 62)
        for _ in range(azar.randrange(3, 8)):
            x, y = cx + azar.randrange(-3, 4), cy + azar.randrange(-2, 3)
            if 0 < x < ANCHO - 1 and 0 < y < ALTO - 1 and libre(x, y):
                poner(x, y, "T" if azar.random() < 0.55 else "t")
    for _ in range(9):
        cx, cy = azar.randrange(8, 104), azar.randrange(6, 62)
        for _ in range(azar.randrange(2, 5)):
            x, y = cx + azar.randrange(-2, 3), cy + azar.randrange(-1, 2)
            if 0 < x < ANCHO - 1 and 0 < y < ALTO - 1 and libre(x, y):
                poner(x, y, azar.choice("RRrrM"))
    # objetos sueltos
    for _ in range(70):
        x, y = azar.randrange(5, 105), azar.randrange(5, 63)
        if libre(x, y) and all(m[y + dy][x + dx] in ".," for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            poner(x, y, azar.choice("TTtRrrMM"))
    for _ in range(14):
        x, y = azar.randrange(30, 100), azar.randrange(8, 62)
        if libre(x, y):
            poner(x, y, azar.choice("CW"))
    # flores
    for _ in range(260):
        x, y = azar.randrange(2, 118), azar.randrange(2, 66)
        if m[y][x] == ".":
            poner(x, y, ",")
    # cartel junto al puente
    poner(97, 31, "L")
    # setas luminosas (junto a los árboles) y rocas con mineral, para los encargos de Pino y Corteza
    for (x, y) in [(14, 32), (89, 42), (44, 6), (47, 61)]:
        poner(x, y, "u")
    for (x, y) in [(50, 34), (38, 48), (90, 48)]:
        poner(x, y, "Y")
    # salida al este, hacia Cuna de Musgo (la puerta > está en datos/mapas/prados_del_eco.puertas)
    for y in (32, 33, 34, 35):
        for x in range(108, ANCHO):
            poner(x, y, "#" if y in (33, 34) and x < ANCHO - 1 else ".")
        poner(ANCHO - 1, y, ">")
    for k, (zx, zy, rx, ry) in zonas.items():
        poner(zx, zy, k)
    return ["".join(f) for f in m], zonas


# ---------------------------------------------------------------------------
# Crear el mapa inicial del Kitovu (donde empieza el juego)
# ---------------------------------------------------------------------------

def crear_kitovu():
    """El Kitovu (64x46): el valle donde cae Maisha.
    Sur-oeste: el cráter. Centro: la granja de Mzee Shamba (lo único vivo), con su estanque,
    el huerto y el campo de trigo. Noroeste: la aldea antigua en ruinas, con el pozo y la torre.
    Norte: el monumento de la leyenda entre raíces gigantes. Noreste: el Arco de Raíz tapado por Giza."""
    ANCHO, ALTO = 64, 46
    azar = random.Random(77)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    def elipse(cx, cy, rx, ry, c):
        for y in range(ALTO):
            for x in range(ANCHO):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    poner(x, y, c)

    def camino(puntos, ancho=2):
        for (a, b) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
            for i in range(pasos + 1):
                t = i / pasos
                x = a[0] + (b[0] - a[0]) * t
                y = a[1] + (b[1] - a[1]) * t
                for dx in range(ancho):
                    for dy in range(ancho):
                        if m[int(y) + dy][int(x) + dx] in ".,":
                            poner(int(x) + dx, int(y) + dy, "#")

    arena = (54, 11)               # la arena de Mzizi, la raíz del Arco (tapa el Arco de Raíz)
    # sitios de las zonas de práctica: cada partida salen 3 de estos 6 (con una forma de 3 posibles)
    practicas = [(8, 24), (32, 37), (49, 33), (55, 23), (6, 33), (43, 39)]
    casa = (30, 23)                # base de la casa de Shamba (la puerta)
    # estanque al oeste de la casa (la rueda del molino da a él) y el sitio de pesca
    elipse(18, 27, 4.5, 2.6, "~")
    elipse(15, 26, 2.5, 1.6, "~")
    # plaza del monumento, losas viejas
    elipse(36, 9, 4, 2.2, "%")
    # huerto: tierra labrada, con zanahorias y el espantapájaros
    for y in range(22, 28):
        for x in range(39, 47):
            poner(x, y, "#")
    for (x, y) in [(40, 23), (42, 23), (44, 23), (40, 25), (42, 25), (44, 25), (46, 23), (46, 25)]:
        poner(x, y, "z")
    poner(43, 26, "e")
    # cerca del huerto (arriba y abajo) con un hueco que arreglar
    for x in range(38, 48):
        poner(x, 21, "v")
        poner(x, 28, "v")
    poner(42, 28, "q")
    # campo de trigo, al norte del huerto
    for y in range(16, 20):
        for x in range(39, 47):
            if (x + y) % 2 == 0 or y == 18:
                poner(x, y, "y")
    # caminos
    camino([(9, 41), (13, 37), (20, 33), (27, 30), (30, casa[1] + 1)])     # cráter → casa
    camino([(32, casa[1] + 1), (36, 25), (38, 25)])                        # casa → huerto
    camino([(38, 20), (40, 14), (44, 12), (47, 11)])                       # → el arco (por la arena)
    camino([(18, 16), (16, 14), (9, 11)])                                 # → la aldea antigua
    camino([(18, 16), (25, 11), (31, 10)])                                 # → torre y monumento
    camino([(38, 14), (37, 11)])
    # acequia del estanque a la rueda del molino (con un puentecito donde cruza el camino)
    for (x, y) in [(22, 25), (23, 25), (23, 24), (24, 24), (24, 23), (25, 23), (25, 22)]:
        poner(x, y, "=" if m[y][x] == "#" else "~")
    # bosque muerto en los bordes, con rocas
    for y in range(ALTO):
        for x in range(ANCHO):
            borde = min(x, y, ANCHO - 1 - x, ALTO - 1 - y)
            grosor = 2.5 + 1.5 * math.sin(x * 0.5 + y * 0.3) + azar.random()
            if borde < grosor and m[y][x] == "." and (x + y) % 2 == 0:
                poner(x, y, "d" if azar.random() < 0.7 else "R")
    # la granja: casa, tronco con tablas, sitio de pesca, gallinas
    poner(*casa, "K")
    poner(17, 21, "Z")
    poner(22, 28, "w")
    for (x, y) in [(26, 26), (34, 27), (36, 23)]:
        poner(x, y, "c")
    # la aldea antigua: casas caídas, el pozo, faroles apagados y un carro volcado
    for (x, y) in [(7, 9), (15, 8), (6, 16), (12, 17)]:
        poner(x, y, "A")
    poner(11, 13, "B")
    for (x, y) in [(9, 13), (16, 12), (21, 14)]:
        poner(x, y, "i")
    poner(17, 17, "V")
    # la torre de la campana y el monumento de la leyenda, entre raíces gigantes
    poner(25, 8, "D")
    poner(36, 9, "F")
    for (x, y) in [(29, 4), (41, 5), (3, 28), (58, 30), (24, 42)]:
        poner(x, y, "N")
    # carteles: a la granja (junto al cráter), a la aldea antigua y al arco
    poner(16, 35, "L")
    poner(33, 12, "L")
    poner(38, 17, "L")
    # cráter, el Arco de Raíz y su zona
    poner(8, 40, "S")
    poner(8, 41, "O")
    poner(54, 5, "P")
    for i, (x, y) in enumerate(practicas):
        poner(x, y, str(i + 1))
    poner(arena[0], arena[1], "7")
    # ruinas y árboles secos sueltos, lejos de lo importante
    ocupado = [(31, 21, 11), (43, 22, 8), (18, 27, 7), (8, 40, 5), (54, 9, 12), (12, 13, 8),
               (36, 9, 6), (25, 7, 4)] + [(x, y, 7) for (x, y) in practicas]

    def libre(x, y):
        if m[y][x] != "." or any(m[y + dy][x + dx] != "." for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            return False
        return all((x - ox) ** 2 + (y - oy) ** 2 > r * r for (ox, oy, r) in ocupado)

    for _ in range(90):
        x, y = azar.randrange(3, ANCHO - 3), azar.randrange(3, ALTO - 3)
        if libre(x, y):
            poner(x, y, azar.choice("ddCWrrRMi"))
    # flores, solo alrededor de la granja (lo único vivo)
    for _ in range(260):
        x, y = azar.randrange(16, 50), azar.randrange(14, 34)
        if m[y][x] == "." and math.hypot(x - 32, (y - 24) * 1.6) < 15:
            poner(x, y, ",")
    zonas = {str(i + 1): "4, 3, 3, 1, , practica" for i in range(len(practicas))}
    zonas["7"] = "6, 5, 3, 0, , jefe:mzizi"
    return ["".join(f) for f in m], zonas


# ---------------------------------------------------------------------------
# Crear el mapa inicial de Cuna de Musgo (la aldea)
# ---------------------------------------------------------------------------

def crear_aldea():
    ANCHO, ALTO = 64, 44
    azar = random.Random(31)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    def elipse(cx, cy, rx, ry, c):
        for y in range(ALTO):
            for x in range(ANCHO):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    poner(x, y, c)

    def camino(puntos, ancho=2):
        for (a, b) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
            for i in range(pasos + 1):
                t = i / pasos
                x = a[0] + (b[0] - a[0]) * t
                y = a[1] + (b[1] - a[1]) * t + math.sin(t * 5.0) * 0.6
                for dx in range(ancho):
                    for dy in range(ancho):
                        if m[int(y) + dy][int(x) + dx] == ".":
                            poner(int(x) + dx, int(y) + dy, "#")

    # estanque al sur, junto a la cocina de Juncia
    elipse(46, 35, 6.5, 3.6, "~")
    elipse(51, 33, 3, 2, "~")
    # plaza de losas delante de la puerta del Gran Árbol
    elipse(32, 21.5, 8, 3.6, "%")
    # caminos: la entrada del oeste (viene del puente de los prados), y a cada casa
    camino([(0, 21), (8, 21), (16, 21), (26, 21)])
    camino([(26, 24), (22, 27), (20, 29)])            # casa-seta de Pino
    camino([(37, 22), (44, 23)])                      # taller de Corteza
    camino([(36, 25), (38, 29), (39, 32)])            # cocina de Juncia, junto al estanque
    camino([(12, 21), (12, 18)], ancho=2)             # puesto de Tawi
    # bosque cerrado en los bordes, con el hueco de la entrada
    for y in range(ALTO):
        for x in range(ANCHO):
            borde = min(x, y, ANCHO - 1 - x, ALTO - 1 - y)
            grosor = 2.5 + 1.5 * math.sin(x * 0.4 + y * 0.3) + azar.random()
            if borde < grosor and m[y][x] == "." and (x + y) % 2 == 0 and not (x < 6 and 18 <= y <= 25):
                poner(x, y, "T" if azar.random() < 0.6 else "t")
    # entrada (puerta <, en datos/mapas/cuna_de_musgo.puertas)
    for y in range(19, 25):
        poner(0, y, "<")
    # el Gran Árbol: la letra marca la base del tronco
    poner(32, 18, "G")
    # edificios (la letra marca el centro de la base) y sus dueños
    poner(19, 30, "h"); poner(23, 31, "p")
    poner(47, 24, "f"); poner(42, 25, "o")
    poner(37, 33, "k")
    poner(34, 35, "?")                                # Juncia, junto a su cocina
    poner(12, 17, "n")
    poner(28, 21, "b")
    # farolillos alrededor de la plaza y en la entrada
    for (x, y) in [(23, 19), (41, 19), (23, 25), (41, 25), (6, 19), (6, 24)]:
        poner(x, y, "l")
    # valla del huerto de Pino
    for x in range(13, 19):
        poner(x, 33, "v")
    # carteles en la entrada
    poner(4, 18, "L")
    # árboles, rocas y matorrales sueltos, lejos de casas y caminos
    ocupado = [(32, 12, 9), (32, 21, 9), (19, 29, 5), (46, 23, 6), (37, 32, 4), (12, 17, 4), (46, 35, 8), (4, 21, 4)]

    def libre(x, y):
        if m[y][x] not in ".,":
            return False
        if any(m[y + dy][x + dx] not in ".," for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
            return False
        return all((x - ox) ** 2 + (y - oy) ** 2 > r * r for (ox, oy, r) in ocupado)

    for _ in range(40):
        x, y = azar.randrange(4, ANCHO - 4), azar.randrange(4, ALTO - 4)
        if libre(x, y):
            poner(x, y, azar.choice("TTtRrM"))
    # setas de adorno junto a los árboles y las raíces del Gran Árbol
    for _ in range(90):
        x, y = azar.randrange(3, ANCHO - 3), azar.randrange(3, ALTO - 3)
        if m[y][x] == "." and any(m[y + dy][x + dx] in "Tt" for dx in (-1, 0, 1) for dy in (-1, 0, 1)) and azar.random() < 0.5:
            poner(x, y, "m")
    for (x, y) in [(25, 17), (39, 17), (27, 16), (24, 15), (40, 16)]:
        poner(x, y, "m")
    # flores: muchas alrededor de la plaza y de las casas, y algunas sueltas
    for _ in range(500):
        x, y = azar.randrange(2, ANCHO - 2), azar.randrange(2, ALTO - 2)
        cerca = min(math.hypot(x - ox, (y - oy) * 1.5) for (ox, oy) in [(32, 21), (19, 30), (47, 24), (37, 33), (12, 17)])
        if m[y][x] == "." and azar.random() < (0.85 if cerca < 11 else 0.12):
            poner(x, y, ",")
    return ["".join(f) for f in m], {}


# ---------------------------------------------------------------------------
# Crear el mapa inicial del Bosque Cobrizo (al norte de los Prados del Eco)
# ---------------------------------------------------------------------------

def crear_bosque():
    """El Bosque Cobrizo (112x72): árboles cobrizos y rojizos muy juntos, senderos estrechos y un arroyo.
    Sur: la entrada desde los Prados. Oeste: la primera zona. Este: la zona de Tawi (de piedra).
    Noreste: la tercera zona. Noroeste: el claro de Pembe, el ciervo de hierro (minijefe), con árboles dentro
    contra los que embiste. Dos claros secretos tras matorrales y troncos podridos con madera."""
    ANCHO, ALTO = 112, 72
    azar = random.Random(55)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    def camino(puntos, ancho=2, meneo=1.0):
        for (a, b) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
            for i in range(pasos + 1):
                t = i / pasos
                x = a[0] + (b[0] - a[0]) * t + math.sin(t * 5.0 + a[1]) * meneo
                y = a[1] + (b[1] - a[1]) * t
                for dx in range(ancho):
                    for dy in range(ancho):
                        xx, yy = int(x) + dx, int(y) + dy
                        if 0 <= xx < ANCHO and 0 <= yy < ALTO:
                            if m[yy][xx] == "~":
                                poner(xx, yy, "=")
                            elif m[yy][xx] != "=":
                                poner(xx, yy, "#")

    zonas = {"1": (30, 50, 10, 7), "2": (84, 47, 12, 8), "3": (86, 16, 11, 7), "4": (38, 15, 14, 10)}

    def en_zona(x, y, margen=2):
        for (zx, zy, rx, ry) in zonas.values():
            if ((x - zx) / (rx + margen)) ** 2 + ((y - zy) / (ry + margen)) ** 2 <= 1.0:
                return True
        return False

    # el arroyo cruza el bosque de oeste a este, serpenteando
    for x in range(ANCHO):
        cy = 33 + 2.2 * math.sin(x * 0.11) + 1.2 * math.sin(x * 0.27 + 1)
        for y in range(int(cy) - 1, int(cy) + 2):
            poner(x, y, "~")
    # senderos (estrechos): entrada → zona 1 → arroyo → claro de Pembe; entrada → zona 2 → zona 3 → claro
    camino([(62, 71), (61, 64), (54, 59), (44, 55), (36, 52)])
    camino([(61, 64), (70, 60), (78, 54)])
    camino([(36, 44), (35, 38), (33, 30), (34, 25)])
    camino([(84, 40), (86, 34), (87, 28), (87, 22)])
    camino([(76, 16), (64, 14), (52, 15)])
    # claros secretos: un hueco en el bosque con un matorral de puerta
    secretos = [(7, 58, 9, 58), (104, 6, 102, 6)]
    reservados = [(62, 66, 4), (8, 58, 3), (104, 6, 3)]

    def libre(x, y):
        if m[y][x] != "." or en_zona(x, y):
            return False
        return all((x - rx) ** 2 + (y - ry) ** 2 > rr * rr for (rx, ry, rr) in reservados)

    # el bosque: muy espeso en los bordes y en manchas, con claros; nunca encima de los senderos
    for y in range(ALTO):
        for x in range(ANCHO):
            borde = min(x, y, ANCHO - 1 - x, ALTO - 1 - y)
            espeso = 0.55 + 0.35 * math.sin(x * 0.17 + 0.6) * math.sin(y * 0.21 + 1.3)
            if borde < 4:
                espeso = 1.0
            cerca_camino = any(m[y + dy][x + dx] in "#=" for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                               if 0 <= x + dx < ANCHO and 0 <= y + dy < ALTO)
            if cerca_camino or not libre(x, y):
                continue
            if (x + y) % 2 == 0 and azar.random() < (espeso * 0.85 if borde < 6 else espeso * 0.5):
                if borde < 4:
                    poner(x, y, "I" if azar.random() < 0.6 else azar.choice("Jj"))
                else:
                    poner(x, y, azar.choice("JJjjI"))
    # dentro del claro de Pembe: cuatro árboles contra los que embiste (y se queda atascado)
    ax, ay = zonas["4"][0], zonas["4"][1]
    for (dx, dy) in [(-7, -3), (7, -3), (-5, 4), (6, 4)]:
        poner(ax + dx, ay + dy, "J" if dx < 0 else "j")
    # claros secretos: el secreto, árboles alrededor y el matorral que hace de puerta
    for (sx, sy, mx, my) in secretos:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                poner(sx + dx, sy + dy, "J" if (dx + dy) % 2 else "j")
        poner(sx, sy, "X")
        poner(mx, my, "M")
        # un pasillo despejado hasta el matorral
        paso = 1 if mx > sx else -1
        for k in range(1, 5):
            if m[my][mx + paso * k] in "JjI":
                poner(mx + paso * k, my, ".")
    # troncos podridos (con madera), tocones y helechos
    for (x, y) in [(48, 61), (71, 66), (22, 42), (97, 53), (60, 27), (14, 22)]:
        poner(x, y, "U")
        for dx in (-1, 1):
            if m[y][x + dx] in "JjI":
                poner(x + dx, y, ".")
    for (x, y) in [(12, 56), (55, 44), (100, 30)]:
        poner(x, y, "H")
    for _ in range(420):
        x, y = azar.randrange(2, ANCHO - 2), azar.randrange(2, ALTO - 2)
        if m[y][x] == "." and not en_zona(x, y, 0):
            poner(x, y, "g" if azar.random() < 0.55 else "r" if azar.random() < 0.3 else ".")
    # algunas rocas con musgo
    for _ in range(26):
        x, y = azar.randrange(5, ANCHO - 5), azar.randrange(5, ALTO - 5)
        if libre(x, y):
            poner(x, y, azar.choice("RRr"))
    # la entrada desde los Prados (puerta _ en datos/mapas/bosque_cobrizo.puertas) y el cartel
    for x in range(60, 66):
        poner(x, ALTO - 1, "_")
    for y in range(ALTO - 5, ALTO - 1):
        for x in range(60, 66):
            if m[y][x] not in "#":
                poner(x, y, ".")
    poner(64, ALTO - 4, "L")
    poner(62, ALTO - 3, "S")
    for k, (zx, zy, rx, ry) in zonas.items():
        poner(zx, zy, k)
    textos = {"1": "10, 7, 5, 2", "2": "12, 8, 5, 3, tawi", "3": "11, 7, 5, 3", "4": "14, 10, 4, 0, , jefe:pembe"}
    return ["".join(f) for f in m], textos


# ---------------------------------------------------------------------------
# Crear el mapa inicial de la Ciénaga Quieta (al este de Cuna de Musgo)
# ---------------------------------------------------------------------------

def crear_cienaga():
    """La Ciénaga Quieta (100x68): charcas de agua quieta entre lenguas de tierra y pasarelas de tablas.
    Oeste: la entrada desde la aldea. Tres zonas corruptas (Juncia de piedra junto a la segunda) y,
    al este, el remanso de Konokono, la caracola de óxido (minijefe). Sauces llorones, árboles muertos,
    juncos y nenúfares. Bayas y juncos dulces para la cocina de Juncia. Dos islas con secretos que solo
    se alcanzarán más adelante (con el hielo de Sigilia) y un secreto tras un matorral."""
    ANCHO, ALTO = 100, 68
    azar = random.Random(77)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    zonas = {"1": (24, 18, 10, 7), "2": (48, 50, 11, 7), "3": (74, 16, 10, 7), "4": (80, 46, 13, 9)}

    def en_zona(x, y, margen=2):
        for (zx, zy, rx, ry) in zonas.values():
            if ((x - zx) / (rx + margen)) ** 2 + ((y - zy) / (ry + margen)) ** 2 <= 1.0:
                return True
        return False

    # el agua: manchas de ruido suave (charcas) que cubren más o menos la mitad del mapa
    fases = [(azar.uniform(0, 6), azar.uniform(0, 6)) for _ in range(4)]

    def ruido(x, y):
        v = 0.0
        for k, (a, b) in enumerate(fases):
            f = 0.07 * (k + 1) ** 1.1
            v += math.sin(x * f + a) * math.cos(y * f * 1.2 + b) / (k + 1)
        return v

    for y in range(ALTO):
        for x in range(ANCHO):
            if ruido(x, y) > 0.18 and not en_zona(x, y, 3):
                poner(x, y, "~")
    # caminos de tierra (y pasarelas donde cruzan el agua)
    def camino(puntos, ancho=2):
        for (a, b) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
            for i in range(pasos + 1):
                t = i / pasos
                x = a[0] + (b[0] - a[0]) * t + math.sin(t * 4 + a[0]) * 0.8
                y = a[1] + (b[1] - a[1]) * t
                for dx in range(ancho):
                    for dy in range(ancho):
                        xx, yy = int(x) + dx, int(y) + dy
                        if 0 <= xx < ANCHO and 0 <= yy < ALTO:
                            poner(xx, yy, "=" if m[yy][xx] in "~=" else "#")

    camino([(0, 33), (10, 32), (18, 26), (22, 22)])                 # entrada → zona 1
    camino([(10, 32), (24, 38), (36, 44), (42, 48)])               # → zona 2 (Juncia)
    camino([(30, 18), (44, 16), (56, 18), (66, 16)])               # zona 1 → zona 3
    camino([(56, 50), (66, 48), (70, 46)])                         # zona 2 → remanso de Konokono
    camino([(74, 22), (76, 30), (78, 38)])                         # zona 3 → remanso
    # islas con secretos (rodeadas de agua: más adelante se llegará con el hielo de Sigilia)
    islas = [(40, 30), (90, 62)]
    for (ix, iy) in islas:
        for dy in range(-4, 5):
            for dx in range(-5, 6):
                d = (dx / 5.0) ** 2 + (dy / 4.0) ** 2
                if d <= 1.0:
                    poner(ix + dx, iy + dy, "~" if d > 0.35 else ".")
        poner(ix, iy, "X")
        poner(ix - 1, iy - 1, "s")
    # un secreto tras un matorral, en el borde norte
    poner(52, 4, "X")
    for (dx, dy) in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]:
        poner(52 + dx, 4 + dy, "s" if dx else "x")
    poner(52, 5, "M")
    for k in range(6, 10):
        if m[k][52] in "~sx":
            poner(52, k, ".")
    reservados = [(4, 33, 4), (52, 4, 2)] + [(ix, iy, 6) for (ix, iy) in islas]

    def libre(x, y):
        if m[y][x] != "." or en_zona(x, y):
            return False
        return all((x - rx) ** 2 + (y - ry) ** 2 > rr * rr for (rx, ry, rr) in reservados)

    # bordes cerrados: sauces y árboles muertos (y agua)
    for y in range(ALTO):
        for x in range(ANCHO):
            borde = min(x, y, ANCHO - 1 - x, ALTO - 1 - y)
            if borde < 3 and m[y][x] == "." and (x + y) % 2 == 0 and not (x < 3 and 30 <= y <= 36):
                poner(x, y, "s" if azar.random() < 0.6 else "x")
    # árboles sueltos y en grupos por la tierra firme
    for _ in range(900):
        x, y = azar.randrange(3, ANCHO - 3), azar.randrange(3, ALTO - 3)
        cerca_camino = any(m[y + dy][x + dx] in "#=" for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        espeso = 0.5 + 0.5 * math.sin(x * 0.19 + 1.1) * math.sin(y * 0.23 + 0.4)
        if libre(x, y) and not cerca_camino and (x + y) % 2 == 0 and azar.random() < espeso:
            poner(x, y, "s" if azar.random() < 0.55 else "x")
    # juncos en las orillas y nenúfares en el agua
    for y in range(1, ALTO - 1):
        for x in range(1, ANCHO - 1):
            orilla = m[y][x] == "." and any(m[y + dy][x + dx] == "~" for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if orilla and azar.random() < 0.35 and not en_zona(x, y, 0):
                poner(x, y, ";")
            elif m[y][x] == "~" and azar.random() < 0.05 and all(m[y + dy][x + dx] == "~" for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                poner(x, y, "*")
    # ingredientes de Juncia: bayas en la tierra y juncos dulces en las orillas
    puestos = 0
    for _ in range(400):
        x, y = azar.randrange(4, ANCHO - 4), azar.randrange(4, ALTO - 4)
        if puestos < 6 and libre(x, y):
            poner(x, y, "$")
            puestos += 1
    puestos = 0
    for _ in range(600):
        x, y = azar.randrange(4, ANCHO - 4), azar.randrange(4, ALTO - 4)
        lejos_islas = all((x - rx) ** 2 + (y - ry) ** 2 > rr * rr for (rx, ry, rr) in reservados)
        if puestos < 5 and m[y][x] == ";" and not en_zona(x, y, 0) and lejos_islas:
            poner(x, y, ":")
            puestos += 1
    # rocas con musgo
    for _ in range(20):
        x, y = azar.randrange(4, ANCHO - 4), azar.randrange(4, ALTO - 4)
        if libre(x, y):
            poner(x, y, azar.choice("Rrr"))
    # la entrada desde la aldea (puerta «(» en datos/mapas/cienaga_quieta.puertas) y el cartel
    for y in range(31, 36):
        poner(0, y, "(")
        for x in range(1, 5):
            if m[y][x] not in "#=":
                poner(x, y, ".")
    poner(3, 30, "L")
    poner(3, 33, "S")
    for k, (zx, zy, rx, ry) in zonas.items():
        poner(zx, zy, k)
    textos = {"1": "10, 7, 5, 2", "2": "11, 7, 5, 3, juncia", "3": "10, 7, 5, 3", "4": "13, 9, 4, 0, , jefe:konokono"}
    return ["".join(f) for f in m], textos


def crear_campo():
    """El Campo Segado (96x64): los campos de cultivo abandonados del norte de Raíz.
    Sur: la entrada desde Cuna de Musgo. Un camino central con un molino roto en el cruce; al oeste y al este,
    dos zonas corruptas entre campos labrados (surcos, trigo seco, espantapájaros, vallas, pacas y máquinas
    oxidadas); un granero en ruinas; un secreto tras un matorral. Al norte, el gran campo donde espera
    la Cosechadora Oxidada (el jefe de Raíz): una arena enorme de surcos."""
    ANCHO, ALTO = 96, 64
    azar = random.Random(97)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    zonas = {"1": (20, 40, 10, 7), "2": (76, 40, 10, 7), "3": (48, 15, 17, 10)}

    def en_zona(x, y, margen=2):
        for (zx, zy, rx, ry) in zonas.values():
            if ((x - zx) / (rx + margen)) ** 2 + ((y - zy) / (ry + margen)) ** 2 <= 1.0:
                return True
        return False

    # campos labrados: rectángulos de surcos con trigo seco salteado
    campos = [(6, 47, 36, 58), (58, 47, 90, 58), (5, 22, 26, 32), (70, 22, 91, 32), (30, 27, 66, 31)]
    for (x0, y0, x1, y1) in campos:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                poner(x, y, "/")
                if y % 2 == 0 and azar.random() < 0.22 and not en_zona(x, y, 0):
                    poner(x, y, "y")
    # la arena de la Cosechadora: surcos en filas (las que recorre la máquina)
    zx, zy, rx, ry = zonas["3"]
    for y in range(ALTO):
        for x in range(ANCHO):
            if ((x - zx) / (rx + 1)) ** 2 + ((y - zy) / (ry + 1)) ** 2 <= 1.0:
                poner(x, y, "/")
    # caminos de tierra
    def camino(puntos, ancho=2):
        for (a, b) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
            for i in range(pasos + 1):
                t = i / pasos
                x = a[0] + (b[0] - a[0]) * t + math.sin(t * 3 + a[1]) * 0.5
                y = a[1] + (b[1] - a[1]) * t
                for dx in range(ancho):
                    for dy in range(ancho):
                        xx, yy = int(x) + dx, int(y) + dy
                        if 0 <= xx < ANCHO and 0 <= yy < ALTO and m[yy][xx] in "./y":
                            poner(xx, yy, "#")

    camino([(47, 63), (47, 52), (47, 40), (47, 30)])           # entrada → cruce → la gran puerta del norte
    camino([(47, 40), (34, 40), (30, 40)])                     # → zona 1
    camino([(48, 40), (62, 40), (66, 40)])                     # → zona 2
    camino([(20, 46), (24, 50), (30, 56)])                     # entre los campos del oeste
    # vallas alrededor de los campos (con huecos)
    for (x0, y0, x1, y1) in campos[:2]:
        for x in range(x0, x1 + 1):
            for y in (y0 - 1, y1 + 1):
                if m[y][x] in "./" and azar.random() < 0.8 and not en_zona(x, y, 1):
                    poner(x, y, "v")
    # espantapájaros en los campos
    for (x, y) in ((12, 50), (28, 55), (66, 52), (84, 49), (14, 26), (82, 28)):
        poner(x, y, "e")
    # el molino en el cruce, el granero y las máquinas viejas
    poner(53, 38, "]")
    poner(36, 52, "[")
    for (x, y) in ((61, 54), (10, 29), (88, 25), (40, 34)):
        poner(x, y, "&")
    # un secreto tras un matorral (en el bosque del noreste)
    poner(90, 8, "X")
    for (dx, dy) in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]:
        poner(90 + dx, 8 + dy, "T" if dx else "t")
    poner(90, 9, "M")
    reservados = [(90, 8, 3), (47, 60, 3)]

    def libre(x, y):
        if m[y][x] != "." or en_zona(x, y):
            return False
        return all((x - rx_) ** 2 + (y - ry_) ** 2 > rr * rr for (rx_, ry_, rr) in reservados)

    # bordes: árboles y árboles secos (con el hueco de la entrada)
    for y in range(ALTO):
        for x in range(ANCHO):
            b = min(x, y, ANCHO - 1 - x, ALTO - 1 - y)
            if b < 3 and m[y][x] in "./" and (x + y) % 2 == 0 and not (44 <= x <= 51 and y > 55):
                poner(x, y, azar.choice("TtTd"))
    # pacas, árboles secos y rocas sueltas
    for _ in range(500):
        x, y = azar.randrange(4, ANCHO - 4), azar.randrange(4, ALTO - 4)
        if libre(x, y) and azar.random() < 0.2:
            poner(x, y, azar.choice("+++ddrRt,"))
    # la entrada desde la aldea (puerta «_» en datos/mapas/campo_segado.puertas) y el cartel
    for x in range(45, 51):
        poner(x, ALTO - 1, "_")
        for y in range(ALTO - 3, ALTO - 1):
            if m[y][x] not in "#":
                poner(x, y, ".")
    poner(51, 59, "L")
    poner(47, 59, "S")
    for k, (zx_, zy_, rx_, ry_) in zonas.items():
        poner(zx_, zy_, k)
    textos = {"1": "10, 7, 5, 3", "2": "10, 7, 5, 3", "3": "17, 10, 4, 0, , jefe:cosechadora"}
    return ["".join(f) for f in m], textos


def crear_sendero():
    """El Sendero del Puente (140x46): el camino de los Prados del Eco a Cuna de Musgo.
    Oeste: prado con el campamento de Msafiri, el pangolín viajero. Centro: el Río Lento y el gran PUENTE DE PIEDRA
    de los antiguos (con pretiles); bajo el puente, un vado de piedras lleva a un islote con un ECO PERDIDO, y en la
    orilla crecen bayas. Este: una zona corrupta junto al camino; al norte, por un ramal, las ruinas de los
    constructores del puente con un secreto tras un matorral. Tres páginas del diario de Msafiri repartidas."""
    ANCHO, ALTO = 140, 46
    azar = random.Random(141)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    zonas = {"1": (98, 33, 10, 6)}

    def en_zona(x, y, margen=2):
        for (zx, zy, rx, ry) in zonas.values():
            if ((x - zx) / (rx + margen)) ** 2 + ((y - zy) / (ry + margen)) ** 2 <= 1.0:
                return True
        return False

    # el Río Lento, de norte a sur (ancho, con curvas)
    rio = {}
    for y in range(ALTO):
        cx = 64 + int(3 * math.sin(y * 0.11) + 1.5 * math.sin(y * 0.29 + 1))
        ancho = 5 + int(1.5 + 1.5 * math.sin(y * 0.17))
        rio[y] = (cx - ancho, cx + ancho)
        for x in range(cx - ancho, cx + ancho + 1):
            poner(x, y, "~")
    # el islote del eco, bajo el puente (al sur), y el vado de piedras que llega a él desde la orilla oeste
    isx, isy = 62, 33
    for y in range(isy - 1, isy + 2):
        for x in range(isx - 2, isx + 3):
            if abs(x - isx) + abs(y - isy) * 2 <= 3:
                poner(x, y, ".")
    for x in range(rio[isy][0], isx - 2):
        poner(x, isy, "'")
    # caminos de tierra
    def camino(puntos, ancho=2):
        for (a, b) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
            for i in range(pasos + 1):
                t = i / pasos
                x = a[0] + (b[0] - a[0]) * t
                y = a[1] + (b[1] - a[1]) * t + math.sin(t * 3 + a[0]) * 0.35
                for dx in range(ancho):
                    for dy in range(ancho):
                        xx, yy = int(x) + dx, int(y) + dy
                        if 0 <= xx < ANCHO and 0 <= yy < ALTO and m[yy][xx] in ".,":
                            poner(xx, yy, "#")

    camino([(0, 22), (14, 23), (28, 21), (44, 22), (54, 21), (60, 21)])          # prado → puente
    camino([(70, 21), (75, 21), (88, 23), (104, 21), (120, 23), (139, 22)])      # puente → Cuna de Musgo
    camino([(30, 21), (31, 16)], 1)                                    # → campamento de Msafiri
    camino([(108, 21), (112, 15), (114, 9)])                           # ramal → ruinas del norte
    camino([(48, 23), (52, 28), (54, 33)], 1)                          # bajada a la orilla, bajo el puente
    # el PUENTE DE PIEDRA: pretiles arriba y abajo, losas en medio
    px0, px1 = rio[21][0] - 3, max(rio[y][1] for y in range(19, 25)) + 3
    for x in range(px0, px1 + 1):
        poner(x, 20, "|")
        poner(x, 21, "-")
        poner(x, 22, "-")
        poner(x, 23, "|")
    # las bocas del puente quedan abiertas al camino, y el camino llega hasta ellas
    for y in (20, 23):
        poner(px0, y, "-"); poner(px1, y, "-")
    for y in (21, 22):
        for x in list(range(px0 - 5, px0)) + list(range(px1 + 1, px1 + 6)):
            if m[y][x] in ".,":
                poner(x, y, "#")
    # el campamento de Msafiri
    poner(30, 14, "{")
    poner(33, 16, "}")
    # ruinas de los constructores del puente (norte-este), con columnas y muros
    for (x, y) in ((108, 6), (118, 6), (110, 10), (120, 10), (113, 4)):
        poner(x, y, "C")
    for (x, y) in ((104, 8), (123, 8), (116, 11)):
        poner(x, y, "W")
    # secreto tras un matorral en las ruinas
    poner(126, 4, "X")
    for (dx, dy) in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (1, 1)]:
        poner(126 + dx, 4 + dy, "T" if dx else "t")
    poner(125, 5, "M"); poner(126, 5, "M")
    # el eco perdido, en el islote
    poner(isx, isy, "@")
    # las páginas del diario: en las ruinas, en la orilla bajo el puente y dentro de la zona corrupta
    for (x, y) in ((114, 5), (55, 36), (101, 31)):
        poner(x, y, "`")
    # bayas en la orilla oeste, bajo el puente
    for (x, y) in ((50, 34), (52, 38), (49, 39), (53, 31)):
        poner(x, y, "$")
    # mojones viejos junto al camino (columnas pequeñas)
    for (x, y) in ((12, 20), (40, 24), (84, 20), (130, 20)):
        poner(x, y, "C")
    reservados = [(30, 15, 4), (62, 33, 4), (114, 7, 6), (126, 4, 2), (52, 35, 4)]

    def libre(x, y):
        if m[y][x] not in ".," or en_zona(x, y):
            return False
        for (rx_, ry_, rr) in reservados:
            if (x - rx_) ** 2 + (y - ry_) ** 2 <= rr * rr:
                return False
        # que no estorbe junto al camino ni al agua
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= x + dx < ANCHO and 0 <= y + dy < ALTO and m[y + dy][x + dx] in "#~-|'":
                    return False
        return True

    # bosque espeso en los bordes de arriba y abajo (con claros), más ralo en el centro
    for y in range(ALTO):
        for x in range(ANCHO):
            borde = min(y, ALTO - 1 - y)
            if not libre(x, y):
                continue
            prob = 0.75 if borde < 3 else (0.35 if borde < 6 else 0.0)
            if azar.random() < prob:
                poner(x, y, azar.choice("TTtT"))
    # árboles sueltos, rocas y flores por el prado
    for _ in range(1400):
        x, y = azar.randrange(1, ANCHO - 1), azar.randrange(1, ALTO - 1)
        if libre(x, y):
            r = azar.random()
            if r < 0.05:
                poner(x, y, azar.choice("Tt"))
            elif r < 0.07:
                poner(x, y, azar.choice("rrR"))
            elif r < 0.22:
                poner(x, y, ",")
    # puertas: oeste a los Prados (<) y este a Cuna de Musgo (>)
    for y in range(20, 25):
        for x in range(0, 3):
            poner(x, y, "#" if x else "<")
        for x in range(ANCHO - 3, ANCHO):
            poner(x, y, "#" if x < ANCHO - 1 else ">")
    poner(6, 19, "L")
    poner(134, 19, "L")
    poner(52, 18, "L")
    poner(4, 22, "S")
    for k, (zx_, zy_, rx_, ry_) in zonas.items():
        poner(zx_, zy_, k)
    textos = {"1": "10, 6, 5, 3"}
    return ["".join(f) for f in m], textos


def crear_pasarelas():
    """Las Pasarelas (140x46): el camino de Cuna de Musgo a la Ciénaga Quieta. Un prado inundado de agua clara,
    con nenúfares y juncos, que se cruza por PASARELAS de tablas sobre pilotes entre islotes.
    Oeste: la orilla de la aldea. Islote del norte: el palafito de Korongo, la garza pescadora. Islote grande del
    centro: una zona corrupta (salen ranas de piedra y babosas). Sur: un islote con un secreto tras un matorral.
    Sureste: el islote del ECO PERDIDO, al que lleva una pasarela ROTA («"») que Korongo arregla al devolverle
    sus nasas. Este: la orilla de la ciénaga. Tres nasas de Korongo repartidas («`»)."""
    ANCHO, ALTO = 140, 46
    azar = random.Random(143)
    m = [["~" for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    zonas = {"1": (94, 28, 9, 5)}
    islas = [(6, 23, 9, 26, 0), (133, 23, 9, 26, 1),           # las orillas (este y oeste)
             (66, 13, 9, 5, 2), (94, 28, 14, 8, 3), (28, 37, 7, 4, 4), (114, 40, 6, 3.5, 5),
             (48, 30, 3, 2, 6), (80, 8, 3, 2, 7), (118, 10, 5, 3, 8), (14, 8, 4, 3, 9)]
    for (cx, cy, rx, ry, sem) in islas:
        for y in range(ALTO):
            for x in range(ANCHO):
                a = math.atan2(y - cy, x - cx)
                r = 1 + 0.18 * math.sin(a * 3 + sem) + 0.1 * math.sin(a * 7 + sem * 2)
                if ((x - cx) / (rx * r)) ** 2 + ((y - cy) / (ry * r)) ** 2 <= 1.0:
                    poner(x, y, ".")

    def tabla_h(x0, x1, y):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for yy in (y, y + 1):
                poner(x, yy, "=" if m[yy][x] in "~=" else "#")

    def tabla_v(x, y0, y1):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for xx in (x, x + 1):
                poner(xx, y, "=" if m[y][xx] in "~=" else "#")

    # la pasarela principal: orilla oeste → islote del norte → islote del centro → orilla este
    tabla_h(10, 38, 22)
    tabla_v(37, 13, 23)
    tabla_h(37, 60, 13)
    tabla_h(72, 84, 14)
    tabla_v(83, 14, 27)
    tabla_h(83, 88, 26)
    tabla_h(104, 128, 26)
    tabla_v(127, 22, 27)
    tabla_h(127, 134, 22)
    # ramal al sur (islote del secreto) y pasarela al islote del eco (con un tramo roto)
    tabla_v(30, 23, 33)
    tabla_v(100, 34, 39)
    tabla_h(100, 109, 38)
    for x in range(102, 106):
        for y in (38, 39):
            poner(x, y, '"')
    # el palafito de Korongo, al norte del islote del norte, y Korongo en su embarcadero
    poner(64, 7, "{")
    poner(68, 12, "}")
    # nasas: en el islote del norte (al este), en el islote del secreto y dentro de la zona
    for (x, y) in ((72, 11), (25, 38), (97, 30)):
        poner(x, y, "`")
    # el eco perdido, en su islote
    poner(115, 40, "@")
    # secreto tras un matorral, en el islote del sur
    poner(31, 39, "X")
    poner(30, 38, "M"); poner(31, 38, "M"); poner(32, 38, "M")
    for (x, y) in ((29, 39), (33, 39), (30, 40), (32, 40)):
        poner(x, y, "s")
    # árboles: sauces y árboles muertos en las islas y en las orillas
    def libre(x, y):
        if m[y][x] != ".":
            return False
        for (zx, zy, rx, ry) in zonas.values():
            if ((x - zx) / (rx + 2)) ** 2 + ((y - zy) / (ry + 2)) ** 2 <= 1.0:
                return False
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= x + dx < ANCHO and 0 <= y + dy < ALTO and m[y + dy][x + dx] in "#=\"{}@`X":
                    return False
        return True

    for _ in range(900):
        x, y = azar.randrange(0, ANCHO), azar.randrange(0, ALTO)
        if libre(x, y):
            r = azar.random()
            if r < 0.12:
                poner(x, y, azar.choice("sssxT"))
            elif r < 0.3:
                poner(x, y, ",")
            elif r < 0.34:
                poner(x, y, "r")
    # juncos (adorno) en las orillas del agua y juncos dulces para recoger; nenúfares sobre el agua
    for y in range(1, ALTO - 1):
        for x in range(1, ANCHO - 1):
            if m[y][x] == "." and any(m[y + dy][x + dx] == "~" for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                if azar.random() < 0.3:
                    poner(x, y, ";")
                elif azar.random() < 0.025:
                    poner(x, y, ":")
            elif m[y][x] == "~" and azar.random() < 0.05:
                if all(m[y + dy][x + dx] in "~*" for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    poner(x, y, "*")
    # puertas: oeste a Cuna de Musgo (<) y este a la Ciénaga Quieta (>)
    for y in range(20, 25):
        for x in range(0, 3):
            poner(x, y, "#" if x else "<")
        for x in range(ANCHO - 3, ANCHO):
            poner(x, y, "#" if x < ANCHO - 1 else ">")
    for x in range(3, 11):
        for y in (22, 23):
            poner(x, y, "#")
    for x in range(ANCHO - 6, ANCHO - 3):
        for y in (22, 23):
            poner(x, y, "#")
    poner(8, 19, "L")
    poner(131, 19, "L")
    poner(4, 22, "S")
    for k, (zx_, zy_, rx_, ry_) in zonas.items():
        poner(zx_, zy_, k)
    textos = {"1": "9, 5, 4, 3"}
    return ["".join(f) for f in m], textos


def crear_senda():
    """La Senda de los Surcos (64x100, de sur a norte): el camino de Cuna de Musgo (sur) al Campo Segado (norte).
    Huertas y bancales de los antiguos labradores, con vallas, pacas y setos. Una ACEQUIA cruza de lado a lado
    (con un puentecito) y sube por el este hasta un huerto rodeado de agua: allí, en medio, el cuarto ECO PERDIDO.
    El foso del huerto («"») se vacía cuando SUNGURA, la liebre guardasemillas, cierra la compuerta al devolverle
    sus tres mazorcas antiguas. Sungura vive en un hórreo («{»), al oeste, junto a la acequia. Una zona corrupta al
    este y un secreto tras un matorral en el seto del oeste. Abajo, verde de la aldea; arriba, el pasto seco del campo."""
    ANCHO, ALTO = 64, 100
    azar = random.Random(151)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    zonas = {"1": (46, 44, 9, 6)}

    def en_zona(x, y, margen=2):
        for (zx, zy, rx, ry) in zonas.values():
            if ((x - zx) / (rx + margen)) ** 2 + ((y - zy) / (ry + margen)) ** 2 <= 1.0:
                return True
        return False

    # bancales de surcos (huertas viejas) a los lados del camino
    bancales = [(4, 74, 20, 84), (40, 76, 58, 88), (6, 30, 22, 40), (4, 46, 18, 54), (24, 4, 38, 10)]
    for (x0, y0, x1, y1) in bancales:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                poner(x, y, "/")
                if y % 2 == 0 and azar.random() < 0.2:
                    poner(x, y, "y")
    # la acequia: de oeste a este, y luego sube por el este hasta el foso del huerto
    for x in range(ANCHO):
        cy = 64 + int(1.2 * math.sin(x * 0.2))
        for y in (cy, cy + 1):
            poner(x, y, "~")
    for y in range(28, 65):
        for x in (58, 59):
            poner(x, y, "~")
    # el huerto del eco (noreste), rodeado por su foso de dos casillas
    hx0, hy0, hx1, hy1 = 44, 10, 60, 26
    for y in range(hy0, hy1 + 1):
        for x in range(hx0, hx1 + 1):
            borde = min(x - hx0, hx1 - x, y - hy0, hy1 - y)
            if borde < 2:
                poner(x, y, '"')
            else:
                poner(x, y, "." if borde > 2 else ",")
    # la acequia del este llega al foso (y sigue siendo agua hasta la compuerta)
    for y in range(27, 30):
        for x in (58, 59):
            poner(x, y, "~")

    def camino(puntos, ancho=2):
        for (a, b) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
            for i in range(pasos + 1):
                t = i / pasos
                x = a[0] + (b[0] - a[0]) * t + math.sin(t * 3 + a[1]) * 0.35
                y = a[1] + (b[1] - a[1]) * t
                for dx in range(ancho):
                    for dy in range(ancho):
                        xx, yy = int(x) + dx, int(y) + dy
                        if 0 <= xx < ANCHO and 0 <= yy < ALTO and m[yy][xx] in ".,/y":
                            poner(xx, yy, "#")

    camino([(31, 99), (31, 90), (28, 80), (30, 70), (30, 66)])                    # aldea → acequia
    camino([(30, 62), (32, 54), (30, 44), (27, 34), (30, 24), (31, 14), (31, 0)])  # acequia → campo
    camino([(29, 72), (18, 70), (12, 68)], 1)                                      # → hórreo de Sungura
    camino([(31, 20), (38, 18), (42, 18)], 1)                                      # → el foso del huerto
    # el puentecito sobre la acequia
    for y in range(60, 68):
        for x in (30, 31):
            if m[y][x] == "~":
                poner(x, y, "=")
            elif m[y][x] in ".,/y":
                poner(x, y, "#")
    # el hórreo de Sungura y Sungura delante
    poner(10, 67, "{")
    poner(14, 70, "}")
    # dentro del huerto: el eco, un viejo espantapájaros (adorno: un mojón) y flores
    poner(52, 18, "@")
    poner(48, 14, "C")
    # vallas a lo largo de los bancales
    for (x0, y0, x1, y1) in bancales:
        for x in range(x0, x1 + 1, 1):
            if m[y0 - 1][x] in ".,":
                poner(x, y0 - 1, "v" if x % 4 else ".")
    # pacas de heno sueltas
    for (x, y) in ((22, 58), (36, 50), (12, 26), (40, 70), (20, 90), (50, 94)):
        poner(x, y, "+")
    # las tres mazorcas: en el bancal del oeste, junto a la acequia del sur-este y dentro de la zona
    for (x, y) in ((10, 50), (50, 70), (48, 46)):
        poner(x, y, "`")
    # secreto tras un matorral en el seto del oeste
    poner(3, 36, "X")
    for (dx, dy) in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0)]:
        poner(3 + dx, 36 + dy, "T" if dx else "t")
    poner(3, 37, "M"); poner(2, 37, "M"); poner(4, 37, "M")
    # bayas junto a la acequia
    for (x, y) in ((8, 62), (44, 62), (56, 36)):
        poner(x, y, "$")
    reservados = [(10, 67, 5), (14, 70, 2), (52, 18, 9), (3, 36, 2), (31, 96, 3)]

    def libre(x, y):
        if m[y][x] not in ".," or en_zona(x, y):
            return False
        for (rx_, ry_, rr) in reservados:
            if (x - rx_) ** 2 + (y - ry_) ** 2 <= rr * rr:
                return False
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= x + dx < ANCHO and 0 <= y + dy < ALTO and m[y + dy][x + dx] in "#~=\"@{}`$X/yv+":
                    return False
        return True

    # setos y árboles en los bordes (más secos hacia el norte) y algún frutal suelto
    for y in range(ALTO):
        for x in range(ANCHO):
            if not libre(x, y):
                continue
            borde = min(x, ANCHO - 1 - x)
            prob = 0.75 if borde < 2 else (0.25 if borde < 4 else 0.0)
            if azar.random() < prob:
                poner(x, y, azar.choice("Tt") if y > 40 or azar.random() < 0.5 else "d")
    for _ in range(1600):
        x, y = azar.randrange(1, ANCHO - 1), azar.randrange(1, ALTO - 1)
        if libre(x, y):
            r = azar.random()
            if r < 0.04:
                poner(x, y, azar.choice("Tt") if y > 40 else azar.choice("Ttd"))
            elif r < 0.06:
                poner(x, y, azar.choice("rrR"))
            elif r < 0.2 and y > 30:
                poner(x, y, ",")
    # puertas: sur a la aldea (_) y norte al Campo Segado (^)
    for x in range(29, 35):
        for y in range(0, 3):
            poner(x, y, "^" if y == 0 else "#")
        for y in range(ALTO - 3, ALTO):
            poner(x, y, "_" if y == ALTO - 1 else "#")
    poner(34, 4, "L")
    poner(26, 70, "L")
    poner(34, 94, "L")
    poner(31, 96, "S")
    for k, (zx_, zy_, rx_, ry_) in zonas.items():
        poner(zx_, zy_, k)
    textos = {"1": "9, 6, 4, 3"}
    return ["".join(f) for f in m], textos


def crear_camino():
    """El Camino Cobrizo (64x100, de norte a sur): el camino de los Prados del Eco (sur) al Bosque Cobrizo (norte).
    Abajo, prado con árboles verdes; según se sube, los árboles se vuelven cobrizos y el suelo se llena de hojas.
    Un arroyo cruza de lado a lado con un puentecito de tablas. Al este, junto al arroyo, la madriguera de FUKO,
    el topo minero (encargo: tres campanillas de cobre que se llevaron los topos de piedra). Al oeste, una zona
    corrupta. Al noreste, tras una peña («0») que no se puede cruzar, la vieja galería de la mina: su boca está
    tapada por un DERRUMBE («"») que Fuko despeja al devolverle las campanillas; dentro, el tercer ECO PERDIDO.
    Al noroeste, un secreto tras un matorral entre los árboles."""
    ANCHO, ALTO = 64, 100
    azar = random.Random(147)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    zonas = {"1": (15, 40, 9, 6)}

    def en_zona(x, y, margen=2):
        for (zx, zy, rx, ry) in zonas.values():
            if ((x - zx) / (rx + margen)) ** 2 + ((y - zy) / (ry + margen)) ** 2 <= 1.0:
                return True
        return False

    # el arroyo, de oeste a este (con curvas) y el puentecito de tablas por donde pasa el camino
    arroyo = {}
    for x in range(ANCHO):
        cy = 57 + int(2.5 * math.sin(x * 0.13) + 1.2 * math.sin(x * 0.31 + 2))
        arroyo[x] = cy
        for y in range(cy - 1, cy + 2):
            poner(x, y, "~")
    # la peña de la vieja mina (noreste): un muro de roca de tres casillas, con bultos, que encierra la hondonada
    for x in range(41, ANCHO):
        for y in (21, 22, 23, 24):
            poner(x, y, "0")
        for y in (1, 2, 3, 4):
            poner(x, y, "0")
    for y in range(1, 25):
        for x in (41, 42, 43, 44):
            poner(x, y, "0")
    for _ in range(40):
        # bultos hacia fuera (nunca hacia dentro de la hondonada)
        lado = azar.randrange(3)
        if lado == 0:
            x, y = azar.randrange(42, ANCHO), 25
        elif lado == 1:
            x, y = 40, azar.randrange(3, 25)
        else:
            x, y = azar.randrange(42, ANCHO), 0
        if not (49 <= x <= 58 and y == 25):
            poner(x, y, "0")
    # la boca de la galería: un derrumbe que tapa el paso por la peña
    for x in range(52, 56):
        for y in (21, 22, 23, 24):
            poner(x, y, '"')
    def camino(puntos, ancho=2):
        for (a, b) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
            for i in range(pasos + 1):
                t = i / pasos
                x = a[0] + (b[0] - a[0]) * t + math.sin(t * 3 + a[1]) * 0.35
                y = a[1] + (b[1] - a[1]) * t
                for dx in range(ancho):
                    for dy in range(ancho):
                        xx, yy = int(x) + dx, int(y) + dy
                        if 0 <= xx < ANCHO and 0 <= yy < ALTO and m[yy][xx] in ".,":
                            poner(xx, yy, "#")

    camino([(31, 99), (31, 90), (24, 81), (20, 72), (24, 64), (27, 60)])           # prado → arroyo
    camino([(27, 54), (33, 48), (38, 40), (36, 31), (31, 22), (30, 12), (31, 0)])  # arroyo → bosque
    camino([(25, 66), (36, 67), (44, 68)], 1)                                     # → madriguera de Fuko
    camino([(36, 33), (46, 30), (53, 28), (53, 25)], 2)                           # → la boca de la galería
    # el puentecito sobre el arroyo
    for y in range(arroyo[27] - 2, arroyo[27] + 3):
        for x in (27, 28):
            poner(x, y, "=" if m[y][x] in "~=" else "#")
    # la madriguera de Fuko (al este, junto al arroyo) y Fuko a la puerta
    poner(48, 66, "{")
    poner(45, 69, "}")
    # dentro de la hondonada: el eco y unas rocas con vetas de mineral
    poner(54, 12, "@")
    for (x, y) in ((48, 8), (60, 18), (59, 7)):
        poner(x, y, "Y")
    # las tres campanillas: junto al arroyo al oeste, entre los árboles del sur y dentro de la zona
    for (x, y) in ((6, 60), (52, 86), (18, 42)):
        poner(x, y, "`")
    # secreto tras un matorral, al noroeste entre los árboles
    poner(8, 14, "X")
    for (dx, dy) in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0)]:
        poner(8 + dx, 14 + dy, "j" if dx else "J")
    poner(8, 15, "M"); poner(7, 15, "M"); poner(9, 15, "M")
    # bayas junto al arroyo
    for (x, y) in ((14, 61), (40, 54), (58, 61)):
        poner(x, y, "$")
    reservados = [(48, 66, 5), (45, 69, 2), (54, 12, 3), (8, 14, 2), (6, 60, 2), (52, 86, 2), (31, 96, 3)]

    def libre(x, y):
        if m[y][x] not in ".," or en_zona(x, y):
            return False
        for (rx_, ry_, rr) in reservados:
            if (x - rx_) ** 2 + (y - ry_) ** 2 <= rr * rr:
                return False
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= x + dx < ANCHO and 0 <= y + dy < ALTO and m[y + dy][x + dx] in "#~=0\"@{}`$X":
                    return False
        return True

    def arbol(y):
        # abajo, árboles de los prados; arriba, cobrizos; en medio, mezclados
        cobre = min(1.0, max(0.0, (66 - y) / 40))
        return azar.choice("JjIj") if azar.random() < cobre else azar.choice("TTt")

    # árboles espesos en los bordes de los lados (con claros) y más ralos dentro
    for y in range(ALTO):
        for x in range(ANCHO):
            if not libre(x, y):
                continue
            borde = min(x, ANCHO - 1 - x)
            prob = 0.7 if borde < 3 else (0.3 if borde < 6 else 0.0)
            if 4 < x < 43 and y < 22:
                prob = max(prob, 0.18)          # el bosque ya empieza arriba
            if azar.random() < prob:
                poner(x, y, arbol(y))
    for _ in range(2200):
        x, y = azar.randrange(1, ANCHO - 1), azar.randrange(1, ALTO - 1)
        if libre(x, y):
            r = azar.random()
            if r < 0.06:
                poner(x, y, arbol(y))
            elif r < 0.08:
                poner(x, y, azar.choice("rrR"))
            elif r < 0.1 and y < 50:
                poner(x, y, "g")
            elif r < 0.22 and y > 40:
                poner(x, y, ",")
    # puertas: sur a los Prados (_) y norte al Bosque Cobrizo (^)
    for x in range(29, 35):
        for y in range(0, 3):
            poner(x, y, "^" if y == 0 else "#")
        for y in range(ALTO - 3, ALTO):
            poner(x, y, "_" if y == ALTO - 1 else "#")
    poner(34, 94, "L")
    poner(26, 4, "L")
    poner(40, 64, "L")
    poner(31, 96, "S")
    for k, (zx_, zy_, rx_, ry_) in zonas.items():
        poner(zx_, zy_, k)
    textos = {"1": "9, 6, 4, 3"}
    return ["".join(f) for f in m], textos


def crear_canada():
    """La Cañada del Eco (140x46, de este a oeste): el camino del Bosque Cobrizo (este) al Lago Espejo (oeste).
    Una garganta entre dos paredes de peña («0») que se estrecha en el centro; por el fondo baja un arroyo hacia el
    lago, con un vado de piedras y un puentecito. Al este, árboles cobrizos del bosque; al oeste, hierba y flores
    que anuncian el lago. Al norte, el aprisco de MBUZI, la cabra montés pastora (encargo: tres cencerros que el
    eco esparció por la cañada). Muy arriba, en una CORNISA de la pared norte, el quinto ECO PERDIDO: solo se sube
    por la ESCALA DE CUERDA («"» en esta cañada) que Mbuzi descuelga al devolverle los cencerros. Al sur, en un
    ensanche, una zona corrupta. Al noroeste, un secreto tras un matorral."""
    ANCHO, ALTO = 140, 46
    azar = random.Random(153)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    zonas = {"1": (58, 33, 9, 5)}

    def en_zona(x, y, margen=2):
        for (zx, zy, rx, ry) in zonas.values():
            if ((x - zx) / (rx + margen)) ** 2 + ((y - zy) / (ry + margen)) ** 2 <= 1.0:
                return True
        return False

    # las dos paredes de peña: más cerradas en el centro (la garganta) y abiertas en los extremos
    norte, sur = {}, {}
    for x in range(ANCHO):
        cierre = math.exp(-((x - 84) / 22.0) ** 2)                  # 1 en la garganta, 0 lejos
        norte[x] = int(8 + 9 * cierre + 1.5 * math.sin(x * 0.21) + math.sin(x * 0.53 + 1))
        sur[x] = int(38 - 9 * cierre + 1.5 * math.sin(x * 0.17 + 2) + math.sin(x * 0.47))
    # bajo la cornisa la pared es más alta: entre la repisa y el fondo hay roca (solo se sube por la escala)
    for x in range(88, 121):
        norte[x] = max(norte[x], int(12.5 - max(0, abs(x - 104) - 7) * 0.7))
    # el ensanche del sur, donde está la zona corrupta
    for x in range(44, 74):
        sur[x] = max(sur[x], int(40.5 - 2 * math.sin((x - 44) / 30 * math.pi) + 1.4 * math.sin(x * 0.45)
                                 + math.sin(x * 0.9 + 1)))
    for x in range(ANCHO):
        for y in range(0, norte[x] + 1):
            poner(x, y, "0")
        for y in range(sur[x], ALTO):
            poner(x, y, "0")
    # la cornisa del eco: una repisa en lo alto de la pared norte, encerrada por la peña
    for x in range(98, 111):
        for y in range(3, 10):
            if ((x - 104) / 6.5) ** 2 + ((y - 6.5) / 2.6) ** 2 <= 1.0:
                poner(x, y, ".")
    # la escala de cuerda: baja de la cornisa al fondo de la cañada (cerrada hasta que Mbuzi la descuelga)
    for y in range(9, norte[104] + 1):
        for x in (104, 105):
            poner(x, y, '"')
    # el aprisco de Mbuzi: un rellano al norte, al oeste de la garganta
    for x in range(30, 50):
        for y in range(2, norte[x] + 1):
            if ((x - 40) / 10.0) ** 2 + ((y - 8) / 6.0) ** 2 <= 1.0:
                poner(x, y, ".")
    # el rincón del secreto, al noroeste
    for x in range(12, 22):
        for y in range(3, norte[x] + 1):
            if ((x - 17) / 5.0) ** 2 + ((y - 6) / 3.5) ** 2 <= 1.0:
                poner(x, y, ".")

    def camino(puntos, ancho=2):
        for (a, b) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
            for i in range(pasos + 1):
                t = i / pasos
                x = a[0] + (b[0] - a[0]) * t
                y = a[1] + (b[1] - a[1]) * t + math.sin(t * 3 + a[0]) * 0.35
                for dx in range(ancho):
                    for dy in range(ancho):
                        xx, yy = int(x) + dx, int(y) + dy
                        if 0 <= xx < ANCHO and 0 <= yy < ALTO and m[yy][xx] in ".,":
                            poner(xx, yy, "#")

    camino([(139, 23), (124, 22), (110, 20), (96, 21), (84, 22), (72, 21), (60, 20), (46, 21), (30, 23), (14, 25), (0, 25)])
    camino([(42, 21), (41, 14)], 1)                                   # → el aprisco de Mbuzi
    camino([(104, 20), (104, norte[104] + 1)], 1)                     # → el pie de la escala
    camino([(64, 21), (60, 28)], 1)                                   # → el ensanche de la zona

    # el arroyo baja hacia el lago (oeste): al este va por el norte del camino, lo cruza bajo un puentecito de
    # tablas, recorre la garganta por el sur y vuelve a cruzarlo por un vado de piedras antes de llegar al lago
    arroyo = {}
    # (en los dos cruces con el camino baja recto, para que el puente y el vado crucen de lado a lado)
    puntos = [(139, 15), (126, 16), (118, 16), (115, 18), (115, 24), (111, 26), (96, 27), (84, 26), (70, 27), (56, 26),
              (44, 26), (38, 26), (34, 25), (34, 19), (28, 18), (14, 18), (0, 19)]
    for (a, b) in zip(puntos, puntos[1:]):
        pasos = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 2) + 1
        for i in range(pasos + 1):
            t = i / pasos
            x = int(a[0] + (b[0] - a[0]) * t)
            y = int(a[1] + (b[1] - a[1]) * t + math.sin(x * 0.4) * 0.6)
            arroyo[x] = min(arroyo.get(x, 99), y)
            for dy in range(3 if x < 30 else 2):
                for dx in (0, 1):
                    xx, yy = x + dx, y + dy
                    if not (0 <= xx < ANCHO and 0 <= yy < ALTO):
                        continue
                    if m[yy][xx] in ".,":
                        poner(xx, yy, "~")
                    elif m[yy][xx] == "#":
                        # donde cruza el camino: al este, un puentecito de tablas; al oeste, un vado de piedras
                        poner(xx, yy, "=" if xx > 70 else "'")
    # el puentecito: una tabla más a cada lado, sobre la orilla (así se apoya en tierra)
    for y in range(ALTO):
        fila = [x for x in range(ANCHO) if m[y][x] == "="]
        if fila:
            for x in (min(fila) - 1, max(fila) + 1):
                if m[y][x] == "#":
                    poner(x, y, "=")
    # rocas caídas de las paredes («ñ»): al pie de la peña, sobre todo en la garganta
    caidas = 0
    for _ in range(400):
        x = azar.randrange(4, ANCHO - 4)
        for y in (norte[x] + 1, sur[x] - 1):
            if caidas >= 22 or not (0 < y < ALTO - 1) or m[y][x] != ".":
                continue
            if any(m[y + dy][x + dx] in "#~='\"{}`@" for dx in (-2, -1, 0, 1, 2) for dy in (-1, 0, 1)):
                continue
            if azar.random() < 0.5 + 0.4 * math.exp(-((x - 84) / 22.0) ** 2):
                poner(x, y, "ñ")
                caidas += 1
    # troncos secos caídos («ç»), hacia el bosque
    for (x, y) in ((124, 29), (100, 30), (131, 13)):
        if m[y][x] == ".":
            poner(x, y, "ç")
    # Mbuzi: su aprisco («{») y ella a la puerta
    poner(40, 7, "{")
    poner(43, 11, "}")
    # el eco, en la cornisa
    poner(104, 5, "@")
    # los tres cencerros: en la zona, junto al vado del oeste y en un saliente del este
    for (x, y) in ((61, 34), (12, arroyo[12] - 2), (122, sur[122] - 2)):
        poner(x, y, "`")
    # el secreto, tras un matorral
    poner(17, 5, "X")
    poner(16, 7, "M"); poner(17, 7, "M"); poner(18, 7, "M")
    # bayas junto al arroyo
    for (x, y) in ((26, arroyo[26] + 3), (88, arroyo[88] - 1), (118, arroyo[118] + 3)):
        if m[y][x] == ".":
            poner(x, y, "$")
    reservados = [(40, 7, 4), (43, 11, 2), (104, 5, 3), (17, 5, 2), (132, 22, 3), (4, 25, 3)]

    def libre(x, y):
        if m[y][x] not in ".," or en_zona(x, y):
            return False
        for (rx_, ry_, rr) in reservados:
            if (x - rx_) ** 2 + (y - ry_) ** 2 <= rr * rr:
                return False
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= x + dx < ANCHO and 0 <= y + dy < ALTO and m[y + dy][x + dx] in "#~='\"@{}`$X":
                    return False
        return True

    def arbol(x):
        # al este, árboles cobrizos del bosque; al oeste, árboles verdes del lago
        cobre = min(1.0, max(0.0, (x - 90) / 30))
        return azar.choice("Jj") if azar.random() < cobre else azar.choice("TTt")

    for _ in range(2600):
        x, y = azar.randrange(1, ANCHO - 1), azar.randrange(1, ALTO - 1)
        if libre(x, y):
            r = azar.random()
            junto_pena = any(m[y + d][x] == "0" for d in (-2, -1, 1, 2) if 0 <= y + d < ALTO)
            if r < (0.12 if junto_pena else 0.03):
                poner(x, y, azar.choice("rrR"))
            elif r < 0.17 and (x > 110 or x < 30):
                poner(x, y, arbol(x))
            elif r < 0.2 and x > 100:
                poner(x, y, "g")
            elif r < 0.32 and x < 50:
                poner(x, y, ",")
    # puertas: este al Bosque Cobrizo (>) y oeste al Lago Espejo (<)
    for y in range(21, 27):
        if m[y][ANCHO - 1] in ".,#":
            for x in range(ANCHO - 3, ANCHO):
                poner(x, y, ">" if x == ANCHO - 1 else "#")
    for y in range(23, 29):
        for x in range(0, 3):
            poner(x, y, "<" if x == 0 else "#")
    poner(132, 19, "L")
    poner(6, 22, "L")
    poner(45, 14, "L")
    poner(134, 23, "S")
    for k, (zx_, zy_, rx_, ry_) in zonas.items():
        poner(zx_, zy_, k)
    textos = {"1": "9, 5, 4, 3"}
    return ["".join(f) for f in m], textos


def crear_lago():
    """El Lago Espejo (96x64): un lugar al oeste de la Cañada del Eco (puerta al este). Un lago grande y quieto con
    una ISLA en el centro, donde aparecerá KIMYA, el Silencio. Lo que solo existe en el reflejo («\\»: un puente de
    luz sobre el agua) se vuelve real cuando Maisha espera sin moverse junto al agua y el lago se calma. Hay dos: el
    largo, del sur a la isla, y uno corto, del oeste a un islote con un secreto. En la orilla sur, la ARENA del
    minijefe de Giza que enturbia el agua (no deja que se calme hasta vencerlo); al noreste, una zona corrupta.
    Sauces y juncos en la orilla, flores y bayas."""
    ANCHO, ALTO = 96, 64
    azar = random.Random(171)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    zonas = {"1": (26, 56, 13, 6), "2": (76, 9, 8, 5)}

    def en_zona(x, y, margen=2):
        for (zx, zy, rx, ry) in zonas.values():
            if ((x - zx) / (rx + margen)) ** 2 + ((y - zy) / (ry + margen)) ** 2 <= 1.0:
                return True
        return False

    # el lago, con la orilla irregular
    LX, LY, RX, RY = 46, 28, 31, 19
    for y in range(ALTO):
        for x in range(ANCHO):
            a = math.atan2(y - LY, x - LX)
            r = 1.0 + 0.06 * math.sin(a * 3 + 0.5) + 0.04 * math.sin(a * 7 + 2)
            if ((x - LX) / RX) ** 2 + ((y - LY) / RY) ** 2 <= r * r:
                poner(x, y, "~")
    # la isla del centro y el islote del noroeste
    for (ix, iy, irx, iry) in ((46, 26, 6.5, 4.5), (35, 14, 3.2, 2.4)):
        for y in range(ALTO):
            for x in range(ANCHO):
                if ((x - ix) / irx) ** 2 + ((y - iy) / iry) ** 2 <= 1.0:
                    poner(x, y, ",")
    # los puentes del reflejo: del sur a la isla y del oeste al islote
    for y in range(31, 48):
        for x in (45, 46):
            if m[y][x] == "~":
                poner(x, y, "\\")
    for x in range(18, 33):
        for y in (14, 15):
            if m[y][x] == "~":
                poner(x, y, "\\")

    def camino(puntos, ancho=2):
        for (a_, b_) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b_[0] - a_[0]), abs(b_[1] - a_[1])) * 2) + 1
            for i in range(pasos + 1):
                t_ = i / pasos
                x = a_[0] + (b_[0] - a_[0]) * t_
                y = a_[1] + (b_[1] - a_[1]) * t_ + math.sin(t_ * 3 + a_[0]) * 0.35
                for dx in range(ancho):
                    for dy in range(ancho):
                        xx, yy = int(x) + dx, int(y) + dy
                        if 0 <= xx < ANCHO and 0 <= yy < ALTO and m[yy][xx] in ".,":
                            poner(xx, yy, "#")

    # el camino: entra por el este y bordea la orilla sur hasta la arena; un ramal sube al pie del puente
    camino([(95, 31), (84, 34), (78, 44), (66, 50), (52, 50), (40, 52), (32, 53)])
    camino([(46, 50), (45, 48)], 2)
    camino([(9, 20), (9, 30), (14, 44), (24, 50)], 1)                  # por el oeste, a la orilla del islote
    camino([(9, 20), (16, 15), (20, 15)], 1)
    # la isla de Kimya: un círculo de piedras talladas («ø») y un sauce viejo en la orilla de la isla
    for (dx, dy) in ((-3, -1), (3, -1), (-2, 2), (2, 2), (0, -3)):
        poner(46 + dx, 26 + dy, "ø")
    poner(51, 25, "s")
    # el embarcadero viejo de madera, junto al pie del puente del reflejo (de la orilla sur hacia dentro)
    for y in range(42, 48):
        for x in (51, 52):
            if m[y][x] == "~":
                poner(x, y, "=")
    # la barca varada en la playa del oeste y el altar de Kimya en la orilla del este, junto a la entrada
    poner(14, 38, "þ")
    poner(79, 26, "ð")
    # nenúfares («*») cerca de las orillas, en las calas tranquilas
    for _ in range(300):
        x, y = azar.randrange(ANCHO), azar.randrange(ALTO)
        if m[y][x] != "~":
            continue
        cerca = any(m[y + dy][x + dx] not in "~*\\=" for dx in (-3, 0, 3) for dy in (-3, 0, 3)
                    if 0 <= x + dx < ANCHO and 0 <= y + dy < ALTO)
        if cerca and azar.random() < 0.35:
            poner(x, y, "*")
    # el secreto, en el islote
    poner(35, 13, "X")
    # sauces, juncos y bayas en la orilla
    for (x, y) in ((84, 30), (70, 46), (16, 40), (12, 26), (60, 7), (30, 9)):
        poner(x, y, "$")
    reservados = [(95, 31, 4), (46, 26, 5), (35, 14, 3), (26, 56, 13), (76, 9, 10), (14, 38, 3), (79, 26, 3), (53, 49, 2)]

    def libre(x, y):
        if m[y][x] not in ".," or en_zona(x, y):
            return False
        for (rx_, ry_, rr) in reservados:
            if (x - rx_) ** 2 + (y - ry_) ** 2 <= rr * rr:
                return False
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= x + dx < ANCHO and 0 <= y + dy < ALTO and m[y + dy][x + dx] in "#~\\X$":
                    return False
        return True

    def orilla(x, y):
        return any(0 <= x + dx < ANCHO and 0 <= y + dy < ALTO and m[y + dy][x + dx] == "~"
                   for dx in (-2, 0, 2) for dy in (-2, 0, 2))

    for y in range(ALTO):
        for x in range(ANCHO):
            if not libre(x, y):
                continue
            borde = min(x, ANCHO - 1 - x, y, ALTO - 1 - y)
            # el bosque del borde, de ancho irregular (sin filas)
            grueso = 2.5 + 2.2 * math.sin(x * 0.31 + y * 0.17) + 1.3 * math.sin(x * 0.07 - y * 0.23 + 1)
            r = azar.random()
            if borde < grueso and r < 0.7:
                poner(x, y, azar.choice("TTtts"))
            elif orilla(x, y) and r < 0.4:
                poner(x, y, "s" if r < 0.05 else ";")
            elif r < 0.04:
                poner(x, y, azar.choice("Ttrs"))
            elif r < 0.16 and not orilla(x, y):
                poner(x, y, ",")
    # puerta al este, a la Cañada del Eco
    for y in range(29, 35):
        for x in range(ANCHO - 3, ANCHO):
            poner(x, y, ">" if x == ANCHO - 1 else "#")
    poner(88, 28, "L")
    poner(48, 50, "L")
    poner(53, 49, "}")                       # Mdiria, el martín pescador (solo cuando ya se le ha rescatado)
    poner(91, 32, "S")
    for k, (zx_, zy_, rx_, ry_) in zonas.items():
        poner(zx_, zy_, k)
    textos = {"1": "13, 6, 4, 0, mdiria, jefe:kambare", "2": "8, 5, 4, 3"}
    return ["".join(f) for f in m], textos


def crear_orilla():
    """La Orilla de Juncos (64x100, de sur a norte): el camino de la Ciénaga Quieta (sur) al Embarcadero Junco
    (norte). Por el este baja el RÍO ANCHO, con camas de juncos en las orillas y un banco de arena en medio, donde
    está el sexto ECO PERDIDO. Por el oeste, el camino entre juncos y sauces. A media altura, la CASA DE BARCAS de
    KASIA, la nutria barquera (encargo: tres remos que se llevó la corriente); al devolvérselos arregla su BALSA («"» en
    esta orilla: el embarcadero roto) y lleva a Maisha al banco de arena. Una zona corrupta en una playa del sur
    y un secreto entre los juncos del noroeste."""
    ANCHO, ALTO = 64, 100
    azar = random.Random(191)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    zonas = {"1": (22, 76, 9, 6)}

    def en_zona(x, y, margen=2):
        for (zx, zy, rx, ry) in zonas.values():
            if ((x - zx) / (rx + margen)) ** 2 + ((y - zy) / (ry + margen)) ** 2 <= 1.0:
                return True
        return False

    # el río ancho, por el este (con curvas), y el banco de arena en medio
    rio = {}
    for y in range(ALTO):
        cx = 47 + int(3 * math.sin(y * 0.07) + 1.5 * math.sin(y * 0.19 + 1))
        ancho = 9 + int(2 * math.sin(y * 0.11 + 2))
        rio[y] = (cx - ancho, cx + ancho)
        for x in range(cx - ancho, min(ANCHO, cx + ancho + 1)):
            poner(x, y, "~")
    for y in range(36, 47):
        for x in range(ANCHO):
            if ((x - 50) / 4.5) ** 2 + ((y - 41) / 4.0) ** 2 <= 1.0:
                poner(x, y, ".")
    # juncos en las dos orillas del río (adorno, se recogen... no: solo adorno)
    for y in range(ALTO):
        x0, x1 = rio[y]
        for x in (x0 - 1, x0 - 2, x1 + 1):
            if 0 <= x < ANCHO and m[y][x] == "." and azar.random() < 0.55:
                poner(x, y, ";")

    def camino(puntos, ancho=2):
        for (a_, b_) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b_[0] - a_[0]), abs(b_[1] - a_[1])) * 2) + 1
            for i in range(pasos + 1):
                t_ = i / pasos
                x = a_[0] + (b_[0] - a_[0]) * t_ + math.sin(t_ * 3 + a_[1]) * 0.35
                y = a_[1] + (b_[1] - a_[1]) * t_
                for dx in range(ancho):
                    for dy in range(ancho):
                        xx, yy = int(x) + dx, int(y) + dy
                        if 0 <= xx < ANCHO and 0 <= yy < ALTO and m[yy][xx] in ".,;":
                            poner(xx, yy, "#")

    camino([(20, 99), (21, 88), (16, 72), (18, 58), (24, 46), (22, 32), (17, 18), (20, 0)])
    camino([(19, 44), (27, 43), (34, 43), (rio[41][0] - 1, 42)], 1)   # → la casa de barcas y el embarcadero de la balsa
    # el embarcadero roto: la balsa que cruza al banco de arena (cerrado hasta que la nutria la arregla)
    for x in range(rio[41][0], 46):
        for y in (41, 42):
            if m[y][x] == "~":
                poner(x, y, '"')
    # la casa de barcas de la nutria y la nutria a la puerta
    poner(rio[37][0] - 6, 37, "{")
    poner(rio[41][0] - 4, 41, "}")
    # el eco, en el banco de arena
    poner(50, 40, "@")
    # los tres remos: en la playa de la zona, entre los juncos del norte y río abajo, en la orilla
    for (x, y) in ((24, 78), (rio[14][0] - 2, 14), (rio[90][0] - 2, 90)):
        poner(x, y, "`")
    # el secreto, entre los juncos del noroeste, tras un matorral
    poner(6, 12, "X")
    poner(5, 13, "M"); poner(6, 13, "M"); poner(7, 13, "M")
    # bayas y junco dulce en la orilla
    for (x, y) in ((12, 60), (rio[26][0] - 3, 26), (8, 88)):
        poner(x, y, "$")
    reservados = [(rio[37][0] - 6, 37, 6), (rio[41][0] - 4, 41, 2), (6, 12, 2), (20, 96, 3), (20, 3, 3)]

    def libre(x, y):
        if m[y][x] not in ".," or en_zona(x, y):
            return False
        for (rx_, ry_, rr) in reservados:
            if (x - rx_) ** 2 + (y - ry_) ** 2 <= rr * rr:
                return False
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= x + dx < ANCHO and 0 <= y + dy < ALTO and m[y + dy][x + dx] in "#~\"@{}`$X":
                    return False
        return True

    for y in range(ALTO):
        for x in range(ANCHO):
            if not libre(x, y):
                continue
            borde = x
            r = azar.random()
            if borde < 3 and r < 0.75:
                poner(x, y, azar.choice("sst"))
            elif r < 0.05:
                poner(x, y, azar.choice("ssTr"))
            elif r < 0.12:
                poner(x, y, ";")
            elif r < 0.2:
                poner(x, y, ",")
    # puertas: sur a la Ciénaga Quieta (_) y norte al Embarcadero Junco (^)
    for x in range(18, 24):
        for y in range(0, 3):
            poner(x, y, "^" if y == 0 else "#")
        for y in range(ALTO - 3, ALTO):
            poner(x, y, "_" if y == ALTO - 1 else "#")
    poner(24, 94, "L")
    poner(25, 45, "L")
    poner(23, 5, "L")
    poner(21, 96, "S")
    for k, (zx_, zy_, rx_, ry_) in zonas.items():
        poner(zx_, zy_, k)
    textos = {"1": "9, 6, 4, 3"}
    return ["".join(f) for f in m], textos


def crear_embarcadero():
    """El Embarcadero Junco (96x72): el puerto del río de Raíz, al norte de la Orilla de Juncos (puerta al sur). El río
    ancho baja por el este; en la orilla del oeste, el PUEBLO DE BARQUEROS: casas de juncos sobre pilotes («æ»),
    pasarelas de madera, un almacén y una grúa rota («å»). Arriba, el MUELLE DEL NORTE con el TRANSBORDADOR varado
    («ß»), y junto a él BATA, el pato barquero, de piedra (zona 2). Abajo, la DÁRSENA: una balsa de agua cerrada por
    muelles, con una gran plataforma de madera en medio, donde acecha el jefe del lugar (zona 1). Al despertar a Bata
    y arreglar el transbordador, el muelle del norte lleva río arriba: LA TRAVESÍA."""
    ANCHO, ALTO = 96, 72
    azar = random.Random(211)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    zonas = {"1": (44, 56, 9, 6), "2": (12, 12, 7, 5), "3": (14, 36, 8, 6)}

    def en_zona(x, y, margen=2):
        for (zx, zy, rx, ry) in zonas.values():
            if ((x - zx) / (rx + margen)) ** 2 + ((y - zy) / (ry + margen)) ** 2 <= 1.0:
                return True
        return False

    # el río ancho, por el este, y la dársena: un entrante de agua cerrado por muelles, abajo
    rio = {}
    for y in range(ALTO):
        cx = 66 + int(3 * math.sin(y * 0.06 + 1) + 1.5 * math.sin(y * 0.17))
        ancho = 11 + int(2 * math.sin(y * 0.09))
        rio[y] = (cx - ancho, cx + ancho)
        for x in range(cx - ancho, min(ANCHO, cx + ancho + 1)):
            poner(x, y, "~")
    for y in range(40, ALTO):
        for x in range(26, rio[y][0] + 1):
            ang = math.atan2(y - 56, x - 44)
            r = 1.0 + 0.08 * math.sin(ang * 3 + 1.2) + 0.05 * math.sin(ang * 7 + 0.4)
            if ((x - 44) / 14) ** 2 + ((y - 56) / 8.5) ** 2 <= r * r:
                poner(x, y, "~")
    # el canal que une la dársena con el río, por el este
    for y in range(52, 61):
        for x in range(54, rio[y][0] + 1):
            poner(x, y, "~")
    # la plataforma de madera en medio de la dársena (la arena del jefe), con una pasarela desde el oeste
    for y in range(52, 61):
        for x in range(37, 52):
            poner(x, y, "=")
    # los cuatro postes de amarre de la plataforma (Mamba se clava en ellos)
    for (x, y) in ((40, 54), (48, 54), (40, 58), (48, 58)):
        poner(x, y, "ł")
    for x in range(26, 37):
        for y in (56, 57):
            if m[y][x] == "~":
                poner(x, y, "=")
    # los muelles que cierran la dársena por el norte y por el sur (no se pisan: pilotes y tablas rotas)
    # el muelle del norte, largo, con el transbordador varado al final
    for x in range(rio[12][0], rio[12][0] + 9):
        for y in (12, 13):
            poner(x, y, "=")
    poner(rio[12][0] + 11, 12, "ß")
    # el muelle del medio, con dos casas de juncos sobre pilotes
    for x in range(rio[30][0], rio[30][0] + 6):
        for y in (30, 31):
            poner(x, y, "=")

    def camino(puntos, ancho=2):
        for (a_, b_) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b_[0] - a_[0]), abs(b_[1] - a_[1])) * 2) + 1
            for i in range(pasos + 1):
                t_ = i / pasos
                x = a_[0] + (b_[0] - a_[0]) * t_ + math.sin(t_ * 3 + a_[1]) * 0.35
                y = a_[1] + (b_[1] - a_[1]) * t_
                for dx in range(ancho):
                    for dy in range(ancho):
                        xx, yy = int(x) + dx, int(y) + dy
                        if 0 <= xx < ANCHO and 0 <= yy < ALTO and m[yy][xx] in ".,;":
                            poner(xx, yy, "#")

    # el camino: entra por el sur, sube por el pueblo hasta el muelle del norte; ramales a la dársena y al prado
    camino([(22, 71), (22, 62), (24, 54), (32, 44), (40, 36), (44, 24), (42, 16), (36, 6), (33, 0)])
    camino([(22, 56), (26, 56)], 2)
    camino([(40, 36), (26, 36), (14, 36)], 1)
    camino([(42, 30), (rio[30][0] - 1, 30)], 2)
    camino([(43, 16), (rio[12][0] - 1, 12)], 2)
    # el pueblo de barqueros: casas de juncos en la orilla y sobre el agua, el almacén y la grúa rota
    # (las casas, con los pilotes en el agua: en la primera casilla de río de la orilla)
    for (x, y) in ((rio[19][0] + 1, 19), (rio[25][0] + 1, 25), (rio[37][0] + 1, 37), (rio[43][0] + 1, 43),
                   (rio[30][0] + 8, 29), (rio[34][0] + 6, 35)):
        poner(x, y, "æ")
    poner(rio[16][0] - 2, 16, "å")
    poner(34, 20, "œ")
    # la casa de Bata, en la orilla junto al muelle del norte (sellada por raíces de Giza: está dentro, vivo),
    # y Bata en el muelle, junto a su transbordador (cuando ya ha salido)
    poner(rio[10][0] - 4, 10, "{")
    poner(rio[12][0] + 3, 12, "}")
    # secretos: tras matorrales en el prado del oeste, en el muelle del medio y entre los juncos del sureste
    poner(5, 22, "X"); poner(5, 23, "M"); poner(6, 23, "M"); poner(4, 23, "M")
    poner(rio[30][0] + 3, 30, "X")
    poner(8, 64, "X")
    # juncos en la orilla del río y de la dársena
    for y in range(ALTO):
        for x in range(ANCHO):
            if m[y][x] == "." and any(0 <= x + dx < ANCHO and 0 <= y + dy < ALTO and m[y + dy][x + dx] == "~"
                                      for dx in (-1, 0, 1) for dy in (-1, 0, 1)) and azar.random() < 0.45:
                poner(x, y, ";")
    for (x, y) in ((10, 48), (20, 8), (rio[60][0] - 3, 66)):
        poner(x, y, "$")
    reservados = [(rio[10][0] - 4, 9, 5), (rio[12][0] - 2, 10, 3), (34, 19, 6), (31, 20, 5), (38, 20, 5), (5, 22, 2), (8, 64, 2), (22, 68, 3), (32, 3, 3)]

    def libre(x, y):
        if m[y][x] not in ".," or en_zona(x, y):
            return False
        for (rx_, ry_, rr) in reservados:
            if (x - rx_) ** 2 + (y - ry_) ** 2 <= rr * rr:
                return False
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if 0 <= x + dx < ANCHO and 0 <= y + dy < ALTO and m[y + dy][x + dx] in "#~=æåßœ{}X$":
                    return False
        return True

    for y in range(ALTO):
        for x in range(ANCHO):
            if not libre(x, y):
                continue
            borde = min(x, y, ALTO - 1 - y)
            r = azar.random()
            if borde < 3 and r < 0.75:
                poner(x, y, azar.choice("sstT"))
            elif r < 0.05:
                poner(x, y, azar.choice("ssTr"))
            elif r < 0.12:
                poner(x, y, ";")
            elif r < 0.2:
                poner(x, y, ",")
    # puertas: sur a la Orilla de Juncos (_) y norte, río arriba: La Travesía (^, cerrada hasta el transbordador)
    for x in range(20, 26):
        for y in range(ALTO - 3, ALTO):
            poner(x, y, "_" if y == ALTO - 1 else "#")
    for x in range(31, 37):
        for y in range(0, 3):
            poner(x, y, "^" if y == 0 else "#")
    poner(27, 66, "L")
    poner(38, 8, "L")
    poner(23, 68, "S")
    for k, (zx_, zy_, rx_, ry_) in zonas.items():
        poner(zx_, zy_, k)
    textos = {"1": "9, 6, 4, 0, , jefe:mamba", "2": "7, 5, 4, 3", "3": "8, 6, 4, 3"}
    return ["".join(f) for f in m], textos


def crear_travesia():
    """La Travesía (48x170, de sur a norte): el río ancho río arriba, del Embarcadero Junco a la Gruta de las Raíces.
    No se anda: se viaja en el TRANSBORDADOR, que sube solo por el centro del río (scripts/mundo/travesia/viaje.gd).
    Las orillas cambian por el camino: juncos y sauces abajo, bosque cerrado en medio, rocas y peñas arriba, cerca de
    la Gruta. A media subida, una ISLA en el lado este (la parada del séptimo eco). Arriba, el MUELLE DE PIEDRA de la
    Gruta, en la orilla oeste, con su camino (cerrado de momento)."""
    ANCHO, ALTO = 48, 170
    azar = random.Random(231)
    m = [["." for _ in range(ANCHO)] for _ in range(ALTO)]

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    # el río: ancho, con curvas suaves; el centro lo usa el viaje (misma fórmula en viaje.gd)
    for y in range(ALTO):
        cx = 24 + 5 * math.sin(y * 0.045) + 2 * math.sin(y * 0.11 + 1)
        ancho = 9 + 1.5 * math.sin(y * 0.07 + 2)
        # junto a la isla, el río se ensancha hacia el este (la isla queda rodeada de agua)
        b = max(0.0, 1 - abs(y - 84) / 19.0)
        ancho_e = ancho + 12 * (b * b * (3 - 2 * b))
        for x in range(ANCHO):
            if cx - ancho <= x <= cx + ancho_e:
                poner(x, y, "~")
    # la isla del este, a media subida
    isla = set()
    for y in range(76, 93):
        for x in range(ANCHO):
            a = math.atan2(y - 84, x - 33)
            r = 1.0 + 0.1 * math.sin(a * 3 + 1)
            if ((x - 33) / 4.5) ** 2 + ((y - 84) / 7.0) ** 2 <= r * r:
                poner(x, y, ".")
                isla.add((x, y))
    poner(34, 84, "@")
    # el muelle de piedra de la Gruta, arriba a la izquierda, y su camino
    cx_m = int(24 + 5 * math.sin(12 * 0.045) + 2 * math.sin(12 * 0.11 + 1) - 9)
    for x in range(cx_m - 4, cx_m + 6):
        for y in (11, 12, 13):
            poner(x, y, "%")
    # el camino de la Gruta: sube del muelle hacia el norte, apartado del agua
    for y in range(0, 11):
        for x in range(cx_m - 7, cx_m - 3):
            poner(x, y, "#")
    # orillas: juncos junto al agua; abajo sauces, en medio bosque cerrado, arriba rocas y peñas
    for y in range(ALTO):
        for x in range(ANCHO):
            if m[y][x] != "." or (x, y) in isla:
                continue
            junto = any(0 <= x + dx < ANCHO and m[y][x + dx] == "~" for dx in (-1, 1))
            r = azar.random()
            if junto and r < 0.6:
                poner(x, y, ";")
            elif y > 110:
                if r < 0.35:
                    poner(x, y, azar.choice("ssTt"))
            elif y > 40:
                if r < 0.55:
                    poner(x, y, azar.choice("TTtsI"))
            else:
                if r < 0.35:
                    poner(x, y, azar.choice("RrrT"))
    # (la isla, con sauces y juncos, y su eco libre)
    for (x, y) in ((35, 79), (36, 88), (31, 90)):
        poner(x, y, "s")
    for (x, y) in ((29, 83), (29, 86), (37, 84), (33, 78)):
        poner(x, y, ";")
    # puertas: abajo, el Embarcadero (se llega en el transbordador); arriba, el camino de la Gruta (cerrado)
    for x in range(20, 28):
        poner(x, ALTO - 1, "_")
    for x in range(cx_m - 7, cx_m - 3):
        poner(x, 0, "^")
    return ["".join(f) for f in m], {}


def crear_gruta():
    """La Gruta de las Raíces (64x84, de sur a norte): una CUEVA por dentro, a oscuras. Se entra por el sur, desde el
    muelle de piedra de La Travesía (las raíces de la boca se apartan con la hoja de Mauti). «0» es roca (paredes).
      - EL VESTÍBULO DE LAS SEMILLAS (abajo): una sala amplia con nichos donde duermen semillas que brillan.
      - EL PASILLO DE LAS RAÍCES DORMIDAS: estrecho y largo, con raíces atravesadas que roncan (sigilo).
      - EL SANTUARIO DE CORTEZA (a la izquierda): donde se consigue el escudo del cetro.
      - LA GALERÍA DE LAS ESPINAS (a la derecha): plantas de Giza que disparan espinas (con el escudo).
      - EL FONDO (arriba): la sala grande donde algo duerme abrazado a las raíces del Primer Árbol.
    Las huellas lilas de Mauti van de la entrada al fondo."""
    ANCHO, ALTO = 64, 84
    m = [["0" for _ in range(ANCHO)] for _ in range(ALTO)]
    azar = random.Random(251)

    def poner(x, y, c):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            m[y][x] = c

    def sala(cx, cy, rx, ry, semilla):
        az = random.Random(semilla)
        fase = az.random() * 6
        for y in range(ALTO):
            for x in range(ANCHO):
                a = math.atan2(y - cy, x - cx)
                r = 1.0 + 0.12 * math.sin(a * 3 + fase) + 0.07 * math.sin(a * 7 + fase * 2)
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= r * r:
                    poner(x, y, ".")

    def tunel(puntos, ancho):
        for (a_, b_) in zip(puntos, puntos[1:]):
            pasos = int(max(abs(b_[0] - a_[0]), abs(b_[1] - a_[1])) * 2) + 1
            for i in range(pasos + 1):
                t_ = i / pasos
                x = a_[0] + (b_[0] - a_[0]) * t_
                y = a_[1] + (b_[1] - a_[1]) * t_
                w = ancho + math.sin(t_ * 5 + a_[0]) * 0.6
                for dx in range(-int(w), int(w) + 1):
                    for dy in range(-int(w), int(w) + 1):
                        if dx * dx + dy * dy <= w * w:
                            poner(int(x) + dx, int(y) + dy, ".")

    # las salas
    sala(32, 72, 12, 7, 1)          # el vestíbulo de las semillas
    sala(12, 40, 7, 6, 2)           # el santuario de corteza
    sala(52, 40, 8, 9, 3)           # la galería de las espinas
    sala(32, 14, 15, 9, 4)          # el fondo
    # los túneles: la boca, el pasillo de las raíces dormidas, los ramales y la subida al fondo
    tunel([(32, 83), (32, 78)], 2.2)
    tunel([(32, 65), (31, 56), (33, 46), (31, 36)], 1.6)          # el pasillo (estrecho)
    tunel([(31, 44), (22, 42), (17, 41)], 1.4)                      # al santuario
    tunel([(33, 48), (42, 44), (46, 42)], 1.4)                      # a la galería
    tunel([(52, 31), (48, 24), (42, 20)], 1.6)                      # de la galería al fondo
    tunel([(31, 36), (31, 30), (30, 23)], 1.2)                      # el atajo del pasillo al fondo (tapado por raíces)
    # las raíces dormidas atravesadas en el pasillo (y la que tapa el atajo)
    for y in (60, 54, 49):
        poner(31, y, "ŕ"); poner(32, y, "ŕ")
    poner(31, 28, "ř"); poner(30, 28, "ř")
    # semillas dormidas en los nichos del vestíbulo y del fondo; el altar del escudo; las espinas de la galería
    for (x, y) in ((22, 70), (25, 66), (40, 66), (43, 71), (36, 77), (27, 77), (20, 14), (44, 12), (26, 8), (38, 8)):
        poner(x, y, "ŝ")
    poner(10, 38, "ą")
    for (x, y) in ((49, 36), (56, 38), (50, 45), (55, 46)):
        poner(x, y, "ę")
    # el corazón del fondo (lo que duerme) y la salida del norte (el Sendero Olvidado, cerrado)
    poner(32, 10, "1")
    for x in range(30, 35):
        poner(x, 0, "^")
        for y in range(1, 6):
            poner(x, y, ".")
    # la entrada (sur)
    for x in range(30, 35):
        poner(x, ALTO - 1, "_")
    poner(32, 80, "S")
    # secretos: dos nichos escondidos
    poner(4, 43, "X")
    tunel([(6, 42), (4, 43)], 0.8)
    poner(61, 52, "X")
    tunel([(59, 48), (61, 52)], 0.8)
    textos = {"1": "12, 7, 4, 3"}
    return ["".join(f) for f in m], textos


# ---------------------------------------------------------------------------
# Dibujar el suelo a partir del texto
# ---------------------------------------------------------------------------

def leer(nombre):
    with open(os.path.join(RAIZ, "datos", "mapas", nombre + ".txt"), encoding="utf-8") as f:
        filas = [l.rstrip("\n") for l in f if not l.startswith(";")]
    ancho = max(len(f) for f in filas)
    return [f.ljust(ancho, ".") for f in filas]


def tipo_suelo(c):
    if c == SUELO_AGUA:
        return "agua"
    if c == SUELO_PUENTE:
        return "puente"
    if c == SUELO_CAMINO:
        return "camino"
    if c == SUELO_LOSAS:
        return "losas"
    return "hierba"


def mascara_suave(tipos, cual, ancho, alto, radio, semilla):
    """Máscara en píxeles de un tipo de suelo con los bordes redondeados (no en escalera)."""
    import numpy as np
    from PIL import ImageFilter
    m = Image.new("L", (ancho, alto))
    m.putdata([255 if tipos[y][x] in cual else 0 for y in range(alto) for x in range(ancho)])
    m = m.resize((ancho * CASILLA, alto * CASILLA), Image.NEAREST).filter(ImageFilter.GaussianBlur(radio))
    a = np.asarray(m, dtype=np.float32) / 255.0
    ruido = np.random.default_rng(semilla).random(a.shape).astype(np.float32)
    # borde irregular: el umbral varía un poco píxel a píxel
    return a > (0.5 + (ruido - 0.5) * 0.18)


def leer_zonas(nombre):
    zonas = {}
    ruta = os.path.join(RAIZ, "datos", "mapas", nombre + ".zonas")
    if os.path.exists(ruta):
        for l in open(ruta, encoding="utf-8"):
            l = l.strip()
            if not l or l.startswith(";") or "=" not in l:
                continue
            k, v = l.split("=")
            partes = [t.strip() for t in v.split(",")]
            rx, ry, borde, enemigos = [int(t) for t in partes[:4]]
            zonas[k.strip()] = {"radios": [rx, ry], "borde": borde, "enemigos": enemigos}
            if len(partes) > 4 and partes[4]:
                zonas[k.strip()]["aldeano"] = partes[4]
            # sexto campo: «practica» (zona de práctica: cada partida salen algunas) o «jefe:<nombre>»
            if len(partes) > 5 and partes[5]:
                if partes[5].startswith("jefe:"):
                    zonas[k.strip()]["jefe"] = partes[5][5:]
                else:
                    zonas[k.strip()]["grupo"] = partes[5]
    return zonas


def leer_puertas(nombre):
    """puerta = nombre, escena de destino, puerta de llegada allí, hacia dónde sale Maisha al llegar aquí"""
    puertas = {}
    ruta = os.path.join(RAIZ, "datos", "mapas", nombre + ".puertas")
    if os.path.exists(ruta):
        for l in open(ruta, encoding="utf-8"):
            l = l.strip()
            if not l or l.startswith(";") or "=" not in l:
                continue
            k, v = l.split("=", 1)
            partes = [t.strip() for t in v.split(",")]
            pid, destino, puerta, salida = partes[:4]
            puertas[k.strip()] = {"id": pid, "destino": destino, "puerta": puerta, "salida": salida}
            if len(partes) > 4 and partes[4].startswith("portal"):
                puertas[k.strip()]["portal"] = partes[4].split(":")[1] if ":" in partes[4] else ""
            # «cerrada:marca»: no deja pasar hasta que se pone esa marca (p. ej. espinas de Giza)
            if len(partes) > 4 and partes[4].startswith("cerrada:"):
                puertas[k.strip()]["cerrada"] = partes[4].split(":")[1]
    return puertas


def exportar_json(nombre):
    """El juego lee el mapa en JSON (así se incluye solo al exportar el juego)."""
    import json
    datos = {"filas": leer(nombre), "zonas": leer_zonas(nombre), "puertas": leer_puertas(nombre), "casilla": CASILLA}
    destino = os.path.join(RAIZ, "datos", "mapas", nombre + ".json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=0)
    print("Mapa para el juego:", destino)
    # el suelo de raíces de piedra de cada zona infectada
    import dibujar_zona
    dibujar_zona.dibujar_zonas_de(nombre)


# mapas cuyo suelo se pinta con detalle (herramientas/pintar_suelo.py); los demás, con el dibujo sencillo
MAPAS_PINTADOS = {"kitovu", "prados_del_eco", "cuna_de_musgo", "bosque_cobrizo", "cienaga_quieta", "campo_segado",
                  "sendero_del_puente", "las_pasarelas", "camino_cobrizo", "senda_surcos", "canada_eco", "lago_espejo",
                  "orilla_juncos", "embarcadero_junco", "la_travesia", "gruta_raices"}


def construir_suelo(nombre):
    if nombre in MAPAS_PINTADOS:
        import pintar_suelo
        pintar_suelo.pintar(nombre)
        return
    filas = leer(nombre)
    alto, ancho = len(filas), len(filas[0])
    azar = random.Random(3)
    img = Image.new("RGB", (ancho * CASILLA, alto * CASILLA))
    px = img.load()
    tipos = [[tipo_suelo(c) for c in f] for f in filas]
    # debajo de un objeto (un farolillo en la plaza, un aldeano en el camino...) el suelo
    # es el que más se repite a su alrededor
    suelos = ".,#~=%"
    for y in range(alto):
        for x in range(ancho):
            if filas[y][x] in suelos:
                continue
            vecinos = [tipos[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                       if 0 <= x + dx < ancho and 0 <= y + dy < alto and filas[y + dy][x + dx] in suelos]
            if vecinos:
                tipos[y][x] = max(set(vecinos), key=vecinos.count)
    es_agua = mascara_suave(tipos, ("agua",), ancho, alto, 7, 1)
    # el camino también pasa por debajo de las losas, para que lleguen a juntarse
    es_camino = mascara_suave(tipos, ("camino", "losas"), ancho, alto, 9, 2)
    es_losas = mascara_suave(tipos, ("losas",), ancho, alto, 9, 4)

    def tipo(x, y):
        if 0 <= x < ancho * CASILLA and 0 <= y < alto * CASILLA:
            tx, ty = x // CASILLA, y // CASILLA
            if tipos[ty][tx] == "puente":
                return "puente"
            if es_agua[y, x]:
                return "agua"
            if es_losas[y, x]:
                return "losas"
            if es_camino[y, x]:
                return "camino"
        return "hierba"

    def cerca(x, y, t, r):
        """¿hay casilla de tipo t a menos de r píxeles?"""
        for dy in (-r, 0, r):
            for dx in (-r, 0, r):
                if tipo(x + dx, y + dy) == t:
                    return True
        return False

    # losas: piedras irregulares (celdas alrededor de puntos repartidos con algo de azar)
    azar_losas = random.Random(17)
    PASO = 9
    centros = {}
    for gy in range(-1, alto * CASILLA // PASO + 2):
        for gx in range(-1, ancho * CASILLA // PASO + 2):
            centros[(gx, gy)] = (gx * PASO + azar_losas.uniform(1, PASO - 1), gy * PASO + azar_losas.uniform(1, PASO - 1),
                                 azar_losas.random())

    def losa(x, y, ruido):
        gx, gy = x // PASO, y // PASO
        d = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                cx, cy, tono = centros[(gx + dx, gy + dy)]
                d.append(((x - cx) ** 2 + ((y - cy) * 1.25) ** 2, cx, cy, tono))
        d.sort()
        (d1, cx, cy, tono), (d2, _, _, _) = d[0], d[1]
        if d2 ** 0.5 - d1 ** 0.5 < 1.3:            # junta entre dos piedras
            return COL["H2"] if ruido < 0.4 else COL["P2"]
        base = COL["P4"] if tono < 0.35 else COL["P3"]
        if y < cy - 2 and tono < 0.35 or (y < cy - 3 and ruido < 0.5):
            base = COL["P4"]                        # cara de arriba, más iluminada
        if ruido > 0.96:
            return COL["P2"]
        return base

    for y in range(alto * CASILLA):
        for x in range(ancho * CASILLA):
            t = tipo(x, y)
            ruido = azar.random()
            if t == "agua":
                # orilla: un píxel de tierra oscura y agua más clara cerca del borde
                if not cerca(x, y, "hierba", 1) or cerca(x, y, "puente", 1):
                    c = COL["A3"] if ruido < 0.93 else COL["A4"]
                    if cerca(x, y, "hierba", 3) and not cerca(x, y, "puente", 3):
                        c = COL["A4"] if ruido < 0.5 else COL["A3"]
                else:
                    c = COL["T2"]
            elif t == "puente":
                tabla = (x // 4) % 2
                c = COL["M4"] if (y % CASILLA) in (1, 14) else (COL["M3"] if tabla else COL["M4"])
                if x % 4 == 0:
                    c = COL["M2"]
            elif t == "losas":
                c = losa(x, y, ruido)
                if cerca(x, y, "hierba", 2) and ruido < 0.3:
                    c = COL["H3"]
            elif t == "camino":
                # borde irregular: cerca de la hierba se mezcla
                borde = cerca(x, y, "hierba", 3)
                if borde and ruido < 0.35:
                    c = COL["H3"]
                else:
                    c = COL["T4"] if ruido < 0.08 else (COL["T2"] if ruido > 0.94 else COL["T3"])
            else:
                c = COL["H3"]
                if ruido < 0.025:
                    c = COL["H2"]
                elif ruido > 0.985:
                    c = COL["H4"]
                if cerca(x, y, "camino", 2) and ruido < 0.12:
                    c = COL["T3"]
            px[x, y] = c

    # matas de hierba y flores encima
    for ty in range(alto):
        for tx in range(ancho):
            if tipos[ty][tx] != "hierba":
                continue
            for _ in range(2):
                x = tx * CASILLA + azar.randrange(1, 14)
                y = ty * CASILLA + azar.randrange(2, 14)
                px[x, y] = COL["H4"]
                px[x + 1, y - 1] = COL["H4"]
                px[x, y + 1] = COL["H2"]
            if filas[ty][tx] == ",":
                for _ in range(azar.randrange(2, 5)):
                    x = tx * CASILLA + azar.randrange(2, 14)
                    y = ty * CASILLA + azar.randrange(2, 13)
                    px[x, y] = azar.choice([COL["F_A"], COL["F_R"], COL["F_L"]])
                    px[x, y + 1] = COL["H2"]

    destino = os.path.join(RAIZ, "arte", "mundos", "raiz", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    img.save(destino)
    print("Suelo dibujado:", destino, img.size)


if __name__ == "__main__":
    nombre = sys.argv[1] if len(sys.argv) > 1 else "prados_del_eco"
    if "--crear" in sys.argv:
        filas, zonas = {"cuna_de_musgo": crear_aldea, "kitovu": crear_kitovu,
                        "bosque_cobrizo": crear_bosque, "cienaga_quieta": crear_cienaga, "campo_segado": crear_campo,
                        "sendero_del_puente": crear_sendero, "las_pasarelas": crear_pasarelas,
                        "camino_cobrizo": crear_camino, "senda_surcos": crear_senda,
                        "canada_eco": crear_canada, "lago_espejo": crear_lago,
                        "orilla_juncos": crear_orilla, "embarcadero_junco": crear_embarcadero, "la_travesia": crear_travesia, "gruta_raices": crear_gruta}.get(nombre, crear_prados)()
        carpeta = os.path.join(RAIZ, "datos", "mapas")
        os.makedirs(carpeta, exist_ok=True)
        with open(os.path.join(carpeta, nombre + ".txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(filas) + "\n")
        if zonas:
            with open(os.path.join(carpeta, nombre + ".zonas"), "w", encoding="utf-8") as f:
                f.write("; zona = semieje horizontal, semieje vertical (en casillas), borde de aviso (casillas), enemigos al cerrarse"
                        "[, aldeano de piedra junto a la zona][, practica | jefe:<nombre>]\n")
                aldeanos = {"2": ", pino", "3": ", corteza"} if nombre == "prados_del_eco" else {}
                for k, z in zonas.items():
                    if isinstance(z, str):
                        f.write(f"{k} = {z}\n")
                        continue
                    zx, zy, rx, ry = z
                    f.write(f"{k} = {rx}, {ry}, 6, 2{aldeanos.get(k, '')}\n")
        print("Mapa creado:", nombre)
    construir_suelo(nombre)
    exportar_json(nombre)
