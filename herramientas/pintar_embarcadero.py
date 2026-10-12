"""LOS OBJETOS DEL EMBARCADERO JUNCO, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_embarcadero.py

Genera (en arte/mundos/raiz/embarcadero/):
  casa_juncos.png     2 × 56×64   las casas de los barqueros: paredes de juncos atados sobre una plataforma de
                                  tablas subida en pilotes, tejado de juncos redondeado, una ventana redonda,
                                  una escalerilla y cosas de barquero (nasas, una red, peces secándose, un remo)
  grua.png            48×76       la grúa del muelle, rota: un poste grueso con su pluma inclinada, la polea
                                  partida, la cuerda colgando y el gancho; un fardo caído al pie
  almacen.png         88×64       el almacén: un cobertizo largo de tablas con tejado de juncos, el portón abierto
                                  y, delante, barriles, cajas y sacos
  transbordador.png   2 × 120×60  el TRANSBORDADOR: una barcaza grande y plana con barandilla, una caseta para el
                                  barquero, una campana y una pértiga larga. 0 varado (escorado, con un boquete en
                                  el casco y algas), 1 arreglado y a flote
"""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_casa_shamba import vetas, rect  # noqa: E402
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
    W, H = 56, 64
    lz = Lienzo(W, H, s=6, semilla=301 + k)
    abajo = 60
    lz.pintar(lz.desenfocar(lz.elipse(28, abajo, 25, 3), 1.0), "#0e0c0a", 0.4)
    _pilotes(lz, (9, 22, 35, 47), 40, abajo)
    # la plataforma de tablas, con el borde claro
    plat = lz.poligono([(3, 40), (53, 38), (54, 43), (4, 45)])
    lz.sombrear(plat, MADERA[2:7], 2, LUZ, textura=((lz.x % 4) < 0.6) * 1.0, fuerza_tex=-0.5)
    lz.pintar(lz.trazo([(3, 40), (53, 38)], 0.6), MADERA[7], 0.9)
    # las paredes de juncos atados (frente y lado) con una banda de cuerda
    frente = rect(lz, 9, 19, 40, 40)
    _juncos_atados(lz, frente, 302 + k)
    lado = lz.poligono([(40, 19), (48, 15), (48, 37), (40, 40)])
    _juncos_atados(lz, lado, 303 + k, JUNCO[:6])
    lz.pintar(lado, "#000000", 0.25)
    for y in (24, 33):
        lz.pintar(lz.trazo([(9, y), (40, y)], 0.5) + lz.trazo([(40, y), (48, y - 3.5)], 0.5), CUERDA, 0.9)
    # la puerta (una cortina de esteras) y la ventana redonda
    puerta = rect(lz, 15, 26, 23, 40)
    lz.pintar(puerta, "#1a120c")
    lz.pintar(rect(lz, 15, 26, 23, 29.5), JUNCO[3], 0.9)                       # la estera enrollada arriba
    ventana = lz.circulo(32, 28, 3.4)
    lz.pintar(ventana, "#140e0a")
    lz.pintar(np.clip(lz.circulo(32, 28, 4.2) - ventana, 0, 1), MADERA[5])
    if k == 0:
        lz.brillo(lz.circulo(32, 28.6, 2.4), "#f9b947", 2.2, 0.5)
    # el tejado de juncos redondeado (como una barca boca abajo), con el borde deshilachado
    hilos = np.sin(lz.x * 3.1 + lz.y * 0.9) * 0.5 + 0.5
    curva = 4 + 0.022 * (lz.x - 27) ** 2
    techo = ((lz.y > curva) & (lz.y < 21 + 0.004 * (lz.x - 27) ** 2) & (lz.x > 4) & (lz.x < 52)).astype(float)
    lz.sombrear(techo, JUNCO, 6, LUZ, textura=hilos * 0.6 + vetas(lz, 0.3, 7, False, 304 + k) * 0.4, fuerza_tex=0.5)
    for x in range(8, 50, 7):
        lz.pintar(lz.trazo([(x, 4.5 + 0.022 * (x - 27) ** 2), (x + 0.5, 20 + 0.004 * (x - 27) ** 2)], 0.45), JUNCO[1], 0.6)
    flecos = np.zeros((lz.H, lz.W))
    for j in range(26):
        x0 = 5 + j * 1.8
        y0 = 21 + 0.004 * (x0 - 27) ** 2
        flecos = np.maximum(flecos, lz.trazo([(x0, y0 - 0.5), (x0 + 0.3, y0 + 1.8 + (j % 3))], 0.5))
    lz.pintar(flecos, JUNCO[5], 0.9)
    # cosas de barquero
    if k == 0:
        # una nasa (cesta de pescar) y un remo apoyado
        nasa = lz.elipse(45, 36, 3.2, 2.4)
        lz.pintar(nasa * (((lz.x + lz.y) % 1.6) < 0.5), JUNCO[4])
        lz.pintar(np.clip(nasa - lz.elipse(45, 36, 2.4, 1.6), 0, 1), JUNCO[2])
        lz.sombrear(lz.trazo([(6, 39), (10, 20)], 0.7), MADERA[4:8], 0.6, LUZ)
        lz.sombrear(lz.elipse(10.4, 18.5, 1.3, 3.0, -15), MADERA[4:8], 1, LUZ)
    else:
        # peces secándose en una cuerda y una red colgada del lado
        lz.pintar(lz.trazo([(10, 22), (24, 22.6)], 0.4), CUERDA)
        for x in (12, 16, 20):
            lz.sombrear(lz.elipse(x, 25, 1.0, 2.3), ["#346161", "#4c8d8d", "#9fd0d0"], 1, LUZ)
        red = lz.poligono([(41, 20), (47, 17), (47, 30), (41, 33)])
        lz.pintar(((np.abs((lz.x + lz.y) % 2.6) < 0.35) | (np.abs((lz.x - lz.y) % 2.6) < 0.35)) * red, "#c9b77d", 0.85)
    # la escalerilla que baja al agua
    for j in range(4):
        lz.pintar(lz.trazo([(26, 46 + j * 3.4), (31, 46 + j * 3.4)], 0.8), MADERA[5])
    lz.pintar(lz.trazo([(26, 44), (26, 58)], 0.6) + lz.trazo([(31, 44), (31, 58)], 0.6), MADERA[3])
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
    W, H = 88, 64
    lz = Lienzo(W, H, s=6, semilla=321)
    suelo = 60
    lz.pintar(lz.desenfocar(lz.elipse(44, suelo, 42, 4), 1.0), "#0e0c0a", 0.45)
    # el cobertizo: frente de tablas verticales y el lado en sombra
    frente = rect(lz, 6, 24, 70, suelo)
    lz.sombrear(frente, MADERA[2:7], 6, LUZ, textura=vetas(lz, 0.45, 13, False, 322), fuerza_tex=0.4)
    lz.pintar(frente * ((lz.x % 4.5) < 0.55), MADERA[0], 0.8)
    lado = lz.poligono([(70, 24), (82, 18), (82, suelo - 6), (70, suelo)])
    lz.sombrear(lado, MADERA[1:5], 3, LUZ, textura=vetas(lz, 0.45, 13, False, 323), fuerza_tex=0.4)
    # el portón abierto: una hoja abierta hacia fuera, dentro oscuridad con sacos apilados
    hueco = rect(lz, 28, 32, 52, suelo)
    lz.pintar(hueco, "#0e0a08")
    for (x, y) in ((33, 55), (39, 56), (36, 50)):
        lz.sombrear(lz.elipse(x, y, 3.6, 2.6), ["#2a2014", "#3e3020", "#54422c"], 2, LUZ)
    hoja = lz.poligono([(52, 32), (60, 34), (60, suelo + 1), (52, suelo)])
    lz.sombrear(hoja, MADERA[3:8], 2, LUZ, textura=vetas(lz, 0.45, 13, False, 324), fuerza_tex=0.4)
    lz.pintar(lz.trazo([(52, 40), (60, 42)], 0.6) + lz.trazo([(52, 52), (60, 54)], 0.6), HIERRO[2])
    lz.pintar(rect(lz, 27, 31, 53, 32.4), MADERA[6])
    # un letrero con un pez pintado encima del portón
    lz.sombrear(rect(lz, 33, 26, 47, 30), MADERA[4:8], 1, LUZ)
    lz.pintar(lz.elipse(40, 28, 3.6, 1.3), "#4c8d8d")
    lz.pintar(lz.poligono([(43, 28), (45.5, 26.6), (45.5, 29.4)]), "#4c8d8d")
    # el tejado de juncos, largo
    hilos = np.sin(lz.x * 3.1 + lz.y * 0.9) * 0.5 + 0.5
    faldon = lz.poligono([(10, 6), (74, 4), (86, 18), (68, 25)])
    lz.sombrear(faldon, JUNCO[:5], 4, LUZ, textura=hilos * 0.6 + vetas(lz, 0.3, 7, False, 325) * 0.4, fuerza_tex=0.5)
    tejado = lz.poligono([(2, 26), (10, 6), (74, 4), (72, 26)])
    lz.sombrear(tejado, JUNCO, 6, LUZ, textura=hilos * 0.6 + vetas(lz, 0.3, 7, False, 326) * 0.4, fuerza_tex=0.5)
    flecos = np.zeros((lz.H, lz.W))
    for j in range(38):
        x0 = 3 + j * 1.85
        flecos = np.maximum(flecos, lz.trazo([(x0, 25.5), (x0 + 0.4, 28 + (j % 3))], 0.5))
    lz.pintar(flecos, JUNCO[5], 0.9)
    # un agujero en el tejado, con los juncos rotos
    lz.pintar(lz.elipse(54, 14, 5, 2.4), "#1a120c")
    for x in (50, 53, 56, 58):
        lz.pintar(lz.trazo([(x, 12.5), (x + 1, 15.5)], 0.4), JUNCO[3])
    # delante: barriles, cajas y un saco
    for (x, y) in ((12, 58), (18, 59)):
        barril = rect(lz, x - 3, y - 8, x + 3, y)
        lz.sombrear(barril, MADERA[2:7], 3, LUZ, textura=((lz.x % 1.5) < 0.3) * 1.0, fuerza_tex=-0.3)
        for yy in (y - 6.5, y - 1.5):
            lz.pintar(rect(lz, x - 3, yy, x + 3, yy + 0.7), HIERRO[2])
        lz.pintar(lz.elipse(x, y - 8, 3, 0.9), MADERA[1])
    caja = rect(lz, 62, 50, 72, 60)
    lz.sombrear(caja, MADERA[3:8], 2, LUZ, textura=vetas(lz, 0.4, 9, True, 327), fuerza_tex=0.4)
    lz.pintar(lz.trazo([(62, 50), (72, 60)], 0.5) + lz.trazo([(72, 50), (62, 60)], 0.5), MADERA[1])
    lz.sombrear(lz.elipse(77, 58, 4, 3), ["#4a3a22", "#6a5232", "#8a6e46", "#a88a5e"], 2, LUZ)
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


def main():
    os.makedirs(SALIDA, exist_ok=True)
    tira([casa_juncos(k) for k in range(2)]).save(os.path.join(SALIDA, "casa_juncos.png"))
    Image.fromarray(grua()).save(os.path.join(SALIDA, "grua.png"))
    Image.fromarray(almacen()).save(os.path.join(SALIDA, "almacen.png"))
    tira([transbordador(k) for k in range(2)]).save(os.path.join(SALIDA, "transbordador.png"))
    print("Objetos del Embarcadero Junco en", SALIDA)


if __name__ == "__main__":
    main()
