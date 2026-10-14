"""
ROPA DE MAISHA dibujada píxel a píxel.

Cada prenda se dibuja UNA VEZ por dirección (abajo, arriba, lado) y se cuelga de un PUNTO DE ANCLAJE
de Maisha (cabeza, cuerpo, brazo...). El juego la mueve sola con cada fotograma de cada animación,
así que no hay que redibujarla para andar o respirar.

Uso:  python3 herramientas/dibujar_prendas.py
Genera:
  arte/personajes/maisha/prendas/<prenda>_<direccion>.png
  datos/prendas.json   (qué piezas tiene cada prenda, dónde se cuelgan y si van delante o detrás)
"""
import json
import os
from PIL import Image

# Colores de la paleta de Raíz. Cada material lleva su propio contorno (su tono más oscuro).
COLORES = {
    # Follaje (hojas, musgo)
    "k": "152814",  # Follaje 1 (contorno)
    "d": "355029",  # Follaje 2
    "m": "5D793E",  # Follaje 3
    "h": "90A153",  # Follaje 4
    # Follaje cobre (brotes, broches)
    "q": "3D3214",  # Follaje cobre 1 (contorno)
    "c": "A37036",  # Follaje cobre 3
    "C": "C68756",  # Follaje cobre 4
    # Brote (verde vivo de Maisha, para que la prenda "sea suya")
    "g": "6FCF4F",  # Brote 2
    "G": "3E9A35",  # Brote 1
    # Paja (sombrero) y cinta roja
    "o": "3D2A10",  # Paja 1 (contorno)
    "p": "A37036",  # Paja 3
    "P": "D29A43",  # Paja 4
    "l": "EFC06A",  # Paja 5 (luz)
    "r": "8F2532",  # Tejado 3 (cinta, sombra)
    "R": "D5525E",  # Tejado 5 (cinta)
    # Raíz (los brazaletes)
    "w": "3A2414",  # raíz oscura (contorno)
    "W": "7E5430",  # raíz
    "X": "A87A48",  # raíz con luz
    "Y": "D0A060",  # corteza con mucha luz
    # Brisa (la bufanda del Aliento)
    "b": "1E5A6E",  # brisa oscura (contorno)
    "B": "5AB0C8",  # brisa
    "v": "9FD8E8",  # brisa clara
    "V": "E0F6FA",  # brisa con luz
    # flor
    "f": "FFD7E0",  # pétalo
    "F": "F9D36A",  # centro
}

# ---------------------------------------------------------------------------
# BRAZALETES DE RAÍZ  (zona: brazos · Arte de la Raíz, niveles 1 y 2)
# Una raíz enroscada en cada muñeca. En el nivel 2 le brota una hojita.
# Se cuelga del anclaje de cada brazo (esquina superior izquierda del brazo).
# ---------------------------------------------------------------------------
BRAZALETE = [
    "wXWw",
    ".ww.",
]
BRAZALETE_HOJA = [
    "...g",
    "wXWG",
    ".ww.",
]

