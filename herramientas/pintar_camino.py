"""LOS OBJETOS DEL CAMINO COBRIZO, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_camino.py

Genera:
  arte/mundos/raiz/camino/madriguera.png  72×58       la casa de Fuko, el topo minero: una loma con una puerta redonda
                                                      de madera (con su ventanuco), un farol de mina, una vagoneta con
                                                      mineral de cobre, un pico apoyado y, sobre la puerta, la cuerda de
                                                      las campanillas con tres ganchos vacíos
  arte/mundos/raiz/camino/topo.png        6 × 24×22   el TOPO DE PIEDRA (enemigo): asomando, fuera, mordiendo,
                                                      atontado, hundiéndose y golpeado (blanco en el juego)
  arte/mundos/raiz/camino/derrumbe.png    3 × 16×24   montones de piedras y maderos del derrumbe de la galería
  arte/mundos/raiz/objetos/campanilla.png 2 × 12×12   una campanilla de cobre de Fuko
  y su icono (16×16) en arte/interfaz/objetos.png (el 21.º)
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_casa_shamba import vetas, rect  # noqa: E402
from pintar_pasarelas import tira, pixeles, MADERA, GIZA, CONTORNO  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "camino")
LUZ = (-0.6, -0.7, 0.5)
TIERRA = ["#1d140f", "#2b1e17", "#3f2c21", "#533b2d", "#684937", "#7c5843", "#91674f", "#a57559"]
HIERBA = ["#141f10", "#1d2e18", "#2b4220", "#3f582f", "#526d38", "#6a8246", "#829856"]
PENA = ["#1e1915", "#2e2620", "#40352b", "#554737", "#6b5a45", "#837054", "#9c8765", "#b5a07c", "#cdbb98"]
COBRE = ["#3a1a0c", "#6a3418", "#9a4e24", "#c06a32", "#e0904e", "#f4b470", "#ffe0b0"]
HIERRO = ["#1a1a1c", "#2e2f33", "#45474d", "#5f626a", "#80838a", "#a5a8ae"]
# el topo: piedra gris azulada, con grietas de Giza (distinta del suelo y de la rana)
TOPO_P = ["#141416", "#222328", "#34363c", "#4a4c52", "#62646a", "#7c7e84", "#98999d", "#b6b6b8"]


def madriguera():
    """La madriguera de Fuko, el topo de las gafas (128×100, la base en el centro de abajo): una loma de tierra con
    hierba y hojas de cobre; la puerta redonda de tablas con herrajes de cobre; una ventanita redonda encendida; el
    tubo de la chimenea que asoma de la loma echando humo; el farol de mina; la cuerda con los tres ganchos (para las
    campanillas); la vagoneta en sus raíles con piedras de cobre que brillan; el pico y la pala; raíces y setas."""
    import pintar_aldea as pa
    W, H = 128, 92
    lz = pa._lienzo(W, H, 8, 91)
    suelo = 88
    cx = 58
    LUZ_ = (-0.6, -0.7, 0.5)
    lz.pintar(lz.desenfocar(lz.elipse(cx + 6, suelo, 60, 5), 2), "#0e0c0a", 0.45)
    # la loma: tierra con volumen, hierba encima y hojas de cobre caídas
    loma = lz.poligono([(cx - 52, suelo), (cx - 44, 50), (cx - 28, 26), (cx - 6, 16), (cx + 16, 18), (cx + 36, 30), (cx + 50, 54), (cx + 56, suelo)])
    lz.sombrear(loma, TIERRA, 14, LUZ_, textura=lz.ruido(1.0, 3, semilla=92), fuerza_tex=0.35)
    borde_h = 70 + (lz.ruido(3, 2, semilla=98) - 0.5) * 16
    hierba = loma * (lz.y < borde_h) * (1 - np.clip(1.25 - np.hypot(lz.x - cx, lz.y - 66) / 19, 0, 1) * 1.5).clip(0, 1)
    hierba = lz.desenfocar(hierba, 0.6)
    lz.sombrear(hierba, HIERBA, 6, LUZ_, textura=pa.vetas(lz, 0.4, 7, False, semilla=93), fuerza_tex=0.5)
    rng = np.random.default_rng(94)
    for k in range(40):
        x, y = cx - 46 + rng.random() * 98, 22 + rng.random() * 60
        if loma[int(y * lz.s), int(x * lz.s)] > 0.5:
            lz.sombrear(lz.elipse(x, y, 1.8, 1.0, rng.uniform(0, 180)), COBRE[1:5], 0.5, LUZ_)
    for k in range(5):                                                   # raíces que asoman de la loma
        x0 = cx - 40 + k * 18
        lz.sombrear(lz.trazo(lz.curva((x0, 60 + k % 2 * 8), (x0 + 5, 56), (x0 + 9, 64)), 1.2, 0.5), TIERRA[3:], 0.5, LUZ_)
    # el tubo de la chimenea, con humo
    lz.sombrear(pa.rect(lz, cx + 18, 4, cx + 23, 22), HIERRO, 1.2, LUZ_)
    lz.sombrear(pa.rect(lz, cx + 16.5, 2, cx + 24.5, 5), HIERRO[2:], 0.6, LUZ_)
    humo = np.zeros((lz.H, lz.W))
    for k in range(5):
        humo = np.maximum(humo, lz.circulo(cx + 21 + k * 2.4, -1 - k * 2.6, 2.4 + k * 0.7))
    lz.pintar(np.clip(lz.desenfocar(humo, 1.0) * 1.4, 0, 1), "#c8c4c0", 0.7)
    # el arco de piedra de la entrada y la puerta redonda de tablas
    arco = np.clip(lz.circulo(cx, 66, 17) - lz.circulo(cx, 66, 13), 0, 1) * (lz.y < suelo)
    dovelas = (np.abs(np.sin(np.arctan2(lz.y - 66, lz.x - cx) * 9)) < 0.15) * 1.0
    lz.sombrear(arco, PENA[2:], 1.5, LUZ_, textura=1 - dovelas * 0.7, fuerza_tex=0.6)
    pu = lz.circulo(cx, 66, 13) * (lz.y < suelo)
    tablas = (np.abs(np.sin((lz.x - cx) / 3.4 * np.pi)) < 0.1).astype(float)
    lz.sombrear(pu, ["#251812", "#3d2418", "#5a3826", "#7a4e35", "#9a6847"], 6, LUZ_, textura=pa.vetas(lz, 0.5, 13, False) * (1 - tablas * 0.8), fuerza_tex=0.45)
    for y in (60, 74):
        lz.sombrear(pa.rect(lz, cx - 12, y - 0.8, cx - 2, y + 0.8), COBRE[2:], 0.5, LUZ_)
    pomo = lz.circulo(cx + 6, 70, 1.6)
    lz.sombrear(pomo, COBRE[2:], 0.6, LUZ_)
    mirilla = lz.circulo(cx, 60, 2.6)
    lz.pintar(np.clip(lz.circulo(cx, 60, 3.4) - mirilla, 0, 1), COBRE[2])
    lz.pintar(mirilla, pa.rampa(["#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - cx, lz.y - 60) / 2.6, 0, 1)))
    # la ventanita redonda a la izquierda
    vx, vy = cx - 28, 58
    lz.sombrear(np.clip(lz.circulo(vx, vy, 6) - lz.circulo(vx, vy, 4.6), 0, 1), COBRE[1:], 0.8, LUZ_)
    vid = lz.circulo(vx, vy, 4.6)
    lz.pintar(vid, pa.rampa(["#a8380f", "#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - vx + 1, lz.y - vy + 1) / 4.6, 0, 1)))
    lz.pintar(np.maximum(pa.rect(lz, vx - 4.6, vy - 0.4, vx + 4.6, vy + 0.4), pa.rect(lz, vx - 0.4, vy - 4.6, vx + 0.4, vy + 4.6)) * vid, "#2a1a12")
    lz.sumar_luz(lz.desenfocar(vid, 3), "#ef8a26", 0.3)
    # la cuerda con los tres ganchos sobre la puerta
    lz.pintar(lz.trazo(lz.curva((cx - 16, 48), (cx, 52), (cx + 16, 48)), 0.6), "#80643c")
    for x in (cx - 8, cx, cx + 8):
        y = 50 + (2 if x == cx else 1)
        lz.pintar(lz.trazo([(x, y), (x, y + 3)], 0.4) + lz.trazo(lz.curva((x, y + 3), (x + 1.5, y + 5), (x - 0.5, y + 4.6)), 0.4), "#80838a")
    # el farol de mina, colgado de un poste a la derecha de la puerta
    lz.sombrear(lz.trazo([(cx + 22, suelo), (cx + 22, 52)], 1.2), MADERA[2:], 0.5, LUZ_)
    lz.sombrear(lz.trazo([(cx + 22, 53), (cx + 27, 53)], 0.9), MADERA[2:], 0.4, LUZ_)
    far = pa.rect(lz, cx + 25, 56, cx + 30, 63)
    lz.pintar(lz.trazo([(cx + 27.5, 53), (cx + 27.5, 56)], 0.4), "#2a2a2a")
    lz.pintar(far, pa.rampa(["#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - cx - 27.5, lz.y - 59.5) / 3.5, 0, 1)))
    lz.sombrear(pa.rect(lz, cx + 24.5, 55, cx + 30.5, 56.5) + pa.rect(lz, cx + 24.5, 62.5, cx + 30.5, 64), HIERRO, 0.4, LUZ_)
    lz.sumar_luz(lz.desenfocar(far, 5), "#ef8a26", 0.45)
    # la vagoneta en sus raíles, llena de piedras de cobre que brillan
    for y in (suelo - 1, suelo + 2):
        lz.pintar(lz.trazo([(cx + 32, y), (cx + 70, y)], 0.6), "#5f626a")
    for x in range(int(cx + 34), int(cx + 70), 5):
        lz.sombrear(pa.rect(lz, x, suelo - 2, x + 2, suelo + 3), MADERA[1:], 0.3, LUZ_)
    vag = lz.poligono([(cx + 38, 72), (cx + 60, 72), (cx + 57, 84), (cx + 41, 84)])
    lz.sombrear(vag, HIERRO, 2, LUZ_, textura=(lz.ruido(0.5, 2, semilla=96) > 0.6) * 1.0, fuerza_tex=0.3)
    lz.pintar(pa.rect(lz, cx + 38, 72, cx + 60, 73.2), HIERRO[4])
    for k in range(9):
        x = cx + 41 + (k % 5) * 4
        y = 70 - (k // 5) * 2.6 - (k % 2)
        p_ = lz.elipse(x, y, 2.4, 1.8, k * 30)
        lz.sombrear(p_, COBRE, 0.8, LUZ_)
        lz.brillo(p_, COBRE[5], 1.4, 0.4)
    for x in (cx + 43, cx + 55):
        lz.sombrear(lz.circulo(x, 85, 2.6), HIERRO, 0.6, LUZ_)
    # el pico y la pala apoyados en la loma, a la izquierda
    lz.sombrear(lz.trazo([(cx - 40, suelo), (cx - 34, 66)], 1.0), MADERA[2:], 0.4, LUZ_)
    lz.sombrear(lz.trazo(lz.curva((cx - 39, 66), (cx - 34, 63), (cx - 29, 66)), 1.2, 0.6), HIERRO, 0.4, LUZ_)
    lz.sombrear(lz.trazo([(cx - 46, suelo), (cx - 44, 68)], 1.0), MADERA[2:], 0.4, LUZ_)
    lz.sombrear(lz.elipse(cx - 46, suelo - 3, 2.4, 3.6), HIERRO, 0.6, LUZ_)
    # setas y hierba al pie
    for (x, r) in ((cx - 18, 2.4), (cx - 22, 1.6), (cx + 14, 2.0)):
        lz.sombrear(lz.trazo([(x, suelo), (x, suelo - r * 1.4)], r * 0.35), ["#8a7658", "#dcc8a0", "#f0e2c0"], 0.4, LUZ_)
        lz.sombrear(lz.elipse(x, suelo - r * 1.5, r, r * 0.6), COBRE[2:], 0.6, LUZ_)
    pa._hierba_pie(lz, cx - 54, cx + 68, suelo - 2, 97)
    return lz.sprite(contorno=0.4)


def topo(estado):
    """El TOPO DE PIEDRA: un topo de roca parda, gordo y sin cuello, con zarpas enormes de excavar (con uñas de
    cobre), hocico rosado, ojillos diminutos y grietas por las que corre la luz violeta de Giza.
    0 asoma (la cabeza y las zarpas salen del montón de tierra) · 1 fuera (de pie) · 2 muerde (se lanza, zarpas
    arriba y boca abierta) · 3 atontado (ojos en espiral, tambaleándose) · 4 se hunde (medio enterrado) · 5 golpeado."""
    W, H = 24, 22
    lz = Lienzo(W, H, s=8, semilla=101 + estado)
    suelo = 21
    hundido = {0: 3.5, 1: 0.0, 2: 0.0, 3: 0.0, 4: 5.5, 5: 0.0}[estado]
    sube = 1.5 if estado == 2 else 0.0
    cx, cy = 12, suelo - 7 - sube + hundido
    if estado in (1, 2, 3, 5):
        lz.pintar(lz.desenfocar(lz.elipse(12, suelo, 8, 1.6), 0.6), "#0e0c0a", 0.5)
    visible = lz.y < suelo - 1 + (0 if hundido == 0 else 0)
    # el cuerpo: un óvalo gordo
    cuerpo = lz.elipse(cx, cy, 7.5, 7.2) * visible
    lz.sombrear(cuerpo, TOPO_P[1:], 4, LUZ, textura=lz.ruido(0.9, 3, semilla=102), fuerza_tex=0.35,
                recorte=("#d8c8b0", 0.3), recorte_dir=(-1, -0.5))
    panza = lz.elipse(cx, cy + 2.5, 4.2, 3.6) * cuerpo
    lz.pintar(panza, TOPO_P[5], 0.6)
    # grietas de Giza
    for (pts, g) in (([(cx - 6, cy - 1), (cx - 4.5, cy + 1), (cx - 5.5, cy + 3)], 0.6), ([(cx + 5, cy - 5), (cx + 6, cy - 2.5), (cx + 5.5, cy)], 0.5)):
        gr = lz.trazo(pts, g) * cuerpo
        lz.pintar(gr, GIZA[1])
        lz.pintar(lz.trazo(pts, g * 0.5) * cuerpo, GIZA[3])
        lz.brillo(gr, GIZA[3], 1.2, 0.8)
    # las zarpas: palas anchas con uñas de cobre (arriba al morder)
    arriba = estado == 2
    for lado in (-1, 1):
        zx = cx + lado * (7.5 if not arriba else 6.5)
        zy = cy + (2.5 if not arriba else -5.5)
        if estado == 3:
            zy += 1.0 if lado < 0 else -1.0
        pala = lz.elipse(zx, zy, 2.8, 2.2, 30 * lado) * (lz.y < suelo - 1)
        lz.sombrear(pala, TOPO_P[2:7], 1.4, LUZ)
        for k in range(3):
            ux = zx + lado * 1.4 + (k - 1) * 1.1
            uy = zy + (2.2 if not arriba else -2.6)
            una = lz.trazo([(ux, zy + (0.8 if not arriba else -0.8)), (ux + lado * 0.4, uy)], 0.7, 0.3) * (lz.y < suelo - 1)
            lz.pintar(una, COBRE[4])
    # el hocico rosado y los bigotes
    hocico = lz.elipse(cx, cy - 1.0, 2.0, 1.5) * visible
    lz.sombrear(hocico, ["#6a2a34", "#a84a58", "#de6771", "#f0a0a8"], 1, LUZ)
    for lado in (-1, 1):
        lz.pintar(lz.trazo([(cx + lado * 1.8, cy - 0.6), (cx + lado * 5, cy - 1.6)], 0.25) * visible, "#d8c8b0", 0.7)
        lz.pintar(lz.trazo([(cx + lado * 1.8, cy - 0.2), (cx + lado * 5, cy + 0.4)], 0.25) * visible, "#d8c8b0", 0.7)
    # boca (abierta al morder) y ojillos (espiral si está atontado)
    if arriba:
        boca = lz.elipse(cx, cy + 1.6, 1.8, 1.4) * visible
        lz.pintar(boca, "#2a0d1a")
        lz.pintar(rect(lz, cx - 1.2, cy + 0.6, cx - 0.4, cy + 1.4) + rect(lz, cx + 0.4, cy + 0.6, cx + 1.2, cy + 1.4), "#f4ead8")
    for lado in (-1, 1):
        ox, oy = cx + lado * 3.0, cy - 3.6
        if estado in (3, 5):
            t = np.linspace(0, 3 * np.pi, 24)
            lz.pintar(lz.trazo([(ox + np.cos(a) * a * 0.11, oy + np.sin(a) * a * 0.11) for a in t], 0.35) * visible, GIZA[3])
        else:
            lz.pintar(lz.circulo(ox, oy, 0.8) * visible, "#140e18")
            lz.pintar(lz.circulo(ox, oy, 0.45) * visible, GIZA[3])
    # el montón de tierra (al asomar y al hundirse)
    if hundido:
        monton = lz.elipse(12, suelo - 1.5, 10, 4.2)
        lz.sombrear(monton, TIERRA[1:], 2.5, LUZ, textura=lz.ruido(0.7, 2, semilla=103), fuerza_tex=0.5)
        terrones = (lz.ruido(0.6, 1, semilla=104) > 0.75) * monton
        lz.pintar(terrones, TIERRA[6], 0.8)
    return lz.sprite(contorno=CONTORNO)


def derrumbe(k):
    """Un montón de piedras pardas (de la peña) y un madero roto de la entibación de la galería."""
    W, H = 16, 24
    lz = Lienzo(W, H, s=8, semilla=111 + k)
    rng = np.random.default_rng(112 + k)
    lz.pintar(lz.desenfocar(lz.elipse(8, 22, 8, 2), 0.6), "#0e0c0a", 0.6)
    piedras = sorted([(rng.random() * 12 + 2, 10 + rng.random() * 11, 2.6 + rng.random() * 2.6) for _ in range(7)], key=lambda p: p[1])
    if k == 1:
        madero = lz.trazo([(1, 9), (15, 16)], 2.4)
        lz.sombrear(madero, MADERA[1:7], 1.2, LUZ, textura=vetas(lz, 0.4, 9, True, 113), fuerza_tex=0.4)
        lz.pintar(lz.trazo([(14, 15.5), (15.5, 15)], 1.6), MADERA[6])
    for (x, y, r) in piedras:
        p = lz.elipse(x, y, r, r * 0.8, rng.random() * 60)
        lz.sombrear(p, PENA, r, LUZ, textura=lz.ruido(0.8, 2, semilla=int(x * 10)), fuerza_tex=0.4)
        lz.pintar((lz.ruido(0.5, 1, semilla=int(y * 10)) > 0.86) * p, COBRE[3], 0.8)
    if k == 2:
        lz.sombrear(lz.trazo([(3, 21), (10, 6)], 2.0), MADERA[1:6], 1.0, LUZ, textura=vetas(lz, 0.4, 9, False, 114), fuerza_tex=0.4)
    tierra = (lz.ruido(0.6, 1, semilla=115) > 0.7) * lz.elipse(8, 20, 7, 3)
    lz.pintar(tierra, TIERRA[4], 0.8)
    return lz.sprite(contorno=CONTORNO * 0.8)


CAMPANA_COL = {"o": "3a1a0c", "c": "9a4e24", "C": "c06a32", "L": "f4b470", "B": "ffe0b0", "r": "8c281e", "h": "5f626a"}
CAMPANA_1 = [
    "............",
    ".....hh.....",
    "....h..h....",
    ".....oo.....",
    "....oCLo....",
    "...ocCLBo...",
    "...ocCLLo...",
    "..occCCLLo..",
    "..oooooooo..",
    ".....rr.....",
    "............",
    "............",
]
CAMPANA_2 = [
    "............",
    ".....hh.....",
    "....h..h....",
    ".....oo.....",
    ".....oCLo...",
    "....ocCLBo..",
    "....ocCLLo..",
    "...occCCLLo.",
    "...oooooooo.",
    "......rr....",
    "............",
    "............",
]
ICONO = [
    "................",
    ".......hh.......",
    "......h..h......",
    "......h..h......",
    ".......oo.......",
    "......oCLo......",
    ".....ocCLBo.....",
    ".....ocCLBo.....",
    "....occCLLLo....",
    "....occCCLLo....",
    "...occcCCLLLo...",
    "...occcCCCLLo...",
    "..oooooooooooo..",
    "..occccccccccc..",
    ".......rr.......",
    "................",
]


def main():
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(madriguera(), "RGBA").save(os.path.join(SALIDA, "madriguera.png"))
    tira([topo(k) for k in range(6)]).save(os.path.join(SALIDA, "topo.png"))
    tira([derrumbe(k) for k in range(3)]).save(os.path.join(SALIDA, "derrumbe.png"))
    hoja = Image.new("RGBA", (24, 12), (0, 0, 0, 0))
    hoja.alpha_composite(pixeles(CAMPANA_1, CAMPANA_COL), (0, 0))
    hoja.alpha_composite(pixeles(CAMPANA_2, CAMPANA_COL), (12, 0))
    hoja.save(os.path.join(RAIZ, "arte", "mundos", "raiz", "objetos", "campanilla.png"))
    # el icono de la mochila: el 21.º de objetos.png (índice 20)
    ruta = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    n = max(21, viejos.width // 16)
    iconos = Image.new("RGBA", (16 * n, 16), (0, 0, 0, 0))
    iconos.alpha_composite(viejos.crop((0, 0, min(viejos.width, 16 * 20), 16)), (0, 0))
    if viejos.width > 16 * 21:
        iconos.alpha_composite(viejos.crop((16 * 21, 0, viejos.width, 16)), (16 * 21, 0))
    iconos.alpha_composite(pixeles(ICONO, CAMPANA_COL), (16 * 20, 0))
    iconos.save(ruta)
    print("Objetos del Camino Cobrizo en", SALIDA)


if __name__ == "__main__":
    main()
