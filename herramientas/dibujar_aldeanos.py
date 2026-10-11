"""
ALDEANOS DE RAÍZ dibujados píxel a píxel (paleta oficial de Raíz).

Cada aldeano se monta con formas sencillas (óvalos sombreados con luz arriba a la izquierda)
y un contorno selectivo: cada material se contornea con su tono más oscuro.

Uso:  python3 herramientas/dibujar_aldeanos.py
Genera arte/personajes/aldeanos/<nombre>_frente.png (24x32, los pies abajo en el centro)
"""
import math
import os
from PIL import Image

# Materiales: tonos de oscuro (contorno) a claro, todos de la paleta de Raíz
MATERIALES = {
    "tortuga":  ["1D2E18", "3F582F", "6A8246", "9AA95F"],   # piel (Hierba 1-4)
    "concha":   ["251812", "492E23", "6D4534", "905C45"],   # Madera
    "musgo":    ["152814", "355029", "5D793E", "90A153"],   # Follaje
    "cana":     ["5C3E26", "C9B07E", "E2CEA0", "FFF8E8"],   # cejas blancas (Pergamino)
    "seta":     ["B02531", "D53946", "DE6771", "E8959C"],   # sombrero rojo (Flor roja 1-4)
    "pie_seta": ["5C3E26", "C9B07E", "E2CEA0", "FFF3C4"],   # cuerpo de seta (Pergamino)
    "escarabajo": ["1C3535", "346161", "4C8D8D", "6DB0B0"], # caparazón (Agua)
    "delantal": ["3D3214", "705425", "A37036", "C68756"],   # cuero (Follaje cobre)
    "rana":     ["152814", "355029", "3E9A35", "6FCF4F"],   # Follaje y Brote
    "panuelo":  ["5C3E26", "C9B07E", "E2CEA0", "FFF8E8"],   # Pergamino
    "pajaro":   ["705425", "B27219", "DF9022", "E6A852"],   # Flor ámbar
    "pecho":    ["A37036", "E6A852", "EDC082", "FFF3C4"],
    "mochila":  ["251812", "492E23", "6D4534", "905C45"],
    "metal":    ["292C25", "525649", "7A806D", "A0A596"],   # Piedra
    "ojo":      ["140E18", "140E18", "140E18", "140E18"],
    "brillo":   ["FFF8E8", "FFF8E8", "FFF8E8", "FFF8E8"],
    "rubor":    ["DE6771", "DE6771", "DE6771", "DE6771"],
    "punto":    ["FFF3C4", "FFF3C4", "FFF3C4", "FFF3C4"],
    "pelo":     ["2B1E17", "533B2D", "7C5843", "A57559"],   # Tierra (castor)
    "cola":     ["251812", "492E23", "6D4534", "6D4534"],   # Madera oscura
    "hocico":   ["5C3E26", "C9B07E", "E2CEA0", "FFF8E8"],   # Pergamino
    "nariz":    ["140E18", "140E18", "140E18", "140E18"],
    "escama":   ["3D3214", "705425", "A37036", "C68756"],   # escamas del pangolín (Follaje cobre)
    "piel_p":   ["5C3E26", "A57559", "C9B07E", "E2CEA0"],   # cara y barriga del pangolín
    "bufanda":  ["1C3535", "346161", "4C8D8D", "6DB0B0"],   # bufanda (Agua)
    "garza":    ["292C25", "525649", "7A806D", "A0A596"],   # plumas grises (Piedra)
    "pecho_g":  ["7A806D", "C9B07E", "E2CEA0", "FFF8E8"],   # pechuga clara
    "pico":     ["705425", "B27219", "DF9022", "E6A852"],   # pico y patas (Flor ámbar)
    "paja":     ["5C3E26", "A37036", "C68756", "E2CEA0"],   # sombrero de paja
    "topo":     ["16131A", "2A2430", "41384A", "5C5066"],   # pelo de topo (negro aterciopelado, violáceo)
    "rosa":     ["7A3348", "B85A70", "DE8A98", "F4BCC4"],   # hocico y manos del topo
    "cobre":    ["6A3418", "9A4E24", "C06A32", "F4B470"],   # el casco de minero
    "liebre":   ["5C3E26", "8E6A44", "B8936A", "D9BC94"],   # pelo de liebre (pardo dorado)
    "maiz":     ["8A4418", "C0702A", "F2C45A", "FDE27E"],   # mazorcas
}
ANCHO, ALTO = 24, 32


