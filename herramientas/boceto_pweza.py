"""Boceto de PWEZA, EL PULPO DE TINTA (jefe de El Canal de Tinta), para decidir con Iam antes de que Claude
lo construya. Tres propuestas en la Gran Dársena (muelle de piedra, canal de tinta profunda y placas de hielo)
y con Maisha al lado para ver la escala:
  A · El Calamar del Tintero Real (⭐ recomendada): metido dentro de un tintero gigante de latón y cristal agrietado;
      saca tentáculos acabados en plumillas de oro. El Sigilo de Hielo congela el tentáculo y vuelca el tintero.
  B · El Pulpo de Pergaminos: tejido con rollos de pergamino empapados en tinta y sellos de lacre rojo como ventosas.
  C · La Hidra de Ocho Plumas: ocho cuellos largos de tinta pura con una corona dorada que salta entre cabezas.
Sale en documentacion/boceto_pweza.png (600×256)."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from pintor import Lienzo, rampa  # noqa: E402
import cinematicas as ci  # noqa: E402

W, H = 600, 256
MORADO = ["#100a1c", "#1c1230", "#2c1e48", "#422c66", "#5e4088", "#805ea8", "#a884cc"]
ORO = ["#3a2408", "#6a4614", "#a07020", "#d4a034", "#f0cc60", "#fff0b0"]
TINTA = ["#05040a", "#0c0818", "#18122c", "#281e44", "#443468"]
HIELO = ["#386890", "#5898c4", "#88c8ec", "#bce8ff", "#ecfcff"]
PAPEL = ["#7a6850", "#a89474", "#d4c2a0", "#f2e6cc"]
LACRE = ["#4a1018", "#7a1c28", "#b42c3c", "#e05060"]
LUZ = (-0.6, -0.6, 0.55)


def darsena(lz, x0):
    """Fondo de cada panel: pared de esclusa al norte, canal de tinta profunda en el centro y muelle abajo."""
    x1 = x0 + 200
    zona = (lz.x >= x0) * (lz.x < x1)
    # Pared de sillería morada al fondo con arcos de acueducto
    pared = zona * (lz.y < 68)
    lz.pintar(pared, rampa(MORADO[1:5], np.clip(lz.y / 70.0, 0, 1)))
    for k in range(3):
        ax = x0 + 36 + k * 64
        arco = pared * (lz.elipse(ax, 68, 18, 28) + ((np.abs(lz.x - ax) < 18) * (lz.y > 46)) > 0)
        lz.pintar(arco, TINTA[0])
    lz.sombrear(zona * (np.abs(lz.y - 68) < 3), ORO[:4], 2, LUZ)
    # Tinta profunda en el canal (y = 68..176)
    agua = zona * (lz.y >= 68) * (lz.y < 176)
    ondas = (np.sin(lz.x * 0.18 + lz.y * 0.35) * np.cos(lz.y * 0.22) > 0.55) * 0.25
    lz.pintar(agua, rampa(TINTA[:4], np.clip((lz.y - 68) / 110.0 + ondas, 0, 1)))
    # Placa de tinta helada cerca del muelle
    placa = agua * lz.poligono([(x0 + 18, 152), (x0 + 42, 144), (x0 + 66, 150), (x0 + 60, 166), (x0 + 24, 168)])
    lz.sombrear(placa, HIELO, 3, LUZ)
    # Muelle de piedra abajo (y >= 176)
    muelle = zona * (lz.y >= 176)
    juntas = (((lz.x % 22) < 1) + ((lz.y % 14) < 1) > 0) * 0.2
    lz.pintar(muelle, rampa(["#261c38", "#3e3058", "#5c487c"], np.clip((lz.y - 176) / 80.0 - juntas, 0, 1)))
    lz.sombrear(zona * (np.abs(lz.y - 176) < 2.5), ORO[1:5], 2, LUZ)


def idea_tintero_real(lz, x0):
    cx = x0 + 105
    # Sombra/ondas en la tinta
    lz.pintar(lz.elipse(cx, 134, 48, 14), TINTA[0], 0.7)
    # El gran tintero de cristal y latón flotando inclinado
    frasco = lz.poligono([(cx - 32, 92), (cx + 32, 92), (cx + 38, 134), (cx - 38, 134)])
    lz.sombrear(frasco, ["#161028", "#2c2248", "#564882", "#9888c4"], 10, LUZ)
    cuello = lz.poligono([(cx - 22, 74), (cx + 22, 74), (cx + 26, 92), (cx - 26, 92)])
    lz.sombrear(cuello, ORO, 6, LUZ)
    lz.sombrear(lz.poligono([(cx - 38, 126), (cx + 38, 126), (cx + 40, 136), (cx - 40, 136)]), ORO[:5], 4, LUZ)
    # Cabeza del pulpo asomando del tintero con corona de archivero y lentes rotos
    cabeza = lz.elipse(cx, 58, 24, 20)
    lz.sombrear(cabeza, MORADO[1:6], 12, LUZ)
    for dx in (-8, 8):
        ojo = lz.elipse(cx + dx, 64, 3.2, 4.0)
        lz.sumar_luz(lz.desenfocar(ojo, 3), "#f0c050", 0.8)
        lz.pintar(ojo, "#fff4b8")
    # Tentáculos rematados en plumillas doradas (uno atrapado en la placa de hielo)
    tentaculos = [
        [(cx - 24, 110), (cx - 52, 124), (x0 + 42, 154)],
        [(cx + 26, 108), (cx + 56, 118), (cx + 64, 152)],
        [(cx - 12, 124), (cx - 26, 148), (cx - 18, 168)],
        [(cx + 12, 124), (cx + 28, 146), (cx + 22, 166)],
    ]
    for pts in tentaculos:
        t = lz.trazo(pts, 4.5, 2.0)
        lz.sombrear(t, MORADO[1:6], 4, LUZ)
        px, py = pts[-1]
        plumilla = lz.poligono([(px - 4, py - 4), (px + 4, py - 4), (px, py + 7)])
        lz.sombrear(plumilla, ORO[1:], 2, LUZ)
    # Témpano de hielo apresando el primer tentáculo
    hielo = lz.poligono([(x0 + 30, 148), (x0 + 44, 136), (x0 + 56, 148), (x0 + 50, 162), (x0 + 32, 160)])
    lz.sombrear(hielo, HIELO[1:], 3, LUZ)


def idea_pergaminos(lz, x0):
    cx = x0 + 105
    lz.pintar(lz.elipse(cx, 136, 52, 14), TINTA[0], 0.7)
    # Manto hecho de rollos de pergamino superpuestos
    manto = lz.elipse(cx, 76, 32, 34)
    bandas = (np.sin((lz.y - 44) * 0.45 + np.cos((lz.x - cx) * 0.15)) > 0.3) * 1.0
    lz.sombrear(manto, PAPEL, 14, LUZ, textura=bandas, fuerza_tex=0.35)
    # Hueco de tinta en la cara y ojos violetas
    cara = lz.elipse(cx, 88, 18, 12)
    lz.pintar(cara, TINTA[0])
    for dx in (-7, 7):
        ojo = lz.elipse(cx + dx, 88, 2.5, 3.5)
        lz.sumar_luz(lz.desenfocar(ojo, 3), "#b080ff", 0.8)
        lz.pintar(ojo, "#e8d4ff")
    # Tentáculos de bandas de pergamino con sellos de lacre rojo como ventosas
    for lado in (-1, 1):
        for k, (dx, dy) in enumerate(((46, 138), (64, 118), (28, 158))):
            pts = [(cx + lado * 14, 102), (cx + lado * (dx - 12), (102 + dy) // 2), (cx + lado * dx, dy)]
            t = lz.trazo(pts, 4.2, 2.2)
            lz.sombrear(t, PAPEL, 3, LUZ)
            for s in (0.45, 0.78):
                sx = int(pts[0][0] * (1 - s) + pts[-1][0] * s)
                sy = int(pts[0][1] * (1 - s) + pts[-1][1] * s)
                lz.sombrear(lz.elipse(sx, sy, 3.2, 3.2), LACRE, 2, LUZ)


def idea_hidra_plumas(lz, x0):
    cx = x0 + 105
    # Cinco cuellos principales emergiendo de remolinos de tinta
    cabezas = [(-54, 78, 0), (-26, 62, 0), (0, 50, 1), (28, 64, 0), (54, 80, 0)]
    for dx, cy, reina in cabezas:
        hx = cx + dx
        bx = cx + int(dx * 0.75)
        lz.pintar(lz.elipse(bx, 138, 14, 5), TINTA[0], 0.8)
        cuello = lz.trazo([(bx, 138), (hx - dx * 0.15, (138 + cy) // 2), (hx, cy)], 5.0, 3.2)
        lz.sombrear(cuello, TINTA[1:] + [MORADO[4]], 4, LUZ)
        cab = lz.elipse(hx, cy, 10, 8)
        lz.sombrear(cab, MORADO[1:6], 5, LUZ)
        # Pico de plumilla dorada
        pico = lz.poligono([(hx - 4, cy + 4), (hx + 4, cy + 4), (hx, cy + 14)])
        lz.sombrear(pico, ORO[1:], 2, LUZ)
        for ox in (-3.5, 3.5):
            lz.pintar(lz.elipse(hx + ox, cy - 1, 1.5, 2.0), "#e0c8ff")
        if reina:
            corona = lz.poligono([(hx - 9, cy - 7), (hx - 6, cy - 16), (hx, cy - 10),
                                  (hx + 6, cy - 16), (hx + 9, cy - 7)])
            lz.sombrear(corona, ORO[1:], 3, LUZ)


def main():
    lz = Lienzo(W, H, semilla=710)
    for i, fn in enumerate((idea_tintero_real, idea_pergaminos, idea_hidra_plumas)):
        x0 = i * 200
        darsena(lz, x0)
        fn(lz, x0)
        ci.maisha_luz(lz, x0 + 28, 220, e=1.0)
    for x in (199, 200, 399, 400):
        lz.pintar((np.abs(lz.x - x) < 0.8) * 1.0, ORO[3])

    salida = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "documentacion", "boceto_pweza.png")
    lz.guardar(salida)
    im = Image.open(salida).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 10)
    except OSError:
        f = ImageFont.load_default()
    titulos = [
        "A · El Calamar del Tintero",
        "B · El Pulpo de Pergaminos",
        "C · La Hidra de Ocho Plumas",
    ]
    for i, t in enumerate(titulos):
        d.rectangle((i * 200 + 4, 236, i * 200 + 196, 252), fill=(10, 6, 18))
        d.text((i * 200 + 10, 238), t, font=f, fill=(248, 226, 160))
    im.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
