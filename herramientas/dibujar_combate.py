"""
ARTE DE COMBATE dibujado píxel a píxel (paleta oficial de Raíz).

Uso:  python3 herramientas/dibujar_combate.py
Genera en arte/:
  personajes/maisha/prendas/cetro_raiz.png   el cetro-rama (se cuelga de la mano como una prenda)
  efectos/semilla.png                        semilla: 2 fotogramas (normal, a punto de estallar)
  efectos/explosion.png                      explosión de una casilla: 5 fotogramas de 16x16
  efectos/brote.png                          brotes que deja la explosión: 2 fotogramas de 16x16
  interfaz/hoja_vida.png                     hoja de vida del HUD: llena y vacía (9x8)
Los Petrinos, el Corazón de Giza y las raíces-espina están en herramientas/dibujar_zona.py.
"""
import math
import os
from PIL import Image

COLORES = {
    # Piedra
    "k": "292C25", "1": "525649", "2": "7A806D", "3": "A0A596",
    # Giza
    "z": "1A0D24", "Z": "3A1650", "p": "6B2A8F", "P": "A855D6",
    # Madera
    "m": "251812", "M": "6D4534", "L": "905C45",
    # Brote y Follaje
    "g": "6FCF4F", "G": "3E9A35", "d": "355029",
    # Corazón, Maisha y blancos
    "a": "E6A852", "A": "DF9022", "w": "FFF8E8", "l": "FFF3C4", "b": "FFE08A", "s": "E8B860",
    # Cobre (semilla)
    "q": "3D3214", "c": "A37036", "C": "C68756",
}


def a_imagen(filas):
    ancho = len(filas[0])
    for i, f in enumerate(filas):
        assert len(f) == ancho, f"fila {i} mide {len(f)} y debería medir {ancho}: {f}"
    img = Image.new("RGBA", (ancho, len(filas)), (0, 0, 0, 0))
    for y, fila in enumerate(filas):
        for x, ch in enumerate(fila):
            if ch != ".":
                c = COLORES[ch]
                img.putpixel((x, y), tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    return img


def tira(imagenes):
    w, h = imagenes[0].size
    hoja = Image.new("RGBA", (w * len(imagenes), h), (0, 0, 0, 0))
    for i, im in enumerate(imagenes):
        hoja.paste(im, (i * w, 0))
    return hoja


def silueta_blanca(img):
    """Fotograma de «golpeado»: la figura en blanco con su contorno."""
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) not in ((0x29, 0x2C, 0x25), (0x1A, 0x0D, 0x24), (0x25, 0x18, 0x12)):
                px[x, y] = (0xFF, 0xF8, 0xE8, 255)
    return out


# ---------------------------------------------------------------------------
# CETRO-RAMA de Maisha (7x18). La mano lo agarra en la fila 13, columna 3.
# ---------------------------------------------------------------------------
CETRO = [
    "g.....g",
    "Gg...gG",
    ".Gg.gG.",
    "..mmm..",
    ".maAam.",
    ".mAwam.",
    ".maAam.",
    "..mmm..",
    "..mLm..",
    "..mMm..",
    "..gMm..",
    "..mGg..",
    "..mMm..",
    "..mLm..",
    "..mMm..",
    "..mMg..",
    "..mMm..",
    "...m...",
]
CETRO_AGARRE = (3, 13)

# ---------------------------------------------------------------------------
# PETRINO: criatura de piedra corrompida por Giza (16x14)
# ---------------------------------------------------------------------------
PETRINO = [
    "................",
    "................",
    ".....kkkkkk.....",
    "...kk333222kk...",
    "..k3332222221k..",
    ".k332222222211k.",
    ".k32PZ2222PZ21k.",
    ".k32ZZ2222ZZ21k.",
    "k3222222p2222211",
    "k222222pp222211k",
    "k22222222p221111",
    "k1222222222111k.",
    ".k11111111111k..",
    "..kkkkkkkkkkk...",
]
PETRINO = [f if f.endswith("k") or f.endswith(".") else f[:-1] + "k" for f in PETRINO]


