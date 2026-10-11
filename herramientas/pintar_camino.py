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
    W, H = 72, 58
    lz = Lienzo(W, H, s=6, semilla=91)
    suelo = 54
    # la loma: tierra cubierta de hierba y hojas, con la boca de la puerta
    loma = lz.elipse(34, suelo + 8, 33, 38) * (lz.y < suelo + 1)
    lz.pintar(lz.desenfocar(lz.elipse(36, suelo, 33, 4), 1.2), "#0e0c0a", 0.5)
    lz.sombrear(loma, HIERBA[1:], 12, LUZ, textura=lz.ruido(1.2, 3, semilla=92), fuerza_tex=0.35)
    hojas = (lz.ruido(0.8, 2, semilla=93) > 0.72) * loma
    lz.pintar(hojas, "#a37036", 0.8)
    lz.pintar((lz.ruido(0.8, 2, semilla=94) > 0.8) * loma, "#cc6351", 0.7)
    # el marco de piedra de la puerta y la puerta redonda de tablas
    marco = lz.elipse(34, 40, 12, 12) * (lz.y < suelo)
    lz.sombrear(marco, PENA[1:], 3, LUZ, textura=lz.ruido(2, 2, semilla=95), fuerza_tex=0.4)
    juntas = np.abs(np.sin(np.arctan2(lz.y - 40, lz.x - 34) * 6)) < 0.18
    lz.pintar(juntas * marco, PENA[1], 0.8)
    puerta = lz.elipse(34, 41, 9, 9.5) * (lz.y < suelo)
    lz.sombrear(puerta, MADERA[1:7], 5, LUZ, textura=vetas(lz, 0.5, 11, False, 96), fuerza_tex=0.45)
    lz.pintar(puerta * ((lz.x % 3.6) < 0.5), MADERA[0], 0.8)
    for y in (36, 47):                                                      # bisagras de cobre
        lz.sombrear(rect(lz, 25.5, y, 33, y + 1.6), COBRE[1:6], 0.8, LUZ)
    pomo = lz.circulo(39, 43, 1.1)
    lz.sombrear(pomo, COBRE[2:], 0.8, LUZ)
    ventanuco = lz.circulo(34, 37, 2.6)
    lz.pintar(ventanuco, "#f9b947")
    lz.brillo(ventanuco, "#f9b947", 2.5, 0.45)
    lz.pintar(lz.trazo([(31.4, 37), (36.6, 37)], 0.5) + lz.trazo([(34, 34.4), (34, 39.6)], 0.5), MADERA[1])
    # la cuerda de las campanillas sobre la puerta, con tres ganchos vacíos
    cuerda = lz.trazo(lz.curva((22, 28), (34, 33), (46, 28), n=30), 0.55)
    lz.pintar(cuerda, "#c9b07e")
    for x in (28, 34, 40):
        lz.pintar(lz.trazo([(x, 30.5 + (1.6 if x == 34 else 0.6)), (x, 32.5 + (1.6 if x == 34 else 0.6))], 0.5), HIERRO[4])
    # el farol de mina en su poste, a la izquierda
    lz.sombrear(rect(lz, 9, 30, 10.6, suelo), MADERA[1:6], 0.9, LUZ, textura=vetas(lz, 0.5, 9, False, 97), fuerza_tex=0.3)
    lz.pintar(lz.trazo([(10, 31), (14, 31)], 0.8), MADERA[3])
    farol = rect(lz, 12.4, 32, 15.6, 37)
    lz.pintar(farol, "#f9b947")
    lz.brillo(farol, "#fde27e", 3, 0.6)
    lz.pintar(rect(lz, 12, 31.4, 16, 32.4) + rect(lz, 12, 36.6, 16, 37.6), HIERRO[2])
    # la vagoneta con mineral de cobre, a la derecha, sobre dos tramos de raíl
    for y in (suelo - 1.4, suelo - 0.2):
        lz.pintar(rect(lz, 48, y, 70, y + 0.7), HIERRO[3])
    caja = lz.poligono([(50, 41), (68, 41), (66.5, 51), (51.5, 51)])
    lz.sombrear(caja, HIERRO, 3, LUZ, textura=lz.ruido(1, 2, semilla=98), fuerza_tex=0.3)
    lz.pintar(rect(lz, 50, 41, 68, 42.3), HIERRO[5], 0.8)
    for x in (52.5, 65.5):
        lz.pintar(lz.circulo(x, 46, 0.6), HIERRO[5])
    for (x, r) in ((54, 3.4), (59, 4.2), (64, 3.2), (56.5, 2.6), (62, 2.8)):
        piedra = lz.circulo(x, 41 - r * 0.4, r) * (lz.y < 42)
        lz.sombrear(piedra, COBRE[:6], r, LUZ, textura=lz.ruido(0.8, 2, semilla=int(x)), fuerza_tex=0.4)
        lz.pintar((lz.ruido(0.5, 1, semilla=int(x) + 3) > 0.8) * piedra, "#3e8f7a", 0.8)
    for x in (54, 64):
        rueda = lz.circulo(x, 52.2, 2.4)
        lz.sombrear(rueda, HIERRO, 1.4, LUZ)
        lz.pintar(lz.circulo(x, 52.2, 0.7), HIERRO[5])
    # el pico, apoyado en la loma a la izquierda de la puerta
    lz.pintar(lz.trazo([(18, suelo - 1), (21.5, 38)], 0.9), MADERA[4])
    lz.sombrear(lz.trazo(lz.curva((17, 39.5), (21.5, 36.5), (26, 39.5), n=12), 1.2, 0.5), HIERRO[1:], 0.8, LUZ)
    # unas setitas y piedras al pie
    for (x, y) in ((4, suelo - 0.5), (27, suelo - 0.2), (45, suelo)):
        lz.sombrear(lz.elipse(x, y - 1, 2.2, 1.4), PENA[2:], 1, LUZ)
    return lz.sprite(contorno=CONTORNO)


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
