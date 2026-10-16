#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_musica_paralelo.py
Regenera todas las pistas musicales de Maisha en paralelo con sintetizador.py
y mide los niveles RMS (dBFS) para calibrar VOLUMEN_MUSICA en sonido.gd.
"""

import os
import sys
import time
import subprocess
import numpy as np
from multiprocessing import Pool, cpu_count

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))

import sintetizador
from sintetizador import SR, semilla, guardar, suavizar_bordes, estereo
import componer_musica
from componer_musica import PIEZAS, TITULOS, NO_SE_REPITEN, DESTINO

def generar_pieza(nombre):
    t0 = time.time()
    funcion = PIEZAS[nombre]
    semilla(len(nombre) * 101)
    x = funcion()
    if nombre in NO_SE_REPITEN:
        x = suavizar_bordes(estereo(x), 0.005, 0.05)
    ruta = os.path.join(DESTINO, nombre + ".ogg")
    guardar(x, ruta, 0.8, calidad=5, titulo=TITULOS.get(nombre, nombre))
    dt = time.time() - t0
    dur = len(x) / SR
    return nombre, dur, dt

def medir_dbfs(ruta):
    """Decodifica el archivo .ogg con ffmpeg y calcula el nivel RMS en dBFS."""
    cmd = [
        sintetizador._ffmpeg(),
        "-i", ruta,
        "-f", "s16le",
        "-ac", "2",
        "-ar", str(SR),
        "-"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    muestras = np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    rms = float(np.sqrt(np.mean(muestras ** 2)))
    if rms > 0:
        return 20.0 * np.log10(rms)
    return -99.0

def main():
    n_cpu = min(6, max(2, cpu_count() - 1))
    piezas = list(PIEZAS.keys())
    print(f"Generando {len(piezas)} pistas de música en paralelo ({n_cpu} procesos)...")
    
    t_inicio = time.time()
    with Pool(processes=n_cpu) as pool:
        for nombre, dur, dt in pool.imap_unordered(generar_pieza, piezas):
            print(f"  [OK] {nombre:20s} ({dur:5.1f}s) en {dt:4.1f}s")
            
    t_total = time.time() - t_inicio
    print(f"\nTodas las piezas generadas en {t_total:.1f} segundos.")
    
    print("\n--- MEDICIÓN DE VOLUMEN (RMS dBFS) ---")
    print(f"{'Pista':22s} | {'RMS (dBFS)':10s} | {'Delta vs -15.5':15s} | {'Sugerencia':10s}")
    print("-" * 65)
    
    resultados = {}
    referencia = -15.5
    for nombre in sorted(piezas):
        ruta = os.path.join(DESTINO, nombre + ".ogg")
        if os.path.exists(ruta):
            db = medir_dbfs(ruta)
            delta = referencia - db # Si db es -18, delta es +2.5 dB
            sugerencia = round(delta * 2) / 2.0 # redondeo a 0.5 dB
            resultados[nombre] = (db, sugerencia)
            print(f"{nombre:22s} | {db:10.2f} | {delta:+15.2f} | {sugerencia:+10.1f} dB")
            
    print("\nFin de medición.")

if __name__ == "__main__":
    main()
