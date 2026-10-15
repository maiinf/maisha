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


def main():
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(np.concatenate([estela(0), estela(1)], axis=1), "RGBA").save(os.path.join(SALIDA, "estela.png"))
    Image.fromarray(np.concatenate([farol(0), farol(1)], axis=1), "RGBA").save(os.path.join(SALIDA, "farol.png"))
    Image.fromarray(np.concatenate([ficha(0), ficha(1)], axis=1), "RGBA").save(os.path.join(SALIDA, "ficha.png"))
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
