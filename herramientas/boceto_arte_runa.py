"""Boceto visual del ARTE DE LA RUNA (niveles 0 a 6 en Sigilia) y del CETRO NUEVO (al acabar el mundo 2),
siguiendo exactamente el formato de documentacion/boceto_artes_grandes.png (Maisha pixel art ×4).

Genera: documentacion/boceto_arte_runa.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_MAISHA = os.path.join(RAIZ, "arte", "personajes", "maisha", "maisha_base_frente.png")
CETRO_RAIZ = os.path.join(RAIZ, "arte", "personajes", "maisha", "prendas", "cetro_3.png")
SALIDA = os.path.join(RAIZ, "documentacion", "boceto_arte_runa.png")


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def px(img, x, y, c):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), rgb(c) if isinstance(c, str) else c)


def fuente(tam):
    for ruta in (
        "/System/Library/Fonts/Supplemental/Verdana.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ):
        if os.path.exists(ruta):
            return ImageFont.truetype(ruta, tam)
    return ImageFont.load_default()


def pintar_maisha_runa(nivel, cetro_img=None):
    """Devuelve un lienzo 36×40 en pixel art 1× con Maisha (pegada en 2,4: centro en x=13..14)
    y los rasgos del Arte de la Runa en el nivel dado (0..6)."""
    lienzo = Image.new("RGBA", (36, 40), (0, 0, 0, 0))
    base = Image.open(BASE_MAISHA).convert("RGBA")
    # Sombra ovalada en el suelo (bajo los pies en x=9..18, y=35)
    for x in range(6, 22):
        for y in range(34, 37):
            if ((x - 13.5) / 7.5) ** 2 + ((y - 35.0) / 1.6) ** 2 <= 1.0:
                px(lienzo, x, y, (34, 28, 58, 180))

    # Halo sutil de fondo a partir del nivel 3 (centrado en Maisha x=14, y=21)
    if nivel >= 3:
        for x in range(1, 28):
            for y in range(6, 35):
                d2 = ((x - 13.5) / 12.5) ** 2 + ((y - 21) / 13.0) ** 2
                if d2 <= 1.0:
                    lienzo.alpha_composite(
                        Image.new("RGBA", (1, 1), (90, 60, 150, 28 if nivel < 6 else 44)),
                        (x, y),
                    )

    # Nivel 5+: Manto / capa de pergamino y caligrafía detrás del cuerpo (x=7..20, y=24..34)
    if nivel >= 5:
        for y in range(24, 34):
            ancho = 6 + (y - 24) // 3
            x_izq, x_der = 14 - ancho, 14 + ancho
            for x in range(x_izq, x_der):
                borde = x in (x_izq, x_der - 1) or y == 33
                col = "2E1A44" if borde else ("E2CEA0" if (x + y) % 3 else "C8B08A")
                if not borde and y in (27, 30) and (x % 2 == 0):
                    col = "D4A034"  # renglón de tinta dorada
                px(lienzo, x, y, col)

    # Pegamos a Maisha en (2, 4): cabeza x=6..21, torso x=9..18, brazos x=6..8 y x=19..21
    lienzo.alpha_composite(base, (2, 4))

    # Nivel 1+: Muñequeras rúnicas en ambos brazos (x=6..8 y x=19..21, y=27..28)
    if nivel >= 1:
        for bx in (6, 19):
            px(lienzo, bx, 27, "4A2A6A")
            px(lienzo, bx + 1, 27, "F4E6C4")
            px(lienzo, bx + 2, 27, "4A2A6A")
            px(lienzo, bx, 28, "D4A034")
            px(lienzo, bx + 1, 28, "6A3E90")
            px(lienzo, bx + 2, 28, "D4A034")

    # Nivel 2+: Pluma de escriba blanca y dorada asomando junto a la cabeza (izquierda, x=4..7, y=8..13)
    if nivel >= 2:
        for dx, dy, col in (
            (7, 13, "D4A034"),
            (6, 12, "F0CC60"),
            (6, 11, "EAE6F8"),
            (5, 10, "FFFFFF"),
            (5, 9, "FFFFFF"),
            (4, 8, "DCD8EC"),
            (6, 9, "DCD8EC"),
        ):
            px(lienzo, dx, dy, col)

    # Nivel 3+: ✦ Estola del Índice sobre los hombros (x=8..19, y=23..25) con dos bandas laterales
    if nivel >= 3:
        for x in range(8, 20):
            px(lienzo, x, 23, "2E1A44")
            px(lienzo, x, 24, "6A3E90" if x not in (9, 18) else "F0CC60")
            px(lienzo, x, 25, "D4A034" if x in (8, 9, 18, 19) else "4A2A6A")
        # Dos caídas de la estola a los lados del corazón de luz (x=10 y x=17, dejando libre el centro x=12..15)
        for sx in (10, 17):
            for sy in range(25, 30):
                px(lienzo, sx, sy, "F0CC60" if sy == 29 else ("8A5AB0" if sy == 27 else "6A3E90"))

    # Nivel 4+: Broche de lacre dorado y amatista en el cuello de la estola (x=13..14, y=23..24)
    if nivel >= 4:
        px(lienzo, 13, 23, "D4A034")
        px(lienzo, 14, 23, "FFF0B0")
        px(lienzo, 13, 24, "C864FF")
        px(lienzo, 14, 24, "D4A034")

    # Nivel 6: ✦ Corona/Halo de los Tres Sigilos flotando alrededor de Maisha (Fuego, Hielo, Rayo)
    if nivel >= 6:
        # Sigilo de Fuego (izquierda, x=2..3, y=18..20)
        for dx, dy, c in ((2, 19, "FF7A26"), (3, 18, "FFE082"), (3, 19, "FF9E40"), (3, 20, "C8401A")):
            px(lienzo, dx, dy, c)
        # Sigilo de Hielo (derecha, x=24..25, y=14..16)
        for dx, dy, c in ((25, 15, "7CE8FF"), (24, 14, "E0FFFF"), (24, 15, "4AB8E8"), (24, 16, "2E6A9E")):
            px(lienzo, dx, dy, c)
        # Sigilo de Rayo (arriba junto al brote, x=9..10 y x=18..19, y=5..6)
        for dx, dy, c in ((9, 6, "FFF6B0"), (10, 5, "F0CC60"), (19, 6, "FFF6B0"), (18, 5, "F0CC60")):
            px(lienzo, dx, dy, c)

    # El cetro apoyado en la mano derecha
    if cetro_img is None:
        cetro_img = Image.open(CETRO_RAIZ).convert("RGBA")
    lienzo.alpha_composite(cetro_img, (19, 16))
    return lienzo


def cetro_nuevo_nivel(n, opcion="A"):
    """Dibuja el Cetro Nuevo (16×23) en el nivel n (0..6) según la opción A, B o C."""
    img = Image.new("RGBA", (16, 23), (0, 0, 0, 0))
    if opcion == "A":
        palo = ("1E2030", "3E425C", "686E92", "9AA2C8")
        runa = "5CE0FF" if n < 4 else ("F0CC60" if n < 6 else "FFF4B8")
        for y in range(9, 22):
            px(img, 6, y, palo[0])
            px(img, 7, y, palo[2])
            px(img, 8, y, palo[1])
            px(img, 9, y, palo[0])
            if (n >= 1 and y == 14) or (n >= 2 and y in (12, 16)) or (n >= 4 and y in (10, 14, 18)):
                px(img, 7, y, runa)
                if n >= 5:
                    px(img, 8, y, "D4A034")
        px(img, 7, 22, palo[0])
        px(img, 8, 22, palo[0])
        for x, y in ((5, 8), (5, 7), (5, 6), (6, 9), (10, 8), (10, 7), (10, 6), (9, 9)):
            px(img, x, y, palo[2] if x in (5, 6) else palo[1])
        if n >= 3:
            for x in range(6, 10):
                px(img, x, 11, "F0CC60" if n >= 5 else "9AA2C8")
            for x, y in ((3, 5), (3, 6), (4, 7), (12, 5), (12, 6), (11, 7)):
                px(img, x, y, "F0CC60" if n >= 6 else palo[2])
        c_borde = "1A4A7A" if n < 5 else "8A5A10"
        c_centro = "58B8FF" if n < 5 else "F9D77A"
        c_luz = "E0F8FF" if n < 5 else "FFFFFF"
        for x, y in ((7, 3), (8, 3), (6, 4), (9, 4), (6, 5), (9, 5), (7, 6), (8, 6)):
            px(img, x, y, c_borde)
        for x, y in ((7, 4), (8, 4), (7, 5), (8, 5)):
            px(img, x, y, c_centro)
        px(img, 7, 4, c_luz)
        if n >= 3:
            for x, y in ((4, 4), (11, 4), (7, 1), (8, 1)):
                px(img, x, y, c_luz if n >= 6 else c_centro)
        if n >= 6:
            px(img, 2, 3, "6FCF4F")
            px(img, 3, 4, "3E9A35")
            px(img, 13, 3, "FFF4B8")
            px(img, 12, 4, "D4A034")
    elif opcion == "B":
        for y in range(9, 22):
            px(img, 6, y, "180E29")
            px(img, 7, y, "54347A" if y % 3 else "D4A034")
            px(img, 8, y, "362052")
            px(img, 9, y, "180E29")
        for x in range(5, 11):
            for y in range(5, 9):
                px(img, x, y, "B882EA" if 6 <= x <= 9 and 6 <= y <= 7 else "2E1A44")
        for y, cols in ((4, (6, 9)), (3, (6, 9)), (2, (7, 8)), (1, (7, 8))):
            for x in range(cols[0], cols[1] + 1):
                px(img, x, y, "FFF0B0" if x == 7 else "D4A034")
    else:
        for y in range(9, 22):
            dx = 1 if (y // 5) % 2 else 0
            px(img, 6 + dx, y, "2A1A10")
            px(img, 7 + dx, y, "7A5230")
            px(img, 8 + dx, y, "4E321C")
        for x in range(4, 12):
            for y in range(3, 9):
                if ((x - 7.5) / 4.0) ** 2 + ((y - 5.5) / 3.2) ** 2 <= 1.0:
                    px(img, x, y, "F9B947" if 6 <= x <= 9 and 4 <= y <= 7 else "3A2818")
        px(img, 7, 5, "FFF8D2")
        px(img, 8, 4, "FFF8D2")
    return img


def main():
    W, H = 920, 575
    img = Image.new("RGBA", (W, H), rgb("12101E"))
    d = ImageDraw.Draw(img)
    f_tit = fuente(15)
    f_sub = fuente(13)
    f_peq = fuente(11)

    # 1. Fila superior: Arte de la Runa (niveles 0 a 6)
    d.text((22, 16), "Arte de la Runa en Sigilia (* = cambio grande en niveles 3 y 6)", font=f_tit, fill=rgb("C9A7E8"))
    etiquetas_runa = [
        "0 base",
        "1 muñequeras",
        "2 + pluma",
        "3 * estola Índice",
        "4 + sello lacre",
        "5 manto escrito",
        "6 * halo 3 Sigilos",
    ]
    for n in range(7):
        x0 = 18 + n * 126
        y0 = 46
        cuadro = pintar_maisha_runa(n).resize((36 * 4, 40 * 4), Image.NEAREST)
        img.alpha_composite(cuadro, (x0, y0))
        d.text((x0 + 10, y0 + 166), etiquetas_runa[n], font=f_peq, fill=rgb("FFF0B0" if n in (3, 6) else "B8B2D4"))

    # 2. Fila central izquierda: Evolución del Cetro Nuevo (Opción A · niveles 0 a 6)
    d.text((22, 246), "Cetro Nuevo al acabar Sigilia · Opción A (niveles 0 a 6)", font=f_tit, fill=rgb("9FD8E8"))
    etiquetas_cetro = [
        "0 piedra",
        "1 runa",
        "2 dos runas",
        "3 * horquilla",
        "4 oro",
        "5 sol",
        "6 * Nexo",
    ]
    for n in range(7):
        x0 = 24 + n * 82
        y0 = 282
        c_img = cetro_nuevo_nivel(n, "A").resize((16 * 5, 23 * 5), Image.NEAREST)
        img.alpha_composite(c_img, (x0, y0))
        d.text((x0 + 30, y0 + 120), f"{n}{'*' if n in (3, 6) else ''}", font=f_sub, fill=rgb("F0CC60" if n in (3, 6) else "DCD8EC"))
        d.text((x0 + 10, y0 + 140), etiquetas_cetro[n], font=f_peq, fill=rgb("B8B2D4"))

    # Maisha con el Arte de la Runa al 6 + Cetro del Nexo al 6
    d.text((640, 246), "Maisha (Runa 6 + Cetro 6)", font=f_tit, fill=rgb("F0CC60"))
    c6 = cetro_nuevo_nivel(6, "A").crop((0, 0, 16, 21))
    m_max = pintar_maisha_runa(6, cetro_img=c6).resize((36 * 4, 40 * 4), Image.NEAREST)
    img.alpha_composite(m_max, (670, 276))

    # 3. Comparativa de las 3 opciones de Cetro Nuevo abajo
    d.line([(22, 456), (898, 456)], fill=rgb("2E2646"), width=2)
    d.text((22, 466), "Opciones para el Cetro Nuevo al acabar Sigilia:", font=f_sub, fill=rgb("F0CC60"))
    opciones = [
        ("A (Recomendada): Cetro del Nexo", "Piedra rúnica, cristal, Semilla y Pluma", "A"),
        ("B: Cálamo del Primer Nombre", "Ébano morado, tintero y plumilla de oro", "B"),
        ("C: Báculo de Ámbar Estelar", "Raíz fosilizada y geoda de ámbar", "C"),
    ]
    for i, (titulo, desc, cod) in enumerate(opciones):
        ox = 22 + i * 296
        oy = 490
        d.rounded_rectangle([ox, oy, ox + 284, oy + 68], radius=6, fill=rgb("1C1830"), outline=rgb("6A4E9A" if i == 0 else "342A4E"))
        icono = cetro_nuevo_nivel(6, cod).resize((16 * 3, 23 * 3), Image.NEAREST)
        img.alpha_composite(icono, (ox + 6, oy - 2))
        d.text((ox + 56, oy + 12), titulo, font=f_peq, fill=rgb("FFF0B0" if i == 0 else "DCD8EC"))
        d.text((ox + 56, oy + 36), desc, font=f_peq, fill=rgb("B8B2D4"))

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    img.save(SALIDA)
    print("Boceto guardado en", SALIDA)


if __name__ == "__main__":
    main()
