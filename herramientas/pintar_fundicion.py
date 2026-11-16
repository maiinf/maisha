"""LA FUNDICIÓN DE ESCORIA (Asterhaul), pintada con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_fundicion.py

Genera en arte/mundos/asterhaul/fundicion/:
  barcaza.png      48×54      UNA BARCAZA DE HIERRO (vista desde arriba): una plancha remachada con baranda de
                   cadena y cuatro argollas, que flota en la escoria (el canto de abajo, al rojo)
  cabrestante.png  2 × 28×36  UN CABRESTANTE: un tambor de cadena con su manivela en un bastidor. 0 y 1: la manivela
                   en dos posiciones (gira al usarlo)
  bloque.png       2 × 24×28  UN BLOQUE-IMÁN de hierro meteórico con una veta azul. 0 quieto · 1 imantado (la veta
                   encendida)
  placa.png        2 × 24×16  UNA PLACA DE PRESIÓN en el suelo. 0 libre · 1 con peso (hundida, el borde encendido)
  compuerta.png    2 × 24×64  UNA COMPUERTA DE CRISOL: una hoja de hierro con contrapesos entre dos guías.
                   0 cerrada · 1 abierta (subida)
  estela.png       24×38      LA ESTELA DEL PULSO: una laja de hierro azulado con dos arcos enfrentados grabados
  kovu.png         5 × 40×30  KOVU DE ESCORIA, la salamandra de hierro fundido: 0 y 1 nada (solo asoma la cresta
                   de hierro) · 2 ASOMA (la cabeza fuera, la boca al rojo: va a escupir) · 3 FUERA, en piedra
                   fría (el cuerpo entero, gris y agrietado) · 4 fuera y golpeado (blanco)
  tenaza.png       28×20      una tenaza de Nyundo al rojo, abierta, mirando a la derecha
  nyundo.png       5 × 112×116  NYUNDO, EL HERRERO DE 4 TENAZAS (jefe): un autómata de forja con cuerpo de huevo de
                   bronce, la cabeza de yelmo con una mirilla y cuatro hombros (los brazos los dibuja el juego).
                   0 en guardia · 1 con el peto abollado · 2 PETO ABIERTO (se le ve el núcleo de ámbar) ·
                   3 abierto y golpeado (blanco) · 4 vencido (apagado, la cabeza caída)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_desfiladero import LUZ, ROCA, BASALTO, AMBAR, HIERRO, MADERA, BLANCO  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "asterhaul", "fundicion")
BRONCE = ["#2a1808", "#4e3010", "#7a5020", "#a87834", "#d0a450", "#f0d088"]
ROJO = ["#5a0e04", "#a02408", "#e04a10", "#f88a20", "#ffc850", "#fff0b0"]
IMAN = ["#0e2a3a", "#1a5a78", "#2e9ac0", "#6ad0f0", "#c0f4ff"]
ESCAMA = ["#1a0c08", "#3a1a0e", "#6a2a10", "#a04414", "#d86a1c", "#f8a040"]
FRIO = ["#1c1c22", "#33343c", "#4e505a", "#6c6e7a", "#8e909c", "#b4b6c0"]


def barcaza():
    W, H = 48, 54
    lz = Lienzo(W, H, s=5, semilla=10600)
    canto = lz.poligono([(1, 53), (47, 53), (47, 46), (1, 46)])
    lz.sombrear(canto, HIERRO[:4], 2.0, LUZ)
    lz.pintar(canto * (lz.y > 50.5), ROJO[2], 0.9)
    lz.pintar(canto * (lz.y > 52), ROJO[4], 0.9)
    plancha = lz.poligono([(1, 47), (47, 47), (47, 1), (1, 1)])
    lz.sombrear(plancha, HIERRO[1:], 16.0, LUZ, textura=lz.ruido(2.0, 3, semilla=10601), fuerza_tex=0.25)
    rejilla = plancha * (((lz.x % 8) < 0.7) | ((lz.y % 8) < 0.7))
    lz.pintar(rejilla, HIERRO[0], 0.45)
    marco = plancha * ((lz.x < 3.2) | (lz.x > 44.8) | (lz.y < 3.2) | (lz.y > 44.8))
    lz.sombrear(marco, HIERRO[2:], 1.2, LUZ)
    for x in range(6, 46, 9):
        for y in (2.1, 45.9):
            lz.pintar(lz.circulo(x, y, 0.8), HIERRO[5])
    for (x, y) in ((6, 6), (42, 6), (6, 42), (42, 42)):                 # las argollas de las cadenas
        lz.sombrear((np.abs(np.hypot(lz.x - x, lz.y - y) - 2.6) < 0.9) * 1.0, BRONCE[2:], 0.8, LUZ)
    iman = lz.circulo(24, 24, 5.5)                                     # el corazón de imán, en el centro
    lz.sombrear(iman, IMAN, 3.0, LUZ)
    lz.pintar((np.abs(np.hypot(lz.x - 24, lz.y - 24) - 7.2) < 0.6) * 1.0, HIERRO[0], 0.8)
    lz.sumar_luz(lz.desenfocar(iman, 2), IMAN[3], 0.5)
    return lz.sprite(contorno=0.4)


def cabrestante(f):
    W, H = 28, 36
    lz = Lienzo(W, H, s=6, semilla=10620)
    for x in (5, 23):
        lz.sombrear(lz.poligono([(x - 2.4, 35), (x + 2.4, 35), (x + 2, 10), (x - 2, 10)]), MADERA, 1.8, LUZ, textura=((lz.y % 5) < 0.7) * 1.0, fuerza_tex=-0.3)
    lz.sombrear(lz.poligono([(2, 35), (26, 35), (25, 31), (3, 31)]), MADERA[1:], 1.6, LUZ)
    tambor = lz.poligono([(7, 26), (21, 26), (21, 14), (7, 14)])
    vueltas = ((lz.x % 2.4) < 1.1) * 1.0
    lz.sombrear(tambor, HIERRO, 5.0, (LUZ[0], LUZ[1] * 1.4, LUZ[2]), textura=vueltas, fuerza_tex=-0.45)
    for x in (7, 21):
        lz.sombrear(lz.elipse(x, 20, 1.6, 7.4), BRONCE[1:], 1.4, LUZ)
    ang = -0.9 if f == 0 else 0.9
    eje = (24.5, 20)
    codo = (eje[0] + np.cos(ang) * 1.5, eje[1] + np.sin(ang) * 7.5)
    lz.sombrear(lz.trazo([eje, codo], 1.3), HIERRO[2:], 0.7, LUZ)
    lz.sombrear(lz.circulo(codo[0], codo[1], 1.9), AMBAR[1:], 1.3, LUZ)
    lz.pintar(lz.trazo([(14, 14), (14, 3)], 0.6), HIERRO[3])            # la cadena que sube
    for y in range(4, 14, 3):
        lz.pintar(lz.circulo(14, y, 1.0), HIERRO[5], 0.8)
    return lz.sprite(contorno=0.5)


def bloque(f):
    W, H = 24, 28
    lz = Lienzo(W, H, s=6, semilla=10640 + f)
    frente = lz.poligono([(2, 27), (22, 27), (22, 12), (2, 12)])
    lz.sombrear(frente, HIERRO[:5], 5.0, LUZ, textura=lz.ruido(1.5, 3, semilla=10641), fuerza_tex=0.3)
    tapa = lz.poligono([(2, 12), (22, 12), (19, 3), (5, 3)])
    lz.sombrear(tapa, HIERRO[2:], 4.0, LUZ, textura=lz.ruido(1.5, 3, semilla=10642), fuerza_tex=0.25)
    lz.pintar(lz.trazo([(2, 12), (22, 12)], 0.4), HIERRO[5], 0.7)
    for (x, y) in ((4, 14.5), (20, 14.5), (4, 24.5), (20, 24.5)):
        lz.pintar(lz.circulo(x, y, 0.8), HIERRO[5])
    veta = frente * (np.abs(lz.y - 19.5 - np.sin(lz.x * 0.9) * 1.6) < 1.1)
    lz.sombrear(veta, IMAN[:4] if f == 0 else IMAN[1:], 1.0, LUZ)
    punto = lz.circulo(12, 7.5, 2.4)
    lz.sombrear(punto, IMAN[:4] if f == 0 else IMAN[1:], 1.6, LUZ)
    if f == 1:
        lz.sumar_luz(lz.desenfocar(veta + punto, 1.8), IMAN[3], 1.0)
    return lz.sprite(contorno=0.5)


def placa(f):
    W, H = 24, 16
    lz = Lienzo(W, H, s=6, semilla=10660 + f)
    fuera = lz.poligono([(1, 15), (23, 15), (21, 2), (3, 2)])
    lz.sombrear(fuera, BRONCE[:5], 3.0, LUZ)
    dentro = lz.poligono([(3.5, 13.4), (20.5, 13.4), (19, 3.8), (5, 3.8)])
    lz.sombrear(dentro, HIERRO[1:4] if f == 0 else HIERRO[:3], 4.0, LUZ)
    lz.pintar(np.clip(fuera - dentro, 0, 1) * (lz.y < 4.4), BRONCE[5], 0.6)
    marca = (np.abs(np.hypot(lz.x - 12, (lz.y - 8.6) * 1.6) - 4.2) < 0.7) * dentro
    lz.pintar(marca, IMAN[1] if f == 0 else IMAN[3])
    if f == 1:
        lz.sumar_luz(lz.desenfocar(marca, 1.4), IMAN[3], 0.9)
        lz.sumar_luz(lz.desenfocar(np.clip(fuera - dentro, 0, 1), 1.0), AMBAR[3], 0.6)
    return lz.sprite(contorno=0.4)


def compuerta(f):
    W, H = 24, 64
    lz = Lienzo(W, H, s=5, semilla=10680 + f)
    for x in (3, 21):                                                  # las dos guías
        lz.sombrear(lz.poligono([(x - 2.4, 63), (x + 2.4, 63), (x + 2.4, 2), (x - 2.4, 2)]), HIERRO[:5], 1.8, LUZ)
        for y in range(8, 62, 9):
            lz.pintar(lz.circulo(x, y, 0.8), HIERRO[5])
    lz.sombrear(lz.poligono([(0, 6), (24, 6), (24, 1), (0, 1)]), BRONCE[1:], 2.0, LUZ)
    y0, y1 = (12, 63) if f == 0 else (3, 20)                            # la hoja (abierta: subida)
    hoja = lz.poligono([(5.6, y1), (18.4, y1), (18.4, y0), (5.6, y0)])
    lz.sombrear(hoja, HIERRO[1:], 5.0, LUZ, textura=lz.ruido(1.6, 3, semilla=10681), fuerza_tex=0.25)
    lz.pintar(hoja * ((lz.y % 10) < 0.8), HIERRO[0], 0.7)
    if f == 0:
        ojo = lz.circulo(12, 36, 3.2)
        lz.sombrear(ojo, IMAN[:4], 1.8, LUZ)
        lz.pintar((np.abs(np.hypot(lz.x - 12, lz.y - 36) - 4.6) < 0.6) * hoja, BRONCE[4])
        lz.pintar(hoja * (lz.y > 60.5), ROJO[2], 0.8)
    return lz.sprite(contorno=0.4)


def estela():
    W, H = 24, 38
    lz = Lienzo(W, H, s=6, semilla=10700)
    cx = 12
    lz.sombrear(lz.elipse(cx, 36, 9, 2), ROCA[:4], 1.0, LUZ)
    laja = lz.poligono([(cx - 7, 36), (cx + 7, 36), (cx + 6.4, 10), (cx + 2, 2), (cx - 3.5, 4), (cx - 6.6, 14)])
    lz.sombrear(laja, ["#0e141c", "#1c2a3a", "#2e4258", "#465e7a", "#64809c", "#8aa6c0"], 4.5, LUZ, textura=lz.ruido(1.6, 3, semilla=10701), fuerza_tex=0.25)
    glifo = np.zeros_like(laja)
    for (ox, lado) in ((cx - 2.6, 1), (cx + 2.6, -1)):                 # dos arcos enfrentados: lo que viene y lo que se va
        d = np.hypot(lz.x - ox, lz.y - 20)
        glifo = np.clip(glifo + (np.abs(d - 5.0) < 0.6) * ((lz.x - ox) * lado < -0.5), 0, 1)
    glifo = np.clip(glifo + lz.circulo(cx, 20, 1.3), 0, 1)
    lz.pintar(glifo * laja, IMAN[3])
    lz.sumar_luz(lz.desenfocar(glifo * laja, 1.4), IMAN[3], 0.8)
    return lz.sprite(contorno=0.5)


def kovu(f):
    W, H = 40, 30
    lz = Lienzo(W, H, s=5, semilla=10720 + f)
    cx = 20
    blanco = f == 4
    if f in (0, 1):
        # nadando: solo asoma la cresta de hierro, con una estela de escoria
        onda = lz.elipse(cx, 24, 15, 3.4)
        lz.pintar(onda, ROJO[4], 0.55)
        lz.pintar(lz.elipse(cx, 24, 11, 2.2), ROJO[5], 0.6)
        for i, (x, alto) in enumerate(((10, 6), (15, 10), (20, 13), (25, 10), (30, 6))):
            alto += (1.5 if (i + f) % 2 else 0)
            pua = lz.poligono([(x - 2.6, 24), (x + 2.6, 24), (x + 0.6 * (1 if f else -1), 24 - alto)])
            lz.sombrear(pua, HIERRO, 1.4, LUZ)
            lz.pintar(pua * (lz.y > 22), ROJO[3], 0.8)
        return lz.sprite(contorno=0.5)
    if f == 2:
        # asoma: la cabeza ancha fuera, los ojos de brasa y la boca abierta al rojo
        lz.pintar(lz.elipse(cx, 26, 16, 3.4), ROJO[4], 0.55)
        cuello = lz.poligono([(cx - 8, 27), (cx + 8, 27), (cx + 7, 16), (cx - 7, 16)])
        lz.sombrear(cuello, ESCAMA, 4.0, LUZ, textura=((lz.y % 3) < 0.7) * 1.0, fuerza_tex=-0.3)
        cabeza = lz.elipse(cx, 13, 11.5, 8)
        lz.sombrear(cabeza, ESCAMA, 5.0, LUZ, textura=lz.ruido(1.6, 2, semilla=10721), fuerza_tex=0.25)
        for x in (cx - 6, cx, cx + 6):
            lz.sombrear(lz.poligono([(x - 2, 7), (x + 2, 7), (x, 1)]), HIERRO, 1.2, LUZ)
        boca = lz.elipse(cx, 17, 6, 3.4)
        lz.pintar(boca, ROJO[1])
        lz.pintar(lz.elipse(cx, 17.4, 4, 2), ROJO[4])
        lz.sumar_luz(lz.desenfocar(boca, 2), ROJO[3], 0.9)
        for lado in (-1, 1):
            lz.pintar(lz.circulo(cx + lado * 6, 11, 1.9), "#140e18")
            lz.pintar(lz.circulo(cx + lado * 6, 11, 1.1), ROJO[4])
        return lz.sprite(contorno=0.5)
    # fuera, en piedra fría: el cuerpo entero, gris, agrietado (de lado, mirando a la derecha)
    piel = (BLANCO + BLANCO[-2:]) if blanco else FRIO
    cola = lz.trazo([(8, 22), (3, 18), (5, 12)], 3.0, 1.0)
    lz.sombrear(cola, piel[:5], 1.4, LUZ)
    for x in (12, 26):
        lz.sombrear(lz.trazo([(x, 22), (x - 2, 27), (x + 2, 28)], 2.0, 1.4), piel[:5], 1.0, LUZ)
    cuerpo = lz.elipse(19, 19, 12, 6)
    lz.sombrear(cuerpo, piel, 4.5, LUZ, textura=lz.ruido(1.6, 2, semilla=10722), fuerza_tex=0.25)
    cabeza = lz.elipse(31, 17, 6.5, 5)
    lz.sombrear(cabeza, piel[1:], 3.0, LUZ)
    for x in (11, 16, 21, 26):
        lz.sombrear(lz.poligono([(x - 2, 14), (x + 2, 14), (x + 0.6, 8)]), HIERRO if not blanco else BLANCO, 1.2, LUZ)
    if not blanco:
        grieta = (cuerpo + cabeza) * (np.abs(lz.ruido(5, 3, semilla=10723) - 0.5) < 0.03)
        lz.pintar(grieta, ROJO[2])
        lz.sumar_luz(lz.desenfocar(grieta, 1.0), ROJO[3], 0.4)
    lz.pintar(lz.circulo(33, 15.6, 1.6), "#ffffff")
    lz.pintar(lz.trazo([(32.2, 15), (33.8, 16.2)], 0.3) + lz.trazo([(33.8, 15), (32.2, 16.2)], 0.3), "#140e18")
    return lz.sprite(contorno=0.5)


def tenaza():
    W, H = 28, 20
    lz = Lienzo(W, H, s=6, semilla=10760)
    muñeca = lz.circulo(5, 10, 4)
    lz.sombrear(muñeca, BRONCE[1:], 2.6, LUZ)
    for lado in (-1, 1):
        garra = lz.trazo([(6, 10 + lado * 2), (14, 10 + lado * 7), (22, 10 + lado * 6.4), (26, 10 + lado * 2.4)], 3.4, 1.6)
        lz.sombrear(garra, ROJO, 1.6, LUZ)
    lz.sumar_luz(lz.desenfocar(lz.elipse(18, 10, 9, 8), 3), ROJO[3], 0.45)
    lz.pintar(lz.circulo(5, 10, 1.2), BRONCE[0])
    return lz.sprite(contorno=0.5)


def nyundo(f):
    W, H = 112, 116
    lz = Lienzo(W, H, s=4, semilla=10780 + min(f, 2))
    cx = 56
    blanco = f == 3
    apagado = f == 4
    bronce = (BLANCO + BLANCO[-2:]) if blanco else (["#16120e", "#2a221a", "#40342a", "#5a4a3a", "#74624c", "#8e7a60"] if apagado else BRONCE)
    hierro = (BLANCO + BLANCO[-2:]) if blanco else HIERRO
    # el pie: un zócalo de hierro atornillado al suelo, y la falda de remaches
    zoc = lz.poligono([(cx - 30, 115), (cx + 30, 115), (cx + 26, 104), (cx - 26, 104)])
    lz.sombrear(zoc, hierro[:5], 3.0, LUZ)
    for x in range(cx - 24, cx + 25, 8):
        lz.pintar(lz.circulo(x, 110, 1.0), hierro[5])
    falda = lz.poligono([(cx - 22, 105), (cx + 22, 105), (cx + 18, 92), (cx - 18, 92)])
    lz.sombrear(falda, hierro[1:], 4.0, LUZ, textura=((lz.x % 6) < 0.8) * 1.0, fuerza_tex=-0.3)
    # el cuerpo: un huevo de bronce
    cuerpo = lz.elipse(cx, 66, 30, 34)
    lz.sombrear(cuerpo, bronce, 18.0, LUZ, textura=lz.ruido(2.4, 3, semilla=10781), fuerza_tex=0.18)
    for y in (46, 86):                                                 # los aros que lo ciñen
        aro = cuerpo * (np.abs(lz.y - y - ((lz.x - cx) / 30.0) ** 2 * 4) < 1.6)
        lz.sombrear(aro, hierro[1:], 1.2, LUZ)
    # los cuatro hombros (de ellos salen los brazos, que dibuja el juego)
    for (dx, dy) in ((-30, 48), (30, 48), (-33, 74), (33, 74)):
        hombro = lz.circulo(cx + dx, dy, 7.5)
        lz.sombrear(hombro, hierro[1:], 4.5, LUZ)
        lz.pintar(lz.circulo(cx + dx, dy, 2.6), hierro[0])
    # el peto: liso, abollado o abierto con el núcleo a la vista
    peto = lz.elipse(cx, 68, 15, 17)
    if f in (2, 3):
        lz.pintar(peto, "#1c0a04" if not blanco else "#ffffff")
        if not blanco:
            nucleo = lz.poligono([(cx, 55), (cx + 9, 68), (cx, 82), (cx - 9, 68)])
            lz.sombrear(nucleo, AMBAR[1:], 5.0, LUZ)
            lz.pintar(lz.circulo(cx - 2.4, 63, 1.8), "#ffffff", 0.9)
            lz.sumar_luz(lz.desenfocar(nucleo, 5), AMBAR[3], 1.0)
        for lado in (-1, 1):                                           # las dos hojas del peto, abiertas a los lados
            hoja = lz.poligono([(cx + lado * 15, 52), (cx + lado * 25, 48), (cx + lado * 27, 86), (cx + lado * 15, 84)])
            lz.sombrear(hoja, bronce[2:], 3.0, LUZ)
    else:
        lz.sombrear(peto, bronce[2:], 9.0, LUZ)
        lz.pintar((np.abs(np.hypot((lz.x - cx) / 15.0, (lz.y - 68) / 17.0) - 1.0) < 0.07) * 1.0, bronce[0], 0.8)
        lz.pintar(lz.trazo([(cx, 51), (cx, 85)], 0.5), bronce[0], 0.8)
        martillo = lz.poligono([(cx - 5, 62), (cx + 5, 62), (cx + 5, 67), (cx + 1.2, 67), (cx + 1.2, 78), (cx - 1.2, 78), (cx - 1.2, 67), (cx - 5, 67)])
        lz.pintar(martillo, bronce[1], 0.9)                             # el martillo grabado en el peto
        if f == 1:
            abolla = lz.elipse(cx + 5, 72, 8, 7)
            lz.sombrear(abolla, bronce[:4], 5.0, (0.6, 0.7, 0.5))
            lz.pintar(lz.trazo([(cx - 2, 64), (cx + 8, 70), (cx + 4, 80)], 0.5), bronce[0])
            lz.pintar(lz.trazo([(cx + 8, 70), (cx + 13, 68)], 0.4), AMBAR[3], 0.9)
    # la cabeza: un yelmo con la mirilla (apagada si está vencido), una chimenea corta y un respiradero
    caida = 6 if apagado else 0
    yelmo = lz.poligono([(cx - 13, 36 + caida), (cx + 13, 36 + caida), (cx + 11, 17 + caida), (cx, 11 + caida), (cx - 11, 17 + caida)])
    lz.sombrear(yelmo, hierro[1:], 8.0, LUZ, textura=lz.ruido(1.8, 2, semilla=10782), fuerza_tex=0.2)
    mirilla = lz.poligono([(cx - 9, 27 + caida), (cx + 9, 27 + caida), (cx + 8, 22.5 + caida), (cx - 8, 22.5 + caida)])
    lz.pintar(mirilla, "#0e0806")
    if not apagado and not blanco:
        lz.pintar(lz.elipse(cx - 4, 24.8, 2.6, 1.6) + lz.elipse(cx + 4, 24.8, 2.6, 1.6), ROJO[4] if f != 2 else IMAN[3])
        lz.sumar_luz(lz.desenfocar(mirilla, 2), ROJO[3] if f != 2 else IMAN[3], 0.8)
    lz.sombrear(lz.poligono([(cx - 15, 38 + caida), (cx + 15, 38 + caida), (cx + 14, 34 + caida), (cx - 14, 34 + caida)]), bronce[2:], 1.4, LUZ)
    chim = lz.poligono([(cx + 5, 14 + caida), (cx + 11, 16 + caida), (cx + 12, 4 + caida), (cx + 6, 3 + caida)])
    lz.sombrear(chim, hierro[:5], 2.0, LUZ)
    if not apagado and not blanco:
        lz.pintar(lz.elipse(cx + 9, 3.4, 3, 1.2), ROJO[3])
    return lz.sprite(contorno=0.4)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    tira("cabrestante", cabrestante, 2)
    tira("bloque", bloque, 2)
    tira("placa", placa, 2)
    tira("compuerta", compuerta, 2)
    tira("kovu", kovu, 5)
    tira("nyundo", nyundo, 5)
    for nombre, fn in (("barcaza", barcaza), ("estela", estela), ("tenaza", tenaza)):
        Image.fromarray(fn(), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))
    print("Fundición pintada en", SALIDA)
