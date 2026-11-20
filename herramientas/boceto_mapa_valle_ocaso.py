"""Boceto del mapa de regiones del VALLE DEL OCASO (mundo 4, el último),
en el mismo estilo que Raíz, Sigilia y Asterhaul.
Entrada desde el sur del Kitovu, ciudad Jioni de los zorros fénec mbweha,
3 caminos (Dunas de Penumbra, Jardín de los Faroles, Calzada de los Obeliscos)
y al sur profundo El Horizonte Inmóvil (donde nace Giza).
Sale en documentacion/boceto_mapa_valle_ocaso.png (1000x645)."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 645
MX0, MY0, MX1, MY1 = 20, 40, 980, 445          # recuadro del mapa (8x6 pantallas)
FONDO = (22, 16, 28)
CREMA = (248, 232, 196)

# Regiones: (id, semilla x, semilla y, color RGB)
REGIONES = [
    ("mirador", 500, 88, (186, 110, 84)),       # 1. El Mirador del Ocaso (norte: entrada desde el sur del Kitovu)
    ("ciudad", 500, 224, (206, 132, 74)),       # Jioni, la Ciudad de los Faroles (centro)
    ("dunas", 190, 224, (148, 86, 118)),        # Camino Oeste: Las Dunas de Penumbra
    ("jardin", 815, 224, (164, 92, 92)),        # Camino Este: El Jardín de los Faroles
    ("calzada", 730, 368, (112, 74, 128)),      # Camino Sureste: La Calzada de los Obeliscos
    ("horizonte", 470, 384, (74, 34, 96)),      # Sur profundo: El Horizonte Inmóvil (donde nace Giza)
    ("risco_no", 150, 82, (104, 62, 92)),
    ("risco_ne", 855, 82, (112, 64, 88)),
    ("abismo_so", 155, 384, (58, 32, 74)),
]

LUGARES = {
    "mirador": ((500, 96), "1. El Mirador del Ocaso"),
    "ciudad": ((500, 218), "Jioni (Ciudad de los Faroles)"),
    "dunas": ((205, 218), "Las Dunas de Penumbra"),
    "jardin": ((805, 218), "El Jardín de los Faroles"),
    "calzada": ((738, 362), "La Calzada de los Obeliscos"),
}

JEFES = [
    ((128, 162), "Kivuli, Alacrán de Sombra"),
    ((888, 164), "Mondo, Polilla del Farol"),
    ((852, 398), "Saa-Mchanga, el Relojero"),
]

FINAL = (465, 388)   # El Horizonte Inmóvil (donde nace Giza)

CAMINOS = [
    [(500, 42), (500, 96), (500, 155), (500, 218)],             # Entrada norte (Kitovu) -> Mirador -> Jioni
    [(500, 218), (400, 218), (305, 218), (205, 218)],           # Jioni -> Dunas de Penumbra (Oeste)
    [(500, 218), (600, 218), (705, 218), (805, 218)],           # Jioni -> Jardín de los Faroles (Este)
    [(500, 218), (578, 266), (656, 315), (738, 362)],           # Jioni -> Calzada de los Obeliscos (Sureste)
    [(500, 218), (488, 286), (476, 340), (465, 388)],           # Jioni -> Horizonte Inmóvil (Sur, sellado hasta 3 relojes)
]

# 12 Faroles de la Hora (las 12 horas detenidas del día)
FAROLES = [
    (438, 108), (566, 114),                                     # Mirador (2)
    (286, 168), (112, 268), (275, 282),                         # Dunas (3)
    (688, 162), (892, 264), (724, 276),                         # Jardín (3)
    (636, 364), (802, 316),                                     # Calzada (2)
    (386, 344), (546, 346),                                     # Acceso al Horizonte / Jioni sur (2)
]

SECRETOS_SOL = [(92, 104), (912, 104), (118, 396)]


def ruido(xs, ys, semilla):
    v = np.zeros_like(xs, dtype=float)
    for k, (f, a) in enumerate(((0.012, 1.0), (0.027, 0.5), (0.06, 0.25))):
        v += a * np.sin(xs * f * (1.3 + k * 0.4) + semilla * 1.7 + np.cos(ys * f * 1.1 + semilla))
    return v


def main():
    img = Image.new("RGB", (W, H), FONDO)
    ys, xs = np.mgrid[MY0:MY1, MX0:MX1].astype(float)

    wx, wy = xs + ruido(xs, ys, 7) * 24, ys + ruido(ys, xs, 9) * 20
    dist = np.stack([np.hypot(wx - sx, (wy - sy) * 1.12) for _, sx, sy, _ in REGIONES])
    cual = dist.argmin(0)
    rgb = np.zeros(xs.shape + (3,), float)
    for i, (_, _, _, col) in enumerate(REGIONES):
        rgb[cual == i] = col

    # Rayos solares radiales suaves saliendo desde El Horizonte Inmóvil (sur)
    ang_h = np.arctan2(ys - 420.0, xs - 465.0)
    rayos = (np.sin(ang_h * 14.0) > 0.55) & (ys > 90)
    rgb[rayos] = np.clip(rgb[rayos] * 1.08 + np.array([12, 6, 2]), 0, 255)

    # Anillos de reloj solar alrededor de Jioni (500, 220)
    d_jioni = np.hypot(xs - 500, (ys - 220) * 1.18)
    anillos = (np.abs(np.sin(d_jioni * 0.08)) > 0.94) & (d_jioni < 190)
    rgb[anillos] = rgb[anillos] * 0.84

    # Textura de dunas onduladas en el oeste y grietas violetas de Giza en El Horizonte Inmóvil
    nombres = [r[0] for r in REGIONES]
    es_dunas = cual == nombres.index("dunas")
    ondas = (np.sin(ys * 0.24 + xs * 0.06) > 0.72) & es_dunas
    rgb[ondas] = np.clip(rgb[ondas] * 1.12 + np.array([16, 8, 6]), 0, 255)

    es_horiz = cual == nombres.index("horizonte")
    vetas = (np.abs(np.sin(xs * 0.09 + np.cos(ys * 0.08) * 3.0)) > 0.96) & es_horiz
    rgb[vetas] = np.array([196, 118, 252])

    # Cuadrícula de pantallas (8x6)
    rejilla = ((xs - MX0) % 120 < 1) | ((ys - MY0) % 67.5 < 1)
    rgb[rejilla] = rgb[rejilla] * 0.78
    img.paste(Image.fromarray(rgb.astype(np.uint8)), (MX0, MY0))

    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 13)
        fp = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana.ttf", 13)
        ft = ImageFont.truetype("/System/Library/Fonts/Supplemental/Verdana Bold.ttf", 15)
    except OSError:
        f = fp = ft = ImageFont.load_default()

    # Caminos principales (punteados dorados; el del sur hacia el Horizonte en malva-oro)
    for idx_c, cam in enumerate(CAMINOS):
        col_c = (212, 146, 250) if idx_c == 4 else (252, 220, 152)
        for (a, b) in zip(cam, cam[1:]):
            n = int(math.hypot(b[0] - a[0], b[1] - a[1]) / 9)
            for k in range(n):
                t = k / max(n, 1)
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                d.rectangle([x - 2, y - 2, x + 2, y + 2], fill=col_c)

    # 12 Faroles de la Hora (pequeños farolitos ámbar luminosos)
    for fx, fy in FAROLES:
        d.ellipse([fx - 6, fy - 6, fx + 6, fy + 6], fill=(255, 206, 102))
        d.rectangle([fx - 3, fy - 5, fx + 3, fy + 4], fill=(255, 240, 178), outline=(58, 30, 18))

    # Secretos de luz y sombra (estrellas de 8 puntas)
    for sx, sy in SECRETOS_SOL:
        for dx, dy in [(-7, 0), (7, 0), (0, -7), (0, 7), (-5, -5), (5, 5), (-5, 5), (5, -5)]:
            d.line([(sx, sy), (sx + dx, sy + dy)], fill=(255, 198, 106), width=2)

    # Icono central de Jioni (Reloj Solar dorado)
    cx, cy = LUGARES["ciudad"][0]
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(64, 30, 56), outline=(255, 214, 118), width=3)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 224, 128))
    d.line([(cx, cy), (cx + 12, cy - 8)], fill=(255, 244, 200), width=2)

    # Entrada norte desde el sur del Kitovu
    ex, ey = 500, 48
    d.polygon([(ex, ey + 10), (ex - 8, ey - 4), (ex + 8, ey - 4)], fill=(255, 216, 130), outline=(42, 22, 18))

    # Jefes de camino (rombos ámbar-cobre)
    for (jx, jy), nom in JEFES:
        d.polygon([(jx, jy - 11), (jx + 11, jy), (jx, jy + 11), (jx - 11, jy)], fill=(214, 96, 48), outline=CREMA)
        tw = d.textlength(nom, font=fp)
        bx = max(MX0 + 4, min(MX1 - tw - 12, jx - tw / 2 - 4))
        by = jy + 14
        d.rectangle([bx, by, bx + tw + 8, by + 18], fill=(24, 14, 30))
        d.text((bx + 4, by + 1), nom, fill=CREMA, font=fp)

    # Lugar donde nace Giza: El Horizonte Inmóvil (rombo púrpura-oro colosal)
    fx, fy = FINAL
    d.polygon([(fx, fy - 15), (fx + 15, fy), (fx, fy + 15), (fx - 15, fy)], fill=(176, 62, 218), outline=(255, 224, 140))
    d.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=(255, 226, 146))
    lbl_f = "El Horizonte Inmóvil (donde nace Giza)"
    twf = d.textlength(lbl_f, font=f)
    d.rectangle([fx - twf / 2 - 6, fy + 18, fx + twf / 2 + 6, fy + 38], fill=(32, 14, 44), outline=(212, 132, 248))
    d.text((fx - twf / 2, fy + 21), lbl_f, fill=(255, 226, 170), font=f)

    # Etiquetas de lugares principales
    for clave, ((lx, ly), nom) in LUGARES.items():
        tw = d.textlength(nom, font=f)
        off_y = 22 if clave == "ciudad" else 14
        bx = max(MX0 + 6, min(MX1 - tw - 16, lx - tw / 2 - 6))
        by = ly + off_y
        d.rectangle([bx, by, bx + tw + 12, by + 20], fill=(20, 14, 28), outline=(232, 182, 108))
        d.text((bx + 6, by + 2), nom, fill=CREMA, font=f)

    # Aviso de entrada norte
    ent_txt = "al norte: sur del Kitovu (Raíz · requiere Cetro del Nexo despierto)"
    twe = d.textlength(ent_txt, font=fp)
    d.rectangle([28, 46, 38 + twe, 66], fill=(24, 16, 30))
    d.text((33, 48), ent_txt, fill=(255, 220, 152), font=fp)

    # Título superior
    d.text((22, 10), "EL VALLE DEL OCASO (Mundo 4 · Final) — mapa de regiones (8×6 pantallas) · boceto para Iam",
           fill=(255, 214, 136), font=ft)

    # Leyenda inferior (2 bloques limpios)
    d.rectangle([20, 460, 480, 626], fill=(30, 20, 38), outline=(212, 166, 98))
    d.text((32, 468), "Mecánica propia · Luz y Sombra (Arte del Ocaso):", fill=(255, 216, 130), font=f)
    lineas_pod = [
        "• Relojes de Sol: giran el atardecer (Oeste / Sur / Este)",
        "• Sombras largas sólidas: puentes y caminos sobre grietas",
        "• Dunas de Penumbra: fijar sombra · Espejos de bronce",
        "• Jardín de los Faroles: apagar/encender luz · Flores nocturnas",
        "• Calzada de los Obeliscos: sombras sincronizadas + Nexo",
        "• Horizonte Inmóvil: soltar el sol para que llegue la noche",
    ]
    for i, ln in enumerate(lineas_pod):
        d.text((32, 492 + i * 21), ln, fill=CREMA, font=fp)

    # Columna derecha de iconos de leyenda
    items_ley = [
        ((255, 214, 118), "Jioni, Ciudad de los Faroles (zorros fénec mbweha)"),
        ((214, 96, 48), "Jefe de camino (3: Kivuli, Mondo y Saa-Mchanga)"),
        ((176, 62, 218), "El Horizonte Inmóvil: donde nace Giza (Jefe final)"),
        ((255, 232, 146), "12 Faroles de la Hora (devuelven el tiempo a Jioni)"),
        ((255, 198, 106), "Secretos de Luz y Sombra (3)"),
        ((252, 220, 152), "Caminos de arena crepuscular y sombras-puente"),
    ]
    for i, (col, txt) in enumerate(items_ley):
        ly = 466 + i * 26
        d.rectangle([498, ly + 2, 514, ly + 16], fill=col, outline=CREMA)
        d.text((524, ly), txt, fill=CREMA, font=fp)

    out = os.path.join(RAIZ, "documentacion", "boceto_mapa_valle_ocaso.png")
    img.save(out)
    print("Guardado:", out)


if __name__ == "__main__":
    main()
