"""
MAISHA dibujada píxel a píxel (24x32 por fotograma).

Cada letra es un píxel con un color de la paleta oficial de Raíz.
Maisha está montada por PIEZAS (brote, cabeza, cuerpo, brazos, piernas) que se colocan
con pequeños desplazamientos en cada fotograma. Así cada animación reutiliza el mismo dibujo
y todas quedan coherentes.

Uso:  python3 herramientas/dibujar_maisha.py
Genera en arte/personajes/maisha/:
  maisha_base_{frente,espalda,perfil}.png       (un fotograma, la hoja de modelo)
  maisha_reposo_{abajo,arriba,lado}.png          (4 fotogramas en fila)
  maisha_andar_{abajo,arriba,lado}.png           (4 fotogramas en fila)
"""
import os
from PIL import Image

ANCHO, ALTO = 24, 32

COLORES = {
    "o": "7A4A2A",  # contorno
    "s": "E8B860",  # sombra
    "b": "FFE08A",  # base
    "l": "FFF3C4",  # luz
    "e": "140E18",  # ojo
    "w": "FFF8E8",  # brillo
    "r": "DE6771",  # rubor (Flor roja 3)
    "g": "6FCF4F",  # hoja
    "G": "3E9A35",  # tallo y sombra de hoja
    "a": "E6A852",  # corazón claro (Flor ámbar 3)
    "A": "DF9022",  # corazón oscuro (Flor ámbar 2)
}
# "." = transparente


# ---------------------------------------------------------------------------
# PIEZAS. Cada pieza es una lista de filas; se pega en (x, y) del lienzo 24x32.
# ---------------------------------------------------------------------------

# --- Brote (frente y espalda): dos posiciones para que se mezca ---
BROTE_A = [
    "........ggg.",
    "gg...gggg...",
    ".ggg.Gg.....",
    "...ggG......",
    ".....G......",
]
BROTE_B = [
    ".........gg.",
    ".g...ggggg..",
    "gggg.Gg.....",
    "...ggG......",
    ".....G......",
]

# --- Brote de perfil ---
BROTE_PERFIL_A = [
    "......ggg..",
    "g...gggg...",
    ".gg.Gg.....",
    "...gG......",
    "....G......",
]
BROTE_PERFIL_B = [
    ".......gg..",
    "....ggggg..",
    "ggg.Gg.....",
    "...gG......",
    "....G......",
]

# --- Cabezas (filas 5 a 19 del lienzo) ---
CABEZA_FRENTE = [
    "....oooGoooo....",
    "..oollllbbbboo..",
    ".ollllllbbbbbbo.",
    "ollllllbbbbbbbso",
    "olllllbbbbbbbbso",
    "ollllbbbbbbbbbso",
    "olbbwebbbbwebbso",
    "obbbeebbbbeebbso",
    "obbbeebbbbeebbso",
    "obbrbbbbbbbbrsso",
    "osbbbbbbbbbbbsso",
    "ossbbbbbbbbbbsso",
    ".ossbbbbbbbbsso.",
    "..oossssssssoo..",
    "....oooooooo....",
]
CABEZA_ESPALDA = list(CABEZA_FRENTE)
CABEZA_ESPALDA[6] = "olbbbbbbbbbbbbso"
CABEZA_ESPALDA[7] = "obbbbbbbbbbbbbso"
CABEZA_ESPALDA[8] = "obbbbbbllbbbbbso"   # pequeño reflejo en la nuca
CABEZA_ESPALDA[9] = "obbbbbblbbbbbsso"

CABEZA_PERFIL = [
    "....oooGoooo....",
    "..oollllbbbboo..",
    ".ollllllbbbbbbo.",
    "ollllllbbbbbbbso",
    "olllllbbbbbbbbso",
    "ollllbbbbbbbbbso",
    "olbbbbbbbbbbwebo",
    "obbbbbbbbbbbeebo",
    "obbbbbbbbbbbeebo",
    "obbbbbbbbbbbbbro",
    "osbbbbbbbbbbbsso",
    "ossbbbbbbbbbbsso",
    ".ossbbbbbbbbsso.",
    "..oossssssssoo..",
    "....oooooooo....",
]

