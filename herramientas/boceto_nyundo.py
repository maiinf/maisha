"""Boceto de NYUNDO, EL GRAN MARTILLO (jefe de La Fundición de Escoria), para decidir con Iam antes de que
Claude lo construya. Tres propuestas en la Gran Fragua sobre el foso de escoria fundida con Maisha al lado:
  A · El Martillo Pilón Viviente (recomendada): colosal mazo de hierro meteórico y bronce con rostro grabado
      y núcleo magnético turquesa; cae con golpes sísmicos sobre el Gran Yunque levantando olas de escoria, y
      cuando queda clavado, Maisha usa el Pulso Magnético en sus anillas laterales para abrir su coraza.
  B · El Herrero de Cuatro Tenazas: autómata de fundición con cuatro brazos que lanza lingotes al rojo vivo.
  C · Los Dos Fuelles del Crisol: pareja de fuelles acorazados que soplan chorros de fuego cruzados.
Sale en documentacion/boceto_nyundo.png (600×256)."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from pintor import Lienzo, rampa  # noqa: E402
import cinematicas as ci  # noqa: E402

W, H = 600, 256
FRAGUA = ["#180c0c", "#2c1412", "#461e18", "#682c1e"]
HIERRO = ["#141620", "#242838", "#384056", "#54607c", "#7888a8"]
COBRE = ["#32180c", "#623218", "#9a5228", "#cf7a3e", "#f2ad68"]
LAVA = ["#5a1408", "#a82e10", "#e86418", "#ffae2c", "#fff090"]
MAGNETO = ["#0c2834", "#185468", "#2c92a8", "#64d8ea", "#dcffff"]
SUELO = ["#241818", "#382624", "#503632", "#6a4842"]
LUZ = (-0.6, -0.6, 0.55)


def sala_fragua(lz, x0):
    x1 = x0 + 200
    zona = (lz.x >= x0) * (lz.x < x1)
    # Pared de la Gran Fragua con cascadas de escoria fundida a los lados
    fondo = zona * (lz.y < 148)
    lz.pintar(fondo, rampa(FRAGUA, np.clip(lz.y / 148.0, 0, 1)))
    for dx in (24, 176):
        col_lava = fondo * (np.abs(lz.x - (x0 + dx)) < 6)
        lz.pintar(col_lava, LAVA[3])
        lz.sumar_luz(lz.desenfocar(col_lava, 7), "#e86418", 0.45)
    # Suelo circular de la Gran Fragua rodeado de escoria
    suelo = zona * (lz.y >= 148)
    lz.pintar(suelo, rampa(SUELO, np.clip((lz.y - 148) / 108.0, 0, 1)))
    anillo = suelo * (np.abs(np.hypot(lz.x - (x0 + 100), (lz.y - 192) * 1.6) - 62) < 2.2)
    lz.pintar(anillo, LAVA[2], 0.8)
    lz.sumar_luz(lz.desenfocar(anillo, 4), "#e86418", 0.35)


def idea_martillo(lz, x0):
    cx = x0 + 105
    # El Gran Yunque en la base
    yunque = lz.poligono([(cx - 34, 152), (cx + 34, 152), (cx + 24, 176), (cx - 24, 176)])
    lz.sombrear(yunque, HIERRO[:4], 8, LUZ)
    # Cadena pesada superior
    cadena = lz.poligono([(cx - 5, 16), (cx + 5, 16), (cx + 5, 58), (cx - 5, 58)])
    lz.sombrear(cadena, COBRE[:4], 3, LUZ)
    # Cabeza colosal del Martillo Pilón de hierro meteórico y bronce
    mazo = lz.poligono([
        (cx - 38, 56), (cx + 38, 56),
        (cx + 42, 128), (cx + 28, 144),
        (cx - 28, 144), (cx - 42, 128),
    ])
    lz.sombrear(mazo, HIERRO, 16, LUZ)
    faja = lz.poligono([(cx - 40, 74), (cx + 40, 74), (cx + 40, 86), (cx - 40, 86)])
    lz.sombrear(faja, COBRE, 5, LUZ)
    # Anillas magnéticas laterales (para tirar con el Pulso Magnético)
    for dx in (-44, 44):
        aro = lz.elipse(cx + dx, 98, 8, 12) - lz.elipse(cx + dx, 98, 4, 7)
        aro = np.clip(aro, 0, 1)
        lz.sombrear(aro, MAGNETO[1:], 3, LUZ)
        lz.sumar_luz(lz.desenfocar(aro, 4), "#64d8ea", 0.6)
    # Núcleo magnético turquesa y ojos de brasa en el frente del mazo
    nucleo = lz.elipse(cx, 110, 11, 13)
    lz.sombrear(nucleo, MAGNETO[1:], 5, LUZ)
    lz.sumar_luz(lz.desenfocar(nucleo, 6), "#64d8ea", 0.75)
    for ox in (-14, 14):
        ojo = lz.elipse(cx + ox, 82, 3.2, 2.2)
        lz.sumar_luz(lz.desenfocar(ojo, 3), "#ffae2c", 0.8)
        lz.pintar(ojo, "#fff090")


def idea_herrero(lz, x0):
    cx, cy = x0 + 105, 116
    lz.pintar(lz.elipse(cx, 176, 38, 9), "#0a080c", 0.55)
    # Torso de caldera de bronce y cabeza con visera de forja
    torso = lz.elipse(cx, cy, 28, 34)
    lz.sombrear(torso, COBRE, 14, LUZ)
    cabeza = lz.poligono([(cx - 14, 66), (cx + 14, 66), (cx + 16, 86), (cx - 16, 86)])
    lz.sombrear(cabeza, HIERRO, 6, LUZ)
    rejilla = lz.poligono([(cx - 10, 74), (cx + 10, 74), (cx + 10, 80), (cx - 10, 80)])
    lz.pintar(rejilla, LAVA[3])
    # Cuatro brazos con tenazas magnéticas
    for (dx, dy) in ((-38, -14), (-42, 16), (38, -14), (42, 16)):
        brazo = lz.trazo([(cx + dx * 0.5, cy + dy * 0.4), (cx + dx, cy + dy)], 4.5)
        lz.sombrear(brazo, HIERRO, 3, LUZ)
        pinza = lz.elipse(cx + dx, cy + dy, 6, 6)
        lz.sombrear(pinza, MAGNETO[1:], 3, LUZ)


def idea_fuelles(lz, x0):
    cx = x0 + 105
    # Dos grandes fuelles acorazados a izquierda y derecha de un crisol central
    crisol = lz.elipse(cx, 134, 18, 22)
    lz.sombrear(crisol, LAVA[1:], 8, LUZ)
    lz.sumar_luz(lz.desenfocar(crisol, 8), "#e86418", 0.65)
    for lado in (-1, 1):
        bx = cx + lado * 42
        fuelle = lz.poligono([
            (bx - lado * 20, 78),
            (bx + lado * 16, 66),
            (bx + lado * 18, 162),
            (bx - lado * 22, 148),
        ])
        lz.sombrear(fuelle, HIERRO, 10, LUZ)
        boquilla = lz.elipse(bx - lado * 20, 118, 6, 8)
        lz.sombrear(boquilla, COBRE, 3, LUZ)


def main():
    lz = Lienzo(W, H, semilla=760)
    for i, fn in enumerate((idea_martillo, idea_herrero, idea_fuelles)):
        x0 = i * 200
        sala_fragua(lz, x0)
        fn(lz, x0)
        ci.maisha_luz(lz, x0 + 26, 220, e=1.0)
    for x in (199, 200, 399, 400):
        lz.pintar((np.abs(lz.x - x) < 0.8) * 1.0, LAVA[3])

    salida = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "documentacion",
        "boceto_nyundo.png",
    )
    lz.guardar(salida)
    im = Image.open(salida).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 10)
    except OSError:
        f = ImageFont.load_default()
    titulos = [
        "A · El Martillo Pilón Viviente",
        "B · El Herrero de 4 Tenazas",
        "C · Los Dos Fuelles del Crisol",
    ]
    for i, t in enumerate(titulos):
        d.rectangle((i * 200 + 4, 236, i * 200 + 196, 252), fill=(16, 10, 10))
        d.text((i * 200 + 10, 238), t, font=f, fill=(255, 222, 140))
    im.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
