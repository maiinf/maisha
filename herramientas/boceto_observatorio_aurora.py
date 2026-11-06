"""Boceto del mapa de EL OBSERVATORIO DE LA AURORA (camino del norte de Sigilia), para decidir con Iam antes de que
Claude lo construya. Es un plano de diseño con la subida nevada, los telescopios y bobinas astrales, los puentes de
constelación, las fichas del Índice y la Cúpula Abierta de Kengele.
Sale en documentacion/boceto_observatorio_aurora.png (1000×700)."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 700
X0, Y0, X1, Y1 = 20, 44, 980, 524
FONDO = (18, 18, 28)
CREMA = (245, 232, 200)
NIEVE = (210, 214, 236)
PIEDRA = (84, 72, 122)
TERRAZA = (130, 122, 168)
COBRE = (232, 182, 86)
AURORA_V = (110, 232, 186)
AURORA_M = (182, 118, 244)
ABISMO = (14, 12, 26)


def fuentes():
    try:
        return (ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 13),
                ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana.ttf", 13),
                ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 15))
    except OSError:
        f = ImageFont.load_default()
        return f, f, f


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    fb, fp, ft = fuentes()

    # Abismo estrellado de la cumbre y cielo con aurora boreal al norte
    d.rectangle([X0, Y0, X1, Y1], fill=ABISMO)
    for x in range(X0, X1, 9):
        for y in range(Y0, Y1, 9):
            if (x * 13 + y * 19) % 43 == 0:
                d.point((x, y), fill=(220, 230, 255))
    # Bandas de aurora boreal arriba
    for k in range(3):
        pts = [(x, Y0 + 28 + k * 14 + int(10 * math.sin(x * 0.018 + k))) for x in range(X0 + 10, X1 - 10, 16)]
        d.line(pts, fill=AURORA_V if k % 2 == 0 else AURORA_M, width=6)

    # Tres grandes terrazas escalonadas de sur a norte unidas por puentes de constelación
    # 1. Terraza Sur (Llegada desde Maandiko y Torre del Reloj Astral)
    d.rounded_rectangle([320, 385, 680, 516], radius=22, fill=NIEVE, outline=PIEDRA, width=4)
    # 2. Terraza Media (Claustro de los Telescopios + Galerías Oeste y Este)
    d.rounded_rectangle([110, 230, 350, 345], radius=18, fill=NIEVE, outline=PIEDRA, width=4)
    d.rounded_rectangle([390, 220, 610, 345], radius=18, fill=TERRAZA, outline=PIEDRA, width=4)
    d.rounded_rectangle([650, 230, 890, 345], radius=18, fill=NIEVE, outline=PIEDRA, width=4)
    # 3. La Gran Cúpula Abierta (Norte: arena de Kengele)
    d.ellipse([370, 56, 630, 192], fill=TERRAZA, outline=COBRE, width=5)
    d.ellipse([392, 74, 608, 174], fill=(64, 54, 98), outline=AURORA_V, width=2)

    # Puentes de Constelación (se encienden al cargar las bobinas astrales con el Sigilo de Rayo)
    puentes = [
        [475, 345, 525, 385],   # terraza sur -> terraza central
        [350, 272, 390, 298],   # galería oeste <-> centro
        [610, 272, 650, 298],   # centro <-> galería este
        [475, 192, 525, 220],   # centro -> Gran Cúpula
    ]
    for p in puentes:
        d.rectangle(p, fill=(76, 168, 196), outline=AURORA_V, width=2)

    # Casa de Observación de Nyota (la astrónoma armiño en blanco) y Estela del Sigilo de Rayo
    d.rectangle([355, 415, 425, 470], fill=PIEDRA, outline=(40, 30, 56), width=2)
    d.pieslice([355, 392, 425, 440], 180, 360, fill=COBRE, outline=(80, 52, 16))
    # Nyota (armiño astrónoma en blanco)
    d.ellipse([442, 442, 456, 458], fill=(240, 238, 248), outline=(110, 104, 136), width=2)
    # Estela del Sigilo de Rayo (dorada/eléctrica)
    d.polygon([(555, 426), (565, 402), (575, 426), (575, 452), (555, 452)],
              fill=(255, 236, 120), outline=(180, 120, 20))

    # Bobinas / Diapasones Astrales (se cargan con el Sigilo de Rayo y se conectan por hilos de cobre)
    bobinas = [(498, 402), (498, 330), (370, 260), (630, 260), (498, 206),
               (410, 124), (590, 124), (500, 72)]
    for (bx, by) in bobinas:
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(255, 232, 110), outline=(90, 60, 15), width=2)

    # Enemigos: Autómatas de Relojería / Centinelas de Cuerda (Saa)
    for (ex, ey) in ((260, 285), (500, 280), (735, 285), (595, 455)):
        d.rectangle([ex - 8, ey - 8, ex + 8, ey + 8], fill=(168, 116, 64), outline=(255, 228, 130), width=2)

    # Cerraduras de hielo y tinta en las galerías laterales
    d.ellipse([295, 272, 325, 302], fill=(130, 210, 245), outline=(230, 250, 255), width=2)
    d.ellipse([675, 272, 705, 302], fill=(28, 20, 48), outline=AURORA_M, width=2)

    # Fichas del Índice (3: la de Nyota en la terraza sur-este, otra en la galería oeste y la de Kengele)
    for (fx, fy) in ((635, 435), (155, 285), (555, 124)):
        d.rectangle([fx - 7, fy - 9, fx + 7, fy + 9], fill=(248, 240, 218), outline=(90, 70, 110), width=2)
        d.line([fx - 4, fy - 3, fx + 4, fy - 3], fill=(90, 70, 110), width=2)
        d.line([fx - 4, fy + 2, fx + 4, fy + 2], fill=(90, 70, 110), width=2)

    # Jefe: Kengele en el centro de la Gran Cúpula Abierta
    jx, jy = 500, 124
    d.polygon([(jx, jy - 22), (jx + 18, jy), (jx, jy + 22), (jx - 18, jy)],
              fill=(218, 166, 68), outline=(255, 245, 200), width=2)

    # Rótulos
    rotulos = [
        (500, 494, "v sur: Maandiko"),
        (415, 476, "1. Cúpula de Nyota (en blanco)"),
        (595, 398, "Estela: Sigilo de Rayo"),
        (230, 236, "2. Galería del Solsticio (2.ª Ficha)"),
        (500, 242, "3. Claustro de los Telescopios"),
        (770, 236, "4. Galería de las Campanas"),
        (500, 152, "5. La Gran Cúpula: JEFE KENGELE (3.ª Ficha)"),
    ]
    for (rx, ry, txt) in rotulos:
        tw = d.textlength(txt, font=fb)
        tx = min(max(rx - tw / 2, X0 + 6), X1 - tw - 6)
        d.rectangle([tx - 5, ry - 2, tx + tw + 5, ry + 17], fill=(20, 18, 32))
        d.text((tx, ry), txt, font=fb, fill=CREMA)

    d.text((20, 12), "EL OBSERVATORIO DE LA AURORA — boceto del trazado y mecánicas (propuesta para Iam)",
           font=ft, fill=COBRE)

    # Leyenda inferior
    ley = [
        ((255, 232, 110), "Bobina / Diapasón astral (se activa con el Sigilo de Rayo U)"),
        ((76, 168, 196), "Puente de Constelación (aparece al encender las bobinas)"),
        ((240, 238, 248), "Nyota, astrónoma armiño en blanco (enseña el Sigilo de Rayo)"),
        ((168, 116, 64), "Saa, autómata de relojería (el rayo lo sobrecarga y detiene)"),
        ((248, 240, 218), "Fichas del Índice (3: Nyota + escriba + ficha del Guardián)"),
        ((218, 166, 68), "Kengele, la Gran Campana Muda (jefe en la Gran Cúpula)"),
        (AURORA_V, "Los tres Sigilos reunidos (Fuego + Hielo + Rayo) abren las galerías"),
        (TERRAZA, "Terrazas de piedra astronómica y observatorios de cobre"),
    ]
    for i, (col, txt) in enumerate(ley):
        x, y = 28 + (i // 4) * 485, 540 + (i % 4) * 36
        d.rectangle([x, y, x + 18, y + 18], fill=col, outline=(120, 110, 140))
        d.text((x + 26, y + 1), txt, font=fp, fill=CREMA)

    salida = os.path.join(RAIZ, "documentacion", "boceto_observatorio_aurora.png")
    img.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