# --- Cuerpos (sin brazos). Filas 20 a 28; la última es el contorno de la entrepierna ---
CUERPO_FRENTE = [
    "ollbbbbbso",
    "ollbbbbbso",
    "olbbwabbso",
    "obbbaAbbso",
    "obbbbbbbso",
    "obbbbbbsso",
    "obbbbbbsso",
    "osbbbbbsso",
    "oooooooooo",
]
CUERPO_FRENTE_LATE = list(CUERPO_FRENTE)   # el corazón brilla un instante
CUERPO_FRENTE_LATE[2] = "olbbwwbbso"
CUERPO_FRENTE_LATE[3] = "obbbwabbso"

CUERPO_ESPALDA = [
    "ollbbbbbso",
    "ollbbbbbso",
    "olbbbbbbso",
    "obbbbbbbso",
    "obbbbbbbso",
    "obbbbbbsso",
    "obbbbbbsso",
    "osbbbbbsso",
    "oooooooooo",
]

# Cuerpo de perfil (12 de ancho: deja sitio a la mano cuando sale de la silueta)
CUERPO_PERFIL = [
    ".olbbbbbbso.",
    ".olbbbbbbao.",
    ".olbbbbbsso.",
    ".olbbbbbsso.",
    ".obbbbbbsso.",
    ".obbbbbbsso.",
    ".osbbbbssso.",
    "..osssssso..",
]
CUERPO_PERFIL_LATE = list(CUERPO_PERFIL)
CUERPO_PERFIL_LATE[1] = ".olbbbbbbwo."
CUERPO_PERFIL_LATE[2] = ".olbbbbbbao."
# Brazo de perfil: se dibuja encima del cuerpo. Dentro de la silueta se separa con tonos de
# sombra (sin contorno cerrado, para que no parezca un aro); la mano lleva contorno solo
# cuando asoma fuera del cuerpo. (columna dentro del cuerpo, dibujo)
# (columna dentro del cuerpo, dibujo, posición de la mano dentro del dibujo)
BRAZO_PERFIL_QUIETO = (4, [
    "sl..",
    "slb.",
    "sbbs",
    ".ss.",
], (1, 3))
# Al andar, el brazo solo se mece 1 píxel (con el cetro en la mano, un balanceo grande
# hace que el cetro dé saltos). Las poses grandes quedan para el golpe.
BRAZO_PERFIL_PASO_DELANTE = (5, BRAZO_PERFIL_QUIETO[1], BRAZO_PERFIL_QUIETO[2])
BRAZO_PERFIL_PASO_DETRAS = (3, BRAZO_PERFIL_QUIETO[1], BRAZO_PERFIL_QUIETO[2])
BRAZO_PERFIL_DELANTE = (6, [   # la mano se adelanta y asoma por delante
    "sl....",
    ".slb..",
    "..slbo",
    "..sbbo",
    "...oo.",
], (3, 3))
BRAZO_PERFIL_DETRAS = (0, [    # la mano va hacia atrás y asoma por la espalda
    "....ls",
    "...lbs",
    "olbbs.",
    "obbs..",
    ".oo...",
], (1, 3))

# --- Brazos de frente (se pegan a los lados del cuerpo, filas 21 a 26) ---
BRAZO_IZQ = [
    "oooo",
    "olbo",
    "olbo",
    "obbo",
    "osso",
    ".ooo",
]
BRAZO_DER = [
    "oooo",
    "obso",
    "obso",
    "osso",
    "osso",
    "ooo.",
]

# --- Piernas de frente: 4 filas (de pie) o 3 (cuerpo agachado al pisar) ---
PIERNA_FRENTE_IZQ = ["osso", "olbo", "obbo", "oooo"]
PIERNA_FRENTE_DER = ["osso", "obso", "obso", "oooo"]
PIERNA_FRENTE_IZQ_PISA = ["osso", "olbo", "oooo"]
PIERNA_FRENTE_DER_PISA = ["osso", "obso", "oooo"]
PIERNA_FRENTE_IZQ_ALZA = ["osso", "oooo"]
PIERNA_FRENTE_DER_ALZA = ["osso", "oooo"]