# ---------------------------------------------------------------------------
# BUFANDA DE BRISA  (zona: torso · Arte del Aliento, niveles 1 y 2)
# Una bufanda de aire al cuello; las puntas ondean. En el nivel 2, las puntas son largas y vuelan con el viento.
# Se cuelga del anclaje «cuerpo» (esquina superior izquierda del cuerpo).
# ---------------------------------------------------------------------------
BUFANDA_ABAJO = [
    "bbbbbbbbbbbb..",
    "bvVvBvVvBvvBb.",
    ".bbbbbbbbbBBvb",
    "..........bBvb",
    "..........bvb.",
    "...........b..",
]
BUFANDA_ARRIBA = [   # de espaldas: el nudo y las puntas caen por la espalda
    "bbbbbbbbbbbb",
    "bvBvBvVvBvvb",
    ".bbbbBvbbbb.",
    ".....bBvb...",
    ".....bvBb...",
    "......bb....",
]
BUFANDA_LADO = [     # de perfil (mirando a la derecha): las puntas se van hacia atrás
    "..bbbbbbbbbb",
    ".bBvVvBvVvBb",
    "bvBbbbbbbbb.",
    "bvb.........",
    ".b..........",
]
BUFANDA_LARGA_ABAJO = [
    "bbbbbbbbbbbb.......",
    "bvVvBvVvBvvBbbb....",
    ".bbbbbbbbbBBvvBbb..",
    "..........bBvbbvVbb",
    "..........bvb..bvVb",
    "...........b....bb.",
]
BUFANDA_LARGA_ARRIBA = [
    "bbbbbbbbbbbb",
    "bvBvBvVvBvvb",
    ".bbbbBvbbbb.",
    ".....bBvb...",
    ".....bvBbb..",
    "......bvVb..",
    ".......bvb..",
    "........b...",
]
BUFANDA_LARGA_LADO = [
    "........bbbbbbbbbb",
    "...bbb.bBvVvBvVvBb",
    ".bbvVvbvBbbbbbbbb.",
    "bvVbbbBvb.........",
    ".bb...bb..........",
]


# ---------------------------------------------------------------------------
# CORONA DE HOJAS  (zona: cabeza · Arte de Raíz)
# Un aro de hojas apoyado en lo alto de la cabeza, con un capullo cobrizo delante.
# Se cuelga del anclaje "cabeza" (esquina superior izquierda de la cabeza, 16 de ancho).
# ---------------------------------------------------------------------------
CORONA_ABAJO = [
    ".k..............k.",
    "khk.....qq.....khk",
    "kmhk...qCcq...khmk",
    ".kmhhhhhqqhhhhhmk.",
    "..kkkkkkkkkkkkkk..",
]
CORONA_ARRIBA = [   # vista desde atrás: sin capullo
    ".k..............k.",
    "khk............khk",
    "kmhk..........khmk",
    ".kmhhhhhhhhhhhhmk.",
    "..kkkkkkkkkkkkkk..",
]
CORONA_LADO = [     # de perfil (mirando a la derecha): hojas detrás, capullo delante
    ".k................",
    "khk...............",
    "kmhk...........qq.",
    ".kmhhhhhhhhhhhqCcq",
    "..kkkkkkkkkkkkkqq.",
]

# ---------------------------------------------------------------------------
# CAPA DE MUSGO  (zona: espalda · Arte de Raíz)
# Cuelga de los hombros hasta las rodillas, con un broche de hoja cobriza.
# Usa el verde del brote de Maisha (g, G): el verde oliva del follaje se perdía sobre la hierba.
# Se cuelga del anclaje "cuerpo".
#   abajo: va DETRÁS de Maisha (solo asoma por los lados y entre las piernas)
#   arriba: va DELANTE (la vemos entera)
#   lado: va DETRÁS y asoma por la espalda
# ---------------------------------------------------------------------------
CAPA_ABAJO = [      # detrás: asoma sobre los hombros, bajo los brazos y entre las piernas
    "kGk........kGk",
    "kGGk......kGGk",
    "kGGk......kGGk",
    "kGGk......kGGk",
    "kGGk......kGGk",
    "kGGk......kGGk",
    "kGGk......kGGk",
    "kdGGGGGGGGGGdk",
    "kdGGGGGGGGGGdk",
    "kddGGGGGGGGddk",
    "kkkkkkkkkkkkkk",
]
CAPA_ARRIBA = [     # delante: la vemos entera; deja ver los brazos y se abre al bajar
    ".kkkkkkkkkk.",
    ".kgggGGGGdk.",
    ".kgGgGGdGdk.",
    ".kgGgGGdGdk.",
    ".kgGgGGdGdk.",
    ".kgGgGGdGdk.",
    "kgGGgGGdGGdk",
    "kgGGgGGdGGdk",
    "kgGgGGGGdGdk",
    "kkgkkgkkdkkk",
]
CAPA_LADO = [       # detrás: cuelga del hombro y asoma por la espalda
    "....kk",
    "...kgk",
    "...kgG",
    "..kgGG",
    "..kgGG",
    ".kgGGG",
    ".kgGGG",
    "kgGGGG",
    "kgGgGG",
    "kkkkkk",
]
# Broche de hoja cobriza: va delante, en el hombro (nunca tapa el corazón)
BROCHE_ABAJO = [
    ".c.",
    "cCq",
    ".q.",
]

