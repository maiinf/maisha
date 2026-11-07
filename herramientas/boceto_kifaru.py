"""Boceto de KIFARU DE BASALTO (jefe de Las Galerías de Ámbar), para decidir con Iam antes de que
Claude lo construya. Tres propuestas en la Cámara del Ancla Oeste con Maisha al lado:
  A · El Rinoceronte de Basalto y Geoda (recomendada): bestia colosal acorazada con placas de basalto y un
      cuerno-taladro de ámbar estelar; al chocar contra una vagoneta lanzada con Carga Sísmica o un pilar,
      su coraza dorsal se abre dejando expuesta la geoda de ámbar de su lomo.
  B · La Tuneladora de Bronce: gusano-máquina cilíndrico con cabeza giratoria que asoma por tres túneles.
  C · El Coloso de los Tres Yunques: golem de roca sin piernas que golpea el suelo creando ondas sísmicas.
Sale en documentacion/boceto_kifaru.png (600×256)."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from pintor import Lienzo, rampa  # noqa: E402
import cinematicas as ci  # noqa: E402

W, H = 600, 256
CAVERNA = ["#100d14", "#1c1622", "#2c2232", "#403246"]
BASALTO = ["#14131c", "#242232", "#38344c", "#524c6c", "#726a90"]
AMBAR = ["#421c04", "#7c3808", "#be6010", "#f0941e", "#ffc842", "#ffe888", "#fff9d6"]
COBRE = ["#2c1a10", "#583420", "#8c5432", "#c47c4c", "#eca870"]
SUELO = ["#241a18", "#3a2a24", "#543c32", "#705244"]
LUZ = (-0.6, -0.6, 0.55)


def camara_mina(lz, x0):
    x1 = x0 + 200
    zona = (lz.x >= x0) * (lz.x < x1)
    # Pared de caverna con vetas y geodas de ámbar al fondo
    fondo = zona * (lz.y < 148)
    lz.pintar(fondo, rampa(CAVERNA, np.clip(lz.y / 148.0, 0, 1)))
    for (gx, gy, r) in ((x0 + 30, 128, 6), (x0 + 172, 124, 7)):
        geoda = zona * lz.poligono([(gx - r, gy + 12), (gx - r * 0.4, gy - r * 2), (gx + r * 0.5, gy - r * 1.6), (gx + r, gy + 12)])
        lz.sombrear(geoda, AMBAR[1:], 4, LUZ)
        lz.sumar_luz(lz.desenfocar(geoda, 6), "#f0941e", 0.4)
    # Raíl de vagoneta al fondo de la cámara
    lz.sombrear(zona * (np.abs(lz.y - 148) < 2.2), COBRE[:4], 1.5, LUZ)
    # Suelo de roca ocre con anillo de arena
    suelo = zona * (lz.y >= 148)
    lz.pintar(suelo, rampa(SUELO, np.clip((lz.y - 148) / 108.0, 0, 1)))
    anillo = suelo * (np.abs(np.hypot(lz.x - (x0 + 100), (lz.y - 192) * 1.6) - 62) < 1.8)
    lz.pintar(anillo, AMBAR[3], 0.65)


def idea_kifaru(lz, x0):
    cx, cy = x0 + 108, 126
    lz.pintar(lz.elipse(cx, 176, 44, 10), "#0a080c", 0.6)
    # Patas macizas de basalto
    for dx in (-26, -10, 14, 28):
        pata = lz.poligono([(cx + dx - 6, 142), (cx + dx + 6, 142), (cx + dx + 7, 172), (cx + dx - 7, 172)])
        lz.sombrear(pata, BASALTO[:4], 4, LUZ)
    # Cuerpo acorazado con placas de basalto y corazón de geoda de ámbar en el lomo
    cuerpo = lz.elipse(cx + 4, cy, 38, 26)
    lz.sombrear(cuerpo, BASALTO, 14, LUZ)
    # Geoda dorsal que brilla entre las placas
    for (gx, gy, r) in ((cx - 2, cy - 22, 8), (cx + 12, cy - 20, 7), (cx + 24, cy - 15, 5)):
        cristal = lz.poligono([(gx - r, gy + 10), (gx, gy - r * 1.7), (gx + r, gy + 10)])
        lz.sombrear(cristal, AMBAR[1:], 4, LUZ)
        lz.sumar_luz(lz.desenfocar(cristal, 5), "#f0941e", 0.5)
    # Cabeza blindada inclinada para embestir hacia Maisha (izquierda)
    cabeza = lz.poligono([(cx - 22, cy - 12), (cx - 48, cy + 4), (cx - 42, cy + 20), (cx - 16, cy + 16)])
    lz.sombrear(cabeza, BASALTO, 8, LUZ)
    # Gran cuerno-taladro de ámbar estelar en el morro
    cuerno = lz.poligono([(cx - 42, cy + 2), (cx - 68, cy - 14), (cx - 48, cy + 14)])
    lz.sombrear(cuerno, AMBAR[2:], 5, LUZ)
    lz.sumar_luz(lz.desenfocar(cuerno, 5), "#ffc842", 0.55)
    # Ojo encendido de ámbar
    ojo = lz.elipse(cx - 32, cy + 4, 2.5, 2.0)
    lz.sumar_luz(lz.desenfocar(ojo, 3), "#ffc842", 0.8)
    lz.pintar(ojo, "#fff9d6")


def idea_tuneladora(lz, x0):
    cx, cy = x0 + 108, 128
    lz.pintar(lz.elipse(cx, 176, 42, 9), "#0a080c", 0.55)
    # Segmentos cilíndricos de bronce y basalto
    for k, (dx, dy, r) in enumerate(((26, 8, 20), (8, 0, 23), (-12, -4, 25), (-32, 4, 22))):
        seg = lz.elipse(cx + dx, cy + dy, r, r * 0.85)
        lz.sombrear(seg, COBRE if k % 2 == 0 else BASALTO, r * 0.5, LUZ)
    # Taladro giratorio frontal de ámbar
    taladro = lz.poligono([(cx - 46, cy - 10), (cx - 72, cy + 6), (cx - 46, cy + 20)])
    lz.sombrear(taladro, AMBAR[1:], 6, LUZ)
    lz.sumar_luz(lz.desenfocar(taladro, 5), "#f0941e", 0.5)


def idea_coloso(lz, x0):
    cx, cy = x0 + 106, 118
    lz.pintar(lz.elipse(cx, 176, 40, 9), "#0a080c", 0.55)
    # Torso trapezoidal de roca y hombreras de yunque
    torso = lz.poligono([(cx - 34, 78), (cx + 34, 78), (cx + 22, 168), (cx - 22, 168)])
    lz.sombrear(torso, BASALTO, 14, LUZ)
    nucleo = lz.elipse(cx, 118, 11, 14)
    lz.sombrear(nucleo, AMBAR[2:], 5, LUZ)
    lz.sumar_luz(lz.desenfocar(nucleo, 6), "#f0941e", 0.6)
    # Dos brazos-martillo gigantes apoyados en el suelo
    for dx in (-38, 38):
        mazo = lz.poligono([(cx + dx - 11, 126), (cx + dx + 11, 126), (cx + dx + 13, 172), (cx + dx - 13, 172)])
        lz.sombrear(mazo, COBRE, 6, LUZ)


def main():
    lz = Lienzo(W, H, semilla=740)
    for i, fn in enumerate((idea_kifaru, idea_tuneladora, idea_coloso)):
        x0 = i * 200
        camara_mina(lz, x0)
        fn(lz, x0)
        ci.maisha_luz(lz, x0 + 26, 220, e=1.0)
    for x in (199, 200, 399, 400):
        lz.pintar((np.abs(lz.x - x) < 0.8) * 1.0, AMBAR[3])

    salida = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "documentacion",
        "boceto_kifaru.png",
    )
    lz.guardar(salida)
    im = Image.open(salida).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 10)
    except OSError:
        f = ImageFont.load_default()
    titulos = [
        "A · El Kifaru de Basalto y Geoda",
        "B · La Tuneladora de Bronce",
        "C · El Coloso de los Yunques",
    ]
    for i, t in enumerate(titulos):
        d.rectangle((i * 200 + 4, 236, i * 200 + 196, 252), fill=(16, 12, 10))
        d.text((i * 200 + 8, 238), t, font=f, fill=(255, 222, 140))
    im.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
