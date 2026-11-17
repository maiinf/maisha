"""LA AGUJA CAÍDA (Asterhaul), pintada con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_aguja.py

Genera en arte/mundos/asterhaul/aguja/:
  monolito.png  3 × 24×56   UN MONOLITO-DIAPASÓN: una piedra de estrella alta, hendida arriba en dos brazos, con un
                corazón de ámbar en la horquilla. 0 dormido · 1 CANTANDO (el ámbar encendido, los brazos vibran)
                · 2 enmudecido (apagado y agrietado: tiene una pluma-cuchilla zumbando cerca)
  penasco.png   40×52       UN PEÑASCO FLOTANTE: una roca de cima plana (32×32) que se afila por debajo, con
                cristales turquesa colgando
  popo.png      5 × 36×30   POPO DE OBSIDIANA, el murciélago resonante: 0 y 1 vuela (alas arriba y abajo) ·
                2 CHILLA (la boca abierta, las orejas tiesas) · 3 ATURDIDO en el suelo (las alas caídas, ojos en
                espiral) · 4 aturdido y golpeado (blanco)
  pluma.png     14×28       UNA PLUMA-CUCHILLA de Kipanga clavada en el suelo: obsidiana con el filo turquesa
  estela.png    24×38       LA ESTELA DE LA RESONANCIA: una laja clara con anillos grabados que salen de un punto
  kipanga.png   6 × 144×100 KIPANGA ASTRAL, EL HALCÓN DE OBSIDIANA Y CRISTAL (jefe): una rapaz titánica de lajas
                de obsidiana, con el corazón de cristal en el pecho y garras de hierro meteórico. 0 y 1 PLANEA
                (alas tendidas; en el 1, alzadas) · 2 LANZA PLUMAS (las alas hacia delante, los filos encendidos)
                · 3 EN PICADO (las alas plegadas atrás, las garras por delante) · 4 ATURDIDO (en el suelo, las
                alas caídas, el corazón al aire) · 5 aturdido y golpeado (blanco)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_desfiladero import LUZ, ROCA, AMBAR, HIERRO, BLANCO  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "asterhaul", "aguja")
ESTRELLA = ["#1a2034", "#2c3650", "#465472", "#667898", "#8c9cba", "#b8c6dc"]
OBSIDIANA = ["#05050c", "#0c0e1c", "#161a30", "#242c4a", "#384468", "#566690"]
CRISTAL = ["#0e2a3a", "#1a5a78", "#2e9ac0", "#6ad0f0", "#c0f4ff", "#ffffff"]
MUDO = ["#16161c", "#26262e", "#3a3a44", "#50505c", "#686874", "#84848e"]


def monolito(f):
    W, H = 24, 56
    lz = Lienzo(W, H, s=6, semilla=10900 + f)
    cx = 12
    piedra = MUDO if f == 2 else ESTRELLA
    pie = lz.poligono([(cx - 9, 55), (cx + 9, 55), (cx + 7.5, 49), (cx - 7.5, 49)])
    lz.sombrear(pie, piedra[:5], 2.2, LUZ)
    fuste = lz.poligono([(cx - 6.5, 49), (cx + 6.5, 49), (cx + 5.4, 22), (cx - 5.4, 22)])
    lz.sombrear(fuste, piedra[1:], 4.5, LUZ, textura=lz.ruido(1.6, 3, semilla=10901), fuerza_tex=0.25)
    for y in (30, 39):                                                 # dos aros grabados
        lz.pintar(lz.trazo([(cx - 6, y), (cx + 6, y)], 0.45) * fuste, piedra[0] if f != 1 else AMBAR[3], 0.9)
    brazos = np.zeros_like(fuste)
    for lado in (-1, 1):                                               # la horquilla: dos brazos de piedra
        brazos = np.clip(brazos + lz.poligono([(cx + lado * 1.6, 23), (cx + lado * 5.6, 23), (cx + lado * 5.0, 2.5), (cx + lado * 2.6, 2.5)]), 0, 1)
    lz.sombrear(brazos, piedra[1:], 1.8, LUZ, textura=lz.ruido(1.4, 2, semilla=10902), fuerza_tex=0.2)
    corazon = lz.poligono([(cx, 15), (cx + 2.2, 19.5), (cx, 24), (cx - 2.2, 19.5)])
    lz.sombrear(corazon, (MUDO[1:5] if f == 2 else (AMBAR[:4] if f == 0 else AMBAR[2:])), 1.4, LUZ)
    if f == 1:
        lz.sumar_luz(lz.desenfocar(corazon, 2.2), AMBAR[3], 1.2)
        lz.sumar_luz(lz.desenfocar(brazos, 1.4), CRISTAL[3], 0.5)
        for lado in (-1, 1):                                           # los brazos, dobles (vibran)
            lz.pintar(lz.trazo([(cx + lado * 7.4, 21), (cx + lado * 7.0, 4)], 0.5, 0.3), CRISTAL[4], 0.8)
        for y in (6, 10, 14):
            lz.pintar(lz.trazo([(cx - 2.0, y), (cx, y - 1.0), (cx + 2.0, y)], 0.4), "#ffffff", 0.85)
    if f == 2:
        lz.pintar(fuste * (np.abs(lz.ruido(5, 3, semilla=10903) - 0.5) < 0.02), MUDO[0], 0.9)
    return lz.sprite(contorno=0.5)


def penasco():
    W, H = 40, 52
    lz = Lienzo(W, H, s=5, semilla=10920)
    cx = 20
    # por debajo: la roca se afila, con cristales que cuelgan
    bajo = lz.poligono([(4, 34), (36, 34), (30, 44), (22, 51), (16, 47), (9, 42)])
    lz.sombrear(bajo, ESTRELLA[:4], 7.0, LUZ, textura=lz.ruido(1.8, 3, semilla=10921), fuerza_tex=0.3)
    for (x, largo) in ((11, 6), (19, 9), (27, 7)):
        cr = lz.poligono([(x - 1.8, 40), (x + 1.8, 40), (x, 40 + largo)])
        lz.sombrear(cr, CRISTAL[1:], 1.0, LUZ)
    # la cima plana, de 32×32 (lo que se pisa)
    cima = lz.poligono([(4, 34), (36, 34), (36, 2), (4, 2)])
    u = lz.x + lz.ruido(9, 2, semilla=10922) * 8
    w = lz.y + lz.ruido(9, 2, semilla=10923) * 8
    junta = ((u % 13) < 0.8) | ((w % 9) < 0.8)
    lz.sombrear(cima, ESTRELLA[1:], 14.0, LUZ, textura=lz.ruido(2.0, 3, semilla=10924), fuerza_tex=0.25)
    lz.pintar(cima * junta, ESTRELLA[0], 0.55)
    borde = cima * ((lz.x < 5.4) | (lz.x > 34.6) | (lz.y < 3.4) | (lz.y > 32.6))
    lz.pintar(borde, CRISTAL[4], 0.5)
    veta = cima * (np.abs(lz.ruido(7, 3, semilla=10925) - 0.5) < 0.016)
    lz.pintar(veta, CRISTAL[2])
    lz.sumar_luz(lz.desenfocar(veta, 1.4), CRISTAL[3], 0.5)
    lz.pintar(lz.trazo([(4, 34.4), (36, 34.4)], 0.6), ESTRELLA[0], 0.8)
    return lz.sprite(contorno=0.4)


def popo(f):
    W, H = 36, 30
    lz = Lienzo(W, H, s=6, semilla=10940 + min(f, 3))
    cx = 18
    blanco = f == 4
    piel = (BLANCO + BLANCO[-2:]) if blanco else OBSIDIANA
    suelo_ = f >= 3
    cy = 20 if suelo_ else 14
    # las alas: membranas de lajas, arriba (0), abajo (1), tiesas (2) o caídas en el suelo (3)
    for lado in (-1, 1):
        if suelo_:
            pts = [(cx + lado * 4, cy - 2), (cx + lado * 16, cy + 1), (cx + lado * 17, cy + 7), (cx + lado * 9, cy + 6), (cx + lado * 4, cy + 4)]
        else:
            sube = {0: -9, 1: 5, 2: -4}[f]
            pts = [(cx + lado * 4, cy - 2), (cx + lado * 11, cy + sube * 0.6 - 3), (cx + lado * 17, cy + sube), (cx + lado * 14, cy + sube * 0.4 + 5),
                   (cx + lado * 10, cy + sube * 0.3 + 2), (cx + lado * 7, cy + 6), (cx + lado * 4, cy + 3)]
        ala = lz.poligono(pts)
        lz.sombrear(ala, piel[:5], 3.0, LUZ)
        lz.pintar(lz.trazo([pts[0], pts[2]], 0.4) * ala, piel[5], 0.6)
        lz.pintar(lz.trazo([pts[0], pts[min(3, len(pts) - 1)]], 0.35) * ala, CRISTAL[2] if not blanco else "#ffffff", 0.6)
    cuerpo = lz.elipse(cx, cy + 1, 5.6, 6.4)
    lz.sombrear(cuerpo, piel[1:], 3.6, LUZ, textura=lz.ruido(1.3, 2, semilla=10941), fuerza_tex=0.2)
    for lado in (-1, 1):                                               # las orejas, de lasca
        alto = 8 if f == 2 else 6
        lz.sombrear(lz.poligono([(cx + lado * 1.6, cy - 4), (cx + lado * 5.2, cy - 4), (cx + lado * 5.0, cy - 4 - alto)]), piel[1:], 1.2, LUZ)
    if suelo_:
        for lado in (-1, 1):
            ox = cx + lado * 2.4
            lz.pintar(lz.circulo(ox, cy, 1.5), "#ffffff")
            lz.pintar(lz.trazo([(ox - 0.8, cy - 0.6), (ox + 0.8, cy + 0.6)], 0.3) + lz.trazo([(ox + 0.8, cy - 0.6), (ox - 0.8, cy + 0.6)], 0.3), "#140e18")
    else:
        for lado in (-1, 1):
            lz.pintar(lz.circulo(cx + lado * 2.4, cy - 0.6, 1.3), CRISTAL[3] if f != 2 else "#ffffff")
        if f == 2:                                                     # chilla: la boca abierta y dos ondas
            lz.pintar(lz.elipse(cx, cy + 3.4, 2.4, 2.0), "#2a0a14")
            lz.pintar(lz.elipse(cx, cy + 3.8, 1.4, 1.0), "#d0456a")
            for r in (9.5, 12.5):
                d = np.hypot(lz.x - cx, (lz.y - cy - 3) * 1.2)
                lz.pintar((np.abs(d - r) < 0.45) * (lz.y > cy + 5), CRISTAL[4], 0.8)
        else:
            lz.pintar(lz.trazo([(cx - 1.2, cy + 3.2), (cx, cy + 4.0), (cx + 1.2, cy + 3.2)], 0.35), piel[0])
    return lz.sprite(contorno=0.5)


def pluma():
    W, H = 14, 28
    lz = Lienzo(W, H, s=6, semilla=10960)
    cx = 7
    hoja = lz.poligono([(cx, 1), (cx + 4.4, 9), (cx + 3.2, 20), (cx, 26), (cx - 3.2, 20), (cx - 4.4, 9)])
    lz.sombrear(hoja, OBSIDIANA[1:], 2.6, LUZ)
    lz.pintar(lz.trazo([(cx, 2), (cx, 25)], 0.4) * hoja, OBSIDIANA[0])
    filo = hoja * (lz.x > cx + 1.6)
    lz.pintar(filo, CRISTAL[3], 0.85)
    lz.pintar(hoja * (np.abs(((lz.y - lz.x) % 4.0) - 2.0) < 0.3) * (lz.x < cx), OBSIDIANA[5], 0.5)
    lz.sumar_luz(lz.desenfocar(filo, 1.2), CRISTAL[3], 0.7)
    lz.pintar(lz.elipse(cx, 26.4, 4.5, 1.4), "#0a0a14", 0.6)          # la sombra donde se clava
    return lz.sprite(contorno=0.5)


def estela():
    W, H = 24, 38
    lz = Lienzo(W, H, s=6, semilla=10980)
    cx = 12
    lz.sombrear(lz.elipse(cx, 36, 9, 2), ESTRELLA[:4], 1.0, LUZ)
    laja = lz.poligono([(cx - 7, 36), (cx + 7, 36), (cx + 6.4, 9), (cx + 1, 2), (cx - 4.6, 5), (cx - 6.6, 15)])
    lz.sombrear(laja, ESTRELLA[1:], 4.5, LUZ, textura=lz.ruido(1.6, 3, semilla=10981), fuerza_tex=0.25)
    d = np.hypot(lz.x - cx, lz.y - 24)
    anillos = ((np.abs(d - 3.0) < 0.5) | (np.abs(d - 6.0) < 0.5) | (np.abs(d - 9.0) < 0.5)) * (lz.y < 25)
    glifo = np.clip(anillos + lz.circulo(cx, 24, 1.3), 0, 1) * laja
    lz.pintar(glifo, AMBAR[3])
    lz.sumar_luz(lz.desenfocar(glifo, 1.4), AMBAR[3], 0.7)
    return lz.sprite(contorno=0.5)


def _ala(lz, cx, hombro_y, lado, punta, piel, filo, encendida, plumas=9):
    """Un ala de lajas: una superficie maciza del hombro a la punta, con el borde de atrás en sierra (las
    plumas-cuchilla, más largas hacia el medio) y una hilera de cobertoras encima."""
    hx = cx + lado * 13
    px, py = cx + lado * punta[0], hombro_y + punta[1]
    largo = np.hypot(px - hx, py - hombro_y)
    dx, dy = (px - hx) / largo, (py - hombro_y) / largo
    nx, ny = -dy * lado, dx * lado                                     # hacia abajo (el lado de las plumas)
    if ny < 0:
        nx, ny = -nx, -ny
    # las plumas-cuchilla: anchas, solapadas
    bases, puntas = [], []
    for k in range(plumas):
        t = 0.1 + 0.9 * k / (plumas - 1)
        bx, by = hx + dx * largo * t, hombro_y + dy * largo * t
        lp = (15 + 19 * np.sin(t * np.pi * 0.8)) * (1.0 if k < plumas - 1 else 1.1)
        bases.append((bx, by))
        puntas.append((bx + nx * lp + dx * 7 * t, by + ny * lp + dy * 7 * t))
    # la superficie del ala, por detrás de las plumas (para que no queden huecos)
    fondo = lz.poligono([(hx, hombro_y - 5), (px, py)] + [((b[0] + q[0]) / 2, (b[1] + q[1]) / 2) for b, q in zip(bases[::-1], puntas[::-1])] + [(hx, hombro_y + 14)])
    lz.sombrear(fondo, piel[:4], 6.0, LUZ)
    masa = fondo.copy()
    for k in range(plumas):
        (bx, by), (ex, ey) = bases[k], puntas[k]
        ancho = 6.6 - 1.6 * k / (plumas - 1)
        pl = lz.poligono([(bx - dx * ancho, by - dy * ancho), (bx + dx * ancho, by + dy * ancho), (ex, ey)])
        lz.sombrear(pl, piel[1:] if k % 2 else piel[2:], 3.0, LUZ)
        lz.pintar(lz.trazo([(bx + dx * ancho * 0.85, by + dy * ancho * 0.85), (ex, ey)], 0.55) * pl, filo, 0.9)
        masa = np.clip(masa + pl, 0, 1)
    # las cobertoras: una hilera de lajas cortas sobre el arranque de las plumas
    for k in range(plumas - 1):
        t = 0.14 + 0.8 * k / (plumas - 2)
        bx, by = hx + dx * largo * t, hombro_y + dy * largo * t
        cob = lz.poligono([(bx - dx * 5, by - dy * 5), (bx + dx * 5, by + dy * 5), (bx + nx * 9 + dx * 2, by + ny * 9 + dy * 2)])
        lz.sombrear(cob, piel[2:], 2.0, LUZ)
    brazo = lz.trazo([(hx, hombro_y), (px, py)], 7.5, 3.0)
    lz.sombrear(brazo, piel[2:], 3.0, LUZ, textura=lz.ruido(1.6, 2, semilla=11000), fuerza_tex=0.2)
    lz.pintar(lz.trazo([(hx, hombro_y - 2.6), (px, py - 1.2)], 0.5) * brazo, piel[5], 0.6)
    if encendida:
        lz.sumar_luz(lz.desenfocar(masa, 2.5), CRISTAL[3], 0.7)
    return np.clip(masa + brazo, 0, 1)


def kipanga(f):
    W, H = 144, 100
    lz = Lienzo(W, H, s=4, semilla=11000 + min(f, 4))
    cx = 72
    blanco = f == 5
    aturdido = f >= 4
    piel = (BLANCO + BLANCO[-2:]) if blanco else OBSIDIANA
    filo = "#ffffff" if blanco else CRISTAL[3]
    hierro = (BLANCO + BLANCO[-2:]) if blanco else HIERRO
    cy = {0: 48, 1: 46, 2: 48, 3: 44}.get(f, 62)                       # el centro del cuerpo (aturdido: en el suelo)
    hombro = cy - 12
    # la cola: un abanico de lajas, detrás
    for k in range(5):
        a = np.radians(90 + (k - 2) * (13 if f != 3 else 6))
        lc = 24 if f != 3 else 30
        tx, ty = cx + np.cos(a) * lc, cy + 14 + np.sin(a) * lc
        pl = lz.poligono([(cx - 3 + (k - 2) * 2.4, cy + 12), (cx + 3 + (k - 2) * 2.4, cy + 12), (tx, ty)])
        lz.sombrear(pl, piel[:5] if k % 2 else piel[1:], 2.4, LUZ)
        lz.pintar(lz.trazo([(cx + (k - 2) * 2.4, cy + 13), (tx, ty)], 0.4) * pl, filo, 0.7)
    # las alas
    punta = {0: (62, 2), 1: (58, -20), 2: (46, 16), 3: (30, -30), 4: (56, 26), 5: (56, 26)}[f]
    for lado in (-1, 1):
        _ala(lz, cx, hombro, lado, punta, piel, filo, f == 2, plumas=9 if f != 3 else 6)
    # las garras de hierro meteórico (en picado, por delante)
    for lado in (-1, 1):
        gx, gy = cx + lado * 8, cy + (24 if f != 3 else 30)
        lz.sombrear(lz.trazo([(cx + lado * 6, cy + 14), (gx, gy)], 3.0, 2.0), piel[1:], 1.4, LUZ)
        for k in (-1, 0, 1):
            lz.sombrear(lz.trazo([(gx, gy), (gx + k * 3.2 + lado, gy + (6 if f != 3 else 9))], 1.5, 0.6), hierro[1:], 0.8, LUZ)
    # el cuerpo: un torso de lajas
    cuerpo = lz.elipse(cx, cy, 15, 21)
    lz.sombrear(cuerpo, piel, 10.0, LUZ, textura=lz.ruido(2.2, 3, semilla=11001), fuerza_tex=0.22)
    for y in (cy - 8, cy + 2, cy + 11):
        lz.pintar(lz.trazo([(cx - 13, y), (cx, y + 4), (cx + 13, y)], 0.55) * cuerpo, piel[0], 0.7)
    # el corazón de cristal resonante, en el pecho
    corazon = lz.elipse(cx, cy + 1, 7.5, 10.5)
    if blanco:
        lz.pintar(corazon, "#ffffff")
    else:
        lz.sombrear(corazon, CRISTAL[1:] if not aturdido else CRISTAL[2:], 5.0, LUZ)
        lz.pintar(lz.elipse(cx - 2.2, cy - 3.4, 1.8, 2.8), "#ffffff", 0.8)
        lz.pintar((np.abs(np.hypot((lz.x - cx) / 7.5, (lz.y - cy - 1) / 10.5) - 1.0) < 0.1) * 1.0, piel[0], 0.8)
        lz.sumar_luz(lz.desenfocar(corazon, 3 if not aturdido else 6), CRISTAL[3], 0.6 if not aturdido else 1.2)
        if aturdido:
            lz.pintar(corazon * (np.abs(lz.ruido(4, 3, semilla=11002) - 0.5) < 0.03), "#ffffff", 0.9)       # resquebrajado
    # la cabeza: capucha de lajas, pico de hierro y ojos de cristal
    hy = cy - (24 if not aturdido else 16)
    hx = cx + (0 if not aturdido else 5)
    cabeza = lz.elipse(hx, hy, 11, 10)
    lz.sombrear(cabeza, piel[1:], 6.0, LUZ, textura=lz.ruido(1.8, 2, semilla=11003), fuerza_tex=0.2)
    lz.sombrear(lz.poligono([(hx - 9, hy - 3), (hx, hy - 12), (hx + 9, hy - 3), (hx, hy - 5)]), piel[2:], 2.0, LUZ)        # la cresta
    pico = lz.poligono([(hx - 4.2, hy + 1.5), (hx + 4.2, hy + 1.5), (hx + 2.4, hy + 7), (hx - 0.6, hy + (12 if f != 3 else 14)), (hx - 2.6, hy + 7)])
    lz.sombrear(pico, hierro[1:], 2.0, LUZ)
    for lado in (-1, 1):
        ox, oy = hx + lado * 4.6, hy - 0.6
        if aturdido:
            lz.pintar(lz.circulo(ox, oy, 2.2), "#ffffff")
            lz.pintar(lz.trazo([(ox - 1.2, oy - 1.0), (ox + 1.2, oy + 1.0)], 0.4) + lz.trazo([(ox + 1.2, oy - 1.0), (ox - 1.2, oy + 1.0)], 0.4), "#140e18")
        else:
            lz.pintar(lz.circulo(ox, oy, 2.2), "#05050c")
            lz.pintar(lz.circulo(ox, oy, 1.4), CRISTAL[4] if f != 3 else "#ff5a20")
            lz.pintar(lz.trazo([(ox - lado * 3.2, oy - 3.4), (ox + lado * 2.4, oy - 1.6)], 0.8), piel[0])                  # el ceño
    return lz.sprite(contorno=0.4)


if __name__ == "__main__":
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)

    def tira(nombre, fn, n):
        Image.fromarray(np.concatenate([fn(f) for f in range(n)], axis=1), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))

    tira("monolito", monolito, 3)
    tira("popo", popo, 5)
    tira("kipanga", kipanga, 6)
    for nombre, fn in (("penasco", penasco), ("pluma", pluma), ("estela", estela)):
        Image.fromarray(fn(), "RGBA").save(os.path.join(SALIDA, nombre + ".png"))
    print("Aguja pintada en", SALIDA)
