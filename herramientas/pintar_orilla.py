"""LOS OBJETOS DE LA ORILLA DE JUNCOS, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_orilla.py

Genera:
  arte/mundos/raiz/orilla/casa_barcas.png  96×72      la casa de Kasia, la nutria barquera: una caseta de tablas sobre
                                                      pilotes en la orilla, con tejado de juncos, una puerta grande
                                                      para sacar la barca, redes tendidas, una boya, y el soporte de
                                                      los remos con tres huecos vacíos
  arte/mundos/raiz/orilla/balsa.png        2 × 40×26  la balsa de troncos atados: 0 medio hundida (rota), 1 a flote,
                                                      con su pértiga
  arte/mundos/raiz/orilla/cangrejo.png     6 × 26×20  el CANGREJO DE HERRUMBRE (enemigo): andando ×2, en guardia
                                                      (pinzas delante), panza arriba, pellizcando y golpeado
  arte/mundos/raiz/objetos/remo.png        2 × 12×12  un remo de Kasia
  y su icono (16×16) en arte/interfaz/objetos.png (el 24.º)
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_casa_shamba import vetas, rect  # noqa: E402
from pintar_pasarelas import tira, pixeles, MADERA, CONTORNO, JUNCO, GIZA  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "orilla")
LUZ = (-0.6, -0.7, 0.5)
AGUA = ["#1c3535", "#285050", "#346161", "#4c8d8d", "#6db0b0"]
RED = ["#3a3020", "#5a4a30", "#7a6640"]
OXIDO = ["#3a160a", "#5e2810", "#86401c", "#a85a2a", "#c87a40", "#e09a5a"]
CAPARAZON = ["#1e1a1a", "#2e2826", "#443a36", "#5a4e48", "#76665c"]


def casa_barcas():
    W, H = 96, 72
    lz = Lienzo(W, H, s=6, semilla=261)
    suelo = 66
    # el agua de la orilla, debajo (la caseta está medio sobre el río)
    agua = lz.poligono([(52, 56), (96, 50), (96, 72), (40, 72)])
    lz.sombrear(agua, AGUA, 4, LUZ, textura=(np.sin(lz.y * 1.8 + lz.x * 0.2) * 0.5 + 0.5), fuerza_tex=0.3)
    lz.pintar(lz.desenfocar(lz.elipse(40, suelo, 36, 4), 1.2), "#0e0c0a", 0.45)
    # los pilotes
    for x in (14, 30, 46, 62, 78):
        p = rect(lz, x - 2, 48, x + 2, suelo + 2)
        lz.sombrear(p, MADERA[1:6], 2, LUZ, textura=vetas(lz, 0.4, 7, False, x), fuerza_tex=0.4)
        lz.pintar(lz.elipse(x, suelo + 1, 3.2, 0.9) * (lz.x > 44), AGUA[4], 0.6)        # el agua al pie del pilote
    # la plataforma de tablas
    plat = lz.poligono([(4, 48), (86, 44), (88, 50), (6, 54)])
    lz.sombrear(plat, MADERA[2:7], 3, LUZ, textura=vetas(lz, 0.4, 13, True, 262), fuerza_tex=0.4)
    lz.pintar(plat * ((lz.x % 5) < 0.6), MADERA[0], 0.7)
    # la caseta: tablas verticales, una puerta grande (abierta, se ve la oscuridad) y una ventana
    frente = rect(lz, 10, 22, 66, 48)
    lz.sombrear(frente, MADERA[2:7], 6, LUZ, textura=vetas(lz, 0.45, 13, False, 263), fuerza_tex=0.4)
    lz.pintar(frente * ((lz.x % 4) < 0.5), MADERA[0], 0.75)
    lado = lz.poligono([(66, 22), (76, 17), (76, 44), (66, 48)])
    lz.sombrear(lado, MADERA[1:5], 3, LUZ, textura=vetas(lz, 0.45, 13, False, 264), fuerza_tex=0.4)
    puerta = rect(lz, 38, 30, 58, 48)
    lz.pintar(puerta, "#0c0a0a")
    lz.pintar(rect(lz, 38, 30, 58, 31.2), MADERA[1])
    lz.sombrear(lz.poligono([(40, 46), (56, 46), (54, 44), (42, 44)]), MADERA[3:7], 1, LUZ)   # la proa de la barca, dentro
    ventana = rect(lz, 16, 30, 24, 37)
    lz.pintar(ventana, "#0c0a0a")
    lz.brillo(lz.elipse(20, 34, 2.4, 1.8), "#e6a852", 2.0, 0.55)
    lz.pintar(rect(lz, 15.5, 33, 24.5, 33.8), MADERA[4])
    # el tejado de juncos, a dos aguas, con el borde deshilachado
    hilos = np.sin(lz.x * 3.1 + lz.y * 0.9) * 0.5 + 0.5
    faldon = lz.poligono([(38, 3), (44, 2), (80, 17), (70, 23)])
    lz.sombrear(faldon, JUNCO[:5], 4, LUZ, textura=hilos * 0.6 + vetas(lz, 0.3, 7, False, 266) * 0.4, fuerza_tex=0.5)
    tejado = lz.poligono([(4, 24), (38, 3), (44, 2), (72, 24)])
    lz.sombrear(tejado, JUNCO, 6, LUZ, textura=hilos * 0.6 + vetas(lz, 0.3, 7, False, 265) * 0.4, fuerza_tex=0.5)
    flecos = np.zeros((lz.H, lz.W))
    for k in range(36):
        x0 = 5 + k * 1.9
        flecos = np.maximum(flecos, lz.trazo([(x0, 23.5), (x0 + 0.4, 26 + (k % 3))], 0.5))
    lz.pintar(flecos, JUNCO[4], 0.9)
    # el soporte de los remos, en la pared: cinco huecos y solo dos remos (faltan tres)
    lz.pintar(rect(lz, 26, 25, 36, 26), MADERA[1])
    for k, x in enumerate((27, 29, 31, 33, 35)):
        if k in (0, 3):
            lz.sombrear(lz.trazo([(x, 25.5), (x, 44)], 0.8), MADERA[4:8], 0.6, LUZ)
            lz.sombrear(lz.elipse(x, 42.5, 1.2, 2.4), MADERA[4:8], 1, LUZ)
        else:
            lz.pintar(lz.circulo(x, 25.6, 0.5), MADERA[0])                       # el hueco vacío
    # una red tendida a secar entre dos palos, con sus flotadores rojos
    for x in (78, 92):
        lz.pintar(lz.trazo([(x, 50), (x, 28)], 0.8), MADERA[4])
    red = lz.poligono([(78, 30), (92, 30), (91, 44), (79, 44)])
    lz.pintar(red * (((lz.x + lz.y) % 2.2 < 0.45) | ((lz.x - lz.y) % 2.2 < 0.45)), RED[1], 0.9)
    for x in (80, 84, 88):
        lz.pintar(lz.circulo(x, 30.5, 0.9), "#de6771")
    # una boya y una cuerda enrollada en la plataforma
    lz.sombrear(lz.circulo(8, 48, 2.4), ["#8a2a2a", "#b04040", "#de6771", "#f4bcc4"], 2, LUZ)
    for r in (2.2, 1.4):
        lz.pintar(np.clip(lz.elipse(70, 49, r * 1.4, r * 0.6) - lz.elipse(70, 49, r * 1.4 - 0.4, r * 0.6 - 0.3), 0, 1), "#a48656")
    return lz.sprite(contorno=CONTORNO)


def balsa(k):
    """La balsa de troncos: 0 medio hundida y torcida (rota, falta un tronco), 1 a flote, con su pértiga."""
    W, H = 40, 26
    lz = Lienzo(W, H, s=6, semilla=271 + k)
    if k == 1:
        lz.pintar(lz.desenfocar(lz.elipse(20, 20, 18, 3.4), 1.0), "#0e1a1a", 0.5)
    troncos = 5 if k == 1 else 4
    for i in range(troncos):
        y = 9 + i * 2.8
        hundido = (0 if k == 1 else i * 1.2)
        t = lz.trazo([(3, y + hundido * 0.4), (37, y - (1.5 if k == 0 and i == 0 else 0))], 2.6)
        lz.sombrear(t, MADERA[1:7], 1.4, LUZ, textura=vetas(lz, 0.4, 9, True, 272 + i), fuerza_tex=0.45)
        lz.pintar(lz.elipse(37, y, 1.0, 1.3), "#a07a50")                              # el corte del tronco
    for x in (9, 31):                                                                    # las cuerdas
        lz.pintar(lz.trazo([(x, 7.5), (x + 0.5, 9 + troncos * 2.8)], 0.7), "#a48656")
    if k == 0:
        # el agua por encima de la mitad de la balsa
        agua = lz.poligono([(0, 15), (40, 11), (40, 26), (0, 26)])
        lz.pintar(agua, AGUA[2], 0.75)
        lz.pintar(agua * (np.sin(lz.x * 0.9 + lz.y * 2) > 0.85), AGUA[4], 0.6)
    else:
        # la pértiga, apoyada encima
        lz.sombrear(lz.trazo([(5, 6), (35, 18)], 0.9), MADERA[3:8], 0.6, LUZ)
        for y in (21.5, 23):
            lz.pintar(lz.trazo([(2, y), (38, y)], 0.4), AGUA[4], 0.5)                 # las ondas
    return lz.sprite(contorno=CONTORNO * 0.8)


def cangrejo(estado):
    """El CANGREJO DE HERRUMBRE, de frente y algo de lado: caparazón de hierro oxidado con grietas violetas de Giza,
    ojos en tallos y dos pinzas grandes. 0-1 andando de lado · 2 en guardia (pinzas juntas delante: el cetro rebota) ·
    3 panza arriba (la semilla le ha dado la vuelta: se le ve la barriga clara y patalea) · 4 pellizcando ·
    5 golpeado (blanco en el juego)."""
    W, H = 26, 20
    lz = Lienzo(W, H, s=8, semilla=281 + estado)
    lz.pintar(lz.desenfocar(lz.elipse(13, 18, 10, 1.6), 0.6), "#0e0c0a", 0.55)
    cx, cy = 13, 12
    if estado == 3:
        # panza arriba: la barriga clara, las patas al aire
        for i, x in enumerate((6, 8, 10, 16, 18, 20)):
            dy = (np.sin(estado * 3 + i) > 0) * 1.2
            lz.pintar(lz.trazo([(x, cy - 1), (x + (x - 13) * 0.25, cy - 6 - dy)], 0.7), OXIDO[2])
        barriga = lz.elipse(cx, cy + 1, 8, 4.5)
        lz.sombrear(barriga, ["#8a7a62", "#b8a888", "#d8ccb0"], 3, LUZ)
        lz.pintar(lz.trazo([(cx - 3, cy + 1), (cx + 3, cy + 1)], 0.4), "#7a6a52")
        for lado in (-1, 1):
            lz.sombrear(lz.elipse(cx + lado * 9.5, cy + 3, 2.6, 2.0), OXIDO[1:], 1.5, LUZ)
        return lz.sprite(contorno=CONTORNO)
    # las patas, a los lados (se mueven al andar)
    paso = 1.0 if estado == 0 else (-1.0 if estado == 1 else 0.0)
    for i, (x, y) in enumerate(((6, 12), (5, 14), (6, 16), (20, 12), (21, 14), (20, 16))):
        d = paso if i % 2 == 0 else -paso
        lado = -1 if x < 13 else 1
        lz.pintar(lz.trazo([(x + lado * 1.5, y - 1), (x + lado * 3.5, y + 1 + d * 0.6), (x + lado * 4, y + 3 + d * 0.6)], 0.7), OXIDO[2])
    # el caparazón de hierro oxidado
    caparazon = lz.elipse(cx, cy, 8.5, 5.5)
    lz.sombrear(caparazon, OXIDO, 5, LUZ, textura=lz.ruido(0.8, 2, semilla=282), fuerza_tex=0.4)
    lz.pintar((lz.ruido(0.5, 1, semilla=283) > 0.82) * caparazon, OXIDO[5], 0.7)
    lz.pintar(lz.trazo([(cx - 3, cy - 2), (cx, cy), (cx + 2, cy - 3)], 0.45) * caparazon, GIZA[3], 0.9)
    lz.brillo(lz.trazo([(cx - 3, cy - 2), (cx, cy)], 0.4), GIZA[3], 1.2, 0.4)
    # los ojos, en tallos
    for lado in (-1, 1):
        lz.pintar(lz.trazo([(cx + lado * 2, cy - 4.5), (cx + lado * 2.5, cy - 8)], 0.6), OXIDO[3])
        lz.pintar(lz.circulo(cx + lado * 2.5, cy - 8.4, 1.0), "#1a1418")
        lz.pintar(lz.circulo(cx + lado * 2.3, cy - 8.7, 0.35), GIZA[4])
    # las pinzas
    for lado in (-1, 1):
        if estado == 2:
            px, py = cx + lado * 3.2, cy + 4.5                      # juntas delante (guardia)
        elif estado == 4:
            px, py = cx + lado * 7, cy - 4                          # arriba, abiertas (pellizca)
        else:
            px, py = cx + lado * 10, cy - 1
        lz.pintar(lz.trazo([(cx + lado * 6, cy), (px, py + 1)], 1.0), OXIDO[2])
        pinza = lz.elipse(px, py, 3.0, 2.2)
        lz.sombrear(pinza, OXIDO[1:], 2, LUZ, textura=lz.ruido(0.6, 1, semilla=284), fuerza_tex=0.3)
        abre = 1.6 if estado == 4 else 0.4
        lz.pintar(lz.trazo([(px - lado * 0.5, py - 1.2), (px + lado * 2.4, py - 1.2 - abre)], 0.45), "#1a1418")
    return lz.sprite(contorno=CONTORNO)


REMO_COL = {"o": "251812", "c": "5b392b", "C": "905c45", "L": "b88a62", "B": "e2cea0", "r": "8c281e", "R": "de6771"}
REMO_1 = [
    "............",
    ".........oo.",
    "........oLo.",
    ".......oLo..",
    "......oCo...",
    ".....oCo....",
    "....orRo....",
    "...occo.....",
    "..oLCCo.....",
    ".oLCCco.....",
    ".oCCco......",
    "..ooo.......",
]
REMO_2 = [
    "............",
    ".oo.........",
    ".oLo........",
    "..oLo.......",
    "...oCo......",
    "....oCo.....",
    "....orRo....",
    ".....occo...",
    ".....oCCLo..",
    ".....ocCCLo.",
    "......ocCCo.",
    ".......ooo..",
]
ICONO = [
    "................",
    "............oo..",
    "...........oLBo.",
    "..........oLLo..",
    ".........oLCo...",
    "........oCCo....",
    ".......oCCo.....",
    "......orRRo.....",
    ".....orRRo......",
    "....occco.......",
    "...oLCCCo.......",
    "..oLLCCco.......",
    ".oLLCCcco.......",
    ".oCCCcco........",
    "..oooo..........",
    "................",
]


def main():
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(casa_barcas()).save(os.path.join(SALIDA, "casa_barcas.png"))
    tira([balsa(k) for k in range(2)]).save(os.path.join(SALIDA, "balsa.png"))
    tira([cangrejo(k) for k in range(6)]).save(os.path.join(SALIDA, "cangrejo.png"))
    hoja = Image.new("RGBA", (24, 12), (0, 0, 0, 0))
    hoja.alpha_composite(pixeles(REMO_1, REMO_COL), (0, 0))
    hoja.alpha_composite(pixeles(REMO_2, REMO_COL), (12, 0))
    hoja.save(os.path.join(RAIZ, "arte", "mundos", "raiz", "objetos", "remo.png"))
    # el icono de la mochila: el 24.º de objetos.png (índice 23)
    ruta = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    n = max(24, viejos.width // 16)
    iconos = Image.new("RGBA", (16 * n, 16), (0, 0, 0, 0))
    iconos.alpha_composite(viejos.crop((0, 0, min(viejos.width, 16 * 23), 16)), (0, 0))
    if viejos.width > 16 * 24:
        iconos.alpha_composite(viejos.crop((16 * 24, 0, viejos.width, 16)), (16 * 24, 0))
    iconos.alpha_composite(pixeles(ICONO, REMO_COL), (16 * 23, 0))
    iconos.save(ruta)
    print("Objetos de la Orilla de Juncos en", SALIDA)


if __name__ == "__main__":
    main()
