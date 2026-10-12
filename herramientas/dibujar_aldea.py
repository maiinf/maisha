"""
CUNA DE MUSGO dibujada píxel a píxel (paleta oficial de Raíz).

Uso:  python3 herramientas/dibujar_aldea.py
Genera en arte/mundos/raiz/aldea/:
  gran_arbol.png            el Gran Árbol hueco (176x208), la base del tronco abajo en el centro
  casa_seta.png             casa de Pino: 2 fotogramas (en ruinas, reconstruida)
  taller.png                taller de Corteza: 2 fotogramas (en ruinas, reconstruido)
  cocina.png                cocina de Juncia: 2 fotogramas
  puesto.png                puesto de Tawi: 2 fotogramas
  farol.png                 farolillo: 2 fotogramas (la llama tiembla)
  valla.png                 trozo de valla de madera
  estatua_<aldeano>.png     aldeanos convertidos en piedra por Giza
  interior_claro.png        el Claro de Calma, dentro del tronco (fondo de la habitación)
  brote_vida.png            el brote del Árbol de la Vida: 4 fotogramas de brillo
"""
import math
import os
import random
from PIL import Image, ImageDraw

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


# Materiales: 4 tonos de oscuro a claro (el primero hace de contorno)
MAT = {
    "corteza": ["Madera 1", "Madera 2", "Madera 3", "Madera 4"],
    "hoja": ["Follaje 1", "Follaje 2", "Follaje 3", "Follaje 4"],
    "musgo": ["Hierba 1", "Hierba 2", "Hierba 3", "Hierba 4"],
    "piedra": ["Piedra 1", "Piedra 2", "Piedra 3", "Piedra 4"],
    "tierra": ["Tierra 1", "Tierra 2", "Tierra 3", "Tierra 4"],
    "seta": ["Flor roja 1", "Flor roja 2", "Flor roja 3", "Flor roja 4"],
    "crema": ["Pergamino 1", "Pergamino 2", "Pergamino 3", "Extremos 2"],
    "cobre": ["Follaje cobre 1", "Follaje cobre 2", "Follaje cobre 3", "Follaje cobre 4"],
    "rojizo": ["Follaje rojizo 1", "Follaje rojizo 2", "Follaje rojizo 3", "Follaje rojizo 4"],
    "ambar": ["Flor ambar 1", "Flor ambar 2", "Flor ambar 3", "Flor ambar 4"],
    "luz": ["Flor ambar 2", "Maisha 2", "Maisha 3", "Maisha 4"],
    "agua": ["Agua 1", "Agua 2", "Agua 3", "Agua 4"],
    "oscuro": ["Extremos 1", "Extremos 1", "Madera 1", "Madera 2"],
    "brote": ["Follaje 2", "Brote 1", "Brote 2", "Maisha 4"],
}


