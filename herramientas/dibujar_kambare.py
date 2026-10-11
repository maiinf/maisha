"""
KAMBARE, EL SILURO DE CIENO: el minijefe del Lago Espejo (paleta oficial de Raíz).

Uso:  python3 herramientas/dibujar_kambare.py
Genera arte/zonas/raiz/kambare.png: 7 fotogramas de 104×60 (se dibuja en 80×46 y se escala ×1,3), mirando a la
derecha (el juego lo voltea):
  0 asoma del cieno (solo la cabeza, los bigotes y la aleta; abajo, plano: el barro lo tapa)
  1 salta (el cuerpo arqueado, la cola arriba)         2-3 varado en la orilla, coleteando
  4 escupe cieno (la cabeza alzada y la boca muy abierta)   5 aturdido (de lado, ojo en espiral)
  6 libre de Giza (limpio: pardo dorado, con pecas, contento)
Un pez gato enorme de barro y óxido, con placas de hierro, grietas de luz violeta y bigotes como cadenas.
"""
import math
import os

import dibujar_criaturas as dc
from dibujar_criaturas import MAT, tira
from dibujar_konokono import HojaE as _HojaE
import dibujar_konokono as dk

MAT["cieno"] = ["Tierra 1", "Tierra 2", "Tierra 3", "Tierra 4"]
MAT["oxido"] = ["Madera 1", "Madera 2", "Flor ambar 1", "Flor ambar 3"]
MAT["vientre"] = ["Tierra 2", "Tierra 4", "Pergamino 1", "Pergamino 2"]
MAT["dorado"] = ["Madera 2", "Madera 4", "Flor ambar 2", "Flor ambar 4"]
MAT["vientre_l"] = ["Madera 3", "Flor ambar 3", "Pergamino 2", "Pergamino 3"]

W, H = 80, 46
SUELO = 44


class HojaK(_HojaE):
    pass


def _perfil(cx, cy, ang, largo):
    """Los puntos de arriba y de abajo de la silueta: la cabeza ancha y plana delante (en cx) y el cuerpo, grueso,
    que se afina hacia la cola. ang: cuánto se arquea (positivo: la cola sube)."""
    arriba, abajo, centro = [], [], []
    for k in range(17):
        t = k / 16
        x = cx + 16 - t * 62 * largo
        y = cy - math.sin(t * math.pi * 0.85) * ang * 6 - t * t * ang * 9
        # media altura: la cabeza alta y chata, el lomo, y la cola fina
        alto = 9.5 * (1 - t) ** 0.55 + 1.6
        if t < 0.12:
            alto *= 0.75 + t * 2.0          # el morro, chato
        arriba.append((x, y - alto * 1.05))
        abajo.append((x, y + alto * 0.8))
        centro.append((x, y))
    return arriba, abajo, centro


