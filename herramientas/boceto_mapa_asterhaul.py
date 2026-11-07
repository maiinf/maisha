"""Boceto del mapa de regiones de ASTERHAUL (mundo 3), en el mismo estilo que Raíz y Sigilia.
Es un boceto de diseño para decidir con Iam, no el mapa del juego.
Sale en documentacion/boceto_mapa_asterhaul.png (1000×635)."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 635
MX0, MY0, MX1, MY1 = 20, 40, 980, 445          # el recuadro del mapa (8x6 pantallas)
FONDO = (24, 22, 20)
CREMA = (245, 230, 190)

# las regiones: (nombre, semilla x, semilla y, color)
REGIONES = [
    ("desfiladero", 230, 390, (132, 96, 78)),    # el Desfiladero del Meteorito, abajo-oeste (entrada desde Kitovu)
    ("ciudad", 490, 250, (168, 114, 64)),        # Mji-Jiwe, la Ciudad del Cráter, en el centro
    ("galerias", 200, 210, (198, 142, 48)),      # las Galerías de Ámbar, al oeste
    ("fundicion", 800, 255, (124, 62, 52)),      # la Fundición de Escoria, al este
    ("aguja", 490, 90, (62, 108, 124)),          # la Aguja Caída (peñascos flotantes), al norte
    ("risco_so", 90, 410, (92, 74, 68)),
    ("risco_se", 830, 405, (96, 68, 62)),
    ("cresta_no", 190, 70, (82, 86, 104)),
    ("cresta_ne", 800, 80, (82, 86, 104)),
]

LUGARES = {   # (x, y) del icono, nombre
    "desfiladero": ((300, 380), "Desfiladero del Meteorito"),
    "ciudad": ((490, 245), "Mji-Jiwe"),
    "galerias": ((200, 210), "Las Galerías de Ámbar"),
    "fundicion": ((790, 235), "La Fundición de Escoria"),
    "aguja": ((490, 95), "La Aguja Caída"),
}
JEFES = [
    ((140, 150), "Kifaru de Basalto"),
    ((855, 295), "Nyundo, el Gran Martillo"),
    ((650, 110), "Kipanga Astral"),
]
FINAL = (490, 308)   # El Núcleo de la Estrella, bajo el cráter central
CAMINOS = [
    [(210, 445), (255, 412), (300, 380), (390, 335), (490, 280)],
    [(490, 245), (380, 235), (290, 222), (200, 210)],
    [(490, 245), (605, 244), (700, 240), (790, 235)],
    [(490, 245), (510, 195), (480, 145), (490, 95)],
]
ESQUIRLAS = [
    (335, 305), (110, 265), (245, 125), (335, 175),
    (640, 315), (710, 180), (895, 185), (930, 360),
    (380, 70), (575, 150), (420, 370), (585, 385),
]
SECRETOS_CARGA = [(90, 110), (905, 415)]


def ruido(xs, ys, semilla):
    v = np.zeros_like(xs, dtype=float)
    for k, (f, a) in enumerate(((0.012, 1.0), (0.027, 0.5), (0.06, 0.25))):
        v += a * np.sin(xs * f * (1.3 + k * 0.4) + semilla * 1.7 + np.cos(ys * f * 1.1 + semilla))
    return v


def main():
    img = Image.new("RGB", (W, H), FONDO)
    ys, xs = np.mgrid[MY0:MY1, MX0:MX1].astype(float)
    # regiones: la semilla más cercana, con los bordes torcidos por ruido
    wx, wy = xs + ruido(xs, ys, 3) * 26, ys + ruido(ys, xs, 4) * 22
    dist = np.stack([np.hypot(wx - sx, (wy - sy) * 1.15) for _, sx, sy, _ in REGIONES])
    cual = dist.argmin(0)
    rgb = np.zeros(xs.shape + (3,), float)
    for i, (_, _, _, col) in enumerate(REGIONES):
        rgb[cual == i] = col

    # anillos concéntricos del Gran Cráter alrededor de Mji-Jiwe (490, 250)
    d_crater = np.hypot(xs - 490, (ys - 255) * 1.25)
    anillos = (np.abs(np.sin(d_crater * 0.085)) > 0.92) & (d_crater < 260)
    rgb[anillos] = rgb[anillos] * 0.82

    # textura: rayado suave y chispas de ámbar en las galerías; magnetismo turquesa en la Aguja
    raya = (np.sin((xs - ys) * 0.5) > 0.85)[..., None]
    rgb = rgb * (1 - raya * 0.07)
    nombres = [r[0] for r in REGIONES]
    es_ambar = np.isin(cual, [nombres.index("galerias"), nombres.index("ciudad")])
    motas_ambar = (np.sin(xs * 1.6) * np.sin(ys * 1.4) > 0.93) & es_ambar
    rgb[motas_ambar] = (255, 212, 96)

    es_aguja = cual == nombres.index("aguja")
    motas_mag = (np.sin(xs * 1.5) * np.cos(ys * 1.5) > 0.92) & es_aguja
    rgb[motas_mag] = (132, 236, 238)

    # el río de escoria fundida: nace en la Fundición del este y baja hacia el sureste
    rio_x = 765 + 36 * np.sin(ys * 0.024) + (ys - 120) * 0.14
    rio = (ys > 120) & (np.abs(xs - rio_x) < 9 + (ys - 120) * 0.025)
    rgb[rio] = (74, 24, 16)
    rgb[rio & (np.sin(ys * 0.35 + xs * 0.2) > 0.45)] = (238, 124, 34)
    rgb[rio & (np.sin(ys * 0.35 + xs * 0.2) > 0.82)] = (255, 224, 112)

    # cuadrícula de pantallas (8x6)
    rejilla = ((xs - MX0) % 120 < 1) | ((ys - MY0) % 67.5 < 1)
    rgb[rejilla] = rgb[rejilla] * 0.75
    img.paste(Image.fromarray(rgb.astype(np.uint8)), (MX0, MY0))

    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 14)
        fp = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana.ttf", 14)
        ft = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 15)
    except OSError:
        f = fp = ft = ImageFont.load_default()

    # vías de vagonetas / caminos principales (punteados con traviesas)
    for cam in CAMINOS:
        for (a, b) in zip(cam, cam[1:]):
            n = int(math.hypot(b[0] - a[0], b[1] - a[1]) / 9)
            for k in range(n):
                t = k / max(n, 1)
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                d.rectangle([x - 2, y - 2, x + 2, y + 2], fill=(240, 212, 156))

    # las 12 Esquirlas de Estrella (cristales de ámbar hexagonales)
    for (x, y) in ESQUIRLAS:
        d.polygon(
            [(x, y - 7), (x + 5, y - 3), (x + 5, y + 3), (x, y + 7), (x - 5, y + 3), (x - 5, y - 3)],
            fill=(255, 204, 72),
            outline=(70, 42, 14),
        )
        d.line([x, y - 4, x, y + 4], fill=(255, 246, 196), width=1)

    # secretos de Carga Sísmica (grietas estrelladas naranjas)
    for (x, y) in SECRETOS_CARGA:
        for a in range(0, 180, 45):
            dx, dy = 9 * math.cos(math.radians(a)), 9 * math.sin(math.radians(a))
            d.line([x - dx, y - dy, x + dx, y + dy], fill=(255, 168, 64), width=2)

    # los 3 jefes de camino y el jefe final en el Núcleo
    for ((x, y), _) in JEFES:
        d.polygon([(x, y - 14), (x + 11, y), (x, y + 14), (x - 11, y)], fill=(196, 108, 28), outline=(255, 232, 180))
    x, y = FINAL
    d.polygon([(x, y - 18), (x + 15, y), (x, y + 18), (x - 15, y)], fill=(212, 52, 70), outline=(255, 235, 235))

    # Mji-Jiwe (el Gran Diapasón y cráter central) y la entrada del Desfiladero
    cx, cy = LUGARES["ciudad"][0]
    d.ellipse([cx - 16, cy - 10, cx + 16, cy + 12], fill=(92, 62, 48), outline=(30, 20, 16))
    d.polygon([(cx - 10, cy + 6), (cx - 10, cy - 18), (cx - 5, cy - 22), (cx - 5, cy + 6)], fill=(60, 56, 76), outline=(24, 20, 30))
    d.polygon([(cx + 5, cy + 6), (cx + 5, cy - 22), (cx + 10, cy - 18), (cx + 10, cy + 6)], fill=(60, 56, 76), outline=(24, 20, 30))
    d.ellipse([cx - 5, cy - 16, cx + 5, cy - 6], fill=(255, 216, 92), outline=(120, 68, 12))

    px_, py_ = LUGARES["desfiladero"][0]
    d.polygon([(px_ - 8, py_ + 8), (px_, py_ - 10), (px_ + 8, py_ + 8)], fill=(250, 196, 106), outline=(60, 40, 10))

    # rótulos
    for clave, ((x, y), nombre) in LUGARES.items():
        tw = d.textlength(nombre, font=f)
        oy = 22 if clave != "aguja" else -36
        d.rectangle([x - tw / 2 - 6, y + oy - 3, x + tw / 2 + 6, y + oy + 18], fill=(20, 20, 18))
        d.text((x - tw / 2, y + oy), nombre, font=f, fill=CREMA)
    for ((x, y), nombre) in JEFES:
        tw = d.textlength(nombre, font=fp)
        d.text((x - tw / 2, y + 16), nombre, font=fp, fill=(255, 232, 196), stroke_width=2, stroke_fill=(26, 18, 14))
    tw = d.textlength("El Núcleo de la Estrella (bajo el Cráter)", font=fp)
    d.text((FINAL[0] - tw / 2, FINAL[1] + 20), "El Núcleo de la Estrella (bajo el Cráter)", font=fp, fill=(255, 220, 220), stroke_width=2, stroke_fill=(30, 10, 14))
    d.text((28, MY1 - 22), "al oeste: Kitovu (Raíz)", font=fp, fill=(235, 215, 180), stroke_width=2, stroke_fill=(24, 18, 16))
    d.text((20, 10), "ASTERHAUL — mapa de regiones (8×6 pantallas) · boceto de diseño", font=ft, fill=(240, 204, 110))

    # leyenda
    ley = [
        ((255, 216, 92), "Mji-Jiwe, la Ciudad del Cráter"),
        ((196, 108, 28), "Jefe de camino (3)"),
        ((212, 52, 70), "Jefe final: el Corazón del Meteorito"),
        ((255, 204, 72), "Esquirla de Estrella (12)"),
        ((255, 168, 64), "Secreto de Carga Sísmica (2)"),
        ((240, 212, 156), "Vía de vagonetas / camino"),
        ((238, 124, 34), "Río de escoria fundida"),
        ((62, 108, 124), "Zona magnética flotante"),
    ]
    for i, (col, txt) in enumerate(ley):
        x, y = 370 + (i // 4) * 305, 465 + (i % 4) * 30
        d.rectangle([x, y, x + 16, y + 16], fill=col, outline=(80, 80, 70))
        d.text((x + 26, y - 1), txt, font=fp, fill=CREMA)

    # recuadro: qué poder del Arte de la Tierra pide cada lugar
    d.rectangle([20, 460, 350, 600], outline=(240, 204, 110), width=1)
    for i, t in enumerate([
        "Poderes (Arte de la Tierra):",
        "Carga Sísmica · Desfiladero y Galerías",
        "Pulso Magnético · Fundición de Escoria",
        "Resonancia de Ámbar · Aguja Caída",
        "Los tres · El Núcleo de la Estrella",
    ]):
        d.text((32, 470 + i * 25), t, font=f if i == 0 else fp, fill=CREMA)

    salida = os.path.join(RAIZ, "documentacion", "boceto_mapa_asterhaul.png")
    img.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
