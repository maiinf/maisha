"""EL PASO DE LA ESCARCHA (Sigilia), pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_escarcha.py

Genera en arte/mundos/sigilia/paso/:
  estela.png   2 × 22×38 las ESTELAS RÚNICAS del paso: losas altas de piedra morada, viejas y gastadas, con renglones
               de letras talladas (los escribas marcaban el camino escribiendo en la piedra), nieve encima, escarcha
               lila y una runa dorada que todavía brilla un poco. Cobijan del viento.
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


def main():
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)
    Image.fromarray(np.concatenate([estela(0), estela(1)], axis=1), "RGBA").save(os.path.join(SALIDA, "estela.png"))
    print("Paso de la Escarcha pintado en", SALIDA)


if __name__ == "__main__":
    main()