class Lienzo:
    def __init__(self):
        self.m = [[None] * ANCHO for _ in range(ALTO)]   # (material, tono) o None

    def ovalo(self, cx, cy, rx, ry, material, plano=False, recorte=None):
        """Óvalo sombreado. plano=True: un solo tono (base)."""
        for y in range(ALTO):
            for x in range(ANCHO):
                nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                if nx * nx + ny * ny <= 1.0:
                    if recorte and not recorte(x, y):
                        continue
                    if plano:
                        t = 2
                    else:
                        luz = -nx * 0.55 - ny * 0.8
                        t = 3 if luz > 0.55 else (2 if luz > -0.1 else 1)
                    self.m[y][x] = (material, t)

    def rect(self, x0, y0, x1, y1, material, tono=2):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= x < ANCHO and 0 <= y < ALTO:
                    self.m[y][x] = (material, tono)

    def px(self, x, y, material, tono=2):
        if 0 <= x < ANCHO and 0 <= y < ALTO:
            self.m[y][x] = (material, tono)

    def imagen(self):
        img = Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))
        hexa = lambda c: tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
        # contorno selectivo: píxel vacío junto a un material → tono más oscuro de ese material
        contorno = {}
        for y in range(ALTO):
            for x in range(ANCHO):
                if self.m[y][x] is None:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < ANCHO and 0 <= ny < ALTO and self.m[ny][nx] is not None:
                            mat = self.m[ny][nx][0]
                            if mat not in ("brillo", "punto"):
                                contorno[(x, y)] = mat
                                break
        for y in range(ALTO):
            for x in range(ANCHO):
                if self.m[y][x] is not None:
                    mat, t = self.m[y][x]
                    img.putpixel((x, y), hexa(MATERIALES[mat][t]))
                elif (x, y) in contorno:
                    img.putpixel((x, y), hexa(MATERIALES[contorno[(x, y)]][0]))
        # contorno interior entre materiales distintos (solo abajo y a la derecha: da volumen)
        return img


def ojos(l, y, x1, x2, alto=3):
    """Dos ojos de 2 píxeles de ancho (x1 y x2 son su columna izquierda), con brillo arriba a la izquierda."""
    for x in (x1, x2):
        for k in range(alto):
            l.px(x, y + k, "ojo")
            l.px(x + 1, y + k, "ojo")
        l.px(x, y, "brillo")


def bibi():
    """BIBI MUSGO: anciana tortuga, guardiana del Gran Árbol. Concha cubierta de musgo y bastón."""
    l = Lienzo()
    l.ovalo(12, 21, 9.5, 8, "concha")                       # concha (detrás)
    l.ovalo(12, 16.5, 8, 4, "musgo", recorte=lambda x, y: y <= 17)   # musgo sobre la concha
    for (x, y) in [(5, 16), (8, 13), (16, 13), (19, 16)]:
        l.px(x, y, "musgo", 3)
    l.ovalo(12, 22.5, 5.5, 5.5, "tortuga")                  # barriga (delante)
    l.ovalo(12, 14, 5.5, 5, "tortuga")                      # cabeza, delante de la concha
    l.ovalo(12, 15, 4, 3.2, "tortuga", plano=True)          # cara más clara
    for y in range(14, 17):
        for x in range(9, 16):
            if l.m[y][x] and l.m[y][x][0] == "tortuga":
                l.m[y][x] = ("tortuga", 3)
    ojos(l, 13, 9, 13, alto=2)
    for x in (8, 9, 10): l.px(x, 11, "cana", 3)             # cejas blancas
    for x in (13, 14, 15): l.px(x, 11, "cana", 3)
    l.px(11, 17, "tortuga", 1); l.px(12, 17, "tortuga", 1)   # boca
    l.rect(7, 28, 9, 30, "tortuga", 1); l.rect(14, 28, 16, 30, "tortuga", 1)   # patas
    for y in range(12, 31):                                  # bastón
        l.px(21, y, "concha", 2 if y % 3 else 3)
    l.px(20, 12, "musgo", 3); l.px(22, 11, "musgo", 3)
    l.ovalo(20.5, 21, 1.7, 1.7, "tortuga")                  # mano en el bastón
    return l.imagen()


