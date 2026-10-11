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
}

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

PRENDAS = {
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
