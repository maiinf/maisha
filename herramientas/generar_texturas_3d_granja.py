#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_texturas_3d_granja.py
Genera las texturas pixel art HD-2D oficiales para el modelo 3D sólido de la Casa Granja de Shamba:
- trasera_casa_granja.png (fachada trasera completa de troncos, piedra, aleros y dos ventanas iluminadas)
- tejado_paja_tile.png (textura continua de paja/tejado trenzado)
- pared_troncos_tile.png (textura continua de troncos de madera)
- mamposteria_tile.png (textura de mampostería de piedra para zócalo y chimenea)
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa
from cinematicas import PIEDRA, PAJA, piedras
import pintar_casa_shamba as pcs

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "arte", "mundos", "kitovu")
os.makedirs(SALIDA, exist_ok=True)

def pintar_trasera():
    """Genera la fachada trasera completa de la casa granja (184x140)."""
    lz = Lienzo(184, 140, s=4, semilla=28)
    x0, x1 = 30, 170
    suelo = 132

    # 1. Zócalo de piedra con musgo
    zocalo = pcs.rect(lz, x0 - 4, 116, x1 + 4, suelo)
    piedras(lz, zocalo, tam=5.2, semilla=3, luz=pcs.LUZ, mortero="#525449", rampa_p=pcs.PIEDRA_C)
    musgo = (lz.ruido(2.5, 3, semilla=31) > 0.68) * zocalo * np.clip((lz.y - 120) / 10, 0, 1)
    lz.pintar(lz.desenfocar(musgo, 0.3), rampa(["#24401f", "#3f5a2f", "#5d7a3c"], lz.ruido(0.7, 2)), 0.8)

    # 2. Paredes de troncos horizontales
    pcs.troncos(lz, x0, x1, 70, 116, alto=6.0, semilla=4)
    lz.pintar(np.clip((84 - lz.y) / 14, 0, 1) * pcs.rect(lz, x0 - 4, 70, x1 + 4, 116), "#120b08", 0.55)

    # 3. Chimenea de piedra (vista trasera a la derecha: x entre 140 y 152)
    chim = pcs.rect(lz, 140, 1.5, 152, 52)
    piedras(lz, chim, tam=3.6, semilla=8, luz=pcs.LUZ, mortero="#525449", rampa_p=pcs.PIEDRA_C)
    lz.pintar(np.clip((lz.x - 146) / 6, 0, 1) * chim, "#120b08", 0.35)
    cap = pcs.rect(lz, 138, 0, 154, 3)
    lz.sombrear(cap, PIEDRA, 1.2, pcs.LUZ)

    # 4. Tejado de paja
    tejado_pts = [(100, 8)]
    for k in range(25):
        tt = k / 24
        tejado_pts.append((100 + 10 + 80 * tt ** 0.95 + np.sin(tt * 8) * 0.6, 8 + 66 * tt))
    tejado_pts += [(193, 75), (193, 78)]
    tejado_pts += [(7, 78), (7, 75)]
    for k in range(24, -1, -1):
        tt = k / 24
        tejado_pts.append((100 - 10 - 80 * tt ** 0.95 - np.sin(tt * 8) * 0.6, 8 + 66 * tt))
    tejado = lz.poligono(tejado_pts) * (lz.x < 184)
    pcs.paja(lz, tejado, semilla=5, capas=6.0, y0=8)
    # Caballete
    cab = lz.elipse(100, 9, 13, 3.4)
    lz.sombrear(cab, PAJA, 2, pcs.LUZ, textura=pcs.vetas(lz, 0.5, 7, True), fuerza_tex=0.4)
    pcs.flecos(lz, 8, 184, 77.5, 3.4, semilla=6)

    # 5. Dos ventanas traseras simétricas iluminadas (revelan vida en el interior de la casa)
    for vx in (54, 126):
        pcs.ventana(lz, vx, 81, vx + 16, 97, encendida=0.55, semilla=vx + 77, luz=pcs.LUZ)

    # 6. Pilares y vigas traseras vistas de refuerzo
    for px_ in (46, 100, 154):
        pilar = pcs.rect(lz, px_ - 1.5, 70, px_ + 1.5, 116)
        lz.sombrear(pilar, pcs.TRONCO, 1.2, pcs.LUZ, textura=pcs.vetas(lz, 0.5, 11, False), fuerza_tex=0.35)

    ruta = os.path.join(SALIDA, "trasera_casa_granja.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_tejado_tile():
    """Genera textura continua de paja para el tejado 3D (128x128)."""
    lz = Lienzo(128, 128, s=4, semilla=42)
    m = pcs.rect(lz, 0, 0, 128, 128)
    pcs.paja(lz, m, semilla=7, capas=12.0, y0=0)
    ruta = os.path.join(SALIDA, "tejado_paja_tile.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_troncos_tile():
    """Genera textura continua de troncos para paredes (128x128)."""
    lz = Lienzo(128, 128, s=4, semilla=43)
    pcs.troncos(lz, 0, 128, 0, 128, alto=8.0, semilla=8, esquinas=False)
    ruta = os.path.join(SALIDA, "pared_troncos_tile.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_mamposteria_tile():
    """Genera textura continua de piedra de cantos rodados para zócalo y chimenea (128x128)."""
    lz = Lienzo(128, 128, s=4, semilla=44)
    m = pcs.rect(lz, 0, 0, 128, 128)
    piedras(lz, m, tam=6.0, semilla=12, luz=pcs.LUZ, mortero="#4a4c42", rampa_p=pcs.PIEDRA_C)
    ruta = os.path.join(SALIDA, "mamposteria_tile.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

if __name__ == "__main__":
    pintar_trasera()
    pintar_tejado_tile()
    pintar_troncos_tile()
    pintar_mamposteria_tile()
    print("Todas las texturas HD-2D para la Casa Granja 3D generadas con éxito.")
