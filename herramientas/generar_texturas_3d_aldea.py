#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_texturas_3d_aldea.py
Genera las texturas pixel art HD-2D oficiales para los modelos 3D de Cuna de Musgo:
- seta_pared_tile.png (cilindro y paredes de madera clara con vetas y musgo para Casa Seta de Pino)
- seta_tejado_tile.png (sombrero de seta carmesí con motas blancas cremosas)
- forja_mamposteria_tile.png (mampostería de piedra tiznada y bloques de sillería para la Forja de Corteza)
- forja_tejado_tile.png (tejadillo de tablillas solapadas de madera oscura con musgo)
- toldo_rayas_tile.png (toldo de lona con rayas verde oliva y crema para el puesto de Tawi)
- ruina_mamposteria_tile.png (bloques de piedra fracturada y desgastada para las ruinas 3D)
- trasera_casa_pino.png (fachada posterior de la Casa Seta con ventana circular iluminada)
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa
from pintar_casa_shamba import vetas, rect
from cinematicas import PIEDRA, piedras
import pintar_aldea as pa

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "arte", "mundos", "raiz", "aldea")
os.makedirs(SALIDA, exist_ok=True)

LUZ = (-0.6, -0.8, 1.0)
CREMA = ["#4a3c28", "#786446", "#a8906c", "#d8c49c", "#f4e6c8", "#fff8ee"]
ROJO = ["#4a1418", "#7a1a24", "#b02636", "#dc3c48", "#f06c68", "#ffa090"]
PIEDRA_C = ["#2a2622", "#443e38", "#645c54", "#867e74", "#aca498", "#cec6b8"]
MADERA = ["#180e08", "#2c1a10", "#482c1c", "#68422c", "#8c5c3e", "#b07a54", "#d49a6e"]
TRONCO = ["#1c120c", "#322016", "#4e3424", "#6e4c36", "#90664a", "#b48462"]

