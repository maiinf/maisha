"""
SINTETIZADOR de Maisha: instrumentos y efectos hechos con matemáticas (numpy), sin muestras de nadie.
Todo lo que suena en el juego sale de aquí, así que es nuestro: no hay derechos de terceros.

Lo usan herramientas/crear_sonidos.py (efectos y ambientes) y herramientas/componer_musica.py (música).
"""
import os
import shutil
import subprocess
import wave

import numpy as np
from scipy import signal

SR = 44100
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_azar = np.random.default_rng(7)


def semilla(n):
    global _azar
    _azar = np.random.default_rng(n)


# --- notas -------------------------------------------------------------------------
NOTAS = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
         "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def hz(nota):
    """'A4' → 440. También acepta números (ya en Hz)."""
    if not isinstance(nota, str):
        return float(nota)
    nombre, octava = nota[:-1], int(nota[-1])
    n = NOTAS[nombre] + (octava + 1) * 12
    return 440.0 * 2 ** ((n - 69) / 12)


def t(dur):
    return np.arange(int(dur * SR)) / SR


# --- osciladores y envolventes -------------------------------------------------------
def seno(f, dur, fase=0.0):
    f = np.broadcast_to(np.asarray(f, dtype=float), (int(dur * SR),)) if np.ndim(f) else f
    if np.ndim(f):
        return np.sin(2 * np.pi * np.cumsum(f) / SR + fase)
    return np.sin(2 * np.pi * f * t(dur) + fase)


def sierra(f, dur, armonicos=12):
    x = np.zeros(int(dur * SR))
    for k in range(1, armonicos + 1):
        x += seno(np.asarray(f) * k, dur) / k * (1 if k % 2 else -1)
    return x * 0.6


def triangulo(f, dur, armonicos=7):
    x = np.zeros(int(dur * SR))
    for i, k in enumerate(range(1, armonicos * 2, 2)):
        x += seno(np.asarray(f) * k, dur) / (k * k) * (1 if i % 2 == 0 else -1)
    return x * 0.8


def ruido(dur):
    return _azar.uniform(-1, 1, int(dur * SR))


def ruido_rosa(dur):
    blanco = _azar.normal(0, 1, int(dur * SR))
    b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, blanco) * 0.25


def adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    s_n = max(0, n - a - d - r)
    env = np.concatenate([np.linspace(0, 1, max(1, a)), np.linspace(1, s, max(1, d)), np.full(s_n, s), np.linspace(s, 0, max(1, r))])
    return np.pad(env, (0, max(0, n - len(env))))[:n]


def caida(n, segundos):
    return np.exp(-np.arange(n) / SR / max(1e-4, segundos))


def subida(n, segundos):
    return np.clip(np.arange(n) / SR / max(1e-4, segundos), 0, 1)


