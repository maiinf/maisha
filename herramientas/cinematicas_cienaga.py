"""Ilustraciones de la Ciénaga Quieta (con el pintor de las cinemáticas; se pintan junto a las demás):

    python3 herramientas/cinematicas.py 10_konokono_libre

  10_konokono_libre   Konokono, ya libre de la herrumbre, saca las antenas en la orilla al amanecer.
                      La niebla se levanta, el agua se aclara y refleja el cielo; las ranas vuelven a sus nenúfares
                      y los trozos de óxido se hunden apagándose. Maisha la mira desde un tronco caído.
"""
import math

import cv2
import numpy as np

from pintor import Lienzo, rampa  # noqa: F401
import cinematicas as ci

W, H = ci.W, ci.H
LUZ = (-0.7, -0.55, 0.5)            # el sol del amanecer, bajo, a la izquierda
HORIZONTE = 124
NACAR = ["#3a2a2e", "#6b5058", "#9c7c82", "#c8a6a0", "#e6c9b8", "#f6e6d4", "#fff6ea"]
CUERPO = ["#1c1d17", "#2f3026", "#4a4935", "#6a6649", "#8e8761", "#b6ad84", "#ddd3ad"]
SAUCE = ["#0f1a16", "#18281f", "#24392b", "#38513b", "#567055", "#7d9474", "#a9b994"]
AGUA_CIELO = ["#2b3d3f", "#4b6766", "#7c9a92", "#b4c6b2", "#e7dcc0", "#f6e2b8"]


def _sauce(lz, x, base, alto, ancho, semilla):
    """Un sauce lejano: tronco corto y una melena de ramas que cae."""
    rng = np.random.default_rng(semilla)
    lz.pintar(lz.trazo([(x, base), (x + 1, base - alto * 0.5), (x + 4, base - alto * 0.75)], 3.4, 1.6), SAUCE[1])
    cy = base - alto * 0.7
    copa = np.maximum(lz.elipse(x + 2, cy, ancho * 0.5, alto * 0.3), lz.elipse(x + 2 - ancho * 0.2, cy - alto * 0.12, ancho * 0.3, alto * 0.2))
    copa = np.maximum(copa, lz.elipse(x + 2 + ancho * 0.22, cy - alto * 0.06, ancho * 0.3, alto * 0.22))
    for _ in range(46):
        a = rng.random() * math.pi
        cx = x + 2 + math.cos(a) * ancho * 0.48
        top = cy + math.sin(a) * alto * 0.2
        largo = alto * (0.2 + rng.random() * 0.35)
        dx = (cx - x) * 0.12
        copa = np.maximum(copa, lz.trazo([(cx, top), (cx + dx, top + largo * 0.6), (cx + dx * 1.4, top + largo)], 2.4, 0.6))
    lz.sombrear(copa, SAUCE, 5, LUZ, textura=lz.ruido(10, 3, semilla=semilla), fuerza_tex=0.25)


def _espiral(cx, cy, r, vueltas=2.4, giro=0.0, n=160):
    pts = []
    for k in range(n):
        u = k / (n - 1)
        a = giro + u * vueltas * 2 * math.pi
        rr = r * (0.96 - u * 0.86)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.94))
    return pts