def aclarar(filas):
    """Sube un tono la piedra (1→2, 2→3, 3→blanco cálido) y enciende las vetas de Giza,
    para que el Petrino destaque sobre el suelo gris de la zona corrupta."""
    tabla = str.maketrans({"1": "2", "2": "3", "3": "l", "p": "P"})
    return [f.translate(tabla) for f in filas]
PETRINO_APLASTADO = [
    "................",
    "................",
    "................",
    "....kkkkkkkk....",
    "..kk3333222kkk..",
    ".k33322222222k..",
    "k332PZ2222PZ211k",
    "k322ZZ2222ZZ221k",
    "k2222222p222211k",
    "k222222pp222211k",
    "k22222222p22111k",
    "k11222222221111k",
    ".k111111111111k.",
    "..kkkkkkkkkkkk..",
]

# ---------------------------------------------------------------------------
# NÚCLEO DE GIZA: cristal violeta sobre una base de piedra (12x18)
# ---------------------------------------------------------------------------
NUCLEO = [
    ".....zz.....",
    "....zPPz....",
    "....zPwz....",
    "...zPPpz....",
    "...zPwPpz...",
    "..zPPPppZz..",
    "..zPwPpppz..",
    "..zPPPppZz..",
    "...zPPpZz...",
    "...zPppZz...",
    "....zpZz....",
    "....zpZz....",
    "..kk1zz1kk..",
    ".k3322211k..",
    "k332222211k.",
    "k22222221111",
    ".k1111111kk.",
    "..kkkkkkk...",
]
NUCLEO[15] = "k222222211k."
GRIETAS_1 = {(5, 3): "l", (5, 4): "z", (6, 5): "l", (6, 6): "z", (7, 7): "l"}
GRIETAS_2 = {**GRIETAS_1, (4, 6): "l", (4, 7): "z", (5, 8): "l", (5, 9): "z", (6, 10): "l", (7, 5): "z", (8, 6): "l"}


def con_grietas(filas, grietas):
    filas = [list(f) for f in filas]
    for (x, y), ch in grietas.items():
        if filas[y][x] != ".":
            filas[y][x] = ch
    return ["".join(f) for f in filas]


# ---------------------------------------------------------------------------
# SEMILLA (8x8): normal y brillando antes de estallar
# ---------------------------------------------------------------------------
SEMILLA = [
    "....gG..",
    "...gG...",
    "..qqqq..",
    ".qcCCcq.",
    ".qcCccq.",
    ".qccccq.",
    "..qqqq..",
    "........",
]
SEMILLA_BRILLA = [f.replace("C", "w").replace("c", "a") for f in SEMILLA]

# ---------------------------------------------------------------------------
# BROTES que deja la explosión (16x16): dos fotogramas para que se mezan
# ---------------------------------------------------------------------------
BROTE_A = [
    "................",
    "................",
    "................",
    "....g......g....",
    "...gG.g...Gg....",
    "....G.Gg..G.....",
    "....G.G...G.g...",
    ".g..dGd..dGdG...",
    "gG...........g..",
    ".G..g.....g..G..",
    ".G.gG.g..gG..G..",
    "dGd.G.G...Gg.Gd.",
    "...dGdGd.dGd....",
    "................",
    "................",
    "................",
]
BROTE_B = [
    "................",
    "................",
    "................",
    ".....g......g...",
    "...gG.g....Gg...",
    "....G.Gg..G.....",
    "....G.G...G..g..",
    "..g.dGd..dGdG...",
    ".gG...........g.",
    ".G...g....g..G..",
    ".G..gG.g.gG..G..",
    "dGd..G.G..Gg.Gd.",
    "...dGdGd.dGd....",
    "................",
    "................",
    "................",
]


