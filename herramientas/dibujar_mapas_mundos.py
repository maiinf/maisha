"""
MAPAS PERGAMINO DEL DIARIO: genera en arte/interfaz/ los mapas pixel art de:
  - mapa_mundo_entero.png (300×190): el mapa completo al conseguir el «Trozo del norte» (Sigilia visible).
  - mapa_sigilia.png (420×220): Paso de la Escarcha, Maandiko, Estanterías, Canal de Tinta, Observatorio y Sección Prohibida.
  - mapa_asterhaul.png (420×220): Desfiladero del Meteorito y tierras del Cráter.

Uso:  python3 herramientas/dibujar_mapas_mundos.py
"""
import math
import os
import random

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "arte", "interfaz")

PAL = {}
for linea in open(os.path.join(RAIZ, "arte", "paletas", "raiz.gpl"), encoding="utf-8"):
    p = linea.split()
    if len(p) >= 4 and p[0].isdigit():
        PAL[" ".join(p[3:])] = tuple(int(v) for v in p[:3])


def _rgb(hex_str: str) -> tuple[int, int, int, int]:
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def _c(nombre: str) -> tuple[int, int, int, int]:
    return PAL[nombre] + (255,)


def _pergamino_base(w: int, h: int, semilla: int, tinte=None) -> Image.Image:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    azar = random.Random(semilla)
    p3 = tinte[0] if tinte else _c("Pergamino 3")
    p2 = tinte[1] if tinte else _c("Pergamino 2")
    for y in range(h):
        for x in range(w):
            borde = min(x, y, w - 1 - x, h - 1 - y)
            ruido = math.sin(x * 0.29) + math.sin(y * 0.31 + x * 0.07)
            if borde < 3 + ruido:
                continue
            es_osc = borde <= 11 or azar.random() < 0.025
            if not es_osc and math.sin(x * 0.04 + semilla) * math.sin(y * 0.06) > 0.78 and azar.random() < 0.45:
                es_osc = True
            px[x, y] = p2 if es_osc else p3
    return img


def _mancha(px, w: int, h: int, cx: float, cy: float, rx: float, ry: float, col, borde, semilla: int = 0) -> None:
    margen_x = int(rx * 0.32) + 8
    margen_y = int(ry * 0.32) + 8
    for y in range(max(0, int(cy - ry - margen_y)), min(h, int(cy + ry + margen_y + 1))):
        for x in range(max(0, int(cx - rx - margen_x)), min(w, int(cx + rx + margen_x + 1))):
            ang = math.atan2(y - cy, x - cx)
            r = 1.0 + 0.14 * math.sin(ang * 3.0 + semilla) + 0.11 * math.sin(ang * 5.0 + semilla * 1.7) + 0.06 * math.cos(ang * 8.0 + semilla)
            q = ((x - cx) / max(rx * r, 0.1)) ** 2 + ((y - cy) / max(ry * r, 0.1)) ** 2
            if px[x, y][3]:
                if q <= 0.78:
                    px[x, y] = col
                elif q <= 1.0:
                    px[x, y] = borde


def _rosa_vientos(d: ImageDraw.ImageDraw, rx: int, ry: int, col_linea, col_norte) -> None:
    d.line([(rx, ry - 9), (rx, ry + 9)], fill=col_linea)
    d.line([(rx - 9, ry), (rx + 9, ry)], fill=col_linea)
    d.polygon([(rx, ry - 11), (rx - 2, ry - 5), (rx + 2, ry - 5)], fill=col_norte)


def mapa_mundo_entero() -> Image.Image:
    w, h = 300, 190
    img = _pergamino_base(w, h, 12)
    px = img.load()
    d = ImageDraw.Draw(img)
    mundos = [
        (78, 120, 52, 36, _c("Hierba 3"), _c("Hierba 1")),
        (150, 48, 52, 26, _rgb("#8b96bd"), _rgb("#3f4566")),
        (232, 110, 44, 34, _c("Flor ambar 3"), _c("Flor ambar 1")),
        (170, 160, 36, 18, _c("Giza 4"), _c("Giza 1")),
    ]
    for k, (x, y, rx, ry, col, bor) in enumerate(mundos):
        _mancha(px, w, h, x, y, rx, ry, col, bor, k * 19 + 5)
    # Nevados y cúpula del Archivo en el norte (Sigilia completa)
    for cx, cy in ((132, 46), (150, 42), (168, 49)):
        d.polygon([(cx, cy - 8), (cx - 7, cy + 4), (cx + 7, cy + 4)], fill=_rgb("#d7d5e8"), outline=_rgb("#3f4566"))
        d.polygon([(cx, cy - 8), (cx - 3, cy - 2), (cx + 3, cy - 2)], fill=_rgb("#f6f5fb"))
    d.pieslice([145, 45, 155, 55], 180, 360, fill=_rgb("#f0cc60"), outline=_c("Pergamino 1"))
    centro = (152, 108)
    for x, y, *_ in mundos:
        pasos = max(1, int(math.hypot(x - centro[0], y - centro[1]) / 3))
        for k in range(pasos):
            t = k / pasos
            if k % 2 == 0:
                d.point((centro[0] + (x - centro[0]) * t, centro[1] + (y - centro[1]) * t), fill=_c("Madera 2"))
    _mancha(px, w, h, centro[0], centro[1], 12, 8, _c("Piedra 3"), _c("Piedra 1"), 3)
    d.point(centro, fill=_c("Flor roja 2"))
    _rosa_vientos(d, 270, 30, _c("Pergamino 1"), _c("Flor roja 2"))
    return img


