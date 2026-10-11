"""
OBJETOS DE RAÍZ dibujados píxel a píxel (paleta oficial de Raíz).
Nivel de detalle «básico pero vivo» para la primera región (Prados del Eco).

Uso:  python3 herramientas/dibujar_raiz.py
Genera en arte/mundos/raiz/objetos/:
  arbol_a.png, arbol_b.png     árboles (32x40), con el tronco abajo en el centro
  roca_grande.png, roca_pequena.png
  matorral.png                 se rompe con una semilla (2 fotogramas: entero, roto)
  columna.png, muro.png        ruinas de piedra
  piedra_eco.png               2 fotogramas: apagada, encendida
  esencia.png                  secreto: 2 fotogramas de brillo
  cartel.png
  mariposa.png                 4 fotogramas: 2 colores x (alas abiertas, cerradas)
  seta_luminosa.png            encargo de Pino: 2 fotogramas de brillo
  roca_mineral.png             roca con cristales de mineral: 2 fotogramas (entera, rota)
  mineral.png                  el mineral suelto, para recoger: 2 fotogramas de brillo
"""
import math
import os
import random
from PIL import Image

PALETA = {
    # Follaje
    "F1": "152814", "F2": "355029", "F3": "5D793E", "F4": "90A153",
    # Madera
    "M1": "251812", "M2": "492E23", "M3": "6D4534", "M4": "905C45",
    # Piedra
    "P1": "292C25", "P2": "525649", "P3": "7A806D", "P4": "A0A596",
    # Hierba (musgo sobre piedra)
    "H2": "3F582F", "H3": "6A8246", "H4": "9AA95F",
    # Flores, ámbar y luz
    "R2": "D53946", "R3": "DE6771", "A2": "DF9022", "A3": "E6A852", "A4": "EDC082",
    "L": "FFF3C4", "W": "FFF8E8",
    # Brote
    "B1": "3E9A35", "B2": "6FCF4F",
    # Agua (brillo de las setas luminosas), Pergamino y ámbar oscuro
    "G1": "1C3535", "G2": "346161", "G3": "4C8D8D", "G4": "6DB0B0",
    "N1": "5C3E26", "N2": "C9B07E", "N3": "E2CEA0", "A1": "B27219",
}


def rgba(clave, a=255):
    c = PALETA[clave]
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def contorno(img, color):
    """Añade un contorno de 1 píxel alrededor de lo dibujado (solo hacia fuera)."""
    px = img.load()
    w, h = img.size
    puntos = []
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] and px[nx, ny] != color:
                        puntos.append((x, y))
                        break
    for p in puntos:
        px[p] = color
    return img


def sombreado(nx, ny, tonos):
    """Elige tono según la normal aproximada (luz arriba a la izquierda). tonos: de oscuro a claro."""
    luz = -nx * 0.6 - ny * 0.8
    if luz > 0.45:
        return tonos[3]
    if luz > 0.0:
        return tonos[2]
    if luz > -0.5:
        return tonos[1]
    return tonos[0]


def arbol(semilla, bultos):
    azar = random.Random(semilla)
    img = Image.new("RGBA", (32, 40), (0, 0, 0, 0))
    px = img.load()
    # tronco
    for y in range(24, 38):
        ancho = 3 if y < 34 else 4 + (y - 34) // 2
        for x in range(16 - ancho, 16 + ancho):
            t = (x - (16 - ancho)) / (2 * ancho)
            px[x, y] = rgba("M4" if t < 0.3 else ("M3" if t < 0.75 else "M2"))
    # copa: varios bultos redondos
    for y in range(32):
        for x in range(32):
            mejor = None
            for (cx, cy, r) in bultos:
                d = math.hypot(x - cx, (y - cy) * 1.05)
                if d <= r:
                    n = ((x - cx) / r, (y - cy) / r)
                    if mejor is None or d / r < mejor[0]:
                        mejor = (d / r, n)
            if mejor:
                nx, ny = mejor[1]
                tono = sombreado(nx, ny, ("F1", "F2", "F3", "F4"))
                # textura de hojas: algunas manchas
                if azar.random() < 0.12:
                    tono = {"F4": "F3", "F3": "F2", "F2": "F3", "F1": "F2"}[tono]
                px[x, y] = rgba(tono)
    return contorno(img, rgba("F1"))


