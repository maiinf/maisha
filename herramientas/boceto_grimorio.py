"""Boceto de EL GRIMORIO DE TINTA (jefe final de Sigilia en La Sección Prohibida), para decidir con Iam antes de que
Claude lo construya. Tres propuestas en la Rotonda del Primer Nombre (con los tres pedestales de Fuego, Hielo y Rayo)
y con Maisha al lado:
  A · El Códice Abierto con Manos de Tinta (recomendada): un libro colosal de cuero morado y oro que levita abierto;
      de sus páginas emergen dos grandes manos de tinta y la Pluma del Primer Nombre. Cambia entre páginas de Fuego,
      Hielo y Rayo, y Maisha debe responder con el Sigilo opuesto.
  B · El Archivero Primero (Sombra con Máscara en Blanco): figura esbelta de tinta que surge del libro con tres anillos.
  C · La Torre de Tomos Encadenados: columna giratoria de libros sujetos por cadenas de hierro.
Sale en documentacion/boceto_grimorio.png (600×256)."""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from pintor import Lienzo, rampa  # noqa: E402
import cinematicas as ci  # noqa: E402

W, H = 600, 256
MORADO = ["#0e0818", "#1a102c", "#2c1c46", "#442c68", "#644490", "#8c68b8"]
ORO = ["#3a2408", "#6a4614", "#a07020", "#d4a034", "#f0cc60", "#fff0b0"]
TINTA = ["#040308", "#0c0818", "#1a1230", "#302252", "#523c82"]
PAPEL = ["#88765a", "#b6a282", "#decba8", "#f6ecd6"]
FUEGO = ["#7a1c10", "#c84418", "#f88830", "#ffe088"]
HIELO = ["#245880", "#4898c8", "#88d4f8", "#e8fcff"]
RAYO = ["#685010", "#b89020", "#f8d850", "#ffffc8"]
LUZ = (-0.6, -0.6, 0.55)


def rotonda(lz, x0):
    x1 = x0 + 200
    zona = (lz.x >= x0) * (lz.x < x1)
    # Pared subterránea del Gran Archivo con arcos góticos y velas
    pared = zona * (lz.y < 142)
    lz.pintar(pared, rampa(MORADO[:4], np.clip(lz.y / 142.0, 0, 1)))
    lz.sombrear(zona * (np.abs(lz.y - 142) < 2.5), ORO[:5], 2, LUZ)
    # Suelo circular de mármol morado con los 3 pedestales rúnicos (Fuego, Rayo, Hielo)
    suelo = zona * (lz.y >= 142)
    lz.pintar(suelo, rampa(MORADO[1:5], np.clip((lz.y - 142) / 114.0, 0, 1)))
    anillo = suelo * (np.abs(np.hypot(lz.x - (x0 + 100), (lz.y - 192) * 1.65) - 66) < 2.0)
    lz.pintar(anillo, ORO[3], 0.8)
    for (dx, dy, col_luz) in ((-58, 178, "#ff8838"), (0, 154, "#ffe868"), (58, 178, "#78d4ff")):
        ped = lz.elipse(x0 + 100 + dx, dy, 9, 5)
        lz.sombrear(ped, ORO[:5], 2, LUZ)
        lz.sumar_luz(lz.desenfocar(ped, 6), col_luz, 0.55)


def idea_codice_manos(lz, x0):
    cx = x0 + 104
    lz.pintar(lz.elipse(cx, 184, 44, 10), TINTA[0], 0.65)
    # Tapas de cuero morado y cantoneras de oro del gran Grimorio abierto
    tapa = lz.poligono([(cx - 46, 78), (cx, 92), (cx + 46, 78), (cx + 42, 134), (cx, 144), (cx - 42, 134)])
    lz.sombrear(tapa, MORADO[2:] + [ORO[3]], 8, LUZ)
    # Páginas abiertas de pergamino con runas escritas
    pag = lz.poligono([(cx - 40, 74), (cx, 88), (cx + 40, 74), (cx + 36, 128), (cx, 138), (cx - 36, 128)])
    lz.sombrear(pag, PAPEL, 6, LUZ)
    lz.pintar(lz.trazo([(cx, 88), (cx, 138)], 1.2), MORADO[1])
    # Ojos luminosos de tinta en las dos páginas y la Pluma del Primer Nombre en el lomo
    for dx in (-16, 16):
        ojo = lz.elipse(cx + dx, 102, 4.5, 6.0)
        lz.pintar(ojo, TINTA[0])
        pup = lz.elipse(cx + dx, 102, 2.2, 3.0)
        lz.sumar_luz(lz.desenfocar(pup, 4), "#c898ff", 0.85)
        lz.pintar(pup, "#f4e8ff")
    pluma = lz.poligono([(cx, 36), (cx + 10, 62), (cx, 88), (cx - 10, 62)])
    lz.sombrear(pluma, ORO[1:], 4, LUZ)
    # Dos grandes manos de tinta con garras de plumilla dorada a los lados
    for lado in (-1, 1):
        brazo = lz.trazo([(cx + lado * 28, 112), (cx + lado * 56, 96), (cx + lado * 64, 122)], 6.0, 4.0)
        lz.sombrear(brazo, TINTA[1:], 4, LUZ)
        for g in (-6, 0, 6):
            garra = lz.poligono([(cx + lado * 64 + g - 2, 122), (cx + lado * 64 + g + 2, 122),
                                 (cx + lado * 64 + g, 132)])
            lz.sombrear(garra, ORO[1:], 2, LUZ)