def mapa_sigilia() -> Image.Image:
    w, h = 420, 220
    img = _pergamino_base(w, h, 31)
    px = img.load()
    d = ImageDraw.Draw(img)
    # Costas y macizos de Sigilia
    _mancha(px, w, h, 210, 114, 158, 76, _rgb("#5a5172"), _rgb("#2e2640"), 11)
    _mancha(px, w, h, 210, 178, 86, 28, _rgb("#cfd0e6"), _rgb("#68648f"), 17)
    _mancha(px, w, h, 86, 108, 46, 36, _rgb("#6d4c36"), _rgb("#372318"), 23)
    _mancha(px, w, h, 336, 108, 48, 36, _rgb("#242246"), _rgb("#100e24"), 29)
    _mancha(px, w, h, 210, 44, 58, 28, _rgb("#3e5078"), _rgb("#1b253d"), 37)
    _mancha(px, w, h, 294, 54, 24, 18, _rgb("#3b1c48"), _rgb("#1a0c24"), 43)

    # Canal de tinta serpenteante al este
    for t in range(18):
        u = t / 17.0
        cx = int(248 + u * 102)
        cy = int(108 + math.sin(u * 3.8) * 10)
        d.ellipse([cx - 6, cy - 4, cx + 6, cy + 4], fill=_rgb("#120c1e"))
        if t % 5 == 2:
            d.rectangle([cx - 1, cy - 5, cx + 1, cy + 5], fill=_rgb("#d4a034"))

    # Paso de la Escarcha: pinos nevados
    for px0, py0 in ((176, 174), (192, 186), (228, 184), (244, 172)):
        d.polygon([(px0, py0 - 9), (px0 - 5, py0 + 2), (px0 + 5, py0 + 2)], fill=_rgb("#e6e3f2"), outline=_rgb("#4e4870"))

    # Maandiko: Gran Archivo con cúpula nervada y torres moradas
    ax, ay = 210, 114
    d.rectangle([ax - 15, ay - 3, ax + 15, ay + 9], fill=_rgb("#423856"), outline=_rgb("#1e1828"))
    d.pieslice([ax - 11, ay - 13, ax + 11, ay + 4], 180, 360, fill=_rgb("#f0cc60"), outline=_rgb("#6a4614"))
    d.line([(ax, ay - 16), (ax, ay - 13)], fill=_rgb("#fff0b0"))
    for tx, ty in ((ax - 22, ay + 4), (ax + 20, ay + 6)):
        d.rectangle([tx - 4, ty - 5, tx + 4, ty + 3], fill=_rgb("#584c6c"), outline=_rgb("#1e1828"))
        d.polygon([(tx, ty - 9), (tx - 5, ty - 5), (tx + 5, ty - 5)], fill=_rgb("#d4a034"))

    # Estanterías Colgantes: pasarelas y lomos de libros
    ex, ey = 84, 108
    for dx in (-12, 0, 12):
        d.rectangle([ex + dx - 4, ey - 10, ex + dx + 4, ey + 6], fill=_rgb("#7e6146"), outline=_rgb("#33241a"))
        d.rectangle([ex + dx - 3, ey - 8, ex + dx + 3, ey - 5], fill=_rgb("#c24854"))
    d.line([(ex - 16, ey + 8), (ex + 16, ey + 8)], fill=_rgb("#4a3626"), width=2)

    # Observatorio de la Aurora: cúpula azul y destellos de estrellas
    ox, oy = 210, 42
    d.rectangle([ox - 10, oy - 2, ox + 10, oy + 7], fill=_rgb("#4b5f88"), outline=_rgb("#1b253d"))
    d.pieslice([ox - 9, oy - 11, ox + 9, ay - 75], 180, 360, fill=_rgb("#73c2e6"), outline=_rgb("#1b253d"))
    d.line([(ox + 2, oy - 9), (ox + 10, oy - 15)], fill=_rgb("#fff0b0"), width=2)
    for sx, sy in ((ox - 24, oy - 6), (ox + 22, oy - 9), (ox - 16, oy + 10)):
        d.point((sx, sy), fill=_rgb("#fff2a8"))

    # Sección Prohibida: sello rojo/violeta
    sx, sy = 294, 54
    d.ellipse([sx - 6, sy - 6, sx + 6, sy + 6], fill=_rgb("#8b2238"), outline=_rgb("#f0cc60"))
    d.rectangle([sx - 2, sy - 2, sx + 2, sy + 2], fill=_rgb("#fff0b0"))

    _rosa_vientos(d, 388, 30, _c("Pergamino 1"), _rgb("#f0cc60"))
    return img


