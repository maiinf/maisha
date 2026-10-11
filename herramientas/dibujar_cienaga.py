"""
OBJETOS DE LA CIÉNAGA QUIETA dibujados píxel a píxel (paleta oficial de Raíz).

Uso:  python3 herramientas/dibujar_cienaga.py
Genera en arte/mundos/raiz/cienaga/:
  sauce.png          2 fotogramas de 48×58: sauces llorones (ramas que cuelgan hasta casi el agua)
  arbol_muerto.png   2 fotogramas de 32×46: árbol muerto con raíces al aire, como de manglar
  juncos.png         2 fotogramas de 16×20: juncos con espigas (adorno, se mecen)
  nenufar.png        2 fotogramas de 16×10: nenúfares sobre el agua (uno con flor)
  babosa.png         6 fotogramas de 22×14: babosa de óxido (anda 0-3, encogida 4, golpeada 5)
Y en arte/mundos/raiz/objetos/ (se recogen como las setas):
  bayas.png          2 fotogramas de 16×16: bayas del pantano (ingrediente de Juncia)
  junco.png          2 fotogramas de 16×16: junco dulce (ingrediente de Juncia)
  sopa.png           2 fotogramas de 16×16: sopa de juncos (el plato de Juncia)
"""
import math
import os
import random

from PIL import Image

from dibujar_bosque import c, contorno, tono, tronco, tira

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "arte", "mundos", "raiz", "cienaga")
OBJ = os.path.join(RAIZ, "arte", "mundos", "raiz", "objetos")

SAUCE = ["1c3530", "2b4a3a", "3f6448", "5d7e52", "8aa16a"]
SAUCE_GRIS = ["1d2a26", "2e3d36", "45574a", "647560", "8a9a7c"]
MADERA = ["251812", "492e23", "6d4534", "905c45", "a8735a"]
MUERTO = ["1f1a17", "362d27", "4f443b", "6b5f53", "8a7d6e"]
JUNCO = ["2f4422", "4d6436", "6a8246", "9aa95f", "c8c48a"]
ESPIGA = ["3f2c21", "5b3a2a", "7c5843"]
NENUFAR = ["1d3a2a", "2f5a3a", "4c7d4a", "77a35e"]
FLOR = ["e8959c", "f4c6cb", "fff3c4"]
OXIDO = ["3a1a10", "6e3218", "9c4f24", "c67238", "e09a5c"]
GIZA = ["3a1650", "6b2a8f", "a855d6", "dcaaf2"]