def roca(ancho, alto, musgo=True, semilla=1):
    azar = random.Random(semilla)
    img = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    px = img.load()
    cx, cy = (ancho - 1) / 2, alto * 0.62
    rx, ry = ancho / 2 - 1, alto * 0.6
    for y in range(alto):
        for x in range(ancho):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny <= 1.0 and y < alto - 1:
                tono = sombreado(nx, ny, ("P1", "P2", "P3", "P4"))
                if musgo and ny < -0.45 and azar.random() < 0.7:
                    tono = "H3" if nx < 0.2 else "H2"
                px[x, y] = rgba(tono)
    return contorno(img, rgba("P1"))


def matorral(roto=False):
    azar = random.Random(7)
    img = Image.new("RGBA", (16, 14), (0, 0, 0, 0))
    px = img.load()
    if roto:
        # ramitas sueltas y hojas por el suelo
        for (x, y) in [(3, 11), (5, 12), (8, 12), (11, 11), (12, 12), (6, 10), (9, 10)]:
            px[x, y] = rgba("M3")
        for (x, y) in [(2, 12), (7, 11), (10, 12), (13, 11), (4, 10)]:
            px[x, y] = rgba("F3")
        return img
    bultos = [(5, 8, 5), (10, 7, 5.5), (8, 5, 4.5)]
    for y in range(14):
        for x in range(16):
            for (cx, cy, r) in bultos:
                if math.hypot(x - cx, y - cy) <= r and y < 13:
                    nx, ny = (x - 8) / 7, (y - 7) / 6
                    tono = sombreado(nx, ny, ("F1", "F2", "F3", "F4"))
                    if azar.random() < 0.15:
                        tono = "F2"
                    px[x, y] = rgba(tono)
                    break
    # unas bayas rojas
    for (x, y) in [(6, 6), (11, 9)]:
        px[x, y] = rgba("R3")
    return contorno(img, rgba("F1"))


def columna():
    img = Image.new("RGBA", (12, 30), (0, 0, 0, 0))
    px = img.load()
    for y in range(4, 29):
        for x in range(2, 10):
            if y < 7 and x > 7 - (y - 4):   # parte superior rota en diagonal
                continue
            t = (x - 2) / 8
            tono = "P4" if t < 0.25 else ("P3" if t < 0.7 else "P2")
            if y in (10, 19) and x % 3 != 0:
                tono = "P2"        # juntas de los bloques
            px[x, y] = rgba(tono)
    for y in range(26, 29):
        for x in range(1, 11):
            px[x, y] = rgba("P3" if x < 6 else "P2")
    for (x, y) in [(4, 13), (5, 14), (5, 15), (6, 16), (7, 22), (6, 23)]:
        px[x, y] = rgba("P1")   # grietas
    for (x, y) in [(3, 7), (2, 8), (3, 9), (9, 25), (8, 24)]:
        px[x, y] = rgba("H3")   # musgo
    return contorno(img, rgba("P1"))


def muro():
    img = Image.new("RGBA", (24, 12), (0, 0, 0, 0))
    px = img.load()
    for y in range(2, 11):
        for x in range(1, 23):
            if y < 4 and (x < 5 or x > 17):
                continue
            tono = "P3" if y < 6 else "P2"
            if y == 6 or (x in (6, 12, 18) and y > 6) or (x in (9, 15) and y < 6):
                tono = "P1"
            if y < 4:
                tono = "P4"
            px[x, y] = rgba(tono)
    for (x, y) in [(7, 4), (8, 4), (14, 3), (20, 6)]:
        px[x, y] = rgba("H3")
    return contorno(img, rgba("P1"))


