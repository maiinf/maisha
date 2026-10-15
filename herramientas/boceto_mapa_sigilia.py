"""Boceto del mapa de regiones de SIGILIA (mundo 2), en el mismo estilo que el de Raíz (documentacion/mapa_raiz.png).
Es un boceto de diseño para decidir con Iam, no el mapa del juego.
Sale en documentacion/boceto_mapa_sigilia.png (1000×635)."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1000, 635
MX0, MY0, MX1, MY1 = 20, 40, 980, 445          # el recuadro del mapa
FONDO = (24, 26, 22)
CREMA = (245, 230, 190)

# las regiones: (nombre, semilla x, semilla y, color)
REGIONES = [
    ("paso", 470, 400, (196, 200, 222)),        # el paso de nieve, abajo
    ("ciudad", 480, 250, (122, 92, 150)),       # Maandiko, en el centro
    ("estanterias", 190, 220, (150, 104, 70)),  # la biblioteca colgante, al oeste
    ("canal", 790, 250, (54, 46, 92)),          # el canal de tinta, al este
    ("observatorio", 470, 90, (70, 96, 130)),   # el observatorio en la cumbre, al norte
    ("monte_o", 160, 380, (150, 150, 176)),
    ("monte_e", 820, 400, (150, 150, 176)),
    ("cumbre_o", 200, 70, (110, 120, 150)),
    ("cumbre_e", 790, 80, (110, 120, 150)),
]

LUGARES = {   # (x, y) del icono, nombre
    "paso": ((470, 395), "Paso de la Escarcha"),
    "ciudad": ((480, 255), "Maandiko"),
    "estanterias": ((200, 210), "Las Estanterías Colgantes"),
    "canal": ((790, 235), "El Canal de Tinta"),
    "observatorio": ((480, 95), "El Observatorio de la Aurora"),
}
JEFES = [((150, 165), "Bibliotecario Hueco"), ((850, 300), "Pweza"), ((640, 120), "Kengele")]
FINAL = (480, 300)   # la Sección Prohibida, bajo el Archivo
CAMINOS = [
    [(470, 445), (450, 420), (470, 395), (490, 360), (480, 290)],
    [(480, 255), (380, 240), (290, 225), (200, 210)],
    [(480, 255), (600, 250), (700, 240), (790, 235)],
    [(480, 255), (500, 200), (470, 150), (480, 95)],
]
FICHAS = [(300, 300), (120, 260), (240, 130), (330, 170), (620, 300), (700, 180), (880, 180), (920, 330),
          (380, 70), (610, 130), (420, 330), (560, 380)]
NIEVE_SECRETOS = [(90, 110), (900, 420)]


def ruido(xs, ys, semilla):
    v = np.zeros_like(xs, dtype=float)
    for k, (f, a) in enumerate(((0.012, 1.0), (0.027, 0.5), (0.06, 0.25))):
        v += a * np.sin(xs * f * (1.3 + k * 0.4) + semilla * 1.7 + np.cos(ys * f * 1.1 + semilla))
    return v


def main():
    img = Image.new("RGB", (W, H), FONDO)
    ys, xs = np.mgrid[MY0:MY1, MX0:MX1].astype(float)
    # regiones: la semilla más cercana, con los bordes torcidos por ruido
    wx, wy = xs + ruido(xs, ys, 1) * 26, ys + ruido(ys, xs, 2) * 22
    dist = np.stack([np.hypot(wx - sx, (wy - sy) * 1.15) for _, sx, sy, _ in REGIONES])
    cual = dist.argmin(0)
    rgb = np.zeros(xs.shape + (3,), float)
    for i, (_, _, _, col) in enumerate(REGIONES):
        rgb[cual == i] = col
    # textura: rayado suave y motas de nieve en las montañas; tinta oscura en el canal
    raya = (np.sin((xs + ys) * 0.5) > 0.85)[..., None]
    rgb = rgb * (1 - raya * 0.07)
    nombres = [r[0] for r in REGIONES]
    monte = np.isin(cual, [nombres.index(n) for n in ("monte_o", "monte_e", "cumbre_o", "cumbre_e", "paso")])
    motas = (np.sin(xs * 1.7) * np.sin(ys * 1.3) > 0.92) & monte
    rgb[motas] = (236, 236, 248)
    # el río de tinta: baja del norte por el este hasta salir abajo a la derecha
    rio_x = 760 + 40 * np.sin(ys * 0.02) + (ys - 40) * 0.12
    rio = np.abs(xs - rio_x) < 10 + (ys - 40) * 0.02
    rgb[rio] = (28, 22, 52)
    rgb[rio & (np.sin(ys * 0.4 + xs * 0.2) > 0.8)] = (120, 100, 190)
    # cuadrícula de pantallas
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
    # los caminos (punteados)
    for cam in CAMINOS:
        for (a, b) in zip(cam, cam[1:]):
            n = int(math.hypot(b[0] - a[0], b[1] - a[1]) / 9)
            for k in range(n):
                t = k / max(n, 1)
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                d.rectangle([x - 2, y - 2, x + 2, y + 2], fill=(232, 214, 168))
    # las fichas del Índice, los secretos de hielo, los jefes y el final
    for (x, y) in FICHAS:
        d.rectangle([x - 5, y - 6, x + 5, y + 6], fill=(244, 236, 216), outline=(90, 70, 110), width=2)
        d.line([x - 2, y - 2, x + 2, y - 2], fill=(90, 70, 110))
        d.line([x - 2, y + 1, x + 2, y + 1], fill=(90, 70, 110))
    for (x, y) in NIEVE_SECRETOS:
        for a in range(0, 180, 45):
            dx, dy = 9 * math.cos(math.radians(a)), 9 * math.sin(math.radians(a))
            d.line([x - dx, y - dy, x + dx, y + dy], fill=(240, 250, 255), width=2)
    for ((x, y), _) in JEFES:
        d.polygon([(x, y - 14), (x + 11, y), (x, y + 14), (x - 11, y)], fill=(112, 52, 160), outline=(220, 190, 240))
    x, y = FINAL
    d.polygon([(x, y - 18), (x + 15, y), (x, y + 18), (x - 15, y)], fill=(212, 52, 70), outline=(255, 235, 235))
    # la ciudad (cúpula dorada) y la puerta del paso
    cx, cy = LUGARES["ciudad"][0]
    d.rectangle([cx - 14, cy - 6, cx + 14, cy + 12], fill=(90, 58, 120), outline=(30, 20, 40))
    d.pieslice([cx - 14, cy - 22, cx + 14, cy + 8], 180, 360, fill=(240, 204, 96), outline=(60, 40, 10))
    px_, py_ = LUGARES["paso"][0]
    d.polygon([(px_ - 8, py_ + 8), (px_, py_ - 10), (px_ + 8, py_ + 8)], fill=(250, 196, 106), outline=(60, 40, 10))
    # rótulos
    for clave, ((x, y), nombre) in LUGARES.items():
        tw = d.textlength(nombre, font=f)
        oy = 22 if clave != "observatorio" else -36
        d.rectangle([x - tw / 2 - 6, y + oy - 3, x + tw / 2 + 6, y + oy + 18], fill=(20, 20, 18))
        d.text((x - tw / 2, y + oy), nombre, font=f, fill=CREMA)
    for ((x, y), nombre) in JEFES:
        tw = d.textlength(nombre, font=fp)
        d.text((x - tw / 2, y + 16), nombre, font=fp, fill=(236, 220, 250), stroke_width=2, stroke_fill=(20, 16, 26))
    tw = d.textlength("Sección Prohibida (bajo el Archivo)", font=fp)
    d.text((FINAL[0] - tw / 2, FINAL[1] + 20), "Sección Prohibida (bajo el Archivo)", font=fp, fill=(255, 220, 220), stroke_width=2, stroke_fill=(30, 10, 14))
    d.text((565, MY1 - 22), "bajando: las Ruinas (Raíz)", font=fp, fill=(30, 26, 40))
    d.text((20, 10), "SIGILIA — mapa de regiones (8×6 pantallas) · boceto de diseño", font=ft, fill=(240, 220, 140))
    # leyenda
    ley = [((240, 204, 96), "Maandiko, la Ciudad-Archivo"), ((112, 52, 160), "Jefe de camino (3)"),
           ((212, 52, 70), "Jefe final: el Grimorio de Tinta"), ((244, 236, 216), "Ficha del Índice (12)"),
           ((240, 250, 255), "Secreto con hielo (2)"), ((232, 214, 168), "Camino principal"),
           ((28, 22, 52), "El Canal de Tinta"), ((196, 200, 222), "Nieve del paso")]
    for i, (col, txt) in enumerate(ley):
        x, y = 370 + (i // 4) * 300, 465 + (i % 4) * 30
        d.rectangle([x, y, x + 16, y + 16], fill=col, outline=(80, 80, 70))
        d.text((x + 26, y - 1), txt, font=fp, fill=CREMA)
    # recuadro: qué sigilo pide cada lugar
    d.rectangle([20, 460, 340, 600], outline=(240, 220, 140), width=1)
    for i, t in enumerate(["Sigilos (arte Runa):", "Fuego · Paso y Estanterías", "Hielo · Canal de Tinta",
                           "Rayo · Observatorio", "Los tres · Sección Prohibida"]):
        d.text((32, 470 + i * 25), t, font=f if i == 0 else fp, fill=CREMA)
    salida = os.path.join(RAIZ, "documentacion", "boceto_mapa_sigilia.png")
    img.save(salida)
    print("hecho", salida)


if __name__ == "__main__":
    main()
