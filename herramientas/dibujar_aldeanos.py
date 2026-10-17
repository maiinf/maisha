"""
ALDEANOS DE RAÍZ dibujados píxel a píxel (paleta oficial de Raíz).

Cada aldeano se monta con formas sencillas (óvalos sombreados con luz arriba a la izquierda)
y un contorno selectivo: cada material se contornea con su tono más oscuro.

Uso:  python3 herramientas/dibujar_aldeanos.py
Genera arte/personajes/aldeanos/<nombre>_frente.png (24x32, los pies abajo en el centro) y <nombre>_anim.png
(4 fotogramas: quieto, respira, parpadea y su gesto; los usa scripts/mundo/aldea/aldeano.gd)
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
    "cabra":    ["525649", "A0A596", "D6D4C8", "FFF8E8"],   # pelo blanco de cabra (Piedra y Pergamino)
    "gris_c":   ["292C25", "525649", "7A806D", "A0A596"],   # manchas grises de la cabra
    "cuerno":   ["5C3E26", "A57559", "C9B07E", "E2CEA0"],   # cuernos curvos, color hueso
    "rojo":     ["5A1418", "8C2028", "B02531", "D53946"],   # pañuelo rojo
    "lente":    ["1E3A2A", "3A8A5A", "8AE0B0", "C8FFE0"],   # cristal verdoso (gafas de forja)
    "laton":    ["3A2A10", "9A7430", "E8C46A", "FBE6A2"],   # latón
    "hollin":   ["1A1A1A", "1A1A1A", "1A1A1A", "1A1A1A"],
    "ceja":     ["0A1418", "0A1418", "0A1418", "0A1418"],
    "brasa":    ["A8380F", "EF8A26", "F9B947", "FDE27E"],
    "vapor":    ["C8C4C0", "D8D4D0", "E8E4E0", "F8F4F0"],
    "flor":     ["8F2532", "D5525E", "F4B39A", "FFE0D8"],
    "azul":     ["1E3A5A", "2E5A8A", "4A82B8", "8AB8E0"],
    # SIGILIA
    "armino":   ["4E4870", "A8A0C4", "E2DEEE", "FFFFFF"],   # pelo blanco de armiño (sombra lila)
    "tinta":    ["0A0814", "16122A", "241E3C", "342C50"],   # la punta negra de la cola
    "morado":   ["2E1A44", "5A3480", "7A52A6", "A07AC4"],   # bufanda morada de escriba
    "en_blanco": ["8A869A", "B4B0C2", "CDCAD8", "E0DEE8"],  # lo que la Tinta Quieta deja sin color
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
    # detalle: el dibujo de la concha, una florecita en el musgo y arrugas de abuela
    for (x, y) in [(5, 20), (6, 23), (18, 20), (19, 23), (6, 26), (18, 26)]:
        l.px(x, y, "concha", 1)
    l.px(15, 12, "flor", 2); l.px(16, 12, "flor", 3); l.px(15, 11, "flor", 1); l.px(16, 11, "punto")
    l.px(9, 15, "tortuga", 1); l.px(14, 15, "tortuga", 1)
    return l


def pino():
    """PINO: niño-seta, curioso y travieso. Sombrero rojo con motas, láminas bajo la copa, pañuelo y bandolera de explorador."""
    l = Lienzo()
    l.ovalo(12, 24, 5, 6, "pie_seta")                        # cuerpo
    l.rect(9, 29, 10, 30, "pie_seta", 1); l.rect(13, 29, 14, 30, "pie_seta", 1)
    l.ovalo(12, 17, 5.5, 4.5, "pie_seta")                    # cara
    l.ovalo(12, 12, 10, 5.5, "seta", recorte=lambda x, y: y <= 14)   # sombrero
    for x in range(4, 21):                                   # láminas bajo el sombrero
        if l.m[14][x]:
            l.px(x, 14, "pie_seta", 1 if x % 2 == 0 else 2)
    for (x, y) in [(6, 11), (7, 10), (11, 9), (12, 8), (15, 11), (18, 12), (9, 12)]:
        l.px(x, y, "punto"); l.px(x + 1, y, "punto")
    ojos(l, 16, 9, 13, alto=3)
    l.px(9, 19, "rubor"); l.px(15, 19, "rubor")
    l.px(12, 19, "pie_seta", 1)                              # sonrisilla traviesa
    # pañuelo verde de explorador al cuello y bandolera cruzada con bolsito
    l.rect(9, 20, 15, 20, "musgo", 2); l.px(11, 21, "musgo", 3); l.px(12, 21, "musgo", 2)
    for k in range(5):
        l.px(9 + k, 21 + k, "delantal", 2)
    l.px(11, 23, "laton", 3)                                 # hebilla
    l.rect(14, 25, 16, 27, "delantal", 1); l.px(15, 25, "delantal", 2)   # bolsito de semillas
    l.ovalo(6.5, 24, 1.6, 2.2, "pie_seta"); l.ovalo(17.5, 24, 1.6, 2.2, "pie_seta")   # brazos
    # detalle: pecas y una hoja en la mano
    l.px(10, 18, "pie_seta", 1); l.px(14, 18, "pie_seta", 1)
    l.px(5, 25, "musgo", 3); l.px(5, 26, "musgo", 2); l.px(4, 25, "musgo", 2); l.px(4, 26, "musgo", 1)
    return l


def corteza():
    """CORTEZA: escarabaja herrera, gruñona y orgullosa. Caparazón brillante, gafas de forja en la frente, cejas
    fruncidas, hollín en las mejillas, delantal de cuero con bolsillo (asoman unas tenazas) y cinto, y el martillo."""
    l = Lienzo()
    l.ovalo(12, 22, 7.5, 8, "escarabajo")                    # cuerpo
    l.px(7, 17, "escarabajo", 3); l.px(8, 16, "escarabajo", 3)   # brillo del caparazón
    l.rect(8, 20, 15, 28, "delantal", 2)                     # delantal
    for y in range(20, 29): l.px(15, y, "delantal", 1)
    l.rect(8, 20, 15, 20, "delantal", 3)
    l.rect(9, 24, 12, 26, "delantal", 1)                     # bolsillo
    l.px(10, 23, "metal", 3); l.px(11, 23, "metal", 2)       # tenazas asomando
    l.px(13, 26, "hollin"); l.px(14, 22, "hollin")           # quemaduras
    l.rect(8, 27, 15, 27, "concha", 1)                       # cinto
    l.px(12, 27, "laton", 2)
    l.ovalo(12, 12, 6, 5, "escarabajo")                      # cabeza
    for (x, y) in [(9, 7), (8, 6), (15, 7), (16, 6)]:        # antenas
        l.px(x, y, "escarabajo", 1)
    l.px(7, 5, "escarabajo", 3); l.px(17, 5, "escarabajo", 3)
    for x in (9, 13):                                        # las gafas de forja en la frente
        l.rect(x, 8, x + 2, 9, "laton", 2)
        l.px(x + 1, 8, "lente", 3); l.px(x + 1, 9, "lente", 2)
    l.px(12, 8, "laton", 1)
    ojos(l, 11, 9, 13, alto=2)
    l.px(8, 10, "ceja"); l.px(9, 10, "ceja"); l.px(10, 11, "ceja")   # cejas fruncidas
    l.px(15, 10, "ceja"); l.px(14, 10, "ceja"); l.px(13, 11, "ceja")
    l.px(11, 14, "ceja"); l.px(12, 14, "ceja")               # boca seria
    l.px(8, 13, "hollin"); l.px(16, 12, "hollin")            # hollín en las mejillas
    l.rect(9, 29, 10, 30, "escarabajo", 1); l.rect(14, 29, 15, 30, "escarabajo", 1)
    l.ovalo(4.5, 22, 1.8, 2.5, "escarabajo")                 # brazo
    l.ovalo(19.5, 21, 1.8, 2.5, "escarabajo")
    for y in range(14, 23): l.px(20, y, "concha", 2)          # mango del martillo
    l.rect(18, 12, 22, 14, "metal", 2); l.rect(18, 12, 22, 12, "metal", 3)
    return l


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
    # detalle: el delantal blanco con manchas de sopa, rubor, lunares del pañuelo y una gota en la cuchara
    l.rect(9, 21, 15, 27, "panuelo", 2); l.rect(9, 21, 15, 21, "panuelo", 3)
    l.px(10, 24, "musgo", 2); l.px(13, 26, "pajaro", 2)
    l.px(8, 16, "rubor"); l.px(16, 16, "rubor")
    for x in (8, 11, 14, 17): l.px(x, 9, "seta", 2)
    l.px(20, 13, "musgo", 3)
    return l


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
    # detalle: plumas de colores en la mochila, la bolsa de monedas y una gorrita de viaje
    l.px(13, 5, "azul", 3); l.px(13, 4, "azul", 2); l.px(17, 4, "flor", 2); l.px(17, 3, "flor", 3)
    l.ovalo(15.5, 26, 1.6, 1.8, "delantal"); l.px(15, 25, "laton", 3)
    l.px(9, 11, "rojo", 2); l.px(10, 11, "rojo", 3); l.px(11, 11, "rojo", 2)
    return l


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
    return l


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
    # detalle: una brújula colgada y la bufanda con rayas
    l.px(8, 22, "laton", 3); l.px(8, 23, "laton", 2)
    l.px(15, 23, "bufanda", 3); l.px(15, 24, "bufanda", 1)
    return l


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
    # detalle: un pececillo colgando del cinto
    l.px(9, 22, "metal", 3); l.px(9, 23, "metal", 2); l.px(9, 24, "azul", 3)
    return l


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
    # detalle: más destello en las gafas y hollín de mina en la cara
    l.px(14, 13, "brillo"); l.px(9, 13, "brillo")
    l.px(7, 15, "hollin"); l.px(17, 16, "hollin")
    return l


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
    # detalle: unas flores en el bolsillo
    l.px(14, 22, "flor", 3); l.px(15, 22, "flor", 2)
    return l


def mbuzi():
    """MBUZI: cabra montés pastora de la Cañada del Eco, mayor y tranquila. Pelo blanco con manchas grises, cuernos
    gruesos que se curvan hacia atrás y hacia fuera, barba larga, ojos entornados con cejas blancas, orejas caídas
    a los lados, pañuelo rojo al cuello y un cayado de pastora con la punta curva."""
    l = Lienzo()
    for y in range(5, 31):                                    # el cayado, apoyado a su derecha
        l.px(21, y, "concha", 2 if y % 4 else 3)
    for (x, y) in ((21, 4), (20, 3), (19, 3), (18, 4), (18, 5)):   # la punta curva
        l.px(x, y, "concha", 3 if y == 3 else 2)
    l.ovalo(11.5, 23.5, 6.2, 7.0, "cabra")                    # cuerpo
    for (x, y) in ((7, 21), (7, 22), (8, 22), (15, 25), (16, 26), (15, 26), (9, 28), (10, 28)):   # manchas grises
        l.px(x, y, "gris_c", 2)
    # los cuernos: gruesos en la base, suben y se curvan hacia atrás y hacia fuera (con anillos)
    for lado in (-1, 1):
        base = 9 if lado < 0 else 14
        tramo = ((0, 8), (0, 7), (0, 6), (lado, 5), (lado * 2, 4), (lado * 3, 4), (lado * 4, 5), (lado * 4, 6))
        for k, (dx, dy) in enumerate(tramo):
            l.px(base + dx, dy, "cuerno", 3 if k % 2 == 0 else 2)
            if k < 4:
                l.px(base + dx - lado, dy, "cuerno", 1 if k % 2 else 2)   # la base, de dos píxeles
    l.ovalo(11.5, 12.5, 4.4, 4.0, "cabra")                    # cabeza
    l.ovalo(11.5, 16, 2.5, 2.8, "cabra")                      # el hocico largo de cabra
    l.ovalo(11.5, 16.8, 1.8, 1.5, "pie_seta", plano=True)     # morro claro
    l.px(10, 16, "nariz"); l.px(13, 16, "nariz")              # los agujeros de la nariz
    l.px(11, 18, "gris_c", 1); l.px(12, 18, "gris_c", 1)      # la boca, tranquila
    for (x0, x1, y) in ((5, 7, 12), (16, 18, 12)):            # orejas caídas a los lados, con el dentro gris
        for x in range(x0, x1 + 1):
            l.px(x, y, "cabra", 2)
            l.px(x, y + 1, "gris_c", 2 if x != (x0 if x0 < 10 else x1) else 3)
    for x in (8, 13):                                         # ojos entornados, con ceja blanca encima
        l.px(x, 11, "cabra", 3); l.px(x + 1, 11, "cabra", 3)
        l.px(x, 12, "ojo"); l.px(x + 1, 12, "ojo")
        l.px(x, 13, "gris_c", 2); l.px(x + 1, 13, "gris_c", 2)
    l.rect(7, 19, 16, 20, "rojo", 2); l.rect(7, 19, 16, 19, "rojo", 3)   # el pañuelo rojo, anudado al lado
    l.px(15, 21, "rojo", 2); l.px(16, 21, "rojo", 1); l.px(16, 22, "rojo", 1)
    for y in range(19, 25):                                   # la barba larga, por encima del pañuelo
        for x in range(11, 13):
            l.px(x, y, "cabra", 3 if (x + y) % 2 else 2)
    l.px(11, 25, "cabra", 2)
    l.ovalo(5, 23, 1.6, 2.6, "cabra")                         # brazos (el derecho sujeta el cayado)
    l.ovalo(19.5, 20.5, 1.7, 2.0, "cabra")
    l.px(20, 21, "gris_c", 1)
    for x in (8, 15):                                         # pezuñas
        l.rect(x - 1, 29, x + 1, 30, "gris_c", 1); l.px(x, 30, "nariz")
    # detalle: un cencerro de latón colgado del pañuelo
    l.px(9, 21, "laton", 3); l.px(9, 22, "laton", 2); l.px(8, 22, "laton", 1); l.px(10, 22, "laton", 1)
    return l


def mdiria():
    """MDIRIA: martín pescador viejo del Lago Espejo. Cabeza grande, lomo turquesa, pecho naranja y garganta blanca,
    un pico larguísimo y oscuro, cejas blancas de viejo, una bufanda de lana amarilla y una red de pescar al hombro."""
    l = Lienzo()
    l.ovalo(12, 22, 6, 6.5, "escarabajo")                     # cuerpo
    l.ovalo(12.5, 23.5, 3.6, 4.6, "pajaro")                   # pecho naranja
    l.ovalo(6.5, 21.5, 2, 4.5, "escarabajo")                  # ala recogida
    for (x, y) in ((6, 19), (6, 21), (7, 23)):
        l.px(x, y, "escarabajo", 3)
    for x in range(4, 8):                                     # la cola, cortita
        l.px(x, 27, "escarabajo", 1)
    l.ovalo(11, 11, 5.5, 5, "escarabajo")                     # cabeza grande
    l.ovalo(10.5, 14.6, 2.6, 1.4, "pecho_g", plano=True)      # garganta blanca
    l.ovalo(8.5, 11.6, 1.6, 1.0, "pajaro", plano=True)        # la mejilla naranja
    l.px(12, 10, "ojo"); l.px(12, 11, "ojo"); l.px(11, 10, "brillo")
    for x in (10, 11, 12, 13):                                # cejas blancas, de viejo
        l.px(x, 8, "cana", 3 if x % 2 else 2)
    l.px(9, 7, "cana", 3)
    for x in range(16, 23):                                   # el pico, largo y oscuro
        l.px(x, 11, "metal", 1 if x > 19 else 2)
        if x < 21:
            l.px(x, 12, "metal", 0 if x > 18 else 1)
    l.rect(7, 16, 15, 17, "maiz", 2); l.rect(7, 16, 15, 16, "maiz", 3)   # bufanda de lana
    l.px(14, 18, "maiz", 2); l.px(14, 19, "maiz", 1)
    for y in range(17, 27):                                   # la red al hombro, con sus nudos
        for x in range(16, 21):
            if (x + y) % 2 == 0:
                l.px(x, y, "delantal", 2 if (x * y) % 3 else 3)
    l.px(17, 17, "seta", 2); l.px(19, 22, "seta", 2)          # flotadores rojos
    for x in (10, 14):                                        # patitas rojas
        l.px(x, 29, "seta", 2); l.px(x - 1, 30, "seta", 1); l.px(x + 1, 30, "seta", 1)
    return l


def bata():
    """BATA: el pato barquero del Embarcadero Junco. Viejo y orondo, de plumas blancas, con el pico ancho y las patas
    naranjas, una gorra de barquero azul con visera, un pañuelo rojo al cuello y la pértiga larga en el ala."""
    l = Lienzo()
    l.ovalo(12, 22, 7, 6.5, "cabra")                          # cuerpo orondo
    l.ovalo(11.5, 23.5, 4.2, 4.4, "pecho_g")                  # la pechuga
    l.ovalo(5.8, 21.5, 2.2, 4.4, "cabra")                     # ala recogida
    for (x, y) in ((5, 20), (5, 22), (6, 24)):
        l.px(x, y, "gris_c", 2)
    for x in range(17, 21):                                   # la cola, levantada
        l.px(x, 19 - (x - 17) // 2, "cabra", 2)
    l.ovalo(12, 11, 5, 4.8, "cabra")                          # cabeza
    ojos(l, 10, 10, 13, alto=2)
    for x in range(8, 16):                                    # el pico ancho y plano
        l.px(x, 14, "pico", 2 if 9 < x < 14 else 1)
        l.px(x, 15, "pico", 1)
    l.px(10, 14, "pico", 3); l.px(11, 14, "pico", 3)
    l.rect(7, 6, 17, 7, "bufanda", 1)                         # la gorra de barquero, con visera
    l.rect(8, 4, 16, 6, "bufanda", 2); l.rect(9, 4, 15, 4, "bufanda", 3)
    l.rect(6, 7, 11, 7, "bufanda", 0)
    l.px(12, 5, "maiz", 3)                                    # el ancla bordada
    l.rect(8, 16, 16, 17, "rojo", 3); l.rect(8, 17, 16, 17, "rojo", 2)   # el pañuelo
    l.px(15, 18, "rojo", 2); l.px(16, 19, "rojo", 1)
    for y in range(3, 31):                                    # la pértiga, larga
        l.px(20 + (1 if y < 12 else 0), y, "concha", 2 if y % 5 else 3)
    l.px(19, 21, "cabra", 3); l.px(19, 22, "cabra", 2)        # el ala que la sujeta
    for x in (9, 15):                                         # patas naranjas, palmeadas
        l.px(x, 29, "pico", 2); l.px(x - 1, 30, "pico", 1); l.px(x, 30, "pico", 2); l.px(x + 1, 30, "pico", 1)
    return l


def kasia():
    """KASIA: nutria barquera de la Orilla de Juncos. Risueña y charlatana: pelo pardo brillante, barriga y morro
    claros, orejitas redondas, bigotes, un sombrero de paja con una cinta azul y un remo al hombro."""
    l = Lienzo()
    for y in range(4, 29):                                    # el remo al hombro (la pala arriba)
        l.px(19, y, "concha", 2 if y % 4 else 3)
    l.ovalo(19.5, 4.5, 1.6, 3.2, "concha")
    l.px(19, 3, "concha", 3)
    l.ovalo(12, 22, 6.2, 7.5, "pelo")                         # cuerpo, alargado
    l.ovalo(12, 23.5, 3.4, 5, "hocico", plano=True)           # barriga clara
    l.ovalo(5, 22, 1.6, 2.6, "pelo")                          # brazos (el derecho, sujetando el remo)
    l.ovalo(18, 19, 1.8, 2.0, "pelo")
    for (x, y) in ((3, 28), (2, 29), (2, 30), (3, 30)):        # la cola, gruesa
        l.px(x, y, "pelo", 2)
    l.ovalo(12, 12.5, 5.2, 4.6, "pelo")                       # cabeza
    l.ovalo(12, 15, 3.0, 2.0, "hocico", plano=True)           # morro claro
    l.px(11, 14, "nariz"); l.px(12, 14, "nariz"); l.px(13, 14, "nariz")
    l.px(12, 16, "rubor")                                      # la sonrisa
    ojos(l, 11, 8, 14, alto=2)
    for (x0, lado) in ((7, -1), (16, 1)):                     # bigotes
        for k in range(3):
            l.px(x0 + lado * k, 15 + (k % 2), "cana", 3)
    l.px(7, 9, "pelo", 1); l.px(17, 9, "pelo", 1)             # orejitas redondas
    l.rect(6, 6, 18, 7, "paja", 2); l.rect(6, 6, 18, 6, "paja", 3)   # el sombrero de paja
    l.rect(8, 3, 16, 5, "paja", 2); l.rect(8, 3, 16, 3, "paja", 3)
    l.rect(8, 5, 16, 5, "bufanda", 2)                         # la cinta azul
    for x in (9, 15):                                         # patas
        l.rect(x - 1, 29, x + 1, 30, "pelo", 1)
    # detalle: un pez asomando del bolsillo y una flor en el sombrero
    l.px(10, 25, "azul", 3); l.px(10, 26, "azul", 2); l.px(9, 25, "azul", 2)
    l.px(15, 4, "flor", 3); l.px(16, 4, "flor", 2)
    return l


# --- Los fotogramas de cada aldeano (para que estén vivos) -----------------------------------------
# 0 quieto · 1 respira (todo lo de arriba baja un píxel; los pies, no) · 2 parpadea (los ojos se cierran) · 3 su gesto

def taa(blanco=False):
    """TAA: el armiño farolero de Sigilia, el que enciende los faroles del Paso de la Escarcha. Esbelto y de cuello
    largo, de pelo blanco con la punta de la cola negra, gafas redondas de latón, bufanda morada de escriba y la
    pértiga de farolero con su ganchito y una llamita en lo alto. EN BLANCO (blanco=True): la Tinta Quieta le ha
    borrado el nombre: todo pálido y sin color, los ojos vacíos y la llamita apagada."""
    l = Lienzo()
    for y in range(3, 31):                                    # la pértiga de farolero
        l.px(19, y, "laton", 2 if y % 6 else 3)
    l.px(20, 3, "laton", 2); l.px(21, 4, "laton", 2); l.px(21, 5, "laton", 1)       # el gancho
    l.px(18, 2, "brasa", 2); l.px(18, 1, "brasa", 3); l.px(17, 2, "brasa", 1)       # la llamita
    for (x, y) in ((3, 29), (2, 28), (2, 27), (3, 26), (4, 25), (5, 25)):            # la cola, larga, con la punta negra
        l.px(x, y, "armino", 2)
    for (x, y) in ((3, 29), (2, 28), (2, 27)):
        l.px(x, y, "tinta", 2)
    l.ovalo(11.5, 23, 4.3, 7.0, "armino")                     # el cuerpo, esbelto
    l.ovalo(11.5, 24.5, 2.2, 4.5, "hocico", plano=True)       # la tripa crema
    l.ovalo(7.5, 22, 1.4, 3.0, "armino")                      # el brazo de la izquierda
    l.ovalo(17.5, 19.5, 1.6, 2.0, "armino")                   # la mano que sujeta la pértiga
    l.ovalo(11.5, 15.5, 2.6, 2.8, "armino")                   # el cuello largo
    l.ovalo(11.5, 10, 5.0, 4.0, "armino")                     # la cabeza
    l.ovalo(11.5, 12.6, 2.4, 1.5, "hocico", plano=True)       # el morro claro
    l.px(11, 12, "rosa", 2); l.px(12, 12, "rosa", 2)          # la naricilla
    l.px(7, 6, "armino", 2); l.px(8, 5, "armino", 2); l.px(8, 6, "rosa", 1)       # orejas redondas
    l.px(15, 6, "armino", 2); l.px(14, 5, "armino", 2); l.px(14, 6, "rosa", 1)
    ojos(l, 9, 9, 14, alto=2)
    for x0 in (9, 14):                                        # las gafas redondas de latón: la montura, fina
        l.px(x0, 8, "laton", 3); l.px(x0 + 1, 8, "laton", 3)
        l.px(x0, 11, "laton", 1); l.px(x0 + 1, 11, "laton", 1)
    for y in (9, 10):
        l.px(8, y, "laton", 2); l.px(16, y, "laton", 2)
    for x in (11, 12, 13):                                    # el puente
        l.px(x, 9, "laton", 3 if x == 12 else 2)
    for (x0, lado) in ((8, -1), (15, 1)):                     # bigotes finos
        for k in range(2):
            l.px(x0 + lado * k, 12 + k, "cana", 3)
    l.rect(8, 16, 15, 17, "morado", 2); l.rect(8, 16, 15, 16, "morado", 3)          # la bufanda morada
    l.px(9, 18, "morado", 2); l.px(9, 19, "morado", 1); l.px(10, 20, "morado", 1)
    l.px(13, 17, "laton", 3)                                  # el broche de pluma
    for x in (9, 14):                                         # las patas
        l.rect(x - 1, 29, x + 1, 30, "armino", 1)
    if blanco:
        # la Tinta Quieta: todo pálido y sin color, los ojos vacíos, la llamita apagada
        for y in range(ALTO):
            for x in range(ANCHO):
                c = l.m[y][x]
                if c is None:
                    continue
                mat, t = c
                if mat == "brasa":
                    l.m[y][x] = None
                elif mat == "ojo":
                    l.m[y][x] = ("en_blanco", 0)
                elif mat == "brillo":
                    l.m[y][x] = ("en_blanco", 1)
                else:
                    l.m[y][x] = ("en_blanco", max(1, min(3, t + (1 if mat in ("tinta", "morado", "laton") else 0))))
    return l


def taa_blanco():
    return taa(True)


def _armino_base(l, cola_x=3):
    """El cuerpo de un armiño de Sigilia (sin ropa): esbelto, de cuello largo, cola con la punta negra."""
    for (x, y) in ((cola_x, 29), (cola_x - 1, 28), (cola_x - 1, 27), (cola_x, 26), (cola_x + 1, 25), (cola_x + 2, 25)):
        l.px(x, y, "armino", 2)
    for (x, y) in ((cola_x, 29), (cola_x - 1, 28), (cola_x - 1, 27)):
        l.px(x, y, "tinta", 2)
    l.ovalo(11.5, 23, 4.3, 7.0, "armino")
    l.ovalo(11.5, 24.5, 2.2, 4.5, "hocico", plano=True)
    l.ovalo(7.5, 22, 1.4, 3.0, "armino")
    l.ovalo(11.5, 15.5, 2.6, 2.8, "armino")
    l.ovalo(11.5, 10, 5.0, 4.0, "armino")
    l.ovalo(11.5, 12.6, 2.4, 1.5, "hocico", plano=True)
    l.px(11, 12, "rosa", 2); l.px(12, 12, "rosa", 2)
    l.px(7, 6, "armino", 2); l.px(8, 5, "armino", 2); l.px(8, 6, "rosa", 1)
    l.px(15, 6, "armino", 2); l.px(14, 5, "armino", 2); l.px(14, 6, "rosa", 1)
    for (x0, lado) in ((8, -1), (15, 1)):
        for k in range(2):
            l.px(x0 + lado * k, 12 + k, "cana", 3)
    for x in (9, 14):
        l.rect(x - 1, 29, x + 1, 30, "armino", 1)


def kalamu():
    """KALAMU: la archivera mayor de Maandiko, una armiña muy anciana. Encorvada, con el pelo de la cabeza más ralo,
    unas gafas pequeñas con su cadenita, un chal morado con flecos sobre los hombros y, de bastón, una pluma de cobre
    enorme. Guarda el trozo del norte del mapa de Mzee Shamba."""
    l = Lienzo()
    for y in range(7, 31):                                    # el bastón de madera oscura...
        l.px(19, y, "concha", 1 if y % 4 else 2)
    for (x, y) in ((18, 6), (20, 6), (17, 5), (21, 5), (18, 4), (20, 4), (17, 3), (19, 3), (18, 2), (19, 1)):   # ...que acaba en una pluma blanca
        l.px(x, y, "cana", 3 if (x + y) % 2 else 2)
    _armino_base(l)
    l.ovalo(17.5, 19.5, 1.6, 2.0, "armino")                   # la mano en la pluma
    ojos(l, 9, 9, 14, alto=2)
    l.px(9, 8, "cana", 3); l.px(10, 8, "cana", 3); l.px(14, 8, "cana", 3); l.px(15, 8, "cana", 3)   # cejas blancas, pobladas
    for x0 in (9, 14):                                        # medias gafas, bajitas, en la punta del hocico
        l.px(x0 - 1, 10, "laton", 2); l.px(x0, 11, "laton", 3); l.px(x0 + 1, 11, "laton", 3); l.px(x0 + 2, 10, "laton", 2)
    for y in range(10, 17):                                   # la cadenita de las gafas
        l.px(16 + (y - 10) // 3, y, "laton", 1)
    l.rect(6, 15, 17, 18, "morado", 2); l.rect(6, 15, 17, 15, "morado", 3)   # el chal
    for x in range(6, 18, 2):
        l.px(x, 19, "morado", 1)
    l.px(7, 16, "laton", 3); l.px(16, 16, "laton", 3)         # el broche
    l.px(10, 6, "cana", 2); l.px(12, 5, "cana", 2); l.px(13, 6, "cana", 1)   # los pelos blancos sueltos
    return l


def wino():
    """WINO: el comerciante del Mercado de Tinta, un armiño joven y rechoncho, con una boina de lana, un delantal de
    cuero manchado de tinta de todos los colores y una pluma detrás de la oreja. Siempre sonríe."""
    l = Lienzo()
    _armino_base(l)
    l.ovalo(11.5, 23, 4.8, 7.0, "armino")                     # (más rechoncho)
    l.ovalo(11.5, 25, 3.2, 4.6, "delantal")                   # el delantal de cuero
    for (x, y, c) in ((10, 23, "azul"), (13, 25, "rojo"), (11, 27, "morado"), (12, 22, "rana")):
        l.px(x, y, c, 2)                                      # manchas de tinta
    l.ovalo(17, 22, 1.4, 3.0, "armino")
    ojos(l, 9, 9, 14, alto=2)
    l.px(11, 13, "rubor", 0); l.px(12, 13, "rubor", 0)         # la sonrisa
    l.px(8, 11, "rubor"); l.px(15, 11, "rubor")
    l.ovalo(11.5, 6.5, 5.2, 2.2, "morado")                    # la boina
    l.px(11, 4, "morado", 3); l.px(12, 3, "morado", 2)
    for y in range(4, 9):                                     # la pluma detrás de la oreja
        l.px(16 + (8 - y) // 2, y, "cana", 3)
    return l


def escriba(blanco=False):
    """UN ESCRIBA de Maandiko: un armiño con su bufanda morada de escriba, un libro abierto y una pluma.
    EN BLANCO (blanco=True): la Tinta Quieta le ha borrado el nombre: pálido y sin color, con los ojos vacíos,
    la pluma seca y el libro en blanco."""
    l = Lienzo()
    _armino_base(l)
    l.ovalo(17, 21, 1.6, 2.0, "armino")
    l.rect(14, 19, 20, 22, "panuelo", 3)                      # el libro abierto, en blanco
    l.px(17, 19, "panuelo", 1); l.px(17, 20, "panuelo", 1); l.px(17, 21, "panuelo", 1)
    for y in range(14, 20):                                   # la pluma seca
        l.px(6 + (19 - y) // 3, y, "cana", 2)
    l.rect(8, 16, 15, 17, "morado", 2)                        # la bufanda de escriba
    l.rect(8, 16, 15, 16, "morado", 3)
    l.px(9, 18, "morado", 2); l.px(9, 19, "morado", 1)
    if not blanco:
        ojos(l, 9, 9, 14, alto=2)
        l.px(15, 20, "tinta", 2); l.px(16, 20, "tinta", 2); l.px(18, 20, "tinta", 2)     # lo escrito en el libro
        l.px(15, 21, "tinta", 1); l.px(17, 21, "tinta", 1)
        l.px(6, 13, "azul", 2)                                # la punta de la pluma, con tinta
        return l
    for y in range(ALTO):
        for x in range(ANCHO):
            c = l.m[y][x]
            if c is None:
                continue
            mat, t = c
            if mat in ("ojo", "brillo"):
                continue
            l.m[y][x] = ("en_blanco", max(1, min(3, t + (1 if mat in ("tinta", "morado", "laton") else 0))))
    ojos(l, 9, 9, 14, alto=2)
    for y in range(ALTO):                                     # los ojos, vacíos (huecos grises, sin brillo)
        for x in range(ANCHO):
            if l.m[y][x] and l.m[y][x][0] in ("ojo", "brillo"):
                l.m[y][x] = ("gris_c", 1)
    return l


def escriba_blanco():
    return escriba(True)


def _copia(l):
    n = Lienzo()
    n.m = [fila[:] for fila in l.m]
    return n


def respira(l):
    n = _copia(l)
    for y in range(27, 0, -1):
        n.m[y] = l.m[y - 1][:]
    n.m[0] = [None] * ANCHO
    return n


def parpadea(l):
    """Los ojos se cierran: de cada ojo queda solo la fila de abajo (las pestañas); lo de encima, del color de la piel."""
    n = _copia(l)
    for y in range(ALTO - 1):
        for x in range(ANCHO):
            c = l.m[y][x]
            if c and c[0] in ("ojo", "brillo"):
                abajo = l.m[y + 1][x]
                if abajo and abajo[0] in ("ojo", "brillo"):
                    piel = None
                    for yy in range(y - 1, -1, -1):
                        cc = l.m[yy][x]
                        if cc and cc[0] not in ("ojo", "brillo"):
                            piel = cc
                            break
                    n.m[y][x] = piel
                elif c[0] == "brillo":
                    n.m[y][x] = ("ojo", 2)
    return n


def alza_derecha(l, filas=2, desde_x=17, desde_y=0):
    """Gesto por defecto: levanta lo que lleva en la mano derecha (lo que hay a la derecha de «desde_x» y por debajo de
    «desde_y», levantando todo el objeto hasta el suelo)."""
    n = _copia(l)
    for x in range(desde_x, ANCHO):
        for y in range(desde_y, ALTO):
            n.m[y][x] = l.m[y + filas][x] if y + filas < ALTO else None
    return n


## Desde qué columna (y fila) se levanta lo de la mano derecha en el gesto por defecto (para no mover picos ni orejas)
ALZA = {"bibi": (19, 0), "msafiri": (20, 0), "korongo": (20, 0), "mbuzi": (19, 0), "mdiria": (16, 15), "bata": (19, 0),
        "kasia": (17, 0), "sungura": (19, 0)}


def _gesto_corteza():
    """Corteza alza el martillo por encima del hombro, y saltan chispas."""
    l = alza_derecha(corteza(), filas=8)
    l.px(23, 2, "brasa", 3); l.px(17, 1, "brasa", 2); l.px(22, 0, "brasa", 2)
    return l


def _gesto_pino():
    """Pino saluda con la mano, muy alto."""
    l = pino()
    for y in range(20, 27):
        for x in range(15, 20):
            if l.m[y][x] and l.m[y][x][0] == "pie_seta" and x >= 16:
                l.m[y][x] = None
    l.ovalo(18.5, 16, 1.6, 2.4, "pie_seta")
    l.px(19, 13, "pie_seta", 3); l.px(18, 13, "pie_seta", 2)
    return l


def _gesto_juncia():
    """Juncia levanta el cucharón y sale vapor."""
    l = alza_derecha(juncia(), filas=4)
    for (x, y) in ((20, 7), (21, 6), (19, 5), (20, 4)):
        l.px(x, y, "vapor", 2 + (x + y) % 2)
    return l


def _gesto_tawi():
    """Tawi agita el ala."""
    l = tawi()
    for y in range(19, 28):
        for x in range(1, 7):
            if l.m[y][x] and l.m[y][x][0] == "pajaro":
                l.m[y][x] = None
    l.ovalo(4, 17, 2.4, 3.2, "pajaro")
    l.px(2, 14, "pajaro", 3); l.px(3, 14, "pajaro", 3)
    return l


def _gesto_fuko():
    """Fuko se sube las gafas con las dos manos (casi no ve)."""
    l = fuko()
    for y in range(18, 25):
        for x in list(range(1, 8)) + list(range(17, 24)):
            if l.m[y][x] and l.m[y][x][0] == "rosa":
                l.m[y][x] = None
    l.ovalo(7, 15, 2.2, 2.2, "rosa")
    l.ovalo(17, 15, 2.2, 2.2, "rosa")
    return l


GESTOS = {"corteza": _gesto_corteza, "pino": _gesto_pino, "juncia": _gesto_juncia, "tawi": _gesto_tawi, "fuko": _gesto_fuko}


def fotogramas(nombre):
    fn = ALDEANOS[nombre]
    base = fn()
    gesto = GESTOS.get(nombre)
    dx, dy = ALZA.get(nombre, (17, 0))
    g = gesto() if gesto else alza_derecha(base, desde_x=dx, desde_y=dy)
    return [base, respira(base), parpadea(base), g]


ALDEANOS = {"kalamu": kalamu, "wino": wino, "escriba": escriba, "escriba_blanco": escriba_blanco, "taa": taa, "taa_blanco": taa_blanco, "bata": bata, "kasia": kasia, "mdiria": mdiria, "mbuzi": mbuzi, "sungura": sungura, "fuko": fuko, "korongo": korongo, "msafiri": msafiri, "bibi": bibi, "pino": pino, "corteza": corteza, "juncia": juncia, "tawi": tawi}

if __name__ == "__main__":
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    destino = os.path.join(raiz, "arte", "personajes", "aldeanos")
    os.makedirs(destino, exist_ok=True)
    for nombre in ALDEANOS:
        fotos = fotogramas(nombre)
        fotos[0].imagen().save(os.path.join(destino, f"{nombre}_frente.png"))
        tira = Image.new("RGBA", (ANCHO * len(fotos), ALTO), (0, 0, 0, 0))
        for i, f in enumerate(fotos):
            tira.paste(f.imagen(), (i * ANCHO, 0))
        tira.save(os.path.join(destino, f"{nombre}_anim.png"))
    print("Aldeanos dibujados en", destino)
