"""LOS OBJETOS DEL EMBARCADERO JUNCO, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_embarcadero.py

Genera (en arte/mundos/raiz/embarcadero/):
  casa_juncos.png     2 × 100×92  las casas de los barqueros, al nivel de detalle de la casa del castor: pilotes con
                                  verdín, plataforma de tablas, paredes de esteras con armazón de troncos, tejado de
                                  paja a capas, ventana con contraventanas y jardinera, porche, escalerilla, barquita
                                  amarrada y cosas de barquero (redes, remos, nasa, peces, cántaros, farolillo)
  grua.png            48×76       la grúa del muelle, rota: un poste grueso con su pluma inclinada, la polea
                                  partida, la cuerda colgando y el gancho; un fardo caído al pie
  almacen.png         132×108     el almacén, al nivel de la casa del castor: zócalo de piedra, troncos, tejado de
                                  paja con buhardilla de carga y polea, portón abierto, letrero del pez, ventana,
                                  barriles, cajas, sacos, tendedero de redes y carretilla
  poste.png           2 × 22×44   un poste de amarre de la dársena (alto, de madera clara, con anillo de cuerda): 0 entero,
                                  1 mordido por Mamba (con las marcas de los dientes y astillas)
  transbordador.png   2 × 120×60  el TRANSBORDADOR: una barcaza grande y plana con barandilla, una caseta para el
                                  barquero, una campana y una pértiga larga. 0 varado (escorado, con un boquete en
                                  el casco y algas), 1 arreglado y a flote
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ, rampa  # noqa: E402
from pintar_casa_shamba import vetas, rect, paja, flecos, ventana, troncos  # noqa: E402
from cinematicas import piedras, flores, COBRE  # noqa: E402
from pintar_pasarelas import tira, MADERA, CONTORNO, JUNCO  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "embarcadero")
LUZ = (-0.6, -0.7, 0.5)
AGUA = ["#1c3535", "#285050", "#346161", "#4c8d8d", "#6db0b0", "#9fd0d0"]
HIERRO = ["#1a1a1c", "#2c2c30", "#424248", "#5a5a62", "#76767e"]
CUERDA = "#a48656"


def _pilotes(lz, xs, arriba, abajo, agua=True):
    for x in xs:
        p = rect(lz, x - 1.7, arriba, x + 1.7, abajo)
        lz.sombrear(p, MADERA[1:6], 1.7, LUZ, textura=vetas(lz, 0.5, 9, False, int(x * 7)), fuerza_tex=0.35)
        if agua:
            lz.pintar(rect(lz, x - 2.6, abajo - 1.2, x + 2.6, abajo + 0.4), AGUA[5], 0.7)
            lz.pintar(rect(lz, x - 1.7, abajo - 4, x + 1.7, abajo - 1.2), "#2e4a2a", 0.6)     # el verdín del agua


def _juncos_atados(lz, mascara, semilla, rampa=JUNCO):
    """Una pared de juncos verticales atados con cuerda cada poco."""
    hilos = np.sin(lz.x * 2.4 + np.sin(lz.y * 0.3) * 0.6) * 0.5 + 0.5
    lz.sombrear(mascara, rampa[1:], 5, LUZ, textura=hilos * 0.7 + vetas(lz, 0.3, 7, False, semilla) * 0.3, fuerza_tex=0.55)
    lz.pintar(mascara * ((lz.x % 2.4) < 0.35), rampa[0], 0.6)


def casa_juncos(k):
    """Una casa de barqueros al nivel de detalle de la casa del castor: plataforma de tablas sobre pilotes (con
    verdín y el agua al pie), paredes de esteras de junco tejido con un armazón de troncos, un tejado grueso de paja a
    capas con caballete, una ventana con contraventanas y jardinera (encendida), la puerta con cortina de esteras, un
    porche con barandilla y escalerilla al agua, y cosas de barquero: redes con flotadores, peces secándose, remos,
    nasas, cántaros y una barquita amarrada debajo. k = 0 o 1: dos casas distintas (la 1, en espejo y con otras cosas)."""
    W, H = 100, 92
    lz = Lienzo(W, H, s=4, semilla=301 + k)
    rng = np.random.default_rng(302 + k)
    abajo = 88
    plat_y = 62
    # el agua al pie, con sombra de la casa y reflejos
    agua = lz.poligono([(0, 78), (100, 74), (100, 92), (0, 92)])
    lz.sombrear(agua, AGUA, 4, LUZ, textura=(np.sin(lz.y * 1.6 + lz.x * 0.25) * 0.5 + 0.5), fuerza_tex=0.35)
    lz.pintar(lz.desenfocar(rect(lz, 8, 76, 92, 92), 3) * agua, "#0a1414", 0.45)
    ondas = (np.abs(np.sin(lz.x * 0.45 + lz.y * 1.9)) < 0.08) * agua
    lz.pintar(ondas, AGUA[5], 0.5)
    # la barquita amarrada debajo, entre los pilotes
    barca = lz.poligono([(18, 80), (52, 79), (48, 85), (22, 86)])
    lz.sombrear(barca, MADERA[1:7], 2, LUZ, textura=vetas(lz, 0.5, 9, True, 303 + k), fuerza_tex=0.4)
    lz.pintar(lz.poligono([(21, 80.4), (49, 79.6), (46.5, 81.6), (23, 82)]), "#1a120c")
    lz.pintar(lz.trazo([(18, 80), (52, 79)], 0.6), MADERA[7])
    lz.pintar(barca * (lz.y > 83) * (np.sin(lz.x * 0.8) > 0), "#4c8d8d", 0.5)          # pintura azul desconchada
    lz.pintar(lz.trazo([(50, 79.5), (58, 68)], 0.4), CUERDA)
    # los pilotes, con verdín y el agua al pie
    for x in (10, 26, 42, 58, 74, 90):
        p = rect(lz, x - 2.2, plat_y, x + 2.2, abajo)
        lz.sombrear(p, ["#1a0f0b", "#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544"], 2.2, LUZ,
                    textura=vetas(lz, 0.6, 11, False, int(x)), fuerza_tex=0.4)
        lz.pintar(rect(lz, x - 2.2, 74, x + 2.2, 80) * (lz.ruido(0.6, 2, semilla=int(x)) > 0.35), "#2e4a2a", 0.75)
        lz.pintar(lz.elipse(x, 78.5, 3.4, 0.9), AGUA[5], 0.7)
        lz.pintar(lz.trazo([(x - 2.2, 70), (x + 2.2, 70.6)], 0.5), CUERDA, 0.9)       # la ligadura de cuerda
    # tornapuntas en cruz entre los pilotes
    for (a, b) in ((10, 26), (42, 58), (74, 90)):
        lz.sombrear(lz.trazo([(a, 64), (b, 74)], 1.0) + lz.trazo([(b, 64), (a, 74)], 1.0), MADERA[2:6], 0.8, LUZ)
    # la plataforma de tablas, con su canto
    plat = lz.poligono([(2, plat_y - 3), (98, plat_y - 5), (98, plat_y), (2, plat_y + 2)])
    tabl = (np.abs(np.sin(lz.x / 4.5 * np.pi)) < 0.1).astype(float)
    lz.sombrear(plat, COBRE, 2, LUZ, textura=1 - tabl * 0.9 + vetas(lz, 0.5, 13) * 0.2, fuerza_tex=0.5)
    canto = lz.poligono([(2, plat_y + 2), (98, plat_y), (98, plat_y + 3), (2, plat_y + 5)])
    lz.sombrear(canto, MADERA[1:6], 1.2, LUZ, textura=vetas(lz, 0.5, 13), fuerza_tex=0.4)
    # la casa: armazón de troncos y paredes de esteras tejidas
    x0, x1, yt = 18, 74, 30
    pared = rect(lz, x0, yt, x1, plat_y - 3)
    tejido = (np.sin(lz.x * 1.9) * np.sin(lz.y * 1.9) > 0).astype(float)
    hilos = vetas(lz, 0.4, 7, False, 304 + k)
    lz.sombrear(pared, ["#3d3214", "#5c4a22", "#7a6431", "#958043", "#b09c5c", "#c9b77d"], 6, LUZ,
                textura=tejido * 0.55 + hilos * 0.45, fuerza_tex=0.55)
    lz.pintar(pared * (np.abs(np.sin(lz.y / 5.5 * np.pi)) < 0.06), "#3d3214", 0.7)       # las costuras de las esteras
    lado = lz.poligono([(x1, yt), (86, yt - 5), (86, plat_y - 7), (x1, plat_y - 3)])
    lz.sombrear(lado, ["#2a2210", "#3d3214", "#5c4a22", "#7a6431", "#958043"], 3, LUZ, textura=tejido * 0.5 + hilos * 0.5, fuerza_tex=0.5)
    for (xa, xb) in ((x0 - 1.8, x0 + 1.8), (x1 - 1.8, x1 + 1.8), (85, 87.4)):
        lz.sombrear(rect(lz, xa, yt - 2, xb, plat_y - 2), ["#1a0f0b", "#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544"], 1.8, LUZ,
                    textura=vetas(lz, 0.6, 11, False, int(xa)), fuerza_tex=0.4)
    lz.sombrear(rect(lz, x0 - 2, plat_y - 6, x1 + 2, plat_y - 3), MADERA[2:7], 1, LUZ, textura=vetas(lz, 0.6, 13), fuerza_tex=0.3)
    # sombra del alero
    lz.pintar(np.clip((yt + 9 - lz.y) / 9, 0, 1) * rect(lz, x0 - 2, yt, 88, plat_y), "#120b08", 0.5)
    # la ventana (con contraventanas y jardinera) y la puerta con cortina de esteras
    vx = 50 if k == 0 else 26
    ventana(lz, vx, 37, vx + 12, 48, encendida=0.6, semilla=305 + k, luz=LUZ)
    px = 26 if k == 0 else 56
    puerta = rect(lz, px, 38, px + 12, plat_y - 3)
    lz.pintar(puerta, "#120c08")
    cortina = rect(lz, px + 0.5, 38, px + 11.5, 47) * (lz.y < 41 + np.sin((lz.x - px) * 0.9) * 0.6 + 4)
    lz.sombrear(cortina, ["#5c4a22", "#958043", "#c9b77d"], 1, LUZ, textura=(np.abs(np.sin(lz.x * 2.2)) < 0.3).astype(float), fuerza_tex=0.4)
    lz.sumar_luz(lz.desenfocar(rect(lz, px + 2, 48, px + 10, plat_y - 4), 2), "#ef8a26", 0.25)
    lz.sombrear(rect(lz, px - 1.5, 36, px + 13.5, 38.2), MADERA[2:7], 0.8, LUZ)
    # el tejado de paja, grueso, a dos aguas y con el caballete trenzado
    tejado = lz.poligono([(4, yt + 4), (44, 2), (52, 2), (96, yt - 1), (96, yt + 2), (4, yt + 7)])
    paja(lz, tejado, semilla=306 + k, capas=5.0, y0=2)
    lz.pintar(tejado * np.clip((lz.x - 54) / 40, 0, 1), "#2a1a0a", 0.3)
    cab = lz.elipse(48, 3, 9, 2.6)
    lz.sombrear(cab, ["#3d2a10", "#704f25", "#a37036", "#d29a43", "#efc06a"], 1.6, LUZ, textura=vetas(lz, 0.5, 7, True), fuerza_tex=0.4)
    for xx in (42, 48, 54):
        lz.pintar(lz.trazo([(xx, 1), (xx + 0.5, 5)], 0.6), "#4a3012", 0.8)
    flecos(lz, 4, 96, yt + 5.5, 3.0, semilla=307 + k)
    # el porche: la barandilla de palos y la escalerilla que baja al agua
    for x in range(4, 18, 3):
        lz.sombrear(rect(lz, x, plat_y - 12, x + 1.1, plat_y - 3), MADERA[3:7], 0.6, LUZ)
    lz.sombrear(rect(lz, 3, plat_y - 13, 18, plat_y - 11.5), MADERA[3:8], 0.8, LUZ)
    for j_ in range(4):
        lz.pintar(lz.trazo([(90, plat_y + 3 + j_ * 4), (96, plat_y + 3 + j_ * 4)], 0.9), MADERA[5])
    lz.pintar(lz.trazo([(90, plat_y), (90, abajo - 2)], 0.7) + lz.trazo([(96, plat_y), (96, abajo - 2)], 0.7), MADERA[3])
    # cosas de barquero
    if k == 0:
        # una red tendida en el lado, con sus flotadores rojos
        red = lz.poligono([(75, yt - 2), (85, yt - 6), (85, yt + 16), (75, yt + 20)])
        malla = ((np.abs((lz.x + lz.y) % 2.6) < 0.35) | (np.abs((lz.x - lz.y) % 2.6) < 0.35)) * red
        lz.pintar(malla, "#d8c8a0", 0.85)
        for (fx, fy) in ((77, yt - 1.5), (80, yt - 3), (83, yt - 4.5)):
            lz.sombrear(lz.circulo(fx, fy, 1.1), ["#8f2532", "#d5525e", "#f4b39a"], 0.8, LUZ)
        # dos remos apoyados y una nasa
        for (rx, ang) in ((8, 0), (12, 1.5)):
            lz.sombrear(lz.trazo([(rx, plat_y - 3), (rx + 3 + ang, plat_y - 26)], 0.7), MADERA[4:8], 0.6, LUZ)
            lz.sombrear(lz.elipse(rx + 3.4 + ang, plat_y - 28, 1.6, 3.6, -8), MADERA[4:8], 1, LUZ)
        nasa = lz.elipse(66, plat_y - 7, 4.5, 3.6)
        lz.pintar(nasa * (((lz.x + lz.y) % 1.6) < 0.55), JUNCO[4])
        lz.pintar(np.clip(nasa - lz.elipse(66, plat_y - 7, 3.5, 2.6), 0, 1), JUNCO[2])
        lz.pintar(lz.elipse(62, plat_y - 7, 1.2, 2.2), "#1a120c")
    else:
        # peces secándose en una cuerda bajo el alero y dos cántaros
        lz.pintar(lz.trazo([(x0 + 2, yt + 6), (x0 + 22, yt + 7)], 0.4), CUERDA)
        for x in range(x0 + 4, x0 + 22, 4):
            lz.sombrear(lz.elipse(x, yt + 10, 1.2, 2.8), ["#1c3535", "#346161", "#4c8d8d", "#9fd0d0"], 1, LUZ)
            lz.pintar(lz.poligono([(x - 1.4, yt + 13), (x + 1.4, yt + 13), (x, yt + 11.5)]), "#346161")
        for (cx, h_) in ((80, 7), (86, 5.5)):
            c_ = lz.elipse(cx, plat_y - 3 - h_ * 0.6, 3.2, h_ * 0.65)
            lz.sombrear(c_, ["#5a2810", "#8a4418", "#b8662a", "#d88a48", "#f0b070"], 2, LUZ)
            lz.pintar(lz.elipse(cx, plat_y - 3 - h_ * 1.2, 1.6, 0.6), "#2a1408")
        # un farolillo de papel colgado
        lz.pintar(lz.trazo([(88, yt + 1), (88, yt + 6)], 0.4), "#1a120c")
        fz = lz.elipse(88, yt + 8.5, 2.2, 2.8)
        lz.pintar(fz, rampa(["#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - 88, lz.y - yt - 8) / 3, 0, 1)))
        lz.sumar_luz(lz.desenfocar(fz, 3), "#ef8a26", 0.35)
    # una maceta con flores junto a la puerta
    mx = px + 15 if k == 0 else px - 4
    lz.sombrear(lz.poligono([(mx - 2.5, plat_y - 7), (mx + 2.5, plat_y - 7), (mx + 1.8, plat_y - 3), (mx - 1.8, plat_y - 3)]), COBRE, 1.2, LUZ)
    flores(lz, 5, (mx - 3, plat_y - 10, mx + 3, plat_y - 7), [["#8f2532", "#d5525e", "#e98378"], ["#b2721a", "#df9022", "#f1c27a"]], semilla=308 + k, tam=0.7)
    return lz.sprite(contorno=CONTORNO)


def grua():
    W, H = 48, 76
    lz = Lienzo(W, H, s=6, semilla=311)
    lz.pintar(lz.desenfocar(lz.elipse(16, 72, 14, 2.6), 0.8), "#0e0c0a", 0.5)
    # la base de piedras y el poste grueso, con dos tornapuntas
    base = lz.elipse(16, 70, 9, 3.4)
    lz.sombrear(base, ["#2e302a", "#41443a", "#5c6052", "#7a806d", "#9aa08a"], 3, LUZ, textura=lz.ruido(1, 2, semilla=312), fuerza_tex=0.4)
    poste = rect(lz, 13, 10, 19, 70)
    lz.sombrear(poste, MADERA[1:7], 3, LUZ, textura=vetas(lz, 0.5, 11, False, 313), fuerza_tex=0.45)
    for lado in (-1, 1):
        lz.sombrear(lz.trazo([(16 + lado * 10, 69), (16 + lado * 1.5, 50)], 1.3), MADERA[2:6], 1, LUZ)
    # la pluma inclinada hacia el agua, rajada en la punta
    pluma = lz.trazo([(16, 16), (44, 6)], 1.8)
    lz.sombrear(pluma, MADERA[2:7], 1.6, LUZ, textura=vetas(lz, 0.5, 11, True, 314), fuerza_tex=0.4)
    lz.pintar(lz.trazo([(36, 9), (41, 7.5)], 0.35), MADERA[0])
    lz.pintar(lz.trazo([(16, 30), (34, 10)], 0.7), CUERDA)                        # el tirante
    # la polea partida y la cuerda colgando con el gancho
    lz.sombrear(lz.circulo(42, 8, 2.4), HIERRO[1:], 2, LUZ)
    lz.pintar(lz.trazo([(42, 8), (43.5, 10.5)], 0.6), "#8a3a1a")                   # la grieta oxidada
    cuerda = lz.trazo(lz.curva((42, 10), (44, 28), (40, 42), n=20), 0.45)
    lz.pintar(cuerda, CUERDA)
    gancho = np.clip(lz.circulo(40, 44.5, 2.2) - lz.circulo(40.6, 44, 1.3), 0, 1) * (lz.x < 41.5)
    lz.sombrear(gancho + lz.trazo([(40, 42), (40, 43)], 0.6), HIERRO[1:], 1, LUZ)
    # la manivela del torno, en el poste
    lz.sombrear(lz.circulo(16, 50, 3.4), MADERA[2:6], 2, LUZ)
    lz.pintar(lz.trazo([(16, 50), (21, 46)], 0.7), HIERRO[3])
    for r in (2.4, 1.6):
        lz.pintar(np.clip(lz.circulo(16, 50, r) - lz.circulo(16, 50, r - 0.4), 0, 1), CUERDA, 0.8)
    # el fardo caído al pie, con la red rota
    fardo = lz.elipse(31, 68, 6.5, 4)
    lz.sombrear(fardo, ["#4a3a22", "#6a5232", "#8a6e46", "#a88a5e"], 3, LUZ, textura=lz.ruido(0.6, 2, semilla=315), fuerza_tex=0.4)
    lz.pintar(((np.abs((lz.x + lz.y) % 2.4) < 0.3) | (np.abs((lz.x - lz.y) % 2.4) < 0.3)) * fardo, CUERDA, 0.8)
    return lz.sprite(contorno=CONTORNO)


def almacen():
    """El almacén del puerto, al nivel de la casa del castor: zócalo de piedra con musgo, paredes de troncos, un
    tejado de paja a capas con una buhardilla de carga (con su viga y su polea, de la que cuelga un fardo), el portón
    abierto (dentro, sacos y barriles en la penumbra), una ventana con contraventanas, el letrero del pez, y delante
    barriles, cajas, sacos de grano, un tendedero de redes y una carretilla."""
    W, H = 132, 108
    lz = Lienzo(W, H, s=4, semilla=321)
    rng = np.random.default_rng(322)
    x0, x1 = 16, 112
    suelo = 102
    # el zócalo de piedra
    zocalo = rect(lz, x0 - 3, 88, x1 + 3, suelo)
    piedras(lz, zocalo, tam=4.6, semilla=323, luz=LUZ, mortero="#525449",
            rampa_p=["#3a3b33", "#5a5d50", "#7a806d", "#9aa08c", "#b9bdaa", "#d6d8c8"])
    musgo = (lz.ruido(2.5, 3, semilla=324) > 0.66) * zocalo * np.clip((lz.y - 92) / 8, 0, 1)
    lz.pintar(lz.desenfocar(musgo, 0.3), rampa(["#24401f", "#3f5a2f", "#5d7a3c"], lz.ruido(0.7, 2)), 0.8)
    # las paredes de troncos y la sombra del alero
    troncos(lz, x0, x1, 46, 88, alto=6.0, semilla=325)
    lz.pintar(np.clip((60 - lz.y) / 14, 0, 1) * rect(lz, x0 - 3, 46, x1 + 3, 88), "#120b08", 0.55)
    # el tejado de paja, largo, a dos aguas (con el hastial a la derecha)
    tejado = lz.poligono([(2, 50), (22, 10), (100, 10), (128, 50), (128, 53), (2, 53)])
    paja(lz, tejado, semilla=326, capas=6.0, y0=10)
    lz.pintar(tejado * np.clip((lz.x - 70) / 60, 0, 1), "#2a1a0a", 0.3)
    cab = rect(lz, 22, 8, 100, 12)
    lz.sombrear(cab, ["#3d2a10", "#704f25", "#a37036", "#d29a43", "#efc06a"], 1.6, LUZ, textura=vetas(lz, 0.5, 7, True), fuerza_tex=0.4)
    flecos(lz, 2, 128, 52.5, 3.2, semilla=327)
    # la buhardilla de carga: una puertecita, la viga que sale y la polea con un fardo colgando
    bx = 64
    troncos(lz, bx - 10, bx + 10, 22, 40, alto=4.5, semilla=328, esquinas=False)
    techito = lz.poligono([(bx - 15, 25), (bx, 12), (bx + 15, 25), (bx + 13, 27), (bx, 16), (bx - 13, 27)])
    techito = np.maximum(techito, lz.poligono([(bx - 13, 25), (bx, 14), (bx + 13, 25)]))
    paja(lz, techito, semilla=329, capas=4.0, y0=12)
    flecos(lz, bx - 14, bx + 14, 26.5, 2.0, semilla=330)
    hueco = rect(lz, bx - 5, 28, bx + 5, 40)
    lz.pintar(hueco, "#120c08")
    lz.sombrear(rect(lz, bx - 6, 27, bx + 6, 28.5), MADERA[2:7], 0.8, LUZ)
    viga = rect(lz, bx - 2, 15, bx + 2, 18) + rect(lz, bx, 15, bx + 2, 17)
    lz.sombrear(lz.trazo([(bx, 16), (bx, 7)], 1.6), ["#1a0f0b", "#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544"], 1.2, LUZ)
    lz.sombrear(lz.circulo(bx, 6.5, 1.8), ["#1b1c1f", "#3d3f43", "#6a6c6f", "#a3a4a6"], 1, LUZ)
    lz.pintar(lz.trazo([(bx + 1.2, 7), (bx + 1.4, 33)], 0.45), CUERDA)
    fardo = lz.elipse(bx + 1.4, 36, 4, 3.4)
    lz.sombrear(fardo, ["#4a3a22", "#6a5232", "#8a6e46", "#a88a5e", "#c8aa7a"], 2.4, LUZ)
    lz.pintar(((np.abs((lz.x + lz.y) % 2.4) < 0.3) | (np.abs((lz.x - lz.y) % 2.4) < 0.3)) * fardo, CUERDA, 0.8)
    # el portón abierto: dentro, penumbra con sacos y barriles; una hoja abierta hacia fuera
    px0, px1 = 30, 56
    lz.sombrear(rect(lz, px0 - 2, 58, px1 + 2, 60), ["#1a0f0b", "#2a1a12", "#47291c", "#643a26", "#7f4d33"], 1, LUZ)
    hueco = rect(lz, px0, 60, px1, 100)
    lz.pintar(hueco, "#0e0a08")
    lz.sumar_luz(lz.desenfocar(rect(lz, px0 + 3, 66, px1 - 3, 96), 4), "#5a3a1a", 0.35)
    for (sx, sy) in ((36, 96), (43, 97), (39, 90), (50, 96)):
        lz.sombrear(lz.elipse(sx, sy, 3.8, 3), ["#2a2014", "#3e3020", "#54422c", "#6a5638"], 2, LUZ)
    lz.sombrear(rect(lz, 47, 84, 54, 94), ["#1a0f0b", "#2a1a12", "#47291c", "#643a26"], 2, LUZ)
    hoja = lz.poligono([(px1, 60), (px1 + 9, 62), (px1 + 9, 102), (px1, 100)])
    tabl = (np.abs(np.sin((lz.x - px1) / 3 * np.pi)) < 0.12).astype(float)
    lz.sombrear(hoja, ["#251812", "#3d2418", "#5a3826", "#7a4e35", "#9a6847"], 3, LUZ, textura=vetas(lz, 0.5, 15, False) * (1 - tabl * 0.8), fuerza_tex=0.45)
    for by_ in (68, 92):
        lz.sombrear(lz.poligono([(px1 + 0.5, by_ - 1), (px1 + 8, by_), (px1 + 8, by_ + 1.2), (px1 + 0.5, by_ + 1)]), ["#1b1c1f", "#3d3f43", "#6a6c6f"], 0.6, LUZ)
    # el letrero del pez, sobre el portón
    letrero = rect(lz, 34, 49, 52, 56)
    lz.sombrear(letrero, COBRE, 1.2, LUZ, textura=vetas(lz, 0.5, 9), fuerza_tex=0.3)
    lz.pintar(lz.elipse(42, 52.5, 4.6, 1.8), "#4c8d8d")
    lz.pintar(lz.poligono([(46, 52.5), (49, 50.5), (49, 54.5)]), "#4c8d8d")
    lz.pintar(lz.circulo(39.5, 52, 0.5), "#1a1418")
    for (cx, cy) in ((35.5, 49.5), (50.5, 49.5)):
        lz.pintar(lz.trazo([(cx, cy), (cx, 46)], 0.4), "#1a120c")
    # la ventana con contraventanas y jardinera
    ventana(lz, 80, 62, 96, 76, encendida=0.4, semilla=331, luz=LUZ)
    # delante: barriles, cajas, sacos, un tendedero de redes y una carretilla
    for (bx2, by2) in ((10, 102), (19, 103)):
        tonel = lz.elipse(bx2, by2 - 6, 5, 6.4)
        duelas = (np.abs(np.sin((lz.x - bx2) / 2.2 * np.pi)) < 0.12).astype(float)
        lz.sombrear(tonel, ["#1a0f0b", "#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259"], 3.5, LUZ, textura=1 - duelas * 0.7, fuerza_tex=0.4)
        for yy in (by2 - 10, by2 - 2.5):
            lz.pintar(np.clip(1 - np.abs(lz.y - yy - (np.abs(lz.x - bx2) / 5) ** 2 * 0.6) / 0.6, 0, 1) * tonel, "#3d3f43")
        lz.sombrear(lz.elipse(bx2, by2 - 12, 4.4, 1.3), ["#5a3a22", "#8a6440", "#b38c5c", "#d2ac78"], 1, LUZ)
    for (cx, cy, w, h_) in ((98, 92, 12, 10), (104, 82, 9, 9)):
        caja = rect(lz, cx, cy, cx + w, cy + h_)
        lz.sombrear(caja, COBRE, 2, LUZ, textura=vetas(lz, 0.5, 11), fuerza_tex=0.35)
        lz.pintar(lz.trazo([(cx, cy), (cx + w, cy + h_)], 0.5) + lz.trazo([(cx + w, cy), (cx, cy + h_)], 0.5), "#47291c", 0.85)
    for (sx, sy) in ((114, 100), (121, 101)):
        saco = lz.poligono([(sx - 5, sy + 1), (sx - 5.5, sy - 5), (sx - 2.5, sy - 9), (sx + 2.5, sy - 9), (sx + 5.5, sy - 5), (sx + 5, sy + 1)])
        lz.sombrear(saco, ["#5a4630", "#8a7454", "#b8a07a", "#d8c49c", "#efe0bf"], 3.5, LUZ, textura=(np.sin(lz.x * 4) * np.sin(lz.y * 4) > 0).astype(float), fuerza_tex=0.15)
        lz.pintar(lz.trazo([(sx - 2.5, sy - 7.5), (sx + 2.5, sy - 7.5)], 0.8), "#47291c")
    # el tendedero de redes (dos palos y la red colgando, con flotadores)
    for x in (114, 127):
        lz.sombrear(lz.trazo([(x, 92), (x, 60)], 0.9), MADERA[3:8], 0.7, LUZ)
    red = lz.poligono([(114, 62), (127, 62), (126, 84), (115, 84)])
    lz.pintar(((np.abs((lz.x + lz.y) % 2.4) < 0.35) | (np.abs((lz.x - lz.y) % 2.4) < 0.35)) * red, "#d8c8a0", 0.85)
    for x in (116, 120.5, 125):
        lz.sombrear(lz.circulo(x, 62.5, 1.1), ["#8f2532", "#d5525e", "#f4b39a"], 0.8, LUZ)
    # la carretilla, con un par de peces encima
    rueda = lz.circulo(76, 99, 3.6)
    lz.sombrear(np.clip(rueda - lz.circulo(76, 99, 2.4), 0, 1), ["#1a0f0b", "#2a1a12", "#47291c", "#643a26"], 1, LUZ)
    lz.sombrear(lz.poligono([(70, 90), (88, 89), (86, 96), (72, 97)]), COBRE, 1.6, LUZ, textura=vetas(lz, 0.5, 9), fuerza_tex=0.3)
    lz.sombrear(lz.trazo([(86, 93), (94, 99)], 0.7), MADERA[3:7], 0.6, LUZ)
    for fx in (76, 81):
        lz.sombrear(lz.elipse(fx, 88.5, 3.2, 1.2, -10), ["#1c3535", "#346161", "#4c8d8d", "#9fd0d0"], 1, LUZ)
    # hierba y florecitas al pie
    hierba = np.zeros((lz.H, lz.W))
    for kk in range(110):
        hx = rng.random() * 132
        if px0 - 2 < hx < px1 + 10:
            continue
        hy = 101 + rng.random() * 5
        hierba = np.maximum(hierba, lz.trazo([(hx, hy), (hx + (rng.random() - 0.5) * 2.4, hy - 2 - rng.random() * 3)], 0.8, 0.3))
    lz.sombrear(hierba, ["#1d2e18", "#2f4a22", "#3f5a2f", "#5d7a3c", "#7c9a4c", "#a8b866"], 0.5, LUZ)
    flores(lz, 6, (60, 102, 72, 106), [["#8f2532", "#d5525e", "#e98378"], ["#b2721a", "#df9022", "#f1c27a"]], semilla=332, tam=0.7)
    return lz.sprite(contorno=CONTORNO)


def transbordador(k):
    """La barcaza grande del río: casco ancho y plano, cubierta de tablas con barandilla, la caseta del barquero con
    su campana y una pértiga larga. Varado (0) está escorado, con algas, un boquete en el casco y la barandilla rota."""
    W, H = 120, 60
    lz = Lienzo(W, H, s=5, semilla=331 + k)
    inclina = 0.06 if k == 0 else 0.0
    cy = 40

    def y_(y, x):
        return y + (x - 60) * inclina

    # la sombra del casco en el agua
    lz.pintar(lz.desenfocar(lz.elipse(60, cy + 9, 56, 3.5), 1.2), AGUA[0], 0.55)
    # el casco: un costado largo, plano, con tablas horizontales
    casco = lz.poligono([(4, y_(cy - 6, 4)), (116, y_(cy - 6, 116)), (110, y_(cy + 8, 110)), (12, y_(cy + 8, 12))])
    tablas = np.sin((lz.y - (lz.x - 60) * inclina) * 1.8) * 0.5 + 0.5
    lz.sombrear(casco, MADERA[1:7], 4, LUZ, textura=tablas * 0.5 + vetas(lz, 0.4, 13, True, 332) * 0.5, fuerza_tex=0.5)
    lz.pintar(casco * (np.abs(np.sin((lz.y - (lz.x - 60) * inclina) * 1.8)) < 0.14), MADERA[0], 0.8)
    if k == 0:
        # algas y verdín por la línea de agua, y el boquete
        algas = casco * (lz.y > y_(cy + 3, lz.x)) * (lz.ruido(0.8, 2, semilla=333) > 0.4)
        lz.pintar(algas, "#2e4a2a", 0.8)
        boquete = lz.elipse(78, y_(cy + 1, 78), 5, 3)
        lz.pintar(boquete, "#0a0806")
        for a in range(8):
            ang = a * np.pi / 4
            lz.pintar(lz.trazo([(78 + np.cos(ang) * 4, y_(cy + 1, 78) + np.sin(ang) * 2.4),
                                (78 + np.cos(ang) * 6.5, y_(cy + 1, 78) + np.sin(ang) * 3.6)], 0.5), MADERA[5])
    # la línea de agua (el agua tapa el fondo del casco)
    linea = y_(cy + 5 if k == 0 else cy + 6, lz.x)
    agua = casco * (lz.y > linea)
    lz.pintar(agua, AGUA[2], 0.9)
    onda = np.clip(1 - np.abs(lz.y - linea - 0.3) / 0.5, 0, 1) * (lz.x > 6) * (lz.x < 114) * (np.sin(lz.x * 0.7) > -0.3)
    lz.pintar(onda, AGUA[5], 0.8)
    # la cubierta, que se ve desde arriba
    cubierta = lz.poligono([(6, y_(cy - 6, 6)), (114, y_(cy - 6, 114)), (110, y_(cy - 14, 110)), (10, y_(cy - 14, 10))])
    lz.sombrear(cubierta, MADERA[3:8], 2, LUZ, textura=((lz.x % 5) < 0.6) * 1.0, fuerza_tex=-0.4)
    lz.pintar(lz.trazo([(4, y_(cy - 6, 4)), (116, y_(cy - 6, 116))], 0.8), MADERA[7])
    # la barandilla: postes y un pasamanos (rota en el varado)
    for x in range(10, 112, 8):
        if k == 0 and 60 < x < 84:
            continue
        lz.pintar(lz.trazo([(x, y_(cy - 7, x)), (x, y_(cy - 12, x))], 0.6), MADERA[5])
    tramos = [(10, 58), (86, 110)] if k == 0 else [(10, 110)]
    for (a, b) in tramos:
        lz.pintar(lz.trazo([(a, y_(cy - 12, a)), (b, y_(cy - 12, b))], 0.6), MADERA[6])
    if k == 0:
        lz.pintar(lz.trazo([(58, y_(cy - 12, 58)), (64, y_(cy - 7, 64))], 0.6), MADERA[6])     # el pasamanos caído
    # la caseta del barquero, con su tejadillo de juncos, una ventana y la campana
    cx = 40
    caseta = rect(lz, cx - 9, y_(cy - 30, cx), cx + 9, y_(cy - 11, cx))
    lz.sombrear(caseta, MADERA[2:7], 4, LUZ, textura=vetas(lz, 0.45, 13, False, 334), fuerza_tex=0.4)
    lz.pintar(caseta * ((lz.x % 3.5) < 0.5), MADERA[0], 0.7)
    ventana = rect(lz, cx - 4, y_(cy - 25, cx), cx + 4, y_(cy - 19, cx))
    lz.pintar(ventana, "#f9b947" if k == 1 else "#140e0a")
    if k == 1:
        lz.brillo(ventana, "#f9b947", 2.5, 0.5)
    techo = lz.poligono([(cx - 13, y_(cy - 29, cx)), (cx, y_(cy - 38, cx)), (cx + 13, y_(cy - 29, cx))])
    lz.sombrear(techo, JUNCO, 4, LUZ, textura=np.sin(lz.x * 3.1 + lz.y * 0.9) * 0.5 + 0.5, fuerza_tex=0.4)
    if k == 0:
        lz.pintar(lz.elipse(cx + 5, y_(cy - 32, cx), 2.6, 1.4), "#1a120c")             # un agujero en el tejadillo
    campana_y = y_(cy - 33, cx + 16)
    lz.pintar(lz.trazo([(cx + 13, y_(cy - 29, cx)), (cx + 17, campana_y - 1)], 0.5), MADERA[4])
    lz.sombrear(lz.poligono([(cx + 15, campana_y + 4), (cx + 16, campana_y), (cx + 18, campana_y), (cx + 19, campana_y + 4)]),
                ["#5a4210", "#8a6a20", "#c09a40", "#e8c868"], 1.5, LUZ)
    # la pértiga larga, apoyada en la cubierta (en el varado, caída al agua)
    if k == 1:
        lz.sombrear(lz.trazo([(60, y_(cy - 9, 60)), (110, y_(cy - 30, 110))], 0.8), MADERA[4:8], 0.6, LUZ)
    else:
        lz.sombrear(lz.trazo([(90, y_(cy - 9, 90)), (118, y_(cy + 10, 118))], 0.8), MADERA[3:7], 0.6, LUZ)
    # unas cuerdas de amarre enrolladas y un par de cajas en cubierta
    for r in (2.2, 1.5):
        lz.pintar(np.clip(lz.elipse(98, y_(cy - 9, 98), r * 1.5, r * 0.6) - lz.elipse(98, y_(cy - 9, 98), r * 1.5 - 0.4, r * 0.6 - 0.3), 0, 1), CUERDA)
    lz.sombrear(rect(lz, 16, y_(cy - 17, 16), 24, y_(cy - 9, 16)), MADERA[3:8], 2, LUZ)
    return lz.sprite(contorno=CONTORNO)


def poste(k):
    """Un poste de amarre alto y gordo, de madera clara gastada por el sol (para que se vea bien sobre la plataforma
    oscura: es donde Mamba se clava), con un anillo de cuerda clara y la cabeza redondeada."""
    W, H = 22, 44
    lz = Lienzo(W, H, s=8, semilla=341 + k)
    claro = ["#4a3a2a", "#6e5a40", "#8e7656", "#ae9670", "#c8b28a", "#e2d0a8"]
    lz.pintar(lz.desenfocar(lz.elipse(11, 41, 9, 2.4), 0.6), "#0e0c0a", 0.55)
    tronco = rect(lz, 5, 8, 17, 41)
    lz.sombrear(tronco, claro, 6, LUZ, textura=vetas(lz, 0.5, 9, False, 342), fuerza_tex=0.5)
    lz.pintar(tronco * ((lz.x % 3.2) < 0.35), claro[1], 0.5)                         # las grietas de la madera
    lz.sombrear(lz.elipse(11, 8, 6, 2.4), claro[2:], 2, LUZ)                         # la cabeza, redondeada
    for r in (4.2, 2.8, 1.4):
        lz.pintar(np.clip(lz.elipse(11, 8, r, r * 0.4) - lz.elipse(11, 8, r - 0.45, r * 0.4 - 0.18), 0, 1), claro[1], 0.7)
    for y in (16, 19):                                                                # el anillo de cuerda, claro
        lz.pintar(lz.trazo([(4.6, y), (17.4, y + 0.7)], 1.1), "#e8d8a8")
        lz.pintar(lz.trazo([(4.6, y + 0.6), (17.4, y + 1.3)], 0.4), "#8a7048")
    lz.pintar(lz.trazo([(16.5, 20), (19, 26), (18, 31)], 0.6), "#e8d8a8")             # el cabo que cuelga
    lz.pintar(rect(lz, 5, 35, 17, 41), "#3e5a34", 0.5)                               # el verdín del pie
    if k == 1:
        # las marcas de los dientes, en dos filas, y astillas levantadas
        for j in range(5):
            for fila in (24, 30):
                lz.pintar(lz.poligono([(5.6 + j * 2.4, fila), (6.6 + j * 2.4, fila + 2.2), (7.6 + j * 2.4, fila)]), "#1a120c")
        for (x, y) in ((4.5, 27), (17.5, 29), (17, 23)):
            lz.pintar(lz.trazo([(x, y), (x + (-2 if x < 11 else 2), y - 2.5)], 0.5), claro[5])
    return lz.sprite(contorno=CONTORNO)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    tira([casa_juncos(k) for k in range(2)]).save(os.path.join(SALIDA, "casa_juncos.png"))
    Image.fromarray(grua()).save(os.path.join(SALIDA, "grua.png"))
    Image.fromarray(almacen()).save(os.path.join(SALIDA, "almacen.png"))
    tira([transbordador(k) for k in range(2)]).save(os.path.join(SALIDA, "transbordador.png"))
    tira([poste(k) for k in range(2)]).save(os.path.join(SALIDA, "poste.png"))
    print("Objetos del Embarcadero Junco en", SALIDA)


if __name__ == "__main__":
    main()
