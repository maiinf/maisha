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
        y[:len(cola)] += cola[:n]
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


NO_SE_REPITEN = ("raiz_libre", "despertar", "purga", "victoria", "objeto", "tarea", "recuerdo", "noche", "amanece", "kitovu", "interior")      # (kitovu e interior vuelven tras un silencio)
PIEZAS = {"despertar": despertar, "kitovu": kitovu, "inicio": inicio, "prados": prados, "aldea": aldea,
          "interior": interior, "combate": combate, "jefe": jefe, "purga": purga, "victoria": victoria, "objeto": objeto, "tarea": tarea,
          "recuerdo": recuerdo, "noche": noche, "amanece": amanece, "bosque": bosque, "jefe_pembe": jefe_pembe,
          "cienaga": cienaga, "jefe_konokono": jefe_konokono, "campo": campo, "jefe_cosechadora": jefe_cosechadora,
          "tienda": tienda, "raiz_libre": raiz_libre, "sendero": sendero, "pasarelas": pasarelas,
          "cobrizo": cobrizo, "surcos": surcos, "canada": canada}

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