def pino():
    """PINO: niño-seta, curioso y travieso. Sombrero rojo con motas."""
    l = Lienzo()
    l.ovalo(12, 24, 5, 6, "pie_seta")                        # cuerpo
    l.rect(9, 29, 10, 30, "pie_seta", 1); l.rect(13, 29, 14, 30, "pie_seta", 1)
    l.ovalo(12, 17, 5.5, 4.5, "pie_seta")                    # cara
    l.ovalo(12, 12, 10, 5.5, "seta", recorte=lambda x, y: y <= 14)   # sombrero
    for (x, y) in [(7, 10), (11, 9), (15, 11), (18, 12), (9, 13)]:
        l.px(x, y, "punto"); l.px(x + 1, y, "punto")
    ojos(l, 16, 9, 13, alto=3)
    l.px(9, 19, "rubor"); l.px(15, 19, "rubor")
    l.ovalo(6.5, 24, 1.6, 2.2, "pie_seta"); l.ovalo(17.5, 24, 1.6, 2.2, "pie_seta")   # brazos
    return l.imagen()


def corteza():
    """CORTEZA: escarabaja herrera. Caparazón brillante, delantal de cuero y martillo."""
    l = Lienzo()
    l.ovalo(12, 22, 7.5, 8, "escarabajo")                    # cuerpo
    l.rect(8, 21, 15, 28, "delantal", 2)                     # delantal
    for y in range(21, 29): l.px(15, y, "delantal", 1)
    l.rect(8, 21, 15, 21, "delantal", 3)
    l.ovalo(12, 12, 6, 5, "escarabajo")                      # cabeza
    for (x, y) in [(9, 7), (8, 6), (15, 7), (16, 6)]:        # antenas
        l.px(x, y, "escarabajo", 1)
    ojos(l, 10, 9, 13)
    l.rect(9, 29, 10, 30, "escarabajo", 1); l.rect(14, 29, 15, 30, "escarabajo", 1)
    l.ovalo(4.5, 22, 1.8, 2.5, "escarabajo")                 # brazo
    l.ovalo(19.5, 21, 1.8, 2.5, "escarabajo")
    for y in range(14, 23): l.px(20, y, "concha", 2)          # mango del martillo
    l.rect(18, 12, 22, 14, "metal", 2); l.rect(18, 12, 22, 12, "metal", 3)
    return l.imagen()


def juncia():
    """JUNCIA: rana cocinera de la Ciénaga. Pañuelo en la cabeza y cuchara de madera."""
    l = Lienzo()
    l.ovalo(12, 23, 8, 7, "rana")                            # cuerpo
    l.ovalo(12, 24.5, 5, 4.5, "pecho", plano=True)           # barriga
    l.ovalo(12, 15, 7.5, 5, "rana")                          # cabeza ancha
    l.ovalo(8, 11, 2.6, 2.6, "rana"); l.ovalo(16, 11, 2.6, 2.6, "rana")   # ojos saltones
    ojos(l, 10, 7, 15, alto=2)
    l.rect(9, 17, 15, 17, "rana", 1)                         # boca
    l.rect(6, 8, 18, 9, "panuelo", 2)                        # pañuelo
    l.rect(6, 8, 18, 8, "panuelo", 3)
    l.px(19, 9, "panuelo", 2); l.px(20, 10, "panuelo", 2)
    l.rect(7, 29, 10, 30, "rana", 1); l.rect(14, 29, 17, 30, "rana", 1)
    l.ovalo(4.5, 23, 1.8, 2.4, "rana")
    for y in range(16, 26): l.px(20, y, "concha", 3)          # cuchara
    l.ovalo(20, 15, 1.6, 2, "concha")
    l.ovalo(19.5, 23, 1.8, 2.4, "rana")
    return l.imagen()


