#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_texturas_3d_sigilia.py
Genera las texturas pixel art HD-2D oficiales para los modelos 3D de Maandiko (Sigilia):
- marmol_sigilia_tile.png (mármol clásico blanco con vetas suaves y ribetes dorados)
- teja_cobriza_tile.png (tejas curvas cobrizas y terracota para tejados clásicos)
- bronce_sigilia_tile.png (metal de bronce antiguo con detalles rúnicos)
- trasera_gran_archivo.png (fachada posterior monumental con hornacinas, pilastras y cartelas rúnicas)
- trasera_taller_taa.png (fachada posterior con chimenea de piedra y ventanal iluminado)
- trasera_casa_escriba.png (fachada posterior con sillares de esquina y ventanales con luz de vela)
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa
from pintar_casa_shamba import vetas, rect
from cinematicas import piedras

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "arte", "mundos", "sigilia", "maandiko")
os.makedirs(SALIDA, exist_ok=True)

LUZ = (-0.6, -0.8, 1.0)
MARMOL = ["#3a3848", "#5a566c", "#848098", "#aba7be", "#d0cde0", "#ebe8f4", "#ffffff"]
ORO = ["#4a3410", "#78561c", "#b0822a", "#e0b040", "#f8d468", "#fffaaa"]
TEJA_COBRE = ["#34140e", "#5c241a", "#883c2e", "#b85642", "#dc765e", "#f29e88"]
TINTA = ["#101428", "#1c2448", "#2c3870", "#4256a4", "#627ce0", "#94aeff"]
PIEDRA_S = ["#282632", "#3e3c4e", "#585468", "#747086", "#9692aa", "#bcbad0"]

