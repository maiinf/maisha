"""Boceto visual del ARTE DE LA TIERRA (niveles 0 a 6 en Asterhaul), su evolución junto al
CETRO DEL NEXO (nexo_0..6 reales) y las opciones de diseño + catálogo de CHUMA (Mercado de la Escoria).

Genera: documentacion/boceto_arte_tierra.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_MAISHA = os.path.join(RAIZ, "arte", "personajes", "maisha", "maisha_base_frente.png")
NEXO_RUTA = os.path.join(RAIZ, "arte", "personajes", "maisha", "prendas", "nexo_%d.png")
SALIDA = os.path.join(RAIZ, "documentacion", "boceto_arte_tierra.png")


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


def pintar_maisha_tierra(nivel):
    """Lienzo 36×40 en pixel art 1× con Maisha, piezas acumulativas de Tierra (0..6) y Cetro del Nexo N."""
    lienzo = Image.new("RGBA", (36, 40), (0, 0, 0, 0))
    base = Image.open(BASE_MAISHA).convert("RGBA")

    # Sombra cálida de basalto
    for x in range(6, 22):
        for y in range(34, 37):
            if ((x - 13.5) / 7.5) ** 2 + ((y - 35.0) / 1.6) ** 2 <= 1.0:
                px(lienzo, x, y, (46, 30, 18, 180))

    # Nivel 6: aura solar suave de ámbar detrás de Maisha
    if nivel >= 6:
        for x in range(1, 28):
            for y in range(6, 35):
                d2 = ((x - 13.5) / 12.5) ** 2 + ((y - 21) / 13.0) ** 2
                if d2 <= 1.0:
                    lienzo.alpha_composite(Image.new("RGBA", (1, 1), (225, 145, 45, 42)), (x, y))

    # Pegamos a Maisha en (2, 4): torso x=9..18, piernas x=9..17, brazos x=6..8 y x=19..21
    lienzo.alpha_composite(base, (2, 4))

    # Nivel 1+: Grebas de basalto y cobre en botas/tobillos (y=32..35)
    if nivel >= 1:
        for x in (10, 11, 12, 15, 16, 17):
            px(lienzo, x, 33, "2E2A36" if x in (10, 17) else "4A4658")
            px(lienzo, x, 34, "C8741C" if x in (11, 16) else "24202C")
            px(lienzo, x, 35, "3A3446")

    # Nivel 5+: Escarcela / faldón de herrero bajo el cinto (x=9..18, y=28..32)
    if nivel >= 5:
        for x in range(9, 19):
            px(lienzo, x, 29, "5A3620" if x not in (10, 17) else "2A1810")
            px(lienzo, x, 30, "74482A" if x in (12, 13, 14, 15) else "3E2414")
            if x in (10, 17):
                px(lienzo, x, 31, "D88830")
            elif 11 <= x <= 16:
                px(lienzo, x, 31, "4A2C1A")

    # Nivel 2+: Cinturón ancho de escoria con hebilla de ámbar (x=9..18, y=27..28)
    if nivel >= 2:
        for x in range(9, 19):
            px(lienzo, x, 27, "3A2414")
            px(lienzo, x, 28, "5E3A22")
        for x in (13, 14):
            px(lienzo, x, 27, "F6C258")
            px(lienzo, x, 28, "FFF2B0" if x == 13 else "D8841C")

    # Nivel 3+: Hombrera asimétrica de geoda con núcleo de ámbar (hombro izquierdo x=6..10, y=21..24)
    if nivel >= 3:
        for x, y, c in (
            (7, 21, "2C2634"), (8, 21, "4A4258"), (9, 21, "6E647C"), (10, 21, "4A4258"),
            (6, 22, "2C2634"), (7, 22, "6E647C"), (8, 22, "FFD26A"), (9, 22, "D8841C"), (10, 22, "2C2634"),
            (7, 23, "4A4258"), (8, 23, "FFF0B0"), (9, 23, "6E647C"),
            (8, 24, "2C2634"), (9, 24, "4A4258"),
        ):
            px(lienzo, x, y, c)

    # Nivel 4+: Guanteletes imantados en ambos puños (x=6..8 y x=19..21, y=26..28)
    if nivel >= 4:
        for bx in (6, 19):
            px(lienzo, bx, 26, "3A4258")
            px(lienzo, bx + 1, 26, "7BE0FF")
            px(lienzo, bx + 2, 26, "3A4258")
            px(lienzo, bx, 27, "222838")
            px(lienzo, bx + 1, 27, "687494")
            px(lienzo, bx + 2, 27, "F4C056")
            px(lienzo, bx + 1, 28, "3A4258")

    # Nivel 6: Cristales / esquirlas de ámbar solar orbitando
    if nivel >= 6:
        for dx, dy in ((3, 17), (25, 13), (23, 27)):
            px(lienzo, dx, dy - 1, "FFF4B8")
            px(lienzo, dx - 1, dy, "E89830")
            px(lienzo, dx, dy, "FFD26A")
            px(lienzo, dx + 1, dy, "D87818")
            px(lienzo, dx, dy + 1, "8E4410")

    # Cetro del Nexo real correspondiente al nivel (nexo_0..6)
    nexo_path = NEXO_RUTA % min(max(nivel, 0), 6)
    if os.path.exists(nexo_path):
        nexo = Image.open(nexo_path).convert("RGBA")
        lienzo.alpha_composite(nexo, (19, 17))
    return lienzo


def icono_tienda(kind):
    """Mini icono 12×12 en pixel art para los artículos de Chuma."""
    im = Image.new("RGBA", (12, 12), (0, 0, 0, 0))
    if kind == "amolar":
        pts = [(2, 8, "566078"), (3, 7, "7884A0"), (4, 6, "9AA6C0"), (5, 5, "D8841C"), (6, 4, "FFD26A"), (7, 3, "FFF0B0"), (8, 4, "9AA6C0"), (9, 5, "566078")]
        for x, y, c in pts:
            px(im, x, y, c); px(im, x, y + 1, c)
    elif kind == "fuelle":
        for x in range(2, 9):
            for y in range(4, 9):
                px(im, x, y, "6E3A20" if (x + y) % 2 else "4A2412")
        for x in range(8, 11):
            px(im, x, 6, "9AA6C0")
        px(im, 4, 6, "FFD26A")
    elif kind == "farol":
        for y in range(3, 9):
            for x in range(4, 8):
                px(im, x, y, "FFF0B0" if 5 <= y <= 7 and 5 <= x <= 6 else "FFD26A")
        for x in (3, 8):
            for y in range(2, 10):
                px(im, x, y, "2E2A36")
        for x in range(4, 8):
            px(im, x, 2, "566078"); px(im, x, 9, "566078")
    else:  # delantal
        for y in range(2, 10):
            for x in range(3, 9):
                px(im, x, y, "3E2212" if x in (3, 8) or y == 9 else ("8A5230" if y < 6 else "6A3E20"))
        px(im, 5, 4, "E89830"); px(im, 6, 4, "FFD26A")
    return im


def main():
    W, H = 940, 720
    img = Image.new("RGBA", (W, H), rgb("16111A"))
    d = ImageDraw.Draw(img)
    f_tit = fuente(15)
    f_sub = fuente(13)
    f_peq = fuente(11)

    # 1. Fila superior: Arte de la Tierra (niveles 0 a 6)
    d.text((22, 16), "Arte de la Tierra en Asterhaul (* = cambio grande en niveles 3 y 6 · Mhunzi)", font=f_tit, fill=rgb("F0B860"))
    etiquetas_tierra = [
        "0 base + nexo_0",
        "1 grebas basalto",
        "2 + cinto ambar",
        "3 * hombrera geoda",
        "4 + guantes iman",
        "5 faldon forja",
        "6 * aura Semilla",
    ]
    for n in range(7):
        x0 = 18 + n * 128
        y0 = 46
        cuadro = pintar_maisha_tierra(n).resize((36 * 4, 40 * 4), Image.NEAREST)
        img.alpha_composite(cuadro, (x0, y0))
        d.text((x0 + 8, y0 + 166), etiquetas_tierra[n], font=f_peq, fill=rgb("FFF0B0" if n in (3, 6) else "D6C6B2"))

    # 2. Fila central: Evolución real del Cetro del Nexo (nexo_0..6 ya pintados) + Maisha al 6
    d.text((22, 242), "Subida del Cetro del Nexo con el Arte de la Tierra (nexo_0..6)", font=f_tit, fill=rgb("9FD8E8"))
    etiquetas_nexo = ["0 piedra", "1 1 runa", "2 2 runas", "3 * horquilla", "4 oro", "5 solar", "6 * Nexo"]
    for n in range(7):
        x0 = 24 + n * 86
        y0 = 276
        nexo_p = NEXO_RUTA % n
        if os.path.exists(nexo_p):
            c_img = Image.open(nexo_p).convert("RGBA").resize((16 * 5, 21 * 5), Image.NEAREST)
            img.alpha_composite(c_img, (x0, y0))
        d.text((x0 + 28, y0 + 112), f"{n}{'*' if n in (3, 6) else ''}", font=f_sub, fill=rgb("F0CC60" if n in (3, 6) else "DCD8EC"))
        d.text((x0 + 10, y0 + 132), etiquetas_nexo[n], font=f_peq, fill=rgb("B8B2D4"))

    d.text((666, 242), "Maisha (Tierra 6 + Nexo 6)", font=f_tit, fill=rgb("F0CC60"))
    m_max = pintar_maisha_tierra(6).resize((36 * 4, 40 * 4), Image.NEAREST)
    img.alpha_composite(m_max, (694, 266))

    # 3. Propuesta de niveles (Opción A vs Opción B) + Mercado de Chuma abajo
    d.line([(22, 444), (918, 444)], fill=rgb("3A2A34"), width=2)
    d.text((22, 454), "Decision 1 · Propuesta de efectos (niveles 1..6 del Arte de la Tierra):", font=f_sub, fill=rgb("F0CC60"))
    tarjetas_tierra = [
        ("Opcion A (Recomendada): Oficio del Crater (Carga, Pulso y Escudo)",
         "1: Carga cuesta 16 Aliento · 2: +20% alcance Tierra · 3* (2 Cristales): +1 Vida y Carga hace 2 de danio",
         "4: +6 Aliento al encender/romper · 5: Carga cada 0,55 s · 6* (4 Cristales): +1 Vida + onda ambar"),
        ("Opcion B: Resistencia pasiva (mas aguante y escudo)",
         "1: Carga cuesta 16 Aliento · 2: +15 Aliento max. · 3* (2 Cristales): +1 Vida y Carga hace 2 de danio",
         "4: Escudo frena mas empuje · 5: Carga cada 0,55 s · 6* (4 Cristales): +1 Vida + onda ambar"),
    ]
    for i, (tit, l1, l2) in enumerate(tarjetas_tierra):
        oy = 478 + i * 66
        d.rounded_rectangle([22, oy, 918, oy + 60], radius=5, fill=rgb("221A24" if i == 0 else "1A151E"),
                             outline=rgb("C88430" if i == 0 else "463648"))
        d.text((34, oy + 6), tit, font=f_peq, fill=rgb("FFF0B0" if i == 0 else "D8CEDC"))
        d.text((34, oy + 24), l1, font=f_peq, fill=rgb("C8C0CC"))
        d.text((34, oy + 40), l2, font=f_peq, fill=rgb("C8C0CC"))

    d.text((22, 620), "Decision 2 · Mercado de la Escoria (Chuma · requiere mercado_escoria):", font=f_sub, fill=rgb("F0CC60"))
    items = [
        ("amolar", "Piedra amolar (4C)", "Mas empuje cetro"),
        ("fuelle", "Fuelle rescoldo (5C)", "+15% rec. Aliento"),
        ("farol", "Farol de geoda (6C)", "Luz minas / esquirlas"),
        ("delantal", "Delantal forja (8C)", "Prenda exclusiva"),
    ]
    for i, (ic, nom, sub) in enumerate(items):
        ix = 22 + i * 226
        iy = 644
        d.rounded_rectangle([ix, iy, ix + 216, iy + 54], radius=5, fill=rgb("241B22"), outline=rgb("7A5230"))
        img.alpha_composite(icono_tienda(ic).resize((12 * 3, 12 * 3), Image.NEAREST), (ix + 8, iy + 9))
        d.text((ix + 50, iy + 10), nom, font=f_peq, fill=rgb("FFF0B0"))
        d.text((ix + 50, iy + 30), sub, font=f_peq, fill=rgb("C8B8A4"))

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    img.save(SALIDA)
    print("Boceto guardado en", SALIDA)


if __name__ == "__main__":
    main()