# --- Piernas de perfil: se dibujan juntas como un bloque, desde la fila 28 ---
#     la pierna lejana va en sombra (s) y la cercana en luz (b, l)
PIERNAS_PERFIL_QUIETO = [
    "ossooobbo.",
    "osso.olbbo",
    "osso.obsso",
    "oooo.ooooo",
]
# Zancada (el cuerpo baja 1 píxel, por eso solo 3 filas)
PIERNAS_PERFIL_ZANCADA_CERCA = [   # la pierna cercana delante
    "..ossobbo...",
    ".osso..olbbo",
    "oooo...ooooo",
]
PIERNAS_PERFIL_ZANCADA_LEJOS = [   # la pierna lejana delante
    "..obbosso...",
    ".olbo..ossso",
    "oooo...ooooo",
]
# Paso intermedio (piernas juntas: una apoyada y la otra levantada)
PIERNAS_PERFIL_PASO_CERCA = [      # apoya la cercana; la lejana pasa por detrás
    "..osobbo.",
    "..osolbo.",
    "..ooolbbo",
    "....ooooo",
]
PIERNAS_PERFIL_PASO_LEJOS = [      # apoya la lejana; la cercana va levantada
    "..osobbo.",
    "..osolbbo",
    "..ossoooo",
    "..ooooo..",
]
# Instante en el aire al correr de perfil (ambas piernas recogidas, 3 filas con dy=-1 -> despegan 2 px del suelo)
PIERNAS_PERFIL_AIRE_CERCA = [
    ".ossobbo..",
    ".ossoolbbo",
    "..oooooooo",
]
PIERNAS_PERFIL_AIRE_LEJOS = [
    ".obbosso..",
    ".olboossso",
    "..oooooooo",
]


# ---------------------------------------------------------------------------
# MONTAJE
# ---------------------------------------------------------------------------

class Lienzo(list):
    """Un fotograma: filas de letras + los PUNTOS DE ANCLAJE donde se cuelga la ropa."""
    anclas = None


def lienzo():
    l = Lienzo(["."] * ANCHO for _ in range(ALTO))
    l.anclas = {}
    return l


def pegar(l, pieza, x, y):
    for j, fila in enumerate(pieza):
        for i, ch in enumerate(fila):
            if ch == ".":
                continue
            yy, xx = y + j, x + i
            if 0 <= yy < ALTO and 0 <= xx < ANCHO:
                l[yy][xx] = ch


def montar_frente(cabeza=CABEZA_FRENTE, cuerpo=CUERPO_FRENTE, brote=BROTE_A,
                  dy=0, dy_cabeza=0, brazo_izq=0, brazo_der=0,
                  pierna_izq=PIERNA_FRENTE_IZQ, pierna_der=PIERNA_FRENTE_DER, brazos_arriba=False):
    """dy: el cuerpo entero baja (al pisar). dy_cabeza: la cabeza baja aún más (respiración).
    brazo_izq/der: desplazamiento vertical de cada brazo (balanceo)."""
    l = lienzo()
    pegar(l, cuerpo, 7, 20 + dy)
    # piernas: empiezan justo bajo el cuerpo; una pierna "alzada" es más corta y no llega al suelo
    pegar(l, pierna_izq, 7, 28 + dy)
    pegar(l, pierna_der, 13, 28 + dy)
    if not brazos_arriba:
        pegar(l, BRAZO_IZQ, 4, 21 + dy + brazo_izq)
        pegar(l, BRAZO_DER, 16, 21 + dy + brazo_der)
    pegar(l, brote, 6, 0 + dy + dy_cabeza)
    pegar(l, cabeza, 4, 5 + dy + dy_cabeza)
    if brazos_arriba:
        pegar(l, BRAZO_IZQ_ARRIBA, 1, 13 + dy)
        pegar(l, BRAZO_DER_ARRIBA, 17, 13 + dy)
    # Anclajes (esquina superior izquierda de cada pieza) para la ropa por capas
    l.anclas = {
        "cabeza": [4, 5 + dy + dy_cabeza],
        "cuerpo": [7, 20 + dy],
        "brazo_izq": [4, 21 + dy + brazo_izq],
        "brazo_der": [16, 21 + dy + brazo_der],
        # mano derecha (de la pantalla): ahí va el cetro. Solo sigue el subir y bajar del cuerpo,
        # no el balanceo del brazo, para que el cetro se mueva limpio (como mucho 1 píxel)
        "mano": [21, 14 + dy] if brazos_arriba else [19, 25 + dy],
        "pie_izq": [7, 28 + dy + len(pierna_izq) - 1],
        "pie_der": [13, 28 + dy + len(pierna_der) - 1],
    }
    return l