def pintar_marmol_tile():
    """Genera textura continua de mármol clásico blanco con vetas suaves (128x128)."""
    lz = Lienzo(128, 128, s=4, semilla=801)
    base = rect(lz, 0, 0, 128, 128)
    tex = lz.ruido(0.8, 3, semilla=802)
    lz.sombrear(base, MARMOL, 12, LUZ, textura=tex, fuerza_tex=0.20)
    # Vetas finas de mármol
    vetas_m = (lz.ruido(2.8, 3, semilla=803) > 0.78)
    lz.pintar(vetas_m, "#aba7be", 0.40)
    # Filete dorado superior e inferior sutil
    lz.pintar(rect(lz, 0, 0, 128, 2), "#e0b040", 0.65)
    lz.pintar(rect(lz, 0, 126, 128, 128), "#78561c", 0.75)
    ruta = os.path.join(SALIDA, "marmol_sigilia_tile.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_teja_cobriza_tile():
    """Genera textura continua de teja curva cobriza / terracota (128x128)."""
    lz = Lienzo(128, 128, s=4, semilla=901)
    base = rect(lz, 0, 0, 128, 128)
    filas = 8
    alto_fila = 128 / filas
    lz.pintar(base, "#34140e")
    for k in range(filas):
        y0 = int(k * alto_fila)
        y1 = int((k + 1) * alto_fila)
        offset_x = (k % 2) * 8
        for x in range(-8 + offset_x, 136, 16):
            teja = rect(lz, max(0, x), y0, min(128, x + 15), y1)
            # Arco curvado de teja canal
            curva = np.sin(np.clip((lz.x - x) / 15.0, 0, 1) * np.pi)
            lz.sombrear(teja, TEJA_COBRE, 1.8, LUZ, textura=curva, fuerza_tex=0.45)
        lz.pintar(rect(lz, 0, y1 - 2, 128, y1), "#1e0c08", 0.65)
    ruta = os.path.join(SALIDA, "teja_cobriza_tile.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_bronce_sigilia_tile():
    """Genera textura continua de bronce patinado antiguo con acentos rúnicos (128x128)."""
    lz = Lienzo(128, 128, s=4, semilla=1001)
    base = rect(lz, 0, 0, 128, 128)
    BRONCE = ["#2a2012", "#483620", "#6e5432", "#9a7848", "#c49e62", "#e8c484"]
    lz.sombrear(base, BRONCE, 8, LUZ, textura=lz.ruido(1.5, 2), fuerza_tex=0.25)
    # Pátina verdosa en juntas y recovecos
    patina = (lz.ruido(2.2, 3, semilla=1002) > 0.74)
    lz.pintar(patina, "#3a6854", 0.55)
    # Remaches dorados en las esquinas
    for rx in (16, 64, 112):
        for ry in (16, 64, 112):
            rem = lz.circulo(rx, ry, 3.5)
            lz.sombrear(rem, ORO, 1.2, LUZ)
    ruta = os.path.join(SALIDA, "bronce_sigilia_tile.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_trasera_gran_archivo():
    """Genera la fachada posterior monumental del Gran Archivo (160x130)."""
    W, H = 160, 130
    lz = Lienzo(W, H, s=4, semilla=1101)
    suelo = 126
    # 1. Podio de mármol escalonado
    podio = rect(lz, 8, 112, 152, suelo)
    lz.sombrear(podio, MARMOL, 4, LUZ)
    lz.pintar(rect(lz, 8, 112, 152, 114), "#ffffff", 0.4)
    # 2. Gran muro de mármol con pilastras
    muro = rect(lz, 18, 32, 142, 112)
    lz.sombrear(muro, MARMOL, 10, LUZ, textura=lz.ruido(0.8, 3), fuerza_tex=0.2)
    # 4 pilastras acanaladas
    for px in (28, 62, 98, 132):
        pilastra = rect(lz, px - 5, 30, px + 5, 112)
        lz.sombrear(pilastra, MARMOL, 1.5, LUZ)
        # Capitel y basa dorados
        lz.sombrear(rect(lz, px - 6, 30, px + 6, 35), ORO, 1, LUZ)
        lz.sombrear(rect(lz, px - 6, 107, px + 6, 112), ORO, 1, LUZ)
    # 3. Tres hornacinas con cartelas de tinta y runas doradas
    for cx in (45, 80, 115):
        hornacina = lz.poligono([(cx - 8, 92), (cx - 8, 56)] +
                                [(cx + np.cos(a) * 8, 56 - np.sin(a) * 8) for a in np.linspace(np.pi, 0, 16)] +
                                [(cx + 8, 56), (cx + 8, 92)])
        lz.sombrear(hornacina, TINTA, 3, LUZ)
        # Cartela rúnica dorada interior
        cartela = rect(lz, cx - 4, 66, cx + 4, 82)
        lz.sombrear(cartela, ORO, 1.2, LUZ)
        lz.sumar_luz(lz.desenfocar(cartela, 2.5), "#f8d468", 0.4)
    # 4. Cornisa perimetral superior moldurada
    cornisa = rect(lz, 14, 24, 146, 32)
    lz.sombrear(cornisa, MARMOL, 2, LUZ)
    lz.pintar(rect(lz, 14, 30, 146, 32), "#e0b040", 0.7)
    # 5. Cúpula dorada visible por encima
    cupula = lz.elipse(80, 24, 38, 22) * rect(lz, 40, 0, 120, 24)
    lz.sombrear(cupula, ORO, 8, LUZ)
    lz.sumar_luz(lz.desenfocar(cupula, 3), "#e0b040", 0.35)
    
    ruta = os.path.join(SALIDA, "trasera_gran_archivo.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_trasera_taller_taa():
    """Genera la fachada posterior del taller de Taa con chimenea y ventanal (120x110)."""
    W, H = 120, 110
    lz = Lienzo(W, H, s=4, semilla=1201)
    suelo = 106
    # Planta baja de piedra
    pb = rect(lz, 18, 58, 102, suelo)
    piedras(lz, pb, tam=4.5, semilla=1202, luz=LUZ, mortero="#22202a", rampa_p=PIEDRA_S)
    # Planta alta en voladizo con entramado de madera
    pa = rect(lz, 14, 28, 106, 58)
    lz.sombrear(pa, ["#4a4436", "#726a58", "#9c947e", "#c8c0a8", "#ece4ce"], 6, LUZ)
    for x in (14, 38, 62, 86, 104):
        lz.sombrear(rect(lz, x, 28, x + 2.5, 58), ["#180e08", "#322016", "#5a3a24", "#7e5236"], 0.8, LUZ)
    # Tejado a dos aguas cobrizo
    techo = lz.poligono([(8, 30), (60, 4), (112, 30)])
    lz.sombrear(techo, TEJA_COBRE, 6, LUZ)
    # Chimenea de piedra a la izquierda
    chim = rect(lz, 24, 0, 36, 58)
    piedras(lz, chim, tam=3.5, semilla=1203, luz=LUZ, mortero="#22202a", rampa_p=PIEDRA_S)
    cap = rect(lz, 22, 0, 38, 4)
    lz.sombrear(cap, PIEDRA_S, 1, LUZ)
    # Ventanal trasero iluminado con luz cálida de vela
    vx, vy = 72, 40
    vent = rect(lz, vx - 8, vy - 6, vx + 8, vy + 6)
    lz.pintar(vent, rampa(["#a8380f", "#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - vx, lz.y - vy) / 8, 0, 1)))
    lz.pintar(np.maximum(rect(lz, vx - 8, vy - 0.4, vx + 8, vy + 0.4), rect(lz, vx - 0.4, vy - 6, vx + 0.4, vy + 6)) * vent, "#1c1410")
    lz.sumar_luz(lz.desenfocar(vent, 3), "#ef8a26", 0.45)
    
    ruta = os.path.join(SALIDA, "trasera_taller_taa.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_trasera_casa_escriba():
    """Genera la fachada posterior de la Casa del Escriba (120x110)."""
    W, H = 120, 110
    lz = Lienzo(W, H, s=4, semilla=1301)
    suelo = 106
    # Muros enlucidos de mármol/estuco blanco
    muro = rect(lz, 20, 32, 100, suelo)
    lz.sombrear(muro, MARMOL, 8, LUZ, textura=lz.ruido(0.7, 2), fuerza_tex=0.18)
    # Sillares de esquina de granito en las aristas
    for ex in (20, 96):
        esq = rect(lz, ex, 32, ex + 4, suelo)
        piedras(lz, esq, tam=3.0, semilla=1302, luz=LUZ, mortero="#303038", rampa_p=PIEDRA_S)
    # Tejado a dos aguas de teja cobriza
    techo = lz.poligono([(12, 34), (60, 8), (108, 34)])
    lz.sombrear(techo, TEJA_COBRE, 6, LUZ)
    # Chimenea esbelta a la derecha
    chim = rect(lz, 78, 2, 88, 52)
    piedras(lz, chim, tam=3.2, semilla=1303, luz=LUZ, mortero="#303038", rampa_p=PIEDRA_S)
    # Ventanas con vidrieras enrejadas y luz cálida
    for (vx, vy) in ((40, 50), (40, 80), (70, 78)):
        vent = rect(lz, vx - 6, vy - 6, vx + 6, vy + 6)
        lz.pintar(vent, rampa(["#a8380f", "#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - vx, lz.y - vy) / 6, 0, 1)))
        lz.pintar(np.maximum(rect(lz, vx - 6, vy - 0.4, vx + 6, vy + 0.4), rect(lz, vx - 0.4, vy - 6, vx + 0.4, vy + 6)) * vent, "#1c1410")
        lz.sumar_luz(lz.desenfocar(vent, 2.5), "#ef8a26", 0.4)
    
    ruta = os.path.join(SALIDA, "trasera_casa_escriba.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

if __name__ == "__main__":
    print("--- Generando texturas 3D pixel art para Maandiko (Sigilia) ---")
    pintar_marmol_tile()
    pintar_teja_cobriza_tile()
    pintar_bronce_sigilia_tile()
    pintar_trasera_gran_archivo()
    pintar_trasera_taller_taa()
    pintar_trasera_casa_escriba()
    print("--- Completado con éxito ---")