def tawi():
    """TAWI: pájaro mercader, siempre de viaje. Mochila enorme llena de cosas."""
    l = Lienzo()
    l.ovalo(16, 12, 6, 7, "mochila")                         # mochila a la espalda (asoma por un lado)
    l.rect(14, 4, 16, 6, "seta", 2); l.rect(18, 5, 20, 6, "musgo", 3)    # cosas que sobresalen
    l.px(21, 9, "metal", 3); l.px(21, 10, "metal", 2)
    l.ovalo(11, 23, 7, 6.5, "pajaro")                        # cuerpo
    l.ovalo(11, 24, 4, 4, "pecho", plano=True)
    l.ovalo(10, 13.5, 6, 5.5, "pajaro")                      # cabeza redonda
    l.ovalo(9.5, 15, 3.5, 2.5, "pecho", plano=True)          # cara clara
    ojos(l, 12, 7, 11, alto=2)
    l.px(9, 15, "delantal", 3); l.px(10, 15, "delantal", 3); l.px(9, 16, "delantal", 1)   # pico
    for (x, y) in [(8, 8), (9, 7), (10, 8)]: l.px(x, y, "pajaro", 3)    # copete
    l.ovalo(4, 23, 1.8, 3.2, "pajaro")                       # ala
    l.rect(15, 17, 15, 22, "delantal", 1)                    # correa
    for x in (8, 9, 12, 13): l.px(x, 29, "delantal", 2); l.px(x, 30, "delantal", 1)   # patas
    return l.imagen()


def shamba():
    """MZEE SHAMBA: castor anciano, agricultor. Sombrero de paja, cejas y barba blancas,
    gafas redondas, dientes de castor, bastón de madera y la cola plana asomando por detrás."""
    l = Lienzo()
    # cola plana detrás (sale a la derecha), con su trama de escamas
    l.ovalo(19.5, 26, 4.5, 3.4, "cola")
    for (x, y) in [(18, 25), (20, 24), (21, 26), (19, 27), (22, 25), (20, 28)]:
        l.px(x, y, "cola", 1)
    l.ovalo(12, 23, 7, 7, "pelo")                               # cuerpo
    l.ovalo(12, 24.5, 4.2, 4.5, "hocico", plano=2)              # barriga clara
    l.ovalo(7, 9.5, 2, 2, "pelo"); l.ovalo(17, 9.5, 2, 2, "pelo")   # orejas redondas
    l.px(7, 9, "pelo", 1); l.px(17, 9, "pelo", 1)
    l.ovalo(12, 13.5, 6.5, 5.5, "pelo")                         # cabeza
    l.ovalo(12, 16.5, 3.8, 2.6, "hocico")                       # hocico claro
    l.rect(11, 14, 12, 15, "nariz")                             # nariz
    l.px(11, 14, "metal", 3)
    l.rect(11, 18, 12, 20, "punto")                             # dientes de castor
    l.px(11, 20, "hocico", 1); l.px(12, 20, "hocico", 2)
    for (x, y) in [(8, 18), (9, 19), (14, 19), (15, 18), (10, 19), (13, 19)]:   # barba blanca
        l.px(x, y, "cana", 3)
    # ojos con gafas redondas (aro fino) y cejas blancas pobladas
    for cx in (9, 14):
        for (dx, dy) in [(-1, -2), (0, -2), (1, -2), (-2, -1), (2, -1), (-2, 0), (2, 0), (-1, 1), (0, 1), (1, 1)]:
            l.px(cx + dx, 12 + dy, "metal", 2)
        l.px(cx - 1, 11, "ojo"); l.px(cx, 11, "ojo"); l.px(cx - 1, 12, "ojo"); l.px(cx, 12, "ojo")
        l.px(cx - 1, 11, "brillo")
    l.px(11, 11, "metal", 2); l.px(12, 11, "metal", 2)          # puente de las gafas
    for (x, y) in [(6, 9), (7, 9), (8, 9), (15, 9), (16, 9), (17, 9)]:
        l.px(x, y, "cana", 3)
    # sombrero de paja: copa y ala ancha
    l.rect(8, 3, 15, 6, "pajaro", 2)
    l.rect(8, 3, 15, 3, "pajaro", 3)
    l.rect(8, 6, 15, 6, "seta", 1)                              # cinta roja
    l.rect(4, 7, 19, 8, "pajaro", 2)
    l.rect(4, 7, 19, 7, "pajaro", 3)
    for x in range(5, 19, 3):
        l.px(x, 8, "pajaro", 1)
    # patas
    l.rect(8, 29, 10, 30, "pelo", 1); l.rect(13, 29, 15, 30, "pelo", 1)
    # bastón tallado con una hoja atada
    for y in range(13, 31):
        l.px(3, y, "concha", 3 if y % 4 else 2)
    l.ovalo(3, 12, 1.6, 1.6, "concha")
    l.px(4, 11, "musgo", 3); l.px(5, 10, "musgo", 3)
    l.ovalo(4.5, 21, 1.8, 2.2, "pelo")                          # mano en el bastón
    l.ovalo(18.5, 21.5, 1.8, 2.4, "pelo")                       # otra mano
    return l.imagen()


