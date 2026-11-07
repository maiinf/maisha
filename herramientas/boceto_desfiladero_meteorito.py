"""Boceto del mapa de EL DESFILADERO DEL METEORITO (entrada a Asterhaul), para decidir con Iam
antes de que Claude lo construya. Es un plano de diseño con el recorrido de oeste a noreste,
el derrumbe donde está atrapada Mauti, el taller de Mwamba, las vías de vagonetas y la Puerta del Cráter.
Sale en documentacion/boceto_desfiladero_meteorito.png (1000×700)."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 700
X0, Y0, X1, Y1 = 20, 44, 980, 524
FONDO = (22, 20, 18)
CREMA = (245, 232, 200)
TIERRA = (118, 86, 68)
ROCA = (68, 56, 64)
TERRAZA = (146, 108, 82)
AMBAR = (255, 198, 68)
CARGA = (242, 132, 42)
RAIL = (188, 174, 156)
GRIETA = (232, 114, 38)


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


def flecha(d, x0, y0, x1, y1, col):
    d.line([(x0, y0), (x1, y1)], fill=col, width=3)
    ang = math.atan2(y1 - y0, x1 - x0)
    for da in (-2.5, 2.5):
        d.line([(x1, y1), (x1 + 8 * math.cos(ang + da), y1 + 8 * math.sin(ang + da))], fill=col, width=3)


def dibujar_via(d, pts):
    for (a, b) in zip(pts, pts[1:]):
        d.line([a, b], fill=(92, 72, 58), width=8)
        d.line([a, b], fill=RAIL, width=4)
        dist = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(dist / 14))
        for k in range(n + 1):
            t = k / n
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            d.rectangle([x - 4, y - 4, x + 4, y + 4], fill=(110, 82, 56))


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    fb, fp, ft = fuentes()

    # Pared de roca basáltica del cañón
    d.rectangle([X0, Y0, X1, Y1], fill=ROCA)
    for x in range(X0, X1, 9):
        for y in range(Y0, Y1, 9):
            if (x * 13 + y * 19) % 37 == 0:
                d.point((x, y), fill=(96, 82, 92))

    # El cauce del Desfiladero (sube de suroeste a noreste con una cantera lateral al sureste)
    # 1. Entrada oeste (Garganta de Basalto)
    d.rounded_rectangle([X0 + 10, 310, 360, 465], radius=22, fill=TIERRA, outline=(42, 34, 38), width=4)
    # 2. Explanada central y Taller de Mwamba
    d.rounded_rectangle([290, 175, 650, 360], radius=24, fill=TERRAZA, outline=(42, 34, 38), width=4)
    # 3. Cantera Hundida del Este (donde cayó la Esquirla de Mwamba)
    d.rounded_rectangle([580, 320, 930, 490], radius=22, fill=TIERRA, outline=(42, 34, 38), width=4)
    # 4. Rampa Norte hacia la Puerta del Cráter (salida a Mji-Jiwe)
    d.rounded_rectangle([540, 62, 920, 225], radius=24, fill=TERRAZA, outline=(42, 34, 38), width=4)

    # Vías de vagonetas que cruzan el desfiladero
    dibujar_via(d, [(70, 395), (325, 395), (325, 275), (595, 275)])
    dibujar_via(d, [(595, 275), (745, 275), (745, 145), (885, 145)])
    dibujar_via(d, [(595, 275), (650, 410), (860, 410)])

    # Vagonetas de hierro cargadas de ámbar (se empujan con Carga Sísmica)
    for (vx, vy) in ((170, 395), (520, 275), (745, 235)):
        d.rectangle([vx - 13, vy - 10, vx + 13, vy + 10], fill=(54, 50, 64), outline=AMBAR, width=2)
        d.ellipse([vx - 7, vy - 6, vx + 7, vy + 6], fill=AMBAR)

    # Derrumbe donde Mauti quedó atrapada (al norte del tramo 1 / oeste del tramo 2)
    rx, ry = 325, 225
    for dx, dy in ((-16, -6), (0, -10), (16, -4), (-10, 8), (10, 8)):
        d.ellipse([rx + dx - 12, ry + dy - 10, rx + dx + 12, ry + dy + 10], fill=(92, 74, 72), outline=GRIETA, width=2)
    # Mauti tras el derrumbe
    d.ellipse([rx - 8, ry - 32, rx + 8, ry - 16], fill=(196, 142, 232), outline=(40, 24, 52), width=2)

    # Muros de basalto agrietados (se rompen con Carga Sísmica)
    for (mx, my, horiz) in ((610, 330, True), (555, 185, False), (235, 340, False)):
        if horiz:
            d.rectangle([mx - 28, my - 8, mx + 28, my + 8], fill=(88, 66, 58), outline=GRIETA, width=2)
            d.line([(mx - 18, my - 6), (mx, my + 6), (mx + 16, my - 5)], fill=AMBAR, width=2)
        else:
            d.rectangle([mx - 8, my - 26, mx + 8, my + 26], fill=(88, 66, 58), outline=GRIETA, width=2)
            d.line([(mx - 6, my - 16), (mx + 6, my), (mx - 5, my + 16)], fill=AMBAR, width=2)

    # Taller del cantero Mwamba y Estela de la Carga Sísmica
    d.rectangle([405, 192, 478, 244], fill=(96, 72, 62), outline=(36, 26, 22), width=2)
    d.polygon([(398, 192), (441, 162), (484, 192)], fill=(198, 128, 68), outline=(70, 42, 18))
    # Mwamba (cantero en gris junto a su yunque)
    d.ellipse([488, 214, 504, 230], fill=(186, 182, 190), outline=(70, 64, 74), width=2)
    # Estela de la Carga Sísmica
    d.polygon([(526, 206), (538, 182), (550, 206), (550, 232), (526, 232)], fill=CARGA, outline=AMBAR, width=2)

    # La Puerta del Cráter (arriba a la derecha, cerrada con 3 pilares-diapasón sísmicos)
    d.rectangle([865, 76, 905, 132], fill=(52, 44, 58), outline=AMBAR, width=3)
    for px in (780, 820, 850):
        d.polygon([(px - 7, 108), (px, 86), (px + 7, 108), (px + 5, 122), (px - 5, 122)], fill=(74, 68, 92), outline=AMBAR, width=2)

    # Geodas de ámbar y enemigos: Kaa-Jiwe (Cangrejos de Geoda)
    for (ex, ey) in ((230, 430), (720, 375), (810, 445), (675, 160)):
        d.ellipse([ex - 11, ey - 8, ex + 11, ey + 8], fill=(116, 62, 38), outline=AMBAR, width=2)

    # Esquirlas de Estrella (2 en el desfiladero: la de Mwamba en la cantera y una tras muro agrietado)
    for (fx, fy) in ((885, 410), (140, 335)):
        d.polygon(
            [(fx, fy - 9), (fx + 7, fy - 4), (fx + 7, fy + 4), (fx, fy + 9), (fx - 7, fy + 4), (fx - 7, fy - 4)],
            fill=AMBAR,
            outline=(70, 42, 14),
            width=2,
        )

    # Flechas de flujo del recorrido
    flecha(d, 90, 435, 200, 435, AMBAR)
    flecha(d, 635, 380, 780, 380, AMBAR)
    flecha(d, 610, 145, 720, 145, AMBAR)

    # Rótulos
    rotulos = [
        (115, 472, "<< oeste: desde Kitovu"),
        (325, 140, "2. Derrumbe (Mauti atrapada)"),
        (455, 252, "1. Taller de Mwamba + Estela de Carga"),
        (760, 496, "3. Cantera Hundida (Esquirla de Mwamba)"),
        (735, 68, "4. Puerta del Cráter (3 pilares sísmicos) >> Mji-Jiwe"),
        (155, 305, "Secreto sísmico (2.ª Esquirla)"),
    ]
    for (rx, ry, txt) in rotulos:
        tw = d.textlength(txt, font=fb)
        tx = min(max(rx - tw / 2, X0 + 6), X1 - tw - 6)
        d.rectangle([tx - 5, ry - 2, tx + tw + 5, ry + 17], fill=(24, 20, 18))
        d.text((tx, ry), txt, font=fb, fill=CREMA)

    d.text(
        (20, 12),
        "EL DESFILADERO DEL METEORITO — boceto del trazado y mecánicas (propuesta para Iam)",
        font=ft,
        fill=AMBAR,
    )

    # Leyenda inferior
    ley = [
        (CARGA, "Estela de Carga Sísmica (enseña a embestir roca)"),
        ((88, 66, 58), "Muro o derrumbe agrietado (cede con Carga Sísmica)"),
        ((54, 50, 64), "Vagoneta de ámbar (se impulsa de un golpe sísmico)"),
        ((186, 182, 190), "Mwamba, viejo cantero mudo de polvo gris"),
        ((196, 142, 232), "Mauti (atrapada tras el derrumbe del cañón)"),
        ((116, 62, 38), "Kaa-Jiwe, Cangrejo de Geoda (vulnerable a Carga)"),
        (AMBAR, "Esquirlas de Estrella (2: cantera + muro secreto)"),
        ((74, 68, 92), "Pilares de la Puerta del Cráter (3 golpes sísmicos)"),
    ]
    for i, (col, txt) in enumerate(ley):
        x, y = 28 + (i // 4) * 485, 540 + (i % 4) * 36
        d.rectangle([x, y, x + 18, y + 18], fill=col, outline=(120, 105, 90))
        d.text((x + 26, y + 1), txt, font=fp, fill=CREMA)

    salida = os.path.join(RAIZ, "documentacion", "boceto_desfiladero_meteorito.png")
    img.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
