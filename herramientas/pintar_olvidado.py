"""EL SENDERO OLVIDADO, pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_olvidado.py

Genera en arte/mundos/raiz/olvidado/:
  pino_nevado.png   2 × 30×46 pinos oscuros de montaña con nieve en cada piso de ramas (dos formas)
  roca_nevada.png   2 × 26×20 rocas con la nieve encima y escarcha en las grietas
  brasero.png       2 × 22×24 el brasero de piedra del camino: 0 apagado (ceniza y escarcha) · 1 encendido (brasas;
                    las llamas las dibuja el juego, que se mueven)
  estatua.png       3 × 30×40 las estatuas de quienes se quedaron quietos, de piedra gris con escarcha, nieve encima
                    y las vetas violetas de Giza: 0 una liebre abrazada a una gavilla (para que nunca la segaran) ·
                    1 un tejón que sostiene un farol apagado (para que la noche no acabara) · 2 una garza con las alas
                    abiertas (para no tener que irse nunca)
  arco_ruinas.png   112×88 la puerta de las Ruinas del Primer Árbol, al final del sendero: dos pilares de piedra
                    clara rotos, raíces enormes del Primer Árbol abrazándolos, el arco con las nueve espirales de los
                    ecos talladas (la niebla de entre los pilares la dibuja el juego)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "olvidado")
LUZ = (-0.6, -0.7, 0.5)
NIEVE = ["#4a5870", "#6e7f98", "#98a8bf", "#c2cfde", "#e2eaf3", "#f6f9fc"]
PINO = ["#08120f", "#0f1d17", "#16291f", "#1f3828", "#2b4832", "#3a5a3e"]
CORTEZA = ["#1a120c", "#2c1f14", "#3f2d1d", "#544028"]
PIEDRA = ["#26282a", "#3a3d40", "#525659", "#6b7073", "#878c8e", "#a5a9aa", "#c4c7c7"]
CLARA = ["#3a3832", "#57544b", "#77736a", "#97938a", "#b6b2a8", "#d4d0c6", "#ece9e1"]   # la piedra del Primer Árbol
GIZA = "#8a4ad0"
RAIZ_C = ["#1c140e", "#2e2216", "#45341f", "#5e4a2c", "#7a6239"]


def _nieve_encima(lz, forma, grosor=1.6, semilla=0):
    """Nieve sobre lo que mira hacia arriba de una forma: la franja de arriba, irregular, con su sombra azulada."""
    bajar = int(grosor * lz.s)
    encima = forma * (1 - np.roll(forma, bajar, axis=0))
    borde = np.clip(encima + (lz.ruido(0.8, 2, semilla=semilla) > 0.62) * np.roll(encima, int(lz.s), axis=0), 0, 1) * forma
    lz.sombrear(borde, NIEVE[2:], 0.8, LUZ, textura=lz.ruido(0.5, 2, semilla=semilla + 1), fuerza_tex=0.2)
    return borde


def _escarcha(lz, forma, cuanta=0.7, semilla=0):
    """Motas de escarcha blanca y azulada sobre una forma (más arriba a la izquierda, donde da la luz)."""
    motas = (lz.ruido(0.35, 1, semilla=semilla) > 1 - cuanta * 0.35) * forma
    lz.pintar(motas, NIEVE[4], 0.75)
    lz.pintar((lz.ruido(0.5, 1, semilla=semilla + 3) > 0.86) * forma, NIEVE[5], 0.6)


def pino(k):
    W, H = 30, 46
    lz = Lienzo(W, H, s=6, semilla=1100 + k)
    cx = 15 + (0.5 if k else 0)
    tronco = lz.poligono([(cx - 2, H - 1), (cx - 1.4, H - 12), (cx + 1.4, H - 12), (cx + 2, H - 1)])
    lz.sombrear(tronco, CORTEZA, 1, LUZ, textura=lz.ruido(0.5, 2, semilla=1101), fuerza_tex=0.4)
    pisos = [(H - 9, 13, 10), (H - 17, 11, 9), (H - 24, 9, 8), (H - 31, 6.5, 8), (H - 37, 4, 7)]
    if k == 1:
        pisos = [(H - 9, 12, 9), (H - 16, 12.5, 9), (H - 23, 9.5, 9), (H - 30, 7.5, 8), (H - 37, 4.5, 8)]
    for i, (yb, ancho, alto) in enumerate(pisos):
        dientes = []
        for t in np.linspace(-1, 1, 9):
            dientes.append((cx + t * ancho, yb + (1.3 if int((t + 1) * 4) % 2 else 0)))
        piso = lz.poligono([(cx, yb - alto)] + dientes[::-1][:1] + dientes + [(cx + ancho, yb)])
        piso = np.maximum(piso, lz.poligono([(cx, yb - alto), (cx - ancho, yb), (cx + ancho, yb)]))
        lz.sombrear(piso, PINO, 3, LUZ, textura=lz.ruido(0.6, 2, semilla=1102 + i), fuerza_tex=0.35)
        _nieve_encima(lz, piso, 1.8 if i < 3 else 1.4, semilla=1110 + i * 3)
    _escarcha(lz, lz.poligono([(cx, 4), (cx - 14, H - 9), (cx + 14, H - 9)]), 0.4, semilla=1120 + k)
    return lz.sprite(contorno=0.4)


def roca(k):
    W, H = 26, 20
    lz = Lienzo(W, H, s=6, semilla=1200 + k)
    if k == 0:
        r = lz.poligono([(2, 19), (3, 10), (8, 4), (15, 3), (21, 6), (24, 13), (23, 19)])
    else:
        r = np.maximum(lz.poligono([(1, 19), (2, 12), (7, 8), (12, 9), (14, 19)]),
                       lz.poligono([(10, 19), (12, 7), (17, 3), (22, 6), (25, 19)]))
    lz.sombrear(r, PIEDRA, 2.5, LUZ, textura=lz.ruido(0.7, 3, semilla=1201 + k), fuerza_tex=0.35)
    grietas = lz.trazo([(9, 8), (11, 12), (10, 16)], 0.3) * r
    lz.pintar(grietas, PIEDRA[0])
    lz.pintar(grietas, NIEVE[3], 0.3)
    _nieve_encima(lz, r, 2.4, semilla=1205 + k)
    _escarcha(lz, r, 0.5, semilla=1208 + k)
    return lz.sprite(contorno=0.4)


def brasero(encendido):
    W, H = 22, 24
    lz = Lienzo(W, H, s=6, semilla=1300)
    pie = lz.poligono([(8, 23), (8.5, 14), (13.5, 14), (14, 23)])
    lz.sombrear(pie, PIEDRA, 1.5, LUZ, textura=lz.ruido(0.5, 2, semilla=1301), fuerza_tex=0.35)
    base = lz.elipse(11, 22.5, 6, 1.6)
    lz.sombrear(base, PIEDRA[1:], 1, LUZ)
    cuenco = lz.poligono([(2, 9), (20, 9), (17.5, 15), (4.5, 15)])
    lz.sombrear(cuenco, PIEDRA, 2, LUZ, textura=lz.ruido(0.6, 2, semilla=1302), fuerza_tex=0.35)
    # las espirales talladas en el cuenco (las mismas de los ecos)
    for cx in (7.5, 14.5):
        pts = [(cx + np.cos(t) * t * 0.22, 12 + np.sin(t) * t * 0.2) for t in np.linspace(0.3, 9, 24)]
        lz.pintar(lz.trazo(pts, 0.25), PIEDRA[1])
    boca = lz.elipse(11, 9, 9, 2.2)
    if encendido:
        lz.pintar(boca, "#2a1208")
        brasas = (lz.ruido(0.5, 2, semilla=1303) > 0.42) * boca
        lz.pintar(brasas, "#c84a14")
        lz.pintar((lz.ruido(0.4, 1, semilla=1304) > 0.7) * boca, "#ffb040")
        lz.sumar_luz(lz.desenfocar(boca, 2), "#ff8a2a", 0.5)
        lz.sumar_luz(lz.desenfocar(cuenco * (lz.y < 12), 1.5), "#ff9a40", 0.25)
    else:
        lz.pintar(boca, "#3a3c40")
        lz.pintar((lz.ruido(0.5, 2, semilla=1305) > 0.5) * boca, "#5c5f64")
        _escarcha(lz, np.maximum(cuenco, boca), 0.9, semilla=1306)
        _nieve_encima(lz, boca, 1.0, semilla=1307)
    return lz.sprite(contorno=0.4)


def _venas(lz, forma, puntos_lista):
    for pts in puntos_lista:
        lz.pintar(lz.trazo(pts, 0.35) * forma, GIZA)
        lz.sumar_luz(lz.desenfocar(lz.trazo(pts, 0.3) * forma, 0.8), "#b080ff", 0.25)


def estatua(k):
    W, H = 30, 40
    lz = Lienzo(W, H, s=6, semilla=1400 + k)
    peana = lz.poligono([(4, 39), (5, 34), (25, 34), (26, 39)])
    lz.sombrear(peana, PIEDRA, 1.5, LUZ, textura=lz.ruido(0.6, 2, semilla=1401), fuerza_tex=0.3)
    _nieve_encima(lz, peana, 1.4, semilla=1402)
    if k == 0:
        # una liebre de pie abrazada a una gavilla de trigo de piedra
        gavilla = lz.poligono([(11, 34), (12, 20), (18, 20), (19, 34)])
        espigas = np.zeros((lz.H, lz.W))
        for i in range(7):
            x = 11.5 + i
            espigas = np.maximum(espigas, lz.trazo([(x, 21), (x - 1 + i * 0.3, 15 - (i % 2))], 0.5))
        cuerpo = lz.elipse(15, 25, 6.5, 8.5)
        cabeza = lz.elipse(15, 13.5, 4.5, 4.2)
        orejas = np.maximum(lz.elipse(12.2, 5.5, 1.7, 5.2, -14), lz.elipse(17.8, 5.5, 1.7, 5.2, 14))
        dentro_orejas = np.maximum(lz.elipse(12.3, 5.8, 0.7, 3.8, -14), lz.elipse(17.7, 5.8, 0.7, 3.8, 14))
        brazos = np.maximum(lz.trazo([(9.5, 21), (12, 26), (17, 26)], 1.6), lz.trazo([(20.5, 21), (18, 25)], 1.6))
        forma = np.clip(cuerpo + cabeza + orejas + espigas + gavilla * 0, 0, 1)
        lz.sombrear(forma, PIEDRA, 2.5, LUZ, textura=lz.ruido(0.6, 3, semilla=1403), fuerza_tex=0.35)
        lz.sombrear(np.clip(gavilla + espigas * 0.0, 0, 1), PIEDRA[1:], 1.2, LUZ, textura=(lz.x % 1.2 < 0.4) * 1.0, fuerza_tex=0.4)
        lz.sombrear(brazos, PIEDRA[1:], 1, LUZ)
        lz.pintar(dentro_orejas, PIEDRA[1], 0.8)
        for ox in (13.2, 16.8):                                   # los ojos, cerrados
            lz.pintar(lz.trazo([(ox - 0.8, 13.6), (ox + 0.8, 13.6)], 0.32), PIEDRA[0])
        lz.pintar(lz.elipse(15, 15.6, 1.1, 0.7), PIEDRA[1])      # el hocico
        lz.pintar(lz.trazo([(15, 34), (15, 30)], 0.3), PIEDRA[1])
        _venas(lz, forma, [[(14, 18), (16, 24), (14, 30)], [(17, 8), (16.5, 12)]])
        todo = np.clip(forma + gavilla + brazos, 0, 1)
    elif k == 1:
        # un tejón sentado que sostiene en alto un farol apagado
        cuerpo = lz.elipse(13, 27.5, 8.5, 6.8)
        cabeza = lz.elipse(12, 18, 5.2, 4.4)
        hocico = lz.elipse(7.5, 19.8, 2.8, 1.9)
        oreja = lz.elipse(15.5, 14.2, 1.6, 1.3)
        patas = np.maximum(lz.elipse(8, 33, 2.6, 1.4), lz.elipse(16, 33.2, 2.6, 1.4))
        brazo = lz.trazo([(17, 24), (20, 18), (21, 12)], 1.6)
        farol = lz.poligono([(19, 4), (24, 4), (23.5, 11), (19.5, 11)])
        asa = lz.trazo([(20, 4), (21.5, 1.5), (23, 4)], 0.4)
        forma = np.clip(cuerpo + cabeza + hocico + oreja + patas, 0, 1)
        lz.sombrear(forma, PIEDRA, 2.5, LUZ, textura=lz.ruido(0.6, 3, semilla=1404), fuerza_tex=0.3)
        # las dos franjas oscuras de la cara del tejón y la lista clara del medio
        lz.pintar(lz.trazo([(9.5, 16.5), (14, 15)], 1.1) * cabeza, PIEDRA[1], 0.9)
        lz.pintar(lz.trazo([(9.5, 19.8), (14.5, 19.5)], 1.0) * cabeza, PIEDRA[1], 0.8)
        lz.pintar(lz.trazo([(8, 18.2), (15, 17.4)], 0.7) * cabeza, PIEDRA[5], 0.8)
        lz.pintar(lz.circulo(5.2, 19.7, 0.6), PIEDRA[0])                       # la nariz
        lz.sombrear(brazo, PIEDRA[1:], 1, LUZ)
        lz.sombrear(farol, PIEDRA[1:], 1, LUZ)
        lz.pintar(lz.trazo([(21.5, 5.5), (21.5, 9.5)], 0.9) * farol, PIEDRA[0])          # el cristal, oscuro
        lz.pintar(asa, PIEDRA[2])
        lz.pintar(lz.trazo([(10.2, 17.2), (11.6, 17.2)], 0.32), PIEDRA[0])      # el ojo, cerrado
        _venas(lz, forma, [[(15, 22), (12, 27), (14, 32)], [(11, 14.5), (12.5, 17)]])
        todo = np.clip(forma + brazo + farol, 0, 1)
    else:
        # una garza de pie con las alas abiertas, como si fuera a echar a volar y no lo hiciera nunca
        patas = np.maximum(lz.trazo([(14, 34), (14, 25)], 0.6), lz.trazo([(16, 34), (16, 25)], 0.6))
        cuerpo = lz.elipse(15, 21, 4.5, 5.5)
        cuello = lz.trazo([(15, 17), (13.5, 12), (15, 8)], 1.4, 1.1)
        cabeza = lz.elipse(15.5, 7, 2.3, 1.9)
        pico = lz.trazo([(17, 7), (21, 8)], 0.6, 0.2)
        ala_i = lz.poligono([(11, 18), (1, 9), (2, 15), (4, 18), (6, 21), (11, 23)])
        ala_d = lz.poligono([(19, 18), (29, 9), (28, 15), (26, 18), (24, 21), (19, 23)])
        forma = np.clip(cuerpo + cuello + cabeza + ala_i + ala_d, 0, 1)
        lz.sombrear(forma, PIEDRA, 2.2, LUZ, textura=lz.ruido(0.6, 3, semilla=1405), fuerza_tex=0.35)
        plumas = ((lz.x - lz.y * 0.6) % 2.2 < 0.4) * (ala_i + ala_d)
        lz.pintar(plumas, PIEDRA[2], 0.6)
        lz.sombrear(patas, PIEDRA[1:], 0.5, LUZ)
        lz.pintar(pico, PIEDRA[3])
        lz.pintar(lz.circulo(15.8, 6.6, 0.4), PIEDRA[0])
        _venas(lz, forma, [[(15, 18), (15.5, 23)], [(10, 17), (5, 12)], [(20, 17), (25, 12)]])
        todo = np.clip(forma + patas, 0, 1)
    _nieve_encima(lz, todo, 1.6, semilla=1410 + k)
    _escarcha(lz, todo, 0.35, semilla=1415 + k)
    return lz.sprite(contorno=0.6)


def arco_ruinas():
    W, H = 112, 88
    lz = Lienzo(W, H, s=4, semilla=1500)
    rng = np.random.default_rng(1501)
    # la niebla entre los pilares (el paso)
    # (la niebla entre los pilares la dibuja el juego, animada: un dibujo no puede tener bordes de humo)
    # los pilares, rotos a distinta altura
    for (x0, x1, arriba, sem) in ((14, 30, 14, 1503), (82, 98, 22, 1504)):
        pilar = lz.poligono([(x0, 87), (x0 + 1, arriba + 4), (x0 + 4, arriba), (x1 - 3, arriba + 3), (x1, arriba + 7), (x1 + 1, 87)])
        sillares = ((lz.y % 9 < 0.7) | (((lz.x + (lz.y // 9) * 4) % 8) < 0.6)) * 1.0
        lz.sombrear(pilar, CLARA, 3, LUZ, textura=1 - sillares * 0.6 + lz.ruido(0.8, 2, semilla=sem) * 0.3, fuerza_tex=0.4)
        _nieve_encima(lz, pilar, 2.0, semilla=sem + 10)
        _escarcha(lz, pilar, 0.4, semilla=sem + 20)
    # el arco (de un pilar al otro, roto en el medio derecho)
    arco = lz.trazo(lz.curva((22, 18), (40, -2), (72, -2), (88, 24), n=50), 7.0, 6.0)
    hueco = lz.poligono([(60, 0), (68, 0), (66, 12), (58, 10)])
    arco = np.clip(arco - hueco, 0, 1)
    lz.sombrear(arco, CLARA, 3, LUZ, textura=lz.ruido(0.8, 2, semilla=1505), fuerza_tex=0.35)
    # las nueve espirales de los ecos, talladas en el arco (la del medio, la del Silencio, plateada)
    for i in range(9):
        t = 0.12 + i * 0.095
        x = 22 + (88 - 22) * t
        y = 16 - np.sin(t * np.pi) * 13
        pts = [(x + np.cos(a) * a * 0.3, y + np.sin(a) * a * 0.28) for a in np.linspace(0.3, 9, 22)]
        lz.pintar(lz.trazo(pts, 0.35) * arco, CLARA[1] if i != 4 else "#a8b8d8")
    _nieve_encima(lz, arco, 2.0, semilla=1506)
    # raíces enormes del Primer Árbol que abrazan los pilares y se hunden en la nieve
    raices = np.zeros((lz.H, lz.W))
    for (pts, g) in (([(0, 84), (2, 58), (24, 52), (18, 22)], 4.5), ([(8, 87), (12, 72), (30, 74), (31, 58)], 2.8),
                     ([(112, 84), (110, 56), (86, 54), (94, 26)], 4.5), ([(104, 87), (100, 70), (82, 74), (81, 60)], 2.6),
                     ([(44, 88), (40, 80), (30, 84), (31, 72)], 1.8), ([(70, 88), (74, 82), (82, 86), (82, 76)], 1.6)):
        raices = np.maximum(raices, lz.trazo(lz.curva(pts[0], pts[1], pts[2], pts[3], n=50), g * 1.7, g * 0.7))
    lz.sombrear(raices, RAIZ_C, 2.5, LUZ, textura=lz.ruido(0.5, 2, semilla=1507), fuerza_tex=0.4)
    _nieve_encima(lz, raices, 1.4, semilla=1508)
    # vetas de Giza que suben por el pilar derecho
    _venas(lz, np.ones((lz.H, lz.W)), [[(90, 86), (88, 70), (91, 56), (89, 40)]])
    # nieve en el suelo, al pie
    suelo = lz.poligono([(0, 82), (30, 80), (56, 83), (82, 80), (112, 82), (112, 88), (0, 88)])
    lz.sombrear(suelo, NIEVE[2:], 2, LUZ)
    del rng
    return lz.sprite(contorno=0.4)


def main():
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(np.concatenate([pino(0), pino(1)], axis=1), "RGBA").save(os.path.join(SALIDA, "pino_nevado.png"))
    Image.fromarray(np.concatenate([roca(0), roca(1)], axis=1), "RGBA").save(os.path.join(SALIDA, "roca_nevada.png"))
    Image.fromarray(np.concatenate([brasero(False), brasero(True)], axis=1), "RGBA").save(os.path.join(SALIDA, "brasero.png"))
    Image.fromarray(np.concatenate([estatua(k) for k in range(3)], axis=1), "RGBA").save(os.path.join(SALIDA, "estatua.png"))
    Image.fromarray(arco_ruinas(), "RGBA").save(os.path.join(SALIDA, "arco_ruinas.png"))
    print("Sendero Olvidado pintado en", SALIDA)


if __name__ == "__main__":
    main()
