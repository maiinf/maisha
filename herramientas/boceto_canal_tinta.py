"""Boceto del mapa de EL CANAL DE TINTA (camino del este de Sigilia), para decidir con Iam antes de que Claude
lo construya. Es un plano de diseño con el recorrido, las esclusas, la corriente, las fichas y la Gran Dársena.
Sale en documentacion/boceto_canal_tinta.png (1000×700)."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 700
X0, Y0, X1, Y1 = 20, 44, 980, 524
FONDO = (22, 20, 28)
CREMA = (245, 232, 200)
NIEVE = (206, 200, 226)
PIEDRA = (96, 74, 126)
MUELLE = (138, 124, 166)
TEJADO = (226, 186, 90)
TINTA = (24, 18, 44)
TINTA_VIVA = (42, 32, 74)
HIELO = (156, 220, 248)
ORO = (242, 202, 96)


def fuentes():
    try:
        return (ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 13),
                ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana.ttf", 13),
                ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 15))
    except OSError:
        f = ImageFont.load_default()
        return f, f, f


def flecha(d, x0, y0, x1, y1, col):
    d.line([(x0, y0), (x1, y1)], fill=col, width=2)
    ang = math.atan2(y1 - y0, x1 - x0)
    for da in (-2.5, 2.5):
        d.line([(x1, y1), (x1 + 7 * math.cos(ang + da), y1 + 7 * math.sin(ang + da))], fill=col, width=2)


def main():
    img = Image.new("RGB", (W, H), FONDO)
    d = ImageDraw.Draw(img)
    fb, fp, ft = fuentes()

    # Terreno nevado y peñas de pizarra morada alrededor
    d.rectangle([X0, Y0, X1, Y1], fill=NIEVE)
    for x in range(X0, X1, 7):
        for y in range(Y0, Y1, 7):
            if (x * 11 + y * 17) % 41 == 0:
                d.point((x, y), fill=(236, 232, 248))
    d.rectangle([X0, Y0, X1, Y0 + 22], fill=(70, 56, 96))
    d.rectangle([X0, Y1 - 22, X1, Y1], fill=(70, 56, 96))

    # El Gran Canal de Tinta: cruza de oeste a este con remansos y baja a la Gran Dársena al sureste
    # Remanso norte (ficha de Mfereji)
    d.rounded_rectangle([190, 78, 370, 220], radius=24, fill=TINTA_VIVA, outline=PIEDRA, width=4)
    # Tramo central con corriente (de oeste a este)
    d.rectangle([X0 + 8, 230, 740, 340], fill=TINTA_VIVA, outline=PIEDRA, width=4)
    # Ramal sur (alcobas y esclusa secundaria)
    d.rounded_rectangle([390, 330, 580, 480], radius=20, fill=TINTA_VIVA, outline=PIEDRA, width=4)
    # Gran Dársena de Tinta (sureste: arena de Pweza)
    d.ellipse([700, 210, 956, 486], fill=TINTA, outline=PIEDRA, width=6)
    d.ellipse([724, 234, 932, 462], fill=TINTA_VIVA, outline=(120, 96, 168), width=2)

    # Muelles y pasarelas de piedra junto al canal
    muelles = [
        [X0 + 8, 175, 210, 232],       # entrada desde Maandiko
        [210, 175, 430, 232],          # muelle de la Casa de la Esclusa
        [430, 165, 680, 232],          # muelle norte con ruedas de compuerta
        [120, 338, 410, 395],          # muelle sur oeste
        [560, 338, 730, 410],          # muelle de llegada a la dársena
        [680, 150, 880, 222],          # balcón norte de la dársena
    ]
    for m in muelles:
        d.rectangle(m, fill=MUELLE, outline=PIEDRA, width=2)

    # Muelle anular de la Gran Dársena (donde pisa Maisha durante la pelea con Pweza)
    d.arc([692, 202, 964, 494], 120, 310, fill=MUELLE, width=18)

    # Compuertas de hierro (esclusas) y ruedas de maniobra
    for xc in (215, 435, 665):
        d.rectangle([xc - 5, 226, xc + 5, 344], fill=(56, 52, 74), outline=ORO, width=2)
        # rueda de esclusa en el muelle norte
        d.ellipse([xc - 9, 204, xc + 9, 222], fill=ORO, outline=(70, 48, 16), width=2)

    # Placas de tinta helada (creadas con el Sigilo de Hielo) flotando en el canal
    for (px, py) in ((280, 150), (325, 280), (500, 285), (595, 285), (480, 405), (760, 340)):
        d.polygon([(px - 22, py), (px - 8, py - 14), (px + 18, py - 12),
                   (px + 24, py + 4), (px + 6, py + 14), (px - 18, py + 10)],
                  fill=HIELO, outline=(230, 250, 255))

    # Flechas de corriente de tinta en el tramo central
    for fx in (260, 370, 520, 620):
        flecha(d, fx, 265, fx + 42, 265, (150, 130, 220))
        flecha(d, fx, 305, fx + 42, 305, (150, 130, 220))

    # Casa de la Esclusa (taller de Mfereji) y Estela del Sigilo de Hielo
    d.rectangle([240, 118, 310, 174], fill=PIEDRA, outline=(40, 30, 56), width=2)
    d.polygon([(234, 118), (275, 88), (316, 118)], fill=TEJADO, outline=(90, 60, 20))
    # Mfereji (armiño esclusista en blanco)
    d.ellipse([270, 184, 284, 200], fill=(240, 238, 248), outline=(110, 104, 136), width=2)
    # Estela del Sigilo de Hielo (brillo celeste)
    d.polygon([(354, 178), (364, 156), (374, 178), (374, 202), (354, 202)],
              fill=HIELO, outline=(60, 120, 170))

    # Charcos de Tinta Quieta (cerraduras de fuego)
    for (cx, cy) in ((198, 150), (410, 365)):
        d.ellipse([cx - 20, cy - 13, cx + 20, cy + 13], fill=TINTA, outline=(168, 96, 236), width=2)

    # Enemigos: Sanguijuelas de Tinta (Ruba) en el agua y Tinteros en los muelles
    for (ex, ey) in ((350, 250), (550, 315), (460, 375), (530, 440)):
        d.ellipse([ex - 9, ey - 6, ex + 9, ey + 6], fill=(92, 48, 148), outline=(210, 170, 255))
    for (tx, ty) in ((250, 365), (610, 195)):
        d.rectangle([tx - 7, ty - 7, tx + 7, ty + 7], fill=(60, 36, 96), outline=ORO)

    # Fichas del Índice (3: la de Mfereji, una en el ramal sur y la de Pweza)
    for (fx, fy) in ((280, 102), (485, 462), (895, 348)):
        d.rectangle([fx - 7, fy - 9, fx + 7, fy + 9], fill=(248, 240, 218), outline=(90, 70, 110), width=2)
        d.line([fx - 4, fy - 3, fx + 4, fy - 3], fill=(90, 70, 110), width=2)
        d.line([fx - 4, fy + 2, fx + 4, fy + 2], fill=(90, 70, 110), width=2)

    # Jefe: Pweza en el centro de la Gran Dársena
    jx, jy = 835, 348
    d.polygon([(jx, jy - 22), (jx + 18, jy), (jx, jy + 22), (jx - 18, jy)],
              fill=(128, 52, 176), outline=(245, 215, 255), width=2)

    # Rótulos explicativos
    rotulos = [
        (95, 152, "<< oeste: Maandiko"),
        (275, 70, "1. Remanso Norte (Ficha de Mfereji)"),
        (275, 206, "Casa de la Esclusa y Mfereji"),
        (385, 140, "Estela: Sigilo de Hielo"),
        (515, 240, "2. El Cauce Mayor (corriente + placas de hielo)"),
        (485, 492, "3. Esclusa Hundida (2.ª Ficha)"),
        (830, 182, "4. La Gran Dársena de Tinta"),
        (835, 380, "JEFE: PWEZA (3.ª Ficha)"),
    ]
    for (rx, ry, txt) in rotulos:
        tw = d.textlength(txt, font=fb)
        tx = min(max(rx - tw / 2, X0 + 6), X1 - tw - 6)
        d.rectangle([tx - 5, ry - 2, tx + tw + 5, ry + 17], fill=(24, 20, 34))
        d.text((tx, ry), txt, font=fb, fill=CREMA)

    d.text((20, 12), "EL CANAL DE TINTA — boceto del trazado y mecánicas (propuesta para decidir con Iam)",
           font=ft, fill=ORO)

    # Leyenda inferior
    ley = [
        (HIELO, "Placa de tinta helada (se crea con el Sigilo de Hielo U)"),
        ((56, 52, 74), "Compuerta de esclusa (se abre girando las ruedas doradas)"),
        ((240, 238, 248), "Mfereji, armiño esclusista en blanco (enseña el Sigilo de Hielo)"),
        ((92, 48, 148), "Ruba (sanguijuela de tinta: el hielo la deja atrapada)"),
        ((248, 240, 218), "Fichas del Índice (3: Mfereji + 2 escribas de Maandiko)"),
        ((128, 52, 176), "Pweza, el Pulpo de Tinta (jefe en la Gran Dársena)"),
        (TINTA, "Cerradura de Tinta Quieta (se derrite con Sigilo de Fuego)"),
        (MUELLE, "Muelles de sillería y pasarelas sobre el canal"),
    ]
    for i, (col, txt) in enumerate(ley):
        x, y = 28 + (i // 4) * 485, 540 + (i % 4) * 36
        d.rectangle([x, y, x + 18, y + 18], fill=col, outline=(120, 110, 140))
        d.text((x + 26, y + 1), txt, font=fp, fill=CREMA)

    salida = os.path.join(RAIZ, "documentacion", "boceto_canal_tinta.png")
    img.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