def piedra_eco(encendida):
    img = Image.new("RGBA", (12, 18), (0, 0, 0, 0))
    px = img.load()
    for y in range(1, 17):
        for x in range(1, 11):
            nx = (x - 5.5) / 5
            ny = (y - 8) / 9
            if nx * nx * 1.2 + max(0, -ny) ** 2 * 2.5 <= 1.0:
                px[x, y] = rgba(sombreado(nx, ny * 0.6, ("P1", "P2", "P3", "P4")))
    # runa en espiral
    runa = [(5, 5), (6, 5), (7, 6), (7, 7), (6, 8), (5, 8), (4, 7), (4, 6), (5, 10), (6, 11), (5, 12)]
    for i, p in enumerate(runa):
        px[p] = rgba(("W" if i % 4 == 0 else "A3") if encendida else "P1")
    return contorno(img, rgba("P1"))


def esencia(brillo):
    img = Image.new("RGBA", (9, 9), (0, 0, 0, 0))
    px = img.load()
    for y in range(9):
        for x in range(9):
            d = math.hypot(x - 4, y - 4)
            if d <= 2.2:
                px[x, y] = rgba("W" if d < 1.2 else "A4")
            elif d <= 3.2 + brillo * 0.8 and (x + y) % 2 == 0:
                px[x, y] = rgba("A3", 200)
    return img


def cartel():
    img = Image.new("RGBA", (14, 16), (0, 0, 0, 0))
    px = img.load()
    for y in range(8, 16):
        for x in (6, 7):
            px[x, y] = rgba("M3" if x == 6 else "M2")
    for y in range(1, 9):
        for x in range(1, 13):
            px[x, y] = rgba("M4" if y < 3 else "M3")
    for x in range(3, 11, 2):
        px[x, 5] = rgba("M1")     # «letras»
    return contorno(img, rgba("M1"))


def mariposa():
    fotos = []
    for color in ("R3", "A3"):
        for abierta in (True, False):
            img = Image.new("RGBA", (5, 4), (0, 0, 0, 0))
            px = img.load()
            px[2, 1] = rgba("M1")
            px[2, 2] = rgba("M1")
            if abierta:
                for p in [(0, 0), (1, 1), (0, 1), (4, 0), (3, 1), (4, 1), (1, 2), (3, 2)]:
                    px[p] = rgba(color)
            else:
                for p in [(1, 0), (1, 1), (3, 0), (3, 1)]:
                    px[p] = rgba(color)
            fotos.append(img)
    return fotos


def seta_luminosa(brillo):
    """Seta de luz fría (agua) con motas que brillan; la 2ª imagen brilla más."""
    img = Image.new("RGBA", (12, 14), (0, 0, 0, 0))
    px = img.load()
    # pie
    for y in range(7, 13):
        for x in (5, 6):
            px[x, y] = rgba("N3" if x == 5 else "N2")
    px[4, 12] = rgba("N2"); px[7, 12] = rgba("N2")
    # sombrero
    for y in range(2, 8):
        for x in range(1, 11):
            nx, ny = (x - 5.5) / 5.0, (y - 7.0) / 5.0
            if nx * nx + ny * ny <= 1.0 and y <= 7:
                tono = "G4" if (nx < -0.1 and ny < -0.45) else ("G3" if ny < -0.15 else "G2")
                px[x, y] = rgba(tono)
    for x in range(2, 10):
        px[x, 7] = rgba("G1")
    # motas de luz
    for (x, y) in [(3, 4), (6, 3), (8, 5)]:
        px[x, y] = rgba("W" if brillo else "L")
    img = contorno(img, rgba("G1"))
    if brillo:
        # destellos alrededor
        for (x, y) in [(0, 2), (11, 4), (1, 9)]:
            px[x, y] = rgba("G4")
    return img


