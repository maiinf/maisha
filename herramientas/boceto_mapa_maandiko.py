"""Boceto del mapa de MAANDIKO, la Ciudad-Archivo de Sigilia (el pueblo del mundo 2), para decidir con Iam antes de
construirla. Es un plano de diseño, no el mapa del juego.
Sale en documentacion/boceto_mapa_maandiko.png (1000×700)."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 700
X0, Y0, X1, Y1 = 20, 40, 980, 520           # el plano
FONDO = (24, 22, 30)
CREMA = (245, 232, 200)
NIEVE = (214, 208, 232)
CALLE = (150, 140, 176)
PIEDRA = (92, 70, 120)
TEJADO = (226, 186, 90)
TINTA = (30, 22, 50)


def fuentes():
    try:
        return (ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 14),
                ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana.ttf", 13),
                ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 15))
    except OSError:
        f = ImageFont.load_default()
        return f, f, f


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    fb, fp, ft = fuentes()
    # la nieve de toda la ciudad, con la muralla alrededor
    d.rectangle([X0, Y0, X1, Y1], fill=NIEVE)
    for x in range(X0, X1, 6):
        for y in range(Y0, Y1, 6):
            if (x * 7 + y * 13) % 37 == 0:
                d.point((x, y), fill=(236, 232, 248))
    d.rectangle([X0 + 8, Y0 + 8, X1 - 8, Y1 - 8], outline=PIEDRA, width=8)
    # el canal de tinta helada: entra por el este y cruza hasta la plaza
    pts = [(X1 - 8, 300), (860, 310), (780, 290), (700, 320), (620, 330), (560, 320)]
    d.line(pts, fill=TINTA, width=26, joint="curve")
    d.line(pts, fill=(110, 90, 170), width=2, joint="curve")
    for (x, y) in ((820, 305), (660, 322)):
        d.rectangle([x - 14, y - 18, x + 14, y + 18], fill=CALLE, outline=PIEDRA)   # puentes
    # las calles: la avenida del sur a la plaza, y de la plaza a cada barrio y a cada salida
    calles = [[(500, Y1 - 8), (500, 360)],                       # avenida de la Puerta Sellada
              [(500, 300), (500, 170)],                          # al Gran Archivo
              [(440, 300), (300, 300), (160, 260), (X0 + 8, 250)],  # oeste: copistas y Estanterías
              [(560, 300), (700, 270), (820, 250), (900, 262), (X1 - 8, 268)],   # este: mercado y salida al canal
              [(500, 170), (380, 120), (300, Y0 + 8)],           # noroeste: subida al Observatorio
              [(300, 300), (300, 420), (380, 460)]]              # callejón (tapado de Tinta Quieta)
    for c in calles:
        d.line(c, fill=CALLE, width=22, joint="curve")
    # la Plaza del Índice: redonda, con la fuente de tinta helada en medio
    d.ellipse([400, 230, 600, 370], fill=CALLE, outline=PIEDRA, width=3)
    d.ellipse([472, 278, 528, 322], fill=TINTA, outline=TEJADO, width=3)
    # el Gran Archivo: cúpula dorada al norte
    d.rectangle([420, 70, 580, 170], fill=PIEDRA, outline=(40, 30, 56), width=2)
    d.pieslice([430, 30, 570, 130], 180, 360, fill=TEJADO, outline=(90, 60, 20))
    d.rectangle([488, 140, 512, 170], fill=(250, 200, 110))
    # casas de escribas (oeste) y la de Kalamu, más grande
    for (x, y) in ((120, 200), (190, 190), (120, 320), (200, 340), (250, 220), (90, 420), (170, 450)):
        d.rectangle([x - 22, y - 16, x + 22, y + 16], fill=PIEDRA, outline=(40, 30, 56))
        d.polygon([(x - 26, y - 16), (x, y - 34), (x + 26, y - 16)], fill=TEJADO, outline=(90, 60, 20))
    d.rectangle([310, 160, 370, 210], fill=PIEDRA, outline=(40, 30, 56), width=2)
    d.polygon([(304, 160), (340, 130), (376, 160)], fill=TEJADO, outline=(90, 60, 20))
    # el mercado de tinta (este): puestos con toldo
    for (x, y) in ((680, 220), (730, 210), (780, 220), (700, 380), (760, 390), (820, 370)):
        d.rectangle([x - 16, y - 10, x + 16, y + 10], fill=(140, 100, 70), outline=(60, 40, 30))
        d.rectangle([x - 18, y - 16, x + 18, y - 9], fill=(170, 80, 140))
    # el taller de Taa (faroles), junto a la avenida
    d.rectangle([560, 410, 620, 460], fill=PIEDRA, outline=(40, 30, 56), width=2)
    d.polygon([(554, 410), (590, 384), (626, 410)], fill=TEJADO, outline=(90, 60, 20))
    # faroles por las calles, Tinta Quieta que tapa calles (manchas negras) y escribas en blanco
    for (x, y) in ((500, 470), (500, 400), (430, 300), (570, 300), (300, 260), (700, 270), (420, 140), (580, 140)):
        d.rectangle([x - 2, y - 8, x + 2, y + 4], fill=(70, 60, 90)); d.rectangle([x - 3, y - 12, x + 3, y - 7], fill=(250, 210, 110))
    for (x, y) in ((330, 400), (650, 160), (860, 450), (230, 120)):
        d.ellipse([x - 22, y - 14, x + 22, y + 14], fill=TINTA, outline=(150, 90, 220), width=2)
    for (x, y) in ((450, 260), (560, 350), (160, 260), (740, 300), (300, 330), (500, 200), (820, 230), (380, 470), (640, 470),
                   (110, 380), (900, 330), (250, 180)):
        d.ellipse([x - 5, y - 7, x + 5, y + 7], fill=(236, 234, 244), outline=(140, 136, 160))
    # Mauti, en la plaza, junto a la fuente
    d.ellipse([530, 248, 544, 264], fill=(200, 190, 240), outline=(120, 100, 180), width=2)
    # salidas
    for (x, y, t) in ((500, Y1 - 4, "sur: Paso de la Escarcha (Puerta Sellada)"), (X0 + 4, 250, "oeste: Estanterías"),
                      (X1 - 4, 300, "este: Canal de Tinta"), (300, Y0 + 4, "norte: Observatorio")):
        tw = d.textlength(t, font=fb)
        tx = min(max(x - tw / 2, X0 + 4), X1 - tw - 4)
        ty = y - 22 if y > Y0 + 20 else y + 6
        d.rectangle([tx - 4, ty - 2, tx + tw + 4, ty + 17], fill=(30, 26, 40))
        d.text((tx, ty), t, font=fb, fill=CREMA)
    # rótulos
    for (x, y, t) in ((500, 382, "Plaza del Índice"), (500, 180, "Gran Archivo"), (340, 216, "Casa de Kalamu"),
                      (160, 485, "Barrio de los Copistas"), (750, 410, "Mercado de Tinta"), (590, 468, "Taller de Taa")):
        tw = d.textlength(t, font=fb)
        d.text((x - tw / 2, y), t, font=fb, fill=(30, 24, 44), stroke_width=2, stroke_fill=(236, 232, 248))
    d.text((20, 10), "MAANDIKO, la Ciudad-Archivo — boceto del plano (propuesta)", font=ft, fill=(240, 220, 140))
    # leyenda
    ley = [(TEJADO, "Gran Archivo (debajo: la Sección Prohibida)"), (PIEDRA, "Casas de escribas"), ((170, 80, 140), "Puestos del mercado"),
           (TINTA, "Tinta Quieta: tapa calles (se derrite con fuego)"), ((236, 234, 244), "Escriba en blanco (12: sus fichas)"),
           ((200, 190, 240), "Mauti, ayudando en la plaza"), ((250, 210, 110), "Farol rúnico (se encienden con fuego)"), (CALLE, "Calles y plaza")]
    for i, (col, txt) in enumerate(ley):
        x, y = 30 + (i // 4) * 480, 540 + (i % 4) * 36
        d.rectangle([x, y, x + 18, y + 18], fill=col, outline=(90, 90, 100))
        d.text((x + 28, y + 1), txt, font=fp, fill=CREMA)
    salida = os.path.join(RAIZ, "documentacion", "boceto_mapa_maandiko.png")
    img.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
