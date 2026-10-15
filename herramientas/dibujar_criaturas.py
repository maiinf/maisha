"""
CRIATURAS DE GIZA en Raíz, dibujadas con detalle (paleta oficial de Raíz).

Uso:  python3 herramientas/dibujar_criaturas.py
Genera en arte/zonas/raiz/:
  petrino.png          Petrino 24x24, 8 fotogramas: quieto 1-2, andar 1-4, embestida, golpeado
  nucleo.png           Corazón de Giza 40x36, 4 fotogramas: sano, grieta 1, grieta 2, golpeado
  nucleo_pequeno.png   Corazón pequeño (zonas de práctica) 28x26, los mismos 4 fotogramas
  mzizi_cabeza.png     Mzizi 48x40, 11 fotogramas: cerrada (grietas 0-3), abierta (grietas 0-3),
                       golpeada cerrada, golpeada abierta, de madera (al vencerla)
  mzizi_cuerpo.png     segmentos del cuerpo 32x22: grande, mediano y pequeño (x2 variantes) y uno de madera
  agujero.png          agujero de Mzizi 48x28: dormido, aviso, abierto, sellado
  piedra.png           piedra que escupe Mzizi 12x12, 4 fotogramas girando

El ojo del Corazón no lleva pupila: la dibuja el juego, mirando a Maisha.
"""
import math
import os
import random

import numpy as np
from PIL import Image
from scipy import ndimage

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAL = {}
for linea in open(os.path.join(RAIZ, "arte", "paletas", "raiz.gpl"), encoding="utf-8"):
    partes = linea.split()
    if len(partes) >= 4 and partes[0].isdigit():
        PAL[" ".join(partes[3:])] = tuple(int(v) for v in partes[:3])

# Materiales: 4 tonos de oscuro a claro (el 0 hace de contorno)
MAT = {
    "piedra": ["Piedra 1", "Piedra 2", "Piedra 3", "Piedra 4"],
    "giza": ["Giza 1", "Giza 2", "Giza 3", "Giza 4"],
    "tierra": ["Tierra 1", "Tierra 2", "Tierra 3", "Tierra 4"],
    "liquen": ["Hierba 1", "Follaje 2", "Hierba 2", "Hierba 3"],
    "brote": ["Follaje 1", "Brote 1", "Brote 2", "Maisha 4"],
    "madera": ["Madera 1", "Madera 2", "Madera 3", "Madera 4"],
    "blanco": ["Extremos 1", "Pergamino 3", "Extremos 2", "Extremos 2"],
    "sombra": ["Extremos 1", "Extremos 1", "Giza 1", "Giza 1"],
}
BRILLA = {"giza", "blanco", "brote"}        # no generan contorno exterior (son luz)


