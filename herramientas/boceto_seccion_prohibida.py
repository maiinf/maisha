"""Boceto del mapa de LA SECCIÓN PROHIBIDA (el subsuelo bajo el Gran Archivo de Maandiko y final de Sigilia),
para decidir con Iam antes de que Claude lo construya. Incluye el Claustro de los Tres Sigilos, el Pasillo de las
Frases Borradas y la Rotonda del Primer Nombre (arena del Grimorio de Tinta).
Sale en documentacion/boceto_seccion_prohibida.png (1000×700)."""
import os

from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 700
X0, Y0, X1, Y1 = 20, 44, 980, 524
FONDO = (16, 12, 24)
CREMA = (245, 232, 200)
PIEDRA = (78, 58, 112)
SUELO = (114, 96, 150)
TINTA = (20, 14, 36)
TINTA_VIVA = (36, 26, 64)
ORO = (242, 202, 96)
FUEGO = (248, 132, 68)
HIELO = (142, 218, 250)
RAYO = (255, 234, 110)


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

    # Foso subterráneo de Tinta Profunda que rodea las cámaras
    d.rectangle([X0, Y0, X1, Y1], fill=TINTA)
    for x in range(X0, X1, 10):
        for y in range(Y0, Y1, 10):
            if (x * 7 + y * 13) % 39 == 0:
                d.point((x, y), fill=(90, 70, 140))

    # 1. Atrio Sur: La Escalera de los 12 Nombres (bajada desde el Gran Archivo)
    d.rounded_rectangle([370, 405, 630, 516], radius=16, fill=SUELO, outline=PIEDRA, width=4)
    for i in range(6):
        ay = 420 + i * 14
        d.rectangle([392, ay, 404, ay + 8], fill=ORO)
        d.rectangle([596, ay, 608, ay + 8], fill=ORO)
    # Mauti y Kalamu junto al umbral
    d.ellipse([468, 476, 482, 492], fill=(204, 192, 244), outline=(110, 90, 170), width=2)
    d.ellipse([518, 476, 532, 492], fill=(240, 236, 248), outline=ORO, width=2)

    # 2. El Claustro de los Tres Sigilos (Centro + Cámaras Oeste y Este)
    d.rounded_rectangle([380, 250, 620, 368], radius=18, fill=SUELO, outline=PIEDRA, width=4)
    # Cámara Oeste (Prueba de Fuego + Hielo: derretir cadenas de tinta y congelar el foso)
    d.rounded_rectangle([110, 245, 330, 372], radius=18, fill=TINTA_VIVA, outline=PIEDRA, width=4)
    d.rectangle([135, 268, 225, 348], fill=SUELO, outline=PIEDRA, width=2)
    for (px, py) in ((265, 290), (265, 330), (355, 308)):
        d.polygon([(px - 18, py), (px - 6, py - 12), (px + 16, py - 10),
                   (px + 20, py + 4), (px + 4, py + 12), (px - 14, py + 8)],
                  fill=HIELO, outline=(230, 250, 255))
    # Cámara Este (Prueba de Hielo + Rayo: bobinas sobre placas y puente de constelación)
    d.rounded_rectangle([670, 245, 890, 372], radius=18, fill=SUELO, outline=PIEDRA, width=4)
    d.rectangle([620, 296, 670, 322], fill=(76, 168, 196), outline=(110, 232, 186), width=2)

    # Puentes y cerraduras
    d.rectangle([480, 368, 520, 405], fill=SUELO, outline=ORO, width=2)
    d.rectangle([476, 198, 524, 250], fill=(76, 168, 196), outline=ORO, width=2)

    # 3. La Rotonda del Primer Nombre (Norte: Arena del Grimorio de Tinta)
    d.ellipse([340, 52, 660, 204], fill=SUELO, outline=ORO, width=5)
    d.ellipse([368, 70, 632, 186], fill=(58, 44, 92), outline=(170, 140, 220), width=2)

    # Los tres pedestales elementales en la Rotonda (Fuego, Hielo, Rayo)
    for (sx, sy, col) in ((400, 128, FUEGO), (500, 74, RAYO), (600, 128, HIELO)):
        d.ellipse([sx - 11, sy - 11, sx + 11, sy + 11], fill=col, outline=(40, 28, 60), width=2)

    # Sello triple en el Claustro Central
    for (sx, sy, col) in ((440, 280, FUEGO), (500, 280, HIELO), (560, 280, RAYO)):
        d.ellipse([sx - 9, sy - 9, sx + 9, sy + 9], fill=col, outline=ORO, width=2)

    # Enemigos: Sombras de Renglón / Ecos Borrados
    for (ex, ey) in ((180, 308), (760, 308), (430, 330), (570, 330)):
        d.ellipse([ex - 8, ey - 8, ex + 8, ey + 8], fill=(44, 30, 76), outline=(190, 150, 255), width=2)

    # Jefe Final: El Grimorio de Tinta en el centro de la Rotonda
    jx, jy = 500, 132
    d.polygon([(jx, jy - 24), (jx + 20, jy), (jx, jy + 24), (jx - 20, jy)],
              fill=(216, 48, 76), outline=(255, 235, 200), width=3)

    # Rótulos
    rotulos = [
        (500, 496, "v sur: Gran Archivo de Maandiko (pide las 12 Fichas)"),
        (500, 430, "1. Escalera de los 12 Nombres (con Mauti y Kalamu)"),
        (220, 248, "2. Cámara del Sello de Fuego y Hielo"),
        (500, 305, "3. Claustro del Triple Sello"),
        (780, 248, "4. Cámara del Sello de Hielo y Rayo"),
        (500, 162, "5. Rotonda del Primer Nombre: JEFE GRIMORIO DE TINTA"),
    ]
    for (rx, ry, txt) in rotulos:
        tw = d.textlength(txt, font=fb)
        tx = min(max(rx - tw / 2, X0 + 6), X1 - tw - 6)
        d.rectangle([tx - 5, ry - 2, tx + tw + 5, ry + 17], fill=(20, 14, 30))
        d.text((tx, ry), txt, font=fb, fill=CREMA)

    d.text((20, 12), "LA SECCIÓN PROHIBIDA — boceto del trazado final de Sigilia (propuesta para Iam)",
           font=ft, fill=ORO)

    # Leyenda inferior
    ley = [
        (FUEGO, "Pedestal / Sello de Fuego (derrite cadenas de Tinta Quieta)"),
        (HIELO, "Placa y Pedestal de Hielo (cruza fosos de tinta profunda)"),
        (RAYO, "Bobina y Pedestal de Rayo (enciende puentes de constelación)"),
        ((216, 48, 76), "El Grimorio de Tinta (jefe final de Sigilia en la Rotonda)"),
        ((44, 30, 76), "Sombra de Renglón (enemigo que nace de las frases borradas)"),
        ((204, 192, 244), "Mauti y Kalamu acompañando a Maisha en la bajada"),
        (ORO, "Los 12 Atriles del Índice (se encienden con las 12 fichas)"),
        (SUELO, "Salas subterráneas de mármol morado bajo el Gran Archivo"),
    ]
    for i, (col, txt) in enumerate(ley):
        x, y = 28 + (i // 4) * 485, 540 + (i % 4) * 36
        d.rectangle([x, y, x + 18, y + 18], fill=col, outline=(120, 110, 140))
        d.text((x + 26, y + 1), txt, font=fp, fill=CREMA)

    salida = os.path.join(RAIZ, "documentacion", "boceto_seccion_prohibida.png")
    img.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
