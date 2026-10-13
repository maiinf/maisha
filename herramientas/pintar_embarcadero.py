"""LOS OBJETOS DEL EMBARCADERO JUNCO, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_embarcadero.py

Genera (en arte/mundos/raiz/embarcadero/):
  casa_juncos.png     2 × 100×92  las casas de los barqueros, al nivel de detalle de la casa del castor: pilotes con
                                  verdín, plataforma de tablas, paredes de esteras con armazón de troncos, tejado de
                                  paja a capas, ventana con contraventanas y jardinera, porche, escalerilla, barquita
                                  amarrada y cosas de barquero (redes, remos, nasa, peces, cántaros, farolillo)
  casa_bata.png       100×92      la casa del barquero Bata, en tierra junto al muelle: como las de juncos, pero
                                  sobre el barro, con el letrero del transbordador, remos cruzados y la campana
  sello_raices.png    2 × 100×92  las raíces de piedra de Giza que sellan su puerta y su ventana: 0 enteras,
                                  1 resquebrajadas
  nudo_giza.png       2 × 28×26   el nudo de Giza escondido en el almacén (late)
  saco.png            2 × 18×18   sacos de grano que lo tapan (se apartan con el Latido)
  barca_bata.png      2 × 48×26   la barca de remos de Bata, a flote (Bata va encima en la pelea contra Mamba)
  grua.png            72×104      la grúa del muelle, rota: base de piedras, poste de tronco con tornapuntas, pluma
                                  rajada y atada, polea partida con el gancho, torno bajo un tejadillo de paja, un
                                  nido arriba; al pie, el fardo de red, un tonel y cabos
  almacen.png         132×108     el almacén, al nivel de la casa del castor: zócalo de piedra, troncos, tejado de
                                  paja con buhardilla de carga y polea, portón abierto, letrero del pez, ventana,
                                  barriles, cajas, sacos, tendedero de redes y carretilla
  poste.png           2 × 22×44   un poste de amarre de la dársena (alto, de madera clara, con anillo de cuerda): 0 entero,
                                  1 mordido por Mamba (con las marcas de los dientes y astillas)
  transbordador.png   3 × 160×84  el TRANSBORDADOR: barcaza de tablas con la proa levantada, barandilla de cuerda,
                                  caseta de troncos con tejado de paja, ventana, campana, farol de proa, bandera,
                                  pértiga y carga. 0 varado (escorado, boquete, algas, barandilla rota), 1 arreglado
                                  (parche de juncos tejidos, farol y ventana encendidos), 2 tapado pero aún escorado
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
BX = 26                                   # dónde está el boquete del transbordador (en su dibujo): del lado del muelle
GIZA_V = ["#2a0d3a", "#3a1650", "#6b2a8f", "#a855d6", "#d6a8f0"]


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


def casa_juncos(k, bata=False):
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
    if bata:
        # en tierra: la sombra de la casa sobre el barro de la orilla, con charcos y juncos
        lz.pintar(lz.desenfocar(lz.elipse(50, 86, 46, 5), 1.2), "#0e0c0a", 0.5)
        for (cx, cy, rx) in ((30, 87, 9), (70, 88, 7)):
            charco = lz.elipse(cx, cy, rx, 1.8)
            lz.pintar(charco, AGUA[2], 0.8)
            lz.pintar(charco * (lz.x < cx - rx * 0.3), AGUA[5], 0.5)
        for x in (4, 7, 92, 96):
            lz.pintar(lz.trazo([(x, 90), (x + 1, 76)], 0.6) + lz.trazo([(x + 2, 90), (x + 1.5, 79)], 0.5), JUNCO[3])
    else:
        # el agua al pie, con sombra de la casa y reflejos
        agua = lz.poligono([(0, 78), (100, 74), (100, 92), (0, 92)])
        lz.sombrear(agua, AGUA, 4, LUZ, textura=(np.sin(lz.y * 1.6 + lz.x * 0.25) * 0.5 + 0.5), fuerza_tex=0.35)
        lz.pintar(lz.desenfocar(rect(lz, 8, 76, 92, 92), 3) * agua, "#0a1414", 0.45)
        ondas = (np.abs(np.sin(lz.x * 0.45 + lz.y * 1.9)) < 0.08) * agua
        lz.pintar(ondas, AGUA[5], 0.5)
    # la barquita amarrada debajo, entre los pilotes
    barca = lz.poligono([(18, 80), (52, 79), (48, 85), (22, 86)]) * (0.0 if bata else 1.0)
    lz.sombrear(barca, MADERA[1:7], 2, LUZ, textura=vetas(lz, 0.5, 9, True, 303 + k), fuerza_tex=0.4)
    if not bata:
        lz.pintar(lz.poligono([(21, 80.4), (49, 79.6), (46.5, 81.6), (23, 82)]), "#1a120c")
        lz.pintar(lz.trazo([(18, 80), (52, 79)], 0.6), MADERA[7])
    if not bata:
        lz.pintar(barca * (lz.y > 83) * (np.sin(lz.x * 0.8) > 0), "#4c8d8d", 0.5)      # pintura azul desconchada
        lz.pintar(lz.trazo([(50, 79.5), (58, 68)], 0.4), CUERDA)
    # los pilotes, con verdín y el agua al pie
    for x in (10, 26, 42, 58, 74, 90):
        p = rect(lz, x - 2.2, plat_y, x + 2.2, abajo)
        lz.sombrear(p, ["#1a0f0b", "#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544"], 2.2, LUZ,
                    textura=vetas(lz, 0.6, 11, False, int(x)), fuerza_tex=0.4)
        lz.pintar(rect(lz, x - 2.2, 74, x + 2.2, 80) * (lz.ruido(0.6, 2, semilla=int(x)) > 0.35), "#2e4a2a" if not bata else "#3a2a1a", 0.75)
        lz.pintar(lz.elipse(x, 78.5 if not bata else 88, 3.4, 0.9), AGUA[5] if not bata else "#2a1a10", 0.7)
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
    if bata:
        # el letrero del transbordador sobre la puerta (una barcaza tallada) y dos remos cruzados en la pared
        letrero = rect(lz, px - 3, 31, px + 15, 36)
        lz.sombrear(letrero, COBRE, 1, LUZ, textura=vetas(lz, 0.5, 9), fuerza_tex=0.3)
        lz.pintar(lz.poligono([(px, 34.5), (px + 12, 34.5), (px + 13.5, 32.5), (px - 1.5, 32.5)]), "#47291c")
        lz.pintar(rect(lz, px + 3, 31.5, px + 6, 33), "#47291c")
        for (a_, b_) in (((58, 33), (72, 52)), ((72, 33), (58, 52))):
            lz.sombrear(lz.trazo([a_, b_], 0.8), MADERA[4:8], 0.6, LUZ)
        for (ex, ey) in ((59, 50.5), (71, 50.5)):
            lz.sombrear(lz.elipse(ex, ey, 1.6, 3.2), MADERA[4:8], 1, LUZ)
        # la campana del barquero, colgada del porche
        lz.pintar(lz.trazo([(10, plat_y - 14), (10, plat_y - 18)], 0.5), "#1a120c")
        lz.sombrear(lz.poligono([(7.6, plat_y - 9), (8.6, plat_y - 14), (11.4, plat_y - 14), (12.4, plat_y - 9)]),
                    ["#5a4210", "#8a6a20", "#c09a40", "#e8c868", "#fff1c0"], 1.4, LUZ)
        # rollos de cuerda de amarre
        for (cx, cy) in ((80, plat_y - 4), (87, plat_y - 4.5)):
            for r in (2.6, 1.7, 0.8):
                lz.pintar(np.clip(lz.elipse(cx, cy, r * 1.5, r * 0.65) - lz.elipse(cx, cy, r * 1.5 - 0.5, r * 0.65 - 0.3), 0, 1), CUERDA)
    # una maceta con flores junto a la puerta
    mx = px + 15 if k == 0 else px - 4
    lz.sombrear(lz.poligono([(mx - 2.5, plat_y - 7), (mx + 2.5, plat_y - 7), (mx + 1.8, plat_y - 3), (mx - 1.8, plat_y - 3)]), COBRE, 1.2, LUZ)
    flores(lz, 5, (mx - 3, plat_y - 10, mx + 3, plat_y - 7), [["#8f2532", "#d5525e", "#e98378"], ["#b2721a", "#df9022", "#f1c27a"]], semilla=308 + k, tam=0.7)
    return lz.sprite(contorno=CONTORNO)


def grua():
    """La grúa del muelle, rota, al nivel de la casa del castor: una base de piedras con musgo, un poste de tronco
    grueso con sus tornapuntas, la pluma inclinada sobre el agua (rajada y atada con cuerda), la polea de hierro partida
    con el gancho colgando, el torno de manivela bajo un tejadillo de paja con la cuerda enrollada, un nido en lo alto
    y, al pie, el fardo de red que se cayó, un tonel y unos cabos."""
    W, H = 72, 104
    lz = Lienzo(W, H, s=4, semilla=311)
    TR = ["#1a0f0b", "#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259"]
    lz.pintar(lz.desenfocar(lz.elipse(24, 100, 20, 3), 0.8), "#0e0c0a", 0.5)
    # la base de piedras
    base = lz.poligono([(8, 100), (10, 88), (16, 85), (32, 85), (38, 88), (40, 100)])
    piedras(lz, base, tam=4.2, semilla=312, luz=LUZ, mortero="#525449",
            rampa_p=["#3a3b33", "#5a5d50", "#7a806d", "#9aa08c", "#b9bdaa", "#d6d8c8"])
    lz.pintar(lz.desenfocar((lz.ruido(2.5, 3, semilla=313) > 0.62) * base, 0.3), "#3f5a2f", 0.75)
    # el poste, un tronco gordo, y dos tornapuntas
    poste = rect(lz, 20, 14, 28, 88)
    lz.sombrear(poste, TR, 4, LUZ, textura=vetas(lz, 0.6, 15, False, 314), fuerza_tex=0.5)
    for lado in (-1, 1):
        t = lz.trazo([(24 + lado * 14, 87), (24 + lado * 3, 62)], 2.0, 1.4)
        lz.sombrear(t, TR[1:], 1.4, LUZ, textura=vetas(lz, 0.6, 9, False, 315), fuerza_tex=0.4)
    for y in (30, 60):
        lz.pintar(lz.trazo([(19.5, y), (28.5, y + 0.8)], 0.8), CUERDA)
    # la pluma, inclinada hacia el agua, rajada y atada con cuerda
    pluma = lz.trazo([(24, 22), (68, 8)], 2.6, 1.8)
    lz.sombrear(pluma, TR, 2.2, LUZ, textura=vetas(lz, 0.6, 15, True, 316), fuerza_tex=0.45)
    lz.pintar(lz.trazo([(52, 13.5), (58, 11.4)], 0.4), "#0e0a08")
    for x in (49, 51.5):
        lz.pintar(lz.trazo([(x, 11), (x + 0.8, 17)], 0.7), CUERDA)
    lz.pintar(lz.trazo([(24, 40), (60, 10.5)], 0.7), CUERDA)                       # el tirante
    # el nido en la punta del poste, con ramitas
    nido = lz.elipse(24, 12, 7, 3)
    lz.pintar(nido * (np.sin(lz.x * 3 + lz.y * 5) > -0.2), "#5a4426")
    lz.pintar(np.clip(nido - lz.elipse(24, 11.4, 5, 1.6), 0, 1), "#7a5a32")
    for (a, b) in ((17, 10), (31, 9), (19, 14), (29, 14.5)):
        lz.pintar(lz.trazo([(24, 12), (a, b)], 0.35), "#6a4e2a")
    # la polea de hierro, partida, y la cuerda con el gancho
    lz.sombrear(lz.circulo(65, 10, 3.2), ["#1b1c1f", "#3d3f43", "#6a6c6f", "#a3a4a6"], 2, LUZ)
    lz.pintar(lz.circulo(65, 10, 1.0), "#1b1c1f")
    lz.pintar(lz.trazo([(65, 7), (67.5, 12.5)], 0.6), "#8a3a1a")
    cuerda = lz.trazo(lz.curva((66.5, 13), (68, 34), (63, 50), n=24), 0.45)
    lz.pintar(cuerda, CUERDA)
    gancho = np.clip(lz.circulo(63, 53.5, 2.6) - lz.circulo(63.7, 53, 1.6), 0, 1) * (lz.x < 64.8)
    lz.sombrear(gancho + lz.trazo([(63, 50), (63, 51.5)], 0.7), ["#1b1c1f", "#3d3f43", "#6a6c6f", "#a3a4a6"], 1, LUZ)
    # el torno de manivela bajo su tejadillo de paja
    tambor = rect(lz, 30, 66, 44, 74)
    lz.sombrear(tambor, TR[1:], 3, LUZ, textura=vetas(lz, 0.5, 9, False, 317), fuerza_tex=0.4)
    for x in np.arange(31, 44, 1.3):
        lz.pintar(lz.trazo([(x, 66.5), (x + 0.6, 73.5)], 0.4), CUERDA, 0.9)
    lz.sombrear(rect(lz, 29, 64, 31, 80) + rect(lz, 43, 64, 45, 80), TR[2:], 1, LUZ)
    lz.pintar(lz.trazo([(45, 70), (49, 66), (50, 67.5)], 0.8), "#3d3f43")
    lz.sombrear(lz.circulo(50.5, 68, 1.1), ["#3d2418", "#7a4e35", "#9a6847"], 0.8, LUZ)
    techo = lz.poligono([(26, 64), (37, 56), (48, 64), (47, 66), (27, 66)])
    paja(lz, techo, semilla=318, capas=3.0, y0=56)
    flecos(lz, 26, 48, 65.5, 1.6, semilla=319)
    # al pie: el fardo de red caído, un tonel y unos cabos enrollados
    fardo = lz.elipse(52, 96, 9, 6)
    lz.sombrear(fardo, ["#4a3a22", "#6a5232", "#8a6e46", "#a88a5e", "#c8aa7a"], 4, LUZ, textura=lz.ruido(0.6, 2, semilla=320), fuerza_tex=0.4)
    lz.pintar(((np.abs((lz.x + lz.y) % 2.4) < 0.3) | (np.abs((lz.x - lz.y) % 2.4) < 0.3)) * fardo, CUERDA, 0.8)
    for x in (47, 55):
        lz.sombrear(lz.circulo(x, 91.5, 1.1), ["#8f2532", "#d5525e", "#f4b39a"], 0.8, LUZ)
    tonel = lz.elipse(6, 95, 4.6, 5.8)
    duelas = (np.abs(np.sin((lz.x - 6) / 2.2 * np.pi)) < 0.12).astype(float)
    lz.sombrear(tonel, TR, 3, LUZ, textura=1 - duelas * 0.7, fuerza_tex=0.4)
    lz.sombrear(lz.elipse(6, 89.5, 4.1, 1.2), ["#5a3a22", "#8a6440", "#b38c5c", "#d2ac78"], 1, LUZ)
    for r in (3.2, 2.2, 1.2):
        lz.pintar(np.clip(lz.elipse(64, 100, r * 1.6, r * 0.7) - lz.elipse(64, 100, r * 1.6 - 0.5, r * 0.7 - 0.35), 0, 1), CUERDA)
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
    # k: 0 varado (escorado, con boquete), 1 arreglado y a flote, 2 con el boquete tapado pero aún escorado
    parcheado = k in (1, 2)
    recto = k == 1
    """El transbordador, al nivel de la casa del castor: una barcaza grande de tablas con la proa levantada, la
    cubierta con barandilla de postes y cuerda, la caseta del barquero de troncos con tejado de paja, su ventana
    (encendida si navega) y la campana; una pértiga larga, un farol en la proa, una bandera, rollos de cuerda, cajas y
    sacos. 0 varado: escorado, con un boquete en el casco, algas, la barandilla rota, agujeros en la paja y la pértiga
    en el agua; 1 arreglado y a flote, con un parche de juncos tejidos donde estaba el boquete."""
    W, H = 160, 84
    lz = Lienzo(W, H, s=4, semilla=331 + k)
    TR = ["#1a0f0b", "#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259"]
    inclina = 0.0 if recto else 0.07
    cy = 58

    def y_(y, x):
        return y + (x - 80) * inclina

    lz.pintar(lz.desenfocar(lz.elipse(80, cy + 13, 76, 4.5), 1.2), AGUA[0], 0.55)
    # el casco: un costado largo con tablas, la proa (derecha) levantada
    casco = lz.poligono([(4, y_(cy - 8, 4)), (140, y_(cy - 8, 140)), (156, y_(cy - 14, 156)), (150, y_(cy + 4, 150)),
                         (138, y_(cy + 11, 138)), (14, y_(cy + 11, 14))])
    tablas = np.sin((lz.y - (lz.x - 80) * inclina) * 1.5) * 0.5 + 0.5
    lz.sombrear(casco, TR[1:], 5, LUZ, textura=tablas * 0.5 + vetas(lz, 0.5, 15, True, 332) * 0.5, fuerza_tex=0.5)
    lz.pintar(casco * (np.abs(np.sin((lz.y - (lz.x - 80) * inclina) * 1.5)) < 0.13), "#120b08", 0.85)
    for x in range(14, 140, 9):                                                           # los clavos
        for yy in (cy - 4, cy + 3):
            lz.pintar(lz.circulo(x, y_(yy, x), 0.45), "#6a6c6f")
    lz.pintar(lz.trazo([(4, y_(cy - 8, 4)), (140, y_(cy - 8, 140)), (156, y_(cy - 14, 156))], 1.0), TR[6])
    # una franja de pintura azul a lo largo del casco (desconchada)
    franja = casco * (np.abs(lz.y - y_(cy - 1, lz.x)) < 1.6) * (lz.ruido(1.2, 2, semilla=333) > 0.35)
    lz.pintar(franja, "#4c8d8d", 0.85)
    if not recto:
        algas = casco * (lz.y > y_(cy + 5, lz.x)) * (lz.ruido(0.8, 2, semilla=334) > 0.35)
        lz.pintar(algas, "#2e4a2a", 0.85)
    if not parcheado:
        boquete = lz.elipse(BX, y_(cy + 2, BX), 7, 4)
        lz.pintar(boquete, "#0a0806")
        for a in range(10):
            ang = a * np.pi / 5
            lz.pintar(lz.trazo([(BX + np.cos(ang) * 5.5, y_(cy + 2, BX) + np.sin(ang) * 3.2),
                                (BX + np.cos(ang) * 8.5, y_(cy + 2, BX) + np.sin(ang) * 5)], 0.6), TR[5])
    else:
        # el parche de juncos tejidos que tapa el boquete (los hizo crecer una semilla de Maisha)
        parche = lz.elipse(BX, y_(cy + 2, BX), 8, 4.6)
        lz.sombrear(parche, ["#3d3214", "#5c4a22", "#7a6431", "#958043", "#b09c5c", "#c9b77d"], 3, LUZ,
                    textura=(np.sin(lz.x * 2.2) * np.sin(lz.y * 2.2) > 0).astype(float), fuerza_tex=0.5)
        lz.pintar(np.clip(parche - lz.elipse(BX, y_(cy + 2, BX), 7, 3.6), 0, 1), CUERDA)
        for j in range(5):
            lz.pintar(lz.trazo([(BX - 6 + j * 3, y_(cy - 2, BX)), (BX - 7 + j * 3.2, y_(cy - 7 - j % 2 * 2, BX))], 0.5), "#6fcf4f")
    # la línea de flotación y las ondas
    linea = y_(cy + (8 if recto else 6), lz.x)
    lz.pintar(casco * (lz.y > linea), AGUA[2], 0.9)
    lz.pintar(np.clip(1 - np.abs(lz.y - linea - 0.3) / 0.6, 0, 1) * (lz.x > 6) * (lz.x < 152) * (np.sin(lz.x * 0.6) > -0.3), AGUA[5], 0.85)
    # la cubierta, vista desde arriba
    cubierta = lz.poligono([(6, y_(cy - 8, 6)), (140, y_(cy - 8, 140)), (154, y_(cy - 14, 154)), (148, y_(cy - 22, 148)),
                            (136, y_(cy - 18, 136)), (12, y_(cy - 18, 12))])
    tabl = (np.abs(np.sin(lz.x / 5 * np.pi)) < 0.1).astype(float)
    lz.sombrear(cubierta, ["#2a1c14", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259"], 2, LUZ,
                textura=1 - tabl * 0.9 + vetas(lz, 0.5, 13) * 0.2, fuerza_tex=0.5)
    # la barandilla: postes y una cuerda (rota en el varado)
    for x in range(10, 150, 9):
        if not recto and 84 < x < 118:
            continue
        top = y_(cy - 17 if x < 138 else cy - 22, x)
        lz.sombrear(rect(lz, x - 0.7, top - 6, x + 0.7, top + 1), TR[3:], 0.6, LUZ)
    tramos = [(10, 146)] if recto else [(10, 82), (118, 146)]
    for (a, b) in tramos:
        pts = [(x, y_(cy - 22.5, x) + (np.sin((x - a) / 9 * np.pi) * 0.6 if True else 0)) for x in np.linspace(a, b, 30)]
        lz.pintar(lz.trazo(pts, 0.6), CUERDA)
    if not recto:
        lz.pintar(lz.trazo([(82, y_(cy - 22.5, 82)), (88, y_(cy - 10, 88)), (92, y_(cy + 6, 92))], 0.6), CUERDA)
    # la caseta del barquero: troncos, tejado de paja, ventana y la campana
    cx0, cx1 = 34, 64
    troncos(lz, cx0, cx1, y_(cy - 46, 49), y_(cy - 18, 49), alto=4.6, semilla=335)
    puertita = rect(lz, cx0 + 4, y_(cy - 38, 40), cx0 + 11, y_(cy - 18, 40))
    lz.pintar(puertita, "#120c08")
    ventana(lz, cx0 + 16, y_(cy - 40, 55), cx0 + 26, y_(cy - 31, 55), encendida=0.75 if recto else 0.0, contras=False, semilla=336, luz=LUZ)
    tej = lz.poligono([(cx0 - 6, y_(cy - 44, cx0)), (49, y_(cy - 62, 49)), (cx1 + 6, y_(cy - 44, cx1)), (cx1 + 6, y_(cy - 41, cx1)), (cx0 - 6, y_(cy - 41, cx0))])
    paja(lz, tej, semilla=337, capas=4.0, y0=cy - 62)
    flecos(lz, cx0 - 6, cx1 + 6, y_(cy - 41.5, 49), 2.2, semilla=338)
    if not recto:
        lz.pintar(lz.elipse(56, y_(cy - 50, 56), 3.4, 1.8), "#120c08")
        for x in (54, 56, 58):
            lz.pintar(lz.trazo([(x, y_(cy - 52, x)), (x + 0.6, y_(cy - 49, x))], 0.4), "#a37036")
    by = y_(cy - 52, 70)
    lz.sombrear(lz.trazo([(66, y_(cy - 44, 66)), (66, by - 4), (72, by - 4)], 0.8), TR[2:], 0.6, LUZ)
    campana = lz.poligono([(69.5, by + 3), (70.5, by - 2), (73.5, by - 2), (74.5, by + 3)])
    lz.sombrear(campana, ["#5a4210", "#8a6a20", "#c09a40", "#e8c868", "#fff1c0"], 1.6, LUZ)
    lz.pintar(lz.circulo(72, by + 3.2, 0.6), "#5a4210")
    # el farol de la proa y la bandera
    fx, fy = 150, y_(cy - 28, 150)
    lz.sombrear(lz.trazo([(fx, y_(cy - 20, fx)), (fx, fy - 3)], 0.7), TR[3:], 0.6, LUZ)
    farol = rect(lz, fx - 2.2, fy - 2, fx + 2.2, fy + 3)
    lz.pintar(farol, rampa(["#47291c", "#a8380f", "#ef8a26", "#fde27e"] if recto else ["#1a1414", "#2a2420", "#3e3630", "#5a4e44"],
                           np.clip(1 - np.hypot(lz.x - fx, lz.y - fy) / 3, 0, 1)))
    if recto:
        lz.sumar_luz(lz.desenfocar(farol, 4), "#ef8a26", 0.45)
    lz.sombrear(lz.trazo([(16, y_(cy - 18, 16)), (16, y_(cy - 44, 16))], 0.7), TR[3:], 0.6, LUZ)
    bandera = lz.poligono([(16.5, y_(cy - 44, 16)), (26, y_(cy - 42, 26) + 1), (16.5, y_(cy - 38, 16))])
    lz.sombrear(bandera, ["#8f2532", "#b02531", "#d5525e", "#f4b39a"] if recto else ["#4a3a3a", "#6a5252", "#8a7070"], 1, LUZ)
    # la pértiga (en el arreglado, apoyada; en el varado, caída al agua) y la carga
    if recto:
        lz.sombrear(lz.trazo([(76, y_(cy - 12, 76)), (150, y_(cy - 46, 150))], 1.0), TR[3:], 0.8, LUZ)
    else:
        lz.sombrear(lz.trazo([(118, y_(cy - 12, 118)), (158, y_(cy + 14, 158))], 1.0), TR[2:], 0.8, LUZ)
    for r in (2.8, 1.9, 1.0):
        lz.pintar(np.clip(lz.elipse(124, y_(cy - 13, 124), r * 1.6, r * 0.65) - lz.elipse(124, y_(cy - 13, 124), r * 1.6 - 0.5, r * 0.65 - 0.3), 0, 1), CUERDA)
    for (bx, bw) in ((84, 10), (96, 8)):
        caja = rect(lz, bx, y_(cy - 24, bx), bx + bw, y_(cy - 15, bx))
        lz.sombrear(caja, COBRE, 1.6, LUZ, textura=vetas(lz, 0.5, 11), fuerza_tex=0.35)
        lz.pintar(lz.trazo([(bx, y_(cy - 24, bx)), (bx + bw, y_(cy - 15, bx))], 0.4), "#47291c", 0.8)
    saco = lz.elipse(110, y_(cy - 17, 110), 4.4, 3.4)
    lz.sombrear(saco, ["#5a4630", "#8a7454", "#b8a07a", "#d8c49c", "#efe0bf"], 2.5, LUZ)
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


def sello(k):
    """Las raíces de piedra de Giza que tapan la puerta y la ventana de la casa de Bata (encima de casa_bata.png, con
    el mismo tamaño). Bajan por los pilotes hasta el suelo, de donde salen las venas. 0 enteras, con grietas violetas
    que brillan; 1 resquebrajadas (al reventar el nudo), a punto de deshacerse."""
    W, H = 100, 92
    lz = Lienzo(W, H, s=4, semilla=351 + k)
    lz.alfa[:] = 0
    rng = np.random.default_rng(352)
    PIEDRA_G = ["#1c1a22", "#2c2a34", "#403c4a", "#57525f", "#6e6878", "#8a8494"]
    raices = np.zeros((lz.H, lz.W))
    # una maraña sobre la puerta (26..38, 38..59) y otra sobre la ventana (49..63, 36..49)
    for (x0, y0, x1, y1, n) in ((24, 36, 40, 60, 11), (47, 34, 65, 51, 8)):
        for j in range(n):
            a = (x0 + rng.random() * (x1 - x0), y0 - 2)
            b = (x0 + rng.random() * (x1 - x0), y1 + 1)
            m = (a[0] + (rng.random() - 0.5) * 10, (a[1] + b[1]) / 2)
            raices = np.maximum(raices, lz.trazo(lz.curva(a, m, b, n=16), 1.6 + rng.random() * 1.2, 0.8))
        for j in range(n // 2):
            y = y0 + rng.random() * (y1 - y0)
            raices = np.maximum(raices, lz.trazo([(x0 - 2, y), ((x0 + x1) / 2, y + (rng.random() - 0.5) * 6), (x1 + 2, y + 1)], 1.2, 0.6))
    # las que bajan por los pilotes hasta el suelo
    for x in (26, 42):
        raices = np.maximum(raices, lz.trazo(lz.curva((x + 4, 58), (x - 2, 72), (x + 1, 90), n=18), 1.4, 0.9))
    lz.sombrear(raices, PIEDRA_G, 1.6, LUZ, textura=lz.ruido(0.5, 2, semilla=353), fuerza_tex=0.4)
    grietas = (np.abs(np.sin(lz.x * 1.3 + lz.ruido(1.0, 2, semilla=354) * 7)) < 0.2) * raices
    lz.pintar(grietas, GIZA_V[3] if k == 0 else GIZA_V[4], 1.0)
    lz.pintar(lz.desenfocar(grietas, 0.6) * raices, GIZA_V[2], 0.6)
    if k == 1:
        # resquebrajadas: grietas claras y trozos que se sueltan
        rotas = (np.abs(np.sin(lz.x * 2.3 + lz.y * 1.7)) < 0.07) * raices
        lz.pintar(rotas, "#d6d0dc", 0.9)
        for j in range(14):
            lz.pintar(lz.circulo(24 + rng.random() * 42, 36 + rng.random() * 50, 0.8 + rng.random() * 0.6), PIEDRA_G[3])
    return lz.sprite(tramado=0.0, contorno=CONTORNO)


def nudo(k):
    """El nudo de Giza: una bola de raíces de piedra enredadas con un corazón violeta que late. 0 y 1 laten."""
    W, H = 28, 26
    lz = Lienzo(W, H, s=8, semilla=361 + k)
    lz.pintar(lz.desenfocar(lz.elipse(14, 23, 11, 2), 0.6), "#0e0c0a", 0.55)
    rng = np.random.default_rng(362)
    bola = np.zeros((lz.H, lz.W))
    for j in range(16):
        a = rng.random() * np.pi * 2
        r = 7 + rng.random() * 2
        bola = np.maximum(bola, lz.trazo(lz.curva((14 + np.cos(a) * r, 14 + np.sin(a) * r * 0.8),
                                                  (14 + (rng.random() - 0.5) * 6, 14 + (rng.random() - 0.5) * 5),
                                                  (14 + np.cos(a + 2.4) * r, 14 + np.sin(a + 2.4) * r * 0.8), n=14), 1.3, 0.8))
    lz.sombrear(bola, ["#1c1a22", "#2c2a34", "#403c4a", "#57525f", "#6e6878", "#8a8494"], 2.4, LUZ, textura=lz.ruido(0.5, 2, semilla=363), fuerza_tex=0.35)
    corazon = lz.elipse(14, 14, 4.2 + k * 0.8, 3.6 + k * 0.7)
    lz.pintar(lz.desenfocar(corazon, 1.5), GIZA_V[2], 0.8)
    lz.sombrear(corazon, GIZA_V[2:] + ["#f4e0ff"], 2.4, LUZ)
    lz.pintar(bola * (lz.ruido(0.4, 1, semilla=364) > 0.55) * corazon, "#2c2a34", 0.9)       # raíces por delante
    for (a, b) in (((4, 22), (0, 25)), ((24, 21), (28, 24)), ((10, 23), (8, 26))):
        lz.pintar(lz.trazo([a, b], 0.9), "#403c4a")
    return lz.sprite(contorno=CONTORNO)


def saco(k):
    """Un saco de grano del almacén (se aparta con el Latido)."""
    W, H = 18, 18
    lz = Lienzo(W, H, s=8, semilla=371 + k)
    lz.pintar(lz.desenfocar(lz.elipse(9, 16, 7, 1.6), 0.6), "#0e0c0a", 0.5)
    s_ = lz.poligono([(3, 16), (2.5, 10), (5, 5), (7, 4 if k else 5), (11, 4 if k else 5), (13, 5), (15.5, 10), (15, 16)])
    lz.sombrear(s_, ["#5a4630", "#8a7454", "#b8a07a", "#d8c49c", "#efe0bf"], 4, LUZ,
                textura=(np.sin(lz.x * 4) * np.sin(lz.y * 4) > 0).astype(float), fuerza_tex=0.15)
    lz.pintar(lz.trazo([(5, 6.5), (13, 6.5)], 0.8), "#47291c")
    if k == 1:
        lz.pintar(lz.elipse(9, 4.5, 2.6, 0.9), "#c9a046")
    return lz.sprite(contorno=CONTORNO)


def barca_bata(k):
    """La barca de remos de Bata (sin Bata: él se pone encima en el juego), a flote, vista un poco desde arriba:
    casco de tablas con la franja azul, los bancos, un farolito en la proa y las ondas. k: 0 y 1, el agua que se mueve."""
    W, H = 48, 26
    lz = Lienzo(W, H, s=6, semilla=381 + k)
    TR = ["#1a0f0b", "#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259"]
    lz.pintar(lz.desenfocar(lz.elipse(24, 20, 22, 3.4), 1.0), AGUA[0], 0.6)
    casco = lz.poligono([(3, 12), (8, 21), (40, 21), (46, 10), (40, 13), (8, 13)])
    lz.sombrear(casco, TR[1:], 3, LUZ, textura=(np.sin(lz.y * 1.7) * 0.5 + 0.5) * 0.5 + vetas(lz, 0.4, 11, True, 382) * 0.5, fuerza_tex=0.5)
    lz.pintar(casco * (np.abs(lz.y - 16.5) < 1.0), "#4c8d8d", 0.9)
    dentro = lz.poligono([(8, 13), (40, 13), (44, 11), (5, 11.5)])
    lz.pintar(dentro, TR[1])
    for x in (15, 29):
        lz.pintar(lz.trazo([(x, 11.5), (x + 1, 13)], 1.3), TR[5])
    lz.pintar(lz.trazo([(3, 12), (8, 13), (40, 13), (46, 10)], 0.8), TR[6])
    lz.pintar(lz.trazo([(44, 10.5), (44, 5)], 0.4), "#1a120c")
    farol = rect(lz, 42.8, 5, 45.2, 8)
    lz.pintar(farol, "#f9b947")
    lz.brillo(farol, "#fde27e", 2, 0.5)
    for y in (21.5, 23):
        fase = k * 1.5
        lz.pintar(lz.trazo([(2 + fase, y), (46 - fase, y)], 0.4), AGUA[5], 0.6)
    return lz.sprite(contorno=CONTORNO)


def main():
    os.makedirs(SALIDA, exist_ok=True)
    tira([casa_juncos(k) for k in range(2)]).save(os.path.join(SALIDA, "casa_juncos.png"))
    Image.fromarray(casa_juncos(0, bata=True)).save(os.path.join(SALIDA, "casa_bata.png"))
    tira([sello(k) for k in range(2)]).save(os.path.join(SALIDA, "sello_raices.png"))
    tira([nudo(k) for k in range(2)]).save(os.path.join(SALIDA, "nudo_giza.png"))
    tira([saco(k) for k in range(2)]).save(os.path.join(SALIDA, "saco.png"))
    tira([barca_bata(k) for k in range(2)]).save(os.path.join(SALIDA, "barca_bata.png"))
    Image.fromarray(grua()).save(os.path.join(SALIDA, "grua.png"))
    Image.fromarray(almacen()).save(os.path.join(SALIDA, "almacen.png"))
    tira([transbordador(k) for k in range(3)]).save(os.path.join(SALIDA, "transbordador.png"))
    tira([poste(k) for k in range(2)]).save(os.path.join(SALIDA, "poste.png"))
    print("Objetos del Embarcadero Junco en", SALIDA)


if __name__ == "__main__":
    main()