# ---------------------------------------------------------------------------
# SOMBRERO DE PAJA  (zona: cabeza · Arte de Raíz · se compra en la tienda de Tawi)
# Copa redonda, ala ancha y una cinta roja. Se cuelga del anclaje "cabeza"; asoma el brote por arriba
# (la copa tiene una muesca en el centro para que no lo tape).
# ---------------------------------------------------------------------------
SOMBRERO_ABAJO = [
    ".....ooo....ooo.....",
    "....olllo..oPPpo....",
    "....olPPPooPPPpo....",
    "....orRRRRRRRRro....",
    "..oooPPPPPPPPPpooo..",
    ".ollllPPPPPPPPPPppo.",
    "oPPPPPPPPPPPPPPPpppo",
    ".oooooooooooooooooo.",
]
SOMBRERO_ARRIBA = [  # de espaldas: el lazo de la cinta cae por detrás
    ".....ooo....ooo.....",
    "....olllo..oPPpo....",
    "....olPPPooPPPpo....",
    "....orRRRRRRRRro....",
    "..oooPPPPPrRrPpooo..",
    ".ollllPPPPrRrPPPppo.",
    "oPPPPPPPPPPrPPPPpppo",
    ".oooooooooorooooooo.",
]
SOMBRERO_LADO = [    # de perfil (mirando a la derecha): el ala se alarga hacia delante
    "....ooo....ooo......",
    "...olllo..oPPpo.....",
    "...olPPPooPPPpo.....",
    "..rorRRRRRRRRro.....",
    ".rRoPPPPPPPPPpooooo.",
    ".olllPPPPPPPPPPPppoo",
    "oPPPPPPPPPPPPPPPpppo",
    ".oooooooooooooooooo.",
]

# ---------------------------------------------------------------------------
# CATÁLOGO: qué piezas forma cada prenda.
#   ancla: punto de Maisha del que cuelga · desplazamiento: píxeles desde ese punto
#   delante: true = se dibuja encima de Maisha; false = detrás
# ---------------------------------------------------------------------------
# El cetro lo dibuja herramientas/dibujar_combate.py. Se lleva como un bastón: la mano lo agarra
# justo bajo el adorno (columna 3, fila 9) y el palo baja hasta el suelo por fuera del brazo.
# Así no tapa la cara y apenas se mueve al andar (como mucho 1 píxel, con el paso).
AGARRE_CETRO = (-3, -9)
## Los cetros del Arte del Cetro (cetro_0 ... cetro_6, 16×21): la mano agarra en la columna 7, fila 13.
## Dos ramas abrazan la gema; las hojas de arriba se vuelven de cobre y, en el 6, todo se dora.
AGARRE_CETRO_N = {"abajo": (-5, -13), "arriba": (-5, -13), "lado": (3, -13)}   # de lado, por delante de la cara


