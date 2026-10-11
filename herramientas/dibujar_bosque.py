"""
OBJETOS DEL BOSQUE COBRIZO dibujados píxel a píxel (paleta oficial de Raíz: Follaje cobre y Follaje rojizo).

Uso:  python3 herramientas/dibujar_bosque.py
Genera en arte/mundos/raiz/bosque/:
  arbol_cobre.png      2 fotogramas de 44×52: árbol de copa cobriza, ancha y baja (con alguna rama rojiza)
  arbol_rojizo.png     2 fotogramas de 44×52: árbol de copa rojiza
  arbol_alto.png       2 fotogramas de 32×72: árbol alto y estrecho (para el bosque cerrado)
  tronco_podrido.png   2 fotogramas de 34×18: tronco caído y podrido (entero · roto por una semilla)
  madera.png           2 fotogramas de 16×16: la madera suelta que deja (para recoger)
  tocon.png            24×20: tocón hueco con setas (se puede mirar)
  helecho.png          2 fotogramas de 16×14: helechos grandes (adorno sin colisión)
Todo con el mismo tamaño de píxel que el resto del juego y la luz arriba a la izquierda.
"""
import math
import os
import random

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "arte", "mundos", "raiz", "bosque")

COBRE = ["3d3214", "705425", "a37036", "c68756", "e0a874"]
ROJIZO = ["472b14", "794123", "ab5031", "cc6351", "e48a72"]
MADERA = ["251812", "492e23", "6d4534", "905c45", "a8735a"]
MUSGO = ["1d2e18", "3f582f", "6a8246", "9aa95f"]
PODRIDO = ["21170f", "3b2a1c", "5a4130", "7a5a43", "957359"]
SETA = ["7a2a1a", "b8422a", "e0683e", "f59a6a", "fff3c4"]
CONTORNO = "160d08"


def c(h, a=255):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def contorno(img, color):
    px = img.load()
    w, h = img.size
    puntos = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3]:
                        puntos.append((x, y))
                        break
    for p in puntos:
        px[p] = c(color)
    return img


def tono(luz, rampa, n=4):
    """De la luz (-1..1) a un color de la rampa (oscuro → claro)."""
    i = int(round((luz * 0.5 + 0.5) * (n - 1)))
    return rampa[max(0, min(n - 1, i))]


