"""Boceto de KENGELE, LA GRAN CAMPANA MUDA (jefe de El Observatorio de la Aurora), para decidir con Iam antes de que
Claude lo construya. Tres propuestas en la Gran Cúpula bajo la aurora boreal y con Maisha al lado:
  A · La Gran Campana de Bronce y Tinta (recomendada): campana colosal grabada con constelaciones y badajo de tinta
      helada; al cargar los diapasones de la cúpula con el Sigilo de Rayo, resuena de verdad y cae aturdida.
  B · El Astrolabio Viviente: anillos concéntricos de latón que giran alrededor de un núcleo de aurora.
  C · El Carillón de los Tres Armiños: órgano de tubos y campanas con tres figuras de piedra que tocan por turnos.
Sale en documentacion/boceto_kengele.png (600×256)."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from pintor import Lienzo, rampa  # noqa: E402
import cinematicas as ci  # noqa: E402

W, H = 600, 256
NOCHE = ["#0a0a18", "#14142c", "#222044", "#363264"]
AURORA = ["#184848", "#288878", "#50d0a8", "#98ffe0"]
BRONCE = ["#2c1c08", "#583a14", "#8c6022", "#c48c36", "#ecb858", "#"]
ORO = ["#3a2408", "#6a4614", "#a07020", "#d4a034", "#f0cc60", "#fff0b0"]
TINTA = ["#05040a", "#0e0a1c", "#1e1636", "#36285a", "#584288"]
PIEDRA = ["#241e38", "#3a3056", "#564878", "#7868a0"]
LUZ = (-0.6, -0.6, 0.55)


def cupula(lz, x0):
    x1 = x0 + 200
    zona = (lz.x >= x0) * (lz.x < x1)
    # Cielo nocturno con cortinas de aurora boreal al fondo
    cielo = zona * (lz.y < 146)
    lz.pintar(cielo, rampa(NOCHE, np.clip(lz.y / 146.0, 0, 1)))
    onda_aurora = np.sin((lz.x - x0) * 0.06) * 14 + 46
    banda = cielo * (np.abs(lz.y - onda_aurora) < 18)
    lz.pintar(banda, AURORA[2], 0.35)
    lz.sumar_luz(lz.desenfocar(banda, 10), "#50e8b8", 0.35)
    # Barandilla curva de cobre y diapasones a los lados
    lz.sombrear(zona * (np.abs(lz.y - 146) < 2.5), ORO[:5], 2, LUZ)
    for dx in (24, 176):
        diap = zona * lz.poligono([(x0 + dx - 5, 146), (x0 + dx - 5, 118), (x0 + dx + 5, 118), (x0 + dx + 5, 146)])
        lz.sombrear(diap, ORO, 3, LUZ)
        lz.sumar_luz(lz.desenfocar(lz.elipse(x0 + dx, 118, 6, 6), 5), "#ffe878", 0.55)
    # Suelo circular de la Gran Cúpula con líneas de constelación doradas
    suelo = zona * (lz.y >= 146)
    lz.pintar(suelo, rampa(PIEDRA[:3], np.clip((lz.y - 146) / 110.0, 0, 1)))
    anillo = suelo * (np.abs( np.hypot(lz.x - (x0 + 100), (lz.y - 190) * 1.6) - 62 ) < 1.8)
    lz.pintar(anillo, ORO[3], 0.75)


def idea_campana(lz, x0):
    cx = x0 + 105
    # Sombra en la cúpula
    lz.pintar(lz.elipse(cx, 186, 36, 9), TINTA[0], 0.6)
    # Yugo superior con orejas de armiño talladas en bronce
    yugo = lz.poligono([(cx - 22, 46), (cx + 22, 46), (cx + 16, 62), (cx - 16, 62)])
    lz.sombrear(yugo, ORO[:5], 5, LUZ)
    # Cuerpo de la gran campana de bronce agrietada por Tinta Quieta
    campana = lz.poligono([
        (cx - 18, 60), (cx + 18, 60),
        (cx + 26, 102), (cx + 42, 132),
        (cx - 42, 132), (cx - 26, 102)
    ])
    lz.sombrear(campana, ORO, 14, LUZ)
    # Friso grabado y grieta de tinta con ojos brillantes
    lz.pintar(campana * (np.abs(lz.y - 122) < 3), TINTA[2])
    hueco = lz.elipse(cx, 92, 14, 10)
    lz.pintar(hueco, TINTA[0])
    for dx in (-6, 6):
        ojo = lz.elipse(cx + dx, 92, 2.2, 3.0)
        lz.sumar_luz(lz.desenfocar(ojo, 3), "#b890ff", 0.8)
        lz.pintar(ojo, "#f0e4ff")
    # Badajo de tinta helada colgando debajo
    badajo = lz.elipse(cx, 142, 11, 11)
    lz.sombrear(badajo, TINTA[1:], 6, LUZ)


def idea_astrolabio(lz, x0):
    cx, cy = x0 + 105, 96
    lz.pintar(lz.elipse(cx, 186, 34, 8), TINTA[0], 0.5)
    # Tres anillos concéntricos de latón inclinados
    for rx, ry, g in ((44, 44, 4.0), (34, 22, 3.5), (22, 36, 3.5)):
        d_anillo = np.abs(np.hypot((lz.x - cx) / rx, (lz.y - cy) / ry) - 1.0) * min(rx, ry)
        aro = (d_anillo < g) * 1.0
        lz.sombrear(aro, ORO, 3, LUZ)
    # Núcleo de tinta y aurora con un gran ojo astral
    nucleo = lz.elipse(cx, cy, 14, 14)
    lz.sombrear(nucleo, TINTA[1:], 6, LUZ)
    ojo = lz.elipse(cx, cy, 6, 8)
    lz.sumar_luz(lz.desenfocar(ojo, 6), "#60f0c8", 0.85)
    lz.pintar(ojo, "#d8fff4")
    lz.pintar(lz.elipse(cx, cy, 2.2, 5.0), TINTA[0])


def idea_carillon(lz, x0):
    cx = x0 + 105
    # Base de piedra y tubos de órgano de bronce
    base = lz.poligono([(cx - 46, 116), (cx + 46, 116), (cx + 50, 168), (cx - 50, 168)])
    lz.sombrear(base, PIEDRA, 8, LUZ)
    for k, dx in enumerate(range(-36, 40, 12)):
        alto = 48 + (3 - abs(k - 3)) * 12
        tubo = lz.poligono([(cx + dx - 4, 116 - alto), (cx + dx + 4, 116 - alto),
                            (cx + dx + 4, 116), (cx + dx - 4, 116)])
        lz.sombrear(tubo, ORO, 4, LUZ)
    # Tres bustos de armiños campaneros en las hornacinas
    for dx in (-26, 0, 26):
        h = lz.elipse(cx + dx, 142, 10, 14)
        lz.sombrear(h, ["#b8b4cc", "#dcd8ec", "#f4f2ff"], 5, LUZ)
        for ox in (-3, 3):
            lz.pintar(lz.elipse(cx + dx + ox, 140, 1.4, 1.8), "#9068e8")


def main():
    lz = Lienzo(W, H, semilla=720)
    for i, fn in enumerate((idea_campana, idea_astrolabio, idea_carillon)):
        x0 = i * 200
        cupula(lz, x0)
        fn(lz, x0)
        ci.maisha_luz(lz, x0 + 28, 220, e=1.0)
    for x in (199, 200, 399, 400):
        lz.pintar((np.abs(lz.x - x) < 0.8) * 1.0, ORO[3])

    salida = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "documentacion", "boceto_kengele.png")
    lz.guardar(salida)
    im = Image.open(salida).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 10)
    except OSError:
        f = ImageFont.load_default()
    titulos = [
        "A · La Gran Campana Muda",
        "B · El Astrolabio Viviente",
        "C · El Carillón de Armiños",
    ]
    for i, t in enumerate(titulos):
        d.rectangle((i * 200 + 4, 236, i * 200 + 196, 252), fill=(10, 6, 18))
        d.text((i * 200 + 10, 238), t, font=f, fill=(248, 226, 160))
    im.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
