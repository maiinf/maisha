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
    """La casa de barcas de Kasia, la nutria barquera (136×108, la base en el centro de abajo): medio sobre el río, en
    pilotes; la nave abierta con la piragua dentro y una rampa al agua; el soporte de los remos vacío (los perdió en
    la crecida); una ventana con macetas; el tejado de juncos con una veleta en forma de pez; boyas y cuerdas
    enrolladas; un farol; y una pizarra en la puerta: «SE ALQUILA BALSA»."""
    import pintar_aldea as pa
    W, H = 136, 100
    lz = pa._lienzo(W, H, 8, 261)
    suelo = 96
    cx = 64
    LUZ_ = (-0.6, -0.7, 0.5)
    MAD = ["#1e140e", "#33231a", "#4a3424", "#634733", "#7d5c42", "#977452", "#b08c66"]
    AGUA_ = ["#1c3a3a", "#285050", "#346161", "#4c8d8d", "#6db0b0", "#9fd0d0"]
    # el río, a la derecha y debajo
    rio = lz.poligono([(cx - 6, suelo - 14), (W, suelo - 18), (W, suelo + 2), (cx - 12, suelo + 2)])
    lz.pintar(rio, pa.rampa(AGUA_, np.clip(0.45 + (lz.ruido(1.2, 2, semilla=262) - 0.5) * 0.8, 0, 1)))
    for k in range(7):
        x = cx + k * 10
        lz.pintar(lz.trazo([(x, suelo - 6 + k % 3), (x + 6, suelo - 6 + k % 3)], 0.6), "#c8f0f0", 0.7)
    # los pilotes
    for x in (cx - 40, cx - 18, cx + 4, cx + 26, cx + 48):
        lz.sombrear(pa.rect(lz, x - 2, 62, x + 2, suelo), MAD, 1, LUZ_, textura=pa.vetas(lz, 0.5, 9, False, semilla=x), fuerza_tex=0.4)
    # la plataforma
    lz.sombrear(pa.rect(lz, cx - 46, 60, cx + 54, 65), MAD, 1.5, LUZ_, textura=pa.vetas(lz, 0.5, 13), fuerza_tex=0.4)
    # la casa: tablas, con la nave abierta a la derecha
    pared = pa.rect(lz, cx - 42, 30, cx + 46, 60)
    tabv = (np.abs(np.sin((lz.x - cx) / 3.4 * np.pi)) < 0.1).astype(float)
    lz.sombrear(pared, MAD, 6, LUZ_, textura=pa.vetas(lz, 0.5, 15, False, semilla=263) * (1 - tabv * 0.7), fuerza_tex=0.45)
    nave = pa.rect(lz, cx + 2, 36, cx + 40, 60)
    lz.pintar(nave, "#120c0a")
    lz.sumar_luz(lz.desenfocar(lz.circulo(cx + 22, 46, 6), 6) * nave, "#ef8a26", 0.25)
    piragua = lz.poligono([(cx + 6, 54), (cx + 12, 51), (cx + 34, 51), (cx + 40, 54), (cx + 34, 57), (cx + 12, 57)])
    lz.sombrear(piragua, ["#3a1a0c", "#6a3418", "#9a4e24", "#c06a32", "#e0904e"], 1.5, LUZ_, textura=pa.vetas(lz, 0.5, 13), fuerza_tex=0.3)
    lz.pintar(lz.trazo([(cx + 12, 52.5), (cx + 34, 52.5)], 0.4), "#e0904e")
    rampa_ = lz.poligono([(cx + 2, 60), (cx + 40, 60), (cx + 46, suelo - 6), (cx + 8, suelo - 6)])
    lz.sombrear(rampa_, MAD[1:], 1, LUZ_, textura=(np.abs(np.sin((lz.y - 60) / 3 * np.pi)) < 0.12) * 1.0, fuerza_tex=0.5)
    # el soporte de los remos, vacío (con sus ganchos)
    lz.sombrear(pa.rect(lz, cx - 38, 34, cx - 22, 36), MAD[2:], 0.4, LUZ_)
    for x in (cx - 35, cx - 30, cx - 25):
        lz.pintar(lz.trazo([(x, 36), (x, 39), (x + 1.4, 40)], 0.5), "#80838a")
    # la ventana con macetas
    pa.ventana(lz, cx - 20, 38, cx - 8, 48, encendida=0.6, contras=True, semilla=264, luz=LUZ_)
    # la puerta y la pizarra
    pu = pa.rect(lz, cx - 40, 42, cx - 28, 60)
    lz.sombrear(pu, ["#251812", "#3d2418", "#5a3826", "#7a4e35"], 2, LUZ_, textura=pa.vetas(lz, 0.5, 11, False), fuerza_tex=0.4)
    piz = pa.rect(lz, cx - 54, 46, cx - 44, 58)
    lz.sombrear(piz, MAD[2:], 0.6, LUZ_)
    lz.pintar(pa.rect(lz, cx - 53, 47, cx - 45, 57), "#1c2420")
    for k in range(3):
        lz.pintar(lz.trazo([(cx - 52, 49 + k * 2.6), (cx - 46.5 + (k % 2), 49 + k * 2.6)], 0.4), "#d8dcd0", 0.9)
    for (a, b) in (((cx - 52, 58), (cx - 50, suelo - 2)), ((cx - 46, 58), (cx - 48, suelo - 2))):
        lz.sombrear(lz.trazo([a, b], 0.6), MAD[2:], 0.3, LUZ_)
    # el tejado de juncos y la veleta-pez
    tej = lz.poligono([(cx - 50, 34), (cx - 30, 12), (cx + 34, 12), (cx + 54, 34), (cx + 50, 36), (cx - 46, 36)])
    pa.paja(lz, tej, semilla=265, capas=4.5, y0=12)
    pa.flecos(lz, cx - 50, cx + 54, 34.5, 3.0, semilla=266)
    lz.sombrear(lz.trazo([(cx + 2, 12), (cx + 2, 2)], 0.8), HIERRO_ if "HIERRO_" in globals() else ["#2e2f33", "#5f626a", "#a5a8ae"], 0.4, LUZ_)
    pez = lz.poligono([(cx - 5, 1), (cx + 5, -1), (cx + 9, 1), (cx + 5, 3), (cx - 5, 1)])
    pez = np.maximum(pez, lz.poligono([(cx - 5, 1), (cx - 9, -2), (cx - 9, 4)]))
    lz.sombrear(pez, ["#3a2a10", "#9a7430", "#e8c46a", "#fbe6a2"], 0.6, LUZ_)
    # boyas, cuerdas y el farol
    for (x, col) in ((cx - 4, ["#7a1a1a", "#c83a3a", "#f08a7a"]), (cx, ["#7a6a1a", "#d8b838", "#f8e890"])):
        lz.pintar(lz.trazo([(x, 36), (x, 39)], 0.4), "#3a2a18")
        lz.sombrear(lz.circulo(x, 41.5, 2.2), col, 0.6, LUZ_)
    rollo = np.clip(lz.elipse(cx + 52, 58, 5, 2.4) - lz.elipse(cx + 52, 58, 2.4, 1), 0, 1)
    lz.sombrear(rollo, ["#5c4428", "#a48656", "#c4a874"], 0.8, LUZ_, textura=(np.sin(np.arctan2(lz.y - 58, lz.x - cx - 52) * 10) > 0) * 1.0, fuerza_tex=0.4)
    lz.pintar(lz.trazo([(cx + 46, 34), (cx + 50, 34), (cx + 50, 38)], 0.5), "#2a1a12")
    far = pa.rect(lz, cx + 48, 38, cx + 52, 43)
    lz.pintar(far, pa.rampa(["#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - cx - 50, lz.y - 40.5) / 3, 0, 1)))
    lz.sumar_luz(lz.desenfocar(far, 4), "#ef8a26", 0.4)
    # juncos en la orilla
    for k in range(10):
        x = cx - 60 + k * 5 + (k % 3)
        lz.sombrear(lz.trazo([(x, suelo), (x + (k % 2) * 2 - 1, suelo - 8 - k % 4 * 3)], 0.7, 0.3), ["#3d3214", "#7a6431", "#b09c5c", "#e2cea0"], 0.3, LUZ_)
    pa._hierba_pie(lz, 2, cx - 12, suelo - 2, 267)
    return lz.sprite(contorno=0.4)


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
