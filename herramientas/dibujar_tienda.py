"""
LA TIENDA DE TAWI: iconos píxel a píxel (paleta de Raíz).

Uso:  python3 herramientas/dibujar_tienda.py
Añade a arte/interfaz/objetos.png (16×16 cada uno, detrás de los 11 que ya hay):
  11 corona de hojas   12 capa de musgo   13 sombrero de paja   14 mapa de los secretos
  15 semilla del olvido   16 cristal del Nexo   17 bayas y junco (el paquete de ingredientes)
Y arte/interfaz/cristal.png (8×10): el cristal pequeño para el HUD y la tienda.
(El retrato de Tawi y el fondo del puesto los pinta herramientas/pintar_tienda.py.)
"""
import os

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COL = {
    "k": "152814", "d": "355029", "m": "5D793E", "h": "90A153",            # follaje
    "q": "3D3214", "c": "A37036", "C": "C68756",                           # cobre
    "g": "6FCF4F", "G": "3E9A35",                                          # brote
    "o": "3D2A10", "p": "A37036", "P": "D29A43", "l": "EFC06A",            # paja
    "r": "8F2532", "R": "D5525E",                                          # cinta
    "w": "3B2416", "W": "A3794F", "y": "E3C391", "Y": "F3E0B8",            # pergamino
    "x": "1A0D24", "v": "6B2A8F", "V": "A855D6", "u": "DCAAF2",            # violeta (olvido, Giza)
    "b": "1E2038", "B": "335777", "n": "4A7A93", "N": "97C1BF", "s": "E8F0DC", "S": "FFFFFF",   # cristal
    "e": "2A0D3A", "f": "6B2A8F", "F": "A855D6",                           # bayas
    "j": "2F4422", "J": "9AA95F", "i": "C8C48A",                           # junco
    "t": "492E23", "T": "6D4534",                                          # cordel
}

CORONA = [
    "................",
    "................",
    "................",
    "................",
    ".k............k.",
    "khk....qq....khk",
    "kmhk..qCcq..khmk",
    "kmhhk.qqqq.khhmk",
    ".kmhhhhhhhhhhmk.",
    "..kmmmmmmmmmmk..",
    "...kkkkkkkkkk...",
    "................",
    "................",
    "................",
    "................",
    "................",
]
CAPA = [
    "................",
    ".....kkkkkk.....",
    "....kGGc.GGk....",
    "...kgGcCq.GGk...",
    "...kgG.q..GGk...",
    "..kgGG....GGdk..",
    "..kgGG....GGdk..",
    "..kgGGG..GGGdk..",
    ".kgGGGGGGGGGGdk.",
    ".kgGgGGGGGGGGdk.",
    ".kgGgGGGGGgGGdk.",
    ".kgGgGGGGGgGGdk.",
    "kgGGgGGGGGgGGGdk",
    "kgGgGGGGGGGgGGdk",
    "kkgkkgkkkgkkdkkk",
    "................",
]
SOMBRERO = [
    "................",
    "................",
    "................",
    "......oooo......",
    ".....olllPo.....",
    ".....olPPPpo....",
    ".....olPPPpo....",
    ".....orRRRro....",
    "...ooPPPPPPpoo..",
    "..ollPPPPPPPppo.",
    ".olPPPPPPPPPPppo",
    ".oPPPPPPPPPPPppo",
    "..oooooooooooooo",
    "................",
    "................",
    "................",
]
MAPA = [
    "................",
    "..wwwwwwwwwwww..",
    ".wYYyYYYYyYYYYw.",
    ".wYyYYhYYYYyYYw.",
    ".wYYYhhYYYRYyYw.",
    ".wYyYYYYYRRRYYw.",
    ".wYYYyYYYYRYYyw.",
    ".wYYWWWYYYYYYYw.",
    ".wYYYYWYYyYYRYw.",
    ".wYyYYWWYYYRRRw.",
    ".wYYYYYYWYYYRYw.",
    ".wYRYyYYYWYYYYw.",
    ".wRRRYYYYYWWYYw.",
    ".wYRYYyYYYYYYyw.",
    "..wwwwwwwwwwww..",
    "................",
]
OLVIDO = [
    "................",
    "................",
    ".......uu.......",
    "......uVVu......",
    ".....uVuuVu.....",
    "....xVVuVVVx....",
    "....xvVVVVvx....",
    "...xvVVuVVVvx...",
    "...xvVVVVVVvx...",
    "...xvvVVVVvvx...",
    "....xvvVVvvx....",
    "....xxvvvvxx....",
    "......xGGx......",
    ".......Gg.......",
    "......gG........",
    "................",
]
CRISTAL = [
    "................",
    ".......bb.......",
    "......bNsb......",
    ".....bNSsnb.....",
    ".....bNsNnb.....",
    "....bNSsNnBb....",
    "....bNsNnnBb....",
    "...bNSNsNnBBb...",
    "...bNsNNnnBBb...",
    "...bnNNNnnBBb...",
    "....bnNnnBBb....",
    "....bnnnnBBb....",
    ".....bnnBBb.....",
    "......bnBb......",
    ".......bb.......",
    "................",
]
INGREDIENTES = [
    "................",
    "..........ji....",
    ".........jJi....",
    "........jJi.....",
    "...ttt.jJi......",
    "..tT..TjJ.......",
    "..T.eeJjee......",
    "...efFfFFfe.....",
    "..efFFfFFFfe....",
    "..eFFufFuFFe....",
    "..efFFfFFFfe....",
    "...eefFfFee.....",
    ".....eeee.......",
    "................",
    "................",
    "................",
]
CRISTAL_HUD = [
    "...bb...",
    "..bNsb..",
    ".bNSsnb.",
    "bNsNnnBb",
    "bNSNnnBb",
    "bnNNnnBb",
    ".bnNnBb.",
    ".bnnnBb.",
    "..bnBb..",
    "...bb...",
]


def imagen(filas):
    w, h = max(len(f) for f in filas), len(filas)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y, f in enumerate(filas):
        for x, ch in enumerate(f):
            if ch != ".":
                col = COL[ch]
                img.putpixel((x, y), tuple(int(col[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    return img


def main():
    ruta = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    nuevos = [CORONA, CAPA, SOMBRERO, MAPA, OLVIDO, CRISTAL, INGREDIENTES]
    hoja = Image.new("RGBA", (16 * (11 + len(nuevos)), 16), (0, 0, 0, 0))
    hoja.alpha_composite(viejos.crop((0, 0, 16 * 11, 16)), (0, 0))
    for i, filas in enumerate(nuevos):
        hoja.alpha_composite(imagen(filas), (16 * (11 + i), 0))
    hoja.save(ruta)
    imagen(CRISTAL_HUD).save(os.path.join(RAIZ, "arte", "interfaz", "cristal.png"))
    print("Iconos de la tienda en", ruta, hoja.size)


if __name__ == "__main__":
    main()