# ---------------------------------------------------------------------------
# EXPLOSIÓN de una casilla (16x16, 5 fotogramas): destello de vida que se abre en hojas
# ---------------------------------------------------------------------------
def explosion():
    fotos = []
    hexa = lambda c: tuple(int(COLORES[c][i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    for f in range(5):
        im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        r_in, r_out = [(0, 3), (0, 6), (3, 7.5), (5, 8), (6, 8)][f]
        for y in range(16):
            for x in range(16):
                d = math.hypot(x - 7.5, y - 7.5)
                if r_in <= d <= r_out:
                    if f == 0:
                        c = "w"
                    elif f == 1:
                        c = "w" if d < 3 else ("l" if d < 5 else "b")
                    elif f == 2:
                        c = "l" if d < 5.5 else "b"
                    elif f == 3:
                        c = "b" if (x + y) % 2 == 0 else "."
                    else:
                        c = "."
                    if c != ".":
                        im.putpixel((x, y), hexa(c))
        # hojas que salen despedidas
        if f >= 2:
            dist = [0, 0, 5, 6.5, 7.5][f]
            for k in range(6):
                ang = math.radians(k * 60 + 30)
                x = int(round(7.5 + dist * math.cos(ang)))
                y = int(round(7.5 + dist * math.sin(ang)))
                for dx, dy, c in ((0, 0, "g"), (1, 0, "G"), (0, 1, "G")):
                    if 0 <= x + dx < 16 and 0 <= y + dy < 16:
                        im.putpixel((x + dx, y + dy), hexa(c))
        fotos.append(im)
    return fotos


# ---------------------------------------------------------------------------
# ESPINAS DE GIZA del umbral (8x14): de bajas a altas en 4 fotogramas
# ---------------------------------------------------------------------------
def espinas():
    altos = [4, 7, 10, 14]
    fotos = []
    for alto in altos:
        filas = [["."] * 8 for _ in range(14)]
        base = 13
        # espina principal (centro) y una lateral más baja
        for j in range(alto):
            y = base - j
            ancho = max(0, (alto - j) * 3 // alto)   # se estrecha hacia la punta
            for x in range(3 - ancho, 5 + ancho):
                if 0 <= x < 8:
                    filas[y][x] = "Z"
            filas[y][3 - ancho] = "z"
            filas[y][min(7, 4 + ancho)] = "z"
            if j >= alto - 2:
                filas[y][3] = "p" if j == alto - 2 else "P"
                filas[y][4] = "z"
        lateral = alto // 2
        for j in range(lateral):
            y = base - j
            x = 6 if j < lateral - 1 else 7
            filas[y][x] = "Z" if j < lateral - 1 else "p"
            if x + 1 < 8:
                filas[y][x + 1] = "z" if j < lateral - 1 else filas[y][x + 1]
        # base de piedra
        for x in range(1, 7):
            filas[base][x] = "1" if x % 2 else "k"
        fotos.append(a_imagen(["".join(f) for f in filas]))
    return fotos


# ---------------------------------------------------------------------------
# HOJA DE VIDA para el HUD (9x8): llena y vacía
# ---------------------------------------------------------------------------
HOJA_LLENA = [
    "....kkk..",
    "..kkggGk.",
    ".kgggGGk.",
    "kggGGGdk.",
    "kgGGGddk.",
    "kGGdddk..",
    ".kkkkk...",
    "k........",
]
HOJA_LLENA = [f.replace("k", "m") for f in HOJA_LLENA]
HOJA_VACIA = [f.replace("g", "d").replace("G", "d") for f in HOJA_LLENA]


if __name__ == "__main__":
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    arte = os.path.join(raiz, "arte")
    for sub in ("personajes/maisha/prendas", "efectos", "interfaz"):
        os.makedirs(os.path.join(arte, sub), exist_ok=True)

    a_imagen(CETRO).save(os.path.join(arte, "personajes/maisha/prendas/cetro_raiz.png"))
    tira([a_imagen(SEMILLA), a_imagen(SEMILLA_BRILLA)]).save(os.path.join(arte, "efectos/semilla.png"))
    tira(explosion()).save(os.path.join(arte, "efectos/explosion.png"))
    tira([a_imagen(BROTE_A), a_imagen(BROTE_B)]).save(os.path.join(arte, "efectos/brote.png"))
    tira([a_imagen(HOJA_LLENA), a_imagen(HOJA_VACIA)]).save(os.path.join(arte, "interfaz/hoja_vida.png"))
    print("Arte de combate dibujado en", arte)