# (Mzee Shamba, más grande, lo dibuja herramientas/dibujar_kitovu.py)
def msafiri():
    """MSAFIRI: pangolín viajero y cronista. Cubierto de escamas cobrizas (placas en filas), hocico largo y fino,
    bufanda, una mochila enorme con un mapa enrollado atravesado encima y un farolillo, y un bastón de caminante."""
    l = Lienzo()
    l.ovalo(12.5, 12.5, 7.5, 6, "mochila")                   # mochila enorme detrás
    for x in range(4, 21):                                    # el mapa enrollado, atravesado encima
        l.px(x, 6, "panuelo", 3); l.px(x, 7, "panuelo", 2); l.px(x, 8, "panuelo", 1)
    l.px(4, 7, "pajaro", 2); l.px(20, 7, "pajaro", 2)
    l.rect(18, 10, 20, 12, "metal", 2); l.px(19, 11, "pecho", 3)         # farolillo
    l.ovalo(12, 23, 6.6, 7.2, "escama")                       # cuerpo
    def placas(y0, y1, x0, x1, cabeza=False):
        # placas en filas: cada placa es un arco claro arriba con sombra debajo; filas alternas desplazadas
        for k, y in enumerate(range(y0, y1, 2)):
            for x in range(x0 + (k % 2), x1, 3):
                for dx in (0, 1):
                    if l.m[y][x + dx] and l.m[y][x + dx][0] == "escama":
                        l.px(x + dx, y, "escama", 3)
                if l.m[y + 1][x + 2] and l.m[y + 1][x + 2][0] == "escama":
                    l.px(x + 2, y + 1, "escama", 1)
    placas(17, 30, 5, 20)
    l.ovalo(12, 25.5, 2.4, 3.6, "piel_p", plano=True)         # barriga clara (estrecha)
    l.ovalo(12, 13, 4.6, 3.6, "escama")                       # cabeza: la coronilla de escamas
    placas(10, 14, 8, 17)
    l.ovalo(12, 16, 3.4, 2.4, "piel_p")                       # cara
    for y in range(17, 21):                                   # hocico largo y fino hacia abajo
        l.px(12, y, "piel_p", 2); l.px(11, y, "piel_p", 3 if y < 19 else 2)
    l.px(11, 21, "nariz"); l.px(12, 21, "nariz")
    l.px(10, 15, "ojo"); l.px(14, 15, "ojo"); l.px(10, 14, "brillo"); l.px(14, 14, "brillo")
    l.px(9, 17, "rubor"); l.px(15, 17, "rubor")
    l.rect(7, 20, 9, 21, "bufanda", 2); l.rect(14, 20, 17, 21, "bufanda", 2)   # bufanda (el hocico por delante)
    l.rect(15, 22, 16, 25, "bufanda", 2); l.px(16, 25, "bufanda", 1); l.px(15, 22, "bufanda", 3)
    l.ovalo(5, 24, 1.5, 2.6, "escama")                        # brazos
    l.ovalo(19, 22.5, 1.5, 2.4, "escama")
    for y in range(12, 31): l.px(21, y, "concha", 2 if y % 3 else 3)   # bastón
    l.px(20, 12, "musgo", 3); l.px(22, 11, "musgo", 3)
    l.ovalo(20.5, 22, 1.5, 1.5, "piel_p")
    l.rect(8, 29, 10, 30, "escama", 1); l.rect(14, 29, 16, 30, "escama", 1)   # patas
    for (x, y) in ((3, 28), (2, 27), (2, 26), (3, 25)):        # cola de escamas que se enrosca
        l.px(x, y, "escama", 2)
    l.px(2, 26, "escama", 3)
    return l.imagen()


