"""Ilustraciones de Asterhaul (con el pintor de las cinemáticas; se pintan junto a las demás):

    python3 herramientas/cinematicas.py 25_asterhaul_libre

  25_asterhaul_libre  EL FINAL DE ASTERHAUL. El amanecer entra en el cráter. Mji-Jiwe, la ciudad de tres terrazas,
                      tiene todas las forjas encendidas y sus chimeneas echan humo dorado. En el centro, el Gran
                      Diapasón vibra y de la Losa abierta sube una columna de luz de ámbar; las tres cadenas rotas
                      cuelgan de las argollas. En primer término, en la cornisa del cráter, Maisha alza el Cetro del
                      Nexo despierto (cristal dorado, el brote y la pluma enroscados) junto a Mauti.
"""
import numpy as np

from pintor import Lienzo, rampa  # noqa: F401
import cinematicas as ci
import cinematicas_sendero as cs

W, H = ci.W, ci.H
LUZ = (0.4, -0.75, 0.55)
ROCA = ["#1e1210", "#382218", "#56341f", "#74482c", "#94623c", "#b8844e", "#dcae72"]
AMBAR = ["#5a2406", "#9a4a0c", "#d8841c", "#f8b040", "#ffd878", "#fff4c8"]


def asterhaul_libre():
    """«El corazón de la estrella late tranquilo, y Mji-Jiwe vuelve a sonar.»"""
    lz = Lienzo(W, H, semilla=250)
    rng = np.random.default_rng(251)
    HZ = 96
    # 1. El cielo del amanecer, con las últimas estrellas arriba
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#141428", "#2c2444", "#5a3a52", "#a85a48", "#e8904a", "#f8c070"], desde=0, hasta=HZ))
    ci.estrellas(lz, 50, 40, semilla=252, color="#f4ecff")
    sol = lz.circulo(300, HZ + 4, 22)
    lz.sumar_luz(lz.desenfocar(sol, 40), "#ffd070", 0.8)
    lz.pintar(sol, "#fff0c0")
    # 2. El borde del cráter, lejos, en contraluz
    borde = lz.poligono([(0, HZ - 6), (60, HZ - 16), (130, HZ - 10), (200, HZ - 20), (300, HZ - 8), (410, HZ - 22), (500, HZ - 12), (600, HZ - 18), (600, HZ + 16), (0, HZ + 16)])
    lz.pintar(borde, "#3a2430")
    lz.pintar(np.clip(borde - lz.desenfocar(borde, 1) * 0.0, 0, 1) * (lz.y < HZ - 4), "#f8b070", 0.25)
    # la llanura del cráter, en sombra todavía (el sol aún no ha bajado hasta aquí)
    llano = (lz.y > HZ + 6) * 1.0
    lz.pintar(llano, rampa(["#3a2028", "#4a2a2a", "#5a3428"], np.clip((lz.y - HZ) / 140 + (lz.ruido(8, 2, semilla=259) - 0.5) * 0.3, 0, 1)))
    lz.pintar(llano * (lz.y < HZ + 12), "#c87048", 0.35)
    # 3. Las tres terrazas de la ciudad, en óvalos que bajan hacia el centro
    cx, cy = 300, 176
    for k, (rx, ry, col) in enumerate(((280, 84, ROCA[2:]), (210, 62, ROCA[1:6]), (140, 42, ROCA[1:5]))):
        terraza = lz.elipse(cx, cy - 6 + k * 6, rx, ry) * (lz.y > HZ)
        lz.sombrear(terraza, col, 20, LUZ, textura=lz.ruido(3, 3, semilla=253 + k), fuerza_tex=0.2)
        filo = np.clip(terraza - lz.elipse(cx, cy - 6 + k * 6 + 3, rx - 4, ry - 3), 0, 1)
        lz.pintar(filo, "#f8c070", 0.55)
    # las casas-taller en las terrazas, con su forja encendida y humo dorado
    humo = np.zeros((lz.H, lz.W))
    for k in range(22):
        a = rng.uniform(0, 2 * np.pi)
        anillo = rng.choice([0.9, 0.72])
        hx, hy = cx + np.cos(a) * 250 * anillo, cy - 8 + np.sin(a) * 74 * anillo
        if hy < HZ + 8 or hy > 240:
            continue
        e = 0.6 + (hy - HZ) / 200
        casa = lz.poligono([(hx - 9 * e, hy), (hx + 9 * e, hy), (hx + 9 * e, hy - 10 * e), (hx - 9 * e, hy - 10 * e)])
        tejado = lz.poligono([(hx - 11 * e, hy - 10 * e), (hx, hy - 18 * e), (hx + 11 * e, hy - 10 * e)])
        lz.sombrear(casa, ROCA[2:], 4 * e, LUZ)
        lz.sombrear(tejado, ["#3a160c", "#6a2c14", "#9a4a1e", "#c46c2c"], 3 * e, LUZ)
        ventana = lz.poligono([(hx - 3 * e, hy - 3 * e), (hx + 1 * e, hy - 3 * e), (hx + 1 * e, hy - 7 * e), (hx - 3 * e, hy - 7 * e)])
        lz.sumar_luz(lz.desenfocar(ventana, 4), "#ffb040", 0.6)
        lz.pintar(ventana, "#ffd878")
        for j in range(5):
            humo = np.maximum(humo, lz.circulo(hx + 5 * e + j * 2.5, hy - 20 * e - j * 7 * e, (2.0 + j * 1.2) * e))
    lz.pintar(lz.desenfocar(humo, 1.5), "#f8d898", 0.45)
    # 4. La Losa abierta y la columna de luz; el Gran Diapasón vibrando; las tres cadenas rotas
    columna = lz.poligono([(cx - 18, cy + 4), (cx + 18, cy + 4), (cx + 34, 0), (cx - 34, 0)])
    lz.sumar_luz(lz.desenfocar(columna, 14) * np.clip(1 - (cy - lz.y) / 200, 0, 1), "#ffc860", 0.7)
    losa = lz.elipse(cx, cy + 4, 40, 12)
    lz.pintar(losa, "#2a1408")
    lz.pintar(lz.elipse(cx, cy + 4, 26, 7), AMBAR[4])
    lz.sumar_luz(lz.desenfocar(lz.elipse(cx, cy + 4, 26, 7), 8), AMBAR[3], 0.9)
    for lado in (-1, 1):
        brazo = lz.trazo([(cx + lado * 5, cy - 6), (cx + lado * 16, cy - 22), (cx + lado * 16, cy - 74)], 6.0, 4.5)
        lz.sombrear(brazo, ["#14161c", "#2a2e3a", "#464c5c", "#6a7284", "#949cae"], 3, LUZ)
        for d in (-3, 3):
            eco = lz.trazo([(cx + lado * (21 + d * 0.0) + lado * abs(d), cy - 20), (cx + lado * (21 + abs(d)), cy - 72)], 0.6)
            lz.pintar(eco, "#fff4c8", 0.5)
    lz.sombrear(lz.trazo([(cx, cy + 2), (cx, cy - 8)], 7), ["#14161c", "#2a2e3a", "#464c5c", "#6a7284"], 3, LUZ)
    for k, ang in enumerate((-2.4, -0.7, 1.6)):
        x0, y0 = cx + np.cos(ang) * 46, cy + 4 + np.sin(ang) * 14
        cadena = lz.trazo(lz.curva((x0, y0), (x0 + np.cos(ang) * 14, y0 + 10), (x0 + np.cos(ang) * 24, y0 + 22), n=16), 1.6)
        lz.pintar(cadena, "#565a6a")
        lz.pintar(cadena * (((lz.x + lz.y) % 3) < 1.2), "#b8bccc", 0.8)
    # 5. La cornisa en primer término, con Maisha y Mauti
    cornisa = lz.poligono([(0, 206), (170, 200), (300, 210), (430, 198), (600, 206), (600, 256), (0, 256)])
    ci.piedras(lz, cornisa, tam=10, semilla=254, rampa_p=ROCA, luz=LUZ, mortero="#140a08")
    lz.pintar(lz.trazo([(0, 206), (170, 200), (300, 210), (430, 198), (600, 206)], 1.6), "#f8c070", 0.6)
    cs._mauti_luz(lz, 262, 236, e=1.7, mira=1)
    ci.maisha_luz(lz, 318, 238, e=1.8)
    # el Cetro del Nexo, en alto: vara clara, aro de oro, cristal dorado con rayos, el brote y la pluma
    px, py = 336, 186
    vara = lz.trazo([(px - 6, py + 46), (px, py)], 2.4, 2.0)
    lz.pintar(vara, "#8a93b0")
    lz.pintar(vara * (((lz.y) % 6) < 2), "#f2d27a", 0.9)
    lz.pintar(lz.trazo([(px - 4, py + 6), (px + 4, py + 6)], 1.8), "#e8c060")
    cristal = lz.poligono([(px, py - 16), (px + 6, py - 8), (px, py), (px - 6, py - 8)])
    lz.sumar_luz(lz.desenfocar(cristal, 18), "#ffd870", 1.0)
    lz.pintar(cristal, rampa(["#c89a30", "#f9d77a", "#fffbe8"], np.clip(1 - (lz.y - (py - 16)) / 16, 0, 1)))
    for a in np.linspace(0, 2 * np.pi, 9)[:-1]:
        rayo = lz.trazo([(px + np.cos(a) * 10, py - 8 + np.sin(a) * 10), (px + np.cos(a) * 22, py - 8 + np.sin(a) * 22)], 0.9, 0.3)
        lz.pintar(rayo, "#fff4c8", 0.85)
    brote = lz.trazo(lz.curva((px - 3, py + 2), (px - 10, py - 6), (px - 12, py - 14), n=12), 1.2)
    lz.pintar(brote, "#6fcf4f")
    lz.pintar(lz.elipse(px - 13, py - 15, 3.4, 1.6, 30), "#9be06a")
    pluma = lz.trazo(lz.curva((px + 3, py + 2), (px + 10, py - 4), (px + 14, py - 14), n=12), 1.6, 0.5)
    lz.pintar(pluma, "#fff8dc")
    # 6. Motas de ámbar que suben del cráter
    motas = np.zeros((lz.H, lz.W))
    for _ in range(70):
        motas = np.maximum(motas, lz.circulo(rng.uniform(120, 480), rng.uniform(20, 200), rng.uniform(0.6, 1.4)))
    lz.sumar_luz(lz.desenfocar(motas, 2), "#ffc860", 0.6)
    lz.sumar_luz(motas, "#fff4c8", 0.9)
    vin = np.clip(np.hypot((lz.x - 300) / 340, (lz.y - 140) / 190) - 0.72, 0, 1) ** 1.4
    lz.pintar(vin, "#0a0608", 0.45)
    return lz


PIEZAS = {"25_asterhaul_libre": asterhaul_libre}