class Hoja:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.mat = np.full((h, w), "", dtype=object)
        self.tono = np.zeros((h, w), dtype=int)
        self.yy, self.xx = np.mgrid[0:h, 0:w]

    # --- máscaras ---------------------------------------------------------
    def elipse(self, cx, cy, rx, ry):
        return ((self.xx + 0.5 - cx) / rx) ** 2 + ((self.yy + 0.5 - cy) / ry) ** 2 <= 1.0

    def poligono(self, puntos):
        from PIL import ImageDraw
        m = Image.new("1", (self.w, self.h))
        ImageDraw.Draw(m).polygon([tuple(p) for p in puntos], fill=1)
        return np.array(m, dtype=bool)

    def trazo(self, puntos, grosores):
        """Una línea gruesa que cambia de grosor (raíces, raicillas, patas)."""
        m = np.zeros((self.h, self.w), dtype=bool)
        for i in range(len(puntos) - 1):
            (x0, y0), (x1, y1) = puntos[i], puntos[i + 1]
            g0, g1 = grosores[i], grosores[i + 1]
            pasos = int(max(abs(x1 - x0), abs(y1 - y0)) * 3) + 1
            for k in range(pasos + 1):
                t = k / pasos
                x, y, g = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, g0 + (g1 - g0) * t
                m |= ((self.xx + 0.5 - x) ** 2 + (self.yy + 0.5 - y) ** 2) <= (g / 2) ** 2
        return m

    # --- pintar -------------------------------------------------------------
    def forma(self, mascara, mat, luz=(-0.55, -0.85), plano=None, separar=True, minimo=1, maximo=3, relieve=1.0, esfera=None):
        """Rellena la máscara con volumen: más luz arriba a la izquierda, sombra abajo a la derecha.
        esfera=(cx, cy, rx, ry): sombreado de un volumen redondo (más claro y definido)."""
        if not mascara.any():
            return
        if esfera is not None:
            ecx, ecy, erx, ery = esfera
            nx = (self.xx + 0.5 - ecx) / erx
            ny = (self.yy + 0.5 - ecy) / ery
            nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
            lx, ly, lz = -0.45, -0.6, 0.66
            s = nx * lx + ny * ly + nz * lz
            tonos = np.where(s > 0.62, 3, np.where(s > 0.22, 2, 1))
        elif plano is not None:
            tonos = np.full((self.h, self.w), plano)
        else:
            d = ndimage.distance_transform_edt(mascara)
            altura = np.sqrt(np.clip(d / max(1.0, d.max() * 0.75), 0, 1)) * relieve
            gy, gx = np.gradient(ndimage.gaussian_filter(altura, 0.8))
            luz_v = np.array(luz) / np.hypot(*luz)
            s = -(gx * luz_v[0] + gy * luz_v[1]) * 3.2
            tonos = np.where(s > 0.35, 3, np.where(s > -0.2, 2, 1))
        tonos = np.clip(tonos, minimo, maximo)
        if separar:
            # borde oscuro donde esta pieza se monta sobre otra ya pintada (abajo y a la derecha)
            borde = mascara & ~ndimage.binary_erosion(mascara)
            debajo = self.mat != ""
            fuera_abajo = np.zeros_like(mascara)
            fuera_abajo[:-1, :] |= ~mascara[1:, :]
            fuera_abajo[:, :-1] |= ~mascara[:, 1:]
            sep = borde & debajo & fuera_abajo
            tonos = np.where(sep, 0, tonos)
        self.mat[mascara] = mat
        self.tono[mascara] = tonos[mascara]

    def px(self, x, y, mat, tono):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.mat[y, x] = mat
            self.tono[y, x] = tono

    def oscurecer(self, mascara, cuanto=1, solo=None, minimo=0):
        m = mascara & (self.mat != "")
        if solo:
            m &= np.isin(self.mat, solo)
        self.tono[m] = np.maximum(minimo, self.tono[m] - cuanto)

    def aclarar(self, mascara, cuanto=1, solo=None):
        m = mascara & (self.mat != "")
        if solo:
            m &= np.isin(self.mat, solo)
        self.tono[m] = np.minimum(3, self.tono[m] + cuanto)

    def linea(self, puntos, mat, tono, solo_encima=False):
        for i in range(len(puntos) - 1):
            (x0, y0), (x1, y1) = puntos[i], puntos[i + 1]
            pasos = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
            for k in range(pasos + 1):
                t = k / pasos
                x, y = int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t))
                if 0 <= x < self.w and 0 <= y < self.h and (not solo_encima or self.mat[y, x] != ""):
                    self.mat[y, x] = mat
                    self.tono[y, x] = tono

    def grieta(self, puntos, ancha=False, brillo=3):
        """Grieta de Giza: borde oscuro, interior violeta y un hilo de luz en el centro."""
        if ancha:
            for (x, y) in _puntos_de(puntos):
                for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    if 0 <= x + dx < self.w and 0 <= y + dy < self.h and self.mat[y + dy, x + dx] not in ("", "giza"):
                        self.mat[y + dy, x + dx] = "giza"
                        self.tono[y + dy, x + dx] = 0
            self.linea(puntos, "giza", brillo, solo_encima=True)
        else:
            self.linea(puntos, "giza", 1, solo_encima=True)
            mitad = puntos[len(puntos) // 2]
            mx, my = int(round(mitad[0])), int(round(mitad[1]))
            if 0 <= mx < self.w and 0 <= my < self.h and self.mat[my, mx] != "":
                self.px(mx, my, "giza", brillo)

    def imagen(self, contorno=True):
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        p = img.load()
        mat, tono = self.mat.copy(), self.tono.copy()
        if contorno:
            lleno = (mat != "") & ~np.isin(mat, list(BRILLA))
            fuera = (mat == "") & ndimage.binary_dilation(lleno, structure=[[0, 1, 0], [1, 1, 1], [0, 1, 0]])
            for y, x in zip(*np.nonzero(fuera)):
                for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                    if 0 <= x + dx < self.w and 0 <= y + dy < self.h and lleno[y + dy, x + dx]:
                        mat[y, x] = self.mat[y + dy, x + dx]
                        tono[y, x] = 0
                        break
        for y in range(self.h):
            for x in range(self.w):
                if mat[y, x]:
                    p[x, y] = PAL[MAT[mat[y, x]][tono[y, x]]] + (255,)
        return img


def _puntos_de(puntos):
    out = []
    for i in range(len(puntos) - 1):
        (x0, y0), (x1, y1) = puntos[i], puntos[i + 1]
        pasos = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for k in range(pasos + 1):
            t = k / pasos
            out.append((int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t))))
    return out