def korongo():
    """KORONGO: garza pescadora de Las Pasarelas. Alta y flaca, plumas grises, pechuga clara, pico largo y amarillo,
    patas finas, un sombrero de paja ancho y su caña de pescar con el sedal y un corcho rojo."""
    l = Lienzo()
    for y in range(24, 31):                                   # patas largas y finas
        l.px(10, y, "pico", 1); l.px(14, y, "pico", 1)
    l.rect(8, 30, 10, 30, "pico", 1); l.rect(14, 30, 16, 30, "pico", 1)
    l.ovalo(12, 19, 5.5, 6, "garza")                          # cuerpo
    l.ovalo(12.5, 20, 3, 4.2, "pecho_g", plano=True)          # pechuga
    for (x, y) in ((7, 17), (7, 19), (7, 21), (16, 18), (17, 20)):   # plumas del ala
        l.px(x, y, "garza", 3)
    l.ovalo(5.5, 21, 1.6, 3.4, "garza")                       # ala recogida
    for y in range(9, 15):                                    # cuello largo, curvado
        l.px(12 + (1 if 10 <= y <= 12 else 0), y, "pecho_g", 2)
        l.px(13 + (1 if 10 <= y <= 12 else 0), y, "garza", 2)
    l.ovalo(13, 8, 2.8, 2.4, "garza")                         # cabeza
    l.px(12, 8, "ojo"); l.px(11, 7, "brillo")
    for x in range(15, 21):                                   # pico largo
        l.px(x, 8, "pico", 3 if x < 19 else 2); l.px(x, 9, "pico", 1 if x > 17 else 2)
    l.rect(6, 4, 19, 5, "paja", 2); l.rect(6, 4, 19, 4, "paja", 3)   # sombrero de paja, ancho
    l.rect(9, 2, 16, 3, "paja", 2); l.rect(9, 2, 16, 2, "paja", 3)
    l.rect(9, 3, 16, 3, "seta", 1)                            # cinta roja
    for y in range(6, 27): l.px(20, y, "concha", 2 if y % 3 else 3)   # la caña, apoyada
    l.px(21, 5, "concha", 3); l.px(22, 4, "concha", 3)
    for y in range(5, 14): l.px(23, y, "cana", 3)                    # el sedal
    l.px(23, 14, "seta", 2); l.px(23, 15, "punto")                   # el corcho
    l.ovalo(18.5, 19, 1.4, 1.6, "garza")                      # la punta del ala sujetando la caña
    return l.imagen()


def fuko():
    """FUKO: topo minero del Camino Cobrizo. Pelo negro aterciopelado, hocico rosa en forma de estrella, manos
    rosadas enormes de cavar, gafas redondas de cristal muy gordo (casi no ve), casco de cobre con una vela
    encendida, y un cinturón con una campanilla y una bolsa."""
    l = Lienzo()
    l.ovalo(12, 22, 7.2, 8, "topo")                           # cuerpo, rechoncho
    l.ovalo(12, 24.5, 3.6, 4.4, "topo", plano=True)          # barriga algo más clara
    for y in range(22, 27):
        for x in range(9, 16):
            if l.m[y][x] and l.m[y][x][0] == "topo" and (x + y) % 3 == 0:
                l.px(x, y, "topo", 3)
    l.rect(5, 23, 19, 24, "delantal", 1)                     # cinturón de cuero
    l.px(12, 23, "metal", 3); l.px(12, 24, "metal", 2)       # hebilla
    l.rect(15, 25, 17, 27, "delantal", 2); l.px(15, 25, "delantal", 3)   # bolsa
    l.px(8, 25, "cobre", 3); l.px(8, 26, "cobre", 2); l.px(7, 26, "cobre", 1); l.px(9, 26, "cobre", 1)   # campanilla
    l.ovalo(12, 13.5, 6, 5, "topo")                           # cabeza
    for x in range(10, 15):                                   # hocico en estrella, rosa
        l.px(x, 17, "rosa", 2)
    l.px(11, 18, "rosa", 2); l.px(12, 18, "rosa", 3); l.px(13, 18, "rosa", 2)
    l.px(10, 16, "rosa", 1); l.px(14, 16, "rosa", 1); l.px(12, 16, "rosa", 3)
    l.px(12, 19, "nariz")
    for (x0) in (8, 13):                                      # gafas redondas de cristal gordo
        l.rect(x0, 13, x0 + 2, 15, "pecho_g", 3)
        l.px(x0, 13, "metal", 2); l.px(x0 + 2, 13, "metal", 2); l.px(x0, 15, "metal", 2); l.px(x0 + 2, 15, "metal", 2)
        l.px(x0 + 1, 14, "ojo"); l.px(x0, 14, "brillo")
    l.px(11, 14, "metal", 2); l.px(12, 14, "metal", 2)       # el puente de las gafas
    l.rect(6, 8, 18, 10, "cobre", 2); l.rect(6, 8, 18, 8, "cobre", 3)   # casco de minero, de cobre
    l.rect(8, 6, 16, 7, "cobre", 2); l.rect(9, 5, 15, 5, "cobre", 3)
    l.rect(5, 10, 19, 10, "cobre", 1)                        # el ala del casco
    l.rect(11, 3, 13, 5, "pie_seta", 3)                      # la vela en el casco
    l.px(12, 2, "pecho", 3); l.px(12, 1, "punto"); l.px(11, 2, "pajaro", 3)
    l.ovalo(4.5, 21, 2.4, 2.6, "rosa")                        # manos enormes de cavar
    l.ovalo(19.5, 21, 2.4, 2.6, "rosa")
    for x in (3, 5):
        l.px(x, 23, "rosa", 3)
    for x in (19, 21):
        l.px(x, 23, "rosa", 3)
    l.rect(8, 29, 10, 30, "rosa", 1); l.rect(14, 29, 16, 30, "rosa", 1)   # pies
    return l.imagen()


