"""Boceto del mapa de MJI-JIWE, LA CIUDAD DEL CRÁTER (ciudad central de Asterhaul), para decidir
con Iam antes de que Claude la construya. Es un plano de diseño con las 3 terrazas concéntricas,
el Gran Diapasón sobre el Núcleo sellado con 3 cadenas, la Gran Forja de Mhunzi, el Mercado de Chuma
y las salidas hacia las 3 rutas de Asterhaul.
Sale en documentacion/boceto_mji_jiwe.png (1000×700)."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 700
X0, Y0, X1, Y1 = 20, 44, 980, 524
FONDO = (22, 20, 18)
CREMA = (245, 232, 200)
ROCA = (58, 48, 56)
TERRAZA_1 = (122, 88, 68)
TERRAZA_2 = (148, 106, 78)
TERRAZA_3 = (172, 126, 88)
CRATER = (42, 32, 40)
AMBAR = (255, 198, 68)
COBRE = (206, 134, 78)
MAGNETO = (96, 214, 224)


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


def edificio(d, x, y, w, h, col_techo=COBRE):
    d.rectangle([x - w // 2, y - h // 2, x + w // 2, y + h // 2], fill=(78, 68, 86), outline=(32, 26, 36), width=2)
    d.polygon([(x - w // 2 - 4, y - h // 2), (x, y - h // 2 - 14), (x + w // 2 + 4, y - h // 2)], fill=col_techo, outline=(56, 34, 18))


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    fb, fp, ft = fuentes()

    # Roca basáltica exterior
    d.rectangle([X0, Y0, X1, Y1], fill=ROCA)

    #Las 3 terrazas concéntricas del anfiteatro de Mji-Jiwe
    cx, cy = 500, 284
    d.ellipse([90, 62, 910, 506], fill=TERRAZA_1, outline=(42, 34, 38), width=4)
    d.ellipse([190, 118, 810, 450], fill=TERRAZA_2, outline=(64, 48, 42), width=3)
    d.ellipse([295, 172, 705, 396], fill=TERRAZA_3, outline=(82, 60, 48), width=3)

    # El foso central del Núcleo de la Estrella y el puente anular del Gran Diapasón
    d.ellipse([410, 220, 590, 348], fill=CRATER, outline=(28, 20, 28), width=4)
    # 3 grandes Cadenas de Hierro Meteórico que sellan el Núcleo (Oeste, Este, Norte)
    for (ax, ay) in ((320, 284), (680, 284), (500, 172)):
        d.line([(cx, cy), (ax, ay)], fill=(40, 38, 48), width=7)
        d.line([(cx, cy), (ax, ay)], fill=(140, 132, 152), width=3)

    # Plataforma central del Gran Diapasón y los 12 Yunques de Memoria alrededor
    d.ellipse([458, 252, 542, 316], fill=(86, 76, 98), outline=AMBAR, width=3)
    d.polygon([(476, 288), (476, 240), (486, 232), (486, 288)], fill=(54, 50, 68), outline=AMBAR)
    d.polygon([(514, 288), (514, 232), (524, 240), (524, 288)], fill=(54, 50, 68), outline=AMBAR)
    d.ellipse([491, 246, 509, 264], fill=AMBAR, outline=(120, 68, 14), width=2)

    # Los 12 Yunques de Memoria en el anillo de la plaza central (se encienden con las 12 Esquirlas)
    for k in range(12):
        ang = k * math.tau / 12
        yx = cx + math.cos(ang) * 116
        yy = cy + math.sin(ang) * 74
        d.rectangle([yx - 5, yy - 4, yx + 5, yy + 4], fill=(64, 58, 74), outline=AMBAR, width=1)

    # Escaleras / rampas radiales entre terrazas
    for (x0, y0, x1, y1) in (
        (220, 445, 360, 355),   # subida desde el Desfiladero (suroeste)
        (295, 284, 100, 284),   # salida oeste a Las Galerías de Ámbar
        (705, 284, 900, 284),   # salida este a La Fundición de Escoria
        (500, 172, 500, 66),    # salida norte a La Aguja Caída
    ):
        d.line([(x0, y0), (x1, y1)], fill=(208, 178, 136), width=14)
        d.line([(x0, y0), (x1, y1)], fill=(138, 104, 76), width=2)

    # Edificios principales:
    # 1. La Gran Forja de Mhunzi (al norte-centro de la terraza media)
    edificio(d, 385, 165, 68, 42, col_techo=(232, 146, 54))
    # Mhunzi (maestra fundidora con gafas de ámbar)
    d.ellipse([377, 192, 393, 208], fill=AMBAR, outline=(60, 36, 14), width=2)

    # 2. El Mercado de la Escoria (tienda de Chuma, al sur-este de la terraza media)
    edificio(d, 635, 380, 60, 38, col_techo=COBRE)
    d.ellipse([627, 404, 643, 420], fill=(224, 152, 88), outline=(60, 36, 14), width=2)

    # 3. El Taller de Mwamba en la ciudad (al suroeste, donde recompensa por encender los hornos/diapasones)
    edificio(d, 330, 390, 52, 34, col_techo=COBRE)
    d.ellipse([322, 412, 338, 428], fill=(210, 204, 218), outline=(60, 54, 68), width=2)

    # Casas-taller de artesanos en gris (despiertan con las 12 Esquirlas)
    for (ex, ey) in ((230, 195), (245, 355), (755, 195), (765, 355), (620, 165)):
        edificio(d, ex, ey, 44, 30, col_techo=(142, 112, 92))

    # Hornos-diapasón vecinales en las 3 calles (se encienden con Carga Sísmica para dar calor a la ciudad)
    for (hx, hy) in ((280, 240), (355, 330), (645, 235), (710, 330), (445, 140), (555, 140)):
        d.polygon([(hx - 6, hy + 8), (hx, hy - 10), (hx + 6, hy + 8)], fill=(78, 72, 96), outline=AMBAR, width=2)

    # Las 3 cerraduras de las salidas de Mji-Jiwe:
    # Oeste (Galerías de Ámbar): tapada por un Muro de Basalto Agrietado (se abre con Carga Sísmica)
    d.rectangle([92, 258, 114, 310], fill=(92, 68, 58), outline=(242, 132, 42), width=3)
    # Este (Fundición de Escoria): puente de hierro retraído (se abre con Carga Sísmica + cadena magnética)
    d.rectangle([886, 258, 908, 310], fill=(64, 58, 76), outline=(238, 118, 38), width=3)
    # Norte (Aguja Caída): ascensor de peñasco flotante y monolito de resonancia
    d.ellipse([476, 56, 524, 86], fill=(68, 118, 136), outline=MAGNETO, width=3)

    # Esquirlas de Estrella ocultas en Mji-Jiwe (2: una tras horno-muro norte y una en el foso sur)
    for (fx, fy) in ((175, 145), (500, 468)):
        d.polygon(
            [(fx, fy - 9), (fx + 7, fy - 4), (fx + 7, fy + 4), (fx, fy + 9), (fx - 7, fy + 4), (fx - 7, fy - 4)],
            fill=AMBAR,
            outline=(70, 42, 14),
            width=2,
        )

    # Rótulos
    rotulos = [
        (195, 480, "<< suroeste: Desfiladero del Meteorito"),
        (185, 252, "<< Oeste: Las Galerías de Ámbar"),
        (805, 252, "Este: La Fundición de Escoria >>"),
        (500, 92, "^^ Norte: La Aguja Caída"),
        (365, 118, "1. Gran Forja de Mhunzi (Arte de la Tierra)"),
        (500, 322, "2. El Gran Diapasón y el Núcleo (3 cadenas)"),
        (685, 426, "3. Mercado de Chuma (mejoras)"),
        (295, 434, "4. Taller de Mwamba (hornos)"),
    ]
    for (rx, ry, txt) in rotulos:
        tw = d.textlength(txt, font=fb)
        tx = min(max(rx - tw / 2, X0 + 6), X1 - tw - 6)
        d.rectangle([tx - 5, ry - 2, tx + tw + 5, ry + 17], fill=(24, 20, 18))
        d.text((tx, ry), txt, font=fb, fill=CREMA)

    d.text(
        (20, 12),
        "MJI-JIWE, LA CIUDAD DEL CRÁTER — boceto del trazado (76×58 casillas · propuesta para Iam)",
        font=ft,
        fill=AMBAR,
    )

    # Leyenda inferior
    ley = [
        (AMBAR, "Mhunzi, maestra fundidora (Arte de la Tierra + mapa)"),
        ((86, 76, 98), "El Gran Diapasón y los 12 Yunques de Memoria"),
        ((224, 152, 88), "Chuma, mercader herrero (vende mejoras de mineral)"),
        ((78, 72, 96), "Hornos-diapasón de calle (dan 3 Cristales con Mwamba)"),
        ((140, 132, 152), "Las 3 Cadenas del Cráter (sellan el Núcleo central)"),
        ((92, 68, 58), "Salidas a Galerías (O), Fundición (E) y Aguja (N)"),
        ((142, 112, 92), "Talleres de artesanos en gris (12 Esquirlas)"),
        (MAGNETO, "Ascensor magnético hacia La Aguja Caída"),
    ]
    for i, (col, txt) in enumerate(ley):
        x, y = 28 + (i // 4) * 485, 540 + (i % 4) * 36
        d.rectangle([x, y, x + 18, y + 18], fill=col, outline=(120, 105, 90))
        d.text((x + 26, y + 1), txt, font=fp, fill=CREMA)

    salida = os.path.join(RAIZ, "documentacion", "boceto_mji_jiwe.png")
    img.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