def idea_archivero(lz, x0):
    cx = x0 + 104
    lz.pintar(lz.elipse(cx, 184, 36, 9), TINTA[0], 0.6)
    # Libro abierto en el suelo como pedestal
    base = lz.poligono([(cx - 34, 162), (cx, 154), (cx + 34, 162), (cx, 174)])
    lz.sombrear(base, PAPEL, 4, LUZ)
    # Cuerpo alto de tinta que emerge del libro
    toga = lz.poligono([(cx - 12, 162), (cx - 24, 96), (cx - 14, 62),
                        (cx + 14, 62), (cx + 24, 96), (cx + 12, 162)])
    lz.sombrear(toga, TINTA, 10, LUZ)
    # Máscara de pergamino en blanco con tres ojos rúnicos (Fuego, Hielo, Rayo)
    mascara = lz.elipse(cx, 56, 14, 17)
    lz.sombrear(mascara, PAPEL[1:], 5, LUZ)
    for (dx, dy, col) in ((-5, 58, "#ff7830"), (5, 58, "#70d0ff"), (0, 49, "#ffe860")):
        lz.pintar(lz.elipse(cx + dx, dy, 2.0, 2.6), col)
    # Tres orbes elementales orbitando
    for (ox, oy, rmp) in ((-44, 92, FUEGO), (0, 32, RAYO), (44, 92, HIELO)):
        lz.sombrear(lz.elipse(cx + ox, oy, 8, 8), rmp, 3, LUZ)


def idea_torre_tomos(lz, x0):
    cx = x0 + 104
    lz.pintar(lz.elipse(cx, 184, 42, 10), TINTA[0], 0.65)
    # Pila giratoria de 5 grandes tomos encadenados
    for k in range(5):
        yk = 152 - k * 22
        dx = int(np.sin(k * 1.3) * 6)
        tomo = lz.poligono([(cx - 32 + dx, yk), (cx - 32 + dx, yk - 18),
                            (cx + 32 + dx, yk - 18), (cx + 32 + dx, yk)])
        col = [MORADO[3], "#5a2438", "#243a5a", "#3a5228", MORADO[4]][k]
        lz.sombrear(tomo, ["#120a18", col, ORO[3]], 4, LUZ)
        lz.pintar(tomo * (np.abs(lz.y - (yk - 9)) < 2), PAPEL[2], 0.85)
    # Ojo central en el tomo del medio y cadenas doradas cruzadas
    lz.pintar(lz.elipse(cx, 98, 12, 8), TINTA[0])
    lz.pintar(lz.elipse(cx, 98, 4, 5), "#f0d8ff")
    cad1 = lz.trazo([(cx - 34, 62), (cx + 34, 148)], 2.2)
    cad2 = lz.trazo([(cx + 34, 62), (cx - 34, 148)], 2.2)
    lz.sombrear(np.maximum(cad1, cad2), ORO, 2, LUZ)


def main():
    lz = Lienzo(W, H, semilla=730)
    for i, fn in enumerate((idea_codice_manos, idea_archivero, idea_torre_tomos)):
        x0 = i * 200
        rotonda(lz, x0)
        fn(lz, x0)
        ci.maisha_luz(lz, x0 + 28, 220, e=1.0)
    for x in (199, 200, 399, 400):
        lz.pintar((np.abs(lz.x - x) < 0.8) * 1.0, ORO[3])

    salida = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "documentacion", "boceto_grimorio.png")
    lz.guardar(salida)
    im = Image.open(salida).convert("RGB")
    d = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 10)
    except OSError:
        f = ImageFont.load_default()
    titulos = [
        "A · El Códice con Manos de Tinta",
        "B · El Archivero sin Rostro",
        "C · La Torre de Tomos",
    ]
    for i, t in enumerate(titulos):
        d.rectangle((i * 200 + 4, 236, i * 200 + 196, 252), fill=(10, 6, 18))
        d.text((i * 200 + 8, 238), t, font=f, fill=(248, 226, 160))
    im.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
