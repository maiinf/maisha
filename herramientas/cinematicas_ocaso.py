"""Ilustraciones del Valle del Ocaso (con el pintor de las cinemáticas; se pintan junto a las demás):

    python3 herramientas/cinematicas.py 26_primera_noche

  26_primera_noche  EL FINAL DEL JUEGO. Por primera vez en siglos se hace de noche en el Valle del Ocaso. El sol,
                    sin cadenas, se acuesta despacio detrás del horizonte y deja una franja de oro; arriba salen las
                    estrellas y una luna fina. Abajo, Jioni duerme: los tejados de las terrazas con los doce Faroles de
                    la Hora encendidos en la plaza. En primer término, en el borde del Altar, Maisha y Mauti, juntos,
                    miran la noche; las tres cadenas sueltas cuelgan del altar.
"""
import numpy as np

from pintor import Lienzo, rampa  # noqa: F401
import cinematicas as ci
import cinematicas_sendero as cs

W, H = ci.W, ci.H
LUZ = (0.3, -0.8, 0.5)
PIEDRA = ["#140c14", "#24162a", "#38243e", "#523656", "#6e4a70", "#8e648e"]


def primera_noche():
    """«El sol por fin descansa. Y Jioni, por fin, duerme.»"""
    lz = Lienzo(W, H, semilla=260)
    rng = np.random.default_rng(261)
    HZ = 120
    # 1. El cielo: noche arriba, una franja de oro abajo donde el sol se ha acostado
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#060818", "#0c1430", "#1c2450", "#3a2c5c", "#8a4a5a", "#e08a50", "#f8c070"], desde=0, hasta=HZ))
    ci.estrellas(lz, 170, 100, semilla=262, color="#f4ecff")
    via = np.clip(1 - np.abs(lz.y - (20 + lz.x * 0.08)) / 26, 0, 1) * (lz.ruido(10, 3, semilla=263) > 0.45)
    lz.sumar_luz(lz.desenfocar(via * 1.0, 6), "#8a90d0", 0.3)
    luna = np.clip(lz.circulo(470, 40, 13) - lz.circulo(476, 36, 12), 0, 1)
    lz.sumar_luz(lz.desenfocar(luna, 10), "#d8e0ff", 0.6)
    lz.pintar(luna, "#fffbe8")
    sol = lz.circulo(300, HZ + 6, 26) * (lz.y < HZ)
    lz.sumar_luz(lz.desenfocar(lz.circulo(300, HZ, 30), 40), "#ffb060", 0.8)
    lz.pintar(sol, "#ffd890")
    # 2. Las colinas del valle, en contraluz
    colinas = lz.poligono([(0, HZ - 4), (90, HZ - 14), (180, HZ - 6), (260, HZ - 2), (340, HZ - 2), (430, HZ - 12), (520, HZ - 6), (600, HZ - 16), (600, HZ + 30), (0, HZ + 30)])
    lz.pintar(colinas, "#2a1a30")
    lz.pintar(colinas * (lz.y < HZ), "#f8a060", 0.25)
    # 3. Jioni dormida: terrazas con tejados y ventanas apagadas; en la plaza, los doce faroles
    for k, (y0, n, e) in enumerate(((HZ + 14, 26, 0.6), (HZ + 34, 20, 0.8), (HZ + 56, 14, 1.0))):
        terraza = lz.poligono([(0, y0), (600, y0 - 4), (600, y0 + 30), (0, y0 + 30)])
        lz.sombrear(terraza, PIEDRA[1:5], 10, LUZ)
        for j in range(n):
            hx = (j + 0.5) * 600 / n + rng.uniform(-8, 8)
            if 230 < hx < 370 and k == 2:
                continue
            casa = lz.poligono([(hx - 10 * e, y0 + 2), (hx + 10 * e, y0 + 2), (hx + 10 * e, y0 - 9 * e), (hx - 10 * e, y0 - 9 * e)])
            cupula = lz.elipse(hx, y0 - 9 * e, 10 * e, 6 * e) * (lz.y < y0 - 9 * e)
            lz.sombrear(np.clip(casa + cupula, 0, 1), PIEDRA[2:], 4 * e, LUZ)
            if rng.random() < 0.25:                                           # (alguna vela, muy bajita)
                v = lz.circulo(hx + 3 * e, y0 - 3 * e, 1.2 * e)
                lz.sumar_luz(lz.desenfocar(v, 3), "#ffb060", 0.4)
                lz.pintar(v, "#ffd890")
    plaza = lz.elipse(300, HZ + 60, 70, 14)
    lz.sombrear(plaza, PIEDRA[2:], 6, LUZ)
    for k in range(12):
        a = k * np.pi / 6
        fx, fy = 300 + np.cos(a) * 58, HZ + 58 + np.sin(a) * 10
        lz.pintar(lz.trazo([(fx, fy), (fx, fy - 10)], 0.7), "#2a1a20")
        f = lz.circulo(fx, fy - 11, 1.8)
        lz.sumar_luz(lz.desenfocar(f, 5), "#ffb040", 0.7)
        lz.pintar(f, "#ffe090")
    # 4. El borde del Altar en primer término, con las cadenas sueltas
    borde = lz.poligono([(0, 214), (200, 206), (330, 210), (460, 204), (600, 212), (600, 256), (0, 256)])
    ci.piedras(lz, borde, tam=10, semilla=264, rampa_p=["#1a1018", "#2e1e2c", "#46303e", "#644454", "#80586a", "#a07484"], luz=LUZ, mortero="#0a060a")
    lz.pintar(lz.trazo([(0, 214), (200, 206), (330, 210), (460, 204), (600, 212)], 1.4), "#f8b070", 0.4)
    for x0 in (120, 470, 520):
        cadena = lz.trazo(lz.curva((x0, 214), (x0 + 6, 228), (x0 - 4, 240), (x0 + 2, 256), n=16), 1.8)
        lz.pintar(cadena, "#4a4e5e")
        lz.pintar(cadena * (((lz.x + lz.y) % 3) < 1.2), "#a8acbc", 0.8)
    # Maisha y Mauti, sentados de espaldas, mirando la noche
    cs._mauti_luz(lz, 278, 226, e=1.6, mira=1)
    ci.maisha_luz(lz, 322, 228, e=1.7)
    # 5. Luciérnagas y el viento de la noche
    motas = np.zeros((lz.H, lz.W))
    for _ in range(40):
        motas = np.maximum(motas, lz.circulo(rng.uniform(40, 560), rng.uniform(140, 210), rng.uniform(0.6, 1.2)))
    lz.sumar_luz(lz.desenfocar(motas, 2), "#c8f080", 0.5)
    lz.sumar_luz(motas, "#f0ffd0", 0.8)
    vin = np.clip(np.hypot((lz.x - 300) / 340, (lz.y - 130) / 190) - 0.7, 0, 1) ** 1.4
    lz.pintar(vin, "#020208", 0.5)
    return lz


PIEZAS = {"26_primera_noche": primera_noche}