def mapa_asterhaul() -> Image.Image:
    w, h = 420, 220
    img = _pergamino_base(w, h, 47)
    px = img.load()
    d = ImageDraw.Draw(img)
    # Cordilleras de basalto y cráter central
    _mancha(px, w, h, 220, 108, 160, 82, _rgb("#8a5d42"), _rgb("#41271c"), 7)
    _mancha(px, w, h, 220, 108, 52, 40, _rgb("#5b4134"), _rgb("#2c1b15"), 13)
    _mancha(px, w, h, 106, 168, 52, 26, _rgb("#b27042"), _rgb("#5e351e"), 19)
    _mancha(px, w, h, 96, 86, 42, 30, _rgb("#c98b2e"), _rgb("#684110"), 23)
    _mancha(px, w, h, 334, 112, 44, 34, _rgb("#8d3a2f"), _rgb("#461814"), 29)
    _mancha(px, w, h, 220, 38, 48, 22, _rgb("#477082"), _rgb("#223a46"), 37)

    # Anillo del Gran Cráter de Mji-Jiwe
    mx, my = 220, 108
    d.ellipse([mx - 26, my - 18, mx + 26, my + 18], outline=_rgb("#2a1a14"), width=3)
    d.ellipse([mx - 20, my - 13, mx + 20, my + 13], outline=_rgb("#e6a852"), width=2)
    d.ellipse([mx - 6, my - 4, mx + 6, my + 4], fill=_rgb("#ffd878"), outline=_rgb("#7d4e18"))

    # Desfiladero del Meteorito: raíles, vagoneta y Puerta del Cráter
    dx, dy = 106, 168
    d.line([(dx - 24, dy + 12), (dx + 22, dy - 14)], fill=_rgb("#3a2820"), width=3)
    d.line([(dx - 24, dy + 12), (dx + 22, dy - 14)], fill=_rgb("#c2b8a8"), width=1)
    d.rectangle([dx - 5, dy - 4, dx + 5, dy + 4], fill=_rgb("#6a5042"), outline=_rgb("#1f1612"))
    d.rectangle([dx + 2, dy - 2, dx + 4, dy], fill=_rgb("#ffd878"))

    # Galerías de Ámbar: cristales dorados
    for gx, gy in ((86, 86), (102, 82), (96, 94)):
        d.polygon([(gx, gy - 7), (gx - 4, gy + 3), (gx + 4, gy + 3)], fill=_rgb("#f6bd4c"), outline=_rgb("#7c4912"))

    # Fundición de Escoria: chimeneas humeantes
    for fx in (324, 342):
        d.rectangle([fx - 4, 104, fx + 4, 118], fill=_rgb("#3d2b2b"), outline=_rgb("#181010"))
        d.rectangle([fx - 3, 102, fx + 3, 104], fill=_rgb("#f06b38"))

    # Aguja Caída: monolito azul astral
    ax, ay = 220, 38
    d.polygon([(ax, ay - 11), (ax - 5, ay + 6), (ax + 5, ay + 6)], fill=_rgb("#7fd0e6"), outline=_rgb("#223a46"))
    d.point((ax, ay - 4), fill=_rgb("#fff6cf"))

    _rosa_vientos(d, 388, 30, _c("Pergamino 1"), _rgb("#e6a852"))
    return img


def main() -> None:
    os.makedirs(SALIDA, exist_ok=True)
    mapa_mundo_entero().save(os.path.join(SALIDA, "mapa_mundo_entero.png"))
    mapa_sigilia().save(os.path.join(SALIDA, "mapa_sigilia.png"))
    mapa_asterhaul().save(os.path.join(SALIDA, "mapa_asterhaul.png"))
    print("Mapas generados en", SALIDA)


if __name__ == "__main__":
    main()