def montar_perfil(cabeza=CABEZA_PERFIL, cuerpo=CUERPO_PERFIL, brote=BROTE_PERFIL_A, brazo=BRAZO_PERFIL_QUIETO,
                  dy=0, dy_cabeza=0, piernas=PIERNAS_PERFIL_QUIETO, piernas_x=8):
    l = lienzo()
    pegar(l, cuerpo, 6, 20 + dy)
    pegar(l, brazo[1], 6 + brazo[0], 22 + dy)
    pegar(l, piernas, piernas_x, 28 + dy)
    pegar(l, brote, 7, 0 + dy + dy_cabeza)
    pegar(l, cabeza, 4, 5 + dy + dy_cabeza)
    l.anclas = {
        "cabeza": [4, 5 + dy + dy_cabeza],
        "cuerpo": [6, 20 + dy],
        "brazo": [6 + brazo[0], 22 + dy],
        "mano": [6 + brazo[0] + brazo[2][0], 22 + dy + brazo[2][1]],
        "piernas": [piernas_x, 28 + dy],
    }
    return l


# ---------------------------------------------------------------------------
# ANIMACIONES (4 fotogramas cada una)
# ---------------------------------------------------------------------------

def reposo_abajo():
    # respira: la cabeza baja 1 píxel en los fotogramas 2 y 3; el brote se mece;
    # el corazón brilla en el 3; parpadea en el 4.
    return [
        montar_frente(),
        montar_frente(dy_cabeza=1, brote=BROTE_B),
        montar_frente(dy_cabeza=1, brote=BROTE_B, cuerpo=CUERPO_FRENTE_LATE),
        montar_frente(),
    ]


def reposo_arriba():
    return [
        montar_frente(cabeza=CABEZA_ESPALDA, cuerpo=CUERPO_ESPALDA),
        montar_frente(cabeza=CABEZA_ESPALDA, cuerpo=CUERPO_ESPALDA, dy_cabeza=1, brote=BROTE_B),
        montar_frente(cabeza=CABEZA_ESPALDA, cuerpo=CUERPO_ESPALDA, dy_cabeza=1, brote=BROTE_B),
        montar_frente(cabeza=CABEZA_ESPALDA, cuerpo=CUERPO_ESPALDA),
    ]


def reposo_lado():
    return [
        montar_perfil(),
        montar_perfil(dy_cabeza=1, brote=BROTE_PERFIL_B),
        montar_perfil(dy_cabeza=1, brote=BROTE_PERFIL_B, cuerpo=CUERPO_PERFIL_LATE),
        montar_perfil(),
    ]


def andar_frente(cabeza, cuerpo):
    return [
        # 1. pisa con la izquierda (de la pantalla): cuerpo abajo, pierna derecha alzada
        montar_frente(cabeza=cabeza, cuerpo=cuerpo, dy=1, brote=BROTE_A, brazo_der=1,
                      pierna_izq=PIERNA_FRENTE_IZQ_PISA, pierna_der=PIERNA_FRENTE_DER_ALZA),
        # 2. paso intermedio: cuerpo arriba, el brote se retrasa
        montar_frente(cabeza=cabeza, cuerpo=cuerpo, brote=BROTE_B),
        # 3. pisa con la derecha
        montar_frente(cabeza=cabeza, cuerpo=cuerpo, dy=1, brote=BROTE_A, brazo_izq=1,
                      pierna_izq=PIERNA_FRENTE_IZQ_ALZA, pierna_der=PIERNA_FRENTE_DER_PISA),
        # 4. paso intermedio
        montar_frente(cabeza=cabeza, cuerpo=cuerpo, brote=BROTE_B),
    ]


def andar_abajo():
    return andar_frente(CABEZA_FRENTE, CUERPO_FRENTE)


def andar_arriba():
    return andar_frente(CABEZA_ESPALDA, CUERPO_ESPALDA)


