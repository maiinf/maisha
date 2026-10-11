"""
EL MAPA DE RAÍZ (pergamino, píxel a píxel con la paleta de Raíz). Raíz es un mundo libre: Cuna de Musgo en el
centro y caminos con nombre propio que llevan a los demás lugares.

Uso:  python3 herramientas/dibujar_mapa_raiz.py
Genera arte/interfaz/mapa_raiz.png (420×220): el terreno y los dibujitos de cada lugar. Los CAMINOS no se
dibujan aquí: los traza el juego (con tinta) cuando Maisha los pisa, y pone NIEBLA sobre lo que aún no conoce.
Los nombres los escribe el juego. Las posiciones de los lugares y los caminos están en scripts/interfaz/mochila.gd
(LUGARES_RAIZ y CAMINOS_RAIZ) y aquí, en LUGARES: si se cambia una, hay que cambiar la otra.
"""
import math
import os
import random

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAL = {}
for linea in open(os.path.join(RAIZ, "arte", "paletas", "raiz.gpl"), encoding="utf-8"):
    p = linea.split()
    if len(p) >= 4 and p[0].isdigit():
        PAL[" ".join(p[3:])] = tuple(int(v) for v in p[:3])

W, H = 420, 220
LUGARES = {
    "prados": (105, 182), "cuna": (208, 140), "bosque": (118, 76), "cienaga": (322, 186), "embarcadero": (388, 120),
    "campo": (208, 40), "gruta": (318, 64), "lago": (40, 110), "ruinas": (384, 30),
}


def c(nombre):
    return PAL[nombre] + (255,)