def sauce(semilla, w=48, h=58):
    azar = random.Random(semilla)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    cx = w // 2
    # tronco retorcido
    for y in range(30, h - 2):
        t = (y - 30) / (h - 32)
        media = 2.4 + 2.6 * t ** 2
        desv = math.sin(y * 0.25) * 1.2
        for x in range(int(cx + desv - media), int(cx + desv + media) + 1):
            u = (x - (cx + desv - media)) / max(1, 2 * media)
            col = tono(0.6 - u * 1.5, MADERA[1:5])
            if (x * 5 + y * 2) % 7 == 0:
                col = MADERA[1]
            px[x, y] = c(col)
    # copa: una cúpula redonda arriba y ramas que cuelgan en cortinas
    for y in range(4, 30):
        for x in range(4, w - 4):
            d = math.hypot((x - cx) / 19.0, (y - 17) / 12.0)
            if d <= 1.0 + azar.random() * 0.06:
                luz = (-(x - cx) / 19.0 * 0.5 - (y - 17) / 12.0 * 0.8) * 0.9 + (1 - d) * 0.3
                col = tono(luz, SAUCE, 5)
                if azar.random() < 0.1:
                    col = SAUCE[1]
                px[x, y] = c(col)
    # cortinas de hojas que cuelgan (cada una con su largo)
    for k in range(17):
        x0 = 6 + k * (w - 12) / 16 + azar.uniform(-0.6, 0.6)
        dist = abs(x0 - cx) / (w / 2)
        y0 = 17 + int(math.sqrt(max(0, 1 - dist * dist)) * 9)
        largo = int(16 + azar.random() * 14 - dist * 8)
        for j in range(largo):
            y = y0 + j
            x = int(round(x0 + math.sin(j * 0.25 + k) * 0.8))
            if 0 <= x < w and 0 <= y < h - 1:
                luz = 0.4 - j / largo * 0.9 - (x0 - cx) / w * 0.6
                px[x, y] = c(tono(luz, SAUCE, 5))
                if j % 3 == 0 and x + 1 < w:
                    px[x + 1, y] = c(tono(luz - 0.3, SAUCE, 5))
    # raíces en el barro
    for (dx, l) in ((-5, 4), (4, 3), (-2, 2), (6, 3)):
        for j in range(l):
            px[cx + dx + (j if dx > 0 else -j), h - 3 + (j // 2)] = c(MADERA[2])
    return contorno(img, "0f1a14")


def arbol_muerto(semilla):
    azar = random.Random(semilla)
    img = Image.new("RGBA", (32, 46), (0, 0, 0, 0))
    px = img.load()
    cx = 16
    # raíces al aire (arcos)
    for k, (dx, alto) in enumerate(((-9, 8), (-5, 10), (5, 9), (9, 7))):
        for j in range(12):
            t = j / 11
            x = cx + dx * t
            y = 44 - math.sin(t * math.pi) * alto * 0.4 - (1 - t) * alto
            px[int(x), int(y)] = c(MUERTO[1 + (k % 2)])
            px[int(x) + 1, int(y)] = c(MUERTO[1])
    # tronco
    for y in range(12, 36):
        media = 2.0 + (y - 12) / 24 * 1.6
        for x in range(int(cx - media), int(cx + media) + 1):
            u = (x - (cx - media)) / max(1, 2 * media)
            px[x, y] = c(tono(0.6 - u * 1.4, MUERTO[1:5]))
    # ramas secas
    for (x0, y0, dx, dy, l) in ((cx, 18, -1, -1.2, 9), (cx, 14, 1, -1.3, 8), (cx - 5, 12, -0.6, -1, 5), (cx + 6, 9, 0.8, -1, 4), (cx, 22, 1.2, -0.6, 7)):
        for j in range(l):
            x, y = int(x0 + dx * j), int(y0 + dy * j)
            if 0 <= x < 32 and 0 <= y < 46:
                px[x, y] = c(MUERTO[2] if j < l - 2 else MUERTO[3])
    # musgo colgando
    for _ in range(5):
        x, y = azar.randrange(8, 24), azar.randrange(10, 22)
        if px[x, y][3]:
            for j in range(azar.randrange(2, 5)):
                if y + j < 46:
                    px[x, y + j] = c(JUNCO[1] if j % 2 else JUNCO[2])
    return contorno(img, "0f0c0a")


def juncos(variante):
    azar = random.Random(30 + variante)
    img = Image.new("RGBA", (16, 20), (0, 0, 0, 0))
    px = img.load()
    for k in range(6 if variante == 0 else 5):
        x0 = 3 + k * 2 + azar.randint(0, 1)
        alto = azar.randint(10, 17)
        curva = azar.uniform(-0.15, 0.15)
        for j in range(alto):
            x = int(round(x0 + curva * j * j / alto))
            y = 19 - j
            px[x, y] = c(JUNCO[1 + (j * 3 // alto)] if k % 2 else JUNCO[2 + (j * 2 // alto)])
        if k % 2 == 0:
            # espiga marrón
            xt = int(round(x0 + curva * alto))
            for j in range(3):
                px[xt, 19 - alto + j] = c(ESPIGA[1 if j else 2])
            px[xt, 19 - alto - 1] = c(JUNCO[3])
    return contorno(img, "14200f")


def nenufar(con_flor):
    img = Image.new("RGBA", (16, 10), (0, 0, 0, 0))
    px = img.load()
    for (cx, cy, r) in ((5, 5, 4.2), (11, 6, 3.4)):
        for y in range(10):
            for x in range(16):
                dx, dy = (x - cx) / r, (y - cy) / (r * 0.6)
                ang = math.atan2(dy, dx)
                if dx * dx + dy * dy <= 1 and not (-0.35 < ang < 0.15):          # la muesca
                    px[x, y] = c(tono(-dx * 0.4 - dy * 0.6, NENUFAR))
    if con_flor:
        for (x, y, k) in ((5, 3, 0), (4, 3, 1), (6, 3, 1), (5, 2, 1), (5, 4, 2)):
            px[x, y] = c(FLOR[k])
    return contorno(img, "0f201a")


def babosa(f):
    """Babosa de óxido: cuerpo de herrumbre con grietas violeta y dos antenas."""
    img = Image.new("RGBA", (22, 14), (0, 0, 0, 0))
    px = img.load()
    estira = [0, 1, 2, 1, -2, 0][f]
    largo = 8 + estira
    alto = 3.6 - estira * 0.3 + (1.2 if f == 4 else 0)
    cx, base = 11, 12
    for y in range(14):
        for x in range(22):
            dx = (x - cx) / largo
            dy = (y - (base - alto)) / alto
            if dx * dx + dy * dy <= 1 and y <= base:
                luz = -dx * 0.3 - dy * 0.8
                px[x, y] = c(tono(luz, OXIDO, 5))
    # concha de herrumbre en el lomo (en espiral)
    sx, sy = cx - 1, base - alto * 1.4
    for y in range(14):
        for x in range(22):
            d = math.hypot(x - sx, (y - sy) * 1.2)
            if d <= 3.6:
                anillo = int(d * 1.3 + math.atan2(y - sy, x - sx) * 0.6) % 3
                px[x, y] = c([OXIDO[1], OXIDO[2], OXIDO[3]][anillo])
    # grietas de Giza
    for (x, y) in ((cx - 4, base - 1), (cx - 3, base - 2), (cx + 3, base - 1)):
        if 0 <= x < 22:
            px[x, y] = c(GIZA[2])
    # antenas con ojos
    if f != 4:
        hx = cx + largo - 2
        for j in range(3):
            px[hx + (j // 2), base - alto - j] = c(OXIDO[2])
        px[hx + 1, int(base - alto - 3)] = c(GIZA[3])
    img = contorno(img, "1a0c08")
    if f == 5:
        p = img.load()
        for y in range(14):
            for x in range(22):
                if p[x, y][3]:
                    p[x, y] = (255, 248, 232, 255)
    return img


def bayas(brillo):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    # hojas
    for (x, y) in ((4, 9), (5, 8), (6, 8), (10, 8), (11, 9), (9, 7), (3, 10)):
        px[x, y] = c(JUNCO[2])
    for (x, y) in ((5, 9), (10, 9), (4, 10)):
        px[x, y] = c(JUNCO[1])
    # bayas moradas brillantes
    for (cx, cy) in ((6, 11), (9, 11), (8, 13), (11, 12), (5, 13)):
        for (dx, dy, k) in ((0, 0, 1), (1, 0, 0), (0, 1, 0), (1, 1, 0)):
            px[cx + dx, cy + dy] = c(["5a2a6b", "8a4aa0", "c98ad6"][k])
        px[cx, cy] = c("c98ad6" if not brillo else "fff3c4")
    return contorno(img, "1a0c20")


def junco(brillo):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    for k in range(3):
        x0 = 6 + k * 2
        for j in range(11):
            px[x0 + (j // 6), 15 - j] = c(["9aa95f", "c8c48a", "e2d6a0"][k])
    # atado con una hebra
    for x in range(5, 12):
        px[x, 10] = c("905c45")
    if brillo:
        px[8, 6] = c("fff8e8")
        px[10, 5] = c("fff8e8")
    return contorno(img, "2a2a14")


def sopa(brillo):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    # cuenco de madera
    for y in range(8, 14):
        for x in range(2, 14):
            dx, dy = (x - 7.5) / 5.8, (y - 8) / 5.5
            if dx * dx + dy * dy <= 1 and y >= 8:
                px[x, y] = c(tono(-dx * 0.5 - dy * 0.3, MADERA[1:5]))
    # la sopa verde con un junco
    for x in range(3, 13):
        px[x, 8] = c("6a8246")
        px[x, 9] = c("9aa95f" if x % 3 else "c8c48a")
    px[11, 7] = c("c8c48a")
    px[12, 6] = c("c8c48a")
    # vapor
    if brillo:
        for (x, y) in ((6, 5), (7, 4), (6, 3), (9, 5), (10, 4)):
            px[x, y] = c("e2e2d4")
    return contorno(img, "1a1210")


def main():
    os.makedirs(DESTINO, exist_ok=True)

    def guardar(carpeta, nombre, img):
        img.save(os.path.join(carpeta, nombre + ".png"))
        print("guardado:", nombre, img.size)

    guardar(DESTINO, "sauce", tira([sauce(1), sauce(2)]))
    guardar(DESTINO, "arbol_muerto", tira([arbol_muerto(3), arbol_muerto(4)]))
    guardar(DESTINO, "juncos", tira([juncos(0), juncos(1)]))
    guardar(DESTINO, "nenufar", tira([nenufar(False), nenufar(True)]))
    guardar(DESTINO, "babosa", tira([babosa(f) for f in range(6)]))
    guardar(OBJ, "bayas", tira([bayas(False), bayas(True)]))
    guardar(OBJ, "junco", tira([junco(False), junco(True)]))
    guardar(OBJ, "sopa", tira([sopa(False), sopa(True)]))
    # iconos de la mochila: bayas (8), junco (9) y sopa (10)
    ruta_iconos = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    iconos = Image.open(ruta_iconos).convert("RGBA")
    if iconos.width < 16 * 11:
        nueva = Image.new("RGBA", (16 * 11, 16), (0, 0, 0, 0))
        nueva.alpha_composite(iconos.crop((0, 0, min(iconos.width, 16 * 8), 16)), (0, 0))
        for i, im in enumerate((bayas(False), junco(False), sopa(False))):
            nueva.alpha_composite(im, (16 * (8 + i), 0))
        nueva.save(ruta_iconos)


if __name__ == "__main__":
    main()
