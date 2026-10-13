"""
ICONOS DE LAS PESTAÑAS DE LA MOCHILA (y de la rueda rápida), píxel a píxel.

Uso:  python3 herramientas/dibujar_pestanas.py
Genera arte/interfaz/pestanas.png: 6 iconos de 16×16 en fila
  0 Misiones (un pergamino con sello)   1 Objetos (la bolsa)   2 Habilidades (un brote de luz)
  3 Mapa (un mapa doblado)              4 Lazos (un corazón con un brote)
  5 Bestiario (una huella de garra)
Cada letra es un color; el borde oscuro se pone solo alrededor de lo dibujado.
"""
import os

import numpy as np
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BORDE = "#22160f"

COLORES = {
    # pergamino
    "P": "#f6e7bf", "p": "#e3c88e", "s": "#b8925c", "t": "#9c7650", "R": "#c9a56a", "r": "#8a6440",
    "c": "#b43a32", "C": "#e5614a",
    # bolsa
    "B": "#a8693c", "b": "#7d4a2a", "d": "#5a321d", "H": "#c98a52", "o": "#e6c06a", "g": "#5d9a3a", "G": "#8ac05a",
    # brote
    "L": "#b8e08a", "l": "#6fbf4a", "m": "#3e7f2f", "y": "#fff3c4", "Y": "#f9d36a", "w": "#7c5843",
    # mapa
    "M": "#efd9a6", "N": "#d4b47a", "n": "#b08a55", "v": "#6d9e4c", "a": "#5f9fb8", "x": "#c23b30",
    # lazos
    "K": "#f29bb0", "k": "#c9607d", "h": "#ffd7e0", "e": "#e6a852", "E": "#ffe2a0",
    # bestiario (una huella de garra con el brillo violeta de Giza)
    "Q": "#b9a6d6", "q": "#8a72b0", "j": "#5c4680", "z": "#e9dcff",
}

MISIONES = [
    "................",
    "................",
    "..RRRRRRRRRRR...",
    ".rPPPPPPPPPPPr..",
    "..RRRRRRRRRRR...",
    "...pPPPPPPPPp...",
    "...ptttttttPp...",
    "...pPPPPPPPPp...",
    "...ptttttPPPp...",
    "...pPPPPPPPPp...",
    "...ptttttttPp...",
    "...pPPPPPPccc...",
    "..RRRRRRRcCCcc..",
    ".rPPPPPPPPcCc...",
    "..RRRRRRRRRc....",
    "................",
]

OBJETOS = [
    "................",
    "......oo........",
    ".....o..o.oo....",
    "......oooo..o...",
    ".....bBBBb......",
    "....bHHHHBb.....",
    "...bHHBBBBBb....",
    "..bHHBBBBBBBb...",
    "..bHBBBBBBBBbG..",
    ".bHHBBBBBBBBbGg.",
    ".bHBBBBBBBBBbg..",
    ".bHBBBBBBBBbbd..",
    ".bBBBBBBBBBbd...",
    "..bbBBBBBbbdd...",
    "...dddddddd.....",
    "................",
]

HABILIDADES = [
    ".......y........",
    "......yYy.......",
    ".......y........",
    "...LL.....LL....",
    "..LlLL...LLlL...",
    "..LllLL.LLllL...",
    "...LllLlLllL....",
    "....LlllmllL....",
    ".....LLmmLL.....",
    ".......mm.......",
    ".......mm.......",
    "......mm........",
    "....wwmmww......",
    "...wwwwwwww.....",
    "....wwwwww......",
    "................",
]

MAPA = [
    "................",
    "................",
    "..MMMMNNNMMMMn..",
    "..MvvMNNNMMaMn..",
    "..MvvvNNNMaaMn..",
    "..MMvMNxNMaMMn..",
    "..MMMMNNxMMMMn..",
    "..MMxMNNNxMMMn..",
    "..MMMxNNNMxMMn..",
    "..MMMMxNNMMxMn..",
    "..MvMMNNNMMMxn..",
    "..MvvMNNNMMxxn..",
    "..MMMMNNNMMMMn..",
    "..nnnnnnnnnnnn..",
    "................",
    "................",
]

LAZOS = [
    "........lL......",
    ".......lLL......",
    "...KKK.m..KKK...",
    "..KhhKKmKKKKKK..",
    ".KhhKKKKKKKKKKk.",
    ".KhKKKKKKKKKKKk.",
    ".KKKKKKKKKKKKKk.",
    ".KKKKKKKKKKKKkk.",
    "..KKKKKKKKKKkk..",
    "...KKKKKKKKkk...",
    "....KKKKKKkk....",
    ".....KKKKkk.....",
    "......KKkk......",
    ".......kk.......",
    "................",
    "................",
]


BESTIARIO = [
    "................",
    "................",
    "...qq......qq...",
    "..qQQq....qQQq..",
    "..qzQq.qq.qzQq..",
    "...qq.qQQq.qq...",
    "......qzQq......",
    ".......qq.......",
    "....jjqqqqjj....",
    "...jqQQQQQQqj...",
    "..jqQzzQQQQQqj..",
    "..jqQzQQQQQQqj..",
    "..jqQQQQQQQQqj..",
    "...jqQQQQQQqj...",
    "....jjqqqqjj....",
    "................",
]


def icono(filas):
    alto, ancho = len(filas), len(filas[0])
    out = np.zeros((alto, ancho, 4), np.uint8)
    lleno = np.zeros((alto, ancho), bool)
    for y, fila in enumerate(filas):
        for x, ch in enumerate(fila):
            if ch in ". ":
                continue
            h = COLORES[ch].lstrip("#")
            out[y, x] = [int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255]
            lleno[y, x] = True
    # borde oscuro alrededor (4 vecinos)
    h = BORDE.lstrip("#")
    borde = [int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255]
    for y in range(alto):
        for x in range(ancho):
            if lleno[y, x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < ancho and 0 <= yy < alto and lleno[yy, xx]:
                    out[y, x] = borde
                    break
    return out


def main():
    tira = np.concatenate([icono(f) for f in (MISIONES, OBJETOS, HABILIDADES, MAPA, LAZOS, BESTIARIO)], axis=1)
    ruta = os.path.join(RAIZ, "arte", "interfaz", "pestanas.png")
    Image.fromarray(tira, "RGBA").save(ruta)
    print("guardado:", ruta)


if __name__ == "__main__":
    main()
