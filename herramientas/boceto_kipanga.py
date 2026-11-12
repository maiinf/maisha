"""Boceto de KIPANGA ASTRAL (jefe de La Aguja Caída), para decidir con Iam antes de que Claude lo construya.
Tres propuestas en el Nido de la Cima de la Aguja con Maisha al lado:
  A · El Halcón de Obsidiana y Cristal (recomendada): rapaz titánica con armadura de lajas de obsidiana,
      pecho de cristal resonante y garras de hierro meteórico; planea lanzando plumas-cuchilla que emiten
      zumbidos; al hacer vibrar los monolitos con la Resonancia de Ámbar, la onda sónica quiebra su vuelo.
  B · El Fénix del Meteorito: ave de fuego astral y plasma con estelas de brasas cósmicas en picado.
  C · El Grifo de Diapasón: cuadrúpedo alado con cabeza de águila y dos antenas-diapasón gemelas.
Sale en documentacion/boceto_kipanga.png (600×256)."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from pintor import Lienzo, rampa  # noqa: E402
import cinematicas as ci  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 600, 256
CIELO_ASTRAL = ["#0c0e18", "#141828", "#1c223a", "#2a3454"]
OBSIDIANA = ["#0e1018", "#181c28", "#282e42", "#3e4866", "#5a6890"]
CRISTAL = ["#183848", "#2a627c", "#4494bc", "#74ceeb", "#c2f2ff"]
AMBAR = ["#3a1804", "#6e3208", "#aa5410", "#e48a20", "#ffbf48", "#ffe690"]
PLATA = ["#222634", "#3e4458", "#646e8c", "#96a2c4", "#d4dcfa"]
SUELO = ["#181a26", "#262b3c", "#383f56", "#4e5774"]
LUZ = (-0.6, -0.6, 0.55)


def nido_aguja(lz, x0):
    x1 = x0 + 200
    zona = (lz.x >= x0) * (lz.x < x1)
    # Fondo de cielo astral con estrellas y nebulosa lejana
    fondo = zona * (lz.y < 148)
    lz.pintar(fondo, rampa(CIELO_ASTRAL, np.clip(lz.y / 148.0, 0, 1)))
    # Vértice de la Aguja Caída (roca inclinada hacia el abismo)
    aguja = zona * lz.poligono([(x0 + 10, 148), (x0 + 80, 40), (x0 + 130, 44), (x0 + 190, 148)])
    lz.sombrear(aguja, OBSIDIANA[:4], 8, LUZ)
    # Suelo del Nido (plataforma circular con runas de viento)
    suelo = zona * (lz.y >= 148)
    lz.pintar(suelo, rampa(SUELO, np.clip((lz.y - 148) / 108.0, 0, 1)))
    anillo = suelo * (np.abs(np.hypot(lz.x - (x0 + 100), (lz.y - 192) * 1.6) - 62) < 2.0)
    lz.pintar(anillo, CRISTAL[3], 0.7)
    lz.sumar_luz(lz.desenfocar(anillo, 5), "#74ceeb", 0.35)


def idea_halcon(lz, x0):
    cx, cy = x0 + 105, 105
    # Sombra en el suelo
    lz.pintar(lz.elipse(cx, 178, 42, 9), "#080a12", 0.6)
    # Alas abiertas de lajas afiladas de obsidiana
    ala_izq = lz.poligono([(cx - 8, cy - 10), (cx - 56, cy - 38), (cx - 72, cy - 16), (cx - 48, cy + 12), (cx - 16, cy + 8)])
    ala_der = lz.poligono([(cx + 8, cy - 10), (cx + 56, cy - 38), (cx + 72, cy - 16), (cx + 48, cy + 12), (cx + 16, cy + 8)])
    lz.sombrear(ala_izq, OBSIDIANA, 6, LUZ)
    lz.sombrear(ala_der, OBSIDIANA, 6, LUZ)
    # Bordes de plumas-cuchilla de cristal
    lz.pintar(ala_izq * (lz.y < cy - 20), CRISTAL[3], 0.7)
    lz.pintar(ala_der * (lz.y < cy - 20), CRISTAL[3], 0.7)
    # Cola en abanico de meteorito
    cola = lz.poligono([(cx - 14, cy + 15), (cx + 14, cy + 15), (cx + 22, cy + 50), (cx - 22, cy + 50)])
    lz.sombrear(cola, OBSIDIANA[:4], 5, LUZ)
    # Cuerpo y pecho de cristal resonante
    cuerpo = lz.elipse(cx, cy + 5, 18, 26)
    lz.sombrear(cuerpo, OBSIDIANA, 7, LUZ)
    pecho_cristal = lz.elipse(cx, cy + 8, 10, 14)
    lz.sombrear(pecho_cristal, CRISTAL, 6, LUZ)
    lz.sumar_luz(lz.desenfocar(pecho_cristal, 6), "#74ceeb", 0.5)
    # Cabeza y pico ganchudo de hierro meteórico
    cabeza = lz.elipse(cx, cy - 20, 12, 11)
    pico = lz.poligono([(cx - 4, cy - 18), (cx + 4, cy - 18), (cx, cy - 8)])
    lz.sombrear(cabeza, OBSIDIANA, 5, LUZ)
    lz.sombrear(pico, AMBAR[3:], 3, LUZ)
    # Ojos brillantes
    lz.pintar(lz.elipse(cx - 5, cy - 21, 2, 2), AMBAR[-1])
    lz.pintar(lz.elipse(cx + 5, cy - 21, 2, 2), AMBAR[-1])
    # Garras que sujetan la 3.ª Cadena
    cadena = (np.abs(lz.y - (cy + 36)) < 3) * (np.abs(lz.x - cx) < 38)
    lz.sombrear(cadena, PLATA, 2, LUZ)


def idea_fenix(lz, x0):
    cx, cy = x0 + 105, 105
    lz.pintar(lz.elipse(cx, 178, 38, 9), "#080a12", 0.6)
    # Alas flameantes de plasma estelar
    ala_izq = lz.poligono([(cx - 6, cy - 8), (cx - 50, cy - 44), (cx - 64, cy - 18), (cx - 40, cy + 15), (cx - 12, cy + 10)])
    ala_der = lz.poligono([(cx + 6, cy - 8), (cx + 50, cy - 44), (cx + 64, cy - 18), (cx + 40, cy + 15), (cx + 12, cy + 10)])
    lz.sombrear(ala_izq, AMBAR[1:5], 6, LUZ)
    lz.sombrear(ala_der, AMBAR[1:5], 6, LUZ)
    lz.sumar_luz(lz.desenfocar(ala_izq + ala_der, 7), "#e48a20", 0.45)
    # Cuerpo de brasa y cresta de fuego
    cuerpo = lz.elipse(cx, cy + 4, 16, 24)
    lz.sombrear(cuerpo, AMBAR, 7, LUZ)
    cabeza = lz.elipse(cx, cy - 18, 11, 10)
    pico = lz.poligono([(cx - 3, cy - 16), (cx + 3, cy - 16), (cx, cy - 8)])
    lz.sombrear(cabeza, AMBAR[2:], 5, LUZ)
    lz.sombrear(pico, PLATA[:3], 3, LUZ)
    lz.sumar_luz(lz.desenfocar(cuerpo, 8), "#ffbf48", 0.5)


def idea_grifo(lz, x0):
    cx, cy = x0 + 105, 110
    lz.pintar(lz.elipse(cx, 178, 44, 10), "#080a12", 0.6)
    # Patas traseras felinas de basalto y delanteras de ave
    patas = lz.poligono([(cx - 24, cy + 20), (cx - 14, cy + 50), (cx + 14, cy + 50), (cx + 24, cy + 20)])
    lz.sombrear(patas, OBSIDIANA[:4], 6, LUZ)
    # Cuerpo híbrido cuadrúpedo
    cuerpo = lz.elipse(cx, cy + 15, 24, 20)
    lz.sombrear(cuerpo, OBSIDIANA, 7, LUZ)
    # Alas de cristal desplegadas
    alas = lz.poligono([(cx - 52, cy - 30), (cx + 52, cy - 30), (cx + 22, cy + 10), (cx - 22, cy + 10)])
    lz.sombrear(alas, CRISTAL, 6, LUZ)
    # Cabeza con antenas-diapasón dobles
    cabeza = lz.elipse(cx, cy - 15, 13, 13)
    lz.sombrear(cabeza, OBSIDIANA, 5, LUZ)
    for dx in (-7, 7):
        diap = (np.abs(lz.x - (cx + dx)) < 2) * (lz.y > cy - 38) * (lz.y < cy - 15)
        lz.pintar(diap, AMBAR[4])
        lz.sumar_luz(lz.desenfocar(diap, 3), "#ffe690", 0.4)


def main():
    lz = Lienzo(W, H, semilla=740)
    for i, fn in enumerate((idea_halcon, idea_fenix, idea_grifo)):
        x0 = i * 200
        nido_aguja(lz, x0)
        fn(lz, x0)
        ci.maisha_luz(lz, x0 + 26, 218, e=1.0)

    # Divisores entre propuestas
    for x in (199, 200, 399, 400):
        lz.pintar((np.abs(lz.x - x) < 0.8) * 1.0, CRISTAL[3])

    os.makedirs(os.path.join(RAIZ, "documentacion"), exist_ok=True)
    salida = os.path.join(RAIZ, "documentacion", "boceto_kipanga.png")
    lz.guardar(salida)

    im = Image.open(salida).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        fb = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 10)
    except OSError:
        fb = ImageFont.load_default()

    titulos = [
        "A · Halcón de Obsidiana (⭐)",
        "B · Fénix del Meteorito",
        "C · Grifo de Diapasón",
    ]
    for i, tit in enumerate(titulos):
        d.rectangle((i * 200 + 4, 236, i * 200 + 196, 252), fill=(12, 14, 24))
        d.text((i * 200 + 8, 238), tit, font=fb, fill=(255, 230, 144) if i == 0 else (194, 242, 255))

    im.save(salida)
    print("boceto de Kipanga guardado en:", salida)


if __name__ == "__main__":
    main()
