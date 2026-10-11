"""LOS OBJETOS DE LA GRANJA DE MZEE SHAMBA, pintados con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_granja.py

Mismas medidas y fotogramas que los de antes (el juego no cambia), en arte/mundos/kitovu/:
  zanahoria.png       2 × 12×12   plantada (penacho de hojas y el hombro naranja) / arrancada (el hoyo)
  cerca.png           2 × 32×16   rota (tabla caída y astillada) / arreglada (tablas nuevas y clavos)
  tronco.png          2 × 36×18   con tablas apoyadas / sin ellas (corteza, musgo y el corte con anillos)
  espantapajaros.png  18×32       camisa remendada, paja que asoma, cara de saco cosida y sombrero
  trigo.png           2 × 16×18   espigas de grano que se mecen
  gallina.png         2 × 10×10   gallina blanca con cresta roja (dos pasos)
  arbol_seco.png      28×40       árbol muerto con el tronco agrietado y ramas retorcidas
  (carro(): un intento pintado del carro volcado; a ese tamaño se leía peor que el de píxel, así que no se usa)
Todos llevan contorno selectivo (un tono más oscuro del propio color), como el resto de sprites.
Lo más pequeño (zanahoria, espantapájaros y gallina) está dibujado píxel a píxel (mapas de letras al final
del archivo): a ese tamaño el pixel art hecho a mano se lee mejor que lo pintado. Las funciones pintadas
de esos tres se quedan por si algún día se dibujan más grandes.
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa, RAIZ  # noqa: E402
from pintar_casa_shamba import TRONCO, CORTE, vetas, rect  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "kitovu")
LUZ = (-0.6, -0.7, 0.5)
TIERRA = ["#1d140f", "#2b1e17", "#3f2c21", "#533b2d", "#684937", "#7c5843", "#91674f"]
NARANJA = ["#5a1a08", "#8a2a0c", "#b8420f", "#d45a17", "#ef8a26", "#f9b947"]
HOJA = ["#12240f", "#1f3a16", "#2f5a20", "#3e7a2a", "#5d9a3a", "#8ac05a", "#b8e08a"]
TABLA = ["#2a1a12", "#47291c", "#643a26", "#7f4d33", "#9a6544", "#b88259", "#d2a07c"]
TABLA_NUEVA = ["#3d2a10", "#704f25", "#a37036", "#c68756", "#e2a978", "#f3cf9e"]
HIERRO = ["#1b1c1f", "#3d3f43", "#6a6c6f", "#a3a4a6"]
PAJA = ["#3d2a10", "#704f25", "#a37036", "#d29a43", "#efc06a", "#f8dc96"]
SACO = ["#4a3a26", "#6e5a40", "#9a8462", "#bfa982", "#ddc8a0", "#efe0bf"]
TELA = ["#3a0d14", "#5a1820", "#8f2532", "#b03a44", "#d5525e", "#e98378"]
BLANCO = ["#6a6c6f", "#a3a4a6", "#d8d4c8", "#efe9dc", "#fffdf4"]
CONTORNO = 0.42


def tira(imgs):
    return np.concatenate(imgs, axis=1)


# ---------------------------------------------------------------- zanahoria
def zanahoria(arrancada):
    lz = Lienzo(12, 12, s=8, semilla=1)
    monton = lz.elipse(6, 10, 5, 1.9)
    migas = lz.ruido(0.4, 2, semilla=2)
    lz.sombrear(monton, TIERRA, 1.6, LUZ, textura=migas, fuerza_tex=0.45)
    if arrancada:
        hoyo = lz.elipse(6, 10.2, 2.6, 1.1)
        lz.pintar(hoyo, "#120b08")
        lz.pintar(lz.elipse(5.6, 9.7, 2.2, 0.6), "#2b1e17", 0.7)
        for (x, y) in [(2.5, 9.2), (9.6, 9.6), (3.4, 11.2), (8.8, 11.4)]:
            lz.sombrear(lz.circulo(x, y, 0.55), TIERRA, 0.4, LUZ)
        return lz.sprite(contorno=CONTORNO)
    # el hombro naranja que asoma, con sus anillos
    hombro = lz.elipse(6, 9.0, 2.2, 1.6)
    anillos = np.clip(np.abs(np.sin((lz.y - 9) * 6)), 0, 1)
    lz.sombrear(hombro, NARANJA, 1.2, LUZ, textura=1 - anillos * 0.5, fuerza_tex=0.3)
    # el penacho: hojas finas y rizadas, en abanico
    hojas = np.zeros((lz.H, lz.W))
    rng = np.random.default_rng(3)
    for (ang, largo) in [(-150, 4.2), (-125, 5.6), (-100, 6.4), (-80, 6.6), (-58, 5.6), (-32, 4.2)]:
        a = np.radians(ang + (rng.random() - 0.5) * 8)
        x0, y0 = 6, 7.8
        x1, y1 = x0 + np.cos(a) * largo, y0 + np.sin(a) * largo
        tallo = lz.trazo(lz.curva((x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - 0.4), (x1, y1), n=10), 0.55, 0.35)
        hojas = np.maximum(hojas, tallo)
        for k in range(4):
            tt = 0.35 + k * 0.18
            hx, hy = x0 + (x1 - x0) * tt, y0 + (y1 - y0) * tt
            hojas = np.maximum(hojas, lz.elipse(hx, hy, 1.0, 0.55, ang + 60 * (1 if k % 2 else -1)))
    lz.sombrear(hojas, HOJA, 0.8, LUZ, textura=lz.ruido(0.3, 2, semilla=4), fuerza_tex=0.3)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- cerca
def poste(lz, x, y0, y1, ancho=2.2, rampa_m=TABLA):
    p = rect(lz, x - ancho / 2, y0, x + ancho / 2, y1)
    p = np.maximum(p, lz.elipse(x, y0, ancho / 2, 0.8))
    lz.sombrear(p, rampa_m, ancho * 0.5, LUZ, textura=vetas(lz, 0.3, 9, False), fuerza_tex=0.35)
    lz.sombrear(lz.elipse(x, y0, ancho / 2 - 0.2, 0.6), CORTE, 0.4, LUZ)


def tablon(lz, puntos, grueso, rampa_m=TABLA, clavos=()):
    t = lz.trazo(puntos, grueso, grueso)
    lz.sombrear(t, rampa_m, grueso * 0.45, LUZ, textura=vetas(lz, 0.35, 11, True), fuerza_tex=0.4)
    for (cx, cy) in clavos:
        lz.sombrear(lz.circulo(cx, cy, 0.45), HIERRO, 0.3, LUZ)
    return t


def cerca(arreglada):
    lz = Lienzo(32, 16, s=8, semilla=5)
    lz.pintar(lz.desenfocar(lz.elipse(16, 15.2, 15, 0.9), 0.4), "#1d2e18", 0.0)
    for x in (2.5, 15.5, 28.5):
        poste(lz, x, 2.4, 15.6)
    if arreglada:
        for y in (5.6, 10.6):
            tablon(lz, [(0, y), (32, y)], 2.0, TABLA_NUEVA, clavos=[(2.5, y), (15.5, y), (28.5, y)])
    else:
        # la tabla de arriba se quedó a medias, astillada en la punta
        tablon(lz, [(0, 5.6), (14.2, 5.6)], 2.0, TABLA, clavos=[(2.5, 5.6)])
        astilla = lz.poligono([(14, 4.6), (16.6, 5.2), (14.4, 5.8), (16, 6.6), (14, 6.6)])
        lz.sombrear(astilla, TABLA, 0.6, LUZ)
        tablon(lz, [(0, 10.6), (6, 10.6)], 2.0, TABLA, clavos=[(2.5, 10.6)])
        # la tabla caída en la hierba y un trozo partido
        tablon(lz, [(17, 14.2), (30.5, 10.2)], 1.9, TABLA)
        tablon(lz, [(18.5, 15.4), (25.5, 14.6)], 1.3, TABLA)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- tronco caído
def tronco(con_tablas):
    lz = Lienzo(36, 18, s=8, semilla=6)
    cuerpo = lz.elipse(16, 12, 15, 5)
    surcos = vetas(lz, 0.35, 21, True, 7)
    lz.sombrear(cuerpo, TRONCO, 4, LUZ, textura=surcos, fuerza_tex=0.55)
    # nudos y una rama rota
    for (nx, ny) in [(9, 11), (20, 13)]:
        nudo = lz.elipse(nx, ny, 1.4, 0.9)
        lz.pintar(nudo, "#1a0f0b", 0.8)
        lz.pintar(lz.elipse(nx - 0.3, ny - 0.3, 0.7, 0.4), "#7f4d33", 0.7)
    rama = lz.trazo([(13, 8), (11.5, 5.4)], 1.4, 0.9)
    lz.sombrear(rama, TRONCO, 0.6, LUZ)
    # musgo encima
    musgo = (lz.ruido(1.0, 3, semilla=8) > 0.6) * cuerpo * np.clip((10.5 - lz.y) / 3, 0, 1)
    lz.pintar(musgo, rampa(HOJA[2:6], lz.ruido(0.4, 2, semilla=9)), 0.9)
    # el corte, con sus anillos y una grieta
    corte = lz.elipse(30, 12, 3.2, 5)
    d = np.hypot((lz.x - 30) / 3.2, (lz.y - 12) / 5)
    lz.pintar(corte, rampa(CORTE, np.clip(0.8 - d * 0.5 - (np.sin(d * 11) * 0.5 + 0.5) * 0.25, 0, 1)))
    lz.pintar(np.clip(corte - lz.elipse(30, 12, 2.6, 4.4), 0, 1), "#47291c")
    lz.pintar(lz.trazo([(30, 12), (31.6, 9)], 0.35) * corte, "#47291c", 0.8)
    # setas pequeñas al pie
    for (sx, sy) in [(5, 15.5), (6.6, 16)]:
        lz.sombrear(lz.trazo([(sx, sy), (sx, sy - 1.2)], 0.5), ["#c4b8a0", "#efe0bf"], 0.3, LUZ)
        lz.sombrear(lz.elipse(sx, sy - 1.4, 0.9, 0.5), TELA[2:], 0.4, LUZ)
    if con_tablas:
        for k in range(3):
            x0 = 3.5 + k * 4
            t = lz.poligono([(x0, 15.5), (x0 + 2.6, 15.5), (x0 + 2.4 + 0.6, 2.4 + k), (x0 + 0.4, 2 + k)])
            lz.sombrear(t, TABLA_NUEVA, 1.2, LUZ, textura=vetas(lz, 0.3, 11, False, 10 + k), fuerza_tex=0.4)
            lz.pintar(np.clip(t - lz.desenfocar(t, 0.4) * 0, 0, 1) * (np.abs(lz.x - (x0 + 1.4)) < 0.15), "#704f25", 0.0)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- espantapájaros
def espantapajaros():
    lz = Lienzo(18, 32, s=8, semilla=11)
    poste(lz, 9, 9, 31.8, 1.7)
    travesano = tablon(lz, [(0.6, 13.6), (17.4, 13.6)], 1.5, TABLA)
    # paja que asoma por las mangas y el bajo
    paja = np.zeros((lz.H, lz.W))
    rng = np.random.default_rng(12)
    for (x0, y0, dx, dy) in [(1.2, 14.5, -1, 1), (16.8, 14.5, 1, 1)] + [(4.5 + k * 1.3, 22.4, (rng.random() - 0.5) * 1.5, 1) for k in range(8)]:
        for j in range(3):
            paja = np.maximum(paja, lz.trazo([(x0 + j * 0.3, y0), (x0 + dx * (1 + rng.random()) + j * 0.3, y0 + dy * (1.4 + rng.random() * 1.4))], 0.45, 0.3))
    lz.sombrear(paja, PAJA, 0.4, LUZ)
    # la camisa remendada
    camisa = lz.poligono([(3.6, 11.6), (14.4, 11.6), (15.6, 15.6), (13.6, 16.2), (13.4, 22.6), (4.6, 22.6), (4.4, 16.2), (2.4, 15.6)])
    cuadros = ((np.floor(lz.x / 1.6) + np.floor(lz.y / 1.6)) % 2)
    lz.sombrear(camisa, TELA, 3, LUZ, textura=cuadros * 0.5 + lz.ruido(0.4, 2) * 0.5, fuerza_tex=0.35)
    remiendo = rect(lz, 7.4, 16.2, 10.4, 19.2)
    lz.sombrear(remiendo, SACO, 1, LUZ)
    for k in range(6):
        lz.pintar(lz.trazo([(7.4 + k * 0.6, 16.2), (7.4 + k * 0.6, 16.6)], 0.25), "#4a3a26", 0.8)
    for (bx, by) in [(9, 13.4), (9, 21)]:
        lz.sombrear(lz.circulo(bx, by, 0.5), ["#3d2a10", "#a37036", "#efc06a"], 0.3, LUZ)
    # cabeza de saco con cara cosida
    cabeza = lz.elipse(9, 7.4, 4.2, 4.2)
    lz.sombrear(cabeza, SACO, 2.8, LUZ, textura=(np.sin(lz.x * 6) * np.sin(lz.y * 6) > 0).astype(float), fuerza_tex=0.15)
    lz.pintar(lz.trazo([(6.4, 10.6), (11.6, 10.6)], 1.0), "#704f25")            # el cordel del cuello
    for (ox, oy) in [(7.4, 6.6), (10.8, 6.6)]:
        lz.pintar(lz.trazo([(ox - 0.7, oy - 0.7), (ox + 0.7, oy + 0.7)], 0.4) + lz.trazo([(ox - 0.7, oy + 0.7), (ox + 0.7, oy - 0.7)], 0.4), "#251812")
    boca = lz.curva((6.8, 8.8), (9, 9.8), (11.2, 8.8), n=12)
    lz.pintar(lz.trazo(boca, 0.35), "#251812")
    for k in range(1, 11, 2):
        x_, y_ = boca[k]
        lz.pintar(lz.trazo([(x_, y_ - 0.5), (x_, y_ + 0.5)], 0.25), "#251812")
    # sombrero de paja
    ala = lz.elipse(9, 3.6, 6.4, 1.4)
    copa = np.maximum(lz.elipse(9, 1.8, 3.6, 1.8), rect(lz, 5.4, 1.8, 12.6, 3.4))
    trenzado = (np.sin(lz.x * 3 + lz.y * 1.2) > 0).astype(float)
    lz.sombrear(ala, PAJA, 0.8, LUZ, textura=trenzado, fuerza_tex=0.3)
    lz.sombrear(copa, PAJA, 1.4, LUZ, textura=trenzado, fuerza_tex=0.3)
    lz.pintar(rect(lz, 5.5, 2.6, 12.5, 3.4), "#3e7a2a", 0.9)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- trigo
def trigo(fotograma):
    lz = Lienzo(16, 18, s=8, semilla=13)
    rng = np.random.default_rng(14)
    for k, x in enumerate((2.8, 6.2, 9.6, 13.0)):
        inclina = (1 if fotograma else -1) * (0.9 if k % 2 else 0.3)
        cima = (x + inclina, 6.5)
        tallo = lz.trazo(lz.curva((x, 18), (x + inclina * 0.2, 12), cima, n=12), 0.8, 0.55)
        lz.sombrear(tallo, ["#4a5a1a", "#7c8a2a", "#a8a840", "#c9c060"], 0.4, LUZ)
        for (hy, lado) in [(13.5, -1), (11, 1)]:
            hoja = lz.trazo(lz.curva((x + inclina * 0.1, hy), (x + lado * 1.6, hy - 1), (x + lado * 2.6, hy + 0.6), n=8), 0.7, 0.3)
            lz.sombrear(hoja, ["#2f4a14", "#5d7a20", "#8aa13a"], 0.3, LUZ)
        # la espiga: granos en dos filas, con las barbas arriba
        for j in range(6):
            gy = cima[1] - j * 1.0
            gx = cima[0] + inclina * j * 0.15
            for lado in (-0.55, 0.55):
                grano = lz.elipse(gx + lado, gy, 0.7, 0.9, 20 * np.sign(lado))
                lz.sombrear(grano, PAJA, 0.5, LUZ)
        for j in range(3):
            lz.pintar(lz.trazo([(cima[0] + inclina * 0.9 + (j - 1) * 0.6, 1.4), (cima[0] + inclina * 1.2 + (j - 1) * 1.1, -0.6)], 0.25), "#efc06a", 0.9)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- gallina
def gallina(fotograma):
    lz = Lienzo(10, 10, s=10, semilla=15)
    # patas
    for px_ in ((4.2, 5.8) if fotograma == 0 else (5.0, 5.4)):
        lz.pintar(lz.trazo([(px_, 7.6), (px_, 9.6)], 0.5), "#df9022")
        lz.pintar(lz.trazo([(px_ - 0.6, 9.6), (px_ + 0.6, 9.6)], 0.4), "#df9022")
    # cola de plumas
    cola = np.maximum(lz.elipse(8.2, 4.6, 1.5, 2.2, -25), lz.elipse(8.8, 4.0, 0.9, 1.8, -40))
    lz.sombrear(cola, BLANCO, 1, LUZ)
    cuerpo = lz.elipse(5.2, 6.0, 3.5, 2.6)
    lz.sombrear(cuerpo, BLANCO, 2, LUZ, textura=lz.ruido(0.3, 2), fuerza_tex=0.15)
    ala = lz.elipse(5.8, 6.0, 2.0, 1.2, -10)
    lz.pintar(np.clip(ala - lz.elipse(5.6, 5.6, 1.8, 0.9, -10), 0, 1), "#a3a4a6", 0.8)
    cabeza = lz.circulo(2.7, 3.6, 1.7)
    lz.sombrear(cabeza, BLANCO, 1.2, LUZ)
    cresta = np.maximum.reduce([lz.circulo(2.0, 1.9, 0.6), lz.circulo(2.8, 1.7, 0.65), lz.circulo(3.5, 2.0, 0.5)])
    lz.sombrear(cresta, TELA[1:], 0.4, LUZ)
    lz.sombrear(lz.elipse(1.9, 4.9, 0.4, 0.6), TELA[2:], 0.3, LUZ)           # barbilla
    pico = lz.poligono([(1.2, 3.4), (-0.1, 3.9), (1.2, 4.3)])
    lz.sombrear(pico, ["#8a5a10", "#df9022", "#f9b947"], 0.3, LUZ)
    lz.pintar(lz.circulo(2.2, 3.4, 0.38), "#120b08")
    return lz.sprite(contorno=CONTORNO)


def main():
    from PIL import Image
    def guardar(nombre, arr):
        Image.fromarray(arr, "RGBA").save(os.path.join(SALIDA, nombre + ".png"))
        print("pintado", nombre)
    guardar("zanahoria", tira([mapa_pixeles(ZANAHORIA_PLANTADA, L_ZANAHORIA), mapa_pixeles(ZANAHORIA_ARRANCADA, L_ZANAHORIA)]))
    guardar("cerca", tira([cerca(False), cerca(True)]))
    guardar("tronco", tira([tronco(True), tronco(False)]))
    guardar("espantapajaros", mapa_pixeles(ESPANTAPAJAROS, L_ESPANTA))
    guardar("trigo", tira([trigo(0), trigo(1)]))
    guardar("gallina", tira([mapa_pixeles(GALLINA_0, L_GALLINA), mapa_pixeles(GALLINA_1, L_GALLINA)]))
    guardar("arbol_seco", arbol_seco())




# ---------------------------------------------------------------- pixel art a mano (para lo más pequeño)
def mapa_pixeles(filas, leyenda):
    """Un sprite dibujado píxel a píxel: cada letra de 'filas' es un color de 'leyenda' ('.' = transparente)."""
    from pintor import hex2
    alto, ancho = len(filas), max(len(f) for f in filas)
    out = np.zeros((alto, ancho, 4), np.uint8)
    for y, fila in enumerate(filas):
        for x, ch in enumerate(fila):
            if ch == "." or ch == " ":
                continue
            c = (np.array(hex2(leyenda[ch])) * 255).round().astype(np.uint8)
            out[y, x, :3] = c
            out[y, x, 3] = 255
    return out


L_ZANAHORIA = {"k": "#12240f", "g": "#2f5a20", "G": "#5d9a3a", "L": "#8ac05a", "l": "#b8e08a",
               "o": "#b8420f", "O": "#ef8a26", "Y": "#f9b947", "d": "#2b1e17", "D": "#533b2d", "T": "#7c5843",
               "e": "#1d140f", "x": "#0d0806", "m": "#684937"}
ZANAHORIA_PLANTADA = [
    "...k...k....",
    "..kLk.kLk.k.",
    "..kGLkLGkkLk",
    ".kLkGkGkLGk.",
    ".kGLkGkGLk..",
    "..kkGkGkGk..",
    "....kGLk....",
    "....kgGk....",
    "...eoOYOe...",
    ".eeoOOOYoee.",
    "eDTmoOOoDTDe",
    ".edddDDddde.",
]
ZANAHORIA_ARRANCADA = [
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "............",
    "..e.....e...",
    ".eTe...eTe..",
    "..eeeeeee.e.",
    ".eTDxxxxDTe.",
    "..eDDddDDe..",
]

L_GALLINA = {"k": "#525458", "w": "#fffdf4", "W": "#d8d4c8", "g": "#a3a4a6", "c": "#d5525e", "C": "#8f2532",
             "y": "#f9b947", "Y": "#df9022", "e": "#120b08", "f": "#df9022"}
GALLINA_0 = [
    "..kck.....",
    ".kcccK....".replace("K", "k"),
    ".kwwwk..kk",
    "ykewwk.kWk",
    "Yywwwkkwgk",
    ".kcwwwwWgk",
    ".kwwWwWggk",
    "..kgWWggk.",
    "...kfkfk..",
    "...f..f...",
]
GALLINA_1 = GALLINA_0[:8] + [
    "....kfk...",
    "...ff.f...",
]

L_ESPANTA = {"k": "#251812", "w": "#643a26", "W": "#9a6544", "V": "#b88259",
             "h": "#a37036", "H": "#d29a43", "J": "#efc06a", "j": "#f8dc96", "b": "#3e7a2a", "B": "#5d9a3a",
             "s": "#9a8462", "S": "#ddc8a0", "Q": "#efe0bf", "q": "#bfa982",
             "r": "#5a1820", "R": "#b03a44", "P": "#e98378", "p": "#c9b48c", "n": "#efc06a", "y": "#efc06a", "Y": "#a37036"}
ESPANTAPAJAROS = [
    "......kkkkkk......",
    ".....kHJjJHhk.....",
    ".....kHJJHHhk.....",
    "..kkkkbBBbbbkkkk..",
    ".kJjJHHHHHHHhhhhk.",
    "..kkkSQQQQQSSkkk..",
    "....kSQQQQSSssk...",
    "....kSkQQQkSssk...",
    "....kSQQQQSSssk...",
    "....kSkkkkkSssk...",
    ".....kSkSkSsssk...",
    "......kkWWWkkk....",
    "..kkkkkrRRRrkkkkk.",
    "yykWWWkRPRRRrkWWky",
    ".ykwwwkRPRnRrkwwky",
    "..kkkkkRRRRRrkkkk.",
    "......kRRppRRrk....",
    "......kRpPppRrk....",
    "......kRppppRrk....",
    "......kRRRRRrrk....",
    "......kRRRnRRrk....",
    "......krRRRRrrk....",
    "......kyYyykyYyk...",
    ".....yk.ykkWy.yk...",
    "........kWwk.......",
    "........kWwk.......",
    "........kWwk.......",
    "........kWwk.......",
    "........kWwk.......",
    "........kWwk.......",
    "........kWwk.......",
    "........kkkk.......",
]



# ---------------------------------------------------------------- árbol seco y carro volcado (alrededor de la granja)
GRIS_MADERA = ["#1b1c1f", "#2b2c30", "#3d3f43", "#525458", "#6a6c6f", "#85878a", "#a3a4a6"]


def arbol_seco():
    """Un árbol muerto (28×40): tronco agrietado que se abre en ramas retorcidas, sin hojas."""
    lz = Lienzo(28, 40, s=6, semilla=21)
    rng = np.random.default_rng(22)
    m = np.zeros((lz.H, lz.W))
    # raíces que se agarran al suelo
    for (dx, l_) in [(-5, 5), (4.6, 4.6), (-2, 3), (2.2, 3)]:
        m = np.maximum(m, lz.trazo(lz.curva((14, 35), (14 + dx * 0.6, 38), (14 + dx, 39.4), n=10), 2.4, 0.8))
    # tronco que se estrecha y se tuerce un poco
    tronco = lz.trazo(lz.curva((14, 39), (13, 28), (15, 18), n=20), 5.2, 2.6)
    m = np.maximum(m, tronco)
    # ramas principales y ramitas
    for (p0, p1, p2, g) in [((14.5, 22), (8, 16), (3, 9), 2.2), ((14.5, 20), (20, 15), (24, 7), 2.2), ((15, 18), (15.5, 10), (13.5, 2), 1.8),
                             ((13.6, 26), (8, 24), (3.5, 19), 1.6), ((15.2, 24), (21, 23), (25.5, 18), 1.4)]:
        m = np.maximum(m, lz.trazo(lz.curva(p0, p1, p2, n=16), g, 0.5))
        for j in range(2):
            tt = 0.55 + j * 0.25
            bx = p0[0] + (p2[0] - p0[0]) * tt
            by = p0[1] + (p2[1] - p0[1]) * tt
            a = np.arctan2(p2[1] - p0[1], p2[0] - p0[0]) + (0.7 if j % 2 else -0.7)
            l_ = 3 + rng.random() * 3
            m = np.maximum(m, lz.trazo([(bx, by), (bx + np.cos(a) * l_, by + np.sin(a) * l_)], 0.8, 0.3))
    grietas = vetas(lz, 0.3, 13, False, 23)
    lz.sombrear(m, GRIS_MADERA, 2.4, LUZ, textura=grietas, fuerza_tex=0.55)
    # un hueco oscuro en el tronco
    lz.pintar(lz.elipse(13.6, 30, 1.1, 1.8), "#0d0a0a", 0.9)
    return lz.sprite(contorno=CONTORNO)


def carro():
    """El carro volcado (44×28): la caja de tablas inclinada, una rueda en su sitio y otra caída, la lanza rota."""
    lz = Lienzo(44, 28, s=6, semilla=24)
    # la rueda caída en el suelo (detrás)
    caida = lz.elipse(33, 24.5, 6.4, 2.2)
    lz.sombrear(caida, TABLA, 1.2, LUZ)
    lz.pintar(lz.elipse(33, 24.2, 4.6, 1.4), "#47291c", 0.8)
    lz.pintar(lz.elipse(33, 24.2, 1.2, 0.5), "#3d3f43")
    # la caja del carro, inclinada
    caja = lz.poligono([(4, 11), (36, 15.5), (35, 21.5), (5, 17)])
    lz.sombrear(caja, TABLA, 2.6, LUZ, textura=vetas(lz, 0.35, 15, True, 25), fuerza_tex=0.45)
    lado = lz.poligono([(6, 6.5), (35, 10.5), (36, 15.5), (4, 11)])
    lz.sombrear(lado, TABLA, 2.2, LUZ, textura=vetas(lz, 0.35, 15, True, 26), fuerza_tex=0.45)
    for k in range(6):
        x0 = 8 + k * 5
        lz.pintar(lz.trazo([(x0, 7.2 + k * 0.7), (x0 - 0.6, 16.4 + k * 0.7)], 0.5), "#2a1a12", 0.8)
    lz.pintar(lz.trazo([(6, 6.6), (35, 10.6)], 0.9), "#b88259", 0.6)
    for (x, y) in [(8, 9), (33, 12.6)]:
        lz.sombrear(lz.circulo(x, y, 0.6), HIERRO, 0.4, LUZ)
    # la rueda entera, con radios y aro de hierro
    rx, ry, r = 12, 20, 6.4
    aro = np.clip(lz.circulo(rx, ry, r) - lz.circulo(rx, ry, r - 1.4), 0, 1)
    radios = np.zeros((lz.H, lz.W))
    for k in range(8):
        a = k * np.pi / 4 + 0.2
        radios = np.maximum(radios, lz.trazo([(rx, ry), (rx + np.cos(a) * (r - 1), ry + np.sin(a) * (r - 1))], 0.8))
    lz.sombrear(radios, TABLA, 0.4, LUZ)
    lz.sombrear(aro, TABLA, 0.7, LUZ)
    lz.pintar(np.clip(lz.circulo(rx, ry, r) - lz.circulo(rx, ry, r - 0.5), 0, 1), "#3d3f43")
    lz.sombrear(lz.circulo(rx, ry, 1.4), HIERRO, 1, LUZ)
    # la lanza rota, con astillas
    lanza = lz.trazo([(35, 13), (42.5, 6.5)], 1.5, 1.2)
    lz.sombrear(lanza, TABLA, 0.7, LUZ)
    lz.pintar(lz.poligono([(42, 5.4), (43.8, 4.6), (43, 6.2), (44, 6.6), (42.8, 7.4)]), "#9a6544")
    # hierbas que crecen por encima (lleva mucho tiempo ahí)
    hierba = np.zeros((lz.H, lz.W))
    for k in range(18):
        hx = 2 + rng_c.random() * 40 if False else 2 + k * 2.3
        hierba = np.maximum(hierba, lz.trazo([(hx, 27.8), (hx + (k % 3 - 1) * 0.8, 24.5 - (k % 4))], 0.6, 0.25))
    lz.sombrear(hierba, HOJA[1:6], 0.3, LUZ)
    return lz.sprite(contorno=CONTORNO)


if __name__ == "__main__":
    main()
