"""EL PASO DE LA ESCARCHA (Sigilia), pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_escarcha.py

Genera en arte/mundos/sigilia/paso/:
  estela.png   2 × 22×38 las ESTELAS RÚNICAS del paso: losas altas de piedra morada, viejas y gastadas, con renglones
               de letras talladas (los escribas marcaban el camino escribiendo en la piedra), nieve encima, escarcha
               lila y una runa dorada que todavía brilla un poco. Cobijan del viento.
  farol.png    2 × 18×34 los FAROLES RÚNICOS del paso: un poste de piedra morada con un fanal de cobre dorado y una
               runa de fuego tallada. 0 apagado (cristal empañado de escarcha, nieve encima) · 1 encendido (cristal
               ámbar y la runa encendida; la llama la dibuja el juego)
  ficha.png    2 × 12×12 una FICHA DEL ÍNDICE caída en la nieve: una tarjeta de pergamino con su pestaña morada y
               un renglón de tinta (el nombre de alguien). 1: un destello
  pagina.png   6 × 18×16 la PÁGINA SUELTA, el enemigo del paso: una hoja de pergamino escrita con Tinta Quieta, con
               dos manchas de tinta por ojos que brillan violeta (Giza). 0-3 aleteando (las esquinas se doblan) ·
               4 en picado (doblada en punta) · 5 golpeada (blanca)
  puerta.png   4 × 104×88 la PUERTA SELLADA de Maandiko, arriba del todo: un arco de piedra morada con runas doradas
               y dos hojas de madera, tapadas por un sello de TINTA QUIETA (tinta negra helada, brillante, con
               carámbanos y vetas violetas). 0 entera · 1 agrietada · 2 medio derretida · 3 abierta (charco de tinta)
Y el icono de la ficha en la mochila (el 28.º de arte/interfaz/objetos.png, índice 27).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "sigilia", "paso")
LUZ = (-0.6, -0.7, 0.5)
NIEVE = ["#4e4870", "#7e76a2", "#b0a9cd", "#c8c2de", "#e6e3f2", "#f6f5fb"]
PIEDRA_S = ["#1e1828", "#2e2640", "#423856", "#584c6c", "#706484", "#8c809c", "#aaa0b8"]   # la piedra morada de Sigilia
ORO = ["#6a4614", "#a07020", "#d4a034", "#f0cc60", "#fff0b0"]


def _nieve_encima(lz, forma, grosor=1.6, semilla=0):
    bajar = int(grosor * lz.s)
    encima = forma * (1 - np.roll(forma, bajar, axis=0))
    borde = np.clip(encima + (lz.ruido(0.8, 2, semilla=semilla) > 0.62) * np.roll(encima, int(lz.s), axis=0), 0, 1) * forma
    lz.sombrear(borde, NIEVE[2:], 0.8, LUZ, textura=lz.ruido(0.5, 2, semilla=semilla + 1), fuerza_tex=0.2)
    return borde


def estela(k):
    W, H = 22, 38
    lz = Lienzo(W, H, s=6, semilla=6100 + k)
    # la losa: alta, un poco inclinada, con la punta redondeada (0) o partida en diagonal (1)
    if k == 0:
        losa = np.maximum(lz.poligono([(4, 37), (4.5, 10), (17.5, 10), (18, 37)]), lz.elipse(11, 10.5, 6.6, 5))
    else:
        losa = lz.poligono([(3.5, 37), (4, 12), (9, 7), (17, 13), (18.5, 37)])
    lz.sombrear(losa, PIEDRA_S, 3.0, LUZ, textura=lz.ruido(2.5, 2, semilla=6101 + k), fuerza_tex=0.12)
    # el canto de la losa (grosor, a la derecha) más oscuro
    canto = losa * (lz.x > 16.2)
    lz.pintar(canto, PIEDRA_S[1], 0.6)
    # renglones de letras talladas: rayitas cortas en filas (unas más gastadas que otras)
    rng = np.random.default_rng(6102 + k)
    tallado = np.zeros((lz.H, lz.W))
    for fila in range(6):
        y = 16 + fila * 3.4
        x = 6.0
        while x < 15.0:
            largo = rng.uniform(0.8, 2.0)
            if rng.random() < 0.85:
                tallado = np.maximum(tallado, lz.trazo([(x, y), (x + largo, y + rng.uniform(-0.4, 0.4))], 0.5))
                if rng.random() < 0.4:
                    tallado = np.maximum(tallado, lz.trazo([(x + largo * 0.5, y - 1.0), (x + largo * 0.5, y + 1.0)], 0.42))
            x += largo + rng.uniform(0.5, 1.1)
    tallado = tallado * losa
    lz.pintar(tallado, PIEDRA_S[0], 1.0)
    lz.pintar(np.clip(np.roll(tallado, int(0.5 * lz.s), axis=0) - tallado, 0, 1) * losa, PIEDRA_S[5], 0.45)   # el filo de luz
    # la runa grande de arriba, dorada, que todavía brilla un poco
    cx, cy = 11, 12.5 if k == 0 else 14
    runa = np.maximum.reduce([lz.trazo([(cx, cy - 2.4), (cx, cy + 2.4)], 0.45),
                              lz.trazo([(cx - 2, cy - 1), (cx, cy + 0.6), (cx + 2, cy - 1)], 0.4),
                              lz.circulo(cx, cy - 2.8, 0.6)])
    lz.sumar_luz(lz.desenfocar(runa, 1.6) * losa, ORO[2], 0.5)
    lz.pintar(runa, ORO[3])
    lz.pintar(runa * (lz.y < cy), ORO[4], 0.6)
    # grietas y musgo seco de invierno abajo; nieve encima y amontonada al pie
    grieta = lz.trazo([(6, 33), (7.5, 29), (6.5, 26)] if k == 0 else [(15, 24), (13.5, 28), (14.5, 33)], 0.35) * losa
    lz.pintar(grieta, PIEDRA_S[0])
    _nieve_encima(lz, losa, 3.2, semilla=6105 + k)
    pie = lz.elipse(11, 36.5, 9, 2.2) * (lz.y < 38)
    lz.sombrear(pie, NIEVE[1:], 1.2, LUZ)
    lz.pintar((lz.ruido(0.35, 1, semilla=6108 + k) > 0.8) * losa * (lz.x < 12), NIEVE[3], 0.6)
    return lz.sprite(contorno=0.5)


def farol(encendido):
    W, H = 18, 34
    lz = Lienzo(W, H, s=6, semilla=6200 + encendido)
    # el poste: una columna de piedra morada, ancha abajo, con su basa y tallas
    poste = np.maximum.reduce([lz.poligono([(6.5, 33), (6.8, 14), (11.2, 14), (11.5, 33)]),
                               lz.poligono([(4.5, 33.5), (4.5, 30), (13.5, 30), (13.5, 33.5)])])
    lz.sombrear(poste, PIEDRA_S, 2.2, LUZ, textura=lz.ruido(2, 2, semilla=6201), fuerza_tex=0.12)
    runa = lz.trazo([(9, 18), (9, 25)], 0.35) + lz.trazo([(7.6, 20), (9, 21.6), (10.4, 20)], 0.32)
    runa = np.clip(runa, 0, 1) * poste
    if encendido:
        lz.sumar_luz(lz.desenfocar(runa, 1.2), ORO[2], 0.6)
        lz.pintar(runa, ORO[3])
    else:
        lz.pintar(runa, PIEDRA_S[0], 0.9)
    # el fanal: una jaula de cobre dorado con cristal y un tejadillo
    jaula = lz.poligono([(5, 13.5), (5.6, 6.5), (12.4, 6.5), (13, 13.5)])
    lz.sombrear(jaula, ORO[:4], 1.2, LUZ)
    cristal = lz.poligono([(6.4, 12.6), (6.8, 7.6), (11.2, 7.6), (11.6, 12.6)])
    if encendido:
        lz.pintar(cristal, "#fde27e")
        lz.sumar_luz(lz.desenfocar(cristal, 1.0), "#ffb040", 0.5)
    else:
        lz.sombrear(cristal, ["#4e4870", "#7e76a2", "#b0a9cd", "#dddaec"], 1.5, LUZ)
        lz.pintar((lz.ruido(0.3, 1, semilla=6203) > 0.7) * cristal, NIEVE[5], 0.7)    # escarcha en el cristal
    lz.pintar(lz.trazo([(9, 7.4), (9, 12.8)], 0.3) * jaula, ORO[0], 0.8)               # el barrote del medio
    tejado = lz.poligono([(3.8, 6.8), (9, 2.2), (14.2, 6.8)])
    lz.sombrear(tejado, ORO, 1.2, LUZ)
    lz.pintar(lz.circulo(9, 1.8, 0.8), ORO[3])
    _nieve_encima(lz, tejado, 1.4, semilla=6204)
    _nieve_encima(lz, poste * (lz.y > 29), 1.0, semilla=6205)
    return lz.sprite(contorno=0.5)


def ficha(destello):
    W, H = 12, 12
    lz = Lienzo(W, H, s=6, semilla=6300)
    tarjeta = lz.poligono([(1.5, 10.5), (2, 3.5), (10.5, 2.8), (10.5, 9.8)])
    lz.sombrear(tarjeta, ["#8a7454", "#c9b07e", "#e2cea0", "#fff3d8"], 1.5, LUZ)
    pestana = lz.poligono([(6.5, 3.2), (6.8, 1.2), (9.6, 1.0), (9.8, 3.0)])
    lz.sombrear(pestana, ["#2e1a44", "#5a3480", "#7a52a6", "#a07ac4"], 0.8, LUZ)
    lz.pintar(lz.trazo([(3, 6), (8.5, 5.5)], 0.35) * tarjeta, "#241e3c", 0.9)          # el nombre
    lz.pintar(lz.trazo([(3, 8), (7, 7.7)], 0.3) * tarjeta, "#5a5070", 0.7)
    if destello:
        lz.sumar_luz(lz.desenfocar(lz.circulo(9, 3, 1), 1.2), "#fff0b0", 0.9)
        lz.pintar(lz.trazo([(9, 1), (9, 5)], 0.25) + lz.trazo([(7, 3), (11, 3)], 0.25), "#fffbe8")
    return lz.sprite(contorno=0.6)


def icono_ficha():
    lz = Lienzo(16, 16, s=6, semilla=6301)
    tarjeta = lz.poligono([(2, 14), (2.5, 4.5), (14, 3.5), (14, 13)])
    lz.sombrear(tarjeta, ["#8a7454", "#c9b07e", "#e2cea0", "#fff3d8"], 2, LUZ)
    pestana = lz.poligono([(9, 4.2), (9.3, 1.4), (13.2, 1.1), (13.5, 3.8)])
    lz.sombrear(pestana, ["#2e1a44", "#5a3480", "#7a52a6", "#a07ac4"], 1, LUZ)
    lz.pintar(lz.trazo([(4, 7.5), (12, 7)], 0.45) * tarjeta, "#241e3c", 0.95)
    lz.pintar(lz.trazo([(4, 10), (10, 9.6)], 0.4) * tarjeta, "#5a5070", 0.8)
    lz.pintar(lz.circulo(4, 12, 0.8) * tarjeta, ORO[2])
    return lz.sprite(contorno=0.8)


PERGAMINO = ["#6a5440", "#a8906a", "#d8c49a", "#f0e2c0", "#fff6e0"]
TINTA = ["#06040c", "#120c1e", "#22183a", "#3a2a5a", "#5a4488", "#8a70c0"]


def pagina(k):
    W, H = 18, 16
    lz = Lienzo(W, H, s=6, semilla=6400 + k)
    if k == 4:
        # en picado: doblada en punta, como un avioncito
        hoja = lz.poligono([(1.5, 9), (16.5, 4.5), (9, 13.5)])
        lz.sombrear(hoja, PERGAMINO, 2, LUZ)
        lz.pintar(lz.trazo([(1.5, 9), (14, 6.5)], 0.35), PERGAMINO[0], 0.8)
        ojos = [(10.5, 7.6), (12.8, 7.0)]
    else:
        # aleteando: las esquinas suben y bajan
        a = [0.0, 1.6, 2.6, 1.2][k] if k < 4 else 0.0
        hoja = lz.poligono([(2, 3 + a), (9, 2.2), (16, 3 + (2.6 - a)), (15.5, 13 - a * 0.4), (9, 13.6), (2.5, 13 - (2.6 - a) * 0.4)])
        lz.sombrear(hoja, PERGAMINO, 2.4, LUZ, textura=lz.ruido(1.5, 2, semilla=6401), fuerza_tex=0.12)
        # la esquina doblada (abajo a la derecha) y su sombra
        doblez = lz.poligono([(15.5, 13 - a * 0.4), (12.5, 13.3), (15.2, 10.4)])
        lz.sombrear(doblez, PERGAMINO[1:], 0.8, LUZ)
        # renglones de tinta
        for fila in range(4):
            y = 5.2 + fila * 2.0
            lz.pintar(lz.trazo([(4, y + a * 0.15), (13.5 - (fila % 2) * 2, y + a * 0.1)], 0.3) * hoja, TINTA[2], 0.75)
        ojos = [(6.6, 7.4 + a * 0.2), (10.8, 7.0 + a * 0.15)]
    # los ojos: dos manchas de tinta con la chispa violeta de Giza
    for (ox, oy) in ojos:
        mancha = lz.elipse(ox, oy, 1.5, 1.2)
        lz.pintar(mancha, TINTA[0])
        lz.sumar_luz(lz.desenfocar(lz.circulo(ox + 0.3, oy - 0.1, 0.5), 0.6), "#b070ff", 0.9)
    lz.pintar(lz.trazo([(ojos[0][0] - 1.4, ojos[0][1] - 1.8), (ojos[0][0] + 1.2, ojos[0][1] - 1.2)], 0.3), TINTA[0])   # el ceño
    lz.pintar(lz.trazo([(ojos[1][0] + 1.4, ojos[1][1] - 1.8), (ojos[1][0] - 1.2, ojos[1][1] - 1.2)], 0.3), TINTA[0])
    if k == 5:
        lz.pintar(hoja, "#ffffff", 0.75)
    return lz.sprite(contorno=0.6)


def puerta(estado):
    W, H = 104, 88
    lz = Lienzo(W, H, s=4, semilla=6500 + estado)
    cx = 52
    # el arco de piedra morada: dos pilares y la bóveda, con dovelas
    arco_fuera = np.maximum(lz.poligono([(10, 88), (10, 34), (94, 34), (94, 88)]), lz.elipse(cx, 34, 42, 30))
    hueco = np.maximum(lz.poligono([(26, 88), (26, 40), (78, 40), (78, 88)]), lz.elipse(cx, 40, 26, 22))
    piedra = np.clip(arco_fuera - hueco, 0, 1)
    juntas = ((lz.y % 8) < 0.7) * 1.0 + (((lz.x + (lz.y // 8) * 7) % 14) < 0.7) * 1.0
    lz.sombrear(piedra, PIEDRA_S, 6, LUZ, textura=1 - juntas * 0.6 + lz.ruido(2, 2, semilla=6501) * 0.2, fuerza_tex=0.25)
    # las runas doradas del arco y la clave con la pluma del Archivo
    for k_ in range(7):
        ang = np.pi * (0.12 + 0.76 * k_ / 6)
        rx, ry = cx - np.cos(ang) * 34, 38 - np.sin(ang) * 24
        r = lz.trazo([(rx, ry - 2), (rx, ry + 2)], 0.5) + lz.trazo([(rx - 1.5, ry - 0.5), (rx + 1.5, ry - 0.5)], 0.45)
        lz.sumar_luz(lz.desenfocar(np.clip(r, 0, 1), 1.2), ORO[2], 0.35 if estado < 3 else 0.6)
        lz.pintar(np.clip(r, 0, 1), ORO[3])
    clave = lz.poligono([(cx - 6, 6), (cx + 6, 6), (cx + 4.5, 16), (cx - 4.5, 16)])
    lz.sombrear(clave, ORO, 3, LUZ)
    pluma = lz.trazo(lz.curva((cx - 2.5, 14), (cx, 10), (cx + 2.5, 7.5), n=12), 1.2, 0.3)
    lz.pintar(pluma, PIEDRA_S[1])
    # el tejadillo de nieve sobre el arco y los pies
    _nieve_encima(lz, arco_fuera, 3.0, semilla=6502)
    # el hueco: las dos hojas de madera (cerradas o abiertas, con luz cálida dentro)
    madera = ["#1e140c", "#33241a", "#4a3626", "#634a34", "#7e6146"]
    if estado < 3:
        hojas = hueco
        tablas = ((lz.x % 6) < 0.8) * 1.0
        lz.sombrear(hojas, madera, 6, LUZ, textura=1 - tablas * 0.6, fuerza_tex=0.3)
        lz.pintar(hojas * (np.abs(lz.x - cx) < 0.8), madera[0])
        for yb in (52, 74):
            lz.pintar(hojas * (np.abs(lz.y - yb) < 1.2), "#2a2a30", 0.9)          # los herrajes
    else:
        dentro = lz.gradiente(["#f9d78a", "#e0a050", "#8a5a30"], desde=40, hasta=88)
        lz.pintar(hueco, dentro)
        lz.pintar(hueco * (lz.y > 70), "#c8a070", 0.4)
        for lado in (-1, 1):                                            # las hojas, abiertas hacia dentro
            hoja = lz.poligono([(cx + lado * 26, 88), (cx + lado * 26, 44), (cx + lado * 18, 48), (cx + lado * 18, 86)])
            lz.sombrear(hoja, madera, 3, LUZ)
    # la TINTA QUIETA: un sello negro, brillante y helado sobre las hojas (cada vez menos)
    if estado < 3:
        cuanto = [1.0, 0.82, 0.5][estado]
        alto_t = 40 + (1 - cuanto) * 40
        ruido_b = lz.ruido(5, 2, semilla=6503)
        sello = hueco * (lz.y > alto_t + (ruido_b - 0.5) * 10) if estado else hueco
        if estado == 0:
            sello = np.maximum(sello, lz.elipse(cx, 58, 34, 36) * (lz.y > 22))
        lz.sombrear(sello, TINTA[:5], 5, LUZ, textura=lz.ruido(8, 2, semilla=6504), fuerza_tex=0.1)
        # el brillo del hielo: reflejos largos y lisos (como charol) arriba a la izquierda, y alguna chispa
        reflejo = np.zeros((lz.H, lz.W))
        for (x0, y0, x1, y1) in ((34, 50, 44, 44), (32, 62, 38, 58), (60, 48, 66, 46)):
            reflejo = np.maximum(reflejo, lz.trazo([(x0, y0), (x1, y1)], 1.4, 0.4))
        lz.pintar(reflejo * sello, "#b8a8e8", 0.7)
        lz.pintar(lz.trazo([(35, 49.5), (41, 46)], 0.5) * sello, "#f0e8ff", 0.9)

        vetas = np.zeros((lz.H, lz.W))
        for pts in ([(30, 70), (38, 64), (42, 68), (50, 60)], [(56, 78), (62, 70), (70, 72), (74, 62)], [(46, 50), (52, 56), (58, 52)]):
            vetas = np.maximum(vetas, lz.trazo(pts, 0.5))
        lz.sumar_luz(lz.desenfocar(vetas * sello, 1.0), "#7a2fa0", 0.6)
        lz.pintar(vetas * sello, "#c27ce6", 0.8)
        # carámbanos de tinta que cuelgan del borde de arriba
        borde = np.clip(sello - np.roll(sello, int(1.5 * lz.s), axis=0), 0, 1)
        for k_ in range(12):
            x0 = 24 + k_ * 5 + (k_ % 3)
            largo = 3 + (k_ * 7 % 5) * (1.2 if estado == 0 else 0.6)
            ys = np.where(borde[:, int(x0 * lz.s)] > 0.5)[0]
            if len(ys):
                y0 = ys[0] / lz.s
                caramb = lz.poligono([(x0 - 1.2, y0 + 1), (x0 + 1.2, y0 + 1), (x0, y0 + largo)])
                lz.sombrear(caramb, TINTA, 1, LUZ)
        if estado >= 1:                                                 # grietas que brillan de fuego
            gr = lz.trazo([(40, 60), (46, 66), (44, 74)], 0.6) + lz.trazo([(62, 56), (58, 64), (64, 72)], 0.6)
            lz.sumar_luz(lz.desenfocar(np.clip(gr, 0, 1) * sello, 1.0), "#ff8a3a", 0.8)
    # el charco de tinta al pie (más grande cuanto más derretida)
    charco = lz.elipse(cx, 86, [26, 32, 40, 44][estado], [3, 4, 5, 5][estado]) * (lz.y < 88)
    lz.sombrear(charco, TINTA, 2, LUZ)
    lz.pintar(charco * (lz.ruido(1, 2, semilla=6507) > 0.7), TINTA[4], 0.4)
    return lz.sprite(contorno=0.5)


def main():
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(np.concatenate([estela(0), estela(1)], axis=1), "RGBA").save(os.path.join(SALIDA, "estela.png"))
    Image.fromarray(np.concatenate([farol(0), farol(1)], axis=1), "RGBA").save(os.path.join(SALIDA, "farol.png"))
    Image.fromarray(np.concatenate([ficha(0), ficha(1)], axis=1), "RGBA").save(os.path.join(SALIDA, "ficha.png"))
    Image.fromarray(np.concatenate([pagina(k) for k in range(6)], axis=1), "RGBA").save(os.path.join(SALIDA, "pagina.png"))
    Image.fromarray(np.concatenate([puerta(k) for k in range(4)], axis=1), "RGBA").save(os.path.join(SALIDA, "puerta.png"))
    # el icono de la ficha en la mochila: el 28.º de objetos.png (índice 27)
    ruta = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    n = max(28, viejos.width // 16)
    iconos = Image.new("RGBA", (16 * n, 16), (0, 0, 0, 0))
    iconos.alpha_composite(viejos.crop((0, 0, min(viejos.width, 16 * 27), 16)), (0, 0))
    if viejos.width > 16 * 28:
        iconos.alpha_composite(viejos.crop((16 * 28, 0, viejos.width, 16)), (16 * 28, 0))
    iconos.alpha_composite(Image.fromarray(icono_ficha(), "RGBA"), (16 * 27, 0))
    iconos.save(ruta)
    print("Paso de la Escarcha pintado en", SALIDA)


if __name__ == "__main__":
    main()
