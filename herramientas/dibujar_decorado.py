"""EL DECORADO DEL SUELO: detalles pequeños que llenan la hierba (no estorban al andar).

    python3 herramientas/dibujar_decorado.py

Genera arte/mundos/raiz/objetos/decorado.png: una tira de piezas de 16×16, dibujadas píxel a píxel
(a este tamaño el pixel art hecho a mano se lee mejor que lo pintado). El juego las reparte por la
hierba con scripts/mundo/decorado.gd. Orden de las piezas (columna):
  0-1 hierba alta (2 fotogramas: se mece)     2 flores amarillas    3 flores rojas    4 flores blancas
  5 helecho    6 arbusto con bayas    7 tocón    8 setas    9 piedrecitas    10 trébol    11 rama caída
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
from pintar_granja import mapa_pixeles  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = {
    "k": "#1d2e18", "g": "#3f582f", "G": "#6a8246", "L": "#9aa95f", "l": "#bcc87e",
    "y": "#df9022", "Y": "#f9c94a", "r": "#b03a44", "R": "#e98378", "w": "#e8e2cc", "W": "#fffdf4",
    "o": "#df9022", "m": "#53392d", "M": "#7c5843", "n": "#a57559", "N": "#c79a78",
    "p": "#525649", "P": "#7a806d", "Q": "#a0a596", "b": "#6a3446", "B": "#c96d4f", "s": "#2b1e17",
}
P = [
    # 0 hierba alta
    ["................", "................", "................", "................", "................",
     "......l.........", "...L..L...l.....", "...L.GL..L......", "..LG.GL..L..L...", "..GG.G.LGG..L...",
     ".kGG.GkLGkGGL...", ".kgG.gkGgkgG.k..", "..kgkgkgkgkgkk..", "...kk.kk.kk.....", "................", "................"],
    # 1 hierba alta, mecida
    ["................", "................", "................", "................", "................",
     ".......l........", "....L..L....l...", "....L.GL..L.....", "...GL.GL..L..L..", "...GG.G.LGG.L...",
     ".kGG.GkLGkGGL...", ".kgG.gkGgkgG.k..", "..kgkgkgkgkgkk..", "...kk.kk.kk.....", "................", "................"],
    # 2 flores amarillas
    ["................", "................", "................", "................", "................", "................",
     ".....Y..........", "....YoY...Y.....", ".....Y.G.YoY....", "..Y..G.G..Y.....", ".YoY.G..GG.G....",
     "..YGkG..G.kG....", "...GkgG.kgk.....", "....kk.kk.......", "................", "................"],
    # 3 flores rojas
    ["................", "................", "................", "................", "................", "................",
     "......R.........", ".....RrR..R.....", "......R.GRrR....", "..R...G.G.R.....", ".RrR..G..GG.G...",
     "..RGk.G..G.kG...", "...GkgG..kgk....", "....kk..kk......", "................", "................"],
    # 4 flores blancas
    ["................", "................", "................", "................", "................", "................",
     ".....W..........", "....WyW...W.....", ".....W.G.WyW....", "..W..G.G..W.....", ".WyW.G..GG.G....",
     "..WGkG..G.kG....", "...GkgG.kgk.....", "....kk.kk.......", "................", "................"],
    # 5 helecho
    ["................", "................", "................", "................", "......L.........",
     ".....LGL...l....", "..l.LG.GL.LL....", "..LLG.G..GL.L...", "...LGG.G.GGL....", ".LL.GGkGkGG.LL..",
     "..LGGkgGgkGGL...", "...kGgkgkgGk....", "....kkgkgkk.....", "......kkk.......", "................", "................"],
    # 6 arbusto con bayas
    ["................", "................", "................", "................", "................",
     ".....kkkkk......", "...kkGLGLGkk....", "..kGLGrGLGGGk...", "..kGGLGGGrLGk...", ".kGrGGGLGGGGGk..",
     ".kgGGrGGGGrGgk..", ".kggGGGgGGGggk..", "..kkggggggggk...", "....kkkkkkkk....", "................", "................"],
    # 7 tocón
    ["................", "................", "................", "................", "................",
     "................", "....mmmmmm......", "...mNNnnNNm.....", "...mNnMMnNm.....", "...MmNNNNmM.....",
     "...MMmmmmMM.....", "...MmMMMmMM.....", "..GMmMMMmMMG....", ".kgmMsMMMsMgk...", "..kssssssssk....", "................"],
    # 8 setas
    ["................", "................", "................", "................", "................", "................",
     "................", "....rRr.........", "...rRWRr..rRr...", "...rrrrr.rRWRr..", ".....w...rrrrr..",
     ".....w.....w....", "....kwk....w....", "...........wk...", "................", "................"],
    # 9 piedrecitas
    ["................", "................", "................", "................", "................", "................",
     "................", "................", "................", "....pP..........", "...pPQP...pP....",
     "...ppPP..pPQp...", "....pp...ppPp.P.", ".........kkk..pp", "................", "................"],
    # 10 trébol
    ["................", "................", "................", "................", "................", "................",
     "................", "................", "...LG.GL........", "..LGGkGGL.LG.GL.", "...LGkGL.LGGkGGL",
     "....kgk...LGkGL.", "..........kgk...", "................", "................", "................"],
    # 11 rama caída
    ["................", "................", "................", "................", "................", "................",
     "................", "................", "..........n.....", "........nNm.....", "..nNNNnnNNmm....",
     ".mNMMMMMMMMMm...", "..mmmmmmmmm..G..", "..........kGL...", "................", "................"],
]


def main():
    piezas = [mapa_pixeles(p, L) for p in P]
    tira = np.concatenate(piezas, axis=1)
    destino = os.path.join(RAIZ, "arte", "mundos", "raiz", "objetos", "decorado.png")
    Image.fromarray(tira, "RGBA").save(destino)
    print("Decorado dibujado:", destino, tira.shape[1], "×", tira.shape[0])


if __name__ == "__main__":
    main()
