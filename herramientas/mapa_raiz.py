"""
MAPA DE REGIONES DE RAÍZ (boceto de diseño, no es el mapa del juego).
8×6 pantallas = 320×135 casillas. Cada píxel del dibujo es una casilla.

Uso:  python3 herramientas/mapa_raiz.py  → documentacion/mapa_raiz.png
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

CAS_X, CAS_Y = 320, 135           # casillas
ESCALA = 3                        # píxeles del dibujo por casilla
PANT_X, PANT_Y = 40, 22.5         # casillas por pantalla

# región: (centro en pantallas, color purgado, nombre)
REGIONES = {
    "prados":   ((1.4, 4.4), "6a8246", "Prados del Eco"),
    "cuna":     ((4.0, 4.7), "9aa95f", "Cuna de Musgo"),
    "bosque":   ((1.5, 1.4), "a37036", "Bosque Cobrizo"),
    "campo":    ((4.1, 1.1), "a57559", "Campo Segado"),
    "cienaga":  ((6.5, 4.1), "355029", "Ciénaga Quieta"),
    "raices":   ((6.6, 1.2), "6d4534", "Raíces Hondas"),
}
AGUA = "4c8d8d"
AGUA_CLARA = "6db0b0"

FUENTES = "/usr/share/fonts/truetype/dejavu/"


def hexa(c, a=255):
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def gris(c):
    r, g, b, a = c
    l = 0.3 * r + 0.59 * g + 0.11 * b
    return (int(l * 0.55 + 15), int(l * 0.56 + 17), int(l * 0.58 + 20), a)


class Ruido:
    """Ruido suave (valores al azar en una rejilla, interpolados): da bordes orgánicos."""
    def __init__(self, semilla, paso):
        azar = random.Random(semilla)
        self.paso = paso
        self.v = [[azar.uniform(-1, 1) for _ in range(CAS_X // paso + 3)] for _ in range(CAS_Y // paso + 3)]

    def __call__(self, x, y):
        gx, gy = x / self.paso, y / self.paso
        ix, iy = int(gx), int(gy)
        fx, fy = gx - ix, gy - iy
        fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        a = self.v[iy][ix] * (1 - fx) + self.v[iy][ix + 1] * fx
        b = self.v[iy + 1][ix] * (1 - fx) + self.v[iy + 1][ix + 1] * fx
        return a * (1 - fy) + b * fy


def rio(y):
    """x (en casillas) del Arroyo de las Corrientes a la altura y: baja del norte al sur."""
    t = y / CAS_Y
    return 118 + 40 * t + 14 * math.sin(t * 7.0) + 6 * math.sin(t * 17.0)


RUIDO_REGION = {}


def region_de(x, y):
    """La región más cercana; cada región tiene su propio ruido para que la frontera serpentee."""
    mejor, dmin = None, 1e9
    for i, (clave, ((cx, cy), _, _)) in enumerate(REGIONES.items()):
        if clave not in RUIDO_REGION:
            RUIDO_REGION[clave] = Ruido(20 + i, 10)
        dx = (x - cx * PANT_X) / PANT_X
        dy = (y - cy * PANT_Y) / PANT_Y
        d = math.sqrt(dx * dx + dy * dy) + RUIDO_REGION[clave](x, y) * 0.28
        if d < dmin:
            mejor, dmin = clave, d
    return mejor


def dibujar_mapa(corrupto=False):
    charcas = Ruido(8, 7)
    img = Image.new("RGBA", (CAS_X, CAS_Y))
    px = img.load()
    for y in range(CAS_Y):
        for x in range(CAS_X):
            r = region_de(x, y)
            c = hexa(REGIONES[r][1])
            # textura: motas
            if (x * 7 + y * 13) % 11 == 0:
                c = tuple(max(0, v - 18) if i < 3 else v for i, v in enumerate(c))
            # agua: arroyo y charcas de la ciénaga
            if abs(x - rio(y)) < 3.2 or (r == "cienaga" and charcas(x, y) > 0.35):
                c = hexa(AGUA_CLARA if (x + y) % 9 == 0 else AGUA)
            if corrupto and r != "cuna":
                c = gris(c)
            px[x, y] = c
    return img.resize((CAS_X * ESCALA, CAS_Y * ESCALA), Image.NEAREST)


def s2p(sx, sy):
    """pantallas → píxeles del dibujo"""
    return sx * PANT_X * ESCALA, sy * PANT_Y * ESCALA


def iconos(d, f):
    # caminos principales (de puntos)
    caminos = [[(1.4, 4.4), (2.6, 4.6), (4.0, 4.7)], [(4.0, 4.7), (4.0, 3.0), (4.1, 1.1)],
               [(1.4, 4.4), (1.5, 2.8), (1.5, 1.4)], [(4.0, 4.7), (5.3, 4.4), (6.5, 4.1)],
               [(1.5, 1.4), (2.8, 1.2), (4.1, 1.1)], [(6.5, 4.1), (6.6, 2.6), (6.6, 1.2)]]
    for c in caminos:
        for (a, b) in zip(c, c[1:]):
            x0, y0 = s2p(*a)
            x1, y1 = s2p(*b)
            n = int(math.hypot(x1 - x0, y1 - y0) / 9)
            for i in range(n):
                t = i / n
                x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                d.rectangle([x - 2, y - 2, x + 2, y + 2], fill=hexa("e2cea0"))
    # zonas corruptas normales
    zonas = [(0.7, 3.8), (2.2, 5.2), (1.0, 5.3), (0.8, 2.0), (2.4, 0.7), (2.3, 2.3), (3.3, 1.9), (5.1, 0.6),
             (5.2, 2.6), (5.8, 5.3), (7.3, 3.3), (7.3, 5.0), (7.4, 0.6), (5.8, 1.8)]
    for (zx, zy) in zonas:
        x, y = s2p(zx, zy)
        d.ellipse([x - 13, y - 9, x + 13, y + 9], fill=hexa("4f5257", 230), outline=hexa("a855d6"), width=2)
    # minijefes
    for (zx, zy) in [(0.9, 0.9), (7.1, 4.2)]:
        x, y = s2p(zx, zy)
        d.polygon([(x, y - 16), (x + 13, y), (x, y + 16), (x - 13, y)], fill=hexa("6b2a8f"), outline=hexa("fff3c4"))
    # jefe
    x, y = s2p(4.1, 0.75)
    d.polygon([(x, y - 22), (x + 18, y), (x, y + 22), (x - 18, y)], fill=hexa("d53946"), outline=hexa("fff3c4"), width=2)
    # aldea
    x, y = s2p(4.0, 4.7)
    d.rectangle([x - 13, y - 4, x + 13, y + 14], fill=hexa("905c45"), outline=hexa("251812"), width=2)
    d.polygon([(x - 17, y - 3), (x, y - 18), (x + 17, y - 3)], fill=hexa("3e9a35"), outline=hexa("251812"))
    # claros de calma
    for (zx, zy) in [(3.1, 4.1), (1.9, 1.9), (6.0, 3.0), (5.3, 1.2)]:
        x, y = s2p(zx, zy)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=hexa("fff3c4"), outline=hexa("3e9a35"), width=3)
    # secretos (vuelta con habilidades de otros mundos)
    for (zx, zy, tipo) in [(7.0, 4.9, "hielo"), (6.0, 4.6, "hielo"), (7.5, 1.9, "roca"), (6.2, 0.5, "roca"), (0.4, 0.4, "estrella"), (2.9, 5.6, "estrella")]:
        x, y = s2p(zx, zy)
        if tipo == "hielo":
            for a in range(0, 180, 45):
                dx, dy = 8 * math.cos(math.radians(a)), 8 * math.sin(math.radians(a))
                d.line([(x - dx, y - dy), (x + dx, y + dy)], fill=hexa("e0ffff"), width=2)
        elif tipo == "roca":
            d.ellipse([x - 8, y - 6, x + 8, y + 6], fill=hexa("7a806d"), outline=hexa("292c25"), width=2)
        else:
            pts = []
            for k in range(10):
                r = 8 if k % 2 == 0 else 3.5
                a = math.radians(k * 36 - 90)
                pts.append((x + r * math.cos(a), y + r * math.sin(a)))
            d.polygon(pts, fill=hexa("e6a852"), outline=hexa("3d3214"))
    # inicio (despertar)
    x, y = s2p(0.9, 4.9)
    d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=hexa("ffe08a"), outline=hexa("7a4a2a"), width=2)
    # nombres de región
    for clave, ((cx, cy), _, nombre) in REGIONES.items():
        x, y = s2p(cx, cy)
        tam = d.textbbox((0, 0), nombre, font=f)
        w = tam[2] - tam[0]
        oy = 26 if clave in ("cuna", "campo") else 0
        d.rectangle([x - w / 2 - 5, y - 11 + oy, x + w / 2 + 5, y + 11 + oy], fill=(20, 22, 18, 200))
        d.text((x - w / 2, y - 9 + oy), nombre, font=f, fill=hexa("fff3c4"))
    x, y = s2p(3.35, 3.35)
    d.text((x, y), "Arroyo de las\nCorrientes", font=f, fill=hexa("e0ffff"))


if __name__ == "__main__":
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    f = ImageFont.truetype(FUENTES + "DejaVuSans-Bold.ttf", 14)
    f2 = ImageFont.truetype(FUENTES + "DejaVuSans.ttf", 14)
    mapa = dibujar_mapa()
    d = ImageDraw.Draw(mapa)
    # cuadrícula de pantallas
    for i in range(9):
        x = i * PANT_X * ESCALA
        d.line([(x, 0), (x, mapa.height)], fill=(255, 243, 196, 50))
    for j in range(7):
        y = j * PANT_Y * ESCALA
        d.line([(0, y), (mapa.width, y)], fill=(255, 243, 196, 50))
    iconos(d, f)
    inicio = dibujar_mapa(corrupto=True).resize((CAS_X, CAS_Y), Image.NEAREST)

    lienzo = Image.new("RGBA", (mapa.width + 40, mapa.height + 230), hexa("1e261a"))
    dl = ImageDraw.Draw(lienzo)
    dl.text((20, 12), "RAÍZ — mapa de regiones (8×6 pantallas, 320×135 casillas) · boceto de diseño", font=f, fill=hexa("ffe08a"))
    lienzo.alpha_composite(mapa, (20, 40))
    y0 = mapa.height + 55
    lienzo.alpha_composite(inicio, (20, y0))
    dl.rectangle([20, y0, 20 + CAS_X, y0 + CAS_Y], outline=hexa("fff3c4"))
    dl.text((20, y0 + CAS_Y + 6), "Al empezar: todo gris salvo la aldea", font=f2, fill=hexa("d6b46e"))
    leyenda = [
        ("ffe08a", "Despertar de Maisha"), ("905c45", "Aldea (con color desde el inicio)"),
        ("4f5257", "Zona corrupta (14)"), ("6b2a8f", "Minijefe (2)"), ("d53946", "Jefe: la Cosechadora Oxidada"),
        ("fff3c4", "Claro de Calma"), ("e6a852", "Secreto"),
        ("e0ffff", "Volver con hielo (Sigilia)"), ("7a806d", "Volver con Carga (Asterhaul)"),
        ("e2cea0", "Camino principal"),
    ]
    lx, ly = 20 + CAS_X + 30, y0
    for i, (c, t) in enumerate(leyenda):
        cx = lx + (i // 5) * 300
        cy = ly + (i % 5) * 30
        dl.rectangle([cx, cy + 3, cx + 16, cy + 19], fill=hexa(c), outline=hexa("fff3c4"))
        dl.text((cx + 26, cy + 2), t, font=f2, fill=hexa("fff3c4"))
    destino = os.path.join(raiz, "documentacion", "mapa_raiz.png")
    lienzo.convert("RGB").save(destino)
    print("Mapa guardado en", destino, lienzo.size)
