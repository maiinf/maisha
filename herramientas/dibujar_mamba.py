"""MAMBA, EL COCODRILO DE HERRUMBRE: el jefe de la dársena del Embarcadero Junco (con el pintor de las cinemáticas).

    python3 herramientas/dibujar_mamba.py

Genera arte/zonas/raiz/mamba.png: 7 fotogramas de 112×52, mirando a la derecha (el juego lo voltea), visto un poco
desde arriba (como todo el juego):
  0 flota (medio hundido: solo el lomo de placas, los ojos y el morro; abajo, el agua lo tapa)
  1 embiste (la boca muy abierta, las patas corriendo, la cola recta)
  2-3 atascado (la cabeza baja, los dientes clavados delante; el cuerpo tira hacia atrás, la cola se agita)
  4 coletazo (el cuerpo doblado en C, la cola barriendo)
  5 aturdido (de lado, la boca entreabierta, el ojo en espiral)
  6 libre de Giza (limpio: verde oliva y bronce, con el vientre claro y una sonrisa de cocodrilo)
Un cocodrilo viejo y enorme cubierto de placas de hierro oxidado, con grietas de luz violeta de Giza entre ellas.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, RAIZ  # noqa: E402
from pintar_pasarelas import tira, CONTORNO, GIZA  # noqa: E402

LUZ = (-0.6, -0.7, 0.5)
OXIDO = ["#24100a", "#3a1a0e", "#5e2c14", "#86401c", "#a85a2a", "#c87a40", "#e09a5a"]
PIEL_G = ["#1a1c16", "#2a2c22", "#3c3e30", "#525444", "#6a6c58"]           # la piel gris entre las placas
VIENTRE = ["#4a3e2c", "#6e5e44", "#948062", "#b8a482"]
OLIVA = ["#18241a", "#26381e", "#3a5228", "#526c34", "#6e8a44", "#94a85a"]
BRONCE = ["#3a2a12", "#5e4420", "#86642e", "#b08a44", "#d4b066"]
AGUA = ["#1c3535", "#285050", "#346161", "#4c8d8d", "#6db0b0", "#9fd0d0"]
W, H = 112, 52


def _columna(lz, pts, gruesos):
    """Un cuerpo largo como una sucesión de óvalos a lo largo de unos puntos (de la cola al morro)."""
    m = np.zeros((lz.H, lz.W))
    for (x, y), g in zip(pts, gruesos):
        m = np.maximum(m, lz.elipse(x, y, g * 1.25, g * 0.85))
    return m


def _espina(x0, y0, x1, y1, curva, n=18):
    pts = []
    for k in range(n):
        t = k / (n - 1)
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t + math.sin(t * math.pi) * curva
        pts.append((x, y))
    return pts


def cocodrilo(f):
    lz = Lienzo(W, H, s=6, semilla=401 + f)
    libre = f == 6
    piel = OLIVA if libre else PIEL_G
    placas_c = BRONCE if libre else OXIDO
    suelo = 46
    # la postura: la columna, de la cola (izquierda) al cuello (derecha)
    if f == 0:
        espina = _espina(8, 40, 80, 39, 0)
    elif f == 1:
        espina = _espina(4, 34, 80, 32, -2)
    elif f in (2, 3):
        cola = 4 if f == 2 else -4
        espina = [(x, y + (cola * (1 - (x - 10) / 70) if x < 80 else 0)) for (x, y) in _espina(10, 34, 80, 34, 0)]
    elif f == 4:
        espina = _espina(30, 16, 82, 34, -10)
        espina = [(30 + (x - 30) * 0.9, y + (16 * (1 - (x - 30) / 52) ** 2 if x < 60 else 0)) for (x, y) in espina]
    elif f == 5:
        espina = _espina(10, 38, 82, 37, 1)
    else:
        espina = _espina(8, 36, 80, 35, -1)
    gruesos = [1.6 + 9.5 * math.sin(min(1.0, k / 11) * math.pi / 2) ** 1.3 for k in range(len(espina))]
    if f != 0:
        lz.pintar(lz.desenfocar(lz.elipse(48, suelo, 44, 3.4), 0.8), "#0e0c0a", 0.5)
    # las patas (detrás y delante), cortas y con garras
    if f not in (0,):
        for (k, dx) in ((5, -1), (13, 1)):
            x, y = espina[k]
            paso = 2.5 if (f == 1 and dx > 0) else (-2.5 if f == 1 else 0)
            for lado in (-1, 1):
                pata = lz.trazo([(x + lado * 2.5, y + 2), (x + lado * 4 + paso, y + 8), (x + lado * 5 + paso, y + 10.5)], 2.8, 2.0)
                lz.sombrear(pata, piel[1:], 1.4, LUZ)
                for g in range(3):
                    lz.pintar(lz.trazo([(x + lado * 5 + paso + g * 1.2 - 1.2, y + 11), (x + lado * 5 + paso + g * 1.6 - 1.8, y + 12.5)], 0.4), "#d8ccb0")
    # el cuerpo
    cuerpo = _columna(lz, espina, gruesos)
    lz.sombrear(cuerpo, piel, 6, LUZ, textura=lz.ruido(0.7, 2, semilla=402), fuerza_tex=0.35)
    # el vientre claro, por abajo
    vientre = cuerpo * (lz.y > np.interp(lz.x, [p[0] for p in espina], [p[1] for p in espina]) + 4.5)
    lz.pintar(vientre, VIENTRE[1] if not libre else "#b8b47a", 0.75)
    lz.pintar(vientre * ((lz.x % 3) < 0.6), VIENTRE[0], 0.5)
    # las placas del lomo: dos filas de escudos (de hierro oxidado; libre, de bronce)
    for k in range(1, len(espina) - 1):
        x, y = espina[k]
        g = gruesos[k]
        for fila in (-0.62, -0.22, 0.18):
            ancho = max(1.1, g * (0.34 if fila == -0.22 else 0.28))
            placa = lz.elipse(x + (0.6 if fila != -0.22 else 0), y + fila * g, ancho, max(0.8, g * 0.18))
            lz.sombrear(placa, placas_c[1:], 1.0, LUZ, textura=lz.ruido(0.4, 1, semilla=403 + k), fuerza_tex=0.3)
        cresta = lz.poligono([(x - 1.2, y - g * 0.8), (x, y - g * 0.8 - 1.8 - (k % 2)), (x + 1.2, y - g * 0.8)])
        lz.pintar(cresta, placas_c[4])
    if not libre:
        # las grietas de Giza entre las placas, que brillan
        grietas = (np.abs(np.sin(lz.x * 0.9 + lz.ruido(1.2, 2, semilla=404) * 6)) < 0.08) * cuerpo * (lz.y < 36)
        lz.pintar(grietas, GIZA[3], 0.9)
        lz.brillo(grietas, GIZA[3], 1.4, 0.35)
    # la cabeza: el morro largo y chato, delante del cuello
    cx, cy = espina[-1]
    boca = {1: 1.0, 4: 0.3, 5: 0.35, 6: 0.0}.get(f, 0.0)
    abajo_cab = 0.0 if f not in (2, 3) else 2.0                       # atascado: la cabeza baja, contra el poste
    craneo = lz.elipse(cx + 4, cy - 1 + abajo_cab, 11, 7.5)
    hocico_sup = lz.poligono([(cx + 6, cy - 6.5 + abajo_cab), (cx + 27, cy - 3.5 + abajo_cab - boca * 5), (cx + 29.5, cy - 1 + abajo_cab - boca * 5),
                              (cx + 28, cy + 1.5 + abajo_cab - boca * 5), (cx + 6, cy + 2.5 + abajo_cab)])
    mandibula = lz.poligono([(cx + 4, cy + 2 + abajo_cab), (cx + 27, cy + 3 + abajo_cab + boca * 6), (cx + 26, cy + 6 + abajo_cab + boca * 6),
                             (cx + 4, cy + 6 + abajo_cab)])
    if boca > 0.2:
        # el interior de la boca, rosado y oscuro
        dentro = lz.poligono([(cx + 6, cy + 1.5 + abajo_cab), (cx + 28, cy + 1 + abajo_cab - boca * 5), (cx + 26, cy + 3 + abajo_cab + boca * 6)])
        lz.pintar(dentro, "#5a1e22")
        lz.pintar(dentro * (lz.y > cy + 2 + abajo_cab), "#8a3a3a", 0.8)
    lz.sombrear(mandibula, piel[1:], 2, LUZ)
    lz.sombrear(np.maximum(craneo, hocico_sup), piel, 3.5, LUZ, textura=lz.ruido(0.6, 2, semilla=405), fuerza_tex=0.3)
    # los dientes, por fuera, en zigzag (amarillentos; libre, blancos)
    diente = "#e8dcb0" if not libre else "#fff8e8"
    for k in range(7):
        x = cx + 9 + k * 2.8
        ys = cy + 1.6 + abajo_cab - boca * 5 * (x - cx - 6) / 22
        yi = cy + 2.8 + abajo_cab + boca * 6 * (x - cx - 4) / 23
        lz.pintar(lz.poligono([(x - 0.7, ys), (x, ys + 1.8), (x + 0.7, ys)]), diente)
        lz.pintar(lz.poligono([(x + 0.7, yi), (x + 1.4, yi - 1.8), (x + 2.1, yi)]), diente)
    # las narinas en la punta y el ojo saltón (con su párpado de placa)
    lz.pintar(lz.circulo(cx + 26.5, cy - 2.8 + abajo_cab - boca * 5, 0.8), "#0e0a08")
    ox, oy = cx + 4, cy - 7 + abajo_cab
    lz.sombrear(lz.elipse(ox, oy, 3.6, 2.8), placas_c[1:], 1.5, LUZ)
    if f == 5:
        for r in (1.6, 0.9):
            lz.pintar(np.clip(lz.circulo(ox + 0.4, oy, r) - lz.circulo(ox + 0.4, oy, r - 0.35), 0, 1), "#fff3c4")
    else:
        color_ojo = "#e6a852" if libre else GIZA[4]
        lz.pintar(lz.elipse(ox + 0.6, oy, 1.5, 1.2), color_ojo)
        lz.pintar(lz.elipse(ox + 0.8, oy, 0.4, 1.0), "#0e0a08")
        if not libre:
            lz.brillo(lz.circulo(ox + 0.6, oy, 1.2), GIZA[3], 2.0, 0.5)
    if libre:
        # una sonrisa de cocodrilo (la comisura hacia arriba)
        lz.pintar(lz.trazo([(cx + 7, cy + 2), (cx + 11, cy + 1.2)], 0.4), "#18241a")
    # flotando: el agua le tapa todo lo de abajo, con una onda alrededor
    if f == 0:
        linea = 38.0
        agua = (lz.y > linea - 0.5) * (lz.y < linea + 1.2) * np.clip(1 - np.abs(lz.x - 56) / 54, 0, 1)
        img = lz.sprite(tramado=0.003, contorno=CONTORNO)
        corte = int(round((linea + 0.8)))
        img[corte:, :, 3] = 0
        onda = Lienzo(W, H, s=6, semilla=409)
        onda.alfa[:] = 0
        onda.pintar(agua, AGUA[5], 0.8)
        o = onda.sprite(tramado=0.0)
        m = o[:, :, 3:4] / 255.0
        img[:, :, :3] = (img[:, :, :3] * (1 - m) + o[:, :, :3] * m).astype(np.uint8)
        img[:, :, 3] = np.maximum(img[:, :, 3], o[:, :, 3])
        return img
    return lz.sprite(tramado=0.003, contorno=CONTORNO)


def main():
    hoja = tira([cocodrilo(f) for f in range(7)])
    ruta = os.path.join(RAIZ, "arte", "zonas", "raiz", "mamba.png")
    hoja.save(ruta)
    print("guardado:", ruta, hoja.size)


if __name__ == "__main__":
    main()