def cuerpo_pez(h, f, cx, cy, ang=0.0, largo=1.0, libre=False, boca=0.0, ojo="giza", mira_arriba=0.0):
    """Kambare entero, de perfil: silueta, vientre, aletas, cola, placas de óxido, ojo, boca y bigotes."""
    piel = "dorado" if libre else "cieno"
    vientre = "vientre_l" if libre else "vientre"
    arriba, abajo, centro = _perfil(cx, cy - mira_arriba * 0.5, ang, largo)
    # la cola, en abanico (debajo del cuerpo)
    xc, yc = centro[-1]
    cola = h.poligono([(xc + 4, yc - 2), (xc - 7, yc - 9 - ang * 3), (xc - 4, yc), (xc - 7, yc + 8 - ang * 2), (xc + 4, yc + 2)])
    h.forma(cola, piel, minimo=1)
    # la aleta de arriba, redondeada, pegada al lomo
    xa, ya = arriba[5]
    aleta = h.poligono([(xa + 5, ya + 1), (xa + 2, ya - 6 - ang), (xa - 3, ya - 7 - ang), (xa - 6, ya + 1)])
    h.forma(aleta, piel, minimo=1)
    # la silueta del cuerpo y la cabeza, de una pieza
    m = h.poligono(arriba + abajo[::-1])
    h.forma(m, piel, esfera=(cx - 6, cy - 6, 30, 11))
    # el vientre claro
    vientre_m = h.poligono([(x, y - (y - c[1]) * 0.1) for (x, y), c in zip(abajo, centro)][::-1] +
                           [(c[0], c[1] + (b[1] - c[1]) * 0.35) for c, b in zip(centro, abajo)])
    h.forma(vientre_m, vientre, minimo=2)
    # la aleta del pecho
    xp, yp = abajo[3]
    h.forma(h.poligono([(xp + 3, yp - 3), (xp - 7, yp + 4), (xp - 4, yp - 3)]), piel, minimo=1)
    if not libre:
        # placas de hierro oxidado en el lomo y grietas de luz violeta de Giza
        for k in (4, 7, 10):
            px, py = arriba[k]
            h.forma(h.elipse(px, py + 2.5, 3.6 - k * 0.15, 2.3), "oxido", esfera=(px - 1, py + 1.5, 4, 2.5))
            h.px(px, py + 2.5, "piedra", 3)
        h.grieta([centro[3], centro[5], (centro[6][0], centro[6][1] - 2)], ancha=True)
        h.grieta([centro[9], centro[11]])
        for k in (3, 7, 11):                       # gotas de barro que cuelgan del vientre
            px, py = abajo[k]
            h.px(px, py + 1, "cieno", 1)
    else:
        for k in (4, 6, 8, 10, 12):                # pecas
            px, py = centro[k]
            h.px(px, py - 3, "dorado", 3)
            h.px(px + 2, py - 1, "dorado", 3)
    # la boca: una raja ancha en el morro, o muy abierta
    mx, my = centro[0][0] - 1, centro[0][1] + 2
    if boca > 0.2:
        h.forma(h.elipse(mx, my, 3 + boca * 2.5, 1.5 + boca * 3.5), "sombra", plano=0)
        h.forma(h.elipse(mx - 1, my + boca * 2.5, 2 + boca * 1.5, 1.0), "vientre", plano=2)
    else:
        h.linea([(mx - 9, my + 1), (mx + 1, my)], "sombra", 0)
    # el ojo, pequeño y arriba
    ox, oy = centro[2][0] + 2, arriba[2][1] + 4
    if ojo == "espiral":
        for (dx, dy) in ((0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)):
            h.px(ox + dx, oy + dy, "blanco", 2 if (dx + dy) % 2 else 1)
    elif ojo == "libre":
        h.forma(h.elipse(ox, oy, 2.0, 2.0), "blanco", plano=2)
        h.px(ox + 0.5, oy, "sombra", 0)
    else:
        h.forma(h.elipse(ox, oy, 2.0, 1.6), "giza", plano=3)
        h.px(ox + 0.6, oy, "giza", 2)
    # los bigotes, largos: cadenas de eslabones (con Giza) o bigotes finos (libre)
    for (dx, dy, ex, ey) in ((0, 1, 14, 9), (-2, 3, 8, 15), (0, -1, 15, -5), (-6, 4, -3, 14)):
        sx, sy = mx + dx, my + dy
        pts = [(sx + ex * t, sy + ey * t + math.sin(t * 3) * 1.5) for t in [k / 8 for k in range(9)]]
        if libre:
            h.linea(pts, "cieno", 1)
        else:
            for k, (x, y) in enumerate(pts):
                h.px(x, y, "piedra", 3 if k % 2 == 0 else 1)
                if k % 2 == 0:
                    h.px(x, y + 1, "piedra", 2)


def _borrar_bajo(h, y):
    """Borra todo lo que queda por debajo de la línea y (lo tapa el cieno)."""
    fila = int(round(y * dk.E))
    h.mat[fila:, :] = ""
    h.tono[fila:, :] = 0


def fotograma(f):
    h = HojaK(round(W * dk.E), round(H * dk.E))
    if f == 0:
        # asoma del cieno: el barro lo corta por abajo (solo se ven la cabeza, el lomo y la aleta)
        cuerpo_pez(h, f, 60, 38, ang=0.0)
        _borrar_bajo(h, 37)
        for x in range(10, W - 2, 3):
            h.px(x, 37 + (x % 2), "cieno", 2)
    elif f == 1:
        cuerpo_pez(h, f, 62, 27, ang=1.4, boca=0.5)
    elif f in (2, 3):
        cuerpo_pez(h, f, 60, SUELO - 10, ang=0.9 if f == 2 else -0.6, boca=0.3 if f == 2 else 0.0)
    elif f == 4:
        cuerpo_pez(h, f, 60, SUELO - 12, ang=-0.4, boca=1.0, mira_arriba=4)
    elif f == 5:
        cuerpo_pez(h, f, 60, SUELO - 9, ang=0.2, ojo="espiral")
    else:
        cuerpo_pez(h, f, 60, SUELO - 11, ang=0.5, libre=True, ojo="libre")
    return h.imagen()


def main():
    if "pezuna" not in MAT:
        MAT["pezuna"] = ["Extremos 1", "Interfaz 1", "Piedra 1", "Piedra 2"]
    hoja = tira([fotograma(f) for f in range(7)])
    ruta = os.path.join(dc.RAIZ, "arte", "zonas", "raiz", "kambare.png")
    hoja.save(ruta)
    print("guardado:", ruta, hoja.size)


if __name__ == "__main__":
    main()