# --- filtros -----------------------------------------------------------------------
def paso_bajo(x, corte, orden=2):
    corte = np.clip(corte, 20, SR / 2 - 100)
    b, a = signal.butter(orden, corte / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def paso_alto(x, corte, orden=2):
    b, a = signal.butter(orden, corte / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def paso_banda(x, bajo, alto, orden=2):
    b, a = signal.butter(orden, [bajo / (SR / 2), alto / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def barrido_bajo(x, desde, hasta, trozos=64):
    """Filtro paso bajo cuyo corte se mueve de «desde» a «hasta» (abrir o cerrar el sonido)."""
    out = np.zeros_like(x)
    largo = len(x) // trozos + 1
    zi = None
    for i in range(trozos):
        corte = desde * (hasta / desde) ** (i / max(1, trozos - 1))
        b, a = signal.butter(2, np.clip(corte, 30, SR / 2 - 200) / (SR / 2), "low")
        trozo = x[i * largo:(i + 1) * largo]
        if zi is None:
            zi = signal.lfilter_zi(b, a) * 0
        y, zi = signal.lfilter(b, a, trozo, zi=zi)
        out[i * largo:i * largo + len(y)] = y
    return out


# --- instrumentos ------------------------------------------------------------------
def kalimba(nota, dur=1.6, fuerza=1.0):
    """Lámina de kalimba: fundamental, parciales inarmónicos y un golpecito al principio."""
    f = hz(nota)
    n = int(dur * SR)
    x = seno(f, dur) * caida(n, dur * 0.42)
    x += 0.25 * seno(f * 2.0, dur) * caida(n, dur * 0.18)
    x += 0.14 * seno(f * 5.42, dur) * caida(n, 0.09)
    x += 0.06 * seno(f * 9.7, dur) * caida(n, 0.03)
    golpe = paso_alto(ruido(0.01), 2500) * caida(int(0.01 * SR), 0.002) * 0.3
    x[:len(golpe)] += golpe
    return x * adsr(n, 0.002, 0.05, 1.0, 0.05) * fuerza


def balafon(nota, dur=0.9, fuerza=1.0):
    """Balafón (marimba de madera): cálido y seco."""
    f = hz(nota)
    n = int(dur * SR)
    x = seno(f, dur) * caida(n, 0.35) + 0.35 * seno(f * 3.9, dur) * caida(n, 0.06) + 0.12 * seno(f * 10.2, dur) * caida(n, 0.015)
    return x * adsr(n, 0.003, 0.05, 1.0, 0.03) * fuerza


def flauta(nota, dur=1.0, fuerza=1.0, vibrato=5.0):
    f = hz(nota)
    n = int(dur * SR)
    vib = 1 + 0.006 * np.sin(2 * np.pi * vibrato * t(dur)) * subida(n, 0.35)
    x = seno(f * vib, dur) + 0.18 * seno(f * 2 * vib, dur) + 0.05 * seno(f * 3 * vib, dur)
    soplo = paso_banda(ruido(dur), f * 0.8, min(f * 4, 12000)) * 0.12
    return (x + soplo) * adsr(n, 0.08, 0.1, 0.8, min(0.25, dur * 0.4)) * fuerza


def colchon(notas, dur, brillo=1200.0, ataque=1.5, salida=1.5, fuerza=1.0):
    """Colchón de cuerdas suaves: sierras desafinadas y filtradas, que entran y salen despacio."""
    n = int(dur * SR)
    x = np.zeros(n)
    for nota in notas:
        f = hz(nota)
        for d in (-0.15, 0.0, 0.17):
            lfo = 1 + 0.0015 * np.sin(2 * np.pi * (0.13 + d) * t(dur) + d * 9)
            x += sierra(f * (1 + d / 100) * lfo, dur, armonicos=8)
    x = paso_bajo(x / (3 * len(notas)), brillo)
    return x * adsr(n, ataque, 0.1, 1.0, salida) * fuerza


def coro(notas, dur, vocal="u", fuerza=1.0):
    """Voces sin palabras (un «uuu» u «ooo»): para lo misterioso y para Giza."""
    formantes = {"u": [(300, 90), (870, 120)], "o": [(450, 100), (800, 120)], "a": [(730, 110), (1090, 130)]}[vocal]
    n = int(dur * SR)
    x = np.zeros(n)
    for nota in notas:
        f = hz(nota)
        for d in (-0.2, 0.1):
            vib = 1 + 0.004 * np.sin(2 * np.pi * (4.6 + d) * t(dur))
            x += sierra(f * (1 + d / 100) * vib, dur, armonicos=20)
    y = sum(paso_banda(x, max(40, c - b), c + b) for c, b in formantes)
    return y / (2 * len(notas)) * adsr(n, 1.0, 0.1, 1.0, 1.2) * fuerza


def bajo(nota, dur, fuerza=1.0):
    f = hz(nota)
    n = int(dur * SR)
    x = seno(f, dur) + 0.3 * seno(f * 2, dur) + 0.1 * triangulo(f, dur)
    return x * adsr(n, 0.01, 0.2, 0.6, 0.15) * fuerza


def tambor(nota="A2", dur=0.5, fuerza=1.0, golpe=0.3):
    """Tambor de mano (djembe/tambor grave): un tono que cae y un poco de piel."""
    f = hz(nota)
    n = int(dur * SR)
    caer = f * (1 + 1.2 * caida(n, 0.03))
    x = seno(caer, dur) * caida(n, dur * 0.35)
    piel = paso_banda(ruido(dur), 200, 3000) * caida(n, 0.02) * golpe
    return (x + piel) * fuerza


def taiko(dur=1.2, fuerza=1.0):
    n = int(dur * SR)
    caer = 55 * (1 + 0.8 * caida(n, 0.05))
    x = seno(caer, dur) * caida(n, 0.45) + 0.4 * paso_bajo(ruido(dur), 300) * caida(n, 0.12)
    return x * fuerza


def maraca(dur=0.12, fuerza=1.0):
    n = int(dur * SR)
    return paso_alto(ruido(dur), 5000) * caida(n, 0.03) * adsr(n, 0.004, 0.02, 0.8, 0.02) * fuerza


def campanita(nota, dur=1.5, fuerza=1.0):
    f = hz(nota)
    n = int(dur * SR)
    x = seno(f, dur) * caida(n, dur * 0.4) + 0.4 * seno(f * 2.76, dur) * caida(n, dur * 0.2) + 0.2 * seno(f * 5.4, dur) * caida(n, dur * 0.08)
    return x * adsr(n, 0.001, 0.05, 1, 0.05) * fuerza


# --- espacio ---------------------------------------------------------------------------
def _ir(segundos, brillo, semilla_ir):
    rng = np.random.default_rng(semilla_ir)
    n = int(segundos * SR)
    ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR / (segundos / 6.5))
    ir = paso_bajo(ir, brillo)
    ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    return ir / np.sqrt(np.sum(ir ** 2))


def reverb(x, segundos=2.5, mezcla=0.3, brillo=6000):
    """Devuelve estéreo (n, 2): la señal seca en el centro y una sala grande alrededor."""
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    out = np.zeros((len(x) + int(segundos * SR), 2))
    for c in range(2):
        mojado = signal.fftconvolve(x[:, c], _ir(segundos, brillo, 11 + c))
        out[:len(mojado), c] += mojado[:len(out)] * mezcla
        out[:len(x), c] += x[:, c] * (1 - mezcla * 0.5)
    return out


def paneo(x, p):
    """p de -1 (izquierda) a 1 (derecha)."""
    if x.ndim == 2:
        x = x.mean(axis=1)
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], axis=1)


def estereo(x):
    return x if x.ndim == 2 else np.stack([x, x], axis=1)


# --- montar --------------------------------------------------------------------------
class Pista:
    """Una pista estéreo en la que se van colocando sonidos en su segundo."""

    def __init__(self, dur):
        self.x = np.zeros((int(dur * SR) + SR * 8, 2))
        self.dur = dur

    def poner(self, sonido, en, volumen=1.0, pan=0.0):
        s = paneo(sonido, pan) if pan else estereo(sonido)
        i = int(en * SR)
        if i >= len(self.x):
            return
        fin = min(len(self.x), i + len(s))
        self.x[i:fin] += s[:fin - i] * volumen

    def mezclar(self, otra, volumen=1.0):
        n = min(len(self.x), len(otra.x))
        self.x[:n] += otra.x[:n] * volumen

    def bucle(self):
        """Para que el final empalme con el principio: lo que suena después del final se suma al principio."""
        n = int(self.dur * SR)
        cola = self.x[n:]
        out = self.x[:n].copy()
        out[:min(n, len(cola))] += cola[:min(n, len(cola))]
        return out

    def entera(self, recortar=True):
        x = self.x
        if recortar:
            vivo = np.nonzero(np.abs(x).max(axis=1) > 1e-4)[0]
            x = x[:vivo[-1] + 1] if len(vivo) else x[:1]
        return x


def normalizar(x, pico=0.89):
    m = np.abs(x).max()
    return x if m == 0 else x / m * pico


def suavizar_bordes(x, entrada=0.003, salida=0.01):
    n = len(x)
    e = np.ones(n)
    a, b = int(entrada * SR), int(salida * SR)
    if a:
        e[:a] = np.linspace(0, 1, a)
    if b:
        e[-b:] = np.minimum(e[-b:], np.linspace(1, 0, b))
    return x * (e[:, None] if x.ndim == 2 else e)


def _ffmpeg():
    """El programa ffmpeg: el del sistema (Homebrew) o, si no hay, el que trae el paquete imageio-ffmpeg."""
    ruta = shutil.which("ffmpeg")
    if ruta:
        return ruta
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise SystemExit("Falta ffmpeg: pip3 install -r herramientas/requirements.txt")


def guardar(x, ruta, pico=0.89, calidad=5, titulo=None):
    """Guarda en .ogg (Vorbis), que es lo que mejor lee Godot."""
    x = normalizar(estereo(x), pico)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    tmp = ruta[:-4] + ".wav"
    datos = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(tmp, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(datos.tobytes())
    etiquetas = ["-metadata", f"title={titulo}", "-metadata", "artist=Maisha"] if titulo else []
    subprocess.run([_ffmpeg(), "-y", "-loglevel", "error", "-i", tmp, "-c:a", "libvorbis", "-q:a", str(calidad)] + etiquetas + [ruta], check=True)
    os.remove(tmp)


# --- piano suave ---------------------------------------------------------------------
def piano(nota, dur=3.0, fuerza=0.7, suelta=None):
    """Piano de fieltro, suave y cálido (como el de las músicas tranquilas de los juegos de mundo abierto).
    Cada nota: parciales ligeramente inarmónicos, tres cuerdas un pelín desafinadas (dan calidez),
    caída en dos tiempos (el golpe y el sonido que se queda), un golpecito de martillo apagado
    y un filtro que la hace más oscura cuanto más flojo se toca.
    «suelta»: segundos hasta que se levanta la tecla (por defecto suena hasta que se apaga sola)."""
    f0 = hz(nota)
    n = int(dur * SR)
    tt = np.arange(n) / SR
    grave = np.clip((np.log2(f0 / 27.5)) / 7.5, 0, 1)            # 0 = nota muy grave, 1 = muy aguda
    t0 = 7.0 - 5.2 * grave                                          # cuánto dura el sonido según la altura
    b = 0.00012 + 0.0009 * grave ** 2                               # inarmonía (las cuerdas graves, menos)
    x = np.zeros(n)
    brillo = 0.55 + 0.9 * fuerza
    for k in range(1, 15):
        fk = f0 * k * np.sqrt(1 + b * k * k)
        if fk > 9000:
            break
        amp = (1.0 / k ** 1.7) * np.exp(-(k - 1) / (2.8 * brillo))
        if k == 2:
            amp *= 1.2
        tau1 = t0 / (1 + 0.55 * (k - 1)) * 0.22
        tau2 = t0 / (1 + 0.35 * (k - 1))
        env = 0.62 * np.exp(-tt / tau1) + 0.38 * np.exp(-tt / tau2)
        for d in (-0.6, 0.0, 0.7):                                  # tres cuerdas (en centésimas de semitono)
            fd = fk * 2 ** (d / 1200)
            x += amp * env * np.sin(2 * np.pi * fd * tt + d) / 3
    # martillo de fieltro: un «tup» muy corto y apagado
    golpe = int(0.025 * SR)
    martillo = paso_bajo(_azar.normal(0, 1, golpe), 900 + 1500 * fuerza) * np.exp(-np.arange(golpe) / (0.004 * SR)) * 0.05
    x[:golpe] += martillo
    x = paso_bajo(x, 1800 + 3800 * fuerza)
    if suelta is not None and suelta < dur:
        i = int(suelta * SR)
        apagar = np.ones(n)
        apagar[i:] = np.exp(-np.arange(n - i) / (0.18 * SR))
        x *= apagar
    ataque = int(0.002 * SR)
    x[:ataque] *= np.linspace(0, 1, ataque)
    return x * fuerza


def acorde_piano(notas, dur=4.0, fuerza=0.5, rasgueo=0.0):
    """Varias notas a la vez (o un poquito escalonadas con «rasgueo», como una mano que no aprieta todo a la vez)."""
    n = int((dur + rasgueo * len(notas)) * SR)
    x = np.zeros(n)
    for i, nota in enumerate(notas):
        s = piano(nota, dur, fuerza * (0.92 if i else 1.0))
        a = int(i * rasgueo * SR)
        x[a:a + len(s)] += s[:n - a]
    return x