def tira(imagenes):
    w = max(i.width for i in imagenes)
    h = max(i.height for i in imagenes)
    hoja = Image.new("RGBA", (w * len(imagenes), h), (0, 0, 0, 0))
    for i, im in enumerate(imagenes):
        hoja.paste(im, (i * w + (w - im.width) // 2, h - im.height))
    return hoja


def blanco(img):
    """Fotograma de «golpeado»: la figura en blanco con un contorno oscuro."""
    a = np.array(img)
    lleno = a[:, :, 3] > 0
    borde = lleno & ~ndimage.binary_erosion(lleno)
    out = np.zeros_like(a)
    out[lleno] = PAL["Extremos 2"] + (255,)
    out[borde] = PAL["Pergamino 3"] + (255,)
    return Image.fromarray(out)


def corteza(h, mascara, azar, paso=3, inclinacion=0.15, desde=0):
    """Surcos verticales de corteza petrificada (un tono más oscuros), algo ondulados."""
    for y in range(h.h):
        for x in range(h.w):
            if mascara[y, x]:
                u = x + math.sin(y * 0.35 + x * 0.1) * 0.8 + y * inclinacion
                if (u + desde) % paso < 0.9 and azar.random() < 0.85:
                    h.oscurecer(_uno(h, x, y), 1, minimo=1)


def _uno(h, x, y):
    m = np.zeros((h.h, h.w), dtype=bool)
    m[y, x] = True
    return m


# =============================================================================
# PETRINO (24x24): un trozo arrancado de la raíz que Giza obliga a caminar
# =============================================================================

def petrino(pose):
    """pose: quieto0, quieto1, andar0..3, embestida"""
    h = Hoja(24, 24)
    azar = random.Random(7)
    cx = 12
    respira = 1 if pose == "quieto1" else 0
    embiste = pose == "embestida"
    paso = int(pose[-1]) if pose.startswith("andar") else -1
    bote = 1 if paso in (1, 3) else 0
    baja = respira + bote + (1 if embiste else 0)
    # --- patas de raicilla (detrás del cuerpo)
    # pie izquierdo y derecho: (adelante, levantado) en cada fotograma del paso
    pies = {0: ((-2, 0), (2, 0)), 1: ((0, 2), (0, 0)), 2: ((2, 0), (-2, 0)), 3: ((0, 0), (0, 2)), -1: ((0, 0), (0, 0))}
    (ai, li), (ad, ld) = pies[paso]
    if embiste:
        (ai, li), (ad, ld) = (-2, 0), (2, 0)
    for lado, adelante, levanta in ((-1, ai, li), (1, ad, ld)):
        x0 = cx + lado * 3
        pie = (cx + lado * 6 + adelante, 22 - levanta)
        h.forma(h.trazo([(x0, 17), (x0 + lado * 2 + adelante * 0.5, 20), pie], [3.2, 2.6, 2.0]), "piedra", maximo=2)
        h.px(pie[0] + lado, pie[1] + 1, "piedra", 1)                    # deditos de raíz
        h.px(pie[0] - lado, pie[1] + 1, "piedra", 2)
    # --- cuerpo: tocón, más ancho abajo
    arriba = 6 + baja
    contorno = [(cx - 6, arriba + 2), (cx - 7, arriba + 6), (cx - 8, 15), (cx - 7.5, 19 - baja * 0.3),
                (cx + 7.5, 19 - baja * 0.3), (cx + 8, 15), (cx + 7, arriba + 6), (cx + 6, arriba + 2)]
    # corona rota en astillas
    astillas = [(cx - 6, arriba + 2), (cx - 5, arriba - 1), (cx - 3, arriba + 1), (cx - 1, arriba - 3),
                (cx + 1, arriba), (cx + 3, arriba - 2), (cx + 5, arriba + 1), (cx + 6, arriba + 2)]
    cuerpo = h.poligono(contorno + astillas[::-1])
    cuerpo |= h.poligono([(cx - 6, arriba + 2)] + astillas + [(cx + 6, arriba + 4), (cx - 6, arriba + 4)])
    h.forma(cuerpo, "piedra", esfera=(cx - 1.5, arriba + 7, 9.0, 10.5))
    corteza(h, cuerpo & (h.yy >= arriba + 4), azar, paso=3, inclinacion=0.12)
    # el corte de arriba: anillos de la madera hechos piedra
    h.forma(h.elipse(cx, arriba + 2.2, 5.5, 1.6) & cuerpo, "piedra", plano=3, separar=False)
    h.px(cx - 1, arriba + 2, "piedra", 2)
    h.px(cx + 2, arriba + 2, "piedra", 2)
    # surcos de corteza y aristas iluminadas arriba a la izquierda
    for x in (cx - 5, cx - 2, cx + 3, cx + 6):
        h.linea([(x, arriba + 5 + (x % 2)), (x + (1 if x > cx else -1) * 0.5, 17 - baja * 0.3)], "piedra", 1, solo_encima=True)
    h.aclarar(h.elipse(cx - 4.5, arriba + 6.5, 1.8, 3.5) & cuerpo, 1)
    # nudo como nariz
    h.forma(h.elipse(cx + 0.5, arriba + 8.0, 1.6, 1.3), "piedra", maximo=3)
    h.px(cx + 1, arriba + 8.5, "piedra", 0)
    # ojos de grieta
    ojo_y = arriba + 6
    for ox in (-3, 3):
        h.px(cx + ox - 2, ojo_y, "giza", 0)
        h.px(cx + ox - 1, ojo_y, "giza", 3)
        h.px(cx + ox + 1, ojo_y, "giza", 3)
        h.px(cx + ox + 2, ojo_y, "giza", 0)
        h.px(cx + ox, ojo_y + 1, "giza", 2)
        h.px(cx + ox - 1, ojo_y + 1, "giza", 1)
        h.px(cx + ox + 1, ojo_y + 1, "giza", 1)
    h.px(cx - 3, ojo_y, "blanco", 2)
    h.px(cx + 3, ojo_y, "blanco", 2)
    # cejas de corteza, fruncidas
    h.linea([(cx - 6, ojo_y - 3), (cx - 2, ojo_y - 1)], "piedra", 0, solo_encima=True)
    h.linea([(cx + 6, ojo_y - 3), (cx + 2, ojo_y - 1)], "piedra", 0, solo_encima=True)
    h.linea([(cx - 6, ojo_y - 4), (cx - 3, ojo_y - 3)], "piedra", 3, solo_encima=True)
    h.linea([(cx + 6, ojo_y - 4), (cx + 3, ojo_y - 3)], "piedra", 3, solo_encima=True)
    if embiste:
        for ox in (-3, 3):
            h.px(cx + ox - 1, ojo_y - 1, "giza", 3)
            h.px(cx + ox + 1, ojo_y - 1, "giza", 3)
    # corazón violeta del pecho y sus venas (dentro del torso, sin salirse por abajo)
    pecho = (cx - 1, arriba + 10)
    h.grieta([(pecho[0] - 3, pecho[1] - 1), (pecho[0] - 1, pecho[1]), (pecho[0], pecho[1] + 1), (pecho[0] + 2, pecho[1] + 2)])
    h.px(pecho[0], pecho[1], "giza", 3)
    h.px(pecho[0] - 1, pecho[1] + 1, "giza", 2)
    # líquen musgoso y una piedrecita encima
    for (x, y) in ((cx - 6, arriba + 10), (cx - 5, arriba + 11), (cx + 5, arriba + 12), (cx + 6, arriba + 11)):
        h.px(x, y, "liquen", 2)
    h.px(cx - 5, arriba + 10, "liquen", 3)
    h.px(cx + 5, arriba + 11, "liquen", 3)
    h.forma(h.elipse(cx + 3, arriba - 2.5, 1.6, 1.2), "piedra", maximo=3)
    # brazos de raicilla
    brazo = -2 if embiste else (1 if paso in (0, 2) else 0)
    h.forma(h.trazo([(cx - 7, arriba + 8), (cx - 10, arriba + 6 + brazo), (cx - 11, arriba + 3 + brazo)], [2.2, 1.6, 1.2]), "piedra", maximo=3)
    h.forma(h.trazo([(cx + 7, arriba + 8), (cx + 10, arriba + 9 - brazo), (cx + 11, arriba + 12 - brazo)], [2.2, 1.6, 1.2]), "piedra", maximo=2)
    h.px(cx - 12, arriba + 2 + brazo, "piedra", 2)
    return h.imagen()


# =============================================================================
# CORAZÓN DE GIZA: tocón de piedra con el ojo de Giza (grande 40x36 y pequeño 28x26)
# =============================================================================

def corazon(grietas, grande=True):
    W, H = (40, 36) if grande else (28, 26)
    e = 1.0 if grande else 0.68
    h = Hoja(W, H)
    azar = random.Random(11)
    cx = W / 2
    suelo = H - 2
    # raíces-garra que se agarran al suelo (detrás)
    for (lado, largo, caida) in ((-1, 15, 2), (1, 15, 3), (-1, 10, 4), (1, 9, 4), (0.3, 6, 5)):
        x0 = cx + lado * 6 * e
        x1 = cx + lado * largo * e
        h.forma(h.trazo([(x0, suelo - 6 * e), ((x0 + x1) / 2, suelo - 2 * e), (x1, suelo + caida * 0.3 * e - 1)],
                        [5 * e, 3.6 * e, 1.6]), "piedra", maximo=2)
        h.px(x1 + lado, suelo, "piedra", 1)
    # el tocón
    ancho_abajo, ancho_arriba = 12 * e, 9 * e
    arriba = 6 * e
    corona = [(cx - ancho_arriba, arriba + 4 * e)]
    pasos = 9
    for i in range(1, pasos):
        x = cx - ancho_arriba + 2 * ancho_arriba * i / pasos
        alto = arriba + (azar.choice((0, 3, 1, 5, 2)) if i % 2 else azar.choice((2, 4))) * e
        corona.append((x, alto))
    corona.append((cx + ancho_arriba, arriba + 3 * e))
    cuerpo = h.poligono(corona + [(cx + ancho_arriba + 1 * e, suelo - 10 * e), (cx + ancho_abajo, suelo - 3 * e),
                                  (cx - ancho_abajo, suelo - 3 * e), (cx - ancho_arriba - 1 * e, suelo - 10 * e)])
    h.forma(cuerpo, "piedra")
    # anillos del corte (arriba), surcos de corteza y nudos
    h.forma(h.elipse(cx, arriba + 4.5 * e, ancho_arriba - 1.5, 2.2 * e) & cuerpo, "piedra", plano=3, separar=False)
    for k in range(1, 3):
        anillo = h.elipse(cx, arriba + 4.5 * e, (ancho_arriba - 1.5) * k / 3, 2.2 * e * k / 3)
        h.oscurecer(anillo & ~h.elipse(cx, arriba + 4.5 * e, (ancho_arriba - 1.5) * k / 3 - 1, 2.2 * e * k / 3 - 0.7), 1, minimo=2)
    surcos = [-9, -6, -3.5, 4, 7, 9.5]
    for s in surcos:
        x = cx + s * e
        h.linea([(x, arriba + 8 * e), (x + s * 0.08, suelo - 5 * e), (x + s * 0.18, suelo - 3 * e)], "piedra", 1, solo_encima=True)
    for (nx, ny) in ((-6.5, 20), (7, 14)):
        h.forma(h.elipse(cx + nx * e, ny * e, 1.7 * e + 0.3, 1.3 * e + 0.3), "piedra", maximo=3)
        h.px(cx + nx * e + 0.4, ny * e + 0.4, "piedra", 0)
    # líquen muerto
    for (lx, ly) in ((-8, 26), (-9, 25), (-7, 27), (8, 22), (9, 23)):
        h.px(cx + lx * e, ly * e, "liquen", 2 + (lx % 2))
    # la grieta vertical con el ojo de Giza (almendra; la pupila la pone el juego)
    oy = 19 * e
    alto_ojo, ancho_ojo = 6.5 * e, 4.2 * e
    almendra = h.poligono([(cx - ancho_ojo, oy), (cx - ancho_ojo * 0.5, oy - alto_ojo * 0.55), (cx, oy - alto_ojo),
                           (cx + ancho_ojo * 0.5, oy - alto_ojo * 0.55), (cx + ancho_ojo, oy),
                           (cx + ancho_ojo * 0.5, oy + alto_ojo * 0.55), (cx, oy + alto_ojo), (cx - ancho_ojo * 0.5, oy + alto_ojo * 0.55)])
    parpado = ndimage.binary_dilation(almendra) & ~almendra
    h.mat[parpado & cuerpo] = "sombra"
    h.tono[parpado & cuerpo] = 0
    h.forma(almendra, "giza", plano=1, separar=False)
    h.forma(h.elipse(cx, oy, 2.6 * e + 0.4, 3.6 * e + 0.4), "giza", plano=2, separar=False)
    h.forma(h.elipse(cx, oy, 1.6 * e + 0.3, 2.4 * e + 0.3), "giza", plano=3, separar=False)
    # la grieta sigue por encima y por debajo del ojo
    h.grieta([(cx, oy - alto_ojo), (cx - 1, oy - alto_ojo - 3 * e), (cx, arriba + 5 * e)])
    h.grieta([(cx, oy + alto_ojo), (cx + 1, oy + alto_ojo + 3 * e), (cx, suelo - 4 * e)])
    # venas que crecen con cada semilla
    venas = [
        [[(cx - 3 * e, oy - 3 * e), (cx - 7 * e, oy - 6 * e), (cx - 8 * e, oy - 10 * e)],
         [(cx + 3 * e, oy + 3 * e), (cx + 7 * e, oy + 5 * e), (cx + 9 * e, oy + 9 * e)]],
        [[(cx + 3 * e, oy - 2 * e), (cx + 8 * e, oy - 5 * e), (cx + 9 * e, oy - 9 * e)],
         [(cx - 3 * e, oy + 3 * e), (cx - 6 * e, oy + 7 * e), (cx - 10 * e, oy + 8 * e)],
         [(cx - 7 * e, oy - 6 * e), (cx - 11 * e, oy - 5 * e)]],
    ]
    for g in range(grietas):
        for v in venas[g]:
            h.grieta(v, ancha=grande, brillo=3)
    if grietas == 2:
        # trozos que ya se han caído
        for (x, y) in ((cx - ancho_arriba + 1, arriba + 6 * e), (cx + ancho_arriba - 2, arriba + 9 * e)):
            h.mat[int(y), int(x)] = ""
            h.mat[int(y) + 1, int(x)] = ""
    return h.imagen()


# =============================================================================
# MZIZI, LA RAÍZ DEL ARCO
# =============================================================================

def mzizi_cabeza(grietas=0, abierta=False, madera=False):
    """La punta de la raíz del Arco, hacia arriba. Cerrada: una punta de raíz con dos costuras por las que
    se escapa la luz de Giza. Abierta: la punta se parte en tres gajos y enseña un anillo de dientes
    de astilla y la garganta violeta. Los ojos son grietas bajo placas de corteza, a los lados."""
    W, H = 48, 46
    h = Hoja(W, H)
    azar = random.Random(23)
    mat = "madera" if madera else "piedra"
    cx = 24
    # --- el bulbo: del cuello (abajo) a lo más ancho y luego la punta
    def ancho(y):
        if y >= 30:
            return 11 + (46 - y) * 0.35                       # el cuello se ensancha hacia el bulbo
        if y >= 18:
            return 17 - (30 - y) * 0.05
        return max(0.0, 16.4 * math.sqrt(max(0.0, (y - 1.5) / 16.5)))   # la punta
    bulbo = np.zeros((H, W), dtype=bool)
    for y in range(H):
        a = ancho(y + 0.5)
        bulbo[y, int(round(cx - a)):int(round(cx + a))] = True
    if abierta:
        # la punta se abre: sin la parte de arriba del bulbo
        bulbo &= h.yy >= 17
    h.forma(bulbo, mat, esfera=(cx - 1, 24, 19, 22))
    # surcos en espiral: la raíz está retorcida
    for k in range(-6, 7):
        puntos = []
        for y in range(4 if not abierta else 18, 45):
            a = ancho(y)
            if a < 2:
                continue
            u = (k / 6.0) + (y - 24) * 0.035
            if abs(u) >= 0.97:
                continue
            puntos.append((cx + math.sin(u * math.pi / 2) * a * 0.98, y))
        for i, (x, y) in enumerate(puntos):
            if (i + k * 5) % 9 < 7 and bulbo[int(y), int(x)]:
                h.oscurecer(_uno(h, int(x), int(y)), 1, minimo=1)
    # bandas del cuello (anillos de crecimiento)
    for y0 in (36, 41):
        anillo = (abs(h.yy - y0 - (h.xx - cx) ** 2 * 0.006) < 0.8) & bulbo
        h.oscurecer(anillo, 1, minimo=0)
        h.aclarar(np.roll(anillo, -1, axis=0) & bulbo, 1)
    if abierta:
        # garganta: un pozo oscuro con la luz violeta al fondo
        boca = h.elipse(cx, 18.5, 13.5, 6)
        h.forma(boca, "sombra", plano=0, separar=False)
        h.forma(h.elipse(cx, 19, 8.5, 3.6), "giza", plano=1, separar=False)
        h.forma(h.elipse(cx, 19.3, 5, 2), "giza", plano=2, separar=False)
        h.forma(h.elipse(cx, 19.4, 2.4, 1), "giza", plano=3, separar=False)
        # anillo de dientes de astilla alrededor de la boca
        for k in range(14):
            a = k / 14 * math.tau
            bx, by = cx + math.cos(a) * 12.5, 18.5 + math.sin(a) * 5.4
            tx, ty = cx + math.cos(a) * 9.5, 18.8 + math.sin(a) * 3.6
            ancho_d = 1.4 if k % 2 else 1.0
            nx_, ny_ = -math.sin(a) * ancho_d, math.cos(a) * ancho_d * 0.5
            h.forma(h.poligono([(bx + nx_, by + ny_), (bx - nx_, by - ny_), (tx, ty)]), mat, minimo=2, maximo=3, separar=False)
        # los tres gajos de la punta, abiertos hacia fuera
        for (ang, dx, largo) in ((-0.95, -12, 15), (0.95, 12, 15), (0.0, 0, 11)):
            if dx == 0:
                gajo = h.poligono([(cx - 6, 13.5), (cx - 4, 6), (cx, 1), (cx + 4, 6), (cx + 6, 13.5)])
                h.forma(gajo, mat, esfera=(cx, 9, 7, 9))
                h.linea([(cx, 2), (cx, 12)], mat, 1, solo_encima=True)
            else:
                lado = 1 if dx > 0 else -1
                base = [(cx + lado * 9, 15), (cx + lado * 15, 20)]
                punta = (cx + lado * 23, 6)
                gajo = h.poligono([base[0], (cx + lado * 14, 7), punta, (cx + lado * 22, 13), base[1]])
                h.forma(gajo, mat, esfera=(cx + lado * 16, 12, 9, 10))
                h.linea([(cx + lado * 12, 15), (cx + lado * 20, 8)], mat, 1, solo_encima=True)
                # dientes en el borde interior del gajo
                for t in (0.3, 0.6):
                    x = cx + lado * (9 + 6 * t)
                    y = 15 - 8 * t
                    h.forma(h.poligono([(x, y), (x - lado * 3, y + 1), (x, y + 2)]), mat, minimo=2, maximo=3, separar=False)
                if not madera:
                    h.grieta([(cx + lado * 13, 14), (cx + lado * 17, 11), (cx + lado * 20, 9)])
    else:
        # punta cerrada: dos costuras por las que se escapa la luz de Giza
        for lado in (-1, 1):
            costura = [(cx + lado * 1, 3), (cx + lado * 4, 9), (cx + lado * 6, 15), (cx + lado * 7, 20)]
            if madera:
                h.linea(costura, mat, 0, solo_encima=True)
            else:
                h.grieta(costura, ancha=True, brillo=3)
        h.aclarar(h.elipse(cx - 5, 9, 2, 4) & bulbo, 1)
    # placas de corteza (cejas) y ojos de grieta, a los dos lados del bulbo
    for lado in (-1, 1):
        ox, oy = cx + lado * 10, 27
        placa = h.poligono([(ox - lado * 4, oy - 4), (ox + lado * 1, oy - 6), (ox + lado * 7, oy - 4), (ox + lado * 6, oy - 2), (ox - lado * 4, oy - 2)])
        h.forma(placa, mat, minimo=2, maximo=3)
        h.linea([(ox - lado * 4, oy - 2), (ox + lado * 6, oy - 2)], mat, 0, solo_encima=True)
        ojo = h.poligono([(ox - lado * 3.5, oy), (ox, oy - 1.5), (ox + lado * 4, oy - 0.5), (ox + lado * 2, oy + 1.8), (ox - lado * 2, oy + 1.5)])
        hondo = ndimage.binary_dilation(ojo) & ~ojo & bulbo
        h.mat[hondo] = mat
        h.tono[hondo] = 0
        if madera:
            h.forma(ojo, "madera", plano=0, separar=False)
        else:
            h.forma(ojo, "giza", plano=2, separar=False)
            h.px(ox, oy, "giza", 3)
            h.px(ox + lado, oy, "giza", 3)
            h.px(ox, oy, "blanco", 2)
    # nudos
    for (nx_, ny_) in ((-4, 33), (6, 38)):
        h.forma(h.elipse(cx + nx_, ny_, 2, 1.6), mat, maximo=3)
        h.px(cx + nx_ + 0.5, ny_ + 0.5, mat, 0)
    # raicillas colgando del bulbo (bigotes) y alguna que sube
    for (x0, y0, lado, largo) in ((-15, 30, -1, 9), (-13, 33, -1, 7), (15, 30, 1, 9), (13, 34, 1, 6), (-16, 24, -1, 6), (16, 23, 1, 5)):
        puntos = [(cx + x0, y0)]
        for k in range(1, largo):
            puntos.append((cx + x0 + lado * (k * 0.7 + math.sin(k) * 0.6), y0 + k * 0.9))
        h.linea(puntos, mat, 1)
        h.px(puntos[-1][0], puntos[-1][1], mat, 2)
    # líquen muerto
    for (x, y, t) in ((-12, 20, 2), (-13, 21, 3), (-11, 21, 2), (-12, 22, 2), (11, 36, 2), (12, 36, 3), (12, 37, 2)):
        if h.mat[y, cx + x]:
            h.px(cx + x, y, "liquen", t)
    # la hojita que aún vive en un lado de la cabeza
    hx, hy = cx + 14, 19 if not abierta else 21
    h.px(hx, hy, mat, 1)
    h.px(hx + 1, hy - 1, "brote", 1)
    h.px(hx + 2, hy - 2, "brote", 2)
    h.px(hx + 3, hy - 2, "brote", 3)
    h.px(hx + 2, hy - 3, "brote", 2)
    h.px(hx + 3, hy - 3, "brote", 1)
    # vena violeta que sube por el cuello
    if not madera:
        h.grieta([(cx - 3, 45), (cx - 4, 40), (cx - 2, 35), (cx - 3, 31)], ancha=True)
    # grietas por los golpes
    trazos = [
        [[(cx + 4, 30), (cx + 7, 34), (cx + 6, 39)]],
        [[(cx - 9, 31), (cx - 11, 36), (cx - 9, 41)], [(cx + 13, 24), (cx + 15, 28)]],
        [[(cx - 1, 22), (cx + 2, 26), (cx + 1, 31), (cx + 3, 35)], [(cx - 14, 26), (cx - 16, 31)], [(cx + 9, 41), (cx + 11, 44)]],
    ]
    for g in range(min(grietas, 3)):
        for t in trazos[g]:
            if madera:
                if g == 0:
                    h.linea(t, "brote", 1, solo_encima=True)
            else:
                h.linea(t, "giza", 2, solo_encima=True)
                for (x, y) in t[1:-1]:
                    h.px(x, y, "giza", 3)
                h.px(t[-1][0], t[-1][1], "giza", 1)
    return h.imagen()


def mzizi_segmento(tam, variante, madera=False):
    """Un tramo del cuerpo visto de frente: un trozo de raíz con su nudo, surcos y vena."""
    W, H = 32, 22
    h = Hoja(W, H)
    azar = random.Random(40 + tam * 3 + variante)
    mat = "madera" if madera else "piedra"
    rx, ry = {0: (14, 9.5), 1: (11.5, 8), 2: (9, 6.5)}[tam]
    cx, cy = W / 2, H / 2
    cuerpo = h.elipse(cx, cy, rx, ry)
    h.forma(cuerpo, mat, esfera=(cx - 0.5, cy - 0.5, rx + 1, ry + 1.5))
    # surcos en espiral, como la cabeza (la raíz está retorcida)
    for k in range(-5, 6):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            u = k / 5.0 + (y - cy) * 0.05 + variante * 0.08
            if abs(u) >= 0.95:
                continue
            x = cx + math.sin(u * math.pi / 2) * rx * 0.98
            if (y + k * 3) % 7 < 5 and 0 <= int(x) < W and cuerpo[y, int(x)]:
                h.oscurecer(_uno(h, int(x), y), 1, minimo=1)
    # anillo / nudo de crecimiento
    yb = cy + (2 if variante else -2)
    anillo = (abs(h.yy - yb - (h.xx - cx) ** 2 * 0.012) < 0.7) & cuerpo
    h.oscurecer(anillo, 1, minimo=0)
    h.aclarar(np.roll(anillo, 1, axis=0) & cuerpo, 1)
    # raicilla lateral
    lado = 1 if variante else -1
    h.forma(h.trazo([(cx + lado * (rx - 1), cy), (cx + lado * (rx + 3), cy - 2), (cx + lado * (rx + 4), cy - 5)], [2.4, 1.6, 1.0]), mat, maximo=2)
    # nudo saliente
    if variante:
        h.forma(h.elipse(cx - rx * 0.4, cy + 1, 2, 1.6), mat, maximo=3)
    # vena violeta (o un poco de musgo, si es de madera)
    if madera:
        for (x, y) in ((cx - 3, cy - 2), (cx - 2, cy - 2), (cx + 4, cy + 2)):
            h.px(x, y, "brote", 1)
    else:
        h.grieta([(cx - 2 + variante * 3, cy - ry + 2), (cx - 1 + variante * 3, cy), (cx + 1 + variante * 3, cy + ry - 2)], ancha=tam == 0)
    # líquen muerto
    if tam == 0 and not madera:
        for (x, y) in ((cx + rx * 0.5, cy - 3), (cx + rx * 0.5 + 1, cy - 3), (cx + rx * 0.55, cy - 2)):
            h.px(x, y, "liquen", 2)
    return h.imagen()


def agujero(estado):
    """estado: dormido, aviso, abierto, sellado"""
    W, H = 48, 28
    h = Hoja(W, H)
    azar = random.Random(5)
    cx, cy = W / 2, H / 2 + 2
    if estado == "sellado":
        # tierra blanda con brotes: ya no hay Giza
        h.forma(h.elipse(cx, cy, 13, 5), "tierra", minimo=2)
        for (x, y) in ((cx - 6, cy - 1), (cx + 2, cy - 2), (cx + 7, cy + 1), (cx - 2, cy + 2)):
            h.px(x, y, "brote", 2)
            h.px(x + 1, y - 1, "brote", 1)
        return h.imagen()
    # tierra levantada alrededor (montículo)
    h.forma(h.elipse(cx, cy, 20, 9), "tierra", relieve=0.8)
    # terrones sueltos
    for _ in range(9):
        a = azar.uniform(0, math.tau)
        x, y = cx + math.cos(a) * azar.uniform(17, 22), cy + math.sin(a) * azar.uniform(7, 10)
        h.forma(h.elipse(x, y, 1.6, 1.2), "tierra", maximo=3)
    # astillas de raíz de piedra en el borde
    for k in range(8):
        a = math.pi * (1.05 + k * 0.12) if k < 5 else math.pi * (0.1 + (k - 5) * 0.35)
        x0, y0 = cx + math.cos(a) * 13, cy + math.sin(a) * 5
        x1, y1 = cx + math.cos(a) * 19, cy + math.sin(a) * 8 - 3
        h.forma(h.trazo([(x0, y0), (x1, y1)], [2.6, 1.0]), "piedra", maximo=3)
    if estado == "dormido":
        h.forma(h.elipse(cx, cy, 11, 4), "tierra", plano=1, separar=False)
        for t in ([(cx - 8, cy), (cx - 3, cy - 1), (cx + 2, cy + 1), (cx + 8, cy)],):
            h.linea(t, "tierra", 0, solo_encima=True)
    elif estado == "aviso":
        h.forma(h.elipse(cx, cy, 11, 4), "tierra", plano=1, separar=False)
        for t in ([(cx - 10, cy), (cx - 4, cy - 1), (cx + 1, cy + 1), (cx + 9, cy - 1)],
                  [(cx - 2, cy - 3), (cx, cy + 3)], [(cx - 14, cy + 2), (cx - 9, cy)], [(cx + 9, cy - 1), (cx + 15, cy + 2)]):
            h.grieta(t, ancha=True)
        for (x, y) in ((cx - 12, cy - 4), (cx + 10, cy - 5), (cx + 3, cy - 6)):
            h.forma(h.elipse(x, y, 1.2, 1.0), "piedra", maximo=3)
    else:
        # abierto: un pozo hondo con el resplandor de Giza al fondo
        h.forma(h.elipse(cx, cy, 13, 5.5), "sombra", plano=0, separar=False)
        h.forma(h.elipse(cx, cy + 0.8, 9, 3.4), "giza", plano=1, separar=False)
        h.forma(h.elipse(cx, cy + 1.2, 5, 1.8), "giza", plano=2, separar=False)
        borde = h.elipse(cx, cy, 13, 5.5) & ~h.elipse(cx, cy + 0.6, 12, 4.6)
        h.mat[borde] = "tierra"
        h.tono[borde] = 0
    return h.imagen()


def piedra(giro):
    W = 12
    h = Hoja(W, W)
    puntos = [(2, 5), (4, 2), (8, 2), (10, 5), (9, 9), (5, 10), (2, 8)]
    a = giro * math.pi / 4
    c = W / 2 - 0.5
    rot = [(c + (x - c) * math.cos(a) - (y - c) * math.sin(a), c + (x - c) * math.sin(a) + (y - c) * math.cos(a)) for (x, y) in puntos]
    h.forma(h.poligono(rot), "piedra")
    cen = [(c + (x - c) * math.cos(a) - (y - c) * math.sin(a), c + (x - c) * math.sin(a) + (y - c) * math.cos(a))
           for (x, y) in ((4, 4), (6, 6), (6, 8))]
    h.grieta(cen)
    h.px(cen[1][0], cen[1][1], "giza", 3)
    return h.imagen()


if __name__ == "__main__":
    destino = os.path.join(RAIZ, "arte", "zonas", "raiz")
    os.makedirs(destino, exist_ok=True)
    poses = ["quieto0", "quieto1", "andar0", "andar1", "andar2", "andar3", "embestida"]
    pet = [petrino(p) for p in poses]
    tira(pet + [blanco(pet[0])]).save(os.path.join(destino, "petrino.png"))
    for grande, nombre in ((True, "nucleo.png"), (False, "nucleo_pequeno.png")):
        c0 = corazon(0, grande)
        tira([c0, corazon(1, grande), corazon(2, grande), blanco(c0)]).save(os.path.join(destino, nombre))
    cabezas = [mzizi_cabeza(g, False) for g in range(4)] + [mzizi_cabeza(g, True) for g in range(4)]
    cabezas += [blanco(cabezas[0]), blanco(cabezas[4]), mzizi_cabeza(3, False, madera=True)]
    tira(cabezas).save(os.path.join(destino, "mzizi_cabeza.png"))
    segs = [mzizi_segmento(t, v) for t in (0, 1, 2) for v in (0, 1)] + [mzizi_segmento(0, 0, True), mzizi_segmento(1, 1, True), mzizi_segmento(2, 0, True)]
    tira(segs).save(os.path.join(destino, "mzizi_cuerpo.png"))
    tira([agujero(e) for e in ("dormido", "aviso", "abierto", "sellado")]).save(os.path.join(destino, "agujero.png"))
    tira([piedra(g) for g in range(4)]).save(os.path.join(destino, "piedra.png"))
    print("Criaturas de Giza dibujadas en", destino)
