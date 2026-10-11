"""
PANTALLA DE INICIO dibujada píxel a píxel (paleta oficial de Raíz).

Uso:  python3 herramientas/dibujar_inicio.py
Genera en arte/interfaz/:
  inicio_fondo.png   640x360: atardecer sobre Raíz. A la izquierda el prado sigue gris;
                     a la derecha, junto al Gran Árbol, ya ha vuelto el color.
  logo_maisha.png    el título «Maisha», con un brote en lugar del punto de la i
                     (se dibuja a doble tamaño en el juego)
  cursor_hoja.png    la hojita que marca la opción elegida en los menús
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def leer_paleta():
    colores = {}
    with open(os.path.join(RAIZ, "arte", "paletas", "raiz.gpl"), encoding="utf-8") as f:
        for linea in f:
            partes = linea.split()
            if len(partes) >= 4 and partes[0].isdigit():
                colores[" ".join(partes[3:])] = tuple(int(v) for v in partes[:3])
    return colores


PAL = leer_paleta()


def c(nombre, a=255):
    return PAL[nombre] + (a,)


# Bayer 4x4 para pasar de un color a otro con tramado (sin colores nuevos)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def tramado(x, y, t):
    """True si en (x, y) toca el segundo color cuando la mezcla es t (0..1)."""
    return t * 16 > BAYER[y % 4][x % 4] + 0.5


def degradado(colores, t, x, y):
    """Elige uno de la lista de colores para la posición t (0..1), con tramado entre bandas."""
    n = len(colores) - 1
    pos = min(max(t, 0.0), 0.9999) * n
    i = int(pos)
    resto = pos - i
    # el tramado solo ocupa la parte central de cada transición: así quedan bandas limpias
    mezcla = min(max((resto - 0.55) / 0.45, 0.0), 1.0)
    return colores[i + 1] if tramado(x, y, mezcla) else colores[i]


ANCHO, ALTO = 640, 360
HORIZONTE = 236


def fondo():
    img = Image.new("RGBA", (ANCHO, ALTO), c("Extremos 1"))
    px = img.load()
    azar = random.Random(4)
    cielo = [c("Giza 1"), c("Giza 2"), c("Giza 3"), c("Flor roja 2"), c("Flor roja 3"), c("Flor ambar 3"), c("Flor ambar 4"), c("Maisha 4")]
    for y in range(HORIZONTE + 4):
        for x in range(ANCHO):
            # el cielo es más claro hacia la derecha, donde se pone el sol detrás del árbol
            t = (y / (HORIZONTE + 4)) ** 1.15 + (x / ANCHO - 0.5) * 0.08
            px[x, y] = degradado(cielo, t, x, y)
    # estrellas arriba
    for _ in range(46):
        x, y = azar.randrange(ANCHO), azar.randrange(0, 70)
        px[x, y] = c("Extremos 2") if azar.random() < 0.4 else c("Giza 4")
    # nubes: varias bolas con la base plana; el sol (abajo a la derecha) ilumina su parte baja
    for (cx, cy, largo, alto) in [(110, 96, 120, 14), (300, 58, 90, 10), (530, 112, 140, 16), (60, 152, 70, 8), (410, 168, 110, 10)]:
        bolas = []
        k = 0
        while k < largo:
            r = alto * (0.55 + 0.45 * math.sin(k / largo * math.pi)) * azar.uniform(0.8, 1.1)
            bolas.append((cx - largo // 2 + k, cy - r * 0.5, r))
            k += int(r * 0.9) + 2
        for y in range(cy - alto - 4, cy + 1):
            for x in range(cx - largo // 2 - alto, cx + largo // 2 + alto):
                if not (0 <= x < ANCHO and 0 <= y < ALTO):
                    continue
                dentro = [(bx, by, r) for (bx, by, r) in bolas if (x - bx) ** 2 + ((y - by) * 1.6) ** 2 <= r * r]
                if not dentro:
                    continue
                bajo = cy - y
                if bajo <= 1:
                    px[x, y] = c("Flor ambar 4")
                elif bajo <= 3:
                    px[x, y] = c("Flor roja 4")
                elif bajo <= alto * 0.6:
                    px[x, y] = c("Flor roja 3")
                else:
                    px[x, y] = c("Giza 4") if tramado(x, y, 0.5) else c("Flor roja 3")
    # colinas lejanas (dos capas)
    for (base, amplitud, color, semilla) in [(206, 14, c("Giza 2"), 1.3), (222, 10, c("Hierba 1"), 2.1)]:
        for x in range(ANCHO):
            alto = base - amplitud * (0.5 + 0.5 * math.sin(x * 0.012 * semilla + semilla)) - 4 * math.sin(x * 0.05 + semilla)
            for y in range(int(alto), HORIZONTE + 4):
                px[x, y] = color
    # bosque lejano: copas redondas sobre la línea del horizonte
    for _ in range(70):
        x = azar.randrange(-10, ANCHO + 10)
        r = azar.randint(5, 10)
        cy = HORIZONTE - azar.randint(0, 6)
        for yy in range(cy - r, cy + 1):
            for xx in range(x - r, x + r + 1):
                if 0 <= xx < ANCHO and (xx - x) ** 2 + ((yy - cy) * 1.2) ** 2 <= r * r:
                    px[xx, yy] = c("Follaje 1") if (xx - x) > -r * 0.3 else c("Follaje 2")
    # el prado: gris a la izquierda, verde a la derecha (el color vuelve desde el Gran Árbol)
    for y in range(HORIZONTE, ALTO):
        prof = (y - HORIZONTE) / (ALTO - HORIZONTE)
        for x in range(ANCHO):
            frontera = 250 + 30 * math.sin(y * 0.09) + 14 * math.sin(y * 0.31 + 1.0) - prof * 40
            verde = x > frontera
            if abs(x - frontera) < 10:
                verde = tramado(x, y, (x - frontera + 10) / 20)
            ruido = azar.random()
            if verde:
                base = c("Hierba 2") if prof < 0.12 else c("Hierba 3")
                if ruido < 0.06:
                    base = c("Hierba 4")
                elif ruido > 0.95:
                    base = c("Hierba 2")
            else:
                base = c("Piedra 2") if prof < 0.12 else c("Piedra 3")
                if ruido < 0.05:
                    base = c("Piedra 4")
                elif ruido > 0.95:
                    base = c("Piedra 2")
            px[x, y] = base
    # matas de hierba y flores en lo verde; piedrecitas grises en lo gris
    for _ in range(900):
        x, y = azar.randrange(ANCHO), azar.randrange(HORIZONTE + 4, ALTO - 2)
        frontera = 250 + 30 * math.sin(y * 0.09) + 14 * math.sin(y * 0.31 + 1.0) - (y - HORIZONTE) / (ALTO - HORIZONTE) * 40
        if x > frontera + 6:
            px[x, y] = c("Hierba 4")
            px[x, y + 1] = c("Hierba 2")
            if azar.random() < 0.25:
                px[x, y] = azar.choice([c("Flor ambar 3"), c("Flor roja 3"), c("Maisha 4")])
        elif x < frontera - 6 and azar.random() < 0.5:
            px[x, y] = c("Piedra 4")
            px[x, y + 1] = c("Piedra 1")
    # camino de tierra que sube hacia el árbol
    for y in range(HORIZONTE + 30, ALTO):
        t = (y - (HORIZONTE + 30)) / (ALTO - HORIZONTE - 30)
        centro = 440 - t * 70 + math.sin(y * 0.07) * 6
        ancho = 6 + t * 26
        for x in range(int(centro - ancho), int(centro + ancho)):
            if 0 <= x < ANCHO:
                borde = abs(x - centro) > ancho - 3
                px[x, y] = c("Tierra 3") if not borde else c("Tierra 2")
                if not borde and azar.random() < 0.06:
                    px[x, y] = c("Tierra 4")
    # el Gran Árbol, sobre la loma de la derecha
    arbol = Image.open(os.path.join(RAIZ, "arte", "mundos", "raiz", "aldea", "gran_arbol.png")).convert("RGBA")
    base_x, base_y = 440, HORIZONTE + 34
    # sombra bajo el árbol
    for y in range(base_y - 6, base_y + 7):
        for x in range(base_x - 80, base_x + 81):
            if ((x - base_x) / 80) ** 2 + ((y - base_y) / 6.5) ** 2 <= 1 and tramado(x, y, 0.5):
                px[x, y] = c("Hierba 1")
    img.alpha_composite(arbol, (base_x - 88, base_y - 198))
    return img


def logo():
    """«Maisha» con la letra de pixel de la interfaz, engrosada al doble, sombreada y con un brote en la i."""
    fuente = ImageFont.truetype(os.path.join(RAIZ, "fuentes", "pixelify_sans.woff"), 12)
    caja = fuente.getbbox("Maisha")
    base = Image.new("L", (caja[2] + 2, caja[3] + 2))
    d = ImageDraw.Draw(base)
    d.fontmode = "1"
    d.text((1, 1 - caja[1] + 1), "Maisha", font=fuente, fill=255)
    bp = base.load()
    w, h = base.size
    # quita el punto de la i (la parte suelta más alta de su columna) para poner el brote
    x_i = int(round(fuente.getlength("Ma"))) + 1
    columna_i = [x for x in range(x_i, x_i + 4) if any(bp[x, y] for y in range(h))]
    filas_i = [y for y in range(h) if any(bp[x, y] for x in columna_i)]
    punto = []
    for y in filas_i:
        if y + 1 in filas_i or y - 1 in filas_i or True:
            punto.append(y)
        if y + 1 not in filas_i:
            break                       # se acaba el primer trozo (el punto)
    for y in punto:
        for x in columna_i:
            bp[x, y] = 0
    centro_i = sum(columna_i) / len(columna_i)
    # al doble: trazos de 2 píxeles
    E = 2
    MARGEN = 6
    W, H = w * E + MARGEN * 2, h * E + MARGEN * 2 + 4
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    lleno = [[False] * W for _ in range(H)]
    for y in range(h):
        for x in range(w):
            if bp[x, y]:
                for dy in range(E):
                    for dx in range(E):
                        lleno[y * E + dy + MARGEN][x * E + dx + MARGEN] = True
    filas = [y for y in range(H) if any(lleno[y])]
    arriba, abajo = min(filas), max(filas)
    # sombra (abajo, 2 píxeles), contorno y relleno con tres tonos de arriba abajo
    for y in range(H):
        for x in range(W):
            if lleno[y][x]:
                continue
            for dy in (2, 3):
                if 0 <= y - dy < H and lleno[y - dy][x]:
                    px[x, y] = c("Extremos 1")
    for y in range(H):
        for x in range(W):
            if lleno[y][x]:
                continue
            if any(0 <= y + dy < H and 0 <= x + dx < W and lleno[y + dy][x + dx]
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                px[x, y] = c("Maisha 1")
    for y in range(H):
        for x in range(W):
            if lleno[y][x]:
                t = (y - arriba) / max(1, abajo - arriba)
                px[x, y] = c("Maisha 4") if t < 0.3 else (c("Maisha 3") if t < 0.72 else c("Maisha 2"))
                # brillo en el borde de arriba de cada trazo
                if y > 0 and not lleno[y - 1][x] and t < 0.6:
                    px[x, y] = c("Extremos 2")
    # el brote sobre la i: tallo y dos hojas
    bx = int(round(centro_i * E + MARGEN))
    top = arriba + (filas_i[len(punto)] if len(punto) < len(filas_i) else 4) * 0 + 0
    tallo_base = min(y for y in range(H) if lleno[y][bx]) - 3     # un hueco, como el del punto de la i
    for k in range(4):
        px[bx, tallo_base - k] = c("Brote 1")
    hojas = [(-1, -4), (-2, -5), (-3, -5), (-3, -6), (-4, -6), (-2, -6),   # hoja izquierda
             (1, -5), (2, -6), (3, -6), (3, -7), (4, -7), (2, -7), (1, -6)]  # hoja derecha
    for (dx, dy) in hojas:
        px[bx + dx, tallo_base + dy] = c("Brote 2") if dy <= -6 else c("Brote 1")
    # contorno del brote
    verdes = {(x, y) for y in range(H) for x in range(W) if px[x, y][:3] in (PAL["Brote 1"], PAL["Brote 2"])}
    for (x, y) in verdes:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if 0 <= q[0] < W and 0 <= q[1] < H and px[q][3] == 0:
                px[q] = c("Follaje 1")
    return img.crop(img.getbbox())


def cursor_hoja():
    img = Image.new("RGBA", (9, 8), (0, 0, 0, 0))
    px = img.load()
    hoja = ["...####..", "..######.", ".#######.", "########.", ".######..", "..####...", ".#.......", "#........"]
    for y, fila in enumerate(hoja):
        for x, ch in enumerate(fila):
            if ch == "#":
                px[x, y] = c("Brote 2") if (x + y) < 7 else c("Brote 1")
    px[6, 0] = c("Maisha 4")
    for (x, y) in [(1, 6), (0, 7)]:
        px[x, y] = c("Follaje 2")
    return img


if __name__ == "__main__":
    destino = os.path.join(RAIZ, "arte", "interfaz")
    os.makedirs(destino, exist_ok=True)
    fondo().save(os.path.join(destino, "inicio_fondo.png"))
    logo().save(os.path.join(destino, "logo_maisha.png"))
    cursor_hoja().save(os.path.join(destino, "cursor_hoja.png"))
    print("Pantalla de inicio dibujada en", destino)