def sungura():
    """SUNGURA: liebre guardasemillas de la Senda de los Surcos. Orejas larguísimas (una doblada), pelo pardo
    dorado con la barriga clara, delantal de saco con bolsillos llenos de semillas, un pañuelo verde al cuello
    y una mazorca bajo el brazo."""
    l = Lienzo()
    for (x0, inclina) in ((9, 0), (14, 1)):                   # las orejas (la derecha, doblada en la punta)
        for y in range(1, 10):
            dx = 0 if not inclina or y > 3 else (3 - y)
            l.px(x0 + dx, y, "liebre", 2); l.px(x0 + dx + 1, y, "liebre", 2 if y % 3 else 3)
            if 2 < y < 9:
                l.px(x0 + dx + (1 if x0 < 12 else 0), y, "rubor", 0)
        l.px(x0 + (3 if inclina else 0), 1, "liebre", 3)
    l.ovalo(12, 23, 6.6, 7.4, "liebre")                       # cuerpo
    l.ovalo(12, 24.5, 3.4, 4.6, "hocico", plano=True)         # barriga clara
    l.rect(7, 21, 17, 28, "delantal", 1)                     # delantal de saco
    l.rect(8, 21, 16, 27, "pie_seta", 1)
    for x in (9, 14):                                         # bolsillos con semillas asomando
        l.rect(x, 24, x + 1, 26, "pie_seta", 0)
        l.px(x, 23, "maiz", 3); l.px(x + 1, 23, "musgo", 3)
    l.ovalo(12, 14, 5.4, 4.8, "liebre")                       # cabeza
    l.ovalo(12, 16.2, 2.6, 1.8, "hocico", plano=True)         # morro claro
    l.px(12, 15, "rubor"); l.px(11, 15, "rubor")              # naricilla rosa
    l.px(11, 17, "nariz"); l.px(12, 17, "nariz")              # boquita
    ojos(l, 12, 8, 14, alto=2)
    l.px(7, 15, "rubor"); l.px(17, 15, "rubor")
    l.rect(8, 18, 16, 19, "musgo", 2); l.px(15, 20, "musgo", 2); l.px(16, 20, "musgo", 1)   # pañuelo verde
    l.ovalo(5, 23, 1.6, 2.6, "liebre")                        # brazos
    l.ovalo(19, 22.5, 1.6, 2.4, "liebre")
    for y in range(18, 27):                                   # la mazorca bajo el brazo
        l.px(20, y, "maiz", 3 if y % 2 else 2); l.px(21, y, "maiz", 2 if y % 2 else 1)
    l.px(20, 17, "musgo", 3); l.px(21, 16, "musgo", 2); l.px(19, 17, "musgo", 2)
    l.ovalo(9, 30, 2.4, 1.2, "liebre"); l.ovalo(15, 30, 2.4, 1.2, "liebre")   # patas largas
    l.px(18, 28, "hocico", 3); l.px(19, 29, "hocico", 3)      # el rabito blanco
    return l.imagen()


ALDEANOS = {"sungura": sungura, "fuko": fuko, "korongo": korongo, "msafiri": msafiri, "bibi": bibi, "pino": pino, "corteza": corteza, "juncia": juncia, "tawi": tawi}

if __name__ == "__main__":
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    destino = os.path.join(raiz, "arte", "personajes", "aldeanos")
    os.makedirs(destino, exist_ok=True)
    for nombre, fn in ALDEANOS.items():
        fn().save(os.path.join(destino, f"{nombre}_frente.png"))
    print("Aldeanos dibujados en", destino)