def andar_lado():
    return [
        # 1. zancada con la pierna cercana delante; el brazo cercano se mece un poco hacia atrás
        montar_perfil(dy=1, brote=BROTE_PERFIL_A, brazo=BRAZO_PERFIL_PASO_DETRAS,
                      piernas=PIERNAS_PERFIL_ZANCADA_CERCA, piernas_x=7),
        # 2. paso intermedio: cuerpo arriba, el brote se retrasa
        montar_perfil(brote=BROTE_PERFIL_B, piernas=PIERNAS_PERFIL_PASO_CERCA, piernas_x=7),
        # 3. zancada con la pierna lejana delante; el brazo cercano se mece un poco hacia delante
        montar_perfil(dy=1, brote=BROTE_PERFIL_A, brazo=BRAZO_PERFIL_PASO_DELANTE,
                      piernas=PIERNAS_PERFIL_ZANCADA_LEJOS, piernas_x=7),
        # 4. paso intermedio
        montar_perfil(brote=BROTE_PERFIL_B, piernas=PIERNAS_PERFIL_PASO_LEJOS, piernas_x=7),
    ]


def golpe_frente(cabeza, cuerpo):
    return [
        # 1. coge impulso: el brazo del cetro sube
        montar_frente(cabeza=cabeza, cuerpo=cuerpo, brazo_der=-2),
        # 2. golpe: el cuerpo se inclina y el brazo baja
        montar_frente(cabeza=cabeza, cuerpo=cuerpo, dy=1, brazo_der=1, brote=BROTE_B,
                      pierna_izq=PIERNA_FRENTE_IZQ_PISA, pierna_der=PIERNA_FRENTE_DER_PISA),
        # 3. recupera
        montar_frente(cabeza=cabeza, cuerpo=cuerpo, dy=1, brote=BROTE_A,
                      pierna_izq=PIERNA_FRENTE_IZQ_PISA, pierna_der=PIERNA_FRENTE_DER_PISA),
    ]


def golpe_abajo():
    return golpe_frente(CABEZA_FRENTE, CUERPO_FRENTE)


def golpe_arriba():
    return golpe_frente(CABEZA_ESPALDA, CUERPO_ESPALDA)


def golpe_lado():
    return [
        montar_perfil(brazo=BRAZO_PERFIL_DETRAS, brote=BROTE_PERFIL_A),
        montar_perfil(dy=1, brazo=BRAZO_PERFIL_DELANTE, brote=BROTE_PERFIL_B,
                      piernas=PIERNAS_PERFIL_ZANCADA_CERCA, piernas_x=7),
        montar_perfil(dy=1, brazo=BRAZO_PERFIL_DELANTE, brote=BROTE_PERFIL_A,
                      piernas=PIERNAS_PERFIL_ZANCADA_CERCA, piernas_x=7),
    ]



# ---------------------------------------------------------------------------
# EXPRESIONES Y ANIMACIONES NUEVAS (correr, sorpresa, daño, celebrar, despertar)
# ---------------------------------------------------------------------------

def cara(cabeza, filas):
    """Una cabeza con otros ojos: filas = {número de fila: dibujo}."""
    c = list(cabeza)
    for i, f in filas.items():
        assert len(f) == 16, (i, f)
        c[i] = f
    return c


OJOS_GRANDES = {6: "olbweebbbweebbso", 7: "obbeeebbbeeebbso", 8: "obbeeebbbeeebbso"}
OJOS_CERRADOS = {6: "olbbbbbbbbbbbbso", 7: "obbbbbbbbbbbbbso", 8: "obbseesbbseesbso"}
OJOS_DANIO = {6: "olbebbbbbbbbebso", 7: "obbbebbbbbbebbso", 8: "obbebbbbbbbbebso"}
OJOS_FELICES = {6: "olbbebbbbbbebbso", 7: "obbebebbbbebebso", 8: "obbbbbbbbbbbbbso"}
CABEZA_SORPRESA = cara(CABEZA_FRENTE, OJOS_GRANDES)
CABEZA_DORMIDA = cara(CABEZA_FRENTE, OJOS_CERRADOS)
CABEZA_DANIO = cara(CABEZA_FRENTE, OJOS_DANIO)
CABEZA_FELIZ = cara(CABEZA_FRENTE, OJOS_FELICES)
CABEZA_PERFIL_DANIO = cara(CABEZA_PERFIL, {6: "olbbbbbbbbbbbebo", 7: "obbbbbbbbbbbebbo", 8: "obbbbbbbbbbbbebo"})