class Lienzo:
    """Mapa de (material, tono). Al final se convierte en imagen con contorno selectivo."""

    def __init__(self, ancho, alto):
        self.w, self.h = ancho, alto
        self.m = [[None] * ancho for _ in range(alto)]
        self.sin_contorno = set()     # materiales que no generan contorno (luces, brillos)

    def dentro(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def px(self, x, y, mat, tono=2):
        x, y = int(x), int(y)
        if self.dentro(x, y):
            self.m[y][x] = (mat, tono)

    def get(self, x, y):
        if self.dentro(x, y):
            return self.m[y][x]
        return None

    def rect(self, x0, y0, x1, y1, mat, tono=2):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.px(x, y, mat, tono)

    def ovalo(self, cx, cy, rx, ry, mat, plano=None, recorte=None, luz_extra=0.0):
        """Óvalo sombreado con luz arriba a la izquierda. plano=n: un solo tono."""
        for y in range(max(0, int(cy - ry - 1)), min(self.h, int(cy + ry + 2))):
            for x in range(max(0, int(cx - rx - 1)), min(self.w, int(cx + rx + 2))):
                nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                if nx * nx + ny * ny <= 1.0:
                    if recorte and not recorte(x, y):
                        continue
                    if plano is not None:
                        t = plano
                    else:
                        luz = -nx * 0.55 - ny * 0.8 + luz_extra
                        t = 3 if luz > 0.55 else (2 if luz > -0.1 else (1 if luz > -0.75 else 0))
                        t = max(t, 1)
                    self.m[y][x] = (mat, t)

    def poligono(self, puntos, mat, tono=2):
        mascara = Image.new("1", (self.w, self.h))
        ImageDraw.Draw(mascara).polygon([tuple(p) for p in puntos], fill=1)
        mp = mascara.load()
        for y in range(self.h):
            for x in range(self.w):
                if mp[x, y]:
                    self.m[y][x] = (mat, tono)

    def linea(self, x0, y0, x1, y1, mat, tono=2, grosor=1):
        pasos = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(pasos + 1):
            t = i / pasos
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for dx in range(grosor):
                for dy in range(grosor):
                    self.px(round(x - grosor / 2 + dx + 0.5), round(y - grosor / 2 + dy + 0.5), mat, tono)

    def imagen(self, contorno=True):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        p = img.load()
        for y in range(self.h):
            for x in range(self.w):
                if self.m[y][x] is not None:
                    mat, t = self.m[y][x]
                    p[x, y] = c(MAT[mat][t])
        if contorno:
            borde = {}
            for y in range(self.h):
                for x in range(self.w):
                    if self.m[y][x] is None:
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            v = self.get(x + dx, y + dy)
                            if v is not None and v[0] not in self.sin_contorno:
                                borde[(x, y)] = v[0]
                                break
            for (x, y), mat in borde.items():
                p[x, y] = c(MAT[mat][0])
        return img


def tira(imagenes):
    w = max(i.width for i in imagenes)
    h = max(i.height for i in imagenes)
    hoja = Image.new("RGBA", (w * len(imagenes), h), (0, 0, 0, 0))
    for i, im in enumerate(imagenes):
        hoja.paste(im, (i * w + (w - im.width) // 2, h - im.height))
    return hoja


# ---------------------------------------------------------------------------
# EL GRAN ÁRBOL
# ---------------------------------------------------------------------------

def gran_arbol():
    W, H = 176, 208
    l = Lienzo(W, H)
    azar = random.Random(41)
    cx = 88
    base = 198            # donde el tronco toca el suelo

    def ancho_tronco(y):
        """Medio ancho del tronco a la altura y: recto arriba y abierto en raíces abajo."""
        t = (y - 92) / (base - 92)
        abre = max(0.0, (t - 0.5) / 0.5)
        return 21 + 5 * t + 34 * abre ** 2.4

    # --- tronco con la base abierta en contrafuertes
    for y in range(92, base + 1):
        medio = ancho_tronco(y)
        giro = math.sin(y * 0.045) * 2.0
        x0, x1 = cx - medio + giro, cx + medio + giro
        for x in range(int(x0), int(x1) + 1):
            u = (x - x0) / (x1 - x0)
            # abajo, el borde se ondula en raíces (lóbulos) que se hunden en la tierra
            if y > base - 14:
                lado = abs(x - cx) / medio
                lobulo = math.cos((x - cx) * 0.21) * 0.5 + 0.5
                if lado > 0.55 and (y - (base - 14)) > 14 * (1 - lobulo * 0.9) + lado * 4:
                    continue
            surco = (x + math.sin(y * 0.09 + x * 0.05) * 3.0) % 9
            tono = 3 if u < 0.2 else (2 if u < 0.6 else 1)
            if surco < 1.2:
                tono = max(1, tono - 1)
            if u > 0.88:
                tono = 1
            # la copa hace sombra sobre la parte alta del tronco
            if y < 112 and u > 0.12:
                tono = max(1, tono - 1)
            l.px(x, y, "corteza", tono)
    # dos raíces largas que se alejan por el suelo a cada lado
    for (lado, largo, caida) in [(-1, 30, 5), (1, 28, 4), (-1, 18, 8), (1, 20, 9)]:
        y_ini = base - 10 + (caida - 4)
        x_ini = cx + lado * (ancho_tronco(y_ini) - 6)
        for i in range(largo):
            t = i / largo
            x = x_ini + lado * i
            y = y_ini + t * caida
            g = 6 * (1 - t) + 1.5
            for k in range(int(round(g))):
                yy = int(y - g / 2 + k)
                tono = 3 if k == 0 else (2 if k < g * 0.6 else 1)
                l.px(x, yy, "corteza", tono)
    # musgo: sobre las partes iluminadas de las raíces y en vetas por la cara izquierda del tronco
    for y in range(100, base + 4):
        for x in range(W):
            v = l.get(x, y)
            if not v or v[0] != "corteza":
                continue
            arriba = l.get(x, y - 1)
            ruido = math.sin(x * 0.7 + y * 0.13) + math.sin(x * 0.23 - y * 0.41)
            if y > base - 16 and v[1] == 3 and ruido > 0.2:
                l.px(x, y, "musgo", 3 if arriba is None or arriba[0] != "corteza" else 2)
            elif x < cx - 12 and ruido > 1.35 and y > 120:
                l.px(x, y, "musgo", 2 if ruido < 1.7 else 3)
    # --- el hueco de la puerta: arco oscuro, con la luz cálida del interior al fondo
    puerta_y0, medio_p = 150, 13
    for y in range(puerta_y0, base + 1):
        for x in range(cx - medio_p - 1, cx + medio_p + 2):
            dx = (x + 0.5 - cx) / medio_p
            dy = (y + 0.5 - (puerta_y0 + medio_p)) / medio_p
            if not ((y >= puerta_y0 + medio_p and abs(dx) <= 1.0) or (dx * dx + dy * dy <= 1.0)):
                continue
            prof = (y - puerta_y0) / (base - puerta_y0)
            # resplandor: elipse de luz en el suelo del fondo
            lx, ly = dx / 0.8, (prof - 0.95) / 0.42
            resplandor = lx * lx + ly * ly
            if resplandor < 0.35:
                tono = ("luz", 2)
            elif resplandor < 0.7:
                tono = ("luz", 1)
            elif resplandor < 1.0:
                tono = ("ambar", 2) if (x + y) % 2 else ("luz", 1)
            elif resplandor < 1.4 and (x + y) % 2 == 0:
                tono = ("ambar", 1)
            else:
                tono = ("oscuro", 0)
            l.px(x, y, *tono)
    # marco del hueco: corteza gastada y clara
    for y in range(puerta_y0 - 2, base + 1):
        for x in range(cx - medio_p - 3, cx + medio_p + 4):
            v = l.get(x, y)
            if v and v[0] == "corteza":
                junto = [l.get(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
                if any(j and j[0] in ("oscuro", "ambar", "luz") for j in junto):
                    l.px(x, y, "corteza", 3 if x < cx + 4 else 2)
    # umbral de raíz en la entrada
    l.rect(cx - 12, base - 1, cx + 12, base, "corteza", 2)
    l.rect(cx - 11, base - 2, cx + 11, base - 2, "corteza", 3)
    # farolillo colgado a la izquierda de la puerta
    l.linea(cx - 22, 146, cx - 22, 154, "oscuro", 2)
    l.rect(cx - 24, 154, cx - 20, 154, "oscuro", 3)
    l.ovalo(cx - 22, 158.5, 3, 4, "ambar")
    l.px(cx - 22, 158, "luz", 3); l.px(cx - 23, 159, "luz", 2); l.px(cx - 22, 160, "luz", 2)
    # ventana redonda iluminada (la habitación de Bibi)
    vx, vy = cx + 10, 122
    l.ovalo(vx, vy, 6, 6, "corteza", plano=3)
    l.ovalo(vx, vy, 4.6, 4.6, "ambar", plano=2)
    l.ovalo(vx - 0.5, vy - 0.5, 3, 3, "luz", plano=2)
    l.rect(vx - 4, vy, vx + 4, vy, "corteza", 1)
    l.rect(vx, vy - 4, vx, vy + 4, "corteza", 1)

    # --- copa: bultos redondos que forman una cúpula ancha
    bultos = [
        (88, 42, 34), (56, 52, 28), (120, 52, 28), (31, 74, 23), (145, 74, 23),
        (70, 24, 22), (106, 24, 22), (88, 72, 30), (54, 88, 22), (122, 88, 22),
        (17, 94, 14), (159, 94, 14), (88, 14, 14), (40, 36, 18), (136, 36, 18),
    ]
    copa = [[None] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            mejor = None
            for (bx, by, r) in bultos:
                d = math.hypot(x + 0.5 - bx, (y + 0.5 - by) * 1.08)
                if d <= r:
                    q = d / r
                    if mejor is None or q < mejor[0]:
                        mejor = (q, (x + 0.5 - bx) / r, (y + 0.5 - by) / r, by)
            copa[y][x] = mejor

    def tono_copa(x, y):
        q, nx, ny, by = copa[y][x]
        luz = -nx * 0.55 - ny * 0.8 - max(0.0, (y - 58) / 58.0) * 0.95
        return 3 if luz > 0.5 else (2 if luz > -0.05 else (1 if luz > -0.7 else 0))

    for y in range(H):
        for x in range(W):
            if copa[y][x]:
                l.m[y][x] = ("hoja", tono_copa(x, y))
    # textura de hojas: «escamas» de follaje. Cada mata tiene el borde de arriba más claro
    # y una línea más oscura debajo; se dibujan de arriba abajo para que se solapen.
    matas = []
    for _ in range(520):
        x, y = azar.randint(2, W - 3), azar.randint(2, 128)
        if copa[y][x] and copa[y][x][0] < 0.93:
            matas.append((y, x))
    matas.sort()
    for (y, x) in matas:
        t = tono_copa(x, y)
        r = 3 if azar.random() < 0.7 else 4
        for dx in range(-r, r + 1):
            arco = int(round(math.sqrt(max(0, r * r - dx * dx)) * 0.55))
            yy = y - arco
            if l.get(x + dx, yy) and copa[yy][x + dx]:
                l.px(x + dx, yy, "hoja", min(3, t + 1) if t < 3 else 3)
                if l.get(x + dx, yy + 1) and copa[yy + 1][x + dx]:
                    l.px(x + dx, yy + 1, "hoja", t)
            if abs(dx) < r and l.get(x + dx, y + 1) and copa[y + 1][x + dx]:
                l.px(x + dx, y + 1, "hoja", max(0, t - 1))
    # borde interior: línea oscura donde un bulto pasa por delante de otro (da volumen)
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            v = copa[y][x]
            w_ = copa[y - 1][x]
            if v and w_ and abs(w_[3] - v[3]) > 6 and w_[3] < v[3] and v[0] > 0.88:
                l.m[y][x] = ("hoja", 0)
    # lianas que cuelgan de la copa
    for _ in range(14):
        x = azar.randint(20, W - 20)
        y = max((yy for yy in range(H) if copa[yy][x]), default=0)
        if y == 0:
            continue
        largo = azar.randint(4, 11)
        for k in range(1, largo):
            if l.get(x, y + k) is None or l.get(x, y + k)[0] in ("hoja", "corteza"):
                l.px(x, y + k, "hoja", 1 if k < largo - 2 else 2)
        l.px(x, y + largo, "seta", 3) if azar.random() < 0.3 else None
    # frutos de luz que cuelgan (el árbol está vivo y protege la aldea)
    for (fx, fy) in [(40, 100), (70, 106), (110, 104), (138, 98), (60, 66), (122, 62), (96, 86), (26, 84), (150, 82), (88, 30)]:
        l.px(fx, fy - 2, "hoja", 0)
        l.ovalo(fx + 0.5, fy + 0.5, 1.7, 1.9, "ambar", plano=2)
        l.px(fx, fy, "luz", 3)
    l.sin_contorno = {"luz", "ambar", "oscuro"}
    return l.imagen()


# ---------------------------------------------------------------------------
# CASAS: cada una con su versión en ruinas y reconstruida
# ---------------------------------------------------------------------------

def casa_seta(reconstruida):
    """Casa de Pino: una seta enorme con puerta redonda."""
    l = Lienzo(56, 64)
    azar = random.Random(5)
    if reconstruida:
        # pie de la seta (la casa)
        for y in range(28, 62):
            t = (y - 28) / 34
            medio = 13 + 4 * t
            for x in range(int(28 - medio), int(28 + medio) + 1):
                u = (x - (28 - medio)) / (2 * medio)
                l.px(x, y, "crema", 3 if u < 0.25 else (2 if u < 0.72 else 1))
        # puerta redonda de madera
        l.ovalo(28, 52, 6, 7, "corteza", recorte=lambda x, y: y < 62)
        l.rect(22, 52, 34, 61, "corteza", 2)
        for x in (25, 28, 31):
            l.rect(x, 47, x, 61, "corteza", 1)
        l.px(32, 55, "ambar", 3)
        # ventanas iluminadas
        for (vx, vy) in [(18, 40), (38, 40)]:
            l.ovalo(vx, vy, 3.2, 3.2, "corteza", plano=1)
            l.ovalo(vx, vy, 2.2, 2.2, "luz", plano=1)
            l.px(vx - 1, vy - 1, "luz", 3)
        # sombrero rojo con motas
        l.ovalo(28, 24, 27, 15, "seta", recorte=lambda x, y: y <= 30)
        for y in range(28, 32):
            for x in range(4, 53):
                if l.get(x, y) and l.get(x, y)[0] == "seta":
                    l.px(x, y, "seta", 0 if y == 31 else 1)
        for (mx, my, r) in [(14, 18, 3), (27, 13, 3.5), (40, 19, 3), (21, 25, 2.2), (35, 26, 2.2), (47, 25, 1.8), (8, 25, 1.6)]:
            l.ovalo(mx, my, r, r * 0.8, "crema", plano=3)
        # chimenea pequeña
        l.rect(40, 6, 43, 12, "piedra", 2)
        l.rect(40, 6, 43, 6, "piedra", 3)
        # escalón
        l.rect(22, 62, 34, 63, "piedra", 2)
    else:
        # tocón roto del pie, con grietas
        for y in range(44, 62):
            t = (y - 44) / 18
            medio = 14 + 3 * t
            for x in range(int(28 - medio), int(28 + medio) + 1):
                u = (x - (28 - medio)) / (2 * medio)
                tono = 3 if u < 0.25 else (2 if u < 0.72 else 1)
                l.px(x, y, "crema", tono)
        # borde superior roto (dientes)
        for x in range(14, 43):
            alto = 44 - int(abs(math.sin(x * 1.3)) * 5 + (x % 4 == 0) * 2)
            for y in range(alto, 46):
                l.px(x, y, "crema", 2 if x < 30 else 1)
        for (x0, y0, x1, y1) in [(20, 47, 23, 55), (33, 46, 31, 53), (31, 53, 34, 58)]:
            l.linea(x0, y0, x1, y1, "crema", 0)
        l.rect(24, 52, 31, 61, "oscuro", 1)       # hueco de la puerta
        # trozos del sombrero por el suelo
        for (px_, py_, rx, ry) in [(9, 56, 7, 4), (46, 57, 8, 4.5), (36, 62, 5, 2.4)]:
            l.ovalo(px_, py_, rx, ry, "seta")
            l.px(px_ - 1, py_ - 1, "crema", 3); l.px(px_ + 2, py_, "crema", 3)
        # escombros
        for _ in range(8):
            x, y = azar.randint(6, 50), azar.randint(58, 63)
            if l.get(x, y) is None:
                l.px(x, y, "crema", 1)
    return l.imagen()


def taller(reconstruido):
    """Taller de Corteza: muros de piedra, tejado de tablas, chimenea con la forja."""
    l = Lienzo(72, 64)
    azar = random.Random(8)

    def muro_piedra(x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            fila = (y - y0) // 5
            for x in range(x0, x1 + 1):
                desplazado = (x + (fila % 2) * 4) % 8
                junta = (y - y0) % 5 == 4 or desplazado == 0
                u = (x - x0) / max(1, x1 - x0)
                tono = 1 if junta else (3 if u < 0.2 and azar.random() < 0.6 else 2)
                l.px(x, y, "piedra", tono)

    if reconstruido:
        muro_piedra(8, 30, 60, 61)
        # tejado de tablas a dos aguas
        for y in range(12, 32):
            t = (y - 12) / 20
            medio = 10 + 26 * t
            for x in range(int(34 - medio), int(34 + medio) + 1):
                tabla = (y - 12) % 4 == 3
                u = (x - (34 - medio)) / (2 * medio)
                tono = 1 if tabla else (3 if u < 0.3 else 2)
                l.px(x, y, "cobre", tono)
        l.rect(4, 31, 64, 32, "cobre", 0)
        # chimenea de la forja con brillo
        muro_piedra(50, 4, 57, 22)
        l.rect(49, 3, 58, 4, "piedra", 3)
        # puerta ancha de taller
        l.rect(28, 42, 41, 61, "corteza", 2)
        for x in (31, 35, 38):
            l.rect(x, 42, x, 61, "corteza", 1)
        l.rect(28, 41, 41, 41, "corteza", 3)
        # ventana con el fuego de la forja
        l.rect(13, 40, 21, 47, "corteza", 1)
        l.rect(14, 41, 20, 46, "ambar", 2)
        l.rect(15, 44, 19, 46, "luz", 1)
        l.px(16, 45, "luz", 3)
        # yunque fuera
        l.rect(48, 55, 58, 57, "piedra", 2)
        l.rect(51, 58, 55, 61, "piedra", 1)
        l.rect(46, 55, 48, 56, "piedra", 2)
        l.rect(48, 55, 58, 55, "piedra", 3)
        # cartel con un martillo
        l.rect(62, 38, 69, 44, "corteza", 3)
        l.rect(63, 40, 68, 40, "piedra", 1); l.rect(65, 40, 65, 43, "corteza", 1)
    else:
        # muros derrumbados: altura irregular
        for x in range(8, 61):
            alto = 46 + int(abs(math.sin(x * 0.37)) * 8 + abs(math.sin(x * 1.1)) * 3)
            for y in range(alto, 62):
                l.px(x, y, "piedra", 2)
        muro_piedra(8, 50, 60, 61)
        for x in range(8, 61):
            for y in range(40, 50):
                alto = 46 + int(abs(math.sin(x * 0.37)) * 8 + abs(math.sin(x * 1.1)) * 3)
                if y >= alto - 4 and y < 50:
                    l.px(x, y, "piedra", 2 if y > alto - 3 else 3)
        l.rect(28, 50, 39, 61, "oscuro", 1)    # hueco
        # vigas caídas
        l.linea(6, 44, 30, 56, "cobre", 2, grosor=2)
        l.linea(40, 40, 64, 52, "cobre", 1, grosor=2)
        # muñón de la chimenea
        muro_piedra(50, 34, 57, 49)
        # yunque frío caído
        l.rect(56, 58, 64, 60, "piedra", 1)
        l.rect(56, 58, 64, 58, "piedra", 3)
        # escombros
        for _ in range(16):
            x, y = azar.randint(2, 70), azar.randint(57, 63)
            if l.get(x, y) is None:
                l.ovalo(x, y, 1.6, 1.2, "piedra")
    return l.imagen()


def cocina(reconstruida):
    """Cocina de Juncia: cabaña de juncos con una olla grande fuera."""
    l = Lienzo(56, 52)
    azar = random.Random(11)
    if reconstruida:
        # paredes de juncos
        for y in range(22, 50):
            for x in range(8, 48):
                l.px(x, y, "cobre", 3 if x % 3 == 0 else 2)
        # tejado de paja
        for y in range(6, 24):
            t = (y - 6) / 18
            medio = 8 + 22 * t
            for x in range(int(28 - medio), int(28 + medio) + 1):
                l.px(x, y, "ambar", 2 if (x + y) % 4 else 1)
        l.rect(4, 23, 52, 24, "ambar", 0)
        l.rect(22, 34, 33, 49, "oscuro", 1)
        # olla humeante
        l.ovalo(45, 46, 7, 5, "piedra")
        l.rect(39, 41, 51, 42, "piedra", 3)
        l.ovalo(45, 41, 5, 1.5, "brote", plano=1)
    else:
        # cabaña hundida: postes y juncos por el suelo
        for x in (10, 26, 44):
            l.rect(x, 26 + (x % 7), x + 2, 49, "cobre", 1)
        for y in range(40, 50):
            for x in range(8, 48):
                if (x * 7 + y * 3) % 11 < 7:
                    l.px(x, y, "cobre", 2 if x % 3 else 3)
        l.linea(6, 34, 30, 44, "ambar", 1, grosor=2)
        l.linea(28, 30, 50, 46, "ambar", 2, grosor=2)
        # olla volcada
        l.ovalo(44, 47, 6, 4, "piedra")
        l.ovalo(39, 48, 2, 3, "oscuro", plano=1)
        for _ in range(10):
            x, y = azar.randint(4, 52), azar.randint(47, 51)
            if l.get(x, y) is None:
                l.px(x, y, "ambar", 1)
    return l.imagen()


def puesto(reconstruido):
    """Puesto de Tawi: mostrador con toldo de rayas."""
    l = Lienzo(52, 48)
    if reconstruido:
        for x in (6, 44):
            l.rect(x, 12, x + 2, 46, "corteza", 2)
        for x in range(2, 50):
            for y in range(8, 18):
                raya = (x // 6) % 2
                l.px(x, y, "seta" if raya else "crema", 2 if y < 16 else 1)
        for x in range(2, 50, 6):
            l.ovalo(x + 3, 18, 3, 2, "seta" if (x // 6) % 2 else "crema", recorte=lambda xx, yy: yy >= 18)
        l.rect(4, 32, 47, 46, "corteza", 2)
        l.rect(4, 32, 47, 33, "corteza", 3)
        for (ox, mat) in [(10, "ambar"), (18, "brote"), (27, "seta"), (36, "agua")]:
            l.ovalo(ox, 30, 3, 2.5, mat)
    else:
        l.rect(6, 22, 8, 46, "corteza", 2)
        l.linea(44, 46, 30, 26, "corteza", 1, grosor=3)
        # toldo rasgado en el suelo
        for x in range(2, 40):
            y = 42 + int(math.sin(x * 0.4) * 2)
            raya = (x // 6) % 2
            l.rect(x, y, x, y + 3, "seta" if raya else "crema", 1)
        l.rect(14, 38, 30, 46, "corteza", 1)
        for (ox, oy) in [(36, 46), (40, 45), (46, 47)]:
            l.ovalo(ox, oy, 2, 1.5, "ambar")
    return l.imagen()


def farol(fotograma):
    l = Lienzo(10, 26)
    l.rect(4, 6, 5, 25, "corteza", 2)
    l.rect(4, 6, 4, 25, "corteza", 3)
    l.rect(2, 5, 7, 5, "corteza", 1)
    l.rect(2, 2, 7, 4, "oscuro", 3)
    l.rect(3, 0, 6, 1, "corteza", 1)
    # llama
    l.rect(3, 2, 6, 4, "ambar", 2)
    l.px(4 + fotograma, 3, "luz", 3)
    l.px(4, 2 + fotograma, "luz", 2)
    l.rect(3, 24, 6, 25, "piedra", 2)
    l.sin_contorno = {"luz", "ambar"}
    return l.imagen()


def valla():
    l = Lienzo(16, 14)
    for x in (2, 13):
        l.rect(x, 2, x + 1, 13, "corteza", 3 if x == 2 else 2)
    l.rect(0, 5, 15, 6, "corteza", 2)
    l.rect(0, 5, 15, 5, "corteza", 3)
    l.rect(0, 10, 15, 11, "corteza", 2)
    l.rect(0, 10, 15, 10, "corteza", 3)
    return l.imagen()


def setitas(variante):
    """Setas pequeñas de adorno (no estorban el paso)."""
    l = Lienzo(14, 12)
    matas = [(4, 9, 3.2, "seta"), (9, 10, 2.4, "seta")] if variante == 0 else [(5, 10, 2.6, "crema"), (9, 8, 3.2, "ambar"), (3, 10, 1.8, "crema")]
    for (x, y, r, mat) in matas:
        l.rect(x - 0.5, y - 1, x + 0.5, 11, "crema", 2)
        l.ovalo(x, y - 2, r, r * 0.7, mat, recorte=lambda xx, yy, y=y: yy <= y - 1)
        if mat == "seta":
            l.px(x - 1, y - 3, "crema", 3)
    for x in range(1, 13):
        if l.get(x, 11) is None and x % 3:
            l.px(x, 11, "musgo", 2)
    return l.imagen()


def estatua(nombre):
    """Convierte el dibujo del aldeano en piedra: tonos de piedra según su luz, grietas y musgo."""
    fuente = Image.open(os.path.join(RAIZ, "arte", "personajes", "aldeanos", f"{nombre}_frente.png")).convert("RGBA")
    w, h = fuente.size
    tonos = [c("Piedra 1"), c("Piedra 2"), c("Piedra 3"), c("Piedra 4")]
    img = Image.new("RGBA", (w, h + 6), (0, 0, 0, 0))
    azar = random.Random(len(nombre))
    p = img.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = fuente.getpixel((x, y))
            if a == 0:
                continue
            lum = 0.3 * r + 0.59 * g + 0.11 * b
            t = 0 if lum < 45 else (1 if lum < 95 else (2 if lum < 150 else 3))
            p[x, y] = tonos[t]
    # grietas
    for _ in range(3):
        x, y = azar.randint(7, w - 8), azar.randint(8, h - 10)
        for k in range(azar.randint(3, 6)):
            if p[x, y][3]:
                p[x, y] = tonos[0]
            x += azar.choice((-1, 0, 1))
            y += 1
    # musgo en lo alto
    for x in range(w):
        for y in range(h):
            if p[x, y][3] and p[x, y] != tonos[0]:
                if azar.random() < 0.45:
                    p[x, y] = c("Hierba 3") if azar.random() < 0.6 else c("Hierba 2")
                break
    # pedestal
    for y in range(h, h + 6):
        for x in range(4, w - 4):
            t = 3 if y == h else (2 if x < w // 2 else 1)
            if y == h + 5 or x in (4, w - 5):
                t = 0
            p[x, y] = tonos[t]
    return img


# ---------------------------------------------------------------------------
# INTERIOR: el Claro de Calma, dentro del tronco
# ---------------------------------------------------------------------------

INTERIOR_W, INTERIOR_H = 352, 224


def interior_claro():
    """Fondo de la habitación. Pared curva de madera arriba, suelo de anillos del árbol,
    estanterías, la cama de hojas de Bibi, la entrada sellada por raíces y el hueco de salida abajo."""
    W, H = INTERIOR_W, INTERIOR_H
    l = Lienzo(W, H)
    azar = random.Random(77)
    cx, cy = W / 2, 128           # centro del suelo
    rx, ry = 160, 84              # suelo ovalado
    # suelo: el corte del tronco, con anillos finos y un borde de musgo
    for y in range(H):
        for x in range(W):
            nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
            d = math.sqrt(nx * nx + ny * ny)
            if d > 1.0:
                continue
            ang = math.atan2(ny, nx)
            ondula = math.sin(ang * 3 + 1.0) * 0.012 + math.sin(ang * 7) * 0.006
            fase = ((d + ondula) * 19) % 1.0
            tono = 3 if fase < 0.16 else 2
            if (d + ondula) * 19 % 3 < 0.16:
                tono = 1            # algún anillo más marcado
            ruido = math.sin(x * 0.9 + y * 0.37) + math.sin(x * 0.31 - y * 1.1)
            musgo = 0.86 + ruido * 0.035
            if d > musgo:
                l.px(x, y, "musgo", 3 if d < musgo + 0.025 else 2)
                continue
            l.px(x, y, "cobre", tono)
    # pared curva del tronco (por encima del suelo)
    for y in range(0, int(cy)):
        for x in range(W):
            nx = (x + 0.5 - cx) / rx
            if abs(nx) > 1.0:
                continue
            borde = cy - ry * math.sqrt(max(0.0, 1 - nx * nx))
            if y < borde:
                alto = borde - y
                if alto > 72:
                    continue
                u = (x - (cx - rx)) / (2 * rx)
                surco = (x + math.sin(y * 0.15) * 2) % 10
                tono = 2 if surco > 1.5 else 1
                if alto < 3:
                    tono = 0
                elif u < 0.12 or u > 0.88:
                    tono = 1
                l.px(x, y, "corteza", tono)
    # techo: borde superior oscuro
    for x in range(W):
        nx = (x + 0.5 - cx) / rx
        if abs(nx) <= 1.0:
            borde = cy - ry * math.sqrt(max(0.0, 1 - nx * nx))
            top = int(borde - 72)
            for y in range(max(0, top), max(0, top + 3)):
                l.px(x, y, "corteza", 0)
    # --- la entrada sellada (al fondo, en el centro): un arco con raíces entrelazadas
    ax, ay = int(cx), 52
    # marco de corteza clara alrededor del arco
    for y in range(ay - 30, ay + 2):
        for x in range(ax - 20, ax + 21):
            dx = (x + 0.5 - ax) / 20
            dy = (y - (ay - 10)) / 20
            if (y >= ay - 10 and abs(dx) <= 1) or dx * dx + dy * dy <= 1:
                l.px(x, y, "corteza", 3 if x < ax else 2)
    for y in range(ay - 26, ay + 2):
        for x in range(ax - 16, ax + 17):
            dx = (x + 0.5 - ax) / 16
            dy = (y - (ay - 10)) / 16
            if (y >= ay - 10 and abs(dx) <= 1) or dx * dx + dy * dy <= 1:
                l.px(x, y, "oscuro", 0)
    for k in range(7):
        x0 = ax - 15 + k * 5
        for y in range(ay - 26, ay + 2):
            x = x0 + int(math.sin(y * 0.3 + k) * 3)
            if l.get(x, y) and l.get(x, y)[0] == "oscuro":
                l.px(x, y, "corteza", 3 if k % 2 else 2)
                l.px(x + 1, y, "corteza", 1)
    # brillo dorado que se escapa entre las raíces (el misterio)
    for (x, y) in [(ax - 9, ay - 6), (ax + 4, ay - 14), (ax + 10, ay - 3), (ax - 2, ay - 20), (ax - 12, ay - 16)]:
        if l.get(x, y) and l.get(x, y)[0] == "oscuro":
            l.px(x, y, "luz", 3)
    # --- estanterías a la derecha con libros y frascos
    for (ex, ey) in [(236, 34), (276, 44)]:
        l.rect(ex, ey, ex + 30, ey + 32, "corteza", 1)
        for k in range(3):
            yy = ey + 9 + k * 10
            l.rect(ex + 1, yy, ex + 29, yy + 1, "corteza", 3)
            x = ex + 2
            while x < ex + 27:
                ancho = azar.randint(2, 3)
                mat = azar.choice(["seta", "agua", "cobre", "rojizo", "crema", "ambar", "hoja"])
                alto = azar.randint(5, 8)
                l.rect(x, yy - alto, x + ancho - 1, yy - 1, mat, 2)
                l.px(x, yy - alto, mat, 3)
                x += ancho + (1 if azar.random() < 0.3 else 0)
    # --- la cama de hojas de Bibi a la izquierda
    l.ovalo(70, 84, 26, 10, "hoja")
    l.ovalo(66, 81, 18, 6, "musgo", plano=3)
    l.ovalo(52, 80, 6, 4, "crema")           # almohada
    # mesita con tetera
    l.rect(104, 64, 120, 66, "corteza", 3)
    l.rect(106, 67, 108, 74, "corteza", 1); l.rect(116, 67, 118, 74, "corteza", 1)
    l.ovalo(112, 61, 4, 3, "agua")
    l.px(116, 59, "agua", 1)
    # farolillos en la pared
    for (fx, fy) in [(36, 46), (160, 22), (196, 22), (318, 50)]:
        l.rect(fx - 2, fy - 3, fx + 2, fy + 3, "ambar", 2)
        l.rect(fx - 1, fy - 1, fx + 1, fy + 1, "luz", 3)
        l.rect(fx - 3, fy - 4, fx + 3, fy - 4, "corteza", 0)
    # alfombra de musgo en el centro (donde se medita)
    l.ovalo(cx, 128, 40, 18, "musgo", plano=2)
    l.ovalo(cx, 128, 34, 14, "musgo", plano=3)
    for k in range(40):
        a = k / 40 * math.tau
        x, y = cx + math.cos(a) * 37, 128 + math.sin(a) * 16
        if k % 4 == 0:
            l.px(x, y, "seta", 3)
        elif k % 4 == 2:
            l.px(x, y, "luz", 3)
    # hueco de salida (abajo en el centro): la luz de fuera
    for y in range(int(cy + ry - 10), H):
        for x in range(int(cx - 16), int(cx + 17)):
            borde = x in (int(cx - 16), int(cx - 15), int(cx + 15), int(cx + 16))
            l.px(x, y, "corteza", 3) if borde else l.px(x, y, "luz", 1 if y < cy + ry - 2 else 2)
    # alfombra de hojas a la entrada
    l.rect(cx - 12, cy + ry - 22, cx + 12, cy + ry - 12, "hoja", 2)
    l.rect(cx - 12, cy + ry - 22, cx + 12, cy + ry - 22, "hoja", 3)
    for x in range(int(cx - 12), int(cx + 13), 3):
        l.px(x, cy + ry - 11, "hoja", 1)
    l.sin_contorno = {"luz", "ambar", "oscuro", "musgo", "cobre"}
    img = l.imagen()
    # alrededor de la habitación: negro (como en las casas de los juegos de Nintendo DS)
    fondo = Image.new("RGBA", (W, H), c("Extremos 1"))
    fondo.alpha_composite(img)
    return fondo



# ---------------------------------------------------------------------------
# INTERIORES DE LAS CASAS (habitación rectangular vista desde arriba, como en Pokémon)
# ---------------------------------------------------------------------------

CASA_W, CASA_H = 320, 208
SUELO = (32, 72, 288, 184)          # x0, y0, x1, y1 del suelo que se pisa
HUECO_X = (148, 172)                # hueco de la puerta, abajo


def habitacion(pared, techo, suelo_fn):
    """Base de una habitación: techo arriba, pared del fondo, paredes laterales finas, suelo y salida."""
    l = Lienzo(CASA_W, CASA_H)
    x0, y0, x1, y1 = SUELO
    # pared del fondo
    for y in range(20, y0):
        for x in range(x0, x1):
            l.px(x, y, *pared(x, y))
    # techo / borde superior
    for y in range(8, 20):
        for x in range(x0 - 8, x1 + 8):
            l.px(x, y, *techo(x, y))
    # zócalo
    l.rect(x0, y0 - 3, x1 - 1, y0 - 1, "corteza", 1)
    l.rect(x0, y0 - 3, x1 - 1, y0 - 3, "corteza", 2)
    # suelo
    for y in range(y0, y1):
        for x in range(x0, x1):
            l.px(x, y, *suelo_fn(x, y))
    # paredes laterales y de delante (se ve solo su canto)
    for y in range(8, y1 + 8):
        for x in list(range(x0 - 8, x0)) + list(range(x1, x1 + 8)):
            l.px(x, y, "corteza", 1 if x in (x0 - 1, x1) else 0)
    for y in range(y1, y1 + 8):
        for x in range(x0 - 8, x1 + 8):
            if HUECO_X[0] <= x < HUECO_X[1]:
                continue
            l.px(x, y, "corteza", 1 if y == y1 else 0)
    # salida: luz de fuera y felpudo
    for y in range(y1, CASA_H):
        for x in range(*HUECO_X):
            l.px(x, y, "luz", 1 if y < y1 + 8 else 2)
    l.rect(HUECO_X[0] + 2, y1 - 10, HUECO_X[1] - 3, y1 - 3, "cobre", 2)
    for x in range(HUECO_X[0] + 3, HUECO_X[1] - 3, 2):
        l.px(x, y1 - 7, "cobre", 3)
    return l


def _fondo_negro(l):
    l.sin_contorno = {"luz", "ambar", "oscuro", "cobre", "crema", "piedra", "corteza", "tierra", "seta", "hoja", "musgo", "agua"}
    img = l.imagen()
    fondo = Image.new("RGBA", img.size, c("Extremos 1"))
    fondo.alpha_composite(img)
    return fondo


def interior_casa_pino():
    """Dentro de la casa-seta de Pino: paredes de seta, techo rojo con láminas, suelo de tablas,
    su cama, el mapa de sus «exploraciones», un catalejo, tarros con luz y la escalera al tejado."""
    azar = random.Random(23)
    def pared(x, y):
        # el pie de la seta por dentro: vetas verticales suaves y sombra bajo el sombrero
        if y < 27:
            return ("crema", 2)
        veta = (x + int(math.sin(y * 0.2 + x) * 1.5)) % 16 == 0
        return ("crema", 2 if veta else 3)
    def techo(x, y):
        # el sombrero visto desde dentro: rojo con las láminas de la seta
        if y < 15:
            return ("seta", 1 if y < 13 else 2)
        return ("crema", 1) if x % 5 == 0 else ("crema", 2)
    def suelo(x, y):
        tabla = (y - 72) // 7
        junta = (y - 72) % 7 == 6 or (x + tabla * 13) % 40 == 0
        if junta:
            return ("corteza", 1)
        return ("corteza", 3 if tabla % 2 == 0 else 2)
    l = habitacion(pared, techo, suelo)
    # alfombra redonda
    l.ovalo(160, 130, 38, 15, "seta", plano=2)
    l.ovalo(160, 130, 31, 11, "crema", plano=3)
    l.ovalo(160, 130, 22, 7, "seta", plano=3)
    # cama a la izquierda (contra la pared)
    l.rect(38, 64, 86, 70, "corteza", 2)          # cabecero
    l.rect(38, 64, 86, 64, "corteza", 3)
    l.rect(38, 71, 86, 104, "corteza", 1)         # armazón
    l.rect(40, 72, 84, 100, "seta", 2)            # manta
    l.rect(40, 72, 84, 73, "seta", 3)
    for (x, y) in [(46, 80), (58, 88), (72, 78), (78, 94), (50, 96), (66, 98)]:
        l.rect(x, y, x + 1, y, "crema", 3)
    l.ovalo(52, 76, 8, 4, "crema")                # almohada
    # baúl de juguetes
    l.rect(40, 112, 64, 128, "corteza", 2)
    l.rect(40, 112, 64, 115, "corteza", 3)
    l.rect(51, 118, 53, 121, "ambar", 2)
    l.ovalo(58, 110, 3, 3, "seta")                # pelota asomando
    # mapa de Pino en la pared (dibujado con mucha imaginación)
    l.rect(95, 27, 141, 59, "corteza", 1)
    l.rect(96, 28, 140, 58, "crema", 2)
    l.rect(96, 28, 140, 29, "crema", 3)
    l.linea(100, 52, 112, 40, "tierra", 2); l.linea(112, 40, 126, 46, "tierra", 2); l.linea(126, 46, 134, 34, "tierra", 2)
    for (x, y) in [(104, 34), (108, 36), (120, 52), (130, 52)]:
        l.px(x, y, "hoja", 2); l.px(x, y + 1, "hoja", 1)
    l.linea(132, 32, 136, 36, "seta", 1); l.linea(136, 32, 132, 36, "seta", 1)    # una X roja
    l.rect(117, 26, 119, 28, "seta", 1)           # chincheta
    # estante con tarros de luz (setas luminosas guardadas)
    l.rect(154, 46, 196, 48, "corteza", 2)
    for k, x in enumerate(range(158, 194, 9)):
        l.rect(x, 37, x + 6, 45, "agua", 2 if k % 2 else 3)
        l.rect(x + 1, 35, x + 5, 36, "corteza", 3)
        l.px(x + 2, 40, "luz", 3)
    # ventana redonda con cielo
    l.ovalo(224, 44, 13, 13, "corteza", plano=2)
    l.ovalo(224, 44, 11, 11, "agua", plano=3)
    l.ovalo(221, 41, 4, 3, "crema", plano=3)        # una nube
    l.rect(213, 44, 235, 44, "corteza", 1)
    l.rect(224, 33, 224, 55, "corteza", 1)
    # catalejo en su trípode
    l.linea(214, 96, 222, 80, "corteza", 1); l.linea(230, 96, 222, 80, "corteza", 1); l.linea(222, 96, 222, 80, "corteza", 2)
    l.linea(214, 80, 232, 70, "ambar", 2, grosor=3)
    l.rect(230, 68, 233, 71, "ambar", 3)
    # escalera al tejado (la torre del vigía)
    for x in (258, 274):
        l.rect(x, 4, x + 2, 82, "corteza", 3 if x == 258 else 2)
    for y in range(10, 82, 8):
        l.rect(260, y, 273, y + 1, "corteza", 2)
    l.rect(254, 0, 280, 8, "oscuro", 0)           # trampilla abierta al cielo
    l.rect(256, 2, 278, 6, "luz", 2)
    # macetas con setitas
    l.rect(262, 160, 280, 176, "tierra", 2)
    l.ovalo(267, 156, 4, 3, "seta"); l.ovalo(275, 158, 3, 2.4, "ambar")
    return _fondo_negro(l)


def interior_taller():
    """Dentro del taller de Corteza: paredes de piedra, la forja encendida, herramientas colgadas,
    el banco de trabajo con dibujos de cetros, un barril y carbón."""
    azar = random.Random(29)
    def pared(x, y):
        fila = (y - 20) // 7
        junta = (y - 20) % 7 == 6 or (x + (fila % 2) * 6) % 12 == 0
        return ("piedra", 1 if junta else (3 if (x // 12 + fila) % 3 == 0 else 2))
    techo = lambda x, y: ("cobre", 1 if y in (8, 19) or x % 32 < 3 else 2)
    def suelo(x, y):
        # tablas anchas y gastadas
        tabla = (y - 72) // 9
        if (y - 72) % 9 == 8 or (x + tabla * 17) % 48 == 0:
            return ("tierra", 1)
        if azar.random() < 0.02:
            return ("tierra", 1)
        return ("tierra", 3 if tabla % 2 == 0 else 2)
    l = habitacion(pared, techo, suelo)
    # losas de piedra delante de la forja
    for y in range(72, 100):
        for x in range(56, 128):
            if ((x - 56) % 12 == 0) or ((y - 72) % 9 == 8):
                l.px(x, y, "piedra", 1)
            else:
                l.px(x, y, "piedra", 2 if (x // 12 + y // 9) % 2 else 3)
    # forja: chimenea de piedra con la boca encendida
    l.rect(60, 10, 124, 74, "piedra", 2)
    for y in range(10, 75, 6):
        l.rect(60, y, 124, y, "piedra", 1)
    l.rect(60, 10, 61, 74, "piedra", 3)
    l.rect(56, 22, 128, 26, "piedra", 3)            # repisa
    l.rect(56, 26, 128, 27, "piedra", 1)
    for y in range(44, 72):                          # boca de la forja (arco)
        for x in range(72, 113):
            dx = (x + 0.5 - 92.5) / 20.5
            dy = (y - 56) / 12
            if y >= 56 or dx * dx + dy * dy <= 1.0:
                l.px(x, y, "oscuro", 0)
    # llamas: lenguas de fuego que suben desde las brasas
    for x in range(74, 111):
        alto = 8 + int(5 * abs(math.sin(x * 0.55)) + 3 * abs(math.sin(x * 0.23)))
        for k in range(alto):
            y = 71 - k
            t = k / alto
            tono = ("luz", 3) if t < 0.3 else (("luz", 2) if t < 0.55 else (("ambar", 2) if t < 0.8 else ("ambar", 1)))
            l.px(x, y, *tono)
    l.rect(72, 70, 112, 71, "ambar", 1)              # brasas del fondo
    for x in range(74, 111, 5):
        l.px(x, 70, "luz", 3)
    # carbón
    l.ovalo(138, 80, 9, 5, "piedra", plano=0)
    for (x, y) in [(134, 78), (140, 77), (137, 81), (143, 80)]:
        l.px(x, y, "piedra", 1)
    # herramientas colgadas
    l.rect(190, 30, 252, 33, "corteza", 2)
    for k, x in enumerate(range(196, 250, 12)):
        l.linea(x, 33, x, 52, "corteza", 3)
        if k % 2 == 0:
            l.rect(x - 4, 49, x + 4, 55, "piedra", 2)  # martillo
            l.rect(x - 4, 49, x + 4, 50, "piedra", 3)
        else:
            l.linea(x - 2, 52, x, 56, "piedra", 3); l.linea(x + 2, 52, x, 56, "piedra", 2)   # tenazas
    # banco de trabajo con dibujos de cetros
    l.rect(226, 72, 284, 80, "corteza", 3)
    l.rect(226, 81, 284, 98, "corteza", 1)
    l.rect(230, 82, 234, 98, "corteza", 2); l.rect(276, 82, 280, 98, "corteza", 2)
    l.rect(236, 70, 258, 76, "crema", 3)
    l.linea(240, 75, 252, 71, "corteza", 1)
    l.ovalo(253, 71, 2, 2, "brote", plano=2)
    l.rect(264, 68, 270, 74, "agua", 2)             # cuenco
    # barril de agua
    l.ovalo(50, 156, 11, 13, "corteza")
    l.rect(39, 150, 61, 151, "piedra", 2); l.rect(39, 162, 61, 163, "piedra", 2)
    l.ovalo(50, 145, 9, 3, "agua", plano=3)
    return _fondo_negro(l)


def yunque():
    l = Lienzo(28, 20)
    l.rect(9, 12, 19, 17, "piedra", 1)              # pie
    l.rect(7, 17, 21, 19, "piedra", 2)
    l.rect(4, 6, 24, 11, "piedra", 2)               # cuerpo
    l.rect(4, 6, 24, 7, "piedra", 3)
    l.rect(0, 7, 4, 9, "piedra", 2)                 # punta
    l.rect(0, 7, 4, 7, "piedra", 3)
    l.px(18, 6, "ambar", 3)                          # una chispa de la forja
    return l.imagen()


def brote_vida(fotograma):
    """El brote del Árbol de la Vida, en el centro del Claro."""
    l = Lienzo(20, 30)
    # tallo
    for y in range(10, 27):
        l.px(10 + int(math.sin(y * 0.4) * 1), y, "brote", 1)
    # hojas
    l.ovalo(6, 13, 4, 2.2, "brote")
    l.ovalo(14.5, 9, 4, 2.2, "brote")
    l.ovalo(10, 5, 2.4, 3.2, "brote")
    # luz que late
    brillo = [3, 2, 3, 3][fotograma]
    l.px(10, 4, "luz", brillo)
    for (x, y) in [(4 + fotograma % 2, 2), (16, 3 + fotograma % 2), (2, 9), (18, 13)]:
        l.px(x, y, "luz", 3 if fotograma % 2 else 2)
    # montoncito de tierra
    l.ovalo(10, 27, 6, 2.5, "tierra")
    l.sin_contorno = {"luz"}
    return l.imagen()


if __name__ == "__main__":
    destino = os.path.join(RAIZ, "arte", "mundos", "raiz", "aldea")
    os.makedirs(destino, exist_ok=True)
    gran_arbol().save(os.path.join(destino, "gran_arbol.png"))
    tira([casa_seta(False), casa_seta(True)]).save(os.path.join(destino, "casa_seta.png"))
    tira([taller(False), taller(True)]).save(os.path.join(destino, "taller.png"))
    tira([cocina(False), cocina(True)]).save(os.path.join(destino, "cocina.png"))
    tira([puesto(False), puesto(True)]).save(os.path.join(destino, "puesto.png"))
    tira([farol(0), farol(1)]).save(os.path.join(destino, "farol.png"))
    valla().save(os.path.join(destino, "valla.png"))
    tira([setitas(0), setitas(1)]).save(os.path.join(destino, "setitas.png"))
    for n in ("pino", "corteza", "juncia", "tawi", "mdiria"):
        estatua(n).save(os.path.join(destino, f"estatua_{n}.png"))
    interior_claro().save(os.path.join(destino, "interior_claro.png"))
    interior_casa_pino().save(os.path.join(destino, "interior_casa_pino.png"))
    interior_taller().save(os.path.join(destino, "interior_taller.png"))
    yunque().save(os.path.join(destino, "yunque.png"))
    tira([brote_vida(i) for i in range(4)]).save(os.path.join(destino, "brote_vida.png"))
    print("Aldea dibujada en", destino)
