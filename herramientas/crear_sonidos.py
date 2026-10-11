"""
EFECTOS DE SONIDO Y AMBIENTES de Maisha, hechos con el sintetizador (sin muestras de nadie).

Uso:  python3 herramientas/crear_sonidos.py
Genera:
  audio/sonidos/<nombre>.ogg     cada efecto (la lista está en EFECTOS, abajo)
  audio/ambiente/<nombre>.ogg    ambientes en bucle: brisa, viento, fuego, agua
                                 (y pájaros, que no se usan ahora: se guardan para un bioma de selva)
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sintetizador import (SR, Pista, adsr, balafon, caida, campanita, guardar, kalimba, paso_alto, paso_bajo,
                          paso_banda, reverb, ruido, ruido_rosa, semilla, seno, sierra, subida, suavizar_bordes,
                          t, tambor, taiko, triangulo, barrido_bajo, coro, estereo)

DESTINO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio")


def _n(dur):
    return int(dur * SR)


def _desliz(f0, f1, dur, curva=1.0):
    """Frecuencia que va de f0 a f1 (exponencial)."""
    u = np.linspace(0, 1, _n(dur)) ** curva
    return f0 * (f1 / f0) ** u


# =============================================================================
# DIÁLOGOS Y MENÚS
# =============================================================================

def dialogo_pasar():
    """El «bip» al pulsar Acción para seguir leyendo (como en los Pokémon de antes): dos notas cortas."""
    x = np.zeros(_n(0.09))
    for i, (f, en) in enumerate(((1318.5, 0.0), (1975.5, 0.035))):
        d = 0.05
        tono = triangulo(f, d, armonicos=3) * adsr(_n(d), 0.002, 0.01, 0.6, 0.02)
        a = _n(en)
        x[a:a + len(tono)] += tono[:len(x) - a] * (0.8 if i == 0 else 0.6)
    return reverb(x, 0.5, 0.12)


def dialogo_cerrar():
    x = np.zeros(_n(0.1))
    for i, (f, en) in enumerate(((1567.98, 0.0), (1046.5, 0.04))):
        d = 0.055
        tono = triangulo(f, d, armonicos=3) * adsr(_n(d), 0.002, 0.01, 0.6, 0.025)
        a = _n(en)
        x[a:a + len(tono)] += tono[:len(x) - a] * 0.6
    return reverb(x, 0.5, 0.12)


def menu_mover():
    d = 0.035
    return triangulo(1760, d, 3) * adsr(_n(d), 0.001, 0.01, 0.5, 0.015) * 0.6


def menu_aceptar():
    p = Pista(0.3)
    p.poner(kalimba("E6", 0.4), 0.0, 0.7)
    p.poner(kalimba("B6", 0.4), 0.05, 0.6)
    return reverb(p.entera(), 0.8, 0.15)


def menu_atras():
    p = Pista(0.3)
    p.poner(kalimba("B5", 0.3), 0.0, 0.6)
    p.poner(kalimba("E5", 0.35), 0.05, 0.6)
    return reverb(p.entera(), 0.8, 0.15)


def mochila_abrir():
    """Una bolsa de tela que se abre y una notita."""
    roce = paso_banda(ruido(0.18), 1500, 6000) * adsr(_n(0.18), 0.03, 0.05, 0.4, 0.08) * 0.35
    p = Pista(0.4)
    p.poner(roce, 0)
    p.poner(kalimba("A5", 0.5), 0.07, 0.5)
    p.poner(kalimba("E6", 0.5), 0.12, 0.4)
    return reverb(p.entera(), 0.7, 0.12)


def mochila_cerrar():
    roce = paso_banda(ruido(0.15), 1200, 5000) * adsr(_n(0.15), 0.01, 0.05, 0.4, 0.07) * 0.35
    p = Pista(0.3)
    p.poner(roce, 0)
    p.poner(kalimba("E6", 0.4), 0.03, 0.4)
    p.poner(kalimba("A5", 0.4), 0.08, 0.4)
    return reverb(p.entera(), 0.7, 0.12)


def pausa():
    p = Pista(0.6)
    for i, nota in enumerate(("D6", "A5", "D5")):
        p.poner(kalimba(nota, 0.6), i * 0.05, 0.5)
    return reverb(p.entera(), 1.2, 0.25)


# =============================================================================
# MAISHA Y EL COMBATE
# =============================================================================

def cetro_golpe():
    """El cetro corta el aire: un «fsss» corto."""
    d = 0.16
    x = ruido(d)
    out = np.zeros(_n(d))
    trozos = 16
    for i in range(trozos):
        a, b = i * len(x) // trozos, (i + 1) * len(x) // trozos
        f = 900 + 2600 * math.sin(math.pi * i / trozos)
        out[a:b] = paso_banda(x[a:b], f * 0.7, f * 1.4)
    return out * adsr(_n(d), 0.02, 0.04, 0.6, 0.08) * 0.5


def golpe_acierto():
    """El cetro le da a un Petrino: un golpe seco de madera contra piedra."""
    d = 0.22
    x = seno(_desliz(260, 110, d), d) * caida(_n(d), 0.05) * 0.9
    x += paso_banda(ruido(d), 800, 4000) * caida(_n(d), 0.015) * 0.6
    x += balafon("D4", d, 0.3)
    return reverb(x, 0.6, 0.1)


def clinc():
    """El cetro rebota en la piedra de un Corazón o de Mzizi: un «clinc» metálico y corto."""
    d = 0.5
    x = sum(seno(f, d) * caida(_n(d), dd) * a for f, dd, a in ((2350, 0.12, 0.5), (3870, 0.07, 0.35), (5600, 0.04, 0.2)))
    x += paso_alto(ruido(d), 4000) * caida(_n(d), 0.004) * 0.4
    return reverb(x, 0.9, 0.18)


def semilla_plantar():
    """La semilla cae al suelo: un «pop» de tierra blanda."""
    d = 0.18
    x = seno(_desliz(420, 160, d, 0.5), d) * caida(_n(d), 0.04) * 0.8
    x += paso_bajo(ruido(d), 1200) * caida(_n(d), 0.02) * 0.4
    return x


def semilla_mecha():
    """La semilla está a punto de estallar: un tic-tic brillante."""
    d = 0.06
    return campanita(2637, d, 0.6) * adsr(_n(d), 0.001, 0.01, 0.6, 0.03)


def explosion():
    """La semilla estalla: un golpe hondo de tierra y hojas que salen volando (no un petardo)."""
    d = 1.4
    n = _n(d)
    golpe = seno(_desliz(120, 38, d, 0.4), d) * caida(n, 0.22)
    tierra = paso_bajo(ruido_rosa(d), 900) * caida(n, 0.3) * 1.6
    hojas = paso_banda(ruido(d), 2500, 9000) * caida(n, 0.12) * subida(n, 0.01) * 0.35
    brote = sum(kalimba(nota, 0.9, 0.18) for nota in ("D5", "A5"))
    x = golpe + tierra + hojas
    x[_n(0.05):_n(0.05) + len(brote)] += brote[:n - _n(0.05)]
    return reverb(paso_bajo(x, 7000) * adsr(n, 0.003, 0.05, 1, 0.3), 1.6, 0.25)


def brotes():
    """Los brotes que deja la explosión: un brillito verde."""
    p = Pista(0.6)
    for i, nota in enumerate(("A5", "E6", "A6")):
        p.poner(campanita(nota, 0.5, 0.3), i * 0.04)
    return reverb(p.entera(), 1.0, 0.3)


def latido():
    """El Latido de Maisha: un «pum-pum» de corazón y un soplo que empuja."""
    p = Pista(0.9)
    for en, f in ((0.0, 1.0), (0.17, 0.7)):
        p.poner(seno(_desliz(95, 45, 0.25), 0.25) * caida(_n(0.25), 0.07) * f, en)
    soplo = paso_banda(ruido(0.6), 300, 2500) * adsr(_n(0.6), 0.02, 0.1, 0.5, 0.4) * 0.4
    p.poner(soplo, 0.12)
    p.poner(kalimba("D5", 0.8, 0.25), 0.15)
    return reverb(p.entera(), 1.2, 0.2)


def maisha_herida():
    """A Maisha le hacen daño: un golpecito y una nota que baja."""
    d = 0.3
    x = seno(_desliz(880, 520, d), d) * adsr(_n(d), 0.003, 0.05, 0.5, 0.15) * 0.5
    x += paso_bajo(ruido(d), 2000) * caida(_n(d), 0.02) * 0.5
    return reverb(x, 0.6, 0.12)


def maisha_cae():
    p = Pista(1.8)
    for i, nota in enumerate(("A5", "F5", "D5", "A4")):
        p.poner(kalimba(nota, 1.2, 0.6), i * 0.18)
    return reverb(p.entera(), 1.8, 0.3)


def recoger():
    """Coger algo (setas, mineral, zanahorias...): dos notas que suben."""
    p = Pista(0.6)
    p.poner(kalimba("A5", 0.6), 0.0, 0.7)
    p.poner(kalimba("E6", 0.7), 0.07, 0.6)
    return reverb(p.entera(), 1.0, 0.2)


def esencia():
    p = Pista(1.2)
    for i, nota in enumerate(("E6", "G#6", "B6", "E7")):
        p.poner(campanita(nota, 0.9, 0.5), i * 0.06)
    return reverb(p.entera(), 1.8, 0.35)


def puerta():
    """Una puerta de madera que se abre."""
    d = 0.5
    chirrido = paso_banda(sierra(_desliz(180, 240, d), d, 10), 400, 2500) * adsr(_n(d), 0.05, 0.1, 0.5, 0.2) * 0.25
    golpe = seno(110, 0.15) * caida(_n(0.15), 0.04) * 0.5
    p = Pista(0.6)
    p.poner(chirrido, 0)
    p.poner(golpe, 0.38)
    return p.entera()


# =============================================================================
# GIZA: ZONAS, PETRINOS Y CORAZONES
# =============================================================================

def _crujido_piedra(dur, densidad=180, grave=True):
    """Muchos chasquidos de piedra seguidos (raíces que se rompen o se mueven)."""
    n = _n(dur)
    x = np.zeros(n)
    rng = np.random.default_rng(int(dur * 1000) + densidad)
    for _ in range(int(densidad * dur)):
        i = rng.integers(0, max(1, n - 800))
        largo = rng.integers(200, 700)
        golpe = rng.normal(0, 1, largo) * np.exp(-np.arange(largo) / rng.uniform(60, 200))
        x[i:i + largo] += golpe * rng.uniform(0.3, 1.0)
    x = paso_banda(x, 300 if grave else 900, 4000 if grave else 7000)
    return x


def petrino_aparece():
    """Un Petrino brota del suelo: crujido de piedra que sube y un soplo violeta."""
    d = 0.9
    n = _n(d)
    crujido = _crujido_piedra(d, 120) * subida(n, 0.5) * adsr(n, 0.01, 0.1, 1, 0.25) * 0.8
    sube = seno(_desliz(70, 160, d), d) * adsr(n, 0.2, 0.2, 0.6, 0.3) * 0.5
    giza = paso_banda(ruido(d), 500, 1800) * adsr(n, 0.3, 0.2, 0.4, 0.3) * 0.25
    return reverb(crujido + sube + giza, 1.2, 0.2)


def petrino_golpeado():
    d = 0.25
    x = seno(_desliz(320, 150, d), d) * caida(_n(d), 0.05) * 0.6 + _crujido_piedra(d, 200) * caida(_n(d), 0.06) * 0.6
    return reverb(x, 0.5, 0.1)


def petrino_muere():
    """Se desmorona: piedras que caen y rebotan."""
    d = 1.0
    n = _n(d)
    x = _crujido_piedra(d, 90) * caida(n, 0.35) * 1.0
    x += seno(_desliz(180, 60, d), d) * caida(n, 0.1) * 0.5
    return reverb(x, 0.9, 0.15)


def petrino_embiste():
    """Gruñido corto de piedra al lanzarse."""
    d = 0.35
    n = _n(d)
    base = sierra(_desliz(95, 70, d), d, 14) * (0.7 + 0.3 * np.sign(np.sin(2 * np.pi * 28 * t(d))))
    return paso_bajo(base, 900) * adsr(n, 0.02, 0.1, 0.6, 0.15) * 0.5


def zona_aviso():
    """Al pisar el borde de una mancha: un «uuu» hondo y frío que crece."""
    d = 2.6
    n = _n(d)
    x = coro(["D2", "G#2"], d, "u", 1.0) * 1.5
    x += paso_bajo(ruido_rosa(d), 300) * adsr(n, 1.0, 0.2, 0.6, 1.0) * 0.6
    return reverb(x, 3.0, 0.4, 3000)


def espinas_suben():
    """Las raíces-espina de piedra se levantan alrededor: rasgado de piedra y un golpe."""
    d = 1.1
    n = _n(d)
    rasgo = _crujido_piedra(d, 260) * subida(n, 0.4) * adsr(n, 0.01, 0.1, 1.0, 0.4)
    golpe = taiko(0.9, 0.9)
    x = rasgo * 0.8
    x[_n(0.35):_n(0.35) + len(golpe)] += golpe[:n - _n(0.35)]
    return reverb(x, 1.5, 0.25, 4000)


def corazon_golpeado():
    """Una semilla le da al Corazón de Giza: crujido y un quejido violeta."""
    d = 0.9
    n = _n(d)
    x = _crujido_piedra(d, 220) * caida(n, 0.15)
    x += coro(["C#4"], d, "a", 0.5) * caida(n, 0.4) * 1.5
    return reverb(x, 1.4, 0.25)


def corazon_roto():
    """El Corazón se rompe: estallido de piedra, y la vida que vuelve (campanitas que suben)."""
    p = Pista(3.2)
    d = 1.2
    p.poner(_crujido_piedra(d, 300) * caida(_n(d), 0.35) * 1.1, 0)
    p.poner(seno(_desliz(150, 40, 0.6), 0.6) * caida(_n(0.6), 0.15), 0)
    for i, nota in enumerate(("D5", "F#5", "A5", "D6", "F#6", "A6")):
        p.poner(campanita(nota, 1.4, 0.5), 0.35 + i * 0.09)
    return reverb(p.entera(), 2.2, 0.3)


def ola_purga():
    """La ola de color que se extiende al purgar: un «shhh» brillante que se abre."""
    d = 2.4
    n = _n(d)
    x = barrido_bajo(ruido_rosa(d), 300, 9000) * adsr(n, 0.4, 0.3, 0.7, 1.2) * 0.5
    x += paso_alto(ruido(d), 7000) * adsr(n, 0.8, 0.2, 0.5, 1.0) * 0.12
    return reverb(x, 2.0, 0.35)


# =============================================================================
# MZIZI, LA RAÍZ DEL ARCO
# =============================================================================

def _rugido(dur, f0, f1, aspereza=0.6):
    """Rugido de raíz: sierras graves desafinadas con un temblor áspero, por formantes de garganta."""
    n = _n(dur)
    f = _desliz(f0, f1, dur, 0.7)
    temblor = 1 + aspereza * 0.5 * np.sign(np.sin(2 * np.pi * 31 * t(dur))) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t(dur)))
    x = sum(sierra(f * r, dur, 18) for r in (1.0, 1.007, 0.993, 2.01)) * temblor
    x = sum(paso_banda(x, a, b) * g for a, b, g in ((90, 300, 1.0), (450, 800, 0.8), (1100, 1600, 0.4)))
    grava = _crujido_piedra(dur, 150) * 0.5
    return (x * 0.5 + grava) * adsr(n, 0.12, 0.3, 0.8, dur * 0.35)


def mzizi_rugido():
    """El rugido de su presentación: largo, hondo, con el suelo crujiendo."""
    d = 2.6
    x = _rugido(d, 62, 48, 0.8)
    golpe = np.zeros(_n(d))
    tk = taiko(1.5, 1.2)
    golpe[:len(tk)] += tk
    return reverb(x + golpe, 3.0, 0.35, 3500)


def mzizi_dolor():
    """Le estalla una semilla: un chillido de madera y piedra que se raja."""
    d = 1.2
    x = _rugido(d, 140, 75, 1.0) * 0.9
    raja = _crujido_piedra(0.5, 350, grave=False) * caida(_n(0.5), 0.15)
    x[:len(raja)] += raja
    return reverb(x, 1.8, 0.3)


def mzizi_aviso():
    """Antes de salir: el suelo retumba bajo el agujero."""
    d = 1.3
    n = _n(d)
    x = paso_bajo(ruido_rosa(d), 160) * 2.5 * subida(n, 0.9)
    x += seno(38 + 4 * np.sin(2 * np.pi * 7 * t(d)), d) * subida(n, 0.8) * 0.6
    x += _crujido_piedra(d, 60) * subida(n, 1.0) * 0.4
    return x * adsr(n, 0.05, 0.1, 1.0, 0.15)


def mzizi_sale():
    """Revienta la tierra y sale."""
    d = 1.0
    n = _n(d)
    x = taiko(1.0, 1.0) + _crujido_piedra(d, 260) * caida(n, 0.3) * 0.9
    x += paso_bajo(ruido_rosa(d), 600) * caida(n, 0.25) * 1.2
    return reverb(x, 1.6, 0.25)


def mzizi_escupe():
    """Escupe una piedra: carraspeo y un «puh»."""
    d = 0.45
    n = _n(d)
    carraspeo = _rugido(0.25, 110, 160, 1.0) * 0.5
    puh = paso_bajo(ruido(0.2), 1200) * caida(_n(0.2), 0.05) * 0.9
    x = np.zeros(n)
    x[:len(carraspeo)] += carraspeo
    x[_n(0.2):_n(0.2) + len(puh)] += puh
    return reverb(x, 0.8, 0.15)


def piedra_rompe():
    d = 0.4
    return reverb(_crujido_piedra(d, 400, grave=False) * caida(_n(d), 0.08), 0.6, 0.12)


def mzizi_vencido():
    """Su último quejido se convierte en un crujido de madera viva, y la vida vuelve a la raíz."""
    p = Pista(6.0)
    p.poner(_rugido(2.2, 90, 40, 0.9), 0.0, 1.0)
    p.poner(_crujido_piedra(2.0, 120) * caida(_n(2.0), 0.8), 1.2, 0.9)
    # madera que cruje (más cálida)
    cruje = paso_banda(sierra(_desliz(70, 55, 1.5), 1.5, 20) * (1 + np.sign(np.sin(2 * np.pi * 12 * t(1.5)))), 200, 1200)
    p.poner(cruje * adsr(_n(1.5), 0.2, 0.3, 0.5, 0.6) * 0.35, 2.2)
    for i, nota in enumerate(("D5", "F#5", "A5", "D6", "E6", "F#6", "A6", "D7")):
        p.poner(campanita(nota, 1.8, 0.45), 3.0 + i * 0.12)
    return reverb(p.entera(), 3.0, 0.35)


def temblor():
    """El suelo tiembla (cuando despierta Mzizi o se limpia la última mancha)."""
    d = 2.2
    n = _n(d)
    x = paso_bajo(ruido_rosa(d), 120) * 3.0 + seno(34 + 3 * np.sin(2 * np.pi * 5 * t(d)), d) * 0.7
    x += _crujido_piedra(d, 50) * 0.3
    return x * adsr(n, 0.3, 0.2, 0.8, 0.9)


def portal_abre():
    """El Arco de Raíz despierta: un acorde que se abre, con brillos."""
    p = Pista(4.0)
    p.poner(estereo(coro(["D4", "A4", "D5", "F#5"], 3.6, "o", 1.0)) * 0.9, 0)
    for i, nota in enumerate(("A5", "D6", "F#6", "A6", "D7", "F#7")):
        p.poner(campanita(nota, 1.6, 0.35), 0.4 + i * 0.15, pan=(i % 3 - 1) * 0.5)
    return reverb(p.entera(), 3.0, 0.4)


# =============================================================================
# PESCA Y TAREAS (cada tarea suena a lo que es)
# =============================================================================

def _chapoteo(dur=0.5, fuerza=1.0, grave=1.0):
    """Algo que cae al agua: un «plop» (una burbuja grande) y gotas que salpican."""
    n = _n(dur)
    rng = np.random.default_rng(int(dur * 100 + fuerza * 10))
    plop = seno(_desliz(260 * grave, 900 * grave, 0.06), 0.06) * caida(_n(0.06), 0.025)
    x = np.zeros(n)
    x[:len(plop)] += plop * 0.9
    x += paso_banda(ruido(dur), 600, 5000) * caida(n, 0.08) * 0.5 * fuerza
    for _ in range(int(12 * fuerza)):
        f = rng.uniform(900, 3200)
        d = rng.uniform(0.01, 0.03)
        m = _n(d)
        u = np.arange(m) / SR
        gota = np.sin(2 * np.pi * np.cumsum(f * (1 + 1.5 * u / d)) / SR) * np.exp(-u / (d * 0.4))
        i = rng.integers(_n(0.03), max(_n(0.04), n - m))
        x[i:i + m] += gota * rng.uniform(0.1, 0.35)
    return x * fuerza


def pesca_lanzar():
    """Lanzar la caña: el sedal silba en el aire y el carrete suelta hilo; el corcho cae al agua."""
    p = Pista(1.4)
    silbido = paso_banda(ruido(0.45), 1500, 6000) * adsr(_n(0.45), 0.05, 0.1, 0.5, 0.25) * 0.4
    p.poner(silbido, 0.0)
    for i in range(10):
        p.poner(paso_alto(ruido(0.008), 3000) * caida(_n(0.008), 0.002) * 0.35, 0.05 + i * 0.03)   # tic-tic-tic del carrete
    p.poner(_chapoteo(0.6, 0.6, 1.3), 0.55)
    return reverb(p.entera(), 0.8, 0.12)


def pesca_espera():
    """Mientras se espera: el corcho se mece y hace ondas (muy flojito)."""
    x = seno(_desliz(500, 700, 0.05), 0.05) * caida(_n(0.05), 0.02) * 0.4
    x = np.concatenate([x, np.zeros(_n(0.2))])
    x += paso_banda(ruido(len(x) / SR), 400, 2000) * caida(len(x), 0.05) * 0.15
    return x


def pesca_pica():
    """¡Pica! Un tirón: el corcho se hunde de golpe y el sedal se tensa («tin»)."""
    p = Pista(0.9)
    p.poner(_chapoteo(0.5, 0.9, 0.8), 0.0)
    p.poner(seno(_desliz(1400, 1800, 0.12), 0.12) * caida(_n(0.12), 0.05) * 0.3, 0.05)
    return reverb(p.entera(), 0.6, 0.12)


def pesca_saca():
    """¡Pescado! El pez sale del agua salpicando y cae a tierra; una notita alegre."""
    p = Pista(1.6)
    p.poner(_chapoteo(0.8, 1.4, 0.7), 0.0)
    for i in range(6):
        p.poner(paso_alto(ruido(0.008), 2500) * caida(_n(0.008), 0.002) * 0.3, 0.05 + i * 0.025)
    p.poner(seno(_desliz(180, 120, 0.12), 0.12) * caida(_n(0.12), 0.04) * 0.5, 0.55)        # cae en la hierba
    p.poner(kalimba("A5", 0.6, 0.5), 0.6)
    p.poner(kalimba("E6", 0.7, 0.45), 0.68)
    return reverb(p.entera(), 1.0, 0.18)


def pesca_escapa():
    """Se escapa: un coletazo en el agua y una nota que baja."""
    p = Pista(1.2)
    p.poner(_chapoteo(0.6, 1.0, 0.9), 0.0)
    p.poner(kalimba("E5", 0.8, 0.4), 0.25)
    p.poner(kalimba("B4", 0.9, 0.35), 0.4)
    return reverb(p.entera(), 1.0, 0.18)


def zanahoria_arrancar():
    """Arrancar una zanahoria: la tierra cruje, se rompen las raicillas y sale con un «plop»."""
    d = 0.55
    n = _n(d)
    tierra = paso_banda(ruido(d), 250, 2500) * subida(n, 0.25) * adsr(n, 0.02, 0.1, 0.8, 0.12) * 0.6
    rng = np.random.default_rng(4)
    for _ in range(18):                               # raicillas que se rompen
        i = rng.integers(_n(0.05), _n(0.35))
        m = rng.integers(60, 240)
        tierra[i:i + m] += rng.normal(0, 1, m) * np.exp(-np.arange(m) / 40) * 0.35
    plop = seno(_desliz(180, 520, 0.07), 0.07) * caida(_n(0.07), 0.03)
    x = paso_bajo(tierra, 3500)
    x[_n(0.36):_n(0.36) + len(plop)] += plop * 0.8
    hojas = paso_banda(ruido(0.15), 2500, 7000) * caida(_n(0.15), 0.05) * 0.15
    x[_n(0.4):_n(0.4) + len(hojas)] += hojas[:len(x) - _n(0.4)]
    return reverb(x, 0.5, 0.1)


def _madera(f=420.0, dur=0.25, fuerza=1.0):
    """Un golpe en una tabla: varios modos de vibración de la madera, secos."""
    x = sum(seno(f * r, dur) * caida(_n(dur), dd) * a for r, dd, a in ((1.0, 0.06, 1.0), (2.31, 0.035, 0.5), (3.9, 0.02, 0.3), (5.6, 0.012, 0.2)))
    x += paso_banda(ruido(dur), 800, 4000) * caida(_n(dur), 0.006) * 0.4
    return x * fuerza


def tablas_coger():
    """Coger las tablas del tronco: madera hueca que choca."""
    p = Pista(0.8)
    for i, (f, en) in enumerate(((380, 0.0), (460, 0.09), (330, 0.2), (520, 0.26))):
        p.poner(_madera(f, 0.3, 0.8 - i * 0.12), en)
    return reverb(p.entera(), 0.6, 0.12)


def cerca_martillo():
    """Arreglar la cerca: tres martillazos (el clavo suena un poco a metal) y la madera que asienta."""
    p = Pista(1.6)
    for i, en in enumerate((0.0, 0.38, 0.74)):
        p.poner(_madera(300, 0.3, 0.9), en)
        clavo = seno(2600 - i * 180, 0.25) * caida(_n(0.25), 0.05) * 0.25 + seno(4100, 0.25) * caida(_n(0.25), 0.02) * 0.1
        p.poner(clavo, en)
    return reverb(p.entera(), 0.7, 0.14)


def cerca_arreglada():
    p = Pista(1.0)
    for i, nota in enumerate(("D5", "F#5", "A5")):
        p.poner(kalimba(nota, 0.8, 0.5), i * 0.08)
    return reverb(p.entera(), 1.0, 0.2)


def espantapajaros_golpe():
    """El cetro le da al espantapájaros: paja y un trapo viejo."""
    d = 0.3
    x = paso_banda(ruido(d), 400, 3000) * caida(_n(d), 0.05) * 0.7
    x += seno(_desliz(160, 90, d), d) * caida(_n(d), 0.04) * 0.4
    x += paso_banda(ruido(d), 3000, 8000) * caida(_n(d), 0.09) * 0.12      # pajitas
    return x


def seta_recoger():
    """Coger una seta luminosa: se suelta del suelo con un «pop» blandito y brilla."""
    p = Pista(1.0)
    p.poner(seno(_desliz(300, 650, 0.05), 0.05) * caida(_n(0.05), 0.02) * 0.6, 0.0)
    p.poner(paso_banda(ruido(0.06), 1000, 4000) * caida(_n(0.06), 0.015) * 0.2, 0.0)
    for i, nota in enumerate(("B6", "E7", "G#7")):
        p.poner(campanita(nota, 0.7, 0.25), 0.06 + i * 0.05)
    return reverb(p.entera(), 1.2, 0.3)


def mineral_romper():
    """Romper una roca con mineral: la piedra se raja y suena el cristal."""
    p = Pista(1.4)
    p.poner(_crujido_piedra(0.5, 380, grave=False) * caida(_n(0.5), 0.12), 0.0)
    for i, nota in enumerate(("E6", "B6", "E7")):
        p.poner(campanita(nota, 1.0, 0.35), 0.12 + i * 0.04)
    return reverb(p.entera(), 1.2, 0.25)


def entregar():
    """Dar algo a alguien: la bolsa y dos notas amables."""
    p = Pista(0.8)
    p.poner(paso_banda(ruido(0.15), 1500, 6000) * adsr(_n(0.15), 0.02, 0.05, 0.4, 0.06) * 0.3, 0.0)
    p.poner(kalimba("D5", 0.6, 0.5), 0.1)
    p.poner(kalimba("A5", 0.7, 0.45), 0.2)
    return reverb(p.entera(), 0.9, 0.18)


def construir():
    """Reconstruir una casa: martillos, una sierra y la madera que cruje al asentarse."""
    p = Pista(3.2)
    rng = np.random.default_rng(12)
    for i in range(9):
        p.poner(_madera(rng.uniform(260, 420), 0.3, rng.uniform(0.6, 1.0)), 0.1 + i * rng.uniform(0.18, 0.3), pan=rng.uniform(-0.5, 0.5))
    sierra_ = paso_banda(ruido(1.0), 1500, 5000) * (0.5 + 0.5 * np.sin(2 * np.pi * 5 * t(1.0)) ** 2) * 0.25
    p.poner(sierra_, 1.2, pan=0.3)
    p.poner(seno(_desliz(80, 60, 0.8), 0.8) * caida(_n(0.8), 0.3) * 0.6, 2.4)
    return reverb(p.entera(), 1.2, 0.2)


def estatua_despierta():
    """Un aldeano de piedra despierta: la piedra se agrieta y cae, y vuelve la vida."""
    p = Pista(3.0)
    p.poner(_crujido_piedra(1.4, 160) * subida(_n(1.4), 1.0), 0.0)
    p.poner(_crujido_piedra(0.6, 300) * caida(_n(0.6), 0.2), 1.4)
    for i, nota in enumerate(("D5", "A5", "D6", "F#6")):
        p.poner(campanita(nota, 1.4, 0.4), 1.5 + i * 0.1)
    return reverb(p.entera(), 2.0, 0.3)


# =============================================================================
# EL COMIENZO: la chispa de vida, la gallina perdida y la puerta
# =============================================================================

def chispa():
    """La chispa de vida: un destello de cristal, suave y cálido."""
    p = Pista(1.4)
    for i, nota in enumerate(("A6", "E7", "C#7")):
        p.poner(campanita(nota, 1.0, 0.35 - i * 0.07), i * 0.07, pan=(i - 1) * 0.4)
    return reverb(p.entera(), 1.6, 0.4)


def chispa_entra():
    """La chispa entra en el brote de Maisha: un acorde de luz que sube."""
    p = Pista(2.2)
    for i, nota in enumerate(("D6", "F#6", "A6", "D7", "E7")):
        p.poner(campanita(nota, 1.5, 0.35), i * 0.06)
    p.poner(barrido_bajo(ruido_rosa(1.2), 400, 8000) * adsr(_n(1.2), 0.4, 0.2, 0.5, 0.5) * 0.25, 0.0)
    return reverb(p.entera(), 2.0, 0.35)


def _cloqueo(f0, dur, rng, abierto=1.0):
    """Un «co» de gallina: tono que sube un poco y se apaga, con la aspereza de la garganta."""
    n = _n(dur)
    u = np.linspace(0, 1, n)
    f = f0 * (1 + 0.35 * np.sin(np.pi * u) * abierto)
    fase = 2 * np.pi * np.cumsum(f) / SR
    pulsos = np.sign(np.sin(fase)) * 0.4 + np.sin(fase)               # áspero, como de pecho
    x = sum(paso_banda(pulsos, a, b) * g for a, b, g in ((600, 1100, 1.0), (1500, 2400, 0.6 * abierto), (2800, 3600, 0.25)))
    env = np.sin(np.pi * u) ** 0.6
    return x * env * rng.uniform(0.8, 1.0)


def gallina_cacareo():
    """Una gallina que cloquea: «co, co, co... coooc» (la que se ha escapado de la granja)."""
    rng = np.random.default_rng(3)
    p = Pista(1.8)
    en = 0.0
    for i in range(rng.integers(3, 5)):
        p.poner(_cloqueo(rng.uniform(420, 520), rng.uniform(0.07, 0.1), rng, 0.6), en)
        en += rng.uniform(0.12, 0.22)
    p.poner(_cloqueo(560, 0.42, rng, 1.0), en + 0.05)
    return reverb(p.entera(), 0.7, 0.12)


def gallina_asustada():
    """La gallina se asusta: un «¡coc!» agudo y un aleteo."""
    rng = np.random.default_rng(8)
    p = Pista(0.9)
    p.poner(_cloqueo(700, 0.18, rng, 1.2), 0.0)
    for i in range(7):
        p.poner(paso_banda(ruido(0.04), 400, 3000) * caida(_n(0.04), 0.012) * 0.5, 0.12 + i * 0.065)
    return reverb(p.entera(), 0.5, 0.1)


def llamar_puerta():
    """«Toc, toc» en la puerta de madera de la granja."""
    p = Pista(0.9)
    for en in (0.0, 0.22):
        p.poner(_madera(190, 0.3, 1.0), en)
    return reverb(p.entera(), 0.6, 0.15)


def sopa():
    """La cuchara en el cuenco de sopa (en la cena)."""
    p = Pista(1.2)
    for i, en in enumerate((0.0, 0.35, 0.7)):
        p.poner(seno(2100 + i * 40, 0.3) * caida(_n(0.3), 0.05) * 0.25 + seno(3300, 0.3) * caida(_n(0.3), 0.03) * 0.1, en)
    return reverb(p.entera(), 0.8, 0.15)


# =============================================================================
# AMBIENTES (en bucle)
# =============================================================================

def _silaba(contorno, dur, rng, trino=0.0, brillo=0.12):
    """Una sílaba de canto: un silbido cuya altura sigue «contorno» (función de 0..1 → Hz),
    con un temblor natural, un poco de armónicos y una envolvente suave."""
    n = _n(dur)
    u = np.linspace(0, 1, n)
    f = contorno(u)
    # temblor natural: pequeñas variaciones lentas de altura
    temblor = np.interp(np.arange(n), np.linspace(0, n, 6), rng.normal(0, 0.012, 6))
    f = f * (1 + temblor)
    if trino:
        f = f * (1 + 0.06 * np.sin(2 * np.pi * trino * u * dur))
    fase = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(fase) + brillo * np.sin(2 * fase + 0.3) + 0.03 * np.sin(3 * fase)
    env = np.sin(np.pi * np.clip(u * 1.0, 0, 1)) ** 0.7
    ataque = max(1, _n(0.006))
    env[:ataque] *= np.linspace(0, 1, ataque)
    if trino:
        env *= 0.65 + 0.35 * np.abs(np.sin(np.pi * trino * u * dur))
    return x * env


def _contorno(rng, f_bajo, f_alto):
    """Una forma de silbido al azar: sube, baja, sube y baja, o casi plano."""
    a, b = rng.uniform(f_bajo, f_alto), rng.uniform(f_bajo, f_alto)
    forma = rng.integers(0, 4)
    if forma == 0:
        return lambda u: a + (b - a) * u ** 0.7
    if forma == 1:
        pico = max(a, b) * rng.uniform(1.1, 1.35)
        return lambda u: a + (pico - a) * np.sin(np.pi * u) + (b - a) * u * 0.3
    if forma == 2:
        return lambda u: a * (b / a) ** (u ** 1.6)
    return lambda u: a * (1 + 0.04 * np.sin(2 * np.pi * u * 2))


def _canto(especie, rng):
    """Una frase de canto según la especie (inspiradas en pájaros de verdad, pero inventadas)."""
    partes = []

    def pausa(seg):
        partes.append(np.zeros(_n(seg)))

    if especie == "zorzal":                         # repite cada motivo 2 o 3 veces y cambia
        for _ in range(rng.integers(2, 4)):
            silabas = [(_contorno(rng, 1900, 4600), rng.uniform(0.06, 0.16), rng.choice([0, 0, 45]))
                       for _ in range(rng.integers(1, 4))]
            for _ in range(rng.integers(2, 4)):
                for (c, d, tr) in silabas:
                    partes.append(_silaba(c, d, rng, trino=tr))
                    pausa(rng.uniform(0.03, 0.06))
                pausa(rng.uniform(0.08, 0.16))
            pausa(rng.uniform(0.15, 0.35))
    elif especie == "mirlo":                        # silbidos graves y redondos, lentos, con un remate agudo
        for _ in range(rng.integers(3, 6)):
            f0 = rng.uniform(1300, 2500)
            f1 = f0 * rng.uniform(0.8, 1.35)
            d = rng.uniform(0.18, 0.38)
            vib = rng.uniform(6, 9)
            partes.append(_silaba(lambda u, f0=f0, f1=f1, vib=vib, d=d: (f0 + (f1 - f0) * u) * (1 + 0.012 * np.sin(2 * np.pi * vib * u * d)), d, rng, brillo=0.06))
            pausa(rng.uniform(0.04, 0.12))
        for _ in range(rng.integers(2, 5)):
            partes.append(_silaba(_contorno(rng, 4500, 7000), 0.035, rng))
            pausa(0.025)
    elif especie == "carbonero":                    # «ti-tu, ti-tu, ti-tu»
        alto, bajo_ = rng.uniform(5200, 6200), rng.uniform(3900, 4500)
        for _ in range(rng.integers(3, 6)):
            partes.append(_silaba(lambda u, a=alto: a * (1 - 0.05 * u), 0.07, rng, brillo=0.05))
            pausa(0.035)
            partes.append(_silaba(lambda u, b=bajo_: b * (1 - 0.03 * u), 0.09, rng, brillo=0.05))
            pausa(0.08)
    elif especie == "chochin":                      # un trino rápido y muy vivo
        base = rng.uniform(4500, 6500)
        for k in range(rng.integers(14, 28)):
            f = base * (1 + 0.15 * np.sin(k * 0.7))
            partes.append(_silaba(lambda u, f=f: f * (1.15 - 0.3 * u), 0.028, rng, brillo=0.04))
            pausa(0.012)
    elif especie == "tortola":                      # un arrullo grave y lejano: «uu-UUU-uu»
        for i, (d, f) in enumerate(((0.25, 520), (0.55, 560), (0.3, 500))):
            x = _silaba(lambda u, f=f: f * (1 + 0.03 * np.sin(np.pi * u)), d, rng, brillo=0.25)
            x += paso_bajo(rng.normal(0, 0.08, len(x)), 900) * np.sin(np.pi * np.linspace(0, 1, len(x)))
            partes.append(x * (0.8 if i != 1 else 1.0))
            pausa(0.12)
    else:                                           # «pit» sueltos y agudos
        for _ in range(rng.integers(1, 4)):
            partes.append(_silaba(_contorno(rng, 6000, 8200), rng.uniform(0.015, 0.03), rng, brillo=0.03))
            pausa(rng.uniform(0.15, 0.5))
    return np.concatenate(partes)


def pajaros(dur=36.0, densidad=1.0, semilla_p=21):
    """Pájaros en un bosque: varios de cada especie, cada uno en su sitio (cerca, lejos, a un lado),
    cantando a su ritmo. Los lejanos suenan más apagados y con más eco."""
    rng = np.random.default_rng(semilla_p)
    especies = [("zorzal", 2), ("mirlo", 2), ("carbonero", 1), ("chochin", 1), ("tortola", 1), ("pit", 2)]
    seco = Pista(dur)
    eco = Pista(dur)
    for especie, cuantos in especies:
        for _ in range(max(1, int(round(cuantos * densidad)))):
            pan = rng.uniform(-0.85, 0.85)
            lejos = rng.uniform(0.15, 1.0) if especie != "tortola" else rng.uniform(0.7, 1.0)
            volumen = 0.75 / (1 + 2.5 * lejos) * (0.55 if especie in ("tortola", "pit") else 1.0)
            corte = 11000 - 7500 * lejos
            descanso = {"zorzal": (3, 8), "mirlo": (4, 10), "carbonero": (6, 14), "chochin": (8, 18), "tortola": (9, 16), "pit": (2, 6)}[especie]
            en = rng.uniform(0, descanso[1])
            while en < dur:
                canto = paso_bajo(_canto(especie, rng), corte)
                seco.poner(canto * volumen * (1 - 0.5 * lejos), en, pan=pan)
                eco.poner(canto * volumen * (0.2 + 0.8 * lejos), en, pan=pan * 0.6)
                en += len(canto) / SR + rng.uniform(*descanso) / densidad
    # hojas que se mueven con la brisa, muy flojito
    hojas = paso_banda(ruido_rosa(dur + 8), 1800, 7000) * 0.03
    hojas *= 0.5 + 0.5 * np.clip(np.sin(2 * np.pi * np.arange(len(hojas)) / SR / 11.0), 0, 1) ** 2
    seco.poner(hojas, 0)
    x = seco.bucle() + reverb(eco.bucle(), 1.1, 0.6, 5000)[:len(seco.bucle())] * 0.35
    return _cerrar_bucle(x, dur)


def brisa(dur=30.0):
    """Brisa suave entre hierba y hojas (sin pájaros): un rumor que va y viene."""
    rng = np.random.default_rng(15)
    n = _n(dur + 2)
    lento = np.interp(np.arange(n), np.linspace(0, n, 16), rng.uniform(0.25, 1.0, 16))
    hojas = paso_banda(ruido_rosa(dur + 2), 1200, 6000) * 0.5 * lento ** 2
    aire = paso_bajo(ruido_rosa(dur + 2), 400) * 0.9 * (0.5 + 0.5 * lento)
    rozar = paso_banda(ruido(dur + 2), 3000, 9000) * 0.03 * lento ** 3
    izq = hojas + aire + rozar
    der = np.roll(hojas, 1200) + aire + np.roll(rozar, 700)
    return _cerrar_bucle(np.stack([izq, der], axis=1), dur)


def agua(dur=24.0):
    """Agua que corre (el arroyo del estanque, el río): un rumor de fondo y burbujitas que suben."""
    rng = np.random.default_rng(9)
    n = _n(dur + 2)
    rumor = paso_banda(ruido_rosa(dur + 2), 180, 1600) * 1.6
    rumor *= 0.75 + 0.25 * np.interp(np.arange(n), np.linspace(0, n, 30), rng.uniform(0.3, 1.0, 30))
    brillo = paso_banda(ruido(dur + 2), 2500, 7000) * 0.06
    x = rumor + brillo
    # burbujas: un tono que sube muy rápido y se apaga (así suena una burbuja al reventar en el agua)
    for _ in range(int(dur * 38)):
        f = rng.uniform(380, 2400)
        d = rng.uniform(0.012, 0.045)
        m = _n(d)
        u = np.arange(m) / SR
        burbuja = np.sin(2 * np.pi * np.cumsum(f * (1 + 2.2 * u / d)) / SR) * np.exp(-u / (d * 0.35))
        i = rng.integers(0, n - m)
        x[i:i + m] += burbuja * rng.uniform(0.05, 0.25)
    y = np.stack([x, np.roll(x, 400) * 0.9 + paso_banda(ruido_rosa(dur + 2), 200, 1500) * 0.3], axis=1)
    return _cerrar_bucle(reverb(y, 1.2, 0.2, 7000), dur)


def viento(dur=30.0):
    """Viento suave entre árboles secos, con ráfagas."""
    n = _n(dur + 4)
    x = ruido_rosa(dur + 4)
    lento = np.interp(np.arange(n), np.linspace(0, n, 12), np.random.default_rng(3).uniform(0.3, 1.0, 12))
    out = barrido_bajo(x, 300, 300) * lento * 1.2
    silbido = paso_banda(x, 600, 1400) * (lento ** 3) * 0.4
    y = np.stack([out + silbido * 0.6, np.roll(out, 900) + silbido], axis=1)
    return _cerrar_bucle(y, dur)


def fuego(dur=20.0):
    """El fuego de la chimenea de Mzee Shamba: rumor y chasquidos."""
    n = _n(dur + 2)
    x = paso_bajo(ruido_rosa(dur + 2), 500) * 0.8
    rng = np.random.default_rng(5)
    for _ in range(int(dur * 7)):
        i = rng.integers(0, n - 600)
        largo = rng.integers(80, 500)
        x[i:i + largo] += paso_bajo(rng.normal(0, 1, largo), 3500) * np.exp(-np.arange(largo) / rng.uniform(20, 90)) * rng.uniform(0.08, 0.3)
    x += paso_bajo(ruido_rosa(dur + 2), 900) * 0.6 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.3 * np.arange(n) / SR))
    return _cerrar_bucle(estereo(paso_bajo(x, 5000)), dur)


def _cerrar_bucle(x, dur):
    """Funde el final con el principio para que el bucle no tenga costura."""
    n = _n(dur)
    x = x[:n + _n(2)] if len(x) >= n + _n(2) else np.pad(x, ((0, n + _n(2) - len(x)), (0, 0)))
    cruce = _n(2)
    out = x[:n].copy()
    rampa = np.linspace(0, 1, cruce)[:, None]
    out[:cruce] = out[:cruce] * rampa + x[n:n + cruce] * (1 - rampa)
    return out


# =============================================================================
# MISIONES, RUEDA RÁPIDA Y ÁRBOL DE LA VIDA
# =============================================================================

def mision_nueva():
    """Sale una misión nueva en el diario: tres notas de kalimba que suben, como abrir una página."""
    p = Pista(1.0)
    roce = paso_banda(ruido(0.2), 2000, 7000) * adsr(_n(0.2), 0.04, 0.05, 0.3, 0.1) * 0.18
    p.poner(estereo(roce), 0.0, 1.0)
    for i, nota in enumerate(("D5", "A5", "D6")):
        p.poner(kalimba(nota, 0.6), 0.04 + i * 0.09, 0.65 - i * 0.08)
    return reverb(p.entera(), 1.2, 0.22)


def mision_cumplida():
    """Misión cumplida: un arpegio brillante de campanitas que se abre (más corto que la fanfarria)."""
    p = Pista(1.6)
    for i, nota in enumerate(("G5", "B5", "D6", "G6")):
        p.poner(kalimba(nota, 0.8), i * 0.07, 0.6)
        p.poner(campanita(nota, 0.9), i * 0.07 + 0.01, 0.25)
    p.poner(campanita("D7", 1.2), 0.32, 0.3)
    return reverb(p.entera(), 1.5, 0.28)


def mision_paso():
    """Un paso del objetivo cumplido: un «tic» suave de dos notas."""
    p = Pista(0.5)
    p.poner(kalimba("A5", 0.35), 0.0, 0.55)
    p.poner(kalimba("E6", 0.4), 0.06, 0.5)
    return reverb(p.entera(), 0.9, 0.18)


def rueda_abrir():
    """La rueda rápida se abre: un soplo corto que gira."""
    d = 0.22
    x = paso_banda(ruido(d), 900, 5000) * adsr(_n(d), 0.05, 0.05, 0.4, 0.12) * 0.4
    return reverb(x + triangulo(1318.5, d, 2) * adsr(_n(d), 0.01, 0.05, 0.3, 0.1) * 0.15, 0.6, 0.15)


def meditar():
    """Maisha medita junto al brote: un acorde suave que crece y respira."""
    dur = 3.0
    p = Pista(dur + 1.0)
    for nota, vol in (("D3", 0.35), ("A3", 0.3), ("F#4", 0.22), ("A4", 0.2)):
        p.poner(coro([nota], dur, "o"), 0.0, vol)
    for i, nota in enumerate(("A5", "D6", "F#6")):
        p.poner(campanita(nota, 1.4), 0.6 + i * 0.35, 0.18)
    return reverb(p.entera(), 2.2, 0.35)


def arte_sube():
    """Un Arte sube de nivel: brota una hoja de luz (acorde que sube y destellos)."""
    p = Pista(1.8)
    for i, nota in enumerate(("D5", "F#5", "A5", "D6", "F#6")):
        p.poner(kalimba(nota, 0.7), i * 0.05, 0.55)
    p.poner(campanita("A6", 1.0), 0.28, 0.3)
    p.poner(campanita("D7", 1.0), 0.36, 0.25)
    brillo = paso_alto(ruido(0.6), 6000) * adsr(_n(0.6), 0.2, 0.1, 0.3, 0.3) * 0.08
    p.poner(estereo(brillo), 0.2, 1.0)
    return reverb(p.entera(), 1.6, 0.3)


# =============================================================================
# EL BOSQUE COBRIZO: el jabalí de hierro y Pembe, el ciervo de hierro
# =============================================================================

def _bramido(dur, f0, f1, ronco=0.5):
    """Bramido de ciervo: una voz que sube y baja por formantes de garganta, con un temblor ronco."""
    n = _n(dur)
    u = np.linspace(0, 1, n)
    f = f0 + (f1 - f0) * np.sin(np.pi * np.clip(u * 1.15, 0, 1)) ** 0.8
    fase = np.cumsum(f) / SR
    voz = np.sign(np.sin(2 * np.pi * fase)) * 0.4 + np.sin(2 * np.pi * fase) * 0.6
    voz = voz * (1 + ronco * 0.4 * np.sin(2 * np.pi * 27 * t(dur)))
    x = sum(paso_banda(voz, a, b) * g for a, b, g in ((180, 420, 1.0), (600, 1000, 0.7), (1500, 2300, 0.25)))
    aire = paso_banda(ruido(dur), 800, 3000) * 0.08
    return (x + aire) * adsr(n, 0.15, 0.2, 0.85, dur * 0.4)


def pembe_bramido():
    """Pembe brama: largo, metálico (el hierro de sus astas vibra) y con el bosque contestando."""
    d = 2.4
    p = Pista(d + 1)
    p.poner(_bramido(d, 150, 330, 0.7), 0.0, 1.0)
    # el hierro de las astas zumba
    zumbido = sum(seno(f, d) * g for f, g in ((523, 0.08), (787, 0.05), (1180, 0.03))) * adsr(_n(d), 0.4, 0.3, 0.6, 0.8)
    p.poner(zumbido, 0.1, 1.0)
    return reverb(p.entera(), 3.2, 0.42, 4000)


def pembe_escarba():
    """Escarba la tierra antes de embestir: tres arañazos y un resoplido."""
    p = Pista(1.0)
    for i in range(3):
        rasgu = paso_banda(ruido(0.12), 300, 2500) * caida(_n(0.12), 0.04) * 0.7
        p.poner(rasgu, i * 0.22, 1.0)
    resopla = paso_banda(ruido(0.35), 400, 1800) * adsr(_n(0.35), 0.02, 0.1, 0.5, 0.2) * 0.6
    p.poner(resopla, 0.62, 1.0)
    return reverb(p.entera(), 0.8, 0.15)


def pembe_galope():
    """Galope: cascos pesados que se alejan."""
    p = Pista(1.4)
    for i in range(6):
        en = i * 0.2 + (0.07 if i % 2 else 0)
        p.poner(tambor("D2", 0.25, 0.9 - i * 0.08, 0.6), en)
        p.poner(paso_bajo(ruido(0.08), 900) * caida(_n(0.08), 0.03) * 0.5, en)
    return reverb(p.entera(), 1.0, 0.18)


def pembe_choque():
    """Las astas se clavan en un árbol: crujido de madera y un «clang» de hierro que vibra."""
    d = 1.6
    p = Pista(d)
    golpe = taiko(1.0, 1.0)
    p.poner(golpe, 0.0, 0.9)
    madera = paso_banda(ruido(0.6), 150, 1500) * caida(_n(0.6), 0.12)
    p.poner(madera, 0.0, 0.9)
    clang = sum(seno(f, 1.4) * caida(_n(1.4), 0.5) * g for f, g in ((311, 0.35), (467, 0.25), (742, 0.18), (1190, 0.1)))
    p.poner(clang, 0.02, 1.0)
    return reverb(p.entera(), 1.6, 0.25)


def pembe_dolor():
    """Le duele: un bramido corto y agudo."""
    return reverb(_bramido(0.7, 260, 420, 1.0) * 0.9, 1.4, 0.3)


def pembe_vencido():
    """El hierro se le cae y Pembe vuelve a ser el guardián del bosque: bramido que se calma y el bosque florece."""
    p = Pista(6.0)
    p.poner(_bramido(1.6, 300, 180, 0.9), 0.0, 1.0)
    for i in range(10):
        trozo = _crujido_piedra(0.3, 300, grave=False) * caida(_n(0.3), 0.08) * 0.5
        p.poner(trozo, 0.9 + i * 0.13, 1.0, pan=(i % 3 - 1) * 0.6)
    p.poner(_bramido(1.8, 160, 240, 0.2) * 0.6, 2.6, 1.0)
    for i, nota in enumerate(("E5", "G#5", "B5", "E6", "F#6", "G#6", "B6", "E7")):
        p.poner(campanita(nota, 1.8, 0.4), 3.2 + i * 0.12)
    return reverb(p.entera(), 3.0, 0.38)


def jabali_grunido():
    """El jabalí de hierro se prepara: gruñido corto y rasposo."""
    d = 0.5
    x = _rugido(d, 95, 130, 1.0) * 0.6 + paso_banda(ruido(d), 200, 900) * adsr(_n(d), 0.02, 0.1, 0.6, 0.2) * 0.4
    return reverb(x, 0.6, 0.12)


# =============================================================================
# LA CIÉNAGA QUIETA: Konokono, la caracola de óxido, y la sopa de Juncia
# =============================================================================

def _gorgoteo(dur, f0=90.0, f1=60.0, burbujas=18, semilla_g=4):
    """Una voz húmeda y grave: un tono que tiembla mucho, filtrado como bajo el agua, con burbujas."""
    n = _n(dur)
    rng = np.random.default_rng(semilla_g)
    f = _desliz(f0, f1, dur) * (1 + 0.12 * np.sin(2 * np.pi * 11 * t(dur)))
    voz = sierra(f, dur) * 0.5 + seno(f * 2, dur) * 0.3
    x = paso_banda(voz, 80, 700) * adsr(n, 0.08, 0.2, 0.8, dur * 0.4)
    for _ in range(burbujas):
        fb = rng.uniform(250, 900)
        d = rng.uniform(0.02, 0.06)
        m = _n(d)
        u = np.arange(m) / SR
        b = np.sin(2 * np.pi * np.cumsum(fb * (1 + 1.8 * u / d)) / SR) * np.exp(-u / (d * 0.4))
        i = rng.integers(0, max(1, n - m))
        x[i:i + m] += b * rng.uniform(0.1, 0.3)
    return x


def _concha(dur=0.4, f=180.0):
    """La concha que roza o golpea: un «toc» hueco de cerámica con un eco de hierro."""
    n = _n(dur)
    hueco = sum(seno(f * k, dur) * caida(n, 0.06 / k) * g for k, g in ((1, 0.6), (2.7, 0.25), (5.1, 0.1)))
    roce = paso_banda(ruido(dur), 900, 4000) * caida(n, 0.03) * 0.3
    return hueco + roce


def konokono_despierta():
    """Konokono despierta: un gorgoteo largo que sube desde el barro y la concha que cruje al moverse."""
    p = Pista(3.0)
    p.poner(_gorgoteo(2.2, 70, 110, 30), 0.0, 1.0)
    for i in range(5):
        p.poner(_crujido_piedra(0.25, 260, grave=True) * caida(_n(0.25), 0.1) * 0.5, 0.6 + i * 0.28, 1.0, pan=(i % 3 - 1) * 0.5)
    p.poner(_chapoteo(0.6, 1.0, 0.6), 1.9, 0.8)
    return reverb(p.entera(), 2.4, 0.35, 3500)


def konokono_rueda():
    """Se mete en la concha y sale rodando: un retumbo que crece y el barro que salpica."""
    d = 1.4
    p = Pista(d + 0.6)
    n = _n(d)
    retumbo = paso_bajo(ruido_rosa(d), 220) * np.linspace(0.3, 1.0, n) * 1.4
    giro = (0.6 + 0.4 * np.sin(2 * np.pi * _desliz(4, 12, d).cumsum() / SR))
    p.poner(retumbo * giro, 0.0, 1.0)
    p.poner(_concha(0.3, 160), 0.0, 0.9)
    for i in range(4):
        p.poner(_chapoteo(0.3, 0.6, 0.7), 0.35 + i * 0.28, 0.6, pan=(i % 2) * 0.8 - 0.4)
    return reverb(p.entera(), 1.2, 0.2)


def konokono_escondida():
    """Se esconde en la concha: un «chof» húmedo y un «toc» hueco."""
    p = Pista(0.9)
    p.poner(paso_banda(ruido(0.2), 200, 1200) * caida(_n(0.2), 0.05) * 0.7, 0.0)
    p.poner(_concha(0.5, 150), 0.08, 1.0)
    return reverb(p.entera(), 0.9, 0.2)


def konokono_traga():
    """Se traga la semilla: un «glup» que baja por la garganta."""
    d = 0.5
    glup = seno(_desliz(420, 110, d, 0.6), d) * adsr(_n(d), 0.01, 0.1, 0.6, 0.25) * 0.8
    garganta = np.pad(_gorgoteo(0.4, 120, 80, 6) * 0.4, (0, _n(d) - _n(0.4)))
    return reverb(paso_bajo(glup, 1400) + garganta, 0.7, 0.15)


def konokono_escupe():
    """Escupe una bola de óxido: un «ptú» húmedo con algo metálico."""
    d = 0.4
    p = Pista(0.7)
    p.poner(paso_banda(ruido(0.12), 500, 3500) * caida(_n(0.12), 0.03), 0.0, 0.9)
    p.poner(seno(_desliz(300, 700, 0.1), 0.1) * caida(_n(0.1), 0.04) * 0.6, 0.02, 1.0)
    p.poner(sum(seno(f, d) * caida(_n(d), 0.12) * g for f, g in ((640, 0.12), (980, 0.07))), 0.03, 1.0)
    return reverb(p.entera(), 0.8, 0.2)


def konokono_dolor():
    """Le duele (la semilla le estalla dentro): gorgoteo agudo y tembloroso."""
    return reverb(_gorgoteo(0.8, 160, 230, 14, 7) * 1.1, 1.2, 0.3)


def konokono_vencida():
    """La herrumbre se le cae, el agua se aclara y las ranas vuelven a cantar."""
    p = Pista(6.5)
    p.poner(_gorgoteo(1.4, 140, 90, 20, 2), 0.0, 1.0)
    for i in range(12):
        trozo = _crujido_piedra(0.25, 320, grave=False) * caida(_n(0.25), 0.07) * 0.45
        p.poner(trozo, 0.7 + i * 0.11, 1.0, pan=(i % 3 - 1) * 0.6)
    p.poner(_chapoteo(1.0, 1.4, 0.8), 2.1, 0.8)
    for i, nota in enumerate(("D5", "F#5", "A5", "D6", "E6", "F#6", "A6", "D7")):
        p.poner(campanita(nota, 1.8, 0.35), 2.6 + i * 0.12)
    for i in range(6):
        p.poner(_croar(0.18 + 0.03 * (i % 2), 150 + 30 * (i % 3)), 4.0 + i * 0.32, 0.5, pan=(i % 3 - 1) * 0.7)
    return reverb(p.entera(), 3.0, 0.35)


def _croar(dur=0.2, f=160.0):
    """Una rana: pulsos rápidos de un tono nasal."""
    n = _n(dur)
    pulsos = (np.sin(2 * np.pi * 38 * t(dur)) > 0.2).astype(float)
    voz = sierra(f, dur) * pulsos
    return paso_banda(voz, 300, 1800) * adsr(n, 0.01, 0.05, 0.8, 0.05) * 0.7


def babosa_chof():
    """La babosa de óxido avanza: un «chof» pegajoso."""
    return reverb(paso_banda(ruido(0.18), 250, 1500) * adsr(_n(0.18), 0.03, 0.05, 0.4, 0.1) * 0.6, 0.5, 0.1)


def sorber():
    """Maisha se toma la sopa: un sorbo, «ahh», y un brillito de vida."""
    p = Pista(1.0)
    p.poner(paso_banda(ruido(0.35), 800, 4500) * adsr(_n(0.35), 0.05, 0.1, 0.7, 0.15) * 0.5, 0.0)
    for i, nota in enumerate(("G5", "B5", "D6")):
        p.poner(campanita(nota, 0.8, 0.35), 0.35 + i * 0.08)
    return reverb(p.entera(), 1.0, 0.2)


def cienaga(dur=30.0):
    """La ciénaga: un zumbido bajo de agua quieta, gotas que caen, burbujas en el barro y alguna rana lejos."""
    rng = np.random.default_rng(13)
    n = _n(dur + 2)
    fondo = paso_bajo(ruido_rosa(dur + 2), 260) * 0.7
    x = fondo.copy()
    for _ in range(int(dur * 2.2)):            # gotas
        f = rng.uniform(900, 2200)
        d = rng.uniform(0.02, 0.05)
        m = _n(d)
        u = np.arange(m) / SR
        g = np.sin(2 * np.pi * np.cumsum(f * (1 + 1.2 * u / d)) / SR) * np.exp(-u / (d * 0.3))
        i = rng.integers(0, n - m)
        x[i:i + m] += g * rng.uniform(0.05, 0.18)
    for _ in range(int(dur * 1.2)):            # burbujas gordas del barro
        f = rng.uniform(120, 300)
        d = rng.uniform(0.06, 0.12)
        m = _n(d)
        u = np.arange(m) / SR
        b = np.sin(2 * np.pi * np.cumsum(f * (1 + 1.0 * u / d)) / SR) * np.exp(-u / (d * 0.4))
        i = rng.integers(0, n - m)
        x[i:i + m] += b * rng.uniform(0.08, 0.2)
    for _ in range(int(dur / 6)):              # ranas lejanas
        i = rng.integers(0, n - _n(0.6))
        c = _croar(0.2, rng.uniform(130, 190)) * 0.12
        x[i:i + len(c)] += c
        x[i + _n(0.3):i + _n(0.3) + len(c)] += c * 0.8
    y = np.stack([x, np.roll(x, 700)], axis=1)
    return _cerrar_bucle(reverb(y, 1.8, 0.3, 5000), dur)


# =============================================================================
# EL CAMPO SEGADO: la Cosechadora Oxidada (motor, cuchillas, vapor y chatarra)
# =============================================================================

def _motor(dur, f0=38.0, f1=38.0, aspereza=0.6):
    """Un motor viejo de vapor: pistonazos graves, traqueteo de chapa y un silbido."""
    n = _n(dur)
    f = _desliz(f0, f1, dur)
    fase = np.cumsum(f) / SR
    golpes = (np.sin(2 * np.pi * fase) > 0.6).astype(float)
    golpes = paso_bajo(golpes, 300) * 1.4
    chapa = paso_banda(ruido(dur), 900, 3500) * (0.5 + 0.5 * np.sin(2 * np.pi * fase * 2)) * 0.25 * aspereza
    fondo = paso_bajo(ruido_rosa(dur), 180) * 0.8
    return (golpes + chapa + fondo) * adsr(n, 0.05, 0.1, 0.9, 0.2)


def cosechadora_arranca():
    """Arranca: el motor tose, coge ritmo y suena el silbato de vapor."""
    p = Pista(2.8)
    p.poner(_motor(2.6, 12, 40, 0.7), 0.0, 1.0)
    silbato = (seno(_desliz(620, 660, 0.9), 0.9) * 0.5 + seno(_desliz(930, 990, 0.9), 0.9) * 0.3) * adsr(_n(0.9), 0.05, 0.1, 0.8, 0.3)
    p.poner(silbato + paso_banda(ruido(0.9), 2000, 6000) * 0.15 * adsr(_n(0.9), 0.02, 0.1, 0.7, 0.3), 1.4, 0.7)
    return reverb(p.entera(), 1.8, 0.3)


def cosechadora_tolva():
    """Abre la tolva de arriba: un chirrido de bisagra oxidada."""
    d = 0.6
    chirrido = sierra(_desliz(420, 260, d, 0.7), d) * (0.6 + 0.4 * np.sin(2 * np.pi * 31 * t(d)))
    return reverb(paso_banda(chirrido, 300, 2500) * adsr(_n(d), 0.02, 0.1, 0.6, 0.2) * 0.6, 0.9, 0.2)


def cosechadora_tuerca():
    """Una tuerca cae: «clonc» de hierro y la chatarra que se amontona."""
    p = Pista(0.8)
    p.poner(sum(seno(f, 0.5) * caida(_n(0.5), 0.12) * g for f, g in ((340, 0.4), (512, 0.3), (861, 0.2))), 0.0)
    p.poner(paso_banda(ruido(0.3), 500, 3000) * caida(_n(0.3), 0.06) * 0.5, 0.02)
    p.poner(_crujido_piedra(0.25, 260, grave=True) * caida(_n(0.25), 0.08) * 0.4, 0.06)
    return reverb(p.entera(), 0.8, 0.2)


def cosechadora_atascada():
    """Se enreda en los brotes: las cuchillas rechinan, el motor se ahoga y la caldera silba al abrirse."""
    p = Pista(2.0)
    p.poner(_motor(0.8, 40, 8, 1.0), 0.0, 0.9)
    rechina = sierra(_desliz(1200, 700, 0.5), 0.5) * adsr(_n(0.5), 0.01, 0.1, 0.6, 0.2)
    p.poner(paso_banda(rechina, 600, 4000) * 0.35, 0.05)
    vapor = paso_banda(ruido(1.2), 2500, 8000) * adsr(_n(1.2), 0.05, 0.2, 0.7, 0.6) * 0.5
    p.poner(vapor, 0.6)
    return reverb(p.entera(), 1.2, 0.25)


def cosechadora_ira():
    """Sube la Ira: el silbato, más agudo y furioso, y un pistonazo."""
    d = 0.8
    silbato = (seno(_desliz(780, 900, d), d) * 0.5 + seno(_desliz(1170, 1350, d), d) * 0.3) * adsr(_n(d), 0.02, 0.1, 0.8, 0.3)
    p = Pista(1.2)
    p.poner(taiko(0.8, 0.9), 0.0, 0.8)
    p.poner(silbato, 0.05, 0.7)
    return reverb(p.entera(), 1.4, 0.3)


def cosechadora_embiste():
    """Frenesí: acelera a fondo (el motor sube y sube)."""
    return reverb(_motor(1.4, 30, 110, 1.0), 0.8, 0.15)


def cosechadora_choque():
    """Se estampa contra el borde: golpe de chapa enorme."""
    p = Pista(1.8)
    p.poner(taiko(1.2, 1.0), 0.0, 1.0)
    p.poner(sum(seno(f, 1.5) * caida(_n(1.5), 0.4) * g for f, g in ((180, 0.35), (271, 0.25), (433, 0.18), (690, 0.1))), 0.0, 1.0)
    p.poner(paso_banda(ruido(0.5), 300, 3000) * caida(_n(0.5), 0.1) * 0.6, 0.0)
    return reverb(p.entera(), 1.6, 0.3)


def cosechadora_dolor():
    """Le dan en la caldera: un estallido de vapor y un quejido de metal."""
    p = Pista(1.0)
    p.poner(paso_banda(ruido(0.5), 1500, 7000) * caida(_n(0.5), 0.15) * 0.7, 0.0)
    quejido = sierra(_desliz(260, 140, 0.6), 0.6) * adsr(_n(0.6), 0.01, 0.1, 0.6, 0.3)
    p.poner(paso_banda(quejido, 150, 1500) * 0.5, 0.03)
    return reverb(p.entera(), 1.0, 0.25)


def cosechadora_vencida():
    """Se apaga: el motor se para, la caldera suspira, la chapa cruje... y crece el trigo (campanitas)."""
    p = Pista(6.5)
    p.poner(_motor(1.8, 40, 6, 0.8), 0.0, 1.0)
    p.poner(paso_banda(ruido(1.6), 1800, 7000) * adsr(_n(1.6), 0.05, 0.3, 0.6, 1.0) * 0.5, 1.2)
    for i in range(10):
        p.poner(_crujido_piedra(0.3, 280, grave=True) * caida(_n(0.3), 0.08) * 0.4, 1.6 + i * 0.15, 1.0, pan=(i % 3 - 1) * 0.6)
    for i, nota in enumerate(("G4", "B4", "D5", "G5", "A5", "B5", "D6", "G6")):
        p.poner(campanita(nota, 2.0, 0.4), 3.4 + i * 0.13)
    return reverb(p.entera(), 3.0, 0.35)


def comprar():
    """Comprar en la tienda de Tawi: cristales que tintinean al caer en la bolsa y un «¡chin!»."""
    p = Pista(1.2)
    for i, nota in enumerate(("E6", "B6", "G#6", "E7")):
        p.poner(campanita(nota, 0.7, 0.35), 0.0 + i * 0.06)
    for i in range(5):
        p.poner(seno(2800 + i * 310, 0.12) * caida(_n(0.12), 0.03) * 0.25, 0.25 + i * 0.05, 1.0, pan=(i % 3 - 1) * 0.5)
    p.poner(paso_banda(ruido(0.2), 400, 2000) * caida(_n(0.2), 0.05) * 0.3, 0.45)
    return reverb(p.entera(), 1.0, 0.25)


def cristal():
    """Se ganan Cristales del Nexo: un brillo frío de cristal."""
    p = Pista(1.0)
    for i, nota in enumerate(("B5", "F#6", "B6")):
        p.poner(campanita(nota, 0.9, 0.3), i * 0.08)
    p.poner(seno(4200, 0.4) * caida(_n(0.4), 0.15) * 0.08, 0.1)
    return reverb(p.entera(), 1.2, 0.3)


def cosechadora_fuego():
    """El acelerón infernal: un «fuuum» de llamarada que se enciende y crepita."""
    d = 1.6
    n = _n(d)
    rugido = paso_banda(ruido_rosa(d), 120, 1800) * adsr(n, 0.08, 0.3, 0.6, 0.6) * 1.2
    barrido = paso_banda(ruido(d), 800, 5000) * np.interp(np.arange(n), [0, n * 0.15, n], [0, 1, 0]) * 0.4
    x = rugido + barrido
    rng = np.random.default_rng(31)
    for _ in range(40):
        i = rng.integers(_n(0.2), n - 400)
        largo = rng.integers(60, 300)
        x[i:i + largo] += paso_banda(rng.normal(0, 1, largo), 1500, 7000) * np.exp(-np.arange(largo) / rng.uniform(15, 60)) * rng.uniform(0.1, 0.35)
    return reverb(x, 1.0, 0.2)


def fuego_quema():
    """Maisha pisa el fuego: un chisporroteo corto."""
    d = 0.35
    x = paso_banda(ruido(d), 2000, 8000) * caida(_n(d), 0.08) * 0.6 + paso_banda(ruido_rosa(d), 200, 1500) * caida(_n(d), 0.12) * 0.4
    return reverb(x, 0.5, 0.15)


def rana_croa():
    """La rana de piedra croa: dos «crooac» graves y rasposos, como piedra que rechina."""
    p = Pista(0.6)
    for k, dt in enumerate((0.0, 0.22)):
        d = 0.16
        base = sierra(_desliz(140 - k * 20, 90, d), d, 12) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 45 * t(d))))
        p.poner(paso_bajo(base, 1200) * adsr(_n(d), 0.01, 0.05, 0.6, 0.06) * 0.55, dt)
    return reverb(p.entera(), 0.6, 0.15)


def rana_salta():
    """Salta: un «fuuup» que sube."""
    d = 0.3
    return paso_banda(ruido(d), 400, 3000) * np.linspace(0, 1, _n(d)) ** 0.5 * caida(_n(d), 0.25) * 0.4 + \
        seno(_desliz(200, 520, d), d) * caida(_n(d), 0.15) * 0.25


def rana_cae():
    """Aterriza: un golpe de piedra contra la madera, con salpicadura."""
    d = 0.45
    golpe = paso_bajo(ruido_rosa(d), 600) * caida(_n(d), 0.08) * 0.9
    chapoteo = paso_banda(ruido(d), 1500, 6000) * caida(_n(d), 0.18) * 0.35
    return reverb(golpe + chapoteo, 0.5, 0.15)


def eco_voz():
    """Un eco perdido despierta: campanitas que se repiten cada vez más lejos y un coro muy suave que sube."""
    p = Pista(3.2)
    for k, (nota, dt) in enumerate((("E6", 0.0), ("B5", 0.18), ("G#5", 0.42), ("E5", 0.7))):
        p.poner(campanita(nota, 1.6), dt, 0.55 * (0.82 ** k))
        p.poner(campanita(nota, 1.2), dt + 0.9, 0.18 * (0.82 ** k))       # el eco de cada nota
    d = 2.6
    f = 330.0
    voz = (seno(f, d) * 0.5 + seno(f * 1.5, d) * 0.3 + seno(f * 2.0, d) * 0.15) * adsr(_n(d), 1.1, 0.4, 0.6, 1.0)
    p.poner(paso_bajo(voz, 1800) * 0.18, 0.3, 1.0)
    return reverb(p.entera(), 2.4, 0.45)


def _papel(d, f0=1500, f1=7000, ataque=0.01):
    x = paso_banda(ruido(d), f0, f1)
    env = np.minimum(np.linspace(0, 1, _n(d)) / max(ataque / d, 1e-3), 1.0) * np.linspace(1, 0, _n(d)) ** 1.5
    return x * env


def topo_excava():
    """El topo de piedra cava bajo tierra: un rascar sordo y grave de tierra y piedrecitas."""
    p = Pista(0.7)
    for k in range(5):
        d = 0.08 + (k % 2) * 0.04
        p.poner(paso_banda(ruido_rosa(d), 150, 1400) * caida(_n(d), d * 0.5) * 0.7, k * 0.11)
        p.poner(paso_banda(ruido(0.03), 2500, 7000) * caida(_n(0.03), 0.01) * 0.2, k * 0.11 + 0.03)
    return reverb(p.entera(), 0.3, 0.1)


def topo_sale():
    """El topo sale de golpe: un reventón de tierra, piedras que saltan y un chasquido de dientes."""
    p = Pista(0.8)
    p.poner(paso_bajo(ruido_rosa(0.35), 700) * caida(_n(0.35), 0.1) * 1.0, 0.0)
    p.poner(seno(90, 0.2) * caida(_n(0.2), 0.06) * 0.5, 0.0)
    for k in range(4):
        p.poner(paso_banda(ruido(0.04), 1800, 6000) * caida(_n(0.04), 0.012) * 0.3, 0.06 + k * 0.07)
    p.poner(paso_banda(ruido(0.03), 3000, 9000) * caida(_n(0.03), 0.008) * 0.5, 0.12)    # el mordisco
    return reverb(p.entera(), 0.4, 0.12)


def campanilla():
    """Una campanilla de cobre de Fuko: un tilín cálido, con su vibrato."""
    p = Pista(1.4)
    p.poner(campanita("E6", 1.2, 0.5), 0.0)
    p.poner(campanita("B6", 1.0, 0.25), 0.05)
    p.poner(campanita("E6", 0.8, 0.2), 0.32)
    return reverb(p.entera(), 1.0, 0.25)


def cuervo_graznido():
    """El cuervo de óxido grazna: un «craa» áspero y metálico, con un chirrido de hierro."""
    p = Pista(0.6)
    for k, d in enumerate((0.16, 0.12)):
        n = _n(d)
        t = np.arange(n) / 44100
        base = np.sign(np.sin(2 * np.pi * (520 - 180 * t / d) * t)) * 0.3
        x = paso_banda(base + ruido(d) * 0.5, 700, 3200) * adsr(n, 0.01, 0.05, 0.6, 0.4)
        p.poner(x * 0.7, k * 0.2)
    p.poner(paso_banda(ruido(0.08), 4000, 9000) * caida(_n(0.08), 0.03) * 0.15, 0.05)
    return reverb(p.entera(), 0.5, 0.15)


def cuervo_picado():
    """El picado: un silbido de aire que sube y un aleteo de hierro."""
    d = 0.5
    n = _n(d)
    silbido = paso_banda(ruido(d), 1500, 6000) * np.interp(np.arange(n), [0, n * 0.7, n], [0, 1, 0]) * 0.5
    aleteo = paso_bajo(ruido_rosa(d), 500) * (np.sin(np.arange(n) / 44100 * 2 * np.pi * 14) > 0.6) * 0.4
    return reverb(silbido + aleteo, 0.4, 0.12)


def agua_baja():
    """La compuerta se cierra y el foso se vacía: un crujido de madera y un gorgoteo largo que se apaga."""
    p = Pista(3.0)
    p.poner(paso_banda(ruido(0.25), 300, 1500) * caida(_n(0.25), 0.1) * 0.5, 0.0)
    rng = np.random.default_rng(5)
    for k in range(26):
        f = 250 + rng.random() * 500
        d = 0.06 + rng.random() * 0.06
        t = np.arange(_n(d)) / 44100
        burbuja = np.sin(2 * np.pi * (f + 900 * t / d) * t) * caida(_n(d), d * 0.4)
        p.poner(burbuja * 0.35 * (1 - k / 30), 0.2 + k * 0.1 + rng.random() * 0.05)
    p.poner(paso_banda(ruido_rosa(2.6), 200, 1200) * np.linspace(0.4, 0, _n(2.6)), 0.2)
    return reverb(p.entera(), 0.8, 0.2)


def pagina():
    """Pasar una hoja del diario: un roce de papel que sube y un golpecito suave al caer."""
    p = Pista(0.45)
    d = 0.32
    x = _papel(d, 1200, 6500, 0.12) * (0.6 + 0.4 * np.sin(np.linspace(0, 9, _n(d))) ** 2)
    p.poner(x * 0.7, 0.0)
    p.poner(paso_bajo(ruido_rosa(0.06), 900) * caida(_n(0.06), 0.02) * 0.6, 0.3)
    return reverb(p.entera(), 0.4, 0.12)


def pluma():
    """La pluma que escribe en el diario: rasguños cortos y secos sobre el papel, a trompicones."""
    p = Pista(0.7)
    t = 0.0
    k = 0
    while t < 0.6:
        d = 0.03 + (k % 3) * 0.018
        x = paso_banda(ruido(d), 2500, 9000) * caida(_n(d), d * 0.6) * (0.35 + 0.25 * (k % 2))
        p.poner(x, t)
        t += d + 0.02 + (k % 4) * 0.012
        k += 1
    return reverb(p.entera(), 0.3, 0.1)


def libro_abrir():
    """Abrir el diario: el crujido del cuero, la tapa que gira y las hojas que se asientan."""
    p = Pista(0.9)
    p.poner(paso_banda(ruido(0.18), 300, 1800) * caida(_n(0.18), 0.08) * 0.5, 0.0)          # cuero que cruje
    p.poner(_papel(0.4, 900, 5000, 0.15) * 0.55, 0.12)
    p.poner(paso_bajo(ruido_rosa(0.09), 500) * caida(_n(0.09), 0.03) * 0.9, 0.5)            # la tapa cae
    p.poner(_papel(0.2, 2000, 8000, 0.05) * 0.25, 0.55)
    return reverb(p.entera(), 0.5, 0.15)


def libro_cerrar():
    """Cerrar el diario: hojas que se juntan y un golpe seco de la tapa."""
    p = Pista(0.6)
    p.poner(_papel(0.22, 1000, 6000, 0.08) * 0.45, 0.0)
    p.poner(paso_bajo(ruido_rosa(0.12), 450) * caida(_n(0.12), 0.035) * 1.0, 0.18)
    p.poner(seno(110, 0.12) * caida(_n(0.12), 0.03) * 0.35, 0.18)
    return reverb(p.entera(), 0.5, 0.15)


# =============================================================================
# CAÑADA DEL ECO: el murciélago de eco, la onda, los cencerros y la escala de cuerda
# =============================================================================

def murcielago_chillido():
    """El murciélago de eco despierta o avisa: tres chirridos agudos, muy rápidos, y la peña que los repite."""
    p = Pista(1.2)
    for k in range(3):
        d = 0.05
        f = _desliz(4200 - k * 300, 6800 - k * 500, d, 0.6)
        x = seno(f, d) * adsr(_n(d), 0.003, 0.02, 0.5, 0.02)
        x = x + paso_banda(ruido(d), 3000, 8000) * caida(_n(d), 0.01) * 0.25
        p.poner(x * 0.5, k * 0.07)
        p.poner(x * 0.16, 0.38 + k * 0.07)            # el eco de la peña, más lejos
        p.poner(x * 0.06, 0.72 + k * 0.07)
    return reverb(p.entera(), 1.4, 0.3)


def murcielago_grito():
    """El grito que suelta la onda: un chillido que baja y vuelve a subir, áspero y con anillo de piedra."""
    d = 0.42
    n = _n(d)
    u = np.linspace(0, 1, n)
    f = 2600 * (1 - 0.45 * np.sin(u * np.pi)) + 300 * np.sin(u * 2 * np.pi * 18)
    x = seno(f, d) * 0.6 + seno(f * 1.5, d) * 0.25
    x = x * (0.6 + 0.4 * np.sin(2 * np.pi * 70 * u * d))      # el anillo: un temblor rápido
    x = x * adsr(n, 0.01, 0.1, 0.7, 0.15)
    x = x + paso_banda(ruido(d), 1500, 5000) * adsr(n, 0.01, 0.1, 0.4, 0.15) * 0.25
    p = Pista(1.6)
    p.poner(x * 0.7, 0.0)
    p.poner(paso_bajo(x, 3500) * 0.22, 0.5)
    return reverb(p.entera(), 1.8, 0.35)


def onda_rebota():
    """La onda choca con la peña y se da la vuelta: un toc hueco de piedra y un silbido que se aleja al revés."""
    p = Pista(0.9)
    toc = seno(_desliz(420, 180, 0.12), 0.12) * caida(_n(0.12), 0.04) * 0.6
    p.poner(toc, 0.0)
    p.poner(paso_bajo(ruido_rosa(0.08), 900) * caida(_n(0.08), 0.02) * 0.6, 0.0)
    d = 0.4
    silbido = paso_banda(ruido(d), 1800, 6000) * np.linspace(0, 1, _n(d)) ** 2 * 0.3
    p.poner(silbido[::-1] * 0.8, 0.05)
    return reverb(p.entera(), 1.2, 0.3)


def murcielago_mareo():
    """Se traga su propio eco y se marea: un pitido que baja dando tumbos y un golpecito de piedra contra el suelo."""
    p = Pista(1.2)
    d = 0.7
    u = np.linspace(0, 1, _n(d))
    f = 1800 * (1 - 0.6 * u) * (1 + 0.08 * np.sin(2 * np.pi * 7 * u * d))
    p.poner(seno(f, d) * adsr(_n(d), 0.02, 0.1, 0.6, 0.3) * 0.35, 0.0)
    p.poner(paso_bajo(ruido_rosa(0.1), 700) * caida(_n(0.1), 0.03) * 0.7, 0.62)
    p.poner(seno(140, 0.1) * caida(_n(0.1), 0.03) * 0.4, 0.62)
    return reverb(p.entera(), 0.9, 0.25)


def murcielago_aleteo():
    """Despega: tres aletazos de piel, sordos y rápidos."""
    p = Pista(0.6)
    for k in range(3):
        d = 0.09
        x = paso_bajo(ruido_rosa(d), 700 + k * 100) * np.sin(np.linspace(0, np.pi, _n(d))) ** 2
        p.poner(x * 0.8, k * 0.12)
    return reverb(p.entera(), 0.5, 0.15)


def cencerro():
    """Un cencerro de Mbuzi: un «clonc» hueco de cobre viejo, con el badajo que repica dos veces."""
    p = Pista(1.6)
    for k, (dt, fuerza) in enumerate(((0.0, 0.6), (0.14, 0.35), (0.26, 0.18))):
        d = 1.0
        n = _n(d)
        x = (seno(620, d) * caida(n, 0.35) + 0.6 * seno(620 * 2.37, d) * caida(n, 0.18) +
             0.35 * seno(620 * 3.9, d) * caida(n, 0.08) + 0.25 * seno(310, d) * caida(n, 0.25))
        golpe = paso_banda(ruido(0.03), 1200, 5000) * caida(_n(0.03), 0.008)
        p.poner(x * fuerza * 0.5, dt)
        p.poner(golpe * fuerza, dt)
    return reverb(p.entera(), 1.6, 0.3)


def escala_tramo():
    """Un tramo de la escala de cuerda que se desenrolla: el zumbido de la cuerda y el peldaño que golpea la roca."""
    p = Pista(0.5)
    d = 0.14
    p.poner(paso_banda(ruido(d), 500, 2500) * np.linspace(0, 1, _n(d)) * 0.25, 0.0)
    toc = seno(_desliz(380, 260, 0.08), 0.08) * caida(_n(0.08), 0.025) * 0.5
    p.poner(toc, 0.13)
    p.poner(paso_banda(ruido(0.05), 800, 4000) * caida(_n(0.05), 0.012) * 0.5, 0.13)
    return reverb(p.entera(), 0.8, 0.2)


EFECTOS = {
    "dialogo_pasar": (dialogo_pasar, 0.5), "dialogo_cerrar": (dialogo_cerrar, 0.45),
    "menu_mover": (menu_mover, 0.35), "menu_aceptar": (menu_aceptar, 0.55), "menu_atras": (menu_atras, 0.5),
    "mochila_abrir": (mochila_abrir, 0.55), "mochila_cerrar": (mochila_cerrar, 0.5), "pausa": (pausa, 0.5),
    "cetro_golpe": (cetro_golpe, 0.45), "golpe_acierto": (golpe_acierto, 0.75), "clinc": (clinc, 0.55),
    "semilla_plantar": (semilla_plantar, 0.6), "semilla_mecha": (semilla_mecha, 0.35), "explosion": (explosion, 0.95),
    "brotes": (brotes, 0.4), "latido": (latido, 0.8), "maisha_herida": (maisha_herida, 0.7), "maisha_cae": (maisha_cae, 0.6),
    "recoger": (recoger, 0.6), "esencia": (esencia, 0.6), "puerta": (puerta, 0.5),
    "petrino_aparece": (petrino_aparece, 0.75), "petrino_golpeado": (petrino_golpeado, 0.65),
    "petrino_muere": (petrino_muere, 0.75), "petrino_embiste": (petrino_embiste, 0.5),
    "zona_aviso": (zona_aviso, 0.6), "espinas_suben": (espinas_suben, 0.85),
    "corazon_golpeado": (corazon_golpeado, 0.8), "corazon_roto": (corazon_roto, 0.85), "ola_purga": (ola_purga, 0.55),
    "mzizi_rugido": (mzizi_rugido, 0.95), "mzizi_dolor": (mzizi_dolor, 0.9), "mzizi_aviso": (mzizi_aviso, 0.8),
    "mzizi_sale": (mzizi_sale, 0.95), "mzizi_escupe": (mzizi_escupe, 0.7), "piedra_rompe": (piedra_rompe, 0.55),
    "mzizi_vencido": (mzizi_vencido, 0.9), "temblor": (temblor, 0.85), "portal_abre": (portal_abre, 0.75),
    "pesca_lanzar": (pesca_lanzar, 0.6), "pesca_espera": (pesca_espera, 0.3), "pesca_pica": (pesca_pica, 0.7),
    "pesca_saca": (pesca_saca, 0.75), "pesca_escapa": (pesca_escapa, 0.6), "zanahoria_arrancar": (zanahoria_arrancar, 0.7),
    "tablas_coger": (tablas_coger, 0.7), "cerca_martillo": (cerca_martillo, 0.8), "cerca_arreglada": (cerca_arreglada, 0.5),
    "espantapajaros_golpe": (espantapajaros_golpe, 0.6), "seta_recoger": (seta_recoger, 0.55), "mineral_romper": (mineral_romper, 0.7),
    "entregar": (entregar, 0.55), "construir": (construir, 0.8), "estatua_despierta": (estatua_despierta, 0.8),
    "chispa": (chispa, 0.45), "chispa_entra": (chispa_entra, 0.6), "gallina_cacareo": (gallina_cacareo, 0.6),
    "gallina_asustada": (gallina_asustada, 0.6), "llamar_puerta": (llamar_puerta, 0.7), "sopa": (sopa, 0.4),
    "mision_nueva": (mision_nueva, 0.55), "mision_cumplida": (mision_cumplida, 0.6), "mision_paso": (mision_paso, 0.45),
    "rueda_abrir": (rueda_abrir, 0.4), "meditar": (meditar, 0.55), "arte_sube": (arte_sube, 0.65),
    "pembe_bramido": (pembe_bramido, 0.9), "pembe_escarba": (pembe_escarba, 0.6), "pembe_galope": (pembe_galope, 0.75),
    "pembe_choque": (pembe_choque, 0.9), "pembe_dolor": (pembe_dolor, 0.8), "pembe_vencido": (pembe_vencido, 0.85),
    "jabali_grunido": (jabali_grunido, 0.65),
    "konokono_despierta": (konokono_despierta, 0.9), "konokono_rueda": (konokono_rueda, 0.85),
    "konokono_escondida": (konokono_escondida, 0.7), "konokono_traga": (konokono_traga, 0.75),
    "konokono_escupe": (konokono_escupe, 0.65), "konokono_dolor": (konokono_dolor, 0.8),
    "konokono_vencida": (konokono_vencida, 0.85), "babosa_chof": (babosa_chof, 0.4), "sorber": (sorber, 0.55),
    "cosechadora_arranca": (cosechadora_arranca, 0.85), "cosechadora_tolva": (cosechadora_tolva, 0.55),
    "cosechadora_tuerca": (cosechadora_tuerca, 0.6), "cosechadora_atascada": (cosechadora_atascada, 0.8),
    "cosechadora_ira": (cosechadora_ira, 0.75), "cosechadora_embiste": (cosechadora_embiste, 0.8),
    "cosechadora_choque": (cosechadora_choque, 0.9), "cosechadora_dolor": (cosechadora_dolor, 0.8),
    "cosechadora_vencida": (cosechadora_vencida, 0.85), "cosechadora_fuego": (cosechadora_fuego, 0.8),
    "fuego_quema": (fuego_quema, 0.6),
    "comprar": (comprar, 0.6), "cristal": (cristal, 0.5),
    "eco_voz": (eco_voz, 0.6),
    "pagina": (pagina, 0.5), "libro_abrir": (libro_abrir, 0.6), "libro_cerrar": (libro_cerrar, 0.6), "pluma": (pluma, 0.35), "topo_excava": (topo_excava, 0.55), "topo_sale": (topo_sale, 0.85), "campanilla": (campanilla, 0.5), "cuervo_graznido": (cuervo_graznido, 0.6), "cuervo_picado": (cuervo_picado, 0.7), "agua_baja": (agua_baja, 0.6), "rana_croa": (rana_croa, 0.6), "rana_salta": (rana_salta, 0.5), "rana_cae": (rana_cae, 0.8),
    "murcielago_chillido": (murcielago_chillido, 0.55), "murcielago_grito": (murcielago_grito, 0.7),
    "onda_rebota": (onda_rebota, 0.6), "murcielago_mareo": (murcielago_mareo, 0.6),
    "murcielago_aleteo": (murcielago_aleteo, 0.5), "cencerro": (cencerro, 0.6), "escala_tramo": (escala_tramo, 0.6),
}

AMBIENTES = {
    "pajaros": lambda: pajaros(36.0, 1.0),
    "viento": viento,
    "fuego": fuego,
    "agua": agua,
    "brisa": brisa,
    "cienaga": cienaga,
}


if __name__ == "__main__":
    solo = sys.argv[1:]
    for nombre, (funcion, pico) in EFECTOS.items():
        if solo and nombre not in solo:
            continue
        semilla(sum(ord(c) * (i + 1) for i, c in enumerate(nombre)))
        x = suavizar_bordes(estereo(funcion()), 0.002, 0.02)
        guardar(x, os.path.join(DESTINO, "sonidos", nombre + ".ogg"), pico)
        print("efecto:", nombre)
    for nombre, funcion in AMBIENTES.items():
        if solo and nombre not in solo:
            continue
        semilla(len(nombre))
        guardar(funcion(), os.path.join(DESTINO, "ambiente", nombre + ".ogg"), 0.7)
        print("ambiente:", nombre)