def cetro_nivel(n):
    """El cetro en el nivel n (0-6) del Arte del Cetro: 0 la rama · 1 cinta verde · 2 gema grande · 3 ✦ CORTEZA DE ROBLE
    (corteza oscura con vetas y aro de cobre) · 4 hojas de cobre · 5 gema dorada · 6 ✦ CETRO DEL PRIMER ÁRBOL (dorado,
    con dos florecillas). Siempre fino: el personaje no debe verse cargado."""
    img = Image.new("RGBA", (16, 21), (0, 0, 0, 0))
    def px(x, y, c):
        if 0 <= x < 16 and 0 <= y < 21:
            img.putpixel((x, y), tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    roble = n >= 3
    oro = n >= 6
    m = ["3A2414", "5A3A20", "7E5430", "A07040"]
    if roble:
        m = ["24130A", "4E2C14", "86542A", "B8844A"]
    if oro:
        m = ["4A3008", "9A7420", "E8C060", "FFF0B0"]
    # el palo: siempre fino (2 de madera y el contorno); el roble se nota por la corteza y el aro, no por el grosor
    for y in range(9, 21):
        cx = 7 + (1 if (y // 6) % 2 and not roble else 0)       # la rama de madera tiene un quiebro
        px(cx - 1, y, m[0])
        px(cx, y, m[3] if y % 4 == 1 else m[2])
        px(cx + 1, y, m[1] if (roble and y % 3 == 0) else (m[2] if y % 5 else m[1]))
        px(cx + 2, y, m[0])
        if roble and y % 5 == 2:
            px(cx, y, m[0])                                          # vetas de la corteza
    px(7, 20, m[0]); px(8, 20, m[0])
    if roble:                                                         # el aro de cobre (de oro en el 6)
        aro = ("F2D27A", "8A6A10") if oro else ("C06A2A", "7A3A14")
        for x in range(6, 10):
            px(x, 12, aro[0]); px(x, 13, aro[1])
        px(7, 12, "FFE0A0")
    if n >= 1 and not oro:                                            # la cinta verde, enroscada
        for (x, y, c) in ((6, 15, "3E9A35"), (7, 16, "6FCF4F"), (8, 16, "6FCF4F"), (9, 17, "3E9A35"), (10, 18, "6FCF4F"), (10, 19, "3E9A35")):
            px(x, y, c)
    # la cabeza: dos ramas que abrazan la gema
    for (x, y) in ((4, 6), (4, 7), (5, 8), (6, 9), (11, 6), (11, 7), (10, 8), (9, 9)):
        px(x, y, m[1])
    for (x, y) in ((4, 5), (11, 5), (3, 4), (12, 4)):
        px(x, y, m[2])
    g = ["8A3A0F", "EF8A26", "FDE27E"] if n < 5 else ["8A6A10", "F9D77A", "FFFFFF"]
    if n >= 2:      # gema grande: un rombo de 6×6
        for (x, y) in ((7, 3), (8, 3), (6, 4), (9, 4), (5, 5), (10, 5), (5, 6), (10, 6), (6, 7), (9, 7), (7, 8), (8, 8)):
            px(x, y, g[0])
        for x in range(6, 10):
            for y in range(4, 8):
                if not ((x, y) in ((6, 4), (9, 4), (6, 7), (9, 7))):
                    px(x, y, g[1])
        px(6, 5, g[2]); px(7, 4, g[2])
    else:           # gema pequeña: 4×4
        for (x, y) in ((7, 4), (8, 4), (6, 5), (9, 5), (6, 6), (9, 6), (7, 7), (8, 7)):
            px(x, y, g[0])
        for (x, y) in ((7, 5), (8, 5), (7, 6), (8, 6)):
            px(x, y, g[1])
        px(7, 5, g[2])
    hoja = ["2F5A20", "6FCF4F", "B8E08A"] if n < 4 else ["6A3418", "E0904E", "FFC08A"]
    for (x, y, k) in ((2, 3, 1), (1, 2, 2), (2, 2, 1), (3, 3, 0), (13, 3, 1), (14, 2, 2), (13, 2, 1), (12, 3, 0),
                      (7, 1, 1), (8, 1, 2), (7, 2, 0), (8, 2, 0)):
        px(x, y, hoja[k])
    if oro:                                                           # dos florecillas entre las hojas
        for (x, y, c) in ((4, 0, "FFD7E0"), (11, 0, "FFD7E0"), (4, 1, "F9D36A"), (11, 1, "F9D36A")):
            px(x, y, c)
    return img


# ---------------------------------------------------------------------------
# PRENDAS GRANDES DE LA RAÍZ (las da el Arte de la Raíz)
# ---------------------------------------------------------------------------
# RAÍCES EN LAS PIERNAS (zona: piernas · Raíz 1; con hojas, Raíz 2). Una raíz enroscada en cada pierna.
RAICES_PIERNA = [
    "Xw...",
    ".wXw.",
    "...wX",
    ".Xw..",
]
RAICES_PIERNA_HOJA = [
    "g....",
    "GXw..",
    ".wXwg",
    "...wX",
    ".Xw..",
]
RAICES_LADO = [
    "Xw......",
    ".wXw.Xw.",
    "...wX.wX",
    ".Xw..Xw.",
]
RAICES_LADO_HOJA = [
    "g.....g.",
    "GXw..XwG",
    ".wXw.Xw.",
    "...wX.wX",
    ".Xw..Xw.",
]
# HOMBRERAS DE CORTEZA (zona: hombros · Raíz 4), con una hoja de roble encima
HOMBRERA_IZQ = [
    "..gg..",
    ".gGhg.",
    "wwGwww",
    "wYXXWw",
    "wXWXXw",
    ".wWww.",
]
HOMBRERA_DER = [f[::-1] for f in HOMBRERA_IZQ]
HOMBRERA_LADO = [
    "..gg...",
    ".gGhg..",
    "wwGwwww",
    "wYXXXWw",
    "wXWXWXw",
    ".wWwww.",
]
# CORONA DEL BOSQUE (zona: cabeza · Raíz 6): astas de rama con flores, a los lados del brote
CORONA_BOSQUE_ABAJO = [
    ".f......................f.",
    "fFf.Xw..............wX.fFf",
    ".fXw.Xw............wX.wXf.",
    "...Xw.Xw..........wX.wX...",
    "....XwwXw........wXwwX....",
    "......wXXwwwwwwwwXXw......",
    "........wwwwwwwwww........",
]
CORONA_BOSQUE_ARRIBA = [
    "........................",
    "..Xw................wX..",
    "Xw.Xw..............wX.wX",
    ".Xw.Xw............wX.wX.",
    "...XwwXw........wXwwX...",
    ".....wXXwwwwwwwwXXw.....",
    ".......wwwwwwwwww.......",
]
CORONA_BOSQUE_LADO = [
    ".f..............",
    "fFf.Xw......f...",
    ".fXw.Xw....fFf..",
    "...Xw.Xw...wXf..",
    "....XwwXw.wX....",
    "......wXXwX.....",
    "........ww......",
]


def capa_hojas(direccion, fotograma):
    """CAPA DE HOJAS (zona: espalda · Raíz 5): escamas de hoja que se mecen (2 fotogramas). Pequeña: no más ancha que
    los brazos. abajo y lado van detrás de Maisha; arriba (de espaldas) va delante y se ve entera."""
    if direccion == "abajo":
        ancho_arriba, ancho_abajo, alto = 14, 16, 10
    elif direccion == "arriba":
        ancho_arriba, ancho_abajo, alto = 12, 14, 10
    else:
        ancho_arriba, ancho_abajo, alto = 5, 7, 10
    w = ancho_abajo + 2
    img = Image.new("RGBA", (w, alto + 2), (0, 0, 0, 0))
    def px(x, y, c):
        if 0 <= x < w and 0 <= y < alto + 2:
            img.putpixel((x, y), tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    for y in range(alto):
        a = ancho_arriba + (ancho_abajo - ancho_arriba) * y / (alto - 1)
        # en el lado la capa cuelga hacia atrás (a la izquierda) y se mece con el paso
        x0 = round((w - a) / 2) if direccion != "lado" else round(w - a - 1 - (y / alto) * (1 + fotograma))
        x0 += (fotograma if direccion != "lado" and y >= alto - 3 else 0)
        for x in range(x0, x0 + round(a)):
            borde = x == x0 or x == x0 + round(a) - 1
            fila, col = y % 3, (x - x0 + (y // 3) * 2) % 4
            if borde:
                px(x, y, "152814")
            elif fila == 0 and col == 0:
                px(x, y, "355029")
            elif col in (1, 2) and fila != 2:
                px(x, y, "90D060" if fila == 0 else "3E9A35")
            else:
                px(x, y, "3E9A35" if (x + y) % 3 else "2E7A2A")
    # las puntas de las hojas, abajo
    y = alto
    a = ancho_abajo
    x0 = round((w - a) / 2) + fotograma if direccion != "lado" else round(w - a - 1 - (1 + fotograma))
    for x in range(x0, x0 + a, 3):
        px(x, y, "152814"); px(x + 1, y, "3E9A35"); px(x + 1, y + 1, "152814")
    return img


def tira(funcion, direccion, n=2):
    """Pone los fotogramas de una prenda animada en una tira horizontal"""
    marcos = [funcion(direccion, k) for k in range(n)]
    img = Image.new("RGBA", (marcos[0].width * n, marcos[0].height), (0, 0, 0, 0))
    for k, m in enumerate(marcos):
        img.alpha_composite(m, (k * m.width, 0))
    return img


PRENDAS = {
    **{f"cetro_{n}": {
        "nombre": f"Cetro (Arte del Cetro {n})",
        "zona": "arma",
        "arte": "cetro",
        "piezas": {d: [(f"cetro_{n}", None, "mano", AGARRE_CETRO_N[d], True)] for d in ("abajo", "arriba", "lado")},
        "de_artes": True,
    } for n in range(0, 7)},
    "raices_piernas": {
        "de_artes": True,
        "nombre": "Raíces en las piernas",
        "zona": "piernas",
        "arte": "raiz",
        "piezas": {
            "abajo": [("raices_pierna", RAICES_PIERNA, "pie_izq", (-1, -4), True), ("raices_pierna", RAICES_PIERNA, "pie_der", (-1, -4), True)],
            "arriba": [("raices_pierna", RAICES_PIERNA, "pie_izq", (-1, -4), True), ("raices_pierna", RAICES_PIERNA, "pie_der", (-1, -4), True)],
            "lado": [("raices_lado", RAICES_LADO, "piernas", (-1, 0), True)],
        },
    },
    "raices_piernas_hoja": {
        "de_artes": True,
        "nombre": "Raíces con hojas en las piernas",
        "zona": "piernas",
        "arte": "raiz",
        "piezas": {
            "abajo": [("raices_pierna_hoja", RAICES_PIERNA_HOJA, "pie_izq", (-1, -5), True), ("raices_pierna_hoja", RAICES_PIERNA_HOJA, "pie_der", (-1, -5), True)],
            "arriba": [("raices_pierna_hoja", RAICES_PIERNA_HOJA, "pie_izq", (-1, -5), True), ("raices_pierna_hoja", RAICES_PIERNA_HOJA, "pie_der", (-1, -5), True)],
            "lado": [("raices_lado_hoja", RAICES_LADO_HOJA, "piernas", (-1, -1), True)],
        },
    },
    "hombreras_corteza": {
        "de_artes": True,
        "nombre": "Hombreras de corteza",
        "zona": "hombros",
        "arte": "raiz",
        "piezas": {
            "abajo": [("hombrera_izq", HOMBRERA_IZQ, "brazo_izq", (-2, -3), True), ("hombrera_der", HOMBRERA_DER, "brazo_der", (0, -3), True)],
            "arriba": [("hombrera_der", HOMBRERA_DER, "brazo_izq", (-2, -3), True), ("hombrera_izq", HOMBRERA_IZQ, "brazo_der", (0, -3), True)],
            "lado": [("hombrera_lado", HOMBRERA_LADO, "brazo", (-3, -3), True)],
        },
    },
    "capa_hojas": {
        "de_artes": True,
        "nombre": "Capa de hojas",
        "zona": "espalda",
        "arte": "raiz",
        "piezas": {
            "abajo": [("capa_hojas_abajo", "tira:abajo", "cuerpo", (-4, -1), False)],
            "arriba": [("capa_hojas_arriba", "tira:arriba", "cuerpo", (-3, -1), True)],
            "lado": [("capa_hojas_lado", "tira:lado", "cuerpo", (-6, 0), False)],
        },
    },
    "corona_bosque": {
        "de_artes": True,
        "nombre": "Corona del bosque",
        "zona": "cabeza",
        "arte": "raiz",
        "piezas": {
            "abajo": [("corona_bosque_abajo", CORONA_BOSQUE_ABAJO, "cabeza", (-5, -5), True)],
            "arriba": [("corona_bosque_arriba", CORONA_BOSQUE_ARRIBA, "cabeza", (-4, -5), True)],
            "lado": [("corona_bosque_lado", CORONA_BOSQUE_LADO, "cabeza", (-1, -5), True)],
        },
    },
    "brazaletes_raiz": {
        "de_artes": True,
        "nombre": "Brazaletes de raíz",
        "zona": "brazos",
        "arte": "raiz",
        "piezas": {
            "abajo": [("brazalete_raiz", BRAZALETE, "brazo_izq", (0, 3), True), ("brazalete_raiz", BRAZALETE, "brazo_der", (-1, 3), True)],
            "arriba": [("brazalete_raiz", BRAZALETE, "brazo_izq", (0, 3), True), ("brazalete_raiz", BRAZALETE, "brazo_der", (-1, 3), True)],
            "lado": [("brazalete_raiz", BRAZALETE, "brazo", (-1, 2), True)],
        },
    },
    "brazaletes_hoja": {
        "de_artes": True,
        "nombre": "Brazaletes de raíz con hoja",
        "zona": "brazos",
        "arte": "raiz",
        "piezas": {
            "abajo": [("brazalete_hoja", BRAZALETE_HOJA, "brazo_izq", (0, 2), True), ("brazalete_hoja", BRAZALETE_HOJA, "brazo_der", (-1, 2), True)],
            "arriba": [("brazalete_hoja", BRAZALETE_HOJA, "brazo_izq", (0, 2), True), ("brazalete_hoja", BRAZALETE_HOJA, "brazo_der", (-1, 2), True)],
            "lado": [("brazalete_hoja", BRAZALETE_HOJA, "brazo", (-1, 1), True)],
        },
    },
    "bufanda_brisa": {
        "de_artes": True,
        "nombre": "Bufanda de brisa",
        "zona": "torso",
        "arte": "aliento",
        "piezas": {
            "abajo": [("bufanda_brisa_abajo", BUFANDA_ABAJO, "cuerpo", (-1, -1), True)],
            "arriba": [("bufanda_brisa_arriba", BUFANDA_ARRIBA, "cuerpo", (-1, -1), True)],
            "lado": [("bufanda_brisa_lado", BUFANDA_LADO, "cuerpo", (-2, -1), True)],
        },
    },
    "bufanda_viento": {
        "de_artes": True,
        "nombre": "Bufanda de viento",
        "zona": "torso",
        "arte": "aliento",
        "piezas": {
            "abajo": [("bufanda_viento_abajo", BUFANDA_LARGA_ABAJO, "cuerpo", (-1, -1), True)],
            "arriba": [("bufanda_viento_arriba", BUFANDA_LARGA_ARRIBA, "cuerpo", (-1, -1), True)],
            "lado": [("bufanda_viento_lado", BUFANDA_LARGA_LADO, "cuerpo", (-8, -1), True)],
        },
    },
    "cetro_raiz": {
        "nombre": "Cetro-rama (Raíz)",
        "zona": "arma",
        "arte": "raiz",
        "piezas": {
            "abajo": [("cetro_raiz", None, "mano", AGARRE_CETRO, True)],
            "arriba": [("cetro_raiz", None, "mano", AGARRE_CETRO, True)],    # va por fuera del brazo: se ve también de espaldas
            "lado": [("cetro_raiz", None, "mano", AGARRE_CETRO, True)],
        },
    },
    "corona_hojas": {
        "nombre": "Corona de hojas",
        "zona": "cabeza",
        "arte": "raiz",
        "piezas": {
            "abajo": [("corona_hojas_abajo", CORONA_ABAJO, "cabeza", (-1, 0), True)],
            "arriba": [("corona_hojas_arriba", CORONA_ARRIBA, "cabeza", (-1, 0), True)],
            "lado": [("corona_hojas_lado", CORONA_LADO, "cabeza", (-1, 0), True)],
        },
    },
    "sombrero_paja": {
        "nombre": "Sombrero de paja",
        "zona": "cabeza",
        "arte": "raiz",
        "piezas": {
            "abajo": [("sombrero_paja_abajo", SOMBRERO_ABAJO, "cabeza", (-2, -4), True)],
            "arriba": [("sombrero_paja_arriba", SOMBRERO_ARRIBA, "cabeza", (-2, -4), True)],
            "lado": [("sombrero_paja_lado", SOMBRERO_LADO, "cabeza", (-2, -4), True)],
        },
    },
    "capa_musgo": {
        "nombre": "Capa de musgo",
        "zona": "espalda",
        "arte": "raiz",
        "piezas": {
            "abajo": [("capa_musgo_abajo", CAPA_ABAJO, "cuerpo", (-2, 0), False),
                      ("capa_musgo_broche", BROCHE_ABAJO, "cuerpo", (0, 1), True)],
            "arriba": [("capa_musgo_arriba", CAPA_ARRIBA, "cuerpo", (-1, 1), True)],
            "lado": [("capa_musgo_lado", CAPA_LADO, "cuerpo", (-3, 1), False)],
        },
    },
}


def a_imagen(filas):
    ancho = max(len(f) for f in filas)
    for i, f in enumerate(filas):
        assert len(f) == ancho, f"fila {i} mide {len(f)} y debería medir {ancho}: {f}"
    img = Image.new("RGBA", (ancho, len(filas)), (0, 0, 0, 0))
    for y, fila in enumerate(filas):
        for x, ch in enumerate(fila):
            if ch != ".":
                c = COLORES[ch]
                img.putpixel((x, y), tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    return img


if __name__ == "__main__":
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    carpeta = os.path.join(raiz, "arte", "personajes", "maisha", "prendas")
    os.makedirs(carpeta, exist_ok=True)
    # Se conservan las prendas que se hayan añadido A MANO en datos/prendas.json:
    # este programa solo reescribe las que dibuja él.
    ruta_json = os.path.join(raiz, "datos", "prendas.json")
    catalogo = {}
    if os.path.exists(ruta_json):
        with open(ruta_json, encoding="utf-8") as f:
            catalogo = json.load(f)
    for clave, p in PRENDAS.items():
        entrada = {"nombre": p["nombre"], "zona": p["zona"], "arte": p["arte"], "piezas": {}}
        if p.get("de_artes"):
            entrada["de_artes"] = True   # la dan las Artes (no se compra ni se elige en la mochila)
        for direccion, piezas in p["piezas"].items():
            lista = []
            for archivo, filas, ancla, (dx, dy), delante in piezas:
                fotogramas = 1
                if isinstance(filas, str) and filas.startswith("tira:"):   # prenda animada (fotogramas en tira)
                    fotogramas = 2
                    tira(capa_hojas, filas[5:], fotogramas).save(os.path.join(carpeta, archivo + ".png"))
                elif filas is not None:   # None = el dibujo lo genera otro programa (p. ej. el cetro)
                    a_imagen(filas).save(os.path.join(carpeta, archivo + ".png"))
                elif archivo.startswith("cetro_") and archivo[6:].isdigit():
                    cetro_nivel(int(archivo[6:])).save(os.path.join(carpeta, archivo + ".png"))
                lista.append({
                    "fotogramas": fotogramas,
                    "textura": f"res://arte/personajes/maisha/prendas/{archivo}.png",
                    "ancla": ancla,
                    "desplazamiento": [dx, dy],
                    "delante": delante,
                })
            entrada["piezas"][direccion] = lista
        catalogo[clave] = entrada
    os.makedirs(os.path.join(raiz, "datos"), exist_ok=True)
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(catalogo, f, indent=1, ensure_ascii=False)
    print("Prendas dibujadas en", carpeta)
