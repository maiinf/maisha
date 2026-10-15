"""
MÚSICA DE MAISHA, compuesta nota a nota con el sintetizador (es nuestra: no hay derechos de terceros).

Uso:  python3 herramientas/componer_musica.py [nombre...]
Genera en audio/musica/:
  despertar.ogg   el comienzo de una partida nueva: como despertar de un largo letargo (no se repite)
  kitovu.ogg      el Kitovu gris: melancólico pero con esperanza (en bucle)
  inicio.ogg      la pantalla de inicio: el tema de Maisha (en bucle)
  prados.ogg      los Prados del Eco: luminoso (en bucle)
  aldea.ogg       Cuna de Musgo: cálido y tranquilo (en bucle)
  interior.ogg    dentro de las casas: una nana suave (en bucle)
  combate.ogg     dentro de una zona de Giza: tensión contenida (en bucle)
  jefe.ogg        la pelea contra Mzizi (en bucle)
  purga.ogg, victoria.ogg, objeto.ogg   fanfarrias cortas
  canada.ogg      la Cañada del Eco: la flauta y su eco en la peña (en bucle)
  lago.ogg        el Lago Espejo: el piano y su reflejo (la misma frase al revés) (en bucle)
  jefe_kuvu.ogg   Kuvu, la seta que manda: la caja de música desafinada en bucle, tambores en tres y la flauta que lo rompe
  paso.ogg        el Paso de Piedra: una caja de música que pregunta, un reloj y la flauta que contesta (en bucle)

El tema de Maisha (la melodía que vuelve en todas): D5 A4 E5 F#5 | E5 D5 A4 (B4) D5
Instrumentos: kalimba y balafón (por las raíces suajilis del mundo), flauta, voces y tambores de mano.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sintetizador import (SR, Pista, bajo, balafon, barrido_bajo, campanita, colchon, coro, estereo, flauta, guardar,
                          piano, acorde_piano, paso_bajo,
                          kalimba, maraca, paso_bajo, paso_banda, reverb, semilla, suavizar_bordes, tambor, taiko, ruido_rosa)
import crear_sonidos

DESTINO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio", "musica")

# =============================================================================
# PARTES CON NOMBRE: melodías y acordes que se pueden reutilizar en otras piezas
# (notas: (nota, pulso, duración en pulsos); acordes: una lista de notas por compás)
# =============================================================================

## «El tema de Maisha»: la melodía que vuelve en todas las piezas
TEMA = [("D5", 0, 1.5), ("A4", 1.5, 0.5), ("E5", 2, 1), ("F#5", 3, 1),
        ("E5", 4, 1.5), ("D5", 5.5, 0.5), ("A4", 6, 1), ("D5", 7, 1)]          # (nota, tiempo, duración) en pulsos


## «El tema de Maisha», en menor (para lo triste o lo dormido)
TEMA_MENOR = [("D5", 0, 1.5), ("A4", 1.5, 0.5), ("E5", 2, 1), ("F5", 3, 1), ("E5", 4, 1.5), ("D5", 5.5, 0.5), ("C5", 6, 1), ("D5", 7, 3)]

## «Acordes del letargo»: los de abrir los ojos (piano, re mayor con novenas)
ACORDES_LETARGO = [["D2", "A2", "F#3", "C#4", "E4"], ["B1", "F#2", "D3", "A3", "C#4"], ["G1", "D2", "B2", "F#3", "A3"],
                   ["A1", "E2", "D3", "E3", "G3"], ["D2", "A2", "F#3", "A3", "E4"], ["G1", "D2", "B2", "D3", "F#3"],
                   ["A1", "E2", "C#3", "E3", "G3"], ["D2", "A2", "D3", "F#3", "A3", "E4"]]

## «El tema de Maisha al despertar»: el tema largo, sobre los acordes del letargo (pulsos desde el 2.º acorde)
TEMA_DESPERTAR = [("D5", 4, 1.5), ("A4", 5.5, 0.5), ("E5", 6, 1), ("F#5", 7, 1),
                  ("E5", 8, 1.5), ("D5", 9.5, 0.5), ("A4", 10, 1), ("C#5", 11, 1),
                  ("D5", 16, 1.5), ("A4", 17.5, 0.5), ("E5", 18, 1), ("F#5", 19, 1),
                  ("A5", 20, 1.5), ("G5", 21.5, 0.5), ("E5", 22, 1), ("F#5", 23, 0.5), ("E5", 23.5, 0.5),
                  ("D5", 28, 4)]

## «Raíces dormidas»: los acordes del Kitovu (re menor, con mucho aire)
ACORDES_RAICES = [["D2", "A2", "F3", "E4"], ["A#1", "F2", "D3", "A3"], ["F2", "C3", "E3", "A3"], ["C2", "G2", "E3", "A3"],
                  ["D2", "A2", "F3", "C4"], ["A#1", "F2", "D3", "A3"], ["F2", "C3", "A3", "E4"], ["C2", "G2", "D3", "E3"],
                  ["G1", "D2", "A#2", "A3"], ["A#1", "F2", "D3", "A3"], ["D2", "A2", "F3", "E4"], ["A1", "E2", "D3", "E3"],
                  ["D2", "A2", "F3", "E4"], ["A#1", "F2", "D3", "A3"], ["F2", "C3", "E3", "A3"], ["A1", "E2", "C#3", "E3"]]

## «Raíces dormidas»: la melodía del Kitovu (pocas notas; en medio, el tema en menor)
MELODIA_RAICES = [("A4", 0.5, 1.5), ("E5", 2, 2), ("D5", 5, 2), ("C5", 8.5, 1.5), ("A4", 10.5, 1.5),
                  ("G4", 13, 2), ("E4", 15, 1),
                  ("D5", 16, 1.5), ("A4", 17.5, 0.5), ("E5", 18, 1), ("F5", 19, 1), ("E5", 20, 1.5), ("D5", 21.5, 1.5),
                  ("A4", 24, 2), ("C5", 26, 2), ("E5", 28, 2), ("D5", 30, 2),
                  ("A#4", 32.5, 1.5), ("A4", 34, 2), ("F4", 37, 1), ("D5", 38.5, 1.5),
                  ("E5", 40.5, 1.5), ("A4", 42, 2), ("D5", 44, 2), ("C#5", 46, 2),
                  ("A5", 48.5, 2), ("D6", 53, 2), ("C6", 56.5, 2), ("A5", 60, 2), ("C#6", 62, 2)]

## «El tema de Maisha completo»: con su respuesta (pantalla de inicio)
TEMA_COMPLETO = [("D5", 0, 1.5), ("A4", 1.5, 0.5), ("E5", 2, 1), ("F#5", 3, 1),
                 ("E5", 4, 1.5), ("D5", 5.5, 0.5), ("A4", 6, 1), ("D5", 7, 1),
                 ("B4", 8, 1), ("D5", 9, 1), ("F#5", 10, 1.5), ("E5", 11.5, 0.5),
                 ("D5", 12, 1), ("E5", 13, 0.5), ("D5", 13.5, 0.5), ("C#5", 14, 2),
                 ("F#5", 16, 1.5), ("E5", 17.5, 0.5), ("D5", 18, 1), ("B4", 19, 1),
                 ("A4", 20, 1), ("C#5", 21, 1), ("E5", 22, 2),
                 ("D5", 24, 1), ("B4", 25, 1), ("G4", 26, 1), ("F#4", 27, 1),
                 ("E4", 28, 2), ("A4", 30, 2)]

## «Camino de los Prados»: el tema de Maisha hecho canción de camino (en sol)
TEMA_CAMINO = [("G5", 0, 1.5), ("D5", 1.5, 0.5), ("A5", 2, 1), ("B5", 3, 1),
               ("A5", 4, 1.5), ("G5", 5.5, 0.5), ("D5", 6, 1), ("G5", 7, 1),
               ("B5", 8, 1), ("A5", 9, 0.5), ("G5", 9.5, 0.5), ("E5", 10, 2),
               ("D5", 12, 1), ("E5", 13, 1), ("G5", 14, 2),
               ("C6", 16, 1.5), ("B5", 17.5, 0.5), ("A5", 18, 1), ("E5", 19, 1),
               ("D5", 20, 1), ("F#5", 21, 1), ("B5", 22, 2),
               ("C6", 24, 1), ("B5", 25, 1), ("G5", 26, 1), ("E5", 27, 1),
               ("D5", 28, 2), ("A5", 30, 1), ("F#5", 31, 1)]

## «Cuna de Musgo»: el motivo saltarín del pueblo (en do)
MOTIVO_MUSGO = [("E5", 0, 1), ("G5", 1, 0.5), ("A5", 1.5, 1), ("G5", 2.5, 1.5),
                ("E5", 4, 1), ("C5", 5, 1), ("D5", 6, 1), ("E5", 7, 1),
                ("F5", 8, 1), ("E5", 9, 1), ("D5", 10, 1), ("C5", 11, 1),
                ("B4", 12, 1), ("D5", 13, 1), ("G5", 14, 2),
                ("A5", 16, 1), ("G5", 17, 1), ("E5", 18, 1), ("C5", 19, 1),
                ("B4", 20, 1), ("D5", 21, 1), ("G5", 22, 1), ("E5", 23, 1),
                ("F5", 24, 1), ("A5", 25, 1), ("G5", 26, 1), ("F5", 27, 1),
                ("D5", 28, 1), ("B4", 29, 1), ("G4", 30, 2)]

## «Nana de la chimenea»: el tema de Maisha como nana (en fa) y sus acordes
TEMA_NANA = [("F5", 0, 1.5), ("C5", 1.5, 0.5), ("G5", 2, 1), ("A5", 3, 1),
             ("G5", 4, 1.5), ("F5", 5.5, 0.5), ("C5", 6, 2),
             ("D5", 8, 1), ("F5", 9, 1), ("A#5", 10, 2),
             ("A5", 12, 1), ("G5", 13, 1), ("E5", 14, 2),
             ("F5", 16, 1.5), ("C5", 17.5, 0.5), ("G5", 18, 1), ("A5", 19, 1),
             ("A#5", 20, 1), ("A5", 21, 1), ("F5", 22, 2),
             ("D5", 24, 1), ("E5", 25, 1), ("F5", 26, 1), ("G5", 27, 1),
             ("E5", 28, 2), ("F5", 30, 2)]
ACORDES_NANA = [["F2", "C3", "A3"], ["D2", "A2", "F3"], ["A#1", "F2", "D3"], ["C2", "G2", "E3"],
                ["A1", "F2", "C3"], ["A#1", "F2", "D3"], ["G1", "D2", "A#2"], ["C2", "G2", "E3"]]


class Tempo:
    def __init__(self, bpm):
        self.bpm = bpm
        self.pulso = 60.0 / bpm

    def s(self, pulsos):
        return pulsos * self.pulso


def acorde(raiz, tipo="M"):
    """Notas de un acorde a partir de su raíz ('D3', 'm' menor, 'M' mayor, 'sus' suspendido)."""
    from sintetizador import NOTAS
    nombre, octava = raiz[:-1], int(raiz[-1])
    base = NOTAS[nombre] + octava * 12
    inter = {"M": (0, 4, 7), "m": (0, 3, 7), "sus": (0, 5, 7), "m7": (0, 3, 7, 10), "M7": (0, 4, 7, 11), "add9": (0, 4, 7, 14)}[tipo]
    nombres = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return [f"{nombres[(base + i) % 12]}{(base + i) // 12}" for i in inter]


def colchones(p, tempo, progresion, compas=4, brillo=1100, volumen=0.5, octava_bajo=None, fuerza_bajo=0.0):
    """Un colchón por acorde y, si se pide, el bajo en la raíz."""
    for i, (raiz, tipo) in enumerate(progresion):
        en = tempo.s(i * compas)
        dur = tempo.s(compas) + 1.2
        p.poner(colchon(acorde(raiz, tipo), dur, brillo, ataque=min(1.2, dur * 0.3), salida=1.2), en, volumen)
        if fuerza_bajo:
            nota = raiz[:-1] + str(octava_bajo or 2)
            p.poner(bajo(nota, tempo.s(compas) * 0.95), en, fuerza_bajo)


def melodia(p, tempo, notas, desde=0.0, instrumento=kalimba, volumen=0.6, pan=0.0, sostener=1.0):
    for (nota, en, dur) in notas:
        sonido = instrumento(nota, max(0.3, tempo.s(dur) * sostener + 0.4))
        p.poner(sonido, tempo.s(desde + en), volumen, pan=pan)


def transportar(notas, semitonos):
    from sintetizador import NOTAS
    nombres = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    out = []
    for (n, en, d) in notas:
        v = NOTAS[n[:-1]] + int(n[-1]) * 12 + semitonos
        out.append((f"{nombres[v % 12]}{v // 12}", en, d))
    return out


def arpegio(p, tempo, raiz, tipo, desde, pulsos, cada=0.5, octava_sube=True, volumen=0.3, instrumento=kalimba, pan=0.0, patron=(0, 1, 2, 1)):
    notas = acorde(raiz, tipo)
    if octava_sube:
        notas = notas + [n[:-1] + str(int(n[-1]) + 1) for n in notas[:1]]
    k = 0
    en = desde
    while en < desde + pulsos - 1e-6:
        nota = notas[patron[k % len(patron)] % len(notas)]
        p.poner(instrumento(nota, tempo.s(cada) + 0.8), tempo.s(en), volumen, pan=pan)
        k += 1
        en += cada


def final(p, bucle=True, sala=2.6, mezcla=0.3, brillo=6500):
    x = p.bucle() if bucle else p.entera()
    y = reverb(x, sala, mezcla, brillo)
    if bucle:
        # la cola de la sala vuelve al principio (el bucle no tiene costura)
        n = len(x)
        cola = y[n:]
        y = y[:n].copy()
        m = min(n, len(cola))
        y[:m] += cola[:m]
        costura = min(int(0.006 * SR), n // 8)
        if costura > 1:
            t_c = np.linspace(0.0, 1.0, costura)[:, None]
            y[-costura:] = y[-costura:] * (1.0 - t_c) + y[0:1] * t_c
    return y


def tocar(p, tempo, notas, desde=0.0, fuerza=0.5, sostener=None, pan=0.0, volumen=1.0):
    """Notas de piano: (nota, pulso, duración en pulsos). «sostener»: segundos que suena cada una (pedal)."""
    for (nota, en, d) in notas:
        dur = sostener if sostener else max(1.2, tempo.s(d) + 1.5)
        p.poner(piano(nota, dur, fuerza, suelta=None if sostener else tempo.s(d) + 0.6), tempo.s(desde + en), volumen, pan=pan)


def acordes(p, tempo, voces, desde=0.0, compas=4, fuerza=0.38, rasgueo=0.05, pan=0.0, volumen=1.0, repetir_en=None):
    """Un acorde de piano por compás (las notas un pelín escalonadas, como una mano tranquila).
    «repetir_en»: pulsos del compás en los que se vuelve a tocar (p. ej. (0, 2))."""
    for i, notas in enumerate(voces):
        if not notas:
            continue
        for k, en in enumerate(repetir_en or (0,)):
            f = fuerza * (1.0 if k == 0 else 0.75)
            p.poner(acorde_piano(notas, tempo.s(compas - en) + 2.5, f, rasgueo), tempo.s(desde + i * compas + en), volumen, pan=pan)


def arpegio_piano(p, tempo, notas, desde, pulsos, cada=0.5, fuerza=0.3, pan=0.0, sostener=3.0):
    k = 0
    en = desde
    while en < desde + pulsos - 1e-6:
        p.poner(piano(notas[k % len(notas)], sostener, fuerza * (1.0 if k % 2 == 0 else 0.85)), tempo.s(en), pan=pan)
        k += 1
        en += cada


def silencio_suave(x, segundos=2.0):
    """Para las piezas que no se repiten: se apagan despacio al final."""
    n = int(segundos * SR)
    x = x.copy()
    x[-n:] *= np.linspace(1, 0, n)[:, None] ** 2
    return x


# =============================================================================
# DESPERTAR (partida nueva): de un largo letargo a abrir los ojos
# Primero todo suena apagado y lejano, como desde dentro del sueño; luego el piano se aclara,
# llegan los pajarillos y suena el tema de Maisha.
# =============================================================================

def despertar():
    dur = 62.0
    p = Pista(dur)
    # 1) zumbido hondo y apagado que se va abriendo
    fondo = colchon(["D2", "A2", "D3", "A3"], 50, 1600, ataque=10.0, salida=8.0, fuerza=0.8)
    p.poner(barrido_bajo(fondo, 110, 2200, 96), 0.0, 0.7)
    # 2) un latido lento que se apaga
    for i, en in enumerate((3.5, 4.7, 6.1, 7.7, 9.5)):
        p.poner(tambor("D2", 0.8, 0.45 * (1 - i * 0.16), golpe=0.04), en)
    # 3) las primeras notas de piano, sueltas y lejanas (apagadas, como oídas medio dormida)
    for nota, en, f in (("A4", 10.5, 0.3), ("D5", 13.2, 0.3), ("F#4", 15.6, 0.28), ("E5", 18.0, 0.32)):
        p.poner(paso_bajo(piano(nota, 6.0, f), 1400), en, 1.0, pan=0.2 if nota in ("A4", "E5") else -0.2)
    # 4) se abren los ojos: acordes de piano y el tema de Maisha
    tempo = Tempo(60)
    inicio = 21.0
    voces = ACORDES_LETARGO
    for i, notas in enumerate(voces):
        p.poner(acorde_piano(notas, 7.0, 0.32, 0.11), inicio + tempo.s(i * 4))
    tema = TEMA_DESPERTAR
    for (nota, en, d) in tema:
        p.poner(piano(nota, 4.5, 0.45), inicio + tempo.s(en))
    # unas notas agudas que brillan al final, como luz entre las hojas
    for nota, en in (("A6", 29), ("F#6", 29.5), ("D6", 30), ("E6", 31)):
        p.poner(piano(nota, 3.0, 0.22), inicio + tempo.s(en), pan=0.3)
    # 5) se levanta una brisa suave entre las hojas secas (el mundo respira)
    brisa = crear_sonidos.brisa(46.0)
    rampa = np.clip((np.arange(len(brisa)) / SR - 2.0) / 14.0, 0, 1)[:, None] ** 1.5
    p.poner(brisa * rampa * 0.5, 9.0)
    x = final(p, bucle=False, sala=3.8, mezcla=0.34, brillo=5500)
    return silencio_suave(x[:int(dur * SR)], 6.0)


# =============================================================================
# KITOVU: piano solo, mucho espacio y silencio (como la música tranquila de los juegos de explorar)
# Melancólica pero con esperanza. No se repite seguida: suena, y vuelve al cabo de un rato.
# =============================================================================

def kitovu():
    tempo = Tempo(56)
    p = Pista(tempo.s(64) + 6)
    voces = ACORDES_RAICES
    for i, notas in enumerate(voces):
        p.poner(acorde_piano(notas, 9.0, 0.26, 0.16), tempo.s(i * 4))
    melodia_rh = MELODIA_RAICES
    for (nota, en, d) in melodia_rh:
        p.poner(piano(nota, 5.0, 0.36 if int(nota[-1]) < 6 else 0.26), tempo.s(en))
    # un colchón casi inaudible debajo, para que el silencio no sea vacío
    p.poner(colchon(["D3", "A3"], tempo.s(64), 700, 6.0, 6.0, 0.6), 0, 0.22)
    x = final(p, bucle=False, sala=4.2, mezcla=0.36, brillo=5000)
    return silencio_suave(x, 4.0)


# =============================================================================
# INICIO: el tema de Maisha al piano, cálido (como el tema de un pueblo de partida en un juego de aventuras)
# =============================================================================

def inicio():
    tempo = Tempo(66)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    voces = [["D2", "A2", "C#3"], ["F#2", "C#3", "E3"], ["G2", "D3", "F#3"], ["A1", "E2", "G2"],
             ["B1", "F#2", "A2"], ["F#2", "C#3", "E3"], ["G2", "D3", "F#3"], ["A1", "E2", "G2"]] * 2
    derecha = [["F#3", "A3", "E4"], ["A3", "C#4", "E4"], ["B3", "D4", "A4"], ["D4", "E4", "A4"],
               ["D4", "F#4", "A4"], ["A3", "C#4", "E4"], ["B3", "D4", "F#4"], ["C#4", "E4", "G4"]] * 2
    for i in range(16):
        base = i * 4
        # mano izquierda: la raíz y un arpegio suave en corcheas
        arpegio_piano(p, tempo, voces[i], base, 4, cada=1.0, fuerza=0.26, sostener=3.0)
        # mano derecha: el acorde en los tiempos 2 y 4, muy suave
        for en in (1.0, 3.0):
            p.poner(acorde_piano(derecha[i], 1.6, 0.16, 0.02), tempo.s(base + en))
    tema = TEMA_COMPLETO
    tocar(p, tempo, tema, desde=0, fuerza=0.46)
    tocar(p, tempo, transportar(tema, 12), desde=32, fuerza=0.36)
    tocar(p, tempo, tema, desde=32, fuerza=0.3)
    return final(p, sala=3.0, mezcla=0.3, brillo=5500)


# =============================================================================
# PRADOS DEL ECO: un camino luminoso (piano con ritmo, flauta y un poco de percusión)
# =============================================================================

def prados():
    tempo = Tempo(96)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    bajos = ["G2", "F#2", "E2", "C2", "A1", "B1", "C2", "D2"] * 2
    quintas = ["D3", "D3", "B2", "G2", "E2", "F#2", "G2", "A2"] * 2
    derecha = [["B3", "D4", "G4"], ["A3", "D4", "F#4"], ["B3", "D4", "G4"], ["B3", "E4", "G4"],
               ["C4", "E4", "G4"], ["A3", "D4", "F#4"], ["B3", "E4", "G4"], ["C4", "D4", "G4"]] * 2
    for i in range(16):
        base = i * 4
        p.poner(piano(bajos[i], 2.5, 0.34, suelta=tempo.s(1.8)), tempo.s(base))
        p.poner(piano(quintas[i], 2.0, 0.24, suelta=tempo.s(1.5)), tempo.s(base + 2))
        for en in (1.0, 1.5, 3.0, 3.5):
            p.poner(acorde_piano(derecha[i], 0.9, 0.15, 0.0) * 1.0, tempo.s(base + en))
    tema = TEMA_CAMINO
    melodia(p, tempo, tema, desde=0, instrumento=lambda n, d: flauta(n, d, 0.5), volumen=0.42, sostener=0.95)
    tocar(p, tempo, tema, desde=32, fuerza=0.42)
    melodia(p, tempo, transportar(tema, -12), desde=32, instrumento=lambda n, d: flauta(n, d, 0.4), volumen=0.25, sostener=0.95)
    for b in range(pulsos):
        p.poner(maraca(0.09, 0.14 if b % 2 else 0.1), tempo.s(b + 0.5))
        if b % 4 == 0 and b >= 32:
            p.poner(tambor("G2", 0.5, 0.22), tempo.s(b))
    return final(p, sala=2.6, mezcla=0.26, brillo=6000)


# =============================================================================
# CUNA DE MUSGO: un pueblo acogedor (piano saltarín y balafón)
# =============================================================================

def aldea():
    tempo = Tempo(88)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    bajos = ["C2", "A1", "D2", "G1", "F1", "E2", "D2", "G1"] * 2
    derecha = [["E3", "G3", "C4"], ["E3", "G3", "C4"], ["F3", "A3", "C4"], ["F3", "G3", "B3"],
               ["E3", "A3", "C4"], ["D3", "G3", "B3"], ["F3", "A3", "C4"], ["F3", "G3", "B3"]] * 2
    for i in range(16):
        base = i * 4
        p.poner(piano(bajos[i], 2.0, 0.34, suelta=tempo.s(0.9)), tempo.s(base))
        p.poner(piano(bajos[i][:-1] + str(int(bajos[i][-1]) + 1), 2.0, 0.26, suelta=tempo.s(0.9)), tempo.s(base + 2))
        for en in (1.0, 3.0):
            p.poner(acorde_piano(derecha[i], 1.2, 0.18, 0.0), tempo.s(base + en))
    motivo = MOTIVO_MUSGO
    melodia(p, tempo, motivo, desde=0, instrumento=balafon, volumen=0.45)
    tocar(p, tempo, motivo, desde=32, fuerza=0.42)
    melodia(p, tempo, transportar(motivo, 12)[::2], desde=32, instrumento=balafon, volumen=0.22, pan=0.3)
    for b in range(pulsos):
        if b % 2:
            p.poner(maraca(0.08, 0.12), tempo.s(b + 0.5))
    return final(p, sala=2.2, mezcla=0.24, brillo=6000)


# =============================================================================
# DENTRO DE LAS CASAS: una nana al piano
# =============================================================================

def interior():
    tempo = Tempo(62)
    p = Pista(tempo.s(32) + 6)
    izquierda = ACORDES_NANA
    for i in range(8):
        arpegio_piano(p, tempo, izquierda[i] + [izquierda[i][1]], i * 4, 4, cada=1.0, fuerza=0.24, sostener=4.0)
    tema = TEMA_NANA
    tocar(p, tempo, tema, desde=0, fuerza=0.36)
    x = final(p, bucle=False, sala=2.6, mezcla=0.3, brillo=4800)
    return silencio_suave(x, 4.0)


# =============================================================================
# COMBATE: dentro de una mancha de Giza (tensión contenida, no estridente)
# =============================================================================

def combate():
    tempo = Tempo(116)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    # voces de Giza: un acorde menor con una nota que roza (re-mi bemol)
    for i in range(4):
        p.poner(coro(["D3", "A3", "D#4"] if i % 2 else ["D3", "A3", "C4"], tempo.s(16) + 1.0, "u", 0.6), tempo.s(i * 16), 0.55)
    ostinato = ["D3", "D3", "F3", "D3", "G3", "D3", "F3", "E3"]
    for b in range(pulsos * 2):
        nota = ostinato[b % 8]
        if b >= 64 and b % 16 >= 8:
            nota = {"F3": "G#3", "G3": "A3"}.get(nota, nota)
        p.poner(balafon(nota, 0.5, 0.5 if b % 2 == 0 else 0.35), tempo.s(b * 0.5))
    for b in range(pulsos):
        p.poner(tambor("A2", 0.5, 0.45 if b % 4 == 0 else 0.25, golpe=0.35), tempo.s(b))
        if b % 4 == 3:
            p.poner(tambor("E3", 0.3, 0.2, golpe=0.6), tempo.s(b + 0.5))
        p.poner(maraca(0.07, 0.1), tempo.s(b + 0.5))
        if b % 8 == 0:
            p.poner(bajo("D2", tempo.s(3.5), 0.4), tempo.s(b))
    for (nota, en) in (("A5", 32), ("G5", 34), ("F5", 36), ("E5", 38), ("D5", 40)):
        p.poner(flauta(nota, tempo.s(2) + 0.2, 0.3), tempo.s(en), pan=0.3)
    return final(p, sala=1.8, mezcla=0.22, brillo=5000)


# =============================================================================
# JEFE: Mzizi, la raíz del Arco
# =============================================================================

def jefe():
    tempo = Tempo(124)
    pulsos = 80
    p = Pista(tempo.s(pulsos))
    for i in range(5):
        notas = [["D2", "A2", "D#3"], ["C2", "G2", "D3"], ["A#1", "F2", "D3"], ["C2", "G2", "D#3"], ["D2", "A2", "D#3"]][i]
        p.poner(coro(notas, tempo.s(16) + 1.0, "o", 0.8), tempo.s(i * 16), 0.6)
        p.poner(bajo(notas[0][:-1] + "1", tempo.s(16)), tempo.s(i * 16), 0.5)
    for b in range(pulsos):
        if b % 4 in (0, 2) or (b % 8 == 7):
            p.poner(taiko(0.9, 0.8 if b % 4 == 0 else 0.55), tempo.s(b))
        for s in range(2):
            p.poner(tambor("D3", 0.3, 0.25 if s == 0 else 0.15, golpe=0.6), tempo.s(b + s * 0.5))
    ostinato = ["D4", "F4", "D4", "D#4", "D4", "A3", "C4", "D#4"]
    for b in range(pulsos * 2):
        if b >= 16:
            p.poner(balafon(ostinato[b % 8], 0.4, 0.42), tempo.s(b * 0.5), pan=-0.2)
    # el grito de la raíz: el tema de Maisha retorcido, en voces
    retorcido = [("D5", 0, 2), ("A4", 2, 1), ("D#5", 3, 3), ("D5", 6, 2)]
    for vuelta in (32, 48, 64):
        melodia(p, tempo, retorcido, desde=vuelta, instrumento=lambda n, d: flauta(n, d, 0.5, vibrato=6.5), volumen=0.45, pan=0.25, sostener=0.95)
    return final(p, sala=2.2, mezcla=0.24, brillo=5000)


# =============================================================================
# FANFARRIAS
# =============================================================================

def purga():
    tempo = Tempo(100)
    p = Pista(4.5)
    for i, nota in enumerate(("D5", "F#5", "A5", "D6")):
        p.poner(kalimba(nota, 1.8, 0.7), tempo.s(i * 0.5))
    p.poner(colchon(acorde("D4", "add9"), 3.5, 2000, 0.2, 2.0), tempo.s(1.5), 0.6)
    for i, nota in enumerate(("A6", "D7", "F#7")):
        p.poner(campanita(nota, 1.5, 0.3), tempo.s(2 + i * 0.25), pan=(i - 1) * 0.5)
    return final(p, bucle=False, sala=2.5, mezcla=0.3)


def victoria():
    tempo = Tempo(96)
    p = Pista(9.0)
    frase = [("D5", 0, 0.5), ("D5", 0.5, 0.5), ("A5", 1, 1), ("F#5", 2, 0.5), ("A5", 2.5, 0.5), ("D6", 3, 2)]
    melodia(p, tempo, frase, instrumento=lambda n, d: flauta(n, d, 0.7), volumen=0.6)
    melodia(p, tempo, frase, volumen=0.5)
    for i, (raiz, tipo) in enumerate((("D3", "M"), ("G3", "M"), ("A3", "M"), ("D3", "add9"))):
        p.poner(colchon(acorde(raiz, tipo), tempo.s(2) + 1.5, 1800, 0.2, 1.2), tempo.s(i * 2), 0.5)
        p.poner(tambor("D2", 0.6, 0.4), tempo.s(i * 2))
    for i, nota in enumerate(("D6", "F#6", "A6", "D7")):
        p.poner(campanita(nota, 1.8, 0.3), tempo.s(6 + i * 0.25))
    return final(p, bucle=False, sala=2.8, mezcla=0.3)


def objeto():
    """¡Has conseguido algo! (como cuando en los Pokémon te dan un objeto)."""
    tempo = Tempo(140)
    p = Pista(3.0)
    frase = [("A4", 0, 0.5), ("D5", 0.5, 0.5), ("F#5", 1, 0.5), ("A5", 1.5, 0.5), ("D6", 2, 2)]
    melodia(p, tempo, frase, instrumento=balafon, volumen=0.45)
    tocar(p, tempo, frase, fuerza=0.5)
    p.poner(acorde_piano(["D3", "A3", "F#4", "A4"], 2.5, 0.32, 0.03), tempo.s(2))
    return final(p, bucle=False, sala=1.8, mezcla=0.25)


def tarea():
    """¡Tarea cumplida! (al entregar un encargo): un arpegio de piano que sube y se queda flotando."""
    tempo = Tempo(120)
    p = Pista(4.0)
    for i, nota in enumerate(("D4", "A4", "D5", "F#5", "A5")):
        p.poner(piano(nota, 3.0, 0.45), tempo.s(i * 0.5))
    p.poner(acorde_piano(["D3", "A3", "F#4"], 3.0, 0.3, 0.02), tempo.s(2))
    p.poner(kalimba("D6", 1.6, 0.35), tempo.s(2.5))
    return final(p, bucle=False, sala=2.4, mezcla=0.3)


# =============================================================================
# PARA EL COMIENZO: los recuerdos, la noche en la granja y el amanecer
# =============================================================================

def recuerdo():
    """«Un eco de antes»: suena cuando Maisha encuentra un recuerdo. Lejano, como un sueño."""
    tempo = Tempo(58)
    p = Pista(11.0)
    p.poner(colchon(["D3", "A3", "E4", "F#4"], 9.0, 1500, 3.0, 4.0, 0.9), 0.0, 0.5)
    for i, notas in enumerate(ACORDES_LETARGO[:2]):
        p.poner(paso_bajo(acorde_piano(notas, 7.0, 0.3, 0.18), 2200), tempo.s(i * 4))
    for (nota, en, d) in TEMA[:4]:
        p.poner(paso_bajo(piano(nota.replace("5", "6").replace("4", "5"), 4.0, 0.3), 3500), tempo.s(1 + en))
    x = final(p, bucle=False, sala=4.5, mezcla=0.45, brillo=4500)
    return silencio_suave(x, 3.0)


def noche():
    """«Noche en la granja»: la cena junto al fuego y el sueño. Piano muy suave, como una nana."""
    tempo = Tempo(56)
    p = Pista(tempo.s(32) + 6)
    for i in range(8):
        arpegio_piano(p, tempo, ACORDES_NANA[i] + [ACORDES_NANA[i][1]], i * 4, 4, cada=1.0, fuerza=0.2, sostener=4.5)
    tocar(p, tempo, transportar(TEMA_NANA, -12)[:12], desde=0, fuerza=0.28)
    tocar(p, tempo, TEMA_NANA[12:], desde=0, fuerza=0.24)
    x = final(p, bucle=False, sala=3.0, mezcla=0.34, brillo=4000)
    return silencio_suave(x, 5.0)


def amanece():
    """«Amanece»: la mañana siguiente. Un arpegio que sube despacio, como la luz por la ventana."""
    tempo = Tempo(72)
    p = Pista(10.0)
    for i, nota in enumerate(("G3", "D4", "A4", "B4", "D5", "F#5", "A5")):
        p.poner(piano(nota, 6.0, 0.32 + i * 0.02), tempo.s(i * 0.5))
    p.poner(acorde_piano(["G2", "D3", "B3", "F#4"], 7.0, 0.26, 0.08), tempo.s(3.5))
    p.poner(flauta("D6", tempo.s(4) + 0.5, 0.4), tempo.s(4))
    for i, nota in enumerate(("A6", "B6", "D7")):
        p.poner(campanita(nota, 2.0, 0.18), tempo.s(5 + i * 0.5), pan=(i - 1) * 0.4)
    x = final(p, bucle=False, sala=3.4, mezcla=0.32)
    return silencio_suave(x, 3.0)


## Los títulos de cada pieza (para buscarlas y reutilizarlas)
TITULOS = {
    "despertar": "Un largo letargo",
    "kitovu": "Raíces dormidas",
    "inicio": "El tema de Maisha",
    "prados": "Camino de los Prados",
    "aldea": "Cuna de Musgo",
    "interior": "Nana de la chimenea",
    "combate": "Manchas de Giza",
    "jefe": "Mzizi, la raíz del Arco",
    "purga": "Vuelve el color",
    "victoria": "El Arco despierta",
    "objeto": "¡Lo tengo!",
    "tarea": "Tarea cumplida",
    "recuerdo": "Un eco de antes",
    "noche": "Noche en la granja",
    "amanece": "Amanece",
    "bosque": "Hojas de cobre",
    "jefe_pembe": "Pembe, el ciervo de hierro",
    "cienaga": "Agua quieta",
    "jefe_konokono": "Konokono, la caracola de óxido",
    "campo": "Surcos de hierro",
    "jefe_cosechadora": "La Cosechadora Oxidada",
    "tienda": "El puesto de Tawi",
    "raiz_libre": "Raíz respira",
    "sendero": "El puente viejo",
    "pasarelas": "Entre juncos",
    "cobrizo": "La loma de cobre",
    "surcos": "Canción de siega",
    "canada": "Lo que la peña devuelve",
    "jefe_kambare": "Kambare, el siluro de cieno",
    "lago": "El agua que recuerda",
    "orilla": "La linterna en la orilla",
    "jefe_mamba": "Mamba, el cocodrilo de herrumbre",
    "embarcadero": "Canción de barqueros",
    "jefe_guardian": "La pesadilla del Guardián",
    "paso": "La casa del observatorio",
    "jefe_kuvu": "La seta que manda",
    "olvidado": "La montaña que no se mueve",
    "ruinas": "Las Ruinas",
    "jefe_arbol": "El miedo del Primer Árbol",
    "travesia": "Río arriba",
    "gruta": "Las raíces que duermen",
    "setas": "Lo que cae y vuelve",
}

# =============================================================================
# BOSQUE COBRIZO: arpa y viento (el tema de Maisha en mi dórico, otoñal)
# =============================================================================

## «Hojas de cobre»: el tema de Maisha en mi dórico, como lo cantaría el bosque
TEMA_COBRE = [("E5", 0, 1.5), ("B4", 1.5, 0.5), ("F#5", 2, 1), ("G5", 3, 1),
              ("F#5", 4, 1.5), ("E5", 5.5, 0.5), ("B4", 6, 2),
              ("C#5", 8, 1), ("E5", 9, 1), ("A5", 10, 1.5), ("G5", 11.5, 0.5),
              ("F#5", 12, 1), ("D5", 13, 1), ("E5", 14, 2),
              ("G5", 16, 1.5), ("F#5", 17.5, 0.5), ("E5", 18, 1), ("B4", 19, 1),
              ("C#5", 20, 1), ("D5", 21, 1), ("F#5", 22, 2),
              ("E5", 24, 1), ("D5", 25, 1), ("B4", 26, 1), ("A4", 27, 1),
              ("B4", 28, 4)]


def bosque():
    tempo = Tempo(76)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    # el arpa: arpegios que suben y bajan sobre mi menor (con la sexta mayor del dórico)
    progresion = [("E3", "m7"), ("C3", "M7"), ("D3", "M"), ("B2", "m7"), ("E3", "m7"), ("A2", "M"), ("C3", "M7"), ("D3", "sus")] * 2
    for i, (raiz, tipo) in enumerate(progresion):
        arpegio(p, tempo, raiz, tipo, i * 4, 4, cada=0.5, volumen=0.22, patron=(0, 1, 2, 3, 2, 1, 0, 2),
                instrumento=lambda n, d: kalimba(n, d + 0.6, 0.8), pan=-0.2)
        p.poner(bajo(raiz[:-1] + "2", tempo.s(4) * 0.95, 0.5), tempo.s(i * 4), 0.35)
    colchones(p, tempo, progresion, compas=4, brillo=900, volumen=0.22)
    # la melodía: primero la flauta sola, luego el piano con la flauta una octava abajo
    melodia(p, tempo, TEMA_COBRE, desde=0, instrumento=lambda n, d: flauta(n, d, 0.45, vibrato=5.0), volumen=0.4, sostener=0.95, pan=0.15)
    tocar(p, tempo, TEMA_COBRE, desde=32, fuerza=0.34, pan=0.1)
    melodia(p, tempo, transportar(TEMA_COBRE, -12), desde=32, instrumento=lambda n, d: flauta(n, d, 0.35), volumen=0.22, sostener=0.95)
    # hojas que caen: campanitas sueltas muy suaves
    rng = np.random.default_rng(14)
    for k in range(18):
        nota = ["B5", "E6", "F#6", "G6", "D6"][rng.integers(5)]
        p.poner(campanita(nota, 1.6, 0.18), tempo.s(rng.random() * pulsos), pan=rng.random() - 0.5)
    return final(p, sala=3.0, mezcla=0.32, brillo=5200)


# =============================================================================
# JEFE DEL BOSQUE: Pembe, el ciervo de hierro (galope y metal)
# =============================================================================

def jefe_pembe():
    tempo = Tempo(132)
    pulsos = 80
    p = Pista(tempo.s(pulsos))
    acords = [["E2", "B2", "F3"], ["C2", "G2", "D3"], ["D2", "A2", "E3"], ["C2", "G2", "D#3"], ["E2", "B2", "F3"]]
    for i in range(5):
        p.poner(coro(acords[i], tempo.s(16) + 1.0, "o", 0.75), tempo.s(i * 16), 0.55)
        p.poner(bajo(acords[i][0][:-1] + "1", tempo.s(16)), tempo.s(i * 16), 0.5)
    # el galope: tambores en tresillo (ta-ta-TAN)
    for b in range(pulsos):
        p.poner(tambor("E2", 0.3, 0.32, golpe=0.5), tempo.s(b))
        p.poner(tambor("B2", 0.25, 0.18, golpe=0.6), tempo.s(b + 1 / 3))
        p.poner(tambor("E2", 0.3, 0.24, golpe=0.5), tempo.s(b + 2 / 3))
        if b % 4 == 0:
            p.poner(taiko(1.0, 0.75), tempo.s(b))
    # el hierro: un ostinato de balafón áspero
    ostinato = ["E4", "G4", "E4", "F4", "E4", "B3", "D4", "F4"]
    for b in range(pulsos * 2):
        if b >= 16:
            p.poner(balafon(ostinato[b % 8], 0.4, 0.4), tempo.s(b * 0.5), pan=-0.25)
    # el bramido: el tema de Maisha retorcido, en la flauta
    retorcido = [("E5", 0, 2), ("B4", 2, 1), ("F5", 3, 3), ("E5", 6, 2)]
    for vuelta in (32, 48, 64):
        melodia(p, tempo, retorcido, desde=vuelta, instrumento=lambda n, d: flauta(n, d, 0.5, vibrato=6.5), volumen=0.45, pan=0.25, sostener=0.95)
    return final(p, sala=2.0, mezcla=0.22, brillo=5200)


# =============================================================================
# LA CIÉNAGA QUIETA: agua parada, niebla y gotas (re dórico, muy lento)
# El tema de Maisha aparece a medias, en el balafón, como un reflejo en el agua.
# =============================================================================

TEMA_AGUA = [("D5", 0, 3), ("A4", 3, 1), ("C5", 4, 2), ("F5", 6, 2), ("E5", 8, 3), ("D5", 11, 1), ("A4", 12, 4),
             ("D5", 16, 3), ("A4", 19, 1), ("C5", 20, 2), ("G5", 22, 2), ("F5", 24, 2), ("E5", 26, 2), ("D5", 28, 4)]


def cienaga():
    tempo = Tempo(62)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    progresion = [("D3", "m7"), ("G2", "M"), ("D3", "m7"), ("C3", "add9"), ("A2", "m7"), ("G2", "M"), ("F2", "M7"), ("A2", "sus")] * 2
    colchones(p, tempo, progresion, compas=4, brillo=700, volumen=0.3, octava_bajo=1, fuerza_bajo=0.3)
    # gotas: piano agudo, muy suave, notas sueltas del acorde
    rng = np.random.default_rng(31)
    for i, (raiz, tipo) in enumerate(progresion):
        notas = acorde(raiz, tipo)
        for k in range(2):
            n = notas[rng.integers(len(notas))]
            alta = n[:-1] + str(int(n[-1]) + 2)
            p.poner(piano(alta, 2.5, 0.18), tempo.s(i * 4 + 1 + k * 2 + rng.random() * 0.5), pan=rng.random() - 0.5)
    # el reflejo del tema: balafón (primera vuelta) y flauta grave con niebla (segunda)
    melodia(p, tempo, TEMA_AGUA, desde=0, instrumento=lambda n, d: balafon(n, d + 0.6, 0.6), volumen=0.35, pan=-0.1)
    melodia(p, tempo, transportar(TEMA_AGUA, -12), desde=32, instrumento=lambda n, d: flauta(n, d, 0.4, vibrato=4.0), volumen=0.32, sostener=0.95, pan=0.1)
    # algo grande respira bajo el barro: un coro muy bajo cada 16 pulsos
    for i in range(4):
        p.poner(coro(["D2", "A2"], tempo.s(8), "u", 0.5), tempo.s(i * 16 + 6), 0.25)
    return final(p, sala=3.6, mezcla=0.38, brillo=4200)


# =============================================================================
# JEFE DE LA CIÉNAGA: Konokono, la caracola de óxido (pesada, lenta, que rueda)
# =============================================================================

def jefe_konokono():
    tempo = Tempo(112)
    pulsos = 96
    p = Pista(tempo.s(pulsos))
    acords = [["D2", "A2", "D#3"], ["C2", "G2", "D3"], ["A#1", "F2", "C3"], ["C2", "G2", "D#3"], ["D2", "A2", "D#3"], ["F2", "C3", "G3"]]
    for i in range(6):
        p.poner(coro(acords[i], tempo.s(16) + 1.0, "o", 0.7), tempo.s(i * 16), 0.5)
        p.poner(bajo(acords[i][0][:-1] + "1", tempo.s(16)), tempo.s(i * 16), 0.55)
    # el arrastre: tambor grave en 3+3+2 (cada compás de 8 corcheas), y la concha que retumba
    for c in range(pulsos // 4):
        base = c * 4
        for k, (en, f) in enumerate(((0, 0.42), (1.5, 0.32), (3.0, 0.36))):
            p.poner(tambor("D2", 0.4, f, golpe=0.4), tempo.s(base + en))
        p.poner(tambor("A2", 0.25, 0.16, golpe=0.7), tempo.s(base + 2.5))
        if c % 2 == 0:
            p.poner(taiko(1.2, 0.7), tempo.s(base))
    # el óxido: ostinato de balafón (re frigio) desde el compás 4
    ostinato = ["D4", "D#4", "D4", "A3", "C4", "D#4", "D4", "F4"]
    for b in range(16, pulsos * 2):
        p.poner(balafon(ostinato[b % 8], 0.4, 0.38), tempo.s(b * 0.5), pan=-0.25)
    # el tema de Maisha, oxidado (con la segunda menor) y lento, en la flauta
    oxidado = [("D5", 0, 3), ("A4", 3, 1), ("D#5", 4, 3), ("F5", 7, 1), ("D#5", 8, 2), ("D5", 10, 2), ("A4", 12, 4)]
    for vuelta in (32, 48, 64, 80):
        melodia(p, tempo, oxidado, desde=vuelta, instrumento=lambda n, d: flauta(n, d, 0.5, vibrato=6.0), volumen=0.42, pan=0.25, sostener=0.95)
    # burbujas: campanitas graves sueltas
    rng = np.random.default_rng(8)
    for k in range(24):
        p.poner(campanita(["D5", "A4", "D#5", "F5"][rng.integers(4)], 0.6, 0.2), tempo.s(rng.random() * pulsos), pan=rng.random() - 0.5)
    return final(p, sala=2.2, mezcla=0.25, brillo=4800)


# =============================================================================
# EL CAMPO SEGADO: tenso y metálico (la mayor parte en la menor, con un traqueteo que no para)
# =============================================================================

TEMA_SURCO = [("A4", 0, 2), ("E4", 2, 1), ("A4", 3, 1), ("C5", 4, 3), ("B4", 7, 1), ("A4", 8, 2), ("G4", 10, 2), ("E4", 12, 4),
              ("A4", 16, 2), ("E4", 18, 1), ("A4", 19, 1), ("D5", 20, 3), ("C5", 23, 1), ("B4", 24, 2), ("G#4", 26, 2), ("A4", 28, 4)]


def campo():
    tempo = Tempo(84)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    progresion = [("A2", "m"), ("F2", "M"), ("D2", "m"), ("E2", "M")] * 4
    colchones(p, tempo, progresion, compas=4, brillo=800, volumen=0.28, octava_bajo=1, fuerza_bajo=0.35)
    # el traqueteo lejano de la máquina: tambor apagado en corcheas, con un acento cada compás
    for b in range(pulsos * 2):
        p.poner(tambor("A2", 0.18, 0.12 + (0.08 if b % 8 == 0 else 0.0), golpe=0.7), tempo.s(b * 0.5))
    # chapa: campanitas graves y desafinadas, sueltas (como hierros que suenan con el viento)
    rng = np.random.default_rng(42)
    for k in range(20):
        nota = ["A4", "D#5", "E5", "A#4"][rng.integers(4)]
        p.poner(campanita(nota, 1.2, 0.14), tempo.s(rng.random() * pulsos), pan=rng.random() - 0.5)
    # ostinato de balafón (la segunda menor da el aire inquieto)
    ost = ["A3", "E4", "A3", "A#3", "A3", "E4", "G3", "E4"]
    for b in range(16, pulsos * 2):
        p.poner(balafon(ost[b % 8], 0.4, 0.32), tempo.s(b * 0.5), pan=-0.25)
    # el tema del surco: flauta (primera vuelta) y piano con la flauta grave (segunda)
    melodia(p, tempo, TEMA_SURCO, desde=0, instrumento=lambda n, d: flauta(n, d, 0.45, vibrato=5.5), volumen=0.38, sostener=0.95, pan=0.15)
    tocar(p, tempo, TEMA_SURCO, desde=32, fuerza=0.3, pan=0.1)
    melodia(p, tempo, transportar(TEMA_SURCO, -12), desde=32, instrumento=lambda n, d: flauta(n, d, 0.35), volumen=0.2, sostener=0.95)
    return final(p, sala=2.6, mezcla=0.28, brillo=4800)


# =============================================================================
# JEFE DE RAÍZ: la Cosechadora Oxidada (pistones, vapor y, al final, el tema de Maisha que resiste)
# =============================================================================

def jefe_cosechadora():
    tempo = Tempo(124)
    pulsos = 128
    p = Pista(tempo.s(pulsos))
    acords = [["A1", "E2", "A2"], ["F1", "C2", "F2"], ["D1", "A1", "D2"], ["E1", "B1", "G#2"]]
    for i in range(pulsos // 8):
        a = acords[i % 4]
        p.poner(coro([n[:-1] + str(int(n[-1]) + 1) for n in a], tempo.s(8) + 0.8, "o", 0.6), tempo.s(i * 8), 0.45)
        p.poner(bajo(a[0], tempo.s(8)), tempo.s(i * 8), 0.55)
    # los pistones: taiko en 1 y 3, tambor en semicorcheas a ráfagas, y un «chas» de vapor en el 4
    for b in range(pulsos):
        if b % 2 == 0:
            p.poner(taiko(0.9, 0.7), tempo.s(b))
        for k in range(4 if (b // 16) % 2 else 2):
            p.poner(tambor("D3", 0.12, 0.12 + (0.06 if k == 0 else 0.0), golpe=0.8), tempo.s(b + k / (4 if (b // 16) % 2 else 2)))
        if b % 4 == 3:
            p.poner(paso_bajo(ruido_rosa(0.25), 6000) * np.linspace(1, 0, int(0.25 * SR)) * 0.12, tempo.s(b))
    # el bajo de hierro: un ostinato de balafón que sube y baja
    ost = ["A3", "A3", "C4", "A3", "D#4", "D4", "C4", "E4"]
    for b in range(32, pulsos * 2):
        p.poner(balafon(ost[b % 8], 0.35, 0.36), tempo.s(b * 0.5), pan=-0.3)
    # el tema de Maisha en menor (flauta) y, en la última vuelta, en mayor (resiste)
    tema_m = [("A5", 0, 2), ("E5", 2, 1), ("F5", 3, 1), ("G5", 4, 3), ("F5", 7, 1), ("E5", 8, 2), ("C5", 10, 2), ("E5", 12, 4)]
    tema_M = [("A5", 0, 2), ("E5", 2, 1), ("F#5", 3, 1), ("G#5", 4, 3), ("F#5", 7, 1), ("E5", 8, 2), ("C#6", 10, 2), ("A5", 12, 4)]
    for vuelta in (48, 64, 80):
        melodia(p, tempo, tema_m, desde=vuelta, instrumento=lambda n, d: flauta(n, d, 0.5, vibrato=6.0), volumen=0.4, pan=0.25, sostener=0.95)
    for vuelta in (96, 112):
        melodia(p, tempo, tema_M, desde=vuelta, instrumento=lambda n, d: flauta(n, d, 0.55, vibrato=5.0), volumen=0.42, pan=0.25, sostener=0.95)
        tocar(p, tempo, tema_M, desde=vuelta, fuerza=0.28, pan=-0.1)
    return final(p, sala=2.0, mezcla=0.22, brillo=5000)


# =============================================================================
# LA TIENDA DE TAWI: alegre y con gracia (re mayor, con un swing de mercado y trinos de pájaro en la flauta)
# =============================================================================

TEMA_TAWI = [("A5", 0, 0.5), ("F#5", 0.5, 0.5), ("A5", 1, 1), ("B5", 2, 0.5), ("A5", 2.5, 0.5), ("F#5", 3, 1),
             ("D5", 4, 0.5), ("E5", 4.5, 0.5), ("F#5", 5, 0.5), ("G5", 5.5, 0.5), ("A5", 6, 2),
             ("B5", 8, 0.5), ("A5", 8.5, 0.5), ("G5", 9, 1), ("E5", 10, 0.5), ("F#5", 10.5, 0.5), ("G5", 11, 1),
             ("F#5", 12, 0.5), ("E5", 12.5, 0.5), ("D5", 13, 0.5), ("C#5", 13.5, 0.5), ("D5", 14, 2)]


def tienda():
    tempo = Tempo(112)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    swing = 0.16                                                    # la corchea de después, un poco tarde
    progresion = [("D3", "M"), ("B2", "m"), ("G2", "M"), ("A2", "M")] * 4
    for i, (raiz, tipo) in enumerate(progresion):
        notas = acorde(raiz, tipo)
        # bajo saltarín de balafón (raíz y quinta)
        for k, (en, n) in enumerate(((0, notas[0]), (1.5, notas[2]), (2, notas[0]), (3 + swing, notas[2]))):
            p.poner(balafon(n[:-1] + "2", 0.35, 0.55), tempo.s(i * 4 + en))
        # acordes de kalimba a contratiempo
        for en in (1 + swing, 3):
            for n in notas:
                p.poner(kalimba(n[:-1] + "4", 0.6, 0.35), tempo.s(i * 4 + en))
    # maraca y tambor de mano con swing
    for b in range(pulsos):
        p.poner(maraca(0.1, 0.35), tempo.s(b))
        p.poner(maraca(0.08, 0.22), tempo.s(b + 0.5 + swing))
        if b % 2 == 0:
            p.poner(tambor("D3", 0.2, 0.25, golpe=0.5), tempo.s(b))
        else:
            p.poner(tambor("A3", 0.15, 0.18, golpe=0.7), tempo.s(b + 0.5 + swing))
    # el tema de Tawi: flauta (con trinos) y luego balafón agudo; y el tema de Maisha asomando al final
    melodia(p, tempo, TEMA_TAWI, desde=0, instrumento=lambda n, d: flauta(n, d, 0.5, vibrato=7.0), volumen=0.4, pan=0.2, sostener=0.9)
    melodia(p, tempo, TEMA_TAWI, desde=16, instrumento=lambda n, d: balafon(n, d + 0.3, 0.55), volumen=0.36, pan=-0.15)
    melodia(p, tempo, TEMA_TAWI, desde=32, instrumento=lambda n, d: flauta(n, d, 0.5, vibrato=7.0), volumen=0.4, pan=0.2, sostener=0.9)
    melodia(p, tempo, transportar(TEMA, 12), desde=48, instrumento=lambda n, d: kalimba(n, d + 0.5, 0.7), volumen=0.35, pan=0.1)
    melodia(p, tempo, transportar(TEMA, 12), desde=56, instrumento=lambda n, d: flauta(n, d, 0.45), volumen=0.3, pan=-0.1, sostener=0.9)
    # trinos de pájaro sueltos (la flauta muy aguda, rapidísima)
    rng = np.random.default_rng(23)
    for k in range(10):
        en = rng.random() * pulsos
        for j in range(4):
            p.poner(flauta(["A6", "B6"][j % 2], 0.07, 0.25), tempo.s(en) + j * 0.05, 0.25, pan=0.5)
    return final(p, sala=1.6, mezcla=0.2, brillo=7000)


# =============================================================================
# RAÍZ RESPIRA: el final del primer mundo (el tema de Maisha completo, cálido; no se repite)
# =============================================================================

def raiz_libre():
    tempo = Tempo(72)
    pulsos = 64
    p = Pista(tempo.s(pulsos) + 4)
    progresion = [("D3", "M"), ("A2", "M"), ("B2", "m"), ("G2", "M"), ("D3", "M"), ("A2", "M"), ("G2", "M"), ("A2", "sus")] * 2
    colchones(p, tempo, progresion, compas=4, brillo=1300, volumen=0.4, octava_bajo=2, fuerza_bajo=0.35)
    # arpegios de piano que suben como raíces que crecen
    for i, (raiz, tipo) in enumerate(progresion):
        notas = acorde(raiz, tipo)
        notas = [n[:-1] + str(int(n[-1]) + 1) for n in notas] + [notas[0][:-1] + str(int(notas[0][-1]) + 2)]
        arpegio_piano(p, tempo, notas, i * 4, 4, cada=0.5, fuerza=0.22, sostener=2.5)
    # el tema completo: piano primero, luego flauta y coro
    tocar(p, tempo, TEMA_COMPLETO, desde=0, fuerza=0.42, pan=0.05)
    melodia(p, tempo, TEMA_COMPLETO, desde=32, instrumento=lambda n, d: flauta(n, d, 0.55, vibrato=5.0), volumen=0.45, sostener=0.95, pan=0.15)
    for i in range(4):
        p.poner(coro(acorde(progresion[8 + i * 2][0], progresion[8 + i * 2][1]), tempo.s(8) + 1.0, "a", 0.5), tempo.s(32 + i * 8), 0.3)
    # campanitas al final (el bosque, la ciénaga y el campo vuelven a sonar)
    for k, nota in enumerate(("D6", "F#6", "A6", "D7")):
        p.poner(campanita(nota, 3.0, 0.4), tempo.s(62) + k * 0.25)
    return silencio_suave(final(p, bucle=False, sala=3.0, mezcla=0.32, brillo=6000), 4.0)


# =============================================================================
# SENDERO DEL PUENTE: «El puente viejo» (caminar tranquilo junto al río; kalimba que corre como el agua)
# =============================================================================

## Una melodía de camino, en sol mayor, que sube y baja como el arco de un puente
TEMA_PUENTE = [("D5", 0, 1), ("G5", 1, 1), ("A5", 2, 1), ("B5", 3, 2), ("A5", 5, 1), ("G5", 6, 2),
               ("E5", 8, 1), ("G5", 9, 1), ("A5", 10, 1.5), ("G5", 11.5, 0.5), ("D5", 12, 4),
               ("D5", 16, 1), ("G5", 17, 1), ("A5", 18, 1), ("B5", 19, 2), ("D6", 21, 1), ("B5", 22, 2),
               ("A5", 24, 1), ("B5", 25, 1), ("A5", 26, 1), ("F#5", 27, 1), ("G5", 28, 4)]


def sendero():
    tempo = Tempo(96)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    progresion = [("G3", "M"), ("E3", "m"), ("C3", "M"), ("D3", "M")] * 4
    colchones(p, tempo, progresion, compas=4, brillo=1000, volumen=0.26, octava_bajo=2, fuerza_bajo=0.32)
    # el río: un arpegio de kalimba que no para (como el agua bajo el puente)
    for i, (raiz, tipo) in enumerate(progresion):
        arpegio(p, tempo, raiz[:-1] + "4", tipo, i * 4, 4, cada=0.5, volumen=0.2, pan=-0.3, patron=(0, 1, 2, 3, 2, 1))
    # los pasos: maraca suave en las corcheas y un tambor grave en el 1
    for b in range(pulsos * 2):
        p.poner(maraca(0.1, 0.12 if b % 2 else 0.18), tempo.s(b * 0.5), pan=0.2)
        if b % 8 == 0:
            p.poner(tambor("G2", 0.3, 0.16, golpe=0.5), tempo.s(b * 0.5))
    # el tema: flauta la primera vuelta; kalimba y piano la segunda (con la flauta haciendo segunda voz)
    melodia(p, tempo, TEMA_PUENTE, desde=0, instrumento=lambda n, d: flauta(n, d, 0.42, vibrato=5.0), volumen=0.36, sostener=0.92, pan=0.15)
    tocar(p, tempo, TEMA_PUENTE, desde=32, fuerza=0.3, pan=0.1)
    melodia(p, tempo, TEMA_PUENTE, desde=32, instrumento=kalimba, volumen=0.3, pan=-0.1)
    melodia(p, tempo, transportar(TEMA_PUENTE, -5), desde=33, instrumento=lambda n, d: flauta(n, d, 0.3), volumen=0.14, sostener=0.9, pan=0.3)
    return final(p, sala=2.4, mezcla=0.26, brillo=5600)


# =============================================================================
# LAS PASARELAS: «Entre juncos» (un vals lento sobre el agua; gotas, balafón y flauta en re dórico)
# =============================================================================

## Un vals (3 pulsos por compás) que se mece como las tablas sobre el agua
TEMA_JUNCOS = [("A4", 0, 2), ("B4", 2, 1), ("C5", 3, 2), ("D5", 5, 1), ("E5", 6, 3), ("D5", 9, 1.5), ("C5", 10.5, 1.5),
               ("A4", 12, 2), ("G4", 14, 1), ("A4", 15, 3), ("B4", 18, 3), ("C5", 21, 2), ("B4", 23, 1),
               ("A4", 24, 2), ("B4", 26, 1), ("C5", 27, 2), ("E5", 29, 1), ("G5", 30, 3), ("F#5", 33, 1.5), ("E5", 34.5, 1.5),
               ("D5", 36, 2), ("C5", 38, 1), ("B4", 39, 3), ("A4", 42, 6)]


def pasarelas():
    tempo = Tempo(104)
    pulsos = 96
    p = Pista(tempo.s(pulsos))
    progresion = [("D3", "m"), ("D3", "m"), ("C3", "M"), ("G2", "M"), ("D3", "m"), ("A2", "m"), ("C3", "M"), ("D3", "m")] * 4
    colchones(p, tempo, progresion, compas=3, brillo=900, volumen=0.24, octava_bajo=2, fuerza_bajo=0.3)
    # el vals: bajo en el 1, balafón en el 2 y el 3 (como las tablas que crujen al pisarlas)
    for i, (raiz, tipo) in enumerate(progresion):
        notas = acorde(raiz[:-1] + "4", tipo)
        for k in (1, 2):
            p.poner(balafon(notas[k], 0.35, 0.22), tempo.s(i * 3 + k), pan=-0.25)
    # gotas de agua: campanitas agudas sueltas
    rng = np.random.default_rng(23)
    for k in range(40):
        p.poner(campanita(["A6", "D7", "E6", "C7"][rng.integers(4)], 0.6, 0.12), tempo.s(rng.random() * pulsos), pan=rng.random() - 0.5)
    # una rana lejana: tambor grave de vez en cuando
    for k in range(10):
        b = int(rng.random() * pulsos)
        p.poner(tambor("D2", 0.2, 0.1, golpe=0.4), tempo.s(b), pan=0.4)
        p.poner(tambor("D2", 0.2, 0.08, golpe=0.4), tempo.s(b + 0.3), pan=0.4)
    melodia(p, tempo, TEMA_JUNCOS, desde=0, instrumento=lambda n, d: flauta(n, d, 0.42, vibrato=4.5), volumen=0.36, sostener=0.9, pan=0.15)
    melodia(p, tempo, TEMA_JUNCOS, desde=48, instrumento=kalimba, volumen=0.32, pan=-0.1)
    tocar(p, tempo, TEMA_JUNCOS, desde=48, fuerza=0.22, pan=0.1)
    return final(p, sala=2.8, mezcla=0.3, brillo=5200)


# =============================================================================
# EL CAMINO COBRIZO: «La loma de cobre» (subiendo hacia el otoño: kalimba, flauta, campanillas y el pico del minero)
# =============================================================================

## En la menor (dórico, con el fa# que le da luz): una melodía que sube como el camino y baja como una hoja
TEMA_LOMA = [("A4", 0, 1), ("C5", 1, 1), ("D5", 2, 1), ("E5", 3, 2), ("G5", 5, 1), ("E5", 6, 2),
             ("D5", 8, 1), ("E5", 9, 1), ("F#5", 10, 1.5), ("E5", 11.5, 0.5), ("D5", 12, 1), ("B4", 13, 1), ("A4", 14, 2),
             ("C5", 16, 1), ("D5", 17, 1), ("E5", 18, 1), ("A5", 19, 2), ("G5", 21, 1), ("E5", 22, 2),
             ("F#5", 24, 1), ("E5", 25, 1), ("D5", 26, 1), ("B4", 27, 1), ("C5", 28, 1), ("B4", 29, 1), ("A4", 30, 2)]


def cobrizo():
    tempo = Tempo(92)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    progresion = [("A2", "m7"), ("E3", "m"), ("D3", "M"), ("A2", "m7"), ("C3", "M7"), ("G2", "M"), ("D3", "M"), ("A2", "m7")] * 2
    colchones(p, tempo, progresion, compas=4, brillo=950, volumen=0.24, octava_bajo=2, fuerza_bajo=0.3)
    # los pasos que suben: un arpegio de kalimba que va siempre hacia arriba
    for i, (raiz, tipo) in enumerate(progresion):
        arpegio(p, tempo, raiz[:-1] + "4", tipo, i * 4, 4, cada=0.5, volumen=0.18, pan=-0.3, patron=(0, 1, 2, 3, 1, 2, 3, 2))
    # el pico del minero, lejos, bajo tierra: dos golpecitos secos cada dos compases
    for c in range(0, pulsos, 8):
        p.poner(tambor("A3", 0.12, 0.07, golpe=0.9), tempo.s(c + 3), pan=0.45)
        p.poner(tambor("A3", 0.12, 0.05, golpe=0.9), tempo.s(c + 3.5), pan=0.45)
    # las campanillas de Fuko: tilín en los cruces
    rng = np.random.default_rng(29)
    for k in range(16):
        b = int(rng.random() * pulsos)
        nota = ["E6", "A6", "B6", "C#7"][rng.integers(4)]
        p.poner(campanita(nota, 0.9, 0.12), tempo.s(b), pan=rng.random() - 0.5)
        p.poner(campanita(nota, 0.7, 0.07), tempo.s(b + 0.25), pan=rng.random() - 0.5)
    # hojas que caen: campanitas graves muy suaves
    for k in range(10):
        p.poner(campanita(["E5", "A5", "D5"][rng.integers(3)], 1.8, 0.1), tempo.s(rng.random() * pulsos), pan=rng.random() - 0.5)
    melodia(p, tempo, TEMA_LOMA, desde=0, instrumento=lambda n, d: flauta(n, d, 0.42, vibrato=4.8), volumen=0.36, sostener=0.92, pan=0.15)
    tocar(p, tempo, TEMA_LOMA, desde=32, fuerza=0.3, pan=0.1)
    melodia(p, tempo, transportar(TEMA_LOMA, -12), desde=32, instrumento=lambda n, d: flauta(n, d, 0.3), volumen=0.16, sostener=0.9, pan=-0.2)
    return final(p, sala=2.6, mezcla=0.28, brillo=5400)


# =============================================================================
# LA SENDA DE LOS SURCOS: «Canción de siega» (6/8 de fiesta de campo: balafón, flauta y palmas, en re mixolidio)
# =============================================================================

## Una canción de trabajo que se vuelve baile (compás de 6/8: dos pulsos de tres corcheas)
TEMA_SIEGA = [("D5", 0, 1), ("E5", 1, 0.5), ("F#5", 1.5, 1), ("A5", 2.5, 0.5), ("G5", 3, 1), ("F#5", 4, 0.5), ("E5", 4.5, 1.5),
              ("D5", 6, 1), ("C5", 7, 0.5), ("D5", 7.5, 1), ("E5", 8.5, 0.5), ("F#5", 9, 3),
              ("A5", 12, 1), ("B5", 13, 0.5), ("A5", 13.5, 1), ("F#5", 14.5, 0.5), ("G5", 15, 1), ("E5", 16, 0.5), ("C5", 16.5, 1.5),
              ("D5", 18, 1), ("E5", 19, 0.5), ("C5", 19.5, 1), ("A4", 20.5, 0.5), ("D5", 21, 3)]


def surcos():
    tempo = Tempo(132)                      # (cada pulso es una corchea del 6/8)
    pulsos = 96
    p = Pista(tempo.s(pulsos))
    progresion = [("D3", "M"), ("B2", "m"), ("E3", "m"), ("G2", "M")] * 4
    colchones(p, tempo, progresion, compas=6, brillo=900, volumen=0.22, octava_bajo=2, fuerza_bajo=0.32)
    for i, (raiz, tipo) in enumerate(progresion):
        notas = acorde(raiz[:-1] + "4", tipo)
        for k in (0, 2, 3, 5):
            p.poner(balafon(notas[k % len(notas)], 0.3, 0.2 if k % 3 == 0 else 0.13), tempo.s(i * 6 + k), pan=-0.25)
    # palmas y un tambor en el 1 de cada compás (la fiesta)
    for b in range(0, pulsos, 3):
        p.poner(maraca(0.08, 0.16 if b % 6 == 0 else 0.1), tempo.s(b), pan=0.3)
        if b % 6 == 0:
            p.poner(tambor("D2", 0.25, 0.16, golpe=0.5), tempo.s(b))
    melodia(p, tempo, TEMA_SIEGA, desde=0, instrumento=lambda n, d: flauta(n, d, 0.42, vibrato=5.0), volumen=0.36, sostener=0.88, pan=0.15)
    melodia(p, tempo, TEMA_SIEGA, desde=24, instrumento=kalimba, volumen=0.3, pan=-0.1)
    melodia(p, tempo, TEMA_SIEGA, desde=48, instrumento=lambda n, d: flauta(n, d, 0.42, vibrato=5.0), volumen=0.34, sostener=0.88, pan=0.15)
    tocar(p, tempo, TEMA_SIEGA, desde=72, fuerza=0.3, pan=0.1)
    melodia(p, tempo, transportar(TEMA_SIEGA, -12), desde=72, instrumento=lambda n, d: flauta(n, d, 0.3), volumen=0.16, sostener=0.9, pan=-0.2)
    return final(p, sala=2.4, mezcla=0.26, brillo=5600)


# =============================================================================
# LA CAÑADA DEL ECO: «Lo que la peña devuelve» (flauta y su eco, kalimba, viento en la garganta, en mi dórico)
# =============================================================================

## El tema de Maisha en mi dórico, en frases cortas con silencios: en cada silencio, la peña la devuelve
FRASES_PENA = [
    [("E5", 0, 1.5), ("B4", 1.5, 0.5), ("F#5", 2, 1), ("G5", 3, 2)],
    [("F#5", 8, 1.5), ("E5", 9.5, 0.5), ("B4", 10, 1), ("D5", 11, 2)],
    [("A5", 16, 1.5), ("G5", 17.5, 0.5), ("F#5", 18, 1), ("E5", 19, 1), ("C#5", 20, 1)],
    [("D5", 24, 1), ("E5", 25, 1), ("B4", 26, 3)],
]
## La frase de Kimya: sin eco, larga y quieta (al final de la vuelta)
FRASE_QUIETA = [("B4", 48, 2), ("E5", 50, 2), ("D5", 52, 1), ("C#5", 53, 1), ("B4", 54, 6)]


def canada():
    tempo = Tempo(78)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    progresion = [("E2", "m7"), ("A2", "M"), ("E2", "m7"), ("D2", "M"), ("C2", "M7"), ("A2", "M"), ("B1", "m"), ("E2", "m7")] * 2
    colchones(p, tempo, progresion, compas=4, brillo=800, volumen=0.22, octava_bajo=1, fuerza_bajo=0.28)
    # la kalimba: un ostinato tranquilo, como gotas que caen en la garganta
    for i, (raiz, tipo) in enumerate(progresion):
        arpegio(p, tempo, raiz[:-1] + "4", tipo, i * 4, 4, cada=1.0, volumen=0.15, pan=-0.35, patron=(0, 2, 1, 2))
    # el viento que pasa por la garganta: ráfagas de ruido rosa que suben y bajan
    rng = np.random.default_rng(53)
    for k in range(7):
        d = 5.0 + rng.random() * 3
        n = int(d * SR)
        viento = ruido_rosa(d) * np.sin(np.linspace(0, np.pi, n)) ** 2
        p.poner(paso_banda(viento, 300 + rng.random() * 200, 1400) * 0.22, k * tempo.s(pulsos) / 7, pan=rng.random() - 0.5)
    # los cencerros de Mbuzi, lejos: clonc
    for k in range(6):
        b = 2 + k * 10 + rng.random() * 3
        p.poner(campanita(["E4", "B3", "G4"][k % 3], 1.6, 0.1), tempo.s(b), pan=0.5 - rng.random())
    # la flauta y su eco: cada frase vuelve dos veces, cada vez más suave, más lejos y del otro lado
    flauta_ = lambda n, d: flauta(n, d, 0.42, vibrato=4.6)
    eco_ = lambda n, d: flauta(n, d, 0.3, vibrato=3.0)
    for vuelta in (0, 32):
        for k, frase in enumerate(FRASES_PENA):
            if vuelta == 32 and k == 3:
                continue                            # (en la segunda vuelta, la última frase deja sitio a Kimya)
            melodia(p, tempo, frase, desde=vuelta, instrumento=flauta_, volumen=0.34, sostener=0.9, pan=-0.2)
            melodia(p, tempo, frase, desde=vuelta + 4, instrumento=eco_, volumen=0.13, sostener=0.9, pan=0.45)
            melodia(p, tempo, frase, desde=vuelta + 6, instrumento=eco_, volumen=0.05, sostener=0.9, pan=0.6)
    # la frase de Kimya: el piano, sin eco, sobre un acorde que se queda quieto
    tocar(p, tempo, FRASE_QUIETA, desde=0, fuerza=0.28, pan=0.0)
    p.poner(coro(["E3", "B3", "D4", "F#4"], tempo.s(12)), tempo.s(48), 0.06)
    return final(p, sala=3.4, mezcla=0.34, brillo=5000)


# =============================================================================
# KAMBARE, EL SILURO DE CIENO: pesada y húmeda (mi menor con el segundo grado bajado), con chapoteos y burbujas
# =============================================================================

def jefe_kambare():
    tempo = Tempo(104)
    pulsos = 96
    p = Pista(tempo.s(pulsos))
    acords = [["E2", "B2", "F3"], ["D2", "A2", "E3"], ["C2", "G2", "D3"], ["D2", "A2", "F3"], ["E2", "B2", "F3"], ["G2", "D3", "A3"]]
    for i in range(6):
        p.poner(coro(acords[i], tempo.s(16) + 1.0, "u", 0.7), tempo.s(i * 16), 0.5)
        p.poner(bajo(acords[i][0][:-1] + "1", tempo.s(16)), tempo.s(i * 16), 0.6)
    # el cieno: un tambor grave que se arrastra (1 . . 1 1 . 1 .) y un taiko en cada salto
    for c in range(pulsos // 4):
        base = c * 4
        for (en, f) in ((0, 0.45), (1.5, 0.3), (2.0, 0.34), (3.0, 0.28)):
            p.poner(tambor("E2", 0.45, f, golpe=0.35), tempo.s(base + en))
        if c % 4 == 3:
            p.poner(taiko(1.4, 0.8), tempo.s(base + 3.5))
    # el agua turbia: un ostinato de kalimba grave que sube y baja como una ola
    ostinato = ["E3", "F3", "B3", "F3", "E3", "D3", "C3", "D3"]
    for b in range(16, pulsos * 2):
        p.poner(kalimba(ostinato[b % 8], 0.5), tempo.s(b * 0.5), 0.3, pan=-0.3)
    # el tema de Maisha, enturbiado, en la flauta grave
    turbio = [("E5", 0, 3), ("B4", 3, 1), ("F5", 4, 3), ("G5", 7, 1), ("F5", 8, 2), ("E5", 10, 2), ("B4", 12, 4)]
    for vuelta in (32, 48, 64, 80):
        melodia(p, tempo, turbio, desde=vuelta, instrumento=lambda n, d: flauta(n, d, 0.48, vibrato=5.5), volumen=0.4, pan=0.25, sostener=0.95)
    # burbujas y chapoteos
    rng = np.random.default_rng(13)
    for k in range(30):
        p.poner(campanita(["E5", "B4", "F5", "G5"][rng.integers(4)], 0.5, 0.18), tempo.s(rng.random() * pulsos), pan=rng.random() - 0.5)
    for k in range(10):
        d = 0.3
        chap = paso_banda(ruido_rosa(d), 400, 2400) * np.exp(-np.linspace(0, 6, int(d * SR)))
        p.poner(chap * 0.25, tempo.s(rng.random() * pulsos), pan=rng.random() - 0.5)
    return final(p, sala=2.2, mezcla=0.27, brillo=4600)


# =============================================================================
# EL LAGO ESPEJO: «El agua que recuerda» (piano y su reflejo, voces suaves y gotas, en re mayor)
# =============================================================================

## Una frase del tema de Maisha y, después, su reflejo: las mismas notas al revés (como en el agua)
FRASE_ORILLA = [("D5", 0, 1.5), ("A4", 1.5, 0.5), ("E5", 2, 1), ("F#5", 3, 1), ("A5", 4, 2), ("G5", 6, 2)]


def _reflejo(frase, desde):
    """La frase al revés en el tiempo (la última nota primero), empezando en «desde»."""
    fin = max(en + d for (_, en, d) in frase)
    return [(n, desde + (fin - en - d), d) for (n, en, d) in frase]


def lago():
    tempo = Tempo(66)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    progresion = [("D3", "M7"), ("B2", "m7"), ("G2", "M7"), ("A2", "M"), ("D3", "M7"), ("F#2", "m7"), ("G2", "M7"), ("A2", "sus")] * 2
    colchones(p, tempo, progresion, compas=4, brillo=700, volumen=0.2, octava_bajo=2, fuerza_bajo=0.22)
    # la kalimba, muy lenta: una nota por pulso, como ondas que se abren
    for i, (raiz, tipo) in enumerate(progresion):
        arpegio(p, tempo, raiz[:-1] + "4", tipo, i * 4, 4, cada=1.0, volumen=0.12, pan=-0.35, patron=(0, 2, 1, 3))
    # voces sin palabras, lejos
    p.poner(coro(["D4", "A4", "F#4"], tempo.s(16)), tempo.s(16), 0.05)
    p.poner(coro(["G3", "D4", "B4"], tempo.s(16)), tempo.s(40), 0.05)
    # gotas de agua: campanitas agudas sueltas, cada una con su eco más suave
    rng = np.random.default_rng(71)
    for k in range(18):
        b = rng.random() * pulsos
        nota = ["A6", "F#6", "D6", "E6"][rng.integers(4)]
        p.poner(campanita(nota, 1.2, 0.1), tempo.s(b), pan=rng.random() - 0.5)
        p.poner(campanita(nota, 1.0, 0.04), tempo.s(b + 0.75), pan=rng.random() - 0.5)
    # el piano: la frase en la orilla y su reflejo en el agua (al revés, más suave y más grave)
    for vuelta in (0, 32):
        tocar(p, tempo, FRASE_ORILLA, desde=vuelta, fuerza=0.34, pan=-0.1)
        tocar(p, tempo, transportar(_reflejo(FRASE_ORILLA, 0), -12), desde=vuelta + 8, fuerza=0.22, pan=0.2)
        melodia(p, tempo, FRASE_ORILLA, desde=vuelta + 16, instrumento=lambda n, d: flauta(n, d, 0.36, vibrato=4.2),
                volumen=0.26, sostener=0.92, pan=0.15)
    # y la frase de Kimya, sin eco, al final de la vuelta
    tocar(p, tempo, FRASE_QUIETA, desde=0, fuerza=0.26, pan=0.0)
    return final(p, sala=3.6, mezcla=0.36, brillo=4800)


# =============================================================================
# LA ORILLA DE JUNCOS: «La linterna en la orilla» (una barcarola: la canción de las barcas, en seis, meciéndose)
# =============================================================================

## En sol mayor, a corcheas (6 por compás): sube como una barca que se aleja y baja como quien espera en la orilla
TEMA_LINTERNA = [("B4", 0, 3), ("D5", 3, 2), ("B4", 5, 1), ("G4", 6, 3), ("A4", 9, 2), ("B4", 11, 1),
                 ("C5", 12, 2), ("E5", 14, 1), ("D5", 15, 2), ("C5", 17, 1), ("B4", 18, 3), ("A4", 21, 3),
                 ("B4", 24, 3), ("D5", 27, 2), ("G5", 29, 1), ("F#5", 30, 3), ("D5", 33, 2), ("B4", 35, 1),
                 ("C5", 36, 2), ("E5", 38, 1), ("D5", 39, 2), ("B4", 41, 1), ("A4", 42, 3), ("F#4", 45, 1), ("G4", 46, 2)]


def orilla():
    tempo = Tempo(132)                 # cada pulso, una corchea: dos «remadas» por compás
    vuelta = 48
    pulsos = vuelta * 3
    p = Pista(tempo.s(pulsos))
    progresion = [("G2", "M"), ("E2", "m"), ("C3", "M"), ("D3", "M"), ("G2", "M"), ("B2", "m"), ("C3", "M"), ("D3", "sus")] * 3
    colchones(p, tempo, progresion, compas=6, brillo=800, volumen=0.2, octava_bajo=2, fuerza_bajo=0.26)
    # el vaivén: la kalimba sube y baja dentro de cada compás, como el agua contra la barca
    for i, (raiz, tipo) in enumerate(progresion):
        arpegio(p, tempo, raiz[:-1] + "4", tipo, i * 6, 6, cada=1.0, volumen=0.13, pan=-0.3, patron=(0, 1, 2, 3, 2, 1))
    # gotas y el remo: campanitas sueltas y, de vez en cuando, un golpe de agua suave
    rng = np.random.default_rng(81)
    for k in range(26):
        p.poner(campanita(["B6", "D7", "G6", "A6"][rng.integers(4)], 0.8, 0.09), tempo.s(rng.random() * pulsos), pan=rng.random() - 0.5)
    for compas in range(0, pulsos // 6, 2):
        chapoteo = paso_banda(ruido_rosa(0.5), 300, 1600) * np.exp(-np.arange(int(0.5 * SR)) / SR / 0.18)
        p.poner(chapoteo * 0.05, tempo.s(compas * 6 + 3), pan=0.35)
    # 1.ª vuelta: la flauta canta; 2.ª: el piano, y la kalimba le contesta una octava arriba; 3.ª: la flauta con las voces
    melodia(p, tempo, TEMA_LINTERNA, desde=0, instrumento=lambda n, d: flauta(n, d, 0.4, vibrato=4.4), volumen=0.32, sostener=0.92, pan=0.15)
    tocar(p, tempo, TEMA_LINTERNA, desde=vuelta, fuerza=0.32, pan=-0.05)
    melodia(p, tempo, transportar(TEMA_LINTERNA[::3], 12), desde=vuelta, instrumento=kalimba, volumen=0.14, pan=0.3)
    melodia(p, tempo, TEMA_LINTERNA, desde=vuelta * 2, instrumento=lambda n, d: flauta(n, d, 0.4, vibrato=4.4), volumen=0.3, sostener=0.92, pan=0.15)
    p.poner(coro(["G3", "D4", "B4"], tempo.s(24)), tempo.s(vuelta * 2), 0.05)
    p.poner(coro(["C4", "E4", "G4"], tempo.s(24)), tempo.s(vuelta * 2 + 24), 0.05)
    return final(p, sala=3.0, mezcla=0.32, brillo=5000)


def jefe_mamba():
    """El tema de la barcarola, pero en menor y a golpes: el río ya no mece, muerde."""
    tempo = Tempo(116)
    pulsos = 96
    p = Pista(tempo.s(pulsos))
    acords = [["G2", "D3", "A#3"], ["D#2", "A#2", "G3"], ["C2", "G2", "D#3"], ["D2", "A2", "F#3"]] * 2
    for i in range(6):
        a = acords[i % len(acords)]
        p.poner(coro(a, tempo.s(16) + 1.0, "o", 0.65), tempo.s(i * 16), 0.45)
        p.poner(bajo(a[0][:-1] + "1", tempo.s(16)), tempo.s(i * 16), 0.6)
    # las mandíbulas: dos golpes secos juntos (clac-clac) y un silencio, y un taiko cuando embiste
    for c in range(pulsos // 4):
        base = c * 4
        for (en, f) in ((0, 0.5), (0.5, 0.42), (2.0, 0.3), (3.0, 0.36), (3.5, 0.3)):
            p.poner(tambor("G2", 0.4, f, golpe=0.25), tempo.s(base + en))
        if c % 4 == 3:
            p.poner(taiko(1.4, 0.85), tempo.s(base + 2.5))
    # el agua: un ostinato de balafón grave en seis contra cuatro (el vaivén de la barcarola, torcido)
    ostinato = ["G3", "A#3", "D4", "A#3", "D#4", "D4"]
    for b in range(16, pulsos * 2):
        p.poner(balafon(ostinato[b % 6], 0.4, 0.22), tempo.s(b * 0.5), pan=-0.3)
    # la barcarola de la Orilla, en menor y más grave, en la flauta
    menor = [(n.replace("B4", "A#4").replace("B5", "A#5").replace("E5", "D#5").replace("F#5", "F#5"), en, d) for (n, en, d) in TEMA_LINTERNA[:12]]
    for vuelta in (32, 64):
        melodia(p, tempo, [(n, en * 0.5, d * 0.5) for (n, en, d) in menor], desde=vuelta, instrumento=lambda n, d: flauta(n, d, 0.48, vibrato=5.5),
                volumen=0.4, pan=0.25, sostener=0.95)
        melodia(p, tempo, [(n, en * 0.5 + 12, d * 0.5) for (n, en, d) in transportar(menor, -12)], desde=vuelta, instrumento=kalimba, volumen=0.3, pan=-0.2)
    rng = np.random.default_rng(17)
    for k in range(12):
        d = 0.3
        chap = paso_banda(ruido_rosa(d), 400, 2400) * np.exp(-np.linspace(0, 6, int(d * SR)))
        p.poner(chap * 0.25, tempo.s(rng.random() * pulsos), pan=rng.random() - 0.5)
    return final(p, sala=2.2, mezcla=0.27, brillo=4800)


# =============================================================================
# EL EMBARCADERO JUNCO: «Canción de barqueros» (una canción de trabajo: pregunta de la flauta, respuesta de las voces)
# =============================================================================

## En re dórico: la flauta pregunta (sube) y las voces contestan (bajan), como cuando se rema a la vez
PREGUNTA = [("D5", 0, 1), ("F5", 1, 1), ("G5", 2, 1), ("A5", 3, 2), ("G5", 5, 1), ("F5", 6, 2)]
RESPUESTA = [("A4", 0, 1), ("G4", 1, 1), ("F4", 2, 1), ("E4", 3, 1), ("D4", 4, 4)]
PREGUNTA_2 = [("A5", 0, 1), ("C6", 1, 1), ("B5", 2, 1), ("A5", 3, 2), ("G5", 5, 1), ("E5", 6, 2)]
RESPUESTA_2 = [("C5", 0, 1), ("A4", 1, 1), ("G4", 2, 1), ("E4", 3, 1), ("D4", 4, 4)]


def embarcadero():
    tempo = Tempo(96)
    pulsos = 128
    p = Pista(tempo.s(pulsos))
    progresion = [("D3", "m"), ("C3", "M"), ("D3", "m"), ("A2", "m"), ("D3", "m"), ("G2", "M"), ("A2", "m"), ("D3", "m")] * 4
    colchones(p, tempo, progresion, compas=4, brillo=900, volumen=0.2, octava_bajo=2, fuerza_bajo=0.3)
    # el remo: balafón en el 1 y el 3 (la pala entra en el agua) y un tambor sordo en el 2 y el 4 (el tirón)
    for i, (raiz, tipo) in enumerate(progresion):
        notas = acorde(raiz[:-1] + "4", tipo)
        for k in (0, 2):
            p.poner(balafon(notas[k // 2], 0.4, 0.26), tempo.s(i * 4 + k), pan=-0.25)
        for k in (1, 3):
            p.poner(tambor("D2", 0.3, 0.2, golpe=0.4), tempo.s(i * 4 + k))
        p.poner(maraca(0.1, 0.08), tempo.s(i * 4 + 3.5), pan=0.3)               # la cuerda que cruje
    # pregunta y respuesta, cuatro veces (cada vuelta de 32 pulsos)
    for vuelta in range(4):
        b = vuelta * 32
        preg, resp = (PREGUNTA, RESPUESTA) if vuelta % 2 == 0 else (PREGUNTA_2, RESPUESTA_2)
        for (desde, frase, quien) in ((b, preg, "flauta"), (b + 8, resp, "voces"), (b + 16, preg, "flauta"), (b + 24, resp, "voces")):
            if quien == "flauta":
                melodia(p, tempo, frase, desde=desde, instrumento=lambda n, d: flauta(n, d, 0.42, vibrato=4.6), volumen=0.34, sostener=0.92, pan=0.2)
            else:
                for (n, en, d) in frase:
                    p.poner(coro([n, transportar([(n, 0, 1)], -12)[0][0]], tempo.s(d) + 0.3, "o", 0.8), tempo.s(desde + en), 0.13)
        if vuelta >= 2:
            tocar(p, tempo, transportar(preg, -12), desde=b + 16, fuerza=0.22, pan=-0.1)
    # la campana del muelle, de vez en cuando, y el agua
    for b in (14, 62, 110):
        p.poner(campanita("A5", 2.4, 0.22), tempo.s(b), pan=0.4)
        p.poner(campanita("A5", 2.0, 0.08), tempo.s(b + 1.5), pan=0.45)
    rng = np.random.default_rng(91)
    for k in range(24):
        p.poner(campanita(["D7", "A6", "F6", "G6"][rng.integers(4)], 0.6, 0.08), tempo.s(rng.random() * pulsos), pan=rng.random() - 0.5)
    return final(p, sala=2.6, mezcla=0.28, brillo=5200)


def jefe_guardian():
    """Un coro grave y lento como un órgano de raíces, un latido de corazón que se acelera y, por encima, una frase
    de Maisha que intenta despertar al Guardián (y casi lo consigue)."""
    tempo = Tempo(92)
    pulsos = 96
    p = Pista(tempo.s(pulsos))
    acords = [["D2", "A2", "F3"], ["A#1", "F2", "D3"], ["G1", "D2", "A#2"], ["A1", "E2", "C#3"]] * 2
    for i in range(6):
        a = acords[i]
        p.poner(coro(a, tempo.s(16) + 1.2, "o", 0.75), tempo.s(i * 16), 0.5)
        p.poner(bajo(a[0][:-1] + "1", tempo.s(16)), tempo.s(i * 16), 0.6)
    # el latido: dos golpes (pum-pum) y silencio; en la segunda mitad, más seguido
    for c in range(pulsos // 4):
        base = c * 4
        p.poner(tambor("D2", 0.5, 0.55, golpe=0.3), tempo.s(base))
        p.poner(tambor("D2", 0.4, 0.4, golpe=0.3), tempo.s(base + 0.5))
        if c >= 12:
            p.poner(tambor("D2", 0.4, 0.4, golpe=0.3), tempo.s(base + 2))
            p.poner(tambor("D2", 0.3, 0.3, golpe=0.3), tempo.s(base + 2.5))
        if c % 4 == 3:
            p.poner(taiko(1.6, 0.85), tempo.s(base + 3))
    # la marioneta: balafón agudo y desafinado, como hilos que tiran
    for b in range(0, pulsos * 2, 3):
        p.poner(balafon(["A4", "A#4", "D5", "C#5"][b % 4], 0.3, 0.16), tempo.s(b * 0.5), pan=0.35)
    # la frase de Maisha en la flauta (el tema que intenta despertarlo)
    frase = [("D5", 0, 2), ("F5", 2, 1), ("A5", 3, 3), ("G5", 6, 1), ("F5", 7, 1), ("E5", 8, 4)]
    for vuelta in (32, 64):
        melodia(p, tempo, frase, desde=vuelta, instrumento=lambda n, d: flauta(n, d, 0.46, vibrato=5.0), volumen=0.4, pan=0.2, sostener=0.95)
        melodia(p, tempo, frase, desde=vuelta + 16, instrumento=kalimba, volumen=0.3, pan=-0.2)
    return final(p, sala=3.0, mezcla=0.35, brillo=4400)


def jefe_kuvu():
    """Hipnótica: la caja de música del Paso de Piedra, pero lenta y desafinada, que gira sin parar (lo que Kuvu le
    canta a Nungu: «descansa»); por debajo, tambores graves en tres, un zumbido de esporas que sube y baja y, en la
    segunda mitad, la flauta de Maisha que rompe el bucle."""
    tempo = Tempo(96)
    pulsos = 96
    p = Pista(tempo.s(pulsos))
    acords = [["D2", "A2", "F3"], ["C#2", "G#2", "E3"], ["D2", "A2", "F3"], ["A#1", "F2", "D3"]] * 2
    for i in range(6):
        a = acords[i]
        p.poner(coro(a, tempo.s(16) + 1.2, "u", 0.6), tempo.s(i * 16), 0.45)
        p.poner(bajo(a[0][:-1] + "1", tempo.s(16)), tempo.s(i * 16), 0.55)
    # tambores en tres (como un vaivén que adormece)
    for b in range(0, pulsos, 3):
        p.poner(tambor("D2", 0.45, 0.5, golpe=0.3), tempo.s(b))
        p.poner(tambor("A2", 0.25, 0.25, golpe=0.2), tempo.s(b + 2))
        if b % 12 == 9:
            p.poner(taiko(1.4, 0.7), tempo.s(b))
    # la caja de música desafinada: la pregunta del Paso, en bucle, un poco más grave cada vuelta
    caja = lambda n, d: campanita(n, max(d * 1.4, 1.0), 0.45)
    for k, desde in enumerate(range(0, pulsos, 8)):
        notas = transportar(PREGUNTA, -1 if k % 2 else 0)
        melodia(p, tempo, notas, desde=desde, instrumento=caja, volumen=0.22, pan=-0.3 + 0.6 * (k % 2))
    # el zumbido de las esporas
    d = tempo.s(pulsos)
    n = int(d * SR)
    u = np.linspace(0, 1, n)
    zumbido = ruido_rosa(d) * (0.5 + 0.5 * np.sin(u * 2 * np.pi * 6)) ** 2
    p.poner(paso_banda(zumbido, 500, 1600) * 0.08, 0.0)
    # la flauta de Maisha, que rompe el bucle
    frase = [("D5", 0, 1), ("F5", 1, 1), ("A5", 2, 2), ("C6", 4, 1), ("A5", 5, 1), ("G5", 6, 2), ("F5", 8, 1), ("E5", 9, 1), ("D5", 10, 2)]
    for vuelta in (48, 72):
        melodia(p, tempo, frase, desde=vuelta, instrumento=lambda n_, d_: flauta(n_, d_, 0.46, vibrato=5.0), volumen=0.38, pan=0.2, sostener=0.95)
    return final(p, sala=3.2, mezcla=0.35, brillo=4600)


NO_SE_REPITEN = ("raiz_libre", "despertar", "purga", "victoria", "objeto", "tarea", "recuerdo", "noche", "amanece", "kitovu", "interior")      # (kitovu e interior vuelven tras un silencio)
# =============================================================================
# PASO DE PIEDRA: misterio y curiosidad (re menor con la sexta mayor, dórico): una caja de música que se pregunta
# cosas, el tic-tac de un reloj que nadie ha parado, el viento del paso y la flauta que contesta
# =============================================================================

## «La casa del observatorio»: la pregunta (sube y se queda en el aire) y la respuesta (baja a casa)
PREGUNTA = [("D5", 0, 0.5), ("F5", 0.5, 0.5), ("E5", 1, 1), ("A5", 2, 1.5), ("G5", 3.5, 0.5),
            ("F5", 4, 0.5), ("E5", 4.5, 0.5), ("B4", 5, 1), ("C#5", 6, 2)]
RESPUESTA = [("A5", 0, 0.5), ("G5", 0.5, 0.5), ("F5", 1, 1), ("E5", 2, 1), ("C5", 3, 1),
             ("D5", 4, 1.5), ("A4", 5.5, 0.5), ("D5", 6, 2)]


def paso():
    tempo = Tempo(84)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    progresion = [("D2", "m"), ("G2", "M"), ("D2", "m"), ("A1", "M"), ("B1", "M"), ("G2", "M"), ("E2", "m7"), ("A1", "M")] * 2
    colchones(p, tempo, progresion, compas=4, brillo=700, volumen=0.2, octava_bajo=1, fuerza_bajo=0.25)
    # el tic-tac del reloj del observatorio: un clic agudo en cada pulso, más suave en los pares
    for b in range(pulsos):
        d = 0.02
        clic = paso_banda(ruido_rosa(d), 3000, 9000) * np.linspace(1, 0, int(d * SR)) ** 3
        p.poner(clic * (0.12 if b % 2 == 0 else 0.07), tempo.s(b), pan=0.25 if b % 2 else -0.25)
    # la caja de música: la pregunta, dos veces, y la respuesta
    caja = lambda n, d: campanita(n, max(d * 1.6, 1.2), 0.5)
    for vuelta in (0, 32):
        melodia(p, tempo, PREGUNTA, desde=vuelta, instrumento=caja, volumen=0.3, pan=-0.15)
        melodia(p, tempo, PREGUNTA, desde=vuelta + 8, instrumento=caja, volumen=0.26, pan=0.1)
        melodia(p, tempo, RESPUESTA, desde=vuelta + 16, instrumento=caja, volumen=0.3, pan=-0.1)
    # en la segunda mitad, la flauta contesta a la caja de música (una octava más abajo, con aire)
    flauta_ = lambda n, d: flauta(n, d, 0.4, vibrato=4.2)
    melodia(p, tempo, transportar(RESPUESTA, -12), desde=40, instrumento=flauta_, volumen=0.3, sostener=0.95, pan=0.2)
    melodia(p, tempo, transportar(PREGUNTA, -12), desde=56, instrumento=flauta_, volumen=0.22, sostener=0.95, pan=0.25)
    # la kalimba, abajo, en arpegios lentos
    for i, (raiz, tipo) in enumerate(progresion):
        if i % 2 == 1:
            arpegio(p, tempo, raiz[:-1] + "3", tipo, i * 4, 4, cada=1.0, volumen=0.12, pan=0.35, patron=(0, 1, 2, 1))
    # el viento del paso, a ráfagas, y alguna piedrecita que rueda
    rng = np.random.default_rng(71)
    for k in range(6):
        d = 4.0 + rng.random() * 3
        n = int(d * SR)
        viento = ruido_rosa(d) * np.sin(np.linspace(0, np.pi, n)) ** 2
        p.poner(paso_banda(viento, 250 + rng.random() * 200, 1200) * 0.2, k * tempo.s(pulsos) / 6, pan=rng.random() - 0.5)
    for k in range(4):
        t0 = tempo.s(6 + k * 15 + rng.random() * 4)
        for j in range(3):
            d = 0.03
            p.poner(paso_banda(ruido_rosa(d), 1200, 4000) * np.linspace(1, 0, int(d * SR)) * (0.1 - j * 0.03), t0 + j * 0.09, pan=0.4)
    return final(p, sala=2.8, mezcla=0.3, brillo=5200)


PIEZAS = {"despertar": despertar, "kitovu": kitovu, "inicio": inicio, "prados": prados, "aldea": aldea,
          "interior": interior, "combate": combate, "jefe": jefe, "purga": purga, "victoria": victoria, "objeto": objeto, "tarea": tarea,
          "recuerdo": recuerdo, "noche": noche, "amanece": amanece, "bosque": bosque, "jefe_pembe": jefe_pembe,
          "cienaga": cienaga, "jefe_konokono": jefe_konokono, "campo": campo, "jefe_cosechadora": jefe_cosechadora,
          "tienda": tienda, "raiz_libre": raiz_libre, "sendero": sendero, "pasarelas": pasarelas,
          "cobrizo": cobrizo, "surcos": surcos, "canada": canada, "jefe_kambare": jefe_kambare, "lago": lago,
          "orilla": orilla, "jefe_mamba": jefe_mamba,
          "embarcadero": embarcadero, "jefe_guardian": jefe_guardian, "paso": paso,
          "jefe_kuvu": jefe_kuvu}

# =============================================================================
# EL SENDERO OLVIDADO: «La montaña que no se mueve» (si menor sin resolver: frío, viento y silencio)
# =============================================================================

## La flauta sola: frases cortas que se quedan colgando (casi nunca vuelven a casa), con silencios largos entre ellas
FRASES_MONTANA = [
    [("F#5", 0, 2), ("E5", 2, 1), ("D5", 3, 1), ("B4", 4, 4)],
    [("D5", 0, 1.5), ("E5", 1.5, 0.5), ("F#5", 2, 2), ("A5", 4, 1), ("G5", 5, 3)],
    [("B5", 0, 2), ("A5", 2, 1), ("F#5", 3, 1), ("E5", 4, 2), ("D5", 6, 2)],
    [("E5", 0, 1), ("F#5", 1, 1), ("D5", 2, 2), ("C#5", 4, 4)],
]


def olvidado():
    tempo = Tempo(60)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    # acordes suspendidos que no terminan de resolver (como algo que no quiere acabar)
    progresion = [("B1", "sus"), ("G1", "M7"), ("E2", "m7"), ("F#1", "sus"), ("B1", "sus"), ("D2", "M7"), ("G1", "M7"), ("F#1", "sus")] * 2
    colchones(p, tempo, progresion, compas=4, brillo=520, volumen=0.18, octava_bajo=1, fuerza_bajo=0.3)
    rng = np.random.default_rng(91)
    # el viento de la montaña: ráfagas largas que suben y bajan, alguna con un silbido
    for k in range(9):
        d = 5.0 + rng.random() * 4
        n = int(d * SR)
        viento = ruido_rosa(d) * np.sin(np.linspace(0, np.pi, n)) ** 2
        p.poner(paso_banda(viento, 220 + rng.random() * 160, 1100) * 0.26, k * tempo.s(pulsos) / 9, pan=rng.random() - 0.5)
        if k % 3 == 1:
            p.poner(paso_banda(viento, 1800, 2600) * 0.05, k * tempo.s(pulsos) / 9 + 1.0, pan=rng.random() - 0.5)
    # campanillas de hielo, sueltas y muy agudas (cristales que chocan)
    for k in range(22):
        b = rng.random() * pulsos
        nota = ["B6", "F#6", "D7", "C#7", "A6"][rng.integers(5)]
        p.poner(campanita(nota, 1.4, 0.07), tempo.s(b), pan=rng.random() - 0.5)
    # la flauta sola, con silencios largos entre frase y frase
    flauta_ = lambda n, d: flauta(n, d, 0.4, vibrato=3.8)
    for k, frase in enumerate(FRASES_MONTANA):
        melodia(p, tempo, frase, desde=4 + k * 14, instrumento=flauta_, volumen=0.3, sostener=0.92, pan=-0.15)
    # voces sin palabras, muy lejos (lo que se quedó quieto en la montaña)
    p.poner(coro(["B2", "F#3", "D4"], tempo.s(16)), tempo.s(20), 0.05)
    p.poner(coro(["G2", "D3", "B3"], tempo.s(16)), tempo.s(44), 0.05)
    # y la frase de Kimya, sin eco, al final
    tocar(p, tempo, FRASE_QUIETA, desde=56, fuerza=0.22, pan=0.0)
    return final(p, sala=3.8, mezcla=0.4, brillo=4200)


PIEZAS["olvidado"] = olvidado



# =============================================================================
# LAS RUINAS DEL PRIMER ÁRBOL: «Las Ruinas» (solemne, re menor, coro lejano) y «El miedo del Primer Árbol» (el jefe
# final: un pulso grave que no para, y por encima vuelven, una a una, las frases de los ecos)
# =============================================================================

def ruinas():
    tempo = Tempo(56)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    progresion = [("D2", "m"), ("A#1", "M7"), ("G1", "m7"), ("A1", "sus")] * 4
    colchones(p, tempo, progresion, compas=4, brillo=600, volumen=0.2, octava_bajo=1, fuerza_bajo=0.32)
    p.poner(coro(["D3", "A3", "F4"], tempo.s(16)), tempo.s(0), 0.07)
    p.poner(coro(["A#2", "F3", "D4"], tempo.s(16)), tempo.s(16), 0.07)
    p.poner(coro(["G2", "D3", "A#3"], tempo.s(16)), tempo.s(32), 0.07)
    p.poner(coro(["A2", "E3", "C#4"], tempo.s(16)), tempo.s(48), 0.07)
    rng = np.random.default_rng(97)
    for k in range(7):
        d = 6.0 + rng.random() * 3
        n = int(d * SR)
        viento = ruido_rosa(d) * np.sin(np.linspace(0, np.pi, n)) ** 2
        p.poner(paso_banda(viento, 200, 900) * 0.16, k * tempo.s(pulsos) / 7, pan=rng.random() - 0.5)
    # el piano, muy despacio: la frase de la orilla, grave, como un recuerdo lejano
    tocar(p, tempo, transportar(FRASE_ORILLA, -12), desde=8, fuerza=0.24, pan=-0.1)
    tocar(p, tempo, FRASE_QUIETA, desde=40, fuerza=0.22, pan=0.1)
    return final(p, sala=4.0, mezcla=0.42, brillo=4000)


def jefe_arbol():
    tempo = Tempo(100)
    pulsos = 128
    p = Pista(tempo.s(pulsos))
    progresion = [("D2", "m"), ("D2", "m"), ("A#1", "M"), ("C2", "M"), ("D2", "m"), ("D2", "m"), ("G1", "m"), ("A1", "M")] * 4
    colchones(p, tempo, progresion, compas=4, brillo=900, volumen=0.24, octava_bajo=1, fuerza_bajo=0.42)
    # el pulso grave: un latido que no para (el miedo)
    def latido_(fuerza):
        d = 0.32
        t = np.linspace(0, d, int(d * SR), endpoint=False)
        f = 42 + 60 * np.exp(-t * 28)                      # el tono cae, como un golpe de corazón
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * fuerza
    for b in range(0, pulsos, 2):
        p.poner(latido_(0.55), tempo.s(b))
        p.poner(latido_(0.32), tempo.s(b + 0.5))
    # las campanillas de hielo, nerviosas
    rng = np.random.default_rng(103)
    for k in range(40):
        b = rng.random() * pulsos
        p.poner(campanita(["D7", "A6", "F6", "E7"][rng.integers(4)], 0.8, 0.06), tempo.s(b), pan=rng.random() - 0.5)
    # por encima, una a una, las frases de los ecos (la flauta y la kalimba), cada vez más claras
    flauta_ = lambda n, d: flauta(n, d, 0.4, vibrato=4.4)
    for k, frase in enumerate(FRASES_MONTANA):
        melodia(p, tempo, frase, desde=8 + k * 28, instrumento=flauta_, volumen=0.22 + k * 0.04, sostener=0.9, pan=-0.2 + k * 0.1)
    tocar(p, tempo, FRASE_QUIETA, desde=112, fuerza=0.3, pan=0.0)
    return final(p, sala=2.8, mezcla=0.3, brillo=6000)


PIEZAS["ruinas"] = ruinas
PIEZAS["jefe_arbol"] = jefe_arbol


# =============================================================================
# LA TRAVESÍA, LA GRUTA Y LA CUEVA DE LAS SETAS (cada una con su música)
# =============================================================================

def travesia():
    """«Río arriba»: el tema de la linterna (la despedida de Mauti), ahora decidido, en re mayor y río arriba: la
    pértiga de Bata marca el compás (un golpe de agua en cada uno) y la corriente empuja por debajo."""
    tempo = Tempo(150)                 # corcheas: seis por compás, como la barcarola, pero con más prisa
    vuelta = 48
    pulsos = vuelta * 3
    p = Pista(tempo.s(pulsos))
    progresion = [("D3", "M"), ("B2", "m"), ("G2", "M"), ("A2", "M"), ("D3", "M"), ("F#2", "m"), ("G2", "M"), ("A2", "sus")] * 3
    colchones(p, tempo, progresion, compas=6, brillo=950, volumen=0.2, octava_bajo=2, fuerza_bajo=0.32)
    for i, (raiz, tipo) in enumerate(progresion):
        arpegio(p, tempo, raiz[:-1] + "4", tipo, i * 6, 6, cada=1.0, volumen=0.14, pan=-0.3, patron=(0, 1, 2, 1, 2, 3))
    # la pértiga: un golpe hondo de agua al empezar cada compás y uno suave a la mitad
    rng = np.random.default_rng(111)
    for compas in range(pulsos // 6):
        golpe = paso_banda(ruido_rosa(0.4), 120, 900) * np.exp(-np.arange(int(0.4 * SR)) / SR / 0.12)
        p.poner(golpe * 0.12, tempo.s(compas * 6), pan=0.3)
        p.poner(golpe * 0.05, tempo.s(compas * 6 + 3), pan=0.3)
    # la corriente, por debajo (ruido que sube y baja despacio)
    d = tempo.s(pulsos)
    n = int(d * SR)
    corriente = paso_banda(ruido_rosa(d), 200, 1200) * (0.6 + 0.4 * np.sin(np.linspace(0, 9 * np.pi, n)))
    p.poner(corriente * 0.05, 0.0)
    for k in range(20):
        p.poner(campanita(["A6", "D7", "F#6"][rng.integers(3)], 0.7, 0.07), tempo.s(rng.random() * pulsos), pan=rng.random() - 0.5)
    tema = transportar(TEMA_LINTERNA, -5)               # de sol a re
    melodia(p, tempo, tema, desde=0, instrumento=lambda n, d: flauta(n, d, 0.42, vibrato=4.8), volumen=0.32, sostener=0.88, pan=0.15)
    tocar(p, tempo, tema, desde=vuelta, fuerza=0.34, pan=-0.05)
    melodia(p, tempo, transportar(tema, 12)[::2], desde=vuelta, instrumento=kalimba, volumen=0.14, pan=0.3)
    melodia(p, tempo, tema, desde=vuelta * 2, instrumento=lambda n, d: flauta(n, d, 0.42, vibrato=4.8), volumen=0.3, sostener=0.88, pan=0.15)
    p.poner(coro(["D4", "A4", "F#4"], tempo.s(24)), tempo.s(vuelta * 2), 0.05)
    return final(p, sala=2.6, mezcla=0.28, brillo=5600)


def gruta():
    """«Las raíces que duermen»: casi a oscuras. Un bordón grave, las raíces que roncan (respiraciones lentas y hondas),
    gotas que caen en charcos y, muy bajito, el tema de Maisha en menor, como quien camina de puntillas."""
    tempo = Tempo(52)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    progresion = [("D2", "m"), ("D2", "m"), ("A#1", "M"), ("A1", "sus")] * 4
    colchones(p, tempo, progresion, compas=4, brillo=380, volumen=0.2, octava_bajo=1, fuerza_bajo=0.34)
    # los ronquidos de las raíces: cada cuatro pulsos, una respiración (sube despacio, baja de golpe)
    for b in range(0, pulsos, 4):
        d = tempo.s(3.2)
        n = int(d * SR)
        forma = np.concatenate([np.linspace(0, 1, int(n * 0.7)) ** 2, np.linspace(1, 0, n - int(n * 0.7)) ** 0.5])
        p.poner(paso_banda(ruido_rosa(d), 60, 320) * forma * 0.2, tempo.s(b + 0.5), pan=(b % 8 - 4) / 8.0)
    # gotas que caen en los charcos, con su eco
    rng = np.random.default_rng(121)
    for k in range(16):
        b = rng.random() * pulsos
        nota = ["A5", "D6", "F5", "E6"][rng.integers(4)]
        p.poner(campanita(nota, 1.0, 0.09), tempo.s(b), pan=rng.random() - 0.5)
        p.poner(campanita(nota, 0.9, 0.035), tempo.s(b + 0.6), pan=rng.random() - 0.5)
    # el tema en menor, de puntillas: el piano, muy suave y con mucho aire
    tocar(p, tempo, TEMA_MENOR, desde=8, fuerza=0.18, pan=-0.1)
    tocar(p, tempo, transportar(TEMA_MENOR, -12), desde=40, fuerza=0.16, pan=0.1)
    p.poner(coro(["D3", "A3", "F4"], tempo.s(16)), tempo.s(24), 0.035)
    return final(p, sala=4.2, mezcla=0.46, brillo=3400)


def setas():
    """«Lo que cae y vuelve»: la cueva de las setas de Kimya. Una kalimba que da vueltas (lo que cae vuelve a la
    tierra), burbujitas de esporas que suben, un bajo que respira y, al final, la frase de Kimya."""
    tempo = Tempo(76)
    pulsos = 64
    p = Pista(tempo.s(pulsos))
    progresion = [("E2", "m7"), ("A2", "M"), ("E2", "m7"), ("F#2", "m7"), ("C2", "M7"), ("A2", "M"), ("B1", "sus"), ("E2", "m7")] * 2
    colchones(p, tempo, progresion, compas=4, brillo=650, volumen=0.18, octava_bajo=1, fuerza_bajo=0.26)
    # la kalimba da vueltas: un patrón que sube y vuelve a empezar desde abajo
    for i, (raiz, tipo) in enumerate(progresion):
        arpegio(p, tempo, raiz[:-1] + "4", tipo, i * 4, 4, cada=0.5, volumen=0.12, pan=-0.25, patron=(0, 1, 2, 3, 2, 1, 0, 2))
    # burbujitas de esporas: notas muy agudas y cortas que suben en grupitos de tres
    rng = np.random.default_rng(131)
    for k in range(18):
        b = rng.random() * (pulsos - 2)
        base = ["E6", "G6", "B6"]
        for j, nota in enumerate(base):
            p.poner(campanita(nota, 0.35, 0.05), tempo.s(b + j * 0.25), pan=rng.random() - 0.5)
    # voces lejanas y la frase de Kimya (sin eco), al final
    p.poner(coro(["E3", "B3", "G4"], tempo.s(16)), tempo.s(16), 0.045)
    p.poner(coro(["C3", "G3", "E4"], tempo.s(16)), tempo.s(32), 0.045)
    melodia(p, tempo, FRASES_PENA[0], desde=20, instrumento=lambda n, d: flauta(n, d, 0.34, vibrato=3.6), volumen=0.22, sostener=0.9, pan=0.2)
    tocar(p, tempo, FRASE_QUIETA, desde=0, fuerza=0.24, pan=0.0)
    return final(p, sala=3.6, mezcla=0.38, brillo=4600)


PIEZAS["travesia"] = travesia
PIEZAS["gruta"] = gruta
PIEZAS["setas"] = setas


# =============================================================================
# SIGILIA (mundo 2): una caja de música que se ha quedado fría. Vals lento en si menor; campanitas como de caja de
# música, el roce del papel y el viento. «El tema de Sigilia» servirá para la ciudad y para el Grimorio.
# =============================================================================

## «El tema de Sigilia»: un vals (3/4) en si menor que sube como quien busca una palabra y baja al recordarla
TEMA_SIGILIA = [("F#5", 0, 2), ("E5", 2, 1), ("D5", 3, 1.5), ("E5", 4.5, 0.5), ("F#5", 5, 1),
                ("A5", 6, 2), ("G5", 8, 1), ("F#5", 9, 3),
                ("E5", 12, 1), ("F#5", 13, 1), ("G5", 14, 1), ("A5", 15, 1.5), ("B5", 16.5, 0.5), ("A5", 17, 1),
                ("F#5", 18, 1), ("E5", 19, 1), ("C#5", 20, 1), ("D5", 21, 3)]


def escarcha():
    """«La nieve que escribe»: el Paso de la Escarcha. Una caja de música (campanitas en vals) que suena helada, con el
    viento que sube y baja, el roce de páginas que pasan volando y, por encima, el tema de Sigilia en la flauta; en la
    segunda vuelta lo recoge el piano, más cálido (como un farol que se enciende)."""
    tempo = Tempo(84)
    pulsos = 96
    p = Pista(tempo.s(pulsos))
    progresion = [("B1", "m"), ("G1", "M"), ("D2", "M"), ("A1", "M"), ("B1", "m"), ("E2", "m"), ("G1", "M"), ("A1", "sus"),
                  ("B1", "m"), ("G1", "M"), ("D2", "M"), ("F#1", "m"), ("B1", "m"), ("E2", "m"), ("A1", "sus"), ("B1", "m")] * 2
    colchones(p, tempo, progresion, compas=3, brillo=600, volumen=0.16, octava_bajo=1, fuerza_bajo=0.26)
    # la caja de música: en cada compás, la raíz abajo y dos campanitas del acorde (un-dos-tres)
    for i, (raiz, tipo) in enumerate(progresion):
        notas = acorde(raiz[:-1] + "5", tipo)
        p.poner(campanita(raiz[:-1] + "4", 1.6, 0.11), tempo.s(i * 3), pan=-0.2)
        p.poner(campanita(notas[1], 1.0, 0.07), tempo.s(i * 3 + 1), pan=0.15)
        p.poner(campanita(notas[2 % len(notas)], 1.0, 0.07), tempo.s(i * 3 + 2), pan=0.25)
    rng = np.random.default_rng(141)
    # el viento: ráfagas largas que suben y bajan
    for k in range(8):
        d = 5.0 + rng.random() * 3
        n = int(d * SR)
        viento = ruido_rosa(d) * np.sin(np.linspace(0, np.pi, n)) ** 2
        p.poner(paso_banda(viento, 260 + rng.random() * 140, 1200) * 0.2, k * tempo.s(pulsos) / 8, pan=rng.random() - 0.5)
    # el roce de las páginas: soplos cortos y agudos, de dos en dos (aleteo)
    for k in range(14):
        b = rng.random() * (pulsos - 1)
        for j in range(2):
            d = 0.12
            n = int(d * SR)
            roce = paso_banda(ruido_rosa(d), 2500, 6000) * np.sin(np.linspace(0, np.pi, n))
            p.poner(roce * 0.06, tempo.s(b) + j * 0.14, pan=rng.random() - 0.5)
    # el tema: primero la flauta (fría), luego el piano (como un farol que se enciende)
    flauta_ = lambda n, d: flauta(n, d, 0.38, vibrato=4.2)
    melodia(p, tempo, TEMA_SIGILIA, desde=6, instrumento=flauta_, volumen=0.28, sostener=0.9, pan=-0.1)
    tocar(p, tempo, transportar(TEMA_SIGILIA, -12), desde=54, fuerza=0.22, pan=0.1)
    p.poner(coro(["B2", "F#3", "D4"], tempo.s(12)), tempo.s(36), 0.04)
    p.poner(coro(["G2", "D3", "B3"], tempo.s(12)), tempo.s(84), 0.04)
    return final(p, sala=3.4, mezcla=0.36, brillo=5200)


PIEZAS["escarcha"] = escarcha
TITULOS["escarcha"] = "La nieve que escribe"

if __name__ == "__main__":
    solo = sys.argv[1:]
    for nombre, funcion in PIEZAS.items():
        if solo and nombre not in solo:
            continue
        semilla(len(nombre) * 101)
        x = funcion()
        if nombre in NO_SE_REPITEN:
            x = suavizar_bordes(estereo(x), 0.005, 0.05)
        guardar(x, os.path.join(DESTINO, nombre + ".ogg"), 0.8, calidad=5, titulo=TITULOS.get(nombre, nombre))
        print("música:", nombre, f"«{TITULOS.get(nombre, nombre)}»", f"{len(x) / SR:.1f} s")
