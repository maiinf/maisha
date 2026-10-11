"""
EL JABALÍ DE HIERRO (enemigo «cazador» de Raíz), píxel a píxel.

Uso:  python3 herramientas/dibujar_jabali.py
Genera arte/zonas/raiz/jabali.png: 3 filas (lado · abajo · arriba) × 5 fotogramas de 28×22:
  0-1 anda   2 se prepara (baja la cabeza y escarba)   3-4 embiste (corre)
El de «lado» mira a la derecha (el juego lo voltea). Giza le ha cubierto el lomo de placas de hierro
oxidado y le brillan los ojos violeta. El blanco al recibir daño y las estrellas del aturdimiento
los pone el juego.
"""
import math
import os

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 28, 22

PELO = ["2a1d17", "43302a", "5e463a", "7a5c49", "93725a"]
HIERRO = ["23252a", "3a3e44", "565c62", "7a8086", "a3a8ab"]
OXIDO = ["5a2e18", "8a4522", "b0602e"]
COLMILLO = ["b8ac90", "e8dcc0", "fff8e8"]
OJO = ["7a2fa0", "c27ce6", "f1d8fb"]
HOCICO = ["6e4a40", "9a6a5c"]
CONTORNO = "120c0a"


def c(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


class Dibujo:
    def __init__(self):
        self.img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.px = self.img.load()

    def p(self, x, y, col):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < W and 0 <= y < H:
            self.px[x, y] = c(col)

    def elipse(self, cx, cy, rx, ry, rampa, luz=(-0.6, -0.8), sobre=True):
        for y in range(H):
            for x in range(W):
                nx, ny = (x - cx) / rx, (y - cy) / ry
                d = nx * nx + ny * ny
                if d <= 1.0 and (sobre or self.px[x, y][3] == 0):
                    l = -nx * luz[0] * -1 * -1 + 0  # (se calcula abajo)
                    l = (-nx * 0.6 - ny * 0.8) * 0.8 + (1 - d) * 0.35
                    i = int(round((l * 0.5 + 0.5) * (len(rampa) - 1)))
                    self.px[x, y] = c(rampa[max(0, min(len(rampa) - 1, i))])

    def rect(self, x0, y0, x1, y1, col):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.p(x, y, col)

    def contorno(self):
        px = self.px
        puntos = []
        for y in range(H):
            for x in range(W):
                if px[x, y][3] == 0:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < W and 0 <= ny < H and px[nx, ny][3]:
                            puntos.append((x, y))
                            break
        for q in puntos:
            px[q] = c(CONTORNO)
        return self.img


def placas(d, xs, y, r=2.6):
    """Placas de hierro solapadas por el lomo, con un filo de óxido."""
    for i, x in enumerate(xs):
        d.elipse(x, y + (i % 2) * 0.4, r, r * 0.8, HIERRO)
        d.p(x + r * 0.6, y + r * 0.5, OXIDO[1])
        d.p(x - r * 0.4, y - r * 0.5, HIERRO[4])


def lado(fot):
    d = Dibujo()
    corre = fot in (3, 4)
    prep = fot == 2
    paso = [0, 1, 0, 0, 1][fot]
    baja = 2 if prep else (1 if corre else 0)
    cy = 11 + (1 if prep else 0) - (1 if fot == 3 else 0)
    # patas cortas y finas con pezuña oscura; al correr se abren adelante y atrás
    for (x, atras) in ((6, True), (9, True), (16, False), (19, False)):
        if corre:
            dx = 2 if ((x < 13) == (paso == 0)) else -2
        elif fot < 2:
            dx = 1 if ((x < 13) == (paso == 0)) else 0
        else:
            dx = 0
        top = cy + 3
        for y in range(top, 19):
            t = (y - top) / max(1, 19 - top)
            xx = x + dx * t
            d.p(xx, y, PELO[1] if atras else PELO[2])
            d.p(xx + 1, y, PELO[0] if atras else PELO[1])
        d.p(x + dx, 19, "1a1210")
        d.p(x + dx + 1, 19, "1a1210")
    # cuerpo: grupa pequeña detrás y hombros grandes delante
    d.elipse(8.5, cy + 0.5, 5.2, 4.4, PELO)
    d.elipse(14.5, cy - 0.5, 6.4, 5.4, PELO)
    # tripa en sombra
    for x in range(5, 20):
        d.p(x, cy + 4 - (1 if x < 8 or x > 17 else 0), PELO[0])
    # placas de hierro por el lomo y crin de cerdas
    placas(d, [7.0, 10.0, 13.0, 16.0], cy - 4.0, 2.5)
    for x in range(17, 21):
        d.p(x, cy - 5 + (x % 2), PELO[4])
        d.p(x, cy - 4, PELO[3])
    # rabo
    d.p(3, cy - 1, PELO[2])
    d.p(2, cy - 2, PELO[3])
    # cabeza en cuña hacia el hocico, más baja al embestir
    hy = cy + 0.5 + baja
    for y in range(int(hy) - 4, int(hy) + 4):
        for x in range(18, 26):
            u = (x - 18) / 7.0
            arriba = hy - 4 + u * 2.6
            abajo = hy + 3 - u * 0.6
            if arriba <= y <= abajo:
                l = 0.35 - (y - arriba) / max(1, abajo - arriba) * 0.9 + (0.2 if u < 0.3 else 0)
                i_ = int(round((l * 0.5 + 0.5) * 4))
                d.p(x, y, PELO[max(0, min(4, i_))])
    # oreja
    d.p(19, hy - 5, PELO[3])
    d.p(20, hy - 5, PELO[2])
    d.p(19, hy - 6, PELO[2])
    # hocico (disco) y colmillo curvo
    d.p(26, hy + 0, HOCICO[1])
    d.p(26, hy + 1, HOCICO[0])
    d.p(26, hy + 2, HOCICO[0])
    d.p(24, hy + 3, COLMILLO[0])
    d.p(25, hy + 2, COLMILLO[1])
    d.p(25, hy + 1, COLMILLO[2])
    # ojo de Giza (brilla más al embestir)
    d.p(22, hy - 2, OJO[2] if corre or prep else OJO[1])
    d.p(21, hy - 2, OJO[0])
    if prep:
        for (x, y) in ((3, 19), (1, 18), (4, 17), (2, 16)):
            d.p(x, y, "684937")
    return d.contorno()


def abajo(fot):
    """De frente (va hacia abajo)."""
    d = Dibujo()
    corre = fot in (3, 4)
    prep = fot == 2
    paso = [0, 1, 0, 0, 1][fot]
    cy = 10 + (1 if prep else 0)
    # patas
    for (x, delante) in ((8, True), (18, True), (10, False), (16, False)):
        sube = (1 if (x < 13) == (paso == 0) else 0) if (corre or fot < 2) else 0
        d.rect(x, cy + 5 - sube, x + 1, 19 - sube, PELO[2] if delante else PELO[1])
    # cuerpo (se ve el pecho) y placas en los hombros, más anchas que la cabeza
    d.elipse(13.5, cy + 1, 7.5, 5.5, PELO)
    placas(d, [7.5, 11.0, 16.0, 19.5], cy - 3.0, 2.5)
    # cabeza en cuña: ancha arriba, estrecha en el hocico
    hy = cy + 4 + (2 if prep else 1 if corre else 0)
    for y in range(int(hy) - 4, int(hy) + 5):
        t = (y - (hy - 4)) / 8.0
        media = 5.2 - t * 2.6
        for x in range(W):
            if abs(x - 13.5) <= media:
                l = 0.45 - t * 0.9 - abs(x - 13.5) / 6.0 * 0.3
                i_ = int(round((l * 0.5 + 0.5) * 4))
                d.p(x, y, PELO[max(0, min(4, i_))])
    for (x, y) in ((9, hy - 4), (18, hy - 4)):
        d.p(x, y, PELO[3])
        d.p(x, y - 1, PELO[2])
    d.rect(12, hy + 2, 15, hy + 4, HOCICO[0])
    d.p(13, hy + 3, "2a1d17")
    d.p(14, hy + 3, "2a1d17")
    for x, dx in ((10, -1), (17, 1)):
        d.p(x, hy + 3, COLMILLO[1])
        d.p(x + dx, hy + 2, COLMILLO[2])
    d.p(11, hy - 1, OJO[1])
    d.p(16, hy - 1, OJO[1])
    if corre or prep:
        d.p(11, hy - 2, OJO[2])
        d.p(16, hy - 2, OJO[2])
    return d.contorno()


def arriba(fot):
    """De espaldas (va hacia arriba): se ve el lomo de hierro y el rabo."""
    d = Dibujo()
    corre = fot in (3, 4)
    paso = [0, 1, 0, 0, 1][fot]
    cy = 11
    for (x, delante) in ((8, False), (18, False), (10, True), (16, True)):
        sube = (1 if (x < 13) == (paso == 0) else 0) if (corre or fot < 2) else 0
        d.rect(x, cy + 4 - sube, x + 1, 19 - sube, PELO[1])
    d.elipse(13.5, cy, 7.5, 6.5, PELO)
    # cabeza asomando por delante (arriba)
    d.elipse(13.5, cy - 6, 4, 3, PELO)
    d.p(10, cy - 9, PELO[3])
    d.p(17, cy - 9, PELO[3])
    # lomo cubierto de placas en dos filas
    placas(d, [9.5, 13.5, 17.5], cy - 2, 2.6)
    placas(d, [11.5, 15.5], cy + 1.5, 2.4)
    # rabo
    d.p(13, cy + 6, PELO[2])
    d.p(14, cy + 7, PELO[2])
    return d.contorno()


def main():
    hoja = Image.new("RGBA", (W * 5, H * 3), (0, 0, 0, 0))
    for fila, fn in enumerate((lado, abajo, arriba)):
        for f in range(5):
            hoja.alpha_composite(fn(f), (f * W, fila * H))
    ruta = os.path.join(RAIZ, "arte", "zonas", "raiz", "jabali.png")
    hoja.save(ruta)
    print("guardado:", ruta, hoja.size)


if __name__ == "__main__":
    main()