def tronco(px, cx, arriba, abajo, ancho_arriba, ancho_abajo, azar, raices=True):
    """Tronco con corteza en vetas, luz por la izquierda y raíces que se agarran al suelo."""
    for y in range(arriba, abajo + 1):
        t = (y - arriba) / max(1, abajo - arriba)
        media = ancho_arriba + (ancho_abajo - ancho_arriba) * t ** 2.2
        for x in range(int(cx - media), int(cx + media) + 1):
            u = (x - (cx - media)) / max(1, 2 * media)
            luz = 0.7 - u * 1.6
            col = tono(luz, MADERA[1:5])
            # vetas de corteza
            if (x * 7 + y // 3 * 3 + int(azar.random() * 1.4)) % 5 == 0 and 0.15 < u < 0.85:
                col = MADERA[1]
            px[x, y] = c(col)
    if raices:
        for lado in (-1, 1):
            for k in range(2):
                x = cx + lado * (ancho_abajo - 1)
                y = abajo - k
                for paso in range(3 + k):
                    xx = int(x + lado * paso)
                    yy = int(y + (paso // 2))
                    if 0 <= xx < 999:
                        try:
                            px[xx, yy] = c(MADERA[2] if paso < 2 else MADERA[1])
                        except IndexError:
                            pass


def copa(img, bultos, rampa_principal, rampa_toques, toques, semilla, tam_mata=3.6):
    """Copa de muchas matas de hojas: cada mata tiene su volumen y la copa entera, el suyo."""
    azar = random.Random(semilla)
    px = img.load()
    w, h = img.size
    dentro = []
    for y in range(h):
        for x in range(w):
            for (bx, by, r) in bultos:
                if math.hypot(x - bx, (y - by) * 1.08) <= r + azar.random() * 0.6:
                    dentro.append((x, y))
                    break
    if not dentro:
        return
    cx = sum(p[0] for p in dentro) / len(dentro)
    cy = sum(p[1] for p in dentro) / len(dentro)
    rx = max(abs(p[0] - cx) for p in dentro) + 1
    ry = max(abs(p[1] - cy) for p in dentro) + 1
    # centros de las matas
    matas = []
    for _ in range(int(len(dentro) / (tam_mata * tam_mata * 1.6))):
        p = azar.choice(dentro)
        matas.append((p[0] + azar.random() - 0.5, p[1] + azar.random() - 0.5, azar.random() < toques))
    for (x, y) in dentro:
        # la mata más cercana
        mejor, segunda = None, None
        for m in matas:
            d = (x - m[0]) ** 2 + (y - m[1]) ** 2
            if mejor is None or d < mejor[0]:
                segunda = mejor
                mejor = (d, m)
            elif segunda is None or d < segunda[0]:
                segunda = (d, m)
        d, (mx, my, roja) = mejor
        # volumen de la mata (luz arriba a la izquierda) + volumen de toda la copa
        nx, ny = (x - mx) / tam_mata, (y - my) / tam_mata
        gx, gy = (x - cx) / rx, (y - cy) / ry
        luz = (-nx * 0.5 - ny * 0.7) * 0.55 + (-gx * 0.5 - gy * 0.75) * 0.9
        # el borde entre matas, más oscuro (por abajo a la derecha de cada mata)
        if segunda and math.sqrt(segunda[0]) - math.sqrt(d) < 0.9 and (nx + ny) > 0:
            luz -= 0.6
        rampa = rampa_toques if roja else rampa_principal
        col = tono(luz, rampa, 4)
        if luz > 0.75 and azar.random() < 0.5:
            col = rampa[4]                      # brillo en las hojas de arriba
        px[x, y] = c(col)
    # huecos entre las hojas por donde se ve oscuro (dan aire a la copa)
    for _ in range(len(dentro) // 90):
        x, y = azar.choice(dentro)
        if (x - cx) / rx + (y - cy) / ry > 0.2:
            px[x, y] = c(rampa_principal[0])


def arbol(rampa, toques, semilla, bultos, w=40, h=56, tronco_arriba=30, ancho=(2.6, 4.6)):
    azar = random.Random(semilla)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    cx = w // 2
    tronco(px, cx, tronco_arriba, h - 3, ancho[0], ancho[1], azar)
    # una rama que asoma bajo la copa
    for k in range(5):
        x = cx + 2 + k
        y = tronco_arriba + 3 - k // 2
        px[x, y] = c(MADERA[2] if k < 3 else MADERA[1])
    copa(img, bultos, rampa, toques[0], toques[1], semilla)
    # sombra de la copa sobre el tronco
    for y in range(tronco_arriba, tronco_arriba + 3):
        for x in range(cx - 4, cx + 5):
            if px[x, y][3] and px[x, y][:3] in [c(m)[:3] for m in MADERA]:
                px[x, y] = c(MADERA[1])
    return contorno(img, CONTORNO)


def tronco_podrido(roto):
    azar = random.Random(41)
    img = Image.new("RGBA", (34, 18), (0, 0, 0, 0))
    px = img.load()
    if roto:
        # astillas y trozos de madera blanda por el suelo
        for _ in range(26):
            x, y = azar.randrange(3, 31), azar.randrange(10, 17)
            px[x, y] = c(azar.choice(PODRIDO[1:4]))
        for (x, y) in [(6, 12), (7, 12), (14, 13), (15, 13), (16, 14), (24, 12), (25, 12)]:
            px[x, y] = c(PODRIDO[3])
        return contorno(img, CONTORNO)
    # tronco tumbado: un cilindro con la corteza rota, musgo encima y el corte con anillos a la izquierda
    for y in range(3, 16):
        for x in range(4, 32):
            ny = (y - 9.5) / 6.5
            if abs(ny) > 1:
                continue
            luz = -ny * 0.9 + 0.1
            col = tono(luz, PODRIDO[0:5], 5)
            if (x * 3 + y * 5 + int(azar.random() * 3)) % 7 == 0:
                col = PODRIDO[1]
            px[x, y] = c(col)
            # musgo por arriba
            if ny < -0.55 and azar.random() < 0.75:
                px[x, y] = c(MUSGO[2] if azar.random() < 0.6 else MUSGO[3])
    # corte con anillos
    for y in range(3, 16):
        for x in range(1, 8):
            d = math.hypot((x - 4.5) / 3.2, (y - 9.5) / 6.4)
            if d <= 1:
                anillo = int(d * 4)
                px[x, y] = c(["5a4130", "7a5a43", "957359", "7a5a43"][min(3, anillo)])
                if d < 0.25:
                    px[x, y] = c("3b2a1c")       # hueco podrido en el centro
    # setas en el lomo
    for (x, y) in [(18, 3), (22, 4)]:
        px[x, y] = c(SETA[2])
        px[x + 1, y] = c(SETA[3])
        px[x, y + 1] = c("e8dcc0")
    return contorno(img, CONTORNO)


def madera(brillo):
    """Unos troncos atados: la madera que pide Tawi."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    for k, (y0, x0) in enumerate([(9, 2), (6, 4), (9, 7)]):
        for y in range(y0, y0 + 4):
            for x in range(x0, x0 + 8):
                ny = (y - y0 - 1.5) / 2
                px[x, y] = c(tono(-ny, MADERA[1:5]))
        for y in range(y0, y0 + 4):
            d = abs(y - y0 - 1.5)
            px[x0 + 7, y] = c("c49a6c" if d < 1 else "a8735a")
    # cuerda
    for y in range(6, 13):
        px[8, y] = c("e2cea0")
    if brillo:
        for (x, y) in [(3, 9), (5, 6), (12, 9)]:
            px[x, y] = c("fff3c4")
    return contorno(img, CONTORNO)


def tocon():
    azar = random.Random(77)
    img = Image.new("RGBA", (24, 20), (0, 0, 0, 0))
    px = img.load()
    # cuerpo del tocón
    for y in range(5, 18):
        for x in range(4, 20):
            u = (x - 4) / 15
            col = tono(0.7 - u * 1.6, MADERA[1:5])
            if (x * 5 + y * 3) % 6 == 0:
                col = MADERA[1]
            px[x, y] = c(col)
    # la boca hueca (arriba) y el agujero de delante
    for y in range(3, 8):
        for x in range(4, 20):
            if ((x - 11.5) / 8) ** 2 + ((y - 5) / 2.6) ** 2 <= 1:
                px[x, y] = c("957359" if ((x - 11.5) / 8) ** 2 + ((y - 5) / 2.6) ** 2 > 0.45 else "21170f")
    for y in range(11, 17):
        for x in range(9, 15):
            if ((x - 11.5) / 3) ** 2 + ((y - 14) / 3) ** 2 <= 1:
                px[x, y] = c("1a120c")
    # raíces y setas
    for (x, y) in [(2, 17), (3, 17), (20, 17), (21, 17), (3, 16), (20, 16)]:
        px[x, y] = c(MADERA[2])
    for (x, y) in [(5, 15), (17, 13), (18, 13)]:
        px[x, y] = c(SETA[2])
        px[x, y + 1] = c("e8dcc0")
    # musgo en la parte de arriba a la izquierda
    for y in range(7, 12):
        for x in range(4, 8):
            if azar.random() < 0.55:
                px[x, y] = c(azar.choice(MUSGO[1:4]))
    return contorno(img, CONTORNO)


def helecho(variante):
    azar = random.Random(90 + variante)
    img = Image.new("RGBA", (16, 14), (0, 0, 0, 0))
    px = img.load()
    hojas = [(-1.0, 7), (-0.45, 9), (0.0, 10), (0.5, 9), (1.05, 7)] if variante == 0 else [(-0.8, 8), (-0.2, 10), (0.35, 10), (0.9, 8)]
    for (ang, largo) in hojas:
        for t in range(largo):
            a = ang * (0.4 + t / largo * 0.9)
            x = 8 + math.sin(a) * t
            y = 13 - math.cos(a) * t * 1.05 + (t / largo) ** 2 * 3
            xi, yi = int(round(x)), int(round(y))
            if 0 <= xi < 16 and 0 <= yi < 14:
                px[xi, yi] = c(MUSGO[1])
            # foliolos a los lados
            for lado in (-1, 1):
                if t % 2 == 0 and t > 1:
                    fx, fy = int(round(x + lado * math.cos(a))), int(round(y + lado * math.sin(a) * 0.5))
                    if 0 <= fx < 16 and 0 <= fy < 14:
                        px[fx, fy] = c(MUSGO[2] if lado < 0 else MUSGO[1])
                        if azar.random() < 0.3:
                            px[fx, fy] = c(MUSGO[3])
    return contorno(img, "14200f")


def tira(imgs):
    w = sum(i.width for i in imgs)
    h = max(i.height for i in imgs)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for i in imgs:
        out.paste(i, (x, h - i.height))
        x += i.width
    return out


def main():
    os.makedirs(DESTINO, exist_ok=True)
    guardar = lambda nombre, img: (img.save(os.path.join(DESTINO, nombre + ".png")), print("guardado:", nombre, img.size))
    guardar("arbol_cobre", tira([
        arbol(COBRE, (ROJIZO, 0.18), 3, [(22, 21, 14), (11, 27, 9.5), (33, 27, 10), (22, 11, 10), (15, 16, 8)],
              w=44, h=52, tronco_arriba=36, ancho=(3.0, 5.0)),
        arbol(COBRE, (ROJIZO, 0.12), 4, [(20, 20, 13), (30, 22, 11), (12, 27, 9), (24, 10, 9), (33, 30, 7)],
              w=44, h=52, tronco_arriba=36, ancho=(3.0, 5.0))]))
    guardar("arbol_rojizo", tira([
        arbol(ROJIZO, (COBRE, 0.2), 5, [(22, 20, 13.5), (10, 26, 9), (33, 27, 9.5), (21, 10, 9.5), (28, 14, 8)],
              w=44, h=52, tronco_arriba=36, ancho=(3.0, 5.0)),
        arbol(ROJIZO, (COBRE, 0.15), 6, [(23, 21, 13), (13, 24, 10.5), (31, 17, 9), (19, 10, 8.5), (30, 29, 8)],
              w=44, h=52, tronco_arriba=36, ancho=(3.0, 5.0))]))
    guardar("arbol_alto", tira([
        arbol(COBRE, (ROJIZO, 0.25), 7, [(16, 16, 9), (12, 26, 8), (20, 34, 8.5), (16, 8, 6.5), (15, 41, 6)],
              w=32, h=72, tronco_arriba=44, ancho=(2.2, 3.6)),
        arbol(ROJIZO, (COBRE, 0.25), 8, [(16, 15, 8.5), (20, 25, 8), (12, 33, 8), (16, 7, 6), (17, 41, 6)],
              w=32, h=72, tronco_arriba=44, ancho=(2.2, 3.6))]))
    guardar("tronco_podrido", tira([tronco_podrido(False), tronco_podrido(True)]))
    madera_img = tira([madera(False), madera(True)])
    guardar("madera", madera_img)
    # la madera suelta se recoge como las setas y el mineral: va con los objetos de Raíz
    madera_img.save(os.path.join(RAIZ, "arte", "mundos", "raiz", "objetos", "madera.png"))
    # y su icono en la mochila (el 8.º de arte/interfaz/objetos.png)
    ruta_iconos = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    iconos = Image.open(ruta_iconos).convert("RGBA")
    if iconos.width < 16 * 8:
        nueva = Image.new("RGBA", (16 * 8, 16), (0, 0, 0, 0))
        nueva.alpha_composite(iconos.crop((0, 0, 16 * 7, 16)), (0, 0))
        nueva.alpha_composite(madera_img.crop((0, 0, 16, 16)), (16 * 7, 0))
        nueva.save(ruta_iconos)
    guardar("tocon", tocon())
    guardar("helecho", tira([helecho(0), helecho(1)]))


if __name__ == "__main__":
    main()