def main():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    azar = random.Random(5)
    # pergamino con el borde irregular y manchas de uso
    for y in range(H):
        for x in range(W):
            borde = min(x, y, W - 1 - x, H - 1 - y)
            ruido = math.sin(x * 0.29) + math.sin(y * 0.31 + x * 0.07)
            if borde < 3 + ruido:
                continue
            tono = "Pergamino 3" if borde > 10 else "Pergamino 2"
            mancha = math.sin(x * 0.04 + 1) * math.sin(y * 0.06) > 0.78
            if azar.random() < 0.025 or mancha and azar.random() < 0.5:
                tono = "Pergamino 2"
            px[x, y] = c(tono)
    d = ImageDraw.Draw(img)

    def dentro(x, y):
        return 0 <= x < W and 0 <= y < H and px[x, y][3]

    def mancha(cx, cy, rx, ry, color, borde, semilla=0):
        for y in range(int(cy - ry - 4), int(cy + ry + 5)):
            for x in range(int(cx - rx - 4), int(cx + rx + 5)):
                ang = math.atan2(y - cy, x - cx)
                r = 1 + 0.16 * math.sin(ang * 4 + semilla) + 0.08 * math.sin(ang * 9 + semilla * 2)
                q = ((x - cx) / (rx * r)) ** 2 + ((y - cy) / (ry * r)) ** 2
                if dentro(x, y):
                    if q <= 0.84:
                        px[x, y] = c(color)
                    elif q <= 1.0:
                        px[x, y] = c(borde)

    L = LUGARES
    # --- los lugares (manchas suaves, como acuarela)
    mancha(*L["prados"], 56, 26, "Hierba 4", "Hierba 2", 1)
    mancha(*L["bosque"], 48, 30, "Follaje cobre 3", "Follaje cobre 1", 2)
    mancha(*L["campo"], 50, 22, "Flor ambar 4", "Tierra 3", 3)
    mancha(*L["gruta"], 34, 24, "Piedra 3", "Piedra 1", 4)
    mancha(*L["cienaga"], 40, 22, "Agua 3", "Agua 1", 5)
    mancha(*L["cuna"], 32, 24, "Follaje 3", "Follaje 1", 6)
    mancha(*L["lago"], 22, 26, "Hierba 3", "Hierba 2", 7)
    mancha(*L["embarcadero"], 24, 18, "Hierba 4", "Hierba 2", 8)
    mancha(*L["ruinas"], 26, 16, "Piedra 4", "Piedra 2", 9)

    def rio(puntos, ancho=2):
        for (a, b) in zip(puntos, puntos[1:]):
            pasos = int(math.hypot(b[0] - a[0], b[1] - a[1])) + 1
            for k in range(pasos):
                t = k / pasos
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                for dx in range(-ancho, ancho + 1):
                    if dentro(int(x + dx), int(y)):
                        col = "Agua 2" if abs(dx) == ancho else ("Agua 4" if dx == -1 else "Agua 3")
                        px[int(x + dx), int(y)] = c(col)

    # --- el Río Lento: baja del norte, pasa entre los prados y la aldea (bajo el puente viejo)
    rio([(170, 4), (176, 40), (166, 80), (160, 120), (166, 160), (158, 200), (162, 216)])
    # --- el río del este: de la gruta a la ciénaga, pasando por el embarcadero (la travesía en barca)
    rio([(330, 72), (352, 92), (372, 112), (376, 140), (352, 168), (340, 186)], 1)
    # --- el Lago Espejo, al oeste
    d.ellipse([L["lago"][0] - 14, L["lago"][1] - 9, L["lago"][0] + 14, L["lago"][1] + 9], fill=c("Agua 3"), outline=c("Agua 1"))
    d.ellipse([L["lago"][0] - 8, L["lago"][1] - 5, L["lago"][0] + 2, L["lago"][1] - 1], fill=c("Agua 4"))

    # --- dibujitos de cada lugar
    def arbolito(x, y, copa, tronco="Madera 2"):
        d.point((x, y), fill=c(tronco))
        d.point((x, y + 1), fill=c(tronco))
        for (dx, dy) in ((0, -1), (-1, -1), (1, -1), (0, -2), (-1, -2), (1, -2), (0, -3)):
            d.point((x + dx, y + dy), fill=c(copa))
        d.point((x - 1, y - 3), fill=c("Pergamino 1"))

    bx, by = L["bosque"]
    for _ in range(48):
        x, y = bx + azar.randint(-40, 40), by + azar.randint(-24, 24)
        if ((x - bx) / 44) ** 2 + ((y - by) / 28) ** 2 < 0.8:
            arbolito(x, y, azar.choice(["Follaje cobre 2", "Follaje rojizo 3", "Follaje rojizo 2", "Follaje cobre 1"]))
    prx, pry = L["prados"]
    for _ in range(40):
        x, y = prx + azar.randint(-50, 50), pry + azar.randint(-22, 22)
        if ((x - prx) / 54) ** 2 + ((y - pry) / 24) ** 2 < 0.75:
            d.point((x, y), fill=c(azar.choice(["Hierba 2", "Hierba 3", "Flor ambar 2", "Flor roja 3"])))
    for (x, y) in ((prx - 14, pry - 2), (prx - 8, pry - 4), (prx - 2, pry - 1)):
        d.rectangle([x, y - 4, x + 1, y], fill=c("Piedra 3"))
        d.point((x, y - 5), fill=c("Piedra 4"))
    # el Arco de Raíz (abajo a la izquierda de los prados): por ahí se vuelve al Kitovu
    ax, ay = prx - 52, pry + 18
    for k in range(13):
        a = math.pi - k / 12 * math.pi
        d.point((ax + math.cos(a) * 5, ay - math.sin(a) * 7), fill=c("Madera 2"))
    d.point((ax, ay - 7), fill=c("Flor ambar 2"))
    # el Gran Árbol de Cuna de Musgo
    gx, gy = L["cuna"][0], L["cuna"][1] + 4
    d.rectangle([gx - 2, gy - 4, gx + 2, gy + 4], fill=c("Madera 2"))
    d.rectangle([gx - 1, gy - 4, gx - 1, gy + 4], fill=c("Madera 4"))
    d.ellipse([gx - 10, gy - 18, gx + 10, gy - 2], fill=c("Follaje 2"), outline=c("Follaje 1"))
    d.ellipse([gx - 7, gy - 16, gx + 3, gy - 8], fill=c("Follaje 3"))
    for (x, y) in ((gx - 14, gy + 2), (gx + 13, gy + 3), (gx - 8, gy + 7), (gx + 9, gy + 8)):
        d.polygon([(x - 2, y), (x, y - 3), (x + 2, y)], fill=c("Flor roja 2"))                 # casitas
    # surcos y molino del Campo Segado
    cx_, cy_ = L["campo"]
    for k in range(7):
        y = cy_ - 10 + k * 3
        d.line([(cx_ - 34 + k, y), (cx_ + 30 - k, y)], fill=c("Tierra 3") if k % 2 else c("Flor ambar 3"))
    d.line([(cx_, cy_ - 14), (cx_, cy_ - 4)], fill=c("Madera 2"))
    d.line([(cx_ - 4, cy_ - 11), (cx_ + 4, cy_ - 7)], fill=c("Madera 2"))
    d.line([(cx_ - 4, cy_ - 7), (cx_ + 4, cy_ - 11)], fill=c("Madera 2"))
    # la Gruta de las Raíces: rocas oscuras con la boca de la cueva y raíces
    gx_, gy_ = L["gruta"]
    d.ellipse([gx_ - 8, gy_ - 6, gx_ + 8, gy_ + 6], fill=c("Piedra 1"))
    d.ellipse([gx_ - 5, gy_ - 3, gx_ + 5, gy_ + 6], fill=c("Extremos 1"))
    for k in range(4):
        pts = [(gx_ - 16 + k * 10 + math.sin(t * 0.7 + k) * 2, gy_ - 18 + t * 3) for t in range(8)]
        d.line(pts, fill=c("Madera 1"), width=1)
    # juncos y charcas de la Ciénaga
    ex, ey = L["cienaga"]
    for _ in range(24):
        x, y = ex + azar.randint(-32, 32), ey + azar.randint(-18, 18)
        if ((x - ex) / 36) ** 2 + ((y - ey) / 20) ** 2 < 0.8:
            d.line([(x, y), (x, y - 3)], fill=c("Hierba 2"))
            d.point((x, y - 4), fill=c("Tierra 2"))
    for (x, y, r) in ((ex - 12, ey - 6, 5), (ex + 10, ey + 6, 4)):
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=c("Agua 1"))
    # el Embarcadero Junco: un muelle de tablas y una barquita
    mx, my = L["embarcadero"]
    d.rectangle([mx - 10, my - 1, mx - 2, my + 1], fill=c("Madera 3"))
    for x in range(mx - 10, mx - 1, 3):
        d.point((x, my + 2), fill=c("Madera 1"))
    d.polygon([(mx - 2, my + 4), (mx + 8, my + 4), (mx + 6, my + 7), (mx, my + 7)], fill=c("Madera 2"))
    d.line([(mx + 3, my + 4), (mx + 3, my - 3)], fill=c("Madera 1"))
    d.polygon([(mx + 4, my - 3), (mx + 8, my + 2), (mx + 4, my + 2)], fill=c("Pergamino 1"))
    for (x, y) in ((mx + 10, my - 6), (mx - 14, my - 8), (mx + 14, my + 2)):
        d.rectangle([x, y - 3, x + 3, y], fill=c("Madera 3"))
        d.polygon([(x - 1, y - 3), (x + 1.5, y - 6), (x + 4, y - 3)], fill=c("Flor roja 2"))
    # las Ruinas del Primer Árbol: columnas rotas alrededor de la silueta de un árbol enorme (solo trazado)
    rx_, ry_ = L["ruinas"]
    for (x, y, h) in ((rx_ - 14, ry_ + 4, 6), (rx_ - 7, ry_ + 6, 3), (rx_ + 8, ry_ + 6, 5), (rx_ + 15, ry_ + 4, 4)):
        d.rectangle([x, y - h, x + 1, y], fill=c("Piedra 2"))
    d.line([(rx_, ry_ + 6), (rx_, ry_ - 6)], fill=c("Pergamino 1"))
    d.arc([rx_ - 12, ry_ - 16, rx_ + 12, ry_ - 2], 180, 360, fill=c("Pergamino 1"))
    d.point((rx_, ry_ - 9), fill=c("Flor ambar 2"))
    # relleno del paisaje: colinas, montes al norte y arboledas sueltas (lejos de los lugares y del agua)
    def libre(x, y, margen=10):
        for (lx, ly) in L.values():
            if abs(x - lx) < 44 + margen and abs(y - ly) < 26 + margen:
                return False
        return dentro(x, y) and px[x, y][:3] in (PAL["Pergamino 3"], PAL["Pergamino 2"])

    for _ in range(26):
        x, y = azar.randint(20, W - 20), azar.randint(16, H - 16)
        if libre(x, y):
            for k in range(-4, 5):                                    # colina: un arco con sombra
                yy = y - int(3.5 * math.cos(k / 4 * math.pi / 2))
                d.point((x + k, yy), fill=c("Tierra 3"))
                if k > 0:
                    d.point((x + k, yy + 1), fill=c("Pergamino 1"))
    for _ in range(40):
        x, y = azar.randint(20, W - 20), azar.randint(14, H - 14)
        if libre(x, y, 4):
            for j in range(azar.randint(2, 4)):
                arbolito(x + azar.randint(-5, 5), y + azar.randint(-3, 3), azar.choice(["Follaje 2", "Hierba 2", "Follaje 3"]))
    for k in range(9):                                                 # montes al norte, en el borde
        x = 60 + k * 30 + azar.randint(-6, 6)
        if not libre(x, 14, 0):
            continue
        d.polygon([(x - 7, 18), (x, 8), (x + 7, 18)], fill=c("Piedra 3"), outline=c("Piedra 1"))
        d.polygon([(x, 8), (x + 7, 18), (x + 2, 18)], fill=c("Piedra 2"))
        d.point((x, 9), fill=c("Pergamino 3"))

    # rosa de los vientos
    rx, ry = 398, 194
    d.line([(rx, ry - 9), (rx, ry + 9)], fill=c("Pergamino 1"))
    d.line([(rx - 9, ry), (rx + 9, ry)], fill=c("Pergamino 1"))
    d.polygon([(rx, ry - 11), (rx - 2, ry - 5), (rx + 2, ry - 5)], fill=c("Flor roja 2"))
    # firma: un brote (el mapa lo va dibujando Maisha al andar)
    fx, fy = 18, 22
    d.line([(fx, fy), (fx, fy - 5)], fill=c("Brote 1"))
    d.point((fx - 1, fy - 6), fill=c("Brote 2")); d.point((fx + 1, fy - 5), fill=c("Brote 2"))
    ruta = os.path.join(RAIZ, "arte", "interfaz", "mapa_raiz.png")
    img.save(ruta)
    print("guardado:", ruta, img.size)


if __name__ == "__main__":
    main()