def _caracola(lz):
    """Konokono libre: el pie largo en la orilla, la concha de nácar con musgo y flores, las antenas fuera."""
    sx, sy, sr = 432, 136, 58            # la concha
    suelo = 206
    # el pie (cuerpo blando), largo y bajo, con la cabeza hacia la izquierda (hacia Maisha)
    pie = lz.poligono([(560, suelo), (548, suelo - 16), (500, suelo - 26), (420, suelo - 30), (360, suelo - 30),
                       (326, suelo - 40), (306, suelo - 46), (294, suelo - 38), (300, suelo - 22), (318, suelo - 6), (360, suelo + 2)])
    pie = lz.desenfocar(pie, 0.8)
    lz.pintar(lz.desenfocar(lz.elipse(432, suelo + 2, 140, 8), 3), "#0e1412", 0.5)
    lz.sombrear(pie, CUERPO, 8, LUZ, textura=lz.ruido(8, 3, semilla=7), fuerza_tex=0.15,
                recorte=("#ffe6b0", 0.6), recorte_dir=(-1, -0.5), rebote=("#5f7d7a", 0.3))
    # contorno oscuro (se separa de la niebla)
    lz.pintar(np.clip(pie - lz.desenfocar(np.clip(pie - 0.5, 0, 1) * 2, 1.4) * 1.2, 0, 1), "#1c1d17", 0.55)
    # brillo húmedo por el lomo del pie
    lz.sumar_luz(lz.desenfocar(lz.trazo([(330, suelo - 38), (380, suelo - 29), (470, suelo - 26)], 1.6, 0.6), 1.2), "#fff6ea", 0.35)
    # cabeza y antenas (con los ojos en la punta), estiradas y contentas
    cabeza = np.maximum(lz.elipse(306, suelo - 40, 16, 11, -10), lz.elipse(320, suelo - 34, 14, 9))
    lz.sombrear(cabeza, CUERPO, 7, LUZ, recorte=("#ffe6b0", 0.7), recorte_dir=(-1, -0.6))
    lz.pintar(np.clip(cabeza - lz.desenfocar(np.clip(cabeza - 0.5, 0, 1) * 2, 1.4) * 1.2, 0, 1), "#1c1d17", 0.5)
    lz.pintar(lz.trazo([(292, suelo - 34), (300, suelo - 31)], 1.0), "#1d2420", 0.6)          # boquita
    for (base, punta, ctrl) in (((300, suelo - 48), (270, suelo - 98), (284, suelo - 78)),
                                ((312, suelo - 48), (304, suelo - 106), (314, suelo - 82))):
        tallo = lz.trazo(lz.curva(base, ctrl, punta, n=20), 4.0, 2.2)
        lz.sombrear(tallo, CUERPO, 2.5, LUZ, recorte=("#ffe6b0", 0.5), recorte_dir=(-1, 0))
        lz.sombrear(lz.circulo(punta[0], punta[1], 4.2), CUERPO[2:], 3, LUZ)
        lz.pintar(lz.circulo(punta[0] - 1, punta[1] + 0.5, 2.0), "#121614")
        lz.pintar(lz.circulo(punta[0] - 1.6, punta[1] - 0.4, 0.8), "#fff6ea")
    # la concha: nácar en espiral, con el canto oscuro de cada vuelta
    concha = lz.elipse(sx, sy, sr, sr * 0.94)
    tex = lz.ruido(9.0, 3, semilla=11)
    lz.sombrear(concha, NACAR, 40, LUZ, textura=tex, fuerza_tex=0.1, recorte=("#fff1d0", 0.7), recorte_dir=(-1, -0.5),
                rebote=("#6b8a86", 0.35))
    # el labio de la concha, más oscuro, y un brillo grande arriba a la izquierda
    lz.pintar(np.clip(concha - lz.elipse(sx, sy, sr - 4, sr * 0.94 - 4), 0, 1), "#5a4246", 0.55)
    lz.sumar_luz(lz.desenfocar(lz.elipse(sx - sr * 0.38, sy - sr * 0.42, sr * 0.28, sr * 0.16, -35), 5) * concha, "#fffaf0", 0.45)
    # reflejos irisados del nácar (verdosos y rosados) a lo largo de la espiral
    esp = _espiral(sx, sy, sr, giro=0.5)
    for k in range(0, len(esp) - 8, 8):
        tramo = esp[k:k + 9]
        col = ["#bfe3d0", "#f2c6c8", "#e8e0b8"][(k // 8) % 3]
        lz.sumar_luz(lz.desenfocar(lz.trazo(tramo, 5.0 * (1 - k / len(esp)) + 1.2, 1.0), 2.0) * concha, col, 0.18)
    surco = lz.desenfocar(lz.trazo(esp, 5.0, 1.2), 1.2)
    lz.pintar(surco, "#4a3438", 0.75)
    lz.pintar(lz.trazo([(x - 2.5, y - 2.5) for (x, y) in esp], 1.8, 0.5), "#fff6ea", 0.45)
    # musgo y flores encima de la concha
    rng = np.random.default_rng(23)
    for k in range(9):
        a = math.pi * (1.05 + k * 0.11)
        mx, my = sx + math.cos(a) * sr * 0.86, sy + math.sin(a) * sr * 0.86
        lz.sombrear(lz.elipse(mx, my, 9 - (k % 3), 4.5, math.degrees(a) + 90), ci.HIERBA[3:8], 3, LUZ,
                    textura=lz.ruido(0.6, 2, semilla=30 + k), fuerza_tex=0.5)
    for k in range(7):
        a = math.pi * (1.1 + k * 0.13)
        fx, fy = sx + math.cos(a) * sr * 0.95, sy + math.sin(a) * sr * 0.95 - 3
        col = ["#f4b39a", "#fff3c4", "#cc6351"][k % 3]
        for p in range(5):
            pa = p * 2 * math.pi / 5
            lz.pintar(lz.circulo(fx + math.cos(pa) * 2.2, fy + math.sin(pa) * 2.2, 1.6), col)
        lz.pintar(lz.circulo(fx, fy, 1.2), "#e6a852")
    # gotas de agua limpia que resbalan de la concha
    for k in range(6):
        gx, gy = sx - sr * 0.4 + k * 14, sy + sr * 0.6 + (k % 2) * 6
        lz.pintar(lz.elipse(gx, gy, 1.4, 2.2), "#dff2ea", 0.8)
        lz.sumar_luz(lz.desenfocar(lz.circulo(gx, gy, 2), 2), "#bfe3d0", 0.4)


def _rana(lz, x, y, e=1.0, mira=1):
    """Una ranita sentada en un nenúfar (silueta con volumen)."""
    cuerpo = np.maximum(lz.elipse(x, y - 3 * e, 5 * e, 3.6 * e), lz.elipse(x + 3 * e * mira, y - 6 * e, 3.2 * e, 2.6 * e))
    lz.sombrear(cuerpo, ci.HIERBA[1:7], 3 * e, LUZ)
    lz.pintar(lz.circulo(x + 4 * e * mira, y - 8 * e, 1.3 * e), "#121614")
    lz.pintar(lz.circulo(x + 4.3 * e * mira, y - 8.4 * e, 0.5 * e), "#fff6ea")


def _nenufar(lz, x, y, r, flor=None, semilla=0):
    hoja = lz.elipse(x, y, r, r * 0.34)
    corte = lz.poligono([(x, y), (x + r * 1.2, y - r * 0.2), (x + r * 1.2, y + r * 0.1)])
    hoja = np.clip(hoja - corte, 0, 1)
    lz.sombrear(hoja, ci.FOLLAJE[2:8], 2.0, LUZ)
    if flor:
        for p in range(6):
            pa = p * math.pi / 3
            lz.pintar(lz.elipse(x - r * 0.2 + math.cos(pa) * 2.2, y - 2.5 + math.sin(pa) * 1.1, 2.2, 1.3, math.degrees(pa)), flor)
        lz.pintar(lz.circulo(x - r * 0.2, y - 3, 1.2), "#f9b947")


def konokono_libre():
    """«La herrumbre se desprende de la concha como corteza vieja. Debajo, la espiral vuelve a ser de nácar y musgo.
    Konokono saca despacio las antenas... y el agua de la ciénaga se aclara a su paso. Las ranas vuelven a cantar.»"""
    lz = Lienzo(W, H, semilla=101)
    # el cielo del amanecer: oscuro arriba a la derecha, cálido y claro abajo a la izquierda (donde sale el sol)
    cielo = lz.gradiente(["#33504f", "#5d7d77", "#a9bca5", "#e7dcc0", "#f8e3b4"], desde=0, hasta=HORIZONTE)
    calido = np.clip(1 - np.hypot((lz.x - 70) / 260, (lz.y - HORIZONTE) / 120), 0, 1)
    lz.pintar(np.ones((lz.H, lz.W)), cielo)
    lz.sumar_luz(calido ** 1.6, "#ffd98a", 0.55)
    lz.sumar_luz(lz.desenfocar(lz.circulo(64, HORIZONTE - 6, 9), 3), "#fff6dc", 0.9)          # el sol
    # sauces y árboles muertos lejanos, en la neblina
    lejos = Lienzo(W, H, semilla=103)
    lejos.img = lz.img.copy()
    for k in range(13):
        x = 150 + k * 37 + (k % 3) * 9
        _sauce(lejos, x, HORIZONTE + 2, 54 + (k % 4) * 10, 38 + (k % 3) * 8, 300 + k)
    for (x, alto) in ((118, 60), (560, 70)):
        lejos.pintar(lejos.trazo([(x, HORIZONTE + 2), (x - 3, HORIZONTE - alto * 0.6), (x + 6, HORIZONTE - alto)], 3.2, 1.0), SAUCE[1])
        lejos.pintar(lejos.trazo([(x - 2, HORIZONTE - alto * 0.5), (x - 16, HORIZONTE - alto * 0.75)], 1.6, 0.6), SAUCE[1])
    borroso = cv2.GaussianBlur(lejos.img.astype(np.float32), (0, 0), 1.0)
    lz.pintar(np.ones((lz.H, lz.W)), borroso)
    lz.pintar(np.clip((lz.y - (HORIZONTE - 80)) / 80, 0, 1) * (lz.y < HORIZONTE + 1), "#d9dfca", 0.55)   # neblina
    # nubes alargadas del amanecer (rompen el degradado del cielo)
    r3 = np.random.default_rng(107)
    for k in range(9):
        cx, cy = r3.random() * 620, 12 + r3.random() * 70
        rx, ry = 50 + r3.random() * 90, 2.5 + r3.random() * 3
        nube = lz.desenfocar(lz.elipse(cx, cy, rx, ry), 2.5) * (lz.y < HORIZONTE - 40)
        col = "#f6dcb0" if cx < 300 else "#9fb8ad"
        lz.pintar(nube, col, 0.45)
        lz.pintar(lz.desenfocar(lz.elipse(cx + 6, cy + ry * 0.8, rx * 0.8, ry * 0.5), 2) * (lz.y < HORIZONTE - 40), "#5d7d77", 0.25)
    # el agua: refleja el cielo y los sauces (volteado), algo más oscuro y con ondas horizontales
    arriba = lz.img[: int(HORIZONTE * lz.s)].copy()
    reflejo = arriba[::-1]
    agua_alto = lz.H - int(HORIZONTE * lz.s)
    reflejo = cv2.resize(reflejo, (lz.W, agua_alto), interpolation=cv2.INTER_LINEAR) if reflejo.shape[0] != agua_alto else reflejo
    ondas = (np.sin(np.arange(agua_alto) * 0.9) * 2.5).astype(int)
    for fila in range(agua_alto):
        reflejo[fila] = np.roll(reflejo[fila], ondas[fila] * (1 + fila // 60), axis=0)
    reflejo = cv2.GaussianBlur(reflejo.astype(np.float32), (0, 0), 1.0)
    reflejo = reflejo * 0.78 + np.array([0.05, 0.1, 0.12]) * 0.22
    lz.img[int(HORIZONTE * lz.s):] = reflejo
    # brillo del sol en el agua (una estela de destellos)
    for k in range(40):
        y = HORIZONTE + 4 + k * 3.2
        ancho = 6 + k * 1.6
        lz.sumar_luz(lz.desenfocar(lz.elipse(64 + k * 1.8, y, ancho * (0.5 + 0.5 * ((k * 7) % 3) / 2), 0.7), 0.6), "#fff1c8", 0.5 * (1 - k / 44))
    # líneas de ondas suaves
    for k in range(26):
        y = HORIZONTE + 6 + k * 5 + (k % 3)
        x0 = (k * 83) % 520
        lz.pintar(lz.trazo([(x0, y), (x0 + 30 + (k % 4) * 10, y)], 0.6, 0.6), "#e9eedf", 0.25)
    # la orilla embarrada con musgo donde está Konokono, y un tronco caído a la izquierda (donde está Maisha)
    orilla = lz.poligono([(262, 220), (284, 205), (330, 199), (420, 198), (520, 196), (600, 192), (600, 248), (480, 244),
                          (380, 240), (300, 236)])
    orilla = lz.desenfocar(orilla, 1.2)
    lz.sombrear(orilla, ["#16130e", "#241f16", "#33301f", "#47462a", "#5f5f36"], 6, LUZ, textura=lz.ruido(14, 3, semilla=5), fuerza_tex=0.2)
    musgo_o = orilla * np.clip(1 - (lz.y - 196) / 9, 0, 1)
    lz.pintar(musgo_o, "#56743a", 0.75)
    # el borde mojado de la orilla brilla un poco y se refleja en el agua
    lz.pintar(lz.desenfocar(lz.trazo([(300, 237), (380, 241), (480, 245), (600, 249)], 2.0, 2.0), 1.0), "#8fa69a", 0.35)
    tronco = lz.trazo([(40, 228), (120, 218), (214, 214)], 15, 11)
    lz.sombrear(tronco, ci.MADERA[0:7], 7, LUZ, textura=lz.ruido(0.8, 3, semilla=8), fuerza_tex=0.4, recorte=("#ffd98a", 0.6), recorte_dir=(-1, -1))
    lz.pintar(lz.trazo([(40, 222), (120, 212), (214, 208)], 3.5, 2.5) * (lz.ruido(1.0, 3, semilla=9) > 0.45), "#6f8a46", 0.8)
    lz.pintar(lz.elipse(214, 214, 5, 7), "#d2a07c")
    lz.pintar(lz.elipse(214, 214, 3, 4.5), "#905c45")
    # Konokono libre
    _caracola(lz)
    # trozos de óxido que se hunden en el agua, con la luz violeta que se apaga
    rng = np.random.default_rng(105)
    for k in range(10):
        x, y = 360 + rng.random() * 200, 206 + rng.random() * 30
        trozo = lz.poligono([(x - 4, y), (x - 1, y - 3 - rng.random() * 2), (x + 4, y - 1), (x + 2, y + 2)])
        lz.sombrear(trozo, ["#2a140c", "#5a2f18", "#8a4a22", "#b06a34", "#cc8a4c"], 2.0, LUZ)
        lz.pintar(lz.trazo([(x - 7, y + 3), (x + 7, y + 3)], 0.6), "#e9eedf", 0.35)
        if k % 3 == 0:
            lz.sumar_luz(lz.desenfocar(lz.circulo(x, y - 1, 2), 3), "#a24fd0", 0.3)
    # nenúfares con ranas
    for (x, y, r, flor, rana) in ((240, 168, 14, "#f6d3dc", True), (190, 150, 9, None, False), (318, 232, 16, "#fff3e6", False),
                                  (126, 186, 11, "#f6d3dc", True), (520, 236, 13, None, True), (560, 152, 8, None, False)):
        _nenufar(lz, x, y, r, flor)
        if rana:
            _rana(lz, x - 2, y - 1, 0.9 + r / 30, mira=1 if x < 300 else -1)
    # Maisha, sobre el tronco, de tres cuartos mirando a Konokono
    ci.maisha(lz, 132, 213, 2.1, "lado", 1, luz=LUZ, recorte=("#ffd98a", 0.8), recorte_dir=(-1, -0.5), brillo=0.7)
    # juncos en primer plano (esquinas), a contraluz
    for (x0, n, s) in ((6, 9, 1), (586, 8, -1)):
        r2 = np.random.default_rng(x0)
        for k in range(n):
            bx = x0 + s * k * 3.2
            alto = 50 + r2.random() * 50
            lz.pintar(lz.trazo([(bx, 258), (bx + s * (4 + r2.random() * 8), 258 - alto)], 2.2, 0.6), "#1a2418")
            if k % 3 == 0:
                tx, ty = bx + s * 6, 258 - alto * 0.85
                lz.pintar(lz.elipse(tx, ty, 2.0, 6), "#3a2414")
    # la niebla que se levanta: jirones claros sobre el agua, a la izquierda y al fondo
    for (cx, cy, rx, ry, f) in ((130, 140, 140, 9, 0.25), (380, 128, 200, 6, 0.22), (520, 170, 90, 7, 0.14)):
        lz.pintar(lz.desenfocar(lz.elipse(cx, cy, rx, ry), 6), "#eef0e0", f)
    # luciérnagas que se van (las últimas de la noche)
    for k in range(10):
        x, y = 160 + rng.random() * 380, 60 + rng.random() * 120
        lz.sumar_luz(lz.desenfocar(lz.circulo(x, y, 1.2), 2), "#fde27e", 0.6)
    # viñeta suave
    vin = np.clip(np.hypot((lz.x - 300) / 360, (lz.y - 140) / 190) - 0.72, 0, 1) ** 1.5
    lz.pintar(vin, "#0a0c0b", 0.5)
    return lz


PIEZAS = {"10_konokono_libre": konokono_libre}
