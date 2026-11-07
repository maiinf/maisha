"""Boceto del mapa de LAS GALERÍAS DE ÁMBAR (camino del oeste de Asterhaul), para decidir con Iam
antes de que Claude lo construya. Es un plano de diseño con la red de raíles, los cambios de agujas,
las vagonetas de ámbar, la talladora Kito, la Bóveda de las Geodas y la Cámara del Ancla Oeste (Kifaru).
Sale en documentacion/boceto_galerias_ambar.png (1000×700)."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 700
X0, Y0, X1, Y1 = 20, 44, 980, 524
FONDO = (22, 20, 18)
CREMA = (245, 232, 200)
ROCA = (52, 42, 48)
GALERIA = (128, 92, 64)
VETA = (156, 112, 72)
AMBAR = (255, 198, 68)
CARGA = (242, 132, 42)
RAIL = (192, 178, 160)
AGUJA = (108, 224, 236)


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


def dibujar_via(d, pts):
    for (a, b) in zip(pts, pts[1:]):
        d.line([a, b], fill=(86, 66, 52), width=8)
        d.line([a, b], fill=RAIL, width=4)
        dist = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(dist / 14))
        for k in range(n + 1):
            t = k / n
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            d.rectangle([x - 4, y - 4, x + 4, y + 4], fill=(106, 78, 54))


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    fb, fp, ft = fuentes()

    # Roca madre oscura de las minas de ámbar
    d.rectangle([X0, Y0, X1, Y1], fill=ROCA)
    for x in range(X0, X1, 8):
        for y in range(Y0, Y1, 8):
            if (x * 17 + y * 13) % 43 == 0:
                d.point((x, y), fill=(210, 158, 64))

    # Las 4 cámaras de Las Galerías de Ámbar (de este a oeste, ya que sale por el oeste de Mji-Jiwe)
    # 1. Entrada Este (desde Mji-Jiwe) y Taller de Kito + Estación de Agujas
    d.rounded_rectangle([540, 210, 955, 355], radius=22, fill=GALERIA, outline=(36, 28, 32), width=4)
    # 2. Veta Norte (Esquirla de Kito, tras barrera de roca que rompe la vagoneta desviada)
    d.rounded_rectangle([560, 64, 860, 195], radius=22, fill=VETA, outline=(36, 28, 32), width=4)
    # 3. Bóveda de las Geodas (sur: oscuridad que se ilumina encendiendo geodas con Carga Sísmica; 2.ª Esquirla)
    d.rounded_rectangle([370, 368, 760, 504], radius=22, fill=(92, 68, 54), outline=(36, 28, 32), width=4)
    # 4. El Cruce Mayor (centro-oeste) y la Cámara del Ancla Oeste (arena de Kifaru de Basalto)
    d.rounded_rectangle([280, 175, 555, 355], radius=22, fill=GALERIA, outline=(36, 28, 32), width=4)
    d.ellipse([44, 145, 296, 415], fill=VETA, outline=(36, 28, 32), width=5)
    d.ellipse([66, 167, 274, 393], fill=GALERIA, outline=AMBAR, width=2)

    # Red de raíles de vagonetas y cambios de agujas
    dibujar_via(d, [(920, 285), (710, 285), (420, 285), (275, 285)])
    dibujar_via(d, [(710, 285), (710, 135), (610, 135)])
    dibujar_via(d, [(420, 285), (420, 435), (695, 435)])
    dibujar_via(d, [(420, 285), (420, 205), (320, 205)])

    # Palancas de Cambio de Agujas (giran el desvío al golpearlas o con Carga Sísmica)
    for (ax, ay) in ((710, 285), (420, 285)):
        d.ellipse([ax - 11, ay - 11, ax + 11, ay + 11], fill=(48, 44, 58), outline=AGUJA, width=3)
        d.line([(ax, ay), (ax + 9, ay - 9)], fill=AGUJA, width=2)

    # Vagonetas de ámbar (para empujar con Carga Sísmica)
    for (vx, vy) in ((835, 285), (495, 285), (245, 215), (245, 345)):
        d.rectangle([vx - 12, vy - 9, vx + 12, vy + 9], fill=(54, 50, 64), outline=AMBAR, width=2)
        d.ellipse([vx - 6, vy - 5, vx + 6, vy + 5], fill=AMBAR)

    # Muros de basalto agrietados en los extremos de vía
    for (mx, my, horiz) in ((710, 198, True), (555, 365, True), (288, 285, False)):
        if horiz:
            d.rectangle([mx - 26, my - 7, mx + 26, my + 7], fill=(88, 66, 58), outline=CARGA, width=2)
        else:
            d.rectangle([mx - 7, my - 26, mx + 7, my + 26], fill=(88, 66, 58), outline=CARGA, width=2)

    # Kito, la talladora de ámbar (en gris junto al primer cambio de agujas)
    d.rectangle([755, 218, 815, 256], fill=(92, 68, 58), outline=(36, 26, 22), width=2)
    d.ellipse([742, 244, 758, 260], fill=(192, 188, 198), outline=(70, 64, 76), width=2)

    # Geodas resonantes de luz en la Bóveda Sur y en las galerías
    for (gx, gy) in ((615, 240), (465, 405), (575, 465), (670, 405), (345, 245)):
        d.polygon([(gx, gy - 11), (gx + 8, gy), (gx, gy + 11), (gx - 8, gy)], fill=AMBAR, outline=(255, 245, 190), width=1)

    # Enemigos: Mchimbaji (Escarabajos Barrenadores de Ámbar) y Kaa-Jiwe
    for (ex, ey) in ((650, 135), (380, 285), (520, 435), (360, 325)):
        d.ellipse([ex - 10, ey - 8, ex + 10, ey + 8], fill=(142, 74, 32), outline=AMBAR, width=2)

    # Las 3 Esquirlas de Estrella (Veta Norte, Bóveda de las Geodas y Cámara de Kifaru)
    for (fx, fy) in ((590, 135), (725, 435), (82, 280)):
        d.polygon(
            [(fx, fy - 9), (fx + 7, fy - 4), (fx + 7, fy + 4), (fx, fy + 9), (fx - 7, fy + 4), (fx - 7, fy - 4)],
            fill=AMBAR,
            outline=(70, 42, 14),
            width=2,
        )

    # Jefe: Kifaru de Basalto y el Ancla de la Cadena Oeste
    jx, jy = 170, 280
    d.polygon([(jx, jy - 22), (jx + 18, jy), (jx, jy + 22), (jx - 18, jy)], fill=(196, 108, 28), outline=(255, 232, 180), width=2)
    # Cadena Oeste hacia Mji-Jiwe
    d.line([(48, 280), (112, 280)], fill=(150, 142, 164), width=5)

    # Rótulos
    rotulos = [
        (875, 330, "Este: desde Mji-Jiwe >>"),
        (785, 196, "1. Taller de Kito + Cambio de Agujas"),
        (710, 72, "2. Veta Norte (Esquirla de Kito)"),
        (565, 480, "3. Bóveda de las Geodas (oscuridad + 2.ª Esquirla)"),
        (415, 152, "4. El Cruce Mayor (desvío triple)"),
        (170, 120, "5. Cámara del Ancla Oeste"),
        (170, 312, "JEFE: KIFARU DE BASALTO (3.ª Esquirla)"),
    ]
    for (rx, ry, txt) in rotulos:
        tw = d.textlength(txt, font=fb)
        tx = min(max(rx - tw / 2, X0 + 6), X1 - tw - 6)
        d.rectangle([tx - 5, ry - 2, tx + tw + 5, ry + 17], fill=(24, 20, 18))
        d.text((tx, ry), txt, font=fb, fill=CREMA)

    d.text(
        (20, 12),
        "LAS GALERÍAS DE ÁMBAR — boceto del trazado y mecánicas (propuesta para decidir con Iam)",
        font=ft,
        fill=AMBAR,
    )

    # Leyenda inferior
    ley = [
        (AGUJA, "Cambio de agujas (gira el desvío de vía con un golpe)"),
        ((54, 50, 64), "Vagoneta de ámbar (se lanza con Carga Sísmica por los raíles)"),
        (AMBAR, "Geoda resonante (al golpearla ilumina las galerías oscuras)"),
        ((192, 188, 198), "Kito, talladora de ámbar en gris (abre el paso al Cruce Mayor)"),
        ((142, 74, 32), "Mchimbaji, Escarabajo Barrenador (rueda por las vías)"),
        ((88, 66, 58), "Barricada de basalto (cede al chocarle una vagoneta lanzada)"),
        ((255, 204, 72), "Esquirlas de Estrella (3: Kito + Bóveda Sur + Kifaru)"),
        ((196, 108, 28), "Kifaru de Basalto (jefe que custodia la Cadena Oeste)"),
    ]
    for i, (col, txt) in enumerate(ley):
        x, y = 28 + (i // 4) * 485, 540 + (i % 4) * 36
        d.rectangle([x, y, x + 18, y + 18], fill=col, outline=(120, 105, 90))
        d.text((x + 26, y + 1), txt, font=fp, fill=CREMA)

    salida = os.path.join(RAIZ, "documentacion", "boceto_galerias_ambar.png")
    img.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