# el brote se pone de punta (sorpresa) o se cae (dormida)
BROTE_ERGUIDO = [
    "..gg...gg...",
    "...gg.gg....",
    "....gGg.....",
    ".....G......",
    ".....G......",
]
BROTE_CAIDO = [
    "............",
    "............",
    "............",
    "ggg..G......",
    ".gggGG......",
]

# brazos en alto (celebrar): se dibujan encima de la cabeza, por fuera
BRAZO_IZQ_ARRIBA = [
    ".oo...",
    "olbo..",
    "olbo..",
    "olbo..",
    "obbo..",
    "obbo..",
    "obso..",
    "osbooo",
    ".oobbo",
    "...ooo",
]
BRAZO_DER_ARRIBA = [
    "...oo.",
    "..obso",
    "..obso",
    "..obso",
    "..osso",
    "..osso",
    "..osso",
    "ooosso",
    "obsso.",
    "ooo...",
]

PIERNA_SENTADA_IZQ = ["obbo", "oooo"]
PIERNA_SENTADA_DER = ["osso", "oooo"]


def correr_frente(cabeza, cuerpo):
    # como andar, pero con un instante en el aire entre paso y paso y los brazos más sueltos
    return [
        montar_frente(cabeza=cabeza, cuerpo=cuerpo, dy=1, brote=BROTE_A, brazo_izq=-1, brazo_der=1,
                      pierna_izq=PIERNA_FRENTE_IZQ_PISA, pierna_der=PIERNA_FRENTE_DER_ALZA),
        montar_frente(cabeza=cabeza, cuerpo=cuerpo, dy=-1, brote=BROTE_B,
                      pierna_izq=PIERNA_FRENTE_IZQ_ALZA, pierna_der=PIERNA_FRENTE_DER_ALZA),
        montar_frente(cabeza=cabeza, cuerpo=cuerpo, dy=1, brote=BROTE_A, brazo_izq=1, brazo_der=-1,
                      pierna_izq=PIERNA_FRENTE_IZQ_ALZA, pierna_der=PIERNA_FRENTE_DER_PISA),
        montar_frente(cabeza=cabeza, cuerpo=cuerpo, dy=-1, brote=BROTE_B,
                      pierna_izq=PIERNA_FRENTE_IZQ_ALZA, pierna_der=PIERNA_FRENTE_DER_ALZA),
    ]


def correr_abajo():
    return correr_frente(CABEZA_FRENTE, CUERPO_FRENTE)


def correr_arriba():
    return correr_frente(CABEZA_ESPALDA, CUERPO_ESPALDA)


def correr_lado():
    return [
        montar_perfil(dy=1, brote=BROTE_PERFIL_A, brazo=BRAZO_PERFIL_PASO_DETRAS,
                      piernas=PIERNAS_PERFIL_ZANCADA_CERCA, piernas_x=7),
        montar_perfil(dy=-1, brote=BROTE_PERFIL_B, piernas=PIERNAS_PERFIL_AIRE_CERCA, piernas_x=7),
        montar_perfil(dy=1, brote=BROTE_PERFIL_A, brazo=BRAZO_PERFIL_PASO_DELANTE,
                      piernas=PIERNAS_PERFIL_ZANCADA_LEJOS, piernas_x=7),
        montar_perfil(dy=-1, brote=BROTE_PERFIL_B, piernas=PIERNAS_PERFIL_AIRE_LEJOS, piernas_x=7),
    ]


def sorpresa_abajo():
    # se le abren los ojos, da un saltito con el brote de punta y vuelve al suelo
    return [
        montar_frente(cabeza=CABEZA_SORPRESA, brote=BROTE_ERGUIDO),
        montar_frente(cabeza=CABEZA_SORPRESA, brote=BROTE_ERGUIDO, dy=-2, brazo_izq=-2, brazo_der=-2,
                      pierna_izq=PIERNA_FRENTE_IZQ_ALZA, pierna_der=PIERNA_FRENTE_DER_ALZA),
        montar_frente(cabeza=CABEZA_SORPRESA, brote=BROTE_ERGUIDO, dy=1,
                      pierna_izq=PIERNA_FRENTE_IZQ_PISA, pierna_der=PIERNA_FRENTE_DER_PISA),
        montar_frente(cabeza=CABEZA_SORPRESA, brote=BROTE_B),
    ]


