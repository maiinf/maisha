"""EL GUARDIÁN DE LA GRUTA: el jefe de la Gruta de las Raíces (con el pintor de las cinemáticas).

    python3 herramientas/dibujar_guardian.py

Genera arte/zonas/raiz/guardian.png: 6 fotogramas de 120×96, mirando a la derecha (el juego lo voltea), un poco
desde arriba (como todo el juego):
  0 quieto (la marioneta: la cabeza gacha, la máscara puesta)      1 escarba (una pata delantera levantada: aviso)
  2 embiste (la cabeza baja, la cornamenta por delante, las patas estiradas)
  3 aturdido (sentado sobre las patas de atrás, la máscara torcida: se le puede dar)
  4 pisa fuerte (se alza de manos: de las pezuñas sale la ola de raíces)
  5 libre (sin máscara: los ojos dorados, flores y hojas nuevas en la cornamenta)
Un ciervo enorme y viejo, mitad animal y mitad raíz: el cuerpo de corteza con musgo, las patas como raíces, una
cornamenta de ramas, y en la cara una MÁSCARA DE GIZA (hueso blanco con grietas violetas).
"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ, rampa  # noqa: E402
from pintar_pasarelas import tira, CONTORNO, GIZA  # noqa: E402

LUZ = (-0.6, -0.7, 0.5)
CORTEZA = ["#140c08", "#22160e", "#342216", "#4a3220", "#62442c", "#7c583a", "#9a724c"]
MUSGO = ["#1d2e18", "#2f4a22", "#4a6a30", "#6a8a40"]
HUESO = ["#5a5266", "#8a8296", "#b8b0c4", "#dcd6e4", "#f4f0f8"]
W, H = 120, 96


def _pata(lz, cadera, rodilla, pie, grueso=4.0):
    """Una pata de ciervo de raíz: gruesa arriba, fina abajo, con su rodilla y una pezuña que se abre en raicillas."""
    arriba = lz.trazo([cadera, rodilla], grueso, grueso * 0.6)
    abajo = lz.trazo([rodilla, pie], grueso * 0.55, grueso * 0.35)
    pata = np.maximum(arriba, abajo)
    lz.sombrear(pata, CORTEZA, 2.2, LUZ, textura=lz.ruido(0.5, 2, semilla=int(cadera[0] * 3 + pie[1])), fuerza_tex=0.4)
    lz.pintar(lz.circulo(rodilla[0], rodilla[1], grueso * 0.42), CORTEZA[4], 0.8)
    for d in (-2.2, 0, 2.2):
        lz.pintar(lz.trazo([(pie[0], pie[1] - 1), (pie[0] + d, pie[1] + 2.2)], 0.8, 0.3), CORTEZA[2])


def _cornamenta(lz, x, y, libre, semilla, alto=34):
    """Una cornamenta grande de ramas: dos troncos que se abren hacia arriba y atrás, cada uno con muchas puntas."""
    rng = np.random.default_rng(semilla)
    ramas = np.zeros((lz.H, lz.W))
    for lado in (-1, 1):
        # una rama abre hacia atrás y la otra hacia delante (de perfil se ven las dos)
        base = (x + lado * 2.0, y)
        medio = (x + lado * 12, y - alto * 0.5)
        punta = (x + lado * 18 + (-4 if lado < 0 else 2), y - alto)
        tronco = lz.curva(base, medio, punta, n=26)
        ramas = np.maximum(ramas, lz.trazo(tronco, 2.8, 1.1))
        for k, (px, py) in enumerate(tronco[3::4]):
            largo = 5 + rng.random() * 5
            a = -math.pi / 2 + lado * 0.35 + (rng.random() - 0.5) * 0.6
            fin = (px + math.cos(a) * largo, py + math.sin(a) * largo)
            ramas = np.maximum(ramas, lz.trazo([(px, py), fin], 1.2, 0.4))
            if k % 2 == 0:
                ramas = np.maximum(ramas, lz.trazo([fin, (fin[0] + lado * 3, fin[1] - 3)], 0.7, 0.3))
    lz.sombrear(ramas, CORTEZA[1:], 1.6, LUZ, textura=lz.ruido(0.4, 1, semilla=semilla), fuerza_tex=0.3)
    if libre:
        hojas = np.zeros((lz.H, lz.W))
        cerca = lz.desenfocar(ramas, 2.5) > 0.06
        for k in range(26):
            hx, hy = x - 8 + (rng.random() - 0.5) * 40, y - 6 - rng.random() * alto
            hojas = np.maximum(hojas, lz.elipse(hx, hy, 2.0, 1.0, rng.random() * 180))
        lz.pintar(hojas * cerca, rampa(["#3e9a35", "#6fcf4f", "#b4e890"], lz.ruido(0.5, 1, semilla=semilla + 1)), 0.95)
        for k in range(9):
            fx, fy = x - 8 + (rng.random() - 0.5) * 36, y - 8 - rng.random() * alto * 0.9
            if cerca[int(fy * lz.s), int(fx * lz.s)] if 0 <= fy < H and 0 <= fx < W else False:
                lz.pintar(lz.circulo(fx, fy, 1.2), ["#f4b39a", "#fde27e", "#e8f0dc"][k % 3])
    else:
        # hilos de la marioneta: las grietas violetas que suben por la cornamenta
        lz.pintar(ramas * (lz.ruido(0.8, 2, semilla=semilla) > 0.7), GIZA[3], 0.7)


def guardian(f):
    lz = Lienzo(W, H, s=5, semilla=601 + f)
    libre = f == 5
    lz.pintar(lz.desenfocar(lz.elipse(58, 90, 44, 4), 1.0), "#050404", 0.6)
    # la postura: dónde están la grupa, el pecho y la cabeza (y cuánto se alza o se agacha)
    ajuste = {0: (0, 0, 0), 1: (0, -2, -3), 2: (0, 4, 8), 3: (0, 8, 4), 4: (0, -14, -26), 5: (0, -2, -10)}[f]
    gy = 52 + ajuste[1] * 0.3
    py = 50 + ajuste[1]
    grupa = (34, gy)
    pecho = (70, py)
    cabeza = (90 + (8 if f == 2 else 0), 40 + ajuste[2] + (14 if f == 2 else 0))
    # patas de atrás (sentado si está aturdido)
    if f == 3:
        _pata(lz, (34, gy + 6), (24, gy + 18), (32, 88), 6)
        _pata(lz, (40, gy + 8), (32, gy + 20), (42, 88), 6)
    else:
        _pata(lz, (32, gy + 8), (26, gy + 22), (28 - (6 if f == 2 else 0), 88), 6)
        _pata(lz, (40, gy + 10), (36, gy + 24), (40, 88), 6)
    # patas de delante, según lo que haga
    if f == 1:
        _pata(lz, (68, py + 8), (76, py + 16), (74, py + 24), 5)          # la que escarba, levantada
        _pata(lz, (76, py + 10), (78, py + 24), (80, 88), 5)
    elif f == 4:
        _pata(lz, (68, py + 6), (80, py + 12), (82, py + 22), 5)
        _pata(lz, (74, py + 8), (88, py + 14), (90, py + 24), 5)
    elif f == 2:
        _pata(lz, (70, py + 8), (84, py + 18), (96, 86), 5)
        _pata(lz, (78, py + 8), (90, py + 20), (102, 88), 5)
    else:
        _pata(lz, (68, py + 8), (70, py + 24), (68, 88), 5)
        _pata(lz, (76, py + 10), (80, py + 24), (80, 88), 5)
    # el cuerpo: grupa, vientre y pecho (un ciervo, no un saco)
    cuerpo = np.maximum.reduce([lz.elipse(grupa[0], grupa[1], 14, 12), lz.elipse(pecho[0], pecho[1], 15, 13),
                                lz.elipse((grupa[0] + pecho[0]) / 2, (grupa[1] + pecho[1]) / 2 + 2, 20, 9)])
    vetas = (np.abs(np.sin(lz.x * 0.35 + np.sin(lz.y * 0.4) * 2)) < 0.15).astype(float)
    lz.sombrear(cuerpo, CORTEZA, 10, LUZ, textura=lz.ruido(0.8, 2, semilla=602) * 0.6 + (1 - vetas) * 0.4, fuerza_tex=0.5)
    musgo = cuerpo * (lz.ruido(2, 2, semilla=603) > 0.52) * (lz.y < (grupa[1] + pecho[1]) / 2 - 2)
    lz.pintar(musgo, rampa(MUSGO, lz.ruido(0.6, 2, semilla=604)), 0.85)
    vientre = cuerpo * (lz.y > (grupa[1] + pecho[1]) / 2 + 6)
    lz.pintar(vientre, CORTEZA[5], 0.5)
    if libre:
        lz.pintar((lz.ruido(0.6, 1, semilla=605) > 0.86) * musgo, "#fde27e", 0.9)
    # la cola corta, de raicillas
    for k in range(4):
        lz.pintar(lz.trazo([(grupa[0] - 12, grupa[1] - 4), (grupa[0] - 17 - k, grupa[1] + k * 2)], 0.9, 0.3), CORTEZA[3])
    # el cuello, fuerte, y la cabeza alargada con su hocico
    cx, cy = cabeza
    cuello = lz.trazo([(pecho[0] + 4, pecho[1] - 6), (cx - 6, cy + 4)], 8, 5.5)
    lz.sombrear(cuello, CORTEZA, 5, LUZ, textura=lz.ruido(0.6, 2, semilla=606), fuerza_tex=0.4)
    angulo = 35 if f == 2 else (15 if f in (0, 3) else 5)
    craneo = lz.elipse(cx, cy, 6.5, 5.5)
    hocico = lz.elipse(cx + math.cos(math.radians(angulo)) * 9, cy + math.sin(math.radians(angulo)) * 9, 6, 3.6, angulo)
    lz.sombrear(np.maximum(craneo, hocico), CORTEZA[1:], 4, LUZ)
    lz.sombrear(lz.elipse(cx - 4, cy - 6, 4, 1.6, -40), CORTEZA[2:], 1, LUZ)                 # la oreja
    _cornamenta(lz, cx - 1, cy - 5, libre, 607 + f, alto=min(24, cy - 8))
    hx = cx + math.cos(math.radians(angulo)) * 14
    hy = cy + math.sin(math.radians(angulo)) * 14
    if libre:
        lz.pintar(lz.elipse(cx + 2, cy - 1, 1.8, 1.4), "#f9d77a")
        lz.brillo(lz.elipse(cx + 2, cy - 1, 1.8, 1.4), "#fde27e", 2.0, 0.6)
        lz.pintar(lz.circulo(cx + 2.5, cy - 1, 0.6), "#3a2410")
        lz.pintar(lz.circulo(hx, hy, 1.1), "#140c08")
    else:
        # la máscara de Giza: un cráneo de ciervo de hueso blanco que le tapa la cara, con grietas violetas
        giro = angulo + (25 if f == 3 else 0)
        frente = lz.elipse(cx + 1, cy - 0.5, 6, 5, giro)
        nariz = lz.trazo([(cx + 2, cy), (hx - 1, hy)], 3.2, 1.8)
        mascara = np.maximum(frente, nariz)
        lz.sombrear(mascara, HUESO, 3.5, LUZ)
        grietas = (np.abs(np.sin(lz.x * 1.1 + lz.ruido(0.8, 2, semilla=608) * 5)) < 0.12) * mascara
        lz.pintar(grietas, GIZA[3], 0.95)
        lz.brillo(grietas, GIZA[3], 1.6, 0.4)
        ojo = lz.elipse(cx + 2, cy - 1, 2.0, 1.5, giro)
        lz.pintar(ojo, "#140818")
        lz.pintar(lz.circulo(cx + 2.2, cy - 1, 0.7), GIZA[4])
        lz.brillo(lz.circulo(cx + 2.2, cy - 1, 0.7), GIZA[4], 1.6, 0.6)
    return lz.sprite(contorno=CONTORNO)


def main():
    hoja = tira([guardian(f) for f in range(6)])
    ruta = os.path.join(RAIZ, "arte", "zonas", "raiz", "guardian.png")
    hoja.save(ruta)
    print("guardado:", ruta, hoja.size)


if __name__ == "__main__":
    main()