def cristal(px, cx, base, alto, inclina=0, tam=(20, 18)):
    """Cristal de mineral: prisma de 3 píxeles de ancho con la punta arriba y contorno ámbar oscuro."""
    puntos = {}
    for k in range(alto):
        y = base - k
        x0 = cx + (inclina * k) // 4
        if k == alto - 1:
            puntos[(x0, y)] = "L"
        else:
            puntos[(x0 - 1, y)] = "A4"
            puntos[(x0, y)] = "A3"
            puntos[(x0 + 1, y)] = "A2"
    dentro = lambda x, y: 0 <= x < tam[0] and 0 <= y < tam[1]   # (ojo: PIL da la vuelta con índices negativos)
    for (x, y) in list(puntos):
        for dx, dy in ((1, 0), (-1, 0), (0, -1)):
            q = (x + dx, y + dy)
            if q not in puntos and dentro(*q):
                px[q] = rgba("A1")
    for (x, y), c in puntos.items():
        if dentro(x, y):
            px[x, y] = rgba(c)
    px[cx - 1, base - alto // 2] = rgba("W")


def roca_mineral(rota):
    """Roca con cristales de mineral ámbar. Rota: escombros (el mineral ya ha salido)."""
    if rota:
        img = Image.new("RGBA", (20, 18), (0, 0, 0, 0))
        px = img.load()
        azar = random.Random(6)
        for _ in range(9):
            cx, cy = azar.randint(2, 17), azar.randint(12, 16)
            for dx in range(-1, 2):
                for dy in range(0, 2):
                    if 0 <= cx + dx < 20 and 0 <= cy + dy < 18:
                        px[cx + dx, cy + dy] = rgba("P3" if dy == 0 else "P2")
        return contorno(img, rgba("P1"))
    img = Image.new("RGBA", (20, 18), (0, 0, 0, 0))
    img.paste(roca(20, 16, musgo=False, semilla=12), (0, 2))
    px = img.load()
    cristal(px, 8, 8, 7, inclina=-1)
    cristal(px, 12, 7, 8)
    cristal(px, 15, 10, 5, inclina=2)
    return img


def mineral(brillo):
    img = Image.new("RGBA", (11, 12), (0, 0, 0, 0))
    px = img.load()
    cristal(px, 4, 10, 9, tam=(11, 12))
    cristal(px, 7, 10, 6, inclina=2, tam=(11, 12))
    if brillo:
        px[0, 1] = rgba("A4"); px[10, 3] = rgba("A4")
    return img


def tira(imagenes):
    w = max(i.width for i in imagenes)
    h = max(i.height for i in imagenes)
    hoja = Image.new("RGBA", (w * len(imagenes), h), (0, 0, 0, 0))
    for i, im in enumerate(imagenes):
        hoja.paste(im, (i * w, h - im.height))
    return hoja


if __name__ == "__main__":
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    destino = os.path.join(raiz, "arte", "mundos", "raiz", "objetos")
    os.makedirs(destino, exist_ok=True)
    arbol(1, [(16, 14, 12), (9, 18, 7), (23, 17, 7.5)]).save(os.path.join(destino, "arbol_a.png"))
    arbol(2, [(13, 13, 10), (20, 11, 9), (17, 20, 9)]).save(os.path.join(destino, "arbol_b.png"))
    roca(20, 16, semilla=3).save(os.path.join(destino, "roca_grande.png"))
    roca(12, 9, musgo=False, semilla=4).save(os.path.join(destino, "roca_pequena.png"))
    tira([matorral(), matorral(roto=True)]).save(os.path.join(destino, "matorral.png"))
    columna().save(os.path.join(destino, "columna.png"))
    muro().save(os.path.join(destino, "muro.png"))
    tira([piedra_eco(False), piedra_eco(True)]).save(os.path.join(destino, "piedra_eco.png"))
    tira([esencia(0), esencia(1)]).save(os.path.join(destino, "esencia.png"))
    cartel().save(os.path.join(destino, "cartel.png"))
    tira(mariposa()).save(os.path.join(destino, "mariposa.png"))
    tira([seta_luminosa(False), seta_luminosa(True)]).save(os.path.join(destino, "seta_luminosa.png"))
    tira([roca_mineral(False), roca_mineral(True)]).save(os.path.join(destino, "roca_mineral.png"))
    tira([mineral(False), mineral(True)]).save(os.path.join(destino, "mineral.png"))
    print("Objetos de Raíz dibujados en", destino)