def danio_abajo():
    return [
        montar_frente(cabeza=CABEZA_DANIO, brote=BROTE_B, dy=1, dy_cabeza=1, brazo_izq=-1, brazo_der=-1,
                      pierna_izq=PIERNA_FRENTE_IZQ_PISA, pierna_der=PIERNA_FRENTE_DER_PISA),
        montar_frente(cabeza=CABEZA_DANIO, brote=BROTE_A, dy=1,
                      pierna_izq=PIERNA_FRENTE_IZQ_PISA, pierna_der=PIERNA_FRENTE_DER_PISA),
    ]


def danio_arriba():
    return [
        montar_frente(cabeza=CABEZA_ESPALDA, cuerpo=CUERPO_ESPALDA, brote=BROTE_B, dy=1, dy_cabeza=1,
                      pierna_izq=PIERNA_FRENTE_IZQ_PISA, pierna_der=PIERNA_FRENTE_DER_PISA),
        montar_frente(cabeza=CABEZA_ESPALDA, cuerpo=CUERPO_ESPALDA, brote=BROTE_A, dy=1,
                      pierna_izq=PIERNA_FRENTE_IZQ_PISA, pierna_der=PIERNA_FRENTE_DER_PISA),
    ]


def danio_lado():
    return [
        montar_perfil(cabeza=CABEZA_PERFIL_DANIO, brote=BROTE_PERFIL_B, dy=1, dy_cabeza=1, brazo=BRAZO_PERFIL_DETRAS),
        montar_perfil(cabeza=CABEZA_PERFIL_DANIO, brote=BROTE_PERFIL_A, dy=1),
    ]


def celebrar_abajo():
    # los brazos (y el cetro) en alto, ojos de alegría y saltitos
    return [
        montar_frente(cabeza=CABEZA_FELIZ, brote=BROTE_ERGUIDO, brazos_arriba=True),
        montar_frente(cabeza=CABEZA_FELIZ, brote=BROTE_B, brazos_arriba=True, dy=-2,
                      pierna_izq=PIERNA_FRENTE_IZQ_ALZA, pierna_der=PIERNA_FRENTE_DER_ALZA),
        montar_frente(cabeza=CABEZA_FELIZ, brote=BROTE_ERGUIDO, brazos_arriba=True, dy=1,
                      pierna_izq=PIERNA_FRENTE_IZQ_PISA, pierna_der=PIERNA_FRENTE_DER_PISA),
        montar_frente(cabeza=CABEZA_FELIZ, brote=BROTE_A, brazos_arriba=True),
    ]


def despertar_abajo():
    # sentada en el suelo, dormida; abre los ojos; se pone de pie y se despereza
    return [
        montar_frente(cabeza=CABEZA_DORMIDA, brote=BROTE_CAIDO, dy=3, dy_cabeza=1,
                      pierna_izq=PIERNA_SENTADA_IZQ, pierna_der=PIERNA_SENTADA_DER),
        montar_frente(cabeza=CABEZA_FRENTE, brote=BROTE_B, dy=3,
                      pierna_izq=PIERNA_SENTADA_IZQ, pierna_der=PIERNA_SENTADA_DER),
        montar_frente(cabeza=CABEZA_DORMIDA, brote=BROTE_A, brazos_arriba=True, dy=0),
        montar_frente(cabeza=CABEZA_FRENTE, brote=BROTE_B),
    ]


# ---------------------------------------------------------------------------
# EXPORTAR
# ---------------------------------------------------------------------------

