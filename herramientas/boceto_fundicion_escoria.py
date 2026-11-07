"""Boceto del mapa de LA FUNDICIÓN DE ESCORIA (camino del este de Asterhaul), para decidir con Iam
antes de que Claude la construya. Es un plano de diseño con los canales de escoria fundida, el maestro
gruista Moto, la Estela del Pulso Magnético, los puentes-grúa de hierro meteórico y la Gran Fragua (Nyundo).
Sale en documentacion/boceto_fundicion_escoria.png (1000×700)."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 700
X0, Y0, X1, Y1 = 20, 44, 980, 524
FONDO = (22, 20, 18)
CREMA = (245, 232, 200)
ROCA = (54, 38, 36)
LOSA = (114, 88, 82)
LAVA_BORDE = (176, 62, 24)
LAVA = (242, 128, 32)
LAVA_LUZ = (255, 214, 92)
HIERRO = (74, 82, 102)
MAGNETO = (96, 224, 236)
AMBAR = (255, 198, 68)


def fuentes():
    try:
        return (
            ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 13),
            ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana.ttf", 13),
            ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 15),
        )
    except OSError:
        f = ImageFont.load_default()
        return f, f, f


def flecha_doble(d, x0, y0, x1, y1, col):
    d.line([(x0, y0), (x1, y1)], fill=col, width=2)
    ang = math.atan2(y1 - y0, x1 - x0)
    for da in (-2.5, 2.5):
        d.line([(x1, y1), (x1 + 6 * math.cos(ang + da), y1 + 6 * math.sin(ang + da))], fill=col, width=2)
        d.line([(x0, y0), (x0 - 6 * math.cos(ang + da), y0 - 6 * math.sin(ang + da))], fill=col, width=2)


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    fb, fp, ft = fuentes()

    # Fondo de roca basáltica y canales de escoria fundida
    d.rectangle([X0, Y0, X1, Y1], fill=ROCA)
    # Gran foso de escoria fundida en el centro-este
    d.rounded_rectangle([180, 66, 955, 502], radius=28, fill=LAVA_BORDE, outline=(36, 22, 20), width=4)
    d.rounded_rectangle([196, 82, 939, 486], radius=22, fill=LAVA)
    for y in range(96, 476, 24):
        d.line([(210, y), (925, y)], fill=LAVA_LUZ, width=1)

    # Plataformas de sillería de basalto sobre la escoria fundida:
    # 1. Muelle Oeste (entrada desde Mji-Jiwe y Caseta de Moto)
    d.rounded_rectangle([38, 205, 345, 365], radius=16, fill=LOSA, outline=(42, 32, 34), width=4)
    # 2. Isla del Crisol Norte (Esquirla de Moto, alcanzada por vagoneta/pasarela sísmica)
    d.rounded_rectangle([240, 78, 485, 168], radius=16, fill=LOSA, outline=(42, 32, 34), width=4)
    # 3. Plataforma Central de los Imanes
    d.rounded_rectangle([435, 215, 650, 355], radius=16, fill=LOSA, outline=(42, 32, 34), width=4)
    # 4. Nave de las Grúas del Sur (2.ª Esquirla, puzle de atraer + repeler grúas)
    d.rounded_rectangle([365, 405, 685, 492], radius=16, fill=LOSA, outline=(42, 32, 34), width=4)
    # 5. La Gran Fragua del Este (arena circular del jefe Nyundo, el Gran Martillo)
    d.ellipse([705, 150, 948, 418], fill=LOSA, outline=(42, 32, 34), width=5)
    d.ellipse([732, 177, 921, 391], fill=(88, 68, 66), outline=AMBAR, width=2)

    # Puentes-grúa y bloques de hierro meteórico (se atraen o repelen con el Pulso Magnético)
    puentes_mag = [
        (385, 285, 36, 22, True),     # puente entre Muelle Oeste y Plataforma Central
        (540, 380, 32, 18, False),    # puente hacia la Nave de las Grúas del Sur
        (676, 285, 32, 22, True),     # puente hacia la Gran Fragua
        (315, 186, 28, 16, False),    # bloque entre Muelle Oeste y Crisol Norte
    ]
    for (bx, by, bw, bh, horiz) in puentes_mag:
        d.rectangle([bx - bw, by - bh, bx + bw, by + bh], fill=HIERRO, outline=MAGNETO, width=2)
        if horiz:
            flecha_doble(d, bx - bw - 14, by, bx + bw + 14, by, MAGNETO)
        else:
            flecha_doble(d, bx, by - bh - 12, bx, by + bh + 12, MAGNETO)

    # Bloques-imán pesados que tapan chorros de fuego o sirven de contrapeso
    for (ix, iy) in ((485, 285), (595, 285), (520, 448)):
        d.rectangle([ix - 12, iy - 12, ix + 12, iy + 12], fill=(48, 56, 74), outline=MAGNETO, width=2)
        d.ellipse([ix - 4, iy - 4, ix + 4, iy + 4], fill=MAGNETO)

    # Caseta de la Grúa (taller de Moto) y Estela del Pulso Magnético
    d.rectangle([165, 222, 232, 266], fill=(84, 62, 58), outline=(34, 24, 22), width=2)
    # Moto (maestro gruista en gris)
    d.ellipse([242, 246, 258, 262], fill=(192, 188, 198), outline=(68, 62, 74), width=2)
    # Estela del Pulso Magnético (brillo turquesa)
    d.polygon([(285, 238), (297, 214), (309, 238), (309, 264), (285, 264)], fill=MAGNETO, outline=(36, 98, 114), width=2)

    # Enemigos: Kovu de Escoria (Salamandras de Hierro Fundido en la lava)
    for (ex, ey) in ((395, 225), (610, 180), (440, 380), (645, 385)):
        d.ellipse([ex - 11, ey - 7, ex + 11, ey + 7], fill=(168, 52, 28), outline=MAGNETO, width=2)

    # Las 3 Esquirlas de Estrella (Crisol Norte, Nave de las Grúas y Gran Fragua)
    for (fx, fy) in ((445, 122), (650, 448), (912, 284)):
        d.polygon(
            [(fx, fy - 9), (fx + 7, fy - 4), (fx + 7, fy + 4), (fx, fy + 9), (fx - 7, fy + 4), (fx - 7, fy - 4)],
            fill=AMBAR,
            outline=(70, 42, 14),
            width=2,
        )

    # Jefe: Nyundo, el Gran Martillo en el centro de la Gran Fragua + Cadena Este
    jx, jy = 826, 284
    d.polygon([(jx, jy - 22), (jx + 18, jy), (jx, jy + 22), (jx - 18, jy)], fill=(196, 108, 28), outline=(255, 232, 180), width=2)
    d.line([(925, 284), (968, 284)], fill=(150, 142, 164), width=5)

    # Rótulos
    rotulos = [
        (105, 336, "<< Oeste: desde Mji-Jiwe"),
        (215, 280, "1. Caseta de Moto + Estela Magnética"),
        (365, 92, "2. Crisol Norte (Esquirla de Moto)"),
        (542, 240, "3. Plataforma de los Imanes"),
        (525, 470, "4. Nave de las Grúas (2.ª Esquirla)"),
        (826, 134, "5. La Gran Fragua del Este"),
        (826, 316, "JEFE: NYUNDO, EL GRAN MARTILLO"),
    ]
    for (rx, ry, txt) in rotulos:
        tw = d.textlength(txt, font=fb)
        tx = min(max(rx - tw / 2, X0 + 6), X1 - tw - 6)
        d.rectangle([tx - 5, ry - 2, tx + tw + 5, ry + 17], fill=(24, 20, 18))
        d.text((tx, ry), txt, font=fb, fill=CREMA)

    d.text(
        (20, 12),
        "LA FUNDICIÓN DE ESCORIA — boceto del trazado y mecánicas (propuesta para decidir con Iam)",
        font=ft,
        fill=AMBAR,
    )

    # Leyenda inferior
    ley = [
        (MAGNETO, "Estela del Pulso Magnético (atrae o repele el hierro meteórico)"),
        (HIERRO, "Puente-grúa o barcaza de hierro (se acerca o aleja con el Pulso)"),
        ((48, 56, 74), "Bloque-imán pesado (sirve de escudo o abre compuertas)"),
        ((192, 188, 198), "Moto, maestro gruista en gris (enseña el Pulso Magnético)"),
        ((168, 52, 28), "Kovu de Escoria (salamandra: el Pulso la saca de la lava)"),
        (LAVA, "Río de escoria fundida (quema si se pisa sin puente de hierro)"),
        (AMBAR, "Esquirlas de Estrella (3: Moto + Nave Sur + Gran Fragua)"),
        ((196, 108, 28), "Nyundo, el Gran Martillo (jefe que custodia la Cadena Este)"),
    ]
    for i, (col, txt) in enumerate(ley):
        x, y = 28 + (i // 4) * 485, 540 + (i % 4) * 36
        d.rectangle([x, y, x + 18, y + 18], fill=col, outline=(120, 105, 90))
        d.text((x + 26, y + 1), txt, font=fp, fill=CREMA)

    salida = os.path.join(RAIZ, "documentacion", "boceto_fundicion_escoria.png")
    img.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
