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
## Los cetros de los niveles del Arte del Cetro (12×20): la mano agarra en la columna 5, fila 11
AGARRE_CETRO_N = (-5, -11)


def cetro_nivel(n):
    """El cetro en el nivel n (1-6) del Arte del Cetro (12×20, la mano en la fila 11): 1 cinta verde · 2 gema más grande · 3 de CORTEZA DE ROBLE (más
    grueso, con nudos tallados) · 4 hojas de cobre · 5 gema dorada con chispas · 6 el CETRO DEL PRIMER ÁRBOL (dorado, con
    una corona de hojas y flores)."""
    img = Image.new("RGBA", (12, 20), (0, 0, 0, 0))
    def px(x, y, c):
        if 0 <= x < 12 and 0 <= y < 20:
            img.putpixel((x, y), tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    roble = n >= 3
    madera = ["3A2414", "5A3A20", "7E5430", "A07040"]
    if roble:
        madera = ["2A1608", "5A3418", "8A5A2A", "B07A3A"]
    if n >= 6:
        madera = ["5A3A08", "B08A2A", "F2D27A", "FFF0B0"]
    # el palo (más grueso desde el roble)
    for y in range(9, 20):
        px(4, y, madera[0]); px(5, y, madera[2] if y % 4 else madera[1]); px(6, y, madera[1])
        px(7, y, madera[0])
        if roble:
            px(3, y, madera[0]); px(4, y, madera[1])
    if roble:
        for y in (12, 16):
            px(5, y, madera[3]); px(4, y + 1, madera[0])                     # nudos tallados
    px(5, 19, madera[0]); px(6, 19, madera[0])
    if n >= 1:                                                               # la cinta verde, enroscada
        for (x, y, c) in ((4, 10, "3E9A35"), (5, 11, "6FCF4F"), (6, 11, "6FCF4F"), (7, 12, "3E9A35"), (8, 13, "6FCF4F"), (8, 14, "3E9A35")):
            px(x, y, c)
    # la gema (más grande desde el 2; dorada desde el 5)
    gema = ["8A3A0F", "EF8A26", "FDE27E"] if n < 5 else ["8A6A10", "F9D77A", "FFF8D0"]
    if n >= 2:
        for (x, y) in ((4, 5), (5, 4), (6, 4), (7, 5), (4, 6), (7, 6), (5, 7), (6, 7)):
            px(x, y, gema[0])
        for (x, y) in ((5, 5), (6, 5), (5, 6), (6, 6)):
            px(x, y, gema[1])
        px(5, 5, gema[2])
    else:
        for (x, y) in ((5, 5), (6, 5), (5, 6), (6, 6)):
            px(x, y, gema[1])
        px(5, 5, gema[2])
    for (x, y) in ((5, 8), (6, 8)):
        px(x, y, madera[1])
    # las hojitas de arriba (de cobre desde el 4)
    hoja = ["2F5A20", "6FCF4F"] if n < 4 else ["6A3418", "E0904E"]
    for (x, y, k) in ((3, 3, 1), (2, 2, 1), (4, 4, 0), (8, 3, 1), (9, 2, 1), (7, 4, 0)):
        px(x, y, hoja[k])
    if n >= 5:
        for (x, y) in ((1, 6), (10, 5), (9, 9), (2, 9)):
            px(x, y, "FDE27E")
    if n >= 6:
        for (x, y, c) in ((2, 1, "6FCF4F"), (3, 0, "8FE06A"), (5, 0, "6FCF4F"), (6, 0, "8FE06A"), (8, 0, "6FCF4F"), (9, 1, "8FE06A"),
                          (1, 3, "6FCF4F"), (10, 3, "6FCF4F"), (4, 0, "FFD7E0"), (7, 1, "FFD7E0"), (4, 1, "F9D36A")):
            px(x, y, c)
    return img

PRENDAS = {
    **{f"cetro_{n}": {
        "nombre": f"Cetro (Arte del Cetro {n})",
        "zona": "arma",
        "arte": "cetro",
        "piezas": {d: [(f"cetro_{n}", None, "mano", AGARRE_CETRO_N, True)] for d in ("abajo", "arriba", "lado")},
    } for n in range(1, 7)},
    "brazaletes_raiz": {
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
        for direccion, piezas in p["piezas"].items():
            lista = []
            for archivo, filas, ancla, (dx, dy), delante in piezas:
                if filas is not None:   # None = el dibujo lo genera otro programa (p. ej. el cetro)
                    a_imagen(filas).save(os.path.join(carpeta, archivo + ".png"))
                elif archivo.startswith("cetro_") and archivo[6:].isdigit():
                    cetro_nivel(int(archivo[6:])).save(os.path.join(carpeta, archivo + ".png"))
                lista.append({
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