def a_imagen(l):
    img = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
    for y in range(ALTO):
        for x in range(ANCHO):
            ch = l[y][x]
            if ch != ".":
                c = COLORES[ch]
                img.putpixel((x, y), tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    return img


def hoja(fotogramas):
    img = Image.new("RGBA", (ANCHO * len(fotogramas), ALTO), (0, 0, 0, 0))
    for i, f in enumerate(fotogramas):
        img.paste(a_imagen(f), (i * ANCHO, 0))
    return img


# Velocidad (fotogramas por segundo) y duración relativa de cada fotograma
RITMO = {
    "reposo": (4.0, [2.0, 1.0, 1.0, 1.0]),   # respiración tranquila: 1,25 s por ciclo
    "andar": (8.0, [1.0, 1.0, 1.0, 1.0]),    # dos pasos cada medio segundo
    "golpe": (16.0, [1.0, 1.0, 2.0]),        # 0,25 s: impulso, golpe, recupera (no se repite)
    "correr": (12.0, [1.0, 1.0, 1.0, 1.0]),  # más rápido que andar, con un instante en el aire
    "sorpresa": (10.0, [1.0, 2.0, 1.0, 3.0]),
    "danio": (10.0, [1.0, 3.0]),
    "celebrar": (8.0, [2.0, 1.0, 1.0, 2.0]),
    "despertar": (3.0, [6.0, 3.0, 3.0, 2.0]),
}
SIN_BUCLE = ("golpe", "sorpresa", "danio", "despertar")


def escribir_anclajes(ruta):
    """Guarda en JSON los anclajes de cada fotograma de cada animación (los lee el juego)."""
    import json
    datos = {nombre: [f.anclas for f in fn()] for nombre, fn in ANIMACIONES.items()}
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=1)


def escribir_spriteframes(ruta):
    """Crea el recurso de Godot con todas las animaciones (se ve y se edita en el editor)."""
    ext, sub, anims = [], [], []
    for i, nombre in enumerate(ANIMACIONES, start=1):
        ext.append(f'[ext_resource type="Texture2D" path="res://arte/personajes/maisha/maisha_{nombre}.png" id="{i}"]')
        tipo = nombre.split("_")[0]
        fps, duraciones = RITMO[tipo]
        bucle = "false" if tipo in SIN_BUCLE else "true"
        fotos = []
        for f, dur in enumerate(duraciones):
            sid = f"{nombre}_{f}"
            sub.append(f'[sub_resource type="AtlasTexture" id="{sid}"]\natlas = ExtResource("{i}")\n'
                       f'region = Rect2({f * ANCHO}, 0, {ANCHO}, {ALTO})')
            fotos.append(f'{{"duration": {dur}, "texture": SubResource("{sid}")}}')
        anims.append(f'{{"frames": [{", ".join(fotos)}], "loop": {bucle}, "name": &"{nombre}", "speed": {fps}}}')
    texto = (f'[gd_resource type="SpriteFrames" load_steps={len(ext) + len(sub) + 1} format=3]\n\n'
             + "\n".join(ext) + "\n\n" + "\n\n".join(sub) + "\n\n[resource]\nanimations = ["
             + ", ".join(anims) + "]\n")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)


ANIMACIONES = {
    "reposo_abajo": reposo_abajo,
    "reposo_arriba": reposo_arriba,
    "reposo_lado": reposo_lado,
    "andar_abajo": andar_abajo,
    "andar_arriba": andar_arriba,
    "andar_lado": andar_lado,
    "golpe_abajo": golpe_abajo,
    "golpe_arriba": golpe_arriba,
    "golpe_lado": golpe_lado,
    "correr_abajo": correr_abajo,
    "correr_arriba": correr_arriba,
    "correr_lado": correr_lado,
    "sorpresa_abajo": sorpresa_abajo,
    "danio_abajo": danio_abajo,
    "danio_arriba": danio_arriba,
    "danio_lado": danio_lado,
    "celebrar_abajo": celebrar_abajo,
    "despertar_abajo": despertar_abajo,
}

if __name__ == "__main__":
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    destino = os.path.join(raiz, "arte", "personajes", "maisha")
    os.makedirs(destino, exist_ok=True)
    a_imagen(montar_frente()).save(os.path.join(destino, "maisha_base_frente.png"))
    a_imagen(montar_frente(cabeza=CABEZA_ESPALDA, cuerpo=CUERPO_ESPALDA)).save(
        os.path.join(destino, "maisha_base_espalda.png"))
    a_imagen(montar_perfil()).save(os.path.join(destino, "maisha_base_perfil.png"))
    for nombre, fn in ANIMACIONES.items():
        hoja(fn()).save(os.path.join(destino, f"maisha_{nombre}.png"))
    escribir_spriteframes(os.path.join(destino, "maisha_animaciones.tres"))
    os.makedirs(os.path.join(raiz, "datos"), exist_ok=True)
    escribir_anclajes(os.path.join(raiz, "datos", "maisha_anclajes.json"))
    print("Maisha dibujada en", destino)