def pintar_seta_pared_tile():
    """Genera textura continua de tablas/estacas de madera cremosa con musgo para la Casa Seta (128x128)."""
    lz = Lienzo(128, 128, s=4, semilla=101)
    base = rect(lz, 0, 0, 128, 128)
    tex = vetas(lz, 0.6, 16, False, semilla=102)
    lz.sombrear(base, CREMA, 8, LUZ, textura=tex, fuerza_tex=0.35)
    # Listones verticales
    for x in range(0, 128, 16):
        lz.pintar(rect(lz, x, 0, x + 1.2, 128), "#322416", 0.65)
        lz.pintar(rect(lz, x + 1.2, 0, x + 2.4, 128), "#fff8ee", 0.25)
    # Zócalo inferior de piedrecitas y musgo
    zocalo = rect(lz, 0, 104, 128, 128)
    piedras(lz, zocalo, tam=4.5, semilla=103, luz=LUZ, mortero="#3a3428", rampa_p=PIEDRA_C)
    musgo = (lz.ruido(2.2, 3, semilla=104) > 0.60) * np.clip((lz.y - 92) / 16, 0, 1)
    lz.pintar(lz.desenfocar(musgo, 0.4), rampa(["#24401f", "#3f5a2f", "#5d7a3c"], lz.ruido(0.7, 2)), 0.8)
    ruta = os.path.join(SALIDA, "seta_pared_tile.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_seta_tejado_tile():
    """Genera textura continua de sombrero de seta carmesí con motas blancas (128x128)."""
    lz = Lienzo(128, 128, s=4, semilla=201)
    base = rect(lz, 0, 0, 128, 128)
    tex = lz.ruido(0.9, 2, semilla=202)
    lz.sombrear(base, ROJO, 10, LUZ, textura=tex, fuerza_tex=0.25)
    # Motas blancas redondeadas repartidas orgánicamente
    motas_pos = [
        (24, 24, 9), (88, 32, 11), (48, 76, 10), (108, 92, 8),
        (16, 112, 7), (72, 116, 6), (124, 16, 7), (4, 16, 7)
    ]
    for (mx, my, mr) in motas_pos:
        mota = lz.elipse(mx, my, mr, mr * 0.85)
        lz.sombrear(mota, ["#c8b8a0", "#e8dcc8", "#fff8ee"], 1.4, LUZ)
    # Poros tenues y textura aterciopelada
    poros = (lz.ruido(4.0, 2, semilla=203) > 0.72)
    lz.pintar(poros, "#7a1a24", 0.3)
    ruta = os.path.join(SALIDA, "seta_tejado_tile.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_forja_mamposteria_tile():
    """Genera textura continua de mampostería de piedra de forja con hollín (128x128)."""
    lz = Lienzo(128, 128, s=4, semilla=301)
    base = rect(lz, 0, 0, 128, 128)
    piedras(lz, base, tam=5.5, semilla=302, luz=LUZ, mortero="#1c1814", rampa_p=PIEDRA_C)
    # Manchas de hollín y ceniza
    hollin = lz.ruido(1.8, 3, semilla=303)
    lz.pintar(np.clip(hollin - 0.45, 0, 1), "#14100c", 0.45)
    # Grietas y musgo en juntas
    musgo = (lz.ruido(2.5, 2, semilla=304) > 0.72)
    lz.pintar(musgo, "#3f5228", 0.4)
    ruta = os.path.join(SALIDA, "forja_mamposteria_tile.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_forja_tejado_tile():
    """Genera textura de tablillas de madera solapadas con musgo (128x128)."""
    lz = Lienzo(128, 128, s=4, semilla=401)
    base = rect(lz, 0, 0, 128, 128)
    filas = 8
    alto_fila = 128 / filas
    lz.pintar(base, "#2a160e")
    for k in range(filas):
        y0 = int(k * alto_fila)
        y1 = int((k + 1) * alto_fila)
        offset_x = (k % 2) * 16
        for x in range(-16 + offset_x, 144, 32):
            tablilla = rect(lz, max(0, x), y0, min(128, x + 30), y1)
            lz.sombrear(tablilla, ["#2a160e", "#47291c", "#643a26", "#7f4d33", "#9a6544"], 1.5, LUZ,
                        textura=vetas(lz, 0.4, 7, True), fuerza_tex=0.35)
        # Sombra de solape inferior
        lz.pintar(rect(lz, 0, y1 - 2, 128, y1), "#120a06", 0.7)
    # Musgo salpicado
    musgo = (lz.ruido(2.0, 3, semilla=405) > 0.68)
    lz.pintar(lz.desenfocar(musgo, 0.5), rampa(["#2a3a1e", "#3e5228", "#566c34"], lz.ruido(0.6, 2)), 0.6)
    ruta = os.path.join(SALIDA, "forja_tejado_tile.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_toldo_rayas_tile():
    """Genera textura continua de toldo a rayas para el puesto de mercado (128x128)."""
    lz = Lienzo(128, 128, s=4, semilla=501)
    base = rect(lz, 0, 0, 128, 128)
    # Rayas verticales alternas: verde bosque / musgo y crema lino
    ancho_raya = 16
    for i in range(8):
        x0 = i * ancho_raya
        x1 = (i + 1) * ancho_raya
        franja = rect(lz, x0, 0, x1, 128)
        if i % 2 == 0:
            lz.sombrear(franja, ["#183a20", "#265430", "#3a7646", "#529a60"], 1.2, LUZ,
                        textura=lz.ruido(1.2, 2), fuerza_tex=0.2)
        else:
            lz.sombrear(franja, ["#5a4e38", "#8c7c5e", "#baa886", "#dfd0b2", "#f4ecdc"], 1.2, LUZ,
                        textura=lz.ruido(1.2, 2), fuerza_tex=0.2)
        # Sombra en los pliegues entre franjas
        lz.pintar(rect(lz, x0, 0, x0 + 1.5, 128), "#101810", 0.4)
    ruta = os.path.join(SALIDA, "toldo_rayas_tile.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_ruina_mamposteria_tile():
    """Genera textura continua de bloques de mampostería fracturada y agrietada para ruinas (128x128)."""
    lz = Lienzo(128, 128, s=4, semilla=601)
    base = rect(lz, 0, 0, 128, 128)
    GRIS_R = ["#1a1a1c", "#28282a", "#3c3c3e", "#545458", "#6e6e72", "#8c8c90"]
    piedras(lz, base, tam=5.0, semilla=602, luz=LUZ, mortero="#141416", rampa_p=GRIS_R)
    # Grietas oscuras
    grietas = (lz.ruido(3.2, 3, semilla=603) > 0.82)
    lz.pintar(grietas, "#0c0c0e", 0.75)
    # Líquenes secos
    liquen = (lz.ruido(2.2, 2, semilla=604) > 0.75)
    lz.pintar(liquen, "#444a38", 0.45)
    ruta = os.path.join(SALIDA, "ruina_mamposteria_tile.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

def pintar_trasera_casa_pino():
    """Genera la fachada trasera completa para la Casa Seta de Pino (120x116)."""
    W, H = 120, 116
    lz = Lienzo(W, H, s=4, semilla=701)
    cx = 60
    suelo = 112
    # Pie de la seta posterior
    pie = lz.poligono([(cx - 30, suelo), (cx - 27, 70), (cx - 24, 52), (cx + 24, 52), (cx + 27, 70), (cx + 30, suelo)])
    tex = vetas(lz, 0.6, 15, False, semilla=702)
    lz.sombrear(pie, CREMA, 10, LUZ, textura=tex, fuerza_tex=0.3)
    zocalo = rect(lz, cx - 31, suelo - 8, cx + 31, suelo)
    piedras(lz, zocalo * pie, tam=3.6, semilla=703, luz=LUZ, mortero="#3a3428", rampa_p=PIEDRA_C)
    musgo = (lz.ruido(2, 3, semilla=704) > 0.62) * pie * np.clip((lz.y - 96) / 12, 0, 1)
    lz.pintar(lz.desenfocar(musgo, 0.4), rampa(["#24401f", "#3f5a2f", "#5d7a3c"], lz.ruido(0.7, 2)), 0.8)
    
    # Ventana trasera redonda central iluminada con luz cálida
    vx, vy, r = cx, 74, 6.0
    aro = np.clip(lz.circulo(vx, vy, r + 1.6) - lz.circulo(vx, vy, r), 0, 1)
    lz.sombrear(aro, TRONCO, 1, LUZ)
    vid = lz.circulo(vx, vy, r)
    lz.pintar(vid, rampa(["#a8380f", "#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - vx + 1, lz.y - vy + 1) / r, 0, 1)))
    lz.pintar(np.maximum(rect(lz, vx - r, vy - 0.5, vx + r, vy + 0.5), rect(lz, vx - 0.5, vy - r, vx + 0.5, vy + r)) * vid, "#2a1a12")
    lz.sumar_luz(lz.desenfocar(vid, 4), "#ef8a26", 0.45)
    
    # Sombrero carmesí visto desde atrás
    som = lz.poligono([(cx - 56, 52), (cx - 50, 34), (cx - 36, 18), (cx - 18, 8), (cx, 5), (cx + 18, 8), (cx + 36, 18), (cx + 50, 34), (cx + 56, 52), (cx, 56)])
    lz.sombrear(som, ROJO, 14, LUZ, textura=lz.ruido(0.8, 2, semilla=705), fuerza_tex=0.25)
    for (x, y, r_m) in ((-30, 24, 5.5), (-10, 38, 4.5), (15, 20, 6.0), (35, 36, 5.0), (0, 16, 4.0)):
        lun = lz.elipse(cx + x, y, r_m, r_m * 0.75) * som
        lz.sombrear(lun, ["#c8b8a0", "#e8dcc8", "#fff8ee"], 1.2, LUZ)
    
    ruta = os.path.join(SALIDA, "trasera_casa_pino.png")
    lz.guardar(ruta)
    print(f"Guardado: {ruta}")

if __name__ == "__main__":
    print("--- Generando texturas 3D pixel art para Cuna de Musgo ---")
    pintar_seta_pared_tile()
    pintar_seta_tejado_tile()
    pintar_forja_mamposteria_tile()
    pintar_forja_tejado_tile()
    pintar_toldo_rayas_tile()
    pintar_ruina_mamposteria_tile()
    pintar_trasera_casa_pino()
    print("--- Completado con éxito ---")
